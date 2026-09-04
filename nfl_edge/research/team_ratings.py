"""Point-in-time opponent-adjusted team ratings from silver team_game rows.

For a snapshot (season, week) we use ONLY games with (season, week) strictly
earlier. Ratings for a metric m (e.g. off epa/play) come from weighted ridge
regression on prior team-games:

    y_g,t = off_t + def_opp + hfa*is_home + eps,   weight = decay(games ago) * season carry

Ridge shrinks every team toward the league mean, which is the partial pooling
that raw season averages lack. Weighting by recency (half-life in team-games)
and discounting prior seasons gives a single, leakage-free solution to opponent
adjustment, recency and shrinkage at once.
"""
from __future__ import annotations
import numpy as np
import polars as pl

METRICS = {
    # metric name -> silver column (offensive perspective value for the team on offense)
    "epa": "off_epa_play",
    "sr": "off_success_rate",
    "db_epa": "off_dropback_epa",
    "rush_epa": "off_rush_epa",
    "epa_ng": "off_epa_play_ng",
    "ed_epa": "off_early_down_epa",
    "explosive": None,  # computed: (explosive_passes+explosive_runs)/plays
    "sack_rate": None,  # sacks/dropbacks (offense allowed)
    "to_rate": None,    # turnovers/plays
    "proe": "off_proe_early_ng",
    "st_epa": "st_epa_for",
}


def _team_index(teams):
    return {t: i for i, t in enumerate(sorted(teams))}


def solve_ratings(rows: pl.DataFrame, value_col: str, halflife_games: float = 10.0, season_carry: float = 0.6,
                  ridge: float = 4.0, cur_season: int | None = None) -> dict:
    """rows: team-game rows with columns team, opp, is_home, season, week, value_col, and 'game_no'
    (a global chronological index). Returns dict(team -> (off, def)), plus hfa and league mean."""
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
    X[np.arange(m), ti] = 1.0           # offense of team
    X[np.arange(m), n + oi] = 1.0       # defense of opponent
    X[:, 2 * n] = r["is_home"].to_numpy().astype(float) * 2 - 1  # +1 home, -1 away
    # recency measured in WEEKS (team-games), not the league-wide game index
    wk = r["week_no"].to_numpy().astype(float)
    ago = wk.max() + 1 - wk
    w = 0.5 ** (ago / halflife_games)
    if cur_season is not None:
        seasons_back = (cur_season - r["season"].to_numpy()).astype(float)
        w = w * (season_carry ** seasons_back)
    W = np.sqrt(w)[:, None]
    A = X * W
    b = yc * W[:, 0]
    # ridge toward 0 for team params, tiny for hfa
    lam = np.full(2 * n + 1, ridge, dtype=float); lam[-1] = 0.01
    AtA = A.T @ A + np.diag(lam)
    beta = np.linalg.solve(AtA, A.T @ b)
    out = {}
    for t, i in idx.items():
        out[t] = (float(beta[i]), float(beta[n + i]))
    return {"ratings": out, "hfa": float(beta[-1]), "mean": float(mu), "n": int(m), "eff_n": float(w.sum())}


def prepare_rows(team_game: pl.DataFrame) -> pl.DataFrame:
    tg = team_game.with_columns([
        ((pl.col("off_explosive_passes") + pl.col("off_explosive_runs")) / pl.col("off_plays")).alias("off_explosive_rate"),
        (pl.col("off_sacks") / pl.col("off_dropbacks").clip(1)).alias("off_sack_rate"),
        (pl.col("off_turnovers") / pl.col("off_plays")).alias("off_to_rate"),
    ])
    # chronological game index: order by season, week, then game_id
    order = tg.select("season", "week", "game_id").unique().sort(["season", "week", "game_id"]).with_row_index("game_no")
    weeks = tg.select("season", "week").unique().sort(["season", "week"]).with_row_index("week_no")
    return tg.join(order, on=["season", "week", "game_id"], how="left").join(weeks, on=["season", "week"], how="left")


def snapshot_ratings(rows: pl.DataFrame, season: int, week: int, metrics: dict | None = None, **kw) -> pl.DataFrame:
    """Ratings using games strictly before (season, week)."""
    prior = rows.filter((pl.col("season") < season) | ((pl.col("season") == season) & (pl.col("week") < week)))
    prior = prior.filter(pl.col("season") >= season - 3)
    metrics = metrics or {"epa": "off_epa_play", "sr": "off_success_rate", "db_epa": "off_dropback_epa", "rush_epa": "off_rush_epa",
                          "epa_ng": "off_epa_play_ng", "explosive": "off_explosive_rate", "sack_rate": "off_sack_rate",
                          "to_rate": "off_to_rate", "proe": "off_proe_early_ng", "st_epa": "st_epa_for", "ed_epa": "off_early_down_epa"}
    recs = {}
    for name, col in metrics.items():
        sol = solve_ratings(prior, col, cur_season=season, **kw)
        if not sol:
            continue
        for t, (o, d) in sol["ratings"].items():
            recs.setdefault(t, {"team": t, "season": season, "week": week})
            recs[t][f"off_{name}"] = o
            recs[t][f"def_{name}"] = d
        recs.setdefault("_meta", {"team": "_meta", "season": season, "week": week})
        recs["_meta"][f"hfa_{name}"] = sol["hfa"]
    df = pl.DataFrame([v for k, v in recs.items() if k != "_meta"])
    return df
