#!/usr/bin/env python3
"""Fail the RUN NFL workflow if the report path can reach Airtable, preflight or the recommendation ledger.

    python3 scripts/ci/assert_no_airtable.py

Runs the same static audit as `tests/test_run_nfl_isolation.py`, inside the workflow, so every report run
carries its own proof in the log rather than relying on a test that ran on some earlier commit.

Exit 0 = the report path imports nothing that knows what Airtable is. Exit 1 = it does, and the run stops
before building anything.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.report_isolation import REPORT_ENTRY_POINTS, audit  # noqa: E402


def main():
    res = audit(ROOT)
    print(f"RUN NFL report path: {len(res['files'])} project modules reachable from "
          f"{len(REPORT_ENTRY_POINTS)} entry points")
    for f in res["files"]:
        print(f"  {f}")
    if res["violations"]:
        print("\nAIRTABLE ISOLATION VIOLATED:", file=sys.stderr)
        for v in res["violations"]:
            print(f"  {v}", file=sys.stderr)
        return 1
    print("\nOK: zero Airtable / preflight / recommendation-ledger reachability. "
          "Report generation is read-only research.")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write(f"\n### Airtable isolation\n\n`{len(res['files'])}` modules reachable from the RUN NFL "
                    "report path; **zero** reach Airtable, preflight, or the recommendation ledger. "
                    "Airtable calls made by this run: **0**.\n\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
