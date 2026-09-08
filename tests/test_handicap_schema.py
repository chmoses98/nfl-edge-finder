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
    """A COMPLETE RECOMMENDED record -- the professional minimum, not the parser minimum.

    Every field here is one the schema now requires before a record may ask the user to risk money. The
    fixture is deliberately the full thing: a test that starts from an under-specified record and passes
    proves only that the validator was not looking.
    """
    d = dict(
        recommendation_id="rec_test0000000000001", schema_version=S.HANDICAP_SCHEMA_VERSION,
        created_at="2026-09-05T00:00:00+00:00", handicap_run_id="20260905T000000Z", packet_sha="abc",
        season=2026, week=1, game_id="2026_01_NE_SEA", kickoff_utc="2026-09-10T00:20:00+00:00",
        market_ticker="KXNFLGAME-26SEP09NESEA-SEA", market_family="GAME_WINNER", side="YES",
        yes_bid=0.60, yes_ask=0.62, no_bid=0.38, no_ask=0.40, mid=0.61,
        market_timestamp="2026-09-05T00:00:00+00:00", minutes_to_kickoff=7220.0,
        support_state=S.SUPPORT_SUPPORTED, model_version="shadow-0.4.0", artifact_hash="deadbeef",
        model_probability=0.64,
        probability_low=0.60, probability_mid=0.66, probability_high=0.72,
        decision=S.RECOMMENDED, grade="B", bet_up_to_probability=0.65,
        proposed_stake=25, recommended_stake=25,
        primary_thesis="thesis",
        key_supporting_factors=["a"], counterarguments=["b"], uncertainties=["c"],
        source_freshness={"shadow_snapshot": "2026-09-05T00:00:00+00:00"},
    )
    d.update(kw)
    return d


def _pass(**kw):
    """A PASS record. Deliberately allowed to be much thinner than a RECOMMENDED one."""
    return _rec(decision=S.PASS, grade="PASS", bet_up_to_probability=None,
                recommended_stake=None, proposed_stake=None, **kw)


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


def test_ask_above_the_ceiling_is_refused_not_warned():
    """The ceiling is a ceiling.

    This was a warning. It is now a hard failure, because the canonical ledger must never be able to record
    "BET up to 0.58" while the book is asking 0.61 -- that is an instruction nobody should follow, preserved
    forever in an immutable record.
    """
    with pytest.raises(S.ValidationError, match="NOT ACTIONABLE"):
        S.validate_recommendation(_rec(bet_up_to_probability=0.50, yes_ask=0.62))


def test_ceiling_exactly_at_the_ask_is_actionable():
    """At the ask is payable. Only ABOVE the ceiling is refused."""
    assert S.validate_recommendation(_rec(bet_up_to_probability=0.62, yes_ask=0.62)) == []


def test_the_no_side_is_checked_against_the_no_ask():
    """A NO position pays the NO ask. Checking it against the YES ask would gate the wrong number."""
    with pytest.raises(S.ValidationError, match="NOT ACTIONABLE"):
        S.validate_recommendation(_rec(side="NO", no_ask=0.40, bet_up_to_probability=0.35))
    assert S.validate_recommendation(_rec(side="NO", no_ask=0.40, bet_up_to_probability=0.45)) == []


def test_recommended_without_an_executable_ask_is_refused():
    """A midpoint is not a price you can pay, and is not accepted in place of one."""
    with pytest.raises(S.ValidationError, match="executable YES ask"):
        S.validate_recommendation(_rec(yes_ask=None, mid=0.61))


def test_unknown_reasoning_tag_warns_rather_than_blocks():
    warns = S.validate_recommendation(_rec(reasoning_tags=["SOMETHING_NEW"]))
    assert any("uncontrolled reasoning_tag" in w for w in warns)


def test_pass_without_a_reason_warns():
    warns = S.validate_recommendation(_pass(primary_thesis=""))
    assert any("PASS without a stated reason" in w for w in warns)


def test_bad_decision_and_side_are_refused():
    with pytest.raises(S.ValidationError):
        S.validate_recommendation(_rec(decision="MAYBE"))
    with pytest.raises(S.ValidationError):
        S.validate_recommendation(_rec(side="BOTH"))


def test_execution_requires_a_positive_stake():
    ex = dict(execution_id="exe_1", recommendation_id="rec_1", executed_at="x", side="YES",
              actual_price=0.5, stake=0)
    with pytest.raises(S.ValidationError, match="positive dollar amount"):
        S.validate_execution(ex)


def test_execution_stake_may_be_fractional():
    """A partial fill is not a whole number of dollars, and refusing one would push it out of the ledger."""
    assert S.validate_execution(dict(execution_id="exe_1", recommendation_id="rec_1", executed_at="x",
                                     side="YES", actual_price=0.54, stake=13.5, contracts=25.0)) == []


def test_execution_stake_must_match_contracts_times_price():
    """stake = contracts * price is an identity. A record where it fails describes two different fills."""
    with pytest.raises(S.ValidationError, match="does not match contracts"):
        S.validate_execution(dict(execution_id="exe_1", recommendation_id="rec_1", executed_at="x",
                                  side="YES", actual_price=0.50, stake=20, contracts=100.0))


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
