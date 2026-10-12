"""PURE_PLAYER_V1_2 additional point-in-time features, from football box scores only.

Two families are added on top of PURE_PLAYER_V1's frozen features (nfl_edge/engines/player/pure_v1/features.py):

    positional opponent   for each defence, prior-only EWMs of what it allowed to each position group (RB / WR / TE):
                          share of the offence's pass attempts thrown to the group, catch rate, yards per target, share
                          of the offence's rush attempts carried by the group, yards per carry; and the same quantities
                          "over expected": what the defence allowed minus what each offence it faced was itself
                          expected to produce for that group at that time (the offence's own prior-only EWM), so a
                          defence is not credited for having faced weak offences. A (player, game) row reads its
                          opponent's values as of that game (the opponent's strictly prior games only).
    available pool        the team's opportunity pool as it stood after the team's previous game: every teammate who
                          played that game, with his mean share over his last three games. `pool_t` / `pool_c` is the
                          pool's total recent target / carry share (near 1 when the roster is unchanged; below 1 when
                          players who held shares have stopped playing -- injury, release, benching); `norm_t` /
                          `norm_c` is the player's own recent share over that total. Uses only finished box scores;
                          nothing about who will be active in the target game (that needs an injury report, which is
                          not point-in-time certified for 2025 -- see docs/research/PURE_PLAYER_V1_2_PREREGISTRATION.md).

Every value is computed from games whose kickoff precedes the target game; the team / opponent previous kickoffs are
already inside the frozen V1 `src_max`, which the pipeline asserts is before the forecast cutoff.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nfl_edge.engines.player.pure_v1.features import TEAM_SHRINK, ewm_prior

POS_GROUPS = ("RB", "WR", "TE")
DEF_NUM = ["tgt", "rec", "ryd", "car", "rsh"]
EPS = 1e-6


def _group_totals(rows: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    """One row per (offence team, game): per-group targets / receptions / receiving yards / carries / rushing yards,
    the offence's pass and rush attempts, the defence and the kickoff."""
    p = rows[rows["played"] & rows["pgroup"].isin(POS_GROUPS)]
    agg = p.groupby(["team", "game_id", "pgroup"]).agg(tgt=("targets", "sum"), rec=("receptions", "sum"), ryd=("receiving_yards", "sum"),
                                                       car=("carries", "sum"), rsh=("rushing_yards", "sum")).reset_index()
    w = agg.pivot_table(index=["team", "game_id"], columns="pgroup", values=DEF_NUM, fill_value=0.0)
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    w = w.reset_index()
    for g in POS_GROUPS:
        for c in DEF_NUM:
            if f"{c}_{g}" not in w.columns:
                w[f"{c}_{g}"] = 0.0
    base = t[["team", "game_id", "opponent", "season", "kickoff", "pa", "ra"]]
    return base.merge(w, on=["team", "game_id"], how="left").fillna({f"{c}_{g}": 0.0 for c in DEF_NUM for g in POS_GROUPS})


def defence_by_group(rows: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    """(defence, game_id) -> prior-only allowed-to-group rates and over-expected rates. Column `opponent` is the
    defence (named so that a player row joins on its own `opponent_team`)."""
    tg = _group_totals(rows, t)
    tg = tg[tg["pa"].notna()].reset_index(drop=True)
    num = [f"{c}_{g}" for g in POS_GROUPS for c in DEF_NUM] + ["pa", "ra"]
    first = sorted(tg["season"].unique())[:3]
    prior = tg[tg["season"].isin(first)][num].mean().to_numpy(float)
    # offence side: what each offence itself was expected to produce for each group (prior-only), per game
    off = ewm_prior(tg, "team", num, prior, shrink=TEAM_SHRINK, prefix="xo_")
    tg = pd.concat([tg, off], axis=1)

    def rates(src: pd.DataFrame, pre: str) -> dict:
        out = {}
        for g in POS_GROUPS:
            out[f"tsh_{g}"] = src[f"{pre}tgt_{g}"] / (src[f"{pre}pa"] + EPS)
            out[f"cr_{g}"] = src[f"{pre}rec_{g}"] / (src[f"{pre}tgt_{g}"] + EPS)
            out[f"ypt_{g}"] = src[f"{pre}ryd_{g}"] / (src[f"{pre}tgt_{g}"] + EPS)
            out[f"csh_{g}"] = src[f"{pre}car_{g}"] / (src[f"{pre}ra"] + EPS)
            out[f"ypc_{g}"] = src[f"{pre}rsh_{g}"] / (src[f"{pre}car_{g}"] + EPS)
        return out

    act = pd.DataFrame(rates(tg, ""), index=tg.index)
    exp = pd.DataFrame(rates(tg, "xo_"), index=tg.index)
    # realised rate is undefined without a denominator; such games carry no information for that rate
    for g in POS_GROUPS:
        for r, den in (("cr", f"tgt_{g}"), ("ypt", f"tgt_{g}"), ("ypc", f"car_{g}")):
            act.loc[tg[den] <= 0, f"{r}_{g}"] = np.nan
    oe = (act - exp).add_prefix("oe_")
    d = pd.concat([tg[["team", "game_id", "opponent", "season", "kickoff"]], tg[num], oe], axis=1)
    # defence side: EWM over the defence's strictly prior games of the allowed counts and of the over-expected rates
    d = d.rename(columns={"team": "offence", "opponent": "defence"})
    dn = ewm_prior(d, "defence", num, prior, shrink=TEAM_SHRINK, prefix="da_")
    oec = [c for c in d.columns if c.startswith("oe_")]
    de = ewm_prior(d, "defence", oec, np.zeros(len(oec)), shrink=TEAM_SHRINK, prefix="d")
    out = pd.concat([d[["defence", "game_id"]], pd.DataFrame(rates(dn, "da_"), index=d.index).add_prefix("dg_"), de.drop(columns=["dn"])], axis=1)
    out.columns = [c.replace("doe_", "dgoe_") for c in out.columns]
    return out.rename(columns={"defence": "opponent_team"})


def attach_defence(d: pd.DataFrame, dg: pd.DataFrame) -> pd.DataFrame:
    """Player rows (with `opponent_team`, `pgroup`) -> the opponent's allowed-to-own-group features:
    opp_tsh, opp_cr, opp_ypt, opp_csh, opp_ypc (levels) and opp_oe_* (over expected)."""
    m = d[["opponent_team", "game_id", "pgroup"]].merge(dg, on=["opponent_team", "game_id"], how="left")
    g = m["pgroup"].to_numpy()
    out = pd.DataFrame(index=d.index)
    for r in ("tsh", "cr", "ypt", "csh", "ypc"):
        for pre, name in (("dg_", f"opp_{r}"), ("dgoe_", f"opp_oe_{r}")):
            v = np.full(len(d), np.nan)
            for grp in POS_GROUPS:
                col = f"{pre}{r}_{grp}"
                if col in m.columns:
                    ix = g == grp
                    v[ix] = m.loc[ix, col].to_numpy(float)
            out[name] = v
    return pd.concat([d, out], axis=1)


def available_pool(rows: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    """(team, game_id) of every team-game -> per player row: pool_t, pool_c, norm_t, norm_c (see module docstring).

    Returns a frame aligned to `rows.index`."""
    r = rows.copy()
    seq = t[["team", "game_id", "team_seq", "season"]].rename(columns={"season": "tseason"})
    r = r.merge(seq, on=["team", "game_id"], how="left", suffixes=("", "_t")).set_index(rows.index)
    p = r[r["played"]].sort_values(["player_id", "kickoff", "game_id"], kind="mergesort")
    gp = p.groupby("player_id", sort=False)
    p = p.assign(r3_t=gp["target_share"].transform(lambda x: x.rolling(3, min_periods=1).mean()),
                 r3_c=gp["carry_share"].transform(lambda x: x.rolling(3, min_periods=1).mean()))
    tgt_pool = p[p["pgroup"].isin(POS_GROUPS)]
    car_pool = p[p["pgroup"].isin(("RB", "QB"))]
    pool_t = tgt_pool.groupby(["team", "team_seq"])["r3_t"].sum().rename("pool_sum_t")
    pool_c = car_pool.groupby(["team", "team_seq"])["r3_c"].sum().rename("pool_sum_c")
    # who played the team's previous game (for excluding the player's own contribution from the pool)
    mine = p[["player_id", "team", "team_seq", "r3_t", "r3_c"]]
    key = r[["player_id", "team", "team_seq", "tseason"]].copy()
    key["prev_seq"] = key["team_seq"] - 1
    prev_season = t[["team", "team_seq", "season"]].rename(columns={"team_seq": "prev_seq", "season": "prev_tseason"})
    key = key.merge(prev_season, on=["team", "prev_seq"], how="left")
    key = key.merge(pool_t.reset_index().rename(columns={"team_seq": "prev_seq"}), on=["team", "prev_seq"], how="left")
    key = key.merge(pool_c.reset_index().rename(columns={"team_seq": "prev_seq"}), on=["team", "prev_seq"], how="left")
    key = key.merge(mine.rename(columns={"team_seq": "prev_seq", "r3_t": "own_prev_t", "r3_c": "own_prev_c"}),
                    on=["player_id", "team", "prev_seq"], how="left")
    key.index = rows.index
    out = pd.DataFrame(index=rows.index)
    same_season = (key["prev_tseason"] == key["tseason"]).to_numpy()
    for s, kind in (("t", "target"), ("c", "carry")):
        own_recent = rows[f"last3_{kind}_share"].to_numpy(float)          # the player's own prior-only last-3 mean
        own_in_pool = key[f"own_prev_{s}"].fillna(0.0).to_numpy(float)    # his contribution if he played last game
        others = key[f"pool_sum_{s}"].fillna(0.0).to_numpy(float) - own_in_pool
        own = np.nan_to_num(own_recent, nan=0.0)
        total = others + own
        pool = np.where(same_season, total, 1.0)
        norm = np.where(same_season & (total > EPS), own / np.maximum(total, EPS), own)
        out[f"pool_{s}"] = pool
        out[f"norm_{s}"] = np.clip(norm, 0.0, 1.0)
        out[f"vac_{s}"] = np.clip(1.0 - pool, 0.0, 1.0) * out[f"norm_{s}"]
    return out
