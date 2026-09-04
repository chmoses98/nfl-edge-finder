"""The 2025 efficiency map is only as good as the candle parser.

A first version of snapshot() read `close_dollars`/`volume_fp`, which the candlestick endpoint does not
return. It produced 54,364 structurally valid rows in which every single price was null, and nothing in the
pipeline objected. These tests pin the parser to a frozen real API response so that failure mode is loud.
"""
import importlib.util, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("bq", os.path.join(ROOT, "scripts", "kalshi", "backfill_quotes.py"))
bq = importlib.util.module_from_spec(spec); spec.loader.exec_module(bq)
FIXTURE = json.load(open(os.path.join(ROOT, "tests", "fixtures", "kalshi_candlesticks.json")))


def test_snapshot_extracts_executable_quotes_from_real_response():
    quoted = [c for c in FIXTURE["h60"] if (c.get("yes_bid") or {}).get("close") is not None]
    assert quoted, "fixture must contain at least one quoted candle"
    for c in quoted:
        s = bq.snapshot(c)
        assert s["bid"] is not None and s["ask"] is not None, "bid/ask must parse from the real field names"
        assert 0.0 <= s["bid"] <= s["ask"] <= 1.0
        assert s["ts"] == c["end_period_ts"]


def test_snapshot_accepts_the_suffixed_field_variant():
    s = bq.snapshot({"end_period_ts": 1, "yes_bid": {"close_dollars": "0.40"}, "yes_ask": {"close_dollars": "0.44"},
                     "price": {"close_dollars": "0.42"}, "volume_fp": "7", "open_interest_fp": "9"})
    assert (s["bid"], s["ask"], s["last"], s["vol"], s["oi"]) == (0.40, 0.44, 0.42, 7.0, 9.0)


def test_empty_book_is_flagged_not_treated_as_a_penny_wide_quote():
    s = bq.snapshot({"end_period_ts": 1, "yes_bid": {"close": "0.0000"}, "yes_ask": {"close": "1.0000"}})
    assert s["book_empty"] is True, "bid 0 / ask 1 is the absence of a market, not a tradable spread"
    s2 = bq.snapshot({"end_period_ts": 1, "yes_bid": {"close": "0.4000"}, "yes_ask": {"close": "0.4400"}})
    assert s2["book_empty"] is False


def test_missing_prices_yield_none_rather_than_zero():
    s = bq.snapshot({"end_period_ts": 1, "yes_bid": {"close": None}, "yes_ask": {"close": None},
                     "price": {"close": None, "mean": None}})
    assert s["bid"] is None and s["ask"] is None and s["last"] is None
    assert s["book_empty"] is False
