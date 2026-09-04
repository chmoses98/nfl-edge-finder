#!/usr/bin/env python3
"""Measure P(player takes >=1 offensive snap | official game-status designation), 2015-2025.

The availability priors in nfl_edge/settlement/availability.py were round numbers. They scale EVERY player-prop
contract value (Kalshi pays $0 to a YES holder when the player is inactive), so a guessed 0.97 vs a measured
0.99 is a systematic 2% mispricing on every prop. This measures them from nflverse injury reports + PFR snap
counts, restricted to players with an established offensive role so deep-bench non-participation does not
contaminate the estimate.

Outputs research/availability/results.json and prints the table that seeds STATE_PLAY_RATES.
"""
import json, os, sys
import numpy as np, polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "research", "availability"); os.makedirs(OUT, exist_ok=True)
SEASONS = range(2015, 2026)
xw = pl.read_parquet(os.path.join(ROOT, "data/silver/player_crosswalk.parquet")).select("gsis_id", "pfr_id").filter(pl.col("pfr_id").is_not_null()).unique("pfr_id")
snaps, inj, games = [], [], []
for s in SEASONS:
    sp = os.path.join(ROOT, f"data/raw/nflverse/snap_counts/snap_counts_{s}.parquet")
    ip = os.path.join(ROOT, f"data/raw/nflverse/injuries/injuries_{s}.parquet")
    if not (os.path.exists(sp) and os.path.exists(ip)):
        continue
    sc = pl.read_parquet(sp).filter(pl.col("game_type") == "REG").select("season", "week", "game_id", "pfr_player_id", "team", "position", "offense_snaps")
    sc = sc.join(xw, left_on="pfr_player_id", right_on="pfr_id", how="inner")
    snaps.append(sc.select(pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32), pl.col("gsis_id").cast(pl.Utf8),
                           pl.col("team").cast(pl.Utf8), pl.col("position").cast(pl.Utf8), pl.col("offense_snaps").cast(pl.Float64)))
    idf = pl.read_parquet(ip)
    tcol = "season_type" if "season_type" in idf.columns else "game_type"
    inj.append(idf.filter(pl.col(tcol) == "REG").select(
        pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32), pl.col("gsis_id").cast(pl.Utf8),
        pl.col("team").cast(pl.Utf8), pl.col("report_status").cast(pl.Utf8), pl.col("practice_status").cast(pl.Utf8)))
SN = pl.concat(snaps); IN = pl.concat(inj)
SN = SN.with_columns(pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32))
IN = IN.with_columns(pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32))
# team-week rosters of players with an ESTABLISHED role: >=10 offensive snaps in any of the previous 3 weeks
SN = SN.sort(["gsis_id", "season", "week"])
# Full player-week GRID: a player who is inactive is ABSENT from the snap file, so participation cannot be
# measured from that file alone. Build every (player, season, week) the player's team actually played, then
# left-join snaps; a null means he did not dress.
team_weeks = SN.select("season", "week", "team").unique()
player_teams = SN.select("gsis_id", "season", "team", "position").unique(["gsis_id", "season", "team"])
GRID = player_teams.join(team_weeks, on=["season", "team"], how="inner")
GRID = GRID.join(SN.select("gsis_id", "season", "week", "offense_snaps"), on=["gsis_id", "season", "week"], how="left")
GRID = GRID.sort(["gsis_id", "season", "week"]).with_columns(pl.col("offense_snaps").fill_null(0.0).alias("snaps0"))
GRID = GRID.with_columns([
    pl.col("snaps0").shift(1).over(["gsis_id", "season"]).alias("s1"),
    pl.col("snaps0").shift(2).over(["gsis_id", "season"]).alias("s2"),
    pl.col("snaps0").shift(3).over(["gsis_id", "season"]).alias("s3"),
]).with_columns(pl.max_horizontal("s1", "s2", "s3").alias("prior_max_snaps"))
E = GRID.filter(pl.col("prior_max_snaps") >= 10)          # established offensive role in the last 3 weeks
IN2 = IN.with_columns(pl.lit(True).alias("on_report"))
E = E.join(IN2, on=["season", "week", "gsis_id"], how="left")
E = E.with_columns([
    pl.when(pl.col("on_report").is_null()).then(pl.lit("NOT_ON_REPORT"))
      .when(pl.col("report_status").is_null()).then(pl.lit("REPORTED_NO_STATUS"))
      .otherwise(pl.col("report_status")).alias("status"),
    (pl.col("offense_snaps").fill_null(0.0) > 0).alias("played"),
    (pl.col("offense_snaps").is_not_null() & (pl.col("offense_snaps") == 0)).alias("dressed_no_snap"),
    pl.col("offense_snaps").is_null().alias("did_not_dress"),
])
res = {"n_player_weeks": E.height, "seasons": [int(E["season"].min()), int(E["season"].max())]}
tab = E.group_by("status").agg(pl.len().alias("n"), pl.col("played").mean().alias("p_plays"),
                               pl.col("dressed_no_snap").mean().alias("p_dressed_no_snap"),
                               pl.col("did_not_dress").mean().alias("p_did_not_dress")).sort("n", descending=True)
print("Participation for established-role offensive players, by official game-status designation")
print(f"(player-weeks: {E.height}, seasons {res['seasons'][0]}-{res['seasons'][1]})")
print(tab.to_pandas().to_string(index=False))
res["by_status"] = tab.to_dicts()
prac = E.filter(pl.col("status").is_in(["NOT_ON_REPORT", "REPORTED_NO_STATUS"])).with_columns(
    pl.col("practice_status").fill_null("NONE")).group_by("practice_status").agg(
    pl.len().alias("n"), pl.col("played").mean().alias("p_plays")).sort("n", descending=True)
print("\nNo game-status designation, by practice participation:")
print(prac.to_pandas().to_string(index=False))
res["no_status_by_practice"] = prac.to_dicts()
byseason = E.group_by(["season", "status"]).agg(pl.len().alias("n"), pl.col("played").mean().alias("p_plays"))
res["by_season_status"] = byseason.filter(pl.col("n") >= 30).sort(["status", "season"]).to_dicts()
print("\nStability of the Questionable rate by season:")
print(byseason.filter((pl.col("status") == "Questionable") & (pl.col("n") >= 30)).sort("season").to_pandas().to_string(index=False))
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)
