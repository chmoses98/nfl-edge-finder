#!/usr/bin/env python3
"""Wave 2 / S1 development selection on seasons <= 2020 ONLY (preregistration section 2).

Fit on 2018-2019 team-games (expected shares cross-fitted by season: 2018's from a share ridge fitted on 2019 and vice
versa), score on 2020 with the share ridge fitted on 2018-2019 (exactly what the 2020 walk-forward simulator uses).
Compares the incumbent moment concentration, S1-0 and S1-1 by mean per-team-game Dirichlet-multinomial log
likelihood with a game-clustered bootstrap, applies the preregistered selection rule, and writes the selected
artifacts for the simulator. Output: data/cache/game_script_v2/wave2/s1_dev.json (folded into S1_SHARE_DISPERSION.json).
"""
from __future__ import annotations
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from nfl_edge.sim import models as M, share_dispersion as SD, training as T

OUT = os.path.join(ROOT, "data", "cache", "game_script_v2", "wave2", "s1_dev.json")
B, SEED = 2000, 20261005


def share_model(e, kind):
    col = "y_share_carry" if kind == "carry" else "y_share_target"
    return M.fit_share_model(e[e[col].notna()].rename(columns={col: "y_share"}), kind)


def other_share(frames, seasons):
    o = frames["outside"]; o = o[o["game_id"].str[:4].astype(int).isin(seasons)]
    return {"carry": float(1 - o["elig_carries"].sum() / max(1, o["team_designed_rush"].sum())),
            "target": float(1 - o["elig_targets"].sum() / max(1, o["team_targets"].sum()))}


def cluster_boot(diff, games):
    df = pd.DataFrame({"g": games, "d": diff}).groupby("g")["d"].agg(["sum", "size"])
    s, n = df["sum"].to_numpy(), df["size"].to_numpy()
    idx = np.random.default_rng(SEED).integers(0, len(s), (B, len(s)))
    b = s[idx].sum(1) / n[idx].sum(1)
    return {"mean": float(s.sum() / n.sum()), "lo": float(np.quantile(b, .025)), "hi": float(np.quantile(b, .975)), "n_team_games": int(n.sum())}


def main():
    frames = T.assemble(range(2016, 2021), verbose=lambda *x: None, priors=T.fit_priors_for(2020))
    e = frames["eligible"]
    res = {"evidence": "DEVELOPMENT (<= 2020 only)", "fit_seasons": [2018, 2019], "score_season": 2020, "families": {}}
    oth = other_share(frames, [2018, 2019])
    for kind in ("carry", "target"):
        # cross-fitted training units
        cnt, shr, F = [], [], []
        for s, other_s in ((2018, 2019), (2019, 2018)):
            sm = share_model(e[e["season"] == other_s], kind)
            c, p, f, _ = SD.team_game_units(e[e["season"] == s], sm, oth[kind], kind)
            cnt += c; shr += p; F.append(f)
        F = np.vstack(F)
        s10 = SD.fit(cnt, shr, None); s11 = SD.fit(cnt, shr, F)
        # 2020 scoring with the 2018-2019 share ridge (the simulator's own expected shares for 2020)
        sm_tr = share_model(e[e["season"].isin([2018, 2019])], kind)
        c20, p20, F20, keys = SD.team_game_units(e[e["season"] == 2020], sm_tr, oth[kind], kind)
        games = [k[0] for k in keys]
        a_inc = np.full(len(c20), sm_tr["alpha"])
        a_s10 = np.full(len(c20), SD.alpha_of(s10, None))
        feats20 = [dict(zip(SD.FEATURES, row)) for row in F20]
        a_s11 = np.array([SD.alpha_of(s11, f) for f in feats20])
        ll = {"incumbent": SD.dm_loglik(c20, p20, a_inc), "S1-0": SD.dm_loglik(c20, p20, a_s10), "S1-1": SD.dm_loglik(c20, p20, a_s11)}
        fam = {"incumbent_alpha_moment": float(sm_tr["alpha"]), "S1-0": s10, "S1-1": s11,
               "alpha_S1_1_2020_quantiles": np.quantile(a_s11, [0.05, 0.25, 0.5, 0.75, 0.95]).tolist(),
               "mean_loglik_2020": {k: float(v.mean()) for k, v in ll.items()},
               "S1_0_minus_incumbent": cluster_boot(ll["S1-0"] - ll["incumbent"], games),
               "S1_1_minus_S1_0": cluster_boot(ll["S1-1"] - ll["S1-0"], games),
               "S1_1_minus_incumbent": cluster_boot(ll["S1-1"] - ll["incumbent"], games),
               "coefficients": dict(zip(SD.FEATURES, s11["beta"]))}
        # preregistered rule
        chosen = "S1-1" if fam["S1_1_minus_S1_0"]["lo"] > 0 else "S1-0"
        beats = fam[f"{chosen.replace('-', '_')}_minus_incumbent"]["lo"] > 0 if chosen == "S1-1" else fam["S1_0_minus_incumbent"]["lo"] > 0
        fam["selected"] = chosen if beats else "NONE"
        fam["status"] = "SELECTED" if beats else "REJECTED_AT_DEVELOPMENT"
        res["families"][kind] = fam
        print(kind, fam["mean_loglik_2020"], fam["selected"], {k: round(v, 3) for k, v in fam["coefficients"].items()}, flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(res, open(OUT, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
