"""Historical Model Architecture Championship (RESEARCH_ONLY): architectures, predictive distributions, scoring.

Every model outputs a joint pmf over the final (home margin, total) on the integer lattice of ``gsdl_tournament``.  The
architectures differ in WHERE THE CENTRE COMES FROM (closing line / football ridge / gradient boosting / drive model / learned
blend) and HOW THE DISTRIBUTION IS BUILT (incumbent residual bank, conditional-empirical kernel on the centre, Gaussian, or an
explicit drive-convolution pmf).  Football-first centres never see a betting line.  Everything is fitted on seasons < Y.
"""
from __future__ import annotations
import os, sys, time, json, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from scripts.sim import hmac_features as H, gsdl_tournament as T

NM, NT, GM, GT = T.NM, T.NT, T.GM, T.GT
TRAIN_START = 2002
OUT = os.path.join(T.ROOT, "research", "historical_architecture_championship")
RES = os.path.join(OUT, "cache")
STATS = ["epa_play", "points", "success_rate", "plays", "sec_per_play", "neutral_pass_rate", "ypa", "ypc", "sack_rate", "pass_epa",
         "rush_epa", "expl_pass", "expl_rush", "hit", "td_rate", "fg_rate", "to_rate", "drives"]
FF1_M = ["f_elo"] + [f"mf_{x}" for x in STATS] + ["f_rest_diff", "f_div"]
FF1_T = [f"sf_{x}" for x in STATS] + ["f_rest_min", "f_short", "f_div", "f_dome"]
QB_M = ["f_qb_epa_diff", "f_qb_change_diff", "f_qb_new_diff"]; QB_T = ["f_qb_epa_sum", "f_qb_change_sum", "f_qb_new_sum"]
FF2_M, FF2_T = FF1_M + QB_M, FF1_T + QB_T
BW = {"k1": (3.0, 5.0), "k2": (4.0, 6.5), "k3": (5.5, 8.0)}
GBT = {"A": dict(max_depth=2, max_iter=250, learning_rate=0.04, min_samples_leaf=60, l2_regularization=2.0),
       "B": dict(max_depth=3, max_iter=400, learning_rate=0.03, min_samples_leaf=40, l2_regularization=5.0)}
_SCHED = None


def sched():
    global _SCHED
    if _SCHED is None:
        x = T.GF.schedule_frame(); _SCHED = x[x["result"].notna() & x["spread_line"].notna() & x["total_line"].notna()].copy()
    return _SCHED


# ------------------------------------------------------------------------------------------------- centres
def _std(Xtr, Xte):
    mu = np.nanmean(Xtr, 0); sd = np.nanstd(Xtr, 0); sd[sd == 0] = 1.0
    f = lambda X: (np.where(np.isfinite(X), X, mu) - mu) / sd
    return f(Xtr), f(Xte)


def ridge_cv(Xtr, ytr, s_tr, Xte, lams=(10.0, 100.0, 1000.0)):
    """Ridge, lambda by leave-one-season-out on the training seasons; returns (test prediction, out-of-fold training predictions)."""
    Z, Zt = _std(Xtr, Xte)
    def fit(a, lam):
        yb = ytr[a].mean(); return yb, np.linalg.solve(Z[a].T @ Z[a] + lam * np.eye(Z.shape[1]), Z[a].T @ (ytr[a] - yb))
    best = None
    for lam in lams:
        oof = np.zeros(len(ytr))
        for s in np.unique(s_tr):
            a = s_tr != s; yb, b = fit(a, lam); oof[~a] = yb + Z[~a] @ b
        sse = ((ytr - oof) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, lam, oof)
    yb, b = fit(np.ones(len(ytr), bool), best[1])
    return yb + Zt @ b, best[2]


def gbt_cv(Xtr, ytr, s_tr, Xte, hp, folds=5):
    seasons = np.unique(s_tr); fold = {s: i % folds for i, s in enumerate(seasons)}; f = np.array([fold[s] for s in s_tr])
    mk = lambda: HistGradientBoostingRegressor(random_state=0, early_stopping=False, **hp)
    oof = np.zeros(len(ytr))
    for k in range(folds):
        a = f != k
        if (~a).sum():
            oof[~a] = mk().fit(Xtr[a], ytr[a]).predict(Xtr[~a])
    return mk().fit(Xtr, ytr).predict(Xte), oof


def centres(kind, tr, te, cache):
    """(cm_te, ct_te, cm_tr_oof, ct_tr_oof) for a centre kind; cached within a season."""
    if kind in cache:
        return cache[kind]
    s = tr["season"].to_numpy(); y_m = tr["result"].to_numpy(float); y_t = tr["total"].to_numpy(float)
    num = lambda d, c: d[c].to_numpy(float)
    if kind == "mkt":
        r = (te["spread_line"].to_numpy(float), te["total_line"].to_numpy(float), tr["spread_line"].to_numpy(float), tr["total_line"].to_numpy(float))
    elif kind == "elo":
        a, ao = ridge_cv(num(tr, ["f_elo"]), y_m, s, num(te, ["f_elo"]), lams=(1.0,))
        b, bo = ridge_cv(num(tr, ["sf_points"]), y_t, s, num(te, ["sf_points"]), lams=(1.0,)); r = (a, b, ao, bo)
    elif kind in ("ff1", "ff2"):
        M, Tc = (FF1_M, FF1_T) if kind == "ff1" else (FF2_M, FF2_T)
        a, ao = ridge_cv(num(tr, M), y_m, s, num(te, M)); b, bo = ridge_cv(num(tr, Tc), y_t, s, num(te, Tc)); r = (a, b, ao, bo)
    elif kind in ("gbtA", "gbtB"):
        cols = list(dict.fromkeys(FF2_M + FF2_T)); hp = GBT[kind[-1]]
        a, ao = gbt_cv(num(tr, cols), y_m, s, num(te, cols), hp); b, bo = gbt_cv(num(tr, cols), y_t, s, num(te, cols), hp); r = (a, b, ao, bo)
    elif kind == "poss":
        def pc(d):
            ph = d["hm_drives"] * (7 * d["hm_td_rate"] + 3 * d["hm_fg_rate"]); pa = d["am_drives"] * (7 * d["am_td_rate"] + 3 * d["am_fg_rate"])
            return np.c_[(ph - pa).to_numpy(float)], np.c_[(ph + pa).to_numpy(float)]
        (mtr, ttr), (mte, tte) = pc(tr), pc(te)
        a, ao = ridge_cv(mtr, y_m, s, mte, lams=(1.0,)); b, bo = ridge_cv(ttr, y_t, s, tte, lams=(1.0,)); r = (a, b, ao, bo)
    elif kind == "ens":                      # football-only ensemble: mean of ff2, best-of-two gbt (A), poss centres
        parts = [centres(k, tr, te, cache) for k in ("ff2", "gbtA", "poss")]
        r = tuple(np.mean([p[i] for p in parts], 0) for i in range(4))
    elif kind in ("blend", "anchor"):
        parts = [centres(k, tr, te, cache) for k in ("ff2", "gbtA", "poss")]
        sp_te, tl_te = te["spread_line"].to_numpy(float), te["total_line"].to_numpy(float)
        sp_tr, tl_tr = tr["spread_line"].to_numpy(float), tr["total_line"].to_numpy(float)
        if kind == "blend":   # learned linear blend of market and football centres (all weights fitted on training seasons)
            Xm_te = np.c_[sp_te, np.array([p[0] for p in parts]).T]
            Xm_tr = np.c_[sp_tr, np.array([p[2] for p in parts]).T]
            Xt_tr = np.c_[tl_tr, np.array([p[3] for p in parts]).T]; Xt_te = np.c_[tl_te, np.array([p[1] for p in parts]).T]
            a, ao = ridge_cv(Xm_tr, y_m, s, Xm_te, lams=(1.0, 10.0, 100.0)); b, bo = ridge_cv(Xt_tr, y_t, s, Xt_te, lams=(1.0, 10.0, 100.0))
        else:                 # anchored residual correction: line + ridge(result - line ~ football minus line)
            Dm_tr = np.array([p[2] - sp_tr for p in parts]).T; Dm_te = np.array([p[0] - sp_te for p in parts]).T
            Dt_tr = np.array([p[3] - tl_tr for p in parts]).T; Dt_te = np.array([p[1] - tl_te for p in parts]).T
            a, ao = ridge_cv(Dm_tr, y_m - sp_tr, s, Dm_te, lams=(100.0, 1000.0, 10000.0)); b, bo = ridge_cv(Dt_tr, y_t - tl_tr, s, Dt_te, lams=(100.0, 1000.0, 10000.0))
            a, ao, b, bo = sp_te + a, sp_tr + ao, tl_te + b, tl_tr + bo
        r = (a, b, ao, bo)
    else:
        raise KeyError(kind)
    cache[kind] = r
    return r


# --------------------------------------------------------------------------------------------- distributions
def _tri(d, h):
    return np.clip(1 - np.abs(d) / h, 0, None)


def kernel_pmfs(tr, cm_tr, ct_tr, cm_te, ct_te, Y, hs, ht, hl=6.0, floor=0.10):
    res = tr["result"].to_numpy(float); tot = tr["total"].to_numpy(float); ws = 0.5 ** ((Y - tr["season"].to_numpy(float)) / hl)
    out = []
    for cm, ct in zip(cm_te, ct_te):
        dm, dt = cm_tr - cm, ct_tr - ct
        w = ws * _tri(dm, hs) * _tri(dt, ht); wide = ws * _tri(dm, 3 * hs) * _tri(dt, 3 * ht)
        if w.sum() < 1e-8:
            w = wide
        t = tot - np.round(dt)
        P = (1 - floor) * T.hist2(*T.finalize(res, t, w / w.sum())) + floor * T.hist2(*T.finalize(res, t, wide / wide.sum()))
        out.append(P / P.sum())
    return out


def gauss_pmfs(cm_tr, ct_tr, tr, cm_te, ct_te):
    e = np.c_[tr["result"].to_numpy(float) - cm_tr, tr["total"].to_numpy(float) - ct_tr]; cov = np.cov(e.T); inv = np.linalg.inv(cov)
    Mg, Tg = np.meshgrid(GM, GT, indexing="ij"); out = []
    for cm, ct in zip(cm_te, ct_te):
        d = np.stack([Mg - cm, Tg - ct], -1); P = np.exp(-0.5 * np.einsum("...i,ij,...j", d, inv, d)); out.append(P / P.sum())
    return out


def _conv_power(f, n):
    out = np.zeros(120); out[0] = 1.0
    for _ in range(n):
        out = np.convolve(out, f)[:120]
    return out


def poss_pmfs(te, sd_drives=1.5):
    """Explicit drive model: each team's points are the sum of D iid drive outcomes (0 / 3 / 7 points) with its matchup TD and
    FG rates; D is the predicted drive count plus a shared discretised-normal shock.  Non-offensive scoring is NOT modelled."""
    e = np.arange(-4, 5); we = np.exp(-0.5 * (e / sd_drives) ** 2); we /= we.sum(); out = []
    for r in te.itertuples(index=False):
        fh = np.zeros(8); fh[0] = 1 - r.hm_td_rate - r.hm_fg_rate; fh[3] = r.hm_fg_rate; fh[7] = r.hm_td_rate
        fa = np.zeros(8); fa[0] = 1 - r.am_td_rate - r.am_fg_rate; fa[3] = r.am_fg_rate; fa[7] = r.am_td_rate
        Dh, Da = int(round(r.hm_drives)), int(round(r.am_drives)); P = np.zeros((NM, NT))
        for ek, wk in zip(e, we):
            ph = _conv_power(fh, max(Dh + ek, 1)); pa = _conv_power(fa, max(Da + ek, 1))
            J = np.outer(ph[:80], pa[:80]); hh, aa = np.meshgrid(np.arange(80), np.arange(80), indexing="ij")
            m = np.clip(hh - aa, -60, 60) + 60; t = np.clip(hh + aa, 0, 130)
            P += wk * np.bincount((m * NT + t).ravel(), weights=J.ravel(), minlength=NM * NT).reshape(NM, NT)
        out.append(P / P.sum())
    return out


# ------------------------------------------------------------------------------------------------ registry
def registry():
    R = {"A1": dict(fam="A", centre="mkt", dist="bank"), "A2": dict(fam="A", centre="mkt", dist="kernel", bw="k1"),
         "A3": dict(fam="A", centre="mkt", dist="bank_fav")}
    for k in BW:
        R[f"B_elo_{k}"] = dict(fam="B", centre="elo", dist="kernel", bw=k)
        R[f"B_ff1_{k}"] = dict(fam="B", centre="ff1", dist="kernel", bw=k)
        R[f"B_ff2_{k}"] = dict(fam="B", centre="ff2", dist="kernel", bw=k)
        R[f"C_gbtA_{k}"] = dict(fam="C", centre="gbtA", dist="kernel", bw=k)
        R[f"C_gbtB_{k}"] = dict(fam="C", centre="gbtB", dist="kernel", bw=k)
        R[f"D_poss_{k}"] = dict(fam="D", centre="poss", dist="kernel", bw=k)
        R[f"F_ens_{k}"] = dict(fam="F", centre="ens", dist="kernel", bw=k)
        R[f"E_blend_{k}"] = dict(fam="E", centre="blend", dist="kernel", bw=k)
        R[f"E_anchor_{k}"] = dict(fam="E", centre="anchor", dist="kernel", bw=k)
    R["B_ff2_gauss"] = dict(fam="B", centre="ff2", dist="gauss"); R["D_poss_raw"] = dict(fam="D", centre="poss", dist="poss_raw")
    R["E_mix_A2_ens"] = dict(fam="E", dist="mix", parts=["A2", "F_ens_k2"]); R["E_mix_A1_ens"] = dict(fam="E", dist="mix", parts=["A1", "F_ens_k2"])
    R["E_mix_A2_blend"] = dict(fam="E", dist="mix", parts=["A2", "E_blend_k1"])
    return R


REG = registry()


def mix_weight(parts, Y):
    """Weight on parts[0], chosen to minimise nine-cell log loss on the previous three seasons' OUT-OF-SAMPLE cached scores."""
    prev = []
    for p in parts:
        path = os.path.join(RES, f"{p}.parquet")
        if not os.path.exists(path):
            return 0.5
        d = pd.read_parquet(path); prev.append(d[(d.season >= Y - 3) & (d.season < Y)].sort_values("game_id"))
    if len(prev[0]) < 200 or len(prev[0]) != len(prev[1]):
        return 0.5
    P = [d[[f"p9_{j}" for j in range(9)]].to_numpy() for d in prev]; oc = prev[0]["oc9"].to_numpy(int); idx = np.arange(len(oc))
    ws = np.linspace(0, 1, 21); ll = [-np.log(np.maximum(w * P[0][idx, oc] + (1 - w) * P[1][idx, oc], 1e-9)).mean() for w in ws]
    return float(ws[int(np.argmin(ll))])


# ---------------------------------------------------------------------------------------------------- scoring
HPm = (np.floor((GT[None, :] + GM[:, None]) / 2)).clip(0, 79).astype(int); APm = (np.floor((GT[None, :] - GM[:, None]) / 2)).clip(0, 79).astype(int)


def score(P, r, u):
    s = T.score_game(P, float(r.result), float(r.total), float(r.spread_line), float(r.total_line), u)
    Pm = P.sum(1); y_m = float(r.result); sp = float(r.spread_line)
    pt = Pm[GM == 0].sum(); pw = Pm[GM > 0].sum() / max(1e-9, 1 - pt)
    s["ml_p"] = float(pw); s["ml_obs"] = float(y_m > 0) if y_m != 0 else np.nan
    pc = Pm[GM > sp].sum() / max(1e-9, 1 - (Pm[GM == sp].sum() if sp == int(sp) else 0.0)); s["cover_p"] = float(pc)
    s["cover_obs"] = float(y_m > sp) if y_m != sp else np.nan
    ph = np.bincount(HPm.ravel(), weights=P.ravel(), minlength=80); pa = np.bincount(APm.ravel(), weights=P.ravel(), minlength=80)
    hp, ap = int(np.clip((r.total + y_m) // 2, 0, 79)), int(np.clip((r.total - y_m) // 2, 0, 79))
    s["crps_h"] = float(((np.cumsum(ph) - (np.arange(80) >= hp)) ** 2).sum()); s["crps_a"] = float(((np.cumsum(pa) - (np.arange(80) >= ap)) ** 2).sum())
    im, it = int(np.clip(y_m, -60, 60)) + 60, int(np.clip(r.total, 0, 130))
    s["jlog"] = float(-np.log(0.99 * P[im, it] + 0.01 / (NM * NT)))
    ci = 0 if (np.sign(sp if sp != 0 else 1) * y_m) > T.ONE_SCORE else 2 if (np.sign(sp if sp != 0 else 1) * y_m) < -T.ONE_SCORE else 1
    si = 0 if r.total >= r.total_line + T.SHOOTOUT_OVER else 2 if r.total <= r.total_line - T.LOW_SCORING_UNDER else 1
    s["oc9"] = ci * 3 + si
    return s


def run_models(ids, seasons, verbose=print):
    os.makedirs(RES, exist_ok=True); H_ = sched()
    rows = {i: [] for i in ids}; t0 = time.time()
    order = [i for i in ids if REG[i]["dist"] != "mix"] + [i for i in ids if REG[i]["dist"] == "mix"]
    for Y in seasons:
        g = H.build(Y, verbose=lambda *_: None); te = g[g.season == Y].reset_index(drop=True)
        tr = g[(g.season >= TRAIN_START) & (g.season < Y) & (g.game_type == "REG")].reset_index(drop=True)
        u = np.random.default_rng(T.SEED + Y).random((len(te), 2)); cache = {}; pm = {}; mixw = {}
        for i in order:
            sp = REG[i]; d = sp["dist"]
            if d == "bank":
                b = T.Bank(H_, Y, start=TRAIN_START, hl=3.0); P = [T.bank_pmf(b, float(a), float(c)) for a, c in zip(te.spread_line, te.total_line)]; cm, ct = te.spread_line.to_numpy(float), te.total_line.to_numpy(float)
            elif d == "bank_fav":
                b = T.Bank(H_, Y, start=TRAIN_START, hl=3.0, fav=True); P = [T.bank_pmf(b, float(a), float(c)) for a, c in zip(te.spread_line, te.total_line)]; cm, ct = te.spread_line.to_numpy(float), te.total_line.to_numpy(float)
            elif d == "kernel":
                cm, ct, cmo, cto = centres(sp["centre"], tr, te, cache); hs, ht = BW[sp["bw"]]
                P = kernel_pmfs(tr, cmo, cto, cm, ct, Y, hs, ht)
            elif d == "gauss":
                cm, ct, cmo, cto = centres(sp["centre"], tr, te, cache); P = gauss_pmfs(cmo, cto, tr, cm, ct)
            elif d == "poss_raw":
                P = poss_pmfs(te); cm = ct = np.full(len(te), np.nan)
            elif d == "mix":
                w = mix_weight(sp["parts"], Y); mixw[i] = w; P = [w * a + (1 - w) * b_ for a, b_ in zip(pm[sp["parts"][0]], pm[sp["parts"][1]])]
                cm = ct = np.full(len(te), np.nan)
            pm[i] = P
            for k, r in enumerate(te.itertuples(index=False)):
                s = score(P[k], r, u[k]); s.update(game_id=r.game_id, season=Y, spread=float(r.spread_line), total_line=float(r.total_line),
                                                   y_m=float(r.result), y_t=float(r.total), cm=float(cm[k]), ct=float(ct[k]), mkt_pwin=float(r.mkt_pwin))
                if i in mixw: s["mix_w"] = mixw[i]
                rows[i].append(s)
        for i in ids:                       # persist after every season so later mixtures see earlier out-of-sample scores
            new = pd.DataFrame(rows[i]); path = os.path.join(RES, f"{i}.parquet")
            if os.path.exists(path):
                old = pd.read_parquet(path); new = pd.concat([old[~old.season.isin(new.season.unique())], new], ignore_index=True)
            new.sort_values("game_id").reset_index(drop=True).to_parquet(path)
        rows = {i: [] for i in ids}
        verbose(f"season {Y} done ({time.time() - t0:.0f}s)")
