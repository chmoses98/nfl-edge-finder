"""Immutable per-contract reconciliation of the owner's fills.

One frozen record per ledger fill, joining only evidence that is ON RECORD:

  recommendation id/time and model snapshot   -> ``handicap.attribution.link_fill`` (exact ticker+side, before fill and
                                                 kickoff; never inferred; absence is NO_RECOMMENDATION_ON_RECORD)
  injuries / confirmed QB / projection as-of   -> caller-supplied availability evidence, else MISSING_* flags
  fills + fees                                 -> the ledger row (price, contracts, fees_paid, fee_state); the row carries no
                                                 exchange order id or fill ids, which is reported as MISSING_ORDER_FILL_DETAIL
  ontology                                     -> ``ontology.classify_ticker`` (combos decoded only from supplied legs)
  settlement + amendments                      -> canonical net = latest amendment chain, ORIGINAL net preserved beside it
  close quote and CLV                          -> caller-supplied close; CLV is close mid of the side held minus the price paid

Nothing is written anywhere; ``record_sha256`` is the digest of the record's canonical JSON so a later run can prove
the evidence it reconciled has not moved. Public-repo rule: ``redact()`` strips tickers, dollars and keys.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from nfl_edge.handicap import attribution as ATTR

from .common import num, parse_ts
from .ontology import COMBO_UNDECODED, SINGLE, classify_ticker

RECONCILE_VERSION = "postmortem-reconcile-1.0.0"


@dataclass(frozen=True)
class ContractRecord:
    source_bet_key: str
    ticker: str
    side: str
    kind: str
    family: str | None
    period: str | None
    game_key: str | None
    executed_at: str | None
    price: float | None
    contracts: float | None
    stake: float | None
    fees_paid: float | None
    fee_state: str | None
    recommendation: dict
    availability: dict
    settlement: dict
    close: dict
    clv: dict
    flags: tuple = field(default_factory=tuple)
    #: Router execution evidence (digests + first/last fill time) when a sidecar row exists for this wager; {} otherwise.
    execution: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in self.__dataclass_fields__}
        d["flags"] = list(self.flags)
        if not d["execution"]:
            del d["execution"]          # absent evidence leaves the record (and its sha256) exactly as it was before this field existed
        return d

    @property
    def record_sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True, default=str).encode()).hexdigest()


#: Every spelling of "the exchange told us which order / fills this was" the router or a destination ledger uses. Any one present
#: clears MISSING_ORDER_FILL_DETAIL; none present keeps the flag (the ids are never inferred).
ORDER_FILL_KEYS = ("order_id", "kalshi_order_id", "fill_ids", "kalshi_fill_ids", "fill_id")

#: What a "close" is. A TRUE close is the exchange's own final pregame price (e.g. the last candlestick before the market closed
#: or kickoff). Everything this pipeline has today is a periodic CAPTURE of the order book taken before kickoff: a PROXY, however
#: recent. A proxy is never reported as a true close and a CLV computed from one is labelled as such.
TRUE_CLOSE = "TRUE_CLOSE"
CAPTURE_PROXY = "CAPTURE_PROXY"
TRUE_CLOSE_SOURCES = frozenset({"EXCHANGE_CLOSE_CANDLE"})


def close_kind(close: dict | None) -> str | None:
    if not close:
        return None
    return TRUE_CLOSE if close.get("source") in TRUE_CLOSE_SOURCES else CAPTURE_PROXY

#: Sidecar fields from the router's execution evidence (kalshi_router.execution_evidence, schema router_execution_evidence.v1). Digests only:
#: this repository is public, so raw order/fill ids never appear here, and a digest cannot be inverted.
EXECUTION_EVIDENCE_FIELDS = ("order_id_digest", "fill_id_digests", "fill_count", "first_fill_ts", "last_fill_ts", "execution_action", "all_taker")
EXECUTION_EVIDENCE_SCHEMA = "router_execution_evidence.v1"


def canonical_settlement(settlement: dict | None, amendments: list) -> dict:
    """Latest amendment wins for the canonical figure; the as-filed figure is always kept beside it."""
    if not settlement:
        return {"state": "UNSETTLED", "result": None, "net_canonical": None, "net_as_filed": None, "amended": False, "flags": ["MISSING_SETTLEMENT"]}
    filed = num(settlement.get("net_profit_loss"))
    canon, amended, flags = filed, False, []
    mine = [a for a in amendments if a.get("source_bet_key") == settlement.get("source_bet_key")]
    for a in sorted(mine, key=lambda a: str(a.get("amendment_id"))):
        c = num(((a.get("superseded_fields") or {}).get("net_profit_loss") or {}).get("corrected"))
        if c is not None:
            canon, amended = c, True
    if canon is None:
        flags.append("NET_UNESTABLISHED")
    return {"state": settlement.get("settlement_status"), "result": settlement.get("result"), "net_canonical": canon,
            "net_as_filed": filed, "amended": amended, "economics_version": settlement.get("economics_version"),
            "gross_return": num(settlement.get("gross_return")), "flags": flags}


def _clv(side: str, price, contracts, fee, close: dict | None) -> dict:
    if not close:
        return {"state": "MISSING_CLOSE", "clv": None, "clv_net_of_fee": None}
    if side == "YES":
        bid, ask = num(close.get("yes_bid")), num(close.get("yes_ask"))
    else:
        bid, ask = num(close.get("no_bid")), num(close.get("no_ask"))
    if bid is None or ask is None or price is None:
        return {"state": "CLOSE_ONE_SIDED_OR_PRICE_MISSING", "clv": None, "clv_net_of_fee": None}
    mid = (bid + ask) / 2.0
    clv = mid - price
    net = None if fee is None or not contracts else clv - fee / contracts
    return {"state": "OK", "close_mid_side": mid, "clv": clv, "clv_net_of_fee": net, "close_kind": close_kind(close),
            "close_quality": close.get("quality") or close.get("close_quality"), "close_captured_at": close.get("captured_at"),
            "close_age_seconds": close.get("close_age_seconds")}


def reconcile(wagers: list, settlements: list, amendments: list, *, recommendations: list | None = None,
              closes: dict | None = None, availability: dict | None = None, kickoffs: dict | None = None,
              legs_by_ticker: dict | None = None, execution_evidence: dict | None = None) -> list:
    """``availability``: {game_key: {projection_as_of, injuries_as_of, qb:{TEAM:{status,confirmed_at}}}}.
    ``kickoffs``: {game_key: iso}. ``execution_evidence``: {source_bet_key: router sidecar row} (optional; absence changes nothing).
    Returns ContractRecord list in ledger order."""
    recs = ATTR.real_recommendations(recommendations or [])
    settle_by_key = {s.get("source_bet_key"): s for s in settlements}
    closes, availability, kickoffs, legs_by_ticker = closes or {}, availability or {}, kickoffs or {}, legs_by_ticker or {}
    out = []
    for w in wagers:
        if w.get("test_only"):
            continue
        t, side = w.get("market_ticker"), w.get("side")
        ont = classify_ticker(t, legs=legs_by_ticker.get(t))
        flags = list(ont.flags)
        execution = {}
        ee = (execution_evidence or {}).get(w.get("source_bet_key"))
        if isinstance(ee, dict) and ee.get("schema_version") == EXECUTION_EVIDENCE_SCHEMA and ee.get("source_bet_key") == w.get("source_bet_key"):
            execution = {k: ee.get(k) for k in EXECUTION_EVIDENCE_FIELDS if k in ee}
            execution["evidence_flags"] = list(ee.get("flags") or [])
        has_ids = any(w.get(k) for k in ORDER_FILL_KEYS) or bool(execution.get("order_id_digest") and execution.get("fill_id_digests"))
        if not has_ids:
            flags.append("MISSING_ORDER_FILL_DETAIL")
        fee, price, contracts = num(w.get("fees_paid")), num(w.get("actual_price")), num(w.get("contracts"))
        if w.get("fees_are_estimated"):
            flags.append("FEES_ESTIMATED")
        if fee is None:
            flags.append("MISSING_FEES")
        link = ATTR.link_fill(w, recs)
        rec = {"state": link.get("state"), "reason": link.get("reason"), "recommendation_id": link.get("recommendation_id"),
               "model_version": None, "created_at": None, "model_as_of": None}
        if rec["state"] != ATTR.LINKED:
            flags.append("MISSING_RECOMMENDATION")
        else:
            src = next((r for r in recs if r.get("recommendation_id") == rec["recommendation_id"]), {})
            rec.update(model_version=src.get("model_version"), created_at=src.get("created_at"), model_as_of=src.get("market_timestamp"))
        av = {"state": "MISSING_AVAILABILITY_EVIDENCE"}
        if ont.kind == SINGLE and ont.game_key in availability:
            a = availability[ont.game_key]
            av = {"state": "PRESENT", "projection_as_of": a.get("projection_as_of"), "injuries_as_of": a.get("injuries_as_of"), "qb": a.get("qb")}
            for k in ("projection_as_of", "injuries_as_of", "qb"):
                if not a.get(k):
                    flags.append(f"MISSING_{k.upper()}")
        else:
            flags.append("MISSING_AVAILABILITY_EVIDENCE" if ont.kind == SINGLE else
                         "AVAILABILITY_NOT_APPLICABLE_TO_COMBO" if ont.kind.startswith("COMBO") else "AVAILABILITY_UNASSESSED_UNCLASSIFIED")
        ko = kickoffs.get(ont.game_key) if ont.game_key else None
        exe = parse_ts(w.get("executed_at"))
        pre = None
        if ko and exe:
            pre = exe < parse_ts(ko)
        elif ont.kind == SINGLE:
            flags.append("MISSING_KICKOFF")
        if pre is False:
            flags.append("EXECUTED_AFTER_KICKOFF")
        st = canonical_settlement(settle_by_key.get(w.get("source_bet_key")), amendments)
        flags += st["flags"]
        close = closes.get(t)
        clv = _clv(side, price, contracts, fee, close) if ont.kind == SINGLE else {"state": "NOT_APPLICABLE_COMBO", "clv": None, "clv_net_of_fee": None}
        if ont.kind == SINGLE and clv["state"] != "OK":
            flags.append("MISSING_CLOSE")
        if ont.kind == COMBO_UNDECODED:
            flags.append("COMBO_REPORTED_SEPARATELY")
        out.append(ContractRecord(
            source_bet_key=w.get("source_bet_key"), ticker=t, side=side, kind=ont.kind, family=ont.family, period=ont.period,
            game_key=ont.game_key, executed_at=w.get("executed_at"), price=price, contracts=contracts, stake=num(w.get("stake")),
            fees_paid=fee, fee_state=w.get("fee_state"), recommendation=rec, availability=av, settlement=st,
            close={"present": bool(close), "pregame_execution": pre, "kind": close_kind(close)}, clv=clv, flags=tuple(sorted(set(flags))),
            execution=execution))
    return out


def redact(records: list) -> dict:
    """Counts and flags only; safe for a public repository (no ticker, key, stake, price or P&L)."""
    from collections import Counter
    flag_counts = Counter(f for r in records for f in r.flags)
    return {"version": RECONCILE_VERSION, "n_records": len(records),
            "kinds": dict(Counter(r.kind for r in records)),
            "settled": sum(1 for r in records if r.settlement.get("net_canonical") is not None),
            "amended": sum(1 for r in records if r.settlement.get("amended")),
            "recommendation_states": dict(Counter(r.recommendation["state"] for r in records)),
            "flag_counts": dict(sorted(flag_counts.items()))}
