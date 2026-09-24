#!/usr/bin/env python3
"""PREREGISTER the two Week-2 game-centre deviation hypotheses (WS3). Idempotent; the output is committed.

    python3 scripts/research/preregister_game_centre_v2.py [--registry research/hypothesis_registry/v2/hypotheses.jsonl]

WHAT IS BEING CLAIMED, AND ON WHAT

The three-arm Week-2 report (market-data: data/shadow/arm_reports/20260923T123122Z/week02.REPORT.md) showed
DATA_ONLY's deviation from the snapshot market centre pointing toward the close more often than away:
latest-pregame margin toward 2 / away 1 / unchanged 13, total toward 3 / away 1 / unchanged 12. Three or four
directional games are not evidence of anything; at T-24h the margin split was the other way (1 / 5). What they
are is a HYPOTHESIS, and this script writes it down, with the bar it must clear, before the first game that
could test it -- Week-3 Thursday Night Football, 2026-09-25T00:15Z. Week 2 can never count toward it.

    H2-GC-MARGIN-2026W02   when |DATA_ONLY margin - snapshot market margin| >= 1.0 point, the market's margin
                           moves toward DATA_ONLY by the close (toward rate > 0.5 over toward + away)
    H2-GC-TOTAL-2026W02    the same for the total

Generation evidence is stored VERBATIM: the published per-horizon counts (every deviation, no threshold -- the
report did not split at 1.0 point) and the latest-pregame counts recomputed at the preregistered 1.0-point
threshold from the report's per-game table (transcribed below), by the same `deviation_signal` the arm report
now runs. Recomputing the published all-deviation latest-pregame counts from that table is also asserted, so a
transcription error cannot pass silently.

WHAT THIS SCRIPT CAN NOT DO: it writes GENERATED and PREREGISTERED lines only. It never moves a hypothesis to
TESTING or a verdict, never touches a model weight and never touches production eligibility. Re-running it
after the hypotheses exist writes nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.arms import registry as R                                         # noqa: E402
from nfl_edge.arms.scorecard import deviation_signal                              # noqa: E402
from nfl_edge.research import hypothesis_registry_v2 as HR                        # noqa: E402

SOURCE = {"branch": "market-data", "commit": "6a056a6cc33e3e551c5169b3b1a0baef97b8db41",
          "report": "data/shadow/arm_reports/20260923T123122Z/week02.REPORT.md",
          "scorecard": "data/shadow/arm_reports/20260923T123122Z/week02.scorecard.json"}
GENERATION_WINDOW = {"season": 2026, "week_lo": 2, "week_hi": 2}
FUTURE_TEST_WINDOW = {"season": 2026, "week_lo": 3, "week_hi": 18}
FIRST_TEST_KICKOFF_UTC = "2026-09-25T00:15:00+00:00"      # Week 3, Thursday Night Football

# Week-2 latest-pregame DATA_ONLY rows, transcribed from the report's per-game table:
# game, minutes to kickoff, DATA_ONLY margin, DATA_ONLY total, actual margin, actual total,
# snapshot market margin, snapshot market total, close margin, close total.
WEEK2_LATEST_PREGAME = [
    ("2026_02_DET_BUF", 167, 3.74, 48.96, 10, 72, 5.5, 54.5, 5.5, 54.5),
    ("2026_02_CAR_ATL", 44, 4.79, 45.58, -31, 37, -1.5, 43.0, -1.5, 43.0),
    ("2026_02_CIN_HOU", 44, 4.76, 45.07, -14, 26, 2.5, 45.0, 2.5, 45.0),
    ("2026_02_CLE_TB", 44, 5.47, 43.49, -4, 42, 9.0, 41.5, 9.0, 41.5),
    ("2026_02_GB_NYJ", 44, -4.20, 46.22, -3, 37, -3.5, 43.5, -2.5, 44.0),
    ("2026_02_MIN_CHI", 44, 2.48, 44.95, -6, 12, 4.5, 46.5, 4.5, 46.5),
    ("2026_02_NO_BAL", 44, 6.54, 45.65, -7, 41, 9.0, 45.5, 9.0, 45.5),
    ("2026_02_PHI_TEN", 44, -7.79, 41.31, -4, 44, -6.5, 39.0, -7.5, 39.5),
    ("2026_02_PIT_NE", 44, 4.42, 44.87, 17, 23, 5.5, 40.0, 5.5, 41.0),
    ("2026_02_JAX_DEN", 42, -1.81, 43.53, 7, 33, 2.5, 45.0, 2.5, 45.0),
    ("2026_02_LV_LAC", 42, 5.00, 41.38, -12, 40, 7.5, 43.0, 7.0, 43.5),
    ("2026_02_MIA_SF", 62, 9.55, 48.28, 22, 48, 13.0, 44.5, 13.0, 44.5),
    ("2026_02_SEA_ARI", 62, -8.44, 40.18, -24, 38, -3.5, 40.0, -3.5, 40.0),
    ("2026_02_WAS_DAL", 62, -1.14, 49.37, 17, 57, 4.5, 50.5, 4.5, 50.5),
    ("2026_02_IND_KC", 66, 5.33, 44.28, 3, 63, 6.5, 45.0, 6.5, 45.0),
    ("2026_02_NYG_LA", 52, 7.09, 51.41, 22, 34, 7.0, 47.5, 7.0, 47.5),
]

# The report's "Information addition" table for DATA_ONLY, every deviation (no threshold), verbatim:
# horizon -> target -> (games, toward, away, unchanged, no close)
WEEK2_PUBLISHED_ALL_DEVIATIONS = {
    "latest_pregame": {"margin": (16, 2, 1, 13, 0), "total": (16, 3, 1, 12, 0)},
    "T-24h": {"margin": (15, 1, 5, 9, 0), "total": (15, 7, 1, 7, 0)},
    "T-6h": {"margin": (6, 1, 0, 5, 0), "total": (6, 1, 2, 3, 0)},
    "T-90m": {"margin": (15, 3, 1, 11, 0), "total": (15, 3, 1, 11, 0)},
    "T-30m": {"margin": (15, 2, 1, 12, 0), "total": (15, 3, 1, 11, 0)},
}


def week2_rows() -> list:
    """The transcribed table as arm-evaluation-shaped rows, so the arm report's own code does the counting."""
    out = []
    for g, mtk, dm, dt, am, at, mm, mt, cm, ct in WEEK2_LATEST_PREGAME:
        out.append({"game_id": g, "season": 2026, "week": 2, "minutes_to_kickoff": float(mtk), "record_status": R.OK,
                    "prediction_id": g, "actual": {"margin": float(am), "total": float(at)},
                    "market_at_snapshot": {"margin": mm, "total": mt},
                    "close": {"status": "OK", "margin": cm, "total": ct},
                    "arms": {R.DATA_ONLY: {"status": R.OK, "projected_home_margin": dm, "projected_total": dt,
                                           "margin_error": dm - am, "total_error": dt - at}}})
    return out


def generation_evidence(target: str) -> dict:
    sig = deviation_signal(week2_rows())
    all_dev = deviation_signal(week2_rows(), threshold=0.0)
    lp = sig["views"]["latest_pregame"][R.DATA_ONLY][target]
    lp_all = all_dev["views"]["latest_pregame"][R.DATA_ONLY][target]
    pub = WEEK2_PUBLISHED_ALL_DEVIATIONS["latest_pregame"][target]
    got = (lp_all["n_games"], lp_all["toward"], lp_all["away"], lp_all["unchanged"], lp_all["no_close"])
    if got != pub:
        raise SystemExit(f"transcription check failed for {target}: recomputed {got}, published {pub}")
    keep = ("n_games", "below_threshold", "meaningful", "toward", "away", "unchanged", "no_close", "no_view",
            "directional", "toward_rate", "toward_rate_wilson95", "share_closer_to_actual_than_snapshot_market",
            "share_closer_to_actual_than_close", "mean_signed_close_move_points")
    horizons = {"latest_pregame": {**{k: lp.get(k) for k in keep}, "threshold_points": 1.0,
                                   "basis": "recomputed at the preregistered threshold from the report's per-game table"}}
    published = {h: dict(zip(("n_games", "toward", "away", "unchanged", "no_close"), v[target]))
                 for h, v in WEEK2_PUBLISHED_ALL_DEVIATIONS.items()}
    for h, v in published.items():
        d = v["toward"] + v["away"]
        v["toward_rate"] = v["toward"] / d if d else None
    return {"evidence_type": "HYPOTHESIS_GENERATING", "source": SOURCE, "arm": R.DATA_ONLY, "target": target,
            "horizons": horizons, "published_all_deviations_no_threshold": published,
            "note": ("Week 2 generated this hypothesis and can never test it. Three or four directional games is "
                     "a reason to look, not evidence; T-24h pointed the other way for the margin.")}


def evaluation_plan(target: str) -> dict:
    th = HR.PREREGISTERED_THRESHOLDS[HR.KIND_GAME_CENTRE]
    return {"hypothesis": f"when |DATA_ONLY {target} - snapshot market {target}| >= {th['meaningful_deviation_points']} "
                          f"point, the market {target} moves toward DATA_ONLY by the close",
            "arm": R.DATA_ONLY, "target": target, "unit": th["unit"],
            "primary_horizon": th["primary_horizon"], "secondary_horizons_descriptive": th["secondary_horizons"],
            "metric": "toward rate = toward / (toward + away) among games with a meaningful deviation",
            "never_in_denominator": ["unchanged", "no_close", "below threshold"],
            "also_reported": ["per-band counts (<=1, 1-2, 2-3, 3-5, >5)", "share closer to actual than snapshot market",
                              "share closer to actual than close", "mean signed close move toward the arm (points)"],
            "hybrid": "HYBRID_30_DATA reported as derived (0.3 x DATA_ONLY deviation), never counted",
            "evidence_source": "scripts/shadow/arm_report.py deviation_signal, one per week, future window only",
            "decision": "suggestion only; a status change is an owner's transition() call"}


def ensure(registry: str, target: str, now: datetime) -> list:
    hid = f"H2-GC-{target.upper()}-2026W02"
    done = []
    cur = HR.current(registry).get(hid)
    if cur is None:
        HR.add(hid=hid, market_family=f"GAME_CENTRE_{target.upper()}", condition=f"|DATA_ONLY {target} - snapshot market {target}| >= 1.0 point",
               direction="market moves toward DATA_ONLY by the close", expected_mechanism=(
                   "DATA_ONLY carries football information the snapshot market has not yet priced; if so the market "
                   "should drift toward it before kickoff"),
               evaluation_metric="toward rate over toward + away (Wilson, multiplicity-adjusted)",
               minimum_sample=HR.PREREGISTERED_THRESHOLDS[HR.KIND_GAME_CENTRE]["min_directional_observations"],
               generation_window=GENERATION_WINDOW, future_test_window=FUTURE_TEST_WINDOW,
               generated_by="scripts/research/preregister_game_centre_v2.py (week-2 arm report)",
               effect_size=None, uncertainty=None, sample_size=16, game_count=16, candidate_slices_considered=None,
               hypothesis_kind=HR.KIND_GAME_CENTRE,
               locator={"kind": HR.KIND_GAME_CENTRE, "arm": R.DATA_ONLY, "target": target, "primary_horizon": "latest_pregame"},
               generation_evidence=generation_evidence(target), path=registry, now=now)
        done.append(f"{hid}: GENERATED")
        cur = HR.current(registry)[hid]
    if cur["status"] == "GENERATED":
        HR.preregister(hid, test_window=FUTURE_TEST_WINDOW, thresholds=HR.PREREGISTERED_THRESHOLDS,
                       evaluation_plan=evaluation_plan(target), preregistered_at=now,
                       first_test_kickoff_utc=FIRST_TEST_KICKOFF_UTC, path=registry,
                       note="preregistered before the first Week-3 kickoff")
        done.append(f"{hid}: PREREGISTERED")
    return done


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=os.path.join(ROOT, HR.DEFAULT_PATH))
    ap.add_argument("--now", default="", help="ISO time of the preregistration (default: now); must precede the first test kickoff")
    a = ap.parse_args(argv)
    now = HR._parse_ts(a.now) if a.now else datetime.now(timezone.utc)
    done = []
    for target in ("margin", "total"):
        done += ensure(a.registry, target, now)
    print(json.dumps({"registry": a.registry, "wrote": done or "nothing (already preregistered)"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
