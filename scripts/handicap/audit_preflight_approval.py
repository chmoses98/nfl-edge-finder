#!/usr/bin/env python3
"""AUDIT ONLY: authenticate one real, already-issued production approval. Writes nothing, anywhere.

    AIRTABLE_TOKEN=... PREFLIGHT_SIGNING_KEY=... \
        python3 scripts/handicap/audit_preflight_approval.py \
            --airtable-record-id recXXXXXXXXXXXXXX --run-id RUN-ID \
            --evidence-root ../evidence

WHY THIS EXISTS. Phase 4H proved the evidence chain from outside the runner: the committed document hashes
to what the approval names, the manifest reconstructs, the gates replay, and every tampered variant fails
closed. What could NOT be proved from outside is the half that needs the two secrets -- that the production
HMAC over the production payloads verifies with the real key. That check already exists and is already
exercised on every import; it simply has no operator-runnable entry point, because the importer performs it
as a side effect of archiving. This script is that entry point and nothing more.

WHAT IT IS NOT. It is not a second approval engine. Every judgement here is made by the SAME functions the
importer uses -- `airtable_bridge.read_preflight_evidence`, `approval.verify`, `approval.check_approval_window`
-- so a pass here means the same thing a pass in the importer means. Reimplementing the HMAC, the payload
hashing or the evidence rules would prove only that a second implementation agrees with itself, which is
worth nothing. The only logic that belongs to this file is selecting the row, ordering the assertions, and
printing a verdict that carries no private data.

WHAT IT MAY TOUCH. Airtable: one GET. Git: nothing. Kalshi: nothing. The row is located with
`list_by_status(PREFLIGHT_APPROVED)`, which is a read, and which makes "the row is approved" a fact about
where it was found rather than a string this script compares for itself.

THE NEGATIVE CONTROLS ARE THE POINT. A verification that only ever says PASS has not been shown to be
capable of saying FAIL. Each control presents the REAL signed approval with one fact altered in memory and
requires a refusal; a control that verifies is a defect and exits non-zero, exactly like a failed positive.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import airtable_bridge as AB      # noqa: E402
from nfl_edge.handicap import approval as APPROVAL       # noqa: E402

OK, BAD = "PASS", "FAIL"


class AuditFailure(RuntimeError):
    """A positive assertion failed, or a negative control verified when it must have refused."""


def _scrub(text: str, *secrets) -> str:
    """Belt and braces. Nothing here is supposed to carry a secret; this makes a slip non-fatal."""
    out = str(text)
    for s in secrets:
        if s:
            out = out.replace(s, "***")
    return out


def find_approved_row(client, record_id: str) -> dict:
    """The row, located among PREFLIGHT_APPROVED rows so its status is established by the query itself."""
    rows = client.list_by_status(AB.STATUS_PREFLIGHT_APPROVED)
    for row in rows:
        if row.get("id") == record_id:
            return row
    raise AuditFailure(
        f"{record_id} is not among the {len(rows)} row(s) currently in "
        f"{AB.STATUS_PREFLIGHT_APPROVED}. An approval audit runs against an approved row; a row in any "
        "other status has not been approved and there is nothing here to authenticate.")


def audit(row: dict, *, record_id: str, run_id: str, evidence_root: str, key: bytes) -> dict:
    """Every positive assertion, in the order the importer makes them. Raises on the first failure."""
    fields = row.get("fields") or {}
    out = {}

    claimed_run = fields.get(AB.F_RUN_ID)
    if claimed_run != run_id:
        raise AuditFailure(f"row Run ID is {claimed_run!r}, expected {run_id!r}")
    out["run_id"] = run_id
    out["status"] = fields.get(AB.F_STATUS)

    candidate_raw = fields.get(AB.F_PAYLOAD)
    approved_raw = fields.get(AB.F_APPROVED_PAYLOAD)
    result_raw = fields.get(AB.F_PREFLIGHT_RESULT)
    for name, raw in ((AB.F_PAYLOAD, candidate_raw), (AB.F_APPROVED_PAYLOAD, approved_raw),
                      (AB.F_PREFLIGHT_RESULT, result_raw)):
        if not isinstance(raw, str) or not raw.strip():
            raise AuditFailure(f"the row carries no {name}; there is nothing to authenticate")
    result = json.loads(result_raw)

    schema = result.get("approval_schema")
    if schema != APPROVAL.APPROVAL_SCHEMA:
        raise AuditFailure(f"approval schema is {schema!r}, expected {APPROVAL.APPROVAL_SCHEMA}")
    out["schema"] = schema

    # The evidence, re-read and re-hashed by the importer's own function. A v2 approval that cannot be
    # bound to its documents raises here rather than reaching the signature check.
    documents, manifest = AB.read_preflight_evidence(fields, evidence_root)
    if not manifest:
        raise AuditFailure(
            "the importer's evidence reader returned no manifest for this row, so the approval is not "
            "bound to any evidence and this audit has nothing to verify against")
    out["evidence_documents"] = len(documents or [])
    out["evidence_manifest_sha256"] = manifest

    # `verify` recomputes both payload hashes from the payloads in front of it and compares them to the
    # signed ones, checks schema and algorithm, checks the row and run the approval names, and finally
    # checks the HMAC. One call covers assertions 4, 5, 6, 9, 10, 13 and 14.
    verified = APPROVAL.verify(
        result, key=key, airtable_record_id=record_id, run_id=run_id,
        candidate_payload=candidate_raw, approved_payload=approved_raw,
        evidence_manifest_sha256=manifest)

    created = AB._parse_ts("createdTime", row.get("createdTime"))
    APPROVAL.check_approval_window(verified.approval_as_of, created)

    out["candidate_payload_sha256"] = verified.candidate_payload_sha256
    out["approved_payload_sha256"] = verified.approved_payload_sha256
    out["approval_as_of"] = verified.approval_as_of.isoformat()
    out["airtable_created_time"] = created.isoformat()
    out["verified"] = verified
    out["_inputs"] = (result, candidate_raw, approved_raw, manifest)
    return out


def negative_controls(*, result: dict, candidate_raw: str, approved_raw: str, manifest: str,
                      record_id: str, run_id: str, key: bytes) -> list:
    """Present the REAL signed approval with one fact altered. Every one must refuse.

    Two shapes per identity field. Altering only what the approval CLAIMS is caught by the explicit row/run
    checks; altering the claim AND what it is presented against reaches the HMAC, which is what proves the
    field is actually signed rather than merely compared.
    """
    def attempt(label, res=None, cand=None, appr=None, man=None, rec=None, run=None):
        try:
            APPROVAL.verify(res if res is not None else result, key=key,
                            airtable_record_id=rec or record_id, run_id=run or run_id,
                            candidate_payload=cand if cand is not None else candidate_raw,
                            approved_payload=appr if appr is not None else approved_raw,
                            evidence_manifest_sha256=man if man is not None else manifest)
        except APPROVAL.ApprovalError as e:
            return {"control": label, "outcome": "REFUSED", "reason": str(e).split(".")[0][:110]}
        return {"control": label, "outcome": "**VERIFIED**", "reason": "accepted a tampered approval"}

    def mutated(**kw):
        r = copy.deepcopy(result)
        r.update(kw)
        return r

    other_rec, other_run = record_id[:-1] + ("X" if not record_id.endswith("X") else "Y"), run_id + "-OTHER"
    return [
        attempt("tamper_approved_payload", appr=approved_raw + " "),
        attempt("tamper_candidate_payload", cand=candidate_raw + " "),
        attempt("tamper_approval_as_of",
                res=mutated(approval_as_of="2000-01-01T00:00:00+00:00")),
        attempt("tamper_manifest", res=mutated(evidence_manifest_sha256="0" * 64)),
        attempt("tamper_record_id", res=mutated(airtable_record_id=other_rec)),
        attempt("tamper_record_id_and_row", res=mutated(airtable_record_id=other_rec), rec=other_rec),
        attempt("tamper_run_id", res=mutated(run_id=other_run)),
        attempt("tamper_run_id_and_row", res=mutated(run_id=other_run), run=other_run),
        attempt("tamper_signature", res=mutated(approval_signature="0" * 64)),
        attempt("tamper_schema_downgrade",
                res=mutated(approval_schema=APPROVAL.LEGACY_APPROVAL_SCHEMAS[0])),
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--airtable-record-id", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--evidence-root", required=True,
                    help="checkout of the preflight-evidence branch")
    ap.add_argument("--base-id", default=AB.BASE_ID)
    ap.add_argument("--table-id", default=AB.TABLE_ID)
    a = ap.parse_args(argv)

    token = os.environ.get("AIRTABLE_TOKEN", "").strip()
    raw_key = os.environ.get(APPROVAL.SIGNING_KEY_ENV, "").strip()
    # These are FAILURES, never a quiet skip. An audit that cannot run has not passed.
    if not token:
        print("AIRTABLE_TOKEN is not set; the audit cannot read the row.", file=sys.stderr)
        return 2
    if not raw_key:
        print(f"{APPROVAL.SIGNING_KEY_ENV} is not set; the audit cannot authenticate the approval.",
              file=sys.stderr)
        return 2
    key = APPROVAL.signing_key()

    print("PHASE 4H-A AUTHENTICATION AUDIT")
    print()
    try:
        client = AB.AirtableClient(token, a.base_id, a.table_id)
        row = find_approved_row(client, a.airtable_record_id)
        res = audit(row, record_id=a.airtable_record_id, run_id=a.run_id,
                    evidence_root=a.evidence_root, key=key)
    except (AuditFailure, APPROVAL.ApprovalError, AB.BridgeError, AB.ConfigurationError,
            AB.TransientError, ValueError) as e:
        print(f"record_id: {a.airtable_record_id}")
        print(f"VERDICT:\nPHASE 4H-A {BAD}")
        print(f"reason: {_scrub(e, token, raw_key)}", file=sys.stderr)
        return 1

    result, candidate_raw, approved_raw, manifest = res.pop("_inputs")
    res.pop("verified")
    print(f"record_id: {a.airtable_record_id}")
    print(f"run_id: {res['run_id']}")
    print(f"status: {res['status']}")
    print(f"schema: {res['schema']}")
    print()
    print(f"candidate_payload_sha256: {res['candidate_payload_sha256']}")
    print(f"approved_payload_sha256: {res['approved_payload_sha256']}")
    print(f"evidence_manifest_sha256: {res['evidence_manifest_sha256']}")
    print(f"evidence_documents: {res['evidence_documents']}")
    print(f"airtable_created_time: {res['airtable_created_time']}")
    print(f"approval_as_of: {res['approval_as_of']}")
    print("production_signature: PASS")
    print("exact_evidence_binding: PASS")
    print("approval_chronology: PASS")
    print()

    controls = negative_controls(result=result, candidate_raw=candidate_raw, approved_raw=approved_raw,
                                 manifest=manifest, record_id=a.airtable_record_id, run_id=a.run_id,
                                 key=key)
    leaked = [c for c in controls if c["outcome"] != "REFUSED"]
    for c in controls:
        print(f"{c['control']}: {c['outcome']}")
    print()
    print("airtable_writes: 0")
    print("git_writes: 0")
    print("private_kalshi_calls: 0")
    print("orders_placed: 0")
    print()
    if leaked:
        print(f"VERDICT:\nPHASE 4H-A {BAD}")
        for c in leaked:
            print(f"negative control {c['control']} VERIFIED a tampered approval", file=sys.stderr)
        return 1
    print(f"VERDICT:\nPHASE 4H-A {OK}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
