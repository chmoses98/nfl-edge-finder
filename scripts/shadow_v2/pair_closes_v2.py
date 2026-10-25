#!/usr/bin/env python3
"""Pair every frozen shadow-v2 projection of a kicked-off game with its CANONICAL CLOSE and compute CLV.

    python3 scripts/shadow_v2/pair_closes_v2.py --market-data /tmp/md [--projections <root>]* --out data/shadow/v2 [--game <id>] [--dry-run] \\
        [--max-games N] [--time-budget-minutes M]

For each game whose kickoff has passed: the close index is built ONCE from the capture (bounded to the game's
days), every projection record of that game (every arm, every horizon, refusals included -- a refusal still
has a market) gets ONE close record and, when it carries a probability, ONE CLV record. Both are written as
write-once batches per game (`closes_v2`, `clv_v2` suffixes) with the same NO_OP / CONFLICT semantics as the
evaluation corpus. The projection files are read, never written. A game whose kickoff is not yet past is skipped:
no close exists before kickoff by definition.

MEMORY SCALES WITH THE GAME. The games and their kickoffs come from the projection index (one small JSON per
projection file, cached by content hash), a game that already holds both its close and its CLV batch under the
current rule versions is skipped by file name before any row is read (reported, never silent), and each remaining
game is streamed from exactly the files that hold it: one close index, one pass, only the NEW rows held until the
batch is written. Season-market rows (no kickoff, never a game-style close) are streamed from the files that hold
them and get their explicit CLOSE_NOT_APPLICABLE_SEASON record, new ones only.

BOUNDED, RESUMABLE, IDEMPOTENT (docs/POSTGAME_SETTLEMENT.md, "Bounded runs"). Kicked-off games are taken oldest kickoff
first, at most --max-games per run and no new group once --time-budget-minutes is spent; the rest is reported as
postponed and the next run continues (a game holding both its batches is skipped by file name). The games of a group
are streamed in ONE pass over the projection files; each game still receives exactly the rows, in the order, a stand-
alone stream would give it, so the batches are byte-identical. The step outputs are written as soon as the games are
done, before the season pass, so a slow tail can never withhold the evidence from the publish gate.
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

from nfl_edge.evaluation import clv as CV, close as CL, openset as OS                    # noqa: E402
from nfl_edge.execution.fees import load_fee_schedule                                    # noqa: E402
from nfl_edge.projection.store import (INDEX_DIRNAME, ProjectionIndex, ScanStats, iter_projections,  # noqa: E402
                                       iter_projections_by_game, may_lack_game_or_kickoff)
from nfl_edge.settlement import reachability as RE                                       # noqa: E402
from nfl_edge.settlement import work_plan as WP                                          # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                       # noqa: E402

CLOSE_SUFFIX, CLV_SUFFIX = "closes_v2", "clv_v2"


def log(*a):
    print(*a, flush=True)


def _dt(s):
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def not_applicable_row(r: dict, now: datetime) -> dict:
    return {"prediction_id": r["record_id"], "evaluation_version": CL.CLOSE_RULE_VERSION,
            "evaluated_at": now.isoformat(), "record_id": r["record_id"], "snapshot_id": r.get("snapshot_id"),
            "model_arm": r.get("model_arm"), "horizon_label": r.get("horizon_label"), "ticker": r.get("ticker"),
            "game_id": None, "close_rule_version": CL.CLOSE_RULE_VERSION,
            "close_status": "CLOSE_NOT_APPLICABLE_SEASON", "close_quality": "NOT_APPLICABLE",
            "close_reason": "a season market has no kickoff; the game-style canonical close is not a "
                            "meaningful question for it and no kickoff is invented to pretend otherwise",
            "flags": ["SEASON_SCOPED"]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--projections", action="append", default=[])
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2"))
    ap.add_argument("--game", action="append", default=[], help="pair exactly these games (examined even if batches exist)")
    ap.add_argument("--recheck-paired", action="store_true", help="re-examine games that already hold close and CLV batches")
    ap.add_argument("--now", default="")
    ap.add_argument("--days-back", type=int, default=14)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--github-output", default="")
    ap.add_argument("--max-games", type=int, default=0,
                    help="pair at most this many kicked-off games per run, oldest kickoff first (0: no cap); the rest wait for the next run")
    ap.add_argument("--time-budget-minutes", type=float, default=0.0,
                    help="stop STARTING game groups once this much wall clock is spent or the next group is estimated not to fit (0: unbounded)")
    ap.add_argument("--max-group-rows", type=int, default=WP.DEFAULT_MAX_GROUP_ROWS_CLOSES,
                    help="projection rows held in memory by one group of games streamed together")
    a = ap.parse_args(argv)
    t0 = time.time()
    now = _dt(a.now) if a.now else datetime.now(timezone.utc)
    md = os.path.join(a.market_data, "data", "shadow", "v2")
    roots = a.projections or [os.path.join(md, "projections")]
    capture_root = os.path.join(a.market_data, "data", "kalshi", "capture")
    try:
        sched = load_fee_schedule(ROOT)
    except Exception as e:  # noqa: BLE001
        sched = None; log(f"fee schedule unavailable: {e}")
    close_corpus = ST.EvaluationCorpus(os.path.join(a.out, "closes"), read_roots=[os.path.join(md, "closes")], suffix=CLOSE_SUFFIX)
    clv_corpus = ST.EvaluationCorpus(os.path.join(a.out, "clv"), read_roots=[os.path.join(md, "clv")], suffix=CLV_SUFFIX)
    batch = ST.batch_id(now)

    index = ProjectionIndex(roots, index_roots=[os.path.join(md, INDEX_DIRNAME)],
                            write_root=None if a.dry_run else os.path.join(a.out, INDEX_DIRNAME))
    isum = index.summary()
    log(f"projection index: {isum['files']} files ({isum['files_index_reused']} reused, {isum['files_indexed_this_run']} indexed now), "
        f"{isum['rows_total']} rows over {isum['games']} games (rss {_rss_mb():.0f} MB)")

    # ---- candidate games: kicked off, holding projections, not already paired under the current rule versions
    forced = list(dict.fromkeys(a.game))
    games = index.games()
    not_kicked_off, no_kickoff, skipped_paired, examine = [], [], [], []
    for gid in (forced or sorted(games)):
        g = games.get(gid)
        if g is None:
            no_kickoff.append(gid); continue
        if not g.get("kickoff_utc"):
            no_kickoff.append(gid); continue
        if now < _dt(g["kickoff_utc"]):
            not_kicked_off.append(gid); continue
        # A game none of whose rows carries a probability can never produce a CLV record, so it never gets a CLV batch;
        # waiting for one made 2026_01_NE_SEA and 2026_01_SF_LA (closes published, no CLV possible) re-streamed on every run.
        if not forced and not a.recheck_paired and close_corpus.has_batch(gid, CL.CLOSE_RULE_VERSION) \
                and (clv_corpus.has_batch(gid, CV.CLV_VERSION) or not g.get("prob")):
            skipped_paired.append(gid); continue
        examine.append(gid)
    log(f"candidates: {len(games)} game(s) with projections; {len(not_kicked_off)} not kicked off; {len(no_kickoff)} without a kickoff; "
        f"{len(skipped_paired)} skipped because immutable {CL.CLOSE_RULE_VERSION} + {CV.CLV_VERSION} batches already exist; {len(examine)} to examine")

    runs = CL.CaptureRuns(capture_root)
    # One open-set ledger, shared across games: it answers "was this exact contract open at this run", which is
    # what separates a close that stands on a delisting from one standing on a failed fetch. Captures written
    # before the open set existed carry none, and the close then behaves exactly as it did before.
    oset = OS.OpenSetLedger(capture_root)
    if not oset.runs:
        oset = None
        log("no open-set evidence in this capture window: closes carry presence UNKNOWN (pre-openset captures)")
    else:
        v = oset.verify()
        log(f"open-set ledger: {v['runs']} runs, {v['verified']} hash-verified, {len(v['mismatched'])} mismatched, {len(v['chain_breaks'])} chain breaks (rss {_rss_mb():.0f} MB)")

    scan = ScanStats()
    summary = {"games_paired": [], "games_skipped_not_kicked_off": not_kicked_off, "games_skipped_already_paired": skipped_paired,
               "games_without_kickoff": no_kickoff, "written_closes": 0, "written_clv": 0,
               "close_status": Counter(), "close_quality": Counter(), "clv_status": Counter(),
               "rows_examined": 0, "rows_game_without_kickoff": 0, "rows_season_pass_game_rows": 0}
    # ---- the owed games, OLDEST KICKOFF FIRST, a GROUP at a time (one pass over the projection files per group).
    #
    # BOUNDED AND RESUMABLE, like settle_v2.py: at most --max-games games per run, no new group once
    # --time-budget-minutes is spent, the rest reported as postponed and picked up by the next scheduled run (a game
    # that holds both its batches is skipped by file name above). Each game's close and CLV batches are written as
    # soon as its group finishes. A snapshot file holds every game on the board, so streaming the games one by one
    # decompressed the same ~750 files once per game (~4 minutes each, measured); a group decompresses them once.
    # Each game still receives exactly the rows, in exactly the order, a stand-alone stream would have given it.
    sched_games = [g for g in (examine if forced else WP.oldest_first(games, examine)) if index.files_for_game(g)]
    budget = WP.Budget(a.time_budget_minutes)      # counted from here: the index above is cached after the first run
    groups = WP.partition(sched_games, games, max_rows=a.max_group_rows, row_key="n")
    selection = WP.select_groups(groups, games, budget, max_games=a.max_games, row_key="n", per_row=WP.CLOSE_SECONDS_PER_ROW)
    log(f"owed: {len(sched_games)} game(s); {len(groups)} group(s) of at most {a.max_group_rows} rows; "
        f"cap {a.max_games or 'none'} game(s), budget {a.time_budget_minutes or 'none'} min")
    na_planner = close_corpus.planner("SEASON")
    n_na = 0
    for group in selection:
        t_group = time.time()
        st = {}
        for gid in group:
            ko = _dt(games[gid]["kickoff_utc"])
            st[gid] = {"idx": CL.CloseIndex(capture_root, gid, ko.isoformat(), runs=runs, days_back=a.days_back, openset=oset),
                       "cp": close_corpus.planner(gid), "vp": clv_corpus.planner(gid), "cache": {},
                       "n_rows": 0, "n_close": 0, "n_clv": 0, "n_nokick": 0}
        group_files = index.files_for_games(group)
        for gid, r in iter_projections_by_game(group_files, group, stats=scan):
            g = st[gid]
            g["n_rows"] += 1
            if not r.get("kickoff_utc"):
                # a game row with no kickoff: nothing to select a close against. A season market carrying a game id
                # still gets its explicit not-applicable record, exactly as one without a game id does.
                if RE.scope_of(r.get("market_family"), r.get("engine")) == RE.SEASON:
                    na_planner.offer(not_applicable_row(r, now))
                    n_na += 1
                else:
                    g["n_nokick"] += 1
                continue
            key = r["ticker"]
            cache = g["cache"]
            if key not in cache:
                cache[key] = g["idx"].select(r["ticker"], series_ticker=r.get("series_ticker"), projection_kickoff_utc=r.get("kickoff_utc"))
            c = cache[key]
            g["cp"].offer({"prediction_id": r["record_id"], "evaluation_version": CL.CLOSE_RULE_VERSION, "evaluated_at": now.isoformat(), "record_id": r["record_id"],
                           "snapshot_id": r.get("snapshot_id"), "model_arm": r.get("model_arm"), "horizon_label": r.get("horizon_label"), **c})
            g["n_close"] += 1
            summary["close_status"][c["close_status"]] += 1; summary["close_quality"][c["close_quality"]] += 1
            if r.get("p_yes") is not None:
                v = CV.clv_record(r, c, schedule=sched, as_of=_dt(r["observed_at"]) if r.get("observed_at") else None)
                g["vp"].offer({"prediction_id": r["record_id"], "evaluation_version": CV.CLV_VERSION, "evaluated_at": now.isoformat(), "game_id": gid, "snapshot_id": r.get("snapshot_id"), **v})
                g["n_clv"] += 1
                summary["clv_status"][v["clv_status"]] += 1
        for gid in group:
            g = st[gid]
            cp, vp, idx, cache = g["cp"], g["vp"], g["idx"], g["cache"]
            summary["rows_examined"] += g["n_rows"]
            summary["rows_game_without_kickoff"] += g["n_nokick"]
            for corpus, planner, ver, key in ((close_corpus, cp, CL.CLOSE_RULE_VERSION, "written_closes"), (clv_corpus, vp, CV.CLV_VERSION, "written_clv")):
                if not (planner.new or planner.noop or planner.conflicts):
                    continue
                if planner.conflicts:
                    raise ST.EvaluationConflict(planner.conflicts)
                if not a.dry_run:
                    man = corpus.write_batch(gid, [], evaluation_version=ver, batch=batch, plan=planner.plan())
                    summary[key] += man.get("written", 0)
            summary["games_paired"].append({"game_id": gid, "records": g["n_rows"], "closes": g["n_close"], "clv": g["n_clv"],
                                            "files": len(index.files_for_game(gid)), "close_plan": cp.counts(), "clv_plan": vp.counts(),
                                            "capture_files_read": idx.stats.get("files_read"), "group_size": len(group),
                                            "seconds": round(time.time() - t_group, 1)})
            log(f"  {gid}: {g['n_rows']} records, closes {g['n_close']} (new {cp.counts()['new']}, unchanged {cp.counts()['unchanged']}), "
                f"clv {g['n_clv']} (new {vp.counts()['new']}), status {dict(Counter(c['close_status'] for c in cache.values()))} (rss {_rss_mb():.0f} MB)")
        log(f"group of {len(group)} game(s) done in {time.time() - t_group:.0f}s over {len(group_files)} file(s); "
            f"{budget.elapsed() / 60:.1f} min of the run used")
        del st
    postponed = list(selection.postponed)
    if postponed:
        log(f"::notice::{len(postponed)} kicked-off game(s) postponed to the next run ({selection.reason}): {postponed[:6]}"
            f"{' ...' if len(postponed) > 6 else ''}")
    summary["games_postponed"] = postponed
    summary["postponed_reason"] = selection.reason

    def write_outputs():
        # Written as soon as the games are done and AGAIN at the end: a season pass that is killed must not take the
        # publish gate's inputs with it (the gate reads the last value of each key).
        if a.github_output:
            with open(a.github_output, "a") as f:
                f.write(f"status={'WROTE' if (summary['written_closes'] or summary['written_clv']) else 'NOTHING_TO_DO'}\n"
                        f"written={summary['written_closes'] + summary['written_clv']}\nbatch_id={batch}\n"
                        f"games_paired={len(summary['games_paired'])}\ngames_postponed={len(postponed)}\n"
                        f"index_written={isum['index_files_written']}\n")
    write_outputs()

    # A season market has no kickoff, so the game-style close ("the last complete observation before kickoff")
    # is not merely missing for it -- it is not a meaningful question. Those rows get an explicit
    # CLOSE_NOT_APPLICABLE_SEASON record rather than being dropped, so a researcher can tell "no close exists"
    # from "this row silently left the pipeline". No fake kickoff is invented to make game logic apply.
    #
    # The files are those the index says hold a row without a game, and a snapshot file holds the whole board, so
    # parsing every row of them (the pass was ~17 of the 20 minutes of a run that had NOTHING new to pair) is
    # replaced by a raw-line reject of every line that certainly has both a game and a kickoff. The rows that
    # reject skips are exactly the ones this pass `continue`s over; the informational count of them comes from
    # the index.
    n_na_other = 0
    season_pass_files = index.files_with_no_game_rows()
    summary["rows_season_pass_game_rows"] += sum(g["n"] for p in season_pass_files for g in index.entries[p]["games"].values())
    for r in iter_projections(files=season_pass_files, stats=scan, line_filter=may_lack_game_or_kickoff):
        if r.get("game_id") and r.get("kickoff_utc"):
            continue                                          # belongs to its game pass (already counted from the index)
        if RE.scope_of(r.get("market_family"), r.get("engine")) == RE.SEASON:
            na_planner.offer(not_applicable_row(r, now))
            n_na += 1
        else:
            n_na_other += 1                                   # no game, no kickoff, not a season market: no close question exists
    summary["rows_examined"] += n_na + n_na_other
    summary["rows_no_game_not_season"] = n_na_other
    if na_planner.conflicts:
        raise ST.EvaluationConflict(na_planner.conflicts)
    if n_na and not a.dry_run:
        man = close_corpus.write_batch("SEASON", [], evaluation_version=CL.CLOSE_RULE_VERSION, batch=batch, plan=na_planner.plan())
        summary["written_closes"] += man.get("written", 0)
    summary["close_status"]["CLOSE_NOT_APPLICABLE_SEASON"] = n_na
    summary["season_rows_not_applicable"] = n_na
    summary["season_rows_not_applicable_plan"] = na_planner.counts()
    summary.update(close_status=dict(summary["close_status"]), close_quality=dict(summary["close_quality"]), clv_status=dict(summary["clv_status"]), batch_id=batch,
                   sign_convention=CV.SIGN_CONVENTION, projection_scan=scan.to_dict(), scan_reconciles=scan.reconciles(), index=isum,
                   perf={"seconds": round(time.time() - t0, 1), "max_rss_mb": round(_rss_mb(), 1)}, dry_run=a.dry_run)
    log(json.dumps({k: v for k, v in summary.items() if k != "games_paired"}, indent=1, default=str))
    write_outputs()
    return 0


if __name__ == "__main__":
    sys.exit(main())
