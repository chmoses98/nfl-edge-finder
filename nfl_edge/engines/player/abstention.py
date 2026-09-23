"""ABSTENTION for player projections: a model that knows when it does not know.

Every player projection gets exactly one state, decided in a fixed order from facts frozen on the record:

    ABSTAIN_IDENTITY            the Kalshi player is not confidently the nflverse player we modelled
    ABSTAIN_INJURY_UNCERTAIN    the player's own availability is Questionable / Doubtful / Out / Unknown
    ABSTAIN_ROLE_UNCERTAIN      role certainty LOW or UNKNOWN (nfl_edge/context/role.py): chart missing or
                                contradicting usage, team change, a teammate ahead of him Out, no usage at all
    ABSTAIN_VOLUME_UNCERTAIN    the team-volume inputs are not trustworthy: no market-implied game environment,
                                or a quarterback statistic with no point-in-time starting quarterback
    ABSTAIN_MARKET_INCOMPLETE   an arm that needs the market ladder, and the ladder is NONE / UNDERIDENTIFIED
    ABSTAIN_MODEL_UNVALIDATED   the (arm, statistic) has no historical evidence of being within tolerance of
                                the market (`VALIDATED_STATS`); the projection is research, never an input
    PROJECTION_LOW_CONFIDENCE   everything above passed, but the model disagrees with the market by more than
                                LARGE_DISAGREEMENT_PP -- measured, on 2026 weeks 1-2, to be where the model is
                                WORST, not where it is best. Large disagreement is a warning, not an edge.
    PROJECTION_VALID            none of the above

`production_eligible` is True only for PROJECTION_VALID, and even then the arm's own production-eligibility
status (nfl_edge/evaluation/eligibility.py) decides whether the projection may influence anything. The
probability is NOT withheld from the record: an abstained projection is still scored prospectively, which is the
only way to learn whether the abstention rule itself is right. What is withheld is authority.
"""
from __future__ import annotations

ABSTENTION_VERSION = "abstention-1.0.0"

PROJECTION_VALID = "PROJECTION_VALID"
PROJECTION_LOW_CONFIDENCE = "PROJECTION_LOW_CONFIDENCE"
ABSTAIN_IDENTITY = "ABSTAIN_IDENTITY"
ABSTAIN_INJURY_UNCERTAIN = "ABSTAIN_INJURY_UNCERTAIN"
ABSTAIN_ROLE_UNCERTAIN = "ABSTAIN_ROLE_UNCERTAIN"
ABSTAIN_VOLUME_UNCERTAIN = "ABSTAIN_VOLUME_UNCERTAIN"
ABSTAIN_MARKET_INCOMPLETE = "ABSTAIN_MARKET_INCOMPLETE"
ABSTAIN_MODEL_UNVALIDATED = "ABSTAIN_MODEL_UNVALIDATED"
STATES = (PROJECTION_VALID, PROJECTION_LOW_CONFIDENCE, ABSTAIN_IDENTITY, ABSTAIN_INJURY_UNCERTAIN, ABSTAIN_ROLE_UNCERTAIN,
          ABSTAIN_VOLUME_UNCERTAIN, ABSTAIN_MARKET_INCOMPLETE, ABSTAIN_MODEL_UNVALIDATED)

# Where large model-market disagreement starts to mean "the model is missing something" rather than "the model
# knows something". Two independent samples agree:
#   2025 Kalshi rungs, HELD OUT (DATA_PLAYER_V3 fitted <= 2024, T-90m, game-clustered; research/player_engine_v3):
#       |d| < 2pp  ~ market (-0.0001..-0.0005);  3-5pp +0.0011 +/- 0.0008;  5-10pp +0.0045 +/- 0.0014;
#       > 10pp  +0.0295 +/- 0.0045
#   2026 week 2, prospective, all arms: 5-10pp +0.0060 +/- 0.0020;  > 10pp +0.0474 +/- 0.0122
# Set at 5pp, the lower edge of the first band that is measurably worse in BOTH. A guard, not a fitted parameter;
# reviewed only through the eligibility layer, never tuned to a week.
LARGE_DISAGREEMENT_PP = 5.0

# (arm engine version, statistic) pairs whose historical evidence puts them within tolerance of the market. EMPTY
# by construction today: on the 2025 Kalshi rungs no data-arm statistic beat or matched the market (research/
# player_engine_v3/RESULTS.md). A statistic enters this set only through the eligibility promotion rules.
VALIDATED_STATS: frozenset = frozenset()

ARMS_NEEDING_LADDER = ("MARKET_PLAYER_DIST", "HYBRID_PLAYER_DIST", "HYBRID_PLAYER_V3")
QB_STATS = ("passing_yards", "passing_tds", "interceptions", "attempts", "completions", "qb_rushing_yards")
ADVERSE_AVAILABILITY = ("QUESTIONABLE", "DOUBTFUL", "EXPECTED_OUT", "OUT", "INACTIVE_CONFIRMED", "UNKNOWN")


def decide(*, arm: str, engine_version: str | None, stat: str | None, identity_confidence: str | None,
           availability_state: str | None, role_certainty: str | None, game_env_known: bool,
           qb_starter_known: bool | None, ladder_identification: str | None, disagreement_pp: float | None,
           market_arm: bool = False) -> dict:
    """One state + every reason that applied (the first in order is the state; the rest are kept for research)."""
    reasons = []
    if identity_confidence not in ("RESOLVED",):
        reasons.append((ABSTAIN_IDENTITY, f"identity {identity_confidence or 'UNRESOLVED'}"))
    av = (availability_state or "UNKNOWN").upper()
    if av in ADVERSE_AVAILABILITY:
        reasons.append((ABSTAIN_INJURY_UNCERTAIN, f"availability {av}"))
    if not market_arm:
        if role_certainty not in ("HIGH", "MEDIUM"):
            reasons.append((ABSTAIN_ROLE_UNCERTAIN, f"role certainty {role_certainty or 'UNKNOWN'}"))
        if not game_env_known:
            reasons.append((ABSTAIN_VOLUME_UNCERTAIN, "no market-implied game environment at the cutoff"))
        if stat in QB_STATS and not qb_starter_known:
            reasons.append((ABSTAIN_VOLUME_UNCERTAIN, "no point-in-time starting quarterback"))
    if arm in ARMS_NEEDING_LADDER and ladder_identification in (None, "NONE", "UNDERIDENTIFIED"):
        reasons.append((ABSTAIN_MARKET_INCOMPLETE, f"ladder {ladder_identification or 'absent'}"))
    if not market_arm and (engine_version, stat) not in VALIDATED_STATS:
        reasons.append((ABSTAIN_MODEL_UNVALIDATED, f"{engine_version}/{stat} has no historical evidence of matching the market"))
    if disagreement_pp is not None and abs(disagreement_pp) > LARGE_DISAGREEMENT_PP:
        reasons.append((PROJECTION_LOW_CONFIDENCE, f"|model - market| = {abs(disagreement_pp):.1f}pp > {LARGE_DISAGREEMENT_PP:.0f}pp"))
    state = reasons[0][0] if reasons else PROJECTION_VALID
    return {"abstention_version": ABSTENTION_VERSION, "state": state, "production_eligible": state == PROJECTION_VALID,
            "reasons": [f"{s}: {why}" for s, why in reasons], "large_disagreement": any(s == PROJECTION_LOW_CONFIDENCE for s, _ in reasons)}
