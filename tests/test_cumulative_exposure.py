"""Portfolio limits are cumulative across handicap runs, or they are not limits.

The defect these pin:

    run A, 13:00   home-side thesis, 2u   -> passes the 3u correlation cap
    run B, 15:00   another home-side, 2u  -> passes the 3u correlation cap, independently
    the desk        4u in one thesis      -> the policy has been broken and every gate said PASS

Each batch was measured against itself. A cap measured against one batch is a cap on batch size, which is a
different and much weaker statement than a cap on exposure.

The fix is one definition of outstanding exposure, read from the committed ledger at the decision timestamp,
that every write path consumes: reserved (approved and unfilled, until kickoff) plus at risk (filled and
unsettled). These tests cover both what it counts and what it deliberately does not.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import risk as R      # noqa: E402
from nfl_edge.handicap import schema as S    # noqa: E402
from nfl_edge.handicap import store          # noqa: E402

T0 = datetime(2026, 9, 9, 13, 0, tzinfo=timezone.utc)
LATER = T0 + timedelta(hours=2)
KICKOFF = T0 + timedelta(hours=7)
# unit = 0.005 * 2000 = $10. Group cap 3u = $30, game cap 4u = $40, slate cap 12u/6% = $120.
# Grade A is used throughout because its cap (2u = $20) is not what binds in these tests; a B+ record is
# capped to 1u before any aggregate limit is reached, which would test the wrong thing.
BANKROLL = 2000.0


def rec(rid, stake, *, game="2026_01_NE_SEA", group="NE_SEA_home", created=T0, kickoff=KICKOFF,
        decision=S.RECOMMENDED, **kw):
    d = dict(recommendation_id=rid, schema_version=S.HANDICAP_SCHEMA_VERSION,
             created_at=created.isoformat(), kickoff_utc=kickoff.isoformat(),
             season=2026, week=1, game_id=game, correlation_group=group, decision=decision,
             recommended_stake=stake, proposed_stake=stake, bankroll_snapshot=BANKROLL,
             grade="A", market_ticker=f"KXNFLGAME-{rid}")
    d.update(kw)
    return d


def ex(rid, stake, *, when=None, eid=None, **kw):
    return dict(execution_id=eid or f"exe_{rid}", recommendation_id=rid,
                executed_at=(when or T0 + timedelta(minutes=5)).isoformat(),
                actual_price=0.50, stake=stake, side="YES", **kw)


def ev(rid, settlement=1.0, *, evaluated=None, observed=None, **kw):
    d = dict(evaluation_id=f"ev_{rid}", recommendation_id=rid, settlement=settlement,
             evaluated_at=(evaluated or KICKOFF + timedelta(hours=4)).isoformat()
             if evaluated is not False else None)
    if observed is not None:
        d["settlement_observed_at"] = observed.isoformat() if observed is not False else observed
    d.update(kw)
    return d


def exposure(recs=(), exes=(), evals=(), as_of=LATER, **kw):
    return R.outstanding_exposure(list(recs), list(exes), list(evals), as_of, **kw)


POLICY = R.RiskPolicy.load(ROOT)


def verdict(batch, outstanding):
    report = POLICY.evaluate([R.Proposal.from_record(r) for r in batch], BANKROLL, outstanding)
    return report, report.verdict_for(batch[0]["recommendation_id"])


# ---- the four adversarial cases the review asked for -------------------------------------------------

def test_two_batches_each_under_the_correlation_cap_are_capped_together():
    """A: 2u passes. B: 2u passes. A+B = 4u against a 3u group cap, so B may only take the last 1u."""
    a = rec("rec_a", 20)
    alone_a, va = verdict([a], R.EMPTY_EXPOSURE)
    assert va.status == R.APPROVED and va.approved_stake == 20

    b = rec("rec_b", 20)
    alone_b, vb = verdict([b], R.EMPTY_EXPOSURE)
    assert vb.status == R.APPROVED, "individually, B is fine -- which is exactly the trap"

    out = exposure([a])
    assert out.total == 20.0
    assert out.by_correlation_group["NE_SEA_home"] == 20.0
    together, vb2 = verdict([b], out)
    assert vb2.status == R.CAPPED and vb2.approved_stake == 10.0, \
        "the group cap is 3u = $30 and $20 is already committed"
    assert vb2.binding_limit == "max_exposure_per_correlation_group_units"
    assert together.exposure_by_correlation_group["NE_SEA_home"] == 30.0
    assert together.batch_exposure == 10.0, "the batch added 1u; the other 2u was already outstanding"
    assert alone_a is not alone_b


def test_a_group_already_at_its_cap_rejects_the_next_position_outright():
    prior = [rec("rec_a", 20), rec("rec_b", 10)]
    out = exposure(prior)
    assert out.by_correlation_group["NE_SEA_home"] == 30.0
    _report, v = verdict([rec("rec_c", 20)], out)
    assert v.status == R.REJECTED and v.approved_stake == 0.0


def test_the_game_cap_is_cumulative_across_runs():
    """4u = $40 per game, spread over two correlation groups so the group cap is not what binds."""
    prior = [rec("rec_a", 20, group="g1"), rec("rec_b", 15, group="g2")]
    out = exposure(prior)
    assert out.by_game["2026_01_NE_SEA"] == 35.0
    _r, v = verdict([rec("rec_c", 20, group="g3")], out)
    assert v.status == R.CAPPED and v.approved_stake == 5.0
    assert v.binding_limit == "max_exposure_per_game_units"


def test_the_slate_cap_is_cumulative_across_runs():
    """12u = $120, or 6% of bankroll = $120; both bind at the same place here."""
    prior = [rec(f"rec_{i}", 20, game=f"g{i}", group=f"c{i}") for i in range(5)]      # $100
    out = exposure(prior)
    assert out.total == 100.0
    _r, v = verdict([rec("rec_new", 20, game="gx", group="cx")], out)
    assert v.status == R.APPROVED and v.approved_stake == 20.0, "$120 of slate room, $100 used"

    prior.append(rec("rec_5", 15, game="g5", group="c5"))                              # $115
    _r2, v2 = verdict([rec("rec_new", 20, game="gx", group="cx")], exposure(prior))
    assert v2.status == R.CAPPED and v2.approved_stake == 5.0
    assert v2.binding_limit in ("max_slate_exposure_units",
                                "max_slate_exposure_fraction_of_bankroll")


def test_separate_airtable_rows_in_one_cycle_cannot_bypass_the_cap(tmp_path):
    """Two rows imported minutes apart is the same trap as two runs hours apart."""
    ledger = tmp_path / "ledger"
    write(ledger, "recommendations", rec("rec_row1", 20))
    out = R.load_outstanding(str(ledger), LATER)
    assert out.total == 20.0
    _r, v = verdict([rec("rec_row2", 20)], out)
    assert v.approved_stake == 10.0


# ---- what counts, and for how long -------------------------------------------------------------------

def test_an_unfilled_approval_reserves_its_full_stake_until_kickoff():
    out = exposure([rec("rec_a", 20)])
    p = out.positions[0]
    assert (p.reserved_stake, p.at_risk_stake, p.exposure) == (20.0, 0.0, 20.0)
    assert "not yet filled" in p.basis


def test_a_partial_fill_is_neither_forgotten_nor_double_counted():
    """$6 filled against a $10 approval holds $10: $6 at risk and $4 still reservable."""
    out = exposure([rec("rec_a", 10)], [ex("rec_a", 6)])
    p = out.positions[0]
    assert p.executed_stake == 6.0 and p.at_risk_stake == 6.0 and p.reserved_stake == 4.0
    assert p.exposure == 10.0, "a recommendation and its own fills are one position, not two"


def test_a_fully_filled_position_is_counted_once():
    out = exposure([rec("rec_a", 10)], [ex("rec_a", 6), ex("rec_a", 4, eid="exe_2")])
    assert out.total == 10.0, "10 approved and 10 filled is 10 of exposure, not 20"


def test_an_overfill_holds_the_larger_number():
    out = exposure([rec("rec_a", 10)], [ex("rec_a", 13)])
    assert out.total == 13.0, "the money actually at risk is what binds, not the approval"


def test_after_kickoff_the_unfilled_reserve_is_released_but_the_fill_is_not():
    after = KICKOFF + timedelta(minutes=1)
    out = exposure([rec("rec_a", 10)], [ex("rec_a", 6)], as_of=after)
    p = out.positions[0]
    assert p.reserved_stake == 0.0, "a pregame position can no longer be established after kickoff"
    assert p.at_risk_stake == 6.0, "the money already down is still down"


def test_a_settled_position_is_released():
    after = KICKOFF + timedelta(hours=5)
    live = exposure([rec("rec_a", 10)], [ex("rec_a", 10)], as_of=after)
    assert live.total == 10.0
    done = exposure([rec("rec_a", 10)], [ex("rec_a", 10)], [ev("rec_a")], as_of=after)
    assert done.total == 0.0
    assert any("settled" in why for _rid, why in done.excluded)


def test_an_unsettled_filled_position_is_still_exposure_long_after_kickoff():
    """No evaluation means no evidence of settlement, and the conservative reading holds the exposure."""
    out = exposure([rec("rec_a", 10)], [ex("rec_a", 10)], as_of=KICKOFF + timedelta(days=3))
    assert out.total == 10.0


# ---- amendments --------------------------------------------------------------------------------------

def test_an_amended_recommendation_is_counted_once_at_the_amended_size():
    original = rec("rec_a", 20)
    amended = rec("rec_a2", 10, amends="rec_a")
    out = exposure([original, amended])
    assert out.total == 10.0, "the chain is one position, at the current opinion's size"
    assert [p.recommendation_id for p in out.positions] == ["rec_a2"]
    assert any("superseded" in why for _rid, why in out.excluded)


def test_a_fill_taken_under_the_superseded_link_still_counts_against_the_amendment():
    """The amendment revised the OPINION. It did not un-spend the money."""
    out = exposure([rec("rec_a", 20), rec("rec_a2", 10, amends="rec_a")], [ex("rec_a", 8)])
    p = out.positions[0]
    assert p.executed_stake == 8.0 and p.at_risk_stake == 8.0
    assert p.reserved_stake == 2.0 and p.exposure == 10.0


def test_an_amendment_that_shrinks_below_the_fill_holds_the_fill():
    out = exposure([rec("rec_a", 20), rec("rec_a2", 5, amends="rec_a")], [ex("rec_a", 12)])
    assert out.total == 12.0


# ---- what is deliberately excluded -------------------------------------------------------------------

@pytest.mark.parametrize("kw,fragment", [
    (dict(test_only=True), "TEST_ONLY"),
    (dict(decision=S.PASS), "consumes no bankroll"),
    (dict(decision=S.WATCHLIST), "consumes no bankroll"),
    (dict(decision=S.RESEARCH_ALERT), "consumes no bankroll"),
])
def test_records_that_risk_no_capital_are_excluded_with_a_reason(kw, fragment):
    out = exposure([rec("rec_x", 20, **kw)])
    assert out.total == 0.0
    assert any(fragment in why for _rid, why in out.excluded), out.excluded


def test_a_decision_made_after_this_one_is_not_prior_exposure():
    """The same decision-time clock every other gate uses. Later positions are not evidence about now."""
    future = rec("rec_future", 20, created=LATER + timedelta(hours=3))
    out = exposure([future], as_of=LATER)
    assert out.total == 0.0
    assert any("after the decision" in why for _rid, why in out.excluded)


def test_a_fill_recorded_after_the_decision_is_not_counted_yet():
    out = exposure([rec("rec_a", 10)], [ex("rec_a", 6, when=LATER + timedelta(hours=1))], as_of=LATER)
    p = out.positions[0]
    assert p.executed_stake == 0.0 and p.reserved_stake == 10.0


def test_the_batch_being_evaluated_is_not_counted_as_its_own_prior_exposure():
    a = rec("rec_a", 20)
    out = exposure([a], exclude_ids={"rec_a"})
    assert out.total == 0.0
    assert any("currently being evaluated" in why for _rid, why in out.excluded)


# ---- the two conservative bounds ---------------------------------------------------------------------

def test_inclusion_uses_the_latest_decision_and_release_uses_the_earliest():
    """Both bounds are rounded against the batch, the same way the quote gate rounds capture times.

    A position kicking off between two decisions in one batch is still held (release judged at the earliest)
    while a position taken between them is already counted (inclusion judged at the latest).
    """
    early, late = T0, T0 + timedelta(hours=4)
    kicks_between = rec("rec_ko", 10, kickoff=T0 + timedelta(hours=2))
    taken_between = rec("rec_mid", 10, created=T0 + timedelta(hours=1), game="g2", group="c2")
    out = R.outstanding_exposure([kicks_between, taken_between], [], [], late, release_as_of=early)
    ids = {p.recommendation_id for p in out.positions}
    assert "rec_ko" in ids, "release judged at the earliest decision: not yet kicked off"
    assert "rec_mid" in ids, "inclusion judged at the latest decision: already taken"


def test_report_for_batch_reads_the_committed_ledger(tmp_path):
    ledger = tmp_path / "ledger"
    write(ledger, "recommendations", rec("rec_prior", 20))
    report = R.report_for_batch([rec("rec_new", 20)], POLICY, str(ledger))
    assert report.outstanding["total"] == 20.0
    assert report.verdict_for("rec_new").approved_stake == 10.0


def test_an_unreadable_ledger_is_not_an_empty_one():
    """The gate refuses on this; here we pin that the report says so rather than reporting zero."""
    report = R.report_for_batch([rec("rec_new", 20)], POLICY, None)
    assert report.outstanding["source"].startswith("UNAVAILABLE")
    assert report.outstanding["total"] == 0.0, "the number is zero and the SOURCE is what makes it unusable"


def write(ledger, kind, record):
    rid = record.get("recommendation_id") if kind == "recommendations" else (
        record.get("execution_id") or record.get("evaluation_id"))
    path = store.record_path(str(ledger), kind, record.get("season", 2026), record.get("week", 1), rid)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(record, f)
    return path


# ---- settlement may not release exposure retroactively -----------------------------------------------
#
# The one fact that can LOOSEN a cap arrives hours after the decisions it would loosen:
#
#   13:00  run A is filled and unsettled
#   15:00  run B is evaluated and must see run A as outstanding
#   20:00  the game settles
#   21:00  the Evaluation is written
#   01:00  the twelve-hourly replay re-evaluates the 15:00 decision -- with that Evaluation in the ledger
#
# Releasing on the mere existence of the Evaluation lets the replay approve exposure that was over the limit
# when the call was actually made. The replay exists to REPRODUCE the pre-trade verdict, not to improve on
# it with hindsight.

FILLED_AT = T0 + timedelta(minutes=5)
DECISION_B = T0 + timedelta(hours=2)          # 15:00
GAME_SETTLES = T0 + timedelta(hours=7)        # 20:00
EVALUATION_WRITTEN = T0 + timedelta(hours=8)  # 21:00
REPLAY_RUNS = T0 + timedelta(hours=12)        # 01:00


def _run_a():
    return (rec("rec_a", 20, kickoff=T0 + timedelta(hours=4)), ex("rec_a", 20, when=FILLED_AT))


def test_A_a_settlement_written_after_the_decision_does_not_release_at_the_decision():
    a, fill = _run_a()
    out = exposure([a], [fill], [ev("rec_a", evaluated=EVALUATION_WRITTEN)], as_of=DECISION_B)
    assert out.total == 20.0, "at 15:00 the outcome was not knowable; the stake is still exposure"
    assert any("not available until" in why for _rid, why in out.excluded)


def test_B_the_same_position_is_released_once_the_settlement_was_available():
    a, fill = _run_a()
    later = exposure([a], [fill], [ev("rec_a", evaluated=EVALUATION_WRITTEN)],
                     as_of=EVALUATION_WRITTEN + timedelta(minutes=1))
    assert later.total == 0.0
    assert any("settled and fully released" in why for _rid, why in later.excluded)


def test_C_the_delayed_replay_reaches_the_verdict_preflight_reached():
    """The property that makes the twelve-hourly import an audit rather than a second opinion."""
    a, fill = _run_a()
    b = rec("rec_b", 20)
    evaluations = [ev("rec_a", evaluated=EVALUATION_WRITTEN)]

    # 15:00, pre-trade: run A is outstanding, so B is capped by the 3u group limit.
    at_decision = exposure([a], [fill], [], as_of=DECISION_B, exclude_ids={"rec_b"})
    _r1, pre = verdict([b], at_decision)

    # 01:00, replay of the SAME 15:00 decision -- now with the 21:00 settlement in the ledger.
    at_replay = exposure([a], [fill], evaluations, as_of=DECISION_B, exclude_ids={"rec_b"})
    _r2, post = verdict([b], at_replay)

    assert pre.approved_stake == 10.0 and pre.status == R.CAPPED
    assert post.approved_stake == pre.approved_stake, \
        "the replay used a settlement that did not exist at the decision and loosened the cap"
    assert post.status == pre.status
    assert REPLAY_RUNS > EVALUATION_WRITTEN > GAME_SETTLES > DECISION_B


def test_D_a_settlement_with_no_usable_timestamp_retains_the_exposure():
    a, fill = _run_a()
    for broken in (ev("rec_a", evaluated=False), ev("rec_a", evaluated=False, settlement_observed_at="soon")):
        out = exposure([a], [fill], [broken], as_of=REPLAY_RUNS)
        assert out.total == 20.0, f"{broken} released exposure without provenance"
        assert any("no usable availability timestamp" in why for _rid, why in out.excluded)


def test_an_explicit_observation_timestamp_is_preferred_over_the_write_time():
    """`evaluated_at` is the conservative FALLBACK. A real observation is stronger provenance."""
    a, fill = _run_a()
    e = ev("rec_a", evaluated=EVALUATION_WRITTEN, observed=GAME_SETTLES)
    between = GAME_SETTLES + timedelta(minutes=30)      # after settlement, before the evaluation was written
    assert exposure([a], [fill], [e], as_of=between).total == 0.0
    assert exposure([a], [fill], [ev("rec_a", evaluated=EVALUATION_WRITTEN)],
                    as_of=between).total == 20.0, "without the observation, the write time governs"


def test_E_no_post_decision_fact_of_any_kind_can_loosen_a_cap():
    """The invariant the four cases above are instances of.

    Sweep every lever that could release exposure -- a later recommendation, a later fill, a later
    settlement -- and assert the exposure measured at T never falls below the exposure measured with only
    the facts that existed at T.
    """
    a, fill = _run_a()
    truth_at_t = exposure([a], [fill], [], as_of=DECISION_B).total
    for extra_evals in ([], [ev("rec_a", evaluated=EVALUATION_WRITTEN)],
                        [ev("rec_a", evaluated=REPLAY_RUNS, observed=GAME_SETTLES)],
                        [ev("rec_a", evaluated=EVALUATION_WRITTEN, observed=EVALUATION_WRITTEN)]):
        got = exposure([a, rec("rec_late", 20, created=REPLAY_RUNS)],
                       [fill, ex("rec_a", 5, when=REPLAY_RUNS, eid="exe_late")],
                       extra_evals, as_of=DECISION_B)
        assert got.total >= truth_at_t, f"{extra_evals} loosened the measurement at {DECISION_B}"


def test_settlement_release_is_judged_at_the_batch_release_bound():
    """Release uses the batch's EARLIEST decision, so a long batch never releases early."""
    a, fill = _run_a()
    e = ev("rec_a", evaluated=GAME_SETTLES + timedelta(minutes=30))
    out = R.outstanding_exposure([a], [fill], [e], REPLAY_RUNS, release_as_of=DECISION_B)
    assert out.total == 20.0, "inclusion looked at 01:00; release must still look at 15:00"


def test_a_test_only_evaluation_never_releases_real_exposure():
    a, fill = _run_a()
    out = exposure([a], [fill], [ev("rec_a", evaluated=T0, test_only=True)], as_of=REPLAY_RUNS)
    assert out.total == 20.0
