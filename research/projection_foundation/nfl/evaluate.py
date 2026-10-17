"""Distributions and scoring for the NFL ladder.

Distribution families are fitted on DEVELOPMENT residuals of each mean model and frozen; validation selects the
family; holdout is scored once. All CIs are game-clustered bootstraps (pf_core.metrics.cluster_bootstrap_diff).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pf_core import dists, metrics, models as M

DIST_CANDIDATES = {
    "count": ["poisson", "nb", "nb_binned", "empirical_ratio"],
    # nb_binned is NOT a yards candidate: it lives on 0.. and pf_core's DistBatch clips out-of-support outcomes to the
    # boundary (crps/logpmf understate the loss of negative-yard games), which would bias the selection toward it.
    "yards": ["normal_binned", "empirical_resid", "empirical_ratio"],
    "binary": ["bernoulli"],
}


def fit_dist(kind: str, family_kind: str, y, mu, lo: int, K: int) -> dict:
    y = np.asarray(y, float)
    mu = np.asarray(mu, float)
    ok = np.isfinite(y) & np.isfinite(mu)
    y, mu = y[ok], mu[ok]
    if kind == "bernoulli":
        return {"kind": "bernoulli"}
    if kind in ("poisson", "nb", "nb_binned"):
        # NB/Poisson live on 0..K; yards are clipped at 0 for these families (documented)
        p = M.fit_dist_params(kind, np.clip(y, 0, None), np.maximum(mu, 0.05))
        p["K"] = K + max(lo, 0) if family_kind != "yards" else K + lo
        return p
    if kind == "normal_binned":
        return M.fit_dist_params(kind, y, mu, lo=lo, K=K, floor_at=None)
    return M.fit_dist_params(kind, y, np.maximum(mu, 0.05) if kind == "empirical_ratio" else mu, lo=lo, K=K)


def make(params: dict, mu) -> dists.DistBatch:
    mu = np.asarray(mu, float)
    if params["kind"] == "bernoulli":
        p = np.clip(mu, 1e-4, 1 - 1e-4)
        return dists.DistBatch(0, np.column_stack([1 - p, p]))
    if params["kind"] in ("poisson", "nb", "nb_binned", "empirical_ratio"):
        mu = np.maximum(mu, 0.05)
    return M.make_dist(params, mu)


def score(y, mu, dist: dists.DistBatch, clusters, rungs=None) -> dict:
    y = np.asarray(y, float)
    pm = metrics.point_metrics(y, mu)
    dm = metrics.dist_metrics(y, dist, thresholds=rungs)
    out = {"n_obs": pm["n"], "n_clusters": int(pd.Series(clusters).nunique()), "mae": pm["mae"], "rmse": pm["rmse"],
           "bias": pm["bias"], "corr": pm["corr"], "mean_actual": pm["mean_actual"], "mean_pred": pm["mean_pred"],
           "crps": dm["crps"], "log_score": dm["log_score"], "cover_50": dm["cover_50"], "cover_80": dm["cover_80"],
           "cover_90": dm["cover_90"], "range_cover_80": dm["range_cover_80"], "pit_var_ratio": dm["pit_var_ratio"],
           "pit_deciles": dm["pit_deciles"], "thresholds": dm.get("thresholds", {})}
    return out


def crps_vec(y, dist):
    return dist.crps(np.asarray(y, float))


def diff(loss_a, loss_b, clusters, n_boot=1000):
    r = metrics.cluster_bootstrap_diff(loss_a, loss_b, clusters, n_boot=n_boot)
    return {"mean_diff": r["mean_diff"], "ci95": r["ci95"], "z": r["z"]}


def threshold_reliability(y, dist, rungs) -> list[dict]:
    out = []
    y = np.asarray(y, float)
    for k in rungs:
        p = dist.prob_ge(k)
        o = (y >= k).astype(float)
        out.append({"rung": f"{k}+", "mean_p": float(p.mean()), "hit_rate": float(o.mean()),
                    "brier": float(np.mean((p - o) ** 2)), "ece": metrics.ece(p, o),
                    "table": metrics.calibration_table(p, o, bins=5)})
    return out
