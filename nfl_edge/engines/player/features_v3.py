"""Point-in-time features for DATA_PLAYER_DIST v3: recency and explicit opportunity structure on top of v2.

What v3 adds, and why (research/player_engine_v3/RESULTS.md has the evidence):

    recency          the player's snap / target / carry share in his LAST prior game and the mean of his last three.
                     The v2 EWMA (half-life 6 games, 0.35 season carry) answers "what has this player been"; a role
                     that changed last week is visible only here. Every value is from strictly prior games
                     (shift(1) inside the player's chronological history), so a prospective row can never see its
                     own game.
    season recency   the number of prior games in the CURRENT season, and whether the player's most recent game
                     was for a different team (a trade / signing the EWMA cannot know about).
    structure        projected targets = team pass-attempt EWMA x target-share EWMA; projected carries likewise.
                     The v2 regression had both factors but only additively; the product is the opportunity the
                     decomposition actually implies, so team volume and share now reconcile by construction.

Nothing here reads a line, a price or an outcome of the game being projected.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

V3_EXTRA = ["last_snap_share", "last3_snap_share", "last_target_share", "last3_target_share", "last_carry_share",
            "last3_carry_share", "n_cur_season", "changed_team", "proj_targets_struct", "proj_carries_struct"]


def add_v3_features(df: pd.DataFrame) -> pd.DataFrame:
    """Requires the v2 columns (target_share / carry_share / snap_share realised, and their EWMAs)."""
    df = df.copy()
    order = df.sort_values(["player_id", "season", "week"], kind="mergesort").index
    d = df.loc[order]
    g = d.groupby("player_id", sort=False)
    for c, name in (("snap_share", "snap_share"), ("target_share", "target_share"), ("carry_share", "carry_share")):
        prev = g[c].shift(1)
        d[f"last_{name}"] = prev
        d[f"last3_{name}"] = g[c].transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    # prior games this season (a prospective row counts the season's completed games before it)
    d["_one"] = d[["targets", "carries", "offense_snaps"]].notna().any(axis=1).astype(float)
    d["n_cur_season"] = d.groupby(["player_id", "season"], sort=False)["_one"].transform(lambda s: s.shift(1).fillna(0).cumsum())
    prev_team = g["team"].shift(1)
    d["last_team"] = prev_team
    d["changed_team"] = ((prev_team.notna()) & (prev_team != d["team"])).astype(float)
    d = d.drop(columns=["_one"])
    df = d.reindex(df.index)
    # missing recency (no prior game): fall back to the EWMA, never to zero -- "no data" and "no usage" differ
    for name in ("snap_share", "target_share", "carry_share"):
        for pre in ("last_", "last3_"):
            col = f"{pre}{name}"
            df[col] = df[col].where(df[col].notna(), df[f"ewma_{name}"])
    df["proj_targets_struct"] = df["ewma_team_pass_att"] * df["ewma_target_share"]
    df["proj_carries_struct"] = df["ewma_team_rush_att"] * df["ewma_carry_share"]
    return df


def has_v3_features(df: pd.DataFrame) -> bool:
    return all(c in df.columns for c in V3_EXTRA)
