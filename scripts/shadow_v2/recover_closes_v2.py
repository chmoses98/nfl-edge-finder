#!/usr/bin/env python3
"""Recover per-game canonical closes (weeks N..M) from `market-data` by fetching ONLY the partitions a close needs.

    python3 scripts/shadow_v2/recover_closes_v2.py plan --weeks 5-8 --season 2026 --schedule data/raw/nflverse/schedules/games.csv
    python3 scripts/shadow_v2/recover_closes_v2.py run  --weeks 5-8 --season 2026 --schedule ... --workdir /mnt/md-window [--dry-run]

Per week: (1) read the week's checkpoint from the branch's TREE METADATA and skip the week if it is complete and
verifies (blob ids, no download); (2) plan the capture days / projection days the week's kicked-off, not-yet-paired games
need from their kickoff times (nfl_edge/shadow/closes_recovery.py); (3) blobless depth-1 fetch + non-cone sparse checkout
of exactly that set; (4) pair_closes_v2.py on those games, in chunks, each chunk audited and published as ONE commit;
(5) when every game of the fully kicked-off week is accounted for, publish the week's checkpoint (append-only, digested).
A dry run does (1)-(4) with nothing written to the branch and says DRY_RUN everywhere; it never makes a checkpoint.

SHADOW / RESEARCH ONLY.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.shadow import closes_recovery as R                                          # noqa: E402

PAIR = os.environ.get("RECOVERY_PAIR_SCRIPT") or os.path.join(ROOT, "scripts", "shadow_v2", "pair_closes_v2.py")
GAME_DONE = re.compile(r"^  (\d{4}_\d{2}_[A-Za-z0-9]+_[A-Za-z0-9]+): \d+ records")
SUBDIRS = [R.CLOSE_DIR, R.CLV_DIR, R.CHECKPOINT_DIR, R.PIDX]


def log(*a):
    print(*a, flush=True)


def _fmt_bytes(n):
    return f"{n / 1e9:.2f} GB" if n >= 1e9 else f"{n / 1e6:.1f} MB"


def estimate(tree_cap_proj: dict, win: R.Window) -> dict:
    """File counts from tree metadata (sizes are unknown without downloading blobs; the fetch measures bytes)."""
    sel = [p for p in tree_cap_proj if R.selected(p, win)]
    return {"selected_files": len(sel), "whole_capture_and_projection_files": len(tree_cap_proj),
            "fraction_of_files": round(len(sel) / len(tree_cap_proj), 4) if tree_cap_proj else None}


def read_checkpoint(repo: str, season: int, week: int, tree: dict):
    path = R.checkpoint_path(season, week)
    if path not in tree:
        return None
    blob = R.git("cat-file", "blob", tree[path][0], cwd=repo).stdout
    try:
        return json.loads(blob)
    except ValueError as e:
        raise R.CheckpointConflict(f"{path} is not valid JSON: {e}") from e


def run_pair(games, *, wt, out, summary_json, now, dry_run, time_budget, log_path):
    cmd = [sys.executable, PAIR, "--market-data", wt, "--out", out, "--no-season-pass", "--summary-json", summary_json,
           "--now", now.isoformat()]
    for g in games:
        cmd += ["--game", g]
    if dry_run:
        cmd.append("--dry-run")
    if time_budget:
        cmd += ["--time-budget-minutes", str(time_budget)]
    done = []
    with open(log_path, "a") as lf:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            lf.write(line)
            m = GAME_DONE.match(line)
            if m:
                done.append(m.group(1))
        rc = p.wait()
    summary = {}
    if os.path.exists(summary_json):
        with open(summary_json) as f:
            summary = json.load(f)
    return rc, done, summary


def process_week(a, week, ctx) -> dict:
    t_week = time.time()
    repo, season, now, dry = a.repo, a.season, ctx["now"], a.dry_run
    games = R.load_week_games(a.schedule, season, week)
    rep = {"week": week, "mode": "DRY_RUN" if dry else "LIVE", "scheduled_games": len(games), "recovered": False}
    if not games:
        rep["status"] = "NO_SCHEDULED_GAMES"
        return rep
    R.fetch_tip(repo)
    tree = R.ls_tree(repo, "origin/market-data", R.CHECKPOINT_DIR, R.CLOSE_DIR, R.CLV_DIR)
    cp = read_checkpoint(repo, season, week, tree)
    if cp is not None:
        problems = R.verify_checkpoint(cp, tree)
        if problems:
            raise R.CheckpointConflict(f"week {week}: checkpoint on the branch does not verify: {problems[:5]}")
        rep.update(status="SKIPPED_COMPLETE", recovered=True, checkpoint_digest=cp["digest_sha256"], batch_id=cp.get("batch_id"),
                   games=len(cp["games"]), seconds=round(time.time() - t_week, 1), bytes_fetched=0)
        log(f"week {week}: checkpoint {cp['digest_sha256'][:12]} verifies against {len(cp['games'])} game(s) on the branch; nothing to fetch")
        return rep

    kicked = [g for g in games if g.kickoff <= now]
    not_kicked = [g for g in games if g.kickoff > now]
    existing = {g.game_id: R.existing_batches(tree, g.game_id) for g in games}
    todo = [g for g in kicked if not existing[g.game_id]["close"]]
    pre = [g for g in kicked if existing[g.game_id]["close"]]
    for g in pre:
        if len(existing[g.game_id]["close"]) > 1:
            raise R.CheckpointConflict(f"{g.game_id}: {len(existing[g.game_id]['close'])} close batches already on the branch: {existing[g.game_id]['close']}")
    rep.update(kicked_off=len(kicked), not_kicked_off=[g.game_id for g in not_kicked], already_paired=[g.game_id for g in pre],
               to_recover=[g.game_id for g in todo])
    log(f"week {week}: {len(games)} scheduled, {len(kicked)} kicked off, {len(pre)} already paired on the branch (left untouched), {len(todo)} to recover")

    game_rec: dict = {}
    for g in pre:
        close_f = existing[g.game_id]["close"][0]
        clv_f = existing[g.game_id]["clv"][-1] if existing[g.game_id]["clv"] else None
        ent = tree[f"{R.CLOSE_DIR}/{g.game_id}/{close_f}"]
        game_rec[g.game_id] = {"status": "PRE_EXISTING", "kickoff_utc": g.kickoff.isoformat(),
                               "close": {"file": close_f, "git_blob_sha1": ent[0]},
                               "clv": ({"file": clv_f, "git_blob_sha1": tree[f"{R.CLV_DIR}/{g.game_id}/{clv_f}"][0]} if clv_f else None)}
    metrics = {"fetch": [], "pair_seconds": 0.0}
    published, no_projection, postponed = [], [], []
    win = None
    if todo:
        win = R.window_for(todo, days_back=a.days_back, proj_lookback=a.proj_lookback)
        big = R.ls_tree(repo, "origin/market-data", R.CAPTURE, R.PROJ)
        est = estimate(big, win)
        first_proj_day = min((p.split("/")[-2] for p in big if p.startswith(R.PROJ + "/")), default=None)
        rep["plan"] = {**win.to_dict(), **est}
        log(f"week {week}: window capture {rep['plan']['capture_days']} projections {rep['plan']['projection_days']}: "
            f"{est['selected_files']} of {est['whole_capture_and_projection_files']} capture+projection files "
            f"({100 * (est['fraction_of_files'] or 0):.1f}%)")
        mat = R.materialise(repo, a.workdir, R.sparse_patterns(win))
        metrics["fetch"].append(mat)
        log(f"week {week}: materialised in {mat['seconds']}s (tree {mat['tree_fetch_seconds']}s, blobs {mat['blob_checkout_seconds']}s); "
            f".git grew {_fmt_bytes(mat['git_dir_bytes_added'])}, worktree {_fmt_bytes(mat['worktree_bytes'])}")
        missing = [p for p in big if R.selected(p, win) and not os.path.exists(os.path.join(a.workdir, p))]
        if missing:
            raise R.RecoveryError(f"week {week}: {len(missing)} planned file(s) are absent after the sparse checkout, e.g. {missing[:3]}")
        chunk = len(todo) if dry else max(1, a.chunk_games)
        t_budget_end = ctx["t_start"] + a.time_budget_minutes * 60 if a.time_budget_minutes else None
        durations = []
        for i in range(0, len(todo), chunk):
            batch = todo[i:i + chunk]
            if t_budget_end and durations and time.time() + 1.3 * max(durations) > t_budget_end:
                postponed += [g.game_id for g in todo[i:]]
                log(f"week {week}: time budget reached; {len(postponed)} game(s) postponed to the next dispatch")
                break
            stage = os.path.join(a.stage, f"wk{week:02d}_{i:03d}")
            shutil.rmtree(stage, ignore_errors=True)
            out = os.path.join(stage, "data", "shadow", "v2")
            os.makedirs(out)
            t0 = time.time()
            rc, _done, summary = run_pair([g.game_id for g in batch], wt=a.workdir, out=out, summary_json=os.path.join(stage, "summary.json"),
                                         now=now, dry_run=dry, time_budget=0, log_path=os.path.join(a.report_dir, f"pair_wk{week:02d}.log"))
            durations.append(time.time() - t0)
            metrics["pair_seconds"] += durations[-1]
            if rc != 0:
                raise R.RecoveryError(f"week {week}: pair_closes_v2 exited {rc}; nothing from this chunk is published or marked complete")
            paired = {p["game_id"]: p for p in summary.get("games_paired", [])}
            for g in batch:
                p = paired.get(g.game_id)
                if p is None:
                    if g.game_id in summary.get("games_without_kickoff", []):
                        no_projection.append(g.game_id)
                        game_rec[g.game_id] = {"status": "NO_PROJECTIONS", "kickoff_utc": g.kickoff.isoformat(),
                                               "note": "no projection row carrying a kickoff names this game in the fetched window; no close is invented"}
                    else:
                        postponed.append(g.game_id)
                    continue
                # the window must have been wide enough: the game must NOT already be on the board on the first day fetched
                lo = win.projection_days[0]
                if p.get("first_file_day") == lo and lo > (first_proj_day or "0000-00-00"):
                    raise R.WindowTooTight(f"{g.game_id} is already on the board on {lo}, the first projection day fetched; widen --proj-lookback")
                rec = {"status": "RECOVERED" if not dry else "DRY_RUN", "kickoff_utc": g.kickoff.isoformat(), "first_projection_day": p.get("first_file_day"),
                       "tickers_by_quality": p.get("tickers_by_quality"), "projection_rows": p.get("records"), "closes": p.get("closes")}
                if not dry:
                    st = R.stage_game(out, g.game_id)
                    if "close" not in st:
                        raise R.RecoveryError(f"{g.game_id}: paired but no close batch was staged")
                    rec.update(close=st["close"], clv=st.get("clv"), rows_by_kind=st["audit"]["rows_by_kind"], tickers_by_kind=st["audit"]["tickers_by_kind"])
                game_rec[g.game_id] = rec
            if not dry:
                staged_ids = [g.game_id for g in batch if game_rec.get(g.game_id, {}).get("status") == "RECOVERED"]
                if staged_ids:
                    res = R.publish_week(repo=repo, stage=stage, subdirs=[R.CLOSE_DIR, R.CLV_DIR, R.PIDX], game_ids=staged_ids,
                                         message=f"shadow v2 closes recovery wk{week:02d}: {len(staged_ids)} game(s) ({R.CL.CLOSE_RULE_VERSION})")
                    log(f"week {week}: chunk published: {res['status']} {res.get('commit', '')[:10]} ({len(staged_ids)} game(s))")
                    published += staged_ids
                shutil.rmtree(stage, ignore_errors=True)
    else:
        log(f"week {week}: nothing to pair")

    rep["metrics"] = metrics
    rep["games"] = game_rec
    rep["no_projections"] = no_projection
    rep["postponed"] = postponed
    accounted = {g.game_id for g in games if game_rec.get(g.game_id, {}).get("status") in ("RECOVERED", "PRE_EXISTING", "NO_PROJECTIONS")}
    week_done = (not not_kicked) and (not postponed) and len(accounted) == len(games) and not dry
    tq = {"TRUE_CLOSE": 0, "EARLIER_QUOTE_PROXY": 0, "MISSING": 0}
    rq = dict(tq)
    for rec in game_rec.values():
        for k, v in (rec.get("tickers_by_kind") or {}).items():
            tq[k] = tq.get(k, 0) + v
        for k, v in (rec.get("rows_by_kind") or {}).items():
            rq[k] = rq.get(k, 0) + v
    rep["tickers_by_kind_recovered"], rep["rows_by_kind_recovered"] = tq, rq
    if dry:
        dq = {"EXCELLENT": 0, "GOOD": 0, "STALE": 0, "MISSING": 0}
        for rec in game_rec.values():
            for k, v in (rec.get("tickers_by_quality") or {}).items():
                dq[k] = dq.get(k, 0) + v
        rep["dry_run_tickers_by_tier"] = dq
        rep["status"] = "DRY_RUN_NOT_RECOVERED"
        log(f"week {week}: DRY_RUN - nothing was written to the branch and nothing is recovered (tiers seen: {dq})")
    elif week_done:
        cp = R.build_checkpoint(season=season, week=week, games=game_rec, window=(win.to_dict() if win else {}), mode="LIVE",
                                batch_id=now.strftime("%Y%m%dT%H%M%SZ"),
                                scope={"capture_days_back": a.days_back, "projection_lookback_days": a.proj_lookback,
                                       "rows": "board snapshots from first listing through the kickoff day; post-kickoff-day snapshots are not paired",
                                       "season_markets": "not part of a windowed recovery"})
        stage = os.path.join(a.stage, f"wk{week:02d}_checkpoint")
        shutil.rmtree(stage, ignore_errors=True)
        cpath = os.path.join(stage, R.checkpoint_path(season, week))
        os.makedirs(os.path.dirname(cpath))
        with open(cpath, "w") as f:
            json.dump(cp, f, indent=1, sort_keys=True)
        res = R.publish_week(repo=repo, stage=stage, subdirs=[R.CHECKPOINT_DIR], game_ids=[],
                             message=f"shadow v2 closes recovery wk{week:02d}: checkpoint {cp['digest_sha256'][:12]}")
        shutil.rmtree(stage, ignore_errors=True)
        rep.update(status="COMPLETE", recovered=True, checkpoint_digest=cp["digest_sha256"], checkpoint_publish=res)
        log(f"week {week}: COMPLETE, checkpoint {cp['digest_sha256'][:12]} published ({res['status']})")
    else:
        rep["status"] = "PARTIAL" if (published or pre) else "NOTHING_RECOVERED"
        rep["recovered"] = False
        why = "not all games kicked off" if not_kicked else ("postponed games" if postponed else "unaccounted games")
        log(f"week {week}: {rep['status']} ({why}); no checkpoint written, a rerun continues from the games still owed")
    rep["recovered_games_published"] = published
    rep["seconds"] = round(time.time() - t_week, 1)
    return rep


def summary_md(reports, mode) -> str:
    lines = [f"### Shadow v2 closes recovery ({'DRY RUN - nothing written or recovered' if mode == 'DRY_RUN' else 'LIVE'})", "",
             "| week | status | games (sched/new/pre-existing) | tickers true / proxy / missing | fetched (.git) | worktree | window selected | seconds |",
             "|---|---|---|---|---|---|---|---|"]
    for r in reports:
        m = r.get("metrics") or {}
        fetched = sum(f["git_dir_bytes_added"] for f in m.get("fetch", []))
        wt = max((f["worktree_bytes"] for f in m.get("fetch", [])), default=0)
        t = r.get("tickers_by_kind_recovered") or {}
        tq = (f"{t.get('TRUE_CLOSE', 0)} / {t.get('EARLIER_QUOTE_PROXY', 0)} / {t.get('MISSING', 0)}" if r["mode"] == "LIVE"
              else f"DRY RUN tiers {r.get('dry_run_tickers_by_tier')}")
        plan = r.get("plan") or {}
        lines.append(f"| {r['week']} | {r.get('status')} | {r.get('scheduled_games')}/{len(r.get('to_recover') or [])}/{len(r.get('already_paired') or [])} | {tq} | "
                     f"{_fmt_bytes(fetched)} | {_fmt_bytes(wt)} | {plan.get('selected_files', 0)} of {plan.get('whole_capture_and_projection_files', 0)} files | {r.get('seconds')} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "run"])
    ap.add_argument("--weeks", required=True)
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--schedule", default=os.path.join(ROOT, "data", "raw", "nflverse", "schedules", "games.csv"))
    ap.add_argument("--repo", default=ROOT)
    ap.add_argument("--workdir", default="/tmp/md-window")
    ap.add_argument("--stage", default="")
    ap.add_argument("--report-dir", default="")
    ap.add_argument("--now", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--chunk-games", type=int, default=8)
    ap.add_argument("--days-back", type=int, default=R.DAYS_BACK)
    ap.add_argument("--proj-lookback", type=int, default=R.PROJ_LOOKBACK)
    ap.add_argument("--time-budget-minutes", type=float, default=0.0, help="do not start another chunk/week that would not fit (0: unbounded)")
    ap.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    ap.add_argument("--summary", default=os.environ.get("GITHUB_STEP_SUMMARY", ""))
    a = ap.parse_args(argv)
    a.stage = a.stage or os.path.join(os.path.dirname(os.path.abspath(a.repo)), "_recovery_stage")
    a.report_dir = a.report_dir or a.stage
    os.makedirs(a.stage, exist_ok=True)
    os.makedirs(a.report_dir, exist_ok=True)
    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    ctx = {"now": now, "t_start": time.time()}
    weeks = R.parse_weeks(a.weeks)
    reports, rc = [], 0
    if a.cmd == "plan":
        R.fetch_tip(a.repo)
        big = R.ls_tree(a.repo, "origin/market-data", R.CAPTURE, R.PROJ)
        for w in weeks:
            games = R.load_week_games(a.schedule, a.season, w)
            win = R.window_for([g for g in games if g.kickoff <= now] or games, days_back=a.days_back, proj_lookback=a.proj_lookback)
            reports.append({"week": w, "games": len(games), **win.to_dict(), **estimate(big, win)})
            log(json.dumps(reports[-1]))
        return 0
    mode = "DRY_RUN" if a.dry_run else "LIVE"
    log(f"mode {mode}; weeks {weeks}; now {now.isoformat()}")
    try:
        for w in weeks:
            spent = [r["seconds"] for r in reports if r.get("seconds") and r.get("status") != "SKIPPED_COMPLETE"]
            if a.time_budget_minutes and spent and time.time() - ctx["t_start"] + 1.3 * max(spent) > a.time_budget_minutes * 60:
                log(f"time budget: week {w} is left for the next dispatch (a week took up to {max(spent):.0f}s)")
                reports.append({"week": w, "mode": mode, "status": "NOT_STARTED_TIME_BUDGET", "recovered": False})
                continue
            reports.append(process_week(a, w, ctx))
    except R.RecoveryError as e:
        log(f"::error::{type(e).__name__}: {e}")
        rc = 1
    finally:
        with open(os.path.join(a.report_dir, "recovery_report.json"), "w") as f:
            json.dump({"mode": mode, "weeks": reports, "elapsed_seconds": round(time.time() - ctx["t_start"], 1)}, f, indent=1, default=str)
        if a.summary and reports:
            with open(a.summary, "a") as f:
                f.write(summary_md(reports, mode))
        if a.github_output:
            done = [r["week"] for r in reports if r.get("recovered")]
            with open(a.github_output, "a") as f:
                f.write(f"mode={mode}\nweeks_complete={','.join(map(str, done))}\n"
                        f"games_recovered={sum(len(r.get('recovered_games_published') or []) for r in reports)}\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
