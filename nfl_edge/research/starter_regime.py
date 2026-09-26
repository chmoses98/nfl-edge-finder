"""STARTER_REGIME_ADJUSTED team strength -- RESEARCH ONLY, NOT WIRED INTO ANY PACKET, ARM OR GATE.

Model id  : DATA_ONLY_SRA  (a challenger to DATA_ONLY, never a replacement)
Version   : starter-regime-0.1.0
Authority : RESEARCH_ONLY. Nothing on the report path imports this module (tests assert it).

The question
------------
`nfl_edge.arms.data_only` rates every team from its prior team-games with a recency weight (half-life 10 weeks,
prior seasons x0.4). A team whose starting quarterback CHANGES keeps its offensive games from the previous regime
at full weight. The quarterback is the largest single driver of offensive EPA, so a rating built on the old
regime describes an offence that will not take the field. This module offers ONE generic change: offensive
metric rows from past games started by a quarterback other than the projected starter of the target game are
multiplied by a single preregistered factor ``w_regime`` in the ratings regression. Defensive rows, special
teams and every other team are untouched. No team, player or game is special-cased.

Point in time (the only way this module may be used)
----------------------------------------------------
* ``past_game_starters`` must be derived from games that were FINAL before the cutoff (the starter of a completed
  game is a historical fact at the cutoff). ``starters_from_pbp`` derives it from play-by-play and the caller must
  pass only final-before-cutoff game ids; ``regime_weights`` refuses any row whose game is not in
  ``allowed_game_ids``.
* ``projected_starters`` (team -> QB id for the TARGET game) must come from pregame evidence observed at or
  before the cutoff -- in this repository that is ``nfl_edge.context.qb_resolution`` (qb-resolution-1.0.0). It must
  never be read from the target game's own play-by-play or the schedule's post-game QB columns. This module has no
  argument through which the target game's realised starter can enter.
* A team with no projected starter (unknown / abstain) gets NO adjustment (w = 1 for all its rows), recorded.

What it is not
--------------
Not validated. Not a patch for any team. The 2026 Week-3 ATL@GB audit that motivated it is GENERATION /
DIAGNOSTIC evidence only (research/tnf_audit_2026_w03/) and can never be counted as validation. The preregistered
prospective test is in research/starter_regime/PREREGISTRATION.md.
"""
from __future__ import annotations

import numpy as np
import polars as pl

from nfl_edge.research.team_ratings import _team_index

MODEL_ID = "DATA_ONLY_SRA"
VERSION = "starter-regime-0.1.0"
AUTHORITY = "RESEARCH_ONLY"

# The offensive rating columns this adjustment applies to: every DATA_ONLY offensive metric EXCEPT special teams,
# declared generically (all scrimmage-offence metrics), not chosen by looking at any one game.
QB_CONDITIONED_COLUMNS = ("off_epa_play", "off_success_rate", "off_dropback_epa", "off_rush_epa", "off_epa_play_ng",
                          "off_explosive_rate", "off_sack_rate", "off_to_rate", "off_proe_early_ng",
                          "off_early_down_epa")
NOT_CONDITIONED = ("st_epa_for",)


class LeakageError(RuntimeError):
    """A row or input that is not point-in-time reached the adjustment."""


def starters_from_pbp(pbp: pl.DataFrame, allowed_game_ids) -> dict:
    """(game_id, team) -> passer id with the most dropbacks, for FINAL-before-cutoff games only.

    Any game id outside ``allowed_game_ids`` is ignored, so the target game (or a game in progress) cannot
    contribute a starter even if its plays are present in the file."""
    allowed = set(allowed_game_ids)
    need = {"game_id", "posteam", "qb_dropback", "passer_player_id"}
    missing = need - set(pbp.columns)
    if missing:
        raise ValueError(f"play-by-play lacks {sorted(missing)}")
    d = (pbp.filter(pl.col("game_id").is_in(list(allowed)) & (pl.col("qb_dropback") == 1)
                    & pl.col("passer_player_id").is_not_null() & pl.col("posteam").is_not_null())
         .group_by(["game_id", "posteam", "passer_player_id"]).agg(pl.len().alias("n"))
         .sort(["game_id", "posteam", "n", "passer_player_id"], descending=[False, False, True, False]))
    out = {}
    for r in d.iter_rows(named=True):
        out.setdefault((r["game_id"], r["posteam"]), r["passer_player_id"])
    return out


def regime_weights(rows: pl.DataFrame, allowed_game_ids, past_game_starters: dict, projected_starters: dict,
                   w_regime: float) -> tuple[pl.DataFrame, dict]:
    """Add a ``regime_w`` column: ``w_regime`` on OFFENSIVE rows (``team`` is the offence) whose past-game starter
    differs from the team's projected starter; 1.0 elsewhere. Returns (rows, audit)."""
    if not 0.0 <= float(w_regime) <= 1.0:
        raise ValueError("w_regime must be in [0, 1]")
    allowed = set(allowed_game_ids)
    stray = sorted(set(rows["game_id"].to_list()) - allowed)
    if stray:
        raise LeakageError(f"{len(stray)} rows from games not final before the cutoff reached the adjustment, "
                           f"e.g. {stray[:3]}")
    bad_keys = sorted({g for (g, _t) in past_game_starters} - allowed)
    if bad_keys:
        raise LeakageError(f"past-game starters supplied for games not final before the cutoff: {bad_keys[:3]}")
    ws, audit = [], {"model_id": MODEL_ID, "version": VERSION, "w_regime": float(w_regime),
                     "teams_without_projected_starter": [], "downweighted": {}}
    for g, t in zip(rows["game_id"].to_list(), rows["team"].to_list()):
        proj = projected_starters.get(t)
        past = past_game_starters.get((g, t))
        if proj is None or past is None or past == proj:
            ws.append(1.0)
        else:
            ws.append(float(w_regime))
            audit["downweighted"].setdefault(t, []).append(g)
    audit["teams_without_projected_starter"] = sorted({t for t in rows["team"].unique().to_list()
                                                       if projected_starters.get(t) is None})
    return rows.with_columns(pl.Series("regime_w", ws, dtype=pl.Float64)), audit


def solve_ratings_weighted(rows: pl.DataFrame, value_col: str, halflife_games: float = 10.0,
                           season_carry: float = 0.4, ridge: float = 4.0, cur_season: int | None = None,
                           row_weight_col: str | None = None) -> dict:
    """`team_ratings.solve_ratings` with an optional extra per-row weight. With ``row_weight_col=None`` (or all
    weights 1) it is numerically identical to the production solver -- a test pins that."""
    r = rows.filter(pl.col(value_col).is_not_null())
    if r.height < 40:
        return {}
    teams = sorted(set(r["team"].to_list()) | set(r["opp"].to_list()))
    idx = _team_index(teams)
    n = len(teams)
    y = r[value_col].to_numpy().astype(float)
    mu = np.average(y)
    yc = y - mu
    m = r.height
    X = np.zeros((m, 2 * n + 1))
    ti = np.array([idx[t] for t in r["team"].to_list()])
    oi = np.array([idx[t] for t in r["opp"].to_list()])
    X[np.arange(m), ti] = 1.0
    X[np.arange(m), n + oi] = 1.0
    X[:, 2 * n] = r["is_home"].to_numpy().astype(float) * 2 - 1
    wk = r["week_no"].to_numpy().astype(float)
    ago = wk.max() + 1 - wk
    w = 0.5 ** (ago / halflife_games)
    if cur_season is not None:
        seasons_back = (cur_season - r["season"].to_numpy()).astype(float)
        w = w * (season_carry ** seasons_back)
    if row_weight_col is not None and row_weight_col in r.columns:
        w = w * r[row_weight_col].to_numpy().astype(float)
    W = np.sqrt(w)[:, None]
    A = X * W
    b = yc * W[:, 0]
    lam = np.full(2 * n + 1, ridge, dtype=float)
    lam[-1] = 0.01
    beta = np.linalg.solve(A.T @ A + np.diag(lam), A.T @ b)
    return {"ratings": {t: (float(beta[i]), float(beta[n + i])) for t, i in idx.items()},
            "hfa": float(beta[-1]), "mean": float(mu), "n": int(m), "eff_n": float(w.sum())}


def ratings_at_cutoff_sra(rows: pl.DataFrame, season: int, allowed_game_ids, past_game_starters: dict,
                          projected_starters: dict, w_regime: float, rating_metrics: dict,
                          hyperparams: dict, seasons_back: int = 3) -> tuple[dict, dict]:
    """DATA_ONLY's `ratings_at_cutoff`, with the regime weight applied to QB-conditioned offensive columns only.

    Offence and defence come out of ONE regression per metric (y = off_team + def_opp + hfa). Applying the weight
    to a row also down-weights what that row says about the OPPONENT's defence; that is inherent in the joint
    model and is recorded in the audit, not hidden."""
    allowed = set(allowed_game_ids)
    prior = rows.filter(pl.col("game_id").is_in(list(allowed)) & (pl.col("season") >= season - seasons_back))
    prior, audit = regime_weights(prior, allowed, past_game_starters, projected_starters, w_regime)
    recs, meta = {}, {"n_team_games": int(prior.height), "audit": audit, "metrics": {}}
    for name, col in rating_metrics.items():
        wcol = "regime_w" if col in QB_CONDITIONED_COLUMNS else None
        sol = solve_ratings_weighted(prior, col, cur_season=season, row_weight_col=wcol, **hyperparams)
        meta["metrics"][name] = {"solved": bool(sol), "regime_weighted": wcol is not None}
        for t, (o, d) in (sol.get("ratings") or {}).items():
            recs.setdefault(t, {})[f"off_{name}"] = o
            recs[t][f"def_{name}"] = d
    audit["opponent_defence_side_effect"] = ("a down-weighted offensive row also carries less weight for the "
                                             "opponent defence rating in the same joint regression")
    return recs, meta
