#!/usr/bin/env python3
"""Where does the model's distribution differ from the market's OWN implied distribution?

For every player ladder with at least three quoted rungs, Kalshi's prices define a discrete survival
function P(Y >= k) directly (after enforcing monotonicity). Comparing that shape with the model's on the same
rungs separates two very different claims:

  * "the model disagrees about the centre"  -- it projects a different mean,
  * "the model disagrees about the shape"   -- same centre, different tail thickness.

The second is the one worth knowing about, because a systematic tail disagreement across many independent
ladders points at the distribution family rather than at any single player.

Only ladders whose median quoted width is under 10 cents are used. Above that the implied survival is an
artefact of an empty book, not a market view (research/shadow/RESULTS.md).
"""
import glob, gzip, json, os, sys
from collections import defaultdict

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "research", "market_shape"); os.makedirs(OUT, exist_ok=True)
MAX_WIDTH = 0.10


def clustered_se(values, clusters):
    v = np.asarray(values, float)
    n = len(v)
    if n < 2:
        return None
    mu = v.mean()
    by = defaultdict(float)
    for x, c in zip(v - mu, clusters):
        by[c] += x
    g = len(by)
    if g < 2:
        return None
    var = sum(t * t for t in by.values()) / (n * n) * (g / (g - 1.0))
    return float(np.sqrt(max(var, 0.0)))


def main():
    mi_files = sorted(glob.glob(os.path.join(ROOT, "data/shadow/ledger", "*", "*.market_implied.json.gz")))
    ob_files = sorted(glob.glob(os.path.join(ROOT, "data/shadow/ledger", "*", "*.observations.jsonl.gz")))
    if not mi_files or not ob_files:
        print("need a ledger snapshot"); return 1
    mi = json.load(gzip.open(mi_files[-1], "rt"))
    obs = [json.loads(l) for l in gzip.open(ob_files[-1], "rt")]
    print(f"market-implied ladders {len(mi)}; observations {len(obs)}")

    # model P(Y>=k) per (ladder key, k) from the supported observations
    model = defaultdict(dict)
    meta = {}
    for r in obs:
        if r.get("support_state") != "SUPPORTED" or r.get("family") != "PLAYER_STAT":
            continue
        k = r.get("threshold")
        if k is None or r.get("model_event_probability") is None:
            continue
        key = r.get("ladder_key") or f"{r.get('player_kalshi_id')}|{r.get('stat')}|{r.get('game_id')}"
        model[key][float(k)] = r["model_event_probability"]
        meta[key] = {"stat": r.get("stat"), "player": r.get("player_name")}

    matched = 0
    rows = []
    for key, lad in mi.items():
        if lad.get("median_width") is None or lad["median_width"] > MAX_WIDTH:
            continue
        mm = model.get(key)
        if not mm:
            # ledger and market-implied may key differently; try a suffix match
            cand = [k2 for k2 in model if key in k2 or k2 in key]
            mm = model[cand[0]] if len(cand) == 1 else None
            if mm:
                key = cand[0]
        if not mm or len(lad["k"]) < 3:
            continue
        ks = [float(x) for x in lad["k"]]
        pm = [float(x) for x in lad["p_monotone"]]
        pairs = [(k, p, mm[k]) for k, p in zip(ks, pm) if k in mm]
        if len(pairs) < 3:
            continue
        matched += 1
        ks_ = np.array([p[0] for p in pairs]); mk = np.array([p[1] for p in pairs]); md = np.array([p[2] for p in pairs])
        # centre: implied mean lower bound = sum of P(Y>=k) over the listed integer rungs
        rows.append({"key": key, "stat": meta.get(key, {}).get("stat"), "n": len(pairs),
                     "width": lad["median_width"],
                     "mkt_mass": float(mk.sum()), "mdl_mass": float(md.sum()),
                     "rung_rank": [float(x) for x in (ks_ - ks_.min()) / max(ks_.max() - ks_.min(), 1e-9)],
                     "diff": [float(x) for x in (md - mk)]})
    print(f"ladders matched with >=3 shared rungs and width <= {MAX_WIDTH}: {matched}")
    if not rows:
        print("no comparable ladders in this snapshot"); return 0

    # centre disagreement vs shape disagreement
    dm = np.array([r["mdl_mass"] - r["mkt_mass"] for r in rows])
    print(f"\nCENTRE: model minus market summed survival (a proxy for the projected mean over listed rungs)")
    print(f"  mean {dm.mean():+.4f}  median {np.median(dm):+.4f}  sd {dm.std(ddof=1):.4f}  n={len(dm)}")

    # shape: after removing each ladder's own mean difference, how does the residual vary along the ladder?
    lo, mid, hi = [], [], []
    lo_c, mid_c, hi_c = [], [], []
    for i, r in enumerate(rows):
        d = np.array(r["diff"]); rr = np.array(r["rung_rank"])
        d = d - d.mean()                      # remove this ladder's own centre disagreement
        for bucket, cl, m in ((lo, lo_c, rr <= 0.34), (mid, mid_c, (rr > 0.34) & (rr < 0.67)),
                              (hi, hi_c, rr >= 0.67)):
            bucket.extend(d[m]); cl.extend([i] * int(m.sum()))
    print(f"\nSHAPE: centre removed, model minus market by position on the ladder")
    print("  (standard errors clustered on ladder -- rungs of one player's ladder are one observation)")
    for lab, v, cl in (("low rungs (likely)", lo, lo_c), ("middle rungs", mid, mid_c),
                       ("high rungs (tail)", hi, hi_c)):
        v = np.array(v)
        se = clustered_se(v, cl)
        naive = v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else float("nan")
        z = abs(v.mean() / se) if se else float("nan")
        print(f"  {lab:20s} n={len(v):5d} ladders={len(set(cl)):3d}  mean {v.mean():+.4f} "
              f"+- {se:.4f} (naive {naive:.4f}, z={z:.2f})")
    tail = np.array(hi)
    print("\n  A positive tail number means the model puts MORE probability in the upper tail than the market.")

    by = defaultdict(list)
    for r in rows:
        by[r["stat"]].append(r["mdl_mass"] - r["mkt_mass"])
    print("\nCENTRE DISAGREEMENT BY STATISTIC")
    for k, v in sorted(by.items(), key=lambda x: -len(x[1])):
        a = np.array(v)
        print(f"  {k:18s} n={len(a):4d} mean {a.mean():+.4f} +- {a.std(ddof=1)/max(np.sqrt(len(a)),1):.4f}")
    json.dump({"n_ladders": matched, "centre_mean": float(dm.mean()),
               "shape": {"low": float(np.mean(lo)), "mid": float(np.mean(mid)), "tail": float(np.mean(hi))},
               "by_stat": {k: float(np.mean(v)) for k, v in by.items()}},
              open(os.path.join(OUT, "results.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
