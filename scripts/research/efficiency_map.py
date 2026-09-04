#!/usr/bin/env python3
"""2025 Kalshi NFL market-efficiency map: where was the market weak, by family x time-to-kickoff?

Input: the reconstructed executable quote at each horizon for every settled archived market
(data/kalshi/backfill/horizons/*.jsonl, built by scripts/kalshi/backfill_quotes.py).

Everything is measured on EXECUTABLE prices. `ask` is what a YES buyer actually pays; `bid` is what a YES
seller receives (equivalently 1-bid is the NO buyer's cost). The midpoint is reported separately and is only
ever used where the midpoint itself is the object of study -- it is not a tradable price.

Metrics per cell:
  n, n_traded, median quote width, median volume/open interest
  calibration of the MID as a probability: Brier, log loss, reliability slope
  favourite-longshot bias: realised settlement frequency by price bucket
  hypothetical execution: mean (y - ask) for YES and (1-y) - (1-bid) for NO, gross and after the Kalshi
  taker fee ceil(0.07*p*(1-p)*100)/100, which is what an actual taker would have paid
  price movement toward the outcome between horizons

Multiplicity: hundreds of cells are tested. Benjamini-Hochberg FDR at q=0.10 is applied to the per-cell
"is mean execution return != 0" tests, and nothing is called an edge -- these are hypothesis-generating.
"""
import glob, json, math, os, sys
from collections import defaultdict
import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "research", "efficiency_map"); os.makedirs(OUT, exist_ok=True)
IN_GLOB = sys.argv[1] if len(sys.argv) > 1 else "/home/user/_md/data/kalshi/backfill/horizons/*.jsonl"
# Calibration against the midpoint is only meaningful where the midpoint is near a real price. On a book
# quoted 23 bid / 62 ask the midpoint is an arithmetic artefact of where a maker parked an empty quote, and
# "the contract settled above the midpoint" says nothing about the market being wrong. Measured on this
# sample it inverts conclusions: receptions at 0.35-0.50 look UNDERpriced by +0.083 on all books and
# OVERpriced by -0.053 on the 84% of books quoted within 10 cents. Every calibration figure is therefore
# computed on tradable books by default; MAX_WIDTH=1.0 reproduces the contaminated version.
MAX_WIDTH = float(os.environ.get("EFFMAP_MAX_WIDTH", "0.10"))
HORIZONS = ["T-168h", "T-72h", "T-48h", "T-24h", "T-12h", "T-6h", "T-3h", "T-90m", "T-30m", "T-0"]


def taker_fee(p, contracts=1.0):
    """Kalshi taker fee: ceil(0.07 * C * P * (1-P)) to the cent."""
    if p is None or not (0 < p < 1):
        return 0.0
    return math.ceil(0.07 * contracts * p * (1 - p) * 100) / 100.0


def load():
    rows = []
    n_empty_book = 0
    n_no_kickoff = 0
    n_too_wide = 0
    for f in glob.glob(IN_GLOB):
        for line in open(f):
            r = json.loads(line)
            if r.get("result") not in ("yes", "no"):
                continue
            if r.get("anchor_kind") != "kickoff":
                # T-0 is measured relative to the anchor. When the anchor fell back to the market's close
                # time, "T-0" is AFTER the game finished: 65% of those quotes sit at settled certainty and
                # would make the market look clairvoyant. A time-to-kickoff study needs a real kickoff.
                n_no_kickoff += 1
                continue
            y = 1.0 if r["result"] == "yes" else 0.0
            fam = r["family"]; stat = r.get("stat")
            cell_fam = f"{fam}:{stat}" if fam == "PLAYER_STAT" else (f"{fam}:{r.get('period')}" if r.get("period") else fam)
            for h, sn in (r.get("snaps") or {}).items():
                bid, ask = sn.get("bid"), sn.get("ask")
                if bid is None or ask is None:
                    continue
                if not (0.0 <= bid <= ask <= 1.0):
                    continue
                if sn.get("book_empty") or (bid <= 0.0 and ask >= 1.0):
                    n_empty_book += 1      # no market at that instant; not a 100-cent spread
                    continue
                if (ask - bid) > MAX_WIDTH:
                    n_too_wide += 1
                    continue
                rows.append({"ticker": r["ticker"], "cluster": r.get("game_id") or r["ticker"], "family": cell_fam, "base_family": fam, "stat": stat,
                             "horizon": h, "y": y, "bid": bid, "ask": ask, "mid": (bid + ask) / 2.0,
                             "width": ask - bid, "vol": sn.get("vol") or 0.0, "oi": sn.get("oi") or 0.0,
                             "age_min": sn.get("age_min"), "threshold": r.get("threshold"),
                             "anchor_kind": r["anchor_kind"], "season": r.get("season"),
                             "final_volume": r.get("final_volume") or 0.0})
    print(f"quoted snapshots {len(rows)}; empty-book skipped {n_empty_book}; "
          f"wider than {MAX_WIDTH:.2f} skipped {n_too_wide}; "
          f"markets dropped for having no kickoff anchor {n_no_kickoff}")
    return pl.DataFrame(rows)


def clustered_se(values, clusters):
    """SE of a mean when observations share a game.

    Both sides of one game are separate contracts settled by one outcome, and a full player ladder is a dozen
    contracts settled by one performance. Treating those as independent understates the SE by roughly sqrt(k).
    This is the standard cluster-robust SE of the mean, clustered on game.
    """
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
    return float(math.sqrt(max(var, 0.0)))


def cell_metrics(d: pl.DataFrame):
    y = d["y"].to_numpy(); mid = d["mid"].to_numpy(); ask = d["ask"].to_numpy(); bid = d["bid"].to_numpy()
    cl = d["cluster"].to_list()
    n = len(y)
    m = np.clip(mid, 1e-4, 1 - 1e-4)
    yes_ret = y - ask                                     # buy YES at the ask, hold to settlement
    no_ret = (1 - y) - (1 - bid)                          # buy NO (cost 1-bid)
    yes_fee = np.array([taker_fee(a) for a in ask]); no_fee = np.array([taker_fee(1 - b) for b in bid])
    out = {"n": int(n), "n_traded": int((d["vol"].to_numpy() > 0).sum()),
           "median_width": float(np.median(ask - bid)), "median_vol": float(np.median(d["vol"].to_numpy())),
           "median_oi": float(np.median(d["oi"].to_numpy())),
           "mean_mid": float(mid.mean()), "obs_yes": float(y.mean()),
           "brier_mid": float(np.mean((mid - y) ** 2)),
           "logloss_mid": float(-np.mean(y * np.log(m) + (1 - y) * np.log(1 - m))),
           "yes_ret_gross": float(yes_ret.mean()), "yes_ret_net": float((yes_ret - yes_fee).mean()),
           "no_ret_gross": float(no_ret.mean()), "no_ret_net": float((no_ret - no_fee).mean()),
           "yes_ret_se": clustered_se(yes_ret - yes_fee, cl), "no_ret_se": clustered_se(no_ret - no_fee, cl),
           "n_clusters": len(set(cl)),
           "yes_ret_se_naive": float((yes_ret - yes_fee).std(ddof=1) / math.sqrt(n)) if n > 1 else None}
    if n > 5 and mid.std() > 1e-6:
        b = np.polyfit(mid, y, 1)
        out["reliability_slope"] = float(b[0]); out["reliability_intercept"] = float(b[1])
    return out


def bh_fdr(pvals, q=0.10):
    p = np.asarray(pvals, float); order = np.argsort(p); m = len(p)
    thresh = q * (np.arange(1, m + 1)) / m
    passed = p[order] <= thresh
    k = np.max(np.where(passed)[0]) + 1 if passed.any() else 0
    cut = p[order][k - 1] if k else -1
    return p <= cut, cut


def main():
    D = load()
    print("horizon observations:", D.height, "| markets:", D["ticker"].n_unique(), flush=True)
    res = {"n_observations": D.height, "n_markets": int(D["ticker"].n_unique()), "cells": {}, "by_price_bucket": {},
           "movement": {}, "tails": {}}
    fams = [f for f, c in D.group_by("family").len().sort("len", descending=True).iter_rows() if c >= 400]
    tests = []
    for fam in fams:
        for h in HORIZONS:
            d = D.filter((pl.col("family") == fam) & (pl.col("horizon") == h))
            if d.height < 150:
                continue
            m = cell_metrics(d)
            res["cells"][f"{fam}|{h}"] = m
            if m.get("yes_ret_se"):
                tests.append((f"{fam}|{h}|YES", m["yes_ret_net"], m["yes_ret_se"], m["n"]))
                tests.append((f"{fam}|{h}|NO", m["no_ret_net"], m["no_ret_se"], m["n"]))
    # What crossing the spread costs is not a hypothesis -- it is the overround plus the fee, and it is very
    # nearly deterministic (within a game the two sides' losses sum to the overround). Testing it against zero
    # produces astronomically significant "findings" that say only that a market maker charges a spread.
    # It is reported as a cost table. The FDR below is spent on the question that can actually surprise us:
    # conditional on price, does the market settle at the rate it charges?
    tests = []
    edges = [0, .02, .05, .10, .20, .35, .50, .65, .80, .90, .95, .98, 1.0]
    for fam in fams:
        for h in ("T-168h", "T-72h", "T-24h", "T-6h", "T-0"):
            d = D.filter((pl.col("family") == fam) & (pl.col("horizon") == h))
            if d.height < 200:
                continue
            mid = d["mid"].to_numpy(); y = d["y"].to_numpy(); cl = d["cluster"].to_list()
            b = np.digitize(mid, edges) - 1
            for i in range(len(edges) - 1):
                msk = b == i
                if msk.sum() < 60 or len(set(np.array(cl)[msk])) < 20:
                    continue
                resid = y[msk] - mid[msk]
                se = clustered_se(resid, list(np.array(cl)[msk]))
                if not se:
                    continue
                tests.append({"cell": f"{fam}|{h}|[{edges[i]:.2f},{edges[i+1]:.2f})", "bias": float(resid.mean()),
                              "se": se, "n": int(msk.sum()), "g": int(len(set(np.array(cl)[msk])))})
    if tests:
        zs = [abs(t["bias"] / t["se"]) for t in tests]
        pv = [2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))) for z in zs]
        sig, cut = bh_fdr(pv, q=0.10)
        for t, p_ in zip(tests, pv):
            t["p"] = float(p_)
        res["fdr"] = {"question": "conditional on the quoted midpoint, does the contract settle at that rate?",
                      "n_tests": len(tests), "q": 0.10, "p_cutoff": float(cut), "n_significant": int(sig.sum()),
                      "significant": [tests[i] for i in np.where(sig)[0]], "all": tests}
    else:
        res["fdr"] = {"n_tests": 0, "n_significant": 0}
    res["cost_to_cross"] = {k: {"yes_net": v["yes_ret_net"], "no_net": v["no_ret_net"], "median_width": v["median_width"]}
                            for k, v in res["cells"].items()}
    # favourite-longshot bias by price bucket, per base family, at the closing proxy
    for fam in sorted({f.split(":")[0] for f in fams}):
        d = D.filter((pl.col("base_family") == fam) & (pl.col("horizon") == "T-0"))
        if d.height < 300:
            continue
        mid = d["mid"].to_numpy(); y = d["y"].to_numpy(); ask = d["ask"].to_numpy()
        b = np.digitize(mid, edges) - 1
        rows = []
        for i in range(len(edges) - 1):
            msk = b == i
            if msk.sum() < 40:
                continue
            fee = np.array([taker_fee(a) for a in ask[msk]])
            clb = np.array(d["cluster"].to_list())[msk]
            resid = y[msk] - mid[msk]
            rows.append({"lo": edges[i], "hi": edges[i + 1], "n": int(msk.sum()), "games": int(len(set(clb))),
                         "mean_mid": float(mid[msk].mean()), "obs": float(y[msk].mean()),
                         "bias": float(resid.mean()), "bias_se": clustered_se(resid, list(clb)),
                         "yes_ret_net": float(((y[msk] - ask[msk]) - fee).mean())})
        res["by_price_bucket"][fam] = rows
    # movement toward the outcome between horizons (does the price improve as kickoff approaches?)
    piv = {}; piv_cluster = {}
    for r in D.iter_rows(named=True):
        piv.setdefault(r["ticker"], {})[r["horizon"]] = r
        piv_cluster[r["ticker"]] = r["cluster"]
    for a, bh in (("T-72h", "T-0"), ("T-24h", "T-0"), ("T-6h", "T-0"), ("T-24h", "T-6h")):
        rows = [(v[a]["mid"], v[bh]["mid"], v[bh]["y"], v[a]["family"], t) for t, v in piv.items() if a in v and bh in v]
        if len(rows) < 200:
            continue
        m0 = np.array([r[0] for r in rows]); m1 = np.array([r[1] for r in rows]); y = np.array([r[2] for r in rows])
        # Only markets that actually moved can move toward or away from the outcome. np.sign(0) is 0, so
        # including unchanged quotes silently scores every one of them as "moved away" -- with a median
        # quote change of a penny or less, that alone drags the share to ~0.37.
        cl_all = [piv_cluster[r[4]] for r in rows]
        mv = m1 != m0
        toward = (np.sign(m1[mv] - m0[mv]) == np.sign(y[mv] - m0[mv])).astype(float)
        moved_right = float(toward.mean()) if mv.sum() else float("nan")
        cl = [c for c, keep in zip(cl_all, mv) if keep]
        res["movement"][f"{a}->{bh}"] = {"n": len(rows), "n_moved": int(mv.sum()),
                                         "n_clusters": len(set(cl_all)),
                                         "mean_abs_move": float(np.mean(np.abs(m1 - m0))),
                                         "share_unchanged": float(1.0 - mv.mean()),
                                         "share_moved_toward_outcome": moved_right,
                                         "share_se_clustered": clustered_se(toward, cl),
                                         "brier_early": float(np.mean((m0 - y) ** 2)), "brier_late": float(np.mean((m1 - y) ** 2))}
    # tails: extreme rungs of player ladders at the close
    for stat in ("receiving_yards", "rushing_yards", "passing_yards", "receptions", "touchdowns"):
        d = D.filter((pl.col("stat") == stat) & (pl.col("horizon") == "T-0") & pl.col("threshold").is_not_null())
        if d.height < 300:
            continue
        th = d["threshold"].to_numpy(); mid = d["mid"].to_numpy(); y = d["y"].to_numpy(); ask = d["ask"].to_numpy()
        bid_ = d["bid"].to_numpy(); cl_all = np.array(d["cluster"].to_list())
        qs = np.quantile(th, [0.25, 0.5, 0.75])
        rows = []
        for lab, msk in (("low", th <= qs[0]), ("mid", (th > qs[0]) & (th <= qs[2])), ("tail", th > qs[2])):
            if msk.sum() < 50:
                continue
            fee = np.array([taker_fee(x) for x in ask[msk]])
            no_net = ((1 - y[msk]) - (1 - bid_[msk])) - np.array([taker_fee(1 - bb) for bb in bid_[msk]])
            yes_net = (y[msk] - ask[msk]) - fee
            resid = y[msk] - mid[msk]
            rows.append({"bucket": lab, "n": int(msk.sum()), "games": int(len(set(cl_all[msk]))),
                         "mean_mid": float(mid[msk].mean()), "obs": float(y[msk].mean()),
                         "brier": float(np.mean((mid[msk] - y[msk]) ** 2)),
                         "calibration_bias": float(resid.mean()),
                         "calibration_bias_se": clustered_se(resid, list(cl_all[msk])),
                         "yes_ret_net": float(yes_net.mean()),
                         "no_ret_net": float(no_net.mean()),
                         "no_ret_net_se": clustered_se(no_net, list(cl_all[msk]))})
        res["tails"][stat] = rows
    # ---- does efficiency vary with liquidity? (P8 microstructure)
    # Open interest at the close and the market's lifetime volume are both populated on the reconstructed
    # book, so the question is answerable rather than assumed. If thin markets are the mispriced ones, the
    # calibration bias should grow as liquidity falls -- and so should the spread that stops you trading it.
    liq = {}
    D0 = D.filter(pl.col("horizon") == "T-0")
    for name, col in (("open_interest_at_close", "oi"), ("market_lifetime_volume", "final_volume")):
        v = D0[col].to_numpy().astype(float)
        qs = np.quantile(v[v > 0], [0.25, 0.5, 0.75]) if (v > 0).any() else [0, 0, 0]
        buckets = [("zero/none", v <= 0), ("Q1 thinnest", (v > 0) & (v <= qs[0])), ("Q2", (v > qs[0]) & (v <= qs[1])),
                   ("Q3", (v > qs[1]) & (v <= qs[2])), ("Q4 deepest", v > qs[2])]
        mid = D0["mid"].to_numpy(); y = D0["y"].to_numpy(); ask = D0["ask"].to_numpy()
        bid = D0["bid"].to_numpy(); cl = np.array(D0["cluster"].to_list())
        rows = []
        for lab, m in buckets:
            if m.sum() < 60 or len(set(cl[m])) < 15:
                continue
            resid = y[m] - mid[m]
            fee = np.array([taker_fee(x) for x in ask[m]])
            nofee = np.array([taker_fee(1 - x) for x in bid[m]])
            rows.append({"bucket": lab, "n": int(m.sum()), "games": int(len(set(cl[m]))),
                         "median_width": float(np.median(ask[m] - bid[m])),
                         "abs_bias": float(np.abs(resid).mean()), "bias": float(resid.mean()),
                         "bias_se": clustered_se(resid, list(cl[m])),
                         "brier": float(np.mean((mid[m] - y[m]) ** 2)),
                         "yes_net": float(((y[m] - ask[m]) - fee).mean()),
                         "no_net": float((((1 - y[m]) - (1 - bid[m])) - nofee).mean())})
        liq[name] = rows
    res["liquidity"] = liq
    print("\nDOES EFFICIENCY VARY WITH LIQUIDITY? (closing quotes)")
    for name, rows in liq.items():
        print(f"  by {name}")
        print(f"    {'bucket':13s} {'n':>5s} {'g':>4s} {'width':>7s} {'bias':>9s} {'+-':>7s} {'|bias|':>7s} "
              f"{'brier':>7s} {'YESnet':>8s} {'NOnet':>8s}")
        for r in rows:
            print(f"    {r['bucket']:13s} {r['n']:5d} {r['games']:4d} {r['median_width']:7.3f} "
                  f"{r['bias']:+9.4f} {(r['bias_se'] or float('nan')):7.4f} {r['abs_bias']:7.4f} "
                  f"{r['brier']:7.4f} {r['yes_net']:+8.4f} {r['no_net']:+8.4f}")
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)
    # ---- print
    print("\nCALIBRATION AND EXECUTION BY FAMILY x HORIZON (net of the Kalshi taker fee)")
    print(f"{'cell':44s} {'n':>6s} {'g':>5s} {'width':>6s} {'mid':>6s} {'obs':>6s} {'brier':>7s} {'YESnet':>8s} {'NOnet':>8s}")
    for k, v in sorted(res["cells"].items()):
        print(f"{k:44s} {v['n']:6d} {v['n_clusters']:5d} {v['median_width']:6.3f} {v['mean_mid']:6.3f} {v['obs_yes']:6.3f} "
              f"{v['brier_mid']:7.4f} {v['yes_ret_net']:+8.4f} {v['no_ret_net']:+8.4f}")
    print(f"\nCALIBRATION TESTS -- does a contract quoted at p settle at rate p?")
    print(f"  {res['fdr']['n_tests']} tests, game-clustered SEs, Benjamini-Hochberg FDR q=0.10 -> "
          f"{res['fdr']['n_significant']} significant")
    for t in sorted(res["fdr"].get("all", []), key=lambda x: x["p"])[:12]:
        mark = "*" if t in res["fdr"]["significant"] else " "
        print(f"  {mark} {t['cell']:52s} bias {t['bias']:+.4f} +- {t['se']:.4f} (n={t['n']}, games={t['g']}, p={t['p']:.3f})")
    print("\nFAVOURITE-LONGSHOT BIAS AT THE CLOSE")
    for fam, rows in res["by_price_bucket"].items():
        print(f"  {fam}")
        for r in rows:
            bse = r.get("bias_se") or float("nan")
            print(f"    [{r['lo']:.2f},{r['hi']:.2f}) n={r['n']:6d} g={r['games']:3d} mid={r['mean_mid']:.3f} "
                  f"obs={r['obs']:.3f} bias={r['bias']:+.4f}+-{bse:.4f} YESnet={r['yes_ret_net']:+.4f}")
    print("\nPRICE MOVEMENT")
    for k, v in res["movement"].items():
        se = v.get("share_se_clustered")
        print(f"  {k:14s} n={v['n']:6d} g={v['n_clusters']:5d} |move|={v['mean_abs_move']:.4f} "
              f"unchanged={v['share_unchanged']:.2f} moved={v['n_moved']:5d} toward outcome={v['share_moved_toward_outcome']:.3f}"
              f"{f' +-{se:.3f}' if se else ''} brier {v['brier_early']:.4f} -> {v['brier_late']:.4f}")
    print("\nPLAYER LADDER TAILS AT THE CLOSE")
    for stat, rows in res["tails"].items():
        for r in rows:
            se = r.get("no_ret_net_se") or float("nan")
            bse = r.get("calibration_bias_se") or float("nan")
            print(f"  {stat:16s} {r['bucket']:5s} n={r['n']:5d} g={r['games']:3d} mid={r['mean_mid']:.3f} "
                  f"obs={r['obs']:.3f} bias={r['calibration_bias']:+.4f}+-{bse:.4f} "
                  f"YESnet={r['yes_ret_net']:+.4f} NOnet={r['no_ret_net']:+.4f}+-{se:.4f}")


if __name__ == "__main__":
    main()
