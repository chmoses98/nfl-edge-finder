#!/usr/bin/env python3
"""Runtime market-mutation test of PURE_PLAYER_V1 on the REAL football data, with a negative control.

For each mutation of the schedule's market columns (original / removed / randomized / partial_blank) this builds a
separate data root (the same bronze stats / snaps / crosswalk files, a mutated schedule), then

    PURE_PLAYER_V1   reruns load -> features -> fit -> forecast for the target season from the files and hashes
                     every model-owned forecast field (kit sidecar rows)       => must be bit-identical
    negative control DATA_PLAYER_V4's VolumeModel, fitted from the same files through the repository's own loader
                     (research.player_distributions.load_player_games -> v4.volume.team_game_table):
                     market_env=True under randomisation, market_env=False under partial blanking / removal
                                                                                  => must change (or refuse)

    python3 scripts/research/pure_player_v1_mutation.py --data-root <dir> --season 2025 --work <scratch> \
        --out research/pure_player_v1/mutation.json [--kit-gate <prop_projection_gate.py>]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.engines.player.pure_v1 import MODEL_NAME, VERSION                 # noqa: E402
from nfl_edge.engines.player.pure_v1 import data as PD                          # noqa: E402
from nfl_edge.engines.player.pure_v1 import features as PF                      # noqa: E402
from nfl_edge.engines.player.pure_v1 import mutation as MU                      # noqa: E402
from nfl_edge.engines.player.pure_v1 import pipeline as PP                      # noqa: E402

LINKED = ("stats_player", "snap_counts", "players", "injuries", "weekly_rosters")


def make_root(src: str, dst: str, mode: str) -> None:
    raw = os.path.join(dst, "data/raw/nflverse"); os.makedirs(os.path.join(raw, "schedules"), exist_ok=True)
    os.makedirs(os.path.join(dst, "data/silver"), exist_ok=True)
    for d in LINKED:
        s = os.path.join(src, "data/raw/nflverse", d)
        if os.path.exists(s) and not os.path.exists(os.path.join(raw, d)):
            os.symlink(s, os.path.join(raw, d))
    xw = os.path.join(dst, "data/silver/player_crosswalk.parquet")
    if not os.path.exists(xw):
        shutil.copy(os.path.join(src, "data/silver/player_crosswalk.parquet"), xw)
    g = pd.read_csv(os.path.join(src, "data/raw/nflverse/schedules/games.csv"), low_memory=False)
    m = MU.mutate_schedule(g, mode)
    m.to_csv(os.path.join(raw, "schedules/games.csv"), index=False)
    m["home_team"] = m["home_team"].replace(PD.TEAM_FIX); m["away_team"] = m["away_team"].replace(PD.TEAM_FIX)
    m.to_parquet(os.path.join(dst, "data/silver/games.parquet"), index=False)


def pure_run(root: str, season: int, out_jsonl: str) -> dict:
    pg = PD.load_player_games(root, range(2013, season + 1))
    rows, t = PF.build(pg)
    out = PP.run(rows, t, season)
    through = str(rows.loc[rows.season < season, "kickoff"].max())
    fc, _ = PP.sidecar_rows(out["player"][MODEL_NAME], VERSION, through)
    with open(out_jsonl, "w") as fh:
        fh.writelines(json.dumps(r, sort_keys=True) + "\n" for r in fc)
    tp = out["team"][MODEL_NAME][["team", "game_id", "vol_pa", "vol_ra", "vol_pts"]]
    return {"n_forecasts": len(fc), "forecast_sha256": MU.forecast_digest(fc),
            "team_env_sha256": MU.forecast_digest(json.loads(tp.round(10).to_json(orient="records")))}


def v4_volume_control(root: str, season: int) -> dict:
    """The negative control: V4's team-volume layer fitted through the repository's market-reading loader."""
    from nfl_edge.engines.player.features_v2 import add_v2_features
    from nfl_edge.engines.player.v4.volume import VolumeModel, team_game_table
    from nfl_edge.research import player_distributions as pdist
    res = {}
    try:
        f = add_v2_features(pdist.load_player_games(root, range(2013, season + 1)))
    except Exception as exc:                                    # noqa: BLE001 -- a refusal IS the observed change
        return {"refused": f"{type(exc).__name__}: {str(exc)[:200]}"}
    teams = team_game_table(f)
    test = teams[(teams.season == season) & teams.pa.notna()]
    for env in (True, False):
        try:
            vm = VolumeModel.fit(teams, season, market_env=env)
            p = vm.predict(test)
            res[f"market_env_{env}"] = {"n_team_games_trained": vm.info["n_team_games"],
                                        "pred_sha256": MU.forecast_digest(json.loads(p[["team", "game_id", "vol_pa", "vol_ra"]].round(10).to_json(orient="records"))),
                                        "mean_vol_pa": round(float(p.vol_pa.mean()), 6)}
        except Exception as exc:                                # noqa: BLE001
            res[f"market_env_{env}"] = {"refused": f"{type(exc).__name__}: {str(exc)[:200]}"}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--season", type=int, default=2025)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "pure_player_v1", "mutation.json"))
    ap.add_argument("--kit-gate", default=None)
    a = ap.parse_args()
    t0 = time.time()
    res = {"season": a.season, "modes": {}, "note": "every mode reruns the full pipeline from files; nothing is copied between modes"}
    for mode in MU.MODES:
        root = os.path.join(a.work, f"root_{mode}")
        make_root(a.data_root, root, mode)
        jp = os.path.join(a.work, f"pure_{mode}.jsonl")
        res["modes"][mode] = {"pure": pure_run(root, a.season, jp), "negative_control_v4_volume": v4_volume_control(root, a.season)}
        print(f"[{time.time() - t0:5.0f}s] {mode}: {json.dumps(res['modes'][mode])}", flush=True)
    base = res["modes"]["original"]
    res["pure_bit_identical"] = all(v["pure"] == base["pure"] for v in res["modes"].values())
    ctl = {m: v["negative_control_v4_volume"] for m, v in res["modes"].items()}
    o = ctl["original"]
    res["negative_control_changed"] = {
        "randomized_market_env_True": ctl["randomized"].get("market_env_True", {}).get("pred_sha256") != o["market_env_True"]["pred_sha256"],
        "partial_blank_market_env_False": ctl["partial_blank"].get("market_env_False") != o["market_env_False"],
        "removed": ctl["removed"] != o,
    }
    res["passed"] = bool(res["pure_bit_identical"] and all(res["negative_control_changed"].values()))
    if a.kit_gate:
        for mode in ("removed", "randomized", "partial_blank"):
            r = subprocess.run([sys.executable, "-I", a.kit_gate, "mutation", "--before", os.path.join(a.work, "pure_original.jsonl"),
                                "--after", os.path.join(a.work, f"pure_{mode}.jsonl")], capture_output=True, text=True)
            out = json.loads(r.stdout) if r.stdout.strip() else {"stderr": r.stderr[-500:]}
            res.setdefault("kit_gate_mutation", {})[mode] = {"returncode": r.returncode, **{k: out.get(k) for k in ("passed", "base_rows", "mutated_rows", "changed_model_outputs")}}
    res["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(json.dumps({"passed": res["passed"], "pure_bit_identical": res["pure_bit_identical"], "negative_control_changed": res["negative_control_changed"]}))
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
