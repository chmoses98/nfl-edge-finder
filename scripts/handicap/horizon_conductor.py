#!/usr/bin/env python3
"""HORIZON CONDUCTOR for RUN NFL and the three-arm game-centre freeze. See nfl_edge/handicap/conductor.py.

    python3 scripts/handicap/horizon_conductor.py --minutes 340 --interval 240 --chain-workflow horizon-conductor.yml

Every pass, for each target:

  * RUN_NFL   -- capture state is `handicap-reports:state/horizons.json`; dispatches `run-nfl-horizons.yml`.
  * THREE_ARM -- capture state is the marker file names under `market-data:data/shadow/arms/horizons/`;
                 dispatches `three-arm-horizons.yml`.

it asks the SAME due rule the workflow's own gate uses (`nfl_edge.handicap.horizons.due_horizons`) and, when a
horizon is owed and no run of that workflow is already queued or running, dispatches one. Near the end of its
job it dispatches its own successor (`--chain-workflow`) so the next conductor does not depend on cron.

Every decision is one JSON line in the log: that line is the audit trail for "was a due horizon recognised,
and was a build started for it".
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.arms.horizons import captured_state                                   # noqa: E402
from nfl_edge.data.nfl_calendar import load_schedule, resolve_active_week           # noqa: E402
from nfl_edge.handicap.conductor import decide, should_chain                         # noqa: E402
from nfl_edge.handicap.horizons import HORIZONS_MIN, due_horizons                    # noqa: E402

TARGETS = {
    "RUN_NFL": {"workflow": "run-nfl-horizons.yml"},
    "THREE_ARM": {"workflow": "three-arm-horizons.yml"},
}


def _git(*args, timeout=180):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=timeout)


def run_nfl_state() -> dict:
    """The RUN NFL capture state, as the gate reads it. Unreadable -> {} (everything uncaptured is due, and the
    workflow's own gate, reading the same file, is what finally decides)."""
    _git("fetch", "--depth=1", "origin", "handicap-reports")
    r = _git("show", "origin/handicap-reports:state/horizons.json", timeout=60)
    try:
        return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}
    except ValueError:
        return {}


def three_arm_state() -> dict:
    _git("fetch", "--depth=1", "--filter=blob:none", "origin", "market-data")
    r = _git("ls-tree", "--name-only", "origin/market-data", "data/shadow/arms/horizons/", timeout=60)
    return captured_state([os.path.basename(x) for x in r.stdout.split() if x.strip()])


STATE_READERS = {"RUN_NFL": run_nfl_state, "THREE_ARM": three_arm_state}


def active_runs(workflow: str) -> int:
    n = 0
    for status in ("queued", "in_progress", "waiting", "pending", "requested"):
        r = subprocess.run(["gh", "run", "list", "--workflow", workflow, "--status", status, "--json", "databaseId"],
                           cwd=ROOT, capture_output=True, text=True, timeout=60)
        try:
            n += len(json.loads(r.stdout or "[]"))
        except ValueError:
            pass
    return n


def dispatch(workflow: str, ref: str) -> tuple[bool, str]:
    r = subprocess.run(["gh", "workflow", "run", workflow, "--ref", ref], cwd=ROOT, capture_output=True, text=True,
                       timeout=60)
    return r.returncode == 0, (r.stderr or r.stdout).strip()[:300]


def one_pass(targets, games, src, now, dispatched, *, dry_run=False, ref="main",
             state_readers=None, active=None, dispatcher=None) -> list:
    """Evaluate every target once. Returns one log line per target. Injection points exist for tests."""
    state_readers = state_readers or STATE_READERS
    active = active or active_runs
    dispatcher = dispatcher or dispatch
    lines = []
    week = resolve_active_week(games, now, schedule_source=src)
    for name in targets:
        wf = TARGETS[name]["workflow"]
        line = {"at": now.isoformat(), "target": name, "workflow": wf}
        if week["status"] != "OK":
            line.update(decision="idle", reason=week.get("reason"))
            lines.append(line)
            continue
        # CHEAP FIRST: with nothing captured, is anything even in its window? If not, no capture state can make
        # something due, so the git fetches that read the state are skipped -- most passes of the week.
        if not due_horizons(week["slate_id"], week["games"], now, {}, horizons_min=HORIZONS_MIN).get("due"):
            d = due_horizons(week["slate_id"], week["games"], now, {}, horizons_min=HORIZONS_MIN)
        else:
            d = due_horizons(week["slate_id"], week["games"], now, state_readers[name](), horizons_min=HORIZONS_MIN)
        due_ids = [r["horizon_id"] for r in (d.get("due") or [])]
        n_active = active(wf) if due_ids and not dry_run else 0
        go, why = decide(due_ids, dispatched.setdefault(name, {}), now, n_active)
        line.update(decision=("dispatch" if go else "wait"), reason=why, due=due_ids,
                    due_lateness_min=[r["late_by_min"] for r in (d.get("due") or [])],
                    missed=[r["horizon_id"] for r in (d.get("missed") or [])],
                    next_pending=(d.get("next_pending") or {}).get("horizon_id"))
        if go:
            ok, msg = (True, "dry run") if dry_run else dispatcher(wf, ref)
            line.update(dispatched=ok, message=msg)
            if ok:
                dispatched[name][frozenset(due_ids)] = now
        lines.append(line)
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=340.0)
    ap.add_argument("--interval", type=float, default=240.0)
    ap.add_argument("--targets", default="RUN_NFL,THREE_ARM")
    ap.add_argument("--ref", default="main")
    ap.add_argument("--chain-workflow", default=None,
                    help="dispatch this workflow once, near the end, so the next conductor does not depend on cron")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    targets = [t.strip() for t in a.targets.split(",") if t.strip() in TARGETS]
    end = time.time() + a.minutes * 60
    dispatched: dict = {}
    chained = False
    games, src, loaded = None, None, 0.0
    while time.time() < end:
        t0 = time.time()
        now = datetime.now(timezone.utc)
        try:
            if games is None or t0 - loaded > 3600:
                games, src = load_schedule(ROOT, allow_download=True)
                loaded = t0
            for line in one_pass(targets, games, src, now, dispatched, dry_run=a.dry_run, ref=a.ref):
                print(json.dumps(line, default=str), flush=True)
        except Exception as exc:  # noqa: BLE001 -- one bad pass must not end the conductor
            print(json.dumps({"at": now.isoformat(), "decision": "error",
                              "reason": f"{type(exc).__name__}: {str(exc)[:200]}"}), flush=True)
        if a.chain_workflow and should_chain(time.time(), end, chained):
            ok, msg = (True, "dry run") if a.dry_run else dispatch(a.chain_workflow, a.ref)
            print(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "decision": "chain",
                              "workflow": a.chain_workflow, "dispatched": ok, "message": msg}), flush=True)
            # A refused chain dispatch is retried on the next pass; the hourly cron is the backstop after that.
            chained = ok
        time.sleep(max(5.0, min(a.interval - (time.time() - t0), end - time.time())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
