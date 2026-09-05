#!/usr/bin/env python3
"""Point-in-time residual research: does our football information predict what the market does next?

At each horizon T the market quotes a price. We hold a model probability formed only from information
available before kickoff. Two questions, in the order that matters:

  A. Does the model predict SUBSEQUENT MARKET MOVEMENT (T -> close)?  If the market eventually moves toward
     us, our disagreements are early rather than wrong, and closing-line value is capturable.
  B. Does the model predict the OUTCOME beyond the contemporaneous price at T?  This is the encompassing
     test run at each horizon instead of only at the close.

Both are run in the honest specification (model and price as separate regressors, cluster-robust on game).
The contaminated shared-baseline specification is reported alongside so the difference is visible rather
than asserted -- on an information-free model it manufactures z = +11.8.
"""
import argparse, glob, json, os, sys
from collections import defaultdict

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research.clv import (clustered_se, movement_direction, movement_regression,  # noqa: E402
                                   naive_movement_regression, signed_clv)

OUT = os.path.join(ROOT, "research", "residual_pit"); os.makedirs(OUT, exist_ok=True)
HORIZONS = ["T-168h", "T-72h", "T-48h", "T-24h", "T-12h", "T-6h", "T-3h", "T-90m", "T-30m"]
MAX_WIDTH = 0.10


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def logit(p):
    p = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def irls(X, y, iters=60):
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = sigmoid(X @ b)
        w = np.clip(p * (1 - p), 1e-9, None)
        z = X @ b + (y - p) / w
        XtW = X.T * w
        nb = np.linalg.solve(XtW @ X + 1e-8 * np.eye(X.shape[1]), XtW @ z)
        if np.max(np.abs(nb - b)) < 1e-9:
            return nb
        b = nb
    return b


def cluster_se_logit(X, y, b, clusters):
    p = sigmoid(X @ b)
    w = np.clip(p * (1 - p), 1e-9, None)
    bread = np.linalg.inv((X.T * w) @ X + 1e-9 * np.eye(X.shape[1]))
    u = X * (y - p)[:, None]
    agg = defaultdict(lambda: np.zeros(X.shape[1]))
    for i, c in enumerate(clusters):
        agg[c] += u[i]
    meat = np.zeros((X.shape[1], X.shape[1]))
    for v in agg.values():
        meat += np.outer(v, v)
    g = len(agg)
    return np.sqrt(np.clip(np.diag(bread @ meat @ bread * (g / max(g - 1, 1))), 0, None))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizons", default="/home/user/_md/data/kalshi/backfill/horizons/*.jsonl")
    ap.add_argument("--arm", default="p_base")
    a = ap.parse_args()

    probs = {r["ticker"]: r for r in pl.read_parquet(
        os.path.join(ROOT, "research/model_vs_market/prop_probs_2025_both_arms.parquet")).iter_rows(named=True)}
    rows = []
    for f in glob.glob(a.horizons):
        for line in open(f):
            r = json.loads(line)
            if r.get("anchor_kind") != "kickoff" or r.get("result") not in ("yes", "no"):
                continue
            m = probs.get(r["ticker"])
            if not m:
                continue
            sn = r.get("snaps") or {}
            close = sn.get("T-0")
            if not close or close.get("bid") is None or close.get("ask") is None:
                continue
            cb, ca = close["bid"], close["ask"]
            if not (0 <= cb <= ca <= 1) or (cb <= 0 and ca >= 1) or (ca - cb) > MAX_WIDTH:
                continue
            mid_close = (cb + ca) / 2.0
            for h in HORIZONS:
                s = sn.get(h)
                if not s or s.get("bid") is None or s.get("ask") is None:
                    continue
                b, ask = s["bid"], s["ask"]
                if not (0 <= b <= ask <= 1) or (b <= 0 and ask >= 1) or (ask - b) > MAX_WIDTH:
                    continue
                rows.append({"cluster": r["game_id"], "stat": m["stat"], "horizon": h,
                             "model": m[a.arm], "mid_t": (b + ask) / 2.0, "ask_t": ask, "bid_t": b,
                             "width_t": ask - b, "mid_close": mid_close, "y": m["y"]})
    D = pl.DataFrame(rows)
    print(f"point-in-time observations: {D.height}  games: {D['cluster'].n_unique()}  arm: {a.arm}")

    res = {"arm": a.arm, "n": D.height, "horizons": {}}
    print(f"\nA. DOES THE MODEL PREDICT SUBSEQUENT MARKET MOVEMENT (T -> close)?")
    print(f"   honest:  mid_close - mid_t ~ a + b*model + c*mid_t      (b is the evidence)")
    print(f"   naive:   mid_close - mid_t ~ a + b*(model - mid_t)      (contaminated, shown for contrast)")
    print(f"   {'horizon':9s} {'n':>7s} {'games':>6s} {'b_model':>9s} {'se':>7s} {'z':>7s} "
          f"{'naive b':>9s} {'naive z':>8s} {'toward':>7s} {'unch':>6s}")
    for h in HORIZONS:
        d = D.filter(pl.col("horizon") == h)
        if d.height < 500:
            continue
        model = d["model"].to_numpy(); mt = d["mid_t"].to_numpy(); mc = d["mid_close"].to_numpy()
        cl = d["cluster"].to_list()
        hon = movement_regression(model, mt, mc, cl)
        nai = naive_movement_regression(model, mt, mc, cl)
        lab = movement_direction(mt, mc, model)
        n_move = int((lab == "toward").sum() + (lab == "away").sum())
        toward = float((lab == "toward").sum() / n_move) if n_move else float("nan")
        unch = float((lab == "unchanged").sum() / len(lab))
        res["horizons"][h] = {"n": d.height, "honest": hon, "naive": nai,
                              "share_toward_of_moved": toward, "share_unchanged": unch}
        print(f"   {h:9s} {d.height:7d} {len(set(cl)):6d} {hon['b_model']:+9.4f} {hon['se_model']:7.4f} "
              f"{hon['z_model']:+7.2f} {nai['b_disagreement']:+9.4f} {nai['z']:+8.2f} "
              f"{toward:7.3f} {unch:6.2f}")

    print(f"\nB. DOES THE MODEL BEAT THE CONTEMPORANEOUS PRICE ON THE OUTCOME? (encompassing at each horizon)")
    print(f"   {'horizon':9s} {'n':>7s} {'b_model':>9s} {'se':>7s} {'z':>7s} {'b_market':>9s} {'se':>7s} {'z':>7s}")
    for h in HORIZONS:
        d = D.filter(pl.col("horizon") == h)
        if d.height < 500:
            continue
        y = d["y"].to_numpy()
        X = np.column_stack([np.ones(d.height), logit(d["model"].to_numpy()), logit(d["mid_t"].to_numpy())])
        b = irls(X, y)
        se = cluster_se_logit(X, y, b, d["cluster"].to_list())
        res["horizons"][h]["encompassing"] = {"b_model": float(b[1]), "se_model": float(se[1]),
                                              "b_market": float(b[2]), "se_market": float(se[2])}
        print(f"   {h:9s} {d.height:7d} {b[1]:+9.4f} {se[1]:7.4f} {b[1]/se[1]:+7.2f} "
              f"{b[2]:+9.4f} {se[2]:7.4f} {b[2]/se[2]:+7.2f}")

    print(f"\nC. SIGNED CLV IN PROBABILITY POINTS (movement in our direction, mid basis)")
    print(f"   {'horizon':9s} {'n':>7s} {'clv':>9s} {'se':>7s} {'z':>7s}")
    for h in HORIZONS:
        d = D.filter(pl.col("horizon") == h)
        if d.height < 500:
            continue
        c = signed_clv(d["mid_t"].to_numpy(), d["mid_close"].to_numpy(), d["model"].to_numpy())
        cl = d["cluster"].to_list()
        se = clustered_se(c, cl)
        res["horizons"][h]["signed_clv"] = {"mean": float(c.mean()), "se": se}
        print(f"   {h:9s} {d.height:7d} {c.mean():+9.5f} {se:7.5f} {c.mean()/se:+7.2f}")
    # ---- D. pre-specified disagreement buckets (fixed before looking; never re-cut on results)
    import math
    BUCKETS = [(0.00, 0.02), (0.02, 0.05), (0.05, 0.10), (0.10, 0.15), (0.15, 1.01)]

    def fee(p):
        return math.ceil(0.07 * p * (1 - p) * 100) / 100.0 if 0 < p < 1 else 0.0

    print(f"\nD. CLV AND ECONOMICS BY PRE-SPECIFIED DISAGREEMENT BUCKET  (horizon T-24h)")
    print(f"   {'|model-mid|':12s} {'n':>7s} {'games':>6s} {'width':>7s} {'CLV(mid)':>9s} {'se':>7s} "
          f"{'z':>6s} {'exec net':>9s} {'se':>7s} {'z':>6s}")
    d24 = D.filter(pl.col("horizon") == "T-24h")
    dis = np.abs(d24["model"].to_numpy() - d24["mid_t"].to_numpy())
    bucket_rows = []
    for lo, hi in BUCKETS:
        m = (dis >= lo) & (dis < hi)
        if m.sum() < 200:
            continue
        sub = d24.filter(pl.Series(m))
        cl = sub["cluster"].to_list()
        c = signed_clv(sub["mid_t"].to_numpy(), sub["mid_close"].to_numpy(), sub["model"].to_numpy())
        se = clustered_se(c, cl)
        # executable: take the side the model favours, pay the spread, hold to settlement
        mo = sub["model"].to_numpy(); ask = sub["ask_t"].to_numpy(); bid = sub["bid_t"].to_numpy()
        y = sub["y"].to_numpy()
        rets, rcl = [], []
        for i in range(len(y)):
            if mo[i] > ask[i]:
                rets.append((y[i] - ask[i]) - fee(ask[i])); rcl.append(cl[i])
            elif (1 - mo[i]) > (1 - bid[i]):
                rets.append(((1 - y[i]) - (1 - bid[i])) - fee(1 - bid[i])); rcl.append(cl[i])
        if len(rets) >= 100:
            arr = np.array(rets); rse = clustered_se(arr, rcl)
            ec, ecse, ecz = arr.mean(), rse, arr.mean() / rse if rse else float("nan")
        else:
            ec = ecse = ecz = float("nan")
        print(f"   [{lo:.2f},{hi:.2f})    {int(m.sum()):7d} {len(set(cl)):6d} "
              f"{float(np.median(sub['width_t'].to_numpy())):7.3f} {c.mean():+9.5f} {se:7.5f} "
              f"{c.mean()/se:+6.2f} {ec:+9.4f} {ecse:7.4f} {ecz:+6.2f}")
        bucket_rows.append({"lo": lo, "hi": hi, "n": int(m.sum()), "games": len(set(cl)),
                            "clv": float(c.mean()), "clv_se": se,
                            "exec_net": float(ec), "exec_se": float(ecse), "n_trades": len(rets)})
    res["disagreement_buckets_T24h"] = bucket_rows

    # placebo: the same bucket analysis with a model that cannot know anything about the specific contract.
    # A dose-response driven by mean reversion in mid_t would appear here too; a real one will not.
    print(f"\n   PLACEBO (model probabilities shuffled within statistic -- same marginal, no contract link)")
    rng = np.random.default_rng(0)
    stat_arr = np.array(d24["stat"].to_list()); model_arr = d24["model"].to_numpy()
    placebo_rows = []
    for trial in range(3):
        perm = model_arr.copy()
        for st in set(stat_arr):
            idx = np.where(stat_arr == st)[0]
            perm[idx] = model_arr[rng.permutation(idx)]
        pdis = np.abs(perm - d24["mid_t"].to_numpy())
        line = f"   trial {trial + 1}:  "
        row = []
        for lo, hi in BUCKETS:
            m = (pdis >= lo) & (pdis < hi)
            if m.sum() < 200:
                line += "     --      "; row.append(None); continue
            sub = d24.filter(pl.Series(m))
            c = signed_clv(sub["mid_t"].to_numpy(), sub["mid_close"].to_numpy(), perm[m])
            se = clustered_se(c, sub["cluster"].to_list())
            line += f" {c.mean():+.5f}(z{c.mean()/se:+.1f})"
            row.append({"lo": lo, "hi": hi, "clv": float(c.mean()), "se": se})
        print(line)
        placebo_rows.append(row)
    res["placebo_buckets_T24h"] = placebo_rows

    print(f"\nE. THE ECONOMIC COMPARISON: CLV against the cost of entry")
    d = D.filter(pl.col("horizon") == "T-24h")
    med_width = float(np.median(d["width_t"].to_numpy()))
    clv24 = res["horizons"].get("T-24h", {}).get("signed_clv", {}).get("mean")
    if clv24:
        print(f"   median quoted width at T-24h        {med_width:.4f}")
        print(f"   half-spread paid to enter            {med_width/2:.4f}")
        print(f"   mean signed CLV captured             {clv24:.5f}")
        print(f"   ratio CLV / half-spread              {clv24/(med_width/2):.3f}")
        res["economics_T24h"] = {"median_width": med_width, "half_spread": med_width / 2,
                                 "signed_clv": clv24, "ratio": clv24 / (med_width / 2)}
    json.dump(res, open(os.path.join(OUT, f"results_{a.arm}.json"), "w"), indent=1, default=float)
    D.write_parquet(os.path.join(OUT, f"pit_dataset_{a.arm}.parquet"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
