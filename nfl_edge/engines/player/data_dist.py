"""DATA_PLAYER_DIST: the football/data distribution of a player statistic, opportunity x efficiency, walk-forward.

STRUCTURE
---------
For every statistic the engine fits, on seasons strictly before the target season:

    opportunity model    E[opportunity | features]     Poisson GLM on the v2 features (team volume x share ...)
    stat mean model      E[stat | features]            OLS (yards) / Poisson GLM (counts, TDs), same features
    distribution family  P(Y <= k | mu, mu_opp, eff)   chosen OUT OF SAMPLE per statistic by the walk-forward
                                                       study (scripts/research/player_engine_v2_study.py) among the
                                                       frozen research families (normal, negbin, poisson, emp-binned,
                                                       hurdle-gamma, two-stage MC) -- never because it is convenient

and outputs ONE LatticeDistribution per (player, game, statistic). Every rung, range and moment is derived from
it, so ladders are coherent by construction.

The frozen research module is IMPORTED for its family implementations and its evaluation code; nothing in it is
edited. The old model's features (`ewma_<stat>`, `ewma_<opp>`, implied total, home, shrink) remain available so the
"v1 features" arm can be run through the identical machinery for the comparison the mission asks for.

UNCERTAINTY is explicit: the record carries the prior-game count, the EWMA shrink weight, the opportunity
projection and the efficiency feature, so an autopsy can say which component missed.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from nfl_edge.engines.player.dist import LatticeDistribution
from nfl_edge.engines.player.features_v2 import V2_FEATURES
from nfl_edge.research import player_distributions as pdist

VERSION = "data-player-dist-2.0.0"
RIDGE = 1.0

# statistic -> (research spec name, outcome column, population, kind, opportunity column, efficiency feature)
# `rush_rec_yards` is new: a marginal model of the SUM, fitted like a yards stat on carries+targets.
STATS = {
    "passing_yards": "passing_yards", "passing_tds": "passing_tds", "interceptions": "interceptions", "attempts": "attempts",
    "completions": "completions", "rushing_yards": "rushing_yards", "carries": "carries", "receiving_yards": "receiving_yards",
    "receptions": "receptions", "touchdowns": "anytime_td", "qb_rushing_yards": "qb_rushing_yards",
}
# out-of-sample family choice per spec (walk-forward, research/player_distributions for the v1 arm; the v2 study
# re-runs the comparison on the v2 features and records its own choice in research/player_engine_v2/results.json).
# Study A (research/player_engine_v2/results.json, walk-forward 2020-2025 on v2 features): the out-of-sample choice per
# statistic, recorded verbatim. It differs from the v1 choice for `attempts` (scale_emp_binned -> normal) and
# `passing_tds` (poisson -> negbin); every other family is confirmed. `qb_rushing_yards` was not in the study and keeps
# the v1 research choice.
DEFAULT_FAMILY = {"attempts": "normal", "completions": "normal", "passing_yards": "normal", "passing_tds": "negbin",
                  "interceptions": "negbin", "qb_rushing_yards": "scale_emp_binned", "receptions": "scale_emp_binned",
                  "receiving_yards": "scale_emp_binned", "carries": "scale_emp_binned", "rushing_yards": "scale_emp_binned",
                  "anytime_td": "negbin", "rush_rec_yards": "scale_emp_binned"}
V1_DESIGN = ["ewma_stat", "ewma_opp", "implied_total", "home", "shrink_w"]
V2_DESIGN = V1_DESIGN + ["ewma_team_pass_att", "ewma_team_rush_att", "ewma_team_snaps", "ewma_team_ypa", "ewma_team_pass_rate",
                         "ewma_target_share", "ewma_carry_share", "ewma_snap_share", "share_recent_delta_target",
                         "share_recent_delta_carry", "qb_changed_recent"]


def _spec(stat: str) -> pdist.StatSpec:
    if stat == "rush_rec_yards":
        return pdist.StatSpec("rush_rec_yards", "rush_rec_yards", "REC", "touches", "yards", list(range(40, 201, 10)), "ypt_rr", "gamma", 3.0, 400)
    return pdist.STAT_SPECS[STATS.get(stat, stat)]


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    if "rush_rec_yards" not in df.columns:
        df = df.copy()
        df["rush_rec_yards"] = df["rushing_yards"].fillna(0) + df["receiving_yards"].fillna(0)
        df["ewma_rush_rec_yards"] = df["ewma_rushing_yards"] + df["ewma_receiving_yards"]
        df["ypt_rr"] = df["ewma_rush_rec_yards"] / (df["ewma_touches"] + 1e-3)
    return df


def design(df: pd.DataFrame, spec: pdist.StatSpec, col: str, feature_set: str) -> np.ndarray:
    cols = V1_DESIGN if feature_set == "v1" else V2_DESIGN
    X = [np.ones(len(df))]
    for c in cols:
        if c == "ewma_stat":
            X.append(df[f"ewma_{col}"].to_numpy(float))
        elif c == "ewma_opp":
            X.append(df[f"ewma_{spec.opp}"].to_numpy(float))
        else:
            X.append(np.nan_to_num(df[c].to_numpy(float), nan=0.0, posinf=0.0, neginf=0.0))
    return np.column_stack(X)


@dataclass
class MeanModel:
    kind: str                       # ols | poisson
    beta: np.ndarray
    mu_x: np.ndarray
    sd_x: np.ndarray
    feature_set: str
    col: str

    def predict(self, df, spec, floor):
        X = design(df, spec, self.col, self.feature_set)
        Xs = np.column_stack([np.ones(len(X)), (X[:, 1:] - self.mu_x) / self.sd_x])
        mu = Xs @ self.beta if self.kind == "ols" else np.exp(np.clip(Xs @ self.beta, -20, 8))
        return np.maximum(mu, floor)


def fit_mean(train: pd.DataFrame, spec: pdist.StatSpec, col: str, kind: str, feature_set: str) -> MeanModel:
    X = design(train, spec, col, feature_set)
    y = np.clip(train[col].to_numpy(float), 0, None)
    mu_x = X[:, 1:].mean(axis=0); sd_x = X[:, 1:].std(axis=0); sd_x[sd_x < 1e-9] = 1.0
    Xs = np.column_stack([np.ones(len(X)), (X[:, 1:] - mu_x) / sd_x])
    if kind == "yards":
        A = Xs.T @ Xs + RIDGE * np.eye(Xs.shape[1]); A[0, 0] -= RIDGE
        beta = np.linalg.solve(A, Xs.T @ y)
        return MeanModel("ols", beta, mu_x, sd_x, feature_set, col)
    beta = np.zeros(Xs.shape[1]); beta[0] = np.log(max(y.mean(), 1e-3))
    pen = RIDGE * np.eye(Xs.shape[1]); pen[0, 0] = 0.0
    for _ in range(60):
        eta = np.clip(Xs @ beta, -20, 8); w = np.exp(eta)
        z = eta + (y - w) / w
        XtW = Xs.T * w
        new = np.linalg.solve(XtW @ Xs + pen, XtW @ z)
        if np.max(np.abs(new - beta)) < 1e-7:
            beta = new; break
        beta = new
    return MeanModel("poisson", beta, mu_x, sd_x, feature_set, col)


@dataclass
class StatDistributionModel:
    stat: str
    spec: pdist.StatSpec
    family_name: str
    feature_set: str
    mean_model: MeanModel
    opp_model: MeanModel
    family: object
    grid: np.ndarray
    train_rows: int
    train_seasons: tuple
    fitted_on: dict = field(default_factory=dict)

    def intermediates(self, rows: pd.DataFrame) -> dict:
        mu = self.mean_model.predict(rows, self.spec, pdist.MU_FLOOR[self.spec.kind])
        muo = self.opp_model.predict(rows, self.spec, 0.1)
        eff = rows[self.spec.eff].to_numpy(float) if self.spec.eff and self.spec.eff in rows.columns else None
        return {"mu": mu, "muo": muo, "eff": eff}

    def cdf_grid(self, rows: pd.DataFrame) -> tuple[np.ndarray, dict]:
        im = self.intermediates(rows)
        F = self.family.cdf_grid(im["mu"], im["muo"], im["eff"], self.grid)
        return F, im

    def distributions(self, rows: pd.DataFrame) -> list:
        F, im = self.cdf_grid(rows)
        out = []
        for i in range(len(rows)):
            d = LatticeDistribution.from_cdf(F[i], meta={"family": self.family_name, "mu": float(im["mu"][i]), "mu_opp": float(im["muo"][i]),
                                                        "eff": (float(im["eff"][i]) if im["eff"] is not None else None),
                                                        "feature_set": self.feature_set, "stat": self.stat})
            out.append(d)
        return out


def fit_stat(train: pd.DataFrame, stat: str, family_name: str, feature_set: str, target_season: int) -> StatDistributionModel:
    spec = _spec(stat)
    train = ensure_columns(train)
    pm = pdist.population_mask(train, spec.pop)
    tr = train[pm & (train.season < target_season)]
    if len(tr) < 500:
        raise ValueError(f"only {len(tr)} training rows for {stat}")
    mm = fit_mean(tr, spec, spec.col, spec.kind, feature_set)
    om = fit_mean(tr, spec, spec.opp, "count", feature_set)
    mu = mm.predict(tr, spec, pdist.MU_FLOOR[spec.kind]); muo = om.predict(tr, spec, 0.1)
    eff = tr[spec.eff].to_numpy(float) if spec.eff and spec.eff in tr.columns else None
    y = np.clip(tr[spec.col].to_numpy(float), 0, None)
    fam = pdist.make_family(family_name, spec)
    if family_name == "two_stage_mc":
        fam.fit_opportunity(muo, tr[spec.opp].to_numpy(float))
        fam.fit(mu, tr[spec.opp].to_numpy(float), eff, y)
    else:
        fam.fit(mu, muo, eff, y)
    return StatDistributionModel(stat, spec, family_name, feature_set, mm, om, fam, np.arange(0, spec.grid_max + 1), int(len(tr)),
                                 (int(tr.season.min()), int(tr.season.max())))


@dataclass
class DataPlayerBundle:
    version: str
    target_season: int
    feature_set: str
    models: dict = field(default_factory=dict)
    families: dict = field(default_factory=dict)
    artifact_sha: str = ""

    def sha(self):
        payload = {"version": self.version, "target_season": self.target_season, "feature_set": self.feature_set,
                   "families": {k: v.family_name for k, v in self.models.items()},
                   "train": {k: [v.train_rows, list(v.train_seasons)] for k, v in self.models.items()}}
        self.artifact_sha = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
        return self.artifact_sha

    def to_json(self):
        return {"version": self.version, "artifact_sha": self.artifact_sha, "target_season": self.target_season, "feature_set": self.feature_set,
                "models": {k: {"family": v.family_name, "train_rows": v.train_rows, "train_seasons": list(v.train_seasons)} for k, v in self.models.items()}}


def fit_bundle(hist: pd.DataFrame, target_season: int, *, feature_set: str = "v2", families: dict | None = None, stats=None,
               verbose=print) -> DataPlayerBundle:
    families = {**DEFAULT_FAMILY, **(families or {})}
    stats = stats or list(STATS) + ["rush_rec_yards"]
    b = DataPlayerBundle(VERSION, target_season, feature_set)
    hist = ensure_columns(hist)
    for stat in stats:
        spec_name = STATS.get(stat, stat)
        fam = families.get(spec_name) or families.get(stat)
        try:
            b.models[stat] = fit_stat(hist, stat, fam, feature_set, target_season)
            b.families[stat] = fam
            verbose(f"  {stat}: {fam} on {b.models[stat].train_rows} rows ({feature_set} features)")
        except ValueError as e:
            verbose(f"  skip {stat}: {e}")
    b.sha()
    return b
