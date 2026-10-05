# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 62 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 3735 | 62 | 4 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 36 | 36 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 43 | 43 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 50 | 50 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 61 | 61 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 62 | 62 | 4 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_DET_CAR | 2026-10-05T00:20 | 30 | CURRENT | -4.50 | 51.50 | 6 | 58 | -4.5/51.5 (kalshi_implied) | -4.5/51.5 (OK) |
|  |  |  | DATA_ONLY | -0.32 | 47.29 |  |  |  |  |
|  |  |  | HYBRID_30 | -3.25 | 50.24 |  |  |  |  |

## Game-centre accuracy — latest_pregame (62 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 62 | 4 | 9.70 | 12.30 | 1.23 | 10.37 | 13.31 | -1.65 | 0.229 |
| DATA_ONLY | 62 | 4 | 10.09 | 12.68 | 1.11 | 11.51 | 14.38 | -0.67 | 0.238 |
| HYBRID_30 | 62 | 4 | 9.79 | 12.34 | 1.20 | 10.67 | 13.57 | -1.35 | 0.231 |
| market at snapshot | 62 | 4 | 9.70 | 12.30 | 1.23 | 10.37 | 13.31 | -1.65 | - |
| market at close | 62 | 4 | 9.75 | 12.29 | 1.25 | 10.48 | 13.44 | -1.63 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 62 | margin | 0.392 | 0.377 | [-0.346, 1.131] | 0.419 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 62 | total | 1.135 | 0.339 | [0.471, 1.799] | 0.371 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 62 | margin | 0.092 | 0.113 | [-0.131, 0.314] | 0.468 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 62 | total | 0.299 | 0.106 | [0.092, 0.507] | 0.419 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 62 | margin | -0.301 | 0.265 | [-0.819, 0.218] | 0.581 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 62 | total | -0.836 | 0.236 | [-1.298, -0.373] | 0.629 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 62 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 62 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 62 | margin | 0.392 | 0.377 | [-0.346, 1.131] | 0.419 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 62 | total | 1.135 | 0.339 | [0.471, 1.799] | 0.371 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 62 | margin | 0.092 | 0.113 | [-0.131, 0.314] | 0.468 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 62 | total | 0.299 | 0.106 | [0.092, 0.507] | 0.419 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 62 | margin | -0.048 | 0.047 | [-0.141, 0.044] | 0.129 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 62 | total | -0.113 | 0.062 | [-0.235, 0.009] | 0.194 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 62 | margin | 0.344 | 0.372 | [-0.386, 1.073] | 0.419 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 62 | total | 1.022 | 0.347 | [0.341, 1.703] | 0.371 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 62 | margin | 0.043 | 0.116 | [-0.184, 0.270] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 62 | total | 0.186 | 0.124 | [-0.057, 0.430] | 0.452 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 62 | 10 | 4 | 48 | 0 | 0.714 | 0.419 | 2.48 |
| DATA_ONLY | total | 62 | 9 | 9 | 44 | 0 | 0.500 | 0.371 | 2.32 |
| HYBRID_30 | margin | 62 | 10 | 4 | 48 | 0 | 0.714 | 0.468 | 0.75 |
| HYBRID_30 | total | 62 | 9 | 9 | 44 | 0 | 0.500 | 0.419 | 0.70 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 11 | 10.70 | 10.68 | 0.500 |
| DATA_ONLY | margin | 1-2 | 17 | 7.73 | 7.41 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 14 | 10.75 | 9.71 | 0.667 |
| DATA_ONLY | margin | >5 | 6 | 13.35 | 13.42 | 1.000 |
| DATA_ONLY | total | <=1 | 20 | 12.07 | 12.22 | 0.400 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 10 | 7.83 | 7.45 | 0.833 |
| DATA_ONLY | total | 3-5 | 16 | 11.38 | 8.62 | 0.500 |
| DATA_ONLY | total | >5 | 5 | 18.60 | 12.70 | 0.000 |
| HYBRID_30 | margin | <=1 | 45 | 9.02 | 8.92 | 0.727 |
| HYBRID_30 | margin | 1-2 | 17 | 11.85 | 11.76 | 0.667 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 45 | 10.59 | 10.60 | 0.533 |
| HYBRID_30 | total | 1-2 | 16 | 10.26 | 9.22 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 62}; DATA_ONLY quality states: {'OK': 62}; close centre status: {'OK': 62}.

## Game-centre accuracy — T-24h (36 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 36 | 4 | 9.47 | 11.84 | 1.44 | 9.82 | 11.97 | 0.79 | 0.229 |
| DATA_ONLY | 36 | 4 | 9.61 | 12.07 | 1.27 | 10.56 | 12.88 | 1.55 | 0.221 |
| HYBRID_30 | 36 | 4 | 9.50 | 11.81 | 1.39 | 9.98 | 12.17 | 1.02 | 0.225 |
| market at snapshot | 36 | 4 | 9.47 | 11.84 | 1.44 | 9.82 | 11.97 | 0.79 | - |
| market at close | 36 | 4 | 9.58 | 11.86 | 1.56 | 9.64 | 11.92 | 0.75 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 36 | margin | 0.138 | 0.559 | [-0.957, 1.232] | 0.444 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 36 | total | 0.740 | 0.462 | [-0.165, 1.646] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 36 | margin | 0.026 | 0.168 | [-0.304, 0.355] | 0.472 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 36 | total | 0.163 | 0.148 | [-0.126, 0.453] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 36 | margin | -0.112 | 0.392 | [-0.879, 0.655] | 0.556 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 36 | total | -0.577 | 0.321 | [-1.206, 0.052] | 0.611 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 36 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 36 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 36 | margin | 0.138 | 0.559 | [-0.957, 1.232] | 0.444 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 36 | total | 0.740 | 0.462 | [-0.165, 1.646] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 36 | margin | 0.026 | 0.168 | [-0.304, 0.355] | 0.472 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 36 | total | 0.163 | 0.148 | [-0.126, 0.453] | 0.444 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 36 | margin | -0.111 | 0.080 | [-0.268, 0.046] | 0.250 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 36 | total | 0.181 | 0.125 | [-0.064, 0.425] | 0.139 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 36 | margin | 0.027 | 0.557 | [-1.066, 1.119] | 0.472 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 36 | total | 0.921 | 0.441 | [0.056, 1.786] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 36 | margin | -0.085 | 0.180 | [-0.438, 0.267] | 0.583 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 36 | total | 0.344 | 0.159 | [0.032, 0.656] | 0.306 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 36 | 6 | 8 | 22 | 0 | 0.429 | 0.444 | 2.73 |
| DATA_ONLY | total | 36 | 13 | 5 | 18 | 0 | 0.722 | 0.444 | 2.52 |
| HYBRID_30 | margin | 36 | 6 | 8 | 22 | 0 | 0.429 | 0.472 | 0.82 |
| HYBRID_30 | total | 36 | 13 | 5 | 18 | 0 | 0.722 | 0.444 | 0.76 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 7.25 | 7.17 | 0.286 |
| DATA_ONLY | margin | 1-2 | 6 | 5.51 | 5.25 | 1.000 |
| DATA_ONLY | margin | 2-3 | 6 | 11.65 | 11.58 | - |
| DATA_ONLY | margin | 3-5 | 10 | 10.31 | 9.35 | 0.500 |
| DATA_ONLY | margin | >5 | 5 | 14.95 | 16.40 | 0.500 |
| DATA_ONLY | total | <=1 | 9 | 9.49 | 9.67 | 0.800 |
| DATA_ONLY | total | 1-2 | 4 | 9.99 | 9.38 | 0.000 |
| DATA_ONLY | total | 2-3 | 9 | 10.46 | 10.33 | 0.833 |
| DATA_ONLY | total | 3-5 | 12 | 11.21 | 10.12 | 0.600 |
| DATA_ONLY | total | >5 | 2 | 13.07 | 7.25 | 1.000 |
| HYBRID_30 | margin | <=1 | 24 | 7.81 | 7.83 | 0.364 |
| HYBRID_30 | margin | 1-2 | 11 | 12.02 | 11.68 | 0.500 |
| HYBRID_30 | margin | 2-3 | 1 | 22.29 | 24.50 | 1.000 |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 25 | 10.15 | 10.20 | 0.769 |
| HYBRID_30 | total | 1-2 | 11 | 9.61 | 8.95 | 0.600 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 36}; DATA_ONLY quality states: {'OK': 36}; close centre status: {'OK': 36}.

## Game-centre accuracy — T-6h (43 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 43 | 4 | 8.93 | 11.65 | 0.00 | 9.16 | 10.80 | -1.86 | 0.242 |
| DATA_ONLY | 43 | 4 | 9.09 | 11.52 | 0.02 | 10.12 | 11.96 | -0.89 | 0.233 |
| HYBRID_30 | 43 | 4 | 8.96 | 11.52 | 0.00 | 9.38 | 11.08 | -1.57 | 0.237 |
| market at snapshot | 43 | 4 | 8.93 | 11.65 | 0.00 | 9.16 | 10.80 | -1.86 | - |
| market at close | 43 | 4 | 9.02 | 11.66 | 0.05 | 9.27 | 10.95 | -1.90 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 43 | margin | 0.157 | 0.483 | [-0.789, 1.103] | 0.442 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 43 | total | 0.962 | 0.409 | [0.160, 1.763] | 0.395 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 43 | margin | 0.034 | 0.145 | [-0.251, 0.319] | 0.465 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 43 | total | 0.213 | 0.127 | [-0.035, 0.461] | 0.442 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 43 | margin | -0.123 | 0.338 | [-0.786, 0.540] | 0.558 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 43 | total | -0.749 | 0.293 | [-1.322, -0.176] | 0.628 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 43 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 43 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 43 | margin | 0.157 | 0.483 | [-0.789, 1.103] | 0.442 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 43 | total | 0.962 | 0.409 | [0.160, 1.763] | 0.395 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 43 | margin | 0.034 | 0.145 | [-0.251, 0.319] | 0.465 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 43 | total | 0.213 | 0.127 | [-0.035, 0.461] | 0.442 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 43 | margin | -0.093 | 0.087 | [-0.263, 0.077] | 0.233 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 43 | total | -0.105 | 0.109 | [-0.317, 0.108] | 0.256 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 43 | margin | 0.064 | 0.475 | [-0.868, 0.996] | 0.465 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 43 | total | 0.857 | 0.439 | [-0.004, 1.718] | 0.395 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 43 | margin | -0.059 | 0.156 | [-0.364, 0.246] | 0.512 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 43 | total | 0.108 | 0.174 | [-0.233, 0.450] | 0.488 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 43 | 10 | 5 | 28 | 0 | 0.667 | 0.442 | 2.62 |
| DATA_ONLY | total | 43 | 10 | 11 | 22 | 0 | 0.476 | 0.395 | 2.34 |
| HYBRID_30 | margin | 43 | 10 | 5 | 28 | 0 | 0.667 | 0.465 | 0.79 |
| HYBRID_30 | total | 43 | 10 | 11 | 22 | 0 | 0.476 | 0.442 | 0.70 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 8 | 8.66 | 8.62 | 0.600 |
| DATA_ONLY | margin | 1-2 | 12 | 8.50 | 8.04 | 0.667 |
| DATA_ONLY | margin | 2-3 | 7 | 10.98 | 10.71 | 1.000 |
| DATA_ONLY | margin | 3-5 | 11 | 7.94 | 7.50 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 11.04 | 12.20 | 0.500 |
| DATA_ONLY | total | <=1 | 13 | 8.74 | 8.77 | 0.600 |
| DATA_ONLY | total | 1-2 | 10 | 9.82 | 10.00 | 0.667 |
| DATA_ONLY | total | 2-3 | 6 | 9.11 | 9.08 | 0.000 |
| DATA_ONLY | total | 3-5 | 10 | 11.08 | 9.15 | 0.200 |
| DATA_ONLY | total | >5 | 4 | 14.53 | 8.50 | 0.667 |
| HYBRID_30 | margin | <=1 | 30 | 8.61 | 8.58 | 0.750 |
| HYBRID_30 | margin | 1-2 | 13 | 9.78 | 9.73 | 0.333 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 32 | 9.36 | 9.31 | 0.467 |
| HYBRID_30 | total | 1-2 | 10 | 8.26 | 7.75 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 43}; DATA_ONLY quality states: {'OK': 43}; close centre status: {'OK': 43}.

## Game-centre accuracy — T-90m (50 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 50 | 4 | 8.79 | 11.29 | 0.35 | 9.80 | 12.07 | -0.34 | 0.239 |
| DATA_ONLY | 50 | 4 | 8.95 | 11.41 | 0.22 | 10.69 | 13.00 | 0.46 | 0.233 |
| HYBRID_30 | 50 | 4 | 8.82 | 11.24 | 0.31 | 10.02 | 12.29 | -0.10 | 0.235 |
| market at snapshot | 50 | 4 | 8.79 | 11.29 | 0.35 | 9.80 | 12.07 | -0.34 | - |
| market at close | 50 | 4 | 8.85 | 11.30 | 0.35 | 9.79 | 12.03 | -0.43 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 50 | margin | 0.165 | 0.445 | [-0.708, 1.037] | 0.420 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 50 | total | 0.895 | 0.375 | [0.160, 1.630] | 0.380 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 50 | margin | 0.031 | 0.134 | [-0.232, 0.294] | 0.460 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 50 | total | 0.217 | 0.118 | [-0.013, 0.448] | 0.440 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 50 | margin | -0.134 | 0.312 | [-0.745, 0.478] | 0.580 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 50 | total | -0.677 | 0.262 | [-1.191, -0.164] | 0.620 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 50 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 50 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 50 | margin | 0.165 | 0.445 | [-0.708, 1.037] | 0.420 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 50 | total | 0.895 | 0.375 | [0.160, 1.630] | 0.380 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 50 | margin | 0.031 | 0.134 | [-0.232, 0.294] | 0.460 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 50 | total | 0.217 | 0.118 | [-0.013, 0.448] | 0.440 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 50 | margin | -0.060 | 0.053 | [-0.163, 0.043] | 0.160 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 50 | total | 0.010 | 0.074 | [-0.134, 0.154] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 50 | margin | 0.105 | 0.441 | [-0.759, 0.968] | 0.440 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 50 | total | 0.905 | 0.397 | [0.126, 1.684] | 0.360 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 50 | margin | -0.029 | 0.136 | [-0.296, 0.238] | 0.520 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 50 | total | 0.227 | 0.150 | [-0.067, 0.522] | 0.420 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 50 | 9 | 5 | 36 | 0 | 0.643 | 0.420 | 2.63 |
| DATA_ONLY | total | 50 | 9 | 11 | 30 | 0 | 0.450 | 0.380 | 2.31 |
| HYBRID_30 | margin | 50 | 9 | 5 | 36 | 0 | 0.643 | 0.460 | 0.79 |
| HYBRID_30 | total | 50 | 9 | 11 | 30 | 0 | 0.450 | 0.440 | 0.69 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 5.92 | 5.78 | 0.400 |
| DATA_ONLY | margin | 1-2 | 12 | 7.24 | 6.92 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.25 | 10.25 | 0.750 |
| DATA_ONLY | margin | 3-5 | 12 | 9.16 | 8.42 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.93 | 16.10 | - |
| DATA_ONLY | total | <=1 | 15 | 11.05 | 11.23 | 0.571 |
| DATA_ONLY | total | 1-2 | 11 | 6.99 | 7.41 | 0.400 |
| DATA_ONLY | total | 2-3 | 7 | 11.31 | 10.50 | 1.000 |
| DATA_ONLY | total | 3-5 | 14 | 10.73 | 8.71 | 0.000 |
| DATA_ONLY | total | >5 | 3 | 20.87 | 14.83 | 0.000 |
| HYBRID_30 | margin | <=1 | 34 | 7.65 | 7.60 | 0.667 |
| HYBRID_30 | margin | 1-2 | 16 | 11.31 | 11.31 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 36 | 9.70 | 9.72 | 0.600 |
| HYBRID_30 | total | 1-2 | 13 | 10.01 | 9.27 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 50}; DATA_ONLY quality states: {'OK': 50}; close centre status: {'OK': 50}.

## Game-centre accuracy — T-30m (61 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 61 | 4 | 9.79 | 12.39 | 1.33 | 10.25 | 13.23 | -1.39 | 0.231 |
| DATA_ONLY | 61 | 4 | 10.16 | 12.76 | 1.23 | 11.32 | 14.20 | -0.30 | 0.239 |
| HYBRID_30 | 61 | 4 | 9.87 | 12.43 | 1.30 | 10.53 | 13.46 | -1.06 | 0.233 |
| market at snapshot | 61 | 4 | 9.79 | 12.39 | 1.33 | 10.25 | 13.23 | -1.39 | - |
| market at close | 61 | 4 | 9.84 | 12.38 | 1.34 | 10.37 | 13.37 | -1.37 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 61 | margin | 0.370 | 0.382 | [-0.380, 1.119] | 0.426 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 61 | total | 1.063 | 0.336 | [0.404, 1.722] | 0.377 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 61 | margin | 0.084 | 0.115 | [-0.141, 0.310] | 0.475 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 61 | total | 0.277 | 0.105 | [0.071, 0.483] | 0.426 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 61 | margin | -0.285 | 0.269 | [-0.812, 0.241] | 0.574 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 61 | total | -0.786 | 0.235 | [-1.246, -0.326] | 0.623 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 61 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 61 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 61 | margin | 0.370 | 0.382 | [-0.380, 1.119] | 0.426 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 61 | total | 1.063 | 0.336 | [0.404, 1.722] | 0.377 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 61 | margin | 0.084 | 0.115 | [-0.141, 0.310] | 0.475 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 61 | total | 0.277 | 0.105 | [0.071, 0.483] | 0.426 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 61 | margin | -0.049 | 0.048 | [-0.143, 0.044] | 0.131 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 61 | total | -0.115 | 0.063 | [-0.239, 0.009] | 0.197 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 61 | margin | 0.321 | 0.378 | [-0.420, 1.061] | 0.426 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 61 | total | 0.948 | 0.345 | [0.272, 1.624] | 0.377 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 61 | margin | 0.035 | 0.118 | [-0.195, 0.266] | 0.508 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 61 | total | 0.162 | 0.124 | [-0.080, 0.405] | 0.459 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 61 | 10 | 4 | 47 | 0 | 0.714 | 0.426 | 2.50 |
| DATA_ONLY | total | 61 | 9 | 9 | 43 | 0 | 0.500 | 0.377 | 2.27 |
| HYBRID_30 | margin | 61 | 10 | 4 | 47 | 0 | 0.714 | 0.475 | 0.75 |
| HYBRID_30 | total | 61 | 9 | 9 | 43 | 0 | 0.500 | 0.426 | 0.68 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 11 | 10.70 | 10.68 | 0.500 |
| DATA_ONLY | margin | 1-2 | 16 | 7.82 | 7.59 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 14 | 10.75 | 9.71 | 0.667 |
| DATA_ONLY | margin | >5 | 6 | 13.35 | 13.42 | 1.000 |
| DATA_ONLY | total | <=1 | 20 | 12.07 | 12.22 | 0.400 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 10 | 7.83 | 7.45 | 0.833 |
| DATA_ONLY | total | 3-5 | 16 | 11.38 | 8.62 | 0.500 |
| DATA_ONLY | total | >5 | 4 | 17.50 | 11.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 44 | 9.11 | 9.02 | 0.727 |
| HYBRID_30 | margin | 1-2 | 17 | 11.85 | 11.76 | 0.667 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 45 | 10.59 | 10.60 | 0.533 |
| HYBRID_30 | total | 1-2 | 15 | 9.66 | 8.67 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 61}; DATA_ONLY quality states: {'OK': 61}; close centre status: {'OK': 61}.

## Contract pricing — latest_pregame (4830 contracts, 62 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4830 | 0.1581 | 0.4772 | 0.415 | 0.417 | 4830 | 0.1581 | 0.1579 | 0.1603 |
| DATA_ONLY | 4830 | 0.1674 | 0.5026 | 0.424 | 0.417 | 4830 | 0.1674 | 0.1579 | 0.1603 |
| HYBRID_30 | 4830 | 0.1601 | 0.4826 | 0.415 | 0.417 | 4830 | 0.1601 | 0.1579 | 0.1603 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4830 | 62 | 0.00937 | [0.00149, 0.01779] | 0.00937 | [0.00149, 0.01779] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4830 | 62 | 0.00203 | [-0.00044, 0.00458] | 0.00203 | [-0.00044, 0.00458] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4830 | 62 | -0.00734 | [-0.01374, -0.00132] | -0.00734 | [-0.01374, -0.00132] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4830 | 62 | - | - | 0.00012 | [-0.00069, 0.00087] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4753 | 62 | - | - | -0.00022 | [-0.00122, 0.00071] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4830 | 62 | - | - | 0.00949 | [0.00155, 0.01796] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4753 | 62 | - | - | 0.00933 | [0.00111, 0.01789] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4830 | 62 | - | - | 0.00215 | [-0.00036, 0.00486] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4753 | 62 | - | - | 0.00186 | [-0.00076, 0.00469] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 248, 'GAME_WINNER': 124, 'SPREAD': 1589, 'TEAM_TOTAL': 1691, 'TOTAL': 1178}; settlement: {'SETTLED': 4830}; close: {'OK': 4753, 'OK_STALE': 77}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 746 / 0.055 / 0.040 | 721 / 0.054 / 0.055 | 737 / 0.054 / 0.047 |
| 0.10-0.20 | 777 / 0.145 / 0.156 | 753 / 0.145 / 0.165 | 775 / 0.146 / 0.161 |
| 0.20-0.30 | 569 / 0.248 / 0.271 | 566 / 0.250 / 0.279 | 559 / 0.249 / 0.252 |
| 0.30-0.40 | 482 / 0.351 / 0.355 | 488 / 0.349 / 0.361 | 487 / 0.348 / 0.361 |
| 0.40-0.50 | 491 / 0.450 / 0.460 | 468 / 0.448 / 0.464 | 531 / 0.449 / 0.480 |
| 0.50-0.60 | 472 / 0.547 / 0.553 | 424 / 0.551 / 0.498 | 448 / 0.549 / 0.536 |
| 0.60-0.70 | 309 / 0.650 / 0.612 | 382 / 0.647 / 0.558 | 319 / 0.649 / 0.608 |
| 0.70-0.80 | 254 / 0.752 / 0.752 | 268 / 0.750 / 0.720 | 253 / 0.751 / 0.719 |
| 0.80-0.90 | 254 / 0.850 / 0.870 | 261 / 0.849 / 0.831 | 251 / 0.851 / 0.880 |
| 0.90-1.00 | 476 / 0.955 / 0.947 | 499 / 0.956 / 0.934 | 470 / 0.956 / 0.949 |

## Contract pricing — T-24h (2803 contracts, 36 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2803 | 0.1548 | 0.4686 | 0.415 | 0.394 | 2803 | 0.1548 | 0.1548 | 0.1557 |
| DATA_ONLY | 2803 | 0.1595 | 0.4820 | 0.423 | 0.394 | 2803 | 0.1595 | 0.1548 | 0.1557 |
| HYBRID_30 | 2803 | 0.1549 | 0.4684 | 0.416 | 0.394 | 2803 | 0.1549 | 0.1548 | 0.1557 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2803 | 36 | 0.00468 | [-0.00665, 0.01715] | 0.00468 | [-0.00665, 0.01715] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2803 | 36 | 0.00006 | [-0.00363, 0.00452] | 0.00006 | [-0.00363, 0.00452] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2803 | 36 | -0.00463 | [-0.01362, 0.00362] | -0.00463 | [-0.01362, 0.00362] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2803 | 36 | - | - | 0.00003 | [-0.00086, 0.00100] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2767 | 36 | - | - | 0.00088 | [-0.00067, 0.00244] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2803 | 36 | - | - | 0.00471 | [-0.00638, 0.01689] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2767 | 36 | - | - | 0.00568 | [-0.00546, 0.01783] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2803 | 36 | - | - | 0.00009 | [-0.00367, 0.00442] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2767 | 36 | - | - | 0.00099 | [-0.00281, 0.00508] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 144, 'GAME_WINNER': 72, 'SPREAD': 924, 'TEAM_TOTAL': 979, 'TOTAL': 684}; settlement: {'SETTLED': 2803}; close: {'OK': 2767, 'OK_STALE': 36}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 441 / 0.055 / 0.018 | 427 / 0.054 / 0.030 | 427 / 0.053 / 0.016 |
| 0.10-0.20 | 440 / 0.145 / 0.123 | 438 / 0.146 / 0.130 | 453 / 0.146 / 0.128 |
| 0.20-0.30 | 338 / 0.249 / 0.272 | 327 / 0.250 / 0.287 | 329 / 0.250 / 0.264 |
| 0.30-0.40 | 268 / 0.349 / 0.340 | 281 / 0.350 / 0.331 | 267 / 0.348 / 0.345 |
| 0.40-0.50 | 295 / 0.451 / 0.417 | 267 / 0.447 / 0.412 | 318 / 0.449 / 0.443 |
| 0.50-0.60 | 261 / 0.546 / 0.529 | 244 / 0.549 / 0.434 | 249 / 0.550 / 0.486 |
| 0.60-0.70 | 180 / 0.646 / 0.572 | 225 / 0.648 / 0.560 | 186 / 0.647 / 0.548 |
| 0.70-0.80 | 161 / 0.751 / 0.745 | 155 / 0.750 / 0.742 | 156 / 0.749 / 0.750 |
| 0.80-0.90 | 142 / 0.852 / 0.831 | 152 / 0.848 / 0.829 | 146 / 0.852 / 0.856 |
| 0.90-1.00 | 277 / 0.956 / 0.931 | 287 / 0.956 / 0.923 | 272 / 0.956 / 0.938 |

## Contract pricing — T-6h (3353 contracts, 43 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3353 | 0.1507 | 0.4565 | 0.415 | 0.415 | 3353 | 0.1507 | 0.1510 | 0.1535 |
| DATA_ONLY | 3353 | 0.1558 | 0.4694 | 0.425 | 0.415 | 3353 | 0.1558 | 0.1510 | 0.1535 |
| HYBRID_30 | 3353 | 0.1512 | 0.4579 | 0.414 | 0.415 | 3353 | 0.1512 | 0.1510 | 0.1535 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3353 | 43 | 0.00513 | [-0.00451, 0.01490] | 0.00513 | [-0.00451, 0.01490] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3353 | 43 | 0.00050 | [-0.00250, 0.00314] | 0.00050 | [-0.00250, 0.00314] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3353 | 43 | -0.00462 | [-0.01228, 0.00287] | -0.00462 | [-0.01228, 0.00287] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3353 | 43 | - | - | -0.00029 | [-0.00127, 0.00064] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3287 | 43 | - | - | -0.00034 | [-0.00175, 0.00094] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3353 | 43 | - | - | 0.00483 | [-0.00504, 0.01479] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3287 | 43 | - | - | 0.00494 | [-0.00524, 0.01520] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3353 | 43 | - | - | 0.00021 | [-0.00319, 0.00316] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3287 | 43 | - | - | 0.00021 | [-0.00328, 0.00330] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 172, 'GAME_WINNER': 86, 'SPREAD': 1102, 'TEAM_TOTAL': 1176, 'TOTAL': 817}; settlement: {'SETTLED': 3353}; close: {'OK': 3287, 'OK_STALE': 66}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 526 / 0.055 / 0.044 | 514 / 0.054 / 0.035 | 528 / 0.054 / 0.040 |
| 0.10-0.20 | 524 / 0.145 / 0.135 | 518 / 0.146 / 0.139 | 525 / 0.146 / 0.141 |
| 0.20-0.30 | 404 / 0.249 / 0.245 | 384 / 0.251 / 0.260 | 404 / 0.251 / 0.243 |
| 0.30-0.40 | 334 / 0.351 / 0.365 | 331 / 0.350 / 0.375 | 322 / 0.349 / 0.379 |
| 0.40-0.50 | 338 / 0.450 / 0.456 | 321 / 0.446 / 0.442 | 376 / 0.449 / 0.452 |
| 0.50-0.60 | 324 / 0.545 / 0.525 | 293 / 0.549 / 0.505 | 301 / 0.549 / 0.535 |
| 0.60-0.70 | 222 / 0.649 / 0.626 | 271 / 0.647 / 0.579 | 214 / 0.648 / 0.617 |
| 0.70-0.80 | 172 / 0.753 / 0.779 | 192 / 0.751 / 0.740 | 178 / 0.750 / 0.775 |
| 0.80-0.90 | 186 / 0.852 / 0.903 | 183 / 0.849 / 0.858 | 179 / 0.851 / 0.894 |
| 0.90-1.00 | 323 / 0.957 / 0.966 | 346 / 0.957 / 0.960 | 326 / 0.956 / 0.969 |

## Contract pricing — T-90m (3895 contracts, 50 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3895 | 0.1519 | 0.4619 | 0.416 | 0.400 | 3895 | 0.1519 | 0.1512 | 0.1536 |
| DATA_ONLY | 3895 | 0.1567 | 0.4746 | 0.424 | 0.400 | 3895 | 0.1567 | 0.1512 | 0.1536 |
| HYBRID_30 | 3895 | 0.1538 | 0.4652 | 0.415 | 0.400 | 3895 | 0.1538 | 0.1512 | 0.1536 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3895 | 50 | 0.00484 | [-0.00502, 0.01450] | 0.00484 | [-0.00502, 0.01450] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3895 | 50 | 0.00194 | [-0.00133, 0.00531] | 0.00194 | [-0.00133, 0.00531] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3895 | 50 | -0.00289 | [-0.01016, 0.00420] | -0.00289 | [-0.01016, 0.00420] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3895 | 50 | - | - | 0.00066 | [-0.00046, 0.00168] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3826 | 50 | - | - | 0.00053 | [-0.00082, 0.00184] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3895 | 50 | - | - | 0.00549 | [-0.00447, 0.01562] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3826 | 50 | - | - | 0.00549 | [-0.00461, 0.01562] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3895 | 50 | - | - | 0.00260 | [-0.00069, 0.00582] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3826 | 50 | - | - | 0.00254 | [-0.00082, 0.00593] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 200, 'GAME_WINNER': 100, 'SPREAD': 1282, 'TEAM_TOTAL': 1363, 'TOTAL': 950}; settlement: {'SETTLED': 3895}; close: {'OK': 3826, 'OK_STALE': 69}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 605 / 0.055 / 0.025 | 593 / 0.054 / 0.032 | 605 / 0.054 / 0.028 |
| 0.10-0.20 | 613 / 0.144 / 0.127 | 599 / 0.146 / 0.132 | 615 / 0.146 / 0.135 |
| 0.20-0.30 | 460 / 0.248 / 0.257 | 455 / 0.250 / 0.257 | 463 / 0.250 / 0.248 |
| 0.30-0.40 | 392 / 0.350 / 0.324 | 391 / 0.350 / 0.330 | 378 / 0.349 / 0.357 |
| 0.40-0.50 | 380 / 0.450 / 0.421 | 375 / 0.447 / 0.424 | 436 / 0.449 / 0.440 |
| 0.50-0.60 | 392 / 0.546 / 0.543 | 341 / 0.549 / 0.493 | 352 / 0.550 / 0.503 |
| 0.60-0.70 | 256 / 0.650 / 0.582 | 309 / 0.647 / 0.563 | 258 / 0.650 / 0.581 |
| 0.70-0.80 | 200 / 0.752 / 0.750 | 224 / 0.749 / 0.723 | 202 / 0.750 / 0.728 |
| 0.80-0.90 | 216 / 0.850 / 0.866 | 210 / 0.849 / 0.848 | 208 / 0.850 / 0.875 |
| 0.90-1.00 | 381 / 0.956 / 0.945 | 398 / 0.956 / 0.935 | 378 / 0.956 / 0.950 |

## Contract pricing — T-30m (4753 contracts, 61 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4753 | 0.1584 | 0.4781 | 0.414 | 0.413 | 4753 | 0.1584 | 0.1583 | 0.1607 |
| DATA_ONLY | 4753 | 0.1669 | 0.5014 | 0.425 | 0.413 | 4753 | 0.1669 | 0.1583 | 0.1607 |
| HYBRID_30 | 4753 | 0.1600 | 0.4827 | 0.415 | 0.413 | 4753 | 0.1600 | 0.1583 | 0.1607 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4753 | 61 | 0.00851 | [0.00034, 0.01634] | 0.00851 | [0.00034, 0.01634] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4753 | 61 | 0.00161 | [-0.00068, 0.00393] | 0.00161 | [-0.00068, 0.00393] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4753 | 61 | -0.00691 | [-0.01318, -0.00055] | -0.00691 | [-0.01318, -0.00055] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4753 | 61 | - | - | 0.00014 | [-0.00068, 0.00096] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4676 | 61 | - | - | -0.00021 | [-0.00123, 0.00076] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4753 | 61 | - | - | 0.00866 | [0.00041, 0.01688] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4676 | 61 | - | - | 0.00847 | [0.00022, 0.01678] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4753 | 61 | - | - | 0.00175 | [-0.00055, 0.00423] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4676 | 61 | - | - | 0.00145 | [-0.00105, 0.00399] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 244, 'GAME_WINNER': 122, 'SPREAD': 1564, 'TEAM_TOTAL': 1664, 'TOTAL': 1159}; settlement: {'SETTLED': 4753}; close: {'OK': 4676, 'OK_STALE': 77}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 739 / 0.055 / 0.041 | 711 / 0.054 / 0.053 | 729 / 0.054 / 0.048 |
| 0.10-0.20 | 763 / 0.145 / 0.153 | 740 / 0.145 / 0.162 | 760 / 0.146 / 0.158 |
| 0.20-0.30 | 560 / 0.248 / 0.271 | 555 / 0.249 / 0.276 | 552 / 0.249 / 0.250 |
| 0.30-0.40 | 476 / 0.351 / 0.351 | 482 / 0.349 / 0.355 | 481 / 0.348 / 0.360 |
| 0.40-0.50 | 487 / 0.450 / 0.456 | 457 / 0.448 / 0.453 | 521 / 0.449 / 0.470 |
| 0.50-0.60 | 462 / 0.546 / 0.541 | 419 / 0.550 / 0.492 | 442 / 0.549 / 0.529 |
| 0.60-0.70 | 302 / 0.650 / 0.603 | 378 / 0.648 / 0.553 | 313 / 0.649 / 0.601 |
| 0.70-0.80 | 252 / 0.751 / 0.750 | 264 / 0.750 / 0.716 | 251 / 0.752 / 0.717 |
| 0.80-0.90 | 248 / 0.850 / 0.867 | 257 / 0.850 / 0.829 | 245 / 0.851 / 0.878 |
| 0.90-1.00 | 464 / 0.955 / 0.946 | 490 / 0.956 / 0.933 | 459 / 0.955 / 0.948 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 36 | 9 | 4 | 3 | 20 | 0 | 0.571 [0.250, 0.842] | 0.444 | 0.444 | 0.06 |
| T-24h | DATA_ONLY | total | 36 | 9 | 9 | 4 | 14 | 0 | 0.692 [0.424, 0.873] | 0.407 | 0.333 | 0.22 |
| T-24h | HYBRID_30 (derived) | margin | 36 | 24 | 2 | 1 | 9 | 0 | 0.667 [0.208, 0.939] | 0.417 | 0.417 | 0.08 |
| T-24h | HYBRID_30 (derived) | total | 36 | 25 | 3 | 2 | 6 | 0 | 0.600 [0.231, 0.882] | 0.273 | 0.273 | 0.05 |
| T-6h | DATA_ONLY | margin | 43 | 8 | 7 | 3 | 25 | 0 | 0.700 [0.397, 0.892] | 0.429 | 0.457 | 0.09 |
| T-6h | DATA_ONLY | total | 43 | 13 | 7 | 9 | 14 | 0 | 0.438 [0.231, 0.668] | 0.367 | 0.333 | -0.08 |
| T-6h | HYBRID_30 (derived) | margin | 43 | 30 | 1 | 2 | 10 | 0 | 0.333 [0.061, 0.792] | 0.462 | 0.462 | -0.04 |
| T-6h | HYBRID_30 (derived) | total | 43 | 32 | 3 | 3 | 5 | 0 | 0.500 [0.188, 0.812] | 0.364 | 0.273 | 0.05 |
| T-90m | DATA_ONLY | margin | 50 | 9 | 7 | 2 | 32 | 0 | 0.778 [0.453, 0.937] | 0.439 | 0.439 | 0.05 |
| T-90m | DATA_ONLY | total | 50 | 15 | 5 | 8 | 22 | 0 | 0.385 [0.177, 0.645] | 0.314 | 0.314 | -0.11 |
| T-90m | HYBRID_30 (derived) | margin | 50 | 34 | 1 | 1 | 14 | 0 | 0.500 [0.095, 0.905] | 0.500 | 0.500 | -0.03 |
| T-90m | HYBRID_30 (derived) | total | 50 | 36 | 0 | 5 | 9 | 0 | 0.000 [0.000, 0.434] | 0.214 | 0.214 | -0.29 |
| T-30m | DATA_ONLY | margin | 61 | 11 | 8 | 2 | 40 | 0 | 0.800 [0.490, 0.943] | 0.400 | 0.400 | 0.08 |
| T-30m | DATA_ONLY | total | 61 | 20 | 7 | 6 | 28 | 0 | 0.538 [0.291, 0.768] | 0.293 | 0.293 | 0.00 |
| T-30m | HYBRID_30 (derived) | margin | 61 | 44 | 2 | 1 | 14 | 0 | 0.667 [0.208, 0.939] | 0.471 | 0.471 | 0.00 |
| T-30m | HYBRID_30 (derived) | total | 61 | 45 | 1 | 2 | 13 | 0 | 0.333 [0.061, 0.792] | 0.125 | 0.125 | -0.03 |
| latest_pregame | DATA_ONLY | margin | 62 | 11 | 8 | 2 | 41 | 0 | 0.800 [0.490, 0.943] | 0.392 | 0.392 | 0.08 |
| latest_pregame | DATA_ONLY | total | 62 | 20 | 7 | 6 | 29 | 0 | 0.538 [0.291, 0.768] | 0.286 | 0.286 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | margin | 62 | 45 | 2 | 1 | 14 | 0 | 0.667 [0.208, 0.939] | 0.471 | 0.471 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | total | 62 | 45 | 1 | 2 | 14 | 0 | 0.333 [0.061, 0.792] | 0.118 | 0.118 | -0.03 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 11 | 2 | 2 | 7 | 0 | 0.500 |
| margin | 1-2 | 17 | 3 | 0 | 14 | 0 | 1.000 |
| margin | 2-3 | 14 | 2 | 1 | 11 | 0 | 0.667 |
| margin | 3-5 | 14 | 2 | 1 | 11 | 0 | 0.667 |
| margin | >5 | 6 | 1 | 0 | 5 | 0 | 1.000 |
| total | <=1 | 20 | 2 | 3 | 15 | 0 | 0.400 |
| total | 1-2 | 11 | 1 | 3 | 7 | 0 | 0.250 |
| total | 2-3 | 10 | 5 | 1 | 4 | 0 | 0.833 |
| total | 3-5 | 16 | 1 | 1 | 14 | 0 | 0.500 |
| total | >5 | 5 | 0 | 1 | 4 | 0 | 0.000 |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 31 | 6 | 0.833 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 31 | 6 | 0.500 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

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

