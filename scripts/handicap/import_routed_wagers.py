#!/usr/bin/env python3
"""Import a kalshi-bet-router payload into the handicap ledger. COUNTS ONLY.

This is the entry point the router's delivery workflow runs. It does not decide
anything: `nfl_edge.handicap.import_routed_wagers` owns identity, week
resolution and every refusal, and this script owns reading a file, finding the
schedule, and reporting what happened without printing a wager.

WHAT NEVER REACHES STDOUT
-------------------------
This repository is public and its Actions logs are public. A payload row
carries market, side, contracts, price, stake and fees. So this prints counts,
verdicts and minted ids -- never a ticker, a price or a stake. A refusal prints
its REASON and the row's position in the batch, which is enough to act on and
carries nothing about the bet.

THE SCHEDULE IS NOT OPTIONAL
----------------------------
An NFL week comes from the real schedule, never from arithmetic on a date. If
no schedule can be read, this fails rather than importing wagers under a
guessed week -- a wager filed in the wrong week is counted in a week it did not
happen in and missing from the one it did.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from nfl_edge.data import nfl_calendar  # noqa: E402
from nfl_edge.handicap.import_routed_wagers import import_rows  # noqa: E402

EXIT_OK = 0
EXIT_REFUSED = 1
EXIT_BAD_INPUT = 2


def read_payload(path: str) -> tuple[str, list]:
    """The router's envelope, checked rather than trusted.

    The batch label appears TWICE -- once on the envelope and once on every row
    -- because MLB's importer reads the envelope and this ledger reads the row.
    Two copies of a value can disagree, so the disagreement is made impossible
    to miss instead of being hoped against: a row whose label differs from its
    envelope's is refused here, before anything is written.
    """
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("payload is not an object")
    batch = payload.get("importBatchId")
    if not isinstance(batch, str) or not batch.strip():
        raise ValueError("payload carries no importBatchId")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("payload carries no rows list")

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"row {index} is not an object")
        stated = row.get("import_batch_id")
        if stated != batch:
            raise ValueError(
                f"row {index} says it belongs to a different import batch than "
                "its own envelope; one of the two is wrong and neither may be "
                "assumed"
            )
    return batch, rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", required=True,
                        help="the router's payload file (an envelope with rows)")
    parser.add_argument("--handicap-root", required=True,
                        help="a checkout of the handicap-data branch")
    parser.add_argument("--schedule", default=None,
                        help="path to an nflverse games.csv; otherwise the usual locations")
    parser.add_argument("--allow-schedule-download", action="store_true",
                        help="fetch the schedule if none is on disk")
    parser.add_argument("--receipts-out", default=None,
                        help="write per-row outcomes (ids and verdicts, never economics)")
    args = parser.parse_args(argv)

    try:
        batch, rows = read_payload(args.payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"unreadable payload: {exc}", file=sys.stderr)
        return EXIT_BAD_INPUT

    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    try:
        games, source = nfl_calendar.load_schedule(
            repo_root, path=args.schedule,
            allow_download=args.allow_schedule_download,
        )
    except FileNotFoundError as exc:
        # Fail closed. The alternative is a wager filed under a guessed week.
        print(f"no schedule, so no week can be established: {exc}", file=sys.stderr)
        return EXIT_BAD_INPUT

    print(f"import batch: {batch}")
    print(f"schedule: {source}")
    print(f"rows in payload: {len(rows)}")

    result = import_rows(args.handicap_root, rows, games=games)

    print(f"  written:         {result['written']}")
    print(f"  already present: {result['already_present']}")
    print(f"  refused:         {result['refused']}")
    for index, reason in result["refusals"]:
        # The reason and the row's POSITION. Never the row.
        print(f"    row {index}: {reason}")

    if args.receipts_out:
        with open(args.receipts_out, "w", encoding="utf-8") as handle:
            json.dump({
                "importBatchId": batch,
                "written": result["written"],
                "alreadyPresent": result["already_present"],
                "refused": result["refused"],
                "refusals": [{"row": i, "reason": r} for i, r in result["refusals"]],
                "idsWritten": result["ids_written"],
            }, handle, indent=2, sort_keys=True)
            handle.write("\n")

    # A REFUSAL IS A FAILURE HERE, unlike in the router's health annotation.
    # The router refuses wagers it cannot classify every fifteen minutes and
    # that is normal; a payload that reached this script has already been
    # classified, reconciled and judged importable, so a row this ledger will
    # not take means the two repositories disagree about what is valid.
    return EXIT_REFUSED if result["refused"] else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
