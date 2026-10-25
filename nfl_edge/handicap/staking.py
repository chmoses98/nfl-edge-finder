"""The stake ladder: how many units (1U-5U, 1U = $75) an accepted candidate may carry, and what stops it carrying more.

The owner's rule (docs/NFL_OPERATING_POLICY.md): stakes are whole units from 1U to 5U; a highly confident recommendation may carry
a larger stake, but the confidence must be DEFENSIBLE; and unvalidated model disagreement alone never justifies an aggressive stake.

So the ladder is written as evidence requirements, tier by tier, and a candidate gets the HIGHEST tier whose every requirement it
meets. It never gets a larger stake because an estimate is large. Requirements are on the CONSERVATIVE end of the fair-value range
(`fair_low`, after the engine's own noise buffer), net of fees, at the price actually payable:

  tier  needs, in addition to the tier below
  ----  ---------------------------------------------------------------------------------------------------------------
  1U    a complete thesis; every independent-challenge item answered and none open; net edge at fair_low >= 2.0c per contract;
        the full stake executable in the displayed book; price at or under the ceiling
  2U    net edge at fair_low >= 4.0c; the thesis survives >= 3 distinct plausible game scripts (or is script-neutral by
        construction, e.g. a pure game-environment contract) AND does not depend on a single script; fair range no wider than 0.20
  3U    net edge at fair_low >= 5.5c; ONE independent corroboration from the list below
  4U    net edge at fair_low >= 7.0c; TWO independent corroborations; the contract's market family is at least LIMITED in
        docs/PRODUCTION_ELIGIBILITY.md
  5U    net edge at fair_low >= 9.0c; THREE corroborations; the family is TRUSTED. Unreachable today BY DESIGN: no arm or family
        is TRUSTED, and nothing here will invent that

Independent corroborations (each counts once, must be independent of the thesis's own evidence, and must name its source):
  INCUMBENT_AGREES      the deployed incumbent prices the same contract, agrees in direction after fees, and the family is WATCH or better
  LINE_MOVE_TOWARD_US   the market has moved toward our side since the first capture by at least 1c with the book still two-sided
  REPLAY_SEGMENT        the historical replay (docs/research/STRATEGY_REPLAY) shows non-negative net ROI AND non-negative CLV in this
                        family and price bucket with a game-clustered lower bound not below -5%
  TACTICAL_DATA         a measured (not hypothesised) tactical or availability fact that the market price has not moved for

NOT corroborations, by rule: Shadow v2 or any research arm, the coherent simulation, a model-market disagreement of any size, the
analyst's own confidence.

Caps that apply at every tier: a model-market disagreement above 10 points on the contract caps it at 1U (on every family the
repository has scored, the market won where the football-only model disagreed by more than 0.10); a fair range wider than 0.20 steps
the tier down by one; a candidate that shares a thesis driver with an accepted candidate shares that driver's budget (risk policy
correlation-group cap); and the risk policy's own game/slate/bankroll caps are applied afterwards by `risk.RiskPolicy`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

STAKING_VERSION = "staking-1.0.0"
UNIT_DOLLARS = 75

#: tier -> (min net edge at fair_low in probability units, corroborations needed, min family eligibility, min distinct winning scripts)
TIERS = {
    1: (0.020, 0, None, 0),
    2: (0.040, 0, None, 3),
    3: (0.055, 1, None, 3),
    4: (0.070, 2, "LIMITED", 3),
    5: (0.090, 3, "TRUSTED", 3),
}
ELIGIBILITY_RANK = {None: 0, "DISABLED": -1, "RESEARCH_ONLY": 0, "WATCH": 1, "LIMITED": 2, "TRUSTED": 3}
CORROBORATIONS = ("INCUMBENT_AGREES", "LINE_MOVE_TOWARD_US", "REPLAY_SEGMENT", "TACTICAL_DATA")
MAX_FAIR_WIDTH = 0.20
LARGE_DISAGREEMENT = 0.10


@dataclass
class StakeInputs:
    net_edge_low: float | None                 # per contract, after fees, at the payable price, using fair_low
    fair_low: float | None
    fair_high: float | None
    challenge_clear: bool
    full_stake_executable: bool
    price_within_ceiling: bool
    winning_scripts: int = 0                   # distinct plausible scripts in which the contract wins
    script_neutral: bool = False
    single_script_dependent: bool = False
    corroborations: tuple = ()
    family_eligibility: str | None = None
    model_market_gap: float | None = None      # |incumbent model - market mid| on this contract, when the incumbent prices it
    flags: tuple = ()


@dataclass
class StakeDecision:
    units: int
    tier: str
    unmet: list = field(default_factory=list)       # what stopped the next tier up, in plain words
    blocked: list = field(default_factory=list)     # why the answer is zero units
    notes: list = field(default_factory=list)

    @property
    def dollars(self) -> int:
        return self.units * UNIT_DOLLARS

    def to_dict(self) -> dict:
        return {"units": self.units, "dollars": self.dollars, "tier": self.tier, "unmet_for_next_tier": self.unmet,
                "blocked": self.blocked, "notes": self.notes, "version": STAKING_VERSION}


def decide(x: StakeInputs) -> StakeDecision:
    blocked = []
    if not x.challenge_clear:
        blocked.append("independent challenge not cleared")
    if not x.full_stake_executable:
        blocked.append("the full stake is not executable in the displayed book")
    if not x.price_within_ceiling:
        blocked.append("the payable price is above the ceiling")
    if x.net_edge_low is None or x.fair_low is None:
        blocked.append("no defensible fair-value range, or fees not established")
    elif x.net_edge_low < TIERS[1][0]:
        blocked.append(f"net edge at the conservative end is {x.net_edge_low * 100:+.1f}c per contract, under the 2.0c minimum")
    if blocked:
        return StakeDecision(0, "NONE", blocked=blocked)

    corr = sorted(set(c for c in x.corroborations if c in CORROBORATIONS))
    best, unmet = 1, []
    for tier in (2, 3, 4, 5):
        need_edge, need_corr, need_elig, need_scripts = TIERS[tier]
        miss = []
        if x.net_edge_low < need_edge:
            miss.append(f"{tier}U needs net edge >= {need_edge * 100:.1f}c at fair_low (have {x.net_edge_low * 100:.1f}c)")
        if len(corr) < need_corr:
            miss.append(f"{tier}U needs {need_corr} independent corroboration(s) (have {len(corr)})")
        if ELIGIBILITY_RANK.get(x.family_eligibility, 0) < ELIGIBILITY_RANK.get(need_elig, 0):
            miss.append(f"{tier}U needs the market family at {need_elig} or better in production eligibility (have {x.family_eligibility or 'none'})")
        if need_scripts and not x.script_neutral and x.winning_scripts < need_scripts:
            miss.append(f"{tier}U needs the contract to win in >= {need_scripts} plausible scripts (have {x.winning_scripts})")
        if tier >= 2 and x.single_script_dependent:
            miss.append(f"{tier}U is not available to a thesis that depends on a single game script")
        if miss:
            unmet = miss
            break
        best = tier

    notes = []
    if x.fair_high is not None and x.fair_low is not None and (x.fair_high - x.fair_low) > MAX_FAIR_WIDTH and best > 1:
        best -= 1
        notes.append(f"fair range is {x.fair_high - x.fair_low:.2f} wide (> {MAX_FAIR_WIDTH}): stepped down one tier")
    if x.model_market_gap is not None and x.model_market_gap > LARGE_DISAGREEMENT and best > 1:
        best = 1
        notes.append(f"model-market gap {x.model_market_gap:.2f} exceeds {LARGE_DISAGREEMENT}: capped at 1U "
                     "(the market won where the football-only model disagreed by more than 0.10 on every scored family)")
    if "DISAGREEMENT_ONLY" in x.flags:
        return StakeDecision(0, "NONE", blocked=["the only support is a model-market disagreement; that is not a thesis"])
    return StakeDecision(best, f"{best}U", unmet=unmet, notes=notes)
