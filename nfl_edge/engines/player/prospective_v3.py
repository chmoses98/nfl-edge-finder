"""PROSPECTIVE INPUTS for DATA_PLAYER_V3: the three input defects of the v2 data arm, fixed at the input, point in time.

The v2 data arm was fitted on rows whose game environment came from the consensus closing line, and applied to
prospective rows whose game environment was NaN -- because `mask_target_season` correctly blanks every
target-season line (a closing line is never point-in-time) and `design()` then turned the NaN into 0.0. A team
with an implied total of zero points projects almost no volume, and the arm was ~40% low across the board (5x low
on touchdowns). Held out on the 2025 Kalshi rungs, that defect alone moved the arm from +0.0099 to +0.0383 Brier
against the market -- the whole of its measured 2026 week-2 deficit (+0.036).

This module supplies, for each prospective row:

    game environment   the MARKET-IMPLIED spread and total of the game at the cutoff (the same Kalshi-implied centre
                       the game engine prices from), never a closing line and never a zero. A game with no identified
                       environment gets NO data distribution -- a refusal, not a guess.
    current season     completed games of the target season whose kickoff is at least COMPLETE_AFTER_HOURS before the
                       cutoff, so a week-2 projection knows what the player did in week 1 (v2 knew only last season).
    starting QB        the depth-chart QB1 of the team at the cutoff (nfl_edge/context/role.py). v2 read the
                       schedule's QB ids, which the point-in-time mask blanks for every unplayed game, so no pregame
                       quarterback row ever qualified and every passing statistic was DATA_UNAVAILABLE.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

V3_INPUTS_VERSION = "player-inputs-3.0.0"
COMPLETE_AFTER_HOURS = 4.0


def completed_current_season(hist: pd.DataFrame, target_season: int, kickoffs: dict, cutoff: datetime,
                             exclude_games=()) -> tuple[pd.DataFrame, dict]:
    """Keep every prior-season row, and target-season rows only for games finished before the cutoff."""
    lim = cutoff - timedelta(hours=COMPLETE_AFTER_HOURS)
    cur = hist.season == target_season
    ok_games = {g for g, k in kickoffs.items() if k is not None and k <= lim and g not in set(exclude_games)}
    keep = ~cur | hist.game_id.isin(ok_games)
    kept = hist[keep].copy()
    used = sorted(set(kept.loc[kept.season == target_season, "game_id"]))
    newest = max((kickoffs[g] for g in used if kickoffs.get(g) is not None), default=None)
    info = {"target_season_games_used": len(used), "target_season_rows_used": int((kept.season == target_season).sum()),
            "target_season_rows_dropped": int((cur & ~keep).sum()), "newest_game_kickoff": newest.isoformat() if newest else None,
            "complete_after_hours": COMPLETE_AFTER_HOURS}
    return kept, info


def attach_market_environment(upcoming: pd.DataFrame, envs: dict) -> pd.DataFrame:
    """spread_line / total_line of each prospective row from the market-implied environment of its game.

    Sign convention is nflverse's: spread_line is the expected HOME margin, which is exactly the game engine's
    `spread` centre. A game without an environment keeps NaN and `env_known` False."""
    up = upcoming.copy()
    sp = up["game_id"].map(lambda g: (envs.get(g) or {}).get("spread"))
    tt = up["game_id"].map(lambda g: (envs.get(g) or {}).get("total"))
    src = up["game_id"].map(lambda g: (envs.get(g) or {}).get("source"))
    up["spread_line"] = pd.to_numeric(sp, errors="coerce")
    up["total_line"] = pd.to_numeric(tt, errors="coerce")
    up["env_source"] = src
    up["env_known"] = up["spread_line"].notna() & up["total_line"].notna()
    return up


def depth_qb_starters(upcoming: pd.DataFrame, qb1_by_team: dict) -> pd.DataFrame:
    """qb_starter from the depth-chart QB1 at the cutoff; `qb1_known` says whether the team had one."""
    up = upcoming.copy()
    q = up["team"].map(lambda t: qb1_by_team.get(t))
    up["qb1_known"] = q.notna()
    up["qb_starter"] = (up["player_id"] == q) & q.notna()
    return up


def usable_rows(feat: pd.DataFrame) -> np.ndarray:
    """A prospective row may get a data distribution only if its game environment is known."""
    if "env_known" not in feat.columns:
        return np.zeros(len(feat), bool)
    return feat["env_known"].fillna(False).astype(bool).to_numpy()
