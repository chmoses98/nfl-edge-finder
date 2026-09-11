#!/usr/bin/env python3
"""Walk-forward feature ablation on the Pinnacle-linked ATP subset: does rest / recent load / surface
transition / rank add anything beyond the Elo+structural ensemble? Logistic models fitted on seasons < t,
evaluated on t (pooled). Features are timestamp-safe: computed from matches strictly before the tournament date."""
from __future__ import annotations
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJ)
from tennis_edge.eval.metrics import summary, bootstrap_diff


def logit(p):
    p = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4); return np.log(p / (1 - p))


def fit(X, y, ridge=1e-2):
    X = np.column_stack([X, np.ones(len(y))]); w = np.zeros(X.shape[1])
    for _ in range(100):
        q = 1 / (1 + np.exp(-(X @ w))); g = X.T @ (q - y) + ridge * w
        H = (X * (q * (1 - q))[:, None]).T @ X + ridge * np.eye(X.shape[1])
        step = np.linalg.solve(H, g); w -= step
        if np.max(np.abs(step)) < 1e-9:
            break
    return w


def predict(w, X):
    return 1 / (1 + np.exp(-(np.column_stack([X, np.ones(len(X))]) @ w)))


def main():
    m = pd.read_parquet(os.path.join(PROJ, "data", "processed", "matches.parquet"))
    m = m[(m.tour == "ATP") & (m.id_system == "sackmann") & (m.outcome_type != "WALKOVER") & m.tourney_date.notna()].copy()
    m["tourney_date"] = pd.to_datetime(m["tourney_date"])
    # per-player activity history (tourney_date as the match date proxy; all matches of a tournament share it)
    ev = pd.concat([m[["tourney_date", "winner_id", "surface", "match_key", "minutes", "games_w", "games_l"]].rename(columns={"winner_id": "pid"}).assign(games=lambda d: d.games_w.fillna(0) + d.games_l.fillna(0)),
                    m[["tourney_date", "loser_id", "surface", "match_key", "minutes", "games_w", "games_l"]].rename(columns={"loser_id": "pid"}).assign(games=lambda d: d.games_w.fillna(0) + d.games_l.fillna(0))])
    ev = ev.sort_values(["pid", "tourney_date"])
    feats = {}
    for pid, g in ev.groupby("pid"):
        dates = g.tourney_date.to_numpy(); surf = g.surface.to_numpy(); games = g.games.to_numpy()
        for i, (d, mk) in enumerate(zip(dates, g.match_key)):
            prev = dates[:i]; 
            if len(prev) == 0:
                feats[(pid, mk)] = (np.nan, 0, 0, 0)
                continue
            # strictly earlier tournaments only (same-date rows are the same event: unknown order)
            earlier = prev < d
            if not earlier.any():
                feats[(pid, mk)] = (np.nan, 0, 0, 0); continue
            last = prev[earlier].max()
            days = (d - last) / np.timedelta64(1, "D")
            w14 = earlier & (prev >= d - np.timedelta64(14, "D"))
            n14 = int(w14.sum()); g14 = float(games[:i][w14].sum())
            last_surface = surf[:i][earlier][-1]
            feats[(pid, mk)] = (days, n14, g14, int(last_surface != surf[i]) if last_surface and surf[i] else 0)
    linked = pd.read_parquet(os.path.join(PROJ, "research", "market_benchmark", "linked_ATP.parquet"))
    sr = pd.read_parquet(os.path.join(PROJ, "research", "market_benchmark", "sr_predictions_ATP.parquet"))
    df = linked.merge(sr[["match_key", "p_sr_300"]], on="match_key").merge(m[["match_key", "winner_id", "loser_id", "winner_rank", "loser_rank"]], on="match_key").drop(columns=["season"], errors="ignore").rename(columns={"season_m": "season"})
    flip = df["y"].to_numpy() == 0
    def side(a, b):
        return np.where(flip, b, a), np.where(flip, a, b)
    fw = np.array([feats.get((p, k), (np.nan, 0, 0, 0)) for p, k in zip(df.winner_id, df.match_key)])
    fl = np.array([feats.get((p, k), (np.nan, 0, 0, 0)) for p, k in zip(df.loser_id, df.match_key)])
    fa, fb = np.where(flip[:, None], fl, fw), np.where(flip[:, None], fw, fl)
    y = df["y"].to_numpy(); mkt = df["market"].to_numpy(); elo = df["model"].to_numpy()
    psr = np.where(flip, 1 - df["p_sr_300"].to_numpy(), df["p_sr_300"].to_numpy())
    ens = logit(0.5 * elo + 0.5 * psr) * 0 + 0.5 * logit(elo) + 0.5 * logit(psr)
    rank_w = pd.to_numeric(df.winner_rank, errors="coerce").fillna(500).clip(1, 2000).to_numpy(); rank_l = pd.to_numeric(df.loser_rank, errors="coerce").fillna(500).clip(1, 2000).to_numpy()
    ra, rb = side(rank_w, rank_l)
    days_a, days_b = np.nan_to_num(fa[:, 0], nan=30).clip(0, 60), np.nan_to_num(fb[:, 0], nan=30).clip(0, 60)
    F = {"ensemble_logit": ens, "log_rank_diff": np.log(rb) - np.log(ra), "rest_diff": np.log1p(days_a) - np.log1p(days_b),
         "load14_diff": fa[:, 1] - fb[:, 1], "games14_diff": (fa[:, 2] - fb[:, 2]) / 20.0, "surface_switch_diff": fa[:, 3] - fb[:, 3]}
    sets = {"ensemble_only": ["ensemble_logit"], "+rank": ["ensemble_logit", "log_rank_diff"], "+rest": ["ensemble_logit", "rest_diff"],
            "+load": ["ensemble_logit", "load14_diff", "games14_diff"], "+surface_switch": ["ensemble_logit", "surface_switch_diff"],
            "+all": list(F)}
    seasons = sorted(df.season.unique()); out = {}
    lines = ["# Feature ablation (ATP, Pinnacle-linked, walk-forward by season)", "", "| feature set | n | brier | log_loss | Brier diff vs ensemble_only [95% CI] | Brier diff vs market |", "|---|---|---|---|---|---|"]
    preds = {}
    for name, cols in sets.items():
        X = np.column_stack([F[c] for c in cols]); p = np.full(len(y), np.nan)
        for s in seasons:
            tr = (df.season < s).to_numpy(); te = (df.season == s).to_numpy()
            if tr.sum() < 800 or te.sum() == 0:
                continue
            w = fit(X[tr], y[tr]); p[te] = predict(w, X[te])
        preds[name] = p
    ok = ~np.isnan(preds["ensemble_only"])
    for name, p in preds.items():
        s = summary(y[ok], p[ok]); b = bootstrap_diff(y[ok], p[ok], preds["ensemble_only"][ok], n_boot=300); bm = bootstrap_diff(y[ok], p[ok], mkt[ok], n_boot=300)
        lines.append(f"| {name} | {int(ok.sum())} | {s['brier']:.4f} | {s['log_loss']:.4f} | {b['diff']:+.5f} [{b['ci_low']:+.5f}, {b['ci_high']:+.5f}] | {bm['diff']:+.5f} |")
    s = summary(y[ok], mkt[ok]); lines.append(f"| market (Pinnacle) | {int(ok.sum())} | {s['brier']:.4f} | {s['log_loss']:.4f} | | |")
    open(os.path.join(PROJ, "research", "market_benchmark", "RESULTS_ABLATION_ATP.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
