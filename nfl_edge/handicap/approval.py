"""The PRE-TRADE APPROVAL contract: what an approval says, and how the ledger knows the worker said it.

WHY THIS IS A MODULE AND NOT A CONVENTION
-----------------------------------------
The bridge previously bound an approved batch to its approval by a hash the approval itself carried. That
detects an *accident* -- a payload edited after approval -- and nothing else. Anyone able to write Airtable
could write both halves:

    Approved Payload = an ungated recommendation
    Preflight Result = {"verdict": "APPROVED", "approved_payload_sha256": sha256(that payload)}

and the two agree perfectly. So "a direct READY_FOR_SYNC row cannot bypass preflight" was a statement about
tidiness, not about security: the check proved the approval was SELF-CONSISTENT, never that the trusted
worker issued it.

An approval is therefore AUTHENTICATED. The preflight worker signs a canonical message with an HMAC key that
exists only as a GitHub Actions secret; the importer reconstructs that message from the ROW'S OWN FACTS and
verifies. Forging an approval now requires the signing key, which is not in Airtable, not in this repository,
not in the Automation and not in ChatGPT.

This is not encryption. The approval stays readable -- that is the point of an audit trail. It is
authentication: proof that this exact approval, for this row, this run, these two payloads and this instant,
came from the worker.

TWO PROVENANCE CLOCKS
---------------------
The old timestamp rule said a recommendation may not postdate its Airtable row by more than five minutes.
That was right when the row WAS the finished recommendation. Under the pre-trade architecture the row is a
REQUEST and the recommendation is made later, by the worker, at approval time:

    13:00  Airtable stamps createdTime on a PREFLIGHT_REQUESTED row      <- request provenance
    13:18  the workflow runs; approval_as_of = 13:18                     <- approval provenance
    13:19  the owner sees a BET
    01:00  the archival importer runs

Applying the old rule to the approved record would reject 13:18 for being eighteen minutes after 13:00 --
rejecting the correct behaviour of the new architecture. So the two clocks are separated:

    CANDIDATE created_at   judged against Airtable createdTime, old anti-backfill discipline, unchanged
    approval_as_of         must be at or after createdTime (bar skew), and no later than createdTime plus
                           the request-age window; it is the decision timestamp of the approved record

And the request-expiry control is measured from AIRTABLE'S clock, not the candidate's. A candidate timestamp
is written by the requester and can say anything; `createdTime` is stamped by Airtable's server. An old
request must not be able to refresh itself by claiming a new draft time.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

APPROVAL_SCHEMA = "preflight-approval/1"
SIGNATURE_ALGORITHM = "HMAC-SHA256"
SIGNING_KEY_ENV = "PREFLIGHT_SIGNING_KEY"

# How long a preflight request stays answerable, measured from the AIRTABLE row's server timestamp. Not a
# market-freshness number -- the gates handle that and the approved record carries approval-time prices. This
# bounds the HANDICAP: past half an hour the thesis, grade and probability band come from a packet nobody has
# revisited. Two capture cycles of slack for a delayed Automation, and no more.
MAX_REQUEST_AGE = timedelta(minutes=30)

# Two independent machines writing timestamps. This is the only slack either clock gets.
CLOCK_SKEW = timedelta(minutes=5)

# The fields the signature covers, in the order the canonical message lists them. Adding a field here is a
# breaking change and must come with a new APPROVAL_SCHEMA, or old signatures would silently verify against
# a message that no longer means the same thing.
SIGNED_FIELDS = ("schema", "airtable_record_id", "run_id",
                 "candidate_payload_sha256", "approved_payload_sha256", "approval_as_of")


class ApprovalError(ValueError):
    """An approval that cannot be authenticated. Never a verdict on the bet -- a refusal to consider one."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def signing_key(env=None) -> bytes:
    """The HMAC key, from the environment only.

    Raises rather than returning None: every caller that reaches here is about to authenticate or issue a
    real-money approval, and "no key" must fail closed at the point of use rather than degrade into an
    unsigned path somebody later mistakes for a signed one.
    """
    raw = (env or os.environ).get(SIGNING_KEY_ENV, "")
    raw = raw.strip() if isinstance(raw, str) else ""
    if not raw:
        raise ApprovalError(
            f"{SIGNING_KEY_ENV} is not set. A pre-trade approval is authenticated, not merely self-"
            "consistent, so without the signing key the worker cannot issue one and the importer cannot "
            "verify one. Generate a strong random key once and store it as a repository Actions secret; see "
            "docs/AIRTABLE_BRIDGE.md.")
    if len(raw) < 32:
        raise ApprovalError(
            f"{SIGNING_KEY_ENV} is only {len(raw)} characters. Use at least 32 bytes of randomness; a short "
            "key is a guessable key and this one authorises real money.")
    return raw.encode("utf-8")


def canonical_message(*, airtable_record_id: str, run_id: str, candidate_payload_sha256: str,
                      approved_payload_sha256: str, approval_as_of: str) -> str:
    """The exact bytes that are signed and verified.

    Compact separators and sorted keys, so the message is a function of its VALUES and not of how any
    particular json.dumps was configured on either side.
    """
    body = {
        "schema": APPROVAL_SCHEMA,
        "airtable_record_id": airtable_record_id,
        "run_id": run_id,
        "candidate_payload_sha256": candidate_payload_sha256,
        "approved_payload_sha256": approved_payload_sha256,
        "approval_as_of": approval_as_of,
    }
    missing = [k for k in SIGNED_FIELDS if not body.get(k)]
    if missing:
        raise ApprovalError(f"cannot build an approval message without {missing}")
    return json.dumps(body, sort_keys=True, separators=(",", ":"))


def sign(key: bytes, message: str) -> str:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).hexdigest()


def issue(*, key: bytes, airtable_record_id: str, run_id: str, candidate_payload: str,
          approved_payload: str, approval_as_of: str) -> dict:
    """The signed block the worker embeds in `Preflight Result`."""
    message = canonical_message(
        airtable_record_id=airtable_record_id, run_id=run_id,
        candidate_payload_sha256=sha256_text(candidate_payload),
        approved_payload_sha256=sha256_text(approved_payload),
        approval_as_of=approval_as_of)
    return {
        "approval_schema": APPROVAL_SCHEMA,
        "approval_signature_algorithm": SIGNATURE_ALGORITHM,
        "approval_signature": sign(key, message),
    }


@dataclass(frozen=True)
class VerifiedApproval:
    """An approval this ledger is willing to act on, and the facts it authenticated."""
    airtable_record_id: str
    run_id: str
    candidate_payload_sha256: str
    approved_payload_sha256: str
    approval_as_of: datetime


def verify(result: dict, *, key: bytes, airtable_record_id: str, run_id: str,
           candidate_payload: str, approved_payload: str) -> VerifiedApproval:
    """Authenticate an approval against the ROW'S OWN FACTS.

    The message is rebuilt from what the importer can see for itself -- this row's id, this row's Run ID, the
    hashes it computed from the two payloads in front of it -- and only `approval_as_of` is taken from the
    result, because that is the one fact only the worker knows. So a signature lifted onto another row,
    another run, an edited approved batch or an edited candidate request reconstructs a DIFFERENT message
    and fails, without any of those needing a separate rule.

    They get separate rules anyway, first, because "signature mismatch" is a useless thing to read at 01:00
    when what actually happened is that somebody edited the payload.
    """
    if not isinstance(result, dict):
        raise ApprovalError("`Preflight Result` is not an object")

    schema = result.get("approval_schema")
    if schema != APPROVAL_SCHEMA:
        raise ApprovalError(
            f"unknown approval schema {schema!r}; this importer authenticates {APPROVAL_SCHEMA!r} only. An "
            "approval whose format we do not recognise is not an approval we can check.")
    algorithm = result.get("approval_signature_algorithm")
    if algorithm != SIGNATURE_ALGORITHM:
        raise ApprovalError(f"unknown signature algorithm {algorithm!r}; expected {SIGNATURE_ALGORITHM}")
    signature = result.get("approval_signature")
    if not signature or not isinstance(signature, str):
        raise ApprovalError("the approval carries no signature; an unsigned approval is not an approval")

    claimed_row = result.get("airtable_record_id")
    if not claimed_row:
        # Not optional. An approval that does not say which request it answers can be moved between rows,
        # and a missing field must never be the easy way past a check.
        raise ApprovalError(
            "the approval names no airtable_record_id. An approval is issued for ONE request and must say "
            "which; a missing row id is a failure, not an omission.")
    if claimed_row != airtable_record_id:
        raise ApprovalError(
            f"the approval was issued for row {claimed_row} but is presented on row {airtable_record_id}; "
            "an approval is not transferable between requests")

    claimed_run = result.get("run_id")
    if claimed_run != run_id:
        raise ApprovalError(
            f"the approval names run {claimed_run!r} but this row is run {run_id!r}")

    candidate_sha = sha256_text(candidate_payload)
    approved_sha = sha256_text(approved_payload)
    if result.get("candidate_payload_sha256") != candidate_sha:
        raise ApprovalError(
            "the candidate `Payload` has changed since it was approved; the approval was issued against a "
            "different request")
    if result.get("approved_payload_sha256") != approved_sha:
        raise ApprovalError(
            "`Approved Payload` has been altered since it was approved; it is not what passed the gates and "
            "will not be archived")

    as_of = result.get("approval_as_of")
    if not as_of:
        raise ApprovalError("the approval carries no approval_as_of, so it has no decision timestamp")
    parsed = _ts(as_of)
    if parsed is None:
        raise ApprovalError(f"approval_as_of {as_of!r} is not an ISO-8601 timestamp")

    message = canonical_message(
        airtable_record_id=airtable_record_id, run_id=run_id,
        candidate_payload_sha256=candidate_sha, approved_payload_sha256=approved_sha,
        approval_as_of=as_of)
    if not hmac.compare_digest(sign(key, message), signature):
        raise ApprovalError(
            "the approval signature does not verify. The pre-trade worker did not issue this approval for "
            "this row, and a recommendation is not archived on an unauthenticated one.")

    return VerifiedApproval(airtable_record_id=airtable_record_id, run_id=run_id,
                           candidate_payload_sha256=candidate_sha,
                           approved_payload_sha256=approved_sha, approval_as_of=parsed)


def check_approval_window(approval_as_of: datetime, airtable_created: datetime, *,
                          max_request_age: timedelta = MAX_REQUEST_AGE,
                          skew: timedelta = CLOCK_SKEW) -> None:
    """The APPROVAL clock, judged against Airtable's server clock rather than the candidate's own.

    Two bounds, and neither is the old "may not postdate the row" rule -- which is exactly what an approval
    is supposed to do:

      * an approval cannot predate the request it answers (bar clock skew between two machines);
      * an approval cannot be issued after the request has expired, because the handicap it rests on has
        gone stale even if the market has been re-priced.
    """
    if approval_as_of < airtable_created - skew:
        raise ApprovalError(
            f"approval_as_of {approval_as_of.isoformat()} predates the Airtable request "
            f"({airtable_created.isoformat()}); an approval cannot answer a request that did not exist yet")
    deadline = airtable_created + max_request_age + skew
    if approval_as_of > deadline:
        age = (approval_as_of - airtable_created).total_seconds() / 60.0
        raise ApprovalError(
            f"the request was {age:.1f} min old when it was approved, beyond the "
            f"{max_request_age.total_seconds() / 60:.0f} min window (measured from Airtable's server "
            "timestamp, not the candidate's self-reported one). The market can be re-priced; the handicap "
            "cannot. A fresh request is required.")


def _ts(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
