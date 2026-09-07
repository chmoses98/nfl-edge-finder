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
  DECISION GATES  derived at import time: the freshness, identity, availability, cost and risk checks a
                  RECOMMENDED record had to pass, with the evidence each one saw.

The immutability rule is enforced by the writer, not by convention: `write_record` refuses to overwrite an
existing path. A changed mind is a NEW record carrying `amends`, so the original opinion and the original
observed price survive. Nothing here rewrites history.

FAIL CLOSED
-----------
The four decisions are NOT held to the same standard, and that asymmetry is the design:

    RECOMMENDED     asks the user to risk money. It must carry the complete professional decision record --
                    identity, lineage, market state, a probability band, a ceiling, a stake, a thesis with
                    its counterarguments, and an explicit statement of what quantitative support it rests on.
                    Anything missing is a hard rejection, not a warning. A warning on a record that is about
                    to become canonical is a warning nobody reads.

    PASS            is a scientific record of a contract that was declined. It is deliberately cheaper to
                    write: requiring a full market snapshot before you may record "the price already
                    reflects the news" would mean the passes never get written, and the comparison of what
                    was taken against what was declined is the most informative thing this ledger will
                    produce.

    WATCHLIST       the same, plus an explicit reason when it is waiting on data.
    RESEARCH_ALERT  a note to the research program, not a betting instruction.

The rule that decides which side of that line a check falls on: does the failure mode cost money, or cost
information? Money-losing failures are errors on RECOMMENDED. Information-losing failures are warnings.

THE CEILING IS A CEILING
------------------------
`bet_up_to_probability` is the maximum price the handicapper will pay. If the executable ask on our side is
ABOVE it, the record recommends buying above its own stated maximum, and it is rejected. It was previously a
warning; a canonical ledger that can say "BET up to 0.58" while the book asks 0.61 is recording an
instruction nobody should follow.

PRICE CONVENTION AND FEES
-------------------------
`bet_up_to_probability` is a Kalshi probability in the same units the user sees when placing the order (0-1
as quoted, i.e. cents/100). Fees are deliberately NOT folded into it -- the user's workflow treats the
displayed price as the cost basis, and fee-aware economics live in nfl_edge/execution/fees.py where they can
be varied without rewriting a single historical recommendation. The displayed pair stays "Current: 56% /
Bet up to: 59%"; net-of-cost economics are a separate, separately-named calculation.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

# 1.1.0 tightens RECOMMENDED to the professional minimum decision record and adds the support-state,
# availability and stake-provenance fields the gates need. It is backward compatible for PASS/WATCHLIST/
# RESEARCH_ALERT and for every record already in the ledger.
HANDICAP_SCHEMA_VERSION = "1.1.0"

# ---- decisions -------------------------------------------------------------------------------------
RECOMMENDED = "RECOMMENDED"
PASS = "PASS"
WATCHLIST = "WATCHLIST"
RESEARCH_ALERT = "RESEARCH_ALERT"
DECISIONS = (RECOMMENDED, PASS, WATCHLIST, RESEARCH_ALERT)

# ---- quantitative support state --------------------------------------------------------------------
# Mirrors nfl_edge/shadow/ledger.py so a recommendation says, in the ledger's own vocabulary, what the model
# could and could not do for this market. It is required on RECOMMENDED: "the model did not price this" is a
# legitimate thing for a handicapper to act on, but it must be SAID, not left to be inferred from a null.
SUPPORT_SUPPORTED = "SUPPORTED"                       # the model priced this market
SUPPORT_UNSUPPORTED_MODEL = "UNSUPPORTED_MODEL"       # no validated model for this family
SUPPORT_UNSUPPORTED_RULES = "UNSUPPORTED_RULES"       # settlement semantics not established
SUPPORT_UNSUPPORTED_IDENTITY = "UNSUPPORTED_IDENTITY"  # Kalshi player id not resolved to a GSIS id
SUPPORT_UNSUPPORTED_GAME = "UNSUPPORTED_GAME"         # market did not join a scheduled game
SUPPORT_QUALITATIVE_ONLY = "QUALITATIVE_ONLY"         # judged without quantitative support, deliberately
SUPPORT_STATES = (SUPPORT_SUPPORTED, SUPPORT_UNSUPPORTED_MODEL, SUPPORT_UNSUPPORTED_RULES,
                  SUPPORT_UNSUPPORTED_IDENTITY, SUPPORT_UNSUPPORTED_GAME, SUPPORT_QUALITATIVE_ONLY)

# A recommendation must never rest on a player identity we could not resolve. Coverage is not worth identity
# integrity: an unresolved Kalshi->GSIS mapping means we do not know whose statistics we priced.
SUPPORT_STATES_BLOCKING_RECOMMENDED = (SUPPORT_UNSUPPORTED_IDENTITY,)

# States that assert a model number stands behind the record, and therefore require model lineage.
SUPPORT_STATES_REQUIRING_MODEL = (SUPPORT_SUPPORTED,)

# ---- player availability ---------------------------------------------------------------------------
# The vocabulary is nfl_edge/settlement/availability.py's; it is restated here so a record can be validated
# without importing the settlement layer.
AVAILABILITY_STATES = ("EXPECTED_ACTIVE", "QUESTIONABLE", "DOUBTFUL", "EXPECTED_OUT", "OUT",
                       "INACTIVE_CONFIRMED", "UNKNOWN")
# Official inactives are released 90 minutes before kickoff. A status still unresolved inside that window is
# not "probably fine" -- it is the one window in which the answer is knowable and we have not looked.
UNRESOLVED_STATUS_GATE_MIN = 90.0
# Availability older than this is not evidence of anything. Six hours matches AvailabilityBook's own default
# staleness threshold, so the two layers cannot disagree about what "current" means.
MAX_AVAILABILITY_STALE_MIN = 360.0
# Families whose settlement depends on a specific player taking the field. For these, availability is not
# context -- it is a term in the price.
PLAYER_MARKET_FAMILIES = ("PLAYER_STAT", "FIRST_TD_SCORER", "ANYTIME_TD")

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
    support_state: str | None = None                # SUPPORT_STATES; required on RECOMMENDED
    support_reason: str | None = None               # why, when it is not SUPPORTED
    model_version: str | None = None
    artifact_hash: str | None = None
    model_probability: float | None = None
    model_projection: dict | None = None
    market_implied_projection: dict | None = None

    # PLAYER AVAILABILITY -- a term in the price for player markets, not background colour
    availability_state: str | None = None
    availability_as_of: str | None = None
    availability_stale_minutes: float | None = None
    availability_sources: dict | None = None

    # CHATGPT HANDICAP
    probability_low: float | None = None
    probability_mid: float | None = None
    probability_high: float | None = None
    bet_up_to_probability: float | None = None      # Kalshi price units, fees NOT folded in
    grade: str | None = None
    # Two stakes, deliberately. `proposed_stake` is what the handicapper asked for; `recommended_stake` is
    # what the risk policy approved. Keeping both is what makes the policy auditable -- see
    # nfl_edge/handicap/risk.py. When no policy ran they are equal.
    proposed_stake: int | None = None               # whole dollars, before portfolio limits
    recommended_stake: int | None = None            # whole dollars, after portfolio limits
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
    """One FILL. Not one position -- one fill.

    A single recommendation is routinely filled in pieces at different prices, and each piece is its own
    immutable record. Economics are computed per fill and aggregated upward; nothing anywhere collapses two
    fills into a single fake price. Where a weighted average is genuinely useful it is derived on demand and
    labelled derived (see nfl_edge/handicap/evaluate.py), never stored as if it were an observed fill.

    `fees_paid` is what the venue actually charged. `fees_are_estimated` says whether that number was
    observed or modelled -- a modelled fee is a perfectly good input to a net-P/L estimate and a completely
    unacceptable input to a realised-P/L claim, so the two can never be confused.
    """
    execution_id: str
    schema_version: str
    recommendation_id: str
    executed_at: str
    actual_price: float
    stake: float                                    # gross dollars staked on THIS fill
    side: str
    contracts: float | None = None                  # fractional permitted; see fees.taker_fee
    fees_paid: float | None = None
    fees_are_estimated: bool = False                # True => this is a model output, not a venue charge
    fee_state: str | None = None                    # KNOWN / UNKNOWN / DEGRADED when the fee was modelled
    execution_style: str | None = None              # taker / maker, for fee attribution
    order_id: str | None = None                     # venue order this fill belongs to, when known
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
    # P/L, aggregated over EVERY fill on the recommendation. Gross and net are separate fields because they
    # answer different questions: gross says whether the call was right, net says whether the bankroll grew.
    # `pnl` is retained as an alias of gross_pnl so older readers keep working; new code reads the explicit
    # names.
    pnl: float | None = None                        # == gross_pnl; kept for backward compatibility
    gross_pnl: float | None = None
    fees_paid: float | None = None                  # actual venue fees, summed across fills
    fees_estimated: float | None = None             # modelled fees, summed; NEVER added to fees_paid
    fees_basis: str | None = None                   # ACTUAL / ESTIMATED / MIXED / NONE
    net_pnl: float | None = None                    # gross_pnl - fees (actual where present)
    gross_dollars_staked: float | None = None
    contracts: float | None = None
    n_executions: int = 0
    average_execution_price: float | None = None    # DERIVED, stake-weighted. Not an observed fill price.
    net_roi: float | None = None
    entry_slippage: float | None = None             # weighted execution price - recommendation-time ask
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
class DecisionGates:
    """Proof that a RECOMMENDED record cleared every real-money gate, and what each gate saw.

    Written as its own immutable file alongside the recommendation, for one specific reason: the
    recommendation is what the handicapper decided and must hash the same on every replay, while the gates
    are what the importer observed at import time. Stamping observations into the recommendation would make
    a byte-identical re-import impossible, and the bridge's idempotency depends on that comparison.

    Gates run ONCE, when the record is first materialised. A record already durably in the ledger was gated
    when it was written; re-gating it later would test today's market against yesterday's decision and fail
    for the wrong reason.
    """
    gates_id: str
    schema_version: str
    recommendation_id: str
    evaluated_at: str
    decision: str
    overall: str                                    # PASS / FAIL / NOT_APPLICABLE
    gates: dict = field(default_factory=dict)       # name -> {status, reason, evidence}
    decision_quote: dict | None = None              # the freshest confirmed executable quote, verbatim
    net_ev: dict | None = None                      # gross edge, fees, slippage, net -- see execution/fees
    risk: dict | None = None                        # the portfolio verdict for this record
    blocking_reasons: list = field(default_factory=list)
    warnings: list = field(default_factory=list)      # seen, recorded, not blocking
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


def new_gates_id(recommendation_id: str) -> str:
    """Deterministic in the recommendation id alone.

    Gates are evaluated exactly once per recommendation, so a second attempt to write them collides with the
    existing file and `write_record` refuses it -- which is the behaviour we want. An id that also hashed the
    evaluation time would let a re-run quietly write a second, contradictory verdict.
    """
    return _uid("gat", recommendation_id)


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


# ---- what a RECOMMENDED record must carry ----------------------------------------------------------
# The professional minimum decision record: enough to reconstruct, months later, WHAT was bet, WHEN, at WHAT
# price, on WHOSE authority, and against WHAT information. A field is on this list only if its absence would
# make one of those questions unanswerable.
REQUIRED_FOR_RECOMMENDED = (
    # identity / lineage -- which decision, from which run, from which packet, on which contract
    ("recommendation_id", "the record's own identity"),
    ("created_at", "when the decision was made"),
    ("handicap_run_id", "which handicap run produced it"),
    ("packet_sha", "which packet it was decided from; without it the inputs cannot be reconstructed"),
    ("season", "slate identity"),
    ("week", "slate identity"),
    ("game_id", "which game"),
    ("kickoff_utc", "when the market resolves, and the deadline the decision had to beat"),
    ("market_ticker", "which contract"),
    ("market_family", "which kind of contract, for attribution"),
    ("side", "YES or NO"),
    # market state at decision time
    ("market_timestamp", "when the quoted market state was observed"),
    ("minutes_to_kickoff", "how far from kickoff the decision was made"),
    # handicap
    ("probability_low", "the bottom of the probability band"),
    ("probability_mid", "the point estimate"),
    ("probability_high", "the top of the probability band"),
    ("bet_up_to_probability", "the maximum price the handicapper will pay"),
    ("grade", "the handicapper's confidence"),
    ("primary_thesis", "why"),
    # model / data lineage
    ("support_state", "what quantitative support this rests on, stated rather than inferred from a null"),
    ("source_freshness", "what information was available, so the decision can be reconstructed"),
)

# Reasoning that a professional record must show its own weaknesses. A thesis with no counterargument and no
# stated uncertainty is advocacy, not analysis, and the postmortem that eventually reads it has nothing to
# check the call against.
REQUIRED_LISTS_FOR_RECOMMENDED = (
    ("key_supporting_factors", "what the thesis rests on"),
    ("counterarguments", "the case against the position"),
    ("uncertainties", "what could make this wrong"),
)


def _side_ask(d: dict):
    """The price payable on OUR side. Never the midpoint -- a midpoint is not an executable price."""
    return d.get("yes_ask") if d.get("side") == "YES" else d.get("no_ask")


def validate_recommendation(d: dict) -> list:
    """Return a list of warnings; raise ValidationError on anything that must not be committed.

    RECOMMENDED records are held to the full professional standard and every shortfall raises. PASS,
    WATCHLIST and RESEARCH_ALERT keep the lighter treatment on purpose -- see the module docstring for why
    the asymmetry is deliberate rather than an oversight.
    """
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

    for name in ("recommended_stake", "proposed_stake"):
        stake = d.get(name)
        if stake is not None:
            if isinstance(stake, bool) or not isinstance(stake, int):
                raise ValidationError(f"{name} must be a whole-dollar integer, got {stake!r}")
            if stake < 0:
                raise ValidationError(f"{name} must be non-negative, got {stake}")

    if d.get("support_state") is not None and d["support_state"] not in SUPPORT_STATES:
        raise ValidationError(f"support_state must be one of {SUPPORT_STATES}, got {d['support_state']!r}")
    if d.get("availability_state") is not None and d["availability_state"] not in AVAILABILITY_STATES:
        raise ValidationError(
            f"availability_state must be one of {AVAILABILITY_STATES}, got {d['availability_state']!r}")

    if d["decision"] == RECOMMENDED:
        _validate_recommended(d, warn)

    if d["decision"] == PASS and d.get("grade") not in (None, "PASS"):
        warn.append(f"PASS record carries grade {d['grade']!r}")
    if d["decision"] == PASS and not d.get("primary_thesis"):
        warn.append("PASS without a stated reason is not scientifically useful")

    for tag in (d.get("reasoning_tags") or []):
        if tag not in CORE_REASONING_TAGS:
            warn.append(f"uncontrolled reasoning_tag {tag!r} (allowed, reported separately)")
    return warn


def _validate_recommended(d: dict, warn: list) -> None:
    """Everything a record must satisfy before it may ask the user to risk money.

    Every check here RAISES. That is the point: a warning attached to a record that is about to become
    canonical is a warning nobody reads, and the ledger has no second chance to catch it -- records are
    immutable, so a defective RECOMMENDED record is permanent.
    """
    missing = [(f, why) for f, why in REQUIRED_FOR_RECOMMENDED if d.get(f) is None or d.get(f) == ""]
    if missing:
        detail = "; ".join(f"{f} ({why})" for f, why in missing)
        raise ValidationError(
            f"a RECOMMENDED record is incomplete and cannot be committed. Missing: {detail}. "
            "A record that asks the user to risk money must carry the full decision record; if these are "
            "not available, record the contract as WATCHLIST or PASS with the reason.")

    for fname, why in REQUIRED_LISTS_FOR_RECOMMENDED:
        v = d.get(fname)
        if not isinstance(v, (list, tuple)) or not [x for x in v if str(x).strip()]:
            raise ValidationError(
                f"a RECOMMENDED record requires a non-empty {fname} ({why}); a thesis with no stated "
                "counterargument or uncertainty cannot be audited after the fact")

    if d.get("grade") == "PASS":
        raise ValidationError("a RECOMMENDED record requires a grade other than PASS")

    # ---- the ceiling is a ceiling ----------------------------------------------------------------
    # The side-specific ask is what we would actually pay. It must exist, and it must not be above the
    # stated maximum. Both were previously warnings; both are now hard failures, because the ledger must
    # never canonically record "BET up to 0.58" while the book is asking 0.61.
    ask = _side_ask(d)
    if ask is None:
        raise ValidationError(
            f"a RECOMMENDED record requires the executable {d['side']} ask "
            f"({'yes_ask' if d['side'] == 'YES' else 'no_ask'}). A midpoint is not an executable price and "
            "is not accepted in its place.")
    if float(ask) > float(d["bet_up_to_probability"]) + 1e-9:
        raise ValidationError(
            f"NOT ACTIONABLE: the executable {d['side']} ask {ask} is ABOVE bet_up_to_probability "
            f"{d['bet_up_to_probability']}. This record instructs a purchase above its own stated maximum "
            "price and is refused. Record it as WATCHLIST until the price comes to you, or raise the "
            "ceiling in a new record with a stated reason.")

    # ---- stake -----------------------------------------------------------------------------------
    stake = d.get("recommended_stake")
    if stake is None or isinstance(stake, bool) or not isinstance(stake, int) or stake <= 0:
        raise ValidationError(
            f"a RECOMMENDED record requires a positive whole-dollar recommended_stake, got {stake!r}. "
            "A recommendation with no size is not a position and cannot be scored for ROI.")
    proposed = d.get("proposed_stake")
    if proposed is not None and stake > proposed:
        raise ValidationError(
            f"recommended_stake {stake} exceeds proposed_stake {proposed}; the risk policy may only cap a "
            "proposal downward, never raise it")

    # ---- quantitative support --------------------------------------------------------------------
    support = d["support_state"]
    if support in SUPPORT_STATES_BLOCKING_RECOMMENDED:
        raise ValidationError(
            f"support_state {support!r} cannot carry a RECOMMENDED record. An unresolved Kalshi->GSIS player "
            "identity means we do not know whose statistics were priced; the market stays visible and "
            "quotable, but it may not become a real recommendation. Coverage is never traded for identity "
            "integrity.")
    if support in SUPPORT_STATES_REQUIRING_MODEL:
        for f in ("model_version", "model_probability"):
            if d.get(f) is None:
                raise ValidationError(
                    f"support_state is {support!r}, which asserts the model priced this market, so {f} is "
                    "required. If the decision was in fact qualitative, say so with "
                    f"support_state={SUPPORT_QUALITATIVE_ONLY!r} rather than claiming support the record "
                    "cannot evidence.")
        if not d.get("artifact_hash"):
            warn.append("support_state SUPPORTED without an artifact_hash: the model version is recorded "
                        "but the exact artifact cannot be pinned")
    elif support != SUPPORT_QUALITATIVE_ONLY and not d.get("support_reason"):
        raise ValidationError(
            f"support_state {support!r} requires a support_reason saying what the model could not do here")

    # A qualitative call is legitimate. Quietly carrying a model number while claiming to be qualitative is
    # not: the scorecard would score a forecast the handicapper says they did not use.
    if support != SUPPORT_SUPPORTED and d.get("model_probability") is not None:
        warn.append(
            f"support_state is {support!r} but model_probability is set; it will be scored as a model "
            "forecast even though the record says the model does not support this market")

    # ---- freshness of the recorded market state --------------------------------------------------
    mtk = d.get("minutes_to_kickoff")
    if isinstance(mtk, (int, float)) and not isinstance(mtk, bool) and mtk <= 0:
        raise ValidationError(
            f"minutes_to_kickoff is {mtk}: the market is at or past kickoff and a post-kickoff record is "
            "not a prospective recommendation")

    # ---- player availability ---------------------------------------------------------------------
    # Applied ONLY to markets whose settlement depends on a specific player taking the field. A game-level
    # market is not gated on anybody's injury status, and pretending otherwise would block half the board
    # for a reason that does not apply to it.
    if d.get("market_family") in PLAYER_MARKET_FAMILIES:
        _validate_player_availability(d)


def _validate_player_availability(d: dict) -> None:
    """Availability gates for player markets, under Kalshi's participation settlement semantics.

    A YES player prop needs the player on the field. Where participation risk is unresolved, the honest
    record is WATCHLIST until it resolves -- not a RECOMMENDED position whose real exposure is to an inactive
    list nobody has read yet.
    """
    state = d.get("availability_state")
    if state is None:
        raise ValidationError(
            "a RECOMMENDED player-market record requires availability_state. Settlement on these contracts "
            "depends on the player taking the field, so an unrecorded availability is an unpriced term.")
    if not d.get("availability_as_of"):
        raise ValidationError(
            "a RECOMMENDED player-market record requires availability_as_of; an availability with no "
            "timestamp cannot be shown to have been current when the decision was made")

    side = d.get("side")
    if state == "INACTIVE_CONFIRMED" and side == "YES":
        raise ValidationError(
            "availability_state INACTIVE_CONFIRMED cannot carry a RECOMMENDED YES player prop: the player is "
            "on the official inactive list and the contract settles at $0.00.")
    if state in ("EXPECTED_OUT", "OUT") and side == "YES":
        raise ValidationError(
            f"availability_state {state!r} cannot carry a RECOMMENDED YES player prop. The measured play "
            "rate for these states is under 2%, so the position is a bet on the injury report being wrong "
            "rather than on the player's production.")
    if state == "UNKNOWN":
        raise ValidationError(
            "availability_state UNKNOWN cannot carry a RECOMMENDED player prop: our sources did not find "
            "this player at all, so participation risk is unquantified. Record it as WATCHLIST until "
            "availability resolves.")
    if state in ("QUESTIONABLE", "DOUBTFUL"):
        mtk = d.get("minutes_to_kickoff")
        if isinstance(mtk, (int, float)) and not isinstance(mtk, bool) and mtk <= UNRESOLVED_STATUS_GATE_MIN:
            raise ValidationError(
                f"availability_state {state!r} within {UNRESOLVED_STATUS_GATE_MIN:.0f} minutes of kickoff "
                f"({mtk:.0f} min) cannot carry a RECOMMENDED player prop. Inactives are released at "
                "T-90m; a status still unresolved inside that window means participation risk is driving "
                "the value and the honest record is WATCHLIST until the list is out.")

    stale = d.get("availability_stale_minutes")
    if isinstance(stale, (int, float)) and not isinstance(stale, bool) and stale > MAX_AVAILABILITY_STALE_MIN:
        raise ValidationError(
            f"availability data is {stale:.0f} minutes old, beyond the "
            f"{MAX_AVAILABILITY_STALE_MIN:.0f} minute limit for a RECOMMENDED player prop. A stale "
            "availability silently reads as ACTIVE, which is exactly the failure this check exists to stop.")


def validate_execution(d: dict) -> list:
    """One fill. Stake may be fractional; a partial fill is not a whole number of dollars."""
    warn = []
    for req in ("execution_id", "recommendation_id", "executed_at", "side"):
        if not d.get(req):
            raise ValidationError(f"missing required field: {req}")
    if d["side"] not in SIDES:
        raise ValidationError(f"side must be YES or NO, got {d['side']!r}")
    _prob("actual_price", d.get("actual_price"), allow_none=False)

    stake = d.get("stake")
    if isinstance(stake, bool) or not isinstance(stake, (int, float)) or stake <= 0:
        raise ValidationError(f"stake must be a positive dollar amount, got {stake!r}")

    contracts = d.get("contracts")
    if contracts is not None:
        if isinstance(contracts, bool) or not isinstance(contracts, (int, float)) or contracts <= 0:
            raise ValidationError(f"contracts must be a positive quantity, got {contracts!r}")
        # stake = contracts * price is an identity, not a convention. A record where it does not hold is
        # describing two different fills, and every downstream P/L number would be wrong in a way no
        # aggregate could reveal.
        implied = float(contracts) * float(d["actual_price"])
        if abs(implied - float(stake)) > max(0.01, 0.005 * float(stake)):
            raise ValidationError(
                f"stake {stake} does not match contracts {contracts} at price {d['actual_price']} "
                f"(implies {implied:.4f}); an execution must be internally consistent")

    fees = d.get("fees_paid")
    if fees is not None:
        if isinstance(fees, bool) or not isinstance(fees, (int, float)) or fees < 0:
            raise ValidationError(f"fees_paid must be a non-negative dollar amount, got {fees!r}")
        if d.get("fees_are_estimated") and not d.get("fee_state"):
            warn.append("fees_are_estimated is set but fee_state is not; an estimated fee should say "
                        "whether the schedule that produced it was KNOWN")
    elif d.get("fees_are_estimated"):
        raise ValidationError("fees_are_estimated is set but fees_paid is None; there is no estimate")

    style = d.get("execution_style")
    if style is not None and style not in ("taker", "maker"):
        raise ValidationError(f"execution_style must be 'taker' or 'maker', got {style!r}")
    return warn


def validate_evaluation(d: dict) -> list:
    """Derived record. Validated so a bad aggregation cannot quietly enter the scorecard."""
    for req in ("evaluation_id", "recommendation_id", "evaluated_at"):
        if not d.get(req):
            raise ValidationError(f"missing required field: {req}")
    for k in ("close_yes_bid", "close_yes_ask", "close_mid", "closing_executable"):
        _prob(k, d.get(k))
    if d.get("settlement") is not None and float(d["settlement"]) not in (0.0, 1.0):
        raise ValidationError(f"settlement must be 0.0 or 1.0, got {d['settlement']}")
    basis = d.get("fees_basis")
    if basis is not None and basis not in ("ACTUAL", "ESTIMATED", "MIXED", "NONE"):
        raise ValidationError(f"fees_basis must be ACTUAL/ESTIMATED/MIXED/NONE, got {basis!r}")
    # gross - fees = net is the whole point of keeping three fields. If they disagree, one of them is a
    # number somebody typed rather than a number something computed.
    g, f, n = d.get("gross_pnl"), d.get("fees_paid"), d.get("net_pnl")
    if g is not None and n is not None:
        expected = float(g) - float(f or 0.0)
        if abs(expected - float(n)) > 0.011:
            raise ValidationError(
                f"net_pnl {n} does not equal gross_pnl {g} minus fees_paid {f or 0.0} ({expected:.2f})")
    if d.get("pnl") is not None and g is not None and abs(float(d["pnl"]) - float(g)) > 1e-6:
        raise ValidationError(f"pnl {d['pnl']} disagrees with gross_pnl {g}; pnl is an alias of gross_pnl")
    return []


def validate_decision_gates(d: dict) -> list:
    for req in ("gates_id", "recommendation_id", "evaluated_at", "decision", "overall"):
        if not d.get(req):
            raise ValidationError(f"missing required field: {req}")
    if d["overall"] not in ("PASS", "FAIL", "NOT_APPLICABLE"):
        raise ValidationError(f"overall must be PASS/FAIL/NOT_APPLICABLE, got {d['overall']!r}")
    if d["decision"] == RECOMMENDED and d["overall"] != "PASS":
        raise ValidationError(
            "a gates record for a RECOMMENDED recommendation must be PASS; a FAIL means the recommendation "
            "should never have been written")
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
    "evaluation": validate_evaluation,
    "decision_gates": validate_decision_gates,
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
