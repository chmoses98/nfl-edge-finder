#!/usr/bin/env python3
"""APP PUBLICATION ALARM: is the canonical app board (handicap-reports:app/latest) still describing the present?

    python3 scripts/ops/app_publication_health.py --board /tmp/board.json --manifest /tmp/manifest.json \
        --allow-download [--feed-index /tmp/live_quotes_index.json] --summary "$GITHUB_STEP_SUMMARY"

Incident 2026-10-06/07: the board stopped at the week-4 MNF pregame build and kept ATL@NO "SCHEDULED" for a day;
nothing here noticed, the app and the live-quote feed did. Each rule below is deterministic and none assumes an NFL
game exists every day:

  DANGLING_EVENT      an event still SCHEDULED / IN_PROGRESS / LIVE more than LOOKBACK_H after its kickoff -- the
                      board stopped refreshing (the same rule as Sift's feed: sift-sports-intelligence
                      scripts/live-quotes/slate.mjs)
  ROLLOVER_OVERDUE    the published report is an earlier slate than the active one, more than ROLLOVER_GRACE_H
                      after the published slate's last game finished (horizons.rollover_due should have run)
  BOARD_TOO_OLD       a slate is active and board.generated_at is older than MAX_AGE_H (the longest normal gap
                      between publishes is MNF rollover -> next T-24h, ~45h)
  FEED_SOURCE_STALE   Sift's live-quote feed index declares STALE_PUBLICATION (optional input; unreadable = warning)

Off-season (no active slate) only DANGLING_EVENT can fire, and only for an event the board itself still calls live.
Exit 1 when any rule fires. Read-only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.data.nfl_calendar import (  # noqa: E402
    GAME_RUNTIME_HOURS, load_schedule, resolve_active_week, week_blocks,
)
from nfl_edge.handicap.horizons import rollover_due  # noqa: E402

LOOKBACK_H = 8.0
ROLLOVER_GRACE_H = 2.0
MAX_AGE_H = 72.0
LIVE = ("SCHEDULED", "IN_PROGRESS", "LIVE")


def _dt(x):
    try:
        return datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def evaluate(board: dict, manifest: dict, games: list, now: datetime, feed_index: dict | None = None) -> dict:
    """Pure: the alarm rules against one board / manifest / schedule / instant."""
    findings = []
    for it in (board or {}).get("items") or []:
        ko = _dt(it.get("start_time_utc"))
        if it.get("status") in LIVE and ko and now - ko > timedelta(hours=LOOKBACK_H):
            findings.append({"rule": "DANGLING_EVENT", "event_id": it.get("event_id"), "status": it.get("status"),
                             "start_time_utc": it.get("start_time_utc"),
                             "detail": f"{it.get('status')} {(now - ko).total_seconds() / 3600:.0f}h after kickoff"})
    week = resolve_active_week(games, now)
    roll = rollover_due(week, manifest)
    if roll:
        pub = next((b for b in week_blocks(games) if b["slate_id"] == (manifest or {}).get("slate_id")), None)
        done = pub["last_kickoff"] + timedelta(hours=GAME_RUNTIME_HOURS) if pub and pub["last_kickoff"] else None
        if done is None or now - done > timedelta(hours=ROLLOVER_GRACE_H):
            findings.append({"rule": "ROLLOVER_OVERDUE", "published_slate_id": roll["published_slate_id"],
                             "active_slate_id": roll["active_slate_id"],
                             "detail": f"published slate finished {done.isoformat() if done else 'unknown'}"})
    gen = _dt((board or {}).get("generated_at"))
    if week.get("status") == "OK" and (gen is None or now - gen > timedelta(hours=MAX_AGE_H)):
        findings.append({"rule": "BOARD_TOO_OLD", "generated_at": (board or {}).get("generated_at"),
                         "detail": f"older than {MAX_AGE_H:.0f}h while {week.get('slate_id')} is active"})
    if feed_index and feed_index.get("status") == "STALE_PUBLICATION":
        findings.append({"rule": "FEED_SOURCE_STALE", "feed_generated_at": feed_index.get("generated_at"),
                         "detail": "; ".join(r for p in feed_index.get("publications") or [] for r in p.get("reasons") or [])})
    return {"checked_at": now.isoformat(), "board_generated_at": (board or {}).get("generated_at"),
            "published_slate_id": (manifest or {}).get("slate_id"), "active_slate_id": week.get("slate_id"),
            "season_active": week.get("status") == "OK", "status": "STALE" if findings else "CURRENT",
            "findings": findings}


def _load(path):
    if not path:
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--feed-index", default=None)
    ap.add_argument("--schedule", default=None)
    ap.add_argument("--allow-download", action="store_true")
    ap.add_argument("--now", default=None)
    ap.add_argument("--summary", default=None)
    a = ap.parse_args(argv)
    now = _dt(a.now) if a.now else datetime.now(timezone.utc)
    games, _ = load_schedule(ROOT, path=a.schedule, allow_download=a.allow_download, download_attempts=3)
    if a.feed_index and _load(a.feed_index) is None:
        print("::warning::the live-quote feed index could not be read; FEED_SOURCE_STALE not evaluated")
    out = evaluate(_load(a.board) or {}, _load(a.manifest) or {}, games, now, _load(a.feed_index))
    print(json.dumps(out, indent=1))
    lines = ["## App publication health", "",
             f"* board generated `{out['board_generated_at']}` · published `{out['published_slate_id']}` · "
             f"active `{out['active_slate_id']}` · **{out['status']}**"]
    lines += [f"* **{f['rule']}** {f.get('event_id') or ''} {f['detail']}" for f in out["findings"]]
    if a.summary:
        with open(a.summary, "a") as f:
            f.write("\n".join(lines) + "\n")
    for f in out["findings"]:
        print(f"::error title=App publication {f['rule']}::{f['detail']}")
    return 1 if out["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
