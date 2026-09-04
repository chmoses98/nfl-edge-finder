#!/usr/bin/env python3
"""Download nflverse release assets into the bronze layer.

Every asset is fetched by its canonical release URL
(https://github.com/nflverse/nflverse-data/releases/download/<release>/<file>)
and written unchanged (raw parquet/csv) under data/raw/nflverse/<release>/,
with a manifest row recording url, retrieval timestamp, bytes, sha256 and
HTTP metadata.  This is a bronze/immutable layer: nothing is transformed here.

Usage: python scripts/data/nflverse_download.py [--only pbp,schedules] [--seasons 2016-2025]
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "data", "raw", "nflverse")
BASE = "https://github.com/nflverse/nflverse-data/releases/download"

# release -> list of (filename pattern, seasons or None for single file)
# Season ranges reflect what nflverse publishes (per nflreadr docs + observed 404s).
def catalog(seasons):
    return {
        "pbp": [f"play_by_play_{s}.parquet" for s in seasons],
        "schedules": ["games.csv", "games.rds"],  # games.csv is the canonical one
        "stats_player": [f"stats_player_week_{s}.parquet" for s in seasons],
        "stats_team": [f"stats_team_week_{s}.parquet" for s in seasons],
        "weekly_rosters": [f"roster_weekly_{s}.parquet" for s in seasons],
        "rosters": [f"roster_{s}.parquet" for s in seasons],
        "snap_counts": [f"snap_counts_{s}.parquet" for s in seasons if s >= 2012],
        "injuries": [f"injuries_{s}.parquet" for s in seasons if s >= 2009],
        "depth_charts": [f"depth_charts_{s}.parquet" for s in seasons if s >= 2001],
        "ftn_charting": [f"ftn_charting_{s}.parquet" for s in seasons if s >= 2022],
        "pbp_participation": [f"pbp_participation_{s}.parquet" for s in seasons if s >= 2016],
        "nextgen_stats": [f"ngs_{s}_{t}.parquet" for s in seasons if s >= 2016 for t in ("passing", "rushing", "receiving")],
        "pfr_advstats": [f"advstats_week_{t}_{s}.parquet" for s in seasons if s >= 2018 for t in ("pass", "rush", "rec", "def")],
        "espn_data": [f"qbr_week_level.parquet", "qbr_season_level.parquet"],
        "players": ["players.parquet"],
        "players_components": ["ff_playerids.parquet"],  # may not exist here; ff ids live in ffverse
        "contracts": ["historical_contracts.parquet"],
        "officials": ["officials.parquet"],
        "combine": ["combine.parquet"],
        "draft_picks": ["draft_picks.parquet"],
        "misc": ["trades.parquet"],
    }

FFVERSE = {  # different repo
    "ff_playerids": ("https://github.com/dynastyprocess/data/raw/master/files/db_playerids.parquet", "db_playerids.parquet"),
    "ff_opportunity": None,
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def fetch(url, dest, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "nfl-edge-finder/0.1 (research)"})
            with urllib.request.urlopen(req, timeout=120) as r, open(dest + ".part", "wb") as f:
                meta = {"status": r.status, "last_modified": r.headers.get("Last-Modified"), "etag": r.headers.get("ETag"), "content_length": r.headers.get("Content-Length")}
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            os.replace(dest + ".part", dest)
            return meta
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"status": 404}
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    return {"status": "failed"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--seasons", default="1999-2026")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.seasons.split("-"))
    seasons = list(range(lo, hi + 1))
    cat = catalog(seasons)
    only = set(a.only.split(",")) if a.only else set(cat)
    manifest_path = os.path.join(OUT, "_manifest.jsonl")
    os.makedirs(OUT, exist_ok=True)
    done = {}
    if os.path.exists(manifest_path):
        for line in open(manifest_path):
            row = json.loads(line)
            done[row["path"]] = row
    for release, files in cat.items():
        if release not in only:
            continue
        d = os.path.join(OUT, release)
        os.makedirs(d, exist_ok=True)
        for fn in files:
            dest = os.path.join(d, fn)
            rel = os.path.relpath(dest, ROOT)
            if rel in done and not a.force and os.path.exists(dest):
                continue
            url = f"{BASE}/{release}/{fn}"
            t0 = time.time()
            meta = fetch(url, dest)
            row = {"path": rel, "url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(), **meta}
            if os.path.exists(dest):
                row["bytes"] = os.path.getsize(dest)
                row["sha256"] = sha256(dest)
            row["seconds"] = round(time.time() - t0, 2)
            print(json.dumps(row), flush=True)
            with open(manifest_path, "a") as f:
                f.write(json.dumps(row) + "\n")
    if "ff_playerids" in only or not a.only:
        url, fn = FFVERSE["ff_playerids"]
        d = os.path.join(OUT, "ff_playerids"); os.makedirs(d, exist_ok=True)
        dest = os.path.join(d, fn)
        if not os.path.exists(dest) or a.force:
            meta = fetch(url, dest)
            row = {"path": os.path.relpath(dest, ROOT), "url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(), **meta}
            if os.path.exists(dest):
                row["bytes"] = os.path.getsize(dest); row["sha256"] = sha256(dest)
            print(json.dumps(row), flush=True)
            with open(manifest_path, "a") as f:
                f.write(json.dumps(row) + "\n")

if __name__ == "__main__":
    main()
