"""Synthetic-only coverage checks for the PIT capture publication alarm."""
from datetime import datetime, timezone

from scripts.ops.pit_availability_health import assess, scheduled_slots


def dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def summary(run_id="20261012T235800Z", injury="UNCHANGED", depth="DIGESTED", espn="CAPTURED", roster="CAPTURED"):
    return {"run_id": run_id, "nflverse_injuries": {"state": injury},
            "nflverse_depth_charts": {"state": depth}, "espn_injuries": {"state": espn},
            "espn_event_rosters": {"state": roster}}


def test_monday_owed_slot_and_missing_publication():
    n = dt("2026-10-13T01:22:00Z")
    assert scheduled_slots(n)[-1] == dt("2026-10-12T23:47:00Z")
    assert assess(n, None)["status"] == "MISSING_PUBLICATION"


def test_published_run_must_not_precede_owed_window():
    assert assess(dt("2026-10-13T01:22:00Z"), summary(run_id="20261012T220000Z"))["status"] == "MISSING_PUBLICATION"


def test_successful_publication_not_equal_certified_inactives():
    v = assess(dt("2026-10-13T01:22:00Z"), summary(roster="NO_GAMES_IN_WINDOW"))
    assert v["status"] == "CAPTURE_RECORDED"
    assert "NOT yet certified" in v["reason"]


def test_source_failure_never_passes():
    v = assess(dt("2026-10-13T01:22:00Z"), summary(espn="FETCH_FAILED"))
    assert v["status"] == "SOURCE_DEGRADED"
    assert "espn_injuries" in v["reason"]


def test_activation_and_grace():
    assert assess(dt("2026-10-12T05:00:00Z"), None)["status"] == "NOT_DUE"
    assert assess(dt("2026-10-12T23:59:00Z"), None)["owed_utc"] == "2026-10-12T21:47:00+00:00"


def test_thursday_overlapping_crons_and_sunday_hours():
    s = scheduled_slots(dt("2026-10-15T23:55:00Z"))
    thu = [x.strftime("%H:%M") for x in s if x.weekday() == 3]
    assert thu == ["02:17", "08:17", "14:17", "20:17", "21:47", "22:47", "23:47"]
    # The next Sunday has hourly slots, independent of market availability.
    ss = scheduled_slots(dt("2026-10-18T23:50:00Z"))
    assert len([x for x in ss if x.date().isoformat() == "2026-10-18"]) == 13


# --- per-slot coverage (real 2026-10-12/13 history: only the 23:47 slot ran, ~2h56m late) ---
from scripts.ops.pit_availability_health import assess_coverage, classify_workflow_runs  # noqa: E402

NOW = dt("2026-10-13T04:00:00Z")


def test_late_run_does_not_cover_earlier_missed_slots():
    cov = assess_coverage(NOW, [summary(run_id="20261013T024334Z")])
    v = {s["slot_utc"][11:16]: s["verdict"] for s in cov["slots"]}
    assert v["21:47"].startswith("MISSING") and v["22:47"].startswith("MISSING")
    assert v["23:47"] == "LATE"
    assert cov["status"] == "COVERAGE_GAPS"
    assert len(cov["gaps"]["event_roster"]) == 3  # all three pregame slots lack timely roster evidence
    assert cov["availability_certified"] is False


def test_no_runs_is_never_ran_vs_ran_without_publication():
    slot = dt("2026-10-12T21:47:00Z")
    assert classify_workflow_runs(slot, []) == "NEVER_RAN"
    ok = [{"event": "schedule", "conclusion": "success", "status": "completed", "createdAt": "2026-10-12T22:05:00Z"}]
    bad = [{"event": "schedule", "conclusion": "failure", "status": "completed", "createdAt": "2026-10-12T22:05:00Z"}]
    pr = [{"event": "pull_request", "conclusion": "success", "status": "completed", "createdAt": "2026-10-12T22:05:00Z"}]
    assert classify_workflow_runs(slot, ok) == "RAN_SUCCESS_NO_PUBLICATION"
    assert classify_workflow_runs(slot, bad) == "RAN_FAILED"
    assert classify_workflow_runs(slot, pr) == "NEVER_RAN"  # dry-run PR runs never publish
    cov = assess_coverage(NOW, [], runs=ok)
    v = [s["verdict"] for s in cov["slots"]]
    assert v[0] == "MISSING:RAN_SUCCESS_NO_PUBLICATION"  # ran at 22:05 (inside slot 21:47's window), published nothing
    assert v[2] == "MISSING:NEVER_RAN"


def test_on_time_complete_run_is_covered_and_failed_source_is_gap():
    runs = [summary(run_id="20261012T215000Z"), summary(run_id="20261012T225000Z"),
            summary(run_id="20261012T235000Z", espn="FETCH_FAILED", roster="SCOREBOARD_FAILED")]
    cov = assess_coverage(NOW, runs)
    v = [s["verdict"] for s in cov["slots"]]
    assert v == ["COVERED", "COVERED", "SOURCE_DEGRADED"]
    assert len(cov["gaps"]["injury_report"]) == 1 and len(cov["gaps"]["event_roster"]) == 1


def test_all_covered_is_ok_but_never_certifies_availability():
    runs = [summary(run_id=r) for r in ("20261012T215000Z", "20261012T225000Z", "20261012T235000Z")]
    cov = assess_coverage(NOW, runs)
    assert cov["status"] == "COVERAGE_OK" and cov["availability_certified"] is False
