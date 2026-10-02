# Three-arm game-centre experiment — 2026 week 3

> **INSUFFICIENT EVIDENCE.** 16 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 1309 | 16 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 6 | 6 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 16 | 16 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 16 | 16 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 16 | 16 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

Raw rows are repeated snapshots of the same games and are never a sample size. The primary unit is `latest_pregame` (one row per game); the canonical horizons are one row per game per horizon.

## Game centres, per game (latest pregame snapshot)

| game | kickoff | T-min | arm | margin | total | actual margin | actual total | mkt@snap margin/total | close margin/total |
|---|---|---|---|---|---|---|---|---|---|
| 2026_03_ATL_GB | 2026-09-25T00:15 | 30 | CURRENT | 5.50 | 42.00 | -21 | 49 | 5.5/42.0 (kalshi_implied) | 5.5/42.0 (OK) |
|  |  |  | DATA_ONLY | 7.14 | 42.90 |  |  |  |  |
|  |  |  | HYBRID_30 | 5.99 | 42.27 |  |  |  |  |
| 2026_03_CAR_CLE | 2026-09-27T17:00 | 39 | CURRENT | -1.50 | 41.50 | 3 | 39 | -1.5/41.5 (kalshi_implied) | -1.5/41.5 (OK) |
|  |  |  | DATA_ONLY | -3.60 | 41.11 |  |  |  |  |
|  |  |  | HYBRID_30 | -2.13 | 41.38 |  |  |  |  |
| 2026_03_CIN_PIT | 2026-09-27T17:00 | 39 | CURRENT | -2.50 | 42.50 | 3 | 57 | -2.5/42.5 (kalshi_implied) | -2.5/42.5 (OK) |
|  |  |  | DATA_ONLY | -0.20 | 42.69 |  |  |  |  |
|  |  |  | HYBRID_30 | -1.81 | 42.56 |  |  |  |  |
| 2026_03_HOU_IND | 2026-09-27T17:00 | 39 | CURRENT | -0.50 | 42.00 | 2 | 36 | -0.5/42.0 (kalshi_implied) | -0.5/42.5 (OK) |
|  |  |  | DATA_ONLY | -3.04 | 43.13 |  |  |  |  |
|  |  |  | HYBRID_30 | -1.26 | 42.34 |  |  |  |  |
| 2026_03_KC_MIA | 2026-09-27T17:00 | 39 | CURRENT | -10.50 | 45.50 | -14 | 34 | -10.5/45.5 (kalshi_implied) | -10.5/45.5 (OK) |
|  |  |  | DATA_ONLY | -6.16 | 45.95 |  |  |  |  |
|  |  |  | HYBRID_30 | -9.20 | 45.64 |  |  |  |  |
| 2026_03_LAC_BUF | 2026-09-27T17:00 | 39 | CURRENT | 7.50 | 49.50 | 8 | 40 | 7.5/49.5 (kalshi_implied) | 7.0/51.0 (OK) |
|  |  |  | DATA_ONLY | 10.19 | 46.91 |  |  |  |  |
|  |  |  | HYBRID_30 | 8.31 | 48.72 |  |  |  |  |
| 2026_03_NE_JAX | 2026-09-27T17:00 | 39 | CURRENT | 2.50 | 45.50 | 29 | 41 | 2.5/45.5 (kalshi_implied) | 2.5/46.0 (OK) |
|  |  |  | DATA_ONLY | 1.09 | 48.38 |  |  |  |  |
|  |  |  | HYBRID_30 | 2.08 | 46.36 |  |  |  |  |
| 2026_03_NYJ_DET | 2026-09-27T17:00 | 39 | CURRENT | 7.50 | 48.00 | 7 | 55 | 7.5/48.0 (kalshi_implied) | 7.0/49.5 (OK) |
|  |  |  | DATA_ONLY | 6.41 | 48.63 |  |  |  |  |
|  |  |  | HYBRID_30 | 7.17 | 48.19 |  |  |  |  |
| 2026_03_SEA_WAS | 2026-09-27T17:00 | 39 | CURRENT | -8.50 | 40.50 | 2 | 64 | -8.5/40.5 (kalshi_implied) | -8.5/39.5 (OK) |
|  |  |  | DATA_ONLY | -10.46 | 41.36 |  |  |  |  |
|  |  |  | HYBRID_30 | -9.09 | 40.76 |  |  |  |  |
| 2026_03_TEN_NYG | 2026-09-27T17:00 | 39 | CURRENT | 1.50 | 37.50 | 5 | 19 | 1.5/37.5 (kalshi_implied) | 1.5/37.5 (OK) |
|  |  |  | DATA_ONLY | 3.43 | 45.58 |  |  |  |  |
|  |  |  | HYBRID_30 | 2.08 | 39.92 |  |  |  |  |
| 2026_03_ARI_SF | 2026-09-27T20:05 | 31 | CURRENT | 8.50 | 48.50 | 6 | 66 | 8.5/48.5 (kalshi_implied) | 9.0/48.5 (OK) |
|  |  |  | DATA_ONLY | 10.50 | 49.43 |  |  |  |  |
|  |  |  | HYBRID_30 | 9.10 | 48.78 |  |  |  |  |
| 2026_03_MIN_TB | 2026-09-27T20:05 | 31 | CURRENT | -0.50 | 42.50 | -7 | 39 | -0.5/42.5 (kalshi_implied) | -0.5/42.5 (OK) |
|  |  |  | DATA_ONLY | -1.80 | 40.28 |  |  |  |  |
|  |  |  | HYBRID_30 | -0.89 | 41.83 |  |  |  |  |
| 2026_03_BAL_DAL | 2026-09-27T20:25 | 51 | CURRENT | -3.50 | 53.50 | -3 | 65 | -3.5/53.5 (kalshi_implied) | -3.5/53.5 (OK) |
|  |  |  | DATA_ONLY | -6.48 | 52.40 |  |  |  |  |
|  |  |  | HYBRID_30 | -4.39 | 53.17 |  |  |  |  |
| 2026_03_LV_NO | 2026-09-27T20:25 | 51 | CURRENT | 3.50 | 43.50 | -8 | 62 | 3.5/43.5 (kalshi_implied) | 3.5/43.5 (OK) |
|  |  |  | DATA_ONLY | 3.69 | 40.31 |  |  |  |  |
|  |  |  | HYBRID_30 | 3.56 | 42.54 |  |  |  |  |
| 2026_03_LA_DEN | 2026-09-28T00:20 | 44 | CURRENT | -0.50 | 44.50 | 4 | 56 | -0.5/44.5 (kalshi_implied) | 0.5/43.0 (OK) |
|  |  |  | DATA_ONLY | -0.78 | 46.30 |  |  |  |  |
|  |  |  | HYBRID_30 | -0.58 | 45.04 |  |  |  |  |
| 2026_03_PHI_CHI | 2026-09-29T00:15 | 38 | CURRENT | -3.50 | 42.50 | 20 | 34 | -3.5/42.5 (kalshi_implied) | -3.5/42.5 (OK) |
|  |  |  | DATA_ONLY | 2.91 | 47.35 |  |  |  |  |
|  |  |  | HYBRID_30 | -1.58 | 43.96 |  |  |  |  |

## Game-centre accuracy — latest_pregame (16 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 1 | 8.31 | 12.12 | -1.94 | 10.97 | 12.46 | -2.91 | 0.256 |
| DATA_ONLY | 16 | 1 | 8.89 | 12.21 | -1.45 | 11.67 | 13.65 | -2.08 | 0.251 |
| HYBRID_30 | 16 | 1 | 8.42 | 12.09 | -1.79 | 11.18 | 12.76 | -2.66 | 0.249 |
| market at snapshot | 16 | 1 | 8.31 | 12.12 | -1.94 | 10.97 | 12.46 | -2.91 | - |
| market at close | 16 | 1 | 8.28 | 12.11 | -1.91 | 11.19 | 12.73 | -2.81 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | 0.580 | 0.647 | [-0.689, 1.848] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | 0.697 | 0.707 | [-0.689, 2.083] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | 0.108 | 0.196 | [-0.276, 0.492] | 0.375 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | 0.209 | 0.212 | [-0.207, 0.625] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | -0.471 | 0.459 | [-1.372, 0.429] | 0.750 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -0.488 | 0.495 | [-1.458, 0.482] | 0.438 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | 0.580 | 0.647 | [-0.689, 1.848] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | 0.697 | 0.707 | [-0.689, 2.083] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | 0.108 | 0.196 | [-0.276, 0.492] | 0.375 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | 0.209 | 0.212 | [-0.207, 0.625] | 0.562 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | 0.031 | 0.085 | [-0.135, 0.198] | 0.125 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | -0.219 | 0.177 | [-0.565, 0.127] | 0.312 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | 0.611 | 0.641 | [-0.646, 1.867] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 0.479 | 0.768 | [-1.026, 1.983] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | 0.139 | 0.207 | [-0.267, 0.545] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | -0.010 | 0.306 | [-0.609, 0.590] | 0.562 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 2 | 2 | 12 | 0 | 0.500 | 0.250 | 2.20 |
| DATA_ONLY | total | 16 | 3 | 3 | 10 | 0 | 0.500 | 0.562 | 2.01 |
| HYBRID_30 | margin | 16 | 2 | 2 | 12 | 0 | 0.500 | 0.375 | 0.66 |
| HYBRID_30 | total | 16 | 3 | 3 | 10 | 0 | 0.500 | 0.562 | 0.60 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.24 | 8.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 7 | 11.48 | 10.93 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 4.10 | 2.70 | 0.000 |
| DATA_ONLY | margin | 3-5 | 1 | 7.84 | 3.50 | - |
| DATA_ONLY | margin | >5 | 1 | 17.09 | 23.50 | - |
| DATA_ONLY | total | <=1 | 7 | 11.44 | 11.93 | 0.500 |
| DATA_ONLY | total | 1-2 | 3 | 9.81 | 9.67 | 0.500 |
| DATA_ONLY | total | 2-3 | 3 | 5.19 | 5.83 | 0.500 |
| DATA_ONLY | total | 3-5 | 2 | 17.52 | 13.50 | - |
| DATA_ONLY | total | >5 | 1 | 26.58 | 18.50 | - |
| HYBRID_30 | margin | <=1 | 14 | 7.74 | 7.57 | 0.500 |
| HYBRID_30 | margin | 1-2 | 2 | 13.19 | 13.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 14 | 10.57 | 10.61 | 0.500 |
| HYBRID_30 | total | 1-2 | 1 | 9.96 | 8.50 | - |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Game-centre accuracy — T-24h (6 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 6 | 1 | 8.42 | 11.58 | -1.42 | 11.92 | 13.03 | -8.25 | 0.258 |
| DATA_ONLY | 6 | 1 | 7.89 | 9.29 | -0.76 | 12.53 | 14.00 | -7.72 | 0.198 |
| HYBRID_30 | 6 | 1 | 8.26 | 10.83 | -1.22 | 12.10 | 13.25 | -8.09 | 0.238 |
| market at snapshot | 6 | 1 | 8.42 | 11.58 | -1.42 | 11.92 | 13.03 | -8.25 | - |
| market at close | 6 | 1 | 8.08 | 11.17 | -1.08 | 12.08 | 13.13 | -8.08 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 6 | margin | -0.525 | 1.484 | [-3.433, 2.384] | 0.333 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 6 | total | 0.613 | 1.369 | [-2.071, 3.296] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 6 | margin | -0.157 | 0.445 | [-1.030, 0.715] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 6 | total | 0.184 | 0.411 | [-0.621, 0.989] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 6 | margin | 0.367 | 1.039 | [-1.669, 2.403] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 6 | total | -0.429 | 0.958 | [-2.307, 1.449] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 6 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 6 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 6 | margin | -0.525 | 1.484 | [-3.433, 2.384] | 0.333 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 6 | total | 0.613 | 1.369 | [-2.071, 3.296] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 6 | margin | -0.157 | 0.445 | [-1.030, 0.715] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 6 | total | 0.184 | 0.411 | [-0.621, 0.989] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 6 | margin | 0.333 | 0.211 | [-0.080, 0.747] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 6 | total | -0.167 | 0.167 | [-0.493, 0.160] | 0.167 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 6 | margin | -0.192 | 1.372 | [-2.880, 2.497] | 0.333 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 6 | total | 0.446 | 1.252 | [-2.007, 2.899] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 6 | margin | 0.176 | 0.365 | [-0.540, 0.891] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 6 | total | 0.017 | 0.310 | [-0.590, 0.624] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 6 | 1 | 1 | 4 | 0 | 0.500 | 0.333 | 2.36 |
| DATA_ONLY | total | 6 | 1 | 0 | 5 | 0 | 1.000 | 0.500 | 2.69 |
| HYBRID_30 | margin | 6 | 1 | 1 | 4 | 0 | 0.500 | 0.333 | 0.71 |
| HYBRID_30 | total | 6 | 1 | 0 | 5 | 0 | 1.000 | 0.500 | 0.81 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.51 | 8.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 2 | 4.85 | 4.75 | - |
| DATA_ONLY | margin | 2-3 | 1 | 3.48 | 0.50 | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 1 | 17.14 | 24.50 | 1.000 |
| DATA_ONLY | total | <=1 | 1 | 16.57 | 17.50 | - |
| DATA_ONLY | total | 1-2 | 1 | 12.60 | 11.50 | - |
| DATA_ONLY | total | 2-3 | 1 | 1.28 | 3.50 | - |
| DATA_ONLY | total | 3-5 | 2 | 15.80 | 15.75 | - |
| DATA_ONLY | total | >5 | 1 | 13.14 | 7.50 | 1.000 |
| HYBRID_30 | margin | <=1 | 5 | 5.45 | 5.20 | 0.000 |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 1 | 22.29 | 24.50 | 1.000 |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 5 | 12.68 | 12.80 | - |
| HYBRID_30 | total | 1-2 | 1 | 9.19 | 7.50 | 1.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 6}; DATA_ONLY quality states: {'OK': 6}; close centre status: {'OK': 6}.

## Game-centre accuracy — T-6h (16 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 1 | 8.44 | 12.18 | -2.06 | 11.00 | 12.53 | -3.00 | 0.263 |
| DATA_ONLY | 16 | 1 | 8.93 | 12.22 | -1.48 | 11.68 | 13.66 | -2.09 | 0.255 |
| HYBRID_30 | 16 | 1 | 8.58 | 12.13 | -1.89 | 11.20 | 12.80 | -2.73 | 0.258 |
| market at snapshot | 16 | 1 | 8.44 | 12.18 | -2.06 | 11.00 | 12.53 | -3.00 | - |
| market at close | 16 | 1 | 8.28 | 12.11 | -1.91 | 11.19 | 12.73 | -2.81 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | 0.489 | 0.670 | [-0.823, 1.802] | 0.312 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | 0.679 | 0.753 | [-0.796, 2.155] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | 0.147 | 0.201 | [-0.247, 0.540] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | 0.204 | 0.226 | [-0.239, 0.646] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | -0.343 | 0.469 | [-1.261, 0.576] | 0.688 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -0.476 | 0.527 | [-1.508, 0.557] | 0.438 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | 0.489 | 0.670 | [-0.823, 1.802] | 0.312 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | 0.679 | 0.753 | [-0.796, 2.155] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | 0.147 | 0.201 | [-0.247, 0.540] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | 0.204 | 0.226 | [-0.239, 0.646] | 0.562 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | 0.156 | 0.149 | [-0.137, 0.449] | 0.125 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | -0.188 | 0.218 | [-0.615, 0.240] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | 0.646 | 0.644 | [-0.617, 1.909] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 0.492 | 0.763 | [-1.004, 1.988] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | 0.303 | 0.215 | [-0.118, 0.724] | 0.188 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | 0.016 | 0.299 | [-0.569, 0.601] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 3 | 2 | 11 | 0 | 0.600 | 0.312 | 2.13 |
| DATA_ONLY | total | 16 | 4 | 2 | 10 | 0 | 0.667 | 0.562 | 2.15 |
| HYBRID_30 | margin | 16 | 3 | 2 | 11 | 0 | 0.600 | 0.312 | 0.64 |
| HYBRID_30 | total | 16 | 4 | 2 | 10 | 0 | 0.667 | 0.562 | 0.65 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 5.87 | 5.83 | 0.500 |
| DATA_ONLY | margin | 1-2 | 7 | 11.71 | 10.93 | 0.500 |
| DATA_ONLY | margin | 2-3 | 3 | 5.04 | 2.50 | - |
| DATA_ONLY | margin | 3-5 | 2 | 5.52 | 5.00 | 1.000 |
| DATA_ONLY | margin | >5 | 1 | 17.09 | 23.50 | - |
| DATA_ONLY | total | <=1 | 5 | 11.06 | 11.50 | 1.000 |
| DATA_ONLY | total | 1-2 | 5 | 10.88 | 11.40 | 0.667 |
| DATA_ONLY | total | 2-3 | 3 | 5.19 | 5.83 | 0.000 |
| DATA_ONLY | total | 3-5 | 1 | 21.69 | 18.50 | - |
| DATA_ONLY | total | >5 | 2 | 19.96 | 12.75 | 1.000 |
| HYBRID_30 | margin | <=1 | 14 | 7.93 | 7.71 | 0.600 |
| HYBRID_30 | margin | 1-2 | 2 | 13.19 | 13.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 14 | 10.67 | 10.75 | 0.600 |
| HYBRID_30 | total | 1-2 | 1 | 8.91 | 7.00 | 1.000 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Game-centre accuracy — T-90m (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 7.07 | 10.48 | -3.80 | 11.43 | 12.95 | -2.50 | 0.241 |
| DATA_ONLY | 15 | 1 | 7.61 | 10.31 | -3.42 | 12.04 | 14.01 | -1.81 | 0.229 |
| HYBRID_30 | 15 | 1 | 7.21 | 10.36 | -3.69 | 11.61 | 13.21 | -2.29 | 0.234 |
| market at snapshot | 15 | 1 | 7.07 | 10.48 | -3.80 | 11.43 | 12.95 | -2.50 | - |
| market at close | 15 | 1 | 7.07 | 10.47 | -3.80 | 11.47 | 13.02 | -2.53 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | 0.543 | 0.693 | [-0.815, 1.900] | 0.267 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 0.604 | 0.725 | [-0.816, 2.025] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | 0.139 | 0.210 | [-0.273, 0.551] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.181 | 0.217 | [-0.245, 0.608] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | -0.403 | 0.484 | [-1.352, 0.546] | 0.733 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -0.423 | 0.507 | [-1.418, 0.572] | 0.467 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | 0.543 | 0.693 | [-0.815, 1.900] | 0.267 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 0.604 | 0.725 | [-0.816, 2.025] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | 0.139 | 0.210 | [-0.273, 0.551] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.181 | 0.217 | [-0.245, 0.608] | 0.533 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | 0.000 | 0.109 | [-0.214, 0.214] | 0.133 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | -0.033 | 0.186 | [-0.397, 0.330] | 0.267 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | 0.543 | 0.681 | [-0.793, 1.878] | 0.267 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 0.571 | 0.815 | [-1.026, 2.167] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | 0.139 | 0.215 | [-0.282, 0.561] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | 0.148 | 0.336 | [-0.510, 0.806] | 0.467 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 2 | 2 | 11 | 0 | 0.500 | 0.267 | 2.20 |
| DATA_ONLY | total | 15 | 3 | 4 | 8 | 0 | 0.429 | 0.533 | 2.09 |
| HYBRID_30 | margin | 15 | 2 | 2 | 11 | 0 | 0.500 | 0.333 | 0.66 |
| HYBRID_30 | total | 15 | 3 | 4 | 8 | 0 | 0.429 | 0.533 | 0.63 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.24 | 8.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 6 | 8.70 | 8.33 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 4.10 | 2.60 | 0.000 |
| DATA_ONLY | margin | 3-5 | 1 | 7.84 | 3.50 | - |
| DATA_ONLY | margin | >5 | 1 | 17.09 | 23.50 | - |
| DATA_ONLY | total | <=1 | 6 | 12.33 | 12.83 | 0.667 |
| DATA_ONLY | total | 1-2 | 3 | 9.81 | 9.67 | 0.500 |
| DATA_ONLY | total | 2-3 | 2 | 4.33 | 4.25 | - |
| DATA_ONLY | total | 3-5 | 3 | 13.98 | 12.50 | 0.000 |
| DATA_ONLY | total | >5 | 1 | 26.58 | 19.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 13 | 6.29 | 6.08 | 0.500 |
| HYBRID_30 | margin | 1-2 | 2 | 13.19 | 13.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 12 | 11.10 | 11.08 | 0.600 |
| HYBRID_30 | total | 1-2 | 2 | 9.69 | 9.50 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Game-centre accuracy — T-30m (16 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 1 | 8.31 | 12.12 | -1.94 | 10.97 | 12.46 | -2.91 | 0.255 |
| DATA_ONLY | 16 | 1 | 8.89 | 12.21 | -1.45 | 11.67 | 13.65 | -2.08 | 0.251 |
| HYBRID_30 | 16 | 1 | 8.42 | 12.09 | -1.79 | 11.18 | 12.76 | -2.66 | 0.249 |
| market at snapshot | 16 | 1 | 8.31 | 12.12 | -1.94 | 10.97 | 12.46 | -2.91 | - |
| market at close | 16 | 1 | 8.28 | 12.11 | -1.91 | 11.19 | 12.73 | -2.81 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | 0.580 | 0.647 | [-0.689, 1.848] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | 0.697 | 0.707 | [-0.689, 2.083] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | 0.108 | 0.196 | [-0.276, 0.492] | 0.375 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | 0.209 | 0.212 | [-0.207, 0.625] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | -0.471 | 0.459 | [-1.372, 0.429] | 0.750 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -0.488 | 0.495 | [-1.458, 0.482] | 0.438 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | 0.580 | 0.647 | [-0.689, 1.848] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | 0.697 | 0.707 | [-0.689, 2.083] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | 0.108 | 0.196 | [-0.276, 0.492] | 0.375 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | 0.209 | 0.212 | [-0.207, 0.625] | 0.562 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | 0.031 | 0.085 | [-0.135, 0.198] | 0.125 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | -0.219 | 0.177 | [-0.565, 0.127] | 0.312 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | 0.611 | 0.641 | [-0.646, 1.867] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 0.479 | 0.768 | [-1.026, 1.983] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | 0.139 | 0.207 | [-0.267, 0.545] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | -0.010 | 0.306 | [-0.609, 0.590] | 0.562 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 2 | 2 | 12 | 0 | 0.500 | 0.250 | 2.20 |
| DATA_ONLY | total | 16 | 3 | 3 | 10 | 0 | 0.500 | 0.562 | 2.01 |
| HYBRID_30 | margin | 16 | 2 | 2 | 12 | 0 | 0.500 | 0.375 | 0.66 |
| HYBRID_30 | total | 16 | 3 | 3 | 10 | 0 | 0.500 | 0.562 | 0.60 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.24 | 8.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 7 | 11.48 | 10.93 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 4.10 | 2.70 | 0.000 |
| DATA_ONLY | margin | 3-5 | 1 | 7.84 | 3.50 | - |
| DATA_ONLY | margin | >5 | 1 | 17.09 | 23.50 | - |
| DATA_ONLY | total | <=1 | 7 | 11.44 | 11.93 | 0.500 |
| DATA_ONLY | total | 1-2 | 3 | 9.81 | 9.67 | 0.500 |
| DATA_ONLY | total | 2-3 | 3 | 5.19 | 5.83 | 0.500 |
| DATA_ONLY | total | 3-5 | 2 | 17.52 | 13.50 | - |
| DATA_ONLY | total | >5 | 1 | 26.58 | 18.50 | - |
| HYBRID_30 | margin | <=1 | 14 | 7.74 | 7.57 | 0.500 |
| HYBRID_30 | margin | 1-2 | 2 | 13.19 | 13.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 14 | 10.57 | 10.61 | 0.500 |
| HYBRID_30 | total | 1-2 | 1 | 9.96 | 8.50 | - |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Contract pricing — latest_pregame (1251 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1251 | 0.1524 | 0.4630 | 0.411 | 0.416 | 1251 | 0.1524 | 0.1535 | 0.1584 |
| DATA_ONLY | 1251 | 0.1591 | 0.4814 | 0.419 | 0.416 | 1251 | 0.1591 | 0.1535 | 0.1584 |
| HYBRID_30 | 1251 | 0.1552 | 0.4694 | 0.411 | 0.416 | 1251 | 0.1552 | 0.1535 | 0.1584 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1251 | 16 | 0.00671 | [-0.00609, 0.02089] | 0.00671 | [-0.00609, 0.02089] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1251 | 16 | 0.00275 | [-0.00083, 0.00628] | 0.00275 | [-0.00083, 0.00628] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1251 | 16 | -0.00396 | [-0.01566, 0.00588] | -0.00396 | [-0.01566, 0.00588] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1251 | 16 | - | - | -0.00108 | [-0.00307, 0.00071] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1213 | 16 | - | - | -0.00129 | [-0.00375, 0.00101] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1251 | 16 | - | - | 0.00563 | [-0.00766, 0.02007] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1213 | 16 | - | - | 0.00562 | [-0.00772, 0.02073] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1251 | 16 | - | - | 0.00167 | [-0.00238, 0.00593] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1213 | 16 | - | - | 0.00155 | [-0.00278, 0.00611] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 414, 'TEAM_TOTAL': 437, 'TOTAL': 304}; settlement: {'SETTLED': 1251}; close: {'OK': 1213, 'OK_STALE': 38}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 204 / 0.056 / 0.044 | 199 / 0.053 / 0.050 | 193 / 0.052 / 0.047 |
| 0.10-0.20 | 196 / 0.146 / 0.163 | 192 / 0.146 / 0.156 | 206 / 0.146 / 0.146 |
| 0.20-0.30 | 140 / 0.248 / 0.221 | 149 / 0.252 / 0.221 | 146 / 0.252 / 0.253 |
| 0.30-0.40 | 143 / 0.350 / 0.357 | 122 / 0.350 / 0.336 | 124 / 0.349 / 0.339 |
| 0.40-0.50 | 122 / 0.453 / 0.492 | 123 / 0.447 / 0.512 | 146 / 0.449 / 0.521 |
| 0.50-0.60 | 120 / 0.545 / 0.525 | 111 / 0.552 / 0.577 | 107 / 0.550 / 0.495 |
| 0.60-0.70 | 78 / 0.651 / 0.628 | 94 / 0.647 / 0.596 | 78 / 0.646 / 0.628 |
| 0.70-0.80 | 62 / 0.754 / 0.806 | 69 / 0.750 / 0.725 | 70 / 0.749 / 0.771 |
| 0.80-0.90 | 63 / 0.847 / 0.905 | 68 / 0.850 / 0.824 | 64 / 0.854 / 0.906 |
| 0.90-1.00 | 123 / 0.953 / 0.959 | 124 / 0.955 / 0.944 | 117 / 0.955 / 0.957 |

## Contract pricing — T-24h (467 contracts, 6 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 467 | 0.1614 | 0.4848 | 0.416 | 0.486 | 467 | 0.1614 | 0.1607 | 0.1634 |
| DATA_ONLY | 467 | 0.1514 | 0.4558 | 0.422 | 0.486 | 467 | 0.1514 | 0.1607 | 0.1634 |
| HYBRID_30 | 467 | 0.1588 | 0.4741 | 0.415 | 0.486 | 467 | 0.1588 | 0.1607 | 0.1634 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 467 | 6 | -0.00997 | [-0.03588, 0.01118] | -0.00997 | [-0.03588, 0.01118] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 467 | 6 | -0.00262 | [-0.00895, 0.00402] | -0.00262 | [-0.00895, 0.00402] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 467 | 6 | 0.00734 | [-0.00966, 0.02907] | 0.00734 | [-0.00966, 0.02907] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 467 | 6 | - | - | 0.00064 | [-0.00161, 0.00304] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 458 | 6 | - | - | 0.00108 | [-0.00345, 0.00569] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 467 | 6 | - | - | -0.00932 | [-0.03347, 0.01090] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 458 | 6 | - | - | -0.00911 | [-0.03127, 0.00847] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 467 | 6 | - | - | -0.00198 | [-0.00837, 0.00512] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 458 | 6 | - | - | -0.00158 | [-0.00705, 0.00436] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 24, 'GAME_WINNER': 12, 'SPREAD': 153, 'TEAM_TOTAL': 164, 'TOTAL': 114}; settlement: {'SETTLED': 467}; close: {'OK': 458, 'OK_STALE': 9}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 70 / 0.058 / 0.029 | 70 / 0.053 / 0.029 | 69 / 0.052 / 0.029 |
| 0.10-0.20 | 72 / 0.147 / 0.194 | 76 / 0.149 / 0.158 | 74 / 0.144 / 0.149 |
| 0.20-0.30 | 54 / 0.248 / 0.352 | 55 / 0.257 / 0.327 | 58 / 0.249 / 0.379 |
| 0.30-0.40 | 54 / 0.347 / 0.444 | 47 / 0.354 / 0.426 | 46 / 0.343 / 0.522 |
| 0.40-0.50 | 49 / 0.450 / 0.571 | 46 / 0.451 / 0.652 | 59 / 0.451 / 0.576 |
| 0.50-0.60 | 44 / 0.543 / 0.659 | 45 / 0.553 / 0.711 | 36 / 0.549 / 0.583 |
| 0.60-0.70 | 33 / 0.651 / 0.727 | 29 / 0.649 / 0.690 | 28 / 0.640 / 0.750 |
| 0.70-0.80 | 20 / 0.753 / 0.950 | 23 / 0.751 / 0.913 | 25 / 0.748 / 0.920 |
| 0.80-0.90 | 24 / 0.849 / 0.958 | 27 / 0.845 / 0.926 | 24 / 0.855 / 0.958 |
| 0.90-1.00 | 47 / 0.953 / 0.957 | 49 / 0.956 / 0.959 | 48 / 0.957 / 0.958 |

## Contract pricing — T-6h (1251 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1251 | 0.1543 | 0.4667 | 0.410 | 0.416 | 1251 | 0.1543 | 0.1545 | 0.1584 |
| DATA_ONLY | 1251 | 0.1598 | 0.4823 | 0.419 | 0.416 | 1251 | 0.1598 | 0.1545 | 0.1584 |
| HYBRID_30 | 1251 | 0.1556 | 0.4706 | 0.409 | 0.416 | 1251 | 0.1556 | 0.1545 | 0.1584 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1251 | 16 | 0.00545 | [-0.00760, 0.01972] | 0.00545 | [-0.00760, 0.01972] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1251 | 16 | 0.00132 | [-0.00284, 0.00529] | 0.00132 | [-0.00284, 0.00529] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1251 | 16 | -0.00413 | [-0.01571, 0.00526] | -0.00413 | [-0.01571, 0.00526] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1251 | 16 | - | - | -0.00016 | [-0.00171, 0.00156] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1213 | 16 | - | - | 0.00065 | [-0.00132, 0.00259] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1251 | 16 | - | - | 0.00529 | [-0.00834, 0.01999] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1213 | 16 | - | - | 0.00626 | [-0.00687, 0.02111] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1251 | 16 | - | - | 0.00116 | [-0.00318, 0.00545] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1213 | 16 | - | - | 0.00202 | [-0.00204, 0.00599] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 414, 'TEAM_TOTAL': 437, 'TOTAL': 304}; settlement: {'SETTLED': 1251}; close: {'OK': 1213, 'OK_STALE': 38}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 204 / 0.056 / 0.059 | 202 / 0.053 / 0.054 | 198 / 0.053 / 0.056 |
| 0.10-0.20 | 196 / 0.145 / 0.148 | 191 / 0.147 / 0.152 | 198 / 0.145 / 0.141 |
| 0.20-0.30 | 147 / 0.249 / 0.252 | 146 / 0.251 / 0.219 | 155 / 0.251 / 0.252 |
| 0.30-0.40 | 135 / 0.351 / 0.348 | 124 / 0.350 / 0.371 | 122 / 0.350 / 0.385 |
| 0.40-0.50 | 123 / 0.452 / 0.488 | 120 / 0.446 / 0.492 | 144 / 0.450 / 0.493 |
| 0.50-0.60 | 119 / 0.544 / 0.521 | 112 / 0.549 / 0.580 | 106 / 0.549 / 0.500 |
| 0.60-0.70 | 82 / 0.651 / 0.610 | 95 / 0.647 / 0.579 | 78 / 0.646 / 0.603 |
| 0.70-0.80 | 59 / 0.756 / 0.814 | 68 / 0.751 / 0.721 | 68 / 0.748 / 0.779 |
| 0.80-0.90 | 65 / 0.850 / 0.908 | 68 / 0.849 / 0.838 | 64 / 0.853 / 0.906 |
| 0.90-1.00 | 121 / 0.955 / 0.959 | 125 / 0.956 / 0.936 | 118 / 0.955 / 0.958 |

## Contract pricing — T-90m (1171 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1171 | 0.1475 | 0.4508 | 0.414 | 0.411 | 1171 | 0.1475 | 0.1470 | 0.1516 |
| DATA_ONLY | 1171 | 0.1502 | 0.4575 | 0.421 | 0.411 | 1171 | 0.1502 | 0.1470 | 0.1516 |
| HYBRID_30 | 1171 | 0.1497 | 0.4545 | 0.413 | 0.411 | 1171 | 0.1497 | 0.1470 | 0.1516 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1171 | 15 | 0.00271 | [-0.01040, 0.01510] | 0.00271 | [-0.01040, 0.01510] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1171 | 15 | 0.00221 | [-0.00192, 0.00600] | 0.00221 | [-0.00192, 0.00600] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1171 | 15 | -0.00050 | [-0.01045, 0.00942] | -0.00050 | [-0.01045, 0.00942] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1171 | 15 | - | - | 0.00051 | [-0.00229, 0.00310] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1134 | 15 | - | - | 0.00056 | [-0.00253, 0.00350] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1171 | 15 | - | - | 0.00322 | [-0.00993, 0.01672] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1134 | 15 | - | - | 0.00334 | [-0.01056, 0.01749] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1171 | 15 | - | - | 0.00272 | [-0.00153, 0.00716] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1134 | 15 | - | - | 0.00283 | [-0.00176, 0.00759] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 387, 'TEAM_TOTAL': 409, 'TOTAL': 285}; settlement: {'SETTLED': 1171}; close: {'OK': 1134, 'OK_STALE': 37}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 184 / 0.056 / 0.033 | 184 / 0.053 / 0.033 | 176 / 0.052 / 0.034 |
| 0.10-0.20 | 184 / 0.145 / 0.136 | 177 / 0.147 / 0.124 | 195 / 0.145 / 0.123 |
| 0.20-0.30 | 131 / 0.248 / 0.221 | 140 / 0.252 / 0.214 | 138 / 0.253 / 0.246 |
| 0.30-0.40 | 128 / 0.348 / 0.328 | 114 / 0.351 / 0.316 | 111 / 0.350 / 0.369 |
| 0.40-0.50 | 116 / 0.450 / 0.474 | 115 / 0.447 / 0.496 | 141 / 0.449 / 0.489 |
| 0.50-0.60 | 120 / 0.544 / 0.550 | 104 / 0.550 / 0.596 | 99 / 0.550 / 0.465 |
| 0.60-0.70 | 71 / 0.651 / 0.606 | 90 / 0.645 / 0.611 | 73 / 0.646 / 0.644 |
| 0.70-0.80 | 60 / 0.753 / 0.800 | 65 / 0.749 / 0.738 | 63 / 0.748 / 0.778 |
| 0.80-0.90 | 60 / 0.849 / 0.933 | 65 / 0.849 / 0.846 | 61 / 0.852 / 0.902 |
| 0.90-1.00 | 117 / 0.954 / 0.949 | 117 / 0.955 / 0.940 | 114 / 0.955 / 0.965 |

## Contract pricing — T-30m (1251 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1251 | 0.1524 | 0.4628 | 0.411 | 0.416 | 1251 | 0.1524 | 0.1535 | 0.1584 |
| DATA_ONLY | 1251 | 0.1591 | 0.4812 | 0.419 | 0.416 | 1251 | 0.1591 | 0.1535 | 0.1584 |
| HYBRID_30 | 1251 | 0.1552 | 0.4694 | 0.411 | 0.416 | 1251 | 0.1552 | 0.1535 | 0.1584 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1251 | 16 | 0.00668 | [-0.00612, 0.02084] | 0.00668 | [-0.00612, 0.02084] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1251 | 16 | 0.00277 | [-0.00081, 0.00631] | 0.00277 | [-0.00081, 0.00631] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1251 | 16 | -0.00391 | [-0.01566, 0.00593] | -0.00391 | [-0.01566, 0.00593] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1251 | 16 | - | - | -0.00112 | [-0.00311, 0.00066] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1213 | 16 | - | - | -0.00133 | [-0.00376, 0.00095] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1251 | 16 | - | - | 0.00556 | [-0.00766, 0.01996] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1213 | 16 | - | - | 0.00555 | [-0.00775, 0.02053] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1251 | 16 | - | - | 0.00165 | [-0.00239, 0.00589] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1213 | 16 | - | - | 0.00153 | [-0.00279, 0.00608] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 414, 'TEAM_TOTAL': 437, 'TOTAL': 304}; settlement: {'SETTLED': 1251}; close: {'OK': 1213, 'OK_STALE': 38}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 203 / 0.056 / 0.044 | 199 / 0.053 / 0.050 | 193 / 0.052 / 0.047 |
| 0.10-0.20 | 196 / 0.146 / 0.158 | 192 / 0.146 / 0.156 | 206 / 0.145 / 0.146 |
| 0.20-0.30 | 141 / 0.247 / 0.227 | 149 / 0.252 / 0.221 | 147 / 0.252 / 0.252 |
| 0.30-0.40 | 142 / 0.350 / 0.359 | 123 / 0.350 / 0.333 | 123 / 0.349 / 0.341 |
| 0.40-0.50 | 123 / 0.452 / 0.488 | 122 / 0.447 / 0.516 | 146 / 0.449 / 0.521 |
| 0.50-0.60 | 120 / 0.545 / 0.525 | 111 / 0.551 / 0.577 | 107 / 0.550 / 0.495 |
| 0.60-0.70 | 78 / 0.650 / 0.628 | 94 / 0.647 / 0.596 | 78 / 0.646 / 0.628 |
| 0.70-0.80 | 62 / 0.754 / 0.806 | 69 / 0.750 / 0.725 | 70 / 0.749 / 0.771 |
| 0.80-0.90 | 63 / 0.847 / 0.905 | 68 / 0.850 / 0.824 | 64 / 0.854 / 0.906 |
| 0.90-1.00 | 123 / 0.953 / 0.959 | 124 / 0.955 / 0.944 | 117 / 0.955 / 0.957 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 6 | 2 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.500 | 0.500 | 0.25 |
| T-24h | DATA_ONLY | total | 6 | 1 | 1 | 0 | 4 | 0 | 1.000 [0.207, 1.000] | 0.400 | 0.400 | 0.20 |
| T-24h | HYBRID_30 (derived) | margin | 6 | 5 | 1 | 0 | 0 | 0 | 1.000 [0.207, 1.000] | 1.000 | 1.000 | 1.00 |
| T-24h | HYBRID_30 (derived) | total | 6 | 5 | 1 | 0 | 0 | 0 | 1.000 [0.207, 1.000] | 0.000 | 0.000 | 1.00 |
| T-6h | DATA_ONLY | margin | 16 | 3 | 2 | 1 | 10 | 0 | 0.667 [0.208, 0.939] | 0.308 | 0.308 | 0.00 |
| T-6h | DATA_ONLY | total | 16 | 5 | 3 | 2 | 6 | 0 | 0.600 [0.231, 0.882] | 0.455 | 0.455 | -0.05 |
| T-6h | HYBRID_30 (derived) | margin | 16 | 14 | 0 | 0 | 2 | 0 | - - | 0.500 | 0.500 | 0.00 |
| T-6h | HYBRID_30 (derived) | total | 16 | 14 | 1 | 0 | 1 | 0 | 1.000 [0.207, 1.000] | 0.000 | 0.000 | 0.75 |
| T-90m | DATA_ONLY | margin | 15 | 2 | 2 | 1 | 10 | 0 | 0.667 [0.208, 0.939] | 0.308 | 0.308 | 0.00 |
| T-90m | DATA_ONLY | total | 15 | 6 | 1 | 3 | 5 | 0 | 0.250 [0.046, 0.699] | 0.333 | 0.333 | -0.28 |
| T-90m | HYBRID_30 (derived) | margin | 15 | 13 | 0 | 0 | 2 | 0 | - - | 0.500 | 0.500 | 0.00 |
| T-90m | HYBRID_30 (derived) | total | 15 | 12 | 0 | 2 | 1 | 0 | 0.000 [0.000, 0.658] | 0.333 | 0.333 | -0.50 |
| T-30m | DATA_ONLY | margin | 16 | 2 | 2 | 1 | 11 | 0 | 0.667 [0.208, 0.939] | 0.286 | 0.286 | 0.04 |
| T-30m | DATA_ONLY | total | 16 | 7 | 2 | 2 | 5 | 0 | 0.500 [0.150, 0.850] | 0.333 | 0.333 | -0.22 |
| T-30m | HYBRID_30 (derived) | margin | 16 | 14 | 0 | 0 | 2 | 0 | - - | 0.500 | 0.500 | 0.00 |
| T-30m | HYBRID_30 (derived) | total | 16 | 14 | 0 | 0 | 2 | 0 | - - | 0.000 | 0.000 | 0.00 |
| latest_pregame | DATA_ONLY | margin | 16 | 2 | 2 | 1 | 11 | 0 | 0.667 [0.208, 0.939] | 0.286 | 0.286 | 0.04 |
| latest_pregame | DATA_ONLY | total | 16 | 7 | 2 | 2 | 5 | 0 | 0.500 [0.150, 0.850] | 0.333 | 0.333 | -0.22 |
| latest_pregame | HYBRID_30 (derived) | margin | 16 | 14 | 0 | 0 | 2 | 0 | - - | 0.500 | 0.500 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | total | 16 | 14 | 0 | 0 | 2 | 0 | - - | 0.000 | 0.000 | 0.00 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 2 | 0 | 1 | 1 | 0 | 0.000 |
| margin | 1-2 | 7 | 2 | 0 | 5 | 0 | 1.000 |
| margin | 2-3 | 5 | 0 | 1 | 4 | 0 | 0.000 |
| margin | 3-5 | 1 | 0 | 0 | 1 | 0 | - |
| margin | >5 | 1 | 0 | 0 | 1 | 0 | - |
| total | <=1 | 7 | 1 | 1 | 5 | 0 | 0.500 |
| total | 1-2 | 3 | 1 | 1 | 1 | 0 | 0.500 |
| total | 2-3 | 3 | 1 | 1 | 1 | 0 | 0.500 |
| total | 3-5 | 2 | 0 | 0 | 2 | 0 | - |
| total | >5 | 1 | 0 | 0 | 1 | 0 | - |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

999 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_03_CAR_CLE | Raheim Sanders | receiving_yards | 1.0 | 0–11 | 34 | 45.87 | 0.99 | 1.2 | 5 | 0.87 | 6.80 | EXPECTED_ACTIVE | True | 0.123 | EFFICIENCY_MISS |
| 2026_03_NYJ_DET | Kenyon Sadiq | receiving_yards | 3.3 | 0–35 | 105 | 35.41 | 0.99 | 1.1 | 8 | 3.05 | 13.12 | EXPECTED_ACTIVE | True | 0.603 | OPPORTUNITY_MISS |
| 2026_03_ARI_SF | Jeremiyah Love | receiving_yards | 1.0 | 0–11 | 19 | 25.63 | 0.98 | 0.9 | 5 | 1.07 | 3.80 | EXPECTED_ACTIVE | True | 0.472 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.0 | 3 | 1.04 | 2.33 | EXPECTED_ACTIVE | True | -0.193 | TEAM_VOLUME_MISS |
| 2026_03_NYJ_DET | Kenyon Sadiq | receptions | 0.7 | 0–5 | 7 | 9.44 | 0.97 | 1.1 | 8 | 0.68 | 0.88 | EXPECTED_ACTIVE | True | 0.612 | OPPORTUNITY_MISS |
| 2026_03_SEA_WAS | Jadarian Price | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 0.9 | 3 | 1.09 | 2.33 | EXPECTED_ACTIVE | True | -0.307 | TEAM_VOLUME_MISS |
| 2026_03_NE_JAX | Bhayshul Tuten | receiving_yards | 2.4 | 0–25 | 17 | 7.64 | 0.88 | 1.2 | 2 | 1.95 | 8.50 | EXPECTED_ACTIVE | True | 0.382 | EFFICIENCY_MISS |
| 2026_03_ARI_SF | Jeremiyah Love | receptions | 0.7 | 0–5 | 5 | 6.75 | 0.95 | 0.9 | 5 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.563 | TEAM_VOLUME_MISS |
| 2026_03_LA_DEN | Kyren Williams | receiving_yards | 11.1 | 0–48 | 70 | 6.30 | 0.98 | 1.7 | 7 | 6.37 | 10.00 | EXPECTED_ACTIVE | True | 0.169 | TEAM_VOLUME_MISS |
| 2026_03_ARI_SF | Jeremiyah Love | rushing_yards | 13.8 | 0–55 | 90 | 5.96 | 0.99 | 3.9 | 21 | 3.53 | 4.29 | EXPECTED_ACTIVE | True | 0.568 | OPPORTUNITY_MISS |
| 2026_03_NYJ_DET | Sione Vaki | rushing_yards | 8.7 | 0–36 | 26 | 5.85 | 0.88 | 3.1 | 6 | 2.81 | 4.33 | EXPECTED_ACTIVE | True | 0.306 | OPPORTUNITY_MISS |
| 2026_03_CAR_CLE | Raheim Sanders | receptions | 0.8 | 0–5 | 4 | 5.40 | 0.90 | 1.2 | 5 | 0.72 | 0.80 | EXPECTED_ACTIVE | True | 0.208 | OPPORTUNITY_MISS |
| 2026_03_CAR_CLE | Deshaun Watson | carries | 2.4 | 0–18 | 11 | 4.95 | 0.86 | 2.4 | 11 | - | - | EXPECTED_ACTIVE | True | 0.577 | TEAM_VOLUME_MISS |
| 2026_03_HOU_IND | Tyler Warren | receptions | 2.2 | 0–6 | 9 | 4.72 | 0.99 | 3.4 | 10 | 0.66 | 0.90 | EXPECTED_ACTIVE | True | 0.439 | OPPORTUNITY_MISS |
| 2026_03_NYJ_DET | Kenyon Sadiq | touchdowns | 0.0 | -–- | 1 | 4.69 | - | 2.7 | 8 | - | - | EXPECTED_ACTIVE | True | 0.142 | OPPORTUNITY_MISS |
| 2026_03_ARI_SF | Tyler Allgeier | receiving_yards | 2.5 | 0–27 | 10 | 4.50 | 0.81 | 1.3 | 4 | 1.98 | 2.50 | EXPECTED_ACTIVE | True | -0.169 | TEAM_VOLUME_MISS |
| 2026_03_MIN_TB | Myles Price | touchdowns | 0.0 | -–- | 1 | 4.43 | - | 2.2 | 0 | - | - | EXPECTED_ACTIVE | True | 0.004 | OPPORTUNITY_MISS |
| 2026_03_NYJ_DET | Jeremy Ruckert | receiving_yards | 8.9 | 0–39 | 39 | 4.38 | 0.95 | 1.6 | 5 | 5.54 | 7.80 | EXPECTED_ACTIVE | True | 0.124 | OPPORTUNITY_MISS |
| 2026_03_LV_NO | Cody White | touchdowns | 0.1 | -–- | 1 | 4.22 | - | 2.5 | 3 | - | - | EXPECTED_ACTIVE | True | -0.007 | UNEXPLAINED_VARIANCE |
| 2026_03_HOU_IND | Foster Moreau | touchdowns | 0.1 | -–- | 1 | 4.12 | - | 1.9 | 4 | - | - | EXPECTED_ACTIVE | True | 0.020 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Drake London | receiving_yards | 52.7 | 4–123 | 194 | 4.10 | 0.99 | 5.9 | 10 | 8.96 | 19.40 | EXPECTED_ACTIVE | True | 0.190 | EFFICIENCY_MISS |
| 2026_03_SEA_WAS | Eric Saubert | touchdowns | 0.1 | -–- | 1 | 4.06 | - | 1.7 | 2 | - | - | EXPECTED_ACTIVE | True | -0.001 | UNEXPLAINED_VARIANCE |
| 2026_03_ARI_SF | Jeremiyah Love | carries | 3.9 | 0–18 | 21 | 4.05 | 0.96 | 3.9 | 21 | - | - | EXPECTED_ACTIVE | True | 0.539 | OPPORTUNITY_MISS |
| 2026_03_LV_NO | Juwan Johnson | receptions | 2.2 | 0–6 | 8 | 4.05 | 0.98 | 2.9 | 8 | 0.77 | 1.00 | EXPECTED_ACTIVE | True | 0.208 | OPPORTUNITY_MISS |
| 2026_03_SEA_WAS | Sam Darnold | passing_tds | 1.5 | 0–4 | 4 | 4.05 | 0.95 | 32.9 | 45 | 0.05 | 0.09 | EXPECTED_ACTIVE | True | 0.047 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Matthew Golden | receiving_yards | 24.0 | 0–67 | 100 | 3.95 | 0.99 | 2.4 | 12 | 10.15 | 8.33 | EXPECTED_ACTIVE | True | 0.435 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Bijan Robinson | rushing_yards | 63.1 | 14–128 | 194 | 3.90 | 0.99 | 12.2 | 29 | 5.16 | 6.69 | EXPECTED_ACTIVE | True | 0.200 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Austin Hooper | touchdowns | 0.1 | -–- | 1 | 3.87 | - | 2.2 | 2 | - | - | EXPECTED_ACTIVE | True | -0.006 | UNEXPLAINED_VARIANCE |
| 2026_03_PHI_CHI | Kalif Raymond | receiving_yards | 21.9 | 0–61 | 90 | 3.84 | 0.99 | 2.2 | 7 | 10.17 | 12.86 | EXPECTED_ACTIVE | True | 0.130 | OPPORTUNITY_MISS |
| 2026_03_NYJ_DET | Jeremy Ruckert | touchdowns | 0.1 | -–- | 1 | 3.76 | - | 2.2 | 5 | - | - | EXPECTED_ACTIVE | True | 0.030 | OPPORTUNITY_MISS |
| 2026_03_MIN_TB | Ted Hurst III | touchdowns | 0.1 | -–- | 1 | 3.71 | - | 4.5 | 3 | - | - | EXPECTED_ACTIVE | True | 0.092 | UNEXPLAINED_VARIANCE |
| 2026_03_CAR_CLE | Tommy Tremble | receiving_yards | 11.1 | 0–48 | 41 | 3.69 | 0.91 | 1.6 | 4 | 6.82 | 10.25 | EXPECTED_ACTIVE | True | 0.188 | TEAM_VOLUME_MISS |
| 2026_03_CIN_PIT | Darnell Washington | receiving_yards | 15.7 | 0–53 | 67 | 3.62 | 0.97 | 1.9 | 4 | 8.44 | 16.75 | EXPECTED_ACTIVE | True | 0.144 | EFFICIENCY_MISS |
| 2026_03_ARI_SF | Michael Wilson | receptions | 3.3 | 1–7 | 11 | 3.60 | 0.99 | 5.7 | 17 | 0.59 | 0.65 | EXPECTED_ACTIVE | True | 0.117 | TEAM_VOLUME_MISS |
| 2026_03_CIN_PIT | Roman Wilson | touchdowns | 0.1 | -–- | 1 | 3.59 | - | 3.1 | 6 | - | - | EXPECTED_ACTIVE | True | 0.053 | OPPORTUNITY_MISS |
| 2026_03_PHI_CHI | Kalif Raymond | touchdowns | 0.1 | -–- | 1 | 3.45 | - | 3.3 | 7 | - | - | EXPECTED_ACTIVE | True | 0.058 | OPPORTUNITY_MISS |
| 2026_03_CAR_CLE | Chuba Hubbard | receiving_yards | 8.1 | 0–35 | 28 | 3.43 | 0.89 | 1.6 | 4 | 5.10 | 7.00 | EXPECTED_ACTIVE | True | 0.322 | TEAM_VOLUME_MISS |
| 2026_03_LV_NO | Mike Washington Jr. | rushing_yards | 13.7 | 0–54 | 54 | 3.41 | 0.95 | 3.9 | 5 | 3.50 | 10.80 | EXPECTED_ACTIVE | True | 0.245 | EFFICIENCY_MISS |
| 2026_03_NE_JAX | Josh Cameron | touchdowns | 0.1 | -–- | 1 | 3.37 | - | 4.5 | 2 | - | - | EXPECTED_ACTIVE | True | -0.011 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Christian Watson | receptions | 2.1 | 0–6 | 7 | 3.37 | 0.96 | 3.4 | 10 | 0.62 | 0.70 | EXPECTED_ACTIVE | True | 0.467 | TEAM_VOLUME_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 178, 'OPPORTUNITY_MISS': 300, 'TEAM_VOLUME_MISS': 100, 'UNEXPLAINED_VARIANCE': 30, 'NO_LARGE_MISS': 368, 'AVAILABILITY_MISS': 16, 'INSUFFICIENT_DATA': 7}.
Missing usage (no snap table or stats row): 23.

## Decision funnel

No funnel accounting is available for this period.

## Player-autopsy coverage — 2026 week 3

Expected games 16 · eligible 16 · diagnosed 16 · excluded 0 · canonical projection units 999 (976 with a box-score value) · eligible units 999, eligible but undiagnosed 0

| game | included | diagnosed units | raw records | eligible units | undiagnosed | rule | exclusion reason |
|---|---|---|---|---|---|---|---|
| 2026_03_ARI_SF | yes | 56 | 112 | 56 | 0 | autopsy-1.1.0 |  |
| 2026_03_ATL_GB | yes | 69 | 138 | 69 | 0 | autopsy-1.1.0 |  |
| 2026_03_BAL_DAL | yes | 64 | 129 | 64 | 0 | autopsy-1.1.0 |  |
| 2026_03_CAR_CLE | yes | 62 | 127 | 62 | 0 | autopsy-1.1.0 |  |
| 2026_03_CIN_PIT | yes | 56 | 112 | 56 | 0 | autopsy-1.1.0 |  |
| 2026_03_HOU_IND | yes | 64 | 129 | 64 | 0 | autopsy-1.1.0 |  |
| 2026_03_KC_MIA | yes | 64 | 128 | 64 | 0 | autopsy-1.1.0 |  |
| 2026_03_LAC_BUF | yes | 59 | 118 | 59 | 0 | autopsy-1.1.0 |  |
| 2026_03_LA_DEN | yes | 60 | 120 | 60 | 0 | autopsy-1.1.0 |  |
| 2026_03_LV_NO | yes | 64 | 128 | 64 | 0 | autopsy-1.1.0 |  |
| 2026_03_MIN_TB | yes | 64 | 128 | 64 | 0 | autopsy-1.1.0 |  |
| 2026_03_NE_JAX | yes | 68 | 137 | 68 | 0 | autopsy-1.1.0 |  |
| 2026_03_NYJ_DET | yes | 57 | 118 | 57 | 0 | autopsy-1.1.0 |  |
| 2026_03_PHI_CHI | yes | 66 | 132 | 66 | 0 | autopsy-1.1.0 |  |
| 2026_03_SEA_WAS | yes | 63 | 126 | 63 | 0 | autopsy-1.1.0 |  |
| 2026_03_TEN_NYG | yes | 63 | 129 | 63 | 0 | autopsy-1.1.0 |  |

