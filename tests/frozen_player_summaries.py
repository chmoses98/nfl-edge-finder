"""Per-distribution summaries of V4 and V3 on tests/test_player_v4.synthetic_league -- the frozen reference for V5's
"V4 and V3 are unchanged" test. Uses only code that existed before V5, so the fixture can be (and was) generated
with main at c53294d:

    python3 tests/frozen_player_summaries.py tests/fixtures/player_v4_v3_frozen.npz

Why summaries and not a hash of every pmf: ~1.3M pmf values rounded to 1e-10 are not reproducible across CI runner
CPUs (floating-point summation order and library builds differ), so an exact digest of them flips between identical trees.
The mean, standard deviation and total mass of every distribution, compared at 1e-6 relative, catch any material
change to V4 or V3 behaviour (see the limits stated in tests/test_player_v5.py); the bundles' own artifact shas
(fitted parameters) stay exact.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.dirname(HERE), HERE]

V3_STATS = ["receptions", "receiving_yards", "passing_yards", "carries"]


def _moments(pmf) -> tuple:
    p = np.asarray(pmf, float)
    k = np.arange(len(p))
    mass = p.sum()
    mean = float((k * p).sum() / mass)
    sd = float(np.sqrt(max(((k - mean) ** 2 * p).sum() / mass, 0.0)))
    return mean, sd, float(mass)


def summaries() -> dict:
    import test_player_v4 as T4
    from nfl_edge.engines.player import data_dist as DD
    from nfl_edge.engines.player.v4 import model as M
    from nfl_edge.engines.player.v4.volume import team_game_table
    from nfl_edge.research import player_distributions as pdist

    df, st = T4.synthetic_league()
    frame = T4.build_frame(df, st)
    teams = team_game_table(frame)
    b = M.fit_bundle(frame, 2016, teams=teams, verbose=lambda *a: None)
    v4_keys, v4 = [], []
    for r in b.intermediates(frame[frame.season == 2016], teams).to_dict("records"):
        for s, d in sorted(b.distributions(r).items()):
            v4_keys.append(f"{r['player_id']}|{r['game_id']}|{s}")
            v4.append(_moments(d.pmf))
    bb = DD.fit_bundle(frame[frame.season < 2016], 2016, feature_set="v3", stats=V3_STATS, verbose=lambda *a: None)
    te = frame[frame.season == 2016]
    v3_keys, v3 = [], []
    for stat, m in sorted(bb.models.items()):
        rows = te[pdist.population_mask(te, m.spec.pop)]
        for (p, g), d in zip(zip(rows.player_id, rows.game_id), m.distributions(rows)):
            v3_keys.append(f"{p}|{g}|{stat}")
            v3.append(_moments(d.pmf))
    return {"v4_sha": np.array(b.artifact_sha), "v4_keys": np.array(v4_keys), "v4": np.array(v4),
            "v3_sha": np.array(bb.artifact_sha), "v3_keys": np.array(v3_keys), "v3": np.array(v3),
            "_bundle": b}


if __name__ == "__main__":
    out = summaries()
    out.pop("_bundle")
    np.savez_compressed(sys.argv[1], **out)
    print(f"v4 {out['v4_sha']} {len(out['v4_keys'])} distributions; v3 {out['v3_sha']} {len(out['v3_keys'])}")
