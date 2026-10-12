"""A1B -- verified pregame inactives (GAME SCRIPT V2 Wave 2, separately preregistered). RESEARCH_ONLY.

Preregistration: research/game_script_v2/wave2/PREREGISTRATION_ADDENDUM_B_A1B.md. A1 (the frozen Wave-2 arm) is
untouched: A1B has its own records, its own source snapshots, its own scorer and its own sample, and never pools
with A1.

Why A1B exists: A1 may claim T0_INACTIVES only when the nflverse weekly roster read at its cutoff already carries
game-day INA statuses. nflverse fills INA retrospectively on a roughly daily cycle (2026 week 5: no INA rows at all
on 2026-10-08 14:34 GMT; week 4: 199, added after those games), so A1's T0 condition can essentially never hold
prospectively. A1B instead freezes its OWN timestamped copies of a candidate pregame source and may use a copy only
if this repository retrieved it before the A1B cutoff.

The source (ESPN core per-competition roster, `didNotPlay` flag -- amendment B1; the `active` flag named in addendum
B is False for every entry before kickoff and is not a game-day list) is a CANDIDATE until the preregistered source
qualification passes (addendum B section 4, restarted by amendment B1). Everything here fails closed:

  * a snapshot proves availability only by OUR retrieval instant -- never by any timestamp the source asserts;
  * only snapshots parsed by the current SOURCE_VERSION are usable; an earlier version's snapshots are kept as
    written and never re-read (no re-derivation of an old observation under a new rule);
  * a team whose response is not HTTP 200 is an OUTAGE; a 200 without a plausible flagged-inactive count (4-12) is
    NOT_PUBLISHED / IMPLAUSIBLE; neither ever produces an inactive (or an active) player;
  * only snapshots retrieved at or after kickoff - RELEASE_FLOOR_MIN and at or before the capture cutoff are usable;
    nothing is ever snapshotted after kickoff;
  * a projected player whose ESPN id cannot be resolved makes the whole team unusable (no guessing by name).

The stdlib part (fetching, parsing, choosing, mapping) is importable by the conductor; nothing here reads an outcome.
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

A1B_VERSION = "wave2-a1b-1.0.0"
SOURCE_VERSION = "a1b-source-1.1.0"                 # amendment B1: didNotPlay (1.0.0 read `active`; never usable)
SOURCE_NAME = "espn_core_competition_roster_didnotplay_flag"
UA = "nfl-edge-finder wave2-a1b research (read-only; github.com/chmoses98/nfl-edge-finder)"
CORE = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
COMPETITION_URL = CORE + "/events/{eid}/competitions/{eid}"
ROSTER_URL = CORE + "/events/{eid}/competitions/{eid}/competitors/{tid}/roster"

PROSPECTIVE_CUTOFF = "2026-10-05T16:14:02+00:00"     # Wave 2's; A1B adds its own start (addendum B section 6)
SNAPSHOT_WINDOW = (0.0, 150.0)       # minutes before kickoff: (lo, hi]; never after kickoff
SNAPSHOT_MIN_GAP_MIN = 10.0          # at most one snapshot per game per 10 minutes
A1B_WINDOW = (35.0, 80.0)            # A1B capture cutoff: minutes before kickoff, (lo, hi]
RELEASE_FLOOR_MIN = 100.0            # a usable snapshot is retrieved no earlier than kickoff - 100 min
LAST_CHANCE_MIN = 45.0               # at or inside this, a capture with no usable source writes NO_USABLE_SOURCE
PLAUSIBLE_INACTIVES = (4, 12)        # per team; outside it the flag is not a game-day inactive list
SRC_PREFIX = "data/research/wave2_a1b/sources/"
REC_PREFIX = "data/research/wave2_a1b/records/"

USABLE, OUTAGE, NOT_PUBLISHED, IMPLAUSIBLE = "USABLE", "OUTAGE", "NOT_PUBLISHED", "IMPLAUSIBLE"
INACTIVE_STATE = "INACTIVE_CONFIRMED"


def _ts(x) -> datetime:
    t = x if isinstance(x, datetime) else datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError(f"timezone-naive instant {x!r}")
    return t


def minutes_to(kickoff, at) -> float:
    return (_ts(kickoff) - _ts(at)).total_seconds() / 60.0


# ------------------------------------------------------------------------------------------ fetching (Actions only)
def fetch(url: str, *, timeout: int = 40, opener=None) -> dict:
    """One HTTP GET with OUR timestamps around it, the status, the source's own headers and the raw bytes' sha256.
    Never raises: a failure is a returned OUTAGE."""
    t0 = datetime.now(timezone.utc)
    meta = {"url": url, "requested_at": t0.isoformat()}
    try:
        if opener is not None:
            status, headers, raw = opener(url)
        else:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                status, headers, raw = getattr(r, "status", 200), dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        status, headers, raw = e.code, dict(e.headers or {}), b""
        meta["error"] = f"HTTPError {e.code}"
    except Exception as e:  # noqa: BLE001 -- a failed fetch is an observation (OUTAGE), not a crash
        status, headers, raw = None, {}, b""
        meta["error"] = f"{type(e).__name__}: {str(e)[:160]}"
    meta.update(status=status, retrieved_at=datetime.now(timezone.utc).isoformat(),
                source_headers={k: v for k, v in (headers or {}).items() if k.lower() in ("date", "last-modified", "etag", "age", "cache-control")},
                sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    try:
        body = json.loads(raw.decode()) if raw else None
    except ValueError:
        body, meta["error"] = None, meta.get("error") or "response was not JSON"
    return {"meta": meta, "body": body}


# ------------------------------------------------------------------------------------------ parsing
def parse_competition(body) -> dict:
    """{'home': team_id, 'away': team_id} from the core competition document (ids only)."""
    out = {}
    for c in (body or {}).get("competitors") or []:
        if isinstance(c, dict) and c.get("homeAway") in ("home", "away") and c.get("id") is not None:
            out[c["homeAway"]] = str(c["id"])
    return out


_ATH = re.compile(r"/athletes/(\d+)")


def _espn_id(entry: dict):
    if entry.get("playerId") is not None:
        return str(entry["playerId"])
    ref = (entry.get("athlete") or {}).get("$ref") if isinstance(entry.get("athlete"), dict) else None
    m = _ATH.search(ref or "")
    return m.group(1) if m else None


def parse_roster(fetched: dict) -> dict:
    """Per-team reading of the roster `didNotPlay` flag (amendment B1). Only players explicitly flagged
    didNotPlay == True are named; the `active` flag is ignored (False for every entry before kickoff)."""
    meta, body = fetched.get("meta") or {}, fetched.get("body")
    if meta.get("status") != 200 or body is None:
        return {"state": OUTAGE, "reason": meta.get("error") or f"HTTP {meta.get('status')}", "inactive_espn_ids": [],
                "n_entries": 0, "n_flagged": 0, "unidentified_inactive": 0}
    entries = [e for e in (body.get("entries") or body.get("items") or []) if isinstance(e, dict)]
    flagged = [e for e in entries if isinstance(e.get("didNotPlay"), bool)]
    ids, unidentified = set(), 0
    for e in flagged:
        if e["didNotPlay"] is True:
            i = _espn_id(e)
            if i is None:
                unidentified += 1
            else:
                ids.add(i)
    n = len(ids) + unidentified
    lo, hi = PLAUSIBLE_INACTIVES
    if not flagged or n == 0:
        state, reason = NOT_PUBLISHED, "HTTP 200 but no player flagged inactive"
    elif not lo <= n <= hi or unidentified:
        state, reason = IMPLAUSIBLE, (f"{n} flagged inactive (plausible {lo}-{hi})" if not lo <= n <= hi
                                      else f"{unidentified} flagged inactive without an ESPN id")
    else:
        state, reason = USABLE, None
    return {"state": state, "reason": reason, "inactive_espn_ids": sorted(ids), "n_entries": len(entries),
            "n_flagged": len(flagged), "unidentified_inactive": unidentified}


def snapshot_document(game: dict, competition: dict, rosters: dict, *, run_id: str) -> dict:
    """The write-once source snapshot for one game. `rosters`: {'home'|'away': fetched}. Raw bodies are kept so
    the reading can be re-derived; OUR retrieval instants are the only availability evidence."""
    teams = {}
    for side in ("home", "away"):
        f = rosters.get(side) or {"meta": {"status": None, "error": "competitor id not resolved"}, "body": None}
        teams[side] = {"team": game[f"{side}_team"], "fetch": f["meta"], "reading": parse_roster(f), "raw": f.get("body")}
    retrieved = [t["fetch"].get("retrieved_at") for t in teams.values() if t["fetch"].get("retrieved_at")]
    last = max(retrieved) if retrieved else None
    return {"a1b_source_version": SOURCE_VERSION, "source": SOURCE_NAME, "run_id": run_id, "game_id": game["game_id"],
            "event_id": str(game["event_id"]), "kickoff_utc": _ts(game["kickoff_utc"]).isoformat(),
            "retrieved_at": last, "minutes_to_kickoff": round(minutes_to(game["kickoff_utc"], last), 2) if last else None,
            "competition_fetch": competition["meta"], "competition_ids": parse_competition(competition.get("body")),
            "teams": teams, "research_only": True, "betting_authority": "NONE",
            "note": "availability is proven only by retrieved_at (this repository's clock); source headers are recorded, never trusted"}


# ------------------------------------------------------------------------------------------ choosing a usable snapshot
def current_version(snaps: list) -> list:
    return [s for s in snaps or [] if s.get("a1b_source_version") == SOURCE_VERSION]


def snapshot_usable_at(snap: dict, cutoff) -> bool:
    """Parsed by the current SOURCE_VERSION, retrieved (by us) at or after kickoff - RELEASE_FLOOR_MIN, at or before
    the cutoff, before kickoff, and both teams USABLE."""
    if snap.get("a1b_source_version") != SOURCE_VERSION:
        return False
    try:
        r, ko, c = _ts(snap["retrieved_at"]), _ts(snap["kickoff_utc"]), _ts(cutoff)
    except (KeyError, TypeError, ValueError):
        return False
    if not (ko - timedelta(minutes=RELEASE_FLOOR_MIN) <= r <= c and r < ko):
        return False
    return all((snap["teams"].get(s) or {}).get("reading", {}).get("state") == USABLE for s in ("home", "away"))


def choose_snapshot(snaps: list, cutoff) -> tuple:
    """(the latest usable snapshot at the cutoff or None, a diagnosis distinguishing OUTAGE from NOT_PUBLISHED).
    Snapshots of an earlier SOURCE_VERSION are not evidence of anything here."""
    snaps = current_version(snaps)
    usable = [s for s in snaps if snapshot_usable_at(s, cutoff)]
    if usable:
        return max(usable, key=lambda s: (s["retrieved_at"], s.get("run_id", ""))), "USABLE"
    in_window = [s for s in snaps if s.get("retrieved_at") and _ts(s["retrieved_at"]) <= _ts(cutoff)
                 and _ts(s["retrieved_at"]) >= _ts(s["kickoff_utc"]) - timedelta(minutes=RELEASE_FLOOR_MIN)]
    if not in_window:
        return None, "NO_SNAPSHOT_IN_WINDOW"
    states = {(s["teams"].get(x) or {}).get("reading", {}).get("state") for s in in_window for x in ("home", "away")}
    if states <= {OUTAGE}:
        return None, "SOURCE_OUTAGE"
    return None, "NOT_PUBLISHED_OR_IMPLAUSIBLE"


# ------------------------------------------------------------------------------------------ identity + treatment
def map_inactives(snap: dict, team_players: dict, espn_of: dict) -> dict:
    """team -> {'inactive': set of gsis ids, 'usable': bool, 'unmapped_projected': [...], 'unmatched_inactive': n}.
    `team_players`: team -> projected gsis ids; `espn_of`: gsis -> espn id. A projected player without an ESPN id
    makes the team unusable: whether that player was declared inactive cannot be known. So does an ESPN id shared by
    two projected players (a conflicting identity)."""
    out = {}
    for side in ("home", "away"):
        t = snap["teams"][side]
        team, ids = t["team"], set(t["reading"]["inactive_espn_ids"])
        players = list(team_players.get(team, []))
        unmapped = sorted(p for p in players if not espn_of.get(p))
        seen, conflicts = {}, set()
        for p in players:
            e = espn_of.get(p)
            if e:
                if str(e) in seen and seen[str(e)] != p:
                    conflicts.update({p, seen[str(e)]})
                seen[str(e)] = p
        inactive = {p for p in players if espn_of.get(p) and str(espn_of[p]) in ids}
        out[team] = {"inactive": inactive, "usable": not unmapped and not conflicts, "unmapped_projected": unmapped,
                     "conflicting_ids": sorted(conflicts),
                     "unmatched_inactive": len(ids - {str(espn_of[p]) for p in players if espn_of.get(p)})}
    return out


def a1b_states(states, player_ids, inactive: set):
    """Confirmed inactive -> INACTIVE_CONFIRMED (row kept: a certain zero); QUESTIONABLE not on a usable list ->
    EXPECTED_ACTIVE (the list is complete for a usable team); every other state unchanged."""
    return [INACTIVE_STATE if p in inactive else ("EXPECTED_ACTIVE" if s == "QUESTIONABLE" else s)
            for s, p in zip(states, player_ids)]


# ------------------------------------------------------------------------------------------ due rules (conductor)
def parse_name(name: str):
    """sources: <game_id>.<run_id>.a1b_src.json.gz ; records: <game_id>.A1B.<run_id>.a1b.json.gz"""
    base = name.replace("\\", "/").split("/")[-1]
    p = base.split(".")
    if len(p) == 5 and p[2:] == ["a1b_src", "json", "gz"]:
        return ("SRC", p[0], p[1])
    if len(p) == 6 and p[1] == "A1B" and p[3:] == ["a1b", "json", "gz"]:
        return ("REC", p[0], p[2])
    return None


def due(games, now, names) -> dict:
    """{'snapshot': [...game ids], 'capture': [...game ids]} owed now. `names`: market-data paths under the A1B prefixes."""
    pc = _ts(PROSPECTIVE_CUTOFF)
    last_src, recs = {}, set()
    for n in names or []:
        p = parse_name(n)
        if not p:
            continue
        if p[0] == "SRC":
            try:
                t = datetime.strptime(p[2], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            last_src[p[1]] = max(last_src.get(p[1], t), t)
        else:
            recs.add(p[1])
    snap, cap = [], []
    for g in games or []:
        ko = g.get("kickoff_utc")
        if not ko or not g.get("game_id") or _ts(ko) <= pc:
            continue
        m = minutes_to(ko, now)
        if SNAPSHOT_WINDOW[0] < m <= SNAPSHOT_WINDOW[1]:
            last = last_src.get(g["game_id"])
            if last is None or (_ts(now) - last).total_seconds() >= SNAPSHOT_MIN_GAP_MIN * 60:
                snap.append(g["game_id"])
        if A1B_WINDOW[0] < m <= A1B_WINDOW[1] and g["game_id"] not in recs:
            cap.append(g["game_id"])
    return {"snapshot": sorted(snap), "capture": sorted(cap)}
