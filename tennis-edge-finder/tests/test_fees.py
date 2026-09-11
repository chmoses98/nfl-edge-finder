import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tennis_edge.pricing.fees import taker_fee, maker_fee, FeeSchedule, expected_value, breakeven_price


def test_taker_fee_peaks_at_50_cents_and_rounds_up():
    assert taker_fee(0.5, 100) == 1.75
    assert taker_fee(0.5, 1) == 0.02          # 0.0175 -> ceil to cent
    assert taker_fee(0.9, 100) == 0.63
    assert taker_fee(0.5, 100) > taker_fee(0.7, 100) > taker_fee(0.9, 100)


def test_maker_fee_only_on_maker_series():
    assert maker_fee(0.5, 100) == 0.0
    assert maker_fee(0.5, 100, FeeSchedule("quadratic_with_maker_fees")) == 0.44   # 0.4375 -> 0.44


def test_ev_separates_raw_and_net():
    evs = expected_value(0.60, yes_ask=0.55, no_ask=0.47, contracts=100)
    yes = [e for e in evs if e.side == "YES"][0]
    assert abs(yes.raw_edge - 0.05) < 1e-12 and yes.ev_per_contract_after_fees < yes.raw_edge
    no = [e for e in evs if e.side == "NO"][0]
    assert no.raw_edge < 0


def test_breakeven_below_fair():
    b = breakeven_price(0.60)
    assert 0.55 < b < 0.60
