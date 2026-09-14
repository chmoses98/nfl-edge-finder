"""Fakes for the LIVE pre-trade path: a Kalshi venue that answers two GETs, and a place to keep evidence.

The live worker asks the venue about ONE contract and stores the answer before it gates. These fakes stand
in for the venue and the branch so the whole leg -- fetch, persist, read back, gate, sign -- runs in a test
with no network and no git remote.

The client serves exactly the two endpoints `nfl_edge/handicap/live_evidence.py` calls and nothing else, in
the shapes `docs/KALSHI_API_NOTES.md` records: `*_dollars` decimal strings on the market object, and an
`orderbook_fp` carrying RESTING BIDS per side. It also stamps `_meta.retrieved_at`, because the retrieval
timestamp is the thing the freshness gate measures from and a fake that skipped it would let a test pass
against evidence that could not have existed.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap import evidence_store as ES     # noqa: E402
from nfl_edge.kalshi import client as KC               # noqa: E402

# The same deep, one-level book the capture-stream fixtures use, so a live test and an archival test are
# comparing the same market rather than two different ones.
DEEP = [(0.56, 100000.0)]


class _Stats:
    def __init__(self):
        self.requests = 0


class FakeKalshiClient:
    """A venue that answers `GET /markets/{t}` and `GET /markets/{t}/orderbook`, and can refuse to.

    Every failure mode the live path must block on has a knob: a market fetch that raises, a book fetch that
    raises, a book that comes back empty, and a market whose status is not tradable. None of them may produce
    an approval.
    """

    base_url = "https://api.elections.kalshi.test/trade-api/v2"

    def __init__(self, *, ask=0.56, ladder=None, status="active", retrieved_at=None,
                 book_retrieved_at=None, fail_market=False, fail_book=False, empty_book=False,
                 no_market=False, no_market_timestamp=False, per_ticker=None):
        self.ask = ask
        self.ladder = DEEP if ladder is None else ladder
        self.status = status
        self.retrieved_at = retrieved_at or datetime(2026, 9, 9, 13, 4, tzinfo=timezone.utc)
        self.book_retrieved_at = book_retrieved_at
        self.fail_market = fail_market
        self.fail_book = fail_book
        self.empty_book = empty_book
        self.no_market = no_market
        self.no_market_timestamp = no_market_timestamp
        self.per_ticker = per_ticker or {}
        self.calls = []
        self.stats = _Stats()

    # ---- per-ticker overrides ------------------------------------------------------------
    def _cfg(self, ticker, name):
        return (self.per_ticker.get(ticker) or {}).get(name, getattr(self, name))

    def _meta(self, url, when):
        return {"url": url, "retrieved_at": when.isoformat(), "latency_ms": 11, "bytes": 256}

    # ---- the two endpoints ---------------------------------------------------------------
    def market(self, ticker):
        self.calls.append(("market", ticker))
        self.stats.requests += 1
        if self._cfg(ticker, "fail_market"):
            raise KC.KalshiError(503, f"markets/{ticker}", "service unavailable")
        if self._cfg(ticker, "no_market"):
            return {"_meta": self._meta(f"markets/{ticker}", self._cfg(ticker, "retrieved_at"))}
        ask = float(self._cfg(ticker, "ask"))
        when = self._cfg(ticker, "retrieved_at")
        body = {
            "market": {
                "ticker": ticker,
                "status": self._cfg(ticker, "status"),
                # Both denominations, exactly as the API reports them. The cents fields are here on purpose:
                # a reader that preferred them would price a 56c contract at 56 dollars, and the live path
                # must be shown to read the dollar fields.
                "yes_bid": int(round((ask - 0.02) * 100)),
                "yes_ask": int(round(ask * 100)),
                "no_bid": int(round((1 - ask - 0.02) * 100)),
                "no_ask": int(round((1 - ask) * 100)),
                "yes_bid_dollars": f"{ask - 0.02:.4f}",
                "yes_ask_dollars": f"{ask:.4f}",
                "no_bid_dollars": f"{1 - ask - 0.02:.4f}",
                "no_ask_dollars": f"{1 - ask:.4f}",
                "last_price_dollars": f"{ask:.4f}",
                "volume_fp": "1200", "open_interest_fp": "4000", "liquidity_dollars": "900.0000",
                "close_time": "2026-09-09T23:00:00Z",
            },
            "_meta": self._meta(f"markets/{ticker}", when),
        }
        if self._cfg(ticker, "no_market_timestamp"):
            body["_meta"].pop("retrieved_at")
        return body

    def orderbook(self, ticker, depth=None):
        self.calls.append(("orderbook", ticker, depth))
        self.stats.requests += 1
        if self._cfg(ticker, "fail_book"):
            raise KC.KalshiError(500, f"markets/{ticker}/orderbook", "boom")
        when = self._cfg(ticker, "book_retrieved_at") or self._cfg(ticker, "retrieved_at")
        if self._cfg(ticker, "empty_book"):
            return {"orderbook_fp": {}, "_meta": self._meta(f"markets/{ticker}/orderbook", when)}
        ladder = self._cfg(ticker, "ladder")
        # Buying YES lifts NO bids: a NO bid at (1-p) is a YES ask at p.
        return {
            "orderbook_fp": {
                "no_dollars": [[f"{1 - p:.4f}", f"{s}"] for p, s in sorted(ladder, key=lambda x: -x[0])],
                "yes_dollars": [["0.5000", "10"]],
            },
            "_meta": self._meta(f"markets/{ticker}/orderbook", when),
        }


def fresh_client(now, *, seconds_old=20, **kw):
    """A venue whose answer was retrieved `seconds_old` before the approval instant."""
    kw.setdefault("retrieved_at", now - timedelta(seconds=seconds_old))
    return FakeKalshiClient(**kw)


def evidence_dir(tmp_path, name="evidence"):
    """A DirectoryEvidenceStore rooted in the test's own tmp_path, plus the root it writes under."""
    root = str(tmp_path / name)
    return ES.DirectoryEvidenceStore(root), root
