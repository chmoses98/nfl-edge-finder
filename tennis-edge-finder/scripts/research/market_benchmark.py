#!/usr/bin/env python3
"""Bookmaker-benchmark study: link tennis-data.co.uk odds rows to canonical matches, then compare
walk-forward model probabilities with vig-removed closing bookmaker probabilities.

Bookmaker prices are a SEPARATE benchmark from Kalshi closes (docs/CLV_AND_SETTLEMENT.md). tennis-data
odds are the site's recorded pre-match odds (typically close to the final pre-match price, but the site does
not document capture time) -- treated as 'pre-match reference price', not certified closing lines.

Steps
  1. load tennis-data season workbooks for the tour (mirror snapshot), tidy odds, implied probs (proportional + Shin)
  2. link rows to canonical Sackmann matches (identity layer; MATCHED only, ambiguity fails closed)
  3. join walk-forward Elo predictions (research/elo_study/predictions_<tour>.parquet)
  4. score model vs market (Brier/log-loss/calibration), by season/level/surface
  5. hybrid: logit-blend weights fitted on seasons < t, evaluated on season t (walk-forward), including
     a market-only recalibration control
  6. disagreement buckets |model - market| with per-bucket scores and the naive 'ROI at market price'
     of following the model against the vig-free market (hypothetical, no fees, no execution)
Outputs research/market_benchmark/RESULTS_<tour>.md and linked parquet.
"""
from __future__ import annotations
import argparse, glob, json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJ)
from tennis_edge.data.tennis_data import load_tennis_data_file, add_implied_probabilities
from tennis_edge.identity.players import link_tennis_data_names, link_summary
from tennis_edge.eval.metrics import summary, bootstrap_diff, reliability_table
from tennis_edge.data.build import locate


def logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4); return np.log(p / (1 - p))


def fit_blend(y, cols, ridge=1e-3):
    """Logistic regression y ~ sum_j w_j * logit(p_j) + b, by Newton with tiny ridge. Returns (w, b)."""
    X = np.column_stack([logit(c) for c in cols] + [np.ones(len(y))])
    w = np.zeros(X.shape[1]); w[0] = 1.0
    for _ in range(100):
        z = X @ w; q = 1 / (1 + np.exp(-z)); g = X.T @ (q - y) + ridge * w
        H = (X * (q * (1 - q))[:, None]).T @ X + ridge * np.eye(X.shape[1])
        step = np.linalg.solve(H, g); w -= step
        if np.max(np.abs(step)) < 1e-9:
            break
    return w


def apply_blend(w, cols):
    X = np.column_stack([logit(c) for c in cols] + [np.ones(len(cols[0]))])
    return 1 / (1 + np.exp(-(X @ w)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tour", default="ATP")
    ap.add_argument("--out", default=os.path.join(PROJ, "research", "market_benchmark"))
    ap.add_argument("--elo-col", default="p_elo_surface_k_lo")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tour = a.tour
    run = locate("tennis_data_mirrors/gmalbert__tennis-predictions/data_files")
    files = sorted(glob.glob(os.path.join(run, "tennis_data_mirrors/gmalbert__tennis-predictions/data_files", "*.xlsx.gz")))
    td_parts, odds_parts = [], []
    for f in files:
        r = load_tennis_data_file(f, tour)
        td_parts.append(r.matches); odds_parts.append(r.odds)
    td = pd.concat(td_parts, ignore_index=True); odds = pd.concat(odds_parts, ignore_index=True)
    odds = add_implied_probabilities(odds, method="proportional")
    m = pd.read_parquet(os.path.join(PROJ, "data", "processed", "matches.parquet"))
    m = m[(m.tour == tour) & (m.id_system == "sackmann") & (m.season >= td.season.min() - 1)].copy()
    m["tourney_date"] = pd.to_datetime(m["tourney_date"]).dt.date
    links = link_tennis_data_names(td, m)
    ls = link_summary(links)
    print("link summary", ls, flush=True)
    ok = links[links.status == "MATCHED"][["td_key", "match_key", "confidence"]]
    # market probability for the WINNER side (rows are winner-first in tennis-data)
    piv = odds.pivot_table(index="td_key", columns="book", values=["p_winner", "p_loser", "odds_winner", "odds_loser"]) if "p_winner" in odds else None
    if piv is None:
        # add_implied_probabilities naming fallback
        raise SystemExit(f"odds columns: {odds.columns.tolist()}")
    piv.columns = [f"{a_}_{b_}" for a_, b_ in piv.columns]
    piv = piv.reset_index()
    preds = pd.read_parquet(os.path.join(PROJ, "research", "elo_study", f"predictions_{tour}.parquet"))
    df = ok.merge(piv, on="td_key").merge(preds, on="match_key")
    df = df.merge(m[["match_key", "level_canonical", "surface", "season", "tourney_date"]].rename(columns={"level_canonical": "level_m", "surface": "surface_m", "season": "season_m"}), on="match_key")
    # pick benchmark books: Pinnacle (PS) preferred, else Avg
    for b in ("PS", "Avg", "B365", "Max"):
        if f"p_winner_{b}" in df:
            df[f"mkt_{b}"] = df[f"p_winner_{b}"]
    if "mkt_PS" not in df:
        raise SystemExit("no Pinnacle column")
    df = df[df.mkt_PS.notna() & df[a.elo_col].notna()].reset_index(drop=True)
    # symmetric orientation
    rng = np.random.default_rng(0); flip = rng.random(len(df)) < 0.5
    y = (~flip).astype(float)
    def orient(p):
        p = np.asarray(p, float); return np.where(flip, 1 - p, p)
    model = orient(df[a.elo_col]); mkt = orient(df["mkt_PS"]); mkt_avg = orient(df["mkt_Avg"]) if "mkt_Avg" in df else None
    res = {"tour": tour, "n_linked": int(len(df)), "link_summary": ls, "model_col": a.elo_col,
           "scores": {"model": summary(y, model), "market_pinnacle": summary(y, mkt)}}
    if mkt_avg is not None and not np.isnan(mkt_avg).all():
        ok_avg = ~np.isnan(mkt_avg)
        res["scores"]["market_avg"] = summary(y[ok_avg], mkt_avg[ok_avg])
    res["bootstrap_model_minus_market_brier"] = bootstrap_diff(y, model, mkt, n_boot=500)
    # per season / level / surface
    seasons = sorted(df.season_m.unique())
    res["by_season"] = {}
    for s in seasons:
        idx = (df.season_m == s).to_numpy()
        if idx.sum() >= 100:
            res["by_season"][int(s)] = {"n": int(idx.sum()), "model": summary(y[idx], model[idx]), "market": summary(y[idx], mkt[idx])}
    res["by_level"] = {}
    for lv, g in df.groupby("level_m").groups.items():
        idx = np.zeros(len(df), bool); idx[np.asarray(list(g))] = True
        if idx.sum() >= 100:
            res["by_level"][lv] = {"n": int(idx.sum()), "model": summary(y[idx], model[idx]), "market": summary(y[idx], mkt[idx])}
    # walk-forward hybrid: fit on seasons < s, evaluate on s
    hyb = np.full(len(df), np.nan); mkt_recal = np.full(len(df), np.nan); weights = {}
    for s in seasons:
        train = (df.season_m < s).to_numpy(); test = (df.season_m == s).to_numpy()
        if train.sum() < 500 or test.sum() == 0:
            continue
        w = fit_blend(y[train], [mkt[train], model[train]])
        hyb[test] = apply_blend(w, [mkt[test], model[test]])
        w2 = fit_blend(y[train], [mkt[train]])
        mkt_recal[test] = apply_blend(w2, [mkt[test]])
        weights[int(s)] = {"w_market": float(w[0]), "w_model": float(w[1]), "intercept": float(w[2]), "n_train": int(train.sum())}
    okh = ~np.isnan(hyb)
    res["hybrid_walk_forward"] = {"weights_by_season": weights, "n": int(okh.sum()),
                                  "hybrid": summary(y[okh], hyb[okh]), "market": summary(y[okh], mkt[okh]), "model": summary(y[okh], model[okh]),
                                  "market_recalibrated": summary(y[okh], mkt_recal[okh]),
                                  "bootstrap_hybrid_minus_market_brier": bootstrap_diff(y[okh], hyb[okh], mkt[okh], n_boot=500)}
    # disagreement buckets
    d = model - mkt; ad = np.abs(d)
    edges = [0, 0.025, 0.05, 0.10, 0.15, 0.20, 1.01]
    buckets = []
    for lo, hi in zip(edges, edges[1:]):
        idx = (ad >= lo) & (ad < hi)
        if idx.sum() == 0:
            continue
        # follow the model: bet the side the model likes more than the market, at the vig-free market price
        side_y = np.where(d[idx] > 0, y[idx], 1 - y[idx])          # 1 if model-favoured side won
        price = np.where(d[idx] > 0, mkt[idx], 1 - mkt[idx])       # vig-free market prob of that side
        roi = np.mean(side_y / price - 1)                            # unit stake at fair decimal odds 1/price
        buckets.append({"bucket": f"{lo:.3f}-{min(hi, 1):.3f}", "n": int(idx.sum()), "model_brier": float(np.mean((model[idx] - y[idx]) ** 2)),
                        "market_brier": float(np.mean((mkt[idx] - y[idx]) ** 2)), "model_logloss": summary(y[idx], model[idx])["log_loss"],
                        "market_logloss": summary(y[idx], mkt[idx])["log_loss"], "model_side_win_rate": float(side_y.mean()),
                        "model_side_avg_market_prob": float(price.mean()), "hypothetical_roi_vs_vigfree_market": float(roi)})
    res["disagreement_buckets"] = buckets
    res["reliability_model"] = reliability_table(y, model); res["reliability_market"] = reliability_table(y, mkt)
    df.assign(y=y, model=model, market=mkt, hybrid=hyb).to_parquet(os.path.join(a.out, f"linked_{tour}.parquet"), index=False)
    json.dump(res, open(os.path.join(a.out, f"results_{tour}.json"), "w"), indent=1, default=str)
    L = [f"# Model vs bookmaker benchmark ({tour})", "", f"Linked matches with Pinnacle odds: {len(df)} (link summary: {ls}). Orientation randomised.",
         f"Model column: {a.elo_col}. Market = Pinnacle, vig removed proportionally.", "",
         "| forecaster | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |", "|---|---|---|---|---|---|---|---|"]
    for k, v in res["scores"].items():
        L.append(f"| {k} | {v['n']} | {v['brier']:.4f} | {v['log_loss']:.4f} | {v['accuracy']:.4f} | {v['ece']:.4f} | {v['cal_slope']:.3f} | {v['cal_intercept']:.3f} |")
    b = res["bootstrap_model_minus_market_brier"]
    L += ["", f"Paired bootstrap Brier(model) - Brier(market): {b['diff']:+.5f} [{b['ci_low']:+.5f}, {b['ci_high']:+.5f}]", ""]
    h = res["hybrid_walk_forward"]
    L += ["## Walk-forward hybrid (fit on prior seasons only)", "", "| forecaster | n | brier | log_loss | cal_slope |", "|---|---|---|---|---|"]
    for k in ("market", "market_recalibrated", "model", "hybrid"):
        v = h[k]; L.append(f"| {k} | {v['n']} | {v['brier']:.4f} | {v['log_loss']:.4f} | {v['cal_slope']:.3f} |")
    L += ["", "| season | w_market | w_model | intercept | n_train |", "|---|---|---|---|---|"]
    for s, w in weights.items():
        L.append(f"| {s} | {w['w_market']:.3f} | {w['w_model']:.3f} | {w['intercept']:+.3f} | {w['n_train']} |")
    bb = h["bootstrap_hybrid_minus_market_brier"]
    L += ["", f"Hybrid - market Brier: {bb['diff']:+.5f} [{bb['ci_low']:+.5f}, {bb['ci_high']:+.5f}]", "",
          "## Disagreement buckets |model - market|", "", "| bucket | n | model brier | market brier | model LL | market LL | model-side win% | avg mkt prob of model side | hypothetical ROI vs vig-free market |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in buckets:
        L.append(f"| {r['bucket']} | {r['n']} | {r['model_brier']:.4f} | {r['market_brier']:.4f} | {r['model_logloss']:.4f} | {r['market_logloss']:.4f} | {r['model_side_win_rate']:.3f} | {r['model_side_avg_market_prob']:.3f} | {r['hypothetical_roi_vs_vigfree_market']:+.3f} |")
    L += ["", "## By season", "", "| season | n | model LL | market LL |", "|---|---|---|---|"]
    for s, v in res["by_season"].items():
        L.append(f"| {s} | {v['n']} | {v['model']['log_loss']:.4f} | {v['market']['log_loss']:.4f} |")
    L += ["", "## By level", "", "| level | n | model LL | market LL |", "|---|---|---|---|"]
    for s, v in res["by_level"].items():
        L.append(f"| {s} | {v['n']} | {v['model']['log_loss']:.4f} | {v['market']['log_loss']:.4f} |")
    open(os.path.join(a.out, f"RESULTS_{tour}.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
