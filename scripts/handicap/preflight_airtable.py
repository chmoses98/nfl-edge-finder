#!/usr/bin/env python3
"""The PRE-TRADE leg: answer PREFLIGHT_REQUESTED rows in Airtable, event-driven.

    AIRTABLE_TOKEN=... python3 scripts/handicap/preflight_airtable.py \
        --market-data ../market-data --handicap-root ../ledger

WHY THIS EXISTS SEPARATELY FROM THE IMPORTER
--------------------------------------------
`preflight_candidate.py` is the right control and the wrong interface. ChatGPT is the thing that produces a
candidate, and in its runtime it can write Airtable and read GitHub -- it cannot run a script, dispatch a
workflow, or clone a branch. So "ChatGPT runs preflight_candidate.py" was a documented intention, not a
mechanism, and a control that the recommending interface cannot reach does not protect anything.

    ChatGPT
      -> writes a PREFLIGHT_REQUESTED row (candidates in `Payload`)
      -> an Airtable Automation fires a GitHub workflow_dispatch          <- one-time owner setup
      -> that workflow checks out main + market-data + handicap-data and runs THIS script
      -> the row becomes PREFLIGHT_APPROVED or PREFLIGHT_BLOCKED, with the verdict in `Preflight Result`
      -> ChatGPT reads the row
      -> ONLY an APPROVED candidate may be surfaced as a BET
      -> the final recommendation is then submitted READY_FOR_SYNC for normal 12-hour archival transport

TWO TRANSPORTS, TWO CADENCES, ON PURPOSE
----------------------------------------
    PRE-TRADE       event-driven. A quote is fresh for fifteen minutes and the owner needs the answer now.
    RECOMMENDATION  twelve-hourly. Archival transport for a decision already made and already approved.

The archival cadence is unchanged and is not to be "fixed" by polling faster: polling for preflight would
spend the Airtable free-tier allowance the archival leg depends on, to buy latency on a leg that does not
need it. This script is invoked BY an event; it does not sit and watch.

WHAT IT DECIDES
---------------
Nothing. It calls `preflight.preflight_batch`, the same function the CLI calls, which calls
`gates.evaluate_gates`, the same function the importer later replays. This script is transport.

FAIL CLOSED
-----------
A row that errors becomes PREFLIGHT_ERROR, never APPROVED. A row this script cannot reach stays
PREFLIGHT_REQUESTED, which is also not APPROVED. There is no state in which silence means yes.

Exit codes: 0 every request answered (approved or blocked -- both are answers), 1 at least one row was
unusable, 2 configuration problem, 3 a transient failure left rows unanswered.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.execution import depth as DEPTH          # noqa: E402
from nfl_edge.execution import quotes as Q             # noqa: E402
from nfl_edge.handicap import airtable_bridge as AB    # noqa: E402
from nfl_edge.handicap import preflight as P           # noqa: E402
from nfl_edge.handicap import risk as RISK             # noqa: E402


def log(msg: str) -> None:
    """Identities, counts and verdicts. Never a payload.

    A thesis dumped into a public Actions log publishes the decision before the market resolves it.
    """
    print(msg, flush=True)


def _summary(results: list, *, run_id: str, now: datetime) -> dict:
    """What gets written back to Airtable. Small, readable, and legible to a human in a hurry."""
    return {
        "schema": "preflight-result/1",
        "run_id": run_id,
        "answered_at": now.isoformat(),
        "verdict": ("APPROVED" if results and all(r.may_be_shown_as_a_bet for r in results)
                    else "BLOCKED"),
        "n_candidates": len(results),
        "n_approved": sum(1 for r in results if r.may_be_shown_as_a_bet),
        "candidates": [{
            "recommendation_id": r.candidate_id,
            "verdict": r.verdict,
            "may_be_shown_as_a_bet": r.may_be_shown_as_a_bet,
            "surface_as": r.surface_as,
            "decision_as_of": r.as_of,
            "proposed_stake": r.proposed_stake,
            "approved_stake": r.approved_stake,
            "blocking_reasons": r.blocking_reasons,
            "warnings": r.warnings,
            "executable_price": (r.decision_quote or {}).get("executable_price"),
            "full_position_vwap": (r.depth or {}).get("vwap"),
            "worst_fill_price": (r.depth or {}).get("worst_price"),
            "net_ev_dollars": (r.net_ev or {}).get("net_ev_dollars"),
            "conservative_net_ev_dollars": (r.net_ev or {}).get("conservative_net_ev_dollars"),
            "gates": {k: v.get("status") for k, v in (r.gates or {}).items()},
        } for r in results],
        "outstanding_exposure": {
            "total": ((results[0].outstanding or {}).get("total") if results else None),
            "by_correlation_group": ((results[0].outstanding or {}).get("by_correlation_group")
                                     if results else None),
        },
        "note": ("Only candidates with may_be_shown_as_a_bet=true may be surfaced as a BET or a final "
                 "RECOMMENDED instruction, and only at approved_stake. Everything else is a CANDIDATE, a "
                 "WATCHLIST entry or a PASS. This answer approves nothing automatically and places nothing."),
    }


def answer_row(row: dict, *, market_data_root: str, ledger_root: str, now: datetime) -> tuple[str, dict]:
    """Preflight one Airtable row. Returns the status to write and the result body."""
    fields = row.get("fields") or {}
    run_id = (fields.get(AB.F_RUN_ID) or "").strip()
    candidates = AB.parse_payload(fields.get(AB.F_PAYLOAD))

    results = P.preflight_batch(
        candidates, market_data_root=market_data_root, ledger_root=ledger_root, root=ROOT)
    body = _summary(results, run_id=run_id, now=now)
    status = (AB.STATUS_PREFLIGHT_APPROVED if body["verdict"] == "APPROVED"
              else AB.STATUS_PREFLIGHT_BLOCKED)
    return status, body


def run(client, *, market_data_root: str, ledger_root: str, sport: str = AB.SPORT_NFL,
        now: datetime | None = None, update_status: bool = True) -> int:
    now = now or datetime.now(timezone.utc)

    try:
        rows = client.list_by_status(AB.STATUS_PREFLIGHT_REQUESTED, sport=sport)
    except AB.TransientError as e:
        log(f"TRANSIENT: could not read Airtable: {e}")
        log("rows left PREFLIGHT_REQUESTED; an unanswered request is not an approval")
        return 3

    log(f"{len(rows)} row(s) with Status={AB.STATUS_PREFLIGHT_REQUESTED} Sport={sport}")
    if not rows:
        log("nothing to preflight")
        return 0

    updates, had_error = {}, False
    for row in rows:
        rid = (row.get("id") or "").strip()
        if not rid:
            log("ERROR  <no record id>: Airtable row has no record id; cannot be answered")
            had_error = True
            continue
        try:
            status, body = answer_row(row, market_data_root=market_data_root,
                                      ledger_root=ledger_root, now=now)
        except (AB.BridgeError, ValueError, RISK.RiskPolicyError) as e:
            # An unusable request is an ERROR, never an approval. The reason goes back to the row so
            # ChatGPT can see what to fix without anyone reading a workflow log.
            log(f"ERROR  {rid}: {AB.scrub(e, '')}")
            had_error = True
            updates[rid] = {
                AB.F_STATUS: AB.STATUS_PREFLIGHT_ERROR,
                AB.F_PREFLIGHT_RESULT: json.dumps(
                    {"schema": "preflight-result/1", "verdict": "ERROR",
                     "answered_at": now.isoformat(), "error": str(e)[:2000],
                     "note": "An unanswered or errored request is NOT an approval."}, indent=1),
            }
            continue

        approved = body["n_approved"]
        log(f"{status:<20} {rid} run={body['run_id']} candidates={body['n_candidates']} "
            f"approved={approved}")
        for c in body["candidates"]:
            if not c["may_be_shown_as_a_bet"]:
                for b in c["blocking_reasons"]:
                    log(f"   blocked {c['recommendation_id']}: {b}")
        updates[rid] = {AB.F_STATUS: status,
                        AB.F_PREFLIGHT_RESULT: json.dumps(body, indent=1, default=str)}

    if not update_status:
        log(f"--no-write: NOT updating Airtable; would have answered {len(updates)} row(s)")
        return 1 if had_error else 0

    try:
        client.write_fields(updates)
    except AB.TransientError as e:
        log(f"TRANSIENT: verdicts computed but could not be written back: {e}")
        log("rows stay PREFLIGHT_REQUESTED; the next dispatch recomputes them")
        return 3

    log(f"answered {len(updates)} row(s); total Airtable requests this run: {client.request_count}")
    return 1 if had_error else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--market-data", required=True,
                    help="checkout of market-data; the quote and depth gates read its capture stream")
    ap.add_argument("--handicap-root", required=True,
                    help="checkout of handicap-data; OUTSTANDING portfolio exposure is read from it")
    ap.add_argument("--base-id", default=AB.BASE_ID)
    ap.add_argument("--table-id", default=AB.TABLE_ID)
    ap.add_argument("--sport", default=AB.SPORT_NFL)
    ap.add_argument("--no-write", action="store_true",
                    help="compute verdicts and print them; change no Airtable row")
    a = ap.parse_args(argv)

    token = os.environ.get("AIRTABLE_TOKEN", "").strip()
    if not token:
        log("AIRTABLE_TOKEN is not set. See docs/AIRTABLE_BRIDGE.md.")
        return 2
    for label, path in (("--market-data", a.market_data), ("--handicap-root", a.handicap_root)):
        if not os.path.isdir(path):
            log(f"{label} {path} is not a directory. Preflight needs the capture stream (executable price "
                "and order book) and the committed ledger (outstanding exposure); neither can be assumed "
                "empty, so nothing is answered.")
            return 2

    client = AB.AirtableClient(token, a.base_id, a.table_id)
    try:
        return run(client, market_data_root=os.path.abspath(a.market_data),
                   ledger_root=os.path.abspath(a.handicap_root), sport=a.sport,
                   update_status=not a.no_write)
    except AB.BridgeError as e:
        log(f"FATAL: {AB.scrub(e, token)}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
