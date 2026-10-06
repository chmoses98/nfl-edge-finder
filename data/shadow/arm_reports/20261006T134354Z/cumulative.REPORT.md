# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 63 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 3829 | 63 | 4 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 37 | 37 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 44 | 44 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 51 | 51 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 62 | 62 | 4 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 63 | 63 | 4 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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
| 2026_04_ATL_NO | 2026-10-06T00:15 | 34 | CURRENT | 0.50 | 47.50 | -21 | 69 | 0.5/47.5 (kalshi_implied) | 0.5/47.0 (OK) |
|  |  |  | DATA_ONLY | 0.79 | 44.32 |  |  |  |  |
|  |  |  | HYBRID_30 | 0.59 | 46.55 |  |  |  |  |

## Game-centre accuracy — latest_pregame (63 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 63 | 4 | 9.89 | 12.50 | 1.56 | 10.55 | 13.48 | -1.96 | 0.230 |
| DATA_ONLY | 63 | 4 | 10.28 | 12.87 | 1.44 | 11.72 | 14.60 | -1.05 | 0.238 |
| HYBRID_30 | 63 | 4 | 9.98 | 12.54 | 1.52 | 10.86 | 13.76 | -1.69 | 0.232 |
| market at snapshot | 63 | 4 | 9.89 | 12.50 | 1.56 | 10.55 | 13.48 | -1.96 | - |
| market at close | 63 | 4 | 9.94 | 12.49 | 1.57 | 10.67 | 13.62 | -1.95 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 63 | margin | 0.390 | 0.371 | [-0.336, 1.117] | 0.413 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 63 | total | 1.167 | 0.335 | [0.511, 1.824] | 0.365 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 63 | margin | 0.091 | 0.112 | [-0.127, 0.310] | 0.460 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 63 | total | 0.310 | 0.105 | [0.105, 0.515] | 0.413 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 63 | margin | -0.299 | 0.261 | [-0.810, 0.212] | 0.587 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 63 | total | -0.858 | 0.233 | [-1.315, -0.400] | 0.635 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 63 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 63 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 63 | margin | 0.390 | 0.371 | [-0.336, 1.117] | 0.413 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 63 | total | 1.167 | 0.335 | [0.511, 1.824] | 0.365 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 63 | margin | 0.091 | 0.112 | [-0.127, 0.310] | 0.460 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 63 | total | 0.310 | 0.105 | [0.105, 0.515] | 0.413 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 63 | margin | -0.048 | 0.046 | [-0.138, 0.043] | 0.127 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 63 | total | -0.119 | 0.062 | [-0.240, 0.002] | 0.206 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 63 | margin | 0.343 | 0.366 | [-0.375, 1.061] | 0.413 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 63 | total | 1.048 | 0.343 | [0.376, 1.720] | 0.365 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 63 | margin | 0.044 | 0.114 | [-0.180, 0.267] | 0.492 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 63 | total | 0.191 | 0.122 | [-0.049, 0.430] | 0.444 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 63 | 10 | 4 | 49 | 0 | 0.714 | 0.413 | 2.45 |
| DATA_ONLY | total | 63 | 10 | 9 | 44 | 0 | 0.526 | 0.365 | 2.33 |
| HYBRID_30 | margin | 63 | 10 | 4 | 49 | 0 | 0.714 | 0.460 | 0.73 |
| HYBRID_30 | total | 63 | 10 | 9 | 44 | 0 | 0.526 | 0.413 | 0.70 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 12 | 11.62 | 11.58 | 0.500 |
| DATA_ONLY | margin | 1-2 | 17 | 7.73 | 7.41 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 14 | 10.75 | 9.71 | 0.667 |
| DATA_ONLY | margin | >5 | 6 | 13.35 | 13.42 | 1.000 |
| DATA_ONLY | total | <=1 | 20 | 12.07 | 12.22 | 0.400 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 10 | 7.83 | 7.45 | 0.833 |
| DATA_ONLY | total | 3-5 | 17 | 12.16 | 9.38 | 0.667 |
| DATA_ONLY | total | >5 | 5 | 18.60 | 12.70 | 0.000 |
| HYBRID_30 | margin | <=1 | 46 | 9.29 | 9.20 | 0.727 |
| HYBRID_30 | margin | 1-2 | 17 | 11.85 | 11.76 | 0.667 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 46 | 10.85 | 10.84 | 0.562 |
| HYBRID_30 | total | 1-2 | 16 | 10.26 | 9.22 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 63}; DATA_ONLY quality states: {'OK': 63}; close centre status: {'OK': 63}.

## Game-centre accuracy — T-24h (37 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 37 | 4 | 9.82 | 12.25 | 2.01 | 10.15 | 12.35 | 0.18 | 0.231 |
| DATA_ONLY | 37 | 4 | 9.94 | 12.43 | 1.83 | 10.93 | 13.32 | 0.85 | 0.223 |
| HYBRID_30 | 37 | 4 | 9.84 | 12.21 | 1.96 | 10.33 | 12.58 | 0.38 | 0.228 |
| market at snapshot | 37 | 4 | 9.82 | 12.25 | 2.01 | 10.15 | 12.35 | 0.18 | - |
| market at close | 37 | 4 | 9.91 | 12.22 | 2.09 | 9.97 | 12.30 | 0.14 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 37 | margin | 0.116 | 0.544 | [-0.950, 1.181] | 0.459 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 37 | total | 0.785 | 0.452 | [-0.100, 1.670] | 0.432 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 37 | margin | 0.019 | 0.164 | [-0.301, 0.340] | 0.486 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 37 | total | 0.178 | 0.144 | [-0.105, 0.461] | 0.432 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 37 | margin | -0.096 | 0.381 | [-0.843, 0.651] | 0.541 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 37 | total | -0.607 | 0.314 | [-1.222, 0.008] | 0.622 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 37 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 37 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 37 | margin | 0.116 | 0.544 | [-0.950, 1.181] | 0.459 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 37 | total | 0.785 | 0.452 | [-0.100, 1.670] | 0.432 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 37 | margin | 0.019 | 0.164 | [-0.301, 0.340] | 0.486 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 37 | total | 0.178 | 0.144 | [-0.105, 0.461] | 0.432 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 37 | margin | -0.081 | 0.083 | [-0.244, 0.082] | 0.243 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 37 | total | 0.176 | 0.121 | [-0.062, 0.413] | 0.135 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 37 | margin | 0.035 | 0.542 | [-1.028, 1.097] | 0.459 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 37 | total | 0.961 | 0.431 | [0.116, 1.806] | 0.324 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 37 | margin | -0.062 | 0.176 | [-0.407, 0.284] | 0.568 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 37 | total | 0.354 | 0.155 | [0.050, 0.658] | 0.297 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 37 | 7 | 8 | 22 | 0 | 0.467 | 0.459 | 2.67 |
| DATA_ONLY | total | 37 | 13 | 5 | 19 | 0 | 0.722 | 0.432 | 2.52 |
| HYBRID_30 | margin | 37 | 7 | 8 | 22 | 0 | 0.467 | 0.486 | 0.80 |
| HYBRID_30 | total | 37 | 13 | 5 | 19 | 0 | 0.722 | 0.432 | 0.76 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 10 | 8.71 | 8.70 | 0.375 |
| DATA_ONLY | margin | 1-2 | 6 | 5.51 | 5.25 | 1.000 |
| DATA_ONLY | margin | 2-3 | 6 | 11.65 | 11.58 | - |
| DATA_ONLY | margin | 3-5 | 10 | 10.31 | 9.35 | 0.500 |
| DATA_ONLY | margin | >5 | 5 | 14.95 | 16.40 | 0.500 |
| DATA_ONLY | total | <=1 | 9 | 9.49 | 9.67 | 0.800 |
| DATA_ONLY | total | 1-2 | 4 | 9.99 | 9.38 | 0.000 |
| DATA_ONLY | total | 2-3 | 10 | 11.85 | 11.50 | 0.833 |
| DATA_ONLY | total | 3-5 | 12 | 11.21 | 10.12 | 0.600 |
| DATA_ONLY | total | >5 | 2 | 13.07 | 7.25 | 1.000 |
| HYBRID_30 | margin | <=1 | 25 | 8.39 | 8.42 | 0.417 |
| HYBRID_30 | margin | 1-2 | 11 | 12.02 | 11.68 | 0.500 |
| HYBRID_30 | margin | 2-3 | 1 | 22.29 | 24.50 | 1.000 |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 26 | 10.63 | 10.65 | 0.769 |
| HYBRID_30 | total | 1-2 | 11 | 9.61 | 8.95 | 0.600 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 37}; DATA_ONLY quality states: {'OK': 37}; close centre status: {'OK': 37}.

## Game-centre accuracy — T-6h (44 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 44 | 4 | 9.22 | 11.96 | 0.49 | 9.44 | 11.16 | -2.31 | 0.243 |
| DATA_ONLY | 44 | 4 | 9.38 | 11.85 | 0.51 | 10.46 | 12.40 | -1.43 | 0.234 |
| HYBRID_30 | 44 | 4 | 9.25 | 11.84 | 0.50 | 9.67 | 11.46 | -2.04 | 0.238 |
| market at snapshot | 44 | 4 | 9.22 | 11.96 | 0.49 | 9.44 | 11.16 | -2.31 | - |
| market at close | 44 | 4 | 9.31 | 11.98 | 0.53 | 9.56 | 11.33 | -2.35 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 44 | margin | 0.160 | 0.472 | [-0.764, 1.084] | 0.432 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 44 | total | 1.012 | 0.403 | [0.223, 1.802] | 0.386 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 44 | margin | 0.035 | 0.142 | [-0.243, 0.313] | 0.455 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 44 | total | 0.230 | 0.125 | [-0.015, 0.475] | 0.432 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 44 | margin | -0.125 | 0.331 | [-0.773, 0.523] | 0.568 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 44 | total | -0.783 | 0.288 | [-1.347, -0.219] | 0.636 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 44 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 44 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 44 | margin | 0.160 | 0.472 | [-0.764, 1.084] | 0.432 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 44 | total | 1.012 | 0.403 | [0.223, 1.802] | 0.386 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 44 | margin | 0.035 | 0.142 | [-0.243, 0.313] | 0.455 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 44 | total | 0.230 | 0.125 | [-0.015, 0.475] | 0.432 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 44 | margin | -0.091 | 0.085 | [-0.257, 0.075] | 0.227 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 44 | total | -0.114 | 0.106 | [-0.322, 0.095] | 0.273 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 44 | margin | 0.069 | 0.465 | [-0.842, 0.980] | 0.455 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 44 | total | 0.899 | 0.431 | [0.053, 1.744] | 0.386 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 44 | margin | -0.056 | 0.152 | [-0.354, 0.242] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 44 | total | 0.116 | 0.170 | [-0.218, 0.450] | 0.477 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 44 | 10 | 5 | 29 | 0 | 0.667 | 0.432 | 2.57 |
| DATA_ONLY | total | 44 | 11 | 11 | 22 | 0 | 0.500 | 0.386 | 2.36 |
| HYBRID_30 | margin | 44 | 10 | 5 | 29 | 0 | 0.667 | 0.455 | 0.77 |
| HYBRID_30 | total | 44 | 11 | 11 | 22 | 0 | 0.500 | 0.432 | 0.71 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 9 | 10.12 | 10.06 | 0.600 |
| DATA_ONLY | margin | 1-2 | 12 | 8.50 | 8.04 | 0.667 |
| DATA_ONLY | margin | 2-3 | 7 | 10.98 | 10.71 | 1.000 |
| DATA_ONLY | margin | 3-5 | 11 | 7.94 | 7.50 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 11.04 | 12.20 | 0.500 |
| DATA_ONLY | total | <=1 | 13 | 8.74 | 8.77 | 0.600 |
| DATA_ONLY | total | 1-2 | 10 | 9.82 | 10.00 | 0.667 |
| DATA_ONLY | total | 2-3 | 6 | 9.11 | 9.08 | 0.000 |
| DATA_ONLY | total | 3-5 | 11 | 12.32 | 10.27 | 0.333 |
| DATA_ONLY | total | >5 | 4 | 14.53 | 8.50 | 0.667 |
| HYBRID_30 | margin | <=1 | 31 | 9.03 | 9.00 | 0.750 |
| HYBRID_30 | margin | 1-2 | 13 | 9.78 | 9.73 | 0.333 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 33 | 9.76 | 9.68 | 0.500 |
| HYBRID_30 | total | 1-2 | 10 | 8.26 | 7.75 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 44}; DATA_ONLY quality states: {'OK': 44}; close centre status: {'OK': 44}.

## Game-centre accuracy — T-90m (51 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 51 | 4 | 9.04 | 11.58 | 0.76 | 10.03 | 12.32 | -0.75 | 0.239 |
| DATA_ONLY | 51 | 4 | 9.21 | 11.71 | 0.65 | 10.97 | 13.33 | -0.04 | 0.234 |
| HYBRID_30 | 51 | 4 | 9.07 | 11.53 | 0.73 | 10.26 | 12.56 | -0.54 | 0.236 |
| market at snapshot | 51 | 4 | 9.04 | 11.58 | 0.76 | 10.03 | 12.32 | -0.75 | - |
| market at close | 51 | 4 | 9.10 | 11.59 | 0.76 | 10.03 | 12.30 | -0.85 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 51 | margin | 0.167 | 0.436 | [-0.688, 1.023] | 0.412 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 51 | total | 0.940 | 0.370 | [0.214, 1.666] | 0.373 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 51 | margin | 0.032 | 0.131 | [-0.226, 0.290] | 0.451 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 51 | total | 0.232 | 0.116 | [0.004, 0.460] | 0.431 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 51 | margin | -0.135 | 0.306 | [-0.735, 0.465] | 0.588 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 51 | total | -0.708 | 0.258 | [-1.215, -0.201] | 0.627 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 51 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 51 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 51 | margin | 0.167 | 0.436 | [-0.688, 1.023] | 0.412 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 51 | total | 0.940 | 0.370 | [0.214, 1.666] | 0.373 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 51 | margin | 0.032 | 0.131 | [-0.226, 0.290] | 0.451 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 51 | total | 0.232 | 0.116 | [0.004, 0.460] | 0.431 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 51 | margin | -0.059 | 0.052 | [-0.160, 0.043] | 0.157 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 51 | total | 0.000 | 0.073 | [-0.143, 0.143] | 0.216 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 51 | margin | 0.108 | 0.432 | [-0.738, 0.955] | 0.431 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 51 | total | 0.940 | 0.391 | [0.174, 1.706] | 0.353 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 51 | margin | -0.027 | 0.133 | [-0.288, 0.235] | 0.510 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 51 | total | 0.232 | 0.147 | [-0.057, 0.520] | 0.412 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 51 | 9 | 5 | 37 | 0 | 0.643 | 0.412 | 2.59 |
| DATA_ONLY | total | 51 | 10 | 11 | 30 | 0 | 0.476 | 0.373 | 2.33 |
| HYBRID_30 | margin | 51 | 9 | 5 | 37 | 0 | 0.643 | 0.451 | 0.78 |
| HYBRID_30 | total | 51 | 10 | 11 | 30 | 0 | 0.476 | 0.431 | 0.70 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 10 | 7.51 | 7.35 | 0.400 |
| DATA_ONLY | margin | 1-2 | 12 | 7.24 | 6.92 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.25 | 10.25 | 0.750 |
| DATA_ONLY | margin | 3-5 | 12 | 9.16 | 8.42 | 0.667 |
| DATA_ONLY | margin | >5 | 5 | 14.93 | 16.10 | - |
| DATA_ONLY | total | <=1 | 15 | 11.05 | 11.23 | 0.571 |
| DATA_ONLY | total | 1-2 | 11 | 6.99 | 7.41 | 0.400 |
| DATA_ONLY | total | 2-3 | 7 | 11.31 | 10.50 | 1.000 |
| DATA_ONLY | total | 3-5 | 15 | 11.66 | 9.57 | 0.250 |
| DATA_ONLY | total | >5 | 3 | 20.87 | 14.83 | 0.000 |
| HYBRID_30 | margin | <=1 | 35 | 8.05 | 8.00 | 0.667 |
| HYBRID_30 | margin | 1-2 | 16 | 11.31 | 11.31 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 37 | 10.04 | 10.04 | 0.625 |
| HYBRID_30 | total | 1-2 | 13 | 10.01 | 9.27 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 51}; DATA_ONLY quality states: {'OK': 51}; close centre status: {'OK': 51}.

## Game-centre accuracy — T-30m (62 games, 4 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 62 | 4 | 9.98 | 12.59 | 1.65 | 10.44 | 13.40 | -1.71 | 0.232 |
| DATA_ONLY | 62 | 4 | 10.34 | 12.95 | 1.56 | 11.53 | 14.43 | -0.70 | 0.240 |
| HYBRID_30 | 62 | 4 | 10.06 | 12.63 | 1.63 | 10.72 | 13.66 | -1.41 | 0.234 |
| market at snapshot | 62 | 4 | 9.98 | 12.59 | 1.65 | 10.44 | 13.40 | -1.71 | - |
| market at close | 62 | 4 | 10.02 | 12.58 | 1.67 | 10.56 | 13.55 | -1.70 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 62 | margin | 0.368 | 0.376 | [-0.369, 1.106] | 0.419 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 62 | total | 1.097 | 0.333 | [0.445, 1.749] | 0.371 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 62 | margin | 0.084 | 0.113 | [-0.138, 0.306] | 0.468 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 62 | total | 0.288 | 0.104 | [0.084, 0.492] | 0.419 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 62 | margin | -0.284 | 0.264 | [-0.802, 0.234] | 0.581 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 62 | total | -0.809 | 0.232 | [-1.264, -0.354] | 0.629 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 62 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 62 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 62 | margin | 0.368 | 0.376 | [-0.369, 1.106] | 0.419 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 62 | total | 1.097 | 0.333 | [0.445, 1.749] | 0.371 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 62 | margin | 0.084 | 0.113 | [-0.138, 0.306] | 0.468 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 62 | total | 0.288 | 0.104 | [0.084, 0.492] | 0.419 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 62 | margin | -0.048 | 0.047 | [-0.141, 0.044] | 0.129 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 62 | total | -0.121 | 0.063 | [-0.244, 0.002] | 0.210 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 62 | margin | 0.320 | 0.371 | [-0.408, 1.048] | 0.419 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 62 | total | 0.976 | 0.341 | [0.308, 1.644] | 0.371 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 62 | margin | 0.036 | 0.116 | [-0.191, 0.263] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 62 | total | 0.167 | 0.122 | [-0.072, 0.406] | 0.452 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 62 | 10 | 4 | 48 | 0 | 0.714 | 0.419 | 2.46 |
| DATA_ONLY | total | 62 | 10 | 9 | 43 | 0 | 0.526 | 0.371 | 2.28 |
| HYBRID_30 | margin | 62 | 10 | 4 | 48 | 0 | 0.714 | 0.468 | 0.74 |
| HYBRID_30 | total | 62 | 10 | 9 | 43 | 0 | 0.526 | 0.419 | 0.68 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 12 | 11.62 | 11.58 | 0.500 |
| DATA_ONLY | margin | 1-2 | 16 | 7.82 | 7.59 | 1.000 |
| DATA_ONLY | margin | 2-3 | 14 | 10.44 | 10.11 | 0.667 |
| DATA_ONLY | margin | 3-5 | 14 | 10.75 | 9.71 | 0.667 |
| DATA_ONLY | margin | >5 | 6 | 13.35 | 13.42 | 1.000 |
| DATA_ONLY | total | <=1 | 20 | 12.07 | 12.22 | 0.400 |
| DATA_ONLY | total | 1-2 | 11 | 10.78 | 11.14 | 0.250 |
| DATA_ONLY | total | 2-3 | 10 | 7.83 | 7.45 | 0.833 |
| DATA_ONLY | total | 3-5 | 17 | 12.16 | 9.38 | 0.667 |
| DATA_ONLY | total | >5 | 4 | 17.50 | 11.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 45 | 9.39 | 9.30 | 0.727 |
| HYBRID_30 | margin | 1-2 | 17 | 11.85 | 11.76 | 0.667 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 46 | 10.85 | 10.84 | 0.562 |
| HYBRID_30 | total | 1-2 | 15 | 9.66 | 8.67 | 0.333 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 62}; DATA_ONLY quality states: {'OK': 62}; close centre status: {'OK': 62}.

## Contract pricing — latest_pregame (4908 contracts, 63 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4908 | 0.1595 | 0.4809 | 0.415 | 0.421 | 4908 | 0.1595 | 0.1594 | 0.1617 |
| DATA_ONLY | 4908 | 0.1692 | 0.5079 | 0.424 | 0.421 | 4908 | 0.1692 | 0.1594 | 0.1617 |
| HYBRID_30 | 4908 | 0.1616 | 0.4867 | 0.415 | 0.421 | 4908 | 0.1616 | 0.1594 | 0.1617 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4908 | 63 | 0.00980 | [0.00160, 0.01799] | 0.00980 | [0.00160, 0.01799] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4908 | 63 | 0.00213 | [-0.00032, 0.00454] | 0.00213 | [-0.00032, 0.00454] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4908 | 63 | -0.00767 | [-0.01387, -0.00140] | -0.00767 | [-0.01387, -0.00140] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4908 | 63 | - | - | 0.00005 | [-0.00071, 0.00078] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4831 | 63 | - | - | -0.00028 | [-0.00120, 0.00067] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4908 | 63 | - | - | 0.00984 | [0.00153, 0.01806] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4831 | 63 | - | - | 0.00970 | [0.00111, 0.01815] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4908 | 63 | - | - | 0.00217 | [-0.00029, 0.00473] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4831 | 63 | - | - | 0.00191 | [-0.00059, 0.00450] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 252, 'GAME_WINNER': 126, 'SPREAD': 1614, 'TEAM_TOTAL': 1719, 'TOTAL': 1197}; settlement: {'SETTLED': 4908}; close: {'OK': 4831, 'OK_STALE': 77}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 756 / 0.055 / 0.044 | 731 / 0.054 / 0.062 | 747 / 0.054 / 0.051 |
| 0.10-0.20 | 789 / 0.145 / 0.162 | 767 / 0.145 / 0.171 | 787 / 0.146 / 0.168 |
| 0.20-0.30 | 578 / 0.248 / 0.275 | 574 / 0.250 / 0.284 | 569 / 0.249 / 0.258 |
| 0.30-0.40 | 491 / 0.351 / 0.358 | 500 / 0.349 / 0.368 | 497 / 0.348 / 0.366 |
| 0.40-0.50 | 502 / 0.450 / 0.466 | 480 / 0.447 / 0.467 | 543 / 0.449 / 0.484 |
| 0.50-0.60 | 478 / 0.547 / 0.554 | 429 / 0.551 / 0.501 | 453 / 0.549 / 0.539 |
| 0.60-0.70 | 314 / 0.650 / 0.618 | 386 / 0.647 / 0.562 | 322 / 0.649 / 0.612 |
| 0.70-0.80 | 258 / 0.752 / 0.756 | 271 / 0.750 / 0.723 | 257 / 0.751 / 0.724 |
| 0.80-0.90 | 258 / 0.850 / 0.872 | 265 / 0.849 / 0.834 | 255 / 0.851 / 0.882 |
| 0.90-1.00 | 484 / 0.955 / 0.948 | 505 / 0.956 / 0.935 | 478 / 0.956 / 0.950 |

## Contract pricing — T-24h (2881 contracts, 37 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2881 | 0.1575 | 0.4760 | 0.415 | 0.402 | 2881 | 0.1575 | 0.1574 | 0.1582 |
| DATA_ONLY | 2881 | 0.1627 | 0.4913 | 0.422 | 0.402 | 2881 | 0.1627 | 0.1574 | 0.1582 |
| HYBRID_30 | 2881 | 0.1578 | 0.4765 | 0.416 | 0.402 | 2881 | 0.1578 | 0.1574 | 0.1582 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2881 | 37 | 0.00525 | [-0.00646, 0.01701] | 0.00525 | [-0.00646, 0.01701] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2881 | 37 | 0.00032 | [-0.00355, 0.00438] | 0.00032 | [-0.00355, 0.00438] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2881 | 37 | -0.00493 | [-0.01366, 0.00350] | -0.00493 | [-0.01366, 0.00350] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2881 | 37 | - | - | 0.00005 | [-0.00081, 0.00099] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2845 | 37 | - | - | 0.00102 | [-0.00042, 0.00256] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2881 | 37 | - | - | 0.00530 | [-0.00613, 0.01681] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2845 | 37 | - | - | 0.00639 | [-0.00503, 0.01798] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2881 | 37 | - | - | 0.00038 | [-0.00368, 0.00456] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2845 | 37 | - | - | 0.00139 | [-0.00241, 0.00529] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 148, 'GAME_WINNER': 74, 'SPREAD': 949, 'TEAM_TOTAL': 1007, 'TOTAL': 703}; settlement: {'SETTLED': 2881}; close: {'OK': 2845, 'OK_STALE': 36}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 451 / 0.055 / 0.024 | 438 / 0.054 / 0.041 | 438 / 0.054 / 0.027 |
| 0.10-0.20 | 451 / 0.145 / 0.135 | 450 / 0.145 / 0.140 | 464 / 0.146 / 0.138 |
| 0.20-0.30 | 350 / 0.249 / 0.283 | 336 / 0.250 / 0.298 | 339 / 0.250 / 0.274 |
| 0.30-0.40 | 275 / 0.349 / 0.345 | 293 / 0.349 / 0.345 | 276 / 0.348 / 0.351 |
| 0.40-0.50 | 309 / 0.451 / 0.427 | 279 / 0.446 / 0.419 | 330 / 0.449 / 0.452 |
| 0.50-0.60 | 265 / 0.546 / 0.532 | 249 / 0.550 / 0.442 | 254 / 0.550 / 0.488 |
| 0.60-0.70 | 184 / 0.646 / 0.582 | 229 / 0.648 / 0.568 | 190 / 0.647 / 0.558 |
| 0.70-0.80 | 165 / 0.751 / 0.752 | 158 / 0.750 / 0.747 | 161 / 0.749 / 0.758 |
| 0.80-0.90 | 146 / 0.852 / 0.836 | 156 / 0.847 / 0.833 | 149 / 0.852 / 0.859 |
| 0.90-1.00 | 285 / 0.956 / 0.933 | 293 / 0.956 / 0.925 | 280 / 0.956 / 0.939 |

## Contract pricing — T-6h (3431 contracts, 44 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3431 | 0.1529 | 0.4624 | 0.416 | 0.421 | 3431 | 0.1529 | 0.1533 | 0.1557 |
| DATA_ONLY | 3431 | 0.1587 | 0.4776 | 0.424 | 0.421 | 3431 | 0.1587 | 0.1533 | 0.1557 |
| HYBRID_30 | 3431 | 0.1536 | 0.4643 | 0.414 | 0.421 | 3431 | 0.1536 | 0.1533 | 0.1557 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3431 | 44 | 0.00580 | [-0.00357, 0.01449] | 0.00580 | [-0.00357, 0.01449] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3431 | 44 | 0.00068 | [-0.00200, 0.00325] | 0.00068 | [-0.00200, 0.00325] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3431 | 44 | -0.00512 | [-0.01201, 0.00213] | -0.00512 | [-0.01201, 0.00213] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3431 | 44 | - | - | -0.00038 | [-0.00136, 0.00060] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3365 | 44 | - | - | -0.00038 | [-0.00171, 0.00081] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3431 | 44 | - | - | 0.00542 | [-0.00435, 0.01437] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3365 | 44 | - | - | 0.00558 | [-0.00417, 0.01479] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3431 | 44 | - | - | 0.00030 | [-0.00267, 0.00306] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3365 | 44 | - | - | 0.00035 | [-0.00268, 0.00327] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 176, 'GAME_WINNER': 88, 'SPREAD': 1127, 'TEAM_TOTAL': 1204, 'TOTAL': 836}; settlement: {'SETTLED': 3431}; close: {'OK': 3365, 'OK_STALE': 66}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 536 / 0.055 / 0.049 | 524 / 0.054 / 0.044 | 538 / 0.054 / 0.045 |
| 0.10-0.20 | 536 / 0.145 / 0.146 | 532 / 0.146 / 0.148 | 537 / 0.146 / 0.151 |
| 0.20-0.30 | 414 / 0.249 / 0.254 | 392 / 0.251 / 0.268 | 414 / 0.251 / 0.251 |
| 0.30-0.40 | 342 / 0.351 / 0.368 | 343 / 0.350 / 0.385 | 332 / 0.349 / 0.386 |
| 0.40-0.50 | 350 / 0.450 / 0.463 | 333 / 0.446 / 0.447 | 388 / 0.449 / 0.459 |
| 0.50-0.60 | 329 / 0.545 / 0.529 | 298 / 0.549 / 0.510 | 306 / 0.549 / 0.539 |
| 0.60-0.70 | 227 / 0.649 / 0.634 | 275 / 0.647 / 0.585 | 217 / 0.648 / 0.622 |
| 0.70-0.80 | 176 / 0.754 / 0.784 | 195 / 0.751 / 0.744 | 182 / 0.750 / 0.780 |
| 0.80-0.90 | 190 / 0.852 / 0.905 | 187 / 0.849 / 0.861 | 183 / 0.851 / 0.896 |
| 0.90-1.00 | 331 / 0.957 / 0.967 | 352 / 0.956 / 0.960 | 334 / 0.956 / 0.970 |

## Contract pricing — T-90m (3973 contracts, 51 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3973 | 0.1537 | 0.4668 | 0.417 | 0.405 | 3973 | 0.1537 | 0.1532 | 0.1555 |
| DATA_ONLY | 3973 | 0.1592 | 0.4816 | 0.423 | 0.405 | 3973 | 0.1592 | 0.1532 | 0.1555 |
| HYBRID_30 | 3973 | 0.1558 | 0.4705 | 0.415 | 0.405 | 3973 | 0.1558 | 0.1532 | 0.1555 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3973 | 51 | 0.00544 | [-0.00479, 0.01524] | 0.00544 | [-0.00479, 0.01524] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3973 | 51 | 0.00206 | [-0.00122, 0.00526] | 0.00206 | [-0.00122, 0.00526] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3973 | 51 | -0.00337 | [-0.01070, 0.00354] | -0.00337 | [-0.01070, 0.00354] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3973 | 51 | - | - | 0.00056 | [-0.00046, 0.00154] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3904 | 51 | - | - | 0.00047 | [-0.00088, 0.00174] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3973 | 51 | - | - | 0.00599 | [-0.00391, 0.01620] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3904 | 51 | - | - | 0.00603 | [-0.00381, 0.01646] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3973 | 51 | - | - | 0.00262 | [-0.00055, 0.00596] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3904 | 51 | - | - | 0.00260 | [-0.00063, 0.00597] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 204, 'GAME_WINNER': 102, 'SPREAD': 1307, 'TEAM_TOTAL': 1391, 'TOTAL': 969}; settlement: {'SETTLED': 3973}; close: {'OK': 3904, 'OK_STALE': 69}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 615 / 0.055 / 0.029 | 603 / 0.054 / 0.040 | 615 / 0.054 / 0.033 |
| 0.10-0.20 | 625 / 0.144 / 0.136 | 612 / 0.145 / 0.139 | 627 / 0.146 / 0.144 |
| 0.20-0.30 | 469 / 0.248 / 0.262 | 464 / 0.250 / 0.265 | 473 / 0.250 / 0.256 |
| 0.30-0.40 | 401 / 0.350 / 0.329 | 403 / 0.350 / 0.340 | 388 / 0.349 / 0.363 |
| 0.40-0.50 | 391 / 0.449 / 0.430 | 387 / 0.446 / 0.429 | 448 / 0.449 / 0.446 |
| 0.50-0.60 | 398 / 0.546 / 0.545 | 346 / 0.550 / 0.497 | 357 / 0.550 / 0.507 |
| 0.60-0.70 | 261 / 0.650 / 0.590 | 313 / 0.647 / 0.569 | 261 / 0.650 / 0.586 |
| 0.70-0.80 | 204 / 0.752 / 0.755 | 227 / 0.749 / 0.727 | 206 / 0.750 / 0.733 |
| 0.80-0.90 | 220 / 0.850 / 0.868 | 214 / 0.849 / 0.850 | 212 / 0.850 / 0.877 |
| 0.90-1.00 | 389 / 0.956 / 0.946 | 404 / 0.956 / 0.936 | 386 / 0.956 / 0.951 |

## Contract pricing — T-30m (4831 contracts, 62 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 4831 | 0.1598 | 0.4819 | 0.414 | 0.417 | 4831 | 0.1598 | 0.1598 | 0.1621 |
| DATA_ONLY | 4831 | 0.1688 | 0.5067 | 0.424 | 0.417 | 4831 | 0.1688 | 0.1598 | 0.1621 |
| HYBRID_30 | 4831 | 0.1615 | 0.4867 | 0.415 | 0.417 | 4831 | 0.1615 | 0.1598 | 0.1621 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 4831 | 62 | 0.00896 | [0.00135, 0.01664] | 0.00896 | [0.00135, 0.01664] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 4831 | 62 | 0.00172 | [-0.00061, 0.00406] | 0.00172 | [-0.00061, 0.00406] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 4831 | 62 | -0.00725 | [-0.01306, -0.00147] | -0.00725 | [-0.01306, -0.00147] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 4831 | 62 | - | - | 0.00006 | [-0.00076, 0.00090] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 4754 | 62 | - | - | -0.00027 | [-0.00123, 0.00072] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 4831 | 62 | - | - | 0.00903 | [0.00124, 0.01693] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 4754 | 62 | - | - | 0.00887 | [0.00096, 0.01677] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 4831 | 62 | - | - | 0.00178 | [-0.00063, 0.00430] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 4754 | 62 | - | - | 0.00150 | [-0.00094, 0.00408] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 248, 'GAME_WINNER': 124, 'SPREAD': 1589, 'TEAM_TOTAL': 1692, 'TOTAL': 1178}; settlement: {'SETTLED': 4831}; close: {'OK': 4754, 'OK_STALE': 77}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 749 / 0.055 / 0.044 | 721 / 0.054 / 0.060 | 739 / 0.054 / 0.051 |
| 0.10-0.20 | 775 / 0.145 / 0.160 | 754 / 0.145 / 0.168 | 772 / 0.146 / 0.165 |
| 0.20-0.30 | 569 / 0.248 / 0.276 | 563 / 0.249 / 0.281 | 562 / 0.249 / 0.256 |
| 0.30-0.40 | 485 / 0.351 / 0.355 | 494 / 0.349 / 0.362 | 491 / 0.348 / 0.365 |
| 0.40-0.50 | 498 / 0.450 / 0.462 | 469 / 0.448 / 0.456 | 533 / 0.449 / 0.475 |
| 0.50-0.60 | 468 / 0.546 / 0.543 | 424 / 0.550 / 0.495 | 447 / 0.549 / 0.532 |
| 0.60-0.70 | 307 / 0.650 / 0.609 | 382 / 0.648 / 0.558 | 316 / 0.649 / 0.604 |
| 0.70-0.80 | 256 / 0.752 / 0.754 | 267 / 0.750 / 0.719 | 255 / 0.752 / 0.722 |
| 0.80-0.90 | 252 / 0.850 / 0.869 | 261 / 0.849 / 0.831 | 249 / 0.851 / 0.880 |
| 0.90-1.00 | 472 / 0.955 / 0.947 | 496 / 0.956 / 0.933 | 467 / 0.955 / 0.949 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 37 | 10 | 4 | 3 | 20 | 0 | 0.571 [0.250, 0.842] | 0.444 | 0.444 | 0.06 |
| T-24h | DATA_ONLY | total | 37 | 9 | 9 | 4 | 15 | 0 | 0.692 [0.424, 0.873] | 0.393 | 0.321 | 0.21 |
| T-24h | HYBRID_30 (derived) | margin | 37 | 25 | 2 | 1 | 9 | 0 | 0.667 [0.208, 0.939] | 0.417 | 0.417 | 0.08 |
| T-24h | HYBRID_30 (derived) | total | 37 | 26 | 3 | 2 | 6 | 0 | 0.600 [0.231, 0.882] | 0.273 | 0.273 | 0.05 |
| T-6h | DATA_ONLY | margin | 44 | 9 | 7 | 3 | 25 | 0 | 0.700 [0.397, 0.892] | 0.429 | 0.457 | 0.09 |
| T-6h | DATA_ONLY | total | 44 | 13 | 8 | 9 | 14 | 0 | 0.471 [0.262, 0.690] | 0.355 | 0.323 | -0.06 |
| T-6h | HYBRID_30 (derived) | margin | 44 | 31 | 1 | 2 | 10 | 0 | 0.333 [0.061, 0.792] | 0.462 | 0.462 | -0.04 |
| T-6h | HYBRID_30 (derived) | total | 44 | 33 | 3 | 3 | 5 | 0 | 0.500 [0.188, 0.812] | 0.364 | 0.273 | 0.05 |
| T-90m | DATA_ONLY | margin | 51 | 10 | 7 | 2 | 32 | 0 | 0.778 [0.453, 0.937] | 0.439 | 0.439 | 0.05 |
| T-90m | DATA_ONLY | total | 51 | 15 | 6 | 8 | 22 | 0 | 0.429 [0.214, 0.674] | 0.306 | 0.306 | -0.10 |
| T-90m | HYBRID_30 (derived) | margin | 51 | 35 | 1 | 1 | 14 | 0 | 0.500 [0.095, 0.905] | 0.500 | 0.500 | -0.03 |
| T-90m | HYBRID_30 (derived) | total | 51 | 37 | 0 | 5 | 9 | 0 | 0.000 [0.000, 0.434] | 0.214 | 0.214 | -0.29 |
| T-30m | DATA_ONLY | margin | 62 | 12 | 8 | 2 | 40 | 0 | 0.800 [0.490, 0.943] | 0.400 | 0.400 | 0.08 |
| T-30m | DATA_ONLY | total | 62 | 20 | 8 | 6 | 28 | 0 | 0.571 [0.326, 0.786] | 0.286 | 0.286 | 0.01 |
| T-30m | HYBRID_30 (derived) | margin | 62 | 45 | 2 | 1 | 14 | 0 | 0.667 [0.208, 0.939] | 0.471 | 0.471 | 0.00 |
| T-30m | HYBRID_30 (derived) | total | 62 | 46 | 1 | 2 | 13 | 0 | 0.333 [0.061, 0.792] | 0.125 | 0.125 | -0.03 |
| latest_pregame | DATA_ONLY | margin | 63 | 12 | 8 | 2 | 41 | 0 | 0.800 [0.490, 0.943] | 0.392 | 0.392 | 0.08 |
| latest_pregame | DATA_ONLY | total | 63 | 20 | 8 | 6 | 29 | 0 | 0.571 [0.326, 0.786] | 0.279 | 0.279 | 0.01 |
| latest_pregame | HYBRID_30 (derived) | margin | 63 | 46 | 2 | 1 | 14 | 0 | 0.667 [0.208, 0.939] | 0.471 | 0.471 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | total | 63 | 46 | 1 | 2 | 14 | 0 | 0.333 [0.061, 0.792] | 0.118 | 0.118 | -0.03 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 12 | 2 | 2 | 8 | 0 | 0.500 |
| margin | 1-2 | 17 | 3 | 0 | 14 | 0 | 1.000 |
| margin | 2-3 | 14 | 2 | 1 | 11 | 0 | 0.667 |
| margin | 3-5 | 14 | 2 | 1 | 11 | 0 | 0.667 |
| margin | >5 | 6 | 1 | 0 | 5 | 0 | 1.000 |
| total | <=1 | 20 | 2 | 3 | 15 | 0 | 0.400 |
| total | 1-2 | 11 | 1 | 3 | 7 | 0 | 0.250 |
| total | 2-3 | 10 | 5 | 1 | 4 | 0 | 0.833 |
| total | 3-5 | 17 | 2 | 1 | 14 | 0 | 0.667 |
| total | >5 | 5 | 0 | 1 | 4 | 0 | 0.000 |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 32 | 6 | 0.833 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 32 | 7 | 0.571 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

4041 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_01_CHI_CAR | Jonathon Brooks | receiving_yards | 1.0 | 0–11 | 48 | 64.75 | 0.99 | 1.0 | 2 | 0.98 | 24.00 | EXPECTED_ACTIVE | True | 0.427 | EFFICIENCY_MISS |
| 2026_04_GB_TB | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 36 | 48.56 | 0.99 | 1.0 | 5 | 1.05 | 7.20 | EXPECTED_ACTIVE | True | 0.223 | EFFICIENCY_MISS |
| 2026_04_IND_WAS | Jacory Croskey-Merritt | receiving_yards | 1.0 | 0–11 | 35 | 47.21 | 0.99 | 1.2 | 4 | 0.86 | 8.75 | EXPECTED_ACTIVE | True | 0.213 | EFFICIENCY_MISS |
| 2026_03_CAR_CLE | Raheim Sanders | receiving_yards | 1.0 | 0–11 | 34 | 45.87 | 0.99 | 1.2 | 5 | 0.87 | 6.80 | EXPECTED_ACTIVE | True | 0.123 | EFFICIENCY_MISS |
| 2026_04_DEN_SF | Kyle Juszczyk | receiving_yards | 1.0 | 0–11 | 28 | 37.77 | 0.99 | 0.5 | 2 | 2.04 | 14.00 | EXPECTED_ACTIVE | True | 0.297 | EFFICIENCY_MISS |
| 2026_03_NYJ_DET | Kenyon Sadiq | receiving_yards | 3.3 | 0–35 | 105 | 35.41 | 0.99 | 1.1 | 8 | 3.05 | 13.12 | EXPECTED_ACTIVE | True | 0.603 | OPPORTUNITY_MISS |
| 2026_04_LAC_SEA | Keaton Mitchell | receiving_yards | 1.0 | 0–11 | 24 | 32.38 | 0.99 | 1.2 | 6 | 0.81 | 4.00 | EXPECTED_ACTIVE | True | 0.342 | EFFICIENCY_MISS |
| 2026_02_IND_KC | Emmett Johnson | receiving_yards | 1.0 | 0–11 | 20 | 26.98 | 0.99 | 0.9 | 2 | 1.08 | 10.00 | EXPECTED_ACTIVE | True | 0.273 | EFFICIENCY_MISS |
| 2026_03_ARI_SF | Jeremiyah Love | receiving_yards | 1.0 | 0–11 | 19 | 25.63 | 0.98 | 0.9 | 5 | 1.07 | 3.80 | EXPECTED_ACTIVE | True | 0.472 | TEAM_VOLUME_MISS |
| 2026_02_SEA_ARI | Jeremiyah Love | receiving_yards | 1.0 | 0–11 | 16 | 21.58 | 0.97 | 1.0 | 3 | 1.05 | 5.33 | EXPECTED_ACTIVE | True | 0.506 | EFFICIENCY_MISS |
| 2026_04_LAC_SEA | Emanuel Wilson | receiving_yards | 2.8 | 0–29 | 39 | 17.54 | 0.97 | 1.2 | 4 | 2.27 | 9.75 | EXPECTED_ACTIVE | True | 0.177 | EFFICIENCY_MISS |
| 2026_04_KC_LV | Emmett Johnson | receiving_yards | 1.0 | 0–11 | 10 | 13.49 | 0.93 | 0.9 | 1 | 1.10 | 10.00 | EXPECTED_ACTIVE | True | -0.243 | EFFICIENCY_MISS |
| 2026_04_JAX_CIN | Bhayshul Tuten | receiving_yards | 1.9 | 0–20 | 18 | 12.14 | 0.93 | 1.2 | 2 | 1.61 | 9.00 | EXPECTED_ACTIVE | True | 0.307 | EFFICIENCY_MISS |
| 2026_02_SEA_ARI | Jadarian Price | receiving_yards | 1.0 | 0–11 | 8 | 10.79 | 0.89 | 0.9 | 2 | 1.08 | 4.00 | EXPECTED_ACTIVE | True | -0.293 | EFFICIENCY_MISS |
| 2026_04_ARI_NYG | Jeremiyah Love | receiving_yards | 1.0 | 0–11 | -8 | -10.79 | 0.05 | 0.9 | 1 | 1.08 | -8.00 | EXPECTED_ACTIVE | True | -0.531 | EFFICIENCY_MISS |
| 2026_04_NYJ_CHI | Braelon Allen | receiving_yards | 1.0 | 0–11 | 8 | 10.79 | 0.89 | 1.2 | 2 | 0.85 | 4.00 | EXPECTED_ACTIVE | True | -0.382 | EFFICIENCY_MISS |
| 2026_01_CLE_JAX | Bhayshul Tuten | receiving_yards | 2.9 | 0–31 | 22 | 9.89 | 0.89 | 1.3 | 1 | 2.33 | 22.00 | EXPECTED_ACTIVE | True | 0.283 | EFFICIENCY_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | receiving_yards | 2.7 | 0–29 | 21 | 9.44 | 0.89 | 1.1 | 3 | 2.49 | 7.00 | EXPECTED_ACTIVE | True | 0.361 | EFFICIENCY_MISS |
| 2026_01_WAS_PHI | Jacory Croskey-Merritt | receiving_yards | 1.0 | 0–11 | -7 | -9.44 | 0.05 | 1.2 | 1 | 0.83 | -7.00 | EXPECTED_ACTIVE | True | -0.183 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.0 | 3 | 1.04 | 2.33 | EXPECTED_ACTIVE | True | -0.193 | TEAM_VOLUME_MISS |
| 2026_03_NYJ_DET | Kenyon Sadiq | receptions | 0.7 | 0–5 | 7 | 9.44 | 0.97 | 1.1 | 8 | 0.68 | 0.88 | EXPECTED_ACTIVE | True | 0.612 | OPPORTUNITY_MISS |
| 2026_03_SEA_WAS | Jadarian Price | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 0.9 | 3 | 1.09 | 2.33 | EXPECTED_ACTIVE | True | -0.307 | TEAM_VOLUME_MISS |
| 2026_04_DAL_HOU | CeeDee Lamb | receptions | 3.1 | 0–7 | 17 | 9.44 | 0.99 | 4.9 | 21 | 0.62 | 0.81 | EXPECTED_ACTIVE | True | 0.352 | TEAM_VOLUME_MISS |
| 2026_04_PIT_CLE | Raheim Sanders | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.1 | 2 | 0.87 | 3.50 | EXPECTED_ACTIVE | True | -0.402 | EFFICIENCY_MISS |
| 2026_02_GB_NYJ | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 6 | 8.09 | 0.85 | 0.9 | 2 | 1.05 | 3.00 | EXPECTED_ACTIVE | True | -0.303 | EFFICIENCY_MISS |
| 2026_02_MIA_SF | Kyle Juszczyk | touchdowns | 0.0 | -–- | 1 | 8.00 | - | 0.0 | 2 | - | - | EXPECTED_ACTIVE | True | 0.068 | UNEXPLAINED_VARIANCE |
| 2026_03_NE_JAX | Bhayshul Tuten | receiving_yards | 2.4 | 0–25 | 17 | 7.64 | 0.88 | 1.2 | 2 | 1.95 | 8.50 | EXPECTED_ACTIVE | True | 0.382 | EFFICIENCY_MISS |
| 2026_04_TEN_BAL | Carnell Tate | receiving_yards | 19.1 | 0–64 | 145 | 7.06 | 0.99 | 1.9 | 12 | 10.12 | 12.08 | EXPECTED_ACTIVE | True | 0.455 | OPPORTUNITY_MISS |
| 2026_04_MIA_MIN | Ollie Gordon II | rushing_yards | 12.5 | 0–50 | 100 | 7.04 | 0.99 | 4.1 | 9 | 3.02 | 11.11 | EXPECTED_ACTIVE | True | 0.394 | EFFICIENCY_MISS |
| 2026_02_CAR_ATL | Jonathon Brooks | receiving_yards | 1.0 | 0–11 | -5 | -6.75 | 0.05 | 1.0 | 1 | 1.00 | -5.00 | EXPECTED_ACTIVE | True | -0.233 | EFFICIENCY_MISS |
| 2026_03_ARI_SF | Jeremiyah Love | receptions | 0.7 | 0–5 | 5 | 6.75 | 0.95 | 0.9 | 5 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.563 | TEAM_VOLUME_MISS |
| 2026_04_GB_TB | MarShawn Lloyd | receptions | 0.7 | 0–5 | 5 | 6.75 | 0.95 | 1.0 | 5 | 0.73 | 1.00 | EXPECTED_ACTIVE | True | 0.199 | OPPORTUNITY_MISS |
| 2026_04_LAC_SEA | Keaton Mitchell | receptions | 0.9 | 0–5 | 5 | 6.75 | 0.95 | 1.2 | 6 | 0.70 | 0.83 | EXPECTED_ACTIVE | True | 0.281 | OPPORTUNITY_MISS |
| 2026_02_GB_NYJ | Chris Brooks | receiving_yards | 3.1 | 0–32 | 15 | 6.74 | 0.83 | 1.3 | 2 | 2.41 | 7.50 | EXPECTED_ACTIVE | True | 0.210 | EFFICIENCY_MISS |
| 2026_04_LA_PHI | Kyren Williams | receiving_yards | 10.3 | 0–45 | 67 | 6.46 | 0.98 | 1.7 | 13 | 6.16 | 5.15 | EXPECTED_ACTIVE | True | 0.236 | TEAM_VOLUME_MISS |
| 2026_03_LA_DEN | Kyren Williams | receiving_yards | 11.1 | 0–48 | 70 | 6.30 | 0.98 | 1.7 | 7 | 6.37 | 10.00 | EXPECTED_ACTIVE | True | 0.169 | TEAM_VOLUME_MISS |
| 2026_04_DEN_SF | RJ Harvey | receptions | 1.4 | 0–5 | 10 | 6.07 | 0.99 | 1.9 | 10 | 0.74 | 1.00 | EXPECTED_ACTIVE | True | 0.444 | TEAM_VOLUME_MISS |
| 2026_04_JAX_CIN | Chase Brown | receptions | 1.9 | 0–5 | 11 | 6.07 | 0.99 | 2.4 | 11 | 0.80 | 1.00 | EXPECTED_ACTIVE | True | 0.279 | TEAM_VOLUME_MISS |
| 2026_04_LA_PHI | Kyren Williams | receptions | 1.2 | 0–5 | 10 | 6.07 | 0.99 | 1.7 | 13 | 0.71 | 0.77 | EXPECTED_ACTIVE | True | 0.315 | TEAM_VOLUME_MISS |
| 2026_03_ARI_SF | Jeremiyah Love | rushing_yards | 13.8 | 0–55 | 90 | 5.96 | 0.99 | 3.9 | 21 | 3.53 | 4.29 | EXPECTED_ACTIVE | True | 0.568 | OPPORTUNITY_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 720, 'OPPORTUNITY_MISS': 1342, 'TEAM_VOLUME_MISS': 274, 'UNEXPLAINED_VARIANCE': 128, 'NO_LARGE_MISS': 1472, 'INSUFFICIENT_DATA': 55, 'AVAILABILITY_MISS': 50}.
Missing usage (no snap table or stats row): 105.

## Decision funnel (BET / WATCH / PASS accounting of the existing gates; no authority)

115 snapshot(s). A contract's terminal state is where it left the existing gate sequence when the model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).

### Newest snapshot 20261005T225057Z (61640 markets)

| stage | markets |
|---|---|
| discovered | 61640 |
| mapped | 53105 |
| supported | 1893 |
| priced | 1893 |
| raw_disagreement | 1345 |
| tradable_book | 1318 |
| data_quality | 1316 |
| executable_price | 793 |
| liquidity | 427 |

Terminal states: {'PASS': 60692, 'WATCH': 521, 'BET': 427}

| family | BET | WATCH | PASS |
|---|---|---|---|
| AWARD | 0 | 0 | 876 |
| BOTH_TEAMS_SCORE | 0 | 0 | 256 |
| BOTH_TEAMS_SCORE_N | 1 | 1 | 254 |
| COACH_EVENT | 0 | 0 | 64 |
| CONFERENCE_WINNER | 0 | 0 | 32 |
| DIVISION_WINNER | 0 | 0 | 32 |
| DRAFT | 0 | 0 | 40 |
| FIRST_TD_SCORER | 0 | 0 | 1686 |
| FIRST_TD_TEAM | 0 | 0 | 1911 |
| GAME_EVENT | 0 | 0 | 260 |
| GAME_PLAYER_LEADER | 0 | 0 | 806 |
| GAME_STAT | 0 | 0 | 5 |
| GAME_WINNER | 0 | 19 | 139 |
| HALF_FULL_RESULT | 0 | 0 | 585 |
| MAKE_PLAYOFFS | 0 | 0 | 33 |
| NFL_BUSINESS_EVENT | 0 | 0 | 5 |
| NOT_NFL_OR_UNKNOWN | 0 | 0 | 2 |
| PERIOD_WINNER | 0 | 0 | 1152 |
| PLAYER_AVAILABILITY | 0 | 0 | 23 |
| PLAYER_ROLE_EVENT | 0 | 0 | 177 |
| PLAYER_STAT | 410 | 85 | 25162 |
| RACE_TO_N | 0 | 0 | 1005 |
| SEASON_DIVISION_ORDER | 0 | 0 | 192 |
| SEASON_DIVISION_STAT | 0 | 0 | 80 |
| SEASON_FANTASY | 0 | 0 | 1182 |
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
| SPREAD | 5 | 179 | 6990 |
| SUPER_BOWL_EVENT | 0 | 0 | 265 |
| SUPER_BOWL_WINNER | 0 | 0 | 32 |
| TEAM_STAT | 0 | 0 | 1566 |
| TEAM_TOTAL | 9 | 113 | 3670 |
| TEAM_WINS_BY_WEEK | 0 | 0 | 728 |
| TOTAL | 2 | 124 | 5726 |
| TOTAL_TD | 0 | 0 | 214 |
| TRANSACTION_EVENT | 0 | 0 | 314 |
| UNKNOWN_NEEDS_CLASSIFICATION | 0 | 0 | 386 |
| WEEK_EVENT | 0 | 0 | 32 |
| WEEK_LEADER | 0 | 0 | 482 |
| WIN_MARGIN_BUCKET | 0 | 0 | 448 |

| rejection reason | n |
|---|---|
| POST_KICKOFF_EXCLUDED | 45688 |
| unmapped | 8535 |
| UNSUPPORTED_RULES | 3403 |
| UNSUPPORTED_MODEL | 2113 |
| no positive disagreement against either executable ask | 548 |
| no order book observed for this ticker (books are captured i | 366 |
| book not tradable for ranking | 27 |
| ask 0.99 above the zero-net-EV ceiling 0.98 | 25 |
| ask 0.98 above the zero-net-EV ceiling 0.97 | 14 |
| ask 0.95 above the zero-net-EV ceiling 0.94 | 11 |
| ask 0.97 above the zero-net-EV ceiling 0.96 | 11 |
| ask 0.42 above the zero-net-EV ceiling 0.40 | 10 |
| ask 0.07 above the zero-net-EV ceiling 0.06 | 9 |
| ask 0.18 above the zero-net-EV ceiling 0.17 | 9 |
| UNSUPPORTED_IDENTITY | 8 |

WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee schedule (`watch_ceiling`). Not replayed: ['portfolio_risk_policy (needs a stake and bankroll)', "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own confirmation is the STALE_DATA support state)"].

Across all 115 snapshots (repeated markets counted per snapshot): {'PASS': 4370696, 'WATCH': 85637, 'BET': 70986}.

