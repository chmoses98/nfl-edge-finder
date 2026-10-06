# Three-arm game-centre experiment — 2026 week 4

> **INSUFFICIENT EVIDENCE.** 16 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 1307 | 16 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 16 | 16 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 16 | 16 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 16 | 16 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 16 | 16 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_ATL_NO | 2026-10-06T00:15 | 34 | CURRENT | 0.50 | 47.50 | -21 | 69 | 0.5/47.5 (kalshi_implied) | 0.5/47.0 (OK) |
|  |  |  | DATA_ONLY | 0.79 | 44.32 |  |  |  |  |
|  |  |  | HYBRID_30 | 0.59 | 46.55 |  |  |  |  |

## Game-centre accuracy — latest_pregame (16 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 1 | 7.31 | 9.12 | 1.56 | 9.62 | 11.08 | -2.88 | 0.223 |
| DATA_ONLY | 16 | 1 | 6.89 | 8.65 | 2.54 | 11.33 | 12.66 | -2.10 | 0.196 |
| HYBRID_30 | 16 | 1 | 7.15 | 8.86 | 1.85 | 10.07 | 11.47 | -2.64 | 0.215 |
| market at snapshot | 16 | 1 | 7.31 | 9.12 | 1.56 | 9.62 | 11.08 | -2.88 | - |
| market at close | 16 | 1 | 7.44 | 9.11 | 1.56 | 9.75 | 11.24 | -3.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | -0.420 | 0.837 | [-2.062, 1.221] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | 1.704 | 0.733 | [0.267, 3.141] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | -0.161 | 0.251 | [-0.654, 0.331] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | 0.450 | 0.237 | [-0.014, 0.913] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | 0.259 | 0.590 | [-0.897, 1.415] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -1.254 | 0.508 | [-2.250, -0.258] | 0.750 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | -0.420 | 0.837 | [-2.062, 1.221] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | 1.704 | 0.733 | [0.267, 3.141] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | -0.161 | 0.251 | [-0.654, 0.331] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | 0.450 | 0.237 | [-0.014, 0.913] | 0.312 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | -0.125 | 0.097 | [-0.315, 0.065] | 0.188 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | -0.125 | 0.141 | [-0.401, 0.151] | 0.188 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | -0.545 | 0.793 | [-2.101, 1.010] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 1.579 | 0.743 | [0.122, 3.036] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | -0.286 | 0.218 | [-0.714, 0.141] | 0.625 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | 0.325 | 0.271 | [-0.206, 0.855] | 0.375 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 4 | 0 | 12 | 0 | 1.000 | 0.438 | 2.73 |
| DATA_ONLY | total | 16 | 2 | 3 | 11 | 0 | 0.400 | 0.250 | 2.98 |
| HYBRID_30 | margin | 16 | 4 | 0 | 12 | 0 | 1.000 | 0.500 | 0.82 |
| HYBRID_30 | total | 16 | 2 | 3 | 11 | 0 | 0.400 | 0.312 | 0.89 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 10.01 | 9.50 | 1.000 |
| DATA_ONLY | margin | 1-2 | 4 | 4.52 | 4.88 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 4 | 6.85 | 7.00 | 1.000 |
| DATA_ONLY | margin | >5 | 3 | 3.03 | 5.00 | 1.000 |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.88 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 3 | 13.68 | 12.83 | 1.000 |
| DATA_ONLY | total | 3-5 | 7 | 11.09 | 9.07 | 1.000 |
| DATA_ONLY | total | >5 | 2 | 15.67 | 10.25 | 0.000 |
| HYBRID_30 | margin | <=1 | 10 | 7.49 | 7.45 | 1.000 |
| HYBRID_30 | margin | 1-2 | 6 | 6.59 | 7.08 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 9 | 10.41 | 10.33 | 0.500 |
| HYBRID_30 | total | 1-2 | 7 | 9.64 | 8.71 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Game-centre accuracy — T-24h (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 7.40 | 9.36 | 2.13 | 9.63 | 11.11 | -2.43 | 0.216 |
| DATA_ONLY | 15 | 1 | 6.92 | 8.79 | 3.14 | 11.35 | 12.74 | -1.51 | 0.184 |
| HYBRID_30 | 15 | 1 | 7.22 | 9.07 | 2.44 | 10.08 | 11.53 | -2.16 | 0.205 |
| market at snapshot | 15 | 1 | 7.40 | 9.36 | 2.13 | 9.63 | 11.11 | -2.43 | - |
| market at close | 15 | 1 | 7.57 | 9.30 | 2.03 | 9.50 | 11.07 | -2.30 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | -0.477 | 0.855 | [-2.153, 1.200] | 0.533 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 1.721 | 0.682 | [0.385, 3.058] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | -0.181 | 0.257 | [-0.683, 0.322] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.451 | 0.228 | [0.004, 0.898] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | 0.296 | 0.603 | [-0.886, 1.478] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -1.271 | 0.467 | [-2.187, -0.355] | 0.800 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | -0.477 | 0.855 | [-2.153, 1.200] | 0.533 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 1.721 | 0.682 | [0.385, 3.058] | 0.267 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | -0.181 | 0.257 | [-0.683, 0.322] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.451 | 0.228 | [0.004, 0.898] | 0.267 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | -0.167 | 0.144 | [-0.448, 0.115] | 0.333 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | 0.133 | 0.186 | [-0.230, 0.497] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | -0.643 | 0.840 | [-2.290, 1.004] | 0.533 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 1.855 | 0.732 | [0.419, 3.290] | 0.200 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | -0.347 | 0.268 | [-0.872, 0.177] | 0.733 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | 0.584 | 0.307 | [-0.017, 1.185] | 0.267 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 5 | 2 | 8 | 0 | 0.714 | 0.533 | 2.77 |
| DATA_ONLY | total | 15 | 4 | 4 | 7 | 0 | 0.500 | 0.267 | 2.68 |
| HYBRID_30 | margin | 15 | 5 | 2 | 8 | 0 | 0.714 | 0.600 | 0.83 |
| HYBRID_30 | total | 15 | 4 | 4 | 7 | 0 | 0.500 | 0.267 | 0.80 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 4 | 8.68 | 8.62 | 0.750 |
| DATA_ONLY | margin | 1-2 | 2 | 3.48 | 4.00 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 5 | 6.58 | 5.50 | 0.667 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 5 | 8.59 | 8.50 | 0.667 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 3 | 17.94 | 15.33 | 0.000 |
| DATA_ONLY | total | 3-5 | 6 | 10.09 | 8.17 | 0.500 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.00 | - |
| HYBRID_30 | margin | <=1 | 10 | 7.76 | 7.85 | 0.667 |
| HYBRID_30 | margin | 1-2 | 5 | 6.13 | 6.50 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 8 | 11.37 | 11.06 | 0.500 |
| HYBRID_30 | total | 1-2 | 7 | 8.61 | 8.00 | 0.500 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Game-centre accuracy — T-6h (16 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 1 | 7.19 | 9.01 | 1.50 | 9.75 | 11.12 | -2.88 | 0.220 |
| DATA_ONLY | 16 | 1 | 6.89 | 8.66 | 2.53 | 11.33 | 12.66 | -2.10 | 0.198 |
| HYBRID_30 | 16 | 1 | 7.06 | 8.79 | 1.81 | 10.16 | 11.51 | -2.64 | 0.209 |
| market at snapshot | 16 | 1 | 7.19 | 9.01 | 1.50 | 9.75 | 11.12 | -2.88 | - |
| market at close | 16 | 1 | 7.44 | 9.11 | 1.56 | 9.75 | 11.24 | -3.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | -0.293 | 0.801 | [-1.862, 1.277] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | 1.584 | 0.677 | [0.257, 2.911] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | -0.123 | 0.241 | [-0.595, 0.349] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | 0.414 | 0.223 | [-0.024, 0.851] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | 0.170 | 0.564 | [-0.935, 1.274] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -1.171 | 0.466 | [-2.084, -0.257] | 0.750 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | -0.293 | 0.801 | [-1.862, 1.277] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | 1.584 | 0.677 | [0.257, 2.911] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | -0.123 | 0.241 | [-0.595, 0.349] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | 0.414 | 0.223 | [-0.024, 0.851] | 0.312 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | -0.250 | 0.102 | [-0.450, -0.050] | 0.312 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | 0.000 | 0.112 | [-0.219, 0.219] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | -0.543 | 0.793 | [-2.096, 1.011] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 1.584 | 0.745 | [0.125, 3.043] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | -0.373 | 0.245 | [-0.854, 0.108] | 0.688 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | 0.414 | 0.288 | [-0.152, 0.979] | 0.375 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 3 | 2 | 11 | 0 | 0.600 | 0.438 | 2.60 |
| DATA_ONLY | total | 16 | 3 | 6 | 7 | 0 | 0.333 | 0.312 | 2.80 |
| HYBRID_30 | margin | 16 | 3 | 2 | 11 | 0 | 0.600 | 0.500 | 0.78 |
| HYBRID_30 | total | 16 | 3 | 6 | 7 | 0 | 0.333 | 0.312 | 0.84 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 4 | 8.67 | 8.25 | 0.667 |
| DATA_ONLY | margin | 1-2 | 3 | 4.49 | 4.50 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 5 | 6.58 | 5.60 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.25 | 0.000 |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.75 | 0.000 |
| DATA_ONLY | total | 1-2 | 1 | 11.68 | 10.50 | 1.000 |
| DATA_ONLY | total | 2-3 | 2 | 14.68 | 14.75 | - |
| DATA_ONLY | total | 3-5 | 8 | 12.01 | 9.69 | 0.333 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 11 | 7.53 | 7.55 | 0.750 |
| HYBRID_30 | margin | 1-2 | 5 | 6.04 | 6.40 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 10 | 10.68 | 10.35 | 0.400 |
| HYBRID_30 | total | 1-2 | 6 | 9.30 | 8.75 | 0.250 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Game-centre accuracy — T-90m (16 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 1 | 7.28 | 9.09 | 1.53 | 9.72 | 11.16 | -2.84 | 0.224 |
| DATA_ONLY | 16 | 1 | 6.89 | 8.65 | 2.54 | 11.33 | 12.66 | -2.10 | 0.197 |
| HYBRID_30 | 16 | 1 | 7.13 | 8.83 | 1.83 | 10.14 | 11.54 | -2.62 | 0.216 |
| market at snapshot | 16 | 1 | 7.28 | 9.09 | 1.53 | 9.72 | 11.16 | -2.84 | - |
| market at close | 16 | 1 | 7.44 | 9.11 | 1.56 | 9.75 | 11.24 | -3.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | -0.389 | 0.824 | [-2.004, 1.226] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | 1.610 | 0.689 | [0.259, 2.961] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | -0.152 | 0.247 | [-0.637, 0.333] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | 0.421 | 0.224 | [-0.018, 0.860] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | 0.237 | 0.580 | [-0.900, 1.374] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -1.189 | 0.478 | [-2.125, -0.253] | 0.750 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | -0.389 | 0.824 | [-2.004, 1.226] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | 1.610 | 0.689 | [0.259, 2.961] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | -0.152 | 0.247 | [-0.637, 0.333] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | 0.421 | 0.224 | [-0.018, 0.860] | 0.312 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | -0.156 | 0.099 | [-0.351, 0.038] | 0.250 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | -0.031 | 0.116 | [-0.259, 0.196] | 0.250 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | -0.545 | 0.793 | [-2.101, 1.010] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 1.579 | 0.743 | [0.122, 3.036] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | -0.308 | 0.229 | [-0.757, 0.141] | 0.688 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | 0.390 | 0.287 | [-0.173, 0.953] | 0.375 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 4 | 1 | 11 | 0 | 0.800 | 0.438 | 2.70 |
| DATA_ONLY | total | 16 | 2 | 5 | 9 | 0 | 0.286 | 0.250 | 2.76 |
| HYBRID_30 | margin | 16 | 4 | 1 | 11 | 0 | 0.800 | 0.500 | 0.81 |
| HYBRID_30 | total | 16 | 2 | 5 | 9 | 0 | 0.286 | 0.312 | 0.83 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 4 | 8.67 | 8.38 | 0.667 |
| DATA_ONLY | margin | 1-2 | 3 | 4.49 | 4.50 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 5 | 6.57 | 5.70 | 1.000 |
| DATA_ONLY | margin | >5 | 2 | 1.82 | 7.50 | - |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.88 | 0.000 |
| DATA_ONLY | total | 1-2 | 2 | 11.22 | 11.50 | 0.500 |
| DATA_ONLY | total | 2-3 | 1 | 18.62 | 16.00 | - |
| DATA_ONLY | total | 3-5 | 8 | 12.00 | 9.69 | 0.500 |
| DATA_ONLY | total | >5 | 1 | 13.00 | 7.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 10 | 7.42 | 7.35 | 0.750 |
| HYBRID_30 | margin | 1-2 | 6 | 6.65 | 7.17 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 9 | 10.45 | 10.39 | 0.400 |
| HYBRID_30 | total | 1-2 | 7 | 9.74 | 8.86 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Game-centre accuracy — T-30m (16 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 1 | 7.31 | 9.12 | 1.56 | 9.62 | 11.08 | -2.88 | 0.223 |
| DATA_ONLY | 16 | 1 | 6.89 | 8.65 | 2.54 | 11.33 | 12.66 | -2.10 | 0.196 |
| HYBRID_30 | 16 | 1 | 7.15 | 8.86 | 1.85 | 10.07 | 11.47 | -2.64 | 0.215 |
| market at snapshot | 16 | 1 | 7.31 | 9.12 | 1.56 | 9.62 | 11.08 | -2.88 | - |
| market at close | 16 | 1 | 7.44 | 9.11 | 1.56 | 9.75 | 11.24 | -3.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | -0.420 | 0.837 | [-2.062, 1.221] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | 1.704 | 0.733 | [0.267, 3.141] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | -0.161 | 0.251 | [-0.654, 0.331] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | 0.450 | 0.237 | [-0.014, 0.913] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | 0.259 | 0.590 | [-0.897, 1.415] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -1.254 | 0.508 | [-2.250, -0.258] | 0.750 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | -0.420 | 0.837 | [-2.062, 1.221] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | 1.704 | 0.733 | [0.267, 3.141] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | -0.161 | 0.251 | [-0.654, 0.331] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | 0.450 | 0.237 | [-0.014, 0.913] | 0.312 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | -0.125 | 0.097 | [-0.315, 0.065] | 0.188 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | -0.125 | 0.141 | [-0.401, 0.151] | 0.188 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | -0.545 | 0.793 | [-2.101, 1.010] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 1.579 | 0.743 | [0.122, 3.036] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | -0.286 | 0.218 | [-0.714, 0.141] | 0.625 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | 0.325 | 0.271 | [-0.206, 0.855] | 0.375 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 4 | 0 | 12 | 0 | 1.000 | 0.438 | 2.73 |
| DATA_ONLY | total | 16 | 2 | 3 | 11 | 0 | 0.400 | 0.250 | 2.98 |
| HYBRID_30 | margin | 16 | 4 | 0 | 12 | 0 | 1.000 | 0.500 | 0.82 |
| HYBRID_30 | total | 16 | 2 | 3 | 11 | 0 | 0.400 | 0.312 | 0.89 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 3 | 10.01 | 9.50 | 1.000 |
| DATA_ONLY | margin | 1-2 | 4 | 4.52 | 4.88 | - |
| DATA_ONLY | margin | 2-3 | 2 | 12.82 | 13.00 | - |
| DATA_ONLY | margin | 3-5 | 4 | 6.85 | 7.00 | 1.000 |
| DATA_ONLY | margin | >5 | 3 | 3.03 | 5.00 | 1.000 |
| DATA_ONLY | total | <=1 | 4 | 7.81 | 7.88 | 0.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 3 | 13.68 | 12.83 | 1.000 |
| DATA_ONLY | total | 3-5 | 7 | 11.09 | 9.07 | 1.000 |
| DATA_ONLY | total | >5 | 2 | 15.67 | 10.25 | 0.000 |
| HYBRID_30 | margin | <=1 | 10 | 7.49 | 7.45 | 1.000 |
| HYBRID_30 | margin | 1-2 | 6 | 6.59 | 7.08 | 1.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 9 | 10.41 | 10.33 | 0.500 |
| HYBRID_30 | total | 1-2 | 7 | 9.64 | 8.71 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Contract pricing — latest_pregame (1243 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1243 | 0.1374 | 0.4212 | 0.419 | 0.421 | 1243 | 0.1374 | 0.1368 | 0.1385 |
| DATA_ONLY | 1243 | 0.1410 | 0.4322 | 0.429 | 0.421 | 1243 | 0.1410 | 0.1368 | 0.1385 |
| HYBRID_30 | 1243 | 0.1366 | 0.4204 | 0.420 | 0.421 | 1243 | 0.1366 | 0.1368 | 0.1385 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1243 | 16 | 0.00364 | [-0.01287, 0.01995] | 0.00364 | [-0.01287, 0.01995] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1243 | 16 | -0.00074 | [-0.00601, 0.00420] | -0.00074 | [-0.00601, 0.00420] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1243 | 16 | -0.00438 | [-0.01636, 0.00716] | -0.00438 | [-0.01636, 0.00716] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1243 | 16 | - | - | 0.00056 | [-0.00074, 0.00196] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1231 | 16 | - | - | 0.00021 | [-0.00109, 0.00161] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1243 | 16 | - | - | 0.00420 | [-0.01211, 0.02073] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1231 | 16 | - | - | 0.00389 | [-0.01252, 0.02060] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1243 | 16 | - | - | -0.00019 | [-0.00515, 0.00485] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1231 | 16 | - | - | -0.00053 | [-0.00559, 0.00446] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 406, 'TEAM_TOTAL': 437, 'TOTAL': 304}; settlement: {'SETTLED': 1243}; close: {'OK': 1231, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 186 / 0.055 / 0.022 | 185 / 0.054 / 0.032 | 187 / 0.055 / 0.021 |
| 0.10-0.20 | 199 / 0.145 / 0.080 | 194 / 0.146 / 0.082 | 196 / 0.146 / 0.102 |
| 0.20-0.30 | 152 / 0.249 / 0.263 | 135 / 0.250 / 0.244 | 146 / 0.250 / 0.212 |
| 0.30-0.40 | 123 / 0.351 / 0.358 | 127 / 0.350 / 0.354 | 123 / 0.350 / 0.366 |
| 0.40-0.50 | 122 / 0.450 / 0.459 | 122 / 0.445 / 0.475 | 130 / 0.449 / 0.454 |
| 0.50-0.60 | 128 / 0.547 / 0.562 | 108 / 0.551 / 0.481 | 125 / 0.548 / 0.552 |
| 0.60-0.70 | 74 / 0.649 / 0.662 | 95 / 0.647 / 0.611 | 81 / 0.651 / 0.704 |
| 0.70-0.80 | 70 / 0.757 / 0.814 | 75 / 0.748 / 0.813 | 62 / 0.754 / 0.806 |
| 0.80-0.90 | 65 / 0.855 / 0.938 | 70 / 0.845 / 0.900 | 66 / 0.847 / 0.924 |
| 0.90-1.00 | 124 / 0.958 / 1.000 | 132 / 0.956 / 0.992 | 127 / 0.954 / 1.000 |

## Contract pricing — T-24h (1165 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1165 | 0.1367 | 0.4206 | 0.418 | 0.416 | 1165 | 0.1367 | 0.1375 | 0.1378 |
| DATA_ONLY | 1165 | 0.1415 | 0.4337 | 0.430 | 0.416 | 1165 | 0.1415 | 0.1375 | 0.1378 |
| HYBRID_30 | 1165 | 0.1372 | 0.4222 | 0.421 | 0.416 | 1165 | 0.1372 | 0.1375 | 0.1378 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1165 | 15 | 0.00476 | [-0.01201, 0.02213] | 0.00476 | [-0.01201, 0.02213] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1165 | 15 | 0.00051 | [-0.00630, 0.00697] | 0.00051 | [-0.00630, 0.00697] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1165 | 15 | -0.00425 | [-0.01536, 0.00659] | -0.00425 | [-0.01536, 0.00659] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1165 | 15 | - | - | -0.00076 | [-0.00199, 0.00044] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1153 | 15 | - | - | 0.00034 | [-0.00124, 0.00196] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1165 | 15 | - | - | 0.00400 | [-0.01265, 0.02075] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1153 | 15 | - | - | 0.00515 | [-0.01182, 0.02241] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1165 | 15 | - | - | -0.00024 | [-0.00713, 0.00612] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1153 | 15 | - | - | 0.00086 | [-0.00639, 0.00789] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 381, 'TEAM_TOTAL': 409, 'TOTAL': 285}; settlement: {'SETTLED': 1165}; close: {'OK': 1153, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 177 / 0.054 / 0.023 | 172 / 0.055 / 0.035 | 173 / 0.055 / 0.035 |
| 0.10-0.20 | 183 / 0.143 / 0.087 | 180 / 0.144 / 0.083 | 189 / 0.147 / 0.085 |
| 0.20-0.30 | 147 / 0.250 / 0.252 | 130 / 0.250 / 0.246 | 135 / 0.252 / 0.244 |
| 0.30-0.40 | 108 / 0.349 / 0.352 | 116 / 0.350 / 0.353 | 111 / 0.349 / 0.333 |
| 0.40-0.50 | 125 / 0.454 / 0.416 | 115 / 0.443 / 0.443 | 127 / 0.448 / 0.441 |
| 0.50-0.60 | 109 / 0.548 / 0.578 | 101 / 0.550 / 0.455 | 109 / 0.551 / 0.541 |
| 0.60-0.70 | 68 / 0.644 / 0.647 | 90 / 0.649 / 0.611 | 78 / 0.649 / 0.628 |
| 0.70-0.80 | 71 / 0.755 / 0.817 | 74 / 0.751 / 0.797 | 65 / 0.752 / 0.846 |
| 0.80-0.90 | 58 / 0.855 / 0.931 | 62 / 0.846 / 0.903 | 61 / 0.849 / 0.934 |
| 0.90-1.00 | 119 / 0.958 / 1.000 | 125 / 0.956 / 0.992 | 117 / 0.956 / 1.000 |

## Contract pricing — T-6h (1243 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1243 | 0.1365 | 0.4194 | 0.419 | 0.421 | 1243 | 0.1365 | 0.1369 | 0.1385 |
| DATA_ONLY | 1243 | 0.1414 | 0.4331 | 0.429 | 0.421 | 1243 | 0.1414 | 0.1369 | 0.1385 |
| HYBRID_30 | 1243 | 0.1368 | 0.4199 | 0.417 | 0.421 | 1243 | 0.1368 | 0.1369 | 0.1385 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1243 | 16 | 0.00495 | [-0.01012, 0.02039] | 0.00495 | [-0.01012, 0.02039] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1243 | 16 | 0.00029 | [-0.00515, 0.00549] | 0.00029 | [-0.00515, 0.00549] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1243 | 16 | -0.00466 | [-0.01605, 0.00589] | -0.00466 | [-0.01605, 0.00589] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1243 | 16 | - | - | -0.00038 | [-0.00234, 0.00128] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1231 | 16 | - | - | -0.00068 | [-0.00274, 0.00112] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1243 | 16 | - | - | 0.00457 | [-0.01141, 0.02050] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1231 | 16 | - | - | 0.00433 | [-0.01211, 0.02094] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1243 | 16 | - | - | -0.00009 | [-0.00640, 0.00579] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1231 | 16 | - | - | -0.00037 | [-0.00690, 0.00544] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 406, 'TEAM_TOTAL': 437, 'TOTAL': 304}; settlement: {'SETTLED': 1243}; close: {'OK': 1231, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 187 / 0.055 / 0.021 | 185 / 0.054 / 0.027 | 195 / 0.054 / 0.021 |
| 0.10-0.20 | 192 / 0.145 / 0.089 | 195 / 0.146 / 0.092 | 194 / 0.147 / 0.103 |
| 0.20-0.30 | 157 / 0.249 / 0.242 | 138 / 0.251 / 0.246 | 152 / 0.252 / 0.237 |
| 0.30-0.40 | 120 / 0.351 / 0.383 | 122 / 0.351 / 0.369 | 116 / 0.348 / 0.371 |
| 0.40-0.50 | 124 / 0.449 / 0.435 | 123 / 0.445 / 0.447 | 138 / 0.448 / 0.442 |
| 0.50-0.60 | 121 / 0.545 / 0.545 | 109 / 0.551 / 0.495 | 113 / 0.549 / 0.575 |
| 0.60-0.70 | 84 / 0.645 / 0.667 | 98 / 0.649 / 0.622 | 78 / 0.649 / 0.667 |
| 0.70-0.80 | 67 / 0.754 / 0.821 | 74 / 0.752 / 0.797 | 66 / 0.754 / 0.848 |
| 0.80-0.90 | 71 / 0.853 / 0.944 | 69 / 0.848 / 0.913 | 66 / 0.851 / 0.924 |
| 0.90-1.00 | 120 / 0.959 / 1.000 | 130 / 0.957 / 0.992 | 125 / 0.957 / 1.000 |

## Contract pricing — T-90m (1243 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1243 | 0.1367 | 0.4198 | 0.419 | 0.421 | 1243 | 0.1367 | 0.1368 | 0.1385 |
| DATA_ONLY | 1243 | 0.1413 | 0.4327 | 0.429 | 0.421 | 1243 | 0.1413 | 0.1368 | 0.1385 |
| HYBRID_30 | 1243 | 0.1387 | 0.4247 | 0.419 | 0.421 | 1243 | 0.1387 | 0.1368 | 0.1385 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1243 | 16 | 0.00461 | [-0.01179, 0.02090] | 0.00461 | [-0.01179, 0.02090] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1243 | 16 | 0.00197 | [-0.00412, 0.00743] | 0.00197 | [-0.00412, 0.00743] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1243 | 16 | -0.00264 | [-0.01420, 0.00857] | -0.00264 | [-0.01420, 0.00857] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1243 | 16 | - | - | -0.00007 | [-0.00135, 0.00113] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1231 | 16 | - | - | -0.00048 | [-0.00179, 0.00071] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1243 | 16 | - | - | 0.00454 | [-0.01173, 0.02099] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1231 | 16 | - | - | 0.00418 | [-0.01232, 0.02095] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1243 | 16 | - | - | 0.00190 | [-0.00377, 0.00719] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1231 | 16 | - | - | 0.00152 | [-0.00416, 0.00667] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 406, 'TEAM_TOTAL': 437, 'TOTAL': 304}; settlement: {'SETTLED': 1243}; close: {'OK': 1231, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 190 / 0.056 / 0.021 | 187 / 0.055 / 0.032 | 188 / 0.054 / 0.021 |
| 0.10-0.20 | 193 / 0.145 / 0.078 | 191 / 0.146 / 0.079 | 197 / 0.146 / 0.102 |
| 0.20-0.30 | 152 / 0.248 / 0.263 | 136 / 0.249 / 0.250 | 147 / 0.251 / 0.231 |
| 0.30-0.40 | 127 / 0.350 / 0.362 | 127 / 0.350 / 0.370 | 122 / 0.350 / 0.393 |
| 0.40-0.50 | 116 / 0.449 / 0.440 | 121 / 0.444 / 0.455 | 137 / 0.450 / 0.445 |
| 0.50-0.60 | 130 / 0.546 / 0.569 | 110 / 0.551 / 0.500 | 120 / 0.551 / 0.542 |
| 0.60-0.70 | 76 / 0.648 / 0.671 | 94 / 0.647 / 0.606 | 79 / 0.653 / 0.671 |
| 0.70-0.80 | 66 / 0.756 / 0.818 | 77 / 0.749 / 0.805 | 60 / 0.753 / 0.833 |
| 0.80-0.90 | 69 / 0.852 / 0.928 | 68 / 0.846 / 0.897 | 69 / 0.848 / 0.928 |
| 0.90-1.00 | 124 / 0.958 / 1.000 | 132 / 0.956 / 0.992 | 124 / 0.957 / 1.000 |

## Contract pricing — T-30m (1243 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1243 | 0.1374 | 0.4213 | 0.419 | 0.421 | 1243 | 0.1374 | 0.1368 | 0.1385 |
| DATA_ONLY | 1243 | 0.1411 | 0.4323 | 0.429 | 0.421 | 1243 | 0.1411 | 0.1368 | 0.1385 |
| HYBRID_30 | 1243 | 0.1365 | 0.4201 | 0.420 | 0.421 | 1243 | 0.1365 | 0.1368 | 0.1385 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1243 | 16 | 0.00362 | [-0.01287, 0.01995] | 0.00362 | [-0.01287, 0.01995] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1243 | 16 | -0.00094 | [-0.00620, 0.00405] | -0.00094 | [-0.00620, 0.00405] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1243 | 16 | -0.00457 | [-0.01642, 0.00715] | -0.00457 | [-0.01642, 0.00715] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1243 | 16 | - | - | 0.00066 | [-0.00058, 0.00201] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1231 | 16 | - | - | 0.00028 | [-0.00104, 0.00167] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1243 | 16 | - | - | 0.00428 | [-0.01203, 0.02077] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1231 | 16 | - | - | 0.00394 | [-0.01252, 0.02061] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1243 | 16 | - | - | -0.00029 | [-0.00527, 0.00480] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1231 | 16 | - | - | -0.00067 | [-0.00573, 0.00445] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 406, 'TEAM_TOTAL': 437, 'TOTAL': 304}; settlement: {'SETTLED': 1243}; close: {'OK': 1231, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 186 / 0.055 / 0.022 | 185 / 0.054 / 0.032 | 187 / 0.055 / 0.021 |
| 0.10-0.20 | 198 / 0.145 / 0.081 | 194 / 0.146 / 0.082 | 195 / 0.145 / 0.097 |
| 0.20-0.30 | 152 / 0.249 / 0.263 | 134 / 0.250 / 0.246 | 147 / 0.250 / 0.218 |
| 0.30-0.40 | 124 / 0.351 / 0.355 | 128 / 0.350 / 0.352 | 123 / 0.351 / 0.366 |
| 0.40-0.50 | 120 / 0.450 / 0.458 | 122 / 0.445 / 0.475 | 130 / 0.449 / 0.454 |
| 0.50-0.60 | 129 / 0.546 / 0.558 | 108 / 0.551 / 0.481 | 125 / 0.548 / 0.552 |
| 0.60-0.70 | 75 / 0.649 / 0.667 | 95 / 0.647 / 0.611 | 81 / 0.651 / 0.704 |
| 0.70-0.80 | 70 / 0.757 / 0.814 | 75 / 0.748 / 0.813 | 62 / 0.754 / 0.806 |
| 0.80-0.90 | 65 / 0.855 / 0.938 | 70 / 0.845 / 0.900 | 66 / 0.847 / 0.924 |
| 0.90-1.00 | 124 / 0.958 / 1.000 | 132 / 0.956 / 0.992 | 127 / 0.954 / 1.000 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 15 | 4 | 2 | 1 | 8 | 0 | 0.667 [0.208, 0.939] | 0.545 | 0.545 | 0.05 |
| T-24h | DATA_ONLY | total | 15 | 5 | 2 | 3 | 5 | 0 | 0.400 [0.118, 0.769] | 0.200 | 0.100 | -0.20 |
| T-24h | HYBRID_30 (derived) | margin | 15 | 10 | 1 | 0 | 4 | 0 | 1.000 [0.207, 1.000] | 0.600 | 0.600 | 0.10 |
| T-24h | HYBRID_30 (derived) | total | 15 | 8 | 2 | 2 | 3 | 0 | 0.500 [0.150, 0.850] | 0.286 | 0.286 | -0.07 |
| T-6h | DATA_ONLY | margin | 16 | 4 | 1 | 1 | 10 | 0 | 0.500 [0.095, 0.905] | 0.500 | 0.500 | 0.04 |
| T-6h | DATA_ONLY | total | 16 | 4 | 3 | 5 | 4 | 0 | 0.375 [0.137, 0.694] | 0.250 | 0.167 | -0.12 |
| T-6h | HYBRID_30 (derived) | margin | 16 | 11 | 0 | 1 | 4 | 0 | 0.000 [0.000, 0.793] | 0.600 | 0.600 | -0.10 |
| T-6h | HYBRID_30 (derived) | total | 16 | 10 | 1 | 3 | 2 | 0 | 0.250 [0.046, 0.699] | 0.333 | 0.333 | -0.25 |
| T-90m | DATA_ONLY | margin | 16 | 4 | 2 | 0 | 10 | 0 | 1.000 [0.342, 1.000] | 0.500 | 0.500 | 0.12 |
| T-90m | DATA_ONLY | total | 16 | 4 | 2 | 3 | 7 | 0 | 0.400 [0.118, 0.769] | 0.167 | 0.167 | -0.12 |
| T-90m | HYBRID_30 (derived) | margin | 16 | 10 | 1 | 0 | 5 | 0 | 1.000 [0.207, 1.000] | 0.667 | 0.667 | 0.08 |
| T-90m | HYBRID_30 (derived) | total | 16 | 9 | 0 | 2 | 5 | 0 | 0.000 [0.000, 0.658] | 0.143 | 0.143 | -0.21 |
| T-30m | DATA_ONLY | margin | 16 | 3 | 3 | 0 | 10 | 0 | 1.000 [0.439, 1.000] | 0.538 | 0.538 | 0.15 |
| T-30m | DATA_ONLY | total | 16 | 4 | 2 | 1 | 9 | 0 | 0.667 [0.208, 0.939] | 0.167 | 0.167 | 0.17 |
| T-30m | HYBRID_30 (derived) | margin | 16 | 10 | 2 | 0 | 4 | 0 | 1.000 [0.342, 1.000] | 0.667 | 0.667 | 0.17 |
| T-30m | HYBRID_30 (derived) | total | 16 | 9 | 0 | 1 | 6 | 0 | 0.000 [0.000, 0.793] | 0.143 | 0.143 | -0.07 |
| latest_pregame | DATA_ONLY | margin | 16 | 3 | 3 | 0 | 10 | 0 | 1.000 [0.439, 1.000] | 0.538 | 0.538 | 0.15 |
| latest_pregame | DATA_ONLY | total | 16 | 4 | 2 | 1 | 9 | 0 | 0.667 [0.208, 0.939] | 0.167 | 0.167 | 0.17 |
| latest_pregame | HYBRID_30 (derived) | margin | 16 | 10 | 2 | 0 | 4 | 0 | 1.000 [0.342, 1.000] | 0.667 | 0.667 | 0.17 |
| latest_pregame | HYBRID_30 (derived) | total | 16 | 9 | 0 | 1 | 6 | 0 | 0.000 [0.000, 0.793] | 0.143 | 0.143 | -0.07 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 3 | 1 | 0 | 2 | 0 | 1.000 |
| margin | 1-2 | 4 | 0 | 0 | 4 | 0 | - |
| margin | 2-3 | 2 | 0 | 0 | 2 | 0 | - |
| margin | 3-5 | 4 | 2 | 0 | 2 | 0 | 1.000 |
| margin | >5 | 3 | 1 | 0 | 2 | 0 | 1.000 |
| total | <=1 | 4 | 0 | 2 | 2 | 0 | 0.000 |
| total | 1-2 | 0 | 0 | 0 | 0 | 0 | - |
| total | 2-3 | 3 | 1 | 0 | 2 | 0 | 1.000 |
| total | 3-5 | 7 | 1 | 0 | 6 | 0 | 1.000 |
| total | >5 | 2 | 0 | 1 | 1 | 0 | 0.000 |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

993 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_04_GB_TB | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 36 | 48.56 | 0.99 | 1.0 | 5 | 1.05 | 7.20 | EXPECTED_ACTIVE | True | 0.223 | EFFICIENCY_MISS |
| 2026_04_IND_WAS | Jacory Croskey-Merritt | receiving_yards | 1.0 | 0–11 | 35 | 47.21 | 0.99 | 1.2 | 4 | 0.86 | 8.75 | EXPECTED_ACTIVE | True | 0.213 | EFFICIENCY_MISS |
| 2026_04_DEN_SF | Kyle Juszczyk | receiving_yards | 1.0 | 0–11 | 28 | 37.77 | 0.99 | 0.5 | 2 | 2.04 | 14.00 | EXPECTED_ACTIVE | True | 0.297 | EFFICIENCY_MISS |
| 2026_04_LAC_SEA | Keaton Mitchell | receiving_yards | 1.0 | 0–11 | 24 | 32.38 | 0.99 | 1.2 | 6 | 0.81 | 4.00 | EXPECTED_ACTIVE | True | 0.342 | EFFICIENCY_MISS |
| 2026_04_LAC_SEA | Emanuel Wilson | receiving_yards | 2.8 | 0–29 | 39 | 17.54 | 0.97 | 1.2 | 4 | 2.27 | 9.75 | EXPECTED_ACTIVE | True | 0.177 | EFFICIENCY_MISS |
| 2026_04_KC_LV | Emmett Johnson | receiving_yards | 1.0 | 0–11 | 10 | 13.49 | 0.93 | 0.9 | 1 | 1.10 | 10.00 | EXPECTED_ACTIVE | True | -0.243 | EFFICIENCY_MISS |
| 2026_04_JAX_CIN | Bhayshul Tuten | receiving_yards | 1.9 | 0–20 | 18 | 12.14 | 0.93 | 1.2 | 2 | 1.61 | 9.00 | EXPECTED_ACTIVE | True | 0.307 | EFFICIENCY_MISS |
| 2026_04_ARI_NYG | Jeremiyah Love | receiving_yards | 1.0 | 0–11 | -8 | -10.79 | 0.05 | 0.9 | 1 | 1.08 | -8.00 | EXPECTED_ACTIVE | True | -0.531 | EFFICIENCY_MISS |
| 2026_04_NYJ_CHI | Braelon Allen | receiving_yards | 1.0 | 0–11 | 8 | 10.79 | 0.89 | 1.2 | 2 | 0.85 | 4.00 | EXPECTED_ACTIVE | True | -0.382 | EFFICIENCY_MISS |
| 2026_04_DAL_HOU | CeeDee Lamb | receptions | 3.1 | 0–7 | 17 | 9.44 | 0.99 | 4.9 | 21 | 0.62 | 0.81 | EXPECTED_ACTIVE | True | 0.352 | TEAM_VOLUME_MISS |
| 2026_04_PIT_CLE | Raheim Sanders | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.1 | 2 | 0.87 | 3.50 | EXPECTED_ACTIVE | True | -0.402 | EFFICIENCY_MISS |
| 2026_04_TEN_BAL | Carnell Tate | receiving_yards | 19.1 | 0–64 | 145 | 7.06 | 0.99 | 1.9 | 12 | 10.12 | 12.08 | EXPECTED_ACTIVE | True | 0.455 | OPPORTUNITY_MISS |
| 2026_04_MIA_MIN | Ollie Gordon II | rushing_yards | 12.5 | 0–50 | 100 | 7.04 | 0.99 | 4.1 | 9 | 3.02 | 11.11 | EXPECTED_ACTIVE | True | 0.394 | EFFICIENCY_MISS |
| 2026_04_GB_TB | MarShawn Lloyd | receptions | 0.7 | 0–5 | 5 | 6.75 | 0.95 | 1.0 | 5 | 0.73 | 1.00 | EXPECTED_ACTIVE | True | 0.199 | OPPORTUNITY_MISS |
| 2026_04_LAC_SEA | Keaton Mitchell | receptions | 0.9 | 0–5 | 5 | 6.75 | 0.95 | 1.2 | 6 | 0.70 | 0.83 | EXPECTED_ACTIVE | True | 0.281 | OPPORTUNITY_MISS |
| 2026_04_LA_PHI | Kyren Williams | receiving_yards | 10.3 | 0–45 | 67 | 6.46 | 0.98 | 1.7 | 13 | 6.16 | 5.15 | EXPECTED_ACTIVE | True | 0.236 | TEAM_VOLUME_MISS |
| 2026_04_DEN_SF | RJ Harvey | receptions | 1.4 | 0–5 | 10 | 6.07 | 0.99 | 1.9 | 10 | 0.74 | 1.00 | EXPECTED_ACTIVE | True | 0.444 | TEAM_VOLUME_MISS |
| 2026_04_JAX_CIN | Chase Brown | receptions | 1.9 | 0–5 | 11 | 6.07 | 0.99 | 2.4 | 11 | 0.80 | 1.00 | EXPECTED_ACTIVE | True | 0.279 | TEAM_VOLUME_MISS |
| 2026_04_LA_PHI | Kyren Williams | receptions | 1.2 | 0–5 | 10 | 6.07 | 0.99 | 1.7 | 13 | 0.71 | 0.77 | EXPECTED_ACTIVE | True | 0.315 | TEAM_VOLUME_MISS |
| 2026_04_DET_CAR | Tetairoa McMillan | receiving_yards | 42.6 | 3–99 | 192 | 5.43 | 0.99 | 4.1 | 16 | 10.49 | 12.00 | EXPECTED_ACTIVE | True | 0.303 | OPPORTUNITY_MISS |
| 2026_04_GB_TB | Jalon Daniels | carries | 2.0 | 0–17 | 8 | 5.40 | 0.83 | 2.0 | 8 | - | - | EXPECTED_ACTIVE | True | 0.696 | TEAM_VOLUME_MISS |
| 2026_04_TEN_BAL | Carnell Tate | receptions | 1.1 | 0–5 | 9 | 5.40 | 0.99 | 1.9 | 12 | 0.60 | 0.75 | EXPECTED_ACTIVE | True | 0.583 | OPPORTUNITY_MISS |
| 2026_04_DET_CAR | Tetairoa McMillan | receptions | 2.4 | 0–6 | 14 | 5.40 | 0.99 | 4.1 | 16 | 0.58 | 0.88 | EXPECTED_ACTIVE | True | 0.435 | OPPORTUNITY_MISS |
| 2026_04_MIA_MIN | T.J. Hockenson | receptions | 1.6 | 0–5 | 13 | 5.40 | 0.99 | 2.2 | 13 | 0.74 | 1.00 | EXPECTED_ACTIVE | True | 0.439 | TEAM_VOLUME_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | receiving_yards | 8.0 | 0–35 | 43 | 5.27 | 0.96 | 1.7 | 7 | 4.83 | 6.14 | EXPECTED_ACTIVE | True | 0.213 | OPPORTUNITY_MISS |
| 2026_04_MIA_MIN | T.J. Hockenson | receiving_yards | 20.9 | 0–71 | 119 | 5.07 | 0.99 | 2.2 | 13 | 9.58 | 9.15 | EXPECTED_ACTIVE | True | 0.420 | TEAM_VOLUME_MISS |
| 2026_04_KC_LV | Michael Mayer | receptions | 1.5 | 0–5 | 8 | 4.72 | 0.99 | 2.1 | 10 | 0.70 | 0.80 | EXPECTED_ACTIVE | True | 0.347 | TEAM_VOLUME_MISS |
| 2026_04_KC_LV | Tyquan Thornton | receiving_yards | 23.7 | 0–66 | 111 | 4.53 | 0.99 | 2.0 | 8 | 11.59 | 13.88 | EXPECTED_ACTIVE | True | 0.058 | OPPORTUNITY_MISS |
| 2026_04_NYJ_CHI | Kyle Monangai | rushing_yards | 36.3 | 3–93 | 146 | 4.39 | 0.99 | 6.7 | 30 | 5.40 | 4.87 | EXPECTED_ACTIVE | True | 0.112 | TEAM_VOLUME_MISS |
| 2026_04_DEN_SF | RJ Harvey | receiving_yards | 13.9 | 0–47 | 68 | 4.33 | 0.98 | 1.9 | 10 | 7.42 | 6.80 | EXPECTED_ACTIVE | True | 0.327 | TEAM_VOLUME_MISS |
| 2026_04_DAL_HOU | CeeDee Lamb | receiving_yards | 49.6 | 4–115 | 189 | 4.32 | 0.99 | 4.9 | 21 | 10.04 | 9.00 | EXPECTED_ACTIVE | True | 0.300 | TEAM_VOLUME_MISS |
| 2026_04_KC_LV | Kenneth Walker III | rushing_yards | 44.6 | 4–114 | 177 | 4.30 | 0.99 | 7.9 | 22 | 5.65 | 8.05 | EXPECTED_ACTIVE | True | 0.417 | OPPORTUNITY_MISS |
| 2026_04_DET_CAR | Isaac TeSlaa | receiving_yards | 21.8 | 0–61 | 95 | 4.10 | 0.99 | 2.0 | 8 | 10.82 | 11.88 | EXPECTED_ACTIVE | True | 0.034 | TEAM_VOLUME_MISS |
| 2026_04_ARI_NYG | Isaiah Likely | receptions | 1.2 | 0–5 | 7 | 4.05 | 0.98 | 1.7 | 12 | 0.71 | 0.58 | EXPECTED_ACTIVE | True | 0.539 | OPPORTUNITY_MISS |
| 2026_04_DET_CAR | Sam LaPorta | receptions | 1.9 | 0–5 | 8 | 4.05 | 0.99 | 2.4 | 13 | 0.78 | 0.62 | EXPECTED_ACTIVE | True | 0.361 | TEAM_VOLUME_MISS |
| 2026_04_JAX_CIN | Tee Higgins | receptions | 2.6 | 0–6 | 11 | 4.05 | 0.99 | 4.2 | 16 | 0.63 | 0.69 | EXPECTED_ACTIVE | True | 0.207 | TEAM_VOLUME_MISS |
| 2026_04_JAX_CIN | Brenton Strange | receptions | 1.7 | 0–5 | 7 | 4.05 | 0.99 | 2.3 | 8 | 0.73 | 0.88 | EXPECTED_ACTIVE | True | 0.351 | OPPORTUNITY_MISS |
| 2026_04_JAX_CIN | Dohnte Meyers | receptions | 1.1 | 0–5 | 7 | 4.05 | 0.98 | 1.8 | 9 | 0.63 | 0.78 | EXPECTED_ACTIVE | True | 0.275 | TEAM_VOLUME_MISS |
| 2026_04_LAC_SEA | Emanuel Wilson | receptions | 0.9 | 0–5 | 3 | 4.05 | 0.85 | 1.2 | 4 | 0.74 | 0.75 | EXPECTED_ACTIVE | True | 0.139 | OPPORTUNITY_MISS |
| 2026_04_MIA_MIN | Malik Washington | rushing_yards | 1.0 | 0–4 | 3 | 4.05 | 0.88 | 1.9 | 2 | 0.53 | 1.50 | EXPECTED_ACTIVE | True | -0.281 | EFFICIENCY_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 179, 'TEAM_VOLUME_MISS': 96, 'OPPORTUNITY_MISS': 337, 'UNEXPLAINED_VARIANCE': 33, 'NO_LARGE_MISS': 324, 'AVAILABILITY_MISS': 9, 'INSUFFICIENT_DATA': 15}.
Missing usage (no snap table or stats row): 24.

## Decision funnel

No funnel accounting is available for this period.

## Player-autopsy coverage — 2026 week 4

Expected games 16 · eligible 16 · diagnosed 15 · excluded 1 · canonical projection units 993 (969 with a box-score value) · eligible units 1061, eligible but undiagnosed 68

| game | included | diagnosed units | raw records | eligible units | undiagnosed | rule | exclusion reason |
|---|---|---|---|---|---|---|---|
| 2026_04_ARI_NYG | yes | 62 | 62 | 62 | 0 | autopsy-1.1.0 |  |
| 2026_04_ATL_NO | NO | 0 | 0 | 68 | 68 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_DAL_HOU | yes | 70 | 70 | 70 | 0 | autopsy-1.1.0 |  |
| 2026_04_DEN_SF | yes | 68 | 68 | 68 | 0 | autopsy-1.1.0 |  |
| 2026_04_DET_CAR | yes | 62 | 62 | 62 | 0 | autopsy-1.1.0 |  |
| 2026_04_GB_TB | yes | 65 | 65 | 65 | 0 | autopsy-1.1.0 |  |
| 2026_04_IND_WAS | yes | 70 | 70 | 70 | 0 | autopsy-1.1.0 |  |
| 2026_04_JAX_CIN | yes | 73 | 73 | 73 | 0 | autopsy-1.1.0 |  |
| 2026_04_KC_LV | yes | 67 | 67 | 67 | 0 | autopsy-1.1.0 |  |
| 2026_04_LAC_SEA | yes | 72 | 72 | 72 | 0 | autopsy-1.1.0 |  |
| 2026_04_LA_PHI | yes | 62 | 62 | 62 | 0 | autopsy-1.1.0 |  |
| 2026_04_MIA_MIN | yes | 65 | 65 | 65 | 0 | autopsy-1.1.0 |  |
| 2026_04_NE_BUF | yes | 69 | 69 | 69 | 0 | autopsy-1.1.0 |  |
| 2026_04_NYJ_CHI | yes | 60 | 60 | 60 | 0 | autopsy-1.1.0 |  |
| 2026_04_PIT_CLE | yes | 63 | 63 | 63 | 0 | autopsy-1.1.0 |  |
| 2026_04_TEN_BAL | yes | 65 | 65 | 65 | 0 | autopsy-1.1.0 |  |

