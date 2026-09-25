"""POINT-IN-TIME QUARTERBACK RESOLUTION: who is expected to throw the team's passes, from what was known at the cutoff.

Why this exists
---------------
`DepthChartBook.qb1()` answers "who is first on the newest chart at or before the cutoff". That is a statement about
the chart, not about the game. ESPN charts are slow to demote an injured starter, so in 2026 Week 2 three of the four
QB1 mismatches against the actual starter were a charted QB1 who was designated OUT at the cutoff (Penix ATL, Murray
MIN, Darnold SEA; docs/KNOWN_LIMITATIONS.md #89). V3 and V4 priced the backup as a non-starter and the Out starter as
the starter, and every pass-catcher on those teams inherited the wrong passing environment. The frozen arms keep that
behaviour (their inputs cannot change in the middle of their prospective collection); DATA_PLAYER_V5 reads this
module instead.

The rule, in order
------------------
    chart     the team's QBs in chart order from the newest chart at or before the cutoff (DepthChartBook already
              selects the vintage; a chart whose vintage is AFTER the cutoff is refused here as well, so a caller
              that hands in the wrong chart cannot leak it)
    evidence  every availability observation about those QBs that existed at the cutoff: the point-in-time
              injury-report vintage, the run's availability captures (sleeper / espn / weekly roster), and the
              official inactive list. An observation is USED only when it was made at or before the cutoff and
              before kickoff; an official inactive observation must carry its own capture time (a list with no
              timestamp cannot be shown to have existed pregame); a POSTGAME observation is never evidence. What
              is rejected is recorded with the reason.
    state     per QB, the most severe usable reading: INACTIVE > OUT > DOUBTFUL > QUESTIONABLE > AVAILABLE. With
              no usable reading a QB is AVAILABLE only if the team's report was known at the cutoff (a healthy
              starter is simply not on the report); otherwise he is UNKNOWN -- never "healthy" by default.

    QB1 AVAILABLE (no designation / Probable / active)
              keep QB1                                       CHART_QB1_AVAILABLE            HIGH
    QB1 OUT / IR / inactive (evidence at the cutoff)
              promote the next charted QB who is not himself Out / inactive
                                                             QB1_OUT_PROMOTED_NEXT          MEDIUM
                                                             (HIGH when the official inactive list, observed
                                                              pregame and at or before the cutoff, names QB1)
              no eligible QB behind him on the chart         QB1_OUT_NO_ELIGIBLE_BACKUP     UNKNOWN  (abstain)
    QB1 DOUBTFUL
              keep QB1 as the structural input, and ABSTAIN on every quarterback-dependent projection of the team
                                                             QB1_DOUBTFUL_ABSTAIN           LOW      (abstain)
    QB1 QUESTIONABLE
              keep QB1, flagged                              QB1_QUESTIONABLE_RETAINED      LOW
    QB1 UNKNOWN (no report at the cutoff)
              keep QB1, flagged                              QB1_STATUS_UNKNOWN_RETAINED    LOW
    no chart QB1 at the cutoff                               NO_CHART_QB1                   UNKNOWN  (abstain)
    the chart handed in post-dates the cutoff                CHART_AFTER_CUTOFF_REFUSED     UNKNOWN  (abstain)

Why Doubtful abstains rather than promotes: a Doubtful designation is a probability, not an outcome, and the model
has one QB slot per team. Promoting the backup would assert certainty the report does not give; keeping QB1 silently
would repeat the #89 defect in a milder form. So the structure keeps the chart QB1 (the least-surprising input) and
the record says, per projection, that its passing environment is not known well enough to be scored as an
opinion -- the probability stays on the record (abstention withholds authority, never the number). Questionable QBs
play in the large majority of cases, so they are retained with a LOW-certainty flag rather than abstained.

Nothing here reads a game's result, a box score, the schedule's starting-QB ids (which nflverse fills in during the
week and finalises after kickoff), or any file newer than the cutoff. The function is pure: the same inputs give the
same answer, and the answer names every piece of evidence it used and every piece it refused.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Sequence

QB_RESOLUTION_VERSION = "qb-resolution-1.0.0"

# normalised availability states, most severe last
AVAILABLE, UNKNOWN, QUESTIONABLE, DOUBTFUL, OUT, INACTIVE = "AVAILABLE", "UNKNOWN", "QUESTIONABLE", "DOUBTFUL", "OUT", "INACTIVE"
SEVERITY = {AVAILABLE: 0, UNKNOWN: 1, QUESTIONABLE: 2, DOUBTFUL: 3, OUT: 4, INACTIVE: 5}
DEFINITIVELY_OUT = (OUT, INACTIVE)

# reasons
CHART_QB1_AVAILABLE = "CHART_QB1_AVAILABLE"
QB1_OUT_PROMOTED_NEXT = "QB1_OUT_PROMOTED_NEXT"
QB1_OUT_NO_ELIGIBLE_BACKUP = "QB1_OUT_NO_ELIGIBLE_BACKUP"
QB1_DOUBTFUL_ABSTAIN = "QB1_DOUBTFUL_ABSTAIN"
QB1_QUESTIONABLE_RETAINED = "QB1_QUESTIONABLE_RETAINED"
QB1_STATUS_UNKNOWN_RETAINED = "QB1_STATUS_UNKNOWN_RETAINED"
NO_CHART_QB1 = "NO_CHART_QB1"
CHART_AFTER_CUTOFF_REFUSED = "CHART_AFTER_CUTOFF_REFUSED"
ABSTAIN_REASONS = (QB1_OUT_NO_ELIGIBLE_BACKUP, QB1_DOUBTFUL_ABSTAIN, NO_CHART_QB1, CHART_AFTER_CUTOFF_REFUSED)

HIGH, MEDIUM, LOW = "HIGH", "MEDIUM", "LOW"

# evidence sources
SRC_INJURY_REPORT = "injury_report"          # the point-in-time nflverse injury-report vintage (ctx.injuries)
SRC_AVAILABILITY = "availability"            # the run's sleeper / espn / weekly-roster captures (AvailabilityBook)
SRC_OFFICIAL_INACTIVES = "official_inactives"
POSTGAME_OBSERVATION = "POSTGAME_OBSERVATION"

# raw status strings from every source -> the normalised state. Unrecognised strings are UNKNOWN, never AVAILABLE.
_STATUS_MAP = {
    "": AVAILABLE, "NONE": AVAILABLE, "ACTIVE": AVAILABLE, "ACT": AVAILABLE, "EXPECTED_ACTIVE": AVAILABLE, "PROBABLE": AVAILABLE,
    "QUESTIONABLE": QUESTIONABLE, "DAY-TO-DAY": QUESTIONABLE, "COV": QUESTIONABLE,
    "DOUBTFUL": DOUBTFUL,
    "OUT": OUT, "EXPECTED_OUT": OUT, "IR": OUT, "INJURED RESERVE": OUT, "INJURED_RESERVE": OUT, "RES": OUT, "PUP": OUT,
    "PHYSICALLY UNABLE TO PERFORM": OUT, "SUS": OUT, "SUSPENSION": OUT, "NON": OUT, "NFI": OUT, "CUT": OUT, "DNR": OUT,
    "INACTIVE": INACTIVE, "INACTIVE_CONFIRMED": INACTIVE,
    "UNKNOWN": UNKNOWN, "NA": UNKNOWN,
}
# the quarterback-dependent statistics of a non-quarterback: his projection runs through the passing environment
PASS_CATCHER_QB_STATS = ("receptions", "receiving_yards", "rush_rec_yards")
PASS_CATCHER_TD_POSITIONS = ("WR", "TE")


def normalize_status(raw) -> str:
    if raw is None:
        return AVAILABLE
    return _STATUS_MAP.get(str(raw).strip().upper(), UNKNOWN)


def _utc(x) -> datetime | None:
    if x is None or x == "":
        return None
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    s = str(x)
    if "-W" in s and "T" not in s:            # a legacy weekly chart vintage ("2024-W03"): not an instant
        return None
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class QbEvidence:
    """One availability observation about one quarterback, with the instant it was made."""
    gsis_id: str
    status: str
    source: str
    observed_at: object = None          # datetime or ISO string; required for official inactives
    evidence_class: str | None = None   # POSTGAME_OBSERVATION is never pregame evidence

    def state(self) -> str:
        return normalize_status(self.status)


def _admissible(ev: QbEvidence, cutoff: datetime | None, kickoff: datetime | None) -> str | None:
    """None when the observation may be used at `cutoff`; otherwise why it may not."""
    if ev.evidence_class == POSTGAME_OBSERVATION:
        return "postgame observation: never pregame evidence"
    obs = _utc(ev.observed_at)
    if ev.source == SRC_OFFICIAL_INACTIVES and obs is None:
        return "official inactive observation without a capture time: cannot be shown to have existed at the cutoff"
    if obs is not None and cutoff is not None and obs > cutoff:
        return f"observed {obs.isoformat()} after the cutoff {cutoff.isoformat()}"
    if obs is not None and kickoff is not None and obs >= kickoff:
        return f"observed {obs.isoformat()} at or after kickoff"
    return None


def qb_states(qbs: Sequence[str], evidence: Iterable[QbEvidence], *, cutoff=None, kickoff=None,
              status_known: bool = True) -> tuple[dict, dict, list, list]:
    """Per QB: (state, the source that decided it), plus the evidence used and refused."""
    cut, ko = _utc(cutoff), _utc(kickoff)
    wanted = set(qbs)
    best, src, used, rejected = {}, {}, [], []
    for ev in evidence:
        if ev.gsis_id not in wanted:
            continue
        why = _admissible(ev, cut, ko)
        row = {"gsis_id": ev.gsis_id, "source": ev.source, "status": ev.status,
               "observed_at": (_utc(ev.observed_at).isoformat() if _utc(ev.observed_at) else None)}
        if why:
            rejected.append({**row, "reason": why})
            continue
        st = ev.state()
        used.append({**row, "state": st})
        # UNKNOWN from one source never overrides a known reading from another
        cur = best.get(ev.gsis_id)
        if st == UNKNOWN and cur is not None:
            continue
        if cur is None or cur == UNKNOWN or SEVERITY[st] > SEVERITY[cur]:
            best[ev.gsis_id] = st
            src[ev.gsis_id] = ev.source
    states = {}
    for q in qbs:
        states[q] = best.get(q, AVAILABLE if status_known else UNKNOWN)
    return states, src, used, rejected


def resolve_team_qb(*, team: str | None, chart_qbs: Sequence[str], cutoff, evidence: Iterable[QbEvidence] = (),
                    chart_vintage=None, kickoff=None, status_known: bool = True) -> dict:
    """The point-in-time projected starting quarterback of one team for one game (see the module docstring).

    chart_qbs: the team's quarterbacks in chart order from the newest chart at or before the cutoff.
    status_known: whether ANY point-in-time availability source covered the team at the cutoff (the injury-report
    vintage or an availability capture). Without one, an unlisted QB is UNKNOWN, not AVAILABLE.
    """
    cut = _utc(cutoff)
    out = {"qb_resolution_version": QB_RESOLUTION_VERSION, "team": team, "cutoff": cut.isoformat() if cut else None,
           "depth_chart_qb1": (chart_qbs[0] if chart_qbs else None), "effective_projected_qb": None,
           "qb_availability_state": None, "effective_qb_availability_state": None, "qb_resolution_reason": None,
           "qb_resolution_certainty": "UNKNOWN", "qb_dependent_abstain": False, "promoted_over": [],
           "chart_vintage": (str(chart_vintage) if chart_vintage is not None else None), "evidence_used": [], "evidence_rejected": []}
    vint = _utc(chart_vintage)
    if vint is not None and cut is not None and vint > cut:
        out.update(depth_chart_qb1=None, qb_resolution_reason=CHART_AFTER_CUTOFF_REFUSED, qb_dependent_abstain=True)
        return out
    if not chart_qbs:
        out.update(qb_resolution_reason=NO_CHART_QB1, qb_dependent_abstain=True)
        return out
    states, src, used, rejected = qb_states(chart_qbs, evidence, cutoff=cut, kickoff=kickoff, status_known=status_known)
    out["evidence_used"], out["evidence_rejected"] = used, rejected
    qb1 = chart_qbs[0]
    s1 = states[qb1]
    out["qb_availability_state"] = s1
    if s1 in DEFINITIVELY_OUT:
        nxt = next((q for q in chart_qbs[1:] if states[q] not in DEFINITIVELY_OUT), None)
        out["promoted_over"] = [q for q in chart_qbs[: chart_qbs.index(nxt)]] if nxt else list(chart_qbs)
        if nxt is None:
            out.update(qb_resolution_reason=QB1_OUT_NO_ELIGIBLE_BACKUP, qb_dependent_abstain=True)
            return out
        confirmed = s1 == INACTIVE and src.get(qb1) == SRC_OFFICIAL_INACTIVES
        cert = HIGH if confirmed else MEDIUM
        if states[nxt] in (QUESTIONABLE, DOUBTFUL, UNKNOWN):
            cert = LOW                                        # the promoted QB is himself uncertain
        out.update(effective_projected_qb=nxt, effective_qb_availability_state=states[nxt],
                   qb_resolution_reason=QB1_OUT_PROMOTED_NEXT, qb_resolution_certainty=cert)
        return out
    out.update(effective_projected_qb=qb1, effective_qb_availability_state=s1)
    if s1 == AVAILABLE:
        out.update(qb_resolution_reason=CHART_QB1_AVAILABLE, qb_resolution_certainty=HIGH)
    elif s1 == DOUBTFUL:
        out.update(qb_resolution_reason=QB1_DOUBTFUL_ABSTAIN, qb_resolution_certainty=LOW, qb_dependent_abstain=True)
    elif s1 == QUESTIONABLE:
        out.update(qb_resolution_reason=QB1_QUESTIONABLE_RETAINED, qb_resolution_certainty=LOW)
    else:
        out.update(qb_resolution_reason=QB1_STATUS_UNKNOWN_RETAINED, qb_resolution_certainty=LOW)
    return out


def is_qb_dependent(stat: str | None, position: str | None) -> bool:
    """Whether a projection of `stat` for a player at `position` runs through the team's passing environment.

    A quarterback's every statistic depends on who the quarterback is. A pass-catcher's receptions / receiving yards
    (and their rush+rec sum) do; so does a WR / TE anytime touchdown, which is driven by his targets. An RB's rushing
    and anytime-TD projection are carried mainly by his carries, and are not abstained for the quarterback."""
    if not stat:
        return False
    if (position or "").upper() == "QB":
        return True
    if stat in PASS_CATCHER_QB_STATS:
        return True
    return stat == "touchdowns" and (position or "").upper() in PASS_CATCHER_TD_POSITIONS


def compact(res: dict) -> dict:
    """The five fields frozen on every V5 player record (and kept by the lean record)."""
    return {"depth_chart_qb1": res.get("depth_chart_qb1"), "effective_projected_qb": res.get("effective_projected_qb"),
            "qb_availability_state": res.get("qb_availability_state"), "qb_resolution_reason": res.get("qb_resolution_reason"),
            "qb_resolution_certainty": res.get("qb_resolution_certainty")}
