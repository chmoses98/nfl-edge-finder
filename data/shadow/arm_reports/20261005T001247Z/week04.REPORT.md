# Three-arm game-centre experiment — 2026 week 4

> **INSUFFICIENT EVIDENCE.** 11 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 870 | 11 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 10 | 10 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 11 | 11 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 11 | 11 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 11 | 11 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 11 | 11 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_MIA_MIN | 2026-10-04T20:05 | 36 | CURRENT | 10.50 | 38.00 | 5 | 25 | 10.5/38.0 (kalshi_implied) | 10.5/38.0 (OK) |
|  |  |  | DATA_ONLY | 10.80 | 43.35 |  |  |  |  |
|  |  |  | HYBRID_30 | 10.59 | 39.60 |  |  |  |  |

## Game-centre accuracy — latest_pregame (11 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 11 | 1 | 6.91 | 7.98 | 2.09 | 8.86 | 10.39 | -0.86 | 0.227 |
| DATA_ONLY | 11 | 1 | 6.20 | 7.46 | 2.56 | 10.13 | 11.43 | 1.55 | 0.213 |
| HYBRID_30 | 11 | 1 | 6.65 | 7.68 | 2.23 | 9.15 | 10.59 | -0.14 | 0.223 |
| market at snapshot | 11 | 1 | 6.91 | 7.98 | 2.09 | 8.86 | 10.39 | -0.86 | - |
| market at close | 11 | 1 | 6.95 | 7.93 | 2.14 | 8.77 | 10.33 | -0.86 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 11 | margin | -0.705 | 1.024 | [-2.712, 1.302] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 11 | total | 1.263 | 0.997 | [-0.691, 3.216] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 11 | margin | -0.263 | 0.306 | [-0.862, 0.336] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 11 | total | 0.289 | 0.322 | [-0.341, 0.920] | 0.364 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 11 | margin | 0.442 | 0.724 | [-0.977, 1.862] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 11 | total | -0.974 | 0.693 | [-2.333, 0.385] | 0.727 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 11 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 11 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 11 | margin | -0.705 | 1.024 | [-2.712, 1.302] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 11 | total | 1.263 | 0.997 | [-0.691, 3.216] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 11 | margin | -0.263 | 0.306 | [-0.862, 0.336] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 11 | total | 0.289 | 0.322 | [-0.341, 0.920] | 0.364 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 11 | margin | -0.045 | 0.106 | [-0.252, 0.162] | 0.091 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 11 | total | 0.091 | 0.061 | [-0.029, 0.210] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 11 | margin | -0.751 | 0.979 | [-2.670, 1.168] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 11 | total | 1.354 | 1.012 | [-0.630, 3.338] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 11 | margin | -0.308 | 0.272 | [-0.841, 0.224] | 0.636 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 11 | total | 0.380 | 0.342 | [-0.291, 1.051] | 0.364 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 11 | 2 | 0 | 9 | 0 | 1.000 | 0.455 | 2.85 |
| DATA_ONLY | total | 11 | 0 | 2 | 9 | 0 | 0.000 | 0.273 | 3.06 |
| HYBRID_30 | margin | 11 | 2 | 0 | 9 | 0 | 1.000 | 0.545 | 0.86 |
| HYBRID_30 | total | 11 | 0 | 2 | 9 | 0 | 0.000 | 0.364 | 0.92 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 1 | 5.80 | 5.50 | - |
| DATA_ONLY | margin | 1-2 | 3 | 4.02 | 4.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.17 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 2 | 14.68 | 14.75 | - |
| DATA_ONLY | total | 3-5 | 4 | 7.26 | 6.50 | - |
| DATA_ONLY | total | >5 | 2 | 15.67 | 10.25 | 0.000 |
| HYBRID_30 | margin | <=1 | 7 | 6.35 | 6.29 | 1.000 |
| HYBRID_30 | margin | 1-2 | 4 | 7.17 | 8.00 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 6 | 8.59 | 8.75 | 0.000 |
| HYBRID_30 | total | 1-2 | 5 | 9.83 | 9.00 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 11}; DATA_ONLY quality states: {'OK': 11}; close centre status: {'OK': 11}.

## Game-centre accuracy — T-24h (10 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 10 | 1 | 6.95 | 8.12 | 2.75 | 8.50 | 10.05 | 0.50 | 0.216 |
| DATA_ONLY | 10 | 1 | 6.17 | 7.55 | 3.47 | 10.06 | 11.49 | 2.78 | 0.193 |
| HYBRID_30 | 10 | 1 | 6.66 | 7.79 | 2.96 | 8.87 | 10.38 | 1.18 | 0.206 |
| market at snapshot | 10 | 1 | 6.95 | 8.12 | 2.75 | 8.50 | 10.05 | 0.50 | - |
| market at close | 10 | 1 | 7.10 | 8.14 | 2.90 | 8.30 | 9.96 | 0.40 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 10 | margin | -0.776 | 1.121 | [-2.975, 1.422] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 10 | total | 1.564 | 0.998 | [-0.393, 3.521] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | margin | -0.289 | 0.334 | [-0.945, 0.366] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 10 | total | 0.371 | 0.335 | [-0.286, 1.027] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | margin | 0.487 | 0.794 | [-1.069, 2.043] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 10 | total | -1.194 | 0.685 | [-2.535, 0.148] | 0.700 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 10 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 10 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | margin | -0.776 | 1.121 | [-2.975, 1.422] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 10 | total | 1.564 | 0.998 | [-0.393, 3.521] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | margin | -0.289 | 0.334 | [-0.945, 0.366] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 10 | total | 0.371 | 0.335 | [-0.286, 1.027] | 0.400 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | margin | -0.150 | 0.130 | [-0.405, 0.105] | 0.300 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 10 | total | 0.200 | 0.170 | [-0.133, 0.533] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | margin | -0.926 | 1.065 | [-3.014, 1.161] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 10 | total | 1.764 | 1.023 | [-0.241, 3.769] | 0.200 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | margin | -0.439 | 0.291 | [-1.010, 0.131] | 0.800 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 10 | total | 0.571 | 0.375 | [-0.165, 1.306] | 0.300 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 10 | 3 | 1 | 6 | 0 | 0.750 | 0.500 | 3.04 |
| DATA_ONLY | total | 10 | 3 | 3 | 4 | 0 | 0.500 | 0.400 | 3.00 |
| HYBRID_30 | margin | 10 | 3 | 1 | 6 | 0 | 0.750 | 0.600 | 0.91 |
| HYBRID_30 | total | 10 | 3 | 3 | 4 | 0 | 0.500 | 0.400 | 0.90 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 5.21 | 5.25 | 0.500 |
| DATA_ONLY | margin | 1-2 | 1 | 0.94 | 0.50 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.50 | 0.500 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 1 | 18.62 | 16.00 | - |
| DATA_ONLY | total | 3-5 | 5 | 9.48 | 7.90 | 0.500 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.00 | - |
| HYBRID_30 | margin | <=1 | 6 | 6.32 | 6.25 | 0.667 |
| HYBRID_30 | margin | 1-2 | 4 | 7.17 | 8.00 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 4 | 9.76 | 9.62 | 0.500 |
| HYBRID_30 | total | 1-2 | 6 | 8.28 | 7.75 | 0.500 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 10}; DATA_ONLY quality states: {'OK': 10}; close centre status: {'OK': 10}.

## Game-centre accuracy — T-6h (11 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 11 | 1 | 6.68 | 7.79 | 1.95 | 8.86 | 10.29 | -0.68 | 0.225 |
| DATA_ONLY | 11 | 1 | 6.20 | 7.46 | 2.56 | 10.13 | 11.43 | 1.55 | 0.214 |
| HYBRID_30 | 11 | 1 | 6.49 | 7.55 | 2.14 | 9.15 | 10.53 | -0.01 | 0.214 |
| market at snapshot | 11 | 1 | 6.68 | 7.79 | 1.95 | 8.86 | 10.29 | -0.68 | - |
| market at close | 11 | 1 | 6.95 | 7.93 | 2.14 | 8.77 | 10.33 | -0.86 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 11 | margin | -0.478 | 0.991 | [-2.420, 1.463] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 11 | total | 1.263 | 0.917 | [-0.535, 3.060] | 0.364 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 11 | margin | -0.195 | 0.297 | [-0.777, 0.387] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 11 | total | 0.289 | 0.304 | [-0.307, 0.885] | 0.364 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 11 | margin | 0.283 | 0.700 | [-1.089, 1.655] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 11 | total | -0.974 | 0.632 | [-2.213, 0.266] | 0.727 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 11 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 11 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 11 | margin | -0.478 | 0.991 | [-2.420, 1.463] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 11 | total | 1.263 | 0.917 | [-0.535, 3.060] | 0.364 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 11 | margin | -0.195 | 0.297 | [-0.777, 0.387] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 11 | total | 0.289 | 0.304 | [-0.307, 0.885] | 0.364 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 11 | margin | -0.273 | 0.124 | [-0.515, -0.030] | 0.364 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 11 | total | 0.091 | 0.132 | [-0.167, 0.349] | 0.091 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 11 | margin | -0.751 | 0.979 | [-2.670, 1.168] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 11 | total | 1.354 | 1.012 | [-0.630, 3.338] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 11 | margin | -0.467 | 0.299 | [-1.053, 0.118] | 0.727 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 11 | total | 0.380 | 0.390 | [-0.385, 1.145] | 0.364 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 11 | 2 | 2 | 7 | 0 | 0.500 | 0.455 | 2.71 |
| DATA_ONLY | total | 11 | 1 | 4 | 6 | 0 | 0.200 | 0.364 | 2.97 |
| HYBRID_30 | margin | 11 | 2 | 2 | 7 | 0 | 0.500 | 0.545 | 0.81 |
| HYBRID_30 | total | 11 | 1 | 4 | 6 | 0 | 0.200 | 0.364 | 0.89 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 5.21 | 5.00 | 0.500 |
| DATA_ONLY | margin | 1-2 | 2 | 3.72 | 3.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.67 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.25 | 0.000 |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.00 | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 2 | 14.68 | 14.75 | - |
| DATA_ONLY | total | 3-5 | 5 | 9.48 | 7.90 | 0.250 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 8 | 6.55 | 6.56 | 0.667 |
| HYBRID_30 | margin | 1-2 | 3 | 6.32 | 7.00 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 6 | 8.77 | 8.58 | 0.000 |
| HYBRID_30 | total | 1-2 | 5 | 9.61 | 9.20 | 0.250 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 11}; DATA_ONLY quality states: {'OK': 11}; close centre status: {'OK': 11}.

## Game-centre accuracy — T-90m (11 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 11 | 1 | 6.82 | 7.92 | 2.00 | 8.86 | 10.39 | -0.68 | 0.227 |
| DATA_ONLY | 11 | 1 | 6.20 | 7.46 | 2.56 | 10.13 | 11.43 | 1.55 | 0.214 |
| HYBRID_30 | 11 | 1 | 6.58 | 7.63 | 2.17 | 9.15 | 10.60 | -0.01 | 0.225 |
| market at snapshot | 11 | 1 | 6.82 | 7.92 | 2.00 | 8.86 | 10.39 | -0.68 | - |
| market at close | 11 | 1 | 6.95 | 7.93 | 2.14 | 8.77 | 10.33 | -0.86 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 11 | margin | -0.614 | 1.027 | [-2.628, 1.399] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 11 | total | 1.263 | 0.930 | [-0.559, 3.085] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 11 | margin | -0.236 | 0.307 | [-0.838, 0.366] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 11 | total | 0.289 | 0.303 | [-0.305, 0.883] | 0.364 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 11 | margin | 0.379 | 0.726 | [-1.044, 1.802] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 11 | total | -0.974 | 0.646 | [-2.240, 0.293] | 0.727 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 11 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 11 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 11 | margin | -0.614 | 1.027 | [-2.628, 1.399] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 11 | total | 1.263 | 0.930 | [-0.559, 3.085] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 11 | margin | -0.236 | 0.307 | [-0.838, 0.366] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 11 | total | 0.289 | 0.303 | [-0.305, 0.883] | 0.364 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 11 | margin | -0.136 | 0.119 | [-0.369, 0.096] | 0.273 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 11 | total | 0.091 | 0.148 | [-0.199, 0.381] | 0.091 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 11 | margin | -0.751 | 0.979 | [-2.670, 1.168] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 11 | total | 1.354 | 1.012 | [-0.630, 3.338] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 11 | margin | -0.372 | 0.272 | [-0.904, 0.160] | 0.727 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 11 | total | 0.380 | 0.396 | [-0.396, 1.156] | 0.364 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 11 | 3 | 1 | 7 | 0 | 0.750 | 0.455 | 2.85 |
| DATA_ONLY | total | 11 | 0 | 4 | 7 | 0 | 0.000 | 0.273 | 2.87 |
| HYBRID_30 | margin | 11 | 3 | 1 | 7 | 0 | 0.750 | 0.545 | 0.86 |
| HYBRID_30 | total | 11 | 0 | 4 | 7 | 0 | 0.000 | 0.364 | 0.86 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 5.21 | 5.25 | 0.500 |
| DATA_ONLY | margin | 1-2 | 2 | 3.72 | 3.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.17 | 0.000 |
| DATA_ONLY | total | 1-2 | 1 | 10.75 | 12.50 | 0.000 |
| DATA_ONLY | total | 2-3 | 1 | 18.62 | 16.00 | - |
| DATA_ONLY | total | 3-5 | 5 | 9.48 | 8.00 | 0.000 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 7 | 6.25 | 6.14 | 0.667 |
| HYBRID_30 | margin | 1-2 | 4 | 7.17 | 8.00 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 6 | 8.48 | 8.58 | 0.000 |
| HYBRID_30 | total | 1-2 | 5 | 9.97 | 9.20 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 11}; DATA_ONLY quality states: {'OK': 11}; close centre status: {'OK': 11}.

## Game-centre accuracy — T-30m (11 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 11 | 1 | 6.91 | 7.98 | 2.09 | 8.86 | 10.39 | -0.86 | 0.227 |
| DATA_ONLY | 11 | 1 | 6.20 | 7.46 | 2.56 | 10.13 | 11.43 | 1.55 | 0.213 |
| HYBRID_30 | 11 | 1 | 6.65 | 7.68 | 2.23 | 9.15 | 10.59 | -0.14 | 0.223 |
| market at snapshot | 11 | 1 | 6.91 | 7.98 | 2.09 | 8.86 | 10.39 | -0.86 | - |
| market at close | 11 | 1 | 6.95 | 7.93 | 2.14 | 8.77 | 10.33 | -0.86 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 11 | margin | -0.705 | 1.024 | [-2.712, 1.302] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 11 | total | 1.263 | 0.997 | [-0.691, 3.216] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 11 | margin | -0.263 | 0.306 | [-0.862, 0.336] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 11 | total | 0.289 | 0.322 | [-0.341, 0.920] | 0.364 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 11 | margin | 0.442 | 0.724 | [-0.977, 1.862] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 11 | total | -0.974 | 0.693 | [-2.333, 0.385] | 0.727 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 11 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 11 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 11 | margin | -0.705 | 1.024 | [-2.712, 1.302] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 11 | total | 1.263 | 0.997 | [-0.691, 3.216] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 11 | margin | -0.263 | 0.306 | [-0.862, 0.336] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 11 | total | 0.289 | 0.322 | [-0.341, 0.920] | 0.364 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 11 | margin | -0.045 | 0.106 | [-0.252, 0.162] | 0.091 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 11 | total | 0.091 | 0.061 | [-0.029, 0.210] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 11 | margin | -0.751 | 0.979 | [-2.670, 1.168] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 11 | total | 1.354 | 1.012 | [-0.630, 3.338] | 0.273 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 11 | margin | -0.308 | 0.272 | [-0.841, 0.224] | 0.636 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 11 | total | 0.380 | 0.342 | [-0.291, 1.051] | 0.364 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 11 | 2 | 0 | 9 | 0 | 1.000 | 0.455 | 2.85 |
| DATA_ONLY | total | 11 | 0 | 2 | 9 | 0 | 0.000 | 0.273 | 3.06 |
| HYBRID_30 | margin | 11 | 2 | 0 | 9 | 0 | 1.000 | 0.545 | 0.86 |
| HYBRID_30 | total | 11 | 0 | 2 | 9 | 0 | 0.000 | 0.364 | 0.92 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 1 | 5.80 | 5.50 | - |
| DATA_ONLY | margin | 1-2 | 3 | 4.02 | 4.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 3 | 7.21 | 7.17 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 2 | 14.68 | 14.75 | - |
| DATA_ONLY | total | 3-5 | 4 | 7.26 | 6.50 | - |
| DATA_ONLY | total | >5 | 2 | 15.67 | 10.25 | 0.000 |
| HYBRID_30 | margin | <=1 | 7 | 6.35 | 6.29 | 1.000 |
| HYBRID_30 | margin | 1-2 | 4 | 7.17 | 8.00 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 6 | 8.59 | 8.75 | 0.000 |
| HYBRID_30 | total | 1-2 | 5 | 9.83 | 9.00 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 11}; DATA_ONLY quality states: {'OK': 11}; close centre status: {'OK': 11}.

## Contract pricing — latest_pregame (854 contracts, 11 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 854 | 0.1327 | 0.4082 | 0.410 | 0.381 | 854 | 0.1327 | 0.1313 | 0.1333 |
| DATA_ONLY | 854 | 0.1337 | 0.4115 | 0.436 | 0.381 | 854 | 0.1337 | 0.1313 | 0.1333 |
| HYBRID_30 | 854 | 0.1320 | 0.4074 | 0.418 | 0.381 | 854 | 0.1320 | 0.1313 | 0.1333 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 854 | 11 | 0.00108 | [-0.01985, 0.02277] | 0.00108 | [-0.01985, 0.02277] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 854 | 11 | -0.00064 | [-0.00651, 0.00534] | -0.00064 | [-0.00651, 0.00534] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 854 | 11 | -0.00173 | [-0.01751, 0.01366] | -0.00173 | [-0.01751, 0.01366] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 854 | 11 | - | - | 0.00134 | [-0.00001, 0.00266] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 844 | 11 | - | - | 0.00094 | [-0.00039, 0.00227] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 854 | 11 | - | - | 0.00242 | [-0.01898, 0.02426] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 844 | 11 | - | - | 0.00203 | [-0.01957, 0.02433] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 854 | 11 | - | - | 0.00070 | [-0.00561, 0.00718] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 844 | 11 | - | - | 0.00029 | [-0.00601, 0.00706] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 44, 'GAME_WINNER': 22, 'SPREAD': 279, 'TEAM_TOTAL': 300, 'TOTAL': 209}; settlement: {'SETTLED': 854}; close: {'OK': 844, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 135 / 0.053 / 0.007 | 124 / 0.055 / 0.008 | 133 / 0.054 / 0.008 |
| 0.10-0.20 | 137 / 0.144 / 0.058 | 133 / 0.147 / 0.060 | 132 / 0.146 / 0.091 |
| 0.20-0.30 | 104 / 0.251 / 0.250 | 94 / 0.252 / 0.202 | 100 / 0.250 / 0.170 |
| 0.30-0.40 | 87 / 0.353 / 0.299 | 83 / 0.351 / 0.265 | 86 / 0.351 / 0.291 |
| 0.40-0.50 | 83 / 0.450 / 0.386 | 77 / 0.446 / 0.364 | 84 / 0.449 / 0.381 |
| 0.50-0.60 | 88 / 0.547 / 0.523 | 79 / 0.553 / 0.430 | 88 / 0.546 / 0.500 |
| 0.60-0.70 | 48 / 0.650 / 0.583 | 67 / 0.646 / 0.537 | 58 / 0.651 / 0.621 |
| 0.70-0.80 | 49 / 0.757 / 0.776 | 53 / 0.746 / 0.774 | 44 / 0.756 / 0.750 |
| 0.80-0.90 | 43 / 0.853 / 0.930 | 48 / 0.844 / 0.854 | 45 / 0.847 / 0.911 |
| 0.90-1.00 | 80 / 0.955 / 1.000 | 96 / 0.957 / 0.990 | 84 / 0.953 / 1.000 |

## Contract pricing — T-24h (776 contracts, 10 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 776 | 0.1304 | 0.4030 | 0.414 | 0.370 | 776 | 0.1304 | 0.1313 | 0.1317 |
| DATA_ONLY | 776 | 0.1333 | 0.4112 | 0.438 | 0.370 | 776 | 0.1333 | 0.1313 | 0.1317 |
| HYBRID_30 | 776 | 0.1304 | 0.4033 | 0.421 | 0.370 | 776 | 0.1304 | 0.1313 | 0.1317 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 776 | 10 | 0.00290 | [-0.02057, 0.02552] | 0.00290 | [-0.02057, 0.02552] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 776 | 10 | -0.00006 | [-0.00935, 0.00798] | -0.00006 | [-0.00935, 0.00798] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 776 | 10 | -0.00297 | [-0.01865, 0.01259] | -0.00297 | [-0.01865, 0.01259] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 776 | 10 | - | - | -0.00086 | [-0.00256, 0.00059] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 766 | 10 | - | - | 0.00041 | [-0.00108, 0.00236] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 776 | 10 | - | - | 0.00204 | [-0.02161, 0.02381] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 766 | 10 | - | - | 0.00335 | [-0.02123, 0.02618] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 776 | 10 | - | - | -0.00093 | [-0.00978, 0.00644] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 766 | 10 | - | - | 0.00035 | [-0.00929, 0.00847] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 40, 'GAME_WINNER': 20, 'SPREAD': 254, 'TEAM_TOTAL': 272, 'TOTAL': 190}; settlement: {'SETTLED': 776}; close: {'OK': 766, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 127 / 0.053 / 0.008 | 110 / 0.056 / 0.009 | 116 / 0.055 / 0.009 |
| 0.10-0.20 | 119 / 0.145 / 0.067 | 122 / 0.146 / 0.066 | 125 / 0.147 / 0.072 |
| 0.20-0.30 | 96 / 0.250 / 0.208 | 85 / 0.251 / 0.176 | 91 / 0.253 / 0.176 |
| 0.30-0.40 | 73 / 0.349 / 0.288 | 75 / 0.350 / 0.253 | 73 / 0.350 / 0.260 |
| 0.40-0.50 | 79 / 0.451 / 0.329 | 71 / 0.444 / 0.324 | 78 / 0.447 / 0.359 |
| 0.50-0.60 | 75 / 0.548 / 0.520 | 70 / 0.552 / 0.386 | 77 / 0.551 / 0.481 |
| 0.60-0.70 | 44 / 0.646 / 0.523 | 62 / 0.648 / 0.532 | 55 / 0.650 / 0.527 |
| 0.70-0.80 | 48 / 0.756 / 0.771 | 51 / 0.750 / 0.745 | 45 / 0.754 / 0.778 |
| 0.80-0.90 | 39 / 0.855 / 0.923 | 40 / 0.843 / 0.850 | 40 / 0.851 / 0.925 |
| 0.90-1.00 | 76 / 0.957 / 1.000 | 90 / 0.956 / 0.989 | 76 / 0.955 / 1.000 |

## Contract pricing — T-6h (854 contracts, 11 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 854 | 0.1310 | 0.4046 | 0.412 | 0.381 | 854 | 0.1310 | 0.1313 | 0.1333 |
| DATA_ONLY | 854 | 0.1339 | 0.4119 | 0.435 | 0.381 | 854 | 0.1339 | 0.1313 | 0.1333 |
| HYBRID_30 | 854 | 0.1296 | 0.4015 | 0.415 | 0.381 | 854 | 0.1296 | 0.1313 | 0.1333 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 854 | 11 | 0.00288 | [-0.01667, 0.02283] | 0.00288 | [-0.01667, 0.02283] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 854 | 11 | -0.00139 | [-0.00660, 0.00327] | -0.00139 | [-0.00660, 0.00327] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 854 | 11 | -0.00426 | [-0.02013, 0.01080] | -0.00426 | [-0.02013, 0.01080] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 854 | 11 | - | - | -0.00032 | [-0.00289, 0.00206] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 844 | 11 | - | - | -0.00072 | [-0.00340, 0.00183] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 854 | 11 | - | - | 0.00255 | [-0.01809, 0.02439] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 844 | 11 | - | - | 0.00219 | [-0.01919, 0.02462] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 854 | 11 | - | - | -0.00171 | [-0.00870, 0.00446] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 844 | 11 | - | - | -0.00212 | [-0.00941, 0.00450] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 44, 'GAME_WINNER': 22, 'SPREAD': 279, 'TEAM_TOTAL': 300, 'TOTAL': 209}; settlement: {'SETTLED': 854}; close: {'OK': 844, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 135 / 0.053 / 0.007 | 123 / 0.055 / 0.000 | 134 / 0.053 / 0.007 |
| 0.10-0.20 | 132 / 0.145 / 0.068 | 135 / 0.147 / 0.067 | 132 / 0.146 / 0.091 |
| 0.20-0.30 | 106 / 0.250 / 0.217 | 95 / 0.252 / 0.200 | 106 / 0.252 / 0.160 |
| 0.30-0.40 | 85 / 0.350 / 0.318 | 81 / 0.351 / 0.284 | 82 / 0.350 / 0.293 |
| 0.40-0.50 | 88 / 0.447 / 0.375 | 77 / 0.445 / 0.338 | 89 / 0.447 / 0.360 |
| 0.50-0.60 | 81 / 0.547 / 0.506 | 80 / 0.553 / 0.450 | 82 / 0.549 / 0.561 |
| 0.60-0.70 | 56 / 0.645 / 0.589 | 70 / 0.649 / 0.557 | 58 / 0.651 / 0.603 |
| 0.70-0.80 | 46 / 0.754 / 0.783 | 51 / 0.751 / 0.745 | 43 / 0.758 / 0.791 |
| 0.80-0.90 | 47 / 0.852 / 0.936 | 48 / 0.847 / 0.875 | 45 / 0.852 / 0.911 |
| 0.90-1.00 | 78 / 0.956 / 1.000 | 94 / 0.958 / 0.989 | 83 / 0.956 / 1.000 |

## Contract pricing — T-90m (854 contracts, 11 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 854 | 0.1313 | 0.4050 | 0.411 | 0.381 | 854 | 0.1313 | 0.1313 | 0.1333 |
| DATA_ONLY | 854 | 0.1341 | 0.4122 | 0.436 | 0.381 | 854 | 0.1341 | 0.1313 | 0.1333 |
| HYBRID_30 | 854 | 0.1333 | 0.4103 | 0.418 | 0.381 | 854 | 0.1333 | 0.1313 | 0.1333 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 854 | 11 | 0.00272 | [-0.01803, 0.02435] | 0.00272 | [-0.01803, 0.02435] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 854 | 11 | 0.00198 | [-0.00463, 0.00842] | 0.00198 | [-0.00463, 0.00842] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 854 | 11 | -0.00075 | [-0.01667, 0.01463] | -0.00075 | [-0.01667, 0.01463] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 854 | 11 | - | - | -0.00001 | [-0.00163, 0.00126] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 844 | 11 | - | - | -0.00040 | [-0.00197, 0.00093] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 854 | 11 | - | - | 0.00271 | [-0.01850, 0.02502] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 844 | 11 | - | - | 0.00235 | [-0.01908, 0.02499] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 854 | 11 | - | - | 0.00196 | [-0.00440, 0.00902] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 844 | 11 | - | - | 0.00160 | [-0.00483, 0.00865] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 44, 'GAME_WINNER': 22, 'SPREAD': 279, 'TEAM_TOTAL': 300, 'TOTAL': 209}; settlement: {'SETTLED': 854}; close: {'OK': 844, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 139 / 0.054 / 0.007 | 126 / 0.056 / 0.008 | 131 / 0.054 / 0.008 |
| 0.10-0.20 | 133 / 0.146 / 0.053 | 133 / 0.148 / 0.060 | 134 / 0.146 / 0.090 |
| 0.20-0.30 | 103 / 0.250 / 0.243 | 93 / 0.252 / 0.204 | 101 / 0.251 / 0.168 |
| 0.30-0.40 | 88 / 0.351 / 0.307 | 82 / 0.351 / 0.280 | 84 / 0.350 / 0.333 |
| 0.40-0.50 | 82 / 0.449 / 0.366 | 76 / 0.444 / 0.342 | 90 / 0.451 / 0.367 |
| 0.50-0.60 | 88 / 0.548 / 0.545 | 81 / 0.552 / 0.457 | 85 / 0.550 / 0.494 |
| 0.60-0.70 | 48 / 0.650 / 0.583 | 66 / 0.647 / 0.530 | 59 / 0.654 / 0.593 |
| 0.70-0.80 | 46 / 0.755 / 0.783 | 54 / 0.746 / 0.759 | 41 / 0.757 / 0.780 |
| 0.80-0.90 | 46 / 0.851 / 0.913 | 47 / 0.844 / 0.851 | 47 / 0.850 / 0.915 |
| 0.90-1.00 | 81 / 0.956 / 1.000 | 96 / 0.957 / 0.990 | 82 / 0.955 / 1.000 |

## Contract pricing — T-30m (854 contracts, 11 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 854 | 0.1327 | 0.4082 | 0.410 | 0.381 | 854 | 0.1327 | 0.1313 | 0.1333 |
| DATA_ONLY | 854 | 0.1337 | 0.4115 | 0.436 | 0.381 | 854 | 0.1337 | 0.1313 | 0.1333 |
| HYBRID_30 | 854 | 0.1320 | 0.4074 | 0.418 | 0.381 | 854 | 0.1320 | 0.1313 | 0.1333 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 854 | 11 | 0.00108 | [-0.01985, 0.02277] | 0.00108 | [-0.01985, 0.02277] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 854 | 11 | -0.00064 | [-0.00651, 0.00534] | -0.00064 | [-0.00651, 0.00534] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 854 | 11 | -0.00173 | [-0.01751, 0.01366] | -0.00173 | [-0.01751, 0.01366] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 854 | 11 | - | - | 0.00134 | [-0.00001, 0.00266] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 844 | 11 | - | - | 0.00094 | [-0.00039, 0.00227] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 854 | 11 | - | - | 0.00242 | [-0.01898, 0.02426] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 844 | 11 | - | - | 0.00203 | [-0.01957, 0.02433] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 854 | 11 | - | - | 0.00070 | [-0.00561, 0.00718] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 844 | 11 | - | - | 0.00029 | [-0.00601, 0.00706] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 44, 'GAME_WINNER': 22, 'SPREAD': 279, 'TEAM_TOTAL': 300, 'TOTAL': 209}; settlement: {'SETTLED': 854}; close: {'OK': 844, 'OK_STALE': 10}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 135 / 0.053 / 0.007 | 124 / 0.055 / 0.008 | 133 / 0.054 / 0.008 |
| 0.10-0.20 | 137 / 0.144 / 0.058 | 133 / 0.147 / 0.060 | 132 / 0.146 / 0.091 |
| 0.20-0.30 | 104 / 0.251 / 0.250 | 94 / 0.252 / 0.202 | 100 / 0.250 / 0.170 |
| 0.30-0.40 | 87 / 0.353 / 0.299 | 83 / 0.351 / 0.265 | 86 / 0.351 / 0.291 |
| 0.40-0.50 | 83 / 0.450 / 0.386 | 77 / 0.446 / 0.364 | 84 / 0.449 / 0.381 |
| 0.50-0.60 | 88 / 0.547 / 0.523 | 79 / 0.553 / 0.430 | 88 / 0.546 / 0.500 |
| 0.60-0.70 | 48 / 0.650 / 0.583 | 67 / 0.646 / 0.537 | 58 / 0.651 / 0.621 |
| 0.70-0.80 | 49 / 0.757 / 0.776 | 53 / 0.746 / 0.774 | 44 / 0.756 / 0.750 |
| 0.80-0.90 | 43 / 0.853 / 0.930 | 48 / 0.844 / 0.854 | 45 / 0.847 / 0.911 |
| 0.90-1.00 | 80 / 0.955 / 1.000 | 96 / 0.957 / 0.990 | 84 / 0.953 / 1.000 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 10 | 2 | 2 | 0 | 6 | 0 | 1.000 [0.342, 1.000] | 0.500 | 0.500 | 0.19 |
| T-24h | DATA_ONLY | total | 10 | 3 | 2 | 2 | 3 | 0 | 0.500 [0.150, 0.850] | 0.286 | 0.143 | -0.07 |
| T-24h | HYBRID_30 (derived) | margin | 10 | 6 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.750 | 0.750 | 0.12 |
| T-24h | HYBRID_30 (derived) | total | 10 | 4 | 2 | 2 | 2 | 0 | 0.500 [0.150, 0.850] | 0.333 | 0.333 | -0.08 |
| T-6h | DATA_ONLY | margin | 11 | 2 | 1 | 1 | 7 | 0 | 0.500 [0.095, 0.905] | 0.444 | 0.444 | 0.06 |
| T-6h | DATA_ONLY | total | 11 | 3 | 1 | 4 | 3 | 0 | 0.200 [0.036, 0.624] | 0.375 | 0.250 | -0.25 |
| T-6h | HYBRID_30 (derived) | margin | 11 | 8 | 0 | 1 | 2 | 0 | 0.000 [0.000, 0.793] | 0.667 | 0.667 | -0.17 |
| T-6h | HYBRID_30 (derived) | total | 11 | 6 | 1 | 3 | 1 | 0 | 0.250 [0.046, 0.699] | 0.400 | 0.400 | -0.30 |
| T-90m | DATA_ONLY | margin | 11 | 2 | 2 | 0 | 7 | 0 | 1.000 [0.342, 1.000] | 0.444 | 0.444 | 0.17 |
| T-90m | DATA_ONLY | total | 11 | 3 | 0 | 3 | 5 | 0 | 0.000 [0.000, 0.561] | 0.250 | 0.250 | -0.31 |
| T-90m | HYBRID_30 (derived) | margin | 11 | 7 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.750 | 0.750 | 0.12 |
| T-90m | HYBRID_30 (derived) | total | 11 | 6 | 0 | 2 | 3 | 0 | 0.000 [0.000, 0.658] | 0.200 | 0.200 | -0.30 |
| T-30m | DATA_ONLY | margin | 11 | 1 | 2 | 0 | 8 | 0 | 1.000 [0.342, 1.000] | 0.500 | 0.500 | 0.15 |
| T-30m | DATA_ONLY | total | 11 | 3 | 0 | 1 | 7 | 0 | 0.000 [0.000, 0.793] | 0.250 | 0.250 | -0.06 |
| T-30m | HYBRID_30 (derived) | margin | 11 | 7 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.750 | 0.750 | 0.12 |
| T-30m | HYBRID_30 (derived) | total | 11 | 6 | 0 | 1 | 4 | 0 | 0.000 [0.000, 0.793] | 0.200 | 0.200 | -0.10 |
| latest_pregame | DATA_ONLY | margin | 11 | 1 | 2 | 0 | 8 | 0 | 1.000 [0.342, 1.000] | 0.500 | 0.500 | 0.15 |
| latest_pregame | DATA_ONLY | total | 11 | 3 | 0 | 1 | 7 | 0 | 0.000 [0.000, 0.793] | 0.250 | 0.250 | -0.06 |
| latest_pregame | HYBRID_30 (derived) | margin | 11 | 7 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.750 | 0.750 | 0.12 |
| latest_pregame | HYBRID_30 (derived) | total | 11 | 6 | 0 | 1 | 4 | 0 | 0.000 [0.000, 0.793] | 0.200 | 0.200 | -0.10 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 1 | 0 | 0 | 1 | 0 | - |
| margin | 1-2 | 3 | 0 | 0 | 3 | 0 | - |
| margin | 2-3 | 2 | 0 | 0 | 2 | 0 | - |
| margin | 3-5 | 3 | 2 | 0 | 1 | 0 | 1.000 |
| margin | >5 | 2 | 0 | 0 | 2 | 0 | - |
| total | <=1 | 3 | 0 | 1 | 2 | 0 | 0.000 |
| total | 1-2 | 0 | 0 | 0 | 0 | 0 | - |
| total | 2-3 | 2 | 0 | 0 | 2 | 0 | - |
| total | 3-5 | 4 | 0 | 0 | 4 | 0 | - |
| total | >5 | 2 | 0 | 1 | 1 | 0 | 0.000 |

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

Expected games 16 · eligible 16 · diagnosed 1 · excluded 15 · canonical projection units 63 (63 with a box-score value) · eligible units 1055, eligible but undiagnosed 992

| game | included | diagnosed units | raw records | eligible units | undiagnosed | rule | exclusion reason |
|---|---|---|---|---|---|---|---|
| 2026_04_ARI_NYG | NO | 0 | 0 | 62 | 62 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_ATL_NO | NO | 0 | 0 | 62 | 62 | — | game not final (or no kickoff) when the report was built |
| 2026_04_DAL_HOU | NO | 0 | 0 | 70 | 70 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_DEN_SF | NO | 0 | 0 | 68 | 68 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_DET_CAR | NO | 0 | 0 | 62 | 62 | — | game not final (or no kickoff) when the report was built |
| 2026_04_GB_TB | NO | 0 | 0 | 65 | 65 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_IND_WAS | NO | 0 | 0 | 70 | 70 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_JAX_CIN | NO | 0 | 0 | 73 | 73 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_KC_LV | NO | 0 | 0 | 67 | 67 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_LAC_SEA | NO | 0 | 0 | 72 | 72 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_LA_PHI | NO | 0 | 0 | 62 | 62 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_MIA_MIN | NO | 0 | 0 | 65 | 65 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_NE_BUF | NO | 0 | 0 | 69 | 69 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_NYJ_CHI | NO | 0 | 0 | 60 | 60 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_PIT_CLE | yes | 63 | 63 | 63 | 0 | autopsy-1.1.0 |  |
| 2026_04_TEN_BAL | NO | 0 | 0 | 65 | 65 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |

