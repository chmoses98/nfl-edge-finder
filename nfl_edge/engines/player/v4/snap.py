"""V4 SNAP-SHARE MODEL: a pregame distribution of the fraction of the team's offensive snaps a player takes.

v3 has no snap model; its implicit estimate is the EWMA of past snap share (half-life 6 games), which does not
know that a teammate is out, that the player himself is returning, questionable, new to the team, or that his last
three games say more than his last season. The estimator here is one ridge regression per position group on
strictly pregame features (nfl_edge/engines/player/v4/features.py), and a second ridge on the absolute residual so
the UNCERTAINTY is a function of the same evidence (a returning or new or questionable player is less certain).

Output per row: mean, sd, a Beta(mean, sd) distribution on [0, 1] (the only clamp is the physical range) and its
10th / 90th percentiles. The sd is what the rest of V4 propagates.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

from nfl_edge.engines.player.v4.features import group_of
from nfl_edge.engines.player.v4.linear import Linear

SNAP_FEATURES = ["ewma_snap_share", "last_snap_share", "last3_snap_share", "max4_snap_share", "cur_mean_snap_share",
                 "n_cur_c", "log_n_prior", "changed_team", "self_new", "self_returning", "own_q", "vac_same_s",
                 "vac_same_s_frac", "vac_same_s_room", "vac_off_same_s", "ret_same_s", "ret_same_s_frac", "n_active_same",
                 "gap_gt1"]
QB_EXTRA = ["qb_starter_f"]
MIN_ROWS = 400


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["n_cur_c"] = np.minimum(d["n_cur_season"].fillna(0), 4) / 4.0
    d["log_n_prior"] = np.log1p(d["n_prior"].fillna(0))
    d["vac_same_s_frac"] = d["vac_same_s"] * d["self_frac_s"]
    d["vac_same_s_room"] = d["vac_same_s"] * (1.0 - d["last3_snap_share"].clip(0, 1))
    d["ret_same_s_frac"] = d["ret_same_s"] * (1.0 - d["self_frac_s"])
    d["gap_gt1"] = (d["games_since_last"].fillna(1) > 1).astype(float)
    d["qb_starter_f"] = d.get("qb_starter", pd.Series(False, index=d.index)).fillna(False).astype(float)
    d["pgroup"] = d["position"].map(group_of)
    return d


@dataclass
class SnapModel:
    mean: dict = field(default_factory=dict)       # group -> Linear
    spread: dict = field(default_factory=dict)     # group -> Linear on |residual|
    features: dict = field(default_factory=dict)
    scale: dict = field(default_factory=dict)      # group -> sd calibration (80% interval coverage on training)
    ablate: bool = False                           # True -> the v3 implicit estimate (EWMA) with a pooled spread

    @classmethod
    def fit(cls, train: pd.DataFrame, *, ablate: bool = False, exclude=()) -> "SnapModel":
        """exclude: feature-name fragments to drop (the no-redistribution ablation drops every teammate feature)."""
        d = prepare(train)
        d = d[d["snap_share"].notna() & (d["offense_snaps"].fillna(0) > 0)]
        m = cls(ablate=ablate)
        for g in ("QB", "RB", "WR", "TE"):
            sub = d[d.pgroup == g]
            if len(sub) < MIN_ROWS:
                continue
            cols = ["ewma_snap_share"] if ablate else SNAP_FEATURES + (QB_EXTRA if g == "QB" else [])
            cols = [c for c in cols if not any(x in c for x in exclude)]
            y = sub["snap_share"].clip(0, 1).to_numpy(float)
            if ablate:
                mean = Linear(["ewma_snap_share"], np.array([0.0, 1.0]), np.zeros(1), np.ones(1))
            else:
                mean = Linear.fit(sub, cols, y)
            r = np.abs(y - np.clip(mean.predict(sub), 0, 1))
            spread = Linear.fit(sub, cols, r)
            sd0 = np.clip(spread.predict(sub), 0.02, 0.45) * np.sqrt(np.pi / 2.0)
            m.scale[g] = float(np.clip(np.quantile(r / sd0, 0.80) / 1.2816, 0.5, 2.0))
            m.mean[g], m.spread[g], m.features[g] = mean, spread, cols
        return m

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        d = prepare(df)
        mean = np.full(len(d), np.nan); sd = np.full(len(d), np.nan)
        for g, mdl in self.mean.items():
            ix = np.where(d.pgroup.to_numpy() == g)[0]
            if not len(ix):
                continue
            sub = d.iloc[ix]
            mean[ix] = np.clip(mdl.predict(sub), 0.005, 0.995)
            # E|r| = sd * sqrt(2/pi) for a normal residual
            sd[ix] = np.clip(self.spread[g].predict(sub), 0.02, 0.45) * np.sqrt(np.pi / 2.0) * self.scale.get(g, 1.0)
        var = np.minimum(sd ** 2, 0.9 * mean * (1 - mean))
        phi = mean * (1 - mean) / np.maximum(var, 1e-6) - 1.0
        a, b = mean * phi, (1 - mean) * phi
        with np.errstate(invalid="ignore"):
            p10 = stats.beta.ppf(0.10, a, b); p90 = stats.beta.ppf(0.90, a, b)
        return pd.DataFrame({"snap_mean": mean, "snap_sd": np.sqrt(var), "snap_p10": p10, "snap_p90": p90}, index=df.index)

    def summary(self) -> dict:
        return {g: {"n_features": len(self.features.get(g, [])), "coef": {k: round(v, 4) for k, v in m.coefficients().items()}}
                for g, m in self.mean.items()}
