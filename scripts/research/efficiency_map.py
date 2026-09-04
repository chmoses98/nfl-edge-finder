#!/usr/bin/env python3
"""2025 Kalshi NFL market-efficiency map: where was the market weak, by family x time-to-kickoff?

Input: the reconstructed executable quote at each horizon for every settled archived market
(data/kalshi/backfill/horizons/*.jsonl, built by scripts/kalshi/backfill_quotes.py).

Everything is measured on EXECUTABLE prices. `ask` is what a YES buyer actually pays; `bid` is what a YES
seller receives (equivalently 1-bid is the NO buyer's cost). The midpoint is reported separately and is only
ever used where the midpoint itself is the object of study -- it is not a tradable price.

Metrics per cell:
  n, n_traded, median quote width, median volume/open interest
  calibration of the MID as a probability: Brier, log loss, reliability slope
  favourite-longshot bias: realised settlement frequency by price bucket
  hypothetical execution: mean (y - ask) for YES and (1-y) - (1-bid) for NO, gross and after the Kalshi
  taker fee ceil(0.07*p*(1-p)*100)/100, which is what an actual taker would have paid
  price movement toward the outcome between horizons

Multiplicity: hundreds of cells are tested. Benjamini-Hochberg FDR at q=0.10 is applied to the per-cell
"is mean execution return != 0" tests, and nothing is called an edge -- these are hypothesis-generating.
"""
import glob, json, math, os, sys
from collections import defaultdict
import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "research", "efficiency_map"); os.makedirs(OUT, exist_ok=True)
MD = sys.argv[1] if len(sys.argv) > 1 else "/home/user/_md"
HORIZONS = ["T-168h", "T-72h", "T-48h", "T-24h", "T-12h", "T-6h", "T-3h", "T-90m", "T-30m", "T-0"]


def taker_fee(p, contracts=1.0):
    """Kalshi taker fee: ceil(0.07 * C * P * (1-P)) to the cent."""
    if p is None or not (0 < p < 1):
        return 0.0
    return math.ceil(0.07 * contracts * p * (1 - p) * 100) / 100.0


def load():
    rows = []
    for f in glob.glob(os.path.join(MD, "data/kalshi/backfill/horizons/*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if r.get("result") not in ("yes", "no"):
                continue
            y = 1.0 if r["result"] == "yes" else 0.0
            fam = r["family"]; stat = r.get("stat")
            cell_fam = f"{fam}:{stat}" if fam == "PLAYER_STAT" else (f"{fam}:{r.get('period')}" if r.get("period") else fam)
            for h, sn in (r.get("snaps") or {}).items():
                bid, ask = sn.get("bid"), sn.get("ask")
                if bid is None or ask is None:
                    continue
                if not (0.0 <= bid <= ask <= 1.0):
                    continue
                rows.append({"ticker": r["ticker"], "family": cell_fam, "base_family": fam, "stat": stat,
                             "horizon": h, "y": y, "bid": bid, "ask": ask, "mid": (bid + ask) / 2.0,
                             "width": ask - bid, "vol": sn.get("vol") or 0.0, "oi": sn.get("oi") or 0.0,
                             "age_min": sn.get("age_min"), "threshold": r.get("threshold"),
                             "anchor_kind": r["anchor_kind"], "season": r.get("season"),
                             "final_volume": r.get("final_volume") or 0.0})
    return pl.DataFrame(rows)


def cell_metrics(d: pl.DataFrame):
    y = d["y"].to_numpy(); mid = d["mid"].to_numpy(); ask = d["ask"].to_numpy(); bid = d["bid"].to_numpy()
    n = len(y)
    m = np.clip(mid, 1e-4, 1 - 1e-4)
    yes_ret = y - ask                                     # buy YES at the ask, hold to settlement
    no_ret = (1 - y) - (1 - bid)                          # buy NO (cost 1-bid)
    yes_fee = np.array([taker_fee(a) for a in ask]); no_fee = np.array([taker_fee(1 - b) for b in bid])
    out = {"n": int(n), "n_traded": int((d["vol"].to_numpy() > 0).sum()),
           "median_width": float(np.median(ask - bid)), "median_vol": float(np.median(d["vol"].to_numpy())),
           "median_oi": float(np.median(d["oi"].to_numpy())),
           "mean_mid": float(mid.mean()), "obs_yes": float(y.mean()),
           "brier_mid": float(np.mean((mid - y) ** 2)),
           "logloss_mid": float(-np.mean(y * np.log(m) + (1 - y) * np.log(1 - m))),
           "yes_ret_gross": float(yes_ret.mean()), "yes_ret_net": float((yes_ret - yes_fee).mean()),
           "no_ret_gross": float(no_ret.mean()), "no_ret_net": float((no_ret - no_fee).mean()),
           "yes_ret_se": float(yes_ret.std(ddof=1) / math.sqrt(n)) if n > 1 else None,
           "no_ret_se": float(no_ret.std(ddof=1) / math.sqrt(n)) if n > 1 else None}
    if n > 5 and mid.std() > 1e-6:
        b = np.polyfit(mid, y, 1)
        out["reliability_slope"] = float(b[0]); out["reliability_intercept"] = float(b[1])
    return out


def bh_fdr(pvals, q=0.10):
    p = np.asarray(pvals, float); order = np.argsort(p); m = len(p)
    thresh = q * (np.arange(1, m + 1)) / m
    passed = p[order] <= thresh
    k = np.max(np.where(passed)[0]) + 1 if passed.any() else 0
    cut = p[order][k - 1] if k else -1
    return p <= cut, cut


def main():
    D = load()
    print("horizon observations:", D.height, "| markets:", D["ticker"].n_unique(), flush=True)
    res = {"n_observations": D.height, "n_markets": int(D["ticker"].n_unique()), "cells": {}, "by_price_bucket": {},
           "movement": {}, "tails": {}}
    fams = [f for f, c in D.group_by("family").len().sort("len", descending=True).iter_rows() if c >= 400]
    tests = []
    for fam in fams:
        for h in HORIZONS:
            d = D.filter((pl.col("family") == fam) & (pl.col("horizon") == h))
            if d.height < 150:
                continue
            m = cell_metrics(d)
            res["cells"][f"{fam}|{h}"] = m
            if m.get("yes_ret_se"):
                tests.append((f"{fam}|{h}|YES", m["yes_ret_net"], m["yes_ret_se"], m["n"]))
                tests.append((f"{fam}|{h}|NO", m["no_ret_net"], m["no_ret_se"], m["n"]))
    # FDR over every cell-side test
    zs = [abs(t[1] / t[2]) if t[2] else 0.0 for t in tests]
    pv = [2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))) for z in zs]
    sig, cut = bh_fdr(pv, q=0.10)
    res["fdr"] = {"n_tests": len(tests), "q": 0.10, "p_cutoff": float(cut), "n_significant": int(sig.sum()),
                  "significant": [{"cell": tests[i][0], "net_return": tests[i][1], "se": tests[i][2], "n": tests[i][3],
                                   "p": pv[i]} for i in np.where(sig)[0]]}
    # favourite-longshot bias by price bucket, per base family, at the closing proxy
    edges = [0, .02, .05, .10, .20, .35, .50, .65, .80, .90, .95, .98, 1.0]
    for fam in sorted({f.split(":")[0] for f in fams}):
        d = D.filter((pl.col("base_family") == fam) & (pl.col("horizon") == "T-0"))
        if d.height < 300:
            continue
        mid = d["mid"].to_numpy(); y = d["y"].to_numpy(); ask = d["ask"].to_numpy()
        b = np.digitize(mid, edges) - 1
        rows = []
        for i in range(len(edges) - 1):
            msk = b == i
            if msk.sum() < 40:
                continue
            fee = np.array([taker_fee(a) for a in ask[msk]])
            rows.append({"lo": edges[i], "hi": edges[i + 1], "n": int(msk.sum()), "mean_mid": float(mid[msk].mean()),
                         "obs": float(y[msk].mean()), "yes_ret_net": float(((y[msk] - ask[msk]) - fee).mean())})
        res["by_price_bucket"][fam] = rows
    # movement toward the outcome between horizons (does the price improve as kickoff approaches?)
    piv = {}
    for r in D.iter_rows(named=True):
        piv.setdefault(r["ticker"], {})[r["horizon"]] = r
    for a, bh in (("T-72h", "T-0"), ("T-24h", "T-0"), ("T-6h", "T-0"), ("T-24h", "T-6h")):
        rows = [(v[a]["mid"], v[bh]["mid"], v[bh]["y"], v[a]["family"]) for v in piv.values() if a in v and bh in v]
        if len(rows) < 200:
            continue
        m0 = np.array([r[0] for r in rows]); m1 = np.array([r[1] for r in rows]); y = np.array([r[2] for r in rows])
        moved_right = np.mean(np.sign(m1 - m0) == np.sign(y - m0))
        res["movement"][f"{a}->{bh}"] = {"n": len(rows), "mean_abs_move": float(np.mean(np.abs(m1 - m0))),
                                         "share_moved_toward_outcome": float(moved_right),
                                         "brier_early": float(np.mean((m0 - y) ** 2)), "brier_late": float(np.mean((m1 - y) ** 2))}
    # tails: extreme rungs of player ladders at the close
    for stat in ("receiving_yards", "rushing_yards", "passing_yards", "receptions", "touchdowns"):
        d = D.filter((pl.col("stat") == stat) & (pl.col("horizon") == "T-0") & pl.col("threshold").is_not_null())
        if d.height < 300:
            continue
        th = d["threshold"].to_numpy(); mid = d["mid"].to_numpy(); y = d["y"].to_numpy(); ask = d["ask"].to_numpy()
        qs = np.quantile(th, [0.25, 0.5, 0.75])
        rows = []
        for lab, msk in (("low", th <= qs[0]), ("mid", (th > qs[0]) & (th <= qs[2])), ("tail", th > qs[2])):
            if msk.sum() < 50:
                continue
            fee = np.array([taker_fee(x) for x in ask[msk]])
            rows.append({"bucket": lab, "n": int(msk.sum()), "mean_mid": float(mid[msk].mean()), "obs": float(y[msk].mean()),
                         "brier": float(np.mean((mid[msk] - y[msk]) ** 2)),
                         "yes_ret_net": float(((y[msk] - ask[msk]) - fee).mean()),
                         "no_ret_net": float((((1 - y[msk]) - (1 - d["bid"].to_numpy()[msk])) - np.array([taker_fee(1 - bb) for bb in d["bid"].to_numpy()[msk]])).mean())})
        res["tails"][stat] = rows
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)
    # ---- print
    print("\nCALIBRATION AND EXECUTION BY FAMILY x HORIZON (net of the Kalshi taker fee)")
    print(f"{'cell':44s} {'n':>6s} {'width':>6s} {'mid':>6s} {'obs':>6s} {'brier':>7s} {'YESnet':>8s} {'NOnet':>8s}")
    for k, v in sorted(res["cells"].items()):
        print(f"{k:44s} {v['n']:6d} {v['median_width']:6.3f} {v['mean_mid']:6.3f} {v['obs_yes']:6.3f} "
              f"{v['brier_mid']:7.4f} {v['yes_ret_net']:+8.4f} {v['no_ret_net']:+8.4f}")
    print(f"\nFDR q=0.10 over {res['fdr']['n_tests']} cell-side tests: {res['fdr']['n_significant']} significant "
          f"(p cutoff {res['fdr']['p_cutoff']:.5f})")
    for s in res["fdr"]["significant"]:
        print(f"   {s['cell']:44s} net {s['net_return']:+.4f} +- {s['se']:.4f} (n={s['n']}, p={s['p']:.2e})")
    print("\nFAVOURITE-LONGSHOT BIAS AT THE CLOSE")
    for fam, rows in res["by_price_bucket"].items():
        print(f"  {fam}")
        for r in rows:
            print(f"    [{r['lo']:.2f},{r['hi']:.2f}) n={r['n']:6d} mid={r['mean_mid']:.3f} obs={r['obs']:.3f} YESnet={r['yes_ret_net']:+.4f}")
    print("\nPRICE MOVEMENT")
    for k, v in res["movement"].items():
        print(f"  {k:14s} n={v['n']:6d} |move|={v['mean_abs_move']:.4f} toward outcome={v['share_moved_toward_outcome']:.3f} "
              f"brier {v['brier_early']:.4f} -> {v['brier_late']:.4f}")
    print("\nPLAYER LADDER TAILS AT THE CLOSE")
    for stat, rows in res["tails"].items():
        for r in rows:
            print(f"  {stat:16s} {r['bucket']:5s} n={r['n']:5d} mid={r['mean_mid']:.3f} obs={r['obs']:.3f} "
                  f"brier={r['brier']:.4f} YESnet={r['yes_ret_net']:+.4f} NOnet={r['no_ret_net']:+.4f}")


if __name__ == "__main__":
    main()
