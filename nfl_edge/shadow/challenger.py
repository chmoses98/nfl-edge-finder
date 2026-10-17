"""shadow-0.5.0 challenger: repairs two verified structural defects in the player mean projection WITHOUT touching the
pinned incumbent (tests/test_incumbent_unchanged.py). RESEARCH / SHADOW ONLY: no authority, no recommendation path.

Defects (research/mean_defect/FINDINGS.md):
  D1  live history excluded this season's completed games, so a player's EWMA only decayed week over week
      (see prospective.pit_history); shrink_w drifted up and projections fell with no new information.
  D2  the count (Poisson) mean models took `shrink_w` as a feature. The EWMA halves its weights at each season boundary,
      so shrink_w is a calendar variable that the fit read as "low-usage player": established players were cut 8-20%
      in weeks 1-6, and the raw-EWMA exp link blew up the top usage tail. v2 uses a calendar-free thinness feature and
      log-usage terms (player_distributions._design design="v2").
"""
from __future__ import annotations

from contextlib import contextmanager
from functools import wraps

from nfl_edge.research import player_distributions as pdist
from nfl_edge.shadow.prospective import pit_history

CHALLENGER_VERSION = "shadow-0.5.0"


@contextmanager
def count_design_v2():
    """Within the block every fit_mean_model call uses design v2 (a no-op for the yardage/TD specs, which keep v1)."""
    orig = pdist.fit_mean_model

    @wraps(orig)
    def patched(*a, **k):
        k.setdefault("design", "v2")
        return orig(*a, **k)

    pdist.fit_mean_model = patched
    try:
        yield
    finally:
        pdist.fit_mean_model = orig


def install(pricer):
    """Patch a loaded copy of the frozen pricer module so main() builds the challenger. Returns the module."""
    fit0, build0, load0 = pricer.fit_bundle, pricer.build_prospective_rows, pdist.load_player_games

    def fit(*a, **k):
        with count_design_v2():
            return fit0(*a, **k)

    def build(hist, upcoming):
        target = int(upcoming.season.max())
        return build0(pit_history(hist, upcoming, target), upcoming)

    def load(root, seasons, *a, **k):
        seasons = list(seasons)
        if seasons and max(seasons) + 1 == pricer_target(pricer):
            seasons.append(pricer_target(pricer))  # the pricer asks for seasons < target; the challenger also wants the target season
        return load0(root, seasons, *a, **k)

    pricer.fit_bundle, pricer.build_prospective_rows, pdist.load_player_games = fit, build, load
    return pricer


def pricer_target(pricer):
    return getattr(pricer, "_CHALLENGER_TARGET", 10**9)
