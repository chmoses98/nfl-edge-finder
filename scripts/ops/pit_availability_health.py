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
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

PREFIX = "data/pit_availability/nfl/runs/"
# First deployment: PR #137, merged on 2026-10-12 at 04:30:52 UTC.
ACTIVATED = datetime(2026, 10, 12, 4, 30, 52, tzinfo=timezone.utc)
GOOD_INJURY = {"UNCHANGED", "NEW_CONTENT"}
GOOD_DEPTH = {"UNCHANGED", "DIGESTED"}
GOOD_ESPN = {"CAPTURED"}
GOOD_ROSTER = {"CAPTURED", "NO_GAMES_IN_WINDOW"}
LATE_MINUTES = 30        # a run later than this after its slot may have missed the roster window [T-240m, T+30m]
MAX_MATCH_HOURS = 6      # a run older than this relative to a slot is not evidence for that slot


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
    """Slots whose purpose is the ~T-90m inactive-list roster window (Sun 11-23, Mon/Thu 21-23 UTC)."""
    wd = slot.weekday()
    return (wd == 6 and 11 <= slot.hour <= 23) or (wd in (0, 3) and slot.hour in (21, 22, 23))


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


def classify_workflow_runs(slot: datetime, runs: list[dict]) -> str:
    """What GitHub says happened for an unmatched slot. `runs` = [{event, conclusion, status, createdAt}, ...]
    for the capture workflow on main (schedule / workflow_dispatch only)."""
    near = []
    for r in runs or []:
        if r.get("event") not in ("schedule", "workflow_dispatch"):
            continue
        try:
            t = _utc(r["createdAt"])
        except (KeyError, ValueError, TypeError):
            continue
        if slot <= t <= slot + timedelta(hours=MAX_MATCH_HOURS):
            near.append(r)
    if not near:
        return "NEVER_RAN"
    if all(r.get("conclusion") not in ("success", None) for r in near):
        return "RAN_FAILED"
    if any(r.get("status") != "completed" for r in near):
        return "RUN_IN_PROGRESS"
    return "RAN_SUCCESS_NO_PUBLICATION"


def assess_coverage(now: datetime, summaries: list[dict], *, runs: list[dict] | None = None,
                    lookback_hours: int = 168, grace_minutes: int = 90,
                    activated: datetime = ACTIVATED) -> dict:
    """Per-slot audit of the last `lookback_hours` of due slots against published summaries.

    Slot verdicts: COVERED | LATE | SOURCE_DEGRADED | MISSING:<cause> (cause from workflow runs when supplied,
    else UNKNOWN_CAUSE). Nothing here certifies a player's availability: absent, late, failed or empty-roster
    evidence is reported as a gap, never as "available"."""
    now = now.astimezone(timezone.utc)
    due = [x for x in scheduled_slots(now, activated) if x <= now - timedelta(minutes=grace_minutes)]
    lo = now - timedelta(hours=lookback_hours)
    window = [x for x in due if x >= lo]
    matched = match_runs(due, summaries)
    if runs is not None:
        # A workflow run that produced a published capture is accounted for by that slot; it must not also be read
        # as "a run happened" for another slot whose window it merely falls inside.
        pub = [run_time(sm) for sm in matched.values()]
        def _accounted(r):
            try:
                t = _utc(r["createdAt"])
            except (KeyError, ValueError, TypeError):
                return False
            return any(abs((t - p).total_seconds()) <= 600 for p in pub)
        runs = [r for r in runs if not _accounted(r)]
    allowed = {"nflverse_injuries": GOOD_INJURY, "nflverse_depth_charts": GOOD_DEPTH,
               "espn_injuries": GOOD_ESPN, "espn_event_rosters": GOOD_ROSTER}
    slots_out, gaps = [], {"injury_report": [], "event_roster": []}
    counts: dict[str, int] = {}
    for slot in window:
        pre = is_pregame_slot(slot)
        sm = matched.get(slot)
        if sm is None:
            cause = classify_workflow_runs(slot, runs) if runs is not None else "UNKNOWN_CAUSE"
            verdict, late, bad = f"MISSING:{cause}", None, []
        else:
            late = round((run_time(sm) - slot).total_seconds() / 60.0, 1)
            bad = [k for k, ok in allowed.items() if (sm.get(k) or {}).get("state") not in ok]
            verdict = "SOURCE_DEGRADED" if bad else ("LATE" if late > LATE_MINUTES else "COVERED")
        counts[verdict] = counts.get(verdict, 0) + 1
        slots_out.append({"slot_utc": slot.isoformat(), "pregame": pre, "verdict": verdict,
                          "minutes_late": late, "bad_sources": bad})
        injury_bad = verdict.startswith("MISSING") or any(b in bad for b in ("nflverse_injuries", "espn_injuries"))
        roster_bad = pre and (verdict.startswith("MISSING") or "espn_event_rosters" in bad or verdict == "LATE")
        if injury_bad:
            gaps["injury_report"].append(slot.isoformat())
        if roster_bad:
            gaps["event_roster"].append(slot.isoformat())
    ok = bool(window) and set(counts) <= {"COVERED"}
    status = "NOT_DUE" if not window else ("COVERAGE_OK" if ok else "COVERAGE_GAPS")
    return {"status": status, "lookback_hours": lookback_hours, "slot_counts": counts, "gaps": gaps,
            "slots": slots_out, "availability_certified": False,
            "note": "A missing, late, failed or empty-roster capture is a gap, never evidence a player was available."}


def read_summaries_dir(store: str) -> list[dict]:
    out = []
    base = Path(store) / "runs"
    for p in sorted(base.rglob("*.summary.json")) if base.is_dir() else []:
        out.append(json.loads(p.read_text(encoding="utf8")))
    return out


def all_summaries(ref: str) -> list[dict]:
    paths = [p for p in git_output("ls-tree", "-r", "--name-only", ref, PREFIX).splitlines()
             if p.endswith(".summary.json")]
    return [json.loads(git_output("show", f"{ref}:{p}")) for p in sorted(paths)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ref", default="origin/market-data")
    ap.add_argument("--now", help="offset-aware ISO 8601 for replay only")
    ap.add_argument("--grace-minutes", type=int, default=90)
    ap.add_argument("--store", help="read summaries from a checked-out store dir (data/pit_availability/nfl) instead of --ref")
    ap.add_argument("--runs-json", help="`gh run list --json event,conclusion,status,createdAt` output for the capture workflow")
    ap.add_argument("--lookback-hours", type=int, default=168)
    ap.add_argument("--summary", help="append one line to GitHub Actions step summary")
    a = ap.parse_args(argv)
    if a.grace_minutes < 0:
        ap.error("--grace-minutes must be nonnegative")
    now = _utc(a.now) if a.now else datetime.now(timezone.utc)
    try:
        sums = read_summaries_dir(a.store) if a.store else all_summaries(a.ref)
        runs = json.loads(Path(a.runs_json).read_text(encoding="utf8")) if a.runs_json else None
        latest = max(sums, key=lambda x: x.get("run_id", ""), default=None)
        result = assess(now, latest, grace_minutes=a.grace_minutes)
        cov = assess_coverage(now, sums, runs=runs, lookback_hours=a.lookback_hours, grace_minutes=a.grace_minutes)
        result["coverage"] = cov
        if result["status"] == "CAPTURE_RECORDED" and cov["status"] == "COVERAGE_GAPS":
            result["status"] = "COVERAGE_GAPS"
            result["reason"] = f"latest capture recorded, but slot gaps in last {a.lookback_hours}h: {cov['slot_counts']}"
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
