#!/usr/bin/env python3
"""Score the Wave-2 PROSPECTIVE records (RESEARCH_ONLY; no output of this script has any authority).

  python scripts/sim/wave2_score.py --records-root /path/to/market-data [--interim] [--out-dir DIR]

Reads (never writes) the write-once records under <root>/data/research/wave2/ and the GAME SCRIPT V2 captures under
<root>/data/shadow/sim/, outcomes from the silver tables (schedule final score; player_games box score), and writes
ONE new JSON file per run: <out-dir>/score_<UTC stamp>.json (refuses to overwrite). Selection, metrics, gates and
minimum samples: nfl_edge/sim/wave2_score.py, PROSPECTIVE_PROTOCOL.md, PREREGISTRATION(_ADDENDUM).md.

Below an arm's frozen minimum the run reports COLLECTING with sample counts only; `--interim` adds INTERIM metrics
that change no status. RISK1's registered test is refused below 397 eligible games.
"""
from __future__ import annotations
import argparse, glob, gzip, json, os, subprocess, sys
from datetime import datetime, timezone
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import pandas as pd

from nfl_edge.sim import data as D, risk1 as R, wave2_score as W

OUT = os.path.join(ROOT, "research", "game_script_v2", "wave2", "prospective")
PLAYER_COLS = ("carries", "rush_yards", "targets", "receptions", "rec_yards", "attempts", "completions", "pass_yards", "pass_td", "any_td")


def record_paths(root: str) -> list:
    return sorted(glob.glob(os.path.join(root, "data", "research", "wave2", "*", "*.wave2.json.gz")))


def kickoffs_from_schedule(sched: pd.DataFrame) -> dict:
    g = sched[sched["gameday"].notna() & sched["gametime"].notna()].copy()
    ko = pd.to_datetime(g["gameday"] + " " + g["gametime"]).dt.tz_localize("America/New_York").dt.tz_convert("UTC")
    return {gid: t.isoformat() for gid, t in zip(g["game_id"], ko)}


def build_outcomes(game_ids, sched: pd.DataFrame) -> dict:
    """FINAL only when the schedule has a final score AND the box score has rows for the game; otherwise
    UNAVAILABLE with the reason (counted, never guessed)."""
    out, by_season = {}, {}
    s = sched.set_index("game_id")
    for gid in game_ids:
        if gid not in s.index:
            out[gid] = {"status": "UNAVAILABLE", "reason": "game not in schedule"}; continue
        r = s.loc[gid]
        if pd.isna(r.get("home_score")) or pd.isna(r.get("away_score")):
            out[gid] = {"status": "UNAVAILABLE", "reason": "no final score in schedule"}; continue
        season = int(r["season"])
        if season not in by_season:
            try:
                by_season[season] = D.load("player_games", [season]).to_pandas()
            except Exception as e:  # noqa: BLE001
                by_season[season] = e
        pg = by_season[season]
        if isinstance(pg, Exception):
            out[gid] = {"status": "UNAVAILABLE", "reason": f"player_games unavailable: {type(pg).__name__}"}; continue
        g = pg[pg["game_id"] == gid]
        if g.empty:
            out[gid] = {"status": "UNAVAILABLE", "reason": "no box score rows in player_games yet"}; continue
        players = {str(p.player_id): {"team": p.team, **{c: float(getattr(p, c)) for c in PLAYER_COLS if hasattr(p, c) and pd.notna(getattr(p, c))}}
                   for p in g.itertuples()}
        out[gid] = {"status": "FINAL", "home_score": float(r["home_score"]), "away_score": float(r["away_score"]),
                    "home_team": r["home_team"], "away_team": r["away_team"], "players": players}
    return out


def risk1_inputs(root: str, kickoffs: dict, sched: pd.DataFrame):
    """Games eligible for RISK1 (last pre-kickoff capture after the cutoff with >= 1 two-sided observation, and a FINAL
    outcome). Observation OUTCOMES are attached only when the frozen minimum is reached."""
    idx = R.capture_index(root)
    if idx.empty:
        return [], None
    sel = R.select_captures(idx, kickoffs)
    if sel.empty:
        return [], None
    outs = build_outcomes(sorted(sel["game_id"]), sched)
    eligible, obs = [], []
    for r in sel.itertuples():
        if outs[r.game_id].get("status") != "FINAL":
            continue
        with gzip.open(r.path, "rt") as f:
            gdoc = json.load(f)["games"][r.game_id]
        proj = r.path.replace(".scripts_v2.json.gz", ".projections.jsonl.gz")
        rows = []
        if os.path.exists(proj):
            with gzip.open(proj, "rt") as f:
                rows = [x for x in (json.loads(line) for line in f) if x.get("game_id") == r.game_id]
        o = R.observations({**gdoc, "game_id": r.game_id}, rows)
        if len(o):
            eligible.append((kickoffs[r.game_id], r.game_id))
            obs.append((r.game_id, gdoc, o))
    if len(eligible) < W.MIN_GAMES["RISK1"]:
        return eligible, None
    frames = []
    for gid, gdoc, o in obs:
        oc = outs[gid]
        game = {"game_id": gid, **{k: oc[k] for k in ("home_score", "away_score", "home_team", "away_team")}}
        by = {c["ticker"]: c for c in gdoc.get("contracts") or []}
        o = o.copy()
        o["y"] = [R.realized_cash(by[t], game, oc["players"]) if t in by else None for t in o["ticker"]]
        o["settlement_source"] = "BOX_SCORE_PRICER_SEMANTICS"
        frames.append(o)
    return eligible, pd.concat(frames, ignore_index=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records-root", required=True, help="a market-data checkout (data/research/wave2, data/shadow/sim)")
    ap.add_argument("--out-dir", default=OUT)
    ap.add_argument("--interim", action="store_true", help="add INTERIM metrics below the minimum (no status change)")
    a = ap.parse_args()
    paths = record_paths(a.records_root)
    records = [W.read_record(p) for p in paths]
    sched = D.schedule().to_pandas()
    kos = kickoffs_from_schedule(sched)
    gids = sorted({gid for r in records for gid in (r["doc"].get("games") or {})})
    outcomes = build_outcomes(gids, sched)
    r_el, r_obs = risk1_inputs(a.records_root, kos, sched)
    res = W.score(records, outcomes, kickoffs=kos, interim=a.interim, risk1_eligible=r_el, risk1_obs=r_obs)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip() or None
    now = datetime.now(timezone.utc)
    res = {"scored_at": now.isoformat(), "git_sha": sha, "records_root": os.path.abspath(a.records_root),
           "interim_requested": bool(a.interim), "settlement_note": "RISK1 outcomes: box score under the pricer's semantics; "
           "Kalshi settlements are not wired in this scorer version (I/O, to be added and logged before RISK1 reaches its minimum)",
           **res}
    os.makedirs(a.out_dir, exist_ok=True)
    path = os.path.join(a.out_dir, f"score_{now.strftime('%Y%m%dT%H%M%SZ')}.json")
    if os.path.exists(path):
        raise FileExistsError(path)
    with open(path, "x") as f:
        json.dump(res, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("wrote", os.path.relpath(path, ROOT), "| games used", len(res["records"]["used"]),
          "| statuses", {k: v.get("evidence_status") for k, v in res["arms"].items()}, "| RISK1", res["RISK1"]["evidence_status"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
