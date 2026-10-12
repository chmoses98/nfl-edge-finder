#!/usr/bin/env python3
"""PURE_PLAYER_V1_2 evaluation (preregistered: docs/research/PURE_PLAYER_V1_2_PREREGISTRATION.md).

Arms, all scored on the SAME matched player-game-statistic rows (one row each):

    PURE_PLAYER_V1      frozen reference (pure-player-v1.0.0) -- the decision reference
    PURE_EWM_BASELINE   frozen simplest sports-only arm
    PURE_PLAYER_V1_2    the challenger
    V4_MARKET_CLOSE     DATA_PLAYER_V4, closing spread / total -- MARKET-INFORMED benchmark, descriptive only
    V4_MEF_AS_IS        V4 market_env=False -- NOT market-free (market-gated training sample) and reads injury / roster
                        statuses that are not point-in-time for 2025; descriptive only

    python3 scripts/research/pure_player_v1_2_study.py --data-root <root> --cache <dir> --seasons 2023 --label dev_2023 --no-v4
    python3 scripts/research/pure_player_v1_2_study.py --data-root <root> --cache <dir> --seasons 2024,2025,2026 --label holdout \
        --arms <cache>/pure_gap_arms_2024_2025.pkl --mutation
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "research"))
import pure_gap_arms as GA                                                                  # noqa: E402
import pure_player_v1_study as S1                                                           # noqa: E402
from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME as V1                  # noqa: E402
from nfl_edge.engines.player.pure_v1 import VERSION as V1_VERSION                            # noqa: E402
from nfl_edge.engines.player.pure_v1 import data as PD                                      # noqa: E402
from nfl_edge.engines.player.pure_v1 import features as PF                                  # noqa: E402
from nfl_edge.engines.player.pure_v1 import mutation as MU                                  # noqa: E402
from nfl_edge.engines.player.pure_v1 import pipeline as P1                                  # noqa: E402
from nfl_edge.engines.player.pure_v1_2 import MODEL_NAME as V12, VERSION as V12_VERSION      # noqa: E402
from nfl_edge.engines.player.pure_v1_2 import pipeline as P12                               # noqa: E402

STATS = ["snap_share", "targets", "receptions", "receiving_yards", "carries", "rushing_yards", "passing_attempts", "completions",
         "passing_yards"]
PRIMARY = (2024, 2025)
SUPPLEMENTARY = 2026
COV_TOL = 0.01


def coverage_delta(A: pd.DataFrame, Bf: pd.DataFrame, nboot: int) -> dict:
    """Δ|cov80 − 0.80| (challenger − reference) per statistic with a game-clustered bootstrap CI."""
    k = ["game_id", "player_id", "statistic"]
    m = A.merge(Bf[k + ["p10", "p90"]], on=k, suffixes=("_a", "_b"))
    out = {}
    for stat, s in m.groupby("statistic"):
        y = s["actual"].to_numpy(float); g = s["game_id"].to_numpy()
        ia = ((s.p10_a <= y) & (y <= s.p90_a)).to_numpy(float); ib = ((s.p10_b <= y) & (y <= s.p90_b)).to_numpy(float)
        codes, inv = np.unique(g, return_inverse=True)
        sa = np.bincount(inv, weights=ia); sb = np.bincount(inv, weights=ib); c = np.bincount(inv).astype(float)
        rng = np.random.default_rng(20261010)
        d = np.empty(nboot)
        for i in range(nboot):
            idx = rng.integers(0, len(codes), len(codes))
            n = c[idx].sum()
            d[i] = abs(sa[idx].sum() / n - 0.8) - abs(sb[idx].sum() / n - 0.8)
        pt = abs(ia.mean() - 0.8) - abs(ib.mean() - 0.8)
        out[stat] = {"cov80_a": round(float(ia.mean()), 4), "cov80_b": round(float(ib.mean()), 4), "delta_abs_dev": round(float(pt), 5),
                     "ci95": [round(float(np.quantile(d, 0.025)), 5), round(float(np.quantile(d, 0.975)), 5)]}
    return out


def decide(primary: dict, cov: dict, supp: dict | None, n_by_season: dict) -> dict:
    """The preregistered rule (PURE_PLAYER_V1_2 vs PURE_PLAYER_V1)."""
    scorable = [s for s in STATS if all(n_by_season.get(se, {}).get(s, 0) >= 200 for se in PRIMARY)]
    if len(scorable) < 7:
        return {"verdict": "BLOCKED_DATA", "scorable_stats": scorable}
    neg = [s for s in STATS if primary[s]["delta_mae"] < 0]
    sig_neg = [s for s in STATS if primary[s]["delta_mae_ci95"] and primary[s]["delta_mae_ci95"][1] < 0]
    worse_mae = [s for s in STATS if primary[s]["delta_mae_ci95"] and primary[s]["delta_mae_ci95"][0] > 0]
    worse_brier = [s for s in STATS if primary[s].get("delta_brier_ci95") and primary[s]["delta_brier_ci95"][0] > 0]
    worse_cov = [s for s in STATS if cov[s]["ci95"][0] > COV_TOL]
    worse_supp = [s for s in STATS if supp and s in supp and supp[s]["delta_mae_ci95"] and supp[s]["delta_mae_ci95"][0] > 0]
    crit = {"a_dmae_negative_on_at_least_6": len(neg) >= 6, "a_ci_below_zero_on_at_least_3": len(sig_neg) >= 3,
            "b_no_stat_significantly_worse_mae": not worse_mae, "b_no_stat_significantly_worse_brier": not worse_brier,
            "c_no_coverage_worsening_beyond_tolerance": not worse_cov, "d_no_stat_significantly_worse_in_2026": not worse_supp}
    return {"verdict": "ACCEPTED_CHALLENGER" if all(crit.values()) else "REJECTED", "criteria": crit, "dmae_negative": neg,
            "dmae_ci_below_zero": sig_neg, "significantly_worse_mae": worse_mae, "significantly_worse_brier": worse_brier,
            "coverage_worse_beyond_tolerance": worse_cov, "significantly_worse_mae_2026": worse_supp, "scorable_stats": scorable}


def mutation_check(data_root: str, season: int, cache: str) -> dict:
    """Real data: rebuild the V1_2 frame from files with the schedule's market columns removed / randomised and rerun
    the target season. Forecast digests must equal the original's."""
    full = pd.read_csv(os.path.join(data_root, "data/raw/nflverse/schedules/games.csv"), low_memory=False)
    stats = PD.read_stats(data_root, range(2013, season + 1)); snaps = PD.read_snaps(data_root, range(2013, season + 1))
    out = {}
    for mode in ("original", "removed", "randomized"):
        sched = MU.mutate_schedule(full, mode)
        pg = PD.build_player_games(stats, snaps, PD.sports_schedule(sched))
        rows, t = PF.build(pg)
        o = P12.run(P12.add_features(rows, t), t, season)
        fc, _ = P1.sidecar_rows(o["player"][V12], V12_VERSION, str(rows.loc[rows.season < season, "kickoff"].max()))
        out[mode] = {"n_forecasts": len(fc), "forecast_sha256": MU.forecast_digest(fc)}
    out["bit_identical"] = len({v["forecast_sha256"] for v in out.values() if isinstance(v, dict)}) == 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--seasons", default="2024,2025,2026")
    ap.add_argument("--label", default="holdout")
    ap.add_argument("--last-season", type=int, default=2026)
    ap.add_argument("--arms", default=None, help="pure_gap_arms pickle with V4 arms for some seasons (reused, not refitted)")
    ap.add_argument("--no-v4", action="store_true")
    ap.add_argument("--mutation", action="store_true")
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "pure_player_v1_2"))
    a = ap.parse_args()
    t0 = time.time()
    log = lambda *x: print(f"[{time.time() - t0:6.0f}s]", *x, flush=True)   # noqa: E731
    seasons = [int(x) for x in a.seasons.split(",")]
    os.makedirs(a.out, exist_ok=True)
    rows, t = S1.pure_frames(a.data_root, a.cache, a.last_season)
    rows12 = P12.add_features(rows, t)
    log("frames", rows12.shape)
    cached = pd.read_pickle(a.arms) if a.arms else None
    frame = teams4 = None
    P = {}; info = {}
    for S in seasons:
        o1 = P1.run(rows, t, S)
        o12 = P12.run(rows12, t, S)
        L = {V1: o1["player"][V1], BASELINE_NAME: o1["player"][BASELINE_NAME], V12: o12["player"][V12]}
        info[S] = {"v1_2_model": o12["model"].info, "n_rows": {k: int(len(v)) for k, v in L.items()}}
        if not a.no_v4:
            for name in (GA.V4_MKT, GA.V4_MEF):
                if cached is not None and S in set(cached["long"][name].season.unique()):
                    L[name] = cached["long"][name][cached["long"][name].season == S].drop(columns=["season"])
                else:
                    if frame is None:
                        from nfl_edge.engines.player.v4.volume import team_game_table
                        frame = S1.v4_frame(a.data_root, a.cache, a.last_season); teams4 = team_game_table(frame)
                    keys = L[V1][["player_id", "game_id"]]
                    act = L[BASELINE_NAME][["game_id", "player_id", "statistic", "season", "week", "pgroup", "actual", "played", "kickoff"]]
                    l4, _, _, i4 = GA.v4_arm(frame, teams4, S, keys, GA.V4_CONFIGS[name])
                    L[name] = l4.merge(act, on=["game_id", "player_id", "statistic"], how="inner").drop(columns=["season"])
                    info[S][name] = i4
        for k, v in L.items():
            P.setdefault(k, []).append(v.assign(season=S))
        log(S, {k: len(v) for k, v in L.items()})
    P = {k: pd.concat(v, ignore_index=True) for k, v in P.items()}
    for k in P:
        P[k]["pgroup"] = P[k]["pgroup"].fillna("NA")
    rung = S1.representative_rung(P[BASELINE_NAME])
    B = a.bootstrap
    scopes = {f"season_{S}": (lambda S: lambda d: d.season == S)(S) for S in seasons}
    if all(s in seasons for s in PRIMARY):
        scopes = {"primary_2024_2025": lambda d: d.season.isin(PRIMARY), **scopes}
    pairs = [(V12, V1), (V12, BASELINE_NAME), (V1, BASELINE_NAME)]
    if not a.no_v4:
        pairs += [(V12, GA.V4_MKT), (V12, GA.V4_MEF), (V1, GA.V4_MKT), (V1, GA.V4_MEF)]
    res = {"protocol": {"preregistration": "docs/research/PURE_PLAYER_V1_2_PREREGISTRATION.md", "label": a.label, "seasons": seasons,
                        "primary": list(PRIMARY), "supplementary": SUPPLEMENTARY, "bootstrap": B, "cluster": "game_id", "seed": 20261010,
                        "versions": {V1: V1_VERSION, V12: V12_VERSION}, "coverage_tolerance": COV_TOL,
                        "labels": {GA.V4_MKT: "MARKET-INFORMED benchmark (closing spread/total); descriptive only",
                                   GA.V4_MEF: "not market-free (market-gated training sample) and uses injury/roster statuses not PIT for 2025; descriptive only"}},
           "info": info, "player": {}, "coverage": {}, "by_group": {}}
    for sc, fn in scopes.items():
        res["player"][sc] = {f"{x}__vs__{y}": S1.compare(P[x][fn(P[x])], P[y][fn(P[y])], rung, B) for x, y in pairs}
        res["coverage"][sc] = coverage_delta(P[V12][fn(P[V12])], P[V1][fn(P[V1])], B)
        log("scope", sc)
    main_scope = "primary_2024_2025" if "primary_2024_2025" in scopes else f"season_{seasons[0]}"
    for grp in ("QB", "RB", "WR", "TE"):
        fn = scopes[main_scope]
        res["by_group"][grp] = S1.compare(P[V12][fn(P[V12]) & (P[V12].pgroup == grp)], P[V1][fn(P[V1]) & (P[V1].pgroup == grp)], rung, B)
    n_by_season = {S: P[V12][P[V12].season == S].groupby("statistic").size().to_dict() for S in seasons}
    res["n_by_season"] = {str(k): v for k, v in n_by_season.items()}
    if main_scope == "primary_2024_2025":
        supp = res["player"].get(f"season_{SUPPLEMENTARY}", {}).get(f"{V12}__vs__{V1}")
        res["decision"] = decide(res["player"][main_scope][f"{V12}__vs__{V1}"], res["coverage"][main_scope], supp, n_by_season)
        log("decision", res["decision"]["verdict"])
    if a.mutation:
        res["mutation_2025"] = mutation_check(a.data_root, 2025, a.cache)
        log("mutation", res["mutation_2025"]["bit_identical"])
    res["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(a.out, f"{a.label}.json"), "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
    log("wrote", os.path.join(a.out, f"{a.label}.json"))


if __name__ == "__main__":
    main()
