#!/usr/bin/env python3
"""Freeze the three game-centre arms for the ledger snapshot the pricer just wrote.

    python3 scripts/shadow/three_arm_snapshot.py --market-data /tmp/md --ledger-dir data/shadow/ledger \
        --out data/shadow/arms [--run-id 20260910T050820Z] [--n-sims 40000]

Two sources of the CURRENT centre:

  --ledger-dir (default)   the newest LOCAL ledger snapshot the pricer just wrote: its game_env sidecar carries
                           the exact centre every game was priced from, and its rows give the reproduction check
  --from-capture           no ledger snapshot exists (the decision-horizon conductor): the centre is re-derived
                           from the latest capture with the incumbent's own estimator (nfl_edge/arms/incumbent_center)

Either way it rates teams from football data
at the capture cutoff, blends, simulates the three arms on common random numbers, prices the same game
contracts the incumbent priced, accounts for the BET/WATCH/PASS funnel over the whole snapshot, and writes
one immutable three-arm snapshot. An identical rerun is a no-op; a contradictory rerun fails closed (exit 4).

Exit codes: 0 written or no-op, 2 no usable ledger snapshot / sidecar, 3 the snapshot would be a
reconstruction (capture too old, or built after kickoff for every game), 4 conflict with an existing snapshot.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.arms import records as REC, registry as R                             # noqa: E402
from nfl_edge.arms.snapshot import build_snapshot, find_ledger_snapshot             # noqa: E402
from nfl_edge.shadow.funnel import build_funnel                                     # noqa: E402


def _emit(path, values: dict):
    if not path:
        return
    with open(path, "a") as f:
        for k, v in values.items():
            f.write(f"{k}={v}\n")


def load_books(capture_root: str) -> dict:
    """Book summaries per ticker, the same shape price_slate records (depth in dollars per side)."""
    books = {}
    for f in sorted(glob.glob(os.path.join(capture_root, "*", "*.books.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            ob = r.get("orderbook_fp") or {}
            def depth(key):
                try:
                    return sum(float(x[1]) for x in (ob.get(key) or []))
                except (TypeError, ValueError, IndexError):
                    return None
            books[r["ticker"]] = {"book_depth_yes": depth("yes_dollars"), "book_depth_no": depth("no_dollars")}
    return books


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True, help="market-data worktree (capture + books)")
    ap.add_argument("--ledger-dir", default=os.path.join(ROOT, "data", "shadow", "ledger"),
                    help="the LOCAL ledger directory the pricer just wrote into")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "arms"))
    ap.add_argument("--run-id", default="", help="a specific ledger run (default: the newest with a sidecar)")
    ap.add_argument("--target-season", type=int, default=0, help="0 = from the sidecar")
    ap.add_argument("--n-sims", type=int, default=R.N_SIMS)
    ap.add_argument("--artifact", default="", help="DATA_ONLY artifact path (default: research/three_arm/...)")
    ap.add_argument("--now", default="", help="ISO wall clock (testing only)")
    ap.add_argument("--no-funnel", action="store_true")
    ap.add_argument("--from-capture", action="store_true",
                    help="derive the CURRENT centre from the latest capture with the incumbent estimator (no ledger)")
    ap.add_argument("--horizon-ids", default="", help="comma-separated horizon ids to mark captured on success")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args()
    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    t0 = datetime.now(timezone.utc)
    capture_root = os.path.join(a.market_data, "data", "kalshi", "capture")
    if a.from_capture:
        import polars as pl
        from nfl_edge.arms.incumbent_center import game_environment, load_capture_snapshot, observation_like_rows
        from nfl_edge.arms.snapshot import build_bank
        try:
            cap = load_capture_snapshot(capture_root)
        except FileNotFoundError as e:
            print(f"::error::{e}"); _emit(a.github_output, {"status": "NO_CAPTURE"}); return 2
        season = a.target_season or now.year
        games = pl.read_parquet(os.path.join(ROOT, "data", "silver", "games.parquet"))
        bank, _fp = build_bank(games, season, {"residual_bank": {"season_lo": 2016, "halflife_seasons": 3.0}})
        t1 = datetime.now(timezone.utc)
        env = game_environment(cap["quotes"], games, season, bank)
        env.update({"run_id": cap["run_id"], "capture_finished_at": cap["run_ts"].isoformat(),
                    "residual_bank": {"season_lo": 2016, "halflife_seasons": 3.0, "n_pairs": int(len(bank.m))}})
        books = load_books(capture_root)
        ledger = {"observations": None, "rows": observation_like_rows(cap["quotes"], cap["confirmed_series"], env, books),
                  "game_env": env, "manifest": {}, "stem": f"{cap['run_id']}.capture", "run_id": cap["run_id"],
                  "model_version": "incumbent-estimator-rerun"}
        print(f"CURRENT centres re-derived from capture {cap['run_id']} for {len(env['games'])} games in "
              f"{(datetime.now(timezone.utc) - t1).total_seconds():.0f}s", flush=True)
    else:
        try:
            ledger = find_ledger_snapshot(a.ledger_dir, a.run_id or None)
        except FileNotFoundError as e:
            print(f"::error::{e}")
            _emit(a.github_output, {"status": "NO_LEDGER"})
            return 2
        season = a.target_season or int(ledger["game_env"].get("target_season") or now.year)
    print(f"three-arm snapshot for ledger {ledger['stem']} (season {season}, {a.n_sims} sims per arm)", flush=True)
    try:
        snap = build_snapshot(root=ROOT, ledger=ledger, now=now, target_season=season, n_sims=a.n_sims,
                              artifact_path=a.artifact or None)
    except ValueError as e:
        print(f"::error::{e}")
        _emit(a.github_output, {"status": "REFUSED", "reason": str(e)})
        return 3
    funnel = None
    if not a.no_funnel:
        from nfl_edge.execution.fees import load_fee_schedule
        rows = ledger.get("rows")
        if rows is None:
            rows = [json.loads(l) for l in gzip.open(ledger["observations"], "rt")]
        if a.from_capture:
            funnel = None            # the funnel accounts for the incumbent's PRICED snapshot; there is none here
        else:
            books = load_books(capture_root)
            funnel = build_funnel(rows, books, load_fee_schedule(ROOT), as_of=datetime.fromisoformat(snap["observed_at"]),
                                  run_id=ledger["run_id"])
        if funnel is not None:
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
