#!/usr/bin/env python3
"""Do the opportunity-engine role features improve the LADDER, not just the mean?

research/opportunity showed the role features cut mean-projection MAE by 2.6-3.1% in 7/7 seasons. Mean error
is not what prices a Kalshi ladder: the ladder consumes P(Y >= k) at each rung, and a better centre can still
leave the tails worse. This refits the whole pipeline -- mean model, opportunity model, distribution family --
walk-forward with and without the role features, and scores the rungs Kalshi actually lists.

Scoring is on the rungs, weighted the way the exchange lists them, with Brier and log loss plus a reliability
slope. Both arms are identical except for the design matrix.
"""
import json, os, sys

import numpy as np
import pandas as pd
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research import player_distributions as pdist  # noqa: E402
from nfl_edge.shadow.models import CHOSEN_FAMILY  # noqa: E402

OUT = os.path.join(ROOT, "research", "ladder_role"); os.makedirs(OUT, exist_ok=True)
EVAL = list(range(2019, 2026))
STATS = ["receiving_yards", "receptions", "rushing_yards", "carries", "targets", "passing_yards"]
# `--family <name>` refits every statistic with one family instead of the one the earlier study chose. Used to
# separate "the role features are bad" from "the family cannot absorb a sharper mean".
FAMILY_OVERRIDE = None


def score(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(np.mean((p - y) ** 2)), float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def main():
    global FAMILY_OVERRIDE
    if "--family" in sys.argv:
        FAMILY_OVERRIDE = sys.argv[sys.argv.index("--family") + 1]
        print(f"family override: {FAMILY_OVERRIDE}")
    df = pl.read_parquet(os.path.join(OUT, "..", "opportunity", "opportunity_features.parquet")).to_pandas()
    df = df.sort_values(["player_id", "season", "week"]).reset_index(drop=True)
    print(f"rows {len(df)}  role features present: {pdist.has_role_features(df)}", flush=True)

    report = {}
    for name in STATS:
        spec = pdist.STAT_SPECS[name]
        fam_name = FAMILY_OVERRIDE or CHOSEN_FAMILY.get(name, "negbin")
        pm = pdist.population_mask(df, spec.pop)
        rows = []
        for S in EVAL:
            tr = df[pm & (df.season < S) & (df.season >= 2016)]
            te = df[pm & (df.season == S)]
            if len(tr) < 2000 or len(te) < 200:
                continue
            y_tr = np.clip(tr[spec.col].to_numpy(float), 0, None)
            y_te = np.clip(te[spec.col].to_numpy(float), 0, None)
            # Which rungs count must NOT depend on the arm being scored. Filtering on each arm's own
            # predicted probability gives the two arms different denominators -- the sharper model pushes a
            # different set of rungs into the band, and the comparison silently measures the change of
            # subset rather than the change of skill. The band is set from the TRAINING outcomes, which both
            # arms share and neither can see at test time.
            live_rung = {}
            for k in spec.thresholds:
                rate = float((y_tr >= k).mean())
                live_rung[k] = 0.02 < rate < 0.98
            arm = {}
            arms_spec = ((("base", False, False), ("role", True, False)) if FAMILY_OVERRIDE else
                         (("base", False, False), ("role", True, False),
                          ("base_cf", False, True), ("role_cf", True, True)))
            for label, role, crossfit in arms_spec:
                mm = pdist.fit_mean_model(tr, spec, spec.col, spec.kind, role=role)
                om = pdist.fit_mean_model(tr, spec, spec.opp, "count", role=role)
                mu_te = pdist.predict_mean(mm, te, spec, spec.col, pdist.MU_FLOOR[spec.kind])
                muo_te = pdist.predict_mean(om, te, spec, spec.opp, 0.1)
                if crossfit:
                    # The family's dispersion describes how far Y falls from mu. Fitting it on IN-SAMPLE mu
                    # measures the residual of a mean model that has already seen those rows, which is
                    # smaller than the residual it will have live -- so the tails come out too tight, and the
                    # more features the mean model has, the tighter they wrongly get. Leave-one-season-out
                    # cross-fitting gives the family an honest mu with a deployment-sized error.
                    mu_tr = np.empty(len(tr)); muo_tr = np.empty(len(tr))
                    tr_seasons = tr.season.to_numpy()
                    for hold in np.unique(tr_seasons):
                        fit_m = tr_seasons != hold
                        if fit_m.sum() < 500:
                            mu_tr[~fit_m] = pdist.predict_mean(mm, tr[~fit_m], spec, spec.col, pdist.MU_FLOOR[spec.kind])
                            muo_tr[~fit_m] = pdist.predict_mean(om, tr[~fit_m], spec, spec.opp, 0.1)
                            continue
                        m2 = pdist.fit_mean_model(tr[fit_m], spec, spec.col, spec.kind, role=role)
                        o2 = pdist.fit_mean_model(tr[fit_m], spec, spec.opp, "count", role=role)
                        mu_tr[~fit_m] = pdist.predict_mean(m2, tr[~fit_m], spec, spec.col, pdist.MU_FLOOR[spec.kind])
                        muo_tr[~fit_m] = pdist.predict_mean(o2, tr[~fit_m], spec, spec.opp, 0.1)
                else:
                    mu_tr = pdist.predict_mean(mm, tr, spec, spec.col, pdist.MU_FLOOR[spec.kind])
                    muo_tr = pdist.predict_mean(om, tr, spec, spec.opp, 0.1)
                eff_tr = tr[spec.eff].to_numpy() if spec.eff and spec.eff in tr.columns else None
                eff_te = te[spec.eff].to_numpy() if spec.eff and spec.eff in te.columns else None
                fam = pdist.make_family(fam_name, spec)
                fam.fit(mu_tr, muo_tr, eff_tr, y_tr)
                grid = np.arange(0, spec.grid_max + 1)
                F = fam.cdf_grid(mu_te, muo_te, eff_te, grid)
                Sv = np.clip(1.0 - np.concatenate([np.zeros((F.shape[0], 1)), F[:, :-1]], axis=1), 0, 1)
                ps, ys = [], []
                for k in spec.thresholds:
                    if not live_rung[k]:
                        continue
                    idx = int(np.clip(np.searchsorted(grid, k, side="left"), 0, len(grid) - 1))
                    ps.append(Sv[:, idx]); ys.append((y_te >= k).astype(float))
                p = np.concatenate(ps); yy = np.concatenate(ys)
                br, ll = score(p, yy)
                arm[label] = {"brier": br, "logloss": ll, "n_rungs": int(len(p)),
                              "mae_mu": float(np.abs(mu_te - y_te).mean())}
            rows.append({"season": S, "n_players": len(te), **{f"{k}_{m}": arm[k][m]
                         for k in arm for m in ("brier", "logloss", "n_rungs", "mae_mu")}})
        if not rows:
            continue
        w = sum(r["base_n_rungs"] for r in rows)
        ARMS = tuple(arm.keys())
        pooled = {m: {k: sum(r[f"{k}_{m}"] * r["base_n_rungs"] for r in rows) / w for k in ARMS}
                  for m in ("brier", "logloss")}
        wins = sum(1 for r in rows if r["role_brier"] < r["base_brier"])
        report[name] = {"by_season": rows, "pooled": pooled, "seasons_improved": wins, "seasons": len(rows)}
        print(f"\n{name}  ({fam_name}, {w} live rungs)")
        print(f"    {'arm':10s} {'Brier':>9s} {'LogLoss':>9s}   (in-sample vs leave-one-season-out family fit)")
        for k in ARMS:
            print(f"    {k:10s} {pooled['brier'][k]:9.5f} {pooled['logloss'][k]:9.5f}")
        if "base_cf" in ARMS:
            cfw = sum(1 for r in rows if r["role_cf_brier"] < r["base_cf_brier"])
            print(f"  role helps in {wins}/{len(rows)} seasons in-sample-fit, {cfw}/{len(rows)} cross-fitted")
            report[name]["seasons_improved_cf"] = cfw
        else:
            print(f"  role helps in {wins}/{len(rows)} seasons")
    tag = f"_{FAMILY_OVERRIDE}" if FAMILY_OVERRIDE else ""
    json.dump(report, open(os.path.join(OUT, f"results{tag}.json"), "w"), indent=1, default=float)
    tot = sum(1 for v in report.values() if v["pooled"]["brier"]["role"] < v["pooled"]["brier"]["base"])
    print(f"\nrole features improve the ladder in {tot}/{len(report)} stats")
    if not FAMILY_OVERRIDE:
        totcf = sum(1 for v in report.values() if v["pooled"]["brier"]["role_cf"] < v["pooled"]["brier"]["base_cf"])
        cfbet = sum(1 for v in report.values() if v["pooled"]["brier"]["base_cf"] < v["pooled"]["brier"]["base"])
        print(f"  cross-fitted: {totcf}/{len(report)}; cross-fitting alone improves the baseline in "
              f"{cfbet}/{len(report)} stats")


if __name__ == "__main__":
    main()
