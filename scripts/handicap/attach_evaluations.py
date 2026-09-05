#!/usr/bin/env python3
"""Attach derived evaluations to recommendations from ledger closes and settlement.

    python3 scripts/handicap/attach_evaluations.py --handicap-root /path/to/handicap-wt \
        --market-data /home/user/_market_data_wt [--write]

Reads every recommendation, finds each ticker's LAST PREGAME observation across published shadow-ledger
snapshots, and writes one evaluation record per recommendation. Recommendations are never touched.

Settlement is taken from the ledger's settled markets when present. A market with no settlement yet is
evaluated for CLV only and recorded as UNSETTLED -- it is re-evaluated later as a NEW evaluation record, so
the CLV-only view and the settled view both survive in the history.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import schema as S       # noqa: E402
from nfl_edge.handicap import store             # noqa: E402
from nfl_edge.handicap.evaluate import evaluate  # noqa: E402


def load_observations(md_root: str, tickers: set) -> dict:
    """ticker -> [observations] across every published snapshot, oldest first."""
    out = defaultdict(list)
    files = sorted(glob.glob(os.path.join(md_root, "data", "shadow", "ledger", "*",
                                          "*.observations.jsonl.gz")))
    for f in files:
        for line in gzip.open(f, "rt"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ticker") in tickers:
                out[r["ticker"]].append(r)
    for t in out:
        out[t].sort(key=lambda r: r.get("observed_at") or "")
    return out, len(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handicap-root", required=True)
    ap.add_argument("--market-data", default="/home/user/_market_data_wt")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--include-test", action="store_true",
                    help="also evaluate TEST_ONLY records (they stay excluded from reports)")
    a = ap.parse_args()

    recs = store.read_kind(a.handicap_root, "recommendations", include_test=a.include_test)
    if not recs:
        print("no recommendations found -- nothing to evaluate")
        return 0
    recs = store.latest_amendment_chain(recs)
    execs = store.index_by(store.read_kind(a.handicap_root, "executions",
                                           include_test=a.include_test), "recommendation_id")

    tickers = {r["market_ticker"] for r in recs}
    obs, n_files = load_observations(a.market_data, tickers)
    print(f"{len(recs)} recommendations, {len(tickers)} tickers, {n_files} ledger snapshots scanned")

    now = datetime.now(timezone.utc)
    written, missing_close, unsettled = 0, 0, 0
    for r in recs:
        rows = obs.get(r["market_ticker"], [])
        settlement = None
        for o in rows:
            if o.get("settlement") is not None:
                settlement = o["settlement"]
        ex = (execs.get(r["recommendation_id"]) or [None])[0]
        ev = evaluate(r, rows, settlement=settlement, execution=ex, now=now)
        if ev.get("close_basis") == "MISSING_CLOSE":
            missing_close += 1
        if ev.get("outcome") == "UNSETTLED":
            unsettled += 1
        if a.write:
            path = store.record_path(a.handicap_root, "evaluations", r["season"], r["week"],
                                     ev["evaluation_id"])
            try:
                S.write_record(path, ev)
                written += 1
            except S.ValidationError:
                pass       # an identical evaluation already exists; evaluations are immutable too
        else:
            print(f"  {r['recommendation_id']}  clv={ev.get('clv')}  outcome={ev.get('outcome')}  "
                  f"close={ev.get('close_basis')}")
    print(f"\nmissing close: {missing_close}   unsettled: {unsettled}")
    print(f"{'wrote ' + str(written) if a.write else 'dry run -- pass --write'} evaluation records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
