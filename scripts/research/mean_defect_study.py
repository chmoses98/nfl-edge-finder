#!/usr/bin/env python3
"""Market-free chronological test of the player mean model: frozen design (v1) vs count-model repair (v2).

Scores P(Y >= k) ladders and mean bias against the box score only. Nothing here looks at a price.
Selection seasons 2021-2024 (fit on seasons < T); 2025 confirmation; 2026 weeks 1-6 untouched by the choice
(the diagnosis that motivated v2 had seen the 2025 and 2026 early-season bias, so those are CONFIRMATION, not discovery).

Usage: python scripts/research/mean_defect_study.py [out.json]   (needs data/raw/nflverse stats_player, snap_counts, players, schedules)
"""
from __future__ import annotations
import json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research import player_distributions as pdist          # noqa: E402
from nfl_edge.shadow.models import fit_bundle                         # noqa: E402

STATS = ["receptions", "targets", "carries"]
WINDOWS = {"select_2021_24": lambda d: d.season.between(2021, 2024), "confirm_2025": lambda d: d.season == 2025,
           "untouched_2026_wk1_6": lambda d: d.season == 2026}


def frame():
    """Feature frame built EXACTLY as the live pricer builds it (scripts/shadow/price_slate.py): same history window,
    same tuned EWMA config (research/player_distributions/results.json), same position priors."""
    cfg = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
    df = pdist.load_player_games(ROOT, range(2013, 2027))
    pri = pdist.position_priors(df, range(2013, 2016))
    return pdist.add_ewma_features(df, halflife=cfg["halflife"], season_carry=cfg["season_carry"],
                                   shrink_k=cfg["shrink_k"], priors=pri)


def score(df, target, design, stat):
    b = fit_bundle(df, target, f"study-{design}", {"mean_design": design, "min_train_season": 2016}, stats=[stat], verbose=lambda *a, **k: None)
    sm = b.stat_models[stat]
    spec = pdist.STAT_SPECS[stat]
    te = df[pdist.population_mask(df, spec.pop) & (df.season == target) & (df.n_prior >= 10)
            & (df[f"ewma_{spec.opp}"] >= spec.elig_min_opp)].copy()   # the listed-player-like population
    grid, S, mu = sm.survival(te)
    ks = [k for k in spec.thresholds]
    rows = []
    for k in ks:
        p = S[:, np.searchsorted(grid, k)]
        y = (te[spec.col].to_numpy() >= k).astype(float)
        rows.append(pd.DataFrame({"k": k, "p": p, "y": y, "early": (te.week.to_numpy() <= 6), "gid": te.game_id.to_numpy(),
                                  "pid": te.player_id.to_numpy()}))
    r = pd.concat(rows)
    return r, float(mu.mean()), float(te[spec.col].mean())


def main(out):
    df = frame()
    res = {}
    for stat in STATS:
        for design in ("v1", "v2"):
            for target in range(2021, 2027):
                r, mu, act = score(df, target, design, stat)
                r["season"] = target
                res.setdefault((stat, design), []).append((r, mu, act, target))
    summary = {}
    for (stat, design), lst in res.items():
        for wname, sel in WINDOWS.items():
            rs = [r for r, mu, act, t in lst if sel(pd.DataFrame({"season": [t]})).iloc[0]]
            if not rs: continue
            r = pd.concat(rs)
            for part, m in (("all", np.ones(len(r), bool)), ("weeks1_6", r.early.to_numpy())):
                g = r[m]
                # one cluster per player-game: sum of squared errors over its rungs
                key = g.gid + "|" + g.pid
                se = ((g.p - g.y) ** 2).groupby(key.values).sum()
                summary[f"{stat}|{design}|{wname}|{part}"] = {
                    "n_rungs": int(len(g)), "n_player_games": int(key.nunique()),
                    "ladder_brier": float(((g.p - g.y) ** 2).mean()),
                    "mean_p": float(g.p.mean()), "hit_rate": float(g.y.mean()),
                    "bias_pts": float((g.p.mean() - g.y.mean()) * 100),
                    "se_sum_per_pg": float(se.mean())}
    json.dump(summary, open(out, "w"), indent=1)
    for stat in STATS:
        for wname in WINDOWS:
            for part in ("all", "weeks1_6"):
                a, b = summary.get(f"{stat}|v1|{wname}|{part}"), summary.get(f"{stat}|v2|{wname}|{part}")
                if a and b:
                    print(f"{stat:10s} {wname:22s} {part:8s} pg={a['n_player_games']:5d}  Brier v1={a['ladder_brier']:.4f} v2={b['ladder_brier']:.4f}"
                          f"  bias(pp) v1={a['bias_pts']:+.1f} v2={b['bias_pts']:+.1f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "research/mean_defect/results.json")
