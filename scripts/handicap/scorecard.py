#!/usr/bin/env python3
"""The long-term handicapper scorecard.

    python3 scripts/handicap/scorecard.py --handicap-root /path/to/handicap-wt [--json]

Compares MODEL, MARKET and CHATGPT HANDICAP on the same resolved recommendations, and RECOMMENDED against
PASS. TEST_ONLY records are excluded. With no resolved sample it says so instead of printing zeros.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import store                      # noqa: E402
from nfl_edge.handicap.scorecard import build_scorecard   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handicap-root", required=True)
    ap.add_argument("--season", type=int, default=None)
    ap.add_argument("--week", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    recs = store.latest_amendment_chain(store.read_kind(a.handicap_root, "recommendations", a.season, a.week))
    evs = store.read_kind(a.handicap_root, "evaluations", a.season, a.week)
    exs = store.read_kind(a.handicap_root, "executions", a.season, a.week)
    sc = build_scorecard(recs, evs, exs)

    if a.json:
        print(json.dumps(sc, indent=1))
        return 0

    print("=" * 74)
    print("NFL HANDICAPPER SCORECARD")
    print("=" * 74)
    print(f"recommendations {sc['n_recommendations']}  evaluated {sc['n_evaluated']}  "
          f"resolved {sc['n_resolved']}  executions {sc['n_executions']}")
    print(f"by decision: {sc['by_decision']}")
    print()
    if sc["status"] != "RESOLVED SAMPLE PRESENT":
        print(sc["status"])
        print(sc["note"])
        print("=" * 74)
        return 0

    h = sc["headline"]
    print(f"HEADLINE  {h['recommendations_resolved']} resolved  {h['wins']}W-{h['losses']}L  "
          f"win rate {h['win_rate']}")
    print(f"          mean CLV {h['mean_clv']}  executable {h['mean_clv_executable']}  "
          f"positive-CLV rate {h['positive_clv_rate']}")
    print(f"          staked ${h['dollars_staked']}  P/L ${h['pnl']}  ROI {h['roi']}")
    print(f"          {h['note']}")
    print()
    print("FORECASTER COMPARISON (same contracts, lower is better)")
    for who in ("model", "market", "chatgpt_handicap"):
        m = sc["forecaster_comparison"][who]
        if m.get("n"):
            print(f"  {who:18s} n={m['n']:4d}  brier {m['brier']:.5f}  logloss {m['log_loss']:.5f}  "
                  f"mean err {m['mean_signed_error']:+.5f}")
        else:
            print(f"  {who:18s} no probabilities recorded")
    print(f"  -> {sc['forecaster_comparison']['interpretation']}")
    print()
    print("RECOMMENDED vs PASS")
    for k in ("RECOMMENDED", "PASS", "WATCHLIST"):
        v = sc["recommended_vs_pass"][k]
        print(f"  {k:12s} n={v['n']:4d}" + ("" if not v["n"] else
              f"  win rate {v['win_rate']}  mean CLV {v['mean_clv']}"))
    print(f"  -> {sc['recommended_vs_pass']['interpretation']}")
    print()
    for name, table in sc["breakdowns"].items():
        rows = {k: v for k, v in table.items() if v.get("recommendations_resolved")}
        if not rows:
            continue
        print(f"{name.upper()}")
        for k, v in rows.items():
            print(f"  {k:24s} n={v['recommendations_resolved']:3d}  win {v['win_rate']}  "
                  f"CLV {v['mean_clv']}  ROI {v['roi']}")
        print()
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
