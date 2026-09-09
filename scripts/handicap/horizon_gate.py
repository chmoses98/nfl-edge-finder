#!/usr/bin/env python3
"""Decision-horizon gate: decide, cheaply, whether a fresh handicap packet is owed right now.

    python3 scripts/handicap/horizon_gate.py --market-data /tmp/md --state <path> \
        --github-output "$GITHUB_OUTPUT"

This runs on every wake of the horizon conductor and is deliberately stdlib-only and network-free (given a
local schedule), so a wake that has nothing to do costs seconds. It resolves the active week, clusters the
slate's kickoffs, and reports which of the T-24h / T-6h / T-90m / T-30m horizons are due and uncaptured.

It does NOT mark anything captured. Capture is recorded by the publish step only after a build succeeded --
a failed expensive run must leave the horizon due, or one bad runner permanently deletes a decision moment.

Exit code is always 0 when the gate could answer; `should_run` in the outputs is the answer. Exit 6 means
the gate could not read the schedule or the active week, which is a fail-closed refusal rather than "no".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.data.nfl_calendar import load_schedule, resolve_active_week  # noqa: E402
from nfl_edge.handicap.horizons import HORIZONS_MIN, due_horizons  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="should a fresh handicap report be built right now?")
    ap.add_argument("--market-data", default=None)
    ap.add_argument("--schedule", default=None)
    ap.add_argument("--allow-download", action="store_true")
    ap.add_argument("--state", default=None, help="horizon capture state JSON (missing = nothing captured)")
    ap.add_argument("--now", default=None)
    ap.add_argument("--horizons", default=",".join(str(h) for h in HORIZONS_MIN),
                    help="comma-separated minutes before kickoff")
    ap.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()

    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    try:
        games, src = load_schedule(ROOT, market_data=a.market_data, path=a.schedule,
                                   allow_download=a.allow_download)
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: cannot read the schedule: {e}", file=sys.stderr)
        return 6

    week = resolve_active_week(games, now, schedule_source=src)
    if week["status"] != "OK":
        out = {"should_run": False, "reason": f"no active slate: {week['reason']}",
               "slate_status": week["status"], "due": [], "missed": [], "slate": week}
    else:
        state = {}
        if a.state and os.path.exists(a.state):
            try:
                state = json.load(open(a.state))
            except ValueError:
                print(f"::warning::horizon state at {a.state} is unreadable; treating as empty")
        horizons = [int(x) for x in a.horizons.split(",") if x.strip()]
        out = due_horizons(week["slate_id"], week["games"], now, state, horizons_min=horizons)
        out["slate_status"] = "OK"
        out["slate"] = week

    print(json.dumps({k: v for k, v in out.items() if k != "slate"}, indent=1))
    print(f"\nreason: {out['reason']}")
    if a.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.json_out)), exist_ok=True)
        with open(a.json_out, "w") as f:
            json.dump(out, f, indent=1)

    if a.github_output:
        slate = out.get("slate") or {}
        due = out.get("due") or []
        with open(a.github_output, "a") as f:
            f.write(f"should_run={'true' if out['should_run'] else 'false'}\n")
            f.write(f"reason={out['reason']}\n")
            f.write(f"season={slate.get('season') or ''}\n")
            f.write(f"week={slate.get('week') or ''}\n")
            f.write(f"slate_id={slate.get('slate_id') or ''}\n")
            f.write(f"horizon_ids={','.join(r['horizon_id'] for r in due)}\n")
            f.write(f"tightest_horizon_min={due[0]['horizon_min'] if due else ''}\n")
            f.write(f"missed={len(out.get('missed') or [])}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
