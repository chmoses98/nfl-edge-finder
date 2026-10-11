"""Point-in-time features for PURE_PLAYER_V1, from football data only.

Every feature of a (player, game) row is built from games that finished before that game's forecast cutoff:

    team environment   exponentially weighted means (EWM) over the team's strictly prior games of its pass attempts,
                       rush attempts, plays, points and efficiency (offence), and of what its defence allowed; the
                       opponent's own prior offence / defence EWMs at the same instant; a football-only expected
                       margin and expected points from those EWMs (the sports-only replacement for a spread / total);
                       home, fixed dome venue, rest days, and whether the starting QB changed between the team's two
                       previous games (finished games only)
    player role        EWM / last / last-3 / max-of-4 / current-season mean of snap share, target share and carry
                       share over the player's strictly prior games; sample size; team change; team games missed
    player efficiency  EWM catch rate, yards per reception / carry / attempt, completion rate

Ordering is by UTC kickoff, never by a week label, and `provenance` records for each row the latest observation
time it consumed (previous game's kickoff + 4 h for the player, his team and the opponent), so a test can assert
source_max_observed_at <= as_of < kickoff on every row. Nothing reads injury reports, depth charts, weather or the
target game's starting quarterback: those sources are not proven point in time here, so the model abstains from them.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nfl_edge.engines.player.pure_v1.data import GAME_DURATION_HOURS

HALFLIFE, SEASON_CARRY = 6.0, 0.35          # the repository's sports-only EWMA constants (research/player_distributions)
TEAM_SHRINK, PLAYER_SHRINK = 4.0, 2.0
GROUP = {"QB": "QB", "RB": "RB", "FB": "RB", "HB": "RB", "WR": "WR", "TE": "TE"}
TEAM_OFF = ["pa", "ra", "plays", "pts", "pass_yds", "rush_yds", "cmp", "tgt", "rec", "rec_yds"]
PLAYER_EWM = ["snap_share", "target_share", "carry_share", "targets", "carries", "receptions", "receiving_yards",
              "rushing_yards", "attempts", "completions", "passing_yards"]


def ewm_prior(df: pd.DataFrame, key: str, cols: list, prior, *, halflife=HALFLIFE, carry=SEASON_CARRY, shrink=PLAYER_SHRINK,
              prefix="e_") -> pd.DataFrame:
    """EWM over STRICTLY PRIOR rows of each key in kickoff order, season-boundary carry, shrunk to `prior`.

    `prior` is a vector (one per column) or a per-row matrix (len(df) x len(cols)). NaN values are skipped."""
    d = df.sort_values([key, "kickoff", "game_id"], kind="mergesort")
    X = d[cols].to_numpy(float)
    P = np.asarray(prior, float)
    P = np.broadcast_to(P, X.shape) if P.ndim == 1 else P[df.index.get_indexer(d.index)]
    keys = d[key].to_numpy(); season = d["season"].to_numpy()
    n, m = X.shape
    out = np.full((n, m), np.nan); cnt = np.zeros(n, int)
    dec = 0.5 ** (1.0 / halflife)
    S = np.zeros(m); W = np.zeros(m); cur = None; last = None; c = 0
    for i in range(n):
        if keys[i] != cur:
            cur = keys[i]; S = np.zeros(m); W = np.zeros(m); c = 0; last = season[i]
        elif season[i] != last:
            f = carry ** (season[i] - last); S = S * f; W = W * f; last = season[i]
        out[i] = (S + shrink * P[i]) / (W + shrink)
        cnt[i] = c
        v = X[i]; ok = np.isfinite(v)
        S = S * dec; W = W * dec
        S[ok] += v[ok]; W[ok] += 1.0
        c += 1
    res = pd.DataFrame(out, columns=[prefix + x for x in cols], index=d.index)
    res[prefix + "n"] = cnt
    return res.reindex(df.index)


def _prev_kickoff(df: pd.DataFrame, key: str) -> pd.Series:
    d = df.sort_values([key, "kickoff", "game_id"], kind="mergesort")
    return d.groupby(key, sort=False)["kickoff"].shift(1).reindex(df.index)


# ------------------------------------------------------------------------------------------------ team table
def team_games(pg: pd.DataFrame) -> pd.DataFrame:
    """One row per (team, game) with realised volume / points (outcomes) and the starter, from the box score."""
    g = pg.groupby(["team", "game_id"], sort=False)
    t = g.agg(season=("season", "first"), week=("week", "first"), kickoff=("kickoff", "first"), opponent=("opponent_team", "first"),
              home=("home", "first"), dome=("dome", "first"), pa=("attempts", "sum"), ra=("carries", "sum"),
              pass_yds=("passing_yards", "sum"), rush_yds=("rushing_yards", "sum"), cmp=("completions", "sum"),
              tgt=("targets", "sum"), rec=("receptions", "sum"), rec_yds=("receiving_yards", "sum"),
              team_snaps=("offense_snaps", "max"), pts=("points_for", "first"), pts_against=("points_against", "first")).reset_index()
    t["plays"] = t["pa"] + t["ra"]
    q = pg[pg["qb_starter"]].sort_values("attempts", ascending=False).drop_duplicates(["team", "game_id"])
    t = t.merge(q[["team", "game_id", "player_id"]].rename(columns={"player_id": "starter"}), on=["team", "game_id"], how="left")
    return t


def add_team_features(t: pd.DataFrame) -> pd.DataFrame:
    """Prior-only offence / defence EWMs per team, the opponent's at the same instant, and matchup features."""
    t = t.copy()
    first = sorted(t["season"].unique())[:3]
    base = t[t["season"].isin(first)]
    off_prior = base[TEAM_OFF].mean().to_numpy(float)
    oe = ewm_prior(t, "team", TEAM_OFF, off_prior, shrink=TEAM_SHRINK, prefix="off_")
    # what each defence allowed = the opponent's offence in that game
    dv = t[["game_id", "team"] + TEAM_OFF].rename(columns={"team": "opponent", **{c: f"a_{c}" for c in TEAM_OFF}})
    t = t.merge(dv, on=["game_id", "opponent"], how="left")
    de = ewm_prior(t, "team", [f"a_{c}" for c in TEAM_OFF], off_prior, shrink=TEAM_SHRINK, prefix="def_")
    de.columns = [c.replace("def_a_", "def_") for c in de.columns]
    t = pd.concat([t, oe, de], axis=1)
    t["prev_kickoff"] = _prev_kickoff(t, "team")
    # recent QB change, from finished games only: did the starters of the team's two previous games differ?
    s = t.sort_values(["team", "kickoff", "game_id"], kind="mergesort")
    p1 = s.groupby("team")["starter"].shift(1); p2 = s.groupby("team")["starter"].shift(2)
    t["qb_changed_recent"] = ((p1.notna()) & (p2.notna()) & (p1 != p2)).astype(float).reindex(t.index)
    rest = (t["kickoff"] - t["prev_kickoff"]).dt.total_seconds() / 86400.0
    t["rest_days"] = rest.where(rest < 20, 14.0).fillna(14.0).clip(3, 14)
    t["team_seq"] = s.groupby("team").cumcount().reindex(t.index)
    # the opponent's own prior EWMs for this same game (its row is strictly prior-only too)
    oc = [c for c in t.columns if c.startswith("off_") or c.startswith("def_")] + ["prev_kickoff"]
    opp = t[["game_id", "team"] + oc].rename(columns={"team": "opponent", **{c: f"o_{c}" for c in oc}})
    t = t.merge(opp, on=["game_id", "opponent"], how="left")
    eps = 1e-6
    t["f_pa"], t["f_ra"], t["f_plays"], t["f_pts"] = t["off_pa"], t["off_ra"], t["off_plays"], t["off_pts"]
    t["f_rate"] = t["off_pa"] / (t["off_plays"] + eps)
    t["f_ypa"] = t["off_pass_yds"] / (t["off_pa"] + eps)
    t["f_ypc"] = t["off_rush_yds"] / (t["off_ra"] + eps)
    t["o_pa_allowed"], t["o_ra_allowed"] = t["o_def_pa"], t["o_def_ra"]
    t["o_plays_allowed"], t["o_pts_allowed"] = t["o_def_plays"], t["o_def_pts"]
    t["o_rate_allowed"] = t["o_def_pa"] / (t["o_def_plays"] + eps)
    t["o_ypa_allowed"] = t["o_def_pass_yds"] / (t["o_def_pa"] + eps)
    t["o_ypc_allowed"] = t["o_def_rush_yds"] / (t["o_def_ra"] + eps)
    t["o_cmp_allowed"] = t["o_def_cmp"] / (t["o_def_pa"] + eps)
    t["o_ypt_allowed"] = t["o_def_rec_yds"] / (t["o_def_tgt"] + eps)
    t["o_off_plays"] = t["o_off_plays"]
    # football-only game environment: EWM point differential of each side, and a matchup points expectation
    t["exp_margin"] = (t["off_pts"] - t["def_pts"]) - (t["o_off_pts"] - t["o_def_pts"])
    t["exp_points"] = 0.5 * (t["off_pts"] + t["o_def_pts"])
    t["home_f"] = t["home"].astype(float); t["dome_f"] = t["dome"].astype(float)
    obs = [t["prev_kickoff"], t["o_prev_kickoff"]]
    t["team_src_max"] = pd.concat(obs, axis=1).max(axis=1)
    return t


# ------------------------------------------------------------------------------------------------ player rows
def add_player_features(pg: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    """Join the team environment and add the player's prior-only role and efficiency features."""
    d = pg.copy()
    tcols = ["team", "game_id", "pa", "ra", "team_snaps", "team_seq", "team_src_max"]
    d = d.merge(t[tcols], on=["team", "game_id"], how="left")
    d["pgroup"] = d["position"].map(GROUP).fillna("OTHER")
    d["snap_share"] = d["offense_snaps"] / d["team_snaps"].where(d["team_snaps"] > 0)
    d["target_share"] = d["targets"] / d["pa"].clip(lower=1)
    d["carry_share"] = d["carries"] / d["ra"].clip(lower=1)
    first = sorted(d["season"].unique())[:3]
    pri = d[d["season"].isin(first)].groupby("pgroup")[PLAYER_EWM].mean()
    P = np.nan_to_num(pri.reindex(d["pgroup"].to_numpy()).to_numpy(float), nan=0.0)
    e = ewm_prior(d, "player_id", PLAYER_EWM, P, shrink=PLAYER_SHRINK, prefix="e_")
    d = pd.concat([d, e], axis=1)
    s = d.sort_values(["player_id", "kickoff", "game_id"], kind="mergesort")
    g = s.groupby("player_id", sort=False)
    for c in ("snap_share", "target_share", "carry_share"):
        s[f"last_{c}"] = g[c].shift(1)
        s[f"last3_{c}"] = g[c].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
        s[f"cur_{c}"] = s.groupby(["player_id", "season"], sort=False)[c].transform(lambda x: x.shift(1).expanding().mean())
    s["max4_snap_share"] = g["snap_share"].transform(lambda x: x.shift(1).rolling(4, min_periods=1).max())
    s["n_cur_season"] = s.groupby(["player_id", "season"], sort=False).cumcount()
    prev_team = g["team"].shift(1); prev_season = g["season"].shift(1); prev_seq = g["team_seq"].shift(1)
    s["changed_team"] = (prev_team.notna() & (prev_team != s["team"])).astype(float)
    same = (prev_team == s["team"]) & (prev_season == s["season"])
    s["games_missed"] = np.where(same, s["team_seq"] - prev_seq - 1, np.nan)
    s["player_prev_kickoff"] = g["kickoff"].shift(1)
    d = s.reindex(d.index)
    for c in ("snap_share", "target_share", "carry_share"):
        for pre in ("last_", "last3_", "cur_"):
            d[pre + c] = d[pre + c].where(d[pre + c].notna(), d["e_" + c])
    d["max4_snap_share"] = d["max4_snap_share"].where(d["max4_snap_share"].notna(), d["e_snap_share"])
    d["log_n_prior"] = np.log1p(d["e_n"])
    d["n_cur_c"] = np.minimum(d["n_cur_season"], 4) / 4.0
    d["gap_gt0"] = (d["games_missed"].fillna(0) > 0).astype(float)
    d["p_cr"] = (d["e_receptions"] / d["e_targets"].clip(lower=0.3)).clip(0.2, 1.0)
    d["p_ypr"] = (d["e_receiving_yards"] / d["e_receptions"].clip(lower=0.3)).clip(2.0, 25.0)
    d["p_ypc"] = (d["e_rushing_yards"] / d["e_carries"].clip(lower=0.3)).clip(-1.0, 10.0)
    d["p_comp"] = (d["e_completions"] / d["e_attempts"].clip(lower=1.0)).clip(0.4, 0.8)
    d["p_ypa"] = (d["e_passing_yards"] / d["e_attempts"].clip(lower=1.0)).clip(3.0, 12.0)
    d["src_max"] = pd.concat([d["player_prev_kickoff"], d["team_src_max"]], axis=1).max(axis=1) + pd.Timedelta(hours=GAME_DURATION_HOURS)
    return d


def build(pg: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """player-game table (data.build_player_games) -> (player rows with features, team table with features)."""
    t = add_team_features(team_games(pg))
    rows = add_player_features(pg, t)
    return rows, t
