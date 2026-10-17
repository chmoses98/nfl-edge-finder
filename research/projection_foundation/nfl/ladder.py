"""Model ladder A..F for NFL team and player families.

A  season-to-date + last season, shrunk to a point-in-time positional/league prior (k tuned on development)
B  EWMA (halflife tuned on development), shrunk
C  opportunity x efficiency (team volume x player share x per-opportunity rate, each EWMA-shrunk)
D  C with game environment (closing spread/total) and schedule-adjusted opponent factors (rolling ridge),
   elasticities fitted on development rows only (Poisson / Bernoulli likelihood with a log offset)
E  LightGBM on PIT features, refitted walk-forward every season (train on all earlier seasons)
F  non-negative stack of B, C, D, E fitted on development predictions only (dev+validation for holdout use)

Tuning objective everywhere: squared error of the mean on development rows (2016-2021).
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from pf_core import models as M
from pf_core.pit import eb_shrink

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

DEV = (2016, 2021)
VAL = (2022, 2023)
HOLD = (2024, 2025)
K_GRID = (1.0, 2.0, 4.0, 8.0, 16.0, 32.0)
H_GRID = (2, 4, 8, 16)


def split_of(season: pd.Series, week: pd.Series, upcoming: pd.Series | None = None) -> pd.Series:
    s = pd.Series("warmup", index=season.index)
    s[season.between(*DEV)] = "development"
    s[season.between(*VAL)] = "validation"
    s[season.between(*HOLD)] = "holdout"
    s[(season == 2026) & (week <= 4)] = "check2026"
    s[(season == 2026) & (week >= 5)] = "embargo2026"   # untouched market holdout: never scored here
    if upcoming is not None:
        s[upcoming.astype(bool)] = "forward"
    return s


def _mse(y, p):
    m = np.isfinite(p) & np.isfinite(y)
    return float(np.mean((y[m] - p[m]) ** 2))


# ----------------------------------------------------------------------------- priors (point in time)
def ratio_prior_pit(df: pd.DataFrame, group: str, num: str, den: str, fallback: float) -> pd.Series:
    """sum(num)/sum(den) for the entity's group over rows on EARLIER blocks only (ratio of sums, not mean of ratios)."""
    d = df[[group, "block", num, den]].copy()
    agg = d.groupby([group, "block"])[[num, den]].sum().reset_index().sort_values([group, "block"])
    g = agg.groupby(group, sort=False)
    agg["_n"] = g[num].cumsum() - agg[num]
    agg["_d"] = g[den].cumsum() - agg[den]
    agg["_r"] = agg["_n"] / agg["_d"].replace(0, np.nan)
    out = d.merge(agg[[group, "block", "_r"]], on=[group, "block"], how="left")["_r"]
    out.index = df.index
    return out.fillna(fallback)


def mean_prior_pit(df, group, col):
    return M.group_prior_pit(df, [group], "block", col)


# ----------------------------------------------------------------------------- A / B tuning
def tune_A(df, col, prior, y, dev_mask):
    best = None
    for k in K_GRID:
        p = M.est_A(df, col, prior, k).to_numpy()
        e = _mse(y[dev_mask], p[dev_mask])
        if best is None or e < best[0]:
            best = (e, k)
    return {"k": best[1]}, M.est_A(df, col, prior, best[1])


def tune_B(df, col, prior, y, dev_mask, halflives=H_GRID):
    best = None
    for h in halflives:
        if f"{col}_ewm{h}" not in df.columns:
            continue
        for k in K_GRID:
            p = M.est_B(df, col, prior, k, h).to_numpy()
            e = _mse(y[dev_mask], p[dev_mask])
            if best is None or e < best[0]:
                best = (e, k, h)
    return {"k": best[1], "halflife": best[2]}, M.est_B(df, col, prior, best[1], best[2])


def tune_rate(df, num, den, prior_rate, y_rate_target, base, dev_mask, halflives=H_GRID, kgrid=(5, 10, 20, 40, 80, 160)):
    """Efficiency rate (num per den) via pf_core.models.ratio_rate; tuned so that base*rate fits the outcome (MSE)."""
    best = None
    for h in halflives:
        if f"{num}_ewm{h}" not in df.columns:
            continue
        for k in kgrid:
            r = M.ratio_rate(df, num, den, h, prior_rate, k).to_numpy()
            e = _mse(y_rate_target[dev_mask], (base * r)[dev_mask])
            if best is None or e < best[0]:
                best = (e, k, h)
    return {"k_den": best[1], "halflife": best[2]}, M.ratio_rate(df, num, den, best[2], prior_rate, best[1])


# ----------------------------------------------------------------------------- D: log-linear elasticities on dev
def fit_loglinear(y, base, X, dev_mask, link="poisson"):
    """mu = base * exp(X @ b) (poisson) or p = 1 - exp(-base*exp(X@b)) (bernoulli, base = TD intensity).
    X columns are centred log-factors / standardised environment terms. Fitted on dev rows only."""
    y = np.asarray(y, float)[dev_mask]
    b0 = np.maximum(np.asarray(base, float)[dev_mask], 1e-6)
    Xd = np.nan_to_num(np.asarray(X, float)[dev_mask])
    ok = np.isfinite(y)
    y, b0, Xd = y[ok], b0[ok], Xd[ok]

    def nll(beta):
        lam = b0 * np.exp(np.clip(Xd @ beta, -3, 3))
        if link == "poisson":
            return float(np.sum(lam - y * np.log(lam))) / len(y) + 1e-4 * float(beta @ beta)
        p = np.clip(1 - np.exp(-lam), 1e-6, 1 - 1e-6)
        return float(-np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))) / len(y) + 1e-4 * float(beta @ beta)

    r = minimize(nll, np.zeros(Xd.shape[1]), method="L-BFGS-B")
    return r.x


def apply_loglinear(base, X, beta):
    return np.asarray(base, float) * np.exp(np.clip(np.nan_to_num(np.asarray(X, float)) @ beta, -3, 3))


# ----------------------------------------------------------------------------- E: LightGBM walk-forward
def lgbm(df, feats, target, objective, train_mask, first_season=2013, params=None):
    d = df.copy()
    d["_train"] = train_mask & d[target].notna() & (d.season >= first_season)
    pr = {"n_jobs": 2}
    if params:
        pr.update(params)
    blocks = sorted(d.season.unique())
    mtb = blocks.index(2016) if 2016 in blocks else 3
    return M.lgbm_walkforward(d, feats, target, "season", objective=objective, min_train_blocks=mtb, params=pr,
                              train_mask_col="_train")


def stack(preds: pd.DataFrame, y, fit_mask):
    cols = list(preds.columns)
    P = preds.to_numpy(float)
    ok = fit_mask & np.isfinite(P).all(axis=1) & np.isfinite(y)
    w = M.fit_stack_weights(y[ok], P[ok])
    return dict(zip(cols, w.tolist())), P @ w
