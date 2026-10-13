"""HMAC (RESEARCH_ONLY) report: leaderboard, paired intervals, per-season, calibration, secondary targets, error decomposition."""
from __future__ import annotations
import json, os, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy import stats
from scripts.sim import hmac_models as M, hmac_features as H
from scripts.sim.hmac_run import load, OUT, PRIM, HOLD, REUSED, SEL, DEV

B = 5000
KEYS = T = M.T.KEYS


def paired_ci(base, d, seasons, col, seed=1):
    b = base[base.season.isin(seasons)]; m = d[d.season.isin(seasons)]
    x, y = b[col].to_numpy(float), m[col].to_numpy(float); ok = np.isfinite(x) & np.isfinite(y)
    x, y = np.where(ok, x, 0.0), np.where(ok, y, 0.0); n = len(x)
    idx = np.random.default_rng(seed).integers(0, n, size=(B, n))
    rel = y.sum() / x.sum() - 1; bs = y[idx].sum(1) / x[idx].sum(1) - 1
    return float(rel), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def calib(df):
    o = {}
    for pit in ("pit_m", "pit_t"):
        h = np.histogram(df[pit], bins=10, range=(0, 1))[0]; o[f"{pit}_p"] = float(stats.chisquare(h).pvalue)
        o[f"{pit}_cov50"] = float(((df[pit] >= .25) & (df[pit] <= .75)).mean()); o[f"{pit}_cov90"] = float(((df[pit] >= .05) & (df[pit] <= .95)).mean())
    for k in KEYS:
        o[f"key{k}"] = [float(df[f"key{k}_p"].mean()), float(df[f"key{k}_obs"].mean())]
    o["onescore"] = [float(df.one_p.mean()), float(df.one_obs.mean())]; o["blowout"] = [float(df.blow_p.mean()), float(df.blow_obs.mean())]
    o["key_brier_sum"] = float(sum(df[f"key{k}_br"].mean() for k in KEYS)); o["one_brier"] = float(df.one_br.mean()); o["blow_brier"] = float(df.blow_br.mean())
    return o


def secondary(df):
    ml = df.dropna(subset=["ml_obs"]); p = ml.ml_p.clip(1e-4, 1 - 1e-4); o = {}
    o["ml_logloss"] = float(-(ml.ml_obs * np.log(p) + (1 - ml.ml_obs) * np.log(1 - p)).mean())
    mk = ml.dropna(subset=["mkt_pwin"]); q = mk.mkt_pwin.clip(1e-4, 1 - 1e-4)
    o["ml_logloss_vs_marketML_sameGames"] = [float(-(mk.ml_obs * np.log(mk.ml_p.clip(1e-4, 1 - 1e-4)) + (1 - mk.ml_obs) * np.log(1 - mk.ml_p.clip(1e-4, 1 - 1e-4))).mean()),
                                              float(-(mk.ml_obs * np.log(q) + (1 - mk.ml_obs) * np.log(1 - q)).mean())]
    cv = df.dropna(subset=["cover_obs"]); o["cover_brier"] = float(((cv.cover_p - cv.cover_obs) ** 2).mean()); o["cover_brier_coinflip"] = 0.25
    o["cover_acc_of_pick"] = float((((cv.cover_p > .5) == (cv.cover_obs == 1))).mean())
    o["team_total_crps"] = float(((df.crps_h + df.crps_a) / 2).mean()); o["joint_logscore"] = float(df.jlog.mean())
    o["ll6_brier6"] = float(df.br6.mean()); o["brier9"] = float(df.br9.mean())
    return o


def decomposition(fz, g_cache={}):
    """Why does the market beat football-first?  Everything here is explanatory (post-hoc), never used for selection."""
    out = {}
    rows = []
    for Y in HOLD + REUSED:
        g = H.build(Y, verbose=lambda *_: None); te = g[g.season == Y].reset_index(drop=True)
        tr = g[(g.season >= M.TRAIN_START) & (g.season < Y) & (g.game_type == "REG")].reset_index(drop=True); cache = {}
        d = te[["game_id", "season", "week", "result", "total", "spread_line", "total_line", "f_qb_change_sum", "f_qb_new_sum", "f_dome", "f_div",
                "sf_sec_per_play", "sf_points", "f_elo", "game_type"]].copy()
        for kind in ("elo", "ff1", "ff2", "gbtA", "poss", "ens", "blend", "anchor"):
            cm, ct, _, _ = M.centres(kind, tr, te, cache); d[f"m_{kind}"] = cm; d[f"t_{kind}"] = ct
        rows.append(d)
    D_ = pd.concat(rows, ignore_index=True); D_.to_parquet(os.path.join(OUT, "decomposition_frame.parquet"))
    for name, seasons in (("holdout_2010_2012", HOLD), ("reused_2013_2025", REUSED)):
        x = D_[D_.season.isin(seasons)]; o = {}
        mk_m, mk_t = x.spread_line, x.total_line
        o["n"] = int(len(x))
        o["margin_MAE"] = {"market": float((x.result - mk_m).abs().mean()), **{k: float((x.result - x[f"m_{k}"]).abs().mean()) for k in ("elo", "ff1", "ff2", "gbtA", "poss", "ens", "blend", "anchor")}}
        o["margin_RMSE"] = {"market": float(np.sqrt(((x.result - mk_m) ** 2).mean())), **{k: float(np.sqrt(((x.result - x[f"m_{k}"]) ** 2).mean())) for k in ("elo", "ff1", "ff2", "gbtA", "poss", "ens", "blend", "anchor")}}
        o["total_MAE"] = {"market": float((x.total - mk_t).abs().mean()), **{k: float((x.total - x[f"t_{k}"]).abs().mean()) for k in ("elo", "ff1", "ff2", "gbtA", "poss", "ens", "blend", "anchor")}}
        o["total_RMSE"] = {"market": float(np.sqrt(((x.total - mk_t) ** 2).mean())), **{k: float(np.sqrt(((x.total - x[f"t_{k}"]) ** 2).mean())) for k in ("elo", "ff1", "ff2", "gbtA", "poss", "ens", "blend", "anchor")}}
        # encompassing regressions: outcome - market on (football - market); slope 0 => the market contains the football signal
        enc = {}
        for tgt, y, mk, fb in (("margin", x.result, mk_m, x.m_ens), ("total", x.total, mk_t, x.t_ens)):
            dx = (fb - mk).to_numpy(float); dy = (y - mk).to_numpy(float); b1 = (dx * dy).sum() / (dx ** 2).sum()
            res = dy - b1 * dx; se = np.sqrt((res ** 2 * dx ** 2).sum()) / (dx ** 2).sum()   # HC0
            enc[tgt] = {"slope": float(b1), "se": float(se), "sd_disagreement": float(dx.std()), "r2_gain_pct_of_market_mse": float(100 * (1 - (res ** 2).sum() / (dy ** 2).sum()))}
        o["encompassing_ens_vs_market"] = enc
        # who is right when they disagree: bins of football-minus-market margin
        dsg = (x.m_ens - x.spread_line); q = pd.qcut(dsg, 5, labels=False, duplicates="drop")
        o["margin_disagreement_bins"] = [{"bin": int(k), "mean_disagreement": float(dsg[q == k].mean()), "mean_outcome_minus_market": float((x.result - x.spread_line)[q == k].mean()), "n": int((q == k).sum())} for k in sorted(q.unique())]
        # subgroup squared-error difference (football minus market): positive => football loses
        e_f = (x.result - x.m_ens) ** 2 - (x.result - x.spread_line) ** 2; tot = e_f.sum()
        grp = {"week_1_4": x.week <= 4, "week_5_9": x.week.between(5, 9), "week_10_plus": x.week >= 10, "qb_change": x.f_qb_change_sum > 0, "no_qb_change": x.f_qb_change_sum == 0,
               "new_qb": x.f_qb_new_sum > 0, "big_spread_10plus": x.spread_line.abs() >= 10, "small_spread_under3": x.spread_line.abs() < 3, "dome": x.f_dome == 1, "outdoor": x.f_dome == 0,
               "division": x.f_div == 1, "playoff": x.game_type != "REG"}
        sp = pd.qcut(x.sf_sec_per_play, 3, labels=["fast_pace", "mid_pace", "slow_pace"]); tt = pd.qcut(x.total_line, 3, labels=["low_total", "mid_total", "high_total"])
        for lab in ("fast_pace", "mid_pace", "slow_pace"): grp[lab] = sp == lab
        for lab in ("low_total", "mid_total", "high_total"): grp[lab] = tt == lab
        o["margin_mse_gap_by_group"] = {k: {"n": int(m.sum()), "football_minus_market_mse": float(e_f[m].mean()), "market_mse": float(((x.result - x.spread_line) ** 2)[m].mean())} for k, m in grp.items() if m.sum() > 30}
        e_t = (x.total - x.t_ens) ** 2 - (x.total - x.total_line) ** 2
        o["total_mse_gap_by_group"] = {k: {"n": int(m.sum()), "football_minus_market_mse": float(e_t[m].mean())} for k, m in grp.items() if m.sum() > 30}
        out[name] = o
    # learning curve: does more training data close the gap?  (ff2 margin MSE vs market, by training window length)
    lc = {}
    for Y in (2012, 2016, 2020, 2024):
        g = H.build(Y, verbose=lambda *_: None); te = g[g.season == Y]
        for n in (2, 4, 8, 30):
            tr = g[(g.season >= max(M.TRAIN_START, Y - n)) & (g.season < Y) & (g.game_type == "REG")]
            if tr.season.nunique() < min(n, Y - M.TRAIN_START) or tr.season.nunique() < 2:
                continue
            cm, ct, _, _ = M.centres("ff2", tr.reset_index(drop=True), te.reset_index(drop=True), {})
            lc.setdefault(Y, {})[n if n < 30 else "all"] = {"seasons": int(tr.season.nunique()), "ff2_over_market_rmse": float(np.sqrt(((te.result - cm) ** 2).mean()) / np.sqrt(((te.result - te.spread_line) ** 2).mean()))}
    out["learning_curve_ff2_margin_rmse_ratio"] = lc
    return out


def main():
    fz = json.load(open(os.path.join(OUT, "frozen.json"))); ids = fz["finalists"]; base = load("A1"); bench = load(fz["market_benchmark"]); R = {}
    for name, seasons in (("holdout_2010_2012", HOLD), ("reused_2013_2025", REUSED)):
        R[name] = {"n_games": int(len(base[base.season.isin(seasons)])), "models": {}}
        for i in ids:
            d = load(i); m = d[d.season.isin(seasons)]
            e = {"means": {p: float(m[c].mean()) for p, c in PRIM.items()}, "calibration": calib(m), "secondary": secondary(m), "vs_A1": {}, "vs_benchmark": {}, "per_season_rel_vs_A1": {}}
            for p, c in PRIM.items():
                e["vs_A1"][p] = paired_ci(base, d, seasons, c); e["vs_benchmark"][p] = paired_ci(bench, d, seasons, c)
                e["per_season_rel_vs_A1"][p] = {int(s): float(d[d.season == s][c].mean() / base[base.season == s][c].mean() - 1) for s in seasons}
            R[name]["models"][i] = e
    R["decomposition"] = decomposition(fz)
    json.dump(R, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)
    pd.set_option("display.width", 250)
    for name in ("holdout_2010_2012", "reused_2013_2025"):
        print("==", name, R[name]["n_games"])
        for i in ids:
            e = R[name]["models"][i]
            print(f"{i:14s}", "  ".join(f"{p[:2]} {e['means'][p]:.3f} ({100 * e['vs_A1'][p][0]:+.2f}% [{100 * e['vs_A1'][p][1][0]:+.2f},{100 * e['vs_A1'][p][1][1]:+.2f}])" for p in PRIM))
    print(json.dumps(R["decomposition"]["holdout_2010_2012"]["margin_RMSE"], indent=0)); print(json.dumps(R["decomposition"]["reused_2013_2025"]["margin_RMSE"], indent=0))


if __name__ == "__main__":
    main()
