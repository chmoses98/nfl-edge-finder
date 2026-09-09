"""The exchange's OWN settlement of a market: the only place an exact scalar payout can come from.

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

WHERE THE EXACT VALUE LIVES, AND WHERE IT DOES NOT
--------------------------------------------------
`settlement_value_dollars` on a finalized market, alongside `result` (`yes` / `no` / `scalar`). Two sources
already exist in this project:

  * the historical archive on `market-data` (`data/kalshi/backfill/markets/<SERIES>.jsonl`), written by
    `scripts/kalshi/backfill.py` from `GET /historical/markets`. It covers seasons behind Kalshi's historical
    cutoff -- the whole 2025 season, and nothing recent;
  * a settlement SNAPSHOT captured at settle time from the public `GET /markets` surface, persisted next to the
    evaluation batch it justifies.

It is NOT in the 10-minutely capture. The capture fetches `status=open` only, so a market that has settled has
left the set it looks at: 1,211,807 captured NFL quote rows carry `status="active"` and not one carries a
settlement. That is why this module exists instead of reading the capture.

PINNED EVIDENCE
---------------
An evaluation row is immutable, so the evidence behind it must not change between runs. The snapshot is
therefore written ONCE per game and every later run reads that file instead of re-fetching. A run that could not
reach the exchange still writes a snapshot -- an empty one, recording the failure -- so the absence of an exact
payout is pinned too, and a rerun reproduces the same refusal rather than contradicting it.
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime, timezone

SNAPSHOT_SUFFIX = "kalshi_settlement_snapshot.json"

SOURCE_SNAPSHOT = "kalshi_settlement_snapshot"
SOURCE_ARCHIVE = "kalshi_historical_archive"

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
    """One raw Kalshi market -> the settlement evidence, or None when it carries no settlement at all."""
    if not market or not market.get("ticker"):
        return None
    res = (market.get("result") or "").strip().lower()
    if not res:
        return None
    rec = {k: market.get(k) for k in SETTLEMENT_FIELDS if market.get(k) is not None}
    rec["ticker"] = market["ticker"]
    rec["result"] = res
    rec["source"] = source
    return rec


def exact_yes_payout(rec: dict | None) -> tuple[float | None, str | None]:
    """Exact payout of one YES contract, in dollars, and the branch it came from.

    `yes`/`no` are exact by definition. `scalar` is exact only if the exchange published the value; when it did
    not, this returns `(None, "scalar")` -- the caller must refuse, never substitute. Nothing here looks at a
    bid, an ask, a midpoint, a last trade or a model.
    """
    if not rec:
        return None, None
    res = (rec.get("result") or "").strip().lower()
    if res == "yes":
        return 1.0, "binary"
    if res == "no":
        return 0.0, "binary"
    if res == "scalar":
        v = _f(rec.get("settlement_value_dollars"))
        if v is None or not (0.0 <= v <= 1.0):
            return None, "scalar"
        return v, "scalar"
    return None, res or None


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

    def scalar_payout(self, ticker: str) -> tuple[float | None, str | None]:
        """The exact payout ONLY for a market the exchange settled scalar; (None, reason) otherwise."""
        rec = self.by_ticker.get(ticker)
        if rec is None:
            return None, "no exchange settlement record for this ticker"
        payout, branch = exact_yes_payout(rec)
        if branch != "scalar":
            return None, f"the exchange settled this market {rec.get('result')!r}, not scalar"
        if payout is None:
            return None, ("the exchange settled this market scalar but published no "
                          "settlement_value_dollars in the evidence available")
        return payout, None

    def load_snapshot(self, path_or_obj) -> int:
        obj = path_or_obj
        if isinstance(path_or_obj, str):
            with open(path_or_obj) as f:
                obj = json.load(f)
            self.sources.append({"source": SOURCE_SNAPSHOT, "path": path_or_obj,
                                 "captured_at": obj.get("captured_at"), "markets": len(obj.get("markets") or {})})
        n = 0
        for rec in (obj.get("markets") or {}).values():
            self.add({**rec, "source": rec.get("source") or SOURCE_SNAPSHOT})
            n += 1
        return n

    def load_archive(self, archive_dir: str, tickers) -> int:
        """The historical tier's settled markets for the tickers we care about."""
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


def find_snapshot(corpus_roots, game_id: str) -> str | None:
    """The pinned snapshot for a game, if any run has already captured one."""
    for root in ([corpus_roots] if isinstance(corpus_roots, str) else corpus_roots):
        hits = sorted(glob.glob(os.path.join(root, game_id, f"*.{SNAPSHOT_SUFFIX}")))
        if hits:
            return hits[0]                # earliest batch: the first capture is the pinned evidence
    return None


def build_snapshot(game_id: str, markets, *, fetch_meta=None, source: str = SOURCE_SNAPSHOT,
                   captured_at: str | None = None) -> dict:
    recs = {}
    for m in markets or []:
        rec = settlement_record(m, source=source)
        if rec:
            recs[rec["ticker"]] = rec
    return {"game_id": game_id, "captured_at": captured_at or datetime.now(timezone.utc).isoformat(),
            "markets": recs, "n_markets": len(recs), "fetch_meta": list(fetch_meta or []),
            "note": ("The exchange's own settlement of every market for this game, captured once and never "
                     "re-fetched: it is the pinned evidence behind immutable evaluation rows. An empty "
                     "`markets` map records that no settlement could be read, which is itself pinned.")}


def fetch_game_settlements(client, event_tickers, tickers=None, *, verbose=None) -> tuple[list, list]:
    """Best-effort read of the exchange's settlements for one game, via the public read-only client.

    Per EVENT first (one request per event covers every rung), falling back to per-ticker for anything still
    missing. Never raises: a failure returns what it has plus provenance describing what went wrong, because a
    settlement run must be able to proceed on the branches that do not need this.
    """
    found, meta = {}, []
    for ev in sorted(set(event_tickers or ())):
        try:
            items, complete, info = client.markets(event_ticker=ev, limit=1000, max_pages=5)
            for m in items or []:
                if m.get("ticker"):
                    found[m["ticker"]] = m
            meta.append({"event_ticker": ev, "markets": len(items or []), "complete": complete,
                         "info": str(info)[:300] if info else None})
        except Exception as e:                                  # noqa: BLE001 - evidence gathering never raises
            meta.append({"event_ticker": ev, "error": f"{type(e).__name__}: {str(e)[:200]}"})
        if verbose:
            verbose(f"  exchange settlements {ev}: {meta[-1].get('markets', meta[-1].get('error'))}")
    missing = [t for t in (tickers or ()) if t not in found]
    for t in missing:
        try:
            body = client.market(t)
            m = (body or {}).get("market") or body
            if m and m.get("ticker"):
                found[m["ticker"]] = m
        except Exception as e:                                  # noqa: BLE001
            meta.append({"ticker": t, "error": f"{type(e).__name__}: {str(e)[:200]}"})
    return list(found.values()), meta
