"""Game Flow Intelligence Championship (RESEARCH_ONLY): final-evaluation report (G5 construction, intervals, calibration,
coherence, offensive-behaviour targets).  Everything here reads frozen forecasts; nothing is refitted on evaluation outcomes."""
from __future__ import annotations
import json, os, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy import stats
from scripts.sim import gf_eval as E, gf_models as GM, gf_data as GD

OUT, B = E.OUT, 5000
PRIM, SEC = E.PRIM, E.SEC
PERIODS = {"holdout_2010_2012": E.HOLD, "reused_2013_2025": E.REUSED, "reused_2021_2025_score_path_exposed": list(range(2021, 2026))}


def recs_for(mid, seasons):
    return E.load_rec(mid, seasons)


def fit_g5_weight(Y, comps):
    """Weight on comps[1] fitted on the three previous seasons' OUT-OF-SAMPLE forecasts only."""
    prev = [y for y in range(Y - 3, Y)]
    r0, r1 = recs_for(comps[0], prev), recs_for(comps[1], prev); m0 = E.metrics(r0); base = m0[PRIM].mean()
    best = None
    for w in np.linspace(0, 1, 11):
        m = E.metrics(E.mix([r0, r1], [1 - w, w])); sc = float(np.mean((m[PRIM].mean() / base).to_numpy()))
        if best is None or sc < best[0]:
            best = (sc, float(w))
    return best[1]


def g5_records(seasons, comps):
    out, ws = [], {}
    for Y in seasons:
        w = fit_g5_weight(Y, comps); ws[Y] = w; out.append(E.mix([recs_for(comps[0], [Y]), recs_for(comps[1], [Y])], [1 - w, w]))
    rec = {k: np.concatenate([o[k] for o in out]) for k in out[0]}; return rec, ws


def paired_ci(base, d, col, seed=11):
    u, v = d[col].to_numpy(float), base[col].to_numpy(float); n = len(u); idx = np.random.default_rng(seed).integers(0, n, size=(B, n))
    bs = u[idx].sum(1) / v[idx].sum(1) - 1; return [float(u.sum() / v.sum() - 1), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def reliability(p, y, bins=10):
    b = np.minimum((p * bins).astype(int), bins - 1); rows = []
    for k in range(bins):
        m = b == k
        if m.sum():
            rows.append({"bin": k, "n": int(m.sum()), "mean_p": float(p[m].mean()), "obs": float(y[m].mean())})
    r = pd.DataFrame(rows); ece = float((r.n * (r.mean_p - r.obs).abs()).sum() / r.n.sum())
    chi = float(((r.n * (r.mean_p - r.obs) ** 2) / np.maximum(r.mean_p * (1 - r.mean_p), 1e-6)).sum()); pval = float(1 - stats.chi2.cdf(chi, max(len(r) - 2, 1)))
    return {"ece": ece, "hl_chi2_p": pval, "bins": r.to_dict(orient="records")}


def coherence(rec):
    pm = rec["pm"]; pe = rec["pe"]; ht = np.arange(-50, 51)
    return {"pmf_sums_to_1_max_err": float(np.abs(rec["pm"].sum(1) - 1).max()), "events_in_01": bool(((pe >= -1e-9) & (pe <= 1 + 1e-9)).all()),
            "home_lead7_equals_pmf_mass_max_err": float(np.abs(pe[:, 4] - pm[:, ht >= 7].sum(1)).max()), "away_lead7_equals_pmf_mass_max_err": float(np.abs(pe[:, 5] - pm[:, ht <= -7].sum(1)).max()),
            "leads_sum_le_1": bool((pe[:, 4] + pe[:, 5] <= 1 + 1e-9).all()), "comeback_le_lead_changes_not_testable": True}


# ------------------------------------------------------------------------------------------ offensive behaviour
TB = ["plays", "dropbacks", "rushes", "drives", "pr_h1", "pr_h2", "pr_trail7", "pr_lead7"]


def team_rows():
    G, T, _ = GD.build(); s = GM.GF.schedule_frame()[["game_id", "home_team", "away_team", "spread_line", "total_line"]]
    t = T.merge(GM.flow_table()[["game_id"]], on="game_id").merge(s, on="game_id", how="inner").dropna(subset=["spread_line", "total_line"])
    t["is_home"] = (t.team == t.home_team).astype(int); t["team_spread"] = np.where(t.is_home == 1, t.spread_line, -t.spread_line)
    t["pr_h1"] = t.db_h1 / (t.db_h1 + t.dr_h1).clip(lower=1); t["pr_h2"] = t.db_h2 / (t.db_h2 + t.dr_h2).clip(lower=1)
    t["pr_trail7"] = np.where(t.db_trail7 + t.dr_trail7 >= 8, t.db_trail7 / (t.db_trail7 + t.dr_trail7).clip(lower=1), np.nan)
    t["pr_lead7"] = np.where(t.db_lead7 + t.dr_lead7 >= 8, t.db_lead7 / (t.db_lead7 + t.dr_lead7).clip(lower=1), np.nan)
    return t.reset_index(drop=True)


def team_features(Y, t):
    g = GM.frame_for(Y).set_index("game_id"); rows = []
    for side, opp in (("h", "a"), ("a", "h")):
        x = t[t.is_home == (1 if side == "h" else 0)]; gg = g.reindex(x.game_id)
        f = pd.DataFrame(index=x.index)
        for st in ("plays", "sec_per_play", "neutral_pass_rate", "epa_play", "success_rate", "pass_epa", "rush_epa", "points", "expl_pass", "expl_rush"):
            f[f"own_{st}"] = gg[f"{side}_off_{st}"].to_numpy(); f[f"opp_{st}"] = gg[f"{opp}_def_{st}"].to_numpy()
        f["own_pass_trail"] = gg[f"{side}_pass_trail"].to_numpy(); f["own_pass_lead"] = gg[f"{side}_pass_lead"].to_numpy(); f["own_pass_slope"] = gg[f"{side}_pass_slope"].to_numpy()
        f["opp_pass_trail"] = gg[f"{opp}_pass_trail"].to_numpy(); f["opp_pass_lead"] = gg[f"{opp}_pass_lead"].to_numpy()
        f["coach_new"] = gg[f"{side}_cnew"].to_numpy(); f["coach_logten"] = gg[f"{side}_clog"].to_numpy()
        f["int_pass"] = f.own_pass_epa * f.opp_pass_epa; f["int_rush"] = f.own_rush_epa * f.opp_rush_epa; f["int_pace"] = f.own_sec_per_play * f.opp_sec_per_play; f["int_expl"] = f.own_expl_pass * f.opp_expl_pass
        rows.append(f)
    return pd.concat(rows).reindex(t.index)


FAM_T = {"T1": ["own_plays", "opp_plays", "own_sec_per_play", "opp_sec_per_play", "own_neutral_pass_rate", "opp_neutral_pass_rate", "own_epa_play", "opp_epa_play", "own_success_rate", "opp_success_rate", "own_pass_epa", "opp_pass_epa", "own_rush_epa", "opp_rush_epa", "own_points", "opp_points"],
         "T2": ["own_pass_trail", "own_pass_lead", "own_pass_slope", "opp_pass_trail", "opp_pass_lead", "coach_new", "coach_logten"],
         "T3": ["int_pass", "int_rush", "int_pace", "int_expl", "own_expl_pass", "opp_expl_pass", "own_expl_rush", "opp_expl_rush"]}


def team_behavior(seasons, bw=(6.0, 9.0)):
    t = team_rows(); out = {}
    for Y in seasons:
        tr = t[(t.season >= GM.TRAIN_START) & (t.season < Y)]; te = t[t.season == Y]; feat = team_features(Y, t)
        base_pred = {k: np.zeros(len(te)) for k in TB}; loo = {k: np.zeros(len(tr)) for k in TB}
        ws = 0.5 ** ((Y - tr.season.to_numpy(float)) / 6.0)
        for hflag in (0, 1):
            mt = (tr.is_home == hflag).to_numpy(); sub = tr[mt]; wsub = ws[mt]; ie = np.where((te.is_home == hflag).to_numpy())[0]
            ds = te.team_spread.to_numpy()[ie][:, None] - sub.team_spread.to_numpy()[None, :]; dt = te.total_line.to_numpy()[ie][:, None] - sub.total_line.to_numpy()[None, :]
            W = wsub[None, :] * GM._tri(ds, bw[0]) * GM._tri(dt, bw[1]) + 1e-9 * wsub[None, :]
            for k in TB:
                v = sub[k].to_numpy(float); ok = np.isfinite(v); Wk = W * ok[None, :]; base_pred[k][ie] = (Wk @ np.nan_to_num(v)) / Wk.sum(1)
            # leave-one-out training means (chunked)
            ix = np.where(mt)[0]
            for a in range(0, len(ix), 400):
                bb = ix[a:a + 400]; ds = tr.team_spread.to_numpy()[bb][:, None] - sub.team_spread.to_numpy()[None, :]; dt = tr.total_line.to_numpy()[bb][:, None] - sub.total_line.to_numpy()[None, :]
                Wl = wsub[None, :] * GM._tri(ds, bw[0]) * GM._tri(dt, bw[1]) + 1e-9 * wsub[None, :]; Wl[np.arange(len(bb)), np.arange(a, a + len(bb))] = 0
                for k in TB:
                    v = sub[k].to_numpy(float); ok = np.isfinite(v); Wk = Wl * ok[None, :]; loo[k][bb] = (Wk @ np.nan_to_num(v)) / Wk.sum(1)
        ftr, fte = feat.loc[tr.index], feat.loc[te.index]
        for k in TB:
            y = te[k].to_numpy(float); ok_te = np.isfinite(y); row = {"n": int(ok_te.sum()), "G0_mae": float(np.abs(y - base_pred[k])[ok_te].mean()), "G0_mse": float(((y - base_pred[k]) ** 2)[ok_te].mean())}
            r = tr[k].to_numpy(float) - loo[k]; okr = np.isfinite(r)
            for fam, cols in FAM_T.items():
                from scripts.sim.hmac_models import ridge_cv
                sh, _ = ridge_cv(ftr[cols].to_numpy(float)[okr], r[okr], tr.season.to_numpy()[okr], fte[cols].to_numpy(float), lams=(300.0, 3000.0, 30000.0))
                p = base_pred[k] + sh; row[f"{fam}_mae"] = float(np.abs(y - p)[ok_te].mean()); row[f"{fam}_mse"] = float(((y - p) ** 2)[ok_te].mean())
            out.setdefault(k, {})[Y] = row
    return out


def summarize_team(tb, seasons):
    s = {}
    for k, d in tb.items():
        rows = [d[Y] for Y in seasons if Y in d]; n = sum(r["n"] for r in rows)
        agg = lambda key: sum(r[key] * r["n"] for r in rows) / n
        s[k] = {"n": n, "G0_mae": agg("G0_mae"), **{f"{f}_rel_mse": float(agg(f"{f}_mse") / agg("G0_mse") - 1) for f in FAM_T}, **{f"{f}_rel_mae": float(agg(f"{f}_mae") / agg("G0_mae") - 1) for f in FAM_T}}
    return s


def main():
    fz = json.load(open(os.path.join(OUT, "frozen.json"))); bw = fz["bandwidth"]; g0, g1 = f"G0_{bw}", f"G1_{bw}"; comps = fz["g5_components"]; res = {"frozen": fz, "periods": {}}
    for pname, seasons in PERIODS.items():
        R = {m: recs_for(m, seasons) for m in ["GU", g0, f"G1_{bw}", f"G2_{bw}", f"G3_{bw}", "G4"]}
        if len(comps) == 2:
            R["G5"], ws = g5_records(seasons, comps)
            res.setdefault("g5_weights", {}).update({str(k): v for k, v in ws.items()})
        M_ = {m: E.metrics(r) for m, r in R.items()}; base = M_[g0]; p = {"n_games": int(len(base)), "models": {}}
        for m, d in M_.items():
            assert (d.game_id.to_numpy() == base.game_id.to_numpy()).all()
            e = {"means": {c: float(d[c].mean()) for c in PRIM + SEC}, "vs_G0": {c: paired_ci(base, d, c) for c in PRIM + SEC} if m != g0 else {}, "vs_GU": {c: paired_ci(M_["GU"], d, c) for c in PRIM + SEC} if m != "GU" else {},
                 "per_season_rel_vs_G0": {c: {int(s): float(d[d.season == s][c].mean() / base[base.season == s][c].mean() - 1) for s in seasons} for c in PRIM} if m != g0 else {}}
            e["calibration"] = {ev: reliability(d[f"p_{ev}"].to_numpy(), d[f"y_{ev}"].to_numpy()) for ev in GM.EV}
            e["coherence"] = coherence(R[m]); p["models"][m] = e
        p["event_base_rates"] = {ev: float(base[f"y_{ev}"].mean()) for ev in GM.EV}; res["periods"][pname] = p
    res["offensive_behavior"] = {"by_period": {}}
    tb = team_behavior(E.DEV + E.SEL + E.HOLD + E.REUSED)
    for name, ss in (("development", E.DEV), ("selection", E.SEL), ("holdout_2010_2012", E.HOLD), ("reused_2013_2025", E.REUSED)):
        res["offensive_behavior"]["by_period"][name] = summarize_team(tb, ss)
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)
    for pname, p in res["periods"].items():
        print("==", pname, p["n_games"])
        for m, e in p["models"].items():
            print(f"{m:8s}", "  ".join(f"{c.replace('crps_','C:').replace('br_','B:')} {e['means'][c]:.4f}" for c in PRIM))
            if e["vs_G0"]:
                print("    vsG0", "  ".join(f"{c[:9]} {100 * v[0]:+.2f}[{100 * v[1]:+.2f},{100 * v[2]:+.2f}]" for c, v in e["vs_G0"].items() if c in PRIM))


if __name__ == "__main__":
    main()
