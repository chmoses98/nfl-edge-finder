"""Semantics engine: the question grammar fails closed and the winning-margin grammar is exhaustively proven."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.semantics import AMBIGUOUS, LIKELY, PROVEN, UNKNOWN, contract_question, question_from_market  # noqa: E402
from nfl_edge.semantics.catalog import FAMILY_CATALOG, catalog_entry, families_by_engine  # noqa: E402
from nfl_edge.kalshi.classifier import classify  # noqa: E402

FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "kalshi_market_samples.json")))


def _wm(ticker, wm, rules, team_uuid="x"):
    return {"ticker": ticker, "event_ticker": ticker.rsplit("-", 1)[0], "series_ticker": "KXNFLWINMARGIN", "strike_type": "custom",
            "custom_strike": {"Winning Margin": wm, "football_team": team_uuid}, "rules_primary": rules, "title": ""}


def test_margin_bucket_2026_structure_is_proven_and_inclusive():
    m = _wm("KXNFLWINMARGIN-26SEP14DENKC-KC7TO14", "7 to 14",
            "If Kansas City has a positive point differential of between 7 and 14 points against Denver in the full game (including overtime)")
    sem, q = question_from_market(m)
    assert q.kind == "RANGE" and q.stat == "margin" and q.subject == "KC" and (q.lo, q.hi) == (7.0, 14.0)
    assert q.semantic_confidence == PROVEN and q.overtime == "INCLUDED"


def test_margin_bucket_open_top_and_tie():
    m = _wm("KXNFLWINMARGIN-26SEP14DENKC-DEN15PLUS", "15 or more",
            "If Denver has a positive point differential of at least 15 points against Kansas City in the full game (including overtime)")
    sem, q = question_from_market(m)
    assert q.kind == "RANGE" and q.subject == "DEN" and q.lo == 15.0 and q.hi is None and q.semantic_confidence == PROVEN
    t = _wm("KXNFLWINMARGIN-26SEP14DENKC-TIE", "tie", "If Kansas City has a positive point differential of exactly 0 points against Denver")
    sem, q = question_from_market(t)
    assert q.kind == "EVENT" and q.event == "TIE" and q.semantic_confidence == PROVEN


def test_margin_bucket_ticker_only_is_likely_not_proven():
    m = {"ticker": "KXNFLWINMARGIN-26SEP14DENKC-KC7TO14", "event_ticker": "KXNFLWINMARGIN-26SEP14DENKC", "series_ticker": "KXNFLWINMARGIN"}
    sem, q = question_from_market(m)
    assert q.kind == "RANGE" and (q.lo, q.hi) == (7.0, 14.0)
    assert q.semantic_confidence == LIKELY and not q.priceable


def test_margin_bucket_disagreeing_readings_fail_closed():
    m = _wm("KXNFLWINMARGIN-26SEP14DENKC-KC7TO14", "1 to 6",
            "If Kansas City has a positive point differential of between 7 and 14 points against Denver")
    sem, q = question_from_market(m)
    assert q.semantic_confidence == AMBIGUOUS and not q.priceable


def test_margin_bucket_2025_archive_structure():
    m = {"ticker": "KXNFLWINMARGIN-26FEB08SEANE-710", "event_ticker": "KXNFLWINMARGIN-26FEB08SEANE", "series_ticker": "KXNFLWINMARGIN",
         "strike_type": "between", "floor_strike": 7, "cap_strike": 10, "title": "Will either Seattle or New England win by 7 to 10 points?",
         "rules_primary": "If either Seattle or New England has a winning margin between 7 to 10 points (inclusive)"}
    sem, q = question_from_market(m)
    assert q.kind == "RANGE" and q.stat == "abs_margin" and (q.lo, q.hi) == (7.0, 10.0) and q.semantic_confidence == PROVEN
    m2 = dict(m, ticker="KXNFLWINMARGIN-26FEB08SEANE-25", floor_strike=25, cap_strike=100, title="at least 25", rules_primary="win by at least 25")
    sem, q = question_from_market(m2)
    assert q.lo == 25.0 and q.hi is None


def test_every_fixture_margin_bucket_parses_proven_and_partitions():
    from collections import defaultdict
    groups = defaultdict(list)
    for m in FIX:
        if m.get("series_ticker", m["ticker"].split("-")[0]) != "KXNFLWINMARGIN":
            continue
        sem, q = question_from_market(m)
        assert q.semantic_confidence == PROVEN, (m["ticker"], q.notes)
        if q.kind == "RANGE":
            groups[(m["event_ticker"], q.subject)].append((q.lo, q.hi))
    for key, rs in groups.items():
        rs = sorted(rs, key=lambda x: (x[0], x[1] if x[1] is not None else 1e9))
        for (lo1, hi1), (lo2, _) in zip(rs, rs[1:]):
            assert hi1 is not None and lo2 == hi1 + 1, f"buckets do not tile the integers: {key} {rs}"


def test_spread_total_team_total_thresholds():
    sem, q = question_from_market({"ticker": "KXNFLSPREAD-26SEP14DENKC-KC8", "event_ticker": "KXNFLSPREAD-26SEP14DENKC", "series_ticker": "KXNFLSPREAD",
                                   "strike_type": "greater", "floor_strike": 7.5, "title": "Kansas City wins by over 7.5 points?"})
    assert (q.kind, q.stat, q.subject, q.op, q.k, q.engine) == ("THRESHOLD", "margin", "KC", ">", 7.5, "GAME") and q.semantic_confidence == PROVEN
    sem, q = question_from_market({"ticker": "KXNFLTOTAL-26SEP14DENKC-48", "event_ticker": "KXNFLTOTAL-26SEP14DENKC", "series_ticker": "KXNFLTOTAL",
                                   "strike_type": "greater", "floor_strike": 47.5, "title": ""})
    assert (q.kind, q.stat, q.op, q.k) == ("THRESHOLD", "total", ">=", 48) and q.semantic_confidence == PROVEN
    sem, q = question_from_market({"ticker": "KXNFL1HTOTAL-26SEP14DENKC-24", "event_ticker": "KXNFL1HTOTAL-26SEP14DENKC", "series_ticker": "KXNFL1HTOTAL",
                                   "strike_type": "greater", "floor_strike": 23.5, "title": ""})
    assert q.engine == "PERIOD" and q.period == "1H" and q.overtime == "NA" and q.k == 24


def test_period_winner_tie_rule_and_second_half_excludes_overtime():
    sem, q = question_from_market({"ticker": "KXNFL1H-26SEP14DENKC-TIE", "event_ticker": "KXNFL1H-26SEP14DENKC", "series_ticker": "KXNFL1H", "title": ""})
    assert q.event == "TIE" and q.tie_rule == "TIE_LEG_YES" and q.engine == "PERIOD"
    sem, q = question_from_market({"ticker": "KXNFL2HSPREAD-26SEP14DENKC-KC3", "event_ticker": "KXNFL2HSPREAD-26SEP14DENKC", "series_ticker": "KXNFL2HSPREAD",
                                   "strike_type": "greater", "floor_strike": 2.5, "title": ""})
    assert q.period == "2H" and q.overtime == "EXCLUDED"


def test_half_full_composite_legs():
    m = {"ticker": "KXNFL1HFT-26SEP14DENKC-DENKC", "event_ticker": "KXNFL1HFT-26SEP14DENKC", "series_ticker": "KXNFL1HFT", "strike_type": "custom",
         "custom_strike": {"1st Half Result": "Denver wins 1st Half", "Fulltime Result": "Kansas City wins game"}, "title": ""}
    sem, q = question_from_market(m)
    assert q.kind == "COMPOSITE" and q.engine == "JOINT" and len(q.legs) == 2 and q.semantic_confidence == PROVEN
    assert q.legs[0].subject == "DEN" and q.legs[0].period == "1H" and q.legs[1].subject == "KC" and q.legs[1].period == "FULL"
    bad = dict(m, custom_strike={"1st Half Result": "Tie in 1st Half", "Fulltime Result": "Kansas City wins game"})
    sem, q = question_from_market(bad)
    assert q.semantic_confidence == AMBIGUOUS


def test_parlay_legs_from_associated_markets():
    m = {"ticker": "KXNFLPREPACKSGP-25DEC083235-56O41", "event_ticker": "KXNFLPREPACKSGP-25DEC083235", "series_ticker": "KXNFLPREPACKSGP",
         "strike_type": "custom", "custom_strike": {"Associated Markets": "KXNFLTOTAL-25DEC08PHILAC-56, KXNFLTOTAL-KXNFLTOTAL-25DEC08PHILAC-41",
                                                     "Associated Market Sides": "Yes, No"}, "title": ""}
    sem, q = question_from_market(m)
    assert q.kind == "COMPOSITE" and q.engine == "JOINT" and len(q.legs) == 2
    assert q.legs[0].op == ">=" and q.legs[0].k == 56 and q.legs[1].op == "<" and q.legs[1].k == 41
    assert "NOT independent" in " ".join(q.notes)


def test_player_stat_question_carries_participation_semantics():
    for m in FIX:
        if m["ticker"].startswith("KXNFLRECYDS-") and m.get("custom_strike"):
            sem, q = question_from_market(m)
            assert q.engine == "PLAYER" and q.op == ">=" and q.k == sem.threshold and q.subject == sem.player_kalshi_id
            assert "fair price" in " ".join(q.notes)
            break
    else:
        pytest.skip("no receiving-yards fixture")


def test_unknown_series_is_unknown_and_not_priceable():
    sem, q = question_from_market({"ticker": "KXNFLPOTM-SEP26NFCOFFENSE-TMCMILLAN4", "event_ticker": "KXNFLPOTM-SEP26NFCOFFENSE", "series_ticker": "KXNFLPOTM", "title": "x"})
    assert q.semantic_confidence == UNKNOWN and q.engine == "NONE" and not q.priceable


def test_catalog_only_proven_supported_families_are_priceable_by_rule():
    for (fam, per), e in FAMILY_CATALOG.items():
        if e.model_support == "PRICED":
            assert e.semantic_confidence == PROVEN and e.settlement == "SUPPORTED", (fam, per)
        if e.engine == "NONE":
            assert e.model_support not in ("PRICED", "SHADOW"), (fam, per)
    assert catalog_entry("PLAYER_STAT", "FULL", "receiving_yards").settlement == "SUPPORTED"
    assert catalog_entry("PLAYER_STAT", "FULL", "sacks").model_support == "DATA_UNAVAILABLE"
    assert catalog_entry("WIN_MARGIN_BUCKET", "FULL").semantic_confidence == PROVEN
    assert catalog_entry("RACE_TO_N", "FULL").model_support == "RESEARCH_REQUIRED"
    assert set(families_by_engine()) >= {"GAME", "PERIOD", "PLAYER", "SEASON", "JOINT", "NONE"}


def test_every_fixture_market_gets_a_question_without_raising():
    seen = set()
    for m in FIX:
        sem, q = question_from_market(m)
        assert q.semantic_confidence in (PROVEN, LIKELY, AMBIGUOUS, UNKNOWN)
        seen.add(q.engine)
    assert "GAME" in seen and "PLAYER" in seen
