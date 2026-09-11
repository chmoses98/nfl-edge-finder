#!/usr/bin/env python3
"""Verify a shadow-v2 projection tree before it is published: manifests match files, every prospective record is
prospective (observed and generated strictly before kickoff, or POST_KICKOFF without a probability), no probability
outside a probability state, mid never equals the ask by construction, and the horizon markers are append-only.

    python3 scripts/shadow_v2/verify_projections.py --root data/shadow/v2/projections [--require-rows]

Exit 1 on any problem. Read-only.
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.projection import record as R                                                # noqa: E402
from nfl_edge.projection.store import read_projections, verify                             # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", default=[])
    ap.add_argument("--require-rows", action="store_true")
    a = ap.parse_args(argv)
    roots = a.root or [os.path.join(ROOT, "data", "shadow", "v2", "projections")]
    v = verify(roots)
    problems = list(v.get("problems") or [])
    rows = read_projections(roots)
    if a.require_rows and not rows:
        problems.append("no projection rows found")
    for r in rows:
        st = r.get("support_state")
        if st in R.PROBABILITY_STATES and r.get("p_yes") is None:
            problems.append(f"{r['record_id']}: {st} without a probability")
        if st not in R.PROBABILITY_STATES and r.get("p_yes") is not None:
            problems.append(f"{r['record_id']}: probability on a refused state {st}")
        if r.get("evidence_class") == R.PROSPECTIVE_FROZEN and r.get("p_yes") is not None:
            rec = R.ProjectionRecord(**{k: r.get(k) for k in ("record_id", "snapshot_id", "ticker", "model_arm", "engine", "engine_version", "distribution_version", "model_version")},
                                     observed_at=r.get("observed_at"), generated_at=r.get("generated_at"), kickoff_utc=r.get("kickoff_utc"))
            if r.get("kickoff_utc"):
                ok, why = R.prospective_check(rec)
                if not ok:
                    problems.append(f"{r['record_id']}: {why}")
        if r.get("mid") is not None and r.get("yes_ask") is not None and r.get("yes_bid") is not None and abs(r["mid"] - (r["yes_bid"] + r["yes_ask"]) / 2.0) > 1e-9:
            problems.append(f"{r['record_id']}: mid is not the midpoint of the quote")
    import glob
    n_files = sum(len(glob.glob(os.path.join(r, "*", "*.projections.jsonl.gz"))) for r in roots)
    print(f"projections verified: {len(rows)} rows, {n_files} files, {len(problems)} problems")
    for p in problems[:50]:
        print("  " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
