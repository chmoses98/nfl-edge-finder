"""Autopsy v2 classifies the first component off in causal order; scorecard v2 clusters by game and never pools evidence classes."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.engines.player import autopsy_v2 as A                                         # noqa: E402
from nfl_edge.evaluation import scorecard_v2 as SC                                          # noqa: E402
from nfl_edge.settlement.results import result_book_from_records                            # noqa: E402

FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "postgame", "dal_phi_2025_w1.results.json")))
GAME = "2026_02_A_H"


def schedule_csv():
    lines = FIX["schedule_csv"].splitlines()
    h = lines[0].split(",")
    row = {k: "" for k in h}
    row.update({"game_id": GAME, "season": "2026", "game_type": "REG", "week": "2", "gameday": "2026-09-13", "gametime": "13:00",
                "away_team": "A", "home_team": "H", "away_score": "20", "home_score": "27", "result": "7", "total": "47", "overtime": "0"})
    return "\n".join([lines[0], ",".join(row[k] for k in h)])


def book(players, snaps):
    rec = {"schedule_csv": schedule_csv(), "players": players, "snaps": snaps, "game_id": GAME, "games_with_player_stats": [GAME], "games_with_snaps": [GAME]}
    return result_book_from_records(rec, min_hours_after_kickoff=0)


def wr(pid, targets, rec_yds, snaps_n, team="H"):
    return ({"player_id": pid, "team": team, "position": "WR", "has_stats_row": True,
             "stats": {"targets": float(targets), "receptions": float(max(1, targets // 2)), "receiving_yards": float(rec_yds), "carries": 0.0, "attempts": 0.0}},
            {"player_id": pid, "team": team, "offense_snaps": float(snaps_n), "defense_snaps": 0.0, "st_snaps": 0.0})


def qb(pid, attempts, team="H"):
    return ({"player_id": pid, "team": team, "position": "QB", "has_stats_row": True, "stats": {"attempts": float(attempts), "passing_yards": 250.0, "carries": 2.0, "targets": 0.0}},
            {"player_id": pid, "team": team, "offense_snaps": 60.0, "defense_snaps": 0.0, "st_snaps": 0.0})


def rec(pid="w1", *, mu=60.0, muo=8.0, tv=34.0, share=0.24, snap=0.85, qb_id="q1", p_plays=0.97, q=None, k=50):
    q = q or {"p025": 5, "p05": 12, "p25": 40, "p50": 58, "p75": 80, "p95": 120, "p975": 140}
    return {"record_id": f"r-{pid}", "snapshot_id": "s", "game_id": GAME, "subject_id": pid, "stat_family": "receiving_yards", "team": "H",
            "model_arm": "DATA_PLAYER_DIST", "threshold": k, "distribution_summary": {"mu": mu, "mu_opp": muo, "quantiles": q},
            "feature_lineage": {"p_plays": p_plays, "availability_state": "EXPECTED_ACTIVE", "projected_team_volume": tv, "projected_share": share,
                                "projected_snap_share": snap, "projected_qb_id": qb_id}}


def _book_with(w_targets=8, w_yards=60, w_snaps=51, qb_att=34, qb_pid="q1"):
    p1, s1 = wr("w1", w_targets, w_yards, w_snaps)
    p2, s2 = qb(qb_pid, qb_att)
    p3, s3 = wr("w2", 6, 40, 50)
    ol = {"player_id": "ol", "team": "H", "offense_snaps": 60.0, "defense_snaps": 0.0, "st_snaps": 0.0}
    return book([p1, p2, p3], [s1, s2, s3, ol])


def test_no_large_miss_when_everything_is_in_range():
    d = A.diagnose(rec(), _book_with())
    assert d["classification"] == A.NO_LARGE_MISS and abs(d["robust_z"]) < 1.5


def test_availability_miss_when_expected_starter_never_played():
    p, s = wr("w1", 0, 0, 0)
    p["stats"] = {"targets": 0.0, "receptions": 0.0, "receiving_yards": 0.0, "carries": 0.0, "attempts": 0.0}
    d = A.diagnose(rec(), book([p], [s]))
    assert d["classification"] == A.AVAILABILITY_MISS


def test_team_volume_miss_when_the_offence_threw_far_less_than_projected():
    d = A.diagnose(rec(tv=34.0, share=0.24), _book_with(w_targets=4, w_yards=20, qb_att=17))
    assert d["classification"] == A.TEAM_VOLUME_MISS


def test_target_share_miss_when_volume_was_right_but_the_share_was_not():
    d = A.diagnose(rec(tv=34.0, share=0.24), _book_with(w_targets=2, w_yards=15, qb_att=34))
    assert d["classification"] == A.TARGET_SHARE_MISS


def test_snap_share_miss_precedes_share_in_the_causal_order():
    d = A.diagnose(rec(snap=0.85), _book_with(w_targets=2, w_yards=10, w_snaps=20, qb_att=34))
    assert d["classification"] == A.SNAP_SHARE_MISS


def test_qb_environment_miss_when_a_different_passer_threw_the_attempts():
    d = A.diagnose(rec(qb_id="q1"), _book_with(w_targets=3, w_yards=15, qb_pid="q9"))
    assert d["classification"] == A.QB_ENVIRONMENT_MISS


def test_efficiency_miss_when_opportunity_landed_but_yards_did_not():
    d = A.diagnose(rec(mu=60.0, muo=8.0), _book_with(w_targets=8, w_yards=15))
    assert d["classification"] == A.YARDS_PER_TARGET_MISS, "receiving yards: the efficiency miss is named by its mechanism"
    # with a frozen catch-rate projection, a catch-rate collapse is named before yards per target
    ctx = {"player_ewma": {"ewma_receptions": 6.0, "ewma_targets": 8.0}}
    p, sn = wr("w1", 8, 15, 51); p["stats"]["receptions"] = 1.0
    d = A.diagnose(rec(mu=60.0, muo=8.0), book([p, qb("q1", 34)[0]], [sn, qb("q1", 34)[1], {"player_id": "ol", "team": "H", "offense_snaps": 60.0, "defense_snaps": 0.0, "st_snaps": 0.0}]), context=ctx)
    assert d["classification"] == A.CATCH_RATE_MISS and d["projected"]["catch_rate"] == 0.75


def test_tail_shape_miss_only_beyond_the_models_own_band():
    d = A.diagnose(rec(), _book_with(w_targets=9, w_yards=200))
    assert d["classification"] in (A.TAIL_SHAPE_MISS, A.YARDS_PER_TARGET_MISS)
    d = A.diagnose(rec(mu=60.0, muo=8.0), _book_with(w_targets=8, w_yards=150))     # eff ratio 18.75/7.5 = 2.5 -> yards per target
    assert d["classification"] == A.YARDS_PER_TARGET_MISS
    # every component in range but the market was much closer to the payout than the model: MODEL_LOCATION_MISS
    r = rec(mu=60.0, muo=8.0, k=50); r["mid"] = 0.15; r["contract_value"] = 0.80
    d = A.diagnose(r, _book_with(w_targets=8, w_yards=48))    # z = (48-58)/29.7 = -0.34, efficiency 6.0 vs 7.5 in range: NO_LARGE_MISS (location needs a large miss)
    assert d["classification"] == A.NO_LARGE_MISS
    r = rec(mu=60.0, muo=8.0, k=50, q={"p025": 30, "p05": 40, "p25": 50, "p50": 58, "p75": 66, "p95": 80, "p975": 90}); r["mid"] = 0.15; r["contract_value"] = 0.80
    d = A.diagnose(r, _book_with(w_targets=8, w_yards=40))    # z = (40-58)/11.9 = -1.5 large; 40 inside [30, 90]; efficiency 5.0 vs 7.5 inside 1.5x
    assert d["classification"] == A.MODEL_LOCATION_MISS


def test_insufficient_data_when_the_record_carries_no_decomposition():
    r = rec(); r["distribution_summary"] = {}
    assert A.diagnose(r, _book_with())["classification"] == A.INSUFFICIENT_DATA


# ---------------------------------------------------------------------------------------------- scorecard
def _row(g, cv, y, mid, cls="PROSPECTIVE_FROZEN", arm="DATA_PLAYER_DIST", **kw):
    r = {"game_id": g, "contract_value": cv, "settled_yes": y, "mid": mid, "evidence_class": cls, "model_arm": arm, "engine": "PLAYER",
         "stat_family": "receiving_yards", "market_family": "PLAYER_STAT", "yes_ask": mid + 0.02, "no_ask": 1 - mid + 0.02, "snapshot_id": "s", "ticker": f"t{g}{cv}{y}"}
    r.update(kw)
    return r


def test_clustered_standard_error_exceeds_naive_when_games_share_a_shock():
    rows = []
    for g in range(20):
        shock = 1.0 if g % 2 == 0 else 0.0
        for j in range(15):
            rows.append(_row(f"g{g}", 0.6, shock, 0.5))
    m = SC.metric_block(rows)
    diffs = [(r["contract_value"] - r["settled_yes"]) ** 2 - (r["mid"] - r["settled_yes"]) ** 2 for r in rows]
    mean = sum(diffs) / len(diffs)
    naive = (sum((d - mean) ** 2 for d in diffs) / (len(diffs) - 1)) ** 0.5 / len(diffs) ** 0.5
    assert m["clusters"] == 20 and m["brier_minus_market_se_clustered"] > naive


def test_historical_and_prospective_rows_are_never_pooled():
    rows = [_row("g1", 0.7, 1.0, 0.5)] * 6 + [_row("g2", 0.1, 1.0, 0.5, cls="HISTORICAL_RESEARCH")] * 6
    sc = SC.build_scorecard(rows, min_segment_n=1)
    assert set(sc["by_evidence_class"]) == {"PROSPECTIVE_FROZEN", "HISTORICAL_RESEARCH"}
    assert sc["by_evidence_class"]["PROSPECTIVE_FROZEN"]["overall"]["brier"] == pytest.approx(0.09)
    assert sc["by_evidence_class"]["HISTORICAL_RESEARCH"]["overall"]["brier"] == pytest.approx(0.81)


def test_executable_block_uses_the_ask_never_the_mid():
    rows = [_row("g1", 0.80, 1.0, 0.50)]          # model 0.80, ask 0.52
    e = SC.executable_block(rows, None, None, edge_min=0.05)
    assert e["n_taken"] == 1 and e["pnl_total"] == pytest.approx(1.0 - 0.52)
    rows = [_row("g1", 0.53, 1.0, 0.50)]          # 3c over the mid but only 1c over the ask: not taken
    assert SC.executable_block(rows, None, None, edge_min=0.05)["n_taken"] == 0


def test_paired_arms_compare_only_common_contracts():
    rows = []
    for i in range(6):
        for arm, cv in (("DATA_PLAYER_DIST", 0.6), ("MARKET_PLAYER_DIST", 0.5)):
            rows.append(_row("g1", cv, 1.0, 0.5, arm=arm, ticker=f"t{i}"))
    rows.append(_row("g1", 0.9, 1.0, 0.5, arm="DATA_PLAYER_DIST", ticker="only-data"))
    pa = SC.paired_arms(rows)
    (k, v), = pa.items()
    assert v["n"] == 6 and v["DATA_PLAYER_DIST"] == pytest.approx(0.16) and v["MARKET_PLAYER_DIST"] == pytest.approx(0.25)
