"""Prospective, append-only capture of NFL availability sources, each stamped with OUR retrieval time.

One run writes (write-once; manifest hash chain, see store.py) under data/pit_availability/nfl/:

    nflverse_injuries/<season>/<run>.<sha16>.parquet + <run>.capture.json
        the nflverse injuries file, stored only when its content is new to the store (content-addressed), with
        retrieved_at / url / last-modified. This is what makes 2026+ injury rows point-in-time: the file has no
        row-level time and nflverse rebuilds it in place (post-kickoff edits measured in the certification).
    nflverse_depth_charts/<season>/<run>.capture.json
        a digest of the depth-chart file: rows and sha256 per `dt` snapshot. A later capture whose digest for an
        OLD snapshot differs proves a historical snapshot was rewritten (the `dt` certification depends on it not
        being rewritten). The rows themselves stay recoverable from nflverse by `dt`.
    espn_injuries/<day>/<run>.json.gz
        the ESPN league injuries endpoint, raw, with retrieved_at (Wed/Thu/Fri practice reports, Saturday final
        statuses, game-day updates).
    espn_event_rosters/<day>/<run>.json.gz
        for games within [T-240m, T+30m]: the ESPN per-event roster of each team, reduced to athlete id, `active`
        and `didNotPlay` flags, with retrieved_at and minutes to kickoff. Evidence for (or against) an official
        ~T-90m inactive list; it is NOT certified and nothing reads it as availability.

Research only: nothing here feeds a gate, a model or a production surface.
"""
from __future__ import annotations

import gzip
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

import polars as pl

from nfl_edge.availability_pit import PIT_VERSION, store

UA = "nfl-edge-finder pit-availability capture (read-only research; github.com/chmoses98/nfl-edge-finder)"
ESPN_INJURIES = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries"
SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
CORE = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
NV = os.path.join("data", "raw", "nflverse")
ROSTER_WINDOW = (-240.0, 30.0)          # minutes relative to kickoff (negative = before)


def _get(url, timeout=45, opener=None):
    t0 = datetime.now(timezone.utc)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with (opener or urllib.request.urlopen)(req, timeout=timeout) as r:
            body = r.read()
        return body, {"status": 200, "bytes": len(body), "requested_at": t0.isoformat(),
                      "retrieved_at": datetime.now(timezone.utc).isoformat(), "url": url}
    except urllib.error.HTTPError as e:
        return None, {"status": e.code, "error": str(e)[:200], "requested_at": t0.isoformat(), "url": url}
    except Exception as e:                                  # noqa: BLE001 -- a capture records failure, never raises
        return None, {"status": None, "error": f"{type(e).__name__}: {str(e)[:200]}", "requested_at": t0.isoformat(), "url": url}


def _manifest_row(root, rel):
    p = os.path.join(root, NV, "_manifest.jsonl")
    best = None
    if os.path.exists(p):
        for line in open(p):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("path") == rel:
                best = r
    return best


def known_shas(store_root, sub):
    out = set()
    for dp, _d, fs in os.walk(os.path.join(store_root, sub)):
        for f in fs:
            if f.endswith(".capture.json"):
                r = json.load(open(os.path.join(dp, f)))
                for k in ("sha256", "sha256_file"):
                    if r.get(k):
                        out.add(r[k])
    return out


def capture_nflverse_injuries(w: store.RunWriter, root, store_root, season, run_id) -> dict:
    rel = f"data/raw/nflverse/injuries/injuries_{season}.parquet"
    src = os.path.join(root, rel)
    meta = _manifest_row(root, rel)
    if not os.path.exists(src) or not meta:
        return {"state": "ABSENT"}
    sha = store.sha256_file(src)
    if meta.get("sha256") and meta["sha256"] != sha:
        return {"state": "REFUSED_HASH_MISMATCH"}
    if sha in known_shas(store_root, f"nflverse_injuries/{season}"):
        return {"state": "UNCHANGED", "sha256": sha, "retrieved_at": meta.get("retrieved_at")}
    fname = f"{run_id}.{sha[:16]}.parquet"
    w.write(f"nflverse_injuries/{season}/{fname}", open(src, "rb").read())
    d = pl.read_parquet(src)
    rec = {"file": fname, "sha256": sha, "retrieved_at": meta["retrieved_at"], "url": meta.get("url"),
           "last_modified": meta.get("last_modified"), "rows": d.height,
           "rows_by_week": {str(k): v for k, v in d.group_by("week").len().sort("week").iter_rows()}, "pit_version": PIT_VERSION}
    w.write_json(f"nflverse_injuries/{season}/{run_id}.capture.json", rec)
    return {"state": "NEW_CONTENT", **{k: rec[k] for k in ("sha256", "retrieved_at", "rows")}}


def capture_depth_digest(w: store.RunWriter, root, store_root, season, run_id) -> dict:
    rel = f"data/raw/nflverse/depth_charts/depth_charts_{season}.parquet"
    src = os.path.join(root, rel)
    meta = _manifest_row(root, rel)
    if not os.path.exists(src) or not meta:
        return {"state": "ABSENT"}
    if store.sha256_file(src) in known_shas(store_root, f"nflverse_depth_charts/{season}"):
        return {"state": "UNCHANGED"}
    d = pl.read_parquet(src)
    if "dt" not in d.columns:
        return {"state": "NO_DT_COLUMN"}
    import hashlib
    digest = {}
    for (dt,), part in sorted(d.sort(["dt", "team", "pos_grp", "pos_slot", "pos_rank", "gsis_id"], nulls_last=True)
                              .partition_by("dt", as_dict=True).items()):
        h = hashlib.sha256(part.drop("dt").write_csv().encode()).hexdigest()
        digest[dt] = {"rows": part.height, "sha256": h}
    rec = {"sha256_file": store.sha256_file(src), "retrieved_at": meta["retrieved_at"], "url": meta.get("url"),
           "last_modified": meta.get("last_modified"), "rows": d.height, "snapshots": len(digest), "per_dt": digest}
    w.write_json(f"nflverse_depth_charts/{season}/{run_id}.capture.json", rec)
    return {"state": "DIGESTED", "snapshots": len(digest), "rows": d.height}


def capture_espn_injuries(w: store.RunWriter, day, run_id, opener=None) -> dict:
    body, meta = _get(ESPN_INJURIES, opener=opener)
    if body is None:
        return {"state": "FETCH_FAILED", **meta}
    try:
        j = json.loads(body)
    except ValueError:
        return {"state": "NOT_JSON", **meta}
    rec = {"meta": meta, "payload": j}
    w.write(f"espn_injuries/{day}/{run_id}.json.gz", gzip.compress(json.dumps(rec, sort_keys=True).encode(), mtime=0))
    n = sum(len(t.get("injuries") or []) for t in (j.get("injuries") or []))
    return {"state": "CAPTURED", "teams": len(j.get("injuries") or []), "rows": n, "retrieved_at": meta["retrieved_at"]}


def capture_event_rosters(w: store.RunWriter, day, run_id, now=None, opener=None) -> dict:
    now = now or datetime.now(timezone.utc)
    body, meta = _get(SCOREBOARD, opener=opener)
    if body is None:
        return {"state": "SCOREBOARD_FAILED", **meta}
    events = []
    for ev in (json.loads(body).get("events") or []):
        try:
            ko = datetime.fromisoformat(str(ev.get("date")).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            continue
        mins = (now - ko).total_seconds() / 60.0
        if not ROSTER_WINDOW[0] <= mins <= ROSTER_WINDOW[1]:
            continue
        comp = (ev.get("competitions") or [{}])[0]
        rec = {"event_id": ev.get("id"), "name": ev.get("shortName"), "kickoff_utc": ko.isoformat(),
               "minutes_to_kickoff": round(-mins, 1), "teams": []}
        for c in comp.get("competitors") or []:
            tid = c.get("id")
            url = f"{CORE}/events/{ev.get('id')}/competitions/{ev.get('id')}/competitors/{tid}/roster"
            rb, rm = _get(url, opener=opener)
            team = {"team_id": tid, "abbr": (c.get("team") or {}).get("abbreviation"), "meta": rm}
            if rb is not None:
                try:
                    entries = json.loads(rb).get("entries") or []
                except ValueError:
                    entries = []
                team["entries"] = [{"athlete_id": (e.get("playerId") or (e.get("athlete") or {}).get("$ref", "").rsplit("/", 1)[-1].split("?")[0]),
                                    "active": e.get("active"), "didNotPlay": e.get("didNotPlay"), "starter": e.get("starter")}
                                   for e in entries if isinstance(e, dict)]
                team["n_entries"] = len(team["entries"])
                team["n_active_false"] = sum(1 for e in team["entries"] if e["active"] is False)
                team["n_did_not_play_true"] = sum(1 for e in team["entries"] if e["didNotPlay"] is True)
            rec["teams"].append(team)
        events.append(rec)
    if events:
        w.write(f"espn_event_rosters/{day}/{run_id}.json.gz",
                gzip.compress(json.dumps({"scoreboard_meta": meta, "events": events}, sort_keys=True).encode(), mtime=0))
    return {"state": "CAPTURED" if events else "NO_GAMES_IN_WINDOW", "events": len(events),
            "teams": [(e["name"], e["minutes_to_kickoff"], [(t.get("abbr"), t.get("n_active_false"), t.get("n_did_not_play_true")) for t in e["teams"]])
                      for e in events]}


def run(root, store_root, *, season: int, now=None, dry_run=False, opener=None, network=True) -> dict:
    now = now or datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ"); day = now.strftime("%Y-%m-%d")
    w = store.RunWriter(store_root, run_id, meta={"mode": "pit_capture", "pit_version": PIT_VERSION, "dry_run": dry_run,
                                                  "started_at": now.isoformat()})
    out = {"run_id": run_id, "season": season,
           "nflverse_injuries": capture_nflverse_injuries(w, root, store_root, season, run_id),
           "nflverse_depth_charts": capture_depth_digest(w, root, store_root, season, run_id)}
    if network:
        out["espn_injuries"] = capture_espn_injuries(w, day, run_id, opener=opener)
        out["espn_event_rosters"] = capture_event_rosters(w, day, run_id, now=now, opener=opener)
    w.write_json(f"runs/{day}/{run_id}.summary.json", out)
    w.seal()
    return out
