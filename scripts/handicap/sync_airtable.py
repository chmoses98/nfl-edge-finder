#!/usr/bin/env python3
"""Poll the Sports Betting Bridge Airtable inbox and import pending handicap runs into handicap-data.

    AIRTABLE_TOKEN=... python3 scripts/handicap/sync_airtable.py --handicap-root ../ledger
    AIRTABLE_TOKEN=... python3 scripts/handicap/sync_airtable.py --handicap-root ../ledger --dry-run

This is the ChatGPT -> Airtable -> GitHub leg. ChatGPT writes one row per handicap run; this reads the rows
marked READY_FOR_SYNC, validates each batch through the existing handicap schema, materialises the records as
immutable files, commits and pushes them, and only then marks the row SYNCED.

The ordering is the whole point and is not negotiable:

    validate -> write -> commit -> PUSH SUCCEEDS -> mark SYNCED

A row marked SYNCED asserts that its records are durably on the remote branch. Marking it before the push
would let a failed push turn into permanent data loss, because the next poll would skip the row. Marking it
after means the worst case is a row that is re-imported, which the idempotency check absorbs silently.

Exit codes: 0 nothing to do or everything imported, 1 at least one row failed permanently (ERROR),
2 configuration problem, 3 a transient failure left work pending (rows stay READY_FOR_SYNC for the next run).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import airtable_bridge as AB    # noqa: E402
from nfl_edge.handicap import store                    # noqa: E402


def log(msg: str) -> None:
    """Every line the sync prints goes through here.

    Payloads never do. A theses-and-probabilities dump in a public Actions log would publish the decision
    before the market resolves it, so the log carries identities, counts and hashes and nothing else.
    """
    print(msg, flush=True)


# ---- git ------------------------------------------------------------------------------------------

def _git(args, cwd, check=True, capture=True):
    r = subprocess.run(["git"] + args, cwd=cwd, text=True, capture_output=capture)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed ({r.returncode}): {(r.stderr or '').strip()[-400:]}")
    return r


def commit_and_push(ledger_root: str, message: str, *, branch: str = store.BRANCH,
                    attempts: int = 5, sleep=time.sleep) -> None:
    """Commit whatever the importer created and get it onto the remote, or raise TransientError.

    Never force-pushes: this branch's audit value is that nothing on it is ever rewritten. Conflicts are
    close to impossible by construction (every path is a fresh record id), so a rejected push means somebody
    else pushed a different record and a plain rebase is the correct, safe response.
    """
    _git(["add", "-A", "--", "data"], cwd=ledger_root)
    if _git(["diff", "--cached", "--quiet"], cwd=ledger_root, check=False).returncode == 0:
        log("nothing staged; no commit created")
        return
    _git(["commit", "-q", "-m", message], cwd=ledger_root)

    last = ""
    for attempt in range(1, attempts + 1):
        # Fully qualified destination: from a detached HEAD (a worktree checkout, or any runner that did
        # not create a local branch) git cannot guess `handicap-data` and refuses the push outright.
        r = _git(["push", "origin", f"HEAD:refs/heads/{branch}"], cwd=ledger_root, check=False)
        if r.returncode == 0:
            log(f"pushed to {branch}")
            return
        last = (r.stderr or "").strip()[-300:]
        log(f"push attempt {attempt}/{attempts} failed: {last}")
        if attempt == attempts:
            break
        _git(["fetch", "origin", branch], cwd=ledger_root, check=False)
        rb = _git(["rebase", f"origin/{branch}"], cwd=ledger_root, check=False)
        unmerged = _git(["diff", "--name-only", "--diff-filter=U"], cwd=ledger_root,
                        check=False).stdout.strip()
        if rb.returncode != 0 or unmerged:
            _git(["rebase", "--abort"], cwd=ledger_root, check=False)
            raise AB.TransientError(
                f"rebase onto origin/{branch} conflicted on: {unmerged or 'unknown paths'}. Refusing to "
                "resolve automatically on an immutable ledger.")
        sleep(min(2 ** attempt, 30))
    raise AB.TransientError(f"could not push to {branch} after {attempts} attempts: {last}")


# ---- sync -----------------------------------------------------------------------------------------

def sync(client, ledger_root: str, *, dry_run: bool = False, now=None,
         pusher=commit_and_push, sport: str = AB.SPORT_NFL, update_status: bool = True) -> int:
    now = now or datetime.now(timezone.utc)

    try:
        rows = client.list_ready(sport=sport)
    except AB.TransientError as e:
        log(f"TRANSIENT: could not read Airtable: {e}")
        log("rows left READY_FOR_SYNC; the next scheduled run retries")
        return 3

    log(f"{len(rows)} row(s) with Status={AB.STATUS_READY} Sport={sport} "
        f"({client.request_count} Airtable request(s) so far)")
    if not rows:
        log("nothing to import")
        return 0

    # Plan every row before writing any of them, and keep the rows independent: one corrupt batch must not
    # stop the others in the same cycle from landing.
    plans, errors = [], {}
    for row in rows:
        rid = (row.get("id") or "").strip()
        if not rid:
            # Unaddressable: there is no id to PATCH a status onto, so it cannot even be marked ERROR.
            log("ERROR  <no record id>: Airtable row has no record id; skipping")
            continue
        try:
            plan = AB.plan_run(row, ledger_root, now=now,
                               base_id=client.base_id, table_id=client.table_id)
        except AB.BridgeError as e:
            log(f"ERROR  {rid}: {e}")
            errors[rid] = str(e)
            continue
        for w in plan.warnings:
            log(f"warn   {rid}: {w}")
        log(f"OK     {rid} run={plan.run_id} season={plan.season} week={plan.week} "
            f"sha={plan.sha[:12]} records={sum(plan.decisions.values())} "
            f"decisions={plan.decisions} new={len(plan.to_write)} "
            f"already_present={len(plan.already_present)}")
        plans.append(plan)

    if dry_run:
        log("\n(dry run -- nothing written, nothing committed, no Airtable status changed)")
        return 1 if errors else 0

    # Write. A row that fails here is a permanent problem with that row only; its files are rolled back.
    written_total, applied = [], []
    for plan in plans:
        try:
            written = AB.apply_plan(plan)
        except AB.BridgeError as e:
            log(f"ERROR  {plan.airtable_id}: {e}")
            errors[plan.airtable_id] = str(e)
            continue
        written_total.extend(written)
        applied.append(plan)
        log(f"wrote  {plan.airtable_id}: {len(written)} file(s)")

    # Push before any row is called SYNCED.
    pushed = True
    if written_total:
        try:
            pusher(ledger_root, _commit_message(applied))
        except (AB.TransientError, RuntimeError) as e:
            pushed = False
            log(f"TRANSIENT: {e}")
            log("records are written locally but NOT durable; leaving rows READY_FOR_SYNC so the next run "
                "re-imports them (already-identical records are absorbed idempotently)")
    else:
        log("no new records; skipping commit (an empty commit would claim work that did not happen)")

    # A row that wrote nothing was already durable BEFORE this run: `plan_run` ran for every row before any
    # row was applied, so `already_present` can only refer to files that came out of the origin checkout,
    # never to files a sibling row created moments ago. That is what makes it safe to call such a row SYNCED
    # even when this run's push failed -- and it is the heal path for "push succeeded, status update did not".
    synced = []
    for plan in applied:
        if plan.writes_nothing:
            log(f"heal   {plan.airtable_id}: all {len(plan.already_present)} record(s) already durable and "
                "identical; marking SYNCED without a commit")
            synced.append(plan.airtable_id)
        elif pushed:
            synced.append(plan.airtable_id)

    updates = {rid: AB.STATUS_ERROR for rid in errors}
    updates.update({rid: AB.STATUS_SYNCED for rid in synced})
    if updates and not update_status:
        log(f"--no-push: NOT updating Airtable; would have set {len(synced)} -> {AB.STATUS_SYNCED}, "
            f"{len(errors)} -> {AB.STATUS_ERROR}")
    elif updates:
        try:
            client.set_status(updates)
            log(f"Airtable: {len(synced)} -> {AB.STATUS_SYNCED}, {len(errors)} -> {AB.STATUS_ERROR}")
        except AB.TransientError as e:
            log(f"TRANSIENT: the ledger is durable but the Airtable status update failed: {e}")
            log("the next run will recognise these records as already imported and set the status then")
            return 3

    log(f"total Airtable requests this run: {client.request_count}")
    if not pushed:
        return 3
    return 1 if errors else 0


def _commit_message(plans: list) -> str:
    runs = len(plans)
    counts = {}
    for p in plans:
        for decision, n in p.decisions.items():
            counts[decision] = counts.get(decision, 0) + n
    detail = ", ".join(f"{n} {d.lower()}" for d, n in sorted(counts.items())) or "0 records"
    return (f"sync {runs} Airtable handicap run{'s' if runs != 1 else ''} ({detail})\n\n"
            + "\n".join(f"{p.airtable_id} run={p.run_id} sha={p.sha[:12]} "
                        f"new={len(p.to_write)} already={len(p.already_present)}" for p in plans))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--handicap-root", required=True,
                    help="worktree/checkout of the handicap-data branch (the ledger)")
    ap.add_argument("--base-id", default=AB.BASE_ID)
    ap.add_argument("--table-id", default=AB.TABLE_ID)
    ap.add_argument("--sport", default=AB.SPORT_NFL)
    ap.add_argument("--dry-run", action="store_true",
                    help="validate pending rows and report; write nothing, change no Airtable status")
    ap.add_argument("--no-push", action="store_true",
                    help="write records but do not commit or push (local inspection only)")
    a = ap.parse_args(argv)

    token = os.environ.get("AIRTABLE_TOKEN", "").strip()
    if not token:
        log("AIRTABLE_TOKEN is not set.")
        log("Create a narrowly scoped Airtable personal access token (data.records:read and")
        log("data.records:write, limited to the Sports Betting Bridge base) and store it as the")
        log("GitHub Actions secret AIRTABLE_TOKEN. See docs/AIRTABLE_BRIDGE.md.")
        return 2
    if not os.path.isdir(a.handicap_root):
        log(f"--handicap-root {a.handicap_root} is not a directory")
        return 2

    client = AB.AirtableClient(token, a.base_id, a.table_id)
    # --no-push must also withhold the status update: SYNCED asserts durability on the remote, and a local
    # write that was never pushed has not earned it.
    pusher = (lambda *_args, **_kw: log("--no-push: skipping commit/push")) if a.no_push else commit_and_push
    try:
        return sync(client, os.path.abspath(a.handicap_root), dry_run=a.dry_run, pusher=pusher,
                    sport=a.sport, update_status=not a.no_push)
    except AB.BridgeError as e:
        # Configuration-shaped BridgeErrors (an empty token) reach here; row-shaped ones never do.
        log(f"FATAL: {AB.scrub(e, token)}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
