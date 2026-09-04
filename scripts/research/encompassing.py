#!/usr/bin/env python3
"""Does the model contain information the market price does not?

The market beats the model outright (research/model_vs_market). That leaves the question that decides what to
do about it: is the model *redundant*, or does it carry orthogonal information that a market-anchored
combination could use?

The standard test is forecast encompassing. Regress the settled outcome on both forecasts in logit space:

    logit P(y=1) = a + b1 * logit(model_p) + b2 * logit(market_mid)

  * b1 ~ 0 with b2 > 0  -> the market encompasses the model; the model adds nothing.
  * b1 > 0              -> the model carries information the price does not, and a blend should beat both.

Fitted by IRLS. Standard errors are clustered on game, because a player's whole ladder settles on one
performance. Evaluation of any blend is walk-forward by week so the blend weights never see the contracts
they are scored on.
"""
import json, math, os, sys
from collections import defaultdict

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "research", "model_vs_market")
HORIZONS = sys.argv[1] if len(sys.argv) > 1 else "/home/user/_md/data/kalshi/backfill/horizons/*.jsonl"
EPS = 1e-4


def logit(p):
    p = np.clip(np.asarray(p, float), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def irls(X, y, ridge=1e-6, iters=50):
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = sigmoid(X @ b)
        w = np.clip(p * (1 - p), 1e-9, None)
        z = X @ b + (y - p) / w
        XtW = X.T * w
        nb = np.linalg.solve(XtW @ X + ridge * np.eye(X.shape[1]), XtW @ z)
        if np.max(np.abs(nb - b)) < 1e-9:
            b = nb
            break
        b = nb
    return b


def cluster_se(X, y, b, clusters):
    """Cluster-robust (sandwich) SEs for a logistic fit."""
    p = sigmoid(X @ b)
    w = np.clip(p * (1 - p), 1e-9, None)
    bread = np.linalg.inv((X.T * w) @ X + 1e-9 * np.eye(X.shape[1]))
    u = X * (y - p)[:, None]
    agg = defaultdict(lambda: np.zeros(X.shape[1]))
    for i, c in enumerate(clusters):
        agg[c] += u[i]
    meat = np.zeros((X.shape[1], X.shape[1]))
    for v in agg.values():
        meat += np.outer(v, v)
    g = len(agg)
    V = bread @ meat @ bread * (g / max(g - 1, 1))
    return np.sqrt(np.clip(np.diag(V), 0, None))


def main():
    import glob
    P = pl.read_parquet(os.path.join(OUT, "prop_probs_2025_both_arms.parquet"))
    probs = {r["ticker"]: r for r in P.iter_rows(named=True)}
    rows = []
    for f in glob.glob(HORIZONS):
        for line in open(f):
            r = json.loads(line)
            if r.get("anchor_kind") != "kickoff" or r.get("result") not in ("yes", "no"):
                continue
            m = probs.get(r["ticker"])
            if not m:
                continue
            s = (r.get("snaps") or {}).get("T-0")
            if not s or s.get("bid") is None or s.get("ask") is None:
                continue
            b, a = s["bid"], s["ask"]
            if not (0 <= b <= a <= 1) or (b <= 0 and a >= 1) or (a - b) > 0.10:
                continue
            rows.append({"cluster": r.get("game_id") or r["ticker"], "week": int(r.get("week") or 0),
                         "stat": m["stat"], "p_base": m["p_base"], "p_role": m["p_role"],
                         "y": m["y"], "mid": (a + b) / 2.0})
    d = pl.DataFrame(rows)
    print(f"contracts: {d.height}, games: {d['cluster'].n_unique()}")
    y = d["y"].to_numpy(); mid = d["mid"].to_numpy(); cl = d["cluster"].to_list()

    for arm in ("p_base", "p_role"):
        p = d[arm].to_numpy()
        X = np.column_stack([np.ones(len(y)), logit(p), logit(mid)])
        b = irls(X, y)
        se = cluster_se(X, y, b, cl)
        print(f"\nENCOMPASSING TEST, model arm = {arm}   (logit outcome ~ 1 + logit model + logit market)")
        for name, coef, s in zip(("intercept", "model", "market"), b, se):
            z = coef / s if s else float("nan")
            print(f"  {name:10s} {coef:+8.4f} +- {s:.4f}   (z = {z:+6.2f})")
        print(f"  interpretation: market coefficient {b[2]:+.3f}, model coefficient {b[1]:+.3f} "
              f"({'model adds information' if abs(b[1] / se[1]) > 2 else 'model is encompassed by the price'})")

    # walk-forward blend by week: weights fitted on earlier weeks only
    print("\nWALK-FORWARD BLEND (weights fitted on strictly earlier weeks)")
    wk = d["week"].to_numpy()
    for arm in ("p_base", "p_role"):
        p = d[arm].to_numpy()
        X = np.column_stack([np.ones(len(y)), logit(p), logit(mid)])
        pred = np.full(len(y), np.nan)
        for w in sorted(set(wk)):
            tr = wk < w; te = wk == w
            if tr.sum() < 800 or te.sum() == 0:
                continue
            pred[te] = sigmoid(X[te] @ irls(X[tr], y[tr]))
        ok = np.isfinite(pred)
        if ok.sum() < 500:
            print(f"  {arm}: too few weeks with enough history"); continue
        def sc(q, m):
            q = np.clip(q, 1e-6, 1 - 1e-6)
            return float(np.mean((q - y[m]) ** 2))
        bb = sc(p[ok], ok); bm = sc(mid[ok], ok); bl = sc(pred[ok], ok)
        dd = (pred[ok] - y[ok]) ** 2 - (mid[ok] - y[ok]) ** 2
        agg = defaultdict(float)
        cls = list(np.array(cl)[ok])
        for x, c in zip(dd - dd.mean(), cls):
            agg[c] += x
        g = len(agg)
        se = math.sqrt(max(sum(t * t for t in agg.values()) / (len(dd) ** 2) * (g / (g - 1)), 0.0))
        print(f"  {arm}: n={int(ok.sum())} model {bb:.5f}  market {bm:.5f}  blend {bl:.5f}   "
              f"blend-market {dd.mean():+.5f} +- {se:.5f} (z={dd.mean()/se:+.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
