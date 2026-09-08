"""Kalshi fee semantics: the 2026 fixed-point rounding model, priced from the schedule in force.

THREE THINGS THAT ARE OFTEN COLLAPSED INTO ONE, AND MUST NOT BE
---------------------------------------------------------------
Kalshi charges a fill in three separately-named parts, and the total is not `ceil(raw, $0.01)`:

    RAW QUADRATIC FEE   coefficient * multiplier * contracts * price * (1 - price)
    TRADE FEE           the raw fee rounded UP to a TRADE_FEE_INCREMENT ($0.000001)
    ROUNDING FEE        cent-alignment: the resulting balance change is floored to the account's balance
                        precision, and the shortfall is charged
    REBATE              the rounding overpayment accumulates PER ORDER across all of its fills; once the
                        accumulator exceeds one balance-precision unit a rebate of one unit is issued --
                        CAPPED so that fill's own net fee cannot go negative, with the unabsorbed remainder
                        left in the accumulator for a later fill to earn

    NET FEE = TRADE FEE + ROUNDING FEE - REBATE          (non-negative by construction, not by flooring)

Balance precision is $0.01 for an ordinary account and $0.0001 for a direct member.

The accumulator is the part that matters economically: it is what makes twenty small fills cost close to one
equivalent large fill. A model that ceils every fill to the next cent independently overstates a twenty-fill
order by up to twenty cents, and a model that ceils the whole order to the next cent understates the rounding
on a fragmented one. Both are wrong in ways that change whether a marginal trade is worth doing.

The CURRENT worked example from Kalshi's Fee Rounding documentation, reproduced exactly by `fee_for_fill`
and pinned in tests/test_fees.py -- one contract at $0.055 under the ordinary 0.07 taker coefficient:

    signed revenue    -$0.055000
    model fee          $0.00363825    = 0.07 x 1 x 0.055 x 0.945
    trade fee          $0.003639      = rounded UP to $0.000001
    aligned change    -$0.060000      = floored to a cent
    rounding fee       $0.001361
    trade + rounding   $0.005000

An older version of this docstring carried a different example for the same fill, with a trade fee of
$0.0085. That was a superseded fee regime, and it survived here for a while precisely because every number
in it was already aligned to four decimals -- so it reproduced perfectly against a rounding increment that
was wrong by two orders of magnitude. A test that cannot fail is not evidence.

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

import glob
import json
import math
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, InvalidOperation

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

# CURRENT venue rounding parameters. Named for the concepts, because the last time these were named after a
# guess ("CENTICENT") the wrong number survived three reviews inside a correct-looking word.
#
# Provenance: the operator's reading of the current Kalshi Fee Rounding documentation, 2026-09-08. This
# environment cannot reach docs.kalshi.com (network egress policy), so these values are OPERATOR-ATTESTED and
# are recorded as such in config/kalshi_fee_schedule.json. See docs/KNOWN_LIMITATIONS.md.
TRADE_FEE_INCREMENT = Decimal("0.000001")        # the trade fee rounds UP to six decimal dollars
NON_DIRECT_BALANCE_PRECISION = Decimal("0.01")   # ordinary accounts settle to the cent
DIRECT_BALANCE_PRECISION = Decimal("0.0001")     # direct members settle four decimals finer

CENT = NON_DIRECT_BALANCE_PRECISION              # the default balance precision, by its ordinary name

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


def ceil_to(value, increment=TRADE_FEE_INCREMENT) -> Decimal:
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
    trade_fee: float               # raw, ceiled UP to TRADE_FEE_INCREMENT ($0.000001)
    rounding_fee: float            # balance-precision alignment on the resulting balance change
    rebate: float                  # one balance-precision unit, CAPPED so net_fee cannot go negative
    net_fee: float                 # trade + rounding - rebate; >= 0 by construction, not by flooring
    balance_change: float          # what the account actually moves by (negative for a buy)
    accumulator_after: float
    rebate_capped: bool = False    # True when the fill could not absorb a whole rebate unit

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def fee_for_fill(price, contracts, coefficient, multiplier, *, accumulator=0.0,
                 balance_precision=CENT) -> FeeComponents:
    """The exchange's own per-fill arithmetic, in exact decimal.

    `accumulator` is the order's running rounding overpayment and must be carried from the previous fill --
    it is per ORDER, across all of its fills, taker and maker alike. Starting each fill from zero would model
    a different, more expensive exchange than the real one.
    """
    precision = _d(balance_precision)
    p, c = _d(price), _d(contracts)
    raw = _d(coefficient) * _d(multiplier) * c * p * (Decimal(1) - p)
    trade_fee = ceil_to(raw, TRADE_FEE_INCREMENT)

    # A buy debits the position cost plus the fee. The account's balance moves in its own precision, and the
    # shortfall from flooring that debit is charged as the rounding fee.
    revenue = -(c * p)
    balance_raw = revenue - trade_fee
    balance = floor_to(balance_raw, precision)
    rounding_fee = balance_raw - balance                       # in [0, precision)

    acc = _d(accumulator) + rounding_fee
    rebate = Decimal("0")
    capped = False
    if acc > precision:
        # The rebate is CAPPED so an individual fill's net fee cannot become negative. This is the venue's
        # rule, not a defensive choice of ours, and it is the difference between modelling the exchange and
        # modelling something more convenient: a tiny fill simply cannot absorb a whole precision unit of
        # credit, and the unabsorbed part stays in the accumulator for a later fill to earn.
        rebate = min(precision, trade_fee + rounding_fee)
        capped = rebate < precision
        acc -= rebate

    net = trade_fee + rounding_fee - rebate                    # >= 0 by construction

    return FeeComponents(
        raw_quadratic=float(raw), trade_fee=float(trade_fee), rounding_fee=float(rounding_fee),
        rebate=float(rebate), net_fee=float(net), balance_change=float(balance),
        accumulator_after=float(acc), rebate_capped=capped)


def fee_for_order(fills, coefficient, multiplier, *, balance_precision=CENT) -> dict:
    """Every fill of one order, carrying the accumulator between them.

    `fills` is [(price, contracts)]. Returns the per-fill components and the order totals -- which is the
    only level at which the rebate mechanism makes sense, since the accumulator is what ties the fills
    together.
    """
    acc = Decimal("0")
    capped = 0
    out, totals = [], {"raw_quadratic": Decimal("0"), "trade_fee": Decimal("0"),
                       "rounding_fee": Decimal("0"), "rebate": Decimal("0"),
                       "net_fee": Decimal("0"), "contracts": Decimal("0"), "cost": Decimal("0")}
    for price, contracts in fills:
        comp = fee_for_fill(price, contracts, coefficient, multiplier,
                            accumulator=acc, balance_precision=balance_precision)
        acc = _d(comp.accumulator_after)
        capped += 1 if comp.rebate_capped else 0
        out.append(comp)
        for k, v in (("raw_quadratic", comp.raw_quadratic), ("trade_fee", comp.trade_fee),
                     ("rounding_fee", comp.rounding_fee),
                     ("rebate", comp.rebate), ("net_fee", comp.net_fee)):
            totals[k] += _d(v)
        totals["contracts"] += _d(contracts)
        totals["cost"] += _d(contracts) * _d(price)
    # No floor here, and none needed. Every fill's net is non-negative by construction because the rebate is
    # capped at that fill's own fee, so the order total cannot be negative either. The exact identity
    #
    #     net_fee_order == SUM(trade_fee_i) + accumulator_final
    #
    # follows directly (the rounding fees minus the rebates ARE the accumulator, which starts at zero), and
    # `rounding_uncertainty` depends on it.
    return {"fills": out, "accumulator_final": float(acc), "rebates_capped": capped,
            **{k: float(v) for k, v in totals.items()}}


# ---- pre-trade rounding uncertainty ----------------------------------------------------------------

# Kalshi's order sizes are FIXED-POINT, not integral. The documented minimum increment is 0.01 contract,
# and fills of 0.30 or 0.03 contracts are ordinary. The earlier bound here assumed a fill was at least one
# whole contract, which made `N <= ceil(contracts)` and was simply false: a 0.90-contract order can arrive
# as ninety separate fills, not one.
CONTRACT_INCREMENT_FRACTIONAL = Decimal("0.01")     # the documented fixed-point minimum
CONTRACT_INCREMENT_WHOLE = Decimal("1")             # only when metadata PROVES fractional trading is off

GRANULARITY_FRACTIONAL = "FRACTIONAL_ENABLED"
GRANULARITY_WHOLE = "WHOLE_CONTRACTS_ONLY"
GRANULARITY_UNKNOWN = "UNKNOWN"                     # treated exactly as FRACTIONAL_ENABLED


def contract_increment(state: str) -> Decimal:
    """The smallest quantity that can fill, from the granularity state.

    UNKNOWN resolves to the FRACTIONAL increment, not the whole-contract one. "We could not establish that
    fractional trading is disabled" and "fractional trading is disabled" are the two cases this distinction
    exists to keep apart, and only one of them may shrink a cost bound.
    """
    return CONTRACT_INCREMENT_WHOLE if state == GRANULARITY_WHOLE else CONTRACT_INCREMENT_FRACTIONAL


def rounding_uncertainty(contracts, balance_precision=CENT,
                         trade_fee_increment=TRADE_FEE_INCREMENT, *,
                         granularity_state: str = GRANULARITY_UNKNOWN,
                         contract_increment_override=None, levels=None) -> dict:
    """A WORST-CASE bound on how much more a FRAGMENTED order can cost than the same order in one fill.

    Before the trade we know the price levels and the quantity at each; we do not know how many pieces the
    venue will fill each level in. The accumulator makes fragmentation CONVERGE on the equivalent order --
    that is its purpose -- but it does not make it identical, and a pre-trade estimate priced as one fill per
    level is therefore slightly optimistic. This says by exactly how much, from the mechanism.

    Two sources, and there are only two:

      CEILING.  `net_fee = SUM(trade_fee_i) + accumulator_final` (the rounding fees minus the rebates ARE
                the accumulator, since it starts at zero). WITHIN ONE PRICE LEVEL the raw quadratic is
                linear in contracts, so `SUM(raw_i) == raw_level`, and each fill's rounding-up adds
                strictly less than one TRADE_FEE_INCREMENT. With N fills the excess is therefore
                < N * TRADE_FEE_INCREMENT.

      RESIDUAL. The accumulator is bounded by one balance precision. This needed re-proving once the venue's
                per-fill REBATE CAP was modelled, because a fill too small to absorb a whole precision unit
                of credit no longer drains the accumulator by a full unit -- so the old one-line argument
                ("anything above one unit immediately rebates one") no longer applies. Writing `A` for the
                accumulator before a fill, `r` for its rounding fee (in [0, precision)) and `t` for its
                trade fee, and assuming A <= precision:

                  no trigger (A + r <= precision)   ->  A' = A + r <= precision.
                  trigger, t + r >= precision       ->  rebate = precision, A' = A + r - precision <= r
                                                        < precision.
                  trigger, t + r <  precision       ->  rebate = t + r, so A' = A - t. The trigger gives
                                                        A > precision - r and the case gives t < precision
                                                        - r, hence t < A: A' is positive, and A' < A
                                                        <= precision.

                So A <= precision is preserved in every case, and the single-fill estimate carries a
                residual of its own that is at least zero -- the DIFFERENCE is bounded by one precision
                unit. `tests/test_fees.py` re-checks this by brute force rather than trusting the argument. Once per ORDER, not once per level.

      bound = N * trade_fee_increment  +  balance_precision

    WHAT N ACTUALLY IS
    ------------------
    N is the largest number of fills the order can arrive in, which is set by the venue's minimum fill
    quantity -- NOT by our stake being a whole number of dollars. Approved stakes are whole DOLLARS; the
    contract quantities they buy are routinely fractional (`$10 / 0.62 = 16.13 contracts`), order-book
    quantities are fixed-point, and Kalshi fills can be fractional down to 0.01 contract. So:

        N = SUM over price levels of ceil(contracts_at_level / contract_increment)

    Summing per level rather than over the total is what keeps this an upper bound on the real thing: a fill
    cannot span two price levels, so the levels fragment independently.

    NO DOUBLE-CHARGING
    ------------------
    `levels` is the observed depth walk (`DepthResult.levels_consumed`). The fee ESTIMATE already prices
    that decomposition exactly -- the VWAP movement across levels is known and paid for there. This function
    bounds only the fragmentation WITHIN each level's known quantity, which is the part nobody can see before
    the order is worked. Passing no `levels` falls back to treating the whole quantity as one level, which is
    a weaker (larger) bound, never a smaller one.

    This is a TRANSACTION-COST bound, not a strategy buffer. It is derived from the venue's published
    rounding and fixed-point rules, and nothing in it may be tuned to make trades easier or harder to find.
    """
    inc = _d(trade_fee_increment)
    prec = _d(balance_precision)
    step = (_d(contract_increment_override) if contract_increment_override is not None
            else contract_increment(granularity_state))
    if step <= 0:
        return {"bound_dollars": None, "reason": f"contract increment {step} is not positive"}

    if levels:
        try:
            quantities = [_d(c) for _p, c in levels]
        except (TypeError, ValueError):
            return {"bound_dollars": None, "reason": f"levels {levels!r} are not (price, contracts) pairs"}
        basis = f"{len(quantities)} observed price level(s)"
    else:
        try:
            quantities = [_d(contracts)]
        except (TypeError, ValueError, InvalidOperation):
            return {"bound_dollars": None, "reason": f"contracts {contracts!r} is not numeric"}
        basis = "the whole quantity as a single price level (no observed book)"

    quantities = [q for q in quantities if q > 0]
    if not quantities:
        return {"bound_dollars": None, "reason": "no positive quantity to bound"}

    # ceil(q / step) per level, in Decimal so 0.29999999 never becomes an extra fill.
    max_fills = sum(int((q / step).to_integral_value(rounding=ROUND_CEILING)) for q in quantities)
    ceiling_bound = _d(max_fills) * inc
    bound = ceiling_bound + prec
    return {
        "max_fills": max_fills,
        "contract_increment": float(step),
        "trade_fee_increment": float(inc),
        "balance_precision": float(prec),
        "granularity_state": granularity_state,
        "levels_basis": basis,
        "trade_fee_ceiling_bound": float(ceiling_bound),
        "accumulator_residual_bound": float(prec),
        "bound_dollars": float(bound),
        "derivation": (f"across {basis}, at most {max_fills} fill(s) of >= {float(step)} contract "
                       f"({granularity_state}), each ceiling strictly under {float(inc)} above the "
                       f"within-level linear quadratic, plus at most {float(prec)} of un-rebated "
                       "accumulator residual across the order"),
    }


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
    verification_policy: dict = field(default_factory=dict)
    granularity: dict = field(default_factory=dict)

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
                 f"{1 - float(price):.4f}) up to {TRADE_FEE_INCREMENT}, then alignment on a {precision} balance, "
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

    # ---- order granularity -------------------------------------------------------------------------
    def granularity_state_for(self, series_ticker: str | None) -> str:
        """Whether this series is known to trade in whole contracts only.

        Defaults to UNKNOWN, which is priced exactly as FRACTIONAL_ENABLED. A series is only moved to
        WHOLE_CONTRACTS_ONLY by a reviewed edit to config/kalshi_fee_schedule.json citing venue metadata --
        the same capture/surface/review discipline the fee multipliers get, and for the same reason: this
        value shrinks a cost bound, so it may never be inferred from silence.
        """
        g = self.granularity or {}
        per_series = (g.get("series") or {}).get(series_ticker) if series_ticker else None
        if isinstance(per_series, dict):
            state = per_series.get("state")
        else:
            state = per_series
        state = state or g.get("default_state") or GRANULARITY_UNKNOWN
        return state if state in (GRANULARITY_FRACTIONAL, GRANULARITY_WHOLE) else GRANULARITY_UNKNOWN

    # ---- freshness ---------------------------------------------------------------------------------
    def max_verification_age_days(self) -> float:
        return float((self.verification_policy or {}).get(
            "max_verification_age_days", DEFAULT_MAX_VERIFICATION_AGE_DAYS))

    def verification(self, series_ticker: str | None, as_of: datetime,
                     observations: "FeeObservations | None" = None) -> dict:
        """Can the applicable fee schedule be ESTABLISHED at `as_of`, and how recently was it checked?

        Four outcomes, three of which block a real recommendation:

            NO_SCHEDULE          no committed window covers this timestamp. Nothing to price with.
            PENDING_CHANGE       Kalshi announced a change effective at or before this decision and the
                                 committed schedule carries no window for it. The registry is knowably
                                 behind the venue, which is worse than never having looked.
            STALE_VERIFICATION   a window is in force but the last confirmation against the live API is
                                 older than the policy allows. A months-old unchecked registry is not a
                                 fee schedule, it is a memory.
            VERIFIED             in force and confirmed within the window.

        A change is never applied here. Capture, surface, block, and require a reviewed window update --
        auto-editing the regulatory schedule from an API response would let the venue silently rewrite every
        historical net-EV number in the ledger.
        """
        at = _iso(as_of)
        if at is None:
            raise FeeStateError(
                "fee-schedule verification requires the DECISION timestamp; the applicable schedule and its "
                "freshness are both statements about a point in time")

        w = self.window_for(at)
        if w is None:
            return {"state": NO_SCHEDULE, "as_of": at.isoformat(), "window_id": None,
                    "reason": f"no committed fee-schedule window covers {at.isoformat()}; the applicable "
                              "schedule cannot be established and no fee may be quoted against it"}

        obs = observations or FeeObservations(None)
        latest_snapshot = obs.latest(at)
        # A fee-change feed we could not read is NOT "no changes announced". It is "we do not know whether a
        # change was announced", and the whole point of ingesting the third source is that this distinction
        # is the one it exists to make.
        fc = (latest_snapshot or {}).get("fee_changes")
        fc_state = "NOT_CAPTURED"
        if isinstance(fc, dict):
            fc_state = "PARSED" if fc.get("parsed") and not fc.get("error") else "INCONCLUSIVE"

        # 1. An announced change the committed schedule has not absorbed.
        pending = []
        for ch in obs.announced_changes(at):
            eff = _change_effective(ch)
            if eff is None or eff > at:
                continue                       # a future change is a future window, not this one's problem
            if series_ticker and ch.get("series_ticker") not in (None, series_ticker):
                continue
            if any(_iso(x.get("effective_from")) == eff for x in self.windows):
                continue                       # already written up as a reviewed window
            pending.append(ch)
        if pending:
            return {
                "state": PENDING_CHANGE, "as_of": at.isoformat(), "window_id": w.get("window_id"),
                "pending_changes": pending,
                "reason": (f"Kalshi announced {len(pending)} fee change(s) effective at or before "
                           f"{at.isoformat()} that config/kalshi_fee_schedule.json does not carry a window "
                           "for. The committed schedule is knowably behind the venue; a reviewed window "
                           "update is required before a real recommendation is priced against it.")}

        # 2. How recently was the schedule actually confirmed? The committed attestation counts, and so does
        #    any clean live capture at or before the decision -- whichever is later.
        verified_at = _iso(w.get("verified_at"))
        basis = f"schedule window {w.get('window_id')} attested {w.get('verified_at')}"
        latest = latest_snapshot
        # A capture only REFRESHES verification if all three of its sources came back clean. An
        # INCONCLUSIVE fee-change feed means the capture did not establish that no change was announced,
        # so it cannot stand in for a confirmation of the schedule.
        if (latest is not None and not latest.get("differences") and not latest.get("errors")
                and fc_state == "PARSED"):
            t = _iso(latest.get("retrieved_at"))
            if t is not None and (verified_at is None or t > verified_at):
                verified_at, basis = t, f"clean live capture at {latest.get('retrieved_at')}"

        limit = self.max_verification_age_days()
        if verified_at is None:
            return {"state": STALE_VERIFICATION, "as_of": at.isoformat(),
                    "window_id": w.get("window_id"), "verified_at": None, "age_days": None,
                    "max_age_days": limit, "fee_changes_state": fc_state,
                    "reason": f"schedule window {w.get('window_id')} carries no verification timestamp, so "
                              "there is no evidence it still matches the venue"}

        age_days = (at - verified_at).total_seconds() / 86400.0
        common = {"as_of": at.isoformat(), "window_id": w.get("window_id"),
                  "verified_at": verified_at.isoformat(), "age_days": round(age_days, 2),
                  "max_age_days": limit, "basis": basis, "source": w.get("source"),
                  "fee_changes_state": fc_state}
        if age_days > limit:
            return dict(common, state=STALE_VERIFICATION,
                        reason=(f"the applicable fee schedule was last verified {age_days:.1f} days before "
                                f"this decision ({basis}), beyond the {limit:.0f}-day policy. Real money is "
                                "not priced off an unchecked registry; run "
                                "scripts/kalshi/capture_fee_metadata.py and commit any reviewed change."))
        return dict(common, state=VERIFIED,
                    reason=f"verified {age_days:.1f} days before the decision ({basis})")

    def describe(self, series_ticker: str, as_of: datetime | None = None) -> str:
        t = self.fee_type(series_ticker)
        if t is None:
            return f"{series_ticker}: fee regime UNKNOWN -- not in the captured registry"
        m = self.multipliers_for(series_ticker, as_of)
        return (f"{series_ticker}: fee_type {t}, taker multiplier {m.taker} ({m.taker_state}), "
                f"maker multiplier {m.maker} ({m.maker_state}), source {m.source}, "
                f"effective {m.effective_from}")


# ---- fee-schedule freshness ------------------------------------------------------------------------

VERIFIED = "VERIFIED"                       # a schedule is in force and was checked recently enough
STALE_VERIFICATION = "STALE_VERIFICATION"   # in force, but nobody has confirmed it against Kalshi lately
PENDING_CHANGE = "PENDING_CHANGE"           # Kalshi has announced a change the committed schedule lacks
NO_SCHEDULE = "NO_SCHEDULE"                 # no window covers this timestamp at all

DEFAULT_MAX_VERIFICATION_AGE_DAYS = 45.0


class FeeObservations:
    """Append-only fee observations captured from the live API onto the market-data branch.

    Two things live here and they answer different questions:

        series metadata      "is the committed registry still what the API reports?"
        /series/fee_changes  "has Kalshi ANNOUNCED a change we have not yet written a window for?"

    The second is why this class exists. A three-source hierarchy that never ingests its third source is a
    documented intention, not a control. `scripts/kalshi/capture_fee_metadata.py` writes these snapshots;
    nothing here writes anything.
    """

    def __init__(self, md_root: str | None):
        self.md_root = md_root
        self._loaded = None

    def _all(self) -> list:
        if self._loaded is not None:
            return self._loaded
        out = []
        if self.md_root:
            pattern = os.path.join(self.md_root, "data", "kalshi", "fees", "*.json")
            for path in sorted(glob.glob(pattern)):
                try:
                    with open(path) as f:
                        d = json.load(f)
                except (OSError, ValueError):
                    continue
                d["_path"] = path
                out.append(d)
        out.sort(key=lambda d: str(d.get("retrieved_at") or ""))
        self._loaded = out
        return out

    def latest(self, as_of: datetime | None = None) -> dict | None:
        """The newest snapshot taken at or before `as_of`. Later ones are not evidence about a past call."""
        cutoff = _iso(as_of)
        best = None
        for d in self._all():
            t = _iso(d.get("retrieved_at"))
            if t is None or (cutoff is not None and t > cutoff):
                continue
            best = d
        return best

    def announced_changes(self, as_of: datetime | None = None) -> list:
        """Every DISTINCT announced fee change captured at or before `as_of`.

        Deduplication is by the CHANGE, not by the series. Because `show_historical=true` is deliberate, one
        series routinely carries several changes -- a past one and a scheduled one, or two scheduled at
        different times -- and the same change reappears in every weekly snapshot. Keying on the series
        alone collapses all of them into whichever the loop happened to see last, which is exactly how an
        applicable unmodelled change gets hidden behind a later, harmless one.
        """
        cutoff = _iso(as_of)
        seen: dict = {}
        for d in self._all():
            t = _iso(d.get("retrieved_at"))
            if t is None or (cutoff is not None and t > cutoff):
                continue
            for ch in ((d.get("fee_changes") or {}).get("changes") or []):
                seen[change_identity(ch)] = dict(ch, _observed_at=d.get("retrieved_at"))
        return [seen[k] for k in sorted(seen, key=lambda k: tuple(str(x) for x in k))]


# `scheduled_ts` is what the documented response actually carries. The other names are defensive.
CHANGE_EFFECTIVE_KEYS = ("scheduled_ts",                                        # documented
                         "effective_at", "effective_time", "effective_from", "effective_date")


def change_identity(ch: dict) -> tuple:
    """A stable identity for one announced fee change, so weekly snapshots converge on ONE logical change.

    The documented response carries an `id`; when it is present that IS the identity, because the venue
    already decided what counts as the same change. The fallback is deterministic and includes everything
    that distinguishes two changes on one series -- the canonical effective timestamp, the fee type and the
    multiplier -- so two changes on the same series can never collapse into one another.
    """
    cid = ch.get("id")
    if cid not in (None, ""):
        return ("id", str(cid))
    eff = _change_effective(ch)
    return ("derived", str(ch.get("series_ticker")), eff.isoformat() if eff else "",
            str(ch.get("fee_type")), str(ch.get("fee_multiplier")))


def _change_effective(ch) -> datetime | None:
    """The moment an announced change takes effect, from whichever key carries it.

    Kalshi's `_ts` suffix is epoch seconds elsewhere in the API and the documented example shows a string, so
    both are accepted rather than betting on one and silently dropping the change if we bet wrong.
    """
    for key in CHANGE_EFFECTIVE_KEYS:
        v = ch.get(key)
        t = _iso(v)
        if t is not None:
            return t
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            try:
                return datetime.fromtimestamp(float(v), tz=timezone.utc)
            except (ValueError, OSError, OverflowError):
                continue
        if isinstance(v, str) and v.strip().isdigit():
            try:
                return datetime.fromtimestamp(float(v.strip()), tz=timezone.utc)
            except (ValueError, OSError, OverflowError):
                continue
    return None


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
        fs.verification_policy = sched.get("verification_policy") or {}
        fs.granularity = sched.get("contract_granularity") or {}
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
    # A worst-case bound on the extra cost of unknown fill fragmentation, derived in `rounding_uncertainty`.
    # `conservative_net_ev_dollars` is net EV less that bound: the number that is still positive even if the
    # venue fragments the order as badly as its own rounding rules permit.
    fee_uncertainty_dollars: float | None = None
    fee_uncertainty: dict | None = None
    conservative_net_ev_dollars: float | None = None

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
    # The bound covers fragmentation WITHIN the observed price levels. The movement ACROSS levels is already
    # priced exactly by `fee.amount` above, which was computed from these same `fills`.
    unc = rounding_uncertainty(contracts, schedule.balance_precision(direct_member),
                               granularity_state=schedule.granularity_state_for(series_ticker),
                               levels=fills)
    bound = unc.get("bound_dollars")
    return NetEV(
        fair_probability=fair_probability, executable_price=executable_price, contracts=contracts,
        stake_dollars=stake, gross_edge=gross_edge, gross_ev_dollars=gross_ev,
        estimated_fees=fee.amount, fee_state=KNOWN, fee_basis=fee.basis,
        estimated_slippage_dollars=float(slippage_dollars), net_ev_dollars=net,
        net_edge=None if not contracts else round(net / float(contracts), 6),
        state=KNOWN, fee_components=fee.components,
        fee_uncertainty_dollars=bound, fee_uncertainty=unc,
        conservative_net_ev_dollars=None if bound is None else round(net - bound, 6))


def contracts_for_stake(stake_dollars, price) -> float:
    """Contracts a dollar stake buys at a price. Fractional by design."""
    if not price or float(price) <= 0:
        return 0.0
    return float(stake_dollars) / float(price)
