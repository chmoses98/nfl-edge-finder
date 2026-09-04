"""Milestone F: conditional distribution families for player-prop ladders.

Kalshi lists player-prop ladders ("receiving yards 40+/50+/.../120+", "receptions 3+/4+",
"passing TDs 1+/2+/3+", anytime TD ...). We need calibrated P(Y >= k) for every rung, so
the question is: given a (weak, point-in-time) projection mu of the stat and of the
opportunity (targets / carries / attempts), which distribution family for Y | mu gives the
best-calibrated ladder probabilities?

Everything here is leakage-free by construction:
  * projection features are exponentially weighted means over the player's PRIOR games
    (strictly earlier (season, week)), with a discount at season boundaries and shrinkage
    toward a fixed position prior estimated on seasons before the research window;
  * game context is the pre-game market line (spread/total from the schedule);
  * families are fit on seasons < S and evaluated on season S (walk-forward).

Design: every family exposes ``cdf_grid(mu, opp, eff, grid) -> (n, len(grid))`` giving
P(Y <= k) at each integer k of ``grid``.  All outcomes are integers, so every family (even
continuous ones) is discretised to the integer lattice via F(k + 0.5) - this makes CRPS,
log score, PIT and ladder probabilities P(Y >= k) = 1 - F(k - 1) directly comparable across
continuous, count and Monte-Carlo families.  Outcomes are clipped at 0 (negative yardage
games are rare and irrelevant for ladders that start at 20+); continuous families are
censored at 0 accordingly.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import polars as pl
from scipy import optimize, special, stats

SKILL_POS = ["QB", "RB", "WR", "TE"]
BASE_STATS = [
    "attempts", "completions", "passing_yards", "passing_tds", "passing_interceptions",
    "carries", "rushing_yards", "rushing_tds",
    "targets", "receptions", "receiving_yards", "receiving_tds",
    "any_td", "touches", "offense_snaps",
]

# ------------------------------------------------------------------------------------ specs
@dataclass
class StatSpec:
    name: str
    col: str                # outcome column in the research table
    pop: str                # population: QB (designated starters), REC (RB/WR/TE), RB, SKILL
    opp: str                # opportunity column (base stat name)
    kind: str               # yards | count | td
    thresholds: list        # Kalshi-style ladder rungs (YES pays if Y >= k)
    eff: str | None = None  # efficiency ratio feature (for two-stage MC)
    eff_kind: str | None = None  # gamma (yards per opp) | binom (success per opp)
    elig_min_opp: float = 0.0    # projected opportunity needed to count as "prop-relevant"
    grid_max: int = 80


STAT_SPECS: dict[str, StatSpec] = {s.name: s for s in [
    StatSpec("attempts", "attempts", "QB", "attempts", "count", list(range(15, 51, 5)), elig_min_opp=0, grid_max=80),
    StatSpec("completions", "completions", "QB", "attempts", "count", list(range(10, 36, 5)), "comp_rate", "binom", 0, 60),
    StatSpec("passing_yards", "passing_yards", "QB", "attempts", "yards", list(range(150, 401, 25)), "ypa", "gamma", 0, 600),
    StatSpec("passing_tds", "passing_tds", "QB", "attempts", "td", [1, 2, 3], "ptd_rate", "binom", 0, 10),
    StatSpec("interceptions", "passing_interceptions", "QB", "attempts", "td", [1, 2], "int_rate", "binom", 0, 8),
    StatSpec("qb_rushing_yards", "rushing_yards", "QB", "carries", "yards", list(range(20, 101, 10)), "ypc", "gamma", 0, 250),
    StatSpec("targets", "targets", "REC", "targets", "count", list(range(1, 13)), elig_min_opp=3.0, grid_max=30),
    StatSpec("receptions", "receptions", "REC", "targets", "count", list(range(1, 11)), "catch_rate", "binom", 3.0, 25),
    StatSpec("receiving_yards", "receiving_yards", "REC", "targets", "yards", list(range(20, 151, 10)), "ypt", "gamma", 3.0, 350),
    StatSpec("receiving_tds", "receiving_tds", "REC", "targets", "td", [1, 2, 3], "rtd_rate", "binom", 3.0, 6),
    StatSpec("carries", "carries", "RB", "carries", "count", list(range(4, 25, 2)), elig_min_opp=6.0, grid_max=45),
    StatSpec("rushing_yards", "rushing_yards", "RB", "carries", "yards", list(range(20, 151, 10)), "ypc", "gamma", 6.0, 350),
    StatSpec("rushing_tds", "rushing_tds", "RB", "carries", "td", [1, 2, 3], "rushtd_rate", "binom", 6.0, 6),
    StatSpec("anytime_td", "any_td", "SKILL", "touches", "td", [1, 2, 3], "anytd_rate", "binom", 6.0, 6),
]}

FAMILIES_BY_KIND = {
    "yards": ["normal", "hurdle_lognormal", "hurdle_gamma", "negbin", "scale_emp", "scale_emp_binned", "two_stage_mc"],
    "count": ["normal", "poisson", "negbin", "scale_emp", "scale_emp_binned", "two_stage_mc"],
    "td": ["normal", "poisson", "negbin", "scale_emp", "scale_emp_binned", "two_stage_mc"],
}


# ------------------------------------------------------------------------------ data loading
def _read_stats(root: str, seasons) -> pl.DataFrame:
    frames = []
    for s in seasons:
        p = os.path.join(root, "data/raw/nflverse/stats_player", f"stats_player_week_{s}.parquet")
        frames.append(pl.read_parquet(p).filter(pl.col("season_type") == "REG"))
    st = pl.concat(frames, how="diagonal_relaxed")
    keep = ["player_id", "player_display_name", "position", "season", "week", "game_id", "team", "opponent_team",
            "completions", "attempts", "passing_yards", "passing_tds", "passing_interceptions",
            "carries", "rushing_yards", "rushing_tds", "receptions", "targets", "receiving_yards", "receiving_tds"]
    st = st.select(keep).filter(pl.col("position").is_in(SKILL_POS))
    st = st.unique(subset=["player_id", "game_id"], keep="first")
    return st


def _read_snaps(root: str, seasons) -> pl.DataFrame:
    frames = []
    for s in seasons:
        p = os.path.join(root, "data/raw/nflverse/snap_counts", f"snap_counts_{s}.parquet")
        if os.path.exists(p):
            frames.append(pl.read_parquet(p).filter(pl.col("game_type") == "REG"))
    sc = pl.concat(frames, how="diagonal_relaxed")
    cw = (pl.read_parquet(os.path.join(root, "data/silver/player_crosswalk.parquet"))
          .select(["gsis_id", "pfr_id"]).drop_nulls().unique(subset=["pfr_id"], keep="first"))
    sc = sc.join(cw, left_on="pfr_player_id", right_on="pfr_id", how="inner")
    sc = sc.select(["gsis_id", "game_id", "season", "week", "team", "opponent", "position", "player", "offense_snaps"])
    sc = sc.filter(pl.col("position").is_in(SKILL_POS)).unique(subset=["gsis_id", "game_id"], keep="first")
    return sc


def load_player_games(root: str, seasons, add_zero_rows: bool = True) -> pd.DataFrame:
    """Player-game rows for skill positions with outcome stats and pre-game market context.

    Adds explicit zero rows for players who took >=1 offensive snap (snap counts) but have no
    stats row (nflverse only lists players who recorded something).  Returns pandas, sorted by
    (player_id, season, week)."""
    st = _read_stats(root, seasons)
    sc = _read_snaps(root, seasons)
    st = st.join(sc.select(["gsis_id", "game_id", "offense_snaps"]),
                 left_on=["player_id", "game_id"], right_on=["gsis_id", "game_id"], how="left")
    st = st.with_columns(pl.lit(False).alias("zero_row"))
    n_zero = 0
    if add_zero_rows:
        missing = sc.filter(pl.col("offense_snaps") > 0).join(
            st.select(["player_id", "game_id"]).with_columns(pl.lit(True).alias("_has")),
            left_on=["gsis_id", "game_id"], right_on=["player_id", "game_id"], how="left"
        ).filter(pl.col("_has").is_null())
        zero = missing.select([
            pl.col("gsis_id").alias("player_id"), pl.col("player").alias("player_display_name"),
            pl.col("position"), pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32), pl.col("game_id"),
            pl.col("team"), pl.col("opponent").alias("opponent_team"),
        ] + [pl.lit(0, dtype=pl.Int32).alias(c) for c in ["completions", "attempts", "passing_yards", "passing_tds",
                                                          "passing_interceptions", "carries", "rushing_yards", "rushing_tds",
                                                          "receptions", "targets", "receiving_yards", "receiving_tds"]]
          + [pl.col("offense_snaps"), pl.lit(True).alias("zero_row")])
        n_zero = zero.height
        st = pl.concat([st.with_columns(pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32)), zero],
                       how="diagonal_relaxed")
    games = pl.read_parquet(os.path.join(root, "data/silver/games.parquet")).select(
        ["game_id", "home_team", "away_team", "spread_line", "total_line", "home_qb_id", "away_qb_id", "roof"])
    st = st.join(games, on="game_id", how="inner")
    st = st.with_columns([
        (pl.col("team") == pl.col("home_team")).alias("home"),
        pl.when(pl.col("team") == pl.col("home_team")).then(pl.col("spread_line")).otherwise(-pl.col("spread_line")).alias("spread_team"),
    ]).with_columns([
        ((pl.col("total_line") + pl.col("spread_team")) / 2).alias("implied_total"),
        ((pl.col("team") == pl.col("home_team")) & (pl.col("player_id") == pl.col("home_qb_id"))
         | (pl.col("team") == pl.col("away_team")) & (pl.col("player_id") == pl.col("away_qb_id"))).alias("qb_starter"),
        (pl.col("rushing_tds") + pl.col("receiving_tds")).alias("any_td"),
        (pl.col("targets") + pl.col("carries")).alias("touches"),
        (pl.col("roof").is_in(["dome", "closed"])).alias("indoor"),
    ]).drop(["home_team", "away_team", "home_qb_id", "away_qb_id", "roof"])
    df = st.to_pandas().sort_values(["player_id", "season", "week"]).reset_index(drop=True)
    df.attrs["n_zero_rows"] = n_zero
    return df


# --------------------------------------------------------------------------- EWMA projections
def position_priors(df: pd.DataFrame, seasons) -> dict[str, np.ndarray]:
    """Per-position mean of BASE_STATS over the given (pre-window) seasons -> prior vectors."""
    sub = df[df.season.isin(list(seasons))]
    out = {}
    for pos, g in sub.groupby("position"):
        out[pos] = np.nan_to_num(g[BASE_STATS].astype(float).mean().to_numpy(), nan=0.0)
    return out


def add_ewma_features(df: pd.DataFrame, halflife: float = 5.0, season_carry: float = 0.5, shrink_k: float = 3.0,
                      priors: dict[str, np.ndarray] | None = None) -> pd.DataFrame:
    """Point-in-time EWMA of every BASE_STAT over the player's PRIOR games only.

    Recursion per player (games in chronological order):  S <- d*S + y,  W <- d*W + 1 with
    d = 0.5**(1/halflife); at a season boundary S, W are additionally multiplied by
    ``season_carry``.  The feature recorded BEFORE the update is
        ewma = (S + k*prior) / (W + k)
    i.e. a precision-weighted shrink toward the position prior with k pseudo-games.
    Also records n_prior (unweighted prior game count), w_eff (W) and shrink_w = k/(W+k)."""
    df = df.copy()
    X = df[BASE_STATS].to_numpy(dtype=float)
    pid = df.player_id.to_numpy()
    season = df.season.to_numpy()
    pos = df.position.to_numpy()
    n, m = X.shape
    d = 0.5 ** (1.0 / halflife)
    out = np.full((n, m), np.nan)
    n_prior = np.zeros(n, dtype=int)
    w_eff = np.zeros(n)
    default_prior = np.zeros(m)
    S = np.zeros(m); W = np.zeros(m); cur = None; last_season = None; cnt = 0
    for i in range(n):
        p = pid[i]
        if p != cur:
            cur = p; S = np.zeros(m); W = np.zeros(m); cnt = 0; last_season = season[i]
        elif season[i] != last_season:
            c = season_carry ** (season[i] - last_season)
            S = S * c; W = W * c; last_season = season[i]
        pr = priors.get(pos[i], default_prior) if priors else default_prior
        out[i] = (S + shrink_k * pr) / (W + shrink_k)
        n_prior[i] = cnt
        w_eff[i] = W[0]
        v = X[i]; msk = np.isfinite(v)
        S = S * d; W = W * d
        S[msk] += v[msk]; W[msk] += 1.0
        cnt += 1
    for j, c in enumerate(BASE_STATS):
        df[f"ewma_{c}"] = out[:, j]
    df["n_prior"] = n_prior
    df["w_eff"] = w_eff
    df["shrink_w"] = shrink_k / (w_eff + shrink_k)
    eps = 1e-3
    df["ypa"] = df.ewma_passing_yards / (df.ewma_attempts + eps)
    df["comp_rate"] = df.ewma_completions / (df.ewma_attempts + eps)
    df["ptd_rate"] = df.ewma_passing_tds / (df.ewma_attempts + eps)
    df["int_rate"] = df.ewma_passing_interceptions / (df.ewma_attempts + eps)
    df["ypc"] = df.ewma_rushing_yards / (df.ewma_carries + eps)
    df["rushtd_rate"] = df.ewma_rushing_tds / (df.ewma_carries + eps)
    df["ypt"] = df.ewma_receiving_yards / (df.ewma_targets + eps)
    df["catch_rate"] = df.ewma_receptions / (df.ewma_targets + eps)
    df["rtd_rate"] = df.ewma_receiving_tds / (df.ewma_targets + eps)
    df["anytd_rate"] = df.ewma_any_td / (df.ewma_touches + eps)
    return df


def population_mask(df: pd.DataFrame, pop: str) -> np.ndarray:
    if pop == "QB":
        return ((df.position == "QB") & df.qb_starter).to_numpy()
    if pop == "REC":
        return df.position.isin(["RB", "WR", "TE"]).to_numpy()
    if pop == "RB":
        return (df.position == "RB").to_numpy()
    if pop == "SKILL":
        return df.position.isin(["RB", "WR", "TE"]).to_numpy()
    raise ValueError(pop)


# ------------------------------------------------------------------------------- mean models
# Role features from the opportunity engine (research/opportunity). Added ALONGSIDE the raw-count EWMA, never
# instead of it: research/opportunity/RESULTS.md shows the multiplicative volume x share reconstruction is
# worse than raw EWMA in every season, while these same quantities as extra regressors improve target and
# carry projection in 7/7 seasons.
# Team volume enters as the team's own point-in-time EWMA, not as a fitted projection. A nested projection
# is only defined on the seasons its walk-forward loop covered, so it is null for the earliest training
# seasons -- which trains its coefficient against a constant zero and then applies it to ~35 at test time.
ROLE_FEATURES = ["pit_route_share", "pit_tprr", "pit_snap_share", "pit_rz_target_share", "pit_adot",
                 "pit_carry_share", "pit_rz_carry_share", "pit_i5_carry_share", "pit_team_dropbacks",
                 "pit_team_rush_att"]


def has_role_features(df: pd.DataFrame) -> bool:
    return all(c in df.columns for c in ROLE_FEATURES)


def _design(df: pd.DataFrame, spec: StatSpec, col: str, role: bool = False) -> np.ndarray:
    base = [
        np.ones(len(df)), df[f"ewma_{col}"].to_numpy(), df[f"ewma_{spec.opp}"].to_numpy(),
        df.implied_total.to_numpy(), df.home.to_numpy(dtype=float), df.shrink_w.to_numpy(),
    ]
    if role:
        base += [np.nan_to_num(df[c].to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
                 for c in ROLE_FEATURES]
    return np.column_stack(base)


def fit_mean_model(train: pd.DataFrame, spec: StatSpec, col: str, kind: str, role: bool = False):
    """Walk-forward point projection mu(x): OLS for yards, Poisson GLM (IRLS) for counts/TDs.

    Features: EWMA of the stat, EWMA of opportunity, team implied total, home, shrink weight; plus the
    opportunity-engine role features when ``role`` is set. The flag is carried in the returned model so
    predict_mean cannot be called with a different design than the one that was fitted."""
    X = _design(train, spec, col, role); y = np.clip(train[col].to_numpy(dtype=float), 0, None)
    # Standardise every non-intercept column on the TRAINING rows and carry the scaler in the model. The
    # design mixes shares (~0.1) with team dropbacks (~35) and air yards per target (~10); under the Poisson
    # exp link an unscaled IRLS with a 1e-6 ridge produces coefficients that are numerically fine in sample
    # and extreme out of it. Standardising is a no-op for the OLS arm's predictions and makes the ridge
    # penalty mean the same thing for every feature.
    mu_x = X[:, 1:].mean(axis=0)
    sd_x = X[:, 1:].std(axis=0)
    sd_x[sd_x < 1e-9] = 1.0
    Xs = np.column_stack([np.ones(len(X)), (X[:, 1:] - mu_x) / sd_x])
    scaler = (mu_x, sd_x)
    if kind == "yards":
        A = Xs.T @ Xs + RIDGE_LAMBDA * np.eye(Xs.shape[1]); A[0, 0] -= RIDGE_LAMBDA
        beta = np.linalg.solve(A, Xs.T @ y)
        return ("ols", beta, role, scaler)
    beta = np.zeros(Xs.shape[1]); beta[0] = np.log(max(y.mean(), 1e-3))
    pen = RIDGE_LAMBDA * np.eye(Xs.shape[1]); pen[0, 0] = 0.0
    for _ in range(50):
        eta = np.clip(Xs @ beta, -20, 8); w = np.exp(eta)
        z = eta + (y - w) / w
        XtW = Xs.T * w
        new = np.linalg.solve(XtW @ Xs + pen, XtW @ z)
        if np.max(np.abs(new - beta)) < 1e-7:
            beta = new; break
        beta = new
    return ("poisson", beta, role, scaler)


def predict_mean(model, df: pd.DataFrame, spec: StatSpec, col: str, floor: float) -> np.ndarray:
    kind, beta, role, scaler = model
    X = _design(df, spec, col, role)
    mu_x, sd_x = scaler
    X = np.column_stack([np.ones(len(X)), (X[:, 1:] - mu_x) / sd_x])
    mu = X @ beta if kind == "ols" else np.exp(np.clip(X @ beta, -20, 8))
    return np.maximum(mu, floor)


RIDGE_LAMBDA = 1.0
MU_FLOOR = {"yards": 1.0, "count": 0.1, "td": 0.01}


# ------------------------------------------------------------------------------- families
def _sigmoid(x):
    return special.expit(x)


def _minimize(f, x0):
    """L-BFGS-B (numerical gradients, tight tolerance) followed by a Nelder-Mead polish: the
    heteroscedasticity slopes are often nearly flat and L-BFGS-B alone can stop at the start."""
    r = optimize.minimize(f, x0, method="L-BFGS-B", options={"ftol": 1e-12, "gtol": 1e-8, "maxiter": 500})
    r2 = optimize.minimize(f, r.x, method="Nelder-Mead", options={"maxiter": 3000, "xatol": 1e-5, "fatol": 1e-4})
    return r2.x if r2.fun <= r.fun else r.x


class Family:
    name = "base"

    def fit(self, mu, opp, eff, y):  # pragma: no cover - interface
        raise NotImplementedError

    def cdf_grid(self, mu, opp, eff, grid) -> np.ndarray:
        raise NotImplementedError


class NormalHetero(Family):
    """Y ~ N(c0 + c1*mu, sigma), log sigma = s0 + s1*log(mu); censored at 0 on the lattice."""
    name = "normal"

    def fit(self, mu, opp, eff, y):
        lm = np.log(mu)
        X = np.column_stack([np.ones_like(mu), mu])
        c = np.linalg.lstsq(X, y, rcond=None)[0]
        r = y - X @ c
        s0 = np.log(r.std() + 1e-6)

        def nll(t):
            m = t[0] + t[1] * mu; ls = t[2] + t[3] * lm
            return np.sum(ls + 0.5 * ((y - m) / np.exp(ls)) ** 2)
        self.theta = _minimize(nll, np.array([c[0], c[1], s0, 0.0]))
        return self

    def cdf_grid(self, mu, opp, eff, grid):
        t = self.theta
        m = t[0] + t[1] * mu; s = np.exp(t[2] + t[3] * np.log(mu))
        F = stats.norm.cdf((grid[None, :] + 0.5 - m[:, None]) / s[:, None])
        F[:, grid < 0] = 0.0
        return F


class _Hurdle(Family):
    """P(Y=0) = sigmoid(a0 + a1*log mu); Y>0 from a positive family with log-linear mean/shape in log mu."""

    def _fit_hurdle(self, lm, y):
        z = (y <= 0).astype(float)

        def nll(t):
            eta = t[0] + t[1] * lm
            return -np.sum(z * eta - np.logaddexp(0, eta))
        self.h = _minimize(nll, np.array([np.log((z.mean() + 1e-3) / (1 - z.mean() + 1e-3)), 0.0]))

    def _p0(self, mu):
        return _sigmoid(self.h[0] + self.h[1] * np.log(mu))


class HurdleLognormal(_Hurdle):
    name = "hurdle_lognormal"

    def fit(self, mu, opp, eff, y):
        lm = np.log(mu); self._fit_hurdle(lm, y)
        pos = y > 0; ly = np.log(y[pos]); l = lm[pos]
        X = np.column_stack([np.ones_like(l), l]); c = np.linalg.lstsq(X, ly, rcond=None)[0]
        s0 = np.log((ly - X @ c).std() + 1e-6)

        def nll(t):
            m = t[0] + t[1] * l; ls = t[2] + t[3] * l
            return np.sum(ls + 0.5 * ((ly - m) / np.exp(ls)) ** 2)
        self.theta = _minimize(nll, np.array([c[0], c[1], s0, 0.0]))
        return self

    def cdf_grid(self, mu, opp, eff, grid):
        t = self.theta; lm = np.log(mu)
        m = t[0] + t[1] * lm; s = np.exp(t[2] + t[3] * lm); p0 = self._p0(mu)
        x = grid + 0.5
        G = np.zeros((len(mu), len(grid)))
        okx = x > 0
        G[:, okx] = stats.norm.cdf((np.log(x[okx])[None, :] - m[:, None]) / s[:, None])
        F = p0[:, None] + (1 - p0[:, None]) * G
        F[:, grid < 0] = 0.0
        return F


class HurdleGamma(_Hurdle):
    name = "hurdle_gamma"

    def fit(self, mu, opp, eff, y):
        lm = np.log(mu); self._fit_hurdle(lm, y)
        pos = y > 0; yp = y[pos]; l = lm[pos]
        X = np.column_stack([np.ones_like(l), l]); c = np.linalg.lstsq(X, np.log(yp), rcond=None)[0]

        def nll(t):
            m = np.exp(t[0] + t[1] * l); k = np.exp(t[2] + t[3] * l)
            return -np.sum(stats.gamma.logpdf(yp, k, scale=m / k))
        self.theta = _minimize(nll, np.array([c[0], c[1], 0.5, 0.0]))
        return self

    def cdf_grid(self, mu, opp, eff, grid):
        t = self.theta; lm = np.log(mu)
        m = np.exp(t[0] + t[1] * lm); k = np.exp(t[2] + t[3] * lm); p0 = self._p0(mu)
        x = grid + 0.5
        G = np.zeros((len(mu), len(grid))); okx = x > 0
        G[:, okx] = stats.gamma.cdf(x[okx][None, :], k[:, None], scale=(m / k)[:, None])
        F = p0[:, None] + (1 - p0[:, None]) * G
        F[:, grid < 0] = 0.0
        return F


class NegBin(Family):
    """Y ~ NB(mean = exp(m0 + m1 log mu), Var = m + alpha m^2), log alpha = s0 + s1 log mu."""
    name = "negbin"

    def fit(self, mu, opp, eff, y):
        lm = np.log(mu); yi = np.round(np.clip(y, 0, None))

        def nll(t):
            m = np.exp(t[0] + t[1] * lm); a = np.exp(np.clip(t[2] + t[3] * lm, -12, 8))
            r = 1.0 / a
            return -np.sum(special.gammaln(yi + r) - special.gammaln(r) - special.gammaln(yi + 1)
                           + r * np.log(r / (r + m)) + yi * np.log(m / (r + m)))
        self.theta = _minimize(nll, np.array([0.0, 1.0, -1.0, 0.0]))
        return self

    def params(self, mu):
        t = self.theta; lm = np.log(mu)
        m = np.exp(t[0] + t[1] * lm); a = np.exp(np.clip(t[2] + t[3] * lm, -12, 8))
        r = 1.0 / a; p = r / (r + m)
        return r, p

    def cdf_grid(self, mu, opp, eff, grid):
        r, p = self.params(mu)
        F = stats.nbinom.cdf(grid[None, :], r[:, None], p[:, None])
        F[:, grid < 0] = 0.0
        return F


class PoissonFam(Family):
    name = "poisson"

    def fit(self, mu, opp, eff, y):
        lm = np.log(mu); yi = np.round(np.clip(y, 0, None))

        def nll(t):
            m = np.exp(t[0] + t[1] * lm)
            return -np.sum(yi * np.log(m) - m)
        self.theta = _minimize(nll, np.array([0.0, 1.0]))
        return self

    def cdf_grid(self, mu, opp, eff, grid):
        m = np.exp(self.theta[0] + self.theta[1] * np.log(mu))
        F = stats.poisson.cdf(grid[None, :], m[:, None])
        F[:, grid < 0] = 0.0
        return F


class ScaleEmpirical(Family):
    """Scale family: r = Y/mu pooled on train; F(x|mu) = ECDF_r(x/mu).  ``bins``>1 uses separate
    ECDFs per mu-quantile bin (lets the shape of the standardized residual vary with mu)."""
    name = "scale_emp"

    def __init__(self, bins: int = 1):
        self.bins = bins
        self.name = "scale_emp" if bins == 1 else "scale_emp_binned"

    def fit(self, mu, opp, eff, y):
        r = np.clip(y, 0, None) / mu
        if self.bins == 1:
            self.edges = np.array([-np.inf, np.inf]); self.ecdfs = [np.sort(r)]
        else:
            qs = np.quantile(mu, np.linspace(0, 1, self.bins + 1)[1:-1])
            self.edges = np.concatenate([[-np.inf], qs, [np.inf]])
            idx = np.searchsorted(qs, mu, side="right")
            self.ecdfs = [np.sort(r[idx == b]) for b in range(self.bins)]
        return self

    def cdf_grid(self, mu, opp, eff, grid):
        idx = np.searchsorted(self.edges[1:-1], mu, side="right") if self.bins > 1 else np.zeros(len(mu), int)
        F = np.zeros((len(mu), len(grid)))
        x = (grid[None, :] + 0.5) / mu[:, None]
        for b, e in enumerate(self.ecdfs):
            rows = np.where(idx == b)[0]
            if len(rows) == 0:
                continue
            F[rows] = np.searchsorted(e, x[rows], side="right") / max(len(e), 1)
        F[:, grid < 0] = 0.0
        return F


class TwoStageMC(Family):
    """Opportunity N ~ NB(mu_opp) (fit on the opportunity stat) x efficiency given N, by Monte Carlo.

    yards:  Y | N=0 -> 0;  P(Y=0|N) = sigmoid(a0 + a1 log N);  Y>0 ~ Gamma(shape=exp(s0+s1 log N),
            mean = exp(m0 + m1 log N + m2 log eff)) with eff the player's shrunk EWMA yards/opp.
    binom:  Y | N ~ BetaBinomial(N, p = sigmoid(b0 + b1 logit(eff)), concentration kappa).
    """
    name = "two_stage_mc"

    def __init__(self, eff_kind: str, nsims: int = 4000, seed: int = 0):
        self.eff_kind = eff_kind; self.nsims = nsims; self.seed = seed

    def fit_opportunity(self, mu_opp, n_opp):
        self.nb = NegBin().fit(mu_opp, None, None, n_opp)
        return self

    def fit(self, mu, opp, eff, y):
        """opp: ACTUAL opportunity counts in the training rows; eff: player efficiency feature."""
        yi = np.clip(y, 0, None); ok = opp > 0
        n = opp[ok].astype(float); yy = yi[ok]; e = eff[ok]
        if self.eff_kind == "gamma":
            ln = np.log(n); z = (yy <= 0).astype(float)

            def nll_h(t):
                eta = t[0] + t[1] * ln
                return -np.sum(z * eta - np.logaddexp(0, eta))
            self.h = _minimize(nll_h, np.array([0.0, -1.0]))
            pos = yy > 0; yp = yy[pos]; lnp = ln[pos]; le = np.log(np.maximum(e[pos], 0.05))
            X = np.column_stack([np.ones_like(lnp), lnp, le]); c = np.linalg.lstsq(X, np.log(yp), rcond=None)[0]

            def nll(t):
                m = np.exp(t[0] + t[1] * lnp + t[2] * le); k = np.exp(t[3] + t[4] * lnp)
                return -np.sum(stats.gamma.logpdf(yp, k, scale=m / k))
            self.theta = _minimize(nll, np.array([c[0], c[1], c[2], 0.5, 0.5]))
        else:
            lg = special.logit(np.clip(e, 1e-3, 1 - 1e-3)); yy = np.round(yy)

            def nll(t):
                p = _sigmoid(t[0] + t[1] * lg); kap = np.exp(t[2])
                return -np.sum(stats.betabinom.logpmf(yy, n, kap * p, kap * (1 - p)))
            self.theta = _minimize(nll, np.array([0.0, 1.0, 3.0]))
        return self

    def sample(self, mu_opp, eff, rng):
        r, p = self.nb.params(mu_opp)
        N = rng.negative_binomial(r[:, None], p[:, None], size=(len(mu_opp), self.nsims)).astype(float)
        Y = np.zeros_like(N)
        pos = N > 0
        if self.eff_kind == "gamma":
            t = self.theta; ln = np.log(np.where(pos, N, 1.0))
            p0 = _sigmoid(self.h[0] + self.h[1] * ln)
            le = np.log(np.maximum(eff, 0.05))[:, None]
            m = np.exp(t[0] + t[1] * ln + t[2] * le); k = np.exp(t[3] + t[4] * ln)
            g = rng.gamma(k, m / k)
            nz = rng.uniform(size=N.shape) >= p0
            Y = np.where(pos & nz, g, 0.0)
        else:
            t = self.theta; kap = np.exp(t[2])
            pm = _sigmoid(t[0] + t[1] * special.logit(np.clip(eff, 1e-3, 1 - 1e-3)))[:, None]
            pdraw = rng.beta(np.broadcast_to(kap * pm, N.shape), np.broadcast_to(kap * (1 - pm), N.shape))
            Y = rng.binomial(N.astype(int), pdraw).astype(float)
        return Y

    def cdf_grid(self, mu, opp, eff, grid):
        """here ``opp`` is the PROJECTED opportunity mean mu_opp (test rows)."""
        rng = np.random.default_rng(self.seed)
        F = np.zeros((len(mu), len(grid)))
        x = grid + 0.5
        step = max(1, int(4e6 // self.nsims))
        for s in range(0, len(mu), step):
            Y = np.sort(self.sample(opp[s:s + step], eff[s:s + step], rng), axis=1)
            for i in range(Y.shape[0]):
                F[s + i] = np.searchsorted(Y[i], x, side="right") / self.nsims
        F[:, grid < 0] = 0.0
        return F


def make_family(name: str, spec: StatSpec) -> Family:
    if name == "normal":
        return NormalHetero()
    if name == "hurdle_lognormal":
        return HurdleLognormal()
    if name == "hurdle_gamma":
        return HurdleGamma()
    if name == "negbin":
        return NegBin()
    if name == "poisson":
        return PoissonFam()
    if name == "scale_emp":
        return ScaleEmpirical(1)
    if name == "scale_emp_binned":
        return ScaleEmpirical(5)
    if name == "two_stage_mc":
        return TwoStageMC(spec.eff_kind)
    raise ValueError(name)


# ------------------------------------------------------------------------------- evaluation
def crps_from_cdf(F: np.ndarray, grid: np.ndarray, y: np.ndarray) -> np.ndarray:
    """CRPS of an integer-lattice predictive distribution: sum_k (F(k) - 1{y<=k})^2."""
    ind = (y[:, None] <= grid[None, :]).astype(float)
    return np.sum((F - ind) ** 2, axis=1)


def pmf_at(F: np.ndarray, grid: np.ndarray, y: np.ndarray) -> np.ndarray:
    j = np.searchsorted(grid, y)
    j = np.clip(j, 0, len(grid) - 1)
    Fy = F[np.arange(len(y)), j]
    Fym1 = np.where(j > 0, F[np.arange(len(y)), np.maximum(j - 1, 0)], 0.0)
    return Fy - Fym1, Fym1


def evaluate_cdf(F: np.ndarray, grid: np.ndarray, y: np.ndarray, thresholds, rng=None) -> dict:
    """Metrics for one family on one set of rows.  F is P(Y<=k) at each grid k."""
    rng = rng or np.random.default_rng(123)
    y = np.clip(np.round(y), 0, grid.max()).astype(int)
    crps = crps_from_cdf(F, grid, y)
    p, Fm1 = pmf_at(F, grid, y)
    logs = np.log(np.maximum(p, 1e-6))
    u = Fm1 + rng.uniform(size=len(y)) * np.maximum(p, 0)
    u = np.clip(u, 0, 1)
    ks = stats.kstest(u, "uniform").statistic
    hist, _ = np.histogram(u, bins=10, range=(0, 1))
    chi2 = np.sum((hist - len(u) / 10) ** 2 / (len(u) / 10))
    chi2_p = 1 - stats.chi2.cdf(chi2, 9)
    out = {"n": int(len(y)), "crps": float(crps.mean()), "logscore": float(logs.mean()),
           "pit_ks": float(ks), "pit_chi2": float(chi2), "pit_chi2_p": float(chi2_p),
           "pit_hist": (hist / len(u)).round(4).tolist()}
    th = []
    preds = []; obs = []
    for k in thresholds:
        j = np.searchsorted(grid, k - 1)
        pk = 1.0 - F[:, j] if k - 1 >= grid[0] else np.ones(len(y))
        ok = (y >= k).astype(float)
        th.append({"k": int(k), "n": int(len(y)), "pred": float(pk.mean()), "obs": float(ok.mean()),
                   "brier": float(np.mean((pk - ok) ** 2))})
        preds.append(pk); obs.append(ok)
    P = np.concatenate(preds); O = np.concatenate(obs)
    out["thresholds"] = th
    out["brier"] = float(np.mean((P - O) ** 2))
    if P.std() > 1e-9:
        slope, intercept = np.polyfit(P, O, 1)
    else:
        slope, intercept = float("nan"), float("nan")
    out["rel_slope"] = float(slope); out["rel_intercept"] = float(intercept)
    # buckets by base rate of the event in this evaluation set
    buckets = {"low": [], "mid": [], "tail": []}
    for t, pk, ok in zip(th, preds, obs):
        b = "low" if t["obs"] >= 0.5 else ("mid" if t["obs"] >= 0.1 else "tail")
        buckets[b].append((pk, ok))
    out["buckets"] = {}
    for b, lst in buckets.items():
        if not lst:
            continue
        pk = np.concatenate([a for a, _ in lst]); ok = np.concatenate([c for _, c in lst])
        out["buckets"][b] = {"n_thresholds": len(lst), "pred": float(pk.mean()), "obs": float(ok.mean()),
                             "brier": float(np.mean((pk - ok) ** 2)),
                             "ratio": float(pk.mean() / max(ok.mean(), 1e-9))}
    # ECE on 10 predicted-probability bins
    bins = np.clip((P * 10).astype(int), 0, 9)
    ece = 0.0
    for b in range(10):
        m = bins == b
        if m.any():
            ece += m.mean() * abs(P[m].mean() - O[m].mean())
    out["ece"] = float(ece)
    return out


def climatology_cdf(train_y: np.ndarray, grid: np.ndarray, n: int) -> np.ndarray:
    e = np.sort(np.clip(train_y, 0, None))
    F = np.searchsorted(e, grid + 0.5, side="right") / len(e)
    return np.tile(F, (n, 1))


# ---------------------------------------------------------------------------- walk-forward
def run_stat_walkforward(df: pd.DataFrame, spec: StatSpec, test_seasons, families=None, nsims: int = 4000,
                         min_train_season: int = 2016, verbose=print) -> dict:
    """Walk-forward fit/evaluate every family for one statistic.  Returns per-season and pooled metrics
    for the full population and the prop-relevant ('eligible') subset."""
    families = families or FAMILIES_BY_KIND[spec.kind]
    pm = population_mask(df, spec.pop)
    d = df[pm & (df.season >= min_train_season)].copy()
    col = spec.col
    grid = np.arange(0, spec.grid_max + 1)
    pooled = {f: {"all": [], "elig": []} for f in families + ["climatology"]}
    per_season = {f: {} for f in families + ["climatology"]}
    fitted_params = {}
    for S in test_seasons:
        tr = d[d.season < S]; te = d[d.season == S]
        if len(te) == 0 or len(tr) == 0:
            continue
        y_tr = np.clip(tr[col].to_numpy(dtype=float), 0, None); y_te = np.clip(te[col].to_numpy(dtype=float), 0, None)
        mm = fit_mean_model(tr, spec, col, spec.kind)
        mu_tr = predict_mean(mm, tr, spec, col, MU_FLOOR[spec.kind]); mu_te = predict_mean(mm, te, spec, col, MU_FLOOR[spec.kind])
        # opportunity projection (for two-stage)
        om = fit_mean_model(tr, spec, spec.opp, "count")
        muo_tr = predict_mean(om, tr, spec, spec.opp, 0.1); muo_te = predict_mean(om, te, spec, spec.opp, 0.1)
        elig = (te[f"ewma_{spec.opp}"].to_numpy() >= spec.elig_min_opp)
        eff_tr = tr[spec.eff].to_numpy() if spec.eff else None
        eff_te = te[spec.eff].to_numpy() if spec.eff else None
        season_rec = {"season": int(S), "n_train": int(len(tr)), "n_test": int(len(te)), "n_elig": int(elig.sum()),
                      "mae_mu": float(np.mean(np.abs(mu_te - y_te))), "mae_ewma": float(np.mean(np.abs(te[f"ewma_{col}"].to_numpy() - y_te)))}
        # climatology baseline
        F = climatology_cdf(y_tr, grid, len(te))
        for sub, msk in (("all", np.ones(len(te), bool)), ("elig", elig)):
            ev = evaluate_cdf(F[msk], grid, y_te[msk], spec.thresholds); ev.update(season_rec)
            pooled["climatology"][sub].append(ev)
        for fam in families:
            if fam == "two_stage_mc" and (spec.eff is None or spec.opp == col):
                continue
            f = make_family(fam, spec)
            if fam == "two_stage_mc":
                f.nsims = nsims
                f.fit_opportunity(muo_tr, tr[spec.opp].to_numpy(dtype=float))
                f.fit(mu_tr, tr[spec.opp].to_numpy(dtype=float), eff_tr, y_tr)
                F = f.cdf_grid(mu_te, muo_te, eff_te, grid)
            else:
                f.fit(mu_tr, muo_tr, eff_tr, y_tr)
                F = f.cdf_grid(mu_te, muo_te, eff_te, grid)
            for sub, msk in (("all", np.ones(len(te), bool)), ("elig", elig)):
                ev = evaluate_cdf(F[msk], grid, y_te[msk], spec.thresholds); ev.update(season_rec)
                pooled[fam][sub].append(ev)
            if hasattr(f, "theta"):
                fitted_params.setdefault(fam, {})[int(S)] = np.asarray(f.theta).round(4).tolist()
        verbose(f"  {spec.name} season {S}: train {len(tr)} test {len(te)} elig {int(elig.sum())} "
                f"mae_mu {season_rec['mae_mu']:.2f} mae_ewma {season_rec['mae_ewma']:.2f}")
    return {"spec": spec, "per_season": pooled, "params": fitted_params}


def aggregate(per_season_list: list[dict]) -> dict:
    """n-weighted pooling of per-season evaluation dicts (thresholds pooled as well)."""
    if not per_season_list:
        return {}
    n = np.array([e["n"] for e in per_season_list], dtype=float); w = n / n.sum()
    out = {"n": int(n.sum()), "seasons": [e["season"] for e in per_season_list]}
    for k in ("crps", "logscore", "pit_ks", "brier", "rel_slope", "rel_intercept", "ece", "mae_mu", "mae_ewma"):
        vals = np.array([e[k] for e in per_season_list], dtype=float)
        out[k] = float(np.nansum(vals * w))
    out["pit_hist"] = np.average(np.array([e["pit_hist"] for e in per_season_list]), axis=0, weights=w).round(4).tolist()
    # pooled PIT chi2 (sum over 10 bins of pooled histogram)
    H = np.sum(np.array([np.array(e["pit_hist"]) * e["n"] for e in per_season_list]), axis=0)
    chi2 = np.sum((H - H.sum() / 10) ** 2 / (H.sum() / 10)); out["pit_chi2"] = float(chi2)
    out["pit_chi2_p"] = float(1 - stats.chi2.cdf(chi2, 9))
    out["crps_by_season"] = {int(e["season"]): round(e["crps"], 4) for e in per_season_list}
    out["brier_by_season"] = {int(e["season"]): round(e["brier"], 5) for e in per_season_list}
    th = {}
    for e in per_season_list:
        for t in e["thresholds"]:
            a = th.setdefault(t["k"], {"k": t["k"], "n": 0, "pred": 0.0, "obs": 0.0, "brier": 0.0})
            a["n"] += t["n"]; a["pred"] += t["pred"] * t["n"]; a["obs"] += t["obs"] * t["n"]; a["brier"] += t["brier"] * t["n"]
    out["thresholds"] = []
    for k in sorted(th):
        a = th[k]
        out["thresholds"].append({"k": k, "n": a["n"], "pred": round(a["pred"] / a["n"], 4), "obs": round(a["obs"] / a["n"], 4),
                                  "brier": round(a["brier"] / a["n"], 5)})
    bk = {}
    for e in per_season_list:
        for b, v in e["buckets"].items():
            a = bk.setdefault(b, {"n": 0.0, "pred": 0.0, "obs": 0.0, "brier": 0.0})
            nn = v["n_thresholds"] * e["n"]
            a["n"] += nn; a["pred"] += v["pred"] * nn; a["obs"] += v["obs"] * nn; a["brier"] += v["brier"] * nn
    out["buckets"] = {b: {"pred": round(a["pred"] / a["n"], 4), "obs": round(a["obs"] / a["n"], 4),
                          "brier": round(a["brier"] / a["n"], 5), "ratio": round(a["pred"] / max(a["obs"], 1e-9), 3)}
                      for b, a in bk.items()}
    return out
