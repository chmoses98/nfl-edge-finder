#!/usr/bin/env python3
"""Five-season walk-forward of the FROZEN incumbent simulation with GAME SCRIPT V2 collected from the same rows.

Equivalent to `python scripts/sim/walkforward.py --seasons 2021,2022,2023,2024,2025 --n-sims 10000 --out-dir DIR`
(the same fit_priors_for -> assemble -> run_season -> evaluate calls per season) plus the read-only script hook and
the eligibility / QB-identification audits. One process per season is safe: every season writes its own files.

Usage: python scripts/sim/baseline_5y.py --seasons 2021,2022,2023,2024,2025 [--n-sims 10000] [--out-dir DIR]
"""
from __future__ import annotations
import argparse, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import five_year as FY


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seasons", default="2021,2022,2023,2024,2025")
    ap.add_argument("--n-sims", type=int, default=10000)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out-dir", default=FY.DEFAULT_OUT)
    a = ap.parse_args()
    for y in [int(s) for s in a.seasons.split(",")]:
        rec = FY.run_season(y, n_sims=a.n_sims, out_dir=a.out_dir, limit=a.limit or None)
        print(y, rec["run"]["games_simulated"], "games;", len(rec["run"]["skipped"]), "skipped", flush=True)


if __name__ == "__main__":
    main()
