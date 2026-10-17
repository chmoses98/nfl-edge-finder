"""Build point-in-time feature rows for games that have NOT been played yet.

The historical research frame (nfl_edge/research/player_distributions.load_player_games) only contains games
with box scores. To price an upcoming game we append a synthetic row per (player, upcoming game) carrying the
game's pre-kickoff context, run the SAME point-in-time EWMA routine over the combined frame, and keep the
synthetic rows. Because a synthetic row is chronologically last for that player, its features are computed from
strictly prior games — the identical code path used in the walk-forward studies, so there is no second
implementation to drift.

Who gets a row: every player Kalshi actually lists a market for (resolved to a GSIS id), plus the projected
starting QBs from the schedule. We never invent a player Kalshi does not price.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import polars as pl

from nfl_edge.research import player_distributions as pdist

SYNTH_STATS = ["completions", "attempts", "passing_yards", "passing_tds", "passing_interceptions", "carries",
               "rushing_yards", "rushing_tds", "receptions", "targets", "receiving_yards", "receiving_tds"]


def build_prospective_rows(hist: pd.DataFrame, upcoming: pd.DataFrame) -> pd.DataFrame:
    """upcoming: one row per (player_id, game_id) with columns
       player_id, position, season, week, game_id, team, opponent_team, spread_line, total_line, home,
       qb_starter, indoor.  Returns the combined frame ready for add_ewma_features."""
    up = upcoming.copy()
    for c in SYNTH_STATS:
        up[c] = np.nan
    up["offense_snaps"] = np.nan
    up["zero_row"] = False
    up["spread_team"] = np.where(up["home"], up["spread_line"], -up["spread_line"])
    up["implied_total"] = (up["total_line"] + up["spread_team"]) / 2.0
    up["any_td"] = np.nan
    up["touches"] = np.nan
    up["player_display_name"] = up.get("player_display_name", up["player_id"])
    up["is_prospective"] = True
    h = hist.copy()
    h["is_prospective"] = False
    both = pd.concat([h, up], ignore_index=True, sort=False)
    both = both.sort_values(["player_id", "season", "week"], kind="mergesort").reset_index(drop=True)
    return both


def upcoming_from_markets(quotes, player_map: dict, games: pl.DataFrame, season: int,
                          positions: dict, qb_ids: dict | None = None) -> pd.DataFrame:
    """quotes: iterable of classified quote dicts with game_id, player_kalshi_id, team.
    player_map: kalshi player uuid -> gsis id.  positions: gsis -> position.  qb_ids: game_id -> set(gsis)."""
    g = games.to_pandas().set_index("game_id")
    seen = {}
    for q in quotes:
        gid = q.get("game_id"); kid = q.get("player_kalshi_id")
        if not gid or not kid or gid not in g.index:
            continue
        gsis = player_map.get(kid)
        if not gsis:
            continue
        key = (gsis, gid)
        if key in seen:
            continue
        row = g.loc[gid]
        team = q.get("team")
        if team not in (row["home_team"], row["away_team"]):
            team = row["home_team"] if q.get("team") == row["home_team"] else team
        if team is None:
            continue
        home = team == row["home_team"]
        seen[key] = {"player_id": gsis, "player_display_name": q.get("player_name"), "position": positions.get(gsis),
                     "season": int(row["season"]), "week": int(row["week"]), "game_id": gid, "team": team,
                     "opponent_team": row["away_team"] if home else row["home_team"],
                     "spread_line": float(row["spread_line"]) if pd.notna(row["spread_line"]) else np.nan,
                     "total_line": float(row["total_line"]) if pd.notna(row["total_line"]) else np.nan,
                     "home": bool(home), "indoor": str(row.get("roof")) in ("dome", "closed"),
                     "qb_starter": bool(qb_ids and gsis in qb_ids.get(gid, set()))}
    return pd.DataFrame(list(seen.values()))
