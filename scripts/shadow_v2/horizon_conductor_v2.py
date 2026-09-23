#!/usr/bin/env python3
"""HORIZON CONDUCTOR: dispatch the Shadow v2 horizon freeze when it is due, instead of hoping cron fires.

Why. `shadow-v2-horizons.yml` is scheduled `*/15` but GitHub started it only 67 times in its first ten days --
roughly every two to five hours. On 2026-09-20 it ran at 05:26, 09:54, 13:49 and 17:08 UTC, so the 1pm
cluster's T-6h freeze (due 11:00) was served at 13:39 against a market 159 minutes later than intended, and its
T-90m freeze (due 15:30) never happened. The gate and the projector were correct; they were simply not started.
The capture conductor solved the same problem for captures by looping inside one long job; this does the same
for horizons, and it is deliberately small: it never projects anything itself.

    python3 scripts/shadow_v2/horizon_conductor_v2.py --minutes 345 --interval 300 \
        --workflow shadow-v2-horizons.yml --ref main

Every pass: read the captured markers from market-data, ask the same `due` rule the gate uses, and when a
horizon is owed and no horizon run is already queued or running, dispatch one (`gh workflow run`). A dispatch is
not repeated for the same horizon set within REDISPATCH_MIN, so a slow projection is never stacked. Every
decision is one JSON line in the log.
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
from nfl_edge.data.nfl_calendar import load_schedule, resolve_active_week          # noqa: E402
from nfl_edge.projection import horizons as HZ                                     # noqa: E402

REDISPATCH_MIN = 45.0


def decide(due_ids: list, dispatched: dict, now: datetime, active_runs: int) -> tuple[bool, str]:
    """Pure decision: dispatch now?  `dispatched` maps a frozenset of horizon ids -> the instant it was sent."""
    if not due_ids:
        return False, "nothing due"
    if active_runs > 0:
        return False, f"{active_runs} horizon run(s) already queued or running: they will serve what is due"
    key = frozenset(due_ids)
    last = dispatched.get(key)
    if last is not None and (now - last).total_seconds() < REDISPATCH_MIN * 60:
        return False, f"dispatched {((now - last).total_seconds() / 60):.0f} min ago for the same horizons"
    return True, f"due: {sorted(due_ids)}"


def markers_on_market_data() -> list:
    subprocess.run(["git", "fetch", "--depth=1", "--filter=blob:none", "origin", "market-data"], cwd=ROOT,
                   capture_output=True, text=True, timeout=180)
    r = subprocess.run(["git", "ls-tree", "--name-only", "origin/market-data", "data/shadow/v2/horizons/"], cwd=ROOT,
                       capture_output=True, text=True, timeout=60)
    return [os.path.basename(x) for x in r.stdout.split() if x.strip()]


def active_horizon_runs(workflow: str) -> int:
    n = 0
    for status in ("queued", "in_progress"):
        r = subprocess.run(["gh", "run", "list", "--workflow", workflow, "--status", status, "--json", "databaseId"],
                           cwd=ROOT, capture_output=True, text=True, timeout=60)
        try:
            n += len(json.loads(r.stdout or "[]"))
        except ValueError:
            pass
    return n


def dispatch(workflow: str, ref: str) -> tuple[bool, str]:
    r = subprocess.run(["gh", "workflow", "run", workflow, "--ref", ref], cwd=ROOT, capture_output=True, text=True, timeout=60)
    return r.returncode == 0, (r.stderr or r.stdout).strip()[:300]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=345.0)
    ap.add_argument("--interval", type=float, default=300.0)
    ap.add_argument("--workflow", default="shadow-v2-horizons.yml")
    ap.add_argument("--ref", default="main")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    end = time.time() + a.minutes * 60
    dispatched: dict = {}
    games, src, loaded = None, None, 0.0
    while time.time() < end:
        t0 = time.time()
        now = datetime.now(timezone.utc)
        line = {"at": now.isoformat()}
        try:
            if games is None or t0 - loaded > 3600:
                games, src = load_schedule(ROOT, allow_download=True)
                loaded = t0
            week = resolve_active_week(games, now, schedule_source=src)
            if week["status"] != "OK":
                line.update(decision="idle", reason=week.get("reason"))
            else:
                d = HZ.due(week["slate_id"], week["games"], now, markers_on_market_data())
                due_ids = [r["horizon_id"] for r in (d.get("due") or [])]
                active = active_horizon_runs(a.workflow) if due_ids and not a.dry_run else 0
                go, why = decide(due_ids, dispatched, now, active)
                line.update(decision=("dispatch" if go else "wait"), reason=why, due=due_ids, missed=len(d.get("missed") or []))
                if go:
                    ok, msg = (True, "dry run") if a.dry_run else dispatch(a.workflow, a.ref)
                    line.update(dispatched=ok, message=msg)
                    if ok:
                        dispatched[frozenset(due_ids)] = now
        except Exception as exc:  # noqa: BLE001 -- one bad pass must not end the conductor
            line.update(decision="error", reason=f"{type(exc).__name__}: {str(exc)[:200]}")
        print(json.dumps(line, default=str), flush=True)
        time.sleep(max(5.0, a.interval - (time.time() - t0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
