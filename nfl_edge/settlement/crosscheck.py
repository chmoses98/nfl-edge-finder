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

Version: crosscheck-1.1.0.

EVIDENCE IS TIME-EVOLVING; THE COMPARISON RULE IS NOT
-----------------------------------------------------
A GAME's derived football settlement is immutable: its score does not change, so a settlement row written once
is written forever. Exchange evidence is not like that. A ticker is EXCHANGE_MISSING at the first postgame run
because the exchange has not resolved it yet, EXCHANGE_NON_TERMINAL while it is merely `determined`, and only
later does a terminal `settled`/`finalized` record appear. All three are truthful readings of DIFFERENT moments.

Cross-checks are published into the write-once EvaluationCorpus, whose identity is
(prediction_id, evaluation_version). Filing every reading under one flat version made the later, truthful
terminal row contradict the earlier provisional one, and the corpus -- correctly, given what it was told -- refused
the whole batch: `EvaluationConflict: 3420 evaluation(s) contradict an already-published truth`. The corpus was
not wrong; the identity was. So the lifecycle is made explicit in the version itself:

    TERMINAL     AGREE / DISAGREE / NOT_COMPARABLE / DERIVED_MISSING   crosscheck-1.1.0+terminal
                 A conclusion drawn from a terminal exchange record and a derived settlement that can no longer
                 change. ONE identity per prediction, forever. Re-running over the same terminal evidence is a
                 NO-OP; two CONTRADICTORY terminal readings still collide and still fail the run loudly, which
                 is the whole point of the corpus -- that case means the exchange amended a settled result, and
                 a human must look.

    PROVISIONAL  EXCHANGE_MISSING / EXCHANGE_NON_TERMINAL,            crosscheck-1.1.0+provisional.<vintage>
                 or a derived settlement that is itself provisional
                 An observation, not a conclusion: "as of this evidence, this was not resolved yet".
                 `<vintage>` is a digest of the evidence observed on BOTH sides, so re-running against unchanged
                 evidence is a NO-OP (no daily churn in a published corpus), while evidence that MOVED files a
                 new row beside the old one. Nothing is rewritten and nothing is deleted: the provisional history
                 of a ticker is readable in full, and the eventual terminal row joins it rather than replacing it.

WHY 1.1.0. Both halves of that rule were wrong about season-scoped settlements, and the corpus on disk records
it: 50,025 published rows are a cross-check of a season settlement that refused with a count of games not yet
played, filed under a vintage that digested only the exchange half -- so the next run, with the count changed,
contradicted them; and 1,617 more are DERIVED_MISSING on such a refusal, filed under +terminal as though the
refusal were final. Rows written under the old rule cannot be re-offered under it without reproducing those
collisions, so the version is bumped: every row filed by the 1.0.0 rule is retired where it lies, never
rewritten and never deleted, and `rank()` keeps ordering the whole history by substance.

`rank()` is how a reader picks one: terminal outranks provisional, and within a tier the later observation wins.
That makes research's choice deterministic when several vintages exist, and it never shows a provisional
"missing" row for a prediction whose terminal verdict has since been recorded.

Rows published before this lifecycle existed carry no evaluation_version at all. They are left exactly as they
are -- historical observations are never rewritten -- and `rank()` classifies them by their own `agreement`, so a
legacy terminal AGREE still outranks any provisional row.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
from datetime import datetime, timezone

from nfl_edge.settlement import kalshi_settlement as KS

CROSSCHECK_VERSION = "crosscheck-1.1.0"

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

# ---------------------------------------------------------------------------------------------- evidence tiers
TERMINAL = "TERMINAL"                        # a conclusion; one identity per prediction, forever
PROVISIONAL = "PROVISIONAL"                  # an observation of evidence that had not arrived yet
# The two agreements that say "the exchange has not spoken yet". They are not the only way a cross-check can
# still be an observation: the DERIVED side can also be waiting on evidence, which is what
# PROVISIONAL_DERIVED_STATUSES below covers.
PROVISIONAL_AGREEMENTS = (EXCHANGE_MISSING, EXCHANGE_NON_TERMINAL)

TERMINAL_VERSION = f"{CROSSCHECK_VERSION}+terminal"
PROVISIONAL_PREFIX = f"{CROSSCHECK_VERSION}+provisional."

# What a cross-check OBSERVED, as opposed to what it concluded. The vintage digest is taken over exactly these,
# so a provisional row is re-filed only when the evidence it saw actually moved.
# The derived side is included because it is NOT always immutable -- see PROVISIONAL_DERIVED_STATUSES. When
# only the exchange half was digested, a cross-check built on a season settlement that refused with "16 of 17
# games not final" kept the same vintage after the count changed to "15 of 17", so the same identity carried
# two different rows and the corpus refused the batch.
EVIDENCE_FIELDS = ("agreement", "exchange_status", "exchange_result", "exchange_settlement_ts",
                   "exchange_settlement_value", "exchange_expiration_value", "exchange_source", "reason",
                   "derived_status", "derived_reason", "derived_settled_yes", "derived_kind")
# A DERIVED settlement that is itself an observation rather than a conclusion. The module opened by saying the
# derived football settlement is immutable, and for a GAME it is -- a final score does not change, and a game
# that is not final is deferred rather than settled. Season-scoped families are the exception: they are
# examined from week 1 onward and refuse with a count of games not yet played, which falls every week. A
# cross-check of one is therefore provisional on BOTH sides, and calling it terminal filed an observation as a
# conclusion (nfl_edge/settlement/settle_v2.py).
PROVISIONAL_DERIVED_STATUSES = ("REFUSED_SEASON_INCOMPLETE",)


def evidence_tier(agreement: str | None, derived_status: str | None = None) -> str:
    """A cross-check is a conclusion only when NEITHER side is still waiting for evidence."""
    if agreement in PROVISIONAL_AGREEMENTS or derived_status in PROVISIONAL_DERIVED_STATUSES:
        return PROVISIONAL
    return TERMINAL


def row_tier(row: dict) -> str:
    """The tier of a cross-check row, from its stamp if it has one and from its substance otherwise."""
    return row.get("evidence_tier") or evidence_tier(row.get("agreement"), row.get("derived_status"))


def evidence_vintage(row: dict) -> str:
    """A digest of the exchange evidence this cross-check saw. Deterministic; no wall clock."""
    payload = json.dumps({k: row.get(k) for k in EVIDENCE_FIELDS}, sort_keys=True, default=str)
    return hashlib.sha1(payload.encode()).hexdigest()[:12]


def evaluation_version(row: dict) -> str:
    """The corpus identity this cross-check belongs under. See the module docstring."""
    if row_tier(row) == PROVISIONAL:
        return PROVISIONAL_PREFIX + evidence_vintage(row)
    return TERMINAL_VERSION


def versioned(row: dict, *, now=None) -> dict:
    """Stamp a cross-check with the evidence lifecycle it belongs to. Never mutates the row it is given.

    `evaluated_at` is when this reading was taken. The corpus excludes it from the content hash, so re-observing
    the same evidence is a no-op and the stored timestamp keeps naming the FIRST time that evidence was seen --
    which is exactly what makes it a usable ordering key for `rank()`.
    """
    tier = row_tier(row)
    now = now or datetime.now(timezone.utc)
    return {**row, "evidence_tier": tier, "evidence_vintage": evidence_vintage(row),
            "provisional": tier == PROVISIONAL, "evaluation_version": evaluation_version(row),
            "evaluated_at": now if isinstance(now, str) else now.isoformat()}


def batch_manifest(rows) -> dict:
    """What a published cross-check batch holds, by identity and by tier.

    A batch carries both tiers at once -- the terminal verdicts reached this run and the provisional observations
    of tickers the exchange has not resolved yet -- so the manifest names the split rather than letting the
    provisional half be invisible in the file it lives in.
    """
    versions, tiers = {}, {}
    for r in rows:
        v = r.get("evaluation_version")
        versions[str(v)] = versions.get(str(v), 0) + 1
        t = row_tier(r)
        tiers[t] = tiers.get(t, 0) + 1
    return {"by_evaluation_version": dict(sorted(versions.items())), "by_evidence_tier": dict(sorted(tiers.items()))}


def rank(row: dict) -> tuple:
    """Sort key for choosing ONE cross-check per prediction: terminal first, then the later observation.

    Classified by the row's own `agreement` rather than by its version string, so rows written before the
    lifecycle existed (no evaluation_version) are ranked on their substance like everything else.
    """
    tier = row_tier(row)
    return (1 if tier == TERMINAL else 0, str(row.get("evaluated_at") or ""), str(row.get("evaluation_version") or ""))


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
    """One cross-check per settlement row, carrying its prediction id. Never mutates the rows it is given.

    The id is attached HERE, from the row itself. It was previously reattached by the caller with a positional
    `zip` after this function had `continue`d past tickerless rows -- so a single skipped row shifted every
    later prediction id onto the wrong cross-check. A row without a ticker now yields a cross-check that says
    so, keeping the output the same length as the input and the join by id rather than by position.
    """
    out = []
    for r in settlement_rows:
        pid = r.get("prediction_id") or r.get("record_id")
        t = r.get("ticker")
        if not t:
            out.append({"crosscheck_version": CROSSCHECK_VERSION, "prediction_id": pid, "record_id": pid,
                        "ticker": None, "market_family": r.get("market_family"), "agreement": NOT_COMPARABLE,
                        "reason": "settlement row carries no ticker to match an exchange record against",
                        "hard_warning": False})
            continue
        row = crosscheck_one(t, r.get("settled_yes"), r.get("settlement_status") or "UNKNOWN", results.get(t),
                             derived_kind=r.get("settlement_kind"), market_family=r.get("market_family"),
                             derived_reason=r.get("settlement_reason"))
        out.append({**row, "prediction_id": pid, "record_id": pid})
    return out


class SummaryAccumulator:
    """summarize(), one cross-check row at a time. Keeps counts, the first 200 disagreements and the set of
    families they touch -- never the rows -- so the settlement driver can summarise the whole corpus while
    reading it game by game."""

    KEEP = 200

    def __init__(self):
        self.n = 0
        self.by_agreement, self.by_family, self.by_tier = {}, {}, {}
        self.disagreements, self.n_disagreements, self.families = [], 0, set()

    def add(self, r: dict):
        self.n += 1
        a = r.get("agreement") or "UNKNOWN"
        self.by_agreement[a] = self.by_agreement.get(a, 0) + 1
        # Every reading is counted under its evidence tier, provisional ones included. A ticker the exchange has
        # not resolved yet is a gap in COVERAGE, not an absence of evidence, and it must stay visible as such.
        t = row_tier(r)
        self.by_tier[t] = self.by_tier.get(t, 0) + 1
        fam = r.get("market_family") or "UNKNOWN"
        d = self.by_family.setdefault(fam, {"n": 0, AGREE: 0, DISAGREE: 0, EXCHANGE_MISSING: 0})
        d["n"] += 1
        d[a] = d.get(a, 0) + 1
        if r.get("hard_warning"):
            self.n_disagreements += 1
            if r.get("market_family"):
                self.families.add(r["market_family"])
            if len(self.disagreements) < self.KEEP:
                self.disagreements.append({k: r.get(k) for k in ("ticker", "market_family", "derived_settled_yes", "exchange_payout",
                                                                 "exchange_result", "exchange_settlement_ts", "exchange_source", "reason")})

    def finish(self) -> dict:
        comparable = self.by_agreement.get(AGREE, 0) + self.by_agreement.get(DISAGREE, 0)
        return {"crosscheck_version": CROSSCHECK_VERSION, "n": self.n, "by_agreement": self.by_agreement,
                "by_evidence_tier": dict(sorted(self.by_tier.items())),
                "provisional": self.by_tier.get(PROVISIONAL, 0), "terminal": self.by_tier.get(TERMINAL, 0),
                "comparable": comparable, "agreement_rate": (self.by_agreement.get(AGREE, 0) / comparable) if comparable else None,
                "n_disagreements": self.n_disagreements, "disagreements": self.disagreements[:self.KEEP],
                "families_with_disagreement": sorted(self.families), "by_family": self.by_family}


def summarize(rows) -> dict:
    """Coverage and, above all, the disagreements -- by family, because a misread contract is a family problem."""
    acc = SummaryAccumulator()
    for r in rows:
        acc.add(r)
    return acc.finish()
