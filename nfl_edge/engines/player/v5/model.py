"""DATA_PLAYER_V5's model: V4's structural chain (nfl_edge/engines/player/v4/model.py), fitted with the quarterback-
identity channel switched on and stamped with V5's own version.

Nothing is copied. `M.fit_bundle(config={"qb_identity": True}, version=VERSION)` appends the team-game quarterback-
identity features (qb_features.py) to exactly four V4 stages -- team pass / rush volume, the pass-catchers' catch
rate and yards per catch, and the starter's own attempts -- and leaves every other stage, feature, prior and
estimator as V4 has them. With the flag absent (V4's own config) those stages are byte-for-byte what V4 fits, so a
V4 bundle, its sha and its distributions do not move when this package is imported or run.

Which QB is the starter (`qb_starter` on the rows, and the projected starter behind the identity features) is the
ONE changed input: the point-in-time resolution (nfl_edge/context/qb_resolution.py) instead of the raw chart QB1.
It reaches every downstream quantity through the structure -- the promoted starter's snap model (qb_starter_f), his
passing population (attempts, completions, yards, TDs, interceptions) and QB rushing, the team's pass volume and so
every pass-catcher's targets, and the catch rate / yards per catch the targets are converted with. No output is
adjusted after the fact.
"""
from __future__ import annotations

from nfl_edge.engines.player.v4 import model as M
from nfl_edge.engines.player.v5 import VERSION

CONFIG = {"qb_identity": True}
STATS = M.STATS


def fit_bundle(frame, target_season: int, config: dict | None = None, *, first_season: int = 2014, teams=None, verbose=print):
    """frame: the V4 player-game table plus qb_features.QB_ID_COLS; `teams` the team table built from that frame."""
    return M.fit_bundle(frame, target_season, {**CONFIG, **(config or {})}, first_season=first_season, teams=teams,
                        verbose=verbose, version=VERSION)
