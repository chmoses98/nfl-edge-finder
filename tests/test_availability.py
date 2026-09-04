"""Availability states and the play rates attached to them.

The rates are measured, not assumed (research/availability/RESULTS.md, 101,917 player-weeks). These tests pin
the properties that must hold whatever the numbers are recalibrated to.
"""
import pytest

from nfl_edge.settlement import availability as A


def test_states_are_ordered_by_how_likely_the_player_is_to_play():
    order = [A.EXPECTED_ACTIVE, A.QUESTIONABLE, A.DOUBTFUL, A.EXPECTED_OUT, A.OUT, A.INACTIVE_CONFIRMED]
    rates = [A.STATE_PLAY_RATES[s][0] for s in order]
    assert rates == sorted(rates, reverse=True), f"play rates are not monotone in severity: {rates}"


def test_doubtful_is_effectively_out():
    """A hand-set prior of 0.25 was wrong by 35x; the measured rate is under 0.01."""
    assert A.STATE_PLAY_RATES[A.DOUBTFUL][0] < 0.10


def test_confirmed_inactive_never_plays():
    assert A.STATE_PLAY_RATES[A.INACTIVE_CONFIRMED] == (0.0, 0.0)


def test_unknown_is_priced_below_the_healthy_rate_not_at_it():
    assert A.STATE_PLAY_RATES[A.UNKNOWN][0] < A.STATE_PLAY_RATES[A.EXPECTED_ACTIVE][0], \
        "a player our sources could not find must not be assumed healthy"


def test_all_rates_are_valid_partitions():
    for state, (p_play, p_nosnap) in A.STATE_PLAY_RATES.items():
        assert 0.0 <= p_play <= 1.0 and 0.0 <= p_nosnap <= 1.0
        assert p_play + p_nosnap <= 1.0 + 1e-12, f"{state} leaves negative inactive probability"


def test_the_most_adverse_known_signal_wins():
    assert A.combine_states({"espn": A.QUESTIONABLE, "sleeper": A.EXPECTED_ACTIVE}) == A.QUESTIONABLE
    assert A.combine_states({"espn": A.EXPECTED_ACTIVE, "roster": A.OUT}) == A.OUT


def test_unknown_never_overrides_a_real_signal():
    assert A.combine_states({"espn": A.UNKNOWN, "sleeper": A.QUESTIONABLE}) == A.QUESTIONABLE
    assert A.combine_states({"espn": A.UNKNOWN}) == A.UNKNOWN
    assert A.combine_states({}) == A.UNKNOWN


def test_two_sources_agreeing_on_expected_out_promote_it_to_out():
    assert A.combine_states({"espn": A.EXPECTED_OUT}) == A.EXPECTED_OUT
    assert A.combine_states({"espn": A.EXPECTED_OUT, "sleeper": A.EXPECTED_OUT}) == A.OUT


def test_depth_rank_moves_probability_from_playing_to_dressed_without_a_snap():
    base_play, base_nosnap = A.rates_for(A.EXPECTED_ACTIVE, depth_rank=1)
    deep_play, deep_nosnap = A.rates_for(A.EXPECTED_ACTIVE, depth_rank=4)
    assert deep_play < base_play, "a fourth-string player should be less likely to take a snap"
    assert deep_nosnap > base_nosnap
    assert deep_play + deep_nosnap == pytest.approx(base_play + base_nosnap), \
        "depth must move mass between branches, not create or destroy availability"


def test_depth_rank_cannot_resurrect_a_ruled_out_player():
    for state in A.BLOCKING_STATES:
        p1 = A.rates_for(state, depth_rank=None)
        p2 = A.rates_for(state, depth_rank=1)
        assert p1 == p2
