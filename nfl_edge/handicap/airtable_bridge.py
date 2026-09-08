"""Airtable -> handicap-data transport for ChatGPT recommendation batches.

ChatGPT can write to Airtable and cannot write to GitHub: the GitHub App exposes write-shaped tools but every
branch/file write returns 403 "Resource not accessible by integration". So Airtable is the inbox and this
module is the postman. It carries a batch from a row in `Recommendation Runs` into the immutable
`handicap-data` ledger and nowhere else.

    ChatGPT -> Airtable row (READY_FOR_SYNC) -> this module -> data/recommendations/... -> git push -> SYNCED

What this module is NOT: a second schema, a second ledger, or a second validator. Every record is checked by
`nfl_edge.handicap.schema.validate_recommendation` and written by `schema.write_record`, exactly as the
manual `scripts/handicap/validate_recommendations.py` path does. The rules that live here are the ones that
only exist because a batch arrived over a wire: is the batch internally coherent, did it already arrive, and
did it arrive when it claims to have been written.

Three failure classes, kept strictly apart, because conflating them is how a transport loses data:

  BridgeError      permanent, in the data. Invalid JSON, a schema-invalid record, a run id that disagrees
                   with its row, a recommendation id already present with different content. The row goes
                   ERROR and a corrected NEW row is the fix. Retrying cannot help.
  TransientError   the wire. 429, 5xx, timeout, unparseable response, a failed push. The row STAYS
                   READY_FOR_SYNC and the next scheduled run retries. Turning one of these into ERROR would
                   discard a real recommendation because a socket closed.
  (neither)        the batch is already durably present and identical. Not an error at all -- this is the
                   heal path for "push succeeded, status update failed", which is a state the system will
                   reach eventually and must survive without human help.

The unit is ONE ROW = ONE HANDICAP RUN = ONE ATOMIC BATCH. If decision #7 of 8 is invalid, none of the 8 are
written. A batch that is partly in the ledger is a batch nobody can score.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from nfl_edge.handicap import approval as APPROVAL
from nfl_edge.handicap import gates as G
from nfl_edge.handicap import schema as S
from nfl_edge.handicap import store

# ---- the bridge base -------------------------------------------------------------------------------
# Hardcoding ids is deliberate: they are not secrets, they are the address of the one inbox this project
# has, and a typo'd base id in a workflow env var would fail as "no pending rows" -- silently, forever.
AIRTABLE_API = "https://api.airtable.com/v0"
BASE_ID = "appYrRmZ1Ax9sFByP"          # Sports Betting Bridge
TABLE_ID = "tbl6kIANJRv6u8gEp"         # Recommendation Runs

F_RUN_ID, F_SPORT, F_STATUS, F_PAYLOAD, F_NOTES = "Run ID", "Sport", "Status", "Payload", "Notes"
# The pre-trade leg's answer, written back onto the requesting row. A separate field from `Payload` so the
# request and the verdict can never be confused for one another, and so the importer's rule -- it writes
# Status and nothing else -- survives untouched.
F_PREFLIGHT_RESULT = "Preflight Result"
# The exact canonical batch the preflight worker APPROVED. `Payload` stays the immutable candidate request;
# this is the machine-approved decision. Three distinguishable stages -- request, approval, ledger record --
# and the importer archives the middle one, not the first.
F_APPROVED_PAYLOAD = "Approved Payload"

STATUS_TEST_ONLY = "TEST_ONLY"          # connectivity scratch; scheduled polling ignores it entirely
STATUS_READY = "READY_FOR_SYNC"         # ChatGPT is done writing; GitHub may ingest
STATUS_SYNCED = "SYNCED"                # every record durably present on handicap-data AND pushed
STATUS_ERROR = "ERROR"                  # permanent data problem; needs a corrected new row

# ---- the pre-trade leg ----------------------------------------------------------------------------
# A SEPARATE transport with a separate cadence, on the same table. The recommendation leg is twelve-hourly
# archival transport and stays exactly that. This leg is event-driven because a quote is fresh for fifteen
# minutes and the owner needs the answer now -- and because polling for it would burn the Airtable free-tier
# allowance the archival leg depends on.
STATUS_PREFLIGHT_REQUESTED = "PREFLIGHT_REQUESTED"   # ChatGPT wants a pre-trade verdict on these candidates
STATUS_PREFLIGHT_APPROVED = "PREFLIGHT_APPROVED"     # every candidate may be surfaced as a BET
STATUS_PREFLIGHT_BLOCKED = "PREFLIGHT_BLOCKED"       # at least one may NOT be surfaced as a BET
STATUS_PREFLIGHT_ERROR = "PREFLIGHT_ERROR"           # the request itself was unusable

# A row that is not PREFLIGHT_APPROVED has not been approved. There is no third state and no default:
# a request that errored, timed out, or was never picked up is not a bet.
PREFLIGHT_STATUSES = (STATUS_PREFLIGHT_REQUESTED, STATUS_PREFLIGHT_APPROVED,
                      STATUS_PREFLIGHT_BLOCKED, STATUS_PREFLIGHT_ERROR)

SPORT_NFL = "NFL"

RECEIPT_KIND = "import_receipts"
GATES_KIND = "decision_gates"

# ---- timestamp integrity ---------------------------------------------------------------------------
# The scientific claim this ledger makes is "this opinion existed before kickoff, at this price". Airtable's
# createdTime is the one timestamp ChatGPT cannot forge, so every payload timestamp is judged against it.
#
#   created_at may sit slightly AFTER createdTime  -- clock skew between two machines. Small tolerance.
#   created_at may sit well BEFORE createdTime     -- the handicap was done, then submitted. Hours, not days.
#
# The backward bound is what actually blocks backfill: without it a row created today could carry a
# recommendation claiming to have been written last month, and nothing in the ledger would contradict it.
CLOCK_SKEW_TOLERANCE = timedelta(minutes=5)
MAX_HANDICAP_LEAD = timedelta(hours=24)


class BridgeError(Exception):
    """Permanent problem with the data. The Airtable row becomes ERROR; retrying will not help."""


class TransientError(Exception):
    """Infrastructure problem. The Airtable row stays READY_FOR_SYNC so the next run retries."""


# ---- token hygiene ---------------------------------------------------------------------------------

def scrub(text, token: str | None) -> str:
    """Remove a token from anything about to be printed, logged or raised.

    Belt and braces. urllib does not echo request headers into HTTPError, but this function is what makes
    that a property of the bridge rather than a property of a dependency we do not control.
    """
    s = "" if text is None else str(text)
    if token:
        s = s.replace(token, "***")
        # A truncated token in an error message is still a token.
        if len(token) > 12:
            s = s.replace(token[:12], "***")
    return s


# ---- Airtable client -------------------------------------------------------------------------------

class AirtableClient:
    """The smallest Airtable client that can do this job, on stdlib only.

    API footprint is a design constraint, not an afterthought: the free tier meters requests per month, so an
    idle poll is exactly ONE request and a successful sync is ONE list plus one PATCH per ten rows.
    `request_count` is exposed so the budget claim in the docs can be tested rather than asserted.
    """

    def __init__(self, token: str, base_id: str = BASE_ID, table_id: str = TABLE_ID, *,
                 opener=None, timeout: float = 30.0, max_attempts: int = 4, sleep=time.sleep):
        if not token:
            raise BridgeError("AIRTABLE_TOKEN is empty; refusing to contact Airtable without credentials")
        self._token = token
        self.base_id, self.table_id = base_id, table_id
        self._opener = opener or urllib.request.urlopen
        self._timeout, self._max_attempts, self._sleep = timeout, max_attempts, sleep
        self.request_count = 0

    @property
    def url(self) -> str:
        return f"{AIRTABLE_API}/{self.base_id}/{self.table_id}"

    def _request(self, method: str, url: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Authorization": f"Bearer {self._token}"}
        if data:
            headers["Content-Type"] = "application/json"
        last = None
        for attempt in range(1, self._max_attempts + 1):
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            self.request_count += 1
            try:
                with self._opener(req, timeout=self._timeout) as r:
                    raw = r.read()
                try:
                    return json.loads(raw)
                except (ValueError, TypeError) as e:
                    # A 200 that is not JSON is Airtable or a proxy misbehaving: transient, not our data.
                    last = TransientError(f"Airtable returned a non-JSON body: {scrub(e, self._token)}")
            except urllib.error.HTTPError as e:
                status = e.code
                detail = scrub(_safe_read(e), self._token)
                if status in (401, 403):
                    # Credentials are a configuration fault. Retrying burns quota and cannot succeed, but it
                    # is NOT a problem with the row -- so it must never mark a row ERROR.
                    raise TransientError(
                        f"Airtable rejected the token (HTTP {status}); check AIRTABLE_TOKEN scopes and that "
                        f"it is granted access to base {self.base_id}: {detail}") from None
                if status == 429 or status >= 500:
                    last = TransientError(f"Airtable HTTP {status}: {detail}")
                    self._sleep(_backoff(attempt, e.headers.get("Retry-After") if e.headers else None))
                    continue
                # 400/404/422 -- a malformed request from us, not a recoverable condition.
                raise TransientError(f"Airtable HTTP {status}: {detail}") from None
            except urllib.error.URLError as e:
                last = TransientError(f"Airtable unreachable: {scrub(e.reason, self._token)}")
            except TimeoutError as e:
                last = TransientError(f"Airtable timed out: {scrub(e, self._token)}")
            except Exception as e:                      # noqa: BLE001 - never leak a token through a traceback
                raise TransientError(f"Airtable request failed: {scrub(e, self._token)}") from None
            if attempt < self._max_attempts:
                self._sleep(_backoff(attempt, None))
        raise last or TransientError("Airtable request failed after retries")

    def list_ready(self, sport: str = SPORT_NFL) -> list[dict]:
        """Pending rows for one sport. One request when there is nothing to do, which is most hours.

        The filter runs server-side so an idle poll transfers no payloads at all, and TEST_ONLY connectivity
        rows are excluded by the Status term rather than by anything we have to remember to do later.
        """
        return self.list_by_status(STATUS_READY, sport)

    def list_by_status(self, status: str, sport: str = SPORT_NFL) -> list[dict]:
        """Rows for one sport in one status, server-side filtered."""
        formula = f"AND({{{F_SPORT}}}='{_esc(sport)}',{{{F_STATUS}}}='{_esc(status)}')"
        params = {"filterByFormula": formula, "pageSize": "100"}
        out, offset = [], None
        while True:
            q = dict(params)
            if offset:
                q["offset"] = offset
            payload = self._request("GET", f"{self.url}?{urllib.parse.urlencode(q)}")
            records = payload.get("records")
            if not isinstance(records, list):
                raise TransientError("Airtable list response has no 'records' array")
            out.extend(records)
            offset = payload.get("offset")
            if not offset:
                return out

    def set_status(self, updates: dict) -> None:
        """Batch status writes, 10 per request -- Airtable's documented maximum.

        Status is the ONLY field the importer ever writes. Run ID, Sport and Payload are source data once the
        row says READY_FOR_SYNC; rewriting them would destroy the provenance the receipt is meant to prove.
        """
        self.write_fields({rid: {F_STATUS: st} for rid, st in updates.items()},
                          allowed={F_STATUS})

    def write_fields(self, updates: dict,
                     *, allowed=frozenset({F_STATUS, F_PREFLIGHT_RESULT, F_APPROVED_PAYLOAD})) -> None:
        """Batch field writes, 10 records per request -- Airtable's documented maximum.

        `allowed` is a whitelist, not documentation. `Run ID`, `Sport` and `Payload` are SOURCE DATA once a
        row has been submitted; rewriting any of them would destroy the provenance the import receipt exists
        to prove. The importer passes `{Status}` and so can only ever write a status; the pre-trade leg
        additionally writes its verdict and the approved batch. Neither can reach `Payload`, which is what
        keeps the candidate REQUEST, the machine APPROVAL and the ledger RECORD three distinguishable
        artifacts rather than one field that quietly became something else.
        """
        for fields in updates.values():
            bad = set(fields) - set(allowed)
            if bad:
                raise BridgeError(
                    f"refusing to write {sorted(bad)} to an Airtable row: only {sorted(allowed)} may be "
                    "written back. The submitted payload is provenance and is never rewritten.")
        items = [{"id": rid, "fields": fields} for rid, fields in updates.items()]
        for i in range(0, len(items), 10):
            self._request("PATCH", self.url, {"records": items[i:i + 10]})


def _safe_read(e) -> str:
    try:
        return e.read().decode("utf-8", "replace")[:400]
    except Exception:                                   # noqa: BLE001
        return ""


def _backoff(attempt: int, retry_after) -> float:
    if retry_after:
        try:
            return min(float(retry_after), 60.0)
        except (TypeError, ValueError):
            pass
    return min(2.0 ** attempt, 30.0)


def _esc(v: str) -> str:
    return str(v).replace("\\", "\\\\").replace("'", "\\'")


# ---- payload parsing and batch coherence -----------------------------------------------------------

def payload_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_payload(records: list) -> str:
    """The exact bytes an approved batch is hashed and transported as.

    One serialisation, used by the worker to write `Approved Payload` and by the importer to re-hash it, so
    the binding is a byte comparison rather than a hopeful re-encoding.
    """
    return json.dumps(records, indent=1, sort_keys=True, default=str)


def parse_payload(text) -> list[dict]:
    """One record or a list of records, matching what the manual validator already accepts.

    A list is what a handicap run actually is, so that is the shape ChatGPT should write; a bare object is
    accepted because refusing it would only ever cost a round trip.
    """
    if not isinstance(text, str) or not text.strip():
        raise BridgeError("Payload field is empty")
    try:
        payload = json.loads(text)
    except (ValueError, TypeError) as e:
        raise BridgeError(f"Payload is not valid JSON: {e}") from None
    records = payload if isinstance(payload, list) else [payload]
    if not records:
        raise BridgeError("Payload contains no records")
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            raise BridgeError(f"payload[{i}] is {type(rec).__name__}, expected a recommendation object")
    return records


def _parse_ts(name: str, value) -> datetime:
    if not value:
        raise BridgeError(f"{name} is required")
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        raise BridgeError(f"{name} is not an ISO-8601 timestamp: {value!r}") from None
    if dt.tzinfo is None:
        raise BridgeError(f"{name} has no timezone: {value!r}; use UTC with an explicit offset")
    return dt.astimezone(timezone.utc)


def check_timestamps(rec: dict, airtable_created: datetime, now: datetime) -> None:
    """The anti-backfill rule for a CANDIDATE REQUEST, judged against the one timestamp ChatGPT cannot write.

    Airtable stamps createdTime server-side. A request that claims to predate its own row by more than a day,
    or that postdates it, or that was written after the game started, is not prospective evidence -- whatever
    else it may be.

    NOT the rule for a machine-approved record. Under the pre-trade architecture the row is a REQUEST and the
    approved recommendation is made later, at approval time, so "may not postdate the row by more than five
    minutes" would reject the architecture working correctly. Approved records go through
    `approval.check_approval_window` and `_check_approved_timestamps` instead, which are stricter about the
    thing that matters: the record must be dated at the SIGNED approval instant, exactly.
    """
    created = _parse_ts("created_at", rec.get("created_at"))
    if created > airtable_created + CLOCK_SKEW_TOLERANCE:
        raise BridgeError(
            f"created_at {created.isoformat()} is after the Airtable row was created "
            f"({airtable_created.isoformat()}); a recommendation cannot be written after it was submitted")
    if created < airtable_created - MAX_HANDICAP_LEAD:
        raise BridgeError(
            f"created_at {created.isoformat()} predates the Airtable row "
            f"({airtable_created.isoformat()}) by more than {MAX_HANDICAP_LEAD}; this ledger does not accept "
            "backfilled recommendations")
    if airtable_created > now + CLOCK_SKEW_TOLERANCE:
        raise BridgeError(f"Airtable createdTime {airtable_created.isoformat()} is in the future")
    kickoff = rec.get("kickoff_utc")
    if kickoff:
        ko = _parse_ts("kickoff_utc", kickoff)
        if created >= ko:
            raise BridgeError(
                f"created_at {created.isoformat()} is at or after kickoff {ko.isoformat()}; a post-kickoff "
                "recommendation is not a prediction")
        if airtable_created >= ko:
            raise BridgeError(
                f"the Airtable row was created at {airtable_created.isoformat()}, at or after kickoff "
                f"{ko.isoformat()}; the decision handoff must be prospective")


def check_batch(records: list, *, run_id: str, airtable_created: datetime, now: datetime,
                approval=None) -> list:
    """Everything that must be true of a BATCH, on top of what the schema says about each record.

    Per-record validity is `schema.validate_recommendation` and is not restated here. What is added is the
    coherence a wire transfer can break: that these records are one run, one slate, distinct, addressable as
    filenames, and recommendations rather than some other record type that happens to carry an id.
    """
    if not run_id:
        raise BridgeError("the Airtable row has no Run ID")
    warnings, seen, slates = [], {}, set()
    for i, rec in enumerate(records):
        label = f"payload[{i}]"
        # Kind first: an execution and a postmortem both carry recommendation_id, so presence of that field
        # is not enough to call something a recommendation.
        for foreign, kind in (("execution_id", "execution"), ("evaluation_id", "evaluation"),
                              ("postmortem_id", "postmortem")):
            if rec.get(foreign):
                raise BridgeError(
                    f"{label} carries {foreign}, so it is an {kind}, not a recommendation. This bridge "
                    "imports recommendation batches only; evaluations are derived by "
                    "scripts/handicap/attach_evaluations.py and never transported.")
        rid = rec.get("recommendation_id")
        if not rid:
            raise BridgeError(f"{label} has no recommendation_id")
        rec.setdefault("schema_version", S.HANDICAP_SCHEMA_VERSION)

        try:
            warns = S.validate_recommendation(rec)
        except S.ValidationError as e:
            raise BridgeError(f"{label} ({rid}): {e}") from None
        warnings.extend(f"{label} ({rid}): {w}" for w in warns)

        if rid in seen:
            raise BridgeError(f"{label}: duplicate recommendation_id {rid!r} (also at payload[{seen[rid]}])")
        seen[rid] = i

        if str(rec.get("handicap_run_id")) != str(run_id):
            raise BridgeError(
                f"{label} ({rid}) has handicap_run_id {rec.get('handicap_run_id')!r} but the Airtable row's "
                f"Run ID is {run_id!r}; they must match exactly so a ledger record can be traced back to the "
                "row that carried it")

        season, week = rec.get("season"), rec.get("week")
        if season is None or week is None:
            raise BridgeError(
                f"{label} ({rid}) is missing season/week; the bridge cannot place a record in the ledger "
                "layout without them")
        if isinstance(season, bool) or not isinstance(season, int) or \
           isinstance(week, bool) or not isinstance(week, int):
            raise BridgeError(f"{label} ({rid}) season/week must be integers, got {season!r}/{week!r}")
        slates.add((season, week))

        # An APPROVED batch is judged by the approval clock (`_check_approved_timestamps`), not by the
        # candidate rule -- the whole point of the new architecture is that the recommendation is made
        # later, by the worker, at approval time. The candidate records in that same row are still put
        # through the rule below; `plan_run` runs this function over both payloads for exactly that reason.
        if approval is None:
            check_timestamps(rec, airtable_created, now)
        elif airtable_created > now + CLOCK_SKEW_TOLERANCE:
            raise BridgeError(f"Airtable createdTime {airtable_created.isoformat()} is in the future")

    if len(slates) > 1:
        raise BridgeError(
            f"batch spans more than one slate: {sorted(slates)}. One Airtable row is one handicap run and a "
            "handicap run covers one season/week.")
    return warnings


# ---- planning: what would be written, and is any of it already there --------------------------------

def _canonical(rec: dict) -> str:
    """The bytes a record compares as. Mirrors how `write_record` serialises, minus reader-added keys."""
    return json.dumps({k: v for k, v in rec.items() if not k.startswith("_")},
                      indent=1, sort_keys=True) + "\n"


def _safe_record_path(root: str, kind: str, season: int, week: int, rid: str) -> str:
    """Resolve a ledger path and prove it stayed inside its week directory.

    `schema._ID_RE` already forbids a slash, so traversal is not reachable today. This check is here so that
    it stays unreachable if that regex is ever loosened -- the id on this path came off the internet.
    """
    if not rid or not S._ID_RE.match(str(rid)):
        # An empty id resolves to "<week>/.json", whose basename still ends in ".json" -- the extension
        # check alone is not enough. Every id that reaches a filesystem path is checked against the schema's
        # own id pattern, because this one came off the internet.
        raise BridgeError(f"{kind} id {rid!r} is empty or has unsafe characters")
    week_root = os.path.abspath(store.week_dir(root, kind, season, week))
    path = os.path.abspath(store.record_path(root, kind, season, week, rid))
    if os.path.dirname(path) != week_root or not os.path.basename(path).endswith(".json"):
        raise BridgeError(f"{kind} id {rid!r} does not resolve to a safe ledger filename")
    return path


@dataclass
class RunPlan:
    """What one Airtable row would do to the ledger, decided before a single byte is written."""
    airtable_id: str
    run_id: str
    created_time: str
    sha: str
    season: int
    week: int
    to_write: list = field(default_factory=list)        # [(path, record)] -- absent from the ledger
    already_present: list = field(default_factory=list)  # [path] -- present and byte-identical
    receipt: tuple | None = None                        # (path, receipt dict) or None if already receipted
    gate_records: list = field(default_factory=list)    # [(path, DecisionGates dict)] for newly written recs
    warnings: list = field(default_factory=list)
    decisions: dict = field(default_factory=dict)       # decision -> count, for the log line
    # Which of the row's two payloads was archived, and the hash binding that let it be.
    payload_source: str = "candidate payload"
    approved_sha: str | None = None

    @property
    def writes_nothing(self) -> bool:
        return not self.to_write and self.receipt is None


def plan_run(row: dict, ledger_root: str, *, now: datetime | None = None,
             base_id: str = BASE_ID, table_id: str = TABLE_ID,
             gate_context: "G.GateContext | None" = None, signing_key=None) -> RunPlan:
    """Validate one row and work out the exact file operations, without performing any of them.

    Planning before writing is what makes a batch atomic: every reason to refuse -- schema, coherence,
    timestamp, conflict -- is discovered while the ledger is still untouched.
    """
    now = now or datetime.now(timezone.utc)
    fields = row.get("fields") or {}
    airtable_id = (row.get("id") or "").strip()
    if not airtable_id:
        raise BridgeError("Airtable row has no record id; it cannot be receipted or status-updated")
    run_id = (fields.get(F_RUN_ID) or "").strip()
    created_time = row.get("createdTime")
    airtable_created = _parse_ts("Airtable createdTime", created_time)

    raw = fields.get(F_PAYLOAD)
    sha = payload_sha(raw if isinstance(raw, str) else json.dumps(raw, sort_keys=True))
    candidate_records = parse_payload(raw)

    # WHICH PAYLOAD IS CANONICAL. `Payload` is the immutable candidate REQUEST. A real RECOMMENDED record is
    # archived from `Approved Payload` -- the exact batch the pre-trade worker approved -- and only after its
    # hash is re-derived here and matched against the hash recorded in `Preflight Result`. Without that, a
    # row could be written straight to READY_FOR_SYNC and walk a bet into the ledger having passed nothing.
    records, source, approved_sha, verified = _canonical_records(
        fields, candidate_records, airtable_id, run_id, airtable_created, signing_key)
    # The CANDIDATE request is still judged by the old anti-backfill discipline -- that clock did not change,
    # and a request that claims to predate its own row by a day is still not prospective evidence. What the
    # approval clock replaces is only the rule about the machine-approved record.
    if verified is not None:
        check_batch(candidate_records, run_id=run_id, airtable_created=airtable_created, now=now)
    warnings = check_batch(records, run_id=run_id, airtable_created=airtable_created, now=now,
                           approval=verified)

    season, week = records[0]["season"], records[0]["week"]
    plan = RunPlan(airtable_id=airtable_id, run_id=run_id, created_time=created_time, sha=sha,
                   season=season, week=week, warnings=warnings,
                   payload_source=source, approved_sha=approved_sha)

    for rec in records:
        plan.decisions[rec.get("decision")] = plan.decisions.get(rec.get("decision"), 0) + 1
        path = _safe_record_path(ledger_root, "recommendations", season, week, rec["recommendation_id"])
        if not os.path.exists(path):
            plan.to_write.append((path, rec))
            continue
        # CASE B / CASE C. The ledger already holds this id; the only question is whether it holds the same
        # opinion. Identical means a previous run got as far as pushing and no further, which is a state the
        # bridge is required to heal rather than escalate.
        try:
            with open(path) as f:
                existing = json.load(f)
        except (OSError, ValueError) as e:
            raise BridgeError(f"existing ledger record {path} is unreadable: {e}") from None
        if _canonical(existing) == _canonical(rec):
            plan.already_present.append(path)
        else:
            raise BridgeError(
                f"CONFLICT: {rec['recommendation_id']} already exists in the ledger with different content "
                f"({os.path.relpath(path, ledger_root)}). Records are immutable and this bridge will not "
                "overwrite one. To revise a decision, submit a NEW row whose records carry `amends` set to "
                "the original recommendation_id.")

    _plan_gates(plan, ledger_root, gate_context, now)
    plan.receipt = _plan_receipt(plan, ledger_root, records, base_id, table_id, now)
    return plan


def _needs_preflight(records: list) -> bool:
    """Does this batch contain a real bet? TEST_ONLY and PASS/WATCHLIST/RESEARCH_ALERT risk no capital."""
    return any(r.get("decision") == S.RECOMMENDED and not r.get("test_only") for r in records or [])


def _canonical_records(fields: dict, candidate_records: list, airtable_id: str, run_id: str,
                      airtable_created: datetime, signing_key) -> tuple:
    """The records this row actually archives, and the AUTHENTICATED proof it is allowed to.

    A batch with no real RECOMMENDED record keeps the simple path: a PASS is scientifically valuable, costs
    nothing, and requiring a pre-trade approval for it would only discourage recording passes.

    A batch WITH one is archived from `Approved Payload`, and only when the approval in `Preflight Result`
    says APPROVED and VERIFIES under the worker's HMAC key against this row's own facts. Hash agreement
    alone is not enough and never was: anyone who can write Airtable can write a payload and a hash of that
    payload, and the two agree perfectly. Forging an approval requires the signing key, which lives only in
    GitHub Actions.

    Anything else -- no approval, a blocked or expired verdict, an edited payload, an approval lifted from
    another row or run, a missing signing key -- is refused. That is what makes "a direct READY_FOR_SYNC row
    cannot bypass preflight" a property of the importer rather than a convention.
    """
    approved_raw = fields.get(F_APPROVED_PAYLOAD)
    result_raw = fields.get(F_PREFLIGHT_RESULT)
    candidate_raw = fields.get(F_PAYLOAD)
    has_approved = isinstance(approved_raw, str) and approved_raw.strip()

    if not _needs_preflight(candidate_records) and not has_approved:
        return candidate_records, "candidate payload (no real recommendation in this batch)", None, None

    if not has_approved:
        raise BridgeError(
            "this row carries a real RECOMMENDED record but no `Approved Payload`. A bet reaches the ledger "
            "only through pre-trade approval: submit it as PREFLIGHT_REQUESTED, and move the row to "
            "READY_FOR_SYNC once it comes back PREFLIGHT_APPROVED. Writing READY_FOR_SYNC directly does not "
            "make a decision approved, it only skips the check.")

    if not isinstance(result_raw, str) or not result_raw.strip():
        raise BridgeError("`Approved Payload` is present but `Preflight Result` is not; there is no "
                          "approval to bind it to")
    try:
        result = json.loads(result_raw)
    except (ValueError, TypeError) as e:
        raise BridgeError(f"`Preflight Result` is not valid JSON: {e}") from None
    if not isinstance(result, dict):
        raise BridgeError("`Preflight Result` is not an object")

    if result.get("verdict") != "APPROVED":
        raise BridgeError(
            f"the preflight verdict on this row is {result.get('verdict')!r}, not APPROVED. A blocked, "
            "expired or errored request can never become a canonical recommendation.")

    if signing_key is None:
        raise BridgeError(
            f"no {APPROVAL.SIGNING_KEY_ENV} available, so this approval cannot be authenticated. A real "
            "recommendation is not archived on an approval we cannot verify; fail closed rather than trust "
            "a self-consistent one.")
    try:
        verified = APPROVAL.verify(
            result, key=signing_key, airtable_record_id=airtable_id, run_id=run_id,
            candidate_payload=candidate_raw if isinstance(candidate_raw, str) else "",
            approved_payload=approved_raw)
        APPROVAL.check_approval_window(verified.approval_as_of, airtable_created)
    except APPROVAL.ApprovalError as e:
        raise BridgeError(str(e)) from None

    records = parse_payload(approved_raw)
    _check_approved_timestamps(records, verified, airtable_created)
    return records, "approved payload (preflight-bound, signature verified)", \
        verified.approved_payload_sha256, verified


def _check_approved_timestamps(records: list, verified, airtable_created: datetime) -> None:
    """The APPROVAL clock on the machine-approved record.

    The old rule -- a recommendation may not postdate its Airtable row by more than five minutes -- is
    deliberately NOT applied here. It was right when the row was the finished recommendation; under the
    pre-trade architecture the row is a request and the recommendation is made later, by the worker, at
    approval time. Applying it would reject the correct behaviour.

    What replaces it is stricter in the way that matters: every approved record must be dated at the SIGNED
    approval instant, exactly. Not near it, not within a tolerance -- the signature covers `approval_as_of`,
    so a record carrying any other `created_at` was not the record that was approved.
    """
    signed = verified.approval_as_of
    for i, rec in enumerate(records):
        created = _parse_ts(f"approved payload[{i}] created_at", rec.get("created_at"))
        if created != signed:
            raise BridgeError(
                f"approved payload[{i}] ({rec.get('recommendation_id')}) is dated {created.isoformat()} but "
                f"the signed approval is for {signed.isoformat()}. Every record in an approved batch carries "
                "the approval timestamp; one that does not is not the record that was approved.")
        kickoff = rec.get("kickoff_utc")
        if kickoff:
            ko = _parse_ts("kickoff_utc", kickoff)
            if signed >= ko:
                raise BridgeError(
                    f"the approval at {signed.isoformat()} is at or after kickoff {ko.isoformat()}; a "
                    "post-kickoff approval is not a prediction")
    if airtable_created is None:
        raise BridgeError("the row carries no Airtable createdTime to judge the approval against")


def _plan_gates(plan: RunPlan, ledger_root: str, gate_context, now: datetime) -> None:
    """Run the real-money gates over the records this batch would newly write.

    Only NEW records are gated. A record already durably in the ledger passed its gates when it was written;
    re-gating it on a replay would test today's market against yesterday's decision and fail for the wrong
    reason -- which would also break the idempotency guarantee that identical replay is harmless.

    A RECOMMENDED record that fails any gate fails the WHOLE BATCH. That is the same atomicity rule the
    schema check already follows, for the same reason: a handicap run that is half in the ledger is a run
    nobody can score, and the missing half looks like decisions that were never made.
    """
    if gate_context is None:
        # No gate context means no situational checks were requested. That is a legitimate mode -- the
        # bridge is still a transport and the schema still fails closed on everything structural -- but a
        # REAL recommendation must not slip through unattended. Test-only records may.
        real = [r for _p, r in plan.to_write
                if r.get("decision") == S.RECOMMENDED and not r.get("test_only")]
        if real:
            raise BridgeError(
                f"{len(real)} RECOMMENDED record(s) in this batch, but no gate context was supplied, so the "
                "decision-time price, transaction costs and portfolio limits were never checked. A real "
                "recommendation is not written unattended without its gates.")
        return

    for _path, rec in plan.to_write:
        report = G.evaluate_gates(rec, gate_context)
        if report.overall == G.FAIL:
            raise BridgeError(
                f"GATE FAILURE for {rec['recommendation_id']}: " + "; ".join(report.blocking_reasons) +
                ". The whole batch is refused -- a partially imported handicap run cannot be scored.")
        if report.overall == G.NOT_APPLICABLE:
            continue
        gpath = _safe_record_path(ledger_root, GATES_KIND, plan.season, plan.week,
                                  S.new_gates_id(rec["recommendation_id"]))
        if os.path.exists(gpath):
            continue                    # gates already recorded for this recommendation; they run once
        plan.gate_records.append((gpath, report.to_record(test_only=bool(rec.get("test_only")), now=now)))


def _plan_receipt(plan: RunPlan, ledger_root: str, records: list, base_id: str, table_id: str,
                  now: datetime) -> tuple | None:
    """Provenance for the transport, kept beside the ledger but never inside a recommendation.

    The recommendation is betting evidence and its schema is not the bridge's to extend. Where a record came
    from is a separate, smaller fact, so it gets a separate, smaller file. If a receipt already exists with
    the same payload hash the row simply arrived twice; a DIFFERENT hash under the same Airtable id means the
    source row was edited after it was synced, which the status lifecycle forbids.
    """
    path = _safe_record_path(ledger_root, RECEIPT_KIND, plan.season, plan.week, plan.airtable_id)
    if os.path.exists(path):
        try:
            with open(path) as f:
                prior = json.load(f)
        except (OSError, ValueError) as e:
            raise BridgeError(f"existing import receipt {path} is unreadable: {e}") from None
        if prior.get("payload_sha256") != plan.sha:
            raise BridgeError(
                f"CONFLICT: Airtable record {plan.airtable_id} was already imported with payload hash "
                f"{prior.get('payload_sha256')} but now presents {plan.sha}. Run ID, Sport and Payload are "
                "immutable once a row is READY_FOR_SYNC; submit a corrected NEW row instead of editing one.")
        return None
    return path, {
        "airtable_base_id": base_id,
        "airtable_table_id": table_id,
        "airtable_record_id": plan.airtable_id,
        "payload_source": plan.payload_source,
        "approved_payload_sha256": plan.approved_sha,
        "airtable_created_time": plan.created_time,
        "run_id": plan.run_id,
        "season": plan.season,
        "week": plan.week,
        "payload_sha256": plan.sha,
        "recommendation_ids": sorted(r["recommendation_id"] for r in records),
        "record_count": len(records),
        "decisions": dict(sorted(plan.decisions.items())),
        "imported_at": now.isoformat(),
        "schema_version": S.HANDICAP_SCHEMA_VERSION,
        "source": "airtable_bridge",
    }


def apply_plan(plan: RunPlan) -> list:
    """Materialise a planned batch, all of it or none of it.

    `write_record` refuses to overwrite, so a path that appeared between plan and apply raises rather than
    clobbers. Anything already written by THIS batch is then removed, because a half-imported handicap run is
    worse than an unimported one: the missing half would look like decisions that were never made.
    """
    written = []
    try:
        for path, rec in plan.to_write:
            S.write_record(path, rec)
            written.append(path)
        for path, gr in plan.gate_records:
            S.write_record(path, gr)
            written.append(path)
        if plan.receipt:
            S.write_record(plan.receipt[0], plan.receipt[1])
            written.append(plan.receipt[0])
    except (S.ValidationError, OSError) as e:
        for path in written:
            try:
                os.remove(path)
            except OSError:
                pass
        raise BridgeError(f"batch write failed and was rolled back: {e}") from None
    return written
