#!/usr/bin/env python3
"""Historical strategy replay CLI: loads the data, runs strategies A-E at an executable ask after fees, writes aggregate results.

    python3 scripts/research/strategy_replay.py                      # full run -> docs/research/strategy_replay_results.json
    python3 scripts/research/strategy_replay.py --dev-only           # prints ONLY the 2025 weeks 1-9 development block; writes nothing

Inputs (all read-only):
  * market-data branch (git ref, blobless clone OK): data/kalshi/backfill/horizons/{0..5}.jsonl  (2025 season, executable top of book),
    data/research/board/2026/board_rows.wk0N.jsonl.gz (2026 weeks 1-5 model-free board table),
    data/shadow/v2/projections/<day>/<snap>.BOARD_V2.projections.jsonl.gz (strategy B)
  * data/raw/nflverse: pbp 2018-2026 and schedules/games.csv   (python3 scripts/data/nflverse_download.py --only pbp,schedules --seasons 2018-2026)
  * config/kalshi_fee_schedule.json

Deterministic: fixed seed, no wall clock in the numbers. Runtime is a few minutes (the engine simulations of strategies D and E dominate).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

import polars as pl  # noqa: E402

import nfl_edge.handicap.expression as EX  # noqa: E402  (injected into the library, which may not import it)
from nfl_edge.data import silver  # noqa: E402
from nfl_edge.execution import fees as F  # noqa: E402
from nfl_edge.research import strategy_replay as SR  # noqa: E402

OUT_JSON = os.path.join(ROOT, "docs", "research", "strategy_replay_results.json")
CACHE = os.path.join(ROOT, "research", "scratch", "strategy_replay")
HORIZON_FILES = [f"data/kalshi/backfill/horizons/{i}.jsonl" for i in range(6)]
BOARD_FILES = [f"data/research/board/2026/board_rows.wk0{i}.jsonl.gz" for i in range(1, 6)]
PROJECTION_LAST_DAY = "2026-10-14"        # BOARD_V2 projections are only needed up to the last 2026 week in the board table


# ------------------------------------------------------------------------------------------------ git helpers
def git_lines(md: str, ref: str, path: str):
    """Stream the lines of a (possibly gzipped) file on the market-data ref without checking it out."""
    p = subprocess.Popen(["git", "-C", md, "show", f"{ref}:{path}"], stdout=subprocess.PIPE)
    stream = gzip.GzipFile(fileobj=p.stdout) if path.endswith(".gz") else p.stdout
    for line in stream:
        line = line.strip()
        if line:
            yield json.loads(line)
    p.wait()
    if p.returncode:
        raise RuntimeError(f"git show {ref}:{path} failed ({p.returncode})")


def git_blob_sha(md: str, ref: str, path: str) -> str:
    out = subprocess.run(["git", "-C", md, "ls-tree", ref, path], capture_output=True, text=True).stdout.split()
    return out[2] if len(out) >= 3 else "unknown"


def fetch_projections(md: str, ref: str, cache_path: str) -> str:
    """Cache the BOARD_V2 game-line projections (compact) once; later runs reuse the file."""
    if os.path.exists(cache_path):
        return cache_path
    files = subprocess.run(["git", "-C", md, "ls-tree", "-r", ref, "--name-only", "data/shadow/v2/projections"], capture_output=True, text=True).stdout.split("\n")
    files = sorted(f for f in files if f.endswith("BOARD_V2.projections.jsonl.gz") and f.split("/")[5] <= PROJECTION_LAST_DAY)

    def one(f):
        out = []
        for r in git_lines(md, ref, f):
            c = SR.compact_projection(r)
            if c:
                out.append(c)
        return out

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with cf.ThreadPoolExecutor(6) as ex, gzip.open(cache_path + ".part", "wt") as w:
        for out in ex.map(one, files):
            for c in out:
                w.write(json.dumps(c) + "\n")
    os.replace(cache_path + ".part", cache_path)
    return cache_path


def build_team_game(seasons, cache_dir):
    path = os.path.join(cache_dir, f"team_game_{seasons[0]}_{seasons[-1]}.parquet")
    pbp_stamp = [os.path.getsize(os.path.join(silver.RAW, "pbp", f"play_by_play_{s}.parquet")) for s in seasons]
    stamp = hashlib.sha256(json.dumps(pbp_stamp).encode()).hexdigest()[:12]
    path = path.replace(".parquet", f"_{stamp}.parquet")
    if os.path.exists(path):
        return pl.read_parquet(path)
    os.makedirs(cache_dir, exist_ok=True)
    tg = pl.concat([silver.team_game_from_pbp(s) for s in seasons], how="diagonal_relaxed")
    tg.write_parquet(path)
    return tg


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------ variants (POST-HOC sensitivity)
def run_variant(boards, ledger, ctx, fn, name):
    settled = []
    for gid in sorted(boards):
        for p in fn(boards[gid], ctx):
            sp = SR.settle_pick(p, ledger.get(gid))
            if sp is not None:
                settled.append(sp)
    ev = SR.evaluate({name: settled}, boards, B=1000, with_tail=False)
    return {blk: {k: ev[blk][name]["ALL"].get(k) for k in ("n_games", "roi", "roi_ci95", "hit_rate", "mean_ask")}
            for blk in (SR.BLOCK_DEV, SR.BLOCK_OOS) if blk in ev}


def sensitivity(boards, ledger, ctx):
    out = {"label": "POST-HOC SENSITIVITY. Evaluated on the same data as the headline numbers, AFTER the pre-registered run. Not used to choose "
                    "anything. Read it as 'how fragile is the headline to the threshold', never as 'the best threshold'.",
           "horizon": SR.PRIMARY_HORIZON, "A_band": {}, "B_min_net_edge": {}, "C_min_gap": {}}
    for band in ((0.50, 0.75), (0.55, 0.80), (0.60, 0.85), (0.65, 0.90), (0.70, 0.90)):
        out["A_band"][f"{band[0]:.2f}-{band[1]:.2f}"] = run_variant(boards, ledger, ctx, lambda b, c, band=band: SR.decide_A(b, c, band=band), "A")
    for edge in (0.02, 0.03, 0.05, 0.08, 0.10):
        out["B_min_net_edge"][f"{edge:.2f}"] = run_variant(boards, ledger, ctx, lambda b, c, e=edge: SR.decide_B(b, c, min_edge=e), "B")
    out["B_incl_PROJECTABLE_NOT_YET_VALIDATED_at_0.05"] = run_variant(
        boards, ledger, ctx, lambda b, c: SR.decide_B(b, c, support=("PRICED", "PROJECTABLE_NOT_YET_VALIDATED")), "B")
    for gap in (1.0, 1.5, 2.5, 3.5, 5.0):
        out["C_min_gap"][f"{gap:.1f}"] = run_variant(boards, ledger, ctx, lambda b, c, g=gap: SR.decide_C(b, c, min_gap=g)["C"], "C")
    return out


def coverage(boards, ledger, sched, stats):
    cov = {"boards": len(boards), "drop_stats": dict(stats), "by_season": {}}
    for season in sorted({b["season"] for b in boards.values()}):
        bs = [b for b in boards.values() if b["season"] == season]
        fam_games = {f: len({b["game_id"] for b in bs if any(r["executable"] and r["family"] == f for r in b["rows"])}) for f in SR.FAMILIES}
        fam_rows = Counter(r["family"] for b in bs for r in b["rows"] if r["executable"])
        all_rows = Counter(r["family"] for b in bs for r in b["rows"])
        cov["by_season"][str(season)] = {"games_with_a_board": len(bs), "games_with_an_executable_row_by_family": fam_games,
                                         "executable_rows_by_family": dict(fam_rows), "rows_by_family": dict(all_rows)}
    return cov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md-repo", default=os.environ.get("MARKET_DATA_REPO", "/tmp/claude-0/data/md"), help="git repo that has the market-data ref")
    ap.add_argument("--md-ref", default="origin/market-data")
    ap.add_argument("--schedule", default=os.path.join(silver.RAW, "schedules", "games.csv"))
    ap.add_argument("--cache-dir", default=CACHE)
    ap.add_argument("--out", default=OUT_JSON)
    ap.add_argument("--draws", type=int, default=SR.FV.DEFAULT_DRAWS)
    ap.add_argument("--dev-only", action="store_true", help="print the 2025 weeks 1-9 development block only; no held-out numbers, no file written")
    ap.add_argument("--skip-sensitivity", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    log = lambda *m: print(f"[{time.time() - t0:6.0f}s]", *m, flush=True)

    sched = SR.read_schedule(a.schedule)
    tg = build_team_game(list(range(2018, 2027)), a.cache_dir)
    rating_book = SR.RatingBook(tg, sched)
    fee_book = SR.FeeBook(F.load_fee_schedule(ROOT))
    proj_path = fetch_projections(a.md_repo, a.md_ref, os.path.join(a.cache_dir, "b_proj.jsonl.gz"))
    projections = SR.ProjectionIndex(SR.read_jsonl(proj_path))
    log("loaded schedule, ratings, fees, projections")

    results = {"horizons": {}, "coverage": {}, "sensitivity": None}
    meta = {
        "replay_version": SR.REPLAY_VERSION, "preregistered": SR.PREREGISTERED,
        "inputs": {"schedule_sha256": sha256_file(a.schedule), "market_data_ref": a.md_ref,
                   "horizon_blobs": {p: git_blob_sha(a.md_repo, a.md_ref, p) for p in HORIZON_FILES},
                   "board_blobs": {p: git_blob_sha(a.md_repo, a.md_ref, p) for p in BOARD_FILES},
                   "projection_cache_sha256": sha256_file(proj_path), "fee_schedule_id": fee_book.schedule.schedule_set_id,
                   "fee_windows": [{"effective_from": w.get("effective_from"), "effective_to": w.get("effective_to")} for w in fee_book.schedule.windows],
                   "engine": {"fairvalue": SR.FV.FAIRVALUE_VERSION, "expression": EX.EXPRESSION_VERSION, "draws": a.draws,
                              "bank_season_lo": SR.FV.BANK_SEASON_LO, "bank_halflife": SR.FV.BANK_HALFLIFE, "bank_seed": SR.FV.BANK_SEED}},
    }
    primary_boards = primary_ledger = primary_ctx = None
    for horizon in (SR.PRIMARY_HORIZON, SR.ROBUSTNESS_HORIZON):
        st25, st26 = {}, {}
        b25, l25 = SR.build_boards_2025((r for i in range(6) for r in git_lines(a.md_repo, a.md_ref, HORIZON_FILES[i])), sched, horizon, st25)
        b26, l26 = SR.build_boards_2026((r for f in BOARD_FILES for r in git_lines(a.md_repo, a.md_ref, f)), horizon, st26)
        boards = {**b25, **b26}
        ledger = SR.merge_ledgers(l25, l26)
        if a.dev_only:
            boards = {g: b for g, b in boards.items() if SR.block_of(b["season"], b["week"]) == SR.BLOCK_DEV}
        log(horizon, "boards", len(b25), "(2025)", len(b26), "(2026)", "in play:", len(boards))
        ctx = SR.Context(fee_book=fee_book, sched=sched, rating_book=rating_book, projections=projections, draws=a.draws, engine=EX)
        res = SR.replay(boards, ledger, ctx, progress=lambda i, n: log(f"  decided {i}/{n}"))
        ev = SR.evaluate(res["picks"], boards)
        if a.dev_only:
            for strat, cells in ev.get(SR.BLOCK_DEV, {}).items():
                for fam, c in cells.items():
                    if c["n_games"]:
                        print(horizon, strat, fam, {k: c.get(k) for k in ("n_games", "roi", "roi_ci95", "hit_rate", "mean_ask")})
            continue
        skip = Counter()
        for d in res["diag"].values():
            skip[str((d.get("DE") or {}).get("skip") or "DECIDED")] += 1
        results["horizons"][horizon] = {"blocks": ev, "unsettled_picks": res["unsettled_picks"], "D_E_outcomes": dict(skip),
                                        "settlement_semantics_check": SR.check_settlement_semantics(boards, ledger, sched)}
        results["coverage"][horizon] = {"2025": coverage(b25, l25, sched, st25), "2026": coverage(b26, l26, sched, st26)}
        if horizon == SR.PRIMARY_HORIZON:
            primary_boards, primary_ledger, primary_ctx = boards, ledger, ctx
        log(horizon, "done")
    if a.dev_only:
        return

    meta["margin_maps"] = {str(s): primary_ctx.margin_map(s) for s in (2025, 2026)}
    meta["information_test"] = SR.information_test(primary_ctx, (2024, 2025, 2026))
    n25 = [g for g in sched.values() if g["season"] == 2025]
    covered = {g for g in primary_boards if g.startswith("2025_")}
    meta["schedule_coverage_2025"] = {"scheduled_games": len(n25), "games_with_kalshi_rows_at_T-90m": len(covered),
                                      "games_without": sorted(g["game_id"] for g in n25 if g["game_id"] not in covered)[:40],
                                      "teams_of_games_without": dict(Counter(t for g in n25 if g["game_id"] not in covered for t in (g["home"], g["away"])).most_common(6))}
    proj_rows = list(SR.read_jsonl(proj_path))
    meta["board_v2"] = {"projection_rows_cached": len(proj_rows), "by_support_state": dict(Counter(r["support_state"] for r in proj_rows)),
                        "by_family": dict(Counter(r["market_family"] for r in proj_rows)),
                        "rows_with_top_of_book_size": sum(1 for r in proj_rows if r.get("yes_ask_size") is not None),
                        "first_generated": min(r["generated_at"] for r in proj_rows), "last_generated": max(r["generated_at"] for r in proj_rows)}
    b_games = {p["game_id"] for s in ("B",) for p in results_picks(primary_boards, primary_ctx)}
    meta["board_v2"]["games_with_a_priced_projection_at_T-90m"] = len(b_games)
    if not a.skip_sensitivity:
        results["sensitivity"] = sensitivity(primary_boards, primary_ledger, primary_ctx)
    results["meta"] = meta
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(results, f, indent=1, sort_keys=True, default=str)
    log("wrote", a.out)


def results_picks(boards, ctx):
    """B's candidate games: every 2026 board with at least one contract that has a PRICED projection at the decision."""
    out = []
    for gid, b in sorted(boards.items()):
        if b["season"] != 2026:
            continue
        if any(ctx.projections.lookup(r["ticker"], b["decision_ts"]) for r in b["rows"] if r["executable"]):
            out.append({"game_id": gid})
    return out


if __name__ == "__main__":
    main()
