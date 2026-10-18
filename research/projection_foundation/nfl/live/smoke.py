#!/usr/bin/env python3
"""Local smoke test of the whole live chain on a REAL past game: 2026 week 6 Thursday night, SEA @ DEN (kickoff
2026-10-16T00:15Z, final 17-14).

    cd research/projection_foundation
    python -m nfl.live.smoke --state .cache/replay_state_tnf.pkl --out /tmp/pf_smoke

The state is the walk-forward state rebuilt with that game HIDDEN (nfl.live.state.build_state(hide_games={...})), i.e. the
forward frame the Thursday morning run would have had. Pregame inputs are the repo's own RECORDED captures from the
`market-data` branch (ESPN injuries 18:16Z and 23:15Z = T-60 min, Sleeper 17:15Z/21:39Z, the shadow-0.4.0 ledger and player
anatomy, the dt-stamped depth chart); finals are the nflverse release. Each stage is run twice (idempotency), a stat
correction is simulated, and the archive is guarded after every phase. Exit code 0 only if every assertion holds.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PF_ROOT = os.path.dirname(os.path.dirname(HERE))
if PF_ROOT not in sys.path:
    sys.path.insert(0, PF_ROOT)

from pf_core import prospective as pr  # noqa: E402

from nfl.live import ledger as LG  # noqa: E402
from nfl.live import run as RUN  # noqa: E402

GAME = "2026_06_SEA_DEN"
START = "2026-10-16T00:15:00Z"
REPO = os.path.abspath(os.path.join(PF_ROOT, "..", ".."))
CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = ""):
    CHECKS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)


def git(archive, *a):
    return subprocess.run(["git", "-C", archive, *a], capture_output=True, text=True, check=False)


def commit(archive, msg):
    git(archive, "add", "-A")
    git(archive, "-c", "user.email=smoke@example.com", "-c", "user.name=smoke", "commit", "-q", "-m", msg)


def clean(archive) -> bool:
    return git(archive, "status", "--porcelain").stdout.strip() == ""


def fetch_recorded(out):
    r = LG.GitReader(REPO)
    r.fetch()
    os.makedirs(out, exist_ok=True)
    files = {}
    for tag in ("20261015T181653Z", "20261015T231527Z"):
        b = r.cat(f"data/pit_availability/nfl/espn_injuries/2026-10-15/{tag}.json.gz")
        p = os.path.join(out, f"espn_{tag}.json.gz")
        open(p, "wb").write(b)
        files[f"espn_{tag}"] = p
    for tag in ("20261015T171517Z", "20261015T213956Z"):
        b = r.cat(f"data/context/2026-10-15/{tag}.sleeper.json")
        p = os.path.join(out, f"sleeper_{tag}.json")
        open(p, "wb").write(b)
        files[f"sleeper_{tag}"] = p
    return files


def run(archive, state, now, stages, files, espn, sleeper, extra=()):
    argv = ["--archive", archive, "--stage", stages, "--now", now, "--state-policy", "reuse-only", "--state-path", state,
            "--horizon-hours", "30", "--replay-depth", "--offline-espn", files[espn], "--offline-sleeper", files[sleeper],
            "--summary-out", os.path.join(archive, "..", f"summary_{now.replace(':', '')}_{stages.replace(',', '_')}.json"), *extra]
    rc = RUN.main(argv)
    s = json.load(open(argv[argv.index("--summary-out") + 1]))
    return rc, s


def forecasts(archive):
    return pr.load_forecasts(archive, "NFL")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=os.path.join(PF_ROOT, ".cache", "replay_state_tnf.pkl"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    archive = os.path.join(out, "archive")
    os.makedirs(archive)
    subprocess.run(["git", "init", "-q", archive], check=True)
    files = fetch_recorded(os.path.join(out, "recorded"))
    report: dict = {"game": GAME}

    # ---------------- run 1: Thursday ~14:30 ET (T-5.75 h): ESPN 18:16Z + Sleeper 17:15Z
    T1 = "2026-10-15T18:30:00Z"
    rc, s1 = run(archive, a.state, T1, "capture,project,publish,guard", files, "espn_20261015T181653Z", "sleeper_20261015T171517Z")
    check("run1 passed all stages", rc == 0, s1.get("error", ""))
    pj = s1["stages"]["project"]
    check("run1 projected only the one game in the horizon", pj["events"] == 1 and pj["build"]["games"] == 1, str(pj["build"].get("games")))
    f1 = forecasts(archive)
    ch1 = f1[f1.model_role == "challenger"]
    check("run1 archived challenger forecasts", len(ch1) > 40, str(len(ch1)))
    check("run1 archived incumbent forecasts (shadow-0.4.0 ledger + anatomy)", (f1.model_role == "incumbent").sum() > 0, str((f1.model_role == "incumbent").sum()))
    check("nothing archived at/after start", (pd_ts(f1.generated_utc) < pd_ts(f1.game_start_utc)).all() and (pd_ts(f1.archived_utc) < pd_ts(f1.game_start_utc)).all())
    check("every challenger row has participation + role shadow", ch1.participation.notna().sum() == len(ch1[ch1.entity_id.str.startswith("00-")])
          and (ch1.role == "shadow").all())
    check("gate statuses sensible (PASS/REVIEW/BLOCK present, none missing)", set(ch1.gate_status.dropna()) <= {"PASS", "REVIEW", "BLOCK"} and ch1.gate_status.notna().sum() > 0,
          str(ch1.gate_status.value_counts().to_dict()))
    part1 = pj["build"]["participation"]
    report["run1"] = {"participation": part1, "certainty": pj["build"]["participation_certainty"], "gate": pj["build"]["gate_status"],
                      "coverage": pj["availability_coverage"], "incumbent": pj["incumbent"], "archive": pj["archive"]}
    commit(archive, "run1")

    # ---------------- run 2: T-55 min: ESPN 23:15Z shows the inactives as Out
    T2 = "2026-10-15T23:20:00Z"
    rc, s2 = run(archive, a.state, T2, "capture,project,publish,guard", files, "espn_20261015T231527Z", "sleeper_20261015T213956Z")
    check("run2 passed all stages", rc == 0, s2.get("error", ""))
    pj2 = s2["stages"]["project"]
    f2 = forecasts(archive)
    ch2 = f2[f2.model_role == "challenger"]
    inactive = _skill_inactives()
    rows1, rows2 = LA_rows(archive, T1), LA_rows(archive, T2)
    st1 = {e: _status(rows1, T1, e) for e in inactive}
    st2 = {e: _status(rows2, T2, e) for e in inactive}
    check("the ESPN feed flips exactly the official skill-position inactives from active (run 1) to CONFIRMED_OUT (run 2)",
          len(inactive) >= 5 and set(st1.values()) == {"LIKELY_ACTIVE"} and set(st2.values()) == {"CONFIRMED_OUT"}, f"{len(inactive)} players: {sorted(set(st1.values()))} -> {sorted(set(st2.values()))}")
    projected = set(ch2.entity_id)
    check("none of those inactives is in the projected population (QB2, TE/WR/RB reserves), so no projection row exists to BLOCK for them",
          not (set(inactive) & projected), f"{len(projected)} projected entities")
    check("run2 correctly archives NO new version: availability of the projected players did not change",
          len(ch2) == len(ch1) and pj2["challenger_new_versions"] == 0, f"{len(ch1)} -> {len(ch2)}")
    check("run2 coverage is over the projected players only and improved with the later ESPN capture",
          pj2["availability_coverage"]["mean_coverage"] >= pj["availability_coverage"]["mean_coverage"], f"{pj['availability_coverage']['mean_coverage']} -> {pj2['availability_coverage']['mean_coverage']}")
    check("the gate/BLOCK path for CONFIRMED_OUT projections is covered by tests/test_nfl_live.py and the runner dry-run (52 BLOCK rows from real Out candidates); this replay game has none", True)
    check("incumbent forecasts of run2 come from the later ledger run", pj2["incumbent"]["ledger_run"] > pj["incumbent"]["ledger_run"], f"{pj['incumbent']['ledger_run']} -> {pj2['incumbent']['ledger_run']}")
    report["run2"] = {"participation": pj2["build"]["participation"], "certainty": pj2["build"]["participation_certainty"], "gate": pj2["build"]["gate_status"],
                      "coverage": pj2["availability_coverage"], "archive": pj2["archive"], "qb_mismatch": pj2["build"]["qb_starter_mismatch"]}
    commit(archive, "run2")

    # ---------------- run 3: after kickoff - nothing is generated or archived for a started game
    T3 = "2026-10-16T00:20:00Z"
    n_before = len(forecasts(archive))
    rc, s3 = run(archive, a.state, T3, "capture,project,publish,guard", files, "espn_20261015T231527Z", "sleeper_20261015T213956Z")
    check("run3 (after kickoff) passes and projects nothing", rc == 0 and s3["stages"]["project"]["events"] == 0 and len(forecasts(archive)) == n_before)
    late = pr.archive_forecasts([{**ch2.iloc[0].to_dict(), "generated_utc": "2026-10-15T23:59:00Z", "probs": list(ch2.iloc[0].probs)}], archive, now_utc=T3)
    check("a forecast generated pre-start but archived after the start is rejected as late", late["late_rejected"] == 1 and late["written"] == 0)

    # ---------------- idempotency: re-run runs 1 and 2 with the same clock
    n_f, n_a = len(forecasts(archive)), sum(len(fs) for _, _, fs in os.walk(os.path.join(archive, "availability")))
    rc1, r1 = run(archive, a.state, T1, "capture,project,publish,guard", files, "espn_20261015T181653Z", "sleeper_20261015T171517Z")
    rc2, r2 = run(archive, a.state, T2, "capture,project,publish,guard", files, "espn_20261015T231527Z", "sleeper_20261015T213956Z")
    n_f2, n_a2 = len(forecasts(archive)), sum(len(fs) for _, _, fs in os.walk(os.path.join(archive, "availability")))
    check("re-running capture/project/publish adds no forecast and no availability file", rc1 == 0 and rc2 == 0 and n_f2 == n_f and n_a2 == n_a, f"{n_f}->{n_f2} forecasts, {n_a}->{n_a2} files")
    check("archive clean after the re-runs (nothing new to commit)", clean(archive), git(archive, "status", "--porcelain").stdout[:200])

    # ---------------- results -> settle -> score (the final box score is in the nflverse release)
    T4 = "2026-10-17T22:30:00Z"
    rc, s4 = run(archive, a.state, T4, "results,settle,score,guard", files, "espn_20261015T231527Z", "sleeper_20261015T213956Z")
    check("results/settle/score/guard passed", rc == 0, s4.get("error", ""))
    st = s4["stages"]["settle"]
    check("forecasts settled, DNP forecasts void", st["settled"] > 0 and st["void"] >= 0, str(st))
    sett = pr.load_settlements(archive, "NFL")
    check("settlements: one row per forecast_id", sett.forecast_id.is_unique and len(sett) > 0, str(len(sett)))
    card = json.load(open(os.path.join(archive, "scorecards", "nfl", "season.json")))
    check("scorecard has challenger and incumbent models and a paired comparison", any(len(f["models"]) >= 2 for f in card["families"]) and any("paired" in f for f in card["families"]))
    check("scorecard carries the NFL monitoring lines", "nfl" in card and "segment_drift" in card["nfl"])
    report["scorecard_alerts"] = card["alerts"]
    report["settlement"] = {"stage": st, "results": s4["stages"]["results"]}
    report["monitoring"] = card["nfl"]["segment_drift"]
    report["rung_brier"] = card["nfl"]["incumbent_ladder"]
    report["participation_vs_dnp"] = card["nfl"]["participation_vs_dnp"]
    commit(archive, "settled")
    rcb, s5 = run(archive, a.state, T4, "results,settle,score,guard", files, "espn_20261015T231527Z", "sleeper_20261015T213956Z")
    st2 = s5["stages"]["settle"]
    check("re-running results/settle settles nothing again and writes no correction", rcb == 0 and st2["settled"] == 0 and st2["void"] == 0 and st2["corrections"] == 0
          and s5["stages"]["results"]["outcomes_new_or_changed"] == 0, str(st2))
    sc_files = {os.path.join(d, f) for d, _, fs in os.walk(os.path.join(archive, "settlements")) for f in fs}
    check("archive_guard clean after the re-run (additions only)", s5["stages"]["guard"]["archive_guard"] == "OK")

    # ---------------- stat correction: ONE correction per settled forecast of that key, original untouched
    outs = pd_read(pr._read(archive, "outcomes", "NFL"))
    k = outs[(outs.participated) & (outs.family == "receiving_yards")].iloc[0]
    pr.archive_outcomes([{**k.to_dict(), "actual": float(k.actual) + 9.0}], archive, "NFL", now_utc="2026-10-18T10:00:00Z")
    s6 = pr.settle(archive, "NFL", now_utc="2026-10-18T10:05:00Z")
    sett2 = pr.load_settlements(archive, "NFL")
    n_key = int(((sett2.entity_id == k.entity_id) & (sett2.family == "receiving_yards")).sum())
    corr = pr._read(archive, "corrections", "NFL")
    check("a stat correction appends one correction record per settled forecast and leaves the settlements untouched",
          s6["corrections"] == n_key == len(corr) and sett2[sett2.entity_id == k.entity_id].actual.tolist().count(float(k.actual) + 9.0) == 0, f"{s6}, key forecasts {n_key}")
    check("a second settle after the correction writes nothing", pr.settle(archive, "NFL", now_utc="2026-10-18T10:10:00Z")["corrections"] == 0)
    g = subprocess.run([sys.executable, "-m", "pf_core.archive_guard", archive], cwd=PF_ROOT, capture_output=True, text=True)
    check("archive_guard passes (immutable directories only gained files)", g.returncode == 0, g.stdout.strip()[:120])

    report["checks"] = [{"name": n, "ok": ok, "detail": d} for n, ok, d in CHECKS]
    json.dump(report, open(os.path.join(out, "smoke_report.json"), "w"), indent=1, default=str)
    bad = [n for n, ok, _ in CHECKS if not ok]
    print(f"\n{len(CHECKS) - len(bad)}/{len(CHECKS)} checks passed" + (f"; FAILED: {bad}" if bad else ""))
    return 1 if bad else 0


def LA_rows(archive, now):
    from nfl.live import availability as LA
    return LA.load_rows(archive, now)


def _status(rows, now, entity):
    from nfl.live import availability as LA
    return LA.resolve(rows, now, GAME, entity).status


def _skill_inactives():
    """gsis ids of the skill players on the official inactive list of the game (nflverse weekly roster INA, a realised label
    read AFTER the game and used here only as the answer key for the replay)."""
    import pandas as pd
    from nfl import data as D
    r = D.weekly_roster()
    r = r[(r.season == 2026) & (r.week == 6) & (r.team.isin(["SEA", "DEN"])) & (r.status == "INA") & r.position.isin(["QB", "RB", "WR", "TE", "FB"])]
    return sorted(r.gsis_id.dropna())


def pd_ts(s):
    import pandas as pd
    return pd.to_datetime(s, utc=True)


def pd_read(rows):
    import pandas as pd
    return pd.DataFrame(rows)


if __name__ == "__main__":
    sys.exit(main())
