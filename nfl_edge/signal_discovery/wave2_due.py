"""Which Signal Lab Wave-2 stages are owed -- stdlib only, so the horizon conductor can ask it.

RESEARCH_ONLY plumbing shared by the horizon conductor (target SIGNAL_LAB) and the job's own gate
(`scripts/research/signal_lab_wave2.py due`), so the two can never disagree. It decides nothing about a signal.
Records are write-once files `data/research/signal_lab_wave2/<observations|entries|settlements>/<season>/<game_id>.json`.
"""

from __future__ import annotations

from datetime import datetime

SEASON = 2026
WEEK_ON_OR_AFTER = 6
RECORD_PREFIX = "data/research/signal_lab_wave2"
KINDS = {"observations": "OBSERVATION", "entries": "ENTRY", "settlements": "SETTLEMENT"}
DIRS = {v: k for k, v in KINDS.items()}
OBSERVE_FROM_MIN, OBSERVE_UNTIL_MIN = 300.0, 20.0
SETTLE_AFTER_MIN = 300.0
GIVE_UP_HOURS = 168.0


def _ts(x) -> datetime:
    t = x if isinstance(x, datetime) else datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError(f"timezone-naive instant {x!r}")
    return t


def record_name(kind: str, game_id: str, season: int = SEASON) -> str:
    return f"{RECORD_PREFIX}/{DIRS[kind]}/{season}/{game_id}.json"


def seen_from_names(names) -> set:
    """{(KIND, game_id)} from published paths (names only; nothing is opened)."""
    out = set()
    for n in names or ():
        parts = str(n).replace("\\", "/").split("/")
        if len(parts) >= 3 and parts[-3] in KINDS and parts[-1].endswith(".json"):
            out.add((KINDS[parts[-3]], parts[-1][: -len(".json")]))
    return out


def in_population(g: dict, weeks=None) -> bool:
    if g.get("season") != SEASON or g.get("game_type", "REG") != "REG":
        return False
    w = g.get("week")
    return (w in weeks) if weeks else (w is not None and w >= WEEK_ON_OR_AFTER)


def due(games, now, seen: set, weeks=None) -> dict[str, list[str]]:
    """{"observe": [...], "enter": [...], "settle": [...]} game ids owed at `now`."""
    now = _ts(now)
    out: dict[str, list[str]] = {"observe": [], "enter": [], "settle": []}
    for g in games or []:
        if not g.get("game_id") or not g.get("kickoff_utc") or not in_population(g, weeks):
            continue
        gid = g["game_id"]
        m = (_ts(g["kickoff_utc"]) - now).total_seconds() / 60.0
        obs, ent, st = ((k, gid) in seen for k in ("OBSERVATION", "ENTRY", "SETTLEMENT"))
        if not obs and OBSERVE_UNTIL_MIN <= m <= OBSERVE_FROM_MIN:
            out["observe"].append(gid)
        if m <= 0 and not ent and -m <= GIVE_UP_HOURS * 60:
            out["enter"].append(gid)
        if ent and not st and -m >= SETTLE_AFTER_MIN:
            out["settle"].append(gid)
    return {k: sorted(v) for k, v in out.items()}


def owed_ids(d: dict[str, list[str]]) -> list[str]:
    return sorted({f"{k}:{g}" for k, v in d.items() for g in v})
