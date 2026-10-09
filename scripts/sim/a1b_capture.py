#!/usr/bin/env python3
"""A1B capture: A0 and A1B on identical rows at a cutoff in (T-80, T-35], from a verified pregame snapshot. RESEARCH_ONLY.

    python3 scripts/sim/a1b_capture.py --market-data /tmp/md --existing-from-git origin/market-data --out .

PREREGISTRATION_ADDENDUM_B_A1B.md. For each post-cutoff game whose kickoff is 35-80 minutes away and has no A1B
record: choose the latest source snapshot RETRIEVED BY THIS REPOSITORY in [T-100, cutoff] with both teams usable
(nfl_edge/sim/a1b.py). With one, simulate A0 (the Wave-2 incumbent, exactly as wave2_prospective.py does: same
bundle, components, input, seed, M0 draws) and A1B (confirmed inactives -> INACTIVE_CONFIRMED, questionable not on
the list -> EXPECTED_ACTIVE) and write one write-once record. Without one, wait while the cutoff is still earlier
than T-45; at or inside T-45 write a NO_USABLE_SOURCE record naming the reason (outage / not published / no
snapshot). A projected player without an ESPN id writes UNUSABLE_IDENTITY. Nothing is ever back-filled.
"""
from __future__ import annotations
import argparse, copy, glob, gzip, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

import wave2_prospective as W2                                  # noqa: E402  (frozen Wave-2 runner: reused, not changed)
import a1b_snapshot as SN                                       # noqa: E402
from nfl_edge.sim import (SIM_VERSION, a1b as A, availability_horizons as AH, data as D, features as F,  # noqa: E402
                          key_numbers as K, prospective as P, simulate as S)

STATUS_FILE = os.path.join(ROOT, "research", "game_script_v2", "wave2", "a1b", "SOURCE_STATUS.json")
N_SIMS = W2.N_SIMS


def _sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def qualification_status() -> dict:
    st = json.load(open(STATUS_FILE))
    return {"status": st["status"], "qualified_at": st.get("qualified_at"), "status_file_sha256": _sha_file(STATUS_FILE)}


def load_snapshots(roots, git_ref, game_id) -> list:
    """Every source snapshot for one game: from local roots and (by name) from a git ref of market-data."""
    out, seen = [], set()
    for root in roots:
        for p in glob.glob(os.path.join(root, A.SRC_PREFIX, "*", f"{game_id}.*.a1b_src.json.gz")):
            raw = open(p, "rb").read()
            rel = os.path.relpath(p, root)
            if rel in seen:
                continue
            seen.add(rel)
            out.append({**json.loads(gzip.decompress(raw)), "_path": rel, "_sha256": hashlib.sha256(raw).hexdigest()})
    if git_ref:
        names = subprocess.run(["git", "ls-tree", "-r", "--name-only", git_ref, A.SRC_PREFIX], cwd=ROOT,
                               capture_output=True, text=True).stdout.split()
        for n in names:
            if os.path.basename(n).startswith(game_id + ".") and n not in seen:
                raw = subprocess.run(["git", "show", f"{git_ref}:{n}"], cwd=ROOT, capture_output=True).stdout
                seen.add(n)
                out.append({**json.loads(gzip.decompress(raw)), "_path": n, "_sha256": hashlib.sha256(raw).hexdigest()})
    return out


def espn_map() -> dict:
    p = pd.read_parquet(os.path.join(ROOT, "data", "raw", "nflverse", "players", "players.parquet"), columns=["gsis_id", "espn_id"])
    p = p.dropna()
    return {str(g): str(e).split(".")[0] for g, e in zip(p["gsis_id"], p["espn_id"])}


def capture(slate, game, cutoff, hist, bundle, season, snaps, espn_of, status) -> dict:
    gid = game["game_id"]
    G = slate["games"].get(gid)
    ko = A._ts(game["kickoff_utc"])
    base = {"game_id": gid, "window": "A1B", "kickoff_utc": ko.isoformat(), "cutoff": cutoff.isoformat(),
            "minutes_to_kickoff": round(A.minutes_to(ko, cutoff), 2), "home_team": game["home_team"],
            "away_team": game["away_team"], "source_qualification": status,
            "snapshots_seen": [{"path": s["_path"], "sha256": s["_sha256"], "retrieved_at": s.get("retrieved_at"),
                                "states": {x: s["teams"][x]["reading"]["state"] for x in ("home", "away")}} for s in snaps]}
    if G is None:
        return {**base, "state": "NOT_IN_SLATE"}
    snap, why = A.choose_snapshot(snaps, cutoff)
    if snap is None:
        return {**base, "state": "NO_USABLE_SOURCE", "reason": why}
    gi = G["input"]
    team_players = {ti.team: [str(p) for p in ti.players["player_id"]] for ti in (gi.home, gi.away)}
    mapped = A.map_inactives(snap, team_players, espn_of)
    src = {"path": snap["_path"], "sha256": snap["_sha256"], "run_id": snap["run_id"], "retrieved_at": snap["retrieved_at"],
           "minutes_to_kickoff": snap["minutes_to_kickoff"], "source": snap["source"],
           "teams": {t: {"inactive_gsis": sorted(v["inactive"]), "unmapped_projected": v["unmapped_projected"], "conflicting_ids": v["conflicting_ids"],
                         "unmatched_inactive": v["unmatched_inactive"]} for t, v in mapped.items()}}
    if not all(v["usable"] for v in mapped.values()):
        return {**base, "state": "UNUSABLE_IDENTITY", "source_used": src}
    inactive = set().union(*(v["inactive"] for v in mapped.values()))
    gin = copy.deepcopy(gi)
    for ti in (gin.home, gin.away):
        ti.players = ti.players.assign(avail_state=A.a1b_states(ti.players["avail_state"], [str(p) for p in ti.players["player_id"]], inactive))
    draws = K.m0_draws(hist, gi.spread_home, gi.total_line, season, N_SIMS, seed=11)
    rec = {**base, "state": "OK", "source_used": src, "centre": {"spread_home": gi.spread_home, "total": gi.total_line,
           "source": gi.center_source}, "arms": {}, "coherence": {},
           "avail_state": {str(p): str(s) for ti in (gi.home, gi.away) for p, s in zip(ti.players["player_id"], ti.players["avail_state"])},
           "a1b_state": {str(p): str(s) for ti in (gin.home, gin.away) for p, s in zip(ti.players["player_id"], ti.players["avail_state"])}}
    for arm, inp in (("A0", gi), ("A1B", gin)):
        res = S.simulate(inp, bundle, n=N_SIMS, seed=11, game_draws={k: draws[k] for k in ("margin", "total", "home", "away")})
        rec["coherence"][arm] = bool(S.coherence_report(res)["ok"])
        rec["arms"][arm] = W2.summarize(res)
    return rec


def write_record(out_root: str, doc: dict, gid: str) -> str:
    run = doc["run_id"]
    d = os.path.join(out_root, A.REC_PREFIX, f"{run[:4]}-{run[4:6]}-{run[6:8]}")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{gid}.A1B.{run}.a1b.json.gz")
    with open(path, "xb") as f:                         # write-once
        f.write(gzip.compress(json.dumps(doc, default=P._json_default).encode(), mtime=0))
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--existing-from-git", default=None)
    ap.add_argument("--out", default=".")
    ap.add_argument("--schedule", default=None)
    ap.add_argument("--cutoff", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    cutoff = A._ts(a.cutoff) if a.cutoff else datetime.now(timezone.utc)
    games = SN.schedule_games(a.schedule)
    names = SN.existing_names(a.out, a.existing_from_git) + SN.existing_names(a.market_data, None)
    todo = A.due(games, cutoff, names)["capture"]
    print("capture due:", todo or "none")
    if not todo:
        return 0
    by = {g["game_id"]: g for g in games}
    status = qualification_status()
    espn_of = espn_map()
    ledger_rows, _, ledger_run = P.latest_ledger(a.market_data, at_or_before=cutoff)
    sched = D.schedule().to_pandas().set_index("game_id")
    for gid in todo:
        game = by[gid]
        season, week = int(sched.loc[gid, "season"]), int(sched.loc[gid, "week"])
        snaps = load_snapshots([a.out, a.market_data], a.existing_from_git, gid)
        snap, why = A.choose_snapshot(snaps, cutoff)
        if snap is None and A.minutes_to(game["kickoff_utc"], cutoff) > A.LAST_CHANCE_MIN:
            print(gid, "no usable snapshot yet:", why, "-- waiting (cutoff earlier than T-45)"); continue
        bpath = os.path.join(ROOT, "research", "simulation_engine", f"bundle_{season}.json")
        bundle = json.load(open(bpath))
        slate = P.slate_inputs(season, week, cutoff, a.market_data, ledger_rows=ledger_rows, priors=F.PriorSet.from_dict(bundle["priors"]))
        rec = capture(slate, game, cutoff, K.history(season - 1), bundle, season, snaps, espn_of, status)
        doc = {"a1b_version": A.A1B_VERSION, "run_id": cutoff.strftime("%Y%m%dT%H%M%SZ"),
               "generated_at": datetime.now(timezone.utc).isoformat(), "cutoff": cutoff.isoformat(), "season": season,
               "week": week, "prospective_cutoff": A.PROSPECTIVE_CUTOFF, "dry_run": bool(a.dry_run), "research_only": True,
               "betting_authority": "NONE", "arm": "A1B", "not_pooled_with": "A1",
               "versions": {"sim": SIM_VERSION, "engine": S.ENGINE_VERSION, "models": bundle.get("models_version"),
                            "a1b": A.A1B_VERSION, "source": A.SOURCE_VERSION},
               "inputs": {"bundle": os.path.relpath(bpath, ROOT), "bundle_sha256": W2._sha(bpath),
                          "components_sha256": W2._sha(W2.COMPONENTS), "ledger_run_id": ledger_run, "sources": slate["sources"]},
               "games": {gid: rec}}
        print(gid, rec["state"], rec.get("reason", ""), "->", write_record(a.out, doc, gid))
    return 0


if __name__ == "__main__":
    sys.exit(main())
