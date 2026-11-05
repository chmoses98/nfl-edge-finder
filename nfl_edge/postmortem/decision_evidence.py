"""Decision-time evidence for the router's execution-evidence join: recommendation / model-run DIGESTS, never raw ids.

RUN NFL already writes one record per recommendation (``records/<recommendation_id>.json``). The router records, for each
executed order, only digests of its private ids and the first/last fill time (``scripts/accounting/execution_evidence_ledger.py``,
vendored verbatim). The link between the two has to be made here, by the repository that owns the decision, and only when it is
exact: same contract, same side, created BEFORE the first fill and within a stated window. This module produces:

* ``candidates_from_records`` -- the link candidates, with ``recommendation_ref`` / ``model_run_ref`` as domain-separated
  sha256 digests (32 hex) and ``model_as_of`` from the record's own ``ledger_feature_cutoff``. A record that lacks a market,
  side, creation time or model as-of is NOT a candidate and is reported under ``skipped`` with the reason; nothing is filled in.
* ``write_candidates`` -- an append-only JSONL beside ``card.json``: an identical line is never written twice and a line is
  never rewritten.
* ``link_executions`` -- the vendored ``link_recommendation`` over those candidates: LINKED only on a unique exact match,
  AMBIGUOUS when two distinct recommendations qualify (never resolved by picking the nearest), MISSING otherwise.

PASS records are not candidates (nothing was recommended for purchase). Public repository: digests only, no ticker prices,
no stakes, no private identifiers.
"""
from __future__ import annotations

import hashlib
import json
import os

from nfl_edge.postmortem.common import parse_ts

DOMAIN = "nfl-edge-finder.decision-evidence.v1"
DIGEST_CHARS = 32            # same width as the router's id digests (128 bits)
RECOMMENDED = "RECOMMENDED"  # nfl_edge.handicap.schema.RECOMMENDED; compared by value so this module imports nothing heavy
#: Window between a recommendation and the first fill within which a link is allowed. OWNER-ADJUSTABLE; there is no
#: hidden default inside link_recommendation (it refuses a non-positive window), so the caller must state one.
DEFAULT_LINK_WINDOW_SECONDS = 6 * 3600


def ref_digest(kind: str, value: str) -> str:
    """Domain-separated digest of a private id. ``kind`` is 'recommendation' or 'model_run'."""
    if kind not in ("recommendation", "model_run"):
        raise ValueError(f"unknown ref kind {kind!r}")
    return hashlib.sha256(f"{DOMAIN}|{kind}|{value}".encode()).hexdigest()[:DIGEST_CHARS]


def _candidate(record: dict) -> tuple[dict | None, str | None]:
    if record.get("decision") != RECOMMENDED:
        return None, "NOT_A_RECOMMENDATION"
    rid = record.get("recommendation_id")
    ticker, side = record.get("market_ticker"), record.get("side")
    created = parse_ts(record.get("created_at"))
    as_of = (record.get("source_freshness") or {}).get("ledger_feature_cutoff")
    as_of_dt = parse_ts(as_of)
    run_id = record.get("handicap_run_id") or record.get("packet_sha")
    for name, val in (("recommendation_id", rid), ("market_ticker", ticker), ("side", side), ("created_at", created),
                      ("model_as_of", as_of_dt), ("model_run_id", run_id)):
        if not val:
            return None, f"MISSING_{name.upper()}"
    return {"market_ticker": ticker, "side": side, "created_at_ts": created.timestamp(),
            "recommendation_ref": ref_digest("recommendation", rid), "model_run_ref": ref_digest("model_run", str(run_id)),
            "model_as_of": as_of_dt.isoformat()}, None


def candidates_from_records(records) -> dict:
    out, skipped = [], {}
    for rec in records:
        cand, why = _candidate(rec)
        if cand:
            out.append(cand)
        else:
            skipped[why] = skipped.get(why, 0) + 1
    return {"candidates": out, "skipped": dict(sorted(skipped.items()))}


def write_candidates(path: str, candidates: list) -> dict:
    """Append-only. Returns counts. An identical line already present is not written again; existing lines are untouched."""
    have = set()
    if os.path.exists(path):
        with open(path) as fh:
            have = {line.rstrip("\n") for line in fh if line.strip()}
    new = [json.dumps(c, sort_keys=True) for c in candidates]
    fresh = [line for line in new if line not in have]
    if fresh:
        with open(path, "a") as fh:
            for line in fresh:
                fh.write(line + "\n")
    return {"written": len(fresh), "already_present": len(new) - len(fresh)}


def read_candidates(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def link_executions(executions: list, candidates: list, *, window_seconds: float = DEFAULT_LINK_WINDOW_SECONDS) -> list:
    """LINK rows (vendored schema) for router EXECUTION rows. ``executions`` carry market_ticker, side, first_fill_ts."""
    from scripts.accounting import execution_evidence_ledger as L          # the byte-identical vendored copy
    rows = []
    for ex in executions:
        rows.append(L.link_recommendation(ex, candidates, window_seconds=window_seconds,
                                          market_ticker=ex["market_ticker"], side=ex["side"]))
    return rows
