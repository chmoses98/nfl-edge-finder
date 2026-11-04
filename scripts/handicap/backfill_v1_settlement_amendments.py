#!/usr/bin/env python3
"""Backfill PROVEN legacy NFL settlement fee corrections; never edit filed records.

Dry run by default:
    python scripts/handicap/backfill_v1_settlement_amendments.py \
        --handicap-root /path/to/handicap-data --season 2026

Explicitly write only independently reconciled append-only amendment files:
    python scripts/handicap/backfill_v1_settlement_amendments.py \
        --handicap-root /path/to/handicap-data --season 2026 --apply

Use this only in a protected handicap-data checkout, with a reviewed commit
and the existing validate_routed_ledger.py gate. stdout contains COUNTS only.
Every unverified fee or amount remains unresolved; never guess a net figure.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import schema, settlement_amendments as AM, store  # noqa: E402


# Ledger values are rounded to four decimal places. This is the same
# sub-cent tolerance used by the established CFB legacy settlement backfill.
FEE_TOLERANCE = Decimal("0.00051")
PROVENANCE = "NFL legacy settlement backfill: fee verified against all recorded owner order fills"


def money(value):
    """Return finite Decimal for a real number, otherwise None."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        return None
    try:
        number = Decimal(str(value))
        return number if number.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def plan(root: str, season: int) -> tuple[list[tuple[str, dict]], dict]:
    """Propose amendments from immutable ledger evidence, no writes."""
    wagers = store.read_kind(root, "imported_wagers", season=season)
    settlements = store.read_kind(root, "wager_settlements", season=season)
    amendments = AM.read_amendments(root)

    by_source = defaultdict(list)
    by_market = defaultdict(list)
    for wager in wagers:
        by_source[wager.get("source_bet_key")].append(wager)
        by_market[wager.get("market_ticker")].append(wager)

    planned = []
    reasons = Counter()
    for settlement in settlements:
        if AM.economics_version_of(settlement) != AM.ECONOMICS_V1:
            reasons["ALREADY_V2"] += 1
            continue
        if amendments.get(settlement.get("settlement_id")):
            # Confirm the existing correction is coherent rather than creating a
            # competing record or silently replacing it.
            AM.canonical_settlement(settlement, amendments[settlement["settlement_id"]])
            reasons["ALREADY_AMENDED"] += 1
            continue
        key = settlement.get("source_bet_key")
        candidates = by_source.get(key, [])
        if len(candidates) != 1:
            reasons["MISSING_OR_DUPLICATE_WAGER"] += 1
            continue
        wager = candidates[0]
        if (settlement.get("season"), settlement.get("week")) != (wager.get("season"), wager.get("week")):
            reasons["WEEK_MISMATCH"] += 1
            continue
        if settlement.get("settlement_status") != "SETTLED" or settlement.get("market_ticker") != wager.get("market_ticker"):
            reasons["MARKET_OR_STATUS_MISMATCH"] += 1
            continue

        gross = money(settlement.get("gross_return"))
        old_net = money(settlement.get("net_profit_loss"))
        stake = money(wager.get("stake"))
        if gross is None or old_net is None or stake is None:
            # A null legacy P&L cannot establish the venue's duplicate fee.
            # Such records need the independent exchange v2 delivery.
            reasons["LEGACY_ECONOMICS_UNESTABLISHED"] += 1
            continue

        ticker = settlement.get("market_ticker")
        market_wagers = by_market.get(ticker, [])
        if not ticker or not market_wagers or any(
            w.get("fees_are_estimated") is not False or money(w.get("fees_paid")) is None
            for w in market_wagers
        ):
            reasons["ACTUAL_MARKET_FEES_UNESTABLISHED"] += 1
            continue
        # Kalshi's v1 settlement fee_cost was the market position's cumulative
        # trading fee. For shared-position YES/NO markets, compare against ALL
        # account orders for that ticker, not just this order's entry fee.
        market_fee = sum((money(w["fees_paid"]) for w in market_wagers), Decimal(0))
        implied_duplicate = gross - stake - old_net
        if abs(implied_duplicate - market_fee) > FEE_TOLERANCE:
            reasons["SETTLEMENT_FEE_NOT_RECONCILED"] += 1
            continue
        if implied_duplicate <= 0:
            reasons["NO_EXTRA_FEE_TO_CORRECT"] += 1
            continue

        new_net = float(round(gross - stake, 4))
        corrected = {
            **settlement,
            "economics_version": AM.ECONOMICS_V2,
            "net_profit_loss": new_net,
            "refusals": [],
        }
        try:
            amendment = AM.build_amendment(
                settlement, settlement["_path"], corrected, wager, provenance=PROVENANCE
            )
        except AM.AmendmentRefused:
            reasons["AMENDMENT_VALIDATION_REFUSED"] += 1
            continue
        if AM.validate(amendment):
            reasons["AMENDMENT_SCHEMA_INVALID"] += 1
            continue
        path = store.record_path(
            root, AM.KIND, settlement["season"], settlement["week"], amendment["amendment_id"]
        )
        if os.path.exists(path):
            reasons["TARGET_ALREADY_EXISTS"] += 1
            continue
        planned.append((path, amendment))

    return planned, {
        "wagers_read": len(wagers),
        "settlements_read": len(settlements),
        "verified_amendments_planned": len(planned),
        "reason_counts": dict(sorted(reasons.items())),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handicap-root", required=True)
    parser.add_argument("--season", required=True, type=int)
    parser.add_argument("--apply", action="store_true", help="write proven append-only records; dry run by default")
    args = parser.parse_args(argv)
    if not os.path.isdir(os.path.join(args.handicap_root, "data")):
        print("missing data/ checkout", file=sys.stderr)
        return 2
    planned, report = plan(args.handicap_root, args.season)
    if args.apply:
        for path, amendment in planned:
            # Idempotence: schema writer refuses existing records, and the
            # original settlement has already been independently hashed.
            schema.write_record(path, amendment)
    print(f"legacy settlement audit: wagers={report['wagers_read']} "
          f"settlements={report['settlements_read']} "
          f"proven={report['verified_amendments_planned']} "
          f"written={len(planned) if args.apply else 0} "
          f"mode={'APPLY' if args.apply else 'DRY_RUN'}")
    for reason, count in report["reason_counts"].items():
        print(f"  {reason}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
