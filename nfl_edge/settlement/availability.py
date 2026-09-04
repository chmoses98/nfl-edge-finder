"""Player availability state, built only from information timestamped before kickoff.

States (never collapse UNKNOWN into active):
    EXPECTED_ACTIVE     no adverse signal; on the active roster
    QUESTIONABLE        official/aggregator status Questionable, or limited practice
    DOUBTFUL            official/aggregator status Doubtful
    EXPECTED_OUT        reported Out for this game, or roster status IR/PUP/SUS/NFI
    OUT                 same, confirmed by two independent sources
    INACTIVE_CONFIRMED  on the official gameday inactive list (not obtainable free today -> reserved)
    UNKNOWN             player not found in any availability source

Each state maps to (p_plays, p_active_no_snap).  p_plays is the probability of taking at least one
offensive snap -- the participation requirement in Kalshi's player-prop rules -- so it also folds in the
chance that a healthy deep-bench player simply never gets on the field.

The base rates below are priors, deliberately conservative, and are registered as hypothesis H-20260904-008
for prospective calibration against 2026 outcomes.  They are NOT fitted to 2026 data.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

EXPECTED_ACTIVE = "EXPECTED_ACTIVE"
QUESTIONABLE = "QUESTIONABLE"
DOUBTFUL = "DOUBTFUL"
EXPECTED_OUT = "EXPECTED_OUT"
OUT = "OUT"
INACTIVE_CONFIRMED = "INACTIVE_CONFIRMED"
UNKNOWN = "UNKNOWN"

# state -> (P(takes >= 1 offensive snap), P(active but never takes a snap))
# The remainder is P(inactive), which settles a YES contract at $0.00.
#
# MEASURED, not assumed (research/availability/RESULTS.md):
#  * 101,917 established-role offensive player-weeks, 2015-2025, official designation vs PFR snap counts:
#      Questionable 0.690 play (stable 0.63-0.80 across all 11 seasons), Doubtful 0.007, Out 0.0005,
#      Probable 0.967, on-report-no-status 0.944.
#  * The population we actually price is narrower -- players Kalshi lists a prop for. On the 4,243 listed
#    player-games in the 2025 archive: not-on-report 0.971, on-report-no-status 0.992, Questionable 0.827
#    (n=104), Out 0.000 (n=33). Kalshi lists props for questionable players it expects to play, so the
#    listed-population Questionable rate is higher than the league-wide one; with n=104 it is shrunk toward
#    the 11-season 0.690 estimate, giving 0.78.
#  * "dressed but never took an offensive snap" -- the branch that settles at a fair price -- is rare in the
#    listed population: 0.5% (not-on-report) to 1.0% (Questionable).
# The earlier hand-set priors were wrong in one important place: DOUBTFUL was set to 0.25 when the measured
# rate is under 0.01. In the modern NFL a Doubtful designation is effectively an Out.
STATE_PLAY_RATES = {
    EXPECTED_ACTIVE: (0.975, 0.005),
    QUESTIONABLE: (0.78, 0.010),
    DOUBTFUL: (0.03, 0.005),
    EXPECTED_OUT: (0.02, 0.005),
    OUT: (0.005, 0.002),
    INACTIVE_CONFIRMED: (0.0, 0.0),
    # UNKNOWN: our sources did not find the player. The unconditional rate among Kalshi-listed players is
    # 0.962; we deliberately price below it and raise a quality flag rather than assume the player is healthy.
    UNKNOWN: (0.90, 0.02),
}
# Depth-chart adjustment. In the listed population the dressed-but-no-snap branch is ~0.5%, so the earlier
# aggressive role floors (0.65 for a 4th-stringer) over-penalised. Only deep reserves are adjusted.
ROLE_SNAP_FLOOR = {1: 1.0, 2: 1.0, 3: 0.98, 4: 0.94}

BLOCKING_STATES = {EXPECTED_OUT, OUT, INACTIVE_CONFIRMED}


@dataclass
class Availability:
    player_id: str | None
    state: str
    p_plays: float
    p_active_no_snap: float
    sources: dict = field(default_factory=dict)
    as_of: str | None = None
    stale_minutes: float | None = None
    notes: list = field(default_factory=list)

    @property
    def p_inactive(self) -> float:
        return max(0.0, 1.0 - self.p_plays - self.p_active_no_snap)

    def to_dict(self):
        d = self.__dict__.copy()
        d["p_inactive"] = self.p_inactive
        return d


_SLEEPER_MAP = {"out": OUT, "ir": EXPECTED_OUT, "pup": EXPECTED_OUT, "sus": EXPECTED_OUT, "nfi": EXPECTED_OUT,
                "doubtful": DOUBTFUL, "questionable": QUESTIONABLE, "probable": EXPECTED_ACTIVE, "cov": QUESTIONABLE,
                "na": UNKNOWN, "dnr": EXPECTED_OUT}
_ESPN_MAP = {"out": OUT, "injured reserve": EXPECTED_OUT, "suspension": EXPECTED_OUT, "doubtful": DOUBTFUL,
             "questionable": QUESTIONABLE, "day-to-day": QUESTIONABLE, "active": EXPECTED_ACTIVE,
             "probable": EXPECTED_ACTIVE, "physically unable to perform": EXPECTED_OUT}
_ROSTER_MAP = {"RES": EXPECTED_OUT, "PUP": EXPECTED_OUT, "SUS": EXPECTED_OUT, "NON": EXPECTED_OUT,
               "CUT": EXPECTED_OUT, "RSN": EXPECTED_OUT, "RSR": EXPECTED_OUT, "ACT": EXPECTED_ACTIVE,
               "DEV": QUESTIONABLE}
_SEVERITY = {EXPECTED_ACTIVE: 0, UNKNOWN: 1, QUESTIONABLE: 2, DOUBTFUL: 3, EXPECTED_OUT: 4, OUT: 5, INACTIVE_CONFIRMED: 6}


def combine_states(states: dict) -> str:
    """Most adverse non-UNKNOWN signal wins; UNKNOWN only if nothing else is known.
    Two independent sources agreeing on EXPECTED_OUT promote it to OUT."""
    known = {k: v for k, v in states.items() if v and v != UNKNOWN}
    if not known:
        return UNKNOWN
    worst = max(known.values(), key=lambda s: _SEVERITY[s])
    if worst == EXPECTED_OUT and sum(1 for v in known.values() if v in (EXPECTED_OUT, OUT)) >= 2:
        return OUT
    return worst


def rates_for(state: str, depth_rank: int | None = None) -> tuple[float, float]:
    p_play, p_nosnap = STATE_PLAY_RATES[state]
    if depth_rank is not None and state not in BLOCKING_STATES:
        floor = ROLE_SNAP_FLOOR.get(int(depth_rank), 0.5)
        # a deep reserve who is healthy still may never take an offensive snap
        moved = p_play * floor
        p_nosnap = p_nosnap + (p_play - moved)
        p_play = moved
    return p_play, p_nosnap


class AvailabilityBook:
    """Availability for every player at one capture timestamp, from the context-capture snapshots.

    Inputs (all carry their own retrieval timestamps):
      sleeper players snapshot   injury_status / practice_participation / depth_chart_order, keyed by sleeper id
      espn injuries snapshot     status per athlete id
      nflverse weekly roster     status per gsis id for the week (published before the week's games)
    A player is looked up by GSIS id; the crosswalk supplies sleeper/espn ids.
    """

    def __init__(self, as_of: datetime, max_staleness_minutes: float = 360.0):
        self.as_of = as_of
        self.max_staleness_minutes = max_staleness_minutes
        self.by_gsis: dict[str, Availability] = {}
        self.source_meta: dict = {}

    @staticmethod
    def _norm(s):
        return (s or "").strip().lower()

    def load_sleeper(self, path: str, crosswalk: dict):
        """crosswalk: sleeper_id -> gsis_id"""
        j = json.load(open(path))
        retrieved = j.get("retrieved_at")
        stale = self._stale(retrieved)
        self.source_meta["sleeper"] = {"retrieved_at": retrieved, "stale_minutes": stale, "path": os.path.basename(path)}
        for sid, p in j.get("players", {}).items():
            gsis = p.get("gsis_id") or crosswalk.get(str(sid))
            if not gsis:
                continue
            st = _SLEEPER_MAP.get(self._norm(p.get("injury_status")), None)
            if st is None:
                st = EXPECTED_ACTIVE if p.get("active") else UNKNOWN
            rec = self.by_gsis.setdefault(gsis, Availability(gsis, UNKNOWN, 0.0, 0.0))
            rec.sources["sleeper"] = {"state": st, "injury_status": p.get("injury_status"),
                                      "body_part": p.get("injury_body_part"), "depth_chart_order": p.get("depth_chart_order"),
                                      "practice": p.get("practice_participation"), "stale_minutes": stale}

    def load_espn(self, path: str, crosswalk: dict):
        """crosswalk: espn_id -> gsis_id"""
        j = json.load(open(path))
        retrieved = j.get("retrieved_at")
        stale = self._stale(retrieved)
        self.source_meta["espn"] = {"retrieved_at": retrieved, "stale_minutes": stale, "path": os.path.basename(path)}
        for inj in j.get("injuries", []):
            gsis = crosswalk.get(str(inj.get("athlete_id")))
            if not gsis:
                continue
            st = _ESPN_MAP.get(self._norm(inj.get("status")), UNKNOWN)
            rec = self.by_gsis.setdefault(gsis, Availability(gsis, UNKNOWN, 0.0, 0.0))
            rec.sources["espn"] = {"state": st, "status": inj.get("status"), "injury": inj.get("injury"),
                                   "date": inj.get("date"), "stale_minutes": stale}

    def load_roster(self, rows, week_label: str = ""):
        """rows: iterable of dicts with gsis_id and status (nflverse weekly roster for the upcoming week)."""
        self.source_meta["roster"] = {"week": week_label, "n": 0}
        n = 0
        for r in rows:
            gsis = r.get("gsis_id")
            if not gsis:
                continue
            st = _ROSTER_MAP.get((r.get("status") or "").upper(), UNKNOWN)
            rec = self.by_gsis.setdefault(gsis, Availability(gsis, UNKNOWN, 0.0, 0.0))
            rec.sources["roster"] = {"state": st, "status": r.get("status")}
            n += 1
        self.source_meta["roster"]["n"] = n

    def _stale(self, retrieved_at):
        if not retrieved_at:
            return None
        try:
            t = datetime.fromisoformat(retrieved_at)
        except ValueError:
            return None
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return round((self.as_of - t).total_seconds() / 60.0, 1)

    def finalize(self):
        for gsis, rec in self.by_gsis.items():
            states = {k: v.get("state") for k, v in rec.sources.items()}
            rec.state = combine_states(states)
            depth = rec.sources.get("sleeper", {}).get("depth_chart_order")
            rec.p_plays, rec.p_active_no_snap = rates_for(rec.state, depth if isinstance(depth, int) else None)
            rec.as_of = self.as_of.isoformat()
            stales = [v.get("stale_minutes") for v in rec.sources.values() if v.get("stale_minutes") is not None]
            rec.stale_minutes = max(stales) if stales else None
            if rec.stale_minutes is not None and rec.stale_minutes > self.max_staleness_minutes:
                rec.notes.append(f"stale availability ({rec.stale_minutes:.0f} min)")
        return self

    def get(self, gsis_id: str) -> Availability:
        rec = self.by_gsis.get(gsis_id)
        if rec is None:
            p, q = rates_for(UNKNOWN)
            return Availability(gsis_id, UNKNOWN, p, q, {}, self.as_of.isoformat(), None, ["player absent from every availability source"])
        return rec

    def is_stale(self) -> bool:
        vals = [m.get("stale_minutes") for m in self.source_meta.values() if isinstance(m, dict) and m.get("stale_minutes") is not None]
        return bool(vals) and max(vals) > self.max_staleness_minutes
