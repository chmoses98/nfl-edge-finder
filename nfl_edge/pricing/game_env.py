"""Market-as-prior joint game environment (MODEL B for game markets).

Given a market-implied home margin `s` (home − away) and total `t`, draw joint (margin, total) outcomes by adding
jointly-sampled historical residual pairs (recency-weighted, so score-variance drift is respected and the
margin/total correlation and key-number mass are preserved). Home/away scores follow as (t±m)/2, so every
derivative market — winner, spread ladder, total ladder, team totals, winning-margin buckets, both-teams-score-N,
race-to-N (approximate), tie — is priced from ONE coherent distribution and cannot contradict itself.
"""
from __future__ import annotations
import numpy as np


class ResidualBank:
    """Joint residual pairs (margin − spread, total − total_line) from settled games, season-weighted
    0.5**(seasons_ago/halflife). Residuals are sampled from games whose spread and total line share the *fractional
    part* of the target lines, so simulated margins/totals stay integer-valued (a half-point residual added to an
    integer spread would otherwise create impossible x.5 margins and dilute key-number mass). Regulation ties in the
    simulation are resolved with an overtime model estimated from historical OT games (tie probability, OT margin,
    OT points), because the residual histogram carries no "hole" at margin 0 the way real outcomes do."""
    def __init__(self, margin_resid, total_resid, seasons, ref_season, spread_lines=None, total_lines=None, overtime=None,
                 results=None, halflife=3.0, rng=None):
        self.m = np.asarray(margin_resid, float); self.t = np.asarray(total_resid, float)
        w = 0.5 ** ((ref_season - np.asarray(seasons, float)) / halflife)
        self.w = w / w.sum()
        self.rng = rng or np.random.default_rng(0)
        self.sfrac = (np.asarray(spread_lines, float) % 1 != 0) if spread_lines is not None else None
        self.tfrac = (np.asarray(total_lines, float) % 1 != 0) if total_lines is not None else None
        # overtime model
        if overtime is not None and results is not None:
            ot = np.asarray(overtime).astype(bool); r = np.asarray(results, float)
            self.p_tie_given_ot = float(np.mean(r[ot] == 0)) if ot.sum() else 0.05
            nz = np.abs(r[ot][r[ot] != 0])
            self.ot_abs_margin = nz if len(nz) else np.array([3.0, 3.0, 6.0, 7.0])
        else:
            self.p_tie_given_ot, self.ot_abs_margin = 0.05, np.array([3.0, 3.0, 6.0, 7.0])

    def sample(self, n, spread=None, total=None):
        w = self.w.copy()
        if spread is not None and self.sfrac is not None:
            w = w * (self.sfrac == (float(spread) % 1 != 0))
        if total is not None and self.tfrac is not None:
            w2 = w * (self.tfrac == (float(total) % 1 != 0))
            if w2.sum() > 0:
                w = w2
        if w.sum() == 0:
            w = self.w
        w = w / w.sum()
        idx = self.rng.choice(len(self.m), size=n, p=w)
        return self.m[idx], self.t[idx]


def simulate_game(spread_home, total_line, bank: ResidualBank, n=20000):
    dm, dt = bank.sample(n, spread=spread_home, total=total_line)
    margin = np.round(spread_home + dm)
    total = np.round(total_line + dt)
    # overtime resolution for regulation ties
    tied = margin == 0
    k = int(tied.sum())
    if k:
        stays_tied = bank.rng.random(k) < bank.p_tie_given_ot
        otm = bank.rng.choice(bank.ot_abs_margin, size=k)
        p_home = 1.0 / (1.0 + np.exp(-spread_home / 6.0))       # side that was favoured is likelier to win OT
        sign = np.where(bank.rng.random(k) < p_home, 1.0, -1.0)
        new_m = np.where(stays_tied, 0.0, sign * otm)
        margin[tied] = new_m
        total[tied] = total[tied] + np.where(stays_tied, 0.0, otm)
    # parity: home+away must be integers -> total and margin must share parity; fix by nudging total by 1 where needed
    odd = (total + margin) % 2 != 0
    total = total + odd * np.where(bank.rng.random(n) < 0.5, 1.0, -1.0)
    home = (total + margin) / 2.0
    away = (total - margin) / 2.0
    return {"margin": margin, "total": total, "home": home, "away": away}


def price_game_markets(sim, home_code, away_code):
    """Return dict of probabilities for standard derivative markets (keys mirror the classifier semantics)."""
    m, t, h, a = sim["margin"], sim["total"], sim["home"], sim["away"]
    out = {"home_win": float(np.mean(m > 0)), "away_win": float(np.mean(m < 0)), "tie": float(np.mean(m == 0))}
    for k in range(1, 22):
        out[f"spread_{home_code}_over_{k - 0.5}"] = float(np.mean(m > k - 0.5))
        out[f"spread_{away_code}_over_{k - 0.5}"] = float(np.mean(-m > k - 0.5))
    for k in range(25, 76):
        out[f"total_ge_{k}"] = float(np.mean(t >= k))
    for k in range(3, 60):
        out[f"teamtotal_{home_code}_ge_{k}"] = float(np.mean(h >= k))
        out[f"teamtotal_{away_code}_ge_{k}"] = float(np.mean(a >= k))
    for lo, hi in ((1, 6), (7, 14), (15, None)):
        hi_ = np.inf if hi is None else hi
        out[f"margin_{home_code}_{lo}_{hi}"] = float(np.mean((m >= lo) & (m <= hi_)))
        out[f"margin_{away_code}_{lo}_{hi}"] = float(np.mean((-m >= lo) & (-m <= hi_)))
    for k in (14, 17, 21, 24, 28, 35):
        out[f"both_ge_{k}"] = float(np.mean((h >= k) & (a >= k)))
    return out
