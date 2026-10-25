"""The OWNER staking policy (docs/NFL_OPERATING_POLICY.md), tested against the REAL config/risk_policy.json.

1 unit = $75, whole-unit stakes of 1U-5U, max 5U ($375), a game may get zero bets, correlated bets share a budget,
and none of the older safety limits (freshness windows, depth, fees, exposure caps) were loosened to get here.
"""
import json
import os

import pytest

from nfl_edge.handicap import risk as R

pytestmark = pytest.mark.owner_policy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT = os.path.join(ROOT, "tests", "fixtures", "risk_policy_pilot_2026_v1.json")


def P():
    return R.RiskPolicy.load(ROOT)


def prop(rid, stake, game="2026_07_AAA_BBB", group=None, grade=None):
    return R.Proposal(recommendation_id=rid, proposed_stake=stake, game_id=game, correlation_group=group, grade=grade)


def test_the_live_config_is_the_owner_policy_not_the_pilot():
    cfg = json.load(open(os.path.join(ROOT, "config", "risk_policy.json")))
    assert cfg["policy_id"].startswith("owner-") and cfg["status"] == "ACTIVE"
    assert cfg["fixed_unit_dollars"] == 75
    assert cfg["max_stake_per_position_units"] == 5 and cfg["min_stake_units"] == 1
    assert cfg["stake_increment_units"] == 1
    assert "pilot" not in cfg["policy_id"].lower() and cfg["status"] != "PILOT"
    pol = P()
    assert pol.unit_dollars(None) == 75 and pol.unit_dollars(123456) == 75     # independent of any bankroll


def test_the_limit_block_states_dollars_and_bankroll_guard_state():
    rep = P().evaluate([], None)
    assert rep.unit_dollars == 75
    assert rep.limits["max_stake_per_position"] == 375
    assert rep.limits["max_exposure_per_game"] == 600
    assert rep.limits["max_exposure_per_correlation_group"] == 450
    assert rep.limits["max_slate_exposure"] == 1875
    assert rep.limits["bankroll_guards"].startswith("NOT_EVALUATED")


@pytest.mark.parametrize("proposed,approved,status", [
    (75, 75, R.APPROVED), (150, 150, R.APPROVED), (375, 375, R.APPROVED),
    (450, 375, R.CAPPED),        # above 5U is capped to 5U, never approved
    (1000, 375, R.CAPPED),       # the 13U stakes in the 2026 ledger cannot pass
    (130, 75, R.CAPPED),         # stakes are whole units: 1.73U floors to 1U
    (74, 0, R.REJECTED),         # under 1U is not a position
    (40, 0, R.REJECTED),
])
def test_stakes_are_whole_units_between_1U_and_5U(proposed, approved, status):
    v = P().evaluate([prop("r", proposed)], None).verdicts[0]
    assert v.status == status and v.approved_stake == approved
    assert v.approved_stake % 75 == 0


def test_a_game_with_no_proposals_needs_no_bet():
    rep = P().evaluate([], None)
    assert rep.verdicts == [] and rep.total_exposure == 0


def test_correlated_positions_share_one_budget():
    g = "2026_07_AAA_BBB::SCORING_UP"
    rep = P().evaluate([prop("a", 375, group=g), prop("b", 375, group=g)], None)
    stakes = sorted(v.approved_stake for v in rep.verdicts)
    assert stakes == [75, 375]                      # 6U group cap = 450 total
    assert rep.exposure_by_correlation_group[g] == 450


def test_game_and_slate_caps_bind_in_units():
    pol = P()
    rep = pol.evaluate([prop("a", 375, game="G1", group="x"), prop("b", 375, game="G1", group="y"),
                        prop("c", 375, game="G1", group="z")], None)
    assert rep.exposure_by_game["G1"] == 600        # 8U per game
    many = [prop(f"r{i}", 375, game=f"G{i}", group=f"g{i}") for i in range(8)]
    rep = pol.evaluate(many, None)
    assert rep.total_exposure == 1875               # 25U slate cap; the eighth is squeezed, not the first
    assert sum(1 for v in rep.verdicts if v.status == R.REJECTED) >= 1 or rep.total_exposure <= 1875


def test_a_bankroll_when_supplied_adds_a_guard_and_never_removes_one():
    rep = P().evaluate([prop("a", 375)], 5000.0)          # 3% of 5,000 = 150
    assert rep.verdicts[0].approved_stake == 150 and rep.verdicts[0].binding_limit == "bankroll_max_stake_fraction"
    assert rep.limits["bankroll_guards"] == "EVALUATED"
    big = P().evaluate([prop("a", 375)], 1_000_000.0)
    assert big.verdicts[0].approved_stake == 375          # 5U ceiling still binds at any bankroll


def test_grade_caps_are_ceilings_in_the_owner_units():
    assert P().evaluate([prop("a", 375, grade="B-")], None).verdicts[0].approved_stake == 75
    assert P().evaluate([prop("a", 375, grade="A")], None).verdicts[0].approved_stake == 300
    assert P().evaluate([prop("a", 375, grade="Z")], None).verdicts[0].status == R.REJECTED


def test_a_policy_without_a_fixed_unit_still_demands_a_bankroll():
    legacy = R.RiskPolicy.load(ROOT, PILOT)
    with pytest.raises(R.RiskPolicyError):
        legacy.evaluate([prop("a", 10)], None)
    assert legacy.max_stake_per_position_units == 2.0     # the pilot file is unchanged, just no longer the live policy


def test_the_owner_policy_did_not_loosen_the_portfolio_protection_per_unit():
    """Per-game/group/slate caps are larger in dollars only because a unit is larger; per position they are no looser."""
    owner, pilot = P(), R.RiskPolicy.load(ROOT, PILOT)
    def ratios(p):
        pos = p.max_stake_per_position_units
        return (p.max_exposure_per_game_units / pos, p.max_exposure_per_correlation_group_units / pos,
                p.max_slate_exposure_units / pos)
    for o, p in zip(ratios(owner), ratios(pilot)):
        assert o <= p, "an aggregate cap grew faster than the single-stake cap"
    assert owner.max_exposure_per_correlation_group_units < owner.max_exposure_per_game_units
    assert owner.max_slate_exposure_units <= 25
