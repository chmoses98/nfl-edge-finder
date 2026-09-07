"""Kalshi fee semantics, traceable to captured metadata and to a versioned fee-schedule config.

Two independent facts decide what a trade costs, and this module keeps them apart because they come from
different places and carry different confidence:

  WHICH REGIME APPLIES   `config/kalshi_nfl_series.json`, captured from the live Kalshi API. It records each
                         series' `fee_type` and `fee_multiplier` exactly as the API reports them. Across 392
                         NFL series there are two regimes:

                             quadratic                   367 series   taker fee only
                             quadratic_with_maker_fees    25 series   taker fee AND a maker fee

                         That distinction is not cosmetic: the 25 maker-fee series include every headline NFL
                         market (KXNFLGAME, KXNFLSPREAD, KXNFLTOTAL, KXNFLANYTD, KXNFLFIRSTTD, KXNFL2TD), so a
                         passive strategy on the markets this project actually studies does not get free entry.

  WHAT THE REGIME COSTS  `config/kalshi_fee_schedule.json`, transcribed from Kalshi's published fee schedule
                         with provenance and a `verified_at`. Coefficients are config, not literals in code,
                         so a platform fee change is a reviewable commit rather than an edit to a formula.

Kalshi's published formulas:

    taker  fee = round_up(0.07   * M * C * P * (1 - P))
    maker  fee = round_up(0.0175 * M * C * P * (1 - P))

where C is contracts IN THE ORDER, P is the price in dollars, M is the series fee multiplier, and `round_up`
rounds the ORDER's fee up to the cent -- once, not per contract. Rounding per contract would overstate the
cost of every multi-contract order; for a 100-lot at 50c it is the difference between $1.75 and $1.00.

THE UNKNOWN, AND WHY IT IS LOUD
-------------------------------
The maker multiplier is NOT exposed by the API -- series metadata carries `fee_type` but no maker coefficient
-- and the published schedule says the multiplier defaults to 0 "unless otherwise indicated" without saying
what the indicated value is for these series. So for the 25 maker-fee NFL series the maker cost is genuinely
unknown.

It is therefore modelled as UNKNOWN and not as a number. `maker_fee()` returns a FeeQuote whose state is
UNKNOWN with `amount=None`, and `net_executable_ev()` refuses to produce a net EV from an unknown cost. The
alternative -- a small plausible default -- is the specific failure this module exists to prevent: a hidden
default that is too low manufactures profitable passive trades that do not exist. Research that wants a
number sweeps `MAKER_MULTIPLIER_SWEEP` and reports every value.

The taker path IS known, and the taker path is the one that matters: passive execution was rejected on core
game markets under H-019, so a real recommendation is a taker order.

PRICE CONVENTION
----------------
Prices here are probabilities in [0, 1] -- the same units the user sees on Kalshi (cents/100). Fees are
returned in dollars. Nothing in this module folds a fee into a price: `bet_up_to_probability` stays a price
the user can read off the ticket, and fee-aware economics live in `net_executable_ev()` beside it, never
merged into it. See docs/OPERATIONS.md for the full vocabulary.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

# ---- fee state -------------------------------------------------------------------------------------
KNOWN = "KNOWN"
UNKNOWN = "UNKNOWN"          # a required coefficient is not available; no number may be invented
DEGRADED = "DEGRADED"        # the series is not in the captured registry, so the regime itself is a guess

TAKER = "taker"
MAKER = "maker"

# Research-only sweep for the unknown maker multiplier. Never a default: a sweep reports a range, a default
# pretends to a number.
MAKER_MULTIPLIER_SWEEP = (0.0, 0.25, 0.5, 1.0)

# FROZEN. The per-contract dollar sweep the H-019 passive-execution study ran with. It is kept verbatim so
# `scripts/research/passive_backtest.py` reproduces its published numbers exactly; the conclusion it reached
# -- passive execution rejected on core game markets -- is not reopened by this module's re-derivation of the
# fee formula. New work uses MAKER_MULTIPLIER_SWEEP, which sweeps the actual published parameter.
MAKER_FEE_SWEEP = (0.0, 0.0025, 0.005, 0.01)

FEE_TYPE_TAKER_ONLY = "quadratic"
FEE_TYPE_WITH_MAKER = "quadratic_with_maker_fees"


class FeeStateError(RuntimeError):
    """Raised when a caller demands a number the fee schedule cannot honestly supply."""


@dataclass(frozen=True)
class FeeQuote:
    """A fee, or an explicit refusal to state one.

    `amount is None` and `state != KNOWN` always travel together: there is no way to read a number off this
    object without also seeing that it is not known.
    """
    amount: float | None
    state: str
    basis: str                       # human-readable derivation, for the ledger
    side: str = TAKER                # taker / maker
    series_ticker: str | None = None
    contracts: float | None = None
    price: float | None = None
    reason: str | None = None        # why UNKNOWN/DEGRADED, when it is

    @property
    def is_known(self) -> bool:
        return self.state == KNOWN and self.amount is not None

    def require(self) -> float:
        if not self.is_known:
            raise FeeStateError(f"fee is {self.state}: {self.reason or self.basis}")
        return float(self.amount)

    def to_dict(self) -> dict:
        return {"amount": self.amount, "state": self.state, "basis": self.basis, "side": self.side,
                "series_ticker": self.series_ticker, "contracts": self.contracts, "price": self.price,
                "reason": self.reason}


def _round_up_cents(value: float, increment: float = 0.01) -> float:
    """Round a whole-order fee UP to the next increment.

    Applied once per order. Floating point is nudged by a relative epsilon first, so a value that sits
    exactly on an increment boundary but arrived there through binary arithmetic is not pushed up a whole
    cent by representation error alone.
    """
    if value <= 0:
        return 0.0
    steps = value / increment
    if abs(steps - round(steps)) < 1e-9:
        steps = round(steps)
    return math.ceil(steps) * increment


@dataclass
class FeeSchedule:
    """Everything needed to price a fill, with each input's confidence attached."""
    fee_type_by_series: dict = field(default_factory=dict)
    fee_multiplier_by_series: dict = field(default_factory=dict)
    taker_coefficient: float = 0.07
    maker_coefficient: float = 0.0175
    maker_multiplier: float | None = None        # None == UNKNOWN. Never silently defaulted.
    rounding_increment: float = 0.01
    settlement_fee_per_contract: float = 0.0
    schedule_id: str = "unversioned"
    provenance: dict = field(default_factory=dict)

    # ---- regime lookup ------------------------------------------------------------------------------
    def fee_type(self, series_ticker: str) -> str | None:
        return self.fee_type_by_series.get(series_ticker)

    def fee_multiplier(self, series_ticker: str) -> float | None:
        m = self.fee_multiplier_by_series.get(series_ticker)
        try:
            return None if m is None else float(m)
        except (TypeError, ValueError):
            return None

    def charges_maker_fee(self, series_ticker: str) -> bool:
        return self.fee_type(series_ticker) == FEE_TYPE_WITH_MAKER

    def knows_series(self, series_ticker: str) -> bool:
        return series_ticker in self.fee_type_by_series

    # ---- fees ---------------------------------------------------------------------------------------
    def taker_fee(self, price: float, contracts: float = 1.0, series_ticker: str | None = None) -> FeeQuote:
        """round_up_to_cent(coefficient * multiplier * contracts * price * (1 - price)), per ORDER.

        Fractional `contracts` is supported and is never truncated. Kalshi order quantities are integers
        today, but a weighted-average or partially-allocated position is a genuinely fractional quantity in
        this ledger's own accounting, and rounding it would misstate the cost.
        """
        bad = _price_problem(price, contracts)
        if bad:
            return FeeQuote(None, UNKNOWN, "taker quadratic", TAKER, series_ticker, contracts, price,
                            reason=bad)
        mult, state, reason = self._multiplier_for(series_ticker)
        if state != KNOWN:
            return FeeQuote(None, state, "taker quadratic", TAKER, series_ticker, contracts, price,
                            reason=reason)
        raw = self.taker_coefficient * mult * float(contracts) * float(price) * (1.0 - float(price))
        amount = _round_up_cents(raw, self.rounding_increment)
        basis = (f"ceil({self.taker_coefficient} * M={mult} * C={contracts} * P={price} * "
                 f"{1 - float(price):.4f}) to {self.rounding_increment:.2f}, per order")
        return FeeQuote(round(amount, 4), KNOWN, basis, TAKER, series_ticker, contracts, price)

    def maker_fee(self, price: float, contracts: float = 1.0, series_ticker: str | None = None,
                  maker_multiplier: float | None = None) -> FeeQuote:
        """The maker fee, or an explicit UNKNOWN. Never a plausible-looking guess.

        Pass `maker_multiplier` to price a specific hypothesis -- that is what MAKER_MULTIPLIER_SWEEP is for.
        The result still names the multiplier in its basis, so a swept number can never later be mistaken
        for a measured one.
        """
        bad = _price_problem(price, contracts)
        if bad:
            return FeeQuote(None, UNKNOWN, "maker quadratic", MAKER, series_ticker, contracts, price,
                            reason=bad)
        if series_ticker is not None and not self.knows_series(series_ticker):
            return FeeQuote(None, DEGRADED, "maker quadratic", MAKER, series_ticker, contracts, price,
                            reason=f"series {series_ticker!r} is not in the captured fee registry, so its "
                                   "fee regime is unknown")
        if series_ticker is not None and not self.charges_maker_fee(series_ticker):
            return FeeQuote(0.0, KNOWN, f"fee_type {self.fee_type(series_ticker)!r}: no maker fee",
                            MAKER, series_ticker, contracts, price)
        m = self.maker_multiplier if maker_multiplier is None else maker_multiplier
        if m is None:
            return FeeQuote(
                None, UNKNOWN, "maker quadratic", MAKER, series_ticker, contracts, price,
                reason="the maker multiplier is not published in Kalshi series metadata and is null in "
                       "config/kalshi_fee_schedule.json; sweep MAKER_MULTIPLIER_SWEEP rather than assuming "
                       "a value")
        raw = self.maker_coefficient * float(m) * float(contracts) * float(price) * (1.0 - float(price))
        amount = _round_up_cents(raw, self.rounding_increment)
        basis = (f"ceil({self.maker_coefficient} * M={m} * C={contracts} * P={price} * "
                 f"{1 - float(price):.4f}) to {self.rounding_increment:.2f}, per order "
                 "[M is a HYPOTHESIS, not measured]")
        return FeeQuote(round(amount, 4), KNOWN, basis, MAKER, series_ticker, contracts, price)

    def entry_fee(self, price: float, contracts: float, series_ticker: str | None,
                  execution_style: str = TAKER, maker_multiplier: float | None = None) -> FeeQuote:
        if execution_style == MAKER:
            return self.maker_fee(price, contracts, series_ticker, maker_multiplier)
        return self.taker_fee(price, contracts, series_ticker)

    def _multiplier_for(self, series_ticker: str | None) -> tuple[float, str, str | None]:
        if series_ticker is None:
            return 1.0, KNOWN, None
        if not self.knows_series(series_ticker):
            return 0.0, DEGRADED, (f"series {series_ticker!r} is not in the captured fee registry "
                                   "(config/kalshi_nfl_series.json); its fee multiplier is unknown")
        m = self.fee_multiplier(series_ticker)
        if m is None:
            return 0.0, UNKNOWN, (f"series {series_ticker!r} is in the registry but reports no "
                                  "fee_multiplier")
        return m, KNOWN, None

    def describe(self, series_ticker: str) -> str:
        t = self.fee_type(series_ticker)
        if t is None:
            return f"{series_ticker}: fee regime UNKNOWN -- not in the captured registry"
        m = self.fee_multiplier(series_ticker)
        if t == FEE_TYPE_TAKER_ONLY:
            return f"{series_ticker}: taker quadratic (multiplier {m}), NO maker fee"
        return (f"{series_ticker}: taker quadratic (multiplier {m}) AND a maker fee whose multiplier is "
                f"{'UNKNOWN' if self.maker_multiplier is None else self.maker_multiplier}")


def _price_problem(price, contracts) -> str | None:
    if price is None:
        return "price is None"
    try:
        p = float(price)
    except (TypeError, ValueError):
        return f"price {price!r} is not numeric"
    if not (0.0 < p < 1.0):
        return f"price {p} is outside (0,1); a fee is only defined for a tradable price"
    if contracts is None:
        return "contracts is None"
    try:
        c = float(contracts)
    except (TypeError, ValueError):
        return f"contracts {contracts!r} is not numeric"
    if c < 0:
        return f"contracts {c} is negative"
    return None


# ---- loading ---------------------------------------------------------------------------------------

def load_fee_schedule(root: str, maker_multiplier: float | None = None) -> FeeSchedule:
    """Build a schedule from the captured series registry plus the versioned fee-schedule config.

    `maker_multiplier` is an explicit research override. It exists so a study can say "assume M=0.5" out
    loud; it is never read from an environment variable and never inferred from a fee_type.
    """
    reg_path = os.path.join(root, "config", "kalshi_nfl_series.json")
    with open(reg_path) as f:
        d = json.load(f)
    recs = d.get("series", d)
    items = recs.items() if isinstance(recs, dict) else [(r.get("ticker"), r) for r in recs]
    by_type, by_mult = {}, {}
    for k, v in items:
        if not isinstance(v, dict):
            continue
        by_type[k] = v.get("fee_type")
        by_mult[k] = v.get("fee_multiplier")

    fs = FeeSchedule(fee_type_by_series=by_type, fee_multiplier_by_series=by_mult)

    sched_path = os.path.join(root, "config", "kalshi_fee_schedule.json")
    if os.path.exists(sched_path):
        with open(sched_path) as f:
            sched = json.load(f)
        taker, maker = sched.get("taker") or {}, sched.get("maker") or {}
        settle = sched.get("settlement") or {}
        fs.schedule_id = sched.get("schedule_id", fs.schedule_id)
        fs.provenance = sched.get("provenance") or {}
        if taker.get("base_coefficient") is not None:
            fs.taker_coefficient = float(taker["base_coefficient"])
        if taker.get("rounding_increment") is not None:
            fs.rounding_increment = float(taker["rounding_increment"])
        if maker.get("base_coefficient") is not None:
            fs.maker_coefficient = float(maker["base_coefficient"])
        # May legitimately be null. A null here IS the UNKNOWN state, and that is the point of the file.
        fs.maker_multiplier = maker.get("maker_multiplier")
        if settle.get("value") is not None:
            fs.settlement_fee_per_contract = float(settle["value"])
    if maker_multiplier is not None:
        fs.maker_multiplier = float(maker_multiplier)
    return fs


# ---- net executable economics ----------------------------------------------------------------------

@dataclass
class NetEV:
    """Gross edge, costs, and what is left -- each nameable on its own.

    `gross_edge` is fair probability minus the price actually payable, in probability units: the number a
    handicapper reasons in. `net_ev_dollars` is what the position is worth after transaction costs. They are
    reported side by side and never merged, so nothing here turns a displayed price into a fee-loaded
    probability.
    """
    fair_probability: float
    executable_price: float
    contracts: float
    stake_dollars: float
    gross_edge: float | None            # probability units
    gross_ev_dollars: float | None
    estimated_fees: float | None
    fee_state: str
    fee_basis: str
    estimated_slippage_dollars: float
    net_ev_dollars: float | None
    net_edge: float | None              # probability units, cost-adjusted
    state: str                          # KNOWN / UNKNOWN / DEGRADED -- mirrors the weakest input
    reason: str | None = None

    @property
    def is_known(self) -> bool:
        return self.state == KNOWN and self.net_ev_dollars is not None

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def net_executable_ev(fair_probability: float, executable_price: float, contracts: float,
                      schedule: FeeSchedule, series_ticker: str | None = None,
                      execution_style: str = TAKER, slippage_dollars: float = 0.0,
                      maker_multiplier: float | None = None) -> NetEV:
    """What the trade is actually worth after what it actually costs.

    A Kalshi contract pays $1. Buying `contracts` at `executable_price` costs `contracts * price` and is
    worth `contracts * fair_probability` under the handicapper's own distribution, so the gross expectation
    is `contracts * (fair - price)`. Entry fees and any stated slippage come off that.

    If the fee is not KNOWN this returns state=UNKNOWN with `net_ev_dollars=None`. It does NOT fall back to
    a zero fee. A caller that gates on net EV therefore fails closed on an unknown cost, which is the whole
    reason the fee state is carried rather than collapsed into a number.
    """
    fee = schedule.entry_fee(executable_price, contracts, series_ticker, execution_style, maker_multiplier)
    try:
        stake = round(float(contracts) * float(executable_price), 6)
    except (TypeError, ValueError):
        stake = 0.0
    gross_edge = gross_ev = None
    if fair_probability is not None and executable_price is not None:
        gross_edge = round(float(fair_probability) - float(executable_price), 6)
        gross_ev = round(float(contracts) * gross_edge, 6)

    if not fee.is_known or gross_ev is None:
        return NetEV(
            fair_probability=fair_probability, executable_price=executable_price, contracts=contracts,
            stake_dollars=stake, gross_edge=gross_edge, gross_ev_dollars=gross_ev,
            estimated_fees=None, fee_state=fee.state, fee_basis=fee.basis,
            estimated_slippage_dollars=float(slippage_dollars), net_ev_dollars=None, net_edge=None,
            state=fee.state if not fee.is_known else UNKNOWN,
            reason=fee.reason or "gross EV is undefined without a fair probability and an executable price")

    net = round(gross_ev - fee.amount - float(slippage_dollars), 6)
    net_edge = None if not contracts else round(net / float(contracts), 6)
    return NetEV(
        fair_probability=fair_probability, executable_price=executable_price, contracts=contracts,
        stake_dollars=stake, gross_edge=gross_edge, gross_ev_dollars=gross_ev,
        estimated_fees=fee.amount, fee_state=KNOWN, fee_basis=fee.basis,
        estimated_slippage_dollars=float(slippage_dollars), net_ev_dollars=net, net_edge=net_edge,
        state=KNOWN)


def contracts_for_stake(stake_dollars: float, price: float) -> float:
    """Contracts a dollar stake buys at a price. Fractional by design -- see `taker_fee`."""
    if not price or float(price) <= 0:
        return 0.0
    return float(stake_dollars) / float(price)
