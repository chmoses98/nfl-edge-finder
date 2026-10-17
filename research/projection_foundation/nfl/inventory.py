"""Data-availability matrix for the NFL Projection Foundation (counts read from the files on disk).

pit_class:
  archived       captured before kickoff with a timestamp (true point-in-time vintage)
  reconstructable  post-game facts whose timing is unambiguous; usable as features for LATER games only
  retrospective  published/revised at an unknown time relative to kickoff -> may contain post-kickoff information
  missing        not available from allowed sources
"""
from __future__ import annotations

import glob
import os

import pandas as pd

from .data import RAW, ROOT


def _rows(pattern, seasons=None):
    fs = sorted(glob.glob(os.path.join(RAW, pattern)))
    n = 0
    ss = []
    for f in fs:
        try:
            n += pd.read_parquet(f, columns=[]).shape[0] if f.endswith(".parquet") else sum(1 for _ in open(f)) - 1
        except Exception:
            n += len(pd.read_parquet(f))
        tail = os.path.splitext(os.path.basename(f))[0].rsplit("_", 1)[-1]
        if tail.isdigit():
            ss.append(int(tail))
    return n, (f"{min(ss)}-{max(ss)}" if ss else "all")


def build() -> list[dict]:
    inv = []

    def add(ds, pattern, pit_class, notes, seasons=None):
        n, s = _rows(pattern) if pattern else (0, seasons or "-")
        inv.append({"dataset": ds, "seasons": seasons or s, "rows": int(n), "pit_class": pit_class, "notes": notes})

    add("nflverse player weekly stats (stats_player)", "stats_player/stats_player_week_*.parquet", "reconstructable",
        "Outcomes and, lagged, the core features. Release available 1999+; 2012-2026 downloaded (2012-2015 warm-up only). 2026 = weeks 1-5 + Thursday week 6.")
    add("nflverse team weekly stats (stats_team)", "stats_team/stats_team_week_*.parquet", "reconstructable",
        "Team pass attempts / carries / yards per game: team-volume outcomes and opponent 'allowed' histories.")
    add("schedules with closing lines (games.csv)", "schedules/games.csv", "archived",
        "spread_line / total_line are the final pregame (closing) lines: pregame by construction, but recorded retrospectively (not our own vintage). "
        "QB ids are the ACTUAL starter for past games (retrospective; announced pregame in practice) and the projected starter for upcoming games.",
        seasons="1999-2026")
    add("weather / roof (schedule temp, wind, roof)", None, "retrospective",
        "temp/wind are game-time observations, not forecasts -> not used as features. Roof is pregame-known and used. "
        "Timestamped NWS/Open-Meteo forecasts exist only from the 2026 context capture on the market-data branch.", seasons="1999-2026")
    add("snap counts (PFR)", "snap_counts/snap_counts_*.parquet", "reconstructable",
        "2012+. Used for offense-snap share history and to add zero-stat participation rows. Participation itself is post-game.")
    add("injury reports (final designation)", "injuries/injuries_*.parquet", "retrospective",
        "2009-2026 Out/Doubtful/Questionable + practice status. No per-row timestamp (date_modified in 2024 only), rebuilt in place; treated as NEAR-pregame (Friday report) and flagged.")
    add("weekly rosters (status ACT/INA/RES)", "weekly_rosters/roster_weekly_*.parquet", "retrospective",
        "Snapshot time unknown; INA is the gameday inactive list (90 min pre-kickoff). Used only for the forward candidate set, never as a backtest feature.")
    add("depth charts", "depth_charts/depth_charts_*.parquet", "retrospective",
        "2012-2024 weekly NFL depth charts without timestamps (retrospective). 2025+ are ESPN daily snapshots with a 'dt' timestamp (archived). Not used in models (only 2 archived seasons).")
    add("Next Gen Stats (passing/rushing/receiving)", "nextgen_stats/ngs_*.parquet", "reconstructable",
        "2016+ weekly aggregates (separation, cushion). Downloaded, not used in these models (not evaluated here).")
    add("players / rosters / crosswalk", "players/players.parquet", "reconstructable",
        "IDs, rookie season, draft round (draft round is pregame). gsis<->pfr crosswalk built by nfl_edge/data/ids.py.")
    inv.append({"dataset": "play-by-play", "seasons": "1999-2026", "rows": 0, "pit_class": "reconstructable",
                "notes": "Not downloaded for this study (team totals from stats_team suffice); available from the pbp release if drive-level pace is needed."})
    inv.append({"dataset": "pbp participation (routes, personnel)", "seasons": "2016-2025", "rows": 0, "pit_class": "reconstructable",
                "notes": "Not downloaded. research/opportunity found route/role shares improve target and carry projection as extra regressors (7/7 seasons) but not on the Kalshi-listed population (research/listed_validation) — priority candidate."})
    inv.append({"dataset": "archived pregame incumbent projections (shadow ledger)", "seasons": "2026",
                "rows": len(glob.glob(os.path.join(ROOT, "data", "shadow", "ledger", "*", "*.observations.jsonl.gz"))),
                "pit_class": "archived",
                "notes": "Week-1 2026 ledger in this checkout; later weeks on the market-data branch. Not needed: the incumbent was replayed walk-forward with its own code (nfl/incumbent.py)."})
    inv.append({"dataset": "pregame timestamped injury/availability vintages", "seasons": "2026 only", "rows": 0, "pit_class": "archived",
                "notes": "Sleeper/ESPN captures on the market-data branch (context-capture.yml) start in 2026: too short for a backtest. Historical seasons have no timestamped vintage -> missing."})
    return inv
