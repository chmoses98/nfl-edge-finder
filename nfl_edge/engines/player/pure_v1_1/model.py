"""PURE_PLAYER_V1_1 fit: PURE_PLAYER_V1's stages verbatim, with the preregistered availability columns added to the
snap-share, target-share and carry-share stages. Everything downstream (count stacks, efficiency rates,
distributions) is refitted on the same training rows exactly as V1 does, because it consumes those stages' output.

The fitted object is V1's own `PureModel` (its `intermediates`, `means`, `team_predict` are reused unchanged: each
stage's `Linear` carries its own column list, so the added columns are read wherever they were fitted).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nfl_edge.engines.player.pure_v1 import model as M
from nfl_edge.engines.player.pure_v1.model import (CARRY_GROUPS, FIRST_SEASON, MIN_TRAIN, SNAP, TARGET_GROUPS, TEAM_PA, TEAM_PTS,
                                                    TEAM_RA, PureModel, fit_distributions, population)
from nfl_edge.engines.player.v4.linear import Linear
from nfl_edge.engines.player.pure_v1_1 import VERSION
from nfl_edge.engines.player.pure_v1_1.features import OWN

SNAP_X = SNAP + OWN
SHARE_EXTRA = {"target": OWN + ["vac_t", "qb1_out"], "carry": OWN + ["vac_c"]}


def fit(rows: pd.DataFrame, t: pd.DataFrame, target_season: int, *, first_season: int = FIRST_SEASON) -> PureModel:
    m = PureModel(target_season=target_season, first_season=first_season, version=VERSION)
    tt = t[(t.season < target_season) & (t.season >= first_season) & t.pa.notna() & t.pts.notna()]
    for name, cols, y in (("pa", TEAM_PA, tt.pa), ("ra", TEAM_RA, tt.ra), ("pts", TEAM_PTS, tt.pts)):
        m.team[name] = Linear.fit(tt, cols, y.to_numpy(float))
        m.team_sd[name] = float(np.std(y.to_numpy(float) - m.team[name].predict(tt)))
    tr = rows[(rows.season < target_season) & (rows.season >= first_season) & rows.played].copy()
    g = tr["pgroup"].to_numpy()
    qbs = (g == "QB") & tr["qb_starter"].to_numpy(bool)
    sm = population(tr, "snap_share") & np.isfinite(tr["snap_share"].to_numpy(float))
    for grp in ("QB", "RB", "WR", "TE"):
        sub = tr[sm & (g == grp)]
        if len(sub) >= MIN_TRAIN:
            m.snap[grp] = Linear.fit(sub, SNAP_X, sub["snap_share"].clip(0, 1).to_numpy(float))
    d = m.intermediates(tr, t)
    for kind, groups in (("target", TARGET_GROUPS), ("carry", CARRY_GROUPS)):
        cols = [f"e_{kind}_share", f"last_{kind}_share", f"last3_{kind}_share", f"cur_{kind}_share", "snap_mean", f"struct_{kind}",
                "changed_team", "n_cur_c", "log_n_prior"] + SHARE_EXTRA[kind]
        for grp in groups:
            mask = (g == grp) & (qbs if grp == "QB" else True)
            sub = d[mask & d[f"{kind}_share"].notna().to_numpy()]
            if len(sub) >= MIN_TRAIN:
                m.share[(kind, grp)] = Linear.fit(sub, cols, sub[f"{kind}_share"].clip(0, 1).to_numpy(float))
    d = m.intermediates(tr, t)
    for raw, groups in (("targets", TARGET_GROUPS), ("carries", CARRY_GROUPS)):
        for grp in groups:
            mask = (g == grp) & (qbs if grp == "QB" else True)
            sub = d[mask]
            if len(sub) >= MIN_TRAIN:
                m.stack[(raw, grp)] = Linear.fit(sub, [f"l_struct_{raw}", f"l_e_{raw}"], sub[raw].to_numpy(float), kind="poisson")
    d = m.intermediates(tr, t)
    for grp in TARGET_GROUPS:
        sub = d[(g == grp) & (d["targets"] > 0).to_numpy()]
        if len(sub) >= MIN_TRAIN:
            m.rate[("cr", grp)] = Linear.fit(sub, ["p_cr", "o_cmp_allowed", "log_n_prior"], (sub.receptions / sub.targets).to_numpy(float),
                                             weights=sub.targets.to_numpy(float))
        sub = d[(g == grp) & (d["receptions"] > 0).to_numpy()]
        if len(sub) >= MIN_TRAIN:
            m.rate[("ypr", grp)] = Linear.fit(sub, ["p_ypr", "o_ypt_allowed", "f_ypa"], (sub.receiving_yards / sub.receptions).to_numpy(float),
                                              weights=sub.receptions.to_numpy(float))
    for grp in CARRY_GROUPS:
        mask = (g == grp) & (qbs if grp == "QB" else True) & (d["carries"] > 0).to_numpy()
        sub = d[mask]
        if len(sub) >= MIN_TRAIN:
            m.rate[("ypc", grp)] = Linear.fit(sub, ["p_ypc", "o_ypc_allowed", "exp_margin"], (sub.rushing_yards / sub.carries).to_numpy(float),
                                              weights=sub.carries.to_numpy(float))
    qb = d[qbs]
    if len(qb) >= MIN_TRAIN:
        m.rate[("attempts", "QB")] = Linear.fit(qb, ["vol_pa", "e_attempts", "exp_margin", "o_rate_allowed"], qb.attempts.to_numpy(float), kind="poisson")
        sub = qb[qb.attempts > 0]
        m.rate[("comp", "QB")] = Linear.fit(sub, ["p_comp", "o_cmp_allowed"], (sub.completions / sub.attempts).to_numpy(float),
                                            weights=sub.attempts.to_numpy(float))
        m.rate[("ypa", "QB")] = Linear.fit(sub, ["p_ypa", "o_ypa_allowed", "f_ypa"], (sub.passing_yards / sub.attempts).to_numpy(float),
                                           weights=sub.attempts.to_numpy(float))
    d = m.intermediates(tr, t)
    fit_distributions(m.dist, d, m.means(d))
    m.info = {"n_team_games": int(len(tt)), "n_player_rows": int(len(tr)), "train_seasons": [first_season, target_season - 1],
              "team_sd": {k: round(v, 3) for k, v in m.team_sd.items()}, "added_columns": {"snap": OWN, **SHARE_EXTRA},
              "train_data_observed_through": str(rows.loc[rows.season < target_season, "kickoff"].max())}
    return m


forecast = M.forecast
