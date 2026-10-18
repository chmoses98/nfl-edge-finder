"""Final results for the archived forecasts (stage `results`).

Source: the nflverse releases the study already uses - `stats_player_week_<season>` (nightly), `stats_team_week_<season>`,
`snap_counts_<season>` and the schedule scores. A game's results are written only when it is FINAL in the data
(schedule score present AND player stats present AND snap counts present for it; snap counts are what distinguish a
zero-stat participant from a DNP/inactive, which props void). Never from in-progress games. If snap counts are still missing
4 days after the game, results are written from the stats table alone and flagged `participation_basis: stats_only`.

Participation convention = the study's: a player-game exists iff the player has a stat line (QB/RB/WR/TE row) or took >= 1
offensive snap. An archived player forecast with no such row for a final game is `participated: False` (void).

Idempotent: an outcome is archived only if it is new or its actual/participated differs from the latest archived one
(a stat correction then becomes ONE correction record in `settle`, original untouched).
"""
from __future__ import annotations

import os
from datetime import timedelta

import numpy as np
import pandas as pd

from pf_core import availability as av
from pf_core import prospective as pr

from nfl import data as D
from nfl.live import SPORT

PLAYER_COL = {"targets": "targets", "receptions": "receptions", "receiving_yards": "receiving_yards", "carries": "carries",
              "rushing_yards": "rushing_yards", "passing_attempts": "attempts", "completions": "completions",
              "passing_yards": "passing_yards", "passing_tds": "passing_tds"}
TEAM_FAMILIES = ("team_pass_attempts", "team_rush_attempts", "team_points")
STATS_ONLY_AFTER = timedelta(days=4)


def _read(release: str, fn: str, base: str | None = None, columns=None) -> pd.DataFrame | None:
    p = os.path.join(base or D.RAW, release, fn)
    return pd.read_parquet(p, columns=columns) if os.path.exists(p) else None


def _crosswalk_pfr(base: str | None = None) -> dict:
    p = os.path.join(base or os.path.join(D.ROOT, "data", "silver"), "player_crosswalk.parquet")
    if not os.path.exists(p):
        return {}
    cw = pd.read_parquet(p, columns=["gsis_id", "pfr_id"]).dropna().drop_duplicates("pfr_id")
    return dict(zip(cw.pfr_id, cw.gsis_id))


def game_results(game_id: str, season: int, sched_row, now_utc: str, raw_base: str | None = None, silver_base: str | None = None) -> dict:
    """Everything needed to settle one game: {"final": bool, "reason": ..., "players": {gsis: row}, "team": {team: {...}}}."""
    out: dict = {"final": False, "reason": None, "players": {}, "team": {}, "basis": "stats+snaps"}
    if pd.isna(sched_row.home_score) or pd.isna(sched_row.away_score):
        out["reason"] = "schedule has no final score yet"
        return out
    st = _read("stats_player", f"stats_player_week_{season}.parquet", raw_base)
    tm = _read("stats_team", f"stats_team_week_{season}.parquet", raw_base)
    sn = _read("snap_counts", f"snap_counts_{season}.parquet", raw_base)
    if st is None or tm is None:
        out["reason"] = "stats files missing"
        return out
    sp = st[(st.game_id == game_id) & st.position.isin(D.SKILL)]
    tp = tm[tm.game_id == game_id]
    if len(sp) < 10 or len(tp) < 2:
        out["reason"] = "player/team stats for the game are not in the nflverse release yet"
        return out
    snaps = None
    if sn is not None:
        sg = sn[sn.game_id == game_id]
        if len(sg) >= 20:
            pfr = _crosswalk_pfr(silver_base)
            sg = sg.assign(gsis=sg.pfr_player_id.map(pfr))
            snaps = sg[(sg.offense_snaps > 0) & sg.gsis.notna() & sg.position.isin(D.SKILL)]
    if snaps is None:
        ko = av._ts(pd.Timestamp(sched_row.kickoff_utc).isoformat())
        if av._ts(now_utc) - ko < STATS_ONLY_AFTER:
            out["reason"] = "snap counts for the game are not in the nflverse release yet"
            return out
        out["basis"] = "stats_only"
    rows = {}
    for _, r in sp.iterrows():
        d = {c: float(r[c]) if pd.notna(r[c]) else 0.0 for c in PLAYER_COL.values()}
        d["any_td"] = float((float(r.rushing_tds or 0) + float(r.receiving_tds or 0)) >= 1)
        d["_row"] = True
        rows[r.player_id] = d
    if snaps is not None:
        for g in set(snaps.gsis) - set(rows):
            d = {c: 0.0 for c in PLAYER_COL.values()}
            d.update(any_td=0.0, _row=False)
            rows[g] = d
    out["players"] = rows
    pts = {D.TEAM_FIX.get(sched_row.home_team, sched_row.home_team): float(sched_row.home_score),
           D.TEAM_FIX.get(sched_row.away_team, sched_row.away_team): float(sched_row.away_score)}
    for _, r in tp.iterrows():
        t = D.TEAM_FIX.get(r.team, r.team)
        out["team"][t] = {"team_pass_attempts": float(r.attempts), "team_rush_attempts": float(r.carries), "team_points": pts.get(t)}
    out["final"] = True
    return out


def build_outcomes(archive: str, now_utc: str, sched: pd.DataFrame, lookback_days: int = 21, raw_base: str | None = None,
                   silver_base: str | None = None) -> tuple[list[dict], dict]:
    """Outcome rows for every archived forecast key whose game is final and whose result is new or changed."""
    f = pr.load_forecasts(archive, SPORT)
    stats = {"games_with_forecasts": 0, "games_final": 0, "games_pending": {}, "outcomes_new_or_changed": 0, "outcomes_unchanged": 0}
    if f.empty:
        return [], stats
    now = av._ts(now_utc)
    f["_start"] = pd.to_datetime(f["game_start_utc"], utc=True)
    f = f[(f._start < pd.Timestamp(now) - pd.Timedelta(hours=2)) & (f._start > pd.Timestamp(now) - pd.Timedelta(days=lookback_days))]
    keys = f.drop_duplicates(["game_id", "entity_id", "family"])[["game_id", "entity_id", "family", "game_start_utc", "model_role"]]
    stats["games_with_forecasts"] = int(keys.game_id.nunique())
    prior = pd.DataFrame(pr._read(archive, "outcomes", SPORT))
    last = {}
    if not prior.empty:
        prior = prior.sort_values("observed_utc").groupby(["game_id", "entity_id", "family"], as_index=False).tail(1)
        last = {(r.game_id, r.entity_id, r.family): (float(r.actual), bool(r.participated)) for r in prior.itertuples()}
    srow = sched.set_index("game_id")
    rows = []
    for gid, kk in keys.groupby("game_id"):
        if gid not in srow.index:
            stats["games_pending"][gid] = "game not in schedule"
            continue
        s = srow.loc[gid]
        res = game_results(gid, int(s.season), s, now_utc, raw_base, silver_base)
        if not res["final"]:
            stats["games_pending"][gid] = res["reason"]
            continue
        stats["games_final"] += 1
        date = av._ts(kk.game_start_utc.iloc[0]).strftime("%Y-%m-%d")
        for _, k in kk.iterrows():
            fam = k.family
            if fam in TEAM_FAMILIES:
                tv = res["team"].get(k.entity_id)
                if tv is None or tv.get(fam) is None:
                    continue
                actual, part = tv[fam], True
            else:
                pr_ = res["players"].get(k.entity_id)
                part = pr_ is not None
                if fam == "anytime_td":
                    actual = pr_["any_td"] if part else 0.0
                else:
                    actual = pr_[PLAYER_COL[fam]] if part else 0.0
            key = (gid, k.entity_id, fam)
            if last.get(key) == (float(actual), bool(part)):
                stats["outcomes_unchanged"] += 1
                continue
            rows.append({"game_id": gid, "entity_id": k.entity_id, "family": fam, "actual": float(actual), "participated": bool(part),
                         "final": True, "source": f"nflverse stats_player/stats_team/snap_counts ({res['basis']})", "game_date": date,
                         "participation_basis": res["basis"]})
            stats["outcomes_new_or_changed"] += 1
    return rows, stats
