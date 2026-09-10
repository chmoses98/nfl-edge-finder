"""Common random numbers: the three arms differ by their centre and by nothing else."""
import hashlib

import numpy as np
import pytest
from scipy import stats

from nfl_edge.arms import crn, registry as R
from nfl_edge.pricing.game_env import ResidualBank, simulate_game


def bank(seed=11):
    rng = np.random.default_rng(0)
    n = 4000
    seasons = rng.integers(2016, 2026, n)
    spreads = rng.choice([-7, -3.5, -3, -1.5, 0, 1, 2.5, 3, 3.5, 7], n)
    totals = rng.choice([41.5, 44, 45.5, 47, 49.5], n)
    home = rng.poisson(23, n); away = rng.poisson(21, n); result = home - away
    overtime = (np.abs(result) <= 3) & (rng.random(n) < 0.15)
    return ResidualBank(result - spreads, home + away - totals, seasons, ref_season=2026, spread_lines=spreads,
                        total_lines=totals, overtime=overtime, results=result, halflife=3.0, rng=np.random.default_rng(seed))


def test_arms_in_the_same_fractional_class_draw_identical_residuals():
    b = bank(); d = crn.draw_uniforms(R.N_SIMS, "run|game|v")
    a = crn.simulate_game_crn(3.0, 44.0, b, d)
    c = crn.simulate_game_crn(-6.0, 47.0, b, d)          # a different centre, the same class
    assert np.array_equal(a["residual_idx"], c["residual_idx"])
    assert d["n"] == R.N_SIMS == 40000 and len(a["margin"]) == 40000


def test_the_same_uniforms_reach_every_arm_and_are_recorded_by_hash():
    d1 = crn.draw_uniforms(1000, "k"); d2 = crn.draw_uniforms(1000, "k"); d3 = crn.draw_uniforms(1000, "other")
    assert d1["sha"] == d2["sha"] and np.array_equal(d1["u_idx"], d2["u_idx"])
    assert d1["sha"] != d3["sha"]
    assert d1["sha"] == hashlib.sha256(b"".join(d1[k].tobytes() for k in ("u_idx", "u_tie", "u_otm", "u_side", "u_parity"))).hexdigest()[:16]


def test_different_fractional_classes_are_coupled_by_quantile_not_identical():
    b = bank(); d = crn.draw_uniforms(20000, "k")
    a = crn.simulate_game_crn(3.0, 44.0, b, d); c = crn.simulate_game_crn(3.5, 44.0, b, d)
    assert not np.array_equal(a["residual_idx"], c["residual_idx"])
    assert a["fractional_class"] != c["fractional_class"]


def test_scores_stay_integer_and_coherent_like_the_incumbent():
    s = crn.simulate_game_crn(3.5, 44.5, bank(), crn.draw_uniforms(20000, "k"))
    assert np.all(s["home"] % 1 == 0) and np.all(s["away"] % 1 == 0)
    assert np.allclose(s["home"] - s["away"], s["margin"]) and np.allclose(s["home"] + s["away"], s["total"])


def test_the_crn_simulator_is_monte_carlo_equivalent_to_the_incumbent():
    """Same bank, same centre: the two samplers describe the same distribution (KS on margins, matched means)."""
    b = bank()
    ours = crn.simulate_game_crn(-3.5, 47.5, b, crn.draw_uniforms(40000, "k"))
    theirs = simulate_game(-3.5, 47.5, bank(), n=40000)
    assert abs(ours["margin"].mean() - theirs["margin"].mean()) < 0.35
    assert abs(np.mean(ours["margin"] > 0) - np.mean(theirs["margin"] > 0)) < 0.012
    assert stats.ks_2samp(ours["margin"], theirs["margin"]).pvalue > 0.01
    assert stats.ks_2samp(ours["total"], theirs["total"]).pvalue > 0.01


def test_weights_match_the_banks_own_rule():
    b = bank()
    w = crn.residual_weights(b, 3.5, 44.5)
    assert abs(w.sum() - 1) < 1e-12
    assert np.all(w[~b.sfrac] == 0), "a half-point centre samples only half-point residuals, as the incumbent does"


def test_challenger_centres_snap_to_the_half_point_grid():
    assert crn.snap_to_grid(4.26) == 4.5 and crn.snap_to_grid(4.24) == 4.0 and crn.snap_to_grid(-2.37) == -2.5
    assert crn.snap_to_grid(51.49) == 51.5


@pytest.mark.parametrize("seed", [1, 2])
def test_the_seed_key_is_deterministic(seed):
    assert crn.seed_from_key(f"a|b|{seed}") == crn.seed_from_key(f"a|b|{seed}")
    assert crn.seed_from_key("a|b|1") != crn.seed_from_key("a|b|2")
