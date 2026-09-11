"""Kalshi fee model, kept SEPARATE from model probabilities.

Verified inputs (series metadata, 2026-09-11 discovery):
  * every tennis series has fee_multiplier = 1;
  * fee_type = "quadratic_with_maker_fees" on KXATPMATCH, KXWTAMATCH and the Grand Slam singles winner
    series (KXAOMENSINGLES, KXFOMEN(SINGLES), KXFOWOMEN(SINGLES), KXUSOMENSINGLES, KXUSOWOMENSINGLES,
    KXWMENSINGLES, KXWWOMENSINGLES); "quadratic" (taker-only) on the other 132 tennis series.
Formula (Kalshi fee schedule effective 2026-07-07, per the exchange's published schedule; the taker
coefficient 0.07 and maker coefficient 0.0175 = 25% of taker are DOCUMENTED, not byte-verified from
this sandbox, which cannot reach kalshi.com -- see docs/KNOWN_LIMITATIONS.md):
    taker fee = ceil_to_cent( 0.07 * M * C * P * (1 - P) )
    maker fee = ceil_to_cent( 0.0175 * M * C * P * (1 - P) )   only on maker-fee series, else 0
where C = contracts, P = price in dollars, M = fee_multiplier. No settlement fee.

Expected value helpers return RAW edge and FEE-ADJUSTED EV separately.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

TAKER_COEF = 0.07
MAKER_COEF = 0.0175


@dataclass(frozen=True)
class FeeSchedule:
    fee_type: str = "quadratic"
    fee_multiplier: float = 1.0
    verified_at: str = "2026-09-11"
    source: str = "GET /series/{ticker} (fee_type, fee_multiplier) + published schedule coefficients"

    @property
    def maker_applies(self) -> bool:
        return self.fee_type == "quadratic_with_maker_fees"


def _ceil_cent(x: float) -> float:
    return math.ceil(round(x * 100, 9)) / 100.0


def taker_fee(price: float, contracts: float, sched: FeeSchedule = FeeSchedule()) -> float:
    return _ceil_cent(TAKER_COEF * sched.fee_multiplier * contracts * price * (1 - price))


def maker_fee(price: float, contracts: float, sched: FeeSchedule = FeeSchedule()) -> float:
    if not sched.maker_applies:
        return 0.0
    return _ceil_cent(MAKER_COEF * sched.fee_multiplier * contracts * price * (1 - price))


@dataclass(frozen=True)
class EV:
    side: str                     # "YES" or "NO"
    price: float                  # executable price paid per contract for that side
    fair: float                   # model probability the side pays $1
    raw_edge: float               # fair - price
    fee_per_contract: float
    ev_per_contract_after_fees: float   # fair - price - fee


def expected_value(fair_yes: float, yes_ask: float | None, no_ask: float | None, contracts: float = 1.0,
                   sched: FeeSchedule = FeeSchedule(), role: str = "taker") -> list[EV]:
    """EV of buying YES at yes_ask and of buying NO at no_ask, per contract, fees separated."""
    out = []
    fee_fn = taker_fee if role == "taker" else maker_fee
    if yes_ask is not None and 0 < yes_ask < 1:
        f = fee_fn(yes_ask, contracts, sched) / contracts
        out.append(EV("YES", yes_ask, fair_yes, fair_yes - yes_ask, f, fair_yes - yes_ask - f))
    if no_ask is not None and 0 < no_ask < 1:
        f = fee_fn(no_ask, contracts, sched) / contracts
        out.append(EV("NO", no_ask, 1 - fair_yes, (1 - fair_yes) - no_ask, f, (1 - fair_yes) - no_ask - f))
    return out


def breakeven_price(fair: float, sched: FeeSchedule = FeeSchedule(), role: str = "taker", contracts: float = 100.0) -> float:
    """Highest price at which buying the side with win-probability `fair` still has non-negative EV after fees.
    ("BET UP TO" in the owner-facing output.) Solved by bisection on price."""
    lo, hi = 0.01, 0.99
    coef = TAKER_COEF if role == "taker" else (MAKER_COEF if sched.maker_applies else 0.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        fee = coef * sched.fee_multiplier * mid * (1 - mid)
        if fair - mid - fee >= 0:
            lo = mid
        else:
            hi = mid
    return math.floor(lo * 100) / 100.0
