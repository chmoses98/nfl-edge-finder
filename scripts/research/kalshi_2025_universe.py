#!/usr/bin/env python3
"""Summarize the archived (historical-tier) Kalshi NFL universe from backfill market lists: counts, settled share,
YES rates by family/threshold, volume/OI distributions, and how many single-game markets join to nflverse games."""
import glob, json, os, sys, collections
import polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi.classifier import classify
MD = sys.argv[1] if len(sys.argv) > 1 else "/home/user/_md"
games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).filter(pl.col("season") >= 2024)
gk = {(r["gameday"], r["away_team"], r["home_team"]): r["game_id"] for r in games.select("gameday", "away_team", "home_team", "game_id").to_dicts()}
rows = []
for f in sorted(glob.glob(os.path.join(MD, "data/kalshi/backfill/markets/*.jsonl"))):
    for line in open(f):
        m = json.loads(line); s = classify(m)
        rows.append({"series": s.series_ticker, "family": s.family, "period": s.period, "stat": s.stat, "threshold": s.threshold, "team": s.team, "player": s.player_name,
                     "game_date": s.game_date, "game_id": gk.get((s.game_date, s.away_team, s.home_team)) if s.game_date else None,
                     "status": m.get("status"), "result": m.get("result"), "volume": float(m.get("volume_fp") or 0), "oi": float(m.get("open_interest_fp") or 0),
                     "open_time": m.get("open_time"), "close_time": m.get("close_time"), "settled": m.get("result") in ("yes", "no")})
d = pl.DataFrame(rows, infer_schema_length=None)
os.makedirs(os.path.join(ROOT, "research/kalshi_2025"), exist_ok=True)
d.write_parquet(os.path.join(ROOT, "research/kalshi_2025/archived_markets.parquet"))
print("archived markets:", d.height, "settled:", int(d["settled"].sum()), "with nflverse game_id:", int(d["game_id"].is_not_null().sum()))
print(d.group_by(["family", "period"]).agg(pl.len().alias("n"), pl.col("settled").sum().alias("settled"), (pl.col("result") == "yes").mean().round(3).alias("yes_rate"),
                                          pl.col("volume").median().round(1).alias("med_vol"), (pl.col("volume") > 0).mean().round(2).alias("traded_share"), pl.col("game_id").is_not_null().mean().round(2).alias("game_join")).sort("n", descending=True).head(30))
print("close_time range:", d["close_time"].min(), d["close_time"].max())
ps = d.filter((pl.col("family") == "PLAYER_STAT") & pl.col("settled"))
print(ps.group_by("stat").agg(pl.len(), (pl.col("result") == "yes").mean().round(3).alias("yes_rate"), pl.col("volume").median().round(1).alias("med_vol")).sort("len", descending=True))
