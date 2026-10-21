#!/usr/bin/env python3
"""Duplicate guard for the scheduled FRESH run (the ~1 h walk-forward rebuild) so each fresh slot can have a backup cron.

GitHub drops and delays cron triggers. The refresh slots already have a backup 12 minutes later, because a refresh run is
idempotent and cheap. The fresh slots (Thu 13:11, Sat 13:11, Sun 08:11 UTC) are not: a dropped one leaves the near-kickoff refresh
runs with no valid saved state, and a second one that rebuilds again just burns an hour. So every scheduled fresh slot gets a
backup run, and every scheduled fresh run (primary or backup) first asks this guard whether a fresh run already COMPLETED:

  The archive commit `nfl projection foundation fresh <UTC minute>` is pushed by ci.sh only after every stage, archive_guard and
  the state save succeeded, so its presence on projection-data inside the window means the slot was done.

  skip=true   such a commit exists within --window-hours before --now: do not rebuild, do not write, do not commit anything
  skip=false  none exists (the primary was dropped, is delayed, or failed): run the whole fresh chain exactly as the primary would

The concurrency group (projection-foundation-nfl-live, cancel-in-progress false) already serialises runs, so a backup that is
queued behind a still-running primary only starts after it finished, then sees its commit and skips. This module only DECIDES:
it is read-only on the archive (never stages, writes or commits), never changes the run clock, so a backup can only produce
forecasts stamped with the time it actually ran (the archive rejects any generated/archived-after-start forecast), and it
touches no file in the walk-forward state fingerprint (nfl.live.state.STATE_CODE), so saved-state compatibility is unchanged.
It fails open: if the history cannot be read, the run proceeds (an extra hour of compute is cheaper than a missing state).

    python3 nfl/live/fresh_guard.py --archive <projection-data checkout> [--now ISO] [--window-hours 6] [--github-output FILE]

Standard library only (it runs before Python dependencies are installed).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

BRANCH = "projection-data"
SUBJECT = re.compile(r"^nfl projection foundation fresh \d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$")
DEPTH = 60                       # commits of history to consider (the archive gets a handful of commits a day)
CLOCK_SKEW = timedelta(minutes=10)


def _git(archive: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", archive, *args], capture_output=True, text=True)


def _ts(s: str) -> datetime:
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def decide(archive: str, now: datetime, window_hours: float = 6.0) -> dict:
    """{'skip': bool, 'reason': str, 'commit': str|None}. Read-only."""
    if _git(archive, "rev-parse", "--verify", "-q", "HEAD").returncode != 0:
        return {"skip": False, "reason": "projection-data has no commits yet", "commit": None}
    if _git(archive, "rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        _git(archive, "fetch", "--quiet", f"--depth={DEPTH}", "origin", BRANCH)      # best effort: the checkout is depth 1
    log = _git(archive, "log", f"-n{DEPTH}", "--format=%H%x09%cI%x09%s")
    if log.returncode != 0:
        return {"skip": False, "reason": f"history unreadable ({log.stderr.strip()[:200]}); running", "commit": None}
    lo, hi = now - timedelta(hours=window_hours), now + CLOCK_SKEW
    for line in log.stdout.splitlines():
        sha, _, rest = line.partition("\t")
        when, _, subject = rest.partition("\t")
        if not SUBJECT.match(subject):
            continue
        try:
            t = _ts(when)
        except ValueError:
            continue
        if lo <= t <= hi:
            return {"skip": True, "commit": sha[:12], "reason": f"a fresh run already completed at {t.strftime('%Y-%m-%dT%H:%MZ')} "
                    f"(commit {sha[:12]}, within the last {window_hours:g} h): nothing to rebuild"}
    return {"skip": False, "commit": None, "reason": f"no completed fresh run in the last {window_hours:g} h: running the fresh chain"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--archive", required=True)
    ap.add_argument("--now", default=None, help="ISO time (default: the current UTC time)")
    ap.add_argument("--window-hours", type=float, default=6.0)
    ap.add_argument("--github-output", default=None)
    a = ap.parse_args(argv)
    now = _ts(a.now) if a.now else datetime.now(timezone.utc)
    d = decide(a.archive, now, a.window_hours)
    print(("::notice::fresh-run guard: " if d["skip"] else "fresh-run guard: ") + d["reason"], flush=True)
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"skip={'true' if d['skip'] else 'false'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
