"""Market reconciliation: how far the football distribution is allowed to move away from the market.

The football simulation produces a full distribution; the quoted ladder identifies the market's own
distribution (location and dispersion).  The reconciled distribution is the FOOTBALL distribution
re-located so that its mean is

    m_final = m_market + w_family * (m_football - m_market)

with ``w_family`` the share of the football-vs-market disagreement that historical OUT-OF-SAMPLE evidence
says was real signal for that statistic family.  ``w = 0`` is "the market is the projection"; ``w = 1``
is "ignore the market".  The weights are fitted by ``fit_weights`` on settled rungs of an earlier period
(minimising the Brier score of the reconciled survival at the quoted thresholds, one weight per family,
with a disagreement-band diagnostic so a large disagreement can be shrunk harder than a small one), and
never on the period they are then evaluated on.  A family with no fitted weight is PASSED, not priced.

The shape of the reconciled distribution is the football shape: the market ladder rarely identifies the
tail (market_dist.py) while the simulation always produces one.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from nfl_edge.engines.player.dist import LatticeDistribution

RECONCILE_VERSION = "reconcile-1.0.0"
WEIGHT_GRID = np.round(np.arange(0.0, 1.01, 0.05), 2)
BANDS = [(0.0, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 1.01)]


def reconcile_distribution(football: LatticeDistribution, market_mean: float | None, w: float | None) -> tuple[LatticeDistribution, dict]:
    """Return (reconciled distribution, attribution).  With no market mean or no weight the football
    distribution is returned untouched and the attribution says so."""
    fm = football.mean()
    if market_mean is None or w is None or not np.isfinite(market_mean):
        return football, {"football_mean": fm, "market_mean": market_mean, "final_mean": fm, "weight": None,
                          "status": "NO_MARKET_CENTRE" if market_mean is None else "NO_WEIGHT"}
    target = market_mean + w * (fm - market_mean)
    if target <= 0:
        target = max(fm * 0.05, 0.01)
    out = football.shifted_to_mean(target, method="scale")
    return out, {"football_mean": fm, "market_mean": float(market_mean), "final_mean": float(out.mean()), "weight": float(w),
                 "disagreement_mean": float(fm - market_mean), "status": "RECONCILED"}


# ------------------------------------------------------------------------------------------ research
def _survival_after_shift(dist: LatticeDistribution, target_mean: float, k: float) -> float:
    if target_mean <= 0:
        target_mean = 0.01
    return dist.shifted_to_mean(target_mean, method="scale").survival(k)


def score_weights(rows: pd.DataFrame, dists: dict, market: dict, weights=WEIGHT_GRID) -> pd.DataFrame:
    """For every rung row (game_id, player_id, stat, k, y, market_mono) compute the reconciled survival at
    each weight.  ``dists`` maps (game_id, player_id, stat) -> football LatticeDistribution; ``market`` maps the
    same key -> market record with '_dist'.  Returns the rows with p_w columns and the disagreement."""
    recs = []
    for r in rows.itertuples():
        key = (r.game_id, r.player_id, r.stat)
        d = dists.get(key); m = market.get(key)
        if d is None or m is None or m.get("identification") in (None, "NONE"):
            continue
        mm = m["_dist"].mean(); fm = d.mean()
        rec = {"ticker": r.ticker, "game_id": r.game_id, "week": r.week, "player_id": r.player_id, "stat": r.stat, "k": r.k, "y": r.y,
               "market_mono": r.market_mono, "market_ident": m["identification"], "football_mean": fm, "market_mean": mm,
               "p_football": d.survival(r.k), "p_market_fit": m["_dist"].survival(r.k)}
        for w in weights:
            rec[f"p_w{w:.2f}"] = _survival_after_shift(d, mm + w * (fm - mm), r.k)
        recs.append(rec)
    return pd.DataFrame(recs)


def fit_weights(scored: pd.DataFrame, weights=WEIGHT_GRID) -> dict:
    """One weight per statistic family: the grid value minimising the Brier score of the reconciled survival
    against settlement, plus the Brier at every grid point and the disagreement-band table so the reader can
    see whether the optimum is flat or sharp.  Fit rows only; confirm on later rows with ``confirm``."""
    out = {}
    for stat, g in scored.groupby("stat"):
        y = g["y"].to_numpy(float)
        curve = {f"{w:.2f}": float(np.mean((g[f"p_w{w:.2f}"].to_numpy(float) - y) ** 2)) for w in weights}
        best_w = min(curve, key=curve.get)
        bands = []
        dis = np.abs(g["p_football"] - g["market_mono"]).to_numpy(float)
        for lo, hi in BANDS:
            m = (dis >= lo) & (dis < hi)
            if m.sum() < 30:
                continue
            sub = g[m]; yy = sub["y"].to_numpy(float)
            bcurve = {f"{w:.2f}": float(np.mean((sub[f"p_w{w:.2f}"].to_numpy(float) - yy) ** 2)) for w in weights}
            bands.append({"band": [lo, hi], "n": int(m.sum()), "best_w": float(min(bcurve, key=bcurve.get)),
                          "brier_market": float(np.mean((sub["market_mono"] - yy) ** 2)),
                          "brier_football": float(np.mean((sub["p_football"] - yy) ** 2)),
                          "brier_best": float(min(bcurve.values()))})
        out[stat] = {"weight": float(best_w), "n": int(len(g)), "games": int(g["game_id"].nunique()), "brier_curve": curve,
                     "brier_market_mono": float(np.mean((g["market_mono"] - y) ** 2)),
                     "brier_football": float(np.mean((g["p_football"] - y) ** 2)), "bands": bands}
    return out


def confirm(scored: pd.DataFrame, weights_by_stat: dict) -> dict:
    """Score the fitted weights on rows they were not fitted on, paired against the market, clustered by game."""
    out = {}
    for stat, g in scored.groupby("stat"):
        w = weights_by_stat.get(stat, {}).get("weight")
        if w is None:
            continue
        col = f"p_w{w:.2f}"
        y = g["y"].to_numpy(float); p = g[col].to_numpy(float); pm = g["market_mono"].to_numpy(float); pf = g["p_football"].to_numpy(float)
        d = (p - y) ** 2 - (pm - y) ** 2
        # game-clustered standard error of the paired Brier difference
        cl = pd.Series(d).groupby(g["game_id"].to_numpy()).sum(); n_g = len(cl); n = len(d)
        se = float(np.sqrt(np.sum((cl - d.sum() / n_g) ** 2) * n_g / (n_g - 1)) / n) if n_g > 1 else float("nan")
        out[stat] = {"weight": float(w), "n": int(n), "games": int(n_g), "brier_reconciled": float(np.mean((p - y) ** 2)),
                     "brier_market_mono": float(np.mean((pm - y) ** 2)), "brier_football": float(np.mean((pf - y) ** 2)),
                     "diff_vs_market": float(d.mean()), "se": se, "z": float(d.mean() / se) if se and se > 0 else None}
    return out


def encompassing(scored: pd.DataFrame) -> dict:
    """logit P(y) = a + b1 logit(p_football) + b2 logit(p_market): the football coefficient's share is the
    textbook check on whether the football model carries information the price does not (the earlier
    research found ~0.0 for the incumbent)."""
    from .models import logistic_fit
    out = {}
    eps = 1e-3
    for stat, g in scored.groupby("stat"):
        pf = np.clip(g["p_football"].to_numpy(float), eps, 1 - eps); pm = np.clip(g["market_mono"].to_numpy(float), eps, 1 - eps)
        X = np.column_stack([np.log(pf / (1 - pf)), np.log(pm / (1 - pm))])
        m = logistic_fit(X, g["y"].to_numpy(float), lam=0.01)
        b = np.asarray(m["beta"]) / np.asarray(m["sd"])   # back to the logit scale
        out[stat] = {"b_football": float(b[0]), "b_market": float(b[1]), "n": int(len(g))}
    return out


def save_weights(path: str, fitted: dict, confirmed: dict, meta: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"version": RECONCILE_VERSION, "meta": meta, "fitted": fitted, "confirmed": confirmed}, f, indent=1)


def load_weights(path: str) -> dict:
    with open(path) as f:
        return json.load(f)
