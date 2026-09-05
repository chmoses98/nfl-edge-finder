#!/usr/bin/env python3
"""Validate a recommendation payload BEFORE it is committed to handicap-data.

    python3 scripts/handicap/validate_recommendations.py path/to/payload.json
    python3 scripts/handicap/validate_recommendations.py payload.json --write --handicap-root /path/to/wt

The payload is either one record or a list of records. Each is checked against the schema, and `--write`
materialises each as its own immutable file under the handicap-data layout. Validation is deliberately
strict about the things that would make the eventual scorecard meaningless -- a RECOMMENDED record with no
price ceiling, a probability band that is inside out, a stake that is not whole dollars -- and lenient about
the things that are genuinely open, such as an unfamiliar reasoning tag.

Exit codes: 0 valid (warnings allowed), 1 invalid, 2 bad input, 3 refused to overwrite an existing record.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import schema as S            # noqa: E402
from nfl_edge.handicap import store                  # noqa: E402

KIND_BY_ID_PREFIX = {"rec": "recommendation", "exe": "execution", "pmt": "postmortem"}


def _kind_of(rec: dict) -> str:
    for field, kind in (("recommendation_id", "recommendation"), ("execution_id", "execution"),
                        ("postmortem_id", "postmortem")):
        if rec.get(field):
            # a postmortem and an execution both carry recommendation_id, so check the specific id first
            if field == "recommendation_id" and (rec.get("execution_id") or rec.get("postmortem_id")):
                continue
            return kind
    raise ValueError("cannot tell what kind of record this is: no recommendation_id/execution_id/"
                     "postmortem_id present")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("payload", help="JSON file: one record or a list of records")
    ap.add_argument("--write", action="store_true", help="write validated records into the ledger")
    ap.add_argument("--handicap-root", default=None,
                    help="worktree of the handicap-data branch (required with --write)")
    ap.add_argument("--allow-test", action="store_true",
                    help="permit test_only records (they are excluded from every report)")
    a = ap.parse_args()

    try:
        payload = json.load(open(a.payload))
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read payload: {e}", file=sys.stderr)
        return 2
    records = payload if isinstance(payload, list) else [payload]
    if not records:
        print("payload contains no records", file=sys.stderr)
        return 2

    ok, problems, warnings, to_write = 0, [], [], []
    for i, rec in enumerate(records):
        label = f"[{i}] {rec.get('recommendation_id') or rec.get('execution_id') or rec.get('postmortem_id') or '<no id>'}"
        try:
            kind = _kind_of(rec)
            rec.setdefault("schema_version", S.HANDICAP_SCHEMA_VERSION)
            warns = S.VALIDATORS[kind](rec)
            if rec.get("test_only") and not a.allow_test:
                raise S.ValidationError("record is marked test_only; pass --allow-test to accept it")
            for w in warns:
                warnings.append(f"{label}: {w}")
            ok += 1
            to_write.append((kind, rec))
            print(f"OK   {label}  ({kind}"
                  + (f", {rec.get('decision')}" if kind == "recommendation" else "") + ")")
        except (S.ValidationError, ValueError) as e:
            problems.append(f"{label}: {e}")
            print(f"FAIL {label}: {e}")

    for w in warnings:
        print(f"warn {w}")
    print(f"\n{ok}/{len(records)} records valid, {len(warnings)} warnings")

    if problems:
        print("\nREFUSING: fix these before committing anything", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    if not a.write:
        print("\n(dry run -- pass --write with --handicap-root to materialise these records)")
        return 0

    if not a.handicap_root:
        print("--write requires --handicap-root", file=sys.stderr)
        return 2

    plural = {"recommendation": "recommendations", "execution": "executions", "postmortem": "postmortems"}
    written = []
    for kind, rec in to_write:
        season = rec.get("season")
        week = rec.get("week")
        if season is None or week is None:
            # executions and postmortems inherit the slate from their recommendation
            src = store.read_kind(a.handicap_root, "recommendations", include_test=True)
            match = next((r for r in src if r["recommendation_id"] == rec.get("recommendation_id")), None)
            if not match:
                print(f"cannot place {rec} -- no season/week and its recommendation is not in the ledger",
                      file=sys.stderr)
                return 2
            season, week = match["season"], match["week"]
        rid = rec.get("recommendation_id") if kind == "recommendation" else (
            rec.get("execution_id") or rec.get("postmortem_id"))
        path = store.record_path(a.handicap_root, plural[kind], season, week, rid)
        try:
            S.write_record(path, rec)
        except S.ValidationError as e:
            print(f"REFUSED: {e}", file=sys.stderr)
            return 3
        written.append(path)
        print(f"wrote {path}")
    print(f"\n{len(written)} records written. Commit them to the `{store.BRANCH}` branch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
