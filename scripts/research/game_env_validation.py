#!/usr/bin/env python3
"""Validate the market-as-prior joint game environment OOS (2016-2025): are team totals, winning-margin buckets,
both-teams-score and win probabilities calibrated when derived from a joint residual bank centred on the closing line?"""
import json, os, numpy as np, polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
import sys; sys.path.insert(0, ROOT)
from nfl_edge.pricing.game_env import ResidualBank, simulate_game
OUT = os.path.join(ROOT, "research/game_env"); os.makedirs(OUT, exist_ok=True)
g = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).filter((pl.col("game_type") == "REG") & pl.col("result").is_not_null() & pl.col("spread_line").is_not_null() & pl.col("total_line").is_not_null() & (pl.col("season") >= 2006)).to_pandas()
g["mres"] = g["result"] - g["spread_line"]; g["tres"] = g["total"] - g["total_line"]
rows = []
rng = np.random.default_rng(1)
for S in range(2016, 2026):
    tr = g[(g.season < S) & (g.season >= S - 10)]; te = g[g.season == S]
    bank = ResidualBank(tr.mres, tr.tres, tr.season, ref_season=S, spread_lines=tr.spread_line, total_lines=tr.total_line,
                        overtime=tr.overtime.fillna(0).astype(int), results=tr.result, halflife=3.0, rng=rng)
    # correlation check
    for _, r in te.iterrows():
        sim = simulate_game(r.spread_line, r.total_line, bank, n=4000)
        h, a, m = sim["home"], sim["away"], sim["margin"]
        rows.append({"season": S, "game_id": r.game_id, "home_score": r.home_score, "away_score": r.away_score, "result": r.result,
                     "p_home_win": float(np.mean(m > 0)), "p_tie": float(np.mean(m == 0)),
                     **{f"p_home_ge_{k}": float(np.mean(h >= k)) for k in (14, 17, 21, 24, 28, 31, 35)},
                     **{f"p_away_ge_{k}": float(np.mean(a >= k)) for k in (14, 17, 21, 24, 28, 31, 35)},
                     **{f"p_both_ge_{k}": float(np.mean((h >= k) & (a >= k))) for k in (17, 21, 24, 28)},
                     "p_home_1_6": float(np.mean((m >= 1) & (m <= 6))), "p_home_7_14": float(np.mean((m >= 7) & (m <= 14))), "p_home_15p": float(np.mean(m >= 15)),
                     "p_away_1_6": float(np.mean((-m >= 1) & (-m <= 6))), "p_away_7_14": float(np.mean((-m >= 7) & (-m <= 14))), "p_away_15p": float(np.mean(-m >= 15))})
d = pl.DataFrame(rows).to_pandas()
def brier(p, y): return float(np.mean((p - y) ** 2))
res = {"n": int(len(d))}
def rel(p, y, name):
    p = np.asarray(p); y = np.asarray(y, float)
    res[name] = {"pred": float(p.mean()), "obs": float(y.mean()), "brier": brier(p, y), "n": int(len(y))}
rel(d.p_home_win, d.result > 0, "home_win")
rel(d.p_tie, d.result == 0, "tie")
for k in (14, 17, 21, 24, 28, 31, 35):
    rel(d[f"p_home_ge_{k}"], d.home_score >= k, f"home_ge_{k}"); rel(d[f"p_away_ge_{k}"], d.away_score >= k, f"away_ge_{k}")
for k in (17, 21, 24, 28):
    rel(d[f"p_both_ge_{k}"], (d.home_score >= k) & (d.away_score >= k), f"both_ge_{k}")
for nm, cond in (("home_1_6", (d.result >= 1) & (d.result <= 6)), ("home_7_14", (d.result >= 7) & (d.result <= 14)), ("home_15p", d.result >= 15),
                 ("away_1_6", (-d.result >= 1) & (-d.result <= 6)), ("away_7_14", (-d.result >= 7) & (-d.result <= 14)), ("away_15p", -d.result >= 15)):
    rel(d[f"p_{nm}"], cond, nm)
# reliability bins for team totals pooled
p = np.concatenate([d[f"p_home_ge_{k}"] for k in (14, 17, 21, 24, 28, 31, 35)] + [d[f"p_away_ge_{k}"] for k in (14, 17, 21, 24, 28, 31, 35)])
y = np.concatenate([(d.home_score >= k).astype(float) for k in (14, 17, 21, 24, 28, 31, 35)] + [(d.away_score >= k).astype(float) for k in (14, 17, 21, 24, 28, 31, 35)])
bins = np.digitize(p, np.linspace(0, 1, 11)) - 1
res["teamtotal_reliability"] = [{"bin": int(b), "pred": float(p[bins == b].mean()), "obs": float(y[bins == b].mean()), "n": int((bins == b).sum())} for b in range(10) if (bins == b).sum() > 30]
slope = np.polyfit(p, y, 1)
res["teamtotal_reliability_slope_intercept"] = [float(slope[0]), float(slope[1])]
res["corr_margin_total_resid_train"] = float(np.corrcoef(g[g.season < 2016].mres, g[g.season < 2016].tres)[0, 1])
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
for k, v in res.items():
    if isinstance(v, dict): print(f"{k:14s} pred={v['pred']:.3f} obs={v['obs']:.3f} brier={v['brier']:.4f}")
print("teamtotal reliability:", res["teamtotal_reliability"]); print("slope/intercept:", res["teamtotal_reliability_slope_intercept"], "corr(mres,tres)=", res["corr_margin_total_resid_train"])
