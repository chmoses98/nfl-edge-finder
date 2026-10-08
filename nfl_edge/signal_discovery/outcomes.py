"""NFL game outcomes, read only after the feature table is frozen. RESEARCH ONLY.

Final scores from the nflverse schedule; first-half scores from play-by-play (the score at the last play of
the second quarter). A schedule/pbp final-score disagreement is OUTCOME_MISMATCH and excluded.
"""

from __future__ import annotations

import os

import pandas as pd
import polars as pl

from nfl_edge.sim import data as D


def load_outcomes(schedule: pd.DataFrame, seasons) -> dict[str, dict]:
    half = {}
    final = {}
    for s in seasons:
        p = os.path.join(D.RAW, "pbp", f"play_by_play_{s}.parquet")
        if not os.path.exists(p):
            continue
        d = pl.read_parquet(p, columns=["game_id", "qtr", "total_home_score", "total_away_score", "play_id"])
        h = d.filter(pl.col("qtr") <= 2).sort(["game_id", "play_id"]).group_by("game_id").agg(
            [pl.col("total_home_score").last().alias("h"), pl.col("total_away_score").last().alias("a")])
        for r in h.iter_rows(named=True):
            half[r["game_id"]] = (r["h"], r["a"])
        f = d.sort(["game_id", "play_id"]).group_by("game_id").agg(
            [pl.col("total_home_score").last().alias("h"), pl.col("total_away_score").last().alias("a")])
        for r in f.iter_rows(named=True):
            final[r["game_id"]] = (r["h"], r["a"])
    out = {}
    for r in schedule.itertuples(index=False):
        if pd.isna(r.home_score) or pd.isna(r.away_score):
            continue
        hp, ap = float(r.home_score), float(r.away_score)
        status = "OK"
        if r.game_id in final and final[r.game_id] != (hp, ap):
            status = "OUTCOME_MISMATCH"
        h1 = half.get(r.game_id)
        out[r.game_id] = {"status": status, "home_points": hp, "away_points": ap, "home_margin": hp - ap,
                          "total_points": hp + ap, "overtime": bool(r.overtime) if not pd.isna(r.overtime) else None,
                          "home_1h": float(h1[0]) if h1 else None, "away_1h": float(h1[1]) if h1 else None}
    return out
