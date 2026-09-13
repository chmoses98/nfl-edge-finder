#!/usr/bin/env python3
"""Print the active (or most recently completed) regular-season week number from the schedule. Stdlib only.

    WEEK=$(python3 scripts/shadow_v2/active_week.py --market-data /tmp/md)

The weekly report and research export are keyed by week; the settle job runs after kickoff, so the week whose
games most recently kicked off is the one with new evidence. Falls back to week 1 when nothing has kicked off.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.data.nfl_calendar import load_schedule                                    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default=None)
    ap.add_argument("--now", default=None)
    a = ap.parse_args()
    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    try:
        games, _ = load_schedule(ROOT, market_data=a.market_data, allow_download=False)
    except Exception:  # noqa: BLE001
        print(1); return 0
    played = []
    for g in games:
        ko = g.get("kickoff_utc")
        if ko is None or g.get("game_type") not in (None, "REG") or not g.get("week"):
            continue
        ko = ko if isinstance(ko, datetime) else datetime.fromisoformat(str(ko).replace("Z", "+00:00"))
        if ko <= now:
            played.append((int(g.get("season") or 0), int(g["week"])))
    if not played:
        print(1); return 0
    season = max(s for s, _ in played)
    print(max(w for s, w in played if s == season))
    return 0


if __name__ == "__main__":
    sys.exit(main())
