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

MEMORY SCALES WITH THE GAME, NOT WITH THE ARCHIVE. The first version read every projection ever published into
memory before it knew which game it was settling; at 1.5 million records of ~8 KB the runner was killed before
the first log line. The work is now ordered the other way round:

    1. the result book decides which games are FINAL;
    2. games that already hold an immutable batch under this settlement version are SKIPPED, by file name,
       before a single projection row is read (reported, never silent);
    3. the projection index (one small JSON per projection file, cached by content hash and published beside
       the corpus) says which files hold each remaining game;
    4. each game is streamed once from exactly those files (whether it needs the player tables is a count the
       index took at parse time) and only the NEW settlement rows of that game are held until its batch is written;
    5. season-scoped records are streamed from the files that hold them and dispatched the same way;
    6. the scorecard and the exchange cross-check are rebuilt from the whole corpus one game directory at a time
       through accumulators, never as a list of rows.

Every probability-carrying record examined is accounted for: dispatched, season-scoped, unreachable (with the
missing key named) -- and `silently_dropped` is computed from those counts and must be zero.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.engines.player import autopsy_v2 as AU                                     # noqa: E402
from nfl_edge.evaluation import scorecard_v2 as SC                                       # noqa: E402
from nfl_edge.projection.store import INDEX_DIRNAME, ProjectionIndex, ScanStats, SidecarCache, iter_projections  # noqa: E402
from nfl_edge.settlement import crosscheck as XC                                         # noqa: E402
from nfl_edge.settlement import reachability as RE                                       # noqa: E402
from nfl_edge.settlement import season_settlement as SS                                  # noqa: E402
from nfl_edge.settlement import settle_v2 as S2                                          # noqa: E402
from nfl_edge.settlement.nflverse_results import build_result_book                       # noqa: E402
from nfl_edge.settlement.period_results import PeriodBook                                # noqa: E402
from nfl_edge.settlement.results import FINAL, READY                                     # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                       # noqa: E402

SUFFIX = "settlements_v2"
AUTOPSY_SUFFIX = "autopsy_v2"
CROSSCHECK_SUFFIX = "crosscheck_v2"
UNREACHABLE_DETAIL_KEEP = 50

# the projection fields copied onto every settlement row (unchanged from the first version)
COPIED = ("record_id", "snapshot_id", "ticker", "model_arm", "engine", "market_family", "period", "stat_family",
          "game_id", "season", "week", "subject_id", "subject_name", "horizon_label", "minutes_to_kickoff",
          "semantic_confidence", "identity_confidence", "evidence_class", "support_state", "p_yes", "contract_value",
          "mid", "yes_bid", "yes_ask", "no_ask", "quote_width", "liquidity", "volume", "series_ticker")


def log(*a):
    print(*a, flush=True)


def _rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def settlement_row(r: dict, s, now: datetime, *, season_scope: bool = False) -> dict:
    row = {"prediction_id": r["record_id"], "evaluation_version": S2.SETTLE_VERSION, "evaluated_at": now.isoformat(),
           **{k: r.get(k) for k in COPIED}}
    if season_scope:
        row["settlement_scope"] = RE.SEASON
    else:
        row["market_identification"] = (r.get("projection_lineage") or {}).get("identification")
        row["availability_state"] = (r.get("feature_lineage") or {}).get("availability_state")
    row.update(s.to_dict())
    # A season-scoped row is stamped with the evidence lifecycle it belongs to: a settlement is terminal and
    # keeps one identity forever, while "the season has not determined this yet" is an observation filed under
    # its own evidence vintage. Without that distinction each week's truthful reading contradicted the last
    # week's and the corpus refused the whole batch (nfl_edge/settlement/settle_v2.py).
    if season_scope:
        row = S2.season_versioned(row)
    return row


def _write_crosschecks(corpus, planner, key: str, batch: str, *, dry_run: bool):
    """One cross-check batch for one game directory, conflicts first.

    A batch holds rows of both evidence tiers -- the terminal verdicts reached this run and the provisional
    observations of tickers the exchange has not resolved yet -- so the manifest records the split. A conflict
    here now means what it is supposed to mean: two TERMINAL readings of the same prediction disagree.
    """
    if planner.conflicts:
        raise ST.EvaluationConflict(planner.conflicts)
    plan = planner.plan()
    if dry_run:
        return
    corpus.write_batch(key, [], evaluation_version=XC.CROSSCHECK_VERSION, batch=batch, plan=plan,
                       manifest_extra=XC.batch_manifest(plan["new"]))


class Accounting:
    """Every probability-carrying record examined this run, by where it went. `silently_dropped` is derived."""

    def __init__(self):
        self.scan = ScanStats()                      # the settlement streams (game passes + season pass)
        self.examined = 0                            # probability rows examined by the settlement streams
        self.game_dispatched = 0
        self.season_dispatched = 0
        self.unreachable = 0
        self.unreachable_detail: list = []
        self.season_pass_game_rows = 0               # game rows met in the season pass (they belong to game passes)
        self.season_already_terminal = 0             # season records whose terminal settlement is already published
        self.no_probability = 0                      # refusals: nothing to settle, by construction (from the index)
        self.by_status = Counter()

    def note_unreachable(self, r: dict, rr: dict):
        self.unreachable += 1
        if len(self.unreachable_detail) < UNREACHABLE_DETAIL_KEEP:
            self.unreachable_detail.append({**{k: r.get(k) for k in ("record_id", "ticker", "market_family", "model_arm")},
                                            "reachability": rr})

    def silently_dropped(self) -> int:
        return self.examined - (self.game_dispatched + self.season_dispatched + self.unreachable
                                + self.season_already_terminal)

    def to_dict(self) -> dict:
        return {"projection_scan": self.scan.to_dict(), "scan_reconciles": self.scan.reconciles(),
                "probability_rows_examined": self.examined, "game_scoped_dispatched": self.game_dispatched,
                "season_scoped_dispatched": self.season_dispatched, "unreachable": self.unreachable,
                "season_already_terminal_not_re_offered": self.season_already_terminal,
                "season_pass_game_rows_deferred_to_game_passes": self.season_pass_game_rows,
                "rows_without_probability_not_examined": self.no_probability,
                "silently_dropped": self.silently_dropped()}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--projections", action="append", default=[], help="projection roots (repeatable); default: market-data's")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2"))
    ap.add_argument("--target-season", type=int, default=2026)
    ap.add_argument("--game", action="append", default=[], help="settle exactly these games (examined even if a batch exists)")
    ap.add_argument("--min-hours-after-kickoff", type=float, default=4.0)
    ap.add_argument("--recheck-settled", action="store_true", help="re-examine games that already hold a batch (no-op unless evidence changed)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--now", default="")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args(argv)
    t0 = time.time()
    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    md = os.path.join(a.market_data, "data", "shadow", "v2")
    roots = a.projections or [os.path.join(md, "projections")]
    acct = Accounting()

    # ---- 1. results
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
    log(f"result book: {len(book.games)} games, period scores for {len(pbook.games)} (rss {_rss_mb():.0f} MB)")

    # ---- 2. the projection index: which files hold which games, without reading rows into memory
    index = ProjectionIndex(roots, index_roots=[os.path.join(md, INDEX_DIRNAME)],
                            write_root=None if a.dry_run else os.path.join(a.out, INDEX_DIRNAME))
    isum = index.summary()
    log(f"projection index: {isum['files']} files ({isum['files_index_reused']} reused, {isum['files_indexed_this_run']} indexed now), "
        f"{isum['rows_total']} rows over {isum['games']} games, {isum['no_game_rows']} rows without a game "
        f"({isum['no_game_probability_rows']} with a probability) from {roots} (rss {_rss_mb():.0f} MB)")

    corpus = ST.EvaluationCorpus(os.path.join(a.out, "settlements"), read_roots=[os.path.join(md, "settlements")], suffix=SUFFIX)
    au_corpus = ST.EvaluationCorpus(os.path.join(a.out, "autopsy"), read_roots=[os.path.join(md, "autopsy")], suffix=AUTOPSY_SUFFIX)
    batch = ST.batch_id(now)
    sidecars = SidecarCache(roots)

    # ---- 3. candidate games: FINAL in the result book, holding projections, not already settled under this version
    final_games = {gid for gid, g in book.games.items() if g.status == FINAL}
    with_rows = set(index.games())
    forced = list(dict.fromkeys(a.game))
    candidates = forced or sorted(final_games & with_rows)
    not_final_with_projections = sorted(with_rows - final_games - set(forced))
    skipped_settled, examine = [], []
    for gid in candidates:
        if not forced and not a.recheck_settled and corpus.has_batch(gid, S2.SETTLE_VERSION):
            skipped_settled.append(gid)
            continue
        examine.append(gid)
    log(f"candidates: {len(candidates)} FINAL game(s) with projections; {len(skipped_settled)} skipped because an immutable "
        f"{S2.SETTLE_VERSION} batch already exists; {len(examine)} to examine; {len(not_final_with_projections)} game(s) with "
        f"projections not yet final (deferred by construction)")
    for gid in examine:
        g = index.game(gid) or {"n": 0, "prob": 0}
        acct.no_probability += g["n"] - g["prob"]

    # One SeasonLedger per season, built once: wins-through-week, division winners and playoff qualification all
    # read the same season's games, and rebuilding it per record would be quadratic in the board.
    season_ledgers = {s: SS.SeasonLedger(book.games, s) for s in sorted({g.season for g in book.games.values() if g.season})}

    # ---- 4. one game at a time
    ready, deferred, written, au_written, season_rows_from_games = [], {}, 0, 0, []
    per_game = []
    for gid in examine:
        t_game = time.time()
        files = index.files_for_game(gid)
        if not files:
            deferred[gid] = "NO_PROJECTIONS: the index holds no file with this game"
            continue
        # does this game's settlement need the player tables? Only a dispatchable, non-season, probability-carrying
        # PLAYER-engine record does, and the index counted exactly those when it parsed the file.
        needs_players = index.game(gid)["player_prob"] > 0
        state, reason = book.readiness(gid, needs_player_stats=needs_players, now=now)
        if state != READY:
            deferred[gid] = f"{state}: {reason}"
            continue
        ready.append(gid)
        # one pass -- settle, plan against the corpus index, keep only what is new
        planner, au_planner = corpus.planner(gid), au_corpus.planner(gid)
        n_prob, n_disp, n_au, n_season_deferred, gstat = 0, 0, 0, 0, Counter()
        for r in iter_projections(files=files, game_ids=[gid], has_probability=True, stats=acct.scan):
            n_prob += 1
            rr = RE.reachability(r)
            if rr["state"] != RE.DISPATCHABLE:
                acct.note_unreachable(r, rr)
                continue
            if rr["scope"] == RE.SEASON:
                season_rows_from_games.append(r)       # examined (and counted) in the season pass below
                n_season_deferred += 1
                continue
            s = S2.settle_projection(r, book, pbook, season_ledger=season_ledgers)
            row = settlement_row(r, s, now)
            n_disp += 1
            gstat[row["settlement_status"]] += 1
            planner.offer(row)
            # autopsy v2: ONE AUTOPSY PER ELIGIBLE PREDICTION (every DATA-arm record with a probability, AU.AUTOPSY_ARMS:
            # v2, v3 and v4), keyed by prediction_id; MARKET_PLAYER_DIST and the HYBRID_* arms are excluded because a
            # causal diagnosis of a ladder-implied price would be manufactured, not measured. The sidecar is fetched
            # for this snapshot only.
            if r.get("model_arm") in AU.AUTOPSY_ARMS:
                side_car = sidecars.get(r.get("snapshot_id")) or {}
                full_ctx = (side_car.get("player_contexts") or {}).get((r.get("player_context") or {}).get("player_context_id"))
                d = AU.diagnose({**r, "team": (r.get("feature_lineage") or {}).get("team")}, book, now=now, context=full_ctx)
                au_planner.offer({"prediction_id": r["record_id"], "evaluation_version": AU.AUTOPSY_VERSION,
                                  "evaluated_at": now.isoformat(), "model_arm": r.get("model_arm"),
                                  "horizon_label": r.get("horizon_label"), "snapshot_id": r.get("snapshot_id"),
                                  "autopsy_denominator": f"one per eligible data-arm prediction ({' / '.join(AU.AUTOPSY_ARMS)}, every horizon)", **d})
                n_au += 1
        acct.examined += n_prob - n_season_deferred
        acct.game_dispatched += n_disp
        acct.by_status.update(gstat)
        if n_disp == 0:
            per_game.append({"game_id": gid, "probability_rows": n_prob, "dispatched": 0})
            continue
        if planner.conflicts:
            raise ST.EvaluationConflict(planner.conflicts)
        pc, ac = planner.counts(), au_planner.counts()
        log(f"  {gid}: {n_disp} rows -> new {pc['new']}, unchanged {pc['unchanged']}, conflicts {pc['conflicts']}; "
            f"autopsies {n_au} -> new {ac['new']}, unchanged {ac['unchanged']} (rss {_rss_mb():.0f} MB)")
        if not a.dry_run:
            man = corpus.write_batch(gid, [], evaluation_version=S2.SETTLE_VERSION, batch=batch, plan=planner.plan())
            written += man.get("written", 0)
        if n_au and not a.dry_run:
            if au_planner.conflicts:
                raise ST.EvaluationConflict(au_planner.conflicts)
            man = au_corpus.write_batch(gid, [], evaluation_version=AU.AUTOPSY_VERSION, batch=batch, plan=au_planner.plan())
            au_written += man.get("written", 0)
        per_game.append({"game_id": gid, "probability_rows": n_prob, "dispatched": n_disp, "by_status": dict(gstat),
                         "settlement": pc, "autopsy": ac, "files": len(files), "needs_player_tables": needs_players,
                         "seconds": round(time.time() - t_game, 1)})
        del planner, au_planner

    # ---- 5. SEASON-SCOPED records: dispatched through the same settlement engine, bucketed by season instead of
    # by game. They settle late (a division needs a complete postseason bracket) but they are examined every run
    # and every outcome is written, so none can silently disappear. They live in the files the index says hold
    # rows without a game; rows WITH a game met on the way belong to their game passes and are counted as such.
    season_planners: dict = {}
    season_files = index.files_with_no_game_rows(prob_only=True)

    def season_stream():
        for r in iter_projections(files=season_files, has_probability=True, stats=acct.scan):
            if r.get("game_id"):
                acct.season_pass_game_rows += 1
                continue
            yield r
        yield from season_rows_from_games

    # A season record whose TERMINAL settlement is already published is immutable and is never settled again --
    # the same discipline as skipping a game that already holds a batch, and for the same two reasons: it cannot
    # change, and re-offering it under the terminal identity would file a second copy of a settled row that
    # every scorecard metric would then count twice. Read once per season directory, ids only.
    season_terminal: dict = {}

    def terminal_ids(season: int) -> set:
        got = season_terminal.get(season)
        if got is None:
            got = season_terminal[season] = {row.get("prediction_id") for row, _ in corpus.iter_rows(f"SEASON_{season}")
                                             if S2.season_evidence_tier(row) == S2.SEASON_TERMINAL}
        return got

    n_season = 0
    for r in season_stream():
        acct.examined += 1
        rr = RE.reachability(r)
        if rr["state"] != RE.DISPATCHABLE:
            acct.note_unreachable(r, rr)
            continue
        if rr["scope"] != RE.SEASON:                 # a game-scoped record without a game cannot be dispatchable
            acct.note_unreachable(r, {**rr, "state": RE.MISSING_KEYS, "missing": ["game_id"]})
            continue
        season = int(rr["season"] if rr.get("season") is not None else r["season"])
        if r["record_id"] in terminal_ids(season):
            acct.season_already_terminal += 1
            continue
        pl = season_planners.get(season)
        if pl is None:
            pl = season_planners[season] = corpus.planner(f"SEASON_{season}")
        s = S2.settle_projection(r, book, None, season_ledger=season_ledgers)
        row = settlement_row(r, s, now, season_scope=True)
        acct.season_dispatched += 1
        n_season += 1
        acct.by_status[row["settlement_status"]] += 1
        pl.offer(row)
    season_tiers = Counter()
    for season, pl in sorted(season_planners.items()):
        key = f"SEASON_{season}"
        pc = pl.counts()
        plan = pl.plan()
        tiers = S2.season_batch_manifest(plan["new"])
        season_tiers.update(tiers["by_evidence_tier"])
        log(f"  {key}: {pc['new'] + pc['unchanged'] + pc['conflicts']} rows -> new {pc['new']}, unchanged {pc['unchanged']}, "
            f"conflicts {pc['conflicts']}; new by evidence tier {tiers['by_evidence_tier']}")
        if pl.conflicts:
            raise ST.EvaluationConflict(pl.conflicts)
        if not a.dry_run:
            # One batch carries both tiers at once, so the manifest names the split rather than letting the
            # provisional half be invisible in the file it lives in.
            man = corpus.write_batch(key, [], evaluation_version=S2.SETTLE_VERSION, batch=batch, plan=plan,
                                     manifest_extra=tiers)
            written += man.get("written", 0)
    del season_planners
    if acct.silently_dropped() != 0:
        raise RuntimeError(f"accounting does not reconcile: {acct.to_dict()}")

    # ---- 6. scorecard + exchange cross-check from the WHOLE corpus (published + staged), one game directory at a time.
    # EXCHANGE CROSS-CHECK: read only from what the pipeline already captured (daily discovery's settled bucket
    # and the historical backfill), so it costs no API calls. The derived football settlement is never replaced
    # by the exchange value: this is a check on our reading of the contract, and a disagreement is a hard
    # research-quality warning that the whole family may have been priced on a wrong reading.
    xres = XC.ExchangeResults(a.market_data)
    log(f"exchange results: {xres.summary()['tickers']} tickers from {len(xres.sources_scanned)} source(s) (rss {_rss_mb():.0f} MB)")
    acc = SC.ScorecardAccumulator()
    xsum_acc = XC.SummaryAccumulator()
    xc_corpus = ST.EvaluationCorpus(os.path.join(a.out, "crosscheck"), read_roots=[os.path.join(md, "crosscheck")], suffix=CROSSCHECK_SUFFIX)
    xc_planners: dict = {}
    corpus_rows = 0
    for gdir in corpus.games():
        for row, _ in corpus.iter_rows(gdir):
            corpus_rows += 1
            acc.add(row, game=gdir)
            # The cross-check is stamped with the evidence lifecycle it belongs to before it is offered to the
            # corpus: a terminal verdict is one immutable identity per prediction, while "the exchange has not
            # resolved this yet" is a provisional observation filed under its own evidence vintage. Without that
            # distinction the later, truthful AGREE contradicted the earlier EXCHANGE_MISSING and the corpus
            # refused the whole batch (see nfl_edge/settlement/crosscheck.py).
            xrow = XC.versioned(XC.crosscheck_rows([row], xres)[0], now=now)
            xsum_acc.add(xrow)
            xkey = row.get("game_id") or "SEASON"           # season settlement rows cross-check under one directory
            xp = xc_planners.get(xkey)
            if xp is None:
                xp = xc_planners[xkey] = xc_corpus.planner(xkey)
            xp.offer(xrow)
        acc.end_game()
        for xkey in [k for k in list(xc_planners) if k != "SEASON"]:
            _write_crosschecks(xc_corpus, xc_planners.pop(xkey), xkey, batch, dry_run=a.dry_run)
    for xkey, xp in xc_planners.items():
        _write_crosschecks(xc_corpus, xp, xkey, batch, dry_run=a.dry_run)
    scorecard = acc.finish(reread=lambda g: (row for row, _ in corpus.iter_rows(g)))
    xsum = xsum_acc.finish()
    log(f"exchange cross-check: {xsum['n']} rows, {xsum['by_evidence_tier']}, {xsum['by_agreement']}, "
        f"disagreements {xsum['n_disagreements']}"
        f"{' in ' + ', '.join(xsum['families_with_disagreement']) if xsum['families_with_disagreement'] else ''}")
    for d in xsum["disagreements"][:10]:
        log(f"  ::warning::SETTLEMENT DISAGREEMENT {d['ticker']}: derived {d['derived_settled_yes']} vs exchange {d['exchange_payout']}")
    au_acc = AU.SummaryAccumulator()
    for gdir in au_corpus.games():
        for row, _ in au_corpus.iter_rows(gdir):
            au_acc.add(row)
    sc_dir = os.path.join(a.out, "scorecards")
    if not a.dry_run:
        os.makedirs(sc_dir, exist_ok=True)
        json.dump(xsum, open(os.path.join(sc_dir, "exchange_crosscheck.json"), "w"), indent=1, default=str)
        json.dump(scorecard, open(os.path.join(sc_dir, "scorecard_v2.json"), "w"), indent=1, default=str)
        open(os.path.join(sc_dir, "SCORECARD_V2.md"), "w").write(SC.render(scorecard))
        json.dump(au_acc.finish(), open(os.path.join(sc_dir, "autopsy_v2_summary.json"), "w"), indent=1, default=str)

    summary = {"batch_id": batch, "settle_version": S2.SETTLE_VERSION, "games_ready": ready, "games_deferred": deferred,
               "games_skipped_already_settled": skipped_settled, "games_not_final_with_projections": not_final_with_projections,
               "candidates": len(candidates), "examined": len(examine), "written": written, "autopsies_written": au_written,
               "by_status": dict(acct.by_status), "corpus_rows": corpus_rows, "dry_run": a.dry_run,
               "season_settle_version": SS.SEASON_SETTLE_VERSION,
               "dispatch": {"game_scoped": acct.game_dispatched, "season_scoped": acct.season_dispatched,
                            "unreachable": acct.unreachable, "unreachable_detail": acct.unreachable_detail,
                            "silently_dropped": acct.silently_dropped()},
               "season_new_by_evidence_tier": dict(season_tiers),
               "accounting": acct.to_dict(), "index": isum, "sidecars": sidecars.stats(), "per_game": per_game,
               "exchange_crosscheck": {k: xsum[k] for k in ("n", "by_agreement", "by_evidence_tier", "provisional",
                                                            "terminal", "comparable", "agreement_rate",
                                                            "n_disagreements", "families_with_disagreement")},
               "exchange_sources": xres.summary(),
               "perf": {"seconds": round(time.time() - t0, 1), "max_rss_mb": round(_rss_mb(), 1)}}
    log(json.dumps(summary, indent=1, default=str))
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"status={'WROTE' if written else 'NOTHING_TO_DO'}\nwritten={written}\nbatch_id={batch}\ngames_ready={len(ready)}\n"
                    f"games_deferred={len(deferred)}\ngames_skipped_settled={len(skipped_settled)}\nindex_written={isum['index_files_written']}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
