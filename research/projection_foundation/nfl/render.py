"""Markdown rendering helpers for RESULTS_NFL.md (tables only; prose lives in narrative.py)."""
from __future__ import annotations

import numpy as np

from pf_core.registry import md_table

ORDER = ["team_pass_attempts", "team_rush_attempts", "team_points", "targets", "receptions", "receiving_yards", "carries",
         "rushing_yards", "passing_attempts", "completions", "passing_yards", "passing_tds", "anytime_td"]


def ci(d, nd=3):
    if not d:
        return "—"
    lo, hi = d["ci95"]
    star = " ✔" if hi < 0 else (" ✘" if lo > 0 else "")
    return f"{d['mean_diff']:+.{nd}f} [{lo:+.{nd}f}, {hi:+.{nd}f}]{star}"


def fam_table(fam, fr, names):
    rows = []
    for m, r in sorted(fr["models"].items(), key=lambda kv: kv[1].get("validation", {}).get("crps", 9e9)):
        v = r.get("validation")
        if not v:
            continue
        nd = 4 if fr["kind"] == "binary" else 3
        rows.append({"Model": names.get(m, m) + (" ★" if m == fr["best_model"] else ""), "dist": r.get("dist", ""),
                     "n": v["n_obs"], "MAE": round(v["mae"], nd), "RMSE": round(v["rmse"], nd), "Bias": round(v["bias"], nd),
                     "CRPS": round(v["crps"], 4), "cover80": round(v["cover_80"], 3), "PIT var": round(v["pit_var_ratio"], 2),
                     "vs A (CRPS)": ci(r.get("vs_baseline"), 4), "vs shadow-0.4.0": ci(r.get("vs_incumbent"), 4),
                     "vs shadow-0.5.0": ci(r.get("vs_challenger_0_5_0"), 4)})
    return md_table(rows, list(rows[0].keys()) if rows else [])


def holdout_table(hold, names):
    rows = []
    for fam in ORDER:
        fo = hold.get(fam) or {}
        for split in ("holdout", "check2026"):
            h = fo.get(split)
            if not h:
                continue
            rows.append({"family": fam, "split": split, "model": names.get(h["model"], h["model"]), "n": h["n_obs"],
                         "MAE": round(h["mae"], 3), "Bias": round(h["bias"], 3), "CRPS": round(h["crps"], 4),
                         "A CRPS": round(h["baseline_A"]["crps"], 4), "vs A": ci(h["vs_baseline"], 4),
                         "0.4.0 CRPS": round(h["INC_0.4.0"]["crps"], 4) if "INC_0.4.0" in h else "—",
                         "vs 0.4.0": ci(h.get("vs_INC_0.4.0"), 4), "vs 0.5.0": ci(h.get("vs_INC_0.5.0"), 4),
                         "cover80": round(h["cover_80"], 3), "PIT var": round(h["pit_var_ratio"], 2)})
    return md_table(rows, list(rows[0].keys()) if rows else [])


def dist_table(sel):
    rows = []
    for fam in ORDER:
        fr = sel["families"].get(fam)
        if not fr:
            continue
        b = fr["best_model"]
        ds = fr["dist_selection"].get(b, {})
        best_d = min(ds, key=lambda k: ds[k]["val_crps"]) if ds else ""
        row = {"family": fam, "mean model": b, "chosen": best_d}
        for k, v in ds.items():
            row[k] = f"{v['val_crps']:.4f} / {v['val_log_score']:.3f}"
        rows.append(row)
    cols = ["family", "mean model", "chosen", "poisson", "nb", "nb_binned", "empirical_ratio", "normal_binned", "empirical_resid", "bernoulli"]
    cols = [c for c in cols if any(c in r for r in rows)]
    return md_table(rows, cols)


def threshold_table(hold):
    rows = []
    for fam in ORDER:
        h = (hold.get(fam) or {}).get("holdout")
        if not h:
            continue
        for t in h.get("threshold_reliability", []):
            rows.append({"family": fam, "rung": t["rung"], "mean P": round(t["mean_p"], 3), "hit rate": round(t["hit_rate"], 3),
                         "over(+)/under(-) confidence": f"{(t['mean_p'] - t['hit_rate']) * 100:+.1f} pp",
                         "Brier": round(t["brier"], 4), "ECE": round(t["ece"], 4)})
    return md_table(rows, list(rows[0].keys()) if rows else [])


def segment_tables(diag, fam, cols):
    out = []
    seg = (diag.get("segments") or {}).get(fam) or {}
    for c in cols:
        rows = seg.get(c) or []
        if not rows:
            continue
        rr = [{"segment": r["segment"], "n": r["n"], "mean actual": round(r["mean_actual"], 2), "mean proj": round(r["mean_pred"], 2),
               "bias": round(r["bias"], 2), "rel bias": f"{r['bias'] / r['mean_actual'] * 100:+.1f}%" if r["mean_actual"] else "—",
               "MAE": round(r["mae"], 2)} for r in rows]
        out.append(f"*{fam} by {c}*\n\n" + md_table(rr, list(rr[0].keys())))
    return "\n".join(out)


def pct(x):
    return f"{x * 100:.1f}%"
