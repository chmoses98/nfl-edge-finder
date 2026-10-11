#!/usr/bin/env python3
"""Convert PURE_PLAYER_V1 kit-format sidecar rows (pure_forecast.v0) to the shared `pure_forecast.v1` contract
(sift-sports-intelligence/pure-contract). Model-owned numbers are copied unchanged; v1 adds the schema version, the
frozen code hash, an explicit `participation_probability: null` (participation is not modelled: forecasts are
conditional on playing), declared sports-only sources and per-feature lineage.

    python3 scripts/research/pure_player_v1_v1sidecar.py --in v0.jsonl[.gz] --out v1.jsonl --frozen git:0441dfc
"""
from __future__ import annotations

import argparse
import gzip
import json

SOURCES = ("nflverse_stats_player_week", "nflverse_snap_counts", "nflverse_schedule_nonmarket_columns")


def convert(r: dict, frozen: str) -> dict:
    src = r["source_max_observed_at"]
    mf = r["model_features"]
    lineage = [{"name": k, "value": v, "source": SOURCES[0], "observed_at": src, "class": "sports_only"} for k, v in sorted(mf["lineage"].items())]
    return {"schema_version": "pure_forecast.v1", "sport": r["sport"], "game_id": r["game_id"], "player_id": r["player_id"],
            "statistic": r["statistic"], "as_of": r["as_of"], "kickoff": r["kickoff"], "source_max_observed_at": src,
            "projection_mode": r["projection_mode"], "model_version": r["model_version"], "model_frozen_hash": frozen,
            "conditional_on_playing": r["conditional_on_playing"], "participation_probability": None, "projection": r["projection"],
            "sources": [{"source_id": s, "class": "sports_only", "max_observed_at": src} for s in SOURCES],
            "feature_lineage": lineage,
            "x_notes": {"abstained_inputs": mf.get("abstained_inputs"), "population": mf.get("population"),
                        "train_seasons_observed_through": mf.get("train_seasons_observed_through")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frozen", required=True)
    a = ap.parse_args()
    op = gzip.open if a.inp.endswith(".gz") else open
    with op(a.inp, "rt") as fi, open(a.out, "w") as fo:
        for line in fi:
            if line.strip():
                fo.write(json.dumps(convert(json.loads(line), a.frozen), sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
