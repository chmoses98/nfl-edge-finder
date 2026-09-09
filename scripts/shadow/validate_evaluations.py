#!/usr/bin/env python3
"""Gate between building evaluations and publishing them. Nothing reaches `market-data` unchecked.

Publishing is irreversible in practice -- the corpus is append-only and a defective row stays there -- so the
checks here are the last place a defect is cheap. Every one of them has a failure it exists to catch:

  manifest present and consistent   a batch with no manifest is a file nobody can verify later
  sha256 matches the file           a truncated or re-compressed batch
  row content hash matches content  a row edited after it was hashed
  no cross-batch contradiction      the same prediction with two different truths
  schema fields present             a row missing prediction_id / evaluation_version cannot be addressed
  settled rows carry a payout       "SETTLED" with settled_yes = None is not a settlement
  refused rows carry NO payout      a refusal with a number in it is a guess wearing a refusal's label
  binary payouts are 0 or 1         a "binary" settlement of 0.37 means the kind field is lying
  scalar payouts name their source  a scalar settlement with no exchange source is an invented number
  event and payout stay distinct    an event probability recorded as a contract value hides a discount
  final status was proven           a settled row whose evidence carries no final proof was not gated
  no post-kickoff close             the one silent corruption that would flatter every CLV number
  original ledger untouched         the ledger files must be byte-identical to what is published

Exit 0 only when every check passes. Usage:
  python3 scripts/shadow/validate_evaluations.py --root data/shadow/evaluations [--market-data /tmp/md]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.shadow import evaluation_store as ST                                  # noqa: E402
from nfl_edge.shadow.evaluation import CLOSE_OK, CLOSE_OK_STALE                     # noqa: E402
from nfl_edge.settlement.settle import (                                            # noqa: E402
    KIND_BINARY, KIND_SCALAR_EXACT, KIND_TIE_SPLIT, REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE, SETTLED,
)
from nfl_edge.settlement.kalshi_settlement import SOURCE_ARCHIVE, SOURCE_SNAPSHOT                    # noqa: E402

REQUIRED_FIELDS = ("prediction_id", "evaluation_version", "schema_version", "ticker", "model_version",
                   "settlement_status", "close_status", "content_hash", "evaluation_id")


def check_rows(rows, path, problems):
    for r in rows:
        pid = r.get("prediction_id") or "<no prediction_id>"
        for f in REQUIRED_FIELDS:
            if r.get(f) in (None, ""):
                problems.append(f"{path}: {pid} missing required field {f}")
        if r.get("evaluation_id") and r["evaluation_id"] != ST.evaluation_id(
                r.get("prediction_id") or "", r.get("evaluation_version") or ""):
            problems.append(f"{path}: {pid} evaluation_id is not sha1(prediction_id|evaluation_version)")
        status, payout, kind = r.get("settlement_status"), r.get("settled_yes"), r.get("settlement_kind")
        if status == SETTLED:
            if payout is None:
                problems.append(f"{path}: {pid} is SETTLED with no settled_yes")
            elif kind == KIND_BINARY and payout not in (0.0, 1.0):
                problems.append(f"{path}: {pid} is a binary settlement paying {payout}")
            elif payout is not None and not (0.0 <= float(payout) <= 1.0):
                problems.append(f"{path}: {pid} pays {payout}, outside [0, 1]")
            if kind == KIND_SCALAR_EXACT:
                # the one branch whose payout cannot be derived from football: it must name where it came from
                if not r.get("exact_payout_source"):
                    problems.append(f"{path}: {pid} is a scalar settlement with no exchange source recorded; "
                                    "a scalar payout with no provenance is an invented number")
                elif r["exact_payout_source"] not in (SOURCE_SNAPSHOT, SOURCE_ARCHIVE):
                    problems.append(f"{path}: {pid} scalar payout source {r['exact_payout_source']!r} is not an "
                                    "exchange settlement source")
                if r.get("exact_payout_known") is not True:
                    problems.append(f"{path}: {pid} is a scalar settlement not marked as an exact payout")
            if kind in (KIND_BINARY, KIND_TIE_SPLIT, KIND_SCALAR_EXACT) and not (
                    r.get("settlement_evidence") or {}).get("final_proofs"):
                problems.append(f"{path}: {pid} was settled with no final-status proof in its evidence; the "
                                "readiness gate cannot have run")
        else:
            if payout is not None:
                problems.append(f"{path}: {pid} is {status} yet carries settled_yes={payout}; "
                                "a refusal must never carry a payout")
            if not r.get("settlement_reason"):
                problems.append(f"{path}: {pid} is {status} with no reason recorded")
            if r.get("exact_payout_known"):
                problems.append(f"{path}: {pid} is {status} yet claims an exact payout is known")
            if status == REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE:
                # the refusal must still carry what WAS proven, or the finding is lost
                if (r.get("settlement_evidence") or {}).get("participation_branch") != "active_no_snap_proven":
                    problems.append(f"{path}: {pid} refuses the scalar payout without recording that the "
                                    "participation branch was proven")
        # the two model quantities must both be present on a row that has either, so neither can silently stand
        # in for the other downstream
        if r.get("model_contract_value") is not None and r.get("model_event_probability") is None:
            problems.append(f"{path}: {pid} carries a contract value with no event probability beside it")
        if r.get("close_status") in (CLOSE_OK, CLOSE_OK_STALE):
            if r.get("close_mid") is None:
                problems.append(f"{path}: {pid} close_status={r['close_status']} with no close_mid")
            # the one corruption that would flatter every CLV number in the corpus
            if r.get("close_observed_at") and r.get("kickoff_utc"):
                try:
                    if datetime.fromisoformat(r["close_observed_at"]) >= datetime.fromisoformat(r["kickoff_utc"]):
                        problems.append(f"{path}: {pid} close observed at {r['close_observed_at']} is NOT before "
                                        f"kickoff {r['kickoff_utc']}")
                except ValueError:
                    problems.append(f"{path}: {pid} has an unparseable close/kickoff timestamp")
            if r.get("close_minutes_to_kickoff") is not None and float(r["close_minutes_to_kickoff"]) < 0:
                problems.append(f"{path}: {pid} close is {r['close_minutes_to_kickoff']} minutes to kickoff "
                                "(negative means after kickoff)")


def ledger_untouched(market_data: str) -> tuple[str, list]:
    """The published ledger must be byte-identical to its committed state. A settle run only reads it.

    Returns `(state, problems)`. When the path is not a git worktree the check cannot run: that is reported as
    `not_a_git_worktree` rather than passing quietly, because "the check did not run" and "the check passed"
    must never look the same in the output.
    """
    if not market_data:
        return "not_checked", []
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=market_data,
                            capture_output=True, text=True)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return "not_a_git_worktree", []
    r = subprocess.run(["git", "status", "--porcelain", "--", "data/shadow/ledger", "data/kalshi"],
                       cwd=market_data, capture_output=True, text=True)
    if r.returncode != 0:
        return "error", [f"could not check the ledger worktree for modifications: {r.stderr.strip()[:200]}"]
    dirty = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if dirty:
        return "MODIFIED", [f"the published ledger/capture worktree has local modifications: {dirty[:5]}"]
    return "unmodified", []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", required=True,
                    help="evaluation corpus root to validate (repeatable)")
    ap.add_argument("--market-data", default="", help="market-data worktree, checked for ledger modifications")
    ap.add_argument("--require-rows", action="store_true", help="fail when there is nothing to validate")
    a = ap.parse_args()

    problems = []
    v = ST.verify_batches(a.root)
    problems.extend(v["problems"])
    n_rows = 0
    for root in a.root:
        for path in sorted(glob.glob(os.path.join(root, "*", "*.evaluations.jsonl.gz"))):
            rows = ST.read_rows(path)
            n_rows += len(rows)
            check_rows(rows, os.path.relpath(path, root), problems)
    ledger_state, ledger_problems = ledger_untouched(a.market_data)
    problems.extend(ledger_problems)

    report = {"roots": a.root, "batches": v["batches"], "rows": n_rows, "unique_rows": v["rows"],
              "published_ledger": ledger_state,
              "problems": problems[:50], "n_problems": len(problems), "ok": not problems}
    print(json.dumps(report, indent=1))
    if ledger_state == "not_a_git_worktree":
        print(f"::warning::{a.market_data} is not a git worktree, so the published ledger could not be "
              "checked for modifications")
    if a.require_rows and not n_rows:
        print("::error::no evaluation rows found to validate")
        return 3
    if problems:
        for p in problems[:20]:
            print(f"::error::{p}")
        return 2
    print(f"validated {v['batches']} batch(es), {n_rows} rows, {v['rows']} unique predictions: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
