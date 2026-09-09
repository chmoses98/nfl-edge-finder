#!/usr/bin/env python3
"""Record decision horizons as captured -- called ONLY after a report build succeeded and verified.

    python3 scripts/handicap/mark_horizons.py --state in.json --out out.json \
        --horizon-ids "2026-REG-01|20260913T1700Z|T-90m,..." --run-id 123

Separating this from the gate is the point: if the expensive build fails, nothing marks the horizon, and the
next wake finds it still due. A gate that consumed the horizon before knowing the build worked would delete
a decision moment on every flaky runner.

Ids are self-describing (`<slate_id>|<cluster kickoff>|T-<n>m`), so only the id list has to travel between
workflow jobs.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.horizons import mark_captured, parse_horizon_id, prune  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="mark decision horizons captured")
    ap.add_argument("--state", default=None, help="existing state file (missing = empty)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--horizon-ids", default="")
    ap.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID"))
    ap.add_argument("--now", default=None)
    ap.add_argument("--keep-days", type=int, default=45)
    a = ap.parse_args()

    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    state = {}
    if a.state and os.path.exists(a.state):
        try:
            state = json.load(open(a.state))
        except ValueError:
            print(f"::warning::{a.state} is unreadable; starting from an empty horizon state")

    ids = [h.strip() for h in a.horizon_ids.split(",") if h.strip()]
    records, bad = [], []
    for hid in ids:
        try:
            records.append(parse_horizon_id(hid))
        except ValueError as e:
            bad.append(str(e))
    if bad:
        print("FAIL: " + "; ".join(bad), file=sys.stderr)
        return 2

    state = mark_captured(state, records, run_id=a.run_id, now=now)
    state = prune(state, now, keep_days=a.keep_days)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(state, f, indent=1, sort_keys=True)
    print(f"marked {len(records)} horizon(s) captured; state now holds "
          f"{len(state.get('captured') or {})} record(s) -> {a.out}")
    for r in records:
        print(f"  {r['horizon_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
