"""settle_ledger: candle quotes → canonical close respects the conservative cutoff; exchange truth drives grading."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "ops"))
from datetime import datetime, timezone, timedelta
import importlib.util

spec = importlib.util.spec_from_file_location("settle_ledger", os.path.join(os.path.dirname(__file__), "..", "scripts", "ops", "settle_ledger.py"))
sl = importlib.util.module_from_spec(spec); spec.loader.exec_module(sl)
from tennis_edge.ledger.close import canonical_close


def test_quotes_from_candles_and_conservative_cutoff():
    t0 = int(datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc).timestamp())
    rec = {"candles_60": [{"end_period_ts": t0 - 10 * 3600, "yes_bid": {"close_dollars": "0.40"}, "yes_ask": {"close_dollars": "0.44"}},
                          {"end_period_ts": t0 - 8 * 3600, "yes_bid": {"close_dollars": "0.45"}, "yes_ask": {"close_dollars": "0.47"}},
                          {"end_period_ts": t0 - 2 * 3600, "yes_bid": {"close_dollars": "0.90"}, "yes_ask": {"close_dollars": "0.92"}},   # in-play
                          {"bad": True}]}
    qs = sl.quotes_from_candles(rec)
    assert len(qs) == 3
    close_t = datetime.fromtimestamp(t0, tz=timezone.utc)
    sched = close_t - timedelta(hours=3)          # nominal start 3h before close (ITF-style unreliable)
    cutoff = min(sched, close_t - timedelta(hours=sl.PREGAME_HOURS))
    cc = canonical_close(qs, cutoff, None)
    assert cc.quote.yes_bid == 0.45 and cc.close_basis == "SCHEDULED_MINUS_MARGIN"   # the in-play 0.90 quote is excluded
