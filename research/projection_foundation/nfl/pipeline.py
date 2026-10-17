"""Build every family's walk-forward predictions (models A..F + incumbents) on one frame.

The same code path serves the backtest and the forward projection: upcoming games are rows with NaN outcomes,
so their features and predictions come out of exactly the functions that were validated.
"""
from __future__ import annotations

import time
import warnings

import numpy as np
import pandas as pd

from pf_core import models as M

from . import data as D
from . import features as F
from . import ladder as L

warnings.filterwarnings("ignore")

# family -> spec
TEAM_FAMILIES = {
    "team_pass_attempts": {"y": "tm_attempts", "own": "own_tm_attempts", "rr": "pass_att", "league": "league_tm_attempts", "K": 90},
    "team_rush_attempts": {"y": "tm_carries", "own": "own_tm_carries", "rr": "rush_att", "league": "league_tm_carries", "K": 80},
    "team_points": {"y": "points", "own": "own_points", "rr": "points", "league": "league_points", "K": 90},
}
PLAYER_FAMILIES = {
    # family: outcome, population, kind, opportunity family, support (lo, K), Kalshi-like rungs
    "targets": dict(y="targets", pop="REC", kind="count", opp=None, lo=0, K=35, rungs=[3, 5, 7, 9]),
    "receptions": dict(y="receptions", pop="REC", kind="count", opp="targets", lo=0, K=30, rungs=[3, 5, 7]),
    "receiving_yards": dict(y="receiving_yards", pop="REC", kind="yards", opp="targets", lo=-20, K=330, rungs=[40, 60, 80, 100]),
    "carries": dict(y="carries", pop="RUSH", kind="count", opp=None, lo=0, K=50, rungs=[10, 15, 20]),
    "rushing_yards": dict(y="rushing_yards", pop="RUSH", kind="yards", opp="carries", lo=-30, K=330, rungs=[40, 60, 80, 100]),
    "passing_attempts": dict(y="attempts", pop="QB", kind="count", opp="team_pass_attempts", lo=0, K=80, rungs=[30, 35, 40]),
    "completions": dict(y="completions", pop="QB", kind="count", opp="passing_attempts", lo=0, K=60, rungs=[18, 22, 25]),
    "passing_yards": dict(y="passing_yards", pop="QB", kind="yards", opp="passing_attempts", lo=-30, K=650, rungs=[200, 250, 300]),
    "passing_tds": dict(y="passing_tds", pop="QB", kind="count", opp="passing_attempts", lo=0, K=10, rungs=[1, 2, 3]),
    "anytime_td": dict(y="any_td", pop="TD", kind="binary", opp="touches", lo=0, K=2, rungs=[1]),
}
INC_STAT = {"targets": "targets", "receptions": "receptions", "receiving_yards": "receiving_yards", "carries": "carries",
            "rushing_yards": "rushing_yards", "passing_attempts": "attempts", "completions": "completions",
            "passing_yards": "passing_yards", "passing_tds": "passing_tds", "anytime_td": "anytime_td"}


def population(pf: pd.DataFrame, pop: str) -> np.ndarray:
    rec = pf.position.isin(["RB", "WR", "TE"])
    if pop == "REC":
        return (rec & (pf.targets_r4 >= 2)).to_numpy()
    if pop == "RUSH":
        return ((pf.position == "RB") & (pf.carries_r4 >= 4)).to_numpy()
    if pop == "QB":
        return ((pf.position == "QB") & pf.qb_starter.astype(bool)).to_numpy()
    if pop == "TD":
        return (rec & ((pf.targets_r4 >= 2) | (pf.carries_r4 >= 4))).to_numpy()
    raise ValueError(pop)


POP_TEXT = {"REC": "RB/WR/TE who played, mean >= 2 targets over their previous 4 games played (PIT)",
            "RUSH": "RBs who played, mean >= 4 carries over their previous 4 games played (PIT)",
            "QB": "the team's starting QB (nflverse schedule starter id; announced pregame)",
            "TD": "RB/WR/TE who played with >= 2 targets or >= 4 carries per game over their previous 4 games (PIT)",
            "TEAM": "every regular-season team-game"}


# ============================================================================ team families
def team_ladder(tf: pd.DataFrame, log=print) -> tuple[pd.DataFrame, dict]:
    tf = tf.copy()
    dev = tf.season.between(*L.DEV).to_numpy() & tf.played.to_numpy()
    params = {}
    preds = {}
    for fam, s in TEAM_FAMILIES.items():
        t0 = time.time()
        y = tf[s["y"]].to_numpy(float)
        prior = tf[s["league"]]
        pa, A = L.tune_A(tf, s["own"], prior, y, dev)
        pb, B = L.tune_B(tf, s["own"], prior, y, dev, halflives=(4, 8))
        h = pb["halflife"]
        plays = M.est_B(tf, "own_plays", tf.league_plays, pb["k"], h)
        prate = M.est_B(tf, "own_pass_rate", pd.Series(np.full(len(tf), np.nanmean(tf.pass_rate)), index=tf.index), pb["k"], h)
        if fam == "team_pass_attempts":
            att_per_db = np.nanmean((tf.tm_attempts / (tf.plays * tf.pass_rate))[dev])
            C = plays * prate * att_per_db
        elif fam == "team_rush_attempts":
            C = plays * (1 - prate)
        else:
            alw = M.est_B(tf, "alw_points", prior, pb["k"], h)
            C = B * alw / prior
        # D: B x opponent (schedule-adjusted ridge) x environment, elasticities fitted on dev
        lof = np.log(tf[f"opp_factor_{s['rr']}"].clip(0.5, 2.0)).fillna(0).to_numpy()
        X_opp = np.column_stack([lof, tf.home.to_numpy(float) - 0.5])
        b_opp = L.fit_loglinear(y, B.to_numpy(), X_opp, dev)
        D_opp = L.apply_loglinear(B.to_numpy(), X_opp, b_opp)
        env = [tf.spread_team.fillna(0).to_numpy() / 7.0, (tf.total_line.fillna(44) - 44).to_numpy() / 7.0]
        if fam == "team_points":
            env = [np.log((tf.implied_total.clip(5, 45) / B).fillna(1.0)).to_numpy()]
        X_env = np.column_stack([X_opp] + [e[:, None] for e in env])
        b_env = L.fit_loglinear(y, B.to_numpy(), X_env, dev)
        Dv = L.apply_loglinear(B.to_numpy(), X_env, b_env)
        feats = [c for c in tf.columns if c.startswith(("own_", "alw_", "rr_", "opp_factor_"))] + \
            ["spread_team", "total_line", "implied_total", "home", "week", "rest", "opp_rest", "indoor", "div_game"]
        E = L.lgbm(tf, feats, s["y"], "poisson", tf.played.to_numpy())
        P = pd.DataFrame({"B": B, "C": C, "D": Dv, "E": E}, index=tf.index)
        w, Fdev = L.stack(P, y, dev)
        valmask = tf.season.between(*L.VAL).to_numpy() & tf.played.to_numpy()
        w2, _ = L.stack(P, y, dev | valmask)
        Fp = P.to_numpy(float) @ np.array(list(w.values()))
        Fp_hold = P.to_numpy(float) @ np.array(list(w2.values()))
        preds[fam] = pd.DataFrame({"A": A, "B": B, "C": C, "D_opp": D_opp, "D": Dv, "E": E, "F": Fp, "F_holdout": Fp_hold,
                                   "MKT": tf.implied_total if fam == "team_points" else np.nan}, index=tf.index)
        params[fam] = {"A": pa, "B": pb, "D_opp_beta": b_opp.tolist(), "D_env_beta": b_env.tolist(),
                       "F_weights_dev": w, "F_weights_dev_val": w2, "seconds": round(time.time() - t0, 1)}
        log(f"  team {fam}: {params[fam]}")
    return preds, params


# ============================================================================ player families
def _prod_tune(df, col, prior, mult, y, mask, halflives=L.H_GRID):
    best = None
    for h in halflives:
        for k in L.K_GRID:
            p = (mult * M.est_B(df, col, prior, k, h)).to_numpy()
            e = L._mse(y[mask], p[mask])
            if best is None or e < best[0]:
                best = (e, k, h)
    return {"k": best[1], "halflife": best[2]}, M.est_B(df, col, prior, best[1], best[2])


def player_ladder(pf: pd.DataFrame, log=print) -> tuple[dict, dict]:
    """pf: player features merged with team predictions (team_att_B/D, team_rush_B/D) and team opponent factors."""
    pf = pf.copy()
    dev_all = pf.season.between(*L.DEV).to_numpy() & pf.y_observed.to_numpy()
    pops = {p: population(pf, p) for p in ("REC", "RUSH", "QB", "TD")}
    dmask = {p: dev_all & m for p, m in pops.items()}
    preds, params = {}, {}
    rec_pos = pf.position.isin(["RB", "WR", "TE"]).to_numpy()
    prior = {c: L.mean_prior_pit(pf, "position", c) for c in
             ["targets", "receptions", "receiving_yards", "carries", "rushing_yards", "attempts", "completions",
              "passing_yards", "passing_tds", "any_td", "tgt_per_att", "carry_share", "pass_share"]}
    rprior = {
        "catch": L.ratio_prior_pit(pf, "position", "receptions", "targets", 0.65),
        "ypt": L.ratio_prior_pit(pf, "position", "receiving_yards", "targets", 8.0),
        "ypc": L.ratio_prior_pit(pf, "position", "rushing_yards", "carries", 4.2),
        "comp": L.ratio_prior_pit(pf, "position", "completions", "attempts", 0.63),
        "ypa": L.ratio_prior_pit(pf, "position", "passing_yards", "attempts", 7.0),
        "ptd": L.ratio_prior_pit(pf, "position", "passing_tds", "attempts", 0.045),
        "rtd": L.ratio_prior_pit(pf, "position", "receiving_tds", "targets", 0.05),
        "rutd": L.ratio_prior_pit(pf, "position", "rushing_tds", "carries", 0.03),
    }
    Y = {f: pf[s["y"]].to_numpy(float) for f, s in PLAYER_FAMILIES.items()}
    lf = lambda c: np.log(pf[c].clip(0.5, 2.0)).fillna(0).to_numpy()          # noqa: E731

    def AB(fam, col, pop):
        pa, A = L.tune_A(pf, col, prior[col], Y[fam], dmask[pop])
        pb, B = L.tune_B(pf, col, prior[col], Y[fam], dmask[pop])
        return pa, A, pb, B

    # ---- opportunity components
    p_tpa, tpa = _prod_tune(pf, "tgt_per_att", prior["tgt_per_att"], pf.team_att_B, Y["targets"], dmask["REC"])
    tgt_C = pf.team_att_B * tpa
    tgt_D0 = pf.team_att_D * tpa
    X_tgt = np.column_stack([pf.spread_team.fillna(0) / 7.0 * (pf.position == "RB"), pf.spread_team.fillna(0) / 7.0 * (pf.position != "RB")])
    b_tgt = L.fit_loglinear(Y["targets"], tgt_D0.to_numpy(), X_tgt, dmask["REC"])
    tgt_D = pd.Series(L.apply_loglinear(tgt_D0.to_numpy(), X_tgt, b_tgt), index=pf.index)
    p_cs, cs = _prod_tune(pf, "carry_share", prior["carry_share"], pf.team_rush_B, Y["carries"], dmask["RUSH"])
    car_C = pf.team_rush_B * cs
    car_D0 = pf.team_rush_D * cs
    X_car = np.column_stack([pf.spread_team.fillna(0) / 7.0])
    b_car = L.fit_loglinear(Y["carries"], car_D0.to_numpy(), X_car, dmask["RUSH"])
    car_D = pd.Series(L.apply_loglinear(car_D0.to_numpy(), X_car, b_car), index=pf.index)
    p_ps, ps = _prod_tune(pf, "pass_share", prior["pass_share"], pf.team_att_B, Y["passing_attempts"], dmask["QB"])
    att_C = pf.team_att_B * ps
    att_D = pf.team_att_D * ps
    comp = {"targets": (p_tpa, tgt_C, tgt_D, b_tgt), "carries": (p_cs, car_C, car_D, b_car), "passing_attempts": (p_ps, att_C, att_D, [])}
    for fam in ("targets", "carries", "passing_attempts"):
        s = PLAYER_FAMILIES[fam]
        col = s["y"]
        pa, A, pb, B = AB(fam, col, s["pop"])
        pp, C, Dv, beta = comp[fam]
        preds[fam] = pd.DataFrame({"A": A, "B": B, "C": C, "D": Dv}, index=pf.index)
        params[fam] = {"A": pa, "B": pb, "share": pp, "D_beta": list(np.atleast_1d(beta).astype(float))}

    # ---- efficiency families: opportunity x rate (x opponent factor)
    eff = {
        "receptions": ("receptions", "targets", "catch", tgt_C, tgt_D, ["opp_factor_catch_rate"]),
        "receiving_yards": ("receiving_yards", "targets", "ypt", tgt_C, tgt_D, ["opp_factor_ypt"]),
        "rushing_yards": ("rushing_yards", "carries", "ypc", car_C, car_D, ["opp_factor_ypc"]),
        "completions": ("completions", "attempts", "comp", att_C, att_D, ["opp_factor_comp_pct"]),
        "passing_yards": ("passing_yards", "attempts", "ypa", att_C, att_D, ["opp_factor_ypa"]),
        "passing_tds": ("passing_tds", "attempts", "ptd", att_C, att_D, ["opp_factor_ptd_rate", "_implied_ratio"]),
    }
    pf["_implied_ratio"] = (pf.implied_total / pf.league_points).clip(0.5, 2.0)
    for fam, (num, den, rk, oC, oD, facs) in eff.items():
        s = PLAYER_FAMILIES[fam]
        pa, A, pb, B = AB(fam, num, s["pop"])
        actual_den = pf[den].to_numpy(float)
        pr, rate = L.tune_rate(pf, num, den, rprior[rk], Y[fam], actual_den, dmask[s["pop"]])
        C = oC * rate
        base = (oD * rate).to_numpy()
        X = np.column_stack([lf(c) for c in facs])
        # yards: fit the elasticity by least squares on the log scale is unstable with negatives -> Poisson quasi-likelihood on y>=0
        yb = np.clip(Y[fam], 0, None)
        beta = L.fit_loglinear(yb, base, X, dmask[s["pop"]])
        Dv = L.apply_loglinear(base, X, beta)
        preds[fam] = pd.DataFrame({"A": A, "B": B, "C": C, "D": Dv}, index=pf.index)
        params[fam] = {"A": pa, "B": pb, "rate": pr, "D_factors": facs, "D_beta": beta.tolist()}

    # ---- anytime TD (binary): intensity = targets x rec-TD rate + carries x rush-TD rate
    fam = "anytime_td"
    pa, A, pb, B = AB(fam, "any_td", "TD")
    prt, rtd = L.tune_rate(pf, "receiving_tds", "targets", rprior["rtd"], pf.receiving_tds.to_numpy(float), pf.targets.to_numpy(float), dmask["TD"])
    pru, rutd = L.tune_rate(pf, "rushing_tds", "carries", rprior["rutd"], pf.rushing_tds.to_numpy(float), pf.carries.to_numpy(float), dmask["TD"])
    lamC = (tgt_C * rtd + car_C * rutd).to_numpy()
    lamD = (tgt_D * rtd + car_D * rutd).to_numpy()
    X = np.column_stack([np.log(pf["_implied_ratio"]).fillna(0).to_numpy(), lf("opp_factor_points")])
    beta = L.fit_loglinear(Y[fam], lamD, X, dmask["TD"], link="bernoulli")
    pC = 1 - np.exp(-lamC)
    pD = 1 - np.exp(-L.apply_loglinear(lamD, X, beta))
    preds[fam] = pd.DataFrame({"A": A, "B": B, "C": pC, "D": pD}, index=pf.index)
    params[fam] = {"A": pa, "B": pb, "rec_td_rate": prt, "rush_td_rate": pru, "D_beta": beta.tolist(), "D_factors": ["implied_ratio", "opp_factor_points"]}

    # ---- E (LightGBM walk-forward) and F (stack)
    base_feats = ["home", "spread_team", "total_line", "implied_total", "week", "is_rookie", "draft_round", "team_changed",
                  "days_since", "career_games", "games_in_season_before", "team_att_B", "team_att_D", "team_rush_B", "team_rush_D",
                  "pos_code", "offense_pct_ewm4", "offense_pct_ewm8", "offense_pct_r4", "offense_pct_last", "offense_pct_std",
                  "opp_factor_pass_att", "opp_factor_rush_att", "opp_factor_points"]
    pf["pos_code"] = pf.position.map({"QB": 0, "RB": 1, "WR": 2, "TE": 3})
    fam_cols = {"targets": ["targets", "tgt_per_att", "receptions", "receiving_air_yards"],
                "receptions": ["targets", "tgt_per_att", "receptions"], "receiving_yards": ["targets", "receiving_yards", "receiving_air_yards", "tgt_per_att"],
                "carries": ["carries", "carry_share", "targets"], "rushing_yards": ["carries", "rushing_yards", "carry_share"],
                "passing_attempts": ["attempts", "pass_share"], "completions": ["attempts", "completions"],
                "passing_yards": ["attempts", "passing_yards", "completions"], "passing_tds": ["attempts", "passing_tds", "passing_yards"],
                "anytime_td": ["any_td", "n_td", "targets", "carries", "receiving_tds", "rushing_tds"]}
    fam_opp = {"receptions": ["opp_factor_catch_rate"], "receiving_yards": ["opp_factor_ypt"], "rushing_yards": ["opp_factor_ypc"],
               "completions": ["opp_factor_comp_pct"], "passing_yards": ["opp_factor_ypa"], "passing_tds": ["opp_factor_ptd_rate"]}
    for fam, s in PLAYER_FAMILIES.items():
        t0 = time.time()
        feats = list(base_feats) + fam_opp.get(fam, [])
        for c in fam_cols[fam]:
            feats += [f"{c}_{x}" for x in ("n", "career", "ewm2", "ewm4", "ewm8", "ewm16", "std", "std_n", "prev", "prev_n")]
            feats += [f"{c}_r4", f"{c}_last"] if f"{c}_r4" in pf.columns else []
        feats += ["C_" + fam, "D_" + fam]
        pf["C_" + fam] = preds[fam]["C"]
        pf["D_" + fam] = preds[fam]["D"]
        feats = [f for f in dict.fromkeys(feats) if f in pf.columns]
        obj = {"count": "poisson", "yards": "regression", "binary": "binary"}[s["kind"]]
        y = s["y"]
        pf["_yE"] = pf[y].where(pf.y_observed)
        if s["kind"] == "binary":
            import lightgbm as lgb  # binary needs predict_proba: do the walk-forward here
            E = pd.Series(np.nan, index=pf.index)
            tr_all = pops[s["pop"]] & pf.y_observed.to_numpy()
            for season in sorted(pf.season.unique()):
                if season < 2016:
                    continue
                tr = tr_all & (pf.season < season).to_numpy() & (pf.season >= 2013).to_numpy()
                mdl = lgb.LGBMClassifier(objective="binary", learning_rate=0.05, n_estimators=300, num_leaves=31, min_child_samples=100,
                                         subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, verbose=-1, n_jobs=2)
                mdl.fit(pf.loc[tr, feats], pf.loc[tr, y].astype(int))
                te = (pf.season == season).to_numpy()
                E[te] = mdl.predict_proba(pf.loc[te, feats])[:, 1]
        else:
            E = L.lgbm(pf, feats, "_yE", obj, pops[s["pop"]])
        preds[fam]["E"] = E
        P = preds[fam][["B", "C", "D", "E"]]
        w, _ = L.stack(P, Y[fam], dmask[s["pop"]])
        valm = pf.season.between(*L.VAL).to_numpy() & pf.y_observed.to_numpy() & pops[s["pop"]]
        w2, _ = L.stack(P, Y[fam], dmask[s["pop"]] | valm)
        preds[fam]["F"] = P.to_numpy(float) @ np.array(list(w.values()))
        preds[fam]["F_holdout"] = P.to_numpy(float) @ np.array(list(w2.values()))
        if s["kind"] == "binary":
            for c in preds[fam].columns:
                preds[fam][c] = preds[fam][c].clip(0.001, 0.999)
        else:
            for c in preds[fam].columns:
                preds[fam][c] = preds[fam][c].clip(lower=0.05 if s["kind"] == "count" else None)
        params[fam]["E_features"] = feats
        params[fam]["F_weights_dev"] = w
        params[fam]["F_weights_dev_val"] = w2
        log(f"  player {fam}: E done in {time.time() - t0:.0f}s; stack {w}")
    return preds, params, pops


# ============================================================================ assembly
def build_frames(upcoming_pg: pd.DataFrame | None = None, upcoming_block: int | None = None, log=print, force: bool = True):
    """Returns (tf with team predictions, pf with player features+team predictions, params)."""
    sched = D.load_schedule()
    tg = D.cached("team_games", lambda: D.team_games(sched))
    pg = D.cached("player_games", lambda: D.player_games(sched))
    t0 = time.time()
    tf = D.cached(f"team_features_{upcoming_block}", lambda: F.team_features(tg, upcoming_block=upcoming_block), force=force)
    log(f"team features {tf.shape} in {time.time() - t0:.0f}s")
    tpreds, tparams = team_ladder(tf, log)
    for fam, short in (("team_pass_attempts", "team_att"), ("team_rush_attempts", "team_rush"), ("team_points", "team_pts")):
        for m in ("B", "D", "E", "F"):
            tf[f"{short}_{m}"] = tpreds[fam][m]
    pg = pg.copy()
    pg["upcoming"] = False
    if upcoming_pg is not None and len(upcoming_pg):
        up = upcoming_pg.copy()
        up["upcoming"] = True
        pg = pd.concat([pg, up], ignore_index=True)
    pg["y_observed"] = ~pg.upcoming
    t0 = time.time()
    pf = D.cached(f"player_features_{upcoming_block}", lambda: F.player_features(pg), force=force)
    log(f"player features {pf.shape} in {time.time() - t0:.0f}s")
    keep = ["game_id", "team", "team_att_B", "team_att_D", "team_rush_B", "team_rush_D", "team_pts_B", "team_pts_D",
            "league_points", "league_tm_attempts", "league_tm_carries"] + [c for c in tf.columns if c.startswith("opp_factor_")] + \
        [c for c in tf.columns if c.startswith("rr_ndef_")]
    pf = pf.merge(tf[keep], on=["game_id", "team"], how="left")
    pf = pf[pf.team_att_B.notna()].reset_index(drop=True)
    pf["split"] = L.split_of(pf.season, pf.week, pf.upcoming)
    tf["split"] = L.split_of(tf.season, tf.week, ~tf.played)
    return tf, tpreds, tparams, pf
