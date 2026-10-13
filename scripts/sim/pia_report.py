"""Personnel Intelligence Championship (RESEARCH_ONLY): freeze rule, final evaluation, report, perturbation tests.

PREDEFINED credibility rule for a personnel family (applied to development + selection seasons pooled, written before any arm
score was read): with m, t the relative change of the arm's margin-RMSE and total-RMSE against P0,
    credible  <=>  min(m, t) <= -0.25%  AND  max(m, t) <= +0.10%  AND  (m + t)/2 improves in >= 4 of the 6 seasons.
P4 combines credible families only.  If none is credible, P4 is not run (no unreliable arm is padded in).
"""
from __future__ import annotations
import hashlib, json, os, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy import stats
from scripts.sim import pia_run as R, pia_features as PF, hmac_models as M
from scripts.sim.hmac_report import calib, secondary

OUT, RES, DEV, SEL, FIN, PRIM = R.OUT, R.RES, R.DEV, R.SEL, R.FIN, R.PRIM
B = 5000


def rmse_rel(a, b, seasons):
    x, y = a[a.season.isin(seasons)], b[b.season.isin(seasons)]
    f = lambda d: (np.sqrt(((d.y_m - d.cm) ** 2).mean()), np.sqrt(((d.y_t - d.ct) ** 2).mean()))
    (m1, t1), (m0, t0) = f(x), f(y); return m1 / m0 - 1, t1 / t0 - 1


def credible_families():
    p0 = R.load("P0"); out = {}
    for fam, arm in (("qb", "P1"), ("off", "P2"), ("def", "P3")):
        d = R.load(arm); m, t = rmse_rel(d, p0, DEV + SEL)
        per = [np.mean(rmse_rel(d, p0, [s])) for s in DEV + SEL]
        ok = (min(m, t) <= -0.0025) and (max(m, t) <= 0.0010) and (sum(v < 0 for v in per) >= 4)
        out[fam] = {"arm": arm, "margin_rmse_rel": float(m), "total_rmse_rel": float(t), "seasons_improved_of_6": int(sum(v < 0 for v in per)), "credible": bool(ok)}
    return out


def freeze():
    cred = credible_families(); fams = [f for f, v in cred.items() if v["credible"]]
    arms = ["P0", "P1", "P2", "P3"] + (["P4"] if fams else []) + ["P5b", "P5", "P5q", "P5p"]
    fz = {"split": {"development": DEV, "selection": SEL, "final_previously_exposed": FIN, "excluded": "2025 (injury report not point-in-time certifiable)"},
          "credibility": cred, "p4_families": fams, "arms_for_final": arms,
          "code_sha256": R.sha(R.CODE + ["scripts/sim/pia_report.py"])}
    json.dump(fz, open(os.path.join(OUT, "frozen.json"), "w"), indent=1); print(json.dumps(cred, indent=1)); print("P4 families:", fams)


def final():
    fz = json.load(open(os.path.join(OUT, "frozen.json"))); assert fz["code_sha256"] == R.sha(R.CODE + ["scripts/sim/pia_report.py"]), "code changed since freeze"
    R.FROZEN_P4 = fz["p4_families"]; R.run_arms(fz["arms_for_final"], FIN)


def aligned(a, b, seasons, col, mask=None):
    x = a[a.season.isin(seasons)].set_index("game_id"); y = b[b.season.isin(seasons)].set_index("game_id"); ix = x.index.intersection(y.index)
    if mask is not None:
        ix = ix.intersection(mask)
    return x.loc[ix], y.loc[ix]


def ci(a, b, seasons, col, mask=None, seed=3):
    """relative change of mean(a[col]) vs mean(b[col]) on common games with a game-clustered bootstrap (one game = one cluster)."""
    x, y = aligned(a, b, seasons, col, mask); u, v = x[col].to_numpy(float), y[col].to_numpy(float); ok = np.isfinite(u) & np.isfinite(v)
    u, v = np.where(ok, u, 0.0), np.where(ok, v, 0.0); n = len(u); idx = np.random.default_rng(seed).integers(0, n, size=(B, n))
    bs = u[idx].sum(1) / v[idx].sum(1) - 1; return [float(u.sum() / v.sum() - 1), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), int(n)]


def rmse_ci(a, b, seasons, ycol, ccol, mask=None, seed=5):
    x, y = aligned(a, b, seasons, ccol, mask); u = ((x[ycol] - x[ccol]) ** 2).to_numpy(float); v = ((y[ycol] - y[ccol]) ** 2).to_numpy(float); n = len(u)
    idx = np.random.default_rng(seed).integers(0, n, size=(B, n)); bs = np.sqrt(u[idx].sum(1) / v[idx].sum(1)) - 1
    return [float(np.sqrt(u.sum() / v.sum()) - 1), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), int(n)]


def market_frame(d):
    """The closing line as a 'model' on the same games: centre = line."""
    m = d.copy(); m["cm"] = m["spread"]; m["ct"] = m["total_line"]; return m


def report(seasons=None, tag="final"):
    fz = json.load(open(os.path.join(OUT, "frozen.json"))); arms = fz["arms_for_final"]; ss = seasons or FIN
    D = {a: R.load(a) for a in arms}; p0 = D["P0"]
    from scripts.sim.hmac_run import load as hload
    a1, a3 = hload("A1"), hload("A3"); a1 = a1[a1.game_id.isin(p0.game_id)]; a3 = a3[a3.game_id.isin(p0.game_id)]
    mk = market_frame(p0)
    res = {"seasons": ss, "tag": tag, "n_games": int(len(p0[p0.season.isin(ss)])), "arms": {}}
    sub = {"all": None, "qb_change_or_backup": set(p0[(p0.qbchg > 0) | (p0.backup > 0)].game_id), "large_favorite_10plus": set(p0[p0.spread.abs() >= 10].game_id),
           "favorite_7plus": set(p0[p0.spread.abs() >= 7].game_id), "late_season_wk10plus": set(p0[p0.week >= 10].game_id), "personnel_features_available": set(p0[p0.pers_ok].game_id)}
    for a in arms:
        d = D[a]; m = d[d.season.isin(ss)]
        e = {"margin_rmse": float(np.sqrt(((m.y_m - m.cm) ** 2).mean())), "total_rmse": float(np.sqrt(((m.y_t - m.ct) ** 2).mean())), "means": {p: float(m[c].mean()) for p, c in PRIM.items()},
             "calibration": calib(m), "secondary": secondary(m), "vs_P0": {}, "vs_A3": {}, "vs_A1": {}, "rmse_vs_P0": rmse_ci(d, p0, ss, "y_m", "cm"), "rmse_vs_market": rmse_ci(d, mk, ss, "y_m", "cm"),
             "total_rmse_vs_market": rmse_ci(d, mk, ss, "y_t", "ct"), "subgroups": {}}
        for p, c in PRIM.items():
            e["vs_P0"][p] = ci(d, p0, ss, c); e["vs_A3"][p] = ci(d, a3, ss, c); e["vs_A1"][p] = ci(d, a1, ss, c)
        if a.startswith("P5"):
            e["vs_P5b"] = {p: ci(d, D["P5b"], ss, c) for p, c in PRIM.items()}; e["rmse_vs_P5b"] = rmse_ci(d, D["P5b"], ss, "y_m", "cm")
        for g, ids in sub.items():
            if ids is not None and len(ids & set(p0[p0.season.isin(ss)].game_id)) < 30:
                continue
            msk = None if ids is None else pd.Index(ids)
            e["subgroups"][g] = {"margin_rmse_vs_P0": rmse_ci(d, p0, ss, "y_m", "cm", msk), "margin_rmse_vs_market": rmse_ci(d, mk, ss, "y_m", "cm", msk), "crps_margin_vs_P0": ci(d, p0, ss, "crps_m", msk)}
        e["per_season_rel_vs_P0"] = {p: {int(s): float(d[(d.season == s)][c].mean() / p0[(p0.season == s)][c].mean() - 1) for s in ss} for p, c in PRIM.items()}
        res["arms"][a] = e
    mm = p0[p0.season.isin(ss)]; ml = mm.dropna(subset=["mkt_pwin", "ml_p"]); q = ml.mkt_pwin.clip(1e-4, 1 - 1e-4)
    res["market"] = {"margin_rmse": float(np.sqrt(((mm.y_m - mm.spread) ** 2).mean())), "total_rmse": float(np.sqrt(((mm.y_t - mm.total_line) ** 2).mean())),
                     "moneyline_logloss": float(-(ml.ml_obs.dropna() * 0).sum()) if False else float(-(ml.ml_obs * np.log(q) + (1 - ml.ml_obs) * np.log(1 - q)).mean())}
    # encompassing: does a centre carry information about the market residual?  (OLS slope with HC0 se)
    enc = {}
    for a in arms:
        m = D[a][D[a].season.isin(ss)]
        for tgt, y, line, c in (("margin", "y_m", "spread", "cm"), ("total", "y_t", "total_line", "ct")):
            dx = (m[c] - m[line]).to_numpy(float); dy = (m[y] - m[line]).to_numpy(float); b = (dx * dy).sum() / (dx ** 2).sum()
            se = np.sqrt((((dy - b * dx) ** 2) * dx ** 2).sum()) / (dx ** 2).sum(); enc.setdefault(a, {})[tgt] = {"slope": float(b), "se": float(se), "sd_disagreement": float(dx.std())}
    res["encompassing_vs_market"] = enc
    # direct test: market residual on pre-specified personnel contrasts (Bonferroni over the 6 tests per target)
    fr = pd.concat([R.frame(Y).query("season == @Y and game_type == 'REG'") for Y in ss], ignore_index=True).set_index("game_id")
    fr["mres"] = fr.result - fr.spread_line; fr["tres"] = fr.total - fr.total_line; direct = {}
    for tgt, feats_, y in (("margin", ["d_qb_drop", "d_qb_adj_epa", "d_lost_OL", "d_lost_DL", "d_lost_CB", "d_lost_WR"], "mres"), ("total", ["s_qb_adj_epa", "s_lost_OL", "s_lost_DL", "s_lost_CB", "s_lost_WR", "s_backup_start"], "tres")):
        for f in feats_:
            x = fr[[f, y]].dropna(); xv = x[f].to_numpy(float) - x[f].mean(); yv = x[y].to_numpy(float) - x[y].mean(); b = (xv * yv).sum() / (xv ** 2).sum()
            se = np.sqrt((((yv - b * xv) ** 2) * xv ** 2).sum()) / (xv ** 2).sum(); z = b / se
            direct[f"{tgt}~{f}"] = {"slope": float(b), "se": float(se), "z": float(z), "p_bonferroni6": float(min(1, 6 * 2 * (1 - stats.norm.cdf(abs(z))))), "n": int(len(x)), "sd_x": float(x[f].std())}
    res["market_residual_on_personnel"] = direct
    json.dump(res, open(os.path.join(OUT, f"results_{tag}.json"), "w"), indent=1, default=str)
    return res


def perturb():
    import polars as pl
    from nfl_edge.availability_pit import loaders as L
    sch = PF.GF.schedule_frame(); G = "2019_08_" + sch[(sch.season == 2019) & (sch.week == 8)].game_id.iloc[0][8:]; gd = sch.set_index("game_id").loc[G, "gameday"]
    seasons = list(range(2001, 2025)); out = {"perturbed_game": G, "gameday": gd}
    q = pd.concat([PF._qb_pbp(s) for s in seasons], ignore_index=True)
    base = PF.qb_table(seasons, q=q.copy()); q2 = q.copy(); m = q2.game_id == G
    q2.loc[m, ["epa", "db", "sacks"]] = q2.loc[m, ["epa", "db", "sacks"]].to_numpy() * np.array([1000, 3, 5]); pert = PF.qb_table(seasons, q=q2)
    gdmap = sch.set_index("game_id")["gameday"]; mm = base.merge(pert, on=["game_id", "team"], suffixes=("_b", "_p")); mm["gd"] = mm.game_id.map(gdmap)
    cols = [c for c in base.columns if c not in ("game_id", "team")]
    moved = lambda sel: int(sum((~np.isclose(sel[f"{c}_b"].astype(float), sel[f"{c}_p"].astype(float), equal_nan=True)).sum() for c in cols))
    out["qb_rows_moved_at_or_before_perturbed_game"] = moved(mm[mm.gd <= gd]); out["qb_rows_moved_after_control"] = moved(mm[mm.gd > gd])
    ps = list(range(2012, 2025)); sn = PF._snaps(ps); inj, _ = L.injuries_certified(PF.ROOT, ps and [s for s in ps if s >= 2010], game_type="REG")
    b, _ = PF.personnel_table(ps, sn=sn.copy(), inj=inj.copy()); sn2 = sn.copy(); mk = sn2.game_id == G
    sn2.loc[mk, ["offense_pct", "defense_pct"]] = 0.99; p1, _ = PF.personnel_table(ps, sn=sn2, inj=inj.copy())
    inj2 = inj.copy(); inj2.loc[inj2.game_id == G, "report_status"] = "Out"; p2, _ = PF.personnel_table(ps, sn=sn.copy(), inj=inj2)
    pc = [c for c in b.columns if c not in ("game_id", "team")]
    def cmp(x):
        z = b.merge(x, on=["game_id", "team"], suffixes=("_b", "_p")); z["gd"] = z.game_id.map(gdmap)
        mv = lambda sel: int(sum((~np.isclose(sel[f"{c}_b"].astype(float), sel[f"{c}_p"].astype(float), equal_nan=True)).sum() for c in pc))
        return mv(z[z.gd <= gd]), mv(z[z.gd > gd])
    out["personnel_snap_perturbation_rows_moved_at_or_before"], out["personnel_snap_perturbation_rows_moved_after_control"] = cmp(p1)
    z_before = b.merge(p2, on=["game_id", "team"], suffixes=("_b", "_p")); z_before["gd"] = z_before.game_id.map(gdmap)
    own = z_before[z_before.game_id == G]; earlier = z_before[z_before.gd < gd]
    out["injury_perturbation_earlier_rows_moved"] = int(sum((~np.isclose(earlier[f"{c}_b"].astype(float), earlier[f"{c}_p"].astype(float), equal_nan=True)).sum() for c in pc))
    out["injury_perturbation_own_game_rows_moved_(positive_control_expected_>0)"] = int(sum((~np.isclose(own[f"{c}_b"].astype(float), own[f"{c}_p"].astype(float), equal_nan=True)).sum() for c in pc))
    json.dump(out, open(os.path.join(OUT, "perturbation.json"), "w"), indent=1); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"freeze": freeze, "final": final, "perturb": perturb, "report": lambda: print(json.dumps({k: v for k, v in report().items() if k in ("n_games", "market")}, indent=1)),
     "report_exposed": lambda: report(DEV + SEL, "dev_select")}[cmd]()
