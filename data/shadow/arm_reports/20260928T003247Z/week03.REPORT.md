# Three-arm game-centre experiment — 2026 week 3

> **INSUFFICIENT EVIDENCE.** 14 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 1128 | 14 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 4 | 4 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 14 | 14 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 13 | 13 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 14 | 14 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 14 | 14 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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

## Game-centre accuracy — latest_pregame (14 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 14 | 1 | 7.50 | 11.27 | -0.21 | 11.11 | 12.76 | -3.11 | 0.243 |
| DATA_ONLY | 14 | 1 | 8.60 | 12.16 | -0.09 | 11.69 | 13.91 | -2.64 | 0.254 |
| HYBRID_30 | 14 | 1 | 7.75 | 11.50 | -0.18 | 11.28 | 13.06 | -2.97 | 0.238 |
| market at snapshot | 14 | 1 | 7.50 | 11.27 | -0.21 | 11.11 | 12.76 | -3.11 | - |
| market at close | 14 | 1 | 7.54 | 11.28 | -0.25 | 11.25 | 12.96 | -2.89 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 14 | margin | 1.100 | 0.512 | [0.096, 2.104] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 14 | total | 0.579 | 0.727 | [-0.847, 2.005] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | margin | 0.255 | 0.162 | [-0.063, 0.573] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | total | 0.174 | 0.218 | [-0.254, 0.601] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | margin | -0.845 | 0.363 | [-1.557, -0.133] | 0.786 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | total | -0.405 | 0.509 | [-1.403, 0.593] | 0.429 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 14 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 14 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | margin | 1.100 | 0.512 | [0.096, 2.104] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | total | 0.579 | 0.727 | [-0.847, 2.005] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | margin | 0.255 | 0.162 | [-0.063, 0.573] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | total | 0.174 | 0.218 | [-0.254, 0.601] | 0.571 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | margin | -0.036 | 0.063 | [-0.160, 0.089] | 0.143 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | total | -0.143 | 0.177 | [-0.490, 0.204] | 0.286 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | margin | 1.064 | 0.503 | [0.079, 2.050] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | total | 0.436 | 0.770 | [-1.073, 1.946] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | margin | 0.219 | 0.167 | [-0.108, 0.546] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | total | 0.031 | 0.298 | [-0.553, 0.615] | 0.571 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 14 | 2 | 1 | 11 | 0 | 0.667 | 0.214 | 2.03 |
| DATA_ONLY | total | 14 | 3 | 2 | 9 | 0 | 0.600 | 0.571 | 1.82 |
| HYBRID_30 | margin | 14 | 2 | 1 | 11 | 0 | 0.667 | 0.357 | 0.61 |
| HYBRID_30 | total | 14 | 3 | 2 | 9 | 0 | 0.600 | 0.571 | 0.55 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 1 | 11.69 | 11.50 | - |
| DATA_ONLY | margin | 1-2 | 7 | 11.48 | 10.93 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 4.10 | 2.70 | 0.000 |
| DATA_ONLY | margin | 3-5 | 1 | 7.84 | 3.50 | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 7 | 11.44 | 11.93 | 0.500 |
| DATA_ONLY | total | 1-2 | 2 | 9.86 | 8.75 | 1.000 |
| DATA_ONLY | total | 2-3 | 3 | 5.19 | 5.83 | 0.500 |
| DATA_ONLY | total | 3-5 | 1 | 21.69 | 18.50 | - |
| DATA_ONLY | total | >5 | 1 | 26.58 | 18.50 | - |
| HYBRID_30 | margin | <=1 | 13 | 7.98 | 7.81 | 0.667 |
| HYBRID_30 | margin | 1-2 | 1 | 4.80 | 3.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 13 | 10.54 | 10.54 | 0.600 |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 14}; DATA_ONLY quality states: {'OK': 14}; close centre status: {'OK': 14}.

## Game-centre accuracy — T-24h (4 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4 | 1 | 5.38 | 6.78 | 5.12 | 12.75 | 14.08 | -11.00 | 0.200 |
| DATA_ONLY | 4 | 1 | 6.22 | 7.00 | 4.48 | 13.03 | 15.04 | -12.39 | 0.173 |
| HYBRID_30 | 4 | 1 | 5.63 | 6.80 | 4.93 | 12.83 | 14.34 | -11.42 | 0.185 |
| market at snapshot | 4 | 1 | 5.38 | 6.78 | 5.12 | 12.75 | 14.08 | -11.00 | - |
| market at close | 4 | 1 | 5.38 | 6.78 | 5.12 | 12.75 | 14.08 | -11.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4 | margin | 0.843 | 0.913 | [-0.947, 2.633] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 4 | total | 0.282 | 1.184 | [-2.038, 2.603] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4 | margin | 0.253 | 0.274 | [-0.284, 0.790] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4 | total | 0.085 | 0.355 | [-0.612, 0.781] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4 | margin | -0.590 | 0.639 | [-1.843, 0.663] | 0.750 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4 | total | -0.198 | 0.829 | [-1.822, 1.427] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 4 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4 | margin | 0.843 | 0.913 | [-0.947, 2.633] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4 | total | 0.282 | 1.184 | [-2.038, 2.603] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4 | margin | 0.253 | 0.274 | [-0.284, 0.790] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4 | total | 0.085 | 0.355 | [-0.612, 0.781] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 4 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 4 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 4 | margin | 0.843 | 0.913 | [-0.947, 2.633] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 4 | total | 0.282 | 1.184 | [-2.038, 2.603] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 4 | margin | 0.253 | 0.274 | [-0.284, 0.790] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 4 | total | 0.085 | 0.355 | [-0.612, 0.781] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 4 | 0 | 0 | 4 | 0 | - | 0.250 | 1.49 |
| DATA_ONLY | total | 4 | 0 | 0 | 4 | 0 | - | 0.500 | 1.86 |
| HYBRID_30 | margin | 4 | 0 | 0 | 4 | 0 | - | 0.250 | 0.45 |
| HYBRID_30 | total | 4 | 0 | 0 | 4 | 0 | - | 0.500 | 0.56 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 1 | 11.69 | 11.50 | - |
| DATA_ONLY | margin | 1-2 | 2 | 4.85 | 4.75 | - |
| DATA_ONLY | margin | 2-3 | 1 | 3.48 | 0.50 | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 16.57 | 17.50 | - |
| DATA_ONLY | total | 1-2 | 1 | 12.60 | 11.50 | - |
| DATA_ONLY | total | 2-3 | 1 | 1.28 | 3.50 | - |
| DATA_ONLY | total | 3-5 | 1 | 21.69 | 18.50 | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 4 | 5.63 | 5.38 | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 4 | 12.83 | 12.75 | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 4}; DATA_ONLY quality states: {'OK': 4}; close centre status: {'OK': 4}.

## Game-centre accuracy — T-6h (14 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 14 | 1 | 7.57 | 11.31 | -0.29 | 11.25 | 12.90 | -3.11 | 0.247 |
| DATA_ONLY | 14 | 1 | 8.60 | 12.16 | -0.09 | 11.69 | 13.91 | -2.64 | 0.254 |
| HYBRID_30 | 14 | 1 | 7.88 | 11.52 | -0.23 | 11.38 | 13.15 | -2.97 | 0.245 |
| market at snapshot | 14 | 1 | 7.57 | 11.31 | -0.29 | 11.25 | 12.90 | -3.11 | - |
| market at close | 14 | 1 | 7.54 | 11.28 | -0.25 | 11.25 | 12.96 | -2.89 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 14 | margin | 1.029 | 0.552 | [-0.054, 2.111] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 14 | total | 0.436 | 0.733 | [-1.001, 1.873] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | margin | 0.309 | 0.166 | [-0.016, 0.633] | 0.214 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | total | 0.131 | 0.220 | [-0.300, 0.562] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | margin | -0.720 | 0.386 | [-1.478, 0.037] | 0.786 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | total | -0.305 | 0.513 | [-1.311, 0.701] | 0.429 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 14 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 14 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | margin | 1.029 | 0.552 | [-0.054, 2.111] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | total | 0.436 | 0.733 | [-1.001, 1.873] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | margin | 0.309 | 0.166 | [-0.016, 0.633] | 0.214 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | total | 0.131 | 0.220 | [-0.300, 0.562] | 0.571 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | margin | 0.036 | 0.098 | [-0.155, 0.227] | 0.143 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | total | 0.000 | 0.203 | [-0.398, 0.398] | 0.143 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | margin | 1.064 | 0.503 | [0.079, 2.050] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | total | 0.436 | 0.770 | [-1.073, 1.946] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | margin | 0.344 | 0.136 | [0.078, 0.610] | 0.143 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | total | 0.131 | 0.306 | [-0.470, 0.731] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 14 | 2 | 2 | 10 | 0 | 0.500 | 0.214 | 1.96 |
| DATA_ONLY | total | 14 | 3 | 1 | 10 | 0 | 0.750 | 0.571 | 1.90 |
| HYBRID_30 | margin | 14 | 2 | 2 | 10 | 0 | 0.500 | 0.214 | 0.59 |
| HYBRID_30 | total | 14 | 3 | 1 | 10 | 0 | 0.750 | 0.571 | 0.57 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 6.14 | 6.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 7 | 11.71 | 10.93 | 0.500 |
| DATA_ONLY | margin | 2-3 | 3 | 5.04 | 2.50 | - |
| DATA_ONLY | margin | 3-5 | 2 | 5.52 | 5.00 | 1.000 |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 5 | 11.06 | 11.50 | 1.000 |
| DATA_ONLY | total | 1-2 | 4 | 11.12 | 11.38 | 1.000 |
| DATA_ONLY | total | 2-3 | 3 | 5.19 | 5.83 | 0.000 |
| DATA_ONLY | total | 3-5 | 1 | 21.69 | 18.50 | - |
| DATA_ONLY | total | >5 | 1 | 26.58 | 18.50 | - |
| HYBRID_30 | margin | <=1 | 13 | 8.12 | 7.88 | 0.500 |
| HYBRID_30 | margin | 1-2 | 1 | 4.80 | 3.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 13 | 10.65 | 10.69 | 0.750 |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 14}; DATA_ONLY quality states: {'OK': 14}; close centre status: {'OK': 14}.

## Game-centre accuracy — T-90m (13 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 13 | 1 | 6.00 | 9.09 | -2.23 | 11.65 | 13.33 | -2.65 | 0.226 |
| DATA_ONLY | 13 | 1 | 7.10 | 9.92 | -2.26 | 12.12 | 14.33 | -2.37 | 0.229 |
| HYBRID_30 | 13 | 1 | 6.30 | 9.29 | -2.24 | 11.79 | 13.58 | -2.57 | 0.221 |
| market at snapshot | 13 | 1 | 6.00 | 9.09 | -2.23 | 11.65 | 13.33 | -2.65 | - |
| market at close | 13 | 1 | 6.08 | 9.11 | -2.31 | 11.58 | 13.31 | -2.58 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 13 | margin | 1.097 | 0.556 | [0.007, 2.188] | 0.231 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 13 | total | 0.462 | 0.743 | [-0.995, 1.920] | 0.538 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 13 | margin | 0.302 | 0.173 | [-0.037, 0.641] | 0.308 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 13 | total | 0.139 | 0.223 | [-0.298, 0.576] | 0.538 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 13 | margin | -0.795 | 0.386 | [-1.552, -0.038] | 0.769 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 13 | total | -0.324 | 0.520 | [-1.344, 0.696] | 0.462 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 13 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 13 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 13 | margin | 1.097 | 0.556 | [0.007, 2.188] | 0.231 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 13 | total | 0.462 | 0.743 | [-0.995, 1.920] | 0.538 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 13 | margin | 0.302 | 0.173 | [-0.037, 0.641] | 0.308 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 13 | total | 0.139 | 0.223 | [-0.298, 0.576] | 0.538 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 13 | margin | -0.077 | 0.096 | [-0.264, 0.110] | 0.154 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 13 | total | 0.077 | 0.178 | [-0.271, 0.425] | 0.231 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 13 | margin | 1.020 | 0.541 | [-0.040, 2.080] | 0.231 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 13 | total | 0.539 | 0.824 | [-1.076, 2.155] | 0.462 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 13 | margin | 0.225 | 0.169 | [-0.106, 0.557] | 0.308 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 13 | total | 0.216 | 0.331 | [-0.434, 0.865] | 0.462 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 13 | 2 | 1 | 10 | 0 | 0.667 | 0.231 | 2.02 |
| DATA_ONLY | total | 13 | 3 | 3 | 7 | 0 | 0.500 | 0.538 | 1.89 |
| HYBRID_30 | margin | 13 | 2 | 1 | 10 | 0 | 0.667 | 0.308 | 0.61 |
| HYBRID_30 | total | 13 | 3 | 3 | 7 | 0 | 0.500 | 0.538 | 0.57 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 1 | 11.69 | 11.50 | - |
| DATA_ONLY | margin | 1-2 | 6 | 8.70 | 8.33 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 4.10 | 2.60 | 0.000 |
| DATA_ONLY | margin | 3-5 | 1 | 7.84 | 3.50 | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 6 | 12.33 | 12.83 | 0.667 |
| DATA_ONLY | total | 1-2 | 2 | 9.86 | 8.75 | 1.000 |
| DATA_ONLY | total | 2-3 | 2 | 4.33 | 4.25 | - |
| DATA_ONLY | total | 3-5 | 2 | 14.30 | 14.50 | 0.000 |
| DATA_ONLY | total | >5 | 1 | 26.58 | 19.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 12 | 6.43 | 6.21 | 0.667 |
| HYBRID_30 | margin | 1-2 | 1 | 4.80 | 3.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 11 | 11.11 | 11.05 | 0.750 |
| HYBRID_30 | total | 1-2 | 1 | 9.42 | 10.50 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 13}; DATA_ONLY quality states: {'OK': 13}; close centre status: {'OK': 13}.

## Game-centre accuracy — T-30m (14 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 14 | 1 | 7.50 | 11.27 | -0.21 | 11.11 | 12.76 | -3.11 | 0.243 |
| DATA_ONLY | 14 | 1 | 8.60 | 12.16 | -0.09 | 11.69 | 13.91 | -2.64 | 0.254 |
| HYBRID_30 | 14 | 1 | 7.75 | 11.50 | -0.18 | 11.28 | 13.06 | -2.97 | 0.238 |
| market at snapshot | 14 | 1 | 7.50 | 11.27 | -0.21 | 11.11 | 12.76 | -3.11 | - |
| market at close | 14 | 1 | 7.54 | 11.28 | -0.25 | 11.25 | 12.96 | -2.89 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 14 | margin | 1.100 | 0.512 | [0.096, 2.104] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 14 | total | 0.579 | 0.727 | [-0.847, 2.005] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | margin | 0.255 | 0.162 | [-0.063, 0.573] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | total | 0.174 | 0.218 | [-0.254, 0.601] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | margin | -0.845 | 0.363 | [-1.557, -0.133] | 0.786 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | total | -0.405 | 0.509 | [-1.403, 0.593] | 0.429 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 14 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 14 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | margin | 1.100 | 0.512 | [0.096, 2.104] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | total | 0.579 | 0.727 | [-0.847, 2.005] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | margin | 0.255 | 0.162 | [-0.063, 0.573] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | total | 0.174 | 0.218 | [-0.254, 0.601] | 0.571 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | margin | -0.036 | 0.063 | [-0.160, 0.089] | 0.143 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | total | -0.143 | 0.177 | [-0.490, 0.204] | 0.286 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | margin | 1.064 | 0.503 | [0.079, 2.050] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | total | 0.436 | 0.770 | [-1.073, 1.946] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | margin | 0.219 | 0.167 | [-0.108, 0.546] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | total | 0.031 | 0.298 | [-0.553, 0.615] | 0.571 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 14 | 2 | 1 | 11 | 0 | 0.667 | 0.214 | 2.03 |
| DATA_ONLY | total | 14 | 3 | 2 | 9 | 0 | 0.600 | 0.571 | 1.82 |
| HYBRID_30 | margin | 14 | 2 | 1 | 11 | 0 | 0.667 | 0.357 | 0.61 |
| HYBRID_30 | total | 14 | 3 | 2 | 9 | 0 | 0.600 | 0.571 | 0.55 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 1 | 11.69 | 11.50 | - |
| DATA_ONLY | margin | 1-2 | 7 | 11.48 | 10.93 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 4.10 | 2.70 | 0.000 |
| DATA_ONLY | margin | 3-5 | 1 | 7.84 | 3.50 | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 7 | 11.44 | 11.93 | 0.500 |
| DATA_ONLY | total | 1-2 | 2 | 9.86 | 8.75 | 1.000 |
| DATA_ONLY | total | 2-3 | 3 | 5.19 | 5.83 | 0.500 |
| DATA_ONLY | total | 3-5 | 1 | 21.69 | 18.50 | - |
| DATA_ONLY | total | >5 | 1 | 26.58 | 18.50 | - |
| HYBRID_30 | margin | <=1 | 13 | 7.98 | 7.81 | 0.667 |
| HYBRID_30 | margin | 1-2 | 1 | 4.80 | 3.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 13 | 10.54 | 10.54 | 0.600 |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 14}; DATA_ONLY quality states: {'OK': 14}; close centre status: {'OK': 14}.

## Contract pricing — latest_pregame (1095 contracts, 14 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1095 | 0.1477 | 0.4500 | 0.411 | 0.415 | 1095 | 0.1477 | 0.1488 | 0.1541 |
| DATA_ONLY | 1095 | 0.1598 | 0.4839 | 0.416 | 0.415 | 1095 | 0.1598 | 0.1488 | 0.1541 |
| HYBRID_30 | 1095 | 0.1518 | 0.4609 | 0.410 | 0.415 | 1095 | 0.1518 | 0.1488 | 0.1541 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1095 | 14 | 0.01216 | [0.00046, 0.02476] | 0.01216 | [0.00046, 0.02476] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1095 | 14 | 0.00417 | [0.00077, 0.00723] | 0.00417 | [0.00077, 0.00723] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1095 | 14 | -0.00799 | [-0.01842, 0.00105] | -0.00799 | [-0.01842, 0.00105] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1095 | 14 | - | - | -0.00112 | [-0.00344, 0.00077] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1057 | 14 | - | - | -0.00121 | [-0.00378, 0.00112] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1095 | 14 | - | - | 0.01104 | [-0.00146, 0.02408] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1057 | 14 | - | - | 0.01137 | [-0.00181, 0.02477] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1095 | 14 | - | - | 0.00304 | [-0.00120, 0.00702] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1057 | 14 | - | - | 0.00310 | [-0.00167, 0.00719] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 56, 'GAME_WINNER': 28, 'SPREAD': 364, 'TEAM_TOTAL': 381, 'TOTAL': 266}; settlement: {'SETTLED': 1095}; close: {'OK': 1057, 'OK_STALE': 38}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 181 / 0.056 / 0.039 | 178 / 0.052 / 0.056 | 171 / 0.051 / 0.047 |
| 0.10-0.20 | 171 / 0.146 / 0.164 | 172 / 0.146 / 0.169 | 183 / 0.146 / 0.148 |
| 0.20-0.30 | 124 / 0.248 / 0.210 | 130 / 0.251 / 0.223 | 125 / 0.252 / 0.248 |
| 0.30-0.40 | 122 / 0.352 / 0.344 | 106 / 0.351 / 0.330 | 109 / 0.349 / 0.312 |
| 0.40-0.50 | 102 / 0.454 / 0.480 | 105 / 0.448 / 0.505 | 123 / 0.449 / 0.520 |
| 0.50-0.60 | 105 / 0.545 / 0.524 | 95 / 0.551 / 0.568 | 92 / 0.550 / 0.500 |
| 0.60-0.70 | 72 / 0.651 / 0.653 | 82 / 0.648 / 0.598 | 71 / 0.645 / 0.620 |
| 0.70-0.80 | 54 / 0.756 / 0.815 | 60 / 0.751 / 0.733 | 63 / 0.749 / 0.794 |
| 0.80-0.90 | 56 / 0.848 / 0.911 | 59 / 0.849 / 0.831 | 58 / 0.854 / 0.914 |
| 0.90-1.00 | 108 / 0.954 / 0.972 | 108 / 0.955 / 0.944 | 100 / 0.956 / 0.970 |

## Contract pricing — T-24h (311 contracts, 4 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 311 | 0.1439 | 0.4374 | 0.428 | 0.518 | 311 | 0.1439 | 0.1448 | 0.1508 |
| DATA_ONLY | 311 | 0.1505 | 0.4526 | 0.419 | 0.518 | 311 | 0.1505 | 0.1448 | 0.1508 |
| HYBRID_30 | 311 | 0.1422 | 0.4315 | 0.424 | 0.518 | 311 | 0.1422 | 0.1448 | 0.1508 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 311 | 4 | 0.00655 | [-0.00653, 0.01989] | 0.00655 | [-0.00653, 0.01989] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 311 | 4 | -0.00171 | [-0.00881, 0.00554] | -0.00171 | [-0.00881, 0.00554] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 311 | 4 | -0.00826 | [-0.01556, -0.00099] | -0.00826 | [-0.01556, -0.00099] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 311 | 4 | - | - | -0.00085 | [-0.00297, 0.00132] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 302 | 4 | - | - | -0.00271 | [-0.00497, -0.00053] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 311 | 4 | - | - | 0.00570 | [-0.00774, 0.02043] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 302 | 4 | - | - | 0.00400 | [-0.00728, 0.01666] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 311 | 4 | - | - | -0.00256 | [-0.01076, 0.00689] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 302 | 4 | - | - | -0.00444 | [-0.00973, 0.00166] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 16, 'GAME_WINNER': 8, 'SPREAD': 103, 'TEAM_TOTAL': 108, 'TOTAL': 76}; settlement: {'SETTLED': 311}; close: {'OK': 302, 'OK_STALE': 9}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 44 / 0.060 / 0.000 | 48 / 0.053 / 0.042 | 44 / 0.052 / 0.000 |
| 0.10-0.20 | 48 / 0.147 / 0.188 | 53 / 0.150 / 0.189 | 51 / 0.144 / 0.157 |
| 0.20-0.30 | 35 / 0.247 / 0.343 | 36 / 0.260 / 0.389 | 40 / 0.250 / 0.375 |
| 0.30-0.40 | 36 / 0.347 / 0.417 | 29 / 0.355 / 0.448 | 26 / 0.343 / 0.500 |
| 0.40-0.50 | 28 / 0.450 / 0.607 | 28 / 0.446 / 0.679 | 36 / 0.451 / 0.611 |
| 0.50-0.60 | 32 / 0.544 / 0.719 | 32 / 0.555 / 0.750 | 25 / 0.550 / 0.680 |
| 0.60-0.70 | 22 / 0.649 / 0.864 | 19 / 0.651 / 0.684 | 20 / 0.639 / 0.850 |
| 0.70-0.80 | 15 / 0.749 / 1.000 | 16 / 0.744 / 1.000 | 19 / 0.750 / 1.000 |
| 0.80-0.90 | 18 / 0.849 / 1.000 | 20 / 0.844 / 1.000 | 17 / 0.858 / 1.000 |
| 0.90-1.00 | 33 / 0.956 / 1.000 | 30 / 0.955 / 1.000 | 33 / 0.959 / 1.000 |

## Contract pricing — T-6h (1095 contracts, 14 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1095 | 0.1494 | 0.4541 | 0.412 | 0.415 | 1095 | 0.1494 | 0.1492 | 0.1541 |
| DATA_ONLY | 1095 | 0.1601 | 0.4844 | 0.416 | 0.415 | 1095 | 0.1601 | 0.1492 | 0.1541 |
| HYBRID_30 | 1095 | 0.1524 | 0.4626 | 0.409 | 0.415 | 1095 | 0.1524 | 0.1492 | 0.1541 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1095 | 14 | 0.01075 | [-0.00128, 0.02387] | 0.01075 | [-0.00128, 0.02387] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1095 | 14 | 0.00297 | [-0.00068, 0.00649] | 0.00297 | [-0.00068, 0.00649] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1095 | 14 | -0.00779 | [-0.01843, 0.00261] | -0.00779 | [-0.01843, 0.00261] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1095 | 14 | - | - | 0.00019 | [-0.00181, 0.00198] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1057 | 14 | - | - | 0.00058 | [-0.00176, 0.00279] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1095 | 14 | - | - | 0.01094 | [-0.00209, 0.02432] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1057 | 14 | - | - | 0.01170 | [-0.00146, 0.02516] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1095 | 14 | - | - | 0.00316 | [-0.00065, 0.00667] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1057 | 14 | - | - | 0.00366 | [-0.00054, 0.00719] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 56, 'GAME_WINNER': 28, 'SPREAD': 364, 'TEAM_TOTAL': 381, 'TOTAL': 266}; settlement: {'SETTLED': 1095}; close: {'OK': 1057, 'OK_STALE': 38}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 178 / 0.056 / 0.056 | 180 / 0.053 / 0.061 | 173 / 0.052 / 0.052 |
| 0.10-0.20 | 173 / 0.145 / 0.145 | 171 / 0.147 / 0.164 | 178 / 0.145 / 0.146 |
| 0.20-0.30 | 126 / 0.248 / 0.230 | 127 / 0.251 / 0.220 | 135 / 0.251 / 0.244 |
| 0.30-0.40 | 118 / 0.350 / 0.322 | 107 / 0.349 / 0.355 | 104 / 0.351 / 0.356 |
| 0.40-0.50 | 105 / 0.452 / 0.495 | 104 / 0.447 / 0.481 | 122 / 0.449 / 0.492 |
| 0.50-0.60 | 103 / 0.543 / 0.524 | 94 / 0.548 / 0.574 | 90 / 0.549 / 0.511 |
| 0.60-0.70 | 74 / 0.652 / 0.622 | 84 / 0.646 / 0.583 | 72 / 0.644 / 0.597 |
| 0.70-0.80 | 53 / 0.757 / 0.811 | 60 / 0.750 / 0.733 | 62 / 0.748 / 0.790 |
| 0.80-0.90 | 57 / 0.849 / 0.912 | 60 / 0.849 / 0.850 | 57 / 0.854 / 0.912 |
| 0.90-1.00 | 108 / 0.955 / 0.972 | 108 / 0.955 / 0.935 | 102 / 0.956 / 0.971 |

## Contract pricing — T-90m (1015 contracts, 13 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1015 | 0.1416 | 0.4351 | 0.416 | 0.409 | 1015 | 0.1416 | 0.1408 | 0.1459 |
| DATA_ONLY | 1015 | 0.1498 | 0.4569 | 0.418 | 0.409 | 1015 | 0.1498 | 0.1408 | 0.1459 |
| HYBRID_30 | 1015 | 0.1454 | 0.4435 | 0.413 | 0.409 | 1015 | 0.1454 | 0.1408 | 0.1459 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1015 | 13 | 0.00815 | [-0.00308, 0.02070] | 0.00815 | [-0.00308, 0.02070] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1015 | 13 | 0.00381 | [-0.00016, 0.00780] | 0.00381 | [-0.00016, 0.00780] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1015 | 13 | -0.00433 | [-0.01450, 0.00469] | -0.00433 | [-0.01450, 0.00469] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1015 | 13 | - | - | 0.00081 | [-0.00204, 0.00339] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 978 | 13 | - | - | 0.00096 | [-0.00247, 0.00406] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1015 | 13 | - | - | 0.00896 | [-0.00301, 0.02315] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 978 | 13 | - | - | 0.00940 | [-0.00307, 0.02402] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1015 | 13 | - | - | 0.00462 | [0.00081, 0.00930] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 978 | 13 | - | - | 0.00491 | [0.00057, 0.01018] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 52, 'GAME_WINNER': 26, 'SPREAD': 337, 'TEAM_TOTAL': 353, 'TOTAL': 247}; settlement: {'SETTLED': 1015}; close: {'OK': 978, 'OK_STALE': 37}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 160 / 0.056 / 0.025 | 163 / 0.053 / 0.037 | 155 / 0.051 / 0.026 |
| 0.10-0.20 | 160 / 0.144 / 0.131 | 158 / 0.147 / 0.133 | 171 / 0.146 / 0.129 |
| 0.20-0.30 | 113 / 0.247 / 0.204 | 120 / 0.252 / 0.217 | 117 / 0.253 / 0.239 |
| 0.30-0.40 | 109 / 0.349 / 0.321 | 97 / 0.351 / 0.309 | 96 / 0.350 / 0.344 |
| 0.40-0.50 | 96 / 0.451 / 0.448 | 98 / 0.448 / 0.480 | 119 / 0.448 / 0.496 |
| 0.50-0.60 | 104 / 0.544 / 0.548 | 88 / 0.549 / 0.591 | 83 / 0.550 / 0.446 |
| 0.60-0.70 | 66 / 0.651 / 0.636 | 78 / 0.646 / 0.615 | 67 / 0.647 / 0.642 |
| 0.70-0.80 | 52 / 0.756 / 0.808 | 55 / 0.749 / 0.745 | 55 / 0.748 / 0.800 |
| 0.80-0.90 | 53 / 0.849 / 0.943 | 57 / 0.848 / 0.860 | 55 / 0.852 / 0.909 |
| 0.90-1.00 | 102 / 0.954 / 0.961 | 101 / 0.955 / 0.941 | 97 / 0.956 / 0.979 |

## Contract pricing — T-30m (1095 contracts, 14 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1095 | 0.1476 | 0.4498 | 0.411 | 0.415 | 1095 | 0.1476 | 0.1488 | 0.1541 |
| DATA_ONLY | 1095 | 0.1598 | 0.4836 | 0.415 | 0.415 | 1095 | 0.1598 | 0.1488 | 0.1541 |
| HYBRID_30 | 1095 | 0.1518 | 0.4609 | 0.410 | 0.415 | 1095 | 0.1518 | 0.1488 | 0.1541 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1095 | 14 | 0.01213 | [0.00043, 0.02471] | 0.01213 | [0.00043, 0.02471] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1095 | 14 | 0.00420 | [0.00078, 0.00725] | 0.00420 | [0.00078, 0.00725] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1095 | 14 | -0.00794 | [-0.01836, 0.00105] | -0.00794 | [-0.01836, 0.00105] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1095 | 14 | - | - | -0.00117 | [-0.00346, 0.00076] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1057 | 14 | - | - | -0.00126 | [-0.00383, 0.00104] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1095 | 14 | - | - | 0.01096 | [-0.00146, 0.02399] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1057 | 14 | - | - | 0.01130 | [-0.00182, 0.02458] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1095 | 14 | - | - | 0.00302 | [-0.00120, 0.00700] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1057 | 14 | - | - | 0.00308 | [-0.00170, 0.00718] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 56, 'GAME_WINNER': 28, 'SPREAD': 364, 'TEAM_TOTAL': 381, 'TOTAL': 266}; settlement: {'SETTLED': 1095}; close: {'OK': 1057, 'OK_STALE': 38}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 180 / 0.056 / 0.039 | 178 / 0.052 / 0.056 | 171 / 0.051 / 0.047 |
| 0.10-0.20 | 171 / 0.146 / 0.158 | 172 / 0.146 / 0.169 | 183 / 0.146 / 0.148 |
| 0.20-0.30 | 125 / 0.247 / 0.216 | 130 / 0.251 / 0.223 | 126 / 0.252 / 0.246 |
| 0.30-0.40 | 121 / 0.351 / 0.347 | 107 / 0.351 / 0.327 | 108 / 0.350 / 0.315 |
| 0.40-0.50 | 103 / 0.453 / 0.476 | 104 / 0.449 / 0.510 | 123 / 0.449 / 0.520 |
| 0.50-0.60 | 105 / 0.545 / 0.524 | 95 / 0.551 / 0.568 | 92 / 0.550 / 0.500 |
| 0.60-0.70 | 72 / 0.651 / 0.653 | 82 / 0.648 / 0.598 | 71 / 0.645 / 0.620 |
| 0.70-0.80 | 54 / 0.756 / 0.815 | 60 / 0.751 / 0.733 | 63 / 0.749 / 0.794 |
| 0.80-0.90 | 56 / 0.848 / 0.911 | 59 / 0.850 / 0.831 | 58 / 0.854 / 0.914 |
| 0.90-1.00 | 108 / 0.953 / 0.972 | 108 / 0.955 / 0.944 | 100 / 0.956 / 0.970 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 4 | 1 | 0 | 0 | 3 | 0 | - - | 0.333 | 0.333 | 0.00 |
| T-24h | DATA_ONLY | total | 4 | 1 | 0 | 0 | 3 | 0 | - - | 0.333 | 0.333 | 0.00 |
| T-24h | HYBRID_30 (derived) | margin | 4 | 4 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-24h | HYBRID_30 (derived) | total | 4 | 4 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-6h | DATA_ONLY | margin | 14 | 2 | 2 | 1 | 9 | 0 | 0.667 [0.208, 0.939] | 0.250 | 0.250 | 0.00 |
| T-6h | DATA_ONLY | total | 14 | 5 | 2 | 1 | 6 | 0 | 0.667 [0.208, 0.939] | 0.444 | 0.444 | -0.06 |
| T-6h | HYBRID_30 (derived) | margin | 14 | 13 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-6h | HYBRID_30 (derived) | total | 14 | 13 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-90m | DATA_ONLY | margin | 13 | 1 | 2 | 1 | 9 | 0 | 0.667 [0.208, 0.939] | 0.250 | 0.250 | 0.00 |
| T-90m | DATA_ONLY | total | 13 | 6 | 1 | 2 | 4 | 0 | 0.333 [0.061, 0.792] | 0.286 | 0.286 | -0.14 |
| T-90m | HYBRID_30 (derived) | margin | 13 | 12 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-90m | HYBRID_30 (derived) | total | 13 | 11 | 0 | 2 | 0 | 0 | 0.000 [0.000, 0.658] | 0.500 | 0.500 | -0.75 |
| T-30m | DATA_ONLY | margin | 14 | 1 | 2 | 1 | 10 | 0 | 0.667 [0.208, 0.939] | 0.231 | 0.231 | 0.04 |
| T-30m | DATA_ONLY | total | 14 | 7 | 2 | 1 | 4 | 0 | 0.667 [0.208, 0.939] | 0.286 | 0.286 | -0.07 |
| T-30m | HYBRID_30 (derived) | margin | 14 | 13 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-30m | HYBRID_30 (derived) | total | 14 | 13 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| latest_pregame | DATA_ONLY | margin | 14 | 1 | 2 | 1 | 10 | 0 | 0.667 [0.208, 0.939] | 0.231 | 0.231 | 0.04 |
| latest_pregame | DATA_ONLY | total | 14 | 7 | 2 | 1 | 4 | 0 | 0.667 [0.208, 0.939] | 0.286 | 0.286 | -0.07 |
| latest_pregame | HYBRID_30 (derived) | margin | 14 | 13 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | total | 14 | 13 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 1 | 0 | 0 | 1 | 0 | - |
| margin | 1-2 | 7 | 2 | 0 | 5 | 0 | 1.000 |
| margin | 2-3 | 5 | 0 | 1 | 4 | 0 | 0.000 |
| margin | 3-5 | 1 | 0 | 0 | 1 | 0 | - |
| margin | >5 | 0 | 0 | 0 | 0 | 0 | - |
| total | <=1 | 7 | 1 | 1 | 5 | 0 | 0.500 |
| total | 1-2 | 2 | 1 | 0 | 1 | 0 | 1.000 |
| total | 2-3 | 3 | 1 | 1 | 1 | 0 | 0.500 |
| total | 3-5 | 1 | 0 | 0 | 1 | 0 | - |
| total | >5 | 1 | 0 | 0 | 1 | 0 | - |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

69 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_03_ATL_GB | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.0 | 3 | 1.04 | 2.33 | EXPECTED_ACTIVE | True | -0.193 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Drake London | receiving_yards | 52.7 | 4–123 | 194 | 4.10 | 0.99 | 5.9 | 10 | 8.96 | 19.40 | EXPECTED_ACTIVE | True | 0.190 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Matthew Golden | receiving_yards | 24.0 | 0–67 | 100 | 3.95 | 0.99 | 2.4 | 12 | 10.15 | 8.33 | EXPECTED_ACTIVE | True | 0.435 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Bijan Robinson | rushing_yards | 63.1 | 14–128 | 194 | 3.90 | 0.99 | 12.2 | 29 | 5.16 | 6.69 | EXPECTED_ACTIVE | True | 0.200 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Austin Hooper | touchdowns | 0.1 | -–- | 1 | 3.87 | - | 2.2 | 2 | - | - | EXPECTED_ACTIVE | True | -0.006 | UNEXPLAINED_VARIANCE |
| 2026_03_ATL_GB | Christian Watson | receptions | 2.1 | 0–6 | 7 | 3.37 | 0.96 | 3.4 | 10 | 0.62 | 0.70 | EXPECTED_ACTIVE | True | 0.467 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Bijan Robinson | carries | 12.2 | 5–22 | 29 | 3.28 | 0.99 | 12.2 | 29 | - | - | EXPECTED_ACTIVE | True | 0.435 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Matthew Golden | touchdowns | 0.1 | -–- | 1 | 2.80 | - | 4.0 | 12 | - | - | EXPECTED_ACTIVE | True | 0.193 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Brian Robinson | touchdowns | 0.1 | -–- | 1 | 2.75 | - | 7.9 | 10 | - | - | EXPECTED_ACTIVE | True | 0.050 | UNEXPLAINED_VARIANCE |
| 2026_03_ATL_GB | MarShawn Lloyd | receptions | 0.7 | 0–5 | 2 | 2.70 | 0.80 | 1.0 | 3 | 0.74 | 0.67 | EXPECTED_ACTIVE | True | 0.352 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Matthew Golden | receptions | 1.5 | 0–5 | 5 | 2.70 | 0.95 | 2.4 | 12 | 0.63 | 0.42 | EXPECTED_ACTIVE | True | 0.480 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Drake London | receptions | 3.3 | 1–7 | 9 | 2.70 | 0.99 | 5.9 | 10 | 0.57 | 0.90 | EXPECTED_ACTIVE | True | 0.246 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Skyy Moore | receiving_yards | 12.2 | 0–53 | 31 | 2.61 | 0.83 | 1.6 | 7 | 7.75 | 4.43 | EXPECTED_ACTIVE | True | 0.200 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Jordan Love | attempts | 32.5 | 18–47 | 53 | 2.45 | 0.98 | 32.5 | 53 | - | - | EXPECTED_ACTIVE | True | -0.019 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Christian Watson | receiving_yards | 41.0 | 3–95 | 96 | 2.15 | 0.95 | 3.4 | 10 | 12.02 | 9.60 | EXPECTED_ACTIVE | True | 0.315 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Christian Watson | touchdowns | 0.2 | -–- | 1 | 2.09 | - | 5.1 | 10 | - | - | EXPECTED_ACTIVE | True | 0.201 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Chris Brooks | receiving_yards | 3.1 | 0–33 | 4 | 1.80 | 0.76 | 1.3 | 1 | 2.43 | 4.00 | EXPECTED_ACTIVE | True | -0.140 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Brian Robinson | rushing_yards | 21.5 | 0–67 | 50 | 1.75 | 0.86 | 4.7 | 10 | 4.59 | 5.00 | EXPECTED_ACTIVE | True | 0.213 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Jordan Love | passing_tds | 1.4 | 0–4 | 2 | 1.35 | 0.75 | 32.5 | 53 | 0.04 | 0.04 | EXPECTED_ACTIVE | True | 0.096 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Skyy Moore | receptions | 1.0 | 0–5 | 3 | 1.35 | 0.82 | 1.6 | 7 | 0.66 | 0.43 | EXPECTED_ACTIVE | True | 0.122 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Chris Brooks | receptions | 0.9 | 0–5 | 1 | 1.35 | 0.75 | 1.3 | 1 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | -0.138 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Tucker Kraft | receptions | 1.8 | 0–5 | 4 | 1.35 | 0.85 | 2.5 | 8 | 0.72 | 0.50 | EXPECTED_ACTIVE | True | 0.368 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Bijan Robinson | touchdowns | 0.4 | -–- | 2 | 1.34 | - | 17.2 | 31 | - | - | EXPECTED_ACTIVE | True | 0.193 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Jordan Love | completions | 21.1 | 11–31 | 28 | 1.18 | 0.85 | 32.5 | 53 | 0.65 | 0.53 | EXPECTED_ACTIVE | True | -0.095 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Brian Robinson | carries | 4.7 | 0–18 | 10 | 1.16 | 0.79 | 4.7 | 10 | - | - | EXPECTED_ACTIVE | True | 0.253 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Jordan Love | passing_yards | 238.6 | 115–362 | 312 | 0.98 | 0.81 | 32.5 | 53 | 7.33 | 5.89 | EXPECTED_ACTIVE | True | -0.058 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Kyle Pitts Sr. | receptions | 2.7 | 0–6 | 1 | -0.90 | 0.25 | 3.7 | 2 | 0.72 | 0.50 | EXPECTED_ACTIVE | True | -0.208 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Michael Penix Jr. | rushing_yards | 10.7 | 0–33 | -2 | -0.81 | 0.05 | 2.8 | 2 | 3.82 | -1.00 | EXPECTED_ACTIVE | True | 0.106 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Michael Penix Jr. | attempts | 32.2 | 18–47 | 25 | -0.79 | 0.23 | 32.2 | 25 | - | - | EXPECTED_ACTIVE | True | 0.069 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Jonnu Smith | receiving_yards | 13.4 | 0–45 | 16 | 0.75 | 0.71 | 1.9 | 3 | 7.07 | 5.33 | EXPECTED_ACTIVE | True | 0.038 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Kyle Pitts Sr. | receiving_yards | 36.6 | 0–102 | 5 | -0.69 | 0.16 | 3.7 | 2 | 9.92 | 2.50 | EXPECTED_ACTIVE | True | -0.165 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Austin Hooper | receptions | 1.1 | 0–5 | 2 | 0.67 | 0.75 | 1.6 | 2 | 0.69 | 1.00 | EXPECTED_ACTIVE | True | -0.025 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Jonnu Smith | receptions | 1.3 | 0–5 | 2 | 0.67 | 0.75 | 1.9 | 3 | 0.70 | 0.67 | EXPECTED_ACTIVE | True | -0.024 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Jordan Love | rushing_yards | 14.7 | 0–46 | 0 | -0.64 | 0.05 | 3.2 | 1 | 4.56 | 0.00 | EXPECTED_ACTIVE | True | 0.063 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Drake London | touchdowns | 0.2 | -–- | 0 | -0.53 | - | 6.7 | 10 | - | - | EXPECTED_ACTIVE | True | -0.097 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Jordan Love | touchdowns | 0.2 | -–- | 0 | -0.51 | - | 2.8 | 1 | - | - | EXPECTED_ACTIVE | True | 0.087 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Michael Penix Jr. | passing_yards | 219.0 | 94–344 | 256 | 0.49 | 0.68 | 32.2 | 25 | 6.79 | 10.24 | EXPECTED_ACTIVE | True | -0.076 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Kyle Pitts Sr. | touchdowns | 0.2 | -–- | 0 | -0.49 | - | 5.1 | 2 | - | - | EXPECTED_ACTIVE | True | 0.004 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Tucker Kraft | touchdowns | 0.2 | -–- | 0 | -0.47 | - | 4.0 | 8 | - | - | EXPECTED_ACTIVE | True | -0.114 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Olamide Zaccheaus | receptions | 1.6 | 0–5 | 2 | 0.45 | 0.62 | 2.6 | 2 | 0.60 | 1.00 | EXPECTED_ACTIVE | True | -0.036 | EFFICIENCY_MISS |

Classification counts over every diagnosed projection: {'TEAM_VOLUME_MISS': 21, 'EFFICIENCY_MISS': 13, 'UNEXPLAINED_VARIANCE': 2, 'OPPORTUNITY_MISS': 13, 'NO_LARGE_MISS': 20}.
Missing usage (no snap table or stats row): 0.

## Decision funnel

No funnel accounting is available for this period.

