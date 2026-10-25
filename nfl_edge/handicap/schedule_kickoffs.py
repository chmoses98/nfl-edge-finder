"""Scheduled kickoff instants from the nflverse schedule, keyed the way a Kalshi event ticker names a game.

WHY THIS EXISTS. The actual-wager postmortem takes each game's scheduled kickoff from the canonical close rows
(`actual_wager_postmortem.kickoffs_by_game`). The Shadow v2 settlement workflow that publishes those closes has been
hitting its 120-minute job limit (every scheduled run since at least 2026-10-23 ended CANCELLED inside the
"Settle every ready game" step), so no closes exist after week 4 and every week 5-7 wager came out with an UNKNOWN
phase: no pregame/live classification, no entry timing. The kickoff itself is not missing data -- it is in the schedule
the capture already caches -- so it is read from there when a close does not supply it.

This is a FALLBACK. A kickoff from a canonical close always wins (`merge_kickoffs`), and a disagreement between the two
is reported rather than resolved. It never invents a time: a game the schedule does not name gets no kickoff.

`gametime` in the nflverse schedule is US/Eastern wall time ("20:20" for the 2026-09-09 opener = 00:20Z).
"""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

_MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
_ET = ZoneInfo("America/New_York")

#: Kalshi event tickers and nflverse disagree about two franchises. Both sides are normalised before keys are compared.
_CANON = {"JAC": "JAX", "LAR": "LA", "WSH": "WAS", "OAK": "LV", "SD": "LAC", "STL": "LA"}


TEAMS = frozenset("ARI ATL BAL BUF CAR CHI CIN CLE DAL DEN DET GB HOU IND JAX KC LA LAC LV MIA MIN NE NO NYG NYJ PHI PIT SEA SF TB TEN WAS".split())


def canon_team(code: str) -> str:
    return _CANON.get(code, code)


def game_key_from_ticker_key(key: str | None) -> str | None:
    """'26OCT04JACCIN' -> '26OCT04JAXCIN' (teams canonicalised). Returns None for anything not a game key."""
    if not key or len(key) < 11 or not key[:2].isdigit() or key[2:5] not in _MONTHS or not key[5:7].isdigit():
        return None
    teams = key[7:]
    # Codes are 2-3 letters, so a bare length split is ambiguous ("NEJAC" is NE+JAC, not NEJ+AC). Only splits whose BOTH
    # halves are real franchises count, and an ambiguous or unmatched key returns None rather than a guess.
    found = {(canon_team(teams[:i]), canon_team(teams[i:])) for i in (2, 3)
             if canon_team(teams[:i]) in TEAMS and canon_team(teams[i:]) in TEAMS}
    if len(found) != 1:
        return None
    away, home = found.pop()
    return key[:7] + away + home


def kickoffs_from_schedule(text: str, season: int) -> dict:
    """{canonical game key -> ISO-8601 UTC kickoff} for one season from nflverse games.csv text."""
    out: dict = {}
    for row in csv.DictReader(io.StringIO(text)):
        if str(row.get("season")) != str(season):
            continue
        day, clock = (row.get("gameday") or "").strip(), (row.get("gametime") or "").strip()
        away, home = canon_team((row.get("away_team") or "").strip()), canon_team((row.get("home_team") or "").strip())
        if not day or not clock or not away or not home:
            continue                       # no time on the schedule is no kickoff, never a guessed one
        try:
            local = datetime.strptime(f"{day} {clock}", "%Y-%m-%d %H:%M").replace(tzinfo=_ET)
        except ValueError:
            continue
        d = local.date()
        key = f"{d:%y}{_MONTHS[d.month - 1]}{d.day:02d}{away}{home}"
        out[key] = local.astimezone(timezone.utc).isoformat().replace("+00:00", "+00:00")
    return out


def merge_kickoffs(from_closes: dict, from_schedule: dict) -> tuple:
    """(kickoffs, report). Close-derived kickoffs win; a schedule value fills a gap; a disagreement is REPORTED."""
    merged, filled, conflicts = {}, [], []
    canon_sched = {game_key_from_ticker_key(k) or k: v for k, v in (from_schedule or {}).items()}
    for k, v in (from_closes or {}).items():
        merged[k] = v
        s = canon_sched.get(game_key_from_ticker_key(k) or k)
        if s is not None and _same_instant(s, v) is False:
            conflicts.append({"game_key": k, "close": v, "schedule": s})
    return merged, {"filled_from_schedule": filled, "conflicts": conflicts, "_canon_sched": canon_sched}


def _same_instant(a: str, b: str):
    try:
        da = datetime.fromisoformat(a.replace("Z", "+00:00"))
        db = datetime.fromisoformat(b.replace("Z", "+00:00"))
    except ValueError:
        return None
    return abs((da - db).total_seconds()) < 1


def kickoffs_for_games(game_keys, from_closes: dict, from_schedule: dict) -> tuple:
    """Kickoff per requested Kalshi game key (the form a ticker carries), closes first, schedule as the fallback."""
    merged, rep = merge_kickoffs(from_closes, from_schedule)
    canon_sched = rep.pop("_canon_sched")
    for k in game_keys:
        if k in merged:
            continue
        s = canon_sched.get(game_key_from_ticker_key(k) or k)
        if s is not None:
            merged[k] = s
            rep["filled_from_schedule"].append(k)
    rep["filled_from_schedule"] = sorted(set(rep["filled_from_schedule"]))
    return merged, rep


def game_ids_from_schedule(text: str, season: int) -> dict:
    """{canonical game key -> nflverse game_id} for one season, so a ticker's event key can be tied back to the packet's game."""
    out: dict = {}
    for row in csv.DictReader(io.StringIO(text)):
        if str(row.get("season")) != str(season):
            continue
        day = (row.get("gameday") or "").strip()
        away, home = canon_team((row.get("away_team") or "").strip()), canon_team((row.get("home_team") or "").strip())
        try:
            d = datetime.strptime(day, "%Y-%m-%d").date()
        except ValueError:
            continue
        out[f"{d:%y}{_MONTHS[d.month - 1]}{d.day:02d}{away}{home}"] = row.get("game_id")
    return out
