"""The real-money gates. The last thing between a ChatGPT decision and the canonical ledger.

`schema.validate_recommendation` checks everything derivable from the record itself. This module checks
everything that requires looking at the WORLD at the moment of import: is the price still there, is the fee
regime known, does the portfolio have room. Splitting them that way is what keeps the schema pure and
testable while still letting the write path fail closed.

    ChatGPT payload
      -> schema validation          (structural; the record is internally coherent)
      -> THESE GATES                (situational; the world still supports the decision)
      -> immutable ledger write     (recommendation + its DecisionGates record, one atomic batch)

Every gate is FAIL-CLOSED for RECOMMENDED: unknown is a failure, not a pass. A gate that cannot reach its
evidence returns UNAVAILABLE, and UNAVAILABLE blocks a real recommendation exactly as a FAIL does. The
alternative -- treating "I could not check" as "it is fine" -- is the failure mode every one of these gates
exists to prevent.

PASS, WATCHLIST and RESEARCH_ALERT are NOT gated. They cost no money, and a stale price is often precisely
the reason a contract is being passed on. Gating them would delete the record of the decision that the
staleness caused.

WHY GATES ARE THEIR OWN RECORD
------------------------------
Gate results go into a `DecisionGates` file, not into the recommendation. The recommendation must hash
identically on every replay -- the bridge's idempotency check compares canonical bytes -- and gate results
are observations made at import time, which by definition differ between replays. Keeping them separate is
what lets "identical replay is harmless" and "gates ran and passed" both be true.

Gates therefore run ONCE, when a record is first materialised. A record already durably in the ledger was
gated when it was written; re-gating it later would test today's market against yesterday's decision and
fail for entirely the wrong reason.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from nfl_edge.execution import fees as F
from nfl_edge.execution import quotes as Q
from nfl_edge.handicap import schema as S

PASS = "PASS"
FAIL = "FAIL"
UNAVAILABLE = "UNAVAILABLE"          # evidence could not be reached; blocks RECOMMENDED like a FAIL
NOT_APPLICABLE = "NOT_APPLICABLE"

BLOCKING = (FAIL, UNAVAILABLE)

# Gate names, stable so the scorecard can count them over time.
G_QUOTE_FRESHNESS = "decision_time_quote_freshness"
G_CEILING = "executable_price_within_ceiling"
G_IDENTITY = "player_identity_resolved"
G_AVAILABILITY = "player_availability_resolved"
G_NET_EV = "net_executable_ev"
G_RISK = "portfolio_risk_policy"


@dataclass
class GateResult:
    status: str
    reason: str = ""
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"status": self.status, "reason": self.reason, "evidence": self.evidence}


@dataclass
class GateReport:
    recommendation_id: str
    decision: str
    overall: str
    gates: dict = field(default_factory=dict)
    decision_quote: dict | None = None
    net_ev: dict | None = None
    risk: dict | None = None
    blocking_reasons: list = field(default_factory=list)

    def to_record(self, *, test_only: bool = False, now: datetime | None = None) -> dict:
        now = now or datetime.now(timezone.utc)
        return S.DecisionGates(
            gates_id=S.new_gates_id(self.recommendation_id),
            schema_version=S.HANDICAP_SCHEMA_VERSION,
            recommendation_id=self.recommendation_id,
            evaluated_at=now.isoformat(),
            decision=self.decision,
            overall=self.overall,
            gates={k: v.to_dict() for k, v in self.gates.items()},
            decision_quote=self.decision_quote,
            net_ev=self.net_ev,
            risk=self.risk,
            blocking_reasons=list(self.blocking_reasons),
            test_only=test_only,
        ).to_dict()


@dataclass
class GateContext:
    """Everything the gates need to look at the world. Any of it may be absent.

    Absence is not neutral: a gate whose evidence is missing returns UNAVAILABLE, which blocks a RECOMMENDED
    record. Callers that genuinely cannot supply a piece of evidence must decide to accept that consequence,
    rather than the gate deciding for them.
    """
    capture_index: Q.CaptureIndex | None = None
    fee_schedule: F.FeeSchedule | None = None
    risk_report=None                                  # nfl_edge.handicap.risk.PortfolioReport
    now: datetime | None = None
    max_quote_age_minutes: float = Q.DEFAULT_MAX_QUOTE_AGE_MIN
    execution_style: str = F.TAKER
    slippage_dollars: float = 0.0
    require_net_ev_positive: bool = False             # see evaluate_gates()


def _series_of(ticker: str | None) -> str | None:
    """Kalshi tickers are SERIES-EVENT-MARKET. The series is everything before the first hyphen."""
    if not ticker:
        return None
    return str(ticker).split("-")[0] or None


def evaluate_gates(rec: dict, ctx: GateContext) -> GateReport:
    """Run every real-money gate against one recommendation.

    `require_net_ev_positive` is OFF by default and that is a deliberate scientific position. This session
    built the primitives to MEASURE net executable EV; it did not invent a minimum-edge rule, because no
    such rule has been justified for this desk and inventing one would silently become a strategy decision
    dressed as a safety check. What the gate does unconditionally is refuse to let a trade look attractive
    while its transaction costs are unknown -- that is a data-integrity check, not a strategy.
    """
    now = ctx.now or datetime.now(timezone.utc)
    decision = rec.get("decision")
    report = GateReport(recommendation_id=rec.get("recommendation_id"), decision=decision,
                        overall=NOT_APPLICABLE)

    if decision != S.RECOMMENDED:
        # Not gated, on purpose. A PASS costs nothing and a stale price is frequently the very reason for it.
        report.gates[G_QUOTE_FRESHNESS] = GateResult(
            NOT_APPLICABLE,
            f"{decision} records are not gated on decision-time price freshness; a stale or missing quote is "
            "recorded as the reason for the decision rather than suppressing the record")
        return report

    if rec.get("test_only"):
        # A TEST_ONLY record risks no capital and is excluded from every report, so the SITUATIONAL gates do
        # not apply to it: they would make the end-to-end connectivity check depend on the live state of a
        # market the fake ticker does not have, and a flaky E2E is worse than no E2E. The STRUCTURAL checks
        # in schema.validate_recommendation still run in full, and those are the part the E2E is proving.
        report.gates[G_QUOTE_FRESHNESS] = GateResult(
            NOT_APPLICABLE,
            "TEST_ONLY record: risks no capital and is excluded from every report, so the live-market gates "
            "do not apply. Structural schema validation still ran in full.")
        return report

    side = rec.get("side", "YES")
    ticker = rec.get("market_ticker")
    series = _series_of(ticker)

    # ---- 1. decision-time executable price -------------------------------------------------------
    dq = None
    if ctx.capture_index is None:
        report.gates[G_QUOTE_FRESHNESS] = GateResult(
            UNAVAILABLE, "no capture index supplied, so the freshness of the executable price could not be "
                         "established; a RECOMMENDED record may not rest on an unverified price")
    else:
        dq = Q.resolve_decision_quote(ctx.capture_index, ticker, side, series_ticker=series, now=now,
                                      max_age_minutes=ctx.max_quote_age_minutes)
        report.decision_quote = dq.to_dict()
        if dq.is_actionable:
            report.gates[G_QUOTE_FRESHNESS] = GateResult(
                PASS, f"confirmed {dq.age_minutes:.1f} min ago ({dq.confirmation_basis})",
                {"executable_price": dq.executable_price, "confirmed_at": dq.confirmed_at,
                 "quote_moved_at": dq.quote_moved_at, "age_minutes": dq.age_minutes})
        else:
            report.gates[G_QUOTE_FRESHNESS] = GateResult(
                FAIL if dq.state in (Q.STALE, Q.NO_QUOTE) else UNAVAILABLE,
                dq.reason or f"decision-time quote state {dq.state}",
                {"state": dq.state, "age_minutes": dq.age_minutes,
                 "max_age_minutes": ctx.max_quote_age_minutes})

    # ---- 2. the decision-time price is still under the ceiling -----------------------------------
    # The schema already checked the ask RECORDED on the decision. This checks the ask that exists NOW,
    # which is the one the user would actually pay.
    ceiling = rec.get("bet_up_to_probability")
    if dq is None or dq.executable_price is None or ceiling is None:
        report.gates[G_CEILING] = GateResult(
            UNAVAILABLE, "no confirmed decision-time executable price to compare against the ceiling")
    elif float(dq.executable_price) > float(ceiling) + 1e-9:
        report.gates[G_CEILING] = GateResult(
            FAIL,
            f"the live {side} ask {dq.executable_price} is ABOVE bet_up_to_probability {ceiling}; the "
            "position is not available at the price this record authorises",
            {"executable_price": dq.executable_price, "bet_up_to_probability": ceiling})
    else:
        report.gates[G_CEILING] = GateResult(
            PASS, f"live {side} ask {dq.executable_price} <= ceiling {ceiling}",
            {"executable_price": dq.executable_price, "bet_up_to_probability": ceiling,
             "headroom": round(float(ceiling) - float(dq.executable_price), 6)})

    # ---- 3. player identity ----------------------------------------------------------------------
    support = rec.get("support_state")
    if rec.get("market_family") not in S.PLAYER_MARKET_FAMILIES:
        report.gates[G_IDENTITY] = GateResult(NOT_APPLICABLE, "not a player market")
    elif support == S.SUPPORT_UNSUPPORTED_IDENTITY:
        report.gates[G_IDENTITY] = GateResult(
            FAIL, "the Kalshi player id is not resolved to a GSIS id; we do not know whose statistics were "
                  "priced. Coverage is never traded for identity integrity.")
    elif support == S.SUPPORT_SUPPORTED and not rec.get("player_id"):
        report.gates[G_IDENTITY] = GateResult(
            FAIL, "support_state SUPPORTED on a player market with no resolved player_id: the record claims "
                  "a quantitative price for a player it cannot name")
    else:
        report.gates[G_IDENTITY] = GateResult(PASS, f"support_state {support}",
                                              {"player_id": rec.get("player_id")})

    # ---- 4. availability -------------------------------------------------------------------------
    # The hard states are enforced in the schema so they cannot be bypassed by writing a record directly.
    # Repeating the verdict here records WHAT WAS SEEN, which the schema's exception does not preserve.
    if rec.get("market_family") not in S.PLAYER_MARKET_FAMILIES:
        report.gates[G_AVAILABILITY] = GateResult(NOT_APPLICABLE, "not a player market")
    else:
        av, stale = rec.get("availability_state"), rec.get("availability_stale_minutes")
        if av is None:
            report.gates[G_AVAILABILITY] = GateResult(
                UNAVAILABLE, "no availability_state recorded for a player market")
        elif stale is not None and float(stale) > S.MAX_AVAILABILITY_STALE_MIN:
            report.gates[G_AVAILABILITY] = GateResult(
                FAIL, f"availability is {float(stale):.0f} min old, beyond "
                      f"{S.MAX_AVAILABILITY_STALE_MIN:.0f} min")
        else:
            report.gates[G_AVAILABILITY] = GateResult(
                PASS, f"availability {av}",
                {"state": av, "as_of": rec.get("availability_as_of"), "stale_minutes": stale})

    # ---- 5. transaction costs --------------------------------------------------------------------
    fair = rec.get("probability_mid")
    price = dq.executable_price if dq is not None and dq.executable_price is not None else None
    if ctx.fee_schedule is None:
        report.gates[G_NET_EV] = GateResult(
            UNAVAILABLE, "no fee schedule supplied; a recommendation may not be recorded as attractive while "
                         "its transaction costs are unmodelled")
    elif fair is None or price is None:
        report.gates[G_NET_EV] = GateResult(
            UNAVAILABLE, "net executable EV needs both a handicap probability and a confirmed executable "
                         "price; one of them is missing")
    else:
        stake = rec.get("recommended_stake") or 0
        contracts = F.contracts_for_stake(float(stake), float(price))
        nev = F.net_executable_ev(float(fair), float(price), contracts, ctx.fee_schedule,
                                  series_ticker=series, execution_style=ctx.execution_style,
                                  slippage_dollars=ctx.slippage_dollars)
        report.net_ev = nev.to_dict()
        if not nev.is_known:
            report.gates[G_NET_EV] = GateResult(
                FAIL,
                f"transaction costs are {nev.fee_state} for this market ({nev.reason}). A trade whose cost "
                "is unknown cannot be shown to survive its costs, and an unknown cost is never treated as "
                "zero.",
                {"fee_state": nev.fee_state, "gross_edge": nev.gross_edge})
        elif ctx.require_net_ev_positive and nev.net_ev_dollars is not None and nev.net_ev_dollars <= 0:
            report.gates[G_NET_EV] = GateResult(
                FAIL,
                f"gross edge {nev.gross_edge:+.4f} is erased by ${nev.estimated_fees:.2f} of estimated fees "
                f"and ${nev.estimated_slippage_dollars:.2f} of slippage; net EV is "
                f"${nev.net_ev_dollars:+.2f}",
                {k: nev.to_dict()[k] for k in ("gross_edge", "gross_ev_dollars", "estimated_fees",
                                               "net_ev_dollars", "net_edge")})
        else:
            report.gates[G_NET_EV] = GateResult(
                PASS,
                f"gross edge {nev.gross_edge:+.4f}, estimated fees ${nev.estimated_fees:.2f}, net EV "
                f"${nev.net_ev_dollars:+.2f}"
                + ("" if ctx.require_net_ev_positive else
                   " (measured and recorded; no minimum-edge rule is enforced -- see module docstring)"),
                {k: nev.to_dict()[k] for k in ("gross_edge", "gross_ev_dollars", "estimated_fees",
                                               "estimated_slippage_dollars", "net_ev_dollars", "net_edge",
                                               "fee_state")})

    # ---- 6. portfolio risk -----------------------------------------------------------------------
    if ctx.risk_report is None:
        report.gates[G_RISK] = GateResult(
            UNAVAILABLE, "no portfolio risk report supplied; aggregate game and correlation-group exposure "
                         "could not be checked")
    else:
        v = ctx.risk_report.verdict_for(rec.get("recommendation_id"))
        report.risk = v.to_dict() if v is not None else None
        if v is None:
            report.gates[G_RISK] = GateResult(
                UNAVAILABLE, "the risk policy produced no verdict for this recommendation")
        elif not v.is_actionable:
            report.gates[G_RISK] = GateResult(
                FAIL, f"rejected by the risk policy ({v.binding_limit}): " + "; ".join(v.reasons),
                {"proposed_stake": v.proposed_stake, "approved_stake": v.approved_stake})
        elif abs(v.approved_stake - float(rec.get("recommended_stake") or 0)) > 1e-9:
            report.gates[G_RISK] = GateResult(
                FAIL,
                f"recommended_stake {rec.get('recommended_stake')} does not match the stake the risk policy "
                f"approved ({v.approved_stake:.2f}); the record must carry the approved size, not the "
                "proposed one",
                {"proposed_stake": v.proposed_stake, "approved_stake": v.approved_stake})
        else:
            report.gates[G_RISK] = GateResult(
                v.status if v.status == "APPROVED" else PASS,
                f"{v.status} at ${v.approved_stake:.2f}" + (f" ({v.binding_limit})" if v.binding_limit
                                                            else ""),
                {"proposed_stake": v.proposed_stake, "approved_stake": v.approved_stake,
                 "status": v.status})
            report.gates[G_RISK].status = PASS

    report.blocking_reasons = [f"{name}: {g.reason}" for name, g in report.gates.items()
                               if g.status in BLOCKING]
    report.overall = FAIL if report.blocking_reasons else PASS
    return report
