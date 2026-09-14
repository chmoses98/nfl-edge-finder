#!/usr/bin/env python3
"""The cheap gate: may this scheduled wake spend an Airtable request? Reads a CSV, needs no secret.

    python3 scripts/handicap/preflight_window_gate.py --market-data ../fees --github-output "$GITHUB_OUTPUT"

Exit codes are the contract:

    0  a decision was reached -- ACTIVE or OUTSIDE_PREFLIGHT_WINDOW, both of them successes
    2  the schedule could not be read: SCHEDULE_ERROR

An unreadable calendar is NOT "no window". Unknown state is not permission, so this exits non-zero and the
workflow fails visibly rather than logging a quiet INACTIVE that would look identical to a healthy Tuesday.

Nothing here touches Airtable, Kalshi, the ledger or the evidence branch, and it is stdlib-only so it cannot
fail on a package resolution. It prints no candidate, player, ticker, price, probability, stake or thesis --
it has none of those and needs none of them to answer a question about the clock.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from nfl_edge.data import nfl_calendar as CAL          # noqa: E402
from nfl_edge.handicap import preflight_window as PW   # noqa: E402


def log(msg: str) -> None:
    print(msg, flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schedule", default=None, help="explicit games.csv; otherwise the canonical search")
    ap.add_argument("--market-data", default=None,
                    help="checkout holding data/kalshi/capture/schedule_cache.csv")
    ap.add_argument("--allow-download", action="store_true",
                    help="fetch the nflverse schedule if no local copy is present")
    ap.add_argument("--now", default=None, help="ISO-8601 instant, for deterministic tests")
    ap.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT") or None)
    ap.add_argument("--json", action="store_true", help="emit the full result as JSON as well")
    a = ap.parse_args(argv)

    now = (datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc))
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    try:
        games, source = CAL.load_schedule(ROOT, market_data=a.market_data, path=a.schedule,
                                          allow_download=a.allow_download)
    except (FileNotFoundError, OSError, ValueError) as e:
        # FAIL CLOSED AND LOUD. Reporting INACTIVE here would be indistinguishable from a quiet Tuesday and
        # would hide a broken checkout for as long as nobody noticed the rows going unanswered.
        log(f"status={PW.STATUS_ERROR}")
        log("active=false")
        log(f"reason=the NFL schedule could not be read: {e}")
        log("airtable_calls=0")
        _write_output(a.github_output, {"active": "false", "status": PW.STATUS_ERROR})
        return 2

    result = PW.evaluate(games, now)
    result["schedule_source"] = os.path.basename(str(source))
    result["reason"] = ("a kickoff cluster is inside its polling window"
                        if result["active"] else "no kickoff cluster is inside its polling window")

    log(f"status={result['status']}")
    log(f"active={'true' if result['active'] else 'false'}")
    log(f"reason={result['reason']}")
    for key in ("game_day", "primary_cluster_utc", "active_window_start_utc", "active_window_end_utc",
                "active_cluster_count", "next_window_start_utc"):
        if result.get(key) is not None:
            log(f"{key}={result[key]}")
    if not result["active"]:
        log("airtable_calls=0")
        log("result=NO_WORK_WINDOW")
    if a.json:
        log(json.dumps(result, sort_keys=True, default=str))

    _write_output(a.github_output, {"active": "true" if result["active"] else "false",
                                    "status": result["status"]})
    return 0


def _write_output(path, values: dict) -> None:
    if not path:
        return
    with open(path, "a") as f:
        for k, v in values.items():
            f.write(f"{k}={v}\n")


if __name__ == "__main__":
    raise SystemExit(main())
