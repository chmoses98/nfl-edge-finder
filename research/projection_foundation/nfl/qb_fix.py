"""QB correction (diagnosed on development data, nfl/diagnostics + RESULTS_NFL.md 'QB volume'):

1. A QB's history included relief / garbage-time / injury-exit appearances where he was not the scheduled starter
   (6.5 attempts on average vs 33.1 as a starter, 18% of QB rows). Those games drag his EWMA down: on 2016-2021 starts whose
   previous 4 games include a non-start, D projected 189.8 passing yards vs 209.9 realised. Fix: QB families use a
   starts-only history (non-start games are treated as unobserved, not as zeros).
2. QB efficiency had no game-environment term; the under-projection grows with the closing implied team total. Fix: the D
   rung adds log(implied total / league points) (and the spread for attempts) with elasticities fitted on 2016-2021.

Produces *_qs variants (A_qs, B_qs, C_qs, D_qs, F_qs) evaluated by the selection stage like any other model; F_qs stacks
B_qs, C_qs, D_qs and the unchanged walk-forward E with weights fitted on development predictions only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pf_core import models as M
from pf_core import pit

from . import ladder as L
from . import pipeline as P

QB_COLS = ["attempts", "completions", "passing_yards", "passing_tds", "pass_share"]


def qb_variants(S) -> dict:
    pf = S["pf"]
    preds = S["preds"]
    q = pf[pf.position == "QB"][["player_id", "game_id", "kickoff_utc", "season", "block", "qb_starter", "y_observed"] + QB_COLS].copy()
    keep = q.qb_starter.astype(bool)
    for c in QB_COLS:
        q[c + "_s"] = q[c].where(keep)
    q = pit.sort_chrono(q, "player_id", "kickoff_utc", "game_id")
    f = pit.lagged_features(q, "player_id", [c + "_s" for c in QB_COLS], halflives=L.H_GRID, season_col="season")
    f = f.set_index(["player_id", "game_id"])
    key = pd.MultiIndex.from_frame(pf[["player_id", "game_id"]])
    feat_cols = [c for c in f.columns if any(c.startswith(x + "_s_") for x in QB_COLS)]
    F = f[feat_cols].reindex(key)
    F.index = pf.index
    d = pd.concat([pf, F], axis=1)
    dev = pf.season.between(*L.DEV).to_numpy() & pf.y_observed.to_numpy() & S["pops"]["QB"]
    # priors over QB starts only (point in time)
    qs = d.position.eq("QB") & d.qb_starter.astype(bool)
    prior = {}
    for c in QB_COLS:
        tmp = d[["block", "position", "season"]].copy()
        tmp["_x"] = d[c].where(qs)
        prior[c] = M.group_prior_pit(tmp.assign(position="QB"), ["position"], "block", "_x", fallback=L.warmup_mean(tmp, "_x"))
    rp = {}
    for num, k, fb in (("completions", "comp", 0.63), ("passing_yards", "ypa", 7.0), ("passing_tds", "ptd", 0.045)):
        tmp = pd.DataFrame({"g": "QB", "block": d.block, "n": d[num].where(qs).fillna(0), "dd": d.attempts.where(qs).fillna(0)})
        rp[k] = L.ratio_prior_pit(tmp, "g", "n", "dd", fb)
    implied = np.log((pf.implied_total / pf.league_points).clip(0.5, 2.0)).fillna(0).to_numpy()
    out, params = {}, {}
    y = {f: pf[P.PLAYER_FAMILIES[f]["y"]].to_numpy(float) for f in ("passing_attempts", "completions", "passing_yards", "passing_tds")}
    # opportunity: attempts
    pa, A = L.tune_A(d, "attempts_s", prior["attempts"], y["passing_attempts"], dev)
    pb, B = L.tune_B(d, "attempts_s", prior["attempts"], y["passing_attempts"], dev)
    best = None
    for h in L.H_GRID:
        for k in L.K_GRID:
            ps = M.est_B(d, "pass_share_s", prior["pass_share"], k, h)
            e = L._mse(y["passing_attempts"][dev], (pf.team_att_B * ps).to_numpy()[dev])
            if best is None or e < best[0]:
                best = (e, k, h)
    ps = M.est_B(d, "pass_share_s", prior["pass_share"], best[1], best[2])
    att_C = (pf.team_att_B * ps).to_numpy()
    X = np.column_stack([implied, pf.spread_team.fillna(0).to_numpy() / 7.0])
    b_att = L.fit_loglinear(y["passing_attempts"], (pf.team_att_D * ps).to_numpy(), X, dev)
    att_D = L.apply_loglinear((pf.team_att_D * ps).to_numpy(), X, b_att)
    out["passing_attempts"] = {"A_qs": A, "B_qs": B, "C_qs": pd.Series(att_C, index=pf.index), "D_qs": pd.Series(att_D, index=pf.index)}
    params["passing_attempts"] = {"A": pa, "B": pb, "share": {"k": best[1], "halflife": best[2]}, "D_beta": b_att.tolist()}
    for fam, num, rk, fac in (("completions", "completions", "comp", "opp_factor_comp_pct"), ("passing_yards", "passing_yards", "ypa", "opp_factor_ypa"),
                              ("passing_tds", "passing_tds", "ptd", "opp_factor_ptd_rate")):
        pa, A = L.tune_A(d, num + "_s", prior[num], y[fam], dev)
        pb, B = L.tune_B(d, num + "_s", prior[num], y[fam], dev)
        pr, rate = L.tune_rate(d, num + "_s", "attempts_s", rp[rk], y[fam], pf.attempts.to_numpy(float), dev)
        C = att_C * rate.to_numpy()
        base = att_D * rate.to_numpy()
        X = np.column_stack([np.log(pf[fac].clip(0.5, 2.0)).fillna(0).to_numpy(), implied])
        beta = L.fit_loglinear(np.clip(y[fam], 0, None), base, X, dev)
        Dv = L.apply_loglinear(base, X, beta)
        out[fam] = {"A_qs": A, "B_qs": B, "C_qs": pd.Series(C, index=pf.index), "D_qs": pd.Series(Dv, index=pf.index)}
        params[fam] = {"A": pa, "B": pb, "rate": pr, "D_factors": [fac, "implied_ratio"], "D_beta": beta.tolist()}
    valm = pf.season.between(*L.VAL).to_numpy() & pf.y_observed.to_numpy() & S["pops"]["QB"]
    for fam in out:
        Pm = pd.DataFrame({"B": out[fam]["B_qs"], "C": out[fam]["C_qs"], "D": out[fam]["D_qs"], "E": preds[fam]["E"]}, index=pf.index)
        w, _ = L.stack(Pm, y[fam], dev)
        w2, _ = L.stack(Pm, y[fam], dev | valm)
        out[fam]["F_qs"] = pd.Series(Pm.to_numpy(float) @ np.array(list(w.values())), index=pf.index)
        out[fam]["F_qs_holdout"] = pd.Series(Pm.to_numpy(float) @ np.array(list(w2.values())), index=pf.index)
        params[fam]["F_weights_dev"] = w
        params[fam]["F_weights_dev_val"] = w2
        for k in out[fam]:
            out[fam][k] = pd.Series(np.asarray(out[fam][k], float), index=pf.index).clip(lower=0.05)
    return out, params
