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
    gross_pnl            contract payoff minus cost, before fees. Says whether the CALL was right.
    fees_paid            what the venue actually charged, summed over fills.
    net_pnl              gross_pnl - fees. Says whether the BANKROLL grew.
    estimated_net_pnl    gross_pnl - modelled fees. A forecast, and labelled one.

Gross P/L is always computable from observed fills and settlement: nothing about it depends on knowing what
the trade cost. NET P/L is a different claim, and it is only true when the costs are actually known.

So `net_pnl` is numeric ONLY when every counted fill carries an OBSERVED venue fee. Anything less --
no fee data, modelled fees, one of two fills missing its charge -- and `net_pnl` and `net_roi` are None.
Not zero, and not "gross minus whatever fees happened to be supplied": subtracting the fees you have from a
position whose other fills you have not reconciled produces a number that looks realised and is not.

The modelled figure still exists, under a name that cannot be mistaken for accounting: `estimated_net_pnl`,
computed from every fee present, actual or modelled, and defined only when NO fill is missing a fee
altogether. When the reconciliation later completes, `net_pnl` becomes numeric on the next evaluation --
nothing has to be corrected, because nothing false was written.

`fees_basis` says which of those worlds the record is in (ACTUAL / ESTIMATED / MIXED / INCOMPLETE / NONE)
and the coverage fields say it in numbers: `fills_total`, `fills_with_actual_fees`, `missing_fee_count`,
`actual_fee_coverage`.
"""
from __future__ import annotations

from datetime import datetime, timezone

from nfl_edge.handicap import schema as S

MISSING_CLOSE = "MISSING_CLOSE"

FEES_ACTUAL = "ACTUAL"           # every counted fill carries an observed venue charge
FEES_ESTIMATED = "ESTIMATED"     # every counted fill carries a modelled fee, none observed
FEES_MIXED = "MIXED"             # some observed, some modelled, none missing
FEES_INCOMPLETE = "INCOMPLETE"   # at least one counted fill carries no fee of any kind, and at least one does
FEES_NONE = "NONE"               # no fee information at all
FEES_BASES = (FEES_ACTUAL, FEES_ESTIMATED, FEES_MIXED, FEES_INCOMPLETE, FEES_NONE)


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


def aggregate_executions(executions: list, won: bool | None = None, *,
                         settlement_fee_per_contract: float | None = None) -> dict:
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

    `settlement_fee_per_contract` is what the fee schedule in force says the venue charges at settlement. It
    defaults to None, meaning "not asserted". When it is a positive number, an observed settlement charge is
    REQUIRED on a settled position before `net_pnl` may be numeric -- a cost the schedule says exists and the
    ledger has not seen is exactly the kind of gap that turns a realised number into a guess. Kalshi charges
    none on these markets today, which is recorded in config/kalshi_fee_schedule.json rather than assumed
    here.
    """
    total_stake = total_contracts = 0.0
    fees_actual = fees_estimated = settlement_actual = 0.0
    n_actual = n_estimated = n_settlement = 0
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

        # A venue-reported settlement or fixed-point rounding adjustment, when one is reported. Preserved
        # and reconciled; never manufactured.
        sf = ex.get("settlement_fee")
        if sf is not None:
            settlement_actual += float(sf)
            n_settlement += 1

    missing = counted - n_actual - n_estimated
    if counted == 0 or missing == counted:
        basis = FEES_NONE
    elif missing > 0:
        basis = FEES_INCOMPLETE
    elif n_actual == counted:
        basis = FEES_ACTUAL
    elif n_estimated == counted:
        basis = FEES_ESTIMATED
    else:
        basis = FEES_MIXED

    # The one question that decides whether a NET number may exist: is every counted fill's cost observed?
    settlement_owed = (settlement_fee_per_contract is not None
                       and float(settlement_fee_per_contract) > 0)
    settlement_observed = (not settlement_owed) or (won is None) or n_settlement == counted
    complete = counted > 0 and n_actual == counted and settlement_observed

    if counted == 0:
        gap = "no executions carry a price, so there is nothing to reconcile"
    elif complete:
        gap = None
    elif missing > 0:
        gap = f"{missing} of {counted} fill(s) carry no fee of any kind"
    elif n_actual < counted:
        gap = (f"{counted - n_actual} of {counted} fill(s) carry a MODELLED fee; a modelled cost cannot "
               "produce a realised net")
    else:
        gap = (f"the fee schedule charges {settlement_fee_per_contract} per contract at settlement and "
               f"only {n_settlement} of {counted} fill(s) report one")

    out = {
        "n_executions": counted,
        "gross_dollars_staked": round(total_stake, 2),
        "contracts": round(total_contracts, 6),
        # DERIVED. A stake-weighted average of real fills -- not a fill anybody made.
        "average_execution_price": (round(total_stake / total_contracts, 6)
                                    if total_contracts > 0 else None),
        "fees_paid": round(fees_actual, 4) if n_actual else None,
        "fees_estimated": round(fees_estimated, 4) if n_estimated else None,
        "settlement_fees_paid": round(settlement_actual, 4) if n_settlement else None,
        "fees_basis": basis,
        # Completeness, in numbers rather than adjectives, so a reader can check the verdict below.
        "fills_total": counted,
        "fills_with_actual_fees": n_actual,
        "fills_with_estimated_fees": n_estimated,
        "missing_fee_count": max(missing, 0),
        "actual_fee_coverage": round(n_actual / counted, 6) if counted else None,
        "fee_coverage_complete": complete,
        "fee_coverage_gap": gap,
    }
    if won is None:
        out.update({"gross_pnl": None, "net_pnl": None, "net_roi": None,
                    "estimated_net_pnl": None, "estimated_net_roi": None})
        return out

    out["gross_pnl"] = round(gross, 2)

    # ACTUAL net: only when every cost is observed. Subtracting the fees that happen to be present from a
    # position whose other fills are unreconciled yields a number that reads as realised and is not one.
    if complete:
        out["net_pnl"] = round(gross - fees_actual - settlement_actual, 2)
        out["net_roi"] = round(out["net_pnl"] / total_stake, 6) if total_stake > 0 else None
    else:
        out["net_pnl"] = None
        out["net_roi"] = None

    # ESTIMATED net: every fee present, actual or modelled. Defined only when no fill is missing a fee
    # altogether, because otherwise it is not an estimate of the whole position either.
    if counted > 0 and missing == 0:
        est = round(gross - fees_actual - fees_estimated - settlement_actual, 2)
        out["estimated_net_pnl"] = est
        out["estimated_net_roi"] = round(est / total_stake, 6) if total_stake > 0 else None
    else:
        out["estimated_net_pnl"] = None
        out["estimated_net_roi"] = None
    return out


def evaluate(rec: dict, observations: list, settlement: float | None = None,
             executions: list | None = None, now=None, execution: dict | None = None,
             *, settlement_fee_per_contract: float | None = None) -> dict:
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

    agg = aggregate_executions(executions, won=won,
                               settlement_fee_per_contract=settlement_fee_per_contract)
    ev.n_executions = agg["n_executions"]
    ev.gross_dollars_staked = agg["gross_dollars_staked"] or None
    ev.contracts = agg["contracts"] or None
    ev.average_execution_price = agg["average_execution_price"]
    ev.fees_paid = agg["fees_paid"]
    ev.fees_estimated = agg["fees_estimated"]
    ev.settlement_fees_paid = agg["settlement_fees_paid"]
    ev.fees_basis = agg["fees_basis"]
    ev.fills_total = agg["fills_total"]
    ev.fills_with_actual_fees = agg["fills_with_actual_fees"]
    ev.fills_with_estimated_fees = agg["fills_with_estimated_fees"]
    ev.missing_fee_count = agg["missing_fee_count"]
    ev.actual_fee_coverage = agg["actual_fee_coverage"]
    ev.fee_coverage_complete = agg["fee_coverage_complete"]
    ev.fee_coverage_gap = agg["fee_coverage_gap"]
    ev.gross_pnl = agg["gross_pnl"]
    ev.net_pnl = agg["net_pnl"]
    ev.net_roi = agg["net_roi"]
    ev.estimated_net_pnl = agg["estimated_net_pnl"]
    ev.estimated_net_roi = agg["estimated_net_roi"]
    # `pnl` is the pre-1.1.0 name, kept as an exact alias of gross_pnl so no existing reader silently
    # changes meaning underneath it. New readers use the explicit names.
    ev.pnl = agg["gross_pnl"]

    # Entry slippage: what we actually paid on average, against the ask the recommendation was written at.
    # Positive means we paid up. Undefined without both numbers, and never assumed to be zero.
    if agg["average_execution_price"] is not None and entry_ask is not None:
        ev.entry_slippage = round(agg["average_execution_price"] - float(entry_ask), 6)

    ev.calibration_bucket = calibration_bucket(rec.get("probability_mid") or rec.get("model_probability"))
    return ev.to_dict()
