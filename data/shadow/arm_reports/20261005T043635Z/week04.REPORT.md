# Three-arm game-centre experiment — 2026 week 4

> **INSUFFICIENT EVIDENCE.** 15 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 1213 | 15 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 14 | 14 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 15 | 15 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_DET_CAR | 2026-10-05T00:20 | 30 | CURRENT | -4.50 | 51.50 | 6 | 58 | -4.5/51.5 (kalshi_implied) | -4.5/51.5 (OK) |
|  |  |  | DATA_ONLY | -0.32 | 47.29 |  |  |  |  |
|  |  |  | HYBRID_30 | -3.25 | 50.24 |  |  |  |  |

## Game-centre accuracy — latest_pregame (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 6.37 | 7.61 | 0.23 | 8.83 | 10.00 | -1.63 | 0.219 |
| DATA_ONLY | 15 | 1 | 5.90 | 6.95 | 1.25 | 10.44 | 11.41 | -0.59 | 0.190 |
| HYBRID_30 | 15 | 1 | 6.19 | 7.25 | 0.54 | 9.25 | 10.33 | -1.32 | 0.211 |
| market at snapshot | 15 | 1 | 6.37 | 7.61 | 0.23 | 8.83 | 10.00 | -1.63 | - |
| market at close | 15 | 1 | 6.50 | 7.59 | 0.23 | 8.93 | 10.12 | -1.73 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | -0.467 | 0.894 | [-2.219, 1.284] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 1.605 | 0.777 | [0.083, 3.127] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | -0.178 | 0.268 | [-0.703, 0.348] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.416 | 0.250 | [-0.075, 0.907] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | 0.290 | 0.630 | [-0.944, 1.523] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -1.189 | 0.539 | [-2.245, -0.134] | 0.733 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | -0.467 | 0.894 | [-2.219, 1.284] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 1.605 | 0.777 | [0.083, 3.127] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | -0.178 | 0.268 | [-0.703, 0.348] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.416 | 0.250 | [-0.075, 0.907] | 0.333 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | -0.133 | 0.103 | [-0.335, 0.069] | 0.200 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | -0.100 | 0.148 | [-0.390, 0.190] | 0.133 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | -0.601 | 0.846 | [-2.259, 1.058] | 0.533 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 1.505 | 0.791 | [-0.044, 3.055] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | -0.311 | 0.232 | [-0.765, 0.143] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | 0.316 | 0.289 | [-0.251, 0.883] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 4 | 0 | 11 | 0 | 1.000 | 0.467 | 2.89 |
| DATA_ONLY | total | 15 | 1 | 3 | 11 | 0 | 0.250 | 0.267 | 2.97 |
| HYBRID_30 | margin | 15 | 4 | 0 | 11 | 0 | 1.000 | 0.533 | 0.87 |
| HYBRID_30 | total | 15 | 1 | 3 | 11 | 0 | 0.250 | 0.333 | 0.89 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 4.13 | 3.50 | 1.000 |
| DATA_ONLY | margin | 1-2 | 4 | 4.52 | 4.88 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 4 | 6.85 | 7.00 | 1.000 |
| DATA_ONLY | margin | >5 | 3 | 3.03 | 5.00 | 1.000 |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.88 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 3 | 13.68 | 12.83 | 1.000 |
| DATA_ONLY | total | 3-5 | 6 | 8.82 | 7.00 | - |
| DATA_ONLY | total | >5 | 2 | 15.67 | 10.25 | 0.000 |
| HYBRID_30 | margin | <=1 | 9 | 5.92 | 5.89 | 1.000 |
| HYBRID_30 | margin | 1-2 | 6 | 6.59 | 7.08 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 8 | 8.91 | 8.94 | 0.333 |
| HYBRID_30 | total | 1-2 | 7 | 9.64 | 8.71 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Game-centre accuracy — T-24h (14 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 14 | 1 | 6.32 | 7.60 | 0.68 | 8.75 | 9.88 | -1.04 | 0.210 |
| DATA_ONLY | 14 | 1 | 5.86 | 6.98 | 1.80 | 10.42 | 11.46 | 0.13 | 0.176 |
| HYBRID_30 | 14 | 1 | 6.14 | 7.26 | 1.02 | 9.18 | 10.27 | -0.69 | 0.197 |
| market at snapshot | 14 | 1 | 6.32 | 7.60 | 0.68 | 8.75 | 9.88 | -1.04 | - |
| market at close | 14 | 1 | 6.57 | 7.72 | 0.64 | 8.61 | 9.84 | -0.89 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 14 | margin | -0.462 | 0.919 | [-2.263, 1.338] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 14 | total | 1.672 | 0.730 | [0.241, 3.104] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | margin | -0.179 | 0.276 | [-0.719, 0.361] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 14 | total | 0.431 | 0.244 | [-0.047, 0.910] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | margin | 0.283 | 0.647 | [-0.986, 1.552] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 14 | total | -1.241 | 0.501 | [-2.223, -0.259] | 0.786 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 14 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 14 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | margin | -0.462 | 0.919 | [-2.263, 1.338] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 14 | total | 1.672 | 0.730 | [0.241, 3.104] | 0.286 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | margin | -0.179 | 0.276 | [-0.719, 0.361] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 14 | total | 0.431 | 0.244 | [-0.047, 0.910] | 0.286 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | margin | -0.250 | 0.126 | [-0.496, -0.004] | 0.357 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 14 | total | 0.143 | 0.199 | [-0.247, 0.533] | 0.214 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | margin | -0.712 | 0.900 | [-2.476, 1.051] | 0.571 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 14 | total | 1.815 | 0.786 | [0.276, 3.355] | 0.214 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | margin | -0.429 | 0.274 | [-0.966, 0.108] | 0.786 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 14 | total | 0.574 | 0.329 | [-0.071, 1.220] | 0.286 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 14 | 4 | 2 | 8 | 0 | 0.667 | 0.500 | 2.92 |
| DATA_ONLY | total | 14 | 4 | 4 | 6 | 0 | 0.500 | 0.286 | 2.70 |
| HYBRID_30 | margin | 14 | 4 | 2 | 8 | 0 | 0.667 | 0.571 | 0.88 |
| HYBRID_30 | total | 14 | 4 | 4 | 6 | 0 | 0.500 | 0.286 | 0.81 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 4.29 | 4.00 | 0.667 |
| DATA_ONLY | margin | 1-2 | 2 | 3.48 | 4.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 5 | 6.58 | 5.50 | 0.667 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 5 | 8.59 | 8.50 | 0.667 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 2 | 14.71 | 12.00 | 0.000 |
| DATA_ONLY | total | 3-5 | 6 | 10.09 | 8.17 | 0.500 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.00 | - |
| HYBRID_30 | margin | <=1 | 9 | 6.15 | 6.22 | 0.600 |
| HYBRID_30 | margin | 1-2 | 5 | 6.13 | 6.50 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 7 | 9.75 | 9.50 | 0.500 |
| HYBRID_30 | total | 1-2 | 7 | 8.61 | 8.00 | 0.500 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 14}; DATA_ONLY quality states: {'OK': 14}; close centre status: {'OK': 14}.

## Game-centre accuracy — T-6h (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 6.23 | 7.46 | 0.17 | 8.97 | 10.06 | -1.63 | 0.216 |
| DATA_ONLY | 15 | 1 | 5.90 | 6.95 | 1.25 | 10.44 | 11.42 | -0.60 | 0.192 |
| HYBRID_30 | 15 | 1 | 6.10 | 7.16 | 0.49 | 9.34 | 10.38 | -1.32 | 0.204 |
| market at snapshot | 15 | 1 | 6.23 | 7.46 | 0.17 | 8.97 | 10.06 | -1.63 | - |
| market at close | 15 | 1 | 6.50 | 7.59 | 0.23 | 8.93 | 10.12 | -1.73 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | -0.331 | 0.855 | [-2.007, 1.344] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 1.478 | 0.715 | [0.077, 2.879] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | -0.137 | 0.257 | [-0.640, 0.366] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.378 | 0.236 | [-0.084, 0.839] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | 0.194 | 0.602 | [-0.986, 1.374] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -1.100 | 0.493 | [-2.066, -0.135] | 0.733 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | -0.331 | 0.855 | [-2.007, 1.344] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 1.478 | 0.715 | [0.077, 2.879] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | -0.137 | 0.257 | [-0.640, 0.366] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.378 | 0.236 | [-0.084, 0.839] | 0.333 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | -0.267 | 0.108 | [-0.478, -0.056] | 0.333 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | 0.033 | 0.114 | [-0.190, 0.257] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | -0.598 | 0.845 | [-2.255, 1.059] | 0.533 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 1.511 | 0.792 | [-0.041, 3.063] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | -0.404 | 0.260 | [-0.914, 0.106] | 0.733 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | 0.411 | 0.308 | [-0.194, 1.015] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 3 | 2 | 10 | 0 | 0.600 | 0.467 | 2.76 |
| DATA_ONLY | total | 15 | 2 | 6 | 7 | 0 | 0.250 | 0.333 | 2.78 |
| HYBRID_30 | margin | 15 | 3 | 2 | 10 | 0 | 0.600 | 0.533 | 0.83 |
| HYBRID_30 | total | 15 | 2 | 6 | 7 | 0 | 0.250 | 0.333 | 0.83 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 4.29 | 3.83 | 0.667 |
| DATA_ONLY | margin | 1-2 | 3 | 4.49 | 4.50 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 5 | 6.58 | 5.60 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.25 | 0.000 |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.75 | 0.000 |
| DATA_ONLY | total | 1-2 | 1 | 11.68 | 10.50 | 1.000 |
| DATA_ONLY | total | 2-3 | 2 | 14.68 | 14.75 | - |
| DATA_ONLY | total | 3-5 | 7 | 10.19 | 8.00 | 0.200 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 10 | 6.12 | 6.15 | 0.750 |
| HYBRID_30 | margin | 1-2 | 5 | 6.04 | 6.40 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 9 | 9.37 | 9.11 | 0.250 |
| HYBRID_30 | total | 1-2 | 6 | 9.30 | 8.75 | 0.250 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Game-centre accuracy — T-90m (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 6.33 | 7.57 | 0.20 | 8.93 | 10.10 | -1.60 | 0.220 |
| DATA_ONLY | 15 | 1 | 5.90 | 6.95 | 1.25 | 10.44 | 11.41 | -0.59 | 0.190 |
| HYBRID_30 | 15 | 1 | 6.17 | 7.22 | 0.52 | 9.32 | 10.41 | -1.30 | 0.212 |
| market at snapshot | 15 | 1 | 6.33 | 7.57 | 0.20 | 8.93 | 10.10 | -1.60 | - |
| market at close | 15 | 1 | 6.50 | 7.59 | 0.23 | 8.93 | 10.12 | -1.73 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | -0.434 | 0.880 | [-2.158, 1.290] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 1.505 | 0.728 | [0.078, 2.932] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | -0.168 | 0.264 | [-0.685, 0.349] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.386 | 0.236 | [-0.077, 0.849] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | 0.266 | 0.619 | [-0.948, 1.480] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -1.119 | 0.505 | [-2.110, -0.129] | 0.733 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | -0.434 | 0.880 | [-2.158, 1.290] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 1.505 | 0.728 | [0.078, 2.932] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | -0.168 | 0.264 | [-0.685, 0.349] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.386 | 0.236 | [-0.077, 0.849] | 0.333 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | -0.167 | 0.105 | [-0.373, 0.040] | 0.267 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | 0.000 | 0.120 | [-0.234, 0.234] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | -0.601 | 0.846 | [-2.259, 1.058] | 0.533 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 1.505 | 0.791 | [-0.044, 3.055] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | -0.335 | 0.243 | [-0.812, 0.143] | 0.733 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | 0.386 | 0.307 | [-0.216, 0.988] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 4 | 1 | 10 | 0 | 0.800 | 0.467 | 2.86 |
| DATA_ONLY | total | 15 | 1 | 5 | 9 | 0 | 0.167 | 0.267 | 2.74 |
| HYBRID_30 | margin | 15 | 4 | 1 | 10 | 0 | 0.800 | 0.533 | 0.86 |
| HYBRID_30 | total | 15 | 1 | 5 | 9 | 0 | 0.167 | 0.333 | 0.82 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 4.29 | 4.00 | 0.667 |
| DATA_ONLY | margin | 1-2 | 3 | 4.49 | 4.50 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 5 | 6.57 | 5.70 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.88 | 0.000 |
| DATA_ONLY | total | 1-2 | 2 | 11.22 | 11.50 | 0.500 |
| DATA_ONLY | total | 2-3 | 1 | 18.62 | 16.00 | - |
| DATA_ONLY | total | 3-5 | 7 | 10.18 | 8.00 | 0.000 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 9 | 5.84 | 5.78 | 0.750 |
| HYBRID_30 | margin | 1-2 | 6 | 6.65 | 7.17 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 8 | 8.95 | 9.00 | 0.250 |
| HYBRID_30 | total | 1-2 | 7 | 9.74 | 8.86 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Game-centre accuracy — T-30m (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 6.37 | 7.61 | 0.23 | 8.83 | 10.00 | -1.63 | 0.219 |
| DATA_ONLY | 15 | 1 | 5.90 | 6.95 | 1.25 | 10.44 | 11.41 | -0.59 | 0.190 |
| HYBRID_30 | 15 | 1 | 6.19 | 7.25 | 0.54 | 9.25 | 10.33 | -1.32 | 0.210 |
| market at snapshot | 15 | 1 | 6.37 | 7.61 | 0.23 | 8.83 | 10.00 | -1.63 | - |
| market at close | 15 | 1 | 6.50 | 7.59 | 0.23 | 8.93 | 10.12 | -1.73 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | -0.467 | 0.894 | [-2.219, 1.284] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 1.605 | 0.777 | [0.083, 3.127] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | -0.178 | 0.268 | [-0.703, 0.348] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.416 | 0.250 | [-0.075, 0.907] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | 0.290 | 0.630 | [-0.944, 1.523] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -1.189 | 0.539 | [-2.245, -0.134] | 0.733 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | -0.467 | 0.894 | [-2.219, 1.284] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 1.605 | 0.777 | [0.083, 3.127] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | -0.178 | 0.268 | [-0.703, 0.348] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.416 | 0.250 | [-0.075, 0.907] | 0.333 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | -0.133 | 0.103 | [-0.335, 0.069] | 0.200 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | -0.100 | 0.148 | [-0.390, 0.190] | 0.133 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | -0.601 | 0.846 | [-2.259, 1.058] | 0.533 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 1.505 | 0.791 | [-0.044, 3.055] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | -0.311 | 0.232 | [-0.765, 0.143] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | 0.316 | 0.289 | [-0.251, 0.883] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 4 | 0 | 11 | 0 | 1.000 | 0.467 | 2.89 |
| DATA_ONLY | total | 15 | 1 | 3 | 11 | 0 | 0.250 | 0.267 | 2.97 |
| HYBRID_30 | margin | 15 | 4 | 0 | 11 | 0 | 1.000 | 0.533 | 0.87 |
| HYBRID_30 | total | 15 | 1 | 3 | 11 | 0 | 0.250 | 0.333 | 0.89 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 4.13 | 3.50 | 1.000 |
| DATA_ONLY | margin | 1-2 | 4 | 4.52 | 4.88 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 4 | 6.85 | 7.00 | 1.000 |
| DATA_ONLY | margin | >5 | 3 | 3.03 | 5.00 | 1.000 |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.88 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 3 | 13.68 | 12.83 | 1.000 |
| DATA_ONLY | total | 3-5 | 6 | 8.82 | 7.00 | - |
| DATA_ONLY | total | >5 | 2 | 15.67 | 10.25 | 0.000 |
| HYBRID_30 | margin | <=1 | 9 | 5.92 | 5.89 | 1.000 |
| HYBRID_30 | margin | 1-2 | 6 | 6.59 | 7.08 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 8 | 8.91 | 8.94 | 0.333 |
| HYBRID_30 | total | 1-2 | 7 | 9.64 | 8.71 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Contract pricing — latest_pregame (1165 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1165 | 0.1302 | 0.4019 | 0.418 | 0.403 | 1165 | 0.1302 | 0.1293 | 0.1310 |
| DATA_ONLY | 1165 | 0.1316 | 0.4054 | 0.432 | 0.403 | 1165 | 0.1316 | 0.1293 | 0.1310 |
| HYBRID_30 | 1165 | 0.1288 | 0.3993 | 0.420 | 0.403 | 1165 | 0.1288 | 0.1293 | 0.1310 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1165 | 15 | 0.00146 | [-0.01610, 0.01772] | 0.00146 | [-0.01610, 0.01772] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1165 | 15 | -0.00134 | [-0.00673, 0.00359] | -0.00134 | [-0.00673, 0.00359] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1165 | 15 | -0.00280 | [-0.01511, 0.01017] | -0.00280 | [-0.01511, 0.01017] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1165 | 15 | - | - | 0.00092 | [-0.00028, 0.00229] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1153 | 15 | - | - | 0.00047 | [-0.00081, 0.00190] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1165 | 15 | - | - | 0.00238 | [-0.01592, 0.01880] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1153 | 15 | - | - | 0.00195 | [-0.01645, 0.01857] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1165 | 15 | - | - | -0.00043 | [-0.00589, 0.00478] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1153 | 15 | - | - | -0.00088 | [-0.00633, 0.00455] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 381, 'TEAM_TOTAL': 409, 'TOTAL': 285}; settlement: {'SETTLED': 1165}; close: {'OK': 1153, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 176 / 0.054 / 0.006 | 175 / 0.055 / 0.006 | 177 / 0.055 / 0.006 |
| 0.10-0.20 | 187 / 0.145 / 0.048 | 180 / 0.147 / 0.050 | 184 / 0.146 / 0.071 |
| 0.20-0.30 | 143 / 0.249 / 0.245 | 127 / 0.250 / 0.220 | 136 / 0.251 / 0.184 |
| 0.30-0.40 | 114 / 0.351 / 0.342 | 115 / 0.350 / 0.322 | 113 / 0.350 / 0.345 |
| 0.40-0.50 | 111 / 0.450 / 0.432 | 110 / 0.446 / 0.464 | 118 / 0.449 / 0.432 |
| 0.50-0.60 | 122 / 0.547 / 0.557 | 103 / 0.551 / 0.466 | 120 / 0.548 / 0.542 |
| 0.60-0.70 | 69 / 0.650 / 0.638 | 91 / 0.647 / 0.593 | 78 / 0.652 / 0.692 |
| 0.70-0.80 | 66 / 0.756 / 0.803 | 72 / 0.748 / 0.806 | 58 / 0.754 / 0.793 |
| 0.80-0.90 | 61 / 0.854 / 0.934 | 66 / 0.845 / 0.894 | 62 / 0.847 / 0.919 |
| 0.90-1.00 | 116 / 0.958 / 1.000 | 126 / 0.956 / 0.992 | 119 / 0.954 / 1.000 |

## Contract pricing — T-24h (1087 contracts, 14 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1087 | 0.1283 | 0.3976 | 0.418 | 0.397 | 1087 | 0.1283 | 0.1291 | 0.1298 |
| DATA_ONLY | 1087 | 0.1315 | 0.4055 | 0.433 | 0.397 | 1087 | 0.1315 | 0.1291 | 0.1298 |
| HYBRID_30 | 1087 | 0.1281 | 0.3974 | 0.421 | 0.397 | 1087 | 0.1281 | 0.1291 | 0.1298 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1087 | 14 | 0.00326 | [-0.01498, 0.02130] | 0.00326 | [-0.01498, 0.02130] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1087 | 14 | -0.00016 | [-0.00750, 0.00706] | -0.00016 | [-0.00750, 0.00706] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1087 | 14 | -0.00342 | [-0.01507, 0.00864] | -0.00342 | [-0.01507, 0.00864] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1087 | 14 | - | - | -0.00087 | [-0.00223, 0.00030] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1075 | 14 | - | - | -0.00007 | [-0.00153, 0.00142] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1087 | 14 | - | - | 0.00239 | [-0.01543, 0.02008] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1075 | 14 | - | - | 0.00322 | [-0.01516, 0.02174] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1087 | 14 | - | - | -0.00103 | [-0.00820, 0.00591] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1075 | 14 | - | - | -0.00023 | [-0.00774, 0.00699] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 56, 'GAME_WINNER': 28, 'SPREAD': 356, 'TEAM_TOTAL': 381, 'TOTAL': 266}; settlement: {'SETTLED': 1087}; close: {'OK': 1075, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 167 / 0.054 / 0.006 | 161 / 0.055 / 0.006 | 162 / 0.055 / 0.006 |
| 0.10-0.20 | 172 / 0.144 / 0.052 | 168 / 0.145 / 0.054 | 178 / 0.147 / 0.056 |
| 0.20-0.30 | 135 / 0.249 / 0.222 | 121 / 0.250 / 0.215 | 125 / 0.253 / 0.216 |
| 0.30-0.40 | 101 / 0.349 / 0.337 | 104 / 0.351 / 0.317 | 102 / 0.350 / 0.314 |
| 0.40-0.50 | 111 / 0.454 / 0.387 | 103 / 0.444 / 0.427 | 115 / 0.449 / 0.417 |
| 0.50-0.60 | 105 / 0.548 / 0.571 | 96 / 0.549 / 0.438 | 104 / 0.552 / 0.538 |
| 0.60-0.70 | 64 / 0.644 / 0.625 | 86 / 0.649 / 0.593 | 74 / 0.650 / 0.608 |
| 0.70-0.80 | 67 / 0.755 / 0.806 | 71 / 0.751 / 0.789 | 60 / 0.751 / 0.833 |
| 0.80-0.90 | 54 / 0.854 / 0.926 | 58 / 0.846 / 0.897 | 58 / 0.849 / 0.931 |
| 0.90-1.00 | 111 / 0.957 / 1.000 | 119 / 0.956 / 0.992 | 109 / 0.956 / 1.000 |

## Contract pricing — T-6h (1165 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1165 | 0.1291 | 0.3997 | 0.419 | 0.403 | 1165 | 0.1291 | 0.1293 | 0.1310 |
| DATA_ONLY | 1165 | 0.1321 | 0.4065 | 0.431 | 0.403 | 1165 | 0.1321 | 0.1293 | 0.1310 |
| HYBRID_30 | 1165 | 0.1289 | 0.3985 | 0.417 | 0.403 | 1165 | 0.1289 | 0.1293 | 0.1310 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1165 | 15 | 0.00296 | [-0.01320, 0.01801] | 0.00296 | [-0.01320, 0.01801] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1165 | 15 | -0.00025 | [-0.00563, 0.00463] | -0.00025 | [-0.00563, 0.00463] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1165 | 15 | -0.00321 | [-0.01502, 0.00866] | -0.00321 | [-0.01502, 0.00866] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1165 | 15 | - | - | -0.00013 | [-0.00202, 0.00153] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1153 | 15 | - | - | -0.00058 | [-0.00254, 0.00124] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1165 | 15 | - | - | 0.00283 | [-0.01468, 0.01913] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1153 | 15 | - | - | 0.00242 | [-0.01556, 0.01894] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1165 | 15 | - | - | -0.00038 | [-0.00697, 0.00522] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1153 | 15 | - | - | -0.00082 | [-0.00747, 0.00470] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 381, 'TEAM_TOTAL': 409, 'TOTAL': 285}; settlement: {'SETTLED': 1165}; close: {'OK': 1153, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 177 / 0.054 / 0.006 | 175 / 0.054 / 0.000 | 185 / 0.054 / 0.005 |
| 0.10-0.20 | 180 / 0.145 / 0.056 | 181 / 0.146 / 0.061 | 182 / 0.148 / 0.071 |
| 0.20-0.30 | 147 / 0.249 / 0.218 | 130 / 0.251 / 0.223 | 142 / 0.252 / 0.211 |
| 0.30-0.40 | 112 / 0.351 / 0.375 | 110 / 0.351 / 0.336 | 106 / 0.348 / 0.349 |
| 0.40-0.50 | 112 / 0.449 / 0.411 | 111 / 0.446 / 0.432 | 126 / 0.448 / 0.421 |
| 0.50-0.60 | 116 / 0.546 / 0.534 | 104 / 0.551 / 0.481 | 108 / 0.549 / 0.565 |
| 0.60-0.70 | 79 / 0.645 / 0.646 | 94 / 0.649 / 0.606 | 75 / 0.650 / 0.653 |
| 0.70-0.80 | 63 / 0.753 / 0.810 | 71 / 0.752 / 0.789 | 62 / 0.754 / 0.839 |
| 0.80-0.90 | 67 / 0.853 / 0.940 | 65 / 0.848 / 0.908 | 62 / 0.852 / 0.919 |
| 0.90-1.00 | 112 / 0.958 / 1.000 | 124 / 0.957 / 0.992 | 117 / 0.958 / 1.000 |

## Contract pricing — T-90m (1165 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1165 | 0.1294 | 0.4002 | 0.418 | 0.403 | 1165 | 0.1294 | 0.1292 | 0.1310 |
| DATA_ONLY | 1165 | 0.1319 | 0.4061 | 0.431 | 0.403 | 1165 | 0.1319 | 0.1292 | 0.1310 |
| HYBRID_30 | 1165 | 0.1309 | 0.4038 | 0.419 | 0.403 | 1165 | 0.1309 | 0.1292 | 0.1310 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1165 | 15 | 0.00255 | [-0.01485, 0.01921] | 0.00255 | [-0.01485, 0.01921] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1165 | 15 | 0.00156 | [-0.00491, 0.00734] | 0.00156 | [-0.00491, 0.00734] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1165 | 15 | -0.00099 | [-0.01258, 0.01102] | -0.00099 | [-0.01258, 0.01102] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1165 | 15 | - | - | 0.00022 | [-0.00116, 0.00138] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1153 | 15 | - | - | -0.00034 | [-0.00187, 0.00099] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1165 | 15 | - | - | 0.00277 | [-0.01516, 0.01930] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1153 | 15 | - | - | 0.00224 | [-0.01596, 0.01881] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1165 | 15 | - | - | 0.00179 | [-0.00419, 0.00745] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1153 | 15 | - | - | 0.00125 | [-0.00482, 0.00702] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 381, 'TEAM_TOTAL': 409, 'TOTAL': 285}; settlement: {'SETTLED': 1165}; close: {'OK': 1153, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 180 / 0.055 / 0.006 | 177 / 0.055 / 0.006 | 178 / 0.054 / 0.006 |
| 0.10-0.20 | 181 / 0.145 / 0.044 | 178 / 0.147 / 0.051 | 185 / 0.147 / 0.070 |
| 0.20-0.30 | 143 / 0.248 / 0.245 | 127 / 0.249 / 0.220 | 137 / 0.251 / 0.204 |
| 0.30-0.40 | 118 / 0.350 / 0.347 | 115 / 0.350 / 0.339 | 112 / 0.350 / 0.375 |
| 0.40-0.50 | 105 / 0.450 / 0.410 | 109 / 0.445 / 0.440 | 125 / 0.450 / 0.424 |
| 0.50-0.60 | 124 / 0.547 / 0.565 | 105 / 0.551 / 0.486 | 115 / 0.551 / 0.530 |
| 0.60-0.70 | 71 / 0.649 / 0.648 | 90 / 0.647 / 0.589 | 76 / 0.654 / 0.658 |
| 0.70-0.80 | 62 / 0.754 / 0.806 | 74 / 0.749 / 0.797 | 56 / 0.754 / 0.821 |
| 0.80-0.90 | 65 / 0.851 / 0.923 | 64 / 0.846 / 0.891 | 65 / 0.848 / 0.923 |
| 0.90-1.00 | 116 / 0.957 / 1.000 | 126 / 0.956 / 0.992 | 116 / 0.957 / 1.000 |

## Contract pricing — T-30m (1165 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1165 | 0.1302 | 0.4020 | 0.418 | 0.403 | 1165 | 0.1302 | 0.1292 | 0.1310 |
| DATA_ONLY | 1165 | 0.1317 | 0.4056 | 0.432 | 0.403 | 1165 | 0.1317 | 0.1292 | 0.1310 |
| HYBRID_30 | 1165 | 0.1287 | 0.3990 | 0.420 | 0.403 | 1165 | 0.1287 | 0.1292 | 0.1310 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1165 | 15 | 0.00144 | [-0.01612, 0.01770] | 0.00144 | [-0.01612, 0.01770] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1165 | 15 | -0.00156 | [-0.00686, 0.00344] | -0.00156 | [-0.00686, 0.00344] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1165 | 15 | -0.00300 | [-0.01521, 0.00979] | -0.00300 | [-0.01521, 0.00979] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1165 | 15 | - | - | 0.00103 | [-0.00016, 0.00229] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1153 | 15 | - | - | 0.00054 | [-0.00072, 0.00194] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1165 | 15 | - | - | 0.00247 | [-0.01574, 0.01889] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1153 | 15 | - | - | 0.00200 | [-0.01636, 0.01863] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1165 | 15 | - | - | -0.00053 | [-0.00609, 0.00473] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1153 | 15 | - | - | -0.00103 | [-0.00651, 0.00443] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 381, 'TEAM_TOTAL': 409, 'TOTAL': 285}; settlement: {'SETTLED': 1165}; close: {'OK': 1153, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 176 / 0.054 / 0.006 | 175 / 0.055 / 0.006 | 177 / 0.055 / 0.006 |
| 0.10-0.20 | 186 / 0.144 / 0.048 | 180 / 0.147 / 0.050 | 183 / 0.146 / 0.066 |
| 0.20-0.30 | 143 / 0.249 / 0.245 | 126 / 0.250 / 0.222 | 137 / 0.250 / 0.190 |
| 0.30-0.40 | 115 / 0.351 / 0.339 | 116 / 0.350 / 0.319 | 113 / 0.350 / 0.345 |
| 0.40-0.50 | 109 / 0.450 / 0.431 | 110 / 0.446 / 0.464 | 118 / 0.449 / 0.432 |
| 0.50-0.60 | 123 / 0.546 / 0.553 | 103 / 0.551 / 0.466 | 120 / 0.548 / 0.542 |
| 0.60-0.70 | 70 / 0.649 / 0.643 | 91 / 0.647 / 0.593 | 78 / 0.652 / 0.692 |
| 0.70-0.80 | 66 / 0.756 / 0.803 | 72 / 0.748 / 0.806 | 58 / 0.754 / 0.793 |
| 0.80-0.90 | 61 / 0.855 / 0.934 | 66 / 0.845 / 0.894 | 62 / 0.847 / 0.919 |
| 0.90-1.00 | 116 / 0.958 / 1.000 | 126 / 0.956 / 0.992 | 119 / 0.954 / 1.000 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 14 | 3 | 2 | 1 | 8 | 0 | 0.667 [0.208, 0.939] | 0.545 | 0.545 | 0.05 |
| T-24h | DATA_ONLY | total | 14 | 5 | 2 | 3 | 4 | 0 | 0.400 [0.118, 0.769] | 0.222 | 0.111 | -0.22 |
| T-24h | HYBRID_30 (derived) | margin | 14 | 9 | 1 | 0 | 4 | 0 | 1.000 [0.207, 1.000] | 0.600 | 0.600 | 0.10 |
| T-24h | HYBRID_30 (derived) | total | 14 | 7 | 2 | 2 | 3 | 0 | 0.500 [0.150, 0.850] | 0.286 | 0.286 | -0.07 |
| T-6h | DATA_ONLY | margin | 15 | 3 | 1 | 1 | 10 | 0 | 0.500 [0.095, 0.905] | 0.500 | 0.500 | 0.04 |
| T-6h | DATA_ONLY | total | 15 | 4 | 2 | 5 | 4 | 0 | 0.286 [0.082, 0.641] | 0.273 | 0.182 | -0.18 |
| T-6h | HYBRID_30 (derived) | margin | 15 | 10 | 0 | 1 | 4 | 0 | 0.000 [0.000, 0.793] | 0.600 | 0.600 | -0.10 |
| T-6h | HYBRID_30 (derived) | total | 15 | 9 | 1 | 3 | 2 | 0 | 0.250 [0.046, 0.699] | 0.333 | 0.333 | -0.25 |
| T-90m | DATA_ONLY | margin | 15 | 3 | 2 | 0 | 10 | 0 | 1.000 [0.342, 1.000] | 0.500 | 0.500 | 0.12 |
| T-90m | DATA_ONLY | total | 15 | 4 | 1 | 3 | 7 | 0 | 0.250 [0.046, 0.699] | 0.182 | 0.182 | -0.18 |
| T-90m | HYBRID_30 (derived) | margin | 15 | 9 | 1 | 0 | 5 | 0 | 1.000 [0.207, 1.000] | 0.667 | 0.667 | 0.08 |
| T-90m | HYBRID_30 (derived) | total | 15 | 8 | 0 | 2 | 5 | 0 | 0.000 [0.000, 0.658] | 0.143 | 0.143 | -0.21 |
| T-30m | DATA_ONLY | margin | 15 | 2 | 3 | 0 | 10 | 0 | 1.000 [0.439, 1.000] | 0.538 | 0.538 | 0.15 |
| T-30m | DATA_ONLY | total | 15 | 4 | 1 | 1 | 9 | 0 | 0.500 [0.095, 0.905] | 0.182 | 0.182 | 0.14 |
| T-30m | HYBRID_30 (derived) | margin | 15 | 9 | 2 | 0 | 4 | 0 | 1.000 [0.342, 1.000] | 0.667 | 0.667 | 0.17 |
| T-30m | HYBRID_30 (derived) | total | 15 | 8 | 0 | 1 | 6 | 0 | 0.000 [0.000, 0.793] | 0.143 | 0.143 | -0.07 |
| latest_pregame | DATA_ONLY | margin | 15 | 2 | 3 | 0 | 10 | 0 | 1.000 [0.439, 1.000] | 0.538 | 0.538 | 0.15 |
| latest_pregame | DATA_ONLY | total | 15 | 4 | 1 | 1 | 9 | 0 | 0.500 [0.095, 0.905] | 0.182 | 0.182 | 0.14 |
| latest_pregame | HYBRID_30 (derived) | margin | 15 | 9 | 2 | 0 | 4 | 0 | 1.000 [0.342, 1.000] | 0.667 | 0.667 | 0.17 |
| latest_pregame | HYBRID_30 (derived) | total | 15 | 8 | 0 | 1 | 6 | 0 | 0.000 [0.000, 0.793] | 0.143 | 0.143 | -0.07 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 2 | 1 | 0 | 1 | 0 | 1.000 |
| margin | 1-2 | 4 | 0 | 0 | 4 | 0 | - |
| margin | 2-3 | 2 | 0 | 0 | 2 | 0 | - |
| margin | 3-5 | 4 | 2 | 0 | 2 | 0 | 1.000 |
| margin | >5 | 3 | 1 | 0 | 2 | 0 | 1.000 |
| total | <=1 | 4 | 0 | 2 | 2 | 0 | 0.000 |
| total | 1-2 | 0 | 0 | 0 | 0 | 0 | - |
| total | 2-3 | 3 | 1 | 0 | 2 | 0 | 1.000 |
| total | 3-5 | 6 | 0 | 0 | 6 | 0 | - |
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
| 2026_04_DET_CAR | NO | 0 | 0 | 62 | 62 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
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

