#!/usr/bin/env python3
"""Direct anytime-TD model vs the count-derived probability, walk-forward, and on Kalshi's own 2025 rungs.

The distribution study found count families under-predict the 1+ touchdown rung by 2-3 points. Candidates:
  count_negbin      P(TD >= 1) from the negative-binomial count family (incumbent)
  count_poisson     P(TD >= 1) from a Poisson count family
  direct_binary     logistic regression on role features (nfl_edge/shadow/models.DirectTDModel)
  base_rate         position base rate (floor)
Evaluated on held-out seasons 2020-2025 (train < S), and separately on the 4,079 settled 2025 KXNFLANYTD rungs.
"""
import json, os, sys, glob
import numpy as np, pandas as pd, polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research import player_distributions as pdist
from nfl_edge.shadow.models import DirectTDModel
from nfl_edge.kalshi.classifier import classify
OUT = os.path.join(ROOT, "research", "anytime_td"); os.makedirs(OUT, exist_ok=True)
cfg = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
df = pdist.load_player_games(ROOT, range(2012, 2026))
priors = pdist.position_priors(df, range(2013, 2016))
df = pdist.add_ewma_features(df, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"], priors=priors)
spec = pdist.STAT_SPECS["anytime_td"]
d = df[pdist.population_mask(df, spec.pop) & (df.season >= 2016)].copy()
d["y"] = (d["any_td"].to_numpy(dtype=float) > 0).astype(float)
res = {"per_season": {}, "pooled": {}}
preds_all = {k: [] for k in ("count_negbin", "count_poisson", "direct_binary", "base_rate")}
ys_all = []; keys_all = []
for S in range(2020, 2026):
    tr = d[(d.season < S) & (d.season >= 2016)]; te = d[d.season == S]
    if not len(te): continue
    y_tr = np.clip(tr[spec.col].to_numpy(float), 0, None); y_te = te["y"].to_numpy()
    mm = pdist.fit_mean_model(tr, spec, spec.col, spec.kind)
    om = pdist.fit_mean_model(tr, spec, spec.opp, "count")
    mu_tr = pdist.predict_mean(mm, tr, spec, spec.col, pdist.MU_FLOOR[spec.kind]); mu_te = pdist.predict_mean(mm, te, spec, spec.col, pdist.MU_FLOOR[spec.kind])
    muo_tr = pdist.predict_mean(om, tr, spec, spec.opp, 0.1); muo_te = pdist.predict_mean(om, te, spec, spec.opp, 0.1)
    eff_tr = tr[spec.eff].to_numpy() if spec.eff else None; eff_te = te[spec.eff].to_numpy() if spec.eff else None
    grid = np.arange(0, spec.grid_max + 1)
    out = {}
    for fam_name, key in (("negbin", "count_negbin"), ("poisson", "count_poisson")):
        f = pdist.make_family(fam_name, spec); f.fit(mu_tr, muo_tr, eff_tr, y_tr)
        F = f.cdf_grid(mu_te, muo_te, eff_te, grid)
        out[key] = np.clip(1.0 - F[:, 0], 1e-6, 1 - 1e-6)      # P(Y >= 1) = 1 - P(Y <= 0)
    out["direct_binary"] = np.clip(DirectTDModel().fit(tr).predict(te), 1e-6, 1 - 1e-6)
    base = tr.groupby("position")["any_td"].apply(lambda s: float((s > 0).mean())).to_dict()
    out["base_rate"] = np.clip(te["position"].map(base).fillna(0.15).to_numpy(float), 1e-6, 1 - 1e-6)
    row = {}
    for k, p in out.items():
        row[k] = {"brier": float(np.mean((p - y_te) ** 2)), "logloss": float(-np.mean(y_te * np.log(p) + (1 - y_te) * np.log(1 - p))),
                  "mean_pred": float(p.mean()), "obs": float(y_te.mean())}
        preds_all[k].append(p)
    res["per_season"][S] = {"n": int(len(te)), **{k: round(v["brier"], 5) for k, v in row.items()}}
    ys_all.append(y_te); keys_all.append(te[["player_id", "game_id"]].copy())
    print(S, res["per_season"][S], flush=True)
y = np.concatenate(ys_all)
for k in preds_all:
    p = np.concatenate(preds_all[k])
    bins = np.minimum((p * 10).astype(int), 9)
    res["pooled"][k] = {"n": int(len(y)), "brier": float(np.mean((p - y) ** 2)),
                        "logloss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
                        "mean_pred": float(p.mean()), "obs": float(y.mean()),
                        "reliability": [{"bin": int(b), "pred": float(p[bins == b].mean()), "obs": float(y[bins == b].mean()),
                                         "n": int((bins == b).sum())} for b in range(10) if (bins == b).sum() >= 100]}
print("\nPOOLED 2020-2025:")
for k, v in sorted(res["pooled"].items(), key=lambda kv: kv[1]["brier"]):
    print(f"  {k:16s} brier={v['brier']:.5f} logloss={v['logloss']:.4f} mean_pred={v['mean_pred']:.3f} obs={v['obs']:.3f}")
    for r in v["reliability"]: print(f"      bin {r['bin']}: pred {r['pred']:.3f} obs {r['obs']:.3f} (n={r['n']})")
# ---- on Kalshi's own settled 2025 anytime-TD rungs
keys = pd.concat(keys_all).reset_index(drop=True)
KM = {}
for k in preds_all: KM[k] = np.concatenate(preds_all[k])
frame = keys.copy(); frame["y"] = y
for k in KM: frame[k] = KM[k]
pm = pl.read_parquet(os.path.join(ROOT, "data/silver/kalshi_player_map_2025.parquet")).filter(pl.col("gsis_id").is_not_null()).select(pl.col("kalshi_player_id").alias("pid"), "gsis_id").unique("pid").to_pandas()
kid2g = dict(zip(pm.pid, pm.gsis_id))
games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).select(pl.col("gameday").alias("gd"), pl.col("away_team").alias("aw"), pl.col("home_team").alias("hm"), "game_id").to_pandas()
gk = {(r.gd, r.aw, r.hm): r.game_id for r in games.itertuples()}
rung = []
for f in glob.glob("/home/user/_md/data/kalshi/backfill/markets/KXNFLANYTD.jsonl") + glob.glob("/home/user/_md/data/kalshi/backfill/markets/KXNFLTD.jsonl"):
    for line in open(f):
        m = json.loads(line)
        if m.get("result") not in ("yes", "no"): continue
        s = classify(m)
        if s.stat != "touchdowns" or not s.game_date: continue
        g = gk.get((s.game_date, s.away_team, s.home_team)); gs = kid2g.get(s.player_kalshi_id)
        if not g or not gs or (s.threshold or 1) != 1: continue
        rung.append({"game_id": g, "player_id": gs, "y_mkt": 1.0 if m["result"] == "yes" else 0.0, "vol": float(m.get("volume_fp") or 0)})
R = pd.DataFrame(rung).merge(frame, on=["game_id", "player_id"], how="inner")
print(f"\nKALSHI 2025 anytime-TD rungs matched: {len(R)}")
res["kalshi_2025"] = {"n": int(len(R))}
if len(R):
    ym = R["y_mkt"].to_numpy()
    for k in preds_all:
        p = np.clip(R[k].to_numpy(), 1e-6, 1 - 1e-6)
        res["kalshi_2025"][k] = {"brier": float(np.mean((p - ym) ** 2)), "mean_pred": float(p.mean()), "obs": float(ym.mean())}
        print(f"  {k:16s} brier={res['kalshi_2025'][k]['brier']:.5f} pred={p.mean():.3f} obs={ym.mean():.3f}")
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
