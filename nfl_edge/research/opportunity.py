"""Player OPPORTUNITY engine: point-in-time role/volume features + walk-forward models.

What this module is for
-----------------------
Downstream ladder pricing needs, for every player-game, a projection of *opportunity*
(snap share, targets, carries, pass attempts, dropbacks, red-zone / inside-5 chances)
together with the dispersion of that projection, so that the conditional distribution
families fitted in ``player_distributions`` have something better than a naive EWMA to
condition on.  ``research/role_features`` showed snap-share features cut target MAE ~3%
and carry MAE ~4-7%; this module turns that into a reusable model.

Leakage discipline
------------------
Every feature for a player-game g is a function of rows strictly earlier than the
kickoff of g:

  * own-history EWMAs are recorded BEFORE the row's own outcome is folded into the
    recursion (two half-lives, season-boundary discount, shrinkage to a position prior
    estimated once on pre-window seasons);
  * team-level EWMAs are built from the team's prior games only;
  * depth chart: the weekly chart for that week pre-2025, the LATEST daily ESPN chart
    strictly before kickoff for 2025+;
  * roster status / injury report: the week's rows, injuries additionally filtered by
    ``date_modified < kickoff``;
  * teammate reallocation: shares of same-position teammates as of their own last game,
    gated on *pregame* availability (roster status + injury report), never on the
    teammate's outcome in this game.

``build_features(root, seasons, cutoff=...)`` makes this testable: with a cutoff, every
game whose kickoff is >= cutoff has its outcomes blanked and contributes nothing to any
aggregate, so features for a game at the cutoff must be bit-identical to the ones built
on the full dataset.  ``tests/test_opportunity_leakage.py`` asserts exactly that.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import polars as pl

from nfl_edge.research.player_distributions import load_player_games

MODEL_VERSION = "opp-1.0.0"
SKILL_POS = ["QB", "RB", "WR", "TE"]
TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA", "LAR": "LA", "SL": "LA", "ARZ": "ARI",
            "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "JAC": "JAX"}

# ------------------------------------------------------------------ column groups
# per-player raw opportunity counts recorded for each player-game
PLAYER_COUNTS = [
    "offense_snaps_pbp", "targets", "carries", "attempts", "sacks_taken", "scrambles",
    "dropbacks", "air_yards", "rz_targets", "rz_carries", "i10_opp", "i5_opp", "routes",
]
# per-player shares of the team total in the same game
PLAYER_SHARES = [
    "snap_share", "target_share", "carry_share", "dropback_share", "air_yards_share",
    "routes_share", "rz_target_share", "rz_carry_share", "i10_share", "i5_share",
]
EWMA_COLS = PLAYER_COUNTS + PLAYER_SHARES
# subset carried forward for the teammate-reallocation feature (post-game EWMA)
POST_COLS = ["target_share", "carry_share", "snap_share", "targets", "carries"]

TEAM_COLS = [
    "team_plays", "team_dropbacks", "team_pass_attempts", "team_carries", "team_targets",
    "team_air_yards", "team_rz_targets", "team_rz_carries", "team_i10_opp", "team_i5_opp",
    "neutral_pass_rate", "proe", "sec_per_play", "rz_trips",
]

HALFLIVES = (3.0, 8.0)


# ------------------------------------------------------------------ generic helpers
def _norm_team(expr: pl.Expr) -> pl.Expr:
    return expr.replace(TEAM_FIX)


def _kickoff_expr() -> pl.Expr:
    """gameday (date str) + gametime (ET 'HH:MM') -> UTC timestamp."""
    t = pl.col("gametime").fill_null("13:00")
    return (
        (pl.col("gameday").cast(pl.Utf8) + pl.lit(" ") + t)
        .str.to_datetime("%Y-%m-%d %H:%M", time_zone="America/New_York", ambiguous="earliest")
        .dt.convert_time_zone("UTC")
        .dt.replace_time_zone(None)
        .alias("kickoff")
    )


def load_schedule(root: str) -> pl.DataFrame:
    g = pl.read_parquet(os.path.join(root, "data/silver/games.parquet"))
    g = g.filter(pl.col("game_type") == "REG")
    g = g.with_columns(_kickoff_expr())
    return g.select(["game_id", "season", "week", "kickoff", "home_team", "away_team",
                     "spread_line", "total_line", "roof", "home_qb_id", "away_qb_id"])


# ------------------------------------------------------------------ play-by-play aggregates
_SCRIMMAGE = (
    ((pl.col("pass_attempt") == 1) | (pl.col("rush_attempt") == 1))
    & (~pl.col("play_type").is_in(["qb_kneel", "qb_spike"]))
)


def pbp_aggregates(root: str, seasons) -> tuple[pl.DataFrame, pl.DataFrame]:
    """(player-game opportunity counts, team-game context) from play-by-play, REG only."""
    want = ["game_id", "season", "week", "season_type", "posteam", "play_type", "pass_attempt",
            "rush_attempt", "sack", "qb_dropback", "qb_scramble", "passer_player_id",
            "receiver_player_id", "rusher_player_id", "yardline_100", "air_yards", "pass_oe",
            "game_seconds_remaining", "fixed_drive", "play_id", "qtr", "score_differential", "wp"]
    p_frames, t_frames = [], []
    for s in seasons:
        path = os.path.join(root, "data/raw/nflverse/pbp", f"play_by_play_{s}.parquet")
        if not os.path.exists(path):
            continue
        names = pl.scan_parquet(path).collect_schema().names()
        cols = [c for c in want if c in names]
        d = pl.read_parquet(path, columns=cols).filter(pl.col("season_type") == "REG")
        d = d.with_columns(_norm_team(pl.col("posteam")).alias("posteam"))
        d = d.filter(pl.col("posteam").is_not_null())
        scr = d.filter(_SCRIMMAGE)

        rec = (scr.filter((pl.col("pass_attempt") == 1) & pl.col("receiver_player_id").is_not_null())
               .group_by(["game_id", "posteam", "receiver_player_id"]).agg([
                   pl.len().alias("targets"),
                   pl.col("air_yards").fill_null(0).sum().alias("air_yards"),
                   (pl.col("yardline_100") <= 20).sum().alias("rz_targets"),
                   (pl.col("yardline_100") <= 10).sum().alias("i10_targets"),
                   (pl.col("yardline_100") <= 5).sum().alias("i5_targets"),
               ]).rename({"receiver_player_id": "player_id"}))
        rush = (scr.filter((pl.col("rush_attempt") == 1) & pl.col("rusher_player_id").is_not_null())
                .group_by(["game_id", "posteam", "rusher_player_id"]).agg([
                    pl.len().alias("carries"),
                    (pl.col("qb_scramble") == 1).sum().alias("scrambles"),
                    (pl.col("yardline_100") <= 20).sum().alias("rz_carries"),
                    (pl.col("yardline_100") <= 10).sum().alias("i10_carries"),
                    (pl.col("yardline_100") <= 5).sum().alias("i5_carries"),
                ]).rename({"rusher_player_id": "player_id"}))
        pas = (scr.filter(pl.col("passer_player_id").is_not_null())
               .group_by(["game_id", "posteam", "passer_player_id"]).agg([
                   ((pl.col("pass_attempt") == 1) & (pl.col("sack") != 1)).sum().alias("pass_attempts"),
                   (pl.col("sack") == 1).sum().alias("sacks_taken"),
               ]).rename({"passer_player_id": "player_id"}))
        pg = rec.join(rush, on=["game_id", "posteam", "player_id"], how="full", coalesce=True)
        pg = pg.join(pas, on=["game_id", "posteam", "player_id"], how="full", coalesce=True)
        pg = pg.with_columns([pl.col(c).fill_null(0) for c in
                              ["targets", "air_yards", "rz_targets", "i10_targets", "i5_targets",
                               "carries", "scrambles", "rz_carries", "i10_carries", "i5_carries",
                               "pass_attempts", "sacks_taken"]])
        pg = pg.with_columns([
            (pl.col("pass_attempts") + pl.col("sacks_taken") + pl.col("scrambles")).alias("dropbacks"),
            (pl.col("i10_targets") + pl.col("i10_carries")).alias("i10_opp"),
            (pl.col("i5_targets") + pl.col("i5_carries")).alias("i5_opp"),
        ]).drop(["i10_targets", "i5_targets", "i10_carries", "i5_carries"])
        p_frames.append(pg)

        is_pass = (pl.col("pass_attempt") == 1) | (pl.col("sack") == 1) | (pl.col("qb_scramble") == 1)
        tg = scr.group_by(["game_id", "posteam"]).agg([
            pl.len().alias("team_plays"),
            ((pl.col("pass_attempt") == 1) & (pl.col("sack") != 1)).sum().alias("team_pass_attempts"),
            (pl.col("sack") == 1).sum().alias("team_sacks"),
            (pl.col("qb_scramble") == 1).sum().alias("team_scrambles"),
            ((pl.col("pass_attempt") == 1) & pl.col("receiver_player_id").is_not_null()).sum().alias("team_targets"),
            ((pl.col("rush_attempt") == 1) & pl.col("rusher_player_id").is_not_null()).sum().alias("team_carries"),
            pl.col("air_yards").fill_null(0).sum().alias("team_air_yards"),
            ((pl.col("pass_attempt") == 1) & (pl.col("yardline_100") <= 20)).sum().alias("team_rz_targets"),
            ((pl.col("rush_attempt") == 1) & (pl.col("yardline_100") <= 20)).sum().alias("team_rz_carries"),
            (pl.col("yardline_100") <= 10).sum().alias("team_i10_opp"),
            (pl.col("yardline_100") <= 5).sum().alias("team_i5_opp"),
            pl.col("pass_oe").mean().alias("proe"),
        ]).with_columns(
            (pl.col("team_pass_attempts") + pl.col("team_sacks") + pl.col("team_scrambles")).alias("team_dropbacks"))

        neu = (scr.filter((pl.col("qtr") <= 3) & (pl.col("wp").is_between(0.2, 0.8))
                          & (pl.col("score_differential").abs() <= 10))
               .group_by(["game_id", "posteam"]).agg(is_pass.mean().alias("neutral_pass_rate")))
        pace = (scr.sort(["game_id", "play_id"])
                .with_columns((pl.col("game_seconds_remaining").shift(1).over(["game_id", "fixed_drive"])
                               - pl.col("game_seconds_remaining")).alias("_dt"))
                .filter((pl.col("_dt") > 0) & (pl.col("_dt") <= 60))
                .group_by(["game_id", "posteam"]).agg(pl.col("_dt").mean().alias("sec_per_play")))
        rzt = (d.filter(pl.col("yardline_100") <= 20).group_by(["game_id", "posteam"])
               .agg(pl.col("fixed_drive").n_unique().alias("rz_trips")))
        tg = tg.join(neu, on=["game_id", "posteam"], how="left") \
               .join(pace, on=["game_id", "posteam"], how="left") \
               .join(rzt, on=["game_id", "posteam"], how="left")
        t_frames.append(tg)
    player = pl.concat(p_frames, how="diagonal_relaxed") if p_frames else pl.DataFrame()
    team = pl.concat(t_frames, how="diagonal_relaxed") if t_frames else pl.DataFrame()
    return player, team


def routes_from_participation(root: str, seasons) -> pl.DataFrame:
    """Routes proxy = number of team dropbacks the player was on the field for (2016+ only).

    nflverse participation gives the 11 offensive players per play; counting the dropback
    plays a player was on the field for is a strict upper bound on routes run (it includes
    pass-blocking backs/TEs), which is why this is called a proxy.  Unavailable pre-2016.
    """
    dbid = []
    for s in seasons:
        pp = os.path.join(root, "data/raw/nflverse/pbp_participation", f"pbp_participation_{s}.parquet")
        pb = os.path.join(root, "data/raw/nflverse/pbp", f"play_by_play_{s}.parquet")
        if not (os.path.exists(pp) and os.path.exists(pb)):
            continue
        db = (pl.read_parquet(pb, columns=["game_id", "play_id", "season_type", "qb_dropback"])
              .filter((pl.col("season_type") == "REG") & (pl.col("qb_dropback") == 1))
              .select(["game_id", pl.col("play_id").cast(pl.Int64)]))
        par = (pl.read_parquet(pp, columns=["nflverse_game_id", "play_id", "offense_players"])
               .rename({"nflverse_game_id": "game_id"})
               .with_columns(pl.col("play_id").cast(pl.Int64)))
        j = db.join(par, on=["game_id", "play_id"], how="inner")
        j = j.filter(pl.col("offense_players").fill_null("").str.len_chars() > 0)
        j = j.with_columns(pl.col("offense_players").str.split(";").alias("pids")).explode("pids")
        j = j.filter(pl.col("pids").str.len_chars() > 0)
        dbid.append(j.group_by(["game_id", "pids"]).agg(pl.len().alias("routes"))
                    .rename({"pids": "player_id"}))
    if not dbid:
        return pl.DataFrame({"game_id": [], "player_id": [], "routes": []})
    return pl.concat(dbid, how="diagonal_relaxed")


def load_snap_pct(root: str, seasons) -> pl.DataFrame:
    frames = []
    for s in seasons:
        p = os.path.join(root, "data/raw/nflverse/snap_counts", f"snap_counts_{s}.parquet")
        if os.path.exists(p):
            frames.append(pl.read_parquet(p).filter(pl.col("game_type") == "REG")
                          .select(["game_id", "pfr_player_id", "offense_snaps", "offense_pct"]))
    sc = pl.concat(frames, how="diagonal_relaxed")
    cw = (pl.read_parquet(os.path.join(root, "data/silver/player_crosswalk.parquet"))
          .select(["gsis_id", "pfr_id"]).drop_nulls().unique(subset=["pfr_id"], keep="first"))
    sc = sc.join(cw, left_on="pfr_player_id", right_on="pfr_id", how="inner")
    return (sc.select([pl.col("gsis_id").alias("player_id"), "game_id",
                       pl.col("offense_snaps").alias("offense_snaps_pbp"),
                       pl.col("offense_pct").alias("snap_share")])
            .unique(subset=["player_id", "game_id"], keep="first"))


# ------------------------------------------------------------------ weekly status sources
def load_depth_charts(root: str, seasons) -> tuple[pl.DataFrame, pl.DataFrame]:
    """(weekly charts pre-2025, daily ESPN charts 2025+).  Returns two frames with a common
    schema so callers can join weekly by (season, week, player_id) and daily as-of kickoff."""
    weekly, daily = [], []
    for s in seasons:
        p = os.path.join(root, "data/raw/nflverse/depth_charts", f"depth_charts_{s}.parquet")
        if not os.path.exists(p):
            continue
        names = pl.scan_parquet(p).collect_schema().names()
        if "depth_team" in names:                       # legacy weekly format (2001-2024)
            d = pl.read_parquet(p)
            if "game_type" in names:
                d = d.filter(pl.col("game_type") == "REG")
            if "formation" in names:
                d = d.filter(pl.col("formation") == "Offense")
            d = d.filter(pl.col("gsis_id").is_not_null())
            weekly.append(d.select([
                pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32),
                pl.col("gsis_id").alias("player_id"),
                pl.col("depth_team").cast(pl.Int32, strict=False).alias("depth_rank"),
            ]).group_by(["season", "week", "player_id"]).agg(pl.col("depth_rank").min()))
        elif "pos_rank" in names:                       # ESPN daily format (2025+)
            d = pl.read_parquet(p).filter(pl.col("gsis_id").is_not_null())
            d = d.filter(pl.col("pos_abb").is_in(SKILL_POS))
            daily.append(d.select([
                pl.col("dt").str.to_datetime("%Y-%m-%dT%H:%M:%SZ").alias("dt"),
                pl.col("gsis_id").alias("player_id"),
                pl.col("pos_rank").cast(pl.Int32).alias("depth_rank"),
            ]).group_by(["dt", "player_id"]).agg(pl.col("depth_rank").min()))
    w = pl.concat(weekly, how="diagonal_relaxed") if weekly else \
        pl.DataFrame(schema={"season": pl.Int32, "week": pl.Int32, "player_id": pl.Utf8, "depth_rank": pl.Int32})
    dd = pl.concat(daily, how="diagonal_relaxed") if daily else \
        pl.DataFrame(schema={"dt": pl.Datetime, "player_id": pl.Utf8, "depth_rank": pl.Int32})
    return w, dd


def load_roster_status(root: str, seasons) -> pl.DataFrame:
    frames = []
    for s in seasons:
        p = os.path.join(root, "data/raw/nflverse/weekly_rosters", f"roster_weekly_{s}.parquet")
        if not os.path.exists(p):
            continue
        d = pl.read_parquet(p, columns=["season", "week", "game_type", "gsis_id", "status", "team"])
        frames.append(d.filter((pl.col("game_type") == "REG") & pl.col("gsis_id").is_not_null())
                      .select([pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32),
                               pl.col("gsis_id").alias("player_id"),
                               pl.col("status").alias("roster_status")]))
    if not frames:
        return pl.DataFrame(schema={"season": pl.Int32, "week": pl.Int32, "player_id": pl.Utf8,
                                    "roster_status": pl.Utf8})
    return pl.concat(frames, how="diagonal_relaxed").unique(subset=["season", "week", "player_id"], keep="last")


def load_injuries(root: str, seasons) -> pl.DataFrame:
    frames = []
    for s in seasons:
        p = os.path.join(root, "data/raw/nflverse/injuries", f"injuries_{s}.parquet")
        if not os.path.exists(p):
            continue
        d = pl.read_parquet(p, columns=["season", "week", "game_type", "gsis_id", "report_status",
                                        "practice_status", "date_modified"])
        frames.append(d.filter((pl.col("game_type") == "REG") & pl.col("gsis_id").is_not_null())
                      .select([pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32),
                               pl.col("gsis_id").alias("player_id"), "report_status", "practice_status",
                               pl.col("date_modified").cast(pl.Datetime("us"))
                               .dt.replace_time_zone(None).alias("inj_ts")]))
    if not frames:
        return pl.DataFrame(schema={"season": pl.Int32, "week": pl.Int32, "player_id": pl.Utf8,
                                    "report_status": pl.Utf8, "practice_status": pl.Utf8,
                                    "inj_ts": pl.Datetime("us")})
    return pl.concat(frames, how="diagonal_relaxed")


# ------------------------------------------------------------------ EWMA recursion
def ewma_prior(values: np.ndarray, gid: np.ndarray, season: np.ndarray, key: np.ndarray,
               priors: dict | None, halflife: float, season_carry: float, shrink_k: float):
    """Point-in-time EWMA over each group's PRIOR rows (rows must be sorted by group then time).

    Returns (pre, post, n_prior, w_eff): ``pre[i]`` is recorded before row i's own value is
    folded in (this is the feature), ``post[i]`` after (used for teammate context, where the
    consumer is a strictly later game).  NaN inputs never update the recursion.
    """
    n, m = values.shape
    d = 0.5 ** (1.0 / halflife)
    pre = np.full((n, m), np.nan)
    post = np.full((n, m), np.nan)
    n_prior = np.zeros(n, dtype=int)
    w_eff = np.zeros(n)
    zero = np.zeros(m)
    S = np.zeros(m); W = np.zeros(m); Wc = 0.0
    cur = None; last_season = None; cnt = 0
    for i in range(n):
        g = gid[i]
        if g != cur:
            cur = g; S = np.zeros(m); W = np.zeros(m); Wc = 0.0; cnt = 0; last_season = season[i]
        elif season[i] != last_season:
            c = season_carry ** float(season[i] - last_season)
            S = S * c; W = W * c; Wc = Wc * c; last_season = season[i]
        pr = priors.get(key[i], zero) if priors is not None else zero
        pre[i] = (S + shrink_k * pr) / (W + shrink_k)
        n_prior[i] = cnt
        w_eff[i] = Wc
        v = values[i]; msk = np.isfinite(v)
        S = S * d; W = W * d; Wc = Wc * d
        S[msk] += v[msk]; W[msk] += 1.0
        if msk.any():
            Wc += 1.0
            cnt += 1
        post[i] = (S + shrink_k * pr) / (W + shrink_k)
    return pre, post, n_prior, w_eff


def raw_ewma_prior(values: np.ndarray, gid: np.ndarray, season: np.ndarray,
                   halflife: float, season_carry: float):
    """Unshrunk EWMA of prior rows (the (a) baseline).  NaN until the group has one row."""
    pre, _, _, _ = ewma_prior(values, gid, season, gid, None, halflife, season_carry, 0.0)
    return pre


# ------------------------------------------------------------------ teammate reallocation
def teammate_snapshots(df: pd.DataFrame, post_cols: list[str], lookback_games: int = 8) -> pd.DataFrame:
    """For every (season, week, team), the last-known post-game shares of every player who
    played for that team in a game STRICTLY EARLIER than that week (within ``lookback_games``
    team games, carried across the season boundary).  Pure pre-kickoff information."""
    rows = []
    cols = ["season", "week", "team", "player_id", "position"] + post_cols
    for team, g in df.sort_values(["season", "week"]).groupby("team", sort=False):
        state: dict[str, tuple] = {}     # player_id -> (team_game_idx, position, values)
        tg_idx = 0
        for (season, week), wk in g.groupby(["season", "week"], sort=True):
            for pid, (idx, pos, vals) in state.items():
                if tg_idx - idx <= lookback_games:
                    rows.append((season, week, team, pid, pos) + tuple(vals))
            for r in wk.itertuples(index=False):
                d = r._asdict()
                state[d["player_id"]] = (tg_idx, d["position"], [d[c] for c in post_cols])
            tg_idx += 1
    return pd.DataFrame(rows, columns=cols)


def add_teammate_context(df: pd.DataFrame, snaps: pd.DataFrame, post_cols: list[str]) -> pd.DataFrame:
    """Sum of prior shares of same-position (and same pass-catcher group) teammates who are
    NOT available this week.  Availability is pregame: roster status ACT and injury report
    status not 'Out'."""
    s = snaps.copy()
    s["unavailable"] = ~s["available"].astype(bool)
    out = s[s.unavailable]
    agg_pos = out.groupby(["season", "week", "team", "position"], as_index=False)[post_cols].sum()
    agg_pos = agg_pos.rename(columns={c: f"out_pos_{c}" for c in post_cols})
    rec = out[out.position.isin(["RB", "WR", "TE"])]
    agg_grp = rec.groupby(["season", "week", "team"], as_index=False)[post_cols].sum()
    agg_grp = agg_grp.rename(columns={c: f"out_grp_{c}" for c in post_cols})
    n_out = out.groupby(["season", "week", "team", "position"], as_index=False).size() \
               .rename(columns={"size": "n_out_pos"})
    df = df.merge(agg_pos, on=["season", "week", "team", "position"], how="left")
    df = df.merge(agg_grp, on=["season", "week", "team"], how="left")
    df = df.merge(n_out, on=["season", "week", "team", "position"], how="left")
    for c in post_cols:
        df[f"out_pos_{c}"] = df[f"out_pos_{c}"].fillna(0.0)
        df[f"out_grp_{c}"] = df[f"out_grp_{c}"].fillna(0.0)
    df["n_out_pos"] = df["n_out_pos"].fillna(0.0)
    # never let a player's own (stale) share count as "vacated by someone else"
    own_unavail = ~df["available"].astype(bool)
    for c in post_cols:
        own = np.where(own_unavail, df[c].fillna(0.0), 0.0)
        df[f"out_pos_{c}"] = np.maximum(df[f"out_pos_{c}"] - own, 0.0)
        df[f"out_grp_{c}"] = np.maximum(df[f"out_grp_{c}"] - own, 0.0)
    return df


# ------------------------------------------------------------------ feature builder
@dataclass
class FeatureConfig:
    halflives: tuple = HALFLIVES
    season_carry: float = 0.5
    shrink_k: float = 3.0
    prior_seasons: tuple = (2012, 2013, 2014, 2015)   # position priors: fixed, pre-test-window
    lookback_games: int = 8


def build_features(root: str, seasons=range(2013, 2026), history_start: int = 2012,
                   cutoff: "pd.Timestamp | None" = None, cfg: FeatureConfig | None = None) -> pd.DataFrame:
    """Point-in-time opportunity features for every skill-position player-game in ``seasons``.

    ``cutoff``: blank the outcomes of every game with kickoff >= cutoff so that they
    contribute to no aggregate.  Feature rows for such games are still produced (they are
    the "pregame" rows), which is what makes the leakage test possible.
    """
    cfg = cfg or FeatureConfig()
    seasons = list(seasons)
    all_seasons = list(range(min(history_start, min(seasons)), max(seasons) + 1))

    sched = load_schedule(root)
    base = load_player_games(root, all_seasons)                     # stats + market context
    base = base[base.position.isin(SKILL_POS)].copy()
    base["team"] = base["team"].replace(TEAM_FIX)
    base = base.merge(sched.select(["game_id", "kickoff"]).to_pandas(), on="game_id", how="inner")

    pbp_p, pbp_t = pbp_aggregates(root, all_seasons)
    pbp_p = pbp_p.rename({"targets": "pbp_targets", "carries": "pbp_carries",
                          "pass_attempts": "pbp_pass_attempts", "posteam": "team"})
    routes = routes_from_participation(root, all_seasons)
    snapp = load_snap_pct(root, all_seasons)

    b = pl.from_pandas(base)
    b = b.join(pbp_p.drop("team"), on=["game_id", "player_id"], how="left")
    b = b.join(routes, on=["game_id", "player_id"], how="left")
    b = b.join(snapp, on=["game_id", "player_id"], how="left")
    b = b.join(pbp_t.rename({"posteam": "team"}), on=["game_id", "team"], how="left")
    df = b.to_pandas()

    # ---- outcomes actually modelled (box score where it exists, pbp for the rest)
    for c in ["targets", "carries", "attempts"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    for c in ["sacks_taken", "scrambles", "air_yards", "rz_targets", "rz_carries", "i10_opp",
              "i5_opp", "routes", "offense_snaps_pbp"]:
        if c not in df:
            df[c] = np.nan
    df["dropbacks"] = df["attempts"] + df["sacks_taken"].fillna(0.0) + df["scrambles"].fillna(0.0)

    # ---- truncation: games at/after the cutoff contribute nothing
    df["future"] = False
    if cutoff is not None:
        df["future"] = df["kickoff"] >= pd.Timestamp(cutoff)
        outcome_cols = [c for c in PLAYER_COUNTS + TEAM_COLS + ["snap_share"] if c in df]
        df.loc[df.future, outcome_cols] = np.nan

    # ---- shares of team opportunity in that game
    def _share(num, den):
        d = df[den].astype(float)
        return np.where(d > 0, df[num].astype(float) / d.replace(0, np.nan), np.nan)

    df["target_share"] = _share("targets", "team_targets")
    df["carry_share"] = _share("carries", "team_carries")
    df["dropback_share"] = _share("dropbacks", "team_dropbacks")
    df["air_yards_share"] = _share("air_yards", "team_air_yards")
    df["routes_share"] = _share("routes", "team_dropbacks")
    df["rz_target_share"] = _share("rz_targets", "team_rz_targets")
    df["rz_carry_share"] = _share("rz_carries", "team_rz_carries")
    df["i10_share"] = _share("i10_opp", "team_i10_opp")
    df["i5_share"] = _share("i5_opp", "team_i5_opp")

    df = df.sort_values(["player_id", "season", "week"]).reset_index(drop=True)

    # ---- position priors (fixed, estimated on pre-window seasons only)
    pri_src = df[df.season.isin(list(cfg.prior_seasons)) & (~df.future)]
    priors = {pos: np.nan_to_num(g[EWMA_COLS].astype(float).mean().to_numpy(), nan=0.0)
              for pos, g in pri_src.groupby("position")}

    V = df[EWMA_COLS].to_numpy(dtype=float)
    pid = df.player_id.to_numpy(); ssn = df.season.to_numpy(); pos = df.position.to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        for hl in cfg.halflives:
            pre, post, n_prior, w_eff = ewma_prior(V, pid, ssn, pos, priors, hl,
                                                   cfg.season_carry, cfg.shrink_k)
            tag = f"hl{int(hl)}"
            for j, c in enumerate(EWMA_COLS):
                df[f"ew_{c}_{tag}"] = pre[:, j]
            if hl == max(cfg.halflives):
                df["n_prior"] = n_prior
                df["w_eff"] = w_eff
                df["shrink_w"] = cfg.shrink_k / (w_eff + cfg.shrink_k)
                for j, c in enumerate(EWMA_COLS):
                    if c in POST_COLS:
                        df[f"post_{c}"] = post[:, j]
            raw = raw_ewma_prior(V, pid, ssn, hl, cfg.season_carry)
            for j, c in enumerate(EWMA_COLS):
                df[f"raw_{c}_{tag}"] = raw[:, j]

    # ---- team-level EWMAs (team's prior games only)
    tg = df[["game_id", "team", "season", "week", "kickoff", "future"] + TEAM_COLS] \
        .drop_duplicates(subset=["game_id", "team"]).sort_values(["team", "season", "week"]).reset_index(drop=True)
    TV = tg[TEAM_COLS].to_numpy(dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        for hl in cfg.halflives:
            pre, _, npt, wt = ewma_prior(TV, tg.team.to_numpy(), tg.season.to_numpy(),
                                         tg.team.to_numpy(), None, hl, cfg.season_carry, 0.0)
            for j, c in enumerate(TEAM_COLS):
                tg[f"tm_{c}_hl{int(hl)}"] = pre[:, j]
            if hl == max(cfg.halflives):
                tg["tm_n_prior"] = npt
    tcols = ["game_id", "team", "tm_n_prior"] + [c for c in tg.columns if c.startswith("tm_") and c != "tm_n_prior"]
    df = df.merge(tg[tcols], on=["game_id", "team"], how="left")

    # ---- depth chart, roster status, injury report (all strictly pre-kickoff)
    wdc, ddc = load_depth_charts(root, all_seasons)
    df = df.merge(wdc.to_pandas(), on=["season", "week", "player_id"], how="left")
    if ddc.height:
        keys = pl.from_pandas(df[["player_id", "game_id", "kickoff"]]).sort("kickoff")
        d2 = ddc.sort("dt")
        if cutoff is not None:
            d2 = d2.filter(pl.col("dt") < pl.lit(pd.Timestamp(cutoff)))
        asof = keys.join_asof(d2.rename({"depth_rank": "depth_rank_daily"}),
                              left_on="kickoff", right_on="dt", by="player_id", strategy="backward")
        df = df.merge(asof.select(["player_id", "game_id", "depth_rank_daily"]).to_pandas(),
                      on=["player_id", "game_id"], how="left")
        df["depth_rank"] = df["depth_rank"].fillna(df["depth_rank_daily"])
        df = df.drop(columns=["depth_rank_daily"])
    df["depth_rank"] = pd.to_numeric(df["depth_rank"], errors="coerce").clip(1, 5)

    ros = load_roster_status(root, all_seasons).to_pandas()
    df = df.merge(ros, on=["season", "week", "player_id"], how="left")
    inj = load_injuries(root, all_seasons)
    if cutoff is not None:
        inj = inj.filter(pl.col("inj_ts").is_null() | (pl.col("inj_ts") < pl.lit(pd.Timestamp(cutoff))))
    inj = (inj.sort("inj_ts").unique(subset=["season", "week", "player_id"], keep="last")
           .select(["season", "week", "player_id", "report_status", "practice_status"]))
    df = df.merge(inj.to_pandas(), on=["season", "week", "player_id"], how="left")

    df["available"] = (df["roster_status"].fillna("") == "ACT") & (df["report_status"].fillna("") != "Out")
    df["inj_questionable"] = (df["report_status"].fillna("") == "Questionable").astype(float)
    df["inj_out"] = (df["report_status"].fillna("") == "Out").astype(float)
    df["dnp"] = df["practice_status"].fillna("").str.contains("Did Not Participate").astype(float)

    # ---- teammate reallocation
    snap_src = df[["season", "week", "team", "player_id", "position"] +
                  [f"post_{c}" for c in POST_COLS]].copy()
    snap_src = snap_src[~df["future"].to_numpy()] if cutoff is not None else snap_src
    snaps = teammate_snapshots(snap_src, [f"post_{c}" for c in POST_COLS], cfg.lookback_games)
    avail = df[["season", "week", "player_id", "available"]].drop_duplicates(
        subset=["season", "week", "player_id"])
    snaps = snaps.merge(avail, on=["season", "week", "player_id"], how="left")
    miss = snaps["available"].isna()
    if miss.any():
        ros_i = ros.set_index(["season", "week", "player_id"])["roster_status"]
        idx = pd.MultiIndex.from_frame(snaps.loc[miss, ["season", "week", "player_id"]])
        snaps.loc[miss, "available"] = (ros_i.reindex(idx).fillna("").to_numpy() == "ACT")
    df = add_teammate_context(df, snaps, [f"post_{c}" for c in POST_COLS])

    # ---- game environment
    df["implied_total"] = df["implied_total"].astype(float)
    df["home"] = df["home"].astype(float)
    df["indoor"] = df["indoor"].astype(float)
    df["spread_team"] = df["spread_team"].astype(float)
    df["total_line"] = df["total_line"].astype(float)
    df["depth1"] = (df["depth_rank"] == 1).astype(float)
    df["depth2"] = (df["depth_rank"] == 2).astype(float)
    df["depth_rank_f"] = df["depth_rank"].fillna(4.0)
    df["roster_act"] = (df["roster_status"].fillna("") == "ACT").astype(float)
    df["is_qb"] = (df.position == "QB").astype(float)
    df["is_rb"] = (df.position == "RB").astype(float)
    df["is_wr"] = (df.position == "WR").astype(float)
    df["is_te"] = (df.position == "TE").astype(float)

    df = df[df.season.isin(seasons)].reset_index(drop=True)
    return df
