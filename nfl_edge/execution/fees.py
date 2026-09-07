"""Kalshi fee semantics: the 2026 fixed-point rounding model, priced from the schedule in force.

THREE THINGS THAT ARE OFTEN COLLAPSED INTO ONE, AND MUST NOT BE
---------------------------------------------------------------
Kalshi charges a fill in three separately-named parts, and the total is not `ceil(raw, $0.01)`:

    RAW QUADRATIC FEE   coefficient * multiplier * contracts * price * (1 - price)
    TRADE FEE           the raw fee ceiled to a CENTICENT ($0.0001)
    ROUNDING FEE        cent-alignment: the resulting balance change is floored to the account's balance
                        precision, and the shortfall is charged
    REBATE              the rounding overpayment accumulates PER ORDER across all of its fills; once the
                        accumulator exceeds a cent, a whole-cent rebate is issued and the accumulator drops
                        by a cent

    NET FEE = TRADE FEE + ROUNDING FEE - REBATE          (never below zero)

The accumulator is the part that matters economically: it is what makes twenty small fills cost the same as
one equivalent large fill. A model that ceils every fill to the next cent independently overstates a
twenty-fill order by up to twenty cents, and a model that ceils the whole order to the next cent understates
the rounding on a fragmented one. Both are wrong in ways that change whether a marginal trade is worth doing.

Worked example from Kalshi's fee-rounding documentation, reproduced by `fee_for_fill` and pinned in
tests/test_fees.py:

    fill 1   revenue -$0.0550, trade fee $0.0085  ->  balance -$0.0635 floored to -$0.0700
             rounding fee $0.0065, accumulator $0.0065, no rebate, net fee $0.0150
    fill 2   same again                            ->  accumulator $0.0130 > $0.01
             rebate $0.0100, accumulator $0.0030, net fee $0.0050

PRE-TRADE VS POST-TRADE
-----------------------
`estimate_order_fee` gives the economically equivalent WHOLE-ORDER cost, which is what a decision needs: the
accumulator converges fragmented fills onto it. `fee_for_fill` reproduces the exchange's per-fill mechanics
and is what a replay or a reconciliation needs.

Neither is authoritative after the fact. Once a trade exists, the exchange's own reported fee is the truth
and `Execution.fees_paid` carries it; these functions are estimates and are labelled as such everywhere they
are recorded.

WHICH MULTIPLIER, AND FROM WHERE
--------------------------------
Two multipliers exist per series, and only one of them is in the API:

    REGULATORY_FEE_SCHEDULE   the CFTC-filed Fee Schedule. Lists BOTH a Maker Multiplier and a Taker
                              Multiplier for each listed non-standard series. Rank 1.
    SERIES_METADATA           GET /series/{ticker}. `fee_multiplier` is the TAKER multiplier; the object
                              carries no maker parameter at all. Rank 2.
    FEE_CHANGES               GET /series/fee_changes. Builds the NEXT window, never overrides the current
                              one. Rank 3.

That the API object is silent about the maker multiplier is NOT evidence that the maker multiplier is
unknown. A value published in the regulatory schedule is a known value. What is genuinely unverified is a
series that charges a maker fee (`fee_type == quadratic_with_maker_fees`) and is not listed in any schedule
window we hold -- for those, and only those, the maker cost is UNVERIFIED and fails closed.

Where two sources disagree for the same window, the state is CONFLICTED and fails closed. A conflict is
reported, never resolved by silently preferring the higher-ranked source.

TIME
----
Fee parameters are versioned by effective window and looked up `as_of` the DECISION timestamp. A
recommendation made at 13:00 is priced with the schedule in force at 13:00, whatever the importer sees when
it runs twelve hours later.

PRICE CONVENTION
----------------
Prices are probabilities in [0, 1] -- the units on the Kalshi ticket. Fees are dollars. Nothing here folds a
fee into a price: `bet_up_to_probability` stays readable off the ticket, and cost economics live in
`net_executable_ev()` beside it.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal

# ---- fee state -------------------------------------------------------------------------------------
KNOWN = "KNOWN"
UNVERIFIED = "UNVERIFIED"      # the series charges this fee but no schedule window we hold names its rate
CONFLICTED = "CONFLICTED"      # two sources disagree for the same window; never resolved by rank
DEGRADED = "DEGRADED"          # the series is not in the captured registry, so the regime itself is a guess
# Retained name for callers that check "not known"; UNKNOWN is the union of the three non-KNOWN states.
UNKNOWN = "UNKNOWN"
NOT_KNOWN_STATES = (UNVERIFIED, CONFLICTED, DEGRADED, UNKNOWN)

TAKER = "taker"
MAKER = "maker"

SRC_REGULATORY = "REGULATORY_FEE_SCHEDULE"
SRC_SERIES_METADATA = "SERIES_METADATA"
SRC_FEE_CHANGES = "FEE_CHANGES"
SOURCE_RANK = {SRC_REGULATORY: 1, SRC_SERIES_METADATA: 2, SRC_FEE_CHANGES: 3}

FEE_TYPE_TAKER_ONLY = "quadratic"
FEE_TYPE_WITH_MAKER = "quadratic_with_maker_fees"

CENTICENT = Decimal("0.0001")
CENT = Decimal("0.01")

# Research-only sweep for a maker multiplier that is genuinely unverified. Never a default.
MAKER_MULTIPLIER_SWEEP = (0.0, 0.25, 0.5, 1.0)

# FROZEN. The per-contract dollar sweep the passive-execution study (research/passive, Milestone K) ran with.
# Kept verbatim so scripts/research/passive_backtest.py reproduces its published numbers exactly; the
# conclusion it reached -- passive execution rejected on core game markets -- is not reopened by this
# module's re-derivation of the fee mechanics.
MAKER_FEE_SWEEP = (0.0, 0.0025, 0.005, 0.01)


class FeeStateError(RuntimeError):
    """Raised when a caller demands a number the fee schedule cannot honestly supply."""


def _d(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def ceil_to(value, increment=CENTICENT) -> Decimal:
    """Round UP to the next increment. Exact: Decimal, not binary floating point."""
    v, inc = _d(value), _d(increment)
    if v <= 0:
        return Decimal("0")
    return (v / inc).quantize(Decimal("1"), rounding=ROUND_CEILING) * inc


def floor_to(value, increment=CENT) -> Decimal:
    """Round DOWN (toward negative infinity) to the increment. A debit floors to a LARGER debit."""
    v, inc = _d(value), _d(increment)
    return (v / inc).quantize(Decimal("1"), rounding=ROUND_FLOOR) * inc


def _iso(t):
    if not t:
        return None
    if isinstance(t, datetime):
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# ---- the per-fill mechanics ------------------------------------------------------------------------

@dataclass(frozen=True)
class FeeComponents:
    """One fill's fee, decomposed exactly as the exchange decomposes it."""
    raw_quadratic: float
    trade_fee: float               # raw, ceiled to a centicent
    rounding_fee: float            # cent-alignment on the balance change
    rebate: float                  # whole cent, when the accumulator crosses one
    net_fee: float                 # trade + rounding - rebate, floored at zero
    balance_change: float          # what the account actually moves by (negative for a buy)
    accumulator_after: float

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def fee_for_fill(price, contracts, coefficient, multiplier, *, accumulator=0.0,
                 balance_precision=CENT) -> FeeComponents:
    """The exchange's own per-fill arithmetic, in exact decimal.

    `accumulator` is the order's running rounding overpayment and must be carried from the previous fill --
    it is per ORDER, across all of its fills, taker and maker alike. Starting each fill from zero would model
    a different, more expensive exchange than the real one.
    """
    p, c = _d(price), _d(contracts)
    raw = _d(coefficient) * _d(multiplier) * c * p * (Decimal(1) - p)
    trade_fee = ceil_to(raw, CENTICENT)

    # A buy debits the position cost plus the fee. The account's balance moves in its own precision, and the
    # shortfall from flooring that debit is charged as the rounding fee.
    revenue = -(c * p)
    balance_raw = revenue - trade_fee
    balance = floor_to(balance_raw, balance_precision)
    rounding_fee = balance_raw - balance                       # >= 0

    acc = _d(accumulator) + rounding_fee
    rebate = Decimal("0")
    if acc > CENT:
        rebate = CENT
        acc -= CENT

    net = trade_fee + rounding_fee - rebate
    if net < 0:
        net = Decimal("0")

    return FeeComponents(
        raw_quadratic=float(raw), trade_fee=float(trade_fee), rounding_fee=float(rounding_fee),
        rebate=float(rebate), net_fee=float(net), balance_change=float(balance),
        accumulator_after=float(acc))


def fee_for_order(fills, coefficient, multiplier, *, balance_precision=CENT) -> dict:
    """Every fill of one order, carrying the accumulator between them.

    `fills` is [(price, contracts)]. Returns the per-fill components and the order totals -- which is the
    only level at which the rebate mechanism makes sense, since the accumulator is what ties the fills
    together.
    """
    acc = Decimal("0")
    out, totals = [], {"raw_quadratic": Decimal("0"), "trade_fee": Decimal("0"),
                       "rounding_fee": Decimal("0"), "rebate": Decimal("0"),
                       "net_fee": Decimal("0"), "contracts": Decimal("0"), "cost": Decimal("0")}
    for price, contracts in fills:
        comp = fee_for_fill(price, contracts, coefficient, multiplier,
                            accumulator=acc, balance_precision=balance_precision)
        acc = _d(comp.accumulator_after)
        out.append(comp)
        for k, v in (("raw_quadratic", comp.raw_quadratic), ("trade_fee", comp.trade_fee),
                     ("rounding_fee", comp.rounding_fee),
                     ("rebate", comp.rebate), ("net_fee", comp.net_fee)):
            totals[k] += _d(v)
        totals["contracts"] += _d(contracts)
        totals["cost"] += _d(contracts) * _d(price)
    return {"fills": out, "accumulator_final": float(acc),
            **{k: float(v) for k, v in totals.items()}}


# ---- the schedule ----------------------------------------------------------------------------------

@dataclass(frozen=True)
class Multipliers:
    """A series' two multipliers for one effective window, with why we believe each."""
    taker: float | None
    maker: float | None
    taker_state: str
    maker_state: str
    source: str | None
    effective_from: str | None
    verified_at: str | None
    reason: str | None = None

    def for_style(self, style: str) -> tuple[float | None, str]:
        return ((self.maker, self.maker_state) if style == MAKER else (self.taker, self.taker_state))

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass(frozen=True)
class FeeQuote:
    """A fee, or an explicit refusal to state one.

    `amount is None` and a non-KNOWN state always travel together: there is no way to read a number off this
    object without also seeing that it is not known.
    """
    amount: float | None
    state: str
    basis: str
    side: str = TAKER
    series_ticker: str | None = None
    contracts: float | None = None
    price: float | None = None
    components: dict | None = None
    multipliers: dict | None = None
    reason: str | None = None

    @property
    def is_known(self) -> bool:
        return self.state == KNOWN and self.amount is not None

    def require(self) -> float:
        if not self.is_known:
            raise FeeStateError(f"fee is {self.state}: {self.reason or self.basis}")
        return float(self.amount)

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class FeeSchedule:
    """Fee parameters for one point in time, plus the regime registry they are applied to."""
    fee_type_by_series: dict = field(default_factory=dict)
    metadata_multiplier_by_series: dict = field(default_factory=dict)   # TAKER, from GET /series
    windows: list = field(default_factory=list)                          # newest last
    schedule_set_id: str = "unversioned"
    source_hierarchy: list = field(default_factory=list)
    rounding: dict = field(default_factory=dict)
    conflict_policy: str = ""

    # ---- regime ------------------------------------------------------------------------------------
    def fee_type(self, series_ticker: str) -> str | None:
        return self.fee_type_by_series.get(series_ticker)

    def charges_maker_fee(self, series_ticker: str) -> bool:
        return self.fee_type(series_ticker) == FEE_TYPE_WITH_MAKER

    def knows_series(self, series_ticker: str) -> bool:
        return series_ticker in self.fee_type_by_series

    # ---- window lookup -----------------------------------------------------------------------------
    def window_for(self, as_of: datetime | None = None) -> dict | None:
        """The schedule window in force at `as_of`. Never "the newest one".

        `as_of=None` means "right now" and exists for DIAGNOSTICS -- `describe()`, an operator poking at the
        registry. It is not reachable from the pricing path: `entry_fee` raises rather than defaulting,
        because a silent wall-clock fallback there would price a 13:00 decision with whatever schedule
        happens to be in force when the importer runs twelve hours later.
        """
        t = _iso(as_of) or datetime.now(timezone.utc)
        best = None
        for w in self.windows:
            start, end = _iso(w.get("effective_from")), _iso(w.get("effective_to"))
            if start is not None and t < start:
                continue
            if end is not None and t >= end:
                continue
            if best is None or (_iso(w.get("effective_from")) or t) > (_iso(best.get("effective_from")) or t):
                best = w
        return best

    def coefficients(self, as_of: datetime | None = None) -> tuple[float, float]:
        w = self.window_for(as_of) or {}
        return (float(w.get("taker_base_coefficient", 0.07)),
                float(w.get("maker_base_coefficient", 0.0175)))

    def balance_precision(self, direct_member: bool = False) -> Decimal:
        r = self.rounding or {}
        key = "balance_precision_direct_member" if direct_member else "balance_precision_default"
        return _d(r.get(key, 0.01 if not direct_member else 0.0001))

    # ---- multipliers -------------------------------------------------------------------------------
    def multipliers_for(self, series_ticker: str | None,
                        as_of: datetime | None = None) -> Multipliers:
        """Reconcile the regulatory schedule against live series metadata, as of a point in time.

        Rank decides which source is CONSULTED first. It does not decide a disagreement: two sources that
        disagree about the same window produce CONFLICTED, because one of them is wrong and we do not know
        which.
        """
        w = self.window_for(as_of)
        eff = (w or {}).get("effective_from")
        ver = (w or {}).get("verified_at")

        if series_ticker is None:
            return Multipliers(1.0, None, KNOWN, UNVERIFIED, None, eff, ver,
                               "no series ticker supplied; taker treated as the standard multiplier")
        if not self.knows_series(series_ticker):
            return Multipliers(None, None, DEGRADED, DEGRADED, None, eff, ver,
                               f"series {series_ticker!r} is not in the captured registry "
                               "(config/kalshi_nfl_series.json); its fee regime is unknown")

        listed = ((w or {}).get("series") or {}).get(series_ticker)
        meta_taker = self.metadata_multiplier_by_series.get(series_ticker)
        try:
            meta_taker = None if meta_taker is None else float(meta_taker)
        except (TypeError, ValueError):
            meta_taker = None

        # --- taker ---
        if listed and listed.get("taker_multiplier") is not None:
            reg_taker = float(listed["taker_multiplier"])
            if meta_taker is not None and abs(meta_taker - reg_taker) > 1e-9:
                return Multipliers(
                    None, None, CONFLICTED, CONFLICTED, SRC_REGULATORY, eff, ver,
                    f"the regulatory schedule gives {series_ticker} a taker multiplier of {reg_taker} but "
                    f"live series metadata reports {meta_taker}. One of them is wrong and rank does not say "
                    "which, so the fee state is CONFLICTED and fails closed.")
            taker, taker_state, taker_src = reg_taker, KNOWN, SRC_REGULATORY
        elif meta_taker is not None:
            taker, taker_state, taker_src = meta_taker, KNOWN, SRC_SERIES_METADATA
        else:
            taker, taker_state, taker_src = None, UNVERIFIED, None

        # --- maker ---
        # The API object carries no maker parameter, so its silence proves nothing. Only two things can
        # establish a maker multiplier: the regulatory schedule listing it, or the series not charging one.
        if listed and listed.get("maker_multiplier") is not None:
            maker, maker_state, maker_src = float(listed["maker_multiplier"]), KNOWN, SRC_REGULATORY
        elif not self.charges_maker_fee(series_ticker):
            maker, maker_state, maker_src = 0.0, KNOWN, SRC_SERIES_METADATA
        else:
            maker, maker_state, maker_src = None, UNVERIFIED, None

        reason = None
        if maker_state == UNVERIFIED:
            reason = (f"{series_ticker} has fee_type {self.fee_type(series_ticker)!r} so it DOES charge a "
                      "maker fee, but no schedule window we hold lists its maker multiplier. Not assumed; "
                      "sweep MAKER_MULTIPLIER_SWEEP for research.")
        elif taker_state == UNVERIFIED:
            reason = f"{series_ticker} reports no taker multiplier in any source"

        return Multipliers(taker, maker, taker_state, maker_state,
                           maker_src or taker_src, eff, ver, reason)

    # ---- fees --------------------------------------------------------------------------------------
    def entry_fee(self, price, contracts, series_ticker, execution_style=TAKER, *,
                  as_of: datetime | None = None, maker_multiplier: float | None = None,
                  direct_member: bool = False, fills=None) -> FeeQuote:
        """The economically equivalent whole-order fee, or an explicit refusal.

        `fills` prices an order that is known to arrive in pieces; omit it and the order is priced as one
        fill, which is what the accumulator makes a fragmented order converge to anyway.

        `as_of` is REQUIRED and is the DECISION timestamp. There is no wall-clock default here on purpose:
        defaulting to now() would price a decision with a schedule that took effect after it was made, which
        is the same class of mistake as judging its price freshness at import time.
        """
        if as_of is None:
            raise FeeStateError(
                "entry_fee requires the DECISION timestamp as `as_of`. Fee parameters are versioned by "
                "effective window, and defaulting to wall clock would price a past decision with a schedule "
                "that may not have existed when it was made.")
        bad = _price_problem(price, contracts)
        if bad:
            return FeeQuote(None, UNVERIFIED, f"{execution_style} quadratic", execution_style,
                            series_ticker, contracts, price, reason=bad)

        m = self.multipliers_for(series_ticker, as_of)
        value, state = m.for_style(execution_style)
        if maker_multiplier is not None and execution_style == MAKER:
            value, state = float(maker_multiplier), KNOWN
        if state != KNOWN or value is None:
            return FeeQuote(None, state if state != KNOWN else UNVERIFIED,
                            f"{execution_style} quadratic", execution_style, series_ticker, contracts,
                            price, multipliers=m.to_dict(),
                            reason=m.reason or f"{execution_style} multiplier is {state}")

        taker_coef, maker_coef = self.coefficients(as_of)
        coef = maker_coef if execution_style == MAKER else taker_coef
        precision = self.balance_precision(direct_member)

        order = fee_for_order(fills or [(price, contracts)], coef, value, balance_precision=precision)
        hypothesis = " [multiplier is a HYPOTHESIS, not measured]" if maker_multiplier is not None else ""
        basis = (f"{execution_style}: ceil({coef} * M={value} * C={contracts} * P={price} * "
                 f"{1 - float(price):.4f}) to {CENTICENT}, then cent-alignment on a {precision} balance, "
                 f"accumulator across {len(order['fills'])} fill(s){hypothesis}")
        return FeeQuote(round(order["net_fee"], 6), KNOWN, basis, execution_style, series_ticker,
                        contracts, price, components=order, multipliers=m.to_dict())

    # backward-compatible single-style helpers
    def taker_fee(self, price, contracts=1.0, series_ticker=None, *, as_of=None, **kw) -> FeeQuote:
        return self.entry_fee(price, contracts, series_ticker, TAKER, as_of=as_of, **kw)

    def maker_fee(self, price, contracts=1.0, series_ticker=None, *, as_of=None,
                  maker_multiplier=None, **kw) -> FeeQuote:
        return self.entry_fee(price, contracts, series_ticker, MAKER, as_of=as_of,
                              maker_multiplier=maker_multiplier, **kw)

    def describe(self, series_ticker: str, as_of: datetime | None = None) -> str:
        t = self.fee_type(series_ticker)
        if t is None:
            return f"{series_ticker}: fee regime UNKNOWN -- not in the captured registry"
        m = self.multipliers_for(series_ticker, as_of)
        return (f"{series_ticker}: fee_type {t}, taker multiplier {m.taker} ({m.taker_state}), "
                f"maker multiplier {m.maker} ({m.maker_state}), source {m.source}, "
                f"effective {m.effective_from}")


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
    if c <= 0:
        return f"contracts {c} is not positive"
    return None


# ---- loading ---------------------------------------------------------------------------------------

def load_fee_schedule(root: str) -> FeeSchedule:
    """Build a schedule from the captured series registry plus the versioned, time-windowed config."""
    with open(os.path.join(root, "config", "kalshi_nfl_series.json")) as f:
        d = json.load(f)
    recs = d.get("series", d)
    items = recs.items() if isinstance(recs, dict) else [(r.get("ticker"), r) for r in recs]
    by_type, by_mult = {}, {}
    for k, v in items:
        if not isinstance(v, dict):
            continue
        by_type[k] = v.get("fee_type")
        by_mult[k] = v.get("fee_multiplier")      # TAKER multiplier; the object has no maker parameter

    fs = FeeSchedule(fee_type_by_series=by_type, metadata_multiplier_by_series=by_mult)

    path = os.path.join(root, "config", "kalshi_fee_schedule.json")
    if os.path.exists(path):
        with open(path) as f:
            sched = json.load(f)
        fs.schedule_set_id = sched.get("schedule_set_id", fs.schedule_set_id)
        fs.source_hierarchy = sched.get("source_hierarchy") or []
        fs.rounding = sched.get("rounding") or {}
        fs.conflict_policy = sched.get("conflict_policy", "")
        fs.windows = sorted(sched.get("schedules") or [],
                            key=lambda w: str(w.get("effective_from") or ""))
    return fs


# ---- net executable economics ----------------------------------------------------------------------

@dataclass
class NetEV:
    """Gross edge, costs, and what is left -- each nameable on its own.

    `gross_edge` is fair probability minus the price actually payable, in probability units: the number a
    handicapper reasons in, and the ONLY sense in which this project uses the word "edge". Model minus market
    is disagreement, never edge. `net_ev_dollars` is what the position is worth after transaction costs. They
    are reported side by side and never merged, so nothing here turns a displayed price into a fee-loaded
    probability.
    """
    fair_probability: float
    executable_price: float
    contracts: float
    stake_dollars: float
    gross_edge: float | None
    gross_ev_dollars: float | None
    estimated_fees: float | None
    fee_state: str
    fee_basis: str
    estimated_slippage_dollars: float
    net_ev_dollars: float | None
    net_edge: float | None
    state: str
    reason: str | None = None
    fee_components: dict | None = None

    @property
    def is_known(self) -> bool:
        return self.state == KNOWN and self.net_ev_dollars is not None

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def net_executable_ev(fair_probability, executable_price, contracts, schedule: FeeSchedule,
                      series_ticker=None, execution_style=TAKER, slippage_dollars=0.0,
                      maker_multiplier=None, *, as_of: datetime | None = None,
                      fills=None, direct_member: bool = False) -> NetEV:
    """What the trade is worth after what it actually costs.

    A Kalshi contract pays $1, so `contracts` bought at `executable_price` are worth
    `contracts * fair_probability` under the handicapper's own distribution and cost `contracts * price`.
    Entry fees and any stated slippage come off that.

    `as_of` is the DECISION timestamp: the fee schedule in force then, not the one current at import.

    A fee that is not KNOWN yields `net_ev_dollars=None` and a non-KNOWN state. It never falls back to zero.
    """
    fee = schedule.entry_fee(executable_price, contracts, series_ticker, execution_style,
                             as_of=as_of, maker_multiplier=maker_multiplier,
                             direct_member=direct_member, fills=fills)
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
            state=fee.state if not fee.is_known else UNVERIFIED,
            reason=fee.reason or "gross EV is undefined without a fair probability and an executable price")

    net = round(gross_ev - fee.amount - float(slippage_dollars), 6)
    return NetEV(
        fair_probability=fair_probability, executable_price=executable_price, contracts=contracts,
        stake_dollars=stake, gross_edge=gross_edge, gross_ev_dollars=gross_ev,
        estimated_fees=fee.amount, fee_state=KNOWN, fee_basis=fee.basis,
        estimated_slippage_dollars=float(slippage_dollars), net_ev_dollars=net,
        net_edge=None if not contracts else round(net / float(contracts), 6),
        state=KNOWN, fee_components=fee.components)


def contracts_for_stake(stake_dollars, price) -> float:
    """Contracts a dollar stake buys at a price. Fractional by design."""
    if not price or float(price) <= 0:
        return 0.0
    return float(stake_dollars) / float(price)
