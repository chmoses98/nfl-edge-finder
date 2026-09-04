"""Ladder pricing and consistency checks.

price_yes(sem, dist) -> probability that a Kalshi contract with MarketSemantics `sem` settles YES, given a
distribution for the underlying statistic. `dist` is either an array of Monte-Carlo samples or a callable
survival function S(x) = P(Y > x). Semantics follow docs/KALSHI_MARKET_TAXONOMY.md:
  operator ">="  : YES iff Y >= threshold (integer ladders: totals, yards, receptions, TDs, season wins)
  operator ">"   : YES iff Y >  floor_strike (spreads: team margin > 7.5)
  operator "range": YES iff range_lo <= Y <= range_hi (win-margin buckets; inclusive both ends)
Market-side checks (check_market_ladder) flag monotonicity violations in quoted prices across strikes of the same
event/team so relative-value candidates surface without any model.
"""
from __future__ import annotations
import numpy as np


def _survival(dist):
    if callable(dist):
        return dist
    x = np.asarray(dist, dtype=float)
    return lambda t: float(np.mean(x > t))


def price_yes(sem, dist) -> float | None:
    S = _survival(dist)
    if sem.operator == ">=" and sem.threshold is not None:
        return S(sem.threshold - 1e-9)          # P(Y >= K) = P(Y > K - eps)
    if sem.operator == ">" and sem.floor_strike is not None:
        return S(float(sem.floor_strike))
    if sem.operator == "range" and sem.range_lo is not None:
        hi = sem.range_hi if sem.range_hi is not None else np.inf
        return S(sem.range_lo - 1e-9) - (S(hi + 1e-9) if np.isfinite(hi) else 0.0)
    return None


def model_ladder_is_monotone(probs_by_threshold: dict) -> bool:
    ks = sorted(probs_by_threshold)
    ps = [probs_by_threshold[k] for k in ks]
    return all(a >= b - 1e-12 for a, b in zip(ps, ps[1:]))


def check_market_ladder(rows, price_key="yes_ask_dollars", bid_key="yes_bid_dollars"):
    """rows: quote rows (dicts) for ONE ladder (same event, same team/player, family with numeric threshold).
    Returns list of violations: a higher strike quoted with a higher yes bid than a lower strike's yes ask
    (i.e. you could buy the easier contract cheaper than someone bids for the harder one) and plain
    non-monotone mid prices."""
    out = []
    xs = []
    for r in rows:
        k = r.get("threshold") if r.get("threshold") is not None else r.get("floor_strike")
        try:
            bid = float(r.get(bid_key) or 0); ask = float(r.get(price_key) or 1)
        except (TypeError, ValueError):
            continue
        if k is None:
            continue
        xs.append((float(k), bid, ask, r.get("ticker")))
    xs.sort()
    for (k1, b1, a1, t1), (k2, b2, a2, t2) in zip(xs, xs[1:]):
        if b2 > a1 + 1e-9:                      # harder contract bid above easier contract ask -> locked inconsistency
            out.append({"type": "crossed", "lower": t1, "upper": t2, "lower_ask": a1, "upper_bid": b2, "gap": round(b2 - a1, 4)})
        m1 = (b1 + a1) / 2; m2 = (b2 + a2) / 2
        if m2 > m1 + 1e-9 and a1 < 1 and b2 > 0:
            out.append({"type": "mid_nonmonotone", "lower": t1, "upper": t2, "lower_mid": round(m1, 4), "upper_mid": round(m2, 4)})
    return out
