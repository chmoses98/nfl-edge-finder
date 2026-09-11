"""Kalshi tennis market parser tests against REAL market records (tests/fixtures/kalshi_tennis_markets_sample.json)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from tennis_edge.kalshi.markets import parse_market, side_from_ticker
from tennis_edge.kalshi.families import SERIES, FAMILIES, unknown_series
from tennis_edge.kalshi.taxonomy import classify_series

FIX = json.load(open(os.path.join(os.path.dirname(__file__), "fixtures", "kalshi_tennis_markets_sample.json")))


def _one(ticker_prefix):
    for m in FIX:
        if m["ticker"].startswith(ticker_prefix):
            return m
    raise KeyError(ticker_prefix)


def test_every_fixture_series_is_registered():
    assert unknown_series({m.get("series_ticker") or m["ticker"].split("-")[0] for m in FIX}) == []


def test_families_all_defined():
    assert {v[0] for v in SERIES.values()} <= set(FAMILIES)


def test_fixture_parse_rate():
    res = [parse_market(m) for m in FIX]
    parsed = sum(r.status == "PARSED" for r in res)
    unsupported = sum(r.status == "UNSUPPORTED_FAMILY" for r in res)
    unparsed = [r for r in res if r.status == "UNPARSED"]
    # fixtures deliberately include a few legacy oddities; the live-universe rate is checked by the health gate
    assert parsed + unsupported >= 0.9 * len(res), [(r.ticker, r.reason) for r in unparsed]


def test_match_winner_zverev():
    m = {"ticker": "KXATPMATCH-26SEP09ZVEVAN-ZVE", "event_ticker": "KXATPMATCH-26SEP09ZVEVAN", "series_ticker": "KXATPMATCH",
         "custom_strike": {"tennis_competitor": "dc4002ad"},
         "rules_primary": "If Alexander Zverev wins the Zverev vs Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal after a ball has been played, then the market resolves to Yes."}
    p = parse_market(m)
    assert p.status == "PARSED" and p.family == "MATCH_WINNER"
    assert p.player_a == "Zverev" and p.player_b == "Van de Zandschulp" and p.subject_is_a is True
    assert p.competition == "US Open Men Singles" and p.round == "QF" and p.year == 2026
    assert p.ball_played_clause and p.competitor_id == "dc4002ad"
    # the other side
    m2 = dict(m, ticker="KXATPMATCH-26SEP09ZVEVAN-VAN", rules_primary=m["rules_primary"].replace("If Alexander Zverev", "If Botic Van de Zandschulp"))
    assert parse_market(m2).subject_is_a is False


def test_side_from_ticker_grammar():
    assert side_from_ticker("KXATPMATCH-26SEP09ZVEVAN-ZVE", "KXATPMATCH-26SEP09ZVEVAN") is True
    assert side_from_ticker("KXATPMATCH-26SEP09ZVEVAN-VAN", "KXATPMATCH-26SEP09ZVEVAN") is False
    assert side_from_ticker("KXATPGSPREAD-26SEP09ZVEVAN-ZVE7", "KXATPGSPREAD-26SEP09ZVEVAN") is True
    assert side_from_ticker("KXATPSETWINNER-26SEP08SHEALC-4-SHE", "KXATPSETWINNER-26SEP08SHEALC") is True
    assert side_from_ticker("KXWTADOUBLES-26SEP08HSIOSTMERSHN-HSIOST", "KXWTADOUBLES-26SEP08HSIOSTMERSHN") is True
    assert side_from_ticker("KXWTADOUBLES-26SEP08HSIOSTMERSHN-MERSHN", "KXWTADOUBLES-26SEP08HSIOSTMERSHN") is False
    # same surname: digit marks the second competitor
    assert side_from_ticker("KXITFWMATCH-26SEP01KIMKIM2-KIM", "KXITFWMATCH-26SEP01KIMKIM2") is True
    assert side_from_ticker("KXITFWMATCH-26SEP01KIMKIM2-KIM2", "KXITFWMATCH-26SEP01KIMKIM2") is False
    # totals have no side
    assert side_from_ticker("KXATPGTOTAL-26SEP08TIAMIC-52", "KXATPGTOTAL-26SEP08TIAMIC") is None


def test_conflicting_sides_fail_closed():
    m = {"ticker": "KXATPMATCH-26SEP09ZVEVAN-VAN", "event_ticker": "KXATPMATCH-26SEP09ZVEVAN", "series_ticker": "KXATPMATCH",
         "rules_primary": "If Alexander Zverev wins the Zverev vs Van de Zandschulp professional tennis match in the 2026 US Open Men Singles Quarterfinal after a ball has been played, then the market resolves to Yes."}
    p = parse_market(m)
    assert p.status == "UNPARSED" and "disagrees" in p.reason


def test_spread_total_exact_set_fields():
    p = parse_market(_one("KXATPGSPREAD-"))
    assert p.family == "GAME_SPREAD" and p.line is not None and p.subject_is_a is not None
    p = parse_market(_one("KXATPGTOTAL-"))
    assert p.family == "TOTAL_GAMES" and p.line is not None and p.subject == ""
    p = parse_market(_one("KXATPEXACTMATCH-"))
    assert p.family == "EXACT_SET_SCORE" and p.exact_score is not None
    p = parse_market(_one("KXATPSETWINNER-"))
    assert p.family == "SET_WINNER" and p.set_index in (1, 2, 3, 4, 5)


def test_floor_strike_disagreement_fails_closed():
    m = dict(_one("KXATPGTOTAL-"))
    m["floor_strike"] = 99.5
    assert parse_market(m).status == "UNPARSED"


def test_unknown_series_fails_closed():
    p = parse_market({"ticker": "KXNEWTENNISTHING-26-X", "event_ticker": "KXNEWTENNISTHING-26", "series_ticker": "KXNEWTENNISTHING", "rules_primary": "If X wins ..."})
    assert p.status == "UNPARSED" and "unknown series" in p.reason


def test_unsupported_family_is_explicit():
    p = parse_market(_one("KXATPS1GWINNER-"))
    assert p.status == "UNSUPPORTED_FAMILY" and p.family == "GAME_WINNER_INPLAY" and p.projectable is False


def test_series_classifier_tag_and_exclusions():
    assert classify_series({"ticker": "KXATPMATCH", "title": "ATP Tennis Match", "tags": ["Tennis"], "category": "Sports"})["is_tennis"]
    assert not classify_series({"ticker": "KXWTAX", "title": "Wealth tax", "tags": ["Growth"], "category": "Politics"})["is_tennis"]
    assert not classify_series({"ticker": "KXTTMATCH", "title": "Men's Table Tennis Match", "tags": ["Table Tennis"], "category": "Sports"})["is_tennis"]
    c = classify_series({"ticker": "KXPICKLEBALLMATCH", "title": "Pickleball Match", "tags": ["Tennis"], "category": "Sports"})
    assert c["is_tennis"] and c["sport"] == "pickleball"
