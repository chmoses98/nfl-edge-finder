"""FIVE-SEASON BASELINE REPORT of the frozen incumbent simulation (2021-2025). RESEARCH_ONLY.

Reads the row-level distributions written by ``five_year.run_season`` and produces, per season AND pooled:
MAE, RMSE, signed bias, CRPS, 50% / 90% coverage, PIT histogram, ladder Brier, the naive prior-only baseline,
sample sizes, plus game-clustered bootstrap intervals for the pooled numbers and an error decomposition
(team volume -> player share -> efficiency) that decides where projection work should go.

The per-season scores use exactly ``backtest.evaluate``'s formulas and floors; ``check_against_evaluate``
re-derives the season numbers and compares them with the ones ``evaluate`` wrote, so the pooled table cannot
silently score a different population.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from . import backtest as Bt
from . import training as T

STATS = ["carries", "rush_yards", "targets", "receptions", "rec_yards", "attempts", "completions", "pass_yards", "pass_td", "any_td"]
PRIMARY_STATS = ["carries", "rush_yards", "targets", "receptions", "rec_yards", "attempts", "completions", "pass_yards"]
TEAM_STATS = ["plays", "pass_att", "rush_att", "dropbacks", "targets", "points", "pass_yards", "rush_yards", "off_td"]
QL = Bt.QLEVELS
I25, I75, I05, I95 = (int(np.argmin(np.abs(QL - q))) for q in (0.25, 0.75, 0.05, 0.95))
B = 2000
SEED = 20261005


def crps_rows(Q: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Vectorised ``backtest.crps_from_quantiles``: 2 x mean pinball loss over the stored quantile levels."""
    d = y[:, None] - Q
    return 2.0 * np.where(d >= 0, QL[None, :] * d, (QL[None, :] - 1) * d).mean(axis=1)


def scored_rows(P: pd.DataFrame, stat: str) -> pd.DataFrame:
    """The rows ``evaluate`` scores for a statistic (predictive mean above the per-statistic floor), with the
    per-row loss columns attached."""
    g = P[(P["stat"] == stat) & (P["mean"] >= Bt.FLOORS.get(stat, 0.0))].copy()
    if g.empty:
        return g
    Q = np.vstack(g["quantiles"].to_numpy()); y = g["actual"].to_numpy(float); mu = g["mean"].to_numpy(float)
    g["ae"] = np.abs(mu - y); g["se"] = (mu - y) ** 2; g["err"] = mu - y
    g["crps"] = crps_rows(Q, y)
    g["in50"] = (y >= Q[:, I25]) & (y <= Q[:, I75]); g["in90"] = (y >= Q[:, I05]) & (y <= Q[:, I95])
    g["pit"] = (Q <= y[:, None]).mean(axis=1)
    g["rpit"] = randomized_pit(np.vstack(g["pmf"].to_numpy()), y, stat)
    if stat in Bt.LADDERS:
        pm = np.vstack(g["pmf"].to_numpy()); surv = 1.0 - np.cumsum(pm, axis=1)
        g["ladder_brier"] = np.mean([(surv[:, k - 1] - (y >= k)) ** 2 for k in Bt.LADDERS[stat]], axis=0)
    if "baseline" in g.columns:
        g["base_ae"] = np.abs(g["baseline"].to_numpy(float) - y)
    return g


def randomized_pit(pmf: np.ndarray, y: np.ndarray, stat: str, seed: int = SEED) -> np.ndarray:
    """F(y-1) + U p(y) on the stored integer pmf -- uniform under a calibrated discrete forecast, unlike the
    endpoint-inclusive interval coverage, which over-counts small integer outcomes."""
    yi = np.clip(np.round(y), 0, Bt.STAT_GRID[stat]).astype(int)
    cdf = np.cumsum(pmf, axis=1)
    below = np.where(yi > 0, cdf[np.arange(len(yi)), np.maximum(yi - 1, 0)], 0.0)
    at = pmf[np.arange(len(yi)), yi]
    u = np.random.default_rng(seed).random(len(yi))
    return below + u * at


def uniformity(pit: np.ndarray, bins: int = 10) -> dict:
    h = np.histogram(pit, bins=bins, range=(0, 1))[0]
    e = len(pit) / bins
    return {"hist": h.tolist(), "chi2": float(((h - e) ** 2 / e).sum()), "df": bins - 1,
            "share_below_0.05": float(np.mean(pit < 0.05)), "share_above_0.95": float(np.mean(pit > 0.95))}


def _clustered(df: pd.DataFrame, cols: list, B_: int = B, seed: int = SEED) -> dict:
    """Means of ``cols`` with game-clustered bootstrap 95% intervals (games resampled, not rows)."""
    gs = df.groupby("game_id")[cols].agg(["sum", "count"])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(gs), size=(B_, len(gs)))
    out = {}
    for c in cols:
        s = gs[(c, "sum")].to_numpy(float); n = gs[(c, "count")].to_numpy(float)
        bs = s[idx].sum(axis=1) / n[idx].sum(axis=1)
        out[c] = {"mean": float(s.sum() / n.sum()), "lo": float(np.quantile(bs, 0.025)), "hi": float(np.quantile(bs, 0.975))}
    return out


def summarize(g: pd.DataFrame, clustered: bool = False) -> dict:
    if g.empty:
        return {}
    rec = {"n": int(len(g)), "n_games": int(g["game_id"].nunique()), "mae": float(g["ae"].mean()), "rmse": float(np.sqrt(g["se"].mean())),
           "bias": float(g["err"].mean()), "crps": float(g["crps"].mean()), "cover50": float(g["in50"].mean()),
           "cover90": float(g["in90"].mean()), "pit_hist": np.histogram(g["pit"], bins=10, range=(0, 1))[0].tolist(),
           "mean_pred": float(g["mean"].mean()), "mean_actual": float(g["actual"].mean()),
           "randomized_pit": uniformity(g["rpit"].to_numpy())}
    if "ladder_brier" in g.columns:
        rec["ladder_brier"] = float(g["ladder_brier"].mean())
    if "base_ae" in g.columns and g["base_ae"].notna().any():
        ok = g[g["base_ae"].notna()]
        rec["baseline_mae"] = float(ok["base_ae"].mean())
        rec["mae_vs_baseline_pct"] = float(100 * (ok["ae"].mean() / ok["base_ae"].mean() - 1))
        rec["n_baseline"] = int(len(ok))
    if clustered:
        cols = ["ae", "crps", "in50", "in90"] + (["ladder_brier"] if "ladder_brier" in g.columns else [])
        rec["ci"] = _clustered(g, cols)
        if "base_ae" in g.columns and g["base_ae"].notna().any():
            ok = g[g["base_ae"].notna()].assign(d_ae=lambda x: x["ae"] - x["base_ae"])
            rec["ci"]["mae_minus_baseline"] = _clustered(ok, ["d_ae"])["d_ae"]
    return rec


def team_summary(Tt: pd.DataFrame, stat: str) -> dict:
    g = Tt[(Tt["stat"] == stat) & Tt["actual"].notna()]
    if g.empty:
        return {}
    Q = np.vstack(g["quantiles"].to_numpy()); y = g["actual"].to_numpy(float); mu = g["mean"].to_numpy(float)
    return {"n": int(len(g)), "mae": float(np.mean(np.abs(mu - y))), "rmse": float(np.sqrt(np.mean((mu - y) ** 2))),
            "bias": float(np.mean(mu - y)), "crps": float(crps_rows(Q, y).mean()),
            "cover50": float(np.mean((y >= Q[:, I25]) & (y <= Q[:, I75]))), "cover90": float(np.mean((y >= Q[:, I05]) & (y <= Q[:, I95])))}


def naive_baseline(season: int, history_start: int = 2016) -> pd.DataFrame:
    """``backtest._baseline`` for the season, on frames built with that season's own frozen priors."""
    priors = T.fit_priors_for(season, history_start)
    frames = T.assemble(range(history_start, season + 1), verbose=lambda *x: None, priors=priors)
    return Bt._baseline(frames, season)


def load_season(out_dir: str, season: int, baseline: pd.DataFrame | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    P = pd.read_parquet(os.path.join(out_dir, f"player_dists_{season}.parquet"))
    Tt = pd.read_parquet(os.path.join(out_dir, f"team_dists_{season}.parquet"))
    if baseline is not None:
        P = P.merge(baseline, on=["game_id", "player_id", "stat"], how="left")
    return P, Tt


def check_against_evaluate(season_rec: dict, ev: dict, tol: float = 1e-9) -> list:
    """Differences between this module's per-season numbers and the ones ``backtest.evaluate`` wrote."""
    bad = []
    for st, r in season_rec["player"].items():
        e = ev["player"].get(st)
        if not e:
            continue
        for k in ("n", "mae", "rmse", "bias", "crps", "cover50", "cover90", "ladder_brier", "baseline_mae"):
            if k in e and k in r and abs(float(e[k]) - float(r[k])) > tol * max(1.0, abs(float(e[k]))):
                bad.append((st, k, e[k], r[k]))
    return bad


# ------------------------------------------------------------------------------------- decomposition
DECOMP = {"rush_yards": ("carries", "rush_att"), "rec_yards": ("targets", "targets"), "receptions": ("targets", "targets"),
          "pass_yards": ("attempts", "pass_att")}


def decomposition(P: pd.DataFrame, Tt: pd.DataFrame) -> dict:
    """Sequential substitution of the realised value for the expected one along the hierarchy
    TEAM VOLUME -> PLAYER SHARE -> PER-OPPORTUNITY EFFICIENCY, per player-game, on ``evaluate``'s scored rows.
    Component errors: team = C s e - mu; share = c e - C s e; efficiency = y - c e  (they sum to y - mu)."""
    out = {}
    tm = Tt.pivot_table(index=["game_id", "team"], columns="stat", values=["mean", "actual"])
    for st, (opp, tvol) in DECOMP.items():
        g = P[(P["stat"] == st) & (P["mean"] >= Bt.FLOORS[st])][["game_id", "team", "player_id", "mean", "actual"]]
        o = P[P["stat"] == opp][["game_id", "player_id", "mean", "actual"]].rename(columns={"mean": "mu_c", "actual": "c"})
        g = g.merge(o, on=["game_id", "player_id"])
        tv = tm.xs(tvol, axis=1, level=1).reset_index().rename(columns={"mean": "mu_C", "actual": "C"})
        g = g.merge(tv, on=["game_id", "team"])
        g = g[(g["mu_c"] > 0) & (g["mu_C"] > 0)]
        e = g["mean"] / g["mu_c"]; s = g["mu_c"] / g["mu_C"]
        team = g["C"] * s * e - g["mean"]; share = g["c"] * e - g["C"] * s * e; eff = g["actual"] - g["c"] * e
        tot = g["actual"] - g["mean"]
        sse = float((tot ** 2).sum())
        comp = {"team_volume": team, "player_share": share, "efficiency": eff}
        out[st] = {"n": int(len(g)), "rmse_total": float(np.sqrt((tot ** 2).mean())),
                   "rmse": {k: float(np.sqrt((v ** 2).mean())) for k, v in comp.items()},
                   "mean_abs": {k: float(v.abs().mean()) for k, v in comp.items()},
                   "variance_share": {k: float((v ** 2).sum() / sse) for k, v in comp.items()},
                   "covariance_share": float(1 - sum((v ** 2).sum() for v in comp.values()) / sse)}
    return out


def pooled_and_by_season(out_dir: str, seasons, baselines: dict | None = None) -> dict:
    by, rows, trows, decomp_rows = {}, {st: [] for st in STATS}, [], []
    for y in seasons:
        P, Tt = load_season(out_dir, y, (baselines or {}).get(y))
        wf = json.load(open(os.path.join(out_dir, f"wf_{y}.json")))
        rec = {"player": {}, "team": {}}
        for st in STATS:
            g = scored_rows(P, st)
            if g.empty:
                continue
            g["season"] = y
            rec["player"][st] = summarize(g, clustered=True)
            rows[st].append(g)
        for st in TEAM_STATS:
            rec["team"][st] = team_summary(Tt, st)
        rec["evaluate_mismatches"] = check_against_evaluate(rec, wf["evaluation"])
        rec["decomposition"] = decomposition(P, Tt)
        rec["run"] = {k: wf["run"].get(k) for k in ("games", "games_simulated", "skipped", "coherence_failures", "player_rows", "team_rows")}
        rec["evidence_class"] = wf["evidence_class"]; rec["train_seasons"] = wf["train_seasons"]
        rec["priors_fit_seasons"] = wf["priors_fit_seasons"]; rec["eligibility"] = wf["eligibility"]
        q = wf["qb_identification"]
        rec["qb_identification"] = {k: q[k] for k in ("team_games", "sim_qb1_is_actual_starter", "rate")}
        by[str(y)] = rec
        Tt["season"] = y; trows.append(Tt)
    pooled = {"player": {}, "team": {}}
    for st in STATS:
        if rows[st]:
            pooled["player"][st] = summarize(pd.concat(rows[st], ignore_index=True), clustered=True)
    Tall = pd.concat(trows, ignore_index=True)
    for st in TEAM_STATS:
        pooled["team"][st] = team_summary(Tall, st)
    return {"by_season": by, "pooled": pooled}
