"""OFFICIAL INACTIVES, as a research observation that can only ever ADD information.

`scripts/data/probe_inactives.py` explains why this repo has never had an inactives collector, and the reason is
correct: an availability feed that silently returns nothing does not degrade to "no information", it degrades to
"everyone is playing", and that is the one answer that removes the protection a fail-closed prop gate exists to
give. A scraper written on the strength of a plausible-looking endpoint would be worse than the gap it fills.

This module is built so that failure mode cannot happen, by construction rather than by care:

    IT NEVER DECLARES ANYONE ACTIVE.  The only state it can produce is INACTIVE_CONFIRMED, for a player the
    source explicitly named. A player's ABSENCE from the list produces nothing at all -- not EXPECTED_ACTIVE,
    not a probability, not a row. So an empty response, a 404, a schema change, or a wrong event id all yield
    zero observations, which is exactly the same as not having run.

    IT IS PLAUSIBILITY-GATED PER TEAM.  An NFL team declares about seven inactives on a normal gameday. A team
    whose list has 0 or 40 names is not an inactive list whatever the field is called, so the whole team's
    observation is marked UNUSABLE and carries no player rows. A partially-parsed team never becomes a
    half-true roster.

    IT IS RESEARCH-ONLY AND SAYS SO ON EVERY ROW.  `betting_authorized` is False and
    `feeds_availability_gate` is False on every observation. Nothing here is wired into
    nfl_edge/settlement/availability.py, whose INACTIVE_CONFIRMED state remains unpopulated by design; promoting
    this source to that gate is a separate, deliberate decision that needs several game days of probe output.

    IT CANNOT BE FAKED AFTER THE FACT.  An observation made after kickoff is labelled POSTGAME_OBSERVATION and
    is excluded from anything that claims to be pregame knowledge. Reconstructing the inactive list after the
    game and presenting it as having been known at T-90 is the specific dishonesty this guards against.

Source: ESPN's public summary endpoint (`site.api.espn.com/.../summary?event=`), which exposes an `inactives`
block for some events, plus the per-competitor roster `active` flag as a secondary reading. Both are free and
already probed by this repo. Whatever the source says is preserved verbatim in `raw_status` -- out, doubtful,
questionable, injured reserve, PUP, suspension, healthy scratch, practice-squad elevation -- rather than being
flattened, because the distinction between "IR" and "healthy scratch" is exactly what makes the record useful
later.

Version: inactives-1.0.0.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone

INACTIVES_VERSION = "inactives-1.0.0"
UA = "nfl-edge-finder shadow-v2 inactives (read-only research; github.com/chmoses98/nfl-edge-finder)"
SUMMARY_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={eid}"

INACTIVE_CONFIRMED = "INACTIVE_CONFIRMED"          # the ONLY state this module can emit for a player
TEAM_USABLE, TEAM_UNUSABLE, TEAM_ABSENT = "USABLE", "UNUSABLE_IMPLAUSIBLE_COUNT", "NO_INACTIVES_BLOCK"
PREGAME, POSTGAME = "PREGAME_OBSERVATION", "POSTGAME_OBSERVATION"
HIGH, MEDIUM, LOW = "HIGH", "MEDIUM", "LOW"

# An NFL team declares about seven inactives (5-9 with elevations and short weeks). Outside this the block is
# not an inactive list, whatever ESPN calls the field. Same bounds the repo's own probe uses.
PLAUSIBLE_INACTIVES = (4, 12)
# The official list is published about 90 minutes before kickoff. Earlier than three hours out it cannot be the
# official list; after kickoff it is not pregame knowledge at all.
WINDOW_EARLY_MIN = 180.0
WINDOW_LATE_MIN = 0.0


def _now():
    return datetime.now(timezone.utc)


def _dt(s):
    if not s:
        return None
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def fetch_summary(event_id: str, *, timeout: int = 45, opener=None) -> tuple[dict | None, str | None, dict]:
    url = SUMMARY_URL.format(eid=event_id)
    t0 = _now()
    meta = {"url": url, "requested_at": t0.isoformat()}
    try:
        if opener is not None:
            body = opener(url)
        else:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = json.loads(r.read().decode())
        meta.update(status=200, retrieved_at=_now().isoformat(),
                    latency_ms=round((_now() - t0).total_seconds() * 1000, 1))
        return body, None, meta
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError, TimeoutError) as exc:
        meta.update(status=getattr(exc, "code", None), error=f"{type(exc).__name__}: {str(exc)[:160]}",
                    retrieved_at=_now().isoformat())
        return None, meta["error"], meta


def _team_code(node: dict) -> str | None:
    t = node.get("team") or {}
    return (t.get("abbreviation") or t.get("shortDisplayName") or "").strip().upper() or None


def parse_inactives(summary: dict | None) -> list:
    """Teams and the players each explicitly named as inactive. Nothing else is inferred."""
    out = []
    for block in ((summary or {}).get("inactives") or []):
        team = _team_code(block)
        players = []
        for a in (block.get("athletes") or []):
            ath = a.get("athlete") or {}
            players.append({"player_name": (ath.get("displayName") or ath.get("fullName") or "").strip() or None,
                            "espn_id": str(ath.get("id")) if ath.get("id") is not None else None,
                            "position": ((ath.get("position") or {}).get("abbreviation")
                                         or (a.get("position") or {}).get("abbreviation")),
                            "raw_status": (a.get("status") or {}).get("name") or (a.get("status") or {}).get("type")
                            or a.get("reason") or "inactive"})
        out.append({"team": team, "players": players})
    return out


def observations(*, game_id: str, event_id: str, kickoff_utc, summary: dict | None, fetch_meta: dict,
                 observed_at=None) -> dict:
    """The frozen inactives record for one game: only confirmed-inactive players, only from a usable team block."""
    obs = _dt(observed_at) or _now()
    ko = _dt(kickoff_utc)
    minutes_to_kick = ((ko - obs).total_seconds() / 60.0) if ko else None
    evidence = POSTGAME if (minutes_to_kick is not None and minutes_to_kick < WINDOW_LATE_MIN) else PREGAME
    conf = LOW
    if minutes_to_kick is not None and WINDOW_LATE_MIN <= minutes_to_kick <= WINDOW_EARLY_MIN:
        conf = HIGH
    elif minutes_to_kick is not None and minutes_to_kick > WINDOW_EARLY_MIN:
        conf = MEDIUM                              # too early to be the official list; recorded, not trusted
    teams, rows = [], []
    blocks = parse_inactives(summary)
    if not blocks:
        teams.append({"team": None, "state": TEAM_ABSENT, "n": 0,
                      "reason": "the summary carries no inactives block for this event"})
    for b in blocks:
        n = len(b["players"])
        usable = PLAUSIBLE_INACTIVES[0] <= n <= PLAUSIBLE_INACTIVES[1]
        teams.append({"team": b["team"], "state": TEAM_USABLE if usable else TEAM_UNUSABLE, "n": n,
                      "reason": None if usable else
                      f"{n} names is outside the plausible {PLAUSIBLE_INACTIVES[0]}-{PLAUSIBLE_INACTIVES[1]} "
                      f"inactives a team declares: not read as an inactive list"})
        if not usable or evidence == POSTGAME:
            continue
        for p in b["players"]:
            rows.append({"inactives_version": INACTIVES_VERSION, "game_id": game_id, "event_id": str(event_id),
                         "team": b["team"], **p, "state": INACTIVE_CONFIRMED,
                         "source": "espn_summary_inactives", "source_url": fetch_meta.get("url"),
                         "source_retrieved_at": fetch_meta.get("retrieved_at"), "observed_at": obs.isoformat(),
                         "kickoff_utc": ko.isoformat() if ko else None,
                         "minutes_to_kickoff": round(minutes_to_kick, 1) if minutes_to_kick is not None else None,
                         "confidence": conf, "evidence_class": evidence,
                         # a player's ABSENCE from this list is never evidence of anything
                         "absence_is_not_evidence": True,
                         "feeds_availability_gate": False, "betting_authorized": False})
    return {"inactives_version": INACTIVES_VERSION, "game_id": game_id, "event_id": str(event_id),
            "observed_at": obs.isoformat(), "kickoff_utc": ko.isoformat() if ko else None,
            "minutes_to_kickoff": round(minutes_to_kick, 1) if minutes_to_kick is not None else None,
            "evidence_class": evidence, "confidence": conf, "teams": teams, "rows": rows,
            "n_confirmed_inactive": len(rows), "fetch": fetch_meta,
            "usable": any(t["state"] == TEAM_USABLE for t in teams) and evidence == PREGAME}


class InactivesBook:
    """Confirmed-inactive players, keyed by (game_id, espn_id) and by name. Absence answers UNKNOWN, never active."""

    def __init__(self, records=()):
        self.by_id, self.by_name, self.games = {}, {}, {}
        for rec in records:
            self.add(rec)

    def add(self, rec: dict):
        self.games[rec.get("game_id")] = {k: rec.get(k) for k in
                                          ("observed_at", "minutes_to_kickoff", "confidence", "evidence_class", "usable", "teams")}
        for r in (rec.get("rows") or ()):
            if r.get("espn_id"):
                self.by_id[(r["game_id"], str(r["espn_id"]))] = r
            if r.get("player_name"):
                self.by_name[(r["game_id"], r["player_name"].strip().lower())] = r

    def state(self, game_id: str, *, espn_id=None, player_name=None) -> dict:
        r = self.by_id.get((game_id, str(espn_id))) if espn_id else None
        if r is None and player_name:
            r = self.by_name.get((game_id, player_name.strip().lower()))
        if r is not None:
            return {"official_inactive_state": INACTIVE_CONFIRMED, "raw_status": r.get("raw_status"),
                    "source": r.get("source"), "source_retrieved_at": r.get("source_retrieved_at"),
                    "observed_at": r.get("observed_at"), "minutes_to_kickoff": r.get("minutes_to_kickoff"),
                    "confidence": r.get("confidence")}
        g = self.games.get(game_id)
        return {"official_inactive_state": "UNKNOWN",
                "reason": ("no usable inactives observation for this game" if not g or not g.get("usable")
                           else "the player was not named on the official inactive list; ABSENCE IS NOT EVIDENCE OF ACTIVITY"),
                "observed_at": (g or {}).get("observed_at"), "confidence": (g or {}).get("confidence")}
