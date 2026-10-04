# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 49 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 2663 | 49 | 4 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 23 | 23 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 30 | 30 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 37 | 37 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 48 | 48 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 49 | 49 | 4 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_IND_WAS | 2026-10-04T13:30 | 38 | CURRENT | -4.50 | 46.50 | -17 | 43 | -4.5/46.5 (kalshi_implied) | -4.5/46.5 (OK) |
|  |  |  | DATA_ONLY | -2.33 | 47.43 |  |  |  |  |
|  |  |  | HYBRID_30 | -3.85 | 46.78 |  |  |  |  |

## Game-centre accuracy — latest_pregame (49 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 49 | 4 | 10.69 | 13.33 | 1.63 | 10.77 | 14.05 | -1.79 | 0.233 |
| DATA_ONLY | 49 | 4 | 11.40 | 13.92 | 1.19 | 11.67 | 14.99 | -0.79 | 0.254 |
| HYBRID_30 | 49 | 4 | 10.88 | 13.45 | 1.50 | 11.01 | 14.29 | -1.49 | 0.238 |
| market at snapshot | 49 | 4 | 10.69 | 13.33 | 1.63 | 10.77 | 14.05 | -1.79 | - |
| market at close | 49 | 4 | 10.71 | 13.32 | 1.65 | 10.88 | 14.19 | -1.73 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 49 | margin | 0.704 | 0.389 | [-0.059, 1.467] | 0.388 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 49 | total | 0.908 | 0.367 | [0.189, 1.626] | 0.408 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 49 | margin | 0.190 | 0.117 | [-0.040, 0.420] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 49 | total | 0.240 | 0.113 | [0.019, 0.462] | 0.449 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 49 | margin | -0.514 | 0.274 | [-1.050, 0.022] | 0.612 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 49 | total | -0.667 | 0.256 | [-1.169, -0.165] | 0.592 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 49 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 49 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 49 | margin | 0.704 | 0.389 | [-0.059, 1.467] | 0.388 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 49 | total | 0.908 | 0.367 | [0.189, 1.626] | 0.408 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 49 | margin | 0.190 | 0.117 | [-0.040, 0.420] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 49 | total | 0.240 | 0.113 | [0.019, 0.462] | 0.449 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 49 | margin | -0.020 | 0.050 | [-0.119, 0.078] | 0.102 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 49 | total | -0.112 | 0.066 | [-0.241, 0.016] | 0.204 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 49 | margin | 0.684 | 0.390 | [-0.081, 1.448] | 0.367 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 49 | total | 0.795 | 0.376 | [0.057, 1.533] | 0.408 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 49 | margin | 0.169 | 0.126 | [-0.078, 0.416] | 0.429 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 49 | total | 0.128 | 0.132 | [-0.132, 0.388] | 0.469 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 49 | 6 | 4 | 39 | 0 | 0.600 | 0.388 | 2.32 |
| DATA_ONLY | total | 49 | 8 | 6 | 35 | 0 | 0.571 | 0.408 | 2.10 |
| HYBRID_30 | margin | 49 | 6 | 4 | 39 | 0 | 0.600 | 0.429 | 0.70 |
| HYBRID_30 | total | 49 | 8 | 6 | 35 | 0 | 0.571 | 0.449 | 0.63 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 14 | 8.56 | 8.00 | 1.000 |
| DATA_ONLY | margin | 2-3 | 13 | 10.40 | 9.85 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.67 | 21.83 | - |
| DATA_ONLY | total | <=1 | 17 | 12.63 | 12.74 | 0.667 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 8 | 6.00 | 6.19 | 0.800 |
| DATA_ONLY | total | 3-5 | 10 | 12.91 | 9.60 | 0.500 |
| DATA_ONLY | total | >5 | 3 | 20.56 | 14.33 | - |
| HYBRID_30 | margin | <=1 | 38 | 9.78 | 9.64 | 0.667 |
| HYBRID_30 | margin | 1-2 | 11 | 14.71 | 14.32 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 39 | 10.81 | 10.83 | 0.583 |
| HYBRID_30 | total | 1-2 | 9 | 10.73 | 9.61 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 49}; DATA_ONLY quality states: {'OK': 49}; close centre status: {'OK': 49}.

## Game-centre accuracy — T-24h (23 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 23 | 4 | 11.52 | 13.82 | 2.39 | 10.24 | 12.87 | 2.07 | 0.236 |
| DATA_ONLY | 23 | 4 | 12.11 | 14.41 | 1.53 | 10.38 | 13.44 | 2.54 | 0.246 |
| HYBRID_30 | 23 | 4 | 11.70 | 13.92 | 2.13 | 10.23 | 12.98 | 2.21 | 0.238 |
| market at snapshot | 23 | 4 | 11.52 | 13.82 | 2.39 | 10.24 | 12.87 | 2.07 | - |
| market at close | 23 | 4 | 11.54 | 13.80 | 2.59 | 10.00 | 12.80 | 1.87 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 23 | margin | 0.591 | 0.680 | [-0.741, 1.923] | 0.391 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 23 | total | 0.138 | 0.548 | [-0.936, 1.212] | 0.565 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 23 | margin | 0.177 | 0.204 | [-0.222, 0.577] | 0.391 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 23 | total | -0.008 | 0.172 | [-0.345, 0.329] | 0.565 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 23 | margin | -0.414 | 0.476 | [-1.346, 0.519] | 0.609 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 23 | total | -0.145 | 0.383 | [-0.895, 0.604] | 0.478 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 23 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 23 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 23 | margin | 0.591 | 0.680 | [-0.741, 1.923] | 0.391 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 23 | total | 0.138 | 0.548 | [-0.936, 1.212] | 0.565 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 23 | margin | 0.177 | 0.204 | [-0.222, 0.577] | 0.391 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 23 | total | -0.008 | 0.172 | [-0.345, 0.329] | 0.565 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 23 | margin | -0.022 | 0.097 | [-0.211, 0.168] | 0.174 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 23 | total | 0.239 | 0.160 | [-0.074, 0.553] | 0.087 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 23 | margin | 0.569 | 0.681 | [-0.765, 1.903] | 0.391 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 23 | total | 0.377 | 0.477 | [-0.559, 1.312] | 0.391 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 23 | margin | 0.156 | 0.220 | [-0.276, 0.587] | 0.435 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 23 | total | 0.231 | 0.151 | [-0.065, 0.528] | 0.304 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 23 | 2 | 6 | 15 | 0 | 0.250 | 0.391 | 2.59 |
| DATA_ONLY | total | 23 | 10 | 1 | 12 | 0 | 0.909 | 0.565 | 2.31 |
| HYBRID_30 | margin | 23 | 2 | 6 | 15 | 0 | 0.250 | 0.391 | 0.78 |
| HYBRID_30 | total | 23 | 10 | 1 | 12 | 0 | 0.909 | 0.565 | 0.69 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 6 | 8.73 | 8.75 | 0.000 |
| DATA_ONLY | margin | 1-2 | 4 | 6.52 | 5.88 | 1.000 |
| DATA_ONLY | margin | 2-3 | 5 | 11.79 | 11.20 | - |
| DATA_ONLY | margin | 3-5 | 5 | 14.03 | 13.20 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.69 | 22.33 | 0.500 |
| DATA_ONLY | total | <=1 | 5 | 9.38 | 9.80 | 1.000 |
| DATA_ONLY | total | 1-2 | 4 | 9.99 | 9.38 | 0.000 |
| DATA_ONLY | total | 2-3 | 7 | 9.24 | 9.86 | 1.000 |
| DATA_ONLY | total | 3-5 | 6 | 12.33 | 12.08 | 1.000 |
| DATA_ONLY | total | >5 | 1 | 13.14 | 7.50 | 1.000 |
| HYBRID_30 | margin | <=1 | 16 | 9.08 | 9.03 | 0.167 |
| HYBRID_30 | margin | 1-2 | 6 | 16.93 | 16.00 | 0.000 |
| HYBRID_30 | margin | 2-3 | 1 | 22.29 | 24.50 | 1.000 |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 19 | 9.99 | 10.16 | 0.900 |
| HYBRID_30 | total | 1-2 | 4 | 11.36 | 10.62 | 1.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 23}; DATA_ONLY quality states: {'OK': 23}; close centre status: {'OK': 23}.

## Game-centre accuracy — T-6h (30 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 30 | 4 | 10.28 | 13.14 | 0.15 | 9.22 | 11.10 | -2.18 | 0.254 |
| DATA_ONLY | 30 | 4 | 10.78 | 13.22 | -0.33 | 9.80 | 12.02 | -1.19 | 0.257 |
| HYBRID_30 | 30 | 4 | 10.43 | 13.09 | 0.01 | 9.31 | 11.31 | -1.88 | 0.253 |
| market at snapshot | 30 | 4 | 10.28 | 13.14 | 0.15 | 9.22 | 11.10 | -2.18 | - |
| market at close | 30 | 4 | 10.28 | 13.13 | 0.18 | 9.38 | 11.28 | -2.18 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 30 | margin | 0.496 | 0.552 | [-0.586, 1.578] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 30 | total | 0.579 | 0.480 | [-0.361, 1.519] | 0.433 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 30 | margin | 0.149 | 0.166 | [-0.176, 0.473] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 30 | total | 0.098 | 0.142 | [-0.180, 0.377] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 30 | margin | -0.347 | 0.386 | [-1.105, 0.410] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 30 | total | -0.481 | 0.350 | [-1.167, 0.206] | 0.567 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 30 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 30 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 30 | margin | 0.496 | 0.552 | [-0.586, 1.578] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 30 | total | 0.579 | 0.480 | [-0.361, 1.519] | 0.433 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 30 | margin | 0.149 | 0.166 | [-0.176, 0.473] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 30 | total | 0.098 | 0.142 | [-0.180, 0.377] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 30 | margin | 0.000 | 0.110 | [-0.215, 0.215] | 0.167 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 30 | total | -0.167 | 0.145 | [-0.450, 0.117] | 0.267 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 30 | margin | 0.496 | 0.538 | [-0.557, 1.550] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 30 | total | 0.413 | 0.500 | [-0.568, 1.393] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 30 | margin | 0.149 | 0.176 | [-0.197, 0.495] | 0.367 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 30 | total | -0.068 | 0.196 | [-0.452, 0.315] | 0.533 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 30 | 7 | 3 | 20 | 0 | 0.700 | 0.400 | 2.48 |
| DATA_ONLY | total | 30 | 8 | 5 | 17 | 0 | 0.615 | 0.433 | 2.09 |
| HYBRID_30 | margin | 30 | 7 | 3 | 20 | 0 | 0.700 | 0.400 | 0.75 |
| HYBRID_30 | total | 30 | 8 | 5 | 17 | 0 | 0.615 | 0.500 | 0.63 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 5 | 11.29 | 11.50 | 0.500 |
| DATA_ONLY | margin | 1-2 | 10 | 9.51 | 8.85 | 0.667 |
| DATA_ONLY | margin | 2-3 | 6 | 10.98 | 10.25 | 1.000 |
| DATA_ONLY | margin | 3-5 | 6 | 9.07 | 9.08 | 0.500 |
| DATA_ONLY | margin | >5 | 3 | 17.19 | 15.50 | 1.000 |
| DATA_ONLY | total | <=1 | 10 | 8.68 | 8.65 | 0.750 |
| DATA_ONLY | total | 1-2 | 9 | 9.61 | 9.94 | 0.600 |
| DATA_ONLY | total | 2-3 | 5 | 7.20 | 7.70 | 0.000 |
| DATA_ONLY | total | 3-5 | 3 | 13.15 | 11.83 | - |
| DATA_ONLY | total | >5 | 3 | 15.04 | 8.83 | 1.000 |
| HYBRID_30 | margin | <=1 | 22 | 9.82 | 9.73 | 0.750 |
| HYBRID_30 | margin | 1-2 | 8 | 12.12 | 11.81 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 25 | 9.27 | 9.32 | 0.545 |
| HYBRID_30 | total | 1-2 | 4 | 6.71 | 6.25 | 1.000 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 30}; DATA_ONLY quality states: {'OK': 30}; close centre status: {'OK': 30}.

## Game-centre accuracy — T-90m (37 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 37 | 4 | 9.80 | 12.42 | 0.58 | 10.05 | 12.65 | -0.05 | 0.246 |
| DATA_ONLY | 37 | 4 | 10.28 | 12.78 | 0.02 | 10.63 | 13.39 | 0.69 | 0.253 |
| HYBRID_30 | 37 | 4 | 9.93 | 12.45 | 0.41 | 10.18 | 12.82 | 0.17 | 0.246 |
| market at snapshot | 37 | 4 | 9.80 | 12.42 | 0.58 | 10.05 | 12.65 | -0.05 | - |
| market at close | 37 | 4 | 9.81 | 12.42 | 0.57 | 10.07 | 12.62 | -0.15 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 37 | margin | 0.484 | 0.489 | [-0.475, 1.443] | 0.378 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 37 | total | 0.577 | 0.416 | [-0.239, 1.393] | 0.432 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 37 | margin | 0.136 | 0.147 | [-0.153, 0.424] | 0.405 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 37 | total | 0.131 | 0.129 | [-0.122, 0.383] | 0.486 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 37 | margin | -0.349 | 0.342 | [-1.020, 0.323] | 0.622 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 37 | total | -0.446 | 0.291 | [-1.017, 0.125] | 0.568 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 37 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 37 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 37 | margin | 0.484 | 0.489 | [-0.475, 1.443] | 0.378 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 37 | total | 0.577 | 0.416 | [-0.239, 1.393] | 0.432 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 37 | margin | 0.136 | 0.147 | [-0.153, 0.424] | 0.405 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 37 | total | 0.131 | 0.129 | [-0.122, 0.383] | 0.486 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 37 | margin | -0.014 | 0.056 | [-0.124, 0.097] | 0.108 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 37 | total | -0.014 | 0.092 | [-0.194, 0.167] | 0.216 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 37 | margin | 0.471 | 0.489 | [-0.487, 1.428] | 0.378 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 37 | total | 0.563 | 0.441 | [-0.301, 1.428] | 0.405 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 37 | margin | 0.122 | 0.153 | [-0.178, 0.422] | 0.405 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 37 | total | 0.117 | 0.168 | [-0.212, 0.447] | 0.432 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 37 | 5 | 4 | 28 | 0 | 0.556 | 0.378 | 2.48 |
| DATA_ONLY | total | 37 | 8 | 7 | 22 | 0 | 0.533 | 0.432 | 2.08 |
| HYBRID_30 | margin | 37 | 5 | 4 | 28 | 0 | 0.556 | 0.405 | 0.74 |
| HYBRID_30 | total | 37 | 8 | 7 | 22 | 0 | 0.533 | 0.486 | 0.63 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 6 | 6.74 | 6.67 | 0.000 |
| DATA_ONLY | margin | 1-2 | 10 | 7.99 | 7.50 | 1.000 |
| DATA_ONLY | margin | 2-3 | 11 | 10.19 | 9.95 | 0.750 |
| DATA_ONLY | margin | 3-5 | 7 | 11.00 | 10.36 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.67 | 21.83 | - |
| DATA_ONLY | total | <=1 | 12 | 11.58 | 11.71 | 0.800 |
| DATA_ONLY | total | 1-2 | 10 | 6.53 | 7.10 | 0.250 |
| DATA_ONLY | total | 2-3 | 6 | 10.10 | 9.58 | 1.000 |
| DATA_ONLY | total | 3-5 | 7 | 11.28 | 9.43 | 0.000 |
| DATA_ONLY | total | >5 | 2 | 24.81 | 18.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 27 | 8.39 | 8.31 | 0.625 |
| HYBRID_30 | margin | 1-2 | 10 | 14.10 | 13.80 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 30 | 9.77 | 9.80 | 0.667 |
| HYBRID_30 | total | 1-2 | 6 | 10.33 | 9.75 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 37}; DATA_ONLY quality states: {'OK': 37}; close centre status: {'OK': 37}.

## Game-centre accuracy — T-30m (48 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 48 | 4 | 10.82 | 13.45 | 1.76 | 10.62 | 13.97 | -1.46 | 0.235 |
| DATA_ONLY | 48 | 4 | 11.50 | 14.04 | 1.34 | 11.44 | 14.77 | -0.33 | 0.257 |
| HYBRID_30 | 48 | 4 | 11.01 | 13.57 | 1.64 | 10.84 | 14.17 | -1.12 | 0.241 |
| market at snapshot | 48 | 4 | 10.82 | 13.45 | 1.76 | 10.62 | 13.97 | -1.46 | - |
| market at close | 48 | 4 | 10.84 | 13.44 | 1.78 | 10.74 | 14.11 | -1.41 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 48 | margin | 0.682 | 0.397 | [-0.096, 1.460] | 0.396 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 48 | total | 0.811 | 0.361 | [0.103, 1.519] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 48 | margin | 0.183 | 0.120 | [-0.052, 0.417] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 48 | total | 0.211 | 0.112 | [-0.008, 0.429] | 0.458 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 48 | margin | -0.499 | 0.279 | [-1.046, 0.047] | 0.604 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 48 | total | -0.600 | 0.253 | [-1.095, -0.105] | 0.583 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 48 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 48 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 48 | margin | 0.682 | 0.397 | [-0.096, 1.460] | 0.396 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 48 | total | 0.811 | 0.361 | [0.103, 1.519] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 48 | margin | 0.183 | 0.120 | [-0.052, 0.417] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 48 | total | 0.211 | 0.112 | [-0.008, 0.429] | 0.458 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 48 | margin | -0.021 | 0.051 | [-0.122, 0.080] | 0.104 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 48 | total | -0.115 | 0.067 | [-0.246, 0.017] | 0.208 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 48 | margin | 0.661 | 0.398 | [-0.119, 1.441] | 0.375 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 48 | total | 0.697 | 0.371 | [-0.031, 1.424] | 0.417 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 48 | margin | 0.162 | 0.128 | [-0.090, 0.413] | 0.438 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 48 | total | 0.096 | 0.131 | [-0.161, 0.353] | 0.479 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 48 | 6 | 4 | 38 | 0 | 0.600 | 0.396 | 2.33 |
| DATA_ONLY | total | 48 | 8 | 6 | 34 | 0 | 0.571 | 0.417 | 2.03 |
| HYBRID_30 | margin | 48 | 6 | 4 | 38 | 0 | 0.600 | 0.438 | 0.70 |
| HYBRID_30 | total | 48 | 8 | 6 | 34 | 0 | 0.571 | 0.458 | 0.61 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 13 | 8.74 | 8.27 | 1.000 |
| DATA_ONLY | margin | 2-3 | 13 | 10.40 | 9.85 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 3 | 23.67 | 21.83 | - |
| DATA_ONLY | total | <=1 | 17 | 12.63 | 12.74 | 0.667 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 8 | 6.00 | 6.19 | 0.800 |
| DATA_ONLY | total | 3-5 | 10 | 12.91 | 9.60 | 0.500 |
| DATA_ONLY | total | >5 | 2 | 19.32 | 12.75 | - |
| HYBRID_30 | margin | <=1 | 37 | 9.90 | 9.78 | 0.667 |
| HYBRID_30 | margin | 1-2 | 11 | 14.71 | 14.32 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 39 | 10.81 | 10.83 | 0.583 |
| HYBRID_30 | total | 1-2 | 8 | 9.68 | 8.62 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 48}; DATA_ONLY quality states: {'OK': 48}; close centre status: {'OK': 48}.

## Contract pricing — latest_pregame (3819 contracts, 49 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3819 | 0.1661 | 0.4986 | 0.414 | 0.423 | 3819 | 0.1661 | 0.1662 | 0.1687 |
| DATA_ONLY | 3819 | 0.1778 | 0.5304 | 0.422 | 0.423 | 3819 | 0.1778 | 0.1662 | 0.1687 |
| HYBRID_30 | 3819 | 0.1691 | 0.5064 | 0.413 | 0.423 | 3819 | 0.1691 | 0.1662 | 0.1687 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3819 | 49 | 0.01168 | [0.00311, 0.02144] | 0.01168 | [0.00311, 0.02144] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3819 | 49 | 0.00297 | [0.00036, 0.00575] | 0.00297 | [0.00036, 0.00575] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3819 | 49 | -0.00872 | [-0.01630, -0.00180] | -0.00872 | [-0.01630, -0.00180] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3819 | 49 | - | - | -0.00003 | [-0.00104, 0.00090] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3753 | 49 | - | - | -0.00035 | [-0.00163, 0.00078] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3819 | 49 | - | - | 0.01166 | [0.00303, 0.02150] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3753 | 49 | - | - | 0.01157 | [0.00277, 0.02153] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3819 | 49 | - | - | 0.00294 | [0.00025, 0.00587] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3753 | 49 | - | - | 0.00270 | [-0.00019, 0.00576] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 196, 'GAME_WINNER': 98, 'SPREAD': 1258, 'TEAM_TOTAL': 1336, 'TOTAL': 931}; settlement: {'SETTLED': 3819}; close: {'OK': 3753, 'OK_STALE': 66}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 593 / 0.055 / 0.049 | 568 / 0.054 / 0.069 | 583 / 0.053 / 0.058 |
| 0.10-0.20 | 615 / 0.145 / 0.185 | 597 / 0.145 / 0.198 | 615 / 0.146 / 0.189 |
| 0.20-0.30 | 445 / 0.248 / 0.281 | 459 / 0.250 / 0.296 | 443 / 0.249 / 0.273 |
| 0.30-0.40 | 387 / 0.351 / 0.367 | 387 / 0.349 / 0.380 | 390 / 0.348 / 0.367 |
| 0.40-0.50 | 394 / 0.450 / 0.475 | 372 / 0.448 / 0.462 | 430 / 0.449 / 0.495 |
| 0.50-0.60 | 367 / 0.546 / 0.550 | 340 / 0.551 / 0.515 | 345 / 0.549 / 0.539 |
| 0.60-0.70 | 249 / 0.650 / 0.610 | 300 / 0.647 / 0.547 | 251 / 0.649 / 0.594 |
| 0.70-0.80 | 195 / 0.750 / 0.733 | 202 / 0.750 / 0.688 | 201 / 0.751 / 0.697 |
| 0.80-0.90 | 200 / 0.849 / 0.855 | 205 / 0.851 / 0.815 | 196 / 0.853 / 0.872 |
| 0.90-1.00 | 374 / 0.954 / 0.933 | 389 / 0.957 / 0.918 | 365 / 0.956 / 0.934 |

## Contract pricing — T-24h (1792 contracts, 23 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1792 | 0.1706 | 0.5107 | 0.414 | 0.393 | 1792 | 0.1706 | 0.1700 | 0.1709 |
| DATA_ONLY | 1792 | 0.1769 | 0.5289 | 0.418 | 0.393 | 1792 | 0.1769 | 0.1700 | 0.1709 |
| HYBRID_30 | 1792 | 0.1711 | 0.5112 | 0.413 | 0.393 | 1792 | 0.1711 | 0.1700 | 0.1709 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1792 | 23 | 0.00623 | [-0.00905, 0.02237] | 0.00623 | [-0.00905, 0.02237] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1792 | 23 | 0.00049 | [-0.00432, 0.00584] | 0.00049 | [-0.00432, 0.00584] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1792 | 23 | -0.00575 | [-0.01691, 0.00587] | -0.00575 | [-0.01691, 0.00587] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1792 | 23 | - | - | 0.00066 | [-0.00062, 0.00184] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1767 | 23 | - | - | 0.00175 | [-0.00044, 0.00410] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1792 | 23 | - | - | 0.00689 | [-0.00807, 0.02296] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1767 | 23 | - | - | 0.00816 | [-0.00684, 0.02347] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1792 | 23 | - | - | 0.00115 | [-0.00382, 0.00676] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1767 | 23 | - | - | 0.00232 | [-0.00224, 0.00750] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 92, 'GAME_WINNER': 46, 'SPREAD': 593, 'TEAM_TOTAL': 624, 'TOTAL': 437}; settlement: {'SETTLED': 1792}; close: {'OK': 1767, 'OK_STALE': 25}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 283 / 0.056 / 0.025 | 276 / 0.054 / 0.043 | 273 / 0.053 / 0.022 |
| 0.10-0.20 | 281 / 0.146 / 0.164 | 282 / 0.146 / 0.181 | 287 / 0.145 / 0.171 |
| 0.20-0.30 | 212 / 0.248 / 0.302 | 215 / 0.251 / 0.326 | 214 / 0.249 / 0.294 |
| 0.30-0.40 | 175 / 0.349 / 0.349 | 185 / 0.349 / 0.346 | 173 / 0.347 / 0.364 |
| 0.40-0.50 | 190 / 0.449 / 0.437 | 171 / 0.448 / 0.398 | 210 / 0.449 / 0.457 |
| 0.50-0.60 | 164 / 0.545 / 0.494 | 157 / 0.550 / 0.433 | 154 / 0.550 / 0.448 |
| 0.60-0.70 | 122 / 0.647 / 0.541 | 142 / 0.648 / 0.535 | 117 / 0.645 / 0.504 |
| 0.70-0.80 | 99 / 0.749 / 0.697 | 89 / 0.748 / 0.697 | 101 / 0.747 / 0.693 |
| 0.80-0.90 | 90 / 0.850 / 0.778 | 98 / 0.848 / 0.786 | 93 / 0.854 / 0.817 |
| 0.90-1.00 | 176 / 0.954 / 0.892 | 177 / 0.956 / 0.881 | 170 / 0.956 / 0.900 |

## Contract pricing — T-6h (2342 contracts, 30 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2342 | 0.1611 | 0.4834 | 0.413 | 0.423 | 2342 | 0.1611 | 0.1614 | 0.1643 |
| DATA_ONLY | 2342 | 0.1675 | 0.4998 | 0.422 | 0.423 | 2342 | 0.1675 | 0.1614 | 0.1643 |
| HYBRID_30 | 2342 | 0.1620 | 0.4862 | 0.413 | 0.423 | 2342 | 0.1620 | 0.1614 | 0.1643 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2342 | 30 | 0.00641 | [-0.00474, 0.01821] | 0.00641 | [-0.00474, 0.01821] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2342 | 30 | 0.00087 | [-0.00199, 0.00352] | 0.00087 | [-0.00199, 0.00352] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2342 | 30 | -0.00554 | [-0.01525, 0.00358] | -0.00554 | [-0.01525, 0.00358] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2342 | 30 | - | - | -0.00029 | [-0.00148, 0.00076] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2287 | 30 | - | - | -0.00016 | [-0.00184, 0.00151] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2342 | 30 | - | - | 0.00612 | [-0.00564, 0.01848] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2287 | 30 | - | - | 0.00647 | [-0.00560, 0.01874] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2342 | 30 | - | - | 0.00058 | [-0.00256, 0.00335] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2287 | 30 | - | - | 0.00079 | [-0.00260, 0.00381] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 120, 'GAME_WINNER': 60, 'SPREAD': 771, 'TEAM_TOTAL': 821, 'TOTAL': 570}; settlement: {'SETTLED': 2342}; close: {'OK': 2287, 'OK_STALE': 55}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 372 / 0.055 / 0.059 | 361 / 0.054 / 0.050 | 366 / 0.054 / 0.055 |
| 0.10-0.20 | 369 / 0.144 / 0.171 | 362 / 0.147 / 0.177 | 367 / 0.146 / 0.177 |
| 0.20-0.30 | 275 / 0.249 / 0.265 | 274 / 0.251 / 0.281 | 282 / 0.250 / 0.259 |
| 0.30-0.40 | 241 / 0.351 / 0.369 | 235 / 0.350 / 0.409 | 232 / 0.349 / 0.392 |
| 0.40-0.50 | 242 / 0.450 / 0.488 | 223 / 0.446 / 0.444 | 267 / 0.449 / 0.472 |
| 0.50-0.60 | 225 / 0.545 / 0.520 | 208 / 0.548 / 0.529 | 210 / 0.549 / 0.529 |
| 0.60-0.70 | 151 / 0.652 / 0.629 | 187 / 0.646 / 0.567 | 149 / 0.648 / 0.617 |
| 0.70-0.80 | 115 / 0.754 / 0.757 | 127 / 0.751 / 0.709 | 122 / 0.750 / 0.738 |
| 0.80-0.90 | 127 / 0.851 / 0.890 | 127 / 0.849 / 0.835 | 123 / 0.850 / 0.886 |
| 0.90-1.00 | 225 / 0.955 / 0.951 | 238 / 0.956 / 0.945 | 224 / 0.955 / 0.955 |

## Contract pricing — T-90m (2884 contracts, 37 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2884 | 0.1605 | 0.4851 | 0.415 | 0.401 | 2884 | 0.1605 | 0.1598 | 0.1624 |
| DATA_ONLY | 2884 | 0.1666 | 0.5012 | 0.421 | 0.401 | 2884 | 0.1666 | 0.1598 | 0.1624 |
| HYBRID_30 | 2884 | 0.1628 | 0.4889 | 0.413 | 0.401 | 2884 | 0.1628 | 0.1598 | 0.1624 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2884 | 37 | 0.00608 | [-0.00469, 0.01708] | 0.00608 | [-0.00469, 0.01708] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2884 | 37 | 0.00234 | [-0.00113, 0.00565] | 0.00234 | [-0.00113, 0.00565] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2884 | 37 | -0.00375 | [-0.01247, 0.00438] | -0.00375 | [-0.01247, 0.00438] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2884 | 37 | - | - | 0.00070 | [-0.00059, 0.00212] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2826 | 37 | - | - | 0.00073 | [-0.00102, 0.00248] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2884 | 37 | - | - | 0.00678 | [-0.00435, 0.01831] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2826 | 37 | - | - | 0.00698 | [-0.00413, 0.01867] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2884 | 37 | - | - | 0.00304 | [-0.00054, 0.00646] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2826 | 37 | - | - | 0.00316 | [-0.00046, 0.00662] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 148, 'GAME_WINNER': 74, 'SPREAD': 951, 'TEAM_TOTAL': 1008, 'TOTAL': 703}; settlement: {'SETTLED': 2884}; close: {'OK': 2826, 'OK_STALE': 58}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 448 / 0.055 / 0.031 | 439 / 0.054 / 0.041 | 451 / 0.053 / 0.035 |
| 0.10-0.20 | 456 / 0.144 / 0.156 | 445 / 0.146 / 0.164 | 456 / 0.146 / 0.162 |
| 0.20-0.30 | 336 / 0.247 / 0.265 | 347 / 0.250 / 0.274 | 344 / 0.249 / 0.267 |
| 0.30-0.40 | 293 / 0.349 / 0.328 | 291 / 0.350 / 0.340 | 284 / 0.349 / 0.359 |
| 0.40-0.50 | 288 / 0.450 / 0.431 | 279 / 0.447 / 0.416 | 330 / 0.449 / 0.455 |
| 0.50-0.60 | 287 / 0.546 / 0.540 | 255 / 0.549 / 0.506 | 249 / 0.549 / 0.494 |
| 0.60-0.70 | 194 / 0.651 / 0.567 | 228 / 0.646 / 0.553 | 192 / 0.649 / 0.562 |
| 0.70-0.80 | 144 / 0.751 / 0.722 | 157 / 0.748 / 0.688 | 150 / 0.749 / 0.693 |
| 0.80-0.90 | 159 / 0.850 / 0.849 | 155 / 0.851 / 0.832 | 151 / 0.852 / 0.854 |
| 0.90-1.00 | 279 / 0.955 / 0.925 | 288 / 0.956 / 0.913 | 277 / 0.956 / 0.931 |

## Contract pricing — T-30m (3742 contracts, 48 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3742 | 0.1667 | 0.5002 | 0.412 | 0.417 | 3742 | 0.1667 | 0.1668 | 0.1693 |
| DATA_ONLY | 3742 | 0.1774 | 0.5293 | 0.422 | 0.417 | 3742 | 0.1774 | 0.1668 | 0.1693 |
| HYBRID_30 | 3742 | 0.1692 | 0.5070 | 0.412 | 0.417 | 3742 | 0.1692 | 0.1668 | 0.1693 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3742 | 48 | 0.01065 | [0.00251, 0.01963] | 0.01065 | [0.00251, 0.01963] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3742 | 48 | 0.00252 | [-0.00005, 0.00496] | 0.00252 | [-0.00005, 0.00496] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3742 | 48 | -0.00813 | [-0.01477, -0.00135] | -0.00813 | [-0.01477, -0.00135] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3742 | 48 | - | - | -0.00004 | [-0.00108, 0.00089] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3676 | 48 | - | - | -0.00037 | [-0.00169, 0.00080] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3742 | 48 | - | - | 0.01061 | [0.00221, 0.01966] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3676 | 48 | - | - | 0.01051 | [0.00194, 0.01988] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3742 | 48 | - | - | 0.00248 | [-0.00016, 0.00527] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3676 | 48 | - | - | 0.00223 | [-0.00057, 0.00521] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 192, 'GAME_WINNER': 96, 'SPREAD': 1233, 'TEAM_TOTAL': 1309, 'TOTAL': 912}; settlement: {'SETTLED': 3742}; close: {'OK': 3676, 'OK_STALE': 66}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 586 / 0.055 / 0.049 | 558 / 0.054 / 0.066 | 575 / 0.053 / 0.059 |
| 0.10-0.20 | 602 / 0.145 / 0.183 | 584 / 0.145 / 0.195 | 601 / 0.146 / 0.186 |
| 0.20-0.30 | 436 / 0.248 / 0.282 | 449 / 0.249 / 0.292 | 435 / 0.249 / 0.269 |
| 0.30-0.40 | 380 / 0.351 / 0.363 | 380 / 0.349 / 0.374 | 384 / 0.348 / 0.365 |
| 0.40-0.50 | 392 / 0.450 / 0.469 | 361 / 0.448 / 0.449 | 420 / 0.449 / 0.483 |
| 0.50-0.60 | 356 / 0.546 / 0.537 | 335 / 0.550 / 0.507 | 339 / 0.549 / 0.531 |
| 0.60-0.70 | 241 / 0.650 / 0.598 | 296 / 0.648 / 0.541 | 245 / 0.649 / 0.584 |
| 0.70-0.80 | 193 / 0.750 / 0.731 | 198 / 0.750 / 0.682 | 199 / 0.752 / 0.693 |
| 0.80-0.90 | 194 / 0.848 / 0.851 | 201 / 0.851 / 0.811 | 190 / 0.853 / 0.868 |
| 0.90-1.00 | 362 / 0.954 / 0.931 | 380 / 0.957 / 0.916 | 354 / 0.955 / 0.932 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 23 | 6 | 2 | 2 | 13 | 0 | 0.500 [0.150, 0.850] | 0.353 | 0.353 | 0.06 |
| T-24h | DATA_ONLY | total | 23 | 5 | 7 | 1 | 10 | 0 | 0.875 [0.529, 0.978] | 0.500 | 0.444 | 0.44 |
| T-24h | HYBRID_30 (derived) | margin | 23 | 16 | 1 | 1 | 5 | 0 | 0.500 [0.095, 0.905] | 0.286 | 0.286 | 0.07 |
| T-24h | HYBRID_30 (derived) | total | 23 | 19 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.250 | 0.250 | 0.25 |
| T-6h | DATA_ONLY | margin | 30 | 5 | 6 | 2 | 17 | 0 | 0.750 [0.409, 0.929] | 0.360 | 0.400 | 0.10 |
| T-6h | DATA_ONLY | total | 30 | 10 | 5 | 4 | 11 | 0 | 0.556 [0.267, 0.811] | 0.450 | 0.450 | -0.03 |
| T-6h | HYBRID_30 (derived) | margin | 30 | 22 | 1 | 1 | 6 | 0 | 0.500 [0.095, 0.905] | 0.375 | 0.375 | 0.00 |
| T-6h | HYBRID_30 (derived) | total | 30 | 25 | 2 | 0 | 3 | 0 | 1.000 [0.342, 1.000] | 0.400 | 0.200 | 0.40 |
| T-90m | DATA_ONLY | margin | 37 | 6 | 5 | 2 | 24 | 0 | 0.714 [0.359, 0.918] | 0.387 | 0.387 | 0.02 |
| T-90m | DATA_ONLY | total | 37 | 12 | 4 | 6 | 15 | 0 | 0.400 [0.168, 0.687] | 0.400 | 0.400 | -0.12 |
| T-90m | HYBRID_30 (derived) | margin | 37 | 27 | 0 | 1 | 9 | 0 | 0.000 [0.000, 0.793] | 0.400 | 0.400 | -0.10 |
| T-90m | HYBRID_30 (derived) | total | 37 | 30 | 0 | 3 | 4 | 0 | 0.000 [0.000, 0.561] | 0.286 | 0.286 | -0.36 |
| T-30m | DATA_ONLY | margin | 48 | 9 | 5 | 2 | 32 | 0 | 0.714 [0.359, 0.918] | 0.333 | 0.333 | 0.05 |
| T-30m | DATA_ONLY | total | 48 | 17 | 6 | 5 | 20 | 0 | 0.545 [0.280, 0.787] | 0.355 | 0.355 | -0.05 |
| T-30m | HYBRID_30 (derived) | margin | 48 | 37 | 0 | 1 | 10 | 0 | 0.000 [0.000, 0.793] | 0.364 | 0.364 | -0.09 |
| T-30m | HYBRID_30 (derived) | total | 48 | 39 | 1 | 1 | 7 | 0 | 0.500 [0.095, 0.905] | 0.111 | 0.111 | 0.00 |
| latest_pregame | DATA_ONLY | margin | 49 | 9 | 5 | 2 | 33 | 0 | 0.714 [0.359, 0.918] | 0.325 | 0.325 | 0.05 |
| latest_pregame | DATA_ONLY | total | 49 | 17 | 6 | 5 | 21 | 0 | 0.545 [0.280, 0.787] | 0.344 | 0.344 | -0.05 |
| latest_pregame | HYBRID_30 (derived) | margin | 49 | 38 | 0 | 1 | 10 | 0 | 0.000 [0.000, 0.793] | 0.364 | 0.364 | -0.09 |
| latest_pregame | HYBRID_30 (derived) | total | 49 | 39 | 1 | 1 | 8 | 0 | 0.500 [0.095, 0.905] | 0.100 | 0.100 | 0.00 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 9 | 1 | 2 | 6 | 0 | 0.333 |
| margin | 1-2 | 14 | 3 | 0 | 11 | 0 | 1.000 |
| margin | 2-3 | 13 | 2 | 1 | 10 | 0 | 0.667 |
| margin | 3-5 | 10 | 0 | 1 | 9 | 0 | 0.000 |
| margin | >5 | 3 | 0 | 0 | 3 | 0 | - |
| total | <=1 | 17 | 2 | 1 | 14 | 0 | 0.667 |
| total | 1-2 | 11 | 1 | 3 | 7 | 0 | 0.250 |
| total | 2-3 | 8 | 4 | 1 | 3 | 0 | 0.800 |
| total | 3-5 | 10 | 1 | 1 | 8 | 0 | 0.500 |
| total | >5 | 3 | 0 | 0 | 3 | 0 | - |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 18 | 3 | 0.667 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 18 | 4 | 0.500 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

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

110 snapshot(s). A contract's terminal state is where it left the existing gate sequence when the model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).

### Newest snapshot 20261004T152503Z (59608 markets)

| stage | markets |
|---|---|
| discovered | 59608 |
| mapped | 51090 |
| supported | 5947 |
| priced | 5947 |
| raw_disagreement | 5123 |
| tradable_book | 5096 |
| data_quality | 5078 |
| executable_price | 3991 |
| liquidity | 868 |

Terminal states: {'PASS': 57655, 'WATCH': 1085, 'BET': 868}

| family | BET | WATCH | PASS |
|---|---|---|---|
| AWARD | 0 | 0 | 875 |
| BOTH_TEAMS_SCORE | 0 | 0 | 256 |
| BOTH_TEAMS_SCORE_N | 0 | 14 | 242 |
| COACH_EVENT | 0 | 0 | 64 |
| CONFERENCE_WINNER | 0 | 0 | 32 |
| DIVISION_WINNER | 0 | 0 | 32 |
| DRAFT | 0 | 0 | 40 |
| FIRST_TD_SCORER | 0 | 0 | 1660 |
| FIRST_TD_TEAM | 0 | 0 | 1905 |
| GAME_EVENT | 0 | 0 | 260 |
| GAME_PLAYER_LEADER | 0 | 0 | 769 |
| GAME_STAT | 0 | 0 | 5 |
| GAME_WINNER | 0 | 21 | 137 |
| HALF_FULL_RESULT | 0 | 0 | 585 |
| MAKE_PLAYOFFS | 0 | 0 | 33 |
| NFL_BUSINESS_EVENT | 0 | 0 | 5 |
| NOT_NFL_OR_UNKNOWN | 0 | 0 | 2 |
| PERIOD_WINNER | 0 | 0 | 1152 |
| PLAYER_AVAILABILITY | 0 | 0 | 23 |
| PLAYER_ROLE_EVENT | 0 | 0 | 177 |
| PLAYER_STAT | 724 | 530 | 23667 |
| RACE_TO_N | 0 | 0 | 1005 |
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
| SPREAD | 44 | 200 | 6546 |
| SUPER_BOWL_EVENT | 0 | 0 | 265 |
| SUPER_BOWL_WINNER | 0 | 0 | 32 |
| TEAM_STAT | 0 | 0 | 1566 |
| TEAM_TOTAL | 77 | 147 | 2988 |
| TEAM_WINS_BY_WEEK | 0 | 0 | 728 |
| TOTAL | 23 | 173 | 5410 |
| TOTAL_TD | 0 | 0 | 214 |
| TRANSACTION_EVENT | 0 | 0 | 314 |
| UNKNOWN_NEEDS_CLASSIFICATION | 0 | 0 | 386 |
| WEEK_EVENT | 0 | 0 | 32 |
| WEEK_LEADER | 0 | 0 | 482 |
| WIN_MARGIN_BUCKET | 0 | 0 | 448 |

| rejection reason | n |
|---|---|
| POST_KICKOFF_EXCLUDED | 36151 |
| unmapped | 8518 |
| UNSUPPORTED_MODEL | 5471 |
| UNSUPPORTED_RULES | 3403 |
| no order book observed for this ticker (books are captured i | 3122 |
| no positive disagreement against either executable ask | 824 |
| UNSUPPORTED_IDENTITY | 114 |
| ask 0.99 above the zero-net-EV ceiling 0.98 | 93 |
| ask 0.97 above the zero-net-EV ceiling 0.96 | 41 |
| ask 0.98 above the zero-net-EV ceiling 0.97 | 35 |
| ask 0.96 above the zero-net-EV ceiling 0.95 | 32 |
| book not tradable for ranking | 27 |
| ask 0.06 above the zero-net-EV ceiling 0.05 | 26 |
| ask 0.95 above the zero-net-EV ceiling 0.94 | 24 |
| ask 0.07 above the zero-net-EV ceiling 0.06 | 24 |

WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee schedule (`watch_ceiling`). Not replayed: ['portfolio_risk_policy (needs a stake and bankroll)', "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own confirmation is the STALE_DATA support state)"].

Across all 110 snapshots (repeated markets counted per snapshot): {'PASS': 4069064, 'WATCH': 83785, 'BET': 69570}.

