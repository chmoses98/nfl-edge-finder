#!/usr/bin/env python3
"""Validate the owner's actual-wager ledger on a handicap-data checkout. COUNTS ONLY.

    python3 scripts/handicap/validate_routed_ledger.py --handicap-root /path/to/handicap-data --result-out r.json

`handicap-data` carries no `.github/`, so a pull request into it gets no check runs at all. kalshi-bet-router's
auto-merge gate therefore needs a verdict from THIS repository's own rules before it may land a delivery
unattended, and this is it. It reads the whole tree the delivery produced -- not just the new rows -- because a
row can be individually valid and still break the ledger (a second record for one order, a settlement filed in
a different week from its wager).

Every imported wager:
  * parses, and passes `imported_wagers.validate`;
  * sits at data/imported_wagers/<season>/week_<NN>/<imported_wager_id>.json, matching its own fields;
  * if routed (`routed-` prefix), carries the id minted from its `source_bet_key`;
  * is the ONLY record for its `source_bet_key`.

Every settlement:
  * parses, and passes `wager_settlements.validate`;
  * sits at data/wager_settlements/<season>/week_<NN>/<settlement_id>.json, matching its own fields;
  * carries the id minted from its wager's key, and that wager exists in the SAME season and week;
  * is the only settlement for that key.

This repository and its Actions logs are public, so only counts and problem CATEGORIES are printed -- never a
ticker, a price or a stake. Exit 0 clean, 1 a problem was found, 2 the tree could not be read.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import imported_wagers, wager_settlements  # noqa: E402
from nfl_edge.handicap.import_routed_settlements import mint_settlement_id  # noqa: E402
from nfl_edge.handicap.import_routed_wagers import ID_PREFIX as WAGER_PREFIX  # noqa: E402
from nfl_edge.handicap.import_routed_wagers import mint_imported_wager_id  # noqa: E402

_WEEK_DIR = re.compile(r"^week_(\d{2})$")


def _records(root: str, kind: str):
    """(season, week, filename id, record-or-None) for every JSON file under a kind."""
    base = os.path.join(root, "data", kind)
    if not os.path.isdir(base):
        return
    for season_name in sorted(os.listdir(base)):
        season_dir = os.path.join(base, season_name)
        if not os.path.isdir(season_dir):
            continue
        for week_name in sorted(os.listdir(season_dir)):
            m = _WEEK_DIR.match(week_name)
            week_dir = os.path.join(season_dir, week_name)
            if not m or not os.path.isdir(week_dir):
                yield season_name, week_name, None, "UNEXPECTED_DIRECTORY"
                continue
            for name in sorted(os.listdir(week_dir)):
                if not name.endswith(".json"):
                    yield season_name, week_name, name, "UNEXPECTED_FILE"
                    continue
                try:
                    with open(os.path.join(week_dir, name), encoding="utf-8") as handle:
                        record = json.load(handle)
                except (OSError, ValueError):
                    yield season_name, week_name, name[:-5], "UNPARSEABLE"
                    continue
                yield int(season_name) if season_name.isdigit() else season_name, int(m.group(1)), name[:-5], record


def validate_tree(root: str) -> dict:
    problems: dict[str, int] = {}

    def problem(category):
        problems[category] = problems.get(category, 0) + 1

    wagers_by_key: dict[str, list] = {}
    n_wagers = 0
    for season, week, rid, rec in _records(root, "imported_wagers"):
        n_wagers += 1
        if isinstance(rec, str):
            problem(f"wager:{rec}")
            continue
        if imported_wagers.validate(rec):
            problem("wager:SCHEMA_INVALID")
        if rec.get("imported_wager_id") != rid:
            problem("wager:FILENAME_IS_NOT_ITS_ID")
        if (rec.get("season"), rec.get("week")) != (season, week):
            problem("wager:FILED_IN_THE_WRONG_WEEK")
        key = rec.get("source_bet_key")
        if str(rid).startswith(f"{WAGER_PREFIX}-"):
            try:
                if mint_imported_wager_id(key) != rid:
                    problem("wager:ID_NOT_MINTED_FROM_ITS_KEY")
            except Exception:  # noqa: BLE001
                problem("wager:ID_NOT_MINTED_FROM_ITS_KEY")
        if key:
            wagers_by_key.setdefault(key, []).append(rec)
    for recs in wagers_by_key.values():
        if len(recs) > 1:
            problem("wager:MORE_THAN_ONE_RECORD_FOR_ONE_ORDER")

    settled_keys: dict[str, int] = {}
    n_settlements = 0
    for season, week, rid, rec in _records(root, "wager_settlements"):
        n_settlements += 1
        if isinstance(rec, str):
            problem(f"settlement:{rec}")
            continue
        if wager_settlements.validate(rec):
            problem("settlement:SCHEMA_INVALID")
        if rec.get("settlement_id") != rid:
            problem("settlement:FILENAME_IS_NOT_ITS_ID")
        if (rec.get("season"), rec.get("week")) != (season, week):
            problem("settlement:FILED_IN_THE_WRONG_WEEK")
        key = rec.get("source_bet_key")
        try:
            if mint_settlement_id(key) != rid:
                problem("settlement:ID_NOT_MINTED_FROM_ITS_WAGERS_KEY")
        except Exception:  # noqa: BLE001
            problem("settlement:ID_NOT_MINTED_FROM_ITS_WAGERS_KEY")
        wager = (wagers_by_key.get(key) or [None])[0]
        if wager is None:
            problem("settlement:ORPHAN_NO_SUCH_WAGER")
        elif (wager.get("season"), wager.get("week")) != (rec.get("season"), rec.get("week")):
            problem("settlement:NOT_IN_ITS_WAGERS_WEEK")
        settled_keys[key] = settled_keys.get(key, 0) + 1
    if any(n > 1 for n in settled_keys.values()):
        problem("settlement:MORE_THAN_ONE_FOR_ONE_WAGER")

    return {"wagers": n_wagers, "settlements": n_settlements, "problems": sum(problems.values()),
            "problem_categories": dict(sorted(problems.items()))}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handicap-root", required=True)
    parser.add_argument("--result-out", default=None)
    args = parser.parse_args(argv)
    if not os.path.isdir(os.path.join(args.handicap_root, "data")):
        print(f"{args.handicap_root} does not look like the handicap ledger: no data/", file=sys.stderr)
        return 2
    result = validate_tree(args.handicap_root)
    print(f"imported wagers: {result['wagers']}")
    print(f"settlements:     {result['settlements']}")
    print(f"problems:        {result['problems']}")
    for category, count in result["problem_categories"].items():
        print(f"  {category}: {count}")
    if args.result_out:
        with open(args.result_out, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    return 1 if result["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
