"""The OWNER staking policy (docs/NFL_OPERATING_POLICY.md), tested against the REAL config/risk_policy.json.

1 unit = $75, whole-unit stakes of 1U-5U, max 5U ($375), a game may get zero bets, correlated bets share a budget,
no slate or per-game caps, and a maximum 5U shared budget per correlated thesis. Price, liquidity and bankroll guards still apply.
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
    assert rep.limits["max_exposure_per_game"] is None
    assert rep.limits["max_exposure_per_correlation_group"] == 375
    assert rep.limits["max_slate_exposure"] is None
    assert rep.limits["slate_binding_limit"] is None
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
    rep = P().evaluate([prop("a", 225, group=g), prop("b", 225, group=g)], None)
    stakes = sorted(v.approved_stake for v in rep.verdicts)
    assert stakes == [150, 225]                    # total stays at 5U = $375
    assert rep.exposure_by_correlation_group[g] == 375


def test_independent_theses_are_not_blocked_by_game_or_slate_caps():
    pol = P()
    same_game = [prop(f"r{i}", 375, game="G1", group=f"G1::different-thesis-{i}") for i in range(3)]
    rep = pol.evaluate(same_game, None)
    assert rep.exposure_by_game["G1"] == 1125    # 15U, no same-game cap
    assert all(v.status == R.APPROVED for v in rep.verdicts)
    many = [prop(f"r{i}", 375, game=f"G{i}", group=f"G{i}::independent") for i in range(8)]
    rep = pol.evaluate(many, None)
    assert rep.total_exposure == 3000            # 40U, no slate cap
    assert all(v.status == R.APPROVED for v in rep.verdicts)


def test_outstanding_exposure_still_consumes_the_shared_thesis_budget():
    g = "G1::SHARED"
    outstanding = R.OutstandingExposure(by_game={"G1": 225}, by_correlation_group={g: 225},
                                        total=225, source="fixture")
    rep = P().evaluate([prop("new", 225, game="G1", group=g)], None, outstanding=outstanding)
    v = rep.verdicts[0]
    assert v.status == R.CAPPED and v.approved_stake == 150
    assert rep.exposure_by_correlation_group[g] == 375


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


def test_only_correlated_thesis_budget_remains_an_aggregate_cap():
    pol = P()
    assert pol.max_exposure_per_game_units is None
    assert pol.max_slate_exposure_units is None
    assert pol.max_slate_exposure_fraction_of_bankroll is None
    assert pol.max_exposure_per_correlation_group_units == 5
    assert pol.max_stake_per_position_units == 5


def test_the_authoritative_document_matches_the_config_and_every_other_workflow_doc_points_to_it():
    cfg = json.load(open(os.path.join(ROOT, "config", "risk_policy.json")))
    doc = open(os.path.join(ROOT, "docs", "NFL_OPERATING_POLICY.md")).read()
    assert f"${cfg['fixed_unit_dollars']}" in doc and "1U to 5U" in doc and "$375" in doc
    assert "per correlation group | 5U" in doc
    assert "per slate | None" in doc
    assert "per game (combined) | None" in doc
    for rel in ("RUN_NFL.md", "DECISION_STANDARD.md", "PREFLIGHT.md", "OPERATIONS.md", "AIRTABLE_BRIDGE.md"):
        assert "NFL_OPERATING_POLICY.md" in open(os.path.join(ROOT, "docs", rel)).read(), rel
    assert "NFL_OPERATING_POLICY.md" in open(os.path.join(ROOT, "README.md")).read()


def test_the_superseded_pilot_values_are_labelled_as_superseded_wherever_they_remain():
    ds = open(os.path.join(ROOT, "docs", "DECISION_STANDARD.md")).read()
    assert "superseded" in ds.split("### The limits")[1].split("### Correlation")[0].lower()


def test_each_stake_tier_maps_to_a_grade_whose_cap_admits_exactly_that_many_units():
    from nfl_edge.handicap import card as C
    pol = P()
    for units in (1, 2, 3, 4, 5):
        v = pol.evaluate([prop("r", units * 75, grade=C.UNITS_TO_GRADE[units])], None).verdicts[0]
        assert v.status == R.APPROVED and v.approved_stake == units * 75, (units, v.to_dict())
