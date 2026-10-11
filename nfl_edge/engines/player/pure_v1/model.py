"""PURE_PLAYER_V1 model: football-only team environment -> role -> opportunity -> efficiency -> distributions.

    environment   ridge on prior-only team / opponent EWMs and the football-only expected margin / points
                  (features.TEAM_*): team pass attempts, rush attempts, points. Fitted on EVERY regular-season
                  team-game of seasons [first_season, target_season) with a box score -- no market filter.
    snap share    ridge per position group on the player's prior snap-share history
    shares        target share (RB / WR / TE), carry share (RB, starting QB): ridge on share history, the
                  predicted snap share and the snap-scaled structural share
    counts        targets = volume x share stacked with the raw-count EWM in a 2-feature Poisson GLM (the
                  repository's opportunity research found the stack beats either alone); carries likewise;
                  starting-QB attempts from predicted team pass volume and his own EWM
    efficiency    catch rate, yards per reception / carry / attempt, completion rate: player EWM rate and the
                  opponent's prior-only allowed rate (opponent adjustment)
    distribution  counts: negative binomial with one dispersion per (statistic, position group); yards: the
                  training distribution of actual / predicted in five predicted-mean bins (heavy right tail and
                  the zero mass come from data, not from a fitted shape); snap share: binned residuals on [0, 1].

CONDITIONAL ON PLAYING. Every player forecast is conditional on the player's own participation (>= 1 offensive
snap or a box-score line); QB passing statistics are conditional on starting. Teammates' realised participation is
never used (it is not pregame information). The baseline arm (`baseline.py`) is scored on exactly the same rows.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from nfl_edge.engines.player.pure_v1 import VERSION
from nfl_edge.engines.player.pure_v1.dists import NBDist, RatioDist, ResidDist
from nfl_edge.engines.player.v4.linear import Linear          # a generic ridge / Poisson estimator (no inputs of its own)

FIRST_SEASON = 2014
TEAM_PA = ["f_pa", "f_rate", "f_plays", "o_pa_allowed", "o_plays_allowed", "o_rate_allowed", "exp_margin", "exp_points",
           "home_f", "dome_f", "rest_days", "qb_changed_recent"]
TEAM_RA = ["f_ra", "f_rate", "f_plays", "o_ra_allowed", "o_plays_allowed", "o_rate_allowed", "exp_margin", "exp_points",
           "home_f", "dome_f", "rest_days", "qb_changed_recent"]
TEAM_PTS = ["f_pts", "o_pts_allowed", "exp_margin", "exp_points", "f_ypa", "o_ypa_allowed", "home_f", "dome_f", "rest_days",
            "qb_changed_recent"]
SNAP = ["e_snap_share", "last_snap_share", "last3_snap_share", "max4_snap_share", "cur_snap_share", "n_cur_c", "log_n_prior",
        "changed_team", "gap_gt0"]
TARGET_GROUPS, CARRY_GROUPS = ("RB", "WR", "TE"), ("RB", "QB")
MIN_TRAIN = 300
# opponent-adjustment context each player row reads from its team-game (all prior-only)
PLAYER_CONTEXT = ["o_cmp_allowed", "o_ypt_allowed", "o_ypc_allowed", "o_ypa_allowed", "o_rate_allowed", "f_ypa", "exp_margin"]

# statistic -> (population, distribution kind)
STATS = {
    "snap_share": ("SNAP", "resid"), "targets": ("REC", "nb"), "receptions": ("REC", "nb"), "receiving_yards": ("REC", "ratio"),
    "carries": ("RUSH", "nb"), "rushing_yards": ("RUSH", "ratio"), "passing_attempts": ("QB", "nb"),
    "completions": ("QB", "nb"), "passing_yards": ("QB", "ratio"),
}
OUTCOME = {"snap_share": "snap_share", "targets": "targets", "receptions": "receptions", "receiving_yards": "receiving_yards",
           "carries": "carries", "rushing_yards": "rushing_yards", "passing_attempts": "attempts", "completions": "completions",
           "passing_yards": "passing_yards"}
LADDERS = {
    "snap_share": [0.25, 0.5, 0.75], "targets": list(range(1, 13)), "receptions": list(range(1, 11)),
    "receiving_yards": list(range(10, 151, 10)), "carries": list(range(2, 25, 2)), "rushing_yards": list(range(10, 151, 10)),
    "passing_attempts": list(range(20, 46, 5)), "completions": list(range(10, 31, 5)), "passing_yards": list(range(150, 351, 25)),
}
# the pregame model inputs carried as lineage on each forecast (all football-only)
LINEAGE = {"snap_share": ["snap_mean", "e_snap_share"], "targets": ["vol_pa", "share_t", "e_targets"],
           "receptions": ["mu_targets", "r_cr"], "receiving_yards": ["mu_receptions", "r_ypr"],
           "carries": ["vol_ra", "share_c", "e_carries"], "rushing_yards": ["mu_carries", "r_ypc"],
           "passing_attempts": ["vol_pa", "e_attempts"], "completions": ["mu_attempts", "r_comp"],
           "passing_yards": ["mu_attempts", "r_ypa"]}


def population(rows: pd.DataFrame, stat: str) -> np.ndarray:
    pop = STATS[stat][0]
    g = rows["pgroup"].to_numpy(); played = rows["played"].to_numpy(bool)
    qbs = (g == "QB") & rows["qb_starter"].to_numpy(bool)
    if pop == "SNAP":
        return played & (np.isin(g, TARGET_GROUPS) | qbs) & np.isfinite(rows["team_snaps"].to_numpy(float))
    if pop == "REC":
        return played & np.isin(g, TARGET_GROUPS)
    if pop == "RUSH":
        return played & ((g == "RB") | qbs)
    return played & qbs


def outcome(rows: pd.DataFrame, stat: str) -> np.ndarray:
    return rows[OUTCOME[stat]].to_numpy(float)


def _fit_dist(kind: str, y, mu):
    ok = np.isfinite(y) & np.isfinite(mu)
    if kind == "nb":
        return NBDist.fit(y[ok], mu[ok])
    if kind == "ratio":
        return RatioDist.fit(y[ok], mu[ok])
    return ResidDist.fit(y[ok], mu[ok])


@dataclass
class PureModel:
    target_season: int
    first_season: int = FIRST_SEASON
    version: str = VERSION
    team: dict = field(default_factory=dict)          # target -> Linear
    team_sd: dict = field(default_factory=dict)
    snap: dict = field(default_factory=dict)          # group -> Linear
    share: dict = field(default_factory=dict)         # (kind, group) -> Linear
    stack: dict = field(default_factory=dict)         # (raw, group) -> Linear (poisson)
    rate: dict = field(default_factory=dict)          # (name, group) -> Linear
    dist: dict = field(default_factory=dict)          # (stat, group) -> distribution
    info: dict = field(default_factory=dict)

    # ---------------------------------------------------------------------------------------------- stages
    def team_predict(self, t: pd.DataFrame) -> pd.DataFrame:
        out = t[["team", "game_id"]].copy()
        out["vol_pa"] = np.clip(self.team["pa"].predict(t), 12, 60)
        out["vol_ra"] = np.clip(self.team["ra"].predict(t), 10, 50)
        out["vol_plays"] = out["vol_pa"] + out["vol_ra"]
        out["vol_pts"] = np.clip(self.team["pts"].predict(t), 3, 50)
        return out

    def _grouped(self, d: pd.DataFrame, models: dict, key_fn, default) -> np.ndarray:
        out = np.asarray(default, float).copy() if np.ndim(default) else np.full(len(d), float(default))
        g = d["pgroup"].to_numpy()
        for grp in np.unique(g):
            m = models.get(key_fn(grp))
            if m is None:
                continue
            ix = np.where(g == grp)[0]
            out[ix] = m.predict(d.iloc[ix])
        return out

    def intermediates(self, rows: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
        ctx = t[["team", "game_id"] + PLAYER_CONTEXT].merge(self.team_predict(t), on=["team", "game_id"], how="left")
        d = rows.drop(columns=[c for c in PLAYER_CONTEXT if c in rows.columns]).merge(ctx, on=["team", "game_id"], how="left")
        d["snap_mean"] = np.clip(self._grouped(d, self.snap, lambda g: g, d["e_snap_share"].to_numpy(float)), 0.005, 0.995)
        for kind, s in (("target", "t"), ("carry", "c")):
            ratio = d[f"e_{kind}_share"] / d["e_snap_share"].clip(lower=0.05)
            d[f"struct_{kind}"] = (ratio * d["snap_mean"]).clip(0, 1)
            d[f"share_{s}"] = np.clip(self._grouped(d, self.share, lambda g, k=kind: (k, g), d[f"e_{kind}_share"].to_numpy(float)), 0.0, 0.8)
        for raw, vol, s in (("targets", "vol_pa", "t"), ("carries", "vol_ra", "c")):
            d[f"struct_{raw}"] = d[vol] * d[f"share_{s}"]
            d[f"l_struct_{raw}"] = np.log(d[f"struct_{raw}"].clip(lower=0) + 0.2)
            d[f"l_e_{raw}"] = np.log(d[f"e_{raw}"].clip(lower=0) + 0.2)
            d[f"mu_{raw}"] = np.maximum(self._grouped(d, self.stack, lambda g, r=raw: (r, g), d[f"struct_{raw}"].to_numpy(float)), 0.01)
        for name, default, lo, hi in (("cr", 0.65, 0.3, 0.95), ("ypr", 10.0, 3.0, 25.0), ("ypc", 4.2, 0.5, 9.0),
                                      ("comp", 0.64, 0.45, 0.8), ("ypa", 7.0, 4.0, 11.0)):
            d[f"r_{name}"] = np.clip(self._grouped(d, self.rate, lambda g, n=name: (n, g), default), lo, hi)
        d["mu_receptions"] = d["mu_targets"] * d["r_cr"]
        d["mu_receiving_yards"] = d["mu_receptions"] * d["r_ypr"]
        d["mu_rushing_yards"] = d["mu_carries"] * d["r_ypc"]
        d["mu_attempts"] = np.maximum(self._grouped(d, self.rate, lambda g: ("attempts", g), d["e_attempts"].to_numpy(float)), 1.0)
        d["mu_completions"] = d["mu_attempts"] * d["r_comp"]
        d["mu_passing_yards"] = d["mu_attempts"] * d["r_ypa"]
        return d

    def means(self, d: pd.DataFrame) -> dict:
        return {"snap_share": d["snap_mean"].to_numpy(float), "targets": d["mu_targets"].to_numpy(float),
                "receptions": d["mu_receptions"].to_numpy(float), "receiving_yards": d["mu_receiving_yards"].to_numpy(float),
                "carries": d["mu_carries"].to_numpy(float), "rushing_yards": d["mu_rushing_yards"].to_numpy(float),
                "passing_attempts": d["mu_attempts"].to_numpy(float), "completions": d["mu_completions"].to_numpy(float),
                "passing_yards": d["mu_passing_yards"].to_numpy(float)}

    def sha(self) -> str:
        blob = json.dumps({"version": self.version, "target_season": self.target_season, "info": self.info}, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]


def fit(rows: pd.DataFrame, t: pd.DataFrame, target_season: int, *, first_season: int = FIRST_SEASON) -> PureModel:
    """Fit every stage on seasons [first_season, target_season). No row is excluded for lacking a market."""
    m = PureModel(target_season=target_season, first_season=first_season)
    tt = t[(t.season < target_season) & (t.season >= first_season) & t.pa.notna() & t.pts.notna()]
    for name, cols, y in (("pa", TEAM_PA, tt.pa), ("ra", TEAM_RA, tt.ra), ("pts", TEAM_PTS, tt.pts)):
        m.team[name] = Linear.fit(tt, cols, y.to_numpy(float))
        m.team_sd[name] = float(np.std(y.to_numpy(float) - m.team[name].predict(tt)))
    tr = rows[(rows.season < target_season) & (rows.season >= first_season) & rows.played].copy()
    g = tr["pgroup"].to_numpy()
    qbs = (g == "QB") & tr["qb_starter"].to_numpy(bool)
    # snap share
    sm = population(tr, "snap_share") & np.isfinite(tr["snap_share"].to_numpy(float))
    for grp in ("QB", "RB", "WR", "TE"):
        sub = tr[sm & (g == grp)]
        if len(sub) >= MIN_TRAIN:
            m.snap[grp] = Linear.fit(sub, SNAP, sub["snap_share"].clip(0, 1).to_numpy(float))
    d = m.intermediates(tr, t)          # snap_mean, volumes (shares / stacks / rates still at their defaults)
    for kind, groups in (("target", TARGET_GROUPS), ("carry", CARRY_GROUPS)):
        cols = [f"e_{kind}_share", f"last_{kind}_share", f"last3_{kind}_share", f"cur_{kind}_share", "snap_mean", f"struct_{kind}",
                "changed_team", "n_cur_c", "log_n_prior"]
        for grp in groups:
            mask = (g == grp) & (qbs if grp == "QB" else True)
            sub = d[mask & d[f"{kind}_share"].notna().to_numpy()]
            if len(sub) >= MIN_TRAIN:
                m.share[(kind, grp)] = Linear.fit(sub, cols, sub[f"{kind}_share"].clip(0, 1).to_numpy(float))
    d = m.intermediates(tr, t)
    for raw, groups in (("targets", TARGET_GROUPS), ("carries", CARRY_GROUPS)):
        for grp in groups:
            mask = (g == grp) & (qbs if grp == "QB" else True)
            sub = d[mask]
            if len(sub) >= MIN_TRAIN:
                m.stack[(raw, grp)] = Linear.fit(sub, [f"l_struct_{raw}", f"l_e_{raw}"], sub[raw].to_numpy(float), kind="poisson")
    d = m.intermediates(tr, t)
    for grp in TARGET_GROUPS:
        sub = d[(g == grp) & (d["targets"] > 0).to_numpy()]
        if len(sub) >= MIN_TRAIN:
            m.rate[("cr", grp)] = Linear.fit(sub, ["p_cr", "o_cmp_allowed", "log_n_prior"], (sub.receptions / sub.targets).to_numpy(float),
                                             weights=sub.targets.to_numpy(float))
        sub = d[(g == grp) & (d["receptions"] > 0).to_numpy()]
        if len(sub) >= MIN_TRAIN:
            m.rate[("ypr", grp)] = Linear.fit(sub, ["p_ypr", "o_ypt_allowed", "f_ypa"], (sub.receiving_yards / sub.receptions).to_numpy(float),
                                              weights=sub.receptions.to_numpy(float))
    for grp in CARRY_GROUPS:
        mask = (g == grp) & (qbs if grp == "QB" else True) & (d["carries"] > 0).to_numpy()
        sub = d[mask]
        if len(sub) >= MIN_TRAIN:
            m.rate[("ypc", grp)] = Linear.fit(sub, ["p_ypc", "o_ypc_allowed", "exp_margin"], (sub.rushing_yards / sub.carries).to_numpy(float),
                                              weights=sub.carries.to_numpy(float))
    qb = d[qbs]
    if len(qb) >= MIN_TRAIN:
        m.rate[("attempts", "QB")] = Linear.fit(qb, ["vol_pa", "e_attempts", "exp_margin", "o_rate_allowed"], qb.attempts.to_numpy(float), kind="poisson")
        sub = qb[qb.attempts > 0]
        m.rate[("comp", "QB")] = Linear.fit(sub, ["p_comp", "o_cmp_allowed"], (sub.completions / sub.attempts).to_numpy(float),
                                            weights=sub.attempts.to_numpy(float))
        m.rate[("ypa", "QB")] = Linear.fit(sub, ["p_ypa", "o_ypa_allowed", "f_ypa"], (sub.passing_yards / sub.attempts).to_numpy(float),
                                           weights=sub.attempts.to_numpy(float))
    d = m.intermediates(tr, t)
    fit_distributions(m.dist, d, m.means(d))
    m.info = {"n_team_games": int(len(tt)), "n_player_rows": int(len(tr)), "train_seasons": [first_season, target_season - 1],
              "team_sd": {k: round(v, 3) for k, v in m.team_sd.items()},
              "train_data_observed_through": str(rows.loc[rows.season < target_season, "kickoff"].max())}
    return m


def fit_distributions(store: dict, d: pd.DataFrame, means: dict) -> None:
    """One distribution per (statistic, position group), fitted on training rows of the statistic's population."""
    g = d["pgroup"].to_numpy()
    for stat, (_, kind) in STATS.items():
        pop = population(d, stat)
        y, mu = outcome(d, stat), means[stat]
        for grp in ("QB", "RB", "WR", "TE"):
            ix = pop & (g == grp)
            if ix.sum() >= 50:
                store[(stat, grp)] = _fit_dist(kind, y[ix], mu[ix])


def forecast(store: dict, d: pd.DataFrame, means: dict, stat: str) -> pd.DataFrame:
    """Distribution summaries for the statistic's population rows: mean, median, p10, p90 and the ladder."""
    pop = population(d, stat)
    g = d["pgroup"].to_numpy()
    parts = []
    for grp in ("QB", "RB", "WR", "TE"):
        ix = np.where(pop & (g == grp))[0]
        dist = store.get((stat, grp))
        if not len(ix) or dist is None:
            continue
        f = dist.summarize(means[stat][ix], LADDERS[stat])
        f.index = d.index[ix]
        parts.append(f)
    return pd.concat(parts).sort_index() if parts else pd.DataFrame()
