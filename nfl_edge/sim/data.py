"""Bronze nflverse -> tidy tables for the simulation layer.

Every table is a pure function of the bronze files under ``data/raw/nflverse`` and is cached under
``data/cache/sim/`` keyed by season, so a rebuild is cheap and nothing here is a vintage of anything
mutable (injuries and depth charts are read by the feature layer with an explicit cutoff, never here).

Counting conventions follow the OFFICIAL box score so that what the simulator produces is what Kalshi
settles on: carries include scrambles and kneels, pass attempts include spikes and exclude sacks,
targets are pass attempts with a named receiver.  These were checked against ``stats_player_week``
(nflverse's official-stat mirror) game by game.
"""
from __future__ import annotations

import os
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(ROOT, "data", "raw", "nflverse")
CACHE = os.path.join(ROOT, "data", "cache", "sim")

TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA", "LAR": "LA", "JAC": "JAX", "WSH": "WAS", "ARZ": "ARI",
            "BLT": "BAL", "CLV": "CLE", "HST": "HOU"}

PBP_COLS = ["game_id", "season", "week", "season_type", "home_team", "away_team", "posteam", "defteam",
            "play_type", "rush_attempt", "pass_attempt", "qb_dropback", "qb_scramble", "qb_kneel", "qb_spike",
            "sack", "complete_pass", "interception", "yards_gained", "rushing_yards", "receiving_yards",
            "passing_yards", "air_yards", "touchdown", "rush_touchdown", "pass_touchdown", "rusher_player_id",
            "receiver_player_id", "passer_player_id", "yardline_100", "down", "ydstogo", "qtr",
            "game_seconds_remaining", "half_seconds_remaining", "score_differential", "wp", "vegas_wp", "xpass",
            "fixed_drive", "fixed_drive_result", "play_id", "two_point_attempt", "field_goal_attempt",
            "field_goal_result", "extra_point_attempt", "extra_point_result", "two_point_conv_result",
            "total_home_score", "total_away_score", "home_score", "away_score", "posteam_type", "fumble_lost",
            "goal_to_go", "penalty", "aborted_play", "epa", "success", "drive_play_count"]


def _norm(col):
    return pl.col(col).replace(TEAM_FIX)


def _read_pbp(season: int) -> pl.DataFrame:
    path = os.path.join(RAW, "pbp", f"play_by_play_{season}.parquet")
    names = pl.scan_parquet(path).collect_schema().names()
    cols = [c for c in PBP_COLS if c in names]
    d = pl.read_parquet(path, columns=cols)
    for c in ("posteam", "defteam", "home_team", "away_team"):
        if c in d.columns:
            d = d.with_columns(_norm(c).alias(c))
    for c in ("rush_attempt", "pass_attempt", "qb_dropback", "qb_scramble", "qb_kneel", "qb_spike", "sack",
              "complete_pass", "interception", "touchdown", "rush_touchdown", "pass_touchdown",
              "two_point_attempt", "field_goal_attempt", "fumble_lost", "penalty", "aborted_play", "success"):
        if c in d.columns:
            d = d.with_columns(pl.col(c).fill_null(0).cast(pl.Int32))
    return d


# ------------------------------------------------------------------------------------------ team-game
# A "play" for volume purposes is any official scrimmage play: runs, passes, sacks, scrambles, kneels,
# spikes.  Penalty no-plays are excluded because they produce no official attempt.
_IS_PLAY = pl.col("play_type").is_in(["run", "pass", "qb_kneel", "qb_spike"])


def team_games(season: int) -> pl.DataFrame:
    """One row per team per game with the volume, split, script and production quantities the game
    environment engine is trained on."""
    d = _read_pbp(season)
    d = d.filter(pl.col("posteam").is_not_null() & pl.col("season_type").is_in(["REG", "POST"]))
    p = d.filter(_IS_PLAY)
    is_pass_play = (pl.col("pass_attempt") == 1) | (pl.col("sack") == 1) | (pl.col("qb_scramble") == 1)
    lead = pl.col("score_differential")
    tg = p.group_by(["game_id", "posteam"]).agg([
        pl.first("season").alias("season"), pl.first("week").alias("week"), pl.first("season_type").alias("season_type"),
        pl.first("home_team").alias("home_team"), pl.first("away_team").alias("away_team"),
        pl.len().alias("plays"),
        is_pass_play.sum().alias("dropbacks"),
        ((pl.col("pass_attempt") == 1) & (pl.col("sack") == 0)).sum().alias("pass_att"),
        (pl.col("sack") == 1).sum().alias("sacks"),
        (pl.col("qb_scramble") == 1).sum().alias("scrambles"),
        (pl.col("rush_attempt") == 1).sum().alias("rush_att"),
        ((pl.col("rush_attempt") == 1) & (pl.col("qb_scramble") == 0) & (pl.col("qb_kneel") == 0)).sum().alias("designed_rush"),
        (pl.col("qb_kneel") == 1).sum().alias("kneels"),
        ((pl.col("pass_attempt") == 1) & (pl.col("sack") == 0) & pl.col("receiver_player_id").is_not_null()).sum().alias("targets"),
        (pl.col("complete_pass") == 1).sum().alias("completions"),
        pl.when(pl.col("complete_pass") == 1).then(pl.col("yards_gained")).otherwise(0).sum().alias("pass_yards"),
        pl.when(pl.col("rush_attempt") == 1).then(pl.col("yards_gained")).otherwise(0).sum().alias("rush_yards"),
        (pl.col("pass_touchdown") == 1).sum().alias("pass_td"),
        (pl.col("rush_touchdown") == 1).sum().alias("rush_td"),
        (pl.col("interception") == 1).sum().alias("ints"),
        ((pl.col("rush_attempt") == 1) & (pl.col("yardline_100") <= 20)).sum().alias("rz_rush"),
        ((pl.col("rush_attempt") == 1) & (pl.col("yardline_100") <= 5)).sum().alias("i5_rush"),
        ((pl.col("pass_attempt") == 1) & (pl.col("yardline_100") <= 20)).sum().alias("rz_pass"),
        pl.col("xpass").mean().alias("xpass_mean"),
        (is_pass_play.cast(pl.Float64) - pl.col("xpass")).mean().alias("proe"),
        # game script: share of plays run while leading / trailing by 4+ / 8+ points
        (lead >= 4).mean().alias("frac_lead4"), (lead <= -4).mean().alias("frac_trail4"),
        (lead >= 8).mean().alias("frac_lead8"), (lead <= -8).mean().alias("frac_trail8"),
        lead.mean().alias("mean_lead"),
        pl.col("fixed_drive").n_unique().alias("drives"),
        (pl.col("epa").mean()).alias("epa_play"),
        (pl.col("success").mean()).alias("success_rate"),
    ])
    # neutral-script pass rate, pace
    neu = (p.filter((pl.col("qtr") <= 3) & (pl.col("wp").is_between(0.2, 0.8)) & (lead.abs() <= 8))
           .group_by(["game_id", "posteam"]).agg([is_pass_play.mean().alias("neutral_pass_rate"),
                                                  pl.len().alias("neutral_plays"),
                                                  (is_pass_play.cast(pl.Float64) - pl.col("xpass")).mean().alias("neutral_proe")]))
    pace = (p.sort(["game_id", "play_id"])
            .with_columns((pl.col("game_seconds_remaining").shift(1).over(["game_id", "fixed_drive"])
                           - pl.col("game_seconds_remaining")).alias("_dt"))
            .filter((pl.col("_dt") > 0) & (pl.col("_dt") <= 60) & (pl.col("qtr") <= 3) & (lead.abs() <= 8))
            .group_by(["game_id", "posteam"]).agg(pl.col("_dt").mean().alias("sec_per_play")))
    rzt = (d.filter((pl.col("yardline_100") <= 20) & _IS_PLAY).group_by(["game_id", "posteam"])
           .agg(pl.col("fixed_drive").n_unique().alias("rz_trips")))
    fg = (d.filter(pl.col("field_goal_attempt") == 1).group_by(["game_id", "posteam"])
          .agg([pl.len().alias("fga"), (pl.col("field_goal_result") == "made").sum().alias("fgm")]))
    tg = (tg.join(neu, on=["game_id", "posteam"], how="left").join(pace, on=["game_id", "posteam"], how="left")
            .join(rzt, on=["game_id", "posteam"], how="left").join(fg, on=["game_id", "posteam"], how="left"))
    # final scores from the last play of the game
    fin = (d.sort(["game_id", "play_id"]).group_by("game_id").agg([
        pl.col("home_score").last().alias("home_score"), pl.col("away_score").last().alias("away_score")]))
    tg = tg.join(fin, on="game_id", how="left").with_columns([
        (pl.col("posteam") == pl.col("home_team")).alias("home"),
    ]).with_columns([
        pl.when(pl.col("home")).then(pl.col("home_score")).otherwise(pl.col("away_score")).alias("points"),
        pl.when(pl.col("home")).then(pl.col("away_score")).otherwise(pl.col("home_score")).alias("opp_points"),
        pl.when(pl.col("home")).then(pl.col("away_team")).otherwise(pl.col("home_team")).alias("opp"),
    ]).rename({"posteam": "team"})
    tg = tg.with_columns([
        (pl.col("points") - pl.col("opp_points")).alias("margin"),
        (pl.col("points") + pl.col("opp_points")).alias("total"),
        (pl.col("dropbacks") / pl.col("plays")).alias("pass_rate"),
        (pl.col("pass_td") + pl.col("rush_td")).alias("off_td"),
    ])
    return tg.sort(["season", "week", "game_id", "team"])


# ---------------------------------------------------------------------------------------- player-game
def _crosswalk() -> pl.DataFrame:
    p = os.path.join(ROOT, "data", "silver", "player_crosswalk.parquet")
    cw = pl.read_parquet(p).select(["gsis_id", "pfr_id"]).filter(pl.col("pfr_id").is_not_null()).unique("pfr_id")
    return cw


def _snaps(season: int) -> pl.DataFrame:
    path = os.path.join(RAW, "snap_counts", f"snap_counts_{season}.parquet")
    if not os.path.exists(path):
        return pl.DataFrame({"game_id": [], "gsis_id": [], "offense_snaps": [], "offense_pct": []})
    s = pl.read_parquet(path, columns=["game_id", "pfr_player_id", "player", "position", "team", "offense_snaps", "offense_pct"])
    s = s.join(_crosswalk(), left_on="pfr_player_id", right_on="pfr_id", how="left")
    s = s.filter(pl.col("gsis_id").is_not_null()).with_columns(_norm("team").alias("team"))
    return s.select(["game_id", "gsis_id", "team", "position", "offense_snaps", "offense_pct"]).unique(["game_id", "gsis_id"])


def _positions(season: int) -> pl.DataFrame:
    path = os.path.join(RAW, "rosters", f"roster_{season}.parquet")
    r = pl.read_parquet(path, columns=["gsis_id", "position", "full_name"]).filter(pl.col("gsis_id").is_not_null())
    return r.unique("gsis_id").rename({"position": "roster_position", "full_name": "player_name"})


def player_games(season: int) -> pl.DataFrame:
    """One row per (player, game) for every player who touched the ball or took an offensive snap, with the
    official-convention counts derived from play-by-play.  Explicit zero rows for snap-only players are the
    difference between 'played and got nothing' and 'did not play', which the opportunity model needs."""
    d = _read_pbp(season)
    d = d.filter(pl.col("posteam").is_not_null() & pl.col("season_type").is_in(["REG", "POST"]))
    p = d.filter(_IS_PLAY)
    key = ["game_id", "posteam"]
    rush = (p.filter((pl.col("rush_attempt") == 1) & pl.col("rusher_player_id").is_not_null())
            .group_by(key + ["rusher_player_id"]).agg([
                pl.len().alias("carries"), pl.col("yards_gained").sum().alias("rush_yards"),
                (pl.col("rush_touchdown") == 1).sum().alias("rush_td"),
                (pl.col("qb_scramble") == 1).sum().alias("scrambles"),
                ((pl.col("qb_scramble") == 0) & (pl.col("qb_kneel") == 0)).sum().alias("designed_carries"),
                (pl.col("yardline_100") <= 20).sum().alias("rz_carries"),
                (pl.col("yardline_100") <= 5).sum().alias("i5_carries"),
                (pl.col("yards_gained") >= 10).sum().alias("rush_10plus"),
            ]).rename({"rusher_player_id": "player_id"}))
    rec = (p.filter((pl.col("pass_attempt") == 1) & (pl.col("sack") == 0) & pl.col("receiver_player_id").is_not_null())
           .group_by(key + ["receiver_player_id"]).agg([
               pl.len().alias("targets"), (pl.col("complete_pass") == 1).sum().alias("receptions"),
               pl.when(pl.col("complete_pass") == 1).then(pl.col("yards_gained")).otherwise(0).sum().alias("rec_yards"),
               (pl.col("pass_touchdown") == 1).sum().alias("rec_td"),
               pl.col("air_yards").fill_null(0).sum().alias("air_yards"),
               (pl.col("yardline_100") <= 20).sum().alias("rz_targets"),
               ((pl.col("yardline_100") <= pl.col("air_yards")) & pl.col("air_yards").is_not_null()).sum().alias("ez_targets"),
           ]).rename({"receiver_player_id": "player_id"}))
    pas = (p.filter(pl.col("passer_player_id").is_not_null() & ((pl.col("pass_attempt") == 1) | (pl.col("sack") == 1)))
           .group_by(key + ["passer_player_id"]).agg([
               ((pl.col("pass_attempt") == 1) & (pl.col("sack") == 0)).sum().alias("attempts"),
               (pl.col("complete_pass") == 1).sum().alias("completions"),
               pl.when(pl.col("complete_pass") == 1).then(pl.col("yards_gained")).otherwise(0).sum().alias("pass_yards"),
               (pl.col("pass_touchdown") == 1).sum().alias("pass_td"),
               (pl.col("interception") == 1).sum().alias("ints"),
               (pl.col("sack") == 1).sum().alias("sacks_taken"),
           ]).rename({"passer_player_id": "player_id"}))
    pg = rush.join(rec, on=key + ["player_id"], how="full", coalesce=True)
    pg = pg.join(pas, on=key + ["player_id"], how="full", coalesce=True)
    counts = ["carries", "rush_yards", "rush_td", "scrambles", "designed_carries", "rz_carries", "i5_carries", "rush_10plus",
              "targets", "receptions", "rec_yards", "rec_td", "air_yards", "rz_targets", "ez_targets",
              "attempts", "completions", "pass_yards", "pass_td", "ints", "sacks_taken"]
    pg = pg.rename({"posteam": "team"})
    sn = _snaps(season)
    # zero rows: snap but no touch
    zero = sn.join(pg.select(["game_id", "player_id"]).with_columns(pl.lit(True).alias("_t")),
                   left_on=["game_id", "gsis_id"], right_on=["game_id", "player_id"], how="left").filter(pl.col("_t").is_null())
    zero = zero.filter(pl.col("offense_snaps") > 0).select([pl.col("game_id"), pl.col("team"), pl.col("gsis_id").alias("player_id")])
    pg = pl.concat([pg, zero], how="diagonal_relaxed")
    pg = pg.with_columns([pl.col(c).fill_null(0).cast(pl.Int32) for c in counts])
    pg = pg.join(sn.select(["game_id", "gsis_id", "offense_snaps", "offense_pct", "position"]),
                 left_on=["game_id", "player_id"], right_on=["game_id", "gsis_id"], how="left")
    pg = pg.join(_positions(season), left_on="player_id", right_on="gsis_id", how="left")
    pg = pg.with_columns(pl.coalesce([pl.col("position"), pl.col("roster_position")]).alias("position")).drop("roster_position")
    meta = d.group_by("game_id").agg([pl.first("season"), pl.first("week"), pl.first("season_type"),
                                      pl.first("home_team"), pl.first("away_team")])
    pg = pg.join(meta, on="game_id", how="left").with_columns([
        (pl.col("team") == pl.col("home_team")).alias("home"),
        pl.when(pl.col("team") == pl.col("home_team")).then(pl.col("away_team")).otherwise(pl.col("home_team")).alias("opp"),
        (pl.col("rush_td") + pl.col("rec_td")).alias("any_td"),
    ])
    return pg.sort(["season", "week", "game_id", "team", "player_id"])


# ------------------------------------------------------------------------------------------ per-play
def carries(season: int) -> pl.DataFrame:
    """One row per official rushing attempt (scrambles and kneels flagged) for the efficiency engine."""
    d = _read_pbp(season)
    c = d.filter(_IS_PLAY & (pl.col("rush_attempt") == 1) & pl.col("rusher_player_id").is_not_null()
                 & pl.col("season_type").is_in(["REG", "POST"]))
    return c.select([
        "game_id", "season", "week", "season_type", pl.col("posteam").alias("team"), pl.col("defteam").alias("opp"),
        pl.col("rusher_player_id").alias("player_id"), pl.col("yards_gained").alias("yards"),
        "yardline_100", "down", "ydstogo", "qtr", "score_differential", "qb_scramble", "qb_kneel",
        pl.col("rush_touchdown").alias("td"), "play_id", "wp"]).sort(["game_id", "play_id"])


def targets(season: int) -> pl.DataFrame:
    """One row per official target for the receiving efficiency engine."""
    d = _read_pbp(season)
    t = d.filter(_IS_PLAY & (pl.col("pass_attempt") == 1) & (pl.col("sack") == 0) & pl.col("receiver_player_id").is_not_null()
                 & pl.col("season_type").is_in(["REG", "POST"]))
    return t.select([
        "game_id", "season", "week", "season_type", pl.col("posteam").alias("team"), pl.col("defteam").alias("opp"),
        pl.col("receiver_player_id").alias("player_id"), pl.col("passer_player_id").alias("passer_id"),
        pl.col("complete_pass").alias("complete"),
        pl.when(pl.col("complete_pass") == 1).then(pl.col("yards_gained")).otherwise(0).alias("yards"),
        "air_yards", "yardline_100", "down", "ydstogo", "qtr", "score_differential",
        pl.col("pass_touchdown").alias("td"), pl.col("interception").alias("intercepted"), "play_id", "wp"]).sort(["game_id", "play_id"])


# --------------------------------------------------------------------------------------------- cache
_BUILDERS = {"team_games": team_games, "player_games": player_games, "carries": carries, "targets": targets}


def load(table: str, seasons, force: bool = False) -> pl.DataFrame:
    """Load a table for several seasons, building and caching per season."""
    os.makedirs(CACHE, exist_ok=True)
    frames = []
    for s in seasons:
        path = os.path.join(CACHE, f"{table}_{s}.parquet")
        src = os.path.join(RAW, "pbp", f"play_by_play_{s}.parquet")
        if not os.path.exists(src):
            continue
        if os.path.exists(path) and not force and os.path.getmtime(path) >= os.path.getmtime(src):
            frames.append(pl.read_parquet(path))
            continue
        f = _BUILDERS[table](s)
        f.write_parquet(path)
        frames.append(f)
    return pl.concat(frames, how="diagonal_relaxed") if frames else pl.DataFrame()


def schedule() -> pl.DataFrame:
    """The nflverse schedule with the consensus line columns.  Callers that project a game must mask the
    line columns for the target game themselves (see features.py) -- a closing line is not a point-in-time
    quantity for the game it closes."""
    g = pl.read_parquet(os.path.join(ROOT, "data", "silver", "games.parquet"))
    return g.with_columns([_norm("home_team").alias("home_team"), _norm("away_team").alias("away_team")])


if __name__ == "__main__":
    import sys
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 2016
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    for t in _BUILDERS:
        f = load(t, range(lo, hi + 1), force="--force" in sys.argv)
        print(t, f.shape, flush=True)
