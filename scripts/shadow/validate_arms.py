#!/usr/bin/env python3
"""Gate between building three-arm artifacts and publishing them. Nothing reaches `market-data` unchecked.

    python3 scripts/shadow/validate_arms.py [--arms data/shadow/arms] [--evaluations data/shadow/arm_evaluations]
                                            [--autopsy data/shadow/player_autopsy] [--market-data /tmp/md] [--require-rows]

Snapshots: manifest present, sha256 and row content hashes match, no duplicate identity, every prekickoff game
record was OBSERVED and GENERATED before its kickoff, every probability inside [0, 1], the hybrid centre equals
0.70 x current + 0.30 x data-only wherever both exist, DATA_ONLY never carries a market centre source, and a
DATA_ONLY that is unavailable leaves the HYBRID unavailable too (no fallback to the market).
Evaluations / autopsies: batch checksums, no cross-batch contradiction, no post-kickoff close, pregame values
copied verbatim from the snapshot where the snapshot is on disk. And the published ledger/capture must be
byte-identical: the experiment reads them and never writes them.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.arms import evaluation as AE, records as REC, registry as R      # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                            # noqa: E402
from nfl_edge.shadow.player_autopsy import SUFFIX as AUTOPSY_SUFFIX           # noqa: E402


def _dt(s):
    return datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def check_snapshots(root, problems) -> int:
    v = REC.verify_snapshots([root])
    problems.extend(v["problems"])
    n = 0
    for path in REC.snapshot_files([root], "arm_games"):
        for g in REC.read_rows(path):
            n += 1
            rid = g.get("record_id")
            if g.get("prekickoff"):
                ko = g.get("kickoff_at")
                if not ko or _dt(g["observed_at"]) >= _dt(ko) or _dt(g["generated_at"]) >= _dt(ko):
                    problems.append(f"{path}: {rid} is marked prekickoff but was not observed AND generated before kickoff")
                arms = g.get("arms") or {}
                cur, do, hy = arms.get(R.CURRENT) or {}, arms.get(R.DATA_ONLY) or {}, arms.get(R.HYBRID) or {}
                if do.get("uses_market_information") is not False or do.get("center_source") != "football_only":
                    problems.append(f"{path}: {rid} DATA_ONLY is not attested market-free")
                if do.get("status") == R.UNAVAILABLE and hy.get("status") != R.UNAVAILABLE:
                    problems.append(f"{path}: {rid} HYBRID has a value while DATA_ONLY is unavailable (a market fallback)")
                if do.get("projected_home_margin") is not None and hy.get("projected_home_margin") is not None:
                    hm = R.HYBRID_WEIGHT_MARKET * cur["projected_home_margin"] + R.HYBRID_WEIGHT_DATA * do["projected_home_margin"]
                    ht = R.HYBRID_WEIGHT_MARKET * cur["projected_total"] + R.HYBRID_WEIGHT_DATA * do["projected_total"]
                    if abs(hm - hy["projected_home_margin"]) > 1e-9 or abs(ht - hy["projected_total"]) > 1e-9:
                        problems.append(f"{path}: {rid} HYBRID is not the preregistered 0.70/0.30 blend")
                if (g.get("simulation") or {}).get("n_sims") != R.N_SIMS:
                    problems.append(f"{path}: {rid} simulated {(g.get('simulation') or {}).get('n_sims')} rows, not {R.N_SIMS}")
            elif g.get("status") not in (R.POST_KICKOFF_EXCLUDED, R.UNAVAILABLE):
                problems.append(f"{path}: {rid} is not prekickoff yet has status {g.get('status')}")
            elif g.get("arms"):
                problems.append(f"{path}: {rid} is excluded yet carries arm forecasts")
    for path in REC.snapshot_files([root], "arm_contracts"):
        for c in REC.read_rows(path):
            for k in ("p_current", "p_data_only", "p_hybrid", "cv_current", "cv_data_only", "cv_hybrid"):
                v = c.get(k)
                if v is not None and not (0.0 <= float(v) <= 1.0):
                    problems.append(f"{path}: {c.get('record_id')} {k}={v} outside [0, 1]")
            if c.get("kickoff_at") and _dt(c["observed_at"]) >= _dt(c["kickoff_at"]):
                problems.append(f"{path}: {c.get('record_id')} contract observed after kickoff")
    return n


def check_evaluations(root, problems, snapshot_roots) -> int:
    n = 0
    for suffix in (AE.GAME_SUFFIX, AE.CONTRACT_SUFFIX):
        v = ST.verify_batches([root], suffix=suffix)
        problems.extend(v["problems"])
    snaps = {**REC.load_records(snapshot_roots, "arm_games"), **REC.load_records(snapshot_roots, "arm_contracts")} if snapshot_roots else {}
    for path in sorted(glob.glob(os.path.join(root, "*", f"*.{AE.GAME_SUFFIX}.jsonl.gz"))):
        for r in ST.read_rows(path):
            n += 1
            src = snaps.get(r.get("prediction_id"))
            if src:
                for arm, a in (r.get("arms") or {}).items():
                    s = (src.get("arms") or {}).get(arm) or {}
                    if a.get("projected_home_margin") != s.get("projected_home_margin") or a.get("projected_total") != s.get("projected_total"):
                        problems.append(f"{path}: {r['prediction_id']} {arm} centre differs from the immutable snapshot")
            cl = r.get("close") or {}
            if cl.get("status") in ("OK", "OK_STALE") and cl.get("latest_quote_observed_ts") and r.get("kickoff_at"):
                if float(cl["latest_quote_observed_ts"]) >= _dt(r["kickoff_at"]).timestamp():
                    problems.append(f"{path}: {r['prediction_id']} closing centre uses a quote at or after kickoff")
    for path in sorted(glob.glob(os.path.join(root, "*", f"*.{AE.CONTRACT_SUFFIX}.jsonl.gz"))):
        for r in ST.read_rows(path):
            n += 1
            if r.get("close_status") in ("OK", "OK_STALE") and r.get("close_observed_at") and r.get("kickoff_at"):
                if _dt(r["close_observed_at"]) >= _dt(r["kickoff_at"]):
                    problems.append(f"{path}: {r['prediction_id']} close observed at or after kickoff")
            if r.get("settlement_status") == "SETTLED" and r.get("settled_yes") is None:
                problems.append(f"{path}: {r['prediction_id']} SETTLED without a payout")
            if r.get("settlement_status") != "SETTLED" and r.get("settled_yes") is not None:
                problems.append(f"{path}: {r['prediction_id']} refused yet carries a payout")
            src = snaps.get(r.get("prediction_id"))
            if src:
                for k in ("p_current", "p_data_only", "p_hybrid", "cv_current", "cv_data_only", "cv_hybrid"):
                    if r.get(k) != src.get(k):
                        problems.append(f"{path}: {r['prediction_id']} {k} differs from the immutable snapshot")
    return n


def check_autopsy(root, problems) -> int:
    v = ST.verify_batches([root], suffix=AUTOPSY_SUFFIX)
    problems.extend(v["problems"])
    n = 0
    for path in sorted(glob.glob(os.path.join(root, "*", f"*.{AUTOPSY_SUFFIX}.jsonl.gz"))):
        for r in ST.read_rows(path):
            n += 1
            if r.get("classification") == "AVAILABILITY_MISS" and r.get("played") is True and (r.get("p_plays") or 1) >= 0.5:
                problems.append(f"{path}: {r['prediction_id']} availability miss on a player who played as expected")
    return n


def ledger_untouched(market_data):
    if not market_data:
        return "not_checked", []
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=market_data, capture_output=True, text=True)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return "not_a_git_worktree", []
    r = subprocess.run(["git", "status", "--porcelain", "--", "data/shadow/ledger", "data/kalshi", "data/shadow/evaluations"],
                       cwd=market_data, capture_output=True, text=True)
    dirty = [ln for ln in r.stdout.splitlines() if ln.strip()]
    return ("MODIFIED", [f"the published ledger/capture/evaluation worktree has local modifications: {dirty[:5]}"]) if dirty else ("unmodified", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="")
    ap.add_argument("--evaluations", default="")
    ap.add_argument("--autopsy", default="")
    ap.add_argument("--market-data", default="")
    ap.add_argument("--require-rows", action="store_true")
    a = ap.parse_args()
    problems, n = [], 0
    snapshot_roots = [r for r in ([a.arms] if a.arms else []) + ([REC.arms_root(a.market_data)] if a.market_data else []) if r and os.path.isdir(r)]
    if a.arms and os.path.isdir(a.arms):
        n += check_snapshots(a.arms, problems)
    if a.evaluations and os.path.isdir(a.evaluations):
        n += check_evaluations(a.evaluations, problems, snapshot_roots)
    if a.autopsy and os.path.isdir(a.autopsy):
        n += check_autopsy(a.autopsy, problems)
    state, lp = ledger_untouched(a.market_data)
    problems.extend(lp)
    print(json.dumps({"rows": n, "published_ledger": state, "n_problems": len(problems), "problems": problems[:50], "ok": not problems}, indent=1))
    if a.require_rows and not n:
        print("::error::no three-arm rows found to validate"); return 3
    if problems:
        for p in problems[:20]:
            print(f"::error::{p}")
        return 2
    print(f"validated {n} three-arm rows: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
