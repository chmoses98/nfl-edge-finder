#!/usr/bin/env python3
"""Arm forecasts for the PURE gap study, cached for the decomposition and the PURE_PLAYER_V1_2 study.

Re-runs, unchanged, the arms of the PURE_PLAYER_V1 held-out comparison (scripts/research/pure_player_v1_study.py) on
the same population and adds one ablation of DATA_PLAYER_V4 that the repository's V4 config already exposes:

    PURE_PLAYER_V1        frozen (nfl_edge/engines/player/pure_v1, pure-player-v1.0.0)
    PURE_EWM_BASELINE     frozen
    V4_MARKET_CLOSE       DATA_PLAYER_V4 default config (market_env=True, consensus closing spread/total) -- MARKET-INFORMED
    V4_MEF_AS_IS          V4 market_env=False (still: training sample gated on a line existing, injury/roster statuses)
    V4_MEF_NO_AVAIL       V4 market_env=False AND redistribution=False: every own-status / teammate-availability
                          feature (injury report, weekly roster, vacated / returning roles) dropped from snap and shares

Per (player, game) it also keeps each arm's component intermediates (team pass / rush volume, snap share) so the
decomposition can factor every mean. Output: <cache>/pure_gap_arms_<seasons>.pkl (not committed; regenerable).

    python3 scripts/research/pure_gap_arms.py --data-root <root> --seasons 2024,2025 --cache <dir>
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats as sstats

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "research"))
import pure_player_v1_study as S1                                                  # noqa: E402  (frozen study helpers)
from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME              # noqa: E402
from nfl_edge.engines.player.pure_v1 import model as PM                            # noqa: E402
from nfl_edge.engines.player.pure_v1 import pipeline as PP                         # noqa: E402

V4_MKT, V4_MEF, V4_NOAV = "V4_MARKET_CLOSE", "V4_MEF_AS_IS", "V4_MEF_NO_AVAIL"
V4_CONFIGS = {V4_MKT: {}, V4_MEF: {"market_env": False}, V4_NOAV: {"market_env": False, "redistribution": False}}
INTER_COLS = ["vol_pa", "vol_ra", "snap_mean"]


def v4_arm(frame, teams, season, keys, config):
    """V4 bundle fitted strictly before `season`; long forecasts (as the frozen study builds them) + intermediates."""
    from nfl_edge.engines.player.v4 import model as M
    b = M.fit_bundle(frame, season, config, teams=teams, verbose=lambda *x: None)
    rows = frame[frame.season == season].merge(keys[["player_id", "game_id"]].drop_duplicates(), on=["player_id", "game_id"], how="inner")
    I = b.intermediates(rows, teams)
    recs = []
    for r in I.to_dict("records"):
        base = {"game_id": r["game_id"], "player_id": r["player_id"]}
        if np.isfinite(r.get("snap_mean", np.nan)):
            med, p10, p90, surv = S1._beta_summary(np.array([r["snap_mean"]]), np.array([r["snap_sd"] if np.isfinite(r.get("snap_sd", np.nan)) else 0.2]),
                                                   PM.LADDERS["snap_share"])
            recs.append({**base, "statistic": "snap_share", "mean": r["snap_mean"], "median": med[0], "p10": p10[0], "p90": p90[0],
                         "thresholds": list(zip(PM.LADDERS["snap_share"], surv[0]))})
        if r["pgroup"] in M.TARGET_GROUPS and np.isfinite(r.get("mu_targets", np.nan)):
            rr = b._r("targets", r["pgroup"], r["cv2_targets"]); mu = r["mu_targets"]; p = rr / (rr + mu)
            recs.append({**base, "statistic": "targets", "mean": mu, "median": sstats.nbinom.ppf(0.5, rr, p), "p10": sstats.nbinom.ppf(0.1, rr, p),
                         "p90": sstats.nbinom.ppf(0.9, rr, p), "thresholds": [(k, sstats.nbinom.sf(k - 1, rr, p)) for k in PM.LADDERS["targets"]]})
        D = b.distributions(r, stats=list(set(S1.V4_STAT.values())))
        for stat, vs in S1.V4_STAT.items():
            dist = D.get(vs)
            if dist is None:
                continue
            recs.append({**base, "statistic": stat, "mean": dist.mean(), "median": dist.quantile(0.5), "p10": dist.quantile(0.1),
                         "p90": dist.quantile(0.9), "thresholds": [(k, dist.survival(k)) for k in PM.LADDERS[stat]]})
    L = pd.DataFrame(recs)
    inter = I[["player_id", "game_id"] + INTER_COLS].drop_duplicates(["player_id", "game_id"])
    tt = teams[(teams.season == season) & teams.pa.notna()]
    v = b.volume.predict(tt)
    T = tt[["team", "game_id"]].assign(vol_pa=v.vol_pa.to_numpy(), vol_ra=v.vol_ra.to_numpy())
    return L, inter, T, {"config": b.config, "bundle_sha": b.artifact_sha}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--seasons", default="2024,2025")
    ap.add_argument("--last-season", type=int, default=2026)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--no-v4", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    log = lambda *x: print(f"[{time.time() - t0:6.0f}s]", *x, flush=True)   # noqa: E731
    seasons = [int(x) for x in a.seasons.split(",")]
    os.makedirs(a.cache, exist_ok=True)
    rows, t = S1.pure_frames(a.data_root, a.cache, a.last_season)
    log("pure frames", rows.shape)
    frame = teams4 = None
    if not a.no_v4:
        from nfl_edge.engines.player.v4.volume import team_game_table
        frame = S1.v4_frame(a.data_root, a.cache, a.last_season)
        teams4 = team_game_table(frame)
        log("v4 frame", frame.shape)
    out = {"long": {}, "inter": {}, "team": {}, "info": {}, "pure_inter": [], "team_actual": []}
    for S in seasons:
        o = PP.run(rows, t, S)
        for k, v in o["player"].items():
            out["long"].setdefault(k, []).append(v.assign(season=S))
        for k, v in o["team"].items():
            out["team"].setdefault(k, []).append(v.assign(season=S))
        d = o["intermediates"]
        keep = ["player_id", "game_id", "team", "opponent_team", "season", "week", "pgroup", "kickoff", "vol_pa", "vol_ra", "snap_mean",
                "snap_share", "e_snap_share", "e_target_share", "e_carry_share", "gap_gt0", "games_missed", "changed_team", "n_cur_season",
                "o_cmp_allowed", "o_ypt_allowed", "o_ypc_allowed", "o_ypa_allowed", "o_rate_allowed", "exp_margin", "f_ypa", "pa", "ra"]
        out["pure_inter"].append(d[[c for c in keep if c in d.columns]].assign(season=S))
        out["info"][S] = {"pure": o["model"].info}
        log(S, "pure done")
        if frame is not None:
            keys = o["player"][MODEL_NAME][["player_id", "game_id"]]
            act = o["player"][BASELINE_NAME][["game_id", "player_id", "statistic", "season", "week", "pgroup", "actual", "played", "kickoff"]]
            for name, cfg in V4_CONFIGS.items():
                L4, I4, T4, i4 = v4_arm(frame, teams4, S, keys, cfg)
                out["long"].setdefault(name, []).append(L4.merge(act, on=["game_id", "player_id", "statistic"], how="inner").assign(season=S))
                out["inter"].setdefault(name, []).append(I4.assign(season=S))
                out["team"].setdefault(name, []).append(T4.assign(season=S))
                out["info"][S][name] = i4
                log(S, name, len(L4))
    res = {"long": {k: pd.concat(v, ignore_index=True) for k, v in out["long"].items()},
           "inter": {k: pd.concat(v, ignore_index=True) for k, v in out["inter"].items()},
           "team": {k: pd.concat(v, ignore_index=True) for k, v in out["team"].items()},
           "pure_inter": pd.concat(out["pure_inter"], ignore_index=True), "info": out["info"], "rows": rows, "teams": t}
    p = os.path.join(a.cache, f"pure_gap_arms_{'_'.join(map(str, seasons))}.pkl")
    pd.to_pickle(res, p)
    log("wrote", p)


if __name__ == "__main__":
    main()
