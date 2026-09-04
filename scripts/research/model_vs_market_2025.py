#!/usr/bin/env python3
"""Head-to-head: the model against the Kalshi closing price, on the same settled 2025 contracts.

Everything else in this repo compares the model to the market prospectively (no outcomes yet) or compares the
market to outcomes (no model). This joins the two: for every 2025 player-prop contract where a walk-forward
model probability and a reconstructed closing quote both exist, it scores both against what actually
happened, and then asks the only question that matters -- what would acting on the disagreement have paid.

The model probabilities come from research/kalshi_2025 (walk-forward, fitted on seasons before 2025). They
predate this session's role features, so this measures the model FAMILY, not shadow-0.3.0.

Calibration is restricted to books quoted within 10 cents; on wider books the midpoint records where a maker
parked an empty quote rather than a price (research/efficiency_map).
"""
import json, math, os, sys
from collections import defaultdict

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "research", "model_vs_market"); os.makedirs(OUT, exist_ok=True)
HORIZONS = sys.argv[1] if len(sys.argv) > 1 else "/home/user/_md/data/kalshi/backfill/horizons/*.jsonl"
MAX_WIDTH = 0.10


def fee(p):
    return math.ceil(0.07 * p * (1 - p) * 100) / 100.0 if 0 < p < 1 else 0.0


def cse(v, cl):
    v = np.asarray(v, float); n = len(v)
    if n < 2:
        return None
    by = defaultdict(float)
    for x, c in zip(v - v.mean(), cl):
        by[c] += x
    g = len(by)
    return float(np.sqrt(max(sum(t * t for t in by.values()) / (n * n) * (g / (g - 1.0)), 0.0))) if g > 1 else None


def main():
    import glob
    mp = pl.read_parquet(os.path.join(ROOT, "research/kalshi_2025/prop_model_probs_2025.parquet"))
    model = {r["ticker"]: (r["model_p"], r["y"], r["stat"]) for r in mp.iter_rows(named=True)}
    print(f"model probabilities available for {len(model)} contracts")

    rows = []
    for f in glob.glob(HORIZONS):
        for line in open(f):
            r = json.loads(line)
            if r.get("anchor_kind") != "kickoff" or r.get("result") not in ("yes", "no"):
                continue
            m = model.get(r["ticker"])
            if not m:
                continue
            s = (r.get("snaps") or {}).get("T-0")
            if not s or s.get("bid") is None or s.get("ask") is None:
                continue
            b, a = s["bid"], s["ask"]
            if not (0 <= b <= a <= 1) or (b <= 0 and a >= 1) or (a - b) > MAX_WIDTH:
                continue
            y = 1.0 if r["result"] == "yes" else 0.0
            rows.append({"cluster": r.get("game_id") or r["ticker"], "stat": m[2], "model_p": m[0], "y": y,
                         "bid": b, "ask": a, "mid": (b + a) / 2.0})
    print(f"matched contracts with a tradable closing book: {len(rows)}")
    if len(rows) < 200:
        print("not enough overlap yet"); return 0
    d = pl.DataFrame(rows)
    p = d["model_p"].to_numpy(); mid = d["mid"].to_numpy(); y = d["y"].to_numpy()
    bid = d["bid"].to_numpy(); ask = d["ask"].to_numpy(); cl = d["cluster"].to_list()

    def sc(q):
        q = np.clip(q, 1e-6, 1 - 1e-6)
        return float(np.mean((q - y) ** 2)), float(-np.mean(y * np.log(q) + (1 - y) * np.log(1 - q)))

    bm, lm = sc(p); bk, lk = sc(mid)
    print(f"\nWHO IS BETTER CALIBRATED ON THE SAME CONTRACTS  (n={len(y)}, games={len(set(cl))})")
    print(f"  model   Brier {bm:.5f}   logloss {lm:.5f}   mean p {p.mean():.4f}")
    print(f"  market  Brier {bk:.5f}   logloss {lk:.5f}   mean mid {mid.mean():.4f}   realised {y.mean():.4f}")
    diff = (p - y) ** 2 - (mid - y) ** 2
    se = cse(diff, cl)
    print(f"  Brier difference (model - market) {diff.mean():+.5f} +- {se:.5f}  "
          f"({'model better' if diff.mean() < 0 else 'market better'})")

    print("\nWHAT ACTING ON THE DISAGREEMENT WOULD HAVE PAID (net of the Kalshi taker fee)")
    print(f"  {'edge threshold':16s} {'trades':>7s} {'games':>6s} {'net/contract':>13s} {'se':>8s} {'z':>6s}")
    res = {"n": len(y), "games": len(set(cl)), "brier_model": bm, "brier_market": bk,
           "brier_diff": float(diff.mean()), "brier_diff_se": se, "thresholds": []}
    for thr in (0.0, 0.02, 0.05, 0.10, 0.15):
        rets, cls = [], []
        for i in range(len(y)):
            if p[i] > ask[i] + fee(ask[i]) + thr:
                rets.append((y[i] - ask[i]) - fee(ask[i])); cls.append(cl[i])
            elif (1 - p[i]) > (1 - bid[i]) + fee(1 - bid[i]) + thr:
                rets.append(((1 - y[i]) - (1 - bid[i])) - fee(1 - bid[i])); cls.append(cl[i])
        if len(rets) < 30:
            continue
        arr = np.array(rets); s2 = cse(arr, cls); z = arr.mean() / s2 if s2 else float("nan")
        mark = "  <-- POSITIVE" if z > 2 else ""
        print(f"  edge > {thr:.2f}       {len(arr):7d} {len(set(cls)):6d} {arr.mean():+13.4f} {s2:8.4f} {z:6.2f}{mark}")
        res["thresholds"].append({"threshold": thr, "trades": len(arr), "games": len(set(cls)),
                                  "net": float(arr.mean()), "se": s2, "z": float(z)})
    print("\nBY STATISTIC -- is there anywhere the model beats the closing price?")
    print(f"  {'stat':18s} {'n':>6s} {'g':>5s} {'model':>8s} {'market':>8s} {'diff':>9s} {'se':>8s} {'z':>6s}")
    bystat = {}
    stats = d["stat"].to_numpy()
    for st in sorted(set(stats)):
        m = stats == st
        if m.sum() < 200:
            continue
        dd = (p[m] - y[m]) ** 2 - (mid[m] - y[m]) ** 2
        cl2 = list(np.array(cl)[m])
        s3 = cse(dd, cl2); z = dd.mean() / s3 if s3 else float("nan")
        mark = "  <-- model better" if z < -2 else ""
        print(f"  {st:18s} {int(m.sum()):6d} {len(set(cl2)):5d} "
              f"{float(np.mean((p[m]-y[m])**2)):8.5f} {float(np.mean((mid[m]-y[m])**2)):8.5f} "
              f"{dd.mean():+9.5f} {s3:8.5f} {z:6.2f}{mark}")
        bystat[st] = {"n": int(m.sum()), "games": len(set(cl2)), "brier_model": float(np.mean((p[m]-y[m])**2)),
                      "brier_market": float(np.mean((mid[m]-y[m])**2)), "diff": float(dd.mean()), "se": s3}
    res["by_stat"] = bystat
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
