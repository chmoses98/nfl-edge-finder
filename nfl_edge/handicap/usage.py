"""Measured player usage and opponent-allowed production, from nflverse player-week tables, for the analyst dossier.

MEASURED, not projected. For a player: games played, last-four and season per-game targets / receptions / receiving yards / carries / rushing yards /
pass attempts / completions / passing yards, target and carry SHARE of his team (last four), and offensive snap share (last four, from snap counts joined
on name and team). For an opponent: per-game production it ALLOWED to each position group, against the league per-game mean, as an index.

Point in time: only weeks strictly before the game's week are used. The opponent-allowed index is RAW (production allowed, not adjusted for the opposing
offences it faced) and is labelled that way: it is context for a role/matchup question, not an adjusted rating. pandas is imported lazily so that nothing on
the import path of the packet builder needs it.
"""
from __future__ import annotations

import glob
import os

USAGE_VERSION = "usage-1.0.0"

STAT_COLS = ("targets", "receptions", "receiving_yards", "carries", "rushing_yards", "attempts", "completions", "passing_yards")
QB_COLS = ("attempts", "completions", "passing_yards", "carries", "rushing_yards")
SKILL_COLS = ("targets", "receptions", "receiving_yards", "carries", "rushing_yards")
POS_GROUP = {"RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE", "QB": "QB"}


def load_tables(raw_root: str, season: int):
    """(player_week_df, snap_df) or (None, None) when the tables are not on disk. Never fabricates."""
    try:
        import pandas as pd
    except ImportError:
        return None, None
    ps = sorted(glob.glob(os.path.join(raw_root, "stats_player", f"stats_player_week_{season}.parquet")))
    sn = sorted(glob.glob(os.path.join(raw_root, "snap_counts", f"snap_counts_{season}.parquet")))
    stats = pd.read_parquet(ps[0]) if ps else None
    snaps = pd.read_parquet(sn[0]) if sn else None
    if stats is not None:
        stats = stats[(stats["season_type"] == "REG")] if "season_type" in stats.columns else stats
    return stats, snaps


def _per_game(df, cols):
    n = len(df)
    return {c: (round(float(df[c].fillna(0).sum()) / n, 2) if n else None) for c in cols}


def player_usage(stats, snaps, player_id: str | None, name: str | None, team: str | None, week: int) -> dict:
    if stats is None or not player_id:
        return {"state": "UNAVAILABLE", "reason": "player-week table not loaded or no player id"}
    d = stats[(stats["player_id"] == player_id) & (stats["week"] < week)].sort_values("week")
    if d.empty:
        return {"state": "NO_PRIOR_GAMES", "reason": "no regular-season games before this week in the table"}
    last4 = d.tail(4)
    team_rows = stats[(stats["team"] == (team or d["team"].iloc[-1])) & (stats["week"].isin(last4["week"]))]
    tgt_share = car_share = None
    if not team_rows.empty:
        tt = float(team_rows["targets"].fillna(0).sum())
        tc = float(team_rows["carries"].fillna(0).sum())
        tgt_share = round(float(last4["targets"].fillna(0).sum()) / tt, 3) if tt else None
        car_share = round(float(last4["carries"].fillna(0).sum()) / tc, 3) if tc else None
    snap_pct = None
    if snaps is not None and name and team:
        s = snaps[(snaps["player"] == name) & (snaps["team"] == team) & (snaps["week"] < week)].sort_values("week").tail(4)
        if len(s):
            snap_pct = round(float(s["offense_pct"].mean()), 3)
    return {"state": "OK", "games_in_table": int(len(d)), "weeks_last4": [int(w) for w in last4["week"]],
            "per_game_last4": _per_game(last4, STAT_COLS), "per_game_season": _per_game(d, STAT_COLS),
            "target_share_last4": tgt_share, "carry_share_last4": car_share, "offense_snap_pct_last4": snap_pct,
            "per_game_by_week_last4": {int(r.week): {c: float(getattr(r, c) or 0) for c in ("targets", "receptions", "receiving_yards", "carries", "rushing_yards", "attempts")}
                                       for r in last4.itertuples()}}


def allowed_to_position(stats, opp_team: str, week: int) -> dict:
    """Per-game production the opponent has ALLOWED to each position group before `week`, with the league per-game mean and the ratio. RAW (not
    schedule-adjusted)."""
    if stats is None:
        return {"state": "UNAVAILABLE"}
    prior = stats[(stats["week"] < week) & (stats["position"].isin(POS_GROUP))].copy()
    if prior.empty:
        return {"state": "NO_PRIOR_GAMES"}
    prior["grp"] = prior["position"].map(POS_GROUP)
    out: dict = {"state": "OK", "basis": "RAW production allowed per game, regular season before this week; not adjusted for opposing offences", "groups": {}}
    games_by_team = prior.groupby("opponent_team")["week"].nunique()
    for grp in ("RB", "WR", "TE", "QB"):
        g = prior[prior["grp"] == grp]
        tot = g.groupby("opponent_team")[list(STAT_COLS)].sum()
        per = tot.div(games_by_team.reindex(tot.index), axis=0)
        if opp_team not in per.index:
            continue
        lg = per.mean()
        row = per.loc[opp_team]
        keep = QB_COLS if grp == "QB" else SKILL_COLS
        out["groups"][grp] = {c: {"allowed_per_game": round(float(row[c]), 2), "league_mean": round(float(lg[c]), 2),
                                  "index": round(float(row[c]) / float(lg[c]), 2) if float(lg[c]) else None}
                              for c in keep if float(lg[c]) > 0}
        out["games_observed"] = int(games_by_team.get(opp_team, 0))
    return out
