#!/usr/bin/env python3
"""Read-only health check for the NFL point-in-time availability capture.

The pipeline cannot learn an injury/teammate-absence feature from a capture that was
never published. Check the due schedule against *published* append-only run summaries,
not GitHub's optimistic job status. This script never writes model inputs or outcomes.

Usage: python3 scripts/ops/pit_availability_health.py --ref origin/market-data \
           [--summary "$GITHUB_STEP_SUMMARY"]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

PREFIX = "data/pit_availability/nfl/runs/"
# First deployment: PR #137, merged on 2026-10-12 at 04:30:52 UTC.
ACTIVATED = datetime(2026, 10, 12, 4, 30, 52, tzinfo=timezone.utc)
# 00:47 UTC slot after each night game (Sunday, Monday, Thursday), owed from this date on. From 2026-11-01 (US
# standard time) those games kick off ~01:15-01:20 UTC, so their ~T-90m inactive lists appear ~23:45-23:50 UTC, after
# the 23:47 slot; without 00:47 the roster evidence after the list (the [T-240m, T+30m] window) would never be read.
NIGHT_SLOT_FROM = datetime(2026, 10, 29, 0, 0, tzinfo=timezone.utc)
GOOD_INJURY = {"UNCHANGED", "NEW_CONTENT"}
GOOD_DEPTH = {"UNCHANGED", "DIGESTED"}
GOOD_ESPN = {"CAPTURED"}
GOOD_ROSTER = {"CAPTURED", "NO_GAMES_IN_WINDOW"}
LATE_MINUTES = 30        # a run later than this after its slot may have missed the roster window [T-240m, T+30m]
MAX_MATCH_HOURS = 6      # a run older than this relative to a slot is not evidence for that slot
# Watchdog: a capture dispatched now is still PROSPECTIVE (stamped with our retrieval time, never backdated), but only
# worth dispatching while the slot's purpose is alive: ~T-90m rosters (pregame slots) or the report-day injury reports.
DISPATCH_GRACE_MIN = 12          # give the primary and backup crons this long before declaring a slot dropped
PREGAME_DISPATCH_MIN = 60
REPORT_DISPATCH_MIN = 180
MAX_DISPATCH_PER_SLOT = 3        # bounded retries (publication failures); then the slot stays a visible gap
# The health job FAILS (an alert someone should act on) only for gaps among the slots due in the last ALERT_HOURS; the
# full LOOKBACK window is still reported slot by slot. Four 6-hourly health runs see every gap, so none is missed, and a
# gap that was already alerted on does not keep the job red for a week.
ALERT_HOURS = 26


def _utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must have UTC offset")
    return dt.astimezone(timezone.utc)


def scheduled_slots(now: datetime, activated: datetime = ACTIVATED) -> list[datetime]:
    """All due UTC capture slots after activation (same schedule as pit-availability-nfl.yml)."""
    now = now.astimezone(timezone.utc)
    day = activated.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    slots = []
    while day <= end:
        wd = day.weekday()  # Monday=0, Sunday=6
        times = []
        if wd in (2, 3, 4, 5):  # Wed-Sat
            times += [(h, 17) for h in (2, 8, 14, 20)]
        if wd == 6:  # Sunday
            times += [(h, 47) for h in range(11, 24)]
        if wd in (0, 3):  # Monday/Thursday pregame
            times += [(h, 47) for h in (21, 22, 23)]
        if wd in (0, 1, 4) and day >= NIGHT_SLOT_FROM:  # 00:47 after the Sunday / Monday / Thursday night game
            times += [(0, 47)]
        for h, m in times:
            slot = day.replace(hour=h, minute=m)
            if activated <= slot <= now:
                slots.append(slot)
        day += timedelta(days=1)
    return sorted(slots)


def git_output(*args: str) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f"git {' '.join(args[:3])}: {proc.stderr.strip()}")
    return proc.stdout


def latest_summary(ref: str) -> dict | None:
    paths = [p for p in git_output("ls-tree", "-r", "--name-only", ref, PREFIX).splitlines()
             if p.startswith(PREFIX) and p.endswith(".summary.json")]
    if not paths:
        return None
    # Run ids are timestamp-prefixed, so lexicographic max is the latest observation.
    p = max(paths)
    result = json.loads(git_output("show", f"{ref}:{p}"))
    result["_path"] = p
    return result


def assess(now: datetime, summary: dict | None, *, grace_minutes: int = 90,
           activated: datetime = ACTIVATED) -> dict:
    now = now.astimezone(timezone.utc)
    if now < activated:
        return {"status": "NOT_DUE", "reason": "capture not activated yet", "owed_utc": None}
    slots = [x for x in scheduled_slots(now, activated) if x <= now - timedelta(minutes=grace_minutes)]
    if not slots:
        return {"status": "NOT_DUE", "reason": "no capture window past delivery grace", "owed_utc": None}
    owed = slots[-1]
    report = {"status": "MISSING_PUBLICATION", "owed_utc": owed.isoformat(),
              "last_capture_utc": None, "source_states": {}, "reason": "no published PIT availability capture"}
    if summary is None:
        return report
    try:
        captured = _utc(summary["run_id"][:4] + "-" + summary["run_id"][4:6] + "-" +
                        summary["run_id"][6:8] + "T" + summary["run_id"][9:11] + ":" +
                        summary["run_id"][11:13] + ":" + summary["run_id"][13:15] + "Z")
    except (KeyError, ValueError, TypeError, IndexError):
        report["reason"] = "published capture summary has invalid run_id"
        return report
    report["last_capture_utc"] = captured.isoformat()
    if captured < owed:
        report["reason"] = "latest published capture predates latest owed slot"
        return report
    allowed = {"nflverse_injuries": GOOD_INJURY, "nflverse_depth_charts": GOOD_DEPTH,
               "espn_injuries": GOOD_ESPN, "espn_event_rosters": GOOD_ROSTER}
    states = {k: (summary.get(k) or {}).get("state") for k in allowed}
    report["source_states"] = states
    bad = [k for k, expected in allowed.items() if states[k] not in expected]
    if bad:
        report["status"] = "SOURCE_DEGRADED"
        report["reason"] = "capture published but input unavailable or failed: " + ", ".join(bad)
    else:
        report["status"] = "CAPTURE_RECORDED"
        report["reason"] = "scheduled run published; individual player availability NOT yet certified"
    return report


def is_pregame_slot(slot: datetime) -> bool:
    """Slots whose purpose is the ~T-90m inactive-list roster window (Sun 11-23, Mon/Thu 21-23, and 00:47 UTC
    Mon/Tue/Fri after the night games)."""
    wd = slot.weekday()
    return ((wd == 6 and 11 <= slot.hour <= 23) or (wd in (0, 3) and slot.hour in (21, 22, 23))
            or (wd in (0, 1, 4) and slot.hour == 0 and slot.minute == 47))


def run_time(summary: dict) -> datetime | None:
    rid = summary.get("run_id") or ""
    try:
        return datetime.strptime(rid, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def match_runs(slots: list[datetime], summaries: list[dict]) -> dict:
    """One-to-one: each published run covers at most one slot (the latest unmatched slot at or before it, within
    MAX_MATCH_HOURS). A single late run therefore cannot paper over earlier missed slots."""
    matched: dict[datetime, dict] = {}
    for sm in sorted((x for x in summaries if run_time(x)), key=run_time):
        t = run_time(sm)
        cands = [x for x in slots if x <= t and (t - x) <= timedelta(hours=MAX_MATCH_HOURS) and x not in matched]
        if cands:
            matched[cands[-1]] = sm
    return matched


def _published_late_into_next_slot(slot: datetime, until: datetime | None, runs: list[dict],
                                   published: list[datetime]) -> bool:
    """A run created inside [slot, until) that waited (for a runner or the concurrency group) past `until` and then
    published: its capture is real but belongs to the later slot's interval, so this slot is still a gap, caused by
    queueing rather than by a publication failure. Needs `updatedAt` (gh run list) to bound when the run finished."""
    if until is None:
        return False
    for r in runs or []:
        try:
            created, updated = run_anchor(r), _utc(r["updatedAt"])
        except (KeyError, ValueError, TypeError):
            continue
        if r.get("event") in ("schedule", "workflow_dispatch") and r.get("conclusion") == "success" \
                and slot <= created < until and any(until <= p <= updated + timedelta(minutes=1) for p in published):
            return True
    return False


def classify_workflow_runs(slot: datetime, runs: list[dict], until: datetime | None = None) -> str:
    """What GitHub says happened for an unmatched slot. `runs` = [{event, conclusion, status, createdAt}, ...]
    for the capture workflow on main (schedule / workflow_dispatch only). A run created at or after `until` (the next
    slot) belongs to that later slot (a late-delivered or gate-skipped duplicate), so it cannot explain this one."""
    near = []
    for r in runs or []:
        if r.get("event") not in ("schedule", "workflow_dispatch"):
            continue
        try:
            t = run_anchor(r)
        except (KeyError, ValueError, TypeError):
            continue
        end = slot + timedelta(hours=MAX_MATCH_HOURS)
        if until is not None:
            end = min(end, until)
        if slot <= t < end:
            near.append(r)
    if not near:
        return "NEVER_RAN"
    if all(r.get("conclusion") not in ("success", None) for r in near):
        return "RAN_FAILED"
    if any(r.get("status") != "completed" for r in near):
        return "RUN_IN_PROGRESS"
    return "RAN_SUCCESS_NO_PUBLICATION"


def upcoming_slots(now: datetime, until: datetime) -> list[datetime]:
    """Capture slots strictly after `now` and at or before `until` (the same schedule as `scheduled_slots`)."""
    return [x for x in scheduled_slots(until, activated=now) if x > now]


def latest_slot(now: datetime, activated: datetime = ACTIVATED) -> datetime | None:
    slots = scheduled_slots(now, activated)
    return slots[-1] if slots else None


def slot_covered(slot: datetime, summaries: list[dict]) -> datetime | None:
    """Time of the first PUBLISHED capture at or after `slot`, else None. Only the published store counts."""
    ts = sorted(t for t in (run_time(x) for x in summaries) if t and t >= slot)
    return ts[0] if ts else None


def gate_decision(now: datetime, summaries: list[dict], *, event: str = "schedule", force: bool = False) -> dict:
    """Capture-run gate: skip only a REDUNDANT run (the latest slot already has a published capture). A late run is
    never skipped (late prospective evidence is still evidence; the coverage guard reports it LATE). Writes nothing."""
    now = now.astimezone(timezone.utc)
    if event == "pull_request" or force:
        return {"capture": True, "reason": "dry-run or forced"}
    slot = latest_slot(now)
    if slot is None:
        return {"capture": True, "reason": "no slot due yet"}
    first = slot_covered(slot, summaries)
    if first is not None:
        return {"capture": False, "slot": slot.isoformat(), "reason": f"slot already covered by published capture {first.isoformat()}"}
    return {"capture": True, "slot": slot.isoformat(), "reason": "latest slot has no published capture"}


def watchdog_decision(now: datetime, summaries: list[dict], runs: list[dict]) -> dict:
    """Dispatch the existing capture workflow iff the latest slot was dropped and its window is still open.
    Never backfills: a closed window stays a gap (assess_coverage reports it)."""
    now = now.astimezone(timezone.utc)
    slot = latest_slot(now - timedelta(minutes=DISPATCH_GRACE_MIN))
    if slot is None:
        return {"action": "NONE", "reason": "NOT_DUE"}
    base = {"slot": slot.isoformat(), "age_min": round((now - slot).total_seconds() / 60.0, 1)}
    window = PREGAME_DISPATCH_MIN if is_pregame_slot(slot) else REPORT_DISPATCH_MIN
    first = slot_covered(slot, summaries)
    if first is not None:
        return {**base, "action": "NONE", "reason": "COVERED", "covered_by": first.isoformat()}
    if base["age_min"] > window:
        return {**base, "action": "NONE", "reason": "WINDOW_CLOSED_GAP_REMAINS"}
    cap = [r for r in runs or [] if r.get("event") in ("schedule", "workflow_dispatch")]
    if any(r.get("status") in ("queued", "in_progress", "waiting", "requested", "pending") for r in cap):
        return {**base, "action": "NONE", "reason": "IN_FLIGHT"}
    def _after(r):
        try:
            return run_anchor(r) >= slot and "clock:" not in (r.get("displayTitle") or "")
        except (KeyError, ValueError, TypeError):
            return False
    if sum(1 for r in cap if r.get("event") == "workflow_dispatch" and _after(r)) >= MAX_DISPATCH_PER_SLOT:
        return {**base, "action": "NONE", "reason": "ATTEMPTS_EXHAUSTED"}
    return {**base, "action": "DISPATCH", "reason": "slot dropped; window open"}


def run_anchor(r: dict) -> datetime:
    """When a capture run belongs: its creation time, or -- for a clock dispatch, created LEAD minutes before its slot
    and told to wait (`not_before`) -- the slot named in its title ("clock:YYYY-MM-DDTHH:MM"). Raises on bad input."""
    created = _utc(r["createdAt"])
    title = r.get("displayTitle") or ""
    i = title.find("clock:")
    if i >= 0:
        try:
            slot = datetime.strptime(title[i + 6:i + 22], "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
            return max(created, slot)
        except ValueError:
            pass
    return created


def run_span(r: dict) -> tuple[datetime, datetime]:
    """[anchor - 1 min, end]: a published capture inside it was produced by this run. `end` is the run's last update
    (gh `updatedAt`) when known, else anchor + 30 min."""
    anchor = run_anchor(r)
    end = anchor + timedelta(minutes=30)
    try:
        end = max(end, _utc(r["updatedAt"]) + timedelta(minutes=1))
    except (KeyError, ValueError, TypeError):
        pass
    return anchor - timedelta(minutes=1), end


def trigger_for(summary: dict, runs: list[dict] | None) -> str:
    """How the run that produced a published capture was started: schedule | watchdog | manual | unknown."""
    t = run_time(summary)
    best = None
    for r in runs or []:
        try:
            lo, hi = run_span(r)
        except (KeyError, ValueError, TypeError):
            continue
        if r.get("event") in ("schedule", "workflow_dispatch") and t and lo <= t <= hi:
            if best is None or lo > best[0]:
                best = (lo, r)
    if best is None:
        return "unknown"
    r = best[1]
    if r["event"] == "schedule":
        return "schedule"
    title = r.get("displayTitle") or ""
    return "clock" if "clock" in title else ("watchdog" if "watchdog:" in title else "manual")


def assess_coverage(now: datetime, summaries: list[dict], *, runs: list[dict] | None = None,
                    lookback_hours: int = 168, grace_minutes: int = 90,
                    activated: datetime = ACTIVATED) -> dict:
    """Per-slot audit of the last `lookback_hours` of due slots against published summaries.

    Slot verdicts: COVERED | LATE | SOURCE_DEGRADED | MISSING:<cause> (cause from workflow runs when supplied,
    else UNKNOWN_CAUSE). Nothing here certifies a player's availability: absent, late, failed or empty-roster
    evidence is reported as a gap, never as "available"."""
    now = now.astimezone(timezone.utc)
    all_slots = scheduled_slots(now, activated)
    due = [x for x in all_slots if x <= now - timedelta(minutes=grace_minutes)]
    lo = now - timedelta(hours=lookback_hours)
    window = [x for x in due if x >= lo]
    matched = match_runs(due, summaries)
    trig = {sl: trigger_for(sm, runs) for sl, sm in matched.items()}
    all_runs = list(runs or [])
    if runs is not None:
        # A workflow run that produced a published capture is accounted for by that slot; it must not also be read
        # as "a run happened" for another slot whose window it merely falls inside.
        pub = [run_time(sm) for sm in matched.values()]
        def _accounted(r):
            try:
                lo, hi = run_span(r)
            except (KeyError, ValueError, TypeError):
                return False
            return any(lo <= p <= hi for p in pub)
        runs = [r for r in runs if not _accounted(r)]
    allowed = {"nflverse_injuries": GOOD_INJURY, "nflverse_depth_charts": GOOD_DEPTH,
               "espn_injuries": GOOD_ESPN, "espn_event_rosters": GOOD_ROSTER}
    slots_out, gaps = [], {"injury_report": [], "event_roster": []}
    counts: dict[str, int] = {}
    for slot in window:
        pre = is_pregame_slot(slot)
        sm = matched.get(slot)
        if sm is None:
            nxt = next((x for x in all_slots if x > slot), None)
            if runs is None:
                cause = "UNKNOWN_CAUSE"
            elif _published_late_into_next_slot(slot, nxt, all_runs, [run_time(x) for x in matched.values()]):
                cause = "RAN_LATE_PUBLISHED_IN_NEXT_SLOT"
            else:
                cause = classify_workflow_runs(slot, runs, nxt)
            verdict, late, bad = f"MISSING:{cause}", None, []
        else:
            late = round((run_time(sm) - slot).total_seconds() / 60.0, 1)
            bad = [k for k, ok in allowed.items() if (sm.get(k) or {}).get("state") not in ok]
            verdict = "SOURCE_DEGRADED" if bad else ("LATE" if late > LATE_MINUTES else "COVERED")
        counts[verdict] = counts.get(verdict, 0) + 1
        slots_out.append({"slot_utc": slot.isoformat(), "pregame": pre, "verdict": verdict,
                          "minutes_late": late, "bad_sources": bad, "trigger": trig.get(slot)})
        injury_bad = verdict.startswith("MISSING") or any(b in bad for b in ("nflverse_injuries", "espn_injuries"))
        roster_bad = pre and (verdict.startswith("MISSING") or "espn_event_rosters" in bad or verdict == "LATE")
        if injury_bad:
            gaps["injury_report"].append(slot.isoformat())
        if roster_bad:
            gaps["event_roster"].append(slot.isoformat())
    ok = bool(window) and set(counts) <= {"COVERED"}
    status = "NOT_DUE" if not window else ("COVERAGE_OK" if ok else "COVERAGE_GAPS")
    recent_lo = now - timedelta(hours=ALERT_HOURS)
    recent_gaps = [x for x in slots_out if x["verdict"] != "COVERED" and _utc(x["slot_utc"]) >= recent_lo]
    by_trigger: dict[str, int] = {}
    for x in slots_out:
        if x["trigger"]:
            by_trigger[x["trigger"]] = by_trigger.get(x["trigger"], 0) + 1
    reliability = {"due_slots": len(window), "covered_on_time": counts.get("COVERED", 0),
                   "published_any": sum(1 for x in slots_out if x["minutes_late"] is not None),
                   "published_by_trigger": by_trigger}
    return {"status": status, "lookback_hours": lookback_hours, "slot_counts": counts, "gaps": gaps,
            "reliability": reliability, "alert_hours": ALERT_HOURS,
            "recent_gaps": [{"slot_utc": x["slot_utc"], "verdict": x["verdict"]} for x in recent_gaps],
            "slots": slots_out, "availability_certified": False,
            "note": "A missing, late, failed or empty-roster capture is a gap, never evidence a player was available."}


def read_summaries_dir(store: str) -> list[dict]:
    if not Path(store).is_dir():
        raise OSError(f"store directory not found: {store}")  # never read a missing store as an empty one
    out = []
    base = Path(store) / "runs"
    for p in sorted(base.rglob("*.summary.json")) if base.is_dir() else []:
        out.append(json.loads(p.read_text(encoding="utf8")))
    return out


def all_summaries(ref: str) -> list[dict]:
    paths = [p for p in git_output("ls-tree", "-r", "--name-only", ref, PREFIX).splitlines()
             if p.endswith(".summary.json")]
    return [json.loads(git_output("show", f"{ref}:{p}")) for p in sorted(paths)]


def decide(a, now: datetime) -> int:
    """gate / watchdog modes: print the decision, export it to $GITHUB_OUTPUT. Always exit 0 (a decision is not an
    alarm); the gate fails OPEN (capture) if the store cannot be read, the watchdog fails closed (no dispatch)."""
    try:
        sums = read_summaries_dir(a.store) if a.store else all_summaries(a.ref)
        sums = [x for x in sums if (run_time(x) or now) <= now]  # only evidence that existed at `now` (matters for replay)
        if a.mode == "gate":
            d = gate_decision(now, sums, event=a.event, force=a.force)
        else:
            runs = json.loads(Path(a.runs_json).read_text(encoding="utf8")) if a.runs_json else []
            d = watchdog_decision(now, sums, runs)
    except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as exc:
        d = {"capture": True, "reason": f"GATE_ERROR fail-open: {exc}"} if a.mode == "gate" else \
            {"action": "NONE", "reason": f"STORE_UNREADABLE: {exc}"}
    print(json.dumps(d, sort_keys=True))
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf8") as fh:
            for k in ("capture", "action", "slot"):
                if k in d:
                    fh.write(f"{k}={str(d[k]).lower() if isinstance(d[k], bool) else d[k]}\n")
    if a.summary:
        with Path(a.summary).open("a", encoding="utf8") as fh:
            fh.write(f"\n### PIT capture {a.mode}\n`{json.dumps(d, sort_keys=True)}`\n")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ref", default="origin/market-data")
    ap.add_argument("--now", help="offset-aware ISO 8601 for replay only")
    ap.add_argument("--grace-minutes", type=int, default=90)
    ap.add_argument("--store", help="read summaries from a checked-out store dir (data/pit_availability/nfl) instead of --ref")
    ap.add_argument("--runs-json", help="`gh run list --json event,conclusion,status,createdAt,updatedAt,displayTitle` "
                                        "output for the capture workflow")
    ap.add_argument("--lookback-hours", type=int, default=168)
    ap.add_argument("--mode", choices=("health", "gate", "watchdog"), default="health")
    ap.add_argument("--event", default="schedule", help="gate mode: triggering event name")
    ap.add_argument("--force", action="store_true", help="gate mode: bypass the redundancy skip")
    ap.add_argument("--summary", help="append one line to GitHub Actions step summary")
    a = ap.parse_args(argv)
    if a.grace_minutes < 0:
        ap.error("--grace-minutes must be nonnegative")
    now = _utc(a.now) if a.now else datetime.now(timezone.utc)
    if a.mode != "health":
        return decide(a, now)
    try:
        sums = read_summaries_dir(a.store) if a.store else all_summaries(a.ref)
        runs = json.loads(Path(a.runs_json).read_text(encoding="utf8")) if a.runs_json else None
        latest = max(sums, key=lambda x: x.get("run_id", ""), default=None)
        result = assess(now, latest, grace_minutes=a.grace_minutes)
        cov = assess_coverage(now, sums, runs=runs, lookback_hours=a.lookback_hours, grace_minutes=a.grace_minutes)
        result["coverage"] = cov
        if result["status"] == "CAPTURE_RECORDED" and cov["recent_gaps"]:
            result["status"] = "COVERAGE_GAPS"
            result["reason"] = (f"{len(cov['recent_gaps'])} slot gap(s) due in the last {ALERT_HOURS}h: "
                                f"{[g['slot_utc'][:16] + ' ' + g['verdict'] for g in cov['recent_gaps']]}; "
                                f"{a.lookback_hours}h: {cov['slot_counts']}")
        elif result["status"] == "CAPTURE_RECORDED" and cov["status"] == "COVERAGE_GAPS":
            result["reason"] = (f"latest capture recorded; no gap in the last {ALERT_HOURS}h "
                                f"(older gaps in the {a.lookback_hours}h report: {cov['slot_counts']})")
    except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as exc:
        result = {"status": "STORE_UNREADABLE", "reason": str(exc), "owed_utc": None}
    print(json.dumps(result, sort_keys=True, indent=2))
    if a.summary:
        with Path(a.summary).open("a", encoding="utf8") as out:
            out.write("\n### NFL PIT availability capture health\n")
            out.write(f"**{result['status']}** — {result['reason']}  \n")
            if "coverage" in result:
                c = result["coverage"]
                out.write(f"Slots ({c['lookback_hours']}h): {c['slot_counts']}  \n")
                out.write(f"Injury-report gaps: {len(c['gaps']['injury_report'])}; event-roster gaps: {len(c['gaps']['event_roster'])}  \n")
            out.write("Published evidence only; not a player-prop projection or certified inactive list.\n")
    return 0 if result["status"] in {"NOT_DUE", "CAPTURE_RECORDED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
