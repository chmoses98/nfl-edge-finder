"""Fee-inclusive break-even, calibrated fair probability WITH uncertainty, and bet-up-to. Never fabricates.

* break-even per contract = (price*C + whole-order fee(price, C)) / C. The fee is a WHOLE-ORDER figure (rounding is
  applied once to the order), taken from ``nfl_edge.execution.fees.FeeSchedule.entry_fee`` through ``fee_fn_from_schedule``;
  an unknown fee is None and propagates to None. It is never replaced by zero or by a guessed coefficient.
* fair probability comes from HELD-OUT calibration evidence for the market family (observed win rate in the model-
  probability bin, shrunk toward the model with a stated prior strength, normal-approximation bounds on the Beta
  posterior). No evidence -> ``calibrated=False``, p/low/high all None, flag MISSING_CALIBRATION. A raw model
  probability is never promoted to a fair probability here.
* an analyst-DECLARED range (the card's existing ANALYST_DECLARED convention) is accepted as ``calibrated=False`` and the
  result says so; it never reads as a calibrated price.
* bet-up-to = the highest whole-cent price at which the CONSERVATIVE (low) fair probability still covers the fee-
  inclusive break-even at the order size. None when the fair low or any fee is unknown.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .common import MIN_CONSERVATIVE_MARGIN, num

Z_ONE_SIDED_90 = 1.2816
DEFAULT_PRIOR_STRENGTH = 20.0      # pseudo-observations of the model's own probability; owner-adjustable


def fee_fn_from_schedule(schedule, series_ticker, as_of):
    """Wrap FeeSchedule.entry_fee as fee_fn(price, contracts) -> dollars | None (None when the fee is not KNOWN)."""
    def fee(price, contracts):
        q = schedule.entry_fee(price, contracts, series_ticker, as_of=as_of)
        return float(q.amount) if q.is_known else None
    return fee


def break_even_per_contract(price, contracts, fee_fn):
    p, c = num(price), num(contracts)
    if p is None or c is None or c <= 0 or not 0.0 < p < 1.0:
        return None
    fee = fee_fn(p, c)
    return None if fee is None else p + fee / c


def contracts_for_budget(price, budget_dollars, fee_fn, iters=6):
    """Contracts C with C*price + fee(price, C) == budget (stake is fee-inclusive in this ledger)."""
    p, b = num(price), num(budget_dollars)
    if p is None or b is None or b <= 0 or not 0.0 < p < 1.0:
        return None
    c = b / p
    for _ in range(iters):
        fee = fee_fn(p, c)
        if fee is None:
            return None
        c = (b - fee) / p
        if c <= 0:
            return None
    return c


@dataclass(frozen=True)
class CalibrationEvidence:
    """Held-out reliability table for ONE market family (+period). bins: ((p_lo, p_hi, n, wins), ...) on the model probability."""
    family: str
    bins: tuple
    source: str                 # dataset / split id, so the evidence is auditable
    min_n: int = 30

    def cell(self, p):
        for lo, hi, n, wins in self.bins:
            if lo <= p < hi or (hi >= 1.0 and p == 1.0):
                return n, wins
        return None


@dataclass(frozen=True)
class FairProbability:
    p: float | None
    low: float | None
    high: float | None
    calibrated: bool
    basis: str
    n_evidence: int | None = None
    flags: tuple = ()


def fit_bins(preds, outcomes, edges):
    """Reliability counts from held-out (prediction, 0/1 outcome) pairs for the given bin edges."""
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        idx = [i for i, p in enumerate(preds) if lo <= p < hi or (hi >= 1.0 and p == 1.0)]
        out.append((lo, hi, len(idx), int(sum(outcomes[i] for i in idx))))
    return tuple(out)


def fair_probability(p_model, evidence: CalibrationEvidence | None = None, *, declared: tuple | None = None,
                     prior_strength=DEFAULT_PRIOR_STRENGTH, z=Z_ONE_SIDED_90) -> FairProbability:
    if declared is not None:
        lo, hi = num(declared[0]), num(declared[1])
        if lo is None or hi is None or not 0 <= lo <= hi <= 1:
            return FairProbability(None, None, None, False, "DECLARED_INVALID", flags=("INVALID_DECLARED_RANGE",))
        return FairProbability((lo + hi) / 2, lo, hi, False, "ANALYST_DECLARED_UNCALIBRATED", flags=("UNCALIBRATED",))
    pm = num(p_model)
    if pm is None or not 0.0 <= pm <= 1.0:
        return FairProbability(None, None, None, False, "NO_MODEL_PROBABILITY", flags=("MISSING_MODEL_PROBABILITY",))
    if evidence is None:
        return FairProbability(None, None, None, False, "NO_CALIBRATION_EVIDENCE", flags=("MISSING_CALIBRATION",))
    cell = evidence.cell(pm)
    if cell is None or cell[0] < evidence.min_n:
        return FairProbability(None, None, None, False, "CALIBRATION_CELL_TOO_THIN",
                               n_evidence=None if cell is None else cell[0], flags=("CALIBRATION_CELL_TOO_THIN",))
    n, wins = cell
    a = wins + prior_strength * pm
    b = (n - wins) + prior_strength * (1 - pm)
    mean = a / (a + b)
    sd = math.sqrt(a * b / ((a + b) ** 2 * (a + b + 1)))
    return FairProbability(mean, max(0.0, mean - z * sd), min(1.0, mean + z * sd), True,
                           f"HELDOUT_CALIBRATION:{evidence.source}", n_evidence=n)


def edge_summary(price, contracts, fee_fn, fair: FairProbability) -> dict:
    be = break_even_per_contract(price, contracts, fee_fn)
    if be is None:
        return {"break_even": None, "edge_point": None, "edge_low": None, "clears_conservatively": None, "flags": ["MISSING_FEE_OR_PRICE"]}
    if fair.low is None:
        return {"break_even": be, "edge_point": None, "edge_low": None, "clears_conservatively": None, "flags": list(fair.flags) or ["NO_FAIR_PROBABILITY"]}
    return {"break_even": be, "edge_point": fair.p - be, "edge_low": fair.low - be,
            "clears_conservatively": fair.low - be > MIN_CONSERVATIVE_MARGIN, "flags": []}


def bet_up_to(fair: FairProbability, budget_dollars, fee_fn, *, min_margin=MIN_CONSERVATIVE_MARGIN) -> dict:
    """Highest whole-cent price whose fee-inclusive break-even at the budget's order size is <= fair.low - min_margin."""
    if fair.low is None:
        return {"bet_up_to_cents": None, "basis": fair.basis, "flags": list(fair.flags) or ["NO_FAIR_PROBABILITY"]}
    best = None
    for cents in range(1, 100):
        price = cents / 100
        c = contracts_for_budget(price, budget_dollars, fee_fn)
        if c is None:
            continue
        be = break_even_per_contract(price, c, fee_fn)
        if be is not None and fair.low - be >= min_margin:
            best = (cents, be, c)
    if best is None:
        return {"bet_up_to_cents": None, "basis": fair.basis, "flags": ["NO_PRICE_CLEARS_CONSERVATIVE_FAIR"]}
    return {"bet_up_to_cents": best[0], "break_even_at_limit": best[1], "contracts_at_limit": best[2],
            "basis": fair.basis, "calibrated": fair.calibrated, "flags": [] if fair.calibrated else ["UNCALIBRATED_FAIR"]}
