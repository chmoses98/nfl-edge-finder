#!/usr/bin/env python3
"""Render research/simulation_engine/RESULTS.md from walkforward.json and reconciliation_2025.json."""
from __future__ import annotations
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "research", "simulation_engine")


def f(x, nd=3):
    return "—" if x is None else (f"{x:.{nd}f}" if isinstance(x, (int, float)) else str(x))


def main():
    wf = json.load(open(os.path.join(OUT, "walkforward.json")))
    rec_path = os.path.join(OUT, "reconciliation_2025.json")
    rec = json.load(open(rec_path)) if os.path.exists(rec_path) else None
    L = ["# Simulation engine (sim-1.0.0): walk-forward evidence", "",
         "Reproduce: `python scripts/sim/walkforward.py --seasons 2023,2024,2025` then `python scripts/sim/reconciliation_study.py`.", "",
         "**HISTORICAL_RESEARCH.** For each season Y the bundle is fitted on seasons 2018..Y-1 (2016-17 warm the features), every "
         "game of Y is simulated (10,000 rows) with the consensus closing line as the centre, and one row per (game, player, "
         "statistic) is scored against the box score.  Baseline = the naive prior-only projection (EWMA share x EWMA team volume, "
         "EWMA rate x count).  Coverage = share of outcomes inside the central 50% / 90% predictive interval.  Ladder Brier = mean "
         "Brier of P(Y >= k) over a fixed threshold grid per statistic (research/simulation_engine/backtest.py::LADDERS), on players "
         "whose predictive mean clears a small floor.", ""]
    stats = ["carries", "rush_yards", "targets", "receptions", "rec_yards", "attempts", "completions", "pass_yards", "pass_td", "any_td"]
    for y in sorted(wf):
        ev = wf[y]["evaluation"]; run = wf[y]["run"]
        L += [f"## {y}: {run['games']} games, {run['player_rows']} player-stat rows", "",
              "| statistic | n | MAE | baseline MAE | Δ% | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for st in stats:
            r = ev["player"].get(st)
            if not r:
                continue
            L.append(f"| {st} | {r['n']} | {f(r['mae'])} | {f(r.get('baseline_mae'))} | {f(r.get('mae_vs_baseline_pct'), 1)} | {f(r['rmse'])} | "
                     f"{f(r['bias'])} | {f(r['crps'])} | {f(r['cover50'])} | {f(r['cover90'])} | {f(r.get('ladder_brier'), 4)} |")
        L += ["", "| team statistic | n | MAE | RMSE | bias | CRPS | cover90 |", "|---|---|---|---|---|---|---|"]
        for st, r in ev["team"].items():
            L.append(f"| {st} | {r['n']} | {f(r['mae'])} | {f(r['rmse'])} | {f(r['bias'])} | {f(r['crps'])} | {f(r['cover90'])} |")
        L.append("")
    if rec:
        L += ["## 2025 Kalshi rungs: football-only vs market vs reconciled", "",
              f"{rec['n_rungs_archive']} settled archived rungs; rows scored where the football distribution and a two-sided quote "
              "within 10 cents exist at the horizon.  `market` = the monotone midpoint of the quoted ladder (research construct, "
              "not executable).  Weights fitted on weeks 1-9, confirmed on weeks 10-22 (paired Brier vs market, game-clustered SE).", ""]
        for h, hr in rec["horizons"].items():
            L += [f"### {h} ({hr['n_scored']} rows, {hr['games']} games)", "",
                  "| statistic | n (all) | Brier football | Brier market | mean football / market / rate | w (weeks 1-9) | confirm n | Brier reconciled | Brier market | Δ vs market | z | b_football | b_market |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for st, b in hr["by_stat_all"].items():
                fw = hr["fitted_on_fit_weeks"].get(st, {}); c = hr["confirmed_on_later_weeks"].get(st, {}); e = hr["encompassing_all"].get(st, {})
                L.append(f"| {st} | {b['n']} | {f(b['brier_football'], 4)} | {f(b['brier_market_mono'], 4)} | "
                         f"{f(b['mean_football'])} / {f(b['mean_market'])} / {f(b['rate'])} | {f(fw.get('weight'), 2)} | {c.get('n', '—')} | "
                         f"{f(c.get('brier_reconciled'), 4)} | {f(c.get('brier_market_mono'), 4)} | {f(c.get('diff_vs_market'), 5)} | {f(c.get('z'), 1)} | "
                         f"{f(e.get('b_football'), 2)} | {f(e.get('b_market'), 2)} |")
            L.append("")
            L += ["Weight fitted on all of 2025 (the value the 2026 season uses):", "", "| statistic | w | Brier curve (w: Brier) |", "|---|---|---|"]
            for st, v in hr["fitted_on_all_2025"].items():
                curve = ", ".join(f"{k}: {vv:.4f}" for k, vv in list(v["brier_curve"].items())[::4])
                L.append(f"| {st} | {v['weight']:.2f} | {curve} |")
            L.append("")
            L += ["Disagreement bands (|football − market| at the rung, weeks 1-9 fit rows): best weight, market Brier, football Brier", "",
                  "| statistic | band | n | best w | Brier market | Brier football | Brier best |", "|---|---|---|---|---|---|---|"]
            for st, v in hr["fitted_on_fit_weeks"].items():
                for bd in v.get("bands", []):
                    L.append(f"| {st} | {bd['band'][0]:.2f}-{bd['band'][1]:.2f} | {bd['n']} | {bd['best_w']:.2f} | {f(bd['brier_market'], 4)} | {f(bd['brier_football'], 4)} | {f(bd['brier_best'], 4)} |")
            L.append("")
    L += ["## Coherence", "", "Every simulated game in every season passed `simulate.coherence_report` (the backtest raises on the first failure): "
          "Σ player carries = team rush attempts, Σ targets = team targets, Σ receptions = completions, Σ receiving yards = passing yards, "
          "Σ QB attempts = team attempts, TD allocations = team TD counts, no negative or fractional counts, receptions ≤ targets, "
          "home + away = total, home − away = margin.  Ladders are monotone by construction (one distribution per player-statistic).", ""]
    open(os.path.join(OUT, "RESULTS.md"), "w").write("\n".join(L) + "\n")
    print("wrote RESULTS.md")


if __name__ == "__main__":
    main()
