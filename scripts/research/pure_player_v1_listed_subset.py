#!/usr/bin/env python3
"""POST-HOC diagnostic (not preregistered, cannot change the verdict): PURE_PLAYER_V1 vs PURE_EWM_BASELINE on the
2025 player-games that Kalshi listed vs those it did not, with paired game-clustered CIs. Shows how a
market-inventory evaluation population would change the measured gain.

    python3 scripts/research/pure_player_v1_listed_subset.py <dir with the full study sidecars, e.g. the study --cache dir>
"""
from __future__ import annotations

import gzip
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts", "research"))
from pure_player_v1_study import boot_ci          # noqa: E402

D = os.path.join(ROOT, "research", "pure_player_v1")


def _lines(path):
    return gzip.open(path + ".gz", "rt") if os.path.exists(path + ".gz") else open(path)


def load(src, name):
    rows = [json.loads(x) for x in _lines(os.path.join(src, f"{name}.forecasts.jsonl"))]
    return pd.DataFrame({"game_id": [r["game_id"] for r in rows], "player_id": [r["player_id"] for r in rows],
                         "statistic": [r["statistic"] for r in rows], "mean": [r["projection"]["mean"] for r in rows]})


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, "sidecars")   # the full sidecars (study --cache dir)
    a, b = load(src, "PURE_PLAYER_V1"), load(src, "PURE_EWM_BASELINE")
    o = pd.DataFrame([json.loads(x) for x in _lines(os.path.join(src, "outcomes.jsonl"))])
    k = ["game_id", "player_id", "statistic"]
    m = a.merge(b, on=k, suffixes=("_a", "_b")).merge(o[k + ["actual"]], on=k)
    m = m[m.game_id.str.startswith("2025_")]
    lad = pd.read_parquet(os.path.join(ROOT, "research/signal_discovery_wave1/prop_ladders.parquet"))
    listed = set(zip(lad.gsis_id, lad.game_id))
    m["listed"] = [(p, g) in listed for p, g in zip(m.player_id, m.game_id)]
    out = {"note": "POST-HOC diagnostic; Kalshi 2025 listing joined after forecasting; never a model input", "by_stat": {}}
    for st, s in m.groupby("statistic"):
        out["by_stat"][st] = {}
        for lab, sub in (("listed", s[s.listed]), ("not_listed", s[~s.listed])):
            y = sub.actual.to_numpy(float)
            d = np.abs(sub.mean_a - y) - np.abs(sub.mean_b - y)
            out["by_stat"][st][lab] = {"n": int(len(sub)), "mae_pure": round(float(np.abs(sub.mean_a - y).mean()), 4),
                                       "mae_base": round(float(np.abs(sub.mean_b - y).mean()), 4), "delta_mae": round(float(d.mean()), 4),
                                       "delta_mae_ci95": boot_ci(d.to_numpy(float), sub.game_id.to_numpy(), 1000)}
    with open(os.path.join(D, "posthoc_listed_subset_2025.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    for st, v in out["by_stat"].items():
        print(st, v["listed"]["n"], v["listed"]["delta_mae"], v["listed"]["delta_mae_ci95"], "|", v["not_listed"]["n"], v["not_listed"]["delta_mae"], v["not_listed"]["delta_mae_ci95"])


if __name__ == "__main__":
    main()
