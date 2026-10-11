#!/usr/bin/env python3
"""Evaluate A1B source qualification (PREREGISTRATION_ADDENDUM_B_A1B.md section B.4). RESEARCH_ONLY.

    python3 scripts/sim/a1b_qualify.py --market-data-ref origin/market-data [--out research/game_script_v2/wave2/a1b]

The qualification set is the first 24 post-cutoff games kicking off after the QUALIFICATION START -- amendment B1:
the committer time of the first-parent commit on origin/main that adds the amendment file (the merge that put source
version 1.1.0 on main; read from git, so it cannot be chosen). Addendum B's original instant (the workflow's first
commit) began a 1.0.0 set that the amendment closed with no usable observation. Writes one new JSON file per run (never overwrites) and NEVER edits SOURCE_STATUS.json: recording a
QUALIFIED / BLOCKED decision is addendum C, a separate commit made from this output.
"""
from __future__ import annotations
import argparse, gzip, json, os, subprocess, sys
from datetime import datetime, timezone
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1b_snapshot as SN                                   # noqa: E402
from nfl_edge.sim import a1b as A, a1b_qualify as Q         # noqa: E402

AMENDMENT = "research/game_script_v2/wave2/PREREGISTRATION_AMENDMENT_B1_A1B_SOURCE.md"


def activation_instant(ref: str = "origin/main"):
    r = subprocess.run(["git", "log", "--first-parent", "--diff-filter=A", "--format=%cI", ref, "--", AMENDMENT], cwd=ROOT,
                       capture_output=True, text=True).stdout.split()
    return A._ts(r[-1]) if r else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data-ref", default="origin/market-data")
    ap.add_argument("--main-ref", default="origin/main")
    ap.add_argument("--schedule", default=None)
    ap.add_argument("--rosters", default=os.path.join(ROOT, "data", "raw", "nflverse", "weekly_rosters"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    import pandas as pd
    act = activation_instant(a.main_ref)
    if act is None:
        print("not started: amendment B1 is not on", a.main_ref); return 0
    now = datetime.now(timezone.utc)
    games = sorted((g for g in SN.schedule_games(a.schedule) if g["kickoff_utc"] > act and g["kickoff_utc"] > A._ts(A.PROSPECTIVE_CUTOFF)),
                   key=lambda g: (g["kickoff_utc"], g["game_id"]))[:Q.N_GAMES]
    names = subprocess.run(["git", "ls-tree", "-r", "--name-only", a.market_data_ref, A.SRC_PREFIX], cwd=ROOT,
                           capture_output=True, text=True).stdout.split()
    want = {g["game_id"] for g in games}
    snaps = {}
    for n in names:
        p = A.parse_name(n)
        if p and p[0] == "SRC" and p[1] in want:
            raw = subprocess.run(["git", "show", f"{a.market_data_ref}:{n}"], cwd=ROOT, capture_output=True).stdout
            snaps.setdefault(p[1], []).append(json.loads(gzip.decompress(raw)))
    players = pd.read_parquet(os.path.join(ROOT, "data", "raw", "nflverse", "players", "players.parquet"), columns=["gsis_id", "espn_id"]).dropna()
    gsis_of = {str(e).split(".")[0]: str(g) for g, e in zip(players["gsis_id"], players["espn_id"])}
    truth = {}
    for season in sorted({int(g["game_id"][:4]) for g in games}):
        path = os.path.join(a.rosters, f"roster_weekly_{season}.parquet")
        if not os.path.exists(path):
            continue
        r = pd.read_parquet(path, columns=["team", "week", "status", "gsis_id"])
        for g in games:
            wk = int(g["game_id"].split("_")[1])
            for team in (g["home_team"], g["away_team"]):
                x = r[(r["week"] == wk) & (r["team"] == team)]
                if (x["status"] == "INA").any():                 # published postgame; absent = not yet
                    truth[(g["game_id"], team)] = set(x.loc[x["status"] == "INA", "gsis_id"].dropna().astype(str))
    res = {"qualification_start": act.isoformat(), "source_version": A.SOURCE_VERSION, "evaluated_at": now.isoformat(), **Q.evaluate(games, snaps, truth, gsis_of, now=now)}
    print(json.dumps({k: res[k] for k in ("decision", "rates", "passed") if k in res}))
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        path = os.path.join(a.out, f"qualification_{now.strftime('%Y%m%dT%H%M%SZ')}.json")
        with open(path, "x") as f:
            json.dump(res, f, indent=1, default=str)
        print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
