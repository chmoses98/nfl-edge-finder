"""Forecast distributions for PURE_PLAYER_V1 and its EWM baseline (identical machinery for both arms).

    NBDist     counts: negative binomial around the forecast mean, one dispersion r by maximum likelihood
    RatioDist  yards: Y = mu * R, R drawn from the training distribution of actual / predicted inside five
               predicted-mean bins (quantiles scale exactly: q_p(mu R) = mu q_p(R) for mu > 0)
    ResidDist  snap share: Y = clip(mu + E, 0, 1), E from training residuals inside five predicted-mean bins

Every summary is a mean, a median, p10 / p90 and P(Y >= k) on a fixed ladder; survival is non-increasing in k by
construction, so the thresholds are monotone.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize, special, stats

NBINS = 5
QGRID = np.linspace(0.0025, 0.9975, 200)


def _frame(mean, median, p10, p90, surv: np.ndarray, ladder) -> pd.DataFrame:
    f = pd.DataFrame({"mean": mean, "median": median, "p10": p10, "p90": p90})
    f["thresholds"] = [list(zip(ladder, np.minimum.accumulate(np.clip(row, 0.0, 1.0)))) for row in surv]
    return f


class NBDist:
    def __init__(self, r: float):
        self.r = float(r)

    @classmethod
    def fit(cls, y, mu) -> "NBDist":
        y = np.asarray(y, float); mu = np.maximum(np.asarray(mu, float), 1e-3)

        def nll(logr):
            r = np.exp(logr)
            ll = (special.gammaln(y + r) - special.gammaln(r) - special.gammaln(y + 1)
                  + r * np.log(r / (r + mu)) + y * np.log(mu / (r + mu)))
            return -ll.sum()
        res = optimize.minimize_scalar(nll, bounds=(np.log(0.2), np.log(1000.0)), method="bounded")
        return cls(float(np.exp(res.x)))

    def summarize(self, mu, ladder) -> pd.DataFrame:
        mu = np.maximum(np.asarray(mu, float), 1e-3)
        p = self.r / (self.r + mu)
        surv = np.column_stack([stats.nbinom.sf(k - 1, self.r, p) for k in ladder])
        return _frame(mu, stats.nbinom.ppf(0.5, self.r, p), stats.nbinom.ppf(0.1, self.r, p), stats.nbinom.ppf(0.9, self.r, p),
                      surv, ladder)


class _Binned:
    floor = 0.0

    def __init__(self, edges, banks):
        self.edges, self.banks = np.asarray(edges, float), [np.sort(np.asarray(b, float)) for b in banks]

    @classmethod
    def _bins(cls, mu):
        qs = np.quantile(mu, np.linspace(0, 1, NBINS + 1)[1:-1])
        return np.unique(qs)

    def _bin(self, mu):
        return np.searchsorted(self.edges, mu, side="right")


class RatioDist(_Binned):
    floor = 1.0

    @classmethod
    def fit(cls, y, mu) -> "RatioDist":
        mu = np.maximum(np.asarray(mu, float), cls.floor)
        r = np.asarray(y, float) / mu
        edges = cls._bins(mu)
        b = np.searchsorted(edges, mu, side="right")
        return cls(edges, [r[b == i] if (b == i).sum() >= 20 else r for i in range(len(edges) + 1)])

    def summarize(self, mu, ladder) -> pd.DataFrame:
        mu = np.maximum(np.asarray(mu, float), self.floor)
        b = self._bin(mu)
        n = len(mu)
        mean = np.empty(n); med = np.empty(n); p10 = np.empty(n); p90 = np.empty(n); surv = np.empty((n, len(ladder)))
        for i, bank in enumerate(self.banks):
            ix = np.where(b == i)[0]
            if not len(ix):
                continue
            m = mu[ix]
            q10, q50, q90 = np.quantile(bank, [0.1, 0.5, 0.9])
            mean[ix], med[ix], p10[ix], p90[ix] = m * bank.mean(), m * q50, m * q10, m * q90
            for j, k in enumerate(ladder):
                surv[ix, j] = 1.0 - np.searchsorted(bank, k / m, side="left") / len(bank)
        return _frame(mean, med, p10, p90, surv, ladder)


class ResidDist(_Binned):
    @classmethod
    def fit(cls, y, mu) -> "ResidDist":
        mu = np.asarray(mu, float); e = np.asarray(y, float) - mu
        edges = cls._bins(mu)
        b = np.searchsorted(edges, mu, side="right")
        return cls(edges, [e[b == i] if (b == i).sum() >= 20 else e for i in range(len(edges) + 1)])

    def summarize(self, mu, ladder) -> pd.DataFrame:
        mu = np.asarray(mu, float)
        b = self._bin(mu)
        n = len(mu)
        mean = np.empty(n); med = np.empty(n); p10 = np.empty(n); p90 = np.empty(n); surv = np.empty((n, len(ladder)))
        for i, bank in enumerate(self.banks):
            ix = np.where(b == i)[0]
            if not len(ix):
                continue
            m = mu[ix]
            qg = np.quantile(bank, QGRID)
            mean[ix] = np.clip(m[:, None] + qg[None, :], 0, 1).mean(axis=1)
            q10, q50, q90 = np.quantile(bank, [0.1, 0.5, 0.9])
            med[ix], p10[ix], p90[ix] = np.clip(m + q50, 0, 1), np.clip(m + q10, 0, 1), np.clip(m + q90, 0, 1)
            for j, k in enumerate(ladder):
                surv[ix, j] = 1.0 - np.searchsorted(bank, k - m, side="left") / len(bank)
        return _frame(mean, med, p10, p90, surv, ladder)
