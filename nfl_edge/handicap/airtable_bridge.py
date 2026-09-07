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
                   READY_FOR_SYNC and the next hour retries. Turning one of these into ERROR would discard a
                   real recommendation because a socket closed.
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

from nfl_edge.handicap import schema as S
from nfl_edge.handicap import store

# ---- the bridge base -------------------------------------------------------------------------------
# Hardcoding ids is deliberate: they are not secrets, they are the address of the one inbox this project
# has, and a typo'd base id in a workflow env var would fail as "no pending rows" -- silently, forever.
AIRTABLE_API = "https://api.airtable.com/v0"
BASE_ID = "appYrRmZ1Ax9sFByP"          # Sports Betting Bridge
TABLE_ID = "tbl6kIANJRv6u8gEp"         # Recommendation Runs

F_RUN_ID, F_SPORT, F_STATUS, F_PAYLOAD, F_NOTES = "Run ID", "Sport", "Status", "Payload", "Notes"

STATUS_TEST_ONLY = "TEST_ONLY"          # connectivity scratch; scheduled polling ignores it entirely
STATUS_READY = "READY_FOR_SYNC"         # ChatGPT is done writing; GitHub may ingest
STATUS_SYNCED = "SYNCED"                # every record durably present on handicap-data AND pushed
STATUS_ERROR = "ERROR"                  # permanent data problem; needs a corrected new row

SPORT_NFL = "NFL"

RECEIPT_KIND = "import_receipts"

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
        formula = f"AND({{{F_SPORT}}}='{_esc(sport)}',{{{F_STATUS}}}='{_esc(STATUS_READY)}')"
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
        items = [{"id": rid, "fields": {F_STATUS: st}} for rid, st in updates.items()]
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
    """The anti-backfill rule, judged against the one timestamp ChatGPT does not control.

    Airtable stamps createdTime server-side. A recommendation that claims to predate its own row by more than
    a day, or that postdates it, or that was written after the game started, is not prospective evidence --
    whatever else it may be.
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


def check_batch(records: list, *, run_id: str, airtable_created: datetime, now: datetime) -> list:
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

        check_timestamps(rec, airtable_created, now)

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
    warnings: list = field(default_factory=list)
    decisions: dict = field(default_factory=dict)       # decision -> count, for the log line

    @property
    def writes_nothing(self) -> bool:
        return not self.to_write and self.receipt is None


def plan_run(row: dict, ledger_root: str, *, now: datetime | None = None,
             base_id: str = BASE_ID, table_id: str = TABLE_ID) -> RunPlan:
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
    records = parse_payload(raw)
    warnings = check_batch(records, run_id=run_id, airtable_created=airtable_created, now=now)

    season, week = records[0]["season"], records[0]["week"]
    plan = RunPlan(airtable_id=airtable_id, run_id=run_id, created_time=created_time, sha=sha,
                   season=season, week=week, warnings=warnings)

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

    plan.receipt = _plan_receipt(plan, ledger_root, records, base_id, table_id, now)
    return plan


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
