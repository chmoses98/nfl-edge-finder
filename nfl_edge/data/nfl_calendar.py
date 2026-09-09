"""Canonical NFL calendar: which season/week is live right now, and when its games kick off.

Three collectors (`scripts/kalshi/capture.py`, `scripts/data/context_capture.py`,
`nfl_edge/data/silver.py`) already read the nflverse `games.csv` schedule. Each one re-derived the
US-Eastern -> UTC conversion inline. This module is the one place that answers the *calendar* question the
report pipeline needs -- **what is the active slate?** -- so that nothing downstream is left hard-coding
`--season 2026 --week 1`, which is exactly how a workflow keeps confidently building last month's slate.

Everything here is stdlib-only on purpose: the horizon gate that calls it wakes every few minutes and must
not need a dependency install to decide it has nothing to do.

Rules the resolver obeys, in order:

* before a week's first kickoff -> that upcoming week;
* while any game in that week is still running -> that week;
* once the whole week is complete -> the next week that has published kickoff times;
* postseason is returned as postseason. `season_type` is always explicit and a playoff round is never
  reported as `REG week N`, because nflverse numbers the Wild Card round week 19 and a caller that only
  reads `week` would happily hand `--week 19` to a regular-season packet builder;
* nothing upcoming, or kickoff times not published yet -> `status="NO_SLATE"` and a named reason. There is
  no guessed week. "I could not tell" must never resolve to a number.
"""
from __future__ import annotations

import csv
import io
import os
from datetime import datetime, timedelta, timezone

# A week block stays "active" until its last kickoff plus this much. An NFL game runs a little over three
# hours; four is the honest rounding, and being slightly generous keeps a Sunday-night game from rolling the
# slate over to next week while it is still being played.
GAME_RUNTIME_HOURS = 4.0

# nflverse `game_type` codes. REG is the regular season; everything else is postseason and is labelled as
# such rather than being flattened into a week number.
POSTSEASON_TYPES = {"WC": "Wild Card", "DIV": "Divisional", "CON": "Conference Championship",
                    "SB": "Super Bowl", "PRO": "Pro Bowl"}
PRESEASON_TYPES = {"PRE"}

SCHEDULE_URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"


# ======================================================================================================
# time
# ======================================================================================================

def eastern_offset_hours(naive_et: datetime) -> int:
    """Hours to ADD to a naive US-Eastern datetime to get UTC (4 during EDT, 5 during EST).

    DST runs from the second Sunday in March to the first Sunday in November.
    """
    year = naive_et.year
    mar1 = datetime(year, 3, 1)
    dst_start = mar1 + timedelta(days=(6 - mar1.weekday()) % 7 + 7)   # 2nd Sunday in March, 02:00 local
    nov1 = datetime(year, 11, 1)
    dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7)         # 1st Sunday in November
    return 4 if dst_start <= naive_et < dst_end else 5


def kickoff_utc(gameday: str, gametime: str):
    """`2026-09-09` + `20:20` (US-Eastern, as nflverse publishes it) -> an aware UTC datetime, or None."""
    if not gameday or not gametime:
        return None
    try:
        naive = datetime.strptime(f"{gameday} {gametime}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None
    return (naive + timedelta(hours=eastern_offset_hours(naive))).replace(tzinfo=timezone.utc)


# ======================================================================================================
# schedule loading
# ======================================================================================================

def schedule_candidates(root: str, market_data: str | None = None) -> list:
    """Where a canonical `games.csv` may already be on disk, most authoritative first."""
    out = [os.path.join(root, "data", "raw", "nflverse", "schedules", "games.csv")]
    if market_data:
        out.append(os.path.join(market_data, "data", "kalshi", "capture", "schedule_cache.csv"))
    return out


def parse_schedule(text: str) -> list:
    """nflverse games.csv text -> the fields the calendar needs, one dict per row with a known kickoff."""
    games = []
    for row in csv.DictReader(io.StringIO(text)):
        try:
            season = int(row["season"])
            week = int(row["week"])
        except (KeyError, TypeError, ValueError):
            continue
        ko = kickoff_utc(row.get("gameday", ""), row.get("gametime", ""))
        games.append({
            "game_id": row.get("game_id"),
            "season": season,
            "week": week,
            "game_type": (row.get("game_type") or "REG").strip().upper(),
            "gameday": row.get("gameday"),
            "away_team": row.get("away_team"),
            "home_team": row.get("home_team"),
            "kickoff_utc": ko,
            "has_result": bool((row.get("result") or "").strip()),
        })
    return games


def load_schedule(root: str, *, market_data: str | None = None, path: str | None = None,
                  allow_download: bool = False, timeout: int = 60):
    """Return `(games, source)`. Raises FileNotFoundError when no schedule can be read at all.

    Fail closed: a caller that cannot read the schedule must not fall back to a guessed week, so this
    raises rather than returning an empty list that would read as "the season is over".
    """
    tried = []
    for p in ([path] if path else schedule_candidates(root, market_data)):
        if p and os.path.exists(p):
            with open(p) as f:
                return parse_schedule(f.read()), p
        tried.append(p)
    if allow_download:
        import urllib.request
        req = urllib.request.Request(SCHEDULE_URL, headers={"User-Agent": "nfl-edge-finder calendar"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return parse_schedule(r.read().decode()), SCHEDULE_URL
    raise FileNotFoundError(
        "no NFL schedule available; looked at " + ", ".join(str(t) for t in tried) +
        " (pass --schedule, or allow a download)")


# ======================================================================================================
# week resolution
# ======================================================================================================

def season_type_of(game_type: str) -> str:
    gt = (game_type or "REG").upper()
    if gt in PRESEASON_TYPES:
        return "PRE"
    return "REG" if gt == "REG" else "POST"


def slate_id(season: int, season_type: str, week: int) -> str:
    """Stable identity for one week block, safe in a filename, an artifact name and a horizon key."""
    return f"{season}-{season_type}-{week:02d}"


def week_blocks(games: list) -> list:
    """Group scheduled games into week blocks, ordered by first known kickoff.

    A block is (season, season_type, week). Postseason rounds keep their own nflverse week numbers, so
    `2026-POST-19` and `2026-REG-19` can never collide even though the integer is the same.
    """
    blocks = {}
    for g in games:
        st = season_type_of(g["game_type"])
        key = (g["season"], st, g["week"])
        b = blocks.setdefault(key, {
            "season": g["season"], "season_type": st, "week": g["week"],
            "game_types": set(), "games": [], "kickoffs": [],
        })
        b["game_types"].add(g["game_type"])
        b["games"].append(g)
        if g["kickoff_utc"]:
            b["kickoffs"].append(g["kickoff_utc"])
    out = []
    for b in blocks.values():
        b["game_types"] = sorted(b["game_types"])
        b["first_kickoff"] = min(b["kickoffs"]) if b["kickoffs"] else None
        b["last_kickoff"] = max(b["kickoffs"]) if b["kickoffs"] else None
        b["games_scheduled"] = len(b["games"])
        b["games_with_kickoff"] = len(b["kickoffs"])
        rounds = sorted({POSTSEASON_TYPES[t] for t in b["game_types"] if t in POSTSEASON_TYPES})
        b["round"] = ", ".join(rounds) if rounds else None
        b["slate_id"] = slate_id(b["season"], b["season_type"], b["week"])
        b["label"] = _label(b)
        out.append(b)
    # Blocks with no published kickoff sort after everything dated, by (season, week), so they are still
    # reachable as "the next thing" and are reported as unscheduled rather than skipped over silently.
    out.sort(key=lambda b: (b["first_kickoff"] or datetime.max.replace(tzinfo=timezone.utc),
                            b["season"], b["week"]))
    return out


def _label(b: dict) -> str:
    if b["season_type"] == "POST":
        return f"{b['season']} postseason {b['round'] or 'round'} (nflverse week {b['week']})"
    if b["season_type"] == "PRE":
        return f"{b['season']} preseason week {b['week']}"
    return f"{b['season']} regular season week {b['week']}"


def block_complete(b: dict, now: datetime, runtime_hours: float = GAME_RUNTIME_HOURS) -> bool:
    """A block is complete once its last game has had time to finish."""
    if b["last_kickoff"] is None:
        return False
    return now >= b["last_kickoff"] + timedelta(hours=runtime_hours)


def resolve_active_week(games: list, now: datetime | None = None, *,
                        runtime_hours: float = GAME_RUNTIME_HOURS,
                        include_preseason: bool = False,
                        schedule_source: str | None = None) -> dict:
    """The season/week a report should be built for, or an explicit refusal.

    Returns a machine-readable dict; `status` is `OK` or `NO_SLATE` and `NO_SLATE` always carries a
    `reason`. There is no third outcome and no guessed week.
    """
    now = now or datetime.now(timezone.utc)
    blocks = [b for b in week_blocks(games)
              if include_preseason or b["season_type"] != "PRE"]
    base = {"status": "NO_SLATE", "reason": None, "resolved_at": now.isoformat(),
            "schedule_source": schedule_source, "season": None, "week": None,
            "season_type": None, "slate_id": None, "label": None}
    if not blocks:
        return dict(base, reason="the schedule contains no regular-season or postseason games")

    remaining = [b for b in blocks if not block_complete(b, now, runtime_hours)]
    if not remaining:
        last = blocks[-1]
        return dict(base, reason=(
            f"offseason: the last scheduled game block ({last['label']}) finished on "
            f"{last['last_kickoff'].date()}; no upcoming slate"))

    b = remaining[0]
    if b["first_kickoff"] is None:
        return dict(base, reason=(
            f"{b['label']} is the next block but no kickoff times are published for it yet; refusing to "
            "guess a week"), season=b["season"], week=b["week"], season_type=b["season_type"],
            slate_id=b["slate_id"], label=b["label"])

    kicked = [k for k in b["kickoffs"] if k <= now]
    upcoming = sorted(k for k in b["kickoffs"] if k > now)
    return {
        "status": "OK",
        "reason": None,
        "resolved_at": now.isoformat(),
        "schedule_source": schedule_source,
        "season": b["season"],
        "week": b["week"],
        "season_type": b["season_type"],
        "game_types": b["game_types"],
        "round": b["round"],
        "slate_id": b["slate_id"],
        "label": b["label"],
        "first_kickoff_utc": b["first_kickoff"].isoformat(),
        "last_kickoff_utc": b["last_kickoff"].isoformat() if b["last_kickoff"] else None,
        "next_kickoff_utc": upcoming[0].isoformat() if upcoming else None,
        "minutes_to_first_kickoff": round((b["first_kickoff"] - now).total_seconds() / 60.0, 1),
        "minutes_to_next_kickoff": (
            None if not upcoming else round((upcoming[0] - now).total_seconds() / 60.0, 1)),
        "games_scheduled": b["games_scheduled"],
        "games_with_kickoff": b["games_with_kickoff"],
        "games_started": len(kicked),
        "games_upcoming": len(upcoming),
        "slate_in_progress": bool(kicked and upcoming),
        "games": [{"game_id": g["game_id"], "away_team": g["away_team"], "home_team": g["home_team"],
                   "kickoff_utc": g["kickoff_utc"].isoformat() if g["kickoff_utc"] else None}
                  for g in sorted(b["games"], key=lambda g: (
                      g["kickoff_utc"] or datetime.max.replace(tzinfo=timezone.utc), g["game_id"] or ""))],
    }
