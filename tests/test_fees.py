"""Kalshi's 2026 fixed-point fee mechanics, and the refusal to state a number the schedule cannot supply.

Two failures this file exists to prevent, in opposite directions:

  a hidden fee default that is too low   manufactures profitable trades that do not exist
  calling a published value "unknown"    refuses trades that are perfectly priceable

The second is the newer mistake. Kalshi's regulatory Fee Schedule lists BOTH a Maker Multiplier and a Taker
Multiplier for each listed non-standard series; `GET /series/{ticker}` carries only the taker one. The API
object's silence about the maker multiplier is not evidence that the maker multiplier is unknown, and
treating it that way blocked KXNFLGAME on a number that is published.

And the rounding is not `ceil(raw, $0.01)`. The trade fee is rounded UP to $0.000001, the balance change is
then aligned to the account's balance precision as a separate rounding fee, and the overpayment accumulates
per order until it earns a rebate of one precision unit -- capped so a fill's own net fee cannot go negative.

The increment has been wrong here twice, in both directions, which is why the primitives are pinned against
numbers that actually DISCRIMINATE: a $0.01 ceiling overstates a twenty-fill order by up to twenty cents,
and a $0.0001 ceiling -- what this file asserted until the increment was re-read from the current venue
documentation -- overstates it by a hundredth of that but is still simply not the rule.
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

def test_the_trade_fee_rounds_up_to_a_millionth_of_a_dollar():
    """$0.000001 -- six decimal dollars. Not a cent, and not a ten-thousandth either.

    These inputs are chosen to DISCRIMINATE. `0.00841234` is untouched by a $0.0001 ceiling only if you
    round it to $0.0085, so the two candidate increments give visibly different answers here; the earlier
    version of this test used values already aligned to $0.0001 and could not have caught the difference.
    """
    assert F.TRADE_FEE_INCREMENT == Decimal("0.000001")
    assert F.ceil_to(Decimal("0.00841234"), F.TRADE_FEE_INCREMENT) == Decimal("0.008413")
    assert F.ceil_to(Decimal("0.008413"), F.TRADE_FEE_INCREMENT) == Decimal("0.008413")
    assert F.ceil_to(Decimal("0.0000001"), F.TRADE_FEE_INCREMENT) == Decimal("0.000001")
    # The increment that used to be here would have given a materially different number.
    assert F.ceil_to(Decimal("0.00841234"), Decimal("0.0001")) == Decimal("0.0085")


def test_the_two_balance_precisions_are_named_and_distinct():
    assert F.NON_DIRECT_BALANCE_PRECISION == Decimal("0.01")
    assert F.DIRECT_BALANCE_PRECISION == Decimal("0.0001")
    assert F.CENT == F.NON_DIRECT_BALANCE_PRECISION


def test_a_direct_member_pays_less_rounding_on_the_same_fill():
    """The finer balance precision is the whole point of the direct-member distinction."""
    ordinary = F.fee_for_fill(0.055, 1, 0.07, 1.0, balance_precision=F.NON_DIRECT_BALANCE_PRECISION)
    direct = F.fee_for_fill(0.055, 1, 0.07, 1.0, balance_precision=F.DIRECT_BALANCE_PRECISION)
    assert direct.rounding_fee < ordinary.rounding_fee
    assert direct.net_fee < ordinary.net_fee
    assert direct.trade_fee == ordinary.trade_fee, "the trade fee does not depend on balance precision"


def test_the_balance_floors_toward_a_larger_debit():
    """A debit rounds AWAY from the account holder. -0.0635 becomes -0.07, not -0.06."""
    assert F.floor_to(Decimal("-0.0635"), F.CENT) == Decimal("-0.07")
    assert F.floor_to(Decimal("-0.07"), F.CENT) == Decimal("-0.07")


def test_decimal_arithmetic_leaves_no_binary_residue():
    """0.07 * 4 * 0.5 * 0.5 is exactly 0.07. Float would make it 0.07000000000000001 and ceil a step up."""
    comp = F.fee_for_fill(0.50, 4, 0.07, 1.0)
    assert comp.trade_fee == pytest.approx(0.07)


# ---- the documented worked example -------------------------------------------------------------------

def test_the_current_official_worked_example_is_reproduced_exactly():
    """The CURRENT Kalshi Fee Rounding example, number for number.

        signed revenue        -$0.055000
        model fee              $0.00363825      = 0.07 x 1 x 0.055 x 0.945
        trade fee              $0.003639        = ceil to $0.000001
        aligned change        -$0.060000        = floor to a cent of (-0.055 - 0.003639)
        rounding fee           $0.001361        = (-0.058639) - (-0.060000)
        trade + rounding       $0.005000

    Note that no synthetic coefficient is needed: the example is one contract at $0.055 under the ordinary
    0.07 taker coefficient, and the model fee falls out exactly. The example this replaced gave a trade fee
    of $0.0085 on the same price and quantity -- a different fee regime, kept in this file long after it
    stopped being current, and reproducing perfectly against the wrong rounding rule because every number in
    it was already aligned to four decimals.
    """
    c = F.fee_for_fill(Decimal("0.055"), 1, Decimal("0.07"), 1,
                       balance_precision=F.NON_DIRECT_BALANCE_PRECISION)
    assert c.raw_quadratic == pytest.approx(0.00363825)
    assert c.trade_fee == pytest.approx(0.003639)
    assert c.balance_change == pytest.approx(-0.060000)
    assert c.rounding_fee == pytest.approx(0.001361)
    assert c.trade_fee + c.rounding_fee == pytest.approx(0.005000)
    assert c.rebate == 0.0, "one fill has not yet accrued a whole precision unit"
    assert c.net_fee == pytest.approx(0.005000)


def test_the_obsolete_worked_example_is_not_presented_as_current():
    """A tripwire, because this exact number outlived its own documentation once already.

    `$0.0085` was the trade fee in an OLDER Kalshi example for a 1-contract fill at $0.055. Under the
    current rules that fill's trade fee is `$0.003639`. Anything in the operating code or documentation
    still offering the old number as the current worked example is stale by construction.
    """
    import glob                                                          # noqa: PLC0415
    import os as _os                                                     # noqa: PLC0415

    offenders = []
    for pattern in ("nfl_edge/**/*.py", "scripts/**/*.py", "config/*.json", "docs/*.md"):
        for path in glob.glob(_os.path.join(ROOT, pattern), recursive=True):
            if _os.path.basename(path) == _os.path.basename(__file__):
                continue                      # this file names the obsolete number in order to forbid it
            with open(path) as f:
                for i, line in enumerate(f, 1):
                    low = line.lower()
                    if "0.0085" not in line:
                        continue
                    if not any(w in low for w in ("example", "documented", "trade fee")):
                        continue
                    # Allowed only where the line itself marks the number as superseded.
                    if any(w in low for w in ("supersede", "older", "obsolete", "historic", "wrong",
                                              "no longer", "used to", "prior", "previous")):
                        continue
                    offenders.append(f"{_os.path.relpath(path, ROOT)}:{i}: {line.strip()[:100]}")
    assert not offenders, ("the obsolete $0.0085 worked example is still presented as current; the current "
                           f"trade fee for that fill is $0.003639: {offenders}")

    # And the current one really is what the engine produces.
    assert F.fee_for_fill(Decimal("0.055"), 1, Decimal("0.07"), 1).trade_fee == pytest.approx(0.003639)


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
    n = 10
    order = F.fee_for_order([(0.055, 1)] * n, 0.07, 1.0)
    assert order["rebate"] > 0, f"{n} fills should earn a rebate"
    independent = sum(F.fee_for_fill(0.055, 1, 0.07, 1.0).net_fee for _ in range(n))
    assert order["net_fee"] < independent, "carrying the accumulator must cost less than restarting it"
    assert F.fee_for_order([(0.055, 1)] * 2, 0.07, 1.0)["rebate"] == 0.0, \
        "two fills have not yet accrued a whole precision unit of rounding"


# ---- the per-fill rebate cap -------------------------------------------------------------------------

def test_a_fills_net_fee_can_never_be_negative():
    """The venue caps the rebate so an individual fill's net fee stays at or above zero.

    This is the exchange's rule. A previous version of this engine let a fill's net go negative and floored
    only the order total -- which models a more generous exchange than the real one on exactly the tiny
    fills where the difference shows up.
    """
    tiny = F.fee_for_fill(0.5, 0.01, 0.07, 1.0, accumulator=0.0098)
    assert tiny.rebate_capped is True
    assert tiny.rebate == pytest.approx(tiny.trade_fee + tiny.rounding_fee)
    assert tiny.net_fee == pytest.approx(0.0)
    assert tiny.net_fee >= 0.0


def test_the_unabsorbed_part_of_a_rebate_stays_in_the_accumulator():
    """A capped rebate is deferred, not forfeited: a later fill can still earn it."""
    capped = F.fee_for_fill(0.5, 0.01, 0.07, 1.0, accumulator=0.0098)
    assert capped.accumulator_after > 0, "the credit the fill could not absorb is still owed"
    assert capped.accumulator_after == pytest.approx(0.0098 + capped.rounding_fee - capped.rebate)


def test_no_fill_of_any_shape_produces_a_negative_net():
    for price in (0.01, 0.055, 0.5, 0.62, 0.99):
        for contracts in (0.01, 0.03, 0.3, 0.9, 1, 7.5, 100):
            for acc in (0.0, 0.005, 0.0098, 0.01):
                for prec in (F.NON_DIRECT_BALANCE_PRECISION, F.DIRECT_BALANCE_PRECISION):
                    c = F.fee_for_fill(price, contracts, 0.07, 1.0, accumulator=acc,
                                       balance_precision=prec)
                    assert c.net_fee >= 0.0, (price, contracts, acc, prec)


def test_the_accumulator_stays_within_one_balance_precision_under_the_cap():
    """Re-proved by brute force, because the cap invalidated the previous one-line argument.

    The old proof was "anything above one unit immediately rebates one", which stops being true once a fill
    too small to absorb a whole unit rebates less. The invariant survives -- see the case analysis in
    `fees.rounding_uncertainty` -- and this checks it rather than trusting it.
    """
    import random                                                       # noqa: PLC0415
    random.seed(11)
    for _ in range(600):
        prec = random.choice([F.NON_DIRECT_BALANCE_PRECISION, F.DIRECT_BALANCE_PRECISION])
        fills = [(round(random.uniform(0.01, 0.99), 4),
                  random.choice([0.01, 0.03, 0.3, 0.9, 1.0, 7.5]))
                 for _ in range(random.randint(1, 40))]
        order = F.fee_for_order(fills, 0.07, 1.0, balance_precision=prec)
        assert 0 <= order["accumulator_final"] <= float(prec) + 1e-12
        # The identity the uncertainty bound rests on, with no flooring anywhere.
        assert order["net_fee"] == pytest.approx(order["trade_fee"] + order["accumulator_final"], abs=1e-9)


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
    """A price between cents. The six-decimal ceiling is what keeps this from being rounded into nonsense."""
    q = sched.taker_fee(0.555, 100, "KXNFLGAME", as_of=AS_OF)
    raw = 0.07 * 100 * 0.555 * 0.445    # a subpenny price makes the raw fee land off a cent boundary
    assert q.components["raw_quadratic"] == pytest.approx(raw)
    assert q.components["trade_fee"] == pytest.approx(
        float(F.ceil_to(Decimal(str(raw)), F.TRADE_FEE_INCREMENT)))
    # `raw` here is a FLOAT product and carries binary residue (…0000000003); the engine computes the same
    # quantity exactly in Decimal. The tolerance is for the test's arithmetic, not the engine's.
    assert q.components["trade_fee"] >= raw - 1e-9


def test_fractional_contracts_at_a_subpenny_price(sched):
    q = sched.taker_fee(0.0555, 12.5, "KXNFLGAME", as_of=AS_OF)
    assert q.is_known
    raw = 0.07 * 12.5 * 0.0555 * 0.9445
    assert q.components["raw_quadratic"] == pytest.approx(raw)
    # the trade fee is a whole number of trade-fee increments
    inc = float(F.TRADE_FEE_INCREMENT)
    assert abs(round(q.components["trade_fee"] / inc) * inc - q.components["trade_fee"]) < 1e-9
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
    """0.0175 * 1 * 100 * 0.25 = $0.4375, rounded up to a trade-fee increment then cent-aligned."""
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
