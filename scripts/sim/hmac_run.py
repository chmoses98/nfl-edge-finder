#!/usr/bin/env python3
"""Historical Model Architecture Championship (RESEARCH_ONLY): protocol driver.

  dev      score every registered model on the DEVELOPMENT seasons (tune bandwidths / GBT depth only)
  select   score on the SELECTION seasons (tuned variants + references) and choose family finalists
  freeze   write frozen.json (finalists, benchmark, split, code hashes) -- committed BEFORE any holdout season is scored
  final    score the frozen finalists on the FINAL HOLDOUT (SIFT-untouched seasons) and on the REUSED-EVIDENCE seasons
  report   leaderboard, paired bootstrap intervals, per-season, calibration, secondary targets
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, warnings
warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from scipy import stats
from scripts.sim import hmac_models as M

OUT, RES = M.OUT, M.RES
DEV, SEL, HOLD, REUSED = [2006, 2007], [2008, 2009], [2010, 2011, 2012], list(range(2013, 2026))
PRIM = {"P1_margin_crps": "crps_m", "P2_total_crps": "crps_t", "P3_script6_logloss": "ll6", "P4_joint9_logloss": "ll9"}
FAMILIES = ["A", "B", "C", "D", "E", "F"]


def load(i):
    return pd.read_parquet(os.path.join(RES, f"{i}.parquet")).sort_values("game_id").reset_index(drop=True)


def rel_vs(base, d, seasons, cols=PRIM):
    b, m = base[base.season.isin(seasons)], d[d.season.isin(seasons)]
    return {p: float(m[c].mean() / b[c].mean() - 1) for p, c in cols.items()}


def score_of(base, d, seasons):
    r = rel_vs(base, d, seasons); return float(np.mean(list(r.values()))), r


def sha(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(open(os.path.join(ROOT, p), "rb").read())
    return h.hexdigest()


CODE = ["scripts/sim/hmac_features.py", "scripts/sim/hmac_models.py", "scripts/sim/hmac_run.py", "scripts/sim/gsdl_features.py", "scripts/sim/gsdl_tournament.py"]


def cmd_choose():
    base = load("A1"); R = M.REG; out = {"development": {}, "selection": {}}
    # 1. development: pick bandwidth per centre type and GBT depth
    tuned = {}
    for centre in ("elo", "ff1", "ff2", "gbtA", "gbtB", "poss", "ens", "blend", "anchor"):
        cands = [i for i, s in R.items() if s.get("centre") == centre and s["dist"] == "kernel"]
        sc = {i: score_of(base, load(i), DEV)[0] for i in cands}; tuned[centre] = min(sc, key=sc.get); out["development"][centre] = sc
    gb = {c: score_of(base, load(tuned[c]), DEV)[0] for c in ("gbtA", "gbtB")}; keep_gbt = min(gb, key=gb.get)
    tuned = {c: v for c, v in tuned.items() if not (c.startswith("gbt") and c != keep_gbt)}
    # 2. selection: leaderboard of tuned variants and fixed references; best per family
    pool = ["A1", "A2", "A3"] + list(tuned.values()) + ["B_ff2_gauss", "D_poss_raw", "E_mix_A2_ens", "E_mix_A1_ens", "E_mix_A2_blend"]
    board = []
    for i in pool:
        sc, r = score_of(base, load(i), SEL); board.append({"id": i, "fam": R[i]["fam"], "mean_rel": sc, **r})
    board = sorted(board, key=lambda x: x["mean_rel"]); out["selection"] = board
    fin = {}
    for fam in FAMILIES:
        c = [b for b in board if b["fam"] == fam and b["id"] != "A1"] if fam == "A" else [b for b in board if b["fam"] == fam]
        if c:
            fin[fam] = c[0]["id"]
    finalists = list(dict.fromkeys(["A1"] + list(fin.values())))
    bench = fin["A"]
    # mixtures whose parts are not frozen finalists still need their parts at final time
    need = set(finalists)
    for i in list(need):
        need |= set(R[i].get("parts", []))
    frozen = {"split": {"burn_in": "2001-2002 (feature EWMA warm-up; models train from 2002)", "development": DEV, "selection": SEL, "final_holdout": HOLD,
                        "reused_evidence": [REUSED[0], REUSED[-1]]},
              "finalists": finalists, "family_winners": fin, "market_benchmark": bench, "incumbent": "A1", "models_to_run": sorted(need),
              "tuned_variants": tuned, "primary_metrics": PRIM, "code_sha256": sha(CODE), "selection_scores": out}
    json.dump(frozen, open(os.path.join(OUT, "frozen.json"), "w"), indent=1)
    print(json.dumps({"tuned": tuned, "family_winners": fin, "benchmark": bench}, indent=1))
    for b in board:
        print(f"{b['id']:18s} {b['fam']} mean {100 * b['mean_rel']:+.2f}%  " + "  ".join(f"{k[:2]} {100 * v:+.2f}" for k, v in b.items() if k.startswith("P")))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["dev", "select", "choose", "final", "report"]); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.cmd == "dev":
        M.run_models(list(M.REG), DEV)
    elif a.cmd == "select":
        M.run_models(list(M.REG), SEL)
    elif a.cmd == "choose":
        cmd_choose()
    elif a.cmd == "final":
        fz = json.load(open(os.path.join(OUT, "frozen.json")))
        assert fz["code_sha256"] == sha(CODE), "code changed since freeze"
        M.run_models(fz["models_to_run"], HOLD + REUSED)
    elif a.cmd == "report":
        import scripts.sim.hmac_report as R
        R.main()


if __name__ == "__main__":
    main()
