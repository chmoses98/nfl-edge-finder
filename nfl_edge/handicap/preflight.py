"""PRE-TRADE preflight: the checks a proposal must survive BEFORE anyone is told to bet.

THE PROBLEM THIS FIXES
----------------------
The decision gates were sound and ran in the wrong place. The Airtable importer runs every twelve hours, so
the sequence could be:

    13:00   ChatGPT says BET
    13:01   the owner places the bet
    01:00   the importer runs
    01:00   the gates discover the book was too thin, the fees eat the edge, or the group cap was already full

Every one of those findings is correct and every one of them is twelve hours late. A control that fires after
the money is down is an audit, not a control.

So the same checks now run at the FRONT of the pipeline:

    HANDICAP CANDIDATE
      -> PRE-TRADE PREFLIGHT            <- here. Nothing is shown as a bet until this passes.
      -> user-visible RECOMMENDED / BET
      -> Airtable READY_FOR_SYNC        <- asserts preflight already passed
      -> delayed GitHub import          <- independently REPLAYS the same evidence
      -> immutable ledger

The twelve-hour cadence is deliberate and is unchanged. What changes is what it means: the importer is no
longer the first place a proposal is checked, it is the place the check is independently reproduced from the
capture stream and committed as evidence. Both run the SAME function on the SAME clock -- each record's own
`created_at` -- which is what makes the replay meaningful. Two implementations of the rules would only tell
us that the second implementation agrees with itself.

NO SECOND COPY OF THE RULES
---------------------------
Nothing in this module decides anything. It assembles a `GateContext` and calls `gates.evaluate_gates`, the
same entry point the importer uses, and it sizes through `risk.report_for_batch`, the same one. Its own job
is narrow and is the part that genuinely differs before the trade:

  * a CANDIDATE is not yet a RECOMMENDED record, so it is evaluated as the record it would become;
  * the stake shown to the owner is the stake the risk policy APPROVED, not the one the handicapper proposed;
  * the verdict is expressed as what the candidate may be CALLED -- and a blocked candidate may be called a
    PASS, a WATCHLIST entry or a CANDIDATE, but never a BET.

APPROVAL TIME IS THE DECISION TIME
---------------------------------
A candidate drafted at 13:00 and preflighted at 13:30 is not a 13:00 decision. If the gates ran against the
candidate's own `created_at`, an approval at 13:30 would be an AUDIT of a 13:00 opportunity -- correct about
a market that no longer exists, and delivered as though it were a live instruction.

So the clock is `approval_as_of`: the moment pre-trade approval is actually evaluated. The executable market
state on the approved record is refreshed to that moment -- the ask, the bid, the mid, the market timestamp
and the minutes to kickoff -- and every gate is then evaluated against it. If the market moved against the
candidate in those thirty minutes, the ceiling or the depth walk blocks it, which is the point.

The HANDICAP does not move. `probability_low/mid/high`, `model_probability`, the thesis and the grade are
the handicapper's opinion from the packet and are carried forward untouched; nothing here recomputes a
predictive model. What is refreshed is the market, because that is the half that goes stale in minutes.

A request can also simply be too old to approve at all. Past `MAX_REQUEST_AGE_MIN` the handicap itself is
stale even if the market is fresh, and the answer is EXPIRED -- submit a new one -- rather than an approval
built on a thesis nobody has looked at in an hour.

WHAT IT STILL DOES NOT DO
-------------------------
It places nothing, orders nothing, and writes nothing to the ledger. A PASS here is permission for a human to
act, not an action.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from nfl_edge.execution import depth as D
from nfl_edge.execution import fees as F
from nfl_edge.execution import quotes as Q
from nfl_edge.handicap import approval as A
from nfl_edge.handicap import gates as G
from nfl_edge.handicap import risk as R
from nfl_edge.handicap import schema as S

# What a candidate may be surfaced as when it has NOT passed preflight. None of these instruct a wager.
CANDIDATE = "CANDIDATE"

APPROVED = "APPROVED"      # may be shown to the owner as a BET, at `approved_stake`
BLOCKED = "BLOCKED"        # may be shown as a candidate/watchlist/pass. Never as a bet.
EXPIRED = "EXPIRED"        # the request sat too long to produce a prospectively defensible approval

# One number, owned by the approval contract, so the worker's expiry and the importer's window can never
# drift apart. See nfl_edge/handicap/approval.py for why it bounds the HANDICAP rather than the market.
MAX_REQUEST_AGE_MIN = A.MAX_REQUEST_AGE.total_seconds() / 60.0


@dataclass
class PreflightResult:
    """One candidate's verdict, and everything the owner needs to see either way."""
    candidate_id: str | None
    verdict: str
    surface_as: str                       # RECOMMENDED when approved; CANDIDATE/PASS otherwise
    as_of: str | None = None              # the APPROVAL timestamp every gate was evaluated at
    candidate_created_at: str | None = None   # when the draft was made, for lineage
    request_age_minutes: float | None = None
    request_age_basis: str | None = None  # which clock the age was measured from
    approved_record: dict | None = None   # the exact canonical record this approval authorises
    proposed_stake: float | None = None
    approved_stake: float | None = None
    blocking_reasons: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    gates: dict = field(default_factory=dict)
    decision_quote: dict | None = None
    depth: dict | None = None
    net_ev: dict | None = None
    fee_schedule: dict | None = None
    risk: dict | None = None
    outstanding: dict | None = None

    @property
    def may_be_shown_as_a_bet(self) -> bool:
        """The single question this module exists to answer."""
        return self.verdict == APPROVED and self.surface_as == S.RECOMMENDED and \
            bool(self.approved_stake) and self.approved_stake > 0

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["may_be_shown_as_a_bet"] = self.may_be_shown_as_a_bet
        return d


def build_context(market_data_root: str | None, *, root: str, risk_report=None,
                  max_quote_age_minutes: float = Q.DEFAULT_MAX_QUOTE_AGE_MIN,
                  max_book_age_minutes: float = D.DEFAULT_MAX_BOOK_AGE_MIN) -> G.GateContext:
    """The gate context, assembled identically for the pre-trade path and the import path.

    Note again what is absent: a `now`. Preflight runs minutes after the decision and the importer runs hours
    after it, and neither may consult a wall clock -- otherwise the two would be answering different
    questions and the replay would prove nothing.
    """
    md = os.path.abspath(market_data_root) if market_data_root else None
    ctx = G.GateContext(
        capture_index=Q.CaptureIndex(md) if md else None,
        book_index=D.BookIndex(md) if md else None,
        fee_schedule=F.load_fee_schedule(root),
        fee_observations=F.FeeObservations(md),
        max_quote_age_minutes=max_quote_age_minutes,
        max_book_age_minutes=max_book_age_minutes,
    )
    ctx.risk_report = risk_report
    return ctx


def _refresh_market_state(rec: dict, ctx, as_of: datetime) -> dict:
    """Re-price the record's MARKET fields at the approval moment. The handicap is left alone.

    Everything replaced here goes stale in minutes -- the two-sided quote, the mid, the market timestamp,
    the time to kickoff. Everything untouched is the handicapper's opinion from the packet:
    `probability_low/mid/high`, `model_probability`, the grade, the thesis, the ceiling. Nothing in this
    module recomputes a predictive model.

    When no fresh quote can be confirmed the record is left exactly as submitted and the freshness gate
    blocks it a moment later, which is the correct answer and a better one than a half-refreshed record.
    """
    if ctx.capture_index is None:
        return rec
    side = rec.get("side", "YES")
    ticker = rec.get("market_ticker")
    dq = Q.resolve_decision_quote(ctx.capture_index, ticker, side,
                                  series_ticker=G._series_of(ticker), as_of=as_of,
                                  max_age_minutes=ctx.max_quote_age_minutes)
    if not dq.is_actionable:
        return rec

    out = dict(rec)
    for field_name, value in (("yes_bid", dq.yes_bid), ("yes_ask", dq.yes_ask),
                              ("no_bid", dq.no_bid), ("no_ask", dq.no_ask)):
        if value is not None:
            out[field_name] = value
    if dq.yes_bid is not None and dq.yes_ask is not None:
        out["mid"] = round((float(dq.yes_bid) + float(dq.yes_ask)) / 2.0, 6)
    out["market_timestamp"] = dq.confirmed_at or as_of.isoformat()

    ko = _ts(rec.get("kickoff_utc"))
    if ko is not None:
        out["minutes_to_kickoff"] = round((ko - as_of).total_seconds() / 60.0, 2)
    return out


def _ts(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def preflight_batch(candidates: list, *, market_data_root: str | None, ledger_root: str | None,
                    root: str, approval_as_of: datetime, policy: R.RiskPolicy | None = None,
                    max_quote_age_minutes: float = Q.DEFAULT_MAX_QUOTE_AGE_MIN,
                    max_book_age_minutes: float = D.DEFAULT_MAX_BOOK_AGE_MIN,
                    max_request_age_minutes: float = MAX_REQUEST_AGE_MIN,
                    request_id: str | None = None, request_created_at: datetime | None = None,
                    bankroll_snapshot: float | None = None) -> list:
    """Preflight a slate of candidates together, AS OF the moment approval is being evaluated.

    Together, not one at a time, because the portfolio limits are statements about a SET of positions: three
    candidates in one correlation group are individually fine and jointly over the cap, and checking them
    separately would approve all three. The cumulative book from earlier runs is folded in by
    `risk.report_for_batch`, so a candidate is measured against everything already outstanding as well as
    against its own slate.

    `approval_as_of` is REQUIRED and is the decision timestamp of anything this approves. There is no
    default: falling back to the candidate's own `created_at` is precisely the bug this argument exists to
    prevent, because the workflow runs minutes-to-hours after the draft was written.

    `request_created_at` is Airtable's SERVER timestamp for the request row, and it is what the expiry
    control is measured from. The candidate's own `created_at` is written by the requester and can say
    anything -- an hours-old request must not be able to refresh itself by claiming a new draft time. When
    there is no Airtable row at all (an operator running the CLI by hand) the candidate's timestamp is the
    only clock available and is used, which the result records so nobody mistakes one for the other.
    """
    if approval_as_of is None:
        raise ValueError(
            "preflight_batch requires `approval_as_of`, the moment pre-trade approval is being evaluated. "
            "Gating at the candidate's own created_at would audit a historical opportunity and present the "
            "result as a live instruction.")
    if approval_as_of.tzinfo is None:
        approval_as_of = approval_as_of.replace(tzinfo=timezone.utc)
    policy = policy or R.RiskPolicy.load(root)

    ctx = build_context(market_data_root, root=root,
                        max_quote_age_minutes=max_quote_age_minutes,
                        max_book_age_minutes=max_book_age_minutes)

    # Every candidate is evaluated as the RECOMMENDED record it would become, at the APPROVAL time, with its
    # market state re-priced to that moment. A candidate is by definition not yet recommended, and
    # `evaluate_gates` correctly declines to gate a non-RECOMMENDED record -- so asking it about the
    # candidate as-is would return NOT_APPLICABLE and approve nothing safely at all.
    # The expiry clock. Airtable's server timestamp when there is one, because it is the half of the
    # provenance the requester cannot write.
    request_at = request_created_at
    if request_at is not None and request_at.tzinfo is None:
        request_at = request_at.replace(tzinfo=timezone.utc)
    age_basis = ("Airtable server createdTime" if request_at is not None
                 else "the candidate's own created_at (no Airtable request row)")

    provisional, ages = [], {}
    for c in candidates:
        clock = request_at if request_at is not None else _ts(c.get("created_at"))
        ages[c.get("recommendation_id")] = (
            None if clock is None else round((approval_as_of - clock).total_seconds() / 60.0, 2))
        p = _refresh_market_state(c, ctx, approval_as_of)
        p = dict(p, decision=S.RECOMMENDED, created_at=approval_as_of.isoformat(),
                 candidate_created_at=c.get("created_at"))
        if request_id:
            p["preflight_request_airtable_id"] = request_id
        provisional.append(p)

    report = R.report_for_batch(provisional, policy, ledger_root, bankroll_snapshot)
    ctx.risk_report = report
    outstanding = getattr(report, "outstanding", None) or {}

    # The stake the owner is shown is the stake the policy APPROVED. Writing it onto the provisional record
    # before gating is what makes the risk gate's stake-match check meaningful rather than circular: the
    # gates then verify the approved size against depth, fees and net EV, which is the size that would
    # actually be worked.
    for p in provisional:
        v = report.verdict_for(p.get("recommendation_id"))
        if v is not None and v.is_actionable:
            p["recommended_stake"] = v.approved_stake

    out = []
    for original, p in zip(candidates, provisional):
        out.append(_one(original, p, ctx, report, outstanding,
                        age_minutes=ages.get(original.get("recommendation_id")),
                        age_basis=age_basis,
                        max_request_age_minutes=max_request_age_minutes))
    return out


def preflight(candidate: dict, **kw) -> PreflightResult:
    """Preflight a single candidate. Sugar over `preflight_batch`; the rules are identical."""
    return preflight_batch([candidate], **kw)[0]


def _one(original: dict, provisional: dict, ctx, report, outstanding, *,
         age_minutes=None, age_basis="", max_request_age_minutes=MAX_REQUEST_AGE_MIN) -> PreflightResult:
    rid = provisional.get("recommendation_id")
    v = report.verdict_for(rid)
    res = PreflightResult(
        candidate_id=rid, verdict=BLOCKED, surface_as=CANDIDATE,
        as_of=provisional.get("created_at"),
        candidate_created_at=original.get("created_at"),
        request_age_minutes=age_minutes, request_age_basis=age_basis,
        proposed_stake=original.get("proposed_stake", original.get("recommended_stake")),
        approved_stake=(v.approved_stake if v is not None and v.is_actionable else None),
        outstanding=outstanding or None)

    # 0. EXPIRY. Before anything else, because an old request cannot be rescued by a good market: the
    #    handicap it carries is the stale half, and no amount of fresh price makes a forgotten thesis
    #    prospective again.
    if age_minutes is None:
        res.verdict = EXPIRED
        res.blocking_reasons.append(
            "no usable request timestamp, so the age of this request at approval cannot be established")
        return res
    if age_minutes < 0:
        res.verdict = EXPIRED
        res.blocking_reasons.append(
            f"the request is dated {abs(age_minutes):.1f} min in the FUTURE relative to this approval "
            f"(measured from {age_basis}); an approval cannot answer a request that does not exist yet")
        return res
    if age_minutes > max_request_age_minutes:
        res.verdict = EXPIRED
        res.blocking_reasons.append(
            f"the preflight request is {age_minutes:.1f} min old measured from {age_basis}, beyond the "
            f"{max_request_age_minutes:.0f} min window. The market can be re-priced; the handicap cannot. "
            "Submit a fresh request rather than approving a thesis nobody has revisited.")
        return res

    # 1. STRUCTURAL. The same schema the importer will apply. A candidate that could not be filed as a
    #    recommendation must not be shown as one either; discovering that twelve hours later is the whole
    #    class of problem this module exists to move forward in time.
    try:
        res.warnings.extend(S.validate_recommendation(provisional) or [])
    except S.ValidationError as e:
        res.blocking_reasons.append(f"schema: {e}")
        return res

    # 2. SITUATIONAL. Byte for byte the checks the importer will replay, at the APPROVAL timestamp.
    gr = G.evaluate_gates(provisional, ctx)
    res.as_of = gr.as_of
    res.gates = {k: g.to_dict() for k, g in gr.gates.items()}
    res.decision_quote, res.depth = gr.decision_quote, gr.depth
    res.net_ev, res.risk, res.fee_schedule = gr.net_ev, gr.risk, gr.fee_schedule
    res.warnings.extend(gr.warnings)
    res.blocking_reasons.extend(gr.blocking_reasons)

    if gr.overall != G.PASS or res.blocking_reasons:
        return res
    if not res.approved_stake or res.approved_stake <= 0:
        res.blocking_reasons.append(
            "the risk policy approved no stake for this candidate, so there is nothing to bet")
        return res

    # 3. The exact record this approval authorises. Not a description of one -- the canonical thing the
    #    ledger will archive, so there is nothing left for a later step to reinterpret.
    res.approved_record = provisional
    res.verdict, res.surface_as = APPROVED, S.RECOMMENDED
    return res


def summarise(results: list) -> str:
    """One line per candidate, in the vocabulary the owner is allowed to act on."""
    lines = []
    for r in results:
        if r.may_be_shown_as_a_bet:
            lines.append(f"BET        {r.candidate_id}  ${r.approved_stake:.2f}"
                         + (f"  (proposed ${float(r.proposed_stake):.2f})"
                            if r.proposed_stake not in (None, r.approved_stake) else ""))
        else:
            lines.append(f"{r.surface_as:<10} {r.candidate_id}  NOT A BET")
            for b in r.blocking_reasons:
                lines.append(f"           - {b}")
    return "\n".join(lines)
