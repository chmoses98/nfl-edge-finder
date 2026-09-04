#!/usr/bin/env python3
"""Does the ladder calibrator help out of sample, or only in the season it was fitted on?

Strict walk-forward with no overlap anywhere:
  * for evaluation season S, the model is fitted on seasons < S;
  * the calibrator is fitted on season S-1 only, using predictions from a model fitted on seasons < S-1 --
    so the calibrator never sees a prediction from a model that trained on the calibration season, and
    never sees season S at all.
Only then is the calibrated model scored on S.
"""
import json, os, sys
from collections import defaultdict

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research import player_distributions as pdist  # noqa: E402
from nfl_edge.pricing.calibration import LadderCalibrator  # noqa: E402
from nfl_edge.shadow.models import CHOSEN_FAMILY  # noqa: E402

OUT = os.path.join(ROOT, "research", "tail_calibration"); os.makedirs(OUT, exist_ok=True)
EVAL = list(range(2020, 2026))
STATS = ["receiving_yards", "rushing_yards", "receptions", "targets", "passing_yards"]


def rung_probs(df, pm, spec, fam_name, train_seasons, test_season, role):
    tr = df[pm & df.season.isin(train_seasons)]
    te = df[pm & (df.season == test_season)]
    if len(tr) < 2000 or len(te) < 200:
        return None
    y_tr = np.clip(tr[spec.col].to_numpy(float), 0, None)
    y_te = np.clip(te[spec.col].to_numpy(float), 0, None)
    mm = pdist.fit_mean_model(tr, spec, spec.col, spec.kind, role=role)
    om = pdist.fit_mean_model(tr, spec, spec.opp, "count", role=role)
    mu_tr = pdist.predict_mean(mm, tr, spec, spec.col, pdist.MU_FLOOR[spec.kind])
    mu_te = pdist.predict_mean(mm, te, spec, spec.col, pdist.MU_FLOOR[spec.kind])
    muo_tr = pdist.predict_mean(om, tr, spec, spec.opp, 0.1)
    muo_te = pdist.predict_mean(om, te, spec, spec.opp, 0.1)
    eff_tr = tr[spec.eff].to_numpy() if spec.eff and spec.eff in tr.columns else None
    eff_te = te[spec.eff].to_numpy() if spec.eff and spec.eff in te.columns else None
    fam = pdist.make_family(fam_name, spec)
    fam.fit(mu_tr, muo_tr, eff_tr, y_tr)
    grid = np.arange(0, spec.grid_max + 1)
    F = fam.cdf_grid(mu_te, muo_te, eff_te, grid)
    Sv = np.clip(1.0 - np.concatenate([np.zeros((F.shape[0], 1)), F[:, :-1]], axis=1), 0, 1)
    P, Y, G = [], [], []
    gid = te["game_id"].to_numpy()
    for k in spec.thresholds:
        if not (0.02 < float((y_tr >= k).mean()) < 0.98):
            continue
        idx = int(np.clip(np.searchsorted(grid, k, side="left"), 0, len(grid) - 1))
        P.append(Sv[:, idx]); Y.append((y_te >= k).astype(float)); G.append(gid)
    if not P:
        return None
    return np.concatenate(P), np.concatenate(Y), np.concatenate(G)


def score(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(np.mean((p - y) ** 2)), float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def main():
    df = pl.read_parquet(os.path.join(ROOT, "research/opportunity/opportunity_features.parquet")).to_pandas()
    df = df.sort_values(["player_id", "season", "week"]).reset_index(drop=True)
    role = pdist.has_role_features(df)
    report = {}
    for name in STATS:
        spec = pdist.STAT_SPECS[name]
        fam_name = CHOSEN_FAMILY.get(name, "negbin")
        pm = pdist.population_mask(df, spec.pop)
        rows = []
        for S in EVAL:
            cal_seasons = list(range(2016, S - 1))
            if len(cal_seasons) < 3:
                continue
            calset = rung_probs(df, pm, spec, fam_name, cal_seasons, S - 1, role)
            testset = rung_probs(df, pm, spec, fam_name, list(range(2016, S)), S, role)
            if calset is None or testset is None:
                continue
            cal = LadderCalibrator().fit(calset[0], calset[1])
            p, y, _g = testset
            pc = cal.transform(p)
            b0, l0 = score(p, y); b1, l1 = score(pc, y)
            lo = p < 0.20
            rows.append({"season": S, "n": int(len(y)), "brier_raw": b0, "brier_cal": b1,
                         "logloss_raw": l0, "logloss_cal": l1, "cal_fit_n": cal.n_fit_,
                         "lowp_bias_raw": float((y[lo] - p[lo]).mean()) if lo.any() else None,
                         "lowp_bias_cal": float((y[lo] - pc[lo]).mean()) if lo.any() else None,
                         "lowp_n": int(lo.sum())})
        if not rows:
            continue
        w = sum(r["n"] for r in rows)
        pooled = {k: sum(r[k] * r["n"] for r in rows) / w for k in
                  ("brier_raw", "brier_cal", "logloss_raw", "logloss_cal")}
        wl = sum(r["lowp_n"] for r in rows)
        pooled["lowp_bias_raw"] = sum(r["lowp_bias_raw"] * r["lowp_n"] for r in rows) / wl
        pooled["lowp_bias_cal"] = sum(r["lowp_bias_cal"] * r["lowp_n"] for r in rows) / wl
        wins = sum(1 for r in rows if r["brier_cal"] < r["brier_raw"])
        report[name] = {"by_season": rows, "pooled": pooled, "seasons_improved": wins, "seasons": len(rows)}
        print(f"\n{name} ({fam_name}), {w} rungs over {len(rows)} seasons")
        print(f"  Brier   {pooled['brier_raw']:.5f} -> {pooled['brier_cal']:.5f} "
              f"({pooled['brier_cal']-pooled['brier_raw']:+.5f})   improves {wins}/{len(rows)} seasons")
        print(f"  LogLoss {pooled['logloss_raw']:.5f} -> {pooled['logloss_cal']:.5f} "
              f"({pooled['logloss_cal']-pooled['logloss_raw']:+.5f})")
        print(f"  bias where model p<0.20 (n={wl}): {pooled['lowp_bias_raw']:+.5f} -> {pooled['lowp_bias_cal']:+.5f}")
    json.dump(report, open(os.path.join(OUT, "calibration_results.json"), "w"), indent=1, default=float)
    imp = sum(1 for v in report.values() if v["pooled"]["brier_cal"] < v["pooled"]["brier_raw"])
    print(f"\nCALIBRATION IMPROVES BRIER IN {imp}/{len(report)} STATISTICS")


if __name__ == "__main__":
    main()
