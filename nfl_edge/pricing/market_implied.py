"""Infer what the MARKET believes, from the ladders it quotes.

Two uses:
 1. `implied_game_lines` — recover the spread/total the Kalshi game ladders imply, so the game-environment
    simulator is centred on the market actually observed at that timestamp rather than a stale reference line.
    (The first session showed a stale consensus line manufactured 6% "mispriced" rungs where the Kalshi-implied
    line produced 0.9%.)
 2. `market_implied_survival` — turn a player's quoted ladder into a monotone survival curve S(k)=P(Y>=k), which
    is the market's own distribution for that statistic. Comparing our distribution to that one localises the
    disagreement (mean vs variance vs tail) instead of reporting one threshold at a time.

Executable vs midpoint: every function takes a `side` argument. "ask" uses what you would actually pay to buy
YES (and 1-bid for NO), "mid" uses the midpoint and is only for studying the midpoint. Nothing here silently
substitutes a midpoint for an executable price.
"""
from __future__ import annotations

import numpy as np


def _price(row, side="mid"):
    b, a = row.get("yes_bid"), row.get("yes_ask")
    if b is None or a is None:
        return None
    if side == "ask":
        return a
    if side == "bid":
        return b
    return (a + b) / 2.0


def pav_monotone_decreasing(ks, ps, weights=None):
    """Pool-adjacent-violators fit of a NON-INCREASING sequence (survival probabilities in k).
    Returns fitted values aligned with the input order."""
    order = np.argsort(ks)
    y = np.asarray(ps, float)[order]
    w = np.ones_like(y) if weights is None else np.asarray(weights, float)[order]
    blocks = [[float(v), float(wi), 1] for v, wi in zip(y, w)]   # [mean, weight, size]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] < blocks[i + 1][0] - 1e-12:              # violates non-increasing
            m1, w1, n1 = blocks[i]; m2, w2, n2 = blocks[i + 1]
            blocks[i:i + 2] = [[(m1 * w1 + m2 * w2) / (w1 + w2), w1 + w2, n1 + n2]]
            i = max(i - 1, 0)
        else:
            i += 1
    expanded = []
    for m, _w, n in blocks:
        expanded.extend([m] * n)
    res = np.empty(len(ps), float)
    res[order] = np.clip(expanded, 0.0, 1.0)
    return res


def market_implied_survival(ladder_rows, side="mid", min_points=3):
    """ladder_rows: dicts with `threshold`, `yes_bid`, `yes_ask` for ONE player+stat (or team+stat).
    Returns dict with the monotone survival points, an implied mean, and diagnostics, or None."""
    pts = []
    for r in ladder_rows:
        k = r.get("threshold")
        p = _price(r, side)
        if k is None or p is None or not (0.0 <= p <= 1.0):
            continue
        pts.append((float(k), float(p), float(r.get("volume") or 0.0), float((r.get("yes_ask") or 1) - (r.get("yes_bid") or 0))))
    if len(pts) < min_points:
        return None
    pts.sort()
    ks = np.array([p[0] for p in pts]); ps = np.array([p[1] for p in pts])
    widths = np.array([p[3] for p in pts])
    w = 1.0 / np.clip(widths, 0.01, None)          # tighter quotes carry more weight
    fitted = pav_monotone_decreasing(ks, ps, w)
    violations = int(np.sum(np.diff(ps) > 1e-9))
    # implied mean via the layer-cake formula over the observed grid, extrapolating the tail geometrically
    mean = 0.0
    if len(ks) >= 2:
        step = np.diff(ks)
        mean = float(ks[0] * fitted[0] + np.sum(step * fitted[1:]))
        if fitted[-1] > 0.02:                       # unresolved upper tail
            mean += float(fitted[-1] * (ks[-1] - ks[-2] if len(ks) > 1 else ks[-1]))
    return {"k": ks.tolist(), "p_raw": ps.tolist(), "p_monotone": fitted.tolist(), "side": side,
            "raw_violations": violations, "implied_mean_lower_bound": mean, "n_points": len(ks),
            "median_width": float(np.median(widths))}


def implied_game_lines(rows, bank, simulate, home_team, away_team, spread_grid=None, total_grid=None,
                       max_width=0.06, min_rungs=6, nsims=20000, seed=3):
    """Least-squares (spread, total) whose coherent simulated distribution best matches the liquid quoted
    full-game winner/spread/total mids. Returns (spread, total, diagnostics) or (None, None, diag)."""
    liq = [r for r in rows if r.get("family") in ("GAME_WINNER", "SPREAD", "TOTAL") and (r.get("period") in ("FULL", None))
           and r.get("yes_bid") is not None and r.get("yes_ask") is not None
           and (r["yes_ask"] - r["yes_bid"]) <= max_width and (r.get("volume") or 0) > 0]
    diag = {"n_liquid_rungs": len(liq)}
    if len(liq) < min_rungs:
        diag["reason"] = "not enough liquid rungs"
        return None, None, diag
    rng = np.random.default_rng(seed)
    spread_grid = spread_grid if spread_grid is not None else np.arange(-17, 17.5, 0.5)
    total_grid = total_grid if total_grid is not None else np.arange(34, 62.5, 0.5)
    best = (np.inf, None, None)
    for s_ in spread_grid:
        for t_ in total_grid:
            sim = simulate(float(s_), float(t_), bank, n=nsims)
            m, t = sim["margin"], sim["total"]
            err = 0.0; wsum = 0.0
            for r in liq:
                mid = (r["yes_bid"] + r["yes_ask"]) / 2.0
                wt = 1.0 / max(0.01, r["yes_ask"] - r["yes_bid"])
                if r["family"] == "GAME_WINNER":
                    pm = float(np.mean(m > 0)) if r.get("team") == home_team else float(np.mean(m < 0))
                elif r["family"] == "SPREAD":
                    x = m if r.get("team") == home_team else -m
                    pm = float(np.mean(x > float(r["floor_strike"])))
                else:
                    pm = float(np.mean(t >= float(r["threshold"])))
                err += wt * (pm - mid) ** 2; wsum += wt
            e = err / wsum
            if e < best[0]:
                best = (e, float(s_), float(t_))
    diag["weighted_sq_error"] = best[0]
    return best[1], best[2], diag
