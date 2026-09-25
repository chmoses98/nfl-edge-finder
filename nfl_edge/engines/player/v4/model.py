"""DATA_PLAYER_V4: snap -> team volume -> role allocation (with teammate redistribution) -> outcome distributions.

Chain (every stage is a small readable model fitted on seasons strictly before the target season):

    snap      SnapModel: per position group, pregame snap share mean + sd (features.py, snap.py)
    volume    VolumeModel: team pass / rush attempts from team + opponent EWMAs and the game environment (volume.py)
    share     target share (RB/WR/TE) and carry share (QB/RB/WR): ridge on the player's own share history, the
              PREDICTED snap share, and the vacated / returning teammate shares weighted by who absorbs them.
              Shares are reconciled per team-game (they cannot sum past the team's total).
    counts    targets = volume x share, stacked with the raw-count EWMA (research/opportunity: a multiplicative
              reconstruction alone loses to the raw EWMA, the two together win), fitted as a 2-feature Poisson GLM.
    outcome   receptions = targets thinned by a shrunk catch rate; yards are COMPOUND: a sum of per-reception
              (per-carry, per-completion) gammas whose count is itself uncertain, so heavy right tails and the
              zero mass come from the structure, not from a fitted shape. Rushing uses a shifted gamma per carry
              (a carry can lose yards). TDs are negative binomial on an opportunity-driven Poisson GLM mean.
    spread    uncertainty is PROPAGATED: the latent opportunity variance is (1 + cv_volume^2)(1 + cv_share^2) - 1,
              where cv_share comes from the snap and share models' own error models; one scalar per statistic
              (kappa) calibrates it on the training seasons by maximum likelihood.

Every stage can be switched off (`config`) for the ablation study; switched off means "use what v3 used" (team
EWMA volume, EWMA shares, EWMA snap share, a constant dispersion), never "use zero".
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats as sst
from scipy.special import gammaln

from nfl_edge.engines.player.dist import LatticeDistribution
from nfl_edge.engines.player.v4 import VERSION
from nfl_edge.engines.player.v4.features import group_of
from nfl_edge.engines.player.v4.linear import Linear
from nfl_edge.engines.player.v4.snap import SnapModel
from nfl_edge.engines.player.v4.volume import VolumeModel, team_game_table

FULL = {"snap": True, "volume": True, "redistribution": True, "allocation": True, "propagate": True, "market_env": True}
STATS = ["receptions", "receiving_yards", "carries", "rushing_yards", "rush_rec_yards", "touchdowns", "attempts",
         "completions", "passing_yards", "passing_tds", "interceptions"]
GRID = {"receptions": 25, "receiving_yards": 350, "carries": 45, "rushing_yards": 350, "rush_rec_yards": 450, "touchdowns": 6,
        "attempts": 80, "completions": 60, "passing_yards": 600, "passing_tds": 10, "interceptions": 8}
TARGET_GROUPS, CARRY_GROUPS = ("RB", "WR", "TE"), ("RB", "QB", "WR")
TD_GROUPS = ("RB", "WR", "TE", "QB")
MIN_TRAIN = 300
RUSH_SHIFT = 3.0                      # a carry is Gamma - 3 yards: losses are possible, the right tail is gamma
# QUARTERBACK IDENTITY (DATA_PLAYER_V5 only; nfl_edge/engines/player/v5). With `config["qb_identity"]` the stages whose
# answer depends on WHO throws the passes also read the team-game's quarterback-identity features: team volume (a new
# starter and his efficiency relative to the previous starter), the pass-catchers' catch rate and yards per catch,
# and the starter's own attempts. V4's config has no such key, so every V4 fit, bundle sha and distribution is
# exactly what it was; the features are appended, never substituted.
QB_IDENTITY = {"volume": ("qb_new_starter", "qb_ypa_delta"), "cr": ("qb_cmp_delta",), "ypr": ("qb_ypa_delta",),
               "attempts": ("qb_new_starter", "qb_exp")}
ABSENCE = {"vac_same", "vac_other", "vac_off_same", "ret_same", "frac", "self_new", "self_returning", "n_active_same", "own_q"}


def population(df: pd.DataFrame, stat: str) -> np.ndarray:
    g = df["position"].map(group_of).to_numpy()
    qb = (g == "QB") & df.get("qb_starter", pd.Series(False, index=df.index)).fillna(False).astype(bool).to_numpy()
    if stat in ("receptions", "receiving_yards", "rush_rec_yards"):
        return np.isin(g, TARGET_GROUPS)
    if stat in ("carries", "rushing_yards"):
        return (g == "RB") | qb
    if stat == "touchdowns":
        return np.isin(g, ("RB", "WR", "TE")) | qb
    return qb


# ------------------------------------------------------------------------------------------------ features
def derive(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["pgroup"] = d["position"].map(group_of)
    e = lambda c: d[f"ewma_{c}"].astype(float)   # noqa: E731
    d["p_cr"] = (e("receptions") / e("targets").clip(lower=0.3)).clip(0.2, 1.0)
    d["p_ypr"] = (e("receiving_yards") / e("receptions").clip(lower=0.3)).clip(2.0, 25.0)
    d["p_ypc"] = (e("rushing_yards") / e("carries").clip(lower=0.3)).clip(-1.0, 10.0)
    d["p_comp"] = (e("completions") / e("attempts").clip(lower=1.0)).clip(0.4, 0.8)
    d["p_ypcomp"] = (e("passing_yards") / e("completions").clip(lower=1.0)).clip(6.0, 16.0)
    d["p_tdrate"] = (e("passing_tds") / e("attempts").clip(lower=1.0)).clip(0.0, 0.12)
    d["p_intrate"] = (e("passing_interceptions") / e("attempts").clip(lower=1.0)).clip(0.0, 0.08)
    d["n_cur_c"] = np.minimum(d["n_cur_season"].fillna(0), 4) / 4.0
    d["log_n_prior"] = np.log1p(d["n_prior"].fillna(0))
    for s in ("t", "c"):
        d[f"vac_same_{s}_frac"] = d[f"vac_same_{s}"] * d[f"self_frac_{s}"]
        d[f"vac_same_{s}_even"] = d[f"vac_same_{s}"] / d["n_active_same"].clip(lower=1)
        d[f"vac_other_{s}_role"] = d[f"vac_other_{s}"] * d[f"self_role_{s}"]
        d[f"vac_off_same_{s}_frac"] = d[f"vac_off_same_{s}"] * d[f"self_frac_{s}"]
        d[f"ret_same_{s}_frac"] = d[f"ret_same_{s}"] * (1.0 - d[f"self_frac_{s}"])
    return d


def share_features(kind: str, cfg: dict) -> list:
    base = [f"ewma_{kind}_share", f"last_{kind}_share", f"last3_{kind}_share", f"cur_mean_{kind}_share", "snap_mean", f"struct_{kind}",
            "changed_team", "n_cur_c", "log_n_prior"]
    s = "t" if kind == "target" else "c"
    red = ["own_q", "self_new", "self_returning", f"vac_same_{s}", f"vac_same_{s}_frac", f"vac_same_{s}_even", f"vac_other_{s}_role",
           f"vac_off_same_{s}_frac", f"ret_same_{s}", f"ret_same_{s}_frac"]
    return base + (red if cfg["redistribution"] else [])


def _env(cols: list, cfg: dict) -> list:
    return cols if cfg["market_env"] else [c for c in cols if c not in ("implied_total", "spread_team")]


def _qbx(cols: list, cfg: dict, stage: str) -> list:
    """`cols` plus the stage's quarterback-identity features when the bundle is a V5 bundle (see QB_IDENTITY)."""
    return list(cols) + list(QB_IDENTITY[stage]) if cfg.get("qb_identity") else cols


# ------------------------------------------------------------------------------------------------ distributions
def nb_pmf(mu: float, r: float, nmax: int) -> np.ndarray:
    k = np.arange(nmax + 1)
    mu = max(float(mu), 1e-6)
    if not np.isfinite(r) or r > 1e6:
        lp = k * np.log(mu) - mu - gammaln(k + 1)
    else:
        p = r / (r + mu)
        lp = gammaln(k + r) - gammaln(r) - gammaln(k + 1) + r * np.log(p) + k * np.log1p(-p)
    pm = np.exp(lp)
    pm[-1] += max(0.0, 1.0 - pm.sum())
    return pm / pm.sum()


def nb_loglik(y, mu, r) -> np.ndarray:
    y = np.asarray(y, float); mu = np.maximum(np.asarray(mu, float), 1e-6); r = np.asarray(r, float)
    return gammaln(y + r) - gammaln(r) - gammaln(y + 1) + r * np.log(r / (r + mu)) + y * np.log(mu / (r + mu))


def compound_survival(pn: np.ndarray, a_per: float, theta: float, shift: float, gmax: int) -> np.ndarray:
    """S[k] = P(sum of N iid (Gamma(a_per, theta) - shift) >= k), N ~ pn, on 0..gmax (negative totals fold into 0)."""
    n = np.arange(1, len(pn))
    keep = pn[1:] > 1e-10
    S = np.zeros(gmax)
    if keep.any():
        nn = n[keep]
        x = (np.arange(1, gmax + 1) - 0.5)[None, :] + shift * nn[:, None]
        S = pn[1:][keep] @ sst.gamma.sf(x, a=a_per * nn[:, None], scale=theta)
    return np.concatenate([[1.0], S])


def fit_shape(y, mu, cv2=None) -> float:
    """kappa (propagated: r = 1 / (kappa * cv2)) or a constant NB shape r, by maximum likelihood on a log grid."""
    grid = np.exp(np.linspace(np.log(0.05), np.log(50.0), 70))
    best, arg = -np.inf, grid[0]
    for g in grid:
        r = (1.0 / (g * np.maximum(cv2, 1e-4))) if cv2 is not None else np.full(len(y), g)
        ll = nb_loglik(y, mu, np.minimum(r, 1e6)).sum()
        if ll > best:
            best, arg = ll, g
    return float(arg)


def compound_dispersion(y, n, m) -> float:
    """Per-unit gamma shape k from E[Y|n] = n m, Var[Y|n] = n m^2 / k (method of moments over training rows)."""
    ok = (n > 0) & np.isfinite(y) & np.isfinite(m) & (m > 0)
    num = (n[ok] * m[ok] ** 2).sum(); den = ((y[ok] - n[ok] * m[ok]) ** 2).sum()
    return float(np.clip(num / max(den, 1e-6), 0.2, 20.0))


# ------------------------------------------------------------------------------------------------ bundle
@dataclass
class V4Bundle:
    target_season: int
    config: dict
    version: str = VERSION
    snap: SnapModel | None = None
    volume: VolumeModel | None = None
    share: dict = field(default_factory=dict)          # (kind, group) -> Linear
    share_spread: dict = field(default_factory=dict)   # (kind, group) -> Linear on |resid|
    stack: dict = field(default_factory=dict)          # (kind, group) -> Linear poisson
    kappa: dict = field(default_factory=dict)          # (stat-ish, group) -> kappa or constant r
    rate: dict = field(default_factory=dict)           # (name, group) -> Linear
    unit: dict = field(default_factory=dict)           # (name, group) -> per-unit gamma shape / params
    info: dict = field(default_factory=dict)
    artifact_sha: str = ""

    # -------------------------------------------------------------------------------------- stage predictions
    def _snap(self, d):
        if self.config["snap"]:
            p = self.snap.predict(d)
            d["snap_mean"], d["snap_sd"] = p["snap_mean"].to_numpy(), p["snap_sd"].to_numpy()
        else:
            d["snap_mean"] = d["ewma_snap_share"].clip(0.005, 0.995)
            d["snap_sd"] = self.info.get("snap_sd_pooled", 0.2)
        return d

    def _volume(self, d, teams):
        v = self.volume.predict(teams)
        d = d.drop(columns=[c for c in ("vol_pa", "vol_ra", "vol_pa_sd", "vol_ra_sd") if c in d.columns])
        return d.merge(v, on=["team", "game_id"], how="left")

    def _shares(self, d):
        for kind, s, groups in (("target", "t", TARGET_GROUPS), ("carry", "c", CARRY_GROUPS)):
            ratio = d[f"ewma_{kind}_share"] / d["ewma_snap_share"].clip(lower=0.05)
            d[f"struct_{kind}"] = (ratio * d["snap_mean"]).clip(0, 1)
            mean = d[f"ewma_{kind}_share"].to_numpy(float).copy(); sd = np.full(len(d), np.nan)
            g = d["pgroup"].to_numpy()
            for grp in groups:
                ix = np.where(g == grp)[0]
                if not len(ix):
                    continue
                m = self.share.get((kind, grp))
                if m is not None and self.config["allocation"]:
                    mean[ix] = m.predict(d.iloc[ix])
                sp = self.share_spread.get((kind, grp))
                if sp is not None:
                    sd[ix] = np.clip(sp.predict(d.iloc[ix]), 0.005, 0.4) * np.sqrt(np.pi / 2)
            d[f"share_{s}"] = np.clip(mean, 0.0, 0.7)
            d[f"share_{s}_sd"] = sd
        # reconciliation: the shares of one team-game cannot exceed the team's total
        for s in ("t", "c"):
            tot = d.groupby(["team", "game_id"])[f"share_{s}"].transform("sum")
            d[f"recon_{s}_sum"] = tot
            d[f"share_{s}"] = np.where(tot > 1.0, d[f"share_{s}"] / tot, d[f"share_{s}"])
        return d

    def _counts(self, d):
        for kind, s, vol, raw, groups in (("target", "t", "vol_pa", "targets", TARGET_GROUPS), ("carry", "c", "vol_ra", "carries", CARRY_GROUPS)):
            d[f"struct_{raw}"] = d[vol] * d[f"share_{s}"]
            d[f"l_struct_{raw}"] = np.log(d[f"struct_{raw}"].clip(lower=0) + 0.2)
            d[f"l_ewma_{raw}"] = np.log(d[f"ewma_{raw}"].clip(lower=0) + 0.2)
            mu = d[f"struct_{raw}"].to_numpy(float).copy()
            g = d["pgroup"].to_numpy()
            for grp in groups:
                ix = np.where(g == grp)[0]
                m = self.stack.get((kind, grp))
                if m is not None and len(ix):
                    mu[ix] = m.predict(d.iloc[ix])
            d[f"mu_{raw}"] = np.maximum(mu, 0.01)
            # latent coefficient of variation of the opportunity: volume x share, both uncertain
            cvv = (d[f"{vol}_sd"] / d[vol].clip(lower=1)) ** 2
            sh = d[f"share_{s}"].clip(lower=0.005)
            samp = sh * (1 - sh) / d[vol].clip(lower=1)
            lat = np.maximum(d[f"share_{s}_sd"].fillna(0.1) ** 2 - samp, (0.1 * sh) ** 2)
            d[f"cv2_{raw}"] = (1 + cvv) * (1 + lat / sh ** 2) - 1
        return d

    def _rates(self, d):
        g = d["pgroup"].to_numpy()
        for name, default in (("cr", 0.65), ("ypr", 10.0), ("ypc", 4.2), ("comp", 0.64), ("ypcomp", 11.0)):
            out = np.full(len(d), default)
            for (nm, grp), m in self.rate.items():
                if nm != name:
                    continue
                ix = np.where(g == grp)[0]
                if len(ix):
                    out[ix] = m.predict(d.iloc[ix])
            d[f"r_{name}"] = out
        d["r_cr"] = d["r_cr"].clip(0.3, 0.95); d["r_ypr"] = d["r_ypr"].clip(3, 25); d["r_ypc"] = d["r_ypc"].clip(0.5, 9)
        d["r_comp"] = d["r_comp"].clip(0.45, 0.8); d["r_ypcomp"] = d["r_ypcomp"].clip(7, 16)
        d["mu_receptions"] = d["mu_targets"] * d["r_cr"]
        # QB attempts first (TD / INT means are conditional on them), then anytime TD from the opportunity means
        def glm(name):
            out = np.full(len(d), np.nan)
            for (nm, grp), m in self.rate.items():
                if nm == name:
                    ix = np.where(g == grp)[0]
                    if len(ix):
                        out[ix] = m.predict(d.iloc[ix])
            return out
        d["mu_attempts"] = glm("attempts")
        d["l_att"] = np.log(np.where(np.isfinite(d["mu_attempts"]), d["mu_attempts"], 30.0))
        d["mu_passing_tds"] = glm("passing_tds")
        d["mu_interceptions"] = glm("interceptions")
        d["l_mu_t"] = np.log(d["mu_targets"].fillna(0) + 0.05)
        d["l_mu_c"] = np.log(d["mu_carries"].fillna(0) + 0.05)
        d["mu_any_td"] = glm("any_td")
        return d

    def intermediates(self, rows: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
        d = derive(rows)
        d = self._snap(d)
        d = self._volume(d, teams)
        d = self._shares(d)
        d = self._counts(d)
        d = self._rates(d)
        return d

    # -------------------------------------------------------------------------------------- distributions
    def _r(self, key, grp, cv2) -> float:
        k = self.kappa.get((key, grp))
        if k is None:
            return 10.0
        if self.config["propagate"] and key in ("targets", "carries"):
            return float(1.0 / (k * max(cv2, 1e-4)))
        return float(k)

    def distributions(self, row: dict, stats=None) -> dict:
        """One (player, game) row of `intermediates` -> {stat: LatticeDistribution} for the stats in its population."""
        out = {}
        grp = row["pgroup"]
        stats = stats or STATS
        qb = grp == "QB" and bool(row.get("qb_starter"))
        rec_ok = grp in TARGET_GROUPS and np.isfinite(row.get("mu_targets", np.nan))
        car_ok = (grp == "RB" or qb) and np.isfinite(row.get("mu_carries", np.nan))
        meta = {"version": self.version, "snap_mean": row.get("snap_mean"), "snap_sd": row.get("snap_sd"), "vol_pa": row.get("vol_pa"),
                "vol_ra": row.get("vol_ra"), "share_t": row.get("share_t"), "share_c": row.get("share_c")}
        pm_rec = pm_car = None
        if rec_ok:
            r_t = self._r("targets", grp, row["cv2_targets"])
            cr = row["r_cr"]
            # binomial thinning of a NB keeps its shape: receptions ~ NB(r_t, mu_targets * cr)
            pm_rec = nb_pmf(row["mu_targets"] * cr, r_t, GRID["receptions"])
            if "receptions" in stats:
                out["receptions"] = LatticeDistribution(pm_rec, meta={**meta, "stat": "receptions", "mu": row["mu_targets"] * cr, "r": r_t,
                                                                         "mu_targets": row["mu_targets"], "catch_rate": cr}, normalize=True)
            k = self.unit.get(("ypr", grp), 1.0)
            S = compound_survival(pm_rec, k, row["r_ypr"] / k, 0.0, GRID["receiving_yards"])
            if "receiving_yards" in stats or "rush_rec_yards" in stats:
                out["receiving_yards"] = LatticeDistribution.from_survival(S, meta={**meta, "stat": "receiving_yards", "ypr": row["r_ypr"], "k_unit": k,
                                                                                    "mu": float((pm_rec * np.arange(len(pm_rec))).sum() * row["r_ypr"])})
        if car_ok:
            r_c = self._r("carries", grp, row["cv2_carries"])
            pm_car = nb_pmf(row["mu_carries"], r_c, GRID["carries"])
            if "carries" in stats:
                out["carries"] = LatticeDistribution(pm_car, meta={**meta, "stat": "carries", "mu": row["mu_carries"], "r": r_c}, normalize=True)
            sig2 = self.unit.get(("ypc_var", grp), 30.0)
            m = row["r_ypc"] + RUSH_SHIFT
            a, th = m * m / sig2, sig2 / m
            S = compound_survival(pm_car, a, th, RUSH_SHIFT, GRID["rushing_yards"])
            if "rushing_yards" in stats or "rush_rec_yards" in stats:
                out["rushing_yards"] = LatticeDistribution.from_survival(S, meta={**meta, "stat": "rushing_yards", "ypc": row["r_ypc"],
                                                                                  "mu": float(row["mu_carries"] * row["r_ypc"])})
        if "rush_rec_yards" in stats and "receiving_yards" in out and grp in TARGET_GROUPS:
            ry = out.get("rushing_yards")
            if ry is None and np.isfinite(row.get("mu_carries", np.nan)) and row["mu_carries"] > 0.05:
                # WR / TE rushing: the same carry chain at the group's per-carry parameters
                pm = nb_pmf(row["mu_carries"], self._r("carries", grp, row.get("cv2_carries", 1.0)), GRID["carries"])
                sig2 = self.unit.get(("ypc_var", grp), self.unit.get(("ypc_var", "RB"), 30.0))
                m = row["r_ypc"] + RUSH_SHIFT
                ry = LatticeDistribution.from_survival(compound_survival(pm, m * m / sig2, sig2 / m, RUSH_SHIFT, GRID["rushing_yards"]))
            pmf = out["receiving_yards"].pmf if ry is None else np.convolve(out["receiving_yards"].pmf, ry.pmf)
            pmf = pmf[: GRID["rush_rec_yards"] + 1].copy(); pmf[-1] += max(0.0, 1 - pmf.sum())
            out["rush_rec_yards"] = LatticeDistribution(pmf, meta={**meta, "stat": "rush_rec_yards"}, normalize=True)
        if "touchdowns" in stats and np.isfinite(row.get("mu_any_td", np.nan)) and (grp in ("RB", "WR", "TE") or qb):
            r = self._r("any_td", grp, 0)
            out["touchdowns"] = LatticeDistribution(nb_pmf(row["mu_any_td"], r, GRID["touchdowns"]),
                                                    meta={**meta, "stat": "touchdowns", "mu": row["mu_any_td"], "r": r}, normalize=True)
        if qb and np.isfinite(row.get("mu_attempts", np.nan)):
            r_a = self._r("attempts", "QB", 0)
            pm_att = nb_pmf(row["mu_attempts"], r_a, GRID["attempts"])
            if "attempts" in stats:
                out["attempts"] = LatticeDistribution(pm_att, meta={**meta, "stat": "attempts", "mu": row["mu_attempts"], "r": r_a}, normalize=True)
            pm_cmp = nb_pmf(row["mu_attempts"] * row["r_comp"], r_a, GRID["completions"])
            if "completions" in stats:
                out["completions"] = LatticeDistribution(pm_cmp, meta={**meta, "stat": "completions", "mu": row["mu_attempts"] * row["r_comp"]}, normalize=True)
            if "passing_yards" in stats:
                k = self.unit.get(("ypcomp", "QB"), 1.0)
                S = compound_survival(pm_cmp, k, row["r_ypcomp"] / k, 0.0, GRID["passing_yards"])
                out["passing_yards"] = LatticeDistribution.from_survival(S, meta={**meta, "stat": "passing_yards", "ypcomp": row["r_ypcomp"]})
            for st, key in (("passing_tds", "passing_tds"), ("interceptions", "interceptions")):
                if st in stats and np.isfinite(row.get(f"mu_{key}", np.nan)):
                    r = self._r(key, "QB", 0)
                    out[st] = LatticeDistribution(nb_pmf(row[f"mu_{key}"], r, GRID[st]), meta={**meta, "stat": st, "mu": row[f"mu_{key}"], "r": r}, normalize=True)
        return {k: v for k, v in out.items() if k in stats}

    # -------------------------------------------------------------------------------------- identity
    def sha(self) -> str:
        payload = {"version": self.version, "target_season": self.target_season, "config": self.config, "info": self.info}
        self.artifact_sha = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]
        return self.artifact_sha

    def summary(self) -> dict:
        return {"version": self.version, "artifact_sha": self.artifact_sha, "target_season": self.target_season, "config": self.config,
                "info": self.info, "kappa": {f"{k[0]}|{k[1]}": round(v, 4) for k, v in self.kappa.items()},
                "unit": {f"{k[0]}|{k[1]}": round(v, 4) for k, v in self.unit.items()},
                "snap": self.snap.summary() if self.snap else None, "volume": self.volume.summary() if self.volume else None}


# ------------------------------------------------------------------------------------------------ fitting
def fit_bundle(frame: pd.DataFrame, target_season: int, config: dict | None = None, *, first_season: int = 2014,
               teams: pd.DataFrame | None = None, verbose=print, version: str | None = None) -> V4Bundle:
    """frame: the player-game table with v2/v3 and v4 (features.py) columns; prospective rows allowed (ignored in fits).

    version: the engine version stamped on the bundle and every distribution it makes (DATA_PLAYER_V5 passes its own;
    None is V4's)."""
    cfg = {**FULL, **(config or {})}
    b = V4Bundle(target_season=target_season, config=cfg, version=version or VERSION)
    teams = team_game_table(frame) if teams is None else teams
    pro = frame.get("is_prospective", pd.Series(False, index=frame.index)).fillna(False).astype(bool)
    tr = frame[(~pro) & (frame.season < target_season) & (frame.season >= first_season)].copy()
    tr = tr[tr["offense_snaps"].fillna(0) > 0]
    # -- snap
    if cfg["snap"]:
        b.snap = SnapModel.fit(tr, exclude=(set() if cfg["redistribution"] else ABSENCE))
    b.info["snap_sd_pooled"] = float(np.std(tr["snap_share"] - tr["ewma_snap_share"]))
    # -- volume
    vcfg_env = cfg["market_env"]
    b.volume = VolumeModel.fit(teams, target_season, ablate=not cfg["volume"], market_env=vcfg_env,
                               extra=tuple(QB_IDENTITY["volume"]) if cfg.get("qb_identity") else ())
    d = b._snap(derive(tr))
    d = b._volume(d, teams)
    # realised shares vs the ACTUAL team volume (targets / team pass attempts, as v2 defines them)
    g = d["pgroup"].to_numpy()
    for kind, s, groups in (("target", "t", TARGET_GROUPS), ("carry", "c", CARRY_GROUPS)):
        ratio = d[f"ewma_{kind}_share"] / d["ewma_snap_share"].clip(lower=0.05)
        d[f"struct_{kind}"] = (ratio * d["snap_mean"]).clip(0, 1)
        cols = share_features(kind, cfg)
        for grp in groups:
            sub = d[(g == grp) & d[f"{kind}_share"].notna()]
            if len(sub) < MIN_TRAIN:
                continue
            y = sub[f"{kind}_share"].clip(0, 1).to_numpy(float)
            m = Linear.fit(sub, cols, y) if cfg["allocation"] else Linear([f"ewma_{kind}_share"], np.array([0.0, 1.0]), np.zeros(1), np.ones(1))
            b.share[(kind, grp)] = m
            b.share_spread[(kind, grp)] = Linear.fit(sub, cols if cfg["propagate"] else [], np.abs(y - np.clip(m.predict(sub), 0, 0.7)))
    d = b._shares(d)
    # -- stacked counts (structure + raw EWMA)
    for kind, raw, vol, groups in (("target", "targets", "vol_pa", TARGET_GROUPS), ("carry", "carries", "vol_ra", CARRY_GROUPS)):
        s = "t" if kind == "target" else "c"
        d[f"l_struct_{raw}"] = np.log((d[vol] * d[f"share_{s}"]).clip(lower=0) + 0.2)
        d[f"l_ewma_{raw}"] = np.log(d[f"ewma_{raw}"].clip(lower=0) + 0.2)
        for grp in groups:
            sub = d[(g == grp) & d[raw].notna()]
            if len(sub) < MIN_TRAIN:
                continue
            b.stack[(kind, grp)] = Linear.fit(sub, [f"l_struct_{raw}", f"l_ewma_{raw}"], sub[raw].to_numpy(float), kind="poisson")
    d = b._counts(d)
    # -- dispersion of targets / carries (kappa when propagated, a constant shape otherwise)
    for raw, groups in (("targets", TARGET_GROUPS), ("carries", CARRY_GROUPS)):
        for grp in groups:
            sub = d[(g == grp) & d[raw].notna() & np.isfinite(d[f"mu_{raw}"])]
            if len(sub) < MIN_TRAIN:
                continue
            b.kappa[(raw, grp)] = fit_shape(sub[raw].to_numpy(float), sub[f"mu_{raw}"].to_numpy(float),
                                            sub[f"cv2_{raw}"].to_numpy(float) if cfg["propagate"] else None)
    # -- efficiency rates
    env = lambda cols: _env(cols, cfg)   # noqa: E731
    for grp in TARGET_GROUPS:
        sub = d[(g == grp) & (d["targets"].fillna(0) > 0)]
        if len(sub) >= MIN_TRAIN:
            b.rate[("cr", grp)] = Linear.fit(sub, _qbx(env(["p_cr", "implied_total", "log_n_prior"]), cfg, "cr"), (sub.receptions / sub.targets).to_numpy(float),
                                             weights=sub.targets.to_numpy(float))
        sub = d[(g == grp) & (d["receptions"].fillna(0) > 0)]
        if len(sub) >= MIN_TRAIN:
            b.rate[("ypr", grp)] = Linear.fit(sub, _qbx(env(["p_ypr", "ewma_team_ypa", "implied_total"]), cfg, "ypr"), (sub.receiving_yards / sub.receptions).to_numpy(float),
                                              weights=sub.receptions.to_numpy(float))
            m = np.clip(b.rate[("ypr", grp)].predict(sub), 3, 25)
            b.unit[("ypr", grp)] = compound_dispersion(sub.receiving_yards.to_numpy(float), sub.receptions.to_numpy(float), m)
    for grp in CARRY_GROUPS:
        mask = (g == grp) & (d["carries"].fillna(0) > 0)
        if grp == "QB":
            mask &= d["qb_starter"].fillna(False).astype(bool).to_numpy()
        sub = d[mask]
        if len(sub) >= MIN_TRAIN:
            b.rate[("ypc", grp)] = Linear.fit(sub, env(["p_ypc", "implied_total", "spread_team"]), (sub.rushing_yards / sub.carries).to_numpy(float),
                                              weights=sub.carries.to_numpy(float))
            m = b.rate[("ypc", grp)].predict(sub)
            res = sub.rushing_yards.to_numpy(float) - sub.carries.to_numpy(float) * m
            b.unit[("ypc_var", grp)] = float(np.clip((res ** 2).sum() / sub.carries.sum(), 5.0, 150.0))
    # -- quarterbacks (starters)
    qb = d[(g == "QB") & d["qb_starter"].fillna(False).astype(bool) & d["attempts"].notna()]
    if len(qb) >= MIN_TRAIN:
        qcols = _qbx(env(["vol_pa", "ewma_attempts", "snap_mean", "qb_changed_recent", "implied_total", "spread_team"]), cfg, "attempts")
        b.rate[("attempts", "QB")] = Linear.fit(qb, qcols, qb.attempts.to_numpy(float), kind="poisson")
        mu = b.rate[("attempts", "QB")].predict(qb)
        b.kappa[("attempts", "QB")] = fit_shape(qb.attempts.to_numpy(float), mu)
        sub = qb[qb.attempts > 0]
        b.rate[("comp", "QB")] = Linear.fit(sub, env(["p_comp", "implied_total", "spread_team"]), (sub.completions / sub.attempts).to_numpy(float),
                                            weights=sub.attempts.to_numpy(float))
        sub = qb[qb.completions > 0]
        b.rate[("ypcomp", "QB")] = Linear.fit(sub, env(["p_ypcomp", "ewma_team_ypa", "implied_total"]), (sub.passing_yards / sub.completions).to_numpy(float),
                                              weights=sub.completions.to_numpy(float))
        m = np.clip(b.rate[("ypcomp", "QB")].predict(sub), 7, 16)
        b.unit[("ypcomp", "QB")] = compound_dispersion(sub.passing_yards.to_numpy(float), sub.completions.to_numpy(float), m)
        qb = qb.assign(l_att=np.log(mu))
        for name, col, cols in (("passing_tds", "passing_tds", ["l_att", "p_tdrate", "ewma_passing_tds", "implied_total"]),
                                ("interceptions", "passing_interceptions", ["l_att", "p_intrate", "spread_team", "implied_total"])):
            b.rate[(name, "QB")] = Linear.fit(qb, env(cols), qb[col].to_numpy(float), kind="poisson")
            b.kappa[(name, "QB")] = fit_shape(qb[col].to_numpy(float), b.rate[(name, "QB")].predict(qb))
    # -- anytime TD
    d["l_mu_t"] = np.log(d["mu_targets"].fillna(0) + 0.05); d["l_mu_c"] = np.log(d["mu_carries"].fillna(0) + 0.05)
    for grp in TD_GROUPS:
        mask = (g == grp) & d["any_td"].notna()
        if grp == "QB":
            mask &= d["qb_starter"].fillna(False).astype(bool).to_numpy()
        sub = d[mask]
        if len(sub) >= MIN_TRAIN:
            b.rate[("any_td", grp)] = Linear.fit(sub, env(["l_mu_t", "l_mu_c", "implied_total", "ewma_any_td"]), sub.any_td.to_numpy(float), kind="poisson")
            b.kappa[("any_td", grp)] = fit_shape(sub.any_td.to_numpy(float), b.rate[("any_td", grp)].predict(sub))
    b.info.update({"n_train_rows": int(len(tr)), "train_seasons": [int(tr.season.min()), int(tr.season.max())],
                   "volume": b.volume.info, "recon_t_over_1": float((d["recon_t_sum"] > 1).mean()),
                   "recon_c_over_1": float((d["recon_c_sum"] > 1).mean())})
    b.sha()
    verbose(f"  v4 bundle {b.artifact_sha}: {b.info['n_train_rows']} rows {b.info['train_seasons']} config {cfg}")
    return b
