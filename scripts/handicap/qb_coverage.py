#!/usr/bin/env python3
"""Report which games of a RUN NFL packet have BOTH quarterbacks confirmed (counts and states only; public-safe).

    python3 scripts/handicap/qb_coverage.py --packet data/handicap_report/packet.json [--confirmations qb/qb_confirmations] \
        [--as-of 2026-11-08T15:00:00Z] --out qb_coverage.json [--summary-md "$GITHUB_STEP_SUMMARY"]

Informational: it never fails a run and never edits the packet. A missing --confirmations path is reported as "no source supplied".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.postmortem import qb_confirmations as QBC  # noqa: E402
from nfl_edge.postmortem.common import parse_ts  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--packet", required=True)
    ap.add_argument("--confirmations", default=None)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary-md", default=None)
    a = ap.parse_args(argv)
    as_of = parse_ts(a.as_of) if a.as_of else datetime.now(timezone.utc)
    games = json.load(open(a.packet))["games"]
    recs, rej = [], []
    supplied = bool(a.confirmations and os.path.exists(a.confirmations))
    if supplied:
        try:
            recs, rej = QBC.load_records_file(a.confirmations)
        except (OSError, ValueError) as exc:
            print(f"::warning::confirmation ledger unreadable: {exc}", file=sys.stderr)
            supplied = False
    resolved = QBC.resolve_slate(recs, games, as_of=as_of)
    cov = QBC.coverage(resolved, games, as_of=as_of)
    cov.update({"source_supplied": supplied, "records_valid": len(recs), "records_rejected": len(rej)})
    with open(a.out, "w") as fh:
        json.dump(cov, fh, indent=1)
    lines = [f"### Confirmed-starter quarterback coverage ({cov['as_of']})", "",
             f"- games with BOTH quarterbacks confirmed: **{cov['games_both_qbs_confirmed']} / {cov['games']}**",
             f"- confirmation source supplied: {'yes' if supplied else 'NO - every game-level score market stays blocked QB_UNKNOWN'}",
             f"- records valid / rejected: {len(recs)} / {len(rej)}",
             f"- team slots not confirmed, by reason: {cov['team_slots_not_confirmed_by_reason'] or 'none'}"]
    text = "\n".join(lines)
    print(text)
    if a.summary_md:
        with open(a.summary_md, "a") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
