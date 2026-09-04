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
