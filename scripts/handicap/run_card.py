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
from nfl_edge.postmortem import decision_evidence as DE  # noqa: E402



def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reports-dir", required=True, help="handicap-reports `latest` directory (packet.json, analysis/)")
    ap.add_argument("--submission", default=None, help="the analyst's submission (reviews + theses). The ONLY input under which a game can be deeply reviewed")
    ap.add_argument("--theses", default=None, help="LEGACY: bare JSON list of theses with no review records. REHEARSAL only unless --allow-unreviewed")
    ap.add_argument("--allow-unreviewed", action="store_true", help="accept --theses in LIVE (they are priced but no game is recorded deeply reviewed)")
    ap.add_argument("--raw-root", default=None, help="data/raw/nflverse (measured usage for the dossiers)")
    ap.add_argument("--bankroll-file", default=None, help="local JSON with the router's context shape; default: env KALSHI_BANKROLL_CONTEXT")
    ap.add_argument("--live-evidence", action="store_true", help="LIVE: fetch each finalist's contract from the venue (read-only public GETs) before the gates")
    ap.add_argument("--fee-root", default=None, help="checkout holding data/kalshi/fees (sparse market-data) when --market-data is not given")
    ap.add_argument("--qb-confirmations", default=None, help="validated confirmed-starter records: a .json document {schema: nfl-qb-confirmations.v1, records: [...]}, a .jsonl "
                    "ledger, or a directory of .jsonl (the append-only ledger on handicap-data: qb_confirmations/). Only records from sources that NAME the starter, observed "
                    "before the decision and before kickoff, for THIS game and team, within 24 h of the decision and 48 h of kickoff, and not withdrawn or in conflict, confirm a quarterback. Without it (or for any game without both quarterbacks confirmed) every "
                    "market whose family depends on the quarterback (nfl_edge/postmortem/qb_dependency.py: score-determined lines, team/game stats, events, QB passing props; pass-catcher props need their own team's QB) is blocked QB_UNKNOWN / QB_NOT_CONFIRMED by the point-in-time gate (fail closed; a depth chart, roster or inactive list is never a confirmation)")
    ap.add_argument("--player-identity-root", default=None, help="data/raw/nflverse holding players/players.parquet, weekly_rosters/roster_weekly_<season>.parquet and "
                    "ff_playerids/db_playerids.csv (default: --raw-root). A contract about ONE named player is judged only after the player's identity and POSITION are VERIFIED "
                    "from these tables (nfl_edge/postmortem/player_identity.py): a quarterback's own rushing/receiving/touchdown prop needs his team's quarterback confirmed AND to be "
                    "him; a player whose identity or position cannot be verified is blocked (PLAYER_IDENTITY_UNVERIFIED), never opened")
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
    from nfl_edge.postmortem import qb_confirmations as QBC
    qb_records, qb_rejected = [], []
    if a.qb_confirmations:
        try:
            qb_records, qb_rejected = QBC.load_records_file(a.qb_confirmations)
        except (OSError, ValueError) as exc:
            print(f"refused: --qb-confirmations is unreadable or the wrong schema: {exc}", file=sys.stderr)
            return 2
    qb_games = run["packet"]["games"]
    run["qb_confirmations"] = QBC.resolve_slate(qb_records, qb_games, as_of=as_of)
    qb_cov = QBC.coverage(run["qb_confirmations"], qb_games, as_of=as_of)
    qb_cov["records_valid"], qb_cov["records_rejected"] = len(qb_records), len(qb_rejected)
    qb_cov["rejections_by_code"] = {}
    for r in qb_rejected:
        qb_cov["rejections_by_code"][r["code"]] = qb_cov["rejections_by_code"].get(r["code"], 0) + 1
    qb_cov["source_supplied"] = bool(a.qb_confirmations)
    from nfl_edge.postmortem import qb_dependency as QD
    qb_cov["qb_dependency_table_version"] = QD.TABLE_VERSION
    from nfl_edge.postmortem import player_identity as PI
    run["decision_time"] = as_of.isoformat()
    run["player_identity_book"] = PI.load_book(a.player_identity_root or a.raw_root, run["packet"].get("season"))
    qb_cov["player_identity"] = run["player_identity_book"].summary()
    theses = json.load(open(a.theses)) if a.theses else []
    submission = json.load(open(a.submission)) if a.submission else None
    if theses and submission is None and a.mode == C.LIVE and not a.allow_unreviewed:
        print("refused: --theses carries no review records; in LIVE mode use --submission (or --allow-unreviewed)", file=sys.stderr)
        return 2
    from nfl_edge.handicap import bankroll as BK
    from nfl_edge.handicap import usage as US
    owner_exp = None
    if a.handicap_root and a.mode == C.LIVE:
        sched_text = open(a.schedule_csv, encoding="utf-8").read()
        ox = C.owner_open_exposure(a.handicap_root, sched_text, run["packet"]["season"])
        owner_exp = sum(ox["by_game"].values()) if ox["state"] == "OK" else None
    bankroll = BK.load(as_of, file_path=a.bankroll_file, open_exposure_dollars=owner_exp) if a.mode == C.LIVE else None
    stats, snaps = US.load_tables(a.raw_root, run["packet"]["season"]) if a.raw_root else (None, None)
    client = None
    if a.live_evidence and a.mode == C.LIVE:
        from nfl_edge.kalshi import client as KC
        client = KC.KalshiClient()
    card = C.run_card(run=run, theses=theses, schedule_text=open(a.schedule_csv, encoding="utf-8").read(), root=ROOT, as_of=as_of, mode=a.mode,
                      handicap_root=a.handicap_root, market_data_root=a.market_data, submission=submission, bankroll=bankroll, stats=stats, snaps=snaps,
                      live_client=client, fee_observations_root=a.fee_root)
    live_docs = card.pop("_live_evidence", None)
    card.pop("_bankroll_private", None)
    card = C.redact_public(card)

    os.makedirs(os.path.join(a.out, "records"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "dossiers"), exist_ok=True)
    dossiers = card.pop("dossiers")
    for gid, d in dossiers.items():
        with open(os.path.join(a.out, "dossiers", f"{gid}.json"), "w") as f:
            json.dump(d, f, indent=1)
    if live_docs:
        os.makedirs(os.path.join(a.out, "evidence"), exist_ok=True)
        for d in live_docs:
            with open(os.path.join(a.out, "evidence", f"{d['market_ticker']}.json"), "w") as f:
                json.dump(d, f)
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
    with open(os.path.join(a.out, "qb_coverage.json"), "w") as f:
        json.dump(qb_cov, f, indent=1)
    # Decision-time evidence for the router's execution-evidence join: digests of the recommendation / model-run ids and the
    # model as-of, beside card.json. Additive and inert (nothing reads it during a run); an incomplete record is skipped and
    # counted, never completed (nfl_edge/postmortem/decision_evidence.py).
    selected = [t["selected"]["record"] for t in card["theses"] if t.get("selected")]
    ev = DE.candidates_from_records(selected)
    DE.write_candidates(os.path.join(a.out, "decision_candidates.jsonl"), ev["candidates"])
    with open(os.path.join(a.out, "decision_candidates_skipped.json"), "w") as f:
        json.dump(ev["skipped"], f, indent=1)
    with open(os.path.join(a.out, "card.json"), "w") as f:
        json.dump(card, f, indent=1, default=str)
    with open(os.path.join(a.out, "CARD.md"), "w") as f:
        f.write(C.render_markdown(card))

    states: dict = {}
    for g in card["games"]:
        states[g["state"]] = states.get(g["state"], 0) + 1
    print(f"card {card['mode']} as of {card['as_of']}: gate {card['data_gate']['status']}, games {len(card['games'])} {states}, "
          f"theses {len(card['theses'])}, lines {len(card['lines'])}; QB confirmed both sides in {qb_cov['games_both_qbs_confirmed']}/{qb_cov['games']} games "
          f"({qb_cov['records_valid']} valid, {qb_cov['records_rejected']} rejected records)")
    return 0 if not card["blocked"] else 5


if __name__ == "__main__":
    raise SystemExit(main())
