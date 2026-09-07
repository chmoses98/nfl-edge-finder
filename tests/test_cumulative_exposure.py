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


def ev(rid, settlement=1.0):
    return dict(evaluation_id=f"ev_{rid}", recommendation_id=rid, settlement=settlement,
                evaluated_at=(KICKOFF + timedelta(hours=4)).isoformat())


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
