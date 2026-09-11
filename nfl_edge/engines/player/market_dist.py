"""MARKET_PLAYER_DIST: the market's own distribution of a player statistic, inferred from its quoted ladder.

When Kalshi lists 50+ / 75+ / 100+ for one player, the three prices are three points of one survival function
and carry information about the market's location, dispersion and tail. This module turns a ladder into

    executable bounds     monotone (PAV) envelopes of the YES bids and YES asks: what the market will PAY for
                          and CHARGE for each rung. Never a midpoint.
    research midpoint     the monotone midpoint curve, for probability benchmarking only.
    a full lattice        a two-parameter family (location, dispersion) fitted to the monotone midpoints by
                          width-weighted least squares, so off-ladder rungs and moments are readable.
    identification        FULL / PARTIAL / UNDERIDENTIFIED, decided by the number of rungs, whether the ladder
                          brackets the median and whether it reaches a tail rung. UNDERIDENTIFIED ladders fix the
                          dispersion at a stat-level prior (named on the record) and fit the location only.

No inversion is ever tolerated: the raw violation count is recorded and the PAV projection removes it. A
ladder of one rung does not identify a distribution and is said to not.
"""
from __future__ import annotations

import numpy as np
from scipy import optimize, stats

from nfl_edge.engines.player.dist import LatticeDistribution
from nfl_edge.pricing.market_implied import pav_monotone_decreasing

VERSION = "market-player-dist-1.0.0"
FULL, PARTIAL, UNDERIDENTIFIED, NONE = "FULL", "PARTIAL", "UNDERIDENTIFIED", "NONE"

# family per statistic kind; the same kinds the data arm uses
KIND_OF = {"passing_yards": "yards", "rushing_yards": "yards", "receiving_yards": "yards", "rush_rec_yards": "yards",
           "receptions": "count", "carries": "count", "attempts": "count", "completions": "count", "targets": "count",
           "passing_tds": "td", "touchdowns": "td", "interceptions": "td", "rushing_tds": "td", "receiving_tds": "td"}
GRID_MAX = {"yards": 400, "count": 60, "td": 8}
# dispersion priors used only when the ladder is UNDERIDENTIFIED: CV (yards) or NB dispersion alpha (counts/tds),
# taken from the walk-forward study's fitted families (research/player_distributions/RESULTS.md, sd ~ mu^0.39-0.48)
DISPERSION_PRIOR = {"yards": 0.62, "count": 0.18, "td": 0.05}


def _survival_family(kind: str, k: np.ndarray, loc: float, disp: float) -> np.ndarray:
    """P(Y >= k) under the two-parameter family for a statistic kind."""
    k = np.asarray(k, float)
    if kind == "yards":
        # gamma with mean loc and CV disp, discretised: P(Y >= k) = P(G > k - 0.5)
        shape = 1.0 / float(np.clip(disp, 0.05, 5.0)) ** 2
        scale = max(loc, 0.5) / shape
        return stats.gamma.sf(np.maximum(k - 0.5, 0.0), shape, scale=scale)
    # counts / TDs: negative binomial with mean loc and Var = loc + alpha loc^2
    alpha = float(np.clip(disp, 1e-4, 50.0))
    r = 1.0 / alpha; p = r / (r + max(loc, 1e-3))
    return stats.nbinom.sf(np.ceil(k) - 1, r, p)


def _lattice(kind: str, loc: float, disp: float) -> LatticeDistribution:
    grid = np.arange(0, GRID_MAX[kind] + 1)
    S = _survival_family(kind, grid, loc, disp)
    S[0] = 1.0
    return LatticeDistribution.from_survival(S, meta={"family": "gamma" if kind == "yards" else "negbin", "loc": loc, "disp": disp})


def _fit(kind: str, ks, ps, ws, fix_disp: float | None = None):
    ks = np.asarray(ks, float); ps = np.asarray(ps, float); ws = np.asarray(ws, float)
    # crude location start: the rung where the survival crosses 0.5, else scaled first rung
    order = np.argsort(ks)
    ks, ps, ws = ks[order], ps[order], ws[order]
    if np.any(ps <= 0.5) and np.any(ps >= 0.5):
        loc0 = float(np.interp(0.5, ps[::-1], ks[::-1]))
    else:
        loc0 = float(ks[0] * (1.6 if ps[0] > 0.5 else 0.7))
    loc0 = max(loc0, 0.3)
    disp0 = DISPERSION_PRIOR[kind]

    def loss(theta):
        loc = np.exp(theta[0]); disp = fix_disp if fix_disp is not None else np.exp(theta[1])
        pred = _survival_family(kind, ks, loc, disp)
        return float(np.sum(ws * (pred - ps) ** 2))
    x0 = np.array([np.log(loc0)] if fix_disp is not None else [np.log(loc0), np.log(disp0)])
    r = optimize.minimize(loss, x0, method="Nelder-Mead", options={"xatol": 1e-5, "fatol": 1e-9, "maxiter": 2000})
    loc = float(np.exp(r.x[0])); disp = fix_disp if fix_disp is not None else float(np.exp(r.x[1]))
    disp = float(np.clip(disp, 0.02, 5.0))
    return loc, disp, float(r.fun)


def market_distribution(stat: str, rungs: list, *, max_width: float = 0.20, min_points_full: int = 3) -> dict:
    """rungs: dicts with threshold, yes_bid, yes_ask (dollars), optional volume. Returns the market distribution record.

    Rungs without a two-sided quote, or wider than `max_width`, are excluded from the fit (an empty book is not a
    view) and counted.
    """
    kind = KIND_OF.get(stat)
    if kind is None:
        return {"version": VERSION, "stat": stat, "identification": NONE, "reason": f"no market family for {stat!r}"}
    pts = []
    excluded = 0
    for r in rungs:
        k, b, a = r.get("threshold"), r.get("yes_bid"), r.get("yes_ask")
        if k is None or b is None or a is None or not (0.0 <= b <= a <= 1.0):
            excluded += 1; continue
        w = a - b
        if w > max_width or (b <= 0.0 and a >= 1.0):
            excluded += 1; continue
        pts.append((float(k), float(b), float(a), w))
    pts.sort()
    n = len(pts)
    out = {"version": VERSION, "stat": stat, "kind": kind, "n_rungs_quoted": len(rungs), "n_rungs_used": n, "n_rungs_excluded": excluded}
    if n == 0:
        out.update(identification=NONE, reason="no two-sided quote inside the width limit")
        return out
    ks = np.array([p[0] for p in pts]); bids = np.array([p[1] for p in pts]); asks = np.array([p[2] for p in pts]); widths = np.array([p[3] for p in pts])
    mids = (bids + asks) / 2.0
    w = 1.0 / np.clip(widths, 0.01, None)
    mid_mono = pav_monotone_decreasing(ks, mids, w)
    bid_mono = pav_monotone_decreasing(ks, bids, w)
    ask_mono = pav_monotone_decreasing(ks, asks, w)
    raw_violations = int(np.sum(np.diff(mids) > 1e-9))
    brackets_median = bool(np.any(mid_mono >= 0.5) and np.any(mid_mono <= 0.5))
    has_tail = bool(np.any(mid_mono <= 0.15))
    ident = FULL if (n >= min_points_full and brackets_median and has_tail and np.median(widths) <= 0.10) else (PARTIAL if n >= 2 else UNDERIDENTIFIED)
    fix = None if ident == FULL else (DISPERSION_PRIOR[kind] if ident == UNDERIDENTIFIED else None)
    if ident == PARTIAL and n == 2:
        fix = None
    loc, disp, sse = _fit(kind, ks, mid_mono, w, fix_disp=fix)
    loc_b, disp_b, _ = _fit(kind, ks, bid_mono, w, fix_disp=disp)
    loc_a, disp_a, _ = _fit(kind, ks, ask_mono, w, fix_disp=disp)
    dist = _lattice(kind, loc, disp)
    out.update(identification=ident, raw_violations=raw_violations, brackets_median=brackets_median, has_tail_rung=has_tail,
               median_width=float(np.median(widths)), rungs=[{"k": float(k), "bid": float(b), "ask": float(a), "mid": float(m), "mid_monotone": float(mm),
                                                              "bid_monotone": float(bm), "ask_monotone": float(am)}
                                                             for k, b, a, m, mm, bm, am in zip(ks, bids, asks, mids, mid_mono, bid_mono, ask_mono)],
               location=loc, dispersion=disp, dispersion_source=("fitted" if fix is None else "stat prior (underidentified)"),
               location_bid_side=loc_b, location_ask_side=loc_a, fit_sse=sse, distribution=dist.summary(), family=dist.meta["family"])
    out["_dist"] = dist
    return out


def survival_bounds(rec: dict, k: float) -> dict:
    """For a rung ON the quoted ladder: the executable bid/ask survival; off the ladder: the fitted family only.

    The bounds are the honest executable statement; the fitted value is research.
    """
    if rec.get("identification") in (None, NONE):
        return {"fitted": None, "bid": None, "ask": None, "on_ladder": False}
    fitted = rec["_dist"].survival(k)
    for r in rec.get("rungs", []):
        if abs(r["k"] - k) < 1e-9:
            return {"fitted": fitted, "bid": r["bid_monotone"], "ask": r["ask_monotone"], "on_ladder": True}
    return {"fitted": fitted, "bid": None, "ask": None, "on_ladder": False}
