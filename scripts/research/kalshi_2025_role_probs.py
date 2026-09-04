#!/usr/bin/env python3
"""Model probabilities for the exact 2025 Kalshi rungs, WITH and WITHOUT the role features.

research/model_vs_market showed the market beating the pre-role-feature model by 0.0104 Brier. The obvious
question -- does this session's opportunity engine close that gap -- needs the two arms scored on the same
contracts. This produces both, walk-forward on seasons < 2025, and writes one row per rung.
"""
import glob, json, os, sys

import numpy as np
import pandas as pd
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research import player_distributions as pdist  # noqa: E402
from nfl_edge.kalshi.classifier import classify  # noqa: E402

MD = sys.argv[1] if len(sys.argv) > 1 else "/home/user/_md"
OUT = os.path.join(ROOT, "research", "model_vs_market"); os.makedirs(OUT, exist_ok=True)
CHOSEN = {"passing_yards": "normal", "rushing_yards": "scale_emp_binned", "receiving_yards": "scale_emp_binned",
          "receptions": "negbin", "passing_tds": "poisson", "anytime_td": "negbin"}
STAT_MAP = {"passing_yards": "passing_yards", "rushing_yards": "rushing_yards",
            "receiving_yards": "receiving_yards", "receptions": "receptions",
            "passing_tds": "passing_tds", "touchdowns": "anytime_td"}


def main():
    df = pl.read_parquet(os.path.join(ROOT, "research/opportunity/opportunity_features.parquet")).to_pandas()
    df = df.sort_values(["player_id", "season", "week"]).reset_index(drop=True)
    assert pdist.has_role_features(df), "opportunity features missing; run scripts/research/opportunity_study.py"

    pmap = pl.read_parquet(os.path.join(ROOT, "data/silver/kalshi_player_map_2025.parquet")) \
        .filter(pl.col("gsis_id").is_not_null()).select("kalshi_player_id", "gsis_id").to_pandas()
    kid2gsis = dict(zip(pmap.kalshi_player_id, pmap.gsis_id))
    games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).filter(pl.col("season") == 2025)
    gk = {(r["gameday"], r["away_team"], r["home_team"]): r["game_id"]
          for r in games.select("gameday", "away_team", "home_team", "game_id").to_dicts()}

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
            rungs.append({"ticker": m["ticker"], "game_id": gid, "player_id": gs, "stat": STAT_MAP[s.stat],
                          "k": float(s.threshold), "y": 1.0 if m["result"] == "yes" else 0.0})
    R = pd.DataFrame(rungs)
    print(f"Kalshi settled rungs joined: {len(R)}  {R.stat.value_counts().to_dict()}", flush=True)

    out = []
    for stat, fam in CHOSEN.items():
        spec = pdist.STAT_SPECS[stat]; col = spec.col
        pm = pdist.population_mask(df, spec.pop)
        d = df[pm & (df.season >= 2016)]
        tr = d[d.season < 2025]; te = d[d.season == 2025].reset_index(drop=True)
        if not len(te):
            continue
        y_tr = np.clip(tr[col].to_numpy(float), 0, None)
        grid = np.arange(0, spec.grid_max + 1)
        F = {}
        for label, role in (("base", False), ("role", True)):
            mm = pdist.fit_mean_model(tr, spec, col, spec.kind, role=role)
            om = pdist.fit_mean_model(tr, spec, spec.opp, "count", role=role)
            mu_tr = pdist.predict_mean(mm, tr, spec, col, pdist.MU_FLOOR[spec.kind])
            mu_te = pdist.predict_mean(mm, te, spec, col, pdist.MU_FLOOR[spec.kind])
            muo_tr = pdist.predict_mean(om, tr, spec, spec.opp, 0.1)
            muo_te = pdist.predict_mean(om, te, spec, spec.opp, 0.1)
            eff_tr = tr[spec.eff].to_numpy() if spec.eff and spec.eff in tr.columns else None
            eff_te = te[spec.eff].to_numpy() if spec.eff and spec.eff in te.columns else None
            fo = pdist.make_family(fam, spec); fo.fit(mu_tr, muo_tr, eff_tr, y_tr)
            F[label] = fo.cdf_grid(mu_te, muo_te, eff_te, grid)
        key = {(g, p): i for i, (g, p) in enumerate(zip(te.game_id, te.player_id))}
        sub = R[R.stat == stat]
        n = 0
        for r in sub.itertuples():
            i = key.get((r.game_id, r.player_id))
            if i is None:
                continue
            k = int(r.k)
            row = {"ticker": r.ticker, "stat": stat, "k": k, "y": r.y}
            for label in ("base", "role"):
                row[f"p_{label}"] = float(1.0 - F[label][i, k - 1]) if 1 <= k <= spec.grid_max else (1.0 if k <= 0 else 0.0)
            out.append(row); n += 1
        print(f"  {stat}: {n} rungs priced under both arms", flush=True)
    O = pl.DataFrame(out)
    O.write_parquet(os.path.join(OUT, "prop_probs_2025_both_arms.parquet"))
    print(f"wrote {O.height} rungs to research/model_vs_market/prop_probs_2025_both_arms.parquet")


if __name__ == "__main__":
    main()
