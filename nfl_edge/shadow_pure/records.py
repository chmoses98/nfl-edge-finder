"""pure_forecast.v1 rows for the PURE arms, with the football-only lineage the W2 spec asks for.

Every row carries, as feature_lineage entries (each with its source and observed_at):
    model inputs            the frozen arm's own lineage (e.g. vol_pa, share_t, e_targets for targets)
    expected workload       predicted snap share, targets / carries / pass-attempt opportunity, team plays
    opponent adjustment     the opponent's prior-only allowed rates (pass / rush volume, completion, yards per
                            target / carry / attempt, pass rate, points)
    game environment        football-only team pass / rush attempts, plays, points, opponent points, expected
                            margin and points, pass rate, home, fixed dome venue, rest days, recent QB change
    script sensitivity      change in the forecast mean for +7 points of football-only expected margin (the model
                            has no game-script state; this is the derivative of its environment inputs)
    assumed starter         whether this player is the team's assumed starting QB and where that came from
Timestamps: a feature computed from box scores is observed at (latest game it used) kickoff + 4 h; a schedule fact
(home, venue, kickoff, assumed starter) at the schedule file's fetched_at. Sources' max_observed_at is the
fetched_at of the files; source_max_observed_at is the latest of those, and is < as_of.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nfl_edge.shadow_pure import SPORT

S_STATS, S_SNAPS, S_SCHED = "nflverse_stats_player_week", "nflverse_snap_counts", "nflverse_schedule_nonmarket_columns"
S_PLAYERS = "nflverse_players_crosswalk"

# intermediates column -> (lineage name, source, timestamp kind: player | team | schedule)
WORKLOAD = [("snap_mean", "exp_snap_share", S_SNAPS, "player"), ("mu_targets", "exp_targets", S_STATS, "player"),
            ("mu_carries", "exp_carries", S_STATS, "player"), ("mu_attempts", "exp_pass_attempts_if_starter", S_STATS, "player"),
            ("share_t", "exp_target_share", S_STATS, "player"), ("share_c", "exp_carry_share", S_STATS, "player")]
OPPONENT = [("o_pa_allowed", "opp_pass_att_allowed", S_STATS), ("o_ra_allowed", "opp_rush_att_allowed", S_STATS),
            ("o_plays_allowed", "opp_plays_allowed", S_STATS), ("o_pts_allowed", "opp_points_allowed", S_SCHED),
            ("o_rate_allowed", "opp_pass_rate_allowed", S_STATS), ("o_cmp_allowed", "opp_completion_rate_allowed", S_STATS),
            ("o_ypt_allowed", "opp_yards_per_target_allowed", S_STATS), ("o_ypc_allowed", "opp_yards_per_carry_allowed", S_STATS),
            ("o_ypa_allowed", "opp_yards_per_pass_att_allowed", S_STATS)]
TEAM_ENV = [("exp_margin", "env_exp_margin", S_SCHED), ("exp_points", "env_exp_points", S_SCHED),
            ("f_rate", "env_team_pass_rate", S_STATS), ("rest_days", "env_rest_days", S_SCHED),
            ("qb_changed_recent", "env_qb_changed_recent", S_STATS)]


def iso(ts) -> str:
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _num(v):
    if v is None:
        return None
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    try:
        f = float(v)
    except (TypeError, ValueError):
        return v
    return round(f, 5) if np.isfinite(f) else None


def build_rows(long: pd.DataFrame, inter: pd.DataFrame, team: pd.DataFrame, script: pd.DataFrame, t: pd.DataFrame, *,
               model_version: str, frozen_hash: str, as_of, sources: dict, schedule_fetched_at, capture_kind: str,
               run_id: str, starter_source: dict) -> list[dict]:
    """long: one arm's forecasts (prospective._long). inter: intermediates of the same rows."""
    key = ["game_id", "player_id"]
    it = inter.drop_duplicates(key).set_index(key)
    tm = team.set_index(["team", "game_id"])
    tt = t.drop_duplicates(["team", "game_id"]).set_index(["team", "game_id"])
    sc = script.drop_duplicates(key).set_index(key)
    srcs = [{"source_id": sid, "class": "sports_only", "max_observed_at": iso(v["max_observed_at"]), "uri": v["uri"],
             "snapshot_sha256": v["snapshot_sha256"]} for sid, v in sorted(sources.items())]
    src_max = max(v["max_observed_at"] for v in sources.values())
    sched_ts = iso(schedule_fetched_at)
    out = []
    for r in long.itertuples(index=False):
        i = it.loc[(r.game_id, r.player_id)]
        tr = tt.loc[(r.team, r.game_id)]
        te = tm.loc[(r.team, r.game_id)]
        player_ts = iso(pd.Timestamp(i["player_prev_kickoff"]) + pd.Timedelta(hours=4)) if pd.notna(i["player_prev_kickoff"]) else None
        team_ts = iso(pd.Timestamp(i["team_src_max"]) + pd.Timedelta(hours=4)) if pd.notna(i["team_src_max"]) else None
        row_obs = iso(r.src_max) if pd.notna(r.src_max) else None

        def ts(kind):
            v = {"player": player_ts, "team": team_ts, "schedule": sched_ts}[kind]
            return v or row_obs or sched_ts
        lin = []
        for name, val in sorted(r.model_inputs.items()):
            lin.append((f"in_{name}", val, S_STATS, ts("player")))
        for col, name, src, kind in WORKLOAD:
            lin.append((name, i.get(col), src, ts(kind)))
        lin.append(("exp_team_plays", te["vol_plays"], S_STATS, ts("team")))
        for col, name, src in OPPONENT:
            lin.append((name, tr.get(col), src, ts("team")))
        for col, name in (("vol_pa", "env_team_pass_att"), ("vol_ra", "env_team_rush_att"), ("vol_pts", "env_team_points"),
                          ("opp_vol_pts", "env_opp_points"), ("opp_vol_pa", "env_opp_pass_att"), ("opp_vol_ra", "env_opp_rush_att")):
            lin.append((name, te.get(col), S_STATS if "pts" not in col else S_SCHED, ts("team")))
        for col, name, src in TEAM_ENV:
            lin.append((name, tr.get(col), src, ts("team")))
        lin.append(("env_home", bool(tr["home"]), S_SCHED, sched_ts))
        lin.append(("env_fixed_dome_venue", bool(tr["dome"]), S_SCHED, sched_ts))
        lin.append(("script_mean_delta_per_7pt_margin", sc.loc[(r.game_id, r.player_id)][r.statistic], S_STATS, ts("team")))
        lin.append(("assumed_starting_qb", bool(i["qb_starter"]), S_SCHED, sched_ts))
        lin.append(("assumed_starting_qb_basis", starter_source.get((r.game_id, r.player_id)) or "not_applicable", S_SCHED, sched_ts))
        lin.append(("player_prior_games", int(i["e_n"]), S_STATS, ts("player")))
        lin.append(("player_games_missed_recent", _num(i["games_missed"]), S_STATS, ts("player")))
        fl = [{"name": n, "value": _num(v), "source": s, "observed_at": o, "class": "sports_only"} for n, v, s, o in lin]
        proj = {"mean": round(float(r.mean), 4), "median": round(float(r.median), 4), "p10": round(float(r.p10), 4),
                "p90": round(float(r.p90), 4),
                "thresholds": [{"at_least": float(a), "probability": round(float(p), 5)} for a, p in r.thresholds]}
        out.append({"schema_version": "pure_forecast.v1", "sport": SPORT, "game_id": r.game_id, "player_id": r.player_id,
                    "statistic": r.statistic, "as_of": iso(as_of), "kickoff": iso(r.kickoff), "source_max_observed_at": iso(src_max),
                    "projection_mode": "PURE_INDEPENDENT", "model_version": model_version, "model_frozen_hash": frozen_hash,
                    "conditional_on_playing": True, "participation_probability": None, "projection": proj,
                    "sources": srcs, "feature_lineage": fl,
                    "x_capture": {"run_id": run_id, "capture_kind": capture_kind, "team": r.team, "opponent": r.opponent_team,
                                  "position": r.position, "position_group": r.pgroup, "season": int(r.season), "week": int(r.week),
                                  "conditional_on": "own participation (>=1 offensive snap or a box-score line)"
                                                    + ("; starting at QB" if r.statistic in ("passing_attempts", "completions", "passing_yards") else ""),
                                  "participation_probability_null_reason": "participation is not modelled by PURE_PLAYER_V1 (frozen); "
                                                                           "no point-in-time availability source is certified",
                                  "script_sensitivity_note": "PURE_PLAYER_V1 has no game-script state; value = forecast-mean change "
                                                             "for +7 points of football-only expected margin"}})
    return out
