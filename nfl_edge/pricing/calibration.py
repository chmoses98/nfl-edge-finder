"""Post-hoc probability calibration for ladder rungs.

research/tail_calibration measured, on 1.4M rung-observations across 1,871 games, that the fitted families
are systematically overconfident in the low-probability region: rungs the model prices at 0.033 settle 0.023
of the time, rungs priced 0.072 settle 0.061. In absolute terms that is only about a point, but at those base
rates it is a 15-40% relative overstatement -- and it lands on exactly the long-shot rungs where the market
is itself already overpricing (research/efficiency_map). Uncorrected, the pricer would read the market's own
long-shot overpricing as an opportunity while being wrong in the same direction, only more so.

The correction is a monotone map from predicted to calibrated probability, fitted in logit space so it cannot
reorder rungs (a ladder that is monotone before calibration stays monotone after) and cannot leave [0,1].
"""
from __future__ import annotations

import numpy as np

EPS = 1e-6


def _logit(p):
    p = np.clip(np.asarray(p, float), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


class LadderCalibrator:
    """Piecewise-linear monotone recalibration of P(Y >= k), fitted in logit space.

    Fitted on (predicted, realised) pairs from a season the model did not train on. Knots are quantiles of
    the predicted logit, and the fitted values are forced non-decreasing, so the map is monotone by
    construction: rung ordering within a ladder is preserved and no probability escapes (0, 1).
    """

    def __init__(self, n_knots: int = 12, min_per_bin: int = 400):
        self.n_knots = n_knots
        self.min_per_bin = min_per_bin
        self.knots_ = None
        self.values_ = None
        self.n_fit_ = 0

    def fit(self, p_pred, y):
        p_pred = np.asarray(p_pred, float); y = np.asarray(y, float)
        m = np.isfinite(p_pred) & np.isfinite(y)
        p_pred, y = p_pred[m], y[m]
        self.n_fit_ = len(y)
        if self.n_fit_ < self.min_per_bin * 3:
            self.knots_ = None
            return self
        z = _logit(p_pred)
        qs = np.linspace(0, 1, self.n_knots + 1)
        edges = np.unique(np.quantile(z, qs))
        if len(edges) < 4:
            self.knots_ = None
            return self
        idx = np.clip(np.digitize(z, edges[1:-1]), 0, len(edges) - 2)
        centres, rates = [], []
        for b in range(len(edges) - 1):
            sel = idx == b
            if sel.sum() < self.min_per_bin:
                continue
            centres.append(float(z[sel].mean()))
            rates.append(float(np.clip(y[sel].mean(), EPS, 1 - EPS)))
        if len(centres) < 3:
            self.knots_ = None
            return self
        # monotone by pool-adjacent-violators on the realised rates
        r = np.array(rates, float); w = np.ones(len(r))
        i = 0
        while i < len(r) - 1:
            if r[i] <= r[i + 1] + 1e-12:
                i += 1
                continue
            new = (r[i] * w[i] + r[i + 1] * w[i + 1]) / (w[i] + w[i + 1])
            r = np.concatenate([r[:i], [new], r[i + 2:]])
            w = np.concatenate([w[:i], [w[i] + w[i + 1]], w[i + 2:]])
            centres = centres[:i] + [centres[i]] + centres[i + 2:]
            i = max(i - 1, 0)
        self.knots_ = np.array(centres, float)
        self.values_ = _logit(r)
        return self

    def transform(self, p_pred):
        p_pred = np.asarray(p_pred, float)
        if self.knots_ is None or len(self.knots_) < 2:
            return p_pred
        z = _logit(p_pred)
        # linear interpolation between knots; beyond the ends, shift by the end offset rather than
        # extrapolating a slope, so a rung far outside the fitted range is nudged, never inverted
        out = np.interp(z, self.knots_, self.values_)
        lo, hi = self.knots_[0], self.knots_[-1]
        out = np.where(z < lo, z + (self.values_[0] - lo), out)
        out = np.where(z > hi, z + (self.values_[-1] - hi), out)
        return _sigmoid(out)

    def to_json(self):
        return {"n_fit": int(self.n_fit_),
                "knots": None if self.knots_ is None else [float(x) for x in self.knots_],
                "values": None if self.values_ is None else [float(x) for x in self.values_]}
