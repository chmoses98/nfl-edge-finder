#!/usr/bin/env python3
"""What shape is the market quoting, and where exactly do we disagree with it?

Fits the market-implied distribution for every 2025 player ladder at a chosen horizon, then decomposes our
model's disagreement into location, tail shape and residual. The point is to replace "model 47%, market 40%"
with a statement about WHICH property of the distribution we are disputing -- because those have different
prospects. Disputing the market's location is disputing the thing it is demonstrably better at
(research/model_vs_market). Disputing its tail shape or leaving a large unexplained residual is a different
claim, and one that a role shock could plausibly justify.
"""
import argparse, glob, json, os, sys
from collections import defaultdict

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.pricing.market_prior import decompose_disagreement, fit_market_shape  # noqa: E402

OUT = os.path.join(ROOT, "research", "market_prior"); os.makedirs(OUT, exist_ok=True)
MAX_WIDTH = 0.10


def load_ladders(path, horizon):
    """Group 2025 rungs into ladders keyed by (game, player, stat) at one horizon."""
    lad = defaultdict(list)
    for f in glob.glob(path):
        for line in open(f):
            r = json.loads(line)
            if r.get("anchor_kind") != "kickoff" or r.get("family") != "PLAYER_STAT":
                continue
            if r.get("threshold") is None or not r.get("player_kalshi_id") or not r.get("game_id"):
                continue
            s = (r.get("snaps") or {}).get(horizon)
            if not s or s.get("bid") is None or s.get("ask") is None:
                continue
            lad[(r["game_id"], r["player_kalshi_id"], r["stat"])].append(
                {"ticker": r["ticker"], "threshold": float(r["threshold"]),
                 "yes_bid": s["bid"], "yes_ask": s["ask"],
                 "y": 1.0 if r.get("result") == "yes" else (0.0 if r.get("result") == "no" else None)})
    return lad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizons", default="/home/user/_md/data/kalshi/backfill/horizons/*.jsonl")
    ap.add_argument("--horizon", default="T-0")
    a = ap.parse_args()

    lad = load_ladders(a.horizons, a.horizon)
    print(f"ladders at {a.horizon}: {len(lad)}")
    probs = {}
    pp = os.path.join(ROOT, "research/model_vs_market/prop_probs_2025_both_arms.parquet")
    if os.path.exists(pp):
        probs = {r["ticker"]: r for r in pl.read_parquet(pp).iter_rows(named=True)}
    print(f"model probabilities available for {len(probs)} rungs")

    shapes, decomps = [], []
    by_stat = defaultdict(list)
    for (gid, pid, stat), rows in lad.items():
        rows = [r for r in rows if (r["yes_ask"] - r["yes_bid"]) <= MAX_WIDTH]
        if len(rows) < 4:
            continue
        sh = fit_market_shape(rows, side="mid")
        if not sh.ok:
            continue
        shapes.append({"game_id": gid, "stat": stat, "n": sh.n_points, "lam": sh.lam, "gam": sh.gam,
                       "curvature": sh.curvature, "rmse": sh.fit_rmse, "mean": sh.implied_mean,
                       "sd": sh.implied_sd, "width": sh.median_width})
        by_stat[stat].append(sh)
        if probs:
            ks = np.array([r["threshold"] for r in sorted(rows, key=lambda x: x["threshold"])])
            mS, ok = [], True
            for r in sorted(rows, key=lambda x: x["threshold"]):
                m = probs.get(r["ticker"])
                if not m:
                    ok = False; break
                mS.append(m["p_base"])
            if ok and len(mS) >= 4:
                d = decompose_disagreement(ks, np.array(mS), sh)
                if d and d.total > 0:
                    decomps.append({"game_id": gid, "stat": stat, **{k: v for k, v in d.to_dict().items()
                                                                     if k != "parts"}})
    print(f"\nMARKET-IMPLIED SHAPE BY STATISTIC (Weibull fit to the quoted ladder, midpoint surface)")
    print(f"  {'stat':18s} {'ladders':>8s} {'lam':>8s} {'gam':>7s} {'mean':>8s} {'sd':>7s} {'rmse':>7s} {'curv':>8s}")
    shape_rows = {}
    for stat, ss in sorted(by_stat.items(), key=lambda x: -len(x[1])):
        if len(ss) < 30:
            continue
        g = np.array([s.gam for s in ss]); l = np.array([s.lam for s in ss])
        m = np.array([s.implied_mean for s in ss if s.implied_mean is not None])
        sd = np.array([s.implied_sd for s in ss if s.implied_sd is not None])
        rm = np.array([s.fit_rmse for s in ss]); cv = np.array([s.curvature for s in ss if s.curvature is not None])
        shape_rows[stat] = {"n": len(ss), "gam_median": float(np.median(g)), "lam_median": float(np.median(l)),
                            "mean_median": float(np.median(m)) if len(m) else None,
                            "sd_median": float(np.median(sd)) if len(sd) else None,
                            "rmse_median": float(np.median(rm)),
                            "curvature_median": float(np.median(cv)) if len(cv) else None}
        r = shape_rows[stat]
        print(f"  {stat:18s} {len(ss):8d} {r['lam_median']:8.2f} {r['gam_median']:7.3f} "
              f"{(r['mean_median'] or float('nan')):8.2f} {(r['sd_median'] or float('nan')):7.2f} "
              f"{r['rmse_median']:7.4f} {(r['curvature_median'] or float('nan')):+8.4f}")

    res = {"horizon": a.horizon, "n_ladders": len(shapes), "shape_by_stat": shape_rows}
    if decomps:
        D = pl.DataFrame(decomps)
        print(f"\nWHY WE DISAGREE  (n={D.height} ladders with a model curve on the same rungs)")
        tot = D["total"].sum()
        for part in ("location", "shape", "residual"):
            v = D[part].to_numpy()
            print(f"  {part:10s} {v.sum()/tot:6.1%} of total disagreement   mean per ladder {v.mean():+.4f}")
        print(f"\n  by statistic (share of that statistic's total disagreement)")
        print(f"  {'stat':18s} {'ladders':>8s} {'location':>9s} {'shape':>8s} {'residual':>9s} "
              f"{'model mean':>11s} {'mkt mean':>9s}")
        dec_rows = {}
        for stat in sorted(set(D["stat"].to_list())):
            s = D.filter(pl.col("stat") == stat)
            if s.height < 20:
                continue
            t = s["total"].sum()
            dec_rows[stat] = {"n": s.height, "location": float(s["location"].sum() / t),
                              "shape": float(s["shape"].sum() / t), "residual": float(s["residual"].sum() / t),
                              "model_mean": float(np.nanmean(s["model_mean"].to_numpy().astype(float))),
                              "market_mean": float(np.nanmean(s["market_mean"].to_numpy().astype(float)))}
            r = dec_rows[stat]
            print(f"  {stat:18s} {s.height:8d} {r['location']:9.1%} {r['shape']:8.1%} {r['residual']:9.1%} "
                  f"{r['model_mean']:11.2f} {r['market_mean']:9.2f}")
        res["disagreement"] = {"n": D.height, "overall": {p: float(D[p].sum() / tot)
                                                          for p in ("location", "shape", "residual")},
                               "by_stat": dec_rows}
        D.write_parquet(os.path.join(OUT, f"disagreement_{a.horizon}.parquet"))
    json.dump(res, open(os.path.join(OUT, f"results_{a.horizon}.json"), "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
