"""Market/model synchronization: a later source must not be able to look like a model edge.

The failure these tests prevent is subtle and does not touch the price. Availability is cutoff-bounded, so the
CONTRACT VALUE cannot absorb later news. But the research layer segments on context fields, and one of those
fields (the injury report) is retrieved after the capture it is scored against. Mine a slice on it and you get:

    "the model beats the market on Doubtful players"

which, on asynchronous rows, means nothing more than "we read the designation before the quote could price it".
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.evaluation import scorecard_v3 as S3                  # noqa: E402
from nfl_edge.research import hypothesis_registry_v2 as HR          # noqa: E402
from nfl_edge.shadow_v2 import pit                                  # noqa: E402

CUT = "2026-09-11T01:05:27+00:00"
EARLIER = "2026-09-11T00:30:00+00:00"
LATER = "2026-09-11T01:42:41+00:00"


# ----------------------------------------------------------------------------------- the classifier itself
def test_a_frontier_past_the_market_cutoff_is_asynchronous():
    s = pit.synchronization(market_observable_through=CUT, model_information_frontier=LATER)
    assert s["synchronization_state"] == pit.ASYNC_MODEL_NEWER
    assert s["information_skew_seconds"] == pytest.approx(2234.0, abs=1.0)
    assert "newer information rather than better modelling" in s["synchronization_reason"]


def test_a_frontier_at_or_before_the_cutoff_is_synchronized():
    assert pit.synchronization(market_observable_through=CUT,
                               model_information_frontier=EARLIER)["synchronization_state"] == pit.SYNCHRONIZED
    assert pit.synchronization(market_observable_through=CUT,
                               model_information_frontier=CUT)["synchronization_state"] == pit.SYNCHRONIZED


def test_missing_timing_is_its_own_state_and_never_silently_synchronized():
    for kw in ({"market_observable_through": None, "model_information_frontier": LATER},
               {"market_observable_through": CUT, "model_information_frontier": None}):
        s = pit.synchronization(**kw)
        assert s["synchronization_state"] == pit.UNKNOWN_TIMING and s["information_skew_seconds"] is None


def test_a_stale_quote_is_not_by_itself_asynchronous():
    """The cutoff is the last instant the market was OBSERVABLE, not the last time its price moved."""
    s = pit.synchronization(market_observable_through=CUT, model_information_frontier=EARLIER,
                            market_observed_at="2026-09-10T19:00:00+00:00")
    assert s["synchronization_state"] == pit.SYNCHRONIZED
    assert s["market_observed_at"].startswith("2026-09-10T19:00")


# ------------------------------------------------------------------------- the scorecard keeps them apart
def _row(i, state, injury, cv=0.6, mid=0.5, settled=1.0):
    """The scorecard recomputes Brier from the frozen prices, so an effect is expressed as cv vs mid."""
    return {"evidence_class": "PROSPECTIVE_FROZEN", "synchronization_state": state,
            "information_skew_seconds": (2234.0 if state == pit.ASYNC_MODEL_NEWER else 0.0),
            "contract_value": cv, "h_mid": mid, "settled_yes": settled, "game_id": f"G{i % 4}",
            "ctx_injury_state": injury, "model_arm": "DATA_PLAYER_DIST", "family_group": "player_rec_yards",
            "record_id": f"R{i}"}


def test_synchronized_and_asynchronous_rows_are_scored_in_separate_buckets():
    rows = [_row(i, pit.SYNCHRONIZED, "LISTED") for i in range(10)] + \
           [_row(i, pit.ASYNC_MODEL_NEWER, "LISTED") for i in range(10, 30)]
    sc = S3.build(rows, min_segment_n=5)
    by = sc["by_synchronization"]["PROSPECTIVE_FROZEN"]
    assert set(by) == {pit.SYNCHRONIZED, pit.ASYNC_MODEL_NEWER}
    assert by[pit.SYNCHRONIZED]["n_rows"] == 10 and by[pit.ASYNC_MODEL_NEWER]["n_rows"] == 20
    assert sc["synchronization"]["counts"] == {pit.ASYNC_MODEL_NEWER: 20, pit.SYNCHRONIZED: 10}
    assert sc["synchronization"]["with_probability"][pit.SYNCHRONIZED] == 10
    assert sc["synchronization"]["skew_seconds"]["max"] == 2234.0
    assert sc["synchronization"]["synchronized_edge_basis"] == "by_synchronization.PROSPECTIVE_FROZEN.SYNCHRONIZED"


def test_synchronization_state_is_a_segment_so_pooling_is_visible():
    rows = [_row(i, pit.SYNCHRONIZED, "LISTED") for i in range(6)] + \
           [_row(i, pit.ASYNC_MODEL_NEWER, "LISTED") for i in range(6, 12)]
    segs = S3.build(rows, min_segment_n=5)["by_evidence_class"]["PROSPECTIVE_FROZEN"]["segments"]
    assert set(segs["synchronization_state"]) == {pit.SYNCHRONIZED, pit.ASYNC_MODEL_NEWER}


# ------------------------------------------------- THE MISSION'S TEST: no synchronized edge from later news
def test_a_later_injury_snapshot_cannot_create_a_synchronized_doubtful_hypothesis():
    """Every "Doubtful beats the market" row is asynchronous. No candidate may be mined from it."""
    rows = [_row(i, pit.ASYNC_MODEL_NEWER, "LISTED", cv=0.95) for i in range(40)]
    sc = S3.build(rows, min_segment_n=5)
    cands = HR.candidates_from_scorecard(sc, season=2026, week=1, min_n=5)
    assert cands == [], "an asynchronous slice was mined as a hypothesis candidate"
    # and the evidence is not destroyed -- it is scored, in its own bucket, where it cannot be misread
    async_block = sc["by_synchronization"]["PROSPECTIVE_FROZEN"][pit.ASYNC_MODEL_NEWER]
    assert async_block["n_rows"] == 40
    assert "ctx_injury_state" in async_block["segments"]


def test_the_same_slice_IS_mined_when_the_rows_are_synchronized():
    """The gate must block asynchrony, not block hypothesis generation."""
    rows = [_row(i, pit.SYNCHRONIZED, "LISTED", cv=0.95) for i in range(40)]
    cands = HR.candidates_from_scorecard(S3.build(rows, min_segment_n=5), season=2026, week=1, min_n=5)
    assert cands, "synchronized evidence must still generate candidates"
    assert all(c["synchronization_basis"] == pit.SYNCHRONIZED for c in cands)
    assert any(c["market_family"] == "ctx_injury_state" for c in cands)


def test_mixing_cannot_smuggle_asynchronous_rows_into_a_candidate():
    """20 synchronized rows with no effect, 200 asynchronous with a huge one: the candidate must see only the 20."""
    # synchronized: the model agrees with the market exactly, so its slice has no effect at all.
    # asynchronous: the model is far better, because it read the designation the quote had not priced.
    rows = [_row(i, pit.SYNCHRONIZED, "LISTED", cv=0.5, mid=0.5) for i in range(20)] + \
           [_row(i, pit.ASYNC_MODEL_NEWER, "LISTED", cv=0.99, mid=0.5) for i in range(20, 220)]
    cands = HR.candidates_from_scorecard(S3.build(rows, min_segment_n=5), season=2026, week=1, min_n=5)
    inj = [c for c in cands if c["market_family"] == "ctx_injury_state"]
    assert inj, "the synchronized slice should still be reported"
    assert inj[0]["sample_size"] == 20, "the candidate pooled asynchronous rows into its sample"
    assert abs(inj[0]["effect_size"]) < 1e-6, "the effect came from the asynchronous rows"
