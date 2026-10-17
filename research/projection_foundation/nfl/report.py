"""summary.json (sift.projection_foundation.sport_summary.v1) + RESULTS_NFL.md from the walk-forward results."""
from __future__ import annotations

import json
import os
import subprocess
import time

import numpy as np

from pf_core import VERSION as PF_VERSION
from pf_core.registry import md_table

from . import inventory as INV
from . import narrative as N
from . import pipeline as P

HERE = os.path.dirname(os.path.abspath(__file__))
PF_ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(PF_ROOT, "results")
MD = os.path.join(PF_ROOT, "RESULTS_NFL.md")
NAMES = {"A": "A_season_avg_shrunk", "B": "B_ewma_shrunk", "C": "C_opportunity_x_efficiency", "D": "D_opp_env_adjusted",
         "D_opp": "D_opp_adjusted_only", "E": "E_lightgbm_walkforward", "F": "F_stack", "MKT": "MKT_closing_implied_total",
         "INC_0.4.0": "incumbent_shadow-0.4.0", "INC_0.5.0": "challenger_shadow-0.5.0", "D_vac": "D_plus_vacated_opportunity",
         "F_vac": "F_plus_vacated_opportunity", "D_av": "D_plus_availability", "F_av": "F_plus_availability",
         "A_qs": "A_qb_starts_only", "B_qs": "B_qb_starts_only", "C_qs": "C_qb_starts_only", "D_qs": "D_qb_starts_env", "F_qs": "F_qb_starts_env_stack", "D_oracle_avail": "D_oracle_availability(bound)",
         "F_oracle_avail": "F_oracle_availability(bound)"}


def _sha():
    try:
        return subprocess.check_output(["git", "-C", PF_ROOT, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _d(x):
    if not x:
        return None
    return {"mean_diff": round(float(x["mean_diff"]), 5), "ci95": [round(float(v), 5) for v in x["ci95"]]}


def _sig(x):
    return x is not None and x["ci95"][1] < 0


def verdict(m, fr, best):
    if m.startswith("INC"):
        return "incumbent"
    if m == "A":
        return "baseline"
    if m == best:
        return "best"
    if m.endswith("oracle_avail"):
        return "rejected"   # not pregame information: an upper bound only
    vb = fr["models"][m].get("vs_best")
    if vb and vb["ci95"][0] <= 0 <= vb["ci95"][1]:
        return "competitive"
    return "rejected"


def readiness(fam, fr, hold, diag):
    best = fr["best_model"]
    v = fr["models"][best]["validation"]
    vb = fr["models"][best].get("vs_baseline")
    h = (hold or {}).get(fam, {}).get("holdout")
    if v["n_obs"] < 300 or not h:
        return "INSUFFICIENT DATA", f"validation n={v['n_obs']}; holdout {'missing' if not h else 'present'}"
    beats_val = best == "A" or _sig(vb)
    beats_hold = _sig(h["vs_baseline"]) if best != "A" else False
    worse_inc = h.get("vs_INC_0.4.0") is not None and h["vs_INC_0.4.0"]["ci95"][0] > 0
    cal_ok = 0.85 <= h["pit_var_ratio"] <= 1.15 and 0.75 <= h["cover_80"] <= 0.85
    if fr["kind"] == "binary":
        cal_ok = abs(h["bias"]) < 0.02
    bad_seg = []
    for col, rows in (diag.get("segments", {}).get(fam) or {}).items():
        if col in ("designation", "spread_bucket", "vacated_targets"):
            continue
        for r in rows:
            if r["n"] >= 300 and r["mean_actual"] > 0 and abs(r["bias"]) / r["mean_actual"] > 0.25:
                bad_seg.append(f"{col}={r['segment']} bias {r['bias']:+.2f} on mean {r['mean_actual']:.2f} (n={r['n']})")
    if worse_inc:
        return "NEEDS IMPROVEMENT", "frozen winner is significantly worse than the incumbent shadow-0.4.0 on holdout"
    if not beats_val:
        return "NEEDS IMPROVEMENT", "no ladder model beat the season-average baseline on validation"
    if beats_val and beats_hold and cal_ok and not bad_seg:
        return "READY", (f"{NAMES.get(best, best)} beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), "
                         f"holdout PIT variance ratio {h['pit_var_ratio']:.2f}, 80% coverage {h['cover_80']:.2f}, no subgroup with >25% relative bias")
    why = []
    if not beats_hold:
        why.append("holdout gain over baseline not significant")
    if not cal_ok:
        why.append(f"holdout calibration off (PIT var {h['pit_var_ratio']:.2f}, cover80 {h['cover_80']:.2f}, bias {h['bias']:+.3f})")
    if bad_seg:
        why.append("subgroup failure: " + "; ".join(bad_seg[:3]))
    return "SHADOW VALIDATION", "; ".join(why)


def build_summary(wf, frozen_doc, S):
    sel, hold, diag = wf["select"], wf.get("holdout", {}), wf.get("diagnostics", {})
    fams = []
    for fam, fr in sel["families"].items():
        best = fr["best_model"]
        models = []
        for m, r in fr["models"].items():
            if "validation" not in r:
                continue
            v = r["validation"]
            models.append({"model": NAMES.get(m, m), "split": "validation", "n_obs": v["n_obs"], "n_clusters": v["n_clusters"],
                           "mae": round(v["mae"], 4), "rmse": round(v["rmse"], 4), "bias": round(v["bias"], 4),
                           "crps": round(v["crps"], 5), "log_score": round(v["log_score"], 4), "cover_50": round(v["cover_50"], 4),
                           "cover_80": round(v["cover_80"], 4), "cover_90": round(v["cover_90"], 4),
                           "pit_var_ratio": round(v["pit_var_ratio"], 4), "vs_baseline": _d(r.get("vs_baseline")),
                           "vs_incumbent": _d(r.get("vs_incumbent")), "verdict": verdict(m, fr, best),
                           "distribution": r.get("dist")})
        h = hold.get(fam, {}).get("holdout")
        ho = None
        if h:
            ho = {"model": NAMES.get(h["model"], h["model"]), "n_obs": h["n_obs"], "mae": round(h["mae"], 4), "crps": round(h["crps"], 5),
                  "bias": round(h["bias"], 4), "cover_80": round(h["cover_80"], 4), "vs_baseline": _d(h["vs_baseline"]),
                  "vs_incumbent": _d(h.get("vs_INC_0.4.0"))}
        rd, why = readiness(fam, fr, hold, diag)
        spec = P.PLAYER_FAMILIES.get(fam)
        fams.append({"family": fam, "unit": fr["unit"], "opportunity_family": fr["opportunity_family"],
                     "population": fr["population"], "models": models, "best_model": NAMES.get(best, best), "holdout": ho,
                     "readiness": rd, "readiness_reason": why})
    out = {
        "schema": "sift.projection_foundation.sport_summary.v1", "sport": "NFL",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "code_sha": _sha(), "pf_core_version": PF_VERSION,
        "splits": {"development": "2016-2021 regular seasons (2012-2015 feature warm-up only)",
                   "validation": "2022-2023 regular seasons",
                   "holdout": "2024-2025 regular seasons (evaluated once, frozen candidates only)",
                   "check_2026": "2026 weeks 1-4, read-only accuracy check (already used in market discovery; never tuned on)",
                   "embargo": "2026 weeks >= 5: untouched market holdout, never scored here"},
        "inventory": INV.build(),
        "families": fams,
        "experiments": N.experiments(wf),
        "error_investigations": N.error_investigations(wf),
        "opponent_adjustment": N.opponent_adjustment(wf, S),
        "opportunity": N.opportunity(wf),
        "calibration": N.calibration(wf),
        "failed_experiments": N.failed_experiments(wf),
        "gate": {"summary": (wf.get("gate") or {}).get("pooled", {}),
                 "error_by_status": {f: v.get("validation", {}).get("error_by_status") for f, v in (wf.get("gate") or {}).get("by_family", {}).items()},
                 "team_reconciliation": (wf.get("gate") or {}).get("team_reconciliation")},
        "priorities": N.priorities(wf),
    }
    return out


def write(wf, frozen_doc, S):
    s = build_summary(wf, frozen_doc, S)
    json.dump(s, open(os.path.join(RESULTS, "summary.json"), "w"), indent=1, default=str)
    open(MD, "w").write(N.render_md(s, wf, frozen_doc))
    return s
