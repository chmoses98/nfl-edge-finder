#!/usr/bin/env python3
"""Freeze the anatomy of every incumbent player projection in the ledger snapshot just written.

    python3 scripts/shadow/player_anatomy.py --market-data /tmp/md --ledger-dir data/shadow/ledger \
        --out data/shadow/player_anatomy

Replays the frozen pricer's player path on the same capture (loaders, features, fitted bundle, branch logic --
imported, never modified), records mu / muo / efficiency / family / quantiles / EWMA inputs / availability
branches per supported player-stat row, reproduces the probability and contract value, and reconciles them
with the ledger row within 1e-9. Mismatches are recorded as REPRODUCTION_MISMATCH and never used as autopsy
evidence. Write-once per (prediction, version); an identical rerun is a no-op; a contradiction fails closed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.arms import incumbent_center as IC, player_anatomy as PA           # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                # noqa: E402


def _emit(path, values):
    if not path:
        return
    with open(path, "a") as f:
        for k, v in values.items():
            f.write(f"{k}={v}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--ledger-dir", default=os.path.join(ROOT, "data", "shadow", "ledger"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "player_anatomy"))
    ap.add_argument("--target-season", type=int, default=0)
    ap.add_argument("--model-version", default=PA.MODEL_VERSION_DEFAULT, help="must equal the pricer's --model-version")
    ap.add_argument("--role-features", action="store_true", help="mirror the pricer's flag exactly")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    season = a.target_season or now.year
    t0 = now
    P = IC.frozen_pricer()
    capture_root = os.path.join(a.market_data, "data", "kalshi", "capture")
    quotes, run_ts, _ages, _confirmed = P.load_latest_quotes(capture_root, IC.MAX_QUOTE_AGE_MIN)
    if not quotes:
        print("::error::no capture quotes"); _emit(a.github_output, {"status": "NO_CAPTURE"}); return 2
    run_id = run_ts.strftime("%Y%m%dT%H%M%SZ")
    rows, ledger_file = IC.find_ledger_rows(a.ledger_dir, run_id)
    if rows is None:
        print(f"::error::no incumbent ledger snapshot for capture {run_id} under {a.ledger_dir}; anatomy needs the ledger row to reconcile against")
        _emit(a.github_output, {"status": "NO_LEDGER"}); return 2
    games = pl.read_parquet(os.path.join(ROOT, "data", "silver", "games.parquet"))
    rep = PA.replay_player_models(ROOT, a.market_data, quotes, run_ts, games, season, model_version=a.model_version,
                                  role_features=a.role_features, verbose=lambda m: print(m, flush=True))
    if rep["bundle"] is not None:
        ledger_sha = next((r.get("model_artifact_sha") for r in rows if r.get("family") == "PLAYER_STAT" and r.get("support_state") == "SUPPORTED"), None)
        print(f"bundle {rep['bundle'].version} sha={rep['bundle'].artifact_sha} (ledger rows carry {ledger_sha})", flush=True)
    recs = PA.collect(rows, quotes, rep, run_id=run_id, feature_cutoff=run_ts.isoformat(), now=now)
    by_game = {}
    for r in recs:
        by_game.setdefault(r["game_id"], []).append(r)
    published = os.path.join(a.market_data, "data", "shadow", "player_anatomy")
    corpus = ST.EvaluationCorpus(a.out, read_roots=[published], suffix=PA.SUFFIX)
    written = unchanged = conflicts = 0
    status_counts = Counter(r["anatomy_status"] for r in recs)
    for gid in sorted(by_game):
        plan = corpus.plan(by_game[gid], gid)
        if plan["conflicts"]:
            conflicts += len(plan["conflicts"]); print(f"::error::{gid}: {len(plan['conflicts'])} anatomy conflict(s)"); continue
        unchanged += len(plan["noop"])
        if plan["new"]:
            m = corpus.write_batch(gid, by_game[gid], evaluation_version=PA.ANATOMY_VERSION, batch=run_id, plan=plan,
                                   manifest_extra={"ledger_file": os.path.basename(ledger_file), "capture_run_id": run_id,
                                                   "bundle_artifact_sha": rep["bundle"].artifact_sha if rep["bundle"] else None,
                                                   "role_features_attached": rep["role_features_attached"],
                                                   "availability_sources": rep["availability_sources"],
                                                   "reconcile_tolerance": PA.RECONCILE_TOL})
            written += m.get("written", 0)
    status = "CONFLICT" if conflicts else ("WROTE" if written else "NO_OP")
    print(json.dumps({"run_id": run_id, "rows": len(recs), "by_status": dict(status_counts), "games": len(by_game),
                      "written": written, "unchanged": unchanged, "conflicts": conflicts, "status": status,
                      "seconds": (datetime.now(timezone.utc) - t0).total_seconds()}, indent=1))
    if status_counts.get(PA.MISMATCH):
        print(f"::warning::{status_counts[PA.MISMATCH]} anatomy row(s) did not reproduce the ledger and are marked {PA.MISMATCH}")
    _emit(a.github_output, {"status": status, "run_id": run_id, "written": written, "mismatches": status_counts.get(PA.MISMATCH, 0)})
    return 4 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
