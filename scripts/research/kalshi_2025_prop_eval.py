#!/usr/bin/env python3
"""Evaluate the chosen distribution families on the EXACT player-prop rungs Kalshi listed in 2025 (settled, archived).
Model: mean model + family fitted on seasons < 2025 (walk-forward, no 2025 information), EWMA features point-in-time.
Join: Kalshi player UUID -> GSIS (data/silver/kalshi_player_map_2025.parquet), nflverse game_id from event ticker, stat, threshold.
Outputs research/kalshi_2025/prop_model_eval.json + parquet of rung-level model probabilities (for later comparison with prices)."""
import json, os, sys, glob
import numpy as np, pandas as pd, polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research import player_distributions as pdist
from nfl_edge.kalshi.classifier import classify
MD = sys.argv[1] if len(sys.argv) > 1 else "/home/user/_md"
OUT = os.path.join(ROOT, "research/kalshi_2025")
CHOSEN = {"passing_yards": "normal", "rushing_yards": "scale_emp_binned", "receiving_yards": "scale_emp_binned", "receptions": "negbin",
          "passing_tds": "poisson", "anytime_td": "negbin"}
STAT_MAP = {"passing_yards": "passing_yards", "rushing_yards": "rushing_yards", "receiving_yards": "receiving_yards", "receptions": "receptions",
            "passing_tds": "passing_tds", "touchdowns": "anytime_td"}
cfg = json.load(open(os.path.join(OUT, "..", "player_distributions", "results.json")))["config"]
df = pdist.load_player_games(ROOT, range(2012, 2026))
priors = pdist.position_priors(df, range(2013, 2016))
df = pdist.add_ewma_features(df, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"], priors=priors)
pmap = pl.read_parquet(os.path.join(ROOT, "data/silver/kalshi_player_map_2025.parquet")).filter(pl.col("gsis_id").is_not_null()).select("kalshi_player_id", "gsis_id").to_pandas()
kid2gsis = dict(zip(pmap.kalshi_player_id, pmap.gsis_id))
games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).filter(pl.col("season") == 2025)
gk = {(r["gameday"], r["away_team"], r["home_team"]): r["game_id"] for r in games.select("gameday", "away_team", "home_team", "game_id").to_dicts()}
rungs = []
for f in glob.glob(os.path.join(MD, "data/kalshi/backfill/markets/KXNFL*.jsonl")):
    for line in open(f):
        m = json.loads(line)
        if m.get("result") not in ("yes", "no"):
            continue
        s = classify(m)
        if s.family != "PLAYER_STAT" or s.stat not in STAT_MAP or s.threshold is None or not s.game_date:
            continue
        gid = gk.get((s.game_date, s.away_team, s.home_team))
        gs = kid2gsis.get(s.player_kalshi_id)
        if not gid or not gs:
            continue
        rungs.append({"ticker": m["ticker"], "game_id": gid, "player_id": gs, "stat": STAT_MAP[s.stat], "k": float(s.threshold), "y": 1.0 if m["result"] == "yes" else 0.0,
                      "volume": float(m.get("volume_fp") or 0), "player_name": s.player_name})
R = pd.DataFrame(rungs)
print("Kalshi settled rungs joined:", len(R), R.stat.value_counts().to_dict())
out_rows = []; summary = {}
for stat, fam in CHOSEN.items():
    spec = pdist.STAT_SPECS[stat]; col = spec.col
    pm = pdist.population_mask(df, spec.pop)
    d = df[pm & (df.season >= 2016)].copy()
    tr = d[d.season < 2025]; te = d[d.season == 2025]
    if not len(te):
        continue
    y_tr = np.clip(tr[col].to_numpy(float), 0, None)
    mm = pdist.fit_mean_model(tr, spec, col, spec.kind)
    mu_tr = pdist.predict_mean(mm, tr, spec, col, pdist.MU_FLOOR[spec.kind]); mu_te = pdist.predict_mean(mm, te, spec, col, pdist.MU_FLOOR[spec.kind])
    om = pdist.fit_mean_model(tr, spec, spec.opp, "count")
    muo_tr = pdist.predict_mean(om, tr, spec, spec.opp, 0.1); muo_te = pdist.predict_mean(om, te, spec, spec.opp, 0.1)
    eff_tr = tr[spec.eff].to_numpy() if spec.eff else None; eff_te = te[spec.eff].to_numpy() if spec.eff else None
    fam_obj = pdist.make_family(fam, spec); fam_obj.fit(mu_tr, muo_tr, eff_tr, y_tr)
    grid = np.arange(0, spec.grid_max + 1)
    F = fam_obj.cdf_grid(mu_te, muo_te, eff_te, grid)          # F[i, g] = P(Y <= grid[g])
    te = te.reset_index(drop=True)
    key = {(g, p): i for i, (g, p) in enumerate(zip(te.game_id, te.player_id))}
    sub = R[R.stat == stat]
    probs = []; ys = []; ks = []; tick = []; mus = []
    for r in sub.itertuples():
        i = key.get((r.game_id, r.player_id))
        if i is None:
            continue
        k = int(r.k)
        p = 1.0 - F[i, k - 1] if 1 <= k <= spec.grid_max else (1.0 if k <= 0 else 0.0)
        probs.append(p); ys.append(r.y); ks.append(k); tick.append(r.ticker); mus.append(mu_te[i])
    p = np.clip(np.array(probs), 1e-4, 1 - 1e-4); y = np.array(ys); k = np.array(ks)
    n = len(y)
    if n == 0:
        summary[stat] = {"n": 0}; continue
    brier = float(np.mean((p - y) ** 2)); clim = float(np.mean((y.mean() - y) ** 2))
    ll = float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
    bins = np.minimum((p * 10).astype(int), 9)
    rel = [{"bin": int(b), "pred": float(p[bins == b].mean()), "obs": float(y[bins == b].mean()), "n": int((bins == b).sum())} for b in range(10) if (bins == b).sum() >= 30]
    byk = sub.groupby("k").size()
    per_k = {}
    for kk in sorted(set(k)):
        m_ = k == kk
        if m_.sum() >= 40:
            per_k[int(kk)] = {"n": int(m_.sum()), "pred": float(p[m_].mean()), "obs": float(y[m_].mean())}
    summary[stat] = {"family": fam, "n": int(n), "brier": brier, "brier_climatology": clim, "brier_skill": 1 - brier / clim, "logloss": ll,
                     "mean_pred": float(p.mean()), "obs_yes": float(y.mean()), "reliability": rel, "per_threshold": per_k,
                     "unmatched_rungs": int(len(sub) - n)}
    print(f"{stat:16s} {fam:16s} n={n:5d} brier={brier:.4f} (clim {clim:.4f}, skill {1 - brier / clim:+.3f}) mean_pred={p.mean():.3f} obs={y.mean():.3f} unmatched={len(sub) - n}")
    for kk, v in per_k.items():
        print(f"    k>={kk:3d} n={v['n']:4d} pred={v['pred']:.3f} obs={v['obs']:.3f}")
    out_rows += [{"ticker": t, "stat": stat, "k": int(kk), "model_p": float(pp), "mu": float(mu), "y": float(yy)} for t, kk, pp, mu, yy in zip(tick, k, p, mus, y)]
pl.DataFrame(out_rows).write_parquet(os.path.join(OUT, "prop_model_probs_2025.parquet"))
json.dump(summary, open(os.path.join(OUT, "prop_model_eval.json"), "w"), indent=1)
