"""Arm evaluation records: verbatim pregame values, strictly pregame closes, movement toward the close."""
from nfl_edge.arms import evaluation as AE, registry as R
from nfl_edge.settlement.results import GameResult


class Book:
    def __init__(self, g):
        self.games = {g.game_id: g}
    def final_verdict(self, gid):
        return None


def game():
    g = GameResult(game_id="G", season=2026, week=2, home_team="H", away_team="A", home_score=27, away_score=20, overtime=0,
                   kickoff_utc="2026-09-13T17:00:00+00:00", status="FINAL", source="test", final_proofs=["postgame_tables"])
    return g


def rec(cur=(3.0, 44.5), do=(1.0, 48.0), do_status=R.OK):
    def arm(arm_id, m, t, status=R.OK):
        return {"arm_id": arm_id, "status": status, "projected_home_margin": m, "projected_total": t, "simulation_center_margin": m,
                "simulation_center_total": t, "implied_home_score": (t + m) / 2, "implied_away_score": (t - m) / 2,
                "center_source": "x", "data_quality_state": status, "simulation": {"p_home_win": 0.6, "p_tie": 0.001}}
    hm, ht = 0.7 * cur[0] + 0.3 * do[0], 0.7 * cur[1] + 0.3 * do[1]
    return {"record_id": "rid", "arms_version": R.ARMS_VERSION, "run_id": "r", "observed_at": "2026-09-12T17:00:00+00:00",
            "minutes_to_kickoff": 1440.0, "game_id": "G", "season": 2026, "week": 2, "home_team": "H", "away_team": "A",
            "kickoff_at": "2026-09-13T17:00:00+00:00", "prekickoff": True, "status": R.OK, "reproduction_check": {"ok": True},
            "arms": {R.CURRENT: arm(R.CURRENT, *cur), R.DATA_ONLY: arm(R.DATA_ONLY, *do, do_status),
                     R.HYBRID: arm(R.HYBRID, hm, ht, do_status)}}


def test_centre_errors_and_movement_toward_the_close():
    ev = AE.evaluate_game(rec(), game(), {"status": "OK", "margin": 2.0, "total": 46.0})
    a = ev["arms"]
    assert a[R.CURRENT]["margin_error"] == 3.0 - 7 and a[R.DATA_ONLY]["margin_error"] == 1.0 - 7
    assert a[R.DATA_ONLY]["margin_minus_market"] == -2.0 and a[R.DATA_ONLY]["margin_disagreement_band"] == "1-2"
    # DATA_ONLY moved the margin DOWN from the market (3 -> 1); the close moved down too (3 -> 2): toward
    assert a[R.DATA_ONLY]["margin_movement_vs_close"] == "toward"
    # DATA_ONLY moved the total UP (44.5 -> 48); the close moved up (44.5 -> 46): toward; actual 47 -> data closer
    assert a[R.DATA_ONLY]["total_movement_vs_close"] == "toward" and a[R.DATA_ONLY]["total_closer_than_market"] is True
    assert a[R.DATA_ONLY]["margin_closer_than_market"] is False           # market 3 is closer to 7 than 1 is
    assert ev["close"]["margin_error"] == 2.0 - 7 and ev["actual"]["home_won"] is True
    assert a[R.CURRENT]["home_win_brier"] == (0.6 - 1) ** 2


def test_an_unavailable_arm_carries_no_error_and_the_values_are_verbatim():
    r = rec(do_status=R.UNAVAILABLE)
    r["arms"][R.DATA_ONLY]["projected_home_margin"] = None; r["arms"][R.DATA_ONLY]["projected_total"] = None
    ev = AE.evaluate_game(r, game(), {"status": "MISSING_CLOSE"})
    assert "margin_error" not in ev["arms"][R.DATA_ONLY]
    assert ev["arms"][R.CURRENT]["projected_home_margin"] == 3.0
    assert ev["arms"][R.HYBRID]["margin_movement_vs_close"] == "no_close"


def test_the_contract_close_is_strictly_pregame_or_missing():
    from nfl_edge.shadow.evaluation import pick_close
    kick = 1_000_000.0
    quotes = [{"observed_ts": kick - 600, "yes_bid": 0.5, "yes_ask": 0.52, "observed_at": "a"},
              {"observed_ts": kick + 60, "yes_bid": 0.9, "yes_ask": 0.92, "observed_at": "b"}]
    close = pick_close(quotes, kick)
    assert close["observed_ts"] == kick - 600
    c = {"record_id": "c", "game_record_id": "rid", "arms_version": R.ARMS_VERSION, "run_id": "r", "observed_at": "x",
         "minutes_to_kickoff": 30.0, "game_id": "G", "season": 2026, "week": 2, "kickoff_at": "2026-09-13T17:00:00+00:00",
         "ticker": "T", "family": "TOTAL", "period": "FULL", "team": None, "threshold": 45, "floor_strike": None, "operator": ">=",
         "direction": "YES", "arm_status": {}, "p_current": 0.5, "p_data_only": 0.6, "p_hybrid": 0.53, "cv_current": 0.5,
         "cv_data_only": 0.6, "cv_hybrid": 0.53, "yes_bid": 0.4, "yes_ask": 0.42, "mid": 0.41}
    ev = AE.evaluate_contract(c, Book(game()), close, kick)
    assert ev["settlement_status"] == "SETTLED" and ev["settled_yes"] == 1.0 and ev["close_status"] == "OK"
    assert ev["p_data_only"] == 0.6 and ev["close_mid"] == 0.51
    missing = AE.evaluate_contract(c, Book(game()), pick_close([quotes[1]], kick), kick)
    assert missing["close_status"] == "MISSING_CLOSE" and missing["close_mid"] is None


def test_a_closing_centre_with_too_few_liquid_quotes_is_missing_not_guessed():
    out = AE.closing_center({}, [], None, "H", "A")
    assert out["status"] == "MISSING_CLOSE" and "margin" not in out
