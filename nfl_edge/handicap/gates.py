"""The real-money gates. The last thing between a ChatGPT decision and the canonical ledger.

`schema.validate_recommendation` checks everything derivable from the record itself. This module checks
everything that requires looking at the WORLD -- but at the world AS IT WAS WHEN THE DECISION WAS MADE.

    ChatGPT payload
      -> schema validation          (structural; the record is internally coherent)
      -> THESE GATES                (situational; the world AT THE DECISION supported it)
      -> immutable ledger write     (recommendation + its DecisionGates record, one atomic batch)

THE CLOCK IS THE DECISION, NOT THE IMPORT
-----------------------------------------
The Airtable bridge is retrospective archival transport running every twelve hours. GitHub ingestion is when
a decision is FILED, not when it is MADE. So every time-sensitive gate here is evaluated `as_of` the
recommendation's own `created_at`, and never at wall clock:

    13:00   decision made, market ask 0.56, recorded
    01:00   importer runs. Game has kicked off; the ask is gone; the book is closed.

Judged at 01:00 that recommendation fails everything, which answers a question nobody asked. Judged at 13:00
it either was or was not a sound call, and that verdict does not change with how long the importer took.

Two rules follow, and they are enforced in the resolvers rather than trusted here:

  * Evidence AFTER the decision is INVISIBLE. A capture taken later is information the handicapper did not
    have; letting it validate the decision would rescue a bet that was stale when it was made.
  * Freshness is measured BACKWARDS from the decision. Import latency cannot change the verdict.

`created_at` is the decision timestamp. Airtable's server-stamped `createdTime` stays what it always was --
independent proof the decision had been handed off by then, and the anti-backfill bound. Those are different
jobs and `airtable_bridge.check_timestamps` still does the second one.

Only the RISK gate is evaluated at import time, and only because it is deterministic from the frozen batch,
the recorded bankroll snapshot and the versioned policy file. It reads no market state, so there is nothing
for latency to change.

FAIL CLOSED
-----------
Every gate blocks RECOMMENDED on anything but a pass. A gate that cannot reach its evidence returns
UNAVAILABLE, and UNAVAILABLE blocks exactly as FAIL does: treating "I could not check" as "it is fine" is
the failure mode all of this exists to prevent.

PASS, WATCHLIST and RESEARCH_ALERT are NOT gated. They cost no money, and a stale price is often precisely
the reason a contract is being passed on.

WHY GATES ARE THEIR OWN RECORD
------------------------------
Gate results go into a `DecisionGates` file, not into the recommendation. The recommendation must hash
identically on every replay -- the bridge's idempotency check compares canonical bytes -- and gate results
are observations made at import time about the decision time. Keeping them separate is what lets "identical
replay is harmless" and "gates ran and passed" both be true.

Gates run ONCE, when a record is first materialised.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from nfl_edge.execution import depth as D
from nfl_edge.execution import fees as F
from nfl_edge.execution import quotes as Q
from nfl_edge.handicap import schema as S

PASS = "PASS"
FAIL = "FAIL"
UNAVAILABLE = "UNAVAILABLE"          # evidence could not be reached; blocks RECOMMENDED like a FAIL
NOT_APPLICABLE = "NOT_APPLICABLE"

BLOCKING = (FAIL, UNAVAILABLE)

# Gate names, stable so the scorecard can count them over time.
G_DECISION_TIME = "decision_timestamp_resolved"
G_QUOTE_FRESHNESS = "decision_time_quote_freshness"
G_CEILING = "executable_price_within_ceiling"
G_IDENTITY = "player_identity_resolved"
G_AVAILABILITY = "player_availability_resolved"
G_DEPTH = "full_position_executable"
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
    depth: dict | None = None
    net_ev: dict | None = None
    risk: dict | None = None
    as_of: str | None = None
    blocking_reasons: list = field(default_factory=list)
    # Things the operator should see that are NOT blockers. Kept strictly apart from blocking_reasons: a
    # warning list that can block, or a blocker list that contains advice, makes both unreadable.
    warnings: list = field(default_factory=list)

    def to_record(self, *, test_only: bool = False, now: datetime | None = None) -> dict:
        now = now or datetime.now(timezone.utc)
        return S.DecisionGates(
            gates_id=S.new_gates_id(self.recommendation_id),
            schema_version=S.HANDICAP_SCHEMA_VERSION,
            recommendation_id=self.recommendation_id,
            evaluated_at=now.isoformat(),
            decision_as_of=self.as_of,
            decision=self.decision,
            overall=self.overall,
            gates={k: v.to_dict() for k, v in self.gates.items()},
            decision_quote=self.decision_quote,
            depth=self.depth,
            net_ev=self.net_ev,
            risk=self.risk,
            blocking_reasons=list(self.blocking_reasons),
            warnings=list(self.warnings),
            test_only=test_only,
        ).to_dict()


@dataclass
class GateContext:
    """Everything the gates need to look at the world as it was at the decision.

    Note what is NOT here: a `now`. There is no wall-clock input, because there is no gate that should
    consult one. The clock comes from each record's own `created_at`.
    """
    capture_index: Q.CaptureIndex | None = None
    book_index: D.BookIndex | None = None
    fee_schedule: F.FeeSchedule | None = None
    risk_report=None                                  # nfl_edge.handicap.risk.PortfolioReport
    max_quote_age_minutes: float = Q.DEFAULT_MAX_QUOTE_AGE_MIN
    max_book_age_minutes: float = D.DEFAULT_MAX_BOOK_AGE_MIN
    execution_style: str = F.TAKER
    direct_member: bool = False


def _series_of(ticker: str | None) -> str | None:
    """Kalshi tickers are SERIES-EVENT-MARKET. The series is everything before the first hyphen."""
    if not ticker:
        return None
    return str(ticker).split("-")[0] or None


def _decision_time(rec: dict) -> tuple[datetime | None, str | None]:
    raw = rec.get("created_at")
    if not raw:
        return None, "the record carries no created_at, so there is no decision time to evaluate it at"
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None, f"created_at {raw!r} is not an ISO-8601 timestamp"
    if dt.tzinfo is None:
        return None, f"created_at {raw!r} has no timezone; use UTC with an explicit offset"
    return dt.astimezone(timezone.utc), None


def evaluate_gates(rec: dict, ctx: GateContext) -> GateReport:
    """Run every real-money gate against one recommendation, as of its own decision timestamp."""
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
        # not apply: they would make the end-to-end connectivity check depend on the market state of a
        # ticker that does not exist, and a flaky E2E is worse than no E2E. The STRUCTURAL checks in
        # schema.validate_recommendation still run in full, and those are what the E2E is proving.
        report.gates[G_QUOTE_FRESHNESS] = GateResult(
            NOT_APPLICABLE,
            "TEST_ONLY record: risks no capital and is excluded from every report, so the live-market gates "
            "do not apply. Structural schema validation still ran in full.")
        return report

    as_of, ts_problem = _decision_time(rec)
    if as_of is None:
        report.gates[G_DECISION_TIME] = GateResult(UNAVAILABLE, ts_problem)
        report.blocking_reasons = [f"{G_DECISION_TIME}: {ts_problem}"]
        report.overall = FAIL
        return report
    report.as_of = as_of.isoformat()
    report.gates[G_DECISION_TIME] = GateResult(
        PASS, f"every market gate below is evaluated as of {as_of.isoformat()}, the decision timestamp -- "
              "not the import time", {"as_of": as_of.isoformat()})

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
        dq = Q.resolve_decision_quote(ctx.capture_index, ticker, side, series_ticker=series, as_of=as_of,
                                      max_age_minutes=ctx.max_quote_age_minutes)
        report.decision_quote = dq.to_dict()
        if dq.is_actionable:
            report.gates[G_QUOTE_FRESHNESS] = GateResult(
                PASS, f"confirmed {dq.age_minutes:.1f} min before the decision ({dq.confirmation_basis})",
                {"executable_price": dq.executable_price, "confirmed_at": dq.confirmed_at,
                 "quote_moved_at": dq.quote_moved_at, "age_minutes": dq.age_minutes,
                 "as_of": dq.as_of})
        else:
            report.gates[G_QUOTE_FRESHNESS] = GateResult(
                FAIL if dq.state in (Q.STALE, Q.NO_QUOTE) else UNAVAILABLE,
                dq.reason or f"decision-time quote state {dq.state}",
                {"state": dq.state, "age_minutes": dq.age_minutes,
                 "max_age_minutes": ctx.max_quote_age_minutes, "as_of": dq.as_of})

    # ---- 2. the decision-time price was under the ceiling ----------------------------------------
    ceiling = rec.get("bet_up_to_probability")
    if dq is None or dq.executable_price is None or ceiling is None:
        report.gates[G_CEILING] = GateResult(
            UNAVAILABLE, "no confirmed decision-time executable price to compare against the ceiling")
    elif float(dq.executable_price) > float(ceiling) + 1e-9:
        report.gates[G_CEILING] = GateResult(
            FAIL,
            f"at the decision the {side} ask was {dq.executable_price}, ABOVE bet_up_to_probability "
            f"{ceiling}; the position was not available at the price this record authorises",
            {"executable_price": dq.executable_price, "bet_up_to_probability": ceiling})
    else:
        report.gates[G_CEILING] = GateResult(
            PASS, f"{side} ask {dq.executable_price} <= ceiling {ceiling} at the decision",
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
        report.gates[G_AVAILABILITY] = _availability_gate(rec, as_of)

    # ---- 5. full-position executability ----------------------------------------------------------
    stake = rec.get("recommended_stake")
    dr = None
    if ctx.book_index is None:
        report.gates[G_DEPTH] = GateResult(
            UNAVAILABLE, "no order-book index supplied, so the approved stake could not be shown to be "
                         "executable; top-of-book is not evidence that a position fills at that price")
    elif not stake:
        report.gates[G_DEPTH] = GateResult(UNAVAILABLE, "no recommended_stake to size the book walk against")
    else:
        dr = D.resolve_full_position(ctx.book_index, ticker, side, float(stake), as_of=as_of,
                                     bet_up_to=ceiling, max_age_minutes=ctx.max_book_age_minutes)
        report.depth = dr.to_dict()
        if dr.is_executable:
            report.gates[G_DEPTH] = GateResult(
                PASS,
                f"${float(stake):.2f} fills from observed liquidity at a VWAP of {dr.vwap} "
                f"(top ask {dr.top_ask}, worst {dr.worst_price}, slippage "
                f"${dr.slippage_dollars:.4f})",
                {"top_ask": dr.top_ask, "vwap": dr.vwap, "worst_price": dr.worst_price,
                 "contracts_required": dr.contracts_required,
                 "slippage_dollars": dr.slippage_dollars,
                 "book_observed_at": dr.book_observed_at})
        else:
            report.gates[G_DEPTH] = GateResult(
                FAIL if dr.state in (D.INSUFFICIENT_DEPTH, D.STALE_BOOK) else UNAVAILABLE,
                dr.reason or f"depth state {dr.state}",
                {"state": dr.state, "top_ask": dr.top_ask, "fillable_stake": dr.fillable_stake,
                 "book_age_minutes": dr.book_age_minutes})

    # ---- 6. transaction costs, on the FULL position ----------------------------------------------
    report.gates[G_NET_EV] = _net_ev_gate(rec, ctx, report, dq, dr, series, as_of)

    # ---- 7. portfolio risk -----------------------------------------------------------------------
    report.gates[G_RISK] = _risk_gate(rec, ctx, report)

    report.blocking_reasons = [f"{name}: {g.reason}" for name, g in report.gates.items()
                               if g.status in BLOCKING]
    report.overall = FAIL if report.blocking_reasons else PASS
    return report


def _availability_gate(rec: dict, as_of: datetime) -> GateResult:
    av, stale = rec.get("availability_state"), rec.get("availability_stale_minutes")
    if av is None:
        return GateResult(UNAVAILABLE, "no availability_state recorded for a player market")
    if stale is not None and float(stale) > S.MAX_AVAILABILITY_STALE_MIN:
        return GateResult(
            FAIL, f"availability was {float(stale):.0f} min old at the decision, beyond "
                  f"{S.MAX_AVAILABILITY_STALE_MIN:.0f} min")
    # The availability snapshot must itself predate the decision -- an availability read AFTER the call was
    # made is not what the call was based on.
    seen = rec.get("availability_as_of")
    if seen:
        try:
            t = datetime.fromisoformat(str(seen).replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            if t > as_of:
                return GateResult(
                    FAIL, f"availability_as_of {t.isoformat()} is AFTER the decision {as_of.isoformat()}; "
                          "the record cites information that did not exist when the call was made")
        except (ValueError, TypeError):
            return GateResult(UNAVAILABLE, f"availability_as_of {seen!r} is not an ISO-8601 timestamp")
    return GateResult(PASS, f"availability {av}",
                      {"state": av, "as_of": seen, "stale_minutes": stale})


def _net_ev_gate(rec, ctx, report, dq, dr, series, as_of) -> GateResult:
    """Net executable EV on the full approved position. Zero or below BLOCKS.

    This is not a minimum-edge rule and does not become one. There is a real difference between

        "require at least +3% edge"                                   -- a strategy threshold
        "do not knowingly record a trade worth <= $0 after its costs" -- arithmetic

    Only the second is enforced. No positive minimum beyond zero is invented here; any buffer is a separately
    authorised strategy decision, and there is deliberately no switch in this module to turn one on.

    The EV is computed at the full-position VWAP where the book is observable, because the VWAP is what the
    position actually costs. Falling back to the top ask would price the trade at its cheapest contract.
    """
    fair = rec.get("probability_mid")
    if ctx.fee_schedule is None:
        return GateResult(
            UNAVAILABLE, "no fee schedule supplied; a recommendation may not be recorded while its "
                         "transaction costs are unmodelled")

    price = None
    basis = None
    slippage = 0.0
    fills = None
    if dr is not None and dr.is_executable:
        price, basis = dr.vwap, "full-position VWAP"
        fills = dr.levels_consumed or None
    elif dq is not None and dq.executable_price is not None:
        price, basis = dq.executable_price, "top-of-book ask (no usable book)"

    if fair is None or price is None:
        return GateResult(
            UNAVAILABLE, "net executable EV needs both a handicap probability and an executable price; one "
                         "of them is missing")

    contracts = (dr.contracts_required if dr is not None and dr.is_executable
                 else F.contracts_for_stake(float(rec.get("recommended_stake") or 0), float(price)))
    nev = F.net_executable_ev(float(fair), float(price), contracts, ctx.fee_schedule,
                              series_ticker=series, execution_style=ctx.execution_style,
                              slippage_dollars=slippage, as_of=as_of, fills=fills,
                              direct_member=ctx.direct_member)
    report.net_ev = dict(nev.to_dict(), price_basis=basis)

    if not nev.is_known:
        return GateResult(
            FAIL,
            f"transaction costs are {nev.fee_state} for this market ({nev.reason}). A trade whose cost is "
            "unknown cannot be shown to survive its costs, and an unknown cost is never treated as zero.",
            {"fee_state": nev.fee_state, "gross_edge": nev.gross_edge, "price_basis": basis})

    if nev.net_ev_dollars is None:
        return GateResult(UNAVAILABLE, "net executable EV could not be calculated",
                          {"price_basis": basis})

    if nev.net_ev_dollars <= 0:
        return GateResult(
            FAIL,
            f"net executable EV is ${nev.net_ev_dollars:+.4f} at the {basis} of {price}: a gross edge of "
            f"{nev.gross_edge:+.4f} does not survive ${nev.estimated_fees:.4f} of entry fees. A trade worth "
            "zero or less after its known costs is not recorded as a recommendation. This is arithmetic, "
            "not a minimum-edge policy.",
            {k: report.net_ev[k] for k in ("gross_edge", "gross_ev_dollars", "estimated_fees",
                                           "net_ev_dollars", "net_edge", "price_basis")})

    return GateResult(
        PASS,
        f"net executable EV ${nev.net_ev_dollars:+.4f} at the {basis} of {price} "
        f"(gross {nev.gross_edge:+.4f}, fees ${nev.estimated_fees:.4f})",
        {k: report.net_ev[k] for k in ("gross_edge", "gross_ev_dollars", "estimated_fees",
                                       "estimated_slippage_dollars", "net_ev_dollars", "net_edge",
                                       "fee_state", "price_basis")})


def _risk_gate(rec, ctx, report) -> GateResult:
    """The one gate legitimately evaluated at import time.

    It is deterministic from the frozen batch, the recorded bankroll snapshot and the versioned policy file.
    It reads no market state, so there is nothing for import latency to change.
    """
    if ctx.risk_report is None:
        return GateResult(
            UNAVAILABLE, "no portfolio risk report supplied; aggregate game and correlation-group exposure "
                         "could not be checked")
    v = ctx.risk_report.verdict_for(rec.get("recommendation_id"))
    report.risk = v.to_dict() if v is not None else None
    if v is None:
        return GateResult(UNAVAILABLE, "the risk policy produced no verdict for this recommendation")
    if not v.is_actionable:
        return GateResult(
            FAIL, f"rejected by the risk policy ({v.binding_limit}): " + "; ".join(v.reasons),
            {"proposed_stake": v.proposed_stake, "approved_stake": v.approved_stake})
    if abs(v.approved_stake - float(rec.get("recommended_stake") or 0)) > 1e-9:
        return GateResult(
            FAIL,
            f"recommended_stake {rec.get('recommended_stake')} does not match the stake the risk policy "
            f"approved ({v.approved_stake:.2f}); the record must carry the approved size, not the proposed "
            "one",
            {"proposed_stake": v.proposed_stake, "approved_stake": v.approved_stake})
    return GateResult(
        PASS, f"{v.status} at ${v.approved_stake:.2f}" + (f" ({v.binding_limit})" if v.binding_limit else ""),
        {"proposed_stake": v.proposed_stake, "approved_stake": v.approved_stake, "status": v.status})
