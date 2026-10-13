#!/usr/bin/env python3
"""Historical Personnel Intelligence Championship (RESEARCH_ONLY): arms, protocol and evaluation.

  phaseb  where does the frozen football-first baseline lose to the market?  (development + selection seasons ONLY)
  dev     score arms on DEVELOPMENT seasons;  select  score on SELECTION seasons;  freeze  write frozen.json
  final   score the frozen arms ONCE on the previously exposed FINAL seasons;  report  tables + intervals
  perturb point-in-time perturbation tests of the new feature pipelines
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, warnings
warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from scripts.sim import hmac_features as H, hmac_models as M, pia_features as PF
from scripts.sim.hmac_report import paired_ci, calib, secondary

OUT = os.path.join(ROOT, "research", "personnel_intelligence_championship")
RES = os.path.join(OUT, "cache")
DEV, SEL, FIN = [2016, 2017, 2018], [2019, 2020, 2021], [2022, 2023, 2024]   # 2025 excluded: injury report not point-in-time certifiable
PRIM = {"P1_margin_crps": "crps_m", "P2_total_crps": "crps_t", "P3_script6_logloss": "ll6", "P4_joint9_logloss": "ll9"}
HS, HT = M.BW["k3"]
LAMS = (300.0, 3000.0, 30000.0)

SIGNED = lambda a, b: f"{a}"
QB_F = ["qb_adj_epa", "qb_drop", "qb_exp", "qb_sack_rate", "backup_start", "qb_unc"]
OFF_F = ["lost_OL", "lost_WR", "lost_TE", "lost_RB", "cont_OL"]
DEF_F = ["lost_DL", "lost_LB", "lost_CB", "lost_S", "cont_DEF"]
FAMILY = {"qb": QB_F, "off": OFF_F, "def": DEF_F}


def frame(Y):
    """Baseline championship frame + new QB / personnel columns (home minus away, and sums)."""
    g = H.build(Y, verbose=lambda *_: None).copy()
    qb = PF.qb_table(list(range(2001, 2025))); pe, _ = PF.personnel_table(list(range(2012, 2025)))
    qb = qb.assign(qb_unc=1 / np.sqrt(qb.qb_eff_db + 50.0))
    new = {}
    for side, tcol in (("h", "home_team"), ("a", "away_team")):
        a = qb[["game_id", "team"] + [c for c in QB_F]].rename(columns={"team": tcol, **{c: f"{side}_{c}" for c in QB_F}})
        b = pe[["game_id", "team"] + OFF_F + DEF_F + ["abs_n_total"]].rename(columns={"team": tcol, **{c: f"{side}_{c}" for c in OFF_F + DEF_F + ["abs_n_total"]}})
        g = g.merge(a, on=["game_id", tcol], how="left").merge(b, on=["game_id", tcol], how="left")
    for c in QB_F + OFF_F + DEF_F + ["abs_n_total"]:
        new[f"d_{c}"] = g[f"h_{c}"] - g[f"a_{c}"]; new[f"s_{c}"] = g[f"h_{c}"] + g[f"a_{c}"]
    g = pd.concat([g, pd.DataFrame(new, index=g.index)], axis=1)
    g["pers_ok"] = g["h_lost_OL"].notna() & g["a_lost_OL"].notna()
    return g


def feats(fams):
    cols = [c for f in fams for c in FAMILY[f]]
    return [f"d_{c}" for c in cols], [f"s_{c}" for c in cols]


def residual_stage(tr, te, base, cols_m, cols_t, target_anchor=None):
    """Ridge on the baseline's OUT-OF-FOLD residual using only the new columns; returns (test shift, training OOF shift)."""
    cm, ct, cmo, cto = base; out = []
    for cols, y, oof, pred, sp in ((cols_m, tr["result"].to_numpy(float), cmo, cm, None), (cols_t, tr["total"].to_numpy(float), cto, ct, None)):
        if not cols:
            out.append((np.zeros(len(te)), np.zeros(len(tr)))); continue
        X, Xt = tr[cols].to_numpy(float), te[cols].to_numpy(float); ok = np.isfinite(X).any(1)
        res = y - oof; s = tr["season"].to_numpy()
        sh_te, sh_oof = M.ridge_cv(X[ok], res[ok], s[ok], Xt, lams=LAMS)
        o = np.zeros(len(tr)); o[ok] = sh_oof; out.append((sh_te, o))
    return out


def arm_centres(arm, tr, te, cache):
    base = M.centres("ff2", tr, te, cache)
    cm, ct, cmo, cto = base
    if arm == "P0":
        return base
    fams = {"P1": ["qb"], "P2": ["off"], "P3": ["def"], "P4": FROZEN_P4}.get(arm)
    if fams is not None:
        cols_m, cols_t = feats(fams)
        (sm, smo), (st, sto) = residual_stage(tr, te, base, cols_m, cols_t)
        return cm + sm, ct + st, cmo + smo, cto + sto
    # market-anchored arms: line + ridge(result - line ~ [ff2 - line, personnel])
    sp_te, tl_te = te["spread_line"].to_numpy(float), te["total_line"].to_numpy(float); sp_tr, tl_tr = tr["spread_line"].to_numpy(float), tr["total_line"].to_numpy(float)
    fams = {"P5b": [], "P5": ["qb", "off", "def"], "P5q": ["qb"], "P5p": ["off", "def"]}[arm]
    cols_m, cols_t = feats(fams)
    Dm_tr = np.c_[cmo - sp_tr, tr[cols_m].to_numpy(float)] if cols_m else (cmo - sp_tr)[:, None]
    Dm_te = np.c_[cm - sp_te, te[cols_m].to_numpy(float)] if cols_m else (cm - sp_te)[:, None]
    Dt_tr = np.c_[cto - tl_tr, tr[cols_t].to_numpy(float)] if cols_t else (cto - tl_tr)[:, None]
    Dt_te = np.c_[ct - tl_te, te[cols_t].to_numpy(float)] if cols_t else (ct - tl_te)[:, None]
    a, ao = M.ridge_cv(Dm_tr, tr["result"].to_numpy(float) - sp_tr, tr["season"].to_numpy(), Dm_te, lams=LAMS)
    b, bo = M.ridge_cv(Dt_tr, tr["total"].to_numpy(float) - tl_tr, tr["season"].to_numpy(), Dt_te, lams=LAMS)
    return sp_te + a, tl_te + b, sp_tr + ao, tl_tr + bo


ARMS = ["P0", "P1", "P2", "P3", "P4", "P5b", "P5", "P5q", "P5p"]
FROZEN_P4 = ["qb", "off", "def"]          # overwritten from frozen.json by `final` (credible families only)


def run_arms(arms, seasons, verbose=print):
    os.makedirs(RES, exist_ok=True); rows = {a: [] for a in arms}
    for Y in seasons:
        g = frame(Y); te = g[(g.season == Y) & (g.game_type == "REG")].reset_index(drop=True)
        tr = g[(g.season >= M.TRAIN_START) & (g.season < Y) & (g.game_type == "REG")].reset_index(drop=True)
        u = np.random.default_rng(M.T.SEED + Y).random((len(te), 2)); cache = {}
        for arm in arms:
            cm, ct, cmo, cto = arm_centres(arm, tr, te, cache)
            P = M.kernel_pmfs(tr, cmo, cto, cm, ct, Y, HS, HT)
            for k, r in enumerate(te.itertuples(index=False)):
                s = M.score(P[k], r, u[k]); s.update(game_id=r.game_id, season=Y, week=int(r.week), spread=float(r.spread_line), total_line=float(r.total_line),
                                                     y_m=float(r.result), y_t=float(r.total), cm=float(cm[k]), ct=float(ct[k]), mkt_pwin=float(r.mkt_pwin),
                                                     backup=float(r.s_backup_start > 0) if r.s_backup_start == r.s_backup_start else np.nan,
                                                     qbchg=float(r.f_qb_change_sum > 0), pers_ok=bool(r.pers_ok))
                rows[arm].append(s)
        for arm in arms:
            new = pd.DataFrame(rows[arm]); path = os.path.join(RES, f"{arm}.parquet")
            if os.path.exists(path):
                old = pd.read_parquet(path); new = pd.concat([old[~old.season.isin(new.season.unique())], new], ignore_index=True)
            new.sort_values("game_id").reset_index(drop=True).to_parquet(path)
        rows = {a: [] for a in arms}; verbose(f"season {Y} done")


def load(a):
    return pd.read_parquet(os.path.join(RES, f"{a}.parquet")).sort_values("game_id").reset_index(drop=True)


def sha(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(open(os.path.join(ROOT, p), "rb").read())
    return h.hexdigest()


CODE = ["scripts/sim/pia_features.py", "scripts/sim/pia_run.py", "scripts/sim/hmac_models.py", "scripts/sim/hmac_features.py"]


def rmse(d, col, y):
    return float(np.sqrt(((d[y] - d[col]) ** 2).mean()))


def phaseb():
    """Where does the frozen football-first baseline (P0 = ff2 centre) lose to the closing line?  Dev + selection seasons only."""
    d = pd.concat([frame(Y).query("season == @Y and game_type == 'REG'") for Y in DEV + SEL], ignore_index=True)
    tr_ = {}
    p0 = load("P0"); p0 = p0[p0.season.isin(DEV + SEL)].set_index("game_id")
    d = d.set_index("game_id").join(p0[["cm", "ct"]]); d["e_f"] = (d.result - d.cm) ** 2 - (d.result - d.spread_line) ** 2
    d["et_f"] = (d.total - d.ct) ** 2 - (d.total - d.total_line) ** 2
    grp = {"all": d.season > 0, "backup_start_either": (d.d_backup_start != 0) | (d.s_backup_start > 0), "no_backup_start": d.s_backup_start == 0,
           "qb_drop_big_neg_home_or_away(|d|>0.05)": d.d_qb_drop.abs() > 0.05, "qb_drop_small": d.d_qb_drop.abs() <= 0.05,
           "OL_starter_out(either team)": (d.s_lost_OL > 0.15), "no_OL_out": d.s_lost_OL <= 0.15, "DL_starter_out": d.s_lost_DL > 0.15, "DB_out": (d.s_lost_CB + d.s_lost_S) > 0.3,
           "multiple_starters_out(sum>=4)": (d.s_abs_n_total if "s_abs_n_total" in d else d.s_lost_OL * 0) >= 4,
           "big_favorite(|spread|>=10)": d.spread_line.abs() >= 10, "spread_3_to_10": d.spread_line.abs().between(3, 10, inclusive="left"), "small_spread": d.spread_line.abs() < 3,
           "late_season(week>=10)": d.week >= 10, "early_season(week<=6)": d.week <= 6, "personnel_features_available": d.pers_ok, "personnel_unavailable(weeks1-3)": ~d.pers_ok}
    out = {k: {"n": int(m.sum()), "football_minus_market_margin_mse": float(d.e_f[m].mean()), "football_minus_market_total_mse": float(d.et_f[m].mean()),
               "market_margin_rmse": float(np.sqrt(((d.result - d.spread_line) ** 2)[m].mean()))} for k, m in grp.items() if m.sum() > 30}
    # population-level: is the gap larger where personnel changes are large?  rank correlation with the squared-error gap
    from scipy import stats
    corr = {}
    for c in ("d_qb_drop", "s_lost_OL", "s_lost_DL", "s_lost_CB", "d_lost_OL", "d_lost_DL", "s_backup_start", "d_backup_start"):
        x = d[c].abs() if c.startswith("d_") else d[c]; ok = x.notna() & d.e_f.notna()
        corr[f"abs({c})" if c.startswith("d_") else c] = {"spearman_with_margin_mse_gap": float(stats.spearmanr(x[ok], d.e_f[ok]).correlation), "n": int(ok.sum())}
    json.dump({"seasons": DEV + SEL, "groups": out, "rank_correlations": corr}, open(os.path.join(OUT, "phaseB.json"), "w"), indent=1)
    for k, v in out.items():
        print(f"{k:42s} n={v['n']:5d} margin gap {v['football_minus_market_margin_mse']:+7.1f}  total gap {v['football_minus_market_total_mse']:+6.1f}")
    print(json.dumps(corr, indent=0))


def pooled(arms, seasons, base="P0"):
    b = load(base); b = b[b.season.isin(seasons)]; r = {}
    for a in arms:
        d = load(a); d = d[d.season.isin(seasons)]
        r[a] = {"margin_rmse": rmse(d, "cm", "y_m"), "total_rmse": rmse(d, "ct", "y_t"), **{p: float(d[c].mean()) for p, c in PRIM.items()},
                **{f"rel_{p}": float(d[c].mean() / b[c].mean() - 1) for p, c in PRIM.items()}}
    mk = {"market_margin_rmse": float(np.sqrt(((b.y_m - b.spread) ** 2).mean())), "market_total_rmse": float(np.sqrt(((b.y_t - b.total_line) ** 2).mean()))}
    return r, mk


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["phaseb", "dev", "select", "freeze", "final", "perturb"]); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.cmd == "dev":
        run_arms(["P0", "P1", "P2", "P3", "P5b", "P5", "P5q", "P5p"], DEV)
    elif a.cmd == "select":
        run_arms(["P0", "P1", "P2", "P3", "P5b", "P5", "P5q", "P5p"], SEL)
    elif a.cmd == "phaseb":
        phaseb()
    elif a.cmd == "freeze":
        import scripts.sim.pia_freeze as FZ
        FZ.main()


if __name__ == "__main__":
    main()
