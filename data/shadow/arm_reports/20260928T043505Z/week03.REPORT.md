# Three-arm game-centre experiment — 2026 week 3

> **INSUFFICIENT EVIDENCE.** 15 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 1215 | 15 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 5 | 5 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 14 | 14 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 15 | 15 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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

## Game-centre accuracy — latest_pregame (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 7.30 | 10.95 | -0.50 | 11.13 | 12.68 | -3.67 | 0.245 |
| DATA_ONLY | 15 | 1 | 8.35 | 11.81 | -0.41 | 11.55 | 13.66 | -3.11 | 0.258 |
| HYBRID_30 | 15 | 1 | 7.54 | 11.17 | -0.47 | 11.26 | 12.93 | -3.50 | 0.243 |
| market at snapshot | 15 | 1 | 7.30 | 10.95 | -0.50 | 11.13 | 12.68 | -3.67 | - |
| market at close | 15 | 1 | 7.27 | 10.93 | -0.47 | 11.37 | 12.96 | -3.57 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | 1.046 | 0.480 | [0.105, 1.986] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 0.420 | 0.696 | [-0.943, 1.784] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | 0.244 | 0.152 | [-0.054, 0.541] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.126 | 0.209 | [-0.283, 0.535] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | -0.802 | 0.341 | [-1.470, -0.134] | 0.800 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -0.294 | 0.487 | [-1.248, 0.660] | 0.400 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | 1.046 | 0.480 | [0.105, 1.986] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 0.420 | 0.696 | [-0.943, 1.784] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | 0.244 | 0.152 | [-0.054, 0.541] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.126 | 0.209 | [-0.283, 0.535] | 0.600 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | 0.033 | 0.091 | [-0.145, 0.211] | 0.133 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | -0.233 | 0.188 | [-0.602, 0.135] | 0.333 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | 1.079 | 0.468 | [0.161, 1.996] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 0.187 | 0.759 | [-1.301, 1.675] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | 0.277 | 0.166 | [-0.048, 0.601] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | -0.107 | 0.310 | [-0.715, 0.500] | 0.600 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 2 | 2 | 11 | 0 | 0.500 | 0.200 | 1.92 |
| DATA_ONLY | total | 15 | 3 | 3 | 9 | 0 | 0.500 | 0.600 | 1.82 |
| HYBRID_30 | margin | 15 | 2 | 2 | 11 | 0 | 0.500 | 0.333 | 0.57 |
| HYBRID_30 | total | 15 | 3 | 3 | 9 | 0 | 0.500 | 0.600 | 0.55 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.24 | 8.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 7 | 11.48 | 10.93 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 4.10 | 2.70 | 0.000 |
| DATA_ONLY | margin | 3-5 | 1 | 7.84 | 3.50 | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 7 | 11.44 | 11.93 | 0.500 |
| DATA_ONLY | total | 1-2 | 3 | 9.81 | 9.67 | 0.500 |
| DATA_ONLY | total | 2-3 | 3 | 5.19 | 5.83 | 0.500 |
| DATA_ONLY | total | 3-5 | 1 | 21.69 | 18.50 | - |
| DATA_ONLY | total | >5 | 1 | 26.58 | 18.50 | - |
| HYBRID_30 | margin | <=1 | 14 | 7.74 | 7.57 | 0.500 |
| HYBRID_30 | margin | 1-2 | 1 | 4.80 | 3.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 14 | 10.57 | 10.61 | 0.500 |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Game-centre accuracy — T-24h (5 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 5 | 1 | 5.20 | 6.39 | 3.20 | 12.80 | 13.87 | -11.40 | 0.221 |
| DATA_ONLY | 5 | 1 | 6.04 | 6.70 | 2.51 | 12.41 | 14.16 | -11.90 | 0.208 |
| HYBRID_30 | 5 | 1 | 5.45 | 6.44 | 2.99 | 12.68 | 13.92 | -11.55 | 0.209 |
| market at snapshot | 5 | 1 | 5.20 | 6.39 | 3.20 | 12.80 | 13.87 | -11.40 | - |
| market at close | 5 | 1 | 5.00 | 6.26 | 3.40 | 12.80 | 13.87 | -11.40 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 5 | margin | 0.842 | 0.707 | [-0.544, 2.229] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 5 | total | -0.392 | 1.139 | [-2.624, 1.840] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 5 | margin | 0.253 | 0.212 | [-0.163, 0.669] | 0.200 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 5 | total | -0.118 | 0.342 | [-0.787, 0.552] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 5 | margin | -0.589 | 0.495 | [-1.560, 0.381] | 0.800 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 5 | total | 0.275 | 0.797 | [-1.288, 1.837] | 0.400 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 5 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 5 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 5 | margin | 0.842 | 0.707 | [-0.544, 2.229] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 5 | total | -0.392 | 1.139 | [-2.624, 1.840] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 5 | margin | 0.253 | 0.212 | [-0.163, 0.669] | 0.200 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 5 | total | -0.118 | 0.342 | [-0.787, 0.552] | 0.600 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 5 | margin | 0.200 | 0.200 | [-0.192, 0.592] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 5 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 5 | margin | 1.042 | 0.735 | [-0.398, 2.483] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 5 | total | -0.392 | 1.139 | [-2.624, 1.840] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 5 | margin | 0.453 | 0.291 | [-0.119, 1.024] | 0.200 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 5 | total | -0.118 | 0.342 | [-0.787, 0.552] | 0.600 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 5 | 0 | 1 | 4 | 0 | 0.000 | 0.200 | 1.36 |
| DATA_ONLY | total | 5 | 0 | 0 | 5 | 0 | - | 0.600 | 2.11 |
| HYBRID_30 | margin | 5 | 0 | 1 | 4 | 0 | 0.000 | 0.200 | 0.41 |
| HYBRID_30 | total | 5 | 0 | 0 | 5 | 0 | - | 0.600 | 0.63 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.51 | 8.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 2 | 4.85 | 4.75 | - |
| DATA_ONLY | margin | 2-3 | 1 | 3.48 | 0.50 | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 16.57 | 17.50 | - |
| DATA_ONLY | total | 1-2 | 1 | 12.60 | 11.50 | - |
| DATA_ONLY | total | 2-3 | 1 | 1.28 | 3.50 | - |
| DATA_ONLY | total | 3-5 | 2 | 15.80 | 15.75 | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 5 | 5.45 | 5.20 | 0.000 |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 5 | 12.68 | 12.80 | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 5}; DATA_ONLY quality states: {'OK': 5}; close centre status: {'OK': 5}.

## Game-centre accuracy — T-6h (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 7.43 | 11.01 | -0.63 | 11.27 | 12.81 | -3.67 | 0.252 |
| DATA_ONLY | 15 | 1 | 8.38 | 11.83 | -0.44 | 11.57 | 13.68 | -3.12 | 0.261 |
| HYBRID_30 | 15 | 1 | 7.72 | 11.22 | -0.58 | 11.36 | 13.02 | -3.50 | 0.252 |
| market at snapshot | 15 | 1 | 7.43 | 11.01 | -0.63 | 11.27 | 12.81 | -3.67 | - |
| market at close | 15 | 1 | 7.27 | 10.93 | -0.47 | 11.37 | 12.96 | -3.57 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | 0.949 | 0.520 | [-0.070, 1.969] | 0.267 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 0.301 | 0.696 | [-1.063, 1.665] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | 0.285 | 0.156 | [-0.021, 0.591] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.090 | 0.209 | [-0.319, 0.499] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | -0.665 | 0.364 | [-1.378, 0.049] | 0.733 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -0.211 | 0.487 | [-1.165, 0.744] | 0.400 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | 0.949 | 0.520 | [-0.070, 1.969] | 0.267 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 0.301 | 0.696 | [-1.063, 1.665] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | 0.285 | 0.156 | [-0.021, 0.591] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.090 | 0.209 | [-0.319, 0.499] | 0.600 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | 0.167 | 0.159 | [-0.146, 0.479] | 0.133 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | -0.100 | 0.214 | [-0.519, 0.319] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | 1.116 | 0.471 | [0.193, 2.039] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 0.201 | 0.754 | [-1.278, 1.680] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | 0.451 | 0.166 | [0.127, 0.776] | 0.133 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | -0.010 | 0.318 | [-0.633, 0.613] | 0.533 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 3 | 2 | 10 | 0 | 0.600 | 0.267 | 1.84 |
| DATA_ONLY | total | 15 | 3 | 2 | 10 | 0 | 0.600 | 0.600 | 1.87 |
| HYBRID_30 | margin | 15 | 3 | 2 | 10 | 0 | 0.600 | 0.267 | 0.55 |
| HYBRID_30 | total | 15 | 3 | 2 | 10 | 0 | 0.600 | 0.600 | 0.56 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 5.87 | 5.83 | 0.500 |
| DATA_ONLY | margin | 1-2 | 7 | 11.71 | 10.93 | 0.500 |
| DATA_ONLY | margin | 2-3 | 3 | 5.04 | 2.50 | - |
| DATA_ONLY | margin | 3-5 | 2 | 5.52 | 5.00 | 1.000 |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 5 | 11.06 | 11.50 | 1.000 |
| DATA_ONLY | total | 1-2 | 5 | 10.88 | 11.40 | 0.667 |
| DATA_ONLY | total | 2-3 | 3 | 5.19 | 5.83 | 0.000 |
| DATA_ONLY | total | 3-5 | 1 | 21.69 | 18.50 | - |
| DATA_ONLY | total | >5 | 1 | 26.58 | 18.50 | - |
| HYBRID_30 | margin | <=1 | 14 | 7.93 | 7.71 | 0.600 |
| HYBRID_30 | margin | 1-2 | 1 | 4.80 | 3.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 14 | 10.67 | 10.75 | 0.600 |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Game-centre accuracy — T-90m (14 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 14 | 1 | 5.89 | 8.84 | -2.39 | 11.64 | 13.21 | -3.29 | 0.229 |
| DATA_ONLY | 14 | 1 | 6.93 | 9.64 | -2.44 | 11.94 | 14.05 | -2.90 | 0.234 |
| HYBRID_30 | 14 | 1 | 6.18 | 9.04 | -2.41 | 11.73 | 13.41 | -3.17 | 0.226 |
| market at snapshot | 14 | 1 | 5.89 | 8.84 | -2.39 | 11.64 | 13.21 | -3.29 | - |
| market at close | 14 | 1 | 5.89 | 8.83 | -2.39 | 11.68 | 13.29 | -3.32 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 14 | margin | 1.039 | 0.518 | [0.023, 2.055] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 14 | total | 0.301 | 0.707 | [-1.085, 1.687] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | margin | 0.287 | 0.161 | [-0.029, 0.602] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | total | 0.090 | 0.212 | [-0.326, 0.506] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | margin | -0.753 | 0.360 | [-1.459, -0.047] | 0.786 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | total | -0.211 | 0.495 | [-1.181, 0.760] | 0.429 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 14 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 14 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | margin | 1.039 | 0.518 | [0.023, 2.055] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | total | 0.301 | 0.707 | [-1.085, 1.687] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | margin | 0.287 | 0.161 | [-0.029, 0.602] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | total | 0.090 | 0.212 | [-0.326, 0.506] | 0.571 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | margin | 0.000 | 0.117 | [-0.230, 0.230] | 0.143 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | total | -0.036 | 0.199 | [-0.426, 0.355] | 0.286 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | margin | 1.039 | 0.501 | [0.057, 2.021] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | total | 0.265 | 0.811 | [-1.324, 1.854] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | margin | 0.287 | 0.168 | [-0.043, 0.616] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | total | 0.055 | 0.347 | [-0.625, 0.734] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 14 | 2 | 2 | 10 | 0 | 0.500 | 0.214 | 1.90 |
| DATA_ONLY | total | 14 | 3 | 4 | 7 | 0 | 0.429 | 0.571 | 1.89 |
| HYBRID_30 | margin | 14 | 2 | 2 | 10 | 0 | 0.500 | 0.286 | 0.57 |
| HYBRID_30 | total | 14 | 3 | 4 | 7 | 0 | 0.429 | 0.571 | 0.57 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.24 | 8.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 6 | 8.70 | 8.33 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 4.10 | 2.60 | 0.000 |
| DATA_ONLY | margin | 3-5 | 1 | 7.84 | 3.50 | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 6 | 12.33 | 12.83 | 0.667 |
| DATA_ONLY | total | 1-2 | 3 | 9.81 | 9.67 | 0.500 |
| DATA_ONLY | total | 2-3 | 2 | 4.33 | 4.25 | - |
| DATA_ONLY | total | 3-5 | 2 | 14.30 | 14.50 | 0.000 |
| DATA_ONLY | total | >5 | 1 | 26.58 | 19.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 13 | 6.29 | 6.08 | 0.500 |
| HYBRID_30 | margin | 1-2 | 1 | 4.80 | 3.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 12 | 11.10 | 11.08 | 0.600 |
| HYBRID_30 | total | 1-2 | 1 | 9.42 | 10.50 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 14}; DATA_ONLY quality states: {'OK': 14}; close centre status: {'OK': 14}.

## Game-centre accuracy — T-30m (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 7.30 | 10.95 | -0.50 | 11.13 | 12.68 | -3.67 | 0.245 |
| DATA_ONLY | 15 | 1 | 8.35 | 11.81 | -0.41 | 11.55 | 13.66 | -3.11 | 0.258 |
| HYBRID_30 | 15 | 1 | 7.54 | 11.17 | -0.47 | 11.26 | 12.93 | -3.50 | 0.243 |
| market at snapshot | 15 | 1 | 7.30 | 10.95 | -0.50 | 11.13 | 12.68 | -3.67 | - |
| market at close | 15 | 1 | 7.27 | 10.93 | -0.47 | 11.37 | 12.96 | -3.57 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | 1.046 | 0.480 | [0.105, 1.986] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 0.420 | 0.696 | [-0.943, 1.784] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | 0.244 | 0.152 | [-0.054, 0.541] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.126 | 0.209 | [-0.283, 0.535] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | -0.802 | 0.341 | [-1.470, -0.134] | 0.800 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -0.294 | 0.487 | [-1.248, 0.660] | 0.400 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | 1.046 | 0.480 | [0.105, 1.986] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 0.420 | 0.696 | [-0.943, 1.784] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | 0.244 | 0.152 | [-0.054, 0.541] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.126 | 0.209 | [-0.283, 0.535] | 0.600 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | 0.033 | 0.091 | [-0.145, 0.211] | 0.133 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | -0.233 | 0.188 | [-0.602, 0.135] | 0.333 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | 1.079 | 0.468 | [0.161, 1.996] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 0.187 | 0.759 | [-1.301, 1.675] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | 0.277 | 0.166 | [-0.048, 0.601] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | -0.107 | 0.310 | [-0.715, 0.500] | 0.600 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 2 | 2 | 11 | 0 | 0.500 | 0.200 | 1.92 |
| DATA_ONLY | total | 15 | 3 | 3 | 9 | 0 | 0.500 | 0.600 | 1.82 |
| HYBRID_30 | margin | 15 | 2 | 2 | 11 | 0 | 0.500 | 0.333 | 0.57 |
| HYBRID_30 | total | 15 | 3 | 3 | 9 | 0 | 0.500 | 0.600 | 0.55 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.24 | 8.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 7 | 11.48 | 10.93 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 4.10 | 2.70 | 0.000 |
| DATA_ONLY | margin | 3-5 | 1 | 7.84 | 3.50 | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 7 | 11.44 | 11.93 | 0.500 |
| DATA_ONLY | total | 1-2 | 3 | 9.81 | 9.67 | 0.500 |
| DATA_ONLY | total | 2-3 | 3 | 5.19 | 5.83 | 0.500 |
| DATA_ONLY | total | 3-5 | 1 | 21.69 | 18.50 | - |
| DATA_ONLY | total | >5 | 1 | 26.58 | 18.50 | - |
| HYBRID_30 | margin | <=1 | 14 | 7.74 | 7.57 | 0.500 |
| HYBRID_30 | margin | 1-2 | 1 | 4.80 | 3.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 14 | 10.57 | 10.61 | 0.500 |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Contract pricing — latest_pregame (1173 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1173 | 0.1463 | 0.4463 | 0.411 | 0.421 | 1173 | 0.1463 | 0.1476 | 0.1527 |
| DATA_ONLY | 1173 | 0.1571 | 0.4769 | 0.417 | 0.421 | 1173 | 0.1571 | 0.1476 | 0.1527 |
| HYBRID_30 | 1173 | 0.1500 | 0.4560 | 0.410 | 0.421 | 1173 | 0.1500 | 0.1476 | 0.1527 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1173 | 15 | 0.01079 | [0.00054, 0.02261] | 0.01079 | [0.00054, 0.02261] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1173 | 15 | 0.00371 | [0.00066, 0.00684] | 0.00371 | [0.00066, 0.00684] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1173 | 15 | -0.00708 | [-0.01667, 0.00096] | -0.00708 | [-0.01667, 0.00096] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1173 | 15 | - | - | -0.00131 | [-0.00345, 0.00059] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1135 | 15 | - | - | -0.00156 | [-0.00407, 0.00071] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1173 | 15 | - | - | 0.00948 | [-0.00185, 0.02223] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1135 | 15 | - | - | 0.00957 | [-0.00207, 0.02284] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1173 | 15 | - | - | 0.00240 | [-0.00184, 0.00631] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1135 | 15 | - | - | 0.00227 | [-0.00246, 0.00671] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 389, 'TEAM_TOTAL': 409, 'TOTAL': 285}; settlement: {'SETTLED': 1173}; close: {'OK': 1135, 'OK_STALE': 38}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 192 / 0.057 / 0.036 | 187 / 0.052 / 0.053 | 182 / 0.052 / 0.044 |
| 0.10-0.20 | 183 / 0.146 / 0.153 | 184 / 0.146 / 0.158 | 195 / 0.146 / 0.138 |
| 0.20-0.30 | 132 / 0.248 / 0.212 | 139 / 0.252 / 0.223 | 135 / 0.252 / 0.244 |
| 0.30-0.40 | 133 / 0.351 / 0.353 | 115 / 0.350 / 0.330 | 116 / 0.349 / 0.328 |
| 0.40-0.50 | 113 / 0.453 / 0.513 | 115 / 0.448 / 0.522 | 136 / 0.449 / 0.544 |
| 0.50-0.60 | 112 / 0.545 / 0.545 | 103 / 0.551 / 0.592 | 99 / 0.550 / 0.525 |
| 0.60-0.70 | 74 / 0.651 / 0.662 | 86 / 0.647 / 0.616 | 74 / 0.646 / 0.635 |
| 0.70-0.80 | 58 / 0.754 / 0.828 | 65 / 0.749 / 0.754 | 66 / 0.749 / 0.803 |
| 0.80-0.90 | 60 / 0.847 / 0.917 | 63 / 0.849 / 0.841 | 61 / 0.853 / 0.918 |
| 0.90-1.00 | 116 / 0.953 / 0.974 | 116 / 0.955 / 0.948 | 109 / 0.956 / 0.972 |

## Contract pricing — T-24h (389 contracts, 5 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 389 | 0.1430 | 0.4339 | 0.422 | 0.517 | 389 | 0.1430 | 0.1434 | 0.1473 |
| DATA_ONLY | 389 | 0.1452 | 0.4393 | 0.420 | 0.517 | 389 | 0.1452 | 0.1434 | 0.1473 |
| HYBRID_30 | 389 | 0.1426 | 0.4308 | 0.418 | 0.517 | 389 | 0.1426 | 0.1434 | 0.1473 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 389 | 5 | 0.00219 | [-0.01041, 0.01737] | 0.00219 | [-0.01041, 0.01737] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 389 | 5 | -0.00046 | [-0.00747, 0.00584] | -0.00046 | [-0.00747, 0.00584] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 389 | 5 | -0.00264 | [-0.01283, 0.00913] | -0.00264 | [-0.01283, 0.00913] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 389 | 5 | - | - | -0.00042 | [-0.00228, 0.00146] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 380 | 5 | - | - | -0.00099 | [-0.00406, 0.00241] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 389 | 5 | - | - | 0.00177 | [-0.01027, 0.01730] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 380 | 5 | - | - | 0.00122 | [-0.00855, 0.01402] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 389 | 5 | - | - | -0.00087 | [-0.00900, 0.00668] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 380 | 5 | - | - | -0.00143 | [-0.00842, 0.00545] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 20, 'GAME_WINNER': 10, 'SPREAD': 128, 'TEAM_TOTAL': 136, 'TOTAL': 95}; settlement: {'SETTLED': 389}; close: {'OK': 380, 'OK_STALE': 9}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 57 / 0.059 / 0.000 | 58 / 0.054 / 0.034 | 57 / 0.052 / 0.000 |
| 0.10-0.20 | 59 / 0.146 / 0.153 | 65 / 0.148 / 0.154 | 62 / 0.145 / 0.129 |
| 0.20-0.30 | 45 / 0.248 / 0.333 | 46 / 0.258 / 0.348 | 49 / 0.249 / 0.367 |
| 0.30-0.40 | 45 / 0.349 / 0.467 | 37 / 0.354 / 0.486 | 37 / 0.343 / 0.541 |
| 0.40-0.50 | 41 / 0.451 / 0.659 | 38 / 0.448 / 0.684 | 48 / 0.449 / 0.667 |
| 0.50-0.60 | 37 / 0.543 / 0.730 | 40 / 0.554 / 0.750 | 30 / 0.548 / 0.667 |
| 0.60-0.70 | 26 / 0.652 / 0.885 | 23 / 0.650 / 0.739 | 23 / 0.641 / 0.870 |
| 0.70-0.80 | 18 / 0.751 / 1.000 | 20 / 0.749 / 1.000 | 22 / 0.749 / 1.000 |
| 0.80-0.90 | 21 / 0.850 / 1.000 | 23 / 0.845 / 1.000 | 20 / 0.854 / 1.000 |
| 0.90-1.00 | 40 / 0.955 / 1.000 | 39 / 0.955 / 1.000 | 41 / 0.958 / 1.000 |

## Contract pricing — T-6h (1173 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1173 | 0.1484 | 0.4512 | 0.412 | 0.421 | 1173 | 0.1484 | 0.1484 | 0.1527 |
| DATA_ONLY | 1173 | 0.1577 | 0.4778 | 0.417 | 0.421 | 1173 | 0.1577 | 0.1484 | 0.1527 |
| HYBRID_30 | 1173 | 0.1509 | 0.4585 | 0.410 | 0.421 | 1173 | 0.1509 | 0.1484 | 0.1527 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1173 | 15 | 0.00932 | [-0.00138, 0.02191] | 0.00932 | [-0.00138, 0.02191] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1173 | 15 | 0.00252 | [-0.00092, 0.00609] | 0.00252 | [-0.00092, 0.00609] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1173 | 15 | -0.00680 | [-0.01689, 0.00253] | -0.00680 | [-0.01689, 0.00253] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1173 | 15 | - | - | -0.00002 | [-0.00181, 0.00185] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1135 | 15 | - | - | 0.00060 | [-0.00140, 0.00280] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1173 | 15 | - | - | 0.00930 | [-0.00235, 0.02239] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1135 | 15 | - | - | 0.01021 | [-0.00140, 0.02328] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1173 | 15 | - | - | 0.00250 | [-0.00102, 0.00651] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1135 | 15 | - | - | 0.00321 | [-0.00036, 0.00688] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 389, 'TEAM_TOTAL': 409, 'TOTAL': 285}; settlement: {'SETTLED': 1173}; close: {'OK': 1135, 'OK_STALE': 38}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 189 / 0.056 / 0.053 | 190 / 0.053 / 0.058 | 185 / 0.052 / 0.049 |
| 0.10-0.20 | 185 / 0.145 / 0.135 | 183 / 0.146 / 0.153 | 188 / 0.145 / 0.138 |
| 0.20-0.30 | 136 / 0.248 / 0.235 | 137 / 0.251 / 0.219 | 145 / 0.251 / 0.241 |
| 0.30-0.40 | 128 / 0.351 / 0.344 | 115 / 0.350 / 0.374 | 113 / 0.350 / 0.381 |
| 0.40-0.50 | 114 / 0.452 / 0.518 | 113 / 0.447 / 0.496 | 134 / 0.450 / 0.515 |
| 0.50-0.60 | 111 / 0.543 / 0.541 | 103 / 0.548 / 0.592 | 97 / 0.550 / 0.526 |
| 0.60-0.70 | 77 / 0.652 / 0.636 | 88 / 0.646 / 0.602 | 75 / 0.645 / 0.613 |
| 0.70-0.80 | 57 / 0.756 / 0.825 | 63 / 0.750 / 0.746 | 65 / 0.748 / 0.800 |
| 0.80-0.90 | 61 / 0.850 / 0.918 | 64 / 0.848 / 0.859 | 60 / 0.853 / 0.917 |
| 0.90-1.00 | 115 / 0.955 / 0.974 | 117 / 0.955 / 0.940 | 111 / 0.955 / 0.973 |

## Contract pricing — T-90m (1093 contracts, 14 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1093 | 0.1406 | 0.4323 | 0.416 | 0.416 | 1093 | 0.1406 | 0.1402 | 0.1450 |
| DATA_ONLY | 1093 | 0.1475 | 0.4513 | 0.419 | 0.416 | 1093 | 0.1475 | 0.1402 | 0.1450 |
| HYBRID_30 | 1093 | 0.1438 | 0.4393 | 0.413 | 0.416 | 1093 | 0.1438 | 0.1402 | 0.1450 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1093 | 14 | 0.00686 | [-0.00372, 0.01922] | 0.00686 | [-0.00372, 0.01922] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1093 | 14 | 0.00319 | [-0.00059, 0.00683] | 0.00319 | [-0.00059, 0.00683] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1093 | 14 | -0.00367 | [-0.01299, 0.00473] | -0.00367 | [-0.01299, 0.00473] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1093 | 14 | - | - | 0.00044 | [-0.00227, 0.00293] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1056 | 14 | - | - | 0.00047 | [-0.00285, 0.00342] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1093 | 14 | - | - | 0.00729 | [-0.00407, 0.02085] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1056 | 14 | - | - | 0.00754 | [-0.00425, 0.02175] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1093 | 14 | - | - | 0.00363 | [-0.00054, 0.00823] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1056 | 14 | - | - | 0.00376 | [-0.00089, 0.00866] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 56, 'GAME_WINNER': 28, 'SPREAD': 362, 'TEAM_TOTAL': 381, 'TOTAL': 266}; settlement: {'SETTLED': 1093}; close: {'OK': 1056, 'OK_STALE': 37}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 172 / 0.056 / 0.023 | 172 / 0.053 / 0.035 | 165 / 0.052 / 0.024 |
| 0.10-0.20 | 171 / 0.144 / 0.123 | 169 / 0.146 / 0.124 | 184 / 0.146 / 0.120 |
| 0.20-0.30 | 122 / 0.247 / 0.213 | 130 / 0.252 / 0.215 | 127 / 0.253 / 0.236 |
| 0.30-0.40 | 118 / 0.348 / 0.322 | 106 / 0.351 / 0.311 | 103 / 0.350 / 0.359 |
| 0.40-0.50 | 108 / 0.450 / 0.491 | 108 / 0.448 / 0.500 | 130 / 0.448 / 0.515 |
| 0.50-0.60 | 112 / 0.544 / 0.571 | 96 / 0.550 / 0.615 | 92 / 0.550 / 0.489 |
| 0.60-0.70 | 67 / 0.652 / 0.642 | 82 / 0.645 / 0.634 | 69 / 0.647 / 0.652 |
| 0.70-0.80 | 56 / 0.754 / 0.821 | 60 / 0.748 / 0.767 | 59 / 0.748 / 0.814 |
| 0.80-0.90 | 57 / 0.848 / 0.947 | 61 / 0.848 / 0.869 | 58 / 0.851 / 0.914 |
| 0.90-1.00 | 110 / 0.954 / 0.964 | 109 / 0.955 / 0.945 | 106 / 0.955 / 0.981 |

## Contract pricing — T-30m (1173 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1173 | 0.1463 | 0.4461 | 0.411 | 0.421 | 1173 | 0.1463 | 0.1476 | 0.1527 |
| DATA_ONLY | 1173 | 0.1570 | 0.4767 | 0.417 | 0.421 | 1173 | 0.1570 | 0.1476 | 0.1527 |
| HYBRID_30 | 1173 | 0.1500 | 0.4560 | 0.410 | 0.421 | 1173 | 0.1500 | 0.1476 | 0.1527 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1173 | 15 | 0.01076 | [0.00054, 0.02258] | 0.01076 | [0.00054, 0.02258] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1173 | 15 | 0.00374 | [0.00067, 0.00687] | 0.00374 | [0.00067, 0.00687] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1173 | 15 | -0.00703 | [-0.01658, 0.00096] | -0.00703 | [-0.01658, 0.00096] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1173 | 15 | - | - | -0.00136 | [-0.00353, 0.00054] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1135 | 15 | - | - | -0.00160 | [-0.00407, 0.00066] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1173 | 15 | - | - | 0.00941 | [-0.00192, 0.02215] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1135 | 15 | - | - | 0.00951 | [-0.00210, 0.02273] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1173 | 15 | - | - | 0.00238 | [-0.00186, 0.00627] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1135 | 15 | - | - | 0.00226 | [-0.00246, 0.00670] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 389, 'TEAM_TOTAL': 409, 'TOTAL': 285}; settlement: {'SETTLED': 1173}; close: {'OK': 1135, 'OK_STALE': 38}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 191 / 0.056 / 0.037 | 187 / 0.052 / 0.053 | 182 / 0.052 / 0.044 |
| 0.10-0.20 | 183 / 0.146 / 0.148 | 184 / 0.146 / 0.158 | 195 / 0.146 / 0.138 |
| 0.20-0.30 | 133 / 0.247 / 0.218 | 139 / 0.252 / 0.223 | 136 / 0.252 / 0.243 |
| 0.30-0.40 | 132 / 0.351 / 0.356 | 116 / 0.350 / 0.328 | 115 / 0.350 / 0.330 |
| 0.40-0.50 | 114 / 0.453 / 0.509 | 114 / 0.449 / 0.526 | 136 / 0.449 / 0.544 |
| 0.50-0.60 | 112 / 0.545 / 0.545 | 103 / 0.551 / 0.592 | 99 / 0.550 / 0.525 |
| 0.60-0.70 | 74 / 0.651 / 0.662 | 86 / 0.647 / 0.616 | 74 / 0.646 / 0.635 |
| 0.70-0.80 | 58 / 0.754 / 0.828 | 65 / 0.749 / 0.754 | 66 / 0.749 / 0.803 |
| 0.80-0.90 | 60 / 0.847 / 0.917 | 63 / 0.849 / 0.841 | 61 / 0.854 / 0.918 |
| 0.90-1.00 | 116 / 0.953 / 0.974 | 116 / 0.955 / 0.948 | 109 / 0.956 / 0.972 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 5 | 2 | 0 | 0 | 3 | 0 | - - | 0.333 | 0.333 | 0.00 |
| T-24h | DATA_ONLY | total | 5 | 1 | 0 | 0 | 4 | 0 | - - | 0.500 | 0.500 | 0.00 |
| T-24h | HYBRID_30 (derived) | margin | 5 | 5 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-24h | HYBRID_30 (derived) | total | 5 | 5 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-6h | DATA_ONLY | margin | 15 | 3 | 2 | 1 | 9 | 0 | 0.667 [0.208, 0.939] | 0.250 | 0.250 | 0.00 |
| T-6h | DATA_ONLY | total | 15 | 5 | 2 | 2 | 6 | 0 | 0.500 [0.150, 0.850] | 0.500 | 0.500 | -0.20 |
| T-6h | HYBRID_30 (derived) | margin | 15 | 14 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-6h | HYBRID_30 (derived) | total | 15 | 14 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-90m | DATA_ONLY | margin | 14 | 2 | 2 | 1 | 9 | 0 | 0.667 [0.208, 0.939] | 0.250 | 0.250 | 0.00 |
| T-90m | DATA_ONLY | total | 14 | 6 | 1 | 3 | 4 | 0 | 0.250 [0.046, 0.699] | 0.375 | 0.375 | -0.31 |
| T-90m | HYBRID_30 (derived) | margin | 14 | 13 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-90m | HYBRID_30 (derived) | total | 14 | 12 | 0 | 2 | 0 | 0 | 0.000 [0.000, 0.658] | 0.500 | 0.500 | -0.75 |
| T-30m | DATA_ONLY | margin | 15 | 2 | 2 | 1 | 10 | 0 | 0.667 [0.208, 0.939] | 0.231 | 0.231 | 0.04 |
| T-30m | DATA_ONLY | total | 15 | 7 | 2 | 2 | 4 | 0 | 0.500 [0.150, 0.850] | 0.375 | 0.375 | -0.25 |
| T-30m | HYBRID_30 (derived) | margin | 15 | 14 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-30m | HYBRID_30 (derived) | total | 15 | 14 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| latest_pregame | DATA_ONLY | margin | 15 | 2 | 2 | 1 | 10 | 0 | 0.667 [0.208, 0.939] | 0.231 | 0.231 | 0.04 |
| latest_pregame | DATA_ONLY | total | 15 | 7 | 2 | 2 | 4 | 0 | 0.500 [0.150, 0.850] | 0.375 | 0.375 | -0.25 |
| latest_pregame | HYBRID_30 (derived) | margin | 15 | 14 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | total | 15 | 14 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 2 | 0 | 1 | 1 | 0 | 0.000 |
| margin | 1-2 | 7 | 2 | 0 | 5 | 0 | 1.000 |
| margin | 2-3 | 5 | 0 | 1 | 4 | 0 | 0.000 |
| margin | 3-5 | 1 | 0 | 0 | 1 | 0 | - |
| margin | >5 | 0 | 0 | 0 | 0 | 0 | - |
| total | <=1 | 7 | 1 | 1 | 5 | 0 | 0.500 |
| total | 1-2 | 3 | 1 | 1 | 1 | 0 | 0.500 |
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

