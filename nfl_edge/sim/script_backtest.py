"""SCRIPT CALIBRATION BACKTEST for GAME SCRIPT V2 (sim-script-2.0.0). RESEARCH_ONLY.

Inputs are the compact per-game script summaries the five-season walk-forward wrote from the very rows it scored
(``five_year.ScriptCollector``): nine cell counts and the marginal-event probabilities of every game. Each game is
then classified AFTER THE FACT by the same ``script_v2.cell_index`` / ``event_indicators`` functions applied to
the realized final margin (overtime included), total and team volume, with the same centre the simulation used.

Baselines are fitted on TRAINING seasons only (every game of 2016..Y-1 with a consensus closing line, each
classified with its own closing line): B0 = unconditional cell / event frequencies; B1 = frequencies within the
game's absolute closing-spread bucket. Preregistered: research/game_script_v2/PREREGISTRATION.md, section 3.

Inference is clustered at the GAME: every score here is one number per game, and the bootstrap resamples games.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data as D
from . import script_v2 as V

SPREAD_BUCKETS = (0.0, 3.0, 7.0, 10.0, np.inf)
N_BINS = 10
B = 2000
SEED = 20261005
HISTORY_START = 2016


def spread_bucket(spread) -> np.ndarray:
    return np.clip(np.searchsorted(np.asarray(SPREAD_BUCKETS), np.abs(np.asarray(spread, float)), side="right") - 1, 0, len(SPREAD_BUCKETS) - 2)


# ----------------------------------------------------------------------------------------- realized
def realized_games(seasons) -> pd.DataFrame:
    """One row per game: closing centre, realized margin/total, realized cell and realized events."""
    g = D.schedule().to_pandas()
    g = g[g["season"].isin(list(seasons)) & g["result"].notna() & g["spread_line"].notna() & g["total_line"].notna()].copy()
    tg = D.load("team_games", sorted(set(g["season"]))).to_pandas()
    vol = tg.set_index(["game_id", "team"])[["plays", "pass_att", "designed_rush"]]
    rows = []
    for r in g.itertuples():
        m, t = float(r.result), float(r.total)
        cell = V.CELLS[int(V.cell_index(np.array([m]), np.array([t]), r.spread_line, r.total_line)[0])]
        h = vol.loc[(r.game_id, r.home_team)] if (r.game_id, r.home_team) in vol.index else None
        a = vol.loc[(r.game_id, r.away_team)] if (r.game_id, r.away_team) in vol.index else None
        kw = {}
        if h is not None and a is not None:
            kw = dict(home_plays=[h["plays"]], away_plays=[a["plays"]], home_pass_att=[h["pass_att"]], away_pass_att=[a["pass_att"]],
                      home_designed=[h["designed_rush"]], away_designed=[a["designed_rush"]])
        ev = V.event_indicators(np.array([m]), np.array([t]), r.spread_line, r.total_line, **kw)
        rows.append({"game_id": r.game_id, "season": int(r.season), "week": int(r.week), "spread_line": float(r.spread_line),
                     "total_line": float(r.total_line), "margin": m, "total": t, "cell": cell,
                     **{f"ev_{k}": (None if v is None else bool(v[0])) for k, v in ev.items()}})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------- baselines
def baselines(train: pd.DataFrame) -> dict:
    """B0 / B1 cell and event frequencies from training games only (Laplace +1 per cell)."""
    k = np.array([V.CELLS.index(c) for c in train["cell"]])
    b0 = (np.bincount(k, minlength=V.N_CELLS) + 1.0) / (len(k) + V.N_CELLS)
    bk = spread_bucket(train["spread_line"])
    b1 = {}
    for j in range(len(SPREAD_BUCKETS) - 1):
        kk = k[bk == j]
        b1[j] = (np.bincount(kk, minlength=V.N_CELLS) + 1.0) / (len(kk) + V.N_CELLS)
    ev0, ev1 = {}, {}
    for e in V.EVENTS:
        col = train[f"ev_{e}"].dropna().astype(float)
        ev0[e] = float((col.sum() + 1) / (len(col) + 2))
        ev1[e] = {}
        for j in range(len(SPREAD_BUCKETS) - 1):
            c = train.loc[(bk == j) & train[f"ev_{e}"].notna(), f"ev_{e}"].astype(float)
            ev1[e][j] = float((c.sum() + 1) / (len(c) + 2))
    return {"B0": b0, "B1": b1, "ev_B0": ev0, "ev_B1": ev1, "n_train_games": int(len(train)),
            "train_seasons": sorted(int(s) for s in train["season"].unique())}


# ------------------------------------------------------------------------------------------- scores
def multiclass_scores(P: np.ndarray, Y: np.ndarray, counts: np.ndarray | None = None) -> dict:
    """Per-game multiclass Brier, smoothed log loss, top-script probability / hit, entropy."""
    brier = ((P - Y) ** 2).sum(axis=1)
    if counts is not None:
        Ps = (counts + 0.5) / (counts.sum(axis=1, keepdims=True) + 0.5 * V.N_CELLS)
    else:
        Ps = P
    ll = -np.log((Ps * Y).sum(axis=1))
    top = P.argmax(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        ent = -np.where(P > 0, P * np.log(P), 0.0).sum(axis=1)
    return {"brier": brier, "log_loss": ll, "top_p": P.max(axis=1), "top_hit": Y[np.arange(len(Y)), top], "entropy": ent}


def reliability(P: np.ndarray, Y: np.ndarray, n_bins: int = N_BINS) -> dict:
    p = P.ravel(); y = Y.ravel()
    b = np.clip((p * n_bins).astype(int), 0, n_bins - 1)
    bins, ece = [], 0.0
    for j in range(n_bins):
        m = b == j
        if not m.any():
            bins.append({"bin": [j / n_bins, (j + 1) / n_bins], "n": 0})
            continue
        mp, fr = float(p[m].mean()), float(y[m].mean())
        ece += m.sum() / len(p) * abs(mp - fr)
        bins.append({"bin": [j / n_bins, (j + 1) / n_bins], "n": int(m.sum()), "mean_p": mp, "freq": fr})
    return {"bins": bins, "ece": float(ece)}


def ece_null(P: np.ndarray, B_: int = B, seed: int = SEED) -> dict:
    """ECE a perfectly calibrated forecaster shows on these games: outcomes drawn from the forecasts themselves."""
    rng = np.random.default_rng(seed)
    cum = np.cumsum(P, axis=1)
    out = np.empty(B_)
    for i in range(B_):
        u = rng.random((len(P), 1))
        k = np.minimum((u > cum).sum(axis=1), V.N_CELLS - 1)
        Y = np.zeros_like(P); Y[np.arange(len(P)), k] = 1.0
        out[i] = reliability(P, Y)["ece"]
    return {"mean": float(out.mean()), "p95": float(np.quantile(out, 0.95)), "p99": float(np.quantile(out, 0.99))}


def boot_diff(a: np.ndarray, b: np.ndarray, B_: int = B, seed: int = SEED) -> dict:
    """Mean of (a - b) per game with a game-level bootstrap 95% interval."""
    d = np.asarray(a, float) - np.asarray(b, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(B_, len(d)))
    bs = d[idx].mean(axis=1)
    return {"mean": float(d.mean()), "lo": float(np.quantile(bs, 0.025)), "hi": float(np.quantile(bs, 0.975)), "n": int(len(d))}


# --------------------------------------------------------------------------------------- the study
def season_table(script_games: list, realized: pd.DataFrame, base: dict) -> pd.DataFrame:
    """Join the scored games with their realized cell / events and their baselines' forecasts."""
    rz = realized.set_index("game_id")
    rows = []
    for g in script_games:
        if g["game_id"] not in rz.index:
            rows.append({"game_id": g["game_id"], "missing_realized": True})
            continue
        r = rz.loc[g["game_id"]]
        counts = np.asarray(g["cell_counts"], float)
        j = int(spread_bucket([g["spread_home"]])[0])
        rec = {"game_id": g["game_id"], "season": g["season"], "week": g["week"], "missing_realized": False,
               "counts": counts, "P": counts / counts.sum(), "B0": base["B0"], "B1": base["B1"][j], "bucket": j,
               "y": V.CELLS.index(r["cell"]), "centre_matches_close": bool(abs(g["spread_home"] - r["spread_line"]) < 1e-9
                                                                            and abs(g["total_line"] - r["total_line"]) < 1e-9)}
        for e in V.EVENTS:
            rec[f"p_{e}"] = g["events"].get(e)
            rec[f"b0_{e}"] = base["ev_B0"][e]; rec[f"b1_{e}"] = base["ev_B1"][e][j]
            rec[f"y_{e}"] = r[f"ev_{e}"]
        rows.append(rec)
    return pd.DataFrame(rows)


def score_block(t: pd.DataFrame, with_null: bool = True) -> dict:
    t = t[~t["missing_realized"]]
    P = np.vstack(t["P"]); C = np.vstack(t["counts"]); P0 = np.vstack(t["B0"]); P1 = np.vstack(t["B1"])
    Y = np.zeros_like(P); Y[np.arange(len(t)), t["y"].to_numpy(int)] = 1.0
    out = {"n_games": int(len(t))}
    sc = {"model": multiclass_scores(P, Y, C), "B0": multiclass_scores(P0, Y), "B1": multiclass_scores(P1, Y)}
    for k, s in sc.items():
        out[k] = {m: float(np.mean(v)) for m, v in s.items()}
        out[k]["reliability"] = reliability({"model": P, "B0": P0, "B1": P1}[k], Y)
    out["brier_model_minus_B0"] = boot_diff(sc["model"]["brier"], sc["B0"]["brier"])
    out["brier_model_minus_B1"] = boot_diff(sc["model"]["brier"], sc["B1"]["brier"])
    out["logloss_model_minus_B0"] = boot_diff(sc["model"]["log_loss"], sc["B0"]["log_loss"])
    out["logloss_model_minus_B1"] = boot_diff(sc["model"]["log_loss"], sc["B1"]["log_loss"])
    out["by_cell"] = {c: {"predicted": float(P[:, k].mean()), "realized": float(Y[:, k].mean()),
                          "B0": float(P0[:, k].mean()), "B1": float(P1[:, k].mean())} for k, c in enumerate(V.CELLS)}
    if with_null:
        out["ece_null"] = ece_null(P)
    ev = {}
    for e in V.EVENTS:
        m = t[f"p_{e}"].notna() & t[f"y_{e}"].notna()
        if not m.any():
            continue
        p = t.loc[m, f"p_{e}"].to_numpy(float); y = t.loc[m, f"y_{e}"].astype(float).to_numpy()
        b0 = t.loc[m, f"b0_{e}"].to_numpy(float); b1 = t.loc[m, f"b1_{e}"].to_numpy(float)
        bm, b0s, b1s = (p - y) ** 2, (b0 - y) ** 2, (b1 - y) ** 2
        ev[e] = {"n": int(m.sum()), "mean_p": float(p.mean()), "rate": float(y.mean()), "brier_model": float(bm.mean()),
                 "brier_B0": float(b0s.mean()), "brier_B1": float(b1s.mean()),
                 "model_minus_B0": boot_diff(bm, b0s), "model_minus_B1": boot_diff(bm, b1s)}
    out["events"] = ev
    return out


def verdict(pooled: dict, by_season: dict) -> dict:
    """The preregistered GAME SCRIPT V2 verdict (PREREGISTRATION.md section 3)."""
    c = {"pooled_brier_better_than_B0": pooled["brier_model_minus_B0"]["hi"] < 0,
         "pooled_brier_not_worse_than_B1": pooled["brier_model_minus_B1"]["lo"] <= 0,
         "pooled_ece_within_null_95": pooled["model"]["reliability"]["ece"] <= pooled["ece_null"]["p95"],
         "no_season_worse_than_B0": all(s["brier_model_minus_B0"]["mean"] <= 0 for s in by_season.values())}
    if pooled["brier_model_minus_B0"]["mean"] > 0:
        v = "REJECTED"
    elif all(c.values()):
        v = "READY_FOR_PROSPECTIVE_RESEARCH"
    else:
        v = "NEEDS_MORE_WORK"
    return {"conditions": c, "verdict": v}


def run(script_games_by_season: dict) -> dict:
    """The full study: per season (baselines refitted on that season's training seasons) and pooled."""
    seasons = sorted(int(s) for s in script_games_by_season)
    realized = realized_games(range(HISTORY_START, max(seasons) + 1))
    tables, out = [], {"by_season": {}, "baselines": {}}
    for y in seasons:
        base = baselines(realized[(realized["season"] >= HISTORY_START) & (realized["season"] < y)])
        t = season_table(script_games_by_season[y], realized[realized["season"] == y], base)
        out["baselines"][str(y)] = {"train_seasons": base["train_seasons"], "n_train_games": base["n_train_games"],
                                    "B0": [float(x) for x in base["B0"]]}
        out["by_season"][str(y)] = score_block(t)
        out["by_season"][str(y)]["missing_realized"] = int(t["missing_realized"].sum())
        out["by_season"][str(y)]["centre_is_close"] = int(t.loc[~t["missing_realized"], "centre_matches_close"].sum())
        tables.append(t)
    allt = pd.concat(tables, ignore_index=True)
    out["pooled"] = score_block(allt)
    out["verdict"] = verdict(out["pooled"], out["by_season"])
    out["cells"] = list(V.CELLS)
    return out
