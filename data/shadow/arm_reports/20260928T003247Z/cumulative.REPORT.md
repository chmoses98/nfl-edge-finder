# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 45 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 2341 | 45 | 3 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 20 | 20 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 26 | 26 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 33 | 33 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 44 | 44 | 3 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 45 | 45 | 3 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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

## Game-centre accuracy — latest_pregame (45 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 45 | 3 | 10.62 | 13.29 | 2.24 | 10.90 | 14.36 | -1.66 | 0.228 |
| DATA_ONLY | 45 | 3 | 11.45 | 14.09 | 1.60 | 11.86 | 15.35 | -0.81 | 0.254 |
| HYBRID_30 | 45 | 3 | 10.85 | 13.47 | 2.05 | 11.15 | 14.61 | -1.40 | 0.234 |
| market at snapshot | 45 | 3 | 10.62 | 13.29 | 2.24 | 10.90 | 14.36 | -1.66 | - |
| market at close | 45 | 3 | 10.67 | 13.28 | 2.24 | 10.99 | 14.47 | -1.57 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 45 | margin | 0.832 | 0.391 | [0.065, 1.599] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 45 | total | 0.961 | 0.376 | [0.224, 1.698] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 45 | margin | 0.226 | 0.118 | [-0.005, 0.458] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 45 | total | 0.253 | 0.117 | [0.025, 0.482] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 45 | margin | -0.606 | 0.275 | [-1.145, -0.067] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 45 | total | -0.707 | 0.262 | [-1.222, -0.193] | 0.600 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 45 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 45 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 45 | margin | 0.832 | 0.391 | [0.065, 1.599] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 45 | total | 0.961 | 0.376 | [0.224, 1.698] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 45 | margin | 0.226 | 0.118 | [-0.005, 0.458] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 45 | total | 0.253 | 0.117 | [0.025, 0.482] | 0.444 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 45 | margin | -0.044 | 0.050 | [-0.142, 0.053] | 0.111 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 45 | total | -0.089 | 0.064 | [-0.215, 0.037] | 0.200 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 45 | margin | 0.788 | 0.392 | [0.019, 1.557] | 0.378 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 45 | total | 0.872 | 0.381 | [0.125, 1.618] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 45 | margin | 0.182 | 0.127 | [-0.067, 0.430] | 0.444 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 45 | total | 0.165 | 0.131 | [-0.092, 0.421] | 0.467 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 45 | 6 | 3 | 36 | 0 | 0.667 | 0.400 | 2.31 |
| DATA_ONLY | total | 45 | 8 | 5 | 32 | 0 | 0.615 | 0.400 | 2.06 |
| HYBRID_30 | margin | 45 | 6 | 3 | 36 | 0 | 0.667 | 0.444 | 0.69 |
| HYBRID_30 | total | 45 | 8 | 5 | 32 | 0 | 0.615 | 0.444 | 0.62 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 8 | 13.08 | 13.25 | 0.500 |
| DATA_ONLY | margin | 1-2 | 13 | 8.72 | 8.19 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.04 | 9.62 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 16 | 13.14 | 13.31 | 0.667 |
| DATA_ONLY | total | 1-2 | 10 | 10.88 | 11.10 | 0.333 |
| DATA_ONLY | total | 2-3 | 7 | 5.32 | 5.14 | 0.800 |
| DATA_ONLY | total | 3-5 | 9 | 12.86 | 9.72 | 0.500 |
| DATA_ONLY | total | >5 | 3 | 20.56 | 14.33 | - |
| HYBRID_30 | margin | <=1 | 35 | 9.94 | 9.83 | 0.750 |
| HYBRID_30 | margin | 1-2 | 10 | 14.02 | 13.40 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 36 | 10.95 | 10.94 | 0.636 |
| HYBRID_30 | total | 1-2 | 8 | 10.83 | 9.75 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 45}; DATA_ONLY quality states: {'OK': 45}; close centre status: {'OK': 45}.

## Game-centre accuracy — T-24h (20 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 20 | 3 | 11.18 | 13.45 | 3.58 | 10.53 | 13.35 | 2.42 | 0.228 |
| DATA_ONLY | 20 | 3 | 12.07 | 14.56 | 2.15 | 10.56 | 13.90 | 2.54 | 0.250 |
| HYBRID_30 | 20 | 3 | 11.44 | 13.72 | 3.15 | 10.48 | 13.47 | 2.46 | 0.233 |
| market at snapshot | 20 | 3 | 11.18 | 13.45 | 3.58 | 10.53 | 13.35 | 2.42 | - |
| market at close | 20 | 3 | 11.30 | 13.53 | 3.70 | 10.25 | 13.26 | 2.20 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 20 | margin | 0.898 | 0.661 | [-0.398, 2.193] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 20 | total | 0.035 | 0.541 | [-1.025, 1.094] | 0.550 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 20 | margin | 0.269 | 0.198 | [-0.120, 0.658] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 20 | total | -0.046 | 0.172 | [-0.383, 0.291] | 0.550 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 20 | margin | -0.628 | 0.463 | [-1.535, 0.279] | 0.600 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 20 | total | -0.081 | 0.377 | [-0.820, 0.659] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 20 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 20 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 20 | margin | 0.898 | 0.661 | [-0.398, 2.193] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 20 | total | 0.035 | 0.541 | [-1.025, 1.094] | 0.550 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 20 | margin | 0.269 | 0.198 | [-0.120, 0.658] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 20 | total | -0.046 | 0.172 | [-0.383, 0.291] | 0.550 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 20 | margin | -0.125 | 0.080 | [-0.282, 0.032] | 0.200 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 20 | total | 0.275 | 0.168 | [-0.054, 0.604] | 0.050 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 20 | margin | 0.773 | 0.691 | [-0.582, 2.127] | 0.400 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 20 | total | 0.310 | 0.472 | [-0.616, 1.235] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 20 | margin | 0.144 | 0.236 | [-0.319, 0.608] | 0.450 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 20 | total | 0.229 | 0.158 | [-0.080, 0.538] | 0.300 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 20 | 1 | 5 | 14 | 0 | 0.167 | 0.400 | 2.46 |
| DATA_ONLY | total | 20 | 8 | 1 | 11 | 0 | 0.889 | 0.550 | 2.21 |
| HYBRID_30 | margin | 20 | 1 | 5 | 14 | 0 | 0.167 | 0.400 | 0.74 |
| HYBRID_30 | total | 20 | 8 | 1 | 11 | 0 | 0.889 | 0.550 | 0.66 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 5 | 9.40 | 9.60 | 0.000 |
| DATA_ONLY | margin | 1-2 | 4 | 6.52 | 5.88 | 1.000 |
| DATA_ONLY | margin | 2-3 | 4 | 11.07 | 10.88 | - |
| DATA_ONLY | margin | 3-5 | 5 | 14.03 | 13.20 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.25 | 0.000 |
| DATA_ONLY | total | <=1 | 4 | 10.62 | 11.12 | 1.000 |
| DATA_ONLY | total | 1-2 | 4 | 9.99 | 9.38 | 0.000 |
| DATA_ONLY | total | 2-3 | 7 | 9.24 | 9.86 | 1.000 |
| DATA_ONLY | total | 3-5 | 5 | 12.81 | 11.90 | 1.000 |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 14 | 9.09 | 9.11 | 0.200 |
| HYBRID_30 | margin | 1-2 | 6 | 16.93 | 16.00 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 17 | 10.20 | 10.32 | 0.889 |
| HYBRID_30 | total | 1-2 | 3 | 12.08 | 11.67 | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 20}; DATA_ONLY quality states: {'OK': 20}; close centre status: {'OK': 20}.

## Game-centre accuracy — T-6h (26 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 26 | 3 | 10.06 | 13.03 | 1.02 | 9.27 | 11.30 | -1.96 | 0.247 |
| DATA_ONLY | 26 | 3 | 10.76 | 13.39 | 0.17 | 9.82 | 12.28 | -1.26 | 0.255 |
| HYBRID_30 | 26 | 3 | 10.27 | 13.07 | 0.76 | 9.35 | 11.54 | -1.75 | 0.247 |
| market at snapshot | 26 | 3 | 10.06 | 13.03 | 1.02 | 9.27 | 11.30 | -1.96 | - |
| market at close | 26 | 3 | 10.13 | 13.04 | 0.98 | 9.35 | 11.40 | -1.96 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 26 | margin | 0.703 | 0.572 | [-0.418, 1.825] | 0.385 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 26 | total | 0.555 | 0.482 | [-0.389, 1.499] | 0.423 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 26 | margin | 0.211 | 0.172 | [-0.125, 0.547] | 0.385 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 26 | total | 0.079 | 0.142 | [-0.199, 0.358] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 26 | margin | -0.492 | 0.400 | [-1.277, 0.293] | 0.615 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 26 | total | -0.476 | 0.357 | [-1.175, 0.223] | 0.577 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 26 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 26 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 26 | margin | 0.703 | 0.572 | [-0.418, 1.825] | 0.385 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 26 | total | 0.555 | 0.482 | [-0.389, 1.499] | 0.423 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 26 | margin | 0.211 | 0.172 | [-0.125, 0.547] | 0.385 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 26 | total | 0.079 | 0.142 | [-0.199, 0.358] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 26 | margin | -0.077 | 0.099 | [-0.271, 0.117] | 0.192 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 26 | total | -0.077 | 0.149 | [-0.368, 0.214] | 0.231 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 26 | margin | 0.626 | 0.552 | [-0.456, 1.709] | 0.423 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 26 | total | 0.478 | 0.519 | [-0.539, 1.496] | 0.462 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 26 | margin | 0.134 | 0.172 | [-0.203, 0.472] | 0.385 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 26 | total | 0.002 | 0.210 | [-0.409, 0.414] | 0.538 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 26 | 6 | 3 | 17 | 0 | 0.667 | 0.385 | 2.49 |
| DATA_ONLY | total | 26 | 7 | 4 | 15 | 0 | 0.636 | 0.423 | 1.96 |
| HYBRID_30 | margin | 26 | 6 | 3 | 17 | 0 | 0.667 | 0.385 | 0.75 |
| HYBRID_30 | total | 26 | 7 | 4 | 15 | 0 | 0.636 | 0.500 | 0.59 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 4 | 12.78 | 13.00 | 0.000 |
| DATA_ONLY | margin | 1-2 | 9 | 9.84 | 9.22 | 0.667 |
| DATA_ONLY | margin | 2-3 | 5 | 10.24 | 9.80 | 1.000 |
| DATA_ONLY | margin | 3-5 | 6 | 9.07 | 9.08 | 0.500 |
| DATA_ONLY | margin | >5 | 2 | 17.23 | 11.50 | 1.000 |
| DATA_ONLY | total | <=1 | 9 | 9.15 | 9.22 | 0.750 |
| DATA_ONLY | total | 1-2 | 8 | 9.57 | 9.75 | 0.750 |
| DATA_ONLY | total | 2-3 | 4 | 6.32 | 6.25 | 0.000 |
| DATA_ONLY | total | 3-5 | 3 | 13.15 | 11.83 | - |
| DATA_ONLY | total | >5 | 2 | 15.88 | 9.75 | 1.000 |
| HYBRID_30 | margin | <=1 | 19 | 10.08 | 10.03 | 0.714 |
| HYBRID_30 | margin | 1-2 | 7 | 10.77 | 10.14 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 22 | 9.28 | 9.30 | 0.600 |
| HYBRID_30 | total | 1-2 | 3 | 5.97 | 6.00 | 1.000 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 26}; DATA_ONLY quality states: {'OK': 26}; close centre status: {'OK': 26}.

## Game-centre accuracy — T-90m (33 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 33 | 3 | 9.59 | 12.24 | 1.29 | 10.18 | 12.96 | 0.30 | 0.241 |
| DATA_ONLY | 33 | 3 | 10.22 | 12.88 | 0.43 | 10.76 | 13.73 | 0.85 | 0.253 |
| HYBRID_30 | 33 | 3 | 9.77 | 12.37 | 1.03 | 10.31 | 13.15 | 0.47 | 0.241 |
| market at snapshot | 33 | 3 | 9.59 | 12.24 | 1.29 | 10.18 | 12.96 | 0.30 | - |
| market at close | 33 | 3 | 9.64 | 12.26 | 1.24 | 10.12 | 12.86 | 0.27 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 33 | margin | 0.633 | 0.503 | [-0.354, 1.619] | 0.394 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 33 | total | 0.579 | 0.437 | [-0.277, 1.435] | 0.424 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 33 | margin | 0.179 | 0.152 | [-0.118, 0.476] | 0.424 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 33 | total | 0.126 | 0.136 | [-0.140, 0.392] | 0.485 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 33 | margin | -0.453 | 0.352 | [-1.144, 0.237] | 0.606 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 33 | total | -0.453 | 0.306 | [-1.052, 0.146] | 0.576 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 33 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 33 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 33 | margin | 0.633 | 0.503 | [-0.354, 1.619] | 0.394 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 33 | total | 0.579 | 0.437 | [-0.277, 1.435] | 0.424 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 33 | margin | 0.179 | 0.152 | [-0.118, 0.476] | 0.424 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 33 | total | 0.126 | 0.136 | [-0.140, 0.392] | 0.485 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 33 | margin | -0.045 | 0.055 | [-0.153, 0.062] | 0.121 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 33 | total | 0.061 | 0.086 | [-0.109, 0.230] | 0.182 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 33 | margin | 0.587 | 0.502 | [-0.397, 1.572] | 0.394 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 33 | total | 0.640 | 0.451 | [-0.243, 1.523] | 0.394 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 33 | margin | 0.134 | 0.156 | [-0.173, 0.440] | 0.424 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 33 | total | 0.187 | 0.164 | [-0.134, 0.508] | 0.424 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 33 | 5 | 3 | 25 | 0 | 0.625 | 0.394 | 2.48 |
| DATA_ONLY | total | 33 | 8 | 5 | 20 | 0 | 0.615 | 0.424 | 2.05 |
| HYBRID_30 | margin | 33 | 5 | 3 | 25 | 0 | 0.625 | 0.424 | 0.74 |
| HYBRID_30 | total | 33 | 8 | 5 | 20 | 0 | 0.615 | 0.485 | 0.62 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 5 | 7.13 | 7.10 | 0.000 |
| DATA_ONLY | margin | 1-2 | 9 | 8.15 | 7.72 | 1.000 |
| DATA_ONLY | margin | 2-3 | 10 | 9.74 | 9.70 | 0.750 |
| DATA_ONLY | margin | 3-5 | 7 | 11.00 | 10.36 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 11 | 12.23 | 12.45 | 0.800 |
| DATA_ONLY | total | 1-2 | 8 | 5.60 | 5.88 | 0.500 |
| DATA_ONLY | total | 2-3 | 6 | 10.10 | 9.58 | 1.000 |
| DATA_ONLY | total | 3-5 | 6 | 10.94 | 9.58 | 0.000 |
| DATA_ONLY | total | >5 | 2 | 24.81 | 18.50 | 0.000 |
| HYBRID_30 | margin | <=1 | 24 | 8.46 | 8.42 | 0.714 |
| HYBRID_30 | margin | 1-2 | 9 | 13.27 | 12.72 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 27 | 9.87 | 9.87 | 0.800 |
| HYBRID_30 | total | 1-2 | 5 | 10.40 | 10.00 | 0.000 |
| HYBRID_30 | total | 2-3 | 1 | 21.62 | 19.50 | 0.000 |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 33}; DATA_ONLY quality states: {'OK': 33}; close centre status: {'OK': 33}.

## Game-centre accuracy — T-30m (44 games, 3 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 44 | 3 | 10.76 | 13.42 | 2.40 | 10.75 | 14.28 | -1.30 | 0.230 |
| DATA_ONLY | 44 | 3 | 11.57 | 14.21 | 1.78 | 11.61 | 15.13 | -0.30 | 0.256 |
| HYBRID_30 | 44 | 3 | 10.98 | 13.60 | 2.21 | 10.97 | 14.49 | -1.00 | 0.237 |
| market at snapshot | 44 | 3 | 10.76 | 13.42 | 2.40 | 10.75 | 14.28 | -1.30 | - |
| market at close | 44 | 3 | 10.81 | 13.41 | 2.40 | 10.84 | 14.40 | -1.20 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 44 | margin | 0.811 | 0.400 | [0.028, 1.594] | 0.409 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 44 | total | 0.857 | 0.370 | [0.132, 1.581] | 0.409 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 44 | margin | 0.219 | 0.121 | [-0.017, 0.456] | 0.455 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 44 | total | 0.221 | 0.115 | [-0.003, 0.446] | 0.455 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 44 | margin | -0.592 | 0.281 | [-1.142, -0.041] | 0.591 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 44 | total | -0.635 | 0.258 | [-1.141, -0.129] | 0.591 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 44 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 44 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 44 | margin | 0.811 | 0.400 | [0.028, 1.594] | 0.409 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 44 | total | 0.857 | 0.370 | [0.132, 1.581] | 0.409 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 44 | margin | 0.219 | 0.121 | [-0.017, 0.456] | 0.455 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 44 | total | 0.221 | 0.115 | [-0.003, 0.446] | 0.455 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 44 | margin | -0.045 | 0.051 | [-0.145, 0.054] | 0.114 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 44 | total | -0.091 | 0.066 | [-0.219, 0.038] | 0.205 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 44 | margin | 0.766 | 0.401 | [-0.020, 1.551] | 0.386 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 44 | total | 0.766 | 0.374 | [0.032, 1.499] | 0.409 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 44 | margin | 0.174 | 0.129 | [-0.080, 0.428] | 0.455 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 44 | total | 0.131 | 0.129 | [-0.122, 0.384] | 0.477 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 44 | 6 | 3 | 35 | 0 | 0.667 | 0.409 | 2.32 |
| DATA_ONLY | total | 44 | 8 | 5 | 31 | 0 | 0.615 | 0.409 | 1.98 |
| HYBRID_30 | margin | 44 | 6 | 3 | 35 | 0 | 0.667 | 0.455 | 0.70 |
| HYBRID_30 | total | 44 | 8 | 5 | 31 | 0 | 0.615 | 0.455 | 0.59 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 8 | 13.08 | 13.25 | 0.500 |
| DATA_ONLY | margin | 1-2 | 12 | 8.93 | 8.50 | 1.000 |
| DATA_ONLY | margin | 2-3 | 12 | 10.04 | 9.62 | 0.667 |
| DATA_ONLY | margin | 3-5 | 10 | 12.30 | 10.80 | 0.000 |
| DATA_ONLY | margin | >5 | 2 | 26.97 | 21.00 | - |
| DATA_ONLY | total | <=1 | 16 | 13.14 | 13.31 | 0.667 |
| DATA_ONLY | total | 1-2 | 10 | 10.88 | 11.10 | 0.333 |
| DATA_ONLY | total | 2-3 | 7 | 5.32 | 5.14 | 0.800 |
| DATA_ONLY | total | 3-5 | 9 | 12.86 | 9.72 | 0.500 |
| DATA_ONLY | total | >5 | 2 | 19.32 | 12.75 | - |
| HYBRID_30 | margin | <=1 | 34 | 10.09 | 9.99 | 0.750 |
| HYBRID_30 | margin | 1-2 | 10 | 14.02 | 13.40 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 36 | 10.95 | 10.94 | 0.636 |
| HYBRID_30 | total | 1-2 | 7 | 9.64 | 8.64 | 0.500 |
| HYBRID_30 | total | 2-3 | 1 | 20.92 | 18.50 | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 44}; DATA_ONLY quality states: {'OK': 44}; close centre status: {'OK': 44}.

## Contract pricing — latest_pregame (3509 contracts, 45 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3509 | 0.1661 | 0.4987 | 0.415 | 0.421 | 3509 | 0.1661 | 0.1662 | 0.1688 |
| DATA_ONLY | 3509 | 0.1799 | 0.5366 | 0.421 | 0.421 | 3509 | 0.1799 | 0.1662 | 0.1688 |
| HYBRID_30 | 3509 | 0.1697 | 0.5082 | 0.414 | 0.421 | 3509 | 0.1697 | 0.1662 | 0.1688 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3509 | 45 | 0.01382 | [0.00450, 0.02319] | 0.01382 | [0.00450, 0.02319] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3509 | 45 | 0.00356 | [0.00061, 0.00645] | 0.00356 | [0.00061, 0.00645] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3509 | 45 | -0.01026 | [-0.01758, -0.00301] | -0.01026 | [-0.01758, -0.00301] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3509 | 45 | - | - | -0.00010 | [-0.00116, 0.00085] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3444 | 45 | - | - | -0.00038 | [-0.00161, 0.00088] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3509 | 45 | - | - | 0.01371 | [0.00416, 0.02343] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3444 | 45 | - | - | 0.01373 | [0.00402, 0.02354] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3509 | 45 | - | - | 0.00346 | [0.00065, 0.00642] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3444 | 45 | - | - | 0.00328 | [0.00027, 0.00645] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 180, 'GAME_WINNER': 90, 'SPREAD': 1158, 'TEAM_TOTAL': 1226, 'TOTAL': 855}; settlement: {'SETTLED': 3509}; close: {'OK': 3444, 'OK_STALE': 65}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 547 / 0.055 / 0.049 | 525 / 0.054 / 0.074 | 538 / 0.053 / 0.061 |
| 0.10-0.20 | 565 / 0.145 / 0.191 | 553 / 0.145 / 0.206 | 568 / 0.146 / 0.192 |
| 0.20-0.30 | 410 / 0.248 / 0.278 | 420 / 0.249 / 0.300 | 402 / 0.248 / 0.274 |
| 0.30-0.40 | 347 / 0.351 / 0.354 | 357 / 0.349 / 0.373 | 359 / 0.347 / 0.359 |
| 0.40-0.50 | 360 / 0.450 / 0.464 | 340 / 0.449 / 0.459 | 390 / 0.449 / 0.492 |
| 0.50-0.60 | 335 / 0.547 / 0.552 | 305 / 0.550 / 0.502 | 313 / 0.549 / 0.537 |
| 0.60-0.70 | 234 / 0.651 / 0.611 | 279 / 0.648 / 0.545 | 234 / 0.648 / 0.577 |
| 0.70-0.80 | 180 / 0.750 / 0.733 | 187 / 0.750 / 0.690 | 188 / 0.751 / 0.702 |
| 0.80-0.90 | 186 / 0.848 / 0.849 | 186 / 0.851 / 0.812 | 183 / 0.853 / 0.869 |
| 0.90-1.00 | 345 / 0.954 / 0.933 | 357 / 0.957 / 0.913 | 334 / 0.956 / 0.934 |

## Contract pricing — T-24h (1560 contracts, 20 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1560 | 0.1691 | 0.5070 | 0.415 | 0.389 | 1560 | 0.1691 | 0.1688 | 0.1705 |
| DATA_ONLY | 1560 | 0.1796 | 0.5372 | 0.415 | 0.389 | 1560 | 0.1796 | 0.1688 | 0.1705 |
| HYBRID_30 | 1560 | 0.1698 | 0.5088 | 0.414 | 0.389 | 1560 | 0.1698 | 0.1688 | 0.1705 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1560 | 20 | 0.01043 | [-0.00595, 0.02643] | 0.01043 | [-0.00595, 0.02643] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1560 | 20 | 0.00066 | [-0.00457, 0.00635] | 0.00066 | [-0.00457, 0.00635] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1560 | 20 | -0.00978 | [-0.02121, 0.00207] | -0.00978 | [-0.02121, 0.00207] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1560 | 20 | - | - | 0.00030 | [-0.00111, 0.00168] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1536 | 20 | - | - | 0.00077 | [-0.00149, 0.00313] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1560 | 20 | - | - | 0.01073 | [-0.00555, 0.02670] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1536 | 20 | - | - | 0.01148 | [-0.00432, 0.02732] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1560 | 20 | - | - | 0.00096 | [-0.00445, 0.00657] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1536 | 20 | - | - | 0.00153 | [-0.00357, 0.00688] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 80, 'GAME_WINNER': 40, 'SPREAD': 518, 'TEAM_TOTAL': 542, 'TOTAL': 380}; settlement: {'SETTLED': 1560}; close: {'OK': 1536, 'OK_STALE': 24}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 248 / 0.055 / 0.020 | 244 / 0.053 / 0.049 | 240 / 0.053 / 0.017 |
| 0.10-0.20 | 244 / 0.146 / 0.164 | 247 / 0.146 / 0.186 | 252 / 0.145 / 0.179 |
| 0.20-0.30 | 184 / 0.248 / 0.299 | 187 / 0.250 / 0.342 | 186 / 0.249 / 0.285 |
| 0.30-0.40 | 149 / 0.349 / 0.322 | 159 / 0.348 / 0.333 | 145 / 0.348 / 0.338 |
| 0.40-0.50 | 163 / 0.449 / 0.423 | 146 / 0.447 / 0.377 | 180 / 0.449 / 0.450 |
| 0.50-0.60 | 144 / 0.545 / 0.500 | 135 / 0.550 / 0.415 | 134 / 0.549 / 0.455 |
| 0.60-0.70 | 105 / 0.646 / 0.552 | 129 / 0.648 / 0.527 | 104 / 0.645 / 0.510 |
| 0.70-0.80 | 89 / 0.747 / 0.697 | 77 / 0.747 / 0.701 | 90 / 0.748 / 0.700 |
| 0.80-0.90 | 82 / 0.850 / 0.768 | 87 / 0.849 / 0.793 | 81 / 0.854 / 0.802 |
| 0.90-1.00 | 152 / 0.955 / 0.888 | 149 / 0.956 / 0.872 | 148 / 0.956 / 0.899 |

## Contract pricing — T-6h (2032 contracts, 26 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2032 | 0.1601 | 0.4815 | 0.415 | 0.421 | 2032 | 0.1601 | 0.1603 | 0.1639 |
| DATA_ONLY | 2032 | 0.1693 | 0.5055 | 0.421 | 0.421 | 2032 | 0.1693 | 0.1603 | 0.1639 |
| HYBRID_30 | 2032 | 0.1619 | 0.4866 | 0.413 | 0.421 | 2032 | 0.1619 | 0.1603 | 0.1639 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2032 | 26 | 0.00920 | [-0.00201, 0.02135] | 0.00920 | [-0.00201, 0.02135] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2032 | 26 | 0.00176 | [-0.00096, 0.00483] | 0.00176 | [-0.00096, 0.00483] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2032 | 26 | -0.00744 | [-0.01792, 0.00187] | -0.00744 | [-0.01792, 0.00187] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2032 | 26 | - | - | -0.00021 | [-0.00146, 0.00112] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1978 | 26 | - | - | -0.00032 | [-0.00222, 0.00165] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2032 | 26 | - | - | 0.00899 | [-0.00295, 0.02181] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1978 | 26 | - | - | 0.00922 | [-0.00329, 0.02248] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2032 | 26 | - | - | 0.00155 | [-0.00142, 0.00476] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1978 | 26 | - | - | 0.00155 | [-0.00176, 0.00519] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 104, 'GAME_WINNER': 52, 'SPREAD': 671, 'TEAM_TOTAL': 711, 'TOTAL': 494}; settlement: {'SETTLED': 2032}; close: {'OK': 1978, 'OK_STALE': 54}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 323 / 0.056 / 0.062 | 317 / 0.054 / 0.057 | 318 / 0.054 / 0.057 |
| 0.10-0.20 | 321 / 0.144 / 0.178 | 317 / 0.147 / 0.189 | 323 / 0.146 / 0.183 |
| 0.20-0.30 | 236 / 0.249 / 0.250 | 235 / 0.250 / 0.285 | 242 / 0.250 / 0.256 |
| 0.30-0.40 | 205 / 0.351 / 0.346 | 204 / 0.349 / 0.387 | 198 / 0.350 / 0.379 |
| 0.40-0.50 | 208 / 0.451 / 0.481 | 194 / 0.447 / 0.438 | 228 / 0.448 / 0.465 |
| 0.50-0.60 | 192 / 0.545 / 0.521 | 171 / 0.547 / 0.509 | 177 / 0.549 / 0.525 |
| 0.60-0.70 | 135 / 0.652 / 0.622 | 166 / 0.646 / 0.566 | 133 / 0.647 / 0.594 |
| 0.70-0.80 | 103 / 0.754 / 0.757 | 113 / 0.750 / 0.717 | 110 / 0.748 / 0.745 |
| 0.80-0.90 | 111 / 0.851 / 0.883 | 110 / 0.849 / 0.836 | 110 / 0.851 / 0.882 |
| 0.90-1.00 | 198 / 0.956 / 0.955 | 205 / 0.956 / 0.941 | 193 / 0.956 / 0.959 |

## Contract pricing — T-90m (2574 contracts, 33 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2574 | 0.1600 | 0.4843 | 0.416 | 0.397 | 2574 | 0.1600 | 0.1590 | 0.1618 |
| DATA_ONLY | 2574 | 0.1682 | 0.5064 | 0.420 | 0.397 | 2574 | 0.1682 | 0.1590 | 0.1618 |
| HYBRID_30 | 2574 | 0.1627 | 0.4893 | 0.413 | 0.397 | 2574 | 0.1627 | 0.1590 | 0.1618 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2574 | 33 | 0.00814 | [-0.00444, 0.01996] | 0.00814 | [-0.00444, 0.01996] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2574 | 33 | 0.00273 | [-0.00106, 0.00663] | 0.00273 | [-0.00106, 0.00663] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2574 | 33 | -0.00541 | [-0.01424, 0.00381] | -0.00541 | [-0.01424, 0.00381] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2574 | 33 | - | - | 0.00098 | [-0.00041, 0.00246] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 2517 | 33 | - | - | 0.00108 | [-0.00076, 0.00293] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2574 | 33 | - | - | 0.00913 | [-0.00346, 0.02153] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 2517 | 33 | - | - | 0.00946 | [-0.00337, 0.02233] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2574 | 33 | - | - | 0.00371 | [-0.00016, 0.00792] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 2517 | 33 | - | - | 0.00392 | [-0.00019, 0.00806] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 132, 'GAME_WINNER': 66, 'SPREAD': 851, 'TEAM_TOTAL': 898, 'TOTAL': 627}; settlement: {'SETTLED': 2574}; close: {'OK': 2517, 'OK_STALE': 57}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 401 / 0.054 / 0.030 | 395 / 0.054 / 0.046 | 406 / 0.053 / 0.034 |
| 0.10-0.20 | 408 / 0.144 / 0.162 | 402 / 0.145 / 0.172 | 406 / 0.146 / 0.167 |
| 0.20-0.30 | 299 / 0.247 / 0.258 | 308 / 0.250 / 0.276 | 305 / 0.249 / 0.266 |
| 0.30-0.40 | 255 / 0.349 / 0.310 | 259 / 0.350 / 0.324 | 251 / 0.349 / 0.339 |
| 0.40-0.50 | 255 / 0.450 / 0.412 | 249 / 0.448 / 0.406 | 289 / 0.448 / 0.446 |
| 0.50-0.60 | 252 / 0.545 / 0.532 | 220 / 0.549 / 0.486 | 221 / 0.549 / 0.484 |
| 0.60-0.70 | 180 / 0.651 / 0.567 | 207 / 0.647 / 0.551 | 176 / 0.649 / 0.545 |
| 0.70-0.80 | 130 / 0.751 / 0.723 | 140 / 0.748 / 0.686 | 138 / 0.749 / 0.696 |
| 0.80-0.90 | 144 / 0.850 / 0.840 | 138 / 0.850 / 0.833 | 137 / 0.851 / 0.854 |
| 0.90-1.00 | 250 / 0.956 / 0.924 | 256 / 0.956 / 0.906 | 245 / 0.956 / 0.931 |

## Contract pricing — T-30m (3432 contracts, 44 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 3432 | 0.1667 | 0.5005 | 0.413 | 0.416 | 3432 | 0.1667 | 0.1669 | 0.1695 |
| DATA_ONLY | 3432 | 0.1795 | 0.5356 | 0.421 | 0.416 | 3432 | 0.1795 | 0.1669 | 0.1695 |
| HYBRID_30 | 3432 | 0.1698 | 0.5089 | 0.413 | 0.416 | 3432 | 0.1698 | 0.1669 | 0.1695 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 3432 | 44 | 0.01274 | [0.00349, 0.02205] | 0.01274 | [0.00349, 0.02205] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 3432 | 44 | 0.00308 | [0.00027, 0.00589] | 0.00308 | [0.00027, 0.00589] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 3432 | 44 | -0.00966 | [-0.01704, -0.00265] | -0.00966 | [-0.01704, -0.00265] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 3432 | 44 | - | - | -0.00011 | [-0.00117, 0.00088] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 3367 | 44 | - | - | -0.00040 | [-0.00166, 0.00082] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 3432 | 44 | - | - | 0.01262 | [0.00334, 0.02225] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 3367 | 44 | - | - | 0.01262 | [0.00311, 0.02243] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 3432 | 44 | - | - | 0.00297 | [0.00013, 0.00602] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 3367 | 44 | - | - | 0.00278 | [-0.00019, 0.00591] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 176, 'GAME_WINNER': 88, 'SPREAD': 1133, 'TEAM_TOTAL': 1199, 'TOTAL': 836}; settlement: {'SETTLED': 3432}; close: {'OK': 3367, 'OK_STALE': 65}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 540 / 0.055 / 0.050 | 515 / 0.053 / 0.072 | 530 / 0.053 / 0.062 |
| 0.10-0.20 | 552 / 0.145 / 0.188 | 540 / 0.145 / 0.204 | 554 / 0.146 / 0.190 |
| 0.20-0.30 | 401 / 0.248 / 0.279 | 410 / 0.249 / 0.295 | 394 / 0.248 / 0.269 |
| 0.30-0.40 | 340 / 0.351 / 0.350 | 350 / 0.349 / 0.366 | 353 / 0.348 / 0.357 |
| 0.40-0.50 | 358 / 0.450 / 0.458 | 329 / 0.449 / 0.444 | 380 / 0.449 / 0.479 |
| 0.50-0.60 | 324 / 0.546 / 0.537 | 300 / 0.550 / 0.493 | 307 / 0.549 / 0.528 |
| 0.60-0.70 | 226 / 0.650 / 0.597 | 275 / 0.648 / 0.538 | 228 / 0.648 / 0.566 |
| 0.70-0.80 | 178 / 0.750 / 0.730 | 183 / 0.750 / 0.683 | 186 / 0.751 / 0.699 |
| 0.80-0.90 | 180 / 0.848 / 0.844 | 182 / 0.851 / 0.808 | 177 / 0.853 / 0.864 |
| 0.90-1.00 | 333 / 0.954 / 0.931 | 348 / 0.957 / 0.911 | 323 / 0.956 / 0.932 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 20 | 5 | 1 | 2 | 12 | 0 | 0.333 [0.061, 0.792] | 0.333 | 0.333 | 0.00 |
| T-24h | DATA_ONLY | total | 20 | 4 | 6 | 1 | 9 | 0 | 0.857 [0.487, 0.974] | 0.500 | 0.438 | 0.44 |
| T-24h | HYBRID_30 (derived) | margin | 20 | 14 | 0 | 1 | 5 | 0 | 0.000 [0.000, 0.793] | 0.167 | 0.167 | -0.08 |
| T-24h | HYBRID_30 (derived) | total | 20 | 17 | 0 | 0 | 3 | 0 | - - | 0.333 | 0.333 | 0.00 |
| T-6h | DATA_ONLY | margin | 26 | 4 | 6 | 2 | 14 | 0 | 0.750 [0.409, 0.929] | 0.364 | 0.409 | 0.11 |
| T-6h | DATA_ONLY | total | 26 | 9 | 4 | 3 | 10 | 0 | 0.571 [0.250, 0.842] | 0.412 | 0.412 | -0.03 |
| T-6h | HYBRID_30 (derived) | margin | 26 | 19 | 1 | 1 | 5 | 0 | 0.500 [0.095, 0.905] | 0.286 | 0.286 | 0.00 |
| T-6h | HYBRID_30 (derived) | total | 26 | 22 | 1 | 0 | 3 | 0 | 1.000 [0.207, 1.000] | 0.500 | 0.250 | 0.12 |
| T-90m | DATA_ONLY | margin | 33 | 5 | 5 | 2 | 21 | 0 | 0.714 [0.359, 0.918] | 0.393 | 0.393 | 0.02 |
| T-90m | DATA_ONLY | total | 33 | 11 | 4 | 4 | 14 | 0 | 0.500 [0.215, 0.785] | 0.364 | 0.364 | -0.02 |
| T-90m | HYBRID_30 (derived) | margin | 33 | 24 | 0 | 1 | 8 | 0 | 0.000 [0.000, 0.793] | 0.333 | 0.333 | -0.11 |
| T-90m | HYBRID_30 (derived) | total | 33 | 27 | 0 | 3 | 3 | 0 | 0.000 [0.000, 0.561] | 0.333 | 0.333 | -0.42 |
| T-30m | DATA_ONLY | margin | 44 | 8 | 5 | 2 | 29 | 0 | 0.714 [0.359, 0.918] | 0.333 | 0.333 | 0.06 |
| T-30m | DATA_ONLY | total | 44 | 16 | 6 | 4 | 18 | 0 | 0.600 [0.313, 0.832] | 0.321 | 0.321 | 0.00 |
| T-30m | HYBRID_30 (derived) | margin | 44 | 34 | 0 | 1 | 9 | 0 | 0.000 [0.000, 0.793] | 0.300 | 0.300 | -0.10 |
| T-30m | HYBRID_30 (derived) | total | 44 | 36 | 1 | 1 | 6 | 0 | 0.500 [0.095, 0.905] | 0.125 | 0.125 | 0.00 |
| latest_pregame | DATA_ONLY | margin | 45 | 8 | 5 | 2 | 30 | 0 | 0.714 [0.359, 0.918] | 0.324 | 0.324 | 0.05 |
| latest_pregame | DATA_ONLY | total | 45 | 16 | 6 | 4 | 19 | 0 | 0.600 [0.313, 0.832] | 0.310 | 0.310 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | margin | 45 | 35 | 0 | 1 | 9 | 0 | 0.000 [0.000, 0.793] | 0.300 | 0.300 | -0.10 |
| latest_pregame | HYBRID_30 (derived) | total | 45 | 36 | 1 | 1 | 7 | 0 | 0.500 [0.095, 0.905] | 0.111 | 0.111 | 0.00 |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 8 | 1 | 1 | 6 | 0 | 0.500 |
| margin | 1-2 | 13 | 3 | 0 | 10 | 0 | 1.000 |
| margin | 2-3 | 12 | 2 | 1 | 9 | 0 | 0.667 |
| margin | 3-5 | 10 | 0 | 1 | 9 | 0 | 0.000 |
| margin | >5 | 2 | 0 | 0 | 2 | 0 | - |
| total | <=1 | 16 | 2 | 1 | 13 | 0 | 0.667 |
| total | 1-2 | 10 | 1 | 2 | 7 | 0 | 0.333 |
| total | 2-3 | 7 | 4 | 1 | 2 | 0 | 0.800 |
| total | 3-5 | 9 | 1 | 1 | 7 | 0 | 0.500 |
| total | >5 | 3 | 0 | 0 | 3 | 0 | - |

### Future-window evaluation of the preregistered hypotheses (generation week excluded)

| hypothesis | status | new games | directional | toward rate | trend | suggested status |
|---|---|---|---|---|---|---|
| H2-GC-MARGIN-2026W02 | PREREGISTERED | 14 | 3 | 0.667 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |
| H2-GC-TOTAL-2026W02 | PREREGISTERED | 14 | 3 | 0.667 | INCONCLUSIVE | INCONCLUSIVE (suggestion only; owner approval required) |

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

