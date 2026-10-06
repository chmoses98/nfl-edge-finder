"""A1 -- information-horizon-correct availability. RESEARCH_ONLY.

Preregistered in research/game_script_v2/wave2/PREREGISTRATION.md, section 5.

The incumbent historical eligible set is built from the FINAL weekly roster, whose INA status is the game-day
inactive list (public about 90 minutes before kickoff), yet a QUESTIONABLE player who survived that list still gets
the questionable participation discount -- a T-0 information set with a T-24 discount. Every Wave-2 artifact names
its horizon:

  T0_GAMEDAY_INACTIVES_WITH_Q_DISCOUNT   the incumbent historical backtest (relabelled, unchanged)
  T0_INACTIVES                           inactives known; INA excluded; a QUESTIONABLE player not inactive is
                                         EXPECTED_ACTIVE (no second discount)
  T24                                    no game-day information: INA is treated as on the active roster;
                                         QUESTIONABLE keeps its discount

Only the EVALUATION season's rows change; the models are trained exactly as the incumbent.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from . import data as D
from . import features as F

A1_VERSION = "sim-a1-1.0.0"
HORIZONS = ("T0_GAMEDAY_INACTIVES_WITH_Q_DISCOUNT", "T0_INACTIVES", "T24")
INACTIVE_RELEASE = timedelta(minutes=90)


def eligible_t24(season: int) -> pd.DataFrame:
    """The season's eligible set WITHOUT game-day inactive information (INA read as ACT); same rules otherwise."""
    games = D.schedule().to_pandas()
    g = games[(games["season"] == season) & games["game_type"].isin(["REG", "WC", "DIV", "CON", "SB"]) & games["home_score"].notna()]
    rows = []
    for week in sorted(g["week"].unique()):
        gw = g[g["week"] == week]
        if season >= 2025:
            depth = F.depth_chart(season, cutoff=pd.Timestamp(gw["gameday"].min()).tz_localize("UTC").to_pydatetime())
        else:
            depth = F.depth_chart(season, week=int(week))
        roster = F.weekly_roster(season, int(week))
        if roster.empty:
            roster = F.weekly_roster(season, int(g["week"].max()))
        roster = roster.assign(status=np.where(roster["status"] == "INA", "ACT", roster["status"]))
        inj = F.injury_designations(season, int(week))
        for r in gw.itertuples():
            for team in (r.home_team, r.away_team):
                e = F.eligible_players(season, int(week), team, depth=depth, roster=roster, injuries=inj, history=None)
                if e.empty:
                    continue
                e["game_id"] = r.game_id; e["season"] = season; e["week"] = int(week)
                rows.append(e)
    return pd.concat(rows, ignore_index=True)


def apply_horizon(frames: dict, season: int, horizon: str) -> dict:
    """Frames for the evaluation season at the given horizon (a frames_hook for five_year.run_season)."""
    if horizon not in HORIZONS:
        raise ValueError(horizon)
    if horizon == "T0_GAMEDAY_INACTIVES_WITH_Q_DISCOUNT":
        return frames
    if horizon == "T0_INACTIVES":
        out = dict(frames)
        e = frames["eligible"].copy()
        m = (e["season"] == season) & (e["avail_state"] == "QUESTIONABLE")
        e["a1_original_state"] = e["avail_state"]
        e.loc[m, "avail_state"] = "EXPECTED_ACTIVE"
        out["eligible"] = e
        out["a1_horizon"] = horizon
        return out
    # T24: rebuild the frames with the evaluation season's eligible set read without inactive information
    from . import training as T
    seasons = sorted(int(s) for s in frames["eligible"]["season"].unique())
    base = T.eligible_frame([s for s in seasons if s != season], verbose=lambda *a: None)
    override = pd.concat([base, eligible_t24(season)], ignore_index=True)
    out = T.assemble(seasons, verbose=lambda *a: None, priors=frames["priors"], eligible_override=override)
    out["a1_horizon"] = horizon
    return out


def prospective_horizon(cutoff: datetime, kickoff: datetime, roster_week: pd.DataFrame, team: str,
                        roster_retrieved_at: datetime | None = None) -> tuple[str, str]:
    """The horizon a prospective record for one team may claim, and why. T0_INACTIVES only when the cutoff is at or
    after the inactive release AND the roster vintage read at the cutoff already carries game-day statuses (an INA)
    for the team AND that roster file was retrieved at or before the cutoff -- a replay of a past cutoff reading a
    later roster download must not learn the inactive list backwards. Otherwise T24."""
    if cutoff.tzinfo is None or kickoff.tzinfo is None:
        raise ValueError("timezone-aware instants required")
    if cutoff < kickoff - INACTIVE_RELEASE:
        return "T24", "cutoff before the inactive release"
    if roster_retrieved_at is None or roster_retrieved_at > cutoff:
        return "T24", "roster vintage not provably retrieved at or before the cutoff"
    has_ina = bool(((roster_week["team"] == team) & (roster_week["status"] == "INA")).any())
    if not has_ina:
        return "T24", "inactive list not observed in the roster vintage read at the cutoff"
    return "T0_INACTIVES", "cutoff after the inactive release and the roster carries game-day statuses"


def availability_states(states: pd.Series, horizon: str) -> pd.Series:
    """The participation state the simulator uses for each eligible row at a horizon."""
    if horizon == "T0_INACTIVES":
        return states.where(states != "QUESTIONABLE", "EXPECTED_ACTIVE")
    return states


def roster_retrieved_at(root: str, season: int) -> datetime | None:
    """Retrieval instant of the weekly-roster file from the nflverse download manifest (None if unknown)."""
    import json, os
    path = os.path.join(root, "data", "raw", "nflverse", "_manifest.jsonl")
    want = f"data/raw/nflverse/weekly_rosters/roster_weekly_{season}.parquet"
    best = None
    if os.path.exists(path):
        for line in open(path):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("path") == want and r.get("retrieved_at"):
                t = datetime.fromisoformat(r["retrieved_at"].replace("Z", "+00:00"))
                best = t if best is None or t > best else best
    return best
