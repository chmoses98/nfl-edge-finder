"""Walk-forward replay of the incumbent player models with THEIR OWN code (read-only imports).

shadow-0.4.0 = frozen design v1 (`nfl_edge.research.player_distributions` + `nfl_edge.shadow.models.fit_bundle`)
shadow-0.5.0 = challenger design v2 (`nfl_edge.shadow.challenger.count_design_v2`, count specs only)

Exactly the replay used by research/mean_defect (scripts/research/mean_defect_study.py::frame): the feature
frame is the live pricer's EWMA config over all prior games (so defect D1 -- live history missing the current
season -- is NOT present in this replay; the replay measures the model design, not the live data bug). Each
target season T is fitted on seasons 2016..T-1 and scored on T. No frozen file is edited: the challenger
context manager swaps functions in memory only.

Output (cache): incumbent_<version>.parquet with (player_id, game_id, stat, mu) and incumbent_<version>_<stat>.npz
holding the full pmf on the incumbent's own grid (0..grid_max) for CRPS / log score / thresholds.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

from .data import CACHE, ROOT

sys.path.insert(0, ROOT)

STATS = ["attempts", "completions", "passing_yards", "passing_tds", "targets", "receptions", "receiving_yards",
         "carries", "rushing_yards"]
VERSIONS = {"shadow-0.4.0": "v1", "shadow-0.5.0": "v2"}


def ensure_silver_games():
    """The incumbent loader reads data/silver/games.parquet (schedule only); build it from the downloaded schedule if absent."""
    p = os.path.join(ROOT, "data", "silver", "games.parquet")
    if not os.path.exists(p):
        from nfl_edge.data import silver
        os.makedirs(os.path.dirname(p), exist_ok=True)
        silver.load_games().write_parquet(p)


def build_frame():
    from nfl_edge.research import player_distributions as pdist
    ensure_silver_games()
    cfg = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
    df = pdist.load_player_games(ROOT, range(2013, 2027))
    pri = pdist.position_priors(df, range(2013, 2016))
    return pdist.add_ewma_features(df, halflife=cfg["halflife"], season_carry=cfg["season_carry"],
                                   shrink_k=cfg["shrink_k"], priors=pri)


def replay(targets=range(2017, 2027), out_dir: str = CACHE) -> dict:
    from nfl_edge.research import player_distributions as pdist
    from nfl_edge.shadow.models import fit_bundle
    from nfl_edge.shadow import challenger as C
    os.makedirs(out_dir, exist_ok=True)
    df = build_frame()
    meta = {"n_frame_rows": int(len(df)), "targets": list(targets)}
    for version, design in VERSIONS.items():
        t0 = time.time()
        rows, pmfs = [], {s: ([], []) for s in STATS}
        for T in targets:
            cfg = {"min_train_season": 2016}
            if design == "v2":
                with C.count_design_v2():
                    b = fit_bundle(df, T, version, cfg, verbose=lambda *a, **k: None)
                    _collect(df, T, b, pdist, rows, pmfs)
            else:
                b = fit_bundle(df, T, version, cfg, verbose=lambda *a, **k: None)
                _collect(df, T, b, pdist, rows, pmfs)
        out = pd.concat(rows, ignore_index=True)
        out.to_parquet(os.path.join(out_dir, f"incumbent_{version}.parquet"), index=False)
        for s, (keys, Ps) in pmfs.items():
            if keys:
                k = pd.concat(keys, ignore_index=True)
                np.savez_compressed(os.path.join(out_dir, f"incumbent_{version}_{s}.npz"),
                                    player_id=k.player_id.to_numpy(str), game_id=k.game_id.to_numpy(str),
                                    P=np.concatenate(Ps).astype(np.float32))
        meta[version] = {"rows": int(len(out)), "seconds": round(time.time() - t0, 1)}
    json.dump(meta, open(os.path.join(out_dir, "incumbent_meta.json"), "w"), indent=1)
    return meta


def _collect(df, T, b, pdist, rows, pmfs):
    te_all = df[df.season == T]
    for s in STATS:
        if s not in b.stat_models:
            continue
        spec = pdist.STAT_SPECS[s]
        te = te_all[pdist.population_mask(te_all, spec.pop)]
        if te.empty:
            continue
        grid, S, mu = b.stat_models[s].survival(te)
        P = np.clip(S - np.concatenate([S[:, 1:], np.zeros((len(S), 1))], axis=1), 0, None)
        rows.append(pd.DataFrame({"player_id": te.player_id.values, "game_id": te.game_id.values, "stat": s,
                                  "mu": mu, "pmf_mean": P @ grid, "season": T}))
        pmfs[s][0].append(te[["player_id", "game_id"]].reset_index(drop=True))
        pmfs[s][1].append(P)
    if b.td_model is not None:
        te = te_all[te_all.position.isin(["RB", "WR", "TE"])]
        p = b.td_model.predict(te)
        rows.append(pd.DataFrame({"player_id": te.player_id.values, "game_id": te.game_id.values, "stat": "anytime_td",
                                  "mu": p, "pmf_mean": p, "season": T}))


def load(version: str, stat: str, out_dir: str = CACHE):
    """Returns (keys DataFrame[player_id, game_id], P matrix on 0..grid_max) or None."""
    p = os.path.join(out_dir, f"incumbent_{version}_{stat}.npz")
    if not os.path.exists(p):
        return None
    z = np.load(p)
    return pd.DataFrame({"player_id": z["player_id"], "game_id": z["game_id"]}), z["P"].astype(float)


if __name__ == "__main__":
    print(replay())
