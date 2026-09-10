"""The challenger-side contract pricer gives the incumbent's answers on a shared simulation."""
import numpy as np

from nfl_edge.arms.pricing import price_contract
from nfl_edge.pricing.game_env import price_game_markets
from nfl_edge.settlement.semantics import game_winner_contract_value


def sim():
    rng = np.random.default_rng(3)
    m = np.round(rng.normal(3, 13, 20000)); t = np.round(rng.normal(45, 13, 20000))
    odd = (t + m) % 2 != 0
    t = t + odd
    return {"margin": m, "total": t, "home": (t + m) / 2, "away": (t - m) / 2}


def test_every_family_matches_the_incumbent_formulae():
    s = sim(); ref = price_game_markets(s, "H", "A")
    p, cv, _ = price_contract(s, {"family": "GAME_WINNER", "team": "H"}, "H", "A")
    assert p == ref["home_win"] and cv == game_winner_contract_value(ref["home_win"], ref["tie"]).contract_value
    p, cv, _ = price_contract(s, {"family": "SPREAD", "period": "FULL", "team": "A", "floor_strike": 3.5}, "H", "A")
    assert p == ref["spread_A_over_3.5"] == cv
    p, _, _ = price_contract(s, {"family": "TOTAL", "period": "FULL", "threshold": 45}, "H", "A")
    assert p == ref["total_ge_45"]
    p, _, _ = price_contract(s, {"family": "TEAM_TOTAL", "period": "FULL", "team": "H", "threshold": 24}, "H", "A")
    assert p == ref["teamtotal_H_ge_24"]
    p, _, _ = price_contract(s, {"family": "BOTH_TEAMS_SCORE_N", "threshold": 21}, "H", "A")
    assert p == ref["both_ge_21"]


def test_unpriceable_contracts_return_a_reason_never_a_number():
    s = sim()
    for q in ({"family": "SPREAD", "period": "1H", "team": "H", "floor_strike": 3.5},
              {"family": "GAME_WINNER", "team": None}, {"family": "WIN_MARGIN_BUCKET", "team": "H"},
              {"family": "TOTAL", "period": "FULL", "threshold": None}):
        p, cv, why = price_contract(s, q, "H", "A")
        assert p is None and cv is None and why


def test_event_probability_and_contract_value_differ_only_for_the_tie_leg():
    s = sim(); s["margin"][:200] = 0.0
    p, cv, _ = price_contract(s, {"family": "GAME_WINNER", "team": "H"}, "H", "A")
    assert cv == p + 0.5 * np.mean(s["margin"] == 0)
