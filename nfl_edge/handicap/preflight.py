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
from nfl_edge.handicap import gates as G
from nfl_edge.handicap import risk as R
from nfl_edge.handicap import schema as S

# What a candidate may be surfaced as when it has NOT passed preflight. None of these instruct a wager.
CANDIDATE = "CANDIDATE"

APPROVED = "APPROVED"      # may be shown to the owner as a BET, at `approved_stake`
BLOCKED = "BLOCKED"        # may be shown as a candidate/watchlist/pass. Never as a bet.


@dataclass
class PreflightResult:
    """One candidate's verdict, and everything the owner needs to see either way."""
    candidate_id: str | None
    verdict: str
    surface_as: str                       # RECOMMENDED when approved; CANDIDATE/PASS otherwise
    as_of: str | None = None
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


def preflight_batch(candidates: list, *, market_data_root: str | None, ledger_root: str | None,
                    root: str, policy: R.RiskPolicy | None = None,
                    max_quote_age_minutes: float = Q.DEFAULT_MAX_QUOTE_AGE_MIN,
                    max_book_age_minutes: float = D.DEFAULT_MAX_BOOK_AGE_MIN,
                    bankroll_snapshot: float | None = None) -> list:
    """Preflight a slate of candidates together.

    Together, not one at a time, because the portfolio limits are statements about a SET of positions: three
    candidates in one correlation group are individually fine and jointly over the cap, and checking them
    separately would approve all three. The cumulative book from earlier runs is folded in by
    `risk.report_for_batch`, so a candidate is measured against everything already outstanding as well as
    against its own slate.
    """
    policy = policy or R.RiskPolicy.load(root)

    # Every candidate is evaluated as the RECOMMENDED record it would become. A candidate is by definition
    # not yet recommended, and `evaluate_gates` correctly declines to gate a non-RECOMMENDED record -- so
    # asking it about the candidate as-is would return NOT_APPLICABLE and approve nothing safely at all.
    provisional = [dict(c, decision=S.RECOMMENDED) for c in candidates]

    report = R.report_for_batch(provisional, policy, ledger_root, bankroll_snapshot)
    outstanding = getattr(report, "outstanding", None) or {}

    # The stake the owner is shown is the stake the policy APPROVED. Writing it onto the provisional record
    # before gating is what makes the risk gate's stake-match check meaningful rather than circular: the
    # gates then verify the approved size against depth, fees and net EV, which is the size that would
    # actually be worked.
    for p in provisional:
        v = report.verdict_for(p.get("recommendation_id"))
        if v is not None and v.is_actionable:
            p["recommended_stake"] = v.approved_stake

    ctx = build_context(market_data_root, root=root, risk_report=report,
                        max_quote_age_minutes=max_quote_age_minutes,
                        max_book_age_minutes=max_book_age_minutes)

    out = []
    for original, p in zip(candidates, provisional):
        out.append(_one(original, p, ctx, report, outstanding))
    return out


def preflight(candidate: dict, **kw) -> PreflightResult:
    """Preflight a single candidate. Sugar over `preflight_batch`; the rules are identical."""
    return preflight_batch([candidate], **kw)[0]


def _one(original: dict, provisional: dict, ctx, report, outstanding) -> PreflightResult:
    rid = provisional.get("recommendation_id")
    v = report.verdict_for(rid)
    res = PreflightResult(
        candidate_id=rid, verdict=BLOCKED, surface_as=CANDIDATE,
        proposed_stake=original.get("proposed_stake", original.get("recommended_stake")),
        approved_stake=(v.approved_stake if v is not None and v.is_actionable else None),
        outstanding=outstanding or None)

    # 1. STRUCTURAL. The same schema the importer will apply. A candidate that could not be filed as a
    #    recommendation must not be shown as one either; discovering that twelve hours later is the whole
    #    class of problem this module exists to move forward in time.
    try:
        res.warnings.extend(S.validate_recommendation(provisional) or [])
    except S.ValidationError as e:
        res.blocking_reasons.append(f"schema: {e}")
        return res

    # 2. SITUATIONAL. Byte for byte the checks the importer will replay.
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
