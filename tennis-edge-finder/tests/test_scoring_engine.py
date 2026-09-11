"""Scoring-engine tests: closed forms, invariants, and Monte Carlo agreement."""
import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from tennis_edge.rules.formats import MatchFormat, TOUR_SINGLES_BO3, SLAM_MEN_2022, TOUR_DOUBLES, resolve_format, FormatResolutionError
from tennis_edge.sim.analytic import (game_win_prob, tiebreak_win_prob, set_win_prob, set_distribution,
                                      match_distribution, match_win_prob, point_probs_from_match_prob)
from tennis_edge.sim import montecarlo as mc


def test_game_closed_form_known_values():
    # classic textbook values (Barnett & Clarke)
    assert abs(game_win_prob(0.5) - 0.5) < 1e-12
    assert abs(game_win_prob(0.6) - 0.7357) < 5e-4
    assert abs(game_win_prob(0.7) - 0.9008) < 5e-4
    assert game_win_prob(0.6, no_ad=True) < game_win_prob(0.6)  # no-ad shortens the favourite's edge


def test_game_symmetry_and_monotone():
    for p in (0.3, 0.45, 0.55, 0.8):
        assert abs(game_win_prob(p) + game_win_prob(1 - p) - 1) < 1e-12
    ps = np.linspace(0.01, 0.99, 50)
    g = [game_win_prob(p) for p in ps]
    assert all(g[i] < g[i + 1] for i in range(len(g) - 1))


def test_tiebreak_symmetric_is_half_and_server_order_irrelevant_when_symmetric():
    assert abs(tiebreak_win_prob(0.65, 0.35) - 0.5) < 1e-12
    assert abs(tiebreak_win_prob(0.65, 0.35, a_serves_first=False) - 0.5) < 1e-12
    # stronger player wins more often; 10-point tiebreak amplifies the edge
    assert tiebreak_win_prob(0.68, 0.38) > 0.5
    assert tiebreak_win_prob(0.68, 0.38, to=10) > tiebreak_win_prob(0.68, 0.38, to=7)


def test_set_distribution_sums_to_one_and_scores_are_legal():
    for tb_at in (6, None, 12):
        d = set_distribution(0.63, 0.37, tb_at, 7, False, True)
        assert abs(sum(d.values()) - 1) < 1e-9
        for (a, b) in d:
            hi, lo = max(a, b), min(a, b)
            if tb_at is None:
                assert hi >= 6 and hi - lo >= 2
            else:
                assert (hi == tb_at + 1 and lo == tb_at) or (hi >= 6 and hi - lo >= 2 and hi <= max(7, tb_at + 1))


def test_set_symmetry():
    assert abs(set_win_prob(0.62, 0.38) - 0.5) < 1e-12
    assert abs(set_win_prob(0.66, 0.40) + set_win_prob(0.60, 0.34) - 1) < 1e-12  # swap players


def test_match_distribution_invariants():
    for fmt in (TOUR_SINGLES_BO3, SLAM_MEN_2022, TOUR_DOUBLES, MatchFormat(5, 6, 7, "ADVANTAGE"), MatchFormat(3, 6, 7, "TB7_AT_12")):
        d = match_distribution(0.66, 0.40, fmt)
        assert abs(sum(d.set_score.values()) - 1) < 1e-9
        assert abs(sum(d.total_games.values()) - 1) < 1e-9
        assert abs(sum(d.game_diff.values()) - 1) < 1e-9
        assert abs(sum(d.tiebreaks.values()) - 1) < 1e-9
        # match winner == sum of winning set-score paths (coherence)
        assert abs(d.p_match - sum(v for (a, b), v in d.set_score.items() if a > b)) < 1e-12
        assert abs(d.p_match - match_win_prob(0.66, 0.40, fmt)) < 1e-9
        # set 1 always played; later sets less often
        assert abs(d.set_winner[1]["played"] - 1) < 1e-12
        assert d.set_winner[fmt.best_of]["played"] < 1
        # totals ladder monotone
        cum = 0.0
        for k in sorted(d.total_games):
            cum += d.total_games[k]
        assert abs(cum - 1) < 1e-9
        for line in (18.5, 20.5, 22.5, 24.5):
            assert d.total_games_over(line) >= d.total_games_over(line + 2)


def test_match_bo5_favours_favourite_more_than_bo3():
    p3 = match_win_prob(0.66, 0.40, TOUR_SINGLES_BO3)
    p5 = match_win_prob(0.66, 0.40, SLAM_MEN_2022)
    assert p5 > p3 > 0.5


def test_match_tiebreak_doubles_less_favourite_edge_than_full_third_set():
    p_full = match_win_prob(0.66, 0.40, MatchFormat(3, 6, 7, "TB7_AT_6", True))
    p_mtb = match_win_prob(0.66, 0.40, TOUR_DOUBLES)
    assert p_full > p_mtb > 0.5


def test_inversion_roundtrip():
    for target in (0.2, 0.5, 0.63, 0.9):
        for fmt in (TOUR_SINGLES_BO3, SLAM_MEN_2022):
            pa, pb = point_probs_from_match_prob(target, 1.28, fmt)
            assert abs(match_win_prob(pa, pb, fmt) - target) < 1e-5


@pytest.mark.parametrize("fmt", [TOUR_SINGLES_BO3, SLAM_MEN_2022, TOUR_DOUBLES, MatchFormat(3, None, 7, "ADVANTAGE")])
def test_monte_carlo_agrees_with_exact(fmt):
    pa, pb = 0.67, 0.41
    n = 60_000
    s = mc.summarize(mc.simulate(pa, pb, fmt, n=n, seed=7))
    d = match_distribution(pa, pb, fmt)
    se = s["se_p_match"]
    assert abs(s["p_match"] - d.p_match) < 4 * se + 1e-9, (s["p_match"], d.p_match, se)
    # total games mean within MC error (sd of totals ~ 6 games)
    mean_exact = sum(k * v for k, v in d.total_games.items())
    assert abs(s["total_games_mean"] - mean_exact) < 4 * 6 / math.sqrt(n) + 0.05
    # set-score distribution agrees
    for k, v in d.set_score.items():
        assert abs(s["set_score"].get(k, 0.0) - v) < 4 * math.sqrt(max(v * (1 - v), 0.0) / n) + 1e-9
    # tiebreak count agrees
    for k, v in d.tiebreaks.items():
        if v > 0.01:
            assert abs(s["tiebreaks"].get(k, 0.0) - v) < 4 * math.sqrt(max(v * (1 - v), 0.0) / n) + 1e-9


def test_format_registry_fail_closed():
    with pytest.raises(FormatResolutionError):
        resolve_format("ATP", "TOUR_500_250", 2026, registry=[])
    assert resolve_format("ATP", "GRAND_SLAM", 2026, "ROLAND_GARROS").final_set == "TB10_AT_6"
    assert resolve_format("ATP", "GRAND_SLAM", 2021, "ROLAND_GARROS").final_set == "ADVANTAGE"
    assert resolve_format("ATP", "GRAND_SLAM", 2020, "WIMBLEDON").final_set == "TB7_AT_12"
    assert resolve_format("ATP", "GRAND_SLAM", 2015, "US_OPEN").final_set == "TB7_AT_6"
    assert resolve_format("WTA", "GRAND_SLAM", 2026, "US_OPEN").best_of == 3
    assert resolve_format("ATP", "TEAM", 2017, "DAVIS_CUP").best_of == 5
    assert resolve_format("ATP", "TEAM", 2024, "DAVIS_CUP").best_of == 3
    assert resolve_format("ATP", "CHALLENGER", 2026, discipline="doubles").no_ad is True
