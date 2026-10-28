"""The self-clocked capture lane and the health attribution it relies on (2026-10-28). Synthetic times only."""
from datetime import UTC, datetime, timedelta
from pathlib import Path

from scripts.ops import pit_availability_clock as C
from scripts.ops.pit_availability_health import (
    ALERT_HOURS,
    MAX_DISPATCH_PER_SLOT,
    assess_coverage,
    is_pregame_slot,
    scheduled_slots,
    trigger_for,
    upcoming_slots,
    watchdog_decision,
)

REPO = Path(__file__).resolve().parents[1]


def dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UTC)


def summary(run_id):
    return {"run_id": run_id, "nflverse_injuries": {"state": "UNCHANGED"}, "nflverse_depth_charts": {"state": "DIGESTED"},
            "espn_injuries": {"state": "CAPTURED"}, "espn_event_rosters": {"state": "CAPTURED"}}


def run(created, title="", event="workflow_dispatch", updated=None, status="completed", conclusion="success"):
    r = {"event": event, "createdAt": created, "status": status, "conclusion": conclusion, "displayTitle": title}
    if updated:
        r["updatedAt"] = updated
    return r


def _chain(start, end, gap_min=3):
    """Lanes back to back: each serves its plan, ends at its deadline (worst case), the next starts gap_min later."""
    served, t, chained = [], start, False
    while t < end:
        deadline = t + timedelta(minutes=C.LIFETIME_MIN)
        p = C.plan(t, deadline, chained=chained)
        served += [x["slot"] for x in p if x["dispatch"]]
        chained = True
        assert all(x["dispatch_at"] >= t for x in p)
        assert all(x["dispatch_at"] == max(x["slot"] - timedelta(minutes=C.LEAD_MIN), t) for x in p)
        t = deadline + timedelta(minutes=gap_min)
    return served


# ------------------------------------------------------------------ the lane's plan


def test_a_lane_dispatches_each_slot_lead_minutes_early_and_never_twice():
    p = C.plan(dt("2026-11-01T11:00:00Z"), dt("2026-11-01T11:00:00Z") + timedelta(minutes=C.LIFETIME_MIN))
    assert [x["slot"].strftime("%H:%M") for x in p] == ["11:47", "12:47", "13:47", "14:47", "15:47", "16:47"]
    assert p[0]["dispatch_at"] == dt("2026-11-01T11:22:00Z")
    early = C.plan(dt("2026-11-01T06:05:00Z"), dt("2026-11-01T06:05:00Z") + timedelta(minutes=C.LIFETIME_MIN))
    assert [x["slot"].strftime("%H:%M") for x in early] == ["11:47"]  # started ~5.7 h early by a cron: still on time
    assert C.plan(dt("2026-11-01T05:05:00Z"), dt("2026-11-01T05:05:00Z") + timedelta(minutes=C.LIFETIME_MIN)) == []
    assert not C.wants_successor(dt("2026-11-01T05:05:00Z"))           # too early: exits, the next cron starts it
    late = C.plan(dt("2026-11-01T11:30:00Z"), dt("2026-11-01T11:30:00Z") + timedelta(minutes=C.LIFETIME_MIN))
    assert late[0]["dispatch_at"] == dt("2026-11-01T11:30:00Z") and late[0]["dispatch"]   # cron lane: dispatch now
    chained = C.plan(dt("2026-11-01T11:30:00Z"), dt("2026-11-01T17:10:00Z"), chained=True)
    assert not chained[0]["dispatch"] and all(x["dispatch"] for x in chained[1:])        # predecessor dispatched it


def test_chained_lanes_cover_a_whole_sunday_and_its_night_slot_without_a_gap():
    served = _chain(dt("2026-11-01T05:05:00Z"), dt("2026-11-02T01:00:00Z"))
    day = [x for x in upcoming_slots(dt("2026-11-01T05:00:00Z"), dt("2026-11-02T01:00:00Z"))]
    assert sorted(set(served)) == day and len(served) == len(set(served))
    assert day[-1] == dt("2026-11-02T00:47:00Z")


def test_report_day_slots_six_hours_apart_are_reached_by_consecutive_lanes():
    served = _chain(dt("2026-11-04T01:30:00Z"), dt("2026-11-07T21:00:00Z"), gap_min=20)
    due = upcoming_slots(dt("2026-11-04T01:30:00Z"), dt("2026-11-07T21:00:00Z"))
    assert sorted(set(served)) == due


def test_a_lane_hands_over_only_when_the_next_one_has_work():
    assert C.wants_successor(dt("2026-11-04T02:40:00Z"))           # Wed 08:17 is inside the next lane's life
    assert not C.wants_successor(dt("2026-11-03T02:00:00Z"))       # Tue: next slot Wed 02:17 is a day away
    assert C.wants_successor(dt("2026-11-03T01:10:00Z"))           # Tue 00:47 still inside its window: verify it
    assert not C.wants_successor(dt("2026-11-03T01:50:00Z"))


# ------------------------------------------------------------------ the 00:47 night-game slots


def test_night_game_slot_after_sunday_monday_thursday_from_2026_10_29_only():
    week = scheduled_slots(dt("2026-11-07T00:00:00Z"))
    night = [x for x in week if x.hour == 0 and x.minute == 47]
    assert [x.strftime("%a %d") for x in night if x >= dt("2026-10-29T00:00:00Z")] == ["Fri 30", "Mon 02", "Tue 03", "Fri 06"]
    assert not [x for x in night if x < dt("2026-10-29T00:00:00Z")]   # no phantom gaps before the slot existed
    assert all(is_pregame_slot(x) for x in night)


# ------------------------------------------------------------------ attribution of clock runs and queued runs


def test_a_clock_run_belongs_to_its_slot_not_to_the_interval_it_was_created_in():
    # dispatched 12:22 for 12:47, waited, captured 12:48; 11:47 had no run at all
    runs = [run("2026-11-01T12:22:05Z", "PIT availability capture · dispatch · clock:2026-11-01T12:47",
                updated="2026-11-01T12:52:00Z")]
    sums = [summary("20261101T124811Z")]
    cov = assess_coverage(dt("2026-11-01T14:30:00Z"), sums, runs=runs, lookback_hours=4)
    v = {x["slot_utc"][11:16]: x for x in cov["slots"]}
    assert v["12:47"]["verdict"] == "COVERED" and v["12:47"]["trigger"] == "clock"
    assert v["11:47"]["verdict"] == "MISSING:NEVER_RAN"
    assert trigger_for(sums[0], runs) == "clock"


def test_a_run_queued_past_the_next_slot_is_named_as_such_not_as_a_publication_failure():
    # real 2026-10-25: created 21:14:43 in 20:47's interval, waited 55.6 min for a runner, published 22:10:33,
    # which matched the 21:47 slot; the 21:32 run was then gate-skipped
    runs = [run("2026-10-25T21:14:43Z", event="schedule", updated="2026-10-25T22:11:30Z"),
            run("2026-10-25T21:32:10Z", event="schedule", updated="2026-10-25T22:11:50Z")]
    sums = [summary("20261025T221033Z")]
    cov = assess_coverage(dt("2026-10-25T23:30:00Z"), sums, runs=runs, lookback_hours=3)
    v = {x["slot_utc"][11:16]: x["verdict"] for x in cov["slots"]}
    assert v["20:47"] == "MISSING:RAN_LATE_PUBLISHED_IN_NEXT_SLOT" and v["21:47"] == "COVERED"  # 23.6 min
    # without `updatedAt` (older run lists) the previous, coarser label is kept
    old = [{k: r[k] for k in r if k != "updatedAt"} for r in runs]
    cov_old = assess_coverage(dt("2026-10-25T23:30:00Z"), sums, runs=old, lookback_hours=3)
    assert {x["slot_utc"][11:16]: x["verdict"] for x in cov_old["slots"]}["20:47"] == "MISSING:RAN_SUCCESS_NO_PUBLICATION"


def test_only_clock_retries_count_toward_the_attempt_limit():
    slot = dt("2026-11-01T12:47:00Z")
    on_time = run("2026-11-01T12:22:05Z", "PIT availability capture · dispatch · clock:2026-11-01T12:47")
    retries = [run(f"2026-11-01T13:{m:02d}:00Z", "PIT availability capture · dispatch · clock-retry:2026-11-01T12:47")
               for m in (8, 18, 28)]
    assert watchdog_decision(slot + timedelta(minutes=22), [], [on_time])["action"] == "DISPATCH"
    assert watchdog_decision(slot + timedelta(minutes=45), [], [on_time] + retries)["reason"] == "ATTEMPTS_EXHAUSTED"
    assert len(retries) == MAX_DISPATCH_PER_SLOT
    waiting = run("2026-11-01T12:22:05Z", "clock:2026-11-01T12:47", status="in_progress", conclusion=None)
    assert watchdog_decision(slot + timedelta(minutes=22), [], [waiting])["reason"] == "IN_FLIGHT"


# ------------------------------------------------------------------ alerts


def test_alerts_are_for_recent_gaps_while_the_week_is_still_reported():
    now = dt("2026-11-02T06:00:00Z")
    sums = [summary(x.strftime("%Y%m%dT%H%M%SZ")) for x in scheduled_slots(now)
            if x >= dt("2026-11-01T00:00:00Z")]                       # everything since Sunday captured on time
    cov = assess_coverage(now, sums, runs=[])
    assert cov["recent_gaps"] == [] and cov["status"] == "COVERAGE_GAPS"  # older gaps stay in the weekly report
    assert cov["alert_hours"] == ALERT_HOURS
    cov2 = assess_coverage(now, sums[:-2], runs=[])                    # the two newest slots were never published
    assert [g["verdict"] for g in cov2["recent_gaps"]] == ["MISSING:NEVER_RAN", "MISSING:NEVER_RAN"]


# ------------------------------------------------------------------ workflows


def test_capture_workflow_waits_for_not_before_before_its_gate_and_has_the_night_crons():
    wf = (REPO / ".github/workflows/pit-availability-nfl.yml").read_text()
    assert "not_before:" in wf
    assert wf.index("- name: Wait for the slot") < wf.index("- name: Check out the published store") < wf.index("- name: Slot gate")
    assert "cron: '47 0 * * 1,2,5'" in wf and "cron: '59 0 * * 1,2,5'" in wf
    assert "max 50" in wf
    capture_timeout = int(wf.split("timeout-minutes:")[1].split()[0])
    assert capture_timeout >= C.MAX_WAIT_MIN + 20  # the wait must not eat the capture's own run time


def test_clock_workflow_is_one_uncancelled_lane_that_only_dispatches_on_main():
    wf = (REPO / ".github/workflows/pit-availability-clock.yml").read_text()
    assert "cancel-in-progress: false" in wf
    assert "contents: read" in wf and "actions: write" in wf and "contents: write" not in wf
    timeout = int(wf.split("timeout-minutes:")[1].split()[0])
    assert timeout >= C.LIFETIME_MIN + 10
    assert "--plan-only" in wf and "github.ref == 'refs/heads/main'" in wf
    for p in ("pit-availability-health.yml", "pit-availability-watchdog.yml"):
        assert "createdAt,updatedAt,displayTitle" in (REPO / ".github/workflows" / p).read_text()
