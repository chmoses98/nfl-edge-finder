"""V4 TEAM VOLUME: pregame expected pass attempts and rush attempts per team-game, with an explicit error scale.

v3's team volume is the team's own EWMA (research/opportunity found the market line adds only ~4% to that, and
the 2026 week-2 "11% under-projection" was the v2 zero-implied-total defect inside the opportunity GLM, not the
EWMA). V4 makes it one coherent, measured layer:

    pass_att ~ team EWMA pass att + team pass-rate EWMA + OPPONENT pass attempts allowed EWMA + implied team total
               + spread (game script) + home + indoor + recent QB change
    rush_att ~ the same with the rushing counterparts

Ridge least squares on team-games of seasons strictly before the target season. The residual sd of each model is
carried as the volume uncertainty that V4 propagates into every player's opportunity. Environment inputs are the
market-implied spread/total in production (never a closing line, never a zero: no environment -> no projection).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from nfl_edge.engines.player.features_v2 import _ewma_by_key
from nfl_edge.engines.player.v4.linear import Linear

HALFLIFE, CARRY, SHRINK = 6.0, 0.35, 4.0
PASS_FEATURES = ["t_pa", "t_rate", "o_pa_allowed", "implied_total", "spread_team", "home_f", "indoor_f", "qb_changed_recent"]
RUSH_FEATURES = ["t_ra", "t_rate", "o_ra_allowed", "implied_total", "spread_team", "home_f", "indoor_f", "qb_changed_recent"]


def team_game_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (team, game): actual attempts (NaN for a prospective game) and pregame features."""
    d = df.copy()
    pro = d.get("is_prospective", pd.Series(False, index=d.index)).fillna(False).astype(bool)
    d["_pa"] = np.where(pro, np.nan, d["attempts"]); d["_ra"] = np.where(pro, np.nan, d["carries"])
    g = d.groupby(["team", "game_id", "season", "week"], sort=False)
    t = g.agg(pa=("_pa", lambda s: s.sum(min_count=1)), ra=("_ra", lambda s: s.sum(min_count=1)),
              opponent=("opponent_team", "first"), implied_total=("implied_total", "first"), spread_team=("spread_team", "first"),
              home=("home", "first"), indoor=("indoor", "first"), qb_changed_recent=("qb_changed_recent", "first")).reset_index()
    t["plays"] = t["pa"] + t["ra"]
    t["rate"] = t["pa"] / t["plays"]
    pri_seasons = sorted(t["season"].unique())[:3]
    prior = t[t.season.isin(pri_seasons)][["pa", "ra", "rate"]].mean().to_numpy(float)
    own = _ewma_by_key(t, "team", ["pa", "ra", "rate"], HALFLIFE, CARRY, SHRINK, prior, "t_")
    t[["t_pa", "t_ra", "t_rate"]] = own[["t_pa", "t_ra", "t_rate"]].to_numpy()
    # what each defence has allowed: the opponent's offensive volume in games against it, strictly prior
    dfn = t[["opponent", "game_id", "season", "week", "pa", "ra"]].rename(columns={"opponent": "defteam"})
    de = _ewma_by_key(dfn, "defteam", ["pa", "ra"], HALFLIFE, CARRY, SHRINK, prior[:2], "o_")
    dfn[["o_pa_allowed", "o_ra_allowed"]] = de[["o_pa", "o_ra"]].to_numpy()
    t = t.merge(dfn[["defteam", "game_id", "o_pa_allowed", "o_ra_allowed"]], left_on=["opponent", "game_id"],
                right_on=["defteam", "game_id"], how="left").drop(columns=["defteam"])
    t["home_f"] = t["home"].fillna(False).astype(float)
    t["indoor_f"] = t["indoor"].fillna(False).astype(float)
    t["qb_changed_recent"] = t["qb_changed_recent"].fillna(0.0).astype(float)
    return t


@dataclass
class VolumeModel:
    pass_m: Linear | None = None
    rush_m: Linear | None = None
    sd_pa: float = 7.0
    sd_ra: float = 6.0
    ablate: bool = False           # True -> the v3 volume (team EWMA only)
    info: dict = field(default_factory=dict)

    @classmethod
    def fit(cls, teams: pd.DataFrame, target_season: int, *, ablate: bool = False, market_env: bool = True) -> "VolumeModel":
        tr = teams[(teams.season < target_season) & teams.pa.notna() & teams.implied_total.notna()]
        m = cls(ablate=ablate)
        if ablate:
            m.pass_m = Linear(["t_pa"], np.array([0.0, 1.0]), np.zeros(1), np.ones(1))
            m.rush_m = Linear(["t_ra"], np.array([0.0, 1.0]), np.zeros(1), np.ones(1))
        else:
            env = (lambda cols: cols) if market_env else (lambda cols: [c for c in cols if c not in ("implied_total", "spread_team")])
            m.pass_m = Linear.fit(tr, env(PASS_FEATURES), tr.pa.to_numpy(float))
            m.rush_m = Linear.fit(tr, env(RUSH_FEATURES), tr.ra.to_numpy(float))
        m.sd_pa = float(np.std(tr.pa - m.pass_m.predict(tr)))
        m.sd_ra = float(np.std(tr.ra - m.rush_m.predict(tr)))
        m.info = {"n_team_games": int(len(tr)), "sd_pass_att": round(m.sd_pa, 3), "sd_rush_att": round(m.sd_ra, 3)}
        return m

    def predict(self, teams: pd.DataFrame) -> pd.DataFrame:
        pa = np.clip(self.pass_m.predict(teams), 12, 60)
        ra = np.clip(self.rush_m.predict(teams), 10, 50)
        return pd.DataFrame({"team": teams.team.to_numpy(), "game_id": teams.game_id.to_numpy(), "vol_pa": pa, "vol_ra": ra,
                             "vol_pa_sd": self.sd_pa, "vol_ra_sd": self.sd_ra})

    def summary(self) -> dict:
        return {**self.info, "pass": {k: round(v, 4) for k, v in self.pass_m.coefficients().items()},
                "rush": {k: round(v, 4) for k, v in self.rush_m.coefficients().items()}}
