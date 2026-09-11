"""Leakage guards: predictions must use only earlier matches; within a tournament rounds are ordered."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import date
import pandas as pd
from tennis_edge.models.elo import Elo, EloConfig, match_sort_key, expected


def _m(key, d, tid, rnd, w, l, num):
    return {"match_key": key, "tourney_date": d, "tourney_id": tid, "round": rnd, "match_num": num, "winner_id": w, "loser_id": l,
            "surface": "Hard", "level_canonical": "TOUR_500_250", "outcome_type": "COMPLETED", "tour": "ATP"}


def test_prediction_precedes_update_and_round_order():
    rows = [_m("k3", date(2026, 1, 1), "T1", "F", "A", "B", 3), _m("k1", date(2026, 1, 1), "T1", "R16", "A", "C", 1), _m("k2", date(2026, 1, 1), "T1", "QF", "A", "D", 2)]
    df = match_sort_key(pd.DataFrame(rows))
    assert df.match_key.tolist() == ["k1", "k2", "k3"]
    cfg = EloConfig(use_surface=False, use_level_k=False, use_level_prior=False)
    r = Elo(cfg).run(pd.DataFrame(rows))
    # first prediction for A is at the initial rating (0.5), later ones rise because A has won before
    assert abs(r.loc[r.match_key == "k1", "p_winner"].iloc[0] - 0.5) < 1e-12
    assert r.loc[r.match_key == "k3", "p_winner"].iloc[0] > 0.5
    # the rating used for k3 equals the rating AFTER k1 and k2, not after k3
    e = Elo(cfg); e.update("A", "C"); e.update("A", "D")
    assert abs(r.loc[r.match_key == "k3", "r_w"].iloc[0] - e.rating("A")) < 1e-9


def test_walkover_not_updated_and_retirement_half_weight():
    rows = [_m("k1", date(2026, 1, 1), "T1", "R16", "A", "B", 1)]
    rows[0]["outcome_type"] = "WALKOVER"
    e = Elo(EloConfig(use_surface=False, use_level_k=False, use_level_prior=False)); e.run(pd.DataFrame(rows))
    assert e.r["A"] == e.r["B"] == 1500.0
    rows[0]["outcome_type"] = "RETIRED"
    e2 = Elo(EloConfig(use_surface=False, use_level_k=False, use_level_prior=False)); e2.run(pd.DataFrame(rows))
    rows[0]["outcome_type"] = "COMPLETED"
    e3 = Elo(EloConfig(use_surface=False, use_level_k=False, use_level_prior=False)); e3.run(pd.DataFrame(rows))
    assert abs((e2.r["A"] - 1500) - 0.5 * (e3.r["A"] - 1500)) < 1e-9
