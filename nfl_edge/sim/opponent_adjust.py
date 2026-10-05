"""OPPONENT-ADJUSTED TEAM RATINGS for the simulation layer -- a separate RESEARCH arm, not deployed.

The incumbent's ``off_*`` / ``def_*`` features are exponentially weighted averages of what a team did and what
its opponents did against it. A defence that has played four bad offences looks good on ``def_epa_play``; the
schedule leaks into the rating. This module removes it with the standard two-sided model, solved at every
(season, week) snapshot on STRICTLY EARLIER games only:

    y[g, t] = mu + off[t] + def[opp(g, t)] + h * home_sign[g, t] + e,      ridge on off and def toward 0

* weights: 0.5 ** (weeks_ago / 8) * 0.5 ** seasons_back -- the incumbent's ``team_halflife`` and
  ``team_season_carry``, so the recency/carry choice is not re-tuned here;
* window: the three previous seasons plus the current season's earlier weeks. Week 1 sees only previous
  seasons, discounted by the carry -- the previous-season prior is explicit, not implicit;
* ``mu`` is the weighted mean of the window (a statistic of earlier games only), and ridge shrinks every
  team toward it, so a team with few recent games is pulled to the league level;
* the ridge strength for evaluation season Y is chosen per metric from ``LAMBDAS`` by one-week-ahead squared
  error on seasons Y-2 and Y-1 only (``select_lambdas``) -- nothing of Y or later sets it.

The feature handed to a model is the MATCHUP expectation for the game: ``mx_<metric> = mu + off[team] +
def[opp] + h * home_sign``, attached to the team's own team-game row, so a model reads its opponent's
adjusted defence without a join (and without the incumbent's own-defence train/serve skew).

Preregistered: research/game_script_v2/PREREGISTRATION.md, section 5.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
import polars as pl

from . import data as D

ADJ_VERSION = "sim-oppadj-1.0.0"
HALFLIFE_WEEKS = 8.0
SEASON_CARRY = 0.5
WINDOW_SEASONS = 3
LAMBDAS = (1.0, 2.0, 4.0, 8.0, 16.0, 32.0)
METRICS = ("epa_play", "success_rate", "dropback_epa", "designed_rush_epa", "explosive_rate", "sack_rate", "plays",
           "sec_per_play", "neutral_pass_rate", "neutral_proe", "td_per_drive")
_IS_PLAY = pl.col("play_type").is_in(["run", "pass", "qb_kneel", "qb_spike"])


# ------------------------------------------------------------------------------------- metric table
def _pbp_extras(season: int) -> pl.DataFrame:
    """Per offence-game: EPA per dropback, EPA per designed rush, explosive plays."""
    d = D._read_pbp(season).filter(pl.col("posteam").is_not_null() & pl.col("season_type").is_in(["REG", "POST"]) & _IS_PLAY)
    designed = (pl.col("rush_attempt") == 1) & (pl.col("qb_scramble") == 0) & (pl.col("qb_kneel") == 0)
    passed = (pl.col("pass_attempt") == 1) & (pl.col("sack") == 0)
    return (d.group_by(["game_id", "posteam"]).agg([
        pl.col("epa").filter(pl.col("qb_dropback") == 1).mean().alias("dropback_epa"),
        pl.col("epa").filter(designed).mean().alias("designed_rush_epa"),
        ((passed & (pl.col("yards_gained") >= 20)) | ((pl.col("rush_attempt") == 1) & (pl.col("yards_gained") >= 10)))
        .sum().alias("_explosive")]).rename({"posteam": "team"}))


def metric_table(seasons) -> pd.DataFrame:
    """One row per (game, offence) with every rated metric, the opponent, the week order and the home sign."""
    tg = D.load("team_games", seasons).to_pandas()
    ex = pl.concat([_pbp_extras(s) for s in seasons if os.path.exists(os.path.join(D.RAW, "pbp", f"play_by_play_{s}.parquet"))]).to_pandas()
    t = tg.merge(ex, on=["game_id", "team"], how="left")
    t["explosive_rate"] = t["_explosive"] / t["plays"].clip(lower=1)
    t["sack_rate"] = t["sacks"] / t["dropbacks"].clip(lower=1)
    t["td_per_drive"] = t["off_td"] / t["drives"].clip(lower=1)
    sched = D.schedule().to_pandas()[["game_id", "location"]]
    t = t.merge(sched, on="game_id", how="left")
    t["home_sign"] = np.where(t["location"] == "Neutral", 0.0, np.where(t["home"], 1.0, -1.0))
    keep = ["game_id", "season", "week", "team", "opp", "home_sign"] + list(METRICS)
    return t[keep].sort_values(["season", "week", "game_id", "team"]).reset_index(drop=True)


# --------------------------------------------------------------------------------------- the solver
def _age(rows_season: np.ndarray, rows_week: np.ndarray, season: int, week: int, last_week: dict) -> np.ndarray:
    """Weeks between each prior row and the snapshot, counting through season boundaries."""
    same = rows_season == season
    age = np.where(same, week - rows_week, 0.0).astype(float)
    for s in np.unique(rows_season[~same]):
        m = rows_season == s
        # the rest of season s after the row, the seasons in between, and the current season's elapsed weeks
        between = sum(last_week.get(int(x), 18) for x in range(int(s) + 1, season))
        age[m] = (last_week.get(int(s), 18) - rows_week[m] + 1) + between + (week - 1)
    return age


def solve(prior: pd.DataFrame, metric: str, lam: float, season: int, week: int, last_week: dict) -> dict | None:
    """Weighted ridge offence/defence/home solution on the prior rows for one metric."""
    r = prior[np.isfinite(prior[metric].to_numpy(float))]
    if len(r) < 40:
        return None
    teams = sorted(set(r["team"]) | set(r["opp"]))
    idx = {t: i for i, t in enumerate(teams)}
    k = len(teams)
    y = r[metric].to_numpy(float)
    age = _age(r["season"].to_numpy(), r["week"].to_numpy(float), season, week, last_week)
    w = 0.5 ** (age / HALFLIFE_WEEKS) * SEASON_CARRY ** (season - r["season"].to_numpy(float))
    mu = float(np.average(y, weights=w))
    X = np.zeros((len(r), 2 * k + 1))
    X[np.arange(len(r)), [idx[t] for t in r["team"]]] = 1.0
    X[np.arange(len(r)), [k + idx[t] for t in r["opp"]]] = 1.0
    X[:, 2 * k] = r["home_sign"].to_numpy(float)
    Xw = X * w[:, None]
    pen = np.full(2 * k + 1, lam); pen[-1] = 1e-3
    beta = np.linalg.solve(X.T @ Xw + np.diag(pen), Xw.T @ (y - mu))
    return {"mu": mu, "off": {t: float(beta[i]) for t, i in idx.items()}, "def": {t: float(beta[k + i]) for t, i in idx.items()},
            "hfa": float(beta[-1]), "n": int(len(r)), "eff_n": float(w.sum())}


def snapshot_matchups(mt: pd.DataFrame, season: int, week: int, lams: dict, last_week: dict,
                      metrics=METRICS) -> pd.DataFrame:
    """mx_<metric> for every team-game of (season, week), from games strictly before it."""
    cur = mt[(mt["season"] == season) & (mt["week"] == week)]
    prior = mt[((mt["season"] < season) & (mt["season"] >= season - WINDOW_SEASONS)) | ((mt["season"] == season) & (mt["week"] < week))]
    out = cur[["game_id", "team", "opp", "home_sign"]].copy()
    for m in metrics:
        sol = solve(prior, m, lams[m], season, week, last_week)
        if sol is None:
            out[f"mx_{m}"] = np.nan
            continue
        out[f"mx_{m}"] = [sol["mu"] + sol["off"].get(t, 0.0) + sol["def"].get(o, 0.0) + sol["hfa"] * hs
                          for t, o, hs in zip(out["team"], out["opp"], out["home_sign"])]
    return out


def _last_weeks(mt: pd.DataFrame) -> dict:
    return {int(s): int(w) for s, w in mt.groupby("season")["week"].max().items()}


def matchup_features(mt: pd.DataFrame, seasons, lams: dict, metrics=METRICS) -> pd.DataFrame:
    lw = _last_weeks(mt)
    parts = []
    for s in seasons:
        for w in sorted(mt.loc[mt["season"] == s, "week"].unique()):
            parts.append(snapshot_matchups(mt, int(s), int(w), lams, lw, metrics))
    return pd.concat(parts, ignore_index=True)


def select_lambdas(mt: pd.DataFrame, eval_season: int, metrics=METRICS, lambdas=LAMBDAS) -> dict:
    """Per metric, the ridge strength with the lowest one-week-ahead squared error over seasons Y-2 and Y-1."""
    tune = [s for s in (eval_season - 2, eval_season - 1) if s in set(mt["season"])]
    if not tune:
        raise ValueError(f"no tuning seasons before {eval_season}")
    lw = _last_weeks(mt)
    errs = {m: {lam: [] for lam in lambdas} for m in metrics}
    for lam in lambdas:
        f = matchup_features(mt, tune, {m: lam for m in metrics}, metrics).merge(
            mt[["game_id", "team"] + list(metrics)], on=["game_id", "team"])
        for m in metrics:
            e = (f[f"mx_{m}"] - f[m]).to_numpy(float)
            errs[m][lam] = float(np.nanmean(e ** 2))
    chosen = {m: min(lambdas, key=lambda lam: (errs[m][lam], lam)) for m in metrics}
    return {"lambdas": chosen, "mse": {m: {str(k): v for k, v in errs[m].items()} for m in metrics}, "tune_seasons": tune}


# ------------------------------------------------------------------------------- primitive diagnostic
def snapshot_unadjusted(mt: pd.DataFrame, season: int, week: int, last_week: dict, metrics=METRICS) -> pd.DataFrame:
    """The same window and weights WITHOUT the opponent model: what the team did plus what the opponent allowed,
    minus the window mean. Isolates the adjustment in the primitive diagnostic."""
    cur = mt[(mt["season"] == season) & (mt["week"] == week)]
    prior = mt[((mt["season"] < season) & (mt["season"] >= season - WINDOW_SEASONS)) | ((mt["season"] == season) & (mt["week"] < week))]
    out = cur[["game_id", "team", "opp"]].copy()
    age = _age(prior["season"].to_numpy(), prior["week"].to_numpy(float), season, week, last_week)
    w = 0.5 ** (age / HALFLIFE_WEEKS) * SEASON_CARRY ** (season - prior["season"].to_numpy(float))
    for m in metrics:
        y = prior[m].to_numpy(float); ok = np.isfinite(y)
        if ok.sum() < 40:
            out[f"ux_{m}"] = np.nan
            continue
        mu = float(np.average(y[ok], weights=w[ok]))
        d = pd.DataFrame({"team": prior["team"].to_numpy()[ok], "opp": prior["opp"].to_numpy()[ok], "y": y[ok], "w": w[ok]})
        d["wy"] = d["w"] * d["y"]
        o = d.groupby("team")[["wy", "w"]].sum(); a = d.groupby("opp")[["wy", "w"]].sum()
        off = (o["wy"] / o["w"]).to_dict(); dfn = (a["wy"] / a["w"]).to_dict()
        out[f"ux_{m}"] = [off.get(t, mu) + dfn.get(op, mu) - mu for t, op in zip(out["team"], out["opp"])]
    return out


def primitive_diagnostic(mt: pd.DataFrame, season: int, lams: dict, metrics=METRICS) -> dict:
    """One-week-ahead error of the adjusted matchup vs the unadjusted pair, every week of ``season``."""
    lw = _last_weeks(mt)
    parts = []
    for w in sorted(mt.loc[mt["season"] == season, "week"].unique()):
        a = snapshot_matchups(mt, season, int(w), lams, lw, metrics)
        u = snapshot_unadjusted(mt, season, int(w), lw, metrics)
        parts.append(a.merge(u, on=["game_id", "team", "opp"]))
    f = pd.concat(parts, ignore_index=True).merge(mt[["game_id", "team"] + list(metrics)], on=["game_id", "team"])
    out = {}
    for m in metrics:
        ok = f[[m, f"mx_{m}", f"ux_{m}"]].notna().all(axis=1)
        y = f.loc[ok, m].to_numpy(float); ea = y - f.loc[ok, f"mx_{m}"].to_numpy(float); eu = y - f.loc[ok, f"ux_{m}"].to_numpy(float)
        g = f.loc[ok, "game_id"].to_numpy()
        out[m] = {"n": int(ok.sum()), "rmse_adjusted": float(np.sqrt(np.mean(ea ** 2))), "rmse_unadjusted": float(np.sqrt(np.mean(eu ** 2))),
                  "mse_diff_by_game": _game_cluster_mean(ea ** 2 - eu ** 2, g),
                  "corr_adjusted": float(np.corrcoef(y, y - ea)[0, 1]), "corr_unadjusted": float(np.corrcoef(y, y - eu)[0, 1])}
    return out


def _game_cluster_mean(x: np.ndarray, g: np.ndarray, B: int = 2000, seed: int = 20261005) -> dict:
    """Mean of x with a game-clustered bootstrap 95% interval."""
    df = pd.DataFrame({"g": g, "x": x}).groupby("g")["x"].agg(["sum", "size"])
    s, n = df["sum"].to_numpy(), df["size"].to_numpy()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(s), size=(B, len(s)))
    boots = s[idx].sum(axis=1) / n[idx].sum(axis=1)
    return {"mean": float(s.sum() / n.sum()), "lo": float(np.quantile(boots, 0.025)), "hi": float(np.quantile(boots, 0.975))}
