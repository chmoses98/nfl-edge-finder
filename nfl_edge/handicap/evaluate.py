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
Neither includes fees. That is deliberate and permanent: CLV asks "did the market move toward me?" and
transaction costs ask "did the bankroll grow?". They are different questions, and merging them makes both
unanswerable. Fees appear in `net_pnl` -- never in CLV, and never in the recommendation's recorded price.

MULTIPLE FILLS
--------------
A recommendation is routinely filled in pieces at different prices:

    BUY YES up to 58%   ->   $20 at 54%   and   $30 at 55%

Every fill is its own immutable Execution record, and economics are computed PER FILL and then summed. This
module never takes "the" execution and never invents a single blended fill price to stand in for two real
ones. A stake-weighted average price IS computed, because it is genuinely useful for slippage, and it is
stored as `average_execution_price` and named DERIVED so it cannot be mistaken for a price the venue
reported.

GROSS AND NET
-------------
    gross_pnl   contract payoff minus cost, before fees. Says whether the CALL was right.
    fees_paid   what the venue actually charged, summed over fills.
    net_pnl     gross_pnl - fees. Says whether the BANKROLL grew.

`fees_basis` records whether those fees were observed or modelled. A modelled fee is a fine input to an
estimate and an unacceptable input to a realised-P/L claim, so an ESTIMATED or MIXED basis is carried on the
record rather than smoothed away -- and only fees the venue actually charged ever reduce `net_pnl`.
"""
from __future__ import annotations

from datetime import datetime, timezone

from nfl_edge.handicap import schema as S

MISSING_CLOSE = "MISSING_CLOSE"

FEES_ACTUAL = "ACTUAL"
FEES_ESTIMATED = "ESTIMATED"
FEES_MIXED = "MIXED"
FEES_NONE = "NONE"


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


def _contracts_of(ex: dict) -> float:
    """Contracts on one fill. Explicit when recorded, else derived from stake and price.

    A Kalshi contract pays $1, so a $stake position at price p is stake/p contracts. The explicit field wins,
    because a venue-reported quantity is evidence and a derivation is only arithmetic.
    """
    c = ex.get("contracts")
    if c is not None:
        try:
            return float(c)
        except (TypeError, ValueError):
            pass
    price, stake = ex.get("actual_price"), ex.get("stake")
    if price and stake and float(price) > 0:
        return float(stake) / float(price)
    return 0.0


def aggregate_executions(executions: list, won: bool | None = None) -> dict:
    """Fill-level economics, summed to the recommendation.

    Each fill contributes independently:

        cost      contracts * price          (== stake)
        payoff    contracts * $1 on a win, $0 on a loss
        gross     payoff - cost

    which for a win is `contracts * (1 - price)` and for a loss is `-stake`. Doing this per fill is what
    makes two fills at different prices come out right; a single blended price would be correct only by
    coincidence, and only for the total.

    `won=None` means the market has not settled. Staked, contracts and fees are still real and are returned;
    every P/L field stays None rather than being reported as a zero that reads like a measurement.
    """
    total_stake = total_contracts = 0.0
    fees_actual = fees_estimated = 0.0
    n_actual = n_estimated = 0
    gross = 0.0
    counted = 0

    for ex in executions or []:
        price = ex.get("actual_price")
        if price is None:
            continue
        counted += 1
        contracts = _contracts_of(ex)
        stake = ex.get("stake")
        stake = float(stake) if stake is not None else contracts * float(price)
        total_stake += stake
        total_contracts += contracts
        if won is not None:
            gross += (contracts * (1.0 - float(price))) if won else -stake

        fee = ex.get("fees_paid")
        if fee is not None:
            if ex.get("fees_are_estimated"):
                fees_estimated += float(fee)
                n_estimated += 1
            else:
                fees_actual += float(fee)
                n_actual += 1

    if n_actual and n_estimated:
        basis = FEES_MIXED
    elif n_actual:
        basis = FEES_ACTUAL
    elif n_estimated:
        basis = FEES_ESTIMATED
    else:
        basis = FEES_NONE

    out = {
        "n_executions": counted,
        "gross_dollars_staked": round(total_stake, 2),
        "contracts": round(total_contracts, 6),
        # DERIVED. A stake-weighted average of real fills -- not a fill anybody made.
        "average_execution_price": (round(total_stake / total_contracts, 6)
                                    if total_contracts > 0 else None),
        "fees_paid": round(fees_actual, 4) if n_actual else None,
        "fees_estimated": round(fees_estimated, 4) if n_estimated else None,
        "fees_basis": basis,
    }
    if won is None:
        out.update({"gross_pnl": None, "net_pnl": None, "net_roi": None})
        return out

    # Only fees the venue actually charged reduce realised P/L. An estimate is carried alongside so the gap
    # between modelled and charged stays measurable, but it never silently becomes a realised number.
    charged = fees_actual if n_actual else 0.0
    out["gross_pnl"] = round(gross, 2)
    out["net_pnl"] = round(gross - charged, 2)
    out["net_roi"] = round(out["net_pnl"] / total_stake, 6) if total_stake > 0 else None
    return out


def evaluate(rec: dict, observations: list, settlement: float | None = None,
             executions: list | None = None, now=None, execution: dict | None = None) -> dict:
    """Build an Evaluation for one recommendation. Pure: nothing here writes or mutates.

    `executions` is EVERY fill on this recommendation. The singular `execution` argument is accepted for
    callers that only ever had one; passing both raises rather than silently picking, because guessing which
    one the caller meant is exactly how a fill goes missing from the accounting.
    """
    if execution is not None:
        if executions is not None:
            raise ValueError("pass `executions` (all fills) or the legacy `execution` (one fill), not both")
        executions = [execution]
    executions = [e for e in (executions or []) if e]

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

    entry_ask = rec.get("yes_ask") if side == "YES" else rec.get("no_ask")

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
        close_mid_side = ev.close_mid if side == "YES" else (
            None if ev.close_mid is None else 1.0 - ev.close_mid)
        entry_mid_side = entry_mid if side == "YES" else (None if entry_mid is None else 1.0 - entry_mid)

        if close_mid_side is not None and entry_mid_side is not None:
            ev.clv = round(close_mid_side - entry_mid_side, 5)
        if close_mid_side is not None and entry_ask is not None:
            ev.clv_executable = round(close_mid_side - entry_ask, 5)

    won = None
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
    elif ev.outcome is None:
        ev.outcome = "UNSETTLED"

    agg = aggregate_executions(executions, won=won)
    ev.n_executions = agg["n_executions"]
    ev.gross_dollars_staked = agg["gross_dollars_staked"] or None
    ev.contracts = agg["contracts"] or None
    ev.average_execution_price = agg["average_execution_price"]
    ev.fees_paid = agg["fees_paid"]
    ev.fees_estimated = agg["fees_estimated"]
    ev.fees_basis = agg["fees_basis"]
    ev.gross_pnl = agg["gross_pnl"]
    ev.net_pnl = agg["net_pnl"]
    ev.net_roi = agg["net_roi"]
    # `pnl` is the pre-1.1.0 name, kept as an exact alias of gross_pnl so no existing reader silently
    # changes meaning underneath it. New readers use the explicit names.
    ev.pnl = agg["gross_pnl"]

    # Entry slippage: what we actually paid on average, against the ask the recommendation was written at.
    # Positive means we paid up. Undefined without both numbers, and never assumed to be zero.
    if agg["average_execution_price"] is not None and entry_ask is not None:
        ev.entry_slippage = round(agg["average_execution_price"] - float(entry_ask), 6)

    ev.calibration_bucket = calibration_bucket(rec.get("probability_mid") or rec.get("model_probability"))
    return ev.to_dict()
