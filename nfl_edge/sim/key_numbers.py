"""M1 -- key-number-aware joint (margin, total) distributions for the game centre. RESEARCH_ONLY.

Preregistered in research/game_script_v2/wave2/PREREGISTRATION.md, section 4. The incumbent
(`pricing/game_env.ResidualBank`) adds a historical residual to the target spread; that convolution is
translation-invariant and smears the integer structure of NFL margins (Wave 1: 7.9% simulated vs 15.4% realized
final margins of exactly 3). Two candidates, nothing else:

  M1-K  kernel-tilted empirical joint: draw the (margin, total) of a whole historical game j with weight
        K(s_j - s; 2.0) K(T_j - T; 4.0) 0.5^(seasons_ago / 3), exponentially tilted so the mean margin is exactly s
        and the mean total exactly T. Realized results keep their integer support and their own home/away parity;
        overtime is inside them. No key number is imposed.
  M1-S  the incumbent residual bank restricted to games whose closing spread is within 1.5 points of s (widened by
        0.5 until 150 games), otherwise identical.

Both return the incumbent's `game_draws` dict, so `simulate.simulate(..., game_draws=...)` uses them unchanged.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data as D
from . import script_v2 as V
from nfl_edge.pricing.game_env import ResidualBank, simulate_game

M1_VERSION = "sim-m1-1.0.0"
HISTORY_START = 2016
H_SPREAD, H_TOTAL, HALFLIFE, MIN_EFF_N = 2.0, 4.0, 3.0, 200
STRAT_HALF_WIDTH, STRAT_STEP, STRAT_MIN_N = 1.5, 0.5, 150
LADDER_OFFSETS = np.arange(-11, 11) + 0.5          # home-margin thresholds floor(s) + 0.5 + j, j = -11..10
TOTAL_OFFSETS = np.arange(-15, 15) + 0.5
LOG_FLOOR = 1e-4


def history(through_season: int, start: int = HISTORY_START, reg_only: bool = True) -> pd.DataFrame:
    """Completed games with a consensus closing spread and total, seasons start..through_season. Fitting uses regular
    season games only, exactly as the incumbent bank (`inputs.historical_bank`); evaluation passes reg_only=False."""
    g = D.schedule().to_pandas()
    g = g[(g["season"] >= start) & (g["season"] <= through_season) & g["result"].notna() & g["spread_line"].notna()
          & g["total_line"].notna()].copy()
    if reg_only:
        g = g[g["game_type"] == "REG"]
    return g[["game_id", "season", "week", "spread_line", "total_line", "result", "total", "overtime"]].reset_index(drop=True)


# ------------------------------------------------------------------------------------------- M1-K
def _tilt(w: np.ndarray, m: np.ndarray, t: np.ndarray, s: float, T: float, iters: int = 60) -> np.ndarray:
    """Exponential tilt of weights w so that the weighted means of m and t are exactly (s, T)."""
    X = np.column_stack([m - s, t - T]).astype(float)
    th = np.zeros(2)
    lw = np.log(np.maximum(w, 1e-300))
    for _ in range(iters):
        a = lw + X @ th
        q = np.exp(a - a.max()); q /= q.sum()
        g = q @ X
        if np.max(np.abs(g)) < 1e-10:
            break
        H = (X * q[:, None]).T @ X - np.outer(g, g) + 1e-9 * np.eye(2)
        step = np.linalg.solve(H, g)
        # damped Newton: never move more than 0.5 in natural units per step
        th -= step / max(1.0, np.max(np.abs(step)) / 0.5)
    a = lw + X @ th
    q = np.exp(a - a.max())
    return q / q.sum()


def kernel_weights(hist: pd.DataFrame, s: float, T: float, ref_season: int) -> tuple[np.ndarray, dict]:
    """M1-K weights over the historical games for a centre (s, T); bandwidths double until the effective sample
    reaches MIN_EFF_N."""
    sj = hist["spread_line"].to_numpy(float); Tj = hist["total_line"].to_numpy(float)
    rec = 0.5 ** ((ref_season - hist["season"].to_numpy(float)) / HALFLIFE)
    hs, ht = H_SPREAD, H_TOTAL
    for _ in range(8):
        w = np.exp(-0.5 * ((sj - s) / hs) ** 2) * np.exp(-0.5 * ((Tj - T) / ht) ** 2) * rec
        eff = w.sum() ** 2 / max((w ** 2).sum(), 1e-300)
        if eff >= MIN_EFF_N:
            break
        hs, ht = hs * 2, ht * 2
    q = _tilt(w, hist["result"].to_numpy(float), hist["total"].to_numpy(float), s, T)
    return q, {"h_spread": hs, "h_total": ht, "eff_n_before_tilt": float(eff), "eff_n": float(1.0 / (q ** 2).sum())}


def m1k_pmf(hist: pd.DataFrame, s: float, T: float, ref_season: int) -> dict:
    """Exact margin pmf of M1-K (the expectation of its draws)."""
    q, info = kernel_weights(hist, s, T, ref_season)
    m = hist["result"].to_numpy(int)
    vals, inv = np.unique(m, return_inverse=True)
    return {"margin": dict(zip(vals.tolist(), np.bincount(inv, weights=q).tolist())), "info": info, "weights": q}


def m1k_draws(hist: pd.DataFrame, s: float, T: float, ref_season: int, n: int, seed: int = 11) -> dict:
    q, info = kernel_weights(hist, s, T, ref_season)
    idx = np.random.default_rng(seed).choice(len(hist), size=n, p=q)
    margin = hist["result"].to_numpy(float)[idx]; total = hist["total"].to_numpy(float)[idx]
    return {"margin": margin, "total": total, "home": (total + margin) / 2.0, "away": (total - margin) / 2.0, "info": info}


# ------------------------------------------------------------------------------------------- M1-S / M0
def _bank(h: pd.DataFrame, ref_season: int, seed: int) -> ResidualBank:
    return ResidualBank(h["result"] - h["spread_line"], h["total"] - h["total_line"], h["season"], ref_season=ref_season,
                        spread_lines=h["spread_line"], total_lines=h["total_line"], overtime=h["overtime"].fillna(0).astype(int),
                        results=h["result"], halflife=3.0, rng=np.random.default_rng(seed))


def m0_draws(hist: pd.DataFrame, s: float, T: float, ref_season: int, n: int, seed: int = 11) -> dict:
    """The incumbent residual bank (as `inputs.historical_bank`, REG and POST games of the history)."""
    return simulate_game(s, T, _bank(hist, ref_season, seed), n=n)


def m1s_draws(hist: pd.DataFrame, s: float, T: float, ref_season: int, n: int, seed: int = 11) -> dict:
    hw = STRAT_HALF_WIDTH
    while True:
        sub = hist[np.abs(hist["spread_line"] - s) <= hw]
        if len(sub) >= STRAT_MIN_N or hw > 30:
            break
        hw += STRAT_STEP
    out = simulate_game(s, T, _bank(sub, ref_season, seed), n=n)
    out["info"] = {"half_width": hw, "n_games": int(len(sub))}
    return out


# ------------------------------------------------------------------------------------------- scoring
def _pmf_from_draws(m: np.ndarray) -> dict:
    vals, cnt = np.unique(np.asarray(m, int), return_counts=True)
    return dict(zip(vals.tolist(), (cnt / cnt.sum()).tolist()))


def score_game(pmf: dict, s: float, realized: float) -> dict:
    """Exact-margin log score and the spread-ladder Brier around the centre."""
    p_exact = max(pmf.get(int(realized), 0.0), LOG_FLOOR)
    ks = np.floor(s) + LADDER_OFFSETS
    vals = np.array(list(pmf.keys()), float); ps = np.array(list(pmf.values()), float)
    surv = np.array([ps[vals > k].sum() for k in ks])
    y = (realized > ks).astype(float)
    return {"log_score": float(np.log(p_exact)), "ladder_brier": float(np.mean((surv - y) ** 2)),
            "p_exact": float(pmf.get(int(realized), 0.0)), "mean": float((vals * ps).sum())}


def total_ladder_brier(totals: np.ndarray, T: float, realized: float) -> float:
    ks = np.floor(T) + TOTAL_OFFSETS
    t = np.asarray(totals, float)
    surv = np.array([np.mean(t > k) for k in ks])
    return float(np.mean((surv - (realized > ks)) ** 2))


def evaluate_season(Y: int, n: int = 40000, models=("M0", "M1-K", "M1-S")) -> pd.DataFrame:
    """Every completed game of season Y, each model fitted on 2016..Y-1 (strictly earlier seasons)."""
    hist = history(Y - 1)
    test = history(Y, start=Y, reg_only=False)
    rows = []
    for i, r in enumerate(test.itertuples()):
        s, T = float(r.spread_line), float(r.total_line)
        rec = {"game_id": r.game_id, "season": Y, "spread": s, "total_line": T, "margin": float(r.result), "total": float(r.total)}
        for mdl in models:
            if mdl == "M1-K":
                pk = m1k_pmf(hist, s, T, Y)
                d = m1k_draws(hist, s, T, Y, n, seed=11 + i)
                pmf = pk["margin"]
            else:
                d = (m0_draws if mdl == "M0" else m1s_draws)(hist, s, T, Y, n, seed=11 + i)
                pmf = _pmf_from_draws(d["margin"])
            sc = score_game(pmf, s, r.result)
            rec.update({f"{mdl}|{k}": v for k, v in sc.items()})
            rec[f"{mdl}|total_ladder_brier"] = total_ladder_brier(d["total"], T, r.total)
            rec[f"{mdl}|mean_total"] = float(np.mean(d["total"]))
            rec[f"{mdl}|coherent"] = bool(np.all(d["home"] + d["away"] == d["total"]) and np.all(d["home"] - d["away"] == d["margin"])
                                          and np.all(np.mod(d["home"], 1) == 0) and np.all(d["home"] >= 0) and np.all(d["away"] >= 0))
            cells = V.cell_index(d["margin"], d["total"], s, T)
            rec[f"{mdl}|cells"] = (np.bincount(cells.astype(np.int64), minlength=9) / len(cells)).tolist()
        rec["cell"] = V.CELLS.index(V.classify(float(r.result), float(r.total), s, T))
        rows.append(rec)
    return pd.DataFrame(rows)


def emergent_key_numbers(through_season: int = 2020, h: float = 2.0, z: float = 2.0) -> list:
    """|margin| values whose development frequency exceeds a Gaussian-smoothed version of the same histogram by
    more than z binomial standard errors. Reported, never imposed."""
    a = np.abs(history(through_season)["result"].to_numpy(int))
    n = len(a)
    support = np.arange(0, a.max() + 1)
    f = np.bincount(a, minlength=len(support)) / n
    K = np.exp(-0.5 * ((support[:, None] - support[None, :]) / h) ** 2)
    sm = (K @ f) / K.sum(axis=1)
    out = []
    for k in support:
        se = np.sqrt(max(sm[k] * (1 - sm[k]), 1e-12) / n)
        if f[k] - sm[k] > z * se:
            out.append({"abs_margin": int(k), "freq": float(f[k]), "smoothed": float(sm[k]), "z": float((f[k] - sm[k]) / se)})
    return out
