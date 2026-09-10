"""The arm scorecard: paired only, game-clustered, sample units named, no verdict on a small sample."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.arms import registry as R                                                    # noqa: E402
from nfl_edge.arms.report import render_scorecard                                          # noqa: E402
from nfl_edge.arms.scorecard import (INSUFFICIENT, build_arm_scorecard, cluster_bootstrap, paired_center,  # noqa: E402
                                     paired_contract, views)


def game_row(gid, week, mtk, *, cur=3.0, do=1.0, hy=2.4, actual=4.0, do_status=R.OK, run="r"):
    def arm(m, status):
        return {"status": status, "projected_home_margin": m if status != R.UNAVAILABLE else None,
                "projected_total": 44.0 if status != R.UNAVAILABLE else None, "margin_error": (m - actual) if status != R.UNAVAILABLE else None,
                "margin_abs_error": abs(m - actual) if status != R.UNAVAILABLE else None, "margin_sq_error": (m - actual) ** 2 if status != R.UNAVAILABLE else None,
                "total_error": 1.0 if status != R.UNAVAILABLE else None, "total_abs_error": 1.0 if status != R.UNAVAILABLE else None,
                "total_sq_error": 1.0 if status != R.UNAVAILABLE else None, "p_home_win": 0.6, "home_win_brier": 0.16,
                "margin_minus_market": (m - cur) if status != R.UNAVAILABLE else None, "margin_disagreement_band": "1-2",
                "total_minus_market": 0.0, "total_disagreement_band": "<=1", "margin_movement_vs_close": "toward",
                "total_movement_vs_close": "unchanged", "margin_closer_than_market": True, "total_closer_than_market": False,
                "data_quality_state": status}
    hy_status = R.UNAVAILABLE if do_status == R.UNAVAILABLE else R.OK
    return {"prediction_id": f"{gid}|{run}|{mtk}", "record_kind": "game", "evaluation_version": R.ARM_EVALUATION_VERSION, "run_id": run,
            "game_id": gid, "season": 2026, "week": week, "minutes_to_kickoff": mtk, "observed_at": f"2026-09-1{week}T00:00:00+00:00",
            "record_status": R.OK, "reproduction_ok": True, "actual": {"margin": actual, "total": 45.0},
            "market_at_snapshot": {"margin": cur, "total": 44.0, "margin_error": cur - actual, "total_error": -1.0, "source": "kalshi_implied"},
            "close": {"status": "OK", "margin": 3.5, "total": 44.5, "margin_error": -0.5},
            "arms": {R.CURRENT: arm(cur, R.OK), R.DATA_ONLY: arm(do, do_status), R.HYBRID: arm(hy, hy_status)}}


def contract_row(gid, ticker, mtk, *, settled=1.0, kind="binary", p=(0.6, 0.55, 0.585), run="r"):
    return {"prediction_id": f"{gid}|{ticker}|{run}", "record_kind": "contract", "game_id": gid, "ticker": ticker, "season": 2026, "week": 1,
            "minutes_to_kickoff": mtk, "observed_at": "2026-09-11T00:00:00+00:00", "family": "SPREAD", "arm_status": {a: R.OK for a in R.PRIMARY_ARMS},
            "p_current": p[0], "p_data_only": p[1], "p_hybrid": p[2], "cv_current": p[0], "cv_data_only": p[1], "cv_hybrid": p[2],
            "settlement_status": "SETTLED", "settled_yes": settled, "settlement_kind": kind, "event_binary_valid": kind == "binary",
            "exact_payout_known": True, "mid_t": 0.5, "close_status": "OK", "close_mid": 0.55}


def test_repeated_snapshots_do_not_inflate_the_sample():
    rows = [game_row("g1", 1, m) for m in (1500, 400, 80, 25)] + [game_row("g2", 1, m) for m in (1500, 400)]
    sc = build_arm_scorecard(rows, [])
    assert sc["sample_units"]["raw"]["n_rows"] == 6 and sc["sample_units"]["raw"]["n_games"] == 2
    assert sc["sample_units"]["latest_pregame"]["n_rows"] == 2
    assert sc["sample_units"]["T-24h"]["n_rows"] == 2 and sc["sample_units"]["T-30m"]["n_rows"] == 1
    assert sc["games"]["latest_pregame"]["paired"][0]["n_games"] == 2


def test_no_verdict_below_the_preregistered_game_floor():
    rows = [game_row(f"g{i}", 1 + i // 16, 30) for i in range(R.MIN_GAMES_FOR_VERDICT - 1)]
    sc = build_arm_scorecard(rows, [])
    assert sc["headline_evidence"] == INSUFFICIENT
    md = render_scorecard(sc, title="t")
    assert "INSUFFICIENT EVIDENCE" in md and "winning" not in md.lower().replace("no winning model", "")
    more = rows + [game_row("gX", 5, 30)]
    assert build_arm_scorecard(more, [])["headline_evidence"] != INSUFFICIENT


def test_paired_comparisons_use_only_games_where_both_arms_exist():
    rows = [game_row("g1", 1, 30), game_row("g2", 1, 30, do_status=R.UNAVAILABLE), game_row("g3", 1, 30)]
    p = paired_center(rows, R.DATA_ONLY, R.CURRENT)
    assert p["n_games"] == 2
    cur = build_arm_scorecard(rows, [])["games"]["latest_pregame"]["arms"]
    assert cur[R.CURRENT]["n_games"] == 3 and cur[R.DATA_ONLY]["n_games"] == 2 and cur[R.HYBRID]["n_games"] == 2
    assert cur[R.DATA_ONLY]["status_counts"] == {"OK": 2, "UNAVAILABLE": 1}


def test_a_degraded_current_reproduction_is_excluded_from_pairs():
    rows = [game_row("g1", 1, 30), game_row("g2", 1, 30)]
    rows[0]["reproduction_ok"] = False
    assert paired_center(rows, R.HYBRID, R.CURRENT)["n_games"] == 1


def test_event_and_contract_spaces_stay_separate():
    rows = [contract_row("g1", "A", 30), contract_row("g1", "B", 30, settled=0.5, kind="tie_split"),
            contract_row("g2", "C", 30, settled=0.0)]
    blk = build_arm_scorecard([], rows)["contracts"]["latest_pregame"]
    e, p = blk["arms"][R.CURRENT]["event"], blk["arms"][R.CURRENT]["payout"]
    assert e["n_rows"] == 2 and p["n_rows"] == 3, "a tie-split payout is a payout, not a Bernoulli realisation"
    assert "log_loss" in e and "log_loss" not in p


def test_paired_contract_differences_are_game_clustered_and_deterministic():
    rows = [contract_row("g1", f"A{i}", 30) for i in range(5)] + [contract_row("g2", f"B{i}", 30, settled=0.0) for i in range(5)]
    a = paired_contract(rows, R.DATA_ONLY, R.CURRENT); b = paired_contract(rows, R.DATA_ONLY, R.CURRENT)
    assert a == b
    assert a["event"]["n_contracts"] == 10 and a["event"]["n_games"] == 2
    assert a["event"]["brier_diff"]["bootstrap"]["unit"] == "game"
    bs = cluster_bootstrap([1, 2, 3, 4, 5, 6], ["x", "x", "x", "y", "y", "y"], B=200, seed=1)
    assert bs["n_clusters"] == 2 and bs["se"] is not None


def test_every_block_prints_games_and_weeks_beside_its_numbers():
    rows = [game_row("g1", 1, 30), game_row("g2", 2, 30)]
    sc = build_arm_scorecard(rows, [])
    blk = sc["games"]["latest_pregame"]
    assert blk["n_games"] == 2 and blk["n_weeks"] == 2
    md = render_scorecard(sc, title="t")
    assert "| unit | rows | games | weeks |" in md and "never a sample size" in md


def test_the_scorecard_carries_the_preregistration_and_refuses_to_learn():
    sc = build_arm_scorecard([], [])
    assert sc["preregistration_sha"] == R.preregistration_sha()
    assert "changes no weight" in sc["no_automatic_learning"]


def test_views_never_represent_a_horizon_with_a_later_snapshot():
    rows = [game_row("g1", 1, 20)]                      # only a T-20m snapshot exists
    v = views(rows)
    assert v["T-24h"][0] == [] and v["T-90m"][0] == [] and v["T-30m"][0] == []
    assert len(v["latest_pregame"][0]) == 1
