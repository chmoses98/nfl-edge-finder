#!/usr/bin/env python3
"""DEAD-CHAIN ALARM for the self-chaining conductors.

    python3 scripts/ops/conductor_health.py --workflow horizon-conductor.yml --workflow kalshi-conductor.yml \
        --optional chmoses98/kalshi-bet-router:router-conductor.yml --restart --summary "$GITHUB_STEP_SUMMARY"

Each conductor keeps itself alive by dispatching its successor, with an hourly cron as the backstop -- and that cron
is the same best-effort scheduler that made the conductors necessary. A chain that dies (a refused dispatch AND a
dropped cron tick) would otherwise be discovered by a missed horizon. This reads each chain's recent runs and names
it ALIVE, DEAD or ABSENT (nfl_edge/handicap/automation.chain_health).

  * a DEAD required chain makes this exit 1 -- a red workflow-health run -- after, with --restart, dispatching that
    conductor once (idempotent: its concurrency group collapses any surplus into one pending run);
  * `--optional owner/repo:workflow` is monitored in another repository (read-only; never restarted from here) and
    never turns the run red -- a chain in a repository whose conductor is not merged yet reads ABSENT.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.handicap.automation import chain_health  # noqa: E402


def list_runs(workflow: str, repo: str | None = None):
    argv = ["gh", "run", "list", "--workflow", workflow, "--limit", "10",
            "--json", "status,conclusion,createdAt,updatedAt,event"]
    if repo:
        argv += ["-R", repo]
    r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout or "[]")
    except ValueError:
        return None


def restart(workflow: str) -> tuple[bool, str]:
    r = subprocess.run(["gh", "workflow", "run", workflow, "--ref", "main"], capture_output=True, text=True, timeout=60)
    return r.returncode == 0, (r.stderr or r.stdout).strip()[:200]


def evaluate(required, optional, now, *, lister=list_runs, restarter=restart, do_restart=False):
    rows, red = [], False
    for wf in required:
        h = chain_health(lister(wf), now)
        # ABSENT on a required chain means we could not even read it: that is not "fine".
        if h["status"] in ("DEAD", "ABSENT"):
            red = True
            if do_restart:
                ok, msg = restarter(wf)
                h["restart"] = {"dispatched": ok, "message": msg}
        rows.append({"workflow": wf, "required": True, **h})
    for spec in optional:
        repo, _, wf = spec.rpartition(":")
        h = chain_health(lister(wf, repo or None), now)
        rows.append({"workflow": spec, "required": False, **h})
    return rows, red


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", action="append", default=[])
    ap.add_argument("--optional", action="append", default=[])
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--summary", default=None)
    a = ap.parse_args(argv)
    rows, red = evaluate(a.workflow, a.optional, datetime.now(timezone.utc), do_restart=a.restart)
    lines = ["## Conductor chains", "", "| chain | required | status | detail |", "|---|---|---|---|"]
    for r in rows:
        extra = f" -- restart dispatched: {r['restart']['dispatched']}" if r.get("restart") else ""
        lines.append(f"| {r['workflow']} | {r['required']} | **{r['status']}** | {r['reason']}{extra} |")
        print(json.dumps(r))
        if r["required"] and r["status"] != "ALIVE":
            print(f"::error::conductor chain {r['workflow']} is {r['status']}: {r['reason']}")
    if a.summary:
        with open(a.summary, "a") as f:
            f.write("\n".join(lines) + "\n")
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
