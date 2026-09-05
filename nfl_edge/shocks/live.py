"""Live shock ingestion: diff consecutive context captures into timestamped, deduplicated shocks.

The whole point of the 2026 system is to record **what we knew and when we knew it**. Two rules follow and
both are enforced here rather than left to discipline:

  * **No retroactive timestamp invention.** If a source does not carry an event time, `first_seen_at` is the
    capture in which the change was first *observed*, never a guess at when it really happened. A source
    timestamp, where one exists, is recorded separately as `source_timestamp` and never overwrites
    `first_seen_at`.
  * **One real-world event is one shock.** Sleeper flipping a player to Out and ESPN reporting the same three
    minutes later is one event seen twice. Both observations are preserved, linked to a canonical shock keyed
    on (entity, game, transition) within a dedup window; the canonical `first_seen_at` is the earliest.

Only structured, already-approved sources are read. No rumour or free-text scraping.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

DEDUP_WINDOW_S = 3600.0

# shock families -- deliberately coarse. Over-classifying weak information manufactures events.
QB_STATUS = "QB_STATUS_CHANGE"
SKILL_STATUS = "SKILL_PLAYER_STATUS_CHANGE"
OL_STATUS = "OFFENSIVE_LINE_STATUS_CHANGE"
DEF_STATUS = "DEFENSIVE_STARTER_STATUS_CHANGE"
INACTIVE_CONFIRMED = "INACTIVE_CONFIRMED"
DEPTH_CHART = "DEPTH_CHART_CHANGE"
WEATHER_WIND = "WEATHER_WIND_CHANGE"
WEATHER_PRECIP = "WEATHER_PRECIP_CHANGE"
OTHER_AVAIL = "OTHER_STRUCTURED_AVAILABILITY_CHANGE"

SKILL_POS = {"QB", "RB", "WR", "TE"}
OL_POS = {"C", "G", "T", "OL", "OT", "OG"}
DEF_POS = {"DE", "DT", "LB", "CB", "S", "FS", "SS", "DL", "DB", "EDGE", "NT", "ILB", "OLB", "MLB"}

# how much a forecast must move to count as a shock at all
WIND_DELTA_MPH = 5.0
PRECIP_DELTA = 0.30


@dataclass
class LiveShock:
    shock_id: str
    canonical_id: str
    first_seen_at: str
    capture_timestamp: str
    source: str
    source_timestamp: str | None
    entity_type: str                    # player | team | game
    entity_id: str
    entity_name: str | None
    entity_position: str | None
    team: str | None
    game_id: str | None
    prior_state: str | None
    new_state: str
    shock_family: str
    timing_basis: str = "exact"         # observed in a capture we took; never backdated
    confidence: str = "medium"
    affected_market_families: list = field(default_factory=list)
    evidence_ref: str | None = None     # capture file the change was observed in
    notes: str = ""

    def to_dict(self):
        return asdict(self)


def _iso(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).isoformat()
    except ValueError:
        return None


def _epoch(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return None


def _family_for(position, new_state):
    if new_state == "inactive":
        return INACTIVE_CONFIRMED
    p = (position or "").upper()
    if p == "QB":
        return QB_STATUS
    if p in SKILL_POS:
        return SKILL_STATUS
    if p in OL_POS:
        return OL_STATUS
    if p in DEF_POS:
        return DEF_STATUS
    return OTHER_AVAIL


def _canon(entity_id, prior, new):
    return "can_" + hashlib.sha1(f"{entity_id}|{prior}|{new}".encode()).hexdigest()[:16]


def _sid(source, entity_id, prior, new, seen):
    return "shk_" + hashlib.sha1(f"{source}|{entity_id}|{prior}|{new}|{seen}".encode()).hexdigest()[:16]


def _sleeper_states(path):
    d = json.load(open(path))
    out = {}
    for pid, p in (d.get("players") or {}).items():
        out[pid] = {"status": p.get("status"), "injury_status": p.get("injury_status"),
                    "active": p.get("active"), "depth": p.get("depth_chart_order"),
                    "name": p.get("full_name"), "position": p.get("position"),
                    "team": p.get("team"), "gsis": p.get("gsis_id")}
    return d.get("retrieved_at") or d.get("run_id"), out


def _weather_states(path):
    out = {}
    retrieved = None
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        retrieved = retrieved or r.get("run_id")
        om = (r.get("open_meteo") or {}).get("hourly") or {}
        ws, pr = om.get("wind_speed_10m") or [], om.get("precipitation") or []
        if not r.get("game_id"):
            continue
        out[r["game_id"]] = {"wind": max(ws) if ws else None,
                             "precip": max(pr) if pr else None,
                             "roof": r.get("roof"), "home": r.get("home_team")}
    return retrieved, out


def diff_captures(prev_path, curr_path, source, evidence_ref=None):
    """Emit LiveShocks for state changes between two consecutive captures of one source."""
    shocks = []
    if source == "sleeper":
        _pt, prev = _sleeper_states(prev_path)
        ct, curr = _sleeper_states(curr_path)
        seen = _iso(ct) or _iso(curr_path)
        for pid, now in curr.items():
            was = prev.get(pid)
            if not was:
                continue                       # a newly appearing player is not a state change
            transitions = []
            if (was.get("injury_status") or "") != (now.get("injury_status") or ""):
                transitions.append(("injury_status", was.get("injury_status") or "none",
                                    now.get("injury_status") or "none"))
            if bool(was.get("active")) != bool(now.get("active")):
                transitions.append(("active", str(was.get("active")), str(now.get("active"))))
            if (was.get("depth") or 0) != (now.get("depth") or 0) and now.get("position") in SKILL_POS:
                transitions.append(("depth_chart_order", str(was.get("depth")), str(now.get("depth"))))
            for kind, prior, new in transitions:
                fam = DEPTH_CHART if kind == "depth_chart_order" else _family_for(now.get("position"), new)
                shocks.append(LiveShock(
                    shock_id=_sid(source, pid, prior, new, seen), canonical_id=_canon(pid, prior, new),
                    first_seen_at=seen, capture_timestamp=seen, source=source, source_timestamp=None,
                    entity_type="player", entity_id=now.get("gsis") or f"sleeper:{pid}",
                    entity_name=now.get("name"), entity_position=now.get("position"),
                    team=now.get("team"), game_id=None, prior_state=prior, new_state=new,
                    shock_family=fam, confidence="medium" if kind != "active" else "high",
                    affected_market_families=["PLAYER_STAT", "FIRST_TD_SCORER"],
                    evidence_ref=evidence_ref or os.path.basename(curr_path),
                    notes=f"{kind} changed in the sleeper capture; first_seen_at is the capture time, "
                          f"not an inferred event time"))
    elif source == "weather":
        _pt, prev = _weather_states(prev_path)
        ct, curr = _weather_states(curr_path)
        seen = _iso(ct) or _iso(curr_path)
        for gid, now in curr.items():
            was = prev.get(gid)
            if not was or now.get("roof") not in ("outdoors", "open"):
                continue
            for key, thresh, fam in (("wind", WIND_DELTA_MPH, WEATHER_WIND),
                                     ("precip", PRECIP_DELTA, WEATHER_PRECIP)):
                a, b = was.get(key), now.get(key)
                if a is None or b is None or abs(b - a) < thresh:
                    continue
                shocks.append(LiveShock(
                    shock_id=_sid(source, f"{gid}:{key}", f"{a:.2f}", f"{b:.2f}", seen),
                    canonical_id=_canon(f"{gid}:{key}", f"{a:.1f}", f"{b:.1f}"),
                    first_seen_at=seen, capture_timestamp=seen, source=source, source_timestamp=None,
                    entity_type="game", entity_id=gid, entity_name=gid, entity_position=None,
                    team=now.get("home"), game_id=gid, prior_state=f"{a:.2f}", new_state=f"{b:.2f}",
                    shock_family=fam, confidence="medium",
                    affected_market_families=["TOTAL", "TEAM_TOTAL", "SPREAD", "PLAYER_STAT"],
                    evidence_ref=evidence_ref or os.path.basename(curr_path),
                    notes=f"kickoff-hour {key} forecast moved {a:.2f} -> {b:.2f}; threshold {thresh}"))
    return shocks


def dedupe(shocks, window_s=DEDUP_WINDOW_S):
    """Link observations of one real-world event. Preserves every observation; picks one canonical row."""
    by_canon = {}
    for s in sorted(shocks, key=lambda x: x.first_seen_at or ""):
        t = _epoch(s.first_seen_at)
        placed = False
        for key, group in by_canon.items():
            if key[0] != s.canonical_id:
                continue
            t0 = _epoch(group[0].first_seen_at)
            if t is not None and t0 is not None and abs(t - t0) <= window_s:
                group.append(s); placed = True
                break
        if not placed:
            by_canon[(s.canonical_id, s.first_seen_at)] = [s]
    canonical, observations = [], []
    for group in by_canon.values():
        group.sort(key=lambda x: x.first_seen_at or "")
        head = group[0]
        canonical.append(head)
        observations.extend(group)
    return canonical, observations


def ingest_context_dir(context_dir, sources=("sleeper", "weather")):
    """Walk a context capture directory in time order and emit deduplicated live shocks."""
    all_shocks = []
    for source, pattern in (("sleeper", "*.sleeper.json"), ("weather", "*.weather.jsonl")):
        if source not in sources:
            continue
        files = sorted(glob.glob(os.path.join(context_dir, "*", pattern)))
        for prev, curr in zip(files, files[1:]):
            try:
                all_shocks.extend(diff_captures(prev, curr, source))
            except (json.JSONDecodeError, KeyError, OSError):
                continue
    return dedupe(all_shocks)
