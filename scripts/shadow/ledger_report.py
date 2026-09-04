#!/usr/bin/env python3
"""Summarise a shadow-ledger snapshot against EXECUTABLE prices, not the midpoint.

The midpoint is not a price. On a book quoted 20 bid / 71 ask the midpoint is 45.5, and a model saying 38 is
not 7.5 points of edge -- it is a number sitting comfortably inside a 51-cent spread that nobody will trade
against. Ranking by distance from the midpoint therefore ranks by *illiquidity*, and the widest, thinnest,
least-traded markets come out on top every time.

This report always shows, per family: the median quoted width, how often the model's price falls INSIDE the
spread (i.e. there is no disagreement a trader could act on at all), how often it clears the far side, and
how often it still clears after the Kalshi taker fee. Nothing here is an edge -- these are prospective
disagreements recorded before kickoff, with no settled outcomes attached yet.
"""
import argparse, glob, gzip, json, math, os, sys
from collections import defaultdict

import numpy as np


def taker_fee(p):
    return math.ceil(0.07 * p * (1 - p) * 100) / 100.0 if 0 < p < 1 else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="data/shadow/ledger")
    ap.add_argument("--json-out", default="")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.ledger, "*", "*.observations.jsonl.gz")))
    if not files:
        print("no ledger files"); return 1
    f = files[-1]
    rows = [json.loads(l) for l in gzip.open(f, "rt")]
    sup = [r for r in rows if r.get("support_state") == "SUPPORTED"
           and r.get("model_contract_value") is not None
           and r.get("yes_bid") is not None and r.get("yes_ask") is not None]
    print(f"snapshot {os.path.basename(f)}")
    print(f"observations {len(rows)}, supported and quoted {len(sup)}\n")

    states = defaultdict(int)
    for r in rows:
        states[r.get("support_state")] += 1
    print("support states: " + ", ".join(f"{k} {v}" for k, v in sorted(states.items(), key=lambda x: -x[1])))

    out = {}
    print(f"\n{'family':22s} {'n':>5s} {'med width':>10s} {'inside spread':>14s} {'clears ask':>11s} "
          f"{'clears bid':>11s} {'after fee':>10s} {'|vs mid|':>9s}")
    agg = defaultdict(lambda: {"n": 0, "inside": 0, "yes": 0, "no": 0, "fee": 0, "w": [], "d": []})
    for r in sup:
        v = r["model_contract_value"]; b = r["yes_bid"]; ask = r["yes_ask"]
        for key in (r["family"], "__ALL__"):
            t = agg[key]
            t["n"] += 1; t["w"].append(ask - b)
            if r.get("model_market_disagreement") is not None:
                t["d"].append(abs(r["model_market_disagreement"]))
            if b <= v <= ask:
                t["inside"] += 1
            if v > ask:
                t["yes"] += 1
            if v < b:
                t["no"] += 1
            if v > ask + taker_fee(ask) or (1 - v) > (1 - b) + taker_fee(1 - b):
                t["fee"] += 1
    for key in sorted(agg, key=lambda k: (k == "__ALL__", -agg[k]["n"])):
        t = agg[key]; n = t["n"]
        row = {"n": n, "median_width": float(np.median(t["w"])), "inside_spread": t["inside"] / n,
               "clears_ask": t["yes"] / n, "clears_bid": t["no"] / n, "clears_after_fee": t["fee"] / n,
               "mean_abs_vs_mid": float(np.mean(t["d"])) if t["d"] else None}
        out[key] = row
        print(f"{key:22s} {n:5d} {row['median_width']:10.3f} {row['inside_spread']:13.1%} "
              f"{row['clears_ask']:10.1%} {row['clears_bid']:10.1%} {row['clears_after_fee']:9.1%} "
              f"{(row['mean_abs_vs_mid'] or float('nan')):9.4f}")

    # the trap, stated numerically: rank by distance from the midpoint and see what you actually get
    d = sorted((r for r in sup if r.get("model_market_disagreement") is not None),
               key=lambda r: -abs(r["model_market_disagreement"]))
    top = d[:50]
    ins = sum(1 for r in top if r["yes_bid"] <= r["model_contract_value"] <= r["yes_ask"])
    print(f"\nTop 50 contracts by |disagreement vs midpoint|:")
    print(f"  median quoted width {np.median([r['yes_ask'] - r['yes_bid'] for r in top]):.3f} "
          f"(all supported: {np.median([r['yes_ask'] - r['yes_bid'] for r in sup]):.3f})")
    print(f"  {ins}/{len(top)} have the model price INSIDE the spread -- no executable disagreement at all")
    fams = defaultdict(int)
    for r in top:
        fams[r["family"]] += 1
    print(f"  families: {dict(sorted(fams.items(), key=lambda x: -x[1]))}")
    out["__top50_by_mid_distance__"] = {"median_width": float(np.median([r["yes_ask"] - r["yes_bid"] for r in top])),
                                        "inside_spread": ins / max(len(top), 1), "families": dict(fams)}
    if a.json_out:
        json.dump(out, open(a.json_out, "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
