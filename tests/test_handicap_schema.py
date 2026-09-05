"""The recommendation ledger's guarantees, pinned.

Everything the eventual experiment depends on is enforced here rather than trusted: immutability, the
separation of recommendation from execution, the exclusion of test data from reports, and the internal
consistency checks that stop a record being committed in a state that cannot later be scored.
"""
import json
import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import schema as S  # noqa: E402
from nfl_edge.handicap import store        # noqa: E402


def _rec(**kw):
    d = dict(
        recommendation_id="rec_test0000000000001", schema_version=S.HANDICAP_SCHEMA_VERSION,
        created_at="2026-09-05T00:00:00+00:00", handicap_run_id="20260905T000000Z", packet_sha="abc",
        season=2026, week=1, game_id="2026_01_NE_SEA", kickoff_utc="2026-09-10T00:20:00+00:00",
        market_ticker="KXNFLGAME-26SEP09NESEA-SEA", market_family="GAME_WINNER", side="YES",
        yes_bid=0.60, yes_ask=0.62, no_bid=0.38, no_ask=0.40, mid=0.61,
        decision=S.RECOMMENDED, grade="B", bet_up_to_probability=0.65, recommended_stake=25,
        primary_thesis="thesis",
    )
    d.update(kw)
    return d


# ---- validation ------------------------------------------------------------------------------------

def test_valid_recommendation_passes():
    assert S.validate_recommendation(_rec()) == []


def test_recommended_requires_a_price_ceiling():
    with pytest.raises(S.ValidationError, match="bet_up_to_probability"):
        S.validate_recommendation(_rec(bet_up_to_probability=None))


def test_recommended_requires_a_thesis():
    with pytest.raises(S.ValidationError, match="primary_thesis"):
        S.validate_recommendation(_rec(primary_thesis=""))


def test_recommended_may_not_carry_the_pass_grade():
    with pytest.raises(S.ValidationError, match="grade"):
        S.validate_recommendation(_rec(grade="PASS"))


def test_inverted_probability_band_is_refused():
    with pytest.raises(S.ValidationError, match="exceeds"):
        S.validate_recommendation(_rec(probability_low=0.7, probability_high=0.3))


def test_probability_mid_must_sit_inside_the_band():
    with pytest.raises(S.ValidationError, match="above probability_high"):
        S.validate_recommendation(_rec(probability_low=0.3, probability_mid=0.9, probability_high=0.5))


def test_probabilities_outside_zero_one_are_refused():
    with pytest.raises(S.ValidationError, match="probability in"):
        S.validate_recommendation(_rec(model_probability=1.4))


def test_stake_must_be_whole_dollars():
    """The user bets whole dollars; a fractional stake cannot be executed as recorded."""
    with pytest.raises(S.ValidationError, match="whole-dollar"):
        S.validate_recommendation(_rec(recommended_stake=12.5))


def test_unactionable_ceiling_warns_but_does_not_block():
    """A ceiling below the ask is a real inconsistency, but the handicapper may be posting a resting view."""
    warns = S.validate_recommendation(_rec(bet_up_to_probability=0.50, yes_ask=0.62))
    assert any("not currently actionable" in w for w in warns)


def test_unknown_reasoning_tag_warns_rather_than_blocks():
    warns = S.validate_recommendation(_rec(reasoning_tags=["SOMETHING_NEW"]))
    assert any("uncontrolled reasoning_tag" in w for w in warns)


def test_pass_without_a_reason_warns():
    warns = S.validate_recommendation(_rec(decision=S.PASS, grade="PASS", primary_thesis="",
                                           bet_up_to_probability=None))
    assert any("PASS without a stated reason" in w for w in warns)


def test_bad_decision_and_side_are_refused():
    with pytest.raises(S.ValidationError):
        S.validate_recommendation(_rec(decision="MAYBE"))
    with pytest.raises(S.ValidationError):
        S.validate_recommendation(_rec(side="BOTH"))


def test_execution_requires_a_positive_whole_dollar_stake():
    ex = dict(execution_id="exe_1", recommendation_id="rec_1", executed_at="x", side="YES",
              actual_price=0.5, stake=0)
    with pytest.raises(S.ValidationError, match="positive whole-dollar"):
        S.validate_execution(ex)


def test_postmortem_requires_a_known_category():
    pm = dict(postmortem_id="pmt_1", recommendation_id="rec_1", written_at="x",
              categories=["NOT_A_CATEGORY"], confidence="low")
    with pytest.raises(S.ValidationError, match="unknown postmortem categories"):
        S.validate_postmortem(pm)


def test_pass_reasons_are_controlled_tags():
    """The commonest reason to decline a bet must have a name, or every pass lands in the unknown bucket."""
    for tag in ("MARKET_ALREADY_PRICED", "PRICE_TOO_EXPENSIVE", "AWAIT_INACTIVE_RELEASE"):
        assert tag in S.CORE_REASONING_TAGS


# ---- immutability ----------------------------------------------------------------------------------

def test_write_record_refuses_to_overwrite():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "r.json")
        S.write_record(p, {"a": 1})
        with pytest.raises(S.ValidationError, match="immutable"):
            S.write_record(p, {"a": 2})
        assert json.load(open(p)) == {"a": 1}, "the original record was modified"


def test_amendment_supersedes_without_deleting():
    original = _rec(recommendation_id="rec_orig")
    revised = _rec(recommendation_id="rec_new", amends="rec_orig", bet_up_to_probability=0.55)
    chain = store.latest_amendment_chain([original, revised])
    ids = {c["recommendation_id"] for c in chain}
    assert ids == {"rec_new"}, "the amended record should not also be counted"
    assert chain[0]["_superseded_ids"] == ["rec_orig"], "the original must remain traceable"


# ---- test-record isolation -------------------------------------------------------------------------

def test_test_only_records_are_excluded_by_default():
    with tempfile.TemporaryDirectory() as d:
        for i, flag in enumerate([True, False]):
            rec = _rec(recommendation_id=f"rec_{i}", test_only=flag)
            S.write_record(store.record_path(d, "recommendations", 2026, 1, rec["recommendation_id"]), rec)
        assert len(store.read_kind(d, "recommendations")) == 1
        assert len(store.read_kind(d, "recommendations", include_test=True)) == 2


def test_one_record_per_file_paths_do_not_collide():
    """The conflict-avoidance property: two records never resolve to the same path."""
    a = store.record_path("/r", "recommendations", 2026, 1, "rec_a")
    b = store.record_path("/r", "recommendations", 2026, 1, "rec_b")
    assert a != b and a.endswith("week_01/rec_a.json")


def test_unknown_record_kind_is_rejected():
    with pytest.raises(ValueError, match="unknown record kind"):
        store.week_dir("/r", "predictions", 2026, 1)
