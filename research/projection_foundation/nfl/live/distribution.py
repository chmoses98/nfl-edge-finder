"""Quantiles and the integer line ladder of a projection's pmf, and the checks that make them trustworthy.

Every player row of `projections/nfl/latest.json` is the summary of ONE integer pmf (the one archived write-once in
`forecasts/nfl/`). The expected value, the median, the 80% range (p10..p90) and the threshold probabilities (P(X >= k)) are read
from it by the existing publisher; this module reads the quantiles and the full line ladder from the SAME pmf, so a reader that
draws the distribution, quotes the range and prices a line is reading one forecast, never two. They are published in a separate
versioned artifact (`distributions_artifact.py`), not by editing the protected research code that writes `latest.json`.

Quantile rule (the one `pf_core.dists.DistBatch.quantile` already uses for p10 / median / p90): the smallest integer x with
P(X <= x) >= level. Nothing is interpolated or smoothed; every value is a point of the pmf's support.

`validate_row` re-derives what the quantiles imply for the other numbers of a row, so a row whose pieces disagree is detected on the
document alone (no pmf needed):
  * q_a = min{x : F(x) >= a}  =>  F(q_a - 1) < a  and  F(q_a) >= a
  * so for an integer line k:  k <= q_a  =>  P(X >= k) >  1 - a   and   k > q_a  =>  P(X >= k) <= 1 - a
A row that fails is left out of the artifact (readers then say "no published distribution") rather than published with a number
that contradicts its own probabilities.
"""
from __future__ import annotations

import math

LEVELS: tuple[tuple[str, float], ...] = (("p05", 0.05), ("p10", 0.10), ("p25", 0.25), ("p50", 0.50), ("p75", 0.75), ("p90", 0.90), ("p95", 0.95))
KEYS = tuple(k for k, _ in LEVELS)
RULE = "smallest integer x with P(X <= x) >= level, from the same integer pmf as the mean and the threshold probabilities"
# thresholds are published rounded to 4 decimals
TOL = 1.5e-4

META = {
    "basis": "integer pmf (one per player row, archived in forecasts/nfl): mean, median, p10/p90, quantiles and the line ladder are all read from it",
    "quantile_rule": RULE,
    "levels": [lvl for _, lvl in LEVELS],
}


def quantile_arrays(dist) -> dict:
    """{key: int array over the batch}, one `DistBatch.quantile` call per level."""
    return {k: dist.quantile(lvl) for k, lvl in LEVELS}


def row_quantiles(qa: dict, j: int) -> dict:
    return {k: int(qa[k][j]) for k in KEYS}


# A count outcome (receptions, completions, ...) is priced on an integer ladder that is not the study's three rungs, so a reader
# pricing a market line needs P(X >= k) for every k the distribution actually spreads over. They come from the same pmf; the
# tails below LADDER_MIN are left out (they carry no decision). Yardage families keep the study's rungs: a yards ladder is
# 20-200 wide and no promoted family uses it.
LADDER_KINDS = ("count", "binary")
LADDER_MIN = 1e-3


def survival_arrays(dist, kind: str) -> dict:
    """{k: P(X >= k) over the batch} for every integer k above the support's floor, for count / binary families; {} otherwise."""
    if kind not in LADDER_KINDS:
        return {}
    return {k: dist.prob_ge(k) for k in range(max(1, dist.lo + 1), dist.lo + dist.P.shape[1] + 1)}


def row_thresholds(surv: dict, study: dict, j: int) -> dict:
    """The published `thresholds` of row j: the study's rungs (always) plus, for count families, every k with LADDER_MIN <= P(X >= k)
    <= 1 - LADDER_MIN. `study` is {k: array} for the study rungs."""
    ks = {k for k, a in surv.items() if LADDER_MIN <= a[j] <= 1 - LADDER_MIN} | set(study)
    return {str(k): round(float((study[k] if k in study else surv[k])[j]), 4) for k in sorted(ks)}


def validate_row(row: dict) -> list[str]:
    """Problems with the row's `quantiles` against its own mean / median / p10 / p90 / thresholds; [] = coherent.
    A row with no `quantiles` has nothing to validate here."""
    q = row.get("quantiles")
    if q is None:
        return []
    if not isinstance(q, dict):
        return ["quantiles is not an object"]
    out: list[str] = []
    vals = []
    for k in KEYS:
        v = q.get(k)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            out.append(f"{k} is missing or not a finite number")
        else:
            vals.append(float(v))
    if out:
        return out
    if extra := set(q) - set(KEYS):
        out.append(f"unexpected quantile keys {sorted(extra)}")
    if any(v < 0 for v in vals):
        out.append("a quantile is negative")
    if any(v != int(v) for v in vals):
        out.append("a quantile is not an integer (the pmf is on integers)")
    if any(b < a for a, b in zip(vals, vals[1:])):
        out.append("quantiles are not in non-decreasing order")
    for key, ref in (("p50", "median"), ("p10", "p10"), ("p90", "p90")):
        if row.get(ref) is not None and q[key] != row[ref]:
            out.append(f"{key} ({q[key]}) disagrees with the row's {ref} ({row[ref]})")
    mean = row.get("mean")
    if not isinstance(mean, (int, float)) or isinstance(mean, bool) or not math.isfinite(mean) or mean < 0:
        out.append("mean is missing, not finite or negative")
    th = row.get("thresholds") or {}
    pts = []
    for ks, p in th.items():
        try:
            k = float(ks)
        except (TypeError, ValueError):
            out.append(f"threshold key {ks!r} is not a number")
            continue
        if isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p) or not 0.0 <= p <= 1.0:
            out.append(f"threshold {ks} probability {p!r} is not a probability")
            continue
        pts.append((k, float(p)))
    pts.sort()
    for (k0, p0), (k1, p1) in zip(pts, pts[1:]):
        if p1 > p0 + TOL:
            out.append(f"P(X>={k1:g}) exceeds P(X>={k0:g}): the probabilities are not one survival function")
    for key, lvl in LEVELS:
        for k, p in pts:
            if k != int(k):
                continue
            if k <= q[key] and not p > 1 - lvl - TOL:
                out.append(f"P(X>={k:g})={p} is too low for {key}={q[key]:g} (must exceed {1 - lvl:.2f})")
            elif k > q[key] and not p <= 1 - lvl + TOL:
                out.append(f"P(X>={k:g})={p} is too high for {key}={q[key]:g} (must be at most {1 - lvl:.2f})")
    return out
