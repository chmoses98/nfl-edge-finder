#!/usr/bin/env python3
"""Weekly and cumulative research report over the evaluation corpus.

One question, asked the same way every week:

    where does the model add information beyond the market, and where is the market consistently smarter?

The report is built from the immutable corpus alone -- no re-settlement, no model, no network -- so any two
people who run it on the same corpus get the same numbers. `--week` restricts to one week; without it the report
is cumulative. Both are written, because a week is a small sample and the cumulative view is the one that will
eventually answer anything.

Usage:
  python3 scripts/shadow/eval_report.py --market-data /tmp/md --out data/shadow/scorecards/latest
  python3 scripts/shadow/eval_report.py --root data/shadow/evaluations --week 1 --season 2026
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.shadow import evaluation_store as ST                                  # noqa: E402
from nfl_edge.shadow.eval_scorecard import build_scorecard, render_report           # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", default=[], help="evaluation corpus root (repeatable)")
    ap.add_argument("--market-data", default="", help="adds <md>/data/shadow/evaluations as a root")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "scorecards", "report"))
    ap.add_argument("--season", type=int, default=0)
    ap.add_argument("--week", type=int, default=0)
    ap.add_argument("--eval-version", default="", help="restrict to one evaluation version")
    ap.add_argument("--min-segment-n", type=int, default=1)
    ap.add_argument("--game", action="append", default=[])
    a = ap.parse_args()

    roots = list(a.root)
    if a.market_data:
        roots.append(os.path.join(a.market_data, "data", "shadow", "evaluations"))
    if not roots:
        roots = [os.path.join(ROOT, "data", "shadow", "evaluations")]
    rows = ST.read_corpus(roots)
    if a.game:
        rows = [r for r in rows if r.get("game_id") in set(a.game)]
    if a.season:
        rows = [r for r in rows if r.get("season") == a.season]
    weekly = [r for r in rows if a.week and r.get("week") == a.week]

    os.makedirs(a.out, exist_ok=True)
    version = a.eval_version or None
    cumulative = build_scorecard(rows, evaluation_version=version, min_segment_n=a.min_segment_n)
    _write(a.out, "cumulative", cumulative, "Shadow evaluation scorecard - cumulative")
    if a.week:
        wk = build_scorecard(weekly, evaluation_version=version, min_segment_n=a.min_segment_n)
        _write(a.out, f"week{a.week:02d}", wk, f"Shadow evaluation scorecard - week {a.week}")
    print(f"corpus: {len(rows)} evaluations from {len(roots)} root(s) -> {a.out}")
    # The summary line reads the keys build_scorecard actually produces. The previous version indexed
    # `n_evaluations` / `model_vs_market`, which the scorecard never had, so every run died with a KeyError
    # after writing its files -- silently, behind the workflow's continue-on-error.
    raw = cumulative["sample_units"]["raw"]
    con = cumulative["sample_units"]["latest_pregame"]
    view = cumulative["views"]["latest_pregame"]["contract_payout_quality"]
    print(json.dumps({"n_observations": raw["n_observations"], "n_contracts": con["n_unique_contracts"],
                      "n_games": raw["n_games"], "counts": cumulative["counts"]["by_settlement_status"],
                      "model_contract_value": view["model_contract_value"],
                      "market_at_snapshot": view["market_at_snapshot"]}, indent=1))
    return 0


def _write(out, stem, sc, title):
    with open(os.path.join(out, f"{stem}.scorecard.json"), "w") as f:
        json.dump(sc, f, indent=1, default=str)
    with open(os.path.join(out, f"{stem}.REPORT.md"), "w") as f:
        f.write(render_report(sc, title=title) + "\n")


if __name__ == "__main__":
    sys.exit(main())
