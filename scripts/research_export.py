#!/usr/bin/env python3
"""Export the Edge Finder research explorer (`app/latest/explorer/`) beside the v1 app payload.

    python3 scripts/research_export.py --reports-dir data/handicap_report --market-data-root /tmp/md \
        --out <staging>/app/latest [--now <aware ISO>]

Run it AFTER `scripts/app_export.py` has published `app/latest` from the same report: the explorer takes its
`run_id`, its `generated_at`, its events, markets, model prices, wagers and settlements from that publication,
so every `evt_` / `prt_` / `mkt_` id here is the one the v1 payload carries (teams: nflverse 3-letter codes;
players: GSIS ids; games: nflverse game ids -- the same `build.participant` / `ids.event_id` calls).

A PURE ADAPTER over data the repository already commits or captures (docs/APP_EXPORT.md, "Research explorer"):

    report   latest/packet.json games[] -- team_profiles (raw splits + opponent-adjusted ridge ratings),
             matchup.pairs, quarterbacks, offensive_line, roles (Sleeper depth chart), injuries.records,
             weather, venue, game_script_inputs, simulation.player_projections (quantiles; RESEARCH)
    market-data  data/kalshi/capture/schedule_cache.csv (nflverse schedule, scores 1999-2026),
             data/kalshi/capture/<day>/<run>.quotes.jsonl (change-suppressed Kalshi quotes, current week only),
             data/shadow/scorecards/<run>/cumulative.scorecard.json (incumbent calibration / accuracy / CLV),
             data/handicap/actual_wagers/<season>/season.actual_wagers.json (owner-wager CLV)

Nothing is fitted here. Per-game averages, rankings over stored values, rolling means and the compression of
change-suppressed quotes are arithmetic; every model number is read from where the repository stored it.
Stdlib only, no network, no write outside the app root. On failure the previous explorer tree is untouched
(`research.publish_explorer` stages and swaps) and the script exits 1.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "contract")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_finder_contract import build, ids, research as R, timeutil  # noqa: E402
from scripts import app_export as v1  # noqa: E402  (identity constants and helpers of the v1 export)

SPORT = v1.SPORT
TEAM_SOURCE = v1.TEAM_SOURCE
PLAYER_SOURCE_GSIS = v1.PLAYER_SOURCE_GSIS
EVENT_SOURCE = v1.EVENT_SOURCE
METHODOLOGY_VERSION = "nfl-explorer-1.0.0"
AUDIT_DATE = "2026-10-03"

PACKET_NAME = "packet.json"
CAPTURE_DIR = ("data", "kalshi", "capture")
SCHEDULE_PATH = ("data", "kalshi", "capture", "schedule_cache.csv")
SCORECARD_DIR = ("data", "shadow", "scorecards")
POSTMORTEM_DIR = ("data", "handicap", "actual_wagers")

HISTORY_SEASONS = 4             # game lists: the current season and the three before it
SERIES_CAP = 40                 # per-game series: the last 40 completed games per team
ROLLING_N = 4                   # trailing mean on the per-game series
QUOTE_LOOKBACK_DAYS = 10        # captures read: from ten days before the earliest board kickoff
QUOTE_HEARTBEAT_S = 6 * 3600    # an unchanged price still gets a point every six hours (volume / OI drift)
QUOTE_MAX_POINTS = 240          # per ticker, after hourly thinning
MARKET_HISTORY_BUDGET = 380_000  # bytes per market_history document (contract budget 400 KB)
EVENT_BUDGET = 145_000          # bytes per event research document (contract budget 150 KB)
PROFILE_BUDGET = 145_000        # bytes per profile (contract budget 150 KB)
HISTORY_FAMILIES = ("game_winner", "spread", "total", "team_total")
EVENT_MARKET_FAMILIES = ("game_winner", "spread", "total", "team_total", "period_winner", "both_teams_score_n",
                         "team_stat", "race_to_n", "win_margin_bucket", "half_full_result", "first_td_team")

LIM_SNAPSHOT = "current snapshot only; no committed history"

# ------------------------------------------------------------------------------------------------ metric tables
# (packet key, name, short name, category, unit, stat_type, higher_is_better, description)
RAW_TEAM_METRICS = [
    ("off_epa_play", "Offensive EPA per play", "Off EPA/play", "offense", "EPA/play", "RATE", True,
     "Mean expected points added per offensive play"),
    ("off_success_rate", "Offensive success rate", "Off SR", "offense", "share", "RATE", True,
     "Share of offensive plays with positive EPA"),
    ("off_dropback_epa", "Offensive EPA per dropback", "Off EPA/db", "offense", "EPA/dropback", "RATE", True,
     "Mean EPA per offensive dropback (passes, sacks, scrambles)"),
    ("off_rush_epa", "Offensive EPA per rush", "Off EPA/rush", "offense", "EPA/rush", "RATE", True,
     "Mean EPA per designed rush"),
    ("off_early_down_epa", "Offensive early-down EPA per play", "Off ED EPA", "offense", "EPA/play", "RATE", True,
     "Mean EPA per first- and second-down offensive play"),
    ("off_epa_play_ng", "Offensive EPA per play, neutral script", "Off EPA/play NS", "offense", "EPA/play", "RATE", True,
     "Mean EPA per offensive play in neutral game script (the silver *_ng columns)"),
    ("off_proe_early_ng", "Early-down pass rate over expected, neutral script", "PROE ED NS", "style", "pct points",
     "RATE", None, "Early-down pass rate over expected in neutral script; a tendency, not a quality"),
    ("off_rz_epa", "Red-zone offensive EPA per play", "RZ EPA", "offense", "EPA/play", "RATE", True,
     "Mean EPA per offensive red-zone play"),
    ("off_cpoe", "Completion percentage over expected", "CPOE", "offense", "pct points", "RATE", True,
     "Completion percentage over expected (nflverse cpoe)"),
    ("off_adot", "Average depth of target", "aDOT", "style", "yards", "RATE", None,
     "Mean air yards per target; a tendency, not a quality"),
    ("off_no_huddle_rate", "No-huddle rate", "No-huddle", "style", "share", "RATE", None,
     "Share of offensive plays run without a huddle"),
    ("off_shotgun_rate", "Shotgun rate", "Shotgun", "style", "share", "RATE", None,
     "Share of offensive plays from shotgun"),
    ("def_epa_play", "Defensive EPA per play allowed", "Def EPA/play", "defense", "EPA/play", "RATE", False,
     "Mean EPA allowed per defensive play (lower is better)"),
    ("def_success_rate", "Defensive success rate allowed", "Def SR", "defense", "share", "RATE", False,
     "Share of opponent plays with positive EPA (lower is better)"),
    ("def_dropback_epa", "Defensive EPA per dropback allowed", "Def EPA/db", "defense", "EPA/dropback", "RATE", False,
     "Mean EPA allowed per opponent dropback (lower is better)"),
    ("def_rush_epa", "Defensive EPA per rush allowed", "Def EPA/rush", "defense", "EPA/rush", "RATE", False,
     "Mean EPA allowed per opponent rush (lower is better)"),
    ("def_early_down_epa", "Defensive early-down EPA allowed", "Def ED EPA", "defense", "EPA/play", "RATE", False,
     "Mean EPA allowed per opponent first- and second-down play (lower is better)"),
    ("def_epa_play_ng", "Defensive EPA per play allowed, neutral script", "Def EPA/play NS", "defense", "EPA/play",
     "RATE", False, "Mean EPA allowed per play in neutral game script (lower is better)"),
    ("def_rz_epa", "Red-zone defensive EPA allowed", "Def RZ EPA", "defense", "EPA/play", "RATE", False,
     "Mean EPA allowed per opponent red-zone play (lower is better)"),
    ("off_explosive_rate", "Explosive play rate", "Off explosive", "offense", "share", "RATE", True,
     "(explosive passes + explosive runs) / offensive plays"),
    ("def_explosive_rate", "Explosive play rate allowed", "Def explosive", "defense", "share", "RATE", False,
     "Opponent explosive plays / defensive plays (lower is better)"),
    ("off_sack_rate_allowed", "Sack rate allowed", "Sack% allowed", "offense", "share", "RATE", False,
     "Sacks taken / offensive dropbacks (lower is better)"),
    ("def_sack_rate", "Defensive sack rate", "Def sack%", "defense", "share", "RATE", True,
     "Sacks / opponent dropbacks"),
    ("def_qb_hit_rate", "Defensive QB hit rate", "QB hit%", "defense", "share", "RATE", True,
     "QB hits / opponent dropbacks"),
    ("off_turnover_rate", "Offensive turnover rate", "Off TO%", "offense", "share", "RATE", False,
     "Turnovers / offensive plays (lower is better)"),
    ("def_takeaway_rate", "Defensive takeaway rate", "Takeaway%", "defense", "share", "RATE", True,
     "Takeaways / defensive plays"),
    ("off_td_drive_rate", "Touchdown drive rate", "TD drive%", "offense", "share", "RATE", True,
     "Touchdown drives / drives"),
    ("off_plays_per_drive", "Plays per drive", "Plays/drive", "style", "plays", "RATE", None,
     "Offensive plays / drives; pace and sustain, not a quality on its own"),
]
RAW_SPLITS = (("season_split", "SEASON"), ("recent_split", "L6"), ("long_baseline", "L34"))

# (packet adjusted key, name, short, higher_is_better, raw counterpart)
ADJ_TEAM_METRICS = [
    ("off_epa", "Adjusted offensive EPA per play", "Adj Off EPA", True),
    ("def_epa", "Adjusted defensive EPA per play allowed", "Adj Def EPA", False),
    ("off_sr", "Adjusted offensive success rate", "Adj Off SR", True),
    ("def_sr", "Adjusted defensive success rate allowed", "Adj Def SR", False),
    ("off_db_epa", "Adjusted offensive EPA per dropback", "Adj Off EPA/db", True),
    ("def_db_epa", "Adjusted defensive EPA per dropback allowed", "Adj Def EPA/db", False),
    ("off_rush_epa", "Adjusted offensive EPA per rush", "Adj Off EPA/rush", True),
    ("def_rush_epa", "Adjusted defensive EPA per rush allowed", "Adj Def EPA/rush", False),
    ("off_epa_ng", "Adjusted offensive EPA per play, neutral script", "Adj Off EPA NS", True),
    ("def_epa_ng", "Adjusted defensive EPA allowed, neutral script", "Adj Def EPA NS", False),
    ("off_explosive", "Adjusted explosive play rate", "Adj Off expl", True),
    ("def_explosive", "Adjusted explosive play rate allowed", "Adj Def expl", False),
    ("off_sack_rate", "Adjusted sack rate allowed", "Adj sack% allowed", False),
    ("def_sack_rate", "Adjusted defensive sack rate", "Adj Def sack%", True),
    ("off_to_rate", "Adjusted offensive turnover rate", "Adj Off TO%", False),
    ("def_to_rate", "Adjusted defensive takeaway rate", "Adj Def TO%", True),
    ("off_proe", "Adjusted early-down pass rate over expected", "Adj PROE", None),
    ("def_proe", "Adjusted opponent pass rate over expected allowed", "Adj Def PROE", None),
    ("off_st_epa", "Adjusted special-teams EPA", "Adj ST EPA", True),
    ("def_st_epa", "Adjusted special-teams EPA allowed", "Adj ST EPA allowed", False),
    ("off_ed_epa", "Adjusted offensive early-down EPA", "Adj Off ED EPA", True),
    ("def_ed_epa", "Adjusted defensive early-down EPA allowed", "Adj Def ED EPA", False),
]
ADJ_METHOD = ("weighted ridge in nfl_edge.research.team_ratings.solve_ratings: y = league mean + off_team + def_opponent "
              "+ hfa, recency half-life 10 weeks, prior-season carry 0.6, ridge 4.0, a 3-season window and only games "
              "strictly before the packet week; a deviation from the league mean of the windowed sample")

# (slug, name, short, higher_is_better, description)
SCHEDULE_METRICS = [
    ("points_for", "Points scored per game", "PF/G", True, "Points the team scored, from the nflverse schedule"),
    ("points_against", "Points allowed per game", "PA/G", False, "Points the opponent scored, from the nflverse schedule"),
    ("point_margin", "Point margin per game", "Margin/G", True, "Points scored minus points allowed"),
]

QB_METRICS = [
    ("epa_per_dropback", "QB EPA per dropback", "QB EPA/db", True),
    ("success_rate", "QB success rate", "QB SR", True),
    ("cpoe", "QB completion percentage over expected", "QB CPOE", True),
    ("adot", "QB average depth of target", "QB aDOT", None),
    ("sack_rate", "QB sack rate", "QB sack%", False),
    ("int_rate", "QB interception rate", "QB INT%", False),
    ("pressure_rate_proxy", "QB pressure rate (QB-hit proxy)", "QB pressure%", False),
    ("deep_rate", "QB deep-attempt rate", "QB deep%", None),
]
QB_SPLITS = ("under_pressure", "clean_pocket")

STAT_LABELS = {"touchdowns": "anytime touchdowns", "receiving_yards": "receiving yards", "receptions": "receptions",
               "rushing_yards": "rushing yards", "carries": "carries", "passing_tds": "passing touchdowns",
               "passing_yards": "passing yards", "attempts": "pass attempts", "completions": "completions"}
STAT_UNITS = {"touchdowns": "touchdowns", "receiving_yards": "yards", "receptions": "receptions",
              "rushing_yards": "yards", "carries": "carries", "passing_tds": "touchdowns", "passing_yards": "yards",
              "attempts": "attempts", "completions": "completions"}

_NAME_SUFFIX = re.compile(r"\b(jr|sr|ii|iii|iv|v)\b")
_DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ResearchExportError(RuntimeError):
    pass


# ------------------------------------------------------------------------------------------------ small helpers

def _load(path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _num(value):
    try:
        return None if value in (None, "") else float(value)
    except (TypeError, ValueError):
        return None


def _iso(value):
    return timeutil.to_iso_or_none(value)


def _max_ts(*values):
    real = [timeutil.parse_ts(v) for v in values if v]
    return timeutil.to_iso(max(real)) if real else None


def name_key(name) -> str:
    """Lowercase letters only, suffixes dropped: the same normalisation idea as nfl_edge.data.ids._norm_name."""
    s = re.sub(r"[^a-z ]", "", str(name or "").lower().replace(".", " ").replace("'", ""))
    return " ".join(_NAME_SUFFIX.sub(" ", s).split())


def met(slug: str) -> str:
    return ids.metric_id(SPORT, slug)


def team_pid(code: str) -> str:
    return ids.participant_id(SPORT, "TEAM", TEAM_SOURCE, code)


def player_pid(gsis: str) -> str:
    return ids.participant_id(SPORT, "PLAYER", PLAYER_SOURCE_GSIS, gsis)


def game_eid(game_id: str) -> str:
    return ids.event_id(SPORT, EVENT_SOURCE, game_id)


def team_participant(code: str, names: dict) -> dict:
    """Exactly `scripts/app_export.Exporter.team_participant`: the same call, the same `prt_` id."""
    city, nick = names.get(code, (None, None))
    display = f"{city} {nick}" if city and nick else code
    return build.participant(sport=SPORT, participant_type="TEAM", source=TEAM_SOURCE, source_id=code,
                             display_name=display, short_name=code)


def _size(doc) -> int:
    return len(json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


# ------------------------------------------------------------------------------------------------ input loading

def read_schedule_rows(market_data_root) -> list[dict]:
    """Every schedule_cache.csv row with an aware UTC kickoff (ET -> UTC exactly as the v1 export does)."""
    if not market_data_root:
        return []
    path = os.path.join(market_data_root, *SCHEDULE_PATH)
    if not os.path.exists(path):
        return []
    from zoneinfo import ZoneInfo
    eastern = ZoneInfo("America/New_York")
    out = []
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if not row.get("game_id") or not row.get("gameday") or not row.get("gametime"):
                continue
            try:
                local = datetime.strptime(f"{row['gameday']} {row['gametime']}", "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            kickoff = local.replace(tzinfo=eastern).astimezone(timezone.utc)
            hs, as_ = _num(row.get("home_score")), _num(row.get("away_score"))
            out.append({"game_id": row["game_id"], "season": int(row["season"]), "week": int(row["week"]),
                        "game_type": row.get("game_type") or "REG", "kickoff": kickoff,
                        "home": row["home_team"], "away": row["away_team"],
                        "home_score": hs, "away_score": as_, "final": hs is not None and as_ is not None,
                        "location": row.get("location"), "roof": row.get("roof"), "surface": row.get("surface"),
                        "stadium": row.get("stadium")})
    out.sort(key=lambda r: (r["kickoff"], r["game_id"]))
    return out


def capture_quote_files(market_data_root, start_day: str, end_day: str) -> list[str]:
    """`data/kalshi/capture/<day>/<run>.quotes.jsonl` for start_day <= day <= end_day, in time order."""
    if not market_data_root:
        return []
    base = os.path.join(market_data_root, *CAPTURE_DIR)
    if not os.path.isdir(base):
        return []
    out = []
    for day in sorted(d for d in os.listdir(base) if _DAY_RE.match(d) and start_day <= d <= end_day):
        ddir = os.path.join(base, day)
        out.extend(os.path.join(ddir, f) for f in sorted(os.listdir(ddir)) if f.endswith(".quotes.jsonl"))
    return out


def _file_lines(path):
    with open(path, encoding="utf-8") as fh:
        yield from fh


def collect_quote_history(paths, wanted: set, *, read_lines=_file_lines) -> dict:
    """ticker -> compressed pregame price points, from change-suppressed capture quotes.

    A capture run writes a row only when a ticker's fingerprint changed, so the quote holds (forward-fills)
    until the next row. Kept: the first row, every row whose bid / ask / last moved, a heartbeat row every six
    hours of unchanged price (volume and open interest keep moving), and the final row. A row repeating the
    previous fingerprint is a no-op. Then hourly thinning (the last state of each UTC hour) above
    QUOTE_MAX_POINTS. Points carry `source = capture:<run_id>`."""
    state: dict[str, dict] = {}
    for path in paths:
        for line in read_lines(path):
            i = line.find('"ticker":"')
            if i < 0:
                continue
            j = line.find('"', i + 10)
            ticker = line[i + 10:j]
            if ticker not in wanted:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("pregame") is False:
                continue
            st = state.setdefault(ticker, {"fp": None, "kept": [], "pending": None})
            fp = row.get("fingerprint")
            if fp is not None and fp == st["fp"]:
                continue
            st["fp"] = fp
            t = timeutil.parse_ts(row["observed_at"])
            pt = {"t": t, "bid": _num(row.get("yes_bid_dollars")), "ask": _num(row.get("yes_ask_dollars")),
                  "last": _num(row.get("last_price_dollars")), "vol": _num(row.get("volume_fp")),
                  "oi": _num(row.get("open_interest_fp")), "run": row.get("run_id")}
            kept = st["kept"]
            if (not kept or (pt["bid"], pt["ask"], pt["last"]) != (kept[-1]["bid"], kept[-1]["ask"], kept[-1]["last"])
                    or (t - kept[-1]["t"]).total_seconds() >= QUOTE_HEARTBEAT_S):
                kept.append(pt)
                st["pending"] = None
            else:
                st["pending"] = pt
    out = {}
    for ticker, st in state.items():
        pts = list(st["kept"])
        if st["pending"] is not None and st["pending"]["t"] > pts[-1]["t"]:
            pts.append(st["pending"])
        pts.sort(key=lambda p: p["t"])
        if len(pts) > QUOTE_MAX_POINTS:
            by_hour = {}
            for p in pts:
                by_hour[p["t"].strftime("%Y%m%d%H")] = p
            pts = sorted(by_hour.values(), key=lambda p: p["t"])[-QUOTE_MAX_POINTS:]
        out[ticker] = [R.price_point(captured_at=p["t"], yes_bid=p["bid"], yes_ask=p["ask"], last_price=p["last"],
                                     volume=p["vol"], open_interest=p["oi"], source=f"capture:{p['run']}")
                       for p in pts]
    return out


def read_scorecard(market_data_root):
    """The newest incumbent cumulative scorecard (data/shadow/scorecards/<run>/cumulative.scorecard.json)."""
    if not market_data_root:
        return None
    base = os.path.join(market_data_root, *SCORECARD_DIR)
    if not os.path.isdir(base):
        return None
    for run in sorted(os.listdir(base), reverse=True):
        p = os.path.join(base, run, "cumulative.scorecard.json")
        if os.path.exists(p):
            doc = _load(p)
            return {"run": run, "path": "/".join(SCORECARD_DIR + (run, "cumulative.scorecard.json")), "doc": doc}
    return None


def read_wager_clv(market_data_root) -> dict:
    """source_bet_key -> {clv_state, clv_dollars} from the actual-wager postmortem (what the v1 export reads)."""
    out = {}
    if not market_data_root:
        return out
    base = os.path.join(market_data_root, *POSTMORTEM_DIR)
    if not os.path.isdir(base):
        return out
    for season in sorted(os.listdir(base)):
        p = os.path.join(base, season, "season.actual_wagers.json")
        if not os.path.exists(p):
            continue
        for w in _load(p).get("wagers") or []:
            if w.get("source_bet_key"):
                out[w["source_bet_key"]] = {"clv_state": w.get("clv_state"), "clv_dollars": _num(w.get("clv_dollars"))}
    return out


def read_v1(app_root) -> dict:
    """The v1 publication this explorer describes. Refuses a root whose last export failed."""
    root = Path(app_root)
    man_path = root / "manifest.json"
    if not man_path.exists():
        raise ResearchExportError(f"{root} has no manifest.json: run scripts/app_export.py first")
    manifest = _load(man_path)
    health_path = root / "health.json"
    if health_path.exists():
        health = _load(health_path)
        if health.get("export_failed") or health.get("payload_run_id") not in (None, manifest["run_id"]):
            raise ResearchExportError("the v1 export of this run failed (health.json export_failed); "
                                      "the explorer is not published over a stale payload")
    out = {"manifest": manifest}
    for kind in ("events", "markets", "model_prices", "recommendations", "wagers", "settlements"):
        p = root / f"{kind}.json"
        out[kind] = _load(p)["items"] if p.exists() else []
    return out


def load_inputs(*, reports_dir, app_root, market_data_root, read_lines=_file_lines) -> dict:
    packet_path = os.path.join(reports_dir, PACKET_NAME)
    if not os.path.exists(packet_path):
        raise ResearchExportError(f"{reports_dir} has no {PACKET_NAME}")
    packet = _load(packet_path)
    report_manifest = _load(os.path.join(reports_dir, "manifest.json"))
    v1docs = read_v1(app_root)
    schedule = read_schedule_rows(market_data_root)
    wanted, start_day, end_day = history_request(packet, v1docs)
    paths = capture_quote_files(market_data_root, start_day, end_day) if wanted else []
    quotes = collect_quote_history(paths, wanted, read_lines=read_lines)
    return {"packet": packet, "report_manifest": report_manifest, "v1": v1docs, "schedule": schedule,
            "quotes": quotes, "quote_files": len(paths), "scorecard": read_scorecard(market_data_root),
            "wager_clv": read_wager_clv(market_data_root), "team_names": v1.team_names()}


def history_request(packet: dict, v1docs: dict) -> tuple[set, str, str]:
    """The tickers whose capture history is read (game-level FULL markets of the packet's games, as the v1
    export published them) and the capture-day window: ten days before the earliest kickoff to the latest."""
    board = {game_eid(g["game_id"]) for g in packet.get("games") or []}
    wanted = {m["kalshi_ticker"] for m in v1docs["markets"]
              if m.get("event_id") in board and m["market_family"] in HISTORY_FAMILIES and m.get("period") == "FULL"
              and m["source"] == v1.REPORT_SOURCE}
    kicks = [timeutil.parse_ts(g["kickoff_utc"]) for g in packet.get("games") or [] if g.get("kickoff_utc")]
    if not kicks:
        return set(), "", ""
    start = (min(kicks) - timedelta(days=QUOTE_LOOKBACK_DAYS)).date().isoformat()
    end = (max(kicks) + timedelta(days=1)).date().isoformat()
    return wanted, start, end


def player_opportunity(game: dict) -> tuple[dict, str | None]:
    """One packet game's `game_script_inputs.player_opportunity` as {team: [player rows]}, and the packet's reason
    when it says the block is UNAVAILABLE (else None).

    `nfl_edge.handicap.script_block.game_script_inputs` writes one of two shapes: {team: [rows]} when the simulation
    published a game script for the game, or {"state": "UNAVAILABLE", "reason": <script source>} when it did not
    (e.g. 2026_04_PIT_CLE in the 2026-10-05 week-4 packet). An absent block reads as empty, as it always has. Any
    other shape is refused rather than read as "no players"."""
    gid = game.get("game_id")
    po = (game.get("game_script_inputs") or {}).get("player_opportunity")
    if po is None:
        return {}, None
    if isinstance(po, dict) and "state" in po:
        reason = po.get("reason")
        if po["state"] == "UNAVAILABLE" and set(po) <= {"state", "reason"} and isinstance(reason, (str, type(None))):
            return {}, reason or "no reason given"
    elif isinstance(po, dict) and all(isinstance(rows, list) and all(isinstance(x, dict) for x in rows)
                                      for rows in po.values()):
        return po, None
    shape = sorted(po)[:6] if isinstance(po, dict) else type(po).__name__
    raise ResearchExportError(f"{gid}: game_script_inputs.player_opportunity has an unrecognised shape {shape!r}: "
                              "expected {team: [player rows]} or {'state': 'UNAVAILABLE', 'reason': ...}")


def opportunity_note(unavailable: dict, n_games: int) -> str:
    """Says which games the packet published without player opportunity, and the packet's reason."""
    reasons = ", ".join(sorted(set(unavailable.values())))
    return (f"packet game_script_inputs.player_opportunity UNAVAILABLE for {len(unavailable)} of {n_games} games "
            f"({', '.join(sorted(unavailable))}; reason: {reasons}): no projected usage shares for their players")


# ------------------------------------------------------------------------------------------------ the builder

class _Builder:
    def __init__(self, inp: dict, now):
        self.inp = inp
        self.packet = inp["packet"]
        self.v1 = inp["v1"]
        self.run_id = self.v1["manifest"]["run_id"]
        self.now = timeutil.to_iso(now)
        self.names = inp.get("team_names") or {}
        self.built_at = timeutil.to_iso(self.packet.get("built_at") or inp["report_manifest"]["built_at"])
        self.season = str(self.packet.get("season"))
        self.games = {g["game_id"]: g for g in self.packet.get("games") or []}
        self.events = {e["event_id"]: e for e in self.v1["events"]}
        self.board_eids = {game_eid(gid): gid for gid in self.games if game_eid(gid) in self.events}
        self.markets = self.v1["markets"]
        self.markets_by_event: dict[str, list] = {}
        for m in self.markets:
            self.markets_by_event.setdefault(m.get("event_id"), []).append(m)
        self.prices_by_market = {}
        for mp in sorted(self.v1["model_prices"], key=lambda r: (r["market_id"], r["generated_at"])):
            self.prices_by_market[mp["market_id"]] = mp
        self.rec_authority = {r["market_id"]: (bool(r["research_only"]), r["authority"]) for r in self.v1["recommendations"]}
        self.docs: list[dict] = []
        self.metrics: dict[str, dict] = {}
        self.metric_windows: dict[str, set] = {}
        self.metric_ranked: set = set()
        self.metric_series: set = set()
        self.metric_splits: dict[str, set] = {}
        self.rankings: dict[tuple, dict] = {}
        self.team_obs: dict[str, list] = {}
        self.team_series: dict[str, list] = {}
        self.player_rows: dict[str, dict] = {}
        self.opportunity_unavailable: dict[str, str] = {}
        self.warnings: list[str] = []
        self.sched_as_of = None
        self.sim_generated_at = None
        self.published_events: set = set(self.events)
        self.market_history_eids: set = set()
        self.cap_evidence: dict[str, list] = {}

    # ---- quality objects ----------------------------------------------------------------------------
    def q(self, status, source, *, limitations=(), production=True, data_as_of=None, coverage=None, sample_size=None,
          source_version=None, methodology_version=METHODOLOGY_VERSION, missingness=None):
        return R.quality(status=status, source=source, generated_at=self.now, production=production,
                         data_as_of=data_as_of, coverage=coverage, sample_size=sample_size,
                         source_version=source_version, methodology_version=methodology_version,
                         limitations=list(limitations), missingness=missingness)

    def q_team_raw(self):
        return self.q("PARTIAL", "handicap-reports latest/packet.json games[].team_profiles (nfl_edge.handicap.teamprofile "
                      "over the silver team_game table built from nflverse play-by-play)",
                      limitations=[LIM_SNAPSHOT, "raw splits are null below 4 games (MIN_GAMES); the recent split is "
                                   "fixed at the last 6 games and the long baseline at the last 34",
                                   "the silver team_game table is rebuilt every run from nflverse and is not committed"],
                      data_as_of=self.built_at, source_version=self.packet.get("schema_version"))

    def q_team_adj(self):
        return self.q("PARTIAL", "handicap-reports latest/packet.json games[].team_profiles[].adjusted "
                      "(nfl_edge.research.team_ratings)",
                      limitations=[LIM_SNAPSHOT, "the ridge ratings have a point-in-time test but no accuracy or "
                                   "stability test", "home-field advantage is one league-wide scalar; no standard "
                                   "error is reported; early-season ratings are dominated by prior seasons"],
                      data_as_of=self.built_at, source_version=self.packet.get("schema_version"))

    def q_schedule(self):
        return self.q("VERIFIED", "market-data data/kalshi/capture/schedule_cache.csv (nflverse schedule)",
                      limitations=[f"per-game series capped at the last {SERIES_CAP} completed games per team; game lists "
                                   f"cover the last {HISTORY_SEASONS} seasons; the source covers 1999-2026"],
                      data_as_of=self.sched_as_of)

    def q_research(self, source, limitations):
        return self.q("RESEARCH", source, limitations=limitations, production=True, data_as_of=self.built_at)

    # ---- metric registry ------------------------------------------------------------------------------
    def register(self, slug, **kw):
        mid = met(slug)
        if mid not in self.metrics:
            self.metrics[mid] = {"slug": slug, **kw}
        return mid

    def note_window(self, mid, label):
        self.metric_windows.setdefault(mid, set()).add(label)

    # ---- rankings --------------------------------------------------------------------------------------
    def make_ranking(self, mid, window, values, hib, quality, universe_label, universe_filter, season):
        rows = [v for v in values if v.get("value") is not None]
        if len(rows) < 2:
            return None
        rk = R.ranking(sport=SPORT, metric_id=mid, universe_label=universe_label, entity_type="TEAM", window=window,
                       as_of=quality["data_as_of"] or self.built_at, higher_is_better=hib, values=rows,
                       run_id=self.run_id, generated_at=self.now, quality=quality, season=season,
                       universe_filter=universe_filter, path_for=R.team_path,
                       links=[R.link(rel="METRIC", target_kind="metric_registry", label="metric registry",
                                     target_id=mid, path=R.app_path(R.METRICS_NAME))])
        self.rankings[(mid, window["label"])] = rk
        self.metric_ranked.add(mid)
        self.docs.append(rk)
        return rk

    # ---- team metrics from the packet ------------------------------------------------------------------
    def team_profiles_from_packet(self) -> dict:
        out = {}
        for gid in sorted(self.games):
            for code, prof in (self.games[gid].get("team_profiles") or {}).items():
                if code != "_meta" and isinstance(prof, dict):
                    out[code] = {**prof, "_game_id": gid}
        return out

    def build_team_metrics(self, codes: list[str]):
        profiles = self.team_profiles_from_packet()
        universe = f"NFL teams, {self.season} (teams on the current packet's slate)"
        q_raw, q_adj = self.q_team_raw(), self.q_team_adj()
        for key, name, short, cat, unit, stype, hib, desc in RAW_TEAM_METRICS:
            mid = met(key)
            for split_key, label in RAW_SPLITS:
                window = R.window("SEASON") if label == "SEASON" else R.window("LAST_N", n=int(label[1:]))
                values = []
                for code in codes:
                    sp = (profiles.get(code) or {}).get(split_key) or {}
                    if sp.get(key) is None:
                        continue
                    values.append({"entity_id": team_pid(code), "display_name": self.team_name(code), "short_name": code,
                                   "value": sp[key], "sample_size": sp.get("n_games")})
                if not values:
                    continue
                self.register(key, kind="raw", name=name, short=short, category=cat, unit=unit, stype=stype, hib=hib,
                              desc=desc)
                self.note_window(mid, label)
                rk = self.make_ranking(mid, window, values, hib, q_raw, universe,
                                       "every team in the current packet with a non-null split (n_games >= 4)", self.season)
                for row in values:
                    pid = row["entity_id"]
                    basis = (profiles.get(row["short_name"]) or {})
                    self.team_obs.setdefault(pid, []).append(R.observation(
                        sport=SPORT, metric_id=mid, entity_id=pid, entity_type="TEAM", value=row["value"], window=window,
                        as_of=self.built_at, source="packet.team_profiles", quality_status="PARTIAL", unit=unit,
                        sample_size=row["sample_size"], season=str(basis.get("basis_season") or self.season),
                        context=R.context_from_ranking(rk, pid) if rk else None,
                        extensions={"basis": basis.get("basis"), "split": split_key}))
        w_adj = R.window("CUSTOM", label="ADJ_RIDGE")
        for key, name, short, hib in ADJ_TEAM_METRICS:
            slug = f"adj_{key}"
            mid = met(slug)
            values = []
            for code in codes:
                adj = (profiles.get(code) or {}).get("adjusted") or {}
                if adj.get(key) is None:
                    continue
                values.append({"entity_id": team_pid(code), "display_name": self.team_name(code), "short_name": code,
                               "value": adj[key]})
            if not values:
                continue
            self.register(slug, kind="adj", name=name, short=short, hib=hib, key=key)
            self.note_window(mid, w_adj["label"])
            rk = self.make_ranking(mid, w_adj, values, hib, q_adj, universe,
                                   "every team in the current packet with an adjusted rating", self.season)
            for row in values:
                pid = row["entity_id"]
                self.team_obs.setdefault(pid, []).append(R.observation(
                    sport=SPORT, metric_id=mid, entity_id=pid, entity_type="TEAM", value=row["value"], window=w_adj,
                    as_of=self.built_at, source="packet.team_profiles.adjusted", quality_status="PARTIAL",
                    unit="deviation from league mean", season=self.season,
                    context=R.context_from_ranking(rk, pid) if rk else None,
                    extensions={"basis": (profiles.get(row["short_name"]) or {}).get("basis")}))

    def team_name(self, code: str) -> str:
        city, nick = self.names.get(code, (None, None))
        return f"{city} {nick}" if city and nick else code

    # ---- schedule: results, opponents, per-game series, season averages --------------------------------
    def build_schedule(self, codes: list[str]):
        rows = self.inp.get("schedule") or []
        finals = [r for r in rows if r["final"]]
        self.sched_as_of = timeutil.to_iso(max(r["kickoff"] for r in finals)) if finals else None
        cur = int(self.season) if self.season.isdigit() else (max(r["season"] for r in rows) if rows else 0)
        first_season = cur - HISTORY_SEASONS + 1
        self.team_games: dict[str, list] = {c: [] for c in codes}
        for r in rows:
            if r["season"] < first_season:
                continue
            for code, opp, ha in ((r["home"], r["away"], "HOME"), (r["away"], r["home"], "AWAY")):
                if code not in self.team_games:
                    continue
                pf = r["home_score"] if ha == "HOME" else r["away_score"]
                pa = r["away_score"] if ha == "HOME" else r["home_score"]
                self.team_games[code].append({**r, "team": code, "opp": opp, "ha": ha, "pf": pf, "pa": pa})
        if not finals:
            return
        q = self.q_schedule()
        universe = f"NFL teams, {cur} season"
        w_season = R.window("SEASON")
        for slug, name, short, hib, desc in SCHEDULE_METRICS:
            mid = met(slug)
            values = []
            for code in codes:
                done = [g for g in self.team_games[code] if g["final"] and g["season"] == cur]
                if not done:
                    continue
                vals = [self._sched_value(slug, g) for g in done]
                values.append({"entity_id": team_pid(code), "display_name": self.team_name(code), "short_name": code,
                               "value": round(sum(vals) / len(vals), 4), "sample_size": len(vals)})
            self.register(slug, kind="schedule", name=name, short=short, hib=hib, desc=desc)
            rk = None
            if values:
                self.note_window(mid, "SEASON")
                rk = self.make_ranking(mid, w_season, values, hib, q, universe,
                                       f"every team with a completed {cur} game in the nflverse schedule", str(cur))
            for row in values:
                pid = row["entity_id"]
                self.team_obs.setdefault(pid, []).append(R.observation(
                    sport=SPORT, metric_id=mid, entity_id=pid, entity_type="TEAM", value=row["value"], window=w_season,
                    as_of=self.sched_as_of, source="schedule_cache.csv", quality_status="VERIFIED", unit="points",
                    sample_size=row["sample_size"], season=str(cur), context=R.context_from_ranking(rk, pid) if rk else None))
            # per-game series, capped
            for code in codes:
                done = [g for g in self.team_games[code] if g["final"]][-SERIES_CAP:]
                if not done:
                    continue
                pts = []
                for g in done:
                    eid = game_eid(g["game_id"])
                    pts.append(R.point(x=g["game_id"], t=g["kickoff"], value=self._sched_value(slug, g),
                                       quality_status="VERIFIED", event_id=eid, opponent_id=team_pid(g["opp"]),
                                       sample_size=1, source="schedule_cache.csv",
                                       path=R.event_path(eid) if eid in self.published_events else None))
                pid = team_pid(code)
                ser = R.time_series(sport=SPORT, metric_id=mid, entity_id=pid, entity_type="TEAM", x_axis="GAME",
                                    points=R.rolling(pts, ROLLING_N), as_of=self.sched_as_of, run_id=self.run_id,
                                    generated_at=self.now, quality=q, unit="points", rolling_window=ROLLING_N,
                                    links=[R.link(rel="TEAM", target_kind="entity_profile", label=self.team_name(code),
                                                  target_id=pid, path=R.team_path(pid))])
                self.metric_series.add(mid)
                self.team_series.setdefault(pid, []).append(ser)
                self.docs.append(ser)

    @staticmethod
    def _sched_value(slug, g):
        if slug == "points_for":
            return g["pf"]
        if slug == "points_against":
            return g["pa"]
        return g["pf"] - g["pa"]

    # ---- players --------------------------------------------------------------------------------------
    def collect_players(self):
        """GSIS id -> what the packet says about that player this week. Only players the simulation projected."""
        for gid in sorted(self.games):
            g = self.games[gid]
            sim = g.get("simulation") or {}
            if sim.get("generated_at"):
                self.sim_generated_at = _max_ts(self.sim_generated_at, sim["generated_at"])
            opp_by_id = {}
            by_team, unavailable = player_opportunity(g)
            if unavailable is not None:
                self.opportunity_unavailable[gid] = unavailable
            for team, lst in by_team.items():
                for x in lst:
                    opp_by_id[x.get("player")] = {**x, "team": team}
            qbs = {}
            for team, lst in (g.get("quarterbacks") or {}).items():
                for x in lst or []:
                    pid_ = ((x.get("profile") or {}).get("player_id"))
                    if pid_:
                        qbs[pid_] = x
            for r in sim.get("player_projections") or []:
                gsis = r.get("player_id")
                if not gsis:
                    continue
                p = self.player_rows.setdefault(gsis, {"gsis": gsis, "name": r.get("player_name") or gsis,
                                                        "team": r.get("team"), "game_id": gid, "rows": [],
                                                        "opportunity": None, "qb": None})
                p["rows"].append(r)
                if gsis in opp_by_id:
                    p["opportunity"] = opp_by_id[gsis]
                if gsis in qbs:
                    p["qb"] = qbs[gsis]
        for p in self.player_rows.values():
            pos = (p["opportunity"] or {}).get("position")
            if not pos:
                pos = self.position_from_roles(p)
            p["position"] = pos

    def position_from_roles(self, p) -> str | None:
        g = self.games.get(p["game_id"]) or {}
        roles = ((g.get("roles") or {}).get("by_team") or {}).get(p["team"]) or {}
        key = name_key(p["name"])
        for slot in sorted(roles):
            for x in roles[slot] or []:
                if name_key(x.get("player")) == key:
                    return x.get("position")
        if p["qb"]:
            return "QB"
        return None

    def player_participant(self, p) -> dict:
        meta = {"team": p["team"]}
        if p.get("position"):
            meta["position"] = p["position"]
        return build.participant(sport=SPORT, participant_type="PLAYER", source=PLAYER_SOURCE_GSIS, source_id=p["gsis"],
                                 display_name=p["name"], metadata=meta)

    def player_observations(self, p) -> tuple[list, dict]:
        pid = player_pid(p["gsis"])
        eid = game_eid(p["game_id"])
        gsis_team = team_pid(p["team"]) if p.get("team") else None
        game = self.games[p["game_id"]]
        home, away = game.get("home_team"), game.get("away_team")
        opp = (away if p["team"] == home else home) if p.get("team") in (home, away) else None
        w_game = R.window("GAME")
        as_of = self.sim_generated_at or self.built_at
        obs, splits = [], {}
        for r in sorted(p["rows"], key=lambda r: r.get("stat") or ""):
            stat = r.get("stat")
            if not stat or r.get("football_mean") is None:
                continue
            slug = f"sim_{stat}"
            mid = self.register(slug, kind="sim", stat=stat)
            self.note_window(mid, "GAME")
            obs.append(R.observation(
                sport=SPORT, metric_id=mid, entity_id=pid, entity_type="PLAYER", value=round(r["football_mean"], 4),
                window=w_game, as_of=as_of, source="packet.simulation.player_projections", quality_status="RESEARCH",
                unit=STAT_UNITS.get(stat), season=self.season, event_id=eid,
                opponent_id=team_pid(opp) if opp else None,
                extensions={k: (round(r[k], 4) if isinstance(r.get(k), float) else r.get(k))
                            for k in ("football_sd", "football_p05", "football_p25", "football_p50", "football_p75",
                                      "football_p95", "market_mean", "market_p50", "final_mean", "final_p50",
                                      "support_state", "p_active", "reconcile_weight", "n_rungs")}))
        opp_row = p.get("opportunity")
        if opp_row:
            for share, base in (("target_share", "targets"), ("carry_share", "carries")):
                if opp_row.get(share) is None:
                    continue
                slug = f"proj_{share}"
                mid = self.register(slug, kind="usage", share=share)
                self.note_window(mid, "GAME")
                obs.append(R.observation(
                    sport=SPORT, metric_id=mid, entity_id=pid, entity_type="PLAYER", value=opp_row[share], window=w_game,
                    as_of=as_of, source="packet.game_script_inputs.player_opportunity", quality_status="RESEARCH",
                    unit="share", season=self.season, event_id=eid, opponent_id=team_pid(opp) if opp else None,
                    extensions={base: opp_row.get(base), "p_active": opp_row.get("p_active"),
                                "opportunity_cv": opp_row.get("opportunity_cv"),
                                "role_uncertainty": opp_row.get("role_uncertainty")}))
        prof = (p.get("qb") or {}).get("profile") or {}
        if prof and not prof.get("insufficient_sample"):
            w_season = R.window("SEASON")
            w_recent = R.window("LAST_N", n=200, label="L200_DROPBACKS")
            for key, name, short, hib in QB_METRICS:
                slug = f"qb_{key}"
                for block, window, dim in (("overall", w_season, None), ("recent_200_dropbacks", w_recent, None),
                                           ("under_pressure", w_season, "pressure"), ("clean_pocket", w_season, "pressure")):
                    v = (prof.get(block) or {}).get(key)
                    if v is None:
                        continue
                    mid = self.register(slug, kind="qb", name=name, short=short, hib=hib, key=key)
                    self.note_window(mid, window["label"])
                    sp = R.split(dim, block) if dim else None
                    if dim:
                        self.metric_splits.setdefault(mid, set()).add(dim)
                    o = R.observation(sport=SPORT, metric_id=mid, entity_id=pid, entity_type="PLAYER", value=v,
                                      window=window, as_of=self.built_at, source="packet.quarterbacks.profile",
                                      quality_status="RESEARCH", split=sp,
                                      sample_size=prof.get("dropbacks") if block == "overall" else None,
                                      season=str(prof.get("basis_season") or self.season))
                    if dim:
                        splits.setdefault(dim, []).append(o)
                    else:
                        obs.append(o)
        _ = gsis_team
        return obs, splits

    def availability_for(self, team: str, name: str | None, game_id: str) -> list[dict]:
        """Injury + depth-chart status of one player (by name within team: ESPN/Sleeper rows carry no GSIS id)."""
        g = self.games.get(game_id) or {}
        eid = game_eid(game_id)
        out = []
        key = name_key(name)
        inj = g.get("injuries") or {}
        as_of = _capture_ts((inj.get("summary") or {}).get("capture_run_id")) or self.built_at
        for rec in inj.get("records") or []:
            if rec.get("team") == team and name_key(rec.get("player")) == key:
                out.append(_availability(rec, as_of, eid))
        roles = g.get("roles") or {}
        r_as_of = _capture_ts(roles.get("capture_run_id")) or self.built_at
        for slot in sorted((roles.get("by_team") or {}).get(team) or {}):
            for x in ((roles.get("by_team") or {}).get(team) or {}).get(slot) or []:
                if name_key(x.get("player")) == key:
                    detail = f"depth chart {slot} #{x.get('depth_chart_order')}" + (
                        f"; injury status {x['injury_status']}" if x.get("injury_status") else "")
                    out.append({"status": str(x.get("status") or "UNKNOWN").upper().replace(" ", "_"), "detail": detail,
                                "as_of": r_as_of, "source": "sleeper depth chart", "event_id": eid})
        return out

    # ---- markets / projections refs --------------------------------------------------------------------
    def projection_ref(self, mp):
        research_only, authority = self.rec_authority.get(mp["market_id"], (True, "RESEARCH_ONLY"))
        return R.projection_ref(mp, research_only=research_only, authority=authority, quality_status="PARTIAL",
                                metric_id=met("incumbent_fair_probability"))

    @staticmethod
    def _market_priority(m):
        mid = m.get("market_probability")
        return (0 if m.get("period") == "FULL" else 1, abs((mid if mid is not None else 0.0) - 0.5), m["kalshi_ticker"])

    def ordered_markets(self, markets, families=EVENT_MARKET_FAMILIES):
        """Round-robin over families, each family ordered FULL period first, then closest to the main line
        (mid nearest 0.5), so a budget keeps a spread of every family rather than all of the first one."""
        ranked = {}
        for m in sorted(markets, key=self._market_priority):
            ranked.setdefault(m["market_family"], []).append(m)
        fams = [f for f in families if f in ranked] + sorted(f for f in ranked if f not in families)
        order, depth = [], 0
        while any(depth < len(ranked[f]) for f in fams):
            order.extend(ranked[f][depth] for f in fams if depth < len(ranked[f]))
            depth += 1
        return order

    def fit_markets(self, doc_builder, markets, budget):
        """Add markets (and their model-price projections) in priority order while the document fits."""
        ordered = self.ordered_markets(markets)
        lo, hi = 0, len(ordered)
        # binary search on how many fit: size is monotone in the count
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if _size(doc_builder(ordered[:mid])) <= budget:
                lo = mid
            else:
                hi = mid - 1
        return ordered[:lo]

    def refs_for(self, markets):
        mrefs = [R.market_ref(m) for m in markets]
        prefs = [self.projection_ref(self.prices_by_market[m["market_id"]]) for m in markets
                 if m["market_id"] in self.prices_by_market]
        return mrefs, prefs

    # ---- market history ---------------------------------------------------------------------------------
    def build_market_history(self):
        quotes = self.inp.get("quotes") or {}
        q = self.q("VERIFIED", "market-data data/kalshi/capture/<day>/<run_id>.quotes.jsonl (Kalshi quotes, written only "
                   "when a ticker's fingerprint changes)",
                   limitations=["change-suppressed captures: each point holds until the next one (forward fill)",
                                "pregame quotes of the game-level FULL markets (game winner, spread, total, team total) "
                                "only, main lines first, within a 400 KB budget per event; every market's current price "
                                "is in markets.json",
                                f"a point is kept when bid/ask/last moves, plus a {QUOTE_HEARTBEAT_S // 3600}-hour "
                                f"heartbeat; thinned to the last state per hour above {QUOTE_MAX_POINTS} points",
                                "current week's events only"],
                   data_as_of=None)
        for eid, gid in sorted(self.board_eids.items()):
            cands = [m for m in self.markets_by_event.get(eid, []) if m["kalshi_ticker"] in quotes
                     and m["market_family"] in HISTORY_FAMILIES and m.get("period") == "FULL"]
            if not cands:
                continue
            series, used = [], 2_000
            for m in self.ordered_markets(cands, HISTORY_FAMILIES):
                s_ = {"market_id": m["market_id"], "kalshi_ticker": m["kalshi_ticker"], "points": quotes[m["kalshi_ticker"]]}
                n = _size(s_)
                if used + n > MARKET_HISTORY_BUDGET:
                    continue
                used += n
                series.append(s_)
            if not series:
                continue
            as_of = max(p["captured_at"] for s_ in series for p in s_["points"])
            qq = dict(q, data_as_of=as_of, sample_size=sum(len(s_["points"]) for s_ in series),
                      coverage=f"{len(series)} of {len(cands)} captured game-level tickers")
            doc = R.market_history(sport=SPORT, run_id=self.run_id, generated_at=self.now, event_id=eid, as_of=as_of,
                                   series=series, quality=qq,
                                   links=[R.link(rel="EVENT_RESEARCH", target_kind="event_research", label=gid,
                                                 target_id=eid, path=R.event_path(eid))])
            self.docs.append(doc)
            self.market_history_eids.add(eid)

    # ---- event research ---------------------------------------------------------------------------------
    def event_doc(self, ev, *, matchup, players, distributions, context, extensions, quality, markets, wagers):
        mrefs, prefs = self.refs_for(markets)
        eid = ev["event_id"]
        links = [R.link(rel="TEAM", target_kind="entity_profile", label=p["display_name"], target_id=p["participant_id"],
                        path=R.team_path(p["participant_id"])) for p in ev["participants"]]
        if eid in self.market_history_eids:
            links.append(R.link(rel="MARKET_HISTORY", target_kind="market_history", label="price history",
                                target_id=eid, path=R.market_history_path(eid)))
        links.append(R.link(rel="CAPABILITIES", target_kind="capability_manifest", label="capabilities",
                            path=R.app_path(R.CAPABILITIES_NAME)))
        parts = [{"participant_id": p["participant_id"], "display_name": p["display_name"],
                  "home_away": "HOME" if p["participant_id"] == ev.get("home_participant") else
                  "AWAY" if p["participant_id"] == ev.get("away_participant") else None,
                  "path": R.team_path(p["participant_id"])} for p in ev["participants"]]
        ext = dict(extensions)
        ext["markets_in_event"] = len(self.markets_by_event.get(eid, []))
        ext["markets_listed_here"] = len(mrefs)
        return R.event_research(sport=SPORT, run_id=self.run_id, generated_at=self.now, event=ev, quality=quality,
                                participants=parts, matchup=matchup, players=players, projections=prefs,
                                distributions=distributions, markets=mrefs,
                                market_history_path=R.market_history_path(eid) if eid in self.market_history_eids else None,
                                context=context, wagers=wagers, links=links, extensions=ext)

    def build_events(self, player_docs: dict):
        obs_by = {pid: {(o["metric_id"], o["window"]["label"]): o for o in lst} for pid, lst in self.team_obs.items()}
        wagers_by_event = {}
        for w in self.v1["wagers"]:
            wagers_by_event.setdefault(w.get("event_id"), []).append(w)
        settle = {s["settlement_id"]: s for s in self.v1["settlements"]}
        clv = self.inp.get("wager_clv") or {}
        matchup_metrics = [(met(f"adj_{k}"), name, "ADJ_RIDGE") for k, name, _, _ in ADJ_TEAM_METRICS] + \
                          [(met(slug), name, "SEASON") for slug, name, _, _, _ in SCHEDULE_METRICS]
        out = []
        for eid in sorted(self.events):
            ev = self.events[eid]
            gid = self.board_eids.get(eid)
            home, away = ev.get("home_participant"), ev.get("away_participant")
            matchup = []
            for mid, name, wl in matchup_metrics if gid else []:   # past games: nothing stored as of the game
                h, a = (obs_by.get(home) or {}).get((mid, wl)), (obs_by.get(away) or {}).get((mid, wl))
                if h or a:
                    matchup.append({"metric_id": mid, "name": name, "home": h, "away": a,
                                    "note": "current-week values (adjusted ratings use games before this week)"})
            wl_ = sorted(wagers_by_event.get(eid, []), key=lambda w: (w["placed_at"], w["wager_id"]))
            outcomes = []
            for w in wl_:
                s = settle.get(w.get("settlement_id")) or {}
                c = clv.get(w.get("source_bet_key")) or {}
                outcomes.append({"wager_id": w["wager_id"], "kalshi_ticker": w["kalshi_ticker"], "selection": w["selection"],
                                 "stake": w["stake"], "average_price": w.get("average_price"),
                                 "result": s.get("result"), "net_pnl": s.get("net_pnl"),
                                 "clv_state": c.get("clv_state"), "clv_dollars": c.get("clv_dollars")})
            ext = {"wager_outcomes": outcomes} if outcomes else {}
            sched = next((r for r in self.inp.get("schedule") or [] if game_eid(r["game_id"]) == eid), None)
            if sched and sched["final"]:
                ext["result"] = {"home_score": sched["home_score"], "away_score": sched["away_score"],
                                 "source": "schedule_cache.csv"}
            if gid:
                doc = self.board_event(ev, gid, matchup, player_docs, ext, [w["wager_id"] for w in wl_])
            else:
                q = self.q("PARTIAL", "the v1 publication (events/markets/wagers/settlements) and the nflverse schedule",
                           limitations=["not on the current packet: a past game referenced by the owner's wager ledger; "
                                        "no packet research (profiles, injuries, weather, projections) is stored for it",
                                        LIM_SNAPSHOT])
                ctx = {"notes": ["past game referenced by the handicap-data wager ledger; research inputs are not "
                                 "stored for past weeks"]}
                if sched:
                    ctx["venue"] = {"stadium": sched.get("stadium"), "roof": sched.get("roof"), "surface": sched.get("surface"),
                                    "location": sched.get("location"), "source": "schedule_cache.csv"}
                mk = self.markets_by_event.get(eid, [])

                def _b(ms, ev=ev, matchup=matchup, ctx=ctx, ext=ext, q=q, wl_=wl_):
                    return self.event_doc(ev, matchup=matchup, players=[], distributions=[], context=ctx, extensions=ext,
                                          quality=q, markets=ms, wagers=[w["wager_id"] for w in wl_])
                doc = _b(self.fit_markets(_b, mk, EVENT_BUDGET))
            out.append(doc)
        self.docs.extend(out)
        return out

    def board_event(self, ev, gid, matchup, player_docs, ext, wager_ids):
        g = self.games[gid]
        eid = ev["event_id"]
        players = []
        for gsis, p in sorted(self.player_rows.items()):
            if p["game_id"] != gid:
                continue
            pid = player_pid(gsis)
            if pid in player_docs:
                players.append({"participant_id": pid, "display_name": p["name"],
                                "team_id": team_pid(p["team"]) if p.get("team") else None,
                                "role": p.get("position"), "path": R.player_path(pid)})
        sim = g.get("simulation") or {}
        gen = sim.get("generated_at") or self.built_at
        dists = []
        for r in sorted(sim.get("player_projections") or [], key=lambda r: (r.get("player_id") or "", r.get("stat") or "")):
            if not r.get("distribution_quantiles_available") or r.get("football_p50") is None:
                continue
            qs = {k[-3:]: r[f"football_{k[-3:]}"] for k in ("football_p05", "football_p25", "football_p50", "football_p75",
                                                              "football_p95") if r.get(k) is not None}
            dists.append({"market_id": None, "metric_id": met(f"sim_{r['stat']}"),
                          "entity_id": player_pid(r["player_id"]) if r.get("player_id") else None,
                          "label": f"{r.get('player_name')} {STAT_LABELS.get(r['stat'], r['stat'])}",
                          "quantiles": qs, "mean": _r(r.get("football_mean")), "stdev": _r(r.get("football_sd")),
                          "samples": None, "run_id": None, "generated_at": timeutil.to_iso(gen),
                          "source": f"{sim.get('sim_version')} run {sim.get('run_id')} (packet.simulation.player_projections)",
                          "quality_status": "RESEARCH"})
        env = (g.get("game_script_inputs") or {}).get("game_environment") or {}
        for key, label in (("home_margin", "home margin"), ("total", "total points"), ("home_points", "home points"),
                           ("away_points", "away points")):
            d = env.get(key)
            if not d or not d.get("range_90"):
                continue
            qs = {"p05": d["range_90"][0], "p25": d["range_50"][0], "p75": d["range_50"][1], "p95": d["range_90"][1]}
            dists.append({"market_id": None, "metric_id": None, "entity_id": None, "label": f"simulated {label}",
                          "quantiles": {k: v for k, v in qs.items() if v is not None}, "mean": _r(d.get("mean")),
                          "stdev": None, "samples": None, "run_id": None, "generated_at": timeutil.to_iso(gen),
                          "source": f"{(g.get('game_script_inputs') or {}).get('script_source')} (packet.game_script_inputs)",
                          "quality_status": "RESEARCH"})
        inj = g.get("injuries") or {}
        inj_as_of = _capture_ts((inj.get("summary") or {}).get("capture_run_id")) or self.built_at
        injuries = [_availability(rec, inj_as_of, eid) for rec in inj.get("records") or []]
        roles = g.get("roles") or {}
        lineups = []
        for team in sorted((roles.get("by_team") or {})):
            for slot in sorted(roles["by_team"][team] or {}):
                for x in roles["by_team"][team][slot] or []:
                    lineups.append({"team": team, "slot": slot, "player": x.get("player"), "position": x.get("position"),
                                    "depth_chart_order": x.get("depth_chart_order"), "status": x.get("status"),
                                    "injury_status": x.get("injury_status"), "source": roles.get("source"),
                                    "capture_run_id": roles.get("capture_run_id")})
        weather = g.get("weather")
        venue = {"name": g.get("venue"), "roof": g.get("roof"), "surface": g.get("surface"),
                 "neutral_site": g.get("neutral_site"), "source": "packet (nflverse schedule / config/stadiums.json)"}
        notes = []
        for n in ((g.get("model_view") or {}).get("caveat"), (g.get("matchup") or {}).get("note"), roles.get("caveat")):
            if n:
                notes.append(n)
        for team in sorted(g.get("offensive_line") or {}):
            ol = g["offensive_line"][team] or {}
            if ol.get("note"):
                notes.append(f"{team} offensive line: {ol['note']}")
                break
        notes.extend(f"packet key question: {k}" for k in g.get("key_questions") or [])
        ctx = {"injuries": injuries, "lineups": lineups, "weather": weather, "venue": venue, "notes": notes}
        gsi = g.get("game_script_inputs") or {}
        ext = dict(ext)
        ext.update({
            "game_id": gid, "packet_built_at": self.built_at, "handicap_run_id": self.packet.get("handicap_run_id"),
            "matchup_pairs": (g.get("matchup") or {}).get("pairs") or [],
            "quarterbacks": g.get("quarterbacks") or {},
            "offensive_line": g.get("offensive_line") or {},
            "game_script_inputs": {k: gsi.get(k) for k in ("authority", "state", "script_source", "market_baseline",
                                                            "game_environment", "team_volume", "not_simulated")},
            "model_view": g.get("model_view"),
            "market_implied": {k: (g.get("market_implied") or {}).get(k) for k in
                               ("label", "implied_spread", "implied_total_median", "win_probability", "implied_score")},
            "data_freshness": g.get("data_freshness"),
            "real_money_status": self.packet.get("real_money_status"),
        })
        q = self.q("PARTIAL", "handicap-reports latest/packet.json games[] + the v1 publication",
                   limitations=[LIM_SNAPSHOT, "simulation distributions are RESEARCH (PROJECTABLE_NOT_YET_VALIDATED)",
                                "injury and depth-chart rows are joined by name (ESPN/Sleeper rows carry no GSIS id)",
                                "markets listed here are the game-level families in priority order within the 150 KB "
                                "document budget; every market of the event is in markets.json"],
                   data_as_of=self.built_at, source_version=self.packet.get("schema_version"))
        mk = [m for m in self.markets_by_event.get(eid, []) if m["market_family"] in EVENT_MARKET_FAMILIES]

        def _b(ms):
            return self.event_doc(ev, matchup=matchup, players=players, distributions=dists, context=ctx, extensions=ext,
                                  quality=q, markets=ms, wagers=wager_ids)
        return _b(self.fit_markets(_b, mk, EVENT_BUDGET))

    # ---- profiles -----------------------------------------------------------------------------------------
    def build_team_profiles(self, codes, player_docs):
        current = {}
        for eid, gid in self.board_eids.items():
            g = self.games[gid]
            current[g["home_team"]] = (eid, g["away_team"], "HOME")
            current[g["away_team"]] = (eid, g["home_team"], "AWAY")
        players_by_team = {}
        for gsis, p in self.player_rows.items():
            pid = player_pid(gsis)
            if pid in player_docs and p.get("team"):
                players_by_team.setdefault(p["team"], []).append(
                    {"participant_id": pid, "display_name": p["name"], "role": p.get("position"), "path": R.player_path(pid)})
        q = self.q("PARTIAL", "packet team_profiles + nflverse schedule + the v1 publication",
                   limitations=[LIM_SNAPSHOT, "no stored home/away splits; per-game rows are schedule results only "
                                "(the silver team_game table is not committed)"], data_as_of=self.built_at)
        out = []
        for code in codes:
            pid = team_pid(code)
            ent = team_participant(code, self.names)
            games, opps = [], {}
            done = [g for g in self.team_games.get(code, []) if g["final"]][-SERIES_CAP:]
            upcoming = [g for g in self.team_games.get(code, []) if not g["final"] and str(g["season"]) == self.season]
            for g in done + upcoming:
                eid = game_eid(g["game_id"])
                res = None
                if g["final"]:
                    outcome = "W" if g["pf"] > g["pa"] else "L" if g["pf"] < g["pa"] else "T"
                    res = {"for": g["pf"], "against": g["pa"], "outcome": outcome}
                status = "FINAL" if g["final"] else (self.events[eid]["status"] if eid in self.events else "SCHEDULED")
                games.append(R.game_ref(event_id=eid, start_time_utc=g["kickoff"], status=status,
                                        opponent_id=team_pid(g["opp"]), opponent_name=self.team_name(g["opp"]),
                                        home_away=g["ha"], result=res,
                                        competition=f"{g['season']} {g['game_type']} week {g['week']}",
                                        path=R.event_path(eid) if eid in self.published_events else None))
                o = opps.setdefault(g["opp"], [])
                o.append(eid)
            opponents = [{"participant_id": team_pid(c), "display_name": self.team_name(c), "event_ids": sorted(set(e)),
                          "path": R.team_path(team_pid(c))} for c, e in sorted(opps.items())]
            metrics = sorted(self.team_obs.get(pid, []), key=lambda o: (o["metric_id"], o["window"]["label"]))
            rankings = [{"ranking_id": rk["ranking_id"], "metric_id": mid, "window_label": wl, "split": None,
                         "path": R.ranking_path(rk["ranking_id"])}
                        for (mid, wl), rk in sorted(self.rankings.items()) if any(e["entity_id"] == pid for e in rk["entries"])]
            series = [{"series_id": s["series_id"], "metric_id": s["metric_id"], "x_axis": "GAME", "split": None,
                       "path": R.series_path(s["series_id"])} for s in self.team_series.get(pid, [])]
            links = [R.link(rel="SERIES", target_kind="time_series", label=self.metric_label(s["metric_id"]),
                            target_id=s["series_id"], path=s["path"]) for s in series]
            availability, mk, ext = [], [], {}
            cur_season_done = [g for g in done if str(g["season"]) == self.season]
            if cur_season_done:
                ext["record"] = {"season": self.season,
                                 "wins": sum(1 for g in cur_season_done if g["pf"] > g["pa"]),
                                 "losses": sum(1 for g in cur_season_done if g["pf"] < g["pa"]),
                                 "ties": sum(1 for g in cur_season_done if g["pf"] == g["pa"]),
                                 "source": "schedule_cache.csv"}
            if code in current:
                eid, opp, ha = current[code]
                gid = self.board_eids[eid]
                inj = self.games[gid].get("injuries") or {}
                as_of = _capture_ts((inj.get("summary") or {}).get("capture_run_id")) or self.built_at
                availability = [_availability(rec, as_of, eid) for rec in inj.get("records") or [] if rec.get("team") == code]
                mk = [m for m in self.markets_by_event.get(eid, []) if m.get("participant_id") == pid]
                links += [R.link(rel="EVENT", target_kind="event_research", label=f"{gid}", target_id=eid,
                                 path=R.event_path(eid)),
                          R.link(rel="OPPONENT", target_kind="entity_profile", label=self.team_name(opp),
                                 target_id=team_pid(opp), path=R.team_path(team_pid(opp)))]
                prof = (self.games[gid].get("team_profiles") or {}).get(code) or {}
                ext["profile_basis"] = {"basis": prof.get("basis"), "basis_season": prof.get("basis_season"),
                                        "n_games": {k: (prof.get(k) or {}).get("n_games") for k, _ in RAW_SPLITS}}
                ext["quarterbacks"] = (self.games[gid].get("quarterbacks") or {}).get(code) or []
                ext["offensive_line"] = (self.games[gid].get("offensive_line") or {}).get(code)
            players = sorted(players_by_team.get(code, []), key=lambda r: (r["display_name"], r["participant_id"]))

            def _b(ms, ent=ent, metrics=metrics, rankings=rankings, series=series, games=games, players=players,
                   opponents=opponents, availability=availability, links=links, ext=ext):
                mrefs, prefs = self.refs_for(ms)
                return R.entity_profile(sport=SPORT, run_id=self.run_id, generated_at=self.now, entity=ent,
                                        entity_type="TEAM", quality=q, season=self.season, league="NFL", metrics=metrics,
                                        series=series, rankings=rankings, games=games, players=players,
                                        opponents=opponents, markets=mrefs, projections=prefs,
                                        availability=availability, links=links, extensions=ext)
            out.append(_b(self.fit_markets(_b, mk, PROFILE_BUDGET)))
        self.docs.extend(out)
        return out

    def metric_label(self, mid):
        m = self.metrics.get(mid) or {}
        return m.get("name") or mid

    def build_player_profiles(self) -> dict:
        q = self.q("PARTIAL", "handicap-reports latest/packet.json games[].simulation.player_projections, "
                   "game_script_inputs.player_opportunity, quarterbacks, injuries, roles + the v1 publication",
                   limitations=["only players the coherent simulation projected in the current packet",
                                "projections and usage shares are RESEARCH (PROJECTABLE_NOT_YET_VALIDATED); no 2026 "
                                "player game logs are committed", LIM_SNAPSHOT,
                                "availability joined by name within team (ESPN/Sleeper rows carry no GSIS id)"],
                   data_as_of=self.sim_generated_at or self.built_at)
        out = {}
        for gsis in sorted(self.player_rows):
            p = self.player_rows[gsis]
            pid = player_pid(gsis)
            ent = self.player_participant(p)
            obs, splits = self.player_observations(p)
            eid = game_eid(p["game_id"])
            g = self.games[p["game_id"]]
            team = p.get("team")
            opp = (g["away_team"] if team == g["home_team"] else g["home_team"]) if team in (g["home_team"], g["away_team"]) else None
            games = []
            if eid in self.events:
                ev = self.events[eid]
                games.append(R.game_ref(event_id=eid, start_time_utc=ev["start_time_utc"], status=ev["status"],
                                        opponent_id=team_pid(opp) if opp else None,
                                        opponent_name=self.team_name(opp) if opp else None,
                                        home_away="HOME" if team == g["home_team"] else "AWAY" if team == g["away_team"] else None,
                                        competition=ev.get("competition"), path=R.event_path(eid)))
            team_ref = {"participant_id": team_pid(team), "display_name": self.team_name(team), "short_name": team,
                        "path": R.team_path(team_pid(team))} if team else None
            links = []
            if team_ref:
                links.append(R.link(rel="TEAM", target_kind="entity_profile", label=team_ref["display_name"],
                                    target_id=team_ref["participant_id"], path=team_ref["path"]))
            if eid in self.events:
                links.append(R.link(rel="EVENT", target_kind="event_research", label=p["game_id"], target_id=eid,
                                    path=R.event_path(eid)))
            mk = [m for m in self.markets_by_event.get(eid, []) if m.get("player_id") == pid]
            ext = {"gsis_id": gsis, "position": p.get("position"),
                   "kalshi_player_ids": sorted({r.get("player_kalshi_id") for r in p["rows"] if r.get("player_kalshi_id")}),
                   "p_active": next((r.get("p_active") for r in p["rows"] if r.get("p_active") is not None), None)}
            if p.get("qb"):
                ext["quarterback"] = {k: p["qb"].get(k) for k in ("depth_chart_order", "status", "injury_status",
                                                                   "availability_confidence", "profile_matched_by", "note")}
                ext["quarterback"]["dropbacks"] = ((p["qb"].get("profile") or {}).get("dropbacks"))
            availability = self.availability_for(team, p["name"], p["game_id"]) if team else []

            def _b(ms, ent=ent, obs=obs, splits=splits, games=games, team_ref=team_ref, links=links, ext=ext,
                   availability=availability, opp=opp, eid=eid):
                mrefs, prefs = self.refs_for(ms)
                opps = [{"participant_id": team_pid(opp), "display_name": self.team_name(opp), "event_ids": [eid],
                         "path": R.team_path(team_pid(opp))}] if opp else []
                return R.entity_profile(sport=SPORT, run_id=self.run_id, generated_at=self.now, entity=ent,
                                        entity_type="PLAYER", quality=q, season=self.season, league="NFL", team=team_ref,
                                        metrics=obs, splits=splits, games=games, opponents=opps, markets=mrefs,
                                        projections=prefs, availability=availability, links=links, extensions=ext)
            out[pid] = _b(self.fit_markets(_b, mk, PROFILE_BUDGET))
        self.docs.extend(out.values())
        return out

    # ---- registry -------------------------------------------------------------------------------------------
    def build_registry(self):
        items = []
        sc = self.inp.get("scorecard")
        for mid in sorted(self.metrics):
            m = self.metrics[mid]
            kind = m["kind"]
            windows = sorted(self.metric_windows.get(mid, set()))
            splits = sorted(self.metric_splits.get(mid, set()))
            ranked = mid in self.metric_ranked
            sup = R.supports(rank=ranked, percentile=ranked, time_series=mid in self.metric_series,
                             windows=len(windows) > 1, splits=bool(splits), opponent_adjustment=kind == "adj")
            if kind == "raw":
                items.append(R.metric(
                    sport=SPORT, slug=m["slug"], name=m["name"], short_name=m["short"],
                    description=(f"{m['desc']}, averaged over the window's team-games: SEASON = the basis season's games, "
                                 "L6 = the last 6, L34 = the last 34 across seasons (games strictly before the packet "
                                 "week). Raw and unadjusted: it describes what happened, not how good the team is."),
                    entity_type="TEAM", category=m["category"], subcategory="raw split", unit=m["unit"],
                    stat_type=m["stype"], source="nflverse play-by-play -> silver team_game -> nfl_edge.handicap.teamprofile",
                    quality=self.q_team_raw(), freshness="FRESH", higher_is_better=m["hib"],
                    comparison_universe=f"NFL teams, {self.season}", supports=sup, windows=windows,
                    source_version=self.packet.get("schema_version"), methodology_version=METHODOLOGY_VERSION,
                    update_frequency="per RUN NFL / shadow-cycle report (about every 2 hours on a slate)",
                    known_limitations=self.q_team_raw()["limitations"]))
            elif kind == "adj":
                items.append(R.metric(
                    sport=SPORT, slug=m["slug"], name=m["name"], short_name=m["short"],
                    description=(f"Opponent-adjusted rating ({m['key']}): the team's "
                                 f"{'offensive' if m['key'].startswith('off_') else 'defensive'} coefficient from the "
                                 f"{ADJ_METHOD}."
                                 + (" Defensive ratings are what the defence allows above average: lower is better."
                                    if m["hib"] is False and m["key"].startswith("def_") else "")),
                    entity_type="TEAM", category="opponent-adjusted",
                    subcategory="offense" if m["key"].startswith("off_") else "defense",
                    unit="deviation from league mean", stat_type="RATING",
                    source="nfl_edge.research.team_ratings.snapshot_ratings via packet team_profiles[].adjusted",
                    quality=self.q_team_adj(), freshness="FRESH", higher_is_better=m["hib"],
                    comparison_universe=f"NFL teams, {self.season}", supports=sup, windows=windows,
                    source_version=self.packet.get("schema_version"), methodology_version=METHODOLOGY_VERSION,
                    update_frequency="per RUN NFL / shadow-cycle report",
                    known_limitations=self.q_team_adj()["limitations"]))
            elif kind == "schedule":
                items.append(R.metric(
                    sport=SPORT, slug=m["slug"], name=m["name"], short_name=m["short"],
                    description=(f"{m['desc']}. SEASON = the mean over the current season's completed games; the GAME "
                                 f"series carries one point per completed game (last {SERIES_CAP}) with a trailing "
                                 f"{ROLLING_N}-game mean."),
                    entity_type="TEAM", category="results", unit="points", stat_type="SCORE",
                    source="nflverse schedule (market-data data/kalshi/capture/schedule_cache.csv)",
                    quality=self.q_schedule(), freshness="FRESH", higher_is_better=m["hib"],
                    comparison_universe=f"NFL teams, {self.season} season", supports=sup, windows=windows,
                    methodology_version=METHODOLOGY_VERSION, historical_start="1999-09-12",
                    update_frequency="hourly schedule-cache refresh", known_limitations=self.q_schedule()["limitations"]))
            elif kind == "sim":
                stat = m["stat"]
                items.append(R.metric(
                    sport=SPORT, slug=m["slug"], name=f"Simulated {STAT_LABELS.get(stat, stat)}",
                    short_name=f"Sim {stat}",
                    description=(f"The coherent simulation's football-only mean of {STAT_LABELS.get(stat, stat)} for the "
                                 "player's game this week (packet simulation.player_projections football_mean); the "
                                 "observation's extensions and the event's distributions carry sd and p05..p95, the "
                                 "market-implied mean and the reconciled final mean. Research evidence, never a bet."),
                    entity_type="PLAYER", category="projection", subcategory="simulation",
                    unit=STAT_UNITS.get(stat), stat_type="COUNT",
                    source="nfl_edge.sim (sim-1.1.0) via packet simulation.player_projections",
                    quality=self.q_sim(), freshness="FRESH", higher_is_better=None, supports=sup, windows=windows,
                    source_version=(self.first_game_value("simulation", "sim_version")),
                    methodology_version=METHODOLOGY_VERSION, update_frequency="with every RUN NFL / shadow cycle",
                    known_limitations=self.q_sim()["limitations"]))
            elif kind == "usage":
                share = m["share"]
                items.append(R.metric(
                    sport=SPORT, slug=m["slug"], name=f"Projected {share.replace('_', ' ')}",
                    short_name=f"Proj {share.split('_')[0]} share",
                    description=(f"The simulation's projected {share.replace('_', ' ')} for the player's game "
                                 "(packet game_script_inputs.player_opportunity): a model input, not observed usage."),
                    entity_type="PLAYER", category="usage", subcategory="projected opportunity", unit="share",
                    stat_type="RATE", source="nfl_edge.sim features via packet game_script_inputs.player_opportunity",
                    quality=self.q_usage(), freshness="FRESH", higher_is_better=None, supports=sup, windows=windows,
                    methodology_version=METHODOLOGY_VERSION, update_frequency="with every RUN NFL / shadow cycle",
                    known_limitations=self.q_usage()["limitations"]))
            elif kind == "qb":
                items.append(R.metric(
                    sport=SPORT, slug=m["slug"], name=m["name"], short_name=m["short"],
                    description=(f"Quarterback {m['key'].replace('_', ' ')} from play-by-play of the basis season "
                                 "(nfl_edge.handicap.teamprofile.build_qb_profiles): SEASON = all dropbacks, "
                                 "L200_DROPBACKS = the most recent 200, split pressure = under_pressure (QB hit or sack) / "
                                 "clean_pocket. Null below 100 dropbacks."),
                    entity_type="PLAYER", category="quarterback", unit=None, stat_type="RATE",
                    source="nflverse play-by-play via packet quarterbacks[].profile", quality=self.q_qb(),
                    freshness="FRESH", higher_is_better=m["hib"], supports=sup, windows=windows, splits=splits,
                    methodology_version=METHODOLOGY_VERSION, update_frequency="per RUN NFL report",
                    known_limitations=self.q_qb()["limitations"]))
        items.append(self.model_metric(sc))
        return R.metric_registry(sport=SPORT, run_id=self.run_id, generated_at=self.now, metrics=items)

    def first_game_value(self, block, key):
        for gid in sorted(self.games):
            v = (self.games[gid].get(block) or {}).get(key)
            if v:
                return v
        return None

    def q_sim(self):
        return self.q_research("coherent simulation sim-1.1.0 (market-data data/shadow/sim) via packet "
                               "simulation.player_projections",
                               ["research only: every simulation row is PROJECTABLE_NOT_YET_VALIDATED; the packet "
                                "recommends nothing", "quantiles exist only for players and stats the simulation exposed",
                                LIM_SNAPSHOT])

    def q_usage(self):
        return self.q_research("packet game_script_inputs.player_opportunity (simulation features)",
                               ["projected opportunity shares are simulation inputs, not observed usage",
                                "observed 2026 usage per player-game is not committed as a table (history exists only "
                                "as 2016-2025 research parquets)", LIM_SNAPSHOT])

    def q_qb(self):
        return self.q_research("packet quarterbacks[].profile (nfl_edge.handicap.teamprofile.build_qb_profiles)",
                               ["matched to depth-chart quarterbacks by a name heuristic",
                                "null below 100 dropbacks (QB_MIN_DROPBACKS)", LIM_SNAPSHOT,
                                "player metrics are RESEARCH: 2026 per-game player values are not committed as a table"])

    def model_metric(self, sc):
        ext = {}
        if sc:
            d = sc["doc"]
            v = (d.get("views") or {}).get("latest_pregame") or {}
            ec = v.get("event_calibration") or {}
            ext["scorecard"] = {
                "source": f"market-data {sc['path']}", "primary_sample_unit": d.get("primary_sample_unit"),
                "sample": (d.get("sample_units") or {}).get("latest_pregame", {}).get("n_unique_contracts"),
                "n_games": v.get("n_games"),
                "model_event_probability": ec.get("model_event_probability"),
                "market_where_spaces_coincide": {k: (ec.get("market_where_spaces_coincide") or {}).get(k)
                                                 for k in ("n", "brier", "log_loss", "mean_predicted", "actual_rate")},
                "calibration_by_event_probability": ec.get("calibration_by_event_probability"),
                "contract_payout_quality": {k: (v.get("contract_payout_quality") or {}).get(k)
                                            for k in ("model_contract_value", "market_at_snapshot")},
                "clv": {k: (v.get("clv") or {}).get(k) for k in ("n", "mean_signed_clv_mid", "mean_signed_clv_executable",
                                                                  "positive_clv_share", "toward_share_of_directional")},
                "by_family": {fam: {k: seg.get(k) for k in ("n_contracts", "event_brier", "model_payout_mse",
                                                            "market_payout_mse")}
                              for fam, seg in sorted(((d.get("segments") or {}).get("family") or {}).items())},
            }
        mv = self.v1["manifest"].get("model_version")
        q = self.q("PARTIAL", "the v1 model_prices (incumbent production shadow ledger)",
                   limitations=["research evidence: the packet recommends nothing (real_money_status NOT VALIDATED)",
                                "model_uncertainty is null on every incumbent row",
                                "the model is behind the closing market on game outcomes and redundant on player props "
                                "(packet model_view caveat; scorecard in extensions)"],
                   data_as_of=self.built_at, source_version=mv)
        return R.metric(
            sport=SPORT, slug="incumbent_fair_probability", name="Incumbent model fair probability",
            short_name="Model P(YES)",
            description=("The incumbent production shadow model's probability that a contract settles YES "
                         "(v1 model_prices.fair_probability; projection_refs point here). Its historical calibration, "
                         "Brier / log loss against the market, CLV and per-family accuracy from the repository's "
                         "cumulative scorecard are in extensions.scorecard."),
            entity_type="MARKET", category="model", subcategory="incumbent", unit="probability", stat_type="PROBABILITY",
            source="market-data data/shadow/ledger (shadow-0.4.0) via the v1 export", quality=q, freshness="FRESH",
            higher_is_better=None, supports=R.supports(), source_version=mv, methodology_version=METHODOLOGY_VERSION,
            update_frequency="every 2 hours + decision horizons", known_limitations=q["limitations"], extensions=ext)


def _r(v, nd=4):
    return None if v is None else round(float(v), nd)


def _capture_ts(run_id):
    """`20261001T234647Z` -> aware timestamp, or None."""
    if not run_id:
        return None
    try:
        return timeutil.to_iso(datetime.strptime(str(run_id), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc))
    except ValueError:
        return None


def _availability(rec: dict, as_of, eid) -> dict:
    who = f"{rec.get('player')} ({rec.get('position')}, {rec.get('team')})"
    bits = [b for b in (rec.get("detail"), f"practice {rec['practice']}" if rec.get("practice") else None,
                        f"return {rec['return_date']}" if rec.get("return_date") else None,
                        f"impact: {rec['likely_role_impact']}" if rec.get("likely_role_impact") else None,
                        "changed since previous capture" if rec.get("changed_since_previous_capture") else None) if b]
    return {"status": str(rec.get("state") or "UNKNOWN").upper().replace(" ", "_"),
            "detail": who + (": " + "; ".join(bits) if bits else ""), "as_of": as_of,
            "source": str(rec.get("source") or "injury capture"), "event_id": eid}


# ------------------------------------------------------------------------------------------------ capabilities

def _cap_table(b: "_Builder", docs: list[dict]) -> list[dict]:
    paths = {"team": None, "player": None, "qb_player": None, "event_board": None, "event_past": None,
             "ranking": None, "series": None, "mh": None}
    for d in docs:
        k = d["kind"]
        if k == "entity_profile" and d["entity_type"] == "TEAM" and paths["team"] is None and d["metrics"]:
            paths["team"] = R.path_for(d)
        elif k == "entity_profile" and d["entity_type"] == "PLAYER":
            paths["player"] = paths["player"] or R.path_for(d)
            if d["splits"] and paths["qb_player"] is None:
                paths["qb_player"] = R.path_for(d)
        elif k == "event_research":
            if d["context"]["injuries"] and paths["event_board"] is None:
                paths["event_board"] = R.path_for(d)
            if d["wagers"] and paths["event_past"] is None:
                paths["event_past"] = R.path_for(d)
        elif k == "ranking" and paths["ranking"] is None:
            paths["ranking"] = R.path_for(d)
        elif k == "time_series" and paths["series"] is None:
            paths["series"] = R.path_for(d)
        elif k == "market_history" and paths["mh"] is None:
            paths["mh"] = R.path_for(d)
    ap = {k: (R.app_path(v) if v else None) for k, v in paths.items()}
    metrics_path = R.app_path(R.METRICS_NAME)
    n = {k: sum(1 for d in docs if d["kind"] == k) for k in ("ranking", "time_series", "market_history", "event_research")}
    n_team = sum(1 for d in docs if d["kind"] == "entity_profile" and d["entity_type"] == "TEAM")
    n_player = sum(1 for d in docs if d["kind"] == "entity_profile" and d["entity_type"] == "PLAYER")
    mh = [d for d in docs if d["kind"] == "market_history"]
    mh_since = min((s_["points"][0]["captured_at"] for d in mh for s_ in d["series"] if s_["points"]), default=None)
    mh_points = sum(len(s_["points"]) for d in mh for s_ in d["series"])
    sched = [r for r in b.inp.get("schedule") or [] if r["final"]]
    first_pub = min((g["kickoff"] for gl in b.team_games.values() for g in gl if g["final"]), default=None) \
        if hasattr(b, "team_games") else None
    raw_ids = sorted(m for m in b.metrics if b.metrics[m]["kind"] == "raw")
    adj_ids = sorted(m for m in b.metrics if b.metrics[m]["kind"] == "adj")
    sched_ids = sorted(m for m in b.metrics if b.metrics[m]["kind"] == "schedule")
    sim_ids = sorted(m for m in b.metrics if b.metrics[m]["kind"] == "sim")
    usage_ids = sorted(m for m in b.metrics if b.metrics[m]["kind"] == "usage")
    qb_ids = sorted(m for m in b.metrics if b.metrics[m]["kind"] == "qb")
    raw_windows = sorted({w for m in raw_ids for w in b.metric_windows.get(m, ())})
    wk = f"{b.season} week {b.packet.get('week')}"

    def ev(*ps):
        return [p for p in ps if p]

    C = R.capability
    caps = [
        C(capability="team_profiles", status="PARTIAL", entity_types=["TEAM"],
          summary=f"{n_team} team profiles: packet raw splits + opponent-adjusted ratings, schedule results, rankings",
          limitations=[LIM_SNAPSHOT], evidence=ev(ap["team"]), coverage=f"all 32 teams; packet metrics for {wk}",
          since=b.built_at),
        C(capability="player_profiles", status="PARTIAL", entity_types=["PLAYER"],
          summary=f"{n_player} player profiles: players the coherent simulation projected this week",
          limitations=["only players with simulation projections in the current packet",
                       "projections and usage are RESEARCH; no 2026 player game logs are committed"],
          evidence=ev(ap["player"]), coverage=wk, since=b.built_at),
        C(capability="event_research", status="PARTIAL", entity_types=["EVENT"],
          summary=f"{n['event_research']} event documents: matchup, injuries, depth charts, weather, game script, "
                  "simulation distributions, markets",
          limitations=[LIM_SNAPSHOT, "past (wagered) events carry markets, wagers and results only"],
          evidence=ev(ap["event_board"], ap["event_past"]), coverage=wk, since=b.built_at),
        C(capability="team_metrics", status="PARTIAL", entity_types=["TEAM"],
          summary=f"{len(raw_ids)} raw EPA/SR/rate metrics ({', '.join(raw_windows)}), {len(sched_ids)} schedule metrics",
          limitations=[LIM_SNAPSHOT, "splits null below 4 games; the silver team_game table is not committed"],
          evidence=ev(ap["team"]), metrics=raw_ids + sched_ids, windows=raw_windows, since=b.built_at),
        C(capability="player_metrics", status="RESEARCH", entity_types=["PLAYER"],
          summary="simulation projections, projected usage shares and QB profile rates for projected players",
          limitations=["committed only as 2016-2025 study parquets; 2026 values are not in a table",
                       "published values are current-week RESEARCH observations"],
          evidence=ev(ap["player"]), metrics=sim_ids + qb_ids),
        C(capability="team_game_logs", status="PARTIAL", entity_types=["TEAM"],
          summary="per-team game lists with scores; per-game points series; the L34 baseline in the profile",
          limitations=["the silver team_game table (per-game EPA / SR box) is rebuilt per run and not committed; "
                       "published per-game rows are schedule results only",
                       f"game lists cover {HISTORY_SEASONS} seasons; series capped at the last {SERIES_CAP} games",
                       "research/game_model/ratings_snapshots.parquet (2009-2025) is not exposed: parquet, a different "
                       "rating code path"],
          evidence=ev(ap["team"], ap["series"]), since=first_pub),
        C(capability="player_game_logs", status="RESEARCH", entity_types=["PLAYER"],
          summary="not published: committed only as 2016-2025 research parquets (research_table, player_usage)",
          limitations=["2026 rows are not committed as a table"]),
        C(capability="historical_results", status="VERIFIED", entity_types=["TEAM", "EVENT"],
          summary="final scores per team game from the nflverse schedule cache",
          limitations=[f"published: the last {HISTORY_SEASONS} seasons per team; source covers 1999-2026"],
          evidence=ev(ap["team"], ap["series"]), coverage=f"{len(sched)} final games in the source",
          since=first_pub),
        C(capability="opponents", status="VERIFIED", entity_types=["TEAM"],
          summary="opponent of every listed game, linked to its profile", evidence=ev(ap["team"]), since=first_pub),
        C(capability="opponent_adjustment", status="PARTIAL", entity_types=["TEAM"],
          summary=f"{len(adj_ids)} opponent-adjusted ridge ratings per team ({ADJ_METHOD})",
          limitations=[LIM_SNAPSHOT, "no accuracy or stability test; no standard errors"],
          evidence=ev(ap["team"], ap["ranking"]), metrics=adj_ids, windows=["ADJ_RIDGE"], since=b.built_at),
        C(capability="schedule_strength", status="UNAVAILABLE", summary="nothing in the repository computes it",
          reasons=["no strength-of-schedule computation exists; derivable from adjusted ratings x schedule but not stored"]),
        C(capability="recent_form_windows", status="PARTIAL", entity_types=["TEAM", "PLAYER"],
          summary="fixed recent windows: L6 / L34 team splits, the last 200 QB dropbacks, a trailing 4-game points mean",
          limitations=["fixed L6 / L34 / 200-dropback windows, not L3/L5", "L6 is null below 4 current-season games"],
          evidence=ev(ap["team"]), windows=[w for w in raw_windows if w != "SEASON"] + ["L200_DROPBACKS"]),
        C(capability="usage", status="RESEARCH", entity_types=["PLAYER"],
          summary="projected target / carry shares for projected players (simulation inputs)",
          limitations=["projected shares, not observed usage; usage history is 2016-2025 research parquets only"]
          + ([opportunity_note(b.opportunity_unavailable, len(b.games))] if b.opportunity_unavailable else []),
          evidence=ev(ap["player"]), metrics=usage_ids),
        C(capability="lineups", status="PARTIAL", entity_types=["EVENT", "PLAYER"],
          summary="Sleeper depth chart per team (slot, order, status) in event context",
          limitations=["depth-chart order is a stated intention, not measured snap share", LIM_SNAPSHOT],
          evidence=ev(ap["event_board"]), since=b.built_at),
        C(capability="injuries", status="VERIFIED", entity_types=["EVENT", "TEAM", "PLAYER"],
          summary="ESPN + Sleeper injury records of the current capture, with changes since the previous one",
          limitations=["records carry names, not GSIS ids; joined to players by name within team"],
          evidence=ev(ap["event_board"], ap["team"]), since=b.built_at),
        C(capability="matchup_metrics", status="PARTIAL", entity_types=["EVENT"],
          summary="home vs away adjusted ratings and season scoring per event; packet matchup.pairs in extensions",
          limitations=[LIM_SNAPSHOT, "derived from the ridge ratings; no history"], evidence=ev(ap["event_board"]),
          since=b.built_at),
        C(capability="projection_distributions", status="PARTIAL", entity_types=["PLAYER", "EVENT"],
          summary="simulation p05..p95 per player stat and the game environment (margin, total, team points)",
          limitations=["research only (PROJECTABLE_NOT_YET_VALIDATED); every distribution is flagged RESEARCH"],
          evidence=ev(ap["event_board"]), metrics=sim_ids, since=b.built_at),
        C(capability="raw_projections", status="PARTIAL", entity_types=["MARKET"],
          summary="incumbent model fair probability per market (v1 model_prices) as projection_refs",
          limitations=["research_only unless the handicap-data ledger recorded a decision", "model_uncertainty null"],
          evidence=ev(ap["event_board"]), metrics=[met("incumbent_fair_probability")],
          since=b.built_at),
        C(capability="market_prices", status="VERIFIED", entity_types=["MARKET"],
          summary="current bid/ask/mid of every listed contract (v1 markets, referenced from events and profiles)",
          evidence=ev(ap["event_board"])),
        C(capability="market_price_history", status="VERIFIED", entity_types=["MARKET", "EVENT"],
          summary=f"{n['market_history']} per-event histories, {mh_points} compressed capture points",
          limitations=["game-level FULL markets within a 400 KB budget per event; current week only",
                       "change-suppressed captures, forward-filled"],
          evidence=ev(ap["mh"]), coverage=f"captures {mh_since[:10] if mh_since else '-'} onward", since=mh_since),
        C(capability="advanced_stats", status="PARTIAL", entity_types=["TEAM", "PLAYER"],
          summary="EPA / success rate / CPOE / PROE / explosive / sack rates (team) and QB EPA, CPOE, pressure splits",
          limitations=[LIM_SNAPSHOT, "QB profile null below 100 dropbacks", "history only as research parquets"],
          evidence=ev(ap["team"], ap["qb_player"]), metrics=raw_ids + qb_ids, since=b.built_at),
        C(capability="situational_splits", status="PARTIAL", entity_types=["PLAYER", "TEAM"],
          summary="QB pressure splits (under_pressure / clean_pocket); neutral-script, early-down and red-zone team "
                  "metric variants",
          limitations=["no stored home/away split tables (derivable from team_game, which is not committed)"],
          evidence=ev(ap["qb_player"] or ap["team"]), splits=["pressure"]),
        C(capability="player_props", status="VERIFIED", entity_types=["MARKET", "PLAYER"],
          summary="player-stat contracts with current prices in player profiles (market side)",
          limitations=["model side is RESEARCH"], evidence=ev(ap["player"])),
        C(capability="team_props", status="VERIFIED", entity_types=["MARKET", "TEAM"],
          summary="team total / team stat / first-TD-team / race-to contracts (market side)", evidence=ev(ap["team"])),
        C(capability="game_markets", status="VERIFIED", entity_types=["MARKET", "EVENT"],
          summary="game winner / spread / total incl. periods (market side)", evidence=ev(ap["event_board"], ap["mh"])),
        C(capability="play_by_play", status="UNAVAILABLE", summary="not exposable from a branch",
          reasons=["nflverse play-by-play is downloaded per run (bronze) and never committed; only aggregates survive"]),
        C(capability="weather", status="VERIFIED", entity_types=["EVENT"],
          summary="NWS forecast at kickoff with the previous capture and a materiality flag",
          evidence=ev(ap["event_board"]), since=b.built_at),
        C(capability="venue_effects", status="UNAVAILABLE", summary="venue attributes only (roof, surface, stadium)",
          reasons=["no venue effect estimate exists anywhere in the repository; attributes are in event context"]),
        C(capability="calibration", status="VERIFIED", entity_types=["MARKET"],
          summary="incumbent cumulative scorecard: Brier / log loss vs market and calibration bands "
                  "(metrics.json, met_nfl.incumbent_fair_probability extensions.scorecard)",
          limitations=["research evaluation: the model is worse than the market overall"],
          evidence=[metrics_path] if b.inp.get("scorecard") else []),
        C(capability="historical_accuracy", status="VERIFIED", entity_types=["MARKET", "EVENT"],
          summary="per-family accuracy (scorecard) and the owner's settled wagers per past event",
          limitations=["research evaluation"], evidence=ev(metrics_path if b.inp.get("scorecard") else None, ap["event_past"])),
        C(capability="clv", status="VERIFIED", entity_types=["MARKET", "EVENT"],
          summary="model CLV (scorecard) and owner-wager CLV where the postmortem established it (event extensions)",
          limitations=["owner CLV only where clv_state is CLV_VALID"],
          evidence=ev(metrics_path if b.inp.get("scorecard") else None, ap["event_past"])),
        C(capability="wager_history", status="VERIFIED", entity_types=["EVENT"],
          summary="owner wagers and settlements per event (wager ids into the v1 wagers.json, outcomes in extensions)",
          evidence=ev(ap["event_past"])),
        C(capability="rankings", status="PARTIAL", entity_types=["TEAM"],
          summary=f"{n['ranking']} team rankings over every team with a value",
          limitations=[LIM_SNAPSHOT + " for packet metrics", "no player rankings (no well-defined player universe)"],
          evidence=ev(ap["ranking"]), since=b.built_at),
        C(capability="time_series", status="PARTIAL", entity_types=["TEAM"],
          summary=f"{n['time_series']} per-game team series (points for / against / margin)",
          limitations=["packet team metrics have no committed history, so only schedule-derived series exist",
                       f"capped at the last {SERIES_CAP} games"],
          evidence=ev(ap["series"]), since=first_pub),
        C(capability="comparisons", status="PARTIAL", entity_types=["TEAM"],
          summary="every team observation carries rank, universe size, league average / median, best and worst",
          limitations=[LIM_SNAPSHOT], evidence=ev(ap["team"], ap["ranking"])),
        C(capability="search", status="VERIFIED", summary="teams, players, events, metrics and rankings",
          evidence=[R.app_path(R.SEARCH_NAME)]),
    ]
    return caps


# ------------------------------------------------------------------------------------------------ public API

def build_explorer(inputs: dict, *, now) -> list[dict]:
    """Pure: loaded inputs in, explorer documents out (registry, capabilities and search index included)."""
    b = _Builder(inputs, now)
    codes = sorted(b.names) or sorted({c for g in b.games.values() for c in (g["home_team"], g["away_team"])})
    b.collect_players()
    b.build_team_metrics(codes)
    b.build_schedule(codes)
    b.build_market_history()
    player_docs = b.build_player_profiles()
    b.build_events(player_docs)
    b.build_team_profiles(codes, player_docs)
    registry = b.build_registry()
    docs = list(b.docs) + [registry]
    caps = _cap_table(b, docs)
    manifest = R.capability_manifest(
        sport=SPORT, run_id=b.run_id, generated_at=b.now, capabilities=caps, audit_date=AUDIT_DATE,
        split_dimensions=[{"dimension": "pressure", "values": list(QB_SPLITS), "status": "RESEARCH"},
                          {"dimension": "home_away", "values": [], "status": "UNAVAILABLE"}],
        windows=[R.window("SEASON"), R.window("LAST_N", n=6), R.window("LAST_N", n=34),
                 R.window("CUSTOM", label="ADJ_RIDGE"), R.window("GAME"),
                 R.window("LAST_N", n=200, label="L200_DROPBACKS")],
        notes=["Audit: scratchpad phase2 audit_nfl.md (2026-10-03), section 4 matrix and section 10.",
               "Not exposed in this pass: per-run incumbent model-probability history (market-data data/shadow/ledger, "
               "354 MB of gz per season), the 2025 backfill candles, Shadow v2 / three-arm research arms, "
               "research/game_model/ratings_snapshots.parquet."])
    docs.append(manifest)
    docs.append(build_search(b, docs))
    return docs


def build_search(b: "_Builder", docs: list[dict]) -> dict:
    entries = []
    for d in docs:
        k = d["kind"]
        if k == "entity_profile":
            e = d["entity"]
            if d["entity_type"] == "TEAM":
                entries.append(R.search_entry(id=e["participant_id"], kind="TEAM", label=e["display_name"],
                                              path=R.app_path(R.path_for(d)), sport=SPORT, aliases=[e["short_name"]],
                                              league="NFL", season=b.season))
            else:
                team = (d.get("team") or {}).get("short_name")
                pos = (e.get("metadata") or {}).get("position")
                entries.append(R.search_entry(id=e["participant_id"], kind="PLAYER", label=e["display_name"],
                                              path=R.app_path(R.path_for(d)), sport=SPORT,
                                              secondary=" ".join(x for x in (pos, team) if x) or None, team=team,
                                              position=pos, league="NFL", season=b.season))
        elif k == "event_research":
            ev = d["event"]
            names = {p["participant_id"]: p.get("short_name") or p["display_name"] for p in ev["participants"]}
            label = f"{names.get(ev.get('away_participant'), '?')} @ {names.get(ev.get('home_participant'), '?')}"
            full = " ".join(p["display_name"] for p in ev["participants"])
            entries.append(R.search_entry(id=ev["event_id"], kind="EVENT", label=label, path=R.app_path(R.path_for(d)),
                                          sport=SPORT, secondary=ev.get("competition"),
                                          aliases=[full, (ev.get("source_ids") or {}).get("nflverse_game_id") or ""],
                                          league="NFL", season=ev.get("season")))
        elif k == "ranking":
            name = b.metric_label(d["metric_id"])
            entries.append(R.search_entry(id=d["ranking_id"], kind="RANKING", label=f"{name} ranking ({d['window']['label']})",
                                          path=R.app_path(R.path_for(d)), sport=SPORT, secondary=d["universe"]["label"],
                                          season=d["universe"]["season"]))
        elif k == "metric_registry":
            for m in d["items"]:
                entries.append(R.search_entry(id=m["metric_id"], kind="METRIC", label=m["name"],
                                              path=R.app_path(R.METRICS_NAME), sport=SPORT, secondary=m["category"],
                                              aliases=[m["short_name"]]))
    return R.search_index(sport=SPORT, run_id=b.run_id, generated_at=b.now, entries=entries)


def explorer_as_of(docs: list[dict], inputs: dict):
    stamps = [timeutil.to_iso(inputs["packet"].get("built_at") or inputs["report_manifest"]["built_at"])]
    stamps += [d["as_of"] for d in docs if d["kind"] == "market_history"]
    return _max_ts(*stamps)


def export_explorer(app_root, *, reports_dir, market_data_root=None, now=None, read_lines=_file_lines) -> dict:
    """Load, build, publish. `now` defaults to the v1 manifest's generated_at (the same publication)."""
    inputs = load_inputs(reports_dir=reports_dir, app_root=app_root, market_data_root=market_data_root,
                         read_lines=read_lines)
    manifest = inputs["v1"]["manifest"]
    now = timeutil.to_iso(now) if now is not None else manifest["generated_at"]
    docs = build_explorer(inputs, now=now)
    as_of = explorer_as_of(docs, inputs)
    q = R.quality(status="PARTIAL", source="nfl-edge-finder handicap packet, market-data captures and schedule, v1 payload",
                  generated_at=now, production=True, data_as_of=as_of, methodology_version=METHODOLOGY_VERSION,
                  coverage=f"{inputs['packet'].get('season')} week {inputs['packet'].get('week')}",
                  limitations=[LIM_SNAPSHOT + " for packet-derived research",
                               "see capabilities.json for every capability's status"])
    warnings = []
    if not inputs["schedule"]:
        warnings.append("no schedule_cache.csv: no historical results, series or schedule metrics")
    if not inputs["quotes"]:
        warnings.append("no capture quotes read: no market history")
    if not inputs["scorecard"]:
        warnings.append("no incumbent scorecard: calibration / accuracy summaries absent")
    games = inputs["packet"].get("games") or []
    unavailable = {}
    for g in games:
        reason = player_opportunity(g)[1]
        if reason is not None:
            unavailable[g["game_id"]] = reason
    if unavailable:
        warnings.append(opportunity_note(unavailable, len(games)))
    index = R.publish_explorer(app_root=Path(app_root), sport=SPORT, run_id=manifest["run_id"], generated_at=now,
                               documents=docs, quality=q, as_of=as_of, commit_sha=manifest.get("commit_sha"),
                               base_manifest_run_id=manifest["run_id"], warnings=warnings)
    return {"index": index, "quote_files": inputs["quote_files"], "warnings": warnings}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="export the Edge Finder research explorer beside app/latest")
    ap.add_argument("--reports-dir", "--data-root", dest="reports_dir",
                    default=os.path.join(REPO_ROOT, "data", "handicap_report"),
                    help="the RUN NFL report directory the v1 export read (manifest.json + packet.json)")
    ap.add_argument("--market-data-root", default=None, help="market-data checkout (schedule, captures, scorecards)")
    ap.add_argument("--out", required=True, help="the app root app_export.py published (app/latest)")
    ap.add_argument("--now", default=None, help="aware ISO timestamp; defaults to the v1 manifest's generated_at")
    args = ap.parse_args(argv)
    try:
        result = export_explorer(args.out, reports_dir=args.reports_dir, market_data_root=args.market_data_root,
                                 now=args.now)
    except Exception as exc:  # noqa: BLE001 -- any failure leaves the previous explorer tree untouched
        traceback.print_exc()
        print(f"RESEARCH EXPORT FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("explorer/ left as it was", file=sys.stderr)
        return 1
    index = result["index"]
    sizes = R.tree_bytes(Path(args.out))
    counts = " ".join(f"{k}={v}" for k, v in index["counts"].items())
    print(f"explorer published to {args.out}/explorer: run {index['run_id']} {counts} "
          f"(capture files read {result['quote_files']}); bytes " + " ".join(f"{k}={v}" for k, v in sizes.items()))
    for w in result["warnings"]:
        print(f"warning: {w}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(f"\n### Edge Finder research explorer\n\n`app/latest/explorer` run `{index['run_id']}` -- "
                     + ", ".join(f"{k} {v}" for k, v in index["counts"].items())
                     + f"; {sum(sizes.values())} bytes\n\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
