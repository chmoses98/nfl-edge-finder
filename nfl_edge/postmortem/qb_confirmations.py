"""Point-in-time CONFIRMED-STARTER quarterback records: strict validation, per-game resolution, slate coverage.

WHY THIS EXISTS
The point-in-time gate (``integration.pit_gate`` -> ``guards.guard_candidate``) blocks every market the QB-dependency table
(``qb_dependency.py``: score-determined lines, team/game stats, events, QB passing props, anything unclassified) gates unless the required quarterbacks are ``CONFIRMED_STARTER`` with a time. Before this
module nothing in the repository could produce that confirmation, so the gate blocked every game-level line (QB_UNKNOWN).
This module is the only door through which a quarterback becomes CONFIRMED_STARTER, and it is narrow on purpose.

WHAT COUNTS AS CONFIRMATION (owner rule, PR #232 review 2026-11-02)
A source that LITERALLY NAMES the starting quarterback, announced before kickoff by someone entitled to say so:
``TEAM_OFFICIAL_ANNOUNCEMENT``, ``HEAD_COACH_STATEMENT_ON_RECORD``, ``NFL_OFFICIAL_LINEUP_NAMING_STARTER``.
A depth chart, an active roster, an inactive list, an injury-report status, a Sleeper/ESPN roster flag, or a model's
expectation does NOT name a starter. They may be recorded (as EXPECTED_UNCONFIRMED, or OUT for a quarterback who is
declared out) so the evidence is visible, but they can never produce CONFIRMED_STARTER, whatever status the record claims.

NO AUTOMATED FEED EXISTS IN THIS REPOSITORY
The existing availability capture (``nfl_edge/availability_pit``) stores injuries and ESPN per-event ACTIVE flags with our
retrieval time. Those are inactive-list evidence, explicitly "NOT certified and nothing reads it as availability". Nothing
fetched automatically names a starter, so this module does NOT fetch anything. Confirmations are recorded by the owner (or
an analyst the owner authorises) through ``scripts/handicap/qb_confirm_append.py`` / the ``nfl-qb-confirm`` workflow, each
with a source reference and the time the source said it. A confirmation is therefore only as good as that record: the
validator checks the shape, the allowlist, the clock, and conflicts; it cannot check that the person told the truth.

FAIL-CLOSED RULES (each is tested)
* a record that fails validation is REJECTED with a code and never reaches a gate;
* a confirmation must have been OBSERVED at or before it was CAPTURED, CAPTURED at or before the decision time, and the
  decision (and the capture) must precede kickoff - records captured in the future relative to the run are invisible;
* GAME-SPECIFIC validity (2026-11-03; replaces the blanket 48 h age): a record counts for ONE game_id and ONE of that game's two
  teams, was OBSERVED before kickoff and before the decision, and must be fresh on BOTH clocks:
    - ``MAX_AGE_AT_DECISION_MIN`` (24 h): observed no more than 24 h before the decision, else STALE_CONFIRMATION;
    - ``MAX_LEAD_BEFORE_KICKOFF_MIN`` (48 h): observed inside the last 48 h before kickoff, else OBSERVED_TOO_EARLY_BEFORE_KICKOFF.
  Why: starters change through the final injury-report week (designations are final on the Friday before a Sunday game, official
  inactives come ~90 min before kickoff); a statement older than the last two days precedes the information that can still change it.
  Both windows are deliberately tighter than the old 48 h blanket, are owner-adjustable constants, and only ever BLOCK;
* the LATEST observation for a team/game decides, so a later OUT / EXPECTED_UNCONFIRMED / UNKNOWN withdraws an earlier
  confirmation (reason WITHDRAWN_BY_LATER_OUT / WITHDRAWN_BY_LATER_RECORD); on an exact observed-time tie a non-confirming record wins;
* two CONFIRMED_STARTER records for different quarterbacks are a CONFLICT -> UNKNOWN, unless the later one explicitly
  ``supersedes`` the earlier record id (a deliberate change of mind with an audit trail);
* every non-confirmed row carries a stable reason code and provenance (record_id, source, source_ref, observed_at, captured_at, as_of,
  kickoff_utc, game_id, team); a team with no visible record at all has no source to cite and is reported QB_UNKNOWN by the gate;
* a team with no usable record is simply absent -> the gate reports ``QB_UNKNOWN:<team>``;
* a game is "QB-confirmed" only when BOTH teams resolve to CONFIRMED_STARTER.

Pure functions; explicit clocks; no network; nothing here supplies a missing fact. Public repository: quarterback ids are
public nflverse/gsis ids; no private identifier belongs in a record.
"""
from __future__ import annotations

import json
import os
from datetime import datetime

from .common import parse_ts

SCHEMA = "nfl-qb-confirmations.v1"
MODULE_VERSION = "nfl-qb-confirmations-2.0.0"

CONFIRMED_STARTER = "CONFIRMED_STARTER"
EXPECTED_UNCONFIRMED = "EXPECTED_UNCONFIRMED"
OUT = "OUT"
UNKNOWN = "UNKNOWN"
STATUSES = (CONFIRMED_STARTER, EXPECTED_UNCONFIRMED, OUT, UNKNOWN)

#: Sources that name the starter. The ONLY sources allowed to carry CONFIRMED_STARTER.
CONFIRMING_SOURCE_TYPES = frozenset({
    "TEAM_OFFICIAL_ANNOUNCEMENT",
    "HEAD_COACH_STATEMENT_ON_RECORD",
    "NFL_OFFICIAL_LINEUP_NAMING_STARTER",
})
#: Sources that do NOT name a starter. Recordable, never confirming (owner rule: depth chart / roster / inactives are not confirmation).
NON_CONFIRMING_SOURCE_TYPES = frozenset({
    "DEPTH_CHART", "SLEEPER_DEPTH_CHART", "ACTIVE_ROSTER", "SLEEPER_ACTIVE", "ESPN_ROSTER_ACTIVE",
    "INACTIVE_LIST", "INJURY_REPORT", "MODEL_EXPECTATION",
})
#: A non-confirming source may only assert these (a QB declared OUT is restrictive and safe to record from an injury report / inactive list).
NON_CONFIRMING_ALLOWED_STATUSES = (EXPECTED_UNCONFIRMED, OUT, UNKNOWN)

#: OWNER-ADJUSTABLE DEFAULTS (both only ever block). Replace the former blanket ``CONFIRMATION_MAX_AGE_MIN = 48 h``.
#: A confirmation must be OBSERVED no more than this long before the DECISION ...
MAX_AGE_AT_DECISION_MIN = 24 * 60.0
#: ... AND no more than this long before KICKOFF, i.e. inside the window in which the final injury designations and the official inactives
#: (the last news that can change a starter) are published. A statement from earlier in the week predates them. Whichever is tighter binds.
MAX_LEAD_BEFORE_KICKOFF_MIN = 48 * 60.0
#: Reason codes of a non-confirmed row (stable strings; reports and tests key on them).
REASON_STALE = "STALE_CONFIRMATION"
REASON_TOO_EARLY = "OBSERVED_TOO_EARLY_BEFORE_KICKOFF"
REASON_CONFLICT = "CONFLICTING_CONFIRMATIONS"
REASON_WITHDRAWN_OUT = "WITHDRAWN_BY_LATER_OUT"
REASON_WITHDRAWN = "WITHDRAWN_BY_LATER_RECORD"
REASON_NOT_CONFIRMED = "NOT_CONFIRMED_BY_ANY_ACCEPTED_SOURCE"

REQUIRED_FIELDS = ("record_id", "game_id", "team", "qb_player_id", "status", "source_type", "source_ref",
                   "observed_at", "captured_at", "captured_by")

# rejection codes (stable strings; tests and reports key on them)
R_NOT_OBJECT = "NOT_AN_OBJECT"
R_BAD_STATUS = "BAD_STATUS"
R_BAD_SOURCE_TYPE = "SOURCE_TYPE_NOT_ALLOWLISTED"
R_NONCONFIRMING_CANNOT_CONFIRM = "NON_CONFIRMING_SOURCE_CANNOT_CONFIRM_STARTER"
R_OBSERVED_AFTER_CAPTURED = "OBSERVED_AFTER_CAPTURED"
R_DUP_ID = "DUPLICATE_RECORD_ID"
R_BAD_SUPERSEDES = "BAD_SUPERSEDES"
R_BAD_SCHEMA = "BAD_SCHEMA"


def _txt(v) -> str | None:
    return v.strip() if isinstance(v, str) and v.strip() else None


def validate_records(raw_records) -> tuple[list[dict], list[dict]]:
    """(valid, rejections). Order-preserving. Timestamps are normalised to aware-UTC ISO strings; nothing is repaired:
    a record with a missing/naive/garbled time, a missing field, a bad status or source is rejected whole."""
    valid, rejected, seen = [], [], set()
    for i, rec in enumerate(raw_records or []):
        def reject(code, rec=rec, i=i):
            rejected.append({"index": i, "record_id": rec.get("record_id") if isinstance(rec, dict) else None, "code": code})
        if not isinstance(rec, dict):
            reject(R_NOT_OBJECT)
            continue
        missing = [f for f in REQUIRED_FIELDS if _txt(rec.get(f)) is None]
        if missing:
            reject("MISSING_FIELD:" + ",".join(missing))
            continue
        status, stype = rec["status"].strip(), rec["source_type"].strip()
        if status not in STATUSES:
            reject(R_BAD_STATUS)
            continue
        if stype not in CONFIRMING_SOURCE_TYPES and stype not in NON_CONFIRMING_SOURCE_TYPES:
            reject(R_BAD_SOURCE_TYPE)
            continue
        if status == CONFIRMED_STARTER and stype not in CONFIRMING_SOURCE_TYPES:
            reject(R_NONCONFIRMING_CANNOT_CONFIRM)            # a depth chart / roster / inactive list never confirms
            continue
        if stype in NON_CONFIRMING_SOURCE_TYPES and status not in NON_CONFIRMING_ALLOWED_STATUSES:
            reject(R_NONCONFIRMING_CANNOT_CONFIRM)
            continue
        obs, cap = parse_ts(rec["observed_at"]), parse_ts(rec["captured_at"])
        if obs is None:
            reject("BAD_TIMESTAMP:observed_at")
            continue
        if cap is None:
            reject("BAD_TIMESTAMP:captured_at")
            continue
        if obs > cap:
            reject(R_OBSERVED_AFTER_CAPTURED)
            continue
        rid = rec["record_id"].strip()
        if rid in seen:
            reject(R_DUP_ID)
            continue
        sup = rec.get("supersedes")
        if sup is not None and not (isinstance(sup, list) and all(isinstance(s, str) and s.strip() for s in sup)):
            reject(R_BAD_SUPERSEDES)
            continue
        seen.add(rid)
        valid.append({
            "record_id": rid, "game_id": rec["game_id"].strip(), "team": rec["team"].strip(),
            "qb_player_id": rec["qb_player_id"].strip(), "qb_name": _txt(rec.get("qb_name")),
            "status": status, "source_type": stype, "source_ref": rec["source_ref"].strip()[:300],
            "observed_at": obs.isoformat(), "captured_at": cap.isoformat(), "captured_by": rec["captured_by"].strip(),
            "supersedes": [s.strip() for s in (sup or [])],
        })
    return valid, rejected


def load_records_file(path: str) -> tuple[list[dict], list[dict]]:
    """A ``.json`` document ``{"schema": SCHEMA, "records": [...]}`` or a ``.jsonl`` ledger (one record per line), or a
    directory of ``*.jsonl`` (the append-only ledger on the data branch). Returns (valid, rejections); an unreadable or
    wrongly-versioned file is a hard error (ValueError), not an empty confirmation set that quietly blocks nothing."""
    raws: list = []
    if os.path.isdir(path):
        files = sorted(os.path.join(path, f) for f in os.listdir(path) if f.endswith(".jsonl"))
    else:
        files = [path]
    for fp in files:
        if fp.endswith(".jsonl"):
            with open(fp, encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raws.append(json.loads(line))
                    except ValueError as exc:
                        raise ValueError(f"{fp}:{n}: not JSON ({exc})") from exc
        else:
            with open(fp, encoding="utf-8") as fh:
                doc = json.load(fh)
            if not isinstance(doc, dict) or doc.get("schema") != SCHEMA or not isinstance(doc.get("records"), list):
                raise ValueError(f"{fp}: expected an object with schema {SCHEMA!r} and a records list "
                                 "(the old team-keyed shape carried no provenance and is no longer accepted)")
            raws.extend(doc["records"])
    return validate_records(raws)


def _transitively_superseded(records: list[dict]) -> set[str]:
    by_id = {r["record_id"]: r for r in records}
    out: set[str] = set()
    stack = [s for r in records for s in r["supersedes"]]
    while stack:
        s = stack.pop()
        if s in out:
            continue
        out.add(s)
        if s in by_id:
            stack.extend(by_id[s]["supersedes"])
    return out


def resolve_team(records: list[dict], *, game_id: str, team: str, kickoff, as_of,
                 max_age_min: float = MAX_AGE_AT_DECISION_MIN, max_lead_min: float = MAX_LEAD_BEFORE_KICKOFF_MIN) -> dict | None:
    """The effective quarterback status for one team in ONE game, or None when no record is visible (-> QB_UNKNOWN: nothing to cite).

    Only records for this game_id AND this team, captured at or before ``as_of`` AND before kickoff (hence observed before both), are
    visible. Every row returned carries a reason (None only when CONFIRMED) and the provenance of the record that decided it, plus the
    clocks it was judged against (``as_of`` = the decision time, ``kickoff_utc``). ``confirmed_at`` is the time the source said it and is
    set only for CONFIRMED_STARTER."""
    dec, ko = parse_ts(as_of), parse_ts(kickoff)
    if dec is None or ko is None or dec >= ko:
        return None                                          # no decision clock, no kickoff, or already kicked off: nothing is usable
    vis = [r for r in records if r["game_id"] == game_id and r["team"] == team
           and parse_ts(r["captured_at"]) <= dec and parse_ts(r["captured_at"]) < ko and parse_ts(r["observed_at"]) < ko]
    if not vis:
        return None
    # latest OBSERVATION decides; on an exact observed-time tie a non-confirming record sorts last (the restrictive one wins)
    vis.sort(key=lambda r: (parse_ts(r["observed_at"]), 0 if r["status"] == CONFIRMED_STARTER else 1, parse_ts(r["captured_at"]), r["record_id"]))
    latest = vis[-1]
    base = {"game_id": game_id, "team": team, "qb_player_id": latest["qb_player_id"], "record_id": latest["record_id"],
            "source": latest["source_type"], "source_ref": latest["source_ref"], "observed_at": latest["observed_at"],
            "captured_at": latest["captured_at"], "as_of": dec.isoformat(), "kickoff_utc": ko.isoformat(),
            "window": {"max_age_at_decision_min": max_age_min, "max_lead_before_kickoff_min": max_lead_min}}
    if latest["status"] != CONFIRMED_STARTER:
        earlier = [r for r in vis[:-1] if r["status"] == CONFIRMED_STARTER]
        if earlier:
            reason = REASON_WITHDRAWN_OUT if latest["status"] == OUT else REASON_WITHDRAWN
            return {**base, "status": latest["status"], "confirmed_at": None, "reason": reason,
                    "withdrawn_record_ids": sorted(r["record_id"] for r in earlier)}
        return {**base, "status": latest["status"], "confirmed_at": None, "reason": REASON_NOT_CONFIRMED}
    ties = [r for r in vis if r["observed_at"] == latest["observed_at"] and r["status"] == CONFIRMED_STARTER
            and r["qb_player_id"] != latest["qb_player_id"]]
    superseded = _transitively_superseded(vis)
    clash = [r for r in vis if r["status"] == CONFIRMED_STARTER and r["qb_player_id"] != latest["qb_player_id"]
             and r["record_id"] not in superseded]
    if ties or clash:
        return {**base, "status": UNKNOWN, "confirmed_at": None, "reason": REASON_CONFLICT,
                "conflicts": sorted({r["record_id"] for r in ties + clash})}
    obs = parse_ts(latest["observed_at"])
    age = (dec - obs).total_seconds() / 60.0
    lead = (ko - obs).total_seconds() / 60.0
    if age > max_age_min:
        return {**base, "status": UNKNOWN, "confirmed_at": None, "reason": REASON_STALE, "age_min": round(age, 1)}
    if lead > max_lead_min:
        return {**base, "status": UNKNOWN, "confirmed_at": None, "reason": REASON_TOO_EARLY, "age_min": round(age, 1),
                "lead_before_kickoff_min": round(lead, 1)}
    return {**base, "status": CONFIRMED_STARTER, "confirmed_at": latest["observed_at"], "reason": None,
            "age_min": round(age, 1), "lead_before_kickoff_min": round(lead, 1)}


def resolve_game(records: list[dict], *, game_id: str, teams, kickoff, as_of, max_age_min: float = MAX_AGE_AT_DECISION_MIN,
                 max_lead_min: float = MAX_LEAD_BEFORE_KICKOFF_MIN) -> dict:
    """{team: row} for the teams that have a visible record (absent team -> QB_UNKNOWN at the gate). A record is only ever matched to the
    game_id and a team in ``teams`` (the game's own two teams), so another game's confirmation, or a team that is not playing in this
    game, can never confirm anything here."""
    out = {}
    for t in teams:
        if not t:
            continue
        row = resolve_team(records, game_id=game_id, team=t, kickoff=kickoff, as_of=as_of, max_age_min=max_age_min, max_lead_min=max_lead_min)
        if row is not None:
            out[t] = row
    return out


def resolve_slate(records: list[dict], games: list[dict], *, as_of, max_age_min: float = MAX_AGE_AT_DECISION_MIN,
                  max_lead_min: float = MAX_LEAD_BEFORE_KICKOFF_MIN) -> dict:
    """{game_id: {team: row}} for every game in the packet. ``games`` entries need game_id, home_team, away_team, kickoff_utc."""
    return {g["game_id"]: resolve_game(records, game_id=g["game_id"], teams=[g.get("home_team"), g.get("away_team")],
                                       kickoff=g.get("kickoff_utc"), as_of=as_of, max_age_min=max_age_min, max_lead_min=max_lead_min)
            for g in games}


def coverage(resolved: dict, games: list[dict], *, as_of) -> dict:
    """Counts only (public-safe): how many games have BOTH quarterbacks confirmed, and why each other game does not."""
    rows, confirmed = [], 0
    reasons: dict = {}
    for g in games:
        gid = g["game_id"]
        per = resolved.get(gid, {})
        sides = {}
        for t in (g.get("home_team"), g.get("away_team")):
            r = per.get(t)
            sides[t] = "ABSENT" if r is None else (r["status"] if r["status"] != UNKNOWN else f"UNKNOWN:{r.get('reason')}")
        both = all(s == CONFIRMED_STARTER for s in sides.values()) and len(sides) == 2
        confirmed += 1 if both else 0
        if not both:
            for t, s in sides.items():
                if s != CONFIRMED_STARTER:
                    reasons[s] = reasons.get(s, 0) + 1
        rows.append({"game_id": gid, "kickoff_utc": g.get("kickoff_utc"), "both_confirmed": both, "teams": sides})
    return {"schema": "nfl-qb-coverage.v1", "module_version": MODULE_VERSION, "as_of": parse_ts(as_of).isoformat() if parse_ts(as_of) else None,
            "games": len(games), "games_both_qbs_confirmed": confirmed, "games_blocked_qb": len(games) - confirmed,
            "team_slots_not_confirmed_by_reason": dict(sorted(reasons.items())), "max_age_at_decision_min": MAX_AGE_AT_DECISION_MIN,
            "max_lead_before_kickoff_min": MAX_LEAD_BEFORE_KICKOFF_MIN, "per_game": rows}


def new_record(*, record_id: str, game_id: str, team: str, qb_player_id: str, status: str, source_type: str, source_ref: str,
               observed_at: str, captured_at: datetime, captured_by: str, qb_name: str | None = None,
               supersedes: list[str] | None = None) -> dict:
    """Build a record dict for the appender; ``captured_at`` is supplied by the caller's clock, never defaulted here."""
    rec = {"record_id": record_id, "game_id": game_id, "team": team, "qb_player_id": qb_player_id, "status": status,
           "source_type": source_type, "source_ref": source_ref, "observed_at": observed_at,
           "captured_at": captured_at.isoformat(), "captured_by": captured_by}
    if qb_name:
        rec["qb_name"] = qb_name
    if supersedes:
        rec["supersedes"] = list(supersedes)
    return rec


__all__ = ["SCHEMA", "CONFIRMED_STARTER", "EXPECTED_UNCONFIRMED", "OUT", "UNKNOWN", "CONFIRMING_SOURCE_TYPES",
           "NON_CONFIRMING_SOURCE_TYPES", "MAX_AGE_AT_DECISION_MIN", "MAX_LEAD_BEFORE_KICKOFF_MIN", "validate_records", "load_records_file", "resolve_team",
           "resolve_game", "resolve_slate", "coverage", "new_record"]
