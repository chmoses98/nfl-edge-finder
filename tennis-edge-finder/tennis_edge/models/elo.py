"""Chronological Elo family: standard, surface-specific (partially pooled), recency/experience-aware K,
level-aware. All ratings are updated strictly in match order; the rating used to PREDICT a match is the
rating BEFORE that match is applied (no leakage by construction: `run()` yields the prediction row before
the update).

Match order: (tourney_date, tourney_id, round order, match_num). Sackmann gives the tournament START
date only, so within a tournament the round order is the chronological key; different tournaments in the
same week are interleaved by date then id, which is a documented approximation (matches from two
simultaneous tournaments cannot influence each other within the week anyway, except through players who
cannot be in both).

Design choices (empirically checked in scripts/research/elo_study.py):
  * K = k0 / (n + offset)^shape (FiveThirtyEight-style), so new players move fast and veterans slowly.
  * Surface rating = pooled blend: r_surface_eff = (1-w) * r_overall + w * r_surface, with w shrinking
    toward 0 when the player has few matches on that surface: w = w_max * n_s / (n_s + n_half).
  * Level offsets: a player's rating carries across levels; cross-level 'translation' is learned by
    the matches themselves (Challenger vs tour players meet in qualifying / early rounds), and the
    level-aware variant adds a fitted per-level margin adjustment to K (lower levels are noisier).
  * Retirements: counted at reduced weight (default 0.5), walkovers ignored, per `outcome_type`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np
import pandas as pd

ROUND_ORDER = {"Q1": 0, "Q2": 1, "Q3": 2, "R128": 3, "R64": 4, "R32": 5, "R16": 6, "QF": 7, "SF": 8, "F": 9, "RR": 5, "BR": 8, "ER": 3}


def match_sort_key(df: pd.DataFrame) -> pd.DataFrame:
    """Return df sorted chronologically with a stable within-tournament round order."""
    r = df["round"].map(lambda x: ROUND_ORDER.get(str(x), 5))
    out = df.assign(_r=r)
    out = out.sort_values(["tourney_date", "tourney_id", "_r", "match_num"], kind="mergesort").drop(columns="_r")
    return out.reset_index(drop=True)


@dataclass
class EloConfig:
    k0: float = 250.0
    offset: float = 5.0
    shape: float = 0.4
    initial: float = 1500.0
    surface_w_max: float = 0.5      # weight on the surface-specific rating when well-sampled
    surface_n_half: float = 20.0    # matches on surface at which w reaches half of w_max
    retirement_weight: float = 0.5
    level_k_mult: dict = field(default_factory=lambda: {"GRAND_SLAM": 1.1, "MASTERS_1000": 1.0, "TOUR_FINALS": 1.0, "TOUR_500_250": 1.0,
                                                        "OLYMPICS": 1.0, "TEAM": 0.9, "CHALLENGER": 0.9, "WTA_125": 0.9, "ITF": 0.8, "OTHER": 0.8})
    use_surface: bool = True
    use_level_k: bool = True
    # tour-level prior: a player's first rating depends on the level they first appear at (documented prior, not fitted here)
    level_prior: dict = field(default_factory=lambda: {"GRAND_SLAM": 1550.0, "MASTERS_1000": 1550.0, "TOUR_500_250": 1500.0, "TOUR_FINALS": 1600.0,
                                                       "OLYMPICS": 1500.0, "TEAM": 1450.0, "CHALLENGER": 1400.0, "WTA_125": 1400.0, "ITF": 1300.0, "OTHER": 1350.0})
    use_level_prior: bool = True


def expected(ra: float, rb: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))


class Elo:
    def __init__(self, cfg: EloConfig = EloConfig()):
        self.cfg = cfg
        self.r: dict = {}           # player -> overall rating
        self.n: dict = {}           # player -> matches played
        self.rs: dict = {}          # (player, surface) -> surface rating
        self.ns: dict = {}          # (player, surface) -> matches on surface
        self.last_date: dict = {}

    def _init(self, p, level):
        if p not in self.r:
            self.r[p] = self.cfg.level_prior.get(level, self.cfg.initial) if self.cfg.use_level_prior else self.cfg.initial
            self.n[p] = 0

    def rating(self, p, surface=None, level=None) -> float:
        self._init(p, level)
        r = self.r[p]
        if self.cfg.use_surface and surface:
            key = (p, surface)
            rs = self.rs.get(key, r)
            ns = self.ns.get(key, 0)
            w = self.cfg.surface_w_max * ns / (ns + self.cfg.surface_n_half)
            return (1 - w) * r + w * rs
        return r

    def k(self, p, level) -> float:
        k = self.cfg.k0 / (self.n[p] + self.cfg.offset) ** self.cfg.shape
        if self.cfg.use_level_k:
            k *= self.cfg.level_k_mult.get(level, 1.0)
        return k

    def predict(self, a, b, surface=None, level=None) -> float:
        return expected(self.rating(a, surface, level), self.rating(b, surface, level))

    def update(self, winner, loser, surface=None, level=None, weight: float = 1.0, date=None):
        self._init(winner, level); self._init(loser, level)
        pw = self.predict(winner, loser, surface, level)
        kw, kl = self.k(winner, level), self.k(loser, level)
        self.r[winner] += weight * kw * (1 - pw)
        self.r[loser] -= weight * kl * (1 - pw)
        if self.cfg.use_surface and surface:
            for p, sgn, kk in ((winner, 1, kw), (loser, -1, kl)):
                key = (p, surface)
                self.rs.setdefault(key, self.r[p])
                self.rs[key] += sgn * weight * kk * (1 - pw)
                self.ns[key] = self.ns.get(key, 0) + 1
        self.n[winner] += 1; self.n[loser] += 1
        if date is not None:
            self.last_date[winner] = date; self.last_date[loser] = date

    def run(self, matches: pd.DataFrame, predict_mask=None) -> pd.DataFrame:
        """Replay matches chronologically. Returns one row per match with the PRE-match prediction.

        Columns: match_key, p_winner (prob assigned to the actual winner BEFORE the match), r_w, r_l,
        n_w, n_l (experience before the match), surface, level_canonical, tourney_date.
        """
        rows = []
        m = match_sort_key(matches)
        for rec in m.itertuples(index=False):
            w, l = rec.winner_id, rec.loser_id
            surface, level = rec.surface, rec.level_canonical
            self._init(w, level); self._init(l, level)
            p = self.predict(w, l, surface, level)
            rows.append((rec.match_key, p, self.rating(w, surface, level), self.rating(l, surface, level), self.n[w], self.n[l],
                         surface, level, rec.tourney_date, rec.tour))
            ot = rec.outcome_type
            if ot == "WALKOVER":
                continue
            weight = self.cfg.retirement_weight if ot in ("RETIRED", "DEFAULT") else 1.0
            self.update(w, l, surface, level, weight, rec.tourney_date)
        return pd.DataFrame(rows, columns=["match_key", "p_winner", "r_w", "r_l", "n_w", "n_l", "surface", "level_canonical", "tourney_date", "tour"])
