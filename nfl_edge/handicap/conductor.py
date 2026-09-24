"""HORIZON CONDUCTOR: start the horizon workflows when a horizon is owed, instead of hoping cron fires.

WHY THIS EXISTS
---------------
`run-nfl-horizons.yml` and `three-arm-horizons.yml` are scheduled `*/15`. Measured over their first 9.5 days,
GitHub actually started the RUN NFL gate on 97 of roughly 1,370 ticks -- about 7% -- with gaps between runs of
105 to 417 minutes (median 196). A T-90m or T-30m horizon has a 60-90 minute window before kickoff, so under
that scheduler it is served only by luck. Weeks 1 and 2 of 2026: 11 of 44 RUN NFL horizons missed, none on
time. The gate and the build were correct; they were simply not started.

`shadow-v2-horizon-conductor.yml` (PR #39) fixed this for the Shadow v2 freeze only, by keeping ONE small
runner looping a stdlib gate and dispatching the freeze workflow when it is due. This module is the same
idea for the two workflows it did not cover, with one addition that matters: the conductor is not itself a
single point of failure on the same broken scheduler.

THREE INDEPENDENT WAYS A CONDUCTOR STARTS
-----------------------------------------
1. It CHAINS. Shortly before its own job limit it dispatches its successor (`workflow_dispatch` through the
   job's own token, which GitHub honours for dispatch events). The successor waits as the one pending run of
   the concurrency group and starts the moment this one ends. Continuity does not depend on cron at all.
2. Its own hourly cron. If a chain link is lost -- a dispatch refused, a runner lost mid-job -- the next cron
   tick that GitHub does honour restarts the chain. The concurrency group collapses any surplus into one
   pending run, so a cron tick arriving while the chain is healthy costs nothing.
3. The horizon workflows keep their own `*/15` crons, and a manual dispatch still works. Nothing here
   replaces them; it adds starts, never removes them.

WHAT IT NEVER DOES
------------------
It builds nothing and marks nothing. It dispatches the SAME horizon workflow a cron would have started, and
that workflow's own gate re-derives what is due from the schedule and the capture state. So a dispatch that
turns out to be unnecessary is a gate run that says "nothing due" -- a few seconds -- and a duplicate can
never produce a second capture: horizon identity and the mark-after-success rule live in the workflow, and
both are unchanged.
"""
from __future__ import annotations

from datetime import datetime

#: Do not re-dispatch the same set of due horizons more often than this while no run is active. A RUN NFL
#: build takes ~17 minutes; a failed one (a stale Kalshi capture, a flaky download) leaves the horizon due and
#: should be retried promptly, but not in a tight loop against a failure that has not changed.
REDISPATCH_MIN = 20.0

#: How long before its own end a conductor dispatches its successor. Long enough that a slow dispatch call
#: still lands before the job limit; short enough that the successor is not pending for most of the run.
CHAIN_LEAD_MIN = 12.0


def decide(due_ids, dispatched: dict, now: datetime, active_runs: int,
           redispatch_min: float = REDISPATCH_MIN) -> tuple[bool, str]:
    """Pure: dispatch the horizon workflow now?

    `dispatched` maps frozenset(horizon ids) -> the instant this conductor last dispatched for exactly that set.
    An ACTIVE run (queued or in progress) is always allowed to serve what is due: stacking a second one behind
    it would only make GitHub cancel the older pending run.
    """
    due_ids = [d for d in (due_ids or []) if d]
    if not due_ids:
        return False, "nothing due"
    if active_runs > 0:
        return False, f"{active_runs} run(s) already queued or running: they will serve what is due"
    key = frozenset(due_ids)
    last = dispatched.get(key)
    if last is not None and (now - last).total_seconds() < redispatch_min * 60:
        return False, (f"dispatched {((now - last).total_seconds() / 60):.0f} min ago for the same horizons; "
                       f"retry after {redispatch_min:.0f} min if still due")
    return True, f"due: {sorted(due_ids)}"


def should_chain(now_epoch: float, end_epoch: float, already_chained: bool,
                 lead_min: float = CHAIN_LEAD_MIN) -> bool:
    """Pure: is it time to dispatch this conductor's successor? At most once per conductor run."""
    return (not already_chained) and (end_epoch - now_epoch) <= lead_min * 60
