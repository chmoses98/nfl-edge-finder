"""The exchange's own TERMINAL settlement: the only place an exact scalar payout can come from.

WHY THIS EXISTS
---------------
Most Kalshi NFL contracts pay $1 or $0 and nflverse proves which (see `settle.py`). One branch does not: a
player who is ACTIVE but never takes a snap settles at "the last fair market price before game start", a scalar
value the exchange computes and publishes. Nothing in nflverse knows that number, and nothing about a quote
implies it:

    a pregame midpoint is a PRICING-TIME PROXY for that branch, which is what
    `semantics.player_prop_contract_value` uses it for. It is not the payout.

Recording a midpoint as `settled_yes` would put a number we invented into an immutable corpus and then score
our own model against it. So the exact value is either read from the exchange or the row is refused.

TERMINALITY: A RESULT IS NOT A SETTLEMENT
----------------------------------------
A Kalshi market acquires a `result` before its settlement is final. The lifecycle runs roughly

    active -> closed -> determined -> settled / finalized

and a **determined** market's result can still be disputed and amended. An immutable evaluation may therefore
only be built from a market that has reached a TERMINAL state, where positions have been paid and the number
cannot change. `result` alone is not evidence of that, so nothing here trusts it on its own.

The terminal statuses are named in `TERMINAL_STATUSES` and nowhere else, so tightening the rule is a one-line
change. Two strings are accepted because two surfaces spell the same terminal state differently: the historical
archive normalises to `finalized` (measured: all 48,845 archived NFL market records carry exactly that, asserted
by `tests/test_kalshi_settlement.py`), while Kalshi's live market status enum reaches the same state as
`settled`. Everything else -- `determined`, `disputed`, `amended`, `closed`, `active`, `open`, `unopened` -- is
explicitly NOT terminal, and each record's own terminal status is recorded so the first live run tells us
empirically which spelling the live surface uses.

WHERE THE EXACT VALUE LIVES, AND WHERE IT DOES NOT
--------------------------------------------------
`settlement_value_dollars` on a terminal market, alongside `result` (`yes` / `no` / `scalar`). Two sources
already exist in this project:

  * the historical archive on `market-data` (`data/kalshi/backfill/markets/<SERIES>.jsonl`), written by
    `scripts/kalshi/backfill.py` from `GET /historical/markets`. It covers seasons behind Kalshi's historical
    cutoff -- the whole 2025 season, and nothing recent;
  * a settlement SNAPSHOT captured at settle time from the public `GET /markets?status=settled` surface, and
    persisted next to the evaluation batch it justifies.

It is NOT in the 10-minutely capture. The capture fetches `status=open` only, so a market that has settled has
left the set it looks at: 1,211,807 captured NFL quote rows carry `status="active"` and not one carries a
settlement.

PINNED EVIDENCE IS FROZEN ON PURPOSE, AND ONLY WHEN IT IS TERMINAL
------------------------------------------------------------------
An evaluation row is immutable, so the evidence behind it must not change between runs: a snapshot is written
once and every later run reads it instead of re-fetching.

That freezing is only legitimate for terminal evidence. A failed request, a partial page, or a market that has
not settled yet are RETRYABLE ACQUISITION STATES -- they mean "we could not read it this time", not "there is no
settlement". Pinning them would turn a transient outage into a permanent hole in the corpus, so a snapshot is
never written from them: the caller defers and the schedule tries again. `build_snapshot` refuses to describe
itself as covering a ticker it holds no terminal record for.
"""
from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

SNAPSHOT_SUFFIX = "kalshi_settlement_snapshot.json"

SOURCE_SNAPSHOT = "kalshi_settlement_snapshot"
SOURCE_ARCHIVE = "kalshi_historical_archive"

# The ONLY statuses that make a record terminal. See the module docstring: `finalized` is what the historical
# archive writes, `settled` is what Kalshi's live status enum calls the same state. `determined` is deliberately
# absent -- a determined result can still be disputed and amended.
TERMINAL_STATUSES = ("finalized", "settled")
# Named so a rejection can say WHY, and so the list of things that look final but are not is auditable.
NON_TERMINAL_STATUSES = ("determined", "disputed", "amended", "closed", "active", "open", "unopened",
                         "initialized", "pending")

# The live status filter. Asking for every status would hand us determined and disputed markets to sift; asking
# the exchange for the terminal set is both cheaper and harder to get wrong.
LIVE_SETTLED_STATUS = "settled"

# Fields copied from a raw Kalshi market record. Deliberately narrow: this is settlement evidence, not a
# market snapshot, and a wide copy would tempt someone to price from it later.
SETTLEMENT_FIELDS = ("ticker", "result", "settlement_value_dollars", "settlement_ts", "status",
                     "expiration_value", "event_ticker")


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def settlement_record(market: dict, *, source: str) -> dict | None:
    """One raw Kalshi market -> the settlement evidence, or None when it carries no result at all.

    A record is kept even when it is not terminal: the caller needs to be able to say "this market exists and is
    still determined" rather than "this market is missing", because those are different waits.
    """
    if not market or not market.get("ticker"):
        return None
    res = (market.get("result") or "").strip().lower()
    if not res:
        return None
    rec = {k: market.get(k) for k in SETTLEMENT_FIELDS if market.get(k) is not None}
    rec["ticker"] = market["ticker"]
    rec["result"] = res
    rec["status"] = (market.get("status") or "").strip().lower() or None
    rec["source"] = source
    return rec


def is_terminal(rec: dict | None) -> tuple[bool, str | None]:
    """Has this market reached a state where its settlement can no longer change? Returns (terminal, reason)."""
    if not rec:
        return False, "no exchange settlement record"
    status = (rec.get("status") or "").strip().lower()
    if not status:
        return False, "the exchange record carries no status, so terminality cannot be established"
    if status in TERMINAL_STATUSES:
        return True, None
    if status in NON_TERMINAL_STATUSES:
        return False, (f"the exchange market is {status!r}, which is not terminal: its result can still change "
                       "and an immutable evaluation may not be built from it")
    return False, f"the exchange market status {status!r} is not a known terminal state"


def exact_yes_payout(rec: dict | None) -> tuple[float | None, str | None]:
    """Exact payout of one YES contract, in dollars, and the branch it came from.

    Returns a payout ONLY for a terminal record. `yes`/`no` are exact by the rules once terminal; `scalar` is
    exact only if the exchange published a value inside [0, 1]. A non-terminal record yields `(None, branch)`
    however complete it looks. Nothing here looks at a bid, an ask, a midpoint, a last trade or a model.
    """
    if not rec:
        return None, None
    res = (rec.get("result") or "").strip().lower()
    branch = "binary" if res in ("yes", "no") else (res or None)
    terminal, _why = is_terminal(rec)
    if not terminal:
        return None, branch
    if res == "yes":
        return 1.0, "binary"
    if res == "no":
        return 0.0, "binary"
    if res == "scalar":
        v = _f(rec.get("settlement_value_dollars"))
        if v is None or not (0.0 <= v <= 1.0):
            return None, "scalar"
        return v, "scalar"
    return None, branch


@dataclass
class ScalarLookup:
    """The outcome of asking for one ticker's exact scalar payout.

    `retryable` is the field that matters: it separates "the exchange has not finished with this market, or we
    could not read it" (wait, and try again) from "the exchange finished and published no value" (a terminal
    evidence deficiency, which is refused permanently). Conflating the two is how a transient outage becomes a
    permanent hole in an immutable corpus.
    """
    payout: float | None = None
    reason: str | None = None
    retryable: bool = False
    record: dict | None = None

    @property
    def source(self):
        return (self.record or {}).get("source")


class ExactSettlementBook:
    """Ticker -> the exchange's own settlement, assembled from pinned evidence only."""

    def __init__(self):
        self.by_ticker: dict[str, dict] = {}
        self.sources: list = []

    def add(self, rec: dict | None):
        if not rec:
            return
        # first writer wins: sources are added in priority order, and a pinned snapshot outranks a later read
        self.by_ticker.setdefault(rec["ticker"], rec)

    def get(self, ticker: str):
        return self.by_ticker.get(ticker)

    def payout(self, ticker: str) -> tuple[float | None, str | None]:
        return exact_yes_payout(self.by_ticker.get(ticker))

    def terminal_tickers(self) -> set:
        return {t for t, rec in self.by_ticker.items() if is_terminal(rec)[0]}

    def scalar_payout(self, ticker: str) -> ScalarLookup:
        """The exact payout for a market the exchange TERMINALLY settled scalar, or why not, and whether waiting
        could change the answer."""
        rec = self.by_ticker.get(ticker)
        if rec is None:
            return ScalarLookup(reason="no exchange settlement record for this ticker", retryable=True)
        terminal, why = is_terminal(rec)
        if not terminal:
            return ScalarLookup(reason=why, retryable=True, record=rec)
        res = (rec.get("result") or "").strip().lower()
        if res != "scalar":
            # terminal and not scalar: waiting cannot turn it into one
            return ScalarLookup(reason=f"the exchange settled this market {res!r}, not scalar", record=rec)
        v = _f(rec.get("settlement_value_dollars"))
        if v is None or not (0.0 <= v <= 1.0):
            return ScalarLookup(
                reason=("the exchange terminally settled this market scalar and published no usable "
                        "settlement_value_dollars, so no exact payout exists to record"),
                retryable=False, record=rec)
        return ScalarLookup(payout=v, record=rec)

    def load_snapshot(self, path_or_obj) -> int:
        obj = path_or_obj
        if isinstance(path_or_obj, str):
            with open(path_or_obj) as f:
                obj = json.load(f)
            self.sources.append({"source": SOURCE_SNAPSHOT, "path": os.path.basename(path_or_obj),
                                 "captured_at": obj.get("captured_at"), "markets": len(obj.get("markets") or {})})
        n = 0
        for rec in (obj.get("markets") or {}).values():
            self.add({**rec, "source": rec.get("source") or SOURCE_SNAPSHOT})
            n += 1
        return n

    def load_archive(self, archive_dir: str, tickers) -> int:
        """The historical tier's settled markets for the tickers we care about.

        The archive is written from `GET /historical/markets`, which Kalshi populates only for markets settled
        before its historical cutoff. That guarantee is stated rather than assumed: every record still has to
        pass `is_terminal`, and a test asserts the archive on `market-data` satisfies it for all 48,845 NFL
        records it holds.
        """
        want = set(tickers or ())
        n = 0
        for path in sorted(glob.glob(os.path.join(archive_dir, "*.jsonl"))):
            for line in open(path):
                if want and not any(t in line for t in _needles(want)):
                    continue
                m = json.loads(line)
                if want and m.get("ticker") not in want:
                    continue
                rec = settlement_record(m, source=SOURCE_ARCHIVE)
                if rec:
                    self.add(rec)
                    n += 1
        if n:
            self.sources.append({"source": SOURCE_ARCHIVE, "path": archive_dir, "markets": n})
        return n


def _needles(tickers):
    """Cheap line prefilter: the shared event prefix of the wanted tickers, so a whole series file is skipped
    without parsing every line of it."""
    return {t.rsplit("-", 1)[0] for t in tickers} or set()


def find_snapshots(corpus_roots, game_id: str) -> list:
    """Every snapshot any run has pinned for this game, oldest batch first.

    A list rather than one file: a later run may legitimately need terminal evidence for a ticker no earlier
    snapshot covers (new predictions, a market that settled later), and it pins that as an ADDITIONAL write-once
    file. Earlier records still win, so nothing already relied upon can change.
    """
    out = []
    for root in ([corpus_roots] if isinstance(corpus_roots, str) else corpus_roots):
        out.extend(sorted(glob.glob(os.path.join(root, game_id, f"*.{SNAPSHOT_SUFFIX}"))))
    return out


def build_snapshot(game_id: str, markets, *, required_tickers=None, fetch_meta=None,
                   source: str = SOURCE_SNAPSHOT, captured_at: str | None = None) -> dict:
    """Freeze the TERMINAL exchange records from a read. Non-terminal records are counted, never frozen.

    `required_tickers` are the tickers whose immutable evaluation depends on this evidence -- the scalar-branch
    ones. The snapshot records whether it actually covers them, so a partial fetch cannot masquerade as complete
    merely because some markets came back.
    """
    recs, non_terminal = {}, {}
    for m in markets or []:
        rec = settlement_record(m, source=source)
        if not rec:
            continue
        terminal, why = is_terminal(rec)
        if terminal:
            recs[rec["ticker"]] = rec
        else:
            non_terminal[rec["ticker"]] = {"status": rec.get("status"), "result": rec.get("result"),
                                           "reason": why}
    required = sorted(set(required_tickers or ()))
    missing = [t for t in required if t not in recs]
    return {"game_id": game_id, "captured_at": captured_at or datetime.now(timezone.utc).isoformat(),
            "markets": recs, "n_markets": len(recs),
            "terminal_statuses_accepted": list(TERMINAL_STATUSES),
            "required_tickers": required, "covers_required": not missing,
            "required_tickers_missing": missing,
            "non_terminal_seen": non_terminal, "n_non_terminal_seen": len(non_terminal),
            "fetch_meta": list(fetch_meta or []),
            "note": ("Terminal exchange settlements for this game, frozen once and never re-fetched: pinned "
                     "evidence behind immutable evaluation rows. Only markets in a terminal state are here; a "
                     "market still determined, a partial page or a failed request is a retryable acquisition "
                     "state and is deliberately NOT frozen.")}


@dataclass
class FetchOutcome:
    """What a live read of the exchange actually achieved, separately from what it found."""
    markets: list
    meta: list
    complete: bool = False              # every event page came back, and per-ticker fallbacks all answered
    errors: int = 0

    def to_dict(self):
        return {"markets_returned": len(self.markets), "complete": self.complete, "errors": self.errors,
                "meta": self.meta}


def fetch_game_settlements(client, event_tickers, tickers=None, *, verbose=None) -> FetchOutcome:
    """Read the exchange's TERMINAL settlements for one game, via the public read-only client.

    Asks for the settled set per EVENT (one request covers every rung), then falls back to the per-ticker market
    endpoint for anything still missing -- a ticker whose event page did not include it must still pass the
    terminality check before it can be used.

    Never raises. It reports `complete` so the caller can tell a full read that found nothing from a partial read
    that simply did not see everything: only the former is safe to freeze.
    """
    found, meta, errors, complete = {}, [], 0, True
    for ev in sorted(set(event_tickers or ())):
        try:
            items, page_complete, info = client.markets(event_ticker=ev, status=LIVE_SETTLED_STATUS,
                                                        limit=1000, max_pages=5)
            for m in items or []:
                if m.get("ticker"):
                    found[m["ticker"]] = m
            if not page_complete:
                complete = False
            meta.append({"event_ticker": ev, "status_filter": LIVE_SETTLED_STATUS,
                         "markets": len(items or []), "complete": page_complete,
                         "info": str(info)[:300] if info else None})
        except Exception as e:                                  # noqa: BLE001 - evidence gathering never raises
            errors += 1
            complete = False
            meta.append({"event_ticker": ev, "error": f"{type(e).__name__}: {str(e)[:200]}"})
        if verbose:
            verbose(f"  exchange settlements {ev}: {meta[-1].get('markets', meta[-1].get('error'))}")
    for t in [t for t in (tickers or ()) if t not in found]:
        try:
            body = client.market(t)
            m = (body or {}).get("market") or body
            if m and m.get("ticker"):
                found[m["ticker"]] = m
        except Exception as e:                                  # noqa: BLE001
            errors += 1
            complete = False
            meta.append({"ticker": t, "error": f"{type(e).__name__}: {str(e)[:200]}"})
    return FetchOutcome(markets=list(found.values()), meta=meta, complete=complete and errors == 0,
                        errors=errors)
