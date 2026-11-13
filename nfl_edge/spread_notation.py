"""Human-facing spread notation for every NFL report (display only; never feeds math).

Standard (shared with SIFT ``src/lib/spreadNotation.ts``):
    pregame ``PHI -6.5``  = PHI projected/priced to win by 6.5
    postgame ``PHI -3``   = PHI actually won by 3
    if TOR is projected to beat PHI by 1.7 the label is ``TOR -1.7``, never ``PHI -1.7``.

Two native conventions exist in this repo and must not be confused:
    * HOME HANDICAP (sportsbook style, points ADDED to home; negative = home favoured):
      ``market_implied.implied_spread``, ``model_view.model_spread``, ``market_baseline.spread_home``.
    * HOME MARGIN (home score minus away score; positive = home favoured/won):
      simulator ``spread_home`` / ``center_spread_home``, nflverse ``spread_line``,
      ``projected_home_margin``, ``home_margin``, ``final_margin``.
"""
from __future__ import annotations

import math

PICKEM = "Pick'em"
MISSING = "--"


def _finite(value) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def team_spread_from_home_margin(value, home: str, away: str, decimals: int = 1) -> str:
    """HOME-minus-AWAY margin -> ``WINNER -N`` (positive = home)."""
    v = _finite(value)
    if v is None or not home or not away or home == away:
        return MISSING
    pts = round(abs(v), decimals)
    if pts == 0:
        return PICKEM
    shown = f"{pts:.{decimals}f}"
    if "." in shown:
        shown = shown.rstrip("0").rstrip(".")
    return f"{home if v > 0 else away} -{shown}"


def team_spread_from_home_handicap(value, home: str, away: str, decimals: int = 1) -> str:
    """Sportsbook HOME handicap -> ``FAVOURITE -N`` (negative = home favoured)."""
    v = _finite(value)
    return MISSING if v is None else team_spread_from_home_margin(-v, home, away, decimals)


def final_margin_label(home_score, away_score, home: str, away: str) -> str:
    """Postgame: ``PHI -3`` means PHI won by 3; a tie is Pick'em."""
    h, a = _finite(home_score), _finite(away_score)
    return MISSING if h is None or a is None else team_spread_from_home_margin(h - a, home, away, decimals=0)


def teams_from_game_id(game_id) -> tuple[str, str] | None:
    """nflverse ``SEASON_WEEK_AWAY_HOME`` -> (home, away); None when the id is not in that shape."""
    parts = str(game_id or "").split("_")
    if len(parts) != 4 or not parts[2] or not parts[3] or parts[2] == parts[3]:
        return None
    return parts[3], parts[2]
