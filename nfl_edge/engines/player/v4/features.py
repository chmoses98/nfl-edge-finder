"""V4 point-in-time features: pregame availability of the player AND his teammates, and the opportunity they vacate.

v3 knows a player's own history. It does not know that the receiver who took 28% of the targets last week is
listed Out this week, or that the back who missed three games is back -- `role_change_pending` flags the first as
text and nothing models it. V4 adds, for every (player, game), from strictly pregame information:

    own status          this week's injury-report designation (OUT / DOUBTFUL / QUESTIONABLE / none) and whether the
                        weekly roster lists him as active. Inactive-on-gameday (roster status INA) is NOT used: it is
                        known 90 minutes before kickoff, and the model must mean the same thing at T-24h.
    teammate pool       every player who played for the team in its last POOL_GAMES games (strictly prior), with his
                        recent role = mean target / carry / snap share over his last three games for the team.
    vacated             the recent role of pool members ruled out for THIS game (report OUT / DOUBTFUL, or a weekly
                        roster status that is not an active roster spot) whose most recent game was the team's most
                        recent game -- a NEW absence. A long absence is already inside everyone's recent shares.
                        Split by position group (same group as the player / other groups) and in-season vs. offseason
                        departures (week 1, a player who left in the offseason).
    returning           the recent role of pool members who are available again after missing the team's last game(s).
    self fraction       the player's own recent role over the total recent role of the AVAILABLE members of his group:
                        who absorbs a vacated share is learned from this, pooled across every team (a hierarchical
                        prior), never fitted team by team.

A player with no history for the team is `self_new` -- never a zero-usage player. Unknown statuses are UNKNOWN,
never "healthy": `status_known` is carried so the model and the abstention layer can tell them apart.
"""
from __future__ import annotations

import os
from collections import defaultdict, deque

import numpy as np
import pandas as pd

POOL_GAMES = 4
GROUP = {"QB": "QB", "RB": "RB", "FB": "RB", "HB": "RB", "WR": "WR", "TE": "TE"}
GROUPS = ("QB", "RB", "WR", "TE")
SHARES = ("target_share", "carry_share", "snap_share")
SHORT = {"target_share": "t", "carry_share": "c", "snap_share": "s"}
# weekly-roster statuses that are not an active 53-man roster spot at the snapshot (INA is a gameday decision and
# is deliberately excluded -- see the module docstring)
ROSTER_OUT = {"RES", "CUT", "RET", "TRD", "EXE", "SUS", "NON", "PUP", "TRC", "E01", "DEV"}
REPORT_OUT = {"OUT", "DOUBTFUL"}

V4_ABSENCE_COLS = (
    ["own_q", "own_d", "own_out", "status_known", "self_new", "self_returning", "n_active_same", "in_pool"]
    + [f"{k}_{s}" for s in ("t", "c", "s") for k in ("vac_same", "vac_other", "vac_off_same", "ret_same", "self_frac", "self_role")]
)
V4_RECENCY_COLS = ["max4_snap_share", "cur_mean_snap_share", "cur_mean_target_share", "cur_mean_carry_share", "games_since_last"]


def group_of(pos) -> str:
    return GROUP.get(str(pos), "OTHER")


# --------------------------------------------------------------------------------------------- pregame status
def status_frame(root: str, seasons) -> pd.DataFrame:
    """(season, week, team, player_id) -> report status (upper case or None) and roster status, from nflverse.

    Report: injuries_<season>.parquet `report_status` for the week (the final pregame report). Roster:
    roster_weekly_<season>.parquet `status`. `roster_known` says whether the team-week has any roster row at all,
    so "not on the roster" is only asserted where the roster exists."""
    inj, ros = [], []
    for s in seasons:
        p = os.path.join(root, "data/raw/nflverse/injuries", f"injuries_{s}.parquet")
        if os.path.exists(p):
            d = pd.read_parquet(p, columns=["season", "week", "team", "gsis_id", "report_status", "game_type"])
            d = d[d.game_type == "REG"]
            inj.append(d)
        p = os.path.join(root, "data/raw/nflverse/weekly_rosters", f"roster_weekly_{s}.parquet")
        if os.path.exists(p):
            d = pd.read_parquet(p, columns=["season", "week", "team", "gsis_id", "status", "game_type"])
            d = d[d.game_type == "REG"]
            ros.append(d)
    cols = ["season", "week", "team", "player_id"]
    i = (pd.concat(inj, ignore_index=True) if inj else pd.DataFrame(columns=["season", "week", "team", "gsis_id", "report_status"]))
    i = i.rename(columns={"gsis_id": "player_id"})
    i["report"] = i["report_status"].astype("string").str.upper()
    i = i.dropna(subset=["player_id"]).drop_duplicates(cols, keep="last")[cols + ["report"]]
    r = (pd.concat(ros, ignore_index=True) if ros else pd.DataFrame(columns=["season", "week", "team", "gsis_id", "status"]))
    r = r.rename(columns={"gsis_id": "player_id", "status": "roster"}).dropna(subset=["player_id"])
    r = r.drop_duplicates(cols, keep="last")[cols + ["roster"]]
    out = r.merge(i, on=cols, how="outer")
    for c in ("season", "week"):
        out[c] = out[c].astype(int)
    return out


class StatusBook:
    """Lookup of a player's pregame status for a team-week, with an explicit UNKNOWN."""

    def __init__(self, frame: pd.DataFrame | None, overrides: dict | None = None, override_weeks=None):
        self.report, self.roster, self.roster_teams, self.report_teams = {}, {}, set(), set()
        if frame is not None and len(frame):
            for s, w, t, p, rep, ros in frame[["season", "week", "team", "player_id", "report", "roster"]].itertuples(index=False):
                k = (int(s), int(w), t, p)
                if isinstance(rep, str) and rep:
                    self.report[k] = rep
                    self.report_teams.add((int(s), int(w), t))
                if isinstance(ros, str) and ros:
                    self.roster[k] = ros
                    self.roster_teams.add((int(s), int(w), t))
        # production overlay: (season, week, player) -> "OUT" / "DOUBTFUL" / "QUESTIONABLE" / "ACTIVE", from the
        # point-in-time injury-report vintage and the availability captures of the run (see project_slate_v2)
        self.overrides = dict(overrides or {})
        self.override_weeks = {(k[0], k[1]) for k in self.overrides} | {(int(a), int(b)) for a, b in (override_weeks or ())}

    def get(self, season, week, team, pid) -> dict:
        k = (int(season), int(week), team, pid)
        ov = self.overrides.get((k[0], k[1], pid))
        # a week the run overlays is read ONLY from the overlay (its point-in-time vintage), never from the file
        rep = ov if (k[0], k[1]) in self.override_weeks else self.report.get(k)
        rep = None if rep == "ACTIVE" else rep
        ros = self.roster.get(k)
        roster_known = (k[0], k[1], team) in self.roster_teams
        report_known = (k[0], k[1], team) in self.report_teams or (k[0], k[1]) in self.override_weeks
        ruled_out = (rep in REPORT_OUT) or (ros in ROSTER_OUT) or (roster_known and ros is None)
        return {"report": rep, "roster": ros, "ruled_out": bool(ruled_out), "questionable": rep == "QUESTIONABLE",
                "doubtful": rep == "DOUBTFUL", "out": rep == "OUT" or (ros in ROSTER_OUT),
                "known": bool(roster_known or report_known)}


# --------------------------------------------------------------------------------------------- absence features
def _played(row_vals) -> bool:
    return any(np.isfinite(v) for v in row_vals)


def add_absence_features(df: pd.DataFrame, status: StatusBook, pool_games: int = POOL_GAMES) -> pd.DataFrame:
    """Requires realised `target_share`, `carry_share`, `snap_share` (NaN on prospective rows) and team/season/week.

    Processes each team's games in chronological order; a row's features use only the team's strictly prior games
    plus this week's pregame statuses. Prospective rows (NaN shares) never enter the pool."""
    df = df.copy()
    out = {c: np.full(len(df), np.nan) for c in V4_ABSENCE_COLS}
    pos_arr = df["position"].map(group_of).to_numpy()
    pid_arr = df["player_id"].to_numpy()
    sh = df[list(SHARES)].to_numpy(float)
    order = df.sort_values(["team", "season", "week"], kind="mergesort")
    for team, tg in order.groupby("team", sort=False):
        pool = {}      # pid -> {"last": seq, "season": s, "group": g, "hist": deque of share triples}
        games = tg.groupby(["season", "week", "game_id"], sort=True).indices
        keys = sorted(games, key=lambda k: (k[0], k[1]))
        for seq, key in enumerate(keys):
            season, week, gid = key
            idx = tg.index.to_numpy()[games[key]]
            new_abs = defaultdict(lambda: np.zeros(3)); off_abs = defaultdict(lambda: np.zeros(3))
            active = defaultdict(lambda: np.zeros(3)); returning = defaultdict(lambda: np.zeros(3))
            n_active = defaultdict(int)
            member_state = {}
            for m, info in pool.items():
                if info["last"] < seq - pool_games:
                    continue
                r = np.nanmean(np.array(info["hist"]), axis=0)
                r = np.nan_to_num(r, nan=0.0)
                st = status.get(season, week, team, m)
                g = info["group"]
                if st["ruled_out"]:
                    if info["last"] == seq - 1:
                        (new_abs if info["season"] == season else off_abs)[g] += r
                    member_state[m] = ("out", r)
                else:
                    active[g] += r; n_active[g] += 1
                    if info["last"] < seq - 1:
                        returning[g] += r
                        member_state[m] = ("ret", r)
                    else:
                        member_state[m] = ("act", r)
            for i in idx:
                p = pid_arr[i]; g = pos_arr[i]
                st = status.get(season, week, team, p)
                ms = member_state.get(p)
                r_self = ms[1] if ms else np.zeros(3)
                in_act = bool(ms and ms[0] in ("act", "ret"))
                denom = active[g] + (0 if in_act else r_self)
                vac_same = new_abs[g] - (r_self if (ms and ms[0] == "out" and pool[p]["last"] == seq - 1 and pool[p]["season"] == season) else 0)
                off_same = off_abs[g] - (r_self if (ms and ms[0] == "out" and pool[p]["last"] == seq - 1 and pool[p]["season"] != season) else 0)
                vac_other = sum((v for gg, v in new_abs.items() if gg != g), np.zeros(3))
                ret_same = returning[g] - (r_self if (ms and ms[0] == "ret") else 0)
                with np.errstate(invalid="ignore", divide="ignore"):
                    frac = np.where(denom > 1e-9, r_self / np.where(denom > 1e-9, denom, 1), 0.0)
                out["own_q"][i] = float(st["questionable"]); out["own_d"][i] = float(st["doubtful"])
                out["own_out"][i] = float(st["out"]); out["status_known"][i] = float(st["known"])
                out["self_new"][i] = float(ms is None)
                out["in_pool"][i] = float(ms is not None)
                out["self_returning"][i] = float(bool(ms) and pool[p]["last"] < seq - 1)
                out["n_active_same"][i] = n_active[g] + (0 if in_act else 1)
                for j, s in enumerate(("t", "c", "s")):
                    out[f"vac_same_{s}"][i] = max(0.0, vac_same[j]); out[f"vac_other_{s}"][i] = max(0.0, vac_other[j])
                    out[f"vac_off_same_{s}"][i] = max(0.0, off_same[j]); out[f"ret_same_{s}"][i] = max(0.0, ret_same[j])
                    out[f"self_frac_{s}"][i] = frac[j]; out[f"self_role_{s}"][i] = r_self[j]
            # update the pool with this game's realised usage (prospective rows have NaN shares and are skipped)
            for i in idx:
                v = sh[i]
                if not _played(v):
                    continue
                p = pid_arr[i]
                info = pool.get(p)
                if info is None:
                    info = pool[p] = {"hist": deque(maxlen=3), "group": pos_arr[i]}
                info["last"] = seq; info["season"] = season
                info["hist"].append(np.nan_to_num(v, nan=0.0))
    for c, v in out.items():
        df[c] = v
    return df


def add_recency_features(df: pd.DataFrame) -> pd.DataFrame:
    """max snap share over the last four games (the healthy-role proxy), current-season means, team-games since the
    player's previous game. All from strictly prior rows of the player."""
    df = df.copy()
    order = df.sort_values(["player_id", "season", "week"], kind="mergesort").index
    d = df.loc[order]
    g = d.groupby("player_id", sort=False)
    d["max4_snap_share"] = g["snap_share"].transform(lambda s: s.shift(1).rolling(4, min_periods=1).max())
    gs = d.groupby(["player_id", "season"], sort=False)
    for c in ("snap_share", "target_share", "carry_share"):
        d[f"cur_mean_{c}"] = gs[c].transform(lambda s: s.shift(1).expanding().mean())
    prev_week = g["week"].shift(1); prev_season = g["season"].shift(1)
    d["games_since_last"] = np.where(prev_season == d["season"], d["week"] - prev_week, np.nan)
    df = d.reindex(df.index)
    # no current-season history -> fall back to the EWMA, never to zero
    for c in ("snap_share", "target_share", "carry_share"):
        df[f"cur_mean_{c}"] = df[f"cur_mean_{c}"].where(df[f"cur_mean_{c}"].notna(), df[f"ewma_{c}"])
    df["max4_snap_share"] = df["max4_snap_share"].where(df["max4_snap_share"].notna(), df["ewma_snap_share"])
    return df
