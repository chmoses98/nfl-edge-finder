"""Promotion-rule evaluation of the projection research arms against the frozen baseline A0 (preregistration
section 6). RESEARCH_ONLY; an arm that passes is reported PROMOTABLE, it is not deployed by this code.

Comparison is PAIRED: every arm is scored on A0's scored rows (the (game, player, statistic) rows whose A0
predictive mean clears ``backtest.FLOORS``), so an arm cannot change which rows are judged. Every interval is a
GAME-clustered bootstrap: the same resampled games are used for all eight statistics of a resample.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from . import baseline_report as BR

PRIMARY = BR.PRIMARY_STATS
MATERIAL = -0.005            # pooled primary must improve by at least 0.5% (registered)
B = 2000
SEED = 20261005


def paired_rows(base_dir: str, arm_dir: str, season: int) -> pd.DataFrame:
    """Per (game, player, stat) on A0's scored population: CRPS and interval membership of both arms."""
    A = pd.read_parquet(os.path.join(base_dir, f"player_dists_{season}.parquet"))
    R = pd.read_parquet(os.path.join(arm_dir, f"player_dists_{season}.parquet"))
    out = []
    for st in PRIMARY:
        a = BR.scored_rows(A, st)[["game_id", "player_id", "stat", "crps", "in50", "in90", "ae"]]
        r = R[R["stat"] == st]
        Q = np.vstack(r["quantiles"].to_numpy()); y = r["actual"].to_numpy(float)
        r = r[["game_id", "player_id", "stat"]].assign(crps=BR.crps_rows(Q, y), in50=(y >= Q[:, BR.I25]) & (y <= Q[:, BR.I75]),
                                                       in90=(y >= Q[:, BR.I05]) & (y <= Q[:, BR.I95]),
                                                       ae=np.abs(r["mean"].to_numpy(float) - y))
        m = a.merge(r, on=["game_id", "player_id", "stat"], suffixes=("_a0", "_arm"), how="left")
        out.append(m)
    d = pd.concat(out, ignore_index=True)
    d["season"] = season
    return d


def _stat_sums(d: pd.DataFrame) -> pd.DataFrame:
    """Per (game, stat) sums, the unit the bootstrap resamples (by game)."""
    d = d.assign(c50a=(d["in50_a0"].astype(float) - 0.5), c90a=(d["in90_a0"].astype(float) - 0.9),
                 c50r=(d["in50_arm"].astype(float) - 0.5), c90r=(d["in90_arm"].astype(float) - 0.9))
    return d.groupby(["game_id", "stat"]).agg(crps_a0=("crps_a0", "sum"), crps_arm=("crps_arm", "sum"), n=("crps_a0", "size"),
                                              in50_a0=("in50_a0", "sum"), in90_a0=("in90_a0", "sum"),
                                              in50_arm=("in50_arm", "sum"), in90_arm=("in90_arm", "sum")).reset_index()


def _summaries(g: pd.DataFrame) -> dict:
    """Primary summary, per-stat relative change and calibration error from per-(game, stat) sums."""
    by = g.groupby("stat")[["crps_a0", "crps_arm", "n", "in50_a0", "in90_a0", "in50_arm", "in90_arm"]].sum()
    rel = (by["crps_arm"] / by["crps_a0"] - 1).reindex(PRIMARY)
    cal_a0 = ((by["in50_a0"] / by["n"] - 0.5).abs() + (by["in90_a0"] / by["n"] - 0.9).abs()).reindex(PRIMARY).mean() / 2
    cal_arm = ((by["in50_arm"] / by["n"] - 0.5).abs() + (by["in90_arm"] / by["n"] - 0.9).abs()).reindex(PRIMARY).mean() / 2
    return {"primary": float(rel.mean()), "by_stat": {k: float(v) for k, v in rel.items()},
            "calibration_error_a0": float(cal_a0), "calibration_error_arm": float(cal_arm), "calibration_delta": float(cal_arm - cal_a0)}


def _boot(g: pd.DataFrame, B_: int = B, seed: int = SEED) -> dict:
    games = g["game_id"].unique()
    pos = {k: i for i, k in enumerate(games)}
    gi = g["game_id"].map(pos).to_numpy()
    rng = np.random.default_rng(seed)
    prim, cal = np.empty(B_), np.empty(B_)
    cols = ["crps_a0", "crps_arm", "n", "in50_a0", "in90_a0", "in50_arm", "in90_arm"]
    for b in range(B_):
        w = np.bincount(rng.integers(0, len(games), len(games)), minlength=len(games))[gi]
        gg = g[cols].mul(w, axis=0).assign(stat=g["stat"].to_numpy())
        s = _summaries(gg)
        prim[b], cal[b] = s["primary"], s["calibration_delta"]
    return {"primary_lo": float(np.quantile(prim, 0.025)), "primary_hi": float(np.quantile(prim, 0.975)),
            "calibration_delta_se": float(cal.std(ddof=1))}


def evaluate_arm(base_dir: str, arm_dir: str, seasons) -> dict:
    by_season, allg = {}, []
    for y in seasons:
        d = paired_rows(base_dir, arm_dir, y)
        missing = int(d["crps_arm"].isna().sum())
        g = _stat_sums(d.dropna(subset=["crps_arm"]))
        s = _summaries(g); s.update(_boot(g)); s["n_rows"] = int(len(d)); s["rows_missing_in_arm"] = missing
        by_season[str(y)] = s
        allg.append(g.assign(game_id=g["game_id"]))
    G = pd.concat(allg, ignore_index=True)
    pooled = _summaries(G); pooled.update(_boot(G))
    improved = [k for k, v in pooled["by_stat"].items() if v < 0]
    best = min(pooled["by_stat"], key=pooled["by_stat"].get)
    drop_best = float(np.mean([v for k, v in pooled["by_stat"].items() if k != best]))
    crit = {
        "improves_in_at_least_4_of_5_seasons": sum(by_season[str(y)]["primary"] < 0 for y in seasons) >= 4,
        "no_season_materially_worse": all(by_season[str(y)]["primary_lo"] <= 0 for y in seasons),
        "pooled_ci_below_zero": pooled["primary_hi"] < 0,
        "pooled_improvement_material": pooled["primary"] <= MATERIAL,
        "calibration_not_materially_worse": pooled["calibration_delta"] <= pooled["calibration_delta_se"],
        "broad_at_least_5_of_8_stats": len(improved) >= 5,
        "survives_dropping_best_stat": drop_best < 0,
    }
    return {"by_season": by_season, "pooled": pooled, "stats_improved_pooled": improved, "most_improved_stat": best,
            "primary_without_most_improved": drop_best, "criteria": crit,
            "verdict": "PROMOTABLE" if all(crit.values()) else "REJECTED"}


def team_crps(out_dir: str, seasons, stats=("plays", "pass_att", "rush_att", "dropbacks", "targets")) -> dict:
    out = {}
    for y in seasons:
        Tt = pd.read_parquet(os.path.join(out_dir, f"team_dists_{y}.parquet"))
        out[str(y)] = {st: BR.team_summary(Tt, st).get("crps") for st in stats}
    return out
