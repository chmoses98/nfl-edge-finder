"""Opponent-defence features: what a defence has allowed, point-in-time.

The player mean model currently has no opponent term at all. It projects a receiver's yards from his own
history and the game's implied total, and is blind to whether he faces the league's best or worst coverage.
That is a real gap and a candidate for information the closing price may not fully contain
(research/model_vs_market: the market encompasses the model, model coefficient -0.02 +- 0.09).

Built exactly like the role features: aggregate what each defence allowed per game, then take an EWMA over
that defence's strictly-prior games with a season-boundary discount and shrinkage toward the league mean.
A defence's own current game never enters its own feature.
"""
from __future__ import annotations

import numpy as np
import polars as pl

from nfl_edge.features.opportunity import group_priors, point_in_time_ewma

ALLOWED = ["receptions", "receiving_yards", "targets", "rushing_yards", "carries",
           "passing_yards", "passing_tds", "any_td"]
DEF_FEATURES = [f"def_allowed_{c}" for c in ALLOWED] + ["def_allowed_rec_yds_per_target",
                                                        "def_allowed_rush_yds_per_carry"]


def build_defense_features(frame, halflife: float = 6.0, season_carry: float = 0.35, shrink_k: float = 4.0,
                           prior_seasons=(2016, 2017, 2018)):
    """Add point-in-time opponent-defence features to a player-game frame (pandas in, pandas out)."""
    was_pandas = not isinstance(frame, pl.DataFrame)
    df = pl.from_pandas(frame) if was_pandas else frame
    df = df.with_columns(pl.col("season").cast(pl.Int64), pl.col("week").cast(pl.Int64))

    # what each defence allowed in each game: sum over the offensive players it faced
    allowed = (df.group_by(["game_id", "opponent_team", "season", "week"])
               .agg([pl.col(c).sum().alias(f"def_allowed_{c}") for c in ALLOWED])
               .rename({"opponent_team": "defteam"}))
    e = 1e-6
    allowed = allowed.with_columns(
        def_allowed_rec_yds_per_target=pl.col("def_allowed_receiving_yards") / (pl.col("def_allowed_targets") + e),
        def_allowed_rush_yds_per_carry=pl.col("def_allowed_rushing_yards") / (pl.col("def_allowed_carries") + e),
    ).with_columns(position=pl.lit("DEF"))

    pri = group_priors(allowed.filter(pl.col("season").is_in(list(prior_seasons))), DEF_FEATURES,
                       list(prior_seasons), key="position")
    allowed = point_in_time_ewma(allowed, DEF_FEATURES, key="defteam", halflife=halflife,
                                 season_carry=season_carry, shrink_k=shrink_k, priors=pri,
                                 prior_key="position", prefix="pit_")
    keep = ["game_id", "defteam"] + [f"pit_{c}" for c in DEF_FEATURES]
    out = df.join(allowed.select(keep).rename({"defteam": "opponent_team"}),
                  on=["game_id", "opponent_team"], how="left")
    return out.to_pandas() if was_pandas else out


PIT_DEF_FEATURES = [f"pit_{c}" for c in DEF_FEATURES]


def has_defense_features(df) -> bool:
    return all(c in df.columns for c in PIT_DEF_FEATURES)
