#!/usr/bin/env python3
"""Wave 2 / M1: development selection (2018-2020, each fitted on 2016..Y-1), emergent key numbers (<= 2020), the
incumbent bank's centring and score-coherence audit, the CONTAMINATED 2021-2025 diagnostic, and the preregistered
minimum prospective sample. Writes research/game_script_v2/wave2/M1_KEY_NUMBERS.json.

Usage: python scripts/sim/wave2_m1.py
"""
from __future__ import annotations
import json, math, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from nfl_edge.sim import key_numbers as K, script_v2 as V

OUT = os.path.join(ROOT, "research", "game_script_v2", "wave2", "M1_KEY_NUMBERS.json")
B, SEED = 2000, 20261005
MODELS = ("M0", "M1-K", "M1-S")


def boot(x):
    x = np.asarray(x, float)
    i = np.random.default_rng(SEED).integers(0, len(x), (B, len(x)))
    b = x[i].mean(axis=1)
    return {"mean": float(x.mean()), "lo": float(np.quantile(b, 0.025)), "hi": float(np.quantile(b, 0.975)), "n": int(len(x))}


def block(d: pd.DataFrame) -> dict:
    out = {"n_games": int(len(d)), "models": {}, "vs_M0": {}}
    Y = np.eye(9)[d["cell"].to_numpy(int)]
    for m in MODELS:
        P = np.vstack(d[f"{m}|cells"].to_numpy())
        out["models"][m] = {"log_score": float(d[f"{m}|log_score"].mean()), "ladder_brier": float(d[f"{m}|ladder_brier"].mean()),
                            "total_ladder_brier": float(d[f"{m}|total_ladder_brier"].mean()),
                            "v2_multiclass_brier": float(((P - Y) ** 2).sum(axis=1).mean()),
                            "mean_abs_centre_error": float((d[f"{m}|mean"] - d["spread"]).abs().mean()),
                            "p_exact_abs3": float(d[f"{m}|p3"].mean()) if f"{m}|p3" in d else None,
                            "coherent_all_games": bool(d[f"{m}|coherent"].all())}
        d[f"{m}|v2"] = ((P - Y) ** 2).sum(axis=1)
    for m in MODELS[1:]:
        out["vs_M0"][m] = {k: boot(d[f"{m}|{c}"] - d[f"M0|{c}"]) for k, c in
                           (("log_score", "log_score"), ("ladder_brier", "ladder_brier"), ("total_ladder_brier", "total_ladder_brier"), ("v2_multiclass_brier", "v2"))}
    out["realized_abs3_share"] = float((d["margin"].abs() == 3).mean())
    return out


def add_p3(d: pd.DataFrame, Y: int) -> pd.DataFrame:
    """Probability each model puts on |margin| = 3 (key-number mass), recomputed from the same draws' pmf."""
    hist = K.history(Y - 1)
    vals = {m: [] for m in MODELS}
    for i, r in enumerate(d.itertuples()):
        s, T = r.spread, r.total_line
        vals["M1-K"].append(sum(p for mm, p in K.m1k_pmf(hist, s, T, Y)["margin"].items() if abs(mm) == 3))
        for m, f in (("M0", K.m0_draws), ("M1-S", K.m1s_draws)):
            x = f(hist, s, T, Y, 40000, seed=11 + i)["margin"]
            vals[m].append(float(np.mean(np.abs(x) == 3)))
    for m in MODELS:
        d[f"{m}|p3"] = vals[m]
    return d


def negative_score_audit(Y: int = 2020) -> dict:
    """Share of simulated rows with a negative team score, incumbent bank vs M1-K, over the season's real centres."""
    hist = K.history(Y - 1); test = K.history(Y, start=Y, reg_only=False)
    neg = {"M0": [], "M1-K": []}
    for i, r in enumerate(test.itertuples()):
        for m, f in (("M0", K.m0_draws), ("M1-K", K.m1k_draws)):
            d = f(hist, r.spread_line, r.total_line, Y, 20000, seed=11 + i)
            neg[m].append(float(np.mean((d["home"] < 0) | (d["away"] < 0))))
    return {m: {"mean_share_rows": float(np.mean(v)), "max_share_rows": float(np.max(v)), "games_with_any": int(np.sum(np.array(v) > 0))}
            for m, v in neg.items()}


def main():
    dev = {y: add_p3(K.evaluate_season(y), y) for y in (2018, 2019, 2020)}
    diag = {y: add_p3(K.evaluate_season(y), y) for y in (2021, 2022, 2023, 2024, 2025)}
    devall = pd.concat(dev.values(), ignore_index=True)
    sel = block(devall.copy())
    best = max(("M1-K", "M1-S"), key=lambda m: sel["vs_M0"][m]["log_score"]["mean"])
    chosen = best if sel["vs_M0"][best]["log_score"]["lo"] > 0 else None
    # minimum prospective sample from the 2020 development season (preregistration section 8)
    d20 = dev[2020]
    diff = (d20[f"{best}|log_score"] - d20["M0|log_score"]).to_numpy()
    eff, sd = float(diff.mean()), float(diff.std(ddof=1))
    n_min = None if eff <= 0 else max(64, int(math.ceil(((1.96 + 0.84) * sd / eff) ** 2 / 16.0) * 16))
    res = {"m1_version": K.M1_VERSION, "evidence": {"development": [2018, 2019, 2020], "contaminated_diagnostic": [2021, 2022, 2023, 2024, 2025]},
           "fit_window": "2016..Y-1, regular season (as the incumbent bank)", "parameters": {
               "h_spread": K.H_SPREAD, "h_total": K.H_TOTAL, "halflife": K.HALFLIFE, "min_eff_n": K.MIN_EFF_N,
               "strat_half_width": K.STRAT_HALF_WIDTH, "strat_min_n": K.STRAT_MIN_N},
           "emergent_key_numbers_le_2020": K.emergent_key_numbers(2020),
           "development": {"by_season": {str(y): block(d.copy()) for y, d in dev.items()}, "pooled": sel},
           "selection": {"best_candidate": best, "selected": chosen or "NONE",
                         "rule": "best log-score candidate if its pooled 2018-2020 advantage over M0 has a 95% interval above 0",
                         "status": "PROSPECTIVE_CHALLENGER_PENDING_DIAGNOSTIC" if chosen else "REJECTED_AT_DEVELOPMENT"},
           "incumbent_audit_2020": {"negative_team_score_rows": negative_score_audit(2020),
                                    "mean_abs_centre_error_points": sel["models"]["M0"]["mean_abs_centre_error"]},
           "contaminated_diagnostic": {"by_season": {str(y): block(d.copy()) for y, d in diag.items()},
                                       "pooled": block(pd.concat(diag.values(), ignore_index=True))},
           "minimum_prospective_sample": {"source": "2020 development season, paired per-game log-score difference",
                                          "effect": eff, "sd": sd, "n_games": n_min}}
    diag_ok = chosen and res["contaminated_diagnostic"]["pooled"]["vs_M0"][chosen]["log_score"]["mean"] > 0
    res["status"] = ("PROSPECTIVE_CHALLENGER" if diag_ok else "DIAGNOSTIC_FAIL") if chosen else "REJECTED_AT_DEVELOPMENT"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(res, open(OUT, "w"), indent=1, default=float)
    print(res["status"], res["selection"], res["minimum_prospective_sample"])


if __name__ == "__main__":
    main()
