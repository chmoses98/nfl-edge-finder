#!/usr/bin/env python3
"""Game Script Discovery Lab (RESEARCH_ONLY) -- selection statistics.

Reads the cached per-game scores of every candidate and applies the preregistered screening rule
(research/game_script_discovery_lab/PREREGISTRATION.md):

  primary metrics (lower is better, vs A0 on identical games): P1 margin CRPS, P2 total CRPS, P3 six-class script log loss,
  P4 nine-cell (joint) log loss.
  screening   = SELECTION seasons 2021-2023 only: paired game-level bootstrap, max-t (White reality-check) adjusted p over
                every candidate x primary metric tested.
  confirm     = CONFIRMATION seasons 2024-2025, read once, for candidates that pass screening (and, descriptively, the top five).
"""
from __future__ import annotations
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from scipy import stats
from scripts.sim.gsdl_tournament import CANDIDATES, RES, OUT, SELECTION, CONFIRM, SEASONS, KEYS

PRIMARY = {"P1_margin_crps": "crps_m", "P2_total_crps": "crps_t", "P3_script6_logloss": "ll6", "P4_joint9_logloss": "ll9"}
B = 5000
MATERIAL = 0.005          # the repo's 0.5% relative materiality bar
HARM = 0.0025


def load(cid):
    return pd.read_parquet(os.path.join(RES, f"{cid}.parquet")).sort_values("game_id").reset_index(drop=True)


def paired(base, cand, col, seasons):
    b = base[base.season.isin(seasons)]; c = cand[cand.season.isin(seasons)]
    assert (b.game_id.values == c.game_id.values).all()
    ok = b[col].notna() & c[col].notna()
    return (c[col].to_numpy()[ok] - b[col].to_numpy()[ok]), b[col].to_numpy()[ok].mean()


def main():
    base = load("A0")
    ids = [c for c in CANDIDATES if c != "A0"]
    data = {cid: load(cid) for cid in ids}
    rng = np.random.default_rng(20261013)
    # ---- screening on the selection seasons
    games = base[base.season.isin(SELECTION)].game_id.values; n = len(games)
    idx = rng.integers(0, n, size=(B, n))
    tobs, rel, dmat = {}, {}, {}
    for cid in ids:
        for pn, col in PRIMARY.items():
            d, bm = paired(base, data[cid], col, SELECTION)
            if len(d) != n:                      # six-class excludes ties: align by padding with zeros
                full = base[base.season.isin(SELECTION)]; mask = full[col].notna().to_numpy(); dd = np.zeros(n); dd[mask] = d; d = dd
            se = d.std(ddof=1) / np.sqrt(n); tobs[(cid, pn)] = d.mean() / se if se > 0 else 0.0
            rel[(cid, pn)] = d.mean() / bm; dmat[(cid, pn)] = d
    keys = list(tobs)
    tstar = np.empty((B, len(keys)))
    for j, k in enumerate(keys):
        d = dmat[k]; dc = d - d.mean(); s = dc[idx]
        tstar[:, j] = s.mean(1) / np.maximum(s.std(1, ddof=1) / np.sqrt(n), 1e-12)
    minstar = tstar.min(1)                          # most negative t = best improvement under the null
    padj = {k: float((minstar <= tobs[k]).mean()) for k in keys}
    praw = {k: float(stats.norm.cdf(tobs[k])) for k in keys}

    # ---- confirmation on the held-out historical seasons (descriptive for non-qualifiers)
    gc = base[base.season.isin(CONFIRM)].game_id.values; nc = len(gc); idc = rng.integers(0, nc, size=(B, nc))
    conf = {}
    for cid in ids:
        for pn, col in PRIMARY.items():
            full = base[base.season.isin(CONFIRM)]; mask = full[col].notna().to_numpy()
            d, bm = paired(base, data[cid], col, CONFIRM); dd = np.zeros(nc); dd[mask] = d
            bs = dd[idc].mean(1) / bm
            conf[(cid, pn)] = {"rel": float(dd.mean() / bm), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                               "by_season": {int(s): float(paired(base, data[cid], col, [s])[0].mean() / paired(base, data[cid], col, [s])[1]) for s in CONFIRM}}

    # ---- all-season per-season relative change (consistency) and calibration
    rows = []
    for cid in ids:
        r = {"id": cid, "stage": CANDIDATES[cid]["stage"], "desc": CANDIDATES[cid]["desc"], "pit_eligible": CANDIDATES[cid]["pit_eligible"]}
        for pn, col in PRIMARY.items():
            r[f"sel_rel_{pn}"] = rel[(cid, pn)]; r[f"sel_p_raw_{pn}"] = praw[(cid, pn)]; r[f"sel_p_adj_{pn}"] = padj[(cid, pn)]
            r[f"conf_rel_{pn}"] = conf[(cid, pn)]["rel"]; r[f"conf_ci_{pn}"] = conf[(cid, pn)]["ci95"]
            r[f"by_season_{pn}"] = {int(s): float(paired(base, data[cid], col, [s])[0].mean() / paired(base, data[cid], col, [s])[1]) for s in SEASONS}
        rows.append(r)
    summ = pd.DataFrame(rows)

    def calib(df):
        o = {}
        for pit in ("pit_m", "pit_t"):
            h = np.histogram(df[pit], bins=10, range=(0, 1))[0]; o[f"{pit}_chi2_p"] = float(stats.chisquare(h).pvalue)
            o[f"{pit}_cov50"] = float(((df[pit] >= .25) & (df[pit] <= .75)).mean()); o[f"{pit}_cov90"] = float(((df[pit] >= .05) & (df[pit] <= .95)).mean())
        o["bias_m"] = float((df["y_m"] - df["spread"] - (df["mean_m"] - df["spread"])).mean()) if "mean_m" in df else np.nan
        for k in KEYS:
            o[f"key{k}_pred"] = float(df[f"key{k}_p"].mean()); o[f"key{k}_obs"] = float(df[f"key{k}_obs"].mean())
        o["one_pred"] = float(df["one_p"].mean()); o["one_obs"] = float(df["one_obs"].mean())
        o["blow_pred"] = float(df["blow_p"].mean()); o["blow_obs"] = float(df["blow_obs"].mean())
        o["key_brier_sum"] = float(sum(df[f"key{k}_br"].mean() for k in KEYS)); o["one_brier"] = float(df["one_br"].mean()); o["blow_brier"] = float(df["blow_br"].mean())
        return o
    cal = {"A0": calib(base), **{cid: calib(data[cid]) for cid in ids}}
    base_prim = {pn: float(base[col].mean()) for pn, col in PRIMARY.items()}
    base_season = {pn: {int(s): float(base[base.season == s][col].mean()) for s in SEASONS} for pn, col in PRIMARY.items()}
    # best (minimum) adjusted p per candidate, then rank
    summ["min_p_adj"] = summ[[f"sel_p_adj_{p}" for p in PRIMARY]].min(axis=1)
    summ["best_rel"] = summ[[f"sel_rel_{p}" for p in PRIMARY]].min(axis=1)
    summ = summ.sort_values(["min_p_adj", "best_rel"]).reset_index(drop=True)
    # qualification rule (all must hold): material (>=0.5%) improvement on a primary metric on selection AND confirmation with the
    # same sign, adjusted p < 0.10 on selection, no primary metric worse than 0.25% on selection, PIT chi2 p >= 0.01, PIT-eligible.
    qual = []
    for r in summ.itertuples():
        best = min(PRIMARY, key=lambda p: getattr(r, f"sel_rel_{p}"))
        c = cal[r.id]; ok = {
            "material_on_selection": getattr(r, f"sel_rel_{best}") <= -MATERIAL,
            "adj_p_lt_0.10": getattr(r, f"sel_p_adj_{best}") < 0.10,
            "confirmed_same_sign_material": getattr(r, f"conf_rel_{best}") <= -MATERIAL and getattr(r, f"conf_ci_{best}")[1] < 0,
            "no_primary_harm": all(getattr(r, f"sel_rel_{p}") <= HARM for p in PRIMARY),
            "pit_calibrated": c["pit_m_chi2_p"] >= 0.01 and c["pit_t_chi2_p"] >= 0.01,
            "pit_eligible": bool(r.pit_eligible)}
        qual.append({"id": r.id, "metric": best, "checks": ok, "qualifies": all(ok.values())})
    out = {"baseline_A0": base_prim, "baseline_A0_by_season": base_season, "n_candidates_tested": len(ids) + 3,
           "n_in_multiplicity_set": len(ids) * len(PRIMARY), "selection_seasons": SELECTION, "confirmation_seasons": CONFIRM,
           "ranking": summ.drop(columns=[]).to_dict(orient="records"), "qualification": qual, "calibration": cal}
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    pd.set_option("display.width", 250)
    show = summ[["id", "sel_rel_P1_margin_crps", "sel_rel_P2_total_crps", "sel_rel_P3_script6_logloss", "sel_rel_P4_joint9_logloss", "min_p_adj"]].copy()
    for c in show.columns[1:5]: show[c] = (100 * show[c]).round(2)
    print(show.to_string(index=False)); print("qualifying:", [q["id"] for q in qual if q["qualifies"]])


if __name__ == "__main__":
    main()
