#!/usr/bin/env python3
"""Real-data check that the prospective code path reproduces the preregistered backtest path.

For one already-played week it (a) runs the frozen walk-forward pipeline (pipeline.run) and (b) re-forecasts the
same games through nfl_edge.shadow_pure.prospective as if it were 2 h before the week's first kickoff, using only
games observable then. Forecast means must agree on every matched row; the population difference (players the
prospective candidate rule did / did not include) is reported, not hidden.

    python3 scripts/shadow_pure/equivalence_check.py --season 2026 --week 4 --out research/pure_shadow_nfl/equivalence_2026_wk04.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME  # noqa: E402
from nfl_edge.engines.player.pure_v1 import data as D  # noqa: E402
from nfl_edge.engines.player.pure_v1 import features as F  # noqa: E402
from nfl_edge.engines.player.pure_v1 import pipeline as PP  # noqa: E402
from nfl_edge.shadow_pure import DATA_FIRST_SEASON, frozen, inputs, prospective  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    seasons = range(DATA_FIRST_SEASON, a.season + 1)
    pg = D.load_player_games(a.root, seasons)
    sched = D.sports_schedule(D.read_schedule(a.root))
    rows, t = F.build(pg)
    bt = PP.run(rows, t, a.season, weeks=[a.week])
    wk = sched[(sched.season == a.season) & (sched.week == a.week)]
    as_of = wk.kickoff.min() - pd.Timedelta(hours=2)
    games = prospective.upcoming_games(sched, as_of.to_pydatetime(), game_ids=wk.game_id)
    syn = prospective.candidates(pg, games, as_of)
    r2, t2 = prospective.build(pg, syn, as_of)
    m, b = prospective.fit(r2, t2, a.season)
    fc = prospective.forecast(r2, t2, m, b, as_of)
    prov = inputs.input_provenance(a.root, seasons, as_of=pd.Timestamp.now(tz="UTC").to_pydatetime())
    out = {"season": a.season, "week": a.week, "prospective_as_of": as_of.isoformat(), "games": int(len(games)),
           "games_in_week": int(len(wk)), "candidate_player_games": int(len(syn)), "model_code_sha256": frozen.code_sha256(),
           "inputs": [{k: r.get(k) for k in ("path", "fetched_at", "sha256")} for r in prov if r.get("status") == "PRESENT"],
           "arms": {}}
    for arm in (MODEL_NAME, BASELINE_NAME):
        k = ["game_id", "player_id", "statistic"]
        A, P = bt["player"][arm], fc["arms"][arm]
        j = A.merge(P, on=k, suffixes=("_b", "_p"))
        d = (j["mean_b"] - j["mean_p"]).abs().to_numpy(float)
        miss = A.merge(P[k], on=k, how="left", indicator=True)
        miss = miss[miss["_merge"] == "left_only"]
        extra = P.merge(A[k], on=k, how="left", indicator=True)
        extra = extra[extra["_merge"] == "left_only"]
        out["arms"][arm] = {"backtest_rows_played": int(len(A)), "prospective_rows": int(len(P)), "matched": int(len(j)),
                            "max_abs_mean_diff": float(d.max()) if len(d) else None,
                            "n_mean_diff_gt_1e-9": int((d > 1e-9).sum()),
                            "max_abs_p10_diff": float((j["p10_b"] - j["p10_p"]).abs().max()),
                            "max_abs_p90_diff": float((j["p90_b"] - j["p90_p"]).abs().max()),
                            "played_but_not_forecast_prospectively": int(len(miss)),
                            "played_but_not_forecast_by_statistic": miss["statistic"].value_counts().sort_index().to_dict(),
                            "forecast_prospectively_but_not_in_played_population": int(len(extra)),
                            # every differing row, with the position label each path used: the backtest reads the
                            # target game's own box-score position, the prospective path the last one known pregame
                            "differing_rows": [{"game_id": r.game_id, "player_id": r.player_id, "statistic": r.statistic,
                                                "mean_backtest": round(float(r.mean_b), 4), "mean_prospective": round(float(r.mean_p), 4),
                                                "position_backtest": r.position_b, "position_prospective": r.position_p}
                                               for r in j[np.abs(j["mean_b"] - j["mean_p"]) > 1e-9].itertuples()]}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out["arms"], indent=1))
    # a difference is acceptable only when the two paths assigned the player different position labels
    ok = all(d["position_backtest"] != d["position_prospective"] for v in out["arms"].values() for d in v["differing_rows"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
