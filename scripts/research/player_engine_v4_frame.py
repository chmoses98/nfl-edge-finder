#!/usr/bin/env python3
"""Build the player-game research frame the v4 studies read: 2013-<last> player-games with v2, v3 and v4 features.

    python3 scripts/research/player_engine_v4_frame.py --out /tmp/pe4/frame.pkl [--last-season 2025]

Everything is point in time (EWMA features from strictly prior games; teammate statuses from each week's own report
and roster). The frame is a local cache (~80k rows), never committed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.engines.player import data_dist as DD                       # noqa: E402
from nfl_edge.engines.player.features_v2 import add_v2_features           # noqa: E402
from nfl_edge.engines.player.features_v3 import add_v3_features           # noqa: E402
from nfl_edge.engines.player.v4 import features as F4                     # noqa: E402
from nfl_edge.research import player_distributions as pdist               # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/pe4/frame.pkl")
    ap.add_argument("--last-season", type=int, default=2025)
    a = ap.parse_args()
    t = time.time()
    cfg = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
    raw = pdist.load_player_games(ROOT, range(2013, a.last_season + 1))
    priors = pdist.position_priors(raw, range(2013, 2016))
    d = pdist.add_ewma_features(raw, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"], priors=priors)
    d = add_v2_features(d, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"])
    d = add_v3_features(DD.ensure_columns(d))
    d = F4.add_recency_features(d)
    d = F4.add_absence_features(d, F4.StatusBook(F4.status_frame(ROOT, range(2013, a.last_season + 1))))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    d.to_pickle(a.out)
    print(f"{len(d)} rows, {d.shape[1]} columns -> {a.out} in {time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
