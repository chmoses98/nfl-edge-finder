"""The market-implied distribution as the DEFAULT prior, and a decomposition of disagreement with it.

Session 2 established that at the 2025 close the independent football model is statistically redundant to the
Kalshi price: with the market included, the model's incremental coefficient was -0.0007 +- 0.0756. Building a
better standalone projection is therefore not the frontier. The frontier is:

    market-implied distribution at T  +  information not yet priced at T  ->  our distribution.

This module turns a quoted ladder into a *research object* with named parts — location, scale, tail
curvature, zero mass — so that "we disagree with the market" can be answered with WHY rather than with two
numbers. It keeps four price surfaces strictly separate:

    executable YES ask   what a YES buyer actually pays
    executable NO ask    what a NO buyer actually pays (1 - yes_bid)
    midpoint             a research construct, NOT executable, never a fair value
    fitted latent        a smooth distribution fitted to the book; a research object only

The economic benchmark is always the executable book. The fitted latent is for locating disagreement, never
for claiming a price.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import special

from nfl_edge.pricing.market_implied import pav_monotone_decreasing

EPS = 1e-6


@dataclass
class MarketShape:
    """A Weibull summary of a quoted ladder: S(k) = exp(-(k/lam)**gam) for k > 0.

    gam is the shape: gam < 1 is a heavier-than-exponential tail, gam > 1 a lighter one. lam is the scale.
    `curvature` is the quadratic term of log(-log S) against log k -- a departure from Weibull, i.e. the
    market's tail bending away from the fitted family, which is exactly the kind of local distortion a role
    shock could produce.
    """
    side: str
    n_points: int
    ks: np.ndarray
    s_obs: np.ndarray
    s_fit: np.ndarray
    lam: float | None = None
    gam: float | None = None
    curvature: float | None = None
    fit_rmse: float | None = None
    implied_mean: float | None = None
    implied_sd: float | None = None
    median_width: float | None = None
    ok: bool = False
    reason: str = ""

    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items() if not isinstance(v, np.ndarray)}
        d["ks"] = [float(x) for x in self.ks]
        d["s_obs"] = [float(x) for x in self.s_obs]
        d["s_fit"] = [float(x) for x in self.s_fit]
        return d


def _survival_points(rows, side):
    """(k, price, width) for one ladder on one price surface, monotone-corrected."""
    pts = []
    for r in rows:
        k = r.get("threshold")
        b, a = r.get("yes_bid"), r.get("yes_ask")
        if k is None or b is None or a is None or not (0.0 <= b <= a <= 1.0):
            continue
        if b <= 0.0 and a >= 1.0:
            continue                      # empty book: not a quote
        p = a if side == "yes_ask" else (b if side == "yes_bid" else (a + b) / 2.0)
        pts.append((float(k), float(p), float(a - b)))
    if not pts:
        return np.array([]), np.array([]), np.array([])
    pts.sort()
    ks = np.array([p[0] for p in pts]); ps = np.array([p[1] for p in pts]); ws = np.array([p[2] for p in pts])
    # width-weighted monotone fit: a tight quote should not be pulled by a wide one next to it
    wts = 1.0 / np.clip(ws, 0.01, None)
    return ks, pav_monotone_decreasing(ks, ps, wts), ws


def fit_market_shape(rows, side="mid", min_points=3) -> MarketShape:
    """Fit a Weibull to a quoted ladder and report its named parts."""
    ks, s, ws = _survival_points(rows, side)
    shape = MarketShape(side=side, n_points=len(ks), ks=ks, s_obs=s, s_fit=np.array([]))
    if len(ks) < min_points:
        shape.reason = f"only {len(ks)} usable rungs"
        return shape
    shape.median_width = float(np.median(ws))
    use = (s > EPS) & (s < 1 - EPS) & (ks > 0)
    if use.sum() < min_points:
        shape.reason = "too few rungs strictly inside (0,1)"
        return shape
    x = np.log(ks[use])
    z = np.log(-np.log(np.clip(s[use], EPS, 1 - EPS)))
    w = 1.0 / np.clip(ws[use], 0.01, None)
    # linear part gives the Weibull; the quadratic term measures departure from it
    A1 = np.column_stack([np.ones(use.sum()), x])
    b1 = np.linalg.lstsq(A1 * w[:, None], z * w, rcond=None)[0]
    gam = float(b1[1])
    if not np.isfinite(gam) or gam <= 0.05 or gam > 40:
        shape.reason = f"implausible shape gam={gam:.3f}"
        return shape
    lam = float(np.exp(-b1[0] / gam))
    if use.sum() >= 4:
        A2 = np.column_stack([np.ones(use.sum()), x, x ** 2])
        b2 = np.linalg.lstsq(A2 * w[:, None], z * w, rcond=None)[0]
        shape.curvature = float(b2[2])
    fitted_full = np.exp(-np.power(np.clip(ks, EPS, None) / lam, gam))
    shape.s_fit = np.clip(fitted_full, 0.0, 1.0)
    shape.fit_rmse = float(np.sqrt(np.mean((shape.s_fit[use] - s[use]) ** 2)))
    shape.lam, shape.gam = lam, gam
    try:
        m1 = special.gamma(1.0 + 1.0 / gam)
        m2 = special.gamma(1.0 + 2.0 / gam)
        shape.implied_mean = float(lam * m1)
        var = lam ** 2 * (m2 - m1 ** 2)
        shape.implied_sd = float(np.sqrt(var)) if var > 0 else None
    except (ValueError, OverflowError):
        pass
    shape.ok = True
    return shape


# --------------------------------------------------------------------------------------- decomposition
def _weibull_S(ks, lam, gam):
    return np.clip(np.exp(-np.power(np.clip(np.asarray(ks, float), EPS, None) / lam, gam)), 0.0, 1.0)


@dataclass
class Disagreement:
    """Why our distribution differs from the market's, in named parts that sum to the total."""
    total: float
    location: float = 0.0
    scale: float = 0.0
    shape: float = 0.0
    residual: float = 0.0
    model_mean: float | None = None
    market_mean: float | None = None
    model_sd: float | None = None
    market_sd: float | None = None
    model_gam: float | None = None
    market_gam: float | None = None
    n_rungs: int = 0
    notes: str = ""
    parts: dict = field(default_factory=dict)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}


def decompose_disagreement(ks, model_S, market_shape: MarketShape) -> Disagreement | None:
    """Attribute |model - market| across the ladder to location, scale and tail shape.

    Sequential attribution: start from the model's own fitted Weibull, move its location to the market's,
    then its scale, then its shape, recording how much of the total gap each step closes. Whatever remains is
    residual -- genuine rung-level structure that no location/scale/shape move explains, which is where a
    localised distortion would live.
    """
    ks = np.asarray(ks, float)
    model_S = np.clip(np.asarray(model_S, float), 0.0, 1.0)
    if not market_shape.ok or market_shape.lam is None:
        return None
    mk = market_shape.ks
    common = np.intersect1d(ks, mk)
    if len(common) < 3:
        return None
    mi = np.searchsorted(ks, common); ki = np.searchsorted(mk, common)
    mS = model_S[mi]; qS = market_shape.s_obs[ki]
    total = float(np.abs(mS - qS).sum())

    # fit the same family to the model's own curve so the two are compared like for like
    use = (mS > EPS) & (mS < 1 - EPS) & (common > 0)
    if use.sum() < 3:
        return None
    x = np.log(common[use]); z = np.log(-np.log(np.clip(mS[use], EPS, 1 - EPS)))
    b = np.linalg.lstsq(np.column_stack([np.ones(use.sum()), x]), z, rcond=None)[0]
    g_m = float(b[1])
    if not np.isfinite(g_m) or g_m <= 0.05 or g_m > 40:
        return None
    l_m = float(np.exp(-b[0] / g_m))
    l_q, g_q = market_shape.lam, market_shape.gam

    def gap(lam, gam):
        return float(np.abs(_weibull_S(common, lam, gam) - qS).sum())

    d0 = gap(l_m, g_m)                     # model as fitted
    d1 = gap(l_q, g_m)                     # location moved to the market's
    d2 = gap(l_q, g_q)                     # shape moved too
    loc = d0 - d1
    shp = d1 - d2
    resid = total - (loc + shp)
    try:
        m1m = special.gamma(1 + 1 / g_m); m2m = special.gamma(1 + 2 / g_m)
        m1q = special.gamma(1 + 1 / g_q); m2q = special.gamma(1 + 2 / g_q)
        mean_m, mean_q = l_m * m1m, l_q * m1q
        sd_m = l_m * np.sqrt(max(m2m - m1m ** 2, 0))
        sd_q = l_q * np.sqrt(max(m2q - m1q ** 2, 0))
    except (ValueError, OverflowError):
        mean_m = mean_q = sd_m = sd_q = None
    return Disagreement(total=total, location=loc, shape=shp, residual=resid, n_rungs=int(len(common)),
                        model_mean=mean_m, market_mean=mean_q, model_sd=sd_m, market_sd=sd_q,
                        model_gam=g_m, market_gam=g_q,
                        parts={"model_as_fitted": d0, "after_location": d1, "after_shape": d2})


def executable_surfaces(rows):
    """The economic benchmark: what a trader could actually do, kept separate from any fitted object."""
    out = {"yes_ask": [], "no_ask": [], "mid": [], "thresholds": [], "widths": []}
    for r in sorted(rows, key=lambda r: (r.get("threshold") if r.get("threshold") is not None else 0)):
        k, b, a = r.get("threshold"), r.get("yes_bid"), r.get("yes_ask")
        if k is None or b is None or a is None or not (0.0 <= b <= a <= 1.0) or (b <= 0 and a >= 1):
            continue
        out["thresholds"].append(float(k))
        out["yes_ask"].append(float(a))
        out["no_ask"].append(float(1.0 - b))
        out["mid"].append(float((a + b) / 2.0))
        out["widths"].append(float(a - b))
    return out
