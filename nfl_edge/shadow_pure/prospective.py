"""Prospective PURE_PLAYER_V1 / PURE_EWM_BASELINE forecasts for games that have not been played.

The frozen package (nfl_edge/engines/player/pure_v1) was written for walk-forward evaluation: its rows are
player-games that exist in the box score. For an upcoming game there is no box score, so this module appends one
synthetic row per (candidate player, upcoming game) with every outcome NaN, runs the package's OWN public stages
(team_games -> add_team_features -> add_player_features -> fit -> intermediates -> forecast) unchanged, and keeps
the synthetic rows. A synthetic row is chronologically last for its player and team, so its features come from
strictly prior games by the same code path the preregistered study used -- there is no second implementation.

Population (decided from football data only, before kickoff; never from a market listing):
    every QB / RB / WR / TE whose most recent appearance (>= 1 offensive snap or a box-score line) was for the team,
    in one of the team's last LOOKBACK_TEAM_GAMES games, plus the team's designated starting QB.
Forecasts are CONDITIONAL ON PLAYING (participation is not modelled). QB passing statistics are conditional on
starting; the assumed starter is the schedule vintage's starting-QB id (nflverse games.csv as fetched before the
cutoff) or, if blank, the starter of the team's previous game. Evaluation scores a QB-passing row only if he did
start, and counts the misses.

Two outcome columns of the target team-game are touched, both only for the synthetic game: the team-game's realised
volume/points are set to NaN (never 0) so nothing downstream can read a fabricated zero, and `team_snaps` is set to
a placeholder 1.0 because the frozen population rule for snap share requires a finite team snap count; it is the
DENOMINATOR OF THE (unknown) OUTCOME, never a model input (forecast means read only prior EWMs).
"""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME
from nfl_edge.engines.player.pure_v1 import baseline as B
from nfl_edge.engines.player.pure_v1 import data as D
from nfl_edge.engines.player.pure_v1 import features as F
from nfl_edge.engines.player.pure_v1 import model as M

LOOKBACK_TEAM_GAMES = 3
TEAM_OUTCOMES = ["pa", "ra", "plays", "pts", "pts_against", "pass_yds", "rush_yds", "cmp", "tgt", "rec", "rec_yds", "team_snaps"]
SCRIPT_MARGIN_SHIFT = 7.0       # points of football-only expected margin for the script-sensitivity diagnostic


class PreKickoffError(RuntimeError):
    pass


def upcoming_games(sched: pd.DataFrame, as_of: datetime, *, game_ids=None, horizon_hours: float = 8 * 24) -> pd.DataFrame:
    """Regular-season games strictly after as_of (and within the horizon), from `data.sports_schedule` output."""
    a = pd.Timestamp(as_of)
    g = sched[(sched["kickoff"] > a) & (sched["kickoff"] <= a + pd.Timedelta(hours=horizon_hours))].copy()
    g = g.sort_values(["kickoff", "game_id"]).reset_index(drop=True)
    # only each team's NEXT game: a later game's features would otherwise be computed through an unplayed one
    nxt = {}
    for r in g.itertuples(index=False):
        for team in (r.home_team, r.away_team):
            nxt.setdefault(team, r.game_id)
    g = g[[nxt.get(h) == gid and nxt.get(a_) == gid for h, a_, gid in zip(g["home_team"], g["away_team"], g["game_id"])]]
    if game_ids is not None:
        g = g[g["game_id"].isin(list(game_ids))]
    return g.reset_index(drop=True)


def _observed(pg: pd.DataFrame, as_of) -> pd.DataFrame:
    """Only games whose box score was observable before as_of (kickoff + 4 h < as_of)."""
    return pg[D.observable_at(pg["kickoff"]) < pd.Timestamp(as_of)]


def candidates(pg: pd.DataFrame, games: pd.DataFrame, as_of) -> pd.DataFrame:
    """Synthetic player-game rows (all outcomes NaN) for every candidate player of every upcoming game."""
    hist = _observed(pg, as_of)
    played = hist[hist["played"]]
    last = played.sort_values(["player_id", "kickoff", "game_id"], kind="mergesort").groupby("player_id").tail(1)
    tg = hist[["team", "game_id", "kickoff"]].drop_duplicates().sort_values(["team", "kickoff", "game_id"], kind="mergesort")
    recent = tg.groupby("team").tail(LOOKBACK_TEAM_GAMES)
    last_starter = (hist[hist["qb_starter"]].sort_values(["team", "kickoff"], kind="mergesort").groupby("team").tail(1)
                    .set_index("team")["player_id"].to_dict())
    rows = []
    for g in games.itertuples(index=False):
        for team, opp, home, qb_sched in ((g.home_team, g.away_team, True, g.home_qb_id), (g.away_team, g.home_team, False, g.away_qb_id)):
            rg = set(recent.loc[recent["team"] == team, "game_id"])
            mine = last[(last["team"] == team) & last["game_id"].isin(rg)]
            starter = qb_sched if isinstance(qb_sched, str) and qb_sched else last_starter.get(team)
            starter_src = "schedule_vintage" if isinstance(qb_sched, str) and qb_sched else ("previous_game_starter" if starter else "none")
            ids = list(mine["player_id"])
            meta = {r.player_id: (r.player_display_name, r.position) for r in mine.itertuples()}
            if starter and starter not in meta:
                prev = hist[hist["player_id"] == starter].sort_values("kickoff").tail(1)
                if len(prev):
                    meta[starter] = (prev["player_display_name"].iloc[0], prev["position"].iloc[0])
                else:
                    meta[starter] = (starter, "QB")
                ids.append(starter)
            for pid in ids:
                name, pos = meta[pid]
                if pos not in D.SKILL:
                    continue
                r = {"player_id": pid, "player_display_name": name, "position": pos, "season": int(g.season), "week": int(g.week),
                     "game_id": g.game_id, "team": team, "opponent_team": opp, "kickoff": g.kickoff, "home": home,
                     "dome": str(g.roof) == "dome", "qb_starter": bool(pos == "QB" and pid == starter),
                     "points_for": np.nan, "points_against": np.nan, "played": True, "offense_snaps": np.nan,
                     "starter_basis": starter_src if pos == "QB" and pid == starter else None}
                for c in D.STAT_COLS:
                    r[c] = np.nan
                rows.append(r)
    out = pd.DataFrame(rows)
    if len(out):
        out = out.drop_duplicates(["player_id", "game_id"], keep="first")
    return out


def build(pg: pd.DataFrame, synth: pd.DataFrame, as_of) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Features for history + synthetic rows through the frozen package's own stages."""
    hist = _observed(pg, as_of).copy()
    hist["_prospective"] = False
    s = synth.drop(columns=["starter_basis"], errors="ignore").copy()
    s["_prospective"] = True
    allr = pd.concat([hist, s[hist.columns]], ignore_index=True)
    allr = allr.sort_values(["player_id", "kickoff", "game_id"], kind="mergesort").reset_index(drop=True)
    pros_games = set(s["game_id"])
    t = F.team_games(allr.drop(columns=["_prospective"]))
    mask = t["game_id"].isin(pros_games)
    for c in TEAM_OUTCOMES:
        if c in t.columns:
            t.loc[mask, c] = np.nan
    t = F.add_team_features(t)
    rows = F.add_player_features(allr, t)
    rows.loc[rows["_prospective"], "team_snaps"] = 1.0         # population placeholder; see module docstring
    return rows, t


def fit(rows: pd.DataFrame, t: pd.DataFrame, target_season: int):
    hist = rows[~rows["_prospective"]]
    return M.fit(hist, t, target_season), B.fit(hist, t, target_season)


def forecast(rows: pd.DataFrame, t: pd.DataFrame, model, base, as_of) -> dict:
    """{arm: long frame (one row per player-game-statistic)}, intermediates, and the script-sensitivity frame."""
    te = rows[rows["_prospective"]].reset_index(drop=True)
    a = pd.Timestamp(as_of)
    if (pd.to_datetime(te["kickoff"], utc=True) <= a).any():
        raise PreKickoffError("a forecast row's kickoff is at or before as_of")
    src = pd.to_datetime(te["src_max"], utc=True)
    if (src.notna() & ~(src < a)).any():
        raise PreKickoffError("a forecast row consumed an observation at or after as_of")
    tt = t[t["game_id"].isin(set(te["game_id"]))]
    d = model.intermediates(te, tt)
    out = {MODEL_NAME: _long(d, model.dist, model.means(d), M.LINEAGE), BASELINE_NAME: _long(d, base.dist, B.means(d), B.LINEAGE)}
    # script sensitivity: forecast-mean change when the football-only expected margin of the team is +7 (and the
    # opponent's -7), everything else fixed. Diagnostic only; the forecast itself uses the unshifted margin.
    t2 = tt.copy()
    t2["exp_margin"] = t2["exp_margin"] + SCRIPT_MARGIN_SHIFT
    d2 = model.intermediates(te, t2)
    m0, m2 = model.means(d), model.means(d2)
    sens = pd.DataFrame({"player_id": te["player_id"], "game_id": te["game_id"]})
    for stat in M.STATS:
        sens[stat] = m2[stat] - m0[stat]
    team = model.team_predict(tt).merge(tt[["team", "game_id", "opponent"]], on=["team", "game_id"])
    opp = team[["team", "game_id", "vol_pts", "vol_pa", "vol_ra"]].rename(
        columns={"team": "opponent", "vol_pts": "opp_vol_pts", "vol_pa": "opp_vol_pa", "vol_ra": "opp_vol_ra"})
    team = team.merge(opp, on=["opponent", "game_id"], how="left")
    return {"arms": out, "intermediates": d, "script": sens, "team": team}


def _long(d: pd.DataFrame, store: dict, means: dict, lineage: dict) -> pd.DataFrame:
    parts = []
    for stat in M.STATS:
        f = M.forecast(store, d, means, stat)
        if not len(f):
            continue
        sub = d.loc[f.index, ["game_id", "player_id", "season", "week", "team", "opponent_team", "position", "pgroup", "kickoff", "src_max"]].copy()
        sub["statistic"] = stat
        sub = pd.concat([sub, f], axis=1)
        sub["model_inputs"] = [dict(zip(lineage[stat], v)) for v in d.loc[f.index, lineage[stat]].to_numpy(float).tolist()]
        parts.append(sub)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
