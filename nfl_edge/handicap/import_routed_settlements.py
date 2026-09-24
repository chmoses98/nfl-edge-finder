"""Import settlements the router attributed, for wagers already in the ledger.

THE ONE RULE THAT MATTERS HERE
-------------------------------
A settlement may only be written for a wager this ledger already holds. A record
whose ``source_bet_key`` matches nothing is REFUSED -- an orphan settlement is a
payout attributed to a bet this repository has no record of, and it would show
up in every total while belonging to nothing.

The wager it settles also supplies the ``season`` and ``week``. Those are not
re-derived from a date here and are not taken from the router: the wager already
resolved them against the real schedule, and a settlement filed in a different
week from its own wager would make both weekly reports wrong at once.

RE-RUNNING IS A NO-OP
----------------------
A market settles once, so a second observation is a duplicate rather than a
correction, and already-present is checked BEFORE writing -- `write_record`
refuses to clobber, so asking it to write blindly would raise rather than no-op.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import fields as dataclass_fields

from nfl_edge.handicap import schema, store
from nfl_edge.handicap import settlement_amendments as AM
from nfl_edge.handicap.import_routed_wagers import conflicting_fields
from nfl_edge.handicap.wager_settlements import (
    SCHEMA_VERSION,
    WagerSettlement,
    validate,
)

#: Prefix on every minted id, so a routed settlement is identifiable as one at
#: a glance. Kept inside schema._ID_RE's character class.
ID_PREFIX = "stl"


class SettlementRefused(Exception):
    """This settlement cannot be filed, and filing it anyway would be worse."""


def mint_settlement_id(source_bet_key: str) -> str:
    """Derived from the WAGER's key alone, for the same reason the wager's is.

    Not from the result, the payout or the settlement time: a correction to any
    of those must land on the same record rather than beside it.
    """
    if not isinstance(source_bet_key, str) or not source_bet_key.strip():
        raise SettlementRefused("source_bet_key is required to mint a settlement id")
    digest = hashlib.sha256(source_bet_key.encode("utf-8")).hexdigest()[:24]
    minted = f"{ID_PREFIX}-{digest}"
    if not schema._ID_RE.match(minted):
        raise SettlementRefused(f"minted id {minted!r} is not a safe record id")
    return minted


def build_record(row: dict, wager: dict) -> WagerSettlement:
    """One router settlement row plus the wager it settles, as a typed record.

    ``season`` and ``week`` come from the WAGER, never from the row and never
    from a date. The wager resolved them against the real schedule; a settlement
    filed in a different week from its own wager would make both weekly reports
    wrong at once.
    """
    known = {f.name for f in dataclass_fields(WagerSettlement)}
    unknown = sorted(set(row) - {*known, "season", "week"})
    if unknown:
        raise SettlementRefused(f"router row carried unknown field(s): {unknown}")

    record = WagerSettlement(
        settlement_id=mint_settlement_id(row.get("source_bet_key")),
        schema_version=SCHEMA_VERSION,
        source_bet_key=row.get("source_bet_key"),
        season=wager["season"],
        week=wager["week"],
        market_ticker=row.get("market_ticker"),
        side=row.get("side"),
        settlement_status=row.get("settlement_status"),
        settled_at=row.get("settled_at"),
        result=row.get("result"),
        gross_return=row.get("gross_return"),
        net_profit_loss=row.get("net_profit_loss"),
        refusals=list(row.get("refusals") or []),
        venue=row.get("venue") or "kalshi",
        economics_version=row.get("economics_version"),
    )

    problems = validate(record.to_dict())
    if problems:
        raise SettlementRefused("; ".join(problems))
    return record


#: What makes an already-filed settlement THE SAME settlement as an incoming row. A market settles once; a
#: second observation that disagrees about the result or the money is not a correction to apply quietly -- it
#: is a CONFLICT, refused and named, and the terminal record already filed is never regressed or rewritten.
IDENTITY_FIELDS = (
    "source_bet_key", "season", "week", "market_ticker", "side", "settlement_status", "settled_at",
    "result", "gross_return", "net_profit_loss", "refusals", "venue",
)


def import_rows(root: str, rows: list) -> dict:
    """Write every settlement whose wager is on disk. Returns counts, reasons and one receipt per row.

    Receipts use the shared vocabulary NEW / DUPLICATE_NOOP / CONFLICT / REFUSED with the router's
    `source_bet_key` and this ledger's minted `settlement_id`, which is what the router's auto-merge gate
    reads. A settlement for a wager not (yet) in the ledger is REFUSED with its reason -- visible, and retried
    by the next settlement run once the wager has landed.
    """
    wagers = {
        record["source_bet_key"]: record
        for record in store.read_kind(root, "imported_wagers")
        if record.get("source_bet_key")
    }

    written, already_present, refusals, receipts = [], [], [], []

    for index, row in enumerate(rows):
        key = row.get("source_bet_key") if isinstance(row, dict) else None
        try:
            wager = wagers.get(key)
            if wager is None:
                raise SettlementRefused(
                    "no imported wager with this source_bet_key; a settlement "
                    "attributed to a bet this repository has no record of would "
                    "count in every total while belonging to nothing"
                )
            record = build_record(row, wager)
        except SettlementRefused as exc:
            refusals.append((index, str(exc)))
            receipts.append({"row": index, "source_bet_key": key, "settlement_id": None,
                             "status": "REFUSED", "success": False, "reason": str(exc)})
            continue

        path = store.record_path(
            root, "wager_settlements", record.season, record.week,
            record.settlement_id,
        )
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                existing = json.load(handle)
            differ = conflicting_fields(existing, record.to_dict(), IDENTITY_FIELDS)
            incoming = record.to_dict()
            if differ and AM.economics_version_of(existing) != AM.economics_version_of(incoming):
                # A NEWER ECONOMICS CONTRACT for a settlement already filed: never a rewrite. Either an
                # append-only amendment the destination can re-derive itself, or a refusal naming why not.
                try:
                    amendment = AM.build_amendment(existing, path, incoming, wager,
                                                   provenance="kalshi-bet-router settle-wagers")
                except AM.AmendmentRefused as exc:
                    reason = f"the filed settlement differs on {differ} and is not an admissible correction: {exc}"
                    refusals.append((index, reason))
                    receipts.append({"row": index, "source_bet_key": key, "settlement_id": record.settlement_id,
                                     "status": "CONFLICT", "success": False, "reason": reason,
                                     "conflicting_fields": [{"field": f} for f in differ]})
                    continue
                amend_path = store.record_path(root, AM.KIND, record.season, record.week,
                                               amendment["amendment_id"])
                if os.path.exists(amend_path):
                    with open(amend_path, encoding="utf-8") as handle:
                        filed = json.load(handle)
                    if AM.same_correction(filed, amendment):
                        already_present.append(amendment["amendment_id"])
                        receipts.append({"row": index, "source_bet_key": key,
                                         "settlement_id": record.settlement_id, "status": "DUPLICATE_NOOP",
                                         "success": True, "amendment_id": amendment["amendment_id"]})
                        continue
                    reason = "a DIFFERENT correction is already filed for this settlement and version"
                    refusals.append((index, reason))
                    receipts.append({"row": index, "source_bet_key": key, "settlement_id": record.settlement_id,
                                     "status": "CONFLICT", "success": False, "reason": reason})
                    continue
                schema.write_record(amend_path, amendment)
                written.append(amendment["amendment_id"])
                receipts.append({"row": index, "source_bet_key": key, "settlement_id": record.settlement_id,
                                 "status": "CORRECTED", "success": True,
                                 "amendment_id": amendment["amendment_id"]})
                continue
            if differ:
                reason = ("a settlement for this wager is already filed and disagrees on "
                          f"{differ}; refusing rather than rewriting or regressing it")
                refusals.append((index, reason))
                receipts.append({"row": index, "source_bet_key": key, "settlement_id": record.settlement_id,
                                 "status": "CONFLICT", "success": False, "reason": reason,
                                 "conflicting_fields": [{"field": f} for f in differ]})
                continue
            already_present.append(record.settlement_id)
            receipts.append({"row": index, "source_bet_key": key, "settlement_id": record.settlement_id,
                             "status": "DUPLICATE_NOOP", "success": True})
            continue
        schema.write_record(path, record.to_dict())
        written.append(record.settlement_id)
        receipts.append({"row": index, "source_bet_key": key, "settlement_id": record.settlement_id,
                         "status": "NEW", "success": True})

    return {
        "written": len(written),
        "already_present": len(already_present),
        "refused": len(refusals),
        "refusals": refusals,
        "ids_written": written,
        "receipts": receipts,
    }
