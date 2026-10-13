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


def test_run_that_published_another_slot_does_not_explain_missing_ones():
    # Real 10-12/13 history: the only run (created 02:43:22Z) published the 23:47 slot; 21:47/22:47 never ran.
    runs = [{"event": "schedule", "conclusion": "success", "status": "completed", "createdAt": "2026-10-13T02:43:22Z"}]
    cov = assess_coverage(NOW, [summary(run_id="20261013T024334Z")], runs=runs)
    v = [s["verdict"] for s in cov["slots"]]
    assert v == ["MISSING:NEVER_RAN", "MISSING:NEVER_RAN", "LATE"]


# --- scheduling reliability: gate + watchdog (Sunday 2026-10-18; pregame slots at :47, 60-min dispatch window) ---
from scripts.ops.pit_availability_health import (  # noqa: E402
    MAX_DISPATCH_PER_SLOT, gate_decision, trigger_for, watchdog_decision)


def run(event, created, status="completed", conclusion="success", title=""):
    return {"event": event, "createdAt": created, "status": status, "conclusion": conclusion, "displayTitle": title}


def test_dropped_schedule_is_dispatched_inside_window_only():
    s = [summary(run_id="20261018T144800Z")]                       # 14:47 slot covered
    assert watchdog_decision(dt("2026-10-18T15:55:00Z"), s, [])["reason"] == "COVERED"      # 15:47 not yet past grace
    d = watchdog_decision(dt("2026-10-18T16:02:00Z"), s, [])                                # 15:47 dropped, 15 min old
    assert d["action"] == "DISPATCH" and d["slot"].startswith("2026-10-18T15:47")


def test_missed_window_is_a_gap_never_backfilled():
    s = [summary(run_id="20261018T144800Z")]
    d = watchdog_decision(dt("2026-10-18T16:50:00Z"), s, [])                                # 63 min after 15:47
    assert d["action"] == "NONE" and d["reason"] == "WINDOW_CLOSED_GAP_REMAINS"
    cov = assess_coverage(dt("2026-10-18T17:30:00Z"), s)   # past the guard's 90-min delivery grace
    assert any(x["slot_utc"].startswith("2026-10-18T15:47") and x["verdict"].startswith("MISSING") for x in cov["slots"])
    assert cov["availability_certified"] is False
    # report-day slot (Wed 02:17Z) has the longer 180-minute window
    assert watchdog_decision(dt("2026-10-14T05:00:00Z"), [], [])["action"] == "DISPATCH"
    assert watchdog_decision(dt("2026-10-14T05:30:00Z"), [], [])["reason"] == "WINDOW_CLOSED_GAP_REMAINS"


def test_overlapping_dispatch_in_flight_then_published_is_idempotent():
    now = dt("2026-10-18T16:02:00Z")
    queued = [run("workflow_dispatch", "2026-10-18T16:01:00Z", status="queued", conclusion=None, title="watchdog:x")]
    assert watchdog_decision(now, [], queued)["reason"] == "IN_FLIGHT"                      # second watchdog does nothing
    # the queued run executes; a duplicate queued behind it re-checks the store and skips
    s = [summary(run_id="20261018T160300Z")]
    g = gate_decision(dt("2026-10-18T16:05:00Z"), s, event="workflow_dispatch")
    assert g["capture"] is False and "already covered" in g["reason"]
    assert watchdog_decision(dt("2026-10-18T16:07:00Z"), s, [])["reason"] == "COVERED"


def test_backup_cron_captures_only_when_primary_dropped():
    assert gate_decision(dt("2026-10-18T15:59:30Z"), [summary(run_id="20261018T154800Z")])["capture"] is False   # primary ran
    assert gate_decision(dt("2026-10-18T15:59:30Z"), [summary(run_id="20261018T144800Z")])["capture"] is True    # primary dropped


def test_delayed_run_is_not_skipped_and_stays_visible_as_late():
    s = [summary(run_id="20261018T154800Z")]
    assert gate_decision(dt("2026-10-18T17:30:00Z"), s)["capture"] is True                   # 16:47 slot has no capture
    s.append(summary(run_id="20261018T173000Z"))
    cov = assess_coverage(dt("2026-10-18T19:00:00Z"), s, lookback_hours=6)
    late = [x for x in cov["slots"] if x["slot_utc"].startswith("2026-10-18T16:47")][0]
    assert late["verdict"] == "LATE" and late["minutes_late"] == 43.0


def test_publication_failure_retries_then_stops_and_gap_stays():
    fails = [run("workflow_dispatch", f"2026-10-18T16:0{i}:00Z", conclusion="failure", title="watchdog:x") for i in range(1, 3)]
    assert watchdog_decision(dt("2026-10-18T16:20:00Z"), [], fails[:1])["action"] == "DISPATCH"
    many = fails + [run("workflow_dispatch", "2026-10-18T16:09:00Z", conclusion="failure", title="watchdog:x")]
    assert len(many) == MAX_DISPATCH_PER_SLOT
    assert watchdog_decision(dt("2026-10-18T16:25:00Z"), [], many)["reason"] == "ATTEMPTS_EXHAUSTED"
    cov = assess_coverage(dt("2026-10-18T16:25:00Z"), [], runs=many, lookback_hours=2)
    assert any(x["verdict"] == "MISSING:RAN_FAILED" for x in cov["slots"])


def test_gate_fail_open_for_dry_run_and_force_and_trigger_provenance():
    s = [summary(run_id="20261018T154800Z")]
    now = dt("2026-10-18T15:59:00Z")
    assert gate_decision(now, s, event="pull_request")["capture"] is True
    assert gate_decision(now, s, event="workflow_dispatch", force=True)["capture"] is True
    sm = summary(run_id="20261018T160300Z")
    assert trigger_for(sm, [run("schedule", "2026-10-18T16:02:40Z")]) == "schedule"
    assert trigger_for(sm, [run("workflow_dispatch", "2026-10-18T16:02:40Z", title="x · watchdog:2026")]) == "watchdog"
    assert trigger_for(sm, [run("workflow_dispatch", "2026-10-18T16:02:40Z", title="manual")]) == "manual"
    assert trigger_for(sm, []) == "unknown"


def test_missing_store_is_unreadable_not_empty(tmp_path):
    import json as _j
    import pytest
    from scripts.ops.pit_availability_health import main, read_summaries_dir
    with pytest.raises(OSError):
        read_summaries_dir(str(tmp_path / "nope"))
    assert main(["--mode", "watchdog", "--store", str(tmp_path / "nope"), "--now", "2026-10-18T16:02:00Z"]) == 0  # no dispatch
    (tmp_path / "ok" / "runs").mkdir(parents=True)
    (tmp_path / "ok" / "runs" / "a.summary.json").write_text(_j.dumps(summary(run_id="20261018T170000Z")))
    # a capture from the "future" relative to --now must not count as evidence at --now
    assert [x["run_id"] for x in read_summaries_dir(str(tmp_path / "ok"))] == ["20261018T170000Z"]
