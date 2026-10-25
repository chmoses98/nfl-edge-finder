#!/usr/bin/env python3
"""NFL Projection Foundation live shadow operation.

    cd research/projection_foundation
    python -m nfl.live.run --archive <checkout of projection-data> --stage all [--dry-run] [--now ISO]

Stages (each idempotent; `all` runs them in order; a failed stage stops the chain and the workflow commits nothing):
  capture   point-in-time availability snapshot (ESPN injuries, Sleeper, nflverse injuries/depth/roster) -> availability/nfl/
  project   frozen-model projections for games that have not started, as-of participation, gate; challenger forecasts and
            the incumbent's (shadow-0.4.0 ledger + anatomy) archived to forecasts/nfl/ (late ones rejected)
  publish   projections/nfl/latest.json (+ timestamped copy when changed) and summary/nfl/latest.json
  results   FINAL results of archived forecasts from nflverse -> outcomes/nfl/ (DNP -> participated False)
  settle    settle-once -> settlements/nfl/, corrections/nfl/
  score     scorecards/nfl/{daily,weekly,season}.{json,md} with segment drift, rung-Brier and participation checks
  guard     pf_core.archive_guard on the archive (additions only in the immutable directories)

--dry-run works on a temporary COPY of the archive: live fetches, real projections, gate, archiving, settle and score all
run, nothing is written to the real archive. Research only: authority is research_only everywhere.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PF_ROOT = os.path.dirname(os.path.dirname(HERE))
REPO_ROOT = os.path.abspath(os.path.join(PF_ROOT, "..", ".."))
if PF_ROOT not in sys.path:
    sys.path.insert(0, PF_ROOT)

import pandas as pd  # noqa: E402

from pf_core import availability as av  # noqa: E402
from pf_core import prospective as pr  # noqa: E402

from nfl import data as D  # noqa: E402
from nfl.live import SPORT  # noqa: E402

STAGES = ["capture", "project", "publish", "results", "settle", "score", "guard"]
VOLATILE = {"generated_utc", "code_sha", "data_asof_utc", "age_minutes", "newest_age_minutes", "built_utc", "build_seconds"}
WORK = os.path.join(D.CACHE, "live_run")


def log(*a):
    print(*a, flush=True)


def now_iso(a) -> str:
    return av.iso(av._ts(a.now)) if a.now else av.iso(datetime.now(timezone.utc))


def _strip(o):
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items() if k not in VOLATILE}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def prepare_archive(archive: str, dry_run: bool) -> tuple[str, str | None]:
    """The directory stages write to. dry-run: a temp copy (with its .git so archive_guard works)."""
    if not dry_run:
        os.makedirs(archive, exist_ok=True)
        return archive, None
    tmp = tempfile.mkdtemp(prefix="pf-nfl-dry-")
    dst = os.path.join(tmp, "archive")
    if os.path.isdir(archive) and os.listdir(archive):
        shutil.copytree(archive, dst, symlinks=True)
    else:
        os.makedirs(dst)
        subprocess.run(["git", "init", "-q", dst], check=True)
    return dst, tmp


def step_summary(md: str):
    p = os.environ.get("GITHUB_STEP_SUMMARY")
    if p:
        with open(p, "a") as f:
            f.write(md + "\n")


def annotate(level: str, msg: str):
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{level}::{msg}", flush=True)
    else:
        print(f"[{level}] {msg}", flush=True)


def _events(a, now):
    sched = D.load_schedule()
    from nfl.live import availability as LA
    return sched, LA.upcoming_events(sched, now, a.horizon_hours)


# ------------------------------------------------------------------------------------------ capture
def stage_capture(a, ctx):
    from nfl.live import availability as LA
    now = ctx["now"]
    offline = None
    if a.offline_espn or a.offline_sleeper:
        offline = {}
        if a.offline_espn:
            rec = json.load(gzip.open(a.offline_espn) if a.offline_espn.endswith(".gz") else open(a.offline_espn))
            offline["espn"] = (rec["payload"], rec["meta"])
        if a.offline_sleeper:
            rec = json.load(open(a.offline_sleeper))
            offline["sleeper"] = (rec["players"], {"retrieved_at": rec["retrieved_at"], "url": LA.SLEEPER_URL})
    res = LA.capture(now, ctx["events"], ctx["archive"], offline=offline, dry_run=False, replay_depth_as_of_now=a.replay_depth)
    obs = res.pop("_observations", [])
    failed = [k for k, v in res["sources"].items() if v.get("state") == "FAILED"]
    for k in failed:
        annotate("warning", f"availability source {k} FAILED: {res['sources'][k].get('error')}")
    if ctx["events"] and not obs:
        raise RuntimeError("availability capture produced no observation at all for upcoming games: " + json.dumps(res["sources"])[:600])
    rows = LA.load_rows(ctx["archive"], now)
    return res, rows


def stage_project(a, ctx, rows):
    from nfl.live import availability as LA, ledger as LG, project as LP, state as ST
    now = ctx["now"]
    events = ctx["events"]
    out: dict = {"events": len(events)}
    stale = os.path.join(WORK, "projection_doc.json")
    if os.path.exists(stale):          # never let a previous run's document be published by this one
        os.remove(stale)
    if not events:
        out["note"] = "no games start inside the horizon: nothing projected, nothing archived"
        return out
    policy = a.state_policy
    S, info = ST.get_state(policy if policy != "reuse-only" else "reuse", path=a.state_path, log=log, allow_fresh=(policy != "reuse-only"))
    out["state"] = info
    summary = json.load(open(os.path.join(PF_ROOT, "results", "summary.json")))
    frozen = json.load(open(os.path.join(PF_ROOT, "results", "nfl_frozen_selection.json")))["families"]
    # coverage of availability over the players we will project
    pf = S["pf"]
    import numpy as np
    in_pop = np.zeros(len(pf), bool)
    for m in S["pops"].values():                 # coverage is over the players we actually project (in at least one family population)
        in_pop |= np.asarray(m, bool)
    fwd = pf[(pf.split == "forward") & pf.game_id.isin({e["event_id"] for e in events}).to_numpy() & in_pop]
    expected: dict[str, list[str]] = {}
    for gid, g in fwd.groupby("game_id"):
        expected[gid] = sorted(set(g.player_id))
    cov = LA.coverage(rows, expected, events, now) if expected else {}
    res = LP.build(S, frozen, summary, now, events, rows, coverage=cov, state_info=info)
    out["build"] = res["stats"]
    out["availability_coverage"] = {k: cov.get(k) for k in ("mean_coverage", "n_events", "participation_status", "participation_certainty")}
    out["_cov_full"] = cov
    if res["doc"] is None:
        return out
    os.makedirs(WORK, exist_ok=True)
    json.dump(res["doc"], open(os.path.join(WORK, "projection_doc.json"), "w"), default=str)
    # incumbent (read-only view of the shadow ledger on market-data)
    inc = {"records": [], "stats": {"skipped": True}}
    try:
        reader = LG.DirReader(a.market_data_dir) if a.market_data_dir else LG.GitReader(REPO_ROOT)
        if not a.market_data_dir and not a.no_incumbent:
            reader.fetch()
        if not a.no_incumbent:
            inc = LG.incumbent_forecasts(reader, now, {e["event_id"] for e in events})
    except Exception as e:  # noqa: BLE001
        inc = {"records": [], "stats": {"error": f"{type(e).__name__}: {str(e)[:300]}"}}
        annotate("warning", f"incumbent ledger unreadable ({inc['stats']['error']}); challenger forecasts are archived without a pair this run")
    out["incumbent"] = inc["stats"]
    ch = res["forecasts"]
    ch = _new_versions(ch, ctx["archive"])
    out["challenger_new_versions"] = len(ch)
    arch = pr.archive_forecasts(ch + inc["records"], ctx["archive"], now_utc=now)
    out["archive"] = {k: v for k, v in arch.items() if k != "paths"}
    return out


def _new_versions(records: list[dict], archive: str) -> list[dict]:
    """Skip a challenger forecast identical (mean, gate, participation) to its latest archived pregame version."""
    if not records:
        return records
    days = sorted({av._ts(r["game_start_utc"]).strftime("%Y-%m-%d") for r in records})
    old = pr.load_forecasts(archive, SPORT, days)
    if old.empty:
        return records
    old = old[old.model_role == "challenger"]
    old = old.sort_values("generated_utc").groupby(["game_id", "entity_id", "family"], as_index=False).tail(1)
    nn = lambda v: None if (v is None or (isinstance(v, float) and v != v)) else v      # noqa: E731  NaN -> None
    last = {(r.game_id, r.entity_id, r.family): (round(float(r.mean), 6), nn(r.gate_status), nn(r.participation)) for r in old.itertuples()}
    keep = []
    for r in records:
        if last.get((r["game_id"], r["entity_id"], r["family"])) == (round(float(r["mean"]), 6), nn(r["gate_status"]), nn(r["participation"])):
            continue
        keep.append(r)
    return keep


# ------------------------------------------------------------------------------------------ publish
def stage_publish(a, ctx):
    out: dict = {}
    doc_p = os.path.join(WORK, "projection_doc.json")
    root = ctx["archive"]
    if os.path.exists(doc_p):
        doc = json.load(open(doc_p))
        pdir = os.path.join(root, "projections", "nfl")
        os.makedirs(pdir, exist_ok=True)
        latest = os.path.join(pdir, "latest.json")
        prev = json.load(open(latest)) if os.path.exists(latest) else None
        same = prev is not None and _strip(prev) == _strip(doc)
        # latest.json only moves forward in time: re-running an older clock (replay, delayed backup cron) must not regress it
        older = prev is not None and av._ts(doc["generated_utc"]) < av._ts(prev["generated_utc"])
        if not same and not older:
            stamp = av._ts(ctx["now"]).strftime("%Y-%m-%dT%H%MZ")
            copy = os.path.join(pdir, f"{stamp}.json.gz")
            if not os.path.exists(copy):       # timestamped copies are write-once; mtime=0 keeps the bytes a pure function of the content
                with open(copy, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
                    gz.write(json.dumps(doc, default=str).encode())
            json.dump(doc, open(latest, "w"), indent=1, default=str)
        out["projections"] = {"changed": not same and not older, "stale_clock_skipped": bool(older), "players": len(doc["players"]), "games": len(doc["games"])}
    else:
        out["projections"] = {"changed": False, "note": "no projection document this run"}
    sdir = os.path.join(root, "summary", "nfl")
    os.makedirs(sdir, exist_ok=True)
    src = os.path.join(PF_ROOT, "results", "summary.json")
    dst = os.path.join(sdir, "latest.json")
    if not os.path.exists(dst) or _strip(json.load(open(src))) != _strip(json.load(open(dst))):
        shutil.copy(src, dst)
        out["summary"] = "updated"
    else:
        out["summary"] = "unchanged"
    return out


# ------------------------------------------------------------------------------------------ results / settle / score / guard
def stage_results(a, ctx):
    from nfl.live import results as RS
    sched = D.load_schedule()
    rows, st = RS.build_outcomes(ctx["archive"], ctx["now"], sched)
    w = pr.archive_outcomes(rows, ctx["archive"], SPORT, now_utc=ctx["now"]) if rows else {"written": 0}
    st["archived"] = {k: v for k, v in w.items() if k != "paths"}
    return st


def stage_settle(a, ctx):
    return pr.settle(ctx["archive"], SPORT, now_utc=ctx["now"])


def stage_score(a, ctx, capture_stats=None):
    from nfl.live import score as SC
    summary = json.load(open(os.path.join(PF_ROOT, "results", "summary.json")))
    cards = SC.build_cards(ctx["archive"], ctx["now"], summary, capture_stats)
    paths = SC.write_cards(cards, ctx["archive"])
    for tag in ("daily", "weekly"):
        step_summary(pr.render_markdown(cards[tag], title=f"NFL projection scorecard ({tag})") + SC.render_nfl_markdown(cards[tag]))
    return {"cards": list(paths), "alerts": {t: [x for x in c["alerts"] if x["status"] in ("WATCH", "ALERT")] for t, c in cards.items()},
            "settled": cards["season"]["settlement"], "capture": cards["season"]["capture"]}


def stage_guard(a, ctx):
    r = subprocess.run([sys.executable, "-m", "pf_core.archive_guard", ctx["archive"]], cwd=PF_ROOT, capture_output=True, text=True)
    print(r.stdout, r.stderr, flush=True)
    if r.returncode != 0:
        raise RuntimeError("archive_guard failed: immutable archive files changed\n" + r.stdout)
    return {"archive_guard": "OK"}


# ------------------------------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--archive", default=os.path.join(PF_ROOT, ".archive"))
    ap.add_argument("--stage", default="all", help="all | comma list of " + ",".join(STAGES))
    ap.add_argument("--now", default=None, help="ISO time (tests/replay); default: the wall clock")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--horizon-hours", type=float, default=120.0)
    ap.add_argument("--state-policy", choices=("fresh", "reuse", "reuse-only"), default="reuse")
    ap.add_argument("--state-path", default=None)
    ap.add_argument("--market-data-dir", default=None, help="plain directory laid out like market-data (tests); default: git")
    ap.add_argument("--no-incumbent", action="store_true")
    ap.add_argument("--offline-espn", default=None)
    ap.add_argument("--offline-sleeper", default=None)
    ap.add_argument("--replay-depth", action="store_true", help="REPLAY ONLY: read the dt-stamped depth-chart file as of --now")
    ap.add_argument("--summary-out", default=None)
    ap.add_argument("--github-output", default=None)
    a = ap.parse_args(argv)
    if a.state_path is None:
        from nfl.live import state as ST
        a.state_path = ST.STATE_FILE
    stages = STAGES if a.stage == "all" else a.stage.split(",")
    now = now_iso(a)
    archive, tmp = prepare_archive(a.archive, a.dry_run)
    ctx = {"now": now, "archive": archive}
    sched, events = _events(a, now)
    ctx["events"] = events
    summary: dict = {"sport": SPORT, "now": now, "dry_run": a.dry_run, "stages": {}, "events": [e["event_id"] for e in events],
                     "authority": "research_only"}
    rows = None
    capture_stats = None
    rc = 0
    t_all = time.time()
    try:
        for st in stages:
            t0 = time.time()
            log(f"=== stage {st} @ {now}{' (dry-run)' if a.dry_run else ''}")
            if st == "capture":
                res, rows = stage_capture(a, ctx)
                res = {k: v for k, v in res.items() if k != "_observations"}
            elif st == "project":
                if rows is None:
                    from nfl.live import availability as LA
                    rows = LA.load_rows(archive, now)
                res = stage_project(a, ctx, rows)
                cov = res.pop("_cov_full", {})
                capture_stats = {"availability_coverage": (res.get("availability_coverage") or {}).get("mean_coverage"),
                                 "participation_status": (res.get("availability_coverage") or {}).get("participation_status"),
                                 "participation_certainty": (res.get("availability_coverage") or {}).get("participation_certainty"),
                                 "newest_capture_age_minutes": {k: v.get("newest_age_minutes") for k, v in (cov.get("events") or {}).items()}}
            elif st == "publish":
                res = stage_publish(a, ctx)
            elif st == "results":
                res = stage_results(a, ctx)
            elif st == "settle":
                res = stage_settle(a, ctx)
            elif st == "score":
                res = stage_score(a, ctx, capture_stats)
            elif st == "guard":
                res = stage_guard(a, ctx)
            else:
                raise SystemExit(f"unknown stage {st}")
            res["seconds"] = round(time.time() - t0, 1)
            summary["stages"][st] = res
            log(json.dumps(res, default=str)[:2500])
    except Exception as e:  # noqa: BLE001
        rc = 1
        summary["failed_stage"] = st
        summary["error"] = f"{type(e).__name__}: {e}"
        traceback.print_exc()
        annotate("error", f"stage {st} failed: {type(e).__name__}: {str(e)[:300]}")
    summary["seconds"] = round(time.time() - t_all, 1)
    summary["archive"] = archive
    if a.summary_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.summary_out)), exist_ok=True)
        json.dump(summary, open(a.summary_out, "w"), indent=1, default=str)
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"state_source={(summary['stages'].get('project', {}).get('state') or {}).get('source') or 'none'}\n")
            f.write(f"failed={'true' if rc else 'false'}\n")
    step_summary(_render_summary(summary))
    if tmp and os.environ.get("KEEP_DRY_ARCHIVE") != "1":
        shutil.rmtree(tmp, ignore_errors=True)
    return rc


def _render_summary(s: dict) -> str:
    L = [f"### NFL live shadow run {s['now']}{' (dry run)' if s['dry_run'] else ''}", "",
         f"Upcoming games in horizon: {len(s['events'])}. Research only.", ""]
    for st, r in s["stages"].items():
        L.append(f"- **{st}** ({r.get('seconds')}s): " + json.dumps({k: v for k, v in r.items() if k not in ("seconds", "cards")}, default=str)[:900])
    if s.get("error"):
        L += ["", f"**FAILED at {s['failed_stage']}**: {s['error']}"]
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
