#!/usr/bin/env python3
"""PRE-TRADE preflight. Run this BEFORE a candidate is shown to anyone as a bet.

    python3 scripts/handicap/preflight_candidate.py candidates.json \
        --market-data /home/user/_market_data_wt --handicap-root /home/user/_ledger_wt

    python3 scripts/handicap/preflight_candidate.py candidates.json ... --json > preflight.json

The payload is one candidate record or a list of them, in the recommendation schema. `decision` may be
CANDIDATE, WATCHLIST or RECOMMENDED -- each is evaluated as the RECOMMENDED record it would become, which is
the only question worth asking before the money moves.

WHY THIS EXISTS SEPARATELY FROM THE IMPORTER
--------------------------------------------
The Airtable importer runs every twelve hours, on purpose. That cadence is right for archival transport and
catastrophic for pre-trade control: without this script the first time anything checks depth, fees, net EV
or the cumulative portfolio caps is up to twelve hours after the owner has already placed the bet.

This runs the SAME gates, from the same module, at the same clock -- the candidate's own `created_at`. The
importer later replays them from the capture stream and commits the evidence. Neither is a copy of the other.

EXIT CODES
    0   every candidate is approved and may be shown as a BET at the approved stake
    2   bad input or missing evidence source
    5   at least one candidate is BLOCKED and must NOT be surfaced as a bet

A blocked candidate is not an error in the pipeline. It is the pipeline working: surface it as a CANDIDATE,
a WATCHLIST entry or a PASS, and record the reasons.

This script places nothing and writes nothing to the ledger.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.execution import depth as DEPTH        # noqa: E402
from nfl_edge.execution import quotes as Q           # noqa: E402
from nfl_edge.handicap import preflight as P         # noqa: E402
from nfl_edge.handicap import risk as RISK           # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("payload", help="JSON file: one candidate record or a list of them")
    ap.add_argument("--market-data", required=True,
                    help="checkout of the market-data branch; the quote and depth gates read its captures")
    ap.add_argument("--handicap-root", required=True,
                    help="checkout of the handicap-data branch; OUTSTANDING portfolio exposure is read from "
                         "it, so caps bind across handicap runs rather than resetting every batch")
    ap.add_argument("--max-quote-age-minutes", type=float, default=Q.DEFAULT_MAX_QUOTE_AGE_MIN)
    ap.add_argument("--max-book-age-minutes", type=float, default=DEPTH.DEFAULT_MAX_BOOK_AGE_MIN)
    ap.add_argument("--bankroll", type=float, default=None,
                    help="override the bankroll snapshot carried on the records")
    ap.add_argument("--json", action="store_true", help="emit the full result objects instead of a summary")
    a = ap.parse_args(argv)

    try:
        payload = json.load(open(a.payload))
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read payload: {e}", file=sys.stderr)
        return 2
    candidates = payload if isinstance(payload, list) else [payload]
    if not candidates:
        print("payload contains no candidates", file=sys.stderr)
        return 2

    for label, path in (("--market-data", a.market_data), ("--handicap-root", a.handicap_root)):
        if not os.path.isdir(path):
            # Fail here rather than inside a gate. Without these two checkouts the answer would be "blocked
            # because we could not look", which is correct and unhelpful; the operator needs to know it is a
            # misconfiguration on this machine and not a verdict on the bet.
            print(f"{label} {path} is not a directory. Preflight needs the capture stream (for the "
                  "executable price and the order book) and the committed ledger (for outstanding "
                  "portfolio exposure); neither can be assumed empty.", file=sys.stderr)
            return 2

    try:
        results = P.preflight_batch(
            candidates, market_data_root=a.market_data, ledger_root=a.handicap_root, root=ROOT,
            max_quote_age_minutes=a.max_quote_age_minutes,
            max_book_age_minutes=a.max_book_age_minutes, bankroll_snapshot=a.bankroll)
    except RISK.RiskPolicyError as e:
        print(f"the risk policy could not be evaluated, so nothing is approved: {e}", file=sys.stderr)
        return 5

    if a.json:
        print(json.dumps([r.to_dict() for r in results], indent=1, sort_keys=True, default=str))
    else:
        print(P.summarise(results))
        out = (results[0].outstanding or {}) if results else {}
        if out:
            print(f"\noutstanding exposure at the decision: ${float(out.get('total') or 0):.2f} "
                  f"across {len(out.get('positions') or [])} live position(s); "
                  f"by group {out.get('by_correlation_group') or {}}")

    approved = [r for r in results if r.may_be_shown_as_a_bet]
    blocked = [r for r in results if not r.may_be_shown_as_a_bet]
    print(f"\n{len(approved)} approved for a BET, {len(blocked)} blocked")
    if blocked:
        print("BLOCKED candidates must NOT be surfaced as a bet or a final RECOMMENDED instruction. "
              "Surface them as CANDIDATE / WATCHLIST / PASS with the reasons above.", file=sys.stderr)
        return 5
    print("These may be surfaced as RECOMMENDED at the APPROVED stake. Preflight authorises a human to act; "
          "it places nothing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
