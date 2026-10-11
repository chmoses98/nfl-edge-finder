"""Refusing PIT loaders. Each returns (rows, report); a row lacking a provable pre-cutoff time is never returned.

The cutoff is per team-game: kickoff - lead (default 90 minutes, the PURE forecast cutoff). Callers may pass a
different lead; nothing is ever loaded at or after kickoff.

Row contract (every loader): season, week, team, game_id, kickoff, cutoff, gsis_id, <values>, observed_at, pit_basis.
Report contract: {"returned": n, "refused": {reason: n}, "by_season": {...}}.
"""
from __future__ import annotations

import glob
import json
import os
import re
import unicodedata
from collections import Counter
from datetime import timedelta

import numpy as np
import pandas as pd
import polars as pl

from nfl_edge.availability_pit import CERTIFIED_INJURY_SEASONS, DEPTH_CHART_FIRST_SEASON

NFLVERSE = os.path.join("data", "raw", "nflverse")
TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA", "ARZ": "ARI", "AZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU",
            "JAC": "JAX", "SL": "LA", "LAR": "LA", "WSH": "WAS"}
INJ_VALUES = ["report_status", "practice_status", "report_primary_injury", "position", "full_name"]
ESPN_TEAM = {"Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL", "Buffalo Bills": "BUF",
             "Carolina Panthers": "CAR", "Chicago Bears": "CHI", "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE",
             "Dallas Cowboys": "DAL", "Denver Broncos": "DEN", "Detroit Lions": "DET", "Green Bay Packers": "GB",
             "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX", "Kansas City Chiefs": "KC",
             "Las Vegas Raiders": "LV", "Los Angeles Chargers": "LAC", "Los Angeles Rams": "LA", "Miami Dolphins": "MIA",
             "Minnesota Vikings": "MIN", "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG",
             "New York Jets": "NYJ", "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT", "San Francisco 49ers": "SF",
             "Seattle Seahawks": "SEA", "Tampa Bay Buccaneers": "TB", "Tennessee Titans": "TEN", "Washington Commanders": "WAS"}


class PITRefusal(RuntimeError):
    pass


def _pd(df: pl.DataFrame) -> pd.DataFrame:
    """polars -> pandas without pyarrow (CI installs none)."""
    return pd.DataFrame(df.to_dict(as_series=False))


def _utc(x):
    return pd.to_datetime(x, utc=True, errors="coerce")


def kickoff_utc(gameday, gametime) -> pd.Series:
    from nfl_edge.engines.player.pure_v1.data import kickoff_utc as k
    return k(list(gameday), list(gametime))


def team_games(root: str) -> pd.DataFrame:
    """season, week, game_type, team, game_id, kickoff (UTC) for every team-game in the schedule."""
    g = pd.read_csv(os.path.join(root, NFLVERSE, "schedules", "games.csv"),
                    usecols=["game_id", "season", "week", "game_type", "gameday", "gametime", "home_team", "away_team"])
    g["kickoff"] = kickoff_utc(g["gameday"], g["gametime"]).to_numpy()
    t = pd.concat([g.assign(team=g["home_team"]), g.assign(team=g["away_team"])], ignore_index=True)
    t["team"] = t["team"].replace(TEAM_FIX)
    return t[["season", "week", "game_type", "team", "game_id", "kickoff"]]


def _with_cutoff(df: pd.DataFrame, tg: pd.DataFrame, lead: timedelta) -> pd.DataFrame:
    df = df.copy()
    df["team"] = df["team"].replace(TEAM_FIX)
    if "game_type" not in df.columns:
        df["game_type"] = "REG"
    m = df.merge(tg, on=["season", "week", "game_type", "team"], how="left")
    m["kickoff"] = _utc(m["kickoff"])
    m["cutoff"] = m["kickoff"] - lead
    return m


# ------------------------------------------------------------------------------------------------ injuries
def vintage_snapshots(roots, season: int) -> list[tuple[pd.Timestamp, str]]:
    """(retrieved_at, parquet path) of every distinct injuries_<season> snapshot under the given roots.

    Reads the repository's content-addressed vintage store (data/raw/nflverse/_vintages/injuries/injuries_<s>/
    index*.jsonl, see nfl_edge/shadow_v2/vintage_snapshots.py) and this module's own capture store
    (<root>/nflverse_injuries/<s>/<run>.<sha16>.parquet with the run's retrieved_at in its manifest row). The
    earliest retrieved_at per content hash is kept: re-registration never re-dates content."""
    best: dict[str, tuple[pd.Timestamp, str]] = {}
    for root in roots or ():
        if not root:
            continue
        vd = os.path.join(root, NFLVERSE, "_vintages", "injuries", f"injuries_{season}")
        for f in glob.glob(os.path.join(vd, "index*.jsonl")):
            for line in open(f):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                p = os.path.join(root, r["snapshot_path"])
                t = pd.Timestamp(r["retrieved_at"])
                if os.path.exists(p) and (r["sha256"] not in best or t < best[r["sha256"]][0]):
                    best[r["sha256"]] = (t, p)
        for f in glob.glob(os.path.join(root, "nflverse_injuries", str(season), "*.capture.json")):
            r = json.load(open(f))
            p = os.path.join(os.path.dirname(f), r["file"])
            t = pd.Timestamp(r["retrieved_at"])
            if os.path.exists(p) and (r["sha256"] not in best or t < best[r["sha256"]][0]):
                best[r["sha256"]] = (t, p)
    return sorted(best.values())


def injuries_certified(root: str, seasons, *, lead: timedelta = timedelta(minutes=90), vintage_roots=None,
                       game_type: str = "REG") -> tuple[pd.DataFrame, dict]:
    """Injury-report rows provably known before each team-game's cutoff.

    Seasons with a row-level `date_modified` (2010-2024): a row is returned iff date_modified < cutoff; it is the
    row's final weekly version (one row per player-week), so `observed_at = date_modified`.
    Other seasons: the newest vintage snapshot retrieved before the cutoff supplies that team-week's rows, with
    `observed_at = retrieved_at`. No qualifying snapshot -> every row of that team-week is refused."""
    tg = team_games(root)
    out, refused, by_season = [], Counter(), {}
    for s in seasons:
        p = os.path.join(root, NFLVERSE, "injuries", f"injuries_{s}.parquet")
        if not os.path.exists(p):
            refused["FILE_ABSENT"] += 1
            continue
        raw = _pd(pl.read_parquet(p))
        raw = raw[raw.get("game_type", game_type) == game_type] if "game_type" in raw.columns else raw
        m = _with_cutoff(raw, tg, lead)
        n0 = len(m)
        nojoin = m["kickoff"].isna()
        refused["NO_TEAM_GAME_JOIN"] += int(nojoin.sum())
        m = m[~nojoin]
        if "date_modified" in m.columns and m["date_modified"].notna().any() and s in CERTIFIED_INJURY_SEASONS:
            dm = _utc(m["date_modified"])
            ok = dm.notna() & (dm < m["cutoff"])
            refused["DATE_MODIFIED_MISSING"] += int(dm.isna().sum())
            refused["DATE_MODIFIED_AT_OR_AFTER_CUTOFF"] += int((dm.notna() & ~ok).sum())
            r = m[ok].copy()
            r["observed_at"] = dm[ok]
            r["pit_basis"] = "nflverse_row_date_modified"
        else:
            snaps = vintage_snapshots(vintage_roots, s)
            if not snaps:
                refused["NO_ROW_TIMESTAMP_AND_NO_VINTAGE"] += len(m)
                by_season[s] = {"rows_in_file": n0, "returned": 0}
                continue
            parts = []
            frames = {}
            for (wk, team), grp in m.groupby(["week", "team"]):
                cut = grp["cutoff"].iloc[0]
                prior = [x for x in snaps if x[0] < cut]
                if not prior:
                    refused["NO_VINTAGE_BEFORE_CUTOFF"] += len(grp)
                    continue
                t, path = prior[-1]
                if path not in frames:
                    v = _pd(pl.read_parquet(path))
                    v["team"] = v["team"].replace(TEAM_FIX)
                    frames[path] = v
                v = frames[path]
                v = v[(v["week"] == wk) & (v["team"] == team)]
                if "game_type" in v.columns:
                    v = v[v["game_type"] == game_type]
                v = _with_cutoff(v, tg, lead)
                v["observed_at"] = t
                v["pit_basis"] = "vintage_snapshot_retrieved_at"
                parts.append(v)
                # rows in the current file for this team-week that the vintage did not contain are post-cutoff
                refused["NOT_IN_PRE_CUTOFF_VINTAGE"] += int((~grp["gsis_id"].isin(set(v["gsis_id"]))).sum())
            r = pd.concat(parts, ignore_index=True) if parts else m.iloc[0:0].assign(observed_at=pd.NaT, pit_basis="")
        if len(r):
            r["observed_at"] = _utc(r["observed_at"])
            r = r[r["observed_at"] < _utc(r["cutoff"])]
        by_season[s] = {"rows_in_file": n0, "returned": int(len(r)), "basis": r["pit_basis"].iloc[0] if len(r) else None}
        out.append(r)
    rows = pd.concat(out, ignore_index=True) if out else pd.DataFrame()
    if len(rows):
        assert_pre_cutoff(rows)
        rows = rows[["season", "week", "team", "game_id", "kickoff", "cutoff", "gsis_id"] + [c for c in INJ_VALUES if c in rows.columns]
                    + ["observed_at", "pit_basis"]]
    return rows, {"returned": int(len(rows)), "refused": dict(refused), "by_season": by_season, "lead_minutes": lead.total_seconds() / 60}


# ------------------------------------------------------------------------------------------------ depth charts
def depth_chart_certified(root: str, season: int, *, lead: timedelta = timedelta(minutes=90)) -> tuple[pd.DataFrame, dict]:
    """For every team-game of the season: the newest `dt` snapshot of that team strictly before the cutoff."""
    if season < DEPTH_CHART_FIRST_SEASON:
        raise PITRefusal(f"depth charts before {DEPTH_CHART_FIRST_SEASON} carry no snapshot time (weekly file); refused")
    d = _pd(pl.read_parquet(os.path.join(root, NFLVERSE, "depth_charts", f"depth_charts_{season}.parquet")))
    d["dt"] = _utc(d["dt"])
    d["team"] = d["team"].replace(TEAM_FIX)
    tg = team_games(root)
    tg = tg[tg["season"] == season].copy()
    tg["kickoff"] = _utc(tg["kickoff"])
    tg["cutoff"] = tg["kickoff"] - lead
    snaps = {t: sorted(set(x)) for t, x in d.groupby("team")["dt"]}
    parts, refused = [], Counter()
    for g in tg.itertuples(index=False):
        ts = snaps.get(g.team)
        if ts is None:
            refused["TEAM_ABSENT"] += 1
            continue
        prior = [x for x in ts if x < g.cutoff]
        if not prior:
            refused["NO_SNAPSHOT_BEFORE_CUTOFF"] += 1
            continue
        t = pd.Timestamp(prior[-1])
        sub = d[(d["team"] == g.team) & (d["dt"] == t)].copy()
        sub["season"], sub["week"], sub["game_id"], sub["kickoff"], sub["cutoff"] = season, g.week, g.game_id, g.kickoff, g.cutoff
        sub["observed_at"], sub["pit_basis"] = t, "nflverse_depth_chart_dt_snapshot"
        sub["snapshot_age_h"] = (g.cutoff - t).total_seconds() / 3600
        parts.append(sub)
    rows = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if len(rows):
        assert_pre_cutoff(rows)
        refused["GSIS_ID_MISSING"] = int(rows["gsis_id"].isna().sum())
        rows = rows[rows["gsis_id"].notna()]
    return rows, {"returned": int(len(rows)), "refused": dict(refused), "team_games": int(len(tg))}


# ------------------------------------------------------------------------------------------------ ESPN captures
def _norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z ]", "", s)
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return " ".join(s.split())


def espn_injuries_captured(capture_files, roster: pd.DataFrame, team_game: pd.DataFrame, *,
                           lead: timedelta = timedelta(minutes=90)) -> tuple[pd.DataFrame, dict]:
    """ESPN injury rows from OUR captures (retrieved_at), newest capture before each team-game's cutoff.

    roster: gsis_id, full_name, team (the season's nflverse roster) for identity -- ESPN rows carry no athlete id,
    so a row is returned only if its normalised name matches exactly one rostered player of that team.
    team_game: team, game_id, kickoff for the games to load."""
    caps = []
    for f in capture_files:
        d = json.load(open(f))
        if "injuries" in d:
            caps.append((pd.Timestamp(d["retrieved_at"]), d))
    caps.sort(key=lambda x: x[0])
    ros = roster.copy()
    ros["team"] = ros["team"].replace(TEAM_FIX)
    ros["k"] = ros["full_name"].map(_norm)
    ident = ros.groupby(["team", "k"])["gsis_id"].agg(lambda x: sorted(set(x)))
    out, refused = [], Counter()
    for g in team_game.itertuples(index=False):
        cutoff = pd.Timestamp(g.kickoff) - lead
        prior = [c for c in caps if c[0] < cutoff]
        if not prior:
            refused["NO_CAPTURE_BEFORE_CUTOFF"] += 1
            continue
        t, d = prior[-1]
        for r in d["injuries"]:
            if ESPN_TEAM.get(r.get("team")) != g.team:
                continue
            rd = pd.to_datetime(r.get("date"), utc=True, errors="coerce")
            if pd.isna(rd) or not rd < cutoff:
                refused["ROW_DATE_MISSING_OR_AFTER_CUTOFF"] += 1
                continue
            ids = ident.get((g.team, _norm(r.get("name"))))
            if not ids or len(ids) != 1:
                refused["IDENTITY_UNMATCHED" if not ids else "IDENTITY_AMBIGUOUS"] += 1
                continue
            out.append({"team": g.team, "game_id": g.game_id, "kickoff": pd.Timestamp(g.kickoff), "cutoff": cutoff, "gsis_id": ids[0],
                        "name": r.get("name"), "position": r.get("position"), "status": r.get("status"), "espn_row_date": rd,
                        "injury": r.get("injury"), "observed_at": t, "pit_basis": "own_capture_retrieved_at"})
    rows = pd.DataFrame(out)
    if len(rows):
        assert_pre_cutoff(rows)
    return rows, {"returned": int(len(rows)), "refused": dict(refused), "captures": len(caps)}


def assert_pre_cutoff(rows: pd.DataFrame) -> None:
    obs, cut = _utc(rows["observed_at"]), _utc(rows["cutoff"])
    bad = obs.isna() | cut.isna() | ~(obs < cut)
    if bad.any():
        raise PITRefusal(f"{int(bad.sum())} rows lack an observed_at strictly before their cutoff")
