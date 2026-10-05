#!/usr/bin/env python3
"""GAME SCRIPT V2 calibration backtest over the five-season walk-forward (preregistration section 3).

Reads the per-game script summaries the walk-forward wrote from the very rows it scored
(``scripts_<Y>.json`` under the baseline output directory) and writes ``script_calibration_5y.json``.

Usage: python scripts/sim/script_backtest.py [--seasons 2021,2022,2023,2024,2025] [--in-dir DIR] [--out PATH]
"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import five_year as FY, script_backtest as SB, script_v2 as V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seasons", default="2021,2022,2023,2024,2025")
    ap.add_argument("--in-dir", default=FY.DEFAULT_OUT)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "game_script_v2", "script_calibration_5y.json"))
    a = ap.parse_args()
    seasons = [int(s) for s in a.seasons.split(",")]
    games = {y: json.load(open(os.path.join(a.in_dir, f"scripts_{y}.json"))) for y in seasons}
    res = SB.run(games)
    res["meta"] = {"script_v2_version": V.SCRIPT_V2_VERSION, "seasons": seasons,
                   "evidence_class": {str(y): FY.EVIDENCE_CLASS.get(y) for y in seasons},
                   "bootstrap": {"resamples": SB.B, "seed": SB.SEED, "unit": "game"},
                   "spread_buckets": [x if x != float("inf") else None for x in SB.SPREAD_BUCKETS],
                   "provenance": V.PROVENANCE,
                   "note": "the nine-cell lattice is the market centre plus the incumbent's residual bank: a test of that bank, not of the volume or player models"}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1, default=float)
    print(json.dumps(res["verdict"], indent=1))


if __name__ == "__main__":
    main()
