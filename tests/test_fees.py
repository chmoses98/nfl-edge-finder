"""Kalshi fee semantics, and the refusal to invent a number the schedule cannot supply.

The failure this file exists to prevent is specific: a hidden fee default that is too small manufactures
profitable trades that do not exist. So the tests check not only that the known formulas are right, but that
the unknown one stays visibly unknown and propagates that all the way to net EV.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.execution import fees as F  # noqa: E402


@pytest.fixture(scope="module")
def sched():
    return F.load_fee_schedule(ROOT)


# ---- the taker formula -----------------------------------------------------------------------------

def test_taker_fee_matches_the_published_formula(sched):
    """round_up_to_cent(0.07 * M * C * P * (1-P)). The peak is at P=0.50."""
    # 100 contracts at 50c: 0.07 * 100 * 0.25 = $1.75 exactly.
    assert sched.taker_fee(0.50, 100, "KXNFLGAME").amount == pytest.approx(1.75)
    # 1 contract at 50c: 0.07 * 0.25 = $0.0175 -> rounds UP to a cent.
    assert sched.taker_fee(0.50, 1, "KXNFLGAME").amount == pytest.approx(0.02)


def test_rounding_is_per_order_not_per_contract(sched):
    """A 100-lot rounds once. Rounding each contract separately would charge $1.00 instead of $0.44."""
    order = sched.taker_fee(0.10, 100, "KXNFLGAME").amount
    per_contract = 100 * sched.taker_fee(0.10, 1, "KXNFLGAME").amount
    assert order == pytest.approx(0.63)          # ceil(0.07 * 100 * 0.10 * 0.90) = ceil(0.63)
    assert per_contract == pytest.approx(1.00)
    assert order < per_contract, "per-contract rounding overstates the cost of every multi-contract order"


def test_a_boundary_value_is_not_pushed_up_a_whole_cent_by_float_error(sched):
    """0.07 * 4 * 0.5 * 0.5 == 0.07 exactly. Binary arithmetic must not turn that into 0.08."""
    assert sched.taker_fee(0.50, 4, "KXNFLGAME").amount == pytest.approx(0.07)


def test_fractional_contracts_are_supported_and_not_truncated(sched):
    """A weighted-average or partially-allocated position is genuinely fractional in this ledger."""
    a = sched.taker_fee(0.50, 37.5, "KXNFLGAME")
    b = sched.taker_fee(0.50, 37.0, "KXNFLGAME")
    assert a.is_known and a.amount == pytest.approx(0.66)     # ceil(0.07*37.5*0.25) = ceil(0.65625)
    assert b.amount == pytest.approx(0.65)                    # ceil(0.07*37*0.25)   = ceil(0.6475)
    assert a.amount != b.amount, "the fractional part was truncated away"


def test_the_series_fee_multiplier_is_honoured(sched):
    """A raised multiplier must raise the fee. Ignoring it silently under-charges every trade."""
    doubled = F.FeeSchedule(fee_type_by_series={"X": "quadratic"}, fee_multiplier_by_series={"X": 2})
    assert doubled.taker_fee(0.50, 100, "X").amount == pytest.approx(3.50)


def test_an_untradable_price_has_no_defined_fee(sched):
    for p in (0.0, 1.0, None, 1.5):
        q = sched.taker_fee(p, 10, "KXNFLGAME")
        assert not q.is_known and q.state == F.UNKNOWN


# ---- the unknown maker multiplier ------------------------------------------------------------------

def test_the_headline_nfl_series_charge_a_maker_fee(sched):
    """Passive entry on the markets this project actually studies is not free."""
    for s in ("KXNFLGAME", "KXNFLSPREAD", "KXNFLTOTAL"):
        assert sched.charges_maker_fee(s), f"{s} should be quadratic_with_maker_fees"


def test_the_maker_multiplier_is_unknown_and_stays_unknown(sched):
    """The API does not publish it. A plausible default here would invent free passive trades."""
    assert sched.maker_multiplier is None, "config must not carry a guessed maker multiplier"
    q = sched.maker_fee(0.50, 100, "KXNFLGAME")
    assert q.state == F.UNKNOWN and q.amount is None
    assert "sweep" in q.reason


def test_an_unknown_fee_refuses_to_yield_a_number(sched):
    with pytest.raises(F.FeeStateError):
        sched.maker_fee(0.50, 100, "KXNFLGAME").require()


def test_a_swept_maker_multiplier_is_labelled_as_a_hypothesis(sched):
    q = sched.maker_fee(0.50, 100, "KXNFLGAME", maker_multiplier=1.0)
    assert q.is_known and q.amount == pytest.approx(0.44)     # ceil(0.0175 * 1 * 100 * 0.25) = ceil(0.4375)
    assert "HYPOTHESIS" in q.basis, "a swept number must never read as a measured one"


def test_a_series_with_no_maker_fee_costs_zero_and_says_so(sched):
    taker_only = next(s for s, t in sched.fee_type_by_series.items() if t == F.FEE_TYPE_TAKER_ONLY)
    q = sched.maker_fee(0.50, 100, taker_only)
    assert q.is_known and q.amount == 0.0
    assert "no maker fee" in q.basis


def test_an_unregistered_series_is_degraded_not_free(sched):
    """A series we have never captured has an unknown regime, which is not the same as a zero fee."""
    assert sched.taker_fee(0.5, 10, "KXNOTAREALSERIES").state == F.DEGRADED
    assert sched.maker_fee(0.5, 10, "KXNOTAREALSERIES").state == F.DEGRADED


# ---- provenance ------------------------------------------------------------------------------------

def test_the_schedule_is_traceable_to_a_dated_source(sched):
    assert sched.schedule_id and sched.schedule_id != "unversioned"
    for k in ("primary_source", "source_label", "verified_at"):
        assert sched.provenance.get(k), f"the fee schedule must record {k}"


def test_the_config_declares_the_maker_state_as_unknown():
    with open(os.path.join(ROOT, "config", "kalshi_fee_schedule.json")) as f:
        d = json.load(f)
    assert d["maker"]["state"] == "UNKNOWN"
    assert d["maker"]["maker_multiplier"] is None
    assert d["taker"]["state"] == "KNOWN"


# ---- net executable EV -----------------------------------------------------------------------------

def test_net_ev_separates_gross_edge_from_costs(sched):
    """Displayed prices stay clean; the cost arithmetic lives here, named."""
    nev = F.net_executable_ev(0.66, 0.62, 100, sched, "KXNFLGAME")
    assert nev.gross_edge == pytest.approx(0.04)
    assert nev.gross_ev_dollars == pytest.approx(4.0)
    assert nev.estimated_fees == pytest.approx(1.65)          # ceil(0.07*100*0.62*0.38 = 1.6492) to the cent
    assert nev.net_ev_dollars == pytest.approx(2.35)
    assert nev.state == F.KNOWN


def test_transaction_costs_can_erase_a_gross_edge(sched):
    """The exact case the desk must be able to see: fair > ask, and the trade is still not worth doing."""
    nev = F.net_executable_ev(0.515, 0.50, 100, sched, "KXNFLGAME")
    assert nev.gross_ev_dollars > 0, "there is a gross edge"
    assert nev.net_ev_dollars < 0, "and it does not survive the fee"


def test_an_unknown_fee_makes_net_ev_unknown_not_zero_fee(sched):
    """The whole point. An unknown cost must never be quietly treated as no cost."""
    nev = F.net_executable_ev(0.66, 0.62, 100, sched, "KXNFLGAME", execution_style=F.MAKER)
    assert nev.net_ev_dollars is None
    assert nev.state == F.UNKNOWN
    assert nev.gross_edge is not None, "gross edge is still reportable; only the net is withheld"


def test_slippage_is_a_separate_named_term(sched):
    base = F.net_executable_ev(0.66, 0.62, 100, sched, "KXNFLGAME")
    slipped = F.net_executable_ev(0.66, 0.62, 100, sched, "KXNFLGAME", slippage_dollars=1.0)
    assert slipped.net_ev_dollars == pytest.approx(base.net_ev_dollars - 1.0)
    assert slipped.estimated_slippage_dollars == 1.0


def test_contracts_for_stake_is_the_kalshi_identity():
    assert F.contracts_for_stake(20, 0.50) == pytest.approx(40.0)
    assert F.contracts_for_stake(20, 0) == 0.0


# ---- the frozen H-019 sweep ------------------------------------------------------------------------

def test_the_frozen_passive_study_sweep_is_preserved():
    """H-019 rejected passive execution. Its published numbers must keep reproducing exactly."""
    assert F.MAKER_FEE_SWEEP == (0.0, 0.0025, 0.005, 0.01)
