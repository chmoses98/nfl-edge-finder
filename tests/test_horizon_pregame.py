"""Every horizon quote must be strictly pregame.

Horizons are offsets from an anchor. When a market could not be matched to an nflverse kickoff the anchor
falls back to the market's close time, which is after the game ends -- so its "T-0" quote is a post-game
price. Measured on the cached KXNFLGAME/KXNFLSPREAD backfill: 0% of kickoff-anchored T-0 quotes sit at
settled certainty versus 65% of close_time-anchored ones. Studies of time-to-kickoff must use the former.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def test_snapshot_choice_is_at_or_before_the_horizon():
    """The snapshot for horizon H is the last candle at or before anchor - H, never one after it."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bq", os.path.join(ROOT, "scripts", "kalshi", "backfill_quotes.py"))
    bq = importlib.util.module_from_spec(spec); spec.loader.exec_module(bq)
    anchor = 1_000_000
    cands = [{"end_period_ts": anchor - d, "yes_bid": {"close": "0.40"}, "yes_ask": {"close": "0.44"}}
             for d in (7200, 3600, 60, 0, -60, -3600)]
    cands.sort(key=lambda x: x["end_period_ts"])
    for name, mins in bq.HORIZONS:
        cut = anchor - mins * 60
        prior = [x for x in cands if x["end_period_ts"] <= cut]
        if not prior:
            continue
        assert prior[-1]["end_period_ts"] <= cut
        assert bq.snapshot(prior[-1])["ts"] <= cut


def test_kickoff_anchor_is_required_for_pregame_claims():
    rows = [{"anchor_kind": "kickoff"}, {"anchor_kind": "close_time"}]
    pregame = [r for r in rows if r["anchor_kind"] == "kickoff"]
    assert len(pregame) == 1


def test_efficiency_map_filters_non_kickoff_anchors():
    src = open(os.path.join(ROOT, "scripts", "research", "efficiency_map.py")).read()
    assert 'r.get("anchor_kind") != "kickoff"' in src, \
        "the efficiency map must drop close_time-anchored rows or its T-0 is post-game"
