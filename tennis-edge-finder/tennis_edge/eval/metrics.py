"""Proper scoring rules, calibration diagnostics and bootstrap intervals.

All functions take y (0/1 outcome for the FIRST-listed player or 'yes' side) and p (probability of y=1).
"""
from __future__ import annotations

import numpy as np


def brier(y, p) -> float:
    y = np.asarray(y, float); p = np.asarray(p, float)
    return float(np.mean((p - y) ** 2))


def log_loss(y, p, eps: float = 1e-6) -> float:
    y = np.asarray(y, float); p = np.clip(np.asarray(p, float), eps, 1 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def accuracy(y, p) -> float:
    y = np.asarray(y, float); p = np.asarray(p, float)
    return float(np.mean((p > 0.5) == (y == 1)))


def calibration_slope_intercept(y, p, eps: float = 1e-6) -> tuple[float, float]:
    """Logistic recalibration: fit y ~ a + b * logit(p) by Newton's method. Perfect calibration: a=0, b=1."""
    y = np.asarray(y, float); p = np.clip(np.asarray(p, float), eps, 1 - eps)
    x = np.log(p / (1 - p))
    a, b = 0.0, 1.0
    for _ in range(50):
        z = a + b * x
        q = 1 / (1 + np.exp(-z))
        w = q * (1 - q)
        g = np.array([np.sum(q - y), np.sum((q - y) * x)])
        H = np.array([[np.sum(w), np.sum(w * x)], [np.sum(w * x), np.sum(w * x * x)]]) + 1e-9 * np.eye(2)
        step = np.linalg.solve(H, g)
        a -= step[0]; b -= step[1]
        if np.max(np.abs(step)) < 1e-10:
            break
    return float(b), float(a)


def ece(y, p, bins: int = 10) -> float:
    y = np.asarray(y, float); p = np.asarray(p, float)
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    tot = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            tot += m.mean() * abs(p[m].mean() - y[m].mean())
    return float(tot)


def reliability_table(y, p, bins: int = 10):
    y = np.asarray(y, float); p = np.asarray(p, float)
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    rows = []
    for b in range(bins):
        m = idx == b
        rows.append({"bin": f"{edges[b]:.1f}-{edges[b + 1]:.1f}", "n": int(m.sum()), "mean_p": float(p[m].mean()) if m.any() else None,
                     "obs_rate": float(y[m].mean()) if m.any() else None})
    return rows


def bootstrap_diff(y, p1, p2, metric=brier, n_boot: int = 1000, seed: int = 0) -> dict:
    """Paired bootstrap CI for metric(p1) - metric(p2). Negative = model 1 better (lower loss)."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y, float); p1 = np.asarray(p1, float); p2 = np.asarray(p2, float)
    n = len(y)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        diffs[i] = metric(y[idx], p1[idx]) - metric(y[idx], p2[idx])
    point = metric(y, p1) - metric(y, p2)
    return {"diff": float(point), "ci_low": float(np.percentile(diffs, 2.5)), "ci_high": float(np.percentile(diffs, 97.5)), "n": int(n),
            "p_better": float(np.mean(diffs < 0))}


def summary(y, p) -> dict:
    b, a = calibration_slope_intercept(y, p)
    return {"n": int(len(y)), "brier": brier(y, p), "log_loss": log_loss(y, p), "accuracy": accuracy(y, p), "ece": ece(y, p),
            "cal_slope": b, "cal_intercept": a}
