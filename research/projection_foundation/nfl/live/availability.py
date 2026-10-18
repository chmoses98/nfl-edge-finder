"""Point-in-time availability capture for the NFL live shadow (module 2 of the live integration).

Emits `pf_core.availability.Observation`s (sift.availability.v1) for every skill-position player (QB/RB/WR/TE/FB) of every
team playing in an upcoming game, from sources the repo already captures or downloads. Every observation carries OUR
capture time (`captured_utc`), the source's own update time when it states one, the event id (nflverse game_id), the
event start, the gsis id, name and team.

Sources and certainty (never upgraded):
  espn_injuries      ESPN league injuries endpoint (relays the official Wed/Thu/Fri practice + game-status reports and
                     game-day updates; the feed's own provenance is RotoWire "basic/manual").   kind injury, REPORTED
  sleeper_players    Sleeper /players/nfl `injury_status` (same official designations, third-party relay). kind injury, REPORTED
  nflverse_injuries  nflverse `injuries_<season>` (final game designation + practice status). No row timestamp: it is
                     stamped with OUR download time, so it can only be read for games that start after that download.
                     kind injury, REPORTED (game designation); practice-only rows are kept as UNKNOWN (provenance only).
  nflverse_depth     nflverse ESPN depth-chart snapshots (`dt` = source time). kind depth (QB1 -> kind starter),
                     PROJECTED. The newest snapshot at or before the capture is used.
  nflverse_roster    nflverse weekly roster `status`: INA is the official game-day inactive list. kind roster, CONFIRMED,
                     and only when the file is for a game that has not started at download time AND the team's list is
                     visibly posted (>= 3 INA rows). ACT rows of such a team -> CONFIRMED active. RES -> OUT, REPORTED.

Not used (measured, see docs/research/NFL_PIT_AVAILABILITY_CERTIFICATION.md and the live README): the ESPN per-event roster
`active` flag (all False before the game: 57/57 entries at T-60 min in the recorded TNF payload) and the ESPN summary
`inactives` block (never present). So CONFIRMED observations exist only if nflverse refreshes the roster between the
~T-90 min inactive list and kickoff; otherwise the strongest pregame evidence is REPORTED (injury designations) and
PROJECTED (depth chart). The report says so; coverage and freshness are measured per run.

Missing availability for a player => UNVERIFIED (gate REVIEW, labelled conditional on playing). Never assumed active.
"""
from __future__ import annotations

import gzip
import json
import os
import re
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable

import pandas as pd

from pf_core import availability as av

from nfl import data as D
from nfl.live import SPORT

UA = "nfl-edge-finder projection-foundation live capture (read-only research; github.com/chmoses98/nfl-edge-finder)"
ESPN_INJURIES_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries"
SLEEPER_URL = "https://api.sleeper.app/v1/players/nfl"
NFLVERSE_BASE = "https://github.com/nflverse/nflverse-data/releases/download"
SKILL = ("QB", "RB", "WR", "TE", "FB")

ESPN_STATUS = {"Out": "OUT", "Doubtful": "DOUBTFUL", "Questionable": "QUESTIONABLE", "Day-To-Day": "QUESTIONABLE",
               "Injured Reserve": "OUT", "Physically Unable to Perform": "OUT", "Suspension": "OUT",
               "Reserve/COVID-19": "OUT", "Non-Football Injury Reserve": "OUT", "Active": "ACTIVE", "Probable": "PROBABLE"}
SLEEPER_STATUS = {"Out": "OUT", "Doubtful": "DOUBTFUL", "Questionable": "QUESTIONABLE", "IR": "OUT", "PUP": "OUT",
                  "Sus": "OUT", "COV": "OUT"}
NFLVERSE_STATUS = {"Out": "OUT", "Doubtful": "DOUBTFUL", "Questionable": "QUESTIONABLE"}
SEVERITY = {"OUT": 5, "INACTIVE": 5, "DOUBTFUL": 4, "QUESTIONABLE": 3, "LIMITED": 2, "PROBABLE": 1, "ACTIVE": 0}
MERGE_WINDOW = timedelta(hours=3)        # injury sources captured within this window of the newest one are merged by severity


# --------------------------------------------------------------------------------------------- generic helpers
def _ts(x):
    return av._ts(x)


def _iso(x) -> str | None:
    d = _ts(x) if not isinstance(x, datetime) else x
    return None if d is None else av.iso(d)


def fetch(url: str, timeout: int = 90, retries: int = 3) -> tuple[bytes | None, dict]:
    """GET with our own capture timestamps; never raises (a failed fetch is recorded, not hidden)."""
    import time
    meta: dict[str, Any] = {"url": url}
    for attempt in range(retries):
        t0 = datetime.now(timezone.utc)
        meta["requested_at"] = t0.isoformat()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            meta.update(status=200, bytes=len(body), retrieved_at=datetime.now(timezone.utc).isoformat())
            meta.pop("error", None)
            return body, meta
        except urllib.error.HTTPError as e:
            meta.update(status=e.code, error=str(e)[:200])
        except Exception as e:  # noqa: BLE001
            meta.update(status=None, error=f"{type(e).__name__}: {str(e)[:200]}")
        time.sleep(2 ** attempt)
    return None, meta


def manifest_row(path_rel: str, root: str = D.ROOT) -> dict | None:
    """Last download-manifest row (our retrieval time, release Last-Modified) of an nflverse file."""
    p = os.path.join(D.RAW, "_manifest.jsonl")
    best = None
    if os.path.exists(p):
        for line in open(p):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("path") == path_rel:
                best = r
    return best


def _last_modified_iso(row: dict | None) -> str | None:
    if not row or not row.get("last_modified"):
        return None
    try:
        from email.utils import parsedate_to_datetime
        return _iso(parsedate_to_datetime(row["last_modified"]))
    except Exception:  # noqa: BLE001
        return None


def upcoming_events(sched: pd.DataFrame, now_utc: str, horizon_hours: float = 120.0) -> list[dict]:
    """Games that have not started at `now` and start within the horizon (event id = nflverse game_id)."""
    now = _ts(now_utc)
    out = []
    for _, g in sched.iterrows():
        ko = g.kickoff_utc
        if pd.isna(ko):
            continue
        ko = ko.to_pydatetime()
        if ko <= now or ko > now + timedelta(hours=horizon_hours):
            continue
        out.append({"event_id": g.game_id, "start_utc": av.iso(ko), "home": g.home_team, "away": g.away_team,
                    "season": int(g.season), "week": int(g.week)})
    return out


def _team_events(events: list[dict]) -> dict[str, dict]:
    m = {}
    for e in events:
        m[e["home"]] = e
        m[e["away"]] = e
    return m


class IdMaps:
    """espn_id / sleeper_id -> gsis, gsis -> (name, position); built from the nflverse players table and weekly roster
    (already downloaded by the workflow). Sleeper's own gsis_id is mostly null, so its player_id is mapped through the
    weekly roster's sleeper_id (168/182 injured skill players in the recorded payload) and, failing that, its espn_id."""

    def __init__(self, players: pd.DataFrame | None = None, roster: pd.DataFrame | None = None, season: int | None = None):
        if players is None:
            p = os.path.join(D.RAW, "players", "players.parquet")
            players = pd.read_parquet(p, columns=["gsis_id", "espn_id", "display_name", "position"]) if os.path.exists(p) else \
                pd.DataFrame(columns=["gsis_id", "espn_id", "display_name", "position"])
        if roster is None:
            seasons = [season] if season else list(range(2026, 2011, -1))[:3]
            frames = []
            for s_ in seasons:
                p = os.path.join(D.RAW, "weekly_rosters", f"roster_weekly_{s_}.parquet")
                if os.path.exists(p):
                    frames.append(pd.read_parquet(p, columns=["gsis_id", "sleeper_id", "espn_id"]))
            roster = pd.concat(frames) if frames else pd.DataFrame(columns=["gsis_id", "sleeper_id", "espn_id"])
        pl = players.dropna(subset=["gsis_id"])
        self.espn_to_gsis = {str(int(e)): g for e, g in zip(pl.espn_id, pl.gsis_id) if pd.notna(e)}
        ro = roster.dropna(subset=["gsis_id"])
        self.sleeper_to_gsis = {str(int(s_)) if isinstance(s_, float) else str(s_): g
                                for s_, g in zip(ro.sleeper_id, ro.gsis_id) if pd.notna(s_)}
        for e, g in zip(ro.espn_id, ro.gsis_id):
            if pd.notna(e):
                self.espn_to_gsis.setdefault(str(int(e)), g)
        self.name = dict(zip(pl.gsis_id, pl.display_name))
        self.pos = dict(zip(pl.gsis_id, pl.position))

    def sleeper_gsis(self, p: dict) -> str | None:
        return (self.sleeper_to_gsis.get(str(p.get("player_id"))) or clean_gsis(p.get("gsis_id")) or
                (self.espn_to_gsis.get(str(p.get("espn_id"))) if p.get("espn_id") else None))


def fix_team(t):
    return D.TEAM_FIX.get(t, t)


def clean_gsis(x) -> str | None:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    return s if re.fullmatch(r"00-\d{7}", s) else None


def _obs(ev: dict, team: str, gsis: str, name: str, kind: str, status: str, certainty: str, source: str, captured: str,
         updated: str | None, url: str | None, detail: dict) -> av.Observation:
    su = _iso(updated) if updated else None
    if su and _ts(su) > _ts(captured):        # a source cannot have updated after we fetched it: keep our clock, drop theirs
        detail = {**detail, "source_updated_after_capture": su}
        su = None
    return av.Observation(sport=SPORT, event_id=ev["event_id"], event_start_utc=ev["start_utc"], entity_id=gsis,
                          entity_name=name or "", team=team, kind=kind, status=status, certainty=certainty, source=source,
                          captured_utc=captured, source_updated_utc=su, source_url=url, detail=detail)


# --------------------------------------------------------------------------------------------- parsers (pure)
def espn_injury_observations(payload: dict, meta: dict, events: list[dict], ids: IdMaps) -> tuple[list[av.Observation], dict]:
    """ESPN site injuries endpoint -> injury observations. Athlete id comes from the player-card link (100% present in
    the recorded payload); gsis via the nflverse players table."""
    tev = _team_events(events)
    cap = _iso(meta["retrieved_at"])
    rx = re.compile(r"/id/(\d+)")
    obs, st = [], Counter()
    for tm in payload.get("injuries") or []:
        for it in tm.get("injuries") or []:
            a = it.get("athlete") or {}
            team_abbr = fix_team((a.get("team") or {}).get("abbreviation"))
            ev = tev.get(team_abbr)
            pos = (a.get("position") or {}).get("abbreviation")
            if ev is None or pos not in SKILL:
                continue
            eid = None
            for l in a.get("links") or []:
                m = rx.search(l.get("href", ""))
                if m:
                    eid = m.group(1)
                    break
            gsis = ids.espn_to_gsis.get(eid) if eid else None
            if not gsis:
                st["unmapped_id"] += 1
                continue
            raw = it.get("status")
            status = ESPN_STATUS.get(raw, "UNKNOWN")
            det = it.get("details") or {}
            obs.append(_obs(ev, team_abbr, gsis, a.get("displayName"), "injury", status, "REPORTED", "espn_injuries", cap,
                            it.get("date"), meta.get("url", ESPN_INJURIES_URL),
                            {"raw_status": raw, "injury": det.get("type"), "location": det.get("location"),
                             "return_date": det.get("returnDate"), "espn_id": eid, "position": pos}))
            st[status] += 1
    return obs, dict(st)


def sleeper_observations(players: dict, meta: dict, events: list[dict], ids: "IdMaps") -> tuple[list[av.Observation], dict]:
    """Sleeper /players/nfl: injury_status for skill players of upcoming teams (absence of a status is not evidence)."""
    tev = _team_events(events)
    cap = _iso(meta["retrieved_at"])
    obs, st = [], Counter()
    for p in players.values():
        if not isinstance(p, dict):
            continue
        team = fix_team(p.get("team"))
        ev = tev.get(team)
        if ev is None or p.get("position") not in SKILL or not p.get("injury_status"):
            continue
        gsis = ids.sleeper_gsis(p)
        if not gsis:
            st["unmapped_id"] += 1
            continue
        status = SLEEPER_STATUS.get(p["injury_status"], "UNKNOWN")
        obs.append(_obs(ev, team, gsis, p.get("full_name"), "injury", status, "REPORTED", "sleeper_players", cap, None,
                        meta.get("url", SLEEPER_URL),
                        {"raw_status": p["injury_status"], "body_part": p.get("injury_body_part"),
                         "practice": p.get("practice_participation"), "position": p.get("position")}))
        st[status] += 1
    return obs, dict(st)


def nflverse_injury_observations(df: pd.DataFrame, meta: dict, events: list[dict]) -> tuple[list[av.Observation], dict]:
    """nflverse injuries file: game designation (REPORTED) or practice-only (UNKNOWN, provenance). `meta` = our download."""
    tev = _team_events(events)
    cap = _iso(meta["retrieved_at"])
    obs, st = [], Counter()
    d = df[df.game_type == "REG"].copy()
    d["team"] = D._fix(d["team"])
    for _, r in d.iterrows():
        ev = tev.get(r.team)
        if ev is None or r.week != ev["week"] or r.season != ev["season"] or r.position not in SKILL or not clean_gsis(r.gsis_id):
            continue
        if isinstance(r.report_status, str) and r.report_status in NFLVERSE_STATUS:
            status = NFLVERSE_STATUS[r.report_status]
        else:
            status = "UNKNOWN"
        obs.append(_obs(ev, r.team, r.gsis_id, r.full_name, "injury", status, "REPORTED", "nflverse_injuries", cap,
                        meta.get("last_modified_iso"), meta.get("url"),
                        {"report_status": None if pd.isna(r.report_status) else r.report_status,
                         "practice_status": None if pd.isna(r.practice_status) else r.practice_status,
                         "injury": None if pd.isna(r.report_primary_injury) else r.report_primary_injury,
                         "position": r.position}))
        st[status] += 1
    return obs, dict(st)


def nflverse_depth_observations(df: pd.DataFrame, meta: dict, events: list[dict]) -> tuple[list[av.Observation], dict]:
    """Newest depth-chart snapshot (dt) at or before our capture. QB rank 1 -> kind starter; others kind depth."""
    tev = _team_events(events)
    cap = _iso(meta["retrieved_at"])
    cap_dt = _ts(cap)
    d = df[df.pos_abb.isin(SKILL)].copy()
    d["team"] = D._fix(d["team"])
    d = d[d.team.isin(tev)]
    d["_dt"] = pd.to_datetime(d["dt"], utc=True, errors="coerce")
    d = d[d._dt.notna() & (d._dt <= pd.Timestamp(cap_dt))]
    st: Counter = Counter()
    obs = []
    if d.empty:
        return obs, {"snapshots": 0}
    snap = d.groupby("team")._dt.transform("max")
    d = d[d._dt == snap]                                    # newest snapshot per team
    # a player can sit in several formation groups: keep his best (lowest) rank
    d = d.sort_values("pos_rank").drop_duplicates(["team", "gsis_id"], keep="first")
    for _, r in d.iterrows():
        g = clean_gsis(r.gsis_id)
        if not g:
            st["no_gsis"] += 1
            continue
        ev = tev[r.team]
        rank = int(r.pos_rank)
        kind = "starter" if (r.pos_abb == "QB" and rank == 1) else "depth"
        status = "STARTING" if rank == 1 else "BENCH"
        obs.append(_obs(ev, r.team, g, r.player_name, kind, status, "PROJECTED", "nflverse_depth", cap, r["_dt"].isoformat(),
                        meta.get("url"), {"slot": r.pos_abb, "rank": rank, "group": r.pos_grp, "position": r.pos_abb}))
        st[kind + ":" + status] += 1
    st["snapshots"] = int(d.groupby("team")._dt.first().nunique())
    return obs, dict(st)


def nflverse_roster_observations(df: pd.DataFrame, meta: dict, events: list[dict]) -> tuple[list[av.Observation], dict]:
    """nflverse weekly roster: INA = official inactive list (CONFIRMED) once a team's list is visibly posted."""
    tev = _team_events(events)
    cap = _iso(meta["retrieved_at"])
    d = df[df.game_type == "REG"].copy()
    d["team"] = D._fix(d["team"])
    obs, st = [], Counter()
    for team, ev in tev.items():
        t = d[(d.team == team) & (d.week == ev["week"]) & (d.season == ev["season"])]
        n_ina = int((t.status == "INA").sum())
        posted = n_ina >= 3
        st[f"list_posted:{posted}"] += 1
        for _, r in t[t.position.isin(SKILL) & t.gsis_id.notna()].iterrows():
            g = clean_gsis(r.gsis_id)
            if not g:
                continue
            if r.status == "INA" and posted:
                obs.append(_obs(ev, team, g, r.full_name, "roster", "INACTIVE", "CONFIRMED", "nflverse_roster", cap,
                                meta.get("last_modified_iso"), meta.get("url"), {"roster_status": "INA", "team_ina": n_ina}))
                st["INACTIVE"] += 1
            elif r.status == "ACT" and posted:
                obs.append(_obs(ev, team, g, r.full_name, "roster", "ACTIVE", "CONFIRMED", "nflverse_roster", cap,
                                meta.get("last_modified_iso"), meta.get("url"), {"roster_status": "ACT", "team_ina": n_ina}))
                st["ACTIVE"] += 1
            elif r.status in ("RES", "CUT", "TRD", "RET", "EXE"):
                obs.append(_obs(ev, team, g, r.full_name, "roster", "OUT", "REPORTED", "nflverse_roster", cap,
                                meta.get("last_modified_iso"), meta.get("url"), {"roster_status": r.status}))
                st["OUT"] += 1
    return obs, dict(st)


# --------------------------------------------------------------------------------------------- capture orchestration
def _nflverse_meta(release: str, fn: str) -> dict:
    rel = os.path.join("data", "raw", "nflverse", release, fn)
    row = manifest_row(rel) or {}
    return {"url": row.get("url") or f"{NFLVERSE_BASE}/{release}/{fn}", "retrieved_at": row.get("retrieved_at"),
            "last_modified_iso": _last_modified_iso(row), "path": rel, "known": bool(row)}


def capture(now_utc: str, events: list[dict], archive: str, *, fetcher: Callable = fetch, offline: dict | None = None,
            dry_run: bool = False, nflverse_dir: str | None = None, replay_depth_as_of_now: bool = False) -> dict:
    """One capture: fetch/read every source, build observations for the upcoming events, write ONE write-once snapshot.

    offline: {"espn": (payload_dict, meta), "sleeper": (payload_dict, meta)} replaces the network fetches (tests/replay with
    recorded payloads). nflverse files are read from data/raw/nflverse (downloaded by scripts/data/nflverse_download.py)."""
    summ: dict[str, Any] = {"captured_for_utc": now_utc, "events": len(events), "sources": {}}
    if not events:
        summ["note"] = "no upcoming games in the horizon"
        return summ
    ids = IdMaps(season=max(e["season"] for e in events))
    all_obs: list[av.Observation] = []
    season = max(e["season"] for e in events)

    def run_src(name, fn):
        try:
            o, st = fn()
            all_obs.extend(o)
            summ["sources"][name] = {"state": "CAPTURED" if o else "EMPTY", "observations": len(o), **{"by": st}}
        except Exception as e:  # noqa: BLE001 - one broken source must not hide the others; it is reported and fails coverage
            summ["sources"][name] = {"state": "FAILED", "error": f"{type(e).__name__}: {str(e)[:200]}"}

    # --- network sources
    def espn():
        if offline and "espn" in offline:
            payload, meta = offline["espn"]
        else:
            body, meta = fetcher(ESPN_INJURIES_URL)
            summ["sources"].setdefault("espn_fetch", {}).update({k: meta.get(k) for k in ("status", "bytes", "retrieved_at", "error")})
            if body is None:
                raise RuntimeError(f"ESPN injuries fetch failed: {meta.get('status')} {meta.get('error')}")
            payload = json.loads(body)
        return espn_injury_observations(payload, meta, events, ids)

    def sleeper():
        if offline and "sleeper" in offline:
            payload, meta = offline["sleeper"]
        else:
            body, meta = fetcher(SLEEPER_URL, timeout=150)
            summ["sources"].setdefault("sleeper_fetch", {}).update({k: meta.get(k) for k in ("status", "bytes", "retrieved_at", "error")})
            if body is None:
                raise RuntimeError(f"Sleeper fetch failed: {meta.get('status')} {meta.get('error')}")
            payload = json.loads(body)
        return sleeper_observations(payload, meta, events, ids)

    run_src("espn_injuries", espn)
    run_src("sleeper_players", sleeper)

    # --- nflverse files (stamped with the time WE downloaded them)
    def _read(release, fn):
        meta = _nflverse_meta(release, fn)
        if not meta["known"] or not meta["retrieved_at"]:
            raise FileNotFoundError(f"{meta['path']} has no download-manifest row (not downloaded in this run?)")
        base = nflverse_dir or D.RAW
        return pd.read_parquet(os.path.join(base, release, fn)), meta

    run_src("nflverse_injuries", lambda: nflverse_injury_observations(*_read("injuries", f"injuries_{season}.parquet"), events))
    def depth():
        df, meta = _read("depth_charts", f"depth_charts_{season}.parquet")
        if replay_depth_as_of_now:
            # REPLAY ONLY: the depth-chart file carries a row-level `dt` (certified point-in-time), so a replay may read today's
            # file as if downloaded at the replay clock: rows with dt after the clock are dropped by the parser.
            meta = {**meta, "retrieved_at": now_utc, "replay_substitution": True}
        return nflverse_depth_observations(df, meta, events)

    run_src("nflverse_depth", depth)
    run_src("nflverse_roster", lambda: nflverse_roster_observations(*_read("weekly_rosters", f"roster_weekly_{season}.parquet"), events))

    # an observation cannot have been captured after "now" (replay runs read nflverse files that were downloaded later): drop it
    late = [o for o in all_obs if _ts(o.captured_utc) > _ts(now_utc)]
    if late:
        summ["dropped_captured_after_now"] = len(late)
        all_obs = [o for o in all_obs if _ts(o.captured_utc) <= _ts(now_utc)]
    summ["observations"] = len(all_obs)
    summ["by_source"] = dict(Counter(o.source for o in all_obs))
    summ["by_certainty"] = dict(Counter(o.certainty for o in all_obs))
    if dry_run:
        summ["snapshot"] = {"written": 0, "dry_run": True}
    else:
        summ["snapshot"] = av.write_snapshot(all_obs, archive, SPORT, now_utc)
    summ["_observations"] = all_obs
    return summ


# --------------------------------------------------------------------------------------------- as-of resolution (merge rule)
def merged_asof(rows: list[dict], cutoff_utc: str) -> dict[tuple, dict]:
    """pf_core `asof` (latest per event/entity/kind before min(cutoff, start)), except that the injury kind merges sources:
    each source's latest observation is kept; among those captured within MERGE_WINDOW of the newest, the most severe
    status wins (ties -> newest), so one source's stale 'Questionable' cannot hide another's fresh 'Out' and a fresh
    'Active' from the newest source is not hidden by an older 'Questionable'. UNKNOWN-status injury rows (practice-only)
    never override a real designation."""
    base = av.asof(rows, cutoff_utc)
    cut = _ts(cutoff_utc)
    per_src: dict[tuple, dict[str, dict]] = {}
    for r in rows:
        if r.get("kind") != "injury":
            continue
        cap, start = _ts(r.get("captured_utc")), _ts(r.get("event_start_utc"))
        if cap is None or cut is None or cap >= cut or (start is not None and cap >= start):
            continue
        k = (r["event_id"], r["entity_id"])
        cur = per_src.setdefault(k, {}).get(r["source"])
        if cur is None or _ts(cur["captured_utc"]) < cap:
            per_src[k][r["source"]] = r
    for k, srcs in per_src.items():
        real = [r for r in srcs.values() if r["status"] != "UNKNOWN"]
        pool = real or list(srcs.values())
        newest = max(pool, key=lambda r: _ts(r["captured_utc"]))
        near = [r for r in pool if _ts(newest["captured_utc"]) - _ts(r["captured_utc"]) <= MERGE_WINDOW]
        chosen = max(near, key=lambda r: (SEVERITY.get(r["status"], -1), r["captured_utc"]))
        if chosen is not newest:
            chosen = {**chosen, "detail": {**chosen.get("detail", {}), "merged_sources": sorted(srcs)}}
        base[(k[0], k[1], "injury")] = chosen
    return base


def resolve(rows: list[dict], cutoff_utc: str, event_id: str, entity_id: str, latest: dict | None = None) -> av.Participation:
    latest = latest if latest is not None else merged_asof(rows, cutoff_utc)
    return av.resolve_participation(latest, event_id, entity_id, cutoff_utc)


def depth_qb1(latest: dict[tuple, dict]) -> dict[tuple, str]:
    """(event_id, team) -> gsis of the PROJECTED starting QB (depth chart QB1)."""
    out = {}
    for (ev, ent, kind), r in latest.items():
        if kind == "starter" and r["status"] == "STARTING":
            out[(ev, r["team"])] = ent
    return out


def injury_table(latest: dict[tuple, dict], season: int, week: int) -> pd.DataFrame:
    """The forward week's designations from AS-OF observations, in the shape of `data.injuries()` (Out/Doubtful/
    Questionable) - replaces the nflverse final-report rows for that week (which carry no timestamp)."""
    rows = []
    for (ev, ent, kind), r in latest.items():
        if kind == "injury":
            m = {"OUT": "Out", "DOUBTFUL": "Doubtful", "QUESTIONABLE": "Questionable"}.get(r["status"])
        elif kind == "roster" and r["status"] == "INACTIVE" and r["certainty"] == "CONFIRMED":
            m = "Out"
        else:
            continue
        if m:
            rows.append({"season": season, "game_type": "REG", "team": r["team"], "week": week, "gsis_id": ent,
                         "report_status": m, "practice_status": None})
    return pd.DataFrame(rows, columns=["season", "game_type", "team", "week", "gsis_id", "report_status", "practice_status"])


def coverage(rows: list[dict], expected: dict[str, list[str]], events: list[dict], now_utc: str) -> dict:
    """pf_core coverage per event at min(now, start); plus per-source and per-certainty shares of the expected entities."""
    cut = {e["event_id"]: min(_ts(now_utc), _ts(e["start_utc"])).strftime("%Y-%m-%dT%H:%M:%SZ") for e in events}
    cov = av.coverage(rows, {k: v for k, v in expected.items() if k in cut}, cut, now_utc)
    lat = {ev: merged_asof(rows, cut[ev]) for ev in expected if ev in cut}
    by_status: Counter = Counter()
    by_cert: Counter = Counter()
    for ev, ents in expected.items():
        for e in ents:
            p = resolve(rows, cut[ev], ev, e, lat[ev]) if ev in lat else None
            if p:
                by_status[p.status] += 1
                by_cert[p.certainty] += 1
    cov["participation_status"] = dict(by_status)
    cov["participation_certainty"] = dict(by_cert)
    return cov


def load_rows(archive: str, now_utc: str, days: int = 9) -> list[dict]:
    now = _ts(now_utc)
    dates = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days + 1)]
    return av.load_snapshots(archive, SPORT, dates)
