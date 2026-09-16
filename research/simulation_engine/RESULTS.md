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

## 2024: 285 games, 67656 player-stat rows

| statistic | n | MAE | baseline MAE | Δ% | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier |
|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1626 | 3.534 | 4.040 | -12.5 | 4.563 | -0.081 | 2.467 | 0.628 | 0.971 | 0.0796 |
| rush_yards | 1676 | 21.061 | 22.716 | -7.3 | 28.149 | -0.807 | 14.577 | 0.556 | 0.939 | 0.0919 |
| targets | 3347 | 2.035 | 2.139 | -4.9 | 2.656 | -0.138 | 1.468 | 0.731 | 0.981 | 0.1057 |
| receptions | 3135 | 1.623 | 1.662 | -2.3 | 2.095 | -0.159 | 1.154 | 0.733 | 0.979 | 0.1040 |
| rec_yards | 3570 | 20.745 | 21.331 | -2.7 | 27.851 | -1.599 | 14.475 | 0.647 | 0.957 | 0.0914 |
| attempts | 570 | 8.413 | 8.930 | -5.8 | 11.613 | 2.161 | 6.327 | 0.456 | 0.826 | 0.1208 |
| completions | 570 | 5.760 | 5.996 | -3.9 | 7.656 | 1.050 | 4.246 | 0.482 | 0.844 | 0.1051 |
| pass_yards | 570 | 68.795 | 70.287 | -2.1 | 88.842 | 8.818 | 49.987 | 0.463 | 0.865 | 0.1245 |
| pass_td | 570 | 0.914 | — | — | 1.115 | 0.033 | 0.597 | 0.758 | 0.961 | 0.1459 |
| any_td | 4411 | 0.384 | — | — | 0.525 | -0.018 | 0.209 | 0.859 | 0.981 | 0.1021 |

| team statistic | n | MAE | RMSE | bias | CRPS | cover90 |
|---|---|---|---|---|---|---|
| dropbacks | 570 | 6.428 | 8.226 | 0.081 | 4.612 | 0.900 |
| off_td | 570 | 1.000 | 1.290 | -0.079 | 0.701 | 0.954 |
| pass_att | 570 | 6.078 | 7.721 | -0.074 | 4.322 | 0.893 |
| pass_td | 570 | 0.878 | 1.093 | -0.046 | 0.589 | 0.965 |
| pass_yards | 570 | 53.945 | 68.110 | -4.801 | 38.349 | 0.932 |
| plays | 570 | 6.694 | 8.261 | 0.381 | 4.686 | 0.925 |
| points | 570 | 7.067 | 8.916 | -0.581 | 5.026 | 0.926 |
| rush_att | 570 | 5.695 | 7.019 | 0.393 | 3.970 | 0.925 |
| rush_td | 570 | 0.736 | 0.951 | -0.033 | 0.487 | 0.977 |
| rush_yards | 570 | 37.756 | 47.141 | 2.027 | 26.322 | 0.918 |
| targets | 570 | 5.871 | 7.423 | 0.058 | 4.164 | 0.898 |

## 2025: 285 games, 67648 player-stat rows

| statistic | n | MAE | baseline MAE | Δ% | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier |
|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1578 | 3.396 | 4.222 | -19.6 | 4.424 | -0.094 | 2.410 | 0.660 | 0.973 | 0.0782 |
| rush_yards | 1648 | 20.347 | 22.951 | -11.3 | 27.568 | 0.211 | 14.068 | 0.571 | 0.936 | 0.0884 |
| targets | 3280 | 2.014 | 2.098 | -4.0 | 2.581 | 0.090 | 1.433 | 0.735 | 0.987 | 0.1036 |
| receptions | 3071 | 1.562 | 1.604 | -2.6 | 1.999 | 0.094 | 1.097 | 0.760 | 0.987 | 0.0990 |
| rec_yards | 3520 | 20.451 | 21.097 | -3.1 | 27.226 | 0.274 | 14.110 | 0.666 | 0.957 | 0.0894 |
| attempts | 570 | 7.032 | 7.781 | -9.6 | 9.220 | 0.736 | 5.094 | 0.493 | 0.886 | 0.1078 |
| completions | 570 | 4.745 | 5.226 | -9.2 | 6.209 | 0.734 | 3.420 | 0.540 | 0.902 | 0.0941 |
| pass_yards | 570 | 60.218 | 64.713 | -6.9 | 76.987 | 3.583 | 42.983 | 0.518 | 0.904 | 0.1207 |
| pass_td | 570 | 0.910 | — | — | 1.108 | -0.028 | 0.604 | 0.723 | 0.974 | 0.1486 |
| any_td | 4332 | 0.395 | — | — | 0.536 | -0.005 | 0.213 | 0.864 | 0.984 | 0.1029 |

| team statistic | n | MAE | RMSE | bias | CRPS | cover90 |
|---|---|---|---|---|---|---|
| dropbacks | 570 | 6.519 | 8.120 | 0.597 | 4.585 | 0.900 |
| off_td | 570 | 1.049 | 1.293 | -0.007 | 0.716 | 0.977 |
| pass_att | 570 | 6.131 | 7.643 | 0.505 | 4.321 | 0.900 |
| pass_td | 570 | 0.917 | 1.115 | -0.012 | 0.610 | 0.977 |
| pass_yards | 570 | 54.134 | 68.272 | 3.757 | 38.319 | 0.926 |
| plays | 570 | 6.744 | 8.511 | 0.704 | 4.782 | 0.904 |
| points | 570 | 7.282 | 9.011 | -0.053 | 5.127 | 0.926 |
| rush_att | 570 | 5.640 | 7.102 | 0.185 | 3.990 | 0.911 |
| rush_td | 570 | 0.754 | 0.944 | 0.004 | 0.489 | 0.974 |
| rush_yards | 570 | 37.910 | 47.912 | 4.537 | 26.467 | 0.911 |
| targets | 570 | 5.845 | 7.330 | 0.696 | 4.129 | 0.914 |

## Coherence

Every simulated game in every season passed `simulate.coherence_report` (the backtest raises on the first failure): sum of player carries = team rush attempts, targets = team targets, receptions = completions, receiving yards = passing yards, QB attempts = team attempts, TD allocations = team TD counts, no negative or fractional counts, receptions <= targets, home + away = total, home - away = margin.  Ladders are monotone by construction -- one distribution per player-statistic.

## Point-in-time status

`tests/test_sim_pit.py` poisons every evaluation-season game after week 3 by a factor of 1,000 and asserts that no feature of an earlier row moves by a bit, with a negative control proving the same poison does reach later rows.  The first version of this layer FAILED that test: the shrinkage targets were computed over the whole assembled frame, so a week-1 projection's league priors had seen week 18.  See the PR description for the old-vs-clean metric delta.

