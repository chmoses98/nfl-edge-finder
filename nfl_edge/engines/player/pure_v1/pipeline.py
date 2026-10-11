"""End-to-end PURE_PLAYER_V1 / PURE_EWM_BASELINE forecasts for one target season, plus the kit sidecar export.

    rows, teams = features.build(data.build_player_games(...))       # football data only
    out = run(rows, teams, target_season)                             # fit on seasons < target, forecast target
    sidecar_rows(out["player"]["PURE_PLAYER_V1"], ...)                # interim PURE JSONL format (one row per player-game-stat)

The forecast cutoff of every row is kickoff - AS_OF_LEAD; every row also carries the latest football observation it
consumed (`src_max`), and `run` refuses to return a row whose observation is not strictly before its cutoff.
"""
from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME
from nfl_edge.engines.player.pure_v1 import baseline as B
from nfl_edge.engines.player.pure_v1 import model as M

AS_OF_LEAD = timedelta(minutes=90)
ID_COLS = ["game_id", "player_id", "season", "week", "team", "opponent_team", "position", "pgroup", "kickoff", "src_max"]


class PointInTimeError(AssertionError):
    pass


def _long(d: pd.DataFrame, store: dict, means: dict, lineage: dict) -> pd.DataFrame:
    parts = []
    for stat in M.STATS:
        f = M.forecast(store, d, means, stat)
        if not len(f):
            continue
        sub = d.loc[f.index, ID_COLS].copy()
        sub["statistic"] = stat
        sub = pd.concat([sub, f], axis=1)
        sub["actual"] = M.outcome(d.loc[f.index], stat)
        sub["played"] = d.loc[f.index, "played"].to_numpy(bool)
        sub["lineage"] = [dict(zip(lineage[stat], vals)) for vals in d.loc[f.index, lineage[stat]].to_numpy(float).tolist()]
        # a forecast whose outcome is missing in the sports data (e.g. a snap count the crosswalk cannot join) is
        # forecast but cannot be scored; it is dropped from the scored table and counted, identically for every arm
        parts.append(sub[np.isfinite(sub["actual"].to_numpy(float))])
    return pd.concat(parts, ignore_index=True)


def check_point_in_time(d: pd.DataFrame) -> None:
    as_of = pd.to_datetime(d["kickoff"], utc=True) - AS_OF_LEAD
    src = pd.to_datetime(d["src_max"], utc=True)
    bad = src.notna() & ~(src < as_of)
    if bad.any():
        raise PointInTimeError(f"{int(bad.sum())} rows consumed an observation at or after their cutoff")


def run(rows: pd.DataFrame, t: pd.DataFrame, target_season: int, *, weeks=None) -> dict:
    model = M.fit(rows, t, target_season)
    base = B.fit(rows, t, target_season)
    te = rows[(rows.season == target_season) & rows.played]
    if weeks is not None:
        te = te[te.week.isin(list(weeks))]
    te = te.reset_index(drop=True)
    check_point_in_time(te)
    d = model.intermediates(te, t)
    player = {MODEL_NAME: _long(d, model.dist, model.means(d), M.LINEAGE),
              BASELINE_NAME: _long(d, base.dist, B.means(d), B.LINEAGE)}
    tt = t[(t.season == target_season) & t.pa.notna()]
    if weeks is not None:
        tt = tt[tt.week.isin(list(weeks))]
    team = {MODEL_NAME: model.team_predict(tt), BASELINE_NAME: B.team_predict(tt)}
    actual = tt[["team", "game_id", "season", "week", "pa", "ra", "plays", "pts"]].reset_index(drop=True)
    for k in team:
        team[k] = actual.merge(team[k], on=["team", "game_id"], how="left")
    pop = {stat: int(M.population(d, stat).sum()) for stat in M.STATS}
    return {"model": model, "baseline": base, "intermediates": d, "player": player, "team": team, "population_counts": pop,
            "team_sd": {MODEL_NAME: model.team_sd, BASELINE_NAME: base.team_sd}}


# ------------------------------------------------------------------------------------------------ kit sidecar
def _iso(ts) -> str:
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def sidecar_rows(long: pd.DataFrame, model_version: str, train_through: str) -> tuple[list[dict], list[dict]]:
    """Kit interim PURE format (scripts/prop_projection_gate.py): forecasts and matching outcomes."""
    fc, oc = [], []
    for r in long.itertuples(index=False):
        k = pd.Timestamp(r.kickoff)
        feats = {"lineage": {a: (None if not np.isfinite(b) else round(float(b), 5)) for a, b in r.lineage.items()},
                 "sources": "nflverse stats_player_week + snap_counts + schedule(allowlisted non-market columns)",
                 "train_seasons_observed_through": train_through,
                 "abstained_inputs": ["injury_reports", "depth_charts", "weather", "target_game_starting_qb_identity"],
                 "population": "every eligible skill player-game in sports data, conditional on own participation"}
        fc.append({"sport": "NFL", "game_id": r.game_id, "player_id": r.player_id, "statistic": r.statistic,
                   "as_of": _iso(k - AS_OF_LEAD), "kickoff": _iso(k), "source_max_observed_at": _iso(r.src_max),
                   "model_version": model_version, "projection_mode": "PURE_INDEPENDENT", "conditional_on_playing": True,
                   "projection": {"mean": round(float(r.mean), 4), "median": round(float(r.median), 4), "p10": round(float(r.p10), 4),
                                  "p90": round(float(r.p90), 4),
                                  "thresholds": [{"at_least": float(a), "probability": round(float(p), 5)} for a, p in r.thresholds]},
                   "model_features": feats})
        oc.append({"sport": "NFL", "game_id": r.game_id, "player_id": r.player_id, "statistic": r.statistic,
                   "actual": float(r.actual), "played": bool(r.played)})
    return fc, oc
