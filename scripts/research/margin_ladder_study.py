#!/usr/bin/env python3
"""Milestone G groundwork: pricing alternate-spread / alternate-total ladders from the closing line.

Kalshi spread rungs settle YES iff margin > k-0.5 (k integer); totals iff total >= k. Given a consensus
closing spread s and total t, how should P(margin > k-0.5) be modelled? Candidates, all walk-forward
(train seasons < S, test S in 2016..2025):
  N   normal(margin; s, sigma) with sigma fit on training seasons
  E   empirical distribution of (margin - s) pooled over training seasons (captures key numbers 3/7)
  E2  empirical conditional on spread bucket (|s|<3, 3-7, >7) -- does the residual shape depend on the favourite size?
Also for totals with (total - t).
Metrics: Brier and log loss over rungs k in -21..21 (spread) / 30..70 (totals); reliability by rung; key-number
mass P(|margin|=3), P(|margin|=7) predicted vs observed.
"""
import json, os, sys
import numpy as np, polars as pl
from scipy.stats import norm
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "research", "ladder_calibration"); os.makedirs(OUT, exist_ok=True)
g = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).filter((pl.col("game_type") == "REG") & pl.col("result").is_not_null() & pl.col("spread_line").is_not_null() & (pl.col("season") >= 2006)).to_pandas()
g["res"] = g["result"] - g["spread_line"]        # margin residual (home - away - spread)
g["tres"] = g["total"] - g["total_line"]
SP_RUNGS = np.arange(-21, 22)   # k: YES iff margin > k - 0.5  (home side)
TOT_RUNGS = np.arange(30, 71)   # YES iff total >= k
res = {"spread": {}, "total": {}}
rows = []
for S in range(2016, 2026):
    tr = g[(g.season < S) & (g.season >= S - 10)]; te = g[g.season == S]
    sig = tr["res"].std(); emp = tr["res"].to_numpy(); tsig = tr["tres"].std(); temp = tr["tres"].to_numpy()
    # bucketed empirical by |spread|
    def bucket(s): return np.where(np.abs(s) < 3, 0, np.where(np.abs(s) <= 7, 1, 2))
    tr_b = bucket(tr["spread_line"].to_numpy()); te_b = bucket(te["spread_line"].to_numpy())
    emp_b = {b: tr["res"].to_numpy()[tr_b == b] for b in (0, 1, 2)}
    y_m = te["result"].to_numpy(); s = te["spread_line"].to_numpy(); tot = te["total"].to_numpy(); tl = te["total_line"].to_numpy()
    for k in SP_RUNGS:
        thr = k - 0.5
        y = (y_m > thr).astype(float)                     # home wins by more than k-0.5
        pN = 1 - norm.cdf((thr - s) / sig)
        pE = np.array([np.mean(emp > (thr - si)) for si in s])
        pE2 = np.array([np.mean(emp_b[b] > (thr - si)) for si, b in zip(s, te_b)])
        for name, p in (("normal", pN), ("empirical", pE), ("empirical_bucket", pE2)):
            p = np.clip(p, 1e-4, 1 - 1e-4)
            rows.append({"market": "spread", "season": S, "k": int(k), "family": name, "n": len(y), "brier": float(np.mean((p - y) ** 2)),
                         "logloss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))), "mean_p": float(p.mean()), "obs": float(y.mean())})
    for k in TOT_RUNGS:
        thr = k - 0.5
        y = (tot > thr).astype(float)
        pN = 1 - norm.cdf((thr - tl) / tsig)
        pE = np.array([np.mean(temp > (thr - ti)) for ti in tl])
        for name, p in (("normal", pN), ("empirical", pE)):
            p = np.clip(p, 1e-4, 1 - 1e-4)
            rows.append({"market": "total", "season": S, "k": int(k), "family": name, "n": len(y), "brier": float(np.mean((p - y) ** 2)),
                         "logloss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))), "mean_p": float(p.mean()), "obs": float(y.mean())})
df = pl.DataFrame(rows)
df.write_parquet(os.path.join(OUT, "rung_metrics.parquet"))
summary = df.group_by(["market", "family"]).agg(pl.col("brier").mean(), pl.col("logloss").mean(), pl.len()).sort(["market", "family"])
print(summary)
# by rung distance from the line (|k - s| bucket) -- where does normal fail?
te_all = g[g.season >= 2016]
sig_all = g[g.season < 2016]["res"].std(); emp_all = g[g.season < 2016]["res"].to_numpy()
# reliability at key rungs relative to the spread: P(margin > s + d) for d in {-7.5..7.5}
rel = []
for d in [-10.5, -7.5, -6.5, -3.5, -2.5, -0.5, 0.5, 2.5, 3.5, 6.5, 7.5, 10.5]:
    y = (te_all["res"].to_numpy() > d).astype(float)
    pN = 1 - norm.cdf(d / sig_all); pE = np.mean(emp_all > d)
    rel.append({"d": d, "obs": float(y.mean()), "normal": float(pN), "empirical": float(pE), "n": int(len(y))})
key = {"P(|margin|==3)_obs": float(np.mean(np.abs(te_all["result"]) == 3)), "P(|margin|==7)_obs": float(np.mean(np.abs(te_all["result"]) == 7)),
       "P(margin==spread_exact_push)_obs": float(np.mean(te_all["res"] == 0)), "sigma_resid_train": float(sig_all), "sigma_resid_test": float(te_all["res"].std()),
       "sigma_total_resid": float(te_all["tres"].std()), "n_test": int(len(te_all))}
out = {"summary": summary.to_dicts(), "reliability_relative_to_spread": rel, "key_numbers": key}
json.dump(out, open(os.path.join(OUT, "results.json"), "w"), indent=1)
print(json.dumps(rel, indent=0)); print(key)
