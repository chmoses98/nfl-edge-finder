#!/usr/bin/env python3
"""Milestone E: walk-forward game-model research vs the closing line.

Questions answered (all out-of-sample, chronological):
  Q1 How well does a football-only model (opponent-adjusted EPA ratings + context)
     predict margin/total vs the closing spread/total?
  Q2 Does a market-aware residual model (closing line + football features) beat the
     closing line at all?  If not, the football features carry no info the close lacks.
  Q3 What blend weight between model and market minimizes OOS error (a proxy for
     "how much should we trust ourselves")?
Outputs research/game_model/results.json and RESULTS.md.
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np, polars as pl
from scipy.stats import norm
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research.team_ratings import prepare_rows, snapshot_ratings  # noqa

OUT = os.path.join(ROOT, "research", "game_model")
os.makedirs(OUT, exist_ok=True)

tg = pl.read_parquet(os.path.join(ROOT, "data/silver/team_game.parquet"))
games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet"))
rows = prepare_rows(tg.filter(pl.col("season_type") == "REG"))
FEATS = ["epa", "sr", "db_epa", "rush_epa", "epa_ng", "explosive", "sack_rate", "to_rate", "proe", "st_epa", "ed_epa"]

# ---------------------------------------------------------------- ratings per snapshot
t0 = time.time()
snaps = []
for season in range(2009, 2026):
    for week in range(1, 19 if season >= 2021 else 18):
        r = snapshot_ratings(rows, season, week, halflife_games=10.0, season_carry=0.4, ridge=4.0)
        if r.height:
            snaps.append(r)
ratings = pl.concat(snaps, how="diagonal_relaxed")
ratings.write_parquet(os.path.join(OUT, "ratings_snapshots.parquet"))
print("ratings snapshots", ratings.shape, f"{time.time()-t0:.0f}s", flush=True)

# ---------------------------------------------------------------- game feature table
g = games.filter((pl.col("game_type") == "REG") & (pl.col("season") >= 2010) & (pl.col("season") <= 2025) & pl.col("result").is_not_null())
home = ratings.rename({c: f"h_{c}" for c in ratings.columns if c not in ("season", "week")}).rename({"h_team": "home_team"})
away = ratings.rename({c: f"a_{c}" for c in ratings.columns if c not in ("season", "week")}).rename({"a_team": "away_team"})
d = g.join(home, on=["season", "week", "home_team"], how="left").join(away, on=["season", "week", "away_team"], how="left")
d = d.with_columns([
    (pl.col("home_rest") - pl.col("away_rest")).alias("rest_diff"),
    pl.col("div_game").cast(pl.Float64),
    (pl.col("roof").is_in(["dome", "closed"])).cast(pl.Float64).alias("indoor"),
    (pl.col("location") == "Neutral").cast(pl.Float64).alias("neutral"),
])
feat_cols = []
for f in FEATS:
    d = d.with_columns([(pl.col(f"h_off_{f}") - pl.col(f"a_def_{f}") * (-1)).alias(f"x_h_{f}"),  # placeholder, replaced below
                        ])
# matchup features: home offense vs away defense, away offense vs home defense
# def rating is "value allowed relative to mean" (positive = allows more), so matchup = off + def_opp
X_exprs = []
for f in FEATS:
    X_exprs.append((pl.col(f"h_off_{f}") + pl.col(f"a_def_{f}")).alias(f"m_h_{f}"))
    X_exprs.append((pl.col(f"a_off_{f}") + pl.col(f"h_def_{f}")).alias(f"m_a_{f}"))
    X_exprs.append(((pl.col(f"h_off_{f}") + pl.col(f"a_def_{f}")) - (pl.col(f"a_off_{f}") + pl.col(f"h_def_{f}"))).alias(f"d_{f}"))
d = d.with_columns(X_exprs)
d = d.drop([c for c in d.columns if c.startswith("x_h_")])
d = d.filter(pl.col("h_off_epa").is_not_null() & pl.col("a_off_epa").is_not_null())
d = d.with_columns((pl.col("week").cast(pl.Float64)).alias("week_f"))
d.write_parquet(os.path.join(OUT, "game_features.parquet"))
print("game feature rows", d.shape, flush=True)

# ---------------------------------------------------------------- walk-forward ridge
def ridge_fit(X, y, lam):
    Xm = X.mean(0); Xs = X.std(0) + 1e-9; ym = y.mean(); Xc = (X - Xm) / Xs; yc = y - ym
    beta = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ yc)
    return beta, Xm, Xs, ym
def ridge_pred(model, X):
    beta, Xm, Xs, ym = model
    return ((X - Xm) / Xs) @ beta + ym

diff_feats = [f"d_{f}" for f in FEATS] + ["rest_diff", "div_game", "neutral"]
sum_feats = [f"m_h_{f}" for f in FEATS] + [f"m_a_{f}" for f in FEATS] + ["indoor", "rest_diff"]
res = {"seasons": {}, "pooled": {}}
pred_rows = []
TEST_SEASONS = list(range(2014, 2026))
for S in TEST_SEASONS:
    tr = d.filter((pl.col("season") < S) & (pl.col("season") >= S - 8)).to_pandas()
    te = d.filter(pl.col("season") == S).to_pandas()
    # early weeks: ratings are mostly prior-season; that's fine (prior games only)
    Xtr = tr[diff_feats].fillna(0).to_numpy(); Xte = te[diff_feats].fillna(0).to_numpy()
    ytr = tr["result"].to_numpy().astype(float); yte = te["result"].to_numpy().astype(float)
    m_marg = ridge_fit(Xtr, ytr, 30.0); p_marg = ridge_pred(m_marg, Xte)
    # totals
    Xtr_t = tr[sum_feats].fillna(0).to_numpy(); Xte_t = te[sum_feats].fillna(0).to_numpy()
    ttr = tr["total"].to_numpy().astype(float); tte = te["total"].to_numpy().astype(float)
    m_tot = ridge_fit(Xtr_t, ttr, 30.0); p_tot = ridge_pred(m_tot, Xte_t)
    # market-aware residual: y - spread ~ feats (+ spread itself)
    sp_tr = tr["spread_line"].to_numpy().astype(float); sp_te = te["spread_line"].to_numpy().astype(float)
    Xr_tr = np.column_stack([Xtr, sp_tr]); Xr_te = np.column_stack([Xte, sp_te])
    m_res = ridge_fit(Xr_tr, ytr - sp_tr, 60.0); p_res = sp_te + ridge_pred(m_res, Xr_te)
    tl_tr = tr["total_line"].to_numpy().astype(float); tl_te = te["total_line"].to_numpy().astype(float)
    m_rest = ridge_fit(np.column_stack([Xtr_t, tl_tr]), ttr - tl_tr, 60.0); p_rest = tl_te + ridge_pred(m_rest, np.column_stack([Xte_t, tl_te]))
    for i in range(len(te)):
        pred_rows.append({"season": S, "week": int(te["week"].iloc[i]), "game_id": te["game_id"].iloc[i], "result": yte[i], "total": tte[i],
                          "spread_line": sp_te[i], "total_line": tl_te[i], "model_margin": p_marg[i], "model_total": p_tot[i],
                          "resid_margin": p_res[i], "resid_total": p_rest[i]})
    def rmse(a, b): return float(np.sqrt(np.mean((a - b) ** 2)))
    res["seasons"][S] = {"n": int(len(te)), "rmse_spread": rmse(sp_te, yte), "rmse_model": rmse(p_marg, yte), "rmse_resid": rmse(p_res, yte),
                         "rmse_blend50": rmse(0.5 * p_marg + 0.5 * sp_te, yte),
                         "rmse_total_line": rmse(tl_te, tte), "rmse_model_total": rmse(p_tot, tte), "rmse_resid_total": rmse(p_rest, tte),
                         "corr_model_spread": float(np.corrcoef(p_marg, sp_te)[0, 1])}
    print(S, {k: round(v, 3) if isinstance(v, float) else v for k, v in res["seasons"][S].items()}, flush=True)

P = pl.DataFrame(pred_rows)
P.write_parquet(os.path.join(OUT, "walkforward_predictions.parquet"))
pp = P.to_pandas()
y = pp["result"].to_numpy(); sp = pp["spread_line"].to_numpy(); pm = pp["model_margin"].to_numpy(); pr = pp["resid_margin"].to_numpy()
def rmse(a, b): return float(np.sqrt(np.mean((a - b) ** 2)))
pooled = {"n": int(len(y)), "rmse_spread": rmse(sp, y), "rmse_model": rmse(pm, y), "rmse_resid": rmse(pr, y),
          "mae_spread": float(np.mean(np.abs(sp - y))), "mae_model": float(np.mean(np.abs(pm - y)))}
# blend weights
blend = {}
for w in np.arange(0, 1.01, 0.1):
    blend[round(float(w), 1)] = rmse(w * pm + (1 - w) * sp, y)
pooled["blend_rmse_by_model_weight"] = blend
# regress result on spread and model jointly (encompassing test): result ~ a + b*spread + c*model
A = np.column_stack([np.ones_like(sp), sp, pm]); coef, *_ = np.linalg.lstsq(A, y, rcond=None)
pooled["encompassing_coef_[const,spread,model]"] = [float(c) for c in coef]
# ATS: model side when |model - spread| > k; hit rate with Wilson CI and push exclusion
ats = {}
for k in (0.0, 1.0, 2.0, 3.0, 4.0):
    sel = np.abs(pm - sp) > k
    side = np.sign(pm - sp)[sel]; cover = np.sign(y - sp)[sel]
    nonpush = cover != 0
    wins = (side[nonpush] == cover[nonpush]).sum(); n = int(nonpush.sum())
    p = wins / n if n else float("nan"); se = np.sqrt(p * (1 - p) / n) if n else float("nan")
    ats[k] = {"n": n, "hit": float(p), "ci95": [float(p - 1.96 * se), float(p + 1.96 * se)]}
pooled["ats_model_vs_spread"] = ats
# win-prob log loss: model normal(sd=13.2) vs spread
sd = 13.2
nz = y != 0
for name, m in (("spread", sp), ("model", pm), ("resid", pr), ("blend30", 0.3 * pm + 0.7 * sp)):
    p = norm.cdf(m[nz] / sd); yy = (y[nz] > 0).astype(float)
    pooled[f"logloss_{name}"] = float(-np.mean(yy * np.log(p) + (1 - yy) * np.log(1 - p)))
    pooled[f"brier_{name}"] = float(np.mean((p - yy) ** 2))
# by-week-bucket: early season vs late
for lab, sel in (("weeks_1_4", pp["week"] <= 4), ("weeks_5_18", pp["week"] > 4)):
    pooled[f"rmse_spread_{lab}"] = rmse(sp[sel], y[sel]); pooled[f"rmse_model_{lab}"] = rmse(pm[sel], y[sel]); pooled[f"rmse_resid_{lab}"] = rmse(pr[sel], y[sel])
# totals pooled
t = pp["total"].to_numpy(); tl = pp["total_line"].to_numpy(); mt = pp["model_total"].to_numpy(); rt = pp["resid_total"].to_numpy()
pooled.update({"rmse_total_line": rmse(tl, t), "rmse_model_total": rmse(mt, t), "rmse_resid_total": rmse(rt, t)})
res["pooled"] = pooled
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)
print(json.dumps(pooled, indent=1, default=float))
