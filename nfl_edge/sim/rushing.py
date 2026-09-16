"""Rushing enrichment: the football inputs a rushing projection should have, with their provenance.

Every candidate here passed three questions before being written down (the audit is in
``research/simulation_engine/RUSHING_ABLATION.md``); the ones that failed are recorded there too, because
"we looked and it was not usable" is the useful half of a feature audit.

RETAINED (source, coverage, point-in-time status)

  blocking / OL      PFR advanced weekly rushing (``pfr_advstats/advstats_week_rush_<s>.parquet``),
                     2018-2026, zero nulls on yards-before-contact, 100% pfr_player_id -> GSIS join.
                     Published per game after it is played, so only a player's or team's EARLIER games
                     enter.  Team yards-before-contact per attempt is the blocking channel; the runner's
                     own yards-after-contact per attempt is the elusiveness channel -- the whole point of
                     splitting them is that the first transfers with the offensive line and the second
                     with the back.
  OL continuity      snap counts (``snap_counts_<s>.parquet``, 2012+): the share of the previous game's
                     five most-used offensive-line snap-takers who were also the five most-used in the
                     game before that, EWMA'd over prior games.  A team trait, from published games only.
  OL absences        the week's injury report, counting offensive linemen designated Out or Doubtful.
                     Historical: the final weekly report, filed before kickoff.  Prospective: resolved
                     through the content-addressed injury vintage at the cutoff (``prospective.py``).
  defensive front    the same quantities on the other side of the ball (what a defence has ALLOWED), from
                     the same prior-games-only aggregates: yards before contact allowed per attempt,
                     stuff rate, explosive-rush rate, rush EPA per attempt.
  opponent adjust    a defence's allowed rate minus the strength of the offences it has actually faced,
                     where "strength" is each of those opponents' own prior-only offensive feature at the
                     time it was played.  Composes two prior-only quantities, so it stays point-in-time.
  stuff / explosive  from play-by-play: share of a runner's (or a defence's) carries gaining <= 0, and
                     the 10+/15+/20+ yard shares.
  QB rush threat     the quarterback share of the team's designed rushes, EWMA over prior games.
  venue              ``indoor`` from the schedule's roof, which is known before kickoff.

REJECTED, and why (not "it sounded smart" -- it failed the audit)

  FTN scheme data    ``ftn_charting`` has run concepts (RPO, sneak, backfield/box counts, motion) from
                     2022, but its only timestamp is a FILE-level ``date_pulled`` that moves when the file
                     is rebuilt -- weeks 1-5 of 2024 all carry 2025-09-01.  There is no per-row
                     publication instant, so a point-in-time claim cannot be made, and with coverage
                     starting in 2022 the earliest evaluation season would have one training season.
  observed weather   the schedule's ``temp`` and ``wind`` are the values MEASURED at the game, i.e.
                     hindsight for a projection, and they are null for every indoor game.  Forecast
                     vintages (the point-in-time replacement) only exist from 2026-09-04, so no
                     historical fit can use them.  ``indoor`` is kept because a roof is known in advance.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd
import polars as pl

from . import data as D
from . import features as F

RUSH_PRIORS_VERSION = "sim-rush-priors-1.0.0"
RUSH_FEATURES_VERSION = "sim-rush-features-1.0.0"

OL_POS = ("T", "G", "C", "OL", "OT", "OG")

# offence-side team levels that get a frozen league prior and an EWMA
TEAM_RUSH_RATES = {"ybc_att": ("ybc", "pfr_carries"), "yac_att": ("yac", "pfr_carries"),
                   "broken_att": ("broken", "pfr_carries"), "stuff_rate": ("stuffs", "carries"),
                   "exp10_rate": ("exp10", "carries"), "exp20_rate": ("exp20", "carries"),
                   "rush_epa_att": ("rush_epa", "carries"), "qb_rush_share": ("qb_carries", "carries")}
PLAYER_RUSH_RATES = {"ybc_att": ("ybc", "pfr_carries"), "yac_att": ("yac", "pfr_carries"),
                     "broken_att": ("broken", "pfr_carries"), "stuff_rate": ("stuffs", "carries"),
                     "exp15_rate": ("exp15", "carries")}
ADJUSTED = ("ybc_att", "stuff_rate", "rush_epa_att")


# ------------------------------------------------------------------------------------ raw aggregates
def _pfr_rush(seasons) -> pd.DataFrame:
    """Per (game, player) yards before/after contact and broken tackles, keyed to GSIS."""
    cw = pl.read_parquet(os.path.join(D.ROOT, "data", "silver", "player_crosswalk.parquet")) \
        .select(["gsis_id", "pfr_id"]).filter(pl.col("pfr_id").is_not_null()).unique("pfr_id")
    frames = []
    for s in seasons:
        p = os.path.join(D.RAW, "pfr_advstats", f"advstats_week_rush_{s}.parquet")
        if not os.path.exists(p):
            continue
        d = pl.read_parquet(p, columns=["game_id", "season", "week", "team", "pfr_player_id", "carries",
                                        "rushing_yards_before_contact", "rushing_yards_after_contact",
                                        "rushing_broken_tackles"])
        d = d.join(cw, left_on="pfr_player_id", right_on="pfr_id", how="inner")
        frames.append(d.select([
            "game_id", pl.col("gsis_id").alias("player_id"), pl.col("team").replace(D.TEAM_FIX).alias("team"),
            pl.col("carries").cast(pl.Float64).alias("pfr_carries"),
            pl.col("rushing_yards_before_contact").cast(pl.Float64).alias("ybc"),
            pl.col("rushing_yards_after_contact").cast(pl.Float64).alias("yac"),
            pl.col("rushing_broken_tackles").cast(pl.Float64).alias("broken")]))
    if not frames:
        return pd.DataFrame(columns=["game_id", "player_id", "team", "pfr_carries", "ybc", "yac", "broken"])
    return pl.concat(frames, how="diagonal_relaxed").to_pandas()


def _ol_continuity(seasons) -> pd.DataFrame:
    """Per (game, team): the share of the five most-used offensive-line snap-takers who were also in the
    previous game's five.  Uses only games already played."""
    frames = []
    for s in seasons:
        p = os.path.join(D.RAW, "snap_counts", f"snap_counts_{s}.parquet")
        if not os.path.exists(p):
            continue
        d = pl.read_parquet(p, columns=["game_id", "season", "week", "team", "position", "player", "offense_snaps"])
        d = d.filter(pl.col("position").is_in(list(OL_POS)) & (pl.col("offense_snaps") > 0))
        d = d.with_columns(pl.col("team").replace(D.TEAM_FIX).alias("team"))
        frames.append(d)
    if not frames:
        return pd.DataFrame(columns=["game_id", "team", "ol_same5"])
    d = pl.concat(frames, how="diagonal_relaxed").to_pandas()
    d = d.sort_values(["team", "season", "week", "offense_snaps"], ascending=[True, True, True, False])
    top = d.groupby(["team", "season", "week", "game_id"]).head(5)
    rows = []
    for team, g in top.groupby("team"):
        prev = None
        for (season, week, game_id), gg in g.groupby(["season", "week", "game_id"], sort=True):
            cur = set(gg["player"])
            rows.append({"game_id": game_id, "team": team,
                         "ol_same5": np.nan if prev is None else len(cur & prev) / 5.0})
            prev = cur
    return pd.DataFrame(rows)


def _ol_out(seasons) -> pd.DataFrame:
    """Per (season, week, team): offensive linemen designated Out or Doubtful on that week's report."""
    rows = []
    for s in seasons:
        p = os.path.join(D.RAW, "injuries", f"injuries_{s}.parquet")
        if not os.path.exists(p):
            continue
        d = pl.read_parquet(p)
        cols = set(d.columns)
        if not {"team", "week", "position", "report_status"} <= cols:
            continue
        d = d.filter(pl.col("position").is_in(list(OL_POS)) & pl.col("report_status").is_in(["Out", "Doubtful"]))
        d = d.with_columns(pl.col("team").replace(D.TEAM_FIX).alias("team"))
        g = d.group_by(["team", "week"]).agg(pl.len().alias("ol_out")).with_columns(pl.lit(s).alias("season"))
        rows.append(g.to_pandas())
    if not rows:
        return pd.DataFrame(columns=["team", "week", "season", "ol_out"])
    return pd.concat(rows, ignore_index=True)


def raw_rush_tables(seasons) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(player-game rushing detail, team-game rushing detail) -- OUTCOMES, not features."""
    car = D.load("carries", seasons).to_pandas()
    car = car[car["qb_kneel"] == 0]
    car["stuff"] = (car["yards"] <= 0).astype(float)
    for k in (10, 15, 20):
        car[f"e{k}"] = (car["yards"] >= k).astype(float)
    pg = car.groupby(["game_id", "season", "week", "team", "player_id"]).agg(
        carries=("yards", "size"), stuffs=("stuff", "sum"), exp10=("e10", "sum"), exp15=("e15", "sum"),
        exp20=("e20", "sum"), rush_yards=("yards", "sum")).reset_index()
    pfr = _pfr_rush(seasons)
    pg = pg.merge(pfr.drop(columns=["team"]), on=["game_id", "player_id"], how="left")
    # team side, plus the QB share of designed rushes and the rush EPA of the carry population
    epa = car.groupby(["game_id", "team"]).agg(rush_epa=("yards", "sum")).reset_index()  # placeholder, replaced below
    tgv = D.load("team_games", seasons).to_pandas()[["game_id", "season", "week", "team", "opp", "home",
                                                     "designed_rush", "rush_att", "epa_play"]]
    tg = pg.groupby(["game_id", "season", "week", "team"]).agg(
        carries=("carries", "sum"), stuffs=("stuffs", "sum"), exp10=("exp10", "sum"), exp20=("exp20", "sum"),
        ybc=("ybc", "sum"), yac=("yac", "sum"), broken=("broken", "sum"), pfr_carries=("pfr_carries", "sum"),
        rush_yards=("rush_yards", "sum")).reset_index()
    qb = D.load("player_games", seasons).to_pandas()
    qb = qb[qb["position"] == "QB"].groupby(["game_id", "team"]).agg(qb_carries=("designed_carries", "sum")).reset_index()
    tg = tg.merge(qb, on=["game_id", "team"], how="left")
    tg["qb_carries"] = tg["qb_carries"].fillna(0.0)
    # rush EPA per attempt from play-by-play, offence side
    pbp_epa = _carry_epa(seasons)
    tg = tg.merge(pbp_epa, on=["game_id", "team"], how="left")
    tg = tg.merge(tgv[["game_id", "team", "opp", "home"]], on=["game_id", "team"], how="left")
    tg = tg.merge(_ol_continuity(seasons), on=["game_id", "team"], how="left")
    tg = tg.merge(_ol_out(seasons), on=["season", "week", "team"], how="left")
    tg["ol_out"] = tg["ol_out"].fillna(0.0)
    return pg, tg


def _carry_epa(seasons) -> pd.DataFrame:
    """Summed EPA on designed rushes, per (game, team).  Read straight from the cached carry rows' source."""
    frames = []
    for s in seasons:
        p = os.path.join(D.RAW, "pbp", f"play_by_play_{s}.parquet")
        if not os.path.exists(p):
            continue
        d = pl.read_parquet(p, columns=["game_id", "posteam", "rush_attempt", "qb_kneel", "epa", "season_type", "play_type"])
        d = d.filter((pl.col("rush_attempt") == 1) & (pl.col("qb_kneel") == 0) & pl.col("posteam").is_not_null()
                     & pl.col("season_type").is_in(["REG", "POST"]))
        frames.append(d.group_by(["game_id", "posteam"]).agg(pl.col("epa").sum().alias("rush_epa")))
    if not frames:
        return pd.DataFrame(columns=["game_id", "team", "rush_epa"])
    out = pl.concat(frames, how="diagonal_relaxed").to_pandas().rename(columns={"posteam": "team"})
    out["team"] = out["team"].replace(D.TEAM_FIX)
    return out


# ----------------------------------------------------------------------------------------- priors
@dataclass(frozen=True)
class RushPriors:
    """Frozen shrinkage targets for the rushing enrichment, fitted on seasons strictly earlier than the
    rows they are applied to -- the same discipline as ``features.PriorSet`` and for the same reason."""
    team_rate: dict
    team_den: dict
    player_rate: dict
    player_rate_all: dict
    ol_same5: float
    fit_seasons: tuple
    version: str = RUSH_PRIORS_VERSION

    def to_dict(self):
        return asdict(self) | {"fit_seasons": list(self.fit_seasons)}

    @classmethod
    def from_dict(cls, d):
        return cls(team_rate=d["team_rate"], team_den=d["team_den"], player_rate=d["player_rate"],
                   player_rate_all=d["player_rate_all"], ol_same5=d["ol_same5"],
                   fit_seasons=tuple(d["fit_seasons"]), version=d.get("version", RUSH_PRIORS_VERSION))

    def player_prior(self, position, rate: str) -> np.ndarray:
        pos = np.asarray(position, dtype=object)
        out = np.full(len(pos), float(self.player_rate_all[rate]))
        for p in np.unique(pos):
            v = self.player_rate.get(f"{p}|{rate}")
            if v is not None:
                out[pos == p] = float(v)
        return out


def fit_rush_priors(pg_fit: pd.DataFrame, tg_fit: pd.DataFrame, position_of: dict | None = None,
                    fit_seasons=None) -> RushPriors:
    seasons = tuple(sorted(int(s) for s in tg_fit["season"].unique())) if fit_seasons is None else tuple(sorted(fit_seasons))
    team_rate, team_den = {}, {}
    for name, (num, den) in TEAM_RUSH_RATES.items():
        n = float(np.nansum(tg_fit[num].to_numpy(dtype=float))); d = float(np.nansum(tg_fit[den].to_numpy(dtype=float)))
        team_rate[name] = n / max(1.0, d)
        team_den[den] = float(np.nanmean(tg_fit[den].to_numpy(dtype=float)))
    pos = np.asarray([(position_of or {}).get(p, "RB") for p in pg_fit["player_id"]], dtype=object)
    player_rate, player_rate_all = {}, {}
    for name, (num, den) in PLAYER_RUSH_RATES.items():
        nv = pg_fit[num].to_numpy(dtype=float); dv = pg_fit[den].to_numpy(dtype=float)
        player_rate_all[name] = float(np.nansum(nv) / max(1.0, np.nansum(dv)))
        for p in np.unique(pos):
            m = pos == p
            player_rate[f"{p}|{name}"] = float(np.nansum(nv[m]) / max(1.0, np.nansum(dv[m])))
    return RushPriors(team_rate=team_rate, team_den=team_den, player_rate=player_rate,
                      player_rate_all=player_rate_all,
                      ol_same5=float(np.nanmean(tg_fit["ol_same5"].to_numpy(dtype=float))), fit_seasons=seasons)


# --------------------------------------------------------------------------------------- features
def team_rush_features(tg: pd.DataFrame, priors: RushPriors, cfg: F.FeatureConfig = F.FEATURE_CONFIG) -> pd.DataFrame:
    """Prior-only offence (``off_*``) and allowed (``def_*``) rushing features, plus the opponent-adjusted
    defensive versions.  Two passes: the raw offence feature first, then the strength of the offences a
    defence has actually faced -- both prior-only, so the composition is too."""
    if priors is None:
        raise F.MissingPriors("team_rush_features needs a RushPriors fitted on earlier seasons")
    t = tg.copy()
    allowed = t[["game_id", "team"] + [c for c in t.columns if c in
                 {"carries", "stuffs", "exp10", "exp20", "ybc", "yac", "broken", "pfr_carries", "rush_epa", "qb_carries"}]]
    allowed = allowed.rename(columns={c: f"a_{c}" for c in allowed.columns if c not in ("game_id", "team")}) \
                     .rename(columns={"team": "opp"})
    t = t.merge(allowed, on=["game_id", "opp"], how="left")
    t = t.sort_values(["team", "season", "week", "game_id"]).reset_index(drop=True)
    num_den = list(TEAM_RUSH_RATES.items())
    cols = []
    for _, (num, den) in num_den:
        cols += [num, den, f"a_{num}", f"a_{den}"]
    cols = list(dict.fromkeys(cols + ["ol_same5"]))
    X = t[cols].to_numpy(dtype=float)
    S, N, _ = F.decayed_prior_sums(t["team"].to_numpy(), None, t["season"].to_numpy(), X,
                                   cfg.team_halflife, cfg.team_season_carry)
    ix = {c: i for i, c in enumerate(cols)}
    k = cfg.team_shrink_k
    for name, (num, den) in num_den:
        prior = priors.team_rate[name]; den_prior = k * priors.team_den[den]
        for pre, sfx in (("off_", ""), ("def_", "a_")):
            t[f"{pre}{name}"] = (S[:, ix[sfx + num]] + prior * den_prior) / (S[:, ix[sfx + den]] + den_prior)
    j = ix["ol_same5"]
    t["ol_continuity"] = (S[:, j] + k * priors.ol_same5) / (N[:, j] + k)
    # opponent adjustment: the strength of the offences this defence has faced, each measured by its own
    # prior-only offence feature at the time that game was played
    faced = t[["game_id", "team"] + [f"off_{n}" for n in ADJUSTED]].rename(
        columns={f"off_{n}": f"faced_{n}" for n in ADJUSTED}).rename(columns={"team": "opp"})
    t = t.merge(faced, on=["game_id", "opp"], how="left")
    t = t.sort_values(["team", "season", "week", "game_id"]).reset_index(drop=True)
    fc = [f"faced_{n}" for n in ADJUSTED]
    Sf, Nf, _ = F.decayed_prior_sums(t["team"].to_numpy(), None, t["season"].to_numpy(),
                                     t[fc].to_numpy(dtype=float), cfg.team_halflife, cfg.team_season_carry)
    for i, n in enumerate(ADJUSTED):
        league = priors.team_rate[n]
        faced_strength = np.where(Nf[:, i] > 0, Sf[:, i] / np.maximum(Nf[:, i], 1e-9), league)
        t[f"def_{n}_adj"] = t[f"def_{n}"] - (faced_strength - league)
    t["rush_features_version"] = RUSH_FEATURES_VERSION
    return t


def player_rush_features(pg: pd.DataFrame, priors: RushPriors, position_of: dict | None = None,
                         cfg: F.FeatureConfig = F.FEATURE_CONFIG) -> pd.DataFrame:
    if priors is None:
        raise F.MissingPriors("player_rush_features needs a RushPriors fitted on earlier seasons")
    p = pg.copy().sort_values(["player_id", "season", "week", "game_id"]).reset_index(drop=True)
    cols = []
    for _, (num, den) in PLAYER_RUSH_RATES.items():
        cols += [num, den]
    cols = list(dict.fromkeys(cols))
    X = p[cols].to_numpy(dtype=float)
    S, _, _ = F.decayed_prior_sums(p["player_id"].to_numpy(), None, p["season"].to_numpy(), X,
                                   cfg.player_halflife_long, cfg.player_season_carry)
    ix = {c: i for i, c in enumerate(cols)}
    pos = np.asarray([(position_of or {}).get(x, "RB") for x in p["player_id"]], dtype=object)
    k = cfg.rate_shrink_k
    for name, (num, den) in PLAYER_RUSH_RATES.items():
        prior = priors.player_prior(pos, name)
        p[f"rt_{name}"] = (S[:, ix[num]] + k * prior) / (S[:, ix[den]] + k)
        p[f"rt_{name}_n"] = S[:, ix[den]]
    p["rush_features_version"] = RUSH_FEATURES_VERSION
    return p


# --------------------------------------------------------------------------------- feature groups
# The ablation arms.  Each is a list of columns added to models.CARRY_FEATURES.
ARMS = {
    "baseline": [],
    "ol": ["off_ybc_att", "ol_continuity", "ol_out", "off_stuff_rate"],
    "front": ["def_ybc_att_adj", "def_stuff_rate_adj", "def_rush_epa_att_adj", "def_exp10_rate"],
    "runner": ["rt_ybc_att", "rt_yac_att", "rt_stuff_rate", "rt_broken_att"],
    "context": ["off_qb_rush_share", "indoor"],
}
ARMS["combined"] = ARMS["ol"] + ARMS["front"] + ARMS["runner"] + ARMS["context"]


def attach(car: pd.DataFrame, tg_feat: pd.DataFrame, pg_feat: pd.DataFrame, schedule: pd.DataFrame) -> pd.DataFrame:
    """Join the enrichment onto per-carry rows (which already carry the base features)."""
    tcols = ["game_id", "team"] + sorted({c for c in tg_feat.columns
                                          if c.startswith(("off_", "def_", "ol_")) and c in set(ARMS["combined"])})
    pcols = ["game_id", "player_id"] + sorted({c for c in pg_feat.columns if c in set(ARMS["combined"])})
    out = car.merge(tg_feat[tcols], on=["game_id", "team"], how="left", suffixes=("", "_rush"))
    out = out.merge(pg_feat[pcols], on=["game_id", "player_id"], how="left", suffixes=("", "_rush"))
    roof = schedule[["game_id", "roof"]].copy()
    roof["indoor"] = roof["roof"].isin(["dome", "closed"]).astype(float)
    return out.merge(roof[["game_id", "indoor"]], on="game_id", how="left")
