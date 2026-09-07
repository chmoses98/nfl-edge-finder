"""Decision-time executable price resolution, against real capture layouts.

The property under test is the one that costs money if it is wrong: a RECOMMENDED record must rest on a
price that was CONFIRMED to exist recently, and "recently" must be measured against the right timestamp.

The capture is change-suppressed, so the naive reading -- "the newest quote row is 3 hours old, therefore
the price is 3 hours stale" -- rejects every quiet book on the board. The correct reading is that a quiet
book confirmed thirty seconds ago is perfectly current. These tests pin both halves: a quiet-but-confirmed
market is FRESH, and an unconfirmed one is not, however recent its last row.
"""
import gzip  # noqa: F401  (kept: capture fixtures mirror the on-disk layout, some of which is gzipped)
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.execution import quotes as Q  # noqa: E402

NOW = datetime(2026, 9, 7, 15, 40, tzinfo=timezone.utc)
TICKER = "KXNFLGAME-26SEP09NESEA-SEA"
SERIES = "KXNFLGAME"


def _run_id(dt):
    return dt.strftime("%Y%m%dT%H%M%SZ")


def capture(tmp_path, runs):
    """Build a capture tree.

    `runs` is [(when, {series: complete}, [quote rows])] -- exactly the shape scripts/kalshi/capture.py
    writes: a manifest per run, and a quotes file holding ONLY the markets whose price changed.
    """
    root = tmp_path / "md"
    for when, series, rows in runs:
        rid = _run_id(when)
        day = root / "data" / "kalshi" / "capture" / when.strftime("%Y-%m-%d")
        day.mkdir(parents=True, exist_ok=True)
        (day / f"{rid}.manifest.json").write_text(json.dumps({
            "run_id": rid, "started_at": when.isoformat(),
            "series": {s: {"n": 10, "complete": c, "tier": "FULL"} for s, c in series.items()},
            "partial": not all(series.values()),
        }))
        if rows:
            (day / f"{rid}.quotes.jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in rows))
    return str(root)


def quote_row(when, ticker=TICKER, yes_ask=0.62, yes_bid=0.60, no_ask=0.40, no_bid=0.38, status="active"):
    return {"ticker": ticker, "series_ticker": SERIES, "observed_at": when.isoformat(),
            "yes_bid": yes_bid, "yes_ask": yes_ask, "no_bid": no_bid, "no_ask": no_ask, "status": status}


def state(tmp_path, mapping):
    p = tmp_path / "md" / "data" / "kalshi" / "capture" / "state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"fingerprints": {}, "last_seen": mapping}))


def resolve(md, side="YES", **kw):
    return Q.resolve_decision_quote(Q.CaptureIndex(md), TICKER, side, series_ticker=SERIES, now=NOW, **kw)


# ---- the happy path --------------------------------------------------------------------------------

def test_a_recently_confirmed_quote_is_fresh_and_executable(tmp_path):
    md = capture(tmp_path, [(NOW - timedelta(minutes=4), {SERIES: True},
                             [quote_row(NOW - timedelta(minutes=4))])])
    q = resolve(md)
    assert q.state == Q.FRESH and q.is_actionable
    assert q.executable_price == 0.62, "the YES side pays the YES ask"
    assert q.age_minutes == pytest.approx(4.0, abs=0.1)


def test_the_no_side_pays_the_no_ask(tmp_path):
    md = capture(tmp_path, [(NOW - timedelta(minutes=2), {SERIES: True},
                             [quote_row(NOW - timedelta(minutes=2))])])
    assert resolve(md, side="NO").executable_price == 0.40


def test_the_midpoint_is_never_returned_as_an_executable_price(tmp_path):
    """You cannot trade an average of two prices."""
    md = capture(tmp_path, [(NOW - timedelta(minutes=2), {SERIES: True},
                             [quote_row(NOW - timedelta(minutes=2), yes_bid=0.50, yes_ask=0.70)])])
    q = resolve(md)
    assert q.executable_price == 0.70
    assert 0.60 not in (q.executable_price, q.executable_bid), "a midpoint leaked into the executable price"


# ---- change suppression: old is not stale ----------------------------------------------------------

def test_an_unchanged_quote_is_current_when_the_capture_confirmed_it(tmp_path):
    """THE central case.

    The price last MOVED three hours ago and the capture has confirmed the market every ten minutes since.
    That is a quiet book, not a stale one, and rejecting it would reject most of the board.
    """
    moved = NOW - timedelta(hours=3)
    runs = [(moved, {SERIES: True}, [quote_row(moved)])]
    runs += [(NOW - timedelta(minutes=m), {SERIES: True}, []) for m in (20, 10, 3)]
    md = capture(tmp_path, runs)

    q = resolve(md)
    assert q.state == Q.FRESH, q.reason
    assert q.executable_price == 0.62
    assert q.quote_moved_at.startswith(moved.isoformat()[:16]), "the price move time must be preserved"
    assert q.age_minutes < 5, "freshness is measured from CONFIRMATION, not from the last price change"
    assert any("still current" in n for n in q.notes)


def test_a_recent_row_with_no_recent_confirmation_is_not_fresh(tmp_path):
    """The mirror image. A row exists, but nothing since confirms the market is still there."""
    md = capture(tmp_path, [(NOW - timedelta(minutes=90), {SERIES: True},
                             [quote_row(NOW - timedelta(minutes=90))])])
    q = resolve(md)
    assert q.state == Q.STALE
    assert "beyond" in q.reason


# ---- confirmation quality --------------------------------------------------------------------------

def test_ticker_level_confirmation_is_preferred_over_the_series_manifest(tmp_path):
    moved = NOW - timedelta(hours=2)
    recent = NOW - timedelta(minutes=6)
    md = capture(tmp_path, [(moved, {SERIES: True}, [quote_row(moved)]),
                            (recent, {SERIES: True}, [])])
    state(tmp_path, {TICKER: _run_id(recent)})
    q = resolve(md)
    assert q.confirmation_basis == Q.CONFIRM_TICKER
    assert q.state == Q.FRESH


def test_a_partial_series_fetch_is_not_a_confirmation(tmp_path):
    """A failed fetch says nothing about the market. Walking back to the last GOOD run is the honest read."""
    good = NOW - timedelta(minutes=40)
    md = capture(tmp_path, [(good, {SERIES: True}, [quote_row(good)]),
                            (NOW - timedelta(minutes=3), {SERIES: False}, [])])
    q = resolve(md)
    assert q.state == Q.STALE, "the newest run failed for this series, so it confirms nothing"
    assert q.confirmation_basis == Q.CONFIRM_SERIES
    assert q.age_minutes == pytest.approx(40.0, abs=0.2)


def test_a_series_never_confirmed_is_unconfirmed_not_stale(tmp_path):
    md = capture(tmp_path, [(NOW - timedelta(minutes=3), {"KXNFLTOTAL": True}, [])])
    q = resolve(md)
    assert q.state == Q.UNCONFIRMED
    assert q.executable_price is None, "an unconfirmed market must not surface a price at all"


def test_no_capture_at_all_is_unconfirmed(tmp_path):
    (tmp_path / "md").mkdir()
    q = resolve(str(tmp_path / "md"))
    assert q.state == Q.UNCONFIRMED and q.executable_price is None


# ---- refusals --------------------------------------------------------------------------------------

def test_a_confirmed_market_with_no_ask_on_our_side_is_no_quote(tmp_path):
    md = capture(tmp_path, [(NOW - timedelta(minutes=2), {SERIES: True},
                             [quote_row(NOW - timedelta(minutes=2), yes_ask=None)])])
    q = resolve(md)
    assert q.state == Q.NO_QUOTE and not q.is_actionable
    assert "midpoint is not a substitute" in q.reason


def test_a_closed_market_is_not_tradable_however_recent(tmp_path):
    md = capture(tmp_path, [(NOW - timedelta(minutes=1), {SERIES: True},
                             [quote_row(NOW - timedelta(minutes=1), status="closed")])])
    q = resolve(md)
    assert q.state == Q.UNCONFIRMED
    assert "not a tradable state" in q.reason


def test_nothing_is_interpolated_between_observations(tmp_path):
    """Two rows at 0.55 and 0.65 must never produce 0.60 for a moment in between."""
    a, b = NOW - timedelta(minutes=30), NOW - timedelta(minutes=2)
    md = capture(tmp_path, [(a, {SERIES: True}, [quote_row(a, yes_ask=0.55)]),
                            (b, {SERIES: True}, [quote_row(b, yes_ask=0.65)])])
    assert resolve(md).executable_price == 0.65, "the resolved price must be an OBSERVED one"


def test_the_freshness_window_is_configurable(tmp_path):
    md = capture(tmp_path, [(NOW - timedelta(minutes=25), {SERIES: True},
                             [quote_row(NOW - timedelta(minutes=25))])])
    assert resolve(md).state == Q.STALE, "25 min is outside the 15 min desk default"
    assert resolve(md, max_age_minutes=30.0).state == Q.FRESH


def test_the_default_window_matches_the_capture_cadence(tmp_path):
    """15 minutes accepts one on-time ~10 minute capture and rejects a missed one."""
    assert Q.DEFAULT_MAX_QUOTE_AGE_MIN == 15.0
