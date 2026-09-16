"""The fitted primitives of the simulation layer.

Each ``fit_*`` takes TRAINING rows only (the caller decides the seasons) and returns a plain dict
artifact -- coefficients, empirical banks and the seasons it saw -- that ``simulate.py`` consumes and
``backtest.py`` re-fits walk-forward.  Nothing here reads a market price.

  game environment   plays per team and pass rate per team, conditional on the REALISED game script
                     (margin, total) so that a simulated 14-point lead lowers the pass rate on that row;
                     touchdowns given points; the pass/rush split of touchdowns.
  opportunity        a player's share of the team's designed carries / targets: propensity from strictly
                     prior usage, depth-chart rank and position, renormalised over the players who are
                     actually available, then a Dirichlet-multinomial draw with a fitted concentration.
  efficiency         expected yards per carry / per target from the runner's or receiver's own history,
                     the opponent's history and the team's, then EMPIRICAL per-touch outcomes drawn from
                     the training bank in the bin of that expected value, plus a fitted per-game shock so
                     the sum over touches is not under-dispersed.
  touchdowns         allocation weights inside the team's simulated touchdown count.

All regressions are ridge on standardised columns with an unpenalised intercept (numpy only).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import SIM_VERSION

MODELS_VERSION = "sim-models-1.0.0"


# ------------------------------------------------------------------------------------------ ridge
def ridge_fit(X: np.ndarray, y: np.ndarray, lam: float = 1.0, w: np.ndarray | None = None) -> dict:
    """Ridge with standardised columns and an unpenalised intercept.  NaNs in X are set to the column mean."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    ok = np.isfinite(y)
    X, y = X[ok], y[ok]
    w = np.ones(len(y)) if w is None else np.asarray(w, float)[ok]
    mu = np.nanmean(X, axis=0); sd = np.nanstd(X, axis=0); sd[sd == 0] = 1.0
    Z = (np.where(np.isfinite(X), X, mu) - mu) / sd
    Zw = Z * w[:, None]
    A = Z.T @ Zw + lam * np.eye(Z.shape[1])
    ybar = np.average(y, weights=w)
    beta = np.linalg.solve(A, Zw.T @ (y - ybar))
    pred = ybar + Z @ beta
    resid = y - pred
    return {"beta": beta.tolist(), "mu": mu.tolist(), "sd": sd.tolist(), "intercept": float(ybar), "lam": lam,
            "resid_sd": float(np.sqrt(np.average(resid ** 2, weights=w))), "n": int(len(y))}


def ridge_predict(m: dict, X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, float)
    mu = np.asarray(m["mu"]); sd = np.asarray(m["sd"])
    Z = (np.where(np.isfinite(X), X, mu) - mu) / sd
    return m["intercept"] + Z @ np.asarray(m["beta"])


def logistic_fit(X: np.ndarray, y: np.ndarray, lam: float = 1.0, iters: int = 30) -> dict:
    """Ridge-penalised logistic regression by IRLS on standardised columns."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    ok = np.isfinite(y); X, y = X[ok], y[ok]
    mu = np.nanmean(X, axis=0); sd = np.nanstd(X, axis=0); sd[sd == 0] = 1.0
    Z = (np.where(np.isfinite(X), X, mu) - mu) / sd
    Z1 = np.column_stack([np.ones(len(y)), Z])
    b = np.zeros(Z1.shape[1]); b[0] = np.log((y.mean() + 1e-6) / (1 - y.mean() + 1e-6))
    P = np.eye(Z1.shape[1]) * lam; P[0, 0] = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(Z1 @ b))); wv = p * (1 - p) + 1e-9
        g = Z1.T @ (y - p) - P @ b
        H = (Z1 * wv[:, None]).T @ Z1 + P
        step = np.linalg.solve(H, g)
        b = b + step
        if np.max(np.abs(step)) < 1e-8:
            break
    return {"beta": b[1:].tolist(), "intercept": float(b[0]), "mu": mu.tolist(), "sd": sd.tolist(), "n": int(len(y))}


def logistic_predict(m: dict, X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, float)
    mu = np.asarray(m["mu"]); sd = np.asarray(m["sd"])
    Z = (np.where(np.isfinite(X), X, mu) - mu) / sd
    return 1 / (1 + np.exp(-(m["intercept"] + Z @ np.asarray(m["beta"]))))


# ------------------------------------------------------------------------------- game environment
PLAYS_FEATURES = ["off_plays", "def_plays", "off_sec_per_play", "def_sec_per_play", "off_neutral_pass_rate",
                  "game_total", "abs_margin", "team_margin", "home"]
PASS_RATE_FEATURES = ["off_neutral_pass_rate", "off_pass_rate", "off_proe", "def_pass_rate", "def_neutral_pass_rate",
                      "team_margin", "team_margin_sq", "game_total", "home"]
PASS_TD_SHARE_FEATURES = ["off_pass_td_share", "def_pass_td_share", "pass_rate", "team_margin"]
MAX_TD = 9


def _env_design(tf: pd.DataFrame) -> pd.DataFrame:
    d = tf.copy()
    d["game_total"] = d["total"].astype(float)
    d["team_margin"] = d["margin"].astype(float)
    d["abs_margin"] = d["team_margin"].abs()
    d["team_margin_sq"] = d["team_margin"] ** 2
    d["home"] = d["home"].astype(float)
    return d


def fit_game_env(tf: pd.DataFrame) -> dict:
    """Fit the volume/split models on team-game rows that already carry the prior-only features."""
    d = _env_design(tf)
    d = d[d["team_n_prior"] >= 4]
    plays = ridge_fit(d[PLAYS_FEATURES].to_numpy(float), d["plays"].to_numpy(float), lam=1.0)
    pr = ridge_fit(d[PASS_RATE_FEATURES].to_numpy(float), d["pass_rate"].to_numpy(float), lam=1.0)
    # residual correlation between the two teams of one game (pace is shared)
    d = d.assign(_rp=d["plays"] - ridge_predict(plays, d[PLAYS_FEATURES].to_numpy(float)),
                 _rr=d["pass_rate"] - ridge_predict(pr, d[PASS_RATE_FEATURES].to_numpy(float)))
    pair = d.merge(d[["game_id", "team", "_rp", "_rr"]].rename(columns={"team": "opp", "_rp": "_rp_o", "_rr": "_rr_o"}),
                   on=["game_id", "opp"], how="inner")
    rho_plays = float(np.corrcoef(pair["_rp"], pair["_rp_o"])[0, 1])
    rho_pr = float(np.corrcoef(pair["_rr"], pair["_rr_o"])[0, 1])
    # touchdowns given points: smoothed empirical table P(off_td = t | points = p)
    tbl = np.ones((80, MAX_TD + 1)) * 0.02
    pts = d["points"].to_numpy(int).clip(0, 79); td = d["off_td"].to_numpy(int).clip(0, MAX_TD)
    for p_, t_ in zip(pts, td):
        tbl[p_, t_] += 1.0
    # pool sparse rows toward neighbours so 1-2-point score gaps do not produce empty rows
    pooled = tbl.copy()
    for p_ in range(80):
        lo, hi = max(0, p_ - 1), min(79, p_ + 1)
        if tbl[p_].sum() < 30:
            pooled[p_] = tbl[lo:hi + 1].sum(axis=0)
    pooled = pooled / pooled.sum(axis=1, keepdims=True)
    # pass share of touchdowns
    dd = d[d["off_td"] > 0]
    pts_share = logistic_fit(np.repeat(dd[PASS_TD_SHARE_FEATURES].to_numpy(float), dd["off_td"].to_numpy(int), axis=0),
                             np.concatenate([np.r_[np.ones(int(a)), np.zeros(int(b))] for a, b in zip(dd["pass_td"], dd["rush_td"])]),
                             lam=1.0)
    league = {"target_rate": float(d["targets"].sum() / d["pass_att"].sum()),
              "kneels_leading": float(d.loc[d["margin"] > 0, "kneels"].mean()),
              "kneels_trailing": float(d.loc[d["margin"] <= 0, "kneels"].mean()),
              "sack_rate": float(d["sacks"].sum() / d["dropbacks"].sum()),
              "scramble_rate": float(d["scrambles"].sum() / d["dropbacks"].sum()),
              "kneels": float(d["kneels"].mean())}
    return {"version": MODELS_VERSION, "plays": plays, "pass_rate": pr, "rho_plays": rho_plays, "rho_pass_rate": rho_pr,
            "td_given_points": pooled.tolist(), "pass_td_share": pts_share, "league": league,
            "train_seasons": sorted(int(s) for s in d["season"].unique()), "n_rows": int(len(d))}


# ------------------------------------------------------------------------------------- opportunity
GROUP_OF = {"RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE", "QB": "QB"}
SHARE_FEATURES = {
    "carry": ["sh_carry_s", "sh_carry_l", "last_sh_carry", "snap_share_s", "snap_share_l", "sh_rz_carry_l",
              "dc1", "dc2", "dc3", "dc_unlisted", "is_rb", "is_qb", "is_wr", "is_te", "is_fb", "no_history", "long_gap",
              "w_short", "prior_share", "prior_x_nohist"],
    "target": ["sh_target_s", "sh_target_l", "last_sh_target", "snap_share_s", "snap_share_l", "sh_rz_target_l",
               "dc1", "dc2", "dc3", "dc_unlisted", "is_rb", "is_qb", "is_wr", "is_te", "is_fb", "no_history", "long_gap",
               "w_short", "prior_share", "prior_x_nohist"],
}


def _cell(d: pd.DataFrame) -> pd.Series:
    rank = d["dc_rank"].astype(float)
    r = np.where(rank.isna(), "u", np.where(rank >= 3, "3", rank.fillna(0).astype(int).astype(str)))
    return d["position"].astype(str) + ":" + pd.Series(r, index=d.index)


def cell_priors(pf_elig: pd.DataFrame) -> dict:
    """Mean realised share by (position, depth-chart rank) over the training rows: the prior for a player
    with no usable history, and a feature for everyone."""
    c = _cell(pf_elig)
    g = pf_elig["y_share"].groupby(c).agg(["mean", "size"])
    g = g[g["size"] >= 30]
    return {k: float(v) for k, v in g["mean"].items()}


def share_design(pf: pd.DataFrame, kind: str, priors: dict | None = None) -> np.ndarray:
    d = pf.copy()
    pri = _cell(d).map(priors or {}).astype(float)
    d["prior_share"] = pri.fillna(0.0)
    rank = d["dc_rank"].astype(float)
    d["dc1"] = (rank == 1).astype(float); d["dc2"] = (rank == 2).astype(float); d["dc3"] = (rank >= 3).astype(float)
    d["dc_unlisted"] = rank.isna().astype(float)
    for p in ("rb", "qb", "wr", "te", "fb"):
        d[f"is_{p}"] = (d["position"] == p.upper()).astype(float)
    d["no_history"] = (d["n_prior"].fillna(0) == 0).astype(float)
    d["long_gap"] = (d["gap_weeks"].fillna(0) >= 4).astype(float)
    d["w_short"] = d[f"sh_{kind}_s_w"].fillna(0.0).clip(upper=6.0)
    for c in SHARE_FEATURES[kind]:
        if c.startswith("sh_") or c.startswith("last_"):
            # no usable history -> the depth-rank prior stands in for it (a rookie RB1 is projected as an RB1,
            # not as the average eligible player)
            d[c] = d[c].astype(float).fillna(d["prior_share"])
        elif c.startswith("snap_"):
            d[c] = d[c].astype(float)
    d["prior_x_nohist"] = d["prior_share"] * d["no_history"]
    return d[SHARE_FEATURES[kind]].to_numpy(float)


def fit_share_model(pf_elig: pd.DataFrame, kind: str) -> dict:
    """``pf_elig`` = eligible player-games (point-in-time eligibility) with the realised share column
    ``y_share`` (share of the team's designed carries or targets, zero for the eligible who got none)."""
    priors = cell_priors(pf_elig)
    X = share_design(pf_elig, kind, priors)
    y = pf_elig["y_share"].to_numpy(float)
    m = ridge_fit(X, y, lam=3.0)
    pred = np.clip(ridge_predict(m, X), 0.0, None)
    # renormalise within team-game the way the simulator will, then fit the Dirichlet concentration by
    # moments on the renormalised expectation: Var(share) = p(1-p)/(alpha+1)
    g = pf_elig[["game_id", "team"]].copy(); g["p"] = pred; g["y"] = y
    tot = g.groupby(["game_id", "team"])["p"].transform("sum").clip(lower=1e-6)
    g["p"] = g["p"] / tot
    mask = (g["p"] > 0.02) & (g["p"] < 0.98)
    v = ((g["y"] - g["p"]) ** 2)[mask]; pq = (g["p"] * (1 - g["p"]))[mask]
    alpha = float(pq.sum() / v.sum() - 1.0)
    alpha = float(np.clip(alpha, 2.0, 200.0))
    # share of the team's volume that goes to players OUTSIDE the eligible set (OL, defenders, uncatalogued)
    return {"kind": kind, "ridge": m, "alpha": alpha, "features": SHARE_FEATURES[kind], "n": int(len(y)), "priors": priors,
            "mean_abs_error": float(np.mean(np.abs(g["y"] - g["p"])))}


# --------------------------------------------------------------------------------------- efficiency
CARRY_FEATURES = ["rt_ypc", "prior_ypc", "def_ypc", "off_ypc", "rt_explosive_rate", "is_qb", "is_wr", "team_margin", "home",
                  "rt_ypc_n"]
TARGET_FEATURES = ["rt_ypt", "prior_ypt", "rt_catch_rate", "rt_adot", "def_ypa", "off_ypa", "def_comp_rate", "off_comp_rate",
                   "is_rb", "is_te", "is_wr", "team_margin", "home", "rt_ypt_n"]
N_BINS = 6


def _eff_design(df: pd.DataFrame, feats: list[str]) -> np.ndarray:
    d = df.copy()
    for p in ("rb", "qb", "wr", "te"):
        d[f"is_{p}"] = (d["position"] == p.upper()).astype(float)
    d["home"] = d["home"].astype(float)
    d["team_margin"] = d["team_margin"].astype(float)
    return d[feats].to_numpy(float)


def _bin_edges(pred: np.ndarray, n_bins: int) -> list[float]:
    q = np.quantile(pred, np.linspace(0, 1, n_bins + 1)[1:-1])
    return [float(x) for x in q]


def _bin_index(pred: np.ndarray, edges: list[float]) -> np.ndarray:
    return np.searchsorted(np.asarray(edges), pred, side="right")


def fit_carry_model(carries: pd.DataFrame) -> dict:
    """``carries``: one row per training carry joined with the runner's prior-only features and the team
    context (team_margin realised).  Scrambles and kneels are modelled separately (flat empirical banks)."""
    c = carries[(carries["qb_scramble"] == 0) & (carries["qb_kneel"] == 0)].copy()
    X = _eff_design(c, CARRY_FEATURES); y = c["yards"].to_numpy(float)
    m = ridge_fit(X, y, lam=5.0)
    pred = ridge_predict(m, X)
    edges = _bin_edges(pred, N_BINS)
    b = _bin_index(pred, edges)
    banks = []
    for k in range(N_BINS):
        yy = np.sort(y[b == k])
        banks.append({"mean": float(yy.mean()), "sd": float(yy.std()), "n": int(len(yy)),
                      "quantiles": np.quantile(yy, np.linspace(0, 1, 201)).tolist()})
    # centre each bank on its own model mean so that a player's expected value shifts the bank additively
    scr = carries[carries["qb_scramble"] == 1]["yards"].to_numpy(float)
    kneel = carries[carries["qb_kneel"] == 1]["yards"].to_numpy(float)
    # per-game shock: E[(Y - k mu)^2] = k sigma_bin^2 + k^2 tau^2, fitted on player-games
    c["_pred"] = pred; c["_sd2"] = np.asarray([banks[i]["sd"] ** 2 for i in b])
    pg = c.groupby(["game_id", "player_id"]).agg(y=("yards", "sum"), mu=("_pred", "sum"), s2=("_sd2", "sum"), k=("yards", "size"))
    pg = pg[pg["k"] >= 3]
    r2 = (pg["y"] - pg["mu"]) ** 2 - pg["s2"]
    tau2 = float(max(0.0, (r2 * pg["k"] ** 2).sum() / (pg["k"] ** 4).sum()))
    return {"ridge": m, "features": CARRY_FEATURES, "edges": edges, "banks": banks, "tau2": tau2,
            "scramble_quantiles": np.quantile(scr, np.linspace(0, 1, 201)).tolist() if len(scr) else [0.0] * 201,
            "kneel_mean": float(kneel.mean()) if len(kneel) else -1.0, "n": int(len(y))}


def fit_target_model(targets: pd.DataFrame) -> dict:
    """Per-target outcome as (complete, yards | complete).  Catch probability is a logistic; expected yards per
    target is a ridge; the empirical bank of yards-given-completion is binned on both predictions so a
    5-yard-aDOT back and a 15-yard-aDOT wideout do not share a distribution.  In simulation a target is
    completed with the player's own catch probability and, if complete, draws yards from the cell's bank
    rescaled to the player's expected yards per reception."""
    t = targets.copy()
    Xc = _eff_design(t, TARGET_FEATURES)
    catch = logistic_fit(Xc, t["complete"].to_numpy(float), lam=1.0)
    ypt = ridge_fit(Xc, t["yards"].to_numpy(float), lam=5.0)
    pc = logistic_predict(catch, Xc); py = ridge_predict(ypt, Xc)
    c_edges = _bin_edges(pc, 3); y_edges = _bin_edges(py, 4)
    cb = _bin_index(pc, c_edges); yb = _bin_index(py, y_edges)
    cells = {}
    comp = t["complete"].to_numpy(int); yds = t["yards"].to_numpy(float)
    for i in range(3):
        for j in range(4):
            m = (cb == i) & (yb == j) & (comp == 1)
            if m.sum() < 100:
                m = (yb == j) & (comp == 1)
            cy = yds[m]
            cells[f"{i}_{j}"] = {"yc_quantiles": np.quantile(cy, np.linspace(0, 1, 201)).tolist(), "ypr": float(cy.mean()),
                                 "sd": float(cy.std()), "n": int(m.sum())}
    t["_pred"] = py; t["_cell"] = [f"{i}_{j}" for i, j in zip(cb, yb)]
    t["_sd2"] = [cells[k]["sd"] ** 2 for k in t["_cell"]]
    pg = t.groupby(["game_id", "player_id"]).agg(y=("yards", "sum"), mu=("_pred", "sum"), s2=("_sd2", "sum"), k=("yards", "size"))
    pg = pg[pg["k"] >= 3]
    r2 = (pg["y"] - pg["mu"]) ** 2 - pg["s2"]
    tau2 = float(max(0.0, (r2 * pg["k"] ** 2).sum() / (pg["k"] ** 4).sum()))
    return {"catch": catch, "ypt": ypt, "features": TARGET_FEATURES, "c_edges": c_edges, "y_edges": y_edges,
            "cells": cells, "tau2": tau2, "n": int(len(t))}


# --------------------------------------------------------------------------------------- touchdowns
def fit_td_weights(pf: pd.DataFrame) -> dict:
    """Touchdown allocation.  Rush TDs are allocated in proportion to (official carries x relative per-carry
    TD propensity ^ gamma), pass TDs to (targets x relative per-target TD propensity ^ gamma), where the
    propensity is the player's own prior-only exposure-weighted TD rate relative to the POOLED rate (so a
    quarterback with a goal-line role is weighted like one, not like the average quarterback).  The
    exponents are fitted by comparing realised TD shares with touch shares on the training rows."""
    d = pf[(pf["team_rush_td"] > 0) | (pf["team_pass_td"] > 0)].copy()
    out = {}
    for kind, touches, team_td, td, rate in (("rush", "carries", "team_rush_td", "rush_td", "rt_rush_td_rate"),
                                              ("pass", "targets", "team_pass_td", "rec_td", "rt_rec_td_rate")):
        s = d[d[team_td] > 0].copy()
        s["touch_share"] = s[touches] / s.groupby(["game_id", "team"])[touches].transform("sum").clip(lower=1)
        s["td_share"] = s[td] / s[team_td]
        s = s[s[touches] > 0]
        pooled = float(pf[td].sum() / max(1.0, pf[touches].sum()))
        rel = (s[rate] / pooled).clip(0.2, 5.0)
        best, best_err = 0.0, np.inf
        for gam in np.linspace(0.0, 2.0, 21):
            w = s["touch_share"] * rel ** gam
            w = w / w.groupby([s["game_id"], s["team"]]).transform("sum").clip(lower=1e-9)
            err = float(np.mean((w - s["td_share"]) ** 2))
            if err < best_err:
                best, best_err = float(gam), err
        out[kind] = {"gamma": best, "mse": best_err, "rate": rate, "pooled_rate": pooled, "n": int(len(s))}
    return out


# ------------------------------------------------------------------------------------ QB starter
def fit_qb_share(elig: pd.DataFrame) -> dict:
    """The share of a team's pass attempts taken by its depth-chart QB1 on the training rows: mostly 1.0,
    with a real left tail (benched, hurt in game, the chart was stale).  Stored as quantiles and drawn per
    simulated row, so a starter's attempt / yardage distributions carry that tail instead of pretending
    he throws every pass in every world."""
    q = elig[(elig["position"] == "QB") & (elig["dc_rank"] == 1)].copy()
    q = q[(q["team_pass_att"].fillna(0) > 0) & (q["attempts"].fillna(0) > 0)]   # he played: absence is the availability layer's job
    share = (q["attempts"].fillna(0) / q["team_pass_att"]).clip(0, 1).to_numpy(float)
    if len(share) < 100:
        share = np.ones(100)
    return {"quantiles": np.quantile(share, np.linspace(0, 1, 201)).tolist(), "n": int(len(share)),
            "p_below_half": float(np.mean(share < 0.5))}


# ----------------------------------------------------------------------------------------- bundle
def bundle(game_env: dict, carry_share: dict, target_share: dict, carry: dict, target: dict, td: dict,
           *, train_seasons, feature_config: dict, other_share: dict, qb_share: dict | None = None) -> dict:
    return {"sim_version": SIM_VERSION, "models_version": MODELS_VERSION, "train_seasons": list(train_seasons),
            "feature_config": feature_config, "game_env": game_env, "carry_share": carry_share,
            "target_share": target_share, "carry": carry, "target": target, "td": td, "other_share": other_share,
            "qb_share": qb_share or {"quantiles": [1.0] * 201, "n": 0, "p_below_half": 0.0}}
