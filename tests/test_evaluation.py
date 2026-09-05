"""Derived evaluation records must never mutate a prediction, and never invent a close."""
import pytest

from nfl_edge.shadow.evaluation import MISSING_CLOSE, evaluate, model_direction, pick_close


def pred(**kw):
    d = {"prediction_id": "p1", "run_id": "r1", "ticker": "T", "model_version": "v",
         "yes_bid": 0.40, "yes_ask": 0.44, "model_contract_value": 0.50}
    d.update(kw)
    return d


def test_a_missing_close_is_recorded_not_filled_in():
    e = evaluate(pred(), None)
    assert e.close_status == MISSING_CLOSE
    assert e.close_mid is None and e.signed_clv_mid is None


def test_post_kickoff_quotes_are_never_chosen_as_the_close():
    quotes = [{"observed_ts": 100, "yes_bid": 0.4, "yes_ask": 0.44},
              {"observed_ts": 250, "yes_bid": 0.5, "yes_ask": 0.54}]   # after kickoff
    got = pick_close(quotes, kickoff_ts=200)
    assert got["observed_ts"] == 100
    assert pick_close([quotes[1]], kickoff_ts=200) is None


def test_the_original_prediction_is_not_mutated():
    p = pred()
    before = dict(p)
    evaluate(p, {"yes_bid": 0.5, "yes_ask": 0.54})
    assert p == before


def test_unchanged_and_no_view_are_never_scored_as_movement():
    e = evaluate(pred(), {"yes_bid": 0.40, "yes_ask": 0.44})
    assert e.movement == "unchanged"
    flat = evaluate(pred(model_contract_value=0.42), {"yes_bid": 0.50, "yes_ask": 0.54})
    assert flat.movement == "no_view", "a model agreeing with the mid has no direction to move toward"


def test_signed_clv_follows_our_view_not_the_move():
    up = evaluate(pred(model_contract_value=0.60), {"yes_bid": 0.46, "yes_ask": 0.50})
    assert up.movement == "toward" and up.signed_clv_mid > 0
    dn = evaluate(pred(model_contract_value=0.30), {"yes_bid": 0.46, "yes_ask": 0.50})
    assert dn.movement == "away" and dn.signed_clv_mid < 0


def test_executable_clv_uses_the_side_we_would_have_crossed():
    e = evaluate(pred(model_contract_value=0.60), {"yes_bid": 0.46, "yes_ask": 0.50})
    assert e.model_direction == "yes"
    assert e.signed_clv_executable == pytest.approx(0.50 - 0.44)


def test_model_direction_handles_exact_agreement():
    assert model_direction(0.42, 0.42) == "none"
    assert model_direction(None, 0.42) == "none"
