"""Common-random-number game simulation: the same residual draws applied to three different centres.

`nfl_edge.pricing.game_env.simulate_game` draws residual indices with `rng.choice(p=w)` and then consumes the
generator again for overtime and parity. Two calls with two centres therefore differ by Monte Carlo noise as
well as by the centre, and with 40,000 draws that noise is about +-0.5 probability points on a coin-flip
contract -- the same order as a small real centre difference. This module removes it.

Every random quantity the incumbent simulator consumes is drawn ONCE per (snapshot, game) as a uniform, and
each arm is simulated by pushing the SAME uniforms through the incumbent's own logic:

    residual index   inverse-CDF of the bank's weights at u_idx        (rng.choice(p=w) is inverse-CDF too)
    OT stays tied    u_tie  < p_tie_given_ot
    OT margin        ot_abs_margin[floor(u_otm * len)]                  (rng.choice without p is uniform)
    OT winner        u_side < sigmoid(spread / 6)
    parity nudge     u_parity < 0.5

The bank's weights depend on the fractional part of the centre (a half-point line samples half-point residuals
so simulated margins stay integers), so two arms whose centres sit in different fractional classes draw the
same QUANTILE of two different weight vectors rather than the same residual. That is the maximal coupling the
incumbent's own structure permits, and it is why challenger centres are placed on the half-point grid: the
fractional class is then explicit and recorded. When the classes agree the residual arrays are bitwise equal.

The incumbent's `simulate_game` is not modified and not called here; it is reproduced. `tests/test_three_arm_crn.py`
proves the reproduction is Monte Carlo-equivalent on a shared bank.
"""
from __future__ import annotations

import hashlib

import numpy as np


def residual_weights(bank, spread, total) -> np.ndarray:
    """Exactly the weight vector `ResidualBank.sample` would use for this (spread, total)."""
    w = bank.w.copy()
    if spread is not None and bank.sfrac is not None:
        w = w * (bank.sfrac == (float(spread) % 1 != 0))
    if total is not None and bank.tfrac is not None:
        w2 = w * (bank.tfrac == (float(total) % 1 != 0))
        if w2.sum() > 0:
            w = w2
    if w.sum() == 0:
        w = bank.w
    return w / w.sum()


def seed_from_key(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")


def draw_uniforms(n: int, key: str) -> dict:
    """One set of uniforms per (snapshot, game): deterministic from the key, shared by every arm."""
    rng = np.random.default_rng(seed_from_key(key))
    u = {"u_idx": rng.random(n), "u_tie": rng.random(n), "u_otm": rng.random(n),
         "u_side": rng.random(n), "u_parity": rng.random(n)}
    u["sha"] = hashlib.sha256(b"".join(u[k].tobytes() for k in ("u_idx", "u_tie", "u_otm", "u_side", "u_parity"))).hexdigest()[:16]
    u["key"] = key
    u["n"] = n
    return u


def residual_indices(bank, spread, total, u_idx: np.ndarray) -> np.ndarray:
    w = residual_weights(bank, spread, total)
    cdf = np.cumsum(w)
    cdf[-1] = 1.0
    return np.minimum(np.searchsorted(cdf, u_idx, side="right"), len(w) - 1)


def simulate_game_crn(spread_home: float, total_line: float, bank, draws: dict) -> dict:
    """The incumbent's simulate_game, step for step, driven by pre-drawn uniforms instead of the bank's rng."""
    n = int(draws["n"])
    idx = residual_indices(bank, spread_home, total_line, draws["u_idx"])
    dm, dt = bank.m[idx], bank.t[idx]
    margin = np.round(spread_home + dm)
    total = np.round(total_line + dt)
    tied = margin == 0
    k = int(tied.sum())
    if k:
        stays_tied = draws["u_tie"][tied] < bank.p_tie_given_ot
        otm = bank.ot_abs_margin[np.minimum((draws["u_otm"][tied] * len(bank.ot_abs_margin)).astype(int),
                                            len(bank.ot_abs_margin) - 1)]
        p_home = 1.0 / (1.0 + np.exp(-spread_home / 6.0))
        sign = np.where(draws["u_side"][tied] < p_home, 1.0, -1.0)
        new_m = np.where(stays_tied, 0.0, sign * otm)
        margin[tied] = new_m
        total[tied] = total[tied] + np.where(stays_tied, 0.0, otm)
    odd = (total + margin) % 2 != 0
    total = total + odd * np.where(draws["u_parity"] < 0.5, 1.0, -1.0)
    home = (total + margin) / 2.0
    away = (total - margin) / 2.0
    return {"margin": margin, "total": total, "home": home, "away": away, "residual_idx": idx,
            "fractional_class": (float(spread_home) % 1 != 0, float(total_line) % 1 != 0)}


def sim_summary(sim: dict) -> dict:
    m, t = sim["margin"], sim["total"]
    return {"p_home_win": float(np.mean(m > 0)), "p_away_win": float(np.mean(m < 0)), "p_tie": float(np.mean(m == 0)),
            "mean_margin": float(m.mean()), "sd_margin": float(m.std()),
            "mean_total": float(t.mean()), "sd_total": float(t.std()),
            "mean_home": float(sim["home"].mean()), "mean_away": float(sim["away"].mean())}


def bank_fingerprint(bank, *, seasons_lo=None, seasons_hi=None, halflife=None, extra: dict | None = None) -> dict:
    """Identity of the residual population an arm was simulated from, so an evaluation can name it."""
    h = hashlib.sha256()
    h.update(np.asarray(bank.m, float).tobytes()); h.update(np.asarray(bank.t, float).tobytes())
    h.update(np.asarray(bank.w, float).tobytes())
    return {"bank_sha": h.hexdigest()[:16], "n_pairs": int(len(bank.m)),
            "seasons": [seasons_lo, seasons_hi], "halflife_seasons": halflife,
            "p_tie_given_ot": float(bank.p_tie_given_ot), **(extra or {})}


def snap_to_grid(x: float, grid: float = 0.5) -> float:
    """Place a continuous centre on the half-point line grid the residual bank keys on (nearest; ties up)."""
    return float(np.floor(float(x) / grid + 0.5) * grid)
