"""Fitted model bundle used to price a prospective slate: game environment + player distributions.

Everything is fitted on seasons STRICTLY BEFORE the target season, then frozen and hashed. The bundle records
its own version and artifact hash so every ledger row can be traced to the exact code+data that produced it.

Player statistics use the families chosen by research/player_distributions (walk-forward, 2020-2025) EXCEPT
anytime touchdown, which that study showed is mis-served by a count family (it under-predicts the 1+ rung by
2-3 points). A direct binary model is fitted here and is compared against the count family in
scripts/research/anytime_td_study.py before being used.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from nfl_edge.research import player_distributions as pdist

# statistic -> family chosen by the walk-forward distribution study
CHOSEN_FAMILY = {
    "attempts": "normal", "completions": "normal", "passing_yards": "normal", "passing_tds": "poisson",
    "interceptions": "negbin", "qb_rushing_yards": "scale_emp_binned", "targets": "negbin",
    "receptions": "negbin", "receiving_yards": "scale_emp_binned", "receiving_tds": "negbin",
    "carries": "negbin", "rushing_yards": "scale_emp_binned", "rushing_tds": "negbin",
    "anytime_td": "direct_binary",
}
# Kalshi stat name -> internal StatSpec name, per position population
KALSHI_STAT_TO_SPEC = {
    ("passing_yards", "QB"): "passing_yards", ("attempts", "QB"): "attempts", ("completions", "QB"): "completions",
    ("passing_tds", "QB"): "passing_tds", ("interceptions", "QB"): "interceptions",
    ("receiving_yards", None): "receiving_yards", ("receptions", None): "receptions",
    ("rushing_yards", None): "rushing_yards", ("carries", None): "carries",
    ("touchdowns", None): "anytime_td",
}


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


class DirectTDModel:
    """P(scores >= 1 touchdown | plays) by logistic regression on point-in-time role features.

    Features: log1p(EWMA any_td), log1p(EWMA touches), log1p(EWMA targets), log1p(EWMA carries),
    team implied total, home, shrink weight, position dummies. Fitted by IRLS with a small ridge.
    """
    name = "direct_binary"
    FEATS = ["ewma_any_td", "ewma_touches", "ewma_targets", "ewma_carries"]

    def __init__(self, ridge: float = 1.0):
        self.ridge = ridge
        self.beta = None
        self.cols = None

    def _design(self, df):
        X = [np.ones(len(df))]
        for c in self.FEATS:
            X.append(np.log1p(np.clip(df[c].to_numpy(dtype=float), 0, None)))
        X.append(df["implied_total"].to_numpy(dtype=float) / 10.0)
        X.append(df["home"].to_numpy(dtype=float))
        X.append(df["shrink_w"].to_numpy(dtype=float))
        pos = df["position"].to_numpy()
        for p in ("RB", "WR", "TE"):
            X.append((pos == p).astype(float))
        return np.column_stack(X)

    def fit(self, train: pd.DataFrame):
        X = self._design(train)
        y = (train["any_td"].to_numpy(dtype=float) > 0).astype(float)
        beta = np.zeros(X.shape[1]); beta[0] = np.log(max(y.mean(), 1e-3) / max(1 - y.mean(), 1e-3))
        for _ in range(40):
            p = _sigmoid(X @ beta)
            w = np.clip(p * (1 - p), 1e-6, None)
            z = X @ beta + (y - p) / w
            XtW = X.T * w
            new = np.linalg.solve(XtW @ X + self.ridge * np.eye(X.shape[1]), XtW @ z)
            if np.max(np.abs(new - beta)) < 1e-8:
                beta = new; break
            beta = new
        self.beta = beta
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        return _sigmoid(self._design(df) @ self.beta)

    def to_json(self):
        return {"name": self.name, "beta": [float(b) for b in self.beta], "feats": self.FEATS, "ridge": self.ridge}


@dataclass
class StatModel:
    spec_name: str
    family_name: str
    mean_model: object
    opp_model: object
    family: object
    grid: np.ndarray
    train_rows: int
    train_seasons: tuple

    def survival(self, rows: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        """Returns (grid, S) with S[i, g] = P(Y >= grid[g]) for each row."""
        spec = pdist.STAT_SPECS[self.spec_name]
        mu = pdist.predict_mean(self.mean_model, rows, spec, spec.col, pdist.MU_FLOOR[spec.kind])
        muo = pdist.predict_mean(self.opp_model, rows, spec, spec.opp, 0.1)
        eff = rows[spec.eff].to_numpy() if spec.eff and spec.eff in rows.columns else None
        F = self.family.cdf_grid(mu, muo, eff, self.grid)          # P(Y <= grid)
        S = np.clip(1.0 - np.concatenate([np.zeros((F.shape[0], 1)), F[:, :-1]], axis=1), 0.0, 1.0)
        return self.grid, S, mu

    def p_at_least(self, rows: pd.DataFrame, ks) -> np.ndarray:
        grid, S, _mu = self.survival(rows)
        idx = np.searchsorted(grid, np.asarray(ks, float), side="left")
        idx = np.clip(idx, 0, len(grid) - 1)
        return S[np.arange(len(rows))[:, None], idx[None, :]] if np.ndim(ks) else S[:, idx]


@dataclass
class ModelBundle:
    version: str
    target_season: int
    train_seasons: tuple
    stat_models: dict = field(default_factory=dict)
    td_model: object = None
    config: dict = field(default_factory=dict)
    artifact_sha: str = ""

    def sha(self):
        payload = {"version": self.version, "target_season": self.target_season,
                   "train_seasons": list(self.train_seasons), "config": self.config,
                   "families": {k: v.family_name for k, v in self.stat_models.items()},
                   "td_model": self.td_model.to_json() if self.td_model is not None else None}
        self.artifact_sha = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
        return self.artifact_sha

    def to_json(self):
        return {"version": self.version, "artifact_sha": self.artifact_sha, "target_season": self.target_season,
                "train_seasons": list(self.train_seasons), "config": self.config,
                "stat_models": {k: {"family": v.family_name, "train_rows": v.train_rows} for k, v in self.stat_models.items()},
                "td_model": self.td_model.to_json() if self.td_model is not None else None}


def fit_bundle(df_hist: pd.DataFrame, target_season: int, version: str, config: dict,
               stats=None, verbose=print) -> ModelBundle:
    """Fit every statistic's mean model and distribution family on seasons < target_season."""
    stats = stats or [s for s in CHOSEN_FAMILY if s in pdist.STAT_SPECS]
    train_seasons = (int(df_hist.season.min()), target_season - 1)
    b = ModelBundle(version=version, target_season=target_season, train_seasons=train_seasons, config=config)
    for name in stats:
        spec = pdist.STAT_SPECS[name]
        fam_name = CHOSEN_FAMILY[name]
        pm = pdist.population_mask(df_hist, spec.pop)
        tr = df_hist[pm & (df_hist.season < target_season) & (df_hist.season >= config.get("min_train_season", 2016))]
        if len(tr) < 500:
            verbose(f"  skip {name}: only {len(tr)} training rows")
            continue
        if fam_name == "direct_binary":
            b.td_model = DirectTDModel().fit(tr)
            verbose(f"  {name}: direct binary model on {len(tr)} rows")
            continue
        y_tr = np.clip(tr[spec.col].to_numpy(dtype=float), 0, None)
        mm = pdist.fit_mean_model(tr, spec, spec.col, spec.kind)
        om = pdist.fit_mean_model(tr, spec, spec.opp, "count")
        mu_tr = pdist.predict_mean(mm, tr, spec, spec.col, pdist.MU_FLOOR[spec.kind])
        muo_tr = pdist.predict_mean(om, tr, spec, spec.opp, 0.1)
        eff_tr = tr[spec.eff].to_numpy() if spec.eff else None
        fam = pdist.make_family(fam_name, spec)
        fam.fit(mu_tr, muo_tr, eff_tr, y_tr)
        b.stat_models[name] = StatModel(name, fam_name, mm, om, fam, np.arange(0, spec.grid_max + 1), len(tr), train_seasons)
        verbose(f"  {name}: {fam_name} on {len(tr)} rows")
    b.sha()
    return b
