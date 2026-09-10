#!/usr/bin/env python3
"""Decide, cheaply, whether a three-arm decision-horizon snapshot is owed right now.

    python3 scripts/shadow/three_arm_horizon_gate.py --markers <file listing marker names> --allow-download \
        --github-output "$GITHUB_OUTPUT"

Stdlib only, network-free given a schedule (or one 2 MB download): resolves the active week, clusters the
kickoffs and applies the SAME `due_horizons` rule as the report conductor, against the append-only marker
files on market-data (`nfl_edge/arms/horizons.py`). A horizon whose kickoff has passed is MISSED and is never
reconstructed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.arms.horizons import captured_state                                  # noqa: E402
from nfl_edge.data.nfl_calendar import load_schedule, resolve_active_week          # noqa: E402
from nfl_edge.handicap.horizons import HORIZONS_MIN, due_horizons                  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default=None)
    ap.add_argument("--schedule", default=None)
    ap.add_argument("--allow-download", action="store_true")
    ap.add_argument("--markers", default=None, help="text file: one captured-horizon marker file name per line")
    ap.add_argument("--now", default=None)
    ap.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    a = ap.parse_args()
    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    try:
        games, src = load_schedule(ROOT, market_data=a.market_data, path=a.schedule, allow_download=a.allow_download)
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: cannot read the schedule: {e}", file=sys.stderr)
        return 6
    week = resolve_active_week(games, now, schedule_source=src)
    if week["status"] != "OK":
        out = {"should_run": False, "reason": f"no active slate: {week['reason']}", "due": [], "missed": []}
    else:
        names = []
        if a.markers and os.path.exists(a.markers):
            names = [ln.strip() for ln in open(a.markers) if ln.strip()]
        out = due_horizons(week["slate_id"], week["games"], now, captured_state(names), horizons_min=HORIZONS_MIN)
        out["captured_markers"] = len(names)
    print(json.dumps({k: v for k, v in out.items() if k != "slate"}, indent=1, default=str))
    if a.github_output:
        due = out.get("due") or []
        with open(a.github_output, "a") as f:
            f.write(f"should_run={'true' if out['should_run'] else 'false'}\n")
            f.write(f"reason={out['reason']}\n")
            f.write(f"season={week.get('season') or ''}\n")
            f.write(f"horizon_ids={','.join(r['horizon_id'] for r in due)}\n")
            f.write(f"missed={len(out.get('missed') or [])}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
