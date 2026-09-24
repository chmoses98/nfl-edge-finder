#!/usr/bin/env python3
"""Player Engine v4 UPSTREAM diagnostics: snap share, team volume, target / carry share and reconciliation, on every
2025 player-game (fitted on seasons <= 2024; closing-line environment, since these are not scored against a market).

    python3 scripts/research/player_engine_v4_upstream.py --frame /tmp/pe4/frame.pkl

Writes research/player_engine_v4/upstream.json. The "V3" column is what v3 uses for the same quantity: the EWMA snap
share, the team EWMA volume, the EWMA target / carry share.
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
from nfl_edge.engines.player.v4 import model as M                       # noqa: E402
from nfl_edge.engines.player.v4.volume import VolumeModel, team_game_table   # noqa: E402


def err(p, y):
    p, y = np.asarray(p, float), np.asarray(y, float)
    ok = np.isfinite(p) & np.isfinite(y)
    if not ok.any():
        return None
    e = p[ok] - y[ok]
    return {"n": int(ok.sum()), "mae": round(float(np.abs(e).mean()), 4), "rmse": round(float(np.sqrt((e ** 2).mean())), 4), "bias": round(float(e.mean()), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", default="/tmp/pe4/frame.pkl")
    ap.add_argument("--season", type=int, default=2025)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "player_engine_v4", "upstream.json"))
    a = ap.parse_args()
    f = pd.read_pickle(a.frame)
    T = team_game_table(f)
    out = {"season": a.season, "note": "every 2025 player-game with a snap count (fits on <= 2024); V3 = the EWMA quantity v3 uses"}
    full = M.fit_bundle(f, a.season, teams=T, verbose=lambda *x: None)
    nored = M.fit_bundle(f, a.season, {"redistribution": False}, teams=T, verbose=lambda *x: None)
    te = f[(f.season == a.season) & (f.offense_snaps.fillna(0) > 0)]
    I = full.intermediates(te, T)
    J = nored.intermediates(te, T)
    I["share_t_nored"], I["share_c_nored"] = J["share_t"].to_numpy(), J["share_c"].to_numpy()
    # ---- snap
    snap = {"all": {"V3": err(I.ewma_snap_share, I.snap_share), "V4": err(I.snap_mean, I.snap_share)}}
    for g in ("QB", "RB", "WR", "TE"):
        s = I[I.pgroup == g]
        snap[g] = {"V3": err(s.ewma_snap_share, s.snap_share), "V4": err(s.snap_mean, s.snap_share)}
    hi = I.snap_sd <= I.snap_sd.median()
    snap["v4_high_certainty(snap_sd<=median)"] = {"V3": err(I[hi].ewma_snap_share, I[hi].snap_share), "V4": err(I[hi].snap_mean, I[hi].snap_share)}
    snap["v4_low_certainty(snap_sd>median)"] = {"V3": err(I[~hi].ewma_snap_share, I[~hi].snap_share), "V4": err(I[~hi].snap_mean, I[~hi].snap_share)}
    for lab, m in (("returning", I.self_returning == 1), ("new_to_team", I.self_new == 1), ("changed_team", I.changed_team == 1),
                   ("teammate_vacated_snaps>0.2", I.vac_same_s > 0.2), ("questionable", I.own_q == 1),
                   ("stable(n_cur>=2,no flags)", (I.n_cur_season >= 2) & (I.self_returning == 0) & (I.self_new == 0) & (I.own_q == 0))):
        snap[lab] = {"V3": err(I[m].ewma_snap_share, I[m].snap_share), "V4": err(I[m].snap_mean, I[m].snap_share)}
    lo, hi_ = full.snap.predict(te)[["snap_p10", "snap_p90"]].to_numpy().T
    snap["interval80_coverage"] = round(float(((te.snap_share >= lo) & (te.snap_share <= hi_)).mean()), 4)
    out["snap"] = snap
    # ---- team volume
    tt = T[(T.season == a.season) & T.pa.notna()]
    vol = {}
    for name, ab in (("V3_team_ewma", True), ("V4", False)):
        vm = VolumeModel.fit(T, a.season, ablate=ab)
        p = vm.predict(tt)
        vol[name] = {"pass_att": err(p.vol_pa, tt.pa), "rush_att": err(p.vol_ra, tt.ra), "plays": err(p.vol_pa + p.vol_ra, tt.plays),
                     "plays_bias_pct": round(float(100 * ((p.vol_pa + p.vol_ra) / tt.plays - 1).mean()), 2)}
    vol["constant_league_mean"] = {"pass_att": err(np.full(len(tt), T[T.season < a.season].pa.mean()), tt.pa),
                                   "rush_att": err(np.full(len(tt), T[T.season < a.season].ra.mean()), tt.ra)}
    out["team_volume"] = vol
    # ---- allocation
    alloc = {}
    for kind, s, groups in (("target", "t", ("RB", "WR", "TE")), ("carry", "c", ("RB", "QB", "WR"))):
        x = I[I.pgroup.isin(groups)]
        blk = {"all": {"V3": err(x[f"ewma_{kind}_share"], x[f"{kind}_share"]), "V4": err(x[f"share_{s}"], x[f"{kind}_share"]),
                       "V4_no_redistribution": err(x[f"share_{s}_nored"], x[f"{kind}_share"])}}
        ab = x[x[f"vac_same_{s}"] > 0.05]
        blk["teammate_absence(vacated same-group share>0.05)"] = {"V3": err(ab[f"ewma_{kind}_share"], ab[f"{kind}_share"]),
                                                                   "V4": err(ab[f"share_{s}"], ab[f"{kind}_share"]),
                                                                   "V4_no_redistribution": err(ab[f"share_{s}_nored"], ab[f"{kind}_share"])}
        rt = x[x[f"ret_same_{s}"] > 0.05]
        blk["teammate_returning(>0.05)"] = {"V3": err(rt[f"ewma_{kind}_share"], rt[f"{kind}_share"]), "V4": err(rt[f"share_{s}"], rt[f"{kind}_share"]),
                                            "V4_no_redistribution": err(rt[f"share_{s}_nored"], rt[f"{kind}_share"])}
        alloc[kind] = blk
    for raw, groups in (("targets", ("RB", "WR", "TE")), ("carries", ("RB",)), ("receptions", ("RB", "WR", "TE"))):
        x = I[I.pgroup.isin(groups)]
        alloc[f"{raw}_count"] = {"V3_ewma": err(x[f"ewma_{raw}"], x[raw]), "V4": err(x[f"mu_{raw}"], x[raw])}
    # reconciliation: predicted share sum per team-game over the players who actually played (the widest set history has)
    g = I.groupby(["team", "game_id"])
    alloc["reconciliation"] = {"target_share_sum_mean": round(float(g.share_t.sum().mean()), 4), "target_share_sum_p95": round(float(g.share_t.sum().quantile(0.95)), 4),
                               "carry_share_sum_mean": round(float(g.share_c.sum().mean()), 4),
                               "pre_cap_target_sum_over_1_pct": round(float(100 * (g.recon_t_sum.first() > 1).mean()), 2),
                               "pre_cap_carry_sum_over_1_pct": round(float(100 * (g.recon_c_sum.first() > 1).mean()), 2),
                               "realised_target_share_sum_mean": round(float(g.target_share.sum().mean()), 4)}
    out["allocation"] = alloc
    out["bundle"] = full.summary()
    json.dump(out, open(a.out, "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("snap", "team_volume", "allocation")}, indent=1)[:6000])


if __name__ == "__main__":
    main()
