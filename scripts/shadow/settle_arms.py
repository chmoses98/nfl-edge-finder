#!/usr/bin/env python3
"""Evaluate the three-arm forecasts of FINAL games into an immutable arm-evaluation corpus.

    published arm snapshots (market-data data/shadow/arms)     the three-arm records, untouched
  + captured quote history                                      the last complete quote strictly BEFORE kickoff
  + nflverse final results                                      the proven score (same result book as settle_games)
  -> data/shadow/arm_evaluations/<game_id>/<version>.<batch>.arm_game_evaluations.jsonl.gz
                                           <version>.<batch>.arm_contract_evaluations.jsonl.gz

Same discipline as scripts/shadow/settle_games.py: readiness is decided per game before anything is written
(a game is DEFERRED whole), the close is chosen per ticker and never after kickoff, settlement comes from the
incumbent engine, and a rerun is NO-OP / new rows only / CONFLICT (exit 4, nothing written).

Usage:
  python3 scripts/shadow/settle_arms.py --market-data /tmp/md --out data/shadow/arm_evaluations [--game G] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.arms import evaluation as AE, incumbent_center as IC, records as REC, registry as R  # noqa: E402
from nfl_edge.data import silver as SV                                        # noqa: E402
from nfl_edge.pricing.game_env import ResidualBank                           # noqa: E402
from nfl_edge.settlement.final_status import fetch_espn_scoreboard            # noqa: E402
from nfl_edge.settlement.nflverse_results import build_result_book           # noqa: E402
from nfl_edge.settlement.results import READY                                # noqa: E402
from nfl_edge.shadow import evaluation as E                                   # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                            # noqa: E402
from nfl_edge.shadow.quote_history import load_game_quotes                    # noqa: E402


def bank_from_schedule(target_season: int, games=None) -> ResidualBank:
    """The incumbent's residual population from the bronze schedule alone (no play-by-play needed here).

    `games` may be supplied (a polars frame in the silver `games` shape); by default the bronze games.csv the
    workflow has just downloaded is read. Tests inject a frame, so the closing centre needs no live file."""
    if games is None:
        games = SV.load_games()
    bank, _meta = IC.incumbent_bank(games, target_season)
    return bank


def _emit(path, values):
    if not path:
        return
    with open(path, "a") as f:
        for k, v in values.items():
            f.write(f"{k}={v}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "arm_evaluations"))
    ap.add_argument("--arms-root", action="append", default=[], help="extra arm snapshot roots (local staging)")
    ap.add_argument("--season", type=int, default=0)
    ap.add_argument("--game", action="append", default=[])
    ap.add_argument("--eval-version", default=R.ARM_EVALUATION_VERSION)
    ap.add_argument("--lookback-days", type=float, default=10.0)
    ap.add_argument("--days-back", type=int, default=14)
    ap.add_argument("--min-hours-after-kickoff", type=float, default=4.0)
    ap.add_argument("--close-max-staleness-min", type=float, default=E.CLOSE_MAX_STALENESS_S / 60.0)
    ap.add_argument("--no-espn-final", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    seasons = [a.season] if a.season else sorted({now.year, now.year - 1})
    book = build_result_book(ROOT, seasons, min_hours_after_kickoff=a.min_hours_after_kickoff)

    roots = [REC.arms_root(a.market_data)] + list(a.arms_root)
    if a.game:
        candidates = sorted(set(a.game))
    else:
        candidates = sorted(g for g, gr in book.games.items() if gr.status == "FINAL" and gr.kickoff_utc
                            and now - timedelta(days=a.lookback_days) <= datetime.fromisoformat(gr.kickoff_utc) <= now)
    if not candidates:
        print("no candidate games"); _emit(a.github_output, {"status": "NOTHING_TO_DO", "written": 0}); return 0
    kicks = [datetime.fromisoformat(book.games[g].kickoff_utc) for g in candidates if g in book.games and book.games[g].kickoff_utc]
    lo = (min(kicks) - timedelta(days=21)).date().isoformat() if kicks else None
    hi = (max(kicks) + timedelta(days=1)).date().isoformat() if kicks else None
    games_recs = REC.load_records(roots, "arm_games", candidates, lo, hi)
    contracts_recs = REC.load_records(roots, "arm_contracts", candidates, lo, hi)
    by_game, cby_game = {}, {}
    for r in games_recs.values():
        if r.get("prekickoff") and r.get("status") == R.OK:
            by_game.setdefault(r["game_id"], []).append(r)
    for r in contracts_recs.values():
        cby_game.setdefault(r["game_id"], []).append(r)
    print(f"arm snapshots: {len(by_game)} candidate game(s) with prekickoff three-arm records "
          f"({sum(len(v) for v in by_game.values())} game rows, {sum(len(v) for v in cby_game.values())} contract rows)", flush=True)
    if not by_game:
        _emit(a.github_output, {"status": "NOTHING_TO_DO", "written": 0}); return 0

    if not a.no_espn_final:
        dates = sorted({book.games[g].kickoff_utc[:10].replace("-", "") for g in by_game if g in book.games and book.games[g].kickoff_utc})
        try:
            atts, meta = fetch_espn_scoreboard(dates, verbose=lambda m: print(m, flush=True))
            book.add_final_attestations(atts); book.sources["espn_final_status"] = meta
        except Exception as e:  # noqa: BLE001 - best effort, never required
            print(f"::warning::ESPN attestation unavailable: {type(e).__name__}", flush=True)

    published = os.path.join(a.market_data, "data", "shadow", "arm_evaluations")
    gcorpus = ST.EvaluationCorpus(a.out, read_roots=[published], suffix=AE.GAME_SUFFIX)
    ccorpus = ST.EvaluationCorpus(a.out, read_roots=[published], suffix=AE.CONTRACT_SUFFIX)
    batch = ST.batch_id(now)
    capture_root = os.path.join(a.market_data, "data", "kalshi", "capture")
    bank = None
    written = unchanged = conflicts = 0
    deferred, done = [], []
    for gid in sorted(by_game):
        game = book.games.get(gid)
        state, reason = book.readiness(gid, needs_player_stats=False, now=now)
        if state != READY:
            deferred.append({"game_id": gid, "state": state, "reason": reason}); print(f"  DEFER {gid}: {state} -- {reason}"); continue
        ko = datetime.fromisoformat(game.kickoff_utc); kickoff_ts = ko.timestamp()
        crecs = cby_game.get(gid, [])
        tickers = sorted({c["ticker"] for c in crecs})
        quotes, qstats = load_game_quotes(capture_root, gid, tickers, kickoff_utc=game.kickoff_utc, days_back=a.days_back)
        closes = {}
        for t in tickers:
            qs = quotes.get(t, [])
            pregame = [q for q in qs if q.get("observed_ts") is not None and q["observed_ts"] < kickoff_ts]
            closes[t] = (E.pick_close(qs, kickoff_ts), len(pregame))
        if bank is None:
            bank = bank_from_schedule(int(game.season or now.year))
        liquid = {t: c for t, (c, _n) in closes.items()
                  if c and c.get("yes_bid") is not None and c.get("yes_ask") is not None}
        close_center = AE.closing_center(liquid, crecs, bank, game.home_team, game.away_team)
        if close_center.get("status") == E.CLOSE_OK and close_center.get("latest_quote_observed_ts") is not None:
            gap = kickoff_ts - close_center["latest_quote_observed_ts"]
            close_center["minutes_to_kickoff"] = gap / 60.0
            if gap > a.close_max_staleness_min * 60.0:
                close_center["status"] = E.CLOSE_OK_STALE
        grows = [AE.evaluate_game(r, game, close_center, evaluation_version=a.eval_version, now=now) for r in by_game[gid]]
        crows = [AE.evaluate_contract(c, book, closes.get(c["ticker"], (None, 0))[0], kickoff_ts,
                                      evaluation_version=a.eval_version, close_candidates_seen=closes.get(c["ticker"], (None, 0))[1],
                                      now=now, max_close_staleness_s=a.close_max_staleness_min * 60.0) for c in crecs]
        gplan, cplan = gcorpus.plan(grows, gid), ccorpus.plan(crows, gid)
        if gplan["conflicts"] or cplan["conflicts"]:
            conflicts += len(gplan["conflicts"]) + len(cplan["conflicts"])
            for c in (gplan["conflicts"] + cplan["conflicts"])[:5]:
                print(f"::error::conflict on {c['prediction_id']} ({gid}): {list(c['fields'])[:5]}")
            continue
        sc = Counter(r["settlement_status"] for r in crows)
        print(f"  {gid}: {len(grows)} game rows, {len(crows)} contract rows | close centre {close_center.get('status')} "
              f"{close_center.get('margin')}/{close_center.get('total')} | settled {sc.get('SETTLED', 0)} | "
              f"new {len(gplan['new'])}+{len(cplan['new'])}, unchanged {len(gplan['noop'])}+{len(cplan['noop'])}", flush=True)
        unchanged += len(gplan["noop"]) + len(cplan["noop"])
        if a.dry_run:
            continue
        extra = {"kickoff_utc": game.kickoff_utc, "game_evidence": game.evidence(), "result_sources": book.sources,
                 "arm_snapshots": sorted({r.get("run_id") for r in by_game[gid]}), "close_center": {k: v for k, v in close_center.items() if k != "diag"},
                 "quote_rows_scanned": qstats.get("rows_matched"), "preregistration_sha": R.preregistration_sha()}
        m1 = gcorpus.write_batch(gid, grows, evaluation_version=a.eval_version, batch=batch, plan=gplan, manifest_extra=extra)
        m2 = ccorpus.write_batch(gid, crows, evaluation_version=a.eval_version, batch=batch, plan=cplan, manifest_extra=extra)
        written += m1.get("written", 0) + m2.get("written", 0)
        done.append(gid)
    status = "CONFLICT" if conflicts else ("WROTE" if written else "NO_OP")
    summary = {"batch_id": batch, "evaluation_version": a.eval_version, "games_done": done, "deferred": deferred,
               "written": written, "unchanged": unchanged, "conflicts": conflicts, "status": status, "dry_run": a.dry_run}
    print(json.dumps(summary, indent=1, default=str))
    _emit(a.github_output, {"status": status, "written": written, "unchanged": unchanged, "games_deferred": len(deferred),
                            "batch_id": batch})
    return 4 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
