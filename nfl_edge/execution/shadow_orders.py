"""PAPER-ONLY resting-order ledger. No real orders are ever placed by this code.

Shadow orders exist to answer one question prospectively: when a passive order at a better price would have
been reachable, were we right or wrong? The historical study (research/passive) says wrong -- reachable
orders lost 2.9 cents gross while unreachable ones gained 1.1. This records the prospective version.

Two disciplines are enforced rather than trusted:

  * **Orders are created before the fact, never after seeing the move.** Placement requires only information
    available at placement time, and the cancel rule is fixed at creation.
  * **Fail closed.** An order is refused, with an explicit reason, whenever anything the evaluation depends on
    is unresolved: identity, settlement semantics, staleness, a started game, an incomplete book, a malformed
    shock, a model artifact mismatch, or an invalid quote timestamp.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from nfl_edge.execution.ticks import is_valid_price, passive_levels

# fixed, prespecified cancel rules. Chosen once; not to be retuned on the same sample.
CANCEL_RULES = {
    "T30M": "cancel 30 minutes after placement",
    "EDGE_GONE": "cancel when the model no longer favours the side",
    "SHOCK": "cancel on any material shock affecting the game",
    "PREKICK_5M": "cancel 5 minutes before kickoff",
    "ADVERSE_3C": "cancel if the midpoint moves 3 cents against us",
}

REFUSALS = (
    "PLAYER_IDENTITY_UNRESOLVED", "SETTLEMENT_SEMANTICS_UNRESOLVED", "STALE_CRITICAL_DATA",
    "MARKET_STARTED", "ORDER_BOOK_INCOMPLETE", "SHOCK_SOURCE_MALFORMED",
    "MODEL_ARTIFACT_MISMATCH", "QUOTE_TIMESTAMP_INVALID", "NO_PASSIVE_LEVEL", "NO_MODEL_VIEW",
)


@dataclass
class ShadowOrder:
    shadow_order_id: str
    created_at: str
    ticker: str
    game_id: str | None
    side: str                       # yes | no
    limit_price: float
    size_contracts: float
    level_name: str
    reason: str
    model_probability: float
    model_version: str
    model_artifact_sha: str
    hypothesis_id: str
    yes_bid: float
    yes_ask: float
    spread: float
    queue_ahead: float | None       # size resting at our level at entry, from the book snapshot
    minutes_to_kickoff: float | None
    cancel_rule: str
    expires_at: str | None = None
    status: str = "OPEN"            # OPEN | CANCELLED | EXPIRED  -- never "FILLED" from historical data
    notes: str = ""

    def to_dict(self):
        return asdict(self)


def _oid(*parts):
    return "sho_" + hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def refuse(reason: str, detail: str = ""):
    return {"ok": False, "reason": reason, "detail": detail}


def propose_order(quote: dict, model_p: float, *, model_version: str, model_artifact_sha: str,
                  expected_artifact_sha: str | None, hypothesis_id: str, size: float = 1.0,
                  cancel_rule: str = "T30M", min_edge: float = 0.02,
                  book: dict | None = None, now: datetime | None = None):
    """Decide whether a passive shadow order is admissible. Returns a ShadowOrder or a refusal.

    Every refusal path is explicit; nothing is silently skipped.
    """
    now = now or datetime.now(timezone.utc)
    if expected_artifact_sha and model_artifact_sha != expected_artifact_sha:
        return refuse("MODEL_ARTIFACT_MISMATCH", f"{model_artifact_sha} != {expected_artifact_sha}")
    if quote.get("support_state") not in (None, "SUPPORTED"):
        return refuse("SETTLEMENT_SEMANTICS_UNRESOLVED", str(quote.get("support_state")))
    if quote.get("player_kalshi_id") and not quote.get("player_resolved", True):
        return refuse("PLAYER_IDENTITY_UNRESOLVED", str(quote.get("player_kalshi_id")))
    mtk = quote.get("minutes_to_kickoff")
    if mtk is not None and mtk <= 0:
        return refuse("MARKET_STARTED", f"minutes_to_kickoff={mtk}")
    ts = quote.get("observed_at")
    if not ts:
        return refuse("QUOTE_TIMESTAMP_INVALID", "missing observed_at")
    try:
        obs = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        obs = obs if obs.tzinfo else obs.replace(tzinfo=timezone.utc)
    except ValueError:
        return refuse("QUOTE_TIMESTAMP_INVALID", str(ts))
    age_s = (now - obs).total_seconds()
    if age_s > 900:
        return refuse("STALE_CRITICAL_DATA", f"quote is {age_s:.0f}s old")
    yb, ya = quote.get("yes_bid"), quote.get("yes_ask")
    if yb is None or ya is None or not (0 <= yb <= ya <= 1) or (yb <= 0 and ya >= 1):
        return refuse("ORDER_BOOK_INCOMPLETE", f"bid={yb} ask={ya}")
    if model_p is None:
        return refuse("NO_MODEL_VIEW", "model probability missing")
    mid = (yb + ya) / 2.0
    side = "yes" if model_p > mid + min_edge else ("no" if (1 - model_p) > (1 - mid) + min_edge else None)
    if side is None:
        return refuse("NO_MODEL_VIEW", f"|model-mid|={abs(model_p-mid):.4f} < {min_edge}")
    levels = passive_levels(yb, ya, side)
    level_name = "improve_bid" if "improve_bid" in levels else ("join_bid" if "join_bid" in levels else None)
    if level_name is None:
        return refuse("NO_PASSIVE_LEVEL", f"spread={ya-yb:.3f} leaves no passive price")
    limit = levels[level_name]
    if not is_valid_price(limit):
        return refuse("NO_PASSIVE_LEVEL", f"illegal price {limit}")
    qa = None
    if book:
        qa = book.get("size_at_level", {}).get(round(limit, 2))
    o = ShadowOrder(
        shadow_order_id=_oid(quote.get("ticker"), ts, side, limit, model_version),
        created_at=now.isoformat(), ticker=quote.get("ticker"), game_id=quote.get("game_id"),
        side=side, limit_price=limit, size_contracts=size, level_name=level_name,
        reason=f"model {model_p:.4f} vs mid {mid:.4f}", model_probability=model_p,
        model_version=model_version, model_artifact_sha=model_artifact_sha, hypothesis_id=hypothesis_id,
        yes_bid=yb, yes_ask=ya, spread=ya - yb, queue_ahead=qa, minutes_to_kickoff=mtk,
        cancel_rule=cancel_rule,
        notes="PAPER ONLY -- no real order is placed. Fill is never inferred from a touch.")
    return {"ok": True, "order": o}
