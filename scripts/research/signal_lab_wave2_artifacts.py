#!/usr/bin/env python3
"""Build, prove and hash the frozen Wave-2 NFL model artifacts. RESEARCH ONLY. Run ONCE, before week 6.

    python scripts/research/signal_lab_wave2_artifacts.py [--check]

1. WF-TOTAL: re-run the Wave-1 walk-forward procedure on the identical corpus and require every 2018-2025 fold
   coefficient to equal `game_evaluation_report.json` exactly; then serialize the 2026 fold (train 2015-2025).
2. Prop ridge: for every family, fit the 2026 fold (train 2016-2025) with the Wave-1 arithmetic and require its
   predictions on the Wave-1 2026 rows to equal `prop_oos_predictions.parquet` exactly.

Writes research/signal_discovery_wave2/models/{wf_total_2026.json, prop_models_2026.json, manifest.json}.
`--check` rebuilds in memory and compares with the committed files (no write).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from nfl_edge.signal_discovery import evaluate_props as EP
from nfl_edge.signal_discovery import wave2_models as M
from nfl_edge.signal_discovery.evaluate_game import walk_forward

OUT = ROOT / "research" / "signal_discovery_wave2" / "models"
W1 = ROOT / "research" / "signal_discovery_wave1"


def _wave1_runner():
    spec = importlib.util.spec_from_file_location("sdw1", ROOT / "scripts" / "research" / "signal_discovery_wave1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build() -> tuple[dict, dict, dict]:
    runner = _wave1_runner()
    set1 = runner.check_frozen(runner.SET1_FILE)
    # ---------------------------------------------------------------- WF-TOTAL
    spec = set1["walk_forward"]["WF-TOTAL"]
    rows, _ = runner._game_rows(list(range(2015, 2026)))
    rerun = walk_forward(rows, "WF-TOTAL", spec)
    report = json.loads((W1 / "game_evaluation_report.json").read_text())
    w1_folds = report["walk_forward"]["WF-TOTAL"]["folds"]
    proof_total = []
    for a, b in zip(rerun["folds"], w1_folds, strict=True):
        assert a["test_season"] == b["test_season"]
        diffs = {k: abs(a["coef"][k] - b["coef"][k]) for k in b["coef"]}
        proof_total.append({"test_season": a["test_season"], "n": a["n"], "max_abs_coef_diff": max(diffs.values())})
        if max(diffs.values()) != 0.0:
            raise SystemExit(f"WF-TOTAL fold {a['test_season']} does not reproduce Wave 1 exactly: {diffs}")
    total = M.fit_wf_total(rows, 2026, spec)
    # ---------------------------------------------------------------- prop ridge
    pmeta = json.loads((W1 / "player_features_manifest.json").read_text())
    pf = pd.read_parquet(W1 / "player_features.parquet")
    if runner.frame_sha(pf) != pmeta["frame_sha256"]:
        raise SystemExit("player feature table does not match its Wave-1 manifest; refusing")
    fams = set1["prop_families"]
    pspec = set1["prop_model"]
    pf = EP.add_baselines(pf, fams)
    oos = pd.read_parquet(W1 / "prop_oos_predictions.parquet")
    models, proof_props = {}, []
    for fam in fams:
        feats, inter, _ = M.family_features(pspec, fam)
        tr = M.prop_training_rows(pf, fam)
        d = EP.family_rows(pf, fam)
        te = d[d["season"] == M.PROP_TEST_SEASON]
        if len(tr) < 300 or len(te) == 0:
            continue
        params = M.fit_prop(tr, fam, feats, inter)
        mine = M.predict_prop(params, te)
        ref_pred, _, ref_resid = EP._fit_predict(tr, te, fam, feats, inter)
        w1 = oos[(oos["family"] == fam["id"]) & (oos["season"] == M.PROP_TEST_SEASON)]
        got = te.assign(pred=mine)[["game_id", "player_id", "pred"]].merge(
            w1[["game_id", "player_id", "pred"]], on=["game_id", "player_id"], suffixes=("", "_w1"), how="outer"
        )
        if got["pred"].isna().any() or got["pred_w1"].isna().any():
            raise SystemExit(f"{fam['id']}: the 2026 rows differ from Wave 1")
        max_diff = float(np.max(np.abs(got["pred"] - got["pred_w1"])))
        if max_diff > 1e-9 or float(np.max(np.abs(mine - ref_pred))) != 0.0:
            raise SystemExit(f"{fam['id']}: predictions do not reproduce Wave 1 ({max_diff})")
        if params["median_offset"] != float(np.median(ref_resid)):
            raise SystemExit(f"{fam['id']}: median offset differs")
        models[fam["id"]] = params
        proof_props.append({"family": fam["id"], "n_train": len(tr), "n_2026_rows": len(te), "max_abs_pred_diff_vs_wave1": max_diff})
    props = {"model": "PROP_RIDGE", "procedure": "evaluate_props._fit_predict (ridge lambda 1), 2026 walk-forward fold",
             "test_season": M.PROP_TEST_SEASON, "train_seasons": [2016, 2025], "families": models}
    proof = {"wf_total_folds": proof_total, "prop_families": proof_props,
             "wave1_set1_sha256": runner.canon_sha(set1), "player_features_frame_sha256": pmeta["frame_sha256"]}
    return total, props, proof


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    total, props, proof = build()
    if args.check:
        same = (json.loads((OUT / "wf_total_2026.json").read_text()) == total
                and json.loads((OUT / "prop_models_2026.json").read_text()) == props)
        print("artifacts reproduce" if same else "ARTIFACTS DIFFER")
        return 0 if same else 1
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "wf_total_2026.json").write_text(json.dumps(total, indent=1, sort_keys=True) + "\n")
    (OUT / "prop_models_2026.json").write_text(json.dumps(props, sort_keys=True) + "\n")
    manifest = {"generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "wf_total_2026_sha256": M.canonical_sha(total), "prop_models_2026_sha256": M.canonical_sha(props),
                "reproduction_proof": proof}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "reproduction_proof"}, indent=1))
    print(json.dumps(proof, indent=1)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
