#!/usr/bin/env python3
"""INDEPENDENT REPLAY: re-run the real-money gates against the exact evidence an approval was issued on.

    python3 scripts/handicap/replay_preflight_evidence.py \
        --result preflight_result.json \
        --approved-payload approved_payload.json \
        --evidence-root ../preflight-evidence \
        --handicap-root ../ledger

WHY THIS IS A SEPARATE ENTRY POINT
----------------------------------
"Trust the signed Airtable result" is authentication, not replay. It proves the worker said this; it proves
nothing about whether the market actually supported it. The whole point of committing pre-trade evidence to
an append-only branch is that somebody -- the twelve-hourly importer, an auditor, the owner on a Tuesday --
can go back to the documents, re-read them, and reach the verdict again without asking the worker.

So this script:

  1. reads the evidence documents at the paths the approval names;
  2. re-hashes each file and refuses any that does not match the hash the approval recorded;
  3. re-derives the manifest hash and refuses if it is not the one the signature covers;
  4. runs `gates.evaluate_gates` -- the SAME function, not a second implementation -- over the approved
     records, at each record's own `created_at`, which is the approval instant;
  5. prints whether the replay agrees with the approval.

A disagreement is not automatically a scandal: the risk gate needs the ledger, and an outstanding book that
has moved since will legitimately change a cumulative cap. Everything else -- the pre-kickoff gate, quote
freshness, the ceiling, the depth walk, fees, net EV -- is a pure function of the frozen record and the
frozen evidence, and those must agree exactly. The exit code says which happened.

Exit codes: 0 replay agrees, 1 replay DISAGREES, 2 the evidence or the inputs could not be read.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import gates as G              # noqa: E402
from nfl_edge.handicap import live_evidence as LE     # noqa: E402
from nfl_edge.handicap import preflight as P          # noqa: E402
from nfl_edge.handicap import risk as R               # noqa: E402
from nfl_edge.handicap import schema as S             # noqa: E402

# Gates that are a pure function of the frozen record plus the frozen evidence. These must reproduce exactly
# on a replay; anything else would mean the evidence has been altered or the gates have.
DETERMINISTIC_GATES = (G.G_DECISION_TIME, G.G_PRE_KICKOFF, G.G_QUOTE_FRESHNESS, G.G_CEILING,
                       G.G_IDENTITY, G.G_AVAILABILITY, G.G_DEPTH, G.G_FEE_SCHEDULE, G.G_NET_EV)


def load_evidence(evidence_root: str, result: dict) -> tuple:
    """Read the documents this approval names, verifying every hash on the way in.

    Returns `(documents, entries)`. Raises `EvidenceError` on the first mismatch: a replay that silently
    accepted altered evidence would be a rubber stamp with extra steps.
    """
    ev = (result or {}).get("evidence") or {}
    entries = ev.get("documents") or []
    if not entries:
        raise LE.EvidenceError(
            "this preflight result names no evidence documents, so there is nothing to replay against. "
            "Approvals issued before the pre-trade rebuild carry no evidence; they can only be re-checked "
            "against the capture stream.")
    docs = []
    for e in entries:
        path = os.path.join(evidence_root, str(e.get("path") or "").lstrip("/"))
        try:
            with open(path, "rb") as f:
                text = f.read().decode("utf-8")
        except OSError as exc:
            raise LE.EvidenceError(
                f"the evidence this approval cites is not present at {e.get('path')}: {exc}. An approval "
                "whose evidence has disappeared cannot be independently replayed.") from None
        docs.append(LE.load_document(text, expected_sha256=e.get("sha256")))

    claimed = ev.get("manifest_sha256")
    recomputed = LE.manifest_sha256(
        [{"path": e.get("path"), "sha256": e.get("sha256")} for e in entries],
        storage=ev.get("storage") or "", commit=ev.get("commit"))
    if claimed and claimed != recomputed:
        raise LE.EvidenceError(
            f"the evidence manifest does not reconstruct: the approval names {claimed} and these documents "
            f"hash to {recomputed}. The set of evidence has been changed since the approval.")
    return docs, entries


def replay(records: list, documents: list, *, ledger_root: str | None, root: str = ROOT,
           fee_observations_root: str | None = None) -> list:
    """Run the gates over the approved records against the stored evidence. Same function, same clock."""
    ctx = P.build_context(None, root=root,
                          capture_index=LE.EvidenceQuoteIndex(documents),
                          book_index=LE.EvidenceBookIndex(documents),
                          fee_observations_root=fee_observations_root)
    if ledger_root:
        policy = R.RiskPolicy.load(root)
        ctx.risk_report = R.report_for_batch(records, policy, ledger_root,
                                             records[0].get("bankroll_snapshot") if records else None)
    return [G.evaluate_gates(rec, ctx) for rec in records]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--result", required=True, help="the row's `Preflight Result` JSON")
    ap.add_argument("--approved-payload", required=True, help="the row's `Approved Payload` JSON")
    ap.add_argument("--evidence-root", required=True,
                    help="checkout of the preflight-evidence branch (or a local evidence directory)")
    ap.add_argument("--handicap-root", default=None,
                    help="checkout of handicap-data; without it the portfolio gate is reported UNAVAILABLE "
                         "and only the deterministic gates are compared")
    ap.add_argument("--fee-observations", default=None)
    a = ap.parse_args(argv)

    try:
        with open(a.result) as f:
            result = json.load(f)
        with open(a.approved_payload) as f:
            payload = json.load(f)
    except (OSError, ValueError) as e:
        print(f"could not read the inputs: {e}")
        return 2
    records = payload if isinstance(payload, list) else [payload]

    try:
        documents, entries = load_evidence(a.evidence_root, result)
    except LE.EvidenceError as e:
        print(f"EVIDENCE: {e}")
        return 2

    print(f"replaying {len(records)} record(s) against {len(entries)} verified evidence document(s)")
    reports = replay(records, documents, ledger_root=a.handicap_root,
                     fee_observations_root=a.fee_observations)

    claimed = {c.get("recommendation_id"): c for c in (result.get("candidates") or [])}
    disagreed = False
    for rec, rep in zip(records, reports):
        rid = rec.get("recommendation_id")
        was_approved = bool((claimed.get(rid) or {}).get("may_be_shown_as_a_bet"))
        print(f"  {rid}: approval said {'APPROVED' if was_approved else 'NOT APPROVED'}, "
              f"replay says {rep.overall}")
        for name in DETERMINISTIC_GATES:
            g = rep.gates.get(name)
            if g is None:
                continue
            if was_approved and g.status in G.BLOCKING:
                print(f"    DISAGREES {name}: {g.reason}")
                disagreed = True
        if rec.get("decision") == S.RECOMMENDED and not rec.get("test_only"):
            if was_approved and rep.overall == G.FAIL and not disagreed:
                print("    (blocked only by a non-deterministic gate; see portfolio risk above)")
    if disagreed:
        print("REPLAY DISAGREES with the approval on at least one deterministic gate.")
        return 1
    print("replay agrees: the stored evidence still supports every deterministic gate this approval passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
