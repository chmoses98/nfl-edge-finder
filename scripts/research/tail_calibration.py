#!/usr/bin/env python3
"""Is the model's upper tail too fat? Measured on settled outcomes, by position on the ladder.

Two independent sources pointed the same way this session:
  * on live ladders the model held MORE upper-tail probability than the market (+0.018, 1.6 SE);
  * on settled 2025 markets the market's own high receiving-yards rungs were OVERPRICED by 7.5 points.

Together those say the market's tail is already too fat and the model's is fatter still -- i.e. the model has
a real tail defect rather than an edge. That is checkable directly against settled outcomes, without any
market prices at all: fit walk-forward, then compare predicted P(Y >= k) with the realised rate, bucketed by
where k sits on each player's ladder.

Rungs are bucketed by the model's own predicted probability, which is the operationally relevant axis (it is
what a pricer would act on) and is available at prediction time.
"""
import json, os, sys
from collections import defaultdict

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research import player_distributions as pdist  # noqa: E402
from nfl_edge.shadow.models import CHOSEN_FAMILY  # noqa: E402

OUT = os.path.join(ROOT, "research", "tail_calibration"); os.makedirs(OUT, exist_ok=True)
EVAL = list(range(2019, 2026))
STATS = ["receiving_yards", "rushing_yards", "receptions", "targets", "passing_yards"]
EDGES = [0.0, 0.02, 0.05, 0.10, 0.20, 0.35, 0.50, 0.70, 1.01]


def clustered_se(v, clusters):
    v = np.asarray(v, float)
    n = len(v)
    if n < 2:
        return None
    by = defaultdict(float)
    for x, c in zip(v - v.mean(), clusters):
        by[c] += x
    g = len(by)
    if g < 2:
        return None
    return float(np.sqrt(max(sum(t * t for t in by.values()) / (n * n) * (g / (g - 1.0)), 0.0)))


def main():
    df = pl.read_parquet(os.path.join(ROOT, "research/opportunity/opportunity_features.parquet")).to_pandas()
    df = df.sort_values(["player_id", "season", "week"]).reset_index(drop=True)
    role = pdist.has_role_features(df)
    print(f"rows {len(df)}, role features {role}")

    report = {}
    for name in STATS:
        spec = pdist.STAT_SPECS[name]
        fam_name = CHOSEN_FAMILY.get(name, "negbin")
        pm = pdist.population_mask(df, spec.pop)
        P, Y, CL = [], [], []
        for S in EVAL:
            tr = df[pm & (df.season < S) & (df.season >= 2016)]
            te = df[pm & (df.season == S)]
            if len(tr) < 2000 or len(te) < 200:
                continue
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
            gid = te["game_id"].to_numpy()
            for k in spec.thresholds:
                if not (0.02 < float((y_tr >= k).mean()) < 0.98):
                    continue
                idx = int(np.clip(np.searchsorted(grid, k, side="left"), 0, len(grid) - 1))
                P.append(Sv[:, idx]); Y.append((y_te >= k).astype(float)); CL.append(gid)
        if not P:
            continue
        p = np.concatenate(P); y = np.concatenate(Y); cl = np.concatenate(CL)
        rows = []
        b = np.digitize(p, EDGES) - 1
        for i in range(len(EDGES) - 1):
            m = b == i
            if m.sum() < 200:
                continue
            resid = y[m] - p[m]
            rows.append({"lo": EDGES[i], "hi": EDGES[i + 1], "n": int(m.sum()),
                         "games": int(len(set(cl[m]))), "pred": float(p[m].mean()),
                         "obs": float(y[m].mean()), "bias": float(resid.mean()),
                         "se": clustered_se(resid, list(cl[m]))})
        report[name] = rows
        print(f"\n{name} ({fam_name})   predicted vs realised, SEs clustered on game")
        print(f"  {'model p':14s} {'n':>7s} {'games':>6s} {'pred':>7s} {'obs':>7s} {'bias':>9s} {'se':>7s} {'z':>6s}")
        for r in rows:
            z = r["bias"] / r["se"] if r["se"] else float("nan")
            flag = "  <-- overconfident" if z < -2 else ("  <-- underconfident" if z > 2 else "")
            print(f"  [{r['lo']:.2f},{r['hi']:.2f})   {r['n']:7d} {r['games']:6d} {r['pred']:7.4f} "
                  f"{r['obs']:7.4f} {r['bias']:+9.4f} {r['se']:7.4f} {z:6.2f}{flag}")
    json.dump(report, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)

    print("\nPOOLED ACROSS STATISTICS (is the tail systematically too fat?)")
    agg = defaultdict(lambda: {"n": 0, "wpred": 0.0, "wobs": 0.0})
    for name, rows in report.items():
        for r in rows:
            key = f"[{r['lo']:.2f},{r['hi']:.2f})"
            a = agg[key]
            a["n"] += r["n"]; a["wpred"] += r["pred"] * r["n"]; a["wobs"] += r["obs"] * r["n"]
    for k in sorted(agg, key=lambda x: float(x[1:5])):
        a = agg[k]
        print(f"  {k:14s} n={a['n']:8d}  pred {a['wpred']/a['n']:.4f}  obs {a['wobs']/a['n']:.4f}  "
              f"bias {(a['wobs']-a['wpred'])/a['n']:+.4f}")


if __name__ == "__main__":
    main()
