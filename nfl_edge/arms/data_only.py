"""DATA_ONLY: a football-only game centre that has never seen a same-game market price.

What it is
----------
The repository's own Milestone-E research model (`scripts/research/game_model_study.py`,
`research/game_model/RESULTS.md`), made reusable and point-in-time safe:

    opponent-adjusted team ratings   weighted ridge on prior team-games, y = off_team + def_opp + hfa
                                     (nfl_edge/research/team_ratings.solve_ratings; half-life 10 weeks,
                                     prior seasons x0.4, ridge 4) over eleven play-by-play metrics
    matchup features                 home offence vs away defence and vice versa, their difference
    schedule context                 rest difference, divisional game, neutral site, indoor
    margin / total models            standardised ridge (lambda 30) fitted on the eight seasons before the
                                     target season, then FROZEN as a hashed artifact

Nothing else. No quarterback identity, no weather, no injuries: those were listed by the research as next
steps, never validated, and a feature without a pre-2026 validated coefficient would be a guess wearing a
model's clothes. They are recorded as unavailable inputs, not silently absent.

What it is NOT allowed to see
-----------------------------
No current same-game market quantity, in any form. The guard is enforceable, not aspirational:

  * the schedule the model reads is `market_free_schedule()`, which DROPS every market column by name before
    any feature code runs and records what it dropped;
  * the design matrix is a WHITELIST: `MARGIN_FEATURES` and `TOTAL_FEATURES` name every column the model may
    consume, and `attest_market_free()` refuses any other column, so `spread_line` cannot be added as a
    predictor without the attestation -- and its tests -- failing;
  * `tests/test_three_arm_data_only.py` poisons the market columns of a schedule and asserts the projection
    does not move by a single bit, and scans this file for market tokens in code.

Point in time
-------------
`ratings_at_cutoff` uses ONLY games that were final before the forecast timestamp (schedule FINAL fields
present, kickoff + 4h <= cutoff), so a Thursday result legitimately informs Sunday's forecast and a game in
progress never does. The artifact is trained on seasons strictly before the target season. The feature cutoff
(latest included kickoff, number of team-games, the bronze file hashes) is recorded on every record.

Sign convention: `projected_home_margin` is home minus away, exactly the incumbent's `spread_home`.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import numpy as np
import polars as pl

from nfl_edge.arms import registry as R
from nfl_edge.data.nfl_calendar import kickoff_utc
from nfl_edge.research.team_ratings import prepare_rows, solve_ratings

# The eleven rating metrics, exactly as the research fitted them.
FEATS = ["epa", "sr", "db_epa", "rush_epa", "epa_ng", "explosive", "sack_rate", "to_rate", "proe", "st_epa", "ed_epa"]
RATING_METRICS = {"epa": "off_epa_play", "sr": "off_success_rate", "db_epa": "off_dropback_epa",
                  "rush_epa": "off_rush_epa", "epa_ng": "off_epa_play_ng", "explosive": "off_explosive_rate",
                  "sack_rate": "off_sack_rate", "to_rate": "off_to_rate", "proe": "off_proe_early_ng",
                  "st_epa": "st_epa_for", "ed_epa": "off_early_down_epa"}
RATING_HYPERPARAMS = {"halflife_games": 10.0, "season_carry": 0.4, "ridge": 4.0}
RATING_SEASONS_BACK = 3
RIDGE_LAMBDA = 30.0
TRAIN_WINDOW_SEASONS = 8

# THE WHITELIST. Every column the two models may consume. Anything else is refused by attest_market_free.
MARGIN_FEATURES = [f"d_{f}" for f in FEATS] + ["rest_diff", "div_game", "neutral"]
TOTAL_FEATURES = [f"m_h_{f}" for f in FEATS] + [f"m_a_{f}" for f in FEATS] + ["indoor", "rest_diff"]
ALLOWED_FEATURES = frozenset(MARGIN_FEATURES) | frozenset(TOTAL_FEATURES)

# Market columns the schedule carries and this model must never read. Dropped by name before any feature
# code sees the frame. The list is deliberately broad: anything that mathematically contains a market number.
FORBIDDEN_INPUT_COLUMNS = frozenset({
    "spread_line", "total_line", "home_moneyline", "away_moneyline", "away_spread_odds", "home_spread_odds",
    "under_odds", "over_odds", "yes_bid", "yes_ask", "no_bid", "no_ask", "mid", "last_price", "implied_spread",
    "implied_total", "kalshi_spread", "kalshi_total", "market_spread", "market_total", "spread_team",
    "implied_team_total", "consensus_spread", "consensus_total", "close_mid", "closing_spread", "closing_total",
})
# Context columns the model reads from the market-free schedule.
SCHEDULE_CONTEXT_COLUMNS = ("home_rest", "away_rest", "div_game", "location", "roof")


class MarketLeak(RuntimeError):
    """A market-derived quantity reached the football-only model."""


# ======================================================================================================
# attestation
# ======================================================================================================

def attest_market_free(columns) -> dict:
    """Refuse any design column outside the whitelist. Returns the attestation record."""
    cols = list(columns)
    bad = sorted(c for c in cols if c not in ALLOWED_FEATURES)
    if bad:
        raise MarketLeak(f"columns outside the DATA_ONLY whitelist reached the design matrix: {bad}")
    forbidden_hits = sorted(c for c in cols if c in FORBIDDEN_INPUT_COLUMNS)
    if forbidden_hits:                      # unreachable given the whitelist, kept as a second lock
        raise MarketLeak(f"market columns in the design matrix: {forbidden_hits}")
    return {"attested": True, "method": "whitelist", "design_columns": cols,
            "forbidden_columns_checked": sorted(FORBIDDEN_INPUT_COLUMNS), "version": R.DATA_ONLY_VERSION}


def market_free_schedule(games: pl.DataFrame) -> tuple[pl.DataFrame, list]:
    """The schedule with every market column removed. Returns (frame, columns_dropped)."""
    dropped = sorted(c for c in games.columns if c in FORBIDDEN_INPUT_COLUMNS)
    return games.drop(dropped), dropped


# ======================================================================================================
# ridge (identical to scripts/research/game_model_study.py)
# ======================================================================================================

def ridge_fit(X, y, lam):
    X = np.asarray(X, float); y = np.asarray(y, float)
    Xm = X.mean(0); Xs = X.std(0) + 1e-9; ym = y.mean()
    Xc = (X - Xm) / Xs; yc = y - ym
    beta = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ yc)
    return {"beta": beta.tolist(), "xm": Xm.tolist(), "xs": Xs.tolist(), "ym": float(ym), "lam": float(lam)}


def ridge_pred(model, X):
    X = np.asarray(X, float)
    return ((X - np.asarray(model["xm"])) / np.asarray(model["xs"])) @ np.asarray(model["beta"]) + model["ym"]


# ======================================================================================================
# the frozen artifact
# ======================================================================================================

@dataclass
class DataOnlyArtifact:
    version: str
    target_season: int
    train_seasons: list
    margin_model: dict
    total_model: dict
    margin_features: list
    total_features: list
    n_train_games: int
    training_source: dict = field(default_factory=dict)
    rating_hyperparams: dict = field(default_factory=lambda: dict(RATING_HYPERPARAMS))
    fitted_at: str | None = None
    artifact_sha: str = ""

    def sha(self) -> str:
        payload = {"version": self.version, "target_season": self.target_season, "train_seasons": self.train_seasons,
                   "margin_model": self.margin_model, "total_model": self.total_model,
                   "margin_features": self.margin_features, "total_features": self.total_features,
                   "n_train_games": self.n_train_games, "rating_hyperparams": self.rating_hyperparams}
        self.artifact_sha = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
        return self.artifact_sha

    def to_json(self) -> dict:
        self.sha()
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_json(cls, d: dict) -> "DataOnlyArtifact":
        a = cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
        recorded = d.get("artifact_sha")
        if recorded and recorded != a.sha():
            raise ValueError(f"artifact sha {recorded} does not match its own content ({a.artifact_sha})")
        return a

    @classmethod
    def load(cls, path: str) -> "DataOnlyArtifact":
        return cls.from_json(json.load(open(path)))

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_json(), f, indent=1)

    def predict(self, features: dict) -> dict:
        """features: name -> value (missing -> 0, as the research's fillna(0)). Returns margin, total, detail."""
        attest_market_free(list(features))
        missing_m = [c for c in self.margin_features if features.get(c) is None]
        missing_t = [c for c in self.total_features if features.get(c) is None]
        xm = [[0.0 if features.get(c) is None else float(features[c]) for c in self.margin_features]]
        xt = [[0.0 if features.get(c) is None else float(features[c]) for c in self.total_features]]
        return {"projected_home_margin": float(ridge_pred(self.margin_model, xm)[0]),
                "projected_total": float(ridge_pred(self.total_model, xt)[0]),
                "missing_margin_features": missing_m, "missing_total_features": missing_t}


def fit_artifact(features: pl.DataFrame, target_season: int, *, lam: float = RIDGE_LAMBDA,
                 window: int = TRAIN_WINDOW_SEASONS, source: dict | None = None,
                 version: str = R.DATA_ONLY_VERSION) -> DataOnlyArtifact:
    """Fit the frozen artifact for `target_season` on the `window` seasons before it, research-identical."""
    attest_market_free(MARGIN_FEATURES + TOTAL_FEATURES)
    tr = features.filter((pl.col("season") < target_season) & (pl.col("season") >= target_season - window)
                         & pl.col("result").is_not_null() & pl.col("total").is_not_null())
    if tr.height < 200:
        raise ValueError(f"only {tr.height} training games for {target_season}; refusing to fit")
    def matrix(cols):
        return tr.select([pl.col(c).cast(pl.Float64).fill_null(0.0).fill_nan(0.0) for c in cols]).to_numpy()
    Xm = matrix(MARGIN_FEATURES); ym = tr["result"].cast(pl.Float64).to_numpy()
    Xt = matrix(TOTAL_FEATURES); yt = tr["total"].cast(pl.Float64).to_numpy()
    seasons = sorted(int(s) for s in tr["season"].unique().to_list())
    art = DataOnlyArtifact(version=version, target_season=int(target_season), train_seasons=[seasons[0], seasons[-1]],
                           margin_model=ridge_fit(Xm, ym, lam), total_model=ridge_fit(Xt, yt, lam),
                           margin_features=list(MARGIN_FEATURES), total_features=list(TOTAL_FEATURES),
                           n_train_games=int(tr.height), training_source=dict(source or {}),
                           fitted_at=datetime.now(timezone.utc).isoformat())
    art.sha()
    return art


# ======================================================================================================
# ratings at a timestamp
# ======================================================================================================

def prepare_team_games(*frames: pl.DataFrame) -> pl.DataFrame:
    """Silver team-game rows (any number of frames, e.g. history + the current season) -> prepared rows."""
    tg = pl.concat([f for f in frames if f is not None and f.height], how="diagonal_relaxed")
    if "season_type" in tg.columns:
        tg = tg.filter(pl.col("season_type") == "REG")
    return prepare_rows(tg)


def final_game_ids_before(games: pl.DataFrame, cutoff: datetime, settle_hours: float = 4.0) -> tuple[set, dict]:
    """Games whose result is published AND whose kickoff + settle_hours <= cutoff. Never a game in progress."""
    ids, latest = set(), None
    for r in games.select("game_id", "gameday", "gametime", "result", "total", "overtime").iter_rows(named=True):
        if r["result"] is None or r["total"] is None:
            continue
        ko = kickoff_utc(str(r["gameday"] or ""), str(r["gametime"] or ""))
        if ko is None or ko + timedelta(hours=settle_hours) > cutoff:
            continue
        ids.add(r["game_id"])
        latest = ko if latest is None or ko > latest else latest
    return ids, {"n_final_games_available": len(ids), "latest_included_kickoff_utc": latest.isoformat() if latest else None,
                 "cutoff_utc": cutoff.isoformat(), "rule": f"result published and kickoff + {settle_hours}h <= cutoff"}


def ratings_at_cutoff(rows: pl.DataFrame, season: int, allowed_game_ids: set, **kw) -> tuple[dict, dict]:
    """team -> {off_<f>, def_<f>} from prior FINAL games only (same solver and metrics as the research)."""
    hp = {**RATING_HYPERPARAMS, **kw}
    prior = rows.filter(pl.col("game_id").is_in(list(allowed_game_ids)) & (pl.col("season") >= season - RATING_SEASONS_BACK))
    recs, meta = {}, {"metrics": {}, "n_team_games": int(prior.height),
                      "seasons_used": sorted(int(s) for s in prior["season"].unique()) if prior.height else []}
    for name, col in RATING_METRICS.items():
        sol = solve_ratings(prior, col, cur_season=season, **hp)
        if not sol:
            meta["metrics"][name] = {"n": 0, "solved": False}
            continue
        meta["metrics"][name] = {"n": sol["n"], "eff_n": round(sol["eff_n"], 1), "hfa": sol["hfa"], "solved": True}
        for t, (o, d) in sol["ratings"].items():
            recs.setdefault(t, {})[f"off_{name}"] = o
            recs[t][f"def_{name}"] = d
    return recs, meta


def ratings_for_week(rows: pl.DataFrame, season: int, week: int, **kw) -> tuple[dict, dict]:
    """Research-style weekly snapshot (games strictly before (season, week)) through the same code path."""
    prior = rows.filter((pl.col("season") < season) | ((pl.col("season") == season) & (pl.col("week") < week)))
    return ratings_at_cutoff(rows, season, set(prior["game_id"].to_list()), **kw)


# ======================================================================================================
# features for one game
# ======================================================================================================

def schedule_context(row: dict) -> dict:
    """Context features from ONE market-free schedule row. Raises on a market column."""
    hits = sorted(k for k in row if k in FORBIDDEN_INPUT_COLUMNS)
    if hits:
        raise MarketLeak(f"schedule row handed to DATA_ONLY still carries market columns: {hits}")
    hr, ar = row.get("home_rest"), row.get("away_rest")
    rest_diff = None if hr is None or ar is None else float(hr) - float(ar)
    div = row.get("div_game")
    return {"rest_diff": rest_diff,
            "div_game": None if div is None else float(div),
            "neutral": float(str(row.get("location") or "") == "Neutral"),
            "indoor": float(str(row.get("roof") or "") in ("dome", "closed"))}


def matchup_features(home: dict | None, away: dict | None, context: dict) -> tuple[dict, list]:
    """The research's feature construction: m_h = h_off + a_def, m_a = a_off + h_def, d = m_h - m_a."""
    feats, missing = {}, []
    for f in FEATS:
        ho, ad = (home or {}).get(f"off_{f}"), (away or {}).get(f"def_{f}")
        ao, hd = (away or {}).get(f"off_{f}"), (home or {}).get(f"def_{f}")
        if None in (ho, ad, ao, hd):
            missing.append(f)
            feats[f"m_h_{f}"] = feats[f"m_a_{f}"] = feats[f"d_{f}"] = None
            continue
        feats[f"m_h_{f}"] = ho + ad
        feats[f"m_a_{f}"] = ao + hd
        feats[f"d_{f}"] = (ho + ad) - (ao + hd)
    for k in ("rest_diff", "div_game", "neutral", "indoor"):
        feats[k] = context.get(k)
    return feats, missing


def project_game(artifact: DataOnlyArtifact, ratings: dict, schedule_row: dict, home: str, away: str) -> dict:
    """One DATA_ONLY centre. `status` is OK, DEGRADED (some feature missing, filled 0 as the research did) or
    UNAVAILABLE (a whole team has no rating: no projection, never a fallback)."""
    ctx = schedule_context(schedule_row)
    feats, missing = matchup_features(ratings.get(home), ratings.get(away), ctx)
    if ratings.get(home) is None or ratings.get(away) is None or len(missing) == len(FEATS):
        who = [t for t in (home, away) if ratings.get(t) is None]
        return {"status": R.UNAVAILABLE, "unavailable_reason": f"no point-in-time rating for {who or [home, away]}",
                "features": feats, "missing_metrics": missing}
    pred = artifact.predict(feats)
    ctx_missing = [k for k in ("rest_diff", "div_game") if ctx.get(k) is None]
    status = R.DEGRADED if (missing or ctx_missing) else R.OK
    return {"status": status,
            "unavailable_reason": None,
            "projected_home_margin": pred["projected_home_margin"], "projected_total": pred["projected_total"],
            "features": feats, "missing_metrics": missing, "missing_context": ctx_missing,
            "attestation": attest_market_free(list(feats)),
            "degraded_reason": (f"missing metrics {missing}, missing context {ctx_missing} (filled with 0 as in the research)"
                                if status == R.DEGRADED else None)}


# ======================================================================================================
# loading the inputs a snapshot needs
# ======================================================================================================

def sha256_file(path: str) -> str | None:
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_inputs(root: str, season: int) -> dict:
    """Silver history + the current season rebuilt from bronze play-by-play, with file identities."""
    from nfl_edge.data import silver as SV
    silver_tg = os.path.join(root, "data", "silver", "team_game.parquet")
    games_p = os.path.join(root, "data", "silver", "games.parquet")
    out = {"team_game_history_path": silver_tg, "team_game_history_sha": sha256_file(silver_tg),
           "games_path": games_p, "games_sha": sha256_file(games_p), "current_season_pbp_path": None,
           "current_season_pbp_sha": None, "current_season_team_games": 0, "unavailable": []}
    if not os.path.exists(silver_tg) or not os.path.exists(games_p):
        out["unavailable"].append("silver team_game/games missing; DATA_ONLY cannot rate teams")
        return out
    hist = pl.read_parquet(silver_tg)
    frames = [hist.filter(pl.col("season") < season)]
    pbp = os.path.join(root, "data", "raw", "nflverse", "pbp", f"play_by_play_{season}.parquet")
    if os.path.exists(pbp):
        try:
            cur = SV.team_game_from_pbp(season)
            frames.append(cur)
            out.update({"current_season_pbp_path": pbp, "current_season_pbp_sha": sha256_file(pbp),
                        "current_season_team_games": int(cur.height)})
        except Exception as e:                      # noqa: BLE001 - recorded, never silently ignored
            out["unavailable"].append(f"current-season play-by-play could not be aggregated: {type(e).__name__}: {e}")
    else:
        out["unavailable"].append(f"no play-by-play file for {season} yet; ratings use prior seasons only")
    out["rows"] = prepare_team_games(*frames)
    out["games"] = pl.read_parquet(games_p)
    return out
