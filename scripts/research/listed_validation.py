#!/usr/bin/env python3
"""H-20260904-022: validate the opportunity/role features on the population that is actually traded.

The prior programme validated role features on a fixed synthetic ladder across every skill-position player.
Kalshi lists a narrow subset -- established starters -- and places rungs near the money. Session 3 found the
gain does not transfer. This is the decisive version, on the exact contracts Kalshi listed in 2025, with the
decision rule applied: if the features do not reliably improve the traded population, they are RETIRED from
the shadow pricer rather than kept because they improve generic prediction.

Population is defined before scoring: every settled 2025 Kalshi player-prop rung with a model probability
under all arms. Identical observations for every arm; clustering on game.
"""
import argparse, json, math, os, sys
from collections import defaultdict

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research.clv import clustered_se  # noqa: E402

OUT = os.path.join(ROOT, "research", "listed_validation"); os.makedirs(OUT, exist_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizons", default="/home/user/_md/data/kalshi/backfill/horizons/*.jsonl")
    a = ap.parse_args()
    P = pl.read_parquet(os.path.join(ROOT, "research/model_vs_market/prop_probs_2025_both_arms.parquet"))
    arms = [c for c in P.columns if c.startswith("p_")]
    print(f"arms available: {arms}")

    # attach the game id so clustering is on game, not on contract
    import glob
    gid = {}
    for f in glob.glob(a.horizons):
        for line in open(f):
            r = json.loads(line)
            if r.get("game_id"):
                gid[r["ticker"]] = r["game_id"]
    P = P.with_columns(pl.col("ticker").replace_strict(gid, default=None).alias("game_id"))
    P = P.filter(pl.col("game_id").is_not_null())
    print(f"settled 2025 Kalshi rungs with a game id and all arms: {P.height}, "
          f"games {P['game_id'].n_unique()}")

    y = P["y"].to_numpy()
    cl = P["game_id"].to_list()

    def brier(p):
        return (np.clip(p, 1e-6, 1 - 1e-6) - y) ** 2

    def logloss(p):
        p = np.clip(p, 1e-6, 1 - 1e-6)
        return -(y * np.log(p) + (1 - y) * np.log(1 - p))

    base = P["p_base"].to_numpy()
    print(f"\n{'arm':12s} {'Brier':>9s} {'LogLoss':>9s} {'vs base (Brier)':>17s} {'se':>8s} {'z':>7s}")
    res = {"n": P.height, "games": P["game_id"].n_unique(), "arms": {}}
    for arm in arms:
        p = P[arm].to_numpy()
        b, l = brier(p).mean(), logloss(p).mean()
        d = brier(p) - brier(base)
        se = clustered_se(d, cl) if arm != "p_base" else None
        z = (d.mean() / se) if se else float("nan")
        res["arms"][arm] = {"brier": float(b), "logloss": float(l),
                            "delta_vs_base": float(d.mean()), "se": se, "z": float(z)}
        print(f"{arm:12s} {b:9.5f} {l:9.5f} {d.mean():+17.5f} {(se or float('nan')):8.5f} {z:+7.2f}")

    print(f"\nBY STATISTIC: role minus base Brier (negative = role better), clustered on game")
    print(f"  {'stat':18s} {'n':>7s} {'games':>6s} {'base':>9s} {'role':>9s} {'delta':>10s} {'se':>8s} {'z':>7s}")
    bystat = {}
    for stat in sorted(set(P["stat"].to_list())):
        s = P.filter(pl.col("stat") == stat)
        if s.height < 200:
            continue
        ys = s["y"].to_numpy(); c2 = s["game_id"].to_list()
        bb = (np.clip(s["p_base"].to_numpy(), 1e-6, 1 - 1e-6) - ys) ** 2
        rr = (np.clip(s["p_role"].to_numpy(), 1e-6, 1 - 1e-6) - ys) ** 2
        d = rr - bb
        se = clustered_se(d, c2)
        bystat[stat] = {"n": s.height, "base": float(bb.mean()), "role": float(rr.mean()),
                        "delta": float(d.mean()), "se": se}
        print(f"  {stat:18s} {s.height:7d} {len(set(c2)):6d} {bb.mean():9.5f} {rr.mean():9.5f} "
              f"{d.mean():+10.5f} {se:8.5f} {(d.mean()/se if se else float('nan')):+7.2f}")
    res["by_stat"] = bystat

    # the decision
    role = res["arms"].get("p_role", {})
    improves = role.get("delta_vs_base", 0) < 0 and abs(role.get("z", 0)) > 2
    n_stat_better = sum(1 for v in bystat.values() if v["delta"] < 0 and v["se"] and abs(v["delta"]/v["se"]) > 2)
    print(f"\nDECISION RULE (H-20260904-022)")
    print(f"  role features improve the traded population overall at |z|>2 : {improves}")
    print(f"  statistics where role improves at |z|>2                      : {n_stat_better}/{len(bystat)}")
    verdict = ("KEEP" if improves else
               (f"KEEP ONLY FOR {n_stat_better} PREREGISTERED FAMILIES" if n_stat_better else "RETIRE"))
    print(f"  VERDICT: {verdict}")
    res["decision"] = {"improves_overall": bool(improves), "n_stats_improved": n_stat_better,
                       "verdict": verdict}
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
