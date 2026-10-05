"""Paired evaluation of a Wave-2 arm against the incumbent on IDENTICAL rows. RESEARCH_ONLY.

The population is always the incumbent's scored rows (backtest.FLOORS on the incumbent's predictive mean), so an arm
cannot choose which rows judge it; intervals resample GAMES. The primary metric of each arm is the preregistered one
(research/game_script_v2/wave2/PREREGISTRATION.md, section 7):

  S1  mean relative CRPS over targets, receptions, receiving yards, carries, rushing yards
  Q1  lower-decile calibration error |P(rPIT < 0.10) - 0.10| over attempts, completions, passing yards
  A1  absolute bias of QUESTIONABLE players' carries + targets
and `min_sample` turns the paired per-game differences of the DEVELOPMENT season into the preregistered minimum
prospective sample ((1.96 + 0.84) sd / effect)^2, rounded up to weeks of 16 games, floored at 64.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd

from . import backtest as Bt
from . import baseline_report as BR

S1_STATS = ("targets", "receptions", "rec_yards", "carries", "rush_yards")
Q1_STATS = ("attempts", "completions", "pass_yards")
OTHER_STATS = ("pass_td", "any_td")
B, SEED = 2000, 20261005


def _rows(d: str, season: int) -> pd.DataFrame:
    return pd.read_parquet(os.path.join(d, f"player_dists_{season}.parquet"))


def _metrics(g: pd.DataFrame, stat: str, prefix: str) -> pd.DataFrame:
    Q = np.vstack(g["quantiles"].to_numpy()); y = g["actual"].to_numpy(float)
    pm = np.vstack(g["pmf"].to_numpy())
    rp = BR.randomized_pit(pm, y, stat)
    return pd.DataFrame({f"{prefix}crps": BR.crps_rows(Q, y), f"{prefix}ae": np.abs(g["mean"].to_numpy(float) - y),
                         f"{prefix}err": g["mean"].to_numpy(float) - y, f"{prefix}rpit": rp,
                         f"{prefix}in50": (y >= Q[:, BR.I25]) & (y <= Q[:, BR.I75]),
                         f"{prefix}in90": (y >= Q[:, BR.I05]) & (y <= Q[:, BR.I95])}, index=g.index)


def paired(base_dir: str, arm_dir: str, season: int, stats) -> pd.DataFrame:
    A, R = _rows(base_dir, season), _rows(arm_dir, season)
    out = []
    for st in stats:
        a = A[(A["stat"] == st) & (A["mean"] >= Bt.FLOORS.get(st, 0.0))]
        r = R[R["stat"] == st].set_index(["game_id", "player_id"])
        a = a[[k in r.index for k in zip(a["game_id"], a["player_id"])]]
        r = r.loc[list(zip(a["game_id"], a["player_id"]))].reset_index()
        ma = _metrics(a.reset_index(drop=True), st, "a0_"); mr = _metrics(r, st, "arm_")
        base = a.reset_index(drop=True)[["game_id", "team", "player_id", "stat", "mean", "actual"]].rename(columns={"mean": "a0_mean"})
        out.append(pd.concat([base, ma.reset_index(drop=True), mr.reset_index(drop=True), r[["mean"]].rename(columns={"mean": "arm_mean"})], axis=1))
    d = pd.concat(out, ignore_index=True)
    d["season"] = season
    return d


def chi2(x: np.ndarray) -> float:
    h = np.histogram(x, bins=10, range=(0, 1))[0]; e = len(x) / 10
    return float(((h - e) ** 2 / e).sum()) if len(x) else float("nan")


def stat_table(d: pd.DataFrame) -> dict:
    out = {}
    for st, g in d.groupby("stat"):
        out[st] = {"n": int(len(g)), "crps_a0": float(g["a0_crps"].mean()), "crps_arm": float(g["arm_crps"].mean()),
                   "rel_crps": float(g["arm_crps"].sum() / g["a0_crps"].sum() - 1), "mae_a0": float(g["a0_ae"].mean()),
                   "mae_arm": float(g["arm_ae"].mean()), "bias_a0": float(g["a0_err"].mean()), "bias_arm": float(g["arm_err"].mean()),
                   "chi2_a0": chi2(g["a0_rpit"].to_numpy()), "chi2_arm": chi2(g["arm_rpit"].to_numpy()),
                   "low_decile_a0": float(np.mean(g["a0_rpit"] < 0.10)), "low_decile_arm": float(np.mean(g["arm_rpit"] < 0.10)),
                   "high_decile_a0": float(np.mean(g["a0_rpit"] > 0.90)), "high_decile_arm": float(np.mean(g["arm_rpit"] > 0.90)),
                   "cover50_a0": float(g["a0_in50"].mean()), "cover50_arm": float(g["arm_in50"].mean()),
                   "cover90_a0": float(g["a0_in90"].mean()), "cover90_arm": float(g["arm_in90"].mean())}
    return out


def _boot(fn, d: pd.DataFrame, B_: int = B, seed: int = SEED) -> dict:
    games = d["game_id"].unique()
    pos = d.groupby("game_id").indices
    rng = np.random.default_rng(seed)
    est = fn(d)
    bs = []
    for _ in range(B_):
        ix = np.concatenate([pos[g] for g in games[rng.integers(0, len(games), len(games))]])
        bs.append(fn(d.iloc[ix]))
    bs = np.asarray(bs)
    return {"mean": float(est), "lo": float(np.nanquantile(bs, 0.025)), "hi": float(np.nanquantile(bs, 0.975)), "n_games": int(len(games))}


# ---------------------------------------------------------------------------------- primary metrics
def s1_primary(d: pd.DataFrame) -> float:
    g = d[d["stat"].isin(S1_STATS)].groupby("stat")[["arm_crps", "a0_crps"]].sum()
    return float((g["arm_crps"] / g["a0_crps"] - 1).mean())


def q1_primary_delta(d: pd.DataFrame) -> float:
    """Change in the lower-decile calibration error (negative = closer to 0.10)."""
    g = d[d["stat"].isin(Q1_STATS)]
    errs = []
    for st, x in g.groupby("stat"):
        errs.append(abs(np.mean(x["arm_rpit"] < 0.1) - 0.1) - abs(np.mean(x["a0_rpit"] < 0.1) - 0.1))
    return float(np.mean(errs))


def a1_primary_delta(d: pd.DataFrame) -> float:
    """Change in |bias| of questionable players' carries + targets (negative = less biased)."""
    g = d[d["questionable"] & d["stat"].isin(("carries", "targets"))]
    return float(abs(g["arm_err"].mean()) - abs(g["a0_err"].mean())) if len(g) else float("nan")


def per_game_effect(d: pd.DataFrame, kind: str) -> pd.Series:
    """Paired per-game difference of the primary quantity (negative = candidate better), for the sample size."""
    if kind == "S1":
        x = d[d["stat"].isin(S1_STATS)].copy()
        scale = x.groupby("stat")["a0_crps"].transform("mean")
        x["d"] = (x["arm_crps"] - x["a0_crps"]) / scale
        return x.groupby("game_id")["d"].mean()
    if kind == "Q1":
        x = d[d["stat"].isin(Q1_STATS)].copy()
        # per-game contribution to the lower-decile mass, signed toward the target 0.10 by the incumbent's side
        side = np.sign(np.mean(x["a0_rpit"] < 0.1) - 0.1) or 1.0
        x["d"] = side * ((x["arm_rpit"] < 0.1).astype(float) - (x["a0_rpit"] < 0.1).astype(float))
        return x.groupby("game_id")["d"].mean()
    if kind == "A1":
        x = d[d["questionable"] & d["stat"].isin(("carries", "targets"))].copy()
        side = np.sign(x["a0_err"].mean()) or 1.0
        x["d"] = side * (x["arm_err"] - x["a0_err"])
        return x.groupby("game_id")["d"].mean()
    raise ValueError(kind)


def min_sample(per_game: pd.Series, games_per_week: int = 16, floor: int = 64) -> dict:
    eff, sd = float(per_game.mean()), float(per_game.std(ddof=1))
    if not np.isfinite(eff) or eff >= 0:
        return {"effect": eff, "sd": sd, "n_games": None, "reason": "development effect is zero or in the wrong direction"}
    n = ((1.96 + 0.84) * sd / abs(eff)) ** 2
    n = max(floor, int(math.ceil(n / games_per_week)) * games_per_week)
    return {"effect": eff, "sd": sd, "n_games": n, "n_weeks": n // games_per_week, "n_seasons_at_285": round(n / 285, 2)}


# ---------------------------------------------------------------------------------- subgroups (S1)
def team_concentration(d: pd.DataFrame) -> pd.Series:
    """Team-game target HHI of the incumbent's expected targets, as terciles (LOW / MID / HIGH)."""
    t = d[d["stat"] == "targets"]
    sh = t["a0_mean"] / t.groupby(["game_id", "team"])["a0_mean"].transform("sum")
    hhi = (sh ** 2).groupby([t["game_id"], t["team"]]).sum()
    lab = pd.qcut(hhi.rank(method="first"), 3, labels=["LOW", "MID", "HIGH"])
    return lab


def subgroup_tables(d: pd.DataFrame, flags: pd.DataFrame | None = None, role: pd.Series | None = None) -> dict:
    out = {}
    conc = team_concentration(d)
    x = d.join(conc.rename("concentration"), on=["game_id", "team"])
    for lab, g in x.groupby("concentration", observed=True):
        out[f"concentration:{lab}"] = stat_table(g[g["stat"].isin(S1_STATS)])
    if role is not None:
        x = x.join(role.rename("role_instability"), on=["game_id", "team"])
        x["role_t"] = pd.qcut(x["role_instability"].rank(method="first"), 3, labels=["STABLE", "MID", "UNSTABLE"])
        for lab, g in x.groupby("role_t", observed=True):
            out[f"role:{lab}"] = stat_table(g[g["stat"].isin(S1_STATS)])
    if flags is not None:
        x = x.merge(flags, on=["game_id", "team", "player_id"], how="left")
        for c in ("TEAMMATE_OF_UNAVAILABLE_STARTER", "NEW_STARTER_NO_HISTORY"):
            if c in x:
                out[f"population:{c}"] = stat_table(x[x[c].fillna(False).astype(bool) & x["stat"].isin(S1_STATS)])
    return out


def arm_report(base_dir: str, arm_dir: str, seasons, stats, kind: str, extra=None) -> dict:
    """By-season and pooled stat tables, the primary with a game-clustered interval, and the per-game effects."""
    res = {"by_season": {}, "pooled": {}}
    alld = []
    for y in seasons:
        d = paired(base_dir, arm_dir, y, stats)
        if extra is not None:
            d = extra(d, y)
        alld.append(d)
        res["by_season"][str(y)] = {"stats": stat_table(d), "primary": _primary(d, kind)}
    D = pd.concat(alld, ignore_index=True)
    res["pooled"] = {"stats": stat_table(D), "primary": _primary(D, kind)}
    res["_rows"] = D
    return res


def _primary(d: pd.DataFrame, kind: str) -> dict:
    fn = {"S1": s1_primary, "Q1": q1_primary_delta, "A1": a1_primary_delta}[kind]
    return _boot(fn, d)
