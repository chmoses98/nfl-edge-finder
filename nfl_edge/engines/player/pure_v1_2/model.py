"""PURE_PLAYER_V1_2 fit: PURE_PLAYER_V1's staged model with the V1_2 feature families added to its stage designs.

The stage structure, estimators (ridge / Poisson, fixed penalty), training population, clipping, distribution
families and ladders are PURE_PLAYER_V1's (`pure_v1.model`), unchanged. Only the column lists below differ; every
fitted `Linear` stores its own columns, so `PureModel.intermediates` (frozen V1 code) evaluates a V1_2 model as is.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nfl_edge.engines.player.pure_v1 import model as M1
from nfl_edge.engines.player.pure_v1_2 import VERSION
from nfl_edge.engines.player.v4.linear import Linear

POOL = ["norm_t", "vac_t", "pool_t", "norm_c", "vac_c", "pool_c"]
SNAP = M1.SNAP + POOL                                                                    # (C)
SHARE_EXTRA = {"target": ["norm_t", "vac_t", "pool_t", "opp_tsh", "opp_oe_tsh"],         # (C) + (B)
               "carry": ["norm_c", "vac_c", "pool_c", "opp_csh", "opp_oe_csh"]}
RATE = {                                                                                 # (A) + (B)
    "cr": ["p_cr", "o_cmp_allowed", "log_n_prior", "opp_cr", "opp_oe_cr", "vol_pts"],
    "ypr": ["p_ypr", "o_ypt_allowed", "f_ypa", "opp_ypt", "opp_oe_ypt", "vol_pts", "exp_margin"],
    "ypc": ["p_ypc", "o_ypc_allowed", "exp_margin", "opp_ypc", "opp_oe_ypc", "vol_pts"],
    "attempts": ["vol_pa", "e_attempts", "exp_margin", "o_rate_allowed"],                # unchanged from V1
    "comp": ["p_comp", "o_cmp_allowed", "vol_pts", "exp_margin"],
    "ypa": ["p_ypa", "o_ypa_allowed", "f_ypa", "vol_pts", "exp_margin"],
}
NEW_FEATURES = sorted(set(POOL + SHARE_EXTRA["target"] + SHARE_EXTRA["carry"] + sum(RATE.values(), [])) - set(
    M1.SNAP + M1.PLAYER_CONTEXT + ["p_cr", "p_ypr", "p_ypc", "p_comp", "p_ypa", "log_n_prior", "f_ypa", "vol_pa", "e_attempts"]))


def fit(rows: pd.DataFrame, t: pd.DataFrame, target_season: int, *, first_season: int = M1.FIRST_SEASON) -> M1.PureModel:
    """Fit every stage on seasons [first_season, target_season); same training population as PURE_PLAYER_V1."""
    m = M1.PureModel(target_season=target_season, first_season=first_season, version=VERSION)
    tt = t[(t.season < target_season) & (t.season >= first_season) & t.pa.notna() & t.pts.notna()]
    for name, cols, y in (("pa", M1.TEAM_PA, tt.pa), ("ra", M1.TEAM_RA, tt.ra), ("pts", M1.TEAM_PTS, tt.pts)):
        m.team[name] = Linear.fit(tt, cols, y.to_numpy(float))
        m.team_sd[name] = float(np.std(y.to_numpy(float) - m.team[name].predict(tt)))
    tr = rows[(rows.season < target_season) & (rows.season >= first_season) & rows.played].copy()
    g = tr["pgroup"].to_numpy()
    qbs = (g == "QB") & tr["qb_starter"].to_numpy(bool)
    sm = M1.population(tr, "snap_share") & np.isfinite(tr["snap_share"].to_numpy(float))
    for grp in ("QB", "RB", "WR", "TE"):
        sub = tr[sm & (g == grp)]
        if len(sub) >= M1.MIN_TRAIN:
            m.snap[grp] = Linear.fit(sub, SNAP, sub["snap_share"].clip(0, 1).to_numpy(float))
    d = m.intermediates(tr, t)
    for kind, groups in (("target", M1.TARGET_GROUPS), ("carry", M1.CARRY_GROUPS)):
        cols = [f"e_{kind}_share", f"last_{kind}_share", f"last3_{kind}_share", f"cur_{kind}_share", "snap_mean", f"struct_{kind}",
                "changed_team", "n_cur_c", "log_n_prior"] + SHARE_EXTRA[kind]
        for grp in groups:
            mask = (g == grp) & (qbs if grp == "QB" else True)
            sub = d[mask & d[f"{kind}_share"].notna().to_numpy()]
            if len(sub) >= M1.MIN_TRAIN:
                m.share[(kind, grp)] = Linear.fit(sub, cols, sub[f"{kind}_share"].clip(0, 1).to_numpy(float))
    d = m.intermediates(tr, t)
    for raw, groups in (("targets", M1.TARGET_GROUPS), ("carries", M1.CARRY_GROUPS)):
        for grp in groups:
            mask = (g == grp) & (qbs if grp == "QB" else True)
            sub = d[mask]
            if len(sub) >= M1.MIN_TRAIN:
                m.stack[(raw, grp)] = Linear.fit(sub, [f"l_struct_{raw}", f"l_e_{raw}"], sub[raw].to_numpy(float), kind="poisson")
    d = m.intermediates(tr, t)
    for grp in M1.TARGET_GROUPS:
        sub = d[(g == grp) & (d["targets"] > 0).to_numpy()]
        if len(sub) >= M1.MIN_TRAIN:
            m.rate[("cr", grp)] = Linear.fit(sub, RATE["cr"], (sub.receptions / sub.targets).to_numpy(float), weights=sub.targets.to_numpy(float))
        sub = d[(g == grp) & (d["receptions"] > 0).to_numpy()]
        if len(sub) >= M1.MIN_TRAIN:
            m.rate[("ypr", grp)] = Linear.fit(sub, RATE["ypr"], (sub.receiving_yards / sub.receptions).to_numpy(float),
                                              weights=sub.receptions.to_numpy(float))
    for grp in M1.CARRY_GROUPS:
        mask = (g == grp) & (qbs if grp == "QB" else True) & (d["carries"] > 0).to_numpy()
        sub = d[mask]
        if len(sub) >= M1.MIN_TRAIN:
            m.rate[("ypc", grp)] = Linear.fit(sub, RATE["ypc"], (sub.rushing_yards / sub.carries).to_numpy(float), weights=sub.carries.to_numpy(float))
    qb = d[qbs]
    if len(qb) >= M1.MIN_TRAIN:
        m.rate[("attempts", "QB")] = Linear.fit(qb, RATE["attempts"], qb.attempts.to_numpy(float), kind="poisson")
        sub = qb[qb.attempts > 0]
        m.rate[("comp", "QB")] = Linear.fit(sub, RATE["comp"], (sub.completions / sub.attempts).to_numpy(float), weights=sub.attempts.to_numpy(float))
        m.rate[("ypa", "QB")] = Linear.fit(sub, RATE["ypa"], (sub.passing_yards / sub.attempts).to_numpy(float), weights=sub.attempts.to_numpy(float))
    d = m.intermediates(tr, t)
    M1.fit_distributions(m.dist, d, m.means(d))
    m.info = {"n_team_games": int(len(tt)), "n_player_rows": int(len(tr)), "train_seasons": [first_season, target_season - 1],
              "team_sd": {k: round(v, 3) for k, v in m.team_sd.items()}, "new_features": NEW_FEATURES,
              "train_data_observed_through": str(rows.loc[rows.season < target_season, "kickoff"].max())}
    return m
