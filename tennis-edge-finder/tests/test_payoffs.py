import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from tennis_edge.kalshi.markets import parse_market
from tennis_edge.pricing.payoffs import price_market, check_consistency, PricingError
from tennis_edge.sim.analytic import match_distribution
from tennis_edge.rules.formats import SLAM_MEN_2022, TOUR_SINGLES_BO3

RULE = "If {who} wins the Zverev vs Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal after a ball has been played, then the market resolves to Yes."
EV = "KXATPMATCH-26SEP09ZVEVAN"


def _mk(series, suffix, rules, **extra):
    ev = f"{series}-26SEP09ZVEVAN"
    return dict({"ticker": f"{ev}-{suffix}", "event_ticker": ev, "series_ticker": series, "rules_primary": rules}, **extra)


def test_full_match_book_is_coherent():
    d = match_distribution(0.67, 0.40, SLAM_MEN_2022)
    ms = [
        _mk("KXATPMATCH", "ZVE", RULE.format(who="Alexander Zverev")),
        _mk("KXATPMATCH", "VAN", RULE.format(who="Botic Van de Zandschulp")),
    ]
    for x, y in ((3, 0), (3, 1), (3, 2)):
        ms.append(_mk("KXATPEXACTMATCH", f"ZVE{x}{y}", f"If Alexander Zverev wins the Alexander Zverev vs Botic Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal by a set score of {x}-{y}, then the market resolves to Yes."))
        ms.append(_mk("KXATPEXACTMATCH", f"VAN{x}{y}", f"If Botic Van de Zandschulp wins the Alexander Zverev vs Botic Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal by a set score of {x}-{y}, then the market resolves to Yes."))
    for line in (30.5, 34.5, 38.5, 42.5):
        ms.append(_mk("KXATPGTOTAL", str(int(line + 0.5)), f"If the number of completed games in the full match is above {line} in the Alexander Zverev vs Botic Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal, then the market resolves to Yes.", floor_strike=line))
    for line in (2.5, 4.5, 6.5):
        ms.append(_mk("KXATPGSPREAD", f"ZVE{int(line + 0.5)}", f"If the game differential in favor of Alexander Zverev across the full match is above {line} games in the Alexander Zverev vs Botic Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal, then the market resolves to Yes.", floor_strike=line))
    for n in (1, 2, 3, 4, 5):
        ms.append(_mk("KXATPSETWINNER", f"{n}-ZVE", f"If Alexander Zverev wins set {n} in the Alexander Zverev vs Botic Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal, then the market resolves to Yes."))
    ms.append(_mk("KXATPTOTALSETS", "4", "If above 3.5 sets are played in the Alexander Zverev vs Botic Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal, then the market resolves to Yes.", floor_strike=3.5))
    ms.append(_mk("KXATPSSPREAD", "ZVE2", "If Alexander Zverev wins by over 1.5 sets in the Alexander Zverev vs Botic Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal, then the market resolves to Yes.", floor_strike=1.5))
    parsed = {}
    prices = []
    for m in ms:
        pm = parse_market(m)
        assert pm.status == "PARSED", (pm.ticker, pm.reason)
        parsed[pm.ticker] = pm
        prices.append(price_market(pm, d))
    assert check_consistency(prices, parsed) == []
    by = {p.ticker: p.fair_yes for p in prices}
    # winner == sum of exact winning paths
    assert abs(by[f"KXATPEXACTMATCH-26SEP09ZVEVAN-ZVE30"] + by["KXATPEXACTMATCH-26SEP09ZVEVAN-ZVE31"] + by["KXATPEXACTMATCH-26SEP09ZVEVAN-ZVE32"] - by["KXATPMATCH-26SEP09ZVEVAN-ZVE"]) < 1e-12
    # all six exact scores sum to 1
    assert abs(sum(v for k, v in by.items() if "EXACTMATCH" in k) - 1) < 1e-12
    # set 1 winner sides sum to 1; set 5 joint < played
    assert abs(by["KXATPSETWINNER-26SEP09ZVEVAN-1-ZVE"] - d.set_winner[1]["a"]) < 1e-12
    # over 3.5 sets == 1 - P(3-0 or 0-3)
    assert abs(by["KXATPTOTALSETS-26SEP09ZVEVAN-4"] - (1 - by["KXATPEXACTMATCH-26SEP09ZVEVAN-ZVE30"] - by["KXATPEXACTMATCH-26SEP09ZVEVAN-VAN30"])) < 1e-12
    # set spread > 1.5 == 3-0 or 3-1
    assert abs(by["KXATPSSPREAD-26SEP09ZVEVAN-ZVE2"] - by["KXATPEXACTMATCH-26SEP09ZVEVAN-ZVE30"] - by["KXATPEXACTMATCH-26SEP09ZVEVAN-ZVE31"]) < 1e-12


def test_unparsed_cannot_be_priced():
    d = match_distribution(0.6, 0.4, TOUR_SINGLES_BO3)
    pm = parse_market({"ticker": "KXATPMATCH-26SEP09ZVEVAN-ZVE", "event_ticker": EV, "series_ticker": "KXATPMATCH", "rules_primary": "garbage"})
    with pytest.raises(PricingError):
        price_market(pm, d)


def test_monotone_violation_detected():
    from tennis_edge.pricing.payoffs import Price
    from tennis_edge.kalshi.markets import ParsedMarket
    p1 = ParsedMarket("t1", "KXATPGTOTAL", "e", family="TOTAL_GAMES", line=20.5)
    p2 = ParsedMarket("t2", "KXATPGTOTAL", "e", family="TOTAL_GAMES", line=22.5)
    v = check_consistency([Price("t1", "TOTAL_GAMES", 0.5, "x"), Price("t2", "TOTAL_GAMES", 0.6, "x")], {"t1": p1, "t2": p2})
    assert v and "not monotone" in v[0]
