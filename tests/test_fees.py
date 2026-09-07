"""Kalshi's 2026 fixed-point fee mechanics, and the refusal to state a number the schedule cannot supply.

Two failures this file exists to prevent, in opposite directions:

  a hidden fee default that is too low   manufactures profitable trades that do not exist
  calling a published value "unknown"    refuses trades that are perfectly priceable

The second is the newer mistake. Kalshi's regulatory Fee Schedule lists BOTH a Maker Multiplier and a Taker
Multiplier for each listed non-standard series; `GET /series/{ticker}` carries only the taker one. The API
object's silence about the maker multiplier is not evidence that the maker multiplier is unknown, and
treating it that way blocked KXNFLGAME on a number that is published.

And the rounding is not `ceil(raw, $0.01)`. The trade fee is ceiled to a CENTICENT, the balance change is
then cent-aligned as a separate rounding fee, and the overpayment accumulates per order until it earns a
whole-cent rebate. Collapsing that to a per-fill cent ceiling overstates a twenty-fill order by up to twenty
cents.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.execution import fees as F  # noqa: E402

AS_OF = datetime(2026, 9, 9, 13, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def sched():
    return F.load_fee_schedule(ROOT)


# ---- rounding primitives ---------------------------------------------------------------------------

def test_the_trade_fee_ceils_to_a_centicent_not_a_cent():
    """$0.0001, not $0.01. A cent ceiling on a small fill overstates it by up to 100x."""
    assert F.ceil_to(Decimal("0.00841"), F.CENTICENT) == Decimal("0.0085")
    assert F.ceil_to(Decimal("0.0085"), F.CENTICENT) == Decimal("0.0085")
    assert F.ceil_to(Decimal("0.00001"), F.CENTICENT) == Decimal("0.0001")


def test_the_balance_floors_toward_a_larger_debit():
    """A debit rounds AWAY from the account holder. -0.0635 becomes -0.07, not -0.06."""
    assert F.floor_to(Decimal("-0.0635"), F.CENT) == Decimal("-0.07")
    assert F.floor_to(Decimal("-0.07"), F.CENT) == Decimal("-0.07")


def test_decimal_arithmetic_leaves_no_binary_residue():
    """0.07 * 4 * 0.5 * 0.5 is exactly 0.07. Float would make it 0.07000000000000001 and ceil a step up."""
    comp = F.fee_for_fill(0.50, 4, 0.07, 1.0)
    assert comp.trade_fee == pytest.approx(0.07)


# ---- the documented worked example -------------------------------------------------------------------

def test_the_documented_rounding_example_is_reproduced_exactly():
    """Kalshi's fee-rounding documentation, fill by fill.

        fill 1  revenue -$0.0550, trade fee $0.0085 -> balance -$0.0635 floors to -$0.0700
                rounding fee $0.0065, accumulator $0.0065, no rebate, net $0.0150
        fill 2  same again -> accumulator $0.0130 > $0.01
                rebate $0.0100, accumulator $0.0030, net $0.0050

    The published example gives the trade fee directly rather than the quadratic behind it, so this pins the
    ROUNDING layer -- which is the part that was wrong -- against the exact numbers. The quadratic itself is
    pinned algebraically above and below.
    """
    # A (coefficient * multiplier) that makes the quadratic land on the documented $0.0085 trade fee for a
    # 1-contract fill at $0.055.
    price, contracts = Decimal("0.055"), Decimal("1")
    coef = Decimal("0.0085") / (contracts * price * (Decimal(1) - price))

    f1 = F.fee_for_fill(price, contracts, coef, 1)
    assert f1.trade_fee == pytest.approx(0.0085)
    assert f1.balance_change == pytest.approx(-0.07)
    assert f1.rounding_fee == pytest.approx(0.0065)
    assert f1.rebate == 0.0
    assert f1.accumulator_after == pytest.approx(0.0065)
    assert f1.net_fee == pytest.approx(0.0150)

    f2 = F.fee_for_fill(price, contracts, coef, 1, accumulator=f1.accumulator_after)
    assert f2.rounding_fee == pytest.approx(0.0065)
    assert f2.rebate == pytest.approx(0.01), "the accumulator crossed a cent and must rebate one"
    assert f2.accumulator_after == pytest.approx(0.0030)
    assert f2.net_fee == pytest.approx(0.0050)


def test_the_accumulator_makes_many_small_fills_converge_on_one_equivalent_fill():
    """The economic point of the mechanism. Without the rebate this diverges by cents per fill."""
    one = F.fee_for_order([(0.50, 100)], 0.07, 1.0)
    many = F.fee_for_order([(0.50, 1)] * 100, 0.07, 1.0)
    # The residual is the un-rebated accumulator, which is bounded by one cent by construction -- so 100
    # fills land within a cent of the single equivalent fill, not within a cent PER FILL.
    assert abs(many["net_fee"] - one["net_fee"]) <= 0.0101, \
        f"100 fills cost {many['net_fee']} vs {one['net_fee']} for one equivalent fill"

    # The naive model -- ceil every fill to the next cent, independently -- is strictly worse, and the gap
    # widens as the per-fill fee shrinks. At 50c the true fee is 1.75c so a cent ceiling costs 14% extra; at
    # 5.5c the true fee is 0.36c and the same ceiling costs nearly 3x.
    naive_50 = 100 * float(F.ceil_to(Decimal("0.07") * Decimal("0.5") * Decimal("0.5"), F.CENT))
    assert naive_50 > many["net_fee"], "a per-fill cent ceiling must overstate the real cost"

    cheap = F.fee_for_order([(0.055, 1)] * 100, 0.07, 1.0)
    naive_cheap = 100 * float(F.ceil_to(Decimal("0.07") * Decimal("0.055") * Decimal("0.945"), F.CENT))
    assert naive_cheap > cheap["net_fee"] * 1.5, \
        "on small fills the naive cent ceiling should be dramatically wrong"


def test_the_accumulator_carries_across_fills_of_one_order():
    """Per ORDER, not per fill. Restarting it each fill models a more expensive exchange than the real one."""
    # Each fill here accrues $0.0013 of rounding, so a rebate is earned on the 8th -- not the 6th. The
    # exact count is the point: the accumulator is a running total, not a per-fill reset.
    n = 10
    order = F.fee_for_order([(0.055, 1)] * n, 0.07, 1.0)
    assert order["rebate"] == pytest.approx(0.01), f"{n} fills should earn exactly one rebate"
    independent = sum(F.fee_for_fill(0.055, 1, 0.07, 1.0).net_fee for _ in range(n))
    assert order["net_fee"] < independent, "carrying the accumulator must cost less than restarting it"
    assert F.fee_for_order([(0.055, 1)] * 7, 0.07, 1.0)["rebate"] == 0.0, \
        "seven fills accrue 0.0091 and must NOT yet earn a rebate"


# ---- the four price/quantity shapes the review asked for -------------------------------------------

def test_whole_contracts_at_a_whole_cent_price(sched):
    """100 @ 50c on KXNFLGAME: 0.07 * 100 * 0.25 = $1.75 exactly, and the balance is already cent-aligned."""
    q = sched.taker_fee(0.50, 100, "KXNFLGAME", as_of=AS_OF)
    assert q.is_known and q.amount == pytest.approx(1.75)
    assert q.components["rounding_fee"] == pytest.approx(0.0)


def test_fractional_contracts(sched):
    """37.5 contracts is a real quantity in this ledger's accounting and is never truncated."""
    a = sched.taker_fee(0.50, 37.5, "KXNFLGAME", as_of=AS_OF)
    b = sched.taker_fee(0.50, 37.0, "KXNFLGAME", as_of=AS_OF)
    assert a.is_known and b.is_known
    assert a.amount != b.amount, "the fractional part was truncated away"
    assert a.components["trade_fee"] == pytest.approx(0.65625 + 0.00005, abs=0.0001) or \
        a.components["trade_fee"] == pytest.approx(0.6563, abs=0.0001)


def test_subpenny_price(sched):
    """A price between cents. The centicent ceiling is what keeps this from being rounded into nonsense."""
    q = sched.taker_fee(0.555, 100, "KXNFLGAME", as_of=AS_OF)
    raw = 0.07 * 100 * 0.555 * 0.445    # a subpenny price makes the raw fee land off a cent boundary
    assert q.components["raw_quadratic"] == pytest.approx(raw)
    assert q.components["trade_fee"] == pytest.approx(float(F.ceil_to(Decimal(str(raw)), F.CENTICENT)))
    assert q.components["trade_fee"] >= raw


def test_fractional_contracts_at_a_subpenny_price(sched):
    q = sched.taker_fee(0.0555, 12.5, "KXNFLGAME", as_of=AS_OF)
    assert q.is_known
    raw = 0.07 * 12.5 * 0.0555 * 0.9445
    assert q.components["raw_quadratic"] == pytest.approx(raw)
    # trade fee is a whole number of centicents, and the net is a whole number of cents once aligned
    assert abs(round(q.components["trade_fee"] / 0.0001) * 0.0001 - q.components["trade_fee"]) < 1e-9
    assert q.components["rounding_fee"] >= 0


def test_multiple_fills_converge_through_the_rebate(sched):
    """A fragmented order and a single order of the same size cost materially the same."""
    fills = [(0.5555, 3.3)] * 12
    frag = sched.taker_fee(0.5555, sum(c for _p, c in fills), "KXNFLGAME", as_of=AS_OF, fills=fills)
    whole = sched.taker_fee(0.5555, sum(c for _p, c in fills), "KXNFLGAME", as_of=AS_OF)
    assert frag.is_known and whole.is_known
    assert frag.amount == pytest.approx(whole.amount, abs=0.02)
    assert frag.components["rebate"] >= 0.0


# ---- multipliers and the source hierarchy ------------------------------------------------------------

def test_the_published_maker_multiplier_is_known_not_unknown(sched):
    """KXNFLGAME is listed in the regulatory schedule with maker 1 and taker 1."""
    m = sched.multipliers_for("KXNFLGAME", AS_OF)
    assert m.maker == pytest.approx(1.0) and m.maker_state == F.KNOWN
    assert m.taker == pytest.approx(1.0) and m.taker_state == F.KNOWN
    assert m.source == F.SRC_REGULATORY
    assert m.effective_from and m.verified_at


def test_the_maker_fee_for_a_listed_series_is_priceable(sched):
    """0.0175 * 1 * 100 * 0.25 = $0.4375, ceiled to a centicent then cent-aligned."""
    q = sched.maker_fee(0.50, 100, "KXNFLGAME", as_of=AS_OF)
    assert q.is_known
    assert q.components["trade_fee"] == pytest.approx(0.4375)
    assert q.amount == pytest.approx(0.44)


def test_an_unlisted_maker_fee_series_is_unverified_not_assumed(sched):
    """KXNFLSPREAD charges a maker fee but no window we hold names its multiplier. That is not zero."""
    m = sched.multipliers_for("KXNFLSPREAD", AS_OF)
    assert m.maker is None and m.maker_state == F.UNVERIFIED
    assert m.taker == pytest.approx(1.0) and m.taker_state == F.KNOWN, \
        "the taker multiplier IS in series metadata and must not be dragged down with the maker one"
    q = sched.maker_fee(0.50, 100, "KXNFLSPREAD", as_of=AS_OF)
    assert not q.is_known and q.state == F.UNVERIFIED
    assert "DOES charge a maker fee" in q.reason


def test_a_taker_only_series_has_a_known_zero_maker_multiplier(sched):
    """Not charging a maker fee is a fact, not an absence of information."""
    taker_only = next(s for s, t in sched.fee_type_by_series.items() if t == F.FEE_TYPE_TAKER_ONLY)
    m = sched.multipliers_for(taker_only, AS_OF)
    assert m.maker == 0.0 and m.maker_state == F.KNOWN
    assert sched.maker_fee(0.50, 100, taker_only, as_of=AS_OF).amount == 0.0


def test_disagreeing_sources_fail_closed_rather_than_resolve_by_rank(sched):
    """Rank decides who is consulted first. It does not decide who is right."""
    fs = F.load_fee_schedule(ROOT)
    fs.metadata_multiplier_by_series = dict(fs.metadata_multiplier_by_series, KXNFLGAME=3.0)
    m = fs.multipliers_for("KXNFLGAME", AS_OF)
    assert m.taker_state == F.CONFLICTED and m.maker_state == F.CONFLICTED
    assert "One of them is wrong" in m.reason
    assert not fs.taker_fee(0.50, 100, "KXNFLGAME", as_of=AS_OF).is_known


def test_an_unregistered_series_is_degraded_not_free(sched):
    assert sched.taker_fee(0.5, 10, "KXNOTAREALSERIES", as_of=AS_OF).state == F.DEGRADED
    assert sched.maker_fee(0.5, 10, "KXNOTAREALSERIES", as_of=AS_OF).state == F.DEGRADED


def test_every_fee_value_preserves_its_provenance(sched):
    m = sched.multipliers_for("KXNFLGAME", AS_OF)
    d = m.to_dict()
    for k in ("taker", "maker", "taker_state", "maker_state", "source", "effective_from", "verified_at"):
        assert k in d, f"a fee value must carry {k}"
    assert sched.fee_type("KXNFLGAME") is not None


def test_the_source_hierarchy_is_declared_in_config(sched):
    ids = [s["id"] for s in sched.source_hierarchy]
    assert ids == [F.SRC_REGULATORY, F.SRC_SERIES_METADATA, F.SRC_FEE_CHANGES]
    assert "FAIL_CLOSED" in sched.conflict_policy


def test_an_untradable_price_has_no_defined_fee(sched):
    for p in (0.0, 1.0, None, 1.5):
        q = sched.taker_fee(p, 10, "KXNFLGAME", as_of=AS_OF)
        assert not q.is_known


def test_an_unknown_fee_refuses_to_yield_a_number(sched):
    with pytest.raises(F.FeeStateError):
        sched.maker_fee(0.50, 100, "KXNFLSPREAD", as_of=AS_OF).require()


# ---- effective windows -------------------------------------------------------------------------------

def test_a_schedule_that_took_effect_later_does_not_price_an_earlier_decision(sched):
    before = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert sched.window_for(AS_OF) is not None
    assert sched.window_for(before) is None, \
        "a decision before any known window has no schedule and must not borrow a later one"


def test_the_window_carries_a_verification_timestamp(sched):
    w = sched.window_for(AS_OF)
    assert w["verified_at"] and w["source"] == F.SRC_REGULATORY
    assert w["effective_from"]


# ---- net executable EV --------------------------------------------------------------------------------

def test_net_ev_separates_gross_edge_from_costs(sched):
    nev = F.net_executable_ev(0.66, 0.62, 100, sched, "KXNFLGAME", as_of=AS_OF)
    assert nev.gross_edge == pytest.approx(0.04)
    assert nev.gross_ev_dollars == pytest.approx(4.0)
    assert nev.state == F.KNOWN
    assert nev.net_ev_dollars == pytest.approx(4.0 - nev.estimated_fees)


def test_transaction_costs_can_erase_a_gross_edge(sched):
    nev = F.net_executable_ev(0.515, 0.50, 100, sched, "KXNFLGAME", as_of=AS_OF)
    assert nev.gross_ev_dollars > 0
    assert nev.net_ev_dollars < 0


def test_an_unverified_fee_makes_net_ev_unknown_not_zero_fee(sched):
    nev = F.net_executable_ev(0.66, 0.62, 100, sched, "KXNFLSPREAD",
                              execution_style=F.MAKER, as_of=AS_OF)
    assert nev.net_ev_dollars is None
    assert nev.state == F.UNVERIFIED
    assert nev.gross_edge is not None, "gross edge is still reportable; only the net is withheld"


def test_contracts_for_stake_is_the_kalshi_identity():
    assert F.contracts_for_stake(20, 0.50) == pytest.approx(40.0)
    assert F.contracts_for_stake(20, 0) == 0.0


# ---- the frozen passive-execution sweep ---------------------------------------------------------------

def test_the_frozen_passive_study_sweep_is_preserved():
    """research/passive (Milestone K) rejected passive execution. Its numbers must keep reproducing."""
    assert F.MAKER_FEE_SWEEP == (0.0, 0.0025, 0.005, 0.01)
