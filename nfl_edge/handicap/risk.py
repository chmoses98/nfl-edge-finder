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
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

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
        """Round DOWN to whole dollars. A risk cap that rounds up is not a cap."""
        if not self.round_stakes_to_dollars:
            return round(stake, 2)
        return float(math.floor(stake + 1e-9))

    # ---- the decision ---------------------------------------------------------------------------
    def evaluate(self, proposals: list, bankroll_snapshot: float) -> PortfolioReport:
        """Cap every proposal against position, grade, game, correlation-group and slate limits.

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

        game_used: dict = {}
        group_used: dict = {}
        total_used = 0.0

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
                room = self.max_exposure_per_game_units * unit - game_used.get(p.game_id, 0.0)
                tighten(max(room, 0.0), "max_exposure_per_game_units",
                        f"game {p.game_id} aggregate cap {self.max_exposure_per_game_units}u")

            if p.correlation_group:
                room = (self.max_exposure_per_correlation_group_units * unit
                        - group_used.get(p.correlation_group, 0.0))
                tighten(max(room, 0.0), "max_exposure_per_correlation_group_units",
                        f"correlation group {p.correlation_group} cap "
                        f"{self.max_exposure_per_correlation_group_units}u")

            tighten(max(slate_cap - total_used, 0.0), slate_limit_name,
                    f"slate aggregate cap ({slate_limit_name})")

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

        report.exposure_by_game = {k: round(v, 2) for k, v in sorted(game_used.items())}
        report.exposure_by_correlation_group = {k: round(v, 2) for k, v in sorted(group_used.items())}
        report.total_exposure = round(total_used, 2)
        return report


def evaluate_records(records: list, policy: RiskPolicy, bankroll_snapshot: float | None = None,
                     decisions=("RECOMMENDED",)) -> PortfolioReport:
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
    return policy.evaluate([Proposal.from_record(r) for r in live], bankroll_snapshot)
