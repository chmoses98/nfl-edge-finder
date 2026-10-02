# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 48 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 2585 | 48 | 4 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 22 | 22 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 29 | 29 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 36 | 36 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 47 | 47 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 48 | 48 | 4 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_PIT_CLE | 2026-10-02T00:15 | 32 | CURRENT | -2.50 | 37.50 | 3 | 51 | -2.5/37.5 (kalshi_implied) | -2.5/37.5 (OK) |
|  |  |  | DATA_ONLY | -3.50 | 40.25 |  |  |  |  |
|  |  |  | HYBRID_30 | -2.80 | 38.32 |  |  |  |  |

## Game-centre accuracy — latest_pregame (48 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 48 | 4 | 10.66 | 13.34 | 1.41 | 10.92 | 14.19 | -1.90 | 0.235 |
| DATA_ONLY | 48 | 4 | 11.33 | 13.91 | 0.91 | 11.82 | 15.13 | -0.90 | 0.256 |
| HYBRID_30 | 48 | 4 | 10.84 | 13.45 | 1.26 | 11.16 | 14.42 | -1.60 | 0.240 |
| market at snapshot | 48 | 4 | 10.66 | 13.34 | 1.41 | 10.92 | 14.19 | -1.90 | - |
| market at close | 48 | 4 | 10.68 | 13.33 | 1.43 | 11.03 | 14.33 | -1.84 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 48 | margin | 0.673 | 0.396 | [-0.104, 1.451] | 0.396 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 48 | total | 0.907 | 0.374 | [0.173, 1.641] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 48 | margin | 0.180 | 0.119 | [-0.054, 0.414] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 48 | total | 0.239 | 0.116 | [0.013, 0.466] | 0.458 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 48 | margin | -0.493 | 0.279 | [-1.039, 0.053] | 0.604 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 48 | total | -0.668 | 0.262 | [-1.180, -0.155] | 0.583 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 48 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 48 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 48 | margin | 0.673 | 0.396 | [-0.104, 1.451] | 0.396 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 48 | total | 0.907 | 0.374 | [0.173, 1.641] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 48 | margin | 0.180 | 0.119 | [-0.054, 0.414] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 48 | total | 0.239 | 0.116 | [0.013, 0.466] | 0.458 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 48 | margin | -0.021 | 0.051 | [-0.122, 0.080] | 0.104 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 48 | total | -0.115 | 0.067 | [-0.246, 0.017] | 0.208 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 48 | margin | 0.653 | 0.397 | [-0.126, 1.431] | 0.375 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 48 | total | 0.792 | 0.384 | [0.039, 1.546] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 48 | margin | 0.159 | 0.128 | [-0.092, 0.411] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 48 | total | 0.125 | 0.135 | [-0.140, 0.390] | 0.479 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 48 | 6 | 4 | 38 | 0 | 0.600 | 0.396 | 2.32 |
| DATA_ONLY | total | 48 | 8 | 6 | 34 | 0 | 0.571 | 0.417 | 2.13 |
| HYBRID_30 | margin | 48 | 6 | 4 | 38 | 0 | 0.600 | 0.438 | 0.70 |
| HYBRID_30 | total | 48 | 8 | 6 | 34 | 0 | 0.571 | 0.458 | 0.64 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 14 | 8.56 | 8.00 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.04 | 9.62 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.67 | 21.83 | - |
| DATA_ONLY | total | <=1 | 16 | 13.14 | 13.31 | 0.667 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 8 | 6.00 | 6.19 | 0.800 |
| DATA_ONLY | total | 3-5 | 10 | 12.91 | 9.60 | 0.500 |
| DATA_ONLY | total | >5 | 3 | 20.56 | 14.33 | - |
| HYBRID_30 | margin | <=1 | 37 | 9.68 | 9.57 | 0.667 |
| HYBRID_30 | margin | 1-2 | 11 | 14.71 | 14.32 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 38 | 11.00 | 11.03 | 0.583 |
| HYBRID_30 | total | 1-2 | 9 | 10.73 | 9.61 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 48}; DATA_ONLY quality states: {'OK': 48}; close centre status: {'OK': 48}.

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

## Game-centre accuracy — T-6h (29 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 29 | 4 | 10.21 | 13.17 | -0.28 | 9.41 | 11.27 | -2.38 | 0.259 |
| DATA_ONLY | 29 | 4 | 10.65 | 13.16 | -0.85 | 9.98 | 12.20 | -1.38 | 0.260 |
| HYBRID_30 | 29 | 4 | 10.34 | 13.09 | -0.45 | 9.51 | 11.48 | -2.08 | 0.258 |
| market at snapshot | 29 | 4 | 10.21 | 13.17 | -0.28 | 9.41 | 11.27 | -2.38 | - |
| market at close | 29 | 4 | 10.21 | 13.15 | -0.24 | 9.59 | 11.45 | -2.38 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 29 | margin | 0.439 | 0.568 | [-0.675, 1.552] | 0.414 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 29 | total | 0.567 | 0.496 | [-0.406, 1.540] | 0.448 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 29 | margin | 0.132 | 0.170 | [-0.203, 0.466] | 0.414 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 29 | total | 0.092 | 0.147 | [-0.196, 0.380] | 0.517 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 29 | margin | -0.307 | 0.398 | [-1.087, 0.473] | 0.586 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 29 | total | -0.475 | 0.362 | [-1.186, 0.235] | 0.552 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 29 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 29 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 29 | margin | 0.439 | 0.568 | [-0.675, 1.552] | 0.414 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 29 | total | 0.567 | 0.496 | [-0.406, 1.540] | 0.448 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 29 | margin | 0.132 | 0.170 | [-0.203, 0.466] | 0.414 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 29 | total | 0.092 | 0.147 | [-0.196, 0.380] | 0.517 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 29 | margin | 0.000 | 0.114 | [-0.223, 0.223] | 0.172 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 29 | total | -0.172 | 0.149 | [-0.465, 0.121] | 0.276 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 29 | margin | 0.439 | 0.553 | [-0.646, 1.523] | 0.414 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 29 | total | 0.395 | 0.517 | [-0.619, 1.409] | 0.483 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 29 | margin | 0.132 | 0.182 | [-0.225, 0.488] | 0.379 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 29 | total | -0.080 | 0.202 | [-0.477, 0.316] | 0.552 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 29 | 7 | 3 | 19 | 0 | 0.700 | 0.414 | 2.50 |
| DATA_ONLY | total | 29 | 8 | 5 | 16 | 0 | 0.615 | 0.448 | 2.13 |
| HYBRID_30 | margin | 29 | 7 | 3 | 19 | 0 | 0.700 | 0.414 | 0.75 |
| HYBRID_30 | total | 29 | 8 | 5 | 16 | 0 | 0.615 | 0.517 | 0.64 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 5 | 11.29 | 11.50 | 0.500 |
| DATA_ONLY | margin | 1-2 | 10 | 9.51 | 8.85 | 0.667 |
| DATA_ONLY | margin | 2-3 | 5 | 10.24 | 9.80 | 1.000 |
| DATA_ONLY | margin | 3-5 | 6 | 9.07 | 9.08 | 0.500 |
| DATA_ONLY | margin | >5 | 3 | 17.19 | 15.50 | 1.000 |
| DATA_ONLY | total | <=1 | 9 | 9.15 | 9.22 | 0.750 |
| DATA_ONLY | total | 1-2 | 9 | 9.61 | 9.94 | 0.600 |
| DATA_ONLY | total | 2-3 | 5 | 7.20 | 7.70 | 0.000 |
| DATA_ONLY | total | 3-5 | 3 | 13.15 | 11.83 | - |
| DATA_ONLY | total | >5 | 3 | 15.04 | 8.83 | 1.000 |
| HYBRID_30 | margin | <=1 | 21 | 9.66 | 9.60 | 0.750 |
| HYBRID_30 | margin | 1-2 | 8 | 12.12 | 11.81 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 24 | 9.50 | 9.56 | 0.545 |
| HYBRID_30 | total | 1-2 | 4 | 6.71 | 6.25 | 1.000 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 29}; DATA_ONLY quality states: {'OK': 29}; close centre status: {'OK': 29}.

## Game-centre accuracy — T-90m (36 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 36 | 4 | 9.72 | 12.42 | 0.25 | 10.24 | 12.81 | -0.15 | 0.250 |
| DATA_ONLY | 36 | 4 | 10.16 | 12.73 | -0.39 | 10.80 | 13.55 | 0.58 | 0.256 |
| HYBRID_30 | 36 | 4 | 9.84 | 12.44 | 0.06 | 10.36 | 12.98 | 0.07 | 0.249 |
| market at snapshot | 36 | 4 | 9.72 | 12.42 | 0.25 | 10.24 | 12.81 | -0.15 | - |
| market at close | 36 | 4 | 9.74 | 12.42 | 0.24 | 10.25 | 12.78 | -0.25 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 36 | margin | 0.438 | 0.501 | [-0.544, 1.419] | 0.389 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 36 | total | 0.567 | 0.428 | [-0.272, 1.406] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 36 | margin | 0.121 | 0.151 | [-0.174, 0.417] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 36 | total | 0.127 | 0.132 | [-0.133, 0.386] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 36 | margin | -0.316 | 0.350 | [-1.003, 0.371] | 0.611 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 36 | total | -0.441 | 0.300 | [-1.028, 0.147] | 0.556 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 36 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 36 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 36 | margin | 0.438 | 0.501 | [-0.544, 1.419] | 0.389 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 36 | total | 0.567 | 0.428 | [-0.272, 1.406] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 36 | margin | 0.121 | 0.151 | [-0.174, 0.417] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 36 | total | 0.127 | 0.132 | [-0.133, 0.386] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 36 | margin | -0.014 | 0.058 | [-0.128, 0.100] | 0.111 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 36 | total | -0.014 | 0.094 | [-0.199, 0.171] | 0.222 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 36 | margin | 0.424 | 0.500 | [-0.556, 1.404] | 0.389 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 36 | total | 0.553 | 0.453 | [-0.335, 1.442] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 36 | margin | 0.108 | 0.157 | [-0.200, 0.415] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 36 | total | 0.113 | 0.173 | [-0.226, 0.452] | 0.444 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 36 | 5 | 4 | 27 | 0 | 0.556 | 0.389 | 2.49 |
| DATA_ONLY | total | 36 | 8 | 7 | 21 | 0 | 0.533 | 0.444 | 2.12 |
| HYBRID_30 | margin | 36 | 5 | 4 | 27 | 0 | 0.556 | 0.417 | 0.75 |
| HYBRID_30 | total | 36 | 8 | 7 | 21 | 0 | 0.533 | 0.500 | 0.63 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 6 | 6.74 | 6.67 | 0.000 |
| DATA_ONLY | margin | 1-2 | 10 | 7.99 | 7.50 | 1.000 |
| DATA_ONLY | margin | 2-3 | 10 | 9.74 | 9.70 | 0.750 |
| DATA_ONLY | margin | 3-5 | 7 | 11.00 | 10.36 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.67 | 21.83 | - |
| DATA_ONLY | total | <=1 | 11 | 12.23 | 12.45 | 0.800 |
| DATA_ONLY | total | 1-2 | 10 | 6.53 | 7.10 | 0.250 |
| DATA_ONLY | total | 2-3 | 6 | 10.10 | 9.58 | 1.000 |
| DATA_ONLY | total | 3-5 | 7 | 11.28 | 9.43 | 0.000 |
| DATA_ONLY | total | >5 | 2 | 24.81 | 18.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 26 | 8.21 | 8.15 | 0.625 |
| HYBRID_30 | margin | 1-2 | 10 | 14.10 | 13.80 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 29 | 9.98 | 10.02 | 0.667 |
| HYBRID_30 | total | 1-2 | 6 | 10.33 | 9.75 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 36}; DATA_ONLY quality states: {'OK': 36}; close centre status: {'OK': 36}.

## Game-centre accuracy — T-30m (47 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 47 | 4 | 10.79 | 13.47 | 1.53 | 10.78 | 14.11 | -1.56 | 0.238 |
| DATA_ONLY | 47 | 4 | 11.44 | 14.03 | 1.06 | 11.59 | 14.92 | -0.43 | 0.259 |
| HYBRID_30 | 47 | 4 | 10.96 | 13.58 | 1.39 | 10.99 | 14.31 | -1.22 | 0.243 |
| market at snapshot | 47 | 4 | 10.79 | 13.47 | 1.53 | 10.78 | 14.11 | -1.56 | - |
| market at close | 47 | 4 | 10.81 | 13.46 | 1.55 | 10.89 | 14.25 | -1.51 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 47 | margin | 0.650 | 0.404 | [-0.142, 1.443] | 0.404 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 47 | total | 0.809 | 0.369 | [0.085, 1.532] | 0.426 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 47 | margin | 0.173 | 0.122 | [-0.066, 0.411] | 0.447 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 47 | total | 0.209 | 0.114 | [-0.014, 0.432] | 0.468 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 47 | margin | -0.478 | 0.284 | [-1.034, 0.079] | 0.596 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 47 | total | -0.599 | 0.258 | [-1.105, -0.094] | 0.574 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 47 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 47 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 47 | margin | 0.650 | 0.404 | [-0.142, 1.443] | 0.404 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 47 | total | 0.809 | 0.369 | [0.085, 1.532] | 0.426 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 47 | margin | 0.173 | 0.122 | [-0.066, 0.411] | 0.447 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 47 | total | 0.209 | 0.114 | [-0.014, 0.432] | 0.468 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 47 | margin | -0.021 | 0.053 | [-0.124, 0.082] | 0.106 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 47 | total | -0.117 | 0.068 | [-0.251, 0.017] | 0.213 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 47 | margin | 0.629 | 0.405 | [-0.165, 1.423] | 0.383 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 47 | total | 0.692 | 0.379 | [-0.051, 1.434] | 0.426 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 47 | margin | 0.151 | 0.131 | [-0.105, 0.408] | 0.447 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 47 | total | 0.092 | 0.134 | [-0.170, 0.355] | 0.489 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 47 | 6 | 4 | 37 | 0 | 0.600 | 0.404 | 2.34 |
| DATA_ONLY | total | 47 | 8 | 6 | 33 | 0 | 0.571 | 0.426 | 2.05 |
| HYBRID_30 | margin | 47 | 6 | 4 | 37 | 0 | 0.600 | 0.447 | 0.70 |
| HYBRID_30 | total | 47 | 8 | 6 | 33 | 0 | 0.571 | 0.468 | 0.62 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 13 | 8.74 | 8.27 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.04 | 9.62 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.67 | 21.83 | - |
| DATA_ONLY | total | <=1 | 16 | 13.14 | 13.31 | 0.667 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 8 | 6.00 | 6.19 | 0.800 |
| DATA_ONLY | total | 3-5 | 10 | 12.91 | 9.60 | 0.500 |
| DATA_ONLY | total | >5 | 2 | 19.32 | 12.75 | - |
| HYBRID_30 | margin | <=1 | 36 | 9.81 | 9.71 | 0.667 |
| HYBRID_30 | margin | 1-2 | 11 | 14.71 | 14.32 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 38 | 11.00 | 11.03 | 0.583 |
| HYBRID_30 | total | 1-2 | 8 | 9.68 | 8.62 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 47}; DATA_ONLY quality states: {'OK': 47}; close centre status: {'OK': 47}.

## Contract pricing — latest_pregame (3743 contracts, 48 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3743 | 0.1666 | 0.4999 | 0.413 | 0.423 | 3743 | 0.1666 | 0.1667 | 0.1692 |
| DATA_ONLY | 3743 | 0.1780 | 0.5311 | 0.422 | 0.423 | 3743 | 0.1780 | 0.1667 | 0.1692 |
| HYBRID_30 | 3743 | 0.1695 | 0.5076 | 0.413 | 0.423 | 3743 | 0.1695 | 0.1667 | 0.1692 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3743 | 48 | 0.01140 | [0.00247, 0.02055] | 0.01140 | [0.00247, 0.02055] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3743 | 48 | 0.00295 | [0.00024, 0.00586] | 0.00295 | [0.00024, 0.00586] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3743 | 48 | -0.00845 | [-0.01542, -0.00181] | -0.00845 | [-0.01542, -0.00181] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3743 | 48 | - | - | -0.00009 | [-0.00113, 0.00080] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3678 | 48 | - | - | -0.00042 | [-0.00174, 0.00071] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3743 | 48 | - | - | 0.01131 | [0.00222, 0.02054] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3678 | 48 | - | - | 0.01122 | [0.00178, 0.02066] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3743 | 48 | - | - | 0.00286 | [-0.00000, 0.00583] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3678 | 48 | - | - | 0.00262 | [-0.00035, 0.00575] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 192, 'GAME_WINNER': 96, 'SPREAD': 1233, 'TEAM_TOTAL': 1310, 'TOTAL': 912}; settlement: {'SETTLED': 3743}; close: {'OK': 3678, 'OK_STALE': 65}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 584 / 0.055 / 0.050 | 558 / 0.054 / 0.070 | 572 / 0.053 / 0.059 |
| 0.10-0.20 | 602 / 0.145 / 0.188 | 585 / 0.145 / 0.197 | 602 / 0.146 / 0.188 |
| 0.20-0.30 | 436 / 0.248 / 0.282 | 450 / 0.249 / 0.298 | 434 / 0.248 / 0.274 |
| 0.30-0.40 | 378 / 0.351 / 0.365 | 378 / 0.349 / 0.378 | 382 / 0.348 / 0.369 |
| 0.40-0.50 | 388 / 0.450 / 0.474 | 366 / 0.448 / 0.464 | 422 / 0.449 / 0.498 |
| 0.50-0.60 | 358 / 0.546 / 0.556 | 331 / 0.551 / 0.517 | 339 / 0.549 / 0.540 |
| 0.60-0.70 | 244 / 0.650 / 0.607 | 297 / 0.648 / 0.549 | 245 / 0.648 / 0.588 |
| 0.70-0.80 | 191 / 0.750 / 0.738 | 198 / 0.750 / 0.692 | 198 / 0.751 / 0.702 |
| 0.80-0.90 | 197 / 0.849 / 0.853 | 200 / 0.851 / 0.815 | 193 / 0.853 / 0.870 |
| 0.90-1.00 | 365 / 0.954 / 0.932 | 380 / 0.956 / 0.916 | 356 / 0.956 / 0.933 |

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

## Contract pricing — T-6h (2266 contracts, 29 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2266 | 0.1617 | 0.4851 | 0.412 | 0.424 | 2266 | 0.1617 | 0.1620 | 0.1650 |
| DATA_ONLY | 2266 | 0.1674 | 0.4999 | 0.422 | 0.424 | 2266 | 0.1674 | 0.1620 | 0.1650 |
| HYBRID_30 | 2266 | 0.1625 | 0.4877 | 0.412 | 0.424 | 2266 | 0.1625 | 0.1620 | 0.1650 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2266 | 29 | 0.00576 | [-0.00607, 0.01741] | 0.00576 | [-0.00607, 0.01741] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2266 | 29 | 0.00078 | [-0.00229, 0.00380] | 0.00078 | [-0.00229, 0.00380] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2266 | 29 | -0.00498 | [-0.01422, 0.00453] | -0.00498 | [-0.01422, 0.00453] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2266 | 29 | - | - | -0.00035 | [-0.00153, 0.00075] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2212 | 29 | - | - | -0.00024 | [-0.00193, 0.00144] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2266 | 29 | - | - | 0.00541 | [-0.00659, 0.01748] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2212 | 29 | - | - | 0.00573 | [-0.00651, 0.01771] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2266 | 29 | - | - | 0.00043 | [-0.00284, 0.00367] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2212 | 29 | - | - | 0.00061 | [-0.00279, 0.00396] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 116, 'GAME_WINNER': 58, 'SPREAD': 746, 'TEAM_TOTAL': 795, 'TOTAL': 551}; settlement: {'SETTLED': 2266}; close: {'OK': 2212, 'OK_STALE': 54}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 362 / 0.055 / 0.061 | 351 / 0.054 / 0.051 | 355 / 0.054 / 0.056 |
| 0.10-0.20 | 357 / 0.144 / 0.174 | 350 / 0.147 / 0.174 | 354 / 0.146 / 0.175 |
| 0.20-0.30 | 266 / 0.249 / 0.267 | 264 / 0.250 / 0.284 | 273 / 0.250 / 0.260 |
| 0.30-0.40 | 232 / 0.351 / 0.366 | 227 / 0.349 / 0.405 | 224 / 0.349 / 0.397 |
| 0.40-0.50 | 235 / 0.450 / 0.489 | 217 / 0.446 / 0.447 | 259 / 0.449 / 0.475 |
| 0.50-0.60 | 217 / 0.545 / 0.525 | 199 / 0.548 / 0.533 | 204 / 0.549 / 0.529 |
| 0.60-0.70 | 146 / 0.652 / 0.623 | 184 / 0.646 / 0.571 | 143 / 0.647 / 0.608 |
| 0.70-0.80 | 111 / 0.754 / 0.766 | 122 / 0.751 / 0.713 | 119 / 0.749 / 0.748 |
| 0.80-0.90 | 124 / 0.851 / 0.887 | 123 / 0.849 / 0.837 | 121 / 0.851 / 0.884 |
| 0.90-1.00 | 216 / 0.956 / 0.949 | 229 / 0.956 / 0.943 | 214 / 0.955 / 0.953 |

## Contract pricing — T-90m (2808 contracts, 36 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2808 | 0.1609 | 0.4865 | 0.415 | 0.401 | 2808 | 0.1609 | 0.1603 | 0.1629 |
| DATA_ONLY | 2808 | 0.1665 | 0.5014 | 0.421 | 0.401 | 2808 | 0.1665 | 0.1603 | 0.1629 |
| HYBRID_30 | 2808 | 0.1632 | 0.4901 | 0.412 | 0.401 | 2808 | 0.1632 | 0.1603 | 0.1629 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2808 | 36 | 0.00555 | [-0.00545, 0.01670] | 0.00555 | [-0.00545, 0.01670] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2808 | 36 | 0.00228 | [-0.00113, 0.00576] | 0.00228 | [-0.00113, 0.00576] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2808 | 36 | -0.00327 | [-0.01202, 0.00514] | -0.00327 | [-0.01202, 0.00514] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2808 | 36 | - | - | 0.00066 | [-0.00078, 0.00202] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2751 | 36 | - | - | 0.00069 | [-0.00109, 0.00244] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2808 | 36 | - | - | 0.00621 | [-0.00483, 0.01766] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2751 | 36 | - | - | 0.00640 | [-0.00482, 0.01806] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2808 | 36 | - | - | 0.00294 | [-0.00071, 0.00656] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2751 | 36 | - | - | 0.00306 | [-0.00095, 0.00686] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 144, 'GAME_WINNER': 72, 'SPREAD': 926, 'TEAM_TOTAL': 982, 'TOTAL': 684}; settlement: {'SETTLED': 2808}; close: {'OK': 2751, 'OK_STALE': 57}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 438 / 0.054 / 0.032 | 429 / 0.054 / 0.042 | 440 / 0.053 / 0.036 |
| 0.10-0.20 | 444 / 0.144 / 0.158 | 433 / 0.145 / 0.162 | 443 / 0.146 / 0.160 |
| 0.20-0.30 | 327 / 0.247 / 0.266 | 338 / 0.250 / 0.275 | 335 / 0.249 / 0.269 |
| 0.30-0.40 | 284 / 0.350 / 0.324 | 282 / 0.350 / 0.337 | 276 / 0.349 / 0.362 |
| 0.40-0.50 | 282 / 0.450 / 0.433 | 273 / 0.447 / 0.418 | 322 / 0.449 / 0.457 |
| 0.50-0.60 | 278 / 0.545 / 0.543 | 246 / 0.549 / 0.508 | 243 / 0.549 / 0.494 |
| 0.60-0.70 | 189 / 0.651 / 0.561 | 225 / 0.647 / 0.556 | 186 / 0.648 / 0.554 |
| 0.70-0.80 | 140 / 0.751 / 0.729 | 152 / 0.748 / 0.691 | 148 / 0.749 / 0.696 |
| 0.80-0.90 | 155 / 0.849 / 0.845 | 151 / 0.851 / 0.834 | 147 / 0.852 / 0.857 |
| 0.90-1.00 | 271 / 0.955 / 0.923 | 279 / 0.956 / 0.910 | 268 / 0.956 / 0.929 |

## Contract pricing — T-30m (3666 contracts, 47 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3666 | 0.1672 | 0.5016 | 0.412 | 0.418 | 3666 | 0.1672 | 0.1673 | 0.1699 |
| DATA_ONLY | 3666 | 0.1775 | 0.5300 | 0.422 | 0.418 | 3666 | 0.1775 | 0.1673 | 0.1699 |
| HYBRID_30 | 3666 | 0.1697 | 0.5083 | 0.412 | 0.418 | 3666 | 0.1697 | 0.1673 | 0.1699 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3666 | 47 | 0.01034 | [0.00129, 0.02033] | 0.01034 | [0.00129, 0.02033] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3666 | 47 | 0.00250 | [-0.00024, 0.00528] | 0.00250 | [-0.00024, 0.00528] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3666 | 47 | -0.00784 | [-0.01575, -0.00095] | -0.00784 | [-0.01575, -0.00095] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3666 | 47 | - | - | -0.00010 | [-0.00115, 0.00076] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3601 | 47 | - | - | -0.00044 | [-0.00170, 0.00067] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3666 | 47 | - | - | 0.01024 | [0.00096, 0.02031] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3601 | 47 | - | - | 0.01013 | [0.00064, 0.02038] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3666 | 47 | - | - | 0.00239 | [-0.00043, 0.00541] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3601 | 47 | - | - | 0.00214 | [-0.00088, 0.00533] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 188, 'GAME_WINNER': 94, 'SPREAD': 1208, 'TEAM_TOTAL': 1283, 'TOTAL': 893}; settlement: {'SETTLED': 3666}; close: {'OK': 3601, 'OK_STALE': 65}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 577 / 0.055 / 0.050 | 548 / 0.053 / 0.068 | 564 / 0.053 / 0.060 |
| 0.10-0.20 | 589 / 0.145 / 0.185 | 572 / 0.145 / 0.194 | 588 / 0.146 / 0.185 |
| 0.20-0.30 | 427 / 0.248 / 0.283 | 440 / 0.249 / 0.293 | 426 / 0.249 / 0.270 |
| 0.30-0.40 | 371 / 0.351 / 0.361 | 371 / 0.349 / 0.372 | 376 / 0.348 / 0.367 |
| 0.40-0.50 | 386 / 0.450 / 0.469 | 355 / 0.448 / 0.451 | 412 / 0.449 / 0.485 |
| 0.50-0.60 | 347 / 0.546 / 0.542 | 326 / 0.550 / 0.509 | 333 / 0.549 / 0.532 |
| 0.60-0.70 | 236 / 0.650 / 0.593 | 293 / 0.648 / 0.543 | 239 / 0.648 / 0.577 |
| 0.70-0.80 | 189 / 0.750 / 0.735 | 194 / 0.750 / 0.686 | 196 / 0.751 / 0.699 |
| 0.80-0.90 | 191 / 0.848 / 0.848 | 196 / 0.851 / 0.811 | 187 / 0.853 / 0.866 |
| 0.90-1.00 | 353 / 0.954 / 0.929 | 371 / 0.956 / 0.914 | 345 / 0.955 / 0.930 |

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
| T-6h | DATA_ONLY | margin | 29 | 5 | 6 | 2 | 16 | 0 | 0.750 [0.409, 0.929] | 0.375 | 0.417 | 0.10 |
| T-6h | DATA_ONLY | total | 29 | 9 | 5 | 4 | 11 | 0 | 0.556 [0.267, 0.811] | 0.450 | 0.450 | -0.03 |
| T-6h | HYBRID_30 (derived) | margin | 29 | 21 | 1 | 1 | 6 | 0 | 0.500 [0.095, 0.905] | 0.375 | 0.375 | 0.00 |
| T-6h | HYBRID_30 (derived) | total | 29 | 24 | 2 | 0 | 3 | 0 | 1.000 [0.342, 1.000] | 0.400 | 0.200 | 0.40 |
| T-90m | DATA_ONLY | margin | 36 | 6 | 5 | 2 | 23 | 0 | 0.714 [0.359, 0.918] | 0.400 | 0.400 | 0.02 |
| T-90m | DATA_ONLY | total | 36 | 11 | 4 | 6 | 15 | 0 | 0.400 [0.168, 0.687] | 0.400 | 0.400 | -0.12 |
| T-90m | HYBRID_30 (derived) | margin | 36 | 26 | 0 | 1 | 9 | 0 | 0.000 [0.000, 0.793] | 0.400 | 0.400 | -0.10 |
| T-90m | HYBRID_30 (derived) | total | 36 | 29 | 0 | 3 | 4 | 0 | 0.000 [0.000, 0.561] | 0.286 | 0.286 | -0.36 |
| T-30m | DATA_ONLY | margin | 47 | 9 | 5 | 2 | 31 | 0 | 0.714 [0.359, 0.918] | 0.342 | 0.342 | 0.05 |
| T-30m | DATA_ONLY | total | 47 | 16 | 6 | 5 | 20 | 0 | 0.545 [0.280, 0.787] | 0.355 | 0.355 | -0.05 |
| T-30m | HYBRID_30 (derived) | margin | 47 | 36 | 0 | 1 | 10 | 0 | 0.000 [0.000, 0.793] | 0.364 | 0.364 | -0.09 |
| T-30m | HYBRID_30 (derived) | total | 47 | 38 | 1 | 1 | 7 | 0 | 0.500 [0.095, 0.905] | 0.111 | 0.111 | 0.00 |
| latest_pregame | DATA_ONLY | margin | 48 | 9 | 5 | 2 | 32 | 0 | 0.714 [0.359, 0.918] | 0.333 | 0.333 | 0.05 |
| latest_pregame | DATA_ONLY | total | 48 | 16 | 6 | 5 | 21 | 0 | 0.545 [0.280, 0.787] | 0.344 | 0.344 | -0.05 |
| latest_pregame | HYBRID_30 (derived) | margin | 48 | 37 | 0 | 1 | 10 | 0 | 0.000 [0.000, 0.793] | 0.364 | 0.364 | -0.09 |
| latest_pregame | HYBRID_30 (derived) | total | 48 | 38 | 1 | 1 | 8 | 0 | 0.500 [0.095, 0.905] | 0.100 | 0.100 | 0.00 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 9 | 1 | 2 | 6 | 0 | 0.333 |
| margin | 1-2 | 14 | 3 | 0 | 11 | 0 | 1.000 |
| margin | 2-3 | 12 | 2 | 1 | 9 | 0 | 0.667 |
| margin | 3-5 | 10 | 0 | 1 | 9 | 0 | 0.000 |
| margin | >5 | 3 | 0 | 0 | 3 | 0 | - |
| total | <=1 | 16 | 2 | 1 | 13 | 0 | 0.667 |
| total | 1-2 | 11 | 1 | 3 | 7 | 0 | 0.250 |
| total | 2-3 | 8 | 4 | 1 | 3 | 0 | 0.800 |
| total | 3-5 | 10 | 1 | 1 | 8 | 0 | 0.500 |
| total | >5 | 3 | 0 | 0 | 3 | 0 | - |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 17 | 3 | 0.667 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 17 | 4 | 0.500 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

3043 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

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
| 2026_04_PIT_CLE | Raheim Sanders | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.1 | 2 | 0.87 | 3.50 | EXPECTED_ACTIVE | True | -0.402 | EFFICIENCY_MISS |
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
| 2026_04_PIT_CLE | Quinshon Judkins | receiving_yards | 8.0 | 0–35 | 43 | 5.27 | 0.96 | 1.7 | 7 | 4.83 | 6.14 | EXPECTED_ACTIVE | True | 0.213 | OPPORTUNITY_MISS |
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

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 535, 'OPPORTUNITY_MISS': 1018, 'TEAM_VOLUME_MISS': 174, 'UNEXPLAINED_VARIANCE': 93, 'NO_LARGE_MISS': 1144, 'INSUFFICIENT_DATA': 40, 'AVAILABILITY_MISS': 39}.
Missing usage (no snap table or stats row): 79.

## Decision funnel (BET / WATCH / PASS accounting of the existing gates; no authority)

101 snapshot(s). A contract's terminal state is where it left the existing gate sequence when the model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).

### Newest snapshot 20261002T125801Z (58604 markets)

| stage | markets |
|---|---|
| discovered | 58604 |
| mapped | 50090 |
| supported | 5713 |
| priced | 5713 |
| raw_disagreement | 4430 |
| tradable_book | 4355 |
| data_quality | 4305 |
| executable_price | 3272 |
| liquidity | 903 |

Terminal states: {'PASS': 56671, 'WATCH': 1030, 'BET': 903}

| family | BET | WATCH | PASS |
|---|---|---|---|
| AWARD | 0 | 0 | 873 |
| BOTH_TEAMS_SCORE | 0 | 0 | 252 |
| BOTH_TEAMS_SCORE_N | 0 | 3 | 249 |
| COACH_EVENT | 0 | 0 | 64 |
| CONFERENCE_WINNER | 0 | 0 | 32 |
| DIVISION_WINNER | 0 | 0 | 32 |
| DRAFT | 0 | 0 | 40 |
| FIRST_TD_SCORER | 0 | 0 | 1632 |
| FIRST_TD_TEAM | 0 | 0 | 1841 |
| GAME_EVENT | 0 | 0 | 256 |
| GAME_PLAYER_LEADER | 0 | 0 | 674 |
| GAME_STAT | 0 | 0 | 5 |
| GAME_WINNER | 0 | 26 | 132 |
| HALF_FULL_RESULT | 0 | 0 | 576 |
| MAKE_PLAYOFFS | 0 | 0 | 33 |
| NFL_BUSINESS_EVENT | 0 | 0 | 5 |
| NOT_NFL_OR_UNKNOWN | 0 | 0 | 2 |
| PERIOD_WINNER | 0 | 0 | 1152 |
| PLAYER_AVAILABILITY | 0 | 0 | 23 |
| PLAYER_ROLE_EVENT | 0 | 0 | 177 |
| PLAYER_STAT | 788 | 489 | 22917 |
| RACE_TO_N | 0 | 0 | 990 |
| SEASON_DIVISION_ORDER | 0 | 0 | 192 |
| SEASON_DIVISION_STAT | 0 | 0 | 80 |
| SEASON_FANTASY | 0 | 0 | 1166 |
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
| SPREAD | 59 | 208 | 6523 |
| SUPER_BOWL_EVENT | 0 | 0 | 263 |
| SUPER_BOWL_WINNER | 0 | 0 | 32 |
| TEAM_STAT | 0 | 0 | 1546 |
| TEAM_TOTAL | 38 | 141 | 3012 |
| TEAM_WINS_BY_WEEK | 0 | 0 | 728 |
| TOTAL | 18 | 163 | 5423 |
| TOTAL_TD | 0 | 0 | 214 |
| TRANSACTION_EVENT | 0 | 0 | 314 |
| UNKNOWN_NEEDS_CLASSIFICATION | 0 | 0 | 386 |
| WEEK_EVENT | 0 | 0 | 32 |
| WEEK_LEADER | 0 | 0 | 482 |
| WIN_MARGIN_BUCKET | 0 | 0 | 441 |

| rejection reason | n |
|---|---|
| POST_KICKOFF_EXCLUDED | 35483 |
| unmapped | 8514 |
| UNSUPPORTED_MODEL | 5420 |
| UNSUPPORTED_RULES | 3355 |
| no order book observed for this ticker (books are captured i | 2368 |
| no positive disagreement against either executable ask | 1283 |
| UNSUPPORTED_IDENTITY | 119 |
| ask 0.99 above the zero-net-EV ceiling 0.98 | 118 |
| book not tradable for ranking | 75 |
| ask 0.98 above the zero-net-EV ceiling 0.97 | 52 |
| ask 0.97 above the zero-net-EV ceiling 0.96 | 43 |
| availability DOUBTFUL unresolved inside T-90m | 32 |
| ask 0.96 above the zero-net-EV ceiling 0.95 | 22 |
| ask 0.95 above the zero-net-EV ceiling 0.94 | 19 |
| ask 0.07 above the zero-net-EV ceiling 0.06 | 19 |

WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee schedule (`watch_ceiling`). Not replayed: ['portfolio_risk_policy (needs a stake and bankroll)', "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own confirmation is the STALE_DATA support state)"].

Across all 101 snapshots (repeated markets counted per snapshot): {'PASS': 3554445, 'WATCH': 73759, 'BET': 60801}.

