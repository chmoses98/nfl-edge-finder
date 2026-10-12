"""End-to-end PURE_PLAYER_V1_2 forecasts for one target season (frozen V1 data path + V1_2 features).

    rows, t = pure_v1.features.build(pure_v1.data.build_player_games(...))   # PURE_PLAYER_V1's frame, unchanged
    rows12 = add_features(rows, t)                                          # + (B) positional opponent, (C) pool
    out = run(rows12, t, target_season)

Same population, same point-in-time assertion (`pure_v1.pipeline.check_point_in_time`), same long format and
sidecar export as PURE_PLAYER_V1, so every arm is scored on identical rows.
"""
from __future__ import annotations

import pandas as pd

from nfl_edge.engines.player.pure_v1 import model as M1
from nfl_edge.engines.player.pure_v1 import pipeline as P1
from nfl_edge.engines.player.pure_v1_2 import MODEL_NAME
from nfl_edge.engines.player.pure_v1_2 import features as F
from nfl_edge.engines.player.pure_v1_2 import model as M


def add_features(rows: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    d = F.attach_defence(rows, F.defence_by_group(rows, t))
    pool = F.available_pool(rows, t)
    return pd.concat([d, pool], axis=1)


def run(rows12: pd.DataFrame, t: pd.DataFrame, target_season: int, *, weeks=None) -> dict:
    model = M.fit(rows12, t, target_season)
    te = rows12[(rows12.season == target_season) & rows12.played]
    if weeks is not None:
        te = te[te.week.isin(list(weeks))]
    te = te.reset_index(drop=True)
    P1.check_point_in_time(te)
    d = model.intermediates(te, t)
    long = P1._long(d, model.dist, model.means(d), M1.LINEAGE)
    tt = t[(t.season == target_season) & t.pa.notna()]
    if weeks is not None:
        tt = tt[tt.week.isin(list(weeks))]
    actual = tt[["team", "game_id", "season", "week", "pa", "ra", "plays", "pts"]].reset_index(drop=True)
    team = actual.merge(model.team_predict(tt), on=["team", "game_id"], how="left")
    return {"model": model, "intermediates": d, "player": {MODEL_NAME: long}, "team": {MODEL_NAME: team}}
