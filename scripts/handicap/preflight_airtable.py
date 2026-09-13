#!/usr/bin/env python3
"""The PRE-TRADE leg: answer PREFLIGHT_REQUESTED rows in Airtable, event-driven and fast.

    AIRTABLE_TOKEN=... PREFLIGHT_SIGNING_KEY=... \
        python3 scripts/handicap/preflight_airtable.py --handicap-root ../ledger

WHY THIS EXISTS SEPARATELY FROM THE IMPORTER
--------------------------------------------
`preflight_candidate.py` is the right control and the wrong interface. ChatGPT is the thing that produces a
candidate, and in its runtime it can write Airtable and read GitHub -- it cannot run a script, dispatch a
workflow, or clone a branch. So "ChatGPT runs preflight_candidate.py" was a documented intention, not a
mechanism, and a control that the recommending interface cannot reach does not protect anything.

    ChatGPT
      -> writes a PREFLIGHT_REQUESTED row (candidates in `Payload`)
      -> opens a `PREFLIGHT NFL` issue, which is the doorbell and carries no data
      -> that workflow checks out main and runs THIS script
      -> it fetches THIS candidate's live market and order book, two GETs, and stores them durably
      -> the row becomes PREFLIGHT_APPROVED or PREFLIGHT_BLOCKED, with the verdict in `Preflight Result`
      -> ChatGPT reads the row
      -> ONLY an APPROVED candidate may be surfaced as a BET
      -> the final recommendation is then submitted READY_FOR_SYNC for normal 12-hour archival transport

WHAT CHANGED, AND WHY
---------------------
On 2026-09-13 this worker took ~101 seconds to start because the workflow checked out the whole `market-data`
branch -- ~17,491 files -- so that the gates could look up ONE ticker in the capture stream. The verdict for
a 17:00:00Z kickoff was written at 17:01:30Z. It was correctly BLOCKED, on a quote that was 17.1 minutes old
because the bulk conductor pass that produced it had itself taken thirteen minutes to publish.

So the live decision path no longer reads the capture stream at all. For every UNIQUE candidate ticker in a
pending batch it fetches the market and the depth-10 order book directly, stamps the real retrieval times,
writes that evidence to the append-only `preflight-evidence` branch, READS IT BACK, and gates against the
stored bytes. The capture stream keeps its job -- immutable history, and the archival replay -- unchanged.

    order of operations, and it is the control:
        collect evidence  ->  persist and publish  ->  read back  ->  gates  ->  approval

An approval cannot be issued before its evidence is durably present, because the approval is computed from
the bytes that were read back off the store.

WHAT IT DECIDES
---------------
Nothing. It calls `preflight.preflight_batch`, which calls `gates.evaluate_gates`, the same function the
importer later replays against the same evidence. This script is transport and instrumentation.

FAIL CLOSED
-----------
A row that errors becomes PREFLIGHT_ERROR, never APPROVED. A row this script cannot reach stays
PREFLIGHT_REQUESTED, which is also not APPROVED. An API failure, an empty book, an unstorable piece of
evidence and an unsignable approval are all errors. There is no state in which silence means yes.

Exit codes: 0 every request answered (approved or blocked -- both are answers), 1 at least one row was
unusable, 2 configuration problem, 3 a transient failure left rows unanswered.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import airtable_bridge as AB    # noqa: E402
from nfl_edge.handicap import approval as APPROVAL     # noqa: E402
from nfl_edge.handicap import evidence_store as ES     # noqa: E402
from nfl_edge.handicap import live_evidence as LE      # noqa: E402
from nfl_edge.handicap import preflight as P           # noqa: E402
from nfl_edge.handicap import risk as RISK             # noqa: E402
from nfl_edge.kalshi import client as KC               # noqa: E402


def log(msg: str) -> None:
    """Identities, counts, timings and verdicts. Never a payload.

    A thesis dumped into a public Actions log publishes the decision before the market resolves it.
    """
    print(msg, flush=True)


class Timer:
    """Wall-clock spans for the Actions summary.

    The incident was a LATENCY incident and nobody could see where the time went without reading raw runner
    logs afterwards. Every phase is measured here so the next slow run explains itself on the summary page.
    """

    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self.spans: dict = {}
        self._open: dict = {}

    def start(self, name):
        self._open[name] = self._clock()

    def stop(self, name):
        t0 = self._open.pop(name, None)
        if t0 is None:
            return None
        self.spans[name] = round(self.spans.get(name, 0.0) + (self._clock() - t0), 3)
        return self.spans[name]

    def add(self, name, seconds):
        self.spans[name] = round(self.spans.get(name, 0.0) + float(seconds), 3)


# ---- live evidence -----------------------------------------------------------------------------------

class LiveEvidenceCollector:
    """Two public GETs per UNIQUE ticker, and nothing else.

    `unique` is not an optimisation detail, it is the contract: a batch that names the same contract twice
    asks the venue once, and both candidates are then gated against the SAME evidence document. Fetching
    twice would give two candidates on one ticker two different prices and make the batch's verdict depend
    on iteration order.

    TEST_ONLY candidates are skipped, and that is a safety property rather than a shortcut. A TEST_ONLY probe
    names a ticker that deliberately does not exist, so fetching it would turn the end-to-end connectivity
    check into a 404 and answer the row ERROR instead of the honest BLOCKED. It risks no capital, the
    situational gates already do not apply to it, and it can never reach an approved state -- so there is
    nothing for evidence to protect.
    """

    def __init__(self, client=None, *, depth: int = LE.DEFAULT_BOOK_DEPTH):
        self.client = client or KC.KalshiClient()
        self.depth = depth
        self.tickers_fetched = 0
        self.api_requests = 0

    def collect(self, candidates: list, *, airtable_record_id: str, run_id: str,
                workflow_run_id: str = "", evidence_run_id: str = "") -> list:
        seen, docs = set(), []
        for c in candidates or []:
            if (c or {}).get("test_only"):
                continue
            ticker = (c or {}).get("market_ticker")
            if not ticker or ticker in seen:
                continue
            seen.add(ticker)
            docs.append(LE.collect(
                self.client, ticker, side=(c.get("side") or "YES"), depth=self.depth,
                airtable_record_id=airtable_record_id, run_id=run_id,
                workflow_run_id=workflow_run_id, evidence_run_id=evidence_run_id,
                kickoff_utc=c.get("kickoff_utc")))
            self.tickers_fetched += 1
        self.api_requests = getattr(getattr(self.client, "stats", None), "requests", 0)
        return docs


def _evidence_run_id(now: datetime) -> str:
    return now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _season_week(candidates: list) -> tuple:
    """Where the evidence files live. Taken from the batch, which the schema requires to carry both."""
    for c in candidates or []:
        season, week = (c or {}).get("season"), (c or {}).get("week")
        if season is not None and week is not None:
            return season, week
    return "unknown", "unknown"


def _assert_evidence_predates(evidence: dict | None, decision_at: datetime) -> None:
    """Prove the fetch-then-stamp ordering actually held, rather than assuming it.

    Every resolver in this system treats evidence dated after the decision as INVISIBLE -- it is information
    the decision did not have. That rule is correct, and it means an inverted clock does not produce a wrong
    answer, it produces a UNIVERSALLY BLOCKED one, whose stated reason ("retrieved after the approval
    instant") reads like a market problem rather than the code defect it is.

    So the ordering is checked here and a violation is an ERROR. It cannot happen when the clock is a real
    wall clock read after the fetch; it can happen if someone pins `now` in a test, or reorders these two
    statements again, and both of those should be loud.
    """
    for doc in (evidence or {}).get("documents") or []:
        for part in ("market", "orderbook"):
            raw = ((doc.get(part) or {}).get("retrieved_at"))
            at = LE._iso(raw)
            if at is not None and at > decision_at:
                raise LE.EvidenceError(
                    f"the {part} evidence for {doc.get('market_ticker')} is stamped {at.isoformat()}, AFTER "
                    f"the decision instant {decision_at.isoformat()}. Evidence cannot postdate the decision "
                    "it informed; the decision instant is taken after the fetch, so this is a clock or an "
                    "ordering fault, not a verdict about the market.")


def gather_evidence(collector, store, candidates: list, *, airtable_record_id: str, run_id: str,
                    workflow_run_id: str, at: datetime, timer: Timer | None = None) -> dict:
    """Fetch, store, publish and READ BACK this batch's market evidence. Raises rather than degrading.

    Returns everything the gates and the approval need: the documents as they came off the store, the
    per-document paths and hashes, the storage reference, and the manifest hash the approval signs.
    """
    timer = timer or Timer()
    # `at` names the evidence run directory only -- it is a label, never a decision clock. The decision
    # instant is taken by the caller AFTER this returns.
    evidence_run_id = _evidence_run_id(at)
    season, week = _season_week(candidates)

    timer.start("market_evidence")
    try:
        docs = collector.collect(candidates, airtable_record_id=airtable_record_id, run_id=run_id,
                                 workflow_run_id=workflow_run_id, evidence_run_id=evidence_run_id)
    finally:
        # Stopped even on a failure, so the summary still says where the time went on the run you most
        # want to read afterwards.
        timer.stop("market_evidence")
    if not docs:
        real = [c for c in candidates or [] if not (c or {}).get("test_only")]
        if real:
            raise LE.EvidenceError(
                "no live market evidence could be fetched for a batch that contains real candidates; a "
                "candidate with nothing to price is not approved")
        # Every candidate is a TEST_ONLY probe: nothing is fetched, nothing is published, and nothing can be
        # approved. An empty manifest is the honest record of that, not a gap to be filled in later.
        return {"evidence_run_id": evidence_run_id, "documents": [], "entries": [],
                "storage": getattr(store, "storage", "none"), "commit": None, "manifest_sha256": None}

    timer.start("evidence_persist")
    to_store = []
    for doc in docs:
        text = LE.canonical_json(doc)
        rel = LE.evidence_relpath(season=season, week=week, airtable_record_id=airtable_record_id,
                                  ticker=doc["market_ticker"],
                                  retrieved_at=doc["market"]["retrieved_at"])
        to_store.append((rel, text, LE.sha256_text(text)))
    try:
        stored = ES.store_batch(
            store, to_store,
            message=f"preflight evidence {evidence_run_id} ({len(to_store)} ticker(s))")
    finally:
        timer.stop("evidence_persist")

    # THE GATES READ WHAT IS STORED. Re-parsing the read-back bytes, rather than reusing the documents in
    # memory, is what makes "approval rests on durable evidence" literal instead of aspirational.
    replayed = [LE.load_document(e["text"], expected_sha256=e["sha256"]) for e in stored["entries"]]
    entries = [{"path": e["path"], "sha256": e["sha256"]} for e in stored["entries"]]
    return {
        "evidence_run_id": evidence_run_id,
        "documents": replayed,
        "entries": entries,
        "storage": stored["storage"],
        "commit": stored["commit"],
        "manifest_sha256": LE.manifest_sha256(entries, storage=stored["storage"],
                                              commit=stored["commit"]),
    }


# ---- the answer --------------------------------------------------------------------------------------

def _summary(results: list, *, run_id: str, airtable_id: str, candidate_payload: str,
             approved_payload: str | None, approval_as_of: datetime, answered_at: datetime,
             evidence: dict | None = None) -> dict:
    """What gets written back to Airtable. Small, readable, and legible to a human in a hurry.

    The hashes are the load-bearing part. `approved_payload_sha256` is what the importer re-derives from
    `Approved Payload` before archiving it, so an approved batch cannot be edited between approval and
    import without the bridge noticing. `evidence` names the exact market documents the verdict was computed
    from, by path, by content hash and by the commit they were published in, so the delayed importer can
    re-read them and reach the verdict again on its own.
    """
    approved = bool(results) and all(r.may_be_shown_as_a_bet for r in results)
    expired = any(r.verdict == P.EXPIRED for r in results)
    ev = evidence or {}
    return {
        "schema": "preflight-result/1",
        "run_id": run_id,
        "airtable_record_id": airtable_id,
        # TWO CLOCKS, DELIBERATELY DIFFERENT. `approval_as_of` is the decision -- stamped after the
        # evidence was fetched and stored, and the timestamp every gate ran at and every approved record
        # carries. `answered_at` is when this answer was written, and is observability only.
        "answered_at": answered_at.isoformat(),
        "approval_as_of": approval_as_of.isoformat(),
        "verdict": "APPROVED" if approved else ("EXPIRED" if expired else "BLOCKED"),
        "candidate_payload_sha256": AB.payload_sha(candidate_payload),
        "approved_payload_sha256": AB.payload_sha(approved_payload) if approved_payload else None,
        "n_candidates": len(results),
        "n_approved": sum(1 for r in results if r.may_be_shown_as_a_bet),
        "evidence": {
            "source": "kalshi public read-only GET /markets/{ticker} and /markets/{ticker}/orderbook",
            "evidence_run_id": ev.get("evidence_run_id"),
            "storage": ev.get("storage"),
            "commit": ev.get("commit"),
            "manifest_sha256": ev.get("manifest_sha256"),
            "documents": ev.get("entries") or [],
        } if ev else None,
        "candidates": [{
            "recommendation_id": r.candidate_id,
            "verdict": r.verdict,
            "may_be_shown_as_a_bet": r.may_be_shown_as_a_bet,
            "surface_as": r.surface_as,
            "candidate_created_at": r.candidate_created_at,
            "approval_as_of": r.as_of,
            "request_age_minutes": r.request_age_minutes,
            "request_age_basis": r.request_age_basis,
            "proposed_stake": r.proposed_stake,
            "approved_stake": r.approved_stake,
            "blocking_reasons": r.blocking_reasons,
            "warnings": r.warnings,
            "executable_price": (r.decision_quote or {}).get("executable_price"),
            "full_position_vwap": (r.depth or {}).get("vwap"),
            "worst_fill_price": (r.depth or {}).get("worst_price"),
            "net_ev_dollars": (r.net_ev or {}).get("net_ev_dollars"),
            "conservative_net_ev_dollars": (r.net_ev or {}).get("conservative_net_ev_dollars"),
            # The three latency facts the incident was about, recorded per candidate: how close to kickoff
            # this answer landed, and how old the two pieces of market evidence were when it did.
            "minutes_to_kickoff_at_approval": (
                ((r.gates or {}).get("decision_before_kickoff") or {}).get("evidence")
                or {}).get("minutes_to_kickoff"),
            "quote_age_minutes": (r.decision_quote or {}).get("age_minutes"),
            "book_age_minutes": (r.depth or {}).get("book_age_minutes"),
            "gates": {k: v.get("status") for k, v in (r.gates or {}).items()},
        } for r in results],
        "outstanding_exposure": {
            "total": ((results[0].outstanding or {}).get("total") if results else None),
            "by_correlation_group": ((results[0].outstanding or {}).get("by_correlation_group")
                                     if results else None),
        },
        "note": ("Only candidates with may_be_shown_as_a_bet=true may be surfaced as a BET or a final "
                 "RECOMMENDED instruction, and only at approved_stake, and only from Approved Payload. "
                 "Move the row to READY_FOR_SYNC to archive it; the importer re-hashes Approved Payload "
                 "against approved_payload_sha256, and re-reads the evidence documents named above. This "
                 "answer places nothing."),
    }


def answer_row(row: dict, *, ledger_root: str, clock, market_data_root: str | None = None,
               fee_observations_root: str | None = None, evidence_collector=None, evidence_store=None,
               workflow_run_id: str = "", signing_key=None, timer: Timer | None = None) -> tuple:
    """Preflight one Airtable row. Returns (status, result body, approved payload or None).

    THREE TIMESTAMPS, AND THE ORDER THEY ARE TAKEN IN IS LOAD-BEARING
    ----------------------------------------------------------------
    `clock()` is read twice, and never before the evidence exists:

        evidence retrieval   stamped by the client when each response actually arrived
        DECISION INSTANT     read AFTER the evidence is fetched, persisted and read back, immediately
                             before the gates. This is `approval_as_of` and the `created_at` of every
                             approved record.
        answered_at          read after the gates, for observability only. Nothing is judged at it.

    Stamping the decision BEFORE the fetch -- which is what this did until it was corrected -- inverts the
    one rule the resolvers are built on: evidence dated after the decision is INVISIBLE, because it is
    information the decision did not have. A quote retrieved a second after a decision instant that was
    stamped a second before it is not fresh evidence arriving promptly; it is evidence from the future, and
    `EvidenceQuoteIndex.confirmation` correctly refuses it. Every live preflight would have blocked on
    "retrieved after the approval instant" -- fail-closed, and useless.

    So the decision instant is taken last, and `_assert_evidence_predates` then proves the ordering held
    rather than assuming it: a clock that went backwards between the fetch and the stamp is an ERROR, not a
    verdict.

    It is stamped PER ROW, because a batch of requests can take meaningful time to work through and the last
    one must not be dated as though it were the first.

    The expiry clock is Airtable's SERVER `createdTime`, not the candidate's self-reported `created_at`: the
    requester writes one of those and not the other.

    TWO EVIDENCE PATHS, ONE SET OF GATES. With an `evidence_collector` this is the LIVE pre-trade path: the
    venue is asked about this candidate's contract directly and the answer is stored durably before it is
    gated. With only a `market_data_root` it is the ARCHIVAL path -- the capture stream, the same evidence
    the importer replays -- which is what `preflight_candidate.py` and the replay CLI use. `main()` always
    wires the live path; there is no flag that turns it off.
    """
    timer = timer or Timer()
    fields = row.get("fields") or {}
    airtable_id = (row.get("id") or "").strip()
    run_id = (fields.get(AB.F_RUN_ID) or "").strip()
    candidate_payload = fields.get(AB.F_PAYLOAD)
    candidates = AB.parse_payload(candidate_payload)
    request_created = AB._parse_ts("Airtable createdTime", row.get("createdTime"))

    evidence, capture_index, book_index = None, None, None
    if evidence_collector is not None:
        if evidence_store is None:
            raise ES.EvidenceStoreError(
                "a live preflight collector was supplied with no evidence store. Evidence that is not "
                "stored dies with the runner, and an approval whose evidence cannot be re-read later is not "
                "issued at all.")
        # FETCH, PERSIST AND READ BACK FIRST. No clock has been read yet: the decision instant cannot be
        # stamped before the evidence it is about exists, or the evidence dates after the decision and the
        # resolvers correctly refuse to see it.
        evidence = gather_evidence(evidence_collector, evidence_store, candidates,
                                   airtable_record_id=airtable_id, run_id=run_id,
                                   workflow_run_id=workflow_run_id, at=clock(), timer=timer)
        capture_index = LE.EvidenceQuoteIndex(evidence["documents"])
        book_index = LE.EvidenceBookIndex(evidence["documents"])
        for doc in evidence["documents"]:
            refusal = LE.tradable_refusal(doc)
            if refusal:
                # Recorded, not raised: a settled or closed market is a real answer about the market, and
                # the quote resolver already refuses a non-tradable status. Saying so here puts the reason
                # in the log next to the ticker it belongs to.
                log(f"   not tradable: {refusal}")
    elif market_data_root is None:
        raise ValueError(
            "answer_row needs either a live evidence collector (the pre-trade path) or a market-data root "
            "(the archival replay path). Gating a real-money candidate against neither is not a mode.")

    # THE DECISION INSTANT. Taken here, with the evidence already durable, and used for nothing else: it is
    # `approval_as_of`, it is the `created_at` of every record this approves, and it is what every
    # time-sensitive gate is evaluated at.
    decision_at = clock()
    _assert_evidence_predates(evidence, decision_at)

    # The ledger read and the gate evaluation are timed apart: they fail for different reasons and are slow
    # for different reasons, and one number covering both hides whichever was actually the problem.
    timer.start("gates")
    try:
        results = P.preflight_batch(
            candidates, market_data_root=market_data_root, ledger_root=ledger_root, root=ROOT,
            approval_as_of=decision_at, request_id=airtable_id, request_created_at=request_created,
            capture_index=capture_index, book_index=book_index,
            fee_observations_root=fee_observations_root or market_data_root,
            phase=timer.add)
    finally:
        timer.stop("gates")
        # `gates` was measured around the whole call, the ledger read included. Subtract it so the two rows
        # add up to what actually happened rather than double-counting.
        if "ledger_load" in timer.spans:
            timer.spans["gates"] = round(max(0.0, timer.spans["gates"] - timer.spans["ledger_load"]), 3)

    approved_records = [r.approved_record for r in results if r.may_be_shown_as_a_bet]
    fully_approved = bool(results) and len(approved_records) == len(results)
    approved_payload = AB.canonical_payload(approved_records) if fully_approved else None

    # ANSWERED_AT is a separate, later read. It is observability -- how long the owner waited -- and is
    # never a clock anything is judged at. Conflating the two is what produced the ordering bug.
    body = _summary(results, run_id=run_id, airtable_id=airtable_id,
                    candidate_payload=candidate_payload if isinstance(candidate_payload, str) else "",
                    approved_payload=approved_payload, approval_as_of=decision_at,
                    answered_at=clock(), evidence=evidence)

    if approved_payload is not None:
        # SIGN it. A hash the approval carries about itself proves only that the approval is self-consistent;
        # anyone who can write Airtable can write both halves. The signature is what makes the importer's
        # refusal to archive an unapproved bet a property rather than an etiquette -- and it now covers the
        # evidence manifest too, so the approval names the exact market documents it was computed from.
        if signing_key is None:
            raise APPROVAL.ApprovalError(
                f"{APPROVAL.SIGNING_KEY_ENV} is not available, so this approval cannot be signed. An "
                "unsigned approval would be refused by the importer, so it is not issued at all.")
        if not (evidence or {}).get("manifest_sha256"):
            raise ES.EvidenceStoreError(
                "no durable evidence manifest for this batch, so no approval is issued. A real-money "
                "approval names the market evidence it rests on; one that cannot is refused.")
        body.update(APPROVAL.issue(
            key=signing_key, airtable_record_id=airtable_id, run_id=run_id,
            candidate_payload=candidate_payload if isinstance(candidate_payload, str) else "",
            approved_payload=approved_payload, approval_as_of=decision_at.isoformat(),
            evidence_manifest_sha256=evidence["manifest_sha256"]))

    status = (AB.STATUS_PREFLIGHT_APPROVED if body["verdict"] == "APPROVED"
              else AB.STATUS_PREFLIGHT_BLOCKED)
    return status, body, approved_payload


# ---- observability -----------------------------------------------------------------------------------

def _candidate_timing(body: dict) -> list:
    """Per-candidate latency facts for the summary. Identities and numbers only -- never a ticker.

    The repository is public. A recommendation id is opaque; a ticker, a price or a stake is the bet.
    """
    return [{
        "recommendation_id": c.get("recommendation_id"),
        "verdict": c.get("verdict"),
        "minutes_to_kickoff_at_approval": c.get("minutes_to_kickoff_at_approval"),
        "quote_age_minutes": c.get("quote_age_minutes"),
        "book_age_minutes": c.get("book_age_minutes"),
    } for c in body.get("candidates") or []]


def render_summary(observations: dict) -> str:
    """The Actions job summary: where the time went, and how close to kickoff the answer landed.

    Deliberately contentless about the BET. No ticker, no price, no stake, no thesis, no payload -- this page
    is public, and a latency dashboard that leaks the position is worse than no dashboard.
    """
    o = observations
    lines = ["## NFL pre-trade preflight", "",
             f"* trigger: `{o.get('trigger') or 'unknown'}`",
             f"* requests answered: {o.get('rows_answered', 0)} "
             f"({o.get('candidates', 0)} candidate(s), {o.get('tickers', 0)} unique ticker(s))",
             f"* Kalshi API requests: {o.get('api_requests', 0)}",
             f"* evidence: `{o.get('evidence_storage') or 'n/a'}` commit "
             f"`{(o.get('evidence_commit') or 'n/a')[:12]}`", "",
             "| phase | seconds |", "| --- | ---: |"]
    for label, key in (("load code + start python", "code_load"),
                       ("read Airtable", "airtable_read"),
                       ("obtain live market evidence", "market_evidence"),
                       ("persist evidence durably", "evidence_persist"),
                       ("load ledger (outstanding exposure)", "ledger_load"),
                       ("run gates", "gates"),
                       ("write verdict to Airtable", "airtable_write"),
                       ("TOTAL request-to-verdict", "request_to_verdict"),
                       ("TOTAL worker wall clock", "worker_total")):
        v = (o.get("spans") or {}).get(key)
        lines.append(f"| {label} | {'-' if v is None else f'{v:.2f}'} |")
    rows = o.get("per_candidate") or []
    if rows:
        lines += ["", "| candidate | verdict | min to kickoff | quote age (min) | book age (min) |",
                  "| --- | --- | ---: | ---: | ---: |"]
        for r in rows:
            def n(x):
                return "-" if x is None else f"{float(x):.2f}"
            lines.append(f"| `{r.get('recommendation_id')}` | {r.get('verdict')} | "
                         f"{n(r.get('minutes_to_kickoff_at_approval'))} | "
                         f"{n(r.get('quote_age_minutes'))} | {n(r.get('book_age_minutes'))} |")
    lines += ["", "_No ticker, price, stake or thesis appears on this page: the Airtable row is the only "
              "place the verdict and the candidate live._"]
    return "\n".join(lines) + "\n"


def write_summary(path: str | None, observations: dict) -> None:
    if not path:
        return
    try:
        with open(path, "a") as f:
            f.write(render_summary(observations))
    except OSError as e:
        log(f"::warning::could not write the run summary: {e}")


# ---- the run -----------------------------------------------------------------------------------------

def run(client, *, ledger_root: str, market_data_root: str | None = None,
        fee_observations_root: str | None = None, sport: str = AB.SPORT_NFL,
        now: datetime | None = None, update_status: bool = True, signing_key=None, clock=None,
        evidence_collector=None, evidence_store=None, workflow_run_id: str = "",
        trigger: str = "", summary_path: str | None = None, timer: Timer | None = None,
        started_at: float | None = None) -> int:
    # `clock` supplies the PER-ROW approval instant. Stamping once at workflow start would date the last row
    # in a batch as though it had been evaluated at the same moment as the first, and with a fifteen-minute
    # quote window that difference is not cosmetic. `now` pins it for tests.
    clock = clock or (lambda: now or datetime.now(timezone.utc))
    timer = timer or Timer()
    t_worker0 = time.monotonic() if started_at is None else started_at
    obs = {"trigger": trigger, "spans": timer.spans, "rows_answered": 0, "candidates": 0,
           "tickers": 0, "api_requests": 0, "per_candidate": []}

    timer.start("airtable_read")
    try:
        rows = client.list_by_status(AB.STATUS_PREFLIGHT_REQUESTED, sport=sport)
    except AB.TransientError as e:
        timer.stop("airtable_read")
        log(f"TRANSIENT: could not read Airtable: {e}")
        log("rows left PREFLIGHT_REQUESTED; an unanswered request is not an approval")
        timer.add("worker_total", time.monotonic() - t_worker0)
        write_summary(summary_path, obs)
        return 3
    timer.stop("airtable_read")

    log(f"{len(rows)} row(s) with Status={AB.STATUS_PREFLIGHT_REQUESTED} Sport={sport}")
    if not rows:
        log("nothing to preflight")
        timer.add("worker_total", time.monotonic() - t_worker0)
        write_summary(summary_path, obs)
        return 0

    updates, had_error = {}, False
    request_to_verdict = None
    for row in rows:
        rid = (row.get("id") or "").strip()
        if not rid:
            log("ERROR  <no record id>: Airtable row has no record id; cannot be answered")
            had_error = True
            continue
        try:
            # NO CLOCK IS READ HERE. `answer_row` takes the decision instant itself, after the evidence is
            # fetched and durable -- see its docstring for why stamping it out here was a defect.
            status, body, approved_payload = answer_row(
                row, ledger_root=ledger_root, clock=clock, market_data_root=market_data_root,
                fee_observations_root=fee_observations_root, evidence_collector=evidence_collector,
                evidence_store=evidence_store, workflow_run_id=workflow_run_id,
                signing_key=signing_key, timer=timer)
        except (AB.BridgeError, ValueError, RISK.RiskPolicyError, APPROVAL.ApprovalError,
                LE.EvidenceError, ES.EvidenceStoreError, KC.KalshiError) as e:
            # An unusable request is an ERROR, never an approval. The reason goes back to the row so
            # ChatGPT can see what to fix without anyone reading a workflow log.
            log(f"ERROR  {rid}: {AB.scrub(e, '')}")
            had_error = True
            updates[rid] = {
                AB.F_STATUS: AB.STATUS_PREFLIGHT_ERROR,
                AB.F_PREFLIGHT_RESULT: json.dumps(
                    {"schema": "preflight-result/1", "verdict": "ERROR",
                     "answered_at": clock().isoformat(), "error": str(e)[:2000],
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
        fields = {AB.F_STATUS: status,
                  AB.F_PREFLIGHT_RESULT: json.dumps(body, indent=1, default=str)}
        if approved_payload is not None:
            # The exact canonical batch this approval authorises. The candidate `Payload` is never touched:
            # request, approval and ledger record stay three distinguishable artifacts.
            fields[AB.F_APPROVED_PAYLOAD] = approved_payload
        updates[rid] = fields

        ev = body.get("evidence") or {}
        obs["rows_answered"] += 1
        obs["candidates"] += body["n_candidates"]
        obs["tickers"] += len(ev.get("documents") or [])
        obs["evidence_storage"] = ev.get("storage") or obs.get("evidence_storage")
        obs["evidence_commit"] = ev.get("commit") or obs.get("evidence_commit")
        obs["per_candidate"].extend(_candidate_timing(body))
        # REQUEST-TO-VERDICT is measured from Airtable's own server timestamp, which is when the owner
        # actually asked -- not from when the runner happened to boot. It is the number the fifteen-minute
        # freshness window and the kickoff deadline are both spent against.
        req_at = AB._parse_ts("Airtable createdTime", row.get("createdTime"))
        answered_at = AB._parse_ts("answered_at", body["answered_at"])
        if req_at is not None and answered_at is not None:
            span = (answered_at - req_at).total_seconds()
            request_to_verdict = span if request_to_verdict is None else max(request_to_verdict, span)

    obs["api_requests"] = getattr(evidence_collector, "api_requests", 0)
    if request_to_verdict is not None:
        timer.add("request_to_verdict", request_to_verdict)

    if not update_status:
        log(f"--no-write: NOT updating Airtable; would have answered {len(updates)} row(s)")
        timer.add("worker_total", time.monotonic() - t_worker0)
        write_summary(summary_path, obs)
        return 1 if had_error else 0

    timer.start("airtable_write")
    try:
        client.write_fields(updates)
    except AB.TransientError as e:
        timer.stop("airtable_write")
        log(f"TRANSIENT: verdicts computed but could not be written back: {e}")
        log("rows stay PREFLIGHT_REQUESTED; the next dispatch recomputes them")
        timer.add("worker_total", time.monotonic() - t_worker0)
        write_summary(summary_path, obs)
        return 3
    timer.stop("airtable_write")

    log(f"answered {len(updates)} row(s); total Airtable requests this run: {client.request_count}")
    timer.add("worker_total", time.monotonic() - t_worker0)
    write_summary(summary_path, obs)
    return 1 if had_error else 0


def main(argv=None) -> int:
    t0 = time.monotonic()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--handicap-root", required=True,
                    help="checkout of handicap-data; OUTSTANDING portfolio exposure is read from it")
    ap.add_argument("--fee-observations", default=None,
                    help="a SPARSE checkout of market-data holding data/kalshi/fees/ only. The live path "
                         "reads fee observations and nothing else from that branch; it never reads the "
                         "capture stream, which is what used to cost ~100s of checkout per run.")
    ap.add_argument("--evidence-branch", default=ES.EVIDENCE_BRANCH,
                    help="append-only branch the live market evidence is published to")
    ap.add_argument("--evidence-repo", default=ROOT,
                    help="git repository the evidence worktree is created from")
    ap.add_argument("--evidence-dir", default=None,
                    help="store evidence in this directory instead of on a branch. For an operator running "
                         "by hand; a directory is not a commit and the result says so.")
    ap.add_argument("--no-evidence-push", action="store_true",
                    help="commit the evidence but do not push it (rehearsal only)")
    ap.add_argument("--book-depth", type=int, default=LE.DEFAULT_BOOK_DEPTH)
    ap.add_argument("--base-id", default=AB.BASE_ID)
    ap.add_argument("--table-id", default=AB.TABLE_ID)
    ap.add_argument("--sport", default=AB.SPORT_NFL)
    ap.add_argument("--trigger", default=os.environ.get("PREFLIGHT_TRIGGER", ""),
                    help="which event started this run; reported on the Actions summary")
    ap.add_argument("--summary-file", default=os.environ.get("GITHUB_STEP_SUMMARY") or None)
    ap.add_argument("--started-at-epoch", type=float, default=None,
                    help="when the JOB started, so 'time to load code' is measurable from inside")
    ap.add_argument("--no-write", action="store_true",
                    help="compute verdicts and print them; change no Airtable row")
    # Kept only so the old invocation fails with an explanation instead of an argparse error. Handing the
    # live path a full market-data checkout is the thing this rebuild removed; silently accepting it would
    # let the hundred-second checkout creep back in unnoticed.
    ap.add_argument("--market-data", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.market_data:
        log("--market-data is no longer accepted by the live pre-trade path. Preflight fetches this "
            "candidate's market and order book directly (two public GETs) instead of reading the capture "
            "stream, which is what cost ~100s of checkout per run. Pass --fee-observations with a SPARSE "
            "checkout of data/kalshi/fees/ if fee-observation evidence is needed; use "
            "scripts/handicap/replay_preflight_evidence.py for the archival replay.")
        return 2

    timer = Timer()
    if a.started_at_epoch:
        timer.add("code_load", max(0.0, time.time() - float(a.started_at_epoch)))

    token = os.environ.get("AIRTABLE_TOKEN", "").strip()
    if not token:
        log("AIRTABLE_TOKEN is not set. See docs/AIRTABLE_BRIDGE.md.")
        return 2
    try:
        key = APPROVAL.signing_key()
    except APPROVAL.ApprovalError as e:
        # Fail here, before reading Airtable. An approval this worker cannot sign is one the importer will
        # refuse, so issuing it would only produce a row that looks approved and can never be archived.
        log(str(e))
        return 2
    if not os.path.isdir(a.handicap_root):
        log(f"--handicap-root {a.handicap_root} is not a directory. Preflight reads OUTSTANDING exposure "
            "from the committed ledger; caps are cumulative and cannot be checked against a book we cannot "
            "see, so nothing is answered.")
        return 2
    if a.fee_observations and not os.path.isdir(a.fee_observations):
        log(f"--fee-observations {a.fee_observations} is not a directory.")
        return 2

    # THE LIVE PATH IS NOT OPTIONAL. There is no switch here that falls back to the capture stream: a
    # pre-trade verdict is computed from evidence fetched seconds earlier and stored durably, or it is not
    # computed. `--evidence-dir` changes WHERE that evidence is kept, never whether it exists.
    try:
        store = (ES.DirectoryEvidenceStore(a.evidence_dir) if a.evidence_dir
                 else ES.GitBranchEvidenceStore(a.evidence_repo, branch=a.evidence_branch,
                                                push=not a.no_evidence_push))
    except ES.EvidenceStoreError as e:
        log(f"cannot prepare the preflight evidence store: {e}")
        return 2
    collector = LiveEvidenceCollector(depth=a.book_depth)

    client = AB.AirtableClient(token, a.base_id, a.table_id)
    try:
        return run(client, ledger_root=os.path.abspath(a.handicap_root),
                   fee_observations_root=os.path.abspath(a.fee_observations) if a.fee_observations else None,
                   sport=a.sport, update_status=not a.no_write, signing_key=key,
                   evidence_collector=collector, evidence_store=store,
                   workflow_run_id=os.environ.get("GITHUB_RUN_ID", ""), trigger=a.trigger,
                   summary_path=a.summary_file, timer=timer, started_at=t0)
    except AB.BridgeError as e:
        log(f"FATAL: {AB.scrub(e, token)}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
