"""Point-in-time features for NFL team-games and player-games (pf_core.pit helpers, shifted).

Every feature attached to a game uses only games that kicked off earlier:
  * own-history features: pf_core.pit.lagged_features (shift-one within entity; NaN = unobserved)
  * opponent features: pf_core.pit.rolling_ridge_ratings refitted before every (season, week) block, plus the raw
    shrunk "allowed" comparator (pf_core.pit.rolling_opponent_allowed)
  * game environment: closing spread / total from the nflverse schedule (pregame market information)
  * teammate availability: final injury-report designations for the game week (near-pregame, see data.injuries)
Upcoming games (no outcome yet) are carried as rows with NaN outcomes so the same code produces forward features.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pf_core import pit

TEAM_COLS = ["tm_attempts", "tm_carries", "points", "plays", "pass_rate", "ypa", "comp_pct", "ypt", "ypc",
             "pass_td_rate", "rush_td_rate", "catch_rate"]
RIDGE_TARGETS = {"tm_attempts": "pass_att", "tm_carries": "rush_att", "points": "points", "ypa": "ypa",
                 "comp_pct": "comp_pct", "ypt": "ypt", "ypc": "ypc", "pass_td_rate": "ptd_rate", "catch_rate": "catch_rate",
                 "plays": "plays", "pass_rate": "pass_rate"}
PLAYER_COLS = ["targets", "receptions", "receiving_yards", "carries", "rushing_yards", "attempts", "completions",
               "passing_yards", "passing_tds", "receiving_tds", "rushing_tds", "any_td", "n_td", "offense_pct",
               "tgt_per_att", "carry_share", "pass_share", "receiving_air_yards"]
HALFLIVES = (2, 4, 8, 16)


def _team_derived(tg: pd.DataFrame) -> pd.DataFrame:
    tg = tg.copy()
    sk = tg["tm_sacks_suffered"].fillna(0)
    tg["plays"] = tg.tm_attempts + sk + tg.tm_carries
    tg["pass_rate"] = (tg.tm_attempts + sk) / tg.plays
    tg["ypa"] = tg.tm_passing_yards / tg.tm_attempts
    tg["comp_pct"] = tg.tm_completions / tg.tm_attempts
    tg["ypt"] = tg.tm_receiving_yards / tg.tm_targets
    tg["catch_rate"] = tg.tm_receptions / tg.tm_targets
    tg["ypc"] = tg.tm_rushing_yards / tg.tm_carries
    tg["pass_td_rate"] = tg.tm_passing_tds / tg.tm_attempts
    tg["rush_td_rate"] = tg.tm_rushing_tds / tg.tm_carries
    return tg


def team_features(tg: pd.DataFrame, ridge_alpha: float = 10.0, upcoming_block: int | None = None) -> pd.DataFrame:
    """tg: data.team_games() (played games + optionally the single upcoming block)."""
    tg = _team_derived(tg)
    if upcoming_block is not None:
        tg = tg[tg.played | (tg.block == upcoming_block)]
    else:
        tg = tg[tg.played]
    tg = pit.sort_chrono(tg, "team", "kickoff_utc", "game_id")
    f = pit.lagged_features(tg, "team", TEAM_COLS, halflives=(4, 8), season_col="season", prefix="own_")
    # defensive "allowed" history: the opponent's offensive outcome, keyed by the defending team
    d = tg[["game_id", "opp", "team", "kickoff_utc", "season"] + TEAM_COLS].rename(columns={"opp": "def_team", "team": "off_team"})
    d = pit.sort_chrono(d, "def_team", "kickoff_utc", "game_id")
    d = pit.lagged_features(d, "def_team", TEAM_COLS, halflives=(4, 8), season_col="season", prefix="alw_")
    alw = [c for c in d.columns if c.startswith("alw_")]
    f = f.merge(d[["game_id", "def_team"] + alw].rename(columns={"def_team": "opp"}), on=["game_id", "opp"], how="left")
    # schedule-adjusted ridge ratings (fit on blocks strictly before this block)
    played = tg[tg.played | (tg.block == upcoming_block)] if upcoming_block else tg
    for col, name in RIDGE_TARGETS.items():
        g = played[["block", "team", "opp", "home", "season", col]].copy()
        if upcoming_block is not None:
            g.loc[g.block == upcoming_block, col] = g.loc[g.block == upcoming_block, col].fillna(0.0)
            # rows of the upcoming block never enter a fit (rolling_ridge_ratings trains on block < b)
        g = g[g[col].notna()]
        r = pit.rolling_ridge_ratings(g, "block", "team", "opp", col, home_col="home", alpha=ridge_alpha,
                                      season_col="season", prior_season_decay=0.5)
        off = r[["block", "team", "off_rating", "n_off", "intercept", "home_adv"]].rename(
            columns={"off_rating": f"rr_off_{name}", "n_off": f"rr_noff_{name}", "intercept": f"rr_int_{name}",
                     "home_adv": f"rr_home_{name}"})
        de = r[["block", "team", "def_rating", "n_def"]].rename(
            columns={"team": "opp", "def_rating": f"rr_def_{name}", "n_def": f"rr_ndef_{name}"})
        f = f.merge(off, on=["block", "team"], how="left").merge(de, on=["block", "opp"], how="left")
        # multiplicative opponent factor relative to the PIT league level
        f[f"opp_factor_{name}"] = (f[f"rr_int_{name}"] + f[f"rr_def_{name}"]) / f[f"rr_int_{name}"]
        f[f"rr_pred_{name}"] = f[f"rr_int_{name}"] + f[f"rr_off_{name}"] + f[f"rr_def_{name}"] + f[f"rr_home_{name}"] * f.home
    # PIT league means (expanding over earlier blocks) for priors
    for col in ("tm_attempts", "tm_carries", "points", "plays"):
        by = tg[tg.played].groupby("block")[col].agg(["sum", "count"]).sort_index()
        lm = (by["sum"].cumsum() - by["sum"]) / (by["count"].cumsum() - by["count"]).replace(0, np.nan)
        lm = lm.reindex(sorted(set(f.block)), method="ffill") if upcoming_block else lm
        f[f"league_{col}"] = f.block.map(lm.ffill()).fillna(tg[col].mean())
    return f


def player_features(pg: pd.DataFrame, halflives=HALFLIVES) -> pd.DataFrame:
    """pg: data.player_games() (+ optional upcoming rows with NaN outcomes). Adds lagged own-history features,
    last-4 rolling means for population definitions, role/continuity flags."""
    pg = pg.copy()
    pg["tgt_per_att"] = pg.targets / pg.tm_attempts.where(pg.tm_attempts > 0)
    pg = pit.sort_chrono(pg, "player_id", "kickoff_utc", "game_id")
    out = pit.lagged_features(pg, "player_id", PLAYER_COLS, halflives=halflives, season_col="season")
    g = out.groupby("player_id", sort=False)
    for c in ("targets", "carries", "attempts", "offense_pct", "tgt_per_att", "carry_share"):
        out[f"{c}_r4"] = g[c].transform(lambda s: s.shift(1).rolling(4, min_periods=1).mean())
        out[f"{c}_last"] = g[c].shift(1)
    out["prev_team"] = g["team"].shift(1)
    out["team_changed"] = (out.prev_team.notna() & (out.prev_team != out.team)).astype(int)
    out["days_since"] = (out.kickoff_utc - g["kickoff_utc"].shift(1)).dt.days
    out["games_in_season_before"] = out["targets_std_n"].fillna(0)
    out["career_games"] = out["targets_n"].fillna(0)
    return out


def teammate_availability(pf: pd.DataFrame, inj: pd.DataFrame) -> pd.DataFrame:
    """Pregame vacated opportunity per (game, team): sum of the PIT EWMA target-per-attempt and carry share of teammates
    designated OUT or DOUBTFUL on the final injury report, among teammates who played in the team's last 3 games.

    Also the 'oracle' version (teammates with role who did NOT participate, a post-game fact) to bound the value."""
    inj = inj[inj.report_status.isin(["Out", "Doubtful"])][["season", "week", "gsis_id", "report_status"]]
    # each player's role entering the game = EWMA including all his earlier games (shifted features on his next row are
    # not available for an absent game, so use 'post-game EWMA' of his most recent game: recompute un-shifted)
    p = pf[["player_id", "team", "season", "week", "block", "kickoff_utc", "targets", "tgt_per_att", "carry_share",
            "tm_attempts", "position"]].copy()
    p = p.sort_values(["player_id", "kickoff_utc"])
    g = p.groupby("player_id", sort=False)
    p["role_tpa"] = g["tgt_per_att"].transform(lambda s: s.ewm(halflife=4, ignore_na=True).mean())
    p["role_cs"] = g["carry_share"].transform(lambda s: s.ewm(halflife=4, ignore_na=True).mean())
    # team game index
    tgi = pf[["team", "block"]].drop_duplicates().sort_values(["team", "block"])
    tgi["tidx"] = tgi.groupby("team").cumcount()
    p = p.merge(tgi, on=["team", "block"], how="left")
    rows = []
    # for every team-game, candidate teammates = played in any of the previous 3 team games
    last = p[["player_id", "team", "tidx", "role_tpa", "role_cs", "position"]]
    for lag in (1, 2, 3):
        x = last.copy()
        x["tidx"] = x.tidx + lag
        x["lag"] = lag
        rows.append(x)
    cand = pd.concat(rows).sort_values("lag").drop_duplicates(["player_id", "team", "tidx"], keep="first")
    cand = cand.merge(tgi, on=["team", "tidx"], how="inner")      # -> block of the game being predicted
    cand["season"] = cand.block // 100
    cand["week"] = cand.block % 100
    played = set(zip(p.player_id, p.block))
    cand["played"] = [(a, b) in played for a, b in zip(cand.player_id, cand.block)]
    cand = cand.merge(inj.rename(columns={"gsis_id": "player_id"}), on=["season", "week", "player_id"], how="left")
    cand["listed_out"] = cand.report_status.notna()
    agg = cand.groupby(["team", "block"]).apply(lambda d: pd.Series({
        "vac_tpa_inj": d.loc[d.listed_out, "role_tpa"].fillna(0).sum(),
        "vac_cs_inj": d.loc[d.listed_out, "role_cs"].fillna(0).sum(),
        "vac_tpa_oracle": d.loc[~d.played, "role_tpa"].fillna(0).sum(),
        "vac_cs_oracle": d.loc[~d.played, "role_cs"].fillna(0).sum(),
        "n_out_listed": int(d.listed_out.sum()),
    }), include_groups=False).reset_index()
    return agg
