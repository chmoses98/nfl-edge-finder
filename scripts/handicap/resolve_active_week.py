#!/usr/bin/env python3
"""Resolve the active NFL season/week from the canonical schedule. Machine-readable, fail-closed.

    python3 scripts/handicap/resolve_active_week.py --market-data /tmp/md --github-output "$GITHUB_OUTPUT"

Prints the resolution as JSON and, with --github-output, writes `status`, `season`, `week`, `season_type`,
`slate_id`, `label`, `reason` and `minutes_to_first_kickoff` as workflow step outputs.

Exit codes
  0  a slate was resolved (status=OK)
  0  no slate, with --allow-no-slate (status=NO_SLATE) -- the caller skips rather than fails
  6  no slate and --allow-no-slate not given
  7  no schedule could be read at all

The whole point is that nothing downstream hard-codes a week. A resolver that cannot tell must say so; it
must never return a plausible number.
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


def apply_pins(res: dict, pin_season, pin_week, games) -> dict:
    """A caller-supplied season/week overrides the resolution -- and says so.

    Pinning is an override, never a silent agreement: the resolved values stay in the payload under
    `auto_*` so a manual run that disagrees with the calendar is visible rather than indistinguishable
    from an automatic one.
    """
    pin_season = int(pin_season) if str(pin_season or "").strip() else None
    pin_week = int(pin_week) if str(pin_week or "").strip() else None
    if pin_season is None and pin_week is None:
        return res
    out = dict(res, auto_status=res.get("status"), auto_season=res.get("season"),
               auto_week=res.get("week"), pinned=True)
    out["season"] = pin_season if pin_season is not None else res.get("season")
    out["week"] = pin_week if pin_week is not None else res.get("week")
    if out["season"] is None or out["week"] is None:
        out["status"] = "NO_SLATE"
        out["reason"] = ("a season/week was pinned only in part and the calendar could not supply the "
                         f"other half ({res.get('reason')})")
        return out
    from nfl_edge.data.nfl_calendar import week_blocks
    block = next((b for b in week_blocks(games)
                  if b["season"] == out["season"] and b["week"] == out["week"]
                  and b["season_type"] != "PRE"), None)
    out["status"] = "OK"
    out["reason"] = None
    if block:
        out.update({"season_type": block["season_type"], "slate_id": block["slate_id"],
                    "label": block["label"] + " (pinned by the caller)",
                    "first_kickoff_utc": (block["first_kickoff"].isoformat()
                                          if block["first_kickoff"] else None),
                    "last_kickoff_utc": (block["last_kickoff"].isoformat()
                                         if block["last_kickoff"] else None),
                    "games_scheduled": block["games_scheduled"]})
    else:
        out["status"] = "NO_SLATE"
        out["reason"] = (f"pinned season {out['season']} week {out['week']} is not in the schedule; "
                         "refusing to build a slate the calendar does not contain")
    return out


def emit_github_output(path: str, res: dict):
    keys = ("status", "reason", "season", "week", "season_type", "slate_id", "label",
            "first_kickoff_utc", "next_kickoff_utc", "minutes_to_first_kickoff",
            "minutes_to_next_kickoff", "games_scheduled", "games_upcoming")
    with open(path, "a") as f:
        for k in keys:
            v = res.get(k)
            f.write(f"{k}={'' if v is None else v}\n")
        wk = res.get("week")
        f.write("week_padded=" + ("" if wk is None else f"{wk:02d}") + "\n")


def main():
    ap = argparse.ArgumentParser(description="resolve the active NFL season/week")
    ap.add_argument("--market-data", default=None,
                    help="market-data worktree (supplies the cached schedule as a fallback source)")
    ap.add_argument("--schedule", default=None, help="explicit games.csv path")
    ap.add_argument("--allow-download", action="store_true",
                    help="fetch the nflverse schedule if no local copy exists")
    ap.add_argument("--now", default=None, help="ISO instant to resolve as of (testing)")
    ap.add_argument("--pin-season", default=None,
                    help="override the resolved season (blank = resolve)")
    ap.add_argument("--pin-week", default=None,
                    help="override the resolved week (blank = resolve)")
    ap.add_argument("--allow-no-slate", action="store_true",
                    help="exit 0 instead of 6 when there is no active slate")
    ap.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    ap.add_argument("--json-out", default=None, help="also write the full resolution here")
    a = ap.parse_args()

    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    try:
        games, src = load_schedule(ROOT, market_data=a.market_data, path=a.schedule,
                                   allow_download=a.allow_download)
    except Exception as e:  # noqa: BLE001 -- any failure to read the schedule is the same fail-closed case
        print(f"FAIL: {e}", file=sys.stderr)
        if a.github_output:
            emit_github_output(a.github_output, {"status": "NO_SCHEDULE", "reason": str(e)[:300]})
        return 7

    res = resolve_active_week(games, now, schedule_source=src)
    res = apply_pins(res, a.pin_season, a.pin_week, games)
    print(json.dumps(res, indent=1))
    if a.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.json_out)), exist_ok=True)
        with open(a.json_out, "w") as f:
            json.dump(res, f, indent=1)
    if a.github_output:
        emit_github_output(a.github_output, res)
    if res["status"] == "OK":
        return 0
    print(f"NO SLATE: {res['reason']}", file=sys.stderr)
    return 0 if a.allow_no_slate else 6


if __name__ == "__main__":
    sys.exit(main())
