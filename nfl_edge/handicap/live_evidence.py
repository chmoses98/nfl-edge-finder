"""CANDIDATE-SPECIFIC live market evidence: two public GETs per ticker, stamped, hashed and replayable.

THE PROBLEM THIS FIXES
----------------------
To learn whether ONE contract can be bought right now, the pre-trade worker used to check out the entire
`market-data` branch and query the capture stream. On 2026-09-13 that checkout fetched for ~57 seconds and
then wrote ~17,491 files for another ~43 seconds; the worker itself did not start until ~101 seconds into
the run, and the verdict landed at 17:01:30Z for a 17:00:00Z kickoff.

The capture stream is the right evidence for the ARCHIVAL replay -- it is immutable, point-in-time and
already committed. It is the wrong evidence for a live pre-trade decision, for two independent reasons:

  * LATENCY. It costs a hundred seconds to read a hundred bytes.
  * FRESHNESS. A bulk conductor pass begins by polling the series universe and then walks thousands of order
    books before it publishes. Run `20260913T164331Z` started at 16:43:31Z and published at 16:56:45Z, so
    even a perfectly healthy capture hands preflight a quote that is already thirteen minutes into its
    fifteen-minute window. The freshness gate was right to block; the architecture gave it nothing to pass.

So the live path stops asking the capture stream what the market was and asks the venue what it IS, for the
one ticker in front of it:

    GET /markets/{ticker}                       one request
    GET /markets/{ticker}/orderbook?depth=10    one request

Nothing here scans the Kalshi universe, and nothing here touches the capture stream's semantics: this module
neither reads nor writes `data/kalshi/capture`, and the conductor's immutable history is unchanged.

WHY THE EVIDENCE IS SHAPED LIKE A CAPTURE ROW
---------------------------------------------
The gates must not learn a second way to read a market. `quotes.resolve_decision_quote` and
`depth.resolve_full_position` already know how to read one capture-shaped quote row and one capture-shaped
book row, and those two functions are the ones the importer replays. So the evidence document EMBEDS exactly
those two rows, and `EvidenceQuoteIndex` / `EvidenceBookIndex` present them through the same tiny interface
`CaptureIndex` / `BookIndex` present. The gate code is untouched, and the archival replay runs the same
resolver over the same bytes.

The raw API bodies are kept alongside them, unmodified, so the derived rows can be re-derived and checked.

WHAT IS DELIBERATELY NOT DONE
-----------------------------
  * No midpoint is ever produced. `executable_price` stays the ask on our side, decided downstream by the
    same resolver as always.
  * No depth is approximated. The order book is the venue's, at the depth we asked for, or there is none.
  * No transient failure passes. A failed GET raises `EvidenceError`, the row is answered PREFLIGHT_ERROR,
    and an unanswered request is not an approval.
  * Nothing here consults a model, a probability or a handicap. Preflight refreshes MARKET STATE.

PUBLIC DATA ONLY
----------------
Both endpoints are unauthenticated public GETs. No account, no credentials, no positions, no fills, no
order surface. That is what makes it safe to commit this evidence to a public branch forever.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

from nfl_edge.execution import quotes as Q
from nfl_edge.kalshi import client as KC

SCHEMA = "preflight-evidence/1"

# Depth 10 is what `scripts/kalshi/capture.py` requests, so the live book and the archived book are the same
# object observed at different moments rather than two different objects.
DEFAULT_BOOK_DEPTH = 10

# Kalshi market states in which a contract can actually be bought. Mirrors the list `quotes` already applies
# to a captured row, so a live refusal and an archived refusal read identically.
TRADABLE_STATUSES = ("active", "open", "initialized")

# The two endpoints, named once. Anything that is not one of these is not part of live preflight evidence.
ENDPOINT_MARKET = "markets/{ticker}"
ENDPOINT_ORDERBOOK = "markets/{ticker}/orderbook"

_SAFE_SEGMENT = re.compile(r"[^A-Za-z0-9._-]")


class EvidenceError(RuntimeError):
    """Candidate-specific evidence could not be established. Never a verdict -- a refusal to reach one."""


# ---- small helpers ---------------------------------------------------------------------------------

def canonical_json(doc: dict) -> str:
    """The exact bytes an evidence document is hashed and stored as.

    Sorted keys and compact separators, so the hash is a function of the document's VALUES and not of how
    any particular `json.dumps` was configured on the machine that wrote it. The file on the evidence branch
    holds these bytes and nothing else, so `sha256(file)` is the document's own hash with no re-serialisation
    step in between for anyone to get wrong.
    """
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def document_sha256(doc: dict) -> str:
    return sha256_text(canonical_json(doc))


def _iso(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _dollars(market: dict, name: str):
    """A price in DOLLARS from a Kalshi market object.

    The API reports `*_dollars` as decimal strings and the bare `yes_bid` / `no_ask` fields in CENTS. Reading
    the bare field as a probability would price a 56c contract at 56 dollars, so the dollar field is
    preferred and the cent field is only ever divided by a hundred -- never used as-is.
    """
    raw = market.get(f"{name}_dollars")
    if raw is not None:
        try:
            return float(raw)
        except (TypeError, ValueError):
            pass
    cents = market.get(name)
    if cents is None:
        return None
    try:
        return round(float(cents) / 100.0, 6)
    except (TypeError, ValueError):
        return None


def _series_of(ticker: str | None) -> str | None:
    if not ticker:
        return None
    return str(ticker).split("-")[0] or None


def _safe(segment: str) -> str:
    """A path segment that cannot escape the evidence tree, whatever a ticker or a record id contains."""
    cleaned = _SAFE_SEGMENT.sub("_", str(segment or "")).strip("._")
    if not cleaned:
        raise EvidenceError("cannot build an evidence path from an empty identifier")
    return cleaned[:120]


def evidence_relpath(*, season, week, airtable_record_id: str, ticker: str, retrieved_at) -> str:
    """`data/preflight_evidence/<season>/week_<WW>/<record id>/<timestamp>_<ticker>.json`.

    Immutable by construction: the leaf carries the retrieval instant AND the ticker, so two candidates in
    one request and two requests for one candidate all land on different paths and nothing is ever rewritten.
    """
    t = _iso(retrieved_at)
    if t is None:
        raise EvidenceError(f"cannot build an evidence path from retrieval timestamp {retrieved_at!r}")
    try:
        wk = f"week_{int(week):02d}"
    except (TypeError, ValueError):
        wk = f"week_{_safe(week)}"
    try:
        yr = str(int(season))
    except (TypeError, ValueError):
        yr = _safe(season)
    stamp = t.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return "/".join(("data", "preflight_evidence", yr, wk, _safe(airtable_record_id),
                     f"{stamp}_{_safe(ticker)}.json"))


# ---- collection ------------------------------------------------------------------------------------

def collect(client, ticker: str, *, side: str = "YES", depth: int = DEFAULT_BOOK_DEPTH,
            airtable_record_id: str = "", run_id: str = "", workflow_run_id: str = "",
            evidence_run_id: str = "", kickoff_utc=None) -> dict:
    """Fetch ONE candidate's live market and order book and return the evidence document.

    Order matters and is not an accident: the market object first, because it is what says the contract is
    tradable at all, then the book. Each carries the retrieval timestamp the CLIENT stamped when the response
    actually arrived -- not the moment this function was entered, and not the moment the batch started.

    Raises `EvidenceError` on any API failure, including a partial one. A transient failure is never an empty
    book and never a missing quote: both of those would read downstream as evidence about the market, and
    what actually happened is that we did not look.
    """
    if not ticker:
        raise EvidenceError("a preflight candidate carries no market_ticker, so no evidence can be fetched")

    try:
        market_body = client.market(ticker)
    except KC.KalshiError as e:
        raise EvidenceError(
            f"the live market fetch for {ticker} failed ({e}). A pre-trade approval rests on a quote we "
            "actually retrieved; an unreachable venue is not a fresh quote.") from None
    market = (market_body or {}).get("market")
    if not isinstance(market, dict) or not market:
        raise EvidenceError(
            f"the live market fetch for {ticker} returned no market object, so there is no quote to approve "
            "against")
    market_meta = (market_body or {}).get("_meta") or {}
    market_at = _iso(market_meta.get("retrieved_at"))
    if market_at is None:
        raise EvidenceError(
            f"the live market response for {ticker} carries no retrieval timestamp; evidence whose age "
            "cannot be established is not evidence")

    try:
        book_body = client.orderbook(ticker, depth=depth)
    except KC.KalshiError as e:
        raise EvidenceError(
            f"the live order book fetch for {ticker} failed ({e}). Top-of-book is not evidence that a "
            "position fills, so a missing book blocks rather than degrades.") from None
    book_meta = (book_body or {}).get("_meta") or {}
    book_at = _iso(book_meta.get("retrieved_at"))
    if book_at is None:
        raise EvidenceError(
            f"the live order book response for {ticker} carries no retrieval timestamp; an undated book "
            "cannot be shown to have been current")
    orderbook = (book_body or {}).get("orderbook_fp")
    if not isinstance(orderbook, dict) or not orderbook:
        raise EvidenceError(
            f"the live order book for {ticker} came back empty at depth {depth}; the depth behind the top of "
            "book is not observable, and top-of-book is not a substitute for it")

    status = str(market.get("status") or "").lower()
    series = _series_of(ticker)
    raw_market = {k: v for k, v in market.items()}
    raw_book = {k: v for k, v in orderbook.items()}

    # The two capture-shaped rows the existing resolvers read. Deliberately NOT the raw market object: the
    # raw object also carries `yes_bid` in CENTS, and `quotes._side_prices` prefers the bare name, so
    # flattening it would price a 56c contract at 56.
    quote_row = {
        "run_id": evidence_run_id or "",
        "observed_at": market_at.isoformat(),
        "ticker": ticker,
        "series_ticker": series,
        "status": market.get("status"),
        "yes_bid_dollars": _dollars(market, "yes_bid"),
        "yes_ask_dollars": _dollars(market, "yes_ask"),
        "no_bid_dollars": _dollars(market, "no_bid"),
        "no_ask_dollars": _dollars(market, "no_ask"),
        "last_price_dollars": _dollars(market, "last_price"),
        "volume_fp": market.get("volume_fp"),
        "open_interest_fp": market.get("open_interest_fp"),
        "liquidity_dollars": market.get("liquidity_dollars"),
        "close_time": market.get("close_time"),
        "source": "live_preflight",
    }
    book_row = {
        "run_id": evidence_run_id or "",
        "observed_at": book_at.isoformat(),
        "ticker": ticker,
        "orderbook_fp": raw_book,
        "error": None,
        "source": "live_preflight",
    }

    doc = {
        "schema": SCHEMA,
        "evidence_run_id": evidence_run_id or "",
        "market_ticker": ticker,
        "series_ticker": series,
        "side_requested": (side or "YES").upper(),
        "kickoff_utc": (_iso(kickoff_utc).isoformat() if _iso(kickoff_utc) else None),
        "request": {
            "airtable_record_id": airtable_record_id or "",
            "run_id": run_id or "",
            "workflow_run_id": str(workflow_run_id or ""),
        },
        "source": {
            "api_base": getattr(client, "base_url", KC.BASE_URL),
            "market_url": market_meta.get("url"),
            "orderbook_url": book_meta.get("url"),
            "access": "public read-only GET; no account, no credentials, no positions, no fills",
        },
        "market": {
            "retrieved_at": market_at.isoformat(),
            "latency_ms": market_meta.get("latency_ms"),
            "status": market.get("status"),
            "tradable": status in TRADABLE_STATUSES,
            "yes_bid": quote_row["yes_bid_dollars"],
            "yes_ask": quote_row["yes_ask_dollars"],
            "no_bid": quote_row["no_bid_dollars"],
            "no_ask": quote_row["no_ask_dollars"],
            "raw_sha256": sha256_text(canonical_json(raw_market)),
            "raw": raw_market,
        },
        "orderbook": {
            "retrieved_at": book_at.isoformat(),
            "latency_ms": book_meta.get("latency_ms"),
            "depth_requested": depth,
            "levels_yes": len((raw_book.get("yes_dollars") or [])),
            "levels_no": len((raw_book.get("no_dollars") or [])),
            "raw_sha256": sha256_text(canonical_json(raw_book)),
            "raw": raw_book,
        },
        "quote_row": quote_row,
        "book_row": book_row,
    }
    return doc


def tradable_refusal(doc: dict) -> str | None:
    """Why this contract is not buyable at all, if it is not. `None` means the venue says it is open.

    Kept separate from the gates: a market that is settled, closed or paused is not a pricing problem, and
    the gate report should say which one it was rather than reporting an absent ask.
    """
    status = str(((doc or {}).get("market") or {}).get("status") or "").lower()
    if not status:
        return f"{doc.get('market_ticker')} came back with no status, so it cannot be shown to be tradable"
    if status not in TRADABLE_STATUSES:
        return (f"{doc.get('market_ticker')} is {status!r} at retrieval, which is not a tradable state; "
                "there is nothing to buy and nothing to approve")
    return None


# ---- the index adapters the gates already know how to read -----------------------------------------

class EvidenceQuoteIndex:
    """`CaptureIndex`'s interface, backed by candidate-specific live evidence rather than the capture stream.

    Two methods is the whole contract `quotes.resolve_decision_quote` uses, which is why the gates do not
    change. The confirmation is TICKER-level and EXACT: we asked the venue about this one contract and it
    answered, at a timestamp the client stamped when the response arrived. There is no series-completeness
    fallback here and there must not be -- a series-level inference is a thing you need when you are reading
    somebody else's bulk poll, and this evidence is not that.
    """

    def __init__(self, documents):
        self._by_ticker = {}
        for doc in documents or []:
            t = (doc or {}).get("market_ticker")
            if t:
                self._by_ticker[t] = doc

    def document(self, ticker):
        return self._by_ticker.get(ticker)

    def confirmation(self, ticker, series_ticker=None, as_of=None):
        doc = self._by_ticker.get(ticker)
        if doc is None:
            return None, None, None, (
                f"no live preflight evidence was collected for {ticker}, so nothing confirms this contract "
                "was open; a candidate with no evidence is not approved on the strength of the others")
        at = _iso(((doc.get("market") or {}).get("retrieved_at")))
        if at is None:
            return None, None, None, f"the preflight evidence for {ticker} carries no retrieval timestamp"
        if as_of is not None and at > as_of:
            # Evidence after the decision instant is invisible here for the same reason it is invisible in
            # the capture stream: it is information the decision did not have.
            return None, None, None, (
                f"the preflight evidence for {ticker} was retrieved at {at.isoformat()}, after the approval "
                f"instant {as_of.isoformat()}")
        return at, Q.CONFIRM_LIVE, doc.get("evidence_run_id") or None, None

    def last_quote_row(self, ticker, not_after=None):
        doc = self._by_ticker.get(ticker)
        if doc is None:
            return None
        row = doc.get("quote_row")
        if not isinstance(row, dict):
            return None
        at = _iso(row.get("observed_at"))
        if not_after is not None and at is not None and at > not_after:
            return None
        return row


class EvidenceBookIndex:
    """`BookIndex`'s interface over the same documents. One method, one book, no scan."""

    def __init__(self, documents):
        self._by_ticker = {}
        for doc in documents or []:
            t = (doc or {}).get("market_ticker")
            if t:
                self._by_ticker[t] = doc

    def latest_book(self, ticker, as_of):
        doc = self._by_ticker.get(ticker)
        if doc is None:
            return None
        row = doc.get("book_row")
        if not isinstance(row, dict) or not row.get("orderbook_fp"):
            return None
        at = _iso(row.get("observed_at"))
        if at is None or (as_of is not None and at > as_of):
            return None
        return row


def load_document(text: str, *, expected_sha256: str | None = None) -> dict:
    """Read a persisted evidence document back, and prove it is the one that was approved against.

    The hash is over the FILE'S OWN BYTES, so a single changed digit anywhere in the document -- a price, a
    timestamp, a book level -- produces a different digest and this raises. That is what makes the replay an
    independent check rather than a restatement of whatever is on the branch today.
    """
    actual = sha256_text(text)
    if expected_sha256 is not None and actual != expected_sha256:
        raise EvidenceError(
            f"preflight evidence does not match the approval: expected sha256 {expected_sha256}, the stored "
            f"bytes hash to {actual}. The evidence an approval was issued against is immutable; a document "
            "that no longer hashes to what the approval recorded has been altered since.")
    try:
        doc = json.loads(text)
    except (ValueError, TypeError) as e:
        raise EvidenceError(f"preflight evidence is not valid JSON: {e}") from None
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise EvidenceError(
            f"preflight evidence declares schema {(doc or {}).get('schema')!r}; this reader replays "
            f"{SCHEMA!r} only")
    return doc


def manifest(entries) -> dict:
    """The batch's evidence, in the canonical shape the approval signature covers.

    Sorted by path so the manifest is a function of WHAT was collected and not of the order a dict happened
    to iterate in, and carrying the storage reference so the commit the evidence landed in is authenticated
    alongside the documents themselves.
    """
    rows = sorted(({"path": e["path"], "sha256": e["sha256"]} for e in entries or []),
                  key=lambda r: (r["path"], r["sha256"]))
    return {"schema": SCHEMA, "entries": rows}


def manifest_sha256(entries, *, storage: str, commit: str | None) -> str:
    body = dict(manifest(entries), storage=storage, commit=commit or "")
    return sha256_text(canonical_json(body))
