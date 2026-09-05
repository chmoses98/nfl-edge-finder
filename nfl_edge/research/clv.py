"""Closing-line value: did the market move toward us, and could it have been captured?

Two traps this module is built to avoid.

**The sign(0) trap.** An unchanged price has not moved toward or away from anything. `np.sign(0) == 0`, so
naive code scores every unchanged quote as "moved away" -- in session 2 that alone dragged a toward-outcome
share to 0.367 +- 0.030, a four-sigma finding that was pure tie handling. Here unchanged quotes are counted
in their own bucket and never assigned a direction.

**The shared-baseline trap.** Regressing (price_close - price_T) on (model - price_T) puts price_T on both
sides with opposite signs. Any measurement noise in price_T then produces a positive slope with no
information whatsoever -- ordinary regression to the mean, reported as "the market moves toward us". The
honest specification enters the model and the market price as SEPARATE regressors:

    price_close - price_T  ~  a + b * model_T + c * price_T

Under the null that the model knows nothing about future movement, b = 0. Noise in price_T is absorbed by c.
Only b is evidence.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np

UNCHANGED_TOL = 1e-9


def clustered_se(values, clusters):
    v = np.asarray(values, float)
    n = len(v)
    if n < 2:
        return None
    by = defaultdict(float)
    for x, c in zip(v - v.mean(), clusters):
        by[c] += x
    g = len(by)
    if g < 2:
        return None
    return float(np.sqrt(max(sum(t * t for t in by.values()) / (n * n) * (g / (g - 1.0)), 0.0)))


def movement_direction(price_from, price_to, model_p, tol=UNCHANGED_TOL):
    """Per-contract movement label. Returns one of 'toward', 'away', 'unchanged', 'no_view'.

    'no_view' is when the model agrees with the price to within tol -- there is no direction to move toward.
    Neither 'unchanged' nor 'no_view' is ever folded into toward/away.
    """
    d = np.asarray(price_to, float) - np.asarray(price_from, float)
    view = np.asarray(model_p, float) - np.asarray(price_from, float)
    out = np.full(len(d), "unchanged", dtype=object)
    moved = np.abs(d) > tol
    has_view = np.abs(view) > tol
    out[moved & ~has_view] = "no_view"
    both = moved & has_view
    out[both & (np.sign(d) == np.sign(view))] = "toward"
    out[both & (np.sign(d) != np.sign(view))] = "away"
    return out


def signed_clv(price_from, price_to, model_p):
    """Movement in the direction of our view, in probability points. Zero when we hold no view."""
    d = np.asarray(price_to, float) - np.asarray(price_from, float)
    view = np.asarray(model_p, float) - np.asarray(price_from, float)
    s = np.sign(view)
    s[np.abs(view) <= UNCHANGED_TOL] = 0.0
    return d * s


def movement_regression(model_p, price_t, price_later, clusters):
    """price_later - price_t ~ a + b*model_p + c*price_t, with cluster-robust standard errors.

    b is the only coefficient that is evidence of information; c absorbs mean reversion in price_t.
    """
    y = np.asarray(price_later, float) - np.asarray(price_t, float)
    X = np.column_stack([np.ones(len(y)), np.asarray(model_p, float), np.asarray(price_t, float)])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    XtX_inv = np.linalg.pinv(X.T @ X)
    agg = defaultdict(lambda: np.zeros(X.shape[1]))
    for i, c in enumerate(clusters):
        agg[c] += X[i] * resid[i]
    meat = np.zeros((X.shape[1], X.shape[1]))
    for v in agg.values():
        meat += np.outer(v, v)
    g = len(agg)
    V = XtX_inv @ meat @ XtX_inv * (g / max(g - 1, 1))
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    return {"intercept": float(beta[0]), "b_model": float(beta[1]), "c_price": float(beta[2]),
            "se_model": float(se[1]), "se_price": float(se[2]),
            "z_model": float(beta[1] / se[1]) if se[1] else float("nan"),
            "n": int(len(y)), "clusters": g}


def naive_movement_regression(model_p, price_t, price_later, clusters):
    """The contaminated specification, kept so the contamination can be SHOWN rather than asserted.

    price_later - price_t ~ a + b*(model_p - price_t). Under pure noise in price_t and a model with no
    information at all, b is positive by construction.
    """
    y = np.asarray(price_later, float) - np.asarray(price_t, float)
    d = np.asarray(model_p, float) - np.asarray(price_t, float)
    X = np.column_stack([np.ones(len(y)), d])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    XtX_inv = np.linalg.pinv(X.T @ X)
    agg = defaultdict(lambda: np.zeros(2))
    for i, c in enumerate(clusters):
        agg[c] += X[i] * resid[i]
    meat = np.zeros((2, 2))
    for v in agg.values():
        meat += np.outer(v, v)
    g = len(agg)
    V = XtX_inv @ meat @ XtX_inv * (g / max(g - 1, 1))
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    return {"b_disagreement": float(beta[1]), "se": float(se[1]),
            "z": float(beta[1] / se[1]) if se[1] else float("nan"), "n": int(len(y)), "clusters": g}
