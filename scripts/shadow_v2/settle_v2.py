#!/usr/bin/env python3
"""Settle every frozen shadow-v2 projection of every FINAL game, build the universal scorecard and the autopsy v2.

    python3 scripts/shadow_v2/settle_v2.py --market-data /tmp/md --projections data/shadow/v2/projections \
        --out data/shadow/v2 --target-season 2026 [--game <id>] [--dry-run]

Reads the published projections (never rewrites them), proves results from nflverse (schedule finals with the
postgame-tables attestation, player statistics, snap counts, play-by-play quarter scores), and appends ONE
write-once settlement batch per game per settlement version to `<out>/settlements/<game_id>/`. A contradiction
between an existing batch and a rerun is a hard error (EvaluationConflict) -- the corpus is append-only. Records
of games that are not yet proven final are deferred, not guessed. Every scorecard is rebuilt from the corpus and
separates PROSPECTIVE_FROZEN from HISTORICAL_RESEARCH evidence.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.engines.player import autopsy_v2 as AU                                     # noqa: E402
from nfl_edge.evaluation import scorecard_v2 as SC                                       # noqa: E402
from nfl_edge.projection.store import read_projections, read_sidecars                    # noqa: E402
from nfl_edge.settlement import crosscheck as XC                                         # noqa: E402
from nfl_edge.settlement import season_settlement as SS                                  # noqa: E402
from nfl_edge.settlement import settle_v2 as S2                                          # noqa: E402
from nfl_edge.settlement.nflverse_results import build_result_book                       # noqa: E402
from nfl_edge.settlement.period_results import PeriodBook                                # noqa: E402
from nfl_edge.settlement.results import READY                                            # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                       # noqa: E402

SUFFIX = "settlements_v2"
AUTOPSY_SUFFIX = "autopsy_v2"
CROSSCHECK_SUFFIX = "crosscheck_v2"


def log(*a):
    print(*a, flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--projections", action="append", default=[], help="projection roots (repeatable); default: market-data's")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2"))
    ap.add_argument("--target-season", type=int, default=2026)
    ap.add_argument("--game", action="append", default=[])
    ap.add_argument("--min-hours-after-kickoff", type=float, default=4.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--now", default="")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args(argv)
    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    roots = a.projections or [os.path.join(a.market_data, "data", "shadow", "v2", "projections")]
    rows = read_projections(roots)
    sidecars = read_sidecars(roots)
    if a.game:
        rows = [r for r in rows if r.get("game_id") in set(a.game)]
    log(f"projections: {len(rows)} records from {roots}")
    book = build_result_book(ROOT, [a.target_season - 1, a.target_season], min_hours_after_kickoff=a.min_hours_after_kickoff)
    pbook = PeriodBook()
    finals = {g.game_id: (g.home_score, g.away_score, g.overtime) for g in book.games.values()}
    for s in (a.target_season,):
        p = os.path.join(ROOT, "data", "raw", "nflverse", "pbp", f"play_by_play_{s}.parquet")
        if os.path.exists(p):
            try:
                pbook.load_pbp(p, finals)
            except Exception as e:  # noqa: BLE001
                log(f"period scores unavailable for {s}: {e}")
    log(f"result book: {len(book.games)} games, period scores for {len(pbook.games)}")
    corpus = ST.EvaluationCorpus(os.path.join(a.out, "settlements"), read_roots=[os.path.join(a.market_data, "data", "shadow", "v2", "settlements")], suffix=SUFFIX)
    au_corpus = ST.EvaluationCorpus(os.path.join(a.out, "autopsy"), read_roots=[os.path.join(a.market_data, "data", "shadow", "v2", "autopsy")], suffix=AUTOPSY_SUFFIX)
    batch = ST.batch_id(now)
    by_game = {}
    for r in rows:
        if r.get("game_id"):
            by_game.setdefault(r["game_id"], []).append(r)
    ready, deferred, written, settled_rows = [], {}, 0, []
    # One SeasonLedger per season, built once: wins-through-week, division winners and playoff qualification all
    # read the same season's games, and rebuilding it per record would be quadratic in the board.
    season_ledgers = {s: SS.SeasonLedger(book.games, s) for s in sorted({g.season for g in book.games.values() if g.season})}
    for gid in sorted(by_game):
        needs_players = any(r.get("engine") == "PLAYER" for r in by_game[gid])
        state, reason = book.readiness(gid, needs_player_stats=needs_players, now=now)
        if state != READY:
            deferred[gid] = f"{state}: {reason}"
            continue
        ready.append(gid)
        out_rows = []
        for r in by_game[gid]:
            if r.get("p_yes") is None:
                continue                                    # a refusal has nothing to settle
            s = S2.settle_projection(r, book, pbook, season_ledger=season_ledgers)
            out_rows.append({"prediction_id": r["record_id"], "evaluation_version": S2.SETTLE_VERSION, "evaluated_at": now.isoformat(),
                             **{k: r.get(k) for k in ("record_id", "snapshot_id", "ticker", "model_arm", "engine", "market_family", "period", "stat_family",
                                                      "game_id", "season", "week", "subject_id", "subject_name", "horizon_label", "minutes_to_kickoff",
                                                      "semantic_confidence", "identity_confidence", "evidence_class", "support_state", "p_yes", "contract_value",
                                                      "mid", "yes_bid", "yes_ask", "no_ask", "quote_width", "liquidity", "volume", "series_ticker")},
                             "market_identification": (r.get("projection_lineage") or {}).get("identification"),
                             "availability_state": (r.get("feature_lineage") or {}).get("availability_state"), **s.to_dict()})
        if not out_rows:
            continue
        settled_rows.extend(out_rows)
        plan = corpus.plan(out_rows, gid)
        log(f"  {gid}: {len(out_rows)} rows -> new {len(plan['new'])}, unchanged {len(plan['noop'])}, conflicts {len(plan['conflicts'])}")
        if plan["conflicts"]:
            raise ST.EvaluationConflict(plan["conflicts"])
        if not a.dry_run:
            man = corpus.write_batch(gid, out_rows, evaluation_version=S2.SETTLE_VERSION, batch=batch, plan=plan)
            written += man.get("written", 0)
        # autopsy v2 on the DATA arm's latest pregame record per (player, stat, ticker)
        au_rows = []
        latest = {}
        for r in by_game[gid]:
            if r.get("model_arm") == "DATA_PLAYER_DIST" and r.get("p_yes") is not None:
                key = (r.get("subject_id"), r.get("stat_family"), r.get("threshold"))
                if key not in latest or (r.get("minutes_to_kickoff") or 1e9) < (latest[key].get("minutes_to_kickoff") or 1e9):
                    latest[key] = r
        for r in latest.values():
            sc = sidecars.get(r.get("snapshot_id")) or {}
            full_ctx = (sc.get("player_contexts") or {}).get((r.get("player_context") or {}).get("player_context_id"))
            d = AU.diagnose({**r, "team": (r.get("feature_lineage") or {}).get("team")}, book, now=now, context=full_ctx)
            au_rows.append({"prediction_id": r["record_id"], "evaluation_version": AU.AUTOPSY_VERSION, "evaluated_at": now.isoformat(), **d})
        if au_rows and not a.dry_run:
            plan = au_corpus.plan(au_rows, gid)
            if plan["conflicts"]:
                raise ST.EvaluationConflict(plan["conflicts"])
            au_corpus.write_batch(gid, au_rows, evaluation_version=AU.AUTOPSY_VERSION, batch=batch, plan=plan)
    # scorecard from the WHOLE corpus (published + staged)
    all_rows = [row for (row, _) in corpus.load().values()]
    # EXCHANGE CROSS-CHECK. Read only from what the pipeline already captured (daily discovery's settled bucket
    # and the historical backfill), so it costs no API calls. The derived football settlement is never replaced
    # by the exchange value: this is a check on our reading of the contract, and a disagreement is a hard
    # research-quality warning that the whole family may have been priced on a wrong reading.
    xres = XC.ExchangeResults(a.market_data)
    xrows = XC.crosscheck_rows(all_rows, xres)
    xsum = XC.summarize(xrows)
    log(f"exchange cross-check: {xsum['n']} rows, {xsum['by_agreement']}, disagreements {xsum['n_disagreements']}"
        f"{' in ' + ', '.join(xsum['families_with_disagreement']) if xsum['families_with_disagreement'] else ''}")
    for d in xsum["disagreements"][:10]:
        log(f"  ::warning::SETTLEMENT DISAGREEMENT {d['ticker']}: derived {d['derived_settled_yes']} vs exchange {d['exchange_payout']}")
    sc_dir = os.path.join(a.out, "scorecards")
    if not a.dry_run:
        os.makedirs(sc_dir, exist_ok=True)
        json.dump(xsum, open(os.path.join(sc_dir, "exchange_crosscheck.json"), "w"), indent=1, default=str)
        xc_corpus = ST.EvaluationCorpus(os.path.join(a.out, "crosscheck"),
                                        read_roots=[os.path.join(a.market_data, "data", "shadow", "v2", "crosscheck")],
                                        suffix=CROSSCHECK_SUFFIX)
        by_g = {}
        for r, row in zip(all_rows, xrows):
            by_g.setdefault(r.get("game_id") or "SEASON", []).append({**row, "prediction_id": r.get("prediction_id") or r.get("record_id")})
        for gid, rws in by_g.items():
            plan = xc_corpus.plan(rws, gid)
            if plan["conflicts"]:
                raise ST.EvaluationConflict(plan["conflicts"])
            xc_corpus.write_batch(gid, rws, evaluation_version=XC.CROSSCHECK_VERSION, batch=batch, plan=plan)
        json.dump(sc, open(os.path.join(sc_dir, "scorecard_v2.json"), "w"), indent=1, default=str)
        open(os.path.join(sc_dir, "SCORECARD_V2.md"), "w").write(SC.render(sc))
        au_all = [row for (row, _) in au_corpus.load().values()]
        json.dump(AU.summarize(au_all), open(os.path.join(sc_dir, "autopsy_v2_summary.json"), "w"), indent=1, default=str)
    summary = {"batch_id": batch, "settle_version": S2.SETTLE_VERSION, "games_ready": ready, "games_deferred": deferred, "written": written,
               "by_status": dict(Counter(r["settlement_status"] for r in settled_rows)), "corpus_rows": len(all_rows), "dry_run": a.dry_run,
               "season_settle_version": SS.SEASON_SETTLE_VERSION,
               "exchange_crosscheck": {k: xsum[k] for k in ("n", "by_agreement", "comparable", "agreement_rate",
                                                            "n_disagreements", "families_with_disagreement")},
               "exchange_sources": xres.summary()}
    log(json.dumps(summary, indent=1, default=str))
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"status={'WROTE' if written else 'NOTHING_TO_DO'}\nwritten={written}\nbatch_id={batch}\ngames_ready={len(ready)}\ngames_deferred={len(deferred)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
