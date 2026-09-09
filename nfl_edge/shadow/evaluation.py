"""Derived evaluation records: enrich a prediction with what the market did next, WITHOUT touching it.

The ledger is append-only and a written observation is immutable. Closing-line value, markouts and
settlement are therefore recorded as separate derived rows keyed by `prediction_id`, so a snapshot can be
re-evaluated as later quotes arrive while the original prediction stays exactly as it was made.

`MISSING_CLOSE` is a real, recorded outcome. A post-kickoff quote is never substituted for a pregame close.

WHAT A ROW CARRIES, AND WHY IT IS SELF-CONTAINED
------------------------------------------------
An evaluation row repeats the state at prediction time (model probability, both sides of the book, availability
state, time to kickoff) instead of pointing at the ledger row it came from. Two reasons: a research query
should never have to join two immutable corpora to ask "how did the model do at T-90m on wide markets", and a
row that carries its own inputs can be checked against the ledger long afterwards, which is what makes a
contradiction detectable at all.

The segmentation bands (`disagreement_band`, `horizon_band`, `probability_band`) are computed once, here, so
every report slices the same way. A band computed per report is a band that quietly changes between reports.

THREE THINGS THAT ARE DELIBERATELY NOT THE SAME FIELD
-----------------------------------------------------
`settled_yes`        what one YES contract paid, in dollars. 0.5 for a tied game winner; the pregame fair
                     price for a player who was active but never took a snap.
`settlement_kind`    how that payout arose. ONLY `binary` is a 0/1 realisation of the football event, so only
                     `binary` rows may enter a Brier score or a calibration bucket.
`settlement_status`  SETTLED, or the REFUSED_* reason the payout could not be proven. A refusal is recorded,
                     never a guessed 0.
"""
from __future__ import annotations

import gzip
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

EVALUATION_SCHEMA_VERSION = "1.0.0"
# The evaluation VERSION is the identity of one truth about a prediction: the store holds exactly one
# evaluation per (prediction_id, evaluation_version). Bump it when the meaning of a field changes, never to
# re-run the same logic -- a re-run of the same version must be a no-op.
EVALUATION_VERSION = "eval-1.0.0"

MISSING_CLOSE = "MISSING_CLOSE"
CLOSE_OK = "OK"
CLOSE_OK_STALE = "OK_STALE"
CLOSE_INCOMPLETE = "INCOMPLETE_CLOSE"
CLOSE_MAX_STALENESS_S = 3600.0     # a "close" more than an hour before kickoff is reported, not silently used

# Disagreement bands in probability points, |model contract value - market mid|.
DISAGREEMENT_BANDS = ((0.03, "<3%"), (0.05, "3-5%"), (0.10, "5-10%"), (0.20, "10-20%"), (float("inf"), "20%+"))
# Time-to-kickoff bands, labelled by the INTERVAL they cover rather than by a horizon they are near. A
# snapshot 380 minutes before kickoff is not "the T-6h snapshot", and calling it that makes a table of results
# read as if six-hour predictions were being compared when they were not. The T-30m/T-90m/T-6h/T-24h horizons
# the research question asks about are the lower edges of these intervals, and `close_minutes_to_kickoff`
# carries the exact distance whenever a finer cut is wanted.
HORIZON_BANDS = ((30.0, "<30m"), (90.0, "30-90m"), (360.0, "90m-6h"), (1440.0, "6-24h"), (float("inf"), ">24h"))


@dataclass
class Evaluation:
    prediction_id: str
    run_id: str
    ticker: str
    model_version: str
    evaluated_at: str
    # ---- identity of this evaluation
    schema_version: str = EVALUATION_SCHEMA_VERSION
    evaluation_version: str = EVALUATION_VERSION
    evaluation_id: str | None = None
    # ---- contract and football identity, copied so a row stands alone
    game_id: str | None = None
    season: int | None = None
    week: int | None = None
    family: str | None = None
    period: str | None = None
    stat: str | None = None
    threshold: float | None = None
    operator: str | None = None
    floor_strike: float | None = None
    team: str | None = None
    player_id: str | None = None
    player_name: str | None = None
    kickoff_utc: str | None = None
    support_state: str | None = None
    calibration_version: str | None = None
    model_artifact_sha: str | None = None
    # state at prediction time, copied for self-containment
    observed_at: str | None = None
    minutes_to_kickoff: float | None = None
    model_p: float | None = None
    model_event_probability: float | None = None
    calibrated_probability: float | None = None
    yes_bid_t: float | None = None
    yes_ask_t: float | None = None
    no_bid_t: float | None = None
    no_ask_t: float | None = None
    mid_t: float | None = None
    model_direction: str | None = None          # yes | no | none
    volume_t: float | None = None
    open_interest_t: float | None = None
    liquidity_t: float | None = None
    minutes_since_price_change_t: float | None = None
    # availability state at prediction time -- kept so information-shock research is possible later
    availability_state: str | None = None
    p_plays: float | None = None
    p_inactive: float | None = None
    # later state
    close_mid: float | None = None
    close_yes_bid: float | None = None
    close_yes_ask: float | None = None
    close_observed_at: str | None = None
    close_minutes_to_kickoff: float | None = None
    close_status: str = MISSING_CLOSE
    close_is_stale: bool | None = None
    close_run_id: str | None = None
    close_volume: float | None = None
    close_open_interest: float | None = None
    close_liquidity: float | None = None
    close_candidates_seen: int | None = None
    # derived
    signed_clv_mid: float | None = None
    signed_clv_executable: float | None = None
    movement: str | None = None                 # toward | away | unchanged | no_view
    width_t: float | None = None
    width_close: float | None = None
    width_change: float | None = None
    liquidity_change: float | None = None
    model_market_disagreement: float | None = None
    disagreement_band: str | None = None
    probability_band: str | None = None
    horizon_band: str | None = None
    # settlement
    settled_yes: float | None = None
    settlement_status: str | None = None
    settlement_kind: str | None = None
    settlement_reason: str | None = None
    settlement_evidence: dict = field(default_factory=dict)
    settlement_source: str | None = None
    notes: str = ""

    def to_dict(self):
        return asdict(self)


def model_direction(model_p, mid, tol=1e-9):
    if model_p is None or mid is None:
        return "none"
    if abs(model_p - mid) <= tol:
        return "none"
    return "yes" if model_p > mid else "no"


def _band(value, bands):
    if value is None:
        return None
    for edge, label in bands:
        if value < edge:
            return label
    return bands[-1][1]


def disagreement_band(disagreement):
    """Band of |model - market|. `None` in, `None` out: an unknown disagreement is not a small one."""
    return _band(None if disagreement is None else abs(disagreement), DISAGREEMENT_BANDS)


def horizon_band(minutes_to_kickoff):
    return _band(minutes_to_kickoff, HORIZON_BANDS)


def probability_band(p, width=0.1):
    """Decile label of a probability, e.g. '0.30-0.40'. Used for the calibration curve."""
    if p is None:
        return None
    p = min(max(float(p), 0.0), 1.0)
    lo = min(int(p / width) * width, 1.0 - width)
    return f"{lo:.2f}-{lo + width:.2f}"


def close_staleness(close: dict | None, kickoff_ts=None, max_staleness_s: float = CLOSE_MAX_STALENESS_S):
    """How long before kickoff the chosen close was observed, and whether that breaches the staleness budget.

    Returns `(seconds_before_kickoff, is_stale)`. `is_stale` is None when the gap is unknown -- an unknown gap
    is reported as unknown, never as fresh.
    """
    if not close:
        return None, None
    gap = None
    if kickoff_ts is not None and close.get("observed_ts") is not None:
        gap = float(kickoff_ts) - float(close["observed_ts"])
    elif close.get("minutes_to_kickoff") is not None:
        gap = float(close["minutes_to_kickoff"]) * 60.0
    if gap is None:
        return None, None
    return gap, gap > max_staleness_s


def evaluate(pred: dict, close: dict | None, settled_yes: float | None = None, *,
             settlement=None, kickoff_ts=None, evaluation_version: str = EVALUATION_VERSION,
             close_candidates_seen: int | None = None, settlement_source: str | None = None,
             max_close_staleness_s: float = CLOSE_MAX_STALENESS_S) -> Evaluation:
    """Build the derived record. `pred` is a ledger row; `close` is the chosen pregame close, or None.

    `pred` is never mutated. `settlement` is an object exposing `status`, `settled_yes`, `kind`, `reason` and
    `evidence` (nfl_edge.settlement.settle.Settlement); when given it is the authority on `settled_yes`, so a
    caller cannot pass a payout that contradicts the proof recorded next to it.
    """
    yb, ya = pred.get("yes_bid"), pred.get("yes_ask")
    mid = (yb + ya) / 2.0 if yb is not None and ya is not None else None
    p = pred.get("model_contract_value", pred.get("model_event_probability"))
    if settlement is not None:
        settled_yes = settlement.settled_yes
    ev = Evaluation(
        prediction_id=pred["prediction_id"], run_id=pred.get("run_id"), ticker=pred.get("ticker"),
        model_version=pred.get("model_version"),
        evaluated_at=datetime.now(timezone.utc).isoformat(),
        evaluation_version=evaluation_version,
        game_id=pred.get("game_id"), season=pred.get("season"), week=pred.get("week"),
        family=pred.get("family"), period=pred.get("period"), stat=pred.get("stat"),
        threshold=pred.get("threshold"), operator=pred.get("operator"), floor_strike=pred.get("floor_strike"),
        team=pred.get("team"), player_id=pred.get("player_id"), player_name=pred.get("player_name"),
        kickoff_utc=pred.get("kickoff_utc"), support_state=pred.get("support_state"),
        calibration_version=pred.get("calibration_version"), model_artifact_sha=pred.get("model_artifact_sha"),
        observed_at=pred.get("observed_at"), minutes_to_kickoff=pred.get("minutes_to_kickoff"),
        model_p=p, model_event_probability=pred.get("model_event_probability"),
        calibrated_probability=pred.get("calibrated_probability"),
        yes_bid_t=yb, yes_ask_t=ya, no_bid_t=pred.get("no_bid"), no_ask_t=pred.get("no_ask"),
        mid_t=mid, model_direction=model_direction(p, mid),
        volume_t=pred.get("volume"), open_interest_t=pred.get("open_interest"),
        liquidity_t=pred.get("liquidity"), minutes_since_price_change_t=pred.get("minutes_since_price_change"),
        availability_state=pred.get("availability_state"), p_plays=pred.get("p_plays"),
        p_inactive=pred.get("p_inactive"),
        width_t=(ya - yb) if yb is not None and ya is not None else None,
        settled_yes=settled_yes, close_candidates_seen=close_candidates_seen,
        settlement_source=settlement_source)
    if p is not None and mid is not None:
        ev.model_market_disagreement = p - mid
        ev.disagreement_band = disagreement_band(ev.model_market_disagreement)
    ev.probability_band = probability_band(p)
    ev.horizon_band = horizon_band(ev.minutes_to_kickoff)
    if settlement is not None:
        ev.settlement_status = settlement.status
        ev.settlement_kind = settlement.kind
        ev.settlement_reason = settlement.reason
        ev.settlement_evidence = settlement.evidence
    if not close:
        ev.notes = "no valid pregame close available"
        return ev
    cb, ca = close.get("yes_bid"), close.get("yes_ask")
    if cb is None or ca is None:
        ev.close_status = CLOSE_INCOMPLETE
        ev.notes = "close quote incomplete"
        return ev
    gap_s, stale = close_staleness(close, kickoff_ts, max_close_staleness_s)
    ev.close_status = CLOSE_OK_STALE if stale else CLOSE_OK
    ev.close_is_stale = stale
    ev.close_yes_bid, ev.close_yes_ask = cb, ca
    ev.close_mid = (cb + ca) / 2.0
    ev.close_observed_at = close.get("observed_at")
    ev.close_run_id = close.get("run_id")
    ev.close_volume = close.get("volume")
    ev.close_open_interest = close.get("open_interest")
    ev.close_liquidity = close.get("liquidity")
    ev.close_minutes_to_kickoff = (gap_s / 60.0) if gap_s is not None else close.get("minutes_to_kickoff")
    ev.width_close = ca - cb
    if ev.width_t is not None:
        ev.width_change = ev.width_close - ev.width_t
    if close.get("liquidity") is not None and pred.get("liquidity") is not None:
        ev.liquidity_change = close["liquidity"] - pred["liquidity"]
    if stale:
        ev.notes = (f"close observed {ev.close_minutes_to_kickoff:.1f} min before kickoff, beyond the "
                    f"{max_close_staleness_s / 60:.0f} min staleness budget") if ev.close_minutes_to_kickoff else ""
    if mid is not None and p is not None:
        d = ev.close_mid - mid
        view = p - mid
        if abs(d) <= 1e-9:
            ev.movement = "unchanged"
        elif abs(view) <= 1e-9:
            ev.movement = "no_view"
        else:
            ev.movement = "toward" if (d > 0) == (view > 0) else "away"
        ev.signed_clv_mid = d * (1.0 if view > 0 else (-1.0 if view < 0 else 0.0))
        # executable CLV: we would have crossed at the ask (yes) or 1-bid (no); compare to the same side later
        if ev.model_direction == "yes" and ya is not None:
            ev.signed_clv_executable = ca - ya
        elif ev.model_direction == "no" and yb is not None:
            ev.signed_clv_executable = (1 - cb) - (1 - yb)
        else:
            ev.signed_clv_executable = 0.0
    return ev


def pick_close(quotes, kickoff_ts):
    """Strict pregame close: the latest complete valid quote strictly before kickoff.

    Never returns a post-kickoff quote. Returns None when no valid pregame quote exists, which the caller
    records as MISSING_CLOSE rather than filling in.
    """
    best = None
    for q in quotes:
        ts = q.get("observed_ts")
        if ts is None or kickoff_ts is None or ts >= kickoff_ts:
            continue
        if q.get("yes_bid") is None or q.get("yes_ask") is None:
            continue
        if best is None or ts > best["observed_ts"]:
            best = q
    return best


def write_evaluations(path, evals):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt") as f:
        for e in evals:
            f.write(json.dumps(e.to_dict(), separators=(",", ":")) + "\n")
    return len(evals)
