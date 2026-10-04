# Three-arm game-centre experiment — 2026 week 4

> **INSUFFICIENT EVIDENCE.** 2 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 141 | 2 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 1 | 1 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 2 | 2 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 2 | 2 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 2 | 2 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 2 | 2 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

Raw rows are repeated snapshots of the same games and are never a sample size. The primary unit is `latest_pregame` (one row per game); the canonical horizons are one row per game per horizon.

## Game centres, per game (latest pregame snapshot)

| game | kickoff | T-min | arm | margin | total | actual margin | actual total | mkt@snap margin/total | close margin/total |
|---|---|---|---|---|---|---|---|---|---|
| 2026_04_PIT_CLE | 2026-10-02T00:15 | 32 | CURRENT | -2.50 | 37.50 | 3 | 51 | -2.5/37.5 (kalshi_implied) | -2.5/37.5 (OK) |
|  |  |  | DATA_ONLY | -3.50 | 40.25 |  |  |  |  |
|  |  |  | HYBRID_30 | -2.80 | 38.32 |  |  |  |  |
| 2026_04_IND_WAS | 2026-10-04T13:30 | 38 | CURRENT | -4.50 | 46.50 | -17 | 43 | -4.5/46.5 (kalshi_implied) | -4.5/46.5 (OK) |
|  |  |  | DATA_ONLY | -2.33 | 47.43 |  |  |  |  |
|  |  |  | HYBRID_30 | -3.85 | 46.78 |  |  |  |  |

## Game-centre accuracy — latest_pregame (2 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | 0.239 |
| DATA_ONLY | 2 | 1 | 10.59 | 11.34 | 4.08 | 7.59 | 8.22 | -3.16 | 0.290 |
| HYBRID_30 | 2 | 1 | 9.48 | 10.16 | 3.67 | 8.23 | 9.35 | -4.45 | 0.237 |
| market at snapshot | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | - |
| market at close | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2 | total | -0.273 | 0.552 | [-1.354, 0.809] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2 | margin | -1.110 | 0.407 | [-1.907, -0.313] | 1.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2 | total | 0.637 | 1.288 | [-1.887, 3.160] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 2 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2 | total | -0.273 | 0.552 | [-1.354, 0.809] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 2 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 2 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 2 | total | -0.273 | 0.552 | [-1.354, 0.809] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 2 | 0 | 0 | 2 | 0 | - | 0.000 | 1.59 |
| DATA_ONLY | total | 2 | 0 | 0 | 2 | 0 | - | 0.500 | 1.84 |
| HYBRID_30 | margin | 2 | 0 | 0 | 2 | 0 | - | 0.000 | 0.48 |
| HYBRID_30 | total | 2 | 0 | 0 | 2 | 0 | - | 0.500 | 0.55 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 1 | 6.50 | 5.50 | - |
| DATA_ONLY | margin | 2-3 | 1 | 14.67 | 12.50 | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 4.43 | 3.50 | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 1 | 10.75 | 13.50 | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 2 | 9.48 | 9.00 | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 2 | 8.23 | 8.50 | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 2}; DATA_ONLY quality states: {'OK': 2}; close centre status: {'OK': 2}.

## Game-centre accuracy — T-24h (1 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1 | 1 | 12.50 | 12.50 | 12.50 | 4.50 | 4.50 | 4.50 | 0.116 |
| DATA_ONLY | 1 | 1 | 14.67 | 14.67 | 14.67 | 4.43 | 4.43 | 4.43 | 0.160 |
| HYBRID_30 | 1 | 1 | 13.15 | 13.15 | 13.15 | 4.48 | 4.48 | 4.48 | 0.140 |
| market at snapshot | 1 | 1 | 12.50 | 12.50 | 12.50 | 4.50 | 4.50 | 4.50 | - |
| market at close | 1 | 1 | 12.50 | 12.50 | 12.50 | 3.50 | 3.50 | 3.50 | - |

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
| DATA_ONLY | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 2.17 |
| DATA_ONLY | total | 1 | 1 | 0 | 0 | 0 | 1.000 | 1.000 | 0.07 |
| HYBRID_30 | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 0.65 |
| HYBRID_30 | total | 1 | 1 | 0 | 0 | 0 | 1.000 | 1.000 | 0.02 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 0 | - | - | - |
| DATA_ONLY | margin | 2-3 | 1 | 14.67 | 12.50 | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 4.43 | 4.50 | 1.000 |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 0 | - | - | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 1 | 13.15 | 12.50 | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 1 | 4.48 | 4.50 | 1.000 |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 1}; DATA_ONLY quality states: {'OK': 1}; close centre status: {'OK': 1}.

## Game-centre accuracy — T-6h (2 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | 0.237 |
| DATA_ONLY | 2 | 1 | 10.59 | 11.34 | 4.08 | 7.59 | 8.22 | -3.16 | 0.290 |
| HYBRID_30 | 2 | 1 | 9.48 | 10.16 | 3.67 | 8.23 | 9.35 | -4.45 | 0.237 |
| market at snapshot | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | - |
| market at close | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2 | total | -0.273 | 0.552 | [-1.354, 0.809] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2 | margin | -1.110 | 0.407 | [-1.907, -0.313] | 1.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2 | total | 0.637 | 1.288 | [-1.887, 3.160] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 2 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2 | total | -0.273 | 0.552 | [-1.354, 0.809] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 2 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 2 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 2 | total | -0.273 | 0.552 | [-1.354, 0.809] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 2 | 0 | 0 | 2 | 0 | - | 0.000 | 1.59 |
| DATA_ONLY | total | 2 | 0 | 0 | 2 | 0 | - | 0.500 | 1.84 |
| HYBRID_30 | margin | 2 | 0 | 0 | 2 | 0 | - | 0.000 | 0.48 |
| HYBRID_30 | total | 2 | 0 | 0 | 2 | 0 | - | 0.500 | 0.55 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 1 | 6.50 | 5.50 | - |
| DATA_ONLY | margin | 2-3 | 1 | 14.67 | 12.50 | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 4.43 | 3.50 | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 1 | 10.75 | 13.50 | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 2 | 9.48 | 9.00 | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 2 | 8.23 | 8.50 | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 2}; DATA_ONLY quality states: {'OK': 2}; close centre status: {'OK': 2}.

## Game-centre accuracy — T-90m (2 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.00 | 9.18 | -4.50 | 0.241 |
| DATA_ONLY | 2 | 1 | 10.59 | 11.34 | 4.08 | 7.59 | 8.22 | -3.16 | 0.289 |
| HYBRID_30 | 2 | 1 | 9.48 | 10.16 | 3.67 | 7.88 | 8.88 | -4.10 | 0.250 |
| market at snapshot | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.00 | 9.18 | -4.50 | - |
| market at close | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 2 | total | -0.410 | 1.339 | [-3.035, 2.216] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2 | total | -0.123 | 0.402 | [-0.910, 0.665] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2 | margin | -1.110 | 0.407 | [-1.907, -0.313] | 1.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2 | total | 0.287 | 0.938 | [-1.551, 2.124] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 2 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2 | total | -0.410 | 1.339 | [-3.035, 2.216] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2 | total | -0.123 | 0.402 | [-0.910, 0.665] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 2 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 2 | total | -0.500 | 0.500 | [-1.480, 0.480] | 0.500 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 2 | total | -0.623 | 0.902 | [-2.390, 1.145] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 2 | 0 | 0 | 2 | 0 | - | 0.000 | 1.59 |
| DATA_ONLY | total | 2 | 0 | 1 | 1 | 0 | 0.000 | 0.500 | 1.34 |
| HYBRID_30 | margin | 2 | 0 | 0 | 2 | 0 | - | 0.000 | 0.48 |
| HYBRID_30 | total | 2 | 0 | 1 | 1 | 0 | 0.000 | 0.500 | 0.40 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 1 | 6.50 | 5.50 | - |
| DATA_ONLY | margin | 2-3 | 1 | 14.67 | 12.50 | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 4.43 | 3.50 | - |
| DATA_ONLY | total | 1-2 | 1 | 10.75 | 12.50 | 0.000 |
| DATA_ONLY | total | 2-3 | 0 | - | - | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 2 | 9.48 | 9.00 | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 2 | 7.88 | 8.00 | 0.000 |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 2}; DATA_ONLY quality states: {'OK': 2}; close centre status: {'OK': 2}.

## Game-centre accuracy — T-30m (2 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | 0.239 |
| DATA_ONLY | 2 | 1 | 10.59 | 11.34 | 4.08 | 7.59 | 8.22 | -3.16 | 0.290 |
| HYBRID_30 | 2 | 1 | 9.48 | 10.16 | 3.67 | 8.23 | 9.35 | -4.45 | 0.237 |
| market at snapshot | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | - |
| market at close | 2 | 1 | 9.00 | 9.66 | 3.50 | 8.50 | 9.86 | -5.00 | - |

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 2 | total | -0.273 | 0.552 | [-1.354, 0.809] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2 | margin | -1.110 | 0.407 | [-1.907, -0.313] | 1.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 2 | total | 0.637 | 1.288 | [-1.887, 3.160] | 0.500 | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 2 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 2 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 2 | total | -0.273 | 0.552 | [-1.354, 0.809] | 0.500 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 2 | margin | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 2 | total | 0.000 | 0.000 | [0.000, 0.000] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 2 | margin | 1.585 | 0.581 | [0.447, 2.724] | 0.000 | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 2 | total | -0.910 | 1.839 | [-4.515, 2.696] | 0.500 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 2 | margin | 0.476 | 0.174 | [0.134, 0.817] | 0.000 | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 2 | total | -0.273 | 0.552 | [-1.354, 0.809] | 0.500 | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 2 | 0 | 0 | 2 | 0 | - | 0.000 | 1.59 |
| DATA_ONLY | total | 2 | 0 | 0 | 2 | 0 | - | 0.500 | 1.84 |
| HYBRID_30 | margin | 2 | 0 | 0 | 2 | 0 | - | 0.000 | 0.48 |
| HYBRID_30 | total | 2 | 0 | 0 | 2 | 0 | - | 0.500 | 0.55 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 1 | 6.50 | 5.50 | - |
| DATA_ONLY | margin | 2-3 | 1 | 14.67 | 12.50 | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 4.43 | 3.50 | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 1 | 10.75 | 13.50 | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 2 | 9.48 | 9.00 | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 2 | 8.23 | 8.50 | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 2}; DATA_ONLY quality states: {'OK': 2}; close centre status: {'OK': 2}.

## Contract pricing — latest_pregame (154 contracts, 2 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 154 | 0.1468 | 0.4386 | 0.404 | 0.448 | 154 | 0.1468 | 0.1444 | 0.1460 |
| DATA_ONLY | 154 | 0.1537 | 0.4555 | 0.424 | 0.448 | 154 | 0.1537 | 0.1444 | 0.1460 |
| HYBRID_30 | 154 | 0.1466 | 0.4414 | 0.406 | 0.448 | 154 | 0.1466 | 0.1444 | 0.1460 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 154 | 2 | 0.00692 | [-0.01137, 0.02569] | 0.00692 | [-0.01137, 0.02569] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 154 | 2 | -0.00020 | [-0.00392, 0.00362] | -0.00020 | [-0.00392, 0.00362] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 154 | 2 | -0.00712 | [-0.02207, 0.00745] | -0.00712 | [-0.02207, 0.00745] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 154 | 2 | - | - | 0.00240 | [0.00162, 0.00321] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 153 | 2 | - | - | 0.00175 | [0.00072, 0.00282] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 154 | 2 | - | - | 0.00932 | [-0.00975, 0.02890] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 153 | 2 | - | - | 0.00871 | [-0.01065, 0.02885] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 154 | 2 | - | - | 0.00220 | [-0.00230, 0.00683] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 153 | 2 | - | - | 0.00155 | [-0.00320, 0.00649] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 8, 'GAME_WINNER': 4, 'SPREAD': 50, 'TEAM_TOTAL': 54, 'TOTAL': 38}; settlement: {'SETTLED': 154}; close: {'OK': 153, 'OK_STALE': 1}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 23 / 0.052 / 0.000 | 22 / 0.057 / 0.000 | 23 / 0.051 / 0.000 |
| 0.10-0.20 | 25 / 0.145 / 0.080 | 24 / 0.149 / 0.125 | 24 / 0.148 / 0.167 |
| 0.20-0.30 | 19 / 0.244 / 0.316 | 20 / 0.252 / 0.300 | 20 / 0.250 / 0.250 |
| 0.30-0.40 | 19 / 0.354 / 0.526 | 14 / 0.350 / 0.571 | 16 / 0.349 / 0.375 |
| 0.40-0.50 | 14 / 0.449 / 0.643 | 14 / 0.442 / 0.429 | 17 / 0.445 / 0.529 |
| 0.50-0.60 | 17 / 0.541 / 0.529 | 19 / 0.553 / 0.632 | 17 / 0.544 / 0.647 |
| 0.60-0.70 | 9 / 0.649 / 0.778 | 9 / 0.637 / 0.556 | 10 / 0.650 / 0.900 |
| 0.70-0.80 | 7 / 0.762 / 0.714 | 6 / 0.730 / 0.667 | 6 / 0.775 / 0.667 |
| 0.80-0.90 | 7 / 0.859 / 1.000 | 10 / 0.845 / 0.900 | 7 / 0.856 / 1.000 |
| 0.90-1.00 | 14 / 0.952 / 1.000 | 16 / 0.957 / 1.000 | 14 / 0.951 / 1.000 |

## Contract pricing — T-24h (76 contracts, 1 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 76 | 0.1490 | 0.4446 | 0.440 | 0.408 | 76 | 0.1490 | 0.1471 | 0.1432 |
| DATA_ONLY | 76 | 0.1699 | 0.4961 | 0.437 | 0.408 | 76 | 0.1699 | 0.1471 | 0.1432 |
| HYBRID_30 | 76 | 0.1562 | 0.4628 | 0.441 | 0.408 | 76 | 0.1562 | 0.1471 | 0.1432 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 76 | 1 | 0.02082 | - | 0.02082 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 76 | 1 | 0.00712 | - | 0.00712 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 76 | 1 | -0.01370 | - | -0.01370 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 76 | 1 | - | - | 0.00193 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 75 | 1 | - | - | 0.00777 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 76 | 1 | - | - | 0.02275 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 75 | 1 | - | - | 0.02887 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 76 | 1 | - | - | 0.00905 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 75 | 1 | - | - | 0.01498 | - | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 4, 'GAME_WINNER': 2, 'SPREAD': 25, 'TEAM_TOTAL': 26, 'TOTAL': 19}; settlement: {'SETTLED': 76}; close: {'OK': 75, 'OK_STALE': 1}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 9 / 0.059 / 0.000 | 10 / 0.067 / 0.000 | 8 / 0.059 / 0.000 |
| 0.10-0.20 | 13 / 0.145 / 0.077 | 12 / 0.151 / 0.250 | 12 / 0.142 / 0.083 |
| 0.20-0.30 | 9 / 0.243 / 0.222 | 9 / 0.253 / 0.222 | 10 / 0.248 / 0.300 |
| 0.30-0.40 | 8 / 0.348 / 0.500 | 8 / 0.350 / 0.500 | 8 / 0.348 / 0.375 |
| 0.40-0.50 | 6 / 0.448 / 0.500 | 7 / 0.433 / 0.286 | 7 / 0.441 / 0.429 |
| 0.50-0.60 | 8 / 0.546 / 0.375 | 9 / 0.550 / 0.444 | 9 / 0.564 / 0.444 |
| 0.60-0.70 | 6 / 0.650 / 0.500 | 3 / 0.631 / 0.333 | 5 / 0.642 / 0.400 |
| 0.70-0.80 | 5 / 0.768 / 0.600 | 5 / 0.744 / 0.600 | 5 / 0.738 / 0.600 |
| 0.80-0.90 | 2 / 0.853 / 1.000 | 4 / 0.849 / 0.750 | 5 / 0.863 / 1.000 |
| 0.90-1.00 | 10 / 0.953 / 1.000 | 9 / 0.959 / 1.000 | 7 / 0.961 / 1.000 |

## Contract pricing — T-6h (154 contracts, 2 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 154 | 0.1456 | 0.4359 | 0.404 | 0.448 | 154 | 0.1456 | 0.1446 | 0.1460 |
| DATA_ONLY | 154 | 0.1538 | 0.4558 | 0.423 | 0.448 | 154 | 0.1538 | 0.1446 | 0.1460 |
| HYBRID_30 | 154 | 0.1460 | 0.4402 | 0.407 | 0.448 | 154 | 0.1460 | 0.1446 | 0.1460 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 154 | 2 | 0.00822 | [-0.00891, 0.02579] | 0.00822 | [-0.00891, 0.02579] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 154 | 2 | 0.00040 | [-0.00261, 0.00350] | 0.00040 | [-0.00261, 0.00350] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 154 | 2 | -0.00781 | [-0.02229, 0.00630] | -0.00781 | [-0.02229, 0.00630] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 154 | 2 | - | - | 0.00096 | [0.00044, 0.00149] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 153 | 2 | - | - | 0.00055 | [-0.00119, 0.00235] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 154 | 2 | - | - | 0.00917 | [-0.00847, 0.02728] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 153 | 2 | - | - | 0.00882 | [-0.01009, 0.02849] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 154 | 2 | - | - | 0.00136 | [-0.00217, 0.00499] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 153 | 2 | - | - | 0.00096 | [-0.00380, 0.00590] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 8, 'GAME_WINNER': 4, 'SPREAD': 50, 'TEAM_TOTAL': 54, 'TOTAL': 38}; settlement: {'SETTLED': 154}; close: {'OK': 153, 'OK_STALE': 1}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 23 / 0.052 / 0.000 | 22 / 0.056 / 0.000 | 23 / 0.052 / 0.000 |
| 0.10-0.20 | 25 / 0.145 / 0.080 | 25 / 0.150 / 0.120 | 24 / 0.149 / 0.167 |
| 0.20-0.30 | 18 / 0.242 / 0.333 | 20 / 0.256 / 0.300 | 20 / 0.250 / 0.250 |
| 0.30-0.40 | 19 / 0.349 / 0.474 | 14 / 0.357 / 0.643 | 16 / 0.347 / 0.375 |
| 0.40-0.50 | 16 / 0.449 / 0.625 | 13 / 0.442 / 0.385 | 17 / 0.446 / 0.529 |
| 0.50-0.60 | 17 / 0.547 / 0.529 | 19 / 0.551 / 0.632 | 17 / 0.546 / 0.647 |
| 0.60-0.70 | 8 / 0.655 / 0.875 | 10 / 0.642 / 0.600 | 10 / 0.651 / 0.900 |
| 0.70-0.80 | 6 / 0.755 / 0.667 | 6 / 0.744 / 0.667 | 6 / 0.775 / 0.667 |
| 0.80-0.90 | 8 / 0.852 / 1.000 | 9 / 0.848 / 0.889 | 6 / 0.850 / 1.000 |
| 0.90-1.00 | 14 / 0.951 / 1.000 | 16 / 0.956 / 1.000 | 15 / 0.948 / 1.000 |

## Contract pricing — T-90m (154 contracts, 2 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 154 | 0.1428 | 0.4295 | 0.409 | 0.448 | 154 | 0.1428 | 0.1447 | 0.1460 |
| DATA_ONLY | 154 | 0.1537 | 0.4553 | 0.423 | 0.448 | 154 | 0.1537 | 0.1447 | 0.1460 |
| HYBRID_30 | 154 | 0.1492 | 0.4442 | 0.403 | 0.448 | 154 | 0.1492 | 0.1447 | 0.1460 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 154 | 2 | 0.01091 | [-0.00360, 0.02581] | 0.01091 | [-0.00360, 0.02581] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 154 | 2 | 0.00647 | [0.00435, 0.00853] | 0.00647 | [0.00435, 0.00853] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 154 | 2 | -0.00445 | [-0.02146, 0.01213] | -0.00445 | [-0.02146, 0.01213] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 154 | 2 | - | - | -0.00191 | [-0.00591, 0.00221] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 153 | 2 | - | - | -0.00230 | [-0.00676, 0.00235] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 154 | 2 | - | - | 0.00901 | [-0.00951, 0.02802] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 153 | 2 | - | - | 0.00869 | [-0.01036, 0.02849] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 154 | 2 | - | - | 0.00456 | [0.00261, 0.00656] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 153 | 2 | - | - | 0.00421 | [0.00177, 0.00675] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 8, 'GAME_WINNER': 4, 'SPREAD': 50, 'TEAM_TOTAL': 54, 'TOTAL': 38}; settlement: {'SETTLED': 154}; close: {'OK': 153, 'OK_STALE': 1}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 23 / 0.054 / 0.000 | 23 / 0.058 / 0.000 | 24 / 0.050 / 0.000 |
| 0.10-0.20 | 24 / 0.145 / 0.042 | 24 / 0.151 / 0.125 | 26 / 0.150 / 0.154 |
| 0.20-0.30 | 19 / 0.242 / 0.316 | 19 / 0.253 / 0.316 | 18 / 0.250 / 0.278 |
| 0.30-0.40 | 19 / 0.354 / 0.526 | 15 / 0.353 / 0.600 | 18 / 0.348 / 0.500 |
| 0.40-0.50 | 13 / 0.449 / 0.538 | 13 / 0.443 / 0.385 | 19 / 0.460 / 0.579 |
| 0.50-0.60 | 19 / 0.546 / 0.632 | 19 / 0.552 / 0.632 | 12 / 0.549 / 0.583 |
| 0.60-0.70 | 9 / 0.657 / 0.778 | 9 / 0.636 / 0.556 | 10 / 0.654 / 0.800 |
| 0.70-0.80 | 6 / 0.763 / 0.667 | 7 / 0.738 / 0.714 | 4 / 0.775 / 0.750 |
| 0.80-0.90 | 8 / 0.859 / 1.000 | 9 / 0.849 / 0.889 | 8 / 0.856 / 0.875 |
| 0.90-1.00 | 14 / 0.953 / 1.000 | 16 / 0.956 / 1.000 | 15 / 0.959 / 1.000 |

## Contract pricing — T-30m (154 contracts, 2 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 154 | 0.1468 | 0.4386 | 0.404 | 0.448 | 154 | 0.1468 | 0.1444 | 0.1460 |
| DATA_ONLY | 154 | 0.1537 | 0.4555 | 0.424 | 0.448 | 154 | 0.1537 | 0.1444 | 0.1460 |
| HYBRID_30 | 154 | 0.1466 | 0.4414 | 0.406 | 0.448 | 154 | 0.1466 | 0.1444 | 0.1460 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 154 | 2 | 0.00692 | [-0.01137, 0.02569] | 0.00692 | [-0.01137, 0.02569] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 154 | 2 | -0.00020 | [-0.00392, 0.00362] | -0.00020 | [-0.00392, 0.00362] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 154 | 2 | -0.00712 | [-0.02207, 0.00745] | -0.00712 | [-0.02207, 0.00745] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 154 | 2 | - | - | 0.00240 | [0.00162, 0.00321] | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 153 | 2 | - | - | 0.00175 | [0.00072, 0.00282] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 154 | 2 | - | - | 0.00932 | [-0.00975, 0.02890] | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 153 | 2 | - | - | 0.00871 | [-0.01065, 0.02885] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 154 | 2 | - | - | 0.00220 | [-0.00230, 0.00683] | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 153 | 2 | - | - | 0.00155 | [-0.00320, 0.00649] | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 8, 'GAME_WINNER': 4, 'SPREAD': 50, 'TEAM_TOTAL': 54, 'TOTAL': 38}; settlement: {'SETTLED': 154}; close: {'OK': 153, 'OK_STALE': 1}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 23 / 0.052 / 0.000 | 22 / 0.057 / 0.000 | 23 / 0.051 / 0.000 |
| 0.10-0.20 | 25 / 0.145 / 0.080 | 24 / 0.149 / 0.125 | 24 / 0.148 / 0.167 |
| 0.20-0.30 | 19 / 0.244 / 0.316 | 20 / 0.252 / 0.300 | 20 / 0.250 / 0.250 |
| 0.30-0.40 | 19 / 0.354 / 0.526 | 14 / 0.350 / 0.571 | 16 / 0.349 / 0.375 |
| 0.40-0.50 | 14 / 0.449 / 0.643 | 14 / 0.442 / 0.429 | 17 / 0.445 / 0.529 |
| 0.50-0.60 | 17 / 0.541 / 0.529 | 19 / 0.553 / 0.632 | 17 / 0.544 / 0.647 |
| 0.60-0.70 | 9 / 0.649 / 0.778 | 9 / 0.637 / 0.556 | 10 / 0.650 / 0.900 |
| 0.70-0.80 | 7 / 0.762 / 0.714 | 6 / 0.730 / 0.667 | 6 / 0.775 / 0.667 |
| 0.80-0.90 | 7 / 0.859 / 1.000 | 10 / 0.845 / 0.900 | 7 / 0.856 / 1.000 |
| 0.90-1.00 | 14 / 0.952 / 1.000 | 16 / 0.957 / 1.000 | 14 / 0.951 / 1.000 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 1 | 0 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-24h | DATA_ONLY | total | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-24h | HYBRID_30 (derived) | margin | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-24h | HYBRID_30 (derived) | total | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-6h | DATA_ONLY | margin | 2 | 0 | 0 | 0 | 2 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-6h | DATA_ONLY | total | 2 | 1 | 0 | 0 | 1 | 0 | - - | 1.000 | 1.000 | 0.00 |
| T-6h | HYBRID_30 (derived) | margin | 2 | 2 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-6h | HYBRID_30 (derived) | total | 2 | 2 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-90m | DATA_ONLY | margin | 2 | 0 | 0 | 0 | 2 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-90m | DATA_ONLY | total | 2 | 1 | 0 | 1 | 0 | 0 | 0.000 [0.000, 0.793] | 1.000 | 1.000 | -1.00 |
| T-90m | HYBRID_30 (derived) | margin | 2 | 2 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-90m | HYBRID_30 (derived) | total | 2 | 2 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-30m | DATA_ONLY | margin | 2 | 0 | 0 | 0 | 2 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-30m | DATA_ONLY | total | 2 | 1 | 0 | 0 | 1 | 0 | - - | 1.000 | 1.000 | 0.00 |
| T-30m | HYBRID_30 (derived) | margin | 2 | 2 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-30m | HYBRID_30 (derived) | total | 2 | 2 | 0 | 0 | 0 | 0 | - - | - | - | - |
| latest_pregame | DATA_ONLY | margin | 2 | 0 | 0 | 0 | 2 | 0 | - - | 0.000 | 0.000 | 0.00 |
| latest_pregame | DATA_ONLY | total | 2 | 1 | 0 | 0 | 1 | 0 | - - | 1.000 | 1.000 | 0.00 |
| latest_pregame | HYBRID_30 (derived) | margin | 2 | 2 | 0 | 0 | 0 | 0 | - - | - | - | - |
| latest_pregame | HYBRID_30 (derived) | total | 2 | 2 | 0 | 0 | 0 | 0 | - - | - | - | - |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 0 | 0 | 0 | 0 | 0 | - |
| margin | 1-2 | 1 | 0 | 0 | 1 | 0 | - |
| margin | 2-3 | 1 | 0 | 0 | 1 | 0 | - |
| margin | 3-5 | 0 | 0 | 0 | 0 | 0 | - |
| margin | >5 | 0 | 0 | 0 | 0 | 0 | - |
| total | <=1 | 1 | 0 | 0 | 1 | 0 | - |
| total | 1-2 | 0 | 0 | 0 | 0 | 0 | - |
| total | 2-3 | 1 | 0 | 0 | 1 | 0 | - |
| total | 3-5 | 0 | 0 | 0 | 0 | 0 | - |
| total | >5 | 0 | 0 | 0 | 0 | 0 | - |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

63 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_04_PIT_CLE | Raheim Sanders | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.1 | 2 | 0.87 | 3.50 | EXPECTED_ACTIVE | True | -0.402 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | receiving_yards | 8.0 | 0–35 | 43 | 5.27 | 0.96 | 1.7 | 7 | 4.83 | 6.14 | EXPECTED_ACTIVE | True | 0.213 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Denzel Boston | receiving_yards | 19.9 | 0–67 | 89 | 3.95 | 0.97 | 1.9 | 7 | 10.55 | 12.71 | EXPECTED_ACTIVE | True | 0.386 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Roman Wilson | receiving_yards | 17.3 | 0–59 | 74 | 3.71 | 0.97 | 1.9 | 6 | 8.91 | 12.33 | EXPECTED_ACTIVE | True | 0.224 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Roman Wilson | touchdowns | 0.1 | -–- | 1 | 3.57 | - | 3.2 | 6 | - | - | EXPECTED_ACTIVE | True | 0.082 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | receiving_yards | 9.7 | 0–42 | 33 | 3.42 | 0.89 | 1.6 | 6 | 5.97 | 5.50 | EXPECTED_ACTIVE | True | 0.486 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Darnell Washington | touchdowns | 0.1 | -–- | 1 | 3.42 | - | 2.7 | 5 | - | - | EXPECTED_ACTIVE | True | 0.047 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | receptions | 1.2 | 0–5 | 6 | 3.37 | 0.96 | 1.7 | 7 | 0.72 | 0.86 | EXPECTED_ACTIVE | True | 0.278 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Deshaun Watson | carries | 2.3 | 0–18 | 7 | 3.15 | 0.80 | 2.3 | 7 | - | - | EXPECTED_ACTIVE | True | 0.611 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Pat Freiermuth | touchdowns | 0.1 | -–- | 1 | 3.01 | - | 3.1 | 5 | - | - | EXPECTED_ACTIVE | True | 0.097 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaleel McLaughlin | touchdowns | 0.1 | -–- | 1 | 2.88 | - | 8.1 | 1 | - | - | QUESTIONABLE | True | -0.048 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Raheim Sanders | receptions | 0.8 | 0–5 | 2 | 2.70 | 0.80 | 1.1 | 2 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | 0.376 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | DK Metcalf | receiving_yards | 42.3 | 3–98 | 115 | 2.66 | 0.97 | 4.2 | 9 | 9.98 | 12.78 | EXPECTED_ACTIVE | True | 0.108 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Harold Fannin Jr. | touchdowns | 0.2 | -–- | 1 | 2.14 | - | 4.9 | 5 | - | - | EXPECTED_ACTIVE | True | 0.059 | UNEXPLAINED_VARIANCE |
| 2026_04_PIT_CLE | Denzel Boston | receptions | 1.2 | 0–5 | 4 | 2.02 | 0.88 | 1.9 | 7 | 0.62 | 0.57 | EXPECTED_ACTIVE | True | 0.456 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | rushing_yards | 42.9 | 3–110 | 93 | 1.81 | 0.88 | 7.8 | 17 | 5.50 | 5.47 | EXPECTED_ACTIVE | True | 0.388 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | touchdowns | 0.2 | -–- | 1 | 1.79 | - | 13.9 | 24 | - | - | EXPECTED_ACTIVE | True | 0.161 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | carries | 9.7 | 3–20 | 17 | 1.54 | 0.86 | 9.7 | 17 | - | - | EXPECTED_ACTIVE | True | 0.469 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | carries | 7.8 | 1–19 | 17 | 1.52 | 0.89 | 7.8 | 17 | - | - | EXPECTED_ACTIVE | True | 0.607 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | interceptions | 0.8 | 0–3 | 2 | 1.35 | 0.85 | 33.5 | 40 | 0.02 | 0.05 | EXPECTED_ACTIVE | True | -0.063 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | passing_tds | 1.2 | 0–3 | 3 | 1.35 | 0.95 | 33.5 | 40 | 0.04 | 0.07 | EXPECTED_ACTIVE | True | 0.052 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Pat Freiermuth | receptions | 1.4 | 0–5 | 3 | 1.35 | 0.82 | 2.0 | 5 | 0.70 | 0.60 | EXPECTED_ACTIVE | True | 0.408 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | receptions | 1.3 | 0–5 | 3 | 1.35 | 0.82 | 1.6 | 6 | 0.77 | 0.50 | EXPECTED_ACTIVE | True | 0.497 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Darnell Washington | receptions | 1.2 | 0–5 | 3 | 1.35 | 0.82 | 1.8 | 5 | 0.70 | 0.60 | EXPECTED_ACTIVE | True | 0.231 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Roman Wilson | receptions | 1.2 | 0–5 | 3 | 1.35 | 0.82 | 1.9 | 6 | 0.61 | 0.50 | EXPECTED_ACTIVE | True | 0.291 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | DK Metcalf | receptions | 2.5 | 0–6 | 5 | 1.35 | 0.85 | 4.2 | 9 | 0.58 | 0.56 | EXPECTED_ACTIVE | True | 0.203 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Darnell Washington | receiving_yards | 15.0 | 0–51 | 27 | 1.28 | 0.79 | 1.8 | 5 | 8.42 | 5.40 | EXPECTED_ACTIVE | True | 0.217 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | passing_yards | 226.4 | 102–351 | 299 | 0.97 | 0.81 | 33.5 | 40 | 6.75 | 7.47 | EXPECTED_ACTIVE | True | -0.054 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | attempts | 33.5 | 19–48 | 40 | 0.74 | 0.77 | 33.5 | 40 | - | - | EXPECTED_ACTIVE | True | -0.003 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Deshaun Watson | passing_yards | 214.0 | 89–339 | 268 | 0.71 | 0.76 | 33.3 | 33 | 6.43 | 8.12 | EXPECTED_ACTIVE | True | -0.160 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Jerry Jeudy | receptions | 2.1 | 0–6 | 3 | 0.67 | 0.75 | 3.8 | 3 | 0.55 | 1.00 | EXPECTED_ACTIVE | True | -0.150 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Harold Fannin Jr. | receptions | 2.1 | 0–6 | 3 | 0.67 | 0.75 | 3.2 | 5 | 0.66 | 0.60 | EXPECTED_ACTIVE | True | 0.317 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Germie Bernard | receptions | 1.1 | 0–5 | 2 | 0.67 | 0.75 | 1.8 | 2 | 0.61 | 1.00 | EXPECTED_ACTIVE | True | 0.036 | EFFICIENCY_MISS |
| 2026_04_PIT_CLE | Quinshon Judkins | rushing_yards | 40.2 | 3–103 | 53 | 0.59 | 0.69 | 9.7 | 17 | 4.15 | 3.12 | EXPECTED_ACTIVE | True | 0.254 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Jaylen Warren | touchdowns | 0.2 | -–- | 0 | -0.56 | - | 12.5 | 23 | - | - | EXPECTED_ACTIVE | True | -0.250 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Deshaun Watson | completions | 20.9 | 11–31 | 24 | 0.51 | 0.69 | 33.3 | 33 | 0.63 | 0.73 | EXPECTED_ACTIVE | True | -0.135 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | DK Metcalf | touchdowns | 0.2 | -–- | 0 | -0.46 | - | 5.8 | 9 | - | - | EXPECTED_ACTIVE | True | -0.123 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Aaron Rodgers | rushing_yards | 9.1 | 0–32 | 0 | -0.45 | 0.05 | 2.5 | 0 | 3.59 | - | EXPECTED_ACTIVE | True | 0.100 | OPPORTUNITY_MISS |
| 2026_04_PIT_CLE | Michael Pittman Jr. | touchdowns | 0.2 | -–- | 0 | -0.42 | - | 5.3 | 4 | - | - | EXPECTED_ACTIVE | True | -0.045 | NO_LARGE_MISS |
| 2026_04_PIT_CLE | Pat Freiermuth | receiving_yards | 19.2 | 0–65 | 17 | 0.42 | 0.62 | 2.0 | 5 | 9.56 | 3.40 | EXPECTED_ACTIVE | True | 0.344 | EFFICIENCY_MISS |

Classification counts over every diagnosed projection: {'EFFICIENCY_MISS': 10, 'OPPORTUNITY_MISS': 38, 'UNEXPLAINED_VARIANCE': 1, 'NO_LARGE_MISS': 14}.
Missing usage (no snap table or stats row): 0.

## Decision funnel

No funnel accounting is available for this period.

## Player-autopsy coverage — 2026 week 4

Expected games 16 · eligible 16 · diagnosed 1 · excluded 15 · canonical projection units 63 (63 with a box-score value) · eligible units 1049, eligible but undiagnosed 986

| game | included | diagnosed units | raw records | eligible units | undiagnosed | rule | exclusion reason |
|---|---|---|---|---|---|---|---|
| 2026_04_ARI_NYG | NO | 0 | 0 | 62 | 62 | — | game not final (or no kickoff) when the report was built |
| 2026_04_ATL_NO | NO | 0 | 0 | 62 | 62 | — | game not final (or no kickoff) when the report was built |
| 2026_04_DAL_HOU | NO | 0 | 0 | 70 | 70 | — | game not final (or no kickoff) when the report was built |
| 2026_04_DEN_SF | NO | 0 | 0 | 68 | 68 | — | game not final (or no kickoff) when the report was built |
| 2026_04_DET_CAR | NO | 0 | 0 | 57 | 57 | — | game not final (or no kickoff) when the report was built |
| 2026_04_GB_TB | NO | 0 | 0 | 65 | 65 | — | game not final (or no kickoff) when the report was built |
| 2026_04_IND_WAS | NO | 0 | 0 | 70 | 70 | — | eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed) |
| 2026_04_JAX_CIN | NO | 0 | 0 | 73 | 73 | — | game not final (or no kickoff) when the report was built |
| 2026_04_KC_LV | NO | 0 | 0 | 66 | 66 | — | game not final (or no kickoff) when the report was built |
| 2026_04_LAC_SEA | NO | 0 | 0 | 72 | 72 | — | game not final (or no kickoff) when the report was built |
| 2026_04_LA_PHI | NO | 0 | 0 | 62 | 62 | — | game not final (or no kickoff) when the report was built |
| 2026_04_MIA_MIN | NO | 0 | 0 | 65 | 65 | — | game not final (or no kickoff) when the report was built |
| 2026_04_NE_BUF | NO | 0 | 0 | 69 | 69 | — | game not final (or no kickoff) when the report was built |
| 2026_04_NYJ_CHI | NO | 0 | 0 | 60 | 60 | — | game not final (or no kickoff) when the report was built |
| 2026_04_PIT_CLE | yes | 63 | 63 | 63 | 0 | autopsy-1.1.0 |  |
| 2026_04_TEN_BAL | NO | 0 | 0 | 65 | 65 | — | game not final (or no kickoff) when the report was built |

