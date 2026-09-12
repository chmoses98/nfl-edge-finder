#!/usr/bin/env python3
"""Pair every frozen shadow-v2 projection of a kicked-off game with its CANONICAL CLOSE and compute CLV.

    python3 scripts/shadow_v2/pair_closes_v2.py --market-data /tmp/md [--projections <root>]* --out data/shadow/v2 [--game <id>] [--dry-run]

For each game whose kickoff has passed: the close index is built ONCE from the capture (bounded to the game's
days), every projection record of that game (every arm, every horizon, refusals included -- a refusal still
has a market) gets ONE close record and, when it carries a probability, ONE CLV record. Both are written as
write-once batches per game (`closes_v2`, `clv_v2` suffixes) with the same NO_OP / CONFLICT semantics as the
evaluation corpus. The projection files are read, never written. A game whose kickoff is not yet past is skipped:
no close exists before kickoff by definition.
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
from nfl_edge.execution.fees import load_fee_schedule
from nfl_edge.settlement import reachability as RE                                   # noqa: E402
from nfl_edge.projection.store import read_projections                                  # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                      # noqa: E402

CLOSE_SUFFIX, CLV_SUFFIX = "closes_v2", "clv_v2"


def log(*a):
    print(*a, flush=True)


def _dt(s):
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--projections", action="append", default=[])
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2"))
    ap.add_argument("--game", action="append", default=[])
    ap.add_argument("--now", default="")
    ap.add_argument("--days-back", type=int, default=14)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args(argv)
    t0 = time.time()
    now = _dt(a.now) if a.now else datetime.now(timezone.utc)
    roots = a.projections or [os.path.join(a.market_data, "data", "shadow", "v2", "projections")]
    rows = read_projections(roots)
    if a.game:
        rows = [r for r in rows if r.get("game_id") in set(a.game)]
    capture_root = os.path.join(a.market_data, "data", "kalshi", "capture")
    try:
        sched = load_fee_schedule(ROOT)
    except Exception as e:  # noqa: BLE001
        sched = None; log(f"fee schedule unavailable: {e}")
    close_corpus = ST.EvaluationCorpus(os.path.join(a.out, "closes"), read_roots=[os.path.join(a.market_data, "data", "shadow", "v2", "closes")], suffix=CLOSE_SUFFIX)
    clv_corpus = ST.EvaluationCorpus(os.path.join(a.out, "clv"), read_roots=[os.path.join(a.market_data, "data", "shadow", "v2", "clv")], suffix=CLV_SUFFIX)
    batch = ST.batch_id(now)
    # A season market has no kickoff, so the game-style close ("the last complete observation before kickoff")
    # is not merely missing for it -- it is not a meaningful question. Those rows get an explicit
    # CLOSE_NOT_APPLICABLE_SEASON record rather than being dropped, so a researcher can tell "no close exists"
    # from "this row silently left the pipeline". No fake kickoff is invented to make game logic apply.
    by_game, not_applicable = {}, []
    for r in rows:
        if r.get("game_id") and r.get("kickoff_utc"):
            by_game.setdefault(r["game_id"], []).append(r)
        elif RE.scope_of(r.get("market_family"), r.get("engine")) == RE.SEASON:
            not_applicable.append(r)
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
        log(f"open-set ledger: {v['runs']} runs, {v['verified']} hash-verified, {len(v['mismatched'])} mismatched, {len(v['chain_breaks'])} chain breaks")
    summary = {"games_paired": [], "games_skipped_not_kicked_off": [], "written_closes": 0, "written_clv": 0, "close_status": Counter(), "close_quality": Counter(), "clv_status": Counter()}
    for gid in sorted(by_game):
        recs = by_game[gid]
        ko = _dt(recs[0]["kickoff_utc"])
        if now < ko:
            summary["games_skipped_not_kicked_off"].append(gid); continue
        idx = CL.CloseIndex(capture_root, gid, ko.isoformat(), runs=runs, days_back=a.days_back, openset=oset)
        close_rows, clv_rows, cache = [], [], {}
        for r in recs:
            key = r["ticker"]
            if key not in cache:
                cache[key] = idx.select(r["ticker"], series_ticker=r.get("series_ticker"), projection_kickoff_utc=r.get("kickoff_utc"))
            c = cache[key]
            close_rows.append({"prediction_id": r["record_id"], "evaluation_version": CL.CLOSE_RULE_VERSION, "evaluated_at": now.isoformat(), "record_id": r["record_id"],
                               "snapshot_id": r.get("snapshot_id"), "model_arm": r.get("model_arm"), "horizon_label": r.get("horizon_label"), **c})
            summary["close_status"][c["close_status"]] += 1; summary["close_quality"][c["close_quality"]] += 1
            if r.get("p_yes") is not None:
                v = CV.clv_record(r, c, schedule=sched, as_of=_dt(r["observed_at"]) if r.get("observed_at") else None)
                clv_rows.append({"prediction_id": r["record_id"], "evaluation_version": CV.CLV_VERSION, "evaluated_at": now.isoformat(), "game_id": gid, "snapshot_id": r.get("snapshot_id"), **v})
                summary["clv_status"][v["clv_status"]] += 1
        for corpus, out_rows, ver, key in ((close_corpus, close_rows, CL.CLOSE_RULE_VERSION, "written_closes"), (clv_corpus, clv_rows, CV.CLV_VERSION, "written_clv")):
            if not out_rows:
                continue
            plan = corpus.plan(out_rows, gid)
            if plan["conflicts"]:
                raise ST.EvaluationConflict(plan["conflicts"])
            if not a.dry_run:
                man = corpus.write_batch(gid, out_rows, evaluation_version=ver, batch=batch, plan=plan)
                summary[key] += man.get("written", 0)
        summary["games_paired"].append({"game_id": gid, "records": len(recs), "closes": len(close_rows), "clv": len(clv_rows), "capture_files_read": idx.stats.get("files_read")})
        log(f"  {gid}: {len(recs)} records, closes {dict(Counter(c['close_status'] for c in close_rows))}")
    # write the explicit not-applicable closes so season rows stay in the corpus
    if not_applicable and not a.dry_run:
        na_rows = [{"prediction_id": r["record_id"], "evaluation_version": CL.CLOSE_RULE_VERSION,
                    "evaluated_at": now.isoformat(), "record_id": r["record_id"], "snapshot_id": r.get("snapshot_id"),
                    "model_arm": r.get("model_arm"), "horizon_label": r.get("horizon_label"), "ticker": r.get("ticker"),
                    "game_id": None, "close_rule_version": CL.CLOSE_RULE_VERSION,
                    "close_status": "CLOSE_NOT_APPLICABLE_SEASON", "close_quality": "NOT_APPLICABLE",
                    "close_reason": "a season market has no kickoff; the game-style canonical close is not a "
                                    "meaningful question for it and no kickoff is invented to pretend otherwise",
                    "flags": ["SEASON_SCOPED"]} for r in not_applicable]
        plan = close_corpus.plan(na_rows, "SEASON")
        if plan["conflicts"]:
            raise ST.EvaluationConflict(plan["conflicts"])
        man = close_corpus.write_batch("SEASON", na_rows, evaluation_version=CL.CLOSE_RULE_VERSION, batch=batch, plan=plan)
        summary["written_closes"] += man.get("written", 0)
        summary["close_status"]["CLOSE_NOT_APPLICABLE_SEASON"] = len(na_rows)
    summary["season_rows_not_applicable"] = len(not_applicable)
    summary.update(close_status=dict(summary["close_status"]), close_quality=dict(summary["close_quality"]), clv_status=dict(summary["clv_status"]), batch_id=batch,
                   sign_convention=CV.SIGN_CONVENTION, perf={"seconds": time.time() - t0, "max_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0}, dry_run=a.dry_run)
    log(json.dumps({k: v for k, v in summary.items() if k != "games_paired"}, indent=1, default=str))
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"status={'WROTE' if (summary['written_closes'] or summary['written_clv']) else 'NOTHING_TO_DO'}\nwritten={summary['written_closes'] + summary['written_clv']}\nbatch_id={batch}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
