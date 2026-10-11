"""PURE_EWM_BASELINE: the simplest sports-only forecaster, scored on exactly PURE_PLAYER_V1's rows.

Every mean is the player's (or team's) own exponentially weighted mean over strictly prior games -- the same
EWM (half-life 6 games, season carry 0.35, shrink to the position prior) PURE_PLAYER_V1 starts from -- with no
environment, role or opponent model on top. Its distributions use PURE_PLAYER_V1's machinery (dists.py), fitted
the same way on the same training seasons, so a difference between the arms is a difference in the forecast
centre and its conditional structure, not in the choice of family.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from nfl_edge.engines.player.pure_v1 import BASELINE_VERSION
from nfl_edge.engines.player.pure_v1.model import FIRST_SEASON, fit_distributions

EWM_COL = {"snap_share": "e_snap_share", "targets": "e_targets", "receptions": "e_receptions", "receiving_yards": "e_receiving_yards",
           "carries": "e_carries", "rushing_yards": "e_rushing_yards", "passing_attempts": "e_attempts",
           "completions": "e_completions", "passing_yards": "e_passing_yards"}
LINEAGE = {k: [v] for k, v in EWM_COL.items()}


def means(d: pd.DataFrame) -> dict:
    return {s: d[c].to_numpy(float) for s, c in EWM_COL.items()}


def team_predict(t: pd.DataFrame) -> pd.DataFrame:
    out = t[["team", "game_id"]].copy()
    out["vol_pa"], out["vol_ra"], out["vol_pts"] = t["f_pa"].to_numpy(), t["f_ra"].to_numpy(), t["f_pts"].to_numpy()
    out["vol_plays"] = t["f_plays"].to_numpy()
    return out


@dataclass
class BaselineModel:
    target_season: int
    version: str = BASELINE_VERSION
    dist: dict = field(default_factory=dict)
    team_sd: dict = field(default_factory=dict)


def fit(rows: pd.DataFrame, t: pd.DataFrame, target_season: int, *, first_season: int = FIRST_SEASON) -> BaselineModel:
    b = BaselineModel(target_season=target_season)
    tr = rows[(rows.season < target_season) & (rows.season >= first_season) & rows.played]
    fit_distributions(b.dist, tr, means(tr))
    tt = t[(t.season < target_season) & (t.season >= first_season) & t.pa.notna() & t.pts.notna()]
    for k, f in (("pa", "f_pa"), ("ra", "f_ra"), ("pts", "f_pts")):
        b.team_sd[k] = float(np.std(tt[k].to_numpy(float) - tt[f].to_numpy(float)))
    return b
