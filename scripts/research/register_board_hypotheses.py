#!/usr/bin/env python3
"""Register and PREREGISTER the Weeks 1-3 board hypotheses (nfl_edge/research/board_hypotheses.py).

    python3 scripts/research/register_board_hypotheses.py --board <dir with board_rows.wk01..03.jsonl.gz> \\
        [--registry research/hypothesis_registry/v2/hypotheses.jsonl] [--miner-cells N]

Each hypothesis is added GENERATED with the discovery window (2026 weeks 1-3) and its discovery evidence
verbatim, then preregistered with the frozen thresholds, the evaluation plan and the first test kickoff
(2026_04_PIT_CLE). `hypothesis_registry_v2.preregister` refuses a preregistration made at or after that
kickoff, so this script cannot be run late by accident. Idempotent: an id already in the registry is skipped.
Nothing here changes a model, a gate, a threshold, a stake or betting authority.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.research import board as B                                      # noqa: E402
from nfl_edge.research import board_hypotheses as BH                          # noqa: E402
from nfl_edge.research import hypothesis_registry_v2 as HR                    # noqa: E402

FIELDS = B.SLIM_FIELDS + ("mid", "close_mid", "team_implied_points", "player_disagreement", "data_only_disagreement",
                          "return_yes", "return_no", "is_main_rung", "rung_offset")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", required=True)
    ap.add_argument("--registry", default=os.path.join(ROOT, HR.DEFAULT_PATH))
    ap.add_argument("--miner-cells", type=int, default=0, help="cells the discovery miner tested (multiplicity context)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    rows = []
    for wk in range(BH.GENERATION_WINDOW["week_lo"], BH.GENERATION_WINDOW["week_hi"] + 1):
        rows.extend(B.read_jsonl_gz(os.path.join(a.board, f"board_rows.wk{wk:02d}.jsonl.gz"), FIELDS))
    weeks = list(range(BH.GENERATION_WINDOW["week_lo"], BH.GENERATION_WINDOW["week_hi"] + 1))
    existing = HR.current(a.registry)
    plan_common = {"sample_unit": "game (every interval is game-clustered)", "data": f"{B.BOARD_VERSION} full-board table, "
                   "rebuilt each week from the immutable capture; settlement FOOTBALL_PROVEN tier only",
                   "evaluator": "nfl_edge.research.board_hypotheses.prospective (suggestion only)",
                   "descriptive_only": ["by-week values", "other horizons", "exchange-only tier"],
                   "never": "Weeks 1-3 (the discovery window) are not evidence for or against any of these"}
    out = []
    for spec in BH.BOARD_HYPOTHESES:
        hid = BH.hypothesis_id(spec)
        if hid in existing:
            out.append({"id": hid, "action": "skipped (already registered)", "status": existing[hid]["status"]})
            continue
        ev = BH.evaluate(spec, rows, weeks=weeks)
        if a.dry_run:
            out.append({"id": hid, "action": "dry-run", "discovery": ev})
            continue
        HR.add(hid=hid, market_family=spec["market_family"], condition=spec["condition"], direction=spec["direction"],
               expected_mechanism=spec["mechanism"], evaluation_metric=f"{spec['metric']} (sign {spec['sign']:+d})",
               minimum_sample=BH.THRESHOLDS["min_future_games"], generation_window=BH.GENERATION_WINDOW,
               future_test_window=BH.FUTURE_WINDOW, generated_by="board-miner discovery + owner Weeks 1-3 review",
               effect_size=ev.get("value"), uncertainty=ev.get("se"), sample_size=ev.get("n"), game_count=ev.get("n_games"),
               candidate_slices_considered=(a.miner_cells or None), hypothesis_kind=BH.HYPOTHESIS_KIND, locator=BH.locator(spec),
               generation_evidence={"discovery_weeks": weeks, **ev}, path=a.registry)
        HR.preregister(hid, test_window=BH.FUTURE_WINDOW, thresholds=BH.THRESHOLDS,
                       evaluation_plan={**plan_common, "primary_metric": spec["metric"], "registered_side": spec["sign"],
                                        "filter": spec["filter"]},
                       first_test_kickoff_utc=BH.FIRST_TEST_KICKOFF_UTC,
                       note=f"preregistered before Week 4: {spec['title']}", path=a.registry)
        out.append({"id": hid, "action": "registered + preregistered", "discovery_value": ev.get("value"),
                    "discovery_ci": ev.get("ci"), "games": ev.get("n_games")})
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
