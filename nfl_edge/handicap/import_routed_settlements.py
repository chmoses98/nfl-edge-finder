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
import os
from dataclasses import fields as dataclass_fields

from nfl_edge.handicap import schema, store
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
    )

    problems = validate(record.to_dict())
    if problems:
        raise SettlementRefused("; ".join(problems))
    return record


def import_rows(root: str, rows: list) -> dict:
    """Write every settlement whose wager is on disk. Returns counts and reasons."""
    wagers = {
        record["source_bet_key"]: record
        for record in store.read_kind(root, "imported_wagers")
        if record.get("source_bet_key")
    }

    written, already_present, refusals = [], [], []

    for index, row in enumerate(rows):
        try:
            wager = wagers.get(row.get("source_bet_key"))
            if wager is None:
                raise SettlementRefused(
                    "no imported wager with this source_bet_key; a settlement "
                    "attributed to a bet this repository has no record of would "
                    "count in every total while belonging to nothing"
                )
            record = build_record(row, wager)
        except SettlementRefused as exc:
            refusals.append((index, str(exc)))
            continue

        path = store.record_path(
            root, "wager_settlements", record.season, record.week,
            record.settlement_id,
        )
        if os.path.exists(path):
            already_present.append(record.settlement_id)
            continue
        schema.write_record(path, record.to_dict())
        written.append(record.settlement_id)

    return {
        "written": len(written),
        "already_present": len(already_present),
        "refused": len(refusals),
        "refusals": refusals,
        "ids_written": written,
    }
