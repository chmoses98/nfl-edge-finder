"""Bankroll and portfolio risk policy for the prospective pilot.

The decision layer proposes stakes. This module decides whether the bankroll may carry them. Those are two
different jobs and they are done by two different things on purpose:

    ChatGPT proposes  ->  risk policy validates / caps  ->  the ledger records BOTH numbers

Recording both is what makes the policy auditable. `proposed_stake` is what the handicapper wanted;
`recommended_stake` is what was approved. If they always agree the policy is not binding and we should say
so; if they often disagree the handicapper is systematically oversized and we should know that too. A policy
that silently overwrote the proposal would destroy the evidence for both claims.

WHAT THIS IS NOT
----------------
It is not Kelly, fractional Kelly, or anything else proportional to estimated edge. Edge-proportional sizing
is a bet on the calibration of the probability that generates the edge, and the ChatGPT handicap layer has
ZERO prospective betting history -- that calibration is the thing this ledger exists to measure, so it cannot
also be an input to sizing. Sizing here is flat in units with grade-based caps. Kelly is a question for after
the handicap layer demonstrates prospective calibration, not before.

It also does not invent dollar amounts. Every limit in `config/risk_policy.json` is a bankroll fraction or a
count of units, so the same policy file is correct at any bankroll. A unit is `unit_fraction_of_bankroll *
bankroll_snapshot`, and `bankroll_snapshot` comes from the recommendation, not from this module.

CORRELATION
-----------
The packet carries QUALITATIVE correlation groups -- "this game's scoring goes up", "the home side wins" --
and this module treats them as exactly that. It does not multiply them into a covariance matrix, because no
such estimate exists for these contracts and inventing one would be worse than admitting there is none.

What it does do is notice concentration. Team ML plus team spread plus the opponent's under is one thesis
bought three times, and a portfolio limit is the honest way to handle a correlation you can name but cannot
measure. The per-group cap is deliberately tighter than the per-game cap for that reason.

Exposure is measured in DOLLARS STAKED. For a Kalshi long that is the maximum loss, which is the quantity a
risk limit should actually bind.

CUMULATIVE, ACROSS RUNS
-----------------------
A limit that resets every batch is not a limit. Two handicap runs two hours apart, each proposing 2u into
the same correlation group, each independently "under" a 3u cap, put 4u into one thesis -- and every gate
says PASS while the desk breaks its own policy.

So the caps bind against OUTSTANDING EXPOSURE PLUS THE CURRENT BATCH. Outstanding exposure is read from the
ledger as of the decision timestamp and is defined conservatively:

    reserved       max(approved recommended stake - executed stake, 0), held until kickoff or supersession
    at risk        executed stake, held until the position settles AND THAT SETTLEMENT WAS AVAILABLE

    total per recommendation = reserved + at risk

That last clause is not pedantry. A settlement is the one fact that can loosen a cap, and it arrives HOURS
after the decisions it would loosen. Releasing on the mere existence of an Evaluation lets the twelve-hourly
replay of a 15:00 decision use a 21:00 settlement and approve exposure that was over the limit when the call
was actually made -- and the replay exists to REPRODUCE the pre-trade verdict, not to improve on it with
hindsight. So a settlement releases exposure at time T only if the ledger can show the outcome was knowable
at or before T, and a settlement with no usable availability timestamp releases nothing at all.

Which is `max(approved, executed)` once a position is fully filled, so a recommendation and its own fills are
never counted twice. A partial fill of $6 against an approved $10 holds $10: $6 at risk and $4 still
reservable. What is EXCLUDED is stated as explicitly as what is included -- TEST_ONLY, PASS/WATCHLIST/
RESEARCH_ALERT, superseded links in an amendment chain, anything decided after `as_of`, and settled
positions -- and every exclusion is recorded with its reason so the arithmetic can be audited rather than
trusted.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from nfl_edge.handicap import store

APPROVED = "APPROVED"          # the proposal stands as submitted
CAPPED = "CAPPED"              # allowed, but at a smaller stake than proposed
REJECTED = "REJECTED"          # not allowed at any size under this policy

DEFAULT_POLICY_PATH = os.path.join("config", "risk_policy.json")


class RiskPolicyError(ValueError):
    """The policy itself, or the state handed to it, is unusable. Never a verdict on a bet."""


@dataclass
class Proposal:
    """One stake the decision layer wants to take."""
    recommendation_id: str
    proposed_stake: float
    game_id: str | None = None
    correlation_group: str | None = None
    grade: str | None = None
    market_ticker: str | None = None

    @classmethod
    def from_record(cls, rec: dict) -> "Proposal":
        stake = rec.get("proposed_stake")
        if stake is None:
            stake = rec.get("recommended_stake")
        return cls(
            recommendation_id=rec.get("recommendation_id"),
            proposed_stake=0.0 if stake is None else float(stake),
            game_id=rec.get("game_id"),
            correlation_group=rec.get("correlation_group"),
            grade=rec.get("grade"),
            market_ticker=rec.get("market_ticker"),
        )


@dataclass
class Verdict:
    """What the policy decided about one proposal, and which limit did the deciding."""
    recommendation_id: str
    status: str
    proposed_stake: float
    approved_stake: float
    binding_limit: str | None = None
    reasons: list = field(default_factory=list)

    @property
    def is_actionable(self) -> bool:
        return self.status in (APPROVED, CAPPED) and self.approved_stake > 0

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class OutstandingPosition:
    """One already-live position's claim on the bankroll, split into why it is still a claim."""
    recommendation_id: str
    approved_stake: float
    executed_stake: float
    reserved_stake: float          # approved but not yet filled, and still fillable
    at_risk_stake: float           # filled and not yet settled
    exposure: float                # reserved + at_risk
    game_id: str | None = None
    correlation_group: str | None = None
    market_ticker: str | None = None
    basis: str = ""

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class OutstandingExposure:
    """What the book already carries at a point in time, and everything deliberately left out of it.

    `excluded` is not decoration. A cumulative limit is only auditable if the reason a position was NOT
    counted is written down next to the number, so a later reviewer can check the subtraction rather than
    take it on faith.
    """
    as_of: str | None = None
    release_as_of: str | None = None
    positions: list = field(default_factory=list)
    by_game: dict = field(default_factory=dict)
    by_correlation_group: dict = field(default_factory=dict)
    total: float = 0.0
    excluded: list = field(default_factory=list)          # [(recommendation_id, reason)]
    source: str = ""

    def to_dict(self) -> dict:
        return {"as_of": self.as_of, "release_as_of": self.release_as_of,
                "total": self.total, "by_game": self.by_game,
                "by_correlation_group": self.by_correlation_group, "source": self.source,
                "positions": [p.to_dict() for p in self.positions],
                "excluded": [{"recommendation_id": r, "reason": w} for r, w in self.excluded]}


EMPTY_EXPOSURE = OutstandingExposure(source="no prior exposure supplied")


@dataclass
class PortfolioReport:
    """The whole slate's verdict, plus the exposure it actually consumes."""
    policy_id: str
    bankroll_snapshot: float
    unit_dollars: float
    verdicts: list = field(default_factory=list)
    exposure_by_game: dict = field(default_factory=dict)
    exposure_by_correlation_group: dict = field(default_factory=dict)
    total_exposure: float = 0.0
    limits: dict = field(default_factory=dict)
    violations: list = field(default_factory=list)
    # What the book already carried BEFORE this batch. The `exposure_by_*` maps above are cumulative --
    # outstanding plus this batch -- because that is what the caps actually bind against.
    outstanding: dict = field(default_factory=dict)
    batch_exposure: float = 0.0

    @property
    def all_approved(self) -> bool:
        return all(v.status == APPROVED for v in self.verdicts)

    def verdict_for(self, recommendation_id: str) -> Verdict | None:
        return next((v for v in self.verdicts if v.recommendation_id == recommendation_id), None)

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["verdicts"] = [v.to_dict() for v in self.verdicts]
        d["all_approved"] = self.all_approved
        return d


@dataclass
class RiskPolicy:
    policy_id: str = "unversioned"
    status: str = "PILOT"
    unit_fraction_of_bankroll: float = 0.005
    max_stake_per_position_units: float = 2.0
    max_exposure_per_game_units: float = 4.0
    max_exposure_per_correlation_group_units: float = 3.0
    max_slate_exposure_units: float = 12.0
    max_slate_exposure_fraction_of_bankroll: float | None = 0.06
    grade_caps_units: dict = field(default_factory=dict)
    round_stakes_to_dollars: bool = True
    min_stake_dollars: float = 1.0

    # ---- loading --------------------------------------------------------------------------------
    @classmethod
    def load(cls, root: str, path: str | None = None) -> "RiskPolicy":
        p = path or os.path.join(root, DEFAULT_POLICY_PATH)
        if not os.path.exists(p):
            raise RiskPolicyError(
                f"no risk policy at {p}. A real recommendation is not sized by default values living in "
                "code; the policy is configuration and must exist.")
        with open(p) as f:
            d = json.load(f)
        known = {k: d[k] for k in d if k in cls.__dataclass_fields__}
        return cls(**known)

    def unit_dollars(self, bankroll: float) -> float:
        return float(bankroll) * float(self.unit_fraction_of_bankroll)

    def _slate_cap(self, unit: float, bankroll: float) -> tuple[float, str]:
        """The MORE BINDING of the unit-count cap and the bankroll-fraction cap.

        Two expressions of the same limit exist because a unit count is easier to reason about and a bankroll
        fraction is what actually protects the account. Taking the minimum means editing one can only ever
        tighten the policy, never quietly loosen it through the other.
        """
        by_units = self.max_slate_exposure_units * unit
        if self.max_slate_exposure_fraction_of_bankroll is None:
            return by_units, "max_slate_exposure_units"
        by_fraction = float(bankroll) * float(self.max_slate_exposure_fraction_of_bankroll)
        return ((by_units, "max_slate_exposure_units") if by_units <= by_fraction
                else (by_fraction, "max_slate_exposure_fraction_of_bankroll"))

    def _round(self, stake: float) -> float:
        """Round DOWN to whole dollars. A risk cap that rounds up is not a cap.

        An INT, not a float. The schema requires a whole-dollar integer stake, and the approved size is
        written straight onto the record the pre-trade path shows the owner -- a 20.0 there is refused by
        `validate_recommendation` at the last moment, for a reason that has nothing to do with the bet.
        """
        if not self.round_stakes_to_dollars:
            return round(stake, 2)
        return int(math.floor(stake + 1e-9))

    # ---- the decision ---------------------------------------------------------------------------
    def evaluate(self, proposals: list, bankroll_snapshot: float,
                 outstanding: "OutstandingExposure | None" = None) -> PortfolioReport:
        """Cap every proposal against position, grade, game, correlation-group and slate limits.

        `outstanding` is what the book ALREADY carries -- from earlier handicap runs, earlier Airtable rows,
        amendments, unfilled approvals and unsettled fills. Every aggregate budget starts partly consumed by
        it, which is the whole difference between a limit and a suggestion: without it, two runs of 2u each
        both pass a 3u correlation cap and the desk ends up at 4u.

        Proposals are processed in descending proposed size so that when a shared budget runs out it is the
        smallest positions that get squeezed, not whichever happened to be listed first. Order-dependence is
        unavoidable in a greedy allocator; making it deterministic and stated is the honest version.
        """
        if bankroll_snapshot is None or float(bankroll_snapshot) <= 0:
            raise RiskPolicyError(
                "bankroll_snapshot must be a positive number; portfolio limits are fractions of a bankroll "
                "and cannot be evaluated without one")
        bankroll = float(bankroll_snapshot)
        unit = self.unit_dollars(bankroll)
        slate_cap, slate_limit_name = self._slate_cap(unit, bankroll)
        report = PortfolioReport(
            policy_id=self.policy_id, bankroll_snapshot=bankroll, unit_dollars=round(unit, 4),
            limits={
                "unit_dollars": round(unit, 4),
                "max_stake_per_position": round(self.max_stake_per_position_units * unit, 2),
                "max_exposure_per_game": round(self.max_exposure_per_game_units * unit, 2),
                "max_exposure_per_correlation_group":
                    round(self.max_exposure_per_correlation_group_units * unit, 2),
                "max_slate_exposure": round(slate_cap, 2),
                "slate_binding_limit": slate_limit_name,
            })

        out = outstanding or EMPTY_EXPOSURE
        report.outstanding = out.to_dict()

        # The budgets start where the book already is. A cap is a statement about the DESK's total position,
        # not about whichever batch happens to be in front of the policy right now.
        game_used: dict = {k: float(v) for k, v in (out.by_game or {}).items()}
        group_used: dict = {k: float(v) for k, v in (out.by_correlation_group or {}).items()}
        total_used = float(out.total or 0.0)
        opening_total = total_used

        for p in sorted(proposals, key=lambda x: (-float(x.proposed_stake or 0.0), x.recommendation_id or "")):
            reasons: list = []
            binding = None
            allowed = float(p.proposed_stake or 0.0)

            if allowed <= 0:
                report.verdicts.append(Verdict(p.recommendation_id, REJECTED, allowed, 0.0,
                                               "non_positive_stake",
                                               ["a proposed stake of zero or less is not a position"]))
                continue

            def tighten(cap: float, name: str, note: str):
                nonlocal allowed, binding
                if cap < allowed:
                    reasons.append(f"{note}: {allowed:.2f} -> {cap:.2f}")
                    allowed = cap
                    binding = name

            tighten(self.max_stake_per_position_units * unit, "max_stake_per_position_units",
                    f"per-position cap {self.max_stake_per_position_units}u")

            if p.grade and self.grade_caps_units:
                gc = self.grade_caps_units.get(p.grade)
                if gc is None:
                    report.verdicts.append(Verdict(
                        p.recommendation_id, REJECTED, float(p.proposed_stake), 0.0, "grade_caps_units",
                        [f"grade {p.grade!r} has no configured cap; the policy will not size a grade it "
                         "does not recognise"]))
                    continue
                tighten(float(gc) * unit, "grade_caps_units", f"grade {p.grade} cap {gc}u")

            if p.game_id:
                used = game_used.get(p.game_id, 0.0)
                room = self.max_exposure_per_game_units * unit - used
                tighten(max(room, 0.0), "max_exposure_per_game_units",
                        f"game {p.game_id} aggregate cap {self.max_exposure_per_game_units}u "
                        f"({used:.2f} already committed)")

            if p.correlation_group:
                used = group_used.get(p.correlation_group, 0.0)
                room = self.max_exposure_per_correlation_group_units * unit - used
                tighten(max(room, 0.0), "max_exposure_per_correlation_group_units",
                        f"correlation group {p.correlation_group} cap "
                        f"{self.max_exposure_per_correlation_group_units}u "
                        f"({used:.2f} already committed)")

            tighten(max(slate_cap - total_used, 0.0), slate_limit_name,
                    f"slate aggregate cap ({slate_limit_name}, {total_used:.2f} already committed)")

            allowed = self._round(allowed)

            if allowed < self.min_stake_dollars:
                report.verdicts.append(Verdict(
                    p.recommendation_id, REJECTED, float(p.proposed_stake), 0.0, binding,
                    reasons + [f"remaining room {allowed:.2f} is below the {self.min_stake_dollars} minimum "
                               "stake; the position is rejected rather than taken at a token size"]))
                report.violations.append(
                    f"{p.recommendation_id}: rejected by {binding or 'policy'}")
                continue

            status = APPROVED if abs(allowed - float(p.proposed_stake)) < 1e-9 else CAPPED
            if status == CAPPED:
                report.violations.append(
                    f"{p.recommendation_id}: proposed {float(p.proposed_stake):.2f} capped to {allowed:.2f} "
                    f"by {binding}")
            report.verdicts.append(Verdict(p.recommendation_id, status, float(p.proposed_stake), allowed,
                                           binding if status == CAPPED else None, reasons))

            if p.game_id:
                game_used[p.game_id] = game_used.get(p.game_id, 0.0) + allowed
            if p.correlation_group:
                group_used[p.correlation_group] = group_used.get(p.correlation_group, 0.0) + allowed
            total_used += allowed

        # These are CUMULATIVE: outstanding plus this batch, which is what the caps bound.
        report.exposure_by_game = {k: round(v, 2) for k, v in sorted(game_used.items())}
        report.exposure_by_correlation_group = {k: round(v, 2) for k, v in sorted(group_used.items())}
        report.total_exposure = round(total_used, 2)
        report.batch_exposure = round(total_used - opening_total, 2)
        return report


def evaluate_records(records: list, policy: RiskPolicy, bankroll_snapshot: float | None = None,
                     decisions=("RECOMMENDED",),
                     outstanding: OutstandingExposure | None = None) -> PortfolioReport:
    """Run the policy over a batch of recommendation dicts.

    Only records whose decision actually consumes bankroll are sized. A PASS carries no exposure and must not
    consume a game's or a group's budget, or a slate of passes would crowd out the one bet that was taken.
    """
    # TEST_ONLY records risk no capital. Letting one consume a game's or the slate's budget would let a
    # connectivity check crowd out a real position.
    live = [r for r in records if r.get("decision") in decisions and not r.get("test_only")]
    if bankroll_snapshot is None:
        snaps = {r.get("bankroll_snapshot") for r in live if r.get("bankroll_snapshot") is not None}
        if len(snaps) > 1:
            raise RiskPolicyError(
                f"the batch carries more than one bankroll_snapshot ({sorted(snaps)}); portfolio limits are "
                "undefined when the records disagree about the size of the bankroll")
        if not snaps:
            raise RiskPolicyError(
                "no bankroll_snapshot on any record in the batch; a portfolio limit expressed as a fraction "
                "of bankroll cannot be evaluated without one")
        bankroll_snapshot = snaps.pop()
    return policy.evaluate([Proposal.from_record(r) for r in live], bankroll_snapshot, outstanding)


# ---- outstanding exposure --------------------------------------------------------------------------

# A recommendation is not gated on a decision's own kickoff here; `_ts` returning None means "no usable
# timestamp", which is always resolved in the direction that KEEPS exposure on the book.
def _ts(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# The order matters: an explicit observation of the outcome is stronger provenance than the moment somebody
# ran the evaluator, and `evaluated_at` is the conservative fallback because it can only be LATER than the
# outcome, never earlier -- so using it can retain exposure too long and can never release it too early.
SETTLEMENT_AVAILABILITY_FIELDS = ("settlement_observed_at", "settlement_determined_at",
                                  "outcome_observed_at", "evaluated_at")


def _settlement_available_at(ev: dict):
    """When a settlement became KNOWABLE, and from which field we learned it.

    Never wall clock. A settlement with no usable timestamp returns `(None, ...)` and releases nothing.
    """
    for f in SETTLEMENT_AVAILABILITY_FIELDS:
        t = _ts(ev.get(f))
        if t is not None:
            return t, f
    return None, "none"


def outstanding_exposure(recommendations: list, executions: list, evaluations: list, as_of,
                         *, release_as_of=None, exclude_ids=(),
                         decisions=("RECOMMENDED",)) -> OutstandingExposure:
    """What the book already carries at `as_of`, from the ledger's own records.

    The definition, and why each half of it is what it is:

      RESERVED   `max(approved_stake - executed_stake, 0)` on a live recommendation. An approval the owner
                 has not yet filled is still a commitment to fill it, so it holds budget. It is released at
                 KICKOFF -- after which the pregame position can no longer be established -- or when an
                 amendment supersedes the record.

      AT RISK    executed stake, held until the position SETTLES. A filled position is exposure in the most
                 literal sense: the money is gone until the contract resolves. Settlement is established
                 from an Evaluation carrying a `settlement`, because that is the ledger's only record that
                 the outcome is known.

    Their sum is `max(approved, executed)` for a fully-filled position, so a recommendation and its own
    fills never double count, and a partial fill neither forgets the filled half nor releases the unfilled
    one.

    Everything is evaluated AS OF the decision timestamp: a recommendation made after `as_of`, or a fill
    that happened after it, was not exposure when this call was made. That is the same clock every other
    gate uses, and it is what makes the answer independent of when the importer got around to the row.
    """
    at = _ts(as_of)
    if at is None:
        raise RiskPolicyError(
            "outstanding_exposure requires a decision timestamp. Cumulative exposure is a statement about a "
            "point in time, and defaulting to wall clock would count positions taken after the decision "
            "being evaluated.")
    # Two bounds, each rounded against the batch, exactly as the quote gate does with capture runs. INCLUSION
    # asks "did this position already exist?" and uses the LATEST decision in the batch, so nothing prior is
    # missed. RELEASE asks "has it gone away yet?" and uses the EARLIEST, so nothing is let go early. A batch
    # spanning one minute makes them the same; a batch spanning hours is judged conservatively at both ends.
    release_at = _ts(release_as_of) or at

    exclude = set(exclude_ids or ())
    excluded: list = []

    live = []
    for r in recommendations or []:
        rid = r.get("recommendation_id")
        if rid in exclude:
            excluded.append((rid, "in the batch currently being evaluated; counted there, not here"))
            continue
        if r.get("test_only"):
            excluded.append((rid, "TEST_ONLY: risks no capital"))
            continue
        if r.get("decision") not in decisions:
            excluded.append((rid, f"decision {r.get('decision')} consumes no bankroll"))
            continue
        created = _ts(r.get("created_at"))
        if created is not None and created > at:
            excluded.append((rid, f"decided at {r.get('created_at')}, after the decision being evaluated"))
            continue
        live.append(r)

    # Only the current opinion in an amendment chain carries exposure. The superseded links stay in the
    # ledger -- they are simply represented by the record that replaced them.
    current = store.latest_amendment_chain(live)
    current_ids = {r["recommendation_id"] for r in current}
    for r in live:
        if r["recommendation_id"] not in current_ids:
            excluded.append((r["recommendation_id"], "superseded by an amendment; the amendment carries it"))

    # Fills, as of the decision. A fill recorded later did not exist yet.
    filled: dict = {}
    for e in executions or []:
        if e.get("test_only"):
            continue
        when = _ts(e.get("executed_at"))
        if when is not None and when > at:
            continue
        rid = e.get("recommendation_id")
        stake = e.get("stake")
        if stake is None:
            price, contracts = e.get("actual_price"), e.get("contracts")
            stake = (float(price) * float(contracts)) if (price and contracts) else 0.0
        filled[rid] = filled.get(rid, 0.0) + float(stake)

    # SETTLEMENT RELEASES EXPOSURE ONLY AS OF A MOMENT THE OUTCOME WAS AVAILABLE.
    #
    # This is the one place where a later fact could quietly loosen an earlier limit. A position filled at
    # 13:00 settles at 20:00 and its Evaluation is written at 21:00; the twelve-hourly replay of the 15:00
    # decision then runs at 01:00 with that Evaluation in the ledger. Releasing on its mere existence would
    # let the replay approve exposure that was over the cap when the decision was actually made -- and the
    # replay is supposed to REPRODUCE the pre-trade verdict, not improve on it with hindsight.
    settled_at: dict = {}
    for ev in evaluations or []:
        if ev.get("settlement") is None or ev.get("test_only"):
            continue
        rid = ev.get("recommendation_id")
        when, basis = _settlement_available_at(ev)
        if when is None:
            # No usable provenance: the settlement is real but we cannot say when it was knowable, so it
            # releases nothing historically. Retaining exposure is the failure that costs opportunity; the
            # other one costs money.
            excluded.append((rid, "a settlement evaluation carries no usable availability timestamp "
                                  "(neither settlement_observed_at nor a parseable evaluated_at), so it "
                                  "cannot release exposure at any past decision"))
            continue
        if rid not in settled_at or when < settled_at[rid][0]:
            settled_at[rid] = (when, basis)

    positions, by_game, by_group = [], {}, {}
    for r in current:
        rid = r["recommendation_id"]
        approved = float(r.get("recommended_stake") or 0.0)
        # A fill on a superseded link is a fill on this position: the amendment revised the opinion, not the
        # money already spent under it.
        executed = float(filled.get(rid, 0.0))
        for prior in r.get("_superseded_ids") or []:
            executed += float(filled.get(prior, 0.0))

        kicked_off = False
        ko = _ts(r.get("kickoff_utc"))
        if ko is not None and ko <= release_at:
            kicked_off = True

        reserved = 0.0 if kicked_off else max(approved - executed, 0.0)

        released = settled_at.get(rid)
        is_settled = released is not None and released[0] <= release_at
        if released is not None and not is_settled:
            excluded.append((rid, f"settled, but the outcome was not available until "
                                  f"{released[0].isoformat()} ({released[1]}), after the decision being "
                                  f"evaluated; the stake is still exposure at this point in time"))
        at_risk = 0.0 if is_settled else executed
        exposure = reserved + at_risk

        if exposure <= 0:
            excluded.append((rid, "settled and fully released" if is_settled else
                             ("kicked off with nothing filled; the position can no longer be established"
                              if kicked_off else "no approved or executed stake")))
            continue

        basis = []
        if reserved > 0:
            basis.append(f"${reserved:.2f} approved and not yet filled")
        if at_risk > 0:
            basis.append(f"${at_risk:.2f} filled and unsettled")
            if released is not None:
                basis.append(f"its settlement was not available until {released[0].isoformat()}")
        positions.append(OutstandingPosition(
            recommendation_id=rid, approved_stake=round(approved, 2), executed_stake=round(executed, 2),
            reserved_stake=round(reserved, 2), at_risk_stake=round(at_risk, 2),
            exposure=round(exposure, 2), game_id=r.get("game_id"),
            correlation_group=r.get("correlation_group"), market_ticker=r.get("market_ticker"),
            basis="; ".join(basis)))
        if r.get("game_id"):
            by_game[r["game_id"]] = by_game.get(r["game_id"], 0.0) + exposure
        if r.get("correlation_group"):
            by_group[r["correlation_group"]] = by_group.get(r["correlation_group"], 0.0) + exposure

    positions.sort(key=lambda p: p.recommendation_id)
    return OutstandingExposure(
        as_of=at.isoformat(), release_as_of=release_at.isoformat(), positions=positions,
        by_game={k: round(v, 2) for k, v in sorted(by_game.items())},
        by_correlation_group={k: round(v, 2) for k, v in sorted(by_group.items())},
        total=round(sum(p.exposure for p in positions), 2),
        excluded=sorted(set(excluded)),
        source="handicap-data ledger: recommendations + executions + evaluations")


def load_outstanding(ledger_root: str, as_of, *, release_as_of=None,
                     exclude_ids=()) -> OutstandingExposure:
    """`outstanding_exposure` over the committed ledger.

    Reads the whole ledger rather than one season/week on purpose: exposure does not respect a week boundary,
    and a Thursday-night position taken in one week's directory is still money at risk on Sunday.
    """
    recs = store.read_kind(ledger_root, "recommendations")
    exes = store.read_kind(ledger_root, "executions")
    evals = store.read_kind(ledger_root, "evaluations")
    out = outstanding_exposure(recs, exes, evals, as_of, release_as_of=release_as_of,
                               exclude_ids=exclude_ids)
    out.source = f"handicap-data ledger at {ledger_root}"
    return out


def batch_window(records: list) -> tuple:
    """The earliest and latest decision timestamp in a batch of records."""
    times = sorted(t for t in (_ts(r.get("created_at")) for r in records or []) if t is not None)
    return (times[0], times[-1]) if times else (None, None)


def report_for_batch(records: list, policy: RiskPolicy, ledger_root: str | None,
                     bankroll_snapshot: float | None = None,
                     decisions=("RECOMMENDED",)) -> PortfolioReport:
    """THE portfolio verdict for a batch, against the whole book rather than the batch alone.

    This is the single entry point every caller uses -- the pre-trade preflight, the Airtable importer, and
    the manual write path -- so there is exactly one definition of "does this fit within the limits". A
    second implementation of the cap arithmetic that read only the batch is the defect this replaces.

    `ledger_root` of None means the committed exposure could not be read. That is not treated as zero: the
    caller gets a report whose `outstanding` says so, and the gate that consumes it should refuse rather
    than assume an empty book.
    """
    live = [r for r in records if r.get("decision") in decisions and not r.get("test_only")]
    if not live:
        return policy.evaluate([], bankroll_snapshot or 1.0, EMPTY_EXPOSURE)

    earliest, latest = batch_window(live)
    if latest is None:
        raise RiskPolicyError(
            "no record in the batch carries a parseable created_at; cumulative exposure is measured at the "
            "decision timestamp and cannot be measured without one")

    if ledger_root is None:
        outstanding = OutstandingExposure(
            as_of=latest.isoformat(), release_as_of=(earliest or latest).isoformat(),
            source="UNAVAILABLE: no ledger root supplied, so committed exposure could not be read")
    else:
        outstanding = load_outstanding(
            ledger_root, latest, release_as_of=earliest,
            exclude_ids={r.get("recommendation_id") for r in live})

    return evaluate_records(live, policy, bankroll_snapshot, decisions, outstanding=outstanding)
