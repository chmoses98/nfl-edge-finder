"""Kalshi settlement rules, which decide what a contract is actually worth.

These are not modelling choices, they are exchange rules, and getting one wrong misprices a whole family
silently. A first version of this platform's documentation claimed an inactive player's contract settles at
the pregame fair price. It does not -- it settles at $0.00. Only a player who dresses and never takes a snap
gets the fair-price branch. That error was worth several cents on every player prop.
"""
import pytest

from nfl_edge.settlement.semantics import (binary_contract_value, game_winner_contract_value,
                                           player_prop_contract_value, settlement_supported)


def test_inactive_settles_at_zero_not_at_the_fair_price():
    """The whole point: an inactive player's YES contract is worthless, however likely the event was."""
    cv = player_prop_contract_value(event_probability=0.60, p_plays=0.0, p_active_no_snap=0.0, fair_price=0.55)
    assert cv.contract_value == pytest.approx(0.0)
    assert cv.p_inactive == pytest.approx(1.0)


def test_active_but_no_snap_settles_at_the_pregame_fair_price():
    cv = player_prop_contract_value(event_probability=0.60, p_plays=0.0, p_active_no_snap=1.0, fair_price=0.55)
    assert cv.contract_value == pytest.approx(0.55)


def test_the_three_branches_are_a_partition_and_the_value_is_their_mixture():
    cv = player_prop_contract_value(0.60, p_plays=0.90, p_active_no_snap=0.04, fair_price=0.50)
    assert cv.p_plays + cv.p_active_no_snap + cv.p_inactive == pytest.approx(1.0)
    assert cv.contract_value == pytest.approx(0.90 * 0.60 + 0.04 * 0.50)
    assert cv.contract_value < cv.event_probability, "availability must haircut a prop, never inflate it"


def test_unknown_fair_price_falls_back_to_the_event_probability():
    """That branch should be EV-neutral when unknown -- never silently free, never silently worthless."""
    cv = player_prop_contract_value(0.42, p_plays=0.80, p_active_no_snap=0.20, fair_price=None)
    assert cv.fair_price_used == pytest.approx(0.42)
    assert cv.contract_value == pytest.approx(0.42)


def test_probabilities_are_clamped_into_a_valid_partition():
    cv = player_prop_contract_value(0.5, p_plays=0.9, p_active_no_snap=0.5, fair_price=0.5)
    assert 0.0 <= cv.p_plays <= 1.0 and 0.0 <= cv.p_active_no_snap <= 1.0 and cv.p_inactive >= 0.0
    assert cv.p_plays + cv.p_active_no_snap <= 1.0 + 1e-12


def test_a_tie_pays_fifty_cents_to_both_sides():
    cv = game_winner_contract_value(p_win=0.50, p_tie=0.02)
    assert cv.contract_value == pytest.approx(0.51)
    # both sides priced this way sum to 1: 0.50+0.01 and 0.48+0.01
    other = game_winner_contract_value(p_win=0.48, p_tie=0.02)
    assert cv.contract_value + other.contract_value == pytest.approx(1.0)


def test_plain_binary_is_just_the_probability():
    assert binary_contract_value(0.37).contract_value == pytest.approx(0.37)


def test_every_contract_value_is_a_probability():
    for cv in (player_prop_contract_value(0.6, 0.9, 0.05, 0.5), game_winner_contract_value(0.5, 0.02),
               binary_contract_value(0.99), player_prop_contract_value(1.0, 1.0, 0.0, 1.0),
               player_prop_contract_value(0.0, 1.0, 0.0, 0.0)):
        assert 0.0 <= cv.contract_value <= 1.0


def test_unknown_families_fail_closed():
    ok, reason = settlement_supported("A_FAMILY_THAT_DOES_NOT_EXIST")
    assert ok is False and reason, "an unmodelled family must be refused with a reason, not priced"
