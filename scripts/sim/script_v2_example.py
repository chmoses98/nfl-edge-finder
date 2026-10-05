#!/usr/bin/env python3
"""ILLUSTRATIVE GAME SCRIPT V2 output for one completed historical game -- what the RUN NFL section looks like.

Simulates the game with that season's walk-forward bundle (trained on earlier seasons only) and the consensus closing
line as the centre, then builds the V2 document for contracts placed AT THE CLOSING LINES (moneyline, the favourite's
spread, the total, both team totals) and at the simulation's own medians for each team's lead passer / rusher /
receiver. These are not Kalshi listings and nothing here is a recommendation; the market column is empty because no
historical Kalshi quote is used.

Usage: python scripts/sim/script_v2_example.py --game 2025_10_KC_DEN [--n-sims 20000]
Writes research/game_script_v2/example_<game>.json and example_<game>.md.
"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np
from nfl_edge.handicap import render as RD, script_block as SB
from nfl_edge.sim import data as D, five_year as FY, inputs as I, simulate as S, script_v2 as V, training as T

STAT_NAME = {"pass_yards": "passing_yards", "rush_yards": "rushing_yards", "receptions": "receptions"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--n-sims", type=int, default=20000)
    a = ap.parse_args()
    g = D.schedule().to_pandas().set_index("game_id").loc[a.game]
    season = int(g["season"])
    bundle = json.load(open(os.path.join(FY.DEFAULT_OUT, f"bundle_{season}.json")))
    frames = T.assemble(range(2016, season + 1), verbose=lambda *x: None, priors=T.fit_priors_for(season))
    gi = I.historical_game_input(frames, a.game, spread_home=float(g["spread_line"]), total_line=float(g["total_line"]))
    res = S.simulate(gi, bundle, n=a.n_sims, bank=I.historical_bank(season), seed=11)
    coh = S.coherence_report(res)
    home, away = gi.home.team, gi.away.team
    fav = home if gi.spread_home > 0 else away
    s, t = abs(gi.spread_home), gi.total_line
    contracts = [{"ticker": f"WIN-{home}", "family": "GAME_WINNER", "team": home},
                 {"ticker": f"WIN-{away}", "family": "GAME_WINNER", "team": away},
                 {"ticker": f"SPREAD-{fav}-{s:g}", "family": "SPREAD", "team": fav, "floor_strike": s},
                 {"ticker": f"TOTAL-{t:g}", "family": "TOTAL", "threshold": t},
                 {"ticker": f"TT-{home}-{(t + gi.spread_home) / 2:.1f}", "family": "TEAM_TOTAL", "team": home, "threshold": (t + gi.spread_home) / 2},
                 {"ticker": f"TT-{away}-{(t - gi.spread_home) / 2:.1f}", "family": "TEAM_TOTAL", "team": away, "threshold": (t - gi.spread_home) / 2}]
    import polars as pl
    pn = pl.read_parquet(os.path.join(D.RAW, "players", "players.parquet"), columns=["gsis_id", "display_name"])
    names = dict(zip(pn["gsis_id"].to_list(), pn["display_name"].to_list()))
    for ti in (gi.home, gi.away):
        for st in ("pass_yards", "rush_yards", "receptions"):
            cand = [(float(np.mean(v[st])), pid) for pid, v in res.player.items() if v["team"] == ti.team and not pid.startswith("OTHER") and st in v]
            if not cand:
                continue
            mu, pid = max(cand)
            med = float(np.median(res.player[pid][st]))
            nm = names.get(pid, pid)
            contracts.append({"ticker": f"{ti.team}-{st}-{pid}-{med:g}+", "family": "PLAYER_STAT", "stat": STAT_NAME[st], "player_id": pid,
                              "player_name": nm, "operator": ">=", "threshold": med, "team": ti.team})
    doc = V.game_document(res, gi, coh, contracts, {})
    # every contract is a candidate in the illustration (the packet details its ranked disagreements and game lines)
    game = {"game_id": a.game, "markets": [{"ticker": c["ticker"]} for c in contracts],
            "simulation": {"largest_reconciled_disagreements": [{"ticker": c["ticker"]} for c in contracts]}}
    view_all = SB.game_script_v2_view(game, doc, source="scripts/sim/script_v2_example.py (illustrative)")
    out = {"illustrative": True, "game_id": a.game, "season": season, "centre": {"spread_home": gi.spread_home, "total": gi.total_line, "source": "consensus closing line"},
           "bundle_train_seasons": bundle["train_seasons"], "realized": {"home_margin": float(g["result"]), "total": float(g["total"]),
                                                                           "cell": V.classify(float(g["result"]), float(g["total"]), gi.spread_home, gi.total_line)},
           "document": doc, "view": view_all}
    base = os.path.join(ROOT, "research", "game_script_v2", f"example_{a.game}")
    json.dump(out, open(base + ".json", "w"), indent=1, default=float)
    md = [f"# ILLUSTRATIVE: GAME SCRIPT V2 for {away} @ {home} (`{a.game}`)", "",
          "Historical game, simulated with the walk-forward bundle trained on "
          f"{min(bundle['train_seasons'])}-{max(bundle['train_seasons'])} and the consensus closing line as the centre. Contracts are placed at the "
          "closing lines and at the simulation's own player medians -- they are not Kalshi listings, carry no market price and are "
          "not recommendations. Generated by `scripts/sim/script_v2_example.py`.", "",
          f"Realized: home margin {out['realized']['home_margin']:+g}, total {out['realized']['total']:g} → cell `{out['realized']['cell']}`.", ""]
    md += RD._game_script_v2_section(view_all, compact=False)
    open(base + ".md", "w").write("\n".join(md) + "\n")
    print("wrote", base + ".json", base + ".md")


if __name__ == "__main__":
    main()
