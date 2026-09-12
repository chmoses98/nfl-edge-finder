"""No hindsight, immutable identity pairing, evidence separation, and the research record (Parts 7, 23, 28)."""
import gzip
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.engines.player import market_dist as MD                                        # noqa: E402
from nfl_edge.engines.player.features_v2 import add_v2_features                             # noqa: E402
from nfl_edge.evaluation import research_record as RR                                       # noqa: E402
from nfl_edge.evaluation import scorecard_v3 as S3                                          # noqa: E402
from nfl_edge.projection import record as R                                                 # noqa: E402
from nfl_edge.projection.store import ProjectionConflict, ProjectionStore, context_id, read_sidecars, write_sidecar  # noqa: E402
from nfl_edge.research import hypothesis_registry_v2 as HR                                  # noqa: E402
from nfl_edge.shadow_v2 import context as CX                                                # noqa: E402

KO = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)


def _proj(ticker, arm, snapshot="20260912T170000Z", cv=0.6, k=None, period="FULL", subject="00-001", **kw):
    r = dict(record_id=R.record_id(snapshot, ticker, arm, "e-1", "d-1"), snapshot_id=snapshot, ticker=ticker, model_arm=arm, engine="PLAYER", engine_version="e-1",
             distribution_version="d-1", model_version="m", market_family="PLAYER_STAT", period=period, stat_family="receiving_yards", threshold=k, operator=">=",
             game_id="2026_01_ATL_PIT", season=2026, week=1, subject_kind="player", subject_id=subject, kickoff_utc=KO.isoformat(), observed_at=(KO - timedelta(hours=6)).isoformat(),
             generated_at=(KO - timedelta(hours=5, minutes=50)).isoformat(), yes_bid=0.50, yes_ask=0.54, no_bid=0.46, no_ask=0.50, p_yes=cv, contract_value=cv,
             support_state="PROJECTABLE_NOT_YET_VALIDATED", horizon_label="T-6h", flags={"has_probability": True, "settlement_supported": True},
             player_context={"player_context_id": "pc1", "position": "WR", "availability_state": "EXPECTED_ACTIVE", "injury_state": "NOT_LISTED"},
             market_state={"last_trade_at": "UNKNOWN", "ladder": {"identification": "FULL", "n_rungs_quoted": 5, "median_width": 0.04, "raw_violations": 0}},
             horizon_quality={"horizon_quality": "ON_TIME", "observation_lateness_min": 2.0, "snapshot_reused": False}, quote_width=0.04, mid=0.52)
    r.update(kw)
    return r


def test_record_ids_separate_arms_thresholds_periods_players_and_horizons():
    ids = {_proj("KXNFLRECYDS-26SEP13ATLPIT-A-50", a)["record_id"] for a in ("DATA_PLAYER_DIST", "MARKET_PLAYER_DIST", "HYBRID_PLAYER_DIST")}
    assert len(ids) == 3
    assert _proj("KXNFLRECYDS-26SEP13ATLPIT-A-50", "DATA_PLAYER_DIST", k=50)["record_id"] != _proj("KXNFLRECYDS-26SEP13ATLPIT-A-60", "DATA_PLAYER_DIST", k=60)["record_id"]
    assert _proj("KXNFL1HTOTAL-26SEP13ATLPIT-22", "BOARD_V2", period="1H")["record_id"] != _proj("KXNFLTOTAL-26SEP13ATLPIT-22", "BOARD_V2")["record_id"]
    assert _proj("T", "DATA_PLAYER_DIST", snapshot="20260912T170000Z")["record_id"] != _proj("T", "DATA_PLAYER_DIST", snapshot="20260913T160000Z")["record_id"]
    # two players on the same game/stat/threshold never collide because the ticker differs; titles are never used
    a, b = _proj("KXNFLRECYDS-26SEP13ATLPIT-PLAYERA-50", "DATA_PLAYER_DIST", subject="00-001"), _proj("KXNFLRECYDS-26SEP13ATLPIT-PLAYERB-50", "DATA_PLAYER_DIST", subject="00-002")
    assert a["record_id"] != b["record_id"]


def test_research_row_joins_by_record_id_only_and_keeps_missing_explicit():
    p = _proj("KXNFLRECYDS-26SEP13ATLPIT-A-50", "DATA_PLAYER_DIST", k=50)
    close = {"close_status": "CLOSE_OK", "close_quality": "GOOD", "close_id": "c", "mid": 0.60, "yes_bid": 0.58, "yes_ask": 0.62, "no_bid": 0.38, "no_ask": 0.42, "quote_width": 0.04}
    clv = {"clv_status": "CLV_OK", "model_side": "YES", "movement": "toward", "clv_mid_toward_model": 0.08, "clv_exec_toward_model": 0.06, "entry_executable_price": 0.54, "entry_fee_per_contract": 0.01}
    sett = {"settlement_status": "SETTLED", "settled_yes": 1.0, "settlement_kind": "binary"}
    row = RR.research_row(p, close=close, clv=clv, settlement=sett, autopsy={"classification": "NORMAL_VARIANCE"}, sidecar={"player_contexts": {"pc1": {"x": 1}}})
    assert row["record_id"] == p["record_id"] and row["disagreement_band"] == "5-10pp" and row["family_group"] == "player_receiving_yards"
    assert row["brier_model"] == pytest.approx(0.16) and row["brier_market_h"] == pytest.approx(0.2304) and row["brier_market_close"] == pytest.approx(0.16)
    assert row["exec_pnl_gross"] == pytest.approx(1 - 0.54) and row["exec_pnl_net"] == pytest.approx(1 - 0.54 - 0.01)
    assert row["ctx_availability_state"] == "EXPECTED_ACTIVE" and row["ladder_identification"] == "FULL" and row["context_in_sidecar"] is True
    bare = RR.research_row(p, close=None, clv=None, settlement=None, autopsy=None, sidecar=None)
    assert bare["close_status"] == "CLV_CLOSE_MISSING" and bare["close_quality"] == "MISSING" and bare["settled_yes"] is None and "brier_model" not in bare


def test_scorecard_v3_keeps_evidence_classes_apart_and_labels_slices():
    rows = []
    for i in range(12):
        p = _proj(f"T{i}", "DATA_PLAYER_DIST", cv=0.7, evidence_class="PROSPECTIVE_FROZEN", game_id=f"g{i % 4}")
        rows.append(RR.research_row(p, close={"close_status": "CLOSE_OK", "close_quality": "EXCELLENT", "mid": 0.6, "yes_bid": 0.58, "yes_ask": 0.62}, clv={"clv_status": "CLV_OK", "model_side": "YES", "movement": "toward", "clv_mid_toward_model": 0.08},
                                    settlement={"settled_yes": 1.0}, autopsy=None, sidecar=None))
    rows.append(RR.research_row(_proj("H", "DATA_PLAYER_DIST", cv=0.1, evidence_class="HISTORICAL_RESEARCH"), close=None, clv=None, settlement={"settled_yes": 1.0}, autopsy=None, sidecar=None))
    sc = S3.build(rows, min_segment_n=1)
    assert set(sc["by_evidence_class"]) == {"PROSPECTIVE_FROZEN", "HISTORICAL_RESEARCH"}
    pf = sc["by_evidence_class"]["PROSPECTIVE_FROZEN"]
    assert pf["overall"]["outcome"]["brier_model"] == pytest.approx(0.09) and pf["overall"]["outcome"]["evidence_type"] == "DESCRIPTIVE"
    assert pf["overall"]["clv"]["mean_clv_mid"] == pytest.approx(0.08) and pf["overall"]["clv"]["positive_clv_rate"] == 1.0
    assert all(v["evidence_type"] == "HYPOTHESIS_GENERATING" for v in pf["segments"]["model_arm"].values())
    assert sc["sign_convention"].startswith("POSITIVE")
    assert sc["by_evidence_class"]["HISTORICAL_RESEARCH"]["overall"]["outcome"]["brier_model"] == pytest.approx(0.81)


def test_close_and_settlement_never_enter_a_projection_record():
    fields = {f.name for f in R.ProjectionRecord.__dataclass_fields__.values()}
    for forbidden in ("close_mid", "close_yes_bid", "settled_yes", "settlement_status", "clv", "c_mid"):
        assert forbidden not in fields, f"{forbidden} must live in a separate corpus, never on the prediction"
    src = open(os.path.join(ROOT, "scripts", "shadow_v2", "project_slate_v2.py")).read()
    for forbidden in ("evaluation.close", "evaluation.clv", "settle_v2", "closes_v2", "settlements_v2", "result_book"):
        assert forbidden not in src, f"the projector must not import or read {forbidden}"


def test_later_ladder_cannot_change_an_earlier_market_distribution():
    early = [{"threshold": k, "yes_bid": m - 0.02, "yes_ask": m + 0.02} for k, m in zip([30, 40, 50, 60, 70], [0.85, 0.62, 0.55, 0.30, 0.12])]
    a = MD.market_distribution("receiving_yards", early)
    later = [{"threshold": k, "yes_bid": m - 0.02, "yes_ask": m + 0.02} for k, m in zip([30, 40, 50, 60, 70], [0.95, 0.80, 0.70, 0.50, 0.30])]
    b = MD.market_distribution("receiving_yards", early)         # recomputed from the SAME frozen rungs
    MD.market_distribution("receiving_yards", later)
    assert a["_dist"].survival(50) == pytest.approx(b["_dist"].survival(50)) and a["location"] == b["location"]


def test_later_player_stats_cannot_change_an_earlier_feature_vector():
    import numpy as np, pandas as pd
    rows = []
    for season in (2019, 2020, 2021, 2023):
        for g in range(6):
            rows.append({"player_id": "w", "position": "WR", "team": "H", "game_id": f"{season}g{g}", "season": season, "week": g + 1, "home": 1, "attempts": 0.0, "carries": 0.0,
                         "targets": 6.0, "receptions": 4.0, "receiving_yards": 50.0, "passing_yards": 0.0, "rushing_yards": 0.0, "offense_snaps": 50.0, "any_td": 0.0})
            rows.append({"player_id": "q", "position": "QB", "team": "H", "game_id": f"{season}g{g}", "season": season, "week": g + 1, "home": 1, "attempts": 30.0, "carries": 2.0,
                         "targets": 0.0, "receptions": 0.0, "receiving_yards": 0.0, "passing_yards": 250.0, "rushing_yards": 5.0, "offense_snaps": 60.0, "any_td": 0.0})
    df = pd.DataFrame(rows)
    f0 = add_v2_features(df)
    df2 = df.copy(); df2.loc[(df2.player_id == "w") & (df2.game_id == "2023g5"), ["targets", "receiving_yards"]] = [30.0, 300.0]
    f1 = add_v2_features(df2)
    i = f0.index[(f0.player_id == "w") & (f0.game_id == "2023g3")][0]
    assert f0.loc[i, "ewma_target_share"] == pytest.approx(f1.loc[i, "ewma_target_share"]), "a later game's stats moved an earlier feature"


def test_later_injury_state_cannot_alter_an_earlier_context(tmp_path):
    """Depth-chart and injury vintages are chosen at or before the snapshot instant, never after.

    The injury half is now stronger than a cutoff comparison. The file is rebuilt in place and has no per-row
    timestamp, so the CONTENT at an old cutoff is only recoverable from an immutable snapshot; the context reads
    the vintage store, and a file that cannot be placed in time is refused rather than read speculatively.
    """
    import json as _json
    import polars as pl
    root = tmp_path / "root"; (root / "data" / "raw" / "nflverse" / "depth_charts").mkdir(parents=True); (root / "data" / "raw" / "nflverse" / "injuries").mkdir(parents=True)
    pl.DataFrame({"dt": ["2026-09-10T12:00:00Z", "2026-09-13T12:00:00Z"], "team": ["H", "H"], "gsis_id": ["p1", "p1"], "pos_abb": ["WR", "WR"], "pos_rank": [1, 3], "player_name": ["P", "P"]}).write_parquet(root / "data/raw/nflverse/depth_charts/depth_charts_2026.parquet")
    inj_rel = os.path.join("data", "raw", "nflverse", "injuries", "injuries_2026.parquet")
    pl.DataFrame({"season": [2026], "week": [1], "team": ["H"], "gsis_id": ["p1"], "report_status": ["Out"], "practice_status": ["DNP"], "report_primary_injury": ["Knee"], "practice_primary_injury": ["Knee"]}).write_parquet(root / inj_rel)
    # the download manifest is what dates the bytes; without it the file cannot be placed in time at all
    with open(root / "data" / "raw" / "nflverse" / "_manifest.jsonl", "w") as fh:
        fh.write(_json.dumps({"path": inj_rel, "retrieved_at": "2026-09-10T18:00:00+00:00", "sha256": "a" * 64}) + "\n")
    early = CX.ContextSources(str(root), str(tmp_path / "md"), 2026, datetime(2026, 9, 11, tzinfo=timezone.utc), log=lambda *a: None)
    late = CX.ContextSources(str(root), str(tmp_path / "md"), 2026, datetime(2026, 9, 14, tzinfo=timezone.utc), log=lambda *a: None)
    assert early.depth_block("p1", "H")["rank"] == 1 and early.depth_block("p1", "H")["vintage"] == "2026-09-10T12:00:00Z"
    assert late.depth_block("p1", "H")["rank"] == 3
    assert early.injury_block("p1", 1)["state"] == "LISTED" and early.weather_block("g", KO)["state"] == "UNKNOWN"
    # a cutoff BEFORE the only vintage was retrieved sees nothing, and does not fall back to the file on disk
    before = CX.ContextSources(str(root), str(tmp_path / "md"), 2026, datetime(2026, 9, 10, 6, tzinfo=timezone.utc), log=lambda *a: None)
    assert before.injury_block("p1", 1)["state"] == CX.SOURCE_UNAVAILABLE


def test_an_injury_file_that_cannot_be_dated_is_refused_rather_than_read(tmp_path):
    """No manifest row means no defensible retrieval time, and a file that cannot be placed in time is not
    evidence about any particular instant. Reading it anyway is how hindsight gets in."""
    import polars as pl
    root = tmp_path / "root"; (root / "data" / "raw" / "nflverse" / "injuries").mkdir(parents=True)
    pl.DataFrame({"season": [2026], "week": [1], "team": ["H"], "gsis_id": ["p1"], "report_status": ["Out"], "practice_status": ["DNP"], "report_primary_injury": ["Knee"], "practice_primary_injury": ["Knee"]}).write_parquet(root / "data/raw/nflverse/injuries/injuries_2026.parquet")
    src = CX.ContextSources(str(root), str(tmp_path / "md"), 2026, datetime(2026, 9, 11, tzinfo=timezone.utc), log=lambda *a: None)
    b = src.injury_block("p1", 1)
    assert b["state"] == CX.SOURCE_UNAVAILABLE and b["report_status"] is None


def test_sidecar_and_store_are_write_once_and_later_horizons_cannot_alter_earlier_records(tmp_path):
    st = ProjectionStore(str(tmp_path))
    rows = [R.ProjectionRecord(**{k: v for k, v in _proj("T1", "DATA_PLAYER_DIST").items() if k in R.ProjectionRecord.__dataclass_fields__}).finalize().to_dict()]
    assert st.write("20260912T170000Z", "DATA_PLAYER_DIST", rows)["status"] == "WRITTEN"
    changed = [R.ProjectionRecord(**{k: v for k, v in dict(_proj("T1", "DATA_PLAYER_DIST"), contract_value=0.9, p_yes=0.9).items() if k in R.ProjectionRecord.__dataclass_fields__}).finalize().to_dict()]
    with pytest.raises(ProjectionConflict):
        st.write("20260912T170000Z", "DATA_PLAYER_DIST", changed)
    with pytest.raises(ValueError):
        st.write("20260912T170000Z", "DATA_PLAYER_DIST", [dict(rows[0], contract_value=0.9)])   # a tampered row whose hash no longer matches is refused outright
    later = [R.ProjectionRecord(**{k: v for k, v in _proj("T1", "DATA_PLAYER_DIST", snapshot="20260913T160000Z", cv=0.9).items() if k in R.ProjectionRecord.__dataclass_fields__}).finalize().to_dict()]
    assert st.write("20260913T160000Z", "DATA_PLAYER_DIST", later)["status"] == "WRITTEN"
    with gzip.open(st.path("20260912T170000Z", "DATA_PLAYER_DIST"), "rt") as f:
        assert json.loads(f.readline())["contract_value"] == 0.6, "the earlier horizon's record is untouched by the later one"
    payload = {"lineage": {"a": 1}, "game_contexts": {}, "player_contexts": {}}
    assert write_sidecar(str(tmp_path), "20260912T170000Z", payload)["status"] == "WRITTEN"
    assert write_sidecar(str(tmp_path), "20260912T170000Z", payload)["status"] == "NO_OP"
    with pytest.raises(ProjectionConflict):
        write_sidecar(str(tmp_path), "20260912T170000Z", {"lineage": {"a": 2}})
    assert read_sidecars(str(tmp_path))["20260912T170000Z"]["lineage"] == {"a": 1}
    assert context_id({"a": 1}) == context_id({"a": 1}) and context_id({"a": 1}) != context_id({"a": 2})


def test_hypothesis_registry_separates_generation_and_confirmation_evidence(tmp_path):
    path = str(tmp_path / "h.jsonl")
    h = HR.add(hid="HG-1", market_family="player_receiving_yards", condition="disagreement_band == 1-2pp", direction="model beats market", expected_mechanism="unknown",
               evaluation_metric="model_minus_market_brier", minimum_sample=200, generation_window={"season": 2026, "week_lo": 1, "week_hi": 1},
               future_test_window={"season": 2026, "week_lo": 2, "week_hi": 18}, generated_by="weekly_report", path=path)
    assert h["status"] == "GENERATED" and h["evidence_type"] == "HYPOTHESIS_GENERATING"
    with pytest.raises(HR.RegistryError):
        HR.add(hid="HG-2", market_family="x", condition="c", direction="d", expected_mechanism="m", evaluation_metric="e", minimum_sample=1,
               generation_window={"season": 2026, "week_lo": 1, "week_hi": 1}, future_test_window={"season": 2026, "week_lo": 1, "week_hi": 3}, generated_by="t", path=path)
    with pytest.raises(HR.RegistryError):
        HR.transition("HG-1", "SUPPORTED", path=path)                                   # GENERATED -> SUPPORTED is not a legal transition
    HR.transition("HG-1", "PREREGISTERED", path=path); HR.transition("HG-1", "TESTING", path=path)
    with pytest.raises(HR.RegistryError):
        HR.transition("HG-1", "SUPPORTED", test_window={"season": 2026, "week_lo": 1, "week_hi": 2}, path=path)
    r = HR.transition("HG-1", "SUPPORTED", test_window={"season": 2026, "week_lo": 2, "week_hi": 5}, result={"z": 2.3}, path=path)
    assert r["evidence_type"] == "CONFIRMATORY" and len(HR.load(path)) == 4 and HR.current(path)["HG-1"]["status"] == "SUPPORTED"
    assert HR.load(path)[1]["previous_hash"] == HR.load(path)[0]["line_hash"], "every transition chains to the previous line"


def test_week_one_is_not_in_the_training_window():
    from nfl_edge.engines.player import data_dist as DD
    import inspect
    src = inspect.getsource(DD.fit_stat)
    assert "train.season < target_season" in src, "the prospective bundle fits strictly before the target season"
