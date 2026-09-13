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
from time import monotonic as _monotonic

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
    # The DELIVERY check, kept deliberately out of `gates`. See `authorize_issuance`: it is a statement
    # about the moment the answer was handed over, not about the decision, so it must never appear in the
    # gate report the importer replays.
    issuance: dict | None = None

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
                  max_book_age_minutes: float = D.DEFAULT_MAX_BOOK_AGE_MIN,
                  capture_index=None, book_index=None,
                  fee_observations_root: str | None = None) -> G.GateContext:
    """The gate context, assembled identically for the pre-trade path and the import path.

    Note again what is absent: a `now`. Preflight runs minutes after the decision and the importer runs hours
    after it, and neither may consult a wall clock -- otherwise the two would be answering different
    questions and the replay would prove nothing.

    TWO SOURCES OF MARKET EVIDENCE, ONE SET OF GATES
    ------------------------------------------------
    `market_data_root` is the capture stream: immutable, point-in-time, and the right evidence for the
    ARCHIVAL replay, which is asking what the market was hours ago. Reading it costs a full checkout of a
    branch that held ~17,491 files on 2026-09-13, which is the wrong price to pay for a live pre-trade
    question about ONE contract.

    So `capture_index` and `book_index` may be supplied directly. The live path passes indexes over
    candidate-specific evidence fetched seconds earlier (see nfl_edge/handicap/live_evidence.py); the
    importer passes nothing and gets the capture stream. Either way `evaluate_gates` is the same function
    reading the same two interfaces, which is what keeps the replay meaningful.

    `fee_observations_root` splits the fee-observation read off from the quote read, so the live path can
    take a SPARSE checkout holding only `data/kalshi/fees/` and still answer the fee-schedule gate properly.
    """
    md = os.path.abspath(market_data_root) if market_data_root else None
    fees_root = os.path.abspath(fee_observations_root) if fee_observations_root else md
    ctx = G.GateContext(
        capture_index=capture_index if capture_index is not None else (Q.CaptureIndex(md) if md else None),
        book_index=book_index if book_index is not None else (D.BookIndex(md) if md else None),
        fee_schedule=F.load_fee_schedule(root),
        fee_observations=F.FeeObservations(fees_root),
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
                    bankroll_snapshot: float | None = None,
                    capture_index=None, book_index=None,
                    fee_observations_root: str | None = None,
                    phase=None) -> list:
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
                        max_book_age_minutes=max_book_age_minutes,
                        capture_index=capture_index, book_index=book_index,
                        fee_observations_root=fee_observations_root)

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

    # `phase(name, seconds)` is OBSERVATION ONLY and is never consulted for anything. The 2026-09-13
    # incident was a latency failure nobody could see the shape of without reading raw runner logs
    # afterwards, and reading the committed ledger is a genuinely separate cost from running the gates --
    # reporting them as one number would hide whichever of the two was actually slow.
    _t0 = _monotonic()
    report = R.report_for_batch(provisional, policy, ledger_root, bankroll_snapshot)
    if phase is not None:
        phase("ledger_load", _monotonic() - _t0)
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

    # 0.5 PRE-KICKOFF. Before the schema, so a post-kickoff request comes back with the gate's own name on
    #     it. The schema also refuses `minutes_to_kickoff <= 0`, but that is a number the REQUESTER supplies
    #     and preflight only recomputes when a fresh quote could be confirmed -- so the case that matters
    #     most, a request whose market state could not be refreshed, is exactly the one where the stale
    #     self-reported figure survives. This reads `kickoff_utc` against the approval clock. It is the same
    #     function `evaluate_gates` runs, so the importer's replay reaches the identical verdict.
    if not provisional.get("test_only"):
        as_of_dt = _ts(provisional.get("created_at"))
        pk = (G.pre_kickoff_gate(provisional, as_of_dt) if as_of_dt is not None else
              G.GateResult(G.UNAVAILABLE,
                           "the approval carries no usable timestamp, so it cannot be shown to predate "
                           "kickoff"))
        res.gates[G.G_PRE_KICKOFF] = pk.to_dict()
        if pk.status in G.BLOCKING:
            res.blocking_reasons.append(f"{G.G_PRE_KICKOFF}: {pk.reason}")
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


# The name that appears on a refusal, stable so a reader can tell an ISSUANCE refusal from a GATE failure
# at a glance. Deliberately not a `G_*` gate constant: see below.
ISSUANCE = "issuance_temporal_authorization"


def authorize_issuance(results: list, *, issued_at: datetime,
                       max_quote_age_minutes: float = Q.DEFAULT_MAX_QUOTE_AGE_MIN,
                       max_book_age_minutes: float = D.DEFAULT_MAX_BOOK_AGE_MIN) -> list:
    """The last thing before an approval is handed over: is it STILL authorised, right now?

    THE RACE THIS CLOSES
    --------------------
    Every gate is evaluated at `approval_as_of`, the decision instant -- correctly, because that is what
    makes the verdict replayable. But the worker then keeps working: it builds the canonical payload, signs
    it, and writes Airtable. Time passes between the decision and the delivery, and two things can expire in
    that window:

        decision at T-1s, kickoff at T        ->  the gates pass, and the owner is told to bet on a game
                                                  that has already started by the time they read it
        quote confirmed 14.9 min before the   ->  the gates pass, and the price the approval authorises is
        decision                                  over the fifteen-minute line before the row is written

    Neither is a defect in the gates. The gates answered the question they were asked, at the moment they
    were asked it. This asks the OTHER question -- may this still be delivered? -- and it can only be asked
    at delivery time.

    WHY THIS IS NOT A GATE, AND MUST NOT BECOME ONE
    -----------------------------------------------
    `decision_before_kickoff` and the freshness gates are pure functions of the record and its evidence, and
    that is what lets the importer reproduce the verdict hours later and get the same answer. This check
    reads a clock that will never exist again. Putting it in `gates` would make the gate report
    irreproducible and quietly break the replay -- so the refusal is recorded on `issuance`, and in
    `blocking_reasons` where the owner will read it, and nowhere else.

    `decision_before_kickoff` therefore stays exactly as it was. This is an ADDITIONAL refusal, never a
    replacement, and it can only ever turn an APPROVED into a BLOCKED.

    FAIL CLOSED
    -----------
    Only candidates that would otherwise be approved are examined -- there is nothing to withdraw from one
    already blocked. For those, a missing or unreadable kickoff, quote timestamp or book timestamp is a
    refusal: at the point of authorising real money, "I cannot tell whether this is still valid" is not a
    yes. Refused candidates lose their approved record, so no payload is built and nothing is signed.

    Returns the refusals as `(candidate_id, reason)`, and mutates the results in place.
    """
    if issued_at.tzinfo is None:
        issued_at = issued_at.replace(tzinfo=timezone.utc)
    refusals = []
    for r in results:
        if not r.may_be_shown_as_a_bet:
            continue
        rec = r.approved_record or {}
        checks = {"issued_at": issued_at.isoformat()}
        reason = None

        # 1. STILL PREGAME. Strictly before, exactly as the gate requires of the decision.
        ko = _ts(rec.get("kickoff_utc"))
        if ko is None:
            reason = ("the approved record carries no readable kickoff_utc, so it cannot be shown to be "
                      "still pregame at the moment of issue")
        else:
            checks["kickoff_utc"] = ko.isoformat()
            checks["minutes_to_kickoff_at_issue"] = round((ko - issued_at).total_seconds() / 60.0, 2)
            if issued_at >= ko:
                reason = (
                    f"kickoff passed while this approval was being prepared: the gates were evaluated at "
                    f"{r.as_of} and the answer was issued at {issued_at.isoformat()}, at or after kickoff "
                    f"{ko.isoformat()}. A pregame position can no longer be authorized.")

        # 2. THE QUOTE IS STILL INSIDE ITS WINDOW, measured from the same confirmation the gate used.
        if reason is None:
            confirmed = _ts((r.decision_quote or {}).get("confirmed_at"))
            if confirmed is None:
                reason = ("the approved record carries no readable quote confirmation time, so its age at "
                          "issue cannot be established")
            else:
                age = round((issued_at - confirmed).total_seconds() / 60.0, 2)
                checks["quote_age_minutes_at_issue"] = age
                if age > max_quote_age_minutes:
                    reason = (
                        f"the confirmed quote went stale while this approval was being prepared: "
                        f"{age:.1f} min old at issue, beyond the {max_quote_age_minutes:.0f} min window. "
                        "The price this approval authorises is no longer one we have seen.")

        # 3. AND SO IS THE BOOK. Its own clock, because books are fetched after quotes and age separately.
        if reason is None:
            observed = _ts((r.depth or {}).get("book_observed_at"))
            if observed is None:
                reason = ("the approved record carries no readable order-book timestamp, so its age at "
                          "issue cannot be established")
            else:
                age = round((issued_at - observed).total_seconds() / 60.0, 2)
                checks["book_age_minutes_at_issue"] = age
                if age > max_book_age_minutes:
                    reason = (
                        f"the order book went stale while this approval was being prepared: {age:.1f} min "
                        f"old at issue, beyond the {max_book_age_minutes:.0f} min window. The depth this "
                        "approval rests on is no longer observed.")

        checks["authorized"] = reason is None
        if reason is not None:
            checks["refusal"] = reason
            r.verdict, r.surface_as = BLOCKED, CANDIDATE
            # The record goes with it. Nothing downstream may build a payload from a withdrawn approval.
            r.approved_record = None
            r.blocking_reasons.append(f"{ISSUANCE}: {reason}")
            refusals.append((r.candidate_id, reason))
        r.issuance = checks
    return refusals


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
