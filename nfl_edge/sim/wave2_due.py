"""Which Wave-2 capture windows are open, owed or missed -- stdlib only, so the horizon conductor can ask it.

RESEARCH_ONLY plumbing. It decides nothing about any prediction: the capture workflow's own gate
(`scripts/sim/wave2_prospective.py --check-only`) still decides what is captured, and records stay write-once.
The windows and the PROSPECTIVE CUTOFF are the frozen ones (PREREGISTRATION.md, PROSPECTIVE_PROTOCOL.md); tests
assert they equal the runner's and the scorer's constants.
"""
from __future__ import annotations

from datetime import datetime, timedelta

PROSPECTIVE_CUTOFF = "2026-10-05T16:14:02+00:00"
WINDOWS = {"EARLY": (90, 240), "LATE": (30, 90)}            # minutes before kickoff, (lo, hi]
RECORD_PREFIX = "data/research/wave2/"


def _ts(x) -> datetime:
    t = x if isinstance(x, datetime) else datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError(f"timezone-naive instant {x!r}")
    return t


def parse_record_name(name: str):
    """<game_id>.<window>.<run_id>.wave2.json.gz -> (game_id, window, run_id), else None (same rule as the runner)."""
    parts = name.replace("\\", "/").split("/")[-1].split(".")
    if len(parts) >= 5 and parts[1] in WINDOWS and parts[-3:] == ["wave2", "json", "gz"]:
        return parts[0], parts[1], parts[2]
    return None


def window_at(kickoff, now) -> str | None:
    mins = (_ts(kickoff) - _ts(now)).total_seconds() / 60.0
    for name, (lo, hi) in WINDOWS.items():
        if lo < mins <= hi:
            return name
    return None


def window_bounds(kickoff, window: str) -> tuple[datetime, datetime]:
    """(opens, closes): the window is open for opens <= t < closes."""
    lo, hi = WINDOWS[window]
    ko = _ts(kickoff)
    return ko - timedelta(minutes=hi), ko - timedelta(minutes=lo)


def due(games, now, seen: set, cutoff: str = PROSPECTIVE_CUTOFF) -> list:
    """['<game_id>:<WINDOW>', ...] for post-cutoff games inside a window with no record for that window yet.
    `games`: dicts with game_id and kickoff_utc (datetime or ISO); `seen`: {(game_id, window)}."""
    pc = _ts(cutoff)
    out = []
    for g in games or []:
        ko = g.get("kickoff_utc")
        if not ko or not g.get("game_id"):
            continue
        ko = _ts(ko)
        if ko <= pc:
            continue
        w = window_at(ko, now)
        if w and (g["game_id"], w) not in seen:
            out.append(f"{g['game_id']}:{w}")
    return sorted(out)


def seen_from_names(names) -> set:
    return {(p[0], p[1]) for p in (parse_record_name(n) for n in names) if p}
