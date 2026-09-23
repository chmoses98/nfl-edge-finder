# Three-arm game-centre experiment — 2026 week 2

> **INSUFFICIENT EVIDENCE.** 16 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 976 | 16 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 6 | 6 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 16 | 16 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

Raw rows are repeated snapshots of the same games and are never a sample size. The primary unit is `latest_pregame` (one row per game); the canonical horizons are one row per game per horizon.

## Game centres, per game (latest pregame snapshot)

| game | kickoff | T-min | arm | margin | total | actual margin | actual total | mkt@snap margin/total | close margin/total |
|---|---|---|---|---|---|---|---|---|---|
| 2026_02_DET_BUF | 2026-09-18T00:15 | 167 | CURRENT | 5.50 | 54.50 | 10 | 72 | 5.5/54.5 (kalshi_implied) | 5.5/54.5 (OK) |
|  |  |  | DATA_ONLY | 3.74 | 48.96 |  |  |  |  |
|  |  |  | HYBRID_30 | 4.97 | 52.84 |  |  |  |  |
| 2026_02_CAR_ATL | 2026-09-20T17:00 | 44 | CURRENT | -1.50 | 43.00 | -31 | 37 | -1.5/43.0 (kalshi_implied) | -1.5/43.0 (OK) |
|  |  |  | DATA_ONLY | 4.79 | 45.58 |  |  |  |  |
|  |  |  | HYBRID_30 | 0.39 | 43.77 |  |  |  |  |
| 2026_02_CIN_HOU | 2026-09-20T17:00 | 44 | CURRENT | 2.50 | 45.00 | -14 | 26 | 2.5/45.0 (kalshi_implied) | 2.5/45.0 (OK) |
|  |  |  | DATA_ONLY | 4.76 | 45.07 |  |  |  |  |
|  |  |  | HYBRID_30 | 3.18 | 45.02 |  |  |  |  |
| 2026_02_CLE_TB | 2026-09-20T17:00 | 44 | CURRENT | 9.00 | 41.50 | -4 | 42 | 9.0/41.5 (kalshi_implied) | 9.0/41.5 (OK) |
|  |  |  | DATA_ONLY | 5.47 | 43.49 |  |  |  |  |
|  |  |  | HYBRID_30 | 7.94 | 42.10 |  |  |  |  |
| 2026_02_GB_NYJ | 2026-09-20T17:00 | 44 | CURRENT | -3.50 | 43.50 | -3 | 37 | -3.5/43.5 (kalshi_implied) | -2.5/44.0 (OK) |
|  |  |  | DATA_ONLY | -4.20 | 46.22 |  |  |  |  |
|  |  |  | HYBRID_30 | -3.71 | 44.32 |  |  |  |  |
| 2026_02_MIN_CHI | 2026-09-20T17:00 | 44 | CURRENT | 4.50 | 46.50 | -6 | 12 | 4.5/46.5 (kalshi_implied) | 4.5/46.5 (OK) |
|  |  |  | DATA_ONLY | 2.48 | 44.95 |  |  |  |  |
|  |  |  | HYBRID_30 | 3.89 | 46.03 |  |  |  |  |
| 2026_02_NO_BAL | 2026-09-20T17:00 | 44 | CURRENT | 9.00 | 45.50 | -7 | 41 | 9.0/45.5 (kalshi_implied) | 9.0/45.5 (OK) |
|  |  |  | DATA_ONLY | 6.54 | 45.65 |  |  |  |  |
|  |  |  | HYBRID_30 | 8.26 | 45.55 |  |  |  |  |
| 2026_02_PHI_TEN | 2026-09-20T17:00 | 44 | CURRENT | -6.50 | 39.00 | -4 | 44 | -6.5/39.0 (kalshi_implied) | -7.5/39.5 (OK) |
|  |  |  | DATA_ONLY | -7.79 | 41.31 |  |  |  |  |
|  |  |  | HYBRID_30 | -6.89 | 39.69 |  |  |  |  |
| 2026_02_PIT_NE | 2026-09-20T17:00 | 44 | CURRENT | 5.50 | 40.00 | 17 | 23 | 5.5/40.0 (kalshi_implied) | 5.5/41.0 (OK) |
|  |  |  | DATA_ONLY | 4.42 | 44.87 |  |  |  |  |
|  |  |  | HYBRID_30 | 5.18 | 41.46 |  |  |  |  |
| 2026_02_JAX_DEN | 2026-09-20T20:05 | 42 | CURRENT | 2.50 | 45.00 | 7 | 33 | 2.5/45.0 (kalshi_implied) | 2.5/45.0 (OK) |
|  |  |  | DATA_ONLY | -1.81 | 43.53 |  |  |  |  |
|  |  |  | HYBRID_30 | 1.21 | 44.56 |  |  |  |  |
| 2026_02_LV_LAC | 2026-09-20T20:05 | 42 | CURRENT | 7.50 | 43.00 | -12 | 40 | 7.5/43.0 (kalshi_implied) | 7.0/43.5 (OK) |
|  |  |  | DATA_ONLY | 5.00 | 41.38 |  |  |  |  |
|  |  |  | HYBRID_30 | 6.75 | 42.51 |  |  |  |  |
| 2026_02_MIA_SF | 2026-09-20T20:25 | 62 | CURRENT | 13.00 | 44.50 | 22 | 48 | 13.0/44.5 (kalshi_implied) | 13.0/44.5 (OK) |
|  |  |  | DATA_ONLY | 9.55 | 48.28 |  |  |  |  |
|  |  |  | HYBRID_30 | 11.96 | 45.63 |  |  |  |  |
| 2026_02_SEA_ARI | 2026-09-20T20:25 | 62 | CURRENT | -3.50 | 40.00 | -24 | 38 | -3.5/40.0 (kalshi_implied) | -3.5/40.0 (OK) |
|  |  |  | DATA_ONLY | -8.44 | 40.18 |  |  |  |  |
|  |  |  | HYBRID_30 | -4.98 | 40.05 |  |  |  |  |
| 2026_02_WAS_DAL | 2026-09-20T20:25 | 62 | CURRENT | 4.50 | 50.50 | 17 | 57 | 4.5/50.5 (kalshi_implied) | 4.5/50.5 (OK) |
|  |  |  | DATA_ONLY | -1.14 | 49.37 |  |  |  |  |
|  |  |  | HYBRID_30 | 2.81 | 50.16 |  |  |  |  |
| 2026_02_IND_KC | 2026-09-21T00:20 | 66 | CURRENT | 6.50 | 45.00 | 3 | 63 | 6.5/45.0 (kalshi_implied) | 6.5/45.0 (OK) |
|  |  |  | DATA_ONLY | 5.33 | 44.28 |  |  |  |  |
|  |  |  | HYBRID_30 | 6.15 | 44.79 |  |  |  |  |
| 2026_02_NYG_LA | 2026-09-22T00:15 | 52 | CURRENT | 7.00 | 47.50 | 22 | 34 | 7.0/47.5 (kalshi_implied) | 7.0/47.5 (OK) |
|  |  |  | DATA_ONLY | 7.09 | 51.41 |  |  |  |  |
|  |  |  | HYBRID_30 | 7.03 | 48.67 |  |  |  |  |

## Game-centre accuracy — latest_pregame (16 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 1 | 11.81 | 13.99 | 4.31 | 10.56 | 13.67 | 4.19 | 0.229 |
| DATA_ONLY | 16 | 1 | 12.44 | 14.82 | 2.67 | 11.36 | 14.74 | 4.85 | 0.254 |
| HYBRID_30 | 16 | 1 | 12.00 | 14.17 | 3.82 | 10.75 | 13.94 | 4.39 | 0.241 |
| market at snapshot | 16 | 1 | 11.81 | 13.99 | 4.31 | 10.56 | 13.67 | 4.19 | - |
| market at close | 16 | 1 | 11.84 | 13.96 | 4.28 | 10.66 | 13.76 | 4.34 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | 0.630 | 0.821 | [-0.979, 2.239] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | 0.793 | 0.644 | [-0.469, 2.054] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | 0.189 | 0.246 | [-0.294, 0.672] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | 0.184 | 0.201 | [-0.211, 0.579] | 0.375 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | -0.441 | 0.575 | [-1.567, 0.685] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -0.609 | 0.449 | [-1.490, 0.272] | 0.688 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | 0.630 | 0.821 | [-0.979, 2.239] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | 0.793 | 0.644 | [-0.469, 2.054] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | 0.189 | 0.246 | [-0.294, 0.672] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | 0.184 | 0.201 | [-0.211, 0.579] | 0.375 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | -0.031 | 0.072 | [-0.172, 0.109] | 0.062 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | -0.094 | 0.082 | [-0.254, 0.067] | 0.188 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | 0.599 | 0.813 | [-0.994, 2.192] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 0.699 | 0.613 | [-0.504, 1.901] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | 0.158 | 0.245 | [-0.323, 0.639] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | 0.090 | 0.182 | [-0.267, 0.447] | 0.375 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 2 | 1 | 13 | 0 | 0.667 | 0.438 | 2.72 |
| DATA_ONLY | total | 16 | 3 | 1 | 12 | 0 | 0.750 | 0.312 | 2.16 |
| HYBRID_30 | margin | 16 | 2 | 1 | 13 | 0 | 0.667 | 0.438 | 0.82 |
| HYBRID_30 | total | 16 | 3 | 1 | 12 | 0 | 0.750 | 0.375 | 0.65 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.05 | 7.75 | 0.000 |
| DATA_ONLY | margin | 1-2 | 4 | 6.24 | 5.50 | 1.000 |
| DATA_ONLY | margin | 2-3 | 4 | 14.45 | 15.62 | 1.000 |
| DATA_ONLY | margin | 3-5 | 4 | 11.57 | 11.75 | - |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 4 | 11.15 | 10.88 | - |
| DATA_ONLY | total | 1-2 | 5 | 10.79 | 11.30 | 0.000 |
| DATA_ONLY | total | 2-3 | 3 | 6.83 | 5.83 | 1.000 |
| DATA_ONLY | total | 3-5 | 3 | 13.19 | 11.33 | 1.000 |
| DATA_ONLY | total | >5 | 1 | 23.04 | 17.50 | - |
| HYBRID_30 | margin | <=1 | 10 | 9.97 | 10.00 | 0.667 |
| HYBRID_30 | margin | 1-2 | 6 | 15.39 | 14.83 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 12 | 9.77 | 9.79 | 0.667 |
| HYBRID_30 | total | 1-2 | 4 | 13.67 | 12.88 | 1.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Game-centre accuracy — T-24h (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 12.17 | 14.26 | 4.70 | 10.47 | 13.58 | 6.00 | 0.238 |
| DATA_ONLY | 15 | 1 | 12.85 | 15.21 | 3.26 | 10.60 | 14.04 | 6.70 | 0.261 |
| HYBRID_30 | 15 | 1 | 12.37 | 14.48 | 4.27 | 10.44 | 13.67 | 6.21 | 0.244 |
| market at snapshot | 15 | 1 | 12.17 | 14.26 | 4.70 | 10.47 | 13.58 | 6.00 | - |
| market at close | 15 | 1 | 12.33 | 14.37 | 4.87 | 10.20 | 13.47 | 5.80 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | 0.681 | 0.826 | [-0.939, 2.300] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 0.130 | 0.647 | [-1.139, 1.398] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | 0.204 | 0.248 | [-0.282, 0.690] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | -0.032 | 0.208 | [-0.439, 0.376] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | -0.477 | 0.578 | [-1.610, 0.657] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -0.161 | 0.452 | [-1.047, 0.725] | 0.533 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | 0.681 | 0.826 | [-0.939, 2.300] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 0.130 | 0.647 | [-1.139, 1.398] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | 0.204 | 0.248 | [-0.282, 0.690] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | -0.032 | 0.208 | [-0.439, 0.376] | 0.533 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | -0.167 | 0.105 | [-0.373, 0.040] | 0.267 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | 0.267 | 0.206 | [-0.138, 0.671] | 0.067 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | 0.514 | 0.866 | [-1.183, 2.211] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 0.396 | 0.562 | [-0.705, 1.498] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | 0.038 | 0.299 | [-0.548, 0.624] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | 0.235 | 0.190 | [-0.138, 0.608] | 0.267 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 1 | 5 | 9 | 0 | 0.167 | 0.467 | 2.59 |
| DATA_ONLY | total | 15 | 7 | 1 | 7 | 0 | 0.875 | 0.533 | 2.28 |
| HYBRID_30 | margin | 15 | 1 | 5 | 9 | 0 | 0.167 | 0.467 | 0.78 |
| HYBRID_30 | total | 15 | 7 | 1 | 7 | 0 | 0.875 | 0.533 | 0.68 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 4 | 8.83 | 9.12 | 0.000 |
| DATA_ONLY | margin | 1-2 | 2 | 8.19 | 7.00 | 1.000 |
| DATA_ONLY | margin | 2-3 | 3 | 13.60 | 14.33 | - |
| DATA_ONLY | margin | 3-5 | 4 | 11.57 | 11.62 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.25 | 0.000 |
| DATA_ONLY | total | <=1 | 3 | 8.63 | 9.00 | 1.000 |
| DATA_ONLY | total | 1-2 | 3 | 9.13 | 8.67 | 0.000 |
| DATA_ONLY | total | 2-3 | 5 | 12.66 | 12.60 | 1.000 |
| DATA_ONLY | total | 3-5 | 4 | 10.59 | 10.25 | 1.000 |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 10 | 10.48 | 10.60 | 0.200 |
| HYBRID_30 | margin | 1-2 | 5 | 16.16 | 15.30 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 12 | 10.02 | 10.17 | 0.875 |
| HYBRID_30 | total | 1-2 | 3 | 12.08 | 11.67 | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Game-centre accuracy — T-6h (6 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 6 | 1 | 11.58 | 13.36 | 2.92 | 7.42 | 9.19 | -1.75 | 0.179 |
| DATA_ONLY | 6 | 1 | 12.36 | 13.53 | -0.77 | 6.82 | 9.43 | -2.03 | 0.209 |
| HYBRID_30 | 6 | 1 | 11.82 | 13.28 | 1.81 | 7.21 | 9.22 | -1.83 | 0.184 |
| market at snapshot | 6 | 1 | 11.58 | 13.36 | 2.92 | 7.42 | 9.19 | -1.75 | - |
| market at close | 6 | 1 | 11.50 | 13.24 | 2.83 | 7.58 | 9.48 | -1.75 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 6 | margin | 0.781 | 1.741 | [-2.632, 4.194] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 6 | total | -0.601 | 0.754 | [-2.079, 0.877] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 6 | margin | 0.234 | 0.522 | [-0.789, 1.258] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 6 | total | -0.208 | 0.246 | [-0.690, 0.275] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 6 | margin | -0.547 | 1.219 | [-2.936, 1.842] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 6 | total | 0.393 | 0.509 | [-0.605, 1.391] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 6 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 6 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 6 | margin | 0.781 | 1.741 | [-2.632, 4.194] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 6 | total | -0.601 | 0.754 | [-2.079, 0.877] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 6 | margin | 0.234 | 0.522 | [-0.789, 1.258] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 6 | total | -0.208 | 0.246 | [-0.690, 0.275] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 6 | margin | 0.083 | 0.083 | [-0.080, 0.247] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 6 | total | -0.167 | 0.211 | [-0.580, 0.247] | 0.333 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 6 | margin | 0.865 | 1.712 | [-2.490, 4.220] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 6 | total | -0.768 | 0.722 | [-2.183, 0.648] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 6 | margin | 0.318 | 0.497 | [-0.656, 1.292] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 6 | total | -0.375 | 0.275 | [-0.914, 0.165] | 0.667 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 6 | 1 | 0 | 5 | 0 | 1.000 | 0.500 | 3.69 |
| DATA_ONLY | total | 6 | 1 | 2 | 3 | 0 | 0.333 | 0.500 | 1.60 |
| HYBRID_30 | margin | 6 | 1 | 0 | 5 | 0 | 1.000 | 0.500 | 1.11 |
| HYBRID_30 | total | 6 | 1 | 2 | 3 | 0 | 0.333 | 0.500 | 0.48 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 1 | 2.22 | 3.50 | - |
| DATA_ONLY | margin | 2-3 | 1 | 17.00 | 19.50 | 1.000 |
| DATA_ONLY | margin | 3-5 | 3 | 12.27 | 11.33 | - |
| DATA_ONLY | margin | >5 | 1 | 18.14 | 12.50 | - |
| DATA_ONLY | total | <=1 | 2 | 4.90 | 4.50 | 0.000 |
| DATA_ONLY | total | 1-2 | 3 | 10.27 | 10.67 | 0.500 |
| DATA_ONLY | total | 2-3 | 0 | - | - | - |
| DATA_ONLY | total | 3-5 | 1 | 0.28 | 3.50 | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 2 | 10.93 | 11.50 | 1.000 |
| HYBRID_30 | margin | 1-2 | 4 | 12.26 | 11.62 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 5 | 8.18 | 8.20 | 0.333 |
| HYBRID_30 | total | 1-2 | 1 | 2.37 | 3.50 | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 6}; DATA_ONLY quality states: {'OK': 6}; close centre status: {'OK': 6}.

## Game-centre accuracy — T-90m (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 11.67 | 13.92 | 5.53 | 10.53 | 14.01 | 3.80 | 0.238 |
| DATA_ONLY | 15 | 1 | 12.28 | 14.81 | 3.85 | 10.95 | 14.55 | 4.01 | 0.265 |
| HYBRID_30 | 15 | 1 | 11.85 | 14.11 | 5.03 | 10.60 | 14.13 | 3.86 | 0.246 |
| market at snapshot | 15 | 1 | 11.67 | 13.92 | 5.53 | 10.53 | 14.01 | 3.80 | - |
| market at close | 15 | 1 | 11.63 | 13.89 | 5.57 | 10.47 | 13.77 | 3.73 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | 0.611 | 0.888 | [-1.130, 2.352] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 0.418 | 0.639 | [-0.835, 1.670] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | 0.183 | 0.266 | [-0.339, 0.706] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.068 | 0.199 | [-0.322, 0.457] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | -0.428 | 0.622 | [-1.647, 0.791] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -0.350 | 0.448 | [-1.229, 0.528] | 0.600 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | 0.611 | 0.888 | [-1.130, 2.352] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 0.418 | 0.639 | [-0.835, 1.670] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | 0.183 | 0.266 | [-0.339, 0.706] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.068 | 0.199 | [-0.322, 0.457] | 0.467 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | 0.033 | 0.059 | [-0.082, 0.149] | 0.067 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | 0.067 | 0.108 | [-0.144, 0.278] | 0.133 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | 0.645 | 0.867 | [-1.056, 2.345] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 0.484 | 0.614 | [-0.720, 1.689] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | 0.217 | 0.250 | [-0.273, 0.707] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | 0.134 | 0.197 | [-0.253, 0.521] | 0.333 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 3 | 1 | 11 | 0 | 0.750 | 0.400 | 2.89 |
| DATA_ONLY | total | 15 | 3 | 1 | 11 | 0 | 0.750 | 0.400 | 2.07 |
| HYBRID_30 | margin | 15 | 3 | 1 | 11 | 0 | 0.750 | 0.400 | 0.87 |
| HYBRID_30 | total | 15 | 3 | 1 | 11 | 0 | 0.750 | 0.467 | 0.62 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 2.50 | 2.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 3 | 7.05 | 6.50 | - |
| DATA_ONLY | margin | 2-3 | 4 | 14.45 | 15.62 | 1.000 |
| DATA_ONLY | margin | 3-5 | 4 | 11.57 | 11.75 | - |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 4 | 11.15 | 11.12 | 1.000 |
| DATA_ONLY | total | 1-2 | 5 | 4.74 | 5.30 | 0.000 |
| DATA_ONLY | total | 2-3 | 3 | 16.92 | 16.00 | 1.000 |
| DATA_ONLY | total | 3-5 | 2 | 11.07 | 10.75 | - |
| DATA_ONLY | total | >5 | 1 | 23.04 | 17.50 | - |
| HYBRID_30 | margin | <=1 | 9 | 9.49 | 9.56 | 0.750 |
| HYBRID_30 | margin | 1-2 | 6 | 15.39 | 14.83 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 12 | 9.86 | 9.92 | 0.750 |
| HYBRID_30 | total | 1-2 | 3 | 13.56 | 13.00 | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Game-centre accuracy — T-30m (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 12.30 | 14.40 | 4.90 | 10.10 | 13.37 | 5.63 | 0.238 |
| DATA_ONLY | 15 | 1 | 12.85 | 15.22 | 3.27 | 10.58 | 14.02 | 6.71 | 0.261 |
| HYBRID_30 | 15 | 1 | 12.47 | 14.57 | 4.41 | 10.19 | 13.52 | 5.95 | 0.251 |
| market at snapshot | 15 | 1 | 12.30 | 14.40 | 4.90 | 10.10 | 13.37 | 5.63 | - |
| market at close | 15 | 1 | 12.33 | 14.37 | 4.87 | 10.20 | 13.47 | 5.80 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | 0.555 | 0.874 | [-1.158, 2.268] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 0.476 | 0.600 | [-0.699, 1.651] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | 0.166 | 0.262 | [-0.347, 0.680] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.085 | 0.188 | [-0.283, 0.453] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | -0.388 | 0.612 | [-1.587, 0.811] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -0.391 | 0.420 | [-1.215, 0.433] | 0.667 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | 0.555 | 0.874 | [-1.158, 2.268] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 0.476 | 0.600 | [-0.699, 1.651] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | 0.166 | 0.262 | [-0.347, 0.680] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.085 | 0.188 | [-0.283, 0.453] | 0.400 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | -0.033 | 0.077 | [-0.184, 0.117] | 0.067 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | -0.100 | 0.087 | [-0.271, 0.071] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | 0.521 | 0.865 | [-1.174, 2.217] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 0.376 | 0.558 | [-0.717, 1.470] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | 0.133 | 0.261 | [-0.379, 0.645] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | -0.015 | 0.159 | [-0.327, 0.297] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 2 | 1 | 12 | 0 | 0.667 | 0.467 | 2.78 |
| DATA_ONLY | total | 15 | 3 | 1 | 11 | 0 | 0.750 | 0.333 | 1.94 |
| HYBRID_30 | margin | 15 | 2 | 1 | 12 | 0 | 0.667 | 0.467 | 0.83 |
| HYBRID_30 | total | 15 | 3 | 1 | 11 | 0 | 0.750 | 0.400 | 0.58 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 8.05 | 7.75 | 0.000 |
| DATA_ONLY | margin | 1-2 | 3 | 6.23 | 5.83 | 1.000 |
| DATA_ONLY | margin | 2-3 | 4 | 14.45 | 15.62 | 1.000 |
| DATA_ONLY | margin | 3-5 | 4 | 11.57 | 11.75 | - |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 4 | 11.15 | 10.88 | - |
| DATA_ONLY | total | 1-2 | 5 | 10.79 | 11.30 | 0.000 |
| DATA_ONLY | total | 2-3 | 3 | 6.83 | 5.83 | 1.000 |
| DATA_ONLY | total | 3-5 | 3 | 13.19 | 11.33 | 1.000 |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 9 | 10.51 | 10.61 | 0.667 |
| HYBRID_30 | margin | 1-2 | 6 | 15.39 | 14.83 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 12 | 9.77 | 9.79 | 0.667 |
| HYBRID_30 | total | 1-2 | 3 | 11.83 | 11.33 | 1.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Contract pricing — latest_pregame (1249 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1249 | 0.1702 | 0.5100 | 0.415 | 0.371 | 1249 | 0.1702 | 0.1697 | 0.1711 |
| DATA_ONLY | 1249 | 0.1826 | 0.5468 | 0.419 | 0.371 | 1249 | 0.1826 | 0.1697 | 0.1711 |
| HYBRID_30 | 1249 | 0.1751 | 0.5245 | 0.411 | 0.371 | 1249 | 0.1751 | 0.1697 | 0.1711 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1249 | 16 | 0.01234 | [-0.00610, 0.03488] | 0.01234 | [-0.00610, 0.03488] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1249 | 16 | 0.00489 | [-0.00079, 0.01219] | 0.00489 | [-0.00079, 0.01219] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1249 | 16 | -0.00745 | [-0.02376, 0.00622] | -0.00745 | [-0.02376, 0.00622] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1249 | 16 | - | - | 0.00048 | [-0.00059, 0.00151] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1234 | 16 | - | - | 0.00067 | [-0.00064, 0.00193] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1249 | 16 | - | - | 0.01282 | [-0.00557, 0.03578] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1234 | 16 | - | - | 0.01330 | [-0.00487, 0.03595] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1249 | 16 | - | - | 0.00537 | [-0.00007, 0.01271] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1234 | 16 | - | - | 0.00573 | [0.00051, 0.01266] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 415, 'TEAM_TOTAL': 434, 'TOTAL': 304}; settlement: {'SETTLED': 1249}; close: {'OK': 1234, 'OK_STALE': 15}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 199 / 0.054 / 0.010 | 189 / 0.055 / 0.042 | 205 / 0.054 / 0.029 |
| 0.10-0.20 | 202 / 0.145 / 0.168 | 199 / 0.145 / 0.176 | 196 / 0.148 / 0.194 |
| 0.20-0.30 | 147 / 0.249 / 0.286 | 148 / 0.250 / 0.318 | 143 / 0.247 / 0.273 |
| 0.30-0.40 | 112 / 0.351 / 0.295 | 126 / 0.347 / 0.333 | 125 / 0.345 / 0.312 |
| 0.40-0.50 | 128 / 0.451 / 0.383 | 122 / 0.447 / 0.344 | 135 / 0.448 / 0.407 |
| 0.50-0.60 | 116 / 0.549 / 0.491 | 105 / 0.550 / 0.381 | 107 / 0.550 / 0.458 |
| 0.60-0.70 | 87 / 0.650 / 0.540 | 105 / 0.648 / 0.495 | 88 / 0.649 / 0.511 |
| 0.70-0.80 | 69 / 0.747 / 0.623 | 66 / 0.745 / 0.652 | 68 / 0.750 / 0.574 |
| 0.80-0.90 | 70 / 0.850 / 0.743 | 69 / 0.850 / 0.754 | 64 / 0.852 / 0.781 |
| 0.90-1.00 | 119 / 0.955 / 0.874 | 120 / 0.956 / 0.850 | 118 / 0.956 / 0.873 |

## Contract pricing — T-24h (1172 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1172 | 0.1736 | 0.5199 | 0.412 | 0.351 | 1172 | 0.1736 | 0.1727 | 0.1733 |
| DATA_ONLY | 1172 | 0.1823 | 0.5470 | 0.417 | 0.351 | 1172 | 0.1823 | 0.1727 | 0.1733 |
| HYBRID_30 | 1172 | 0.1745 | 0.5233 | 0.411 | 0.351 | 1172 | 0.1745 | 0.1727 | 0.1733 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1172 | 15 | 0.00872 | [-0.01267, 0.03013] | 0.00872 | [-0.01267, 0.03013] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1172 | 15 | 0.00096 | [-0.00586, 0.00828] | 0.00096 | [-0.00586, 0.00828] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1172 | 15 | -0.00777 | [-0.02269, 0.00776] | -0.00777 | [-0.02269, 0.00776] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1172 | 15 | - | - | 0.00089 | [-0.00061, 0.00228] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1157 | 15 | - | - | 0.00191 | [-0.00078, 0.00492] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1172 | 15 | - | - | 0.00961 | [-0.01161, 0.03111] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1157 | 15 | - | - | 0.01090 | [-0.00935, 0.03244] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1172 | 15 | - | - | 0.00184 | [-0.00491, 0.00915] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1157 | 15 | - | - | 0.00299 | [-0.00342, 0.00976] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 390, 'TEAM_TOTAL': 407, 'TOTAL': 285}; settlement: {'SETTLED': 1172}; close: {'OK': 1157, 'OK_STALE': 15}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 193 / 0.054 / 0.021 | 182 / 0.054 / 0.033 | 186 / 0.053 / 0.016 |
| 0.10-0.20 | 184 / 0.146 / 0.147 | 183 / 0.145 / 0.169 | 190 / 0.146 / 0.174 |
| 0.20-0.30 | 140 / 0.249 / 0.279 | 139 / 0.248 / 0.317 | 136 / 0.248 / 0.250 |
| 0.30-0.40 | 103 / 0.351 / 0.291 | 120 / 0.346 / 0.300 | 109 / 0.348 / 0.294 |
| 0.40-0.50 | 127 / 0.448 / 0.378 | 109 / 0.446 / 0.303 | 133 / 0.448 / 0.406 |
| 0.50-0.60 | 105 / 0.545 / 0.438 | 99 / 0.547 / 0.313 | 102 / 0.549 / 0.402 |
| 0.60-0.70 | 79 / 0.647 / 0.456 | 105 / 0.648 / 0.505 | 79 / 0.647 / 0.418 |
| 0.70-0.80 | 69 / 0.746 / 0.638 | 60 / 0.748 / 0.617 | 68 / 0.747 / 0.618 |
| 0.80-0.90 | 61 / 0.850 / 0.705 | 63 / 0.851 / 0.730 | 60 / 0.853 / 0.750 |
| 0.90-1.00 | 111 / 0.955 / 0.847 | 112 / 0.956 / 0.839 | 109 / 0.955 / 0.862 |

## Contract pricing — T-6h (471 contracts, 6 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 471 | 0.1571 | 0.4690 | 0.417 | 0.439 | 471 | 0.1571 | 0.1570 | 0.1599 |
| DATA_ONLY | 471 | 0.1632 | 0.4804 | 0.410 | 0.439 | 471 | 0.1632 | 0.1570 | 0.1599 |
| HYBRID_30 | 471 | 0.1591 | 0.4734 | 0.412 | 0.439 | 471 | 0.1591 | 0.1570 | 0.1599 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 471 | 6 | 0.00613 | [-0.02232, 0.03445] | 0.00613 | [-0.02232, 0.03445] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 471 | 6 | 0.00203 | [-0.00567, 0.00937] | 0.00203 | [-0.00567, 0.00937] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 471 | 6 | -0.00410 | [-0.02596, 0.01830] | -0.00410 | [-0.02596, 0.01830] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 471 | 6 | - | - | 0.00012 | [-0.00254, 0.00208] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 460 | 6 | - | - | -0.00053 | [-0.00458, 0.00272] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 471 | 6 | - | - | 0.00625 | [-0.02250, 0.03485] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 460 | 6 | - | - | 0.00610 | [-0.02285, 0.03465] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 471 | 6 | - | - | 0.00215 | [-0.00512, 0.00929] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 460 | 6 | - | - | 0.00182 | [-0.00495, 0.00949] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 24, 'GAME_WINNER': 12, 'SPREAD': 156, 'TEAM_TOTAL': 165, 'TOTAL': 114}; settlement: {'SETTLED': 471}; close: {'OK': 460, 'OK_STALE': 11}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 77 / 0.054 / 0.039 | 77 / 0.053 / 0.013 | 77 / 0.055 / 0.039 |
| 0.10-0.20 | 74 / 0.143 / 0.203 | 74 / 0.146 / 0.189 | 72 / 0.147 / 0.208 |
| 0.20-0.30 | 55 / 0.250 / 0.236 | 52 / 0.252 / 0.423 | 54 / 0.250 / 0.278 |
| 0.30-0.40 | 39 / 0.353 / 0.385 | 50 / 0.348 / 0.480 | 48 / 0.350 / 0.396 |
| 0.40-0.50 | 53 / 0.452 / 0.566 | 49 / 0.443 / 0.388 | 52 / 0.446 / 0.538 |
| 0.50-0.60 | 43 / 0.548 / 0.488 | 36 / 0.545 / 0.417 | 43 / 0.554 / 0.512 |
| 0.60-0.70 | 30 / 0.650 / 0.667 | 39 / 0.644 / 0.692 | 30 / 0.650 / 0.633 |
| 0.70-0.80 | 27 / 0.751 / 0.852 | 26 / 0.747 / 0.769 | 26 / 0.748 / 0.769 |
| 0.80-0.90 | 27 / 0.850 / 0.852 | 27 / 0.849 / 0.889 | 30 / 0.850 / 0.900 |
| 0.90-1.00 | 46 / 0.956 / 0.957 | 41 / 0.955 / 1.000 | 39 / 0.958 / 1.000 |

## Contract pricing — T-90m (1171 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1171 | 0.1719 | 0.5175 | 0.417 | 0.372 | 1171 | 0.1719 | 0.1701 | 0.1713 |
| DATA_ONLY | 1171 | 0.1817 | 0.5459 | 0.416 | 0.372 | 1171 | 0.1817 | 0.1701 | 0.1713 |
| HYBRID_30 | 1171 | 0.1757 | 0.5250 | 0.412 | 0.372 | 1171 | 0.1757 | 0.1701 | 0.1713 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1171 | 15 | 0.00984 | [-0.01182, 0.03284] | 0.00984 | [-0.01182, 0.03284] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1171 | 15 | 0.00378 | [-0.00229, 0.01071] | 0.00378 | [-0.00229, 0.01071] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1171 | 15 | -0.00606 | [-0.02325, 0.00969] | -0.00606 | [-0.02325, 0.00969] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1171 | 15 | - | - | 0.00184 | [0.00055, 0.00317] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1156 | 15 | - | - | 0.00222 | [0.00043, 0.00441] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1171 | 15 | - | - | 0.01168 | [-0.00930, 0.03501] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1156 | 15 | - | - | 0.01233 | [-0.00868, 0.03547] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1171 | 15 | - | - | 0.00562 | [-0.00023, 0.01278] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1156 | 15 | - | - | 0.00617 | [0.00082, 0.01265] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 388, 'TEAM_TOTAL': 408, 'TOTAL': 285}; settlement: {'SETTLED': 1171}; close: {'OK': 1156, 'OK_STALE': 15}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 183 / 0.053 / 0.016 | 180 / 0.054 / 0.044 | 192 / 0.054 / 0.031 |
| 0.10-0.20 | 186 / 0.144 / 0.172 | 185 / 0.144 / 0.184 | 177 / 0.146 / 0.192 |
| 0.20-0.30 | 141 / 0.247 / 0.277 | 140 / 0.249 / 0.321 | 143 / 0.246 / 0.273 |
| 0.30-0.40 | 105 / 0.349 / 0.286 | 121 / 0.348 / 0.322 | 112 / 0.348 / 0.321 |
| 0.40-0.50 | 118 / 0.450 / 0.390 | 113 / 0.446 / 0.345 | 127 / 0.447 / 0.417 |
| 0.50-0.60 | 110 / 0.546 / 0.491 | 100 / 0.548 / 0.380 | 101 / 0.547 / 0.455 |
| 0.60-0.70 | 86 / 0.649 / 0.512 | 98 / 0.648 / 0.520 | 83 / 0.648 / 0.470 |
| 0.70-0.80 | 63 / 0.747 / 0.651 | 61 / 0.747 / 0.639 | 63 / 0.749 / 0.603 |
| 0.80-0.90 | 69 / 0.851 / 0.739 | 62 / 0.852 / 0.790 | 62 / 0.850 / 0.774 |
| 0.90-1.00 | 110 / 0.958 / 0.873 | 111 / 0.956 / 0.847 | 111 / 0.956 / 0.874 |

## Contract pricing — T-30m (1172 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1172 | 0.1724 | 0.5160 | 0.410 | 0.351 | 1172 | 0.1724 | 0.1719 | 0.1733 |
| DATA_ONLY | 1172 | 0.1815 | 0.5448 | 0.418 | 0.351 | 1172 | 0.1815 | 0.1719 | 0.1733 |
| HYBRID_30 | 1172 | 0.1760 | 0.5276 | 0.408 | 0.351 | 1172 | 0.1760 | 0.1719 | 0.1733 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1172 | 15 | 0.00911 | [-0.01167, 0.03096] | 0.00911 | [-0.01167, 0.03096] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1172 | 15 | 0.00357 | [-0.00262, 0.00973] | 0.00357 | [-0.00262, 0.00973] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1172 | 15 | -0.00555 | [-0.02174, 0.00967] | -0.00555 | [-0.02174, 0.00967] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1172 | 15 | - | - | 0.00052 | [-0.00071, 0.00162] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1157 | 15 | - | - | 0.00074 | [-0.00066, 0.00216] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1172 | 15 | - | - | 0.00964 | [-0.01042, 0.03128] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1157 | 15 | - | - | 0.01012 | [-0.00985, 0.03169] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1172 | 15 | - | - | 0.00409 | [-0.00161, 0.01044] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1157 | 15 | - | - | 0.00446 | [-0.00103, 0.01051] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 390, 'TEAM_TOTAL': 407, 'TOTAL': 285}; settlement: {'SETTLED': 1172}; close: {'OK': 1157, 'OK_STALE': 15}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 193 / 0.054 / 0.010 | 179 / 0.054 / 0.034 | 197 / 0.054 / 0.030 |
| 0.10-0.20 | 189 / 0.145 / 0.164 | 186 / 0.145 / 0.167 | 182 / 0.148 / 0.187 |
| 0.20-0.30 | 137 / 0.250 / 0.285 | 138 / 0.249 / 0.304 | 134 / 0.247 / 0.261 |
| 0.30-0.40 | 106 / 0.352 / 0.274 | 118 / 0.347 / 0.314 | 120 / 0.346 / 0.300 |
| 0.40-0.50 | 125 / 0.452 / 0.368 | 112 / 0.447 / 0.286 | 125 / 0.448 / 0.360 |
| 0.50-0.60 | 105 / 0.548 / 0.438 | 100 / 0.550 / 0.350 | 101 / 0.550 / 0.426 |
| 0.60-0.70 | 79 / 0.649 / 0.494 | 101 / 0.648 / 0.475 | 82 / 0.649 / 0.476 |
| 0.70-0.80 | 67 / 0.746 / 0.612 | 62 / 0.745 / 0.629 | 66 / 0.750 / 0.561 |
| 0.80-0.90 | 64 / 0.849 / 0.719 | 65 / 0.851 / 0.738 | 58 / 0.852 / 0.759 |
| 0.90-1.00 | 107 / 0.954 / 0.860 | 111 / 0.956 / 0.838 | 107 / 0.955 / 0.860 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

998 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_02_IND_KC | Emmett Johnson | receiving_yards | 1.0 | 0–11 | 20 | 26.98 | 0.99 | 0.9 | 2 | 1.08 | 10.00 | EXPECTED_ACTIVE | True | 0.273 | EFFICIENCY_MISS |
| 2026_02_SEA_ARI | Jeremiyah Love | receiving_yards | 1.0 | 0–11 | 16 | 21.58 | 0.97 | 1.0 | 3 | 1.05 | 5.33 | EXPECTED_ACTIVE | True | 0.506 | EFFICIENCY_MISS |
| 2026_02_SEA_ARI | Jadarian Price | receiving_yards | 1.0 | 0–11 | 8 | 10.79 | 0.89 | 0.9 | 2 | 1.08 | 4.00 | EXPECTED_ACTIVE | True | -0.293 | EFFICIENCY_MISS |
| 2026_02_GB_NYJ | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 6 | 8.09 | 0.85 | 0.9 | 2 | 1.05 | 3.00 | EXPECTED_ACTIVE | True | -0.303 | EFFICIENCY_MISS |
| 2026_02_MIA_SF | Kyle Juszczyk | touchdowns | 0.0 | -–- | 1 | 8.00 | - | 0.0 | 2 | - | - | EXPECTED_ACTIVE | True | 0.068 | UNEXPLAINED_VARIANCE |
| 2026_02_CAR_ATL | Jonathon Brooks | receiving_yards | 1.0 | 0–11 | -5 | -6.75 | 0.05 | 1.0 | 1 | 1.00 | -5.00 | EXPECTED_ACTIVE | True | -0.233 | EFFICIENCY_MISS |
| 2026_02_GB_NYJ | Chris Brooks | receiving_yards | 3.1 | 0–32 | 15 | 6.74 | 0.83 | 1.3 | 2 | 2.41 | 7.50 | EXPECTED_ACTIVE | True | 0.210 | EFFICIENCY_MISS |
| 2026_02_NYG_LA | Blake Corum | receiving_yards | 2.9 | 0–30 | 13 | 5.85 | 0.82 | 1.2 | 1 | 2.33 | 13.00 | EXPECTED_ACTIVE | True | -0.050 | EFFICIENCY_MISS |
| 2026_02_GB_NYJ | Kenyon Sadiq | receiving_yards | 3.5 | 0–37 | 17 | 5.73 | 0.83 | 1.1 | 3 | 3.16 | 5.67 | EXPECTED_ACTIVE | True | 0.473 | TEAM_VOLUME_MISS |
| 2026_02_GB_NYJ | Breece Hall | receiving_yards | 12.2 | 0–53 | 63 | 5.31 | 0.96 | 1.8 | 5 | 6.88 | 12.60 | EXPECTED_ACTIVE | True | 0.314 | TEAM_VOLUME_MISS |
| 2026_02_NYG_LA | Davante Adams | receiving_yards | 48.7 | 4–113 | 195 | 4.63 | 0.99 | 5.5 | 10 | 8.91 | 19.50 | EXPECTED_ACTIVE | True | 0.196 | EFFICIENCY_MISS |
| 2026_02_CIN_HOU | Foster Moreau | receiving_yards | 7.7 | 0–34 | 34 | 4.59 | 0.95 | 1.4 | 2 | 5.47 | 17.00 | EXPECTED_ACTIVE | True | 0.137 | EFFICIENCY_MISS |
| 2026_02_CIN_HOU | Dalton Schultz | receptions | 2.5 | 0–6 | 12 | 4.50 | 0.99 | 3.2 | 14 | 0.78 | 0.86 | EXPECTED_ACTIVE | True | 0.373 | TEAM_VOLUME_MISS |
| 2026_02_CLE_TB | Denzel Boston | receiving_yards | 19.3 | 0–65 | 95 | 4.46 | 0.98 | 1.9 | 7 | 10.28 | 13.57 | EXPECTED_ACTIVE | True | 0.318 | TEAM_VOLUME_MISS |
| 2026_02_NO_BAL | Derrick Henry | receiving_yards | 5.6 | 0–59 | 19 | 4.27 | 0.80 | 1.3 | 3 | 4.27 | 6.33 | EXPECTED_ACTIVE | True | 0.093 | OPPORTUNITY_MISS |
| 2026_02_CLE_TB | Denzel Boston | touchdowns | 0.1 | -–- | 1 | 4.18 | - | 4.5 | 7 | - | - | EXPECTED_ACTIVE | True | 0.131 | UNEXPLAINED_VARIANCE |
| 2026_02_WAS_DAL | Rachaad White | receiving_yards | 9.5 | 0–41 | 40 | 4.15 | 0.94 | 1.6 | 6 | 5.78 | 6.67 | EXPECTED_ACTIVE | True | 0.191 | OPPORTUNITY_MISS |
| 2026_02_IND_KC | Kenneth Walker | receiving_yards | 13.1 | 0–44 | 61 | 4.12 | 0.98 | 1.7 | 10 | 7.86 | 6.10 | EXPECTED_ACTIVE | True | 0.313 | TEAM_VOLUME_MISS |
| 2026_02_CAR_ATL | Jalen Coker | receptions | 2.0 | 0–6 | 8 | 4.05 | 0.98 | 2.9 | 9 | 0.70 | 0.89 | EXPECTED_ACTIVE | True | 0.317 | OPPORTUNITY_MISS |
| 2026_02_DET_BUF | Jared Goff | passing_tds | 1.6 | 0–4 | 4 | 4.05 | 0.95 | 34.9 | 38 | 0.05 | 0.11 | EXPECTED_ACTIVE | True | 0.060 | EFFICIENCY_MISS |
| 2026_02_NO_BAL | Derrick Henry | receptions | 0.9 | 0–5 | 3 | 4.05 | 0.85 | 1.3 | 3 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.090 | OPPORTUNITY_MISS |
| 2026_02_NO_BAL | Rashod Bateman | receptions | 1.4 | 0–5 | 7 | 4.05 | 0.98 | 2.3 | 9 | 0.61 | 0.78 | EXPECTED_ACTIVE | True | 0.389 | OPPORTUNITY_MISS |
| 2026_02_SEA_ARI | Jeremiyah Love | receptions | 0.7 | 0–5 | 3 | 4.05 | 0.85 | 1.0 | 3 | 0.73 | 1.00 | EXPECTED_ACTIVE | True | 0.592 | OPPORTUNITY_MISS |
| 2026_02_CIN_HOU | Dalton Schultz | receiving_yards | 32.8 | 0–91 | 140 | 4.01 | 0.99 | 3.2 | 14 | 10.21 | 10.00 | EXPECTED_ACTIVE | True | 0.246 | TEAM_VOLUME_MISS |
| 2026_02_CIN_HOU | Woody Marks | receiving_yards | 7.8 | 0–34 | 27 | 3.64 | 0.89 | 1.6 | 6 | 4.96 | 4.50 | EXPECTED_ACTIVE | True | 0.241 | TEAM_VOLUME_MISS |
| 2026_02_CIN_HOU | Samaje Perine | receiving_yards | 5.2 | 0–55 | 16 | 3.60 | 0.79 | 1.5 | 1 | 3.61 | 16.00 | EXPECTED_ACTIVE | True | 0.098 | EFFICIENCY_MISS |
| 2026_02_NO_BAL | Rashod Bateman | receiving_yards | 22.6 | 0–63 | 88 | 3.55 | 0.98 | 2.3 | 9 | 9.93 | 9.78 | EXPECTED_ACTIVE | True | 0.238 | OPPORTUNITY_MISS |
| 2026_02_JAX_DEN | Jaylen Waddle | receiving_yards | 42.1 | 3–98 | 138 | 3.46 | 0.99 | 4.0 | 10 | 10.45 | 13.80 | EXPECTED_ACTIVE | True | 0.161 | OPPORTUNITY_MISS |
| 2026_02_IND_KC | Kenneth Walker | receptions | 1.3 | 0–5 | 6 | 3.37 | 0.96 | 1.7 | 10 | 0.78 | 0.60 | EXPECTED_ACTIVE | True | 0.445 | TEAM_VOLUME_MISS |
| 2026_02_NYG_LA | Davante Adams | receptions | 3.0 | 0–7 | 8 | 3.37 | 0.96 | 5.5 | 10 | 0.55 | 0.80 | EXPECTED_ACTIVE | True | 0.294 | OPPORTUNITY_MISS |
| 2026_02_NYG_LA | Terrance Ferguson | receptions | 1.1 | 0–5 | 6 | 3.37 | 0.96 | 1.6 | 9 | 0.64 | 0.67 | EXPECTED_ACTIVE | True | 0.296 | OPPORTUNITY_MISS |
| 2026_02_WAS_DAL | Rachaad White | receptions | 1.3 | 0–5 | 6 | 3.37 | 0.96 | 1.6 | 6 | 0.78 | 1.00 | EXPECTED_ACTIVE | True | 0.250 | OPPORTUNITY_MISS |
| 2026_02_IND_KC | Tyquan Thornton | receiving_yards | 24.3 | 0–68 | 86 | 3.28 | 0.97 | 2.1 | 4 | 11.57 | 21.50 | EXPECTED_ACTIVE | True | -0.037 | EFFICIENCY_MISS |
| 2026_02_PIT_NE | Jaylen Warren | receiving_yards | 10.7 | 0–46 | 34 | 3.28 | 0.88 | 1.7 | 4 | 6.13 | 8.50 | EXPECTED_ACTIVE | True | 0.344 | OPPORTUNITY_MISS |
| 2026_02_LV_LAC | Tre Tucker | receiving_yards | 33.5 | 0–93 | 119 | 3.17 | 0.97 | 3.7 | 7 | 9.12 | 17.00 | EXPECTED_ACTIVE | True | 0.154 | EFFICIENCY_MISS |
| 2026_02_NYG_LA | Terrance Ferguson | receiving_yards | 14.5 | 0–49 | 54 | 3.17 | 0.96 | 1.6 | 9 | 8.81 | 6.00 | EXPECTED_ACTIVE | True | 0.353 | OPPORTUNITY_MISS |
| 2026_02_DET_BUF | Dalton Kincaid | receiving_yards | 27.3 | 0–76 | 95 | 3.16 | 0.97 | 2.2 | 8 | 12.60 | 11.88 | EXPECTED_ACTIVE | True | 0.368 | OPPORTUNITY_MISS |
| 2026_02_CLE_TB | Deshaun Watson | carries | 2.3 | 0–18 | 7 | 3.15 | 0.80 | 2.3 | 7 | - | - | EXPECTED_ACTIVE | True | 0.570 | OPPORTUNITY_MISS |
| 2026_02_IND_KC | Travis Kelce | receptions | 2.4 | 0–6 | 9 | 3.15 | 0.99 | 3.5 | 11 | 0.69 | 0.82 | EXPECTED_ACTIVE | True | 0.216 | TEAM_VOLUME_MISS |
| 2026_02_PHI_TEN | DeVonta Smith | receptions | 2.7 | 0–6 | 10 | 3.15 | 0.99 | 4.3 | 13 | 0.63 | 0.77 | EXPECTED_ACTIVE | True | 0.337 | TEAM_VOLUME_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 186, 'UNEXPLAINED_VARIANCE': 28, 'TEAM_VOLUME_MISS': 74, 'OPPORTUNITY_MISS': 307, 'NO_LARGE_MISS': 382, 'INSUFFICIENT_DATA': 18, 'AVAILABILITY_MISS': 3}.
Missing usage (no snap table or stats row): 21.

## Decision funnel

No funnel accounting is available for this period.

