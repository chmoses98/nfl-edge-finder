#!/usr/bin/env python3
"""Walk-forward structural serve/return model on tour-level matches (where serve stats exist), scored on the
Pinnacle-linked subset produced by market_benchmark.py, alongside Elo and a simple logit-average ensemble."""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJ)
from tennis_edge.models.serve_return import ServeReturnModel, SRConfig
from tennis_edge.models.elo import match_sort_key
from tennis_edge.sim.analytic import match_win_prob
from tennis_edge.rules.formats import TOUR_SINGLES_BO3, SLAM_MEN_2022, SLAM_WOMEN_2022
from tennis_edge.eval.metrics import summary, bootstrap_diff


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tour", default="ATP"); ap.add_argument("--from-year", type=int, default=2000)
    a = ap.parse_args()
    m = pd.read_parquet(os.path.join(PROJ, "data", "processed", "matches.parquet"))
    m = m[(m.tour == a.tour) & (m.outcome_type != "WALKOVER") & m.tourney_date.notna() & (m.season >= a.from_year) & (m.id_system == "sackmann")
          & m.level_canonical.isin(["GRAND_SLAM", "MASTERS_1000", "TOUR_500_250", "TOUR_FINALS", "OLYMPICS", "TEAM", "CHALLENGER"])].copy()
    m["tourney_date"] = pd.to_datetime(m["tourney_date"]).dt.date
    m = match_sort_key(m)
    res = {}
    for n_prior in (300, 600, 1200):
        sr = ServeReturnModel(SRConfig(n_prior_points=n_prior))
        r = sr.run(m)
        slam = ((m.level_canonical == "GRAND_SLAM") & (m.best_of == 5)).to_numpy()
        p = np.array([match_win_prob(pa, pb, SLAM_MEN_2022 if s else TOUR_SINGLES_BO3) for pa, pb, s in zip(r.pa, r.pb, slam)])
        res[n_prior] = pd.DataFrame({"match_key": r.match_key, f"p_sr_{n_prior}": p, "pts_min": np.minimum(r.pts_w, r.pts_l)})
        print("done", n_prior, flush=True)
    out = res[300]
    for k in (600, 1200):
        out = out.merge(res[k][["match_key", f"p_sr_{k}"]], on="match_key")
    out.to_parquet(os.path.join(PROJ, "research", "market_benchmark", f"sr_predictions_{a.tour}.parquet"), index=False)
    linked = pd.read_parquet(os.path.join(PROJ, "research", "market_benchmark", f"linked_{a.tour}.parquet"))
    df = linked.merge(out, on="match_key")
    flip = df["y"].to_numpy() == 0
    y = df["y"].to_numpy(); mkt = df["market"].to_numpy(); elo = df["model"].to_numpy()
    def orient(p):
        p = np.asarray(p, float); return np.where(flip, 1 - p, p)
    def logit(p):
        p = np.clip(p, 1e-4, 1 - 1e-4); return np.log(p / (1 - p))
    lines = [f"# Structural serve/return study ({a.tour}, Pinnacle-linked subset, n={len(df)})", "", "| forecaster | brier | log_loss | cal_slope | boot Brier diff vs market [95% CI] |", "|---|---|---|---|---|"]
    for name, p in [("market", mkt), ("elo (k_lo surface)", elo)] + [(f"sr_prior{k}", orient(df[f"p_sr_{k}"])) for k in (300, 600, 1200)] + \
                   [(f"avg_logit(elo, sr600)", 1 / (1 + np.exp(-(0.5 * logit(elo) + 0.5 * logit(orient(df["p_sr_600"]))))))]:
        s = summary(y, p); b = bootstrap_diff(y, p, mkt, n_boot=300)
        lines.append(f"| {name} | {s['brier']:.4f} | {s['log_loss']:.4f} | {s['cal_slope']:.3f} | {b['diff']:+.5f} [{b['ci_low']:+.5f}, {b['ci_high']:+.5f}] |")
    # evidence-rich subset
    rich = df["pts_min"].to_numpy() >= 3000
    lines += ["", f"Subset with >= 3000 serve points seen for both players (n={int(rich.sum())}):", "", "| forecaster | brier | log_loss |", "|---|---|---|"]
    for name, p in [("market", mkt), ("elo", elo), ("sr600", orient(df["p_sr_600"]))]:
        s = summary(y[rich], p[rich]); lines.append(f"| {name} | {s['brier']:.4f} | {s['log_loss']:.4f} |")
    open(os.path.join(PROJ, "research", "market_benchmark", f"RESULTS_SR_{a.tour}.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
