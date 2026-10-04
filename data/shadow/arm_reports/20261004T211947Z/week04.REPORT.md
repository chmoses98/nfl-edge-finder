# Three-arm game-centre experiment — 2026 week 4

> **INSUFFICIENT EVIDENCE.** 10 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 786 | 10 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 9 | 9 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 10 | 10 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 10 | 10 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 10 | 10 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 10 | 10 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

Raw rows are repeated snapshots of the same games and are never a sample size. The primary unit is `latest_pregame` (one row per game); the canonical horizons are one row per game per horizon.

## Game centres, per game (latest pregame snapshot)

| game | kickoff | T-min | arm | margin | total | actual margin | actual total | mkt@snap margin/total | close margin/total |
|---|---|---|---|---|---|---|---|---|---|
| 2026_04_PIT_CLE | 2026-10-02T00:15 | 32 | CURRENT | -2.50 | 37.50 | 3 | 51 | -2.5/37.5 (kalshi_implied) | -2.5/37.5 (OK) |
|  |  |  | DATA_ONLY | -3.50 | 40.25 |  |  |  |  |
|  |  |  | HYBRID_30 | -2.80 | 38.32 |  |  |  |  |
| 2026_04_IND_WAS | 2026-10-04T13:30 | 38 | CURRENT | -4.50 | 46.50 | -17 | 43 | -4.5/46.5 (kalshi_implied) | -4.5/46.5 (OK) |
|  |  |  | DATA_ONLY | -2.33 | 47.43 |  |  |  |  |
|  |  |  | HYBRID_30 | -3.85 | 46.78 |  |  |  |  |
| 2026_04_ARI_NYG | 2026-10-04T17:00 | 49 | CURRENT | -1.50 | 43.50 | 12 | 60 | -1.5/43.5 (kalshi_implied) | -1.5/43.5 (OK) |
|  |  |  | DATA_ONLY | 1.03 | 48.25 |  |  |  |  |
|  |  |  | HYBRID_30 | -0.74 | 44.93 |  |  |  |  |
| 2026_04_DAL_HOU | 2026-10-04T17:00 | 49 | CURRENT | 2.50 | 48.00 | -4 | 64 | 2.5/48.0 (kalshi_implied) | 2.5/48.0 (OK) |
|  |  |  | DATA_ONLY | 6.58 | 45.38 |  |  |  |  |
|  |  |  | HYBRID_30 | 3.72 | 47.22 |  |  |  |  |
| 2026_04_GB_TB | 2026-10-04T17:00 | 49 | CURRENT | -2.50 | 38.50 | -3 | 31 | -2.5/38.5 (kalshi_implied) | -1.5/38.0 (OK) |
|  |  |  | DATA_ONLY | 0.81 | 44.00 |  |  |  |  |
|  |  |  | HYBRID_30 | -1.51 | 40.15 |  |  |  |  |
| 2026_04_JAX_CIN | 2026-10-04T17:00 | 49 | CURRENT | 2.50 | 51.00 | -5 | 39 | 2.5/51.0 (kalshi_implied) | 2.5/51.0 (OK) |
|  |  |  | DATA_ONLY | -2.98 | 50.14 |  |  |  |  |
|  |  |  | HYBRID_30 | 0.86 | 50.74 |  |  |  |  |
| 2026_04_LA_PHI | 2026-10-04T17:00 | 49 | CURRENT | -3.50 | 42.50 | -4 | 44 | -3.5/42.5 (kalshi_implied) | -3.5/42.5 (OK) |
|  |  |  | DATA_ONLY | -4.94 | 45.64 |  |  |  |  |
|  |  |  | HYBRID_30 | -3.93 | 43.44 |  |  |  |  |
| 2026_04_NE_BUF | 2026-10-04T17:00 | 49 | CURRENT | 7.50 | 49.00 | -3 | 55 | 7.5/49.0 (kalshi_implied) | 7.0/49.5 (OK) |
|  |  |  | DATA_ONLY | 3.70 | 48.94 |  |  |  |  |
|  |  |  | HYBRID_30 | 6.36 | 48.98 |  |  |  |  |
| 2026_04_NYJ_CHI | 2026-10-04T17:00 | 49 | CURRENT | 3.50 | 42.50 | 11 | 35 | 3.5/42.5 (kalshi_implied) | 3.5/42.5 (OK) |
|  |  |  | DATA_ONLY | 9.37 | 46.34 |  |  |  |  |
|  |  |  | HYBRID_30 | 5.26 | 43.65 |  |  |  |  |
| 2026_04_TEN_BAL | 2026-10-04T17:00 | 49 | CURRENT | 12.00 | 42.50 | 6 | 42 | 12.0/42.5 (kalshi_implied) | 12.0/42.5 (OK) |
|  |  |  | DATA_ONLY | 10.62 | 46.32 |  |  |  |  |
|  |  |  | HYBRID_30 | 11.59 | 43.65 |  |  |  |  |

## Game-centre accuracy — latest_pregame (10 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 10 | 1 | 7.05 | 8.19 | 1.75 | 8.45 | 10.09 | -2.25 | 0.246 |
| DATA_ONLY | 10 | 1 | 6.24 | 7.60 | 2.24 | 9.30 | 10.49 | -0.13 | 0.231 |
| HYBRID_30 | 10 | 1 | 6.75 | 7.85 | 1.90 | 8.61 | 10.10 | -1.61 | 0.241 |
| market at snapshot | 10 | 1 | 7.05 | 8.19 | 1.75 | 8.45 | 10.09 | -2.25 | - |
| market at close | 10 | 1 | 7.10 | 8.14 | 1.80 | 8.35 | 10.02 | -2.25 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 10 | margin | -0.806 | 1.127 | [-3.014, 1.403] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 10 | total | 0.854 | 1.005 | [-1.116, 2.824] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | margin | -0.298 | 0.336 | [-0.956, 0.360] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | total | 0.158 | 0.325 | [-0.478, 0.794] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | margin | 0.507 | 0.798 | [-1.056, 2.071] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | total | -0.697 | 0.703 | [-2.074, 0.681] | 0.700 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 10 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 10 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | margin | -0.806 | 1.127 | [-3.014, 1.403] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | total | 0.854 | 1.005 | [-1.116, 2.824] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | margin | -0.298 | 0.336 | [-0.956, 0.360] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | total | 0.158 | 0.325 | [-0.478, 0.794] | 0.400 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | margin | -0.050 | 0.117 | [-0.279, 0.179] | 0.100 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | total | 0.100 | 0.067 | [-0.031, 0.231] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | margin | -0.856 | 1.076 | [-2.965, 1.254] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | total | 0.954 | 1.028 | [-1.061, 2.970] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | margin | -0.348 | 0.297 | [-0.931, 0.234] | 0.700 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | total | 0.258 | 0.353 | [-0.435, 0.950] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 10 | 2 | 0 | 8 | 0 | 1.000 | 0.500 | 3.11 |
| DATA_ONLY | total | 10 | 0 | 2 | 8 | 0 | 0.000 | 0.300 | 2.83 |
| HYBRID_30 | margin | 10 | 2 | 0 | 8 | 0 | 1.000 | 0.600 | 0.93 |
| HYBRID_30 | total | 10 | 0 | 2 | 8 | 0 | 0.000 | 0.400 | 0.85 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 3 | 4.02 | 4.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.17 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 2 | 14.68 | 14.75 | - |
| DATA_ONLY | total | 3-5 | 4 | 7.26 | 6.50 | - |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 6 | 6.47 | 6.42 | 1.000 |
| HYBRID_30 | margin | 1-2 | 4 | 7.17 | 8.00 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 6 | 8.59 | 8.75 | 0.000 |
| HYBRID_30 | total | 1-2 | 4 | 8.63 | 8.00 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 10}; DATA_ONLY quality states: {'OK': 10}; close centre status: {'OK': 10}.

## Game-centre accuracy — T-24h (9 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 9 | 1 | 7.17 | 8.39 | 2.50 | 7.89 | 9.51 | -1.00 | 0.236 |
| DATA_ONLY | 9 | 1 | 6.22 | 7.72 | 3.21 | 9.14 | 10.46 | 1.05 | 0.211 |
| HYBRID_30 | 9 | 1 | 6.82 | 8.02 | 2.71 | 8.16 | 9.68 | -0.38 | 0.224 |
| market at snapshot | 9 | 1 | 7.17 | 8.39 | 2.50 | 7.89 | 9.51 | -1.00 | - |
| market at close | 9 | 1 | 7.28 | 8.38 | 2.61 | 7.78 | 9.56 | -1.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 9 | margin | -0.951 | 1.239 | [-3.379, 1.476] | 0.556 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 9 | total | 1.255 | 1.061 | [-0.825, 3.335] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 9 | margin | -0.348 | 0.368 | [-1.069, 0.373] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 9 | total | 0.267 | 0.356 | [-0.431, 0.964] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 9 | margin | 0.603 | 0.878 | [-1.118, 2.324] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 9 | total | -0.988 | 0.730 | [-2.419, 0.443] | 0.667 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 9 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 9 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 9 | margin | -0.951 | 1.239 | [-3.379, 1.476] | 0.556 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 9 | total | 1.255 | 1.061 | [-0.825, 3.335] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 9 | margin | -0.348 | 0.368 | [-1.069, 0.373] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 9 | total | 0.267 | 0.356 | [-0.431, 0.964] | 0.444 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 9 | margin | -0.111 | 0.139 | [-0.383, 0.161] | 0.222 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 9 | total | 0.111 | 0.162 | [-0.206, 0.429] | 0.222 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 9 | margin | -1.062 | 1.181 | [-3.377, 1.252] | 0.556 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 9 | total | 1.366 | 1.054 | [-0.699, 3.431] | 0.222 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 9 | margin | -0.459 | 0.325 | [-1.095, 0.177] | 0.778 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 9 | total | 0.378 | 0.360 | [-0.327, 1.083] | 0.333 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 9 | 2 | 1 | 6 | 0 | 0.667 | 0.556 | 3.28 |
| DATA_ONLY | total | 9 | 3 | 2 | 4 | 0 | 0.600 | 0.444 | 2.85 |
| HYBRID_30 | margin | 9 | 2 | 1 | 6 | 0 | 0.667 | 0.667 | 0.99 |
| HYBRID_30 | total | 9 | 3 | 2 | 4 | 0 | 0.600 | 0.444 | 0.86 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 1 | 4.62 | 5.50 | 0.000 |
| DATA_ONLY | margin | 1-2 | 1 | 0.94 | 0.50 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.50 | 0.500 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 1 | 18.62 | 16.00 | - |
| DATA_ONLY | total | 3-5 | 4 | 7.26 | 6.38 | 0.667 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.00 | - |
| HYBRID_30 | margin | <=1 | 5 | 6.54 | 6.50 | 0.500 |
| HYBRID_30 | margin | 1-2 | 4 | 7.17 | 8.00 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 4 | 9.76 | 9.62 | 0.500 |
| HYBRID_30 | total | 1-2 | 5 | 6.88 | 6.50 | 0.667 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 9}; DATA_ONLY quality states: {'OK': 9}; close centre status: {'OK': 9}.

## Game-centre accuracy — T-6h (10 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 10 | 1 | 6.85 | 8.01 | 1.65 | 8.40 | 9.91 | -2.10 | 0.243 |
| DATA_ONLY | 10 | 1 | 6.24 | 7.60 | 2.24 | 9.30 | 10.49 | -0.13 | 0.232 |
| HYBRID_30 | 10 | 1 | 6.61 | 7.74 | 1.83 | 8.57 | 9.98 | -1.51 | 0.232 |
| market at snapshot | 10 | 1 | 6.85 | 8.01 | 1.65 | 8.40 | 9.91 | -2.10 | - |
| market at close | 10 | 1 | 7.10 | 8.14 | 1.80 | 8.35 | 10.02 | -2.25 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 10 | margin | -0.606 | 1.086 | [-2.734, 1.523] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 10 | total | 0.904 | 0.933 | [-0.925, 2.733] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | margin | -0.238 | 0.325 | [-0.874, 0.398] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | total | 0.173 | 0.310 | [-0.436, 0.781] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | margin | 0.367 | 0.768 | [-1.138, 1.873] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | total | -0.732 | 0.646 | [-1.997, 0.534] | 0.700 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 10 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 10 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | margin | -0.606 | 1.086 | [-2.734, 1.523] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | total | 0.904 | 0.933 | [-0.925, 2.733] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | margin | -0.238 | 0.325 | [-0.874, 0.398] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | total | 0.173 | 0.310 | [-0.436, 0.781] | 0.400 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | margin | -0.250 | 0.134 | [-0.513, 0.013] | 0.300 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | total | 0.050 | 0.138 | [-0.221, 0.321] | 0.100 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | margin | -0.856 | 1.076 | [-2.965, 1.254] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | total | 0.954 | 1.028 | [-1.061, 2.970] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | margin | -0.488 | 0.329 | [-1.134, 0.158] | 0.700 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | total | 0.223 | 0.395 | [-0.551, 0.997] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 10 | 1 | 2 | 7 | 0 | 0.333 | 0.500 | 2.91 |
| DATA_ONLY | total | 10 | 1 | 3 | 6 | 0 | 0.250 | 0.400 | 2.78 |
| HYBRID_30 | margin | 10 | 1 | 2 | 7 | 0 | 0.333 | 0.600 | 0.87 |
| HYBRID_30 | total | 10 | 1 | 3 | 6 | 0 | 0.250 | 0.400 | 0.83 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 1 | 4.62 | 5.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 2 | 3.72 | 3.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.67 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.25 | 0.000 |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.00 | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 2 | 14.68 | 14.75 | - |
| DATA_ONLY | total | 3-5 | 4 | 7.26 | 6.50 | 0.333 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 7 | 6.74 | 6.79 | 0.500 |
| HYBRID_30 | margin | 1-2 | 3 | 6.32 | 7.00 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 6 | 8.77 | 8.58 | 0.000 |
| HYBRID_30 | total | 1-2 | 4 | 8.27 | 8.12 | 0.333 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 10}; DATA_ONLY quality states: {'OK': 10}; close centre status: {'OK': 10}.

## Game-centre accuracy — T-90m (10 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 10 | 1 | 7.00 | 8.15 | 1.70 | 8.35 | 9.96 | -2.15 | 0.247 |
| DATA_ONLY | 10 | 1 | 6.24 | 7.60 | 2.24 | 9.30 | 10.49 | -0.13 | 0.232 |
| HYBRID_30 | 10 | 1 | 6.72 | 7.83 | 1.86 | 8.54 | 10.01 | -1.54 | 0.243 |
| market at snapshot | 10 | 1 | 7.00 | 8.15 | 1.70 | 8.35 | 9.96 | -2.15 | - |
| market at close | 10 | 1 | 7.10 | 8.14 | 1.80 | 8.35 | 10.02 | -2.25 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 10 | margin | -0.756 | 1.125 | [-2.960, 1.449] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 10 | total | 0.954 | 0.970 | [-0.946, 2.855] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | margin | -0.283 | 0.336 | [-0.941, 0.374] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | total | 0.188 | 0.316 | [-0.431, 0.806] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | margin | 0.472 | 0.796 | [-1.088, 2.033] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | total | -0.767 | 0.677 | [-2.093, 0.560] | 0.700 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 10 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 10 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | margin | -0.756 | 1.125 | [-2.960, 1.449] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | total | 0.954 | 0.970 | [-0.946, 2.855] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | margin | -0.283 | 0.336 | [-0.941, 0.374] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | total | 0.188 | 0.316 | [-0.431, 0.806] | 0.400 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | margin | -0.100 | 0.125 | [-0.344, 0.144] | 0.200 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | total | 0.000 | 0.129 | [-0.253, 0.253] | 0.100 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | margin | -0.856 | 1.076 | [-2.965, 1.254] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | total | 0.954 | 1.028 | [-1.061, 2.970] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | margin | -0.383 | 0.300 | [-0.971, 0.205] | 0.700 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | total | 0.188 | 0.383 | [-0.563, 0.938] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 10 | 2 | 1 | 7 | 0 | 0.667 | 0.500 | 3.06 |
| DATA_ONLY | total | 10 | 0 | 3 | 7 | 0 | 0.000 | 0.300 | 2.73 |
| HYBRID_30 | margin | 10 | 2 | 1 | 7 | 0 | 0.667 | 0.600 | 0.92 |
| HYBRID_30 | total | 10 | 0 | 3 | 7 | 0 | 0.000 | 0.400 | 0.82 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 1 | 4.62 | 5.50 | 0.000 |
| DATA_ONLY | margin | 1-2 | 2 | 3.72 | 3.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.17 | 0.000 |
| DATA_ONLY | total | 1-2 | 1 | 10.75 | 12.50 | 0.000 |
| DATA_ONLY | total | 2-3 | 1 | 18.62 | 16.00 | - |
| DATA_ONLY | total | 3-5 | 4 | 7.26 | 6.50 | - |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 6 | 6.41 | 6.33 | 0.500 |
| HYBRID_30 | margin | 1-2 | 4 | 7.17 | 8.00 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 6 | 8.48 | 8.58 | 0.000 |
| HYBRID_30 | total | 1-2 | 4 | 8.63 | 8.00 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 10}; DATA_ONLY quality states: {'OK': 10}; close centre status: {'OK': 10}.

## Game-centre accuracy — T-30m (10 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 10 | 1 | 7.05 | 8.19 | 1.75 | 8.45 | 10.09 | -2.25 | 0.246 |
| DATA_ONLY | 10 | 1 | 6.24 | 7.60 | 2.24 | 9.30 | 10.49 | -0.13 | 0.231 |
| HYBRID_30 | 10 | 1 | 6.75 | 7.85 | 1.90 | 8.61 | 10.10 | -1.61 | 0.241 |
| market at snapshot | 10 | 1 | 7.05 | 8.19 | 1.75 | 8.45 | 10.09 | -2.25 | - |
| market at close | 10 | 1 | 7.10 | 8.14 | 1.80 | 8.35 | 10.02 | -2.25 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 10 | margin | -0.806 | 1.127 | [-3.014, 1.403] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 10 | total | 0.854 | 1.005 | [-1.116, 2.824] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | margin | -0.298 | 0.336 | [-0.956, 0.360] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | total | 0.158 | 0.325 | [-0.478, 0.794] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | margin | 0.507 | 0.798 | [-1.056, 2.071] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | total | -0.697 | 0.703 | [-2.074, 0.681] | 0.700 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 10 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 10 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | margin | -0.806 | 1.127 | [-3.014, 1.403] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | total | 0.854 | 1.005 | [-1.116, 2.824] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | margin | -0.298 | 0.336 | [-0.956, 0.360] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | total | 0.158 | 0.325 | [-0.478, 0.794] | 0.400 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | margin | -0.050 | 0.117 | [-0.279, 0.179] | 0.100 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | total | 0.100 | 0.067 | [-0.031, 0.231] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | margin | -0.856 | 1.076 | [-2.965, 1.254] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | total | 0.954 | 1.028 | [-1.061, 2.970] | 0.300 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | margin | -0.348 | 0.297 | [-0.931, 0.234] | 0.700 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | total | 0.258 | 0.353 | [-0.435, 0.950] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 10 | 2 | 0 | 8 | 0 | 1.000 | 0.500 | 3.11 |
| DATA_ONLY | total | 10 | 0 | 2 | 8 | 0 | 0.000 | 0.300 | 2.83 |
| HYBRID_30 | margin | 10 | 2 | 0 | 8 | 0 | 1.000 | 0.600 | 0.93 |
| HYBRID_30 | total | 10 | 0 | 2 | 8 | 0 | 0.000 | 0.400 | 0.85 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 3 | 4.02 | 4.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.17 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 2 | 14.68 | 14.75 | - |
| DATA_ONLY | total | 3-5 | 4 | 7.26 | 6.50 | - |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 6 | 6.47 | 6.42 | 1.000 |
| HYBRID_30 | margin | 1-2 | 4 | 7.17 | 8.00 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 6 | 8.59 | 8.75 | 0.000 |
| HYBRID_30 | total | 1-2 | 4 | 8.63 | 8.00 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 10}; DATA_ONLY quality states: {'OK': 10}; close centre status: {'OK': 10}.

## Contract pricing — latest_pregame (776 contracts, 10 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 776 | 0.1338 | 0.4112 | 0.413 | 0.402 | 776 | 0.1338 | 0.1328 | 0.1349 |
| DATA_ONLY | 776 | 0.1303 | 0.4034 | 0.435 | 0.402 | 776 | 0.1303 | 0.1328 | 0.1349 |
| HYBRID_30 | 776 | 0.1319 | 0.4075 | 0.419 | 0.402 | 776 | 0.1319 | 0.1328 | 0.1349 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 776 | 10 | -0.00351 | [-0.02420, 0.01769] | -0.00351 | [-0.02420, 0.01769] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 776 | 10 | -0.00192 | [-0.00757, 0.00400] | -0.00192 | [-0.00757, 0.00400] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 776 | 10 | 0.00159 | [-0.01402, 0.01742] | 0.00159 | [-0.01402, 0.01742] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 776 | 10 | - | - | 0.00100 | [-0.00026, 0.00226] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 766 | 10 | - | - | 0.00063 | [-0.00064, 0.00192] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 776 | 10 | - | - | -0.00251 | [-0.02377, 0.01917] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 766 | 10 | - | - | -0.00293 | [-0.02455, 0.01907] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 776 | 10 | - | - | -0.00092 | [-0.00687, 0.00494] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 766 | 10 | - | - | -0.00132 | [-0.00752, 0.00493] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 40, 'GAME_WINNER': 20, 'SPREAD': 253, 'TEAM_TOTAL': 273, 'TOTAL': 190}; settlement: {'SETTLED': 776}; close: {'OK': 766, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 118 / 0.054 / 0.008 | 110 / 0.056 / 0.009 | 115 / 0.055 / 0.009 |
| 0.10-0.20 | 123 / 0.145 / 0.065 | 120 / 0.147 / 0.067 | 120 / 0.145 / 0.100 |
| 0.20-0.30 | 98 / 0.250 / 0.265 | 89 / 0.251 / 0.213 | 93 / 0.250 / 0.183 |
| 0.30-0.40 | 80 / 0.352 / 0.325 | 77 / 0.351 / 0.286 | 80 / 0.350 / 0.312 |
| 0.40-0.50 | 75 / 0.448 / 0.427 | 73 / 0.446 / 0.384 | 81 / 0.450 / 0.395 |
| 0.50-0.60 | 84 / 0.547 / 0.548 | 72 / 0.553 / 0.472 | 80 / 0.548 / 0.550 |
| 0.60-0.70 | 42 / 0.650 / 0.667 | 59 / 0.648 / 0.610 | 52 / 0.650 / 0.692 |
| 0.70-0.80 | 42 / 0.755 / 0.786 | 45 / 0.745 / 0.822 | 38 / 0.759 / 0.763 |
| 0.80-0.90 | 39 / 0.852 / 0.949 | 43 / 0.845 / 0.907 | 39 / 0.850 / 0.974 |
| 0.90-1.00 | 75 / 0.955 / 1.000 | 88 / 0.957 / 1.000 | 78 / 0.953 / 1.000 |

## Contract pricing — T-24h (698 contracts, 9 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 698 | 0.1318 | 0.4067 | 0.417 | 0.393 | 698 | 0.1318 | 0.1328 | 0.1333 |
| DATA_ONLY | 698 | 0.1295 | 0.4022 | 0.437 | 0.393 | 698 | 0.1295 | 0.1328 | 0.1333 |
| HYBRID_30 | 698 | 0.1294 | 0.4013 | 0.423 | 0.393 | 698 | 0.1294 | 0.1328 | 0.1333 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 698 | 9 | -0.00239 | [-0.02726, 0.02177] | -0.00239 | [-0.02726, 0.02177] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 698 | 9 | -0.00244 | [-0.01093, 0.00516] | -0.00244 | [-0.01093, 0.00516] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 698 | 9 | -0.00005 | [-0.01688, 0.01751] | -0.00005 | [-0.01688, 0.01751] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 698 | 9 | - | - | -0.00093 | [-0.00287, 0.00071] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 688 | 9 | - | - | 0.00042 | [-0.00132, 0.00262] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 698 | 9 | - | - | -0.00332 | [-0.02747, 0.01991] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 688 | 9 | - | - | -0.00200 | [-0.02699, 0.02213] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 698 | 9 | - | - | -0.00337 | [-0.01148, 0.00302] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 688 | 9 | - | - | -0.00205 | [-0.01094, 0.00563] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 36, 'GAME_WINNER': 18, 'SPREAD': 228, 'TEAM_TOTAL': 245, 'TOTAL': 171}; settlement: {'SETTLED': 698}; close: {'OK': 688, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 109 / 0.055 / 0.009 | 96 / 0.056 / 0.010 | 100 / 0.055 / 0.010 |
| 0.10-0.20 | 106 / 0.144 / 0.075 | 109 / 0.146 / 0.073 | 114 / 0.147 / 0.079 |
| 0.20-0.30 | 90 / 0.251 / 0.222 | 80 / 0.251 / 0.188 | 82 / 0.253 / 0.195 |
| 0.30-0.40 | 65 / 0.349 / 0.323 | 69 / 0.350 / 0.275 | 68 / 0.349 / 0.279 |
| 0.40-0.50 | 72 / 0.451 / 0.361 | 67 / 0.443 / 0.343 | 73 / 0.448 / 0.384 |
| 0.50-0.60 | 71 / 0.548 / 0.549 | 63 / 0.552 / 0.429 | 68 / 0.552 / 0.544 |
| 0.60-0.70 | 38 / 0.645 / 0.605 | 54 / 0.650 / 0.611 | 48 / 0.647 / 0.583 |
| 0.70-0.80 | 41 / 0.754 / 0.780 | 43 / 0.749 / 0.791 | 38 / 0.752 / 0.789 |
| 0.80-0.90 | 35 / 0.854 / 0.943 | 35 / 0.845 / 0.914 | 36 / 0.851 / 0.972 |
| 0.90-1.00 | 71 / 0.957 / 1.000 | 82 / 0.957 / 1.000 | 71 / 0.955 / 1.000 |

## Contract pricing — T-6h (776 contracts, 10 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 776 | 0.1317 | 0.4066 | 0.414 | 0.402 | 776 | 0.1317 | 0.1328 | 0.1349 |
| DATA_ONLY | 776 | 0.1303 | 0.4036 | 0.435 | 0.402 | 776 | 0.1303 | 0.1328 | 0.1349 |
| HYBRID_30 | 776 | 0.1301 | 0.4029 | 0.417 | 0.402 | 776 | 0.1301 | 0.1328 | 0.1349 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 776 | 10 | -0.00141 | [-0.02170, 0.01939] | -0.00141 | [-0.02170, 0.01939] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 776 | 10 | -0.00167 | [-0.00699, 0.00373] | -0.00167 | [-0.00699, 0.00373] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 776 | 10 | -0.00026 | [-0.01570, 0.01512] | -0.00026 | [-0.01570, 0.01512] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 776 | 10 | - | - | -0.00104 | [-0.00338, 0.00090] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 766 | 10 | - | - | -0.00145 | [-0.00394, 0.00075] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 776 | 10 | - | - | -0.00245 | [-0.02308, 0.01868] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 766 | 10 | - | - | -0.00288 | [-0.02433, 0.01927] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 776 | 10 | - | - | -0.00271 | [-0.00997, 0.00343] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 766 | 10 | - | - | -0.00314 | [-0.01066, 0.00360] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 40, 'GAME_WINNER': 20, 'SPREAD': 253, 'TEAM_TOTAL': 273, 'TOTAL': 190}; settlement: {'SETTLED': 776}; close: {'OK': 766, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 118 / 0.053 / 0.008 | 109 / 0.055 / 0.000 | 116 / 0.054 / 0.009 |
| 0.10-0.20 | 120 / 0.145 / 0.075 | 122 / 0.146 / 0.074 | 120 / 0.146 / 0.100 |
| 0.20-0.30 | 99 / 0.251 / 0.232 | 90 / 0.252 / 0.211 | 99 / 0.252 / 0.172 |
| 0.30-0.40 | 77 / 0.350 / 0.351 | 75 / 0.351 / 0.307 | 75 / 0.350 / 0.320 |
| 0.40-0.50 | 82 / 0.447 / 0.402 | 73 / 0.444 / 0.356 | 82 / 0.445 / 0.390 |
| 0.50-0.60 | 76 / 0.547 / 0.539 | 73 / 0.553 / 0.493 | 78 / 0.549 / 0.590 |
| 0.60-0.70 | 48 / 0.644 / 0.667 | 62 / 0.651 / 0.629 | 52 / 0.651 / 0.673 |
| 0.70-0.80 | 39 / 0.753 / 0.795 | 43 / 0.750 / 0.791 | 39 / 0.761 / 0.795 |
| 0.80-0.90 | 43 / 0.851 / 0.953 | 43 / 0.849 / 0.930 | 38 / 0.855 / 0.974 |
| 0.90-1.00 | 74 / 0.956 / 1.000 | 86 / 0.958 / 1.000 | 77 / 0.955 / 1.000 |

## Contract pricing — T-90m (776 contracts, 10 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 776 | 0.1326 | 0.4084 | 0.414 | 0.402 | 776 | 0.1326 | 0.1329 | 0.1349 |
| DATA_ONLY | 776 | 0.1305 | 0.4040 | 0.435 | 0.402 | 776 | 0.1305 | 0.1329 | 0.1349 |
| HYBRID_30 | 776 | 0.1327 | 0.4091 | 0.418 | 0.402 | 776 | 0.1327 | 0.1329 | 0.1349 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 776 | 10 | -0.00205 | [-0.02308, 0.01928] | -0.00205 | [-0.02308, 0.01928] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 776 | 10 | 0.00006 | [-0.00600, 0.00583] | 0.00006 | [-0.00600, 0.00583] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 776 | 10 | 0.00211 | [-0.01433, 0.01849] | 0.00211 | [-0.01433, 0.01849] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 776 | 10 | - | - | -0.00027 | [-0.00187, 0.00102] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 766 | 10 | - | - | -0.00058 | [-0.00229, 0.00077] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 776 | 10 | - | - | -0.00232 | [-0.02343, 0.01893] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 766 | 10 | - | - | -0.00266 | [-0.02424, 0.01937] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 776 | 10 | - | - | -0.00021 | [-0.00607, 0.00545] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 766 | 10 | - | - | -0.00051 | [-0.00662, 0.00535] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 40, 'GAME_WINNER': 20, 'SPREAD': 253, 'TEAM_TOTAL': 273, 'TOTAL': 190}; settlement: {'SETTLED': 776}; close: {'OK': 766, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 120 / 0.055 / 0.008 | 112 / 0.056 / 0.009 | 116 / 0.054 / 0.009 |
| 0.10-0.20 | 120 / 0.145 / 0.058 | 121 / 0.148 / 0.066 | 122 / 0.147 / 0.098 |
| 0.20-0.30 | 98 / 0.250 / 0.255 | 87 / 0.252 / 0.218 | 92 / 0.251 / 0.185 |
| 0.30-0.40 | 80 / 0.351 / 0.338 | 76 / 0.350 / 0.303 | 80 / 0.350 / 0.350 |
| 0.40-0.50 | 75 / 0.448 / 0.400 | 72 / 0.443 / 0.361 | 84 / 0.452 / 0.393 |
| 0.50-0.60 | 84 / 0.547 / 0.571 | 74 / 0.552 / 0.500 | 76 / 0.550 / 0.553 |
| 0.60-0.70 | 42 / 0.649 / 0.667 | 58 / 0.648 / 0.603 | 52 / 0.652 / 0.654 |
| 0.70-0.80 | 41 / 0.755 / 0.780 | 46 / 0.745 / 0.804 | 34 / 0.755 / 0.794 |
| 0.80-0.90 | 40 / 0.852 / 0.950 | 42 / 0.846 / 0.905 | 43 / 0.849 / 0.953 |
| 0.90-1.00 | 76 / 0.955 / 1.000 | 88 / 0.957 / 1.000 | 77 / 0.955 / 1.000 |

## Contract pricing — T-30m (776 contracts, 10 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 776 | 0.1338 | 0.4112 | 0.413 | 0.402 | 776 | 0.1338 | 0.1328 | 0.1349 |
| DATA_ONLY | 776 | 0.1303 | 0.4034 | 0.435 | 0.402 | 776 | 0.1303 | 0.1328 | 0.1349 |
| HYBRID_30 | 776 | 0.1319 | 0.4075 | 0.419 | 0.402 | 776 | 0.1319 | 0.1328 | 0.1349 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 776 | 10 | -0.00351 | [-0.02420, 0.01769] | -0.00351 | [-0.02420, 0.01769] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 776 | 10 | -0.00192 | [-0.00757, 0.00400] | -0.00192 | [-0.00757, 0.00400] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 776 | 10 | 0.00159 | [-0.01402, 0.01742] | 0.00159 | [-0.01402, 0.01742] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 776 | 10 | - | - | 0.00100 | [-0.00026, 0.00226] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 766 | 10 | - | - | 0.00063 | [-0.00064, 0.00192] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 776 | 10 | - | - | -0.00251 | [-0.02377, 0.01917] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 766 | 10 | - | - | -0.00293 | [-0.02455, 0.01907] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 776 | 10 | - | - | -0.00092 | [-0.00687, 0.00494] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 766 | 10 | - | - | -0.00132 | [-0.00752, 0.00493] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 40, 'GAME_WINNER': 20, 'SPREAD': 253, 'TEAM_TOTAL': 273, 'TOTAL': 190}; settlement: {'SETTLED': 776}; close: {'OK': 766, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 118 / 0.054 / 0.008 | 110 / 0.056 / 0.009 | 115 / 0.055 / 0.009 |
| 0.10-0.20 | 123 / 0.145 / 0.065 | 120 / 0.147 / 0.067 | 120 / 0.145 / 0.100 |
| 0.20-0.30 | 98 / 0.250 / 0.265 | 89 / 0.251 / 0.213 | 93 / 0.250 / 0.183 |
| 0.30-0.40 | 80 / 0.352 / 0.325 | 77 / 0.351 / 0.286 | 80 / 0.350 / 0.312 |
| 0.40-0.50 | 75 / 0.448 / 0.427 | 73 / 0.446 / 0.384 | 81 / 0.450 / 0.395 |
| 0.50-0.60 | 84 / 0.547 / 0.548 | 72 / 0.553 / 0.472 | 80 / 0.548 / 0.550 |
| 0.60-0.70 | 42 / 0.650 / 0.667 | 59 / 0.648 / 0.610 | 52 / 0.650 / 0.692 |
| 0.70-0.80 | 42 / 0.755 / 0.786 | 45 / 0.745 / 0.822 | 38 / 0.759 / 0.763 |
| 0.80-0.90 | 39 / 0.852 / 0.949 | 43 / 0.845 / 0.907 | 39 / 0.850 / 0.974 |
| 0.90-1.00 | 75 / 0.955 / 1.000 | 88 / 0.957 / 1.000 | 78 / 0.953 / 1.000 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 9 | 1 | 2 | 0 | 6 | 0 | 1.000 [0.342, 1.000] | 0.500 | 0.500 | 0.19 |
| T-24h | DATA_ONLY | total | 9 | 3 | 2 | 1 | 3 | 0 | 0.667 [0.208, 0.939] | 0.333 | 0.167 | 0.08 |
| T-24h | HYBRID_30 (derived) | margin | 9 | 5 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.750 | 0.750 | 0.12 |
| T-24h | HYBRID_30 (derived) | total | 9 | 4 | 2 | 1 | 2 | 0 | 0.667 [0.208, 0.939] | 0.400 | 0.400 | 0.10 |
| T-6h | DATA_ONLY | margin | 10 | 1 | 1 | 1 | 7 | 0 | 0.500 [0.095, 0.905] | 0.444 | 0.444 | 0.06 |
| T-6h | DATA_ONLY | total | 10 | 3 | 1 | 3 | 3 | 0 | 0.250 [0.046, 0.699] | 0.429 | 0.286 | -0.21 |
| T-6h | HYBRID_30 (derived) | margin | 10 | 7 | 0 | 1 | 2 | 0 | 0.000 [0.000, 0.793] | 0.667 | 0.667 | -0.17 |
| T-6h | HYBRID_30 (derived) | total | 10 | 6 | 1 | 2 | 1 | 0 | 0.333 [0.061, 0.792] | 0.500 | 0.500 | -0.25 |
| T-90m | DATA_ONLY | margin | 10 | 1 | 2 | 0 | 7 | 0 | 1.000 [0.342, 1.000] | 0.444 | 0.444 | 0.17 |
| T-90m | DATA_ONLY | total | 10 | 3 | 0 | 2 | 5 | 0 | 0.000 [0.000, 0.658] | 0.286 | 0.286 | -0.21 |
| T-90m | HYBRID_30 (derived) | margin | 10 | 6 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.750 | 0.750 | 0.12 |
| T-90m | HYBRID_30 (derived) | total | 10 | 6 | 0 | 1 | 3 | 0 | 0.000 [0.000, 0.793] | 0.250 | 0.250 | -0.12 |
| T-30m | DATA_ONLY | margin | 10 | 0 | 2 | 0 | 8 | 0 | 1.000 [0.342, 1.000] | 0.500 | 0.500 | 0.15 |
| T-30m | DATA_ONLY | total | 10 | 3 | 0 | 1 | 6 | 0 | 0.000 [0.000, 0.793] | 0.286 | 0.286 | -0.07 |
| T-30m | HYBRID_30 (derived) | margin | 10 | 6 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.750 | 0.750 | 0.12 |
| T-30m | HYBRID_30 (derived) | total | 10 | 6 | 0 | 1 | 3 | 0 | 0.000 [0.000, 0.793] | 0.250 | 0.250 | -0.12 |
| latest_pregame | DATA_ONLY | margin | 10 | 0 | 2 | 0 | 8 | 0 | 1.000 [0.342, 1.000] | 0.500 | 0.500 | 0.15 |
| latest_pregame | DATA_ONLY | total | 10 | 3 | 0 | 1 | 6 | 0 | 0.000 [0.000, 0.793] | 0.286 | 0.286 | -0.07 |
| latest_pregame | HYBRID_30 (derived) | margin | 10 | 6 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.750 | 0.750 | 0.12 |
| latest_pregame | HYBRID_30 (derived) | total | 10 | 6 | 0 | 1 | 3 | 0 | 0.000 [0.000, 0.793] | 0.250 | 0.250 | -0.12 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 0 | 0 | 0 | 0 | 0 | - |
| margin | 1-2 | 3 | 0 | 0 | 3 | 0 | - |
| margin | 2-3 | 2 | 0 | 0 | 2 | 0 | - |
| margin | 3-5 | 3 | 2 | 0 | 1 | 0 | 1.000 |
| margin | >5 | 2 | 0 | 0 | 2 | 0 | - |
| total | <=1 | 3 | 0 | 1 | 2 | 0 | 0.000 |
| total | 1-2 | 0 | 0 | 0 | 0 | 0 | - |
| total | 2-3 | 2 | 0 | 0 | 2 | 0 | - |
| total | 3-5 | 4 | 0 | 0 | 4 | 0 | - |
| total | >5 | 1 | 0 | 1 | 0 | 0 | 0.000 |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

63 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_04_PIT_CLE | Raheim Sanders | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.1 | 2 | 0.87 | 3.50 | EXPECTED_ACTIVE | True | -0.402 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | receiving_yards | 8.0 | 0–35 | 43 | 5.27 | 0.96 | 1.7 | 7 | 4.83 | 6.14 | EXPECTED_ACTIVE | True | 0.213 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Denzel Boston | receiving_yards | 19.9 | 0–67 | 89 | 3.95 | 0.97 | 1.9 | 7 | 10.55 | 12.71 | EXPECTED_ACTIVE | True | 0.386 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Roman Wilson | receiving_yards | 17.3 | 0–59 | 74 | 3.71 | 0.97 | 1.9 | 6 | 8.91 | 12.33 | EXPECTED_ACTIVE | True | 0.224 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Roman Wilson | touchdowns | 0.1 | -–- | 1 | 3.57 | - | 3.2 | 6 | - | - | EXPECTED_ACTIVE | True | 0.082 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | receiving_yards | 9.7 | 0–42 | 33 | 3.42 | 0.89 | 1.6 | 6 | 5.97 | 5.50 | EXPECTED_ACTIVE | True | 0.486 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Darnell Washington | touchdowns | 0.1 | -–- | 1 | 3.42 | - | 2.7 | 5 | - | - | EXPECTED_ACTIVE | True | 0.047 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | receptions | 1.2 | 0–5 | 6 | 3.37 | 0.96 | 1.7 | 7 | 0.72 | 0.86 | EXPECTED_ACTIVE | True | 0.278 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Deshaun Watson | carries | 2.3 | 0–18 | 7 | 3.15 | 0.80 | 2.3 | 7 | - | - | EXPECTED_ACTIVE | True | 0.611 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Pat Freiermuth | touchdowns | 0.1 | -–- | 1 | 3.01 | - | 3.1 | 5 | - | - | EXPECTED_ACTIVE | True | 0.097 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaleel McLaughlin | touchdowns | 0.1 | -–- | 1 | 2.88 | - | 8.1 | 1 | - | - | QUESTIONABLE | True | -0.048 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Raheim Sanders | receptions | 0.8 | 0–5 | 2 | 2.70 | 0.80 | 1.1 | 2 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.376 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | DK Metcalf | receiving_yards | 42.3 | 3–98 | 115 | 2.66 | 0.97 | 4.2 | 9 | 9.98 | 12.78 | EXPECTED_ACTIVE | True | 0.108 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Harold Fannin Jr. | touchdowns | 0.2 | -–- | 1 | 2.14 | - | 4.9 | 5 | - | - | EXPECTED_ACTIVE | True | 0.059 | UNEXPLAINED_VARIANCE |
| 2026_04_PIT_CLE | Denzel Boston | receptions | 1.2 | 0–5 | 4 | 2.02 | 0.88 | 1.9 | 7 | 0.62 | 0.57 | EXPECTED_ACTIVE | True | 0.456 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | rushing_yards | 42.9 | 3–110 | 93 | 1.81 | 0.88 | 7.8 | 17 | 5.50 | 5.47 | EXPECTED_ACTIVE | True | 0.388 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | touchdowns | 0.2 | -–- | 1 | 1.79 | - | 13.9 | 24 | - | - | EXPECTED_ACTIVE | True | 0.161 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | carries | 9.7 | 3–20 | 17 | 1.54 | 0.86 | 9.7 | 17 | - | - | EXPECTED_ACTIVE | True | 0.469 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | carries | 7.8 | 1–19 | 17 | 1.52 | 0.89 | 7.8 | 17 | - | - | EXPECTED_ACTIVE | True | 0.607 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | interceptions | 0.8 | 0–3 | 2 | 1.35 | 0.85 | 33.5 | 40 | 0.02 | 0.05 | EXPECTED_ACTIVE | True | -0.063 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | passing_tds | 1.2 | 0–3 | 3 | 1.35 | 0.95 | 33.5 | 40 | 0.04 | 0.07 | EXPECTED_ACTIVE | True | 0.052 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Pat Freiermuth | receptions | 1.4 | 0–5 | 3 | 1.35 | 0.82 | 2.0 | 5 | 0.70 | 0.60 | EXPECTED_ACTIVE | True | 0.408 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | receptions | 1.3 | 0–5 | 3 | 1.35 | 0.82 | 1.6 | 6 | 0.77 | 0.50 | EXPECTED_ACTIVE | True | 0.497 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Darnell Washington | receptions | 1.2 | 0–5 | 3 | 1.35 | 0.82 | 1.8 | 5 | 0.70 | 0.60 | EXPECTED_ACTIVE | True | 0.231 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Roman Wilson | receptions | 1.2 | 0–5 | 3 | 1.35 | 0.82 | 1.9 | 6 | 0.61 | 0.50 | EXPECTED_ACTIVE | True | 0.291 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | DK Metcalf | receptions | 2.5 | 0–6 | 5 | 1.35 | 0.85 | 4.2 | 9 | 0.58 | 0.56 | EXPECTED_ACTIVE | True | 0.203 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Darnell Washington | receiving_yards | 15.0 | 0–51 | 27 | 1.28 | 0.79 | 1.8 | 5 | 8.42 | 5.40 | EXPECTED_ACTIVE | True | 0.217 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | passing_yards | 226.4 | 102–351 | 299 | 0.97 | 0.81 | 33.5 | 40 | 6.75 | 7.47 | EXPECTED_ACTIVE | True | -0.054 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | attempts | 33.5 | 19–48 | 40 | 0.74 | 0.77 | 33.5 | 40 | - | - | EXPECTED_ACTIVE | True | -0.003 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Deshaun Watson | passing_yards | 214.0 | 89–339 | 268 | 0.71 | 0.76 | 33.3 | 33 | 6.43 | 8.12 | EXPECTED_ACTIVE | True | -0.160 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Jerry Jeudy | receptions | 2.1 | 0–6 | 3 | 0.67 | 0.75 | 3.8 | 3 | 0.55 | 1.00 | EXPECTED_ACTIVE | True | -0.150 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Harold Fannin Jr. | receptions | 2.1 | 0–6 | 3 | 0.67 | 0.75 | 3.2 | 5 | 0.66 | 0.60 | EXPECTED_ACTIVE | True | 0.317 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Germie Bernard | receptions | 1.1 | 0–5 | 2 | 0.67 | 0.75 | 1.8 | 2 | 0.61 | 1.00 | EXPECTED_ACTIVE | True | 0.036 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | rushing_yards | 40.2 | 3–103 | 53 | 0.59 | 0.69 | 9.7 | 17 | 4.15 | 3.12 | EXPECTED_ACTIVE | True | 0.254 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | touchdowns | 0.2 | -–- | 0 | -0.56 | - | 12.5 | 23 | - | - | EXPECTED_ACTIVE | True | -0.250 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Deshaun Watson | completions | 20.9 | 11–31 | 24 | 0.51 | 0.69 | 33.3 | 33 | 0.63 | 0.73 | EXPECTED_ACTIVE | True | -0.135 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | DK Metcalf | touchdowns | 0.2 | -–- | 0 | -0.46 | - | 5.8 | 9 | - | - | EXPECTED_ACTIVE | True | -0.123 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | rushing_yards | 9.1 | 0–32 | 0 | -0.45 | 0.05 | 2.5 | 0 | 3.59 | - | EXPECTED_ACTIVE | True | 0.100 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Michael Pittman Jr. | touchdowns | 0.2 | -–- | 0 | -0.42 | - | 5.3 | 4 | - | - | EXPECTED_ACTIVE | True | -0.045 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Pat Freiermuth | receiving_yards | 19.2 | 0–65 | 17 | 0.42 | 0.62 | 2.0 | 5 | 9.56 | 3.40 | EXPECTED_ACTIVE | True | 0.344 | EFFICIENCY_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 10, 'OPPORTUNITY_MISS': 38, 'UNEXPLAINED_VARIANCE': 1, 'NO_LARGE_MISS': 14}.
Missing usage (no snap table or stats row): 0.

## Decision funnel

No funnel accounting is available for this period.

## Player-autopsy coverage — 2026 week 4

Expected games 16 · eligible 16 · diagnosed 1 · excluded 15 · canonical projection units 63 (63 with a box-score value) · eligible units 1053, eligible but undiagnosed 990

| game | included | diagnosed units | raw records | eligible units | undiagnosed | rule | exclusion reason |
|---|---|---|---|---|---|---|---|
| 2026_04_ARI_NYG | NO | 0 | 0 | 62 | 62 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_ATL_NO | NO | 0 | 0 | 62 | 62 | — | game not final (or no kickoff) when the report was built |
| 2026_04_DAL_HOU | NO | 0 | 0 | 70 | 70 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_DEN_SF | NO | 0 | 0 | 68 | 68 | — | game not final (or no kickoff) when the report was built |
| 2026_04_DET_CAR | NO | 0 | 0 | 60 | 60 | — | game not final (or no kickoff) when the report was built |
| 2026_04_GB_TB | NO | 0 | 0 | 65 | 65 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_IND_WAS | NO | 0 | 0 | 70 | 70 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_JAX_CIN | NO | 0 | 0 | 73 | 73 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_KC_LV | NO | 0 | 0 | 67 | 67 | — | game not final (or no kickoff) when the report was built |
| 2026_04_LAC_SEA | NO | 0 | 0 | 72 | 72 | — | game not final (or no kickoff) when the report was built |
| 2026_04_LA_PHI | NO | 0 | 0 | 62 | 62 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_MIA_MIN | NO | 0 | 0 | 65 | 65 | — | game not final (or no kickoff) when the report was built |
| 2026_04_NE_BUF | NO | 0 | 0 | 69 | 69 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_NYJ_CHI | NO | 0 | 0 | 60 | 60 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_PIT_CLE | yes | 63 | 63 | 63 | 0 | autopsy-1.1.0 |  |
| 2026_04_TEN_BAL | NO | 0 | 0 | 65 | 65 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |

