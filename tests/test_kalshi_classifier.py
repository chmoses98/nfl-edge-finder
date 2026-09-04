import json, os, collections
import pytest
from nfl_edge.kalshi.classifier import classify, parse_event_ticker, UNKNOWN

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "kalshi_market_samples.json")
SAMPLES = json.load(open(FIX))


def by_ticker(t):
    return next(m for m in SAMPLES if m["ticker"] == t)


def test_event_ticker_parse():
    assert parse_event_ticker("KXNFLSPREAD-26SEP14DENKC") == {"game_date": "2026-09-14", "away_kalshi": "DEN", "home_kalshi": "KC"}
    assert parse_event_ticker("KXNFLRECYDS-26SEP10SFLAR")["home_kalshi"] == "LAR"
    assert parse_event_ticker("KXNFLGAME-26SEP09NESEA") == {"game_date": "2026-09-09", "away_kalshi": "NE", "home_kalshi": "SEA"}
    assert parse_event_ticker("KXNFLWINS-27IND") is None
    assert parse_event_ticker("KXNFLWINSWEEK-26W12") is None


def test_spread_semantics():
    s = classify(by_ticker("KXNFLSPREAD-26SEP14DENKC-KC8"))
    assert s.family == "SPREAD" and s.team_kalshi == "KC" and s.team == "KC" and s.floor_strike == 7.5 and s.operator == ">"
    assert s.home_team == "KC" and s.away_team == "DEN" and s.period == "FULL" and s.confidence >= 0.9


def test_total_is_ge_integer():
    s = classify(by_ticker("KXNFLTOTAL-26SEP14DENKC-64"))
    assert s.family == "TOTAL" and s.threshold == 64 and s.operator == ">=" and s.floor_strike == 63.5


def test_team_total():
    s = classify(by_ticker("KXNFLTEAMTOTAL-26SEP10SFLAR-SF8"))
    assert s.family == "TEAM_TOTAL" and s.team == "SF" and s.threshold == 8 and s.operator == ">="


def test_player_ladders():
    s = classify(by_ticker("KXNFLRECYDS-26SEP10SFLAR-LARDADAMS17-120"))
    assert s.family == "PLAYER_STAT" and s.stat == "receiving_yards" and s.threshold == 120 and s.operator == ">="
    assert s.player_name == "Davante Adams" and s.jersey == 17 and s.team == "LA" and s.player_kalshi_id
    s = classify(by_ticker("KXNFLPASSYDS-26SEP10SFLAR-SFBPURDY13-350"))
    assert s.player_name == "Brock Purdy" and s.threshold == 350 and s.team == "SF" and s.stat == "passing_yards"
    s = classify(by_ticker("KXNFLTD-26SEP10SFLAR-SFJJAMES29-1"))
    assert s.stat == "touchdowns" and s.threshold == 1 and s.player_name == "Jordan James"
    s = classify(by_ticker("KXNFLREC-26SEP10SFLAR-LARDADAMS17-10"))
    assert s.stat == "receptions" and s.threshold == 10


def test_win_margin_and_tie():
    s = classify(by_ticker("KXNFLWINMARGIN-26SEP14DENKC-KC7TO14"))
    assert s.family == "WIN_MARGIN_BUCKET" and s.team == "KC" and s.range_lo == 7 and s.range_hi == 14
    s = classify(by_ticker("KXNFLWINMARGIN-26SEP14DENKC-TIE"))
    assert s.is_tie_leg


def test_period_families():
    s = classify(by_ticker("KXNFL1HSPREAD-26SEP14DENKC-KC8"))
    assert s.family == "SPREAD" and s.period == "1H" and s.team == "KC" and s.floor_strike == 7.5
    s = classify(by_ticker("KXNFL1Q-26SEP14DENKC-TIE"))
    assert s.family == "PERIOD_WINNER" and s.period == "1Q" and s.is_tie_leg
    s = classify(by_ticker("KXNFL1HFT-26SEP14DENKC-TIEKC"))
    assert s.family == "HALF_FULL_RESULT"


def test_game_winner():
    s = classify(by_ticker("KXNFLGAME-26SEP21NYGLAR-NYG"))
    assert s.family == "GAME_WINNER" and s.team == "NYG" and s.away_team == "NYG" and s.home_team == "LA"


def test_season_wins_ge():
    s = classify(by_ticker("KXNFLWINS-27IND-9"))
    assert s.family == "SEASON_WINS" and s.threshold == 9 and s.operator == ">=" and s.team == "IND"


def test_first_td_none_and_team():
    s = classify(by_ticker("KXNFLFIRSTTD-26SEP10SFLAR-NONE"))
    assert s.family == "FIRST_TD_SCORER" and s.is_none_leg
    s = classify(by_ticker("KXNFLFIRSTTDTEAM-26SEP14DENKC-KC"))
    assert s.family == "FIRST_TD_TEAM" and s.team == "KC"


def test_nothing_single_game_is_unknown_and_report_coverage():
    counts = collections.Counter()
    unknown = []
    low = []
    for m in SAMPLES:
        s = classify(m)
        counts[s.family] += 1
        if s.family == UNKNOWN:
            unknown.append(m["ticker"])
        if s.scope == "GAME" and s.game_date and s.confidence < 0.8:
            low.append((m["ticker"], s.notes))
    nfl_game_series_unknown = [t for t in unknown if parse_event_ticker(t.rsplit("-", 1)[0])]
    assert not nfl_game_series_unknown, nfl_game_series_unknown[:10]
    # every KXNFL* series in the fixture must have a family (unknowns are logged, not tolerated silently)
    kxnfl_unknown = sorted({t.split("-")[0] for t in unknown if t.startswith("KXNFL")})
    assert not kxnfl_unknown, kxnfl_unknown
    # single-game markets must parse with high confidence
    assert not low, low[:10]


def test_structured_floor_and_margin_or_more():
    s = classify(by_ticker("KXNFLTD-26AUG13ARILV-LVAJEANTY2-1"))
    assert s.threshold == 1 and s.operator == ">=" and s.confidence >= 0.8
    s = classify(by_ticker("KXNFLWINMARGIN-26SEP13CLEJAC-CLE15PLUS"))
    assert s.range_lo == 15 and s.range_hi is None and s.team == "CLE"
    s = classify(by_ticker("KXNFLRACE-26SEP14DENKC-35-NONE"))
    assert s.family == "RACE_TO_N" and s.is_none_leg and s.threshold == 35 and s.home_team == "KC"


def test_not_nfl_prefixes():
    assert classify({"ticker": "KXSBUX-27JANSTORES-41800", "event_ticker": "KXSBUX-27JANSTORES"}).family == "NOT_NFL"
    assert classify({"ticker": "KXNFLXA-28JANHEAD-20000", "event_ticker": "KXNFLXA-28JANHEAD"}).family == "NOT_NFL"
    assert classify({"ticker": "KXAFCCLGAME-26AUG11JAZITJ-TIE", "event_ticker": "KXAFCCLGAME-26AUG11JAZITJ"}).family == "NOT_NFL"


def test_anytime_td_without_strike():
    s = classify({"ticker": "KXNFLANYTD-26FEB08SEANE-NEMHOLLINS13", "event_ticker": "KXNFLANYTD-26FEB08SEANE", "title": "Mack Hollins: Anytime Touchdown",
                  "strike_type": "structured", "custom_strike": {"football_player": "x", "football_team": "y"}})
    assert s.family == "PLAYER_STAT" and s.stat == "touchdowns" and s.threshold == 1 and s.operator == ">=" and s.player_name == "Mack Hollins" and s.team == "NE"
