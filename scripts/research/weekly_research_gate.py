#!/usr/bin/env python3
"""Is there a completed NFL week whose weekly research reports are not yet published? Stdlib only, seconds.

A week is COMPLETE when every game of it is FINAL in the nflverse schedule and the last kickoff is at least
`--settle-hours` old (the postgame job settles and autopsies in the hours after a game). The reports for week N
are missing when `data/research/weekly/<season>/week_NN/BOARD_EDGE_DISCOVERY.md` is absent from market-data.

Writes `work`, `weeks` (1..N, comma-separated: the cumulative scope) and `target` (N) for the workflow.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.settlement.results import FINAL, games_from_schedule_text, load_schedule_text   # noqa: E402


def completed_weeks(games, season: int, now: datetime, settle_hours: float) -> list:
    by = {}
    for g in games:
        if g.season == season and g.week is not None and g.kickoff_utc:
            by.setdefault(int(g.week), []).append(g)
    out = []
    for w in sorted(by):
        gs = by[w]
        last = max(datetime.fromisoformat(g.kickoff_utc) for g in gs)
        if all(g.status == FINAL for g in gs) and now >= last + timedelta(hours=settle_hours):
            out.append(w)
        else:
            break
    return out


def published(ref: str, season: int, week: int, repo: str) -> bool:
    path = f"data/research/weekly/{season}/week_{week:02d}/BOARD_EDGE_DISCOVERY.md"
    r = subprocess.run(["git", "cat-file", "-e", f"{ref}:{path}"], cwd=repo, capture_output=True)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--md-ref", default="origin/market-data")
    ap.add_argument("--settle-hours", type=float, default=30.0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--now", default="")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args()
    now = datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc)
    text, src = load_schedule_text(ROOT, allow_download=True)
    weeks = completed_weeks(games_from_schedule_text(text, seasons=[a.season]), a.season, now, a.settle_hours)
    target = weeks[-1] if weeks else None
    work = bool(target) and (a.force or not published(a.md_ref, a.season, target, ROOT))
    print(f"schedule {src}; complete weeks {weeks}; target {target}; work {work}")
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"work={'true' if work else 'false'}\nweeks={','.join(str(w) for w in weeks)}\ntarget={target or ''}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
