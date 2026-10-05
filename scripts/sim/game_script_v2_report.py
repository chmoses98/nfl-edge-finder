#!/usr/bin/env python3
"""Build the machine-readable research artifacts of the GAME SCRIPT V2 / five-season study.

  baseline     research/game_script_v2/baseline_5y.json        (frozen incumbent, 2021-2025, + audits)
  validation   research/game_script_v2/validation_5y.json      (injury redistribution, weather, score-path arm)
  ablation     research/game_script_v2/opponent_adjustment_ablation.json   (arms A1-A5, R1 vs A0)

Inputs are the local outputs of scripts/sim/baseline_5y.py, scripts/sim/oppadj_ablation.py and the naive-baseline
cache (data/cache/game_script_v2/, never committed). scripts/sim/script_backtest.py writes
script_calibration_5y.json; scripts/sim/write_game_script_v2.py renders every Markdown summary from the JSON.

Usage: python scripts/sim/game_script_v2_report.py {baseline,validation,ablation} [--seasons ...]
"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from nfl_edge.sim import (ablation_report as AR, baseline_report as BR, five_year as FY, injury_validation as IV,
                          score_path as SP, weather_research as WR)

OUT = os.path.join(ROOT, "research", "game_script_v2")
CACHE = os.path.join(ROOT, "data", "cache", "game_script_v2")
START_SHA = "d5c7f8dfa014b9be3aff7550734b6208e7314554"


def _dump(name, obj):
    os.makedirs(OUT, exist_ok=True)
    json.dump(obj, open(os.path.join(OUT, name), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("wrote", name)


def baseline(seasons):
    naive = {}
    for y in seasons:
        p = os.path.join(CACHE, "naive", f"naive_{y}.parquet")
        if not os.path.exists(p):
            BR.naive_baseline(y).to_parquet(p)
        naive[y] = pd.read_parquet(p)
    rep = BR.pooled_and_by_season(FY.DEFAULT_OUT, seasons, naive)
    rp = json.load(open(os.path.join(OUT, "reproduction_2023_2025.json")))
    rep["reproduction"] = {"diagnosis": rp["diagnosis"],
                           "seasons": {y: {"components_differing": sorted(k for k, v in s["bundle_components"].items() if v == "DIFFERS"),
                                           "other_share": s["other_share"], "team_stats_differing": s["team_stats_differing"],
                                           "max_abs_rel_change": s["max_abs_rel_change"]} for y, s in rp["seasons"].items()}}
    rep["meta"] = {"start_main_sha": START_SHA, "seasons": seasons, "n_sims": 10000,
                   "evidence_class": {str(y): FY.EVIDENCE_CLASS[y] for y in seasons},
                   "command": "python scripts/sim/baseline_5y.py --seasons 2021,2022,2023,2024,2025 --n-sims 10000",
                   "equivalent_to": "python scripts/sim/walkforward.py --seasons 2021,2022,2023,2024,2025 --n-sims 10000 --out-dir DIR",
                   "bootstrap": {"resamples": BR.B, "seed": BR.SEED, "unit": "game"},
                   "floors": __import__("nfl_edge.sim.backtest", fromlist=["FLOORS"]).FLOORS}
    _dump("baseline_5y.json", rep)


def validation(seasons):
    out = {"injury_redistribution": IV.run(FY.DEFAULT_OUT, seasons)}
    tm = {}
    for y in seasons:
        for g in json.load(open(os.path.join(FY.DEFAULT_OUT, f"scripts_{y}.json"))):
            tm[g["game_id"]] = g["team_means"]
    out["weather"] = {"historical": WR.historical_descriptive(range(2016, max(seasons) + 1), tm),
                      "prospective_2026": WR.prospective_accumulation(os.path.join(ROOT, "data", "context"))}
    path = SP.path_table(range(2016, max(seasons) + 1))
    rows = {y: np.load(os.path.join(FY.DEFAULT_OUT, f"rows_{y}.npz")) for y in seasons}
    ev = SP.evaluate(rows, path, seasons)
    sp = SP.summarize(ev, seasons)
    sp["pbp_final_mismatch_games"] = int((~path["pbp_final_matches"]).sum())
    sp["n_path_games"] = int(len(path))
    out["score_path"] = sp
    _dump("validation_5y.json", out)


def ablation(seasons, arms):
    diag = json.load(open(os.path.join(CACHE, "oppadj", "features_diagnostic.json")))
    res = {"features": diag, "arms": {}, "team_crps": {"A0": AR.team_crps(FY.DEFAULT_OUT, seasons)}}
    for a in arms:
        d = os.path.join(CACHE, "arms", a)
        if not all(os.path.exists(os.path.join(d, f"player_dists_{y}.parquet")) for y in seasons):
            res["arms"][a] = {"verdict": "NOT_RUN", "reason": "missing seasons"}
            continue
        res["arms"][a] = AR.evaluate_arm(FY.DEFAULT_OUT, d, seasons)
        res["team_crps"][a] = AR.team_crps(d, seasons)
        print(a, res["arms"][a]["verdict"], round(res["arms"][a]["pooled"]["primary"], 5), flush=True)
    import importlib.util
    spec = importlib.util.spec_from_file_location("oa", os.path.join(ROOT, "scripts", "sim", "oppadj_ablation.py"))
    oa = importlib.util.module_from_spec(spec); spec.loader.exec_module(oa)
    res["arm_specs"] = {a: oa.ARMS[a] for a in arms}
    res["meta"] = {"seasons": seasons, "material_threshold": AR.MATERIAL, "bootstrap": {"resamples": AR.B, "seed": AR.SEED, "unit": "game"},
                   "population": "paired on A0's scored rows (backtest.FLOORS on the A0 predictive mean)"}
    _dump("opponent_adjustment_ablation.json", res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["baseline", "validation", "ablation"])
    ap.add_argument("--seasons", default="2021,2022,2023,2024,2025")
    ap.add_argument("--arms", default="A1,A2,A3,A4,A5,R1")
    a = ap.parse_args()
    seasons = [int(s) for s in a.seasons.split(",")]
    {"baseline": lambda: baseline(seasons), "validation": lambda: validation(seasons),
     "ablation": lambda: ablation(seasons, a.arms.split(","))}[a.cmd]()


if __name__ == "__main__":
    main()
