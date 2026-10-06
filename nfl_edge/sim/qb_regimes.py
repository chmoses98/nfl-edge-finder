"""Q1 -- quarterback starter-share regimes. RESEARCH_ONLY.

Preregistered in research/game_script_v2/wave2/PREREGISTRATION.md, section 3.

The simulated QB1 (`inputs._qb1`) takes a share of the team's pass attempts drawn per row. The incumbent fits that
share's distribution only on depth-chart QB1 rows WITH attempts, so the starter who was active but did not play the
expected role never enters it. Q1 models the share as a mixture of three regimes of the SIMULATED QB1's realised
share -- FULL >= 0.90, PARTIAL 0.25-0.90, LOW < 0.25 (zero included) -- with regime probabilities from a
multinomial logistic on pregame features, and each regime's share from its empirical training distribution.

The game's share distribution is handed to the simulator as 201 quantiles of the mixture, which it samples exactly as
it samples the incumbent's quantiles (ONE uniform per row), so every other random draw is unchanged. The team's pass
attempts and the receivers' targets never depend on which quarterback throws; Q1 cannot move them.

Reported separately, never merged: IDENTIFICATION ERROR (the simulated QB1 did not throw the team's first pass) and
EXIT / PARTIAL GAME (he threw it and finished below 0.90).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
import polars as pl

from . import data as D

Q1_VERSION = "sim-q1-1.0.0"
REGIMES = ("FULL", "PARTIAL", "LOW")
FULL_MIN, LOW_MAX = 0.90, 0.25
FEATURES = ("q1_last_game_starter", "q1_starts_last4", "q1_questionable", "q1_first_start_for_team",
            "q1_returning_from_absence", "q1_low_history", "q1_other_viable_qb")
RIDGE = 1.0


def regime_of(share) -> np.ndarray:
    s = np.asarray(share, float)
    return np.where(s >= FULL_MIN, 0, np.where(s >= LOW_MAX, 1, 2))


def first_passers(seasons) -> pd.DataFrame:
    """The passer of each team-game's first pass attempt (sacks excluded), from play-by-play."""
    out = []
    for s in seasons:
        p = os.path.join(D.RAW, "pbp", f"play_by_play_{s}.parquet")
        if not os.path.exists(p):
            continue
        d = D._read_pbp(s).filter(pl.col("posteam").is_not_null() & (pl.col("pass_attempt") == 1) & (pl.col("sack") == 0)
                                  & pl.col("passer_player_id").is_not_null())
        f = d.sort(["game_id", "play_id"]).group_by(["game_id", "posteam"], maintain_order=True).agg(
            pl.first("passer_player_id").alias("first_passer"), pl.first("season"), pl.first("week"))
        out.append(f.rename({"posteam": "team"}))
    return pl.concat(out).to_pandas() if out else pd.DataFrame(columns=["game_id", "team", "first_passer", "season", "week"])


def _team_history(seasons) -> pd.DataFrame:
    """Per team-game in chronological order: who started (first passer)."""
    fp = first_passers(seasons)
    return fp.sort_values(["team", "season", "week", "game_id"]).reset_index(drop=True)


def attach_features(frames: dict) -> dict:
    """Add the preregistered q1_* pregame features to every eligible QB row (strictly prior team-games only)."""
    e = frames["eligible"]
    seasons = sorted(int(s) for s in e["season"].unique())
    hist = _team_history(seasons)
    pg = D.load("player_games", seasons).to_pandas()[["game_id", "player_id", "attempts", "season", "week"]]
    # cumulative prior career attempts per player, strictly before each game
    order = {g: i for i, g in enumerate(D.schedule().to_pandas().sort_values(["season", "week", "game_id"])["game_id"])}
    pg = pg.assign(_o=pg["game_id"].map(order).fillna(1e12)).sort_values(["player_id", "_o"])
    career = {pid: (g["_o"].to_numpy(), np.cumsum(g["attempts"].fillna(0).to_numpy())) for pid, g in pg.groupby("player_id")}

    def prior_attempts(pid, k):
        o, c = career.get(pid, (np.array([]), np.array([])))
        j = np.searchsorted(o, k, side="left")          # games strictly before order k
        return float(c[j - 1]) if j > 0 else 0.0
    hist = hist.assign(_o=hist["game_id"].map(order).fillna(1e12))
    team_seq = {t: g.sort_values("_o").reset_index(drop=True) for t, g in hist.groupby("team")}
    out = e.copy()
    for c in FEATURES:
        out[c] = np.nan
    qb = out[out["position"] == "QB"]
    rows = {}
    for idx, r in qb.iterrows():
        seq = team_seq.get(r["team"])
        if seq is None:
            continue
        k = order.get(r["game_id"])
        prior = seq[seq["_o"] < k]
        last4 = prior.tail(4)
        starts_all = (prior["first_passer"] == r["player_id"])
        last_start = bool(len(prior)) and prior.iloc[-1]["first_passer"] == r["player_id"]
        mates = qb[(qb["game_id"] == r["game_id"]) & (qb["team"] == r["team"]) & (qb["player_id"] != r["player_id"])]["player_id"]
        pa = prior_attempts(r["player_id"], k)
        rows[idx] = {"q1_last_game_starter": float(last_start),
                     "q1_starts_last4": float((last4["first_passer"] == r["player_id"]).mean()) if len(last4) else 0.0,
                     "q1_questionable": float(r.get("avail_state") == "QUESTIONABLE"),
                     "q1_first_start_for_team": float(not starts_all.any()),
                     "q1_returning_from_absence": float(starts_all.any() and not last_start and len(prior) > 0
                                                        and prior.iloc[-1]["first_passer"] != r["player_id"]),
                     "q1_low_history": float(pa < 100),
                     "q1_other_viable_qb": float(last4["first_passer"].isin(set(mates)).any())}
    f = pd.DataFrame.from_dict(rows, orient="index")
    for c in FEATURES:
        out.loc[f.index, c] = f[c]
    frames = dict(frames); frames["eligible"] = out
    return frames


# ------------------------------------------------------------------------------------------- labels
def qb1_rows(elig: pd.DataFrame) -> pd.DataFrame:
    """The simulated QB1 of each team-game (inputs._qb1's rule) with its realised share of team pass attempts."""
    q = elig[elig["position"] == "QB"].copy()
    q = q.sort_values(["game_id", "team", "dc_rank", "sh_attempt_l"], ascending=[True, True, True, False], na_position="last")
    q = q.drop_duplicates(["game_id", "team"])
    q = q[q["team_pass_att"].fillna(0) > 0]
    q["share"] = (q["attempts"].fillna(0) / q["team_pass_att"]).clip(0, 1)
    q["regime"] = regime_of(q["share"])
    return q


def label_errors(q: pd.DataFrame) -> pd.DataFrame:
    fp = first_passers(sorted(int(s) for s in q["season"].unique()))
    q = q.merge(fp[["game_id", "team", "first_passer"]], on=["game_id", "team"], how="left")
    q["identification_error"] = q["first_passer"].notna() & (q["first_passer"] != q["player_id"])
    q["exit_partial"] = (~q["identification_error"]) & (q["share"] < FULL_MIN)
    return q


# ------------------------------------------------------------------------------------------- model
def fit(q: pd.DataFrame, conditional: bool = True) -> dict:
    """Regime model + within-regime share quantiles from TRAINING QB1 rows."""
    y = q["regime"].to_numpy(int)
    shares = q["share"].to_numpy(float)
    regq = {}
    for k in range(3):
        s = shares[y == k]
        regq[REGIMES[k]] = np.quantile(s if len(s) >= 20 else shares, np.linspace(0, 1, 201)).tolist()
    freq = (np.bincount(y, minlength=3) + 1.0) / (len(y) + 3.0)
    out = {"version": Q1_VERSION, "form": "Q1" if conditional else "Q1-0", "regime_quantiles": regq,
           "unconditional": freq.tolist(), "n": int(len(y)), "features": list(FEATURES) if conditional else []}
    if conditional:
        X = q[list(FEATURES)].to_numpy(float)
        mu = np.nanmean(X, axis=0); sd = np.nanstd(X, axis=0); sd[sd == 0] = 1.0
        Z = (np.where(np.isfinite(X), X, mu) - mu) / sd
        coef, icpt = _multinomial_ridge(Z, np.asarray(y, int), RIDGE)
        for c in range(3):
            if not np.any(np.asarray(y) == c):    # a class never seen: fall back to unconditional for it
                coef[c] = 0.0; icpt[c] = -20.0
        out.update({"coef": coef.tolist(), "intercept": icpt.tolist(), "mu": mu.tolist(), "sd": sd.tolist()})
    return out


def _multinomial_ridge(Z: np.ndarray, y: np.ndarray, ridge: float, k: int = 3):
    """Multinomial logistic regression, sum of log losses + ridge/2 * ||coef||^2 (intercepts unpenalised) -- the
    objective of scikit-learn's LogisticRegression(C=1/ridge) with the lbfgs solver, without the dependency."""
    from scipy.optimize import minimize
    n, p = Z.shape
    Y = np.zeros((n, k)); Y[np.arange(n), y] = 1.0

    def f(theta):
        W = theta[:k * p].reshape(k, p); b = theta[k * p:]
        eta = Z @ W.T + b
        eta -= eta.max(axis=1, keepdims=True)
        lse = np.log(np.exp(eta).sum(axis=1))
        P = np.exp(eta - lse[:, None])
        loss = float((lse - (eta * Y).sum(axis=1)).sum() + 0.5 * ridge * (W ** 2).sum())
        G = P - Y
        return loss, np.concatenate([(G.T @ Z + ridge * W).ravel(), G.sum(axis=0)])

    r = minimize(f, np.zeros(k * p + k), jac=True, method="L-BFGS-B", options={"maxiter": 5000, "gtol": 1e-8})
    return r.x[:k * p].reshape(k, p).copy(), r.x[k * p:].copy()


def probabilities(model: dict, X: np.ndarray) -> np.ndarray:
    X = np.atleast_2d(np.asarray(X, float))
    if not model.get("features"):
        return np.tile(np.asarray(model["unconditional"]), (len(X), 1))
    mu, sd = np.asarray(model["mu"]), np.asarray(model["sd"])
    Z = (np.where(np.isfinite(X), X, mu) - mu) / sd
    eta = Z @ np.asarray(model["coef"]).T + np.asarray(model["intercept"])
    eta -= eta.max(axis=1, keepdims=True)
    p = np.exp(eta)
    return p / p.sum(axis=1, keepdims=True)


def mixture_quantiles(model: dict, pi: np.ndarray, n_grid: int = 2001) -> list:
    """201 quantiles of sum_k pi_k F_k, with F_k the regime's empirical distribution (its 201 stored quantiles)."""
    grid = np.linspace(0, 1, n_grid)
    F = np.zeros(n_grid)
    for k, name in enumerate(REGIMES):
        q = np.asarray(model["regime_quantiles"][name])
        F += pi[k] * np.searchsorted(q, grid, side="right") / len(q)
    F = np.maximum.accumulate(np.clip(F, 0, 1))
    levels = np.linspace(0, 1, 201)
    # generalised inverse: the smallest share whose mixture CDF reaches the level
    idx = np.minimum(np.searchsorted(F, levels - 1e-12, side="left"), n_grid - 1)
    return grid[idx].tolist()


def game_quantiles(model: dict, qb_row) -> list:
    x = np.array([[float(qb_row.get(f, np.nan)) if hasattr(qb_row, "get") else np.nan for f in model.get("features", [])]])
    pi = probabilities(model, x)[0] if model.get("features") else np.asarray(model["unconditional"])
    return mixture_quantiles(model, pi)
