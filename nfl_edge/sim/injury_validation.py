"""INJURY / AVAILABILITY REDISTRIBUTION validation on the five-season walk-forward. RESEARCH_ONLY; no arm.

Historical availability is the FINAL pregame injury designation in the nflverse report for that week -- the only
historical artifact (a documented limitation: prospective runs read the content-addressed vintage at the cutoff,
``prospective.injury_vintage``). Populations (preregistration section 9):

  TEAMMATE_OF_OUT_STARTER   players whose team's depth-chart-1 RB / WR / TE was designated Out / Doubtful (as registered)
  TEAMMATE_OF_UNAVAILABLE_STARTER  POST-HOC broadening: the depth-chart-1 RB / WR / TE was unavailable for ANY reason
                            (designation, game-day inactive, off the active roster). Added because the historical
                            eligible set is the game-day active list, so most absences carry no designation.
  QUESTIONABLE              the questionable players themselves
  MULTIPLE_OUT              players on team-games with two or more depth-chart 1-2 RB / WR / TE unavailable
  NEW_STARTER_NO_HISTORY    depth-chart-1 players with no prior game in the history
  QB_STARTER_ERROR          every player of a team-game whose simulated QB1 did not throw the most passes
  REST                      everything else

Scored on carries and targets (the opportunity the simulator redistributes), on ``backtest.evaluate``'s scored
rows: bias, CRPS, 50% / 90% coverage and the PIT histogram.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from . import baseline_report as BR
from . import training as T

POPULATIONS = ("TEAMMATE_OF_OUT_STARTER", "TEAMMATE_OF_UNAVAILABLE_STARTER", "QUESTIONABLE", "MULTIPLE_OUT", "NEW_STARTER_NO_HISTORY", "QB_STARTER_ERROR")
STATS = ("carries", "targets")


def _unavailable_starters(season: int, eligible: pd.DataFrame) -> pd.DataFrame:
    """Depth-chart RB/WR/TE ranks 1-2 for each team-game who are NOT in the eligible set, with the reason:
    an Out/Doubtful designation, a game-day inactive (INA) with no designation, or another roster status."""
    from . import data as D, features as F
    sched = D.schedule().to_pandas()
    g = sched[(sched["season"] == season) & sched["home_score"].notna()]
    elig = set(zip(eligible["game_id"], eligible["player_id"]))
    rows = []
    daily = season >= 2025
    for week in sorted(g["week"].unique()):
        gw = g[g["week"] == week]
        if daily:
            depth = F.depth_chart(season, cutoff=pd.Timestamp(gw["gameday"].min()).tz_localize("UTC").to_pydatetime())
        else:
            depth = F.depth_chart(season, week=int(week))
        inj = F.injury_designations(season, int(week)); des = dict(zip(inj["player_id"], inj["report_status"]))
        ros = F.weekly_roster(season, int(week)); stat = dict(zip(ros["player_id"], ros["status"]))
        dc = depth[depth["dc_pos"].isin(["RB", "WR", "TE"]) & (depth["dc_rank"] <= 2)]
        for r in gw.itertuples():
            for team in (r.home_team, r.away_team):
                for d in dc[dc["team"] == team].itertuples():
                    if (r.game_id, d.player_id) in elig:
                        continue
                    why = ("DESIGNATED_" + str(des[d.player_id]).upper()) if des.get(d.player_id) in ("Out", "Doubtful") else \
                          ("GAME_DAY_INACTIVE" if stat.get(d.player_id) == "INA" else f"ROSTER_{stat.get(d.player_id, 'ABSENT')}")
                    rows.append({"game_id": r.game_id, "team": team, "player_id": d.player_id, "dc_rank": int(d.dc_rank),
                                 "position": d.dc_pos, "reason": why})
    return pd.DataFrame(rows, columns=["game_id", "team", "player_id", "dc_rank", "position", "reason"])


def populations(season: int, out_dir: str) -> tuple[pd.DataFrame, dict]:
    """(game_id, team, player_id) -> population flags for the season's eligible players, and reason counts."""
    el = pd.read_parquet(os.path.join(out_dir, f"eligible_{season}.parquet"))
    un = _unavailable_starters(season, el)
    s1 = un[un["dc_rank"] == 1]
    starter_out_tg = set(zip(s1["game_id"], s1["team"]))
    d1 = s1[s1["reason"].str.startswith("DESIGNATED_")]
    designated_tg = set(zip(d1["game_id"], d1["team"]))
    n_un = un.groupby(["game_id", "team"]).size()
    multi_tg = set(n_un[n_un >= 2].index)
    wf = json.load(open(os.path.join(out_dir, f"wf_{season}.json")))
    qb_err_tg = {(m["game_id"], m["team"]) for m in wf["qb_identification"]["misses"]}
    tg = list(zip(el["game_id"], el["team"]))
    flags = pd.DataFrame({"game_id": el["game_id"], "team": el["team"], "player_id": el["player_id"],
                          "TEAMMATE_OF_OUT_STARTER": [x in designated_tg for x in tg],
                          "TEAMMATE_OF_UNAVAILABLE_STARTER": [x in starter_out_tg for x in tg],
                          "QUESTIONABLE": (el["avail_state"] == "QUESTIONABLE").to_numpy(),
                          "MULTIPLE_OUT": [x in multi_tg for x in tg],
                          "NEW_STARTER_NO_HISTORY": ((el["dc_rank"] == 1) & (el["n_prior"].fillna(0) == 0)).to_numpy(),
                          "QB_STARTER_ERROR": [x in qb_err_tg for x in tg]})
    flags["REST"] = ~flags[list(POPULATIONS)].any(axis=1)
    reasons = {"dc1_unavailable_by_reason": {k: int(v) for k, v in s1["reason"].value_counts().items()},
               "dc1_or_dc2_unavailable_by_reason": {k: int(v) for k, v in un["reason"].value_counts().items()},
               "team_games_with_dc1_unavailable": len(starter_out_tg), "team_games_with_2plus_unavailable": len(multi_tg)}
    return flags, reasons


def _block(g: pd.DataFrame) -> dict:
    if g.empty:
        return {"n": 0}
    return {"n": int(len(g)), "n_games": int(g["game_id"].nunique()), "bias": float(g["err"].mean()), "mae": float(g["ae"].mean()),
            "crps": float(g["crps"].mean()), "cover50": float(g["in50"].mean()), "cover90": float(g["in90"].mean()),
            "pit_hist": np.histogram(g["pit"], bins=10, range=(0, 1))[0].tolist()}


def run(out_dir: str, seasons) -> dict:
    res = {"by_season": {}, "pooled": {}}
    pooled = {st: [] for st in STATS}
    for y in seasons:
        P = pd.read_parquet(os.path.join(out_dir, f"player_dists_{y}.parquet"))
        fl, reasons = populations(y, out_dir)
        res["by_season"][str(y)] = {"unavailability": reasons}
        for st in STATS:
            g = BR.scored_rows(P, st).merge(fl, on=["game_id", "team", "player_id"], how="left")
            for c in list(POPULATIONS) + ["REST"]:
                g[c] = g[c].fillna(False).astype(bool)
            res["by_season"][str(y)][st] = {c: _block(g[g[c]]) for c in list(POPULATIONS) + ["REST"]}
            pooled[st].append(g)
    for st in STATS:
        g = pd.concat(pooled[st], ignore_index=True)
        res["pooled"][st] = {}
        for c in list(POPULATIONS) + ["REST"]:
            sub = g[g[c]]
            b = _block(sub)
            if len(sub) and c != "REST":
                ci = BR._clustered(sub, ["in90", "in50", "err"])
                b["ci"] = ci
            res["pooled"][st][c] = b
    res["note"] = ("historical designations are the final pregame report (the only historical artifact); a player can sit in "
                   "several populations at once; populations are descriptive and select on pregame information only")
    return res
