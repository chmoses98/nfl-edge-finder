"""PERIOD ENGINE: one joint quarter-score simulation per game, from the full-game centre and a period residual bank.

WHY NOT DIVIDE THE FULL-GAME LINE
---------------------------------
Measured on 2,639 regular-season games (2016-2025, nflverse play-by-play):

    1H margin  = 0.47 + 0.559 x spread     (not 0.5 x spread)      residual sd 10.2
    1Q margin  = 0.26 + 0.222 x spread     (not 0.25 x spread)     residual sd 6.5
    1H total   = -0.59 + 0.521 x total     (about half)            residual sd 8.7
    1Q total   = 0.40 + 0.187 x total      (NOT a quarter)         residual sd 5.6

and the first-half margin has the same key-number mass structure as the full game (|margin| = 3: 12%, 7: 12%,
10: 9%, 0: 7%), which a normal cannot carry. So the engine is:

    latent state     the 8-vector of (home, away) points in Q1..Q4, drawn jointly
    centre           per-component regression on the full-game implied team totals, fitted walk-forward
    shape            an EMPIRICAL residual bank of whole 8-vectors from historical games (recency-weighted),
                     resampled jointly so quarter-to-quarter and home-away dependence is preserved
    discretisation   round to integers, clip at zero
    overtime         regulation ties resolved with the historical OT model, only for the full-game leg of
                     half/full composites; period questions never see overtime (rules: period points only)

Every period question (winner / spread / total / team total / both-score for 1H, 2H, 1Q..4Q, and the half/full
composite) is then an indicator on the same draws, so all period ladders are coherent with each other. The
full-game distribution implied by the period simulation is NOT the game engine's; the gap is measured and
recorded per snapshot (`cross_engine_gap`), never hidden.

Candidates compared walk-forward in research/period_engine (scripts/research/period_engine_study.py, 1,612 test
games 2020-2025): NAIVE_SCALE (division, normal residuals), REG_NORMAL (regression + independent normal residuals),
REG_EMPIRICAL_JOINT (regression + jointly resampled residual vectors, rounded), LINE_BUCKET_EMPIRICAL (whole
historical games from the same line bucket), KERNEL_EMPIRICAL (whole games, Gaussian line-proximity x recency
weights) and KERNEL_EMPIRICAL_SHIFTED (kernel resampling + the INTEGER regression-centre shift).

Preregistered rule: lowest mean Brier over the four liquid ladders (1H winner, 1H spread, 1H total, 1Q total); a
tie within 0.0005 is broken by the key-number mass of the 1H margin closest to observed. Result: REG_EMPIRICAL_JOINT
0.18458, KERNEL_EMPIRICAL_SHIFTED 0.18502 (tie), and the shifted kernel carries |m| in {0,3,7} at 0.049/0.088/0.079
against observed 0.069/0.124/0.114 where the residual bank carries 0.040/0.075/0.061. So the DEFAULT is
KERNEL_EMPIRICAL_SHIFTED (`method="kernel_shift"`); every candidate stays in the study so the choice is auditable, and
the key-number under-prediction that remains is a named limitation (docs/SHADOW_V2.md).
"""
from __future__ import annotations

import hashlib
import os

import numpy as np
import polars as pl

from nfl_edge.semantics.questions import COMPOSITE, EVENT, PERIOD, RANGE, THRESHOLD, Question

ENGINE_VERSION = "period-engine-2.0.0"
DISTRIBUTION_VERSION = "period-residual-bank-1.0.0"
QUARTERS = ("q1", "q2", "q3", "q4")
PERIOD_QUARTERS = {"1Q": ("q1",), "2Q": ("q2",), "3Q": ("q3",), "4Q": ("q4",), "1H": ("q1", "q2"), "2H": ("q3", "q4"),
                   "FULL": ("q1", "q2", "q3", "q4")}
COLS = ["hq1", "hq2", "hq3", "hq4", "aq1", "aq2", "aq3", "aq4"]


# ------------------------------------------------------------------------------------------- dataset
def quarter_scores_from_pbp(path: str, season_type: str = "REG") -> pl.DataFrame:
    """One row per game: end-of-quarter cumulative scores (Q1..Q4) from the last post-play score of each quarter.

    Reproduces the final score in every non-overtime game (256/256 in 2024; 2,489/2,495 across 2016-2025, the six
    exceptions being games whose play-by-play ends with a scoring play recorded without post-play totals -- those
    rows are dropped rather than repaired).
    """
    lf = pl.scan_parquet(path)
    cols = ["game_id", "play_id", "qtr", "posteam", "home_team", "away_team", "posteam_score_post", "defteam_score_post",
            "home_score", "away_score", "season_type", "season", "week"]
    df = lf.select(cols).filter(pl.col("season_type") == season_type).collect()
    df = df.sort(["game_id", "play_id"]).with_columns([
        pl.when(pl.col("posteam") == pl.col("home_team")).then(pl.col("posteam_score_post")).otherwise(pl.col("defteam_score_post")).alias("home_post"),
        pl.when(pl.col("posteam") == pl.col("home_team")).then(pl.col("defteam_score_post")).otherwise(pl.col("posteam_score_post")).alias("away_post")])
    q = (df.filter(pl.col("qtr") <= 4).with_columns(pl.col("qtr").cast(pl.Int32))
         .group_by(["game_id", "qtr"]).agg([pl.col("home_post").drop_nulls().last().alias("h"), pl.col("away_post").drop_nulls().last().alias("a"),
                                             pl.col("season").first(), pl.col("week").first(), pl.col("home_team").first(), pl.col("away_team").first(),
                                             pl.col("home_score").first().alias("home_final"), pl.col("away_score").first().alias("away_final")]))
    w = q.pivot(values=["h", "a"], index=["game_id", "season", "week", "home_team", "away_team", "home_final", "away_final"], on="qtr").sort("game_id")
    for i in range(1, 5):
        if f"h_{i}" not in w.columns:
            w = w.with_columns(pl.lit(None, dtype=pl.Float64).alias(f"h_{i}"), pl.lit(None, dtype=pl.Float64).alias(f"a_{i}"))
    for i in range(1, 5):
        ph = pl.col(f"h_{i-1}") if i > 1 else pl.lit(0.0)
        pa = pl.col(f"a_{i-1}") if i > 1 else pl.lit(0.0)
        w = w.with_columns([(pl.col(f"h_{i}") - ph).alias(f"hq{i}"), (pl.col(f"a_{i}") - pa).alias(f"aq{i}")])
    w = w.with_columns([pl.col("h_4").alias("home_reg"), pl.col("a_4").alias("away_reg")])
    return w.select(["game_id", "season", "week", "home_team", "away_team", "home_final", "away_final", "home_reg", "away_reg"] + COLS)


def build_period_table(root: str, seasons, games: pl.DataFrame | None = None) -> pl.DataFrame:
    """Quarter scores joined to the schedule's lines and overtime flag. Rows with any missing quarter are dropped."""
    frames = []
    for s in seasons:
        p = os.path.join(root, "data", "raw", "nflverse", "pbp", f"play_by_play_{s}.parquet")
        if os.path.exists(p):
            frames.append(quarter_scores_from_pbp(p))
    if not frames:
        raise FileNotFoundError("no play-by-play files for the requested seasons")
    w = pl.concat(frames, how="diagonal_relaxed")
    if games is None:
        games = pl.read_parquet(os.path.join(root, "data", "silver", "games.parquet"))
    g = games.select(["game_id", "spread_line", "total_line", "overtime", "result", "total"])
    w = w.join(g, on="game_id", how="inner")
    w = w.filter(pl.all_horizontal([pl.col(c).is_not_null() for c in COLS]) & pl.col("spread_line").is_not_null() & pl.col("total_line").is_not_null())
    # a game whose regulation quarters do not reproduce its final (without overtime) is evidence we cannot trust
    ok = (pl.col("overtime").fill_null(0) == 1) | ((pl.col("home_reg") == pl.col("home_final")) & (pl.col("away_reg") == pl.col("away_final")))
    return w.filter(ok).with_columns([((pl.col("total_line") + pl.col("spread_line")) / 2.0).alias("home_implied"),
                                      ((pl.col("total_line") - pl.col("spread_line")) / 2.0).alias("away_implied")])


# ------------------------------------------------------------------------------------------- model
class PeriodBank:
    """Per-quarter regression centres + a joint empirical residual bank, fitted on training games only."""

    def __init__(self, train: pl.DataFrame, *, ref_season: int, halflife: float = 3.0):
        # polars -> numpy directly (no pandas / pyarrow bridge: the test runner installs neither pyarrow nor needs it)
        col = lambda c: train[c].to_numpy().astype(float)  # noqa: E731
        X = np.column_stack([np.ones(train.height), col("home_implied"), col("away_implied")])
        self.beta = {}
        Y = np.column_stack([col(c) for c in COLS])
        self.resid = np.empty_like(Y)
        for j, c in enumerate(COLS):
            b = np.linalg.lstsq(X, Y[:, j], rcond=None)[0]
            self.beta[c] = b
            self.resid[:, j] = Y[:, j] - X @ b
        season = col("season")
        w = 0.5 ** ((ref_season - season) / halflife)
        self.w = w / w.sum()
        self.n = train.height
        self.Y = Y                                    # the historical 8-vectors themselves (kernel methods)
        self.fitted = X @ np.column_stack([self.beta[c] for c in COLS])
        self.lines = np.column_stack([col("spread_line"), col("total_line")])
        # overtime model from training games that went to overtime
        ot = train["overtime"].fill_null(0).to_numpy().astype(int) == 1
        res = col("result")
        self.p_tie_given_ot = float(np.mean(res[ot] == 0)) if ot.sum() else 0.05
        nz = np.abs(res[ot][res[ot] != 0])
        self.ot_abs_margin = nz if len(nz) else np.array([3.0, 3.0, 6.0, 7.0])
        self.train_seasons = (int(season.min()), int(season.max()))
        self.fingerprint = hashlib.sha256(self.resid.tobytes() + self.w.tobytes()).hexdigest()[:16]

    def center(self, spread_home: float, total_line: float) -> np.ndarray:
        hi, ai = (total_line + spread_home) / 2.0, (total_line - spread_home) / 2.0
        x = np.array([1.0, hi, ai])
        return np.array([x @ self.beta[c] for c in COLS])

    def kernel_weights(self, spread_home: float, total_line: float, bw_spread: float = 2.0, bw_total: float = 3.0) -> np.ndarray:
        """Recency x line-proximity weights over the training games (a nonparametric conditional distribution)."""
        ds = (self.lines[:, 0] - spread_home) / bw_spread
        dt = (self.lines[:, 1] - total_line) / bw_total
        w = self.w * np.exp(-0.5 * (ds * ds + dt * dt))
        if w.sum() <= 0:
            w = self.w
        return w / w.sum()

    def simulate(self, spread_home: float, total_line: float, n: int = 40000, rng=None, draws: dict | None = None,
                 method: str = "kernel_shift") -> dict:
        """Joint quarter scores for one game. `draws` (uniforms) allows common random numbers across centres.

        method  residual       regression centre + jointly resampled residual 8-vectors, rounded
                kernel         whole historical 8-vectors resampled with line-proximity x recency weights (no shift)
                kernel_shift   kernel resampling, each vector shifted by the INTEGER difference between the regression
                               centre at the target line and at the sampled game's own line (default: preserves the
                               integer key-number structure while centring exactly; see research/period_engine)
        """
        rng = rng or np.random.default_rng(0)
        mu = self.center(spread_home, total_line)
        w = self.w if method == "residual" else self.kernel_weights(spread_home, total_line)
        if draws is not None:
            cdf = np.cumsum(w); cdf[-1] = 1.0
            idx = np.minimum(np.searchsorted(cdf, draws["u_idx"][:n], side="right"), self.n - 1)
            u_tie, u_otm, u_side = draws["u_tie"][:n], draws["u_otm"][:n], draws["u_side"][:n]
        else:
            idx = rng.choice(self.n, size=n, p=w)
            u_tie, u_otm, u_side = rng.random(n), rng.random(n), rng.random(n)
        if method == "residual":
            Y = np.clip(np.round(mu[None, :] + self.resid[idx]), 0, None)
        elif method == "kernel":
            Y = self.Y[idx]
        elif method == "kernel_shift":
            Y = np.clip(self.Y[idx] + np.round(mu[None, :] - self.fitted[idx]), 0, None)
        else:
            raise ValueError(method)
        out = {c: Y[:, j] for j, c in enumerate(COLS)}
        out["home_reg"] = out["hq1"] + out["hq2"] + out["hq3"] + out["hq4"]
        out["away_reg"] = out["aq1"] + out["aq2"] + out["aq3"] + out["aq4"]
        margin = out["home_reg"] - out["away_reg"]
        # overtime for the full-game leg only
        tied = margin == 0
        k = int(tied.sum())
        ot_pts_home = np.zeros(n); ot_pts_away = np.zeros(n)
        if k:
            stays = u_tie[tied] < self.p_tie_given_ot
            otm = self.ot_abs_margin[np.minimum((u_otm[tied] * len(self.ot_abs_margin)).astype(int), len(self.ot_abs_margin) - 1)]
            p_home = 1.0 / (1.0 + np.exp(-spread_home / 6.0))
            home_wins = u_side[tied] < p_home
            ot_pts_home[tied] = np.where(stays, 0.0, np.where(home_wins, otm, 0.0))
            ot_pts_away[tied] = np.where(stays, 0.0, np.where(home_wins, 0.0, otm))
        out["home"] = out["home_reg"] + ot_pts_home
        out["away"] = out["away_reg"] + ot_pts_away
        out["margin"] = out["home"] - out["away"]
        out["total"] = out["home"] + out["away"]
        out["residual_idx"] = idx
        return out


def period_stat(sim: dict, stat: str, period: str, subject: str | None, home: str, away: str) -> np.ndarray:
    qs = PERIOD_QUARTERS[period]
    h = sum(sim["h" + q] for q in qs)
    a = sum(sim["a" + q] for q in qs)
    if period == "FULL":
        h, a = sim["home"], sim["away"]
    if stat == "margin":
        if subject == home:
            return h - a
        if subject == away:
            return a - h
        return h - a
    if stat == "total":
        return h + a
    if stat == "team_points":
        if subject == home:
            return h
        if subject == away:
            return a
        raise ValueError(f"team_points needs a team in the game ({subject!r})")
    if stat == "min_team_points":
        return np.minimum(h, a)
    if stat == "abs_margin":
        return np.abs(h - a)
    raise ValueError(f"{stat!r} is not a period score function")


def indicator(sim: dict, q: Question, home: str, away: str) -> np.ndarray:
    if q.kind == THRESHOLD:
        x = period_stat(sim, q.stat, q.period, q.subject, home, away)
        return {">=": x >= q.k, ">": x > q.k, "<=": x <= q.k, "<": x < q.k}[q.op]
    if q.kind == RANGE:
        x = period_stat(sim, q.stat, q.period, q.subject, home, away)
        ind = x >= q.lo
        return ind & (x <= q.hi) if q.hi is not None else ind
    if q.kind == EVENT:
        if q.event == "WIN":
            return period_stat(sim, "margin", q.period, q.subject, home, away) > 0
        if q.event == "TIE":
            return period_stat(sim, "margin", q.period, None, home, away) == 0
        if q.event == "BOTH_SCORE":
            qs = PERIOD_QUARTERS[q.period]
            return (sum(sim["h" + x] for x in qs) > 0) & (sum(sim["a" + x] for x in qs) > 0)
        raise ValueError(f"event {q.event!r} is not a period score function")
    if q.kind == COMPOSITE:
        ind = np.ones(len(sim["margin"]), bool)
        for leg in q.legs:
            ind &= indicator(sim, leg, home, away)
        return ind
    raise ValueError(q.kind)


def answer(sim: dict, q: Question, home: str, away: str) -> dict:
    if q.engine not in (PERIOD, "JOINT") and not (q.kind == COMPOSITE):
        return {"p_yes": None, "contract_value": None, "reason": f"question belongs to the {q.engine} engine"}
    if q.kind != COMPOSITE and q.period not in PERIOD_QUARTERS:
        return {"p_yes": None, "contract_value": None, "reason": f"period {q.period!r} unknown"}
    try:
        ind = indicator(sim, q, home, away)
    except (ValueError, KeyError) as e:
        return {"p_yes": None, "contract_value": None, "reason": str(e)}
    p = float(np.mean(ind))
    cv = p
    if q.kind == EVENT and q.event == "WIN" and q.period == "FULL" and q.tie_rule == "HALF_PAYOUT":
        cv = p + 0.5 * float(np.mean(sim["margin"] == 0))
    return {"p_yes": p, "contract_value": cv, "n_draws": int(len(ind)), "reason": None, "engine_version": ENGINE_VERSION}


def cross_engine_gap(period_sim: dict, game_sim: dict) -> dict:
    """How far the period simulation's implied full game sits from the game engine's, on the same centre."""
    def stats(s):
        return {"p_home_win": float(np.mean(s["margin"] > 0)), "p_tie": float(np.mean(s["margin"] == 0)),
                "mean_margin": float(np.mean(s["margin"])), "sd_margin": float(np.std(s["margin"])),
                "mean_total": float(np.mean(s["total"])), "sd_total": float(np.std(s["total"]))}
    a, b = stats(period_sim), stats(game_sim)
    return {"period_engine": a, "game_engine": b, "diff": {k: a[k] - b[k] for k in a}}


def summary(sim: dict) -> dict:
    out = {}
    for per in ("1Q", "1H", "2H", "FULL"):
        m = period_stat(sim, "margin", per, None, "H", "A")
        t = period_stat(sim, "total", per, None, "H", "A")
        out[per] = {"p_home": float(np.mean(m > 0)), "p_tie": float(np.mean(m == 0)), "mean_margin": float(m.mean()),
                    "mean_total": float(t.mean()), "sd_total": float(t.std())}
    return out
