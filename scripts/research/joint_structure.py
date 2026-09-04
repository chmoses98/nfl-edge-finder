#!/usr/bin/env python3
"""Does the market's per-contract pricing imply a joint distribution that matches reality?

Kalshi prices each contract on its own. Outcomes inside one game are not independent: when a quarterback has
a big day his receivers do too, and a blowout suppresses the losing team's rushing and inflates its passing.
If the exchange's marginals are right (they are -- research/model_vs_market) but the implied JOINT structure
is wrong, that is the one place a model could hold information a market of single-contract quotes does not,
because no single quote has to encode a correlation.

Method: for every pair of settled player-prop contracts on DIFFERENT players in the same game, compare the
realised joint rate P(both YES) with the product of the two closing midpoints. Under independence those
match. Pairs are grouped by whether the two players share a team. Standard errors are clustered on game --
one game contributes many pairs and they are anything but independent of each other.

Only tradable books (quoted within 10 cents) are used, for the reasons in research/efficiency_map.
"""
import glob, json, math, os, sys
from collections import defaultdict
from itertools import combinations

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "research", "joint_structure"); os.makedirs(OUT, exist_ok=True)
HORIZONS = sys.argv[1] if len(sys.argv) > 1 else "/home/user/_md/data/kalshi/backfill/horizons/*.jsonl"
MAX_WIDTH = 0.10
MAX_PAIRS_PER_GAME = 4000


def cse(v, cl):
    v = np.asarray(v, float); n = len(v)
    if n < 2:
        return None
    by = defaultdict(float)
    for x, c in zip(v - v.mean(), cl):
        by[c] += x
    g = len(by)
    return float(np.sqrt(max(sum(t * t for t in by.values()) / (n * n) * (g / (g - 1.0)), 0.0))) if g > 1 else None


def main():
    bygame = defaultdict(list)
    for f in glob.glob(HORIZONS):
        for line in open(f):
            r = json.loads(line)
            if r.get("anchor_kind") != "kickoff" or r.get("result") not in ("yes", "no"):
                continue
            if r.get("family") != "PLAYER_STAT" or not r.get("player_kalshi_id") or not r.get("game_id"):
                continue
            s = (r.get("snaps") or {}).get("T-0")
            if not s or s.get("bid") is None or s.get("ask") is None:
                continue
            b, a = s["bid"], s["ask"]
            if not (0 <= b <= a <= 1) or (b <= 0 and a >= 1) or (a - b) > MAX_WIDTH:
                continue
            mid = (a + b) / 2.0
            if not (0.05 < mid < 0.95):        # near-certain legs carry no information about dependence
                continue
            bygame[r["game_id"]].append({"pid": r["player_kalshi_id"], "team": r.get("team"),
                                         "stat": r.get("stat"), "mid": mid,
                                         "y": 1.0 if r["result"] == "yes" else 0.0})
    print(f"games with usable contracts: {len(bygame)}")

    # The marginals are already known to be overpriced on the YES side by 1.5-4.9 points
    # (research/efficiency_map). Comparing a realised JOINT rate to a product of overpriced marginals
    # measures that marginal bias twice over and reports it as negative dependence. Each leg is therefore
    # debiased first, using a calibration map estimated from these same contracts' own settlement rates by
    # price bucket -- so what is left is dependence beyond what the true marginals imply.
    EDGES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    allc = [c for cs in bygame.values() for c in cs]
    mids = np.array([c["mid"] for c in allc]); ys = np.array([c["y"] for c in allc])
    b = np.clip(np.digitize(mids, EDGES) - 1, 0, len(EDGES) - 2)
    cal = {}
    for i in range(len(EDGES) - 1):
        m = b == i
        if m.sum() >= 100:
            cal[i] = float(ys[m].mean())
    print("  leg calibration (quoted midpoint bucket -> realised rate):")
    for i in sorted(cal):
        m = b == i
        print(f"    [{EDGES[i]:.2f},{EDGES[i+1]:.2f})  n={int(m.sum()):6d}  mid {mids[m].mean():.4f} "
              f"-> realised {cal[i]:.4f}")
    for cs in bygame.values():
        for c in cs:
            k = int(np.clip(np.digitize(c["mid"], EDGES) - 1, 0, len(EDGES) - 2))
            c["p_cal"] = cal.get(k, c["mid"])

    groups = {"same team": [], "opposing teams": []}
    clusters = {"same team": [], "opposing teams": []}
    npairs = 0
    for gid, cs in bygame.items():
        if len(cs) < 2:
            continue
        pairs = list(combinations(range(len(cs)), 2))
        if len(pairs) > MAX_PAIRS_PER_GAME:
            idx = np.random.default_rng(0).choice(len(pairs), MAX_PAIRS_PER_GAME, replace=False)
            pairs = [pairs[i] for i in idx]
        for i, j in pairs:
            x, y = cs[i], cs[j]
            if x["pid"] == y["pid"]:
                continue                      # same player's own ladder is mechanically dependent
            key = "same team" if (x["team"] and x["team"] == y["team"]) else "opposing teams"
            groups[key].append((x["p_cal"] * y["p_cal"], x["y"] * y["y"]))
            clusters[key].append(gid)
            npairs += 1
    print(f"cross-player pairs within a game: {npairs}")

    res = {}
    print(f"\n{'pair type':16s} {'pairs':>8s} {'games':>6s} {'implied':>9s} {'realised':>9s} {'excess':>9s} "
          f"{'se':>8s} {'z':>6s}")
    for key in ("same team", "opposing teams"):
        v = groups[key]
        if len(v) < 500:
            continue
        imp = np.array([a for a, _ in v]); real = np.array([b for _, b in v])
        d = real - imp
        se = cse(d, clusters[key]); z = d.mean() / se if se else float("nan")
        mark = "  <-- dependence not priced" if abs(z) > 2 else ""
        print(f"{key:16s} {len(v):8d} {len(set(clusters[key])):6d} {imp.mean():9.4f} {real.mean():9.4f} "
              f"{d.mean():+9.4f} {se:8.4f} {z:6.2f}{mark}")
        res[key] = {"pairs": len(v), "games": len(set(clusters[key])), "implied": float(imp.mean()),
                    "realised": float(real.mean()), "excess": float(d.mean()), "se": se, "z": float(z)}
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)
    print("\nLegs are debiased to their own realised rate first, so a non-zero excess is dependence the")
    print("market's per-contract pricing does not capture -- not the marginal bias measured elsewhere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
