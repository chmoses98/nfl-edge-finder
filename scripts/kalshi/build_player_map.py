#!/usr/bin/env python3
"""Map Kalshi player UUIDs (custom_strike.football_player) to nflverse GSIS ids.

Evidence per Kalshi player: display name from market titles, team code from the
ticker token, jersey number from the ticker token. Matching is deterministic and
auditable: exact normalized-name match within the same team and season roster,
then jersey agreement as a tiebreaker/confirmation. No fuzzy matching at
prediction time: unresolved ids are written with status UNRESOLVED and must be
resolved by a human or a later exact match.

Usage: build_player_map.py --discovery-dir <dir> [--season 2026] -> data/silver/kalshi_player_map.parquet (+ .json)
"""
from __future__ import annotations
import argparse, json, os, sys, glob
import polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi.classifier import classify, KALSHI_TO_NFLVERSE  # noqa
from nfl_edge.data.ids import _norm_name  # noqa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discovery-dir", required=True)
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--extra-markets-glob", default="", help="optional jsonl files of raw markets (e.g. backfill lists)")
    a = ap.parse_args()
    obs = {}
    files = glob.glob(os.path.join(a.discovery_dir, "markets", "*.json"))
    markets = []
    for f in files:
        for st, v in json.load(open(f)).items():
            markets.extend(v["markets"])
    if a.extra_markets_glob:
        for f in glob.glob(a.extra_markets_glob):
            markets.extend(json.loads(l) for l in open(f))
    for m in markets:
        s = classify(m)
        if not s.player_kalshi_id or not s.player_name:
            continue
        rec = obs.setdefault(s.player_kalshi_id, {"names": {}, "teams": {}, "jerseys": {}, "team_uuid": s.team_kalshi_id, "n": 0})
        rec["n"] += 1
        rec["names"][s.player_name] = rec["names"].get(s.player_name, 0) + 1
        if s.team:
            rec["teams"][s.team] = rec["teams"].get(s.team, 0) + 1
        if s.jersey is not None:
            rec["jerseys"][s.jersey] = rec["jerseys"].get(s.jersey, 0) + 1
    ros = pl.read_parquet(os.path.join(ROOT, "data", "raw", "nflverse", "rosters", f"roster_{a.season}.parquet"))
    ros = ros.select("gsis_id", "full_name", "team", "jersey_number", "position", "status").filter(pl.col("gsis_id").is_not_null())
    ros = ros.with_columns(pl.col("full_name").map_elements(_norm_name, return_dtype=pl.Utf8).alias("name_key"),
                           pl.col("team").replace({"ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "JAC": "JAX", "LAR": "LA", "WSH": "WAS"}).alias("team"))
    players = pl.read_parquet(os.path.join(ROOT, "data", "raw", "nflverse", "players", "players.parquet")).select("gsis_id", "display_name", "latest_team", "position", "last_season", "jersey_number")
    players = players.with_columns(pl.col("display_name").map_elements(_norm_name, return_dtype=pl.Utf8).alias("name_key"))
    rows = []
    for kid, rec in obs.items():
        name = max(rec["names"], key=rec["names"].get)
        team = max(rec["teams"], key=rec["teams"].get) if rec["teams"] else None
        jersey = max(rec["jerseys"], key=rec["jerseys"].get) if rec["jerseys"] else None
        key = _norm_name(name)
        cand = ros.filter(pl.col("name_key") == key)
        status, gsis, method = "UNRESOLVED", None, None
        if team:
            c2 = cand.filter(pl.col("team") == team)
            if c2.height == 1:
                gsis, status, method = c2["gsis_id"][0], "RESOLVED", "name+team"
                if jersey is not None and c2["jersey_number"][0] is not None and int(c2["jersey_number"][0]) != jersey:
                    status, method = "RESOLVED_JERSEY_MISMATCH", "name+team(jersey differs)"
            elif c2.height > 1 and jersey is not None:
                c3 = c2.filter(pl.col("jersey_number") == jersey)
                if c3.height == 1:
                    gsis, status, method = c3["gsis_id"][0], "RESOLVED", "name+team+jersey"
        if gsis is None and cand.height == 1:
            gsis, status, method = cand["gsis_id"][0], "RESOLVED_TEAM_UNCONFIRMED", "name only (unique in season roster)"
        if gsis is None:
            c4 = players.filter((pl.col("name_key") == key) & (pl.col("last_season") >= a.season - 1))
            if c4.height == 1:
                gsis, status, method = c4["gsis_id"][0], "RESOLVED_PLAYERS_TABLE", "name only (players.parquet, unique recent)"
        rows.append({"kalshi_player_id": kid, "kalshi_team_id": rec["team_uuid"], "name": name, "team": team, "jersey": jersey, "n_markets": rec["n"],
                     "gsis_id": gsis, "status": status, "method": method, "season": a.season, "all_names": json.dumps(rec["names"])})
    df = pl.DataFrame(rows)
    out = os.path.join(ROOT, "data", "silver", "kalshi_player_map.parquet")
    df.write_parquet(out)
    df.write_json(os.path.join(ROOT, "data", "silver", "kalshi_player_map.json"))
    print(df.group_by("status").len().sort("len", descending=True))
    print(df.filter(pl.col("status") == "UNRESOLVED").select("name", "team", "jersey", "n_markets").head(30))


if __name__ == "__main__":
    main()
