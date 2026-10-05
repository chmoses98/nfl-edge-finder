#!/usr/bin/env python3
"""Opponent-adjustment research arms (research/game_script_v2/PREREGISTRATION.md, sections 5-6).

  features  for each evaluation season Y: choose the ridge strengths on Y-2 / Y-1, build the PIT matchup
            features mx_<metric> for every team-game 2016..Y, and score the primitive diagnostic on Y
  run       one arm x one evaluation season: the frozen walk-forward with the arm's extra features / switches

Usage:
  python scripts/sim/oppadj_ablation.py features --seasons 2021,2022,2023,2024,2025
  python scripts/sim/oppadj_ablation.py run --arm A1 --seasons 2021 [--n-sims 10000]
"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import pandas as pd
from nfl_edge.sim import five_year as FY, opponent_adjust as O

CACHE = os.path.join(ROOT, "data", "cache", "game_script_v2")
ENV_PLAYS = ["mx_plays", "mx_sec_per_play"]
ENV_PASS = ["mx_neutral_pass_rate", "mx_neutral_proe"]
EFF_CARRY = ["mx_designed_rush_epa", "mx_success_rate", "mx_explosive_rate"]
EFF_TARGET = ["mx_dropback_epa", "mx_success_rate", "mx_explosive_rate"]
ARMS = {
    "A1": {"plays_extra": ENV_PLAYS, "pass_rate_extra": ENV_PASS},
    "A2": {"carry_extra": EFF_CARRY, "target_extra": EFF_TARGET},
    "A3": {"plays_extra": ENV_PLAYS, "pass_rate_extra": ENV_PASS, "carry_extra": EFF_CARRY, "target_extra": EFF_TARGET},
    "A4": {"opponent_def": True},
    "A5": {"opponent_def": True, "plays_extra": ENV_PLAYS, "pass_rate_extra": ENV_PASS},
    # stage 2 (PREREGISTRATION.md addendum): the code-audit repair of the outside-the-eligible-set share
    "R1": {"outside_share_repair": True},
}


def features(seasons):
    os.makedirs(os.path.join(CACHE, "oppadj"), exist_ok=True)
    mt = O.metric_table(range(2016, max(seasons) + 1))
    diag = {}
    for y in seasons:
        sel = O.select_lambdas(mt, y)
        mx = O.matchup_features(mt[mt["season"] <= y], range(2016, y + 1), sel["lambdas"])
        mx.to_parquet(os.path.join(CACHE, "oppadj", f"mx_{y}.parquet"))
        diag[str(y)] = {"lambda_selection": sel, "primitive": O.primitive_diagnostic(mt[mt["season"] <= y], y, sel["lambdas"])}
        print(y, sel["lambdas"], flush=True)
        json.dump(diag, open(os.path.join(CACHE, "oppadj", "features_diagnostic.json"), "w"), indent=1)


def _attach(season):
    mx = pd.read_parquet(os.path.join(CACHE, "oppadj", f"mx_{season}.parquet"))
    cols = [c for c in mx.columns if c.startswith("mx_")]
    mx = mx[["game_id", "team"] + cols]

    def hook(frames, s):
        assert s == season
        out = dict(frames)
        for k in ("team", "carries", "targets"):
            out[k] = frames[k].drop(columns=[c for c in cols if c in frames[k].columns]).merge(mx, on=["game_id", "team"], how="left")
        return out
    return hook


def run(arm, seasons, n_sims):
    for y in seasons:
        out = os.path.join(CACHE, "arms", arm)
        rec = FY.run_season(y, n_sims=n_sims, out_dir=out, arm=ARMS[arm], frames_hook=_attach(y))
        print(arm, y, rec["run"]["games_simulated"], "games", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["features", "run"])
    ap.add_argument("--seasons", default="2021,2022,2023,2024,2025")
    ap.add_argument("--arm", default="A1")
    ap.add_argument("--n-sims", type=int, default=10000)
    a = ap.parse_args()
    seasons = [int(s) for s in a.seasons.split(",")]
    features(seasons) if a.cmd == "features" else run(a.arm, seasons, a.n_sims)


if __name__ == "__main__":
    main()
