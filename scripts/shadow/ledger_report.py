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
    # ---- how much of the apparent disagreement sits where the model is KNOWN to be miscalibrated?
    # research/tail_calibration measured the bias walk-forward on 1.4M rungs: about -0.010 where the model
    # prices below 0.20 and -0.005 between 0.20 and 0.35. Reporting the raw disagreement count without this
    # invites acting on a defect we have already measured.
    def tail_bias(p):
        return 0.010 if p < 0.20 else (0.005 if p < 0.35 else 0.0)

    props = [r for r in sup if r.get("family") == "PLAYER_STAT" and r.get("model_event_probability") is not None]
    if props:
        yes = [r for r in props if r["model_contract_value"] > r["yes_ask"] + taker_fee(r["yes_ask"])]
        no = [r for r in props if (1 - r["model_contract_value"]) > (1 - r["yes_bid"]) + taker_fee(1 - r["yes_bid"])]
        adj = 0
        for r in yes:
            p_ = r["model_event_probability"]
            scale = r["model_contract_value"] / max(p_, 1e-9)
            if r["model_contract_value"] - tail_bias(p_) * scale > r["yes_ask"] + taker_fee(r["yes_ask"]):
                adj += 1
        share = np.mean([r["model_event_probability"] < 0.20 for r in yes]) if yes else 0.0
        print(f"\nPLAYER_STAT disagreements that clear the far side after fees: "
              f"{len(yes)} YES-side, {len(no)} NO-side (of {len(props)})")
        print(f"  {share:.0%} of the YES-side sit below model p=0.20, where the model is measured to run "
              f"about 0.010 too high (research/tail_calibration)")
        print(f"  subtracting that measured bias: {len(yes)} -> {adj} YES-side disagreements")
        print("  This is a diagnostic, not a correction: the frozen model is unchanged (see H-20260904-015).")
        out["__player_stat_disagreement__"] = {"yes_side": len(yes), "no_side": len(no),
                                               "yes_side_after_measured_tail_bias": adj,
                                               "yes_side_share_below_0_20": float(share)}
    if a.json_out:
        json.dump(out, open(a.json_out, "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
