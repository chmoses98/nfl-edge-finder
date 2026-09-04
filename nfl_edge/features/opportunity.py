"""Player opportunity engine: decompose production into team volume x player role.

The baseline feature layer is an EWMA of a player's raw counting stats. That confounds two things which move
for entirely different reasons: how much the *team* throws or runs (game script, pace, opponent, the market's
own spread and total), and what *share* of that the player takes (role, injuries above him on the depth
chart, personnel packages). A back-up who is promoted has a stable share history of ~0 and a raw-target
history of ~0; the decomposition lets his share jump the moment the role does, while raw EWMA needs weeks to
catch up.

    targets_i   ~ team_dropbacks   x  route_share_i  x  targets_per_route_i
    carries_i   ~ team_rush_att    x  carry_share_i

Routes are real, not a snap proxy: nflverse `pbp_participation.offense_players` lists the 11 men on the field
for every play from 2016 through 2025 (92% of plays in the early seasons, 100% from 2023). A route is a
dropback the player was on the field for.

Everything is point-in-time. Shares are EWMAs over the player's strictly-prior games with the same season
carry and shrinkage as the baseline; team volume is an EWMA over the team's strictly-prior games combined
with the pre-game market line. No quantity on a row is computed from that row's own game.
"""
from __future__ import annotations

import glob
import os

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PBP = os.path.join(ROOT, "data", "raw", "nflverse", "pbp")
PART = os.path.join(ROOT, "data", "raw", "nflverse", "pbp_participation")

PBP_COLS = ["game_id", "play_id", "posteam", "season", "week", "pass", "rush", "qb_dropback", "sack",
            "qb_scramble", "rusher_player_id", "receiver_player_id", "yardline_100", "air_yards",
            "two_point_attempt", "play_type", "pass_touchdown", "rush_touchdown", "epa"]


def _season_usage(season: int) -> tuple[pl.DataFrame, pl.DataFrame]:
    """(player-game usage, team-game volume) for one season."""
    p = pl.read_parquet(os.path.join(PBP, f"play_by_play_{season}.parquet"), columns=PBP_COLS)
    p = p.filter(pl.col("posteam").is_not_null() & pl.col("play_type").is_in(["pass", "run"]))
    p = p.with_columns(
        is_dropback=(pl.col("qb_dropback").fill_null(0) == 1),
        is_rush=((pl.col("rush").fill_null(0) == 1) & (pl.col("qb_scramble").fill_null(0) == 0)),
        rz=(pl.col("yardline_100") <= 20), i10=(pl.col("yardline_100") <= 10), i5=(pl.col("yardline_100") <= 5),
    )
    team = p.group_by(["game_id", "posteam"]).agg(
        team_plays=pl.len(),
        team_dropbacks=pl.col("is_dropback").sum(),
        team_rush_att=pl.col("is_rush").sum(),
        team_rz_plays=pl.col("rz").sum(),
        team_rz_dropbacks=(pl.col("rz") & pl.col("is_dropback")).sum(),
        team_rz_rush=(pl.col("rz") & pl.col("is_rush")).sum(),
        team_i5_rush=(pl.col("i5") & pl.col("is_rush")).sum(),
        team_air_yards=pl.col("air_yards").sum(),
        team_epa=pl.col("epa").mean(),
    ).rename({"posteam": "team"})

    # targets and carries are attributed directly by the play's own participant columns
    tg = (p.filter(pl.col("receiver_player_id").is_not_null())
          .group_by(["game_id", "receiver_player_id"])
          .agg(targets=pl.len(), rz_targets=pl.col("rz").sum(), i10_targets=pl.col("i10").sum(),
               air_yards=pl.col("air_yards").sum())
          .rename({"receiver_player_id": "player_id"}))
    ca = (p.filter(pl.col("rusher_player_id").is_not_null() & pl.col("is_rush"))
          .group_by(["game_id", "rusher_player_id"])
          .agg(carries=pl.len(), rz_carries=pl.col("rz").sum(), i5_carries=pl.col("i5").sum())
          .rename({"rusher_player_id": "player_id"}))

    # routes: the player was on the field for a dropback
    part = pl.read_parquet(os.path.join(PART, f"pbp_participation_{season}.parquet"),
                           columns=["nflverse_game_id", "play_id", "offense_players"])
    part = part.filter(pl.col("offense_players").is_not_null() & (pl.col("offense_players").str.len_chars() > 0))
    part = part.rename({"nflverse_game_id": "game_id"}).with_columns(pl.col("play_id").cast(pl.Int64))
    j = p.select(["game_id", "play_id", "posteam", "is_dropback", "is_rush", "rz"]) \
          .with_columns(pl.col("play_id").cast(pl.Int64)).join(part, on=["game_id", "play_id"], how="inner")
    j = j.with_columns(pl.col("offense_players").str.split(";")).explode("offense_players")
    j = j.filter(pl.col("offense_players").str.len_chars() > 0).rename({"offense_players": "player_id"})
    ro = j.group_by(["game_id", "player_id"]).agg(
        usage_team=pl.col("posteam").mode().first(),
        pbp_snaps=pl.len(), routes=pl.col("is_dropback").sum(), rush_snaps=pl.col("is_rush").sum(),
        rz_routes=(pl.col("rz") & pl.col("is_dropback")).sum(), rz_snaps=pl.col("rz").sum())
    # how many plays did participation actually cover for this game/team (denominator honesty)
    cov = j.group_by(["game_id", "posteam"]).agg(part_plays=pl.col("play_id").n_unique()).rename({"posteam": "team"})

    usage = ro.join(tg, on=["game_id", "player_id"], how="full", coalesce=True) \
              .join(ca, on=["game_id", "player_id"], how="full", coalesce=True)
    usage = usage.with_columns(pl.col(c).fill_null(0) for c in
                               ["pbp_snaps", "routes", "rush_snaps", "rz_routes", "rz_snaps", "targets",
                                "rz_targets", "i10_targets", "carries", "rz_carries", "i5_carries"])
    usage = usage.with_columns(season=pl.lit(season, dtype=pl.Int64))
    team = team.join(cov, on=["game_id", "team"], how="left").with_columns(
        season=pl.lit(season, dtype=pl.Int64),
        part_coverage=(pl.col("part_plays") / pl.col("team_plays")).clip(0, 1.5))
    return usage, team


def build_usage(seasons: list[int], out_dir: str | None = None) -> tuple[pl.DataFrame, pl.DataFrame]:
    us, ts = [], []
    for s in seasons:
        if not os.path.exists(os.path.join(PART, f"pbp_participation_{s}.parquet")):
            continue
        u, t = _season_usage(s)
        us.append(u); ts.append(t)
    usage = pl.concat(us, how="diagonal_relaxed"); team = pl.concat(ts, how="diagonal_relaxed")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        usage.write_parquet(os.path.join(out_dir, "player_usage.parquet"))
        team.write_parquet(os.path.join(out_dir, "team_volume.parquet"))
    return usage, team


SHARE_COLS = ["route_share", "target_share", "tprr", "carry_share", "rz_route_share", "rz_target_share",
              "rz_carry_share", "i5_carry_share", "snap_share", "adot", "air_yards_share"]


def attach_shares(usage: pl.DataFrame, team: pl.DataFrame) -> pl.DataFrame:
    """Per player-game shares of the team's own volume in that game (an outcome, not yet a feature)."""
    d = usage.join(team.drop("season"), on=["game_id", "team"], how="inner") if "team" in usage.columns else None
    if d is None:
        raise ValueError("usage must carry a team column; join the roster first")
    e = 1e-6
    return d.with_columns(
        route_share=pl.col("routes") / (pl.col("team_dropbacks") + e),
        target_share=pl.col("targets") / (pl.col("team_dropbacks") + e),
        tprr=pl.col("targets") / (pl.col("routes") + e),
        carry_share=pl.col("carries") / (pl.col("team_rush_att") + e),
        rz_route_share=pl.col("rz_routes") / (pl.col("team_rz_dropbacks") + e),
        rz_target_share=pl.col("rz_targets") / (pl.col("team_rz_dropbacks") + e),
        rz_carry_share=pl.col("rz_carries") / (pl.col("team_rz_rush") + e),
        i5_carry_share=pl.col("i5_carries") / (pl.col("team_i5_rush") + e),
        snap_share=pl.col("pbp_snaps") / (pl.col("team_plays") + e),
        adot=pl.col("air_yards") / (pl.col("targets") + e),
        air_yards_share=pl.col("air_yards") / (pl.col("team_air_yards") + e),
    )


def point_in_time_ewma(df: pl.DataFrame, cols: list[str], key: str = "player_id", halflife: float = 5.0,
                       season_carry: float = 0.5, shrink_k: float = 3.0,
                       priors: dict[str, np.ndarray] | None = None, prior_key: str = "position",
                       prefix: str = "pit_") -> pl.DataFrame:
    """EWMA of `cols` over strictly-prior rows of each `key`, shrunk toward a group prior.

    Identical recursion to the baseline feature layer, applied to shares instead of raw counts. The value
    written on row i uses rows 0..i-1 only; the update happens after the write.
    """
    df = df.sort([key, "season", "week"])
    X = df.select(cols).to_numpy().astype(float)
    ids = df[key].to_numpy()
    season = df["season"].to_numpy()
    grp = df[prior_key].to_numpy() if prior_key in df.columns else np.array([""] * df.height)
    n, m = X.shape
    d = 0.5 ** (1.0 / halflife)
    out = np.full((n, m), np.nan)
    w_eff = np.zeros(n)
    n_prior = np.zeros(n, dtype=int)
    zero = np.zeros(m)
    S = np.zeros(m); W = np.zeros(m); cur = None; last = None; cnt = 0
    for i in range(n):
        if ids[i] != cur:
            cur = ids[i]; S = np.zeros(m); W = np.zeros(m); cnt = 0; last = season[i]
        elif season[i] != last:
            c = season_carry ** max(1, int(season[i] - last))
            S = S * c; W = W * c; last = season[i]
        pr = priors.get(grp[i], zero) if priors else zero
        out[i] = (S + shrink_k * pr) / (W + shrink_k)
        w_eff[i] = W[0]; n_prior[i] = cnt
        v = X[i]; msk = np.isfinite(v)
        S = S * d; W = W * d
        S[msk] += v[msk]; W[msk] += 1.0
        cnt += 1
    for j, c in enumerate(cols):
        df = df.with_columns(pl.Series(f"{prefix}{c}", out[:, j]))
    return df.with_columns(pl.Series(f"{prefix}w_eff", w_eff), pl.Series(f"{prefix}n_prior", n_prior),
                           pl.Series(f"{prefix}shrink_w", shrink_k / (w_eff + shrink_k)))


def group_priors(df: pl.DataFrame, cols: list[str], seasons: list[int], key: str = "position") -> dict:
    sub = df.filter(pl.col("season").is_in(seasons))
    out = {}
    for g, sd in sub.group_by(key):
        name = g[0] if isinstance(g, tuple) else g
        out[name] = np.nan_to_num(sd.select(cols).mean().to_numpy()[0], nan=0.0)
    return out
