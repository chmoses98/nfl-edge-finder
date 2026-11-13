from nfl_edge.handicap.render import (
    _team_spread_from_home_handicap,
    _team_spread_from_home_margin,
)


def test_home_handicap_is_opposite_of_home_win_margin():
    assert _team_spread_from_home_handicap(-6.5, "PHI", "TOR") == "PHI -6.5"
    assert _team_spread_from_home_handicap(+6.5, "PHI", "TOR") == "TOR -6.5"
    assert _team_spread_from_home_handicap(-3, "PHI", "TOR") == "PHI -3"
    assert _team_spread_from_home_handicap(0, "PHI", "TOR") == "Pick'em"


def test_raw_home_margin_names_winner_not_loser():
    assert _team_spread_from_home_margin(+6.5, "PHI", "TOR") == "PHI -6.5"
    assert _team_spread_from_home_margin(-1.7, "PHI", "TOR") == "TOR -1.7"
    assert _team_spread_from_home_margin(+30, "PHI", "TOR") == "PHI -30"
    assert _team_spread_from_home_margin(None, "PHI", "TOR") == "--"
    assert _team_spread_from_home_margin(float("nan"), "PHI", "TOR") == "--"


# ---------------------------------------------------------------- shared module + every report surface
import os  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.spread_notation import (  # noqa: E402
    final_margin_label,
    team_spread_from_home_handicap,
    team_spread_from_home_margin,
    teams_from_game_id,
)


def test_two_native_conventions_render_identically_for_the_same_game():
    for margin in (-12.5, -1.7, 0.0, 3.0, 7.5):
        assert team_spread_from_home_handicap(-margin, "PHI", "TOR") == team_spread_from_home_margin(margin, "PHI", "TOR")


def test_final_results_home_away_and_ties():
    assert final_margin_label(27, 24, "PHI", "DAL") == "PHI -3"
    assert final_margin_label(17, 31, "PHI", "DAL") == "DAL -14"
    assert final_margin_label(20, 20, "PHI", "DAL") == "Pick'em"
    assert final_margin_label(None, 20, "PHI", "DAL") == "--"


def test_missing_and_degenerate_inputs_never_invent_a_favourite():
    for bad in (None, "x", float("nan"), float("inf"), True):
        assert team_spread_from_home_margin(bad, "PHI", "TOR") == "--"
        assert team_spread_from_home_handicap(bad, "PHI", "TOR") == "--"
    assert team_spread_from_home_margin(3, "PHI", "PHI") == "--"
    assert team_spread_from_home_margin(0.04, "PHI", "TOR") == "Pick'em"
    assert team_spread_from_home_margin(-0.06, "PHI", "TOR") == "TOR -0.1"
    assert team_spread_from_home_margin(10.0, "PHI", "TOR") == "PHI -10"


def test_nflverse_game_id_is_away_then_home():
    assert teams_from_game_id("2026_10_TOR_PHI") == ("PHI", "TOR")
    assert teams_from_game_id("bad") is None


def test_cover_and_error_math_is_unchanged_by_display():
    # Market PHI -6.5 (home handicap -6.5); final PHI 27-24 => PHI -3, did not cover.
    home_handicap, final_margin = -6.5, 27 - 24
    assert final_margin + home_handicap < 0
    assert team_spread_from_home_handicap(home_handicap, "PHI", "TOR") == "PHI -6.5"
    assert final_margin_label(27, 24, "PHI", "TOR") == "PHI -3"
    # Projected TOR -1.7 (margin -1.7) vs PHI -3 final: error 4.7 in margin units.
    assert round(abs(-1.7 - final_margin), 6) == 4.7


def test_simulation_centre_is_a_home_margin_not_a_handicap():
    """sim/simulate.py: spread_home = expected home margin (home - away). An away-favoured centre must name the away team."""
    from test_handicap_sim_projection_exposure import _game_with, _many_sim_rows  # noqa: E402

    from nfl_edge.handicap.render import render_game_markdown

    g = _game_with(_many_sim_rows(1))
    home, away = g["home_team"], g["away_team"]
    g["simulation"]["center"] = {"source": "kalshi_implied", "spread_home": -1.7, "total": 44.5}
    md = render_game_markdown(g)
    assert f"spread {away} -1.7 = home-minus-away margin -1.7" in md
    assert f"spread {home} -1.7" not in md


def test_three_arm_rows_name_the_projected_and_actual_winner():
    from nfl_edge.arms.report import render_game_rows

    row = {"game_id": "2026_10_TOR_PHI", "kickoff_at": "2026-11-12T00:00", "minutes_to_kickoff": 60,
           "arms": {}, "actual": {"margin": 3, "total": 51}, "market_at_snapshot": {"margin": -1.7, "total": 44.5, "source": "kalshi"},
           "close": {"margin": 2.5, "total": 45, "status": "ok"}}
    out = "\n".join(render_game_rows([row]))
    assert "3 (PHI -3)" in out
    assert "-1.7 (TOR -1.7)" in out
    assert "2.5 (PHI -2.5)" in out
    assert "(PHI -1.7)" not in out


def test_weekly_autopsy_rows_route_through_the_shared_formatter():
    # Source guard: the autopsy renderer needs a full weekly doc with no fixture in-repo.
    from nfl_edge.research import weekly_reports as W

    src = open(W.__file__).read()
    assert "final_margin_label(f['final_home'], f['final_away'], g['home'], g['away'])" in src
    assert "team_spread_from_home_margin(mk.get('home_margin'), g['home'], g['away'])" in src
