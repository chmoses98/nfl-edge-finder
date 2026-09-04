import numpy as np
from nfl_edge.pricing.game_env import ResidualBank, simulate_game, price_game_markets


def _bank():
    rng = np.random.default_rng(0)
    n = 4000
    seasons = rng.integers(2016, 2026, n)
    spreads = rng.choice([-7, -3.5, -3, -1.5, 0, 1, 2.5, 3, 3.5, 7], n)
    totals = rng.choice([41.5, 44, 45.5, 47, 49.5], n)
    home = rng.poisson(23, n); away = rng.poisson(21, n)
    result = home - away
    overtime = (np.abs(result) <= 3) & (rng.random(n) < 0.15)   # synthetic OT games, some of which end tied
    return ResidualBank(result - spreads, home + away - totals, seasons, ref_season=2026, spread_lines=spreads, total_lines=totals,
                        overtime=overtime, results=result, halflife=3.0, rng=rng)


def test_scores_are_integer_and_coherent():
    sim = simulate_game(3.5, 44.5, _bank(), n=5000)
    assert np.all(np.mod(sim["home"], 1) == 0) and np.all(np.mod(sim["away"], 1) == 0)
    assert np.allclose(sim["home"] - sim["away"], sim["margin"]) and np.allclose(sim["home"] + sim["away"], sim["total"])
    p = price_game_markets(sim, "SEA", "NE")
    assert abs(p["home_win"] + p["away_win"] + p["tie"] - 1) < 1e-9
    assert p["spread_SEA_over_3.5"] <= p["spread_SEA_over_2.5"] <= p["home_win"]
    assert p["total_ge_45"] <= p["total_ge_44"] and p["teamtotal_SEA_ge_28"] <= p["teamtotal_SEA_ge_21"]
    assert p["tie"] < 0.02


def test_favourite_direction():
    sim_fav = simulate_game(7.0, 45.0, _bank(), n=5000); sim_dog = simulate_game(-7.0, 45.0, _bank(), n=5000)
    assert np.mean(sim_fav["margin"] > 0) > 0.65 > 0.35 > np.mean(sim_dog["margin"] > 0)
