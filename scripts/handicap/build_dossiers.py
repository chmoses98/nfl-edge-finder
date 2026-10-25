#!/usr/bin/env python3
"""Write the per-game review dossiers and the all-game triage index beside a built RUN NFL report.

    python3 scripts/handicap/build_dossiers.py --reports-dir data/handicap_report --schedule-csv data/raw/nflverse/schedules/games.csv

Adds to the report directory (so the publish step carries it into `handicap-reports/latest/`):

    dossiers/<game_id>.json   measured / simulation / unavailable, per game (nfl_edge/handicap/dossier.py)
    dossiers/index.md|json    EVERY game in the packet with a triage rank and the reasons; an ordering for deep review, never a filter

Reads the packet only. No ledger, no Kalshi, no model authority. Fail-soft in the workflow: a failure here must not stop the report.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import dossier as DS  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reports-dir", required=True)
    ap.add_argument("--schedule-csv", default=None, help="nflverse games.csv, for rest days; absent = rest UNAVAILABLE")
    a = ap.parse_args(argv)
    with open(os.path.join(a.reports_dir, "packet.json")) as f:
        packet = json.load(f)
    sched = open(a.schedule_csv, encoding="utf-8").read() if a.schedule_csv and os.path.exists(a.schedule_csv) else ""
    ref = DS.slate_reference(packet)
    out = os.path.join(a.reports_dir, "dossiers")
    os.makedirs(out, exist_ok=True)
    now = datetime.now(timezone.utc)
    rows = []
    for g in packet.get("games", []):
        d = DS.build_dossier(g, ref, DS.schedule_row(sched, g["game_id"]) if sched else None)
        t = DS.triage(g, d)
        started = datetime.fromisoformat(g["kickoff_utc"].replace("Z", "+00:00")) <= now
        rows.append({"game_id": g["game_id"], "matchup": f"{g['away_team']} @ {g['home_team']}", "kickoff_utc": g["kickoff_utc"], "started": started, **t})
        with open(os.path.join(out, f"{g['game_id']}.json"), "w") as f:
            json.dump(d, f, indent=1)
    order = sorted(rows, key=lambda r: (r["started"], -r["score"]))
    for i, r in enumerate([x for x in order if not x["started"]], 1):
        r["triage_rank"] = i
    with open(os.path.join(out, "index.json"), "w") as f:
        json.dump({"version": DS.DOSSIER_VERSION, "packet_sha": packet.get("packet_sha"), "built_at": packet.get("built_at"), "games": order,
                   "slate_reference": ref, "note": "Triage ORDERS deep review; it never removes a game. Every game here must end the card in an explicit state."}, f, indent=1)
    lines = ["# Review order (triage)", "", f"packet `{packet.get('packet_sha')}`, built {packet.get('built_at')}. An ordering for deep review, not a screen and not a signal.", "",
             "| rank | game | kickoff (UTC) | score | why |", "|---|---|---|---|---|"]
    for r in order:
        lines.append(f"| {r.get('triage_rank', '–')} | {r['matchup']}{' (started)' if r['started'] else ''} | {r['kickoff_utc'][5:16].replace('T', ' ')} | {r['score']} | {'; '.join(r['reasons']) or '—'} |")
    lines += ["", "Unavailable in every dossier (not captured): " + "; ".join(DS.UNAVAILABLE)]
    with open(os.path.join(out, "index.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"dossiers: {len(rows)} game(s), {sum(1 for r in rows if not r['started'])} unstarted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
