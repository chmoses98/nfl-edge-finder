#!/usr/bin/env python3
"""Walk-forward backtest of the simulation layer: fit on seasons < Y, simulate every game of Y.

Usage: python scripts/sim/walkforward.py --seasons 2023,2024,2025 [--n-sims 10000] [--limit N]
Writes research/simulation_engine/{player,team}_dists_<Y>.parquet, bundle_<Y>.json and walkforward.json.
"""
from __future__ import annotations
import argparse, json, os, pickle, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import backtest as B, training as T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seasons", default="2023,2024,2025")
    ap.add_argument("--n-sims", type=int, default=10000)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--history-start", type=int, default=2016)
    ap.add_argument("--frames-cache", default=os.path.join(ROOT, "data", "cache", "sim", "frames.pkl"))
    a = ap.parse_args()
    seasons = [int(s) for s in a.seasons.split(",")]
    if os.path.exists(a.frames_cache):
        frames = pickle.load(open(a.frames_cache, "rb"))
    else:
        frames = T.assemble(range(a.history_start, max(seasons) + 1))
        os.makedirs(os.path.dirname(a.frames_cache), exist_ok=True)
        pickle.dump(frames, open(a.frames_cache, "wb"))
    out_path = os.path.join(B.OUT, "walkforward.json")
    results = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for y in seasons:
        info = B.run_season(y, frames, n_sims=a.n_sims, limit=a.limit or None, verbose=print)
        ev = B.evaluate(y, frames)
        results[str(y)] = {"run": info, "evaluation": ev}
        json.dump(results, open(out_path, "w"), indent=1)
        print(json.dumps({k: {kk: round(vv, 3) for kk, vv in v.items() if isinstance(vv, float)} for k, v in ev["player"].items()}, indent=0))


if __name__ == "__main__":
    main()
