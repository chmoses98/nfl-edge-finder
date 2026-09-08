"""A historical announcement is evidence. It is not a permanent accusation.

`show_historical=true` was added so the fee-change feed never loses evidence, and it worked: the first live
Kalshi Fee Health run returned 145 announced changes going back to October 2025. The classification did not
work. Every change without a committed window starting at its exact effective instant counted as UNMODELLED,
so an announcement from 1 January made a 8 September decision `PENDING_CHANGE` -- even though a REVIEWED
window took effect on 7 July, explicitly stating maker 1 / taker 1 for that very series, and the live API
still agreed with it.

That is backwards. The July window is the later, human-checked statement of the same regime; it supersedes
the January announcement it postdates. Under the old rule the correct configuration could never be reached:
every historical change would have had to be back-filled as a window, forever, and a genuinely live one
would sit invisible in a list of 145.

The rule these tests pin, for a decision at T under the window W in force at T:

    E unknown               UNDATED               never clears anything; surfaced for review
    a window begins at E    COVERED               already absorbed by a reviewed window
    E < W.effective_from    HISTORICAL_SUPERSEDED evidence, not a blocker
    W.start <= E <= T       LIVE_UNMODELLED       the regime moved under this decision -- BLOCKS
    E > T                   UPCOMING_UNMODELLED   a deadline: the health job shouts, pricing does not

The decision gate and the health job then use that classification differently, on purpose, and the tests
below pin both -- because collapsing them is how the desk either misses a real change or learns to ignore a
permanently red job.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.execution import fees as F        # noqa: E402
from nfl_edge.handicap import gates as G        # noqa: E402

SERIES = "KXNFLGAME"

# The dates from the live incident, so the fixture and the observation describe the same story.
JAN = datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)          # the historical venue change
JUL = datetime(2026, 7, 7, 0, 0, tzinfo=timezone.utc)          # the reviewed window in force
AUG = datetime(2026, 8, 15, 0, 0, tzinfo=timezone.utc)         # a change AFTER the window began
SEP = datetime(2026, 9, 8, 21, 0, tzinfo=timezone.utc)         # the decision
OCT = datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc)         # an upcoming change
JUN = datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc)          # before any committed window


def change(eff, *, series=SERIES, **kw):
    """One announced change in the documented shape: `scheduled_ts` is the effective instant."""
    d = {"series_ticker": series, "fee_type": "quadratic_with_maker_fees", "fee_multiplier": 1,
         "id": f"chg-{series}-{eff.isoformat() if eff else 'undated'}"}
    if eff is not None:
        d["scheduled_ts"] = eff.isoformat().replace("+00:00", "Z")
    d.update(kw)
    return d


def schedule(*window_starts, verified_at=None, max_age_days=3650.0):
    """A schedule with reviewed windows at the given starts, each closed by the next.

    Built rather than loaded so the tests state their own premises: the committed config is a moving target
    and these are assertions about the RULE, not about today's registry.
    """
    starts = sorted(window_starts)
    windows = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else None
        windows.append({
            "window_id": start.date().isoformat(),
            "effective_from": start.isoformat(),
            "effective_to": end.isoformat() if end else None,
            "verified_at": (verified_at or (start + timedelta(days=1))).isoformat(),
            "source": "REGULATORY_FEE_SCHEDULE",
            "taker_multiplier": 1.0, "maker_multiplier": 1.0,
            "series": {SERIES: {"maker_multiplier": 1.0, "taker_multiplier": 1.0}},
        })
    return F.FeeSchedule(windows=windows,
                         fee_type_by_series={SERIES: F.FEE_TYPE_WITH_MAKER},
                         verification_policy={"max_verification_age_days": max_age_days})


def observations(tmp_path, changes, *, retrieved=None, parsed=True, fc_error=None, name="snap"):
    d = tmp_path / "md" / "data" / "kalshi" / "fees"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps({
        "retrieved_at": (retrieved or (SEP - timedelta(hours=2))).isoformat(),
        "differences": [], "errors": {},
        "fee_changes": {"changes": list(changes), "parsed": parsed, "error": fc_error,
                        "show_historical": True, "shape": "series_fee_change_arr"}}))
    return F.FeeObservations(str(tmp_path / "md"))


def report():
    """The gate records its evidence on a report; the tests only care about the verdict."""
    return SimpleNamespace(fee_schedule=None)


def counts(sched, changes, at, **kw):
    return {k: len(v) for k, v in sched.classify_changes(changes, at, **kw).items()}


# ---- A. the incident: a historical change superseded by a later reviewed window ------------------------

def test_A_a_january_change_does_not_block_a_september_decision_under_a_july_window(tmp_path):
    """THE DEFECT. Jan 1 change, Jul 7 reviewed window, Sep 8 decision -> VERIFIED."""
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(JAN)])
    v = sched.verification(SERIES, SEP, obs)
    assert v["state"] == F.VERIFIED, v.get("reason")
    assert counts(sched, [change(JAN)], SEP)[F.CHANGE_SUPERSEDED] == 1


def test_A_the_superseded_change_is_still_in_the_classification(tmp_path):
    """Not blocking is not the same as not recorded. The evidence has to remain reachable."""
    sched = schedule(JUL)
    c = sched.classify_changes([change(JAN)], SEP)
    assert c[F.CHANGE_SUPERSEDED][0]["id"] == change(JAN)["id"]
    assert c[F.CHANGE_LIVE_UNMODELLED] == []


# ---- B. a change after the window began still blocks ---------------------------------------------------

def test_B_an_august_change_under_a_july_window_blocks_a_september_decision(tmp_path):
    """The regime moved under this decision and nobody reviewed it. This is what the control is for."""
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(AUG)])
    v = sched.verification(SERIES, SEP, obs)
    assert v["state"] == F.PENDING_CHANGE
    assert len(v["pending_changes"]) == 1
    assert counts(sched, [change(AUG)], SEP)[F.CHANGE_LIVE_UNMODELLED] == 1


def test_B_the_live_gate_blocks_a_real_recommendation_on_it(tmp_path):
    """The state has to reach the gate, not just the report."""
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(AUG)])
    ctx = G.GateContext(fee_schedule=sched, fee_observations=obs)
    res = G._fee_schedule_gate(ctx, report(), SERIES, SEP)
    assert res.status == G.FAIL, res.detail


def test_B_a_superseded_change_leaves_that_same_gate_passing(tmp_path):
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(JAN)])
    ctx = G.GateContext(fee_schedule=sched, fee_observations=obs)
    assert G._fee_schedule_gate(ctx, report(), SERIES, SEP).status == G.PASS


# ---- C. an upcoming change is a deadline, not today's problem ------------------------------------------

def test_C_a_future_change_leaves_the_current_decision_verified(tmp_path):
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(OCT)])
    assert sched.verification(SERIES, SEP, obs)["state"] == F.VERIFIED


def test_C_but_the_health_classification_surfaces_it(tmp_path):
    """The health job must shout BEFORE the effective time, which is the whole point of the feed."""
    sched = schedule(JUL)
    c = counts(sched, [change(OCT)], SEP)
    assert c[F.CHANGE_UPCOMING_UNMODELLED] == 1
    assert c[F.CHANGE_LIVE_UNMODELLED] == 0


def test_C_the_same_change_blocks_once_its_effective_time_has_passed(tmp_path):
    """Nothing about it changed except the decision timestamp. That is the only thing that should matter."""
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(OCT)])
    after = OCT + timedelta(days=1)
    assert sched.verification(SERIES, after, obs)["state"] == F.PENDING_CHANGE


# ---- D. a reviewed future window absorbs the upcoming change -------------------------------------------

def test_D_a_reviewed_october_window_covers_the_october_change(tmp_path):
    sched = schedule(JUL, OCT)
    obs = observations(tmp_path, [change(OCT)])
    assert sched.verification(SERIES, SEP, obs)["state"] == F.VERIFIED
    assert counts(sched, [change(OCT)], SEP)[F.CHANGE_COVERED] == 1
    assert counts(sched, [change(OCT)], SEP)[F.CHANGE_UPCOMING_UNMODELLED] == 0


def test_D_a_decision_after_october_resolves_to_the_new_window(tmp_path):
    sched = schedule(JUL, OCT)
    obs = observations(tmp_path, [change(OCT)])
    after = OCT + timedelta(days=5)
    v = sched.verification(SERIES, after, obs)
    assert v["state"] == F.VERIFIED
    assert v["window_id"] == OCT.date().isoformat()
    # And the July window is what a July decision still resolves to. History does not move.
    assert sched.verification(SERIES, JUL + timedelta(days=5), obs)["window_id"] == JUL.date().isoformat()


# ---- E. a later window may not retroactively cover an earlier decision ---------------------------------

def test_E_a_june_decision_has_no_schedule_even_though_july_exists(tmp_path):
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(JAN)])
    v = sched.verification(SERIES, JUN, obs)
    assert v["state"] == F.NO_SCHEDULE
    assert v["window_id"] is None


def test_E_supersession_is_measured_from_the_applicable_window_not_the_newest(tmp_path):
    """With two windows, a decision inside the FIRST is judged against the first.

    A change dated between the two windows is live-unmodelled for a decision in the first window and merely
    superseded for one in the second. Using "the newest window" instead of "the applicable window" would
    silently clear the first case, which is a real bet priced under a regime nobody reviewed.
    """
    sched = schedule(JUL, OCT)
    between = AUG
    assert counts(sched, [change(between)], SEP)[F.CHANGE_LIVE_UNMODELLED] == 1
    assert counts(sched, [change(between)], OCT + timedelta(days=1))[F.CHANGE_SUPERSEDED] == 1


# ---- F. many historical changes, all retained, none blocking -------------------------------------------

def test_F_a_pile_of_old_changes_is_evidence_and_nothing_else(tmp_path):
    sched = schedule(JUL)
    old = [change(JUL - timedelta(days=n), series=f"KX{n:03d}") for n in range(1, 40)]
    c = sched.classify_changes(old, SEP)
    assert len(c[F.CHANGE_SUPERSEDED]) == 39
    assert c[F.CHANGE_LIVE_UNMODELLED] == [] and c[F.CHANGE_UPCOMING_UNMODELLED] == []
    obs = observations(tmp_path, old)
    assert sched.verification(None, SEP, obs)["state"] == F.VERIFIED


def test_F_one_live_change_hidden_among_forty_old_ones_still_blocks(tmp_path):
    """The failure mode the old classification created: a real one lost in a list nobody reads."""
    sched = schedule(JUL)
    changes = [change(JUL - timedelta(days=n), series=f"KX{n:03d}") for n in range(1, 40)]
    changes.insert(17, change(AUG))
    obs = observations(tmp_path, changes)
    v = sched.verification(SERIES, SEP, obs)
    assert v["state"] == F.PENDING_CHANGE
    assert [ch["id"] for ch in v["pending_changes"]] == [change(AUG)["id"]]


# ---- G. a change exactly at the window boundary --------------------------------------------------------

def test_G_a_change_at_the_window_start_is_covered_not_pending(tmp_path):
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(JUL)])
    assert sched.verification(SERIES, SEP, obs)["state"] == F.VERIFIED
    assert counts(sched, [change(JUL)], SEP)[F.CHANGE_COVERED] == 1


def test_G_a_change_one_second_after_the_window_start_is_live_unmodelled(tmp_path):
    """The boundary is exact on purpose: `covered` means a reviewed window begins AT the change."""
    sched = schedule(JUL)
    late = change(JUL + timedelta(seconds=1))
    assert counts(sched, [late], SEP)[F.CHANGE_LIVE_UNMODELLED] == 1
    obs = observations(tmp_path, [late])
    assert sched.verification(SERIES, SEP, obs)["state"] == F.PENDING_CHANGE


def test_G_a_decision_exactly_at_the_change_instant_counts_it_as_live(tmp_path):
    sched = schedule(JUL)
    assert counts(sched, [change(AUG)], AUG)[F.CHANGE_LIVE_UNMODELLED] == 1


# ---- H. an unreadable feed still fails closed ----------------------------------------------------------

def test_H_an_inconclusive_feed_cannot_refresh_a_stale_attestation(tmp_path):
    """Unreadable is not "no changes announced". A capture that could not read the third source is not a
    confirmation of anything, so it may not stand in for one -- which is the only way an old attestation
    gets rescued."""
    sched = schedule(JUL, verified_at=SEP - timedelta(days=60), max_age_days=45.0)
    obs = observations(tmp_path, [], parsed=False, fc_error="unrecognised response shape")
    v = sched.verification(SERIES, SEP, obs)
    assert v["state"] == F.STALE_VERIFICATION
    assert v["fee_changes_state"] == "INCONCLUSIVE"


def test_H_the_same_capture_read_cleanly_does_refresh_it(tmp_path):
    """The contrast that makes the previous test about the FEED and not about the dates."""
    sched = schedule(JUL, verified_at=SEP - timedelta(days=60), max_age_days=45.0)
    obs = observations(tmp_path, [change(JAN)])          # superseded, and the feed parsed
    v = sched.verification(SERIES, SEP, obs)
    assert v["state"] == F.VERIFIED
    assert v["fee_changes_state"] == "PARSED"


def test_H_an_undated_change_is_never_silently_cleared(tmp_path):
    """No effective time means it cannot be placed before or after the window; it is not harmless."""
    sched = schedule(JUL)
    c = sched.classify_changes([change(None)], SEP)
    assert len(c[F.CHANGE_UNDATED]) == 1
    assert c[F.CHANGE_SUPERSEDED] == [] and c[F.CHANGE_LIVE_UNMODELLED] == []


def test_H_classification_requires_a_decision_timestamp():
    with pytest.raises(F.FeeStateError):
        schedule(JUL).classify_changes([change(JAN)], None)


# ---- the health job's own semantics ---------------------------------------------------------------------

def test_the_health_check_still_fails_on_a_live_or_upcoming_unmodelled_change(tmp_path):
    """Superseded changes stop failing the check. Nothing else does."""
    src = open(os.path.join(ROOT, "scripts", "kalshi", "capture_fee_metadata.py")).read()
    assert "classify_changes" in src, "the health job must use the same classifier as the gate"
    assert "CHANGE_LIVE_UNMODELLED" in src and "CHANGE_UPCOMING_UNMODELLED" in src
    assert "CHANGE_UNDATED" in src
    # And the superseded bucket must NOT be in the actionable list the check exits on.
    actionable = src.split("unmodelled = (")[1].split("snapshot[\"unmodelled_changes\"]")[0]
    assert "CHANGE_SUPERSEDED" not in actionable


def test_the_observation_keeps_every_raw_change(tmp_path):
    """Classification adds structure. It must never be a filter on the append-only evidence."""
    src = open(os.path.join(ROOT, "scripts", "kalshi", "capture_fee_metadata.py")).read()
    assert 'snapshot["fee_changes"] = fetch_fee_changes(client)' in src, \
        "the raw feed must be written to the observation untouched"


def test_series_scoping_still_applies(tmp_path):
    """A live change on somebody else's series is not this series' blocker."""
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(AUG, series="KXSOMETHINGELSE")])
    assert sched.verification(SERIES, SEP, obs)["state"] == F.VERIFIED
    assert sched.verification(None, SEP, obs)["state"] == F.PENDING_CHANGE


def test_a_change_with_no_series_is_treated_as_applying_to_all(tmp_path):
    """An exchange-wide announcement carries no series ticker; it must not slip through series scoping."""
    sched = schedule(JUL)
    obs = observations(tmp_path, [change(AUG, series=None)])
    assert sched.verification(SERIES, SEP, obs)["state"] == F.PENDING_CHANGE


# ---- what the health job FAILS on, as opposed to what it records ----------------------------------------

def test_the_actionable_set_is_scoped_to_series_this_repository_prices():
    """The feed is exchange-wide; the schedule is not.

    A fee change on a crypto perpetual cannot make an NFL net-EV number wrong, and the decision gate is
    already per-series for that reason. Scoping the FAILURE set keeps the weekly job meaningful; scoping
    the OBSERVATION would destroy evidence, so it is not scoped.
    """
    src = open(os.path.join(ROOT, "scripts", "kalshi", "capture_fee_metadata.py")).read()
    assert "def in_scope(ch):" in src
    assert 'return t is None or t in reg' in src, \
        "an exchange-wide announcement carries no series ticker and must stay in scope"
    assert '"out_of_registry_unmodelled_changes"' in src, \
        "out-of-registry actionable changes must still be recorded, just not failed on"


def test_the_check_still_fails_closed_on_no_schedule_or_stale_verification():
    src = open(os.path.join(ROOT, "scripts", "kalshi", "capture_fee_metadata.py")).read()
    assert "state not in (FEES.VERIFIED, FEES.PENDING_CHANGE)" in src, \
        "NO_SCHEDULE and STALE_VERIFICATION must remain hard failures"
    assert "if a.check and not snapshot[\"fee_changes\"].get(\"parsed\")" in src, \
        "an unreadable feed must remain a hard failure"
    assert "if a.check and diffs:" in src, \
        "a live registry conflict must remain a hard failure"


def test_show_historical_and_the_documented_shape_are_untouched():
    """The corrections this fix rests on must not be quietly rolled back to make the job green."""
    src = open(os.path.join(ROOT, "scripts", "kalshi", "capture_fee_metadata.py")).read()
    assert "show_historical=True" in src or "show_historical: bool = True" in src
    assert "series_fee_change_arr" in open(os.path.join(ROOT, "scripts", "kalshi",
                                                        "capture_fee_metadata.py")).read()
    assert "scheduled_ts" in F.CHANGE_EFFECTIVE_KEYS[0]
