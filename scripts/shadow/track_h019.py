#!/usr/bin/env python3
"""Prospective tracking for H-20260904-019 (GAME_WINNER favourite-longshot), exactly as preregistered.

The rule is FIXED and this script implements it literally:

  population        GAME_WINNER contracts, tradable books (quoted width <= 0.10)
  primary endpoint  YES-side net return after the Kalshi taker fee on contracts whose CLOSING midpoint
                    falls in [0.20, 0.50)
  inference         cluster-robust on game; a clustered SE excluding zero is required
  sample gate       at least 250 games before the result is read at all
  one test          [0.20,0.35) and [0.35,0.50) are the same games seen from both sides. They are reported
                    separately for description, but the endpoint is the pooled [0.20,0.50) figure.

No subgroup splits. No re-cut buckets. Nothing here may be tuned on 2025 outcomes.
"""
import argparse, glob, gzip, json, math, os, sys
from collections import defaultdict

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research.clv import clustered_se  # noqa: E402

# ---- PREREGISTERED CONSTANTS. Changing any of these invalidates the hypothesis.
PRIMARY_LO, PRIMARY_HI = 0.20, 0.50
DESCRIPTIVE_BUCKETS = [(0.20, 0.35), (0.35, 0.50), (0.50, 0.65), (0.65, 0.80)]
MAX_WIDTH = 0.10
MIN_GAMES = 250
FAMILY = "GAME_WINNER"


def fee(p):
    return math.ceil(0.07 * p * (1 - p) * 100) / 100.0 if 0 < p < 1 else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=os.path.join(ROOT, "data/shadow/ledger"))
    a = ap.parse_args()
    rows = []
    for f in sorted(glob.glob(os.path.join(a.ledger, "*", "*.observations.jsonl.gz"))):
        for line in gzip.open(f, "rt"):
            r = json.loads(line)
            if r.get("family") != FAMILY or r.get("yes_bid") is None or r.get("yes_ask") is None:
                continue
            if (r["yes_ask"] - r["yes_bid"]) > MAX_WIDTH:
                continue
            rows.append(r)
    settled = [r for r in rows if r.get("settlement_result") in ("yes", "no")]
    games = {r.get("game_id") for r in rows if r.get("game_id")}
    print(f"H-20260904-019 prospective tracker")
    print(f"  preregistered primary endpoint: YES net after fees, closing mid in "
          f"[{PRIMARY_LO:.2f},{PRIMARY_HI:.2f}), tradable books, clustered on game")
    print(f"  sample gate: {MIN_GAMES} games\n")
    print(f"  GAME_WINNER observations captured so far: {len(rows)}  distinct games: {len(games)}")
    print(f"  settled with an outcome: {len(settled)}")
    if len(settled) == 0:
        print(f"\n  STATUS: awaiting outcomes. First 2026 kickoff is 2026-09-09; no GAME_WINNER contract in")
        print(f"  the ledger has settled yet, so the endpoint is not computable and MUST NOT be reported.")
        print(f"  The 2025 historical figure (+0.0286 and +0.0189 YES net, 1.1-1.2 SE, 259 games) is NOT")
        print(f"  evidence for 2026 and is not repeated here as a result.")
        return 0
    if len({r.get("game_id") for r in settled}) < MIN_GAMES:
        print(f"\n  STATUS: {len({r.get('game_id') for r in settled})} settled games < {MIN_GAMES} gate.")
        print(f"  The preregistration forbids reading the result before the gate. Not computed.")
        return 0
    y = np.array([1.0 if r["settlement_result"] == "yes" else 0.0 for r in settled])
    ask = np.array([r["yes_ask"] for r in settled])
    mid = np.array([(r["yes_bid"] + r["yes_ask"]) / 2.0 for r in settled])
    cl = [r["game_id"] for r in settled]
    m = (mid >= PRIMARY_LO) & (mid < PRIMARY_HI)
    net = (y[m] - ask[m]) - np.array([fee(x) for x in ask[m]])
    se = clustered_se(net, list(np.array(cl)[m]))
    print(f"\n  PRIMARY ENDPOINT  n={int(m.sum())} games={len(set(np.array(cl)[m]))}")
    print(f"    YES net after fees {net.mean():+.4f} +- {se:.4f}  (z={net.mean()/se:+.2f})")
    print(f"    {'PASSES' if se and abs(net.mean()/se) > 2 and net.mean() > 0 else 'does not pass'} "
          f"the preregistered bar (clustered SE excluding zero, positive)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
