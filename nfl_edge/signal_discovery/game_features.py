"""Market-blind, outcome-blind NFL game features. RESEARCH ONLY.

*** OPPONENT ADJUSTMENT ***
Reuses the repository's preregistered solver unchanged (``nfl_edge.sim.opponent_adjust.solve``,
sim-oppadj-1.0.0): at every (season, week) snapshot, a weighted ridge

    y[g, t] = mu + off[t] + def[opp] + h * home_sign + e

on the three previous seasons plus the current season's EARLIER weeks (8-week half-life, 0.5 season carry),
with the ridge strength per metric chosen by ``select_lambdas`` on seasons Y-2 and Y-1 only. The metric table
is the module's own ``metric_table`` plus a few extra per-team-game metrics computed here from the same
play-by-play (early-down EPA, explosive pass / rush rates, points, pressure rate). Applying the same solver to
more metrics is not a new adjustment method.

*** WHAT A FEATURE ROW MAY READ ***
Team-game metrics of games strictly before the snapshot week, and the schedule's identity / site / rest /
division / roof fields for the target game. It never reads ``spread_line``, ``total_line``, moneylines or any
odds column, and never the target game's own result (``tests/test_signal_discovery_nfl.py`` pins this).

*** SIGN CONVENTION (home perspective) ***
``mx_<side>.<m>``   the side's offense expectation against the opponent defense (mu + off + def_opp +/- hfa)
``net.<m>``         mx_home - mx_away for good-is-high metrics; mx_away - mx_home for bad-is-high
                    (sack_rate, pressure_rate): positive always favours HOME.
``q_<side>_off.<m>``/``q_<side>_def.<m>`` unit quality in league SDs at the snapshot, positive = better unit.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import polars as pl

from nfl_edge.sim import data as D
from nfl_edge.sim import opponent_adjust as OA

EXTRA_METRICS = ("early_epa", "explosive_pass_rate", "explosive_rush_rate", "points", "pressure_rate")
METRICS = tuple(OA.METRICS) + EXTRA_METRICS
BAD_IS_HIGH = {"sack_rate", "pressure_rate"}
NEUTRAL_METRICS = {"plays", "sec_per_play", "neutral_pass_rate", "neutral_proe"}  # tendencies, no good/bad
SCHEDULE_FIELDS = ("game_id", "season", "week", "game_type", "gameday", "gametime", "home_team", "away_team",
                   "location", "home_rest", "away_rest", "div_game", "roof", "surface")


def _extras(season: int) -> pl.DataFrame:
    d = D._read_pbp(season).filter(pl.col("posteam").is_not_null() & pl.col("season_type").is_in(["REG", "POST"])
                                   & pl.col("play_type").is_in(["run", "pass"]))
    passed = (pl.col("pass_attempt") == 1) & (pl.col("sack") == 0)
    rush = (pl.col("rush_attempt") == 1) & (pl.col("qb_kneel") == 0)
    out = d.group_by(["game_id", "posteam"]).agg([
        pl.col("epa").filter(pl.col("down") <= 2).mean().alias("early_epa"),
        (passed & (pl.col("yards_gained") >= 20)).sum().alias("_xp"),
        passed.sum().alias("_np"),
        (rush & (pl.col("yards_gained") >= 10)).sum().alias("_xr"),
        rush.sum().alias("_nr"),
        (pl.col("qb_dropback") == 1).sum().alias("_db"),
    ]).with_columns([
        (pl.col("_xp") / pl.col("_np").clip(lower_bound=1)).alias("explosive_pass_rate"),
        (pl.col("_xr") / pl.col("_nr").clip(lower_bound=1)).alias("explosive_rush_rate"),
    ]).rename({"posteam": "team"})
    part_path = os.path.join(D.RAW, "pbp_participation", f"pbp_participation_{season}.parquet")
    if os.path.exists(part_path):
        part = pl.read_parquet(part_path, columns=["nflverse_game_id", "play_id", "was_pressure"]).rename(
            {"nflverse_game_id": "game_id"})
        drop = d.filter(pl.col("qb_dropback") == 1).select(["game_id", "play_id", "posteam"]).with_columns(
            pl.col("play_id").cast(pl.Int64))
        part = part.with_columns(pl.col("play_id").cast(pl.Int64))
        pr = drop.join(part, on=["game_id", "play_id"], how="left").group_by(["game_id", "posteam"]).agg([
            pl.col("was_pressure").cast(pl.Float64).mean().alias("pressure_rate"),
            pl.col("was_pressure").is_not_null().sum().alias("_pr_n")]).rename({"posteam": "team"})
        pr = pr.with_columns(pl.when(pl.col("_pr_n") >= 10).then(pl.col("pressure_rate")).otherwise(None).alias("pressure_rate"))
        out = out.join(pr.select(["game_id", "team", "pressure_rate"]), on=["game_id", "team"], how="left")
    else:
        out = out.with_columns(pl.lit(None, dtype=pl.Float64).alias("pressure_rate"))
    out = out.with_columns(pl.col("team").replace(D.TEAM_FIX))
    return out.select(["game_id", "team", "early_epa", "explosive_pass_rate", "explosive_rush_rate", "pressure_rate"])


def metric_table(seasons) -> pd.DataFrame:
    """sim metric table + the extra metrics. One row per (game, offence)."""
    mt = OA.metric_table(seasons)
    ex = pl.concat([_extras(s) for s in seasons], how="diagonal_relaxed")
    ex = pd.DataFrame(ex.to_dicts())
    tg = pd.DataFrame(D.load("team_games", seasons).select(["game_id", "team", "points"]).to_dicts())
    mt = mt.merge(ex, on=["game_id", "team"], how="left").merge(tg, on=["game_id", "team"], how="left")
    return mt.sort_values(["season", "week", "game_id", "team"]).reset_index(drop=True)


def _snapshot_ratings(mt: pd.DataFrame, season: int, week: int, lams: dict, last_week: dict) -> dict:
    prior = mt[((mt["season"] < season) & (mt["season"] >= season - OA.WINDOW_SEASONS))
               | ((mt["season"] == season) & (mt["week"] < week))]
    out = {}
    for m in METRICS:
        out[m] = OA.solve(prior, m, lams.get(m, 8.0), season, week, last_week)
    cur_raw = {}
    # unadjusted comparator (window means, same weights) for the raw-EPA baseline
    u = OA.snapshot_unadjusted(mt, season, week, last_week, metrics=("epa_play",))
    for _, r in u.iterrows():
        cur_raw[r["team"]] = r["ux_epa_play"]
    out["_raw_epa"] = cur_raw
    out["_prior_max_key"] = (int(prior["season"].max()), int(prior.loc[prior["season"] == prior["season"].max(), "week"].max())) if len(prior) else None
    return out


def _z(sol: dict, part: str, team: str) -> float | None:
    vals = np.array(list(sol[part].values()), dtype=float)
    if team not in sol[part] or vals.std() == 0:
        return None
    return float((sol[part][team] - vals.mean()) / vals.std())


def game_rows(mt: pd.DataFrame, schedule: pd.DataFrame, seasons, lambdas_by_season: dict) -> pd.DataFrame:
    """One market-blind feature row per scheduled game in ``seasons`` (home perspective)."""
    lw = OA._last_weeks(mt)
    rows = []
    sched = schedule[list(SCHEDULE_FIELDS)]
    for season in seasons:
        lams = lambdas_by_season[season]
        for week in sorted(sched.loc[sched["season"] == season, "week"].unique()):
            snap = _snapshot_ratings(mt, int(season), int(week), lams, lw)
            for _, g in sched[(sched["season"] == season) & (sched["week"] == week)].iterrows():
                h, a = g["home_team"], g["away_team"]
                hs = 0.0 if g["location"] == "Neutral" else 1.0
                row = {k: g[k] for k in SCHEDULE_FIELDS}
                row["neutral"] = hs == 0.0
                row["history_through"] = f"{snap['_prior_max_key'][0]}-W{snap['_prior_max_key'][1]:02d}" if snap["_prior_max_key"] else None
                for m in METRICS:
                    sol = snap[m]
                    if sol is None or h not in sol["off"] or a not in sol["off"]:
                        for k in (f"mx_home.{m}", f"mx_away.{m}", f"net.{m}", f"q_home_off.{m}", f"q_home_def.{m}",
                                  f"q_away_off.{m}", f"q_away_def.{m}"):
                            row[k] = None
                        continue
                    mxh = sol["mu"] + sol["off"][h] + sol["def"][a] + sol["hfa"] * hs
                    mxa = sol["mu"] + sol["off"][a] + sol["def"][h] - sol["hfa"] * hs
                    row[f"mx_home.{m}"], row[f"mx_away.{m}"] = mxh, mxa
                    sign = -1.0 if m in BAD_IS_HIGH else 1.0
                    row[f"net.{m}"] = None if m in NEUTRAL_METRICS else sign * (mxh - mxa)
                    for side, t in (("home", h), ("away", a)):
                        zo, zd = _z(sol, "off", t), _z(sol, "def", t)
                        # quality: offence good-is-high; a defence coefficient is what it ALLOWS
                        row[f"q_{side}_off.{m}"] = None if zo is None else (sign * zo if m not in NEUTRAL_METRICS else zo)
                        row[f"q_{side}_def.{m}"] = None if zd is None else (-sign * zd if m not in NEUTRAL_METRICS else zd)
                raw = snap["_raw_epa"]
                row["raw.epa_net"] = (raw.get(h) - raw.get(a)) if (h in raw and a in raw) else None
                _environment(row)
                rows.append(row)
    return pd.DataFrame(rows)


def _environment(row: dict) -> None:
    g = row.get
    pl_ = (g("mx_home.plays"), g("mx_away.plays"))
    row["env.plays"] = sum(pl_) if None not in pl_ else None
    sp = (g("mx_home.sec_per_play"), g("mx_away.sec_per_play"))
    row["env.sec_per_play"] = sum(sp) / 2 if None not in sp else None
    pr = (g("mx_home.neutral_pass_rate"), g("mx_away.neutral_pass_rate"))
    row["env.neutral_pass_rate"] = sum(pr) / 2 if None not in pr else None
    pts = (g("mx_home.points"), g("mx_away.points"))
    row["baseline.total"] = sum(pts) if None not in pts else None
    row["baseline.home_margin"] = pts[0] - pts[1] if None not in pts else None
    d = (g("q_home_def.epa_play"), g("q_away_def.epa_play"))
    row["def_quality_sum.epa"] = sum(d) if None not in d else None
    o = (g("q_home_off.epa_play"), g("q_away_off.epa_play"))
    row["off_quality_sum.epa"] = sum(o) if None not in o else None
    hr, ar = g("home_rest"), g("away_rest")
    row["ctx.rest_diff"] = (hr - ar) if hr is not None and ar is not None else None


def qb_change(schedule_with_qbs: pd.DataFrame) -> pd.DataFrame:
    """NEAR-PIT context: did each team's starting QB differ from its previous game's starter?

    The starter ids in the schedule are the REALISED starters. A starter is normally announced before
    kickoff, so this is treated as pregame-knowable but labelled NEAR_PIT (a surprise start is possible)."""
    s = schedule_with_qbs.sort_values(["season", "week"])
    long = pd.concat([
        s[["game_id", "season", "week", "home_team", "home_qb_id"]].rename(columns={"home_team": "team", "home_qb_id": "qb"}),
        s[["game_id", "season", "week", "away_team", "away_qb_id"]].rename(columns={"away_team": "team", "away_qb_id": "qb"}),
    ]).sort_values(["team", "season", "week"])
    long["prev_qb"] = long.groupby("team")["qb"].shift(1)
    long["prev_season"] = long.groupby("team")["season"].shift(1)
    long["qb_change"] = (long["qb"] != long["prev_qb"]) & long["prev_qb"].notna() & (long["prev_season"] == long["season"])
    return long[["game_id", "team", "qb_change"]]
