# Simulation engine (sim-1.0.0): walk-forward evidence

Reproduce: `python scripts/sim/walkforward.py --seasons 2023,2024,2025`.  Generated from `walkforward.json` by `scripts/sim/write_results.py` -- do not edit by hand.

**HISTORICAL_RESEARCH.** For each evaluation season Y:

* the shrinkage priors (league levels, pooled rates, rate denominators, position rates) are fitted on the RAW rows of seasons strictly before Y and frozen (`training.fit_priors_for`), then applied to Y;
* the frames are rebuilt per evaluation season so no statistic of Y can reach a row of Y;
* the model bundle is fitted on 2018..Y-1 (2016-17 warm the EWMAs);
* every game of Y is simulated (10,000 rows) with the nflverse consensus CLOSING line as the game centre, and one row per (game, player, statistic) is scored against the box score.

Baseline = the naive prior-only projection (EWMA share x EWMA team volume; EWMA rate x count). Coverage = share of outcomes inside the central 50% / 90% predictive interval.  Ladder Brier = mean Brier of P(Y >= k) over the fixed threshold grid in `backtest.LADDERS`, on players whose predictive mean clears a small per-statistic floor.

## 2023: 285 games, 67544 player-stat rows

| statistic | n | MAE | baseline MAE | Δ% | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier |
|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1609 | 3.507 | 4.127 | -15.0 | 4.566 | 0.029 | 2.468 | 0.649 | 0.965 | 0.0788 |
| rush_yards | 1668 | 19.578 | 21.797 | -10.2 | 26.000 | 1.329 | 13.505 | 0.577 | 0.942 | 0.0859 |
| targets | 3302 | 2.052 | 2.105 | -2.5 | 2.645 | -0.115 | 1.475 | 0.721 | 0.987 | 0.1063 |
| receptions | 3081 | 1.627 | 1.648 | -1.3 | 2.103 | -0.121 | 1.156 | 0.738 | 0.987 | 0.1039 |
| rec_yards | 3472 | 21.332 | 21.882 | -2.5 | 29.035 | -1.672 | 14.871 | 0.636 | 0.951 | 0.0936 |
| attempts | 570 | 8.197 | 8.708 | -5.9 | 11.313 | 1.514 | 6.114 | 0.467 | 0.847 | 0.1170 |
| completions | 570 | 5.722 | 6.004 | -4.7 | 7.633 | 0.778 | 4.230 | 0.477 | 0.833 | 0.1063 |
| pass_yards | 570 | 69.624 | 72.417 | -3.9 | 89.324 | 5.992 | 50.658 | 0.472 | 0.846 | 0.1259 |
| pass_td | 570 | 0.842 | — | — | 1.038 | 0.074 | 0.553 | 0.798 | 0.977 | 0.1367 |
| any_td | 4331 | 0.370 | — | — | 0.503 | -0.001 | 0.195 | 0.873 | 0.985 | 0.0951 |

| team statistic | n | MAE | RMSE | bias | CRPS | cover90 |
|---|---|---|---|---|---|---|
| dropbacks | 570 | 6.360 | 7.997 | -0.760 | 4.486 | 0.925 |
| off_td | 570 | 1.031 | 1.306 | 0.022 | 0.706 | 0.972 |
| pass_att | 570 | 6.004 | 7.457 | -0.695 | 4.207 | 0.909 |
| pass_td | 570 | 0.820 | 1.043 | 0.006 | 0.554 | 0.974 |
| pass_yards | 570 | 54.234 | 67.754 | -7.839 | 38.538 | 0.932 |
| plays | 570 | 6.726 | 8.391 | -0.160 | 4.731 | 0.918 |
| points | 570 | 7.352 | 9.305 | -0.189 | 5.204 | 0.932 |
| rush_att | 570 | 5.898 | 7.224 | 0.584 | 4.100 | 0.918 |
| rush_td | 570 | 0.720 | 0.887 | 0.016 | 0.461 | 0.988 |
| rush_yards | 570 | 38.036 | 46.906 | 8.126 | 25.991 | 0.904 |
| targets | 570 | 5.705 | 7.114 | -0.477 | 3.998 | 0.919 |

## Coherence

Every simulated game in every season passed `simulate.coherence_report` (the backtest raises on the first failure): sum of player carries = team rush attempts, targets = team targets, receptions = completions, receiving yards = passing yards, QB attempts = team attempts, TD allocations = team TD counts, no negative or fractional counts, receptions <= targets, home + away = total, home - away = margin.  Ladders are monotone by construction -- one distribution per player-statistic.

## Point-in-time status

`tests/test_sim_pit.py` poisons every evaluation-season game after week 3 by a factor of 1,000 and asserts that no feature of an earlier row moves by a bit, with a negative control proving the same poison does reach later rows.  The first version of this layer FAILED that test: the shrinkage targets were computed over the whole assembled frame, so a week-1 projection's league priors had seen week 18.  See the PR description for the old-vs-clean metric delta.

