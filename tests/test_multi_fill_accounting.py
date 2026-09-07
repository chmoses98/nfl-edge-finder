"""Multiple fills, and the two bugs that made a two-fill position report the wrong profit.

The worked example from the desk, used throughout:

    Recommendation:  BUY YES up to 58%
    Actual fills:    $20 at 54%   ->  37.037... contracts
                     $30 at 55%   ->  54.545... contracts

    On a WIN:  20*(1-0.54)/0.54 + 30*(1-0.55)/0.55  =  17.0370 + 24.5455  =  $41.58
    On a LOSS: -$50

Two independent defects produced the wrong answer before this session:

  1. `attach_evaluations.py` took `(execs.get(rid) or [None])[0]` -- the FIRST fill only. The $30 at 55c
     simply did not exist as far as the evaluation was concerned.

  2. `scorecard._headline` looped over executions and added the evaluation-level `pnl` inside the loop, so a
     two-fill recommendation contributed its P/L twice while its stake summed correctly. The ROI was
     therefore wrong in the most flattering possible direction.

Both are pinned here with exact arithmetic, because "roughly right" is how a doubled P/L survives review.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import schema as S            # noqa: E402
from nfl_edge.handicap import scorecard as SC        # noqa: E402
from nfl_edge.handicap.evaluate import aggregate_executions, evaluate  # noqa: E402

KICKOFF = "2026-09-10T00:20:00+00:00"


def rec(rid="rec_mf1", side="YES", **kw):
    d = dict(recommendation_id=rid, side=side, decision=S.RECOMMENDED, kickoff_utc=KICKOFF,
             market_ticker="KXNFLGAME-26SEP09NESEA-SEA", market_family="GAME_WINNER",
             game_id="2026_01_NE_SEA", grade="B+", yes_ask=0.58, mid=0.56,
             probability_mid=0.62, model_probability=0.61, recommended_stake=50)
    d.update(kw)
    return d


def fill(price, stake, rid="rec_mf1", **kw):
    d = dict(execution_id=f"exe_{price}_{stake}", recommendation_id=rid, executed_at="2026-09-09T18:00:00Z",
             side="YES", actual_price=price, stake=stake, contracts=stake / price)
    d.update(kw)
    return d


TWO_FILLS = [fill(0.54, 20), fill(0.55, 30)]
CLOSE = [{"observed_at": "2026-09-10T00:00:00+00:00", "yes_bid": 0.60, "yes_ask": 0.62, "mid": 0.61}]


# ---- fill-level arithmetic -------------------------------------------------------------------------

def test_two_fills_at_different_prices_produce_exact_win_pnl():
    agg = aggregate_executions(TWO_FILLS, won=True)
    assert agg["gross_dollars_staked"] == pytest.approx(50.0)
    assert agg["contracts"] == pytest.approx(20 / 0.54 + 30 / 0.55)
    assert agg["gross_pnl"] == pytest.approx(41.58, abs=0.01)


def test_two_fills_lose_exactly_what_was_staked():
    agg = aggregate_executions(TWO_FILLS, won=False)
    assert agg["gross_pnl"] == pytest.approx(-50.0)
    assert agg["net_roi"] == pytest.approx(-1.0)


def test_the_blended_price_is_the_one_that_reproduces_the_aggregate():
    """`average_execution_price` is stake / contracts, not the mean of the quoted prices.

    That distinction matters. Defined this way the blend is the single price that buys exactly the same
    number of contracts for the same money, so it reproduces the aggregate P/L exactly -- which is what
    makes it a legitimate basis for slippage. The naive dollar-weighted mean of the two fill prices does
    NOT have that property, and using it would put a small error into every slippage number.

    It is still DERIVED, and no execution record carries it. It is a summary of two real fills, never a
    substitute for them.
    """
    agg = aggregate_executions(TWO_FILLS, won=True)
    blended = agg["average_execution_price"]
    assert 0.54 < blended < 0.55, "the blend must sit between the two real fills"

    at_blend = aggregate_executions([fill(blended, 50)], won=True)
    assert at_blend["gross_pnl"] == pytest.approx(agg["gross_pnl"], abs=0.005), \
        "the derived blend must reproduce the aggregate exactly, or slippage is measured against a fiction"

    naive = (20 * 0.54 + 30 * 0.55) / 50.0
    assert blended != pytest.approx(naive, abs=1e-5), \
        "the blend must be stake/contracts, not the mean of the quoted prices"
    assert {e["actual_price"] for e in TWO_FILLS} == {0.54, 0.55}, \
        "no execution record may carry the derived price"


def test_an_unsettled_position_reports_stake_but_no_pnl():
    """Zero and unknown are different. A zero P/L on an unsettled bet reads like a measurement."""
    agg = aggregate_executions(TWO_FILLS, won=None)
    assert agg["gross_dollars_staked"] == pytest.approx(50.0)
    assert agg["gross_pnl"] is None and agg["net_pnl"] is None and agg["net_roi"] is None


def test_contracts_are_derived_from_stake_when_not_recorded():
    bare = [dict(execution_id="e", recommendation_id="r", executed_at="x", side="YES",
                 actual_price=0.50, stake=20)]
    assert aggregate_executions(bare, won=True)["contracts"] == pytest.approx(40.0)


def test_fractional_contract_quantities_are_handled_exactly():
    agg = aggregate_executions([fill(0.40, 13.5)], won=True)
    assert agg["contracts"] == pytest.approx(33.75)
    assert agg["gross_pnl"] == pytest.approx(33.75 * 0.60, abs=0.01)


# ---- fees ------------------------------------------------------------------------------------------

def test_actual_fees_are_subtracted_from_net_but_not_from_gross():
    fills = [fill(0.54, 20, fees_paid=0.35), fill(0.55, 30, fees_paid=0.52)]
    agg = aggregate_executions(fills, won=True)
    assert agg["gross_pnl"] == pytest.approx(41.58, abs=0.01)
    assert agg["fees_paid"] == pytest.approx(0.87)
    assert agg["net_pnl"] == pytest.approx(40.71, abs=0.01)
    assert agg["fees_basis"] == "ACTUAL"


def test_estimated_fees_never_reduce_realised_pnl():
    """An estimate is a fine input to a forecast and an unacceptable input to a realised-P/L claim."""
    fills = [fill(0.54, 20, fees_paid=0.35, fees_are_estimated=True)]
    agg = aggregate_executions(fills, won=True)
    assert agg["fees_estimated"] == pytest.approx(0.35)
    assert agg["fees_paid"] is None
    assert agg["net_pnl"] == pytest.approx(agg["gross_pnl"]), "an estimate must not move net P/L"
    assert agg["fees_basis"] == "ESTIMATED"


def test_a_mixed_basis_is_reported_as_mixed():
    fills = [fill(0.54, 20, fees_paid=0.35), fill(0.55, 30, fees_paid=0.52, fees_are_estimated=True)]
    agg = aggregate_executions(fills, won=True)
    assert agg["fees_basis"] == "MIXED"
    assert agg["fees_paid"] == pytest.approx(0.35), "only the charged fee reduces net P/L"
    assert agg["net_pnl"] == pytest.approx(agg["gross_pnl"] - 0.35, abs=0.01)


def test_no_fee_information_is_none_not_zero():
    agg = aggregate_executions(TWO_FILLS, won=True)
    assert agg["fees_paid"] is None and agg["fees_basis"] == "NONE"


# ---- the evaluation record -------------------------------------------------------------------------

def test_evaluate_uses_every_fill():
    ev = evaluate(rec(), CLOSE, settlement=1.0, executions=TWO_FILLS)
    assert ev["n_executions"] == 2
    assert ev["gross_dollars_staked"] == pytest.approx(50.0)
    assert ev["gross_pnl"] == pytest.approx(41.58, abs=0.01)
    assert ev["pnl"] == ev["gross_pnl"], "the legacy `pnl` field must remain an exact alias of gross_pnl"


def test_evaluate_records_entry_slippage_against_the_recommendation_ask():
    """We recommended at a 0.58 ask and filled at ~0.545, so we did BETTER than the recorded price."""
    ev = evaluate(rec(), CLOSE, settlement=1.0, executions=TWO_FILLS)
    assert ev["entry_slippage"] < 0
    assert ev["entry_slippage"] == pytest.approx(ev["average_execution_price"] - 0.58, abs=1e-6)


def test_clv_is_unchanged_by_fees():
    """CLV asks whether the market moved toward us. Costs ask whether the bankroll grew. Different questions."""
    plain = evaluate(rec(), CLOSE, settlement=1.0, executions=TWO_FILLS)
    feed = evaluate(rec(), CLOSE, settlement=1.0,
                    executions=[fill(0.54, 20, fees_paid=5.0), fill(0.55, 30, fees_paid=5.0)])
    assert plain["clv"] == feed["clv"]
    assert plain["clv_executable"] == feed["clv_executable"]
    assert feed["net_pnl"] < feed["gross_pnl"], "the fee must still show up somewhere"


def test_passing_both_execution_shapes_is_an_error_not_a_guess():
    with pytest.raises(ValueError, match="not both"):
        evaluate(rec(), CLOSE, settlement=1.0, executions=TWO_FILLS, execution=TWO_FILLS[0])


def test_the_evaluation_record_validates():
    ev = evaluate(rec(), CLOSE, settlement=1.0, executions=[fill(0.54, 20, fees_paid=0.35)])
    assert S.validate_evaluation(ev) == []


def test_a_net_pnl_that_disagrees_with_gross_minus_fees_is_refused():
    """The three fields exist to be cross-checkable. If they disagree, one was typed rather than computed."""
    with pytest.raises(S.ValidationError, match="does not equal"):
        S.validate_evaluation({"evaluation_id": "e", "recommendation_id": "r", "evaluated_at": "x",
                               "gross_pnl": 41.58, "fees_paid": 0.87, "net_pnl": 41.58})


# ---- the scorecard, which is where the double-count lived ------------------------------------------

def _scorecard(recs, evals, execs):
    return SC.build_scorecard(recs, evals, execs)


def test_scorecard_counts_pnl_once_per_recommendation_not_once_per_fill():
    """THE regression. Two fills previously contributed the position's P/L twice."""
    r = rec()
    ev = evaluate(r, CLOSE, settlement=1.0, executions=TWO_FILLS)
    out = _scorecard([r], [ev], TWO_FILLS)
    head = out["headline"]
    assert head["n_fills"] == 2, "both fills must be visible"
    assert head["dollars_staked"] == pytest.approx(50.0)
    assert head["gross_pnl"] == pytest.approx(41.58, abs=0.01), "P/L must be counted ONCE"
    assert head["gross_roi"] == pytest.approx(41.58 / 50.0, abs=0.001)


def test_a_one_fill_and_a_two_fill_position_are_scored_consistently():
    """If the double-count were still present, splitting a fill in two would inflate the ROI."""
    single = rec("rec_one")
    ev_single = evaluate(single, CLOSE, settlement=1.0, executions=[fill(0.50, 50, rid="rec_one")])
    one = _scorecard([single], [ev_single], [fill(0.50, 50, rid="rec_one")])["headline"]

    split = rec("rec_two")
    fills = [fill(0.50, 25, rid="rec_two"), fill(0.50, 25, rid="rec_two")]
    fills[1]["execution_id"] = "exe_second"
    ev_split = evaluate(split, CLOSE, settlement=1.0, executions=fills)
    two = _scorecard([split], [ev_split], fills)["headline"]

    assert one["gross_pnl"] == pytest.approx(two["gross_pnl"], abs=0.01)
    assert one["gross_roi"] == pytest.approx(two["gross_roi"], abs=0.0001)


def test_scorecard_separates_gross_and_net_roi():
    r = rec()
    fills = [fill(0.54, 20, fees_paid=0.35), fill(0.55, 30, fees_paid=0.52)]
    ev = evaluate(r, CLOSE, settlement=1.0, executions=fills)
    head = _scorecard([r], [ev], fills)["headline"]
    assert head["total_fees_paid"] == pytest.approx(0.87)
    assert head["net_pnl"] == pytest.approx(head["gross_pnl"] - 0.87, abs=0.01)
    assert head["net_roi"] < head["gross_roi"]
    assert head["fees_basis"] == "ACTUAL"


def test_scorecard_reports_how_many_recommendations_were_actually_executed():
    taken, not_taken = rec("rec_a"), rec("rec_b")
    evs = [evaluate(taken, CLOSE, settlement=1.0, executions=[fill(0.50, 20, rid="rec_a")]),
           evaluate(not_taken, CLOSE, settlement=0.0, executions=[])]
    head = _scorecard([taken, not_taken], evs, [fill(0.50, 20, rid="rec_a")])["headline"]
    assert head["n_recommendations_executed"] == 1
    assert head["execution_rate"] == pytest.approx(0.5)


def test_an_underpowered_sample_says_so():
    r = rec()
    ev = evaluate(r, CLOSE, settlement=1.0, executions=TWO_FILLS)
    out = _scorecard([r], [ev], TWO_FILLS)
    assert out["power"]["verdict"] == "UNDERPOWERED"
    assert out["power"]["n_resolved_recommended"] == 1


def test_an_empty_ledger_says_empty_rather_than_printing_zeros():
    out = _scorecard([], [], [])
    assert out["status"] == "NO RESOLVED RECOMMENDATIONS"
    assert out["breakdowns"] == {}
    assert out["power"]["verdict"] == "EMPTY"


def test_exposure_is_reported_by_game_and_by_correlation_group():
    a = rec("rec_a", correlation_group="2026_01_NE_SEA::SCORING_UP", recommended_stake=20)
    b = rec("rec_b", correlation_group="2026_01_NE_SEA::SCORING_UP", recommended_stake=30)
    c = rec("rec_c", game_id="2026_01_KC_BUF", correlation_group="2026_01_KC_BUF::SCORING_UP",
            recommended_stake=15)
    out = _scorecard([a, b, c], [], [])
    assert out["exposure"]["by_game"]["2026_01_NE_SEA"]["recommended_stake"] == pytest.approx(50.0)
    assert out["exposure"]["max_correlation_group_recommended_stake"] == pytest.approx(50.0)


def test_gate_rejections_are_unavailable_rather_than_zero_when_not_supplied():
    """No gate data and no gate rejections look identical and mean opposite things."""
    assert _scorecard([], [], [])["gate_activity"]["available"] is False
    with_gates = SC.build_scorecard([], [], [], decision_gates=[
        {"overall": "FAIL", "gates": {"decision_time_quote_freshness": {"status": "FAIL"}}}])
    assert with_gates["gate_activity"]["available"] is True
    assert with_gates["gate_activity"]["counts"]["decision_time_quote_freshness_FAIL"] == 1
