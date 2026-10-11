#!/usr/bin/env python3
"""Command for the shared PURE gate's `rerun` (sift-sports-intelligence/pure-contract/pure_gate.py).

The gate needs the market inputs as separate files it can delete or randomise. The nflverse schedule mixes both,
so the experiment splits it once: a sports-only data root (stats, snaps, crosswalk, schedule WITHOUT market
columns) and `market_lines.csv` (game_id + the schedule's spread / total / moneyline / odds columns). This command
rejoins them the way a production loader would (a missing or unreadable market file -> no market columns) and runs

    default     PURE_PLAYER_V1 for --season, writing the kit sidecar rows to {out}/pure_forecasts.jsonl
    --control   the negative control: DATA_PLAYER_V4's VolumeModel (market_env=True) through the repository's
                market-reading loader, writing its team-volume predictions to the same file name

    python3 scripts/research/pure_player_v1_rerun_cli.py --sports-root DIR --market-lines FILE --season 2025 --out DIR [--control]
    python3 scripts/research/pure_player_v1_rerun_cli.py --split-from DATA_ROOT --sports-root DIR --market-lines FILE   # one-off split
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "research"))
from nfl_edge.engines.player.pure_v1 import mutation as MU                     # noqa: E402
import pure_player_v1_mutation as PM                                           # noqa: E402

RAW = ("stats_player", "snap_counts", "players", "injuries", "weekly_rosters")


def split(src: str, sports_root: str, market_lines: str) -> None:
    g = pd.read_csv(os.path.join(src, "data/raw/nflverse/schedules/games.csv"), low_memory=False)
    cols = [c for c in MU.MARKET_SCHEDULE_COLUMNS if c in g.columns]
    os.makedirs(os.path.join(sports_root, "data/raw/nflverse/schedules"), exist_ok=True)
    os.makedirs(os.path.join(sports_root, "data/silver"), exist_ok=True)
    g.drop(columns=cols).to_csv(os.path.join(sports_root, "data/raw/nflverse/schedules/games.csv"), index=False)
    os.makedirs(os.path.dirname(os.path.abspath(market_lines)), exist_ok=True)
    g[["game_id"] + cols].to_csv(market_lines, index=False)
    for d in RAW:
        dst = os.path.join(sports_root, "data/raw/nflverse", d)
        if not os.path.exists(dst):
            os.symlink(os.path.realpath(os.path.join(src, "data/raw/nflverse", d)), dst)
    xw = os.path.join(sports_root, "data/silver/player_crosswalk.parquet")
    if not os.path.exists(xw):
        os.symlink(os.path.realpath(os.path.join(src, "data/silver/player_crosswalk.parquet")), xw)


def compose(sports_root: str, market_lines: str, work: str) -> str:
    """A data root whose schedule = sports schedule + whatever market file was supplied."""
    root = os.path.join(work, "root")
    os.makedirs(os.path.join(root, "data/raw/nflverse/schedules"), exist_ok=True); os.makedirs(os.path.join(root, "data/silver"), exist_ok=True)
    for d in RAW:
        os.symlink(os.path.realpath(os.path.join(sports_root, "data/raw/nflverse", d)), os.path.join(root, "data/raw/nflverse", d))
    os.symlink(os.path.realpath(os.path.join(sports_root, "data/silver/player_crosswalk.parquet")), os.path.join(root, "data/silver/player_crosswalk.parquet"))
    g = pd.read_csv(os.path.join(sports_root, "data/raw/nflverse/schedules/games.csv"), low_memory=False)
    try:
        m = pd.read_csv(market_lines, low_memory=False)
        m = m[[c for c in m.columns if c == "game_id" or c in MU.MARKET_SCHEDULE_COLUMNS]]
        g = g.merge(m, on="game_id", how="left")
    except (OSError, ValueError, KeyError, pd.errors.ParserError):
        pass                                                # absent / unreadable market file: no market columns
    g.to_csv(os.path.join(root, "data/raw/nflverse/schedules/games.csv"), index=False)
    from nfl_edge.engines.player.pure_v1.data import TEAM_FIX
    g["home_team"] = g["home_team"].replace(TEAM_FIX); g["away_team"] = g["away_team"].replace(TEAM_FIX)
    g.to_parquet(os.path.join(root, "data/silver/games.parquet"), index=False)
    return root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sports-root", required=True)
    ap.add_argument("--market-lines", required=True)
    ap.add_argument("--season", type=int, default=2025)
    ap.add_argument("--out")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--split-from")
    a = ap.parse_args()
    if a.split_from:
        split(a.split_from, a.sports_root, a.market_lines)
        return 0
    os.makedirs(a.out, exist_ok=True)
    dest = os.path.join(a.out, "pure_forecasts.jsonl")
    with tempfile.TemporaryDirectory() as work:
        root = compose(a.sports_root, a.market_lines, work)
        if a.control:
            res = PM.v4_volume_control(root, a.season)
            if "refused" in res or any("refused" in v for v in res.values()):
                print(json.dumps(res), file=sys.stderr)
                return 3
            with open(dest, "w") as fh:
                fh.write(json.dumps(res, sort_keys=True) + "\n")
        else:
            PM.pure_run(root, a.season, dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
