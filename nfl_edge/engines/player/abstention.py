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

ARMS_NEEDING_LADDER = ("MARKET_PLAYER_DIST", "HYBRID_PLAYER_DIST", "HYBRID_PLAYER_V3", "HYBRID_PLAYER_V4")
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


# --------------------------------------------------------------------------------------------------------- V4
# DATA_PLAYER_V4 / HYBRID_PLAYER_V4 carry their own structural uncertainty (nfl_edge/engines/player/v4), so their
# abstention can say WHICH upstream quantity is unknown, not only that the context is thin. Thresholds are set
# before any scoring and are not fitted: a predicted snap-share sd above 0.15 is wider than the typical error of a
# stable starter's EWMA; a 10% vacated same-group share is a role shock by any reading of the 2014-2024 absence data.
ABSTENTION_V4_VERSION = "abstention-v4-1.0.0"
ABSTAIN_SNAP_UNCERTAIN = "ABSTAIN_SNAP_UNCERTAIN"
ABSTAIN_TEAMMATE_SHOCK = "ABSTAIN_TEAMMATE_SHOCK"
ABSTAIN_EXTRAPOLATION = "ABSTAIN_EXTRAPOLATION"
STATES_V4 = STATES + (ABSTAIN_SNAP_UNCERTAIN, ABSTAIN_TEAMMATE_SHOCK, ABSTAIN_EXTRAPOLATION)
SNAP_SD_MAX = 0.15
VACATED_SHOCK = 0.10
MIN_SNAP_SUPPORT = 0.15


def decide_v4(inter: dict, *, stat: str | None, p_model: float | None, p_market: float | None, arm: str = "DATA_PLAYER_V4",
              engine_version: str | None = None, identity_confidence: str | None = "RESOLVED", availability_state: str | None = None,
              role_certainty: str | None = None, game_env_known: bool = True, qb_starter_known: bool | None = True,
              ladder_identification: str | None = "IDENTIFIED") -> dict:
    """The v4 state from the model's own intermediates (snap sd, teammate vacated share, role transition flags) plus the
    shared context facts. `structural_state` ignores the MODEL_UNVALIDATED stamp so research can score the rule itself."""
    reasons = []
    if identity_confidence not in ("RESOLVED",):
        reasons.append((ABSTAIN_IDENTITY, f"identity {identity_confidence or 'UNRESOLVED'}"))
    # availability_state None = not supplied (research replays); "UNKNOWN" = supplied and unknown, which is never "healthy"
    av = (availability_state or "").upper()
    if inter.get("own_q") or inter.get("own_d") or av in ADVERSE_AVAILABILITY:
        reasons.append((ABSTAIN_INJURY_UNCERTAIN, f"own designation {'QUESTIONABLE' if inter.get('own_q') else av or 'DOUBTFUL'}"))
    if role_certainty in ("LOW", "UNKNOWN") or inter.get("self_new") or inter.get("changed_team") or inter.get("self_returning"):
        why = ("new to the team" if inter.get("self_new") else "changed team" if inter.get("changed_team") else
               "returning from absence" if inter.get("self_returning") else f"role certainty {role_certainty}")
        reasons.append((ABSTAIN_ROLE_UNCERTAIN, why))
    vac = max(float(inter.get("vac_same_t") or 0.0), float(inter.get("vac_same_c") or 0.0))
    if vac >= VACATED_SHOCK:
        reasons.append((ABSTAIN_TEAMMATE_SHOCK, f"{vac:.0%} of the group's opportunity vacated this week"))
    sd = inter.get("snap_sd")
    if sd is not None and sd == sd and sd > SNAP_SD_MAX:
        reasons.append((ABSTAIN_SNAP_UNCERTAIN, f"predicted snap-share sd {sd:.2f} > {SNAP_SD_MAX}"))
    sm = inter.get("snap_mean")
    if sm is not None and sm == sm and sm < MIN_SNAP_SUPPORT:
        reasons.append((ABSTAIN_EXTRAPOLATION, f"predicted snap share {sm:.2f} below the {MIN_SNAP_SUPPORT} support of the rung population"))
    if not game_env_known:
        reasons.append((ABSTAIN_VOLUME_UNCERTAIN, "no market-implied game environment at the cutoff"))
    if stat in QB_STATS and not qb_starter_known:
        reasons.append((ABSTAIN_VOLUME_UNCERTAIN, "no point-in-time starting quarterback"))
    if arm.startswith("HYBRID") and ladder_identification in (None, "NONE", "UNDERIDENTIFIED"):
        reasons.append((ABSTAIN_MARKET_INCOMPLETE, f"ladder {ladder_identification or 'absent'}"))
    dis = None if (p_model is None or p_market is None) else 100.0 * (float(p_model) - float(p_market))
    large = dis is not None and abs(dis) > LARGE_DISAGREEMENT_PP
    structural = [r for r in reasons] + ([(PROJECTION_LOW_CONFIDENCE, f"|model - market| = {abs(dis):.1f}pp")] if large else [])
    unvalidated = (engine_version, stat) not in VALIDATED_STATS
    full = list(reasons)
    if unvalidated:
        full.append((ABSTAIN_MODEL_UNVALIDATED, f"{engine_version}/{stat} has no prospective evidence of matching the market"))
    if large:
        full.append((PROJECTION_LOW_CONFIDENCE, f"|model - market| = {abs(dis):.1f}pp > {LARGE_DISAGREEMENT_PP:.0f}pp"))
    state = full[0][0] if full else PROJECTION_VALID
    return {"abstention_version": ABSTENTION_V4_VERSION, "state": state, "production_eligible": state == PROJECTION_VALID,
            "structural_state": structural[0][0] if structural else PROJECTION_VALID,
            "reasons": [f"{s}: {why}" for s, why in full], "large_disagreement": large}


# --------------------------------------------------------------------------------------------------------- V5
# DATA_PLAYER_V5 / HYBRID_PLAYER_V5 (nfl_edge/engines/player/v5) are V4's structure with a point-in-time projected
# starting quarterback (nfl_edge/context/qb_resolution.py). Their abstention is V4's, unchanged, plus ONE reason: the
# resolution itself said the team's passing environment is not known well enough -- chart QB1 Doubtful
# (QB1_DOUBTFUL_ABSTAIN), QB1 out with no eligible QB behind him, no chart QB1, or a chart that post-dated the cutoff
# -- and the statistic runs through that environment (qb_resolution.is_qb_dependent: every QB statistic, a
# pass-catcher's receptions / receiving yards / rush+rec yards, a WR / TE anytime TD). A Questionable QB1 is retained
# and flagged LOW, not abstained. Like every abstention the probability stays on the record; only authority goes.
ABSTENTION_V5_VERSION = "abstention-v5-1.0.0"
ABSTAIN_QB_UNCERTAIN = "ABSTAIN_QB_UNCERTAIN"
STATES_V5 = STATES_V4 + (ABSTAIN_QB_UNCERTAIN,)
_AFTER_QB = (ABSTAIN_MARKET_INCOMPLETE, ABSTAIN_MODEL_UNVALIDATED, PROJECTION_LOW_CONFIDENCE)


def decide_v5(inter: dict, *, stat: str | None, p_model: float | None, p_market: float | None, arm: str = "DATA_PLAYER_V5",
              engine_version: str | None = None, identity_confidence: str | None = "RESOLVED", availability_state: str | None = None,
              role_certainty: str | None = None, game_env_known: bool = True, position: str | None = None,
              ladder_identification: str | None = "IDENTIFIED") -> dict:
    """decide_v4 on the V5 intermediates, with the point-in-time quarterback (not the raw chart QB1) as the starting
    quarterback, plus ABSTAIN_QB_UNCERTAIN where the resolution abstained and the statistic depends on the QB."""
    from nfl_edge.context import qb_resolution as QR
    base = decide_v4(inter, stat=stat, p_model=p_model, p_market=p_market, arm=arm, engine_version=engine_version,
                     identity_confidence=identity_confidence, availability_state=availability_state, role_certainty=role_certainty,
                     game_env_known=game_env_known, qb_starter_known=bool(inter.get("effective_projected_qb")),
                     ladder_identification=ladder_identification)
    pos = position or inter.get("pgroup")
    full = [tuple(r.split(": ", 1)) for r in base["reasons"]]
    if inter.get("qb_dependent_abstain") and QR.is_qb_dependent(stat, pos):
        why = (f"{inter.get('qb_resolution_reason')}: the team's quarterback is not resolvable at the cutoff "
               f"(chart QB1 {inter.get('qb_availability_state')})")
        i = next((j for j, (s, _) in enumerate(full) if s in _AFTER_QB), len(full))
        full.insert(i, (ABSTAIN_QB_UNCERTAIN, why))
    structural = [r for r in full if r[0] != ABSTAIN_MODEL_UNVALIDATED]
    state = full[0][0] if full else PROJECTION_VALID
    return {"abstention_version": ABSTENTION_V5_VERSION, "state": state, "production_eligible": state == PROJECTION_VALID,
            "structural_state": structural[0][0] if structural else PROJECTION_VALID,
            "reasons": [f"{s}: {why}" for s, why in full], "large_disagreement": base["large_disagreement"],
            "qb_resolution": {k: inter.get(k) for k in ("depth_chart_qb1", "effective_projected_qb", "qb_availability_state",
                                                        "qb_resolution_reason", "qb_resolution_certainty")}}
