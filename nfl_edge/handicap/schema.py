"""Immutable record schemas for the ChatGPT handicap layer.

Four record types, each append-only and each in its own file, so that a ChatGPT write is a file CREATE and
never an edit of a shared document. That is a conflict-avoidance decision as much as a scientific one: two
recommendations written minutes apart touch different paths and cannot collide.

  RECOMMENDATION  what was decided, at what observed price, on what reasoning. Never mutated.
  EXECUTION       what the user actually did. A recommendation is an opinion; an execution is a position.
                  They are separate records because they answer different questions -- was the call good,
                  and did the bankroll benefit -- and conflating them makes both unanswerable.
  EVALUATION      derived, attached later from close and settlement. Never written by the handicapper.
  POSTMORTEM      why it went the way it did, with named categories and an explicit confidence.

The immutability rule is enforced by the writer, not by convention: `write_record` refuses to overwrite an
existing path. A changed mind is a NEW record carrying `amends`, so the original opinion and the original
observed price survive. Nothing here rewrites history.

Fees: `bet_up_to_probability` is a Kalshi probability in the same units the user sees when placing the order
(0-1 as quoted, i.e. cents/100). Fees are deliberately NOT folded into it -- the user's workflow treats the
displayed price as the cost basis, and fee-aware analysis lives in nfl_edge/execution/fees.py where it can be
varied without rewriting a single historical recommendation.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

HANDICAP_SCHEMA_VERSION = "1.0.0"

# ---- decisions -------------------------------------------------------------------------------------
RECOMMENDED = "RECOMMENDED"
PASS = "PASS"
WATCHLIST = "WATCHLIST"
RESEARCH_ALERT = "RESEARCH_ALERT"
DECISIONS = (RECOMMENDED, PASS, WATCHLIST, RESEARCH_ALERT)

# Grade is the handicapper's combined confidence, NOT a formula over model edge. Objective components are
# preserved alongside it (model probability, observed price, bet_up_to) so the two can be compared later.
GRADES = ("A+", "A", "A-", "B+", "B", "B-", "C", "PASS")

SIDES = ("YES", "NO")

# ---- postmortem categories (Part IX) ----------------------------------------------------------------
POSTMORTEM_CATEGORIES = (
    "GOOD_PROCESS_VARIANCE",      # right call, wrong outcome -- the most important category to use honestly
    "MODEL_MEAN_ERROR",
    "MODEL_TAIL_ERROR",
    "ROLE_ERROR",
    "INJURY_ASSUMPTION_ERROR",
    "GAME_SCRIPT_ERROR",
    "MATCHUP_THESIS_ERROR",
    "WEATHER_ERROR",
    "MARKET_ALREADY_PRICED",
    "PRICE_TOO_EXPENSIVE",
    "EXECUTION_ERROR",
    "UNEXPECTED_IN_GAME_INJURY",
    "SMALL_SAMPLE_VARIANCE",
    "OTHER",
)

# Reasoning tags are free-form but a controlled core is offered so the scorecard can group by mechanism.
# Unknown tags are allowed (the handicapper may see something we did not anticipate) and are reported as
# "uncontrolled" in the scorecard rather than rejected.
CORE_REASONING_TAGS = (
    "ROLE_EXPANSION", "ROLE_CONTRACTION", "INJURY_REPLACEMENT", "QB_CHANGE", "OL_INJURY",
    "PACE", "GAME_SCRIPT", "MATCHUP_PASS", "MATCHUP_RUN", "MATCHUP_COVERAGE", "RED_ZONE",
    "WEATHER_WIND", "WEATHER_PRECIP", "MARKET_STALE", "MARKET_OVERREACTION", "LADDER_SHAPE",
    "TAIL_PRICING", "MODEL_DISAGREEMENT", "LIQUIDITY", "CORRELATION_HEDGE", "PRICE_VALUE",
    # Reasons a contract was declined are tags too. A PASS is a record with reasoning, and the most common
    # reasons to pass -- the price already reflects the news, the book is too thin, the news has not
    # resolved yet -- need names, or every pass lands in the uncontrolled bucket.
    "MARKET_ALREADY_PRICED", "PRICE_TOO_EXPENSIVE", "AWAIT_INACTIVE_RELEASE", "INSUFFICIENT_LIQUIDITY",
    "ROLE_UNCERTAIN", "MODEL_UNTRUSTED_HERE",
)

_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,120}$")


class ValidationError(ValueError):
    """Raised when a payload is not fit to be committed. Always names the field."""


def _uid(prefix: str, *parts) -> str:
    return prefix + "_" + hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:20]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Recommendation:
    """One considered contract. RECOMMENDED, PASS, WATCHLIST or RESEARCH_ALERT.

    A PASS is a first-class scientific record, not an absence. The comparison we eventually want -- did the
    handicapper's judgement add anything over the model's raw disagreement -- is only possible if the
    contracts that were seriously considered and declined are recorded with the same fidelity as the ones
    taken. Passes are recorded where a contract received serious consideration, not for every rung on the
    board.
    """
    recommendation_id: str
    schema_version: str
    created_at: str
    handicap_run_id: str
    packet_sha: str | None                 # ties the decision to the exact packet it was made from

    # football identity
    season: int | None
    week: int | None
    game_id: str | None
    kickoff_utc: str | None

    # market identity
    market_ticker: str
    market_family: str | None = None
    player_id: str | None = None
    player_name: str | None = None
    side: str = "YES"
    threshold: float | None = None

    # OBSERVED MARKET -- frozen at decision time, never refreshed
    yes_bid: float | None = None
    yes_ask: float | None = None
    no_bid: float | None = None
    no_ask: float | None = None
    mid: float | None = None
    width: float | None = None
    volume: float | None = None
    open_interest: float | None = None
    market_timestamp: str | None = None
    minutes_to_kickoff: float | None = None

    # MODEL -- what the quantitative layer said, for later attribution
    model_version: str | None = None
    artifact_hash: str | None = None
    model_probability: float | None = None
    model_projection: dict | None = None
    market_implied_projection: dict | None = None

    # CHATGPT HANDICAP
    probability_low: float | None = None
    probability_mid: float | None = None
    probability_high: float | None = None
    bet_up_to_probability: float | None = None      # Kalshi price units, fees NOT folded in
    grade: str | None = None
    recommended_stake: int | None = None            # whole dollars
    bankroll_snapshot: float | None = None

    decision: str = WATCHLIST

    # THESIS
    primary_thesis: str = ""
    key_supporting_factors: list = field(default_factory=list)
    counterarguments: list = field(default_factory=list)
    uncertainties: list = field(default_factory=list)
    reasoning_tags: list = field(default_factory=list)

    # DATA STATE at decision time
    injury_state: dict | None = None
    weather_state: dict | None = None
    role_state: dict | None = None
    market_movement_state: dict | None = None
    source_freshness: dict | None = None

    # correlation (Part XV)
    correlation_group: str | None = None
    correlation_direction: str | None = None
    correlation_strength: str | None = None         # qualitative when no quantitative estimate exists

    # lineage
    amends: str | None = None                       # recommendation_id this supersedes; never an in-place edit
    test_only: bool = False                         # TEST_ONLY records are excluded from every report

    def to_dict(self):
        return asdict(self)


@dataclass
class Execution:
    """What the user actually did. Deliberately separate from the recommendation."""
    execution_id: str
    schema_version: str
    recommendation_id: str
    executed_at: str
    actual_price: float
    stake: int
    side: str
    contracts: float | None = None
    fees_paid: float | None = None
    venue: str = "kalshi"
    notes: str = ""
    test_only: bool = False

    def to_dict(self):
        return asdict(self)


@dataclass
class Evaluation:
    """Derived. Attached after close/settlement. Never written by the handicapper, never mutates the rec."""
    evaluation_id: str
    schema_version: str
    recommendation_id: str
    evaluated_at: str
    close_yes_bid: float | None = None
    close_yes_ask: float | None = None
    close_mid: float | None = None
    closing_executable: float | None = None         # the price we could actually have taken at close
    clv: float | None = None                        # signed, in our direction, mid basis
    clv_executable: float | None = None
    settlement: float | None = None                 # 1.0 / 0.0 / None if unsettled
    outcome: str | None = None                      # WIN / LOSS / VOID / UNSETTLED
    pnl: float | None = None                        # only when an execution exists
    model_probability_error: float | None = None
    handicap_probability_error: float | None = None
    market_probability_error: float | None = None
    calibration_bucket: str | None = None
    reasoning_tags: list = field(default_factory=list)
    close_basis: str | None = None                  # how close was established, or why it is missing
    test_only: bool = False

    def to_dict(self):
        return asdict(self)


@dataclass
class Postmortem:
    postmortem_id: str
    schema_version: str
    recommendation_id: str
    written_at: str
    categories: list = field(default_factory=list)
    confidence: str = "medium"                      # low / medium / high -- never asserted as certain
    narrative: str = ""
    lessons: list = field(default_factory=list)
    test_only: bool = False

    def to_dict(self):
        return asdict(self)


# ---- construction helpers --------------------------------------------------------------------------

def new_recommendation_id(handicap_run_id: str, market_ticker: str, side: str, created_at: str) -> str:
    return _uid("rec", handicap_run_id, market_ticker, side, created_at)


def new_execution_id(recommendation_id: str, executed_at: str, actual_price) -> str:
    return _uid("exe", recommendation_id, executed_at, actual_price)


def new_evaluation_id(recommendation_id: str, evaluated_at: str) -> str:
    return _uid("evl", recommendation_id, evaluated_at)


def new_postmortem_id(recommendation_id: str, written_at: str) -> str:
    return _uid("pmt", recommendation_id, written_at)


# ---- validation ------------------------------------------------------------------------------------

def _prob(name, v, allow_none=True):
    if v is None:
        if allow_none:
            return
        raise ValidationError(f"{name} is required")
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        raise ValidationError(f"{name} must be numeric, got {type(v).__name__}")
    if not (0.0 <= float(v) <= 1.0):
        raise ValidationError(f"{name} must be a probability in [0,1], got {v}")


def validate_recommendation(d: dict) -> list:
    """Return a list of warnings; raise ValidationError on anything that must not be committed."""
    warn = []
    for req in ("recommendation_id", "created_at", "handicap_run_id", "market_ticker", "decision", "side"):
        if not d.get(req):
            raise ValidationError(f"missing required field: {req}")
    if not _ID_RE.match(str(d["recommendation_id"])):
        raise ValidationError(f"recommendation_id has unsafe characters: {d['recommendation_id']!r}")
    if d["decision"] not in DECISIONS:
        raise ValidationError(f"decision must be one of {DECISIONS}, got {d['decision']!r}")
    if d["side"] not in SIDES:
        raise ValidationError(f"side must be YES or NO, got {d['side']!r}")
    if d.get("grade") is not None and d["grade"] not in GRADES:
        raise ValidationError(f"grade must be one of {GRADES}, got {d['grade']!r}")

    for k in ("yes_bid", "yes_ask", "no_bid", "no_ask", "mid", "model_probability",
              "probability_low", "probability_mid", "probability_high", "bet_up_to_probability"):
        _prob(k, d.get(k))

    lo, mid, hi = d.get("probability_low"), d.get("probability_mid"), d.get("probability_high")
    if lo is not None and hi is not None and lo > hi:
        raise ValidationError(f"probability_low {lo} exceeds probability_high {hi}")
    if mid is not None and lo is not None and mid < lo:
        raise ValidationError(f"probability_mid {mid} below probability_low {lo}")
    if mid is not None and hi is not None and mid > hi:
        raise ValidationError(f"probability_mid {mid} above probability_high {hi}")

    stake = d.get("recommended_stake")
    if stake is not None:
        if isinstance(stake, bool) or not isinstance(stake, int):
            raise ValidationError(f"recommended_stake must be a whole-dollar integer, got {stake!r}")
        if stake < 0:
            raise ValidationError(f"recommended_stake must be non-negative, got {stake}")

    if d["decision"] == RECOMMENDED:
        # A recommendation the user cannot act on is not a recommendation.
        if d.get("bet_up_to_probability") is None:
            raise ValidationError("a RECOMMENDED record requires bet_up_to_probability")
        if not d.get("primary_thesis"):
            raise ValidationError("a RECOMMENDED record requires a primary_thesis")
        if d.get("grade") in (None, "PASS"):
            raise ValidationError("a RECOMMENDED record requires a grade other than PASS")
        # The price must actually be available at or under the ceiling, or the record is internally
        # inconsistent: it recommends buying above the stated maximum.
        ask = d.get("yes_ask") if d["side"] == "YES" else d.get("no_ask")
        if ask is not None and d["bet_up_to_probability"] < ask:
            warn.append(f"bet_up_to {d['bet_up_to_probability']} is below the {d['side']} ask {ask} -- "
                        "this recommendation is not currently actionable")
        if not d.get("recommended_stake"):
            warn.append("RECOMMENDED without a recommended_stake")
    if d["decision"] == PASS and d.get("grade") not in (None, "PASS"):
        warn.append(f"PASS record carries grade {d['grade']!r}")
    if d["decision"] == PASS and not d.get("primary_thesis"):
        warn.append("PASS without a stated reason is not scientifically useful")

    for tag in (d.get("reasoning_tags") or []):
        if tag not in CORE_REASONING_TAGS:
            warn.append(f"uncontrolled reasoning_tag {tag!r} (allowed, reported separately)")
    return warn


def validate_execution(d: dict) -> list:
    for req in ("execution_id", "recommendation_id", "executed_at", "side"):
        if not d.get(req):
            raise ValidationError(f"missing required field: {req}")
    if d["side"] not in SIDES:
        raise ValidationError(f"side must be YES or NO, got {d['side']!r}")
    _prob("actual_price", d.get("actual_price"), allow_none=False)
    stake = d.get("stake")
    if isinstance(stake, bool) or not isinstance(stake, int) or stake <= 0:
        raise ValidationError(f"stake must be a positive whole-dollar integer, got {stake!r}")
    return []


def validate_postmortem(d: dict) -> list:
    for req in ("postmortem_id", "recommendation_id", "written_at"):
        if not d.get(req):
            raise ValidationError(f"missing required field: {req}")
    cats = d.get("categories") or []
    if not cats:
        raise ValidationError("a postmortem must carry at least one category")
    bad = [c for c in cats if c not in POSTMORTEM_CATEGORIES]
    if bad:
        raise ValidationError(f"unknown postmortem categories: {bad}")
    if d.get("confidence") not in ("low", "medium", "high"):
        raise ValidationError("confidence must be low, medium or high")
    return []


VALIDATORS = {
    "recommendation": validate_recommendation,
    "execution": validate_execution,
    "postmortem": validate_postmortem,
}


def write_record(path: str, payload: dict, *, overwrite: bool = False):
    """Append-only file write. Refuses to clobber an existing record.

    This is the immutability guarantee. A revised opinion is a new file with `amends` pointing at the old
    one; the original price, timestamp and reasoning stay exactly as they were written.
    """
    if os.path.exists(path) and not overwrite:
        raise ValidationError(
            f"record already exists and records are immutable: {path}. To revise a decision, write a NEW "
            "record with `amends` set to the original recommendation_id.")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(payload, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)
    return path
