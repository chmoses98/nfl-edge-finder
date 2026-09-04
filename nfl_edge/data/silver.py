"""Silver layer: canonical football entities built from bronze nflverse files.

Nothing here is point-in-time *feature* engineering; this layer only cleans and
aggregates per game so that gold/feature code can apply strict "prior games
only" joins on top of it.

Tables
------
games(season, week, game_id, game_type, gameday, kickoff_utc?, home_team, away_team,
      home_score, away_score, result(home-away), total, spread_line(home favored +),
      total_line, moneylines, roof, surface, temp, wind, div_game, rest, qbs, coaches,
      stadium_id, referee)
team_game(season, week, game_id, team, opp, is_home, offensive + defensive per-play
      aggregates from play-by-play)
"""
from __future__ import annotations
import os
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(ROOT, "data", "raw", "nflverse")
SILVER = os.path.join(ROOT, "data", "silver")

TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA", "ARZ": "ARI", "AZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "JAC": "JAX", "SL": "LA", "LAR": "LA", "WSH": "WAS"}


def norm_team(col: str) -> pl.Expr:
    return pl.col(col).replace(TEAM_FIX)


def load_games() -> pl.DataFrame:
    g = pl.read_csv(os.path.join(RAW, "schedules", "games.csv"), infer_schema_length=20000)
    g = g.with_columns(norm_team("home_team").alias("home_team"), norm_team("away_team").alias("away_team"))
    return g


def team_game_from_pbp(season: int) -> pl.DataFrame:
    p = os.path.join(RAW, "pbp", f"play_by_play_{season}.parquet")
    cols = ["season", "week", "game_id", "season_type", "posteam", "defteam", "home_team", "away_team", "play_type", "epa", "success",
            "qb_dropback", "pass", "rush", "down", "ydstogo", "yardline_100", "score_differential", "game_seconds_remaining",
            "wp", "vegas_wp", "xpass", "pass_oe", "cpoe", "air_yards", "yards_gained", "qb_hit", "sack", "interception", "fumble_lost",
            "penalty", "special", "field_goal_attempt", "punt_attempt", "kickoff_attempt", "fixed_drive", "fixed_drive_result",
            "series_success", "qb_scramble", "no_huddle", "shotgun", "aborted_play", "touchdown", "qb_epa", "complete_pass",
            "incomplete_pass", "play_clock", "drive_play_count", "penalty_team", "penalty_yards", "goal_to_go", "field_goal_result", "kick_distance"]
    lf = pl.scan_parquet(p)
    have = [c for c in cols if c in lf.collect_schema().names()]
    df = lf.select(have).collect()
    df = df.with_columns(norm_team("posteam").alias("posteam"), norm_team("defteam").alias("defteam"),
                         norm_team("home_team").alias("home_team"), norm_team("away_team").alias("away_team"))
    # scrimmage plays only (pass/run incl. scrambles; drop kneels, spikes, no_play, ST)
    scrim = df.filter(pl.col("play_type").is_in(["pass", "run"]) & pl.col("epa").is_not_null() & pl.col("posteam").is_not_null())
    scrim = scrim.with_columns([
        (pl.col("wp").is_between(0.05, 0.95) if "wp" in scrim.columns else pl.lit(True)).alias("non_garbage"),
        (pl.col("down") <= 2).alias("early_down"),
        ((pl.col("pass") == 1) & (pl.col("yards_gained") >= 20)).alias("explosive_pass"),
        ((pl.col("rush") == 1) & (pl.col("yards_gained") >= 12)).alias("explosive_run"),
        (pl.col("yardline_100") <= 20).alias("red_zone"),
        (pl.col("score_differential").abs() <= 7).alias("neutral_score"),
        ((pl.col("interception") == 1) | (pl.col("fumble_lost") == 1)).alias("turnover"),
    ])
    def agg(side: str):
        team = "posteam" if side == "off" else "defteam"
        opp = "defteam" if side == "off" else "posteam"
        g = scrim.group_by(["season", "week", "game_id", team]).agg([
            pl.len().alias("plays"),
            pl.col("epa").mean().alias("epa_play"),
            pl.col("epa").sum().alias("epa_total"),
            pl.col("success").mean().alias("success_rate"),
            pl.col("epa").filter(pl.col("qb_dropback") == 1).mean().alias("dropback_epa"),
            pl.col("epa").filter(pl.col("qb_dropback") == 1).count().alias("dropbacks"),
            pl.col("success").filter(pl.col("qb_dropback") == 1).mean().alias("dropback_sr"),
            pl.col("epa").filter((pl.col("rush") == 1) & (pl.col("qb_scramble") != 1)).mean().alias("rush_epa"),
            pl.col("epa").filter((pl.col("rush") == 1) & (pl.col("qb_scramble") != 1)).count().alias("rushes"),
            pl.col("success").filter((pl.col("rush") == 1) & (pl.col("qb_scramble") != 1)).mean().alias("rush_sr"),
            pl.col("epa").filter(pl.col("early_down")).mean().alias("early_down_epa"),
            pl.col("epa").filter(pl.col("non_garbage")).mean().alias("epa_play_ng"),
            pl.col("success").filter(pl.col("non_garbage")).mean().alias("success_rate_ng"),
            pl.col("epa").filter(pl.col("non_garbage") & (pl.col("qb_dropback") == 1)).mean().alias("dropback_epa_ng"),
            pl.col("epa").filter(pl.col("non_garbage") & (pl.col("rush") == 1)).mean().alias("rush_epa_ng"),
            pl.col("explosive_pass").sum().alias("explosive_passes"),
            pl.col("explosive_run").sum().alias("explosive_runs"),
            pl.col("sack").sum().alias("sacks"),
            pl.col("qb_hit").sum().alias("qb_hits"),
            pl.col("interception").sum().alias("ints"),
            pl.col("fumble_lost").sum().alias("fumbles_lost"),
            pl.col("turnover").sum().alias("turnovers"),
            pl.col("pass_oe").filter(pl.col("non_garbage") & pl.col("early_down")).mean().alias("proe_early_ng"),
            pl.col("pass_oe").mean().alias("proe"),
            pl.col("cpoe").mean().alias("cpoe"),
            pl.col("air_yards").filter(pl.col("pass") == 1).mean().alias("adot"),
            pl.col("epa").filter(pl.col("red_zone")).mean().alias("rz_epa"),
            pl.col("epa").filter(pl.col("red_zone")).count().alias("rz_plays"),
            pl.col("touchdown").sum().alias("tds"),
            pl.col("yards_gained").sum().alias("yards"),
            pl.col("no_huddle").mean().alias("no_huddle_rate"),
            pl.col("shotgun").mean().alias("shotgun_rate"),
            pl.col("epa").filter(pl.col("neutral_score")).count().alias("neutral_plays"),
        ]).rename({team: "team"})
        return g.rename({c: f"{side}_{c}" for c in g.columns if c not in ("season", "week", "game_id", "team")})
    off = agg("off"); de = agg("def")
    # special teams EPA (kickoffs, punts, FGs) attributed to posteam
    st = df.filter(pl.col("special") == 1 if "special" in df.columns else pl.col("play_type").is_in(["kickoff", "punt", "field_goal", "extra_point"]))
    st = st.filter(pl.col("epa").is_not_null() & pl.col("posteam").is_not_null())
    st_off = st.group_by(["game_id", "posteam"]).agg(pl.col("epa").sum().alias("st_epa_for"), pl.col("field_goal_attempt").sum().alias("fga"),
                                                       (pl.col("field_goal_result") == "made").sum().alias("fgm")).rename({"posteam": "team"})
    st_def = st.group_by(["game_id", "defteam"]).agg(pl.col("epa").sum().alias("st_epa_against")).rename({"defteam": "team"})
    # pace: seconds per scrimmage play in neutral situations -> use plays count and drives
    drives = df.filter(pl.col("fixed_drive").is_not_null() & pl.col("posteam").is_not_null()).group_by(["game_id", "posteam"]).agg(
        pl.col("fixed_drive").n_unique().alias("drives"),
        (pl.col("fixed_drive_result") == "Touchdown").sum().alias("drive_td_plays")).rename({"posteam": "team"})
    dr = df.filter(pl.col("fixed_drive").is_not_null() & pl.col("posteam").is_not_null()).group_by(["game_id", "posteam", "fixed_drive"]).agg(
        pl.col("fixed_drive_result").first().alias("res")).group_by(["game_id", "posteam"]).agg(
        (pl.col("res") == "Touchdown").sum().alias("td_drives"), (pl.col("res") == "Field goal").sum().alias("fg_drives"),
        pl.col("res").is_in(["Turnover", "Turnover on downs", "Opp touchdown"]).sum().alias("to_drives"), pl.len().alias("n_drives")).rename({"posteam": "team"})
    out = off.join(de, on=["season", "week", "game_id", "team"], how="full", coalesce=True)
    out = out.join(st_off, on=["game_id", "team"], how="left").join(st_def, on=["game_id", "team"], how="left").join(dr, on=["game_id", "team"], how="left")
    meta = df.select("game_id", "home_team", "away_team", "season_type").unique(subset=["game_id"])
    out = out.join(meta, on="game_id", how="left").with_columns(
        (pl.col("team") == pl.col("home_team")).alias("is_home"),
        pl.when(pl.col("team") == pl.col("home_team")).then(pl.col("away_team")).otherwise(pl.col("home_team")).alias("opp"))
    return out


def build(seasons=range(2006, 2026), force=False):
    os.makedirs(SILVER, exist_ok=True)
    frames = []
    for s in seasons:
        p = os.path.join(SILVER, f"team_game_{s}.parquet")
        if os.path.exists(p) and not force:
            frames.append(pl.read_parquet(p)); continue
        tg = team_game_from_pbp(s)
        tg.write_parquet(p)
        frames.append(tg)
        print("built", s, tg.shape, flush=True)
    allf = pl.concat(frames, how="diagonal_relaxed")
    allf.write_parquet(os.path.join(SILVER, "team_game.parquet"))
    g = load_games()
    g.write_parquet(os.path.join(SILVER, "games.parquet"))
    return allf, g


if __name__ == "__main__":
    import sys
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 2006
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    build(range(lo, hi + 1), force="--force" in sys.argv)
