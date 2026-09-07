"""Decision-time executable quote resolution.

The handicap packet and the price you can actually trade are two different facts with two different
freshness requirements, and conflating them is how a desk records a bet at a price that no longer exists:

  A) MODEL / INFORMATION SNAPSHOT   The shadow-pricing run the packet was built from. It may legitimately be
                                    hours old: a forecast does not decay on a ten-minute clock, and
                                    recomputing it at decision time would silently change the forecast that
                                    the recommendation claims to be based on. Frozen, always.

  B) EXECUTABLE MARKET PRICE        What you can pay right now. It decays on a ten-minute clock, because the
                                    conductor captures roughly that often. This module resolves (B), and
                                    only (B).

This module never touches (A). It reads the capture stream, returns a side-specific executable bid/ask with
the timestamps that justify it, and says nothing about fair value.

CHANGE-SUPPRESSED CAPTURE, AND WHY "OLD" IS NOT "STALE"
-------------------------------------------------------
`scripts/kalshi/capture.py` writes a quote row only when the price fingerprint CHANGES. A market that has not
moved in three hours has no row in the last seventeen captures -- and is nonetheless perfectly current, because
the capture confirmed it seventeen times. Treating "last written row is 3h old" as staleness would reject
every quiet book on the board, which is most of them.

So two timestamps are tracked and they mean different things:

    quote_moved_at      when the price last CHANGED. Can be arbitrarily old on a quiet market. Not staleness.
    confirmed_at        when the capture last CONFIRMED this ticker was open at that price. THIS is freshness.

`confirmed_at` is established at the strongest level available, and the level used is recorded so a reader
can see how much the confirmation is worth:

    TICKER_LAST_SEEN    capture/state.json records the run in which each ticker was last observed open.
                        Exact: this ticker, this run. Preferred whenever present.
    SERIES_COMPLETE     the ticker's series was fetched completely in that run's manifest, and the ticker
                        has a written quote no later than it. Strong but series-level: it proves the series
                        was polled successfully, not that this individual ticker came back in the page.

A ticker whose series came back PARTIAL is never confirmed by that run -- a failed fetch is not a
confirmation -- so resolution walks back to the newest run that did succeed.

WHAT THIS MODULE REFUSES TO DO
------------------------------
  * It never returns a midpoint as an executable price. You cannot trade a midpoint. `executable_price` is
    the ask on your side and nothing else.
  * It never interpolates. A price between two observations was never observed.
  * It never infers a quote from an old observation on a market the capture has since stopped confirming.
  * When it cannot establish freshness it says STALE or UNCONFIRMED and returns no price. It does not
    return the best thing it found.
"""
from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

# Desk policy. The conductor captures roughly every 10 minutes, so 15 accepts one on-time capture plus a
# little slack and rejects a missed one. Configurable because it is a policy, not a fact about the world.
DEFAULT_MAX_QUOTE_AGE_MIN = 15.0

FRESH = "FRESH"                    # confirmed inside the window; tradable
STALE = "STALE"                    # confirmed, but too long ago
UNCONFIRMED = "UNCONFIRMED"        # no capture run confirms this ticker at all
NO_QUOTE = "NO_QUOTE"              # confirmed open, but the book has no usable price on our side

CONFIRM_TICKER = "TICKER_LAST_SEEN"
CONFIRM_SERIES = "SERIES_COMPLETE"


@dataclass
class DecisionQuote:
    """The freshest confirmed executable quote for one ticker on one side, with its justification."""
    ticker: str
    side: str
    state: str
    executable_price: float | None = None     # the ASK on our side. Never a midpoint.
    executable_bid: float | None = None       # what we could sell into, for reference
    yes_bid: float | None = None
    yes_ask: float | None = None
    no_bid: float | None = None
    no_ask: float | None = None
    quote_moved_at: str | None = None         # last observed price CHANGE
    confirmed_at: str | None = None           # last capture confirmation -- freshness is judged on this
    confirmation_basis: str | None = None     # CONFIRM_TICKER / CONFIRM_SERIES
    age_minutes: float | None = None          # now - confirmed_at
    max_age_minutes: float = DEFAULT_MAX_QUOTE_AGE_MIN
    series_ticker: str | None = None
    capture_run_id: str | None = None
    reason: str | None = None
    notes: list = field(default_factory=list)

    @property
    def is_actionable(self) -> bool:
        """Fresh, and carrying a real price on our side. The only state a RECOMMENDED record may rest on."""
        return self.state == FRESH and self.executable_price is not None

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def _iso(t):
    if not t:
        return None
    try:
        dt = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _f(x):
    try:
        v = float(x)
        return None if v != v else v
    except (TypeError, ValueError):
        return None


def _run_started_at(run_id: str, manifest: dict | None) -> datetime | None:
    """A run's time. The manifest's own `started_at` when we have it, else the run id, which encodes it."""
    if manifest:
        t = _iso(manifest.get("started_at"))
        if t:
            return t
    try:
        return datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


class CaptureIndex:
    """Read-only view over the capture stream, built once and queried per ticker.

    Scanning is bounded to the newest `max_runs` runs: resolution only ever needs enough history to find one
    confirmation and one written quote, and the capture directory holds months.
    """

    def __init__(self, md_root: str, max_runs: int = 200):
        self.md_root = md_root
        self.max_runs = max_runs
        self._manifests: list[tuple[str, datetime, dict]] = []   # (run_id, started_at, manifest), newest last
        self._state: dict = {}
        self._loaded = False

    # ---- loading --------------------------------------------------------------------------------
    def _capture_root(self) -> str:
        return os.path.join(self.md_root, "data", "kalshi", "capture")

    def load(self) -> "CaptureIndex":
        if self._loaded:
            return self
        root = self._capture_root()
        paths = sorted(glob.glob(os.path.join(root, "*", "*.manifest.json")))[-self.max_runs:]
        for p in paths:
            run_id = os.path.basename(p).split(".")[0]
            try:
                with open(p) as f:
                    man = json.load(f)
            except (OSError, ValueError):
                continue
            started = _run_started_at(run_id, man)
            if started is None:
                continue
            self._manifests.append((run_id, started, man))
        self._manifests.sort(key=lambda x: x[1])
        state_path = os.path.join(root, "state.json")
        if os.path.exists(state_path):
            try:
                with open(state_path) as f:
                    self._state = json.load(f)
            except (OSError, ValueError):
                self._state = {}
        self._loaded = True
        return self

    # ---- confirmation ---------------------------------------------------------------------------
    def latest_run(self):
        self.load()
        return self._manifests[-1] if self._manifests else None

    def confirmation(self, ticker: str, series_ticker: str | None) -> tuple[datetime | None, str | None,
                                                                           str | None, str | None]:
        """(confirmed_at, basis, run_id, reason-if-none) for one ticker.

        Ticker-level confirmation wins when the capture recorded it. `last_seen` is written by
        scripts/kalshi/capture.py for every ticker returned open in a run, changed or not, which is exactly
        the fact change-suppression otherwise destroys. Captures written before that field existed simply do
        not have it, and resolution falls back to series-level confirmation rather than failing.
        """
        self.load()
        if not self._manifests:
            return None, None, None, "no capture manifests found under data/kalshi/capture"

        last_seen = (self._state.get("last_seen") or {}).get(ticker)
        if last_seen:
            run_id = last_seen if isinstance(last_seen, str) else last_seen.get("run_id")
            for rid, started, _man in reversed(self._manifests):
                if rid == run_id:
                    return started, CONFIRM_TICKER, rid, None
            t = _run_started_at(str(run_id), None)
            if t:
                return t, CONFIRM_TICKER, str(run_id), None

        if not series_ticker:
            return None, None, None, (f"{ticker}: no ticker-level confirmation in capture state and no "
                                      "series ticker to fall back on")
        for rid, started, man in reversed(self._manifests):
            entry = (man.get("series") or {}).get(series_ticker)
            if entry and entry.get("complete"):
                return started, CONFIRM_SERIES, rid, None
        return None, None, None, (f"series {series_ticker!r} was not fetched completely in any of the last "
                                  f"{len(self._manifests)} capture runs")

    # ---- last written quote ---------------------------------------------------------------------
    def last_quote_row(self, ticker: str, not_after: datetime | None = None) -> dict | None:
        """The most recent WRITTEN quote row for a ticker -- i.e. the last time its price moved.

        Files are walked newest-first and the walk stops at the first hit, so a quiet market costs one file
        read more per unchanged interval rather than a full history scan.
        """
        self.load()
        files = sorted(glob.glob(os.path.join(self._capture_root(), "*", "*.quotes.jsonl")))
        for path in reversed(files[-self.max_runs:]):
            best = None
            try:
                with open(path) as f:
                    for line in f:
                        if ticker not in line:
                            continue                    # cheap pre-filter before JSON parsing
                        try:
                            r = json.loads(line)
                        except ValueError:
                            continue
                        if r.get("ticker") != ticker:
                            continue
                        ts = _iso(r.get("observed_at"))
                        if not_after is not None and ts is not None and ts > not_after:
                            continue
                        if best is None or (ts and _iso(best.get("observed_at")) and
                                            ts > _iso(best["observed_at"])):
                            best = r
            except OSError:
                continue
            if best is not None:
                return best
        return None


def _side_prices(row: dict) -> dict:
    """Kalshi reports `*_dollars` fields; the shadow ledger normalises them. Accept either shape."""
    def pick(*names):
        for n in names:
            v = _f(row.get(n))
            if v is not None:
                return v
        return None
    return {
        "yes_bid": pick("yes_bid", "yes_bid_dollars"),
        "yes_ask": pick("yes_ask", "yes_ask_dollars"),
        "no_bid": pick("no_bid", "no_bid_dollars"),
        "no_ask": pick("no_ask", "no_ask_dollars"),
    }


def resolve_decision_quote(index: "CaptureIndex", ticker: str, side: str, *,
                           series_ticker: str | None = None, now: datetime | None = None,
                           max_age_minutes: float = DEFAULT_MAX_QUOTE_AGE_MIN) -> DecisionQuote:
    """The freshest CONFIRMED side-specific executable quote, or an explicit refusal.

    Returns a DecisionQuote in exactly one of four states, and only FRESH is actionable:

        FRESH        confirmed within `max_age_minutes` and carrying an ask on our side
        NO_QUOTE     confirmed and current, but there is no usable ask on our side
        STALE        the newest confirmation is older than the window
        UNCONFIRMED  no capture run confirms this ticker

    Nothing here consults the shadow ledger, so the model's forecast and its snapshot lineage are untouched
    by definition, not by discipline.
    """
    now = now or datetime.now(timezone.utc)
    side = (side or "YES").upper()
    q = DecisionQuote(ticker=ticker, side=side, state=UNCONFIRMED, max_age_minutes=max_age_minutes,
                      series_ticker=series_ticker)

    confirmed_at, basis, run_id, reason = index.confirmation(ticker, series_ticker)
    if confirmed_at is None:
        q.reason = reason
        return q

    q.confirmed_at = confirmed_at.isoformat()
    q.confirmation_basis = basis
    q.capture_run_id = run_id
    q.age_minutes = round((now - confirmed_at).total_seconds() / 60.0, 2)

    row = index.last_quote_row(ticker, not_after=confirmed_at)
    if row is None:
        q.state = UNCONFIRMED
        q.reason = (f"{ticker} was confirmed open at {q.confirmed_at} but the capture stream holds no "
                    "written quote for it, so there is no observed price to use")
        return q

    prices = _side_prices(row)
    q.yes_bid, q.yes_ask = prices["yes_bid"], prices["yes_ask"]
    q.no_bid, q.no_ask = prices["no_bid"], prices["no_ask"]
    q.quote_moved_at = row.get("observed_at")
    # The executable price is the ask on OUR side. Never the midpoint: a midpoint is an average of two
    # prices, and you cannot trade an average.
    q.executable_price = q.yes_ask if side == "YES" else q.no_ask
    q.executable_bid = q.yes_bid if side == "YES" else q.no_bid

    moved = _iso(q.quote_moved_at)
    if moved is not None and confirmed_at > moved:
        q.notes.append(
            f"price unchanged since {q.quote_moved_at}; still current -- the capture confirmed this series "
            f"at {q.confirmed_at} and writes a row only on a price CHANGE")

    status = (row.get("status") or "").lower()
    if status and status not in ("active", "open", "initialized"):
        q.state = UNCONFIRMED
        q.reason = f"{ticker} last reported status {status!r}, which is not a tradable state"
        return q

    if q.age_minutes > max_age_minutes:
        q.state = STALE
        q.reason = (f"newest confirmation for {ticker} is {q.age_minutes:.1f} min old, beyond the "
                    f"{max_age_minutes:.0f} min decision-time freshness window")
        return q

    if q.executable_price is None:
        q.state = NO_QUOTE
        q.reason = (f"{ticker} is current but carries no {side} ask; there is no price to pay, and a "
                    "midpoint is not a substitute for one")
        return q

    q.state = FRESH
    return q


def resolve_from_root(md_root: str, ticker: str, side: str, *, series_ticker: str | None = None,
                      now: datetime | None = None,
                      max_age_minutes: float = DEFAULT_MAX_QUOTE_AGE_MIN,
                      max_runs: int = 200) -> DecisionQuote:
    """Convenience wrapper that builds a one-shot index. Prefer reusing a CaptureIndex across a batch."""
    return resolve_decision_quote(CaptureIndex(md_root, max_runs=max_runs), ticker, side,
                                  series_ticker=series_ticker, now=now, max_age_minutes=max_age_minutes)
