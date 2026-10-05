#!/usr/bin/env python3
"""Wave 2 PROSPECTIVE capture: incumbent and candidate arms on IDENTICAL rows, frozen before kickoff. RESEARCH_ONLY.

Protocol: research/game_script_v2/wave2/PREREGISTRATION.md and PROSPECTIVE_PROTOCOL.md. For every game of the week
whose kickoff falls in this run's window, and that has no record for that window yet, simulate the game with:

  A0  the incumbent bundle (research/simulation_engine/bundle_<season>.json), unchanged
  S1  the same bundle with ONLY the carry / target concentration models grafted in (frozen components file)
  Q1  the same bundle with ONLY the quarterback share mixture grafted in
  A1  the incumbent bundle with availability at the horizon this record may claim (T0_INACTIVES only after the
      inactive release with game-day statuses observed; otherwise identical to A0 and marked so)
  M1  the incumbent bundle with the game's (margin, total) drawn from M1-K instead of the residual bank

all with the same seed, and write one write-once file per game and window (with: metadata, horizon, the market state read, per-arm player
and team distributions as quantiles / pmfs, M0 vs M1 margin pmfs, and the A0 GAME SCRIPT V2 cell probabilities).

Windows (minutes before kickoff): EARLY = (90, 240], LATE = (30, 90]. A record never exists for a game whose kickoff
is before the PROSPECTIVE CUTOFF, and never carries anything timestamped after its own cutoff.

Usage: python scripts/sim/wave2_prospective.py --check-only [--existing-from-git origin/market-data] [--github-output F]
       python scripts/sim/wave2_prospective.py --market-data DIR [--cutoff ISO] [--out .] [--dry-run]
One write-once file per game and window: data/research/wave2/<day>/<game_id>.<window>.<run_id>.wave2.json.gz
"""
from __future__ import annotations
import argparse, copy, glob, gzip, hashlib, json, os, sys
from datetime import datetime, timedelta, timezone
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd

from nfl_edge.sim import (SIM_VERSION, availability_horizons as AH, data as D, features as F, inputs as I, key_numbers as K,
                          prospective as P, script_v2 as V, simulate as S)
from nfl_edge.sim.risk1 import PROSPECTIVE_CUTOFF

WAVE2_VERSION = "wave2-prospective-1.0.0"
COMPONENTS = os.path.join(ROOT, "research", "game_script_v2", "wave2", "components_2026.json")
WINDOWS = {"EARLY": (90, 240), "LATE": (30, 90)}
ARMS = ("A0", "S1", "Q1", "A1", "M1")
QL = np.round(np.arange(0.01, 1.0, 0.02), 4)
COUNT_STATS = ("carries", "targets", "receptions", "attempts", "completions", "pass_td", "any_td")
YARD_STATS = ("rush_yards", "rec_yards", "pass_yards")
TEAM_STATS = ("plays", "pass_att", "rush_att", "designed_rush", "dropbacks", "targets", "points")
N_SIMS = 10000


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else None


def arm_bundles(bundle: dict, comps: dict) -> dict:
    """The incumbent bundle and, for S1 / Q1, a deep copy with ONLY that arm's component replaced."""
    s1 = copy.deepcopy(bundle)
    s1["carry_share"]["alpha_model"] = comps["S1"]["carry"]; s1["target_share"]["alpha_model"] = comps["S1"]["target"]
    q1 = copy.deepcopy(bundle)
    q1["qb_share"] = comps["Q1"]["qb_share"]
    return {"A0": bundle, "S1": s1, "Q1": q1, "A1": bundle, "M1": bundle}


def _pmf(x, nmax=80):
    xi = np.clip(np.round(np.asarray(x, float)), 0, nmax).astype(int)
    p = np.bincount(xi, minlength=nmax + 1) / len(xi)
    nz = np.flatnonzero(p > 0)
    lo, hi = (int(nz[0]), int(nz[-1])) if len(nz) else (0, 0)
    return {"lo": lo, "p": [round(float(v), 5) for v in p[lo:hi + 1]]}


def summarize(res) -> dict:
    out = {"players": {}, "teams": {}}
    for pid, Pl in res.player.items():
        if pid.startswith("OTHER"):
            continue
        rec = {"team": Pl["team"], "p_active": round(float(np.mean(Pl["active"])), 4)}
        for st in COUNT_STATS:
            if st in Pl:
                rec[st] = _pmf(Pl[st])
        for st in YARD_STATS:
            if st in Pl:
                x = np.asarray(Pl[st], float)
                rec[st] = {"mean": round(float(x.mean()), 2), "q": [round(float(v), 1) for v in np.quantile(x, QL)]}
        out["players"][pid] = rec
    for team, Tm in res.team.items():
        out["teams"][team] = {st: {"mean": round(float(np.mean(Tm[st])), 2), "q": [round(float(v), 1) for v in np.quantile(np.asarray(Tm[st], float), QL)]}
                              for st in TEAM_STATS if st in Tm}
    return out


def with_horizon(gi, horizon: str):
    """A1: the GameInput with participation states at the horizon (T0_INACTIVES: no second questionable discount)."""
    g = copy.deepcopy(gi)
    for ti in (g.home, g.away):
        ti.players = ti.players.assign(avail_state=AH.availability_states(ti.players["avail_state"], horizon))
    return g


def _parse_name(name: str):
    """<game_id>.<window>.<run_id>.wave2.json.gz -> (game_id, window)."""
    parts = os.path.basename(name).split(".")
    return (parts[0], parts[1]) if len(parts) >= 5 and parts[1] in WINDOWS else None


def existing_records(roots, git_ref: str | None = None) -> set:
    seen = set()
    for root in roots:
        for p in glob.glob(os.path.join(root, "data", "research", "wave2", "*", "*.wave2.json.gz")):
            k = _parse_name(p)
            if k:
                seen.add(k)
    if git_ref:
        import subprocess
        out = subprocess.run(["git", "ls-tree", "-r", "--name-only", git_ref, "data/research/wave2"], capture_output=True, text=True, cwd=ROOT)
        for line in out.stdout.splitlines():
            k = _parse_name(line)
            if k:
                seen.add(k)
    return seen


def due_games(sched: pd.DataFrame, cutoff: datetime, seen: set) -> dict:
    """game_id -> window for games whose kickoff is in a capture window, after the PROSPECTIVE CUTOFF, unrecorded."""
    pcut = datetime.fromisoformat(PROSPECTIVE_CUTOFF)
    g = sched[sched["gameday"].notna() & sched["gametime"].notna()].copy()
    g["kickoff"] = pd.to_datetime(g["gameday"] + " " + g["gametime"]).dt.tz_localize("America/New_York").dt.tz_convert("UTC")
    todo = {}
    for r in g.itertuples():
        ko = r.kickoff.to_pydatetime()
        mins = (ko - cutoff).total_seconds() / 60.0
        for wname, (lo, hi) in WINDOWS.items():
            if lo < mins <= hi and ko > pcut and (r.game_id, wname) not in seen:
                todo[r.game_id] = (wname, int(r.season), int(r.week))
    return todo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default=None)
    ap.add_argument("--cutoff", default=None)
    ap.add_argument("--out", default=".")
    ap.add_argument("--check-only", action="store_true", help="schedule + record index only; prints due games")
    ap.add_argument("--existing-from-git", default=None, help="a git ref whose data/research/wave2 tree lists existing records")
    ap.add_argument("--github-output", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cutoff = datetime.fromisoformat(a.cutoff.replace("Z", "+00:00")) if a.cutoff else datetime.now(timezone.utc)
    if a.check_only:
        from nfl_edge.data import silver
        sched = silver.load_games().to_pandas()
    else:
        sched = D.schedule().to_pandas()
    seen = existing_records([r for r in (a.market_data, a.out) if r], a.existing_from_git)
    todo = due_games(sched, cutoff, seen)
    if a.github_output:
        with open(a.github_output, "a") as f:
            f.write(f"due={'true' if todo else 'false'}\n")
    if a.check_only or not todo:
        print("due:", todo or "none"); return
    ledger_rows, man, ledger_run = P.latest_ledger(a.market_data, at_or_before=cutoff)
    comps = json.load(open(COMPONENTS))
    written = []
    for (season, week), grp in pd.Series(todo).groupby(lambda gid: todo[gid][1:]):
        bpath = os.path.join(ROOT, "research", "simulation_engine", f"bundle_{season}.json")
        bundle = json.load(open(bpath))
        bundles = arm_bundles(bundle, comps)
        slate = P.slate_inputs(season, week, cutoff, a.market_data, ledger_rows=ledger_rows, priors=F.PriorSet.from_dict(bundle["priors"]))
        roster = F.weekly_roster(season, week)
        roster.attrs["retrieved_at"] = AH.roster_retrieved_at(ROOT, season)
        hist = K.history(season - 1)
        for gid in grp.index:
            wname = todo[gid][0]
            rec = capture_game(slate, gid, wname, cutoff, roster, hist, bundles, season)
            doc = {"wave2_version": WAVE2_VERSION, "run_id": cutoff.strftime("%Y%m%dT%H%M%SZ"),
                   "generated_at": datetime.now(timezone.utc).isoformat(), "cutoff": cutoff.isoformat(), "season": season,
                   "week": week, "prospective_cutoff": PROSPECTIVE_CUTOFF, "dry_run": bool(a.dry_run), "research_only": True,
                   "betting_authority": "NONE",
                   "versions": {"sim": SIM_VERSION, "engine": S.ENGINE_VERSION, "models": bundle.get("models_version"),
                                "m1": K.M1_VERSION, "a1": AH.A1_VERSION, "s1": comps["S1"]["carry"].get("version"),
                                "q1": comps["Q1"]["qb_share"]["regime_model"].get("version")},
                   "inputs": {"bundle": os.path.relpath(bpath, ROOT), "bundle_sha256": _sha(bpath), "components_sha256": _sha(COMPONENTS),
                              "ledger_run_id": ledger_run, "sources": slate["sources"]},
                   "games": {gid: rec}}
            written.append(write_record(a.out, doc, gid, wname))
    print("wrote", written)


def capture_game(slate, gid, wname, cutoff, roster, hist, bundles, season) -> dict:
    G = slate["games"].get(gid)
    if G is None:
        return {"window": wname, "state": "NOT_IN_SLATE"}
    gi, ko = G["input"], G["kickoff"].to_pydatetime()
    hz = {t: AH.prospective_horizon(cutoff, ko, roster, t, roster.attrs.get("retrieved_at")) for t in (gi.home.team, gi.away.team)}
    horizon = "T0_INACTIVES" if all(h[0] == "T0_INACTIVES" for h in hz.values()) else "T24"
    draws = {"M0": K.m0_draws(hist, gi.spread_home, gi.total_line, season, N_SIMS, seed=11),
             "M1": K.m1k_draws(hist, gi.spread_home, gi.total_line, season, N_SIMS, seed=11)}
    rec = {"window": wname, "state": "OK", "kickoff_utc": ko.isoformat(), "cutoff": cutoff.isoformat(),
           "minutes_to_kickoff": (ko - cutoff).total_seconds() / 60.0, "horizon": horizon,
           "horizon_by_team": {t: {"horizon": h[0], "why": h[1]} for t, h in hz.items()},
           "centre": {"spread_home": gi.spread_home, "total": gi.total_line, "source": gi.center_source},
           "arms": {}, "coherence": {}, "a1_identical_to_a0": horizon != "T0_INACTIVES"}
    for arm in ARMS:
        gin = with_horizon(gi, horizon) if arm == "A1" else gi
        gd = draws["M1" if arm == "M1" else "M0"]
        res = S.simulate(gin, bundles[arm], n=N_SIMS, seed=11, game_draws={k: gd[k] for k in ("margin", "total", "home", "away")})
        rec["coherence"][arm] = bool(S.coherence_report(res)["ok"])
        rec["arms"][arm] = summarize(res)
        if arm in ("A0", "M1"):
            rec["arms"][arm]["margin_pmf"] = _pmf(np.asarray(res.margin) + 80, 160)
            rec["arms"][arm]["v2_cells"] = V.cell_probabilities(V.cell_index(res.margin, res.total, gi.spread_home, gi.total_line)).tolist()
    return rec


def write_record(out_root: str, doc: dict, gid: str, wname: str) -> str:
    """Write-once: an existing record for the same game, window and run is refused, never overwritten."""
    run_id = doc["run_id"]
    day = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}"
    d = os.path.join(out_root, "data", "research", "wave2", day)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{gid}.{wname}.{run_id}.wave2.json.gz")
    if os.path.exists(path):
        raise FileExistsError(path)
    with gzip.open(path, "wt") as f:
        json.dump(doc, f, default=P._json_default)
    return path


if __name__ == "__main__":
    main()
