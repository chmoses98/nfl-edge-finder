"""NFL Projection Foundation: raw nflverse -> player-game and team-game frames.

Inputs are the bronze nflverse release files downloaded by `scripts/data/nflverse_download.py` into
data/raw/nflverse (gitignored, immutable release URLs) plus the repo's silver crosswalk
(data/silver/player_crosswalk.parquet, built by nfl_edge/data/ids.py). Nothing here is a feature:
outcomes and identifiers only. Point-in-time features live in features.py.

Availability convention (explicit, see RESULTS_NFL.md "Availability"):
  * A player-game row exists iff the player took >= 1 offensive snap (snap counts) or recorded a stat.
    "Did he play" is a POST-game fact, so every player-level metric in this study is CONDITIONAL ON
    PARTICIPATION, the same convention sportsbook props settle under (DNP = void). The participation
    probability is modelled separately (availability.py) from pregame information only (injury report
    designation, last-game role) and its effect is quantified there.
  * Missed games never enter a player's history (they are not zeros).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RAW = os.path.join(ROOT, "data", "raw", "nflverse")
CACHE = os.path.join(ROOT, "research", "projection_foundation", ".cache")
SKILL = ["QB", "RB", "WR", "TE"]
TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA", "ARZ": "ARI", "AZ": "ARI", "BLT": "BAL", "CLV": "CLE",
            "HST": "HOU", "JAC": "JAX", "SL": "LA", "LAR": "LA", "WSH": "WAS"}
FIRST_SEASON = 2012          # snap counts start 2012; 2012-2015 are warm-up history only
STAT_COLS = ["completions", "attempts", "passing_yards", "passing_tds", "passing_interceptions", "sacks_suffered",
             "carries", "rushing_yards", "rushing_tds", "receptions", "targets", "receiving_yards", "receiving_tds",
             "receiving_air_yards", "passing_air_yards"]


def _fix(s: pd.Series) -> pd.Series:
    return s.replace(TEAM_FIX)


def load_schedule() -> pd.DataFrame:
    g = pd.read_csv(os.path.join(RAW, "schedules", "games.csv"), low_memory=False)
    g["home_team"] = _fix(g["home_team"])
    g["away_team"] = _fix(g["away_team"])
    g = g[(g.game_type == "REG") & (g.season >= FIRST_SEASON)].copy()
    # kickoff in UTC from US/Eastern local gameday+gametime
    ts = pd.to_datetime(g["gameday"] + " " + g["gametime"].fillna("13:00"), errors="coerce")
    g["kickoff_utc"] = ts.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="shift_forward").dt.tz_convert("UTC")
    g["block"] = g.season * 100 + g.week
    return g


def team_games(sched: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per (team, game): outcomes (pass attempts, rush attempts, points) + pregame market context."""
    sched = load_schedule() if sched is None else sched
    frames = []
    for s in sorted(sched.season.unique()):
        p = os.path.join(RAW, "stats_team", f"stats_team_week_{s}.parquet")
        if os.path.exists(p):
            t = pd.read_parquet(p)
            frames.append(t[t.season_type == "REG"])
    st = pd.concat(frames, ignore_index=True)
    st["team"] = _fix(st["team"])
    keep = ["game_id", "team", "attempts", "completions", "carries", "passing_yards", "rushing_yards", "targets",
            "receptions", "receiving_yards", "passing_tds", "rushing_tds", "sacks_suffered", "receiving_air_yards"]
    st = st[keep].rename(columns={c: f"tm_{c}" for c in keep if c not in ("game_id", "team")})
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        d = sched[["game_id", "season", "week", "block", "gameday", "kickoff_utc", "spread_line", "total_line", "roof",
                   "temp", "wind", "div_game", f"{side}_team", f"{opp}_team", f"{side}_score", f"{opp}_score",
                   f"{side}_qb_id", f"{side}_rest", f"{opp}_rest"]].copy()
        d.columns = ["game_id", "season", "week", "block", "gameday", "kickoff_utc", "spread_line", "total_line", "roof",
                     "temp", "wind", "div_game", "team", "opp", "points", "opp_points", "qb_id", "rest", "opp_rest"]
        d["home"] = int(side == "home")
        # spread_line is home-favoured positive (nflverse): team spread = + for favourite
        d["spread_team"] = d["spread_line"] if side == "home" else -d["spread_line"]
        rows.append(d)
    tg = pd.concat(rows, ignore_index=True)
    tg["implied_total"] = (tg.total_line + tg.spread_team) / 2
    tg["indoor"] = tg.roof.isin(["dome", "closed"]).astype(int)
    tg = tg.merge(st, on=["game_id", "team"], how="left")
    tg["played"] = tg.points.notna()
    return tg.sort_values(["team", "kickoff_utc"]).reset_index(drop=True)


def _crosswalk() -> pd.DataFrame:
    p = os.path.join(ROOT, "data", "silver", "player_crosswalk.parquet")
    cw = pd.read_parquet(p, columns=["gsis_id", "pfr_id", "rookie_season", "draft_round", "birth_date"])
    return cw


def player_games(sched: pd.DataFrame | None = None) -> pd.DataFrame:
    """Skill-position player-game rows (participated), outcomes + identifiers + team totals."""
    sched = load_schedule() if sched is None else sched
    seasons = sorted(sched.season.unique())
    frames = []
    for s in seasons:
        p = os.path.join(RAW, "stats_player", f"stats_player_week_{s}.parquet")
        if os.path.exists(p):
            t = pd.read_parquet(p, columns=["player_id", "player_display_name", "position", "season", "week", "season_type",
                                            "game_id", "team", "opponent_team"] + STAT_COLS)
            frames.append(t[(t.season_type == "REG") & t.position.isin(SKILL)])
    st = pd.concat(frames, ignore_index=True).drop(columns="season_type")
    st = st.drop_duplicates(["player_id", "game_id"])
    st["team"] = _fix(st["team"])
    st["opponent_team"] = _fix(st["opponent_team"])
    # snap counts (2012+) -> offense snaps / pct and zero rows for players with snaps but no stat line
    cw = _crosswalk()
    pfr = cw[["gsis_id", "pfr_id"]].dropna().drop_duplicates("pfr_id")
    sframes = []
    for s in seasons:
        p = os.path.join(RAW, "snap_counts", f"snap_counts_{s}.parquet")
        if os.path.exists(p):
            t = pd.read_parquet(p)
            sframes.append(t[t.game_type == "REG"])
    sc = pd.concat(sframes, ignore_index=True)
    sc = sc.merge(pfr, left_on="pfr_player_id", right_on="pfr_id", how="inner")
    sc["team"] = _fix(sc["team"])
    sc["opponent"] = _fix(sc["opponent"])
    sc = sc.drop_duplicates(["gsis_id", "game_id"])
    st = st.merge(sc[["gsis_id", "game_id", "offense_snaps", "offense_pct"]].rename(columns={"gsis_id": "player_id"}),
                  on=["player_id", "game_id"], how="left")
    st["zero_row"] = False
    have = set(zip(st.player_id, st.game_id))
    z = sc[(sc.offense_snaps > 0) & sc.position.isin(SKILL)]
    z = z[[(a, b) not in have for a, b in zip(z.gsis_id, z.game_id)]]
    zero = pd.DataFrame({"player_id": z.gsis_id, "player_display_name": z.player, "position": z.position,
                         "season": z.season, "week": z.week, "game_id": z.game_id, "team": z.team,
                         "opponent_team": z.opponent, "offense_snaps": z.offense_snaps, "offense_pct": z.offense_pct})
    for c in STAT_COLS:
        zero[c] = 0
    zero["zero_row"] = True
    pg = pd.concat([st, zero], ignore_index=True)
    # positions: nflverse stats position can drift; use the player's modal position across his career (stable role id)
    pos = pg.groupby("player_id")["position"].agg(lambda s: s.mode().iat[0])
    pg["position"] = pg.player_id.map(pos)
    pg = pg[pg.position.isin(SKILL)]
    tg = team_games(sched)
    pg = pg.merge(tg[["game_id", "team", "block", "kickoff_utc", "gameday", "opp", "home", "spread_team", "total_line",
                      "implied_total", "indoor", "qb_id", "tm_attempts", "tm_carries", "tm_targets", "points", "wind"]],
                  on=["game_id", "team"], how="inner")
    for c in STAT_COLS:
        pg[c] = pg[c].fillna(0).astype(float)
    pg["any_td"] = ((pg.rushing_tds + pg.receiving_tds) >= 1).astype(float)
    pg["n_td"] = pg.rushing_tds + pg.receiving_tds
    pg["touches"] = pg.targets + pg.carries
    pg["target_share"] = pg.targets / pg.tm_targets.where(pg.tm_targets > 0)
    pg["carry_share"] = pg.carries / pg.tm_carries.where(pg.tm_carries > 0)
    pg["pass_share"] = pg.attempts / pg.tm_attempts.where(pg.tm_attempts > 0)
    pg["qb_starter"] = (pg.position == "QB") & (pg.player_id == pg.qb_id)
    meta = cw.drop_duplicates("gsis_id").set_index("gsis_id")
    pg["rookie_season"] = pg.player_id.map(meta["rookie_season"])
    pg["draft_round"] = pg.player_id.map(meta["draft_round"])
    pg["is_rookie"] = (pg.season == pg.rookie_season).astype(int)
    pg = pg.sort_values(["player_id", "kickoff_utc", "game_id"], kind="mergesort").reset_index(drop=True)
    return pg


def injuries() -> pd.DataFrame:
    """Final pregame injury designation per (season, week, team, player). nflverse carries no reliable
    per-row timestamp (date_modified only in some seasons), so this is treated as NEAR-pregame: the
    designation is published on the Friday (Saturday/Monday for other slates) final report."""
    frames = []
    for s in range(2009, 2027):
        p = os.path.join(RAW, "injuries", f"injuries_{s}.parquet")
        if os.path.exists(p):
            t = pd.read_parquet(p, columns=["season", "game_type", "team", "week", "gsis_id", "report_status", "practice_status"])
            frames.append(t[t.game_type == "REG"])
    inj = pd.concat(frames, ignore_index=True)
    inj["team"] = _fix(inj["team"])
    inj = inj.drop_duplicates(["season", "week", "gsis_id"], keep="last")
    return inj


def weekly_roster() -> pd.DataFrame:
    frames = []
    for s in range(FIRST_SEASON, 2027):
        p = os.path.join(RAW, "weekly_rosters", f"roster_weekly_{s}.parquet")
        if os.path.exists(p):
            t = pd.read_parquet(p, columns=["season", "week", "team", "gsis_id", "position", "status", "game_type"])
            frames.append(t[t.game_type == "REG"])
    r = pd.concat(frames, ignore_index=True)
    r["team"] = _fix(r["team"])
    return r.drop_duplicates(["season", "week", "gsis_id"], keep="last")


def cached(name: str, builder, force: bool = False) -> pd.DataFrame:
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, f"{name}.parquet")
    if os.path.exists(p) and not force:
        return pd.read_parquet(p)
    df = builder()
    df.to_parquet(p, index=False)
    return df
