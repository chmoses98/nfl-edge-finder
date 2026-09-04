"""Point-in-time guarantees for the opportunity features.

Every opportunity feature is an EWMA over a player's or team's strictly-prior games. The failure mode that
matters is subtle: an off-by-one that writes the feature after the update instead of before makes the model
look excellent in backtest and worthless live. These tests assert the property directly rather than
inspecting the recursion -- if row i's feature can be changed by editing row i's own outcome, it leaks.
"""
import numpy as np
import polars as pl
import pytest

from nfl_edge.features.opportunity import group_priors, point_in_time_ewma

COLS = ["target_share", "route_share"]


def frame(vals, seasons=None, weeks=None, key="p1"):
    n = len(vals)
    return pl.DataFrame({
        "player_id": [key] * n,
        "season": seasons or [2020] * n,
        "week": weeks or list(range(1, n + 1)),
        "position": ["WR"] * n,
        "target_share": [float(v) for v in vals],
        "route_share": [float(v) for v in vals],
    })


def test_feature_on_a_row_ignores_that_rows_own_outcome():
    """The canonical leakage test: perturb row i's outcome, row i's feature must not move."""
    base = frame([0.1, 0.2, 0.3, 0.4, 0.5])
    a = point_in_time_ewma(base, COLS, shrink_k=3.0)
    for i in range(base.height):
        bumped = base.with_columns(
            pl.when(pl.int_range(pl.len()) == i).then(pl.lit(99.0)).otherwise(pl.col("target_share")).alias("target_share"))
        b = point_in_time_ewma(bumped, COLS, shrink_k=3.0)
        assert a["pit_target_share"][i] == pytest.approx(b["pit_target_share"][i]), \
            f"row {i}'s feature moved when row {i}'s own outcome changed -- the feature leaks the label"
        if i + 1 < base.height:
            assert a["pit_target_share"][i + 1] != pytest.approx(b["pit_target_share"][i + 1]), \
                f"row {i+1}'s feature did NOT move when row {i} changed -- prior games are being ignored"


def test_future_games_never_affect_past_features():
    short = point_in_time_ewma(frame([0.1, 0.2, 0.3]), COLS)
    long = point_in_time_ewma(frame([0.1, 0.2, 0.3, 0.9, 0.9, 0.9]), COLS)
    for i in range(3):
        assert short["pit_target_share"][i] == pytest.approx(long["pit_target_share"][i])


def test_first_ever_game_is_the_pure_prior():
    priors = {"WR": np.array([0.17, 0.62])}
    d = point_in_time_ewma(frame([0.4, 0.4]), COLS, shrink_k=3.0, priors=priors)
    assert d["pit_target_share"][0] == pytest.approx(0.17)
    assert d["pit_route_share"][0] == pytest.approx(0.62)
    assert d["pit_n_prior"][0] == 0 and d["pit_shrink_w"][0] == pytest.approx(1.0)


def test_players_do_not_bleed_into_each_other():
    two = pl.concat([frame([0.9, 0.9, 0.9], key="a"), frame([0.1, 0.1, 0.1], key="b")])
    d = point_in_time_ewma(two, COLS, shrink_k=3.0).sort(["player_id", "week"])
    b_first = d.filter(pl.col("player_id") == "b")["pit_target_share"][0]
    assert b_first == pytest.approx(0.0), "player b's first game inherited player a's history"


def test_season_boundary_discounts_rather_than_resets_or_carries_fully():
    within = point_in_time_ewma(frame([0.5, 0.5, 0.5, 0.5], seasons=[2020] * 4), COLS, season_carry=0.5)
    across = point_in_time_ewma(frame([0.5, 0.5, 0.5, 0.5], seasons=[2020, 2020, 2021, 2021],
                                      weeks=[1, 2, 1, 2]), COLS, season_carry=0.5)
    assert across["pit_target_share"][2] < within["pit_target_share"][2], "season carry did not discount"
    assert across["pit_target_share"][2] > 0.0, "season boundary wrongly wiped the player's history"


def test_group_priors_only_see_the_seasons_they_are_given():
    d = pl.concat([frame([0.1, 0.1], seasons=[2016, 2016]), frame([9.0, 9.0], seasons=[2024, 2024])])
    pr = group_priors(d.filter(pl.col("season") < 2019), COLS, [2016, 2017, 2018])
    assert pr["WR"][0] == pytest.approx(0.1), "priors absorbed data from outside the pre-window seasons"


def test_walk_forward_split_never_trains_on_the_evaluation_season():
    seasons = np.array([2018, 2019, 2020, 2021])
    for S in (2019, 2020, 2021):
        train = seasons < S
        assert not train[seasons == S].any()
        assert seasons[train].max() < S
