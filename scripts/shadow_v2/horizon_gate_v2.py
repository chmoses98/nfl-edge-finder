#!/usr/bin/env python3
"""Decide, cheaply, whether a shadow-v2 decision-horizon projection is owed right now (T-24h / T-6h / T-90m / T-30m).

    python3 scripts/shadow_v2/horizon_gate_v2.py --markers <file listing marker names> --allow-download --github-output "$GITHUB_OUTPUT"

Stdlib only. Same `due_horizons` rule as the incumbent conductors, against the v2 marker directory
(`data/shadow/v2/horizons/` on market-data, append-only). A horizon whose kickoff has passed is MISSED and is
never reconstructed; the missed list is printed so the report can say which horizons the record lacks.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.data.nfl_calendar import load_schedule, resolve_active_week          # noqa: E402
from nfl_edge.projection import horizons as HZ                                     # noqa: E402


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
        out = HZ.due(week["slate_id"], week["games"], now, names)
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
