#!/usr/bin/env python3
"""Freeze the 2026 Wave-2 arm components the prospective runner grafts into the incumbent bundle.

S1: the selected form (S1-1, chosen on <= 2020) refitted on the 2018-2025 training seasons with expected shares
cross-fitted by season and the incumbent bundle_2026's OTHER share. Q1: the selected form (Q1-0, chosen on <= 2020)
refitted on 2018-2025. Training is not validation: parameters may use every completed season; the FORMS may not change.
Output: research/game_script_v2/wave2/components_2026.json
"""
from __future__ import annotations
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
from nfl_edge.sim import qb_regimes as QR, share_dispersion as SD, training as T

OUT = os.path.join(ROOT, "research", "game_script_v2", "wave2", "components_2026.json")


def main():
    b = json.load(open(os.path.join(ROOT, "research", "simulation_engine", "bundle_2026.json")))
    frames = T.assemble(range(2016, 2026), verbose=lambda *x: None, priors=T.fit_priors_for(2026))
    e = frames["eligible"]; e = e[e["season"].isin(b["train_seasons"])]
    s1 = {k: SD.fit_for_bundle(e, b["other_share"][k], k, "S1-1") for k in ("carry", "target")}
    qm = QR.fit(QR.qb1_rows(e), conditional=False)
    qq = QR.mixture_quantiles(qm, np.asarray(qm["unconditional"]))
    out = {"for_bundle": "research/simulation_engine/bundle_2026.json", "bundle_train_seasons": b["train_seasons"],
           "selected_forms": {"S1": "S1-1", "Q1": "Q1-0"}, "S1": s1,
           "Q1": {"qb_share": {"quantiles": qq, "n": qm["n"], "p_below_half": float(np.mean(np.asarray(qq) < 0.5)), "regime_model": qm}},
           "research_only": True}
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    print({k: round(float(np.exp(v["b0"])), 2) for k, v in s1.items()}, qm["unconditional"])


if __name__ == "__main__":
    main()
