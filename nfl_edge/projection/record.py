"""The universal projection record.

One row per (snapshot, contract, model arm). Every field the mission lists is here, and two rules govern
how they are used:

  1. `mid` is a RESEARCH quantity. It is never an executable price and nothing downstream may treat it as a
     cost to buy or sell. `yes_ask` / `no_ask` are what a buyer pays; `yes_bid` / `no_bid` are what a seller
     receives. Probability benchmarking (model vs mid) and trade economics (model vs ask, less fees) are
     separate questions and are kept in separate fields.
  2. The record is IMMUTABLE. Its identity is `record_id = sha1(snapshot_id | ticker | model_arm | engine_version
     | distribution_version)` and its `content_hash` covers every claim it makes; `generated_at` is the only
     volatile field. A rerun that reproduces the same claims is a no-op; a rerun that contradicts them is a
     CONFLICT and writes nothing (`nfl_edge/projection/store.py`).

Two evidence classes never mix: PROSPECTIVE_FROZEN rows are written before kickoff from a capture observed
before kickoff (both timestamps are on the row and are checked); HISTORICAL_RESEARCH rows are walk-forward
reconstructions used for model development and are labelled so nobody can score them as prospective.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

SCHEMA_VERSION = "projection-2.0.0"
PROSPECTIVE_FROZEN = "PROSPECTIVE_FROZEN"
HISTORICAL_RESEARCH = "HISTORICAL_RESEARCH"
VOLATILE_FIELDS = ("generated_at",)

# support states of ONE record (the board accounting maps them to terminal states)
PRICED = "PRICED"                                              # PROVEN semantics, validated/shadow engine, p_yes written
PROJECTABLE_NOT_YET_VALIDATED = "PROJECTABLE_NOT_YET_VALIDATED"  # p_yes written, LIKELY semantics or unvalidated engine: research only
CAPTURE_ONLY = "CAPTURE_ONLY"
RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
SEMANTICS_AMBIGUOUS = "SEMANTICS_AMBIGUOUS"
DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
IDENTITY_UNRESOLVED = "IDENTITY_UNRESOLVED"
UNSUPPORTED = "UNSUPPORTED"
NON_FOOTBALL_MODEL = "NON_FOOTBALL_MODEL"
JOINT_MODEL_REQUIRED = "JOINT_MODEL_REQUIRED"
POST_KICKOFF = "POST_KICKOFF"
STALE_MARKET = "STALE_MARKET"
DEGRADED_INPUT = "DEGRADED_INPUT"
SETTLEMENT_UNSUPPORTED = "SETTLEMENT_UNSUPPORTED"
SUPPORT_STATES = (PRICED, PROJECTABLE_NOT_YET_VALIDATED, CAPTURE_ONLY, RESEARCH_REQUIRED, SEMANTICS_AMBIGUOUS, DATA_UNAVAILABLE,
                  IDENTITY_UNRESOLVED, UNSUPPORTED, NON_FOOTBALL_MODEL, JOINT_MODEL_REQUIRED, POST_KICKOFF, STALE_MARKET,
                  DEGRADED_INPUT, SETTLEMENT_UNSUPPORTED)
# states that carry a probability
PROBABILITY_STATES = (PRICED, PROJECTABLE_NOT_YET_VALIDATED)


def record_id(snapshot_id: str, ticker: str, model_arm: str, engine_version: str, distribution_version: str) -> str:
    return hashlib.sha1(f"{snapshot_id}|{ticker}|{model_arm}|{engine_version}|{distribution_version}".encode()).hexdigest()[:20]


def content_hash(row: dict) -> str:
    payload = {k: v for k, v in row.items() if k not in VOLATILE_FIELDS and k != "content_hash"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:20]


@dataclass
class ProjectionRecord:
    # ---- identity
    record_id: str
    snapshot_id: str                       # the capture run this projection prices (observed market)
    ticker: str
    model_arm: str                         # e.g. GAME_MARKET_PRIOR, PERIOD_RESIDUAL_V1, DATA_PLAYER_DIST, MARKET_PLAYER_DIST, HYBRID_PLAYER_DIST
    engine: str                            # GAME | PERIOD | PLAYER | SEASON | JOINT | NONE
    engine_version: str
    distribution_version: str
    model_version: str
    schema_version: str = SCHEMA_VERSION
    evidence_class: str = PROSPECTIVE_FROZEN
    # ---- contract
    series_ticker: str | None = None
    event_ticker: str | None = None
    market_family: str | None = None
    period: str | None = None
    stat_family: str | None = None
    question: dict = field(default_factory=dict)      # the Question, verbatim
    threshold: float | None = None
    range_lo: float | None = None
    range_hi: float | None = None
    operator: str | None = None
    yes_semantics: str | None = None
    semantic_confidence: str | None = None
    settlement_rule_version: str | None = None
    # ---- football identity
    game_id: str | None = None
    season: int | None = None
    week: int | None = None
    home_team: str | None = None
    away_team: str | None = None
    subject_kind: str | None = None                   # team | player | none
    subject_id: str | None = None                     # nflverse team code or GSIS id
    subject_kalshi_id: str | None = None
    subject_name: str | None = None
    identity_confidence: str | None = None            # RESOLVED | RESOLVED_UNCONFIRMED | UNRESOLVED | NOT_APPLICABLE
    # ---- time
    observed_at: str | None = None                    # when the market was observed (capture)
    generated_at: str | None = None                   # wall clock of this projection (volatile)
    kickoff_utc: str | None = None
    minutes_to_kickoff: float | None = None
    data_cutoff: str | None = None                    # latest information the projection used
    horizon_label: str | None = None                  # T-24h | T-6h | T-90m | T-30m | CYCLE
    horizon_target_min: float | None = None
    horizon_lateness_min: float | None = None         # actual snapshot time minus the intended horizon instant (>= 0 late)
    horizon_id: str | None = None
    # ---- market at observation (never later, never earlier)
    yes_bid: float | None = None
    yes_ask: float | None = None
    no_bid: float | None = None
    no_ask: float | None = None
    mid: float | None = None                          # RESEARCH midpoint. NOT executable.
    quote_width: float | None = None
    volume: float | None = None
    open_interest: float | None = None
    liquidity: float | None = None
    market_confirmed: bool | None = None              # the series was fetched completely in this capture run
    market_quality: dict = field(default_factory=dict)
    # ---- projection
    p_yes: float | None = None                        # P(YES) of the football/event question
    contract_value: float | None = None               # E[payout] with settlement branches folded in
    p_yes_low: float | None = None                    # research uncertainty band when the arm carries one
    p_yes_high: float | None = None
    support_state: str = CAPTURE_ONLY
    support_reason: str | None = None
    data_quality: dict = field(default_factory=dict)
    projection_lineage: dict = field(default_factory=dict)
    feature_lineage: dict = field(default_factory=dict)
    distribution_summary: dict = field(default_factory=dict)
    # ---- research-only comparisons (never "edge")
    model_market_disagreement_mid: float | None = None   # contract_value - mid  (probability benchmarking)
    yes_ask_disagreement: float | None = None            # contract_value - yes_ask (economics side, pre-fee)
    no_ask_disagreement: float | None = None
    content_hash: str | None = None

    def finalize(self) -> "ProjectionRecord":
        if self.yes_bid is not None and self.yes_ask is not None:
            self.mid = (self.yes_bid + self.yes_ask) / 2.0
            self.quote_width = self.yes_ask - self.yes_bid
        if self.contract_value is not None:
            if self.mid is not None:
                self.model_market_disagreement_mid = self.contract_value - self.mid
            if self.yes_ask is not None:
                self.yes_ask_disagreement = self.contract_value - self.yes_ask
            if self.no_ask is not None:
                self.no_ask_disagreement = (1.0 - self.contract_value) - self.no_ask
        if self.p_yes is not None and not (0.0 <= self.p_yes <= 1.0):
            raise ValueError(f"p_yes {self.p_yes} outside [0, 1] on {self.ticker}")
        if self.support_state not in PROBABILITY_STATES and self.p_yes is not None:
            raise ValueError(f"support state {self.support_state} must not carry a probability ({self.ticker})")
        if self.support_state in PROBABILITY_STATES and self.p_yes is None:
            raise ValueError(f"support state {self.support_state} without a probability ({self.ticker})")
        d = asdict(self)
        self.content_hash = content_hash(d)
        return self

    def to_dict(self) -> dict:
        return asdict(self)


def prospective_check(rec: ProjectionRecord) -> tuple[bool, str | None]:
    """Both timestamps strictly before kickoff, or the record must be POST_KICKOFF with no probability."""
    from datetime import datetime
    def _dt(s):
        if not s:
            return None
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    ko, obs, gen = _dt(rec.kickoff_utc), _dt(rec.observed_at), _dt(rec.generated_at)
    if ko is None:
        return False, "no kickoff"
    if obs is None or obs >= ko:
        return False, "observed_at is not strictly before kickoff"
    if gen is None or gen >= ko:
        return False, "generated_at is not strictly before kickoff"
    return True, None
