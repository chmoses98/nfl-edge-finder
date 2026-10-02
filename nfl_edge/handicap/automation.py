"""AUTONOMOUS POSTGAME + CHAIN HEALTH: the pure decisions behind "nobody should have to press Run".

Thursday 2026-09-24/25 (ATL@GB, kickoff 00:15Z, final ~03:30Z): the postgame work happened only because the owner
dispatched it -- postgame-settle at 05:01Z (the 3-hourly cron's next delivery was 05:05Z; the one before, 21:35Z),
and in kalshi-bet-router settle-wagers at 05:03Z/05:21Z and deliver-wagers at 05:11Z. The workflows are correct and
idempotent; they were not started. The horizon conductor already keeps a runner alive for the pregame horizons;
these functions let it also start the postgame workflows at fixed offsets after each kickoff cluster, retry a
transient failure a bounded number of times, and let workflow-health raise an alarm when a conductor chain dies.

STATES, as reported by the postgame run itself (classify_postgame):

    WAITING_FOR_SOURCE  games are final but a source (nflverse stats/snaps, the exchange's terminal settlement)
                        is not there yet; every candidate was deferred -- the next tick retries
    RUNNING             a run is queued or in progress (reported by the conductor, never by a finished run)
    PARTIAL_COMPLETE    something was written and something is still deferred
    COMPLETE            everything owed is written, or nothing was owed
    BLOCKED             a rerun CONTRADICTED a published record (CONFLICT) or the run failed. CONFLICT stays red
                        until a person resolves it; nothing is overwritten

Everything here is stdlib-only and pure: callers inject `now`, run lists and the schedule.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from nfl_edge.handicap.horizons import cluster_kickoffs

#: Offsets after a cluster's LAST kickoff at which the postgame workflows are started. A game is final ~3h15m
#: after kickoff; nflverse statistics and the exchange's terminal settlement follow at their own pace, and every
#: dispatched workflow has its own gate that defers what is not ready -- so later ticks are the retries.
POSTGAME_OFFSETS_MIN = (240, 360, 540, 780)
#: A tick is owed from its instant for this long; after that the next tick (or the workflow's own cron) owns it.
POSTGAME_WINDOW_MIN = 120.0
#: Look this far back for kickoffs whose postgame ticks may still be open.
POSTGAME_LOOKBACK_MIN = max(POSTGAME_OFFSETS_MIN) + POSTGAME_WINDOW_MIN
#: A failed dispatched run is retried at most this many times per tick set, this far apart.
POSTGAME_MAX_ATTEMPTS = 3
POSTGAME_RETRY_MIN = 20.0

POSTGAME_WORKFLOWS = ("postgame-settle.yml", "actual-wagers.yml", "shadow-v2-settle.yml")

STATES = ("WAITING_FOR_SOURCE", "RUNNING", "PARTIAL_COMPLETE", "COMPLETE", "BLOCKED")


def _dt(x):
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    if not x:
        return None
    try:
        d = datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def postgame_ticks(games: list, now: datetime, *, offsets_min=POSTGAME_OFFSETS_MIN,
                   window_min: float = POSTGAME_WINDOW_MIN) -> list:
    """Postgame ticks that are owed at `now`: [{tick_id, cluster_key, tick_utc, last_kickoff_utc, games}].

    Clusters are formed over games that kicked off within the lookback, independently of which week the calendar
    now calls active -- the Monday night game's ticks run into Tuesday, after the calendar has moved on."""
    lookback = timedelta(minutes=max(offsets_min) + window_min)
    recent = [g for g in games if _dt(g.get("kickoff_utc")) and now - lookback <= _dt(g["kickoff_utc"]) <= now]
    due = []
    for c in cluster_kickoffs(recent):
        last = _dt(c["latest_kickoff_utc"])
        for off in offsets_min:
            t = last + timedelta(minutes=off)
            if t <= now < t + timedelta(minutes=window_min):
                due.append({"tick_id": f"POST|{c['cluster_key']}|+{int(off)}m", "cluster_key": c["cluster_key"],
                            "tick_utc": t.isoformat(), "last_kickoff_utc": last.isoformat(),
                            "games": list(c["game_ids"])})
    return due


def decide_postgame(due_ticks: list, attempts: dict, now: datetime, active_runs: int, last_conclusion: str | None,
                    *, max_attempts: int = POSTGAME_MAX_ATTEMPTS, retry_min: float = POSTGAME_RETRY_MIN):
    """Pure: dispatch this postgame workflow now?

    `attempts` maps frozenset(tick ids) -> {"n": dispatches so far, "last": instant}. One dispatch serves every due
    tick at once (the workflow's gate settles every ready game). A new tick set is dispatched immediately; the same
    set again only if the last run FAILED, after `retry_min`, at most `max_attempts` times in all. An active run is
    never stacked. A successful run is never repeated for the same ticks."""
    ids = sorted(t["tick_id"] for t in (due_ticks or []))
    if not ids:
        return False, "no postgame tick owed"
    if active_runs > 0:
        return False, f"{active_runs} run(s) already queued or running: they serve the tick"
    key = frozenset(ids)
    rec = attempts.get(key)
    if rec is None:
        return True, f"postgame tick(s) owed: {ids}"
    if (last_conclusion or "").lower() != "failure":
        return False, f"already dispatched for {ids}; last run {last_conclusion or 'unknown'}"
    if rec["n"] >= max_attempts:
        return False, f"{rec['n']} attempts for {ids} failed; left red for a person and the next tick"
    if (now - rec["last"]).total_seconds() < retry_min * 60:
        return False, f"last attempt failed {((now - rec['last']).total_seconds() / 60):.0f} min ago; retry after {retry_min:.0f}"
    return True, f"retry {rec['n'] + 1}/{max_attempts} after a failed run for {ids}"


def record_dispatch(attempts: dict, due_ticks: list, now: datetime) -> None:
    key = frozenset(t["tick_id"] for t in due_ticks)
    rec = attempts.get(key) or {"n": 0, "last": now}
    attempts[key] = {"n": rec["n"] + 1, "last": now}


def classify_postgame(*, gate_work: str | None, settle_status: str | None, written, deferred,
                      arms_status: str | None = None, autopsy_status: str | None = None,
                      job_status: str | None = None, named_games: bool = False) -> dict:
    """The state of ONE finished postgame-settle run, from its step outputs. Unknown numbers read as 0."""
    def n(x):
        try:
            return int(x or 0)
        except (TypeError, ValueError):
            return 0
    w, d = n(written), n(deferred)
    statuses = {str(s or "").upper() for s in (settle_status, arms_status, autopsy_status)}
    if "CONFLICT" in statuses:
        return {"state": "BLOCKED", "reason": "a rerun contradicted a published record (CONFLICT); nothing was "
                                              "overwritten -- a person must resolve it"}
    if str(job_status or "").lower() == "failure":
        return {"state": "BLOCKED", "reason": "the run failed before finishing; the horizon conductor retries it "
                                              f"(up to {POSTGAME_MAX_ATTEMPTS} attempts per tick) and the next tick "
                                              "follows"}
    wrote_any = w > 0 or "WROTE" in statuses
    if str(gate_work or "").lower() != "true" and not named_games and not wrote_any:
        return {"state": "COMPLETE", "reason": "no final game is missing an evaluation batch"}
    if d > 0 and wrote_any:
        return {"state": "PARTIAL_COMPLETE", "reason": f"{w} record(s) written; {d} game(s) still waiting on a source"}
    if d > 0:
        return {"state": "WAITING_FOR_SOURCE", "reason": f"{d} game(s) deferred (pending statistics, snaps or a "
                                                         "terminal exchange settlement); the next tick retries"}
    return {"state": "COMPLETE", "reason": (f"{w} record(s) written" if wrote_any
                                            else "every candidate game was already evaluated")}


#: Operational health of one finished run (the reliability contract's states). NOT_APPLICABLE = nothing was owed.
HEALTH_STATES = ("HEALTHY", "DEGRADED", "FAILED", "NOT_APPLICABLE")


def classify_shadow_v2_settle(*, settle_status: str | None, closes_status: str | None, index_written=None,
                              evidence_publish: str | None = None, research: str | None = None,
                              research_publish: str | None = None, job_status: str | None = None) -> dict:
    """The health of ONE finished shadow-v2-settle run, from its step outputs and step outcomes.

    The run's primary product is the write-once EVIDENCE (settlement, close and CLV batches), published first. The
    research export / scorecard v3 / weekly report after it is DERIVED and rebuildable from the corpus every run.

        FAILED          an evidence step failed (the job itself is red; this only names it)
        DEGRADED        the evidence is settled and published (or nothing was owed), but the derived rebuild failed
                        or ran past its step limit -- the previous published report stands, the next run rebuilds
        HEALTHY         evidence written and published, derived rebuild published
        NOT_APPLICABLE  no game was ready and nothing new to pair; the derived rebuild still ran cleanly

    Between 2026-09-27 and 2026-10-01 the derived rebuild ran into the 90-minute JOB limit on ~28 consecutive runs
    (e.g. 36937919712: evidence published 23:30Z, research step killed 00:26Z), so every run ended TIMED_OUT
    although its settlement evidence was already on market-data. The step now has its own limit and reports here.
    """
    def n(x):
        try:
            return int(x or 0)
        except (TypeError, ValueError):
            return 0
    oc = {k: str(v or "").lower() for k, v in (("evidence_publish", evidence_publish), ("research", research),
                                               ("research_publish", research_publish), ("job", job_status))}
    wrote = (str(settle_status or "").upper() == "WROTE" or str(closes_status or "").upper() == "WROTE"
             or n(index_written) > 0)
    if oc["evidence_publish"] == "failure" or (oc["job"] == "failure" and oc["research_publish"] != "failure"):
        return {"health": "FAILED", "reason": "a settlement/close/CLV evidence step failed; nothing derived can "
                                              "stand in for it -- see the failed step"}
    if oc["research_publish"] == "failure":
        return {"health": "FAILED", "reason": "the derived research export was rebuilt but could not be published"}
    if oc["research"] not in ("success", ""):
        return {"health": "DEGRADED",
                "reason": ("settlement evidence " + ("published" if wrote else "unchanged (nothing new owed)") +
                           f"; the derived research export / scorecard v3 / weekly report did not finish "
                           f"({oc['research']}, including running past its step limit) -- the previous published "
                           "report stands and the next run rebuilds it")}
    if wrote:
        return {"health": "HEALTHY", "reason": "settlement evidence and the derived research export published"}
    return {"health": "NOT_APPLICABLE", "reason": "no game newly ready to settle or pair; derived rebuild clean"}


#: A conductor chain with no queued/running link whose last activity is older than this is dead. A healthy
#: hand-off shows the successor as pending/queued, so the only legitimate gap is seconds.
CHAIN_DEAD_AFTER_MIN = 15.0
_ACTIVE = ("queued", "in_progress", "waiting", "pending", "requested")


def chain_health(runs: list, now: datetime, *, dead_after_min: float = CHAIN_DEAD_AFTER_MIN) -> dict:
    """ALIVE / DEAD / ABSENT for one self-chaining conductor, from its recent runs (`gh run list --json` shape)."""
    if runs is None:
        return {"status": "ABSENT", "reason": "the workflow could not be listed (not deployed here yet?)"}
    active = [r for r in runs if (r.get("status") or "") in _ACTIVE]
    if active:
        return {"status": "ALIVE", "reason": f"{len(active)} link(s) queued or running"}
    last = max((_dt(r.get("updatedAt") or r.get("createdAt")) for r in runs
                if _dt(r.get("updatedAt") or r.get("createdAt"))), default=None)
    if last is None:
        return {"status": "DEAD", "reason": "no run on record"}
    idle = (now - last).total_seconds() / 60.0
    if idle <= dead_after_min:
        return {"status": "ALIVE", "reason": f"between links ({idle:.0f} min since the last one ended)"}
    return {"status": "DEAD", "reason": f"no link queued or running for {idle:.0f} min"}
