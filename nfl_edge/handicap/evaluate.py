"""Derived evaluation of recommendations. Never mutates a recommendation.

Close is established from the shadow ledger, which holds a pregame observation per market per snapshot. The
closing observation is the LAST pregame one: a post-kickoff quote is never substituted for a close, because a
price after kickoff reflects the game, not the market's pregame opinion. When no pregame snapshot exists near
kickoff the evaluation records MISSING_CLOSE as an outcome rather than reaching for the nearest number.

Three probability errors are recorded side by side -- model, market, handicapper -- because the whole point
of the ledger is to find out whose judgement, if any, adds value. They are computed identically so the
comparison is fair.

CLV is signed in the direction of the position and reported on two bases:
  clv              close mid  minus  entry mid          -- the standard, comparable across venues
  clv_executable   close mid  minus  the ask we paid    -- what the position actually cost to establish
Neither includes fees; fee-aware analysis is separate by design (see nfl_edge/execution/fees.py).
"""
from __future__ import annotations

from datetime import datetime, timezone

from nfl_edge.handicap import schema as S

MISSING_CLOSE = "MISSING_CLOSE"


def _iso(t):
    if not t:
        return None
    try:
        return datetime.fromisoformat(str(t).replace("Z", "+00:00"))
    except ValueError:
        return None


def pick_close(observations: list, kickoff) -> dict | None:
    """Last PREGAME observation for a ticker. Never a post-kickoff quote."""
    ko = _iso(kickoff)
    best = None
    for o in observations:
        ts = _iso(o.get("observed_at"))
        if ts is None:
            continue
        if ko is not None and ts >= ko:
            continue
        if o.get("mid") is None and o.get("yes_bid") is None:
            continue
        if best is None or ts > _iso(best["observed_at"]):
            best = o
    return best


def calibration_bucket(p) -> str | None:
    if p is None:
        return None
    edges = [0.0, 0.05, 0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90, 0.95, 1.0]
    for lo, hi in zip(edges, edges[1:]):
        if lo <= p < hi:
            return f"{lo:.2f}-{hi:.2f}"
    return "0.95-1.00"


def evaluate(rec: dict, observations: list, settlement: float | None = None,
             execution: dict | None = None, now=None) -> dict:
    """Build an Evaluation for one recommendation. Pure: nothing here writes or mutates."""
    now = now or datetime.now(timezone.utc)
    side = rec.get("side", "YES")
    close = pick_close(observations, rec.get("kickoff_utc"))

    ev = S.Evaluation(
        evaluation_id=S.new_evaluation_id(rec["recommendation_id"], now.isoformat()),
        schema_version=S.HANDICAP_SCHEMA_VERSION,
        recommendation_id=rec["recommendation_id"],
        evaluated_at=now.isoformat(),
        reasoning_tags=list(rec.get("reasoning_tags") or []),
        test_only=bool(rec.get("test_only")),
    )

    if close is None:
        ev.close_basis = MISSING_CLOSE
        ev.outcome = "UNSETTLED" if settlement is None else None
    else:
        ev.close_yes_bid = close.get("yes_bid")
        ev.close_yes_ask = close.get("yes_ask")
        ev.close_mid = close.get("mid")
        ev.close_basis = f"last pregame ledger observation at {close.get('observed_at')}"
        # The executable close is the price we could have TAKEN at close on our side.
        ev.closing_executable = close.get("yes_ask") if side == "YES" else close.get("no_ask")

        entry_mid = rec.get("mid")
        entry_ask = rec.get("yes_ask") if side == "YES" else rec.get("no_ask")
        close_mid_side = ev.close_mid if side == "YES" else (
            None if ev.close_mid is None else 1.0 - ev.close_mid)
        entry_mid_side = entry_mid if side == "YES" else (None if entry_mid is None else 1.0 - entry_mid)

        if close_mid_side is not None and entry_mid_side is not None:
            ev.clv = round(close_mid_side - entry_mid_side, 5)
        if close_mid_side is not None and entry_ask is not None:
            ev.clv_executable = round(close_mid_side - entry_ask, 5)

    if settlement is not None:
        ev.settlement = float(settlement)
        won = (settlement >= 0.5) if side == "YES" else (settlement < 0.5)
        ev.outcome = "WIN" if won else "LOSS"
        realised = 1.0 if won else 0.0

        def err(p):
            if p is None:
                return None
            p_side = p if side == "YES" else 1.0 - p
            return round(p_side - realised, 5)

        ev.model_probability_error = err(rec.get("model_probability"))
        ev.handicap_probability_error = err(rec.get("probability_mid"))
        ev.market_probability_error = err(rec.get("mid"))

        if execution:
            price = execution.get("actual_price")
            stake = execution.get("stake")
            if price is not None and stake:
                # Kalshi contracts pay $1. A $stake position at price p buys stake/p contracts.
                contracts = execution.get("contracts") or (stake / price if price > 0 else 0.0)
                ev.pnl = round(contracts * (1.0 - price) if won else -float(stake), 2)
    elif ev.outcome is None:
        ev.outcome = "UNSETTLED"

    ev.calibration_bucket = calibration_bucket(rec.get("probability_mid") or rec.get("model_probability"))
    return ev.to_dict()
