#!/usr/bin/env python3
"""Does the EXISTENCE of a Kalshi ladder tell us a player has a role the depth chart missed?

Week 1 2026 under-projected real contributors whose depth-chart rank was 3+ while Kalshi was actively
listing ladders for them.  The listing is a statement by the market that the player matters, and it is
legitimate to read it as an ELIGIBILITY / ROLE-UNCERTAINTY signal.  It is NOT legitimate to read the
player's QUOTE into the football-only projection -- the quote enters only through the separate
reconciliation layer -- so nothing here touches a price, a midpoint, a bid or an ask.  The only input is
the boolean "a ladder for this player exists in the market universe".

Procedure (the same fit / confirm discipline as the reconciliation weights):
  * the carry-share and target-share models are fitted on seasons <= 2024 with frozen priors;
  * shares are predicted for every point-in-time eligible player-game of 2025 and renormalised within the
    team-game exactly as the simulator does;
  * a FLOOR per (position, depth-chart band) is fitted on 2025 weeks 1-9 as a quantile of the realised
    share of LISTED players in that cell, and applied as ``p = max(p, floor)`` before renormalisation;
  * the floor is then confirmed on weeks 10-22, and on the players it is meant to help (listed, rank 3+)
    as well as on everyone, because a floor that fixes the tail by breaking the starters is not a fix.

Writes research/simulation_engine/role_signal_2025.json and role_floor.json.
"""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import backtest as B, data as D, features as F, kalshi_history as K, models as M, training as T

QUANTILES = (0.10, 0.20, 0.25, 0.33, 0.40, 0.50)


def band(dc_rank) -> str:
    r = pd.to_numeric(dc_rank, errors="coerce")
    return np.where(r.isna(), "unlisted", np.where(r <= 2, "dc1-2", "dc3+"))


def predicted_shares(frames: dict, season: int, kind: str, bundle_share: dict) -> pd.DataFrame:
    e = frames["eligible"]; e = e[e["season"] == season].copy()
    X = M.share_design(e, kind, bundle_share["priors"])
    e["p_raw"] = np.clip(M.ridge_predict(bundle_share["ridge"], X), 0.0, None)
    return e


def renormalise(e: pd.DataFrame, col: str, other_share: float) -> pd.Series:
    tot = e.groupby(["game_id", "team"])[col].transform("sum").clip(lower=1e-9)
    return e[col] / tot * (1.0 - other_share)


def evaluate(e: pd.DataFrame, kind: str, other_share: float, floor: dict | None) -> dict:
    y = "y_share_carry" if kind == "carry" else "y_share_target"
    vol = "team_designed_rush" if kind == "carry" else "team_targets"
    d = e[e[y].notna()].copy()
    d["p_floored"] = d["p_raw"]
    if floor:
        key = d["position"].astype(str) + "|" + band(d["dc_rank"])
        f = key.map({k: v for k, v in floor.items()}).astype(float).fillna(0.0)
        d["p_floored"] = np.where(d["market_listed"] > 0, np.maximum(d["p_raw"], f), d["p_raw"])
    d["p"] = renormalise(d, "p_floored", other_share)
    err = d["p"] - d[y]
    cnt_err = (d["p"] - d[y]) * d[vol]
    listed3 = (d["market_listed"] > 0) & (band(d["dc_rank"]) != "dc1-2")
    starters = band(d["dc_rank"]) == "dc1-2"
    # the actual Week-1 failure population: the model has no usable history, so it falls back to the
    # depth-rank cell prior, and the depth chart is exactly what was wrong
    thin = (d["n_prior"].fillna(0) <= 2) | (d["gap_weeks"].fillna(99) >= 4)
    listed_thin = (d["market_listed"] > 0) & thin

    def blk(mask):
        if mask.sum() == 0:
            return None
        return {"n": int(mask.sum()), "share_mae": float(np.mean(np.abs(err[mask]))),
                "count_mae": float(np.mean(np.abs(cnt_err[mask]))), "count_bias": float(np.mean(cnt_err[mask]))}
    return {"all": blk(pd.Series(True, index=d.index)), "listed_rank3_plus": blk(listed3),
            "starters": blk(starters), "listed_thin_history": blk(listed_thin)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default="/home/user/_market_data_wt")
    ap.add_argument("--season", type=int, default=2025)
    ap.add_argument("--fit-weeks", default="1-9")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.fit_weeks.split("-"))
    priors = T.fit_priors_for(a.season)
    frames = T.assemble(range(2016, a.season + 1), verbose=lambda *x: None, priors=priors)
    bundle = T.fit_bundle(a.season, frames, verbose=lambda *x: None)
    rungs = K.load_rungs(a.market_data, a.season)
    listed = rungs.groupby(["game_id", "player_id"]).size().rename("n_rungs").reset_index()
    listed["market_listed"] = 1.0
    out = {"season": a.season, "fit_weeks": [lo, hi], "n_listed_pairs": int(len(listed)),
           "rule": "the boolean existence of a Kalshi ladder only; no price, midpoint, bid or ask is read",
           "kinds": {}}
    floor_final = {}
    for kind in ("carry", "target"):
        e = predicted_shares(frames, a.season, kind, bundle[f"{kind}_share"])
        e = e.merge(listed, on=["game_id", "player_id"], how="left")
        e["market_listed"] = e["market_listed"].fillna(0.0)
        other = bundle["other_share"][kind]
        y = "y_share_carry" if kind == "carry" else "y_share_target"
        fit = e[(e["week"] >= lo) & (e["week"] <= hi)]
        conf = e[e["week"] > hi]
        cells = (fit["position"].astype(str) + "|" + band(fit["dc_rank"]))
        base_conf = evaluate(conf, kind, other, None)
        best = None
        for q in QUANTILES:
            floor = {}
            for cell, g in fit[fit["market_listed"] > 0].groupby(cells[fit["market_listed"] > 0]):
                gg = g[g[y].notna()]
                if len(gg) >= 40:
                    floor[cell] = float(np.quantile(gg[y], q))
            r = evaluate(fit, kind, other, floor)
            cand = {"quantile": q, "floor": floor, "fit": r}
            if best is None or r["all"]["share_mae"] < best["fit"]["all"]["share_mae"]:
                best = cand
        conf_r = evaluate(conf, kind, other, best["floor"])
        base_fit = evaluate(fit, kind, other, None)
        helped = (conf_r["listed_rank3_plus"]["count_mae"] < base_conf["listed_rank3_plus"]["count_mae"])
        harmed = (conf_r["starters"]["count_mae"] > base_conf["starters"]["count_mae"] * 1.02)
        deploy = bool(helped and not harmed and conf_r["all"]["share_mae"] <= base_conf["all"]["share_mae"])
        out["kinds"][kind] = {"chosen_quantile": best["quantile"], "floor": best["floor"],
                              "fit_baseline": base_fit, "fit_floored": best["fit"],
                              "confirm_baseline": base_conf, "confirm_floored": conf_r,
                              "helps_target_population": helped, "harms_starters": harmed, "deployed": deploy}
        if deploy:
            floor_final[kind] = {"quantile": best["quantile"], "floor": best["floor"]}
        lt0 = base_conf.get("listed_thin_history") or {}; lt1 = conf_r.get("listed_thin_history") or {}
        out["kinds"][kind]["confirm_listed_thin_history"] = {"baseline": lt0, "floored": lt1}
        print(f"{kind}: listed+thin-history (n {lt0.get('n')}) count MAE {lt0.get('count_mae', float('nan')):.3f} -> "
              f"{lt1.get('count_mae', float('nan')):.3f}, bias {lt0.get('count_bias', float('nan')):+.3f} -> "
              f"{lt1.get('count_bias', float('nan')):+.3f}", flush=True)
        print(f"{kind}: q={best['quantile']} cells={len(best['floor'])} | confirm listed rank3+ count MAE "
              f"{base_conf['listed_rank3_plus']['count_mae']:.3f} -> {conf_r['listed_rank3_plus']['count_mae']:.3f} "
              f"| starters {base_conf['starters']['count_mae']:.3f} -> {conf_r['starters']['count_mae']:.3f} "
              f"| all share MAE {base_conf['all']['share_mae']:.5f} -> {conf_r['all']['share_mae']:.5f} "
              f"| DEPLOY={deploy}", flush=True)
    os.makedirs(B.OUT, exist_ok=True)
    json.dump(out, open(os.path.join(B.OUT, "role_signal_2025.json"), "w"), indent=1)
    json.dump({"version": "role-floor-1.0.0", "fitted_on": f"{a.season} weeks {lo}-{hi}, confirmed on {hi+1}+",
               "rule": out["rule"], "floors": floor_final},
              open(os.path.join(B.OUT, "role_floor.json"), "w"), indent=1)
    print("deployed floors:", json.dumps({k: v["quantile"] for k, v in floor_final.items()}))


if __name__ == "__main__":
    main()
