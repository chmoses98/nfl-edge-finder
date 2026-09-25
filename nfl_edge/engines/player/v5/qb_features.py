"""V5 QUARTERBACK-IDENTITY FEATURES: what changes for a team when a different quarterback throws its passes.

V4's structure knows the starting quarterback only as a FLAG on one row (`qb_starter`): it decides which QB row gets
passing distributions and feeds his snap model. Nothing else in V4 depends on who the quarterback is -- team pass
volume, the pass-catchers' catch rate and yards per catch are the same whether the starter or the third-stringer
plays, which is exactly why a wrong QB1 (docs/KNOWN_LIMITATIONS.md #89) left every pass-catcher on the wrong passing
environment. V5 adds, per team-game, four features of the PROJECTED starter, all from strictly prior games:

    qb_new_starter   1 when the projected starter is not the quarterback who started the team's previous game
    qb_ypa_delta     the projected starter's shrunk yards per attempt minus the previous starter's, both measured at
                     this game's instant (0 when the starter is unchanged)
    qb_cmp_delta     the same for completion rate
    qb_exp           log(1 + career pass attempts) of the projected starter

A quarterback's rates are exponentially weighted over his own attempt-bearing games (half-life HALFLIFE_GAMES) and
shrunk to a replacement-level prior with SHRINK_ATTEMPTS pseudo-attempts: a backup with 40 career attempts is mostly
the prior, a veteran is mostly himself. The prior and the shrinkage are fixed constants, set before any scoring and
never fitted to the evaluation window; the model learns how much each feature matters (V4's stages with the features
appended: nfl_edge/engines/player/v4/model.py QB_IDENTITY).

WHO is the projected starter:
    historical team-games   the realised starter (the schedule's starting-QB id; the quarterback with the most
                            attempts if the schedule has none). In training this is the analogue of a correctly
                            resolved pregame quarterback. It is ALSO what the "previous starter" of the next game is:
                            a finished game's starter is known before the next one.
    projected team-games    ONLY the `starters` map handed in -- the point-in-time resolution
                            (nfl_edge/context/qb_resolution.py) -- never the schedule's QB id of an unplayed game.
                            A game in the map with no resolved quarterback gets NaN features (unknown, never zero;
                            the fitted stages fill a NaN with the training mean).
"""
from __future__ import annotations

from bisect import bisect_left

import numpy as np
import pandas as pd

HALFLIFE_GAMES = 12.0
SHRINK_ATTEMPTS = 150.0
PRIOR_YPA = 6.2              # replacement level: a QB with no history is a replacement-level QB
PRIOR_CMP = 0.60
QB_ID_COLS = ["qb_projected_id", "qb_new_starter", "qb_ypa_delta", "qb_cmp_delta", "qb_exp"]


def _is_pro(df: pd.DataFrame) -> np.ndarray:
    return df.get("is_prospective", pd.Series(False, index=df.index)).fillna(False).astype(bool).to_numpy()


def realised_starters(df: pd.DataFrame) -> dict:
    """(team, game_id) -> gsis of the quarterback who started each PLAYED team-game (see the module docstring)."""
    h = df[(~_is_pro(df)) & (df["position"] == "QB")]
    out = {}
    if not len(h):
        return out
    att = h["attempts"].fillna(0).to_numpy(float)
    flag = h.get("qb_starter", pd.Series(False, index=h.index)).fillna(False).astype(bool).to_numpy()
    pid_all = h["player_id"].to_numpy()
    for key, ix in h.groupby(["team", "game_id"], sort=False).indices.items():
        f, a = flag[ix], att[ix]
        if f.any():                                   # the schedule's starter (two flagged: the one who threw more)
            sel = ix[f]
            out[key] = pid_all[sel[int(np.argmax(att[sel]))]]
        elif a.max() > 0:
            out[key] = pid_all[ix[int(np.argmax(a))]]
    return out


class QbHistory:
    """Per quarterback: exponentially weighted passing sums AFTER each of his attempt-bearing games, for strictly-prior
    lookups at any (season, week)."""

    def __init__(self, df: pd.DataFrame, halflife: float = HALFLIFE_GAMES):
        h = df[(~_is_pro(df)) & (df["position"] == "QB") & (df["attempts"].fillna(0) > 0)]
        h = h.sort_values(["player_id", "season", "week"], kind="mergesort")
        dec = 0.5 ** (1.0 / halflife)
        self.keys, self.sums = {}, {}
        for pid, g in h.groupby("player_id", sort=False):
            ks, ss = [], []
            y = c = a = raw = 0.0
            for s, w, yds, cmp_, att in g[["season", "week", "passing_yards", "completions", "attempts"]].itertuples(index=False):
                y = y * dec + float(np.nan_to_num(yds)); c = c * dec + float(np.nan_to_num(cmp_)); a = a * dec + float(att)
                raw += float(att)
                ks.append((int(s), int(w))); ss.append((y, c, a, raw))
            self.keys[pid], self.sums[pid] = ks, ss

    def rates(self, pid, season: int, week: int) -> tuple[float, float, float]:
        """(shrunk ypa, shrunk completion rate, log1p career attempts) from games strictly before (season, week)."""
        ks = self.keys.get(pid)
        y = c = a = raw = 0.0
        if ks:
            i = bisect_left(ks, (int(season), int(week))) - 1
            if i >= 0:
                y, c, a, raw = self.sums[pid][i]
        k = SHRINK_ATTEMPTS
        return (y + k * PRIOR_YPA) / (a + k), (c + k * PRIOR_CMP) / (a + k), float(np.log1p(raw))


def team_game_qb_features(df: pd.DataFrame, starters: dict | None = None) -> pd.DataFrame:
    """One row per (team, game_id): the projected starter and the four identity features."""
    starters = dict(starters or {})
    real = realised_starters(df)
    hist = QbHistory(df)
    tg = df[["team", "game_id", "season", "week"]].drop_duplicates(["team", "game_id"])
    tg = tg.sort_values(["team", "season", "week"], kind="mergesort")
    rows = []
    for team, g in tg.groupby("team", sort=False):
        prev = None
        for gid, s, w in g[["game_id", "season", "week"]].itertuples(index=False):
            key = (team, gid)
            qb = starters[key] if key in starters else real.get(key)
            if qb is None or (isinstance(qb, float) and np.isnan(qb)):
                rows.append({"team": team, "game_id": gid, "qb_projected_id": None, "qb_new_starter": np.nan,
                             "qb_ypa_delta": np.nan, "qb_cmp_delta": np.nan, "qb_exp": np.nan})
            else:
                ypa, cmp_, exp = hist.rates(qb, s, w)
                if prev is None or prev == qb:
                    new, dy, dc = 0.0, 0.0, 0.0
                else:
                    pypa, pcmp, _ = hist.rates(prev, s, w)
                    new, dy, dc = 1.0, ypa - pypa, cmp_ - pcmp
                rows.append({"team": team, "game_id": gid, "qb_projected_id": qb, "qb_new_starter": new,
                             "qb_ypa_delta": dy, "qb_cmp_delta": dc, "qb_exp": exp})
            # the NEXT game's "previous starter" is who actually started this one -- known once it is played
            if real.get(key) is not None:
                prev = real[key]
    return pd.DataFrame(rows, columns=["team", "game_id"] + QB_ID_COLS)


def add_qb_identity_features(df: pd.DataFrame, starters: dict | None = None) -> pd.DataFrame:
    """Attach QB_ID_COLS to every row of its team-game. `starters` overrides the projected starter of the games it
    names (the point-in-time resolution); every other game uses its realised starter."""
    d = df.drop(columns=[c for c in QB_ID_COLS if c in df.columns])
    f = team_game_qb_features(d, starters)
    out = d.merge(f, on=["team", "game_id"], how="left")
    out.index = d.index
    return out


def apply_starters(df: pd.DataFrame, starters: dict) -> pd.DataFrame:
    """Set `qb_starter` on the rows of the team-games in `starters` from the resolution: True for the projected
    starter's own row, False for every other quarterback of that team-game (a team with no resolved QB: all False)."""
    d = df.copy()
    key = list(zip(d["team"], d["game_id"]))
    hit = np.array([k in starters for k in key])
    if hit.any():
        qb = np.array([starters.get(k) for k in key], dtype=object)
        d.loc[hit, "qb_starter"] = (d.loc[hit, "player_id"].to_numpy() == qb[hit]) & pd.notna(qb[hit])
    return d
