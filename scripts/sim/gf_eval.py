#!/usr/bin/env python3
"""Game Flow Intelligence Championship (RESEARCH_ONLY): protocol, scoring and report.

Primary metrics (lower is better; predefined): halftime-margin CRPS, halftime-total CRPS, Brier of comp4q (within 8 entering Q4),
lead14 (either team leads by 14+ at any point), comeback10 (trailed by 10+ and won).  A challenger ADVANCES only if, on the
SELECTION seasons pooled, it improves at least one primary metric by >= 0.5% (relative to G0) AND no primary metric is worse
than G0 by more than 0.5% AND the improved metric improves in every selection season.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, warnings
warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from scripts.sim import gf_models as GM, gf_data as GD

OUT, RES = GM.OUT, GM.RES
DEV, SEL, HOLD, REUSED = [2006, 2007], [2008, 2009], [2010, 2011, 2012], list(range(2013, 2026))
PRIM = ["crps_ht_m", "crps_ht_t", "br_comp4q", "br_lead14", "br_comeback10"]
SEC = ["br_lc4", "br_home_lead7_ht", "br_away_lead7_ht", "br_drought20", "ae_h2_t"]
THRESH = 0.005
_FLOW = None


def flow():
    global _FLOW
    if _FLOW is None:
        _FLOW = GM.flow_table().set_index("game_id")
    return _FLOW


def load_rec(mid, seasons):
    parts = [np.load(os.path.join(RES, f"{mid}_{Y}.npz"), allow_pickle=True) for Y in seasons]
    return {k: np.concatenate([p[k] for p in parts]) for k in ("game_id", "pm", "pt", "pe", "mh2")}


def metrics(rec) -> pd.DataFrame:
    F = flow().loc[rec["game_id"]]; n = len(F)
    im = np.clip(np.round(F.ht_m.to_numpy()) + 50, 0, 100).astype(int); it = np.clip(np.round(F.ht_t.to_numpy()), 0, 80).astype(int)
    cm, ct = np.cumsum(rec["pm"], 1), np.cumsum(rec["pt"], 1)
    o = pd.DataFrame({"game_id": rec["game_id"], "season": F.season.to_numpy(),
                      "crps_ht_m": ((cm - (np.arange(GM.NPM)[None, :] >= im[:, None])) ** 2).sum(1), "crps_ht_t": ((ct - (np.arange(GM.NPT)[None, :] >= it[:, None])) ** 2).sum(1)})
    for j, e in enumerate(GM.EV):
        o[f"br_{e}"] = (rec["pe"][:, j] - F[e].to_numpy(float)) ** 2; o[f"p_{e}"] = rec["pe"][:, j]; o[f"y_{e}"] = F[e].to_numpy(float)
    o["ae_h2_t"] = np.abs(rec["mh2"] - F.h2_t.to_numpy(float))
    return o


def mix(recs, w):
    w = np.asarray(w) / np.sum(w); return {"game_id": recs[0]["game_id"], "pm": sum(a * r["pm"] for a, r in zip(w, recs)), "pt": sum(a * r["pt"] for a, r in zip(w, recs)),
                                           "pe": sum(a * r["pe"] for a, r in zip(w, recs)), "mh2": sum(a * r["mh2"] for a, r in zip(w, recs))}


def rel(base, d, cols=PRIM, seasons=None):
    if seasons is not None:
        base, d = base[base.season.isin(seasons)], d[d.season.isin(seasons)]
    return {c: float(d[c].mean() / base[c].mean() - 1) for c in cols}


def tune_bandwidth():
    best = None
    for bw in GM.BW:
        d = metrics(load_rec(f"G0_{bw}", DEV)); b = metrics(load_rec("GU", DEV)); r = float(np.mean(list(rel(b, d).values())))
        print(f"G0 {bw}: mean relative change vs unconditional on dev = {100 * r:+.2f}%")
        if best is None or r < best[0]:
            best = (r, bw)
    return best[1]


def advance(base, d):
    r_all = rel(base, d, seasons=SEL); per = [rel(base, d, seasons=[s]) for s in SEL]
    improved = [c for c in PRIM if r_all[c] <= -THRESH and all(p[c] < 0 for p in per)]
    harmed = [c for c in PRIM if r_all[c] > THRESH]
    return {"rel_selection": r_all, "improved_metrics": improved, "harmed_metrics": harmed, "advances": bool(improved) and not harmed}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["dev0", "dev", "select", "freeze", "final", "report"]); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.cmd == "dev0":
        GM.run(["GU"] + [f"G0_{b}" for b in GM.BW], DEV)
    elif a.cmd == "dev":
        bw = tune_bandwidth(); json.dump({"bandwidth": bw}, open(os.path.join(OUT, "tuned.json"), "w"))
        GM.run([f"G1_{bw}", f"G2_{bw}", f"G3_{bw}", "G4"], DEV)
    elif a.cmd == "select":
        bw = json.load(open(os.path.join(OUT, "tuned.json")))["bandwidth"]; GM.run(["GU", f"G0_{bw}", f"G1_{bw}", f"G2_{bw}", f"G3_{bw}", "G4"], SEL)
    elif a.cmd == "freeze":
        bw = json.load(open(os.path.join(OUT, "tuned.json")))["bandwidth"]; g0 = metrics(load_rec(f"G0_{bw}", SEL)); res = {}
        for m in (f"G1_{bw}", f"G2_{bw}", f"G3_{bw}", "G4"):
            res[m] = advance(g0, metrics(load_rec(m, SEL))); print(m, {k: (round(100 * v, 2) if isinstance(v, float) else v) for k, v in res[m]["rel_selection"].items()}, res[m]["advances"])
        adv = [m for m, v in res.items() if v["advances"]]
        fz = {"bandwidth": bw, "advance_results": res, "advancing": adv, "split": {"development": DEV, "selection": SEL, "final_holdout": HOLD, "reused_evidence": [2013, 2025]},
              "models_for_final": ["GU", f"G0_{bw}", f"G1_{bw}", f"G2_{bw}", f"G3_{bw}", "G4"], "g5_components": [f"G0_{bw}"] + adv,
              "code_sha256": hashlib.sha256(b"".join(open(os.path.join(ROOT, p), "rb").read() for p in ["scripts/sim/gf_data.py", "scripts/sim/gf_models.py"])).hexdigest()}
        json.dump(fz, open(os.path.join(OUT, "frozen.json"), "w"), indent=1); print("advancing:", adv)
    elif a.cmd == "final":
        fz = json.load(open(os.path.join(OUT, "frozen.json")))
        assert fz["code_sha256"] == hashlib.sha256(b"".join(open(os.path.join(ROOT, p), "rb").read() for p in ["scripts/sim/gf_data.py", "scripts/sim/gf_models.py"])).hexdigest(), "code changed since freeze"
        GM.run(fz["models_for_final"], HOLD + REUSED)
    elif a.cmd == "report":
        import scripts.sim.gf_report as R; R.main()


if __name__ == "__main__":
    main()
