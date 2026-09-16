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


TD_STATS = {"any_td", "pass_td", "rush_td", "rec_td", "touchdowns", "passing_tds", "rushing_tds", "receiving_tds"}


def _poisson_lattice(mean: float, n: int) -> LatticeDistribution:
    k = np.arange(n)
    lam = max(float(mean), 1e-6)
    logp = -lam + k * np.log(lam) - np.cumsum(np.log(np.maximum(k, 1)))
    pmf = np.exp(logp); pmf[-1] += max(0.0, 1.0 - pmf.sum())
    return LatticeDistribution(pmf / pmf.sum(), meta={"family": "poisson", "loc": lam})


KIND_OF_STAT = {"rush_yards": "yards", "rec_yards": "yards", "pass_yards": "yards", "rushing_yards": "yards",
                "receiving_yards": "yards", "passing_yards": "yards", "receptions": "count", "carries": "count",
                "attempts": "count", "completions": "count", "targets": "count"}
MAX_SCALE = 4.0


def relocate(football: LatticeDistribution, target: float, stat: str | None = None) -> LatticeDistribution:
    """Move a football distribution to a target mean.

    * Touchdown families (small integer counts): a Poisson at the target mean -- an integer lattice with a
      0.0005 mean cannot be stretched 40x, and the allocation step is Poisson-like anyway.
    * Yardage and count families within a factor of MAX_SCALE of the target: the football SHAPE, support
      scaled (`LatticeDistribution.shifted_to_mean`).
    * Yardage and count families further away than that (the simulation gave a player a fraction of the role
      the market did): the football shape carries no information about a role it did not model, so the
      market's own two-parameter family (gamma / negative binomial with the stat-level dispersion prior of
      `engines.player.market_dist`) is used at the target mean.  A Poisson is never used for yards."""
    fm = football.mean()
    if stat in TD_STATS or (stat not in KIND_OF_STAT and fm < 0.5):
        return _poisson_lattice(target, football.n)
    ratio = target / max(fm, 1e-9)
    if ratio > MAX_SCALE or ratio < 1.0 / MAX_SCALE:
        from nfl_edge.engines.player.market_dist import DISPERSION_PRIOR, _survival_family
        kind = KIND_OF_STAT.get(stat, "yards")
        grid = np.arange(0, football.n)
        S = _survival_family(kind, grid, float(target), DISPERSION_PRIOR[kind]); S[0] = 1.0
        return LatticeDistribution.from_survival(S, meta={"family": "market_prior_family", "loc": float(target)})
    return football.shifted_to_mean(target, method="scale")


def reconcile_distribution(football: LatticeDistribution, market_mean: float | None, w: float | None,
                           stat: str | None = None) -> tuple[LatticeDistribution, dict]:
    """Return (reconciled distribution, attribution).  With no market mean or no weight the football
    distribution is returned untouched and the attribution says so."""
    fm = football.mean()
    if market_mean is None or w is None or not np.isfinite(market_mean):
        return football, {"football_mean": fm, "market_mean": market_mean, "final_mean": fm, "weight": None,
                          "status": "NO_MARKET_CENTRE" if market_mean is None else "NO_WEIGHT"}
    target = market_mean + w * (fm - market_mean)
    if target <= 0:
        target = max(fm * 0.05, 0.01)
    out = relocate(football, target, stat)
    return out, {"football_mean": fm, "market_mean": float(market_mean), "final_mean": float(out.mean()), "weight": float(w),
                 "disagreement_mean": float(fm - market_mean), "status": "RECONCILED"}


# ------------------------------------------------------------------------------------------ research
def _survival_after_shift(dist: LatticeDistribution, target_mean: float, k: float, stat: str | None = None) -> float:
    if target_mean <= 0:
        target_mean = 0.01
    return relocate(dist, target_mean, stat).survival(k)


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
            rec[f"p_w{w:.2f}"] = _survival_after_shift(d, mm + w * (fm - mm), r.k, r.stat)
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


MIN_FIT_ROWS = 500
MAX_CONFIRM_Z = 1.0


def deploy_weights(fitted_all: dict, fitted_fit: dict, confirmed: dict) -> dict:
    """The weight a family actually USES, from three pieces of evidence: the weight fitted on the early
    weeks, its paired confirmation on the later weeks, and the weight fitted on the whole season.

    A family earns a non-zero weight only if (a) the early-week fit had at least MIN_FIT_ROWS rows and
    a non-zero optimum, (b) that weight was not worse than the market on the later weeks beyond
    MAX_CONFIRM_Z, and (c) the deployed value is the SMALLER of the early-week and whole-season optima.
    Anything else deploys 0 -- the football distribution is shown at the market mean and never ranked --
    with the reason recorded."""
    out = {}
    for stat, allv in fitted_all.items():
        w_all = allv["weight"]; ff = fitted_fit.get(stat); cf = confirmed.get(stat)
        if not ff or ff["n"] < MIN_FIT_ROWS:
            out[stat] = {"weight": 0.0, "reason": "no early-week fit with enough rows to confirm", "w_all_2025": w_all,
                         "w_fit": ff["weight"] if ff else None, "n_fit": ff["n"] if ff else 0}
            continue
        if ff["weight"] <= 0.0:
            out[stat] = {"weight": 0.0, "reason": "early-week optimum was 0", "w_all_2025": w_all, "w_fit": 0.0, "n_fit": ff["n"]}
            continue
        z = (cf or {}).get("z")
        if cf is None or z is None or z > MAX_CONFIRM_Z:
            out[stat] = {"weight": 0.0, "reason": f"later-week confirmation worse than the market (z={z})", "w_all_2025": w_all,
                         "w_fit": ff["weight"], "n_fit": ff["n"], "confirm": cf}
            continue
        out[stat] = {"weight": float(min(ff["weight"], w_all)), "reason": "early-week fit confirmed on later weeks; smaller of the two optima",
                     "w_all_2025": w_all, "w_fit": ff["weight"], "n_fit": ff["n"], "confirm": cf}
    return out


def save_weights(path: str, fitted: dict, confirmed: dict, meta: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"version": RECONCILE_VERSION, "meta": meta, "fitted": fitted, "confirmed": confirmed}, f, indent=1)


def load_weights(path: str) -> dict:
    with open(path) as f:
        return json.load(f)
