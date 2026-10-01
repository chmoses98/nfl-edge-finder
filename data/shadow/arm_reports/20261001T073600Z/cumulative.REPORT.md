# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 47 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 2522 | 47 | 3 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 22 | 22 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 28 | 28 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 35 | 35 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 46 | 46 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 47 | 47 | 3 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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

## Game-centre accuracy — latest_pregame (47 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 47 | 3 | 10.77 | 13.46 | 1.55 | 10.86 | 14.20 | -1.65 | 0.232 |
| DATA_ONLY | 47 | 3 | 11.43 | 14.02 | 1.07 | 11.85 | 15.21 | -0.69 | 0.253 |
| HYBRID_30 | 47 | 3 | 10.94 | 13.57 | 1.41 | 11.12 | 14.46 | -1.36 | 0.238 |
| market at snapshot | 47 | 3 | 10.77 | 13.46 | 1.55 | 10.86 | 14.20 | -1.65 | - |
| market at close | 47 | 3 | 10.79 | 13.45 | 1.57 | 10.98 | 14.34 | -1.60 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 47 | margin | 0.666 | 0.405 | [-0.127, 1.460] | 0.404 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 47 | total | 0.985 | 0.374 | [0.252, 1.718] | 0.404 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 47 | margin | 0.178 | 0.122 | [-0.062, 0.417] | 0.447 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 47 | total | 0.262 | 0.116 | [0.035, 0.489] | 0.447 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 47 | margin | -0.489 | 0.285 | [-1.047, 0.069] | 0.596 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 47 | total | -0.723 | 0.261 | [-1.235, -0.211] | 0.596 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 47 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 47 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 47 | margin | 0.666 | 0.405 | [-0.127, 1.460] | 0.404 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 47 | total | 0.985 | 0.374 | [0.252, 1.718] | 0.404 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 47 | margin | 0.178 | 0.122 | [-0.062, 0.417] | 0.447 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 47 | total | 0.262 | 0.116 | [0.035, 0.489] | 0.447 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 47 | margin | -0.021 | 0.053 | [-0.124, 0.082] | 0.106 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 47 | total | -0.117 | 0.068 | [-0.251, 0.017] | 0.213 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 47 | margin | 0.645 | 0.406 | [-0.150, 1.440] | 0.383 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 47 | total | 0.868 | 0.385 | [0.113, 1.623] | 0.404 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 47 | margin | 0.156 | 0.131 | [-0.100, 0.413] | 0.447 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 47 | total | 0.145 | 0.137 | [-0.123, 0.413] | 0.468 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 47 | 6 | 4 | 37 | 0 | 0.600 | 0.404 | 2.35 |
| DATA_ONLY | total | 47 | 8 | 6 | 33 | 0 | 0.571 | 0.404 | 2.11 |
| HYBRID_30 | margin | 47 | 6 | 4 | 37 | 0 | 0.600 | 0.447 | 0.71 |
| HYBRID_30 | total | 47 | 8 | 6 | 33 | 0 | 0.571 | 0.447 | 0.63 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 13 | 8.72 | 8.19 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.04 | 9.62 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.67 | 21.83 | - |
| DATA_ONLY | total | <=1 | 16 | 13.14 | 13.31 | 0.667 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 7 | 5.32 | 5.14 | 0.800 |
| DATA_ONLY | total | 3-5 | 10 | 12.91 | 9.60 | 0.500 |
| DATA_ONLY | total | >5 | 3 | 20.56 | 14.33 | - |
| HYBRID_30 | margin | <=1 | 36 | 9.79 | 9.68 | 0.667 |
| HYBRID_30 | margin | 1-2 | 11 | 14.71 | 14.32 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 37 | 10.95 | 10.96 | 0.583 |
| HYBRID_30 | total | 1-2 | 9 | 10.73 | 9.61 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 47}; DATA_ONLY quality states: {'OK': 47}; close centre status: {'OK': 47}.

## Game-centre accuracy — T-24h (22 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 22 | 3 | 11.48 | 13.88 | 1.93 | 10.50 | 13.12 | 1.95 | 0.241 |
| DATA_ONLY | 22 | 3 | 12.00 | 14.40 | 0.93 | 10.65 | 13.71 | 2.46 | 0.250 |
| HYBRID_30 | 22 | 3 | 11.63 | 13.95 | 1.63 | 10.49 | 13.24 | 2.11 | 0.243 |
| market at snapshot | 22 | 3 | 11.48 | 13.88 | 1.93 | 10.50 | 13.12 | 1.95 | - |
| market at close | 22 | 3 | 11.50 | 13.86 | 2.14 | 10.30 | 13.07 | 1.80 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 22 | margin | 0.520 | 0.707 | [-0.867, 1.906] | 0.409 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 22 | total | 0.147 | 0.573 | [-0.977, 1.271] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 22 | margin | 0.156 | 0.212 | [-0.260, 0.572] | 0.409 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 22 | total | -0.007 | 0.180 | [-0.360, 0.346] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 22 | margin | -0.364 | 0.495 | [-1.334, 0.607] | 0.591 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 22 | total | -0.154 | 0.400 | [-0.939, 0.630] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 22 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 22 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 22 | margin | 0.520 | 0.707 | [-0.867, 1.906] | 0.409 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 22 | total | 0.147 | 0.573 | [-0.977, 1.271] | 0.545 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 22 | margin | 0.156 | 0.212 | [-0.260, 0.572] | 0.409 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 22 | total | -0.007 | 0.180 | [-0.360, 0.346] | 0.545 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 22 | margin | -0.023 | 0.101 | [-0.221, 0.176] | 0.182 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 22 | total | 0.205 | 0.163 | [-0.116, 0.525] | 0.091 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 22 | margin | 0.497 | 0.708 | [-0.891, 1.885] | 0.409 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 22 | total | 0.352 | 0.499 | [-0.626, 1.329] | 0.409 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 22 | margin | 0.133 | 0.229 | [-0.316, 0.583] | 0.455 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 22 | total | 0.197 | 0.154 | [-0.105, 0.499] | 0.318 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 22 | 2 | 6 | 14 | 0 | 0.250 | 0.409 | 2.61 |
| DATA_ONLY | total | 22 | 9 | 1 | 12 | 0 | 0.900 | 0.545 | 2.41 |
| HYBRID_30 | margin | 22 | 2 | 6 | 14 | 0 | 0.250 | 0.409 | 0.78 |
| HYBRID_30 | total | 22 | 9 | 1 | 12 | 0 | 0.900 | 0.545 | 0.72 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 6 | 8.73 | 8.75 | 0.000 |
| DATA_ONLY | margin | 1-2 | 4 | 6.52 | 5.88 | 1.000 |
| DATA_ONLY | margin | 2-3 | 4 | 11.07 | 10.88 | - |
| DATA_ONLY | margin | 3-5 | 5 | 14.03 | 13.20 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.69 | 22.33 | 0.500 |
| DATA_ONLY | total | <=1 | 4 | 10.62 | 11.12 | 1.000 |
| DATA_ONLY | total | 1-2 | 4 | 9.99 | 9.38 | 0.000 |
| DATA_ONLY | total | 2-3 | 7 | 9.24 | 9.86 | 1.000 |
| DATA_ONLY | total | 3-5 | 6 | 12.33 | 12.08 | 1.000 |
| DATA_ONLY | total | >5 | 1 | 13.14 | 7.50 | 1.000 |
| HYBRID_30 | margin | <=1 | 15 | 8.80 | 8.80 | 0.167 |
| HYBRID_30 | margin | 1-2 | 6 | 16.93 | 16.00 | 0.000 |
| HYBRID_30 | margin | 2-3 | 1 | 22.29 | 24.50 | 1.000 |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 18 | 10.30 | 10.47 | 0.889 |
| HYBRID_30 | total | 1-2 | 4 | 11.36 | 10.62 | 1.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 22}; DATA_ONLY quality states: {'OK': 22}; close centre status: {'OK': 22}.

## Game-centre accuracy — T-6h (28 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 28 | 3 | 10.38 | 13.36 | -0.09 | 9.27 | 11.18 | -1.98 | 0.256 |
| DATA_ONLY | 28 | 3 | 10.79 | 13.34 | -0.65 | 9.95 | 12.25 | -1.05 | 0.255 |
| HYBRID_30 | 28 | 3 | 10.50 | 13.28 | -0.26 | 9.39 | 11.44 | -1.70 | 0.254 |
| market at snapshot | 28 | 3 | 10.38 | 13.36 | -0.09 | 9.27 | 11.18 | -1.98 | - |
| market at close | 28 | 3 | 10.38 | 13.34 | -0.05 | 9.45 | 11.37 | -1.98 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 28 | margin | 0.418 | 0.589 | [-0.735, 1.572] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 28 | total | 0.686 | 0.499 | [-0.293, 1.665] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 28 | margin | 0.126 | 0.177 | [-0.221, 0.472] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 28 | total | 0.125 | 0.149 | [-0.166, 0.416] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 28 | margin | -0.293 | 0.412 | [-1.100, 0.515] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 28 | total | -0.561 | 0.365 | [-1.276, 0.155] | 0.571 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 28 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 28 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 28 | margin | 0.418 | 0.589 | [-0.735, 1.572] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 28 | total | 0.686 | 0.499 | [-0.293, 1.665] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 28 | margin | 0.126 | 0.177 | [-0.221, 0.472] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 28 | total | 0.125 | 0.149 | [-0.166, 0.416] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 28 | margin | 0.000 | 0.118 | [-0.231, 0.231] | 0.179 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 28 | total | -0.179 | 0.155 | [-0.482, 0.125] | 0.286 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 28 | margin | 0.418 | 0.573 | [-0.704, 1.541] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 28 | total | 0.507 | 0.523 | [-0.519, 1.533] | 0.464 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 28 | margin | 0.126 | 0.188 | [-0.244, 0.495] | 0.393 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 28 | total | -0.054 | 0.208 | [-0.461, 0.354] | 0.536 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 28 | 7 | 3 | 18 | 0 | 0.700 | 0.429 | 2.55 |
| DATA_ONLY | total | 28 | 8 | 5 | 15 | 0 | 0.615 | 0.429 | 2.11 |
| HYBRID_30 | margin | 28 | 7 | 3 | 18 | 0 | 0.700 | 0.429 | 0.76 |
| HYBRID_30 | total | 28 | 8 | 5 | 15 | 0 | 0.615 | 0.500 | 0.63 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 5 | 11.29 | 11.50 | 0.500 |
| DATA_ONLY | margin | 1-2 | 9 | 9.84 | 9.22 | 0.667 |
| DATA_ONLY | margin | 2-3 | 5 | 10.24 | 9.80 | 1.000 |
| DATA_ONLY | margin | 3-5 | 6 | 9.07 | 9.08 | 0.500 |
| DATA_ONLY | margin | >5 | 3 | 17.19 | 15.50 | 1.000 |
| DATA_ONLY | total | <=1 | 9 | 9.15 | 9.22 | 0.750 |
| DATA_ONLY | total | 1-2 | 9 | 9.61 | 9.94 | 0.600 |
| DATA_ONLY | total | 2-3 | 4 | 6.32 | 6.25 | 0.000 |
| DATA_ONLY | total | 3-5 | 3 | 13.15 | 11.83 | - |
| DATA_ONLY | total | >5 | 3 | 15.04 | 8.83 | 1.000 |
| HYBRID_30 | margin | <=1 | 20 | 9.85 | 9.80 | 0.750 |
| HYBRID_30 | margin | 1-2 | 8 | 12.12 | 11.81 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 23 | 9.36 | 9.39 | 0.545 |
| HYBRID_30 | total | 1-2 | 4 | 6.71 | 6.25 | 1.000 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 28}; DATA_ONLY quality states: {'OK': 28}; close centre status: {'OK': 28}.

## Game-centre accuracy — T-90m (35 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 35 | 3 | 9.84 | 12.56 | 0.41 | 10.17 | 12.82 | 0.20 | 0.246 |
| DATA_ONLY | 35 | 3 | 10.26 | 12.86 | -0.22 | 10.80 | 13.62 | 0.91 | 0.251 |
| HYBRID_30 | 35 | 3 | 9.96 | 12.57 | 0.23 | 10.32 | 13.01 | 0.41 | 0.246 |
| market at snapshot | 35 | 3 | 9.84 | 12.56 | 0.41 | 10.17 | 12.82 | 0.20 | - |
| market at close | 35 | 3 | 9.86 | 12.56 | 0.40 | 10.16 | 12.76 | 0.13 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 35 | margin | 0.421 | 0.515 | [-0.588, 1.431] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 35 | total | 0.633 | 0.435 | [-0.219, 1.486] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 35 | margin | 0.116 | 0.155 | [-0.187, 0.420] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 35 | total | 0.145 | 0.135 | [-0.119, 0.410] | 0.486 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 35 | margin | -0.305 | 0.360 | [-1.012, 0.401] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 35 | total | -0.488 | 0.304 | [-1.085, 0.109] | 0.571 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 35 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 35 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 35 | margin | 0.421 | 0.515 | [-0.588, 1.431] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 35 | total | 0.633 | 0.435 | [-0.219, 1.486] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 35 | margin | 0.116 | 0.155 | [-0.187, 0.420] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 35 | total | 0.145 | 0.135 | [-0.119, 0.410] | 0.486 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 35 | margin | -0.014 | 0.060 | [-0.131, 0.103] | 0.114 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 35 | total | 0.014 | 0.093 | [-0.168, 0.196] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 35 | margin | 0.407 | 0.514 | [-0.601, 1.415] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 35 | total | 0.648 | 0.456 | [-0.246, 1.542] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 35 | margin | 0.102 | 0.161 | [-0.214, 0.418] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 35 | total | 0.160 | 0.171 | [-0.176, 0.495] | 0.429 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 35 | 5 | 4 | 26 | 0 | 0.556 | 0.400 | 2.53 |
| DATA_ONLY | total | 35 | 8 | 6 | 21 | 0 | 0.571 | 0.429 | 2.13 |
| HYBRID_30 | margin | 35 | 5 | 4 | 26 | 0 | 0.556 | 0.429 | 0.76 |
| HYBRID_30 | total | 35 | 8 | 6 | 21 | 0 | 0.571 | 0.486 | 0.64 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 6 | 6.74 | 6.67 | 0.000 |
| DATA_ONLY | margin | 1-2 | 9 | 8.15 | 7.72 | 1.000 |
| DATA_ONLY | margin | 2-3 | 10 | 9.74 | 9.70 | 0.750 |
| DATA_ONLY | margin | 3-5 | 7 | 11.00 | 10.36 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.67 | 21.83 | - |
| DATA_ONLY | total | <=1 | 11 | 12.23 | 12.45 | 0.800 |
| DATA_ONLY | total | 1-2 | 9 | 6.06 | 6.50 | 0.333 |
| DATA_ONLY | total | 2-3 | 6 | 10.10 | 9.58 | 1.000 |
| DATA_ONLY | total | 3-5 | 7 | 11.28 | 9.43 | 0.000 |
| DATA_ONLY | total | >5 | 2 | 24.81 | 18.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 25 | 8.30 | 8.26 | 0.625 |
| HYBRID_30 | margin | 1-2 | 10 | 14.10 | 13.80 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 28 | 9.91 | 9.93 | 0.727 |
| HYBRID_30 | total | 1-2 | 6 | 10.33 | 9.75 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 35}; DATA_ONLY quality states: {'OK': 35}; close centre status: {'OK': 35}.

## Game-centre accuracy — T-30m (46 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 46 | 3 | 10.90 | 13.59 | 1.68 | 10.72 | 14.12 | -1.30 | 0.235 |
| DATA_ONLY | 46 | 3 | 11.54 | 14.14 | 1.23 | 11.60 | 14.99 | -0.21 | 0.255 |
| HYBRID_30 | 46 | 3 | 11.07 | 13.70 | 1.55 | 10.95 | 14.34 | -0.98 | 0.241 |
| market at snapshot | 46 | 3 | 10.90 | 13.59 | 1.68 | 10.72 | 14.12 | -1.30 | - |
| market at close | 46 | 3 | 10.92 | 13.58 | 1.71 | 10.84 | 14.27 | -1.25 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 46 | margin | 0.643 | 0.413 | [-0.167, 1.452] | 0.413 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 46 | total | 0.886 | 0.369 | [0.163, 1.609] | 0.413 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 46 | margin | 0.170 | 0.124 | [-0.074, 0.414] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 46 | total | 0.232 | 0.114 | [0.008, 0.455] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 46 | margin | -0.473 | 0.290 | [-1.042, 0.096] | 0.587 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 46 | total | -0.654 | 0.258 | [-1.159, -0.149] | 0.587 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 46 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 46 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 46 | margin | 0.643 | 0.413 | [-0.167, 1.452] | 0.413 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 46 | total | 0.886 | 0.369 | [0.163, 1.609] | 0.413 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 46 | margin | 0.170 | 0.124 | [-0.074, 0.414] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 46 | total | 0.232 | 0.114 | [0.008, 0.455] | 0.457 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 46 | margin | -0.022 | 0.054 | [-0.127, 0.084] | 0.109 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 46 | total | -0.120 | 0.070 | [-0.256, 0.017] | 0.217 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 46 | margin | 0.621 | 0.414 | [-0.190, 1.432] | 0.391 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 46 | total | 0.766 | 0.380 | [0.022, 1.510] | 0.413 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 46 | margin | 0.148 | 0.134 | [-0.114, 0.410] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 46 | total | 0.112 | 0.135 | [-0.153, 0.378] | 0.478 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 46 | 6 | 4 | 36 | 0 | 0.600 | 0.413 | 2.37 |
| DATA_ONLY | total | 46 | 8 | 6 | 32 | 0 | 0.571 | 0.413 | 2.04 |
| HYBRID_30 | margin | 46 | 6 | 4 | 36 | 0 | 0.600 | 0.457 | 0.71 |
| HYBRID_30 | total | 46 | 8 | 6 | 32 | 0 | 0.571 | 0.457 | 0.61 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 12 | 8.93 | 8.50 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.04 | 9.62 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.67 | 21.83 | - |
| DATA_ONLY | total | <=1 | 16 | 13.14 | 13.31 | 0.667 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 7 | 5.32 | 5.14 | 0.800 |
| DATA_ONLY | total | 3-5 | 10 | 12.91 | 9.60 | 0.500 |
| DATA_ONLY | total | >5 | 2 | 19.32 | 12.75 | - |
| HYBRID_30 | margin | <=1 | 35 | 9.93 | 9.83 | 0.667 |
| HYBRID_30 | margin | 1-2 | 11 | 14.71 | 14.32 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 37 | 10.95 | 10.96 | 0.583 |
| HYBRID_30 | total | 1-2 | 8 | 9.68 | 8.62 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 46}; DATA_ONLY quality states: {'OK': 46}; close centre status: {'OK': 46}.

## Contract pricing — latest_pregame (3665 contracts, 47 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3665 | 0.1669 | 0.5011 | 0.414 | 0.422 | 3665 | 0.1669 | 0.1671 | 0.1696 |
| DATA_ONLY | 3665 | 0.1788 | 0.5335 | 0.422 | 0.422 | 3665 | 0.1788 | 0.1671 | 0.1696 |
| HYBRID_30 | 3665 | 0.1700 | 0.5091 | 0.414 | 0.422 | 3665 | 0.1700 | 0.1671 | 0.1696 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3665 | 47 | 0.01188 | [0.00238, 0.02184] | 0.01188 | [0.00238, 0.02184] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3665 | 47 | 0.00310 | [0.00035, 0.00601] | 0.00310 | [0.00035, 0.00601] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3665 | 47 | -0.00879 | [-0.01642, -0.00127] | -0.00879 | [-0.01642, -0.00127] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3665 | 47 | - | - | -0.00013 | [-0.00112, 0.00079] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3600 | 47 | - | - | -0.00044 | [-0.00170, 0.00074] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3665 | 47 | - | - | 0.01175 | [0.00175, 0.02212] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3600 | 47 | - | - | 0.01169 | [0.00141, 0.02227] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3665 | 47 | - | - | 0.00297 | [0.00004, 0.00615] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3600 | 47 | - | - | 0.00274 | [-0.00040, 0.00608] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 188, 'GAME_WINNER': 94, 'SPREAD': 1208, 'TEAM_TOTAL': 1282, 'TOTAL': 893}; settlement: {'SETTLED': 3665}; close: {'OK': 3600, 'OK_STALE': 65}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 570 / 0.055 / 0.051 | 546 / 0.054 / 0.071 | 560 / 0.053 / 0.061 |
| 0.10-0.20 | 590 / 0.145 / 0.190 | 573 / 0.145 / 0.201 | 591 / 0.146 / 0.190 |
| 0.20-0.30 | 426 / 0.248 / 0.279 | 439 / 0.249 / 0.296 | 423 / 0.248 / 0.274 |
| 0.30-0.40 | 368 / 0.351 / 0.359 | 373 / 0.349 / 0.373 | 374 / 0.347 / 0.366 |
| 0.40-0.50 | 380 / 0.450 / 0.468 | 358 / 0.448 / 0.464 | 413 / 0.449 / 0.494 |
| 0.50-0.60 | 350 / 0.547 / 0.551 | 321 / 0.551 / 0.508 | 328 / 0.549 / 0.534 |
| 0.60-0.70 | 240 / 0.650 / 0.604 | 291 / 0.648 / 0.546 | 241 / 0.648 / 0.581 |
| 0.70-0.80 | 188 / 0.750 / 0.734 | 196 / 0.750 / 0.689 | 195 / 0.751 / 0.697 |
| 0.80-0.90 | 193 / 0.848 / 0.850 | 195 / 0.851 / 0.810 | 189 / 0.852 / 0.868 |
| 0.90-1.00 | 360 / 0.954 / 0.931 | 373 / 0.957 / 0.914 | 351 / 0.956 / 0.932 |

## Contract pricing — T-24h (1716 contracts, 22 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1716 | 0.1716 | 0.5136 | 0.413 | 0.392 | 1716 | 0.1716 | 0.1710 | 0.1721 |
| DATA_ONLY | 1716 | 0.1772 | 0.5304 | 0.417 | 0.392 | 1716 | 0.1772 | 0.1710 | 0.1721 |
| HYBRID_30 | 1716 | 0.1718 | 0.5134 | 0.412 | 0.392 | 1716 | 0.1718 | 0.1710 | 0.1721 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1716 | 22 | 0.00558 | [-0.01041, 0.02090] | 0.00558 | [-0.01041, 0.02090] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1716 | 22 | 0.00019 | [-0.00456, 0.00505] | 0.00019 | [-0.00456, 0.00505] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1716 | 22 | -0.00539 | [-0.01674, 0.00702] | -0.00539 | [-0.01674, 0.00702] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1716 | 22 | - | - | 0.00060 | [-0.00067, 0.00195] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1692 | 22 | - | - | 0.00148 | [-0.00066, 0.00388] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1716 | 22 | - | - | 0.00619 | [-0.00959, 0.02138] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1692 | 22 | - | - | 0.00724 | [-0.00805, 0.02255] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1716 | 22 | - | - | 0.00080 | [-0.00446, 0.00591] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1692 | 22 | - | - | 0.00176 | [-0.00300, 0.00650] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 88, 'GAME_WINNER': 44, 'SPREAD': 568, 'TEAM_TOTAL': 598, 'TOTAL': 418}; settlement: {'SETTLED': 1716}; close: {'OK': 1692, 'OK_STALE': 24}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 274 / 0.055 / 0.026 | 266 / 0.053 / 0.045 | 265 / 0.053 / 0.023 |
| 0.10-0.20 | 268 / 0.146 / 0.168 | 270 / 0.146 / 0.178 | 275 / 0.145 / 0.175 |
| 0.20-0.30 | 203 / 0.248 / 0.305 | 206 / 0.250 / 0.330 | 204 / 0.249 / 0.294 |
| 0.30-0.40 | 167 / 0.349 / 0.341 | 177 / 0.349 / 0.339 | 165 / 0.347 / 0.364 |
| 0.40-0.50 | 184 / 0.449 / 0.435 | 164 / 0.448 / 0.402 | 203 / 0.449 / 0.458 |
| 0.50-0.60 | 156 / 0.545 / 0.500 | 148 / 0.550 / 0.432 | 145 / 0.549 / 0.448 |
| 0.60-0.70 | 116 / 0.647 / 0.543 | 139 / 0.648 / 0.540 | 112 / 0.645 / 0.509 |
| 0.70-0.80 | 94 / 0.748 / 0.702 | 84 / 0.748 / 0.702 | 96 / 0.747 / 0.698 |
| 0.80-0.90 | 88 / 0.850 / 0.773 | 94 / 0.848 / 0.787 | 88 / 0.854 / 0.807 |
| 0.90-1.00 | 166 / 0.954 / 0.886 | 168 / 0.956 / 0.875 | 163 / 0.955 / 0.896 |

## Contract pricing — T-6h (2188 contracts, 28 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2188 | 0.1622 | 0.4868 | 0.413 | 0.421 | 2188 | 0.1622 | 0.1626 | 0.1656 |
| DATA_ONLY | 2188 | 0.1685 | 0.5029 | 0.422 | 0.421 | 2188 | 0.1685 | 0.1626 | 0.1656 |
| HYBRID_30 | 2188 | 0.1631 | 0.4895 | 0.413 | 0.421 | 2188 | 0.1631 | 0.1626 | 0.1656 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2188 | 28 | 0.00628 | [-0.00445, 0.01841] | 0.00628 | [-0.00445, 0.01841] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2188 | 28 | 0.00090 | [-0.00214, 0.00408] | 0.00090 | [-0.00214, 0.00408] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2188 | 28 | -0.00538 | [-0.01550, 0.00322] | -0.00538 | [-0.01550, 0.00322] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2188 | 28 | - | - | -0.00038 | [-0.00156, 0.00089] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2134 | 28 | - | - | -0.00021 | [-0.00189, 0.00153] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2188 | 28 | - | - | 0.00590 | [-0.00543, 0.01823] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2134 | 28 | - | - | 0.00631 | [-0.00513, 0.01913] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2188 | 28 | - | - | 0.00052 | [-0.00271, 0.00406] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2134 | 28 | - | - | 0.00077 | [-0.00258, 0.00449] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 112, 'GAME_WINNER': 56, 'SPREAD': 721, 'TEAM_TOTAL': 767, 'TOTAL': 532}; settlement: {'SETTLED': 2188}; close: {'OK': 2134, 'OK_STALE': 54}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 349 / 0.056 / 0.063 | 339 / 0.054 / 0.053 | 343 / 0.054 / 0.058 |
| 0.10-0.20 | 344 / 0.144 / 0.177 | 337 / 0.147 / 0.181 | 343 / 0.145 / 0.178 |
| 0.20-0.30 | 257 / 0.249 / 0.261 | 254 / 0.250 / 0.280 | 262 / 0.250 / 0.260 |
| 0.30-0.40 | 222 / 0.351 / 0.360 | 221 / 0.349 / 0.394 | 216 / 0.349 / 0.394 |
| 0.40-0.50 | 226 / 0.450 / 0.478 | 210 / 0.446 / 0.448 | 250 / 0.449 / 0.468 |
| 0.50-0.60 | 208 / 0.545 / 0.519 | 189 / 0.548 / 0.519 | 193 / 0.549 / 0.518 |
| 0.60-0.70 | 143 / 0.652 / 0.615 | 177 / 0.647 / 0.565 | 139 / 0.648 / 0.597 |
| 0.70-0.80 | 109 / 0.754 / 0.761 | 121 / 0.751 / 0.711 | 116 / 0.748 / 0.741 |
| 0.80-0.90 | 119 / 0.851 / 0.882 | 118 / 0.850 / 0.831 | 117 / 0.851 / 0.880 |
| 0.90-1.00 | 211 / 0.956 / 0.948 | 222 / 0.956 / 0.941 | 209 / 0.956 / 0.952 |

## Contract pricing — T-90m (2730 contracts, 35 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2730 | 0.1615 | 0.4883 | 0.416 | 0.398 | 2730 | 0.1615 | 0.1606 | 0.1633 |
| DATA_ONLY | 2730 | 0.1673 | 0.5038 | 0.421 | 0.398 | 2730 | 0.1673 | 0.1606 | 0.1633 |
| HYBRID_30 | 2730 | 0.1636 | 0.4914 | 0.413 | 0.398 | 2730 | 0.1636 | 0.1606 | 0.1633 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2730 | 35 | 0.00581 | [-0.00587, 0.01757] | 0.00581 | [-0.00587, 0.01757] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2730 | 35 | 0.00210 | [-0.00175, 0.00580] | 0.00210 | [-0.00175, 0.00580] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2730 | 35 | -0.00371 | [-0.01247, 0.00520] | -0.00371 | [-0.01247, 0.00520] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2730 | 35 | - | - | 0.00084 | [-0.00061, 0.00225] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2673 | 35 | - | - | 0.00091 | [-0.00087, 0.00271] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2730 | 35 | - | - | 0.00666 | [-0.00547, 0.01908] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2673 | 35 | - | - | 0.00689 | [-0.00546, 0.01944] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2730 | 35 | - | - | 0.00295 | [-0.00109, 0.00673] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2673 | 35 | - | - | 0.00310 | [-0.00120, 0.00710] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 140, 'GAME_WINNER': 70, 'SPREAD': 901, 'TEAM_TOTAL': 954, 'TOTAL': 665}; settlement: {'SETTLED': 2730}; close: {'OK': 2673, 'OK_STALE': 57}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 425 / 0.055 / 0.033 | 416 / 0.054 / 0.043 | 427 / 0.054 / 0.037 |
| 0.10-0.20 | 432 / 0.144 / 0.162 | 421 / 0.145 / 0.166 | 430 / 0.145 / 0.163 |
| 0.20-0.30 | 317 / 0.247 / 0.262 | 328 / 0.250 / 0.271 | 326 / 0.249 / 0.267 |
| 0.30-0.40 | 274 / 0.349 / 0.314 | 276 / 0.350 / 0.326 | 266 / 0.349 / 0.350 |
| 0.40-0.50 | 275 / 0.450 / 0.425 | 266 / 0.447 / 0.417 | 311 / 0.448 / 0.447 |
| 0.50-0.60 | 268 / 0.546 / 0.534 | 236 / 0.549 / 0.496 | 237 / 0.549 / 0.489 |
| 0.60-0.70 | 185 / 0.651 / 0.557 | 219 / 0.647 / 0.553 | 182 / 0.648 / 0.549 |
| 0.70-0.80 | 138 / 0.750 / 0.725 | 150 / 0.748 / 0.687 | 146 / 0.749 / 0.692 |
| 0.80-0.90 | 151 / 0.849 / 0.841 | 146 / 0.851 / 0.829 | 143 / 0.851 / 0.853 |
| 0.90-1.00 | 265 / 0.956 / 0.921 | 272 / 0.956 / 0.908 | 262 / 0.956 / 0.927 |

## Contract pricing — T-30m (3588 contracts, 46 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3588 | 0.1676 | 0.5028 | 0.413 | 0.416 | 3588 | 0.1676 | 0.1677 | 0.1703 |
| DATA_ONLY | 3588 | 0.1784 | 0.5325 | 0.422 | 0.416 | 3588 | 0.1784 | 0.1677 | 0.1703 |
| HYBRID_30 | 3588 | 0.1702 | 0.5098 | 0.413 | 0.416 | 3588 | 0.1702 | 0.1677 | 0.1703 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3588 | 46 | 0.01081 | [0.00107, 0.02014] | 0.01081 | [0.00107, 0.02014] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3588 | 46 | 0.00264 | [0.00004, 0.00538] | 0.00264 | [0.00004, 0.00538] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3588 | 46 | -0.00818 | [-0.01533, -0.00036] | -0.00818 | [-0.01533, -0.00036] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3588 | 46 | - | - | -0.00014 | [-0.00125, 0.00076] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3523 | 46 | - | - | -0.00046 | [-0.00179, 0.00066] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3588 | 46 | - | - | 0.01067 | [0.00078, 0.02039] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3523 | 46 | - | - | 0.01059 | [0.00048, 0.02056] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3588 | 46 | - | - | 0.00249 | [-0.00035, 0.00535] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3523 | 46 | - | - | 0.00226 | [-0.00070, 0.00538] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 184, 'GAME_WINNER': 92, 'SPREAD': 1183, 'TEAM_TOTAL': 1255, 'TOTAL': 874}; settlement: {'SETTLED': 3588}; close: {'OK': 3523, 'OK_STALE': 65}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 563 / 0.055 / 0.052 | 536 / 0.054 / 0.069 | 552 / 0.053 / 0.062 |
| 0.10-0.20 | 577 / 0.145 / 0.187 | 560 / 0.145 / 0.198 | 577 / 0.146 / 0.187 |
| 0.20-0.30 | 417 / 0.248 / 0.281 | 429 / 0.249 / 0.291 | 415 / 0.249 / 0.270 |
| 0.30-0.40 | 361 / 0.351 / 0.355 | 366 / 0.349 / 0.366 | 368 / 0.348 / 0.364 |
| 0.40-0.50 | 378 / 0.450 / 0.463 | 347 / 0.448 / 0.450 | 403 / 0.449 / 0.481 |
| 0.50-0.60 | 339 / 0.546 / 0.537 | 316 / 0.550 / 0.500 | 322 / 0.549 / 0.525 |
| 0.60-0.70 | 232 / 0.650 / 0.591 | 287 / 0.648 / 0.540 | 235 / 0.649 / 0.570 |
| 0.70-0.80 | 186 / 0.750 / 0.731 | 192 / 0.750 / 0.682 | 193 / 0.751 / 0.694 |
| 0.80-0.90 | 187 / 0.848 / 0.845 | 191 / 0.851 / 0.806 | 183 / 0.853 / 0.863 |
| 0.90-1.00 | 348 / 0.954 / 0.928 | 364 / 0.957 / 0.912 | 340 / 0.956 / 0.929 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 22 | 6 | 2 | 2 | 12 | 0 | 0.500 [0.150, 0.850] | 0.375 | 0.375 | 0.06 |
| T-24h | DATA_ONLY | total | 22 | 4 | 7 | 1 | 10 | 0 | 0.875 [0.529, 0.978] | 0.500 | 0.444 | 0.44 |
| T-24h | HYBRID_30 (derived) | margin | 22 | 15 | 1 | 1 | 5 | 0 | 0.500 [0.095, 0.905] | 0.286 | 0.286 | 0.07 |
| T-24h | HYBRID_30 (derived) | total | 22 | 18 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.250 | 0.250 | 0.25 |
| T-6h | DATA_ONLY | margin | 28 | 5 | 6 | 2 | 15 | 0 | 0.750 [0.409, 0.929] | 0.391 | 0.435 | 0.11 |
| T-6h | DATA_ONLY | total | 28 | 9 | 5 | 4 | 10 | 0 | 0.556 [0.267, 0.811] | 0.421 | 0.421 | -0.03 |
| T-6h | HYBRID_30 (derived) | margin | 28 | 20 | 1 | 1 | 6 | 0 | 0.500 [0.095, 0.905] | 0.375 | 0.375 | 0.00 |
| T-6h | HYBRID_30 (derived) | total | 28 | 23 | 2 | 0 | 3 | 0 | 1.000 [0.342, 1.000] | 0.400 | 0.200 | 0.40 |
| T-90m | DATA_ONLY | margin | 35 | 6 | 5 | 2 | 22 | 0 | 0.714 [0.359, 0.918] | 0.414 | 0.414 | 0.02 |
| T-90m | DATA_ONLY | total | 35 | 11 | 4 | 5 | 15 | 0 | 0.444 [0.189, 0.733] | 0.375 | 0.375 | -0.08 |
| T-90m | HYBRID_30 (derived) | margin | 35 | 25 | 0 | 1 | 9 | 0 | 0.000 [0.000, 0.793] | 0.400 | 0.400 | -0.10 |
| T-90m | HYBRID_30 (derived) | total | 35 | 28 | 0 | 3 | 4 | 0 | 0.000 [0.000, 0.561] | 0.286 | 0.286 | -0.36 |
| T-30m | DATA_ONLY | margin | 46 | 9 | 5 | 2 | 30 | 0 | 0.714 [0.359, 0.918] | 0.351 | 0.351 | 0.05 |
| T-30m | DATA_ONLY | total | 46 | 16 | 6 | 5 | 19 | 0 | 0.545 [0.280, 0.787] | 0.333 | 0.333 | -0.05 |
| T-30m | HYBRID_30 (derived) | margin | 46 | 35 | 0 | 1 | 10 | 0 | 0.000 [0.000, 0.793] | 0.364 | 0.364 | -0.09 |
| T-30m | HYBRID_30 (derived) | total | 46 | 37 | 1 | 1 | 7 | 0 | 0.500 [0.095, 0.905] | 0.111 | 0.111 | 0.00 |
| latest_pregame | DATA_ONLY | margin | 47 | 9 | 5 | 2 | 31 | 0 | 0.714 [0.359, 0.918] | 0.342 | 0.342 | 0.05 |
| latest_pregame | DATA_ONLY | total | 47 | 16 | 6 | 5 | 20 | 0 | 0.545 [0.280, 0.787] | 0.323 | 0.323 | -0.05 |
| latest_pregame | HYBRID_30 (derived) | margin | 47 | 36 | 0 | 1 | 10 | 0 | 0.000 [0.000, 0.793] | 0.364 | 0.364 | -0.09 |
| latest_pregame | HYBRID_30 (derived) | total | 47 | 37 | 1 | 1 | 8 | 0 | 0.500 [0.095, 0.905] | 0.100 | 0.100 | 0.00 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 9 | 1 | 2 | 6 | 0 | 0.333 |
| margin | 1-2 | 13 | 3 | 0 | 10 | 0 | 1.000 |
| margin | 2-3 | 12 | 2 | 1 | 9 | 0 | 0.667 |
| margin | 3-5 | 10 | 0 | 1 | 9 | 0 | 0.000 |
| margin | >5 | 3 | 0 | 0 | 3 | 0 | - |
| total | <=1 | 16 | 2 | 1 | 13 | 0 | 0.667 |
| total | 1-2 | 11 | 1 | 3 | 7 | 0 | 0.250 |
| total | 2-3 | 7 | 4 | 1 | 2 | 0 | 0.800 |
| total | 3-5 | 10 | 1 | 1 | 8 | 0 | 0.500 |
| total | >5 | 3 | 0 | 0 | 3 | 0 | - |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 16 | 3 | 0.667 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 16 | 4 | 0.500 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

2980 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_01_CHI_CAR | Jonathon Brooks | receiving_yards | 1.0 | 0–11 | 48 | 64.75 | 0.99 | 1.0 | 2 | 0.98 | 24.00 | EXPECTED_ACTIVE | True | 0.427 | EFFICIENCY_MISS |
| 2026_03_CAR_CLE | Raheim Sanders | receiving_yards | 1.0 | 0–11 | 34 | 45.87 | 0.99 | 1.2 | 5 | 0.87 | 6.80 | EXPECTED_ACTIVE | True | 0.123 | EFFICIENCY_MISS |
| 2026_03_NYJ_DET | Kenyon Sadiq | receiving_yards | 3.3 | 0–35 | 105 | 35.41 | 0.99 | 1.1 | 8 | 3.05 | 13.12 | EXPECTED_ACTIVE | True | 0.603 | OPPORTUNITY_MISS |
| 2026_02_IND_KC | Emmett Johnson | receiving_yards | 1.0 | 0–11 | 20 | 26.98 | 0.99 | 0.9 | 2 | 1.08 | 10.00 | EXPECTED_ACTIVE | True | 0.273 | EFFICIENCY_MISS |
| 2026_03_ARI_SF | Jeremiyah Love | receiving_yards | 1.0 | 0–11 | 19 | 25.63 | 0.98 | 0.9 | 5 | 1.07 | 3.80 | EXPECTED_ACTIVE | True | 0.472 | TEAM_VOLUME_MISS |
| 2026_02_SEA_ARI | Jeremiyah Love | receiving_yards | 1.0 | 0–11 | 16 | 21.58 | 0.97 | 1.0 | 3 | 1.05 | 5.33 | EXPECTED_ACTIVE | True | 0.506 | EFFICIENCY_MISS |
| 2026_02_SEA_ARI | Jadarian Price | receiving_yards | 1.0 | 0–11 | 8 | 10.79 | 0.89 | 0.9 | 2 | 1.08 | 4.00 | EXPECTED_ACTIVE | True | -0.293 | EFFICIENCY_MISS |
| 2026_01_CLE_JAX | Bhayshul Tuten | receiving_yards | 2.9 | 0–31 | 22 | 9.89 | 0.89 | 1.3 | 1 | 2.33 | 22.00 | EXPECTED_ACTIVE | True | 0.283 | EFFICIENCY_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | receiving_yards | 2.7 | 0–29 | 21 | 9.44 | 0.89 | 1.1 | 3 | 2.49 | 7.00 | EXPECTED_ACTIVE | True | 0.361 | EFFICIENCY_MISS |
| 2026_01_WAS_PHI | Jacory Croskey-Merritt | receiving_yards | 1.0 | 0–11 | -7 | -9.44 | 0.05 | 1.2 | 1 | 0.83 | -7.00 | EXPECTED_ACTIVE | True | -0.183 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.0 | 3 | 1.04 | 2.33 | EXPECTED_ACTIVE | True | -0.193 | TEAM_VOLUME_MISS |
| 2026_03_NYJ_DET | Kenyon Sadiq | receptions | 0.7 | 0–5 | 7 | 9.44 | 0.97 | 1.1 | 8 | 0.68 | 0.88 | EXPECTED_ACTIVE | True | 0.612 | OPPORTUNITY_MISS |
| 2026_03_SEA_WAS | Jadarian Price | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 0.9 | 3 | 1.09 | 2.33 | EXPECTED_ACTIVE | True | -0.307 | TEAM_VOLUME_MISS |
| 2026_02_GB_NYJ | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 6 | 8.09 | 0.85 | 0.9 | 2 | 1.05 | 3.00 | EXPECTED_ACTIVE | True | -0.303 | EFFICIENCY_MISS |
| 2026_02_MIA_SF | Kyle Juszczyk | touchdowns | 0.0 | -–- | 1 | 8.00 | - | 0.0 | 2 | - | - | EXPECTED_ACTIVE | True | 0.068 | UNEXPLAINED_VARIANCE |
| 2026_03_NE_JAX | Bhayshul Tuten | receiving_yards | 2.4 | 0–25 | 17 | 7.64 | 0.88 | 1.2 | 2 | 1.95 | 8.50 | EXPECTED_ACTIVE | True | 0.382 | EFFICIENCY_MISS |
| 2026_02_CAR_ATL | Jonathon Brooks | receiving_yards | 1.0 | 0–11 | -5 | -6.75 | 0.05 | 1.0 | 1 | 1.00 | -5.00 | EXPECTED_ACTIVE | True | -0.233 | EFFICIENCY_MISS |
| 2026_03_ARI_SF | Jeremiyah Love | receptions | 0.7 | 0–5 | 5 | 6.75 | 0.95 | 0.9 | 5 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.563 | TEAM_VOLUME_MISS |
| 2026_02_GB_NYJ | Chris Brooks | receiving_yards | 3.1 | 0–32 | 15 | 6.74 | 0.83 | 1.3 | 2 | 2.41 | 7.50 | EXPECTED_ACTIVE | True | 0.210 | EFFICIENCY_MISS |
| 2026_03_LA_DEN | Kyren Williams | receiving_yards | 11.1 | 0–48 | 70 | 6.30 | 0.98 | 1.7 | 7 | 6.37 | 10.00 | EXPECTED_ACTIVE | True | 0.169 | TEAM_VOLUME_MISS |
| 2026_03_ARI_SF | Jeremiyah Love | rushing_yards | 13.8 | 0–55 | 90 | 5.96 | 0.99 | 3.9 | 21 | 3.53 | 4.29 | EXPECTED_ACTIVE | True | 0.568 | OPPORTUNITY_MISS |
| 2026_02_NYG_LA | Blake Corum | receiving_yards | 2.9 | 0–30 | 13 | 5.85 | 0.82 | 1.2 | 1 | 2.33 | 13.00 | EXPECTED_ACTIVE | True | -0.050 | EFFICIENCY_MISS |
| 2026_03_NYJ_DET | Sione Vaki | rushing_yards | 8.7 | 0–36 | 26 | 5.85 | 0.88 | 3.1 | 6 | 2.81 | 4.33 | EXPECTED_ACTIVE | True | 0.306 | OPPORTUNITY_MISS |
| 2026_02_GB_NYJ | Kenyon Sadiq | receiving_yards | 3.5 | 0–37 | 17 | 5.73 | 0.83 | 1.1 | 3 | 3.16 | 5.67 | EXPECTED_ACTIVE | True | 0.473 | TEAM_VOLUME_MISS |
| 2026_03_CAR_CLE | Raheim Sanders | receptions | 0.8 | 0–5 | 4 | 5.40 | 0.90 | 1.2 | 5 | 0.72 | 0.80 | EXPECTED_ACTIVE | True | 0.208 | OPPORTUNITY_MISS |
| 2026_02_GB_NYJ | Breece Hall | receiving_yards | 12.2 | 0–53 | 63 | 5.31 | 0.96 | 1.8 | 5 | 6.88 | 12.60 | EXPECTED_ACTIVE | True | 0.314 | TEAM_VOLUME_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | touchdowns | 0.0 | -–- | 1 | 4.99 | - | 2.7 | 4 | - | - | EXPECTED_ACTIVE | True | 0.047 | UNEXPLAINED_VARIANCE |
| 2026_03_CAR_CLE | Deshaun Watson | carries | 2.4 | 0–18 | 11 | 4.95 | 0.86 | 2.4 | 11 | - | - | EXPECTED_ACTIVE | True | 0.577 | TEAM_VOLUME_MISS |
| 2026_01_CHI_CAR | Kalif Raymond | receptions | 1.5 | 0–5 | 8 | 4.72 | 0.99 | 2.1 | 9 | 0.70 | 0.89 | EXPECTED_ACTIVE | True | 0.070 | OPPORTUNITY_MISS |
| 2026_01_DAL_NYG | Isaiah Likely | receptions | 1.4 | 0–5 | 8 | 4.72 | 0.99 | 1.9 | 8 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.381 | OPPORTUNITY_MISS |
| 2026_03_HOU_IND | Tyler Warren | receptions | 2.2 | 0–6 | 9 | 4.72 | 0.99 | 3.4 | 10 | 0.66 | 0.90 | EXPECTED_ACTIVE | True | 0.439 | OPPORTUNITY_MISS |
| 2026_03_NYJ_DET | Kenyon Sadiq | touchdowns | 0.0 | -–- | 1 | 4.69 | - | 2.7 | 8 | - | - | EXPECTED_ACTIVE | True | 0.142 | OPPORTUNITY_MISS |
| 2026_01_BUF_HOU | Dalton Kincaid | receiving_yards | 26.6 | 0–74 | 130 | 4.68 | 0.99 | 2.3 | 6 | 11.60 | 21.67 | EXPECTED_ACTIVE | True | 0.238 | OPPORTUNITY_MISS |
| 2026_02_NYG_LA | Davante Adams | receiving_yards | 48.7 | 4–113 | 195 | 4.63 | 0.99 | 5.5 | 10 | 8.91 | 19.50 | EXPECTED_ACTIVE | True | 0.196 | EFFICIENCY_MISS |
| 2026_02_CIN_HOU | Foster Moreau | receiving_yards | 7.7 | 0–34 | 34 | 4.59 | 0.95 | 1.4 | 2 | 5.47 | 17.00 | EXPECTED_ACTIVE | True | 0.137 | EFFICIENCY_MISS |
| 2026_02_CIN_HOU | Dalton Schultz | receptions | 2.5 | 0–6 | 12 | 4.50 | 0.99 | 3.2 | 14 | 0.78 | 0.86 | EXPECTED_ACTIVE | True | 0.373 | TEAM_VOLUME_MISS |
| 2026_03_ARI_SF | Tyler Allgeier | receiving_yards | 2.5 | 0–27 | 10 | 4.50 | 0.81 | 1.3 | 4 | 1.98 | 2.50 | EXPECTED_ACTIVE | True | -0.169 | TEAM_VOLUME_MISS |
| 2026_02_CLE_TB | Denzel Boston | receiving_yards | 19.3 | 0–65 | 95 | 4.46 | 0.98 | 1.9 | 7 | 10.28 | 13.57 | EXPECTED_ACTIVE | True | 0.318 | TEAM_VOLUME_MISS |
| 2026_03_MIN_TB | Myles Price | touchdowns | 0.0 | -–- | 1 | 4.43 | - | 2.2 | 0 | - | - | EXPECTED_ACTIVE | True | 0.004 | OPPORTUNITY_MISS |
| 2026_03_NYJ_DET | Jeremy Ruckert | receiving_yards | 8.9 | 0–39 | 39 | 4.38 | 0.95 | 1.6 | 5 | 5.54 | 7.80 | EXPECTED_ACTIVE | True | 0.124 | OPPORTUNITY_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 525, 'OPPORTUNITY_MISS': 980, 'TEAM_VOLUME_MISS': 174, 'UNEXPLAINED_VARIANCE': 92, 'NO_LARGE_MISS': 1130, 'INSUFFICIENT_DATA': 40, 'AVAILABILITY_MISS': 39}.
Missing usage (no snap table or stats row): 79.

## Decision funnel (BET / WATCH / PASS accounting of the existing gates; no authority)

95 snapshot(s). A contract's terminal state is where it left the existing gate sequence when the model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).

### Newest snapshot 20261001T012500Z (54862 markets)

| stage | markets |
|---|---|
| discovered | 54862 |
| mapped | 46355 |
| supported | 4228 |
| priced | 4228 |
| raw_disagreement | 3256 |
| tradable_book | 3137 |
| data_quality | 3090 |
| executable_price | 2135 |
| liquidity | 284 |

Terminal states: {'PASS': 53625, 'WATCH': 953, 'BET': 284}

| family | BET | WATCH | PASS |
|---|---|---|---|
| AWARD | 0 | 0 | 873 |
| BOTH_TEAMS_SCORE | 0 | 0 | 196 |
| BOTH_TEAMS_SCORE_N | 0 | 1 | 195 |
| COACH_EVENT | 0 | 0 | 64 |
| CONFERENCE_WINNER | 0 | 0 | 32 |
| DIVISION_WINNER | 0 | 0 | 32 |
| DRAFT | 0 | 0 | 40 |
| FIRST_TD_SCORER | 0 | 0 | 1588 |
| FIRST_TD_TEAM | 0 | 0 | 1449 |
| GAME_EVENT | 0 | 0 | 214 |
| GAME_PLAYER_LEADER | 0 | 0 | 567 |
| GAME_STAT | 0 | 0 | 5 |
| GAME_WINNER | 2 | 22 | 134 |
| HALF_FULL_RESULT | 0 | 0 | 576 |
| MAKE_PLAYOFFS | 0 | 0 | 33 |
| NFL_BUSINESS_EVENT | 0 | 0 | 5 |
| NOT_NFL_OR_UNKNOWN | 0 | 0 | 2 |
| PERIOD_WINNER | 0 | 0 | 1152 |
| PLAYER_AVAILABILITY | 0 | 0 | 23 |
| PLAYER_ROLE_EVENT | 0 | 0 | 177 |
| PLAYER_STAT | 264 | 385 | 21174 |
| RACE_TO_N | 0 | 0 | 780 |
| SEASON_DIVISION_ORDER | 0 | 0 | 192 |
| SEASON_DIVISION_STAT | 0 | 0 | 80 |
| SEASON_FANTASY | 0 | 0 | 1159 |
| SEASON_LEADER | 0 | 0 | 604 |
| SEASON_MATCHUP | 0 | 0 | 496 |
| SEASON_PLAYER_SPECIAL | 0 | 0 | 306 |
| SEASON_PLAYER_STAT | 0 | 0 | 1129 |
| SEASON_SEED | 0 | 0 | 224 |
| SEASON_SPECIAL | 0 | 0 | 66 |
| SEASON_TEAM_EVENT | 0 | 0 | 390 |
| SEASON_TEAM_H2H | 0 | 0 | 22 |
| SEASON_TEAM_LEADER | 0 | 0 | 96 |
| SEASON_WINS | 0 | 0 | 547 |
| SPREAD | 2 | 226 | 6524 |
| SUPER_BOWL_EVENT | 0 | 0 | 263 |
| SUPER_BOWL_WINNER | 0 | 0 | 32 |
| TEAM_STAT | 0 | 0 | 1266 |
| TEAM_TOTAL | 12 | 155 | 3004 |
| TEAM_WINS_BY_WEEK | 0 | 0 | 728 |
| TOTAL | 4 | 164 | 5415 |
| TOTAL_TD | 0 | 0 | 214 |
| TRANSACTION_EVENT | 0 | 0 | 314 |
| UNKNOWN_NEEDS_CLASSIFICATION | 0 | 0 | 386 |
| WEEK_EVENT | 0 | 0 | 32 |
| WEEK_LEADER | 0 | 0 | 482 |
| WIN_MARGIN_BUCKET | 0 | 0 | 343 |

| rejection reason | n |
|---|---|
| POST_KICKOFF_EXCLUDED | 34745 |
| unmapped | 8507 |
| UNSUPPORTED_MODEL | 4548 |
| UNSUPPORTED_RULES | 2823 |
| no order book observed for this ticker (books are captured i | 1850 |
| no positive disagreement against either executable ask | 972 |
| book not tradable for ranking | 119 |
| ask 0.99 above the zero-net-EV ceiling 0.98 | 101 |
| ask 0.97 above the zero-net-EV ceiling 0.96 | 51 |
| ask 0.98 above the zero-net-EV ceiling 0.97 | 45 |
| availability DOUBTFUL unresolved inside T-90m | 32 |
| ask 0.07 above the zero-net-EV ceiling 0.06 | 18 |
| ask 0.90 above the zero-net-EV ceiling 0.89 | 16 |
| ask 0.88 above the zero-net-EV ceiling 0.87 | 15 |
| ask 0.96 above the zero-net-EV ceiling 0.95 | 14 |

WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee schedule (`watch_ceiling`). Not replayed: ['portfolio_risk_policy (needs a stake and bankroll)', "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own confirmation is the STALE_DATA support state)"].

Across all 95 snapshots (repeated markets counted per snapshot): {'PASS': 3223208, 'WATCH': 67995, 'BET': 57046}.

