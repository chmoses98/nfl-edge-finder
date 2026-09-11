"""Horizon quality classes and the status flags every projection record carries.

HORIZON QUALITY (Part 17): a T-24h snapshot taken 40 minutes late is not a T-24h snapshot. Every record with a
horizon carries target, observation and generation timestamps, the lateness of each, and a class:

    ON_TIME          market observed within LATE_ACCEPTABLE_MIN of the target instant
    LATE_ACCEPTABLE  observed later than that but within LATE_DEGRADED_MIN
    LATE_DEGRADED    later still, but before kickoff (kept, segmentable, never pooled silently with ON_TIME)
    MISSED           no pre-kickoff observation for the horizon (the marker says so; no record is written)
    CYCLE            not a canonical horizon (the 2-hourly cycle)

STATUS FLAGS (Part 20): a research probability must never sound like production support. Eight booleans that
answer different questions and are never collapsed:

    has_probability          a p_yes was written (PRICED or PROJECTABLE_NOT_YET_VALIDATED)
    semantics_proven         the question is PROVEN (not LIKELY)
    identity_resolved        the subject maps to a canonical id (team code or GSIS id) -- teams always; players per map
    settlement_supported     the family has a settlement branch in settle_v2 / settle (catalog SUPPORTED)
    historically_validated   the engine has a historical study behind it for this family (research/ ...)
    prospectively_validated  ALWAYS False on this branch: zero prospective evidence exists before merge
    execution_supported      ALWAYS False: v2 has no execution path
    betting_authorized       ALWAYS False: v2 has no real-money authority
"""
from __future__ import annotations

from datetime import datetime, timezone

LATE_ACCEPTABLE_MIN = 10.0
LATE_DEGRADED_MIN = 45.0
ON_TIME, LATE_ACCEPTABLE, LATE_DEGRADED, MISSED, CYCLE = "ON_TIME", "LATE_ACCEPTABLE", "LATE_DEGRADED", "MISSED", "CYCLE"
HISTORICALLY_VALIDATED_ENGINES = {"GAME": True, "PERIOD": True, "PLAYER": True, "JOINT": False, "SEASON": False, "NONE": False}


def _dt(s):
    if not s:
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def horizon_quality(horizon_label: str | None, horizon_target_min: float | None, kickoff_utc: str | None, observed_at: str | None,
                    generated_at: str | None, *, snapshot_reused: bool = False) -> dict:
    """Timestamps and the class. `lateness` is observation minus target (minutes, positive = late)."""
    out = {"horizon_quality": CYCLE, "horizon_target_utc": None, "observation_lateness_min": None, "generation_lateness_min": None,
           "exact_target_missed": None, "snapshot_reused": bool(snapshot_reused)}
    ko, obs, gen = _dt(kickoff_utc), _dt(observed_at), _dt(generated_at)
    if not horizon_label or horizon_label == CYCLE or horizon_target_min is None or ko is None:
        return out
    from datetime import timedelta
    target = ko - timedelta(minutes=float(horizon_target_min))
    out["horizon_target_utc"] = target.isoformat()
    if obs is None or obs >= ko:
        out["horizon_quality"] = MISSED
        return out
    late_obs = (obs - target).total_seconds() / 60.0
    out["observation_lateness_min"] = late_obs
    out["generation_lateness_min"] = ((gen - target).total_seconds() / 60.0) if gen else None
    out["exact_target_missed"] = abs(late_obs) > LATE_ACCEPTABLE_MIN
    if abs(late_obs) <= LATE_ACCEPTABLE_MIN:
        out["horizon_quality"] = ON_TIME
    elif late_obs <= LATE_DEGRADED_MIN:
        out["horizon_quality"] = LATE_ACCEPTABLE
    else:
        out["horizon_quality"] = LATE_DEGRADED
    return out


def status_flags(*, support_state: str, semantic_confidence: str | None, identity_confidence: str | None, subject_kind: str | None,
                 settlement_support: str | None, engine: str | None) -> dict:
    has_p = support_state in ("PRICED", "PROJECTABLE_NOT_YET_VALIDATED")
    if subject_kind == "player":
        ident = identity_confidence in ("RESOLVED", "RESOLVED_UNCONFIRMED")
    elif subject_kind == "team":
        ident = True
    else:
        ident = subject_kind is None or subject_kind == "none"
    return {"has_probability": has_p, "semantics_proven": semantic_confidence == "PROVEN", "identity_resolved": bool(ident),
            "settlement_supported": settlement_support == "SUPPORTED", "historically_validated": bool(HISTORICALLY_VALIDATED_ENGINES.get(engine, False)) and has_p,
            "prospectively_validated": False, "execution_supported": False, "betting_authorized": False}
