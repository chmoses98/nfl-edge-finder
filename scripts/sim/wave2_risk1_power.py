#!/usr/bin/env python3
"""Wave 2 / RISK1 minimum prospective sample (preregistration section 8), from the 2020 DEVELOPMENT season only.

Re-simulates every 2020 game exactly as the development walk-forward did (same bundle, bank and seeds), prices
synthetic contracts -- the closing spread / total and alternate lines, both team totals, and each major player's
statistics at his simulated quartiles -- with the GAME SCRIPT V2 matrix, takes the synthetic price to be the simulated
probability, and settles them on the real 2020 results under the pricer's semantics. The per-game contrast
(mean outcome - p over top-tercile P55 contracts) - (same over bottom tercile), terciles inside family x probability
quintile, gives the between-game sd; the minimum sample for a 0.02 effect at 80% power is ((1.96 + 0.84) sd / 0.02)^2.

Output: data/cache/game_script_v2/wave2/risk1_power.json (+ the observation table as parquet).
"""
from __future__ import annotations
import json, math, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from nfl_edge.sim import data as D, inputs as I, risk1 as R, script_v2 as V, simulate as S, training as T

DEV = os.path.join(ROOT, "data", "cache", "game_script_v2", "wave2", "dev", "A0")
OUT = os.path.join(ROOT, "data", "cache", "game_script_v2", "wave2", "risk1_power.json")
STATS = {"pass_yards": "passing_yards", "rush_yards": "rushing_yards", "rec_yards": "receiving_yards", "receptions": "receptions",
         "carries": "carries", "attempts": "attempts", "completions": "completions"}
FLOOR = {"pass_yards": 100, "rush_yards": 12, "rec_yards": 12, "receptions": 1.5, "carries": 3, "attempts": 15, "completions": 10}
EFFECT = 0.02


def contracts_for(res, gi):
    s, t, home, away = gi.spread_home, gi.total_line, gi.home.team, gi.away.team
    fav = home if s >= 0 else away
    c = [{"ticker": f"W-{home}", "family": "GAME_WINNER", "team": home}, {"ticker": f"W-{away}", "family": "GAME_WINNER", "team": away}]
    for k in (abs(s) - 3, abs(s), abs(s) + 3):
        c.append({"ticker": f"S-{fav}-{k:g}", "family": "SPREAD", "team": fav, "floor_strike": k})
    for k in (t - 7, t - 3, t, t + 3, t + 7):
        c.append({"ticker": f"T-{k:g}", "family": "TOTAL", "threshold": k})
    for team, imp in ((home, (t + s) / 2), (away, (t - s) / 2)):
        for k in (imp - 3, imp, imp + 3):
            c.append({"ticker": f"TT-{team}-{k:g}", "family": "TEAM_TOTAL", "team": team, "threshold": k})
    for pid, P in res.player.items():
        if pid.startswith("OTHER"):
            continue
        for st, name in STATS.items():
            if st in P and float(np.mean(P[st])) >= FLOOR[st]:
                for q in (25, 50, 75):
                    k = float(np.percentile(P[st], q))
                    c.append({"ticker": f"P-{pid}-{st}-{q}", "family": "PLAYER_STAT", "stat": name, "player_id": pid,
                              "operator": ">=", "threshold": max(k, 0.5), "team": P["team"]})
    return c


def main():
    bundle = json.load(open(os.path.join(DEV, "bundle_2020.json")))
    frames = T.assemble(range(2016, 2021), verbose=lambda *x: None, priors=T.fit_priors_for(2020))
    sched = D.schedule().to_pandas()
    g = sched[(sched["season"] == 2020) & sched["home_score"].notna() & sched["spread_line"].notna() & sched["total_line"].notna()
              & sched["game_type"].isin(["REG", "WC", "DIV", "CON", "SB"])].sort_values(["week", "game_id"])
    pg = D.load("player_games", [2020]).to_pandas()
    bank = I.historical_bank(2020)
    obs = []
    for i, r in enumerate(g.itertuples()):
        gi = I.historical_game_input(frames, r.game_id, spread_home=r.spread_line, total_line=r.total_line)
        res = S.simulate(gi, bundle, n=10000, bank=bank, seed=11 + i)
        cs = contracts_for(res, gi)
        doc = V.game_document(res, gi, S.coherence_report(res), cs, {})
        stats = {p.player_id: {"team": p.team, **{st: float(getattr(p, st)) for st in STATS}} for p in pg[pg["game_id"] == r.game_id].itertuples()}
        game = {"game_id": r.game_id, "home_team": r.home_team, "away_team": r.away_team, "home_score": float(r.home_score), "away_score": float(r.away_score)}
        bycontract = {c["ticker"]: c for c in cs}
        for c in doc["contracts"]:
            if c.get("p_cash") is None:
                continue
            y = R.realized_cash(bycontract[c["ticker"]], game, stats)
            if y is None:
                continue
            obs.append({"game_id": r.game_id, "ticker": c["ticker"], "family": c["family"], "p_model": c["p_cash"], "mid": c["p_cash"],
                        "edge": 0.0, "y": y, **R.derived(doc, c)})
    d = pd.DataFrame(obs)
    d.to_parquet(OUT.replace(".json", ".parquet"))
    d = d[(d["p_model"] > 0.03) & (d["p_model"] < 0.97)].copy()
    d["pq"] = pd.qcut(d["p_model"], 5, labels=False, duplicates="drop")
    d["terc"] = d.groupby(["family", "pq"])["p55"].transform(lambda x: pd.qcut(x.rank(method="first"), 3, labels=False))
    d["resid"] = d["y"] - d["p_model"]
    per = d[d["terc"].isin([0, 2])].groupby(["game_id", "terc"])["resid"].mean().unstack()
    per = per.dropna()
    contrast = (per[2] - per[0]).to_numpy()
    sd = float(contrast.std(ddof=1))
    n = int(math.ceil(((1.96 + 0.84) * sd / EFFECT) ** 2))
    res = {"evidence": "DEVELOPMENT (2020 only; synthetic prices = simulated probabilities)", "n_contracts": int(len(d)),
           "n_games": int(len(per)), "per_game_contrast_mean": float(contrast.mean()), "per_game_contrast_sd": sd,
           "minimal_effect": EFFECT, "n_games_required": n, "n_weeks_required_at_16": math.ceil(n / 16),
           "underpowered_at_one_season": n > 2 * 285, "by_family_contracts": d["family"].value_counts().to_dict(),
           "note": "the 2020 contrast itself is not evidence; only its spread across games sets the sample size"}
    json.dump(res, open(OUT, "w"), indent=1, default=float)
    print(json.dumps(res, indent=0, default=float))


if __name__ == "__main__":
    main()
