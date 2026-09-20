# Three-arm game-centre experiment — season to date (cumulative)

> **INSUFFICIENT EVIDENCE.** 16 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 281 | 16 | 2 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 1 | 1 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 6 | 6 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 6 | 6 | 2 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 15 | 15 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 16 | 16 | 2 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

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

## Game-centre accuracy — latest_pregame (16 games, 2 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 16 | 2 | 11.78 | 13.82 | 1.91 | 11.47 | 16.42 | -7.22 | 0.204 |
| DATA_ONLY | 16 | 2 | 12.64 | 14.54 | 1.51 | 13.22 | 17.58 | -6.24 | 0.247 |
| HYBRID_30 | 16 | 2 | 12.04 | 13.99 | 1.79 | 11.95 | 16.72 | -6.93 | 0.214 |
| market at snapshot | 16 | 2 | 11.78 | 13.82 | 1.91 | 11.47 | 16.42 | -7.22 | - |
| market at close | 16 | 2 | 11.84 | 13.82 | 1.97 | 11.50 | 16.50 | -7.31 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 16 | margin | 0.858 | 0.622 | [-0.360, 2.076] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 16 | total | 1.749 | 0.621 | [0.531, 2.967] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | margin | 0.257 | 0.186 | [-0.108, 0.623] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 16 | total | 0.481 | 0.199 | [0.092, 0.870] | 0.375 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | margin | -0.601 | 0.435 | [-1.453, 0.252] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 16 | total | -1.268 | 0.430 | [-2.110, -0.426] | 0.688 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 16 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 16 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | margin | 0.858 | 0.622 | [-0.360, 2.076] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 16 | total | 1.749 | 0.621 | [0.531, 2.967] | 0.312 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | margin | 0.257 | 0.186 | [-0.108, 0.623] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 16 | total | 0.481 | 0.199 | [0.092, 0.870] | 0.375 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | margin | -0.062 | 0.111 | [-0.279, 0.154] | 0.125 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 16 | total | -0.031 | 0.055 | [-0.140, 0.077] | 0.125 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | margin | 0.796 | 0.644 | [-0.466, 2.057] | 0.438 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 16 | total | 1.718 | 0.633 | [0.477, 2.959] | 0.375 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | margin | 0.195 | 0.228 | [-0.251, 0.641] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 16 | total | 0.450 | 0.207 | [0.043, 0.856] | 0.438 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 16 | 2 | 1 | 13 | 0 | 0.667 | 0.500 | 2.10 |
| DATA_ONLY | total | 16 | 2 | 2 | 12 | 0 | 0.500 | 0.312 | 2.38 |
| HYBRID_30 | margin | 16 | 2 | 1 | 13 | 0 | 0.667 | 0.500 | 0.63 |
| HYBRID_30 | total | 16 | 2 | 2 | 12 | 0 | 0.500 | 0.375 | 0.71 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 5 | 15.37 | 15.80 | 1.000 |
| DATA_ONLY | margin | 1-2 | 3 | 4.77 | 4.17 | - |
| DATA_ONLY | margin | 2-3 | 3 | 14.06 | 13.17 | 1.000 |
| DATA_ONLY | margin | 3-5 | 5 | 13.78 | 11.50 | 0.000 |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 5 | 17.11 | 17.20 | 1.000 |
| DATA_ONLY | total | 1-2 | 3 | 11.72 | 12.33 | 0.000 |
| DATA_ONLY | total | 2-3 | 1 | 1.17 | 1.00 | 1.000 |
| DATA_ONLY | total | 3-5 | 5 | 10.90 | 7.00 | 0.000 |
| DATA_ONLY | total | >5 | 2 | 17.55 | 12.25 | - |
| HYBRID_30 | margin | <=1 | 13 | 11.50 | 11.31 | 1.000 |
| HYBRID_30 | margin | 1-2 | 3 | 14.36 | 13.83 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 11 | 12.73 | 12.68 | 0.667 |
| HYBRID_30 | total | 1-2 | 5 | 10.23 | 8.80 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 16}; DATA_ONLY quality states: {'OK': 16}; close centre status: {'OK': 16}.

## Game-centre accuracy — T-24h (1 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1 | 1 | 19.50 | 19.50 | -19.50 | 2.50 | 2.50 | 2.50 | 0.182 |
| DATA_ONLY | 1 | 1 | 23.87 | 23.87 | -23.87 | 0.12 | 0.12 | -0.12 | 0.387 |
| HYBRID_30 | 1 | 1 | 20.81 | 20.81 | -20.81 | 1.72 | 1.72 | 1.72 | 0.258 |
| market at snapshot | 1 | 1 | 19.50 | 19.50 | -19.50 | 2.50 | 2.50 | 2.50 | - |
| market at close | 1 | 1 | 19.50 | 19.50 | -19.50 | 1.00 | 1.00 | 1.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 1 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 1 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 1 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 1 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 1 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 1 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 1 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 1 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 4.37 |
| DATA_ONLY | total | 1 | 1 | 0 | 0 | 0 | 1.000 | 1.000 | 2.62 |
| HYBRID_30 | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 1.31 |
| HYBRID_30 | total | 1 | 1 | 0 | 0 | 0 | 1.000 | 1.000 | 0.78 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 0 | - | - | - |
| DATA_ONLY | margin | 2-3 | 0 | - | - | - |
| DATA_ONLY | margin | 3-5 | 1 | 23.87 | 19.50 | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 0 | - | - | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 1 | 0.12 | 2.50 | 1.000 |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 0 | - | - | - |
| HYBRID_30 | margin | 1-2 | 1 | 20.81 | 19.50 | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 1 | 1.72 | 2.50 | 1.000 |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 1}; DATA_ONLY quality states: {'OK': 1}; close centre status: {'OK': 1}.

## Game-centre accuracy — T-6h (6 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 6 | 1 | 14.33 | 16.09 | 2.17 | 6.50 | 8.95 | 0.50 | 0.314 |
| DATA_ONLY | 6 | 1 | 14.20 | 15.78 | 1.71 | 8.49 | 10.68 | 2.73 | 0.301 |
| HYBRID_30 | 6 | 1 | 14.29 | 15.93 | 2.03 | 6.75 | 9.39 | 1.17 | 0.315 |
| market at snapshot | 6 | 1 | 14.33 | 16.09 | 2.17 | 6.50 | 8.95 | 0.50 | - |
| market at close | 6 | 1 | 14.83 | 16.27 | 2.00 | 6.67 | 9.04 | 0.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 6 | margin | -0.133 | 1.421 | [-2.919, 2.652] | 0.667 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 6 | total | 1.989 | 0.717 | [0.584, 3.393] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 6 | margin | -0.040 | 0.426 | [-0.876, 0.796] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 6 | total | 0.247 | 0.243 | [-0.230, 0.723] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 6 | margin | 0.093 | 0.995 | [-1.857, 2.043] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 6 | total | -1.742 | 0.642 | [-3.000, -0.484] | 1.000 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 6 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 6 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 6 | margin | -0.133 | 1.421 | [-2.919, 2.652] | 0.667 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 6 | total | 1.989 | 0.717 | [0.584, 3.393] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 6 | margin | -0.040 | 0.426 | [-0.876, 0.796] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 6 | total | 0.247 | 0.243 | [-0.230, 0.723] | 0.333 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 6 | margin | -0.500 | 0.316 | [-1.120, 0.120] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 6 | total | -0.167 | 0.422 | [-0.993, 0.660] | 0.333 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 6 | margin | -0.633 | 1.316 | [-3.213, 1.946] | 0.833 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 6 | total | 1.822 | 1.023 | [-0.184, 3.828] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 6 | margin | -0.540 | 0.407 | [-1.337, 0.257] | 0.833 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 6 | total | 0.080 | 0.523 | [-0.946, 1.105] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 6 | 3 | 1 | 2 | 0 | 0.750 | 0.667 | 2.54 |
| DATA_ONLY | total | 6 | 3 | 1 | 2 | 0 | 0.750 | 0.000 | 2.49 |
| HYBRID_30 | margin | 6 | 3 | 1 | 2 | 0 | 0.750 | 0.667 | 0.76 |
| HYBRID_30 | total | 6 | 3 | 1 | 2 | 0 | 0.750 | 0.333 | 0.75 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 19.41 | 20.00 | - |
| DATA_ONLY | margin | 1-2 | 1 | 4.39 | 3.00 | 1.000 |
| DATA_ONLY | margin | 2-3 | 1 | 19.10 | 22.00 | 1.000 |
| DATA_ONLY | margin | 3-5 | 1 | 6.57 | 10.50 | 0.000 |
| DATA_ONLY | margin | >5 | 1 | 16.33 | 10.50 | 1.000 |
| DATA_ONLY | total | <=1 | 2 | 8.64 | 8.25 | 1.000 |
| DATA_ONLY | total | 1-2 | 1 | 1.27 | 0.50 | - |
| DATA_ONLY | total | 2-3 | 1 | 9.70 | 7.50 | 0.000 |
| DATA_ONLY | total | 3-5 | 1 | 17.49 | 13.50 | - |
| DATA_ONLY | total | >5 | 1 | 5.18 | 1.00 | 1.000 |
| HYBRID_30 | margin | <=1 | 4 | 16.05 | 16.25 | 1.000 |
| HYBRID_30 | margin | 1-2 | 2 | 10.78 | 10.50 | 0.500 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 4 | 6.23 | 6.12 | 0.667 |
| HYBRID_30 | total | 1-2 | 2 | 7.78 | 7.25 | 1.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 6}; DATA_ONLY quality states: {'OK': 6}; close centre status: {'OK': 6}.

## Game-centre accuracy — T-90m (6 games, 2 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 6 | 2 | 11.33 | 12.82 | -2.67 | 7.33 | 9.99 | -5.00 | 0.255 |
| DATA_ONLY | 6 | 2 | 11.20 | 12.55 | -3.37 | 9.40 | 12.30 | -4.05 | 0.254 |
| HYBRID_30 | 6 | 2 | 11.29 | 12.67 | -2.88 | 7.84 | 10.62 | -4.71 | 0.247 |
| market at snapshot | 6 | 2 | 11.33 | 12.82 | -2.67 | 7.33 | 9.99 | -5.00 | - |
| market at close | 6 | 2 | 11.50 | 12.96 | -2.83 | 7.33 | 10.12 | -5.17 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 6 | margin | -0.134 | 1.270 | [-2.624, 2.356] | 0.667 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 6 | total | 2.062 | 1.157 | [-0.206, 4.330] | 0.167 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 6 | margin | -0.040 | 0.381 | [-0.787, 0.707] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 6 | total | 0.502 | 0.401 | [-0.284, 1.287] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 6 | margin | 0.094 | 0.889 | [-1.650, 1.837] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 6 | total | -1.560 | 0.779 | [-3.088, -0.032] | 0.833 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 6 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 6 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 6 | margin | -0.134 | 1.270 | [-2.624, 2.356] | 0.667 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 6 | total | 2.062 | 1.157 | [-0.206, 4.330] | 0.167 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 6 | margin | -0.040 | 0.381 | [-0.787, 0.707] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 6 | total | 0.502 | 0.401 | [-0.284, 1.287] | 0.333 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 6 | margin | -0.167 | 0.167 | [-0.493, 0.160] | 0.167 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 6 | total | 0.000 | 0.129 | [-0.253, 0.253] | 0.167 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 6 | margin | -0.300 | 1.377 | [-2.999, 2.398] | 0.667 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 6 | total | 2.062 | 1.160 | [-0.213, 4.336] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 6 | margin | -0.207 | 0.499 | [-1.185, 0.771] | 0.667 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 6 | total | 0.502 | 0.389 | [-0.261, 1.264] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 6 | 0 | 1 | 5 | 0 | 0.000 | 0.667 | 2.33 |
| DATA_ONLY | total | 6 | 2 | 1 | 3 | 0 | 0.667 | 0.167 | 2.94 |
| HYBRID_30 | margin | 6 | 0 | 1 | 5 | 0 | 0.000 | 0.667 | 0.70 |
| HYBRID_30 | total | 6 | 2 | 1 | 3 | 0 | 0.667 | 0.333 | 0.88 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 2 | 9.48 | 10.00 | - |
| DATA_ONLY | margin | 1-2 | 1 | 6.26 | 4.50 | - |
| DATA_ONLY | margin | 2-3 | 1 | 19.10 | 21.50 | - |
| DATA_ONLY | margin | 3-5 | 2 | 11.45 | 11.00 | 0.000 |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 15.92 | 15.50 | 1.000 |
| DATA_ONLY | total | 1-2 | 1 | 1.36 | 3.00 | - |
| DATA_ONLY | total | 2-3 | 1 | 1.17 | 1.00 | 1.000 |
| DATA_ONLY | total | 3-5 | 2 | 7.44 | 3.50 | 0.000 |
| DATA_ONLY | total | >5 | 1 | 23.04 | 17.50 | - |
| HYBRID_30 | margin | <=1 | 4 | 11.37 | 11.50 | - |
| HYBRID_30 | margin | 1-2 | 2 | 11.13 | 11.00 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 4 | 6.49 | 6.50 | 1.000 |
| HYBRID_30 | total | 1-2 | 2 | 10.53 | 9.00 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 6}; DATA_ONLY quality states: {'OK': 6}; close centre status: {'OK': 6}.

## Game-centre accuracy — T-30m (15 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 15 | 1 | 12.27 | 14.22 | 2.33 | 11.07 | 16.35 | -6.53 | 0.212 |
| DATA_ONLY | 15 | 1 | 13.06 | 14.93 | 2.03 | 12.56 | 17.16 | -5.12 | 0.254 |
| HYBRID_30 | 15 | 1 | 12.51 | 14.39 | 2.24 | 11.47 | 16.55 | -6.11 | 0.222 |
| market at snapshot | 15 | 1 | 12.27 | 14.22 | 2.33 | 11.07 | 16.35 | -6.53 | - |
| market at close | 15 | 1 | 12.33 | 14.23 | 2.40 | 11.10 | 16.43 | -6.63 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 15 | margin | 0.798 | 0.661 | [-0.498, 2.094] | 0.533 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 15 | total | 1.497 | 0.607 | [0.307, 2.686] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | margin | 0.239 | 0.198 | [-0.149, 0.628] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 15 | total | 0.402 | 0.195 | [0.020, 0.784] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | margin | -0.559 | 0.463 | [-1.466, 0.349] | 0.467 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 15 | total | -1.094 | 0.420 | [-1.917, -0.271] | 0.667 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 15 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 15 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | margin | 0.798 | 0.661 | [-0.498, 2.094] | 0.533 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 15 | total | 1.497 | 0.607 | [0.307, 2.686] | 0.333 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | margin | 0.239 | 0.198 | [-0.149, 0.628] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 15 | total | 0.402 | 0.195 | [0.020, 0.784] | 0.400 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | margin | -0.067 | 0.118 | [-0.298, 0.165] | 0.133 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 15 | total | -0.033 | 0.059 | [-0.149, 0.082] | 0.133 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | margin | 0.731 | 0.685 | [-0.611, 2.074] | 0.467 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 15 | total | 1.463 | 0.620 | [0.248, 2.678] | 0.400 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | margin | 0.173 | 0.242 | [-0.302, 0.647] | 0.533 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 15 | total | 0.369 | 0.204 | [-0.031, 0.769] | 0.467 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 15 | 2 | 1 | 12 | 0 | 0.667 | 0.533 | 2.13 |
| DATA_ONLY | total | 15 | 2 | 2 | 11 | 0 | 0.500 | 0.333 | 2.17 |
| HYBRID_30 | margin | 15 | 2 | 1 | 12 | 0 | 0.667 | 0.533 | 0.64 |
| HYBRID_30 | total | 15 | 2 | 2 | 11 | 0 | 0.500 | 0.400 | 0.65 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 5 | 15.37 | 15.80 | 1.000 |
| DATA_ONLY | margin | 1-2 | 2 | 4.02 | 4.00 | - |
| DATA_ONLY | margin | 2-3 | 3 | 14.06 | 13.17 | 1.000 |
| DATA_ONLY | margin | 3-5 | 5 | 13.78 | 11.50 | 0.000 |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 5 | 17.11 | 17.20 | 1.000 |
| DATA_ONLY | total | 1-2 | 3 | 11.72 | 12.33 | 0.000 |
| DATA_ONLY | total | 2-3 | 1 | 1.17 | 1.00 | 1.000 |
| DATA_ONLY | total | 3-5 | 5 | 10.90 | 7.00 | 0.000 |
| DATA_ONLY | total | >5 | 1 | 12.06 | 7.00 | - |
| HYBRID_30 | margin | <=1 | 12 | 12.04 | 11.88 | 1.000 |
| HYBRID_30 | margin | 1-2 | 3 | 14.36 | 13.83 | 0.000 |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 11 | 12.73 | 12.68 | 0.667 |
| HYBRID_30 | total | 1-2 | 4 | 8.00 | 6.62 | 0.000 |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 15}; DATA_ONLY quality states: {'OK': 15}; close centre status: {'OK': 15}.

## Contract pricing — latest_pregame (1242 contracts, 16 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1242 | 0.1764 | 0.5254 | 0.421 | 0.494 | 1242 | 0.1764 | 0.1762 | 0.1772 |
| DATA_ONLY | 1242 | 0.1961 | 0.5754 | 0.430 | 0.494 | 1242 | 0.1961 | 0.1762 | 0.1772 |
| HYBRID_30 | 1242 | 0.1794 | 0.5317 | 0.422 | 0.494 | 1242 | 0.1794 | 0.1762 | 0.1772 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1242 | 16 | 0.01971 | [0.00482, 0.03530] | 0.01971 | [0.00482, 0.03530] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1242 | 16 | 0.00301 | [-0.00240, 0.00851] | 0.00301 | [-0.00240, 0.00851] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1242 | 16 | -0.01670 | [-0.02830, -0.00572] | -0.01670 | [-0.02830, -0.00572] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1242 | 16 | - | - | 0.00021 | [-0.00151, 0.00187] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1230 | 16 | - | - | -0.00073 | [-0.00293, 0.00148] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1242 | 16 | - | - | 0.01992 | [0.00424, 0.03626] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1230 | 16 | - | - | 0.01916 | [0.00270, 0.03651] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1242 | 16 | - | - | 0.00322 | [-0.00251, 0.00937] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1230 | 16 | - | - | 0.00231 | [-0.00395, 0.00901] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 64, 'GAME_WINNER': 32, 'SPREAD': 404, 'TEAM_TOTAL': 438, 'TOTAL': 304}; settlement: {'SETTLED': 1242}; close: {'OK': 1230, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 173 / 0.055 / 0.104 | 168 / 0.055 / 0.137 | 170 / 0.055 / 0.112 |
| 0.10-0.20 | 205 / 0.143 / 0.239 | 195 / 0.144 / 0.277 | 203 / 0.144 / 0.236 |
| 0.20-0.30 | 149 / 0.247 / 0.329 | 152 / 0.247 / 0.362 | 143 / 0.246 / 0.308 |
| 0.30-0.40 | 119 / 0.350 / 0.437 | 133 / 0.350 / 0.459 | 130 / 0.347 / 0.454 |
| 0.40-0.50 | 133 / 0.447 / 0.541 | 123 / 0.451 / 0.577 | 142 / 0.450 / 0.585 |
| 0.50-0.60 | 125 / 0.547 / 0.672 | 110 / 0.550 / 0.582 | 120 / 0.548 / 0.658 |
| 0.60-0.70 | 83 / 0.652 / 0.687 | 96 / 0.648 / 0.573 | 81 / 0.651 / 0.642 |
| 0.70-0.80 | 59 / 0.750 / 0.797 | 65 / 0.755 / 0.708 | 59 / 0.752 / 0.763 |
| 0.80-0.90 | 66 / 0.848 / 0.924 | 62 / 0.852 / 0.871 | 67 / 0.851 / 0.925 |
| 0.90-1.00 | 130 / 0.955 / 0.962 | 138 / 0.958 / 0.949 | 127 / 0.957 / 0.969 |

## Contract pricing — T-24h (77 contracts, 1 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 77 | 0.2031 | 0.5922 | 0.415 | 0.455 | 77 | 0.2031 | 0.2071 | 0.2057 |
| DATA_ONLY | 77 | 0.2553 | 0.7304 | 0.377 | 0.455 | 77 | 0.2553 | 0.2071 | 0.2057 |
| HYBRID_30 | 77 | 0.2088 | 0.5998 | 0.410 | 0.455 | 77 | 0.2088 | 0.2071 | 0.2057 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 77 | 1 | 0.05211 | - | 0.05211 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 77 | 1 | 0.00561 | - | 0.00561 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 77 | 1 | -0.04650 | - | -0.04650 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 77 | 1 | - | - | -0.00397 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 77 | 1 | - | - | -0.00260 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 77 | 1 | - | - | 0.04814 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 77 | 1 | - | - | 0.04951 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 77 | 1 | - | - | 0.00164 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 77 | 1 | - | - | 0.00301 | - | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 4, 'GAME_WINNER': 2, 'SPREAD': 25, 'TEAM_TOTAL': 27, 'TOTAL': 19}; settlement: {'SETTLED': 77}; close: {'OK': 77}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 11 / 0.059 / 0.091 | 14 / 0.043 / 0.286 | 10 / 0.054 / 0.100 |
| 0.10-0.20 | 12 / 0.142 / 0.333 | 11 / 0.143 / 0.455 | 11 / 0.141 / 0.364 |
| 0.20-0.30 | 9 / 0.247 / 0.444 | 12 / 0.249 / 0.500 | 10 / 0.249 / 0.400 |
| 0.30-0.40 | 10 / 0.347 / 0.300 | 10 / 0.357 / 0.400 | 10 / 0.356 / 0.400 |
| 0.40-0.50 | 8 / 0.455 / 0.500 | 9 / 0.457 / 0.333 | 11 / 0.455 / 0.455 |
| 0.50-0.60 | 7 / 0.545 / 0.429 | 4 / 0.560 / 0.250 | 7 / 0.543 / 0.429 |
| 0.60-0.70 | 4 / 0.626 / 0.750 | 5 / 0.640 / 0.400 | 5 / 0.643 / 0.600 |
| 0.70-0.80 | 5 / 0.748 / 0.600 | 1 / 0.703 / 1.000 | 3 / 0.762 / 0.667 |
| 0.80-0.90 | 3 / 0.863 / 0.667 | 4 / 0.837 / 0.750 | 4 / 0.861 / 0.750 |
| 0.90-1.00 | 8 / 0.955 / 1.000 | 7 / 0.950 / 0.857 | 6 / 0.946 / 1.000 |

## Contract pricing — T-6h (466 contracts, 6 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 466 | 0.1885 | 0.5585 | 0.419 | 0.418 | 466 | 0.1885 | 0.1899 | 0.1904 |
| DATA_ONLY | 466 | 0.1971 | 0.5807 | 0.443 | 0.418 | 466 | 0.1971 | 0.1899 | 0.1904 |
| HYBRID_30 | 466 | 0.1871 | 0.5564 | 0.424 | 0.418 | 466 | 0.1871 | 0.1899 | 0.1904 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 466 | 6 | 0.00865 | [-0.01933, 0.04168] | 0.00865 | [-0.01933, 0.04168] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 466 | 6 | -0.00137 | [-0.00607, 0.00362] | -0.00137 | [-0.00607, 0.00362] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 466 | 6 | -0.01002 | [-0.03878, 0.01441] | -0.01002 | [-0.03878, 0.01441] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 466 | 6 | - | - | -0.00146 | [-0.00347, 0.00054] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 461 | 6 | - | - | -0.00214 | [-0.00671, 0.00283] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 466 | 6 | - | - | 0.00719 | [-0.02152, 0.04167] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 461 | 6 | - | - | 0.00664 | [-0.02421, 0.04282] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 466 | 6 | - | - | -0.00283 | [-0.00866, 0.00330] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 461 | 6 | - | - | -0.00355 | [-0.01177, 0.00548] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 24, 'GAME_WINNER': 12, 'SPREAD': 151, 'TEAM_TOTAL': 165, 'TOTAL': 114}; settlement: {'SETTLED': 466}; close: {'OK': 461, 'OK_STALE': 5}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 68 / 0.057 / 0.103 | 60 / 0.057 / 0.100 | 68 / 0.057 / 0.088 |
| 0.10-0.20 | 74 / 0.143 / 0.230 | 72 / 0.147 / 0.250 | 73 / 0.146 / 0.247 |
| 0.20-0.30 | 55 / 0.248 / 0.309 | 56 / 0.247 / 0.304 | 53 / 0.248 / 0.264 |
| 0.30-0.40 | 48 / 0.351 / 0.375 | 47 / 0.350 / 0.362 | 46 / 0.347 / 0.413 |
| 0.40-0.50 | 50 / 0.447 / 0.360 | 41 / 0.452 / 0.390 | 54 / 0.448 / 0.333 |
| 0.50-0.60 | 46 / 0.546 / 0.543 | 41 / 0.547 / 0.439 | 44 / 0.544 / 0.568 |
| 0.60-0.70 | 31 / 0.655 / 0.581 | 43 / 0.647 / 0.419 | 31 / 0.649 / 0.548 |
| 0.70-0.80 | 23 / 0.753 / 0.522 | 27 / 0.753 / 0.630 | 22 / 0.751 / 0.591 |
| 0.80-0.90 | 27 / 0.854 / 0.852 | 23 / 0.851 / 0.739 | 23 / 0.844 / 0.783 |
| 0.90-1.00 | 44 / 0.959 / 0.909 | 56 / 0.958 / 0.911 | 52 / 0.955 / 0.904 |

## Contract pricing — T-90m (465 contracts, 6 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 465 | 0.1664 | 0.4975 | 0.427 | 0.477 | 465 | 0.1664 | 0.1674 | 0.1678 |
| DATA_ONLY | 465 | 0.1791 | 0.5265 | 0.434 | 0.477 | 465 | 0.1791 | 0.1674 | 0.1678 |
| HYBRID_30 | 465 | 0.1678 | 0.4974 | 0.425 | 0.477 | 465 | 0.1678 | 0.1674 | 0.1678 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 465 | 6 | 0.01269 | [-0.01799, 0.04780] | 0.01269 | [-0.01799, 0.04780] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 465 | 6 | 0.00141 | [-0.00943, 0.01295] | 0.00141 | [-0.00943, 0.01295] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 465 | 6 | -0.01128 | [-0.03578, 0.00924] | -0.01128 | [-0.03578, 0.00924] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 465 | 6 | - | - | -0.00099 | [-0.00305, 0.00129] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 460 | 6 | - | - | -0.00174 | [-0.00493, 0.00223] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 465 | 6 | - | - | 0.01170 | [-0.02017, 0.04912] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 460 | 6 | - | - | 0.01102 | [-0.02195, 0.05090] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 465 | 6 | - | - | 0.00042 | [-0.01161, 0.01350] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 460 | 6 | - | - | -0.00033 | [-0.01418, 0.01409] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 24, 'GAME_WINNER': 12, 'SPREAD': 151, 'TEAM_TOTAL': 164, 'TOTAL': 114}; settlement: {'SETTLED': 465}; close: {'OK': 460, 'OK_STALE': 5}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 64 / 0.056 / 0.078 | 62 / 0.057 / 0.097 | 67 / 0.057 / 0.060 |
| 0.10-0.20 | 75 / 0.141 / 0.213 | 72 / 0.144 / 0.250 | 72 / 0.147 / 0.222 |
| 0.20-0.30 | 55 / 0.245 / 0.327 | 58 / 0.250 / 0.328 | 54 / 0.248 / 0.333 |
| 0.30-0.40 | 47 / 0.351 / 0.383 | 49 / 0.354 / 0.408 | 48 / 0.347 / 0.396 |
| 0.40-0.50 | 44 / 0.447 / 0.432 | 48 / 0.454 / 0.521 | 53 / 0.449 / 0.509 |
| 0.50-0.60 | 49 / 0.548 / 0.694 | 37 / 0.551 / 0.595 | 43 / 0.551 / 0.698 |
| 0.60-0.70 | 36 / 0.658 / 0.667 | 35 / 0.647 / 0.543 | 32 / 0.654 / 0.625 |
| 0.70-0.80 | 17 / 0.754 / 0.765 | 28 / 0.748 / 0.714 | 22 / 0.749 / 0.727 |
| 0.80-0.90 | 28 / 0.849 / 0.929 | 23 / 0.851 / 0.913 | 26 / 0.852 / 0.962 |
| 0.90-1.00 | 50 / 0.957 / 0.980 | 53 / 0.957 / 0.981 | 48 / 0.959 / 0.979 |

## Contract pricing — T-30m (1165 contracts, 15 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1165 | 0.1790 | 0.5325 | 0.417 | 0.482 | 1165 | 0.1790 | 0.1788 | 0.1799 |
| DATA_ONLY | 1165 | 0.1959 | 0.5753 | 0.430 | 0.482 | 1165 | 0.1959 | 0.1788 | 0.1799 |
| HYBRID_30 | 1165 | 0.1805 | 0.5353 | 0.420 | 0.482 | 1165 | 0.1805 | 0.1788 | 0.1799 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 1165 | 15 | 0.01695 | [0.00173, 0.03226] | 0.01695 | [0.00173, 0.03226] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 1165 | 15 | 0.00155 | [-0.00309, 0.00608] | 0.00155 | [-0.00309, 0.00608] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 1165 | 15 | -0.01540 | [-0.02718, -0.00391] | -0.01540 | [-0.02718, -0.00391] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 1165 | 15 | - | - | 0.00024 | [-0.00171, 0.00205] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 1153 | 15 | - | - | -0.00075 | [-0.00325, 0.00168] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 1165 | 15 | - | - | 0.01719 | [0.00141, 0.03346] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 1153 | 15 | - | - | 0.01636 | [-0.00036, 0.03333] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 1165 | 15 | - | - | 0.00179 | [-0.00338, 0.00699] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 1153 | 15 | - | - | 0.00081 | [-0.00502, 0.00694] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 60, 'GAME_WINNER': 30, 'SPREAD': 379, 'TEAM_TOTAL': 411, 'TOTAL': 285}; settlement: {'SETTLED': 1165}; close: {'OK': 1153, 'OK_STALE': 12}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 167 / 0.054 / 0.108 | 158 / 0.054 / 0.133 | 162 / 0.055 / 0.117 |
| 0.10-0.20 | 192 / 0.143 / 0.240 | 182 / 0.144 / 0.275 | 189 / 0.144 / 0.233 |
| 0.20-0.30 | 139 / 0.247 / 0.331 | 142 / 0.247 / 0.352 | 134 / 0.247 / 0.299 |
| 0.30-0.40 | 113 / 0.351 / 0.425 | 125 / 0.350 / 0.448 | 125 / 0.348 / 0.448 |
| 0.40-0.50 | 130 / 0.447 / 0.531 | 113 / 0.451 / 0.540 | 132 / 0.450 / 0.553 |
| 0.50-0.60 | 114 / 0.546 / 0.640 | 105 / 0.550 / 0.562 | 114 / 0.548 / 0.640 |
| 0.60-0.70 | 75 / 0.651 / 0.653 | 92 / 0.648 / 0.554 | 75 / 0.651 / 0.613 |
| 0.70-0.80 | 57 / 0.750 / 0.789 | 61 / 0.756 / 0.689 | 57 / 0.753 / 0.754 |
| 0.80-0.90 | 60 / 0.847 / 0.917 | 58 / 0.852 / 0.862 | 61 / 0.852 / 0.918 |
| 0.90-1.00 | 118 / 0.954 / 0.958 | 129 / 0.958 / 0.946 | 116 / 0.956 / 0.966 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

1055 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_01_CHI_CAR | Jonathon Brooks | receiving_yards | 1.0 | 0–11 | 48 | 64.75 | 0.99 | 1.0 | 2 | 0.98 | 24.00 | EXPECTED_ACTIVE | True | 0.427 | EFFICIENCY_MISS |
| 2026_01_SF_LA | Deebo Samuel Sr. | rushing_yards | 1.0 | 0–4 | 12 | 16.19 | 0.99 | 2.0 | 1 | 0.50 | 12.00 | EXPECTED_ACTIVE | True | 0.460 | EFFICIENCY_MISS |
| 2026_01_CLE_JAX | Bhayshul Tuten | receiving_yards | 2.9 | 0–31 | 22 | 9.89 | 0.89 | 1.3 | 1 | 2.33 | 22.00 | EXPECTED_ACTIVE | True | 0.283 | EFFICIENCY_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | receiving_yards | 2.7 | 0–29 | 21 | 9.44 | 0.89 | 1.1 | 3 | 2.49 | 7.00 | EXPECTED_ACTIVE | True | 0.361 | EFFICIENCY_MISS |
| 2026_01_WAS_PHI | Jacory Croskey-Merritt | receiving_yards | 1.0 | 0–11 | -7 | -9.44 | 0.05 | 1.2 | 1 | 0.83 | -7.00 | EXPECTED_ACTIVE | True | -0.183 | EFFICIENCY_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | touchdowns | 0.0 | -–- | 1 | 4.99 | - | 2.7 | 4 | - | - | EXPECTED_ACTIVE | True | 0.047 | UNEXPLAINED_VARIANCE |
| 2026_01_CHI_CAR | Kalif Raymond | receptions | 1.5 | 0–5 | 8 | 4.72 | 0.99 | 2.1 | 9 | 0.70 | 0.89 | EXPECTED_ACTIVE | True | 0.070 | OPPORTUNITY_MISS |
| 2026_01_DAL_NYG | Isaiah Likely | receptions | 1.4 | 0–5 | 8 | 4.72 | 0.99 | 1.9 | 8 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.406 | OPPORTUNITY_MISS |
| 2026_01_BUF_HOU | Dalton Kincaid | receiving_yards | 26.6 | 0–74 | 130 | 4.68 | 0.99 | 2.3 | 6 | 11.60 | 21.67 | EXPECTED_ACTIVE | True | 0.238 | OPPORTUNITY_MISS |
| 2026_01_BAL_IND | Derrick Henry | receiving_yards | 5.3 | 0–56 | 19 | 4.27 | 0.80 | 1.3 | 1 | 4.05 | 19.00 | EXPECTED_ACTIVE | True | 0.062 | EFFICIENCY_MISS |
| 2026_01_CLE_JAX | Denzel Boston | touchdowns | 0.1 | -–- | 1 | 4.24 | - | 4.5 | 4 | - | - | EXPECTED_ACTIVE | True | 0.062 | UNEXPLAINED_VARIANCE |
| 2026_01_MIA_LV | Caleb Douglas | receiving_yards | 19.8 | 0–67 | 94 | 4.20 | 0.98 | 1.9 | 7 | 10.66 | 13.43 | EXPECTED_ACTIVE | True | 0.198 | OPPORTUNITY_MISS |
| 2026_01_DAL_NYG | Isaiah Likely | receiving_yards | 16.8 | 0–57 | 78 | 4.11 | 0.97 | 1.9 | 8 | 8.94 | 9.75 | EXPECTED_ACTIVE | True | 0.420 | OPPORTUNITY_MISS |
| 2026_01_CHI_CAR | Jalen Coker | receptions | 2.2 | 0–6 | 8 | 4.05 | 0.98 | 3.0 | 9 | 0.71 | 0.89 | EXPECTED_ACTIVE | True | 0.253 | OPPORTUNITY_MISS |
| 2026_01_CLE_JAX | Trevor Lawrence | passing_tds | 1.6 | 0–4 | 4 | 4.05 | 0.95 | 33.5 | 23 | 0.05 | 0.17 | EXPECTED_ACTIVE | True | 0.010 | EFFICIENCY_MISS |
| 2026_01_NO_DET | Travis Etienne Jr. | receptions | 1.3 | 0–5 | 7 | 4.05 | 0.98 | 1.9 | 9 | 0.71 | 0.78 | EXPECTED_ACTIVE | True | 0.363 | OPPORTUNITY_MISS |
| 2026_01_NYJ_TEN | Kenyon Sadiq | receptions | 0.7 | 0–5 | 3 | 4.05 | 0.85 | 1.1 | 3 | 0.67 | 1.00 | EXPECTED_ACTIVE | True | 0.292 | OPPORTUNITY_MISS |
| 2026_01_TB_CIN | Samaje Perine | receiving_yards | 7.3 | 0–32 | 30 | 4.05 | 0.93 | 1.5 | 3 | 4.95 | 10.00 | EXPECTED_ACTIVE | True | 0.055 | EFFICIENCY_MISS |
| 2026_01_TB_CIN | Bucky Irving | receptions | 1.4 | 0–5 | 7 | 4.05 | 0.98 | 1.9 | 7 | 0.76 | 1.00 | EXPECTED_ACTIVE | True | 0.142 | OPPORTUNITY_MISS |
| 2026_02_DET_BUF | Jared Goff | passing_tds | 1.6 | 0–4 | 4 | 4.05 | 0.95 | 34.9 | 38 | 0.05 | 0.11 | EXPECTED_ACTIVE | True | 0.060 | EFFICIENCY_MISS |
| 2026_01_SF_LA | Kaelon Black | rushing_yards | 14.1 | 0–56 | 65 | 3.98 | 0.96 | 3.9 | 14 | 3.61 | 4.64 | EXPECTED_ACTIVE | True | 0.028 | OPPORTUNITY_MISS |
| 2026_01_CHI_CAR | Chuba Hubbard | receiving_yards | 9.7 | 0–42 | 38 | 3.94 | 0.92 | 1.7 | 3 | 5.75 | 12.67 | EXPECTED_ACTIVE | True | 0.118 | EFFICIENCY_MISS |
| 2026_01_CHI_CAR | Jalen Coker | receiving_yards | 33.3 | 0–92 | 138 | 3.94 | 0.99 | 3.0 | 9 | 10.95 | 15.33 | EXPECTED_ACTIVE | True | 0.226 | OPPORTUNITY_MISS |
| 2026_01_WAS_PHI | Antonio Williams | touchdowns | 0.1 | -–- | 1 | 3.90 | - | 4.5 | 4 | - | - | EXPECTED_ACTIVE | True | -0.000 | UNEXPLAINED_VARIANCE |
| 2026_01_GB_MIN | Christian Watson | receiving_yards | 42.6 | 3–99 | 147 | 3.83 | 0.99 | 3.6 | 8 | 11.72 | 18.38 | EXPECTED_ACTIVE | True | 0.154 | OPPORTUNITY_MISS |
| 2026_01_GB_MIN | Matthew Golden | receiving_yards | 23.7 | 0–66 | 95 | 3.76 | 0.99 | 2.4 | 12 | 9.79 | 7.92 | EXPECTED_ACTIVE | True | 0.220 | OPPORTUNITY_MISS |
| 2026_01_NO_DET | Jahmyr Gibbs | carries | 10.5 | 3–21 | 29 | 3.66 | 0.99 | 10.5 | 29 | - | - | EXPECTED_ACTIVE | True | 0.529 | OPPORTUNITY_MISS |
| 2026_01_DEN_KC | Kenneth Walker III | rushing_yards | 49.8 | 4–127 | 173 | 3.63 | 0.98 | 9.3 | 23 | 5.35 | 7.52 | EXPECTED_ACTIVE | True | 0.232 | OPPORTUNITY_MISS |
| 2026_01_NO_DET | Jahmyr Gibbs | rushing_yards | 55.9 | 13–113 | 156 | 3.45 | 0.99 | 10.5 | 29 | 5.32 | 5.38 | EXPECTED_ACTIVE | True | 0.308 | OPPORTUNITY_MISS |
| 2026_01_GB_MIN | Matthew Golden | receptions | 1.5 | 0–5 | 6 | 3.37 | 0.96 | 2.4 | 12 | 0.62 | 0.50 | EXPECTED_ACTIVE | True | 0.394 | OPPORTUNITY_MISS |
| 2026_01_NO_DET | Devaughn Vele | receptions | 1.9 | 0–5 | 7 | 3.37 | 0.99 | 2.9 | 9 | 0.65 | 0.78 | EXPECTED_ACTIVE | True | 0.304 | OPPORTUNITY_MISS |
| 2026_01_CLE_JAX | Josh Cameron | touchdowns | 0.1 | -–- | 1 | 3.35 | - | 4.5 | 2 | - | - | EXPECTED_ACTIVE | True | -0.022 | OPPORTUNITY_MISS |
| 2026_01_CHI_CAR | Kalif Raymond | receiving_yards | 23.3 | 0–65 | 84 | 3.35 | 0.97 | 2.1 | 9 | 11.07 | 9.33 | EXPECTED_ACTIVE | True | -0.053 | OPPORTUNITY_MISS |
| 2026_01_NO_DET | Noah Fant | touchdowns | 0.1 | -–- | 1 | 3.32 | - | 2.5 | 8 | - | - | EXPECTED_ACTIVE | True | 0.014 | OPPORTUNITY_MISS |
| 2026_01_MIA_LV | Jack Bech | touchdowns | 0.1 | -–- | 1 | 3.30 | - | 3.2 | 4 | - | - | EXPECTED_ACTIVE | True | 0.032 | UNEXPLAINED_VARIANCE |
| 2026_01_GB_MIN | Kyler Murray | attempts | 33.9 | 20–48 | 5 | -3.26 | 0.01 | 33.9 | 5 | - | - | EXPECTED_ACTIVE | True | 0.155 | OPPORTUNITY_MISS |
| 2026_01_DAL_NYG | Javonte Williams | receiving_yards | 9.4 | 0–41 | 31 | 3.22 | 0.88 | 1.8 | 5 | 5.25 | 6.20 | EXPECTED_ACTIVE | True | 0.201 | OPPORTUNITY_MISS |
| 2026_01_TB_CIN | Mike Gesicki | receiving_yards | 21.2 | 0–72 | 78 | 3.16 | 0.96 | 2.1 | 7 | 10.22 | 11.14 | EXPECTED_ACTIVE | True | 0.173 | OPPORTUNITY_MISS |
| 2026_02_DET_BUF | Dalton Kincaid | receiving_yards | 27.3 | 0–76 | 95 | 3.16 | 0.97 | 2.2 | 8 | 12.60 | 11.88 | EXPECTED_ACTIVE | True | 0.368 | OPPORTUNITY_MISS |
| 2026_01_ARI_LAC | Kendrick Bourne | receptions | 1.5 | 0–5 | 8 | 3.15 | 0.99 | 2.3 | 8 | 0.64 | 1.00 | EXPECTED_ACTIVE | True | 0.174 | OPPORTUNITY_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 174, 'UNEXPLAINED_VARIANCE': 38, 'OPPORTUNITY_MISS': 404, 'TEAM_VOLUME_MISS': 4, 'NO_LARGE_MISS': 400, 'INSUFFICIENT_DATA': 18, 'AVAILABILITY_MISS': 17}.
Missing usage (no snap table or stats row): 35.

## Decision funnel (BET / WATCH / PASS accounting of the existing gates; no authority)

46 snapshot(s). A contract's terminal state is where it left the existing gate sequence when the model's own contract value stands in for a handicap. BET here means every mechanical gate the preflight applies would pass; it is still not a recommendation (that needs a human handicap and the signed preflight).

### Newest snapshot 20260920T000850Z (33420 markets)

| stage | markets |
|---|---|
| discovered | 33420 |
| mapped | 25456 |
| supported | 5749 |
| priced | 5749 |
| raw_disagreement | 4422 |
| tradable_book | 4310 |
| data_quality | 4308 |
| executable_price | 3225 |
| liquidity | 1401 |

Terminal states: {'PASS': 30937, 'WATCH': 1082, 'BET': 1401}

| family | BET | WATCH | PASS |
|---|---|---|---|
| AWARD | 0 | 0 | 865 |
| BOTH_TEAMS_SCORE | 0 | 0 | 128 |
| BOTH_TEAMS_SCORE_N | 0 | 5 | 123 |
| COACH_EVENT | 0 | 0 | 64 |
| CONFERENCE_WINNER | 0 | 0 | 32 |
| DIVISION_WINNER | 0 | 0 | 32 |
| DRAFT | 0 | 0 | 40 |
| FIRST_TD_SCORER | 0 | 0 | 792 |
| FIRST_TD_TEAM | 0 | 0 | 934 |
| GAME_EVENT | 0 | 0 | 131 |
| GAME_STAT | 0 | 0 | 5 |
| GAME_WINNER | 0 | 24 | 72 |
| HALF_FULL_RESULT | 0 | 0 | 288 |
| MAKE_PLAYOFFS | 0 | 0 | 33 |
| NFL_BUSINESS_EVENT | 0 | 0 | 5 |
| NOT_NFL_OR_UNKNOWN | 0 | 0 | 2 |
| PERIOD_WINNER | 0 | 0 | 576 |
| PLAYER_AVAILABILITY | 0 | 0 | 23 |
| PLAYER_ROLE_EVENT | 0 | 0 | 177 |
| PLAYER_STAT | 1298 | 584 | 10327 |
| RACE_TO_N | 0 | 0 | 525 |
| SEASON_DIVISION_ORDER | 0 | 0 | 192 |
| SEASON_DIVISION_STAT | 0 | 0 | 80 |
| SEASON_FANTASY | 0 | 0 | 938 |
| SEASON_LEADER | 0 | 0 | 785 |
| SEASON_MATCHUP | 0 | 0 | 496 |
| SEASON_PLAYER_SPECIAL | 0 | 0 | 306 |
| SEASON_PLAYER_STAT | 0 | 0 | 1129 |
| SEASON_SEED | 0 | 0 | 224 |
| SEASON_SPECIAL | 0 | 0 | 63 |
| SEASON_TEAM_EVENT | 0 | 0 | 390 |
| SEASON_TEAM_H2H | 0 | 0 | 22 |
| SEASON_TEAM_LEADER | 0 | 0 | 96 |
| SEASON_WINS | 0 | 0 | 547 |
| SPREAD | 47 | 215 | 3120 |
| SUPER_BOWL_EVENT | 0 | 0 | 234 |
| SUPER_BOWL_WINNER | 0 | 0 | 32 |
| TEAM_STAT | 0 | 0 | 920 |
| TEAM_TOTAL | 36 | 90 | 1475 |
| TEAM_WINS_BY_WEEK | 0 | 0 | 728 |
| TOTAL | 20 | 164 | 2623 |
| TOTAL_TD | 0 | 0 | 206 |
| TRANSACTION_EVENT | 0 | 0 | 277 |
| UNKNOWN_NEEDS_CLASSIFICATION | 0 | 0 | 386 |
| WEEK_EVENT | 0 | 0 | 32 |
| WEEK_LEADER | 0 | 0 | 238 |
| WIN_MARGIN_BUCKET | 0 | 0 | 224 |

| rejection reason | n |
|---|---|
| POST_KICKOFF_EXCLUDED | 12784 |
| unmapped | 7964 |
| UNSUPPORTED_MODEL | 4948 |
| UNSUPPORTED_RULES | 1851 |
| no order book observed for this ticker (books are captured i | 1822 |
| no positive disagreement against either executable ask | 1327 |
| ask 0.99 above the zero-net-EV ceiling 0.98 | 178 |
| UNSUPPORTED_IDENTITY | 124 |
| book not tradable for ranking | 112 |
| ask 0.98 above the zero-net-EV ceiling 0.97 | 47 |
| ask 0.97 above the zero-net-EV ceiling 0.96 | 32 |
| ask 0.96 above the zero-net-EV ceiling 0.95 | 20 |
| ask 0.06 above the zero-net-EV ceiling 0.05 | 19 |
| ask 0.08 above the zero-net-EV ceiling 0.07 | 18 |
| ask 0.95 above the zero-net-EV ceiling 0.94 | 17 |

WATCH rows carry the highest executable price at which one contract still has net EV > 0 under the committed fee schedule (`watch_ceiling`). Not replayed: ['portfolio_risk_policy (needs a stake and bankroll)', "decision_time_quote_freshness (needs a decision timestamp; the snapshot's own confirmation is the STALE_DATA support state)"].

Across all 46 snapshots (repeated markets counted per snapshot): {'PASS': 1159790, 'WATCH': 33200, 'BET': 27274}.

