#!/usr/bin/env python3
"""RUN NFL report build: resolve the week, call the canonical packet builder, and stamp a vintage manifest.

    python3 scripts/handicap/build_report.py --market-data /tmp/md --out data/handicap_report

This is the operational wrapper the workflows call. It does NOT re-implement the packet: it shells out to
`scripts/handicap/run_nfl.py`, which owns `build_packet` and the canonical renderer, so there is exactly one
code path that can produce a `slate.md` or a `games/<game_id>.md` and no chance of a "simplified" second one
drifting away from it.

What this adds on top:

* **week resolution** -- season/week come from the schedule (see `nfl_edge/data/nfl_calendar.py`) unless the
  caller pins them. Nothing is hard-coded to a week that was current when the workflow was written.
* **a vintage manifest** -- when the report was built, how old the ledger, Kalshi capture and context
  captures were at that moment, the model version, the source SHAs and the minutes to each kickoff. A stale
  report is allowed to exist; a stale report that *looks* current is not.
* **fail closed** -- a missing ledger, a stale ledger past `--max-ledger-age-min`, a nonzero packet build, a
  missing `slate.md`, or fewer game files than the packet has games all exit nonzero, and nothing is
  published. The previous good report stays up wearing its own timestamp.

This command reads no Airtable, writes no Airtable, creates no recommendation and requests no preflight.
It is an evidence generator.

Exit codes
  0 SUCCESS       report built and verified
  5 SKIPPED       no active slate (offseason / kickoffs unpublished); only with --skip-if-no-slate
  2 FAILED        no ledger
  3 FAILED        ledger older than --max-ledger-age-min
  4 FAILED        no ledger rows for the resolved week
  6 FAILED        no active slate and skipping not allowed
  7 FAILED        no schedule readable
  8 FAILED        outputs missing or inconsistent after the build
  9 FAILED        the Kalshi capture the ledger was priced from is older than --max-capture-age-min
 10 FAILED        --require-context-run-id names a capture that failed, is absent, or the packet never read
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.data.nfl_calendar import load_schedule, resolve_active_week  # noqa: E402
from nfl_edge.handicap.report_freshness import (  # noqa: E402
    DEFAULT_MAX_CAPTURE_AGE_MIN, capture_vintage, check_capture_age, check_context_reached_packet,
    check_fresh_context, find_context_run,
)
from nfl_edge.handicap.report_outputs import report_paths, verify_report_outputs  # noqa: E402

RUN_NFL = os.path.join(ROOT, "scripts", "handicap", "run_nfl.py")


def _iso(x):
    if not x:
        return None
    try:
        return datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except ValueError:
        return None


def _age_min(ts, now):
    d = _iso(ts)
    return None if d is None else round((now - d).total_seconds() / 60.0, 1)


def newest_ledger(md_root: str):
    """The newest published ledger snapshot's manifest, without re-reading the (large) observations."""
    obs = sorted(glob.glob(os.path.join(md_root, "data", "shadow", "ledger", "*",
                                        "*.observations.jsonl.gz")))
    if not obs:
        return None, None
    man = obs[-1].replace(".observations.jsonl.gz", ".ledger_manifest.json")
    return obs[-1], (json.load(open(man)) if os.path.exists(man) else {})


def newest_capture(md_root: str, now):
    """Vintage of the newest Kalshi capture run under the market-data tree."""
    mans = sorted(glob.glob(os.path.join(md_root, "data", "kalshi", "capture", "*", "*.manifest.json")))
    if not mans:
        return {"run_id": None, "captured_at": None, "age_min": None,
                "note": "no Kalshi capture found under the market-data tree"}
    try:
        m = json.load(open(mans[-1]))
    except ValueError:
        m = {}
    run_id = m.get("run_id") or os.path.basename(mans[-1]).split(".")[0]
    ts = m.get("finished_at") or m.get("started_at") or m.get("run_at")
    if not ts:
        # run_id is itself a UTC stamp (20260909T060120Z); it is the vintage when nothing better exists.
        try:
            ts = datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            ts = None
    return {"run_id": run_id, "captured_at": ts, "age_min": _age_min(ts, now),
            "quotes_files": len(mans)}


def newest_context(md_root: str, now):
    mans = sorted(glob.glob(os.path.join(md_root, "data", "context", "*", "*.manifest.json")))
    if not mans:
        return {"run_id": None, "captured_at": None, "age_min": None,
                "note": "no context capture found under the market-data tree"}
    run_id = os.path.basename(mans[-1]).split(".")[0]
    try:
        ts = datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        ts = None
    return {"run_id": run_id, "captured_at": ts, "age_min": _age_min(ts, now)}


def git_sha(repo: str, ref: str = "HEAD"):
    r = subprocess.run(["git", "rev-parse", ref], cwd=repo, text=True, capture_output=True)
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser(description="build and verify a RUN NFL handicap report")
    ap.add_argument("--market-data", default="/home/user/_market_data_wt")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "handicap_report"),
                    help="report directory (packet.json, slate.md, games/, manifest.json)")
    ap.add_argument("--season", type=int, default=None, help="pin the season (default: resolve)")
    ap.add_argument("--week", type=int, default=None, help="pin the week (default: resolve)")
    ap.add_argument("--schedule", default=None)
    ap.add_argument("--allow-download", action="store_true")
    ap.add_argument("--max-ledger-age-min", type=float, default=None)
    ap.add_argument("--max-capture-age-min", type=float, default=None,
                    help=("refuse if the Kalshi capture the ledger was PRICED FROM is older than this. A "
                          f"fresh ledger is not a fresh market (default policy {DEFAULT_MAX_CAPTURE_AGE_MIN:.0f}m "
                          "for fresh/horizon builds)"))
    ap.add_argument("--require-context-run-id", default=None,
                    help=("the context capture this run produced. It must exist, must not have failed "
                          "closed, and must be one the packet actually read"))
    ap.add_argument("--max-context-age-min", type=float, default=None,
                    help="refuse if --require-context-run-id is older than this")
    ap.add_argument("--movement-files", type=int, default=None)
    ap.add_argument("--skip-if-no-slate", action="store_true",
                    help="exit 5 (SKIPPED) rather than 6 (FAILED) when there is no active slate")
    ap.add_argument("--focus-game-id", default=None,
                    help="a game to surface in the manifest; the full slate is still built")
    ap.add_argument("--trigger", default="manual",
                    help="what caused this run (manual / shadow-cycle / horizon)")
    ap.add_argument("--horizon-ids", default="", help="comma-separated horizon ids this run satisfies")
    ap.add_argument("--artifact-name", default=None)
    ap.add_argument("--now", default=None)
    ap.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    ap.add_argument("--summary", default=os.environ.get("GITHUB_STEP_SUMMARY"))
    a = ap.parse_args()

    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    run_url = None
    if os.environ.get("GITHUB_SERVER_URL") and os.environ.get("GITHUB_REPOSITORY"):
        run_url = (f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
                   f"/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}")

    # ---- 1. which slate? -----------------------------------------------------------------------
    week_res = None
    if a.season is None or a.week is None:
        try:
            games, src = load_schedule(ROOT, market_data=a.market_data, path=a.schedule,
                                       allow_download=a.allow_download)
        except Exception as e:  # noqa: BLE001
            return _fail(a, 7, "NO_SCHEDULE", f"cannot read the NFL schedule: {e}", now)
        week_res = resolve_active_week(games, now, schedule_source=src)
        if week_res["status"] != "OK":
            code, status = (5, "SKIPPED") if a.skip_if_no_slate else (6, "FAILED")
            return _fail(a, code, status, f"no active slate: {week_res['reason']}", now,
                         week=week_res)
        season, week = week_res["season"], week_res["week"]
    else:
        season, week = a.season, a.week
        # A pinned week still gets its schedule context where the schedule is readable, so the manifest can
        # report minutes-to-kickoff instead of leaving the freshest fact about the report blank.
        try:
            games, src = load_schedule(ROOT, market_data=a.market_data, path=a.schedule,
                                       allow_download=a.allow_download)
            week_res = _pinned_week_context(games, season, week, now, src)
        except Exception:  # noqa: BLE001 -- a pinned run must not fail for want of a schedule
            week_res = {"status": "PINNED", "season": season, "week": week,
                        "reason": "schedule unavailable; season/week were pinned by the caller"}

    print(f"slate: season {season} week {week} "
          f"({(week_res or {}).get('label') or 'pinned by the caller'})")

    # ---- 2. freshness gates, before anything expensive ----------------------------------------
    # These run BEFORE the build so a stale-market or failed-context run costs seconds, and -- more to the
    # point -- so it can never reach the manifest, `latest/`, or a horizon being marked captured.
    ledger_path, ledger_man = newest_ledger(a.market_data)
    cap_vintage = capture_vintage(ledger_man or {}, now)
    if ledger_path is None and a.max_capture_age_min is not None:
        return _fail(a, 2, "FAILED", "no shadow ledger available under the market-data tree", now,
                     week=week_res)
    problem = check_capture_age(cap_vintage, a.max_capture_age_min)
    if problem:
        return _fail(a, 9, "FAILED", problem, now, week=week_res)
    if a.max_capture_age_min is not None:
        print(f"kalshi capture: {cap_vintage['snapshot_run_id']} queried {cap_vintage['queried_at']} "
              f"({cap_vintage['age_min']}m old, limit {a.max_capture_age_min:.0f}m)")

    ctx_required = None
    if a.require_context_run_id:
        problem = check_fresh_context(a.market_data, a.require_context_run_id, now=now,
                                      max_age_min=a.max_context_age_min)
        if problem:
            return _fail(a, 10, "FAILED", problem, now, week=week_res)
        ctx_required = find_context_run(a.market_data, a.require_context_run_id)
        print(f"fresh context: {a.require_context_run_id} present, nothing failed closed")

    # ---- 3. build the packet through the canonical builder -------------------------------------
    out = os.path.abspath(a.out)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out, exist_ok=True)
    cmd = [sys.executable, RUN_NFL, "--market-data", a.market_data,
           "--season", str(season), "--week", str(week), "--out", out]
    if a.max_ledger_age_min is not None:
        cmd += ["--max-ledger-age-min", str(a.max_ledger_age_min)]
    if a.movement_files is not None:
        cmd += ["--movement-files", str(a.movement_files)]
    print("+ " + " ".join(cmd), flush=True)
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    if rc != 0:
        reason = {2: "no shadow ledger available under the market-data tree",
                  3: f"the newest ledger is older than --max-ledger-age-min={a.max_ledger_age_min}",
                  4: f"the ledger has no rows for season {season} week {week}"}.get(
                      rc, f"run_nfl.py exited {rc}")
        return _fail(a, rc if rc in (2, 3, 4) else 8, "FAILED", reason, now, week=week_res)

    # ---- 4. verify the outputs before anything is published ------------------------------------
    packet_path = os.path.join(out, "packet.json")
    if not os.path.exists(packet_path):
        return _fail(a, 8, "FAILED", "packet build produced no packet.json", now, week=week_res)
    with open(packet_path) as f:
        packet = json.load(f)
    problems = verify_report_outputs(out, packet)
    if problems:
        return _fail(a, 8, "FAILED", "incomplete report: " + "; ".join(problems), now, week=week_res)
    game_ids = [g["game_id"] for g in packet["games"]]

    # The build reads the tree itself, so this is where "did the packet actually use this run's fresh
    # capture?" can be answered -- and it is answered before manifest.json exists, so a failure here
    # publishes nothing and marks no horizon.
    problem = check_context_reached_packet(a.require_context_run_id, packet.get("sources"))
    if problem:
        return _fail(a, 10, "FAILED", problem, now, week=week_res)

    # ---- 5. manifest: what this report is made of, and how old each ingredient was -------------
    s = packet["slate_summary"]
    focus = a.focus_game_id if a.focus_game_id in game_ids else None
    manifest = {
        "report_status": "SUCCESS",
        "schema_version": "1.0.0",
        "built_at": now.isoformat(),
        "trigger": a.trigger,
        "handicap_run_id": packet["handicap_run_id"],
        "packet_sha": packet["packet_sha"],
        "packet_schema_version": packet.get("schema_version"),
        "season": season,
        "week": week,
        "season_type": (week_res or {}).get("season_type"),
        "slate_id": (week_res or {}).get("slate_id"),
        "slate_label": (week_res or {}).get("label"),
        "week_resolution": week_res,
        "model_version": (ledger_man or {}).get("model_version") or packet["sources"].get("model_version"),
        "vintages": {
            "shadow_pricing": {
                "ledger_file": os.path.basename(ledger_path) if ledger_path else None,
                "ledger_run_id": (ledger_man or {}).get("run_id"),
                "written_at": (ledger_man or {}).get("written_at"),
                "age_min": _age_min((ledger_man or {}).get("written_at"), now),
                "observations": ((ledger_man or {}).get("counts") or {}).get("written"),
                "snapshot_run_id": (ledger_man or {}).get("snapshot_run_id"),
            },
            # The gated one is `priced_from`: the capture the LEDGER was built on. `newest_in_tree` can be
            # newer and is informational -- pricing did not see it.
            "kalshi_capture": dict(cap_vintage, newest_in_tree=newest_capture(a.market_data, now)),
            "context": dict(newest_context(a.market_data, now),
                            captures_used=packet["sources"].get("context_captures"),
                            fresh_capture_this_run=a.require_context_run_id,
                            fresh_capture_sources=(ctx_required or {}).get("sources")),
            "team_profile_basis": packet["sources"].get("team_profile_basis"),
            "qb_profile_basis": packet["sources"].get("qb_profile_basis"),
        },
        "sources": {
            "main_sha": git_sha(ROOT),
            "market_data_sha": git_sha(a.market_data) if os.path.isdir(a.market_data) else None,
            "workflow": os.environ.get("GITHUB_WORKFLOW"),
            "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
            "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "workflow_run_url": run_url,
        },
        "counts": {
            "games": s["games"],
            "markets_listed": s["markets_listed_slate"],
            "markets_supported": s["markets_supported_slate"],
            "blocking_data_issues": len(s["blocking_data_issues"]),
            "new_or_changed_injuries": len(s["new_or_changed_injuries"]),
            "weather_concerns": len(s["weather_concerns"]),
        },
        "freshness_policy": {
            "max_ledger_age_min": a.max_ledger_age_min,
            "max_capture_age_min": a.max_capture_age_min,
            "max_context_age_min": a.max_context_age_min,
            "required_context_run_id": a.require_context_run_id,
            "note": ("Enforced before publication. A gate that could not reach its evidence refuses; it "
                     "never resolves to 'probably fine'."),
        },
        "blocking_data_issues": s["blocking_data_issues"],
        "kickoffs": [{"game_id": g["game_id"], "kickoff_utc": g["kickoff_utc"],
                      "minutes_to_kickoff": g.get("minutes_to_kickoff"),
                      "game_state": g.get("game_state"),
                      "file": f"games/{g['game_id']}.md"} for g in packet["games"]],
        "minutes_to_first_kickoff": min(
            [g["minutes_to_kickoff"] for g in packet["games"] if g.get("minutes_to_kickoff") is not None],
            default=None),
        "focus_game_id": focus,
        "focus_game_file": f"games/{focus}.md" if focus else None,
        "horizon_ids": [h for h in a.horizon_ids.split(",") if h.strip()],
        "artifact_name": a.artifact_name,
        "files": report_paths(packet),
        "real_money_status": packet["real_money_status"],
        "airtable": "NOT CONTACTED -- report generation neither reads nor writes Airtable",
        "note": ("Evidence only. Model/market differences are labelled DISAGREEMENT ONLY -- REQUIRES "
                 "HANDICAP and are never edges, selections or recommendations."),
    }
    if a.focus_game_id and not focus:
        manifest["focus_game_warning"] = (
            f"{a.focus_game_id} is not on this slate; the full canonical packet was built anyway")
        print(f"::warning::focus game {a.focus_game_id} is not on season {season} week {week}")
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)

    _report(a, manifest, out, now)
    return 0


def _pinned_week_context(games, season, week, now, src):
    """Schedule facts for a caller-pinned season/week, without letting them change the week."""
    from nfl_edge.data.nfl_calendar import season_type_of, week_blocks
    for b in week_blocks(games):
        if b["season"] == season and b["week"] == week and b["season_type"] != "PRE":
            return {"status": "PINNED", "season": season, "week": week,
                    "season_type": b["season_type"], "slate_id": b["slate_id"], "label": b["label"],
                    "schedule_source": src,
                    "first_kickoff_utc": b["first_kickoff"].isoformat() if b["first_kickoff"] else None,
                    "last_kickoff_utc": b["last_kickoff"].isoformat() if b["last_kickoff"] else None,
                    "minutes_to_first_kickoff": (
                        None if not b["first_kickoff"]
                        else round((b["first_kickoff"] - now).total_seconds() / 60.0, 1)),
                    "games_scheduled": b["games_scheduled"],
                    "reason": "season/week pinned by the caller"}
    _ = season_type_of
    return {"status": "PINNED", "season": season, "week": week, "schedule_source": src,
            "reason": "season/week pinned by the caller; the schedule has no such block"}


def _fail(a, code, status, reason, now, week=None):
    print(f"{status}: {reason}", file=sys.stderr)
    payload = {"report_status": status, "reason": reason, "built_at": now.isoformat(),
               "season": (week or {}).get("season"), "week": (week or {}).get("week"),
               "slate_id": (week or {}).get("slate_id"), "trigger": a.trigger,
               "workflow_run_id": os.environ.get("GITHUB_RUN_ID")}
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"report_status={status}\n")
            f.write(f"reason={reason}\n")
            for k in ("season", "week", "slate_id"):
                f.write(f"{k}={payload.get(k) or ''}\n")
            f.write("publish=false\n")
    if a.summary:
        with open(a.summary, "a") as f:
            f.write(f"## RUN NFL — {status}\n\n{reason}\n\n"
                    "Nothing was published; any existing `latest/` report keeps its own timestamp.\n")
    return code


def _lim(x):
    return "none" if x is None else f"{float(x):.0f}m"


def _report(a, m, out, now):
    v = m["vintages"]
    label = m["slate_label"] or f"season {m['season']} week {m['week']}"
    print("\nRUN NFL report SUCCESS")
    print(f"  {label}  "
          f"packet_sha {m['packet_sha']}  run {m['handicap_run_id']}")
    print(f"  games {m['counts']['games']}  markets {m['counts']['markets_listed']}  "
          f"model-supported {m['counts']['markets_supported']}  "
          f"blocking issues {m['counts']['blocking_data_issues']}")
    print(f"  ledger {v['shadow_pricing']['ledger_run_id']} age {v['shadow_pricing']['age_min']}m"
          f"  |  kalshi capture priced from {v['kalshi_capture']['age_min']}m"
          f"  |  context age {v['context']['age_min']}m")
    print(f"  written to {out}")

    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write("report_status=SUCCESS\n")
            f.write("publish=true\n")
            for k, val in (("season", m["season"]), ("week", m["week"]),
                           ("slate_id", m["slate_id"]), ("packet_sha", m["packet_sha"]),
                           ("handicap_run_id", m["handicap_run_id"]),
                           ("games", m["counts"]["games"]),
                           ("markets_listed", m["counts"]["markets_listed"]),
                           ("markets_supported", m["counts"]["markets_supported"]),
                           ("artifact_name", m["artifact_name"] or ""),
                           ("report_dir", out)):
                f.write(f"{k}={val if val is not None else ''}\n")
            f.write(f"week_padded={m['week']:02d}\n")

    if a.summary:
        sp, kc, ctx = v["shadow_pricing"], v["kalshi_capture"], v["context"]
        lines = [
            "## RUN NFL — SUCCESS", "",
            f"**{label}**  ·  "
            f"trigger `{m['trigger']}`  ·  built `{m['built_at']}`", "",
            "| field | value |", "|---|---|",
            f"| status | **SUCCESS** |",
            f"| season / week | {m['season']} / {m['week']} ({m['season_type'] or 'REG'}) |",
            f"| report run id | `{m['handicap_run_id']}` |",
            f"| workflow run | {m['sources']['workflow_run_id'] or 'n/a'} |",
            f"| packet sha | `{m['packet_sha']}` |",
            f"| main sha | `{(m['sources']['main_sha'] or '')[:12]}` |",
            f"| market-data sha | `{(m['sources']['market_data_sha'] or '')[:12]}` |",
            f"| model version | `{m['model_version']}` |",
            f"| shadow-pricing vintage | {sp['written_at']} ({sp['age_min']}m old) |",
            f"| Kalshi capture priced from | {kc['queried_at']} "
            f"(**{kc['age_min']}m** old, limit {_lim(m['freshness_policy']['max_capture_age_min'])}) |",
            f"| newest Kalshi capture in tree | {(kc.get('newest_in_tree') or {}).get('captured_at')} "
            f"({(kc.get('newest_in_tree') or {}).get('age_min')}m old) |",
            f"| context vintage | {ctx['captured_at']} ({ctx['age_min']}m old) |",
            f"| fresh context this run | {ctx.get('fresh_capture_this_run') or 'not required'} |",
            f"| minutes to first kickoff | {m['minutes_to_first_kickoff']} |",
            f"| games | {m['counts']['games']} |",
            f"| markets listed | {m['counts']['markets_listed']} |",
            f"| markets model-supported | {m['counts']['markets_supported']} |",
            f"| blocking data-health issues | {m['counts']['blocking_data_issues']} |",
            f"| artifact | `{m['artifact_name'] or 'n/a'}` |",
            f"| horizons captured | {', '.join(m['horizon_ids']) or 'n/a'} |",
            "",
        ]
        if m["blocking_data_issues"]:
            lines += ["### Blocking data-health issues", ""]
            for b in m["blocking_data_issues"][:20]:
                lines.append(f"* `{b.get('game_id')}` — {b.get('flag')}: {b.get('detail')}")
            lines.append("")
        lines += ["### Game files", ""]
        for k in m["kickoffs"]:
            mark = "  ← **focus**" if k["game_id"] == m["focus_game_id"] else ""
            lines.append(f"* `{k['file']}` — kickoff {k['kickoff_utc']} "
                         f"(T-{k['minutes_to_kickoff']}m, {k['game_state']}){mark}")
        lines += ["", "_Evidence only. Every model/market difference is labelled "
                  "`DISAGREEMENT ONLY -- REQUIRES HANDICAP`. Nothing here is a bet, a recommendation or a "
                  "real-money authority, and no Airtable call is made on this path._", ""]
        with open(a.summary, "a") as f:
            f.write("\n".join(lines))
    _ = now


if __name__ == "__main__":
    sys.exit(main())
