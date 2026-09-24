"""Player context, end to end, and the V4 data arm in the autopsy.

Three things the Week-2 audit found with no test behind them:

  1. NOTHING TESTED THE WHOLE PATH. Role context was unit-tested at the chart (test_role_context.py) and the health
     gate was tested on hand-written rows, but no test followed an ESPN-format depth chart through the frozen player
     context, its compact form on the record, the research row and the slim row into `weekly_report_v2.health()`.
     That is the path that read 0% for a season's first weeks when the chart never reached the runner, and a unit
     test on either end would not have noticed.
  2. A BARE 0% READ AS A FAULT. 2026 Week 2 reports 0% depth and 0% role, correctly: its records were frozen before
     context-1.3.0 (#39) loaded a chart at all. The gate now says so, and still calls a 1.3.0 record with no chart
     placement a fault.
  3. DATA_PLAYER_V4 WAS NEVER AUTOPSIED. The settle loop and the health gate named v2 and v3 only. V4 is a data arm
     like them and joins them; HYBRID_PLAYER_V4 stays out exactly as HYBRID_PLAYER_V3 does, and V4 stays
     RESEARCH_ONLY -- this changes what is diagnosed, never what is eligible.

Deterministic, in memory or under tmp_path, no network.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "shadow_v2"))

from nfl_edge.context import role as RO                                           # noqa: E402
from nfl_edge.engines.player import autopsy_v2 as A                               # noqa: E402
from nfl_edge.evaluation import eligibility as EL                                 # noqa: E402
from nfl_edge.evaluation.research_record import research_row                      # noqa: E402
from nfl_edge.evaluation.research_slim import slim                                # noqa: E402
from nfl_edge.shadow_v2 import context as CX                                      # noqa: E402

import weekly_report_v2 as WR                                                     # noqa: E402
from test_autopsy_and_scorecard_v2 import GAME, _book_with                        # noqa: E402
from test_role_context import espn_rows                                           # noqa: E402

CUTOFF = datetime(2026, 9, 20, 17, 0, tzinfo=timezone.utc)      # Sunday morning: the Saturday (T1) chart is newest
KICKOFF = datetime(2026, 9, 20, 17, 25, tzinfo=timezone.utc)
KC_GAME = "2026_02_KC_BUF"
PLAYERS = (("00-QB1", "QB", {"last_snap_share": 1.0, "n_cur_season": 1, "last_team": "KC"}),
           ("00-WR1", "WR", {"last_snap_share": 0.9, "n_cur_season": 1, "last_team": "KC"}),
           ("00-RB2", "RB", {"last_snap_share": 0.55, "n_cur_season": 1, "last_team": "KC"}),
           ("00-TE1", "TE", {"last_snap_share": 0.8, "n_cur_season": 1, "last_team": "KC"}))


def sources(tmp_path, *, with_chart=True):
    if with_chart:
        p = tmp_path / "data" / "raw" / "nflverse" / "depth_charts"
        p.mkdir(parents=True)
        espn_rows().write_parquet(p / "depth_charts_2026.parquet")
    return CX.ContextSources(str(tmp_path), str(tmp_path / "md"), 2026, CUTOFF, log=lambda *a: None)


def projection(gsis, compact, *, arm="DATA_PLAYER_V3"):
    return {"record_id": f"rec-{gsis}-{arm}", "snapshot_id": "20260920T170000Z", "ticker": f"KXNFLREC-{gsis}", "model_arm": arm,
            "engine": "PLAYER", "market_family": "PLAYER_STAT", "stat_family": "receiving_yards", "game_id": KC_GAME,
            "season": 2026, "week": 2, "kickoff_utc": KICKOFF.isoformat(), "subject_id": gsis, "p_yes": 0.5,
            "contract_value": 0.5, "mid": 0.48, "player_context": compact}


def rows_through_the_real_path(src):
    """chart -> frozen player context -> compact context on the record -> research row -> slim row."""
    out = []
    for gsis, pos, feat in PLAYERS:
        full = CX.player_context(src, gsis=gsis, team="KC", week=2, game_id=KC_GAME, kickoff=KICKOFF, feat_row=feat,
                                 avail=None, position=pos)
        cid = f"pc-{gsis}"
        compact = CX.compact_player_context(full, cid)
        rr = research_row(projection(gsis, compact), close=None, clv=None, settlement=None, autopsy=None,
                          sidecar={"player_contexts": {cid: full}})
        out.append(slim(json.loads(json.dumps(rr, default=str))))       # through JSON, as the export writes it
    return out


def rendered_counts(pc: dict) -> str:
    """What the report's coverage table prints in the counts column for this gate (render(): non-pct keys, 300 chars)."""
    return json.dumps({k: v for k, v in pc.items() if "pct" not in k}, default=str)[:300]


# ------------------------------------------------------------------ 1. end to end: the chart reaches the health gate
def test_a_real_format_depth_chart_reaches_the_health_gate_with_depth_and_role_coverage(tmp_path):
    rows = rows_through_the_real_path(sources(tmp_path))
    assert all(r.get("player_context_version") == CX.CONTEXT_VERSION for r in rows)
    pc = WR.health(rows, [], [], 2026, 2)["PLAYER_CONTEXT_COVERAGE"]
    assert pc["player_probability_rows"] == len(PLAYERS)
    assert pc["depth_chart_known_pct"] == 100.0, pc
    assert pc["role_known_pct"] > 0, pc
    assert pc["role_context"] == "LOADED"
    # the Saturday promotion is what the record froze, not Wednesday's chart and not Monday's
    rb2 = next(r for r in rows if r.get("record_id", "").startswith("rec-00-RB2"))
    assert rb2.get("ctx_depth_chart_rank") == 1


def test_the_same_path_without_a_chart_is_a_fault_not_history(tmp_path):
    """A 1.3.0 record whose runner had no depth file must never be excused as 'predates role context'."""
    rows = rows_through_the_real_path(sources(tmp_path, with_chart=False))
    pc = WR.health(rows, [], [], 2026, 2)["PLAYER_CONTEXT_COVERAGE"]
    assert pc["depth_chart_known_pct"] == 0.0 and pc["role_known_pct"] == 0.0
    assert pc["role_context"].startswith("NO_PLACEMENT"), pc["role_context"]
    assert set(pc["role_certainty"]) <= {RO.LOW, RO.UNKNOWN}


# ------------------------------------------------------------------ 2. the Week-2 zero is labelled as history
def pre_role_row(i, *, version="context-1.2.0"):
    """A research row as the pre-#39 context wrote it: no depth rank, and no role keys on the compact context."""
    compact = {"player_context_id": f"pc-{i}", "position": "WR", "team": "KC", "availability_state": "EXPECTED_ACTIVE",
               "injury_state": "NOT_LISTED_AT_THIS_VINTAGE", "injury_report_maturity": "MATURE", "depth_chart_rank": None,
               "weather_state": "KNOWN"}
    sidecar = {"player_contexts": {f"pc-{i}": {"context_version": version}}} if version else None
    rr = research_row(projection(f"p{i}", compact), close=None, clv=None, settlement=None, autopsy=None, sidecar=sidecar)
    return slim(json.loads(json.dumps(rr, default=str)))


def test_week_2_zero_coverage_says_the_records_predate_role_context():
    rows = [pre_role_row(i) for i in range(5)]
    pc = WR.health(rows, [], [], 2026, 2)["PLAYER_CONTEXT_COVERAGE"]
    assert pc["depth_chart_known_pct"] == 0.0 and pc["role_known_pct"] == 0.0     # the history is not rewritten
    assert pc["role_context"].startswith("PREDATES_ROLE_CONTEXT")
    assert "context-1.3.0" in pc["role_context"] and "#39" in pc["role_context"]
    # and the report's table actually prints it (the counts column is cut at 300 characters)
    assert "PREDATES_ROLE_CONTEXT" in rendered_counts(pc)


def test_without_a_sidecar_the_missing_role_certainty_is_the_evidence():
    rows = [pre_role_row(i, version=None) for i in range(3)]
    assert all(r.get("player_context_version") is None for r in rows)
    assert CX.role_context_note(rows).startswith("PREDATES_ROLE_CONTEXT")


def test_a_mixed_week_is_loaded_and_counts_the_rows_that_predate(tmp_path):
    rows = rows_through_the_real_path(sources(tmp_path)) + [pre_role_row(i) for i in range(2)]
    note = CX.role_context_note(rows)
    assert note.startswith("LOADED") and "2 of 6 rows predate" in note


def test_version_comparison_is_numeric():
    assert CX.predates_role_context({"player_context_version": "context-1.2.9", "ctx_role_certainty": "HIGH"})
    assert not CX.predates_role_context({"player_context_version": "context-1.3.0"})
    assert not CX.predates_role_context({"player_context_version": "context-1.10.0"})
    assert CX.role_context_note([]) is None


# ------------------------------------------------------------------ 3. DATA_PLAYER_V4 is autopsied like v2 / v3
def v4_rec(*, snap=0.85, vol_pa=34.0, share_t=0.24, mu=60.0, mu_targets=8.0, q=None, arm="DATA_PLAYER_V4"):
    """A LEAN V4 record as projection/lean.py writes it: the model's own intermediate names, p05 / p50 / p95 only."""
    q = q or {"p05": 12, "p50": 58, "p95": 120}
    # `team` at the top level is what settle_v2 adds from the feature lineage before it calls diagnose
    return {"record_id": "r-v4", "snapshot_id": "s", "game_id": GAME, "subject_id": "w1", "stat_family": "receiving_yards", "team": "H",
            "model_arm": arm, "threshold": 50, "distribution_summary": {"mu": mu, "quantiles": q},
            "feature_lineage": {"p_plays": 0.97, "availability_state": "EXPECTED_ACTIVE", "team": "H", "pgroup": "WR",
                                "snap_mean": snap, "vol_pa": vol_pa, "vol_ra": 25.0, "share_t": share_t, "share_c": None,
                                "mu_targets": mu_targets, "mu_carries": None, "qb_starter": False, "inputs_version": "player-inputs-4.0.0"}}


def test_v4_is_an_autopsy_arm_and_no_hybrid_is():
    assert "DATA_PLAYER_V4" in A.AUTOPSY_ARMS
    assert not any(a.startswith(("HYBRID_", "MARKET_")) for a in A.AUTOPSY_ARMS)
    settle = open(os.path.join(ROOT, "scripts", "shadow_v2", "settle_v2.py")).read()
    assert 'r.get("model_arm") in AU.AUTOPSY_ARMS' in settle, "the settle loop must autopsy exactly AU.AUTOPSY_ARMS"


def test_v4_stays_research_only_by_design():
    assert "DATA_PLAYER_V4" in EL.RESEARCH_BY_DESIGN and "HYBRID_PLAYER_V4" in EL.RESEARCH_BY_DESIGN


def test_the_health_gate_counts_settled_v4_rows_and_not_the_v4_hybrid():
    rows = [{"model_arm": arm, "ticker": f"T-{arm}", "contract_value": 0.5, "settled_yes": 1, "engine": "PLAYER"}
            for arm in ("DATA_PLAYER_DIST", "DATA_PLAYER_V3", "DATA_PLAYER_V4", "HYBRID_PLAYER_V3", "HYBRID_PLAYER_V4")]
    assert WR.health(rows, [], [], 2026, 2)["AUTOPSY_COVERAGE"]["data_arm_settled"] == 3


def test_a_v4_record_in_range_is_no_large_miss_not_insufficient_data():
    d = A.diagnose(v4_rec(), _book_with())
    assert d["projected"]["snap_share"] == 0.85 and d["projected"]["team_volume"] == 34.0
    assert d["projected"]["share"] == 0.24 and d["projected"]["opportunity"] == 8.0
    assert d["robust_z"] is not None and d["classification"] == A.NO_LARGE_MISS


def test_a_v4_team_volume_miss_is_found_through_its_own_names():
    tight = {"p05": 38, "p50": 58, "p95": 80}
    d = A.diagnose(v4_rec(q=tight), _book_with(w_targets=4, w_yards=20, qb_att=17))
    assert d["large_miss"] and d["classification"] == A.TEAM_VOLUME_MISS


def test_the_v4_adapter_never_touches_another_arm():
    """The adapter is keyed on the arm: a v3 record with the same lean names is read exactly as before."""
    d = A.diagnose(v4_rec(arm="DATA_PLAYER_V3"), _book_with())
    assert d["projected"]["snap_share"] is None and d["robust_z"] is None
