"""The 2025 Kalshi player-prop archive as an evaluation set: one row per settled rung with the quotes at
each archived horizon, resolved to the nflverse game and GSIS player.

Reads ``data/kalshi/backfill/horizons/*.jsonl`` on the market-data branch (written by the backfill
workflows) and ``data/silver/kalshi_player_map_2025.parquet``.  Mirrors the loader of
``scripts/research/player_engine_v2_study.py`` so the two studies score the same contracts.
"""
from __future__ import annotations

import glob
import json
import os

import pandas as pd
import polars as pl

from . import data as D

STAT_MAP = {"passing_yards": "pass_yards", "rushing_yards": "rush_yards", "receiving_yards": "rec_yards",
            "receptions": "receptions", "passing_tds": "pass_td", "touchdowns": "any_td",
            "carries": "carries", "attempts": "attempts", "completions": "completions"}
HORIZONS = ["T-24h", "T-6h", "T-90m", "T-0"]


def load_rungs(market_data: str, season: int = 2025, horizons=HORIZONS) -> pd.DataFrame:
    pmap = pl.read_parquet(os.path.join(D.ROOT, "data", "silver", f"kalshi_player_map_{season}.parquet"))
    pmap = pmap.filter(pl.col("gsis_id").is_not_null() & pl.col("status").str.starts_with("RESOLVED"))
    kid2gsis = dict(zip(pmap["kalshi_player_id"].to_list(), pmap["gsis_id"].to_list()))
    games = D.schedule().filter(pl.col("season") == season)
    gk = {(r["gameday"], r["away_team"], r["home_team"]): (r["game_id"], r["week"])
          for r in games.select("gameday", "away_team", "home_team", "game_id", "week").to_dicts()}
    rows = []
    for f in sorted(glob.glob(os.path.join(market_data, "data", "kalshi", "backfill", "horizons", "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("family") != "PLAYER_STAT" or r.get("result") not in ("yes", "no") or r.get("stat") not in STAT_MAP \
                    or r.get("threshold") is None or r.get("operator") != ">=":
                continue
            gw = gk.get((r["game_date"], r["away_team"], r["home_team"]))
            gs = kid2gsis.get(r.get("player_kalshi_id"))
            if not gw or not gs:
                continue
            rec = {"ticker": r["ticker"], "game_id": gw[0], "week": int(gw[1]), "player_id": gs, "kalshi_stat": r["stat"],
                   "stat": STAT_MAP[r["stat"]], "k": float(r["threshold"]), "y": 1.0 if r["result"] == "yes" else 0.0}
            snaps = r.get("snaps") or {}
            for h in horizons:
                s = snaps.get(h) or {}
                rec[f"bid_{h}"] = s.get("bid"); rec[f"ask_{h}"] = s.get("ask")
            rows.append(rec)
    return pd.DataFrame(rows)


def market_ladders(rungs: pd.DataFrame, horizon: str, max_width: float = 0.20) -> dict:
    """{(game_id, player_id, stat): market_distribution record} at one horizon, from the archived quotes."""
    from nfl_edge.engines.player.market_dist import market_distribution
    out = {}
    b, a = f"bid_{horizon}", f"ask_{horizon}"
    for key, g in rungs.groupby(["game_id", "player_id", "stat"]):
        lad = [{"threshold": r.k, "yes_bid": getattr(r, b), "yes_ask": getattr(r, a)} for r in g.itertuples()
               if getattr(r, b) is not None and getattr(r, a) is not None]
        if not lad:
            continue
        out[key] = market_distribution(g["kalshi_stat"].iloc[0], lad, max_width=max_width)
    return out
