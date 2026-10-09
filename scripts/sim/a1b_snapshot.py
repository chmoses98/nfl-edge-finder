#!/usr/bin/env python3
"""A1B source snapshots: freeze the candidate pregame inactive source for games about to kick off. RESEARCH_ONLY.

    python3 scripts/sim/a1b_snapshot.py --check-only --existing-from-git origin/market-data [--github-output F]
    python3 scripts/sim/a1b_snapshot.py --existing-from-git origin/market-data --out .

PREREGISTRATION_ADDENDUM_B_A1B.md section B.5. For every post-cutoff game whose kickoff is within 150 minutes (never at
or after kickoff), at most once per 10 minutes, fetch the ESPN core competition document and both competitors'
rosters, and write ONE write-once snapshot with the raw bodies, the HTTP statuses, the source's own headers
(recorded, never trusted), the raw-bytes sha256 and THIS repository's request / retrieval instants -- the only
evidence of when the information was available. A failed fetch is recorded as an OUTAGE, never as an empty list.
stdlib only.
"""
from __future__ import annotations
import argparse, csv, glob, gzip, io, json, os, subprocess, sys
from datetime import datetime, timezone
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.data.nfl_calendar import fetch_schedule_text, kickoff_utc  # noqa: E402
from nfl_edge.sim import a1b as A                                         # noqa: E402


def schedule_games(path: str | None = None) -> list:
    if path and os.path.exists(path):
        text = (gzip.open(path, "rt") if path.endswith(".gz") else open(path)).read()
    else:
        text, _ = fetch_schedule_text(timeout=90, user_agent=A.UA)
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        ko = kickoff_utc(r.get("gameday"), r.get("gametime"))
        if ko is None or not r.get("espn"):
            continue
        out.append({"game_id": r["game_id"], "event_id": str(r["espn"]).split(".")[0], "kickoff_utc": ko,
                    "home_team": r["home_team"], "away_team": r["away_team"]})
    return out


def existing_names(out_root: str, git_ref: str | None) -> list:
    names = [os.path.relpath(p, out_root) for p in glob.glob(os.path.join(out_root, "data", "research", "wave2_a1b", "**", "*.gz"),
                                                             recursive=True)]
    if git_ref:
        r = subprocess.run(["git", "ls-tree", "-r", "--name-only", git_ref, "data/research/wave2_a1b"], cwd=ROOT,
                           capture_output=True, text=True)
        names += r.stdout.split()
    return names


def snapshot_game(game: dict, *, run_id: str, opener=None) -> dict:
    eid = game["event_id"]
    comp = A.fetch(A.COMPETITION_URL.format(eid=eid), opener=opener)
    ids = A.parse_competition(comp.get("body"))
    rosters = {side: A.fetch(A.ROSTER_URL.format(eid=eid, tid=ids[side]), opener=opener) for side in ("home", "away") if side in ids}
    return A.snapshot_document(game, comp, rosters, run_id=run_id)


def write_snapshot(out_root: str, doc: dict) -> str:
    """Write-once: an existing file for the same game and run is refused, never overwritten. A snapshot retrieved at
    or after kickoff is refused outright (never written)."""
    if doc.get("retrieved_at") and A.minutes_to(doc["kickoff_utc"], doc["retrieved_at"]) <= 0:
        raise ValueError(f"{doc['game_id']}: retrieved at or after kickoff -- not a pregame snapshot, not written")
    run = doc["run_id"]
    d = os.path.join(out_root, A.SRC_PREFIX, f"{run[:4]}-{run[4:6]}-{run[6:8]}")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{doc['game_id']}.{run}.a1b_src.json.gz")
    with open(path, "xb") as f:
        f.write(gzip.compress(json.dumps(doc, sort_keys=True).encode(), mtime=0))
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    ap.add_argument("--schedule", default=None)
    ap.add_argument("--existing-from-git", default=None)
    ap.add_argument("--now", default=None)
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--github-output", default=None)
    a = ap.parse_args(argv)
    now = A._ts(a.now) if a.now else datetime.now(timezone.utc)
    games = schedule_games(a.schedule)
    d = A.due(games, now, existing_names(a.out, a.existing_from_git))
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"snapshot={'true' if d['snapshot'] else 'false'}\ncapture={'true' if d['capture'] else 'false'}\n")
    print("due:", json.dumps(d))
    if a.check_only:
        return 0
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    by = {g["game_id"]: g for g in games}
    wrote = []
    for gid in d["snapshot"]:
        doc = snapshot_game(by[gid], run_id=run_id)
        try:
            p = write_snapshot(a.out, doc)
        except (ValueError, FileExistsError) as e:
            print("refused:", e); continue
        wrote.append(p)
        print(gid, {s: (t["reading"]["state"], len(t["reading"]["inactive_espn_ids"]), t["fetch"].get("status"))
                    for s, t in doc["teams"].items()}, "T-%.1f" % (doc["minutes_to_kickoff"] or -1))
    print("wrote", len(wrote))
    return 0


if __name__ == "__main__":
    sys.exit(main())
