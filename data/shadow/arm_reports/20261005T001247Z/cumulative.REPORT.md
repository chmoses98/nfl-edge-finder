# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 58 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 3392 | 58 | 4 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 32 | 32 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 39 | 39 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 46 | 46 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 57 | 57 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 58 | 58 | 4 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_MIA_MIN | 2026-10-04T20:05 | 36 | CURRENT | 10.50 | 38.00 | 5 | 25 | 10.5/38.0 (kalshi_implied) | 10.5/38.0 (OK) |
|  |  |  | DATA_ONLY | 10.80 | 43.35 |  |  |  |  |
|  |  |  | HYBRID_30 | 10.59 | 39.60 |  |  |  |  |

## Game-centre accuracy — latest_pregame (58 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 58 | 4 | 10.03 | 12.61 | 1.66 | 10.48 | 13.56 | -1.50 | 0.231 |
| DATA_ONLY | 58 | 4 | 10.44 | 13.03 | 1.35 | 11.52 | 14.57 | -0.27 | 0.245 |
| HYBRID_30 | 58 | 4 | 10.13 | 12.66 | 1.56 | 10.75 | 13.81 | -1.13 | 0.235 |
| market at snapshot | 58 | 4 | 10.03 | 12.61 | 1.66 | 10.48 | 13.56 | -1.50 | - |
| market at close | 58 | 4 | 10.06 | 12.59 | 1.68 | 10.56 | 13.67 | -1.46 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 58 | margin | 0.406 | 0.384 | [-0.346, 1.158] | 0.414 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 58 | total | 1.038 | 0.353 | [0.345, 1.730] | 0.379 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 58 | margin | 0.094 | 0.116 | [-0.133, 0.321] | 0.466 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 58 | total | 0.267 | 0.110 | [0.051, 0.484] | 0.431 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 58 | margin | -0.312 | 0.270 | [-0.841, 0.216] | 0.586 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 58 | total | -0.770 | 0.247 | [-1.254, -0.287] | 0.621 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 58 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 58 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 58 | margin | 0.406 | 0.384 | [-0.346, 1.158] | 0.414 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 58 | total | 1.038 | 0.353 | [0.345, 1.730] | 0.379 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 58 | margin | 0.094 | 0.116 | [-0.133, 0.321] | 0.466 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 58 | total | 0.267 | 0.110 | [0.051, 0.484] | 0.431 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 58 | margin | -0.026 | 0.047 | [-0.117, 0.066] | 0.103 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 58 | total | -0.078 | 0.057 | [-0.190, 0.035] | 0.172 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 58 | margin | 0.380 | 0.380 | [-0.365, 1.126] | 0.397 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 58 | total | 0.960 | 0.363 | [0.249, 1.671] | 0.379 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 58 | margin | 0.068 | 0.119 | [-0.166, 0.302] | 0.483 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 58 | total | 0.190 | 0.127 | [-0.060, 0.439] | 0.448 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 58 | 8 | 4 | 46 | 0 | 0.667 | 0.414 | 2.45 |
| DATA_ONLY | total | 58 | 8 | 8 | 42 | 0 | 0.500 | 0.379 | 2.29 |
| HYBRID_30 | margin | 58 | 8 | 4 | 46 | 0 | 0.667 | 0.466 | 0.73 |
| HYBRID_30 | total | 58 | 8 | 8 | 42 | 0 | 0.500 | 0.431 | 0.69 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 10 | 11.52 | 11.60 | 0.333 |
| DATA_ONLY | margin | 1-2 | 16 | 7.84 | 7.41 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 13 | 11.09 | 9.65 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.93 | 16.10 | - |
| DATA_ONLY | total | <=1 | 19 | 12.20 | 12.34 | 0.500 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 9 | 7.40 | 7.28 | 0.800 |
| DATA_ONLY | total | 3-5 | 14 | 11.30 | 8.71 | 0.500 |
| DATA_ONLY | total | >5 | 5 | 18.60 | 12.70 | 0.000 |
| HYBRID_30 | margin | <=1 | 43 | 9.23 | 9.13 | 0.700 |
| HYBRID_30 | margin | 1-2 | 15 | 12.70 | 12.63 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 43 | 10.62 | 10.65 | 0.538 |
| HYBRID_30 | total | 1-2 | 14 | 10.41 | 9.39 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 58}; DATA_ONLY quality states: {'OK': 58}; close centre status: {'OK': 58}.

## Game-centre accuracy — T-24h (32 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 32 | 4 | 10.06 | 12.37 | 2.19 | 9.88 | 12.25 | 1.50 | 0.233 |
| DATA_ONLY | 32 | 4 | 10.18 | 12.66 | 1.72 | 10.46 | 13.06 | 2.56 | 0.232 |
| HYBRID_30 | 32 | 4 | 10.08 | 12.36 | 2.05 | 9.99 | 12.42 | 1.82 | 0.231 |
| market at snapshot | 32 | 4 | 10.06 | 12.37 | 2.19 | 9.88 | 12.25 | 1.50 | - |
| market at close | 32 | 4 | 10.12 | 12.36 | 2.38 | 9.67 | 12.18 | 1.36 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 32 | margin | 0.115 | 0.599 | [-1.059, 1.289] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 32 | total | 0.590 | 0.507 | [-0.405, 1.585] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 32 | margin | 0.017 | 0.180 | [-0.337, 0.370] | 0.469 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 32 | total | 0.111 | 0.162 | [-0.207, 0.428] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 32 | margin | -0.098 | 0.420 | [-0.921, 0.725] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 32 | total | -0.479 | 0.353 | [-1.171, 0.213] | 0.562 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 32 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 32 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 32 | margin | 0.115 | 0.599 | [-1.059, 1.289] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 32 | total | 0.590 | 0.507 | [-0.405, 1.585] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 32 | margin | 0.017 | 0.180 | [-0.337, 0.370] | 0.469 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 32 | total | 0.111 | 0.162 | [-0.207, 0.428] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 32 | margin | -0.062 | 0.080 | [-0.220, 0.095] | 0.219 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 32 | total | 0.203 | 0.123 | [-0.037, 0.444] | 0.125 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 32 | margin | 0.052 | 0.592 | [-1.108, 1.213] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 32 | total | 0.793 | 0.474 | [-0.136, 1.722] | 0.344 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 32 | margin | -0.046 | 0.186 | [-0.410, 0.318] | 0.562 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 32 | total | 0.314 | 0.157 | [0.005, 0.623] | 0.312 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 32 | 5 | 7 | 20 | 0 | 0.417 | 0.438 | 2.74 |
| DATA_ONLY | total | 32 | 12 | 4 | 16 | 0 | 0.750 | 0.500 | 2.59 |
| HYBRID_30 | margin | 32 | 5 | 7 | 20 | 0 | 0.417 | 0.469 | 0.82 |
| HYBRID_30 | total | 32 | 12 | 4 | 16 | 0 | 0.750 | 0.500 | 0.78 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 8 | 7.85 | 7.88 | 0.167 |
| DATA_ONLY | margin | 1-2 | 5 | 5.40 | 4.80 | 1.000 |
| DATA_ONLY | margin | 2-3 | 6 | 11.65 | 11.58 | - |
| DATA_ONLY | margin | 3-5 | 8 | 11.41 | 10.44 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.95 | 16.40 | 0.500 |
| DATA_ONLY | total | <=1 | 7 | 9.16 | 9.57 | 0.750 |
| DATA_ONLY | total | 1-2 | 4 | 9.99 | 9.38 | 0.000 |
| DATA_ONLY | total | 2-3 | 8 | 10.41 | 10.62 | 1.000 |
| DATA_ONLY | total | 3-5 | 11 | 11.03 | 10.18 | 0.600 |
| DATA_ONLY | total | >5 | 2 | 13.07 | 7.25 | 1.000 |
| HYBRID_30 | margin | <=1 | 21 | 8.09 | 8.07 | 0.333 |
| HYBRID_30 | margin | 1-2 | 10 | 13.03 | 12.80 | 0.500 |
| HYBRID_30 | margin | 2-3 | 1 | 22.29 | 24.50 | 1.000 |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 22 | 10.20 | 10.32 | 0.818 |
| HYBRID_30 | total | 1-2 | 10 | 9.51 | 8.90 | 0.600 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 32}; DATA_ONLY quality states: {'OK': 32}; close centre status: {'OK': 32}.

## Game-centre accuracy — T-6h (39 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 39 | 4 | 9.33 | 12.05 | 0.49 | 9.15 | 10.94 | -1.62 | 0.247 |
| DATA_ONLY | 39 | 4 | 9.50 | 11.98 | 0.26 | 10.00 | 12.02 | -0.31 | 0.243 |
| HYBRID_30 | 39 | 4 | 9.37 | 11.94 | 0.42 | 9.32 | 11.19 | -1.22 | 0.243 |
| market at snapshot | 39 | 4 | 9.33 | 12.05 | 0.49 | 9.15 | 10.94 | -1.62 | - |
| market at close | 39 | 4 | 9.41 | 12.06 | 0.56 | 9.26 | 11.09 | -1.67 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 39 | margin | 0.166 | 0.504 | [-0.822, 1.153] | 0.436 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 39 | total | 0.848 | 0.438 | [-0.009, 1.706] | 0.410 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 39 | margin | 0.035 | 0.152 | [-0.262, 0.332] | 0.462 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 39 | total | 0.171 | 0.135 | [-0.094, 0.436] | 0.462 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 39 | margin | -0.130 | 0.353 | [-0.823, 0.562] | 0.564 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 39 | total | -0.677 | 0.314 | [-1.293, -0.062] | 0.615 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 39 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 39 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 39 | margin | 0.166 | 0.504 | [-0.822, 1.153] | 0.436 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 39 | total | 0.848 | 0.438 | [-0.009, 1.706] | 0.410 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 39 | margin | 0.035 | 0.152 | [-0.262, 0.332] | 0.462 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 39 | total | 0.171 | 0.135 | [-0.094, 0.436] | 0.462 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 39 | margin | -0.077 | 0.093 | [-0.259, 0.105] | 0.231 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 39 | total | -0.103 | 0.118 | [-0.334, 0.128] | 0.231 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 39 | margin | 0.089 | 0.496 | [-0.883, 1.061] | 0.436 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 39 | total | 0.746 | 0.469 | [-0.173, 1.664] | 0.410 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 39 | margin | -0.042 | 0.163 | [-0.361, 0.278] | 0.487 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 39 | total | 0.069 | 0.185 | [-0.295, 0.432] | 0.487 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 39 | 9 | 5 | 25 | 0 | 0.643 | 0.436 | 2.60 |
| DATA_ONLY | total | 39 | 9 | 9 | 21 | 0 | 0.500 | 0.410 | 2.35 |
| HYBRID_30 | margin | 39 | 9 | 5 | 25 | 0 | 0.643 | 0.462 | 0.78 |
| HYBRID_30 | total | 39 | 9 | 9 | 21 | 0 | 0.500 | 0.462 | 0.70 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 7 | 9.55 | 9.64 | 0.500 |
| DATA_ONLY | margin | 1-2 | 11 | 8.73 | 8.09 | 0.667 |
| DATA_ONLY | margin | 2-3 | 7 | 10.98 | 10.71 | 1.000 |
| DATA_ONLY | margin | 3-5 | 9 | 8.39 | 7.94 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 11.04 | 12.20 | 0.500 |
| DATA_ONLY | total | <=1 | 12 | 8.67 | 8.67 | 0.750 |
| DATA_ONLY | total | 1-2 | 9 | 9.61 | 9.94 | 0.600 |
| DATA_ONLY | total | 2-3 | 6 | 9.11 | 9.08 | 0.000 |
| DATA_ONLY | total | 3-5 | 8 | 10.86 | 9.38 | 0.250 |
| DATA_ONLY | total | >5 | 4 | 14.53 | 8.50 | 0.667 |
| HYBRID_30 | margin | <=1 | 28 | 8.91 | 8.88 | 0.727 |
| HYBRID_30 | margin | 1-2 | 11 | 10.54 | 10.50 | 0.333 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 29 | 9.24 | 9.22 | 0.500 |
| HYBRID_30 | total | 1-2 | 9 | 8.32 | 7.89 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 39}; DATA_ONLY quality states: {'OK': 39}; close centre status: {'OK': 39}.

## Game-centre accuracy — T-90m (46 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 46 | 4 | 9.12 | 11.62 | 0.79 | 9.86 | 12.28 | -0.01 | 0.242 |
| DATA_ONLY | 46 | 4 | 9.29 | 11.80 | 0.45 | 10.64 | 13.13 | 1.06 | 0.242 |
| HYBRID_30 | 46 | 4 | 9.15 | 11.58 | 0.69 | 10.04 | 12.47 | 0.31 | 0.241 |
| market at snapshot | 46 | 4 | 9.12 | 11.62 | 0.79 | 9.86 | 12.28 | -0.01 | - |
| market at close | 46 | 4 | 9.16 | 11.62 | 0.82 | 9.83 | 12.22 | -0.11 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 46 | margin | 0.174 | 0.461 | [-0.731, 1.078] | 0.413 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 46 | total | 0.784 | 0.395 | [0.009, 1.559] | 0.391 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 46 | margin | 0.032 | 0.139 | [-0.240, 0.305] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 46 | total | 0.180 | 0.124 | [-0.064, 0.423] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 46 | margin | -0.142 | 0.323 | [-0.775, 0.492] | 0.587 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 46 | total | -0.604 | 0.276 | [-1.146, -0.062] | 0.609 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 46 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 46 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 46 | margin | 0.174 | 0.461 | [-0.731, 1.078] | 0.413 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 46 | total | 0.784 | 0.395 | [0.009, 1.559] | 0.391 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 46 | margin | 0.032 | 0.139 | [-0.240, 0.305] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 46 | total | 0.180 | 0.124 | [-0.064, 0.423] | 0.457 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 46 | margin | -0.043 | 0.053 | [-0.148, 0.061] | 0.152 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 46 | total | 0.033 | 0.078 | [-0.121, 0.186] | 0.174 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 46 | margin | 0.130 | 0.456 | [-0.765, 1.025] | 0.413 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 46 | total | 0.816 | 0.420 | [-0.006, 1.639] | 0.370 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 46 | margin | -0.011 | 0.141 | [-0.287, 0.264] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 46 | total | 0.212 | 0.159 | [-0.100, 0.525] | 0.413 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 46 | 8 | 5 | 33 | 0 | 0.615 | 0.413 | 2.61 |
| DATA_ONLY | total | 46 | 8 | 10 | 28 | 0 | 0.444 | 0.391 | 2.31 |
| HYBRID_30 | margin | 46 | 8 | 5 | 33 | 0 | 0.615 | 0.457 | 0.78 |
| HYBRID_30 | total | 46 | 8 | 10 | 28 | 0 | 0.444 | 0.457 | 0.69 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 8 | 6.35 | 6.31 | 0.250 |
| DATA_ONLY | margin | 1-2 | 11 | 7.35 | 6.86 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.25 | 10.25 | 0.750 |
| DATA_ONLY | margin | 3-5 | 10 | 9.81 | 9.00 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.93 | 16.10 | - |
| DATA_ONLY | total | <=1 | 14 | 11.15 | 11.32 | 0.667 |
| DATA_ONLY | total | 1-2 | 10 | 6.53 | 7.10 | 0.250 |
| DATA_ONLY | total | 2-3 | 7 | 11.31 | 10.50 | 1.000 |
| DATA_ONLY | total | 3-5 | 12 | 10.53 | 8.83 | 0.000 |
| DATA_ONLY | total | >5 | 3 | 20.87 | 14.83 | 0.000 |
| HYBRID_30 | margin | <=1 | 32 | 7.85 | 7.80 | 0.636 |
| HYBRID_30 | margin | 1-2 | 14 | 12.12 | 12.14 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 34 | 9.66 | 9.69 | 0.615 |
| HYBRID_30 | total | 1-2 | 11 | 10.16 | 9.50 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 46}; DATA_ONLY quality states: {'OK': 46}; close centre status: {'OK': 46}.

## Game-centre accuracy — T-30m (57 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 57 | 4 | 10.13 | 12.70 | 1.76 | 10.36 | 13.48 | -1.22 | 0.234 |
| DATA_ONLY | 57 | 4 | 10.51 | 13.12 | 1.48 | 11.32 | 14.38 | 0.13 | 0.247 |
| HYBRID_30 | 57 | 4 | 10.22 | 12.76 | 1.68 | 10.60 | 13.69 | -0.81 | 0.237 |
| market at snapshot | 57 | 4 | 10.13 | 12.70 | 1.76 | 10.36 | 13.48 | -1.22 | - |
| market at close | 57 | 4 | 10.16 | 12.69 | 1.79 | 10.44 | 13.60 | -1.18 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 57 | margin | 0.383 | 0.390 | [-0.381, 1.146] | 0.421 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 57 | total | 0.959 | 0.350 | [0.272, 1.646] | 0.386 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 57 | margin | 0.086 | 0.117 | [-0.144, 0.317] | 0.474 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 57 | total | 0.243 | 0.110 | [0.028, 0.458] | 0.439 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 57 | margin | -0.296 | 0.274 | [-0.833, 0.241] | 0.579 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 57 | total | -0.716 | 0.245 | [-1.195, -0.236] | 0.614 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 57 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 57 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 57 | margin | 0.383 | 0.390 | [-0.381, 1.146] | 0.421 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 57 | total | 0.959 | 0.350 | [0.272, 1.646] | 0.386 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 57 | margin | 0.086 | 0.117 | [-0.144, 0.317] | 0.474 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 57 | total | 0.243 | 0.110 | [0.028, 0.458] | 0.439 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 57 | margin | -0.026 | 0.048 | [-0.119, 0.067] | 0.105 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 57 | total | -0.079 | 0.058 | [-0.193, 0.036] | 0.175 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 57 | margin | 0.356 | 0.386 | [-0.401, 1.114] | 0.404 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 57 | total | 0.880 | 0.360 | [0.174, 1.586] | 0.386 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 57 | margin | 0.060 | 0.121 | [-0.177, 0.298] | 0.491 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 57 | total | 0.164 | 0.127 | [-0.085, 0.413] | 0.456 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 57 | 8 | 4 | 45 | 0 | 0.667 | 0.421 | 2.46 |
| DATA_ONLY | total | 57 | 8 | 8 | 41 | 0 | 0.500 | 0.386 | 2.24 |
| HYBRID_30 | margin | 57 | 8 | 4 | 45 | 0 | 0.667 | 0.474 | 0.74 |
| HYBRID_30 | total | 57 | 8 | 8 | 41 | 0 | 0.500 | 0.439 | 0.67 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 10 | 11.52 | 11.60 | 0.333 |
| DATA_ONLY | margin | 1-2 | 15 | 7.95 | 7.60 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 13 | 11.09 | 9.65 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.93 | 16.10 | - |
| DATA_ONLY | total | <=1 | 19 | 12.20 | 12.34 | 0.500 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 9 | 7.40 | 7.28 | 0.800 |
| DATA_ONLY | total | 3-5 | 14 | 11.30 | 8.71 | 0.500 |
| DATA_ONLY | total | >5 | 4 | 17.50 | 11.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 42 | 9.33 | 9.24 | 0.700 |
| HYBRID_30 | margin | 1-2 | 15 | 12.70 | 12.63 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 43 | 10.62 | 10.65 | 0.538 |
| HYBRID_30 | total | 1-2 | 13 | 9.74 | 8.77 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 57}; DATA_ONLY quality states: {'OK': 57}; close centre status: {'OK': 57}.

## Contract pricing — latest_pregame (4519 contracts, 58 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4519 | 0.1605 | 0.4835 | 0.414 | 0.414 | 4519 | 0.1605 | 0.1603 | 0.1627 |
| DATA_ONLY | 4519 | 0.1703 | 0.5105 | 0.425 | 0.414 | 4519 | 0.1703 | 0.1603 | 0.1627 |
| HYBRID_30 | 4519 | 0.1629 | 0.4899 | 0.414 | 0.414 | 4519 | 0.1629 | 0.1603 | 0.1627 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4519 | 58 | 0.00984 | [0.00117, 0.01821] | 0.00984 | [0.00117, 0.01821] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4519 | 58 | 0.00239 | [-0.00016, 0.00499] | 0.00239 | [-0.00016, 0.00499] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4519 | 58 | -0.00745 | [-0.01390, -0.00097] | -0.00745 | [-0.01390, -0.00097] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4519 | 58 | - | - | 0.00015 | [-0.00071, 0.00100] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4444 | 58 | - | - | -0.00018 | [-0.00122, 0.00080] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4519 | 58 | - | - | 0.00999 | [0.00143, 0.01861] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4444 | 58 | - | - | 0.00986 | [0.00095, 0.01874] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4519 | 58 | - | - | 0.00254 | [-0.00013, 0.00532] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4444 | 58 | - | - | 0.00228 | [-0.00064, 0.00512] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 232, 'GAME_WINNER': 116, 'SPREAD': 1487, 'TEAM_TOTAL': 1582, 'TOTAL': 1102}; settlement: {'SETTLED': 4519}; close: {'OK': 4444, 'OK_STALE': 75}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 705 / 0.055 / 0.043 | 670 / 0.054 / 0.060 | 693 / 0.054 / 0.051 |
| 0.10-0.20 | 727 / 0.145 / 0.165 | 706 / 0.145 / 0.174 | 723 / 0.146 / 0.172 |
| 0.20-0.30 | 530 / 0.249 / 0.274 | 533 / 0.250 / 0.280 | 523 / 0.249 / 0.254 |
| 0.30-0.40 | 455 / 0.351 / 0.347 | 456 / 0.349 / 0.353 | 460 / 0.348 / 0.352 |
| 0.40-0.50 | 463 / 0.450 / 0.454 | 435 / 0.448 / 0.446 | 497 / 0.449 / 0.475 |
| 0.50-0.60 | 438 / 0.547 / 0.546 | 400 / 0.551 / 0.492 | 416 / 0.549 / 0.526 |
| 0.60-0.70 | 288 / 0.650 / 0.601 | 358 / 0.647 / 0.545 | 299 / 0.649 / 0.589 |
| 0.70-0.80 | 237 / 0.751 / 0.743 | 249 / 0.749 / 0.707 | 239 / 0.752 / 0.707 |
| 0.80-0.90 | 236 / 0.849 / 0.864 | 243 / 0.850 / 0.819 | 234 / 0.851 / 0.876 |
| 0.90-1.00 | 440 / 0.954 / 0.943 | 469 / 0.957 / 0.930 | 435 / 0.955 / 0.945 |

## Contract pricing — T-24h (2492 contracts, 32 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2492 | 0.1588 | 0.4791 | 0.413 | 0.385 | 2492 | 0.1588 | 0.1586 | 0.1595 |
| DATA_ONLY | 2492 | 0.1635 | 0.4933 | 0.423 | 0.385 | 2492 | 0.1635 | 0.1586 | 0.1595 |
| HYBRID_30 | 2492 | 0.1589 | 0.4791 | 0.415 | 0.385 | 2492 | 0.1589 | 0.1586 | 0.1595 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2492 | 32 | 0.00475 | [-0.00803, 0.01809] | 0.00475 | [-0.00803, 0.01809] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2492 | 32 | 0.00011 | [-0.00427, 0.00436] | 0.00011 | [-0.00427, 0.00436] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2492 | 32 | -0.00464 | [-0.01444, 0.00500] | -0.00464 | [-0.01444, 0.00500] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2492 | 32 | - | - | 0.00015 | [-0.00081, 0.00123] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2458 | 32 | - | - | 0.00115 | [-0.00041, 0.00294] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2492 | 32 | - | - | 0.00490 | [-0.00788, 0.01796] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2458 | 32 | - | - | 0.00603 | [-0.00687, 0.01929] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2492 | 32 | - | - | 0.00026 | [-0.00414, 0.00454] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2458 | 32 | - | - | 0.00132 | [-0.00346, 0.00557] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 128, 'GAME_WINNER': 64, 'SPREAD': 822, 'TEAM_TOTAL': 870, 'TOTAL': 608}; settlement: {'SETTLED': 2492}; close: {'OK': 2458, 'OK_STALE': 34}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 401 / 0.055 / 0.020 | 376 / 0.054 / 0.035 | 381 / 0.053 / 0.018 |
| 0.10-0.20 | 387 / 0.146 / 0.137 | 392 / 0.146 / 0.143 | 400 / 0.146 / 0.142 |
| 0.20-0.30 | 299 / 0.249 / 0.274 | 291 / 0.251 / 0.285 | 295 / 0.250 / 0.258 |
| 0.30-0.40 | 240 / 0.349 / 0.325 | 252 / 0.349 / 0.313 | 238 / 0.348 / 0.332 |
| 0.40-0.50 | 263 / 0.450 / 0.403 | 235 / 0.447 / 0.379 | 281 / 0.448 / 0.431 |
| 0.50-0.60 | 231 / 0.546 / 0.506 | 218 / 0.550 / 0.417 | 222 / 0.550 / 0.459 |
| 0.60-0.70 | 160 / 0.647 / 0.537 | 201 / 0.648 / 0.537 | 167 / 0.647 / 0.515 |
| 0.70-0.80 | 142 / 0.750 / 0.725 | 135 / 0.749 / 0.719 | 141 / 0.750 / 0.723 |
| 0.80-0.90 | 127 / 0.851 / 0.819 | 134 / 0.847 / 0.806 | 128 / 0.853 / 0.844 |
| 0.90-1.00 | 242 / 0.955 / 0.921 | 258 / 0.956 / 0.915 | 239 / 0.955 / 0.929 |

## Contract pricing — T-6h (3042 contracts, 39 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3042 | 0.1534 | 0.4637 | 0.413 | 0.410 | 3042 | 0.1534 | 0.1538 | 0.1565 |
| DATA_ONLY | 3042 | 0.1588 | 0.4773 | 0.426 | 0.410 | 3042 | 0.1588 | 0.1538 | 0.1565 |
| HYBRID_30 | 3042 | 0.1537 | 0.4648 | 0.414 | 0.410 | 3042 | 0.1537 | 0.1538 | 0.1565 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3042 | 39 | 0.00532 | [-0.00464, 0.01511] | 0.00532 | [-0.00464, 0.01511] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3042 | 39 | 0.00026 | [-0.00240, 0.00270] | 0.00026 | [-0.00240, 0.00270] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3042 | 39 | -0.00506 | [-0.01294, 0.00303] | -0.00506 | [-0.01294, 0.00303] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3042 | 39 | - | - | -0.00036 | [-0.00159, 0.00079] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2978 | 39 | - | - | -0.00035 | [-0.00198, 0.00116] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3042 | 39 | - | - | 0.00496 | [-0.00519, 0.01517] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2978 | 39 | - | - | 0.00514 | [-0.00549, 0.01576] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3042 | 39 | - | - | -0.00010 | [-0.00313, 0.00274] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2978 | 39 | - | - | -0.00005 | [-0.00337, 0.00313] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 156, 'GAME_WINNER': 78, 'SPREAD': 1000, 'TEAM_TOTAL': 1067, 'TOTAL': 741}; settlement: {'SETTLED': 3042}; close: {'OK': 2978, 'OK_STALE': 64}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 484 / 0.055 / 0.048 | 462 / 0.054 / 0.039 | 477 / 0.054 / 0.044 |
| 0.10-0.20 | 476 / 0.144 / 0.147 | 472 / 0.147 / 0.148 | 475 / 0.146 / 0.154 |
| 0.20-0.30 | 363 / 0.249 / 0.248 | 349 / 0.251 / 0.258 | 368 / 0.250 / 0.231 |
| 0.30-0.40 | 307 / 0.351 / 0.349 | 302 / 0.350 / 0.364 | 298 / 0.349 / 0.366 |
| 0.40-0.50 | 314 / 0.450 / 0.449 | 287 / 0.446 / 0.418 | 339 / 0.448 / 0.440 |
| 0.50-0.60 | 289 / 0.546 / 0.516 | 269 / 0.549 / 0.498 | 275 / 0.549 / 0.531 |
| 0.60-0.70 | 199 / 0.650 / 0.608 | 247 / 0.647 / 0.563 | 197 / 0.649 / 0.599 |
| 0.70-0.80 | 155 / 0.754 / 0.768 | 172 / 0.751 / 0.721 | 159 / 0.751 / 0.755 |
| 0.80-0.90 | 166 / 0.851 / 0.898 | 166 / 0.849 / 0.843 | 162 / 0.851 / 0.889 |
| 0.90-1.00 | 289 / 0.956 / 0.962 | 316 / 0.957 / 0.956 | 292 / 0.956 / 0.966 |

## Contract pricing — T-90m (3584 contracts, 46 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3584 | 0.1543 | 0.4684 | 0.415 | 0.394 | 3584 | 0.1543 | 0.1537 | 0.1561 |
| DATA_ONLY | 3584 | 0.1594 | 0.4820 | 0.424 | 0.394 | 3584 | 0.1594 | 0.1537 | 0.1561 |
| HYBRID_30 | 3584 | 0.1564 | 0.4721 | 0.414 | 0.394 | 3584 | 0.1564 | 0.1537 | 0.1561 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3584 | 46 | 0.00508 | [-0.00541, 0.01599] | 0.00508 | [-0.00541, 0.01599] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3584 | 46 | 0.00207 | [-0.00115, 0.00544] | 0.00207 | [-0.00115, 0.00544] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3584 | 46 | -0.00300 | [-0.01121, 0.00469] | -0.00300 | [-0.01121, 0.00469] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3584 | 46 | - | - | 0.00064 | [-0.00040, 0.00179] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3517 | 46 | - | - | 0.00059 | [-0.00080, 0.00206] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3584 | 46 | - | - | 0.00572 | [-0.00492, 0.01722] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3517 | 46 | - | - | 0.00580 | [-0.00491, 0.01739] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3584 | 46 | - | - | 0.00271 | [-0.00069, 0.00610] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3517 | 46 | - | - | 0.00274 | [-0.00078, 0.00634] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 184, 'GAME_WINNER': 92, 'SPREAD': 1180, 'TEAM_TOTAL': 1254, 'TOTAL': 874}; settlement: {'SETTLED': 3584}; close: {'OK': 3517, 'OK_STALE': 67}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 564 / 0.055 / 0.027 | 542 / 0.054 / 0.035 | 558 / 0.054 / 0.030 |
| 0.10-0.20 | 565 / 0.144 / 0.136 | 554 / 0.146 / 0.141 | 564 / 0.146 / 0.145 |
| 0.20-0.30 | 420 / 0.248 / 0.257 | 421 / 0.251 / 0.257 | 427 / 0.250 / 0.244 |
| 0.30-0.40 | 362 / 0.350 / 0.312 | 358 / 0.350 / 0.316 | 350 / 0.349 / 0.346 |
| 0.40-0.50 | 357 / 0.449 / 0.412 | 342 / 0.447 / 0.401 | 401 / 0.449 / 0.429 |
| 0.50-0.60 | 356 / 0.546 / 0.537 | 317 / 0.550 / 0.486 | 322 / 0.549 / 0.491 |
| 0.60-0.70 | 233 / 0.651 / 0.562 | 285 / 0.647 / 0.547 | 241 / 0.650 / 0.560 |
| 0.70-0.80 | 184 / 0.751 / 0.739 | 204 / 0.748 / 0.706 | 187 / 0.751 / 0.711 |
| 0.80-0.90 | 197 / 0.850 / 0.858 | 193 / 0.849 / 0.834 | 190 / 0.851 / 0.868 |
| 0.90-1.00 | 346 / 0.956 / 0.939 | 368 / 0.956 / 0.929 | 344 / 0.956 / 0.945 |

## Contract pricing — T-30m (4442 contracts, 57 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4442 | 0.1609 | 0.4846 | 0.412 | 0.409 | 4442 | 0.1609 | 0.1607 | 0.1632 |
| DATA_ONLY | 4442 | 0.1698 | 0.5092 | 0.425 | 0.409 | 4442 | 0.1698 | 0.1607 | 0.1632 |
| HYBRID_30 | 4442 | 0.1629 | 0.4901 | 0.414 | 0.409 | 4442 | 0.1629 | 0.1607 | 0.1632 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4442 | 57 | 0.00894 | [0.00038, 0.01687] | 0.00894 | [0.00038, 0.01687] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4442 | 57 | 0.00201 | [-0.00043, 0.00440] | 0.00201 | [-0.00043, 0.00440] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4442 | 57 | -0.00694 | [-0.01333, -0.00038] | -0.00694 | [-0.01333, -0.00038] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4442 | 57 | - | - | 0.00014 | [-0.00068, 0.00100] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4367 | 57 | - | - | -0.00019 | [-0.00123, 0.00081] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4442 | 57 | - | - | 0.00908 | [0.00046, 0.01733] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4367 | 57 | - | - | 0.00893 | [0.00022, 0.01733] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4442 | 57 | - | - | 0.00215 | [-0.00028, 0.00471] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4367 | 57 | - | - | 0.00188 | [-0.00070, 0.00463] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 228, 'GAME_WINNER': 114, 'SPREAD': 1462, 'TEAM_TOTAL': 1555, 'TOTAL': 1083}; settlement: {'SETTLED': 4442}; close: {'OK': 4367, 'OK_STALE': 75}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 698 / 0.054 / 0.043 | 660 / 0.054 / 0.058 | 685 / 0.054 / 0.051 |
| 0.10-0.20 | 714 / 0.145 / 0.162 | 693 / 0.145 / 0.172 | 709 / 0.146 / 0.169 |
| 0.20-0.30 | 521 / 0.249 / 0.274 | 523 / 0.250 / 0.275 | 515 / 0.249 / 0.250 |
| 0.30-0.40 | 448 / 0.351 / 0.344 | 449 / 0.349 / 0.347 | 454 / 0.348 / 0.350 |
| 0.40-0.50 | 461 / 0.450 / 0.449 | 424 / 0.448 / 0.434 | 487 / 0.449 / 0.464 |
| 0.50-0.60 | 427 / 0.547 / 0.534 | 395 / 0.551 / 0.486 | 410 / 0.549 / 0.520 |
| 0.60-0.70 | 280 / 0.650 / 0.589 | 354 / 0.648 / 0.540 | 293 / 0.649 / 0.580 |
| 0.70-0.80 | 235 / 0.751 / 0.740 | 245 / 0.749 / 0.702 | 237 / 0.752 / 0.705 |
| 0.80-0.90 | 230 / 0.849 / 0.861 | 239 / 0.850 / 0.816 | 228 / 0.852 / 0.873 |
| 0.90-1.00 | 428 / 0.954 / 0.942 | 460 / 0.957 / 0.928 | 424 / 0.955 / 0.943 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 32 | 8 | 4 | 2 | 18 | 0 | 0.667 [0.300, 0.903] | 0.417 | 0.417 | 0.10 |
| T-24h | DATA_ONLY | total | 32 | 7 | 9 | 3 | 13 | 0 | 0.750 [0.468, 0.911] | 0.440 | 0.360 | 0.30 |
| T-24h | HYBRID_30 (derived) | margin | 32 | 21 | 2 | 1 | 8 | 0 | 0.667 [0.208, 0.939] | 0.455 | 0.455 | 0.09 |
| T-24h | HYBRID_30 (derived) | total | 32 | 22 | 3 | 2 | 5 | 0 | 0.600 [0.231, 0.882] | 0.300 | 0.300 | 0.05 |
| T-6h | DATA_ONLY | margin | 39 | 7 | 7 | 3 | 22 | 0 | 0.700 [0.397, 0.892] | 0.406 | 0.438 | 0.09 |
| T-6h | DATA_ONLY | total | 39 | 12 | 6 | 8 | 13 | 0 | 0.429 [0.214, 0.674] | 0.407 | 0.370 | -0.09 |
| T-6h | HYBRID_30 (derived) | margin | 39 | 28 | 1 | 2 | 8 | 0 | 0.333 [0.061, 0.792] | 0.455 | 0.455 | -0.05 |
| T-6h | HYBRID_30 (derived) | total | 39 | 29 | 3 | 3 | 4 | 0 | 0.500 [0.188, 0.812] | 0.400 | 0.300 | 0.05 |
| T-90m | DATA_ONLY | margin | 46 | 8 | 7 | 2 | 29 | 0 | 0.778 [0.453, 0.937] | 0.421 | 0.421 | 0.05 |
| T-90m | DATA_ONLY | total | 46 | 14 | 4 | 8 | 20 | 0 | 0.333 [0.138, 0.609] | 0.344 | 0.344 | -0.14 |
| T-90m | HYBRID_30 (derived) | margin | 46 | 32 | 1 | 1 | 12 | 0 | 0.500 [0.095, 0.905] | 0.500 | 0.500 | -0.04 |
| T-90m | HYBRID_30 (derived) | total | 46 | 34 | 0 | 5 | 7 | 0 | 0.000 [0.000, 0.434] | 0.250 | 0.250 | -0.33 |
| T-30m | DATA_ONLY | margin | 57 | 10 | 7 | 2 | 38 | 0 | 0.778 [0.453, 0.937] | 0.383 | 0.383 | 0.07 |
| T-30m | DATA_ONLY | total | 57 | 19 | 6 | 6 | 26 | 0 | 0.500 [0.254, 0.746] | 0.316 | 0.316 | -0.05 |
| T-30m | HYBRID_30 (derived) | margin | 57 | 42 | 1 | 1 | 13 | 0 | 0.500 [0.095, 0.905] | 0.467 | 0.467 | -0.03 |
| T-30m | HYBRID_30 (derived) | total | 57 | 43 | 1 | 2 | 11 | 0 | 0.333 [0.061, 0.792] | 0.143 | 0.143 | -0.04 |
| latest_pregame | DATA_ONLY | margin | 58 | 10 | 7 | 2 | 39 | 0 | 0.778 [0.453, 0.937] | 0.375 | 0.375 | 0.07 |
| latest_pregame | DATA_ONLY | total | 58 | 19 | 6 | 6 | 27 | 0 | 0.500 [0.254, 0.746] | 0.308 | 0.308 | -0.05 |
| latest_pregame | HYBRID_30 (derived) | margin | 58 | 43 | 1 | 1 | 13 | 0 | 0.500 [0.095, 0.905] | 0.467 | 0.467 | -0.03 |
| latest_pregame | HYBRID_30 (derived) | total | 58 | 43 | 1 | 2 | 12 | 0 | 0.333 [0.061, 0.792] | 0.133 | 0.133 | -0.03 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 10 | 1 | 2 | 7 | 0 | 0.333 |
| margin | 1-2 | 16 | 3 | 0 | 13 | 0 | 1.000 |
| margin | 2-3 | 14 | 2 | 1 | 11 | 0 | 0.667 |
| margin | 3-5 | 13 | 2 | 1 | 10 | 0 | 0.667 |
| margin | >5 | 5 | 0 | 0 | 5 | 0 | - |
| total | <=1 | 19 | 2 | 2 | 15 | 0 | 0.500 |
| total | 1-2 | 11 | 1 | 3 | 7 | 0 | 0.250 |
| total | 2-3 | 9 | 4 | 1 | 4 | 0 | 0.800 |
| total | 3-5 | 14 | 1 | 1 | 12 | 0 | 0.500 |
| total | >5 | 5 | 0 | 1 | 4 | 0 | 0.000 |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 27 | 5 | 0.800 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 27 | 5 | 0.400 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

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

112 snapshot(s). A contract's terminal state is where it left the existing gate sequence when the model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).

### Newest snapshot 20261004T231904Z (60621 markets)

| stage | markets |
|---|---|
| discovered | 60621 |
| mapped | 52103 |
| supported | 1420 |
| priced | 1420 |
| raw_disagreement | 1077 |
| tradable_book | 1054 |
| data_quality | 312 |
| executable_price | 133 |
| liquidity | 59 |

Terminal states: {'PASS': 60383, 'WATCH': 179, 'BET': 59}

| family | BET | WATCH | PASS |
|---|---|---|---|
| AWARD | 0 | 0 | 875 |
| BOTH_TEAMS_SCORE | 0 | 0 | 256 |
| BOTH_TEAMS_SCORE_N | 0 | 2 | 254 |
| COACH_EVENT | 0 | 0 | 64 |
| CONFERENCE_WINNER | 0 | 0 | 32 |
| DIVISION_WINNER | 0 | 0 | 32 |
| DRAFT | 0 | 0 | 40 |
| FIRST_TD_SCORER | 0 | 0 | 1665 |
| FIRST_TD_TEAM | 0 | 0 | 1911 |
| GAME_EVENT | 0 | 0 | 260 |
| GAME_PLAYER_LEADER | 0 | 0 | 805 |
| GAME_STAT | 0 | 0 | 5 |
| GAME_WINNER | 0 | 14 | 144 |
| HALF_FULL_RESULT | 0 | 0 | 585 |
| MAKE_PLAYOFFS | 0 | 0 | 33 |
| NFL_BUSINESS_EVENT | 0 | 0 | 5 |
| NOT_NFL_OR_UNKNOWN | 0 | 0 | 2 |
| PERIOD_WINNER | 0 | 0 | 1152 |
| PLAYER_AVAILABILITY | 0 | 0 | 23 |
| PLAYER_ROLE_EVENT | 0 | 0 | 177 |
| PLAYER_STAT | 45 | 5 | 25325 |
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
| SPREAD | 3 | 64 | 6924 |
| SUPER_BOWL_EVENT | 0 | 0 | 265 |
| SUPER_BOWL_WINNER | 0 | 0 | 32 |
| TEAM_STAT | 0 | 0 | 1566 |
| TEAM_TOTAL | 7 | 32 | 3375 |
| TEAM_WINS_BY_WEEK | 0 | 0 | 728 |
| TOTAL | 4 | 62 | 5649 |
| TOTAL_TD | 0 | 0 | 214 |
| TRANSACTION_EVENT | 0 | 0 | 314 |
| UNKNOWN_NEEDS_CLASSIFICATION | 0 | 0 | 386 |
| WEEK_EVENT | 0 | 0 | 32 |
| WEEK_LEADER | 0 | 0 | 482 |
| WIN_MARGIN_BUCKET | 0 | 0 | 448 |

| rejection reason | n |
|---|---|
| POST_KICKOFF_EXCLUDED | 44930 |
| unmapped | 8518 |
| UNSUPPORTED_RULES | 3403 |
| UNSUPPORTED_MODEL | 2334 |
| quality flags ['availability_stale'] | 740 |
| no positive disagreement against either executable ask | 343 |
| no order book observed for this ticker (books are captured i | 74 |
| book not tradable for ranking | 23 |
| UNSUPPORTED_IDENTITY | 16 |
| ask 0.91 above the zero-net-EV ceiling 0.90 | 6 |
| ask 0.99 above the zero-net-EV ceiling 0.98 | 6 |
| ask 0.63 above the zero-net-EV ceiling 0.61 | 5 |
| ask 0.51 above the zero-net-EV ceiling 0.49 | 4 |
| ask 0.39 above the zero-net-EV ceiling 0.37 | 4 |
| ask 0.18 above the zero-net-EV ceiling 0.17 | 4 |

WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee schedule (`watch_ceiling`). Not replayed: ['portfolio_risk_policy (needs a stake and bankroll)', "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own confirmation is the STALE_DATA support state)"].

Across all 112 snapshots (repeated markets counted per snapshot): {'PASS': 4189018, 'WATCH': 84441, 'BET': 69755}.

