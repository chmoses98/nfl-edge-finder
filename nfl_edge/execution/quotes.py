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

AS OF THE DECISION, NOT AS OF THE IMPORT
----------------------------------------
Every question here is asked at the DECISION timestamp, never at the moment the importer happens to run. The
Airtable bridge is retrospective archival transport on a twelve-hour cadence, so "is this price fresh?"
evaluated at import time answers a question nobody asked and would fail every recommendation whose game had
since kicked off.

So `as_of` is the recommendation's `created_at`, and two rules follow from it:

  * Evidence AFTER `as_of` is invisible. A capture that happened after the decision cannot be used to
    validate the decision -- it is information the handicapper did not have, and using it would let a bet
    that was stale when made pass because the market was re-captured later.
  * Freshness is measured from `as_of` backwards. A quote confirmed 4 minutes before the decision is fresh
    whether the importer reads it 10 seconds or 10 days later. Import latency cannot change whether a
    historically valid recommendation passes.

WHICH TIMESTAMP MEANS "THE INFORMATION EXISTED"
-----------------------------------------------
A capture run works through ~270 series over several minutes, so the run's start time and the moment a given
series actually came back are materially different. Using run-start for everything is wrong in one direction
that matters: it claims information was available EARLIER than it was, which would let a capture taken after
the decision look like it came before.

The manifest therefore records `observed_at` per series, and that is used where present. Where only run-level
timestamps exist (captures written before that field), the conservative choice is made per question:

    "did this predate the decision?"   ->  the LATEST plausible time (finished_at, else start)
    "how old is it?"                   ->  the EARLIEST plausible time (started_at)

Both directions round against the recommendation, so an old capture can only ever be judged less usable than
it really was, never more.

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
    as_of: str | None = None                  # the DECISION timestamp every question here was asked at
    age_minutes: float | None = None          # as_of - confirmed_at. Never wall-clock minus confirmed_at.
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
    """A run's start. The manifest's own `started_at` when we have it, else the run id, which encodes it."""
    if manifest:
        t = _iso(manifest.get("started_at"))
        if t:
            return t
    try:
        return datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def series_times(run_id: str, manifest: dict | None, series_ticker: str | None) -> tuple[datetime | None,
                                                                                         datetime | None]:
    """(available_at, age_from) for one series in one run -- the two timestamps, chosen conservatively.

        available_at  the LATEST moment this information could have become knowable. Used to decide whether
                      the evidence predates a decision. Erring late means an ambiguous capture is treated as
                      possibly-after the decision and therefore ignored.
        age_from      the EARLIEST moment it could have been current. Used to measure staleness. Erring
                      early means an ambiguous capture is treated as older than it may be.

    Where the manifest records this series' own `observed_at` -- the moment its fetch actually returned --
    both collapse onto that one exact time and no conservatism is needed. Older captures have only run-level
    timestamps, so the two diverge, and both directions round against the recommendation.
    """
    started = _run_started_at(run_id, manifest)
    entry = ((manifest or {}).get("series") or {}).get(series_ticker) if series_ticker else None
    exact = _iso((entry or {}).get("observed_at"))
    if exact is not None:
        return exact, exact
    finished = _iso((manifest or {}).get("finished_at"))
    return (finished or started), started


class CaptureIndex:
    """Read-only view over the capture stream, built once and queried per ticker.

    TWO DIFFERENT BOUNDS, because the two lookups have different reach:

      max_runs             how far back to look for a CONFIRMATION. Short by design -- a confirmation older
                           than the freshness window is useless, so scanning further only costs time.

      max_quote_scan_runs  how far back to look for the last WRITTEN quote. Must be much longer, because
                           change suppression means a quiet market's last row can be days old and still be
                           the current price. Sharing one bound with `max_runs` would make every market that
                           had not moved in ~33 hours resolve as UNCONFIRMED and block a perfectly good
                           recommendation -- a false negative that would bite hardest on exactly the quiet
                           week-out books where a handicapper is most likely to find something.

    Both scans walk newest-first and stop at the first hit, so an active market costs one file read and only
    a genuinely silent ticker pays for the depth.
    """

    def __init__(self, md_root: str, max_runs: int = 200, max_quote_scan_runs: int = 1500):
        self.md_root = md_root
        self.max_runs = max_runs
        # ~1500 runs is roughly ten days at a 10-minute cadence -- far beyond any plausible quiet period for
        # a market inside its own game week, and still bounded so a ticker that was never captured cannot
        # walk the entire history.
        self.max_quote_scan_runs = max_quote_scan_runs
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

    def confirmation(self, ticker: str, series_ticker: str | None,
                     as_of: datetime | None = None) -> tuple[datetime | None, str | None,
                                                             str | None, str | None]:
        """(confirmed_at, basis, run_id, reason-if-none) -- the newest confirmation AT OR BEFORE `as_of`.

        `as_of` is the DECISION time. A capture that happened after the decision is information the
        handicapper did not have, so it is invisible here: including it would let a bet that was stale when
        it was made pass because the market was re-captured later.

        Ticker-level confirmation wins when the capture recorded it. `last_seen` is written by
        scripts/kalshi/capture.py for every ticker returned open in a run, changed or not, which is exactly
        the fact change-suppression otherwise destroys.

        But `last_seen` is a MUTABLE file holding only the latest run per ticker, so it cannot answer "which
        run last saw this ticker as of last Tuesday". When its run is later than `as_of` it is simply not
        usable evidence for that decision, and resolution falls through to the per-run manifests -- which
        are immutable, one file per run, and can answer the historical question exactly.
        """
        self.load()
        if not self._manifests:
            return None, None, None, "no capture manifests found under data/kalshi/capture"

        last_seen = (self._state.get("last_seen") or {}).get(ticker)
        if last_seen:
            run_id = last_seen if isinstance(last_seen, str) else last_seen.get("run_id")
            for rid, _started, man in reversed(self._manifests):
                if rid == run_id:
                    available_at, age_from = series_times(rid, man, series_ticker)
                    if as_of is None or (available_at is not None and available_at <= as_of):
                        return age_from, CONFIRM_TICKER, rid, None
                    break               # this ticker-level record postdates the decision; fall through
            else:
                t = _run_started_at(str(run_id), None)
                if t is not None and (as_of is None or t <= as_of):
                    return t, CONFIRM_TICKER, str(run_id), None

        if not series_ticker:
            return None, None, None, (f"{ticker}: no ticker-level confirmation at or before "
                                      f"{as_of.isoformat() if as_of else 'now'} and no series ticker to "
                                      "fall back on")
        for rid, _started, man in reversed(self._manifests):
            entry = (man.get("series") or {}).get(series_ticker)
            if not (entry and entry.get("complete")):
                continue
            available_at, age_from = series_times(rid, man, series_ticker)
            if as_of is not None and (available_at is None or available_at > as_of):
                continue                # captured after the decision: not evidence the decision could use
            return age_from, CONFIRM_SERIES, rid, None
        return None, None, None, (
            f"series {series_ticker!r} was not fetched completely in any capture run at or before "
            f"{as_of.isoformat() if as_of else 'now'} (scanned {len(self._manifests)} runs)")

    # ---- last written quote ---------------------------------------------------------------------
    def last_quote_row(self, ticker: str, not_after: datetime | None = None) -> dict | None:
        """The most recent WRITTEN quote row for a ticker -- i.e. the last time its price MOVED.

        Bounded by `max_quote_scan_runs`, not `max_runs`: see the class docstring for why those are different
        numbers. Files are walked newest-first and the walk stops at the first hit, so an active market costs
        one file read and only a silent ticker pays for the depth.
        """
        self.load()
        files = sorted(glob.glob(os.path.join(self._capture_root(), "*", "*.quotes.jsonl")))
        for path in reversed(files[-self.max_quote_scan_runs:]):
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
                           series_ticker: str | None = None, as_of: datetime | None = None,
                           now: datetime | None = None,
                           max_age_minutes: float = DEFAULT_MAX_QUOTE_AGE_MIN) -> DecisionQuote:
    """The freshest CONFIRMED side-specific executable quote AS OF THE DECISION, or an explicit refusal.

    `as_of` is the recommendation's decision timestamp and is the only clock this function reads. Evidence
    after it is invisible; freshness is measured backwards from it. Import latency therefore cannot change
    the verdict: a recommendation that was valid when made stays valid when archived twelve hours later, and
    one that was stale when made cannot be rescued by a later capture.

    (`now` is accepted as the old spelling of the same argument. It is the decision time, not wall clock.)

    Returns a DecisionQuote in exactly one of four states, and only FRESH is actionable:

        FRESH        confirmed within `max_age_minutes` BEFORE the decision, carrying an ask on our side
        NO_QUOTE     confirmed and current, but there is no usable ask on our side
        STALE        the newest pre-decision confirmation is older than the window
        UNCONFIRMED  no capture run at or before the decision confirms this ticker

    Nothing here consults the shadow ledger, so the model's forecast and its snapshot lineage are untouched
    by definition, not by discipline.
    """
    as_of = as_of or now
    if as_of is None:
        raise ValueError(
            "resolve_decision_quote requires the DECISION timestamp. There is no wall-clock default: "
            "defaulting to now() is exactly the bug this argument exists to prevent, because the importer "
            "runs hours after the decision it is archiving.")
    side = (side or "YES").upper()
    q = DecisionQuote(ticker=ticker, side=side, state=UNCONFIRMED, max_age_minutes=max_age_minutes,
                      series_ticker=series_ticker)
    q.as_of = as_of.isoformat()

    confirmed_at, basis, run_id, reason = index.confirmation(ticker, series_ticker, as_of)
    if confirmed_at is None:
        q.reason = reason
        return q

    q.confirmed_at = confirmed_at.isoformat()
    q.confirmation_basis = basis
    q.capture_run_id = run_id
    q.age_minutes = round((as_of - confirmed_at).total_seconds() / 60.0, 2)

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
        q.reason = (f"newest confirmation for {ticker} at or before the decision is {q.age_minutes:.1f} min "
                    f"older than it, beyond the {max_age_minutes:.0f} min decision-time freshness window")
        return q

    if q.executable_price is None:
        q.state = NO_QUOTE
        q.reason = (f"{ticker} is current but carries no {side} ask; there is no price to pay, and a "
                    "midpoint is not a substitute for one")
        return q

    q.state = FRESH
    return q


def resolve_from_root(md_root: str, ticker: str, side: str, *, series_ticker: str | None = None,
                      as_of: datetime | None = None, now: datetime | None = None,
                      max_age_minutes: float = DEFAULT_MAX_QUOTE_AGE_MIN,
                      max_runs: int = 200) -> DecisionQuote:
    """Convenience wrapper that builds a one-shot index. Prefer reusing a CaptureIndex across a batch."""
    return resolve_decision_quote(CaptureIndex(md_root, max_runs=max_runs), ticker, side,
                                  series_ticker=series_ticker, as_of=as_of or now,
                                  max_age_minutes=max_age_minutes)
