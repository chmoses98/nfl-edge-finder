#!/usr/bin/env python3
"""Self-clocked lane for the NFL PIT availability capture (research only).

Why: GitHub's scheduler is not a clock for this repository. From 2026-10-20 to 10-28 it never created 36% of the
capture cron events (26 of 72; Sunday 10-25 11:47-13:47 and Monday 10-26 21:47-22:47 had none at all), created the
report-day ones 2.2-5.5 h late, and never created 67% of the watchdog's own cron events -- so the cron-driven
watchdog failed exactly when it was needed. Jobs then waited for a runner (median 2 min, p90 34, max 92) because
the account's long-running conductors hold most runners.

What this does: ONE long-lived job (`.github/workflows/pit-availability-clock.yml`, its own concurrency lane) keeps
time itself. For every capture slot inside its ~5.7 h life it:

  1. dispatches the EXISTING capture workflow `LEAD_MIN` minutes before the slot with `not_before=<slot>`; that run
     takes a runner early, waits until the slot, then runs the unchanged "Slot gate" (skip if the slot already has a
     published capture) and captures -- so the runner queue is absorbed before the slot instead of after it;
  2. from `slot + VERIFY_AFTER_MIN` re-checks the PUBLISHED store with the watchdog's own rule
     (`watchdog_decision`: dispatch only while the slot's window is open, nothing in flight, at most 3 attempts).

Before it ends it dispatches its successor when another slot falls inside the next lane's life, so the lane spans a
whole capture day; frequent crons restart it if the chain ever breaks, and the per-slot crons and the cron watchdog
stay as independent fallbacks.

What it never does: capture or publish by itself (every capture goes through the one capture workflow, its single
concurrency group and its gate, so duplicate triggers cannot produce two captures for one slot), backfill, or stamp
anything other than the capture's real retrieval time. A slot it cannot reach stays a visible gap in the health check.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ops.pit_availability_health import (
    PREGAME_DISPATCH_MIN,
    REPORT_DISPATCH_MIN,
    is_pregame_slot,
    latest_slot,
    read_summaries_dir,
    upcoming_slots,
    watchdog_decision,
)

LEAD_MIN = 25            # dispatch this long before the slot: absorbs the runner queue (p90 34 min) before the slot
MAX_WAIT_MIN = 50        # the capture workflow refuses to wait longer than this for `not_before`
VERIFY_AFTER_MIN = 20    # first published-store check after the slot (a capture takes ~2-12 min)
RECHECK_MIN = 10         # then every 10 minutes while the slot's window is open
LIFETIME_MIN = 340       # a hosted job may run 360 min; leave room to hand over
HANDOVER_MIN = 3         # stop planning new dispatches this close to the deadline


def _utc(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UTC)


def window_min(slot: datetime) -> int:
    return PREGAME_DISPATCH_MIN if is_pregame_slot(slot) else REPORT_DISPATCH_MIN


def plan(start: datetime, deadline: datetime, chained: bool = False) -> list[dict]:
    """Slots this lane serves: every slot whose dispatch time (slot - LEAD_MIN) falls before the hand-over point. A
    slot whose verification outlives this lane is verified by the successor's catch-up check, so report-day slots 6 h
    apart are served by consecutive ~5.7 h lanes without a gap.

    A slot whose dispatch time has already passed is dispatched now by a lane the crons started (nobody else did), but
    only VERIFIED by a chained lane: its predecessor dispatched it, and the verification re-dispatches if it is
    still unpublished (the capture's gate would skip a duplicate anyway; this avoids the extra run)."""
    out = []
    last_dispatch = deadline - timedelta(minutes=HANDOVER_MIN)
    for slot in upcoming_slots(start, deadline + timedelta(minutes=LEAD_MIN)):
        due = slot - timedelta(minutes=LEAD_MIN)
        if due > last_dispatch:
            continue
        overdue = due < start
        out.append({"slot": slot, "dispatch_at": max(due, start), "dispatch": not (chained and overdue)})
    return out


def wants_successor(now: datetime, lifetime_min: int = LIFETIME_MIN) -> bool:
    """Hand over only if a successor starting now has work: a slot it can dispatch within its own life, or the
    latest slot still inside its window (to verify / retry). Otherwise no runner is held through an idle stretch
    (Monday night to Wednesday); the crons start the next lane."""
    if plan(now, now + timedelta(minutes=lifetime_min), chained=True):
        return True
    last = latest_slot(now)
    return last is not None and now < last + timedelta(minutes=window_min(last))


# ------------------------------------------------------------------ I/O (GitHub CLI + the published store)

def _sh(*args: str, check: bool = True) -> str:
    return subprocess.run(args, check=check, capture_output=True, text=True).stdout


def published_summaries(dest: str) -> list[dict]:
    _sh("bash", "scripts/pit_availability/checkout_store.sh", dest)
    return read_summaries_dir(f"{dest}/data/pit_availability/nfl")


def capture_runs() -> list[dict]:
    out = _sh("gh", "run", "list", "--workflow", "pit-availability-nfl.yml", "--branch", "main", "--limit", "100",
              "--json", "event,conclusion,status,createdAt,updatedAt,displayTitle")
    return json.loads(out or "[]")


def dispatch_capture(slot: datetime, reason: str, not_before: datetime | None, dry: bool) -> None:
    cmd = ["gh", "workflow", "run", "pit-availability-nfl.yml", "--ref", "main", "-f", f"reason={reason}"]
    if not_before is not None:
        cmd += ["-f", f"not_before={not_before.strftime('%Y-%m-%dT%H:%M:%SZ')}"]
    log({"event": "DISPATCH", "slot": slot.isoformat(), "reason": reason, "dry_run": dry, "cmd": " ".join(cmd)})
    if not dry:
        _sh(*cmd)


def dispatch_successor(dry: bool) -> None:
    cmd = ["gh", "workflow", "run", "pit-availability-clock.yml", "--ref", "main", "-f", "reason=chain"]
    log({"event": "CHAIN", "dry_run": dry, "cmd": " ".join(cmd)})
    if not dry:
        _sh(*cmd)


def log(d: dict) -> None:
    print(json.dumps({"at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), **d}, sort_keys=True), flush=True)


def sleep_until(t: datetime) -> None:
    while True:
        left = (t - datetime.now(UTC)).total_seconds()
        if left <= 0:
            return
        time.sleep(min(left, 300))


def verify(slot: datetime, deadline: datetime, store: str, dry: bool) -> str:
    """Re-check the published store for `slot` until it is covered or its window closes (or the lane ends)."""
    close = slot + timedelta(minutes=window_min(slot))
    t = slot + timedelta(minutes=VERIFY_AFTER_MIN)
    while t <= min(close, deadline):
        sleep_until(t)
        now = datetime.now(UTC)
        try:
            d = watchdog_decision(now, published_summaries(store), capture_runs())
        except (subprocess.CalledProcessError, OSError, ValueError, json.JSONDecodeError) as exc:
            d = {"action": "NONE", "reason": f"CHECK_FAILED: {exc}"}  # fails closed, like the watchdog
        log({"event": "VERIFY", "slot": slot.isoformat(), **{k: v for k, v in d.items() if k != "slot"},
             "decision_slot": d.get("slot")})
        if d.get("reason") in ("COVERED", "WINDOW_CLOSED_GAP_REMAINS", "ATTEMPTS_EXHAUSTED"):
            return d["reason"]
        if d.get("action") == "DISPATCH" and d.get("slot") == slot.isoformat():
            dispatch_capture(slot, f"clock-retry:{slot.strftime('%Y-%m-%dT%H:%M')}", None, dry)
        t = now + timedelta(minutes=RECHECK_MIN)
    return "LANE_ENDED_OR_WINDOW_CLOSED"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--store", default="/tmp/pit_md_clock")
    ap.add_argument("--lifetime-min", type=int, default=LIFETIME_MIN)
    ap.add_argument("--dry-run", action="store_true", help="plan and log; dispatch nothing")
    ap.add_argument("--plan-only", action="store_true", help="print the plan for this lane and exit")
    ap.add_argument("--no-chain", dest="chain", action="store_false", help="never dispatch a successor lane")
    ap.add_argument("--chained", action="store_true", help="this lane was started by its predecessor")
    a = ap.parse_args(argv)
    start = datetime.now(UTC)
    deadline = start + timedelta(minutes=a.lifetime_min)
    slots = plan(start, deadline, chained=a.chained)
    log({"event": "LANE_START", "deadline": deadline.isoformat(), "slots": [x["slot"].isoformat() for x in slots]})
    if a.plan_only:
        return 0
    # catch-up first: the latest past slot, if it is uncovered and still inside its window (the watchdog's rule)
    last = latest_slot(start)
    if last is not None and start < last + timedelta(minutes=window_min(last)):
        verify(last, deadline, a.store, a.dry_run)
    for x in slots:
        sleep_until(x["dispatch_at"])
        if x["dispatch"]:
            dispatch_capture(x["slot"], f"clock:{x['slot'].strftime('%Y-%m-%dT%H:%M')}", x["slot"], a.dry_run)
        outcome = verify(x["slot"], deadline, a.store, a.dry_run)
        log({"event": "SLOT_DONE", "slot": x["slot"].isoformat(), "outcome": outcome})
    if a.chain and wants_successor(datetime.now(UTC), a.lifetime_min):
        dispatch_successor(a.dry_run)
        log({"event": "LANE_END", "chained": True})
    else:
        log({"event": "LANE_END", "chained": False})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
