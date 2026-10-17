"""shadow-0.5.0 challenger: repairs two verified structural defects in the player mean projection WITHOUT editing any frozen or
pinned file (tests/test_incumbent_unchanged.py, tests/test_negative_research_preserved.py). RESEARCH / SHADOW ONLY.

Defects (research/mean_defect/FINDINGS.md):
  D1  live history excluded this season's completed games, so a player's EWMA only decayed week over week (`pit_history`).
  D2  the count (Poisson) mean models took `shrink_w` as a feature. The EWMA halves its weights at each season boundary, so
      shrink_w is a calendar variable that the fit read as "low-usage player": established players were cut 8-20% in weeks
      1-6, and the raw-EWMA exp link blew up the top usage tail. v2 uses a calendar-free thinness feature and log-usage terms.

Mechanism: the frozen `player_distributions` code is reused unchanged. While `count_design_v2()` is active its `_design` is
swapped for a dispatcher (v2 design for count specs only), fitted models carry a "v2" marker as a 6th tuple element, and
`predict_mean` re-enters the same design for marked models. Outside the context everything is the frozen code.
"""
from __future__ import annotations

from contextlib import contextmanager

import numpy as np
import pandas as pd

from nfl_edge.research import player_distributions as pdist

CHALLENGER_VERSION = "shadow-0.5.0"
THIN_K = 3.0
THIN_CAP = 16


def sample_thinness(df: pd.DataFrame) -> np.ndarray:
    """k / (min(n_prior, cap) + k): how thin the PLAYER's own game sample is, and nothing else (no season-boundary term)."""
    return THIN_K / (np.minimum(df.n_prior.to_numpy(dtype=float), THIN_CAP) + THIN_K)


def design_v2(df, spec, col, role=False, defense=False):
    """Log usage terms + calendar-free thinness. Same intercept/implied_total/home columns as the frozen design."""
    return np.column_stack([
        np.ones(len(df)), np.log1p(df[f"ewma_{col}"].to_numpy()), np.log1p(df[f"ewma_{spec.opp}"].to_numpy()),
        df.implied_total.to_numpy(), df.home.to_numpy(dtype=float), sample_thinness(df)])


def pit_history(hist: pd.DataFrame, upcoming: pd.DataFrame, target_season: int) -> pd.DataFrame:
    """Completed games of the TARGET season strictly before the earliest upcoming week (rows of the slate's own week, or of any
    upcoming game, are dropped so a re-run after kickoff cannot see a result it is pricing). Earlier seasons pass through."""
    if hist.empty or upcoming.empty:
        return hist
    cur = hist.season == target_season
    first_week = int(upcoming.loc[upcoming.season == target_season, "week"].min()) if (upcoming.season == target_season).any() else 0
    drop = cur & ((hist.week >= first_week) | hist.game_id.isin(set(upcoming.game_id)))
    return hist[~drop].copy()


@contextmanager
def count_design_v2():
    orig_design, orig_fit, orig_predict = pdist._design, pdist.fit_mean_model, pdist.predict_mean
    state = {"v2": False}

    def design(df, spec, col, role=False, defense=False):
        if state["v2"] and spec.kind == "count":
            return design_v2(df, spec, col, role, defense)
        return orig_design(df, spec, col, role, defense)

    def fit(train, spec, col, kind, *a, **k):
        state["v2"] = True
        try:
            m = orig_fit(train, spec, col, kind, *a, **k)
        finally:
            state["v2"] = False
        return (*m, "v2") if spec.kind == "count" else m

    def predict(model, df, spec, col, floor):
        state["v2"] = len(model) > 5 and model[5] == "v2"
        try:
            return orig_predict(model, df, spec, col, floor)
        finally:
            state["v2"] = False

    pdist._design, pdist.fit_mean_model, pdist.predict_mean = design, fit, predict
    try:
        yield
    finally:
        pdist._design, pdist.fit_mean_model, pdist.predict_mean = orig_design, orig_fit, orig_predict


def install(pricer):
    """Patch a loaded copy of the frozen pricer module so main() builds the challenger, for the life of this process."""
    from contextlib import ExitStack
    stack = ExitStack()
    stack.enter_context(count_design_v2())            # dedicated challenger process: never exited
    build0, load0 = pricer.build_prospective_rows, pdist.load_player_games
    target = getattr(pricer, "_CHALLENGER_TARGET", 10**9)

    def build(hist, upcoming):
        return build0(pit_history(hist, upcoming, int(upcoming.season.max())), upcoming)

    def load(root, seasons, *a, **k):
        seasons = list(seasons)
        if seasons and max(seasons) + 1 == target:
            seasons.append(target)                    # the pricer asks for seasons < target; the challenger also wants the target season
        return load0(root, seasons, *a, **k)

    pricer.build_prospective_rows, pdist.load_player_games = build, load
    pricer._challenger_stack = stack
    return pricer
