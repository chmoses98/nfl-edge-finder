"""Structural serve/return model: point-level abilities with hierarchical shrinkage, fitted chronologically.

For each player we maintain shrunken running estimates of
    serve_ability  s_i = logit(P(win point on own serve)) deviation from the tour/surface baseline
    return_ability r_i = logit(P(win point on return))     deviation from the baseline
using the match serve statistics in Sackmann (w_svpt, w_1stWon, w_2ndWon, l_svpt, ...), which exist for
tour-level (and many Challenger) matches but NOT for ITF/futures. Every observation is opponent-adjusted:
a server's realised point rate is compared with what the opponent's return ability predicted, so a hold-
heavy match against a weak returner is not credited as strong serving.

Prediction for A vs B on surface S:
    logit p_A_serve = base_S + s_A - r_B
    logit p_B_serve = base_S + s_B - r_A
then (pa, pb) = (p_A_serve, 1 - p_B_serve) feed tennis_edge.sim.analytic for the whole distribution.

Shrinkage: ability = (sum of point-weighted opponent-adjusted excess) / (points observed + n_prior_points),
i.e. a precision-weighted mean with a zero-mean prior worth n_prior_points serve points. Time decay
multiplies old evidence by exp(-days/tau). Everything is updated in match order so the estimate used to
predict a match uses only matches completed before it.

For players/matches WITHOUT serve statistics (ITF, most WTA lower levels, doubles) the model has no
evidence and returns the baseline (abilities 0); the data_quality score records points_seen so the caller
can fall back to the Elo-implied point probabilities (point_probs_from_match_prob).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd

from tennis_edge.models.elo import match_sort_key


def logit(p):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


@dataclass
class SRConfig:
    n_prior_points: float = 600.0     # ~ 8 matches of serve points before the data dominates the prior
    tau_days: float = 365.0           # exponential evidence decay scale
    min_points_for_estimate: int = 200


class ServeReturnModel:
    def __init__(self, cfg: SRConfig = SRConfig()):
        self.cfg = cfg
        self.s_num = {}; self.s_den = {}; self.r_num = {}; self.r_den = {}; self.last = {}
        self.base_num = {}; self.base_den = {}

    def _decay(self, p, date):
        if p in self.last and date is not None and self.last[p] is not None:
            days = (date - self.last[p]).days
            if days > 0:
                f = math.exp(-days / self.cfg.tau_days)
                for d in (self.s_num, self.s_den, self.r_num, self.r_den):
                    if p in d:
                        d[p] *= f
        self.last[p] = date

    def baseline(self, tour, surface):
        key = (tour, surface)
        den = self.base_den.get(key, 0.0)
        if den < 2000:
            tden = sum(v for (t, s), v in self.base_den.items() if t == tour)
            if tden >= 2000:
                return sum(v for (t, s), v in self.base_num.items() if t == tour) / tden
            return 0.64 if tour == "ATP" else 0.57
        return self.base_num[key] / den

    def abilities(self, p):
        s = self.s_num.get(p, 0.0) / (self.s_den.get(p, 0.0) + self.cfg.n_prior_points)
        r = self.r_num.get(p, 0.0) / (self.r_den.get(p, 0.0) + self.cfg.n_prior_points)
        return s, r

    def points_seen(self, p):
        return self.s_den.get(p, 0.0) + self.r_den.get(p, 0.0)

    def predict(self, a, b, tour, surface):
        base = logit(self.baseline(tour, surface))
        sa, ra = self.abilities(a); sb, rb = self.abilities(b)
        pa = sigmoid(base + sa - rb)
        pb_serve = sigmoid(base + sb - ra)
        return pa, 1 - pb_serve

    @staticmethod
    def _num(x):
        try:
            if x is None or pd.isna(x):
                return None
            return float(x)
        except (TypeError, ValueError):
            return None

    def update(self, rec):
        for side in ("w", "l"):
            pid = rec.winner_id if side == "w" else rec.loser_id
            oid = rec.loser_id if side == "w" else rec.winner_id
            svpt = self._num(getattr(rec, f"{side}_svpt")); w1 = self._num(getattr(rec, f"{side}_1stWon")); w2 = self._num(getattr(rec, f"{side}_2ndWon"))
            if svpt is None or w1 is None or w2 is None or svpt < 20:
                continue
            won = w1 + w2
            if won > svpt:
                continue
            rate = min(max(won / svpt, 0.02), 0.98)
            base = logit(self.baseline(rec.tour, rec.surface))
            s_p, _ = self.abilities(pid); _, r_o = self.abilities(oid)
            excess = logit(rate) - (base + s_p - r_o)
            self.s_num[pid] = self.s_num.get(pid, 0.0) + svpt * (s_p + excess)
            self.s_den[pid] = self.s_den.get(pid, 0.0) + svpt
            self.r_num[oid] = self.r_num.get(oid, 0.0) + svpt * (r_o - excess)
            self.r_den[oid] = self.r_den.get(oid, 0.0) + svpt
            key = (rec.tour, rec.surface)
            self.base_num[key] = self.base_num.get(key, 0.0) + won
            self.base_den[key] = self.base_den.get(key, 0.0) + svpt

    def run(self, matches: pd.DataFrame) -> pd.DataFrame:
        rows = []
        m = match_sort_key(matches)
        for rec in m.itertuples(index=False):
            w, l = rec.winner_id, rec.loser_id
            self._decay(w, rec.tourney_date); self._decay(l, rec.tourney_date)
            pa, pb = self.predict(w, l, rec.tour, rec.surface)
            rows.append((rec.match_key, pa, pb, self.points_seen(w), self.points_seen(l)))
            if rec.outcome_type != "WALKOVER":
                self.update(rec)
        return pd.DataFrame(rows, columns=["match_key", "pa", "pb", "pts_w", "pts_l"])
