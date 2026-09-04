import numpy as np
from nfl_edge.kalshi.classifier import classify
from nfl_edge.pricing.ladder import price_yes, check_market_ladder, model_ladder_is_monotone


def test_price_semantics_integer_ladder():
    sem = classify({"ticker": "KXNFLRECYDS-26SEP10SFLAR-LARDADAMS17-120", "event_ticker": "KXNFLRECYDS-26SEP10SFLAR", "title": "Davante Adams: 120+ receiving yards",
                    "strike_type": "greater", "floor_strike": 119.5})
    samples = np.array([119, 120, 121, 50, 200])
    assert abs(price_yes(sem, samples) - 3 / 5) < 1e-9          # >= 120 counts 120
    sem2 = classify({"ticker": "KXNFLSPREAD-26SEP14DENKC-KC8", "event_ticker": "KXNFLSPREAD-26SEP14DENKC", "title": "Kansas City wins by over 7.5 points?",
                     "strike_type": "greater", "floor_strike": 7.5})
    margins = np.array([7, 8, 10, -3])
    assert abs(price_yes(sem2, margins) - 2 / 4) < 1e-9
    sem3 = classify({"ticker": "KXNFLWINMARGIN-26SEP14DENKC-KC7TO14", "event_ticker": "KXNFLWINMARGIN-26SEP14DENKC", "title": "x", "strike_type": "custom",
                     "custom_strike": {"Winning Margin": "7 to 14"}})
    assert abs(price_yes(sem3, np.array([6, 7, 14, 15])) - 2 / 4) < 1e-9


def test_market_ladder_checks():
    rows = [{"ticker": "A-50", "threshold": 50, "yes_bid_dollars": "0.60", "yes_ask_dollars": "0.62"},
            {"ticker": "A-60", "threshold": 60, "yes_bid_dollars": "0.65", "yes_ask_dollars": "0.70"},
            {"ticker": "A-70", "threshold": 70, "yes_bid_dollars": "0.20", "yes_ask_dollars": "0.25"}]
    v = check_market_ladder(rows)
    assert any(x["type"] == "crossed" and x["upper"] == "A-60" for x in v)
    assert model_ladder_is_monotone({50: 0.6, 60: 0.4, 70: 0.2}) and not model_ladder_is_monotone({50: 0.6, 60: 0.7})


# ---- ladder calibration ------------------------------------------------------------------------
def test_calibrator_preserves_rung_order_within_a_ladder():
    """A calibrated ladder must stay monotone: P(Y>=1) >= P(Y>=2) >= ... or the prices are incoherent."""
    import numpy as np
    from nfl_edge.pricing.calibration import LadderCalibrator
    rng = np.random.default_rng(1)
    true = rng.beta(0.7, 4, 50000)
    pred = np.clip(true * 1.4 + 0.004, 1e-4, 0.999)
    y = (rng.random(len(true)) < true).astype(float)
    c = LadderCalibrator().fit(pred, y)
    ladder = np.array([0.82, 0.60, 0.41, 0.22, 0.11, 0.04, 0.01])
    out = c.transform(ladder)
    assert np.all(np.diff(out) <= 1e-12), f"calibration reordered a monotone ladder: {out}"


def test_calibrator_keeps_probabilities_inside_the_unit_interval():
    import numpy as np
    from nfl_edge.pricing.calibration import LadderCalibrator
    rng = np.random.default_rng(2)
    true = rng.beta(0.7, 4, 50000)
    pred = np.clip(true * 1.4 + 0.004, 1e-4, 0.999)
    c = LadderCalibrator().fit(pred, (rng.random(len(true)) < true).astype(float))
    out = c.transform(np.array([1e-9, 1e-4, 0.5, 1 - 1e-4, 1 - 1e-9]))
    assert np.all(out > 0.0) and np.all(out < 1.0)


def test_calibrator_is_a_no_op_when_it_has_too_little_data_to_fit():
    """Failing closed: an unfittable calibrator must pass probabilities through unchanged, not guess."""
    import numpy as np
    from nfl_edge.pricing.calibration import LadderCalibrator
    c = LadderCalibrator().fit(np.array([0.1, 0.2, 0.3]), np.array([0.0, 1.0, 0.0]))
    p = np.array([0.05, 0.5, 0.9])
    assert np.allclose(c.transform(p), p)
    assert c.to_json()["knots"] is None
