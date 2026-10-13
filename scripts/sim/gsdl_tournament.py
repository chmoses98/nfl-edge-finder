#!/usr/bin/env python3
"""Game Script Discovery Lab (RESEARCH_ONLY) -- tournament runner.

Every candidate is a complete predictive JOINT distribution of the final (home margin, total) on the integer lattice, built
exactly (no Monte Carlo) from a weighted set of historical outcomes, then optionally LOCATION-TILTED by a ridge model of
the market residual.  All scoring is from the pmf: margin / total CRPS, six-class script log loss, the repo's nine-cell
lattice, key-number mass, one-score / blowout probabilities, randomized PIT.

Walk-forward: season Y is predicted from games of seasons < Y only.  Reuses the incumbent's ResidualBank conventions
(``nfl_edge.pricing.game_env.ResidualBank``: season half-life 3, fractional-line matching, overtime model, parity fix) and the
nine-cell thresholds of ``nfl_edge.research.script_autopsy`` so Stage A reproduces the published baseline.

Usage: python scripts/sim/gsdl_tournament.py run [--stages A,B,C,D,E] [--seasons 2021,...]
"""
from __future__ import annotations
import argparse, json, os, sys, time, warnings
warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from nfl_edge.research.script_autopsy import ONE_SCORE, SHOOTOUT_OVER, LOW_SCORING_UNDER, BLOWOUT_MARGIN
from scripts.sim import gsdl_features as GF

OUT = os.path.join(ROOT, "research", "game_script_discovery_lab")
RES = os.path.join(OUT, "cache")
SEASONS = [2021, 2022, 2023, 2024, 2025]
SELECTION = [2021, 2022, 2023]          # screening / model selection
CONFIRM = [2024, 2025]                  # historical confirmation (touched once, for finalists / top five)
TRAIN_START = 2018                       # first season whose games train the feature models (2016-17 warm the EWMAs)
NM, NT = 121, 131                        # lattice: margin -60..60, total 0..130
GM = np.arange(NM) - 60; GT = np.arange(NT)
KEYS = [3, 6, 7, 10, 14]
SEED = 20261013

# ------------------------------------------------------------------------------------------------- feature sets
def fs(names):  # helper: margin and total columns for a list of matchup stats
    return [f"mf_{x}" for x in names], [f"sf_{x}" for x in names]

FAMILIES = {
    "mkt":   (["f_spread", "f_spread_sq"], ["f_total_line", "f_abs_spread"]),
    "oadj":  fs(["epa_play", "points", "success_rate"]),
    "tempo": fs(["plays", "sec_per_play", "neutral_pass_rate"]),
    "eff":   fs(["pass_epa", "rush_epa", "ypa", "ypc"]),
    "expl":  fs(["expl_pass", "expl_rush"]),
    "press": fs(["sack_rate", "hit"]),
    "qb":    (["f_qb_epa_diff", "f_qb_change_diff", "f_qb_new_diff"], ["f_qb_epa_sum", "f_qb_change_sum", "f_qb_new_sum"]),
    "rest":  (["f_rest_diff", "f_div"], ["f_rest_min", "f_short", "f_div", "f_dome"]),
    "coach": (["f_cnew_diff", "f_clog_diff"], ["f_cnew_sum", "f_clog_sum"]),
    "resid": (["f_ats_diff"], ["f_ou_mean"]),
    "wx":    ([], ["w_temp", "w_wind"]),      # NON_PIT observed weather: descriptive only, never eligible for claims
}
INTERACT = {
    "pass":  (["i_pass_m"], ["i_pass_s"], "eff"), "rush": (["i_rush_m"], ["i_rush_s"], "eff"),
    "pace":  (["i_pace_m"], ["i_pace_s"], "tempo"), "press_qb": (["i_press_m"], ["i_press_s"], "press+qb"),
    "coach_opp": (["i_coach_m"], ["i_coach_s"], "coach"), "expl": (["i_expl_m"], ["i_expl_s"], "expl"),
}
PIT_FAMILIES = ["mkt", "oadj", "tempo", "eff", "expl", "press", "qb", "rest", "coach", "resid"]


def union(names):
    m, t = [], []
    for n in names:
        a, b = FAMILIES[n]; m += a; t += b
    return list(dict.fromkeys(m)), list(dict.fromkeys(t))


def _cands():
    C = {}
    def add(cid, stage, desc, dist="A0", fam=(), inter=None, pit=True, extra=None):
        m, t = union(list(fam)) if fam else ([], [])
        if inter:
            im, it, base = INTERACT[inter]
            bm, bt = union(base.split("+")); m = list(dict.fromkeys(m + bm + im)); t = list(dict.fromkeys(t + bt + it))
        C[cid] = {"id": cid, "stage": stage, "desc": desc, "dist": dist, "families": list(fam), "interaction": inter,
                  "margin_features": m, "total_features": t, "pit_eligible": pit, **(extra or {})}
    add("A0", "A", "Incumbent market-centred residual bank (hl 3, 2016+, fractional match, OT model)")
    for f in FAMILIES:
        add(f"B_{f}", "B", f"A0 location-tilted by ridge on family '{f}'", fam=[f], pit=(f != "wx"))
    for k in INTERACT:
        add(f"C_{k}", "C", f"A0 tilted by main effects + interaction '{k}'", inter=k)
    D = {
        "D_uniform": ("bank, no season weighting", dict(hl=1e9)), "D_hl6": ("bank, half-life 6", dict(hl=6.0)),
        "D_2010": ("bank window 2010+, hl 3", dict(start=2010)),
        "D_gauss": ("bivariate Gaussian (bank moments)", dict(kind="gauss")),
        "D_kern_a": ("kernel on (spread,total line) h=(2,3.5), 2010+, hl 6", dict(kind="kernel", hs=2.0, ht=3.5, start=2010, hl=6.0)),
        "D_kern_b": ("kernel on (spread,total line) h=(3,5), 2010+, hl 6", dict(kind="kernel", hs=3.0, ht=5.0, start=2010, hl=6.0)),
        "D_mix": ("50/50 mixture of A0 and kernel_a", dict(kind="mix")),
        "D_indep": ("A0 marginals, independent margin and total", dict(post="indep")),
        "D_bk_spread": ("bank restricted to same |spread| bucket", dict(bucket="spread")),
        "D_bk_total": ("bank restricted to same total-line tercile", dict(bucket="total")),
        "D_bk_both": ("bank restricted to same spread bucket and total tercile", dict(bucket="both")),
        "D_fav": ("favourite-oriented bank (home/away symmetric)", dict(fav=True)),
        # regularised variants added after the raw sparse-support versions put zero mass on realised outcomes (log-loss blow-up):
        # a 10% tail floor from the incumbent bank.  Declared before any of them was scored.
        "D_kern_a_reg": ("kernel_a with 10% incumbent-bank floor", dict(kind="kernel", hs=2.0, ht=3.5, start=2010, hl=6.0, floor=0.1)),
        "D_kern_b_reg": ("kernel_b with 10% incumbent-bank floor", dict(kind="kernel", hs=3.0, ht=5.0, start=2010, hl=6.0, floor=0.1)),
        "D_bk_spread_reg": ("spread-bucket bank with 10% incumbent-bank floor", dict(bucket="spread", floor=0.1)),
        "D_bk_total_reg": ("total-tercile bank with 10% incumbent-bank floor", dict(bucket="total", floor=0.1)),
    }
    for k, (d, p) in D.items():
        add(k, "D", d, dist=k, extra={"dist_params": p})
    C["A0"]["dist_params"] = {}
    for k in C:
        C[k].setdefault("dist_params", {})
    return C


CANDIDATES = _cands()

# --------------------------------------------------------------------------------------------- pmf construction
def hist2(m, t, w):
    m = np.clip(m, -60, 60).astype(np.int64) + 60; t = np.clip(t, 0, 130).astype(np.int64)
    return np.bincount(m * NT + t, weights=w, minlength=NM * NT).reshape(NM, NT)


def finalize(m, t, w):
    """Home+away points must be integers: margin and total share parity.  Odd rows split to total+-1 (the incumbent nudge)."""
    odd = ((t + m) % 2) != 0
    return (np.concatenate([m[~odd], m[odd], m[odd]]), np.concatenate([t[~odd], t[odd] + 1, t[odd] - 1]),
            np.concatenate([w[~odd], w[odd] / 2, w[odd] / 2]))


class Bank:
    def __init__(self, g: pd.DataFrame, Y: int, start=2016, hl=3.0, bucket=None, fav=False):
        h = g[(g["season"] < Y) & (g["season"] >= start) & (g["game_type"] == "REG")]
        self.m = (h["result"] - h["spread_line"]).to_numpy(float); self.t = (h["total"] - h["total_line"]).to_numpy(float)
        self.sp = h["spread_line"].to_numpy(float); self.tl = h["total_line"].to_numpy(float)
        self.season = h["season"].to_numpy(float)
        self.sfrac = (self.sp % 1 != 0); self.tfrac = (self.tl % 1 != 0)
        w = 0.5 ** ((Y - self.season) / hl) if hl < 1e8 else np.ones(len(h)); self.w0 = w / w.sum()
        self.bucket = bucket; self.fav = fav
        self.sgn = np.where(self.sp >= 0, 1.0, -1.0)
        if fav:
            self.m = self.sgn * self.m
        self.sb = np.digitize(np.abs(self.sp), [3, 7, 10])
        self.q = np.quantile(self.tl, [1 / 3, 2 / 3]); self.tb = np.digitize(self.tl, self.q)
        ot = h[(h["overtime"].fillna(0) == 1)]["result"].to_numpy(float)
        self.p_tie = float(np.mean(ot == 0)) if len(ot) else 0.05
        nz = np.abs(ot[ot != 0]) if len(ot) else np.array([3.0, 3.0, 6.0, 7.0])
        self.ot_vals, cnt = np.unique(nz, return_counts=True); self.ot_p = cnt / cnt.sum()

    def weights(self, spread, tl):
        w = self.w0 * (self.sfrac == (spread % 1 != 0))
        w2 = w * (self.tfrac == (tl % 1 != 0))
        w = w2 if w2.sum() > 0 else w
        if self.bucket in ("spread", "both"):
            w3 = w * (self.sb == np.digitize(abs(spread), [3, 7, 10]))
            w = w3 if w3.sum() > 0.05 * w.sum() else w
        if self.bucket in ("total", "both"):
            w3 = w * (self.tb == np.digitize(tl, self.q))
            w = w3 if w3.sum() > 0.05 * w.sum() else w
        return w / w.sum()


def tilt(m, t, w, dm, dt, iters=10):
    """Exponential tilt of w so the weighted means move by (dm, dt): keeps integer support, so key numbers are not blurred."""
    X = np.stack([m, t], 1); mean0 = w @ X; tgt = mean0 + np.array([dm, dt]); th = np.zeros(2); q = w
    for _ in range(iters):
        z = X @ th; z -= z.max(); q = w * np.exp(z); q /= q.sum()
        mean = q @ X; g = mean - tgt
        if np.abs(g).max() < 1e-7:
            break
        cov = (X * q[:, None]).T @ X - np.outer(mean, mean)
        th = np.clip(th - np.linalg.solve(cov + 1e-9 * np.eye(2), g), -0.3, 0.3)
    return q


def bank_pmf(b: Bank, spread, tl, dm=0.0, dt=0.0):
    w = b.weights(spread, tl)
    mres, tres = b.m, b.t
    if dm or dt:
        w = tilt(mres, tres, w, dm, dt)
    sg = (1.0 if spread >= 0 else -1.0) if b.fav else 1.0
    m0 = np.round(spread + sg * mres); t0 = np.round(tl + tres)
    keep = w > 1e-12; m0, t0, w = m0[keep], t0[keep], w[keep]
    tie = m0 == 0
    M, T, W = [m0[~tie]], [t0[~tie]], [w[~tie]]
    if tie.any():
        wt, tt = w[tie], t0[tie]
        M.append(np.zeros_like(tt)); T.append(tt); W.append(wt * b.p_tie)
        ph = 1.0 / (1.0 + np.exp(-spread / 6.0))
        for v, pv in zip(b.ot_vals, b.ot_p):
            for sgn, ps in ((1.0, ph), (-1.0, 1 - ph)):
                M.append(np.full_like(tt, sgn * v)); T.append(tt + v); W.append(wt * (1 - b.p_tie) * pv * ps)
    return hist2(*finalize(np.concatenate(M), np.concatenate(T), np.concatenate(W)))


class Kernel:
    def __init__(self, g, Y, hs, ht, start, hl):
        h = g[(g["season"] < Y) & (g["season"] >= start) & (g["game_type"] == "REG")]
        self.m = h["result"].to_numpy(float); self.t = h["total"].to_numpy(float)
        self.sp = h["spread_line"].to_numpy(float); self.tl = h["total_line"].to_numpy(float)
        self.w0 = 0.5 ** ((Y - h["season"].to_numpy(float)) / hl); self.hs, self.ht = hs, ht

    def pmf(self, spread, tl, dm=0.0, dt=0.0):
        w = self.w0 * np.clip(1 - np.abs(self.sp - spread) / self.hs, 0, None) * np.clip(1 - np.abs(self.tl - tl) / self.ht, 0, None)
        if w.sum() < 1e-6:
            w = self.w0 * np.clip(1 - np.abs(self.sp - spread) / (3 * self.hs), 0, None)
        w = w / w.sum()
        m = self.m; t = self.t + np.round(tl - self.tl)
        if dm or dt:
            w = tilt(m, t, w, dm, dt)
        return hist2(*finalize(m, t, w))


def gauss_pmf(b: Bank, spread, tl, dm=0.0, dt=0.0):
    w = b.weights(spread, tl); mu = np.array([w @ b.m, w @ b.t]); X = np.stack([b.m, b.t], 1) - mu
    cov = (X * w[:, None]).T @ X; mu = mu + np.array([dm, dt])
    Mg, Tg = np.meshgrid(GM, GT, indexing="ij")
    d = np.stack([Mg - (spread + mu[0]), Tg - (tl + mu[1])], -1); inv = np.linalg.inv(cov)
    P = np.exp(-0.5 * np.einsum("...i,ij,...j", d, inv, d)); return P / P.sum()


# ------------------------------------------------------------------------------------------------------ scoring
def _orient(spread):
    return 1.0 if spread >= 0 else -1.0


def score_game(P, y_m, y_t, spread, tl, u):
    """All per-game scores from the pmf P (home margin x total).  Tied regulation+OT games (y_m == 0) are excluded from
    the six-class score only."""
    Pm = P.sum(1); Pt = P.sum(0); cm = np.cumsum(Pm); ct = np.cumsum(Pt)
    im = int(np.clip(y_m, -60, 60)) + 60; it = int(np.clip(y_t, 0, 130))
    o = {"crps_m": float(((cm - (np.arange(NM) >= im)) ** 2).sum()), "crps_t": float(((ct - (np.arange(NT) >= it)) ** 2).sum())}
    o["pit_m"] = float(cm[im] - Pm[im] + u[0] * Pm[im]); o["pit_t"] = float(ct[it] - Pt[it] + u[1] * Pt[it])
    sg = _orient(spread); fm = sg * GM
    cls = np.full(NM, -1); cls[fm >= 14] = 0; cls[(fm >= 7) & (fm <= 13)] = 1; cls[(fm >= 1) & (fm <= 6)] = 2
    cls[(fm <= -1) & (fm >= -6)] = 3; cls[(fm <= -7) & (fm >= -13)] = 4; cls[fm <= -14] = 5
    p6 = np.bincount(cls[cls >= 0], weights=Pm[cls >= 0], minlength=6); p6 = p6 / p6.sum()
    ofm = sg * y_m
    if ofm != 0:
        k = 0 if ofm >= 14 else 1 if ofm >= 7 else 2 if ofm >= 1 else 3 if ofm >= -6 else 4 if ofm >= -13 else 5
        o["ll6"] = float(-np.log(max(p6[k], 1e-9))); o["br6"] = float(((p6 - (np.arange(6) == k)) ** 2).sum())
    else:
        o["ll6"] = np.nan; o["br6"] = np.nan
    ci = np.where(fm > ONE_SCORE, 0, np.where(fm < -ONE_SCORE, 2, 1)); si = np.where(GT >= tl + SHOOTOUT_OVER, 0, np.where(GT <= tl - LOW_SCORING_UNDER, 2, 1))
    A = np.zeros((3, NM)); A[ci, np.arange(NM)] = 1; B = np.zeros((NT, 3)); B[np.arange(NT), si] = 1
    p9 = (A @ P @ B).ravel(); p9 = p9 / p9.sum()
    oc = int((0 if ofm > ONE_SCORE else 2 if ofm < -ONE_SCORE else 1) * 3 + (0 if y_t >= tl + SHOOTOUT_OVER else 2 if y_t <= tl - LOW_SCORING_UNDER else 1))
    o["ll9"] = float(-np.log(max(p9[oc], 1e-9))); o["br9"] = float(((p9 - (np.arange(9) == oc)) ** 2).sum())
    for k in KEYS:
        pk = Pm[60 + k] + Pm[60 - k]; ok = float(abs(y_m) == k)
        o[f"key{k}_p"] = float(pk); o[f"key{k}_br"] = float((pk - ok) ** 2); o[f"key{k}_obs"] = ok
    p1 = float(Pm[np.abs(GM) <= ONE_SCORE].sum()); o["one_p"] = p1; o["one_obs"] = float(abs(y_m) <= ONE_SCORE); o["one_br"] = (p1 - o["one_obs"]) ** 2
    pb = float(Pm[np.abs(GM) >= BLOWOUT_MARGIN].sum()); o["blow_p"] = pb; o["blow_obs"] = float(abs(y_m) >= BLOWOUT_MARGIN); o["blow_br"] = (pb - o["blow_obs"]) ** 2
    o["mean_m"] = float(Pm @ GM); o["mean_t"] = float(Pt @ GT)
    for j in range(9):
        o[f"p9_{j}"] = float(p9[j])
    return o


# ----------------------------------------------------------------------------------------------------- ridge shift
def ridge_shift(Xtr, ytr, season_tr, Xte, lams=(30.0, 300.0, 3000.0)):
    """Ridge with standardised columns; lambda chosen by leave-one-season-out CV on the TRAINING seasons only.
    Returns prediction minus the training mean (the location shift)."""
    mu = np.nanmean(Xtr, 0); sd = np.nanstd(Xtr, 0); sd[sd == 0] = 1.0
    Z = (np.where(np.isfinite(Xtr), Xtr, mu) - mu) / sd; Zt = (np.where(np.isfinite(Xte), Xte, mu) - mu) / sd
    def fit(Zx, yx, lam):
        yb = yx.mean(); return yb, np.linalg.solve(Zx.T @ Zx + lam * np.eye(Zx.shape[1]), Zx.T @ (yx - yb))
    best, bl = None, lams[-1]
    for lam in lams:
        err = 0.0
        for s in np.unique(season_tr):
            a = season_tr != s; yb, bt = fit(Z[a], ytr[a], lam); err += ((ytr[~a] - (yb + Z[~a] @ bt)) ** 2).sum()
        if best is None or err < best:
            best, bl = err, lam
    yb, bt = fit(Z, ytr, bl)
    return Zt @ bt, bl


_SCHED = None
def sched():
    global _SCHED
    if _SCHED is None:
        x = GF.schedule_frame(); _SCHED = x[x["result"].notna() & x["spread_line"].notna() & x["total_line"].notna()].copy()
    return _SCHED


def candidate_pmfs(cand, g, Y, test, cache):
    """Return the pmf of every test game of season Y."""
    H = sched()
    dp = cand["dist_params"]; kind = dp.get("kind", "bank")
    key = ("bank", dp.get("start", 2016), dp.get("hl", 3.0), dp.get("bucket"), dp.get("fav", False))
    if key not in cache:
        cache[key] = Bank(H, Y, start=key[1], hl=key[2], bucket=key[3], fav=key[4])
    b = cache[key]
    if kind in ("kernel", "mix"):
        kp = CANDIDATES["D_kern_a"]["dist_params"] if kind == "mix" else dp
        kk = ("kern", kp["hs"], kp["ht"], kp["start"], kp["hl"])
        if kk not in cache:
            cache[kk] = Kernel(H, Y, kp["hs"], kp["ht"], kp["start"], kp["hl"])
        kern = cache[kk]
        if kind == "mix" and ("bank", 2016, 3.0, None, False) not in cache:
            cache[("bank", 2016, 3.0, None, False)] = Bank(H, Y)
        if kind == "mix":
            b0 = cache[("bank", 2016, 3.0, None, False)]
    # location shifts from the ridge models
    dm = np.zeros(len(test)); dt = np.zeros(len(test)); lam = {}
    tr = g[(g["season"] < Y) & (g["season"] >= TRAIN_START) & (g["game_type"] == "REG")]
    for tgt, cols, out in (("mres", cand["margin_features"], dm), ("tres", cand["total_features"], dt)):
        if cols:
            sh, l = ridge_shift(tr[cols].to_numpy(float), tr[tgt].to_numpy(float), tr["season"].to_numpy(), test[cols].to_numpy(float))
            out[:] = np.clip(sh, -4.0, 4.0); lam[tgt] = l
    out = []
    for i, r in enumerate(test.itertuples(index=False)):
        sp, tl = float(r.spread_line), float(r.total_line)
        if kind == "bank":
            P = bank_pmf(b, sp, tl, dm[i], dt[i])
        elif kind == "gauss":
            P = gauss_pmf(b, sp, tl, dm[i], dt[i])
        elif kind == "kernel":
            P = kern.pmf(sp, tl, dm[i], dt[i])
        elif kind == "mix":
            P = 0.5 * bank_pmf(b0, sp, tl, dm[i], dt[i]) + 0.5 * kern.pmf(sp, tl, dm[i], dt[i])
        if dp.get("floor"):
            if ("bank", 2016, 3.0, None, False) not in cache:
                cache[("bank", 2016, 3.0, None, False)] = Bank(H, Y)
            P = (1 - dp["floor"]) * P / P.sum() + dp["floor"] * bank_pmf(cache[("bank", 2016, 3.0, None, False)], sp, tl, dm[i], dt[i])
        if dp.get("post") == "indep":
            P = np.outer(P.sum(1), P.sum(0))
        out.append(P / P.sum())
    return out, lam


def cell_prior_scores(g, Y, test, buckets):
    """Cell-level references (published B0 / B1): empirical nine-cell frequency of games before Y, optionally by |spread| bucket."""
    tr = g[(g["season"] < Y) & (g["season"] >= 2016)]
    def cells(d):
        sg = np.where(d["spread_line"] >= 0, 1.0, -1.0); fm = sg * d["result"].to_numpy(float)
        c = np.where(fm > ONE_SCORE, 0, np.where(fm < -ONE_SCORE, 2, 1)); s = np.where(d["total"] >= d["total_line"] + SHOOTOUT_OVER, 0, np.where(d["total"] <= d["total_line"] - LOW_SCORING_UNDER, 2, 1))
        return (c * 3 + s).astype(int)
    trc = cells(tr); tec = cells(test)
    bt = np.digitize(np.abs(tr["spread_line"]), [3, 7, 10]) if buckets else np.zeros(len(tr), int)
    be = np.digitize(np.abs(test["spread_line"]), [3, 7, 10]) if buckets else np.zeros(len(test), int)
    rows = []
    for i in range(len(test)):
        m = bt == be[i]; p = np.bincount(trc[m], minlength=9) / max(1, m.sum()); k = tec[i]
        rows.append({"ll9": float(-np.log(max(p[k], 1e-9))), "br9": float(((p - (np.arange(9) == k)) ** 2).sum())})
    return pd.DataFrame(rows)


def run_candidate(cid, seasons, verbose=print):
    os.makedirs(RES, exist_ok=True)
    path = os.path.join(RES, f"{cid}.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    cand = CANDIDATES.get(cid); rows = []; t0 = time.time()
    for Y in seasons:
        g = GF.build_season_frame(Y, verbose=lambda *_: None)
        test = g[(g["season"] == Y)].reset_index(drop=True)
        rng = np.random.default_rng(SEED + Y); U = rng.random((len(test), 2))
        if cid in ("A1", "A2"):
            sc = cell_prior_scores(g, Y, test, buckets=(cid == "A2")); sc.insert(0, "game_id", test["game_id"]); sc["season"] = Y; rows.append(sc); continue
        pm, lam = candidate_pmfs(cand, g, Y, test, {})
        for i, r in enumerate(test.itertuples(index=False)):
            s = score_game(pm[i], float(r.result), float(r.total), float(r.spread_line), float(r.total_line), U[i])
            s.update(game_id=r.game_id, season=Y, spread=float(r.spread_line), total_line=float(r.total_line), y_m=float(r.result), y_t=float(r.total))
            rows.append(s)
    df = pd.concat(rows, ignore_index=True) if isinstance(rows[0], pd.DataFrame) else pd.DataFrame(rows)
    df.to_parquet(path); verbose(f"{cid}: {len(df)} games, {time.time() - t0:.1f}s"); return df


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run", "list"]); ap.add_argument("--ids", default="")
    ap.add_argument("--seasons", default=",".join(map(str, SEASONS)))
    a = ap.parse_args(); seasons = [int(s) for s in a.seasons.split(",")]
    if a.cmd == "list":
        print(json.dumps(CANDIDATES, indent=1)); return
    ids = a.ids.split(",") if a.ids else ["A0", "A1", "A2"] + list(CANDIDATES)[1:]
    for cid in dict.fromkeys(ids):
        run_candidate(cid, seasons)


if __name__ == "__main__":
    main()
