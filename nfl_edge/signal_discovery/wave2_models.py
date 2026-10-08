"""Frozen Wave-2 model artifacts: the Wave-1 fitting procedures, serialized. RESEARCH ONLY.

* WF-TOTAL: the Wave-1 walk-forward OLS (`evaluate_game.walk_forward`, spec `hypotheses_set1.walk_forward["WF-TOTAL"]`)
  of total_resid on [gap.total, env.plays, env.sec_per_play, def_quality_sum.epa, off_quality_sum.epa] + intercept.
  The 2026 fold trains on every usable season < 2026 (2015-2025), exactly as fold N trains on seasons < N.
* Prop projection: the Wave-1 ridge (`evaluate_props._fit_predict`, lambda 1, training-mean imputation and
  standardisation) for the 2026 walk-forward fold (train 2016-2025), per family.

`fit_*` return plain JSON-able parameter dicts; `predict_*` apply them. Nothing here is ever refit after the
artifact is committed: the Wave-2 runner loads the committed JSON and refuses a file whose hash differs.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np
import pandas as pd

from nfl_edge.signal_discovery import stats
from nfl_edge.signal_discovery.evaluate_props import (
    TRAIN_FIRST,
    _design,
    _num,
    family_rows,
)

WF_TOTAL_FEATURES = ("gap.total", "env.plays", "env.sec_per_play", "def_quality_sum.epa", "off_quality_sum.epa")
PROP_TEST_SEASON = 2026
LAMBDA = 1.0


def canonical_sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


# --------------------------------------------------------------------------- WF-TOTAL


def fit_wf_total(rows: list[dict], test_season: int, spec: dict) -> dict[str, Any]:
    """The Wave-1 fold procedure for `test_season`: OLS on usable rows of seasons < test_season."""
    feats, target = spec["features"], spec["target"]
    usable = [r for r in rows if r.get(target) is not None and all(r.get(f) is not None for f in feats)]
    tr = [r for r in usable if r["season"] < test_season]
    X = np.column_stack([np.ones(len(tr))] + [[r[f] for r in tr] for f in feats])
    res = stats.ols([r[target] for r in tr], X)
    return {
        "model": "WF-TOTAL",
        "procedure": "nfl_edge.signal_discovery.evaluate_game.walk_forward (OLS, intercept + features, train seasons < test)",
        "test_season": test_season,
        "features": list(feats),
        "target": target,
        "coef": dict(zip(["intercept"] + list(feats), [float(b) for b in res["beta"]], strict=True)),
        "n_train": len(tr),
        "train_seasons": sorted({r["season"] for r in tr}),
        "pick_threshold_points": spec["pick_threshold_points"],
    }


def predict_wf_total(artifact: dict[str, Any], features: dict[str, float | None]) -> float | None:
    """Predicted total residual (actual - market total). None when any input is missing (never imputed)."""
    c = artifact["coef"]
    vals = [features.get(f) for f in artifact["features"]]
    if any(v is None or (isinstance(v, float) and np.isnan(v)) for v in vals):
        return None
    return float(c["intercept"] + sum(c[f] * float(v) for f, v in zip(artifact["features"], vals, strict=True)))


# --------------------------------------------------------------------------- prop ridge


def family_features(spec: dict, fam: dict) -> tuple[list[str], list[tuple[str, str]], list[str]]:
    feats = [f.replace("{stat}", fam["stat"]) for f in spec["model_features"]]
    inters = spec["interactions"].get(fam["id"], [])
    return feats, [(a, b) for a, b, _ in inters], [n for _, _, n in inters]


def fit_prop(tr: pd.DataFrame, fam: dict, features: list[str], inter: list[tuple[str, str]]) -> dict[str, Any]:
    """`evaluate_props._fit_predict`'s arithmetic, keeping the parameters it discards."""
    y = _num(tr, fam["stat"])
    Xtr = _design(tr, fam, features, inter)
    mu = np.nanmean(Xtr, axis=0)
    mu = np.where(np.isfinite(mu), mu, 0.0)
    Xtr = np.where(np.isfinite(Xtr), Xtr, mu)
    sd = Xtr.std(axis=0)
    sd[0] = 1.0
    sd = np.where(sd > 0, sd, 1.0)
    shift = mu * (np.arange(len(mu)) > 0)
    Ztr = (Xtr - shift) / sd
    pen = np.eye(Ztr.shape[1]) * LAMBDA
    pen[0, 0] = 0.0
    beta = np.linalg.solve(Ztr.T @ Ztr + pen, Ztr.T @ y)
    resid = y - Ztr @ beta
    q = np.quantile(resid, [0.1, 0.25, 0.75, 0.9])
    return {
        "family": fam["id"],
        "stat": fam["stat"],
        "kalshi_stat": fam.get("kalshi_stat"),
        "features": features,
        "interactions": [list(p) for p in inter],
        "mu": [float(v) for v in mu],
        "sd": [float(v) for v in sd],
        "beta": [float(v) for v in beta],
        "median_offset": float(np.median(resid)),
        "resid_q10_q25_q75_q90": [float(v) for v in q],
        "n_train": len(tr),
    }


def predict_prop(params: dict[str, Any], te: pd.DataFrame) -> np.ndarray:
    """Raw ridge prediction `pred` (add `median_offset` for the model median), training-mean imputation."""
    X = _design(te, {"stat": params["stat"]}, params["features"], [tuple(p) for p in params["interactions"]])
    mu = np.asarray(params["mu"])
    sd = np.asarray(params["sd"])
    X = np.where(np.isfinite(X), X, mu)
    Z = (X - mu * (np.arange(len(mu)) > 0)) / sd
    return Z @ np.asarray(params["beta"])


def prop_training_rows(pf: pd.DataFrame, fam: dict, test_season: int = PROP_TEST_SEASON) -> pd.DataFrame:
    d = family_rows(pf, fam)
    return d[(d["season"] >= TRAIN_FIRST) & (d["season"] < test_season)]
