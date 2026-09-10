#!/usr/bin/env python3
"""Freeze the three game-centre arms for the latest capture snapshot.

    python3 scripts/shadow/three_arm_snapshot.py --market-data /tmp/md [--ledger-dir data/shadow/ledger] \
        --out data/shadow/arms [--n-sims 40000] [--horizon-ids ...]

The CURRENT centre is obtained by REPLAYING the incumbent pricer's own game-environment block on the same
capture (nfl_edge/arms/incumbent_center.py): its loaders, its residual bank and seed, its grid search and
40,000-row simulation, in its call order. The frozen pricer is imported, never modified.

  * with --ledger-dir naming a directory holding the incumbent's ledger snapshot for this capture (the shadow
    cycle, which has just priced it), the replayed simulation is checked against the ledger's prices ticker by
    ticker (`exact_replay_verified`), the incumbent's own numbers are carried on every contract, and the
    BET/WATCH/PASS funnel is accounted over the priced snapshot;
  * without one (the horizon conductor), the replay is `exact_replay_unverified`, the contract universe is the
    capture's rows with the incumbent's support gating mirrored, and no funnel is written.

DATA_ONLY rates teams from football data at the capture cutoff, HYBRID_30 blends, all three are simulated on
common random numbers and price the same contracts, and one immutable snapshot is written. An identical rerun
is a no-op; a contradictory rerun fails closed (exit 4).

Exit codes: 0 written or no-op, 2 no capture, 3 refused as a reconstruction, 4 conflict.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.arms import incumbent_center as IC, records as REC, registry as R      # noqa: E402
from nfl_edge.arms.snapshot import build_snapshot                                    # noqa: E402
from nfl_edge.shadow.funnel import build_funnel                                      # noqa: E402


def _emit(path, values: dict):
    if not path:
        return
    with open(path, "a") as f:
        for k, v in values.items():
            f.write(f"{k}={v}\n")


def book_summaries(books: dict) -> dict:
    """Depth per side, the shape the funnel reads (the frozen pricer's own book_summary is used when present)."""
    P = IC.frozen_pricer()
    return {t: P.book_summary(b) for t, b in books.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True, help="market-data worktree (capture + books)")
    ap.add_argument("--ledger-dir", default="", help="LOCAL ledger directory the pricer just wrote into (optional)")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "arms"))
    ap.add_argument("--target-season", type=int, default=0, help="0 = the wall-clock year")
    ap.add_argument("--n-sims", type=int, default=R.N_SIMS)
    ap.add_argument("--artifact", default="", help="DATA_ONLY artifact path (default: research/three_arm/...)")
    ap.add_argument("--now", default="", help="ISO wall clock (testing only)")
    ap.add_argument("--no-funnel", action="store_true")
    ap.add_argument("--limit-games", type=int, default=0, help="mirror the pricer's own --limit-games (testing only)")
    ap.add_argument("--horizon-ids", default="", help="comma-separated horizon ids to mark captured on success")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args()
    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    t0 = datetime.now(timezone.utc)
    season = a.target_season or now.year
    try:
        rep = IC.replay_game_environment(a.market_data, ROOT, season, limit_games=a.limit_games,
                                         verbose=lambda m: print(m, flush=True))
    except FileNotFoundError as e:
        print(f"::error::{e}")
        _emit(a.github_output, {"status": "NO_CAPTURE"})
        return 2
    env, run_id = rep["env"], rep["run_id"]
    print(f"incumbent replay for capture {run_id}: {len(env['games'])} game environments in "
          f"{(datetime.now(timezone.utc) - t0).total_seconds():.0f}s", flush=True)
    rows, ledger_file = (None, None)
    if a.ledger_dir:
        rows, ledger_file = IC.find_ledger_rows(a.ledger_dir, run_id)
    if rows is None:
        rows = IC.observation_like_rows(rep["quotes"], rep["confirmed_series"], env, rep["books"])
        model_version = "incumbent-replay-unverified"
        print("no incumbent ledger snapshot for this capture: contract universe from the capture, replay unverified", flush=True)
    else:
        model_version = os.path.basename(ledger_file).split(".")[1] if "." in os.path.basename(ledger_file) else "unknown"
        print(f"incumbent ledger snapshot found: {os.path.basename(ledger_file)} ({len(rows)} rows); replay will be verified", flush=True)
    ledger = {"observations": ledger_file, "rows": rows, "game_env": env, "manifest": {}, "stem": f"{run_id}.replay",
              "run_id": run_id, "model_version": model_version, "bank": rep["bank"], "sims": rep["sims"]}
    try:
        snap = build_snapshot(root=ROOT, ledger=ledger, now=now, target_season=season, n_sims=a.n_sims,
                              artifact_path=a.artifact or None)
    except ValueError as e:
        print(f"::error::{e}")
        _emit(a.github_output, {"status": "REFUSED", "reason": str(e)})
        return 3
    funnel = None
    if not a.no_funnel and ledger_file is not None:
        from nfl_edge.execution.fees import load_fee_schedule
        funnel = build_funnel(rows, book_summaries(rep["books"]), load_fee_schedule(ROOT),
                              as_of=datetime.fromisoformat(snap["observed_at"]), run_id=run_id)
        print(f"funnel: {funnel['n_markets']} markets -> " + ", ".join(f"{s['stage']} {s['n']}" for s in funnel["stages"])
              + f" -> {funnel['terminal_states']}", flush=True)
    writer = REC.ArmsWriter(a.out, snap["run_id"])
    try:
        man = writer.write(snap["games"], snap["contracts"],
                           manifest_extra={**snap["manifest_extra"], "seconds": (datetime.now(timezone.utc) - t0).total_seconds()},
                           funnel=funnel)
    except REC.ArmsConflict as e:
        print(f"::error::{e}")
        _emit(a.github_output, {"status": "CONFLICT"})
        return 4
    pre = sum(1 for g in snap["games"] if g.get("prekickoff"))
    if a.horizon_ids and man.get("status") in ("WRITTEN", "NO_OP"):
        from nfl_edge.arms.horizons import write_markers
        for path in write_markers(a.out, a.horizon_ids.split(","), run_id=snap["run_id"], status=man.get("status"), now=now):
            print(f"horizon marker: {os.path.relpath(path, a.out)}")
    print(json.dumps({k: v for k, v in man.items() if k not in ("preregistration", "data_only")}, indent=1, default=str))
    _emit(a.github_output, {"status": man.get("status"), "run_id": snap["run_id"], "games_prekickoff": pre,
                            "contracts": len(snap["contracts"])})
    if pre == 0:
        print("::notice::no game on this snapshot is before kickoff; nothing prospective was recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
