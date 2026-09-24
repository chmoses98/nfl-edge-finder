"""Small, transparent estimators used by every V4 component: ridge least squares and a ridge Poisson GLM.

Standardised features, unpenalised intercept, one fixed penalty (no search). Coefficients are readable and are
written into the fitted bundle's summary so a reader can see what each component learned.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

RIDGE = 1.0


def matrix(df: pd.DataFrame, cols: list) -> np.ndarray:
    """Design matrix; a NaN feature becomes the column's training mean at fit time (see `Linear.fit`) -- never 0."""
    return np.column_stack([df[c].to_numpy(float) for c in cols]) if cols else np.zeros((len(df), 0))


@dataclass
class Linear:
    cols: list
    beta: np.ndarray
    mu: np.ndarray
    sd: np.ndarray
    kind: str = "ols"            # ols | poisson

    @classmethod
    def fit(cls, df: pd.DataFrame, cols: list, y, kind: str = "ols", ridge: float = RIDGE, weights=None) -> "Linear":
        X = matrix(df, cols)
        mu = np.nanmean(X, axis=0) if X.shape[1] else np.zeros(0)
        mu = np.nan_to_num(mu, nan=0.0)
        X = np.where(np.isfinite(X), X, mu)
        sd = X.std(axis=0) if X.shape[1] else np.zeros(0)
        sd[sd < 1e-9] = 1.0
        Xs = np.column_stack([np.ones(len(X)), (X - mu) / sd])
        y = np.asarray(y, float)
        w = np.ones(len(y)) if weights is None else np.asarray(weights, float)
        pen = ridge * np.eye(Xs.shape[1]); pen[0, 0] = 0.0
        if kind == "ols":
            XtW = Xs.T * w
            beta = np.linalg.solve(XtW @ Xs + pen, XtW @ y)
        else:
            beta = np.zeros(Xs.shape[1]); beta[0] = np.log(max(np.average(y, weights=w), 1e-3))
            for _ in range(80):
                eta = np.clip(Xs @ beta, -20, 8); m = np.exp(eta)
                z = eta + (y - m) / m
                XtW = Xs.T * (w * m)
                new = np.linalg.solve(XtW @ Xs + pen, XtW @ z)
                if np.max(np.abs(new - beta)) < 1e-8:
                    beta = new; break
                beta = new
        return cls(list(cols), beta, mu, sd, kind)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        X = matrix(df, self.cols)
        X = np.where(np.isfinite(X), X, self.mu)
        eta = self.beta[0] + ((X - self.mu) / self.sd) @ self.beta[1:] if len(self.cols) else np.full(len(df), self.beta[0])
        return eta if self.kind == "ols" else np.exp(np.clip(eta, -20, 8))

    def coefficients(self) -> dict:
        """Per-unit (unstandardised) coefficients, for the bundle summary."""
        b = self.beta[1:] / self.sd
        return {"intercept": float(self.beta[0] - (b * self.mu).sum()), **{c: float(v) for c, v in zip(self.cols, b)}}
