"""When was a pregame projection actually COMPUTED, and was that before its game's kickoff?

Shared by the player autopsy (`player_autopsy.py`, rule autopsy-1.1.0) and the full-board research table
(`nfl_edge/research/board.py`). A neutral module so the board's point-in-time joins do not import the autopsy.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def _ts(s):
    if not s:
        return None
    try:
        t = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        try:
            t = datetime.strptime(str(s), "%Y%m%dT%H%M%SZ")
        except ValueError:
            return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def generated_at(row: dict):
    """When the projection on this row was actually COMPUTED: the later of its pricing run's instant (`run_id`
    is the run's UTC start stamp) and the anatomy's own `evaluated_at`.

    This is not `observed_at`. The capture is change-suppressed, so the 2-hourly pricer keeps re-pricing a game's
    LAST pregame quote for days after the game has been played: the quote is pregame (`minutes_to_kickoff` stays
    87.5) but the model inputs are read at run time -- availability above all, which on 2026_02_NYG_LA flips a
    receiver from QUESTIONABLE to OUT the morning after the game he was hurt in. Such a row is a postgame
    reading and is never autopsy evidence. None when neither stamp parses (the row is then not trusted)."""
    stamps = [t for t in (_ts(row.get("run_id")), _ts(row.get("evaluated_at"))) if t is not None]
    return max(stamps) if stamps else None


def kickoff_of(row: dict):
    """The row's kickoff: its own `kickoff_utc`, else observed_at + minutes_to_kickoff."""
    ko = _ts(row.get("kickoff_utc"))
    if ko is not None:
        return ko
    obs, mtk = _ts(row.get("observed_at")), _f(row.get("minutes_to_kickoff"))
    if obs is None or mtk is None:
        return None
    return obs + timedelta(minutes=mtk)


def generated_pregame(row: dict) -> bool:
    """True only when the row provably was computed strictly before its game's kickoff."""
    g, ko = generated_at(row), kickoff_of(row)
    return g is not None and ko is not None and g < ko
