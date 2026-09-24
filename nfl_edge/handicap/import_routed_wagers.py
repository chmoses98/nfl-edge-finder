"""Import wagers the owner actually placed, delivered by kalshi-bet-router.

WHAT THE ROUTER SENDS AND WHAT THIS RESOLVES
--------------------------------------------
The router reconstructs one ORDER from its Kalshi fills and sends the exchange
evidence: market, side, contracts, the quantity-weighted fill price, the fee the
exchange itself reported, the cash consumed, and the contest's own date.

It deliberately does NOT send two things, and this module supplies both:

  * ``imported_wager_id``. A router has no business naming records in this
    ledger. It is minted here, DETERMINISTICALLY from ``source_bet_key``, so the
    same order re-delivered lands on the same record rather than a second one
    under a new name.

  * ``season`` and ``week``. ``ImportedWager`` requires both, and the router
    knows only the date. Turning a date into an NFL week is calendar knowledge,
    and it is resolved here from the REAL schedule -- never computed from the
    date by arithmetic. A wager whose date matches no scheduled game, or matches
    more than one week, is REFUSED rather than filed under a guess.

WHY REFUSING BEATS GUESSING HERE
--------------------------------
A wager filed under the wrong week is not a small error: the weekly reports read
by week, so it would be counted in a week it did not happen in and missing from
the one it did. Two wrong numbers from one guess. An unresolvable wager is
reported and left out, which is one honest gap instead.

IDENTITY IS NOT ECONOMICS
-------------------------
``imported_wager_id`` is derived from ``source_bet_key`` alone -- not from the
stake, the price, the fee or the import batch. Correcting an economics field on
an already-imported wager must land on the SAME record, and a re-import under a
different batch id is still the same wager rather than a second one.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import fields as dataclass_fields

from nfl_edge.data import nfl_calendar
from nfl_edge.handicap import schema, store
from nfl_edge.handicap.imported_wagers import (
    ENTRY_METHOD_IMPORTED_RECEIPT,
    SCHEMA_VERSION,
    ImportedWager,
    validate,
)

#: Prefix on every minted id, so a routed wager is identifiable as one at a
#: glance in a directory listing. Kept inside schema._ID_RE's character class.
ID_PREFIX = "routed"


class ImportRefused(Exception):
    """This wager cannot be filed, and filing it anyway would be worse."""


def mint_imported_wager_id(source_bet_key: str) -> str:
    """A stable id for one order, derived only from the venue's own identity.

    Deliberately NOT a function of the economics or the import batch: a
    correction to a fee must land on the same record, and the same order noticed
    by a second backfill is the same wager.
    """
    if not isinstance(source_bet_key, str) or not source_bet_key.strip():
        raise ImportRefused("source_bet_key is required to mint a wager id")
    digest = hashlib.sha256(source_bet_key.encode("utf-8")).hexdigest()[:24]
    minted = f"{ID_PREFIX}-{digest}"
    if not schema._ID_RE.match(minted):
        raise ImportRefused(f"minted id {minted!r} is not a safe record id")
    return minted


def resolve_season_week(game_date: str, games: list) -> tuple[int, int]:
    """The season and week this contest actually belongs to, from the schedule.

    Matched against scheduled games rather than computed from the date. NFL
    weeks straddle Thursday to Monday and the boundaries move, so arithmetic on
    a date is a guess even when it is usually right.

    Refuses when the date matches no scheduled game, and refuses when it matches
    more than one (season, week) -- an ambiguous answer is not an answer, and
    picking one would hide the ambiguity in a number nobody rechecks.
    """
    matches = {
        (g["season"], g["week"])
        for g in games
        if g.get("gameday") == game_date and nfl_calendar.season_type_of(
            g.get("game_type") or "REG"
        ) == "REG"
    }
    if not matches:
        raise ImportRefused(
            f"no scheduled REG game on {game_date!r}; the week cannot be established "
            "from the schedule, and it will not be computed from the date"
        )
    if len(matches) > 1:
        raise ImportRefused(
            f"{game_date!r} maps to more than one season/week {sorted(matches)}; "
            "refusing rather than choosing one"
        )
    return matches.pop()


def build_record(row: dict, games: list) -> ImportedWager:
    """One router row plus this repository's own knowledge, as a typed record.

    Built through the DATACLASS rather than as a dict on purpose. `validate()`
    does not check `season` and `week`, so a dict assembled by hand could be
    written without them and would then be invisible to every weekly report. The
    dataclass requires them, which makes that mistake impossible rather than
    merely discouraged.
    """
    source_bet_key = row.get("source_bet_key")
    season, week = resolve_season_week(row.get("game_date"), games)

    record = ImportedWager(
        imported_wager_id=mint_imported_wager_id(source_bet_key),
        schema_version=SCHEMA_VERSION,
        source_bet_key=source_bet_key,
        import_batch_id=row.get("import_batch_id"),
        entry_method=row.get("entry_method") or ENTRY_METHOD_IMPORTED_RECEIPT,
        season=season,
        week=week,
        game_date=row.get("game_date"),
        market_ticker=row.get("market_ticker"),
        side=row.get("side"),
        executed_at=row.get("executed_at"),
        contracts=row.get("contracts"),
        actual_price=row.get("actual_price"),
        stake=row.get("stake"),
        fees_paid=row.get("fees_paid"),
        fees_are_estimated=bool(row.get("fees_are_estimated", False)),
        fee_state=row.get("fee_state"),
        venue=row.get("venue") or "kalshi",
    )

    # A router row carrying a field this ledger does not model is a contract
    # break, not something to drop quietly: the sender believes it was recorded.
    known = {f.name for f in dataclass_fields(ImportedWager)}
    unknown = sorted(set(row) - known)
    if unknown:
        raise ImportRefused(f"router row carried unknown field(s): {unknown}")

    problems = validate(record.to_dict())
    if problems:
        raise ImportRefused("; ".join(problems))
    return record


#: The fields that make an already-filed wager THE SAME wager as an incoming row. Provenance (the import batch,
#: the entry method, notes) is deliberately absent: the same order re-delivered under a different batch label is
#: still the same wager, by the identity rule above. Every economic and placement fact is present, so a
#: re-delivery that DISAGREES about a stake, a fee or a week is a conflict -- never a quiet no-op.
IDENTITY_FIELDS = (
    "source_bet_key", "season", "week", "game_date", "market_ticker", "side", "executed_at",
    "contracts", "actual_price", "stake", "fees_paid", "fees_are_estimated", "fee_state", "venue",
)


def _same(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=1e-9)
    return a == b


def conflicting_fields(existing: dict, incoming: dict, fields=IDENTITY_FIELDS) -> list:
    """FIELD NAMES where an already-filed record and an incoming one disagree. Names only, never values."""
    return [f for f in fields if not _same(existing.get(f), incoming.get(f))]


def import_rows(root: str, rows: list, *, games: list) -> dict:
    """Write every row that is not already filed. Returns counts, reasons and one receipt per row.

    ALREADY-PRESENT IS CHECKED BEFORE WRITING, not caught afterwards.
    `schema.write_record` refuses to clobber, which is the immutability
    guarantee -- so a re-import would raise rather than no-op if this asked it
    to write blindly. Re-running a backfill has to be boring.

    ALREADY-PRESENT IS NOT THE SAME AS AGREEING. A record on disk under the
    minted id whose economics differ from the incoming row is a CONFLICT: it is
    refused, never rewritten, and named field by field (names, not values) so
    the disagreement can be resolved by a person. Treating it as a duplicate
    would let a delivery report success while the ledger and the exchange
    disagree about what was paid.

    THE RECEIPTS are what the router's auto-merge gate reads: one row per
    payload row, in payload order, carrying the router's own `source_bet_key`,
    this ledger's minted `imported_wager_id`, and a verdict in the shared
    vocabulary NEW / DUPLICATE_NOOP / CONFLICT / REFUSED. Before 2026-09-24 this
    importer returned counts only, which the router's gate cannot read -- one
    reason NFL was never activated for scheduled delivery.
    """
    written, already_present, refused, receipts = [], [], [], []

    for index, row in enumerate(rows):
        key = row.get("source_bet_key") if isinstance(row, dict) else None
        try:
            record = build_record(row, games)
        except ImportRefused as exc:
            refused.append((index, str(exc)))
            receipts.append({"row": index, "source_bet_key": key, "imported_wager_id": None,
                             "status": "REFUSED", "success": False, "reason": str(exc)})
            continue

        path = store.record_path(
            root, "imported_wagers", record.season, record.week,
            record.imported_wager_id,
        )
        if not os.path.exists(path):
            # Same id filed under a DIFFERENT week is the same wager disagreeing about its week.
            elsewhere = [p for p in _paths_for_id(root, "imported_wagers", record.imported_wager_id)
                         if os.path.abspath(p) != os.path.abspath(path)]
            if elsewhere:
                path = elsewhere[0]
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                existing = json.load(handle)
            differ = conflicting_fields(existing, record.to_dict())
            if differ:
                reason = ("an imported wager with this identity is already filed and disagrees on "
                          f"{differ}; refusing rather than rewriting an immutable record")
                refused.append((index, reason))
                receipts.append({"row": index, "source_bet_key": key,
                                 "imported_wager_id": record.imported_wager_id, "status": "CONFLICT",
                                 "success": False, "reason": reason,
                                 "conflicting_fields": [{"field": f} for f in differ]})
                continue
            already_present.append(record.imported_wager_id)
            receipts.append({"row": index, "source_bet_key": key,
                             "imported_wager_id": record.imported_wager_id, "status": "DUPLICATE_NOOP",
                             "success": True})
            continue
        schema.write_record(path, record.to_dict())
        written.append(record.imported_wager_id)
        receipts.append({"row": index, "source_bet_key": key, "imported_wager_id": record.imported_wager_id,
                         "status": "NEW", "success": True})

    return {
        "written": len(written),
        "already_present": len(already_present),
        "refused": len(refused),
        "refusals": refused,
        "ids_written": written,
        "receipts": receipts,
    }


def _paths_for_id(root: str, kind: str, record_id: str) -> list:
    """Every file named for this id under a kind, whatever season/week directory it sits in."""
    base = os.path.join(root, "data", kind)
    out = []
    if not os.path.isdir(base):
        return out
    for directory, _subdirs, names in os.walk(base):
        if f"{record_id}.json" in names:
            out.append(os.path.join(directory, f"{record_id}.json"))
    return sorted(out)
