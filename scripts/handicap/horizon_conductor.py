#!/usr/bin/env python3
"""HORIZON CONDUCTOR for RUN NFL and the three-arm game-centre freeze. See nfl_edge/handicap/conductor.py.

    python3 scripts/handicap/horizon_conductor.py --minutes 340 --interval 240 --chain-workflow horizon-conductor.yml

Every pass, for each target:

  * RUN_NFL   -- capture state is `handicap-reports:state/horizons.json`; dispatches `run-nfl-horizons.yml`.
  * THREE_ARM -- capture state is the marker file names under `market-data:data/shadow/arms/horizons/`;
                 dispatches `three-arm-horizons.yml`.
  * SIGNAL_LAB -- Football Signal Discovery Lab Wave 2 (RESEARCH_ONLY). State is the record names under
                 `market-data:data/research/signal_lab_wave2/`; an observe / enter / settle stage owed by
                 `nfl_edge.signal_discovery.wave2_due` dispatches `signal-lab-wave2.yml`, whose own gate decides.
  * A1B       -- Wave-2 A1B verified-pregame-inactives research (RESEARCH_ONLY, addendum B): source snapshots
                 (T-150 .. kickoff, every 10 min) and the A1B capture (T-80 .. T-35) per `nfl_edge.sim.a1b.due`;
                 dispatches `a1b-research.yml`, whose own gate decides.
  * WAVE2     -- GAME SCRIPT V2 Wave-2 research capture (RESEARCH_ONLY). Capture state is the record names under
                 `market-data:data/research/wave2/`; a (game, EARLY | LATE) window is owed while it is open and
                 has no record (`nfl_edge.sim.wave2_due`); dispatches `wave2-research.yml`, whose own gate decides.

it asks the SAME due rule the workflow's own gate uses (`nfl_edge.handicap.horizons.due_horizons`) and, when a
horizon is owed and no run of that workflow is already queued or running, dispatches one. Near the end of its
job it dispatches its own successor (`--chain-workflow`) so the next conductor does not depend on cron.

Every decision is one JSON line in the log: that line is the audit trail for "was a due horizon recognised,
and was a build started for it".
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.arms.horizons import captured_state                                   # noqa: E402
from nfl_edge.data.nfl_calendar import load_schedule, resolve_active_week           # noqa: E402
from nfl_edge.handicap.automation import (                                            # noqa: E402
    POSTGAME_WORKFLOWS, decide_postgame, postgame_ticks, record_dispatch,
)
from nfl_edge.handicap.conductor import decide, handover_end, should_chain           # noqa: E402
from nfl_edge.handicap.horizons import HORIZONS_MIN, cluster_kickoffs, due_horizons, rollover_due  # noqa: E402
from nfl_edge.signal_discovery import wave2_due as signal_lab_due                    # noqa: E402
from nfl_edge.sim import a1b as a1b_due                                               # noqa: E402
from nfl_edge.sim import wave2_due                                                    # noqa: E402

TARGETS = {
    "RUN_NFL": {"workflow": "run-nfl-horizons.yml"},
    "THREE_ARM": {"workflow": "three-arm-horizons.yml"},
    "WAVE2": {"workflow": "wave2-research.yml"},
    "SIGNAL_LAB": {"workflow": "signal-lab-wave2.yml"},
    "A1B": {"workflow": "a1b-research.yml"},
}


def _git(*args, timeout=180):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=timeout)


def run_nfl_state() -> dict:
    """The RUN NFL capture state, as the gate reads it. Unreadable -> {} (everything uncaptured is due, and the
    workflow's own gate, reading the same file, is what finally decides)."""
    _git("fetch", "--depth=1", "origin", "handicap-reports")
    r = _git("show", "origin/handicap-reports:state/horizons.json", timeout=60)
    try:
        return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}
    except ValueError:
        return {}


def run_nfl_published() -> dict:
    """The published `latest/manifest.json` on handicap-reports (one small API read, not a branch fetch).
    Unreadable -> {} (a rollover is then owed and run-nfl-horizons' own gate, reading the branch, decides)."""
    repo = os.environ.get("GITHUB_REPOSITORY", "chmoses98/nfl-edge-finder")
    r = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github.raw",
                        f"repos/{repo}/contents/latest/manifest.json?ref=handicap-reports"],
                       cwd=ROOT, capture_output=True, text=True, timeout=60)
    try:
        return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}
    except ValueError:
        return {}


def three_arm_state() -> dict:
    _git("fetch", "--depth=1", "--filter=blob:none", "origin", "market-data")
    r = _git("ls-tree", "--name-only", "origin/market-data", "data/shadow/arms/horizons/", timeout=60)
    return captured_state([os.path.basename(x) for x in r.stdout.split() if x.strip()])


def wave2_state() -> set:
    """{(game_id, window)} already recorded on market-data (names only; no record is opened)."""
    _git("fetch", "--depth=1", "--filter=blob:none", "origin", "market-data")
    r = _git("ls-tree", "-r", "--name-only", "origin/market-data", wave2_due.RECORD_PREFIX, timeout=60)
    return wave2_due.seen_from_names(r.stdout.split())


def signal_lab_state() -> set:
    """{(KIND, game_id)} already recorded on market-data (names only; no record is opened)."""
    _git("fetch", "--depth=1", "--filter=blob:none", "origin", "market-data")
    r = _git("ls-tree", "-r", "--name-only", "origin/market-data", signal_lab_due.RECORD_PREFIX, timeout=60)
    return signal_lab_due.seen_from_names(r.stdout.split())


def a1b_state() -> list:
    """A1B source-snapshot and record names on market-data (names only; nothing is opened)."""
    _git("fetch", "--depth=1", "--filter=blob:none", "origin", "market-data")
    r = _git("ls-tree", "-r", "--name-only", "origin/market-data", "data/research/wave2_a1b/", timeout=60)
    return r.stdout.split()


STATE_READERS = {"RUN_NFL": run_nfl_state, "THREE_ARM": three_arm_state, "WAVE2": wave2_state,
                 "SIGNAL_LAB": signal_lab_state, "A1B": a1b_state}


def active_runs(workflow: str) -> int:
    n = 0
    for status in ("queued", "in_progress", "waiting", "pending", "requested"):
        r = subprocess.run(["gh", "run", "list", "--workflow", workflow, "--status", status, "--json", "databaseId"],
                           cwd=ROOT, capture_output=True, text=True, timeout=60)
        try:
            n += len(json.loads(r.stdout or "[]"))
        except ValueError:
            pass
    return n


def dispatch(workflow: str, ref: str) -> tuple[bool, str]:
    r = subprocess.run(["gh", "workflow", "run", workflow, "--ref", ref], cwd=ROOT, capture_output=True, text=True,
                       timeout=60)
    return r.returncode == 0, (r.stderr or r.stdout).strip()[:300]


def one_pass(targets, games, src, now, dispatched, *, dry_run=False, ref="main",
             state_readers=None, active=None, dispatcher=None, published_reader=None) -> list:
    """Evaluate every target once. Returns one log line per target. Injection points exist for tests."""
    state_readers = state_readers or STATE_READERS
    active = active or active_runs
    dispatcher = dispatcher or dispatch
    lines = []
    week = resolve_active_week(games, now, schedule_source=src)
    for name in targets:
        wf = TARGETS[name]["workflow"]
        line = {"at": now.isoformat(), "target": name, "workflow": wf}
        if name == "SIGNAL_LAB":
            # Not tied to the active-week resolver. CHEAP FIRST: with nothing recorded, is anything owed at all?
            # Only then is market-data listed (a stage already recorded is not owed again).
            maybe = signal_lab_due.owed_ids(signal_lab_due.due(games, now, set()))
            due_ids = signal_lab_due.owed_ids(signal_lab_due.due(games, now, state_readers[name]())) if maybe else []
            n_active = active(wf) if due_ids and not dry_run else 0
            go, why = decide(due_ids, dispatched.setdefault(name, {}), now, n_active)
            line.update(decision=("dispatch" if go else "wait"), reason=why, due=due_ids)
            if go:
                ok, msg = (True, "dry run") if dry_run else dispatcher(wf, ref)
                line.update(dispatched=ok, message=msg)
                if ok:
                    dispatched[name][frozenset(due_ids)] = now
            lines.append(line)
            continue
        if name == "A1B":
            # A1B (addendum B): a source snapshot every 10 minutes from T-150 to kickoff, and the A1B capture in
            # (T-80, T-35]. CHEAP FIRST: nothing in either window -> market-data is not listed. Snapshot ids carry a
            # 10-minute bucket so the same game is re-dispatched each bucket, never faster.
            maybe = a1b_due.due(games, now, [])
            if maybe["snapshot"] or maybe["capture"]:
                d = a1b_due.due(games, now, state_readers[name]())
                bucket = int(now.timestamp() // (a1b_due.SNAPSHOT_MIN_GAP_MIN * 60))
                due_ids = [f"SNAP:{g}:{bucket}" for g in d["snapshot"]] + [f"A1B:{g}" for g in d["capture"]]
            else:
                due_ids = []
            n_active = active(wf) if due_ids and not dry_run else 0
            go, why = decide(due_ids, dispatched.setdefault(name, {}), now, n_active)
            line.update(decision=("dispatch" if go else "wait"), reason=why, due=due_ids)
            if go:
                ok, msg = (True, "dry run") if dry_run else dispatcher(wf, ref)
                line.update(dispatched=ok, message=msg)
                if ok:
                    dispatched[name][frozenset(due_ids)] = now
            lines.append(line)
            continue
        if name == "WAVE2":
            # Not tied to the active-week resolver: any post-cutoff game whose EARLY / LATE window is open is owed.
            # CHEAP FIRST: no window open for any game -> nothing can be owed, so market-data is not even listed.
            open_ids = wave2_due.due(games, now, set())
            due_ids = wave2_due.due(games, now, state_readers[name]()) if open_ids else []
            n_active = active(wf) if due_ids and not dry_run else 0
            go, why = decide(due_ids, dispatched.setdefault(name, {}), now, n_active)
            line.update(decision=("dispatch" if go else "wait"), reason=why, due=due_ids, open=open_ids)
            if go:
                ok, msg = (True, "dry run") if dry_run else dispatcher(wf, ref)
                line.update(dispatched=ok, message=msg)
                if ok:
                    dispatched[name][frozenset(due_ids)] = now
            lines.append(line)
            continue
        if week["status"] != "OK":
            line.update(decision="idle", reason=week.get("reason"))
            lines.append(line)
            continue
        # CHEAP FIRST: with nothing captured, is anything even in its window? If not, no capture state can make
        # something due, so the git fetches that read the state are skipped -- most passes of the week.
        if not due_horizons(week["slate_id"], week["games"], now, {}, horizons_min=HORIZONS_MIN).get("due"):
            d = due_horizons(week["slate_id"], week["games"], now, {}, horizons_min=HORIZONS_MIN)
        else:
            d = due_horizons(week["slate_id"], week["games"], now, state_readers[name](), horizons_min=HORIZONS_MIN)
        due_ids = [r["horizon_id"] for r in (d.get("due") or [])]
        # RUN NFL only: a published report of an earlier slate is a build owed now (horizons.rollover_due).
        roll = (rollover_due(week, published_reader())
                if name == "RUN_NFL" and not due_ids and published_reader is not None else None)
        if roll:
            due_ids = [roll["rollover_id"]]
            line.update(rollover=roll)
        n_active = active(wf) if due_ids and not dry_run else 0
        go, why = decide(due_ids, dispatched.setdefault(name, {}), now, n_active)
        line.update(decision=("dispatch" if go else "wait"), reason=why, due=due_ids,
                    due_lateness_min=[r["late_by_min"] for r in (d.get("due") or [])],
                    missed=[r["horizon_id"] for r in (d.get("missed") or [])],
                    next_pending=(d.get("next_pending") or {}).get("horizon_id"))
        if go:
            ok, msg = (True, "dry run") if dry_run else dispatcher(wf, ref)
            line.update(dispatched=ok, message=msg)
            if ok:
                dispatched[name][frozenset(due_ids)] = now
        lines.append(line)
    return lines


def last_conclusion(workflow: str):
    r = subprocess.run(["gh", "run", "list", "--workflow", workflow, "--limit", "1", "--json", "status,conclusion"],
                       cwd=ROOT, capture_output=True, text=True, timeout=60)
    try:
        runs = json.loads(r.stdout or "[]")
    except ValueError:
        return None
    return (runs[0].get("conclusion") or runs[0].get("status")) if runs else None


def postgame_pass(games, now, attempts, *, dry_run=False, ref="main", workflows=POSTGAME_WORKFLOWS,
                  active=None, conclusion=None, dispatcher=None) -> list:
    """POSTGAME target: start the postgame workflows at fixed offsets after each kickoff cluster
    (nfl_edge/handicap/automation.py). Each workflow's own gate decides what is ready; duplicates are no-ops."""
    active = active or active_runs
    conclusion = conclusion or last_conclusion
    dispatcher = dispatcher or dispatch
    ticks = postgame_ticks(games or [], now)
    lines = []
    for wf in workflows:
        line = {"at": now.isoformat(), "target": "POSTGAME", "workflow": wf,
                "due": [t["tick_id"] for t in ticks]}
        if not ticks:
            line.update(decision="idle", reason="no postgame tick owed")
            lines.append(line)
            continue
        per_wf = attempts.setdefault(wf, {})
        n_active = 0 if dry_run else active(wf)
        last = None if dry_run else conclusion(wf)
        go, why = decide_postgame(ticks, per_wf, now, n_active, last)
        line.update(decision=("dispatch" if go else "wait"), reason=why,
                    state=("RUNNING" if n_active else None), last_conclusion=last)
        if go:
            ok, msg = (True, "dry run") if dry_run else dispatcher(wf, ref)
            line.update(dispatched=ok, message=msg)
            if ok:
                record_dispatch(per_wf, ticks, now)
        lines.append(line)
    return lines


def horizon_trigger_epochs(games, src, now) -> list:
    """Every horizon trigger instant of the active slate (every target uses the same HORIZONS_MIN)."""
    from datetime import timedelta
    week = resolve_active_week(games, now, schedule_source=src)
    if week.get("status") != "OK":
        return []
    out = []
    for c in cluster_kickoffs(week.get("games") or []):
        for h in HORIZONS_MIN:
            out.append((c["kickoff_utc"] - timedelta(minutes=h)).timestamp())
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=340.0)
    ap.add_argument("--interval", type=float, default=240.0)
    ap.add_argument("--targets", default="RUN_NFL,THREE_ARM",
                    help="comma list of RUN_NFL, THREE_ARM, WAVE2 (wave2-research.yml), SIGNAL_LAB "
                         "(signal-lab-wave2.yml), POSTGAME "
                         "(postgame-settle / actual-wagers / shadow-v2-settle)")
    ap.add_argument("--ref", default="main")
    ap.add_argument("--chain-workflow", default=None,
                    help="dispatch this workflow once, near the end, so the next conductor does not depend on cron")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    requested = [t.strip() for t in a.targets.split(",")]
    targets = [t for t in requested if t in TARGETS]
    postgame = "POSTGAME" in requested
    pg_attempts: dict = {}
    end = time.time() + a.minutes * 60
    dispatched: dict = {}
    chained = False
    games, src, loaded = None, None, 0.0
    while time.time() < end:
        t0 = time.time()
        now = datetime.now(timezone.utc)
        try:
            if games is None or t0 - loaded > 3600:
                games, src = load_schedule(ROOT, allow_download=True)
                loaded = t0
            for line in one_pass(targets, games, src, now, dispatched, dry_run=a.dry_run, ref=a.ref,
                                 published_reader=run_nfl_published):
                print(json.dumps(line, default=str), flush=True)
            if postgame:
                for line in postgame_pass(games, now, pg_attempts, dry_run=a.dry_run, ref=a.ref):
                    print(json.dumps(line, default=str), flush=True)
        except Exception as exc:  # noqa: BLE001 -- one bad pass must not end the conductor
            print(json.dumps({"at": now.isoformat(), "decision": "error",
                              "reason": f"{type(exc).__name__}: {str(exc)[:200]}"}), flush=True)
        # Never hand over on top of a horizon trigger (conductor.handover_end). Only ever moves the end earlier.
        try:
            new_end, why = handover_end(end, horizon_trigger_epochs(games, src, now), time.time())
            if why and new_end < end:
                end = new_end
                print(json.dumps({"at": now.isoformat(), "decision": "handover-guard", "reason": why,
                                  "loop_ends_at": datetime.fromtimestamp(end, timezone.utc).isoformat()}), flush=True)
        except Exception as exc:  # noqa: BLE001 -- the guard is an optimisation; the natural end still works
            print(json.dumps({"at": now.isoformat(), "decision": "handover-guard-error",
                              "reason": f"{type(exc).__name__}: {str(exc)[:200]}"}), flush=True)
        if a.chain_workflow and should_chain(time.time(), end, chained):
            ok, msg = (True, "dry run") if a.dry_run else dispatch(a.chain_workflow, a.ref)
            print(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "decision": "chain",
                              "workflow": a.chain_workflow, "dispatched": ok, "message": msg}), flush=True)
            # A refused chain dispatch is retried on the next pass; the hourly cron is the backstop after that.
            chained = ok
        time.sleep(max(5.0, min(a.interval - (time.time() - t0), end - time.time())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
