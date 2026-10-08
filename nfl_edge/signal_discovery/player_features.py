"""Point-in-time player opportunity features for the prop study. RESEARCH ONLY; market-blind.

Architecture (GAME -> TEAM -> PLAYER):
  game_features.py  opponent-adjusted team ratings -> team-perspective context on every player-game row:
                    expected plays / pace, expected script (opponent-adjusted scoring baseline margin from the
                    team's view -- football only, never the spread), opponent pass / rush / explosive defence
                    quality, the team's own pressure / sack expectation and QB (dropback) efficiency.
  nfl_edge.sim.features  (reused unchanged) decayed player shares (target, carry, attempt, red-zone, snap) at
                    two half-lives, last-game shares, exposure-weighted per-touch rates shrunk to FROZEN
                    position priors fitted on 2012-2015 only, and the team's own volume EWMAs.

Everything on a row is computed from that subject's strictly earlier games (``decayed_prior_sums`` excludes
the row itself; the repository's test suite perturbs a row's outcome and asserts its features do not move).

ROLE_STABILITY (pre-registered, from pregame quantities only):
  INSUFFICIENT_ROLE_HISTORY  fewer than 3 prior appearances
  INJURY_DEPENDENT           the player is listed Questionable/Doubtful on the week's final injury report, or a
                             same-team same-position teammate with a larger long-window share is listed
                             Out/Doubtful (NEAR_PIT: the final weekly report, published before kickoff, is the
                             only historical vintage; 2025-26 rows carry no modification timestamp)
  ROLE_CHANGE                |short-window - long-window| primary share >= 0.10, or snap share >= 0.15
  STABLE_ROLE                otherwise
Rows exist only for players who appeared in the game (CONDITIONAL ON PLAYING; Kalshi settles an inactive player's
over NO -- the prop economics below are therefore conditional too, and say so).
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import polars as pl

from nfl_edge.sim import data as D
from nfl_edge.sim import features as F

PRIOR_SEASONS = (2012, 2013, 2014, 2015)
PLAYER_SEASONS = tuple(range(2016, 2027))
POSITIONS = ("QB", "RB", "WR", "TE")
OUTCOME_COLS = ("attempts", "completions", "pass_yards", "pass_td", "ints", "carries", "rush_yards", "receptions",
                "rec_yards", "targets", "offense_snaps", "rush_td", "rec_td")

CONTEXT_MAP = {
    # team-perspective name: (home source, away source)
    "ctx.team_plays": ("mx_home.plays", "mx_away.plays"),
    "ctx.env_plays": ("env.plays", "env.plays"),
    "ctx.team_neutral_pass_rate": ("mx_home.neutral_pass_rate", "mx_away.neutral_pass_rate"),
    "ctx.team_sec_per_play": ("mx_home.sec_per_play", "mx_away.sec_per_play"),
    "ctx.team_points": ("mx_home.points", "mx_away.points"),
    "ctx.opp_points": ("mx_away.points", "mx_home.points"),
    "ctx.team_dropback_epa": ("mx_home.dropback_epa", "mx_away.dropback_epa"),
    "ctx.team_rush_epa": ("mx_home.designed_rush_epa", "mx_away.designed_rush_epa"),
    "ctx.team_sack_rate": ("mx_home.sack_rate", "mx_away.sack_rate"),
    "ctx.team_pressure_rate": ("mx_home.pressure_rate", "mx_away.pressure_rate"),
    "ctx.team_explosive_pass": ("mx_home.explosive_pass_rate", "mx_away.explosive_pass_rate"),
    "ctx.team_explosive_rush": ("mx_home.explosive_rush_rate", "mx_away.explosive_rush_rate"),
    "ctx.opp_pass_def_q": ("q_away_def.dropback_epa", "q_home_def.dropback_epa"),
    "ctx.opp_rush_def_q": ("q_away_def.designed_rush_epa", "q_home_def.designed_rush_epa"),
    "ctx.opp_expl_pass_def_q": ("q_away_def.explosive_pass_rate", "q_home_def.explosive_pass_rate"),
    "ctx.opp_pass_rush_q": ("q_away_def.sack_rate", "q_home_def.sack_rate"),
    "ctx.team_protection_q": ("q_home_off.sack_rate", "q_away_off.sack_rate"),
    "ctx.team_qb_q": ("q_home_off.dropback_epa", "q_away_off.dropback_epa"),
}


def _injuries(season: int) -> pd.DataFrame:
    p = os.path.join(D.RAW, "injuries", f"injuries_{season}.parquet")
    if not os.path.exists(p):
        return pd.DataFrame(columns=["season", "week", "gsis_id", "report_status"])
    i = pl.read_parquet(p, columns=["season", "week", "gsis_id", "team", "report_status"]).filter(pl.col("gsis_id").is_not_null())
    return pd.DataFrame(i.to_dicts())


def build(game_features: pd.DataFrame) -> pd.DataFrame:
    priors_t = pd.DataFrame(D.load("team_games", PRIOR_SEASONS).to_dicts())
    priors_p = pd.DataFrame(D.load("player_games", PRIOR_SEASONS).to_dicts())
    priors = F.fit_priors(priors_t, priors_p, fit_seasons=PRIOR_SEASONS)
    seasons = list(PRIOR_SEASONS) + list(PLAYER_SEASONS)  # history needed for decayed sums
    tg = pd.DataFrame(D.load("team_games", seasons).to_dicts())
    pg = pd.DataFrame(D.load("player_games", seasons).to_dicts())
    tf = F.team_features(tg, F.FEATURE_CONFIG, priors)
    pf = F.player_features(pg, tg, F.FEATURE_CONFIG, priors=priors)
    pf = pf[pf["season"].isin(PLAYER_SEASONS) & pf["position"].isin(POSITIONS) & (pf["season_type"] == "REG")].copy()
    team_cols = ["game_id", "team"] + [c for c in tf.columns if c.startswith(("off_", "def_")) and not c.startswith("off_td")]
    pf = pf.merge(tf[team_cols].drop_duplicates(["game_id", "team"]), on=["game_id", "team"], how="left")
    # team-perspective game context (market-blind)
    gf = game_features.set_index("game_id")
    ctx = {k: [] for k in CONTEXT_MAP}
    script, home_flag = [], []
    for gid, team in zip(pf["game_id"], pf["team"], strict=False):
        if gid not in gf.index:
            for k in CONTEXT_MAP:
                ctx[k].append(np.nan)
            script.append(np.nan)
            home_flag.append(np.nan)
            continue
        g = gf.loc[gid]
        is_home = g["home_team"] == team
        home_flag.append(bool(is_home))
        for k, (hs, as_) in CONTEXT_MAP.items():
            v = g[hs] if is_home else g[as_]
            ctx[k].append(np.nan if v is None else float(v))
        bm = g["baseline.home_margin"]
        script.append(np.nan if bm is None else (float(bm) if is_home else -float(bm)))
    for k, v in ctx.items():
        pf[k] = v
    pf["ctx.expected_script"] = script
    pf["ctx.is_home"] = home_flag
    pf = _role_stability(pf)
    return pf.reset_index(drop=True)


def _primary_share(pos: str) -> tuple[str, str]:
    return {"QB": ("sh_attempt_s", "sh_attempt_l"), "RB": ("sh_carry_s", "sh_carry_l")}.get(pos, ("sh_target_s", "sh_target_l"))


def _role_stability(pf: pd.DataFrame) -> pd.DataFrame:
    inj = pd.concat([_injuries(s) for s in PLAYER_SEASONS], ignore_index=True)
    inj["report_status"] = inj["report_status"].fillna("")
    status = {(int(r.season), int(r.week), r.gsis_id): r.report_status for r in inj.itertuples()}
    pf["inj.status"] = [status.get((int(s), int(w), p), "") for s, w, p in zip(pf["season"], pf["week"], pf["player_id"], strict=False)]
    out_list: dict = {}
    for r in inj[inj["report_status"].isin(["Out", "Doubtful"])].itertuples():
        out_list.setdefault((int(r.season), int(r.week), r.team), set()).add(r.gsis_id)
    # each player's appearances: (season, week, team, position, long-window primary share at that appearance;
    # that share is itself computed from strictly earlier games)
    hist: dict = {}
    for r in pf[["player_id", "season", "week", "team", "position", "sh_target_l", "sh_carry_l", "sh_attempt_l"]].itertuples(index=False):
        lshare = {"QB": r.sh_attempt_l, "RB": r.sh_carry_l}.get(r.position, r.sh_target_l)
        hist.setdefault(r.player_id, []).append((int(r.season), int(r.week), r.team, r.position, lshare))
    for v in hist.values():
        v.sort()

    def last_share(pid: str, season: int, week: int, team: str):
        best = None
        for s_, w_, t_, pos_, sh_ in hist.get(pid, []):
            if (s_, w_) >= (season, week):
                break
            if s_ == season and t_ == team:
                best = (pos_, sh_)
        return best

    flags = []
    for r in pf[["season", "week", "team", "position", "player_id", "sh_target_l", "sh_carry_l", "sh_attempt_l"]].itertuples(index=False):
        s_, w_ = int(r.season), int(r.week)
        mine = {"QB": r.sh_attempt_l, "RB": r.sh_carry_l}.get(r.position, r.sh_target_l)
        flag = False
        for o in out_list.get((s_, w_, r.team), ()):
            if o == r.player_id:
                continue
            ls = last_share(o, s_, w_, r.team)
            if ls is not None and ls[0] == r.position and ls[1] is not None and np.isfinite(ls[1]) and np.isfinite(mine) and ls[1] > mine:
                flag = True
                break
        flags.append(flag)
    pf["inj.teammate_out"] = flags
    sh_s = np.where(pf["position"] == "QB", pf["sh_attempt_s"], np.where(pf["position"] == "RB", pf["sh_carry_s"], pf["sh_target_s"])).astype(float)
    sh_l = np.where(pf["position"] == "QB", pf["sh_attempt_l"], np.where(pf["position"] == "RB", pf["sh_carry_l"], pf["sh_target_l"])).astype(float)
    snap_d = (pf["snap_share_s"] - pf["snap_share_l"]).abs().to_numpy(float)
    role = np.full(len(pf), "STABLE_ROLE", dtype=object)
    change = (np.isfinite(sh_s) & np.isfinite(sh_l) & (np.abs(sh_s - sh_l) >= 0.10)) | (np.isfinite(snap_d) & (snap_d >= 0.15))
    role[change] = "ROLE_CHANGE"
    injury = pf["inj.status"].isin(["Questionable", "Doubtful"]).to_numpy() | pf["inj.teammate_out"].to_numpy(bool)
    role[injury] = "INJURY_DEPENDENT"
    role[pf["n_prior"].to_numpy() < 3] = "INSUFFICIENT_ROLE_HISTORY"
    pf["role_stability"] = role
    return pf
