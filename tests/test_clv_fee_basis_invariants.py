"""Regression: Kalshi fee-inclusive position display must not contaminate selection CLV.

A 50¢ exchange fill can appear as ~51.7¢ in the Kalshi UI after fees.
Neither the UI average-cost number nor an estimated fee-inclusive break-even
is a closing market quote. These tests protect quote-based CLV from that mix-up.
"""
from datetime import datetime, timezone
from pathlib import Path

import pytest

from nfl_edge.evaluation import clv as V
from nfl_edge.execution import fees as F


ROOT = Path(__file__).resolve().parents[1]
AS_OF = datetime(2026, 11, 3, tzinfo=timezone.utc)


def horizon(*, bid=0.50, ask=0.50, model_probability=0.60):
    return {
        "record_id": "synthetic-fee-basis",
        "ticker": "KXNFLTOTAL-TEST",
        "series_ticker": "KXNFLTOTAL",
        "horizon_label": "T-6h",
        "model_arm": "TEST",
        "contract_value": model_probability,
        "yes_bid": bid,
        "yes_ask": ask,
        "no_bid": 1.0 - ask,
        "no_ask": 1.0 - bid,
    }


def observed_close(*, bid=0.50, ask=0.50):
    mid = (bid + ask) / 2.0
    return {
        "close_id": "observed-pregame-quote",
        "close_status": "CLOSE_OK",
        "close_quality": "EXCELLENT",
        "close_age_seconds": 60.0,
        "yes_bid": bid,
        "yes_ask": ask,
        "no_bid": 1.0 - ask,
        "no_ask": 1.0 - bid,
        "mid": mid,
        "no_mid": 1.0 - mid,
    }


@pytest.mark.parametrize("model_probability,side", [(0.60, "YES"), (0.40, "NO")])
def test_fee_inclusive_ui_basis_is_not_market_movement(model_probability, side):
    schedule = F.load_fee_schedule(str(ROOT))
    # Example: a genuine 50¢ fill is shown as ~51.7¢ once transaction fees
    # are rolled into the *position cost basis*. That is NOT a new quote.
    ui_fee_inclusive_cost_basis = 0.5175
    assert ui_fee_inclusive_cost_basis > 0.50

    result = V.clv_record(
        horizon(model_probability=model_probability),
        observed_close(),
        schedule=schedule,
        as_of=AS_OF,
    )
    assert result["clv_status"] == "CLV_OK"
    assert result["model_side"] == side
    # Selection signal: same fee-exclusive quote at horizon and close => 0.
    assert result["clv_mid_toward_model"] == pytest.approx(0.0)
    # The hypothetical executable entry remains the raw 50¢ ASK.
    assert result["entry_executable_price"] == pytest.approx(0.50)
    assert result["clv_exec_toward_model"] == pytest.approx(0.0)
    # The fee is charged ONCE, and only in the separate fee-aware measure.
    fee = result["entry_fee_per_contract"]
    assert result["entry_fee_state"] == "KNOWN" and fee > 0
    assert result["clv_net_of_fee"] == pytest.approx(-fee)
    assert result["entry_break_even"] == pytest.approx(0.50 + fee)
    assert result["clv_mid_toward_model"] != pytest.approx(0.50 - ui_fee_inclusive_cost_basis)


def test_unchanged_market_with_a_spread_is_not_a_bad_selection_signal():
    schedule = F.load_fee_schedule(str(ROOT))
    r = V.clv_record(
        horizon(bid=0.48, ask=0.50),
        observed_close(bid=0.48, ask=0.50),
        schedule=schedule,
        as_of=AS_OF,
    )
    # Two identical books: mid-to-mid market movement is zero.
    assert r["clv_mid_toward_model"] == pytest.approx(0.0)
    # Buying at ASK and comparing to MID includes crossing the spread.
    assert r["clv_exec_toward_model"] == pytest.approx(-0.01)
    assert r["clv_net_of_fee"] == pytest.approx(-0.01 - r["entry_fee_per_contract"])


def test_a_real_one_cent_adverse_move_is_negative_before_fees():
    schedule = F.load_fee_schedule(str(ROOT))
    r = V.clv_record(
        horizon(),
        observed_close(bid=0.49, ask=0.49),
        schedule=schedule,
        as_of=AS_OF,
    )
    assert r["clv_mid_toward_model"] == pytest.approx(-0.01)
    assert r["clv_exec_toward_model"] == pytest.approx(-0.01)
    assert r["clv_net_of_fee"] == pytest.approx(-0.01 - r["entry_fee_per_contract"])
