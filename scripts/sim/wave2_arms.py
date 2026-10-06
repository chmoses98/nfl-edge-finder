#!/usr/bin/env python3
"""Wave 2 arm runner: the frozen walk-forward (five_year.run_season) with one Wave-2 arm switched on.

  python scripts/sim/wave2_arms.py --arm S1 --seasons 2020 --phase dev     # DEVELOPMENT (<= 2020)
  python scripts/sim/wave2_arms.py --arm S1 --seasons 2021 --phase diag    # CONTAMINATED_DIAGNOSTIC (2021-2025)

Writes data/cache/game_script_v2/wave2/<phase>/<arm>/. The incumbent of a phase is arm A0 (no switch).
"""
from __future__ import annotations
import argparse, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import five_year as FY

CACHE = os.path.join(ROOT, "data", "cache", "game_script_v2", "wave2")
ARMS = {"A0": {}, "S1": {"s1": True, "s1_form": "S1-1"}, "Q1": {"q1": True, "q1_form": "Q1-0"}, "A1T0": {"a1_horizon": "T0_INACTIVES"},
        "A1T24": {"a1_horizon": "T24"}}


def frames_hook_for(arm: str):
    spec = ARMS[arm]
    if not spec.get("a1_horizon") and not (spec.get("q1") and spec.get("q1_form") == "Q1"):
        return None
    def hook(frames, season):
        out = frames
        if spec.get("q1") and spec.get("q1_form") == "Q1":
            from nfl_edge.sim import qb_regimes as QR
            out = QR.attach_features(out)
        if spec.get("a1_horizon"):
            from nfl_edge.sim import availability_horizons as AH
            out = AH.apply_horizon(out, season, spec["a1_horizon"])
        return out
    return hook


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--seasons", required=True)
    ap.add_argument("--phase", required=True, choices=["dev", "diag"])
    ap.add_argument("--n-sims", type=int, default=10000)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    for y in [int(s) for s in a.seasons.split(",")]:
        if a.phase == "dev" and y > 2020:
            raise SystemExit("development runs are <= 2020 only")
        out = a.out or os.path.join(CACHE, a.phase, a.arm)
        rec = FY.run_season(y, n_sims=a.n_sims, out_dir=out, arm=ARMS[a.arm] or None, frames_hook=frames_hook_for(a.arm),
                            limit=a.limit or None)
        print(a.arm, y, rec["run"]["games_simulated"], "games", flush=True)


if __name__ == "__main__":
    main()
