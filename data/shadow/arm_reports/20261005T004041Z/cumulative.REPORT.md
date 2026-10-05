# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 61 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 3647 | 61 | 4 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 35 | 35 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 42 | 42 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 49 | 49 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 60 | 60 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 61 | 61 | 4 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_DEN_SF | 2026-10-04T20:25 | 40 | CURRENT | 2.50 | 48.00 | 10 | 38 | 2.5/48.0 (kalshi_implied) | 2.5/48.5 (OK) |
|  |  |  | DATA_ONLY | 3.98 | 47.63 |  |  |  |  |
|  |  |  | HYBRID_30 | 2.94 | 47.89 |  |  |  |  |
| 2026_04_KC_LV | 2026-10-04T20:25 | 40 | CURRENT | -4.50 | 47.50 | -3 | 57 | -4.5/47.5 (kalshi_implied) | -5.5/47.5 (OK) |
|  |  |  | DATA_ONLY | -5.46 | 43.83 |  |  |  |  |
|  |  |  | HYBRID_30 | -4.79 | 46.40 |  |  |  |  |
| 2026_04_LAC_SEA | 2026-10-04T20:25 | 40 | CURRENT | 7.00 | 44.00 | 7 | 53 | 7.0/44.0 (kalshi_implied) | 7.5/42.0 (OK) |
|  |  |  | DATA_ONLY | 12.45 | 41.32 |  |  |  |  |
|  |  |  | HYBRID_30 | 8.63 | 43.20 |  |  |  |  |

## Game-centre accuracy — latest_pregame (61 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 61 | 4 | 9.69 | 12.33 | 1.43 | 10.43 | 13.39 | -1.57 | 0.226 |
| DATA_ONLY | 61 | 4 | 10.16 | 12.76 | 1.23 | 11.52 | 14.44 | -0.50 | 0.237 |
| HYBRID_30 | 61 | 4 | 9.80 | 12.39 | 1.37 | 10.72 | 13.65 | -1.25 | 0.229 |
| market at snapshot | 61 | 4 | 9.69 | 12.33 | 1.43 | 10.43 | 13.39 | -1.57 | - |
| market at close | 61 | 4 | 9.74 | 12.32 | 1.44 | 10.55 | 13.53 | -1.55 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 61 | margin | 0.467 | 0.375 | [-0.269, 1.203] | 0.410 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 61 | total | 1.085 | 0.340 | [0.417, 1.752] | 0.377 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 61 | margin | 0.114 | 0.113 | [-0.108, 0.335] | 0.459 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 61 | total | 0.284 | 0.106 | [0.075, 0.492] | 0.426 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 61 | margin | -0.353 | 0.264 | [-0.870, 0.163] | 0.590 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 61 | total | -0.801 | 0.237 | [-1.266, -0.336] | 0.623 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 61 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 61 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 61 | margin | 0.467 | 0.375 | [-0.269, 1.203] | 0.410 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 61 | total | 1.085 | 0.340 | [0.417, 1.752] | 0.377 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 61 | margin | 0.114 | 0.113 | [-0.108, 0.335] | 0.459 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 61 | total | 0.284 | 0.106 | [0.075, 0.492] | 0.426 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 61 | margin | -0.049 | 0.048 | [-0.143, 0.044] | 0.131 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 61 | total | -0.115 | 0.063 | [-0.239, 0.009] | 0.197 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 61 | margin | 0.418 | 0.371 | [-0.309, 1.144] | 0.410 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 61 | total | 0.970 | 0.349 | [0.286, 1.654] | 0.377 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 61 | margin | 0.064 | 0.116 | [-0.163, 0.291] | 0.492 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 61 | total | 0.169 | 0.125 | [-0.076, 0.414] | 0.459 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 61 | 10 | 4 | 47 | 0 | 0.714 | 0.410 | 2.46 |
| DATA_ONLY | total | 61 | 9 | 9 | 43 | 0 | 0.500 | 0.377 | 2.29 |
| HYBRID_30 | margin | 61 | 10 | 4 | 47 | 0 | 0.714 | 0.459 | 0.74 |
| HYBRID_30 | total | 61 | 9 | 9 | 43 | 0 | 0.500 | 0.426 | 0.69 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 11 | 10.70 | 10.68 | 0.500 |
| DATA_ONLY | margin | 1-2 | 17 | 7.73 | 7.41 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 13 | 11.09 | 9.65 | 0.667 |
| DATA_ONLY | margin | >5 | 6 | 13.35 | 13.42 | 1.000 |
| DATA_ONLY | total | <=1 | 20 | 12.07 | 12.22 | 0.400 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 10 | 7.83 | 7.45 | 0.833 |
| DATA_ONLY | total | 3-5 | 15 | 11.42 | 8.77 | 0.500 |
| DATA_ONLY | total | >5 | 5 | 18.60 | 12.70 | 0.000 |
| HYBRID_30 | margin | <=1 | 45 | 9.02 | 8.92 | 0.727 |
| HYBRID_30 | margin | 1-2 | 16 | 12.01 | 11.84 | 0.667 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 45 | 10.59 | 10.60 | 0.533 |
| HYBRID_30 | total | 1-2 | 15 | 10.42 | 9.40 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 61}; DATA_ONLY quality states: {'OK': 61}; close centre status: {'OK': 61}.

## Game-centre accuracy — T-24h (35 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 35 | 4 | 9.47 | 11.90 | 1.76 | 9.87 | 12.06 | 1.04 | 0.223 |
| DATA_ONLY | 35 | 4 | 9.70 | 12.19 | 1.49 | 10.55 | 12.94 | 1.90 | 0.219 |
| HYBRID_30 | 35 | 4 | 9.52 | 11.89 | 1.68 | 10.02 | 12.26 | 1.30 | 0.220 |
| market at snapshot | 35 | 4 | 9.47 | 11.90 | 1.76 | 9.87 | 12.06 | 1.04 | - |
| market at close | 35 | 4 | 9.56 | 11.89 | 1.90 | 9.73 | 12.04 | 0.96 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 35 | margin | 0.231 | 0.567 | [-0.879, 1.342] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 35 | total | 0.682 | 0.472 | [-0.243, 1.606] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 35 | margin | 0.053 | 0.171 | [-0.281, 0.388] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 35 | total | 0.144 | 0.151 | [-0.151, 0.439] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 35 | margin | -0.178 | 0.397 | [-0.956, 0.600] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 35 | total | -0.538 | 0.328 | [-1.180, 0.105] | 0.600 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 35 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 35 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 35 | margin | 0.231 | 0.567 | [-0.879, 1.342] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 35 | total | 0.682 | 0.472 | [-0.243, 1.606] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 35 | margin | 0.053 | 0.171 | [-0.281, 0.388] | 0.457 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 35 | total | 0.144 | 0.151 | [-0.151, 0.439] | 0.457 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 35 | margin | -0.086 | 0.078 | [-0.239, 0.067] | 0.229 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 35 | total | 0.143 | 0.122 | [-0.097, 0.382] | 0.143 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 35 | margin | 0.146 | 0.560 | [-0.953, 1.244] | 0.457 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 35 | total | 0.824 | 0.443 | [-0.044, 1.693] | 0.343 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 35 | margin | -0.032 | 0.177 | [-0.379, 0.314] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 35 | total | 0.287 | 0.153 | [-0.013, 0.587] | 0.314 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 35 | 6 | 7 | 22 | 0 | 0.462 | 0.429 | 2.72 |
| DATA_ONLY | total | 35 | 13 | 4 | 18 | 0 | 0.765 | 0.457 | 2.51 |
| HYBRID_30 | margin | 35 | 6 | 7 | 22 | 0 | 0.462 | 0.457 | 0.82 |
| HYBRID_30 | total | 35 | 13 | 4 | 18 | 0 | 0.765 | 0.457 | 0.75 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 7.25 | 7.17 | 0.286 |
| DATA_ONLY | margin | 1-2 | 6 | 5.51 | 5.25 | 1.000 |
| DATA_ONLY | margin | 2-3 | 6 | 11.65 | 11.58 | - |
| DATA_ONLY | margin | 3-5 | 9 | 10.74 | 9.33 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.95 | 16.40 | 0.500 |
| DATA_ONLY | total | <=1 | 9 | 9.49 | 9.67 | 0.800 |
| DATA_ONLY | total | 1-2 | 4 | 9.99 | 9.38 | 0.000 |
| DATA_ONLY | total | 2-3 | 8 | 10.41 | 10.62 | 1.000 |
| DATA_ONLY | total | 3-5 | 12 | 11.21 | 10.12 | 0.600 |
| DATA_ONLY | total | >5 | 2 | 13.07 | 7.25 | 1.000 |
| HYBRID_30 | margin | <=1 | 23 | 7.77 | 7.76 | 0.400 |
| HYBRID_30 | margin | 1-2 | 11 | 12.02 | 11.68 | 0.500 |
| HYBRID_30 | margin | 2-3 | 1 | 22.29 | 24.50 | 1.000 |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 24 | 10.20 | 10.29 | 0.833 |
| HYBRID_30 | total | 1-2 | 11 | 9.61 | 8.95 | 0.600 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 35}; DATA_ONLY quality states: {'OK': 35}; close centre status: {'OK': 35}.

## Game-centre accuracy — T-6h (42 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 42 | 4 | 8.89 | 11.67 | 0.25 | 9.23 | 10.88 | -1.75 | 0.237 |
| DATA_ONLY | 42 | 4 | 9.15 | 11.62 | 0.17 | 10.11 | 11.99 | -0.65 | 0.231 |
| HYBRID_30 | 42 | 4 | 8.96 | 11.57 | 0.23 | 9.41 | 11.15 | -1.42 | 0.232 |
| market at snapshot | 42 | 4 | 8.89 | 11.67 | 0.25 | 9.23 | 10.88 | -1.75 | - |
| market at close | 42 | 4 | 8.99 | 11.69 | 0.30 | 9.33 | 11.04 | -1.79 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 42 | margin | 0.259 | 0.483 | [-0.688, 1.206] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 42 | total | 0.883 | 0.411 | [0.077, 1.688] | 0.405 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 42 | margin | 0.064 | 0.145 | [-0.221, 0.349] | 0.452 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 42 | total | 0.187 | 0.127 | [-0.062, 0.436] | 0.452 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 42 | margin | -0.195 | 0.339 | [-0.858, 0.469] | 0.571 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 42 | total | -0.695 | 0.294 | [-1.272, -0.118] | 0.619 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 42 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 42 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 42 | margin | 0.259 | 0.483 | [-0.688, 1.206] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 42 | total | 0.883 | 0.411 | [0.077, 1.688] | 0.405 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 42 | margin | 0.064 | 0.145 | [-0.221, 0.349] | 0.452 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 42 | total | 0.187 | 0.127 | [-0.062, 0.436] | 0.452 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 42 | margin | -0.095 | 0.089 | [-0.270, 0.079] | 0.238 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 42 | total | -0.107 | 0.111 | [-0.325, 0.111] | 0.262 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 42 | margin | 0.164 | 0.476 | [-0.769, 1.097] | 0.452 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 42 | total | 0.775 | 0.442 | [-0.091, 1.642] | 0.405 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 42 | margin | -0.031 | 0.157 | [-0.338, 0.276] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 42 | total | 0.080 | 0.176 | [-0.265, 0.425] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 42 | 10 | 5 | 27 | 0 | 0.667 | 0.429 | 2.59 |
| DATA_ONLY | total | 42 | 10 | 11 | 21 | 0 | 0.476 | 0.405 | 2.29 |
| HYBRID_30 | margin | 42 | 10 | 5 | 27 | 0 | 0.667 | 0.452 | 0.78 |
| HYBRID_30 | total | 42 | 10 | 11 | 21 | 0 | 0.476 | 0.452 | 0.69 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 8 | 8.66 | 8.62 | 0.600 |
| DATA_ONLY | margin | 1-2 | 12 | 8.50 | 8.04 | 0.667 |
| DATA_ONLY | margin | 2-3 | 7 | 10.98 | 10.71 | 1.000 |
| DATA_ONLY | margin | 3-5 | 10 | 8.10 | 7.20 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 11.04 | 12.20 | 0.500 |
| DATA_ONLY | total | <=1 | 13 | 8.74 | 8.77 | 0.600 |
| DATA_ONLY | total | 1-2 | 10 | 9.82 | 10.00 | 0.667 |
| DATA_ONLY | total | 2-3 | 6 | 9.11 | 9.08 | 0.000 |
| DATA_ONLY | total | 3-5 | 9 | 11.11 | 9.44 | 0.200 |
| DATA_ONLY | total | >5 | 4 | 14.53 | 8.50 | 0.667 |
| HYBRID_30 | margin | <=1 | 30 | 8.61 | 8.58 | 0.750 |
| HYBRID_30 | margin | 1-2 | 12 | 9.83 | 9.67 | 0.333 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 32 | 9.36 | 9.31 | 0.467 |
| HYBRID_30 | total | 1-2 | 9 | 8.32 | 7.89 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 42}; DATA_ONLY quality states: {'OK': 42}; close centre status: {'OK': 42}.

## Game-centre accuracy — T-90m (49 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 49 | 4 | 8.76 | 11.31 | 0.57 | 9.87 | 12.16 | -0.21 | 0.234 |
| DATA_ONLY | 49 | 4 | 9.01 | 11.49 | 0.36 | 10.69 | 13.04 | 0.68 | 0.232 |
| HYBRID_30 | 49 | 4 | 8.81 | 11.28 | 0.51 | 10.06 | 12.36 | 0.06 | 0.232 |
| market at snapshot | 49 | 4 | 8.76 | 11.31 | 0.57 | 9.87 | 12.16 | -0.21 | - |
| market at close | 49 | 4 | 8.82 | 11.32 | 0.57 | 9.86 | 12.12 | -0.31 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 49 | margin | 0.253 | 0.445 | [-0.620, 1.126] | 0.408 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 49 | total | 0.827 | 0.376 | [0.089, 1.565] | 0.388 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 49 | margin | 0.057 | 0.134 | [-0.206, 0.320] | 0.449 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 49 | total | 0.196 | 0.118 | [-0.036, 0.428] | 0.449 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 49 | margin | -0.196 | 0.312 | [-0.808, 0.416] | 0.592 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 49 | total | -0.631 | 0.263 | [-1.147, -0.116] | 0.612 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 49 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 49 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 49 | margin | 0.253 | 0.445 | [-0.620, 1.126] | 0.408 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 49 | total | 0.827 | 0.376 | [0.089, 1.565] | 0.388 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 49 | margin | 0.057 | 0.134 | [-0.206, 0.320] | 0.449 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 49 | total | 0.196 | 0.118 | [-0.036, 0.428] | 0.449 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 49 | margin | -0.061 | 0.054 | [-0.167, 0.044] | 0.163 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 49 | total | 0.010 | 0.075 | [-0.137, 0.157] | 0.204 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 49 | margin | 0.192 | 0.441 | [-0.672, 1.056] | 0.429 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 49 | total | 0.837 | 0.400 | [0.054, 1.621] | 0.367 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 49 | margin | -0.004 | 0.137 | [-0.271, 0.264] | 0.510 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 49 | total | 0.206 | 0.152 | [-0.091, 0.504] | 0.429 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 49 | 9 | 5 | 35 | 0 | 0.643 | 0.408 | 2.60 |
| DATA_ONLY | total | 49 | 9 | 11 | 29 | 0 | 0.450 | 0.388 | 2.27 |
| HYBRID_30 | margin | 49 | 9 | 5 | 35 | 0 | 0.643 | 0.449 | 0.78 |
| HYBRID_30 | total | 49 | 9 | 11 | 29 | 0 | 0.450 | 0.449 | 0.68 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 5.92 | 5.78 | 0.400 |
| DATA_ONLY | margin | 1-2 | 12 | 7.24 | 6.92 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.25 | 10.25 | 0.750 |
| DATA_ONLY | margin | 3-5 | 11 | 9.41 | 8.23 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.93 | 16.10 | - |
| DATA_ONLY | total | <=1 | 15 | 11.05 | 11.23 | 0.571 |
| DATA_ONLY | total | 1-2 | 11 | 6.99 | 7.41 | 0.400 |
| DATA_ONLY | total | 2-3 | 7 | 11.31 | 10.50 | 1.000 |
| DATA_ONLY | total | 3-5 | 13 | 10.73 | 8.88 | 0.000 |
| DATA_ONLY | total | >5 | 3 | 20.87 | 14.83 | 0.000 |
| HYBRID_30 | margin | <=1 | 34 | 7.65 | 7.60 | 0.667 |
| HYBRID_30 | margin | 1-2 | 15 | 11.45 | 11.37 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 36 | 9.70 | 9.72 | 0.600 |
| HYBRID_30 | total | 1-2 | 12 | 10.20 | 9.50 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 49}; DATA_ONLY quality states: {'OK': 49}; close centre status: {'OK': 49}.

## Game-centre accuracy — T-30m (60 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 60 | 4 | 9.78 | 12.42 | 1.52 | 10.32 | 13.31 | -1.30 | 0.228 |
| DATA_ONLY | 60 | 4 | 10.22 | 12.84 | 1.36 | 11.33 | 14.25 | -0.13 | 0.239 |
| HYBRID_30 | 60 | 4 | 9.88 | 12.47 | 1.47 | 10.58 | 13.54 | -0.95 | 0.231 |
| market at snapshot | 60 | 4 | 9.78 | 12.42 | 1.52 | 10.32 | 13.31 | -1.30 | - |
| market at close | 60 | 4 | 9.82 | 12.41 | 1.54 | 10.43 | 13.45 | -1.28 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 60 | margin | 0.446 | 0.381 | [-0.301, 1.192] | 0.417 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 60 | total | 1.010 | 0.338 | [0.348, 1.672] | 0.383 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 60 | margin | 0.107 | 0.115 | [-0.118, 0.332] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 60 | total | 0.261 | 0.106 | [0.053, 0.468] | 0.433 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 60 | margin | -0.339 | 0.268 | [-0.864, 0.186] | 0.583 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 60 | total | -0.750 | 0.236 | [-1.212, -0.288] | 0.617 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 60 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 60 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 60 | margin | 0.446 | 0.381 | [-0.301, 1.192] | 0.417 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 60 | total | 1.010 | 0.338 | [0.348, 1.672] | 0.383 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 60 | margin | 0.107 | 0.115 | [-0.118, 0.332] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 60 | total | 0.261 | 0.106 | [0.053, 0.468] | 0.433 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 60 | margin | -0.050 | 0.049 | [-0.145, 0.045] | 0.133 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 60 | total | -0.117 | 0.064 | [-0.243, 0.010] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 60 | margin | 0.396 | 0.376 | [-0.342, 1.133] | 0.417 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 60 | total | 0.894 | 0.346 | [0.215, 1.573] | 0.383 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 60 | margin | 0.057 | 0.118 | [-0.174, 0.287] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 60 | total | 0.144 | 0.124 | [-0.100, 0.388] | 0.467 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 60 | 10 | 4 | 46 | 0 | 0.714 | 0.417 | 2.47 |
| DATA_ONLY | total | 60 | 9 | 9 | 42 | 0 | 0.500 | 0.383 | 2.24 |
| HYBRID_30 | margin | 60 | 10 | 4 | 46 | 0 | 0.714 | 0.467 | 0.74 |
| HYBRID_30 | total | 60 | 9 | 9 | 42 | 0 | 0.500 | 0.433 | 0.67 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 11 | 10.70 | 10.68 | 0.500 |
| DATA_ONLY | margin | 1-2 | 16 | 7.82 | 7.59 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 13 | 11.09 | 9.65 | 0.667 |
| DATA_ONLY | margin | >5 | 6 | 13.35 | 13.42 | 1.000 |
| DATA_ONLY | total | <=1 | 20 | 12.07 | 12.22 | 0.400 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 10 | 7.83 | 7.45 | 0.833 |
| DATA_ONLY | total | 3-5 | 15 | 11.42 | 8.77 | 0.500 |
| DATA_ONLY | total | >5 | 4 | 17.50 | 11.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 44 | 9.11 | 9.02 | 0.727 |
| HYBRID_30 | margin | 1-2 | 16 | 12.01 | 11.84 | 0.667 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 45 | 10.59 | 10.60 | 0.533 |
| HYBRID_30 | total | 1-2 | 14 | 9.80 | 8.82 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 60}; DATA_ONLY quality states: {'OK': 60}; close centre status: {'OK': 60}.

## Contract pricing — latest_pregame (4752 contracts, 61 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4752 | 0.1583 | 0.4779 | 0.414 | 0.415 | 4752 | 0.1583 | 0.1582 | 0.1605 |
| DATA_ONLY | 4752 | 0.1680 | 0.5043 | 0.425 | 0.415 | 4752 | 0.1680 | 0.1582 | 0.1605 |
| HYBRID_30 | 4752 | 0.1604 | 0.4835 | 0.415 | 0.415 | 4752 | 0.1604 | 0.1582 | 0.1605 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4752 | 61 | 0.00974 | [0.00144, 0.01813] | 0.00974 | [0.00144, 0.01813] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4752 | 61 | 0.00206 | [-0.00058, 0.00471] | 0.00206 | [-0.00058, 0.00471] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4752 | 61 | -0.00768 | [-0.01393, -0.00154] | -0.00768 | [-0.01393, -0.00154] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4752 | 61 | - | - | 0.00015 | [-0.00070, 0.00095] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4675 | 61 | - | - | -0.00020 | [-0.00124, 0.00075] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4752 | 61 | - | - | 0.00988 | [0.00133, 0.01820] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4675 | 61 | - | - | 0.00972 | [0.00093, 0.01833] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4752 | 61 | - | - | 0.00221 | [-0.00053, 0.00489] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4675 | 61 | - | - | 0.00192 | [-0.00099, 0.00476] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 244, 'GAME_WINNER': 122, 'SPREAD': 1564, 'TEAM_TOTAL': 1663, 'TOTAL': 1159}; settlement: {'SETTLED': 4752}; close: {'OK': 4675, 'OK_STALE': 77}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 738 / 0.055 / 0.041 | 711 / 0.054 / 0.056 | 728 / 0.054 / 0.048 |
| 0.10-0.20 | 765 / 0.145 / 0.157 | 741 / 0.145 / 0.167 | 761 / 0.146 / 0.163 |
| 0.20-0.30 | 559 / 0.249 / 0.268 | 557 / 0.250 / 0.280 | 550 / 0.249 / 0.249 |
| 0.30-0.40 | 475 / 0.351 / 0.352 | 477 / 0.350 / 0.356 | 480 / 0.348 / 0.358 |
| 0.40-0.50 | 484 / 0.450 / 0.461 | 457 / 0.448 / 0.455 | 520 / 0.449 / 0.477 |
| 0.50-0.60 | 463 / 0.547 / 0.551 | 419 / 0.551 / 0.494 | 441 / 0.549 / 0.533 |
| 0.60-0.70 | 303 / 0.650 / 0.611 | 378 / 0.648 / 0.553 | 315 / 0.649 / 0.606 |
| 0.70-0.80 | 251 / 0.751 / 0.749 | 264 / 0.749 / 0.716 | 250 / 0.751 / 0.716 |
| 0.80-0.90 | 248 / 0.850 / 0.867 | 257 / 0.849 / 0.829 | 247 / 0.851 / 0.879 |
| 0.90-1.00 | 466 / 0.955 / 0.946 | 491 / 0.956 / 0.933 | 460 / 0.955 / 0.948 |

## Contract pricing — T-24h (2725 contracts, 35 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2725 | 0.1550 | 0.4695 | 0.414 | 0.390 | 2725 | 0.1550 | 0.1550 | 0.1560 |
| DATA_ONLY | 2725 | 0.1601 | 0.4839 | 0.423 | 0.390 | 2725 | 0.1601 | 0.1550 | 0.1560 |
| HYBRID_30 | 2725 | 0.1552 | 0.4695 | 0.415 | 0.390 | 2725 | 0.1552 | 0.1550 | 0.1560 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2725 | 35 | 0.00508 | [-0.00727, 0.01895] | 0.00508 | [-0.00727, 0.01895] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2725 | 35 | 0.00015 | [-0.00393, 0.00484] | 0.00015 | [-0.00393, 0.00484] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2725 | 35 | -0.00493 | [-0.01482, 0.00356] | -0.00493 | [-0.01482, 0.00356] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2725 | 35 | - | - | 0.00006 | [-0.00091, 0.00100] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2689 | 35 | - | - | 0.00088 | [-0.00069, 0.00239] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2725 | 35 | - | - | 0.00514 | [-0.00684, 0.01902] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2689 | 35 | - | - | 0.00609 | [-0.00597, 0.01975] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2725 | 35 | - | - | 0.00021 | [-0.00392, 0.00478] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2689 | 35 | - | - | 0.00108 | [-0.00295, 0.00544] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 140, 'GAME_WINNER': 70, 'SPREAD': 899, 'TEAM_TOTAL': 951, 'TOTAL': 665}; settlement: {'SETTLED': 2725}; close: {'OK': 2689, 'OK_STALE': 36}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 433 / 0.055 / 0.018 | 417 / 0.054 / 0.031 | 417 / 0.053 / 0.017 |
| 0.10-0.20 | 425 / 0.145 / 0.125 | 425 / 0.146 / 0.132 | 440 / 0.146 / 0.130 |
| 0.20-0.30 | 329 / 0.249 / 0.264 | 317 / 0.250 / 0.287 | 320 / 0.250 / 0.259 |
| 0.30-0.40 | 263 / 0.349 / 0.335 | 272 / 0.349 / 0.324 | 261 / 0.348 / 0.337 |
| 0.40-0.50 | 286 / 0.450 / 0.416 | 257 / 0.447 / 0.397 | 307 / 0.449 / 0.440 |
| 0.50-0.60 | 253 / 0.546 / 0.522 | 238 / 0.550 / 0.429 | 241 / 0.550 / 0.477 |
| 0.60-0.70 | 175 / 0.647 / 0.571 | 221 / 0.649 / 0.552 | 183 / 0.647 / 0.546 |
| 0.70-0.80 | 156 / 0.751 / 0.737 | 150 / 0.749 / 0.733 | 152 / 0.749 / 0.743 |
| 0.80-0.90 | 138 / 0.852 / 0.826 | 149 / 0.847 / 0.826 | 142 / 0.852 / 0.852 |
| 0.90-1.00 | 267 / 0.955 / 0.929 | 279 / 0.956 / 0.921 | 262 / 0.956 / 0.935 |

## Contract pricing — T-6h (3275 contracts, 42 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3275 | 0.1508 | 0.4570 | 0.414 | 0.413 | 3275 | 0.1508 | 0.1511 | 0.1537 |
| DATA_ONLY | 3275 | 0.1563 | 0.4707 | 0.425 | 0.413 | 3275 | 0.1563 | 0.1511 | 0.1537 |
| HYBRID_30 | 3275 | 0.1513 | 0.4584 | 0.413 | 0.413 | 3275 | 0.1513 | 0.1511 | 0.1537 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3275 | 42 | 0.00545 | [-0.00369, 0.01491] | 0.00545 | [-0.00369, 0.01491] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3275 | 42 | 0.00050 | [-0.00233, 0.00315] | 0.00050 | [-0.00233, 0.00315] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3275 | 42 | -0.00495 | [-0.01286, 0.00187] | -0.00495 | [-0.01286, 0.00187] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3275 | 42 | - | - | -0.00030 | [-0.00131, 0.00075] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3209 | 42 | - | - | -0.00034 | [-0.00183, 0.00098] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3275 | 42 | - | - | 0.00515 | [-0.00411, 0.01517] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3209 | 42 | - | - | 0.00527 | [-0.00424, 0.01584] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3275 | 42 | - | - | 0.00020 | [-0.00285, 0.00326] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3209 | 42 | - | - | 0.00021 | [-0.00298, 0.00320] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 168, 'GAME_WINNER': 84, 'SPREAD': 1077, 'TEAM_TOTAL': 1148, 'TOTAL': 798}; settlement: {'SETTLED': 3275}; close: {'OK': 3209, 'OK_STALE': 66}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 518 / 0.055 / 0.044 | 503 / 0.054 / 0.036 | 519 / 0.054 / 0.040 |
| 0.10-0.20 | 513 / 0.144 / 0.136 | 506 / 0.146 / 0.140 | 511 / 0.146 / 0.143 |
| 0.20-0.30 | 394 / 0.249 / 0.241 | 374 / 0.250 / 0.259 | 395 / 0.250 / 0.235 |
| 0.30-0.40 | 326 / 0.351 / 0.362 | 322 / 0.350 / 0.370 | 317 / 0.349 / 0.375 |
| 0.40-0.50 | 333 / 0.450 / 0.456 | 310 / 0.446 / 0.432 | 367 / 0.448 / 0.452 |
| 0.50-0.60 | 314 / 0.545 / 0.522 | 288 / 0.549 / 0.500 | 293 / 0.549 / 0.529 |
| 0.60-0.70 | 215 / 0.650 / 0.623 | 267 / 0.648 / 0.573 | 209 / 0.649 / 0.617 |
| 0.70-0.80 | 169 / 0.753 / 0.775 | 187 / 0.751 / 0.733 | 173 / 0.750 / 0.769 |
| 0.80-0.90 | 180 / 0.852 / 0.900 | 180 / 0.849 / 0.856 | 175 / 0.851 / 0.891 |
| 0.90-1.00 | 313 / 0.956 / 0.965 | 338 / 0.957 / 0.959 | 316 / 0.956 / 0.968 |

## Contract pricing — T-90m (3817 contracts, 49 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3817 | 0.1520 | 0.4624 | 0.415 | 0.397 | 3817 | 0.1520 | 0.1514 | 0.1538 |
| DATA_ONLY | 3817 | 0.1572 | 0.4760 | 0.424 | 0.397 | 3817 | 0.1572 | 0.1514 | 0.1538 |
| HYBRID_30 | 3817 | 0.1540 | 0.4660 | 0.415 | 0.397 | 3817 | 0.1540 | 0.1514 | 0.1538 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3817 | 49 | 0.00520 | [-0.00437, 0.01520] | 0.00520 | [-0.00437, 0.01520] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3817 | 49 | 0.00204 | [-0.00110, 0.00527] | 0.00204 | [-0.00110, 0.00527] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3817 | 49 | -0.00316 | [-0.01061, 0.00384] | -0.00316 | [-0.01061, 0.00384] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3817 | 49 | - | - | 0.00065 | [-0.00045, 0.00173] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3748 | 49 | - | - | 0.00053 | [-0.00083, 0.00191] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3817 | 49 | - | - | 0.00585 | [-0.00416, 0.01602] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3748 | 49 | - | - | 0.00586 | [-0.00432, 0.01619] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3817 | 49 | - | - | 0.00269 | [-0.00047, 0.00612] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3748 | 49 | - | - | 0.00264 | [-0.00069, 0.00615] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 196, 'GAME_WINNER': 98, 'SPREAD': 1257, 'TEAM_TOTAL': 1335, 'TOTAL': 931}; settlement: {'SETTLED': 3817}; close: {'OK': 3748, 'OK_STALE': 69}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 597 / 0.055 / 0.025 | 583 / 0.054 / 0.033 | 596 / 0.054 / 0.029 |
| 0.10-0.20 | 601 / 0.144 / 0.128 | 588 / 0.146 / 0.134 | 601 / 0.146 / 0.136 |
| 0.20-0.30 | 451 / 0.248 / 0.253 | 446 / 0.250 / 0.258 | 454 / 0.250 / 0.244 |
| 0.30-0.40 | 384 / 0.350 / 0.320 | 378 / 0.350 / 0.323 | 371 / 0.349 / 0.353 |
| 0.40-0.50 | 374 / 0.449 / 0.420 | 365 / 0.447 / 0.414 | 425 / 0.449 / 0.435 |
| 0.50-0.60 | 382 / 0.546 / 0.542 | 336 / 0.550 / 0.488 | 345 / 0.550 / 0.499 |
| 0.60-0.70 | 250 / 0.650 / 0.580 | 305 / 0.647 / 0.557 | 254 / 0.650 / 0.579 |
| 0.70-0.80 | 197 / 0.751 / 0.746 | 219 / 0.748 / 0.717 | 199 / 0.750 / 0.724 |
| 0.80-0.90 | 210 / 0.850 / 0.862 | 207 / 0.849 / 0.845 | 204 / 0.850 / 0.873 |
| 0.90-1.00 | 371 / 0.956 / 0.943 | 390 / 0.956 / 0.933 | 368 / 0.956 / 0.948 |

## Contract pricing — T-30m (4675 contracts, 60 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4675 | 0.1587 | 0.4789 | 0.413 | 0.411 | 4675 | 0.1587 | 0.1585 | 0.1609 |
| DATA_ONLY | 4675 | 0.1675 | 0.5030 | 0.425 | 0.411 | 4675 | 0.1675 | 0.1585 | 0.1609 |
| HYBRID_30 | 4675 | 0.1603 | 0.4836 | 0.414 | 0.411 | 4675 | 0.1603 | 0.1585 | 0.1609 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4675 | 60 | 0.00888 | [0.00046, 0.01735] | 0.00888 | [0.00046, 0.01735] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4675 | 60 | 0.00169 | [-0.00095, 0.00429] | 0.00169 | [-0.00095, 0.00429] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4675 | 60 | -0.00719 | [-0.01357, -0.00110] | -0.00719 | [-0.01357, -0.00110] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4675 | 60 | - | - | 0.00014 | [-0.00074, 0.00097] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4598 | 60 | - | - | -0.00021 | [-0.00129, 0.00078] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4675 | 60 | - | - | 0.00902 | [0.00063, 0.01752] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4598 | 60 | - | - | 0.00885 | [0.00033, 0.01763] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4675 | 60 | - | - | 0.00183 | [-0.00086, 0.00461] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4598 | 60 | - | - | 0.00153 | [-0.00125, 0.00440] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 240, 'GAME_WINNER': 120, 'SPREAD': 1539, 'TEAM_TOTAL': 1636, 'TOTAL': 1140}; settlement: {'SETTLED': 4675}; close: {'OK': 4598, 'OK_STALE': 77}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 731 / 0.054 / 0.041 | 701 / 0.054 / 0.054 | 720 / 0.054 / 0.049 |
| 0.10-0.20 | 752 / 0.145 / 0.154 | 728 / 0.145 / 0.165 | 747 / 0.146 / 0.161 |
| 0.20-0.30 | 550 / 0.249 / 0.269 | 547 / 0.250 / 0.276 | 542 / 0.249 / 0.245 |
| 0.30-0.40 | 468 / 0.351 / 0.348 | 470 / 0.349 / 0.351 | 474 / 0.348 / 0.357 |
| 0.40-0.50 | 482 / 0.450 / 0.456 | 446 / 0.448 / 0.444 | 510 / 0.449 / 0.467 |
| 0.50-0.60 | 452 / 0.546 / 0.540 | 414 / 0.551 / 0.488 | 435 / 0.549 / 0.526 |
| 0.60-0.70 | 295 / 0.650 / 0.600 | 374 / 0.648 / 0.548 | 309 / 0.649 / 0.599 |
| 0.70-0.80 | 249 / 0.751 / 0.747 | 260 / 0.749 / 0.712 | 248 / 0.751 / 0.714 |
| 0.80-0.90 | 242 / 0.850 / 0.864 | 253 / 0.850 / 0.826 | 241 / 0.851 / 0.876 |
| 0.90-1.00 | 454 / 0.955 / 0.945 | 482 / 0.956 / 0.932 | 449 / 0.955 / 0.947 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 35 | 9 | 4 | 2 | 20 | 0 | 0.667 [0.300, 0.903] | 0.423 | 0.423 | 0.10 |
| T-24h | DATA_ONLY | total | 35 | 9 | 9 | 3 | 14 | 0 | 0.750 [0.468, 0.911] | 0.423 | 0.346 | 0.29 |
| T-24h | HYBRID_30 (derived) | margin | 35 | 23 | 2 | 1 | 9 | 0 | 0.667 [0.208, 0.939] | 0.417 | 0.417 | 0.08 |
| T-24h | HYBRID_30 (derived) | total | 35 | 24 | 3 | 2 | 6 | 0 | 0.600 [0.231, 0.882] | 0.273 | 0.273 | 0.05 |
| T-6h | DATA_ONLY | margin | 42 | 8 | 7 | 3 | 24 | 0 | 0.700 [0.397, 0.892] | 0.412 | 0.441 | 0.09 |
| T-6h | DATA_ONLY | total | 42 | 13 | 7 | 9 | 13 | 0 | 0.438 [0.231, 0.668] | 0.379 | 0.345 | -0.09 |
| T-6h | HYBRID_30 (derived) | margin | 42 | 30 | 1 | 2 | 9 | 0 | 0.333 [0.061, 0.792] | 0.417 | 0.417 | -0.04 |
| T-6h | HYBRID_30 (derived) | total | 42 | 32 | 3 | 3 | 4 | 0 | 0.500 [0.188, 0.812] | 0.400 | 0.300 | 0.05 |
| T-90m | DATA_ONLY | margin | 49 | 9 | 7 | 2 | 31 | 0 | 0.778 [0.453, 0.937] | 0.425 | 0.425 | 0.05 |
| T-90m | DATA_ONLY | total | 49 | 15 | 5 | 8 | 21 | 0 | 0.385 [0.177, 0.645] | 0.324 | 0.324 | -0.12 |
| T-90m | HYBRID_30 (derived) | margin | 49 | 34 | 1 | 1 | 13 | 0 | 0.500 [0.095, 0.905] | 0.467 | 0.467 | -0.03 |
| T-90m | HYBRID_30 (derived) | total | 49 | 36 | 0 | 5 | 8 | 0 | 0.000 [0.000, 0.434] | 0.231 | 0.231 | -0.31 |
| T-30m | DATA_ONLY | margin | 60 | 11 | 8 | 2 | 39 | 0 | 0.800 [0.490, 0.943] | 0.388 | 0.388 | 0.08 |
| T-30m | DATA_ONLY | total | 60 | 20 | 7 | 6 | 27 | 0 | 0.538 [0.291, 0.768] | 0.300 | 0.300 | 0.00 |
| T-30m | HYBRID_30 (derived) | margin | 60 | 44 | 2 | 1 | 13 | 0 | 0.667 [0.208, 0.939] | 0.438 | 0.438 | 0.00 |
| T-30m | HYBRID_30 (derived) | total | 60 | 45 | 1 | 2 | 12 | 0 | 0.333 [0.061, 0.792] | 0.133 | 0.133 | -0.03 |
| latest_pregame | DATA_ONLY | margin | 61 | 11 | 8 | 2 | 40 | 0 | 0.800 [0.490, 0.943] | 0.380 | 0.380 | 0.08 |
| latest_pregame | DATA_ONLY | total | 61 | 20 | 7 | 6 | 28 | 0 | 0.538 [0.291, 0.768] | 0.293 | 0.293 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | margin | 61 | 45 | 2 | 1 | 13 | 0 | 0.667 [0.208, 0.939] | 0.438 | 0.438 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | total | 61 | 45 | 1 | 2 | 13 | 0 | 0.333 [0.061, 0.792] | 0.125 | 0.125 | -0.03 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 11 | 2 | 2 | 7 | 0 | 0.500 |
| margin | 1-2 | 17 | 3 | 0 | 14 | 0 | 1.000 |
| margin | 2-3 | 14 | 2 | 1 | 11 | 0 | 0.667 |
| margin | 3-5 | 13 | 2 | 1 | 10 | 0 | 0.667 |
| margin | >5 | 6 | 1 | 0 | 5 | 0 | 1.000 |
| total | <=1 | 20 | 2 | 3 | 15 | 0 | 0.400 |
| total | 1-2 | 11 | 1 | 3 | 7 | 0 | 0.250 |
| total | 2-3 | 10 | 5 | 1 | 4 | 0 | 0.833 |
| total | 3-5 | 15 | 1 | 1 | 13 | 0 | 0.500 |
| total | >5 | 5 | 0 | 1 | 4 | 0 | 0.000 |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 30 | 6 | 0.833 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 30 | 6 | 0.500 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

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

