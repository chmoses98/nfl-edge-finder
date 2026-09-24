#!/usr/bin/env python3
"""CAPTURE HEALTH, season to date, for RUN NFL and the three-arm freeze -- split BEFORE / AFTER the conductor.

    python3 scripts/handicap/horizon_capture_health.py --run-nfl-state state.json \
        --three-arm-markers-dir /tmp/md/data/shadow/arms/horizons --out data/ops/capture_health \
        --fail-on-recent-miss-hours 48

Every owed horizon of every slate that has started is classified against the SCHEDULE, never against what
happens to have been recorded (`nfl_edge.evaluation.capture_health.horizon_delivery`):

    DELIVERED_ON_TIME / DELIVERED_LATE / DELIVERED_DEGRADED / MISSED / DUE / NOT_YET_DUE

A missed horizon writes no record by construction, so counting records would report 0 missed forever. A
capture recorded at or after kickoff is MISSED, not "very late".

WHY THE ERA SPLIT
-----------------
Weeks 1-2 were served by a */15 cron that GitHub started ~7% of the time. Those misses are real and permanent
and are reported as such -- but a season-to-date "0% on time" would describe that scheduler, not the one now
running. Every horizon is therefore tagged with the era its TRIGGER fell in:

    BEFORE_CONDUCTOR   trigger before CONDUCTOR_DEPLOYED_UTC -- history, never rewritten
    AFTER_CONDUCTOR    trigger at or after it -- the health of the current system

and the two are summarised separately. Nothing here edits a capture record; this only reads them.

Lateness is measured at the moment the capture was RECORDED (after its build finished), which is later than
the market snapshot the packet froze. The labels therefore err toward late, never toward on time.

Exit 1 with `--fail-on-recent-miss-hours N` when an AFTER_CONDUCTOR horizon whose kickoff fell in the last N
hours was MISSED -- a visible red run, rather than a number nobody reads.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.data.nfl_calendar import load_schedule, week_blocks                   # noqa: E402
from nfl_edge.evaluation.capture_health import horizon_delivery                      # noqa: E402

#: When the horizon conductor (.github/workflows/horizon-conductor.yml) began serving these horizons. The
#: first horizon after it is 2026 week 3's T-6h (2026-09-24T18:15Z), so any instant between the week 3 T-24h
#: capture (00:34Z) and 18:15Z classifies every horizon identically.
CONDUCTOR_DEPLOYED_UTC = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)

ERA_BEFORE, ERA_AFTER = "BEFORE_CONDUCTOR", "AFTER_CONDUCTOR"


def _dt(s):
    if not s:
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def run_nfl_markers(state: dict) -> list:
    """RUN NFL keeps one state document; turn each record into the marker shape capture_health reads."""
    out = []
    for hid, rec in ((state or {}).get("captured") or {}).items():
        out.append({"horizon_id": hid, "snapshot_id": rec.get("captured_at"), "status": rec.get("status")})
    return out


def three_arm_markers(directory: str | None) -> list:
    out = []
    if not directory or not os.path.isdir(directory):
        return out
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".json"):
            continue
        try:
            doc = json.load(open(os.path.join(directory, name)))
        except (OSError, ValueError):
            continue
        out.append({"horizon_id": doc.get("horizon_id"), "snapshot_id": doc.get("captured_at"),
                    "status": doc.get("status")})
    return out


def season_health(games: list, markers: list, now: datetime, *, season: int,
                  deployed: datetime = CONDUCTOR_DEPLOYED_UTC) -> dict:
    rows = []
    for b in week_blocks(games):
        if b["season"] != season or b["season_type"] != "REG" or b["first_kickoff"] is None:
            continue
        if b["first_kickoff"] - timedelta(days=2) > now:
            continue                                       # nothing of this slate can be owed yet
        hd = horizon_delivery(b["slate_id"], [{"game_id": g["game_id"], "kickoff_utc": g["kickoff_utc"]}
                                              for g in b["games"] if g.get("kickoff_utc")], markers, now)
        for r in hd["rows"]:
            r["slate_id"] = b["slate_id"]
            r["week"] = b["week"]
            r["era"] = ERA_AFTER if _dt(r["trigger_utc"]) >= deployed else ERA_BEFORE
            rows.append(r)
    return {"rows": rows, "summary": {era: summarise([r for r in rows if r["era"] == era])
                                      for era in (ERA_BEFORE, ERA_AFTER)}}


def summarise(rows: list) -> dict:
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    owed = [r for r in rows if r["status"] not in ("NOT_YET_DUE", "DUE")]
    delivered = [r for r in owed if r["status"].startswith("DELIVERED")]
    lat = sorted(r["lateness_min"] for r in delivered if r.get("lateness_min") is not None)
    return {"horizons": len(rows), "owed": len(owed), "delivered": len(delivered),
            "missed": counts.get("MISSED", 0), "counts": counts,
            "delivered_pct": round(100.0 * len(delivered) / len(owed), 1) if owed else None,
            "on_time_pct": round(100.0 * counts.get("DELIVERED_ON_TIME", 0) / len(owed), 1) if owed else None,
            "median_lateness_min": lat[len(lat) // 2] if lat else None,
            "missed_ids": [r["horizon_id"] for r in owed if r["status"] == "MISSED"]}


def render(doc: dict) -> str:
    L = [f"# Horizon capture health — season {doc['season']} (as of {doc['as_of']})", "",
         f"Conductor era boundary: {doc['conductor_deployed_utc']}. BEFORE_CONDUCTOR is history and is never "
         "rewritten; AFTER_CONDUCTOR is the health of the current system. Lateness is measured when the capture "
         "was recorded (after its build), so labels err toward late.", ""]
    for target, t in doc["targets"].items():
        L += [f"## {target}", "", "| era | owed | delivered | on time | late | degraded | missed | delivered % | "
              "on-time % | median lateness (min) |", "|---|---|---|---|---|---|---|---|---|---|"]
        for era, s in t["summary"].items():
            c = s["counts"]
            L.append(f"| {era} | {s['owed']} | {s['delivered']} | {c.get('DELIVERED_ON_TIME', 0)} | "
                     f"{c.get('DELIVERED_LATE', 0)} | {c.get('DELIVERED_DEGRADED', 0)} | {s['missed']} | "
                     f"{s['delivered_pct']} | {s['on_time_pct']} | {s['median_lateness_min']} |")
        for era, s in t["summary"].items():
            if s["missed_ids"]:
                L.append(f"\n{era} missed: " + ", ".join(s["missed_ids"]))
        L.append("")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-nfl-state", default=None)
    ap.add_argument("--three-arm-markers-dir", default=None)
    ap.add_argument("--schedule", default=None)
    ap.add_argument("--season", type=int, default=None)
    ap.add_argument("--now", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fail-on-recent-miss-hours", type=float, default=None)
    a = ap.parse_args(argv)
    now = _dt(a.now) if a.now else datetime.now(timezone.utc)
    games, _src = load_schedule(ROOT, path=a.schedule, allow_download=True)
    season = a.season or now.year
    state = json.load(open(a.run_nfl_state)) if a.run_nfl_state and os.path.exists(a.run_nfl_state) else {}
    targets = {"RUN_NFL": season_health(games, run_nfl_markers(state), now, season=season),
               "THREE_ARM": season_health(games, three_arm_markers(a.three_arm_markers_dir), now, season=season)}
    doc = {"capture_health_report": "horizon-capture-health-1.0.0", "season": season, "as_of": now.isoformat(),
           "conductor_deployed_utc": CONDUCTOR_DEPLOYED_UTC.isoformat(),
           "notes": ["RUN_NFL records were pruned after 45 days until 2026-09-24 (now 400); a pruned record "
                     "would read as MISSED, so an early-season figure quoted late in the season should be checked "
                     "against the history index on handicap-reports."],
           "targets": targets}
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, f"{season}.capture_health.json"), "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True, default=str)
    md = render(doc)
    with open(os.path.join(a.out, f"{season}.CAPTURE_HEALTH.md"), "w") as f:
        f.write(md)
    print(md)
    if a.fail_on_recent_miss_hours is not None:
        horizon = now - timedelta(hours=a.fail_on_recent_miss_hours)
        recent = [(t, r["horizon_id"]) for t, v in targets.items() for r in v["rows"]
                  if r["era"] == ERA_AFTER and r["status"] == "MISSED" and _dt(r["kickoff_utc"]) >= horizon]
        if recent:
            for t, hid in recent:
                print(f"::error::{t}: horizon {hid} was MISSED under the conductor")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
