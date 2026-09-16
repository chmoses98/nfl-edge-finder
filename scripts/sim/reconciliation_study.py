#!/usr/bin/env python3
"""Market reconciliation research on the 2025 Kalshi archive.

Joins the walk-forward simulation distributions of 2025 (fitted on <= 2024) to the settled 2025 rungs and
their archived quotes, then, per statistic family:
  * fits the reconciliation weight on weeks 1-9 and confirms it on weeks 10-22 (paired against the market,
    game-clustered), at T-0 and at T-24h;
  * reports the encompassing regression, the Brier curve over the weight grid, and the disagreement bands;
  * fits the weight the 2026 season will USE on all of 2025 (no 2026 outcome enters).

Writes research/simulation_engine/reconciliation_2025.json, reconciliation_weights.json and
RECONCILIATION.md.
"""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import backtest as B, kalshi_history as K, reconcile as R
from nfl_edge.engines.player.dist import LatticeDistribution

OUT = B.OUT


def load_dists(season: int) -> dict:
    P = pd.read_parquet(os.path.join(OUT, f"player_dists_{season}.parquet"))
    d = {}
    for r in P.itertuples():
        pmf = np.asarray(r.pmf, float)
        if pmf.sum() <= 0:
            continue
        d[(r.game_id, r.player_id, r.stat)] = LatticeDistribution(pmf / pmf.sum(), meta={"mean": r.mean})
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default="/home/user/_market_data_wt")
    ap.add_argument("--fit-weeks", default="1-9")
    ap.add_argument("--horizons", default="T-0,T-24h")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.fit_weeks.split("-"))
    rungs = K.load_rungs(a.market_data, 2025)
    dists = load_dists(2025)
    results = {"n_rungs_archive": int(len(rungs)), "n_dists": len(dists), "horizons": {}}
    final_weights = None
    for h in a.horizons.split(","):
        market = K.market_ladders(rungs, h)
        rows = rungs.copy()
        b, aa = f"bid_{h}", f"ask_{h}"
        rows = rows[rows[b].notna() & rows[aa].notna() & ((rows[aa] - rows[b]) <= 0.10)]
        rows["market_mono"] = [next((x["mid_monotone"] for x in (market.get((r.game_id, r.player_id, r.stat)) or {}).get("rungs", [])
                                     if abs(x["k"] - r.k) < 1e-9), (getattr(r, b) + getattr(r, aa)) / 2) for r in rows.itertuples()]
        scored = R.score_weights(rows, dists, market)
        fit = scored[(scored["week"] >= lo) & (scored["week"] <= hi)]
        conf = scored[scored["week"] > hi]
        fitted = R.fit_weights(fit)
        confirmed = R.confirm(conf, fitted)
        enc = R.encompassing(scored)
        allfit = R.fit_weights(scored)
        results["horizons"][h] = {"n_scored": int(len(scored)), "games": int(scored["game_id"].nunique()),
                                  "fit_weeks": [lo, hi], "fitted_on_fit_weeks": fitted, "confirmed_on_later_weeks": confirmed,
                                  "encompassing_all": enc, "fitted_on_all_2025": allfit,
                                  "by_stat_all": {st: {"n": int(len(g)), "brier_football": float(np.mean((g.p_football - g.y) ** 2)),
                                                       "brier_market_mono": float(np.mean((g.market_mono - g.y) ** 2)),
                                                       "mean_football": float(g.p_football.mean()), "mean_market": float(g.market_mono.mean()),
                                                       "rate": float(g.y.mean())} for st, g in scored.groupby("stat")}}
        scored.to_parquet(os.path.join(OUT, f"reconciliation_scored_2025_{h}.parquet"))
        if h == "T-0":
            final_weights = allfit
        print(h, json.dumps({k: {"w": v["weight"], "n": v["n"], "mkt": round(v["brier_market_mono"], 5), "fb": round(v["brier_football"], 5)}
                             for k, v in fitted.items()}, indent=0))
        print(h, "confirm", json.dumps({k: {kk: (round(vv, 5) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in confirmed.items()}, indent=0))
    json.dump(results, open(os.path.join(OUT, "reconciliation_2025.json"), "w"), indent=1)
    R.save_weights(os.path.join(OUT, "reconciliation_weights.json"), final_weights or {}, results["horizons"].get("T-0", {}).get("confirmed_on_later_weeks", {}),
                   {"fitted_on": "2025 weeks 1-22 at T-0 (closing quotes); the 2026 season is the first period these weights are evaluated on",
                    "confirmation": "weights fitted on weeks 1-9 and confirmed on weeks 10-22 are in reconciliation_2025.json",
                    "sim_version": "sim-1.0.0"})
    print("wrote", os.path.join(OUT, "reconciliation_weights.json"))


if __name__ == "__main__":
    main()
