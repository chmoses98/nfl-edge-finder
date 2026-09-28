# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 46 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 2428 | 46 | 3 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 21 | 21 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 27 | 27 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 34 | 34 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 45 | 45 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 46 | 46 | 3 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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

## Game-centre accuracy — latest_pregame (46 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 46 | 3 | 10.49 | 13.16 | 2.10 | 10.91 | 14.30 | -1.87 | 0.229 |
| DATA_ONLY | 46 | 3 | 11.31 | 13.95 | 1.46 | 11.81 | 15.25 | -1.00 | 0.255 |
| HYBRID_30 | 46 | 3 | 10.71 | 13.34 | 1.91 | 11.15 | 14.54 | -1.61 | 0.235 |
| market at snapshot | 46 | 3 | 10.49 | 13.16 | 2.10 | 10.91 | 14.30 | -1.87 | - |
| market at close | 46 | 3 | 10.51 | 13.15 | 2.12 | 11.03 | 14.44 | -1.82 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 46 | margin | 0.820 | 0.383 | [0.070, 1.571] | 0.391 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 46 | total | 0.901 | 0.373 | [0.170, 1.631] | 0.413 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 46 | margin | 0.223 | 0.116 | [-0.003, 0.450] | 0.435 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 46 | total | 0.236 | 0.115 | [0.010, 0.462] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 46 | margin | -0.597 | 0.269 | [-1.124, -0.070] | 0.609 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 46 | total | -0.665 | 0.260 | [-1.175, -0.155] | 0.587 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 46 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 46 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 46 | margin | 0.820 | 0.383 | [0.070, 1.571] | 0.391 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 46 | total | 0.901 | 0.373 | [0.170, 1.631] | 0.413 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 46 | margin | 0.223 | 0.116 | [-0.003, 0.450] | 0.435 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 46 | total | 0.236 | 0.115 | [0.010, 0.462] | 0.457 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 46 | margin | -0.022 | 0.054 | [-0.127, 0.084] | 0.109 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 46 | total | -0.120 | 0.070 | [-0.256, 0.017] | 0.217 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 46 | margin | 0.799 | 0.384 | [0.046, 1.551] | 0.370 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 46 | total | 0.781 | 0.383 | [0.030, 1.533] | 0.413 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 46 | margin | 0.201 | 0.126 | [-0.045, 0.448] | 0.435 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 46 | total | 0.117 | 0.137 | [-0.151, 0.384] | 0.478 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 46 | 6 | 4 | 36 | 0 | 0.600 | 0.391 | 2.26 |
| DATA_ONLY | total | 46 | 8 | 6 | 32 | 0 | 0.571 | 0.413 | 2.05 |
| HYBRID_30 | margin | 46 | 6 | 4 | 36 | 0 | 0.600 | 0.435 | 0.68 |
| HYBRID_30 | total | 46 | 8 | 6 | 32 | 0 | 0.571 | 0.457 | 0.62 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 13 | 8.72 | 8.19 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.04 | 9.62 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 16 | 13.14 | 13.31 | 0.667 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 7 | 5.32 | 5.14 | 0.800 |
| DATA_ONLY | total | 3-5 | 9 | 12.86 | 9.72 | 0.500 |
| DATA_ONLY | total | >5 | 3 | 20.56 | 14.33 | - |
| HYBRID_30 | margin | <=1 | 36 | 9.79 | 9.68 | 0.667 |
| HYBRID_30 | margin | 1-2 | 10 | 14.02 | 13.40 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 37 | 10.95 | 10.96 | 0.583 |
| HYBRID_30 | total | 1-2 | 8 | 10.83 | 9.75 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 46}; DATA_ONLY quality states: {'OK': 46}; close centre status: {'OK': 46}.

## Game-centre accuracy — T-24h (21 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 21 | 3 | 10.86 | 13.16 | 3.19 | 10.64 | 13.33 | 1.69 | 0.231 |
| DATA_ONLY | 21 | 3 | 11.75 | 14.25 | 1.79 | 10.53 | 13.73 | 1.95 | 0.255 |
| HYBRID_30 | 21 | 3 | 11.13 | 13.43 | 2.77 | 10.55 | 13.40 | 1.77 | 0.236 |
| market at snapshot | 21 | 3 | 10.86 | 13.16 | 3.19 | 10.64 | 13.33 | 1.69 | - |
| market at close | 21 | 3 | 10.93 | 13.23 | 3.36 | 10.38 | 13.25 | 1.48 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 21 | margin | 0.895 | 0.629 | [-0.338, 2.127] | 0.381 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 21 | total | -0.114 | 0.535 | [-1.164, 0.935] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 21 | margin | 0.268 | 0.189 | [-0.101, 0.638] | 0.381 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 21 | total | -0.088 | 0.169 | [-0.419, 0.243] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 21 | margin | -0.626 | 0.440 | [-1.489, 0.237] | 0.619 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 21 | total | 0.026 | 0.375 | [-0.708, 0.760] | 0.476 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 21 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 21 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 21 | margin | 0.895 | 0.629 | [-0.338, 2.127] | 0.381 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 21 | total | -0.114 | 0.535 | [-1.164, 0.935] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 21 | margin | 0.268 | 0.189 | [-0.101, 0.638] | 0.381 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 21 | total | -0.088 | 0.169 | [-0.419, 0.243] | 0.571 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 21 | margin | -0.071 | 0.093 | [-0.254, 0.111] | 0.190 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 21 | total | 0.262 | 0.160 | [-0.053, 0.576] | 0.048 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 21 | margin | 0.823 | 0.659 | [-0.469, 2.115] | 0.381 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 21 | total | 0.148 | 0.477 | [-0.788, 1.083] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 21 | margin | 0.197 | 0.231 | [-0.256, 0.650] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 21 | total | 0.174 | 0.160 | [-0.139, 0.487] | 0.333 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 21 | 1 | 6 | 14 | 0 | 0.143 | 0.381 | 2.38 |
| DATA_ONLY | total | 21 | 8 | 1 | 12 | 0 | 0.889 | 0.571 | 2.25 |
| HYBRID_30 | margin | 21 | 1 | 6 | 14 | 0 | 0.143 | 0.381 | 0.71 |
| HYBRID_30 | total | 21 | 8 | 1 | 12 | 0 | 0.889 | 0.571 | 0.68 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 6 | 8.73 | 8.75 | 0.000 |
| DATA_ONLY | margin | 1-2 | 4 | 6.52 | 5.88 | 1.000 |
| DATA_ONLY | margin | 2-3 | 4 | 11.07 | 10.88 | - |
| DATA_ONLY | margin | 3-5 | 5 | 14.03 | 13.20 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.25 | 0.000 |
| DATA_ONLY | total | <=1 | 4 | 10.62 | 11.12 | 1.000 |
| DATA_ONLY | total | 1-2 | 4 | 9.99 | 9.38 | 0.000 |
| DATA_ONLY | total | 2-3 | 7 | 9.24 | 9.86 | 1.000 |
| DATA_ONLY | total | 3-5 | 6 | 12.33 | 12.08 | 1.000 |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 15 | 8.80 | 8.80 | 0.167 |
| HYBRID_30 | margin | 1-2 | 6 | 16.93 | 16.00 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 18 | 10.30 | 10.47 | 0.889 |
| HYBRID_30 | total | 1-2 | 3 | 12.08 | 11.67 | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 21}; DATA_ONLY quality states: {'OK': 21}; close centre status: {'OK': 21}.

## Game-centre accuracy — T-6h (27 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 27 | 3 | 9.89 | 12.83 | 0.78 | 9.35 | 11.31 | -2.31 | 0.250 |
| DATA_ONLY | 27 | 3 | 10.56 | 13.18 | -0.04 | 9.83 | 12.21 | -1.58 | 0.258 |
| HYBRID_30 | 27 | 3 | 10.09 | 12.87 | 0.53 | 9.41 | 11.52 | -2.09 | 0.251 |
| market at snapshot | 27 | 3 | 9.89 | 12.83 | 0.78 | 9.35 | 11.31 | -2.31 | - |
| market at close | 27 | 3 | 9.89 | 12.81 | 0.81 | 9.48 | 11.47 | -2.37 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 27 | margin | 0.671 | 0.551 | [-0.409, 1.752] | 0.407 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 27 | total | 0.476 | 0.470 | [-0.446, 1.398] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 27 | margin | 0.201 | 0.165 | [-0.123, 0.526] | 0.407 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 27 | total | 0.059 | 0.138 | [-0.212, 0.330] | 0.519 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 27 | margin | -0.470 | 0.386 | [-1.227, 0.287] | 0.593 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 27 | total | -0.417 | 0.348 | [-1.099, 0.265] | 0.556 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 27 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 27 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 27 | margin | 0.671 | 0.551 | [-0.409, 1.752] | 0.407 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 27 | total | 0.476 | 0.470 | [-0.446, 1.398] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 27 | margin | 0.201 | 0.165 | [-0.123, 0.526] | 0.407 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 27 | total | 0.059 | 0.138 | [-0.212, 0.330] | 0.519 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 27 | margin | 0.000 | 0.122 | [-0.240, 0.240] | 0.185 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 27 | total | -0.130 | 0.152 | [-0.428, 0.169] | 0.259 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 27 | margin | 0.671 | 0.533 | [-0.374, 1.717] | 0.407 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 27 | total | 0.346 | 0.517 | [-0.667, 1.359] | 0.481 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 27 | margin | 0.201 | 0.179 | [-0.149, 0.552] | 0.370 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 27 | total | -0.071 | 0.215 | [-0.492, 0.351] | 0.556 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 27 | 7 | 3 | 17 | 0 | 0.700 | 0.407 | 2.41 |
| DATA_ONLY | total | 27 | 7 | 5 | 15 | 0 | 0.583 | 0.444 | 1.95 |
| HYBRID_30 | margin | 27 | 7 | 3 | 17 | 0 | 0.700 | 0.407 | 0.72 |
| HYBRID_30 | total | 27 | 7 | 5 | 15 | 0 | 0.583 | 0.519 | 0.58 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 5 | 11.29 | 11.50 | 0.500 |
| DATA_ONLY | margin | 1-2 | 9 | 9.84 | 9.22 | 0.667 |
| DATA_ONLY | margin | 2-3 | 5 | 10.24 | 9.80 | 1.000 |
| DATA_ONLY | margin | 3-5 | 6 | 9.07 | 9.08 | 0.500 |
| DATA_ONLY | margin | >5 | 2 | 17.23 | 11.50 | 1.000 |
| DATA_ONLY | total | <=1 | 9 | 9.15 | 9.22 | 0.750 |
| DATA_ONLY | total | 1-2 | 9 | 9.61 | 9.94 | 0.600 |
| DATA_ONLY | total | 2-3 | 4 | 6.32 | 6.25 | 0.000 |
| DATA_ONLY | total | 3-5 | 3 | 13.15 | 11.83 | - |
| DATA_ONLY | total | >5 | 2 | 15.88 | 9.75 | 1.000 |
| HYBRID_30 | margin | <=1 | 20 | 9.85 | 9.80 | 0.750 |
| HYBRID_30 | margin | 1-2 | 7 | 10.77 | 10.14 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 23 | 9.36 | 9.39 | 0.545 |
| HYBRID_30 | total | 1-2 | 3 | 5.97 | 6.00 | 1.000 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 27}; DATA_ONLY quality states: {'OK': 27}; close centre status: {'OK': 27}.

## Game-centre accuracy — T-90m (34 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 34 | 3 | 9.44 | 12.09 | 1.12 | 10.22 | 12.92 | -0.04 | 0.242 |
| DATA_ONLY | 34 | 3 | 10.06 | 12.72 | 0.28 | 10.73 | 13.63 | 0.54 | 0.254 |
| HYBRID_30 | 34 | 3 | 9.62 | 12.21 | 0.87 | 10.33 | 13.09 | 0.13 | 0.243 |
| market at snapshot | 34 | 3 | 9.44 | 12.09 | 1.12 | 10.22 | 12.92 | -0.04 | - |
| market at close | 34 | 3 | 9.46 | 12.09 | 1.10 | 10.21 | 12.86 | -0.12 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 34 | margin | 0.622 | 0.488 | [-0.335, 1.579] | 0.382 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 34 | total | 0.509 | 0.429 | [-0.332, 1.351] | 0.441 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 34 | margin | 0.176 | 0.147 | [-0.112, 0.465] | 0.412 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 34 | total | 0.107 | 0.133 | [-0.154, 0.367] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 34 | margin | -0.446 | 0.342 | [-1.116, 0.224] | 0.618 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 34 | total | -0.402 | 0.301 | [-0.992, 0.187] | 0.559 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 34 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 34 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 34 | margin | 0.622 | 0.488 | [-0.335, 1.579] | 0.382 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 34 | total | 0.509 | 0.429 | [-0.332, 1.351] | 0.441 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 34 | margin | 0.176 | 0.147 | [-0.112, 0.465] | 0.412 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 34 | total | 0.107 | 0.133 | [-0.154, 0.367] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 34 | margin | -0.015 | 0.061 | [-0.135, 0.106] | 0.118 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 34 | total | 0.015 | 0.096 | [-0.173, 0.202] | 0.206 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 34 | margin | 0.608 | 0.488 | [-0.348, 1.563] | 0.382 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 34 | total | 0.524 | 0.452 | [-0.362, 1.410] | 0.412 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 34 | margin | 0.162 | 0.154 | [-0.141, 0.464] | 0.412 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 34 | total | 0.121 | 0.172 | [-0.215, 0.458] | 0.441 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 34 | 5 | 4 | 25 | 0 | 0.556 | 0.382 | 2.42 |
| DATA_ONLY | total | 34 | 8 | 6 | 20 | 0 | 0.571 | 0.441 | 2.05 |
| HYBRID_30 | margin | 34 | 5 | 4 | 25 | 0 | 0.556 | 0.412 | 0.73 |
| HYBRID_30 | total | 34 | 8 | 6 | 20 | 0 | 0.571 | 0.500 | 0.61 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 6 | 6.74 | 6.67 | 0.000 |
| DATA_ONLY | margin | 1-2 | 9 | 8.15 | 7.72 | 1.000 |
| DATA_ONLY | margin | 2-3 | 10 | 9.74 | 9.70 | 0.750 |
| DATA_ONLY | margin | 3-5 | 7 | 11.00 | 10.36 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 11 | 12.23 | 12.45 | 0.800 |
| DATA_ONLY | total | 1-2 | 9 | 6.06 | 6.50 | 0.333 |
| DATA_ONLY | total | 2-3 | 6 | 10.10 | 9.58 | 1.000 |
| DATA_ONLY | total | 3-5 | 6 | 10.94 | 9.58 | 0.000 |
| DATA_ONLY | total | >5 | 2 | 24.81 | 18.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 25 | 8.30 | 8.26 | 0.625 |
| HYBRID_30 | margin | 1-2 | 9 | 13.27 | 12.72 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 28 | 9.91 | 9.93 | 0.727 |
| HYBRID_30 | total | 1-2 | 5 | 10.40 | 10.00 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 34}; DATA_ONLY quality states: {'OK': 34}; close centre status: {'OK': 34}.

## Game-centre accuracy — T-30m (45 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 45 | 3 | 10.62 | 13.29 | 2.24 | 10.77 | 14.22 | -1.52 | 0.231 |
| DATA_ONLY | 45 | 3 | 11.42 | 14.07 | 1.63 | 11.56 | 15.03 | -0.51 | 0.258 |
| HYBRID_30 | 45 | 3 | 10.84 | 13.47 | 2.06 | 10.97 | 14.42 | -1.22 | 0.239 |
| market at snapshot | 45 | 3 | 10.62 | 13.29 | 2.24 | 10.77 | 14.22 | -1.52 | - |
| market at close | 45 | 3 | 10.64 | 13.27 | 2.27 | 10.89 | 14.37 | -1.47 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 45 | margin | 0.799 | 0.391 | [0.033, 1.565] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 45 | total | 0.798 | 0.366 | [0.080, 1.515] | 0.422 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 45 | margin | 0.216 | 0.118 | [-0.015, 0.448] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 45 | total | 0.205 | 0.113 | [-0.018, 0.427] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 45 | margin | -0.583 | 0.275 | [-1.121, -0.045] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 45 | total | -0.593 | 0.256 | [-1.095, -0.092] | 0.578 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 45 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 45 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 45 | margin | 0.799 | 0.391 | [0.033, 1.565] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 45 | total | 0.798 | 0.366 | [0.080, 1.515] | 0.422 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 45 | margin | 0.216 | 0.118 | [-0.015, 0.448] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 45 | total | 0.205 | 0.113 | [-0.018, 0.427] | 0.467 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 45 | margin | -0.022 | 0.055 | [-0.130, 0.085] | 0.111 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 45 | total | -0.122 | 0.071 | [-0.262, 0.018] | 0.222 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 45 | margin | 0.777 | 0.392 | [0.009, 1.545] | 0.378 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 45 | total | 0.676 | 0.377 | [-0.063, 1.414] | 0.422 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 45 | margin | 0.194 | 0.128 | [-0.057, 0.445] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 45 | total | 0.082 | 0.135 | [-0.183, 0.347] | 0.489 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 45 | 6 | 4 | 35 | 0 | 0.600 | 0.400 | 2.28 |
| DATA_ONLY | total | 45 | 8 | 6 | 31 | 0 | 0.571 | 0.422 | 1.98 |
| HYBRID_30 | margin | 45 | 6 | 4 | 35 | 0 | 0.600 | 0.444 | 0.68 |
| HYBRID_30 | total | 45 | 8 | 6 | 31 | 0 | 0.571 | 0.467 | 0.59 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 12 | 8.93 | 8.50 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.04 | 9.62 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 16 | 13.14 | 13.31 | 0.667 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 7 | 5.32 | 5.14 | 0.800 |
| DATA_ONLY | total | 3-5 | 9 | 12.86 | 9.72 | 0.500 |
| DATA_ONLY | total | >5 | 2 | 19.32 | 12.75 | - |
| HYBRID_30 | margin | <=1 | 35 | 9.93 | 9.83 | 0.667 |
| HYBRID_30 | margin | 1-2 | 10 | 14.02 | 13.40 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 37 | 10.95 | 10.96 | 0.583 |
| HYBRID_30 | total | 1-2 | 7 | 9.64 | 8.64 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 45}; DATA_ONLY quality states: {'OK': 45}; close centre status: {'OK': 45}.

## Contract pricing — latest_pregame (3587 contracts, 46 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3587 | 0.1653 | 0.4965 | 0.415 | 0.423 | 3587 | 0.1653 | 0.1654 | 0.1680 |
| DATA_ONLY | 3587 | 0.1786 | 0.5332 | 0.422 | 0.423 | 3587 | 0.1786 | 0.1654 | 0.1680 |
| HYBRID_30 | 3587 | 0.1687 | 0.5056 | 0.414 | 0.423 | 3587 | 0.1687 | 0.1654 | 0.1680 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3587 | 46 | 0.01333 | [0.00399, 0.02296] | 0.01333 | [0.00399, 0.02296] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3587 | 46 | 0.00342 | [0.00068, 0.00643] | 0.00342 | [0.00068, 0.00643] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3587 | 46 | -0.00991 | [-0.01733, -0.00250] | -0.00991 | [-0.01733, -0.00250] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3587 | 46 | - | - | -0.00019 | [-0.00128, 0.00074] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3522 | 46 | - | - | -0.00051 | [-0.00179, 0.00062] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3587 | 46 | - | - | 0.01315 | [0.00344, 0.02304] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3522 | 46 | - | - | 0.01310 | [0.00305, 0.02315] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3587 | 46 | - | - | 0.00324 | [0.00028, 0.00647] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3522 | 46 | - | - | 0.00300 | [-0.00003, 0.00642] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 184, 'GAME_WINNER': 92, 'SPREAD': 1183, 'TEAM_TOTAL': 1254, 'TOTAL': 874}; settlement: {'SETTLED': 3587}; close: {'OK': 3522, 'OK_STALE': 65}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 558 / 0.055 / 0.048 | 534 / 0.054 / 0.073 | 549 / 0.053 / 0.060 |
| 0.10-0.20 | 577 / 0.145 / 0.187 | 565 / 0.145 / 0.202 | 580 / 0.146 / 0.188 |
| 0.20-0.30 | 418 / 0.248 / 0.278 | 429 / 0.249 / 0.298 | 412 / 0.248 / 0.272 |
| 0.30-0.40 | 358 / 0.351 / 0.358 | 366 / 0.349 / 0.372 | 366 / 0.348 / 0.363 |
| 0.40-0.50 | 371 / 0.450 / 0.474 | 350 / 0.449 / 0.466 | 403 / 0.449 / 0.501 |
| 0.50-0.60 | 342 / 0.547 / 0.558 | 313 / 0.550 / 0.511 | 320 / 0.549 / 0.544 |
| 0.60-0.70 | 236 / 0.651 / 0.614 | 283 / 0.648 / 0.551 | 237 / 0.649 / 0.582 |
| 0.70-0.80 | 184 / 0.750 / 0.739 | 192 / 0.750 / 0.698 | 191 / 0.751 / 0.707 |
| 0.80-0.90 | 190 / 0.848 / 0.853 | 190 / 0.851 / 0.816 | 186 / 0.852 / 0.871 |
| 0.90-1.00 | 353 / 0.954 / 0.935 | 365 / 0.956 / 0.915 | 343 / 0.956 / 0.936 |

## Contract pricing — T-24h (1638 contracts, 21 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1638 | 0.1677 | 0.5029 | 0.414 | 0.395 | 1638 | 0.1677 | 0.1674 | 0.1687 |
| DATA_ONLY | 1638 | 0.1769 | 0.5300 | 0.416 | 0.395 | 1638 | 0.1769 | 0.1674 | 0.1687 |
| HYBRID_30 | 1638 | 0.1686 | 0.5050 | 0.413 | 0.395 | 1638 | 0.1686 | 0.1674 | 0.1687 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1638 | 21 | 0.00921 | [-0.00655, 0.02498] | 0.00921 | [-0.00655, 0.02498] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1638 | 21 | 0.00084 | [-0.00458, 0.00594] | 0.00084 | [-0.00458, 0.00594] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1638 | 21 | -0.00837 | [-0.02033, 0.00290] | -0.00837 | [-0.02033, 0.00290] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1638 | 21 | - | - | 0.00035 | [-0.00083, 0.00157] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1614 | 21 | - | - | 0.00101 | [-0.00107, 0.00340] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1638 | 21 | - | - | 0.00956 | [-0.00604, 0.02502] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1614 | 21 | - | - | 0.01046 | [-0.00451, 0.02560] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1638 | 21 | - | - | 0.00119 | [-0.00419, 0.00608] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1614 | 21 | - | - | 0.00195 | [-0.00309, 0.00664] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 84, 'GAME_WINNER': 42, 'SPREAD': 543, 'TEAM_TOTAL': 570, 'TOTAL': 399}; settlement: {'SETTLED': 1638}; close: {'OK': 1614, 'OK_STALE': 24}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 261 / 0.055 / 0.019 | 254 / 0.053 / 0.047 | 253 / 0.053 / 0.016 |
| 0.10-0.20 | 255 / 0.146 / 0.157 | 259 / 0.146 / 0.178 | 263 / 0.145 / 0.171 |
| 0.20-0.30 | 194 / 0.248 / 0.299 | 197 / 0.250 / 0.335 | 195 / 0.249 / 0.287 |
| 0.30-0.40 | 158 / 0.350 / 0.342 | 167 / 0.348 / 0.347 | 156 / 0.347 / 0.359 |
| 0.40-0.50 | 176 / 0.449 / 0.449 | 156 / 0.447 / 0.397 | 192 / 0.449 / 0.474 |
| 0.50-0.60 | 149 / 0.545 / 0.510 | 143 / 0.550 / 0.434 | 139 / 0.548 / 0.460 |
| 0.60-0.70 | 109 / 0.647 / 0.569 | 133 / 0.648 / 0.541 | 107 / 0.646 / 0.523 |
| 0.70-0.80 | 92 / 0.747 / 0.707 | 81 / 0.748 / 0.716 | 93 / 0.748 / 0.710 |
| 0.80-0.90 | 85 / 0.850 / 0.776 | 90 / 0.849 / 0.800 | 84 / 0.853 / 0.810 |
| 0.90-1.00 | 159 / 0.955 / 0.893 | 158 / 0.956 / 0.880 | 156 / 0.955 / 0.904 |

## Contract pricing — T-6h (2110 contracts, 27 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2110 | 0.1592 | 0.4788 | 0.414 | 0.425 | 2110 | 0.1592 | 0.1595 | 0.1627 |
| DATA_ONLY | 2110 | 0.1677 | 0.5011 | 0.421 | 0.425 | 2110 | 0.1677 | 0.1595 | 0.1627 |
| HYBRID_30 | 2110 | 0.1607 | 0.4834 | 0.413 | 0.425 | 2110 | 0.1607 | 0.1595 | 0.1627 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2110 | 27 | 0.00846 | [-0.00191, 0.01997] | 0.00846 | [-0.00191, 0.01997] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2110 | 27 | 0.00155 | [-0.00093, 0.00447] | 0.00155 | [-0.00093, 0.00447] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2110 | 27 | -0.00691 | [-0.01618, 0.00186] | -0.00691 | [-0.01618, 0.00186] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2110 | 27 | - | - | -0.00031 | [-0.00158, 0.00092] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2056 | 27 | - | - | -0.00027 | [-0.00211, 0.00147] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2110 | 27 | - | - | 0.00815 | [-0.00282, 0.01978] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2056 | 27 | - | - | 0.00849 | [-0.00279, 0.02048] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2110 | 27 | - | - | 0.00124 | [-0.00146, 0.00433] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2056 | 27 | - | - | 0.00138 | [-0.00161, 0.00468] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 108, 'GAME_WINNER': 54, 'SPREAD': 696, 'TEAM_TOTAL': 739, 'TOTAL': 513}; settlement: {'SETTLED': 2110}; close: {'OK': 2056, 'OK_STALE': 54}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 334 / 0.056 / 0.060 | 327 / 0.054 / 0.055 | 330 / 0.054 / 0.055 |
| 0.10-0.20 | 333 / 0.144 / 0.171 | 329 / 0.146 / 0.182 | 333 / 0.146 / 0.177 |
| 0.20-0.30 | 246 / 0.249 / 0.252 | 245 / 0.250 / 0.282 | 252 / 0.250 / 0.254 |
| 0.30-0.40 | 215 / 0.351 / 0.358 | 212 / 0.349 / 0.396 | 207 / 0.349 / 0.391 |
| 0.40-0.50 | 217 / 0.451 / 0.493 | 203 / 0.447 / 0.448 | 240 / 0.449 / 0.479 |
| 0.50-0.60 | 200 / 0.545 / 0.530 | 180 / 0.547 / 0.522 | 184 / 0.549 / 0.533 |
| 0.60-0.70 | 138 / 0.652 / 0.630 | 170 / 0.646 / 0.576 | 136 / 0.647 / 0.603 |
| 0.70-0.80 | 107 / 0.754 / 0.766 | 116 / 0.750 / 0.724 | 113 / 0.749 / 0.752 |
| 0.80-0.90 | 115 / 0.851 / 0.887 | 114 / 0.849 / 0.842 | 113 / 0.850 / 0.885 |
| 0.90-1.00 | 205 / 0.956 / 0.956 | 214 / 0.956 / 0.944 | 202 / 0.956 / 0.960 |

## Contract pricing — T-90m (2652 contracts, 34 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2652 | 0.1591 | 0.4817 | 0.416 | 0.400 | 2652 | 0.1591 | 0.1582 | 0.1610 |
| DATA_ONLY | 2652 | 0.1667 | 0.5026 | 0.420 | 0.400 | 2652 | 0.1667 | 0.1582 | 0.1610 |
| HYBRID_30 | 2652 | 0.1616 | 0.4862 | 0.413 | 0.400 | 2652 | 0.1616 | 0.1582 | 0.1610 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2652 | 34 | 0.00761 | [-0.00411, 0.01927] | 0.00761 | [-0.00411, 0.01927] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2652 | 34 | 0.00251 | [-0.00111, 0.00628] | 0.00251 | [-0.00111, 0.00628] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2652 | 34 | -0.00511 | [-0.01372, 0.00350] | -0.00511 | [-0.01372, 0.00350] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2652 | 34 | - | - | 0.00082 | [-0.00059, 0.00230] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2595 | 34 | - | - | 0.00088 | [-0.00081, 0.00265] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2652 | 34 | - | - | 0.00844 | [-0.00324, 0.02057] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2595 | 34 | - | - | 0.00870 | [-0.00341, 0.02114] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2652 | 34 | - | - | 0.00333 | [-0.00056, 0.00716] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2595 | 34 | - | - | 0.00348 | [-0.00055, 0.00747] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 136, 'GAME_WINNER': 68, 'SPREAD': 876, 'TEAM_TOTAL': 926, 'TOTAL': 646}; settlement: {'SETTLED': 2652}; close: {'OK': 2595, 'OK_STALE': 57}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 413 / 0.055 / 0.029 | 404 / 0.054 / 0.045 | 416 / 0.053 / 0.034 |
| 0.10-0.20 | 419 / 0.144 / 0.158 | 413 / 0.145 / 0.167 | 419 / 0.146 / 0.162 |
| 0.20-0.30 | 308 / 0.247 / 0.260 | 318 / 0.250 / 0.274 | 315 / 0.249 / 0.263 |
| 0.30-0.40 | 264 / 0.349 / 0.311 | 268 / 0.350 / 0.325 | 258 / 0.349 / 0.345 |
| 0.40-0.50 | 267 / 0.450 / 0.431 | 259 / 0.448 / 0.417 | 300 / 0.448 / 0.457 |
| 0.50-0.60 | 260 / 0.545 / 0.542 | 228 / 0.549 / 0.500 | 230 / 0.549 / 0.500 |
| 0.60-0.70 | 181 / 0.651 / 0.569 | 211 / 0.647 / 0.559 | 178 / 0.649 / 0.551 |
| 0.70-0.80 | 134 / 0.750 / 0.731 | 145 / 0.748 / 0.697 | 142 / 0.749 / 0.704 |
| 0.80-0.90 | 148 / 0.849 / 0.845 | 142 / 0.850 / 0.838 | 140 / 0.851 / 0.857 |
| 0.90-1.00 | 258 / 0.956 / 0.926 | 264 / 0.956 / 0.909 | 254 / 0.956 / 0.933 |

## Contract pricing — T-30m (3510 contracts, 45 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3510 | 0.1659 | 0.4982 | 0.413 | 0.418 | 3510 | 0.1659 | 0.1661 | 0.1687 |
| DATA_ONLY | 3510 | 0.1781 | 0.5321 | 0.422 | 0.418 | 3510 | 0.1781 | 0.1661 | 0.1687 |
| HYBRID_30 | 3510 | 0.1688 | 0.5062 | 0.413 | 0.418 | 3510 | 0.1688 | 0.1661 | 0.1687 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3510 | 45 | 0.01227 | [0.00351, 0.02204] | 0.01227 | [0.00351, 0.02204] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3510 | 45 | 0.00296 | [0.00026, 0.00562] | 0.00296 | [0.00026, 0.00562] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3510 | 45 | -0.00931 | [-0.01690, -0.00249] | -0.00931 | [-0.01690, -0.00249] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3510 | 45 | - | - | -0.00020 | [-0.00128, 0.00074] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3445 | 45 | - | - | -0.00053 | [-0.00170, 0.00068] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3510 | 45 | - | - | 0.01207 | [0.00309, 0.02180] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3445 | 45 | - | - | 0.01200 | [0.00286, 0.02215] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3510 | 45 | - | - | 0.00276 | [-0.00018, 0.00548] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3445 | 45 | - | - | 0.00251 | [-0.00050, 0.00553] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 180, 'GAME_WINNER': 90, 'SPREAD': 1158, 'TEAM_TOTAL': 1227, 'TOTAL': 855}; settlement: {'SETTLED': 3510}; close: {'OK': 3445, 'OK_STALE': 65}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 551 / 0.055 / 0.049 | 524 / 0.053 / 0.071 | 541 / 0.053 / 0.061 |
| 0.10-0.20 | 564 / 0.145 / 0.184 | 552 / 0.145 / 0.199 | 566 / 0.146 / 0.186 |
| 0.20-0.30 | 409 / 0.248 / 0.279 | 419 / 0.249 / 0.294 | 404 / 0.249 / 0.267 |
| 0.30-0.40 | 351 / 0.351 / 0.353 | 359 / 0.349 / 0.365 | 360 / 0.348 / 0.361 |
| 0.40-0.50 | 369 / 0.450 / 0.469 | 339 / 0.449 / 0.451 | 393 / 0.449 / 0.489 |
| 0.50-0.60 | 331 / 0.546 / 0.544 | 308 / 0.550 / 0.503 | 314 / 0.549 / 0.535 |
| 0.60-0.70 | 228 / 0.650 / 0.601 | 279 / 0.648 / 0.545 | 231 / 0.649 / 0.571 |
| 0.70-0.80 | 182 / 0.750 / 0.736 | 188 / 0.750 / 0.691 | 189 / 0.751 / 0.704 |
| 0.80-0.90 | 184 / 0.848 / 0.848 | 186 / 0.851 / 0.812 | 180 / 0.852 / 0.867 |
| 0.90-1.00 | 341 / 0.954 / 0.933 | 356 / 0.956 / 0.913 | 332 / 0.956 / 0.934 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 21 | 6 | 1 | 2 | 12 | 0 | 0.333 [0.061, 0.792] | 0.333 | 0.333 | 0.00 |
| T-24h | DATA_ONLY | total | 21 | 4 | 6 | 1 | 10 | 0 | 0.857 [0.487, 0.974] | 0.529 | 0.471 | 0.41 |
| T-24h | HYBRID_30 (derived) | margin | 21 | 15 | 0 | 1 | 5 | 0 | 0.000 [0.000, 0.793] | 0.167 | 0.167 | -0.08 |
| T-24h | HYBRID_30 (derived) | total | 21 | 18 | 0 | 0 | 3 | 0 | - - | 0.333 | 0.333 | 0.00 |
| T-6h | DATA_ONLY | margin | 27 | 5 | 6 | 2 | 14 | 0 | 0.750 [0.409, 0.929] | 0.364 | 0.409 | 0.11 |
| T-6h | DATA_ONLY | total | 27 | 9 | 4 | 4 | 10 | 0 | 0.500 [0.215, 0.785] | 0.444 | 0.444 | -0.11 |
| T-6h | HYBRID_30 (derived) | margin | 27 | 20 | 1 | 1 | 5 | 0 | 0.500 [0.095, 0.905] | 0.286 | 0.286 | 0.00 |
| T-6h | HYBRID_30 (derived) | total | 27 | 23 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.500 | 0.250 | 0.12 |
| T-90m | DATA_ONLY | margin | 34 | 6 | 5 | 2 | 21 | 0 | 0.714 [0.359, 0.918] | 0.393 | 0.393 | 0.02 |
| T-90m | DATA_ONLY | total | 34 | 11 | 4 | 5 | 14 | 0 | 0.444 [0.189, 0.733] | 0.391 | 0.391 | -0.09 |
| T-90m | HYBRID_30 (derived) | margin | 34 | 25 | 0 | 1 | 8 | 0 | 0.000 [0.000, 0.793] | 0.333 | 0.333 | -0.11 |
| T-90m | HYBRID_30 (derived) | total | 34 | 28 | 0 | 3 | 3 | 0 | 0.000 [0.000, 0.561] | 0.333 | 0.333 | -0.42 |
| T-30m | DATA_ONLY | margin | 45 | 9 | 5 | 2 | 29 | 0 | 0.714 [0.359, 0.918] | 0.333 | 0.333 | 0.06 |
| T-30m | DATA_ONLY | total | 45 | 16 | 6 | 5 | 18 | 0 | 0.545 [0.280, 0.787] | 0.345 | 0.345 | -0.05 |
| T-30m | HYBRID_30 (derived) | margin | 45 | 35 | 0 | 1 | 9 | 0 | 0.000 [0.000, 0.793] | 0.300 | 0.300 | -0.10 |
| T-30m | HYBRID_30 (derived) | total | 45 | 37 | 1 | 1 | 6 | 0 | 0.500 [0.095, 0.905] | 0.125 | 0.125 | 0.00 |
| latest_pregame | DATA_ONLY | margin | 46 | 9 | 5 | 2 | 30 | 0 | 0.714 [0.359, 0.918] | 0.324 | 0.324 | 0.05 |
| latest_pregame | DATA_ONLY | total | 46 | 16 | 6 | 5 | 19 | 0 | 0.545 [0.280, 0.787] | 0.333 | 0.333 | -0.05 |
| latest_pregame | HYBRID_30 (derived) | margin | 46 | 36 | 0 | 1 | 9 | 0 | 0.000 [0.000, 0.793] | 0.300 | 0.300 | -0.10 |
| latest_pregame | HYBRID_30 (derived) | total | 46 | 37 | 1 | 1 | 7 | 0 | 0.500 [0.095, 0.905] | 0.111 | 0.111 | 0.00 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 9 | 1 | 2 | 6 | 0 | 0.333 |
| margin | 1-2 | 13 | 3 | 0 | 10 | 0 | 1.000 |
| margin | 2-3 | 12 | 2 | 1 | 9 | 0 | 0.667 |
| margin | 3-5 | 10 | 0 | 1 | 9 | 0 | 0.000 |
| margin | >5 | 2 | 0 | 0 | 2 | 0 | - |
| total | <=1 | 16 | 2 | 1 | 13 | 0 | 0.667 |
| total | 1-2 | 11 | 1 | 3 | 7 | 0 | 0.250 |
| total | 2-3 | 7 | 4 | 1 | 2 | 0 | 0.800 |
| total | 3-5 | 9 | 1 | 1 | 7 | 0 | 0.500 |
| total | >5 | 3 | 0 | 0 | 3 | 0 | - |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 15 | 3 | 0.667 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 15 | 4 | 0.500 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

2076 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

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
| 2026_03_ATL_GB | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.0 | 3 | 1.04 | 2.33 | EXPECTED_ACTIVE | True | -0.193 | TEAM_VOLUME_MISS |
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
| 2026_03_ATL_GB | Drake London | receiving_yards | 52.7 | 4–123 | 194 | 4.10 | 0.99 | 5.9 | 10 | 8.96 | 19.40 | EXPECTED_ACTIVE | True | 0.190 | EFFICIENCY_MISS |
| 2026_01_CHI_CAR | Jalen Coker | receptions | 2.2 | 0–6 | 8 | 4.05 | 0.98 | 3.0 | 9 | 0.71 | 0.89 | EXPECTED_ACTIVE | True | 0.253 | OPPORTUNITY_MISS |
| 2026_01_CLE_JAX | Trevor Lawrence | passing_tds | 1.6 | 0–4 | 4 | 4.05 | 0.95 | 33.5 | 23 | 0.05 | 0.17 | EXPECTED_ACTIVE | True | 0.010 | EFFICIENCY_MISS |
| 2026_01_NO_DET | Travis Etienne Jr. | receptions | 1.3 | 0–5 | 7 | 4.05 | 0.98 | 1.9 | 9 | 0.71 | 0.78 | EXPECTED_ACTIVE | True | 0.363 | OPPORTUNITY_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | receptions | 0.7 | 0–5 | 3 | 4.05 | 0.85 | 1.1 | 3 | 0.67 | 1.00 | EXPECTED_ACTIVE | True | 0.292 | OPPORTUNITY_MISS |
| 2026_01_TB_CIN | Samaje Perine | receiving_yards | 7.3 | 0–32 | 30 | 4.05 | 0.93 | 1.5 | 3 | 4.95 | 10.00 | EXPECTED_ACTIVE | True | 0.055 | EFFICIENCY_MISS |
| 2026_01_TB_CIN | Bucky Irving | receptions | 1.4 | 0–5 | 7 | 4.05 | 0.98 | 1.9 | 7 | 0.76 | 1.00 | EXPECTED_ACTIVE | True | 0.142 | OPPORTUNITY_MISS |
| 2026_02_CAR_ATL | Jalen Coker | receptions | 2.0 | 0–6 | 8 | 4.05 | 0.98 | 2.9 | 9 | 0.70 | 0.89 | EXPECTED_ACTIVE | True | 0.317 | OPPORTUNITY_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 362, 'TEAM_VOLUME_MISS': 95, 'UNEXPLAINED_VARIANCE': 64, 'OPPORTUNITY_MISS': 700, 'NO_LARGE_MISS': 785, 'INSUFFICIENT_DATA': 41, 'AVAILABILITY_MISS': 29}.
Missing usage (no snap table or stats row): 70.

## Decision funnel (BET / WATCH / PASS accounting of the existing gates; no authority)

83 snapshot(s). A contract's terminal state is where it left the existing gate sequence when the model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).

### Newest snapshot 20260927T232119Z (47622 markets)

| stage | markets |
|---|---|
| discovered | 47622 |
| mapped | 39319 |
| supported | 1385 |
| priced | 1385 |
| raw_disagreement | 847 |
| tradable_book | 802 |
| data_quality | 788 |
| executable_price | 603 |
| liquidity | 304 |

Terminal states: {'PASS': 47133, 'WATCH': 185, 'BET': 304}

| family | BET | WATCH | PASS |
|---|---|---|---|
| AWARD | 0 | 0 | 869 |
| BOTH_TEAMS_SCORE | 0 | 0 | 192 |
| BOTH_TEAMS_SCORE_N | 0 | 0 | 192 |
| COACH_EVENT | 0 | 0 | 64 |
| CONFERENCE_WINNER | 0 | 0 | 32 |
| DIVISION_WINNER | 0 | 0 | 32 |
| DRAFT | 0 | 0 | 40 |
| FIRST_TD_SCORER | 0 | 0 | 1228 |
| FIRST_TD_TEAM | 0 | 0 | 1420 |
| GAME_EVENT | 0 | 0 | 196 |
| GAME_PLAYER_LEADER | 0 | 0 | 550 |
| GAME_STAT | 0 | 0 | 5 |
| GAME_WINNER | 0 | 10 | 118 |
| HALF_FULL_RESULT | 0 | 0 | 441 |
| MAKE_PLAYOFFS | 0 | 0 | 33 |
| NFL_BUSINESS_EVENT | 0 | 0 | 5 |
| NOT_NFL_OR_UNKNOWN | 0 | 0 | 2 |
| PERIOD_WINNER | 0 | 0 | 864 |
| PLAYER_AVAILABILITY | 0 | 0 | 23 |
| PLAYER_ROLE_EVENT | 0 | 0 | 177 |
| PLAYER_STAT | 290 | 84 | 18429 |
| RACE_TO_N | 0 | 0 | 765 |
| SEASON_DIVISION_ORDER | 0 | 0 | 192 |
| SEASON_DIVISION_STAT | 0 | 0 | 80 |
| SEASON_FANTASY | 0 | 0 | 1136 |
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
| SPREAD | 2 | 37 | 5345 |
| SUPER_BOWL_EVENT | 0 | 0 | 243 |
| SUPER_BOWL_WINNER | 0 | 0 | 32 |
| TEAM_STAT | 0 | 0 | 1246 |
| TEAM_TOTAL | 10 | 22 | 2631 |
| TEAM_WINS_BY_WEEK | 0 | 0 | 728 |
| TOTAL | 2 | 32 | 4336 |
| TOTAL_TD | 0 | 0 | 214 |
| TRANSACTION_EVENT | 0 | 0 | 281 |
| UNKNOWN_NEEDS_CLASSIFICATION | 0 | 0 | 386 |
| WEEK_EVENT | 0 | 0 | 32 |
| WEEK_LEADER | 0 | 0 | 359 |
| WIN_MARGIN_BUCKET | 0 | 0 | 336 |

| rejection reason | n |
|---|---|
| POST_KICKOFF_EXCLUDED | 33256 |
| unmapped | 8303 |
| UNSUPPORTED_RULES | 2635 |
| UNSUPPORTED_MODEL | 2027 |
| no positive disagreement against either executable ask | 538 |
| no order book observed for this ticker (books are captured i | 299 |
| book not tradable for ranking | 45 |
| ask 0.99 above the zero-net-EV ceiling 0.98 | 22 |
| UNSUPPORTED_IDENTITY | 16 |
| availability DOUBTFUL unresolved inside T-90m | 12 |
| ask 0.97 above the zero-net-EV ceiling 0.96 | 9 |
| ask 0.58 above the zero-net-EV ceiling 0.57 | 5 |
| ask 0.52 above the zero-net-EV ceiling 0.50 | 5 |
| ask 0.98 above the zero-net-EV ceiling 0.97 | 5 |
| ask 0.60 above the zero-net-EV ceiling 0.58 | 4 |

WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee schedule (`watch_ceiling`). Not replayed: ['portfolio_risk_policy (needs a stake and bankroll)', "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own confirmation is the STALE_DATA support state)"].

Across all 83 snapshots (repeated markets counted per snapshot): {'PASS': 2620159, 'WATCH': 60786, 'BET': 53464}.

