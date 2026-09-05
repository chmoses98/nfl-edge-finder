"""CLV accounting must not manufacture signal from its own arithmetic.

Two failure modes are pinned here. Session 2 shipped the first one: np.sign(0) == 0 scored every unchanged
quote as having moved away from the outcome, producing a 4-sigma result out of tie handling. The second is
subtler and would be worse -- regressing (price_close - price_T) on (model - price_T) shares price_T across
both sides, so noise in price_T alone produces a positive slope with no information present.
"""
import numpy as np

from nfl_edge.research.clv import (movement_direction, movement_regression,
                                   naive_movement_regression, signed_clv)


def test_unchanged_prices_are_never_scored_as_moving():
    d = movement_direction([0.4, 0.4, 0.4], [0.4, 0.5, 0.3], [0.6, 0.6, 0.6])
    assert list(d) == ["unchanged", "toward", "away"]


def test_no_view_is_distinguished_from_unchanged():
    d = movement_direction([0.4], [0.5], [0.4])
    assert list(d) == ["no_view"], "a model that agrees with the price has no direction to move toward"


def test_signed_clv_is_zero_when_we_hold_no_view():
    assert signed_clv([0.4], [0.9], [0.4])[0] == 0.0


def test_signed_clv_signs_by_our_view_not_by_the_move():
    assert signed_clv([0.4], [0.5], [0.6])[0] > 0     # we said higher, it went higher
    assert signed_clv([0.4], [0.3], [0.6])[0] < 0     # we said higher, it went lower
    assert signed_clv([0.4], [0.3], [0.2])[0] > 0     # we said lower, it went lower


def test_an_information_free_model_produces_no_signal_in_the_honest_specification():
    """A model that is pure noise -- independent of the truth -- must give b_model indistinguishable from 0,
    while the naive shared-baseline specification manufactures a large positive slope from price noise alone."""
    rng = np.random.default_rng(0)
    n = 6000
    true = rng.uniform(0.2, 0.8, n)
    price_t = np.clip(true + rng.normal(0, 0.06, n), 0.01, 0.99)      # noisy observation of the truth
    price_later = np.clip(true + rng.normal(0, 0.06, n), 0.01, 0.99)  # independent later observation
    model = rng.uniform(0.2, 0.8, n)                                  # knows NOTHING about `true`
    clusters = [f"g{i//8}" for i in range(n)]
    honest = movement_regression(model, price_t, price_later, clusters)
    naive = naive_movement_regression(model, price_t, price_later, clusters)
    assert abs(honest["z_model"]) < 3.0, f"honest spec found signal in an information-free model: {honest}"
    assert naive["b_disagreement"] > 0.02 and naive["z"] > 5, (
        "the naive spec must visibly manufacture a positive slope from price noise; "
        f"got b={naive['b_disagreement']:.3f} z={naive['z']:.2f}")


def test_honest_specification_recovers_real_information():
    """When the model genuinely knows where the price is going, b_model must be positive."""
    rng = np.random.default_rng(1)
    n = 4000
    price_t = rng.uniform(0.2, 0.8, n)
    future = np.clip(price_t + rng.normal(0, 0.08, n), 0.01, 0.99)
    model = np.clip(future + rng.normal(0, 0.03, n), 0.01, 0.99)      # model sees the future price
    clusters = [f"g{i//8}" for i in range(n)]
    honest = movement_regression(model, price_t, future, clusters)
    assert honest["b_model"] > 0.3 and honest["z_model"] > 5, honest
