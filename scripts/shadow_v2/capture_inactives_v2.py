#!/usr/bin/env python3
"""Freeze the official gameday inactive list for games about to kick off. RESEARCH ONLY.

    python3 scripts/shadow_v2/capture_inactives_v2.py --out data/shadow/v2 --window-min 150

Runs near the official publication window (about 90 minutes before kickoff) and records, per game, only the
players a source explicitly names as inactive -- with the source, its timestamp, the observation instant, and a
confidence derived from where in the window the observation fell. It can never declare anyone active: see
`nfl_edge/shadow_v2/inactives.py` for why that asymmetry is the whole design, and
`scripts/data/probe_inactives.py` for the history of why this repo refused to build a collector until it could
be built this way.

Nothing here feeds the real-money availability gate. Every row carries feeds_availability_gate=False and
betting_authorized=False.

Writes `<out>/inactives/<YYYY-MM-DD>/<run_id>.inactives.json` (one object per game) plus a manifest. A game
whose observation lands after kickoff is written as POSTGAME_OBSERVATION and contributes no player rows, so an
inactive list can never be reconstructed after the fact and presented as pregame knowledge.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.data.nfl_calendar import SCHEDULE_URL, kickoff_utc                           # noqa: E402
from nfl_edge.shadow_v2 import inactives as IN                                             # noqa: E402


def log(m):
    print(m, flush=True)


def schedule_rows(path: str | None):
    if path and os.path.exists(path):
        text = open(path).read()
    else:
        req = urllib.request.Request(SCHEDULE_URL, headers={"User-Agent": IN.UA})
        with urllib.request.urlopen(req, timeout=90) as r:
            text = r.read().decode()
    return list(csv.DictReader(io.StringIO(text)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2"))
    ap.add_argument("--schedule", default=None, help="a local games.csv (e.g. market-data's schedule_cache.csv)")
    ap.add_argument("--window-min", type=float, default=150.0, help="capture games kicking off within this many minutes")
    ap.add_argument("--season", type=int, default=None)
    ap.add_argument("--now", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    now = IN._dt(a.now) or datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    rows = schedule_rows(a.schedule)
    upcoming = []
    for r in rows:
        if a.season and str(r.get("season")) != str(a.season):
            continue
        if not r.get("espn"):
            continue
        try:
            ko = IN._dt(kickoff_utc(str(r.get("gameday")), str(r.get("gametime"))))
        except (ValueError, TypeError):
            continue
        if ko is None:
            continue
        mins = (ko - now).total_seconds() / 60.0
        if IN.WINDOW_LATE_MIN <= mins <= a.window_min:
            upcoming.append({"game_id": r.get("game_id"), "event_id": str(r.get("espn")), "kickoff_utc": ko.isoformat(),
                             "minutes_to_kickoff": round(mins, 1)})
    upcoming.sort(key=lambda g: g["minutes_to_kickoff"])
    log(f"{len(upcoming)} game(s) inside the {a.window_min:g}-minute publication window")
    day = os.path.join(a.out, "inactives", now.strftime("%Y-%m-%d"))
    os.makedirs(day, exist_ok=True)
    out, usable, confirmed = [], 0, 0
    for g in upcoming:
        body, err, meta = (None, "dry run", {"url": IN.SUMMARY_URL.format(eid=g["event_id"])}) if a.dry_run \
            else IN.fetch_summary(g["event_id"])
        rec = IN.observations(game_id=g["game_id"], event_id=g["event_id"], kickoff_utc=g["kickoff_utc"],
                              summary=body, fetch_meta=meta, observed_at=now)
        if err:
            rec["fetch_error"] = err
        out.append(rec)
        usable += 1 if rec["usable"] else 0
        confirmed += rec["n_confirmed_inactive"]
        log(f"  {g['game_id']} T-{g['minutes_to_kickoff']:.0f}m: {rec['n_confirmed_inactive']} confirmed inactive, "
            f"{rec['evidence_class']}, confidence {rec['confidence']}"
            + (f" [{err}]" if err else ""))
    manifest = {"inactives_version": IN.INACTIVES_VERSION, "run_id": run_id, "observed_at": now.isoformat(),
                "window_minutes": a.window_min, "games_in_window": len(upcoming), "games_usable": usable,
                "players_confirmed_inactive": confirmed, "dry_run": bool(a.dry_run),
                "research_only": True, "feeds_availability_gate": False, "betting_authorized": False,
                "asymmetry": "the collector can only ADD a confirmed inactive; it can never declare a player active, "
                             "so an outage yields zero rows rather than 'everyone is playing'"}
    if not a.dry_run:
        with open(os.path.join(day, f"{run_id}.inactives.json"), "w") as fh:
            json.dump({"manifest": manifest, "games": out}, fh, separators=(",", ":"), default=str)
    json.dump(manifest, open(os.path.join(day, f"{run_id}.inactives_manifest.json"), "w"), separators=(",", ":"), default=str)
    print(json.dumps(manifest, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
