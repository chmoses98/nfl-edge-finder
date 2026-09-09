#!/usr/bin/env python3
"""Decide, cheaply, whether the postgame settlement job has anything to do.

A scheduled poll that downloads play-by-play and re-reads the whole ledger to discover there is no finished
game is a job that burns Actions minutes to learn nothing. This gate reads only the schedule (one 2 MB csv) and
the directory listing of the published evaluation corpus, and answers in seconds.

A game is WORK when

  * it has a published final score, and
  * its kickoff is inside the lookback window (default 10 days), and
  * the published corpus has no evaluation batch for it under the current evaluation version.

The lookback window is what stops a game that never had a prediction -- or a family we deliberately refuse --
from being retried for the rest of the season. A game older than the window is reported once as
`unevaluated_outside_window` so it is visible rather than forgotten.

Games that kicked off BEFORE the shadow ledger's first snapshot are ignored entirely rather than reported as
unevaluated: there is no pregame prediction for them and never will be, so listing 6,732 historical games as
"work not done" would bury the one game that actually matters. The ledger's earliest capture day is read from
the published corpus, so the boundary is a fact about the data, not a hard-coded date.

`--github-output` writes `work`, `games`, `n_games` for the workflow to branch on. Exit status is always 0
unless the gate itself could not read the schedule: "nothing to do" is not a failure.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.settlement.results import (                                          # noqa: E402
    FINAL, games_from_schedule_text, load_schedule_text,
)
from nfl_edge.shadow.evaluation import EVALUATION_VERSION                           # noqa: E402


def ledger_start(market_data: str) -> str | None:
    """The earliest day the shadow ledger has a snapshot for, as YYYY-MM-DD, or None if there is no ledger."""
    days = sorted(os.path.basename(d) for d in glob.glob(os.path.join(
        market_data, "data", "shadow", "ledger", "*")) if os.path.isdir(d))
    return days[0] if days else None


def evaluated_games(corpus_root: str, evaluation_version: str | None) -> set:
    """Games that already have at least one published batch for this evaluation version."""
    out = set()
    for d in sorted(glob.glob(os.path.join(corpus_root, "*"))):
        if not os.path.isdir(d):
            continue
        pattern = f"{evaluation_version}.*.evaluations.jsonl.gz" if evaluation_version else "*.evaluations.jsonl.gz"
        if glob.glob(os.path.join(d, pattern)):
            out.add(os.path.basename(d))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--schedule", default="", help="path to nflverse games.csv (default: repo bronze copy)")
    ap.add_argument("--allow-download", action="store_true",
                    help="fetch the schedule over https when no local copy exists")
    ap.add_argument("--eval-version", default=EVALUATION_VERSION)
    ap.add_argument("--lookback-days", type=float, default=10.0)
    ap.add_argument("--min-hours-after-kickoff", type=float, default=4.0)
    ap.add_argument("--github-output", default="")
    ap.add_argument("--since", default="", help="ignore games kicking off before this YYYY-MM-DD "
                                                "(default: the shadow ledger's first capture day)")
    ap.add_argument("--now", default="", help="ISO timestamp to evaluate against (testing)")
    a = ap.parse_args()
    now = datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc)

    # raises when no schedule can be read at all, which is the right failure: a gate that cannot see the
    # schedule must never report "nothing to do".
    text, source = load_schedule_text(ROOT, market_data=a.market_data, path=a.schedule or None,
                                      allow_download=a.allow_download)
    games = games_from_schedule_text(text, source=source)

    corpus_root = os.path.join(a.market_data, "data", "shadow", "evaluations")
    done = evaluated_games(corpus_root, a.eval_version)
    start = a.since or ledger_start(a.market_data)
    work, outside, waiting, before_ledger = [], [], [], 0
    for g in games:
        if g.status != FINAL or not g.kickoff_utc:
            continue
        if start and g.kickoff_utc[:10] < start:
            before_ledger += 1
            continue
        ko = datetime.fromisoformat(g.kickoff_utc)
        if ko > now:
            continue
        if g.game_id in done:
            continue
        if now < ko + timedelta(hours=a.min_hours_after_kickoff):
            waiting.append(g.game_id)
        elif ko >= now - timedelta(days=a.lookback_days):
            work.append(g.game_id)
        else:
            outside.append(g.game_id)

    work.sort()
    report = {"now": now.isoformat(), "schedule_source": source, "evaluation_version": a.eval_version,
              "games_final_unevaluated_in_window": work,
              "games_final_too_recent_to_be_sure": sorted(waiting),
              "unevaluated_outside_window": sorted(outside)[-20:],
              "n_unevaluated_outside_window": len(outside),
              "ledger_starts": start, "games_before_the_ledger_ignored": before_ledger,
              "already_evaluated_games": len(done)}
    print(json.dumps(report, indent=1))
    if outside:
        print(f"::notice::{len(outside)} final game(s) older than {a.lookback_days} days have no evaluation "
              f"batch; the newest are {sorted(outside)[-5:]}. Settle them explicitly with --game if that is wrong.")
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"work={'true' if work else 'false'}\n")
            f.write(f"n_games={len(work)}\n")
            f.write("games=" + " ".join(work) + "\n")
            f.write("game_args=" + " ".join(f"--game {g}" for g in work) + "\n")
    print(f"work={'true' if work else 'false'} ({len(work)} game(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
