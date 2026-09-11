import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import date
from tennis_edge.pricing.competition import classify_competition, lookup_surface
from tennis_edge.identity.kalshi_map import KalshiPlayerMapper


def test_classify():
    assert classify_competition("US Open Men Singles", "ATP")["level"] == "GRAND_SLAM"
    assert classify_competition("M15 Budapest", "ATP")["level"] == "ITF"
    assert classify_competition("W35 Zhengzhou", "WTA")["tour"] == "WTA"
    assert classify_competition("ATP Challenger Seville", "ATP")["level"] == "CHALLENGER"
    assert classify_competition("US Open Mixed Doubles", "MIXED")["discipline"] == "mixed"
    assert lookup_surface("ATP Winston Salem", None, {"winston salem": "Hard"})[0] == "Hard"
    assert lookup_surface("ATP Nowhere", None, {})[0] is None


def test_mapper_fails_closed_on_namesakes(tmp_path):
    st = {"ATP": {"players": {"1": {"name": "Alexander Zverev", "last_date": "2026-08-30"}, "2": {"name": "Alexander Zverev", "last_date": "2026-07-01"},
                              "3": {"name": "Karen Khachanov", "last_date": "2026-08-30"}, "4": {"name": "Old Namesake", "last_date": "2010-01-01"}, "5": {"name": "Old Namesake", "last_date": "2026-01-01"}}}}
    mp = KalshiPlayerMapper(st, cache_path=str(tmp_path / "c.json"))
    today = date(2026, 9, 11)
    assert mp.resolve("ATP", "Alexander Zverev", "u1", today)["status"] == "AMBIGUOUS"
    r = mp.resolve("ATP", "Karen Khachanov", "u2", today)
    assert r["status"] == "MAPPED" and r["player_id"] == "3" and r["confidence"] == 1.0
    assert mp.resolve("ATP", "Old Namesake", None, today)["player_id"] == "5"      # one recently-active namesake
    assert mp.resolve("ATP", "Nobody Here", None, today)["status"] == "UNMAPPED"
    assert mp.resolve("ATP", "Karen Khachanov", "u2", today)["source"] == "cache"
