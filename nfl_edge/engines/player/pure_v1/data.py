"""Football-data-only inputs for PURE_PLAYER_V1, behind explicit column allowlists.

Sources (nflverse bronze files, unchanged):
    stats_player/stats_player_week_<season>.parquet   box-score stats per player-game (REG only)
    snap_counts/snap_counts_<season>.parquet          offensive snaps per player-game (REG only)
    data/silver/player_crosswalk.parquet              pfr -> gsis ids (or players/players.parquet)
    schedules/games.csv                               ONLY the columns in SCHEDULE_ALLOWLIST

The schedule file also carries consensus spread / total / moneyline / odds columns. They are never selected: the
reader takes the intersection of the file's header with SCHEDULE_ALLOWLIST, so the pipeline runs identically when
those columns are present, absent or randomised (the runtime mutation test reruns it all three ways).

Population: every QB / RB / WR / TE player-game of a regular-season game with a box-score row or at least one
offensive snap. Nothing about which players a market lists enters here.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import polars as pl

SKILL = ("QB", "RB", "WR", "TE")
STAT_COLS = ["completions", "attempts", "passing_yards", "passing_tds", "passing_interceptions", "carries", "rushing_yards",
             "rushing_tds", "receptions", "targets", "receiving_yards", "receiving_tds"]
PLAYER_ALLOWLIST = ("player_id", "player_display_name", "position", "season", "week", "game_id", "team", "opponent_team",
                    *STAT_COLS, "offense_snaps")
SCHEDULE_ALLOWLIST = ("game_id", "season", "game_type", "week", "gameday", "gametime", "home_team", "away_team",
                      "home_score", "away_score", "roof", "home_qb_id", "away_qb_id")
# tokens that must never name a column the model consumes (checked by `attest_sports_only`)
MARKET_TOKENS = ("spread", "moneyline", "odds", "implied", "kalshi", "market", "vegas", "price", "line")
TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA", "ARZ": "ARI", "AZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU",
            "JAC": "JAX", "SL": "LA", "LAR": "LA", "WSH": "WAS"}
ET = ZoneInfo("America/New_York")
GAME_DURATION_HOURS = 4.0      # a game's box score is treated as observable only kickoff + 4 h (as DATA_ONLY does)


class MarketColumnError(ValueError):
    pass


def attest_sports_only(columns) -> None:
    """Refuse any consumed column whose name looks like a market quantity."""
    bad = [c for c in columns if any(t in str(c).lower() for t in MARKET_TOKENS) and c not in ("home_qb_id", "away_qb_id")]
    if bad:
        raise MarketColumnError(f"market-like columns reached PURE_PLAYER_V1: {bad}")


def _team(s: pd.Series) -> pd.Series:
    return s.astype("string").replace(TEAM_FIX)


def kickoff_utc(gameday, gametime) -> pd.Series:
    """nflverse gameday (local date) + gametime (US/Eastern clock) -> UTC timestamps."""
    out = []
    for d, t in zip(gameday, gametime):
        if not isinstance(d, str) or not d:
            out.append(pd.NaT); continue
        hh, mm = (str(t).split(":") + ["0"])[:2] if isinstance(t, str) and t else ("13", "00")
        local = datetime.strptime(d, "%Y-%m-%d").replace(hour=int(hh), minute=int(mm), tzinfo=ET)
        out.append(pd.Timestamp(local.astimezone(timezone.utc)))
    return pd.Series(pd.to_datetime(out, utc=True))


def sports_schedule(sched: pd.DataFrame) -> pd.DataFrame:
    """Regular-season games, allowlisted columns only, normalised teams and UTC kickoff."""
    cols = [c for c in SCHEDULE_ALLOWLIST if c in sched.columns]
    g = sched[cols].copy()
    for c in SCHEDULE_ALLOWLIST:
        if c not in g.columns:
            g[c] = np.nan
    attest_sports_only(g.columns)
    g = g[g["game_type"].astype(str) == "REG"].copy()
    g["home_team"], g["away_team"] = _team(g["home_team"]), _team(g["away_team"])
    g["kickoff"] = kickoff_utc(g["gameday"].tolist(), g["gametime"].tolist()).to_numpy()
    g["season"] = g["season"].astype(int); g["week"] = g["week"].astype(int)
    return g.reset_index(drop=True)


def read_schedule(root: str) -> pd.DataFrame:
    p = os.path.join(root, "data/raw/nflverse/schedules/games.csv")
    header = pl.read_csv(p, n_rows=0).columns
    keep = [c for c in header if c in SCHEDULE_ALLOWLIST]
    return pl.read_csv(p, columns=keep, infer_schema_length=20000).to_pandas()


def _crosswalk(root: str) -> pd.DataFrame:
    p = os.path.join(root, "data/silver/player_crosswalk.parquet")
    if not os.path.exists(p):
        p = os.path.join(root, "data/raw/nflverse/players/players.parquet")
    cw = pl.read_parquet(p, columns=["gsis_id", "pfr_id"]).drop_nulls().unique(subset=["pfr_id"], keep="first")
    return cw.to_pandas()


def read_stats(root: str, seasons) -> pd.DataFrame:
    frames = []
    for s in seasons:
        p = os.path.join(root, "data/raw/nflverse/stats_player", f"stats_player_week_{s}.parquet")
        if os.path.exists(p):
            frames.append(pl.read_parquet(p).filter(pl.col("season_type") == "REG"))
    st = pl.concat(frames, how="diagonal_relaxed")
    keep = ["player_id", "player_display_name", "position", "season", "week", "game_id", "team", "opponent_team", *STAT_COLS]
    return st.select(keep).to_pandas()


def read_snaps(root: str, seasons) -> pd.DataFrame:
    frames = []
    for s in seasons:
        p = os.path.join(root, "data/raw/nflverse/snap_counts", f"snap_counts_{s}.parquet")
        if os.path.exists(p):
            frames.append(pl.read_parquet(p).filter(pl.col("game_type") == "REG"))
    sc = pl.concat(frames, how="diagonal_relaxed").to_pandas()
    cw = _crosswalk(root)
    sc = sc.merge(cw, left_on="pfr_player_id", right_on="pfr_id", how="inner")
    return sc.rename(columns={"gsis_id": "player_id", "player": "player_display_name", "opponent": "opponent_team"})[
        ["player_id", "player_display_name", "position", "season", "week", "game_id", "team", "opponent_team", "offense_snaps"]]


def build_player_games(stats: pd.DataFrame, snaps: pd.DataFrame, schedule: pd.DataFrame) -> pd.DataFrame:
    """One row per skill player-game: box score + offensive snaps + allowlisted schedule context.

    A player with snaps but no box-score row gets an explicit zero-stat row (nflverse lists only players who
    recorded something). `schedule` must already be `sports_schedule` output."""
    st = stats[stats["position"].isin(SKILL)].drop_duplicates(["player_id", "game_id"], keep="first").copy()
    sn = snaps[snaps["position"].isin(SKILL)].drop_duplicates(["player_id", "game_id"], keep="first")
    st = st.merge(sn[["player_id", "game_id", "offense_snaps"]], on=["player_id", "game_id"], how="left")
    extra = sn[sn["offense_snaps"].fillna(0) > 0].merge(st[["player_id", "game_id"]].assign(_has=True), on=["player_id", "game_id"], how="left")
    extra = extra[extra["_has"].isna()].drop(columns=["_has"])
    for c in STAT_COLS:
        extra[c] = 0.0
    df = pd.concat([st, extra[st.columns]], ignore_index=True)
    df = df[[c for c in PLAYER_ALLOWLIST if c in df.columns]].copy()
    attest_sports_only(df.columns)
    df["team"] = _team(df["team"]); df["opponent_team"] = _team(df["opponent_team"])
    sched = schedule[["game_id", "home_team", "away_team", "home_score", "away_score", "roof", "home_qb_id", "away_qb_id", "kickoff"]]
    df = df.merge(sched, on="game_id", how="inner")
    df["home"] = df["team"] == df["home_team"]
    df["dome"] = df["roof"].astype(str) == "dome"           # a fixed venue property; retractable roof state is NOT used
    df["qb_starter"] = (df["position"] == "QB") & (
        (df["home"] & (df["player_id"] == df["home_qb_id"])) | (~df["home"] & (df["player_id"] == df["away_qb_id"])))
    df["points_for"] = np.where(df["home"], df["home_score"], df["away_score"]).astype(float)
    df["points_against"] = np.where(df["home"], df["away_score"], df["home_score"]).astype(float)
    df = df.drop(columns=["home_team", "away_team", "home_score", "away_score", "roof", "home_qb_id", "away_qb_id"])
    for c in STAT_COLS + ["offense_snaps"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
    df["season"] = df["season"].astype(int); df["week"] = df["week"].astype(int)
    opp = df[STAT_COLS].fillna(0).sum(axis=1) > 0
    df["played"] = (df["offense_snaps"].fillna(0) > 0) | opp
    _starter_fallback(df)
    return df.sort_values(["player_id", "kickoff", "game_id"], kind="mergesort").reset_index(drop=True)


def _starter_fallback(df: pd.DataFrame) -> None:
    """Team-games whose schedule names no starting QB: the QB with the most attempts started (box score)."""
    q = df[df["position"] == "QB"]
    has = q.groupby(["team", "game_id"])["qb_starter"].transform("any")
    miss = q[~has]
    if len(miss):
        top = miss.sort_values("attempts", ascending=False).drop_duplicates(["team", "game_id"]).index
        df.loc[top, "qb_starter"] = True


def load_player_games(root: str, seasons) -> pd.DataFrame:
    sched = sports_schedule(read_schedule(root))
    return build_player_games(read_stats(root, seasons), read_snaps(root, seasons), sched)


def observable_at(kickoff) -> pd.Series:
    """When a played game's box score may be used: kickoff + GAME_DURATION_HOURS."""
    return pd.to_datetime(kickoff, utc=True) + timedelta(hours=GAME_DURATION_HOURS)
