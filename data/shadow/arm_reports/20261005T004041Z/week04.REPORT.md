# Three-arm game-centre experiment — 2026 week 4

> **INSUFFICIENT EVIDENCE.** 14 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 1125 | 14 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 13 | 13 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 14 | 14 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 14 | 14 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 14 | 14 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 14 | 14 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_DEN_SF | 2026-10-04T20:25 | 40 | CURRENT | 2.50 | 48.00 | 10 | 38 | 2.5/48.0 (kalshi_implied) | 2.5/48.5 (OK) |
|  |  |  | DATA_ONLY | 3.98 | 47.63 |  |  |  |  |
|  |  |  | HYBRID_30 | 2.94 | 47.89 |  |  |  |  |
| 2026_04_KC_LV | 2026-10-04T20:25 | 40 | CURRENT | -4.50 | 47.50 | -3 | 57 | -4.5/47.5 (kalshi_implied) | -5.5/47.5 (OK) |
|  |  |  | DATA_ONLY | -5.46 | 43.83 |  |  |  |  |
|  |  |  | HYBRID_30 | -4.79 | 46.40 |  |  |  |  |
| 2026_04_LAC_SEA | 2026-10-04T20:25 | 40 | CURRENT | 7.00 | 44.00 | 7 | 53 | 7.0/44.0 (kalshi_implied) | 7.5/42.0 (OK) |
|  |  |  | DATA_ONLY | 12.45 | 41.32 |  |  |  |  |
|  |  |  | HYBRID_30 | 8.63 | 43.20 |  |  |  |  |

## Game-centre accuracy — latest_pregame (14 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 14 | 1 | 6.07 | 7.36 | 1.00 | 9.00 | 10.21 | -1.29 | 0.203 |
| DATA_ONLY | 14 | 1 | 5.87 | 6.99 | 1.79 | 10.42 | 11.46 | 0.13 | 0.184 |
| HYBRID_30 | 14 | 1 | 5.97 | 7.09 | 1.24 | 9.36 | 10.49 | -0.86 | 0.198 |
| market at snapshot | 14 | 1 | 6.07 | 7.36 | 1.00 | 9.00 | 10.21 | -1.29 | - |
| market at close | 14 | 1 | 6.21 | 7.34 | 1.00 | 9.11 | 10.33 | -1.39 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 14 | margin | -0.202 | 0.917 | [-1.999, 1.595] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 14 | total | 1.419 | 0.810 | [-0.168, 3.007] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | margin | -0.101 | 0.276 | [-0.642, 0.440] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | total | 0.355 | 0.261 | [-0.156, 0.867] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | margin | 0.101 | 0.645 | [-1.163, 1.366] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | total | -1.064 | 0.563 | [-2.167, 0.039] | 0.714 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 14 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 14 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | margin | -0.202 | 0.917 | [-1.999, 1.595] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | total | 1.419 | 0.810 | [-0.168, 3.007] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | margin | -0.101 | 0.276 | [-0.642, 0.440] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | total | 0.355 | 0.261 | [-0.156, 0.867] | 0.357 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | margin | -0.143 | 0.110 | [-0.359, 0.073] | 0.214 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | total | -0.107 | 0.159 | [-0.418, 0.204] | 0.143 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | margin | -0.345 | 0.866 | [-2.043, 1.353] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | total | 1.312 | 0.824 | [-0.302, 2.926] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | margin | -0.244 | 0.238 | [-0.711, 0.223] | 0.643 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | total | 0.248 | 0.302 | [-0.344, 0.840] | 0.429 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 14 | 4 | 0 | 10 | 0 | 1.000 | 0.429 | 2.80 |
| DATA_ONLY | total | 14 | 1 | 3 | 10 | 0 | 0.250 | 0.286 | 2.88 |
| HYBRID_30 | margin | 14 | 4 | 0 | 10 | 0 | 1.000 | 0.500 | 0.84 |
| HYBRID_30 | total | 14 | 1 | 3 | 10 | 0 | 0.250 | 0.357 | 0.86 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 4.13 | 3.50 | 1.000 |
| DATA_ONLY | margin | 1-2 | 4 | 4.52 | 4.88 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 3 | 3.03 | 5.00 | 1.000 |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.88 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 3 | 13.68 | 12.83 | 1.000 |
| DATA_ONLY | total | 3-5 | 5 | 8.44 | 7.10 | - |
| DATA_ONLY | total | >5 | 2 | 15.67 | 10.25 | 0.000 |
| HYBRID_30 | margin | <=1 | 9 | 5.92 | 5.89 | 1.000 |
| HYBRID_30 | margin | 1-2 | 5 | 6.06 | 6.40 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 8 | 8.91 | 8.94 | 0.333 |
| HYBRID_30 | total | 1-2 | 6 | 9.95 | 9.08 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 14}; DATA_ONLY quality states: {'OK': 14}; close centre status: {'OK': 14}.

## Game-centre accuracy — T-24h (13 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 13 | 1 | 6.08 | 7.43 | 1.46 | 8.81 | 10.01 | -0.50 | 0.194 |
| DATA_ONLY | 13 | 1 | 5.82 | 7.02 | 2.43 | 10.39 | 11.51 | 0.97 | 0.166 |
| HYBRID_30 | 13 | 1 | 5.96 | 7.15 | 1.75 | 9.21 | 10.37 | -0.06 | 0.183 |
| market at snapshot | 13 | 1 | 6.08 | 7.43 | 1.46 | 8.81 | 10.01 | -0.50 | - |
| market at close | 13 | 1 | 6.27 | 7.47 | 1.50 | 8.77 | 10.05 | -0.46 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 13 | margin | -0.257 | 0.967 | [-2.152, 1.639] | 0.462 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 13 | total | 1.586 | 0.783 | [0.051, 3.122] | 0.308 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 13 | margin | -0.120 | 0.291 | [-0.690, 0.450] | 0.538 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 13 | total | 0.400 | 0.261 | [-0.113, 0.912] | 0.308 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 13 | margin | 0.136 | 0.681 | [-1.199, 1.471] | 0.538 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 13 | total | -1.186 | 0.538 | [-2.240, -0.132] | 0.769 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 13 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 13 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 13 | margin | -0.257 | 0.967 | [-2.152, 1.639] | 0.462 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 13 | total | 1.586 | 0.783 | [0.051, 3.122] | 0.308 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 13 | margin | -0.120 | 0.291 | [-0.690, 0.450] | 0.538 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 13 | total | 0.400 | 0.261 | [-0.113, 0.912] | 0.308 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 13 | margin | -0.192 | 0.121 | [-0.429, 0.044] | 0.308 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 13 | total | 0.038 | 0.183 | [-0.320, 0.397] | 0.231 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 13 | margin | -0.449 | 0.929 | [-2.270, 1.372] | 0.538 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 13 | total | 1.625 | 0.823 | [0.011, 3.238] | 0.231 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 13 | margin | -0.313 | 0.268 | [-0.838, 0.212] | 0.769 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 13 | total | 0.438 | 0.324 | [-0.197, 1.074] | 0.308 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 13 | 4 | 1 | 8 | 0 | 0.800 | 0.462 | 2.90 |
| DATA_ONLY | total | 13 | 4 | 3 | 6 | 0 | 0.571 | 0.308 | 2.69 |
| HYBRID_30 | margin | 13 | 4 | 1 | 8 | 0 | 0.800 | 0.538 | 0.87 |
| HYBRID_30 | total | 13 | 4 | 3 | 6 | 0 | 0.571 | 0.308 | 0.81 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 4.29 | 4.00 | 0.667 |
| DATA_ONLY | margin | 1-2 | 2 | 3.48 | 4.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 4 | 6.63 | 4.50 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 5 | 8.59 | 8.50 | 0.667 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 1 | 18.62 | 16.00 | - |
| DATA_ONLY | total | 3-5 | 6 | 10.09 | 8.17 | 0.500 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.00 | - |
| HYBRID_30 | margin | <=1 | 8 | 5.85 | 5.81 | 0.750 |
| HYBRID_30 | margin | 1-2 | 5 | 6.13 | 6.50 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 6 | 9.90 | 9.75 | 0.667 |
| HYBRID_30 | total | 1-2 | 7 | 8.61 | 8.00 | 0.500 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 13}; DATA_ONLY quality states: {'OK': 13}; close centre status: {'OK': 13}.

## Game-centre accuracy — T-6h (14 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 14 | 1 | 5.93 | 7.20 | 0.93 | 9.14 | 10.26 | -1.29 | 0.201 |
| DATA_ONLY | 14 | 1 | 5.87 | 6.99 | 1.79 | 10.42 | 11.46 | 0.13 | 0.184 |
| HYBRID_30 | 14 | 1 | 5.87 | 6.99 | 1.19 | 9.46 | 10.54 | -0.86 | 0.188 |
| market at snapshot | 14 | 1 | 5.93 | 7.20 | 0.93 | 9.14 | 10.26 | -1.29 | - |
| market at close | 14 | 1 | 6.21 | 7.34 | 1.00 | 9.11 | 10.33 | -1.39 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 14 | margin | -0.059 | 0.871 | [-1.766, 1.647] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 14 | total | 1.276 | 0.737 | [-0.168, 2.721] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | margin | -0.058 | 0.263 | [-0.573, 0.456] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | total | 0.312 | 0.243 | [-0.164, 0.789] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | margin | 0.001 | 0.613 | [-1.199, 1.202] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | total | -0.964 | 0.509 | [-1.961, 0.033] | 0.714 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 14 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 14 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | margin | -0.059 | 0.871 | [-1.766, 1.647] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | total | 1.276 | 0.737 | [-0.168, 2.721] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | margin | -0.058 | 0.263 | [-0.573, 0.456] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | total | 0.312 | 0.243 | [-0.164, 0.789] | 0.357 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | margin | -0.286 | 0.114 | [-0.509, -0.063] | 0.357 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | total | 0.036 | 0.123 | [-0.204, 0.276] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | margin | -0.345 | 0.866 | [-2.043, 1.353] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | total | 1.312 | 0.824 | [-0.302, 2.926] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | margin | -0.344 | 0.272 | [-0.877, 0.189] | 0.714 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | total | 0.348 | 0.324 | [-0.288, 0.984] | 0.429 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 14 | 3 | 2 | 9 | 0 | 0.600 | 0.429 | 2.66 |
| DATA_ONLY | total | 14 | 2 | 6 | 6 | 0 | 0.250 | 0.357 | 2.67 |
| HYBRID_30 | margin | 14 | 3 | 2 | 9 | 0 | 0.600 | 0.500 | 0.80 |
| HYBRID_30 | total | 14 | 2 | 6 | 6 | 0 | 0.250 | 0.357 | 0.80 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 4.29 | 3.83 | 0.667 |
| DATA_ONLY | margin | 1-2 | 3 | 4.49 | 4.50 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 4 | 6.63 | 4.38 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.25 | 0.000 |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.75 | 0.000 |
| DATA_ONLY | total | 1-2 | 1 | 11.68 | 10.50 | 1.000 |
| DATA_ONLY | total | 2-3 | 2 | 14.68 | 14.75 | - |
| DATA_ONLY | total | 3-5 | 6 | 10.09 | 8.25 | 0.200 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 10 | 6.12 | 6.15 | 0.750 |
| HYBRID_30 | margin | 1-2 | 4 | 5.24 | 5.38 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 9 | 9.37 | 9.11 | 0.250 |
| HYBRID_30 | total | 1-2 | 5 | 9.61 | 9.20 | 0.250 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 14}; DATA_ONLY quality states: {'OK': 14}; close centre status: {'OK': 14}.

## Game-centre accuracy — T-90m (14 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 14 | 1 | 6.04 | 7.31 | 0.96 | 9.11 | 10.31 | -1.25 | 0.204 |
| DATA_ONLY | 14 | 1 | 5.87 | 6.99 | 1.79 | 10.42 | 11.46 | 0.13 | 0.184 |
| HYBRID_30 | 14 | 1 | 5.95 | 7.06 | 1.21 | 9.43 | 10.57 | -0.84 | 0.199 |
| market at snapshot | 14 | 1 | 6.04 | 7.31 | 0.96 | 9.11 | 10.31 | -1.25 | - |
| market at close | 14 | 1 | 6.21 | 7.34 | 1.00 | 9.11 | 10.33 | -1.39 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 14 | margin | -0.167 | 0.900 | [-1.931, 1.597] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 14 | total | 1.312 | 0.754 | [-0.166, 2.790] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | margin | -0.090 | 0.271 | [-0.621, 0.441] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | total | 0.323 | 0.245 | [-0.157, 0.803] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | margin | 0.076 | 0.633 | [-1.165, 1.318] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | total | -0.989 | 0.524 | [-2.016, 0.038] | 0.714 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 14 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 14 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | margin | -0.167 | 0.900 | [-1.931, 1.597] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | total | 1.312 | 0.754 | [-0.166, 2.790] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | margin | -0.090 | 0.271 | [-0.621, 0.441] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | total | 0.323 | 0.245 | [-0.157, 0.803] | 0.357 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | margin | -0.179 | 0.113 | [-0.399, 0.042] | 0.286 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | total | 0.000 | 0.128 | [-0.252, 0.252] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | margin | -0.345 | 0.866 | [-2.043, 1.353] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | total | 1.312 | 0.824 | [-0.302, 2.926] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | margin | -0.269 | 0.252 | [-0.762, 0.225] | 0.714 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | total | 0.323 | 0.323 | [-0.310, 0.956] | 0.429 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 14 | 4 | 1 | 9 | 0 | 0.800 | 0.429 | 2.77 |
| DATA_ONLY | total | 14 | 1 | 5 | 8 | 0 | 0.167 | 0.286 | 2.63 |
| HYBRID_30 | margin | 14 | 4 | 1 | 9 | 0 | 0.800 | 0.500 | 0.83 |
| HYBRID_30 | total | 14 | 1 | 5 | 8 | 0 | 0.167 | 0.357 | 0.79 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 4.29 | 4.00 | 0.667 |
| DATA_ONLY | margin | 1-2 | 3 | 4.49 | 4.50 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 4 | 6.63 | 4.50 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.88 | 0.000 |
| DATA_ONLY | total | 1-2 | 2 | 11.22 | 11.50 | 0.500 |
| DATA_ONLY | total | 2-3 | 1 | 18.62 | 16.00 | - |
| DATA_ONLY | total | 3-5 | 6 | 10.09 | 8.25 | 0.000 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 9 | 5.84 | 5.78 | 0.750 |
| HYBRID_30 | margin | 1-2 | 5 | 6.13 | 6.50 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 8 | 8.95 | 9.00 | 0.250 |
| HYBRID_30 | total | 1-2 | 6 | 10.07 | 9.25 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 14}; DATA_ONLY quality states: {'OK': 14}; close centre status: {'OK': 14}.

## Game-centre accuracy — T-30m (14 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 14 | 1 | 6.07 | 7.36 | 1.00 | 9.00 | 10.21 | -1.29 | 0.203 |
| DATA_ONLY | 14 | 1 | 5.87 | 6.99 | 1.79 | 10.42 | 11.46 | 0.13 | 0.184 |
| HYBRID_30 | 14 | 1 | 5.97 | 7.09 | 1.24 | 9.36 | 10.49 | -0.86 | 0.198 |
| market at snapshot | 14 | 1 | 6.07 | 7.36 | 1.00 | 9.00 | 10.21 | -1.29 | - |
| market at close | 14 | 1 | 6.21 | 7.34 | 1.00 | 9.11 | 10.33 | -1.39 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 14 | margin | -0.202 | 0.917 | [-1.999, 1.595] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 14 | total | 1.419 | 0.810 | [-0.168, 3.007] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | margin | -0.101 | 0.276 | [-0.642, 0.440] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | total | 0.355 | 0.261 | [-0.156, 0.867] | 0.357 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | margin | 0.101 | 0.645 | [-1.163, 1.366] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | total | -1.064 | 0.563 | [-2.167, 0.039] | 0.714 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 14 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 14 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | margin | -0.202 | 0.917 | [-1.999, 1.595] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | total | 1.419 | 0.810 | [-0.168, 3.007] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | margin | -0.101 | 0.276 | [-0.642, 0.440] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | total | 0.355 | 0.261 | [-0.156, 0.867] | 0.357 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | margin | -0.143 | 0.110 | [-0.359, 0.073] | 0.214 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | total | -0.107 | 0.159 | [-0.418, 0.204] | 0.143 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | margin | -0.345 | 0.866 | [-2.043, 1.353] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | total | 1.312 | 0.824 | [-0.302, 2.926] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | margin | -0.244 | 0.238 | [-0.711, 0.223] | 0.643 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | total | 0.248 | 0.302 | [-0.344, 0.840] | 0.429 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 14 | 4 | 0 | 10 | 0 | 1.000 | 0.429 | 2.80 |
| DATA_ONLY | total | 14 | 1 | 3 | 10 | 0 | 0.250 | 0.286 | 2.88 |
| HYBRID_30 | margin | 14 | 4 | 0 | 10 | 0 | 1.000 | 0.500 | 0.84 |
| HYBRID_30 | total | 14 | 1 | 3 | 10 | 0 | 0.250 | 0.357 | 0.86 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 4.13 | 3.50 | 1.000 |
| DATA_ONLY | margin | 1-2 | 4 | 4.52 | 4.88 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 3 | 7.03 | 5.83 | 1.000 |
| DATA_ONLY | margin | >5 | 3 | 3.03 | 5.00 | 1.000 |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.88 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 3 | 13.68 | 12.83 | 1.000 |
| DATA_ONLY | total | 3-5 | 5 | 8.44 | 7.10 | - |
| DATA_ONLY | total | >5 | 2 | 15.67 | 10.25 | 0.000 |
| HYBRID_30 | margin | <=1 | 9 | 5.92 | 5.89 | 1.000 |
| HYBRID_30 | margin | 1-2 | 5 | 6.06 | 6.40 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 8 | 8.91 | 8.94 | 0.333 |
| HYBRID_30 | total | 1-2 | 6 | 9.95 | 9.08 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 14}; DATA_ONLY quality states: {'OK': 14}; close centre status: {'OK': 14}.

## Contract pricing — latest_pregame (1087 contracts, 14 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1087 | 0.1292 | 0.3997 | 0.415 | 0.395 | 1087 | 0.1292 | 0.1281 | 0.1300 |
| DATA_ONLY | 1087 | 0.1317 | 0.4057 | 0.433 | 0.395 | 1087 | 0.1317 | 0.1281 | 0.1300 |
| HYBRID_30 | 1087 | 0.1278 | 0.3973 | 0.419 | 0.395 | 1087 | 0.1278 | 0.1281 | 0.1300 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1087 | 14 | 0.00250 | [-0.01598, 0.01964] | 0.00250 | [-0.01598, 0.01964] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1087 | 14 | -0.00143 | [-0.00694, 0.00412] | -0.00143 | [-0.00694, 0.00412] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1087 | 14 | -0.00393 | [-0.01601, 0.00990] | -0.00393 | [-0.01601, 0.00990] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1087 | 14 | - | - | 0.00108 | [-0.00016, 0.00248] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1075 | 14 | - | - | 0.00060 | [-0.00080, 0.00214] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1087 | 14 | - | - | 0.00358 | [-0.01551, 0.02071] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1075 | 14 | - | - | 0.00314 | [-0.01612, 0.02022] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1087 | 14 | - | - | -0.00035 | [-0.00637, 0.00518] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1075 | 14 | - | - | -0.00084 | [-0.00674, 0.00479] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 56, 'GAME_WINNER': 28, 'SPREAD': 356, 'TEAM_TOTAL': 381, 'TOTAL': 266}; settlement: {'SETTLED': 1087}; close: {'OK': 1075, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 168 / 0.054 / 0.006 | 165 / 0.054 / 0.006 | 168 / 0.055 / 0.006 |
| 0.10-0.20 | 175 / 0.144 / 0.046 | 168 / 0.147 / 0.054 | 170 / 0.146 / 0.071 |
| 0.20-0.30 | 133 / 0.250 / 0.233 | 118 / 0.251 / 0.220 | 127 / 0.250 / 0.165 |
| 0.30-0.40 | 107 / 0.352 / 0.327 | 104 / 0.351 / 0.298 | 106 / 0.351 / 0.330 |
| 0.40-0.50 | 104 / 0.449 / 0.433 | 99 / 0.446 / 0.424 | 107 / 0.449 / 0.411 |
| 0.50-0.60 | 113 / 0.547 / 0.549 | 98 / 0.551 / 0.449 | 113 / 0.547 / 0.531 |
| 0.60-0.70 | 63 / 0.650 / 0.635 | 87 / 0.647 / 0.575 | 74 / 0.652 / 0.689 |
| 0.70-0.80 | 63 / 0.756 / 0.794 | 68 / 0.747 / 0.794 | 55 / 0.754 / 0.782 |
| 0.80-0.90 | 55 / 0.854 / 0.927 | 62 / 0.845 / 0.887 | 58 / 0.847 / 0.914 |
| 0.90-1.00 | 106 / 0.957 / 1.000 | 118 / 0.956 / 0.992 | 109 / 0.953 / 1.000 |

## Contract pricing — T-24h (1009 contracts, 13 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1009 | 0.1269 | 0.3946 | 0.416 | 0.388 | 1009 | 0.1269 | 0.1278 | 0.1286 |
| DATA_ONLY | 1009 | 0.1311 | 0.4048 | 0.434 | 0.388 | 1009 | 0.1311 | 0.1278 | 0.1286 |
| HYBRID_30 | 1009 | 0.1270 | 0.3949 | 0.420 | 0.388 | 1009 | 0.1270 | 0.1278 | 0.1286 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1009 | 13 | 0.00422 | [-0.01732, 0.02287] | 0.00422 | [-0.01732, 0.02287] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1009 | 13 | 0.00007 | [-0.00813, 0.00677] | 0.00007 | [-0.00813, 0.00677] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1009 | 13 | -0.00415 | [-0.01708, 0.00978] | -0.00415 | [-0.01708, 0.00978] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1009 | 13 | - | - | -0.00087 | [-0.00234, 0.00046] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 997 | 13 | - | - | -0.00013 | [-0.00165, 0.00161] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1009 | 13 | - | - | 0.00335 | [-0.01777, 0.02112] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 997 | 13 | - | - | 0.00414 | [-0.01727, 0.02259] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1009 | 13 | - | - | -0.00080 | [-0.00882, 0.00551] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 997 | 13 | - | - | -0.00006 | [-0.00870, 0.00681] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 52, 'GAME_WINNER': 26, 'SPREAD': 331, 'TEAM_TOTAL': 353, 'TOTAL': 247}; settlement: {'SETTLED': 1009}; close: {'OK': 997, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 159 / 0.054 / 0.006 | 151 / 0.054 / 0.007 | 152 / 0.054 / 0.007 |
| 0.10-0.20 | 157 / 0.143 / 0.051 | 155 / 0.145 / 0.052 | 165 / 0.147 / 0.055 |
| 0.20-0.30 | 126 / 0.249 / 0.198 | 111 / 0.249 / 0.207 | 116 / 0.252 / 0.198 |
| 0.30-0.40 | 96 / 0.350 / 0.323 | 95 / 0.350 / 0.295 | 96 / 0.350 / 0.292 |
| 0.40-0.50 | 102 / 0.453 / 0.382 | 93 / 0.444 / 0.387 | 104 / 0.448 / 0.404 |
| 0.50-0.60 | 97 / 0.548 / 0.557 | 90 / 0.551 / 0.422 | 96 / 0.552 / 0.521 |
| 0.60-0.70 | 59 / 0.646 / 0.627 | 82 / 0.649 / 0.573 | 71 / 0.650 / 0.606 |
| 0.70-0.80 | 62 / 0.755 / 0.790 | 66 / 0.750 / 0.773 | 56 / 0.752 / 0.821 |
| 0.80-0.90 | 50 / 0.855 / 0.920 | 55 / 0.846 / 0.891 | 54 / 0.850 / 0.926 |
| 0.90-1.00 | 101 / 0.957 / 1.000 | 111 / 0.956 / 0.991 | 99 / 0.956 / 1.000 |

## Contract pricing — T-6h (1087 contracts, 14 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1087 | 0.1280 | 0.3972 | 0.415 | 0.395 | 1087 | 0.1280 | 0.1281 | 0.1300 |
| DATA_ONLY | 1087 | 0.1318 | 0.4059 | 0.432 | 0.395 | 1087 | 0.1318 | 0.1281 | 0.1300 |
| HYBRID_30 | 1087 | 0.1277 | 0.3958 | 0.414 | 0.395 | 1087 | 0.1277 | 0.1281 | 0.1300 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1087 | 14 | 0.00377 | [-0.01384, 0.01988] | 0.00377 | [-0.01384, 0.01988] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1087 | 14 | -0.00032 | [-0.00613, 0.00501] | -0.00032 | [-0.00613, 0.00501] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1087 | 14 | -0.00409 | [-0.01618, 0.00843] | -0.00409 | [-0.01618, 0.00843] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1087 | 14 | - | - | -0.00013 | [-0.00224, 0.00163] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1075 | 14 | - | - | -0.00059 | [-0.00274, 0.00131] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1087 | 14 | - | - | 0.00364 | [-0.01490, 0.02086] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1075 | 14 | - | - | 0.00322 | [-0.01597, 0.02041] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1087 | 14 | - | - | -0.00045 | [-0.00749, 0.00581] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1075 | 14 | - | - | -0.00091 | [-0.00804, 0.00530] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 56, 'GAME_WINNER': 28, 'SPREAD': 356, 'TEAM_TOTAL': 381, 'TOTAL': 266}; settlement: {'SETTLED': 1087}; close: {'OK': 1075, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 169 / 0.054 / 0.006 | 164 / 0.054 / 0.000 | 176 / 0.053 / 0.006 |
| 0.10-0.20 | 169 / 0.145 / 0.053 | 169 / 0.146 / 0.059 | 168 / 0.147 / 0.071 |
| 0.20-0.30 | 137 / 0.250 / 0.204 | 120 / 0.251 / 0.217 | 133 / 0.252 / 0.188 |
| 0.30-0.40 | 104 / 0.352 / 0.365 | 101 / 0.351 / 0.317 | 101 / 0.348 / 0.337 |
| 0.40-0.50 | 107 / 0.448 / 0.411 | 100 / 0.445 / 0.400 | 117 / 0.448 / 0.419 |
| 0.50-0.60 | 106 / 0.546 / 0.528 | 99 / 0.551 / 0.465 | 100 / 0.549 / 0.550 |
| 0.60-0.70 | 72 / 0.645 / 0.639 | 90 / 0.650 / 0.589 | 70 / 0.652 / 0.657 |
| 0.70-0.80 | 60 / 0.752 / 0.800 | 66 / 0.751 / 0.773 | 57 / 0.754 / 0.825 |
| 0.80-0.90 | 61 / 0.852 / 0.934 | 62 / 0.848 / 0.903 | 58 / 0.852 / 0.914 |
| 0.90-1.00 | 102 / 0.958 / 1.000 | 116 / 0.957 / 0.991 | 107 / 0.957 / 1.000 |

## Contract pricing — T-90m (1087 contracts, 14 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1087 | 0.1282 | 0.3976 | 0.415 | 0.395 | 1087 | 0.1282 | 0.1280 | 0.1300 |
| DATA_ONLY | 1087 | 0.1319 | 0.4061 | 0.432 | 0.395 | 1087 | 0.1319 | 0.1280 | 0.1300 |
| HYBRID_30 | 1087 | 0.1301 | 0.4022 | 0.418 | 0.395 | 1087 | 0.1301 | 0.1280 | 0.1300 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1087 | 14 | 0.00367 | [-0.01505, 0.02084] | 0.00367 | [-0.01505, 0.02084] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1087 | 14 | 0.00189 | [-0.00464, 0.00814] | 0.00189 | [-0.00464, 0.00814] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1087 | 14 | -0.00179 | [-0.01343, 0.01175] | -0.00179 | [-0.01343, 0.01175] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1087 | 14 | - | - | 0.00015 | [-0.00117, 0.00145] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1075 | 14 | - | - | -0.00040 | [-0.00189, 0.00106] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1087 | 14 | - | - | 0.00382 | [-0.01521, 0.02128] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1075 | 14 | - | - | 0.00332 | [-0.01605, 0.02049] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1087 | 14 | - | - | 0.00204 | [-0.00424, 0.00794] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1075 | 14 | - | - | 0.00152 | [-0.00482, 0.00757] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 56, 'GAME_WINNER': 28, 'SPREAD': 356, 'TEAM_TOTAL': 381, 'TOTAL': 266}; settlement: {'SETTLED': 1087}; close: {'OK': 1075, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 172 / 0.055 / 0.006 | 167 / 0.054 / 0.006 | 169 / 0.054 / 0.006 |
| 0.10-0.20 | 169 / 0.145 / 0.041 | 167 / 0.147 / 0.054 | 171 / 0.147 / 0.070 |
| 0.20-0.30 | 134 / 0.249 / 0.231 | 118 / 0.251 / 0.220 | 128 / 0.251 / 0.188 |
| 0.30-0.40 | 110 / 0.352 / 0.336 | 102 / 0.351 / 0.314 | 105 / 0.350 / 0.362 |
| 0.40-0.50 | 99 / 0.449 / 0.404 | 99 / 0.444 / 0.404 | 114 / 0.450 / 0.404 |
| 0.50-0.60 | 114 / 0.546 / 0.561 | 100 / 0.551 / 0.470 | 108 / 0.551 / 0.519 |
| 0.60-0.70 | 65 / 0.649 / 0.646 | 86 / 0.648 / 0.570 | 72 / 0.654 / 0.653 |
| 0.70-0.80 | 59 / 0.754 / 0.797 | 69 / 0.748 / 0.783 | 53 / 0.753 / 0.811 |
| 0.80-0.90 | 59 / 0.851 / 0.915 | 61 / 0.845 / 0.885 | 61 / 0.848 / 0.918 |
| 0.90-1.00 | 106 / 0.956 / 1.000 | 118 / 0.956 / 0.992 | 106 / 0.956 / 1.000 |

## Contract pricing — T-30m (1087 contracts, 14 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1087 | 0.1292 | 0.3997 | 0.415 | 0.395 | 1087 | 0.1292 | 0.1281 | 0.1300 |
| DATA_ONLY | 1087 | 0.1317 | 0.4057 | 0.433 | 0.395 | 1087 | 0.1317 | 0.1281 | 0.1300 |
| HYBRID_30 | 1087 | 0.1278 | 0.3973 | 0.419 | 0.395 | 1087 | 0.1278 | 0.1281 | 0.1300 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1087 | 14 | 0.00250 | [-0.01598, 0.01964] | 0.00250 | [-0.01598, 0.01964] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1087 | 14 | -0.00143 | [-0.00694, 0.00412] | -0.00143 | [-0.00694, 0.00412] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1087 | 14 | -0.00393 | [-0.01601, 0.00990] | -0.00393 | [-0.01601, 0.00990] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1087 | 14 | - | - | 0.00108 | [-0.00016, 0.00248] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1075 | 14 | - | - | 0.00060 | [-0.00080, 0.00214] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1087 | 14 | - | - | 0.00358 | [-0.01551, 0.02071] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1075 | 14 | - | - | 0.00314 | [-0.01612, 0.02022] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1087 | 14 | - | - | -0.00035 | [-0.00637, 0.00518] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1075 | 14 | - | - | -0.00084 | [-0.00674, 0.00479] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 56, 'GAME_WINNER': 28, 'SPREAD': 356, 'TEAM_TOTAL': 381, 'TOTAL': 266}; settlement: {'SETTLED': 1087}; close: {'OK': 1075, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 168 / 0.054 / 0.006 | 165 / 0.054 / 0.006 | 168 / 0.055 / 0.006 |
| 0.10-0.20 | 175 / 0.144 / 0.046 | 168 / 0.147 / 0.054 | 170 / 0.146 / 0.071 |
| 0.20-0.30 | 133 / 0.250 / 0.233 | 118 / 0.251 / 0.220 | 127 / 0.250 / 0.165 |
| 0.30-0.40 | 107 / 0.352 / 0.327 | 104 / 0.351 / 0.298 | 106 / 0.351 / 0.330 |
| 0.40-0.50 | 104 / 0.449 / 0.433 | 99 / 0.446 / 0.424 | 107 / 0.449 / 0.411 |
| 0.50-0.60 | 113 / 0.547 / 0.549 | 98 / 0.551 / 0.449 | 113 / 0.547 / 0.531 |
| 0.60-0.70 | 63 / 0.650 / 0.635 | 87 / 0.647 / 0.575 | 74 / 0.652 / 0.689 |
| 0.70-0.80 | 63 / 0.756 / 0.794 | 68 / 0.747 / 0.794 | 55 / 0.754 / 0.782 |
| 0.80-0.90 | 55 / 0.854 / 0.927 | 62 / 0.845 / 0.887 | 58 / 0.847 / 0.914 |
| 0.90-1.00 | 106 / 0.957 / 1.000 | 118 / 0.956 / 0.992 | 109 / 0.953 / 1.000 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 13 | 3 | 2 | 0 | 8 | 0 | 1.000 [0.342, 1.000] | 0.500 | 0.500 | 0.15 |
| T-24h | DATA_ONLY | total | 13 | 5 | 2 | 2 | 4 | 0 | 0.500 [0.150, 0.850] | 0.250 | 0.125 | -0.06 |
| T-24h | HYBRID_30 (derived) | margin | 13 | 8 | 1 | 0 | 4 | 0 | 1.000 [0.207, 1.000] | 0.600 | 0.600 | 0.10 |
| T-24h | HYBRID_30 (derived) | total | 13 | 6 | 2 | 2 | 3 | 0 | 0.500 [0.150, 0.850] | 0.286 | 0.286 | -0.07 |
| T-6h | DATA_ONLY | margin | 14 | 3 | 1 | 1 | 9 | 0 | 0.500 [0.095, 0.905] | 0.455 | 0.455 | 0.05 |
| T-6h | DATA_ONLY | total | 14 | 4 | 2 | 5 | 3 | 0 | 0.286 [0.082, 0.641] | 0.300 | 0.200 | -0.20 |
| T-6h | HYBRID_30 (derived) | margin | 14 | 10 | 0 | 1 | 3 | 0 | 0.000 [0.000, 0.793] | 0.500 | 0.500 | -0.12 |
| T-6h | HYBRID_30 (derived) | total | 14 | 9 | 1 | 3 | 1 | 0 | 0.250 [0.046, 0.699] | 0.400 | 0.400 | -0.30 |
| T-90m | DATA_ONLY | margin | 14 | 3 | 2 | 0 | 9 | 0 | 1.000 [0.342, 1.000] | 0.455 | 0.455 | 0.14 |
| T-90m | DATA_ONLY | total | 14 | 4 | 1 | 3 | 6 | 0 | 0.250 [0.046, 0.699] | 0.200 | 0.200 | -0.20 |
| T-90m | HYBRID_30 (derived) | margin | 14 | 9 | 1 | 0 | 4 | 0 | 1.000 [0.207, 1.000] | 0.600 | 0.600 | 0.10 |
| T-90m | HYBRID_30 (derived) | total | 14 | 8 | 0 | 2 | 4 | 0 | 0.000 [0.000, 0.658] | 0.167 | 0.167 | -0.25 |
| T-30m | DATA_ONLY | margin | 14 | 2 | 3 | 0 | 9 | 0 | 1.000 [0.439, 1.000] | 0.500 | 0.500 | 0.17 |
| T-30m | DATA_ONLY | total | 14 | 4 | 1 | 1 | 8 | 0 | 0.500 [0.095, 0.905] | 0.200 | 0.200 | 0.15 |
| T-30m | HYBRID_30 (derived) | margin | 14 | 9 | 2 | 0 | 3 | 0 | 1.000 [0.342, 1.000] | 0.600 | 0.600 | 0.20 |
| T-30m | HYBRID_30 (derived) | total | 14 | 8 | 0 | 1 | 5 | 0 | 0.000 [0.000, 0.793] | 0.167 | 0.167 | -0.08 |
| latest_pregame | DATA_ONLY | margin | 14 | 2 | 3 | 0 | 9 | 0 | 1.000 [0.439, 1.000] | 0.500 | 0.500 | 0.17 |
| latest_pregame | DATA_ONLY | total | 14 | 4 | 1 | 1 | 8 | 0 | 0.500 [0.095, 0.905] | 0.200 | 0.200 | 0.15 |
| latest_pregame | HYBRID_30 (derived) | margin | 14 | 9 | 2 | 0 | 3 | 0 | 1.000 [0.342, 1.000] | 0.600 | 0.600 | 0.20 |
| latest_pregame | HYBRID_30 (derived) | total | 14 | 8 | 0 | 1 | 5 | 0 | 0.000 [0.000, 0.793] | 0.167 | 0.167 | -0.08 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 2 | 1 | 0 | 1 | 0 | 1.000 |
| margin | 1-2 | 4 | 0 | 0 | 4 | 0 | - |
| margin | 2-3 | 2 | 0 | 0 | 2 | 0 | - |
| margin | 3-5 | 3 | 2 | 0 | 1 | 0 | 1.000 |
| margin | >5 | 3 | 1 | 0 | 2 | 0 | 1.000 |
| total | <=1 | 4 | 0 | 2 | 2 | 0 | 0.000 |
| total | 1-2 | 0 | 0 | 0 | 0 | 0 | - |
| total | 2-3 | 3 | 1 | 0 | 2 | 0 | 1.000 |
| total | 3-5 | 5 | 0 | 0 | 5 | 0 | - |
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

