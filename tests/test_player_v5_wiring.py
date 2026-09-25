"""DATA_PLAYER_V5 / HYBRID_PLAYER_V5 in production: arm registration, fail-soft build, lean records, RUN NFL display,
eligibility (RESEARCH_ONLY by design), autopsy. Every existing arm stays exactly where and what it was."""
from __future__ import annotations

import json

import pytest

import scripts.shadow_v2.project_slate_v2 as P
from nfl_edge.engines.player import v4 as V4
from nfl_edge.engines.player import v5 as V5
from nfl_edge.projection import lean as LEAN
from test_player_v4 import _full_record, _row


# ------------------------------------------------------------------------------------------------ registration
def test_v5_arms_are_appended_after_every_existing_arm():
    assert P.PLAYER_ARMS[:7] == ("DATA_PLAYER_DIST", "MARKET_PLAYER_DIST", "HYBRID_PLAYER_DIST", "DATA_PLAYER_V3", "HYBRID_PLAYER_V3",
                                 "DATA_PLAYER_V4", "HYBRID_PLAYER_V4")
    assert P.PLAYER_ARMS[7:] == ("DATA_PLAYER_V5", "HYBRID_PLAYER_V5") == P.V5_ARMS
    assert P.V4_ARMS == ("DATA_PLAYER_V4", "HYBRID_PLAYER_V4")
    from nfl_edge.projection import record as R
    ids = {R.record_id("snap", "T", arm, v, "lattice-1.0.0") for arm, v in
           (("DATA_PLAYER_V4", V4.VERSION), ("HYBRID_PLAYER_V4", V4.HYBRID_VERSION), ("DATA_PLAYER_V5", V5.VERSION), ("HYBRID_PLAYER_V5", V5.HYBRID_VERSION))}
    assert len(ids) == 4


def test_eligibility_keeps_v5_research_only_whatever_a_short_sample_says():
    from nfl_edge.evaluation import eligibility as EL
    assert "DATA_PLAYER_V5" in EL.RESEARCH_BY_DESIGN and "HYBRID_PLAYER_V5" in EL.RESEARCH_BY_DESIGN
    assert "DATA_PLAYER_V5" not in EL.KNOWN_DEFECTS
    # a strong-looking short sample (below the >= 48 games / >= 3 weeks every RESEARCH_BY_DESIGN arm must first reach)
    m = {"arm": "DATA_PLAYER_V5", "family": "ALL", "n_games": 40, "n_weeks": 2, "delta_brier_game_mean": -0.01, "delta_brier_se": 0.001,
         "delta_brier_upper95": -0.008, "z": -10.0, "ece": 0.01, "clv_game_mean": 0.02, "clv_se": 0.001, "sync_share": 1.0,
         "close_quality_share": 1.0, "pnl_net_game_mean": 0.01, "pnl_net_se": 0.001}
    st, _ = EL.decide(m)
    assert st == EL.RESEARCH_ONLY
    doc = EL.build(EL.Accumulator(), as_of="2026-09-24T00:00:00Z", sources=[])
    assert doc["arms"]["DATA_PLAYER_V5"] == "RESEARCH_ONLY" and doc["arms"]["HYBRID_PLAYER_V5"] == "RESEARCH_ONLY"
    assert EL.status_for({"arms": {}, "families": {}}, "DATA_PLAYER_V5", "player_receptions")["status"] == "RESEARCH_ONLY"
    from nfl_edge.handicap.packet import eligibility_summary
    s = eligibility_summary(None)
    assert s["arms"]["DATA_PLAYER_V5"] == "RESEARCH_ONLY" and s["arms"]["HYBRID_PLAYER_V5"] == "RESEARCH_ONLY"


# ------------------------------------------------------------------------------------------------ RUN NFL
def test_run_nfl_shows_v5_as_labelled_research_beside_v3_and_v4():
    import nfl_edge.handicap.shadow_v2_block as SV2
    doc = {"arms": {"MARKET_PLAYER_DIST": "WATCH"}, "families": {}}
    promoted = {"state": "ABSTAIN_MODEL_UNVALIDATED", "qb_resolution": {"qb_resolution_reason": "QB1_OUT_PROMOTED_NEXT",
                                                                         "effective_projected_qb": "00-cousins", "qb_resolution_certainty": "MEDIUM"}}
    arms = {"MARKET_PLAYER_DIST": _row("MARKET_PLAYER_DIST", 0.41), "DATA_PLAYER_V3": _row("DATA_PLAYER_V3", 0.47),
            "DATA_PLAYER_V4": _row("DATA_PLAYER_V4", 0.52), "HYBRID_PLAYER_V4": _row("HYBRID_PLAYER_V4", 0.43),
            "DATA_PLAYER_V5": _row("DATA_PLAYER_V5", 0.38, abstention=promoted), "HYBRID_PLAYER_V5": _row("HYBRID_PLAYER_V5", 0.40)}
    b = SV2.market_view(arms, {}, eligibility=doc)
    assert b["primary_arm"] == "DATA_PLAYER_V3" and b["eligibility"] == "RESEARCH_ONLY"
    v5 = b["other_arms"]["DATA_PLAYER_V5"]
    assert v5["eligibility"] == "RESEARCH_ONLY" and v5["p_yes"] == 0.38 and "research" in v5["research_arm"]
    assert v5["qb_resolution"] == {"reason": "QB1_OUT_PROMOTED_NEXT", "effective_projected_qb": "00-cousins", "certainty": "MEDIUM"}
    h5 = b["other_arms"]["HYBRID_PLAYER_V5"]
    assert h5["market_derived"] is True and h5["eligibility"] == "RESEARCH_ONLY" and "qb_resolution" not in h5
    # V4's view is exactly what it was
    assert "research_arm" not in b["other_arms"]["DATA_PLAYER_V4"] and "qb_resolution" not in b["other_arms"]["DATA_PLAYER_V4"]
    # V5 is never promoted into the primary slot over v3 or v4
    assert SV2.market_view({"DATA_PLAYER_V4": arms["DATA_PLAYER_V4"], "DATA_PLAYER_V5": arms["DATA_PLAYER_V5"]}, {}, eligibility=doc)["primary_arm"] == "DATA_PLAYER_V4"


# ------------------------------------------------------------------------------------------------ lean records
QB = {"depth_chart_qb1": "00-penix", "effective_projected_qb": "00-cousins", "qb_availability_state": "OUT",
      "qb_resolution_reason": "QB1_OUT_PROMOTED_NEXT", "qb_resolution_certainty": "MEDIUM"}


def test_v5_lean_records_keep_the_quarterback_resolution_and_v4_lean_is_unchanged():
    full = _full_record()
    v5 = dict(full, model_arm="DATA_PLAYER_V5", player_context={**full["player_context"], **LEAN.v5_qb_fields(QB)},
              feature_lineage={"snap_mean": 0.8, **QB})
    ln = LEAN.lean(v5, intermediates=True, data_arm="DATA_PLAYER_V5", context_keep=LEAN.PLAYER_CONTEXT_KEEP_V5)
    assert {k: ln["player_context"][k] for k in LEAN.V5_QB_FIELDS} == QB and ln["feature_lineage"]["effective_projected_qb"] == "00-cousins"
    hy = LEAN.lean(dict(v5, model_arm="HYBRID_PLAYER_V5"), intermediates=False, data_arm="DATA_PLAYER_V5", context_keep=LEAN.PLAYER_CONTEXT_KEEP_V5)
    assert hy["feature_lineage"]["qb_resolution_reason"] == "QB1_OUT_PROMOTED_NEXT" and "snap_mean" not in hy["feature_lineage"]
    assert hy["feature_lineage"]["intermediates"] == "DATA_PLAYER_V5 record, same snapshot and ticker"
    # V4 with the defaults: identical to main (no QB fields kept, the same reference string)
    v4 = LEAN.lean(dict(full, player_context={**full["player_context"], **QB}))
    assert not set(LEAN.V5_QB_FIELDS) & set(v4["player_context"])
    v4h = LEAN.lean(dict(full, model_arm="HYBRID_PLAYER_V4", feature_lineage={"snap_mean": 1, **QB}), intermediates=False)
    assert v4h["feature_lineage"] == {"intermediates": "DATA_PLAYER_V4 record, same snapshot and ticker"}
    assert LEAN.PLAYER_CONTEXT_KEEP == ("player_context_id", "position", "team", "availability_state", "injury_state", "injury_report_maturity",
                                        "injury_report_rows_for_week", "role_certainty", "role_class", "depth_chart_rank", "depth_chart_group_rank",
                                        "weather_state", "official_inactive_state", "official_inactive_observed_at", "team_pass_attempts",
                                        "qb_depth_chart", "qb_schedule")


# ------------------------------------------------------------------------------------------------ fail-soft
class _Q:
    kind, k, op = "THRESHOLD", 4.0, ">="


def _arms_with_v4():
    from nfl_edge.engines.player.dist import LatticeDistribution
    import numpy as np
    pa = P.PlayerArms()
    pa.identity = {"kid": ("00-x", "RESOLVED")}
    pmf = np.full(11, 1 / 11)
    pa.data_v4 = {("00-x", "g", "receptions"): LatticeDistribution(pmf, meta={"mu": 5.0})}
    pa.feat_v4 = {("00-x", "g"): {"snap_mean": 0.8}}
    return pa


def test_a_v5_failure_refuses_v5_and_costs_nothing_else(monkeypatch):
    pa = _arms_with_v4()
    q = {"player_kalshi_id": "kid", "game_id": "g", "stat": "receptions"}
    before = json.dumps(pa.answer("DATA_PLAYER_V4", "T", q, _Q())[0], sort_keys=True, default=str)
    boom = []
    monkeypatch.setattr(P.PV5, "build", lambda *a, **k: boom.append(1) or (_ for _ in ()).throw(RuntimeError("synthetic v5 failure")))

    class A:
        target_season = 2026
    P.build_player_v5(pa, A(), [], {}, None, {}, {}, {}, None, None, None, {}, {}, log=lambda *a: None)
    assert boom and pa.v5_info["error"].startswith("RuntimeError") and pa.data_v5 == {}
    ans, lineage, feat, _ = pa.answer("DATA_PLAYER_V5", "T", q, _Q())
    assert ans["p_yes"] is None and "v5 build failed" in ans["reason"] and "every other arm is unaffected" in ans["reason"]
    assert json.dumps(pa.answer("DATA_PLAYER_V4", "T", q, _Q())[0], sort_keys=True, default=str) == before
    assert set(pa.data_v4) == {("00-x", "g", "receptions")}


def test_v5_answer_carries_the_resolved_quarterback_for_the_autopsy():
    from nfl_edge.engines.player.dist import LatticeDistribution
    import numpy as np
    pa = _arms_with_v4()
    pa.data_v5 = {("00-x", "g", "receptions"): LatticeDistribution(np.full(11, 1 / 11), meta={"mu": 5.0})}
    pa.feat_v5 = {("00-x", "g"): {"snap_mean": 0.8, **QB}}
    ans, lineage, feat, s = pa.answer("DATA_PLAYER_V5", "T", {"player_kalshi_id": "kid", "game_id": "g", "stat": "receptions"}, _Q())
    assert ans["p_yes"] is not None and feat["projected_qb_id"] == "00-cousins" and feat["inputs_version"] == V5.INPUTS_VERSION
    assert lineage["family"] == "v5-structural"
    h, _, hf, _ = pa.answer("HYBRID_PLAYER_V5", "T", {"player_kalshi_id": "kid", "game_id": "g", "stat": "receptions"}, _Q())
    assert h["p_yes"] is None and "hybrid unavailable" in h["reason"]            # no market ladder in this fixture


def test_autopsy_reads_v5_through_the_lean_path():
    from nfl_edge.engines.player import autopsy_v2 as AU
    assert AU.AUTOPSY_ARMS[:3] == ("DATA_PLAYER_DIST", "DATA_PLAYER_V3", "DATA_PLAYER_V4") and AU.AUTOPSY_ARMS[3] == "DATA_PLAYER_V5"
    assert "HYBRID_PLAYER_V5" not in AU.AUTOPSY_ARMS


def test_the_projector_builds_v5_after_v4_and_fail_soft():
    import inspect
    src = inspect.getsource(P.build_player_arms)
    assert src.index("PV4.build(") < src.index("build_player_v5(")
    body = inspect.getsource(P.build_player_v5)
    assert "except Exception" in body and "P.v5_info" in body


@pytest.mark.parametrize("arm", ["DATA_PLAYER_V5", "HYBRID_PLAYER_V5"])
def test_v5_engine_versions_are_mapped(arm):
    import inspect
    src = inspect.getsource(P)
    assert f"ARM_{arm.split('_')[0]}_V5: V5." in src
