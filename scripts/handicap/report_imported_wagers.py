#!/usr/bin/env python3
"""Print the imported-wager ledger's accounting summary. NOT a model result.

Every wager in `imported_wagers` was placed by the owner and recommended by
nothing in this repository, so the record below is a fact about a bankroll. The
scorecard is where the model's record lives, and it does not read this kind.

Reads only.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from nfl_edge.handicap import store  # noqa: E402
from nfl_edge.handicap.imported_wager_report import render, summarize  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handicap-root", required=True,
                        help="a checkout of the handicap-data branch")
    parser.add_argument("--season", required=True, type=int)
    parser.add_argument("--week", type=int, default=None,
                        help="restrict to one week; otherwise the whole season")
    args = parser.parse_args(argv)

    kind_dir = os.path.join(args.handicap_root, "data", "imported_wagers")
    if not os.path.isdir(kind_dir):
        # "the kind has never been written to" and "a season in which nothing
        # was wagered" are different facts. Printing zeros would state the
        # second one.
        print(f"no imported_wagers records at {kind_dir}", file=sys.stderr)
        return 1

    records = store.read_kind(args.handicap_root, "imported_wagers",
                              season=args.season, week=args.week)
    # Settlements are their own kind. Absent is the record for "not settled
    # yet", so a kind that was never written to is a legitimate empty list.
    settlements = store.read_kind(args.handicap_root, "wager_settlements",
                                  season=args.season, week=args.week)
    print(render(summarize(records, args.season, settlements=settlements)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
