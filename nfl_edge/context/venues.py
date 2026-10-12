"""Which stadium a game is actually played in, and what kind of roof it has. Stdlib only.

Two upstream facts cannot be taken from the nflverse schedule as published:

* **The venue.** nflverse marks some international games as an ordinary Home game and even keeps the home
  team's `stadium_id` (2026_05_PHI_JAX: location "Home", stadium_id "JAX00", stadium "Tottenham Hotspur
  Stadium"). Neither the Neutral flag nor the stadium id says the game left Jacksonville; only the stadium
  NAME does. A forecast looked up from the home team's coordinates is then the forecast for the wrong city.
* **The roof.** nflverse leaves `roof` blank for a retractable-roof stadium until the open/closed decision is
  made, so a blank roof is not "outdoors". The physical roof type lives in `config/stadiums.json`.

Both the context capture (what to fetch) and the handicap packet (what to show) read this module, so they
cannot disagree about either fact.
"""
from __future__ import annotations

import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STADIUMS_PATH = os.path.join(ROOT, "config", "stadiums.json")

ROOF_TYPES = ("dome", "retractable", "open")

# The venue verdicts. HOME_STADIUM is the only one under which the home team's coordinates are the venue's.
HOME_STADIUM = "HOME_STADIUM"
OTHER_VENUE = "OTHER_VENUE"
NO_CONFIG = "NO_CONFIG"                     # the home team has no entry in config/stadiums.json
UNVERIFIED = "UNVERIFIED"                   # the schedule names no stadium at all; nothing contradicts home

_CACHE: dict = {}


def load_stadiums(path: str | None = None) -> dict:
    """config/stadiums.json keyed by team code (the `_note` keys dropped). {} when the file is absent."""
    p = path or STADIUMS_PATH
    if p not in _CACHE:
        try:
            with open(p) as f:
                raw = json.load(f)
        except (OSError, ValueError):
            raw = {}
        _CACHE[p] = {k: v for k, v in raw.items() if not k.startswith("_") and isinstance(v, dict)}
    return _CACHE[p]


def _norm(name) -> str:
    s = str(name or "").strip().lower().replace("’", "'").replace("‘", "'")
    return " ".join(s.split())


def venue_check(home_team: str | None, stadium: str | None, stadium_id: str | None, stadiums: dict) -> dict:
    """Is the scheduled venue the home team's own stadium? Independent of nflverse's Neutral flag.

    A schedule stadium NAME that is neither the configured name nor one of its known aliases is another venue,
    even when the stadium id matches (the London case above). A renamed home stadium therefore fails closed
    (no home forecast is attached) until the new name is added to `aliases`, and the reason says so.
    """
    st = (stadiums or {}).get(home_team or "")
    if not st:
        return {"venue": NO_CONFIG, "home_stadium": None,
                "reason": f"no config/stadiums.json entry for home team {home_team!r}"}
    names = {_norm(st.get("stadium"))} | {_norm(a) for a in st.get("aliases") or []}
    sid_cfg, sid = str(st.get("stadium_id") or ""), str(stadium_id or "")
    if not _norm(stadium) and not sid:
        return {"venue": UNVERIFIED, "home_stadium": st.get("stadium"),
                "reason": "the schedule names no stadium; assumed to be the home team's stadium"}
    if sid and sid_cfg and sid != sid_cfg:
        return {"venue": OTHER_VENUE, "home_stadium": st.get("stadium"),
                "reason": (f"scheduled stadium id {sid} ({stadium}) is not {home_team}'s home stadium "
                           f"{sid_cfg} ({st.get('stadium')})")}
    if _norm(stadium) and _norm(stadium) not in names:
        return {"venue": OTHER_VENUE, "home_stadium": st.get("stadium"),
                "reason": (f"scheduled stadium {stadium!r} is not {home_team}'s home stadium "
                           f"{st.get('stadium')!r} (nor a known alias of it in config/stadiums.json)")}
    return {"venue": HOME_STADIUM, "home_stadium": st.get("stadium"), "reason": None}


def roof_type(home_team: str | None, stadiums: dict) -> str | None:
    """The home stadium's physical roof (dome / retractable / open), or None when it is not configured."""
    rt = ((stadiums or {}).get(home_team or "") or {}).get("roof_type")
    return rt if rt in ROOF_TYPES else None
