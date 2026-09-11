"""Canonical close and CLV for pre-match markets.

CANONICAL_CLOSE = last valid EXECUTABLE quote strictly before the match's first ball.
  * executable: both yes_bid and yes_ask present, 0 < bid <= ask < 1, and the observation is a real quote
    (a captured market record or an orderbook top), never a trade print and never a settlement value.
  * strictly before first ball: prefer actual_first_ball_at (SportsTruth). When it is unknown, the
    conservative fallback is scheduled_start - safety_margin (default 5 min) with close_basis =
    "SCHEDULED_MINUS_MARGIN", and strict evaluations exclude such rows (fail closed, TENNIS-6/10).
  * never synthesised: if no executable quote exists before the cutoff, there is no close (close=None).

CLV definitions (all from the perspective of buying YES at the prediction-time price):
  midpoint CLV      = close_mid - decision_price
  executable CLV    = close_bid_yes - decision_ask_yes   (what a taker who bought YES could sell back for
                      at the close, minus what they paid; conservative, spread-inclusive)
  raw prob movement = close_mid - decision_mid
Fees are NOT included here; see tennis_edge.pricing.fees.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

SAFETY_MARGIN = timedelta(minutes=5)


@dataclass(frozen=True)
class Quote:
    ts: datetime
    yes_bid: float | None
    yes_ask: float | None
    yes_bid_size: float | None = None
    yes_ask_size: float | None = None
    source: str = "market_record"    # market_record | orderbook | candle_bidask

    @property
    def executable(self) -> bool:
        return (self.yes_bid is not None and self.yes_ask is not None and 0.0 < self.yes_bid <= self.yes_ask < 1.0
                and self.source in ("market_record", "orderbook", "candle_bidask"))

    @property
    def mid(self) -> float | None:
        return 0.5 * (self.yes_bid + self.yes_ask) if self.executable else None


@dataclass(frozen=True)
class CanonicalClose:
    quote: Quote | None
    cutoff: datetime
    close_basis: str            # ACTUAL_FIRST_BALL | SCHEDULED_MINUS_MARGIN | NONE
    seconds_to_cutoff: float | None
    n_quotes_considered: int


def canonical_close(quotes: list[Quote], scheduled_start: datetime | None, actual_first_ball: datetime | None,
                    margin: timedelta = SAFETY_MARGIN) -> CanonicalClose:
    if actual_first_ball is not None:
        cutoff, basis = actual_first_ball, "ACTUAL_FIRST_BALL"
    elif scheduled_start is not None:
        cutoff, basis = scheduled_start - margin, "SCHEDULED_MINUS_MARGIN"
    else:
        return CanonicalClose(None, datetime.max, "NONE", None, len(quotes))
    best = None
    for q in quotes:
        if q.ts < cutoff and q.executable and (best is None or q.ts > best.ts):
            best = q
    return CanonicalClose(best, cutoff, basis, (cutoff - best.ts).total_seconds() if best else None, len(quotes))


@dataclass(frozen=True)
class CLV:
    midpoint_clv: float | None
    executable_clv: float | None
    raw_prob_movement: float | None
    decision_mid: float | None
    close_mid: float | None


def clv(decision: Quote, close: CanonicalClose) -> CLV:
    """CLV for a hypothetical YES purchase at the decision-time ask."""
    if close.quote is None or not decision.executable:
        return CLV(None, None, None, decision.mid, None)
    cq = close.quote
    return CLV(midpoint_clv=cq.mid - decision.yes_ask, executable_clv=cq.yes_bid - decision.yes_ask,
               raw_prob_movement=cq.mid - decision.mid, decision_mid=decision.mid, close_mid=cq.mid)
