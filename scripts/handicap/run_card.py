#!/usr/bin/env python3
"""RUN NFL card builder. Reads the published packet + analysis shards and the analyst's thesis file; writes the card.

    python3 scripts/handicap/run_card.py --reports-dir /tmp/hr/latest --theses theses.json --schedule-csv schedule_cache.csv \
        --handicap-root /tmp/hd --market-data /tmp/md --out /tmp/card [--mode LIVE|REHEARSAL] [--as-of 2026-10-25T12:00:00Z]

Reads and computes only. It places nothing and never touches a Kalshi account (the client in this repository has no order surface).
With --market-data and --handicap-root the real preflight (depth walk, fee schedule, quote age, caps against the owner's open book) runs
on every candidate line and only an APPROVED line is called a BET; without them a line is a CANDIDATE and says so.

Outputs (in --out): card.json, CARD.md, records/<recommendation_id>.json (candidate records for the separate, gated write step),
dossiers/<game_id>.json. Stdout carries counts and states only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import card as C  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reports-dir", required=True, help="handicap-reports `latest` directory (packet.json, analysis/)")
    ap.add_argument("--theses", default=None, help="JSON list of analyst theses; none = every game is TRIAGED_NO_THESIS")
    ap.add_argument("--schedule-csv", required=True, help="nflverse games.csv (market-data: data/kalshi/capture/schedule_cache.csv)")
    ap.add_argument("--handicap-root", default=None)
    ap.add_argument("--market-data", default=None)
    ap.add_argument("--mode", choices=(C.LIVE, C.REHEARSAL), default=C.LIVE)
    ap.add_argument("--as-of", default=None, help="decision time. LIVE defaults to now; REHEARSAL defaults to the capture time + 4 min")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    run = C.load_reports(a.reports_dir)
    cap = C._ts(run["packet"]["games"][0]["data_freshness"]["ledger_feature_cutoff"])
    if a.as_of:
        as_of = C._ts(a.as_of)
    elif a.mode == C.REHEARSAL:
        from datetime import timedelta
        as_of = cap + timedelta(minutes=4)
    else:
        as_of = datetime.now(timezone.utc)
    theses = json.load(open(a.theses)) if a.theses else []
    card = C.run_card(run=run, theses=theses, schedule_text=open(a.schedule_csv, encoding="utf-8").read(), root=ROOT, as_of=as_of, mode=a.mode,
                      handicap_root=a.handicap_root, market_data_root=a.market_data)

    os.makedirs(os.path.join(a.out, "records"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "dossiers"), exist_ok=True)
    dossiers = card.pop("dossiers")
    for gid, d in dossiers.items():
        with open(os.path.join(a.out, "dossiers", f"{gid}.json"), "w") as f:
            json.dump(d, f, indent=1)
    for t in card["theses"]:
        sel = t.get("selected")
        if sel:
            with open(os.path.join(a.out, "records", f"{sel['recommendation_id']}.json"), "w") as f:
                json.dump(sel["record"], f, indent=1)
    for t in card["theses"]:
        pr = t.get("pass_record")
        if pr:
            with open(os.path.join(a.out, "records", f"{pr['recommendation_id']}.json"), "w") as f:
                json.dump(pr, f, indent=1)
    with open(os.path.join(a.out, "card.json"), "w") as f:
        json.dump(card, f, indent=1, default=str)
    with open(os.path.join(a.out, "CARD.md"), "w") as f:
        f.write(C.render_markdown(card))

    states: dict = {}
    for g in card["games"]:
        states[g["state"]] = states.get(g["state"], 0) + 1
    print(f"card {card['mode']} as of {card['as_of']}: gate {card['data_gate']['status']}, games {len(card['games'])} {states}, "
          f"theses {len(card['theses'])}, lines {len(card['lines'])}")
    return 0 if not card["blocked"] else 5


if __name__ == "__main__":
    raise SystemExit(main())
