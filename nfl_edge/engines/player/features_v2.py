"""Point-in-time features for Player Engine v2: OPPORTUNITY and EFFICIENCY decomposed, with explicit uncertainty.

Built on top of the frozen research table (`nfl_edge/research/player_distributions.load_player_games` +
`add_ewma_features`, imported, never edited) and adding, all from the player's and team's STRICTLY PRIOR games:

    team volume      EWMA of the team's pass attempts, rush attempts and offensive snaps per game
    player shares    EWMA of target share (targets / team pass attempts), carry share (carries / team rush
                     attempts), snap share (offense snaps / team snaps), red-zone-free (no play-by-play needed)
    QB environment   EWMA of the team's yards per attempt and pass rate; whether the team's QB in its previous
                     game differs from the one before (a recent QB change signal)
    role change      the change in a player's share over his last two games vs his EWMA (recent role shift)
    sample size      prior game count and the EWMA shrink weight, so uncertainty is explicit

Every feature for game g is computed from games with (season, week) strictly earlier than g. A prospective row
(a game not yet played) is chronologically last for its player and team, so the same code produces its features
from prior games only -- the same construction the frozen pricer uses (`nfl_edge/shadow/prospective.py`).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TEAM_COLS = ["team_pass_att", "team_rush_att", "team_snaps", "team_pass_yards", "team_plays"]
SHARE_COLS = ["target_share", "carry_share", "snap_share"]
V2_FEATURES = ["ewma_team_pass_att", "ewma_team_rush_att", "ewma_team_snaps", "ewma_team_ypa", "ewma_team_pass_rate",
               "ewma_target_share", "ewma_carry_share", "ewma_snap_share", "share_recent_delta_target", "share_recent_delta_carry",
               "qb_changed_recent", "n_prior", "shrink_w"]


def _ewma_by_key(df: pd.DataFrame, key: str, cols: list, halflife: float, season_carry: float, shrink_k: float, prior: np.ndarray | None,
                 prefix: str) -> pd.DataFrame:
    """EWMA over strictly prior rows per key, chronological, with season-boundary carry and shrink to a prior."""
    d = df.sort_values([key, "season", "week"], kind="mergesort")
    X = d[cols].to_numpy(float)
    keys = d[key].to_numpy(); season = d["season"].to_numpy()
    n, m = X.shape
    out = np.full((n, m), np.nan); cnt = np.zeros(n, int)
    dec = 0.5 ** (1.0 / halflife)
    pr = np.zeros(m) if prior is None else np.asarray(prior, float)
    S = np.zeros(m); W = np.zeros(m); cur = None; last = None; c = 0
    for i in range(n):
        if keys[i] != cur:
            cur = keys[i]; S = np.zeros(m); W = np.zeros(m); c = 0; last = season[i]
        elif season[i] != last:
            f = season_carry ** (season[i] - last); S = S * f; W = W * f; last = season[i]
        out[i] = (S + shrink_k * pr) / (W + shrink_k)
        cnt[i] = c
        v = X[i]; ok = np.isfinite(v)
        S = S * dec; W = W * dec
        S[ok] += v[ok]; W[ok] += 1.0
        c += 1
    res = pd.DataFrame(out, columns=[prefix + c_ for c_ in cols], index=d.index)
    res[prefix + "n"] = cnt
    return res.reindex(df.index)


def team_game_volume(df: pd.DataFrame) -> pd.DataFrame:
    """Per (team, game): pass attempts, rush attempts, offensive snaps (max over players), plays, pass yards."""
    g = df.groupby(["team", "game_id", "season", "week"], sort=False)
    t = g.agg(team_pass_att=("attempts", "sum"), team_rush_att=("carries", "sum"), team_snaps=("offense_snaps", "max"),
              team_pass_yards=("passing_yards", "sum")).reset_index()
    t["team_plays"] = t["team_pass_att"] + t["team_rush_att"]
    return t


def add_v2_features(df: pd.DataFrame, *, halflife: float = 6.0, season_carry: float = 0.35, shrink_k: float = 2.0) -> pd.DataFrame:
    """Attach the v2 opportunity / share / team-volume / QB-environment features. Prospective rows (NaN outcomes) get
    features from prior games only, exactly like historical rows."""
    df = df.copy()
    tv = team_game_volume(df)
    tv["team_ypa"] = tv["team_pass_yards"] / tv["team_pass_att"].clip(lower=1)
    tv["team_pass_rate"] = tv["team_pass_att"] / tv["team_plays"].clip(lower=1)
    # league priors from the earliest seasons present (never the evaluation window)
    pri_seasons = sorted(tv["season"].unique())[:3]
    pri = tv[tv["season"].isin(pri_seasons)][TEAM_COLS + ["team_ypa", "team_pass_rate"]].mean().to_numpy(float)
    te = _ewma_by_key(tv, "team", TEAM_COLS + ["team_ypa", "team_pass_rate"], halflife, season_carry, 4.0, pri, "ewma_")
    tv2 = pd.concat([tv[["team", "game_id"]], te], axis=1)
    df = df.merge(tv2.drop(columns=["ewma_n"]), on=["team", "game_id"], how="left")
    # player shares vs the team's ACTUAL volume in the same game (a realised share; its EWMA is the prior-only feature)
    df = df.merge(tv[["team", "game_id", "team_pass_att", "team_rush_att", "team_snaps"]], on=["team", "game_id"], how="left")
    df["target_share"] = df["targets"] / df["team_pass_att"].clip(lower=1)
    df["carry_share"] = df["carries"] / df["team_rush_att"].clip(lower=1)
    df["snap_share"] = df["offense_snaps"] / df["team_snaps"].clip(lower=1)
    pos_prior = {}
    for pos, g in df[df["season"].isin(sorted(df["season"].unique())[:3])].groupby("position"):
        pos_prior[pos] = np.nan_to_num(g[SHARE_COLS].mean().to_numpy(float), nan=0.0)
    parts = []
    for pos, g in df.groupby("position", sort=False):
        parts.append(_ewma_by_key(g, "player_id", SHARE_COLS, halflife, season_carry, shrink_k, pos_prior.get(pos), "ewma_"))
    sh = pd.concat(parts).reindex(df.index)
    df[["ewma_target_share", "ewma_carry_share", "ewma_snap_share"]] = sh[["ewma_target_share", "ewma_carry_share", "ewma_snap_share"]]
    # recent role change: mean share over the last 2 prior games minus the EWMA (prior-only by construction)
    for c, name in (("target_share", "share_recent_delta_target"), ("carry_share", "share_recent_delta_carry")):
        d = df.sort_values(["player_id", "season", "week"], kind="mergesort")
        recent = d.groupby("player_id")[c].transform(lambda s: s.shift(1).rolling(2, min_periods=1).mean())
        df[name] = (recent.reindex(df.index) - df["ewma_" + c]).fillna(0.0)
    # QB environment: did the team's starting QB change between its previous two games?
    qb = df[df["position"] == "QB"].sort_values(["team", "season", "week", "attempts"], ascending=[True, True, True, False])
    qb = qb.drop_duplicates(["team", "game_id"], keep="first")[["team", "game_id", "season", "week", "player_id"]].sort_values(["team", "season", "week"])
    qb["prev_qb"] = qb.groupby("team")["player_id"].shift(1)
    qb["prev2_qb"] = qb.groupby("team")["player_id"].shift(2)
    qb["qb_changed_recent"] = ((qb["prev_qb"].notna()) & (qb["prev2_qb"].notna()) & (qb["prev_qb"] != qb["prev2_qb"])).astype(float)
    df = df.merge(qb[["team", "game_id", "qb_changed_recent"]], on=["team", "game_id"], how="left")
    df["qb_changed_recent"] = df["qb_changed_recent"].fillna(0.0)
    df = df.drop(columns=["team_pass_att", "team_rush_att", "team_snaps"], errors="ignore")
    return df


def has_v2_features(df: pd.DataFrame) -> bool:
    return all(c in df.columns for c in V2_FEATURES)
