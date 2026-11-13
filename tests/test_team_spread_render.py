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
