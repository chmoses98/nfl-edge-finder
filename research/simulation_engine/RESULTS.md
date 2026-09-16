# Simulation engine (sim-1.0.0): walk-forward evidence

Reproduce: `python scripts/sim/walkforward.py --seasons 2023,2024,2025` then `python scripts/sim/reconciliation_study.py`.

**HISTORICAL_RESEARCH.** For each season Y the bundle is fitted on seasons 2018..Y-1 (2016-17 warm the features), every game of Y is simulated (10,000 rows) with the consensus closing line as the centre, and one row per (game, player, statistic) is scored against the box score.  Baseline = the naive prior-only projection (EWMA share x EWMA team volume, EWMA rate x count).  Coverage = share of outcomes inside the central 50% / 90% predictive interval.  Ladder Brier = mean Brier of P(Y >= k) over a fixed threshold grid per statistic (research/simulation_engine/backtest.py::LADDERS), on players whose predictive mean clears a small floor.

## 2023: 285 games, 67544 player-stat rows

| statistic | n | MAE | baseline MAE | Δ% | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier |
|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1611 | 3.506 | 4.130 | -15.1 | 4.564 | 0.033 | 2.468 | 0.647 | 0.964 | 0.0788 |
| rush_yards | 1677 | 19.541 | 21.758 | -10.2 | 25.949 | 1.388 | 13.474 | 0.577 | 0.942 | 0.0857 |
| targets | 3292 | 2.055 | 2.104 | -2.3 | 2.648 | -0.133 | 1.478 | 0.720 | 0.987 | 0.1066 |
| receptions | 3079 | 1.627 | 1.647 | -1.2 | 2.104 | -0.132 | 1.157 | 0.739 | 0.986 | 0.1040 |
| rec_yards | 3466 | 21.311 | 21.827 | -2.4 | 29.022 | -1.749 | 14.863 | 0.636 | 0.951 | 0.0936 |
| attempts | 570 | 8.196 | 8.707 | -5.9 | 11.303 | 1.454 | 6.112 | 0.470 | 0.846 | 0.1170 |
| completions | 570 | 5.722 | 6.005 | -4.7 | 7.626 | 0.715 | 4.227 | 0.474 | 0.837 | 0.1062 |
| pass_yards | 570 | 69.665 | 72.446 | -3.8 | 89.236 | 5.316 | 50.662 | 0.470 | 0.847 | 0.1259 |
| pass_td | 570 | 0.842 | — | — | 1.038 | 0.074 | 0.553 | 0.796 | 0.977 | 0.1367 |
| any_td | 4340 | 0.370 | — | — | 0.504 | -0.001 | 0.195 | 0.874 | 0.985 | 0.0953 |

| team statistic | n | MAE | RMSE | bias | CRPS | cover90 |
|---|---|---|---|---|---|---|
| dropbacks | 570 | 6.361 | 7.997 | -0.755 | 4.487 | 0.923 |
| off_td | 570 | 1.031 | 1.306 | 0.022 | 0.706 | 0.972 |
| pass_att | 570 | 6.008 | 7.464 | -0.757 | 4.212 | 0.909 |
| pass_td | 570 | 0.820 | 1.043 | 0.006 | 0.554 | 0.974 |
| pass_yards | 570 | 54.311 | 67.842 | -8.537 | 38.599 | 0.930 |
| plays | 570 | 6.726 | 8.392 | -0.158 | 4.732 | 0.918 |
| points | 570 | 7.352 | 9.305 | -0.189 | 5.204 | 0.932 |
| rush_att | 570 | 5.901 | 7.225 | 0.608 | 4.101 | 0.918 |
| rush_td | 570 | 0.720 | 0.887 | 0.015 | 0.461 | 0.988 |
| rush_yards | 570 | 38.068 | 46.929 | 8.253 | 26.012 | 0.895 |
| targets | 570 | 5.709 | 7.123 | -0.587 | 4.003 | 0.916 |

## 2024: 285 games, 67656 player-stat rows

| statistic | n | MAE | baseline MAE | Δ% | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier |
|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1629 | 3.529 | 4.038 | -12.6 | 4.560 | -0.082 | 2.465 | 0.627 | 0.970 | 0.0795 |
| rush_yards | 1685 | 21.055 | 22.722 | -7.3 | 28.128 | -0.802 | 14.578 | 0.554 | 0.936 | 0.0919 |
| targets | 3351 | 2.034 | 2.135 | -4.7 | 2.656 | -0.149 | 1.468 | 0.731 | 0.980 | 0.1057 |
| receptions | 3123 | 1.627 | 1.665 | -2.3 | 2.099 | -0.169 | 1.157 | 0.732 | 0.978 | 0.1042 |
| rec_yards | 3581 | 20.707 | 21.278 | -2.7 | 27.819 | -1.640 | 14.448 | 0.647 | 0.956 | 0.0913 |
| attempts | 570 | 8.409 | 8.924 | -5.8 | 11.608 | 2.129 | 6.323 | 0.460 | 0.825 | 0.1208 |
| completions | 570 | 5.757 | 5.996 | -4.0 | 7.649 | 1.013 | 4.244 | 0.479 | 0.844 | 0.1050 |
| pass_yards | 570 | 68.737 | 70.250 | -2.2 | 88.748 | 8.355 | 49.950 | 0.460 | 0.867 | 0.1244 |
| pass_td | 570 | 0.914 | — | — | 1.115 | 0.033 | 0.597 | 0.754 | 0.960 | 0.1459 |
| any_td | 4404 | 0.385 | — | — | 0.525 | -0.018 | 0.209 | 0.857 | 0.982 | 0.1022 |

| team statistic | n | MAE | RMSE | bias | CRPS | cover90 |
|---|---|---|---|---|---|---|
| dropbacks | 570 | 6.428 | 8.225 | 0.084 | 4.610 | 0.900 |
| off_td | 570 | 1.000 | 1.290 | -0.079 | 0.701 | 0.954 |
| pass_att | 570 | 6.075 | 7.720 | -0.108 | 4.322 | 0.893 |
| pass_td | 570 | 0.878 | 1.092 | -0.046 | 0.589 | 0.965 |
| pass_yards | 570 | 53.928 | 68.100 | -5.281 | 38.355 | 0.930 |
| plays | 570 | 6.693 | 8.260 | 0.383 | 4.684 | 0.925 |
| points | 570 | 7.067 | 8.916 | -0.581 | 5.026 | 0.926 |
| rush_att | 570 | 5.698 | 7.021 | 0.411 | 3.971 | 0.923 |
| rush_td | 570 | 0.736 | 0.951 | -0.033 | 0.487 | 0.977 |
| rush_yards | 570 | 37.797 | 47.178 | 2.207 | 26.343 | 0.918 |
| targets | 570 | 5.868 | 7.421 | -0.005 | 4.162 | 0.900 |

## 2025: 285 games, 67648 player-stat rows

| statistic | n | MAE | baseline MAE | Δ% | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier |
|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1575 | 3.396 | 4.227 | -19.7 | 4.426 | -0.095 | 2.411 | 0.660 | 0.972 | 0.0782 |
| rush_yards | 1653 | 20.335 | 22.943 | -11.4 | 27.537 | 0.262 | 14.049 | 0.572 | 0.935 | 0.0882 |
| targets | 3276 | 2.012 | 2.097 | -4.1 | 2.579 | 0.086 | 1.432 | 0.735 | 0.987 | 0.1035 |
| receptions | 3073 | 1.561 | 1.602 | -2.5 | 1.998 | 0.090 | 1.097 | 0.760 | 0.986 | 0.0989 |
| rec_yards | 3519 | 20.423 | 21.061 | -3.0 | 27.195 | 0.254 | 14.094 | 0.666 | 0.957 | 0.0893 |
| attempts | 570 | 7.028 | 7.780 | -9.7 | 9.217 | 0.715 | 5.090 | 0.493 | 0.886 | 0.1078 |
| completions | 570 | 4.742 | 5.226 | -9.3 | 6.205 | 0.711 | 3.418 | 0.539 | 0.904 | 0.0940 |
| pass_yards | 570 | 60.189 | 64.711 | -7.0 | 76.950 | 3.305 | 42.953 | 0.516 | 0.898 | 0.1206 |
| pass_td | 570 | 0.910 | — | — | 1.108 | -0.029 | 0.604 | 0.721 | 0.974 | 0.1487 |
| any_td | 4332 | 0.396 | — | — | 0.537 | -0.007 | 0.214 | 0.862 | 0.984 | 0.1034 |

| team statistic | n | MAE | RMSE | bias | CRPS | cover90 |
|---|---|---|---|---|---|---|
| dropbacks | 570 | 6.519 | 8.120 | 0.598 | 4.585 | 0.900 |
| off_td | 570 | 1.049 | 1.293 | -0.007 | 0.716 | 0.977 |
| pass_att | 570 | 6.128 | 7.641 | 0.490 | 4.320 | 0.902 |
| pass_td | 570 | 0.917 | 1.115 | -0.012 | 0.610 | 0.977 |
| pass_yards | 570 | 54.103 | 68.256 | 3.515 | 38.318 | 0.923 |
| plays | 570 | 6.744 | 8.510 | 0.704 | 4.781 | 0.904 |
| points | 570 | 7.282 | 9.011 | -0.053 | 5.127 | 0.926 |
| rush_att | 570 | 5.640 | 7.102 | 0.194 | 3.990 | 0.911 |
| rush_td | 570 | 0.754 | 0.944 | 0.004 | 0.489 | 0.974 |
| rush_yards | 570 | 37.889 | 47.893 | 4.624 | 26.465 | 0.905 |
| targets | 570 | 5.841 | 7.326 | 0.665 | 4.127 | 0.914 |

## 2025 Kalshi rungs: football-only vs market vs reconciled

28347 settled archived rungs; rows scored where the football distribution and a two-sided quote within 10 cents exist at the horizon.  `market` = the monotone midpoint of the quoted ladder (research construct, not executable).  Weights fitted on weeks 1-9, confirmed on weeks 10-22 (paired Brier vs market, game-clustered SE).

### T-0 (21697 rows, 264 games)

| statistic | n (all) | Brier football | Brier market | mean football / market / rate | w (weeks 1-9) | confirm n | Brier reconciled | Brier market | Δ vs market | z | b_football | b_market |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| any_td | 3720 | 0.1583 | 0.1570 | 0.212 / 0.230 / 0.226 | 0.60 | 2050 | 0.1513 | 0.1514 | -0.00007 | -0.1 | 0.20 | 0.75 |
| pass_td | 684 | 0.1513 | 0.1533 | 0.349 / 0.363 / 0.357 | — | — | — | — | — | — | 1.39 | -0.39 |
| pass_yards | 2602 | 0.1693 | 0.1597 | 0.337 / 0.353 / 0.343 | 0.00 | 2048 | 0.1648 | 0.1620 | 0.00281 | 2.0 | -0.16 | 1.14 |
| rec_yards | 6834 | 0.2148 | 0.2090 | 0.381 / 0.430 / 0.404 | 0.00 | 5439 | 0.2108 | 0.2094 | 0.00145 | 1.6 | 0.08 | 0.89 |
| receptions | 4445 | 0.1889 | 0.1829 | 0.383 / 0.424 / 0.385 | 0.00 | 4413 | 0.1846 | 0.1829 | 0.00170 | 1.6 | 0.02 | 0.91 |
| rush_yards | 3412 | 0.2146 | 0.2090 | 0.383 / 0.431 / 0.414 | 0.25 | 2813 | 0.2066 | 0.2051 | 0.00152 | 0.8 | 0.19 | 0.73 |

Weight fitted on all of 2025 (the value the 2026 season uses):

| statistic | w | Brier curve (w: Brier) |
|---|---|---|
| any_td | 0.70 | 0.00: 0.1587, 0.20: 0.1581, 0.40: 0.1577, 0.60: 0.1575, 0.80: 0.1575, 1.00: 0.1583 |
| pass_td | 1.00 | 0.00: 0.1533, 0.20: 0.1527, 0.40: 0.1522, 0.60: 0.1517, 0.80: 0.1514, 1.00: 0.1513 |
| pass_yards | 0.00 | 0.00: 0.1626, 0.20: 0.1632, 0.40: 0.1640, 0.60: 0.1653, 0.80: 0.1669, 1.00: 0.1693 |
| rec_yards | 0.05 | 0.00: 0.2106, 0.20: 0.2107, 0.40: 0.2111, 0.60: 0.2118, 0.80: 0.2131, 1.00: 0.2148 |
| receptions | 0.15 | 0.00: 0.1847, 0.20: 0.1846, 0.40: 0.1849, 0.60: 0.1857, 0.80: 0.1869, 1.00: 0.1889 |
| rush_yards | 0.05 | 0.00: 0.2093, 0.20: 0.2094, 0.40: 0.2099, 0.60: 0.2109, 0.80: 0.2124, 1.00: 0.2146 |

Disagreement bands (|football − market| at the rung, weeks 1-9 fit rows): best weight, market Brier, football Brier

| statistic | band | n | best w | Brier market | Brier football | Brier best |
|---|---|---|---|---|---|---|
| any_td | 0.00-0.05 | 1150 | 1.00 | 0.1488 | 0.1483 | 0.1483 |
| any_td | 0.05-0.10 | 372 | 0.40 | 0.1907 | 0.1943 | 0.1918 |
| any_td | 0.10-0.20 | 136 | 0.00 | 0.2150 | 0.2375 | 0.2181 |
| pass_yards | 0.00-0.05 | 310 | 0.35 | 0.1419 | 0.1424 | 0.1416 |
| pass_yards | 0.05-0.10 | 147 | 0.00 | 0.1710 | 0.1827 | 0.1745 |
| pass_yards | 0.10-0.20 | 93 | 0.00 | 0.1505 | 0.1856 | 0.1628 |
| rec_yards | 0.00-0.05 | 556 | 1.00 | 0.1973 | 0.1974 | 0.1974 |
| rec_yards | 0.05-0.10 | 401 | 0.70 | 0.2135 | 0.2129 | 0.2125 |
| rec_yards | 0.10-0.20 | 351 | 0.00 | 0.2078 | 0.2304 | 0.2141 |
| rec_yards | 0.20-1.01 | 87 | 0.00 | 0.2435 | 0.2939 | 0.2389 |
| rush_yards | 0.00-0.05 | 233 | 1.00 | 0.2083 | 0.2071 | 0.2071 |
| rush_yards | 0.05-0.10 | 153 | 0.00 | 0.2179 | 0.2170 | 0.2123 |
| rush_yards | 0.10-0.20 | 164 | 0.00 | 0.2448 | 0.2555 | 0.2440 |
| rush_yards | 0.20-1.01 | 49 | 0.70 | 0.2901 | 0.2500 | 0.2474 |

### T-24h (16931 rows, 250 games)

| statistic | n (all) | Brier football | Brier market | mean football / market / rate | w (weeks 1-9) | confirm n | Brier reconciled | Brier market | Δ vs market | z | b_football | b_market |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| any_td | 2894 | 0.1547 | 0.1533 | 0.206 / 0.222 / 0.219 | 0.45 | 1773 | 0.1503 | 0.1501 | 0.00019 | 0.3 | 0.23 | 0.71 |
| pass_td | 651 | 0.1553 | 0.1579 | 0.357 / 0.368 / 0.367 | — | — | — | — | — | — | 1.55 | -0.54 |
| pass_yards | 2143 | 0.1692 | 0.1651 | 0.335 / 0.346 / 0.342 | 0.15 | 1816 | 0.1704 | 0.1696 | 0.00088 | 0.9 | 0.14 | 0.83 |
| rec_yards | 5294 | 0.2153 | 0.2093 | 0.384 / 0.434 / 0.412 | 0.00 | 4321 | 0.2110 | 0.2096 | 0.00141 | 1.5 | 0.13 | 0.87 |
| receptions | 3384 | 0.1904 | 0.1839 | 0.389 / 0.435 / 0.392 | — | — | — | — | — | — | -0.07 | 1.00 |
| rush_yards | 2565 | 0.2165 | 0.2097 | 0.381 / 0.420 / 0.425 | 0.15 | 2252 | 0.2093 | 0.2075 | 0.00180 | 1.3 | 0.14 | 0.77 |

Weight fitted on all of 2025 (the value the 2026 season uses):

| statistic | w | Brier curve (w: Brier) |
|---|---|---|
| any_td | 0.70 | 0.00: 0.1555, 0.20: 0.1548, 0.40: 0.1543, 0.60: 0.1540, 0.80: 0.1541, 1.00: 0.1547 |
| pass_td | 1.00 | 0.00: 0.1577, 0.20: 0.1570, 0.40: 0.1564, 0.60: 0.1559, 0.80: 0.1556, 1.00: 0.1553 |
| pass_yards | 0.10 | 0.00: 0.1661, 0.20: 0.1661, 0.40: 0.1663, 0.60: 0.1669, 0.80: 0.1678, 1.00: 0.1692 |
| rec_yards | 0.10 | 0.00: 0.2112, 0.20: 0.2113, 0.40: 0.2116, 0.60: 0.2123, 0.80: 0.2135, 1.00: 0.2153 |
| receptions | 0.05 | 0.00: 0.1855, 0.20: 0.1856, 0.40: 0.1861, 0.60: 0.1870, 0.80: 0.1884, 1.00: 0.1904 |
| rush_yards | 0.10 | 0.00: 0.2114, 0.20: 0.2114, 0.40: 0.2119, 0.60: 0.2129, 0.80: 0.2143, 1.00: 0.2165 |

Disagreement bands (|football − market| at the rung, weeks 1-9 fit rows): best weight, market Brier, football Brier

| statistic | band | n | best w | Brier market | Brier football | Brier best |
|---|---|---|---|---|---|---|
| any_td | 0.00-0.05 | 734 | 1.00 | 0.1421 | 0.1427 | 0.1427 |
| any_td | 0.05-0.10 | 272 | 0.50 | 0.1810 | 0.1850 | 0.1818 |
| any_td | 0.10-0.20 | 104 | 0.00 | 0.2122 | 0.2287 | 0.2190 |
| pass_yards | 0.00-0.05 | 202 | 0.70 | 0.1061 | 0.1068 | 0.1067 |
| pass_yards | 0.05-0.10 | 83 | 0.95 | 0.2119 | 0.2057 | 0.2057 |
| pass_yards | 0.10-0.20 | 39 | 0.00 | 0.1667 | 0.2053 | 0.1723 |
| rec_yards | 0.00-0.05 | 368 | 1.00 | 0.1903 | 0.1899 | 0.1899 |
| rec_yards | 0.05-0.10 | 267 | 0.80 | 0.2245 | 0.2227 | 0.2223 |
| rec_yards | 0.10-0.20 | 266 | 0.00 | 0.2181 | 0.2408 | 0.2237 |
| rec_yards | 0.20-1.01 | 72 | 0.00 | 0.2036 | 0.2998 | 0.2283 |
| rush_yards | 0.00-0.05 | 144 | 1.00 | 0.2174 | 0.2114 | 0.2114 |
| rush_yards | 0.05-0.10 | 71 | 1.00 | 0.2451 | 0.2366 | 0.2366 |
| rush_yards | 0.10-0.20 | 77 | 0.00 | 0.2278 | 0.2564 | 0.2356 |

## Coherence

Every simulated game in every season passed `simulate.coherence_report` (the backtest raises on the first failure): Σ player carries = team rush attempts, Σ targets = team targets, Σ receptions = completions, Σ receiving yards = passing yards, Σ QB attempts = team attempts, TD allocations = team TD counts, no negative or fractional counts, receptions ≤ targets, home + away = total, home − away = margin.  Ladders are monotone by construction (one distribution per player-statistic).

