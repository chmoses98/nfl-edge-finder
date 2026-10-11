"""Market-input mutations for the runtime non-leakage test of PURE_PLAYER_V1.

The test reruns the WHOLE pipeline (load -> features -> fit -> forecast) on the same football data with the
schedule's market columns (a) as published, (b) removed, (c) randomised and (d) blanked for a random 30% of games,
and requires bit-identical forecasts. A negative control (DATA_PLAYER_V4's VolumeModel, which reads those columns)
must change under the same mutations, which proves the test can detect a dependency.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd

MARKET_SCHEDULE_COLUMNS = ("away_moneyline", "home_moneyline", "spread_line", "away_spread_odds", "home_spread_odds", "total_line",
                           "under_odds", "over_odds")
MODES = ("original", "removed", "randomized", "partial_blank")


def mutate_schedule(sched: pd.DataFrame, mode: str, seed: int = 7) -> pd.DataFrame:
    g = sched.copy()
    cols = [c for c in MARKET_SCHEDULE_COLUMNS if c in g.columns]
    rng = np.random.default_rng(seed)
    if mode == "original":
        return g
    if mode == "removed":
        return g.drop(columns=cols)
    if mode == "randomized":
        for c in cols:
            v = pd.to_numeric(g[c], errors="coerce").to_numpy(float)
            scale = np.nanstd(v) if np.isfinite(v).any() else 1.0
            g[c] = rng.permutation(np.nan_to_num(v, nan=0.0)) + rng.normal(0, max(scale, 1.0), len(g))
        return g
    if mode == "partial_blank":
        blank = rng.random(len(g)) < 0.30
        for c in cols:
            g.loc[blank, c] = np.nan
        return g
    raise ValueError(mode)


def forecast_digest(rows: list[dict]) -> str:
    """sha256 of the canonical JSON of every model-owned forecast field (order-independent)."""
    canon = sorted(json.dumps(r, sort_keys=True, separators=(",", ":"), allow_nan=False) for r in rows)
    return hashlib.sha256("\n".join(canon).encode()).hexdigest()
