# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 57 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 3308 | 57 | 4 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 31 | 31 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 38 | 38 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 45 | 45 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 56 | 56 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 57 | 57 | 4 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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

## Game-centre accuracy — latest_pregame (57 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 57 | 4 | 10.11 | 12.69 | 1.59 | 10.44 | 13.57 | -1.75 | 0.235 |
| DATA_ONLY | 57 | 4 | 10.52 | 13.13 | 1.27 | 11.40 | 14.49 | -0.59 | 0.249 |
| HYBRID_30 | 57 | 4 | 10.21 | 12.75 | 1.49 | 10.68 | 13.79 | -1.41 | 0.238 |
| market at snapshot | 57 | 4 | 10.11 | 12.69 | 1.59 | 10.44 | 13.57 | -1.75 | - |
| market at close | 57 | 4 | 10.14 | 12.68 | 1.61 | 10.52 | 13.68 | -1.71 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 57 | margin | 0.408 | 0.390 | [-0.357, 1.173] | 0.421 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 57 | total | 0.962 | 0.351 | [0.274, 1.650] | 0.386 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 57 | margin | 0.094 | 0.118 | [-0.137, 0.325] | 0.474 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 57 | total | 0.244 | 0.110 | [0.028, 0.459] | 0.439 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 57 | margin | -0.314 | 0.274 | [-0.852, 0.224] | 0.579 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 57 | total | -0.718 | 0.245 | [-1.199, -0.238] | 0.614 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 57 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 57 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 57 | margin | 0.408 | 0.390 | [-0.357, 1.173] | 0.421 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 57 | total | 0.962 | 0.351 | [0.274, 1.650] | 0.386 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 57 | margin | 0.094 | 0.118 | [-0.137, 0.325] | 0.474 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 57 | total | 0.244 | 0.110 | [0.028, 0.459] | 0.439 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 57 | margin | -0.026 | 0.048 | [-0.119, 0.067] | 0.105 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 57 | total | -0.079 | 0.058 | [-0.193, 0.036] | 0.175 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 57 | margin | 0.382 | 0.387 | [-0.377, 1.141] | 0.404 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 57 | total | 0.883 | 0.361 | [0.176, 1.590] | 0.386 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 57 | margin | 0.068 | 0.121 | [-0.170, 0.306] | 0.491 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 57 | total | 0.165 | 0.127 | [-0.085, 0.414] | 0.456 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 57 | 8 | 4 | 45 | 0 | 0.667 | 0.421 | 2.48 |
| DATA_ONLY | total | 57 | 8 | 8 | 41 | 0 | 0.500 | 0.386 | 2.24 |
| HYBRID_30 | margin | 57 | 8 | 4 | 45 | 0 | 0.667 | 0.474 | 0.75 |
| HYBRID_30 | total | 57 | 8 | 8 | 41 | 0 | 0.500 | 0.439 | 0.67 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 16 | 7.84 | 7.41 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 13 | 11.09 | 9.65 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.93 | 16.10 | - |
| DATA_ONLY | total | <=1 | 19 | 12.20 | 12.34 | 0.500 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 9 | 7.40 | 7.28 | 0.800 |
| DATA_ONLY | total | 3-5 | 14 | 11.30 | 8.71 | 0.500 |
| DATA_ONLY | total | >5 | 4 | 18.67 | 12.62 | 0.000 |
| HYBRID_30 | margin | <=1 | 42 | 9.32 | 9.21 | 0.700 |
| HYBRID_30 | margin | 1-2 | 15 | 12.70 | 12.63 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 43 | 10.62 | 10.65 | 0.538 |
| HYBRID_30 | total | 1-2 | 13 | 10.09 | 9.12 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 57}; DATA_ONLY quality states: {'OK': 57}; close centre status: {'OK': 57}.

## Game-centre accuracy — T-24h (31 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 31 | 4 | 10.23 | 12.54 | 2.10 | 9.74 | 12.19 | 1.10 | 0.240 |
| DATA_ONLY | 31 | 4 | 10.32 | 12.82 | 1.59 | 10.21 | 12.85 | 2.05 | 0.239 |
| HYBRID_30 | 31 | 4 | 10.24 | 12.53 | 1.95 | 9.81 | 12.31 | 1.38 | 0.237 |
| market at snapshot | 31 | 4 | 10.23 | 12.54 | 2.10 | 9.74 | 12.19 | 1.10 | - |
| market at close | 31 | 4 | 10.27 | 12.52 | 2.27 | 9.56 | 12.15 | 0.98 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 31 | margin | 0.093 | 0.618 | [-1.119, 1.304] | 0.452 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 31 | total | 0.469 | 0.509 | [-0.529, 1.466] | 0.516 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 31 | margin | 0.010 | 0.186 | [-0.355, 0.374] | 0.484 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 31 | total | 0.072 | 0.163 | [-0.246, 0.391] | 0.516 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 31 | margin | -0.083 | 0.433 | [-0.933, 0.767] | 0.548 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 31 | total | -0.396 | 0.354 | [-1.091, 0.298] | 0.548 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 31 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 31 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 31 | margin | 0.093 | 0.618 | [-1.119, 1.304] | 0.452 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 31 | total | 0.469 | 0.509 | [-0.529, 1.466] | 0.516 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 31 | margin | 0.010 | 0.186 | [-0.355, 0.374] | 0.484 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 31 | total | 0.072 | 0.163 | [-0.246, 0.391] | 0.516 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 31 | margin | -0.048 | 0.082 | [-0.208, 0.111] | 0.194 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 31 | total | 0.177 | 0.124 | [-0.065, 0.420] | 0.129 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 31 | margin | 0.044 | 0.611 | [-1.154, 1.243] | 0.452 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 31 | total | 0.646 | 0.465 | [-0.266, 1.558] | 0.355 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 31 | margin | -0.039 | 0.192 | [-0.414, 0.337] | 0.548 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 31 | total | 0.250 | 0.148 | [-0.041, 0.541] | 0.323 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 31 | 4 | 7 | 20 | 0 | 0.364 | 0.452 | 2.80 |
| DATA_ONLY | total | 31 | 12 | 3 | 16 | 0 | 0.800 | 0.516 | 2.54 |
| HYBRID_30 | margin | 31 | 4 | 7 | 20 | 0 | 0.364 | 0.484 | 0.84 |
| HYBRID_30 | total | 31 | 12 | 3 | 16 | 0 | 0.800 | 0.516 | 0.76 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 7 | 8.14 | 8.29 | 0.000 |
| DATA_ONLY | margin | 1-2 | 5 | 5.40 | 4.80 | 1.000 |
| DATA_ONLY | margin | 2-3 | 6 | 11.65 | 11.58 | - |
| DATA_ONLY | margin | 3-5 | 8 | 11.41 | 10.44 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.95 | 16.40 | 0.500 |
| DATA_ONLY | total | <=1 | 7 | 9.16 | 9.57 | 0.750 |
| DATA_ONLY | total | 1-2 | 4 | 9.99 | 9.38 | 0.000 |
| DATA_ONLY | total | 2-3 | 8 | 10.41 | 10.62 | 1.000 |
| DATA_ONLY | total | 3-5 | 10 | 10.30 | 9.80 | 0.750 |
| DATA_ONLY | total | >5 | 2 | 13.07 | 7.25 | 1.000 |
| HYBRID_30 | margin | <=1 | 20 | 8.24 | 8.22 | 0.250 |
| HYBRID_30 | margin | 1-2 | 10 | 13.03 | 12.80 | 0.500 |
| HYBRID_30 | margin | 2-3 | 1 | 22.29 | 24.50 | 1.000 |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 22 | 10.20 | 10.32 | 0.818 |
| HYBRID_30 | total | 1-2 | 9 | 8.87 | 8.33 | 0.750 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 31}; DATA_ONLY quality states: {'OK': 31}; close centre status: {'OK': 31}.

## Game-centre accuracy — T-6h (38 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 38 | 4 | 9.45 | 12.18 | 0.37 | 9.04 | 10.86 | -2.01 | 0.252 |
| DATA_ONLY | 38 | 4 | 9.60 | 12.10 | 0.11 | 9.78 | 11.81 | -0.81 | 0.249 |
| HYBRID_30 | 38 | 4 | 9.48 | 12.07 | 0.29 | 9.18 | 11.07 | -1.65 | 0.248 |
| market at snapshot | 38 | 4 | 9.45 | 12.18 | 0.37 | 9.04 | 10.86 | -2.01 | - |
| market at close | 38 | 4 | 9.51 | 12.19 | 0.43 | 9.16 | 11.03 | -2.05 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 38 | margin | 0.149 | 0.517 | [-0.864, 1.162] | 0.447 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 38 | total | 0.743 | 0.436 | [-0.112, 1.598] | 0.421 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 38 | margin | 0.030 | 0.156 | [-0.275, 0.335] | 0.474 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 38 | total | 0.137 | 0.134 | [-0.126, 0.401] | 0.474 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 38 | margin | -0.119 | 0.362 | [-0.829, 0.591] | 0.553 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 38 | total | -0.606 | 0.314 | [-1.221, 0.009] | 0.605 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 38 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 38 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 38 | margin | 0.149 | 0.517 | [-0.864, 1.162] | 0.447 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 38 | total | 0.743 | 0.436 | [-0.112, 1.598] | 0.421 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 38 | margin | 0.030 | 0.156 | [-0.275, 0.335] | 0.474 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 38 | total | 0.137 | 0.134 | [-0.126, 0.401] | 0.474 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 38 | margin | -0.066 | 0.095 | [-0.251, 0.120] | 0.211 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 38 | total | -0.118 | 0.120 | [-0.353, 0.117] | 0.237 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 38 | margin | 0.083 | 0.509 | [-0.915, 1.081] | 0.447 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 38 | total | 0.625 | 0.465 | [-0.286, 1.536] | 0.421 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 38 | margin | -0.036 | 0.167 | [-0.364, 0.292] | 0.474 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 38 | total | 0.019 | 0.183 | [-0.340, 0.378] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 38 | 8 | 5 | 25 | 0 | 0.615 | 0.447 | 2.64 |
| DATA_ONLY | total | 38 | 9 | 8 | 21 | 0 | 0.529 | 0.421 | 2.28 |
| HYBRID_30 | margin | 38 | 8 | 5 | 25 | 0 | 0.615 | 0.474 | 0.79 |
| HYBRID_30 | total | 38 | 9 | 8 | 21 | 0 | 0.529 | 0.474 | 0.68 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 6 | 10.18 | 10.42 | 0.333 |
| DATA_ONLY | margin | 1-2 | 11 | 8.73 | 8.09 | 0.667 |
| DATA_ONLY | margin | 2-3 | 7 | 10.98 | 10.71 | 1.000 |
| DATA_ONLY | margin | 3-5 | 9 | 8.39 | 7.94 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 11.04 | 12.20 | 0.500 |
| DATA_ONLY | total | <=1 | 12 | 8.67 | 8.67 | 0.750 |
| DATA_ONLY | total | 1-2 | 9 | 9.61 | 9.94 | 0.600 |
| DATA_ONLY | total | 2-3 | 6 | 9.11 | 9.08 | 0.000 |
| DATA_ONLY | total | 3-5 | 7 | 9.79 | 8.79 | 0.333 |
| DATA_ONLY | total | >5 | 4 | 14.53 | 8.50 | 0.667 |
| HYBRID_30 | margin | <=1 | 27 | 9.04 | 9.02 | 0.700 |
| HYBRID_30 | margin | 1-2 | 11 | 10.54 | 10.50 | 0.333 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 29 | 9.24 | 9.22 | 0.500 |
| HYBRID_30 | total | 1-2 | 8 | 7.49 | 7.19 | 0.600 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 38}; DATA_ONLY quality states: {'OK': 38}; close centre status: {'OK': 38}.

## Game-centre accuracy — T-90m (45 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 45 | 4 | 9.21 | 11.72 | 0.70 | 9.77 | 12.24 | -0.32 | 0.247 |
| DATA_ONLY | 45 | 4 | 9.37 | 11.90 | 0.33 | 10.47 | 12.99 | 0.68 | 0.247 |
| HYBRID_30 | 45 | 4 | 9.24 | 11.69 | 0.59 | 9.92 | 12.40 | -0.02 | 0.245 |
| market at snapshot | 45 | 4 | 9.21 | 11.72 | 0.70 | 9.77 | 12.24 | -0.32 | - |
| market at close | 45 | 4 | 9.24 | 11.72 | 0.71 | 9.76 | 12.20 | -0.40 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 45 | margin | 0.160 | 0.472 | [-0.764, 1.084] | 0.422 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 45 | total | 0.705 | 0.396 | [-0.072, 1.481] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 45 | margin | 0.028 | 0.142 | [-0.251, 0.306] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 45 | total | 0.155 | 0.124 | [-0.089, 0.398] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 45 | margin | -0.132 | 0.331 | [-0.780, 0.516] | 0.578 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 45 | total | -0.550 | 0.277 | [-1.093, -0.007] | 0.600 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 45 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 45 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 45 | margin | 0.160 | 0.472 | [-0.764, 1.084] | 0.422 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 45 | total | 0.705 | 0.396 | [-0.072, 1.481] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 45 | margin | 0.028 | 0.142 | [-0.251, 0.306] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 45 | total | 0.155 | 0.124 | [-0.089, 0.398] | 0.467 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 45 | margin | -0.033 | 0.054 | [-0.138, 0.072] | 0.133 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 45 | total | 0.011 | 0.077 | [-0.140, 0.162] | 0.178 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 45 | margin | 0.127 | 0.467 | [-0.788, 1.041] | 0.422 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 45 | total | 0.716 | 0.417 | [-0.101, 1.532] | 0.378 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 45 | margin | -0.006 | 0.144 | [-0.287, 0.276] | 0.489 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 45 | total | 0.166 | 0.156 | [-0.140, 0.471] | 0.422 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 45 | 7 | 5 | 33 | 0 | 0.583 | 0.422 | 2.65 |
| DATA_ONLY | total | 45 | 8 | 9 | 28 | 0 | 0.471 | 0.400 | 2.26 |
| HYBRID_30 | margin | 45 | 7 | 5 | 33 | 0 | 0.583 | 0.467 | 0.79 |
| HYBRID_30 | total | 45 | 8 | 9 | 28 | 0 | 0.471 | 0.467 | 0.68 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 7 | 6.43 | 6.50 | 0.000 |
| DATA_ONLY | margin | 1-2 | 11 | 7.35 | 6.86 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.25 | 10.25 | 0.750 |
| DATA_ONLY | margin | 3-5 | 10 | 9.81 | 9.00 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.93 | 16.10 | - |
| DATA_ONLY | total | <=1 | 14 | 11.15 | 11.32 | 0.667 |
| DATA_ONLY | total | 1-2 | 10 | 6.53 | 7.10 | 0.250 |
| DATA_ONLY | total | 2-3 | 7 | 11.31 | 10.50 | 1.000 |
| DATA_ONLY | total | 3-5 | 11 | 9.82 | 8.36 | 0.000 |
| DATA_ONLY | total | >5 | 3 | 20.87 | 14.83 | 0.000 |
| HYBRID_30 | margin | <=1 | 31 | 7.94 | 7.89 | 0.600 |
| HYBRID_30 | margin | 1-2 | 14 | 12.12 | 12.14 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 34 | 9.66 | 9.69 | 0.615 |
| HYBRID_30 | total | 1-2 | 10 | 9.65 | 9.05 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 45}; DATA_ONLY quality states: {'OK': 45}; close centre status: {'OK': 45}.

## Game-centre accuracy — T-30m (56 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 56 | 4 | 10.21 | 12.79 | 1.70 | 10.31 | 13.49 | -1.47 | 0.237 |
| DATA_ONLY | 56 | 4 | 10.60 | 13.22 | 1.41 | 11.19 | 14.29 | -0.19 | 0.251 |
| HYBRID_30 | 56 | 4 | 10.30 | 12.85 | 1.61 | 10.53 | 13.68 | -1.09 | 0.241 |
| market at snapshot | 56 | 4 | 10.21 | 12.79 | 1.70 | 10.31 | 13.49 | -1.47 | - |
| market at close | 56 | 4 | 10.24 | 12.78 | 1.72 | 10.39 | 13.61 | -1.43 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 56 | margin | 0.384 | 0.397 | [-0.393, 1.162] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 56 | total | 0.880 | 0.348 | [0.199, 1.562] | 0.393 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 56 | margin | 0.086 | 0.120 | [-0.148, 0.321] | 0.482 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 56 | total | 0.218 | 0.109 | [0.005, 0.432] | 0.446 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 56 | margin | -0.298 | 0.279 | [-0.844, 0.249] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 56 | total | -0.662 | 0.243 | [-1.138, -0.186] | 0.607 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 56 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 56 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 56 | margin | 0.384 | 0.397 | [-0.393, 1.162] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 56 | total | 0.880 | 0.348 | [0.199, 1.562] | 0.393 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 56 | margin | 0.086 | 0.120 | [-0.148, 0.321] | 0.482 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 56 | total | 0.218 | 0.109 | [0.005, 0.432] | 0.446 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 56 | margin | -0.027 | 0.048 | [-0.122, 0.068] | 0.107 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 56 | total | -0.080 | 0.059 | [-0.197, 0.036] | 0.179 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 56 | margin | 0.357 | 0.393 | [-0.414, 1.128] | 0.411 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 56 | total | 0.800 | 0.358 | [0.099, 1.501] | 0.393 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 56 | margin | 0.060 | 0.123 | [-0.182, 0.301] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 56 | total | 0.138 | 0.127 | [-0.110, 0.386] | 0.464 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 56 | 8 | 4 | 44 | 0 | 0.667 | 0.429 | 2.50 |
| DATA_ONLY | total | 56 | 8 | 8 | 40 | 0 | 0.500 | 0.393 | 2.18 |
| HYBRID_30 | margin | 56 | 8 | 4 | 44 | 0 | 0.667 | 0.482 | 0.75 |
| HYBRID_30 | total | 56 | 8 | 8 | 40 | 0 | 0.500 | 0.446 | 0.65 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 12.16 | 12.28 | 0.333 |
| DATA_ONLY | margin | 1-2 | 15 | 7.95 | 7.60 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 13 | 11.09 | 9.65 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.93 | 16.10 | - |
| DATA_ONLY | total | <=1 | 19 | 12.20 | 12.34 | 0.500 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 9 | 7.40 | 7.28 | 0.800 |
| DATA_ONLY | total | 3-5 | 14 | 11.30 | 8.71 | 0.500 |
| DATA_ONLY | total | >5 | 3 | 17.21 | 11.00 | 0.000 |
| HYBRID_30 | margin | <=1 | 41 | 9.42 | 9.33 | 0.700 |
| HYBRID_30 | margin | 1-2 | 15 | 12.70 | 12.63 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 43 | 10.62 | 10.65 | 0.538 |
| HYBRID_30 | total | 1-2 | 12 | 9.33 | 8.42 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 56}; DATA_ONLY quality states: {'OK': 56}; close centre status: {'OK': 56}.

## Contract pricing — latest_pregame (4441 contracts, 57 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4441 | 0.1611 | 0.4854 | 0.414 | 0.418 | 4441 | 0.1611 | 0.1611 | 0.1635 |
| DATA_ONLY | 4441 | 0.1703 | 0.5108 | 0.425 | 0.418 | 4441 | 0.1703 | 0.1611 | 0.1635 |
| HYBRID_30 | 4441 | 0.1634 | 0.4914 | 0.415 | 0.418 | 4441 | 0.1634 | 0.1611 | 0.1635 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4441 | 57 | 0.00919 | [0.00073, 0.01775] | 0.00919 | [0.00073, 0.01775] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4441 | 57 | 0.00222 | [-0.00033, 0.00495] | 0.00222 | [-0.00033, 0.00495] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4441 | 57 | -0.00697 | [-0.01351, -0.00049] | -0.00697 | [-0.01351, -0.00049] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4441 | 57 | - | - | 0.00007 | [-0.00082, 0.00095] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4366 | 57 | - | - | -0.00026 | [-0.00130, 0.00078] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4441 | 57 | - | - | 0.00926 | [0.00068, 0.01820] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4366 | 57 | - | - | 0.00912 | [0.00027, 0.01797] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4441 | 57 | - | - | 0.00229 | [-0.00028, 0.00506] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4366 | 57 | - | - | 0.00203 | [-0.00062, 0.00501] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 228, 'GAME_WINNER': 114, 'SPREAD': 1461, 'TEAM_TOTAL': 1555, 'TOTAL': 1083}; settlement: {'SETTLED': 4441}; close: {'OK': 4366, 'OK_STALE': 75}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 688 / 0.055 / 0.044 | 656 / 0.054 / 0.061 | 675 / 0.054 / 0.052 |
| 0.10-0.20 | 713 / 0.145 / 0.168 | 693 / 0.145 / 0.177 | 711 / 0.146 / 0.174 |
| 0.20-0.30 | 524 / 0.249 / 0.277 | 528 / 0.250 / 0.282 | 516 / 0.249 / 0.258 |
| 0.30-0.40 | 448 / 0.351 / 0.353 | 450 / 0.349 / 0.358 | 454 / 0.348 / 0.357 |
| 0.40-0.50 | 455 / 0.450 / 0.462 | 431 / 0.448 / 0.450 | 494 / 0.449 / 0.478 |
| 0.50-0.60 | 434 / 0.547 / 0.551 | 393 / 0.551 / 0.501 | 408 / 0.549 / 0.537 |
| 0.60-0.70 | 282 / 0.650 / 0.613 | 350 / 0.648 / 0.557 | 293 / 0.649 / 0.601 |
| 0.70-0.80 | 230 / 0.751 / 0.743 | 241 / 0.749 / 0.714 | 233 / 0.752 / 0.708 |
| 0.80-0.90 | 232 / 0.849 / 0.866 | 238 / 0.850 / 0.828 | 228 / 0.852 / 0.886 |
| 0.90-1.00 | 435 / 0.954 / 0.943 | 461 / 0.957 / 0.931 | 429 / 0.955 / 0.944 |

## Contract pricing — T-24h (2414 contracts, 31 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2414 | 0.1601 | 0.4827 | 0.414 | 0.392 | 2414 | 0.1601 | 0.1599 | 0.1609 |
| DATA_ONLY | 2414 | 0.1634 | 0.4933 | 0.423 | 0.392 | 2414 | 0.1634 | 0.1599 | 0.1609 |
| HYBRID_30 | 2414 | 0.1595 | 0.4810 | 0.415 | 0.392 | 2414 | 0.1595 | 0.1599 | 0.1609 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2414 | 31 | 0.00328 | [-0.01011, 0.01714] | 0.00328 | [-0.01011, 0.01714] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2414 | 31 | -0.00057 | [-0.00497, 0.00398] | -0.00057 | [-0.00497, 0.00398] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2414 | 31 | -0.00385 | [-0.01433, 0.00562] | -0.00385 | [-0.01433, 0.00562] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2414 | 31 | - | - | 0.00016 | [-0.00088, 0.00122] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2380 | 31 | - | - | 0.00117 | [-0.00051, 0.00300] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2414 | 31 | - | - | 0.00344 | [-0.00961, 0.01690] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2380 | 31 | - | - | 0.00457 | [-0.00828, 0.01794] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2414 | 31 | - | - | -0.00041 | [-0.00459, 0.00401] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2380 | 31 | - | - | 0.00066 | [-0.00360, 0.00512] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 124, 'GAME_WINNER': 62, 'SPREAD': 796, 'TEAM_TOTAL': 843, 'TOTAL': 589}; settlement: {'SETTLED': 2414}; close: {'OK': 2380, 'OK_STALE': 34}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 383 / 0.055 / 0.021 | 362 / 0.054 / 0.036 | 365 / 0.053 / 0.019 |
| 0.10-0.20 | 374 / 0.146 / 0.142 | 379 / 0.146 / 0.148 | 389 / 0.146 / 0.147 |
| 0.20-0.30 | 293 / 0.249 / 0.280 | 286 / 0.250 / 0.290 | 286 / 0.250 / 0.266 |
| 0.30-0.40 | 232 / 0.349 / 0.336 | 246 / 0.349 / 0.321 | 233 / 0.348 / 0.339 |
| 0.40-0.50 | 256 / 0.449 / 0.414 | 231 / 0.447 / 0.385 | 276 / 0.449 / 0.438 |
| 0.50-0.60 | 227 / 0.546 / 0.515 | 211 / 0.550 / 0.431 | 213 / 0.550 / 0.479 |
| 0.60-0.70 | 154 / 0.647 / 0.558 | 193 / 0.649 / 0.560 | 160 / 0.646 / 0.531 |
| 0.70-0.80 | 135 / 0.750 / 0.726 | 127 / 0.749 / 0.732 | 134 / 0.749 / 0.724 |
| 0.80-0.90 | 123 / 0.851 / 0.821 | 129 / 0.848 / 0.822 | 124 / 0.853 / 0.855 |
| 0.90-1.00 | 237 / 0.955 / 0.920 | 250 / 0.956 / 0.916 | 234 / 0.955 / 0.927 |

## Contract pricing — T-6h (2964 contracts, 38 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2964 | 0.1542 | 0.4658 | 0.414 | 0.416 | 2964 | 0.1542 | 0.1548 | 0.1575 |
| DATA_ONLY | 2964 | 0.1585 | 0.4769 | 0.425 | 0.416 | 2964 | 0.1585 | 0.1548 | 0.1575 |
| HYBRID_30 | 2964 | 0.1544 | 0.4668 | 0.414 | 0.416 | 2964 | 0.1544 | 0.1548 | 0.1575 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2964 | 38 | 0.00427 | [-0.00683, 0.01458] | 0.00427 | [-0.00683, 0.01458] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2964 | 38 | 0.00023 | [-0.00262, 0.00288] | 0.00023 | [-0.00262, 0.00288] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2964 | 38 | -0.00404 | [-0.01246, 0.00443] | -0.00404 | [-0.01246, 0.00443] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2964 | 38 | - | - | -0.00055 | [-0.00166, 0.00047] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2900 | 38 | - | - | -0.00054 | [-0.00211, 0.00092] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2964 | 38 | - | - | 0.00371 | [-0.00732, 0.01442] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2900 | 38 | - | - | 0.00388 | [-0.00726, 0.01481] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2964 | 38 | - | - | -0.00032 | [-0.00359, 0.00268] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2900 | 38 | - | - | -0.00026 | [-0.00366, 0.00291] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 152, 'GAME_WINNER': 76, 'SPREAD': 974, 'TEAM_TOTAL': 1040, 'TOTAL': 722}; settlement: {'SETTLED': 2964}; close: {'OK': 2900, 'OK_STALE': 64}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 467 / 0.055 / 0.049 | 448 / 0.054 / 0.040 | 459 / 0.054 / 0.046 |
| 0.10-0.20 | 464 / 0.144 / 0.151 | 459 / 0.147 / 0.153 | 463 / 0.146 / 0.158 |
| 0.20-0.30 | 356 / 0.250 / 0.253 | 344 / 0.251 / 0.262 | 361 / 0.251 / 0.235 |
| 0.30-0.40 | 299 / 0.351 / 0.358 | 296 / 0.350 / 0.372 | 291 / 0.349 / 0.375 |
| 0.40-0.50 | 308 / 0.449 / 0.458 | 283 / 0.446 / 0.424 | 332 / 0.448 / 0.449 |
| 0.50-0.60 | 284 / 0.546 / 0.525 | 262 / 0.549 / 0.511 | 271 / 0.549 / 0.539 |
| 0.60-0.70 | 191 / 0.650 / 0.628 | 239 / 0.648 / 0.582 | 191 / 0.649 / 0.618 |
| 0.70-0.80 | 148 / 0.754 / 0.770 | 164 / 0.751 / 0.732 | 155 / 0.751 / 0.755 |
| 0.80-0.90 | 162 / 0.851 / 0.901 | 161 / 0.849 / 0.857 | 155 / 0.852 / 0.903 |
| 0.90-1.00 | 285 / 0.956 / 0.961 | 308 / 0.957 / 0.958 | 286 / 0.956 / 0.965 |

## Contract pricing — T-90m (3506 contracts, 45 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3506 | 0.1551 | 0.4706 | 0.415 | 0.399 | 3506 | 0.1551 | 0.1545 | 0.1570 |
| DATA_ONLY | 3506 | 0.1592 | 0.4817 | 0.424 | 0.399 | 3506 | 0.1592 | 0.1545 | 0.1570 |
| HYBRID_30 | 3506 | 0.1567 | 0.4732 | 0.414 | 0.399 | 3506 | 0.1567 | 0.1545 | 0.1570 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3506 | 45 | 0.00407 | [-0.00598, 0.01443] | 0.00407 | [-0.00598, 0.01443] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3506 | 45 | 0.00165 | [-0.00141, 0.00494] | 0.00165 | [-0.00141, 0.00494] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3506 | 45 | -0.00242 | [-0.01005, 0.00485] | -0.00242 | [-0.01005, 0.00485] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3506 | 45 | - | - | 0.00060 | [-0.00047, 0.00167] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3439 | 45 | - | - | 0.00058 | [-0.00075, 0.00189] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3506 | 45 | - | - | 0.00467 | [-0.00573, 0.01535] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3439 | 45 | - | - | 0.00476 | [-0.00569, 0.01542] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3506 | 45 | - | - | 0.00225 | [-0.00117, 0.00554] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3439 | 45 | - | - | 0.00229 | [-0.00126, 0.00575] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 180, 'GAME_WINNER': 90, 'SPREAD': 1154, 'TEAM_TOTAL': 1227, 'TOTAL': 855}; settlement: {'SETTLED': 3506}; close: {'OK': 3439, 'OK_STALE': 67}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 545 / 0.055 / 0.028 | 528 / 0.055 / 0.036 | 543 / 0.054 / 0.031 |
| 0.10-0.20 | 552 / 0.144 / 0.139 | 542 / 0.146 / 0.144 | 552 / 0.146 / 0.149 |
| 0.20-0.30 | 415 / 0.248 / 0.260 | 415 / 0.251 / 0.260 | 418 / 0.250 / 0.249 |
| 0.30-0.40 | 354 / 0.350 / 0.319 | 352 / 0.350 / 0.321 | 346 / 0.349 / 0.350 |
| 0.40-0.50 | 350 / 0.449 / 0.420 | 338 / 0.447 / 0.405 | 395 / 0.449 / 0.435 |
| 0.50-0.60 | 352 / 0.546 / 0.543 | 310 / 0.550 / 0.497 | 313 / 0.549 / 0.505 |
| 0.60-0.70 | 227 / 0.651 / 0.577 | 277 / 0.647 / 0.563 | 234 / 0.649 / 0.573 |
| 0.70-0.80 | 179 / 0.751 / 0.737 | 196 / 0.747 / 0.714 | 180 / 0.750 / 0.711 |
| 0.80-0.90 | 191 / 0.850 / 0.864 | 188 / 0.850 / 0.846 | 186 / 0.851 / 0.876 |
| 0.90-1.00 | 341 / 0.955 / 0.938 | 360 / 0.956 / 0.931 | 339 / 0.956 / 0.944 |

## Contract pricing — T-30m (4364 contracts, 56 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4364 | 0.1616 | 0.4865 | 0.413 | 0.414 | 4364 | 0.1616 | 0.1615 | 0.1640 |
| DATA_ONLY | 4364 | 0.1698 | 0.5095 | 0.425 | 0.414 | 4364 | 0.1698 | 0.1615 | 0.1640 |
| HYBRID_30 | 4364 | 0.1634 | 0.4916 | 0.414 | 0.414 | 4364 | 0.1634 | 0.1615 | 0.1640 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4364 | 56 | 0.00827 | [0.00023, 0.01751] | 0.00827 | [0.00023, 0.01751] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4364 | 56 | 0.00183 | [-0.00062, 0.00448] | 0.00183 | [-0.00062, 0.00448] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4364 | 56 | -0.00644 | [-0.01337, -0.00025] | -0.00644 | [-0.01337, -0.00025] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4364 | 56 | - | - | 0.00006 | [-0.00088, 0.00094] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4289 | 56 | - | - | -0.00027 | [-0.00142, 0.00081] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4364 | 56 | - | - | 0.00833 | [0.00000, 0.01776] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4289 | 56 | - | - | 0.00817 | [-0.00042, 0.01787] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4364 | 56 | - | - | 0.00189 | [-0.00064, 0.00487] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4289 | 56 | - | - | 0.00162 | [-0.00108, 0.00466] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 224, 'GAME_WINNER': 112, 'SPREAD': 1436, 'TEAM_TOTAL': 1528, 'TOTAL': 1064}; settlement: {'SETTLED': 4364}; close: {'OK': 4289, 'OK_STALE': 75}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 681 / 0.055 / 0.044 | 646 / 0.054 / 0.059 | 667 / 0.054 / 0.052 |
| 0.10-0.20 | 700 / 0.145 / 0.166 | 680 / 0.145 / 0.175 | 697 / 0.146 / 0.172 |
| 0.20-0.30 | 515 / 0.249 / 0.278 | 518 / 0.250 / 0.278 | 508 / 0.249 / 0.254 |
| 0.30-0.40 | 441 / 0.351 / 0.349 | 443 / 0.349 / 0.352 | 448 / 0.348 / 0.355 |
| 0.40-0.50 | 453 / 0.450 / 0.457 | 420 / 0.448 / 0.438 | 484 / 0.449 / 0.467 |
| 0.50-0.60 | 423 / 0.547 / 0.539 | 388 / 0.551 / 0.495 | 402 / 0.549 / 0.530 |
| 0.60-0.70 | 274 / 0.650 / 0.602 | 346 / 0.648 / 0.552 | 287 / 0.649 / 0.592 |
| 0.70-0.80 | 228 / 0.751 / 0.741 | 237 / 0.749 / 0.709 | 231 / 0.752 / 0.706 |
| 0.80-0.90 | 226 / 0.849 / 0.863 | 234 / 0.850 / 0.825 | 222 / 0.852 / 0.883 |
| 0.90-1.00 | 423 / 0.954 / 0.941 | 452 / 0.957 / 0.929 | 418 / 0.955 / 0.943 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 31 | 7 | 4 | 2 | 18 | 0 | 0.667 [0.300, 0.903] | 0.417 | 0.417 | 0.10 |
| T-24h | DATA_ONLY | total | 31 | 7 | 9 | 2 | 13 | 0 | 0.818 [0.523, 0.949] | 0.458 | 0.375 | 0.35 |
| T-24h | HYBRID_30 (derived) | margin | 31 | 20 | 2 | 1 | 8 | 0 | 0.667 [0.208, 0.939] | 0.455 | 0.455 | 0.09 |
| T-24h | HYBRID_30 (derived) | total | 31 | 22 | 3 | 1 | 5 | 0 | 0.750 [0.301, 0.954] | 0.333 | 0.333 | 0.17 |
| T-6h | DATA_ONLY | margin | 38 | 6 | 7 | 3 | 22 | 0 | 0.700 [0.397, 0.892] | 0.406 | 0.438 | 0.09 |
| T-6h | DATA_ONLY | total | 38 | 12 | 6 | 7 | 13 | 0 | 0.462 [0.232, 0.709] | 0.423 | 0.385 | -0.08 |
| T-6h | HYBRID_30 (derived) | margin | 38 | 27 | 1 | 2 | 8 | 0 | 0.333 [0.061, 0.792] | 0.455 | 0.455 | -0.05 |
| T-6h | HYBRID_30 (derived) | total | 38 | 29 | 3 | 2 | 4 | 0 | 0.600 [0.231, 0.882] | 0.444 | 0.333 | 0.11 |
| T-90m | DATA_ONLY | margin | 45 | 7 | 7 | 2 | 29 | 0 | 0.778 [0.453, 0.937] | 0.421 | 0.421 | 0.05 |
| T-90m | DATA_ONLY | total | 45 | 14 | 4 | 7 | 20 | 0 | 0.364 [0.152, 0.646] | 0.355 | 0.355 | -0.11 |
| T-90m | HYBRID_30 (derived) | margin | 45 | 31 | 1 | 1 | 12 | 0 | 0.500 [0.095, 0.905] | 0.500 | 0.500 | -0.04 |
| T-90m | HYBRID_30 (derived) | total | 45 | 34 | 0 | 4 | 7 | 0 | 0.000 [0.000, 0.490] | 0.273 | 0.273 | -0.27 |
| T-30m | DATA_ONLY | margin | 56 | 9 | 7 | 2 | 38 | 0 | 0.778 [0.453, 0.937] | 0.383 | 0.383 | 0.07 |
| T-30m | DATA_ONLY | total | 56 | 19 | 6 | 6 | 25 | 0 | 0.500 [0.254, 0.746] | 0.324 | 0.324 | -0.05 |
| T-30m | HYBRID_30 (derived) | margin | 56 | 41 | 1 | 1 | 13 | 0 | 0.500 [0.095, 0.905] | 0.467 | 0.467 | -0.03 |
| T-30m | HYBRID_30 (derived) | total | 56 | 43 | 1 | 2 | 10 | 0 | 0.333 [0.061, 0.792] | 0.154 | 0.154 | -0.04 |
| latest_pregame | DATA_ONLY | margin | 57 | 9 | 7 | 2 | 39 | 0 | 0.778 [0.453, 0.937] | 0.375 | 0.375 | 0.07 |
| latest_pregame | DATA_ONLY | total | 57 | 19 | 6 | 6 | 26 | 0 | 0.500 [0.254, 0.746] | 0.316 | 0.316 | -0.05 |
| latest_pregame | HYBRID_30 (derived) | margin | 57 | 42 | 1 | 1 | 13 | 0 | 0.500 [0.095, 0.905] | 0.467 | 0.467 | -0.03 |
| latest_pregame | HYBRID_30 (derived) | total | 57 | 43 | 1 | 2 | 11 | 0 | 0.333 [0.061, 0.792] | 0.143 | 0.143 | -0.04 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 9 | 1 | 2 | 6 | 0 | 0.333 |
| margin | 1-2 | 16 | 3 | 0 | 13 | 0 | 1.000 |
| margin | 2-3 | 14 | 2 | 1 | 11 | 0 | 0.667 |
| margin | 3-5 | 13 | 2 | 1 | 10 | 0 | 0.667 |
| margin | >5 | 5 | 0 | 0 | 5 | 0 | - |
| total | <=1 | 19 | 2 | 2 | 15 | 0 | 0.500 |
| total | 1-2 | 11 | 1 | 3 | 7 | 0 | 0.250 |
| total | 2-3 | 9 | 4 | 1 | 4 | 0 | 0.800 |
| total | 3-5 | 14 | 1 | 1 | 12 | 0 | 0.500 |
| total | >5 | 4 | 0 | 1 | 3 | 0 | 0.000 |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 26 | 5 | 0.800 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 26 | 5 | 0.400 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

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

111 snapshot(s). A contract's terminal state is where it left the existing gate sequence when the model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).

### Newest snapshot 20261004T194431Z (60174 markets)

| stage | markets |
|---|---|
| discovered | 60174 |
| mapped | 51656 |
| supported | 2750 |
| priced | 2750 |
| raw_disagreement | 2364 |
| tradable_book | 2340 |
| data_quality | 2323 |
| executable_price | 1844 |
| liquidity | 126 |

Terminal states: {'PASS': 59571, 'WATCH': 477, 'BET': 126}

| family | BET | WATCH | PASS |
|---|---|---|---|
| AWARD | 0 | 0 | 875 |
| BOTH_TEAMS_SCORE | 0 | 0 | 256 |
| BOTH_TEAMS_SCORE_N | 0 | 6 | 250 |
| COACH_EVENT | 0 | 0 | 64 |
| CONFERENCE_WINNER | 0 | 0 | 32 |
| DIVISION_WINNER | 0 | 0 | 32 |
| DRAFT | 0 | 0 | 40 |
| FIRST_TD_SCORER | 0 | 0 | 1665 |
| FIRST_TD_TEAM | 0 | 0 | 1908 |
| GAME_EVENT | 0 | 0 | 260 |
| GAME_PLAYER_LEADER | 0 | 0 | 795 |
| GAME_STAT | 0 | 0 | 5 |
| GAME_WINNER | 0 | 9 | 149 |
| HALF_FULL_RESULT | 0 | 0 | 585 |
| MAKE_PLAYOFFS | 0 | 0 | 33 |
| NFL_BUSINESS_EVENT | 0 | 0 | 5 |
| NOT_NFL_OR_UNKNOWN | 0 | 0 | 2 |
| PERIOD_WINNER | 0 | 0 | 1152 |
| PLAYER_AVAILABILITY | 0 | 0 | 23 |
| PLAYER_ROLE_EVENT | 0 | 0 | 177 |
| PLAYER_STAT | 126 | 231 | 24844 |
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
| SPREAD | 0 | 94 | 6779 |
| SUPER_BOWL_EVENT | 0 | 0 | 265 |
| SUPER_BOWL_WINNER | 0 | 0 | 32 |
| TEAM_STAT | 0 | 0 | 1566 |
| TEAM_TOTAL | 0 | 56 | 3298 |
| TEAM_WINS_BY_WEEK | 0 | 0 | 728 |
| TOTAL | 0 | 81 | 5552 |
| TOTAL_TD | 0 | 0 | 214 |
| TRANSACTION_EVENT | 0 | 0 | 314 |
| UNKNOWN_NEEDS_CLASSIFICATION | 0 | 0 | 386 |
| WEEK_EVENT | 0 | 0 | 32 |
| WEEK_LEADER | 0 | 0 | 482 |
| WIN_MARGIN_BUCKET | 0 | 0 | 448 |

| rejection reason | n |
|---|---|
| POST_KICKOFF_EXCLUDED | 41990 |
| unmapped | 8518 |
| UNSUPPORTED_RULES | 3403 |
| UNSUPPORTED_MODEL | 3233 |
| no order book observed for this ticker (books are captured i | 1718 |
| no positive disagreement against either executable ask | 386 |
| UNSUPPORTED_GAME | 232 |
| ask 0.99 above the zero-net-EV ceiling 0.98 | 52 |
| UNSUPPORTED_IDENTITY | 48 |
| book not tradable for ranking | 24 |
| ask 0.98 above the zero-net-EV ceiling 0.97 | 21 |
| ask 0.95 above the zero-net-EV ceiling 0.94 | 15 |
| availability QUESTIONABLE unresolved inside T-90m | 15 |
| ask 0.06 above the zero-net-EV ceiling 0.05 | 12 |
| ask 0.97 above the zero-net-EV ceiling 0.96 | 11 |

WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee schedule (`watch_ceiling`). Not replayed: ['portfolio_risk_policy (needs a stake and bankroll)', "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own confirmation is the STALE_DATA support state)"].

Across all 111 snapshots (repeated markets counted per snapshot): {'PASS': 4128635, 'WATCH': 84262, 'BET': 69696}.

