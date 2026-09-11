"""SPORTS_TRUTH and EXCHANGE_TRUTH are separate objects. Never grade money from the physical result alone.

SportsTruth  -- what happened on court (winner, score, retirement/walkover/default, sets & games
                completed, actual start/finish when known, source + confidence).
ExchangeTruth -- what Kalshi did to the contract (terminal result yes/no/scalar, settlement value in
                dollars, settlement timestamp, expiration_value string), verbatim from the API.

Verified on 2026-09-11 discovery data: 1,836 of ~61k finalized live-tier tennis markets settled as
result="scalar" with settlement_value_dollars strictly between 0 and 1 (walkovers / cancellations /
incomplete scopes resolved to a "fair price" by the exchange). Those contracts had NO binary sporting
outcome from the exchange's point of view, so model scoring on sports truth and P/L on exchange truth
must be kept apart.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime

OUTCOME_TYPES = ("COMPLETED", "RETIRED", "WALKOVER", "DEFAULT", "UNFINISHED", "UNKNOWN")


@dataclass(frozen=True)
class SportsTruth:
    match_id: str
    winner_id: str | None
    loser_id: str | None
    outcome_type: str                    # one of OUTCOME_TYPES
    score_raw: str = ""
    sets_w: int | None = None
    sets_l: int | None = None
    games_w: int | None = None
    games_l: int | None = None
    retiring_player_id: str | None = None
    actual_first_ball_at: datetime | None = None
    actual_finish_at: datetime | None = None
    source: str = ""                     # e.g. "sackmann", "kalshi_expiration_value", "manual"
    confidence: float = 0.0              # 0..1; scoring requires >= 0.9

    def __post_init__(self):
        if self.outcome_type not in OUTCOME_TYPES:
            raise ValueError(f"bad outcome_type {self.outcome_type}")

    @property
    def gradeable_binary(self) -> bool:
        """Can a match-winner prediction be scored on this truth? Walkovers/unfinished: no."""
        return self.outcome_type in ("COMPLETED", "RETIRED", "DEFAULT") and self.winner_id is not None and self.confidence >= 0.9

    def to_dict(self):
        d = asdict(self)
        for k in ("actual_first_ball_at", "actual_finish_at"):
            if d[k] is not None:
                d[k] = d[k].isoformat()
        return d


@dataclass(frozen=True)
class ExchangeTruth:
    ticker: str
    status: str                          # Kalshi status (finalized/settled/...)
    result: str                          # "yes" | "no" | "scalar" | ""
    settlement_value_dollars: float | None
    settlement_ts: datetime | None
    expiration_value: str = ""
    source_run_id: str = ""

    @property
    def terminal(self) -> bool:
        return self.result in ("yes", "no", "scalar") and self.settlement_value_dollars is not None

    @property
    def binary(self) -> bool:
        return self.result in ("yes", "no")

    @property
    def payout_yes(self) -> float | None:
        """Dollars paid per YES contract at settlement (1, 0, or the scalar fair price)."""
        return self.settlement_value_dollars if self.terminal else None

    @classmethod
    def from_market(cls, m: dict, run_id: str = "") -> "ExchangeTruth":
        sv = m.get("settlement_value_dollars")
        st = m.get("settlement_ts")
        return cls(m["ticker"], m.get("status", ""), m.get("result", "") or "", float(sv) if sv not in (None, "") else None,
                   datetime.fromisoformat(st.replace("Z", "+00:00")) if st else None, m.get("expiration_value", "") or "", run_id)

    def to_dict(self):
        d = asdict(self)
        if d["settlement_ts"] is not None:
            d["settlement_ts"] = d["settlement_ts"].isoformat()
        return d


def reconcile(sports: SportsTruth, exchange: ExchangeTruth, market_subject_is_winner_side: bool | None) -> dict:
    """Cross-check the two truths for a MATCH_WINNER contract.

    Returns {'consistent': bool, 'reason': str}. Inconsistency is a health-gate failure (TENNIS-8/9),
    never auto-resolved: e.g. sports truth says A won by retirement but the exchange settled scalar
    (pre-first-ball walkover) -- that means our start/retirement classification is wrong or the
    exchange applied a rule we do not model, and a human must look.
    """
    if not exchange.terminal:
        return {"consistent": True, "reason": "exchange not terminal yet"}
    if exchange.result == "scalar":
        ok = sports.outcome_type in ("WALKOVER", "UNFINISHED", "UNKNOWN")
        return {"consistent": ok, "reason": "scalar settlement implies no ball played / incomplete scope" if not ok else "scalar vs walkover: consistent"}
    if market_subject_is_winner_side is None:
        return {"consistent": False, "reason": "cannot map market subject to sports winner"}
    expect_yes = market_subject_is_winner_side
    got_yes = exchange.result == "yes"
    return {"consistent": expect_yes == got_yes, "reason": "" if expect_yes == got_yes else "exchange result contradicts sports winner"}
