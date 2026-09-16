#!/usr/bin/env python3
"""Rushing-enrichment ablation: does any of it improve TRUE out-of-sample rushing prediction?

Arms (each adds columns to models.CARRY_FEATURES): baseline, +ol, +front (opponent-adjusted defensive
front), +runner (yards before/after contact, stuff, broken tackles), +context (QB rush threat, indoor),
combined.

For each evaluation season Y the per-carry model is fitted on carries of seasons < Y ONLY -- including the
frozen shrinkage priors of both the base features and the enrichment -- and scored on Y:

  per carry        MAE and RMSE of expected yards, and the variance explained
  per player-game  MAE / RMSE / bias of summed expected rushing yards against the box score, on rows with
                   >= 6 carries (the population a rushing ladder is listed on)

A feature set is retained only if it improves the player-game rushing-yards error out of sample in every
evaluation season.  Writes research/simulation_engine/rushing_ablation.json.
"""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import backtest as B, data as D, features as F, models as M, rushing as RU, training as T


def build(seasons, priors, rush_priors, position_of, cfg=F.FEATURE_CONFIG):
    """Per-carry rows with the base features AND the enrichment, all from frozen priors."""
    tg = D.load("team_games", seasons).to_pandas()
    pg = D.load("player_games", seasons).to_pandas()
    tf = F.team_features(tg, cfg, priors)
    pf = F.player_features(pg, tg, cfg, priors=priors)
    pgr, tgr = RU.raw_rush_tables(seasons)
    tgrf = RU.team_rush_features(tgr, rush_priors, cfg)
    pgrf = RU.player_rush_features(pgr, rush_priors, position_of, cfg)
    tf_off = tf[["game_id", "team", "off_ypc", "off_ypa", "off_comp_rate", "margin", "home"]].rename(columns={"margin": "team_margin"})
    tf_def = tf[["game_id", "team", "def_ypc", "def_ypa", "def_comp_rate"]].rename(columns={"team": "opp"})
    pfeat = pf[~pf["phantom"]][["game_id", "player_id", "position", "rt_ypc", "prior_ypc", "rt_explosive_rate", "rt_ypc_n",
                                "rt_ypt", "prior_ypt", "rt_catch_rate", "rt_adot", "rt_ypt_n"]]
    car = D.load("carries", seasons).to_pandas()
    car = car.merge(pfeat, on=["game_id", "player_id"], how="inner").merge(tf_off, on=["game_id", "team"], how="inner") \
             .merge(tf_def, on=["game_id", "opp"], how="inner")
    return RU.attach(car, tgrf, pgrf, D.schedule().to_pandas())


def score(car_train, car_test, extra):
    feats = M.CARRY_FEATURES + [c for c in extra if c in car_test.columns]
    tr = car_train[(car_train["qb_scramble"] == 0) & (car_train["qb_kneel"] == 0)]
    te = car_test[(car_test["qb_scramble"] == 0) & (car_test["qb_kneel"] == 0)].copy()
    Xtr = M._eff_design(tr, feats); Xte = M._eff_design(te, feats)
    m = M.ridge_fit(Xtr, tr["yards"].to_numpy(float), lam=5.0)
    te["pred"] = M.ridge_predict(m, Xte)
    y = te["yards"].to_numpy(float); p = te["pred"].to_numpy(float)
    per_carry = {"n": int(len(te)), "mae": float(np.mean(np.abs(p - y))), "rmse": float(np.sqrt(np.mean((p - y) ** 2))),
                 "r2": float(1 - np.sum((p - y) ** 2) / np.sum((y - y.mean()) ** 2))}
    g = te.groupby(["game_id", "player_id"]).agg(pred=("pred", "sum"), actual=("yards", "sum"), n=("yards", "size"))
    g = g[g["n"] >= 6]
    d = g["pred"] - g["actual"]
    per_game = {"n": int(len(g)), "mae": float(np.mean(np.abs(d))), "rmse": float(np.sqrt(np.mean(d ** 2))),
                "bias": float(np.mean(d))}
    return {"features": feats, "n_features": len(feats), "per_carry": per_carry, "per_player_game": per_game,
            "coef": {c: round(float(b), 4) for c, b in zip(feats, m["beta"])}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seasons", default="2023,2024,2025")
    ap.add_argument("--history-start", type=int, default=2018, help="PFR advanced stats begin in 2018")
    a = ap.parse_args()
    seasons = [int(s) for s in a.seasons.split(",")]
    out = {"arms": list(RU.ARMS), "history_start": a.history_start, "by_season": {},
           "rejected": {"ftn_scheme": "only a file-level date_pulled, which moves when the file is rebuilt "
                                      "(weeks 1-5 of 2024 all carry 2025-09-01), so no per-row publication "
                                      "instant exists and no point-in-time claim can be made; coverage also "
                                      "starts in 2022, leaving one training season for the earliest evaluation",
                        "observed_weather": "the schedule's temp/wind are measured AT the game (hindsight) and "
                                            "are null indoors; forecast vintages only exist from 2026-09-04, so "
                                            "no historical fit can use them. 'indoor' (roof) is retained."}}
    pos_all = D.load("player_games", range(a.history_start, max(seasons) + 1)).to_pandas()
    position_of = dict(zip(pos_all["player_id"], pos_all["position"]))
    for y in seasons:
        priors = T.fit_priors_for(y, a.history_start)
        train_seasons = list(range(a.history_start, y))
        pgr_tr, tgr_tr = RU.raw_rush_tables(train_seasons)
        rush_priors = RU.fit_rush_priors(pgr_tr, tgr_tr, position_of, fit_seasons=train_seasons)
        car = build(range(a.history_start, y + 1), priors, rush_priors, position_of)
        tr = car[car["season"] < y]; te = car[car["season"] == y]
        print(f"{y}: priors {list(priors.fit_seasons)[:1]}..{list(priors.fit_seasons)[-1]}, "
              f"train carries {len(tr)}, test carries {len(te)}", flush=True)
        out["by_season"][str(y)] = {name: score(tr, te, extra) for name, extra in RU.ARMS.items()}
        for name, r in out["by_season"][str(y)].items():
            print(f"   {name:9s} per-carry MAE {r['per_carry']['mae']:.4f} r2 {r['per_carry']['r2']:+.5f} | "
                  f"player-game MAE {r['per_player_game']['mae']:.3f} RMSE {r['per_player_game']['rmse']:.3f} "
                  f"bias {r['per_player_game']['bias']:+.3f} (n {r['per_player_game']['n']})", flush=True)
    base = {y: out["by_season"][y]["baseline"]["per_player_game"]["mae"] for y in out["by_season"]}
    out["verdict"] = {}
    for name in RU.ARMS:
        deltas = {y: out["by_season"][y][name]["per_player_game"]["mae"] - base[y] for y in out["by_season"]}
        out["verdict"][name] = {"delta_player_game_mae": deltas,
                                "improves_every_season": all(v < 0 for v in deltas.values()),
                                "mean_delta": float(np.mean(list(deltas.values())))}
    os.makedirs(B.OUT, exist_ok=True)
    json.dump(out, open(os.path.join(B.OUT, "rushing_ablation.json"), "w"), indent=1)
    print(json.dumps(out["verdict"], indent=1))


if __name__ == "__main__":
    main()
