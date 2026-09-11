"""EXCHANGE CROSS-CHECK: did the exchange settle this contract the way we read it?

Every v2 settlement is derived from football evidence -- nflverse finals, play-by-play quarter scores, player
stat tables, the postseason bracket. That is deliberate: it keeps settlement independent of the venue and makes
a wrong reading of a contract visible instead of self-confirming. But independence cuts both ways. If our
reading of a novel contract's semantics is wrong, football evidence will settle it confidently and wrongly, and
nothing in the system would ever notice.

So the exchange's own resolution is read back and compared. The comparison is a CHECK, never a source:

    the derived football result is never replaced by the exchange value.  A settlement that failed on football
    evidence stays failed; the exchange saying "yes" does not rescue an unresolvable player identity or an
    ambiguous question. Substituting it would quietly convert a semantics failure into a settled row, which is
    the exact failure mode this exists to catch.

    a disagreement is a HARD research-quality warning.  It means one of two things, both serious: we read the
    contract wrong, or the exchange settled against the football facts. Either way every projection priced
    against that reading is suspect, and the disagreement is recorded per ticker so the whole family can be
    pulled from analysis.

    old records are never rewritten.  The cross-check is a new append-only row keyed by ticker and batch, not
    an edit of a projection or of a settlement.

Exchange evidence is read from what the pipeline already captures, in this order, and costs no API calls:

    discovery   data/kalshi/discovery/<run>/markets/<SERIES>.json -> the `settled` bucket. The daily discovery
                fetches status=open,unopened,closed,settled, so terminal results arrive here by themselves.
    backfill    data/kalshi/backfill/markets/<SERIES>.jsonl -> historical finalized markets.
    snapshots   the pinned per-game settlement snapshots the incumbent settler writes.

Only TERMINAL statuses count (`finalized` / `settled`); `determined` is excluded because a determined result can
still be disputed and amended (nfl_edge/settlement/kalshi_settlement.py). A non-terminal exchange record is
reported as such, never as a disagreement.

Version: crosscheck-1.0.0.
"""
from __future__ import annotations

import glob
import json
import os

from nfl_edge.settlement import kalshi_settlement as KS

CROSSCHECK_VERSION = "crosscheck-1.0.0"

AGREE = "AGREE"
DISAGREE = "DISAGREE"                        # hard research-quality warning
EXCHANGE_MISSING = "EXCHANGE_MISSING"        # no terminal exchange record captured yet
EXCHANGE_NON_TERMINAL = "EXCHANGE_NON_TERMINAL"
DERIVED_MISSING = "DERIVED_MISSING"          # our own settlement refused; nothing to compare
NOT_COMPARABLE = "NOT_COMPARABLE"            # e.g. a tie-split payout against a binary exchange result
PAYOUT_TOLERANCE = 1e-6

SRC_DISCOVERY = "kalshi_discovery_settled_bucket"
SRC_BACKFILL = "kalshi_backfill_markets"
SRC_SNAPSHOT = "kalshi_settlement_snapshot"


def _terminal(rec: dict | None) -> tuple[bool, str | None]:
    if not rec:
        return False, "no exchange record"
    return KS.is_terminal(rec)


class ExchangeResults:
    """Terminal exchange settlements read off what the pipeline already has on disk. No network."""

    def __init__(self, market_data: str | None = None, *, roots=None):
        self.by_ticker: dict = {}
        self.sources_scanned: list = []
        if market_data:
            self._scan_discovery(os.path.join(market_data, "data", "kalshi", "discovery"))
            self._scan_backfill(os.path.join(market_data, "data", "kalshi", "backfill", "markets"))
        for r in (roots or ()):
            self._scan_snapshots(r)

    def _add(self, market: dict, source: str):
        rec = KS.settlement_record(market, source=source)
        if not rec:
            return
        ok, _ = KS.is_terminal(rec)
        prev = self.by_ticker.get(rec["ticker"])
        # a terminal record always beats a non-terminal one; otherwise first writer wins (discovery is newest)
        if prev is None or (ok and not KS.is_terminal(prev)[0]):
            self.by_ticker[rec["ticker"]] = rec

    def _scan_discovery(self, root: str):
        runs = sorted(glob.glob(os.path.join(root, "*")))
        for run in reversed(runs):                                # newest run first
            files = sorted(glob.glob(os.path.join(run, "markets", "*.json")))
            if not files:
                continue
            self.sources_scanned.append({"source": SRC_DISCOVERY, "run": os.path.basename(run), "files": len(files)})
            for f in files:
                try:
                    blob = json.load(open(f))
                except (OSError, ValueError):
                    continue
                for state in ("settled", "closed"):
                    for m in ((blob.get(state) or {}).get("markets") or []):
                        self._add(m, SRC_DISCOVERY)

    def _scan_backfill(self, root: str):
        files = sorted(glob.glob(os.path.join(root, "*.jsonl")))
        if files:
            self.sources_scanned.append({"source": SRC_BACKFILL, "files": len(files)})
        for f in files:
            try:
                for line in open(f):
                    self._add(json.loads(line), SRC_BACKFILL)
            except (OSError, ValueError):
                continue

    def _scan_snapshots(self, root: str):
        files = sorted(glob.glob(os.path.join(root, "**", "*settlement*.json"), recursive=True))
        if files:
            self.sources_scanned.append({"source": SRC_SNAPSHOT, "files": len(files)})
        for f in files:
            try:
                blob = json.load(open(f))
            except (OSError, ValueError):
                continue
            for m in (blob.get("markets") or blob.get("records") or []):
                self._add(m, SRC_SNAPSHOT)

    def get(self, ticker: str) -> dict | None:
        return self.by_ticker.get(ticker)

    def summary(self) -> dict:
        terminal = sum(1 for r in self.by_ticker.values() if KS.is_terminal(r)[0])
        return {"tickers": len(self.by_ticker), "terminal": terminal, "non_terminal": len(self.by_ticker) - terminal,
                "sources": self.sources_scanned}


def crosscheck_one(ticker: str, derived_settled_yes, derived_status: str, exchange: dict | None, *,
                   derived_kind: str | None = None, market_family: str | None = None,
                   derived_reason: str | None = None) -> dict:
    """One comparison row. Records both answers and their provenance whatever the verdict."""
    row = {"crosscheck_version": CROSSCHECK_VERSION, "ticker": ticker, "market_family": market_family,
           "derived_settled_yes": derived_settled_yes, "derived_status": derived_status, "derived_kind": derived_kind,
           "derived_reason": derived_reason,
           "exchange_result": (exchange or {}).get("result"), "exchange_status": (exchange or {}).get("status"),
           "exchange_settlement_ts": (exchange or {}).get("settlement_ts"),
           "exchange_settlement_value": (exchange or {}).get("settlement_value_dollars"),
           "exchange_expiration_value": (exchange or {}).get("expiration_value"),
           "exchange_source": (exchange or {}).get("source"), "exchange_payout": None,
           "agreement": None, "reason": None, "hard_warning": False}
    ok, why = _terminal(exchange)
    if exchange is None:
        row.update(agreement=EXCHANGE_MISSING, reason="no exchange settlement captured for this ticker")
        return row
    if not ok:
        row.update(agreement=EXCHANGE_NON_TERMINAL, reason=why or f"exchange status {exchange.get('status')!r} is not terminal")
        return row
    payout, pay_why = KS.exact_yes_payout(exchange)
    row["exchange_payout"] = payout
    if derived_settled_yes is None:
        row.update(agreement=DERIVED_MISSING, reason=derived_reason or "no derived football settlement to compare")
        return row
    if payout is None:
        row.update(agreement=NOT_COMPARABLE, reason=pay_why or "exchange record carries no usable payout")
        return row
    if derived_kind == "tie_split" and abs(payout - 0.5) > PAYOUT_TOLERANCE and payout in (0.0, 1.0):
        row.update(agreement=NOT_COMPARABLE, reason="derived payout is a tie split; the exchange resolved binary")
        return row
    if abs(float(derived_settled_yes) - float(payout)) <= PAYOUT_TOLERANCE:
        row.update(agreement=AGREE, reason=f"both resolve to {payout:g}")
        return row
    row.update(agreement=DISAGREE, hard_warning=True,
               reason=f"RESEARCH-QUALITY WARNING: football evidence settles {derived_settled_yes:g}, the exchange settled "
                      f"{payout:g} ({exchange.get('result')!r}). Either the contract was read wrong or the exchange settled "
                      f"against the football facts; every projection priced on this reading is suspect.")
    return row


def crosscheck_rows(settlement_rows, results: ExchangeResults) -> list:
    """One cross-check per settled/refused row. Never mutates the settlement rows it is given."""
    out = []
    for r in settlement_rows:
        t = r.get("ticker")
        if not t:
            continue
        out.append(crosscheck_one(t, r.get("settled_yes"), r.get("settlement_status") or "UNKNOWN", results.get(t),
                                  derived_kind=r.get("settlement_kind"), market_family=r.get("market_family"),
                                  derived_reason=r.get("settlement_reason")))
    return out


def summarize(rows) -> dict:
    """Coverage and, above all, the disagreements -- by family, because a misread contract is a family problem."""
    by_agreement, by_family, disagreements = {}, {}, []
    for r in rows:
        a = r.get("agreement") or "UNKNOWN"
        by_agreement[a] = by_agreement.get(a, 0) + 1
        fam = r.get("market_family") or "UNKNOWN"
        d = by_family.setdefault(fam, {"n": 0, AGREE: 0, DISAGREE: 0, EXCHANGE_MISSING: 0})
        d["n"] += 1
        d[a] = d.get(a, 0) + 1
        if r.get("hard_warning"):
            disagreements.append({k: r.get(k) for k in ("ticker", "market_family", "derived_settled_yes", "exchange_payout",
                                                        "exchange_result", "exchange_settlement_ts", "exchange_source", "reason")})
    comparable = by_agreement.get(AGREE, 0) + by_agreement.get(DISAGREE, 0)
    return {"crosscheck_version": CROSSCHECK_VERSION, "n": len(rows), "by_agreement": by_agreement,
            "comparable": comparable, "agreement_rate": (by_agreement.get(AGREE, 0) / comparable) if comparable else None,
            "n_disagreements": len(disagreements), "disagreements": disagreements[:200],
            "families_with_disagreement": sorted({d["market_family"] for d in disagreements if d.get("market_family")}),
            "by_family": by_family}
