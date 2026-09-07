#!/usr/bin/env python3
"""Validate a recommendation payload BEFORE it is committed to handicap-data.

    python3 scripts/handicap/validate_recommendations.py path/to/payload.json
    python3 scripts/handicap/validate_recommendations.py payload.json --write --handicap-root /path/to/wt

The payload is either one record or a list of records. Each is checked against the schema, and `--write`
materialises each as its own immutable file under the handicap-data layout. Validation is deliberately
strict about the things that would make the eventual scorecard meaningless -- a RECOMMENDED record with no
price ceiling, a probability band that is inside out, a stake that is not whole dollars -- and lenient about
the things that are genuinely open, such as an unfamiliar reasoning tag.

THE TWO WRITE PATHS MUST BE EQUIVALENT
--------------------------------------
This is the manual/engineering fallback for the Airtable bridge. Both write to the same immutable ledger, so
both are held to the same standard: a REAL (non-TEST_ONLY) `RECOMMENDED` record is written only after the
decision-time gates pass -- freshness, live ceiling, identity, availability, transaction costs, portfolio
limits -- and its `DecisionGates` record is written beside it.

Without that, this script would be a hole straight through every protection the bridge applies, reachable by
anyone who found it in the runbook. `--market-data` is therefore required whenever the payload contains a
real recommendation. TEST_ONLY records and PASS/WATCHLIST/RESEARCH_ALERT need only the structural checks, for
the same reasons the bridge gives them the same treatment.

Exit codes: 0 valid (warnings allowed), 1 invalid, 2 bad input, 3 refused to overwrite an existing record,
4 a real recommendation failed a decision gate.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from datetime import datetime, timezone               # noqa: E402

from nfl_edge.execution import fees as FEES           # noqa: E402
from nfl_edge.execution import quotes as Q            # noqa: E402
from nfl_edge.handicap import gates as G              # noqa: E402
from nfl_edge.handicap import risk as RISK            # noqa: E402
from nfl_edge.handicap import schema as S             # noqa: E402
from nfl_edge.handicap import store                   # noqa: E402

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
    ap.add_argument("--market-data", default=None,
                    help="checkout of the market-data branch. REQUIRED to write a real RECOMMENDED record: "
                         "the decision-time gates read its capture stream.")
    ap.add_argument("--max-quote-age-minutes", type=float, default=Q.DEFAULT_MAX_QUOTE_AGE_MIN)
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

    # ---- the gates ----------------------------------------------------------------------------------
    real_recs = [rec for kind, rec in to_write
                 if kind == "recommendation" and rec.get("decision") == S.RECOMMENDED
                 and not rec.get("test_only")]
    gate_records = []
    if real_recs:
        if not a.market_data:
            print(f"\n{len(real_recs)} real RECOMMENDED record(s) in this payload, but --market-data was "
                  "not given. A real recommendation is not written without its decision-time gates -- the "
                  "executable price, transaction costs and portfolio limits all have to be checked against "
                  "the world, and the capture stream is where that evidence lives.", file=sys.stderr)
            return 2
        if not os.path.isdir(a.market_data):
            print(f"\n--market-data {a.market_data} is not a directory", file=sys.stderr)
            return 2

        now = datetime.now(timezone.utc)
        ctx = G.GateContext(capture_index=Q.CaptureIndex(os.path.abspath(a.market_data)),
                            fee_schedule=FEES.load_fee_schedule(ROOT), now=now,
                            max_quote_age_minutes=a.max_quote_age_minutes)
        try:
            ctx.risk_report = RISK.evaluate_records(real_recs, RISK.RiskPolicy.load(ROOT))
        except RISK.RiskPolicyError as e:
            print(f"\nrisk policy could not be evaluated: {e}", file=sys.stderr)
            return 4

        failures = []
        for rec in real_recs:
            report = G.evaluate_gates(rec, ctx)
            for name, res in report.gates.items():
                if res.status not in ("PASS", "NOT_APPLICABLE"):
                    print(f"gate {name}: {res.status} -- {res.reason}")
            if report.overall == G.FAIL:
                failures.append(f"{rec['recommendation_id']}: " + "; ".join(report.blocking_reasons))
            else:
                gate_records.append(report.to_record(now=now))

        if failures:
            print("\nREFUSING: these records did not pass the decision-time gates", file=sys.stderr)
            for f in failures:
                print(f"  - {f}", file=sys.stderr)
            return 4
        print(f"\nall {len(real_recs)} real recommendation(s) passed the decision-time gates")

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

    # The gate evidence lands beside the record it justifies, in the same commit.
    by_id = {r["recommendation_id"]: r for r in real_recs}
    for gr in gate_records:
        src = by_id[gr["recommendation_id"]]
        path = store.record_path(a.handicap_root, "decision_gates", src["season"], src["week"],
                                 gr["gates_id"])
        try:
            S.write_record(path, gr)
        except S.ValidationError:
            continue                    # gates already recorded for this recommendation; they run once
        written.append(path)
        print(f"wrote {path}")

    print(f"\n{len(written)} records written. Commit them to the `{store.BRANCH}` branch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
