# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 31 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 1213 | 31 | 2 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 16 | 16 | 2 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 12 | 12 | 2 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 20 | 20 | 2 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 30 | 30 | 2 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 31 | 31 | 2 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

Raw rows are repeated snapshots of the same games and are never a sample size. The primary unit is `latest_pregame` (one row per game); the canonical horizons are one row per game per horizon.

## Game centres, per game (latest pregame snapshot)

| game | kickoff | T-min | arm | margin | total | actual margin | actual total | mkt@snap margin/total | close margin/total |
|---|---|---|---|---|---|---|---|---|---|
| 2026_01_SF_LA | 2026-09-11T00:35 | 80 | CURRENT | 4.50 | 47.50 | -20 | 34 | 4.5/47.5 (kalshi_implied) | 4.5/47.5 (OK) |
|  |  |  | DATA_ONLY | 4.26 | 51.49 |  |  |  |  |
|  |  |  | HYBRID_30 | 4.43 | 48.70 |  |  |  |  |
| 2026_01_ATL_PIT | 2026-09-13T17:00 | 31 | CURRENT | 6.50 | 40.00 | 7 | 33 | 6.5/40.0 (kalshi_implied) | 6.5/40.0 (OK) |
|  |  |  | DATA_ONLY | 3.49 | 45.06 |  |  |  |  |
|  |  |  | HYBRID_30 | 5.60 | 41.52 |  |  |  |  |
| 2026_01_BAL_IND | 2026-09-13T17:00 | 31 | CURRENT | -2.50 | 47.50 | -18 | 64 | -2.5/47.5 (kalshi_implied) | -2.5/47.5 (OK) |
|  |  |  | DATA_ONLY | 0.63 | 47.31 |  |  |  |  |
|  |  |  | HYBRID_30 | -1.56 | 47.44 |  |  |  |  |
| 2026_01_BUF_HOU | 2026-09-13T17:00 | 31 | CURRENT | -0.50 | 44.50 | -5 | 67 | -0.5/44.5 (kalshi_implied) | 0.5/44.0 (OK) |
|  |  |  | DATA_ONLY | 1.78 | 45.88 |  |  |  |  |
|  |  |  | HYBRID_30 | 0.18 | 44.91 |  |  |  |  |
| 2026_01_CHI_CAR | 2026-09-13T17:00 | 31 | CURRENT | -2.50 | 46.50 | -22 | 96 | -2.5/46.5 (kalshi_implied) | -2.5/46.5 (OK) |
|  |  |  | DATA_ONLY | -2.78 | 46.56 |  |  |  |  |
|  |  |  | HYBRID_30 | -2.58 | 46.52 |  |  |  |  |
| 2026_01_CLE_JAX | 2026-09-13T17:00 | 31 | CURRENT | 9.00 | 40.50 | 24 | 44 | 9.0/40.5 (kalshi_implied) | 10.0/40.5 (OK) |
|  |  |  | DATA_ONLY | 9.61 | 40.60 |  |  |  |  |
|  |  |  | HYBRID_30 | 9.18 | 40.53 |  |  |  |  |
| 2026_01_NO_DET | 2026-09-13T17:00 | 31 | CURRENT | 7.00 | 49.50 | 1 | 61 | 7.0/49.5 (kalshi_implied) | 7.0/49.5 (OK) |
|  |  |  | DATA_ONLY | 5.54 | 48.34 |  |  |  |  |
|  |  |  | HYBRID_30 | 6.56 | 49.15 |  |  |  |  |
| 2026_01_NYJ_TEN | 2026-09-13T17:00 | 31 | CURRENT | 0.50 | 38.50 | -13 | 33 | 0.5/38.5 (kalshi_implied) | 0.5/38.5 (OK) |
|  |  |  | DATA_ONLY | 3.31 | 43.07 |  |  |  |  |
|  |  |  | HYBRID_30 | 1.34 | 39.87 |  |  |  |  |
| 2026_01_TB_CIN | 2026-09-13T17:00 | 31 | CURRENT | 4.00 | 51.00 | 6 | 60 | 4.0/51.0 (kalshi_implied) | 4.0/51.0 (OK) |
|  |  |  | DATA_ONLY | 2.50 | 47.94 |  |  |  |  |
|  |  |  | HYBRID_30 | 3.55 | 50.08 |  |  |  |  |
| 2026_01_ARI_LAC | 2026-09-13T20:25 | 83 | CURRENT | 9.50 | 46.50 | -12 | 40 | 9.5/46.5 (kalshi_implied) | 9.5/46.5 (OK) |
|  |  |  | DATA_ONLY | 7.10 | 49.70 |  |  |  |  |
|  |  |  | HYBRID_30 | 8.78 | 47.46 |  |  |  |  |
| 2026_01_GB_MIN | 2026-09-13T20:25 | 83 | CURRENT | 1.50 | 45.50 | 17 | 61 | 1.5/45.5 (kalshi_implied) | 1.5/45.0 (OK) |
|  |  |  | DATA_ONLY | 2.43 | 45.08 |  |  |  |  |
|  |  |  | HYBRID_30 | 1.78 | 45.37 |  |  |  |  |
| 2026_01_MIA_LV | 2026-09-13T20:25 | 83 | CURRENT | 2.50 | 40.50 | 14 | 40 | 2.5/40.5 (kalshi_implied) | 2.5/39.5 (OK) |
|  |  |  | DATA_ONLY | -2.33 | 45.18 |  |  |  |  |
|  |  |  | HYBRID_30 | 1.05 | 41.90 |  |  |  |  |
| 2026_01_WAS_PHI | 2026-09-13T20:25 | 83 | CURRENT | 6.50 | 43.00 | 2 | 46 | 6.5/43.0 (kalshi_implied) | 6.5/43.0 (OK) |
|  |  |  | DATA_ONLY | 6.39 | 44.64 |  |  |  |  |
|  |  |  | HYBRID_30 | 6.47 | 43.49 |  |  |  |  |
| 2026_01_DAL_NYG | 2026-09-14T00:20 | 53 | CURRENT | -2.50 | 47.00 | 8 | 48 | -2.5/47.0 (kalshi_implied) | -3.5/47.5 (OK) |
|  |  |  | DATA_ONLY | 1.43 | 49.17 |  |  |  |  |
|  |  |  | HYBRID_30 | -1.32 | 47.65 |  |  |  |  |
| 2026_01_DEN_KC | 2026-09-15T00:15 | 50 | CURRENT | 1.50 | 42.00 | 21 | 41 | 1.5/42.0 (kalshi_implied) | 1.5/42.0 (OK) |
|  |  |  | DATA_ONLY | -2.87 | 41.12 |  |  |  |  |
|  |  |  | HYBRID_30 | 0.19 | 41.73 |  |  |  |  |
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

## Game-centre accuracy — latest_pregame (31 games, 2 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 31 | 2 | 12.03 | 14.10 | 3.35 | 10.81 | 15.02 | -1.00 | 0.220 |
| DATA_ONLY | 31 | 2 | 12.74 | 14.87 | 2.36 | 11.94 | 15.96 | 0.02 | 0.254 |
| HYBRID_30 | 31 | 2 | 12.25 | 14.27 | 3.06 | 11.10 | 15.26 | -0.69 | 0.232 |
| market at snapshot | 31 | 2 | 12.03 | 14.10 | 3.35 | 10.81 | 15.02 | -1.00 | - |
| market at close | 31 | 2 | 12.08 | 14.09 | 3.37 | 10.87 | 15.11 | -0.97 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 31 | margin | 0.711 | 0.522 | [-0.313, 1.735] | 0.484 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 31 | total | 1.133 | 0.441 | [0.269, 1.997] | 0.323 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 31 | margin | 0.213 | 0.157 | [-0.094, 0.521] | 0.484 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 31 | total | 0.289 | 0.139 | [0.016, 0.563] | 0.387 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 31 | margin | -0.498 | 0.366 | [-1.215, 0.219] | 0.516 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 31 | total | -0.844 | 0.306 | [-1.444, -0.243] | 0.677 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 31 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 31 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 31 | margin | 0.711 | 0.522 | [-0.313, 1.735] | 0.484 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 31 | total | 1.133 | 0.441 | [0.269, 1.997] | 0.323 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 31 | margin | 0.213 | 0.157 | [-0.094, 0.521] | 0.484 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 31 | total | 0.289 | 0.139 | [0.016, 0.563] | 0.387 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 31 | margin | -0.048 | 0.067 | [-0.180, 0.083] | 0.097 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 31 | total | -0.065 | 0.050 | [-0.163, 0.034] | 0.161 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 31 | margin | 0.663 | 0.526 | [-0.368, 1.693] | 0.452 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 31 | total | 1.069 | 0.434 | [0.217, 1.920] | 0.355 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 31 | margin | 0.165 | 0.170 | [-0.168, 0.497] | 0.516 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 31 | total | 0.225 | 0.136 | [-0.042, 0.492] | 0.419 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 31 | 4 | 2 | 25 | 0 | 0.667 | 0.484 | 2.43 |
| DATA_ONLY | total | 31 | 5 | 3 | 23 | 0 | 0.625 | 0.323 | 2.17 |
| HYBRID_30 | margin | 31 | 4 | 2 | 25 | 0 | 0.667 | 0.484 | 0.73 |
| HYBRID_30 | total | 31 | 5 | 3 | 23 | 0 | 0.625 | 0.387 | 0.65 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 7 | 13.28 | 13.50 | 0.500 |
| DATA_ONLY | margin | 1-2 | 6 | 5.50 | 5.00 | 1.000 |
| DATA_ONLY | margin | 2-3 | 7 | 14.28 | 14.57 | 1.000 |
| DATA_ONLY | margin | 3-5 | 9 | 12.80 | 11.61 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 9 | 14.47 | 14.39 | 1.000 |
| DATA_ONLY | total | 1-2 | 8 | 11.14 | 11.69 | 0.000 |
| DATA_ONLY | total | 2-3 | 4 | 5.41 | 4.62 | 1.000 |
| DATA_ONLY | total | 3-5 | 8 | 11.76 | 8.62 | 0.500 |
| DATA_ONLY | total | >5 | 2 | 17.55 | 12.25 | - |
| HYBRID_30 | margin | <=1 | 22 | 11.10 | 11.02 | 0.800 |
| HYBRID_30 | margin | 1-2 | 9 | 15.05 | 14.50 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 23 | 11.19 | 11.17 | 0.667 |
| HYBRID_30 | total | 1-2 | 8 | 10.83 | 9.75 | 0.500 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 31}; DATA_ONLY quality states: {'OK': 31}; close centre status: {'OK': 31}.

## Game-centre accuracy — T-24h (16 games, 2 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 2 | 12.62 | 14.65 | 3.19 | 9.97 | 13.16 | 5.78 | 0.235 |
| DATA_ONLY | 16 | 2 | 13.54 | 15.89 | 1.57 | 9.94 | 13.60 | 6.27 | 0.269 |
| HYBRID_30 | 16 | 2 | 12.90 | 14.96 | 2.70 | 9.89 | 13.24 | 5.93 | 0.245 |
| market at snapshot | 16 | 2 | 12.62 | 14.65 | 3.19 | 9.97 | 13.16 | 5.78 | - |
| market at close | 16 | 2 | 12.78 | 14.75 | 3.34 | 9.62 | 13.05 | 5.50 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | 0.911 | 0.806 | [-0.669, 2.492] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | -0.027 | 0.626 | [-1.254, 1.199] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | 0.273 | 0.242 | [-0.201, 0.748] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | -0.079 | 0.200 | [-0.471, 0.313] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | -0.638 | 0.565 | [-1.744, 0.469] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -0.051 | 0.437 | [-0.908, 0.805] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | 0.911 | 0.806 | [-0.669, 2.492] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | -0.027 | 0.626 | [-1.254, 1.199] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | 0.273 | 0.242 | [-0.201, 0.748] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | -0.079 | 0.200 | [-0.471, 0.313] | 0.562 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | -0.156 | 0.099 | [-0.351, 0.038] | 0.250 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | 0.344 | 0.208 | [-0.063, 0.751] | 0.062 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | 0.755 | 0.845 | [-0.901, 2.411] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 0.316 | 0.532 | [-0.726, 1.359] | 0.375 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | 0.117 | 0.291 | [-0.453, 0.687] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | 0.265 | 0.181 | [-0.089, 0.619] | 0.250 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 1 | 5 | 10 | 0 | 0.167 | 0.438 | 2.70 |
| DATA_ONLY | total | 16 | 8 | 1 | 7 | 0 | 0.889 | 0.562 | 2.30 |
| HYBRID_30 | margin | 16 | 1 | 5 | 10 | 0 | 0.167 | 0.438 | 0.81 |
| HYBRID_30 | total | 16 | 8 | 1 | 7 | 0 | 0.889 | 0.562 | 0.69 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 4 | 8.83 | 9.12 | 0.000 |
| DATA_ONLY | margin | 1-2 | 2 | 8.19 | 7.00 | 1.000 |
| DATA_ONLY | margin | 2-3 | 3 | 13.60 | 14.33 | - |
| DATA_ONLY | margin | 3-5 | 5 | 14.03 | 13.20 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.25 | 0.000 |
| DATA_ONLY | total | <=1 | 3 | 8.63 | 9.00 | 1.000 |
| DATA_ONLY | total | 1-2 | 3 | 9.13 | 8.67 | 0.000 |
| DATA_ONLY | total | 2-3 | 6 | 10.57 | 10.92 | 1.000 |
| DATA_ONLY | total | 3-5 | 4 | 10.59 | 10.25 | 1.000 |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 10 | 10.48 | 10.60 | 0.200 |
| HYBRID_30 | margin | 1-2 | 6 | 16.93 | 16.00 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 13 | 9.38 | 9.58 | 0.889 |
| HYBRID_30 | total | 1-2 | 3 | 12.08 | 11.67 | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Game-centre accuracy — T-6h (12 games, 2 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 12 | 2 | 12.96 | 14.79 | 2.54 | 6.96 | 9.07 | -0.62 | 0.246 |
| DATA_ONLY | 12 | 2 | 13.28 | 14.70 | 0.47 | 7.65 | 10.07 | 0.35 | 0.255 |
| HYBRID_30 | 12 | 2 | 13.06 | 14.67 | 1.92 | 6.98 | 9.30 | -0.33 | 0.249 |
| market at snapshot | 12 | 2 | 12.96 | 14.79 | 2.54 | 6.96 | 9.07 | -0.62 | - |
| market at close | 12 | 2 | 13.17 | 14.83 | 2.42 | 7.12 | 9.26 | -0.88 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 12 | margin | 0.324 | 1.080 | [-1.794, 2.441] | 0.583 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 12 | total | 0.694 | 0.631 | [-0.543, 1.931] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 12 | margin | 0.097 | 0.324 | [-0.538, 0.732] | 0.583 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 12 | total | 0.019 | 0.179 | [-0.331, 0.370] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 12 | margin | -0.227 | 0.756 | [-1.709, 1.256] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 12 | total | -0.675 | 0.506 | [-1.667, 0.318] | 0.750 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 12 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 12 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 12 | margin | 0.324 | 1.080 | [-1.794, 2.441] | 0.583 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 12 | total | 0.694 | 0.631 | [-0.543, 1.931] | 0.250 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 12 | margin | 0.097 | 0.324 | [-0.538, 0.732] | 0.583 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 12 | total | 0.019 | 0.179 | [-0.331, 0.370] | 0.417 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 12 | margin | -0.208 | 0.179 | [-0.559, 0.142] | 0.250 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 12 | total | -0.167 | 0.225 | [-0.607, 0.274] | 0.333 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 12 | margin | 0.116 | 1.054 | [-1.950, 2.181] | 0.667 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 12 | total | 0.527 | 0.713 | [-0.871, 1.926] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 12 | margin | -0.111 | 0.332 | [-0.763, 0.540] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 12 | total | -0.147 | 0.290 | [-0.716, 0.421] | 0.583 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 12 | 4 | 1 | 7 | 0 | 0.800 | 0.583 | 3.11 |
| DATA_ONLY | total | 12 | 4 | 3 | 5 | 0 | 0.571 | 0.250 | 2.04 |
| HYBRID_30 | margin | 12 | 4 | 1 | 7 | 0 | 0.800 | 0.583 | 0.93 |
| HYBRID_30 | total | 12 | 4 | 3 | 5 | 0 | 0.571 | 0.417 | 0.61 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 19.41 | 20.00 | - |
| DATA_ONLY | margin | 1-2 | 2 | 3.30 | 3.25 | 1.000 |
| DATA_ONLY | margin | 2-3 | 2 | 18.05 | 20.75 | 1.000 |
| DATA_ONLY | margin | 3-5 | 4 | 10.85 | 11.12 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 17.23 | 11.50 | 1.000 |
| DATA_ONLY | total | <=1 | 4 | 6.77 | 6.38 | 0.667 |
| DATA_ONLY | total | 1-2 | 4 | 8.02 | 8.12 | 0.500 |
| DATA_ONLY | total | 2-3 | 1 | 9.70 | 7.50 | 0.000 |
| DATA_ONLY | total | 3-5 | 2 | 8.88 | 8.50 | - |
| DATA_ONLY | total | >5 | 1 | 5.18 | 1.00 | 1.000 |
| HYBRID_30 | margin | <=1 | 6 | 14.34 | 14.67 | 1.000 |
| HYBRID_30 | margin | 1-2 | 6 | 11.77 | 11.25 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 9 | 7.31 | 7.28 | 0.500 |
| HYBRID_30 | total | 1-2 | 3 | 5.97 | 6.00 | 1.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 12}; DATA_ONLY quality states: {'OK': 12}; close centre status: {'OK': 12}.

## Game-centre accuracy — T-90m (20 games, 2 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 20 | 2 | 11.93 | 13.92 | 3.58 | 9.22 | 12.72 | 2.23 | 0.250 |
| DATA_ONLY | 20 | 2 | 12.26 | 14.48 | 2.19 | 9.88 | 13.33 | 2.94 | 0.268 |
| HYBRID_30 | 20 | 2 | 12.02 | 14.01 | 3.16 | 9.34 | 12.85 | 2.44 | 0.254 |
| market at snapshot | 20 | 2 | 11.93 | 13.92 | 3.58 | 9.22 | 12.72 | 2.23 | - |
| market at close | 20 | 2 | 11.95 | 13.93 | 3.55 | 9.18 | 12.56 | 2.12 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 20 | margin | 0.331 | 0.751 | [-1.142, 1.803] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 20 | total | 0.655 | 0.550 | [-0.422, 1.732] | 0.350 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 20 | margin | 0.099 | 0.225 | [-0.343, 0.541] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 20 | total | 0.118 | 0.175 | [-0.225, 0.462] | 0.450 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 20 | margin | -0.231 | 0.526 | [-1.262, 0.800] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 20 | total | -0.537 | 0.384 | [-1.290, 0.216] | 0.650 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 20 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 20 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 20 | margin | 0.331 | 0.751 | [-1.142, 1.803] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 20 | total | 0.655 | 0.550 | [-0.422, 1.732] | 0.350 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 20 | margin | 0.099 | 0.225 | [-0.343, 0.541] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 20 | total | 0.118 | 0.175 | [-0.225, 0.462] | 0.450 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 20 | margin | -0.025 | 0.068 | [-0.158, 0.108] | 0.100 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 20 | total | 0.050 | 0.088 | [-0.123, 0.223] | 0.150 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 20 | margin | 0.306 | 0.755 | [-1.175, 1.786] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 20 | total | 0.705 | 0.533 | [-0.340, 1.751] | 0.350 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 20 | margin | 0.074 | 0.236 | [-0.388, 0.537] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 20 | total | 0.168 | 0.172 | [-0.168, 0.505] | 0.400 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 20 | 3 | 2 | 15 | 0 | 0.600 | 0.500 | 2.78 |
| DATA_ONLY | total | 20 | 5 | 2 | 13 | 0 | 0.714 | 0.350 | 2.16 |
| HYBRID_30 | margin | 20 | 3 | 2 | 15 | 0 | 0.600 | 0.500 | 0.83 |
| HYBRID_30 | total | 20 | 5 | 2 | 13 | 0 | 0.714 | 0.450 | 0.65 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 4 | 5.99 | 6.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 3 | 7.05 | 6.50 | - |
| DATA_ONLY | margin | 2-3 | 5 | 15.38 | 16.80 | 1.000 |
| DATA_ONLY | margin | 3-5 | 6 | 11.53 | 11.50 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 5 | 12.11 | 12.00 | 1.000 |
| DATA_ONLY | total | 1-2 | 6 | 4.18 | 4.92 | 0.000 |
| DATA_ONLY | total | 2-3 | 4 | 12.98 | 12.25 | 1.000 |
| DATA_ONLY | total | 3-5 | 4 | 9.26 | 7.12 | 0.000 |
| DATA_ONLY | total | >5 | 1 | 23.04 | 17.50 | - |
| HYBRID_30 | margin | <=1 | 12 | 10.49 | 10.62 | 0.750 |
| HYBRID_30 | margin | 1-2 | 8 | 14.33 | 13.88 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 16 | 9.02 | 9.06 | 0.833 |
| HYBRID_30 | total | 1-2 | 4 | 10.65 | 9.88 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 20}; DATA_ONLY quality states: {'OK': 20}; close centre status: {'OK': 20}.

## Game-centre accuracy — T-30m (30 games, 2 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 30 | 2 | 12.28 | 14.31 | 3.62 | 10.58 | 14.93 | -0.45 | 0.225 |
| DATA_ONLY | 30 | 2 | 12.96 | 15.08 | 2.65 | 11.57 | 15.67 | 0.79 | 0.257 |
| HYBRID_30 | 30 | 2 | 12.49 | 14.48 | 3.33 | 10.83 | 15.11 | -0.08 | 0.237 |
| market at snapshot | 30 | 2 | 12.28 | 14.31 | 3.62 | 10.58 | 14.93 | -0.45 | - |
| market at close | 30 | 2 | 12.33 | 14.30 | 3.63 | 10.65 | 15.02 | -0.42 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 30 | margin | 0.676 | 0.539 | [-0.380, 1.733] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 30 | total | 0.986 | 0.430 | [0.144, 1.829] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 30 | margin | 0.203 | 0.162 | [-0.114, 0.520] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 30 | total | 0.244 | 0.136 | [-0.023, 0.511] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 30 | margin | -0.473 | 0.377 | [-1.213, 0.266] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 30 | total | -0.743 | 0.299 | [-1.329, -0.156] | 0.667 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 30 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 30 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 30 | margin | 0.676 | 0.539 | [-0.380, 1.733] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 30 | total | 0.986 | 0.430 | [0.144, 1.829] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 30 | margin | 0.203 | 0.162 | [-0.114, 0.520] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 30 | total | 0.244 | 0.136 | [-0.023, 0.511] | 0.400 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 30 | margin | -0.050 | 0.069 | [-0.186, 0.086] | 0.100 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 30 | total | -0.067 | 0.052 | [-0.169, 0.036] | 0.167 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 30 | margin | 0.626 | 0.542 | [-0.437, 1.689] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 30 | total | 0.920 | 0.422 | [0.093, 1.747] | 0.367 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 30 | margin | 0.153 | 0.175 | [-0.190, 0.496] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 30 | total | 0.177 | 0.132 | [-0.082, 0.436] | 0.433 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 30 | 4 | 2 | 24 | 0 | 0.667 | 0.500 | 2.45 |
| DATA_ONLY | total | 30 | 5 | 3 | 22 | 0 | 0.625 | 0.333 | 2.05 |
| HYBRID_30 | margin | 30 | 4 | 2 | 24 | 0 | 0.667 | 0.500 | 0.74 |
| HYBRID_30 | total | 30 | 5 | 3 | 22 | 0 | 0.625 | 0.400 | 0.62 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 7 | 13.28 | 13.50 | 0.500 |
| DATA_ONLY | margin | 1-2 | 5 | 5.35 | 5.10 | 1.000 |
| DATA_ONLY | margin | 2-3 | 7 | 14.28 | 14.57 | 1.000 |
| DATA_ONLY | margin | 3-5 | 9 | 12.80 | 11.61 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 9 | 14.47 | 14.39 | 1.000 |
| DATA_ONLY | total | 1-2 | 8 | 11.14 | 11.69 | 0.000 |
| DATA_ONLY | total | 2-3 | 4 | 5.41 | 4.62 | 1.000 |
| DATA_ONLY | total | 3-5 | 8 | 11.76 | 8.62 | 0.500 |
| DATA_ONLY | total | >5 | 1 | 12.06 | 7.00 | - |
| HYBRID_30 | margin | <=1 | 21 | 11.39 | 11.33 | 0.800 |
| HYBRID_30 | margin | 1-2 | 9 | 15.05 | 14.50 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 23 | 11.19 | 11.17 | 0.667 |
| HYBRID_30 | total | 1-2 | 7 | 9.64 | 8.64 | 0.500 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 30}; DATA_ONLY quality states: {'OK': 30}; close centre status: {'OK': 30}.

## Contract pricing — latest_pregame (2414 contracts, 31 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2414 | 0.1745 | 0.5209 | 0.416 | 0.425 | 2414 | 0.1745 | 0.1741 | 0.1753 |
| DATA_ONLY | 2414 | 0.1890 | 0.5605 | 0.424 | 0.425 | 2414 | 0.1890 | 0.1741 | 0.1753 |
| HYBRID_30 | 2414 | 0.1777 | 0.5297 | 0.415 | 0.425 | 2414 | 0.1777 | 0.1741 | 0.1753 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2414 | 31 | 0.01457 | [0.00290, 0.02772] | 0.01457 | [0.00290, 0.02772] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2414 | 31 | 0.00328 | [-0.00018, 0.00732] | 0.00328 | [-0.00018, 0.00732] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2414 | 31 | -0.01129 | [-0.02135, -0.00241] | -0.01129 | [-0.02135, -0.00241] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2414 | 31 | - | - | 0.00036 | [-0.00072, 0.00146] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2387 | 31 | - | - | -0.00002 | [-0.00146, 0.00143] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2414 | 31 | - | - | 0.01493 | [0.00316, 0.02831] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2387 | 31 | - | - | 0.01478 | [0.00260, 0.02845] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2414 | 31 | - | - | 0.00364 | [0.00002, 0.00785] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2387 | 31 | - | - | 0.00335 | [-0.00047, 0.00775] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 124, 'GAME_WINNER': 62, 'SPREAD': 794, 'TEAM_TOTAL': 845, 'TOTAL': 589}; settlement: {'SETTLED': 2414}; close: {'OK': 2387, 'OK_STALE': 27}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 366 / 0.054 / 0.055 | 347 / 0.054 / 0.084 | 367 / 0.054 / 0.068 |
| 0.10-0.20 | 394 / 0.144 / 0.203 | 381 / 0.144 / 0.223 | 385 / 0.146 / 0.213 |
| 0.20-0.30 | 286 / 0.248 / 0.308 | 290 / 0.248 / 0.334 | 277 / 0.247 / 0.285 |
| 0.30-0.40 | 225 / 0.351 / 0.360 | 251 / 0.348 / 0.390 | 250 / 0.347 / 0.380 |
| 0.40-0.50 | 258 / 0.449 / 0.457 | 235 / 0.449 / 0.438 | 267 / 0.449 / 0.479 |
| 0.50-0.60 | 230 / 0.547 / 0.565 | 210 / 0.550 / 0.471 | 221 / 0.549 / 0.552 |
| 0.60-0.70 | 162 / 0.650 / 0.593 | 197 / 0.648 / 0.523 | 163 / 0.650 / 0.558 |
| 0.70-0.80 | 126 / 0.748 / 0.698 | 127 / 0.750 / 0.669 | 125 / 0.751 / 0.656 |
| 0.80-0.90 | 130 / 0.849 / 0.823 | 127 / 0.851 / 0.803 | 125 / 0.852 / 0.848 |
| 0.90-1.00 | 237 / 0.955 / 0.916 | 249 / 0.957 / 0.900 | 234 / 0.956 / 0.919 |

## Contract pricing — T-24h (1249 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1249 | 0.1754 | 0.5243 | 0.412 | 0.357 | 1249 | 0.1754 | 0.1748 | 0.1753 |
| DATA_ONLY | 1249 | 0.1868 | 0.5583 | 0.415 | 0.357 | 1249 | 0.1868 | 0.1748 | 0.1753 |
| HYBRID_30 | 1249 | 0.1767 | 0.5281 | 0.411 | 0.357 | 1249 | 0.1767 | 0.1748 | 0.1753 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1249 | 16 | 0.01140 | [-0.00716, 0.03242] | 0.01140 | [-0.00716, 0.03242] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1249 | 16 | 0.00124 | [-0.00488, 0.00789] | 0.00124 | [-0.00488, 0.00789] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1249 | 16 | -0.01016 | [-0.02502, 0.00383] | -0.01016 | [-0.02502, 0.00383] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1249 | 16 | - | - | 0.00059 | [-0.00092, 0.00203] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1234 | 16 | - | - | 0.00162 | [-0.00097, 0.00428] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1249 | 16 | - | - | 0.01199 | [-0.00606, 0.03286] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1234 | 16 | - | - | 0.01331 | [-0.00402, 0.03351] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1249 | 16 | - | - | 0.00183 | [-0.00440, 0.00876] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1234 | 16 | - | - | 0.00299 | [-0.00279, 0.00959] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 415, 'TEAM_TOTAL': 434, 'TOTAL': 304}; settlement: {'SETTLED': 1249}; close: {'OK': 1234, 'OK_STALE': 15}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 204 / 0.054 / 0.025 | 196 / 0.053 / 0.051 | 196 / 0.053 / 0.020 |
| 0.10-0.20 | 196 / 0.146 / 0.158 | 194 / 0.145 / 0.186 | 201 / 0.145 / 0.184 |
| 0.20-0.30 | 149 / 0.248 / 0.289 | 151 / 0.248 / 0.331 | 146 / 0.249 / 0.260 |
| 0.30-0.40 | 113 / 0.350 / 0.292 | 130 / 0.347 / 0.308 | 119 / 0.349 / 0.303 |
| 0.40-0.50 | 135 / 0.449 / 0.385 | 118 / 0.447 / 0.305 | 144 / 0.448 / 0.410 |
| 0.50-0.60 | 112 / 0.545 / 0.438 | 103 / 0.548 / 0.311 | 109 / 0.549 / 0.404 |
| 0.60-0.70 | 83 / 0.646 / 0.470 | 110 / 0.648 / 0.500 | 84 / 0.647 / 0.429 |
| 0.70-0.80 | 74 / 0.746 / 0.635 | 61 / 0.747 / 0.623 | 71 / 0.747 / 0.620 |
| 0.80-0.90 | 64 / 0.850 / 0.703 | 67 / 0.850 / 0.731 | 64 / 0.853 / 0.750 |
| 0.90-1.00 | 119 / 0.955 / 0.857 | 119 / 0.956 / 0.840 | 115 / 0.954 / 0.870 |

## Contract pricing — T-6h (937 contracts, 12 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 937 | 0.1727 | 0.5135 | 0.418 | 0.429 | 937 | 0.1727 | 0.1734 | 0.1751 |
| DATA_ONLY | 937 | 0.1801 | 0.5303 | 0.427 | 0.429 | 937 | 0.1801 | 0.1734 | 0.1751 |
| HYBRID_30 | 937 | 0.1730 | 0.5146 | 0.418 | 0.429 | 937 | 0.1730 | 0.1734 | 0.1751 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 937 | 12 | 0.00738 | [-0.01268, 0.02948] | 0.00738 | [-0.01268, 0.02948] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 937 | 12 | 0.00034 | [-0.00387, 0.00461] | 0.00034 | [-0.00387, 0.00461] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 937 | 12 | -0.00704 | [-0.02573, 0.00918] | -0.00704 | [-0.02573, 0.00918] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 937 | 12 | - | - | -0.00067 | [-0.00243, 0.00090] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 921 | 12 | - | - | -0.00134 | [-0.00435, 0.00165] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 937 | 12 | - | - | 0.00672 | [-0.01321, 0.02848] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 921 | 12 | - | - | 0.00637 | [-0.01413, 0.02872] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 937 | 12 | - | - | -0.00033 | [-0.00497, 0.00459] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 921 | 12 | - | - | -0.00087 | [-0.00636, 0.00468] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 48, 'GAME_WINNER': 24, 'SPREAD': 307, 'TEAM_TOTAL': 330, 'TOTAL': 228}; settlement: {'SETTLED': 937}; close: {'OK': 921, 'OK_STALE': 16}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 145 / 0.056 / 0.069 | 137 / 0.055 / 0.051 | 145 / 0.055 / 0.062 |
| 0.10-0.20 | 148 / 0.143 / 0.216 | 146 / 0.146 / 0.219 | 145 / 0.146 / 0.228 |
| 0.20-0.30 | 110 / 0.249 / 0.273 | 108 / 0.249 / 0.361 | 107 / 0.249 / 0.271 |
| 0.30-0.40 | 87 / 0.352 / 0.379 | 97 / 0.348 / 0.423 | 94 / 0.348 / 0.404 |
| 0.40-0.50 | 103 / 0.449 / 0.466 | 90 / 0.447 / 0.389 | 106 / 0.447 / 0.434 |
| 0.50-0.60 | 89 / 0.547 / 0.517 | 77 / 0.546 / 0.429 | 87 / 0.549 / 0.540 |
| 0.60-0.70 | 61 / 0.653 / 0.623 | 82 / 0.646 / 0.549 | 61 / 0.650 / 0.590 |
| 0.70-0.80 | 50 / 0.752 / 0.700 | 53 / 0.750 / 0.698 | 48 / 0.749 / 0.688 |
| 0.80-0.90 | 54 / 0.852 / 0.852 | 50 / 0.850 / 0.820 | 53 / 0.848 / 0.849 |
| 0.90-1.00 | 90 / 0.957 / 0.933 | 97 / 0.957 / 0.948 | 91 / 0.956 / 0.945 |

## Contract pricing — T-90m (1559 contracts, 20 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1559 | 0.1720 | 0.5164 | 0.416 | 0.389 | 1559 | 0.1720 | 0.1709 | 0.1720 |
| DATA_ONLY | 1559 | 0.1801 | 0.5386 | 0.421 | 0.389 | 1559 | 0.1801 | 0.1709 | 0.1720 |
| HYBRID_30 | 1559 | 0.1740 | 0.5191 | 0.413 | 0.389 | 1559 | 0.1740 | 0.1709 | 0.1720 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1559 | 20 | 0.00814 | [-0.00769, 0.02705] | 0.00814 | [-0.00769, 0.02705] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1559 | 20 | 0.00203 | [-0.00308, 0.00762] | 0.00203 | [-0.00308, 0.00762] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1559 | 20 | -0.00612 | [-0.01947, 0.00652] | -0.00612 | [-0.01947, 0.00652] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1559 | 20 | - | - | 0.00110 | [-0.00038, 0.00240] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1539 | 20 | - | - | 0.00116 | [-0.00090, 0.00319] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1559 | 20 | - | - | 0.00924 | [-0.00764, 0.02803] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1539 | 20 | - | - | 0.00950 | [-0.00724, 0.02868] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1559 | 20 | - | - | 0.00312 | [-0.00243, 0.00894] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1539 | 20 | - | - | 0.00329 | [-0.00247, 0.00941] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 80, 'GAME_WINNER': 40, 'SPREAD': 514, 'TEAM_TOTAL': 545, 'TOTAL': 380}; settlement: {'SETTLED': 1559}; close: {'OK': 1539, 'OK_STALE': 20}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 241 / 0.054 / 0.033 | 232 / 0.055 / 0.052 | 251 / 0.055 / 0.040 |
| 0.10-0.20 | 248 / 0.143 / 0.181 | 244 / 0.144 / 0.197 | 235 / 0.146 / 0.196 |
| 0.20-0.30 | 186 / 0.247 / 0.290 | 188 / 0.249 / 0.314 | 188 / 0.246 / 0.282 |
| 0.30-0.40 | 146 / 0.350 / 0.301 | 162 / 0.349 / 0.333 | 155 / 0.348 / 0.335 |
| 0.40-0.50 | 159 / 0.449 / 0.390 | 151 / 0.448 / 0.358 | 170 / 0.448 / 0.412 |
| 0.50-0.60 | 148 / 0.547 / 0.520 | 132 / 0.548 / 0.417 | 138 / 0.548 / 0.507 |
| 0.60-0.70 | 114 / 0.651 / 0.526 | 129 / 0.648 / 0.512 | 109 / 0.650 / 0.486 |
| 0.70-0.80 | 78 / 0.748 / 0.667 | 85 / 0.747 / 0.647 | 83 / 0.749 / 0.627 |
| 0.80-0.90 | 91 / 0.850 / 0.780 | 81 / 0.852 / 0.815 | 82 / 0.851 / 0.817 |
| 0.90-1.00 | 148 / 0.957 / 0.899 | 155 / 0.956 / 0.884 | 148 / 0.956 / 0.899 |

## Contract pricing — T-30m (2337 contracts, 30 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2337 | 0.1757 | 0.5243 | 0.414 | 0.416 | 2337 | 0.1757 | 0.1753 | 0.1766 |
| DATA_ONLY | 2337 | 0.1887 | 0.5600 | 0.424 | 0.416 | 2337 | 0.1887 | 0.1753 | 0.1766 |
| HYBRID_30 | 2337 | 0.1783 | 0.5314 | 0.414 | 0.416 | 2337 | 0.1783 | 0.1753 | 0.1766 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2337 | 30 | 0.01302 | [0.00136, 0.02466] | 0.01302 | [0.00136, 0.02466] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2337 | 30 | 0.00256 | [-0.00085, 0.00616] | 0.00256 | [-0.00085, 0.00616] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2337 | 30 | -0.01046 | [-0.01922, -0.00157] | -0.01046 | [-0.01922, -0.00157] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2337 | 30 | - | - | 0.00038 | [-0.00068, 0.00143] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2310 | 30 | - | - | -0.00001 | [-0.00146, 0.00138] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2337 | 30 | - | - | 0.01340 | [0.00172, 0.02505] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2310 | 30 | - | - | 0.01323 | [0.00127, 0.02524] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2337 | 30 | - | - | 0.00294 | [-0.00065, 0.00673] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2310 | 30 | - | - | 0.00264 | [-0.00124, 0.00667] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 120, 'GAME_WINNER': 60, 'SPREAD': 769, 'TEAM_TOTAL': 818, 'TOTAL': 570}; settlement: {'SETTLED': 2337}; close: {'OK': 2310, 'OK_STALE': 27}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 360 / 0.054 / 0.056 | 337 / 0.054 / 0.080 | 359 / 0.054 / 0.070 |
| 0.10-0.20 | 381 / 0.144 / 0.202 | 368 / 0.144 / 0.220 | 371 / 0.146 / 0.210 |
| 0.20-0.30 | 276 / 0.249 / 0.308 | 280 / 0.248 / 0.329 | 268 / 0.247 / 0.280 |
| 0.30-0.40 | 219 / 0.351 / 0.352 | 243 / 0.348 / 0.383 | 245 / 0.347 / 0.376 |
| 0.40-0.50 | 255 / 0.449 / 0.451 | 225 / 0.449 / 0.413 | 257 / 0.449 / 0.459 |
| 0.50-0.60 | 219 / 0.547 / 0.543 | 205 / 0.550 / 0.459 | 215 / 0.549 / 0.540 |
| 0.60-0.70 | 154 / 0.650 / 0.571 | 193 / 0.648 / 0.513 | 157 / 0.650 / 0.541 |
| 0.70-0.80 | 124 / 0.748 / 0.694 | 123 / 0.750 / 0.659 | 123 / 0.752 / 0.650 |
| 0.80-0.90 | 124 / 0.848 / 0.815 | 123 / 0.852 / 0.797 | 119 / 0.852 / 0.840 |
| 0.90-1.00 | 225 / 0.954 / 0.911 | 240 / 0.957 / 0.896 | 223 / 0.956 / 0.915 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 16 | 4 | 1 | 2 | 9 | 0 | 0.333 [0.061, 0.792] | 0.333 | 0.333 | 0.00 |
| T-24h | DATA_ONLY | total | 16 | 3 | 6 | 1 | 6 | 0 | 0.857 [0.487, 0.974] | 0.538 | 0.462 | 0.54 |
| T-24h | HYBRID_30 (derived) | margin | 16 | 10 | 0 | 1 | 5 | 0 | 0.000 [0.000, 0.793] | 0.167 | 0.167 | -0.08 |
| T-24h | HYBRID_30 (derived) | total | 16 | 13 | 0 | 0 | 3 | 0 | - - | 0.333 | 0.333 | 0.00 |
| T-6h | DATA_ONLY | margin | 12 | 2 | 4 | 1 | 5 | 0 | 0.800 [0.376, 0.964] | 0.500 | 0.600 | 0.25 |
| T-6h | DATA_ONLY | total | 12 | 4 | 2 | 2 | 4 | 0 | 0.500 [0.150, 0.850] | 0.375 | 0.375 | 0.00 |
| T-6h | HYBRID_30 (derived) | margin | 12 | 6 | 1 | 1 | 4 | 0 | 0.500 [0.095, 0.905] | 0.333 | 0.333 | 0.00 |
| T-6h | HYBRID_30 (derived) | total | 12 | 9 | 1 | 0 | 2 | 0 | 1.000 [0.207, 1.000] | 0.667 | 0.333 | 0.17 |
| T-90m | DATA_ONLY | margin | 20 | 4 | 3 | 1 | 12 | 0 | 0.750 [0.301, 0.954] | 0.500 | 0.500 | 0.03 |
| T-90m | DATA_ONLY | total | 20 | 5 | 3 | 2 | 10 | 0 | 0.600 [0.231, 0.882] | 0.400 | 0.400 | 0.03 |
| T-90m | HYBRID_30 (derived) | margin | 20 | 12 | 0 | 1 | 7 | 0 | 0.000 [0.000, 0.793] | 0.375 | 0.375 | -0.12 |
| T-90m | HYBRID_30 (derived) | total | 20 | 16 | 0 | 1 | 3 | 0 | 0.000 [0.000, 0.793] | 0.250 | 0.250 | -0.25 |
| T-30m | DATA_ONLY | margin | 30 | 7 | 3 | 1 | 19 | 0 | 0.750 [0.301, 0.954] | 0.391 | 0.391 | 0.07 |
| T-30m | DATA_ONLY | total | 30 | 9 | 4 | 3 | 14 | 0 | 0.571 [0.250, 0.842] | 0.333 | 0.333 | 0.02 |
| T-30m | HYBRID_30 (derived) | margin | 30 | 21 | 0 | 1 | 8 | 0 | 0.000 [0.000, 0.793] | 0.333 | 0.333 | -0.11 |
| T-30m | HYBRID_30 (derived) | total | 30 | 23 | 1 | 1 | 5 | 0 | 0.500 [0.095, 0.905] | 0.143 | 0.143 | 0.00 |
| latest_pregame | DATA_ONLY | margin | 31 | 7 | 3 | 1 | 20 | 0 | 0.750 [0.301, 0.954] | 0.375 | 0.375 | 0.06 |
| latest_pregame | DATA_ONLY | total | 31 | 9 | 4 | 3 | 15 | 0 | 0.571 [0.250, 0.842] | 0.318 | 0.318 | 0.02 |
| latest_pregame | HYBRID_30 (derived) | margin | 31 | 22 | 0 | 1 | 8 | 0 | 0.000 [0.000, 0.793] | 0.333 | 0.333 | -0.11 |
| latest_pregame | HYBRID_30 (derived) | total | 31 | 23 | 1 | 1 | 6 | 0 | 0.500 [0.095, 0.905] | 0.125 | 0.125 | 0.00 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 7 | 1 | 1 | 5 | 0 | 0.500 |
| margin | 1-2 | 6 | 1 | 0 | 5 | 0 | 1.000 |
| margin | 2-3 | 7 | 2 | 0 | 5 | 0 | 1.000 |
| margin | 3-5 | 9 | 0 | 1 | 8 | 0 | 0.000 |
| margin | >5 | 2 | 0 | 0 | 2 | 0 | - |
| total | <=1 | 9 | 1 | 0 | 8 | 0 | 1.000 |
| total | 1-2 | 8 | 0 | 2 | 6 | 0 | 0.000 |
| total | 2-3 | 4 | 3 | 0 | 1 | 0 | 1.000 |
| total | 3-5 | 8 | 1 | 1 | 6 | 0 | 0.500 |
| total | >5 | 2 | 0 | 0 | 2 | 0 | - |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 0 | 0 | - | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 0 | 0 | - | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

1999 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_01_CHI_CAR | Jonathon Brooks | receiving_yards | 1.0 | 0–11 | 48 | 64.75 | 0.99 | 1.0 | 2 | 0.98 | 24.00 | EXPECTED_ACTIVE | True | 0.427 | EFFICIENCY_MISS |
| 2026_02_IND_KC | Emmett Johnson | receiving_yards | 1.0 | 0–11 | 20 | 26.98 | 0.99 | 0.9 | 2 | 1.08 | 10.00 | EXPECTED_ACTIVE | True | 0.273 | EFFICIENCY_MISS |
| 2026_02_SEA_ARI | Jeremiyah Love | receiving_yards | 1.0 | 0–11 | 16 | 21.58 | 0.97 | 1.0 | 3 | 1.05 | 5.33 | EXPECTED_ACTIVE | True | 0.506 | EFFICIENCY_MISS |
| 2026_01_SF_LA | Deebo Samuel Sr. | rushing_yards | 1.0 | 0–4 | 12 | 16.19 | 0.99 | 2.0 | 1 | 0.50 | 12.00 | EXPECTED_ACTIVE | True | 0.460 | EFFICIENCY_MISS |
| 2026_02_SEA_ARI | Jadarian Price | receiving_yards | 1.0 | 0–11 | 8 | 10.79 | 0.89 | 0.9 | 2 | 1.08 | 4.00 | EXPECTED_ACTIVE | True | -0.293 | EFFICIENCY_MISS |
| 2026_01_CLE_JAX | Bhayshul Tuten | receiving_yards | 2.9 | 0–31 | 22 | 9.89 | 0.89 | 1.3 | 1 | 2.33 | 22.00 | EXPECTED_ACTIVE | True | 0.283 | EFFICIENCY_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | receiving_yards | 2.7 | 0–29 | 21 | 9.44 | 0.89 | 1.1 | 3 | 2.49 | 7.00 | EXPECTED_ACTIVE | True | 0.361 | EFFICIENCY_MISS |
| 2026_01_WAS_PHI | Jacory Croskey-Merritt | receiving_yards | 1.0 | 0–11 | -7 | -9.44 | 0.05 | 1.2 | 1 | 0.83 | -7.00 | EXPECTED_ACTIVE | True | -0.183 | EFFICIENCY_MISS |
| 2026_02_GB_NYJ | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 6 | 8.09 | 0.85 | 0.9 | 2 | 1.05 | 3.00 | EXPECTED_ACTIVE | True | -0.303 | EFFICIENCY_MISS |
| 2026_02_MIA_SF | Kyle Juszczyk | touchdowns | 0.0 | -–- | 1 | 8.00 | - | 0.0 | 2 | - | - | EXPECTED_ACTIVE | True | 0.068 | UNEXPLAINED_VARIANCE |
| 2026_02_CAR_ATL | Jonathon Brooks | receiving_yards | 1.0 | 0–11 | -5 | -6.75 | 0.05 | 1.0 | 1 | 1.00 | -5.00 | EXPECTED_ACTIVE | True | -0.233 | EFFICIENCY_MISS |
| 2026_02_GB_NYJ | Chris Brooks | receiving_yards | 3.1 | 0–32 | 15 | 6.74 | 0.83 | 1.3 | 2 | 2.41 | 7.50 | EXPECTED_ACTIVE | True | 0.210 | EFFICIENCY_MISS |
| 2026_02_NYG_LA | Blake Corum | receiving_yards | 2.9 | 0–30 | 13 | 5.85 | 0.82 | 1.2 | 1 | 2.33 | 13.00 | EXPECTED_ACTIVE | True | -0.050 | EFFICIENCY_MISS |
| 2026_02_GB_NYJ | Kenyon Sadiq | receiving_yards | 3.5 | 0–37 | 17 | 5.73 | 0.83 | 1.1 | 3 | 3.16 | 5.67 | EXPECTED_ACTIVE | True | 0.473 | TEAM_VOLUME_MISS |
| 2026_02_GB_NYJ | Breece Hall | receiving_yards | 12.2 | 0–53 | 63 | 5.31 | 0.96 | 1.8 | 5 | 6.88 | 12.60 | EXPECTED_ACTIVE | True | 0.314 | TEAM_VOLUME_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | touchdowns | 0.0 | -–- | 1 | 4.99 | - | 2.7 | 4 | - | - | EXPECTED_ACTIVE | True | 0.047 | UNEXPLAINED_VARIANCE |
| 2026_01_CHI_CAR | Kalif Raymond | receptions | 1.5 | 0–5 | 8 | 4.72 | 0.99 | 2.1 | 9 | 0.70 | 0.89 | EXPECTED_ACTIVE | True | 0.070 | OPPORTUNITY_MISS |
| 2026_01_DAL_NYG | Isaiah Likely | receptions | 1.4 | 0–5 | 8 | 4.72 | 0.99 | 1.9 | 8 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.406 | OPPORTUNITY_MISS |
| 2026_01_BUF_HOU | Dalton Kincaid | receiving_yards | 26.6 | 0–74 | 130 | 4.68 | 0.99 | 2.3 | 6 | 11.60 | 21.67 | EXPECTED_ACTIVE | True | 0.238 | OPPORTUNITY_MISS |
| 2026_02_NYG_LA | Davante Adams | receiving_yards | 48.7 | 4–113 | 195 | 4.63 | 0.99 | 5.5 | 10 | 8.91 | 19.50 | EXPECTED_ACTIVE | True | 0.196 | EFFICIENCY_MISS |
| 2026_02_CIN_HOU | Foster Moreau | receiving_yards | 7.7 | 0–34 | 34 | 4.59 | 0.95 | 1.4 | 2 | 5.47 | 17.00 | EXPECTED_ACTIVE | True | 0.137 | EFFICIENCY_MISS |
| 2026_02_CIN_HOU | Dalton Schultz | receptions | 2.5 | 0–6 | 12 | 4.50 | 0.99 | 3.2 | 14 | 0.78 | 0.86 | EXPECTED_ACTIVE | True | 0.373 | TEAM_VOLUME_MISS |
| 2026_02_CLE_TB | Denzel Boston | receiving_yards | 19.3 | 0–65 | 95 | 4.46 | 0.98 | 1.9 | 7 | 10.28 | 13.57 | EXPECTED_ACTIVE | True | 0.318 | TEAM_VOLUME_MISS |
| 2026_01_BAL_IND | Derrick Henry | receiving_yards | 5.3 | 0–56 | 19 | 4.27 | 0.80 | 1.3 | 1 | 4.05 | 19.00 | EXPECTED_ACTIVE | True | 0.062 | EFFICIENCY_MISS |
| 2026_02_NO_BAL | Derrick Henry | receiving_yards | 5.6 | 0–59 | 19 | 4.27 | 0.80 | 1.3 | 3 | 4.27 | 6.33 | EXPECTED_ACTIVE | True | 0.093 | OPPORTUNITY_MISS |
| 2026_01_CLE_JAX | Denzel Boston | touchdowns | 0.1 | -–- | 1 | 4.24 | - | 4.5 | 4 | - | - | EXPECTED_ACTIVE | True | 0.062 | UNEXPLAINED_VARIANCE |
| 2026_01_MIA_LV | Caleb Douglas | receiving_yards | 19.8 | 0–67 | 94 | 4.20 | 0.98 | 1.9 | 7 | 10.66 | 13.43 | EXPECTED_ACTIVE | True | 0.198 | OPPORTUNITY_MISS |
| 2026_02_CLE_TB | Denzel Boston | touchdowns | 0.1 | -–- | 1 | 4.18 | - | 4.5 | 7 | - | - | EXPECTED_ACTIVE | True | 0.131 | UNEXPLAINED_VARIANCE |
| 2026_02_WAS_DAL | Rachaad White | receiving_yards | 9.5 | 0–41 | 40 | 4.15 | 0.94 | 1.6 | 6 | 5.78 | 6.67 | EXPECTED_ACTIVE | True | 0.191 | OPPORTUNITY_MISS |
| 2026_02_IND_KC | Kenneth Walker | receiving_yards | 13.1 | 0–44 | 61 | 4.12 | 0.98 | 1.7 | 10 | 7.86 | 6.10 | EXPECTED_ACTIVE | True | 0.313 | TEAM_VOLUME_MISS |
| 2026_01_DAL_NYG | Isaiah Likely | receiving_yards | 16.8 | 0–57 | 78 | 4.11 | 0.97 | 1.9 | 8 | 8.94 | 9.75 | EXPECTED_ACTIVE | True | 0.420 | OPPORTUNITY_MISS |
| 2026_01_CHI_CAR | Jalen Coker | receptions | 2.2 | 0–6 | 8 | 4.05 | 0.98 | 3.0 | 9 | 0.71 | 0.89 | EXPECTED_ACTIVE | True | 0.253 | OPPORTUNITY_MISS |
| 2026_01_CLE_JAX | Trevor Lawrence | passing_tds | 1.6 | 0–4 | 4 | 4.05 | 0.95 | 33.5 | 23 | 0.05 | 0.17 | EXPECTED_ACTIVE | True | 0.010 | EFFICIENCY_MISS |
| 2026_01_NO_DET | Travis Etienne Jr. | receptions | 1.3 | 0–5 | 7 | 4.05 | 0.98 | 1.9 | 9 | 0.71 | 0.78 | EXPECTED_ACTIVE | True | 0.363 | OPPORTUNITY_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | receptions | 0.7 | 0–5 | 3 | 4.05 | 0.85 | 1.1 | 3 | 0.67 | 1.00 | EXPECTED_ACTIVE | True | 0.292 | OPPORTUNITY_MISS |
| 2026_01_TB_CIN | Samaje Perine | receiving_yards | 7.3 | 0–32 | 30 | 4.05 | 0.93 | 1.5 | 3 | 4.95 | 10.00 | EXPECTED_ACTIVE | True | 0.055 | EFFICIENCY_MISS |
| 2026_01_TB_CIN | Bucky Irving | receptions | 1.4 | 0–5 | 7 | 4.05 | 0.98 | 1.9 | 7 | 0.76 | 1.00 | EXPECTED_ACTIVE | True | 0.142 | OPPORTUNITY_MISS |
| 2026_02_CAR_ATL | Jalen Coker | receptions | 2.0 | 0–6 | 8 | 4.05 | 0.98 | 2.9 | 9 | 0.70 | 0.89 | EXPECTED_ACTIVE | True | 0.317 | OPPORTUNITY_MISS |
| 2026_02_DET_BUF | Jared Goff | passing_tds | 1.6 | 0–4 | 4 | 4.05 | 0.95 | 34.9 | 38 | 0.05 | 0.11 | EXPECTED_ACTIVE | True | 0.060 | EFFICIENCY_MISS |
| 2026_02_NO_BAL | Derrick Henry | receptions | 0.9 | 0–5 | 3 | 4.05 | 0.85 | 1.3 | 3 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.090 | OPPORTUNITY_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 349, 'UNEXPLAINED_VARIANCE': 62, 'TEAM_VOLUME_MISS': 74, 'OPPORTUNITY_MISS': 687, 'NO_LARGE_MISS': 765, 'INSUFFICIENT_DATA': 38, 'AVAILABILITY_MISS': 24}.
Missing usage (no snap table or stats row): 62.

## Decision funnel (BET / WATCH / PASS accounting of the existing gates; no authority)

69 snapshot(s). A contract's terminal state is where it left the existing gate sequence when the model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).

### Newest snapshot 20260924T231506Z (44474 markets)

| stage | markets |
|---|---|
| discovered | 44474 |
| mapped | 36180 |
| supported | 5083 |
| priced | 5083 |
| raw_disagreement | 3756 |
| tradable_book | 3666 |
| data_quality | 3652 |
| executable_price | 2604 |
| liquidity | 1220 |

Terminal states: {'PASS': 42209, 'WATCH': 1045, 'BET': 1220}

| family | BET | WATCH | PASS |
|---|---|---|---|
| AWARD | 0 | 0 | 869 |
| BOTH_TEAMS_SCORE | 0 | 0 | 184 |
| BOTH_TEAMS_SCORE_N | 0 | 6 | 178 |
| COACH_EVENT | 0 | 0 | 64 |
| CONFERENCE_WINNER | 0 | 0 | 32 |
| DIVISION_WINNER | 0 | 0 | 32 |
| DRAFT | 0 | 0 | 40 |
| FIRST_TD_SCORER | 0 | 0 | 1153 |
| FIRST_TD_TEAM | 0 | 0 | 1298 |
| GAME_EVENT | 0 | 0 | 189 |
| GAME_PLAYER_LEADER | 0 | 0 | 351 |
| GAME_STAT | 0 | 0 | 5 |
| GAME_WINNER | 0 | 34 | 94 |
| HALF_FULL_RESULT | 0 | 0 | 432 |
| MAKE_PLAYOFFS | 0 | 0 | 33 |
| NFL_BUSINESS_EVENT | 0 | 0 | 5 |
| NOT_NFL_OR_UNKNOWN | 0 | 0 | 2 |
| PERIOD_WINNER | 0 | 0 | 864 |
| PLAYER_AVAILABILITY | 0 | 0 | 23 |
| PLAYER_ROLE_EVENT | 0 | 0 | 177 |
| PLAYER_STAT | 1085 | 510 | 15379 |
| RACE_TO_N | 0 | 0 | 735 |
| SEASON_DIVISION_ORDER | 0 | 0 | 192 |
| SEASON_DIVISION_STAT | 0 | 0 | 80 |
| SEASON_FANTASY | 0 | 0 | 1129 |
| SEASON_LEADER | 0 | 0 | 603 |
| SEASON_MATCHUP | 0 | 0 | 496 |
| SEASON_PLAYER_SPECIAL | 0 | 0 | 306 |
| SEASON_PLAYER_STAT | 0 | 0 | 1129 |
| SEASON_SEED | 0 | 0 | 224 |
| SEASON_SPECIAL | 0 | 0 | 66 |
| SEASON_TEAM_EVENT | 0 | 0 | 390 |
| SEASON_TEAM_H2H | 0 | 0 | 22 |
| SEASON_TEAM_LEADER | 0 | 0 | 96 |
| SEASON_WINS | 0 | 0 | 547 |
| SPREAD | 55 | 195 | 4812 |
| SUPER_BOWL_EVENT | 0 | 0 | 241 |
| SUPER_BOWL_WINNER | 0 | 0 | 32 |
| TEAM_STAT | 0 | 0 | 1206 |
| TEAM_TOTAL | 58 | 150 | 2165 |
| TEAM_WINS_BY_WEEK | 0 | 0 | 728 |
| TOTAL | 22 | 150 | 4012 |
| TOTAL_TD | 0 | 0 | 214 |
| TRANSACTION_EVENT | 0 | 0 | 281 |
| UNKNOWN_NEEDS_CLASSIFICATION | 0 | 0 | 386 |
| WEEK_EVENT | 0 | 0 | 32 |
| WEEK_LEADER | 0 | 0 | 359 |
| WIN_MARGIN_BUCKET | 0 | 0 | 322 |

| rejection reason | n |
|---|---|
| POST_KICKOFF_EXCLUDED | 23399 |
| unmapped | 8294 |
| UNSUPPORTED_MODEL | 5033 |
| UNSUPPORTED_RULES | 2549 |
| no order book observed for this ticker (books are captured i | 1381 |
| no positive disagreement against either executable ask | 1327 |
| ask 0.99 above the zero-net-EV ceiling 0.98 | 188 |
| UNSUPPORTED_IDENTITY | 116 |
| book not tradable for ranking | 90 |
| ask 0.98 above the zero-net-EV ceiling 0.97 | 61 |
| ask 0.97 above the zero-net-EV ceiling 0.96 | 22 |
| ask 0.06 above the zero-net-EV ceiling 0.05 | 19 |
| ask 0.95 above the zero-net-EV ceiling 0.94 | 18 |
| ask 0.96 above the zero-net-EV ceiling 0.95 | 14 |
| ask 0.88 above the zero-net-EV ceiling 0.87 | 14 |

WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee schedule (`watch_ceiling`). Not replayed: ['portfolio_risk_policy (needs a stake and bankroll)', "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own confirmation is the STALE_DATA support state)"].

Across all 69 snapshots (repeated markets counted per snapshot): {'PASS': 2004433, 'WATCH': 47568, 'BET': 38230}.

