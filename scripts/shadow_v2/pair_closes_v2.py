#!/usr/bin/env python3
"""Pair every frozen shadow-v2 projection of a kicked-off game with its CANONICAL CLOSE and compute CLV.

    python3 scripts/shadow_v2/pair_closes_v2.py --market-data /tmp/md [--projections <root>]* --out data/shadow/v2 [--game <id>] [--dry-run]

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
from nfl_edge.projection.store import INDEX_DIRNAME, ProjectionIndex, ScanStats, iter_projections  # noqa: E402
from nfl_edge.settlement import reachability as RE                                       # noqa: E402
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
        if not forced and not a.recheck_paired and close_corpus.has_batch(gid, CL.CLOSE_RULE_VERSION) \
                and clv_corpus.has_batch(gid, CV.CLV_VERSION):
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
    na_planner = close_corpus.planner("SEASON")
    n_na = 0
    for gid in examine:
        files = index.files_for_game(gid)
        ko = _dt(games[gid]["kickoff_utc"])
        idx = CL.CloseIndex(capture_root, gid, ko.isoformat(), runs=runs, days_back=a.days_back, openset=oset)
        cp, vp = close_corpus.planner(gid), clv_corpus.planner(gid)
        cache, n_rows, n_close, n_clv, n_nokick = {}, 0, 0, 0, 0
        for r in iter_projections(files=files, game_ids=[gid], stats=scan):
            n_rows += 1
            if not r.get("kickoff_utc"):
                # a game row with no kickoff: nothing to select a close against. A season market carrying a game id
                # still gets its explicit not-applicable record, exactly as one without a game id does.
                if RE.scope_of(r.get("market_family"), r.get("engine")) == RE.SEASON:
                    na_planner.offer(not_applicable_row(r, now))
                    n_na += 1
                else:
                    n_nokick += 1
                continue
            key = r["ticker"]
            if key not in cache:
                cache[key] = idx.select(r["ticker"], series_ticker=r.get("series_ticker"), projection_kickoff_utc=r.get("kickoff_utc"))
            c = cache[key]
            cp.offer({"prediction_id": r["record_id"], "evaluation_version": CL.CLOSE_RULE_VERSION, "evaluated_at": now.isoformat(), "record_id": r["record_id"],
                      "snapshot_id": r.get("snapshot_id"), "model_arm": r.get("model_arm"), "horizon_label": r.get("horizon_label"), **c})
            n_close += 1
            summary["close_status"][c["close_status"]] += 1; summary["close_quality"][c["close_quality"]] += 1
            if r.get("p_yes") is not None:
                v = CV.clv_record(r, c, schedule=sched, as_of=_dt(r["observed_at"]) if r.get("observed_at") else None)
                vp.offer({"prediction_id": r["record_id"], "evaluation_version": CV.CLV_VERSION, "evaluated_at": now.isoformat(), "game_id": gid, "snapshot_id": r.get("snapshot_id"), **v})
                n_clv += 1
                summary["clv_status"][v["clv_status"]] += 1
        summary["rows_examined"] += n_rows
        summary["rows_game_without_kickoff"] += n_nokick
        for corpus, planner, ver, key in ((close_corpus, cp, CL.CLOSE_RULE_VERSION, "written_closes"), (clv_corpus, vp, CV.CLV_VERSION, "written_clv")):
            if not (planner.new or planner.noop or planner.conflicts):
                continue
            if planner.conflicts:
                raise ST.EvaluationConflict(planner.conflicts)
            if not a.dry_run:
                man = corpus.write_batch(gid, [], evaluation_version=ver, batch=batch, plan=planner.plan())
                summary[key] += man.get("written", 0)
        summary["games_paired"].append({"game_id": gid, "records": n_rows, "closes": n_close, "clv": n_clv, "files": len(files),
                                        "close_plan": cp.counts(), "clv_plan": vp.counts(), "capture_files_read": idx.stats.get("files_read")})
        log(f"  {gid}: {n_rows} records, closes {n_close} (new {cp.counts()['new']}, unchanged {cp.counts()['unchanged']}), "
            f"clv {n_clv} (new {vp.counts()['new']}), status {dict(Counter(c['close_status'] for c in cache.values()))} (rss {_rss_mb():.0f} MB)")
        del idx, cp, vp, cache

    # A season market has no kickoff, so the game-style close ("the last complete observation before kickoff")
    # is not merely missing for it -- it is not a meaningful question. Those rows get an explicit
    # CLOSE_NOT_APPLICABLE_SEASON record rather than being dropped, so a researcher can tell "no close exists"
    # from "this row silently left the pipeline". No fake kickoff is invented to make game logic apply.
    n_na_other = 0
    for r in iter_projections(files=index.files_with_no_game_rows(), stats=scan):
        if r.get("game_id") and r.get("kickoff_utc"):
            summary["rows_season_pass_game_rows"] += 1        # belongs to its game pass
            continue
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
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"status={'WROTE' if (summary['written_closes'] or summary['written_clv']) else 'NOTHING_TO_DO'}\nwritten={summary['written_closes'] + summary['written_clv']}\nbatch_id={batch}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
