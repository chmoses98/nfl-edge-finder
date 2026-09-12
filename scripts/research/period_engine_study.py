#!/usr/bin/env python3
"""Period engine: walk-forward comparison of candidate period distributions (HISTORICAL_RESEARCH).

    python3 scripts/research/period_engine_study.py [--test-seasons 2020-2025] [--n-sims 8000]

Every candidate is centred on the full-game CONSENSUS closing line (the only historical market line this
repository has) and evaluated on the ladders Kalshi actually lists: 1H winner (home / away / tie), 1H spread
rungs, 1H total rungs, 1Q total rungs, 1Q spread rungs. Fitted on seasons strictly before each test season.

Candidates
    NAIVE_SCALE              period line = share x full line (0.5 for halves, 0.25 for quarters); normal residuals
    REG_NORMAL               per-quarter regression centre; independent normal residuals with the training sd
    REG_EMPIRICAL_JOINT      per-quarter regression centre; joint empirical residual 8-vectors, rounded
    LINE_BUCKET_EMPIRICAL    whole historical quarter-score vectors from games in the same (spread, total) bucket
    KERNEL_EMPIRICAL         whole historical vectors resampled with Gaussian line-proximity x recency weights
    KERNEL_EMPIRICAL_SHIFTED kernel resampling + integer shift by the regression centre difference (the default)

Preregistered choice rule: lowest mean Brier over the four liquid ladders (1H winner, 1H spread, 1H total, 1Q total);
ties (< 0.0005) broken by the key-number mass closest to observed.

Metrics: Brier and log loss per ladder, reliability slope, CRPS on the 1H total, key-number mass on the 1H
margin (|m| in {0, 3, 7}) predicted vs observed. Game-clustered standard errors on Brier differences vs the
default. No market quotes: the 2025 archive holds ~200 period contracts over six playoff games, which is too
few for a market comparison and is reported as such.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.engines import period as PE   # noqa: E402

OUT = os.path.join(ROOT, "research", "period_engine")
SPREAD_RUNGS_1H = [k + 0.5 for k in range(-10, 10)]       # P(1H home margin > k)
TOTAL_RUNGS_1H = list(range(14, 35))
TOTAL_RUNGS_1Q = list(range(3, 18))
SPREAD_RUNGS_1Q = [k + 0.5 for k in range(-6, 6)]
SHARE = {"1H": 0.5, "1Q": 0.25}


def _clustered_se(diff, cl):
    diff = np.asarray(diff, float)
    by = defaultdict(float)
    for x, c in zip(diff - diff.mean(), cl):
        by[c] += x
    g = len(by); n = len(diff)
    return float(np.sqrt(sum(v * v for v in by.values()) / (n * n) * (g / max(g - 1, 1)))) if g > 1 else float("nan")


def candidate_sims(kind, bank, train_df, s, t, n, rng):
    if kind == "REG_EMPIRICAL_JOINT":
        return bank.simulate(s, t, n=n, rng=rng, method="residual")
    if kind == "KERNEL_EMPIRICAL":
        return bank.simulate(s, t, n=n, rng=rng, method="kernel")
    if kind == "KERNEL_EMPIRICAL_SHIFTED":
        return bank.simulate(s, t, n=n, rng=rng, method="kernel_shift")
    if kind == "REG_NORMAL":
        mu = bank.center(s, t); sd = bank.resid.std(axis=0)
        Y = np.clip(np.round(mu[None, :] + rng.normal(size=(n, 8)) * sd[None, :]), 0, None)
        return _pack(Y)
    if kind == "NAIVE_SCALE":
        # per-quarter share of the full-game implied team totals; residual sd from the training quarter points
        hi, ai = (t + s) / 2.0, (t - s) / 2.0
        mu = np.array([hi * 0.25] * 4 + [ai * 0.25] * 4)
        sd = train_df[PE.COLS].to_numpy().astype(float).std(axis=0)
        Y = np.clip(np.round(mu[None, :] + rng.normal(size=(n, 8)) * sd[None, :]), 0, None)
        return _pack(Y)
    if kind == "LINE_BUCKET_EMPIRICAL":
        d = train_df
        m = (np.abs(d["spread_line"].to_numpy().astype(float) - s) <= 1.5) & (np.abs(d["total_line"].to_numpy().astype(float) - t) <= 2.5)
        if m.sum() < 40:
            m = (np.abs(d["spread_line"].to_numpy().astype(float) - s) <= 3.0) & (np.abs(d["total_line"].to_numpy().astype(float) - t) <= 5.0)
        if m.sum() < 20:
            m = np.ones(len(d), bool)
        pool = d[PE.COLS].to_numpy().astype(float)[m]
        Y = pool[rng.integers(0, len(pool), size=n)]
        return _pack(Y)
    raise ValueError(kind)


def _pack(Y):
    out = {c: Y[:, j] for j, c in enumerate(PE.COLS)}
    out["home_reg"] = sum(out["hq" + str(i)] for i in range(1, 5)); out["away_reg"] = sum(out["aq" + str(i)] for i in range(1, 5))
    out["home"], out["away"] = out["home_reg"], out["away_reg"]
    out["margin"] = out["home"] - out["away"]; out["total"] = out["home"] + out["away"]
    return out


def ladders_from_sim(sim):
    m1h = sim["hq1"] + sim["hq2"] - sim["aq1"] - sim["aq2"]; t1h = sim["hq1"] + sim["hq2"] + sim["aq1"] + sim["aq2"]
    m1q = sim["hq1"] - sim["aq1"]; t1q = sim["hq1"] + sim["aq1"]
    out = {"1H_home": float(np.mean(m1h > 0)), "1H_away": float(np.mean(m1h < 0)), "1H_tie": float(np.mean(m1h == 0)),
           "1Q_home": float(np.mean(m1q > 0)), "1Q_away": float(np.mean(m1q < 0)), "1Q_tie": float(np.mean(m1q == 0)),
           "key0": float(np.mean(m1h == 0)), "key3": float(np.mean(np.abs(m1h) == 3)), "key7": float(np.mean(np.abs(m1h) == 7))}
    for k in SPREAD_RUNGS_1H:
        out[f"1H_spread_{k}"] = float(np.mean(m1h > k))
    for k in TOTAL_RUNGS_1H:
        out[f"1H_total_{k}"] = float(np.mean(t1h >= k))
    for k in TOTAL_RUNGS_1Q:
        out[f"1Q_total_{k}"] = float(np.mean(t1q >= k))
    for k in SPREAD_RUNGS_1Q:
        out[f"1Q_spread_{k}"] = float(np.mean(m1q > k))
    # CRPS on 1H total via the lattice CDF
    grid = np.arange(0, 80)
    out["_cdf_1h_total"] = np.array([np.mean(t1h <= g) for g in grid])
    return out


def actual_ladders(row):
    m1h = row["hq1"] + row["hq2"] - row["aq1"] - row["aq2"]; t1h = row["hq1"] + row["hq2"] + row["aq1"] + row["aq2"]
    m1q = row["hq1"] - row["aq1"]; t1q = row["hq1"] + row["aq1"]
    out = {"1H_home": float(m1h > 0), "1H_away": float(m1h < 0), "1H_tie": float(m1h == 0),
           "1Q_home": float(m1q > 0), "1Q_away": float(m1q < 0), "1Q_tie": float(m1q == 0),
           "key0": float(m1h == 0), "key3": float(abs(m1h) == 3), "key7": float(abs(m1h) == 7), "_t1h": t1h}
    for k in SPREAD_RUNGS_1H:
        out[f"1H_spread_{k}"] = float(m1h > k)
    for k in TOTAL_RUNGS_1H:
        out[f"1H_total_{k}"] = float(t1h >= k)
    for k in TOTAL_RUNGS_1Q:
        out[f"1Q_total_{k}"] = float(t1q >= k)
    for k in SPREAD_RUNGS_1Q:
        out[f"1Q_spread_{k}"] = float(m1q > k)
    return out


GROUPS = {"1H winner": ["1H_home", "1H_away", "1H_tie"], "1H spread ladder": [f"1H_spread_{k}" for k in SPREAD_RUNGS_1H],
          "1H total ladder": [f"1H_total_{k}" for k in TOTAL_RUNGS_1H], "1Q total ladder": [f"1Q_total_{k}" for k in TOTAL_RUNGS_1Q],
          "1Q spread ladder": [f"1Q_spread_{k}" for k in SPREAD_RUNGS_1Q], "1Q winner": ["1Q_home", "1Q_away", "1Q_tie"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-seasons", default="2020-2025")
    ap.add_argument("--train-from", type=int, default=2012)
    ap.add_argument("--n-sims", type=int, default=8000)
    ap.add_argument("--candidates", default="NAIVE_SCALE,REG_NORMAL,REG_EMPIRICAL_JOINT,LINE_BUCKET_EMPIRICAL,KERNEL_EMPIRICAL,KERNEL_EMPIRICAL_SHIFTED")
    ap.add_argument("--default", default="KERNEL_EMPIRICAL_SHIFTED")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.test_seasons.split("-"))
    table = PE.build_period_table(ROOT, range(a.train_from, hi + 1))
    print(f"period table: {table.height} games {table['season'].min()}-{table['season'].max()}", flush=True)
    cands = a.candidates.split(",")
    preds = {c: [] for c in cands}; acts = []; clusters = []; seasons = []
    crps = {c: [] for c in cands}
    for S in range(lo, hi + 1):
        train = table.filter(pl.col("season") < S); test = table.filter(pl.col("season") == S)
        bank = PE.PeriodBank(train, ref_season=S)
        rng = np.random.default_rng(S)
        for row in test.iter_rows(named=True):
            s, t = float(row["spread_line"]), float(row["total_line"])
            act = actual_ladders(row); acts.append(act); clusters.append(row["game_id"]); seasons.append(S)
            for c in cands:
                sim = candidate_sims(c, bank, train, s, t, a.n_sims, rng)
                lad = ladders_from_sim(sim)
                cdf = lad.pop("_cdf_1h_total")
                crps[c].append(float(np.sum((cdf - (act["_t1h"] <= np.arange(0, 80)).astype(float)) ** 2)))
                preds[c].append(lad)
        print(f"  season {S}: {test.height} test games (train {train.height})", flush=True)
    n = len(acts)
    res = {"n_games": n, "test_seasons": [lo, hi], "n_sims": a.n_sims, "candidates": {}, "paired_vs_default": {}}
    default = a.default
    def brier_rows(c, keys):
        P = np.array([[p[k] for k in keys] for p in preds[c]]); Y = np.array([[y[k] for k in keys] for y in acts])
        return ((P - Y) ** 2).mean(axis=1), P, Y
    for c in cands:
        rc = {"crps_1h_total": float(np.mean(crps[c]))}
        for g, keys in GROUPS.items():
            b, P, Y = brier_rows(c, keys)
            Pc = np.clip(P, 1e-6, 1 - 1e-6)
            ll = float(np.mean(-(Y * np.log(Pc) + (1 - Y) * np.log(1 - Pc))))
            slope = float(np.polyfit(P.ravel(), Y.ravel(), 1)[0]) if P.std() > 1e-9 else float("nan")
            rc[g] = {"brier": float(b.mean()), "log_loss": ll, "reliability_slope": slope, "mean_pred": float(P.mean()), "mean_obs": float(Y.mean())}
        rc["key_numbers_1H_margin"] = {k: {"pred": float(np.mean([p[k] for p in preds[c]])), "obs": float(np.mean([y[k] for y in acts]))} for k in ("key0", "key3", "key7")}
        res["candidates"][c] = rc
    for c in cands:
        if c == default:
            continue
        pv = {}
        for g, keys in GROUPS.items():
            b_c, _, _ = brier_rows(c, keys); b_d, _, _ = brier_rows(default, keys)
            d = b_c - b_d
            pv[g] = {"mean_diff": float(d.mean()), "clustered_se": _clustered_se(d, clusters)}
        res["paired_vs_default"][c] = pv
    # by-season stability of the default
    res["default_by_season"] = {}
    for S in range(lo, hi + 1):
        idx = [i for i, s_ in enumerate(seasons) if s_ == S]
        keys = GROUPS["1H spread ladder"]
        P = np.array([[preds[default][i][k] for k in keys] for i in idx]); Y = np.array([[acts[i][k] for k in keys] for i in idx])
        res["default_by_season"][S] = {"n": len(idx), "1H_spread_brier": float(((P - Y) ** 2).mean())}
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)
    with open(os.path.join(OUT, "RESULTS.md"), "w") as f:
        f.write(render(res, cands, default))
    print(open(os.path.join(OUT, "RESULTS.md")).read())


def render(res, cands, default):
    L = ["# Period engine: walk-forward comparison of period distributions (HISTORICAL_RESEARCH)", "",
         f"`scripts/research/period_engine_study.py`. {res['n_games']} regular-season games, test seasons "
         f"{res['test_seasons'][0]}-{res['test_seasons'][1]}, every candidate fitted on seasons strictly before the test season "
         f"and centred on the consensus closing line; {res['n_sims']} draws per game. HISTORICAL_RESEARCH evidence: used to choose the "
         "shadow engine, never mixed with prospective records.", "",
         "## Ladder Brier (lower is better)", "", "| candidate | " + " | ".join(GROUPS) + " | CRPS 1H total |", "|---|" + "---|" * (len(GROUPS) + 1)]
    for c in cands:
        rc = res["candidates"][c]
        L.append(f"| {c}{' (default)' if c == default else ''} | " + " | ".join(f"{rc[g]['brier']:.5f}" for g in GROUPS) + f" | {rc['crps_1h_total']:.3f} |")
    L += ["", "## Log loss", "", "| candidate | " + " | ".join(GROUPS) + " |", "|---|" + "---|" * len(GROUPS)]
    for c in cands:
        rc = res["candidates"][c]
        L.append(f"| {c} | " + " | ".join(f"{rc[g]['log_loss']:.5f}" for g in GROUPS) + " |")
    L += ["", "## Reliability slope (ideal 1.00) and mean predicted / observed", "", "| candidate | " + " | ".join(GROUPS) + " |", "|---|" + "---|" * len(GROUPS)]
    for c in cands:
        rc = res["candidates"][c]
        L.append(f"| {c} | " + " | ".join(f"{rc[g]['reliability_slope']:.2f} ({rc[g]['mean_pred']:.3f}/{rc[g]['mean_obs']:.3f})" for g in GROUPS) + " |")
    L += ["", "## Key-number mass of the 1H margin (predicted / observed)", "", "| candidate | |m|=0 | |m|=3 | |m|=7 |", "|---|---|---|---|"]
    for c in cands:
        k = res["candidates"][c]["key_numbers_1H_margin"]
        L.append(f"| {c} | {k['key0']['pred']:.3f} / {k['key0']['obs']:.3f} | {k['key3']['pred']:.3f} / {k['key3']['obs']:.3f} | {k['key7']['pred']:.3f} / {k['key7']['obs']:.3f} |")
    L += ["", f"## Paired Brier differences vs {default} (game-clustered SE; positive = {default} better)", "",
          "| candidate | " + " | ".join(GROUPS) + " |", "|---|" + "---|" * len(GROUPS)]
    for c, pv in res["paired_vs_default"].items():
        L.append(f"| {c} | " + " | ".join(f"{pv[g]['mean_diff']:+.5f} ± {pv[g]['clustered_se']:.5f}" for g in GROUPS) + " |")
    L += ["", f"## {default} by test season (1H spread ladder Brier)", "", "| season | games | Brier |", "|---|---|---|"]
    for s, v in res["default_by_season"].items():
        L.append(f"| {s} | {v['n']} | {v['1H_spread_brier']:.5f} |")
    L += ["", "## Market comparison", "",
          "Not possible historically: the 2025 Kalshi archive holds 203 first-half / first-quarter contracts over six playoff games "
          "(68 1H spread, 63 1H total, 24 1Q spread, 21 1H winner, 18 1Q total, 9 1Q winner). The prospective record is the only "
          "way to learn whether this engine adds information to Kalshi's period quotes, which is why it is shadow-only.", "",
          "## What this establishes and does not", "",
          "* The regression centres are the point: the naive division baseline mis-centres every period ladder (1Q total is 19% of the "
          "full line, 1H margin 56% of the spread).",
          "* Ladders within one period are coherent by construction (one simulation); the choice among candidates is a shape question "
          "(key-number mass, tails), which the Brier alone is nearly blind to -- read the key-number and reliability rows.",
          "* Nothing here is a betting result. The engine is SHADOW: it writes projections and accumulates prospective evidence."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
