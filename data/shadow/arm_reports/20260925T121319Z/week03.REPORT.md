# Three-arm game-centre experiment — 2026 week 3

> **INSUFFICIENT EVIDENCE.** 1 distinct game(s) with a scored latest-pregame three-arm record; the preregistered floor for any verdict is 64 games. Every number below is a description of a small, correlated sample. There is no winning model here and this report will never print one after one slate.

## Sample units (games)

| unit | rows | games | weeks | note |
|---|---|---|---|---|
| raw | 65 | 1 | 1 | every pregame snapshot; repeated, correlated; diagnostics only |
| T-24h | 0 | 0 | 0 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-6h | 1 | 1 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-90m | 0 | 0 | 0 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| T-30m | 1 | 1 | 1 | freshest snapshot at or before the horizon, within the tolerance; ties broken on (observed_at, prediction_id) |
| latest_pregame | 1 | 1 | 1 | one row per (game, ticker): the smallest positive minutes_to_kickoff, ties broken on (observed_at, prediction_id) |

Raw rows are repeated snapshots of the same games and are never a sample size. The primary unit is `latest_pregame` (one row per game); the canonical horizons are one row per game per horizon.

## Game centres, per game (latest pregame snapshot)

| game | kickoff | T-min | arm | margin | total | actual margin | actual total | mkt@snap margin/total | close margin/total |
|---|---|---|---|---|---|---|---|---|---|
| 2026_03_ATL_GB | 2026-09-25T00:15 | 30 | CURRENT | 5.50 | 42.00 | -21 | 49 | 5.5/42.0 (kalshi_implied) | 5.5/42.0 (OK) |
|  |  |  | DATA_ONLY | 7.14 | 42.90 |  |  |  |  |
|  |  |  | HYBRID_30 | 5.99 | 42.27 |  |  |  |  |

## Game-centre accuracy — latest_pregame (1 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1 | 1 | 26.50 | 26.50 | 26.50 | 7.00 | 7.00 | -7.00 | 0.486 |
| DATA_ONLY | 1 | 1 | 28.14 | 28.14 | 28.14 | 6.10 | 6.10 | -6.10 | 0.570 |
| HYBRID_30 | 1 | 1 | 26.99 | 26.99 | 26.99 | 6.73 | 6.73 | -6.73 | 0.482 |
| market at snapshot | 1 | 1 | 26.50 | 26.50 | 26.50 | 7.00 | 7.00 | -7.00 | - |
| market at close | 1 | 1 | 26.50 | 26.50 | 26.50 | 7.00 | 7.00 | -7.00 | - |

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
| DATA_ONLY | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 1.64 |
| DATA_ONLY | total | 1 | 0 | 0 | 1 | 0 | - | 1.000 | 0.90 |
| HYBRID_30 | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 0.49 |
| HYBRID_30 | total | 1 | 0 | 0 | 1 | 0 | - | 1.000 | 0.27 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 1 | 28.14 | 26.50 | - |
| DATA_ONLY | margin | 2-3 | 0 | - | - | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 6.10 | 7.00 | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 0 | - | - | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 1 | 26.99 | 26.50 | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 1 | 6.73 | 7.00 | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 1}; DATA_ONLY quality states: {'OK': 1}; close centre status: {'OK': 1}.

## Game-centre accuracy — T-24h (0 games, 0 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 0 | - | - | - | - | - | - | - | - |  (excluded/unavailable: 0)
| DATA_ONLY | 0 | - | - | - | - | - | - | - | - |  (excluded/unavailable: 0)
| HYBRID_30 | 0 | - | - | - | - | - | - | - | - |  (excluded/unavailable: 0)

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 0 | 0 | 0 | 0 | 0 | - | - | - |
| DATA_ONLY | total | 0 | 0 | 0 | 0 | 0 | - | - | - |
| HYBRID_30 | margin | 0 | 0 | 0 | 0 | 0 | - | - | - |
| HYBRID_30 | total | 0 | 0 | 0 | 0 | 0 | - | - | - |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 0 | - | - | - |
| DATA_ONLY | margin | 2-3 | 0 | - | - | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 0 | - | - | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 0 | - | - | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 0 | - | - | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 0 | - | - | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {}; DATA_ONLY quality states: {}; close centre status: {}.

## Game-centre accuracy — T-6h (1 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1 | 1 | 26.50 | 26.50 | 26.50 | 7.00 | 7.00 | -7.00 | 0.476 |
| DATA_ONLY | 1 | 1 | 28.14 | 28.14 | 28.14 | 6.10 | 6.10 | -6.10 | 0.572 |
| HYBRID_30 | 1 | 1 | 26.99 | 26.99 | 26.99 | 6.73 | 6.73 | -6.73 | 0.482 |
| market at snapshot | 1 | 1 | 26.50 | 26.50 | 26.50 | 7.00 | 7.00 | -7.00 | - |
| market at close | 1 | 1 | 26.50 | 26.50 | 26.50 | 7.00 | 7.00 | -7.00 | - |

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
| DATA_ONLY | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 1.64 |
| DATA_ONLY | total | 1 | 0 | 0 | 1 | 0 | - | 1.000 | 0.90 |
| HYBRID_30 | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 0.49 |
| HYBRID_30 | total | 1 | 0 | 0 | 1 | 0 | - | 1.000 | 0.27 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 1 | 28.14 | 26.50 | - |
| DATA_ONLY | margin | 2-3 | 0 | - | - | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 6.10 | 7.00 | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 0 | - | - | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 1 | 26.99 | 26.50 | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 1 | 6.73 | 7.00 | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 1}; DATA_ONLY quality states: {'OK': 1}; close centre status: {'OK': 1}.

## Game-centre accuracy — T-90m (0 games, 0 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 0 | - | - | - | - | - | - | - | - |  (excluded/unavailable: 0)
| DATA_ONLY | 0 | - | - | - | - | - | - | - | - |  (excluded/unavailable: 0)
| HYBRID_30 | 0 | - | - | - | - | - | - | - | - |  (excluded/unavailable: 0)

### Paired differences (negative favours the first arm)

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs CURRENT | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |

### Against the market centre, same games

| comparison | games | metric | mean diff in abs error (A - B) | SE | 95% CI | share A closer | evidence |
|---|---|---|---|---|---|---|---|
| CURRENT vs market_at_snapshot | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs close | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs close | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 0 | margin | - | - | - | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs close | 0 | total | - | - | - | - | INSUFFICIENT_EVIDENCE |

### Information addition: did the deviation from the snapshot market point toward the close?

| arm | quantity | games | toward | away | unchanged | no close | toward share | closer to actual than market | mean |dev| |
|---|---|---|---|---|---|---|---|---|---|
| DATA_ONLY | margin | 0 | 0 | 0 | 0 | 0 | - | - | - |
| DATA_ONLY | total | 0 | 0 | 0 | 0 | 0 | - | - | - |
| HYBRID_30 | margin | 0 | 0 | 0 | 0 | 0 | - | - | - |
| HYBRID_30 | total | 0 | 0 | 0 | 0 | 0 | - | - | - |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 0 | - | - | - |
| DATA_ONLY | margin | 2-3 | 0 | - | - | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 0 | - | - | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 0 | - | - | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 0 | - | - | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 0 | - | - | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {}; DATA_ONLY quality states: {}; close centre status: {}.

## Game-centre accuracy — T-30m (1 games, 1 weeks; INSUFFICIENT_EVIDENCE)

| arm | games | weeks | margin MAE | margin RMSE | margin bias | total MAE | total RMSE | total bias | home-win Brier |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 1 | 1 | 26.50 | 26.50 | 26.50 | 7.00 | 7.00 | -7.00 | 0.482 |
| DATA_ONLY | 1 | 1 | 28.14 | 28.14 | 28.14 | 6.10 | 6.10 | -6.10 | 0.568 |
| HYBRID_30 | 1 | 1 | 26.99 | 26.99 | 26.99 | 6.73 | 6.73 | -6.73 | 0.481 |
| market at snapshot | 1 | 1 | 26.50 | 26.50 | 26.50 | 7.00 | 7.00 | -7.00 | - |
| market at close | 1 | 1 | 26.50 | 26.50 | 26.50 | 7.00 | 7.00 | -7.00 | - |

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
| DATA_ONLY | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 1.64 |
| DATA_ONLY | total | 1 | 0 | 0 | 1 | 0 | - | 1.000 | 0.90 |
| HYBRID_30 | margin | 1 | 0 | 0 | 1 | 0 | - | 0.000 | 0.49 |
| HYBRID_30 | total | 1 | 0 | 0 | 1 | 0 | - | 1.000 | 0.27 |

### Disagreement bands (|challenger − market| in points; one sample cut five ways, not five studies)

| arm | quantity | band | games | arm MAE | market MAE | toward share |
|---|---|---|---|---|---|---|
| DATA_ONLY | margin | <=1 | 0 | - | - | - |
| DATA_ONLY | margin | 1-2 | 1 | 28.14 | 26.50 | - |
| DATA_ONLY | margin | 2-3 | 0 | - | - | - |
| DATA_ONLY | margin | 3-5 | 0 | - | - | - |
| DATA_ONLY | margin | >5 | 0 | - | - | - |
| DATA_ONLY | total | <=1 | 1 | 6.10 | 7.00 | - |
| DATA_ONLY | total | 1-2 | 0 | - | - | - |
| DATA_ONLY | total | 2-3 | 0 | - | - | - |
| DATA_ONLY | total | 3-5 | 0 | - | - | - |
| DATA_ONLY | total | >5 | 0 | - | - | - |
| HYBRID_30 | margin | <=1 | 1 | 26.99 | 26.50 | - |
| HYBRID_30 | margin | 1-2 | 0 | - | - | - |
| HYBRID_30 | margin | 2-3 | 0 | - | - | - |
| HYBRID_30 | margin | 3-5 | 0 | - | - | - |
| HYBRID_30 | margin | >5 | 0 | - | - | - |
| HYBRID_30 | total | <=1 | 1 | 6.73 | 7.00 | - |
| HYBRID_30 | total | 1-2 | 0 | - | - | - |
| HYBRID_30 | total | 2-3 | 0 | - | - | - |
| HYBRID_30 | total | 3-5 | 0 | - | - | - |
| HYBRID_30 | total | >5 | 0 | - | - | - |

Centre source at snapshot: {'kalshi_implied': 1}; DATA_ONLY quality states: {'OK': 1}; close centre status: {'OK': 1}.

## Contract pricing — latest_pregame (80 contracts, 1 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 80 | 0.2514 | 0.7070 | 0.378 | 0.487 | 80 | 0.2514 | 0.2529 | 0.2554 |
| DATA_ONLY | 80 | 0.2861 | 0.8218 | 0.380 | 0.487 | 80 | 0.2861 | 0.2529 | 0.2554 |
| HYBRID_30 | 80 | 0.2626 | 0.7416 | 0.386 | 0.487 | 80 | 0.2626 | 0.2529 | 0.2554 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 80 | 1 | 0.03467 | - | 0.03467 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 80 | 1 | 0.01125 | - | 0.01125 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 80 | 1 | -0.02342 | - | -0.02342 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 80 | 1 | - | - | -0.00152 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 79 | 1 | - | - | -0.00079 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 80 | 1 | - | - | 0.03315 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 79 | 1 | - | - | 0.03431 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 80 | 1 | - | - | 0.00972 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 79 | 1 | - | - | 0.01060 | - | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 4, 'GAME_WINNER': 2, 'SPREAD': 27, 'TEAM_TOTAL': 28, 'TOTAL': 19}; settlement: {'SETTLED': 80}; close: {'OK': 79, 'OK_STALE': 1}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 16 / 0.053 / 0.188 | 16 / 0.046 / 0.312 | 15 / 0.057 / 0.267 |
| 0.10-0.20 | 13 / 0.150 / 0.538 | 13 / 0.144 / 0.538 | 11 / 0.150 / 0.455 |
| 0.20-0.30 | 9 / 0.254 / 0.444 | 10 / 0.244 / 0.300 | 11 / 0.251 / 0.455 |
| 0.30-0.40 | 10 / 0.349 / 0.500 | 8 / 0.349 / 0.750 | 9 / 0.349 / 0.556 |
| 0.40-0.50 | 8 / 0.458 / 0.625 | 8 / 0.449 / 0.500 | 8 / 0.446 / 0.625 |
| 0.50-0.60 | 5 / 0.560 / 0.400 | 4 / 0.547 / 0.250 | 7 / 0.559 / 0.429 |
| 0.60-0.70 | 7 / 0.657 / 0.429 | 7 / 0.652 / 0.429 | 7 / 0.654 / 0.286 |
| 0.70-0.80 | 2 / 0.755 / 0.500 | 3 / 0.743 / 0.333 | 3 / 0.764 / 0.667 |
| 0.80-0.90 | 4 / 0.850 / 0.750 | 5 / 0.849 / 0.600 | 4 / 0.841 / 0.750 |
| 0.90-1.00 | 6 / 0.952 / 1.000 | 6 / 0.961 / 1.000 | 5 / 0.948 / 1.000 |

## Contract pricing — T-6h (80 contracts, 1 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 80 | 0.2496 | 0.7017 | 0.379 | 0.487 | 80 | 0.2496 | 0.2557 | 0.2554 |
| DATA_ONLY | 80 | 0.2871 | 0.8224 | 0.379 | 0.487 | 80 | 0.2871 | 0.2557 | 0.2554 |
| HYBRID_30 | 80 | 0.2636 | 0.7447 | 0.385 | 0.487 | 80 | 0.2636 | 0.2557 | 0.2554 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 80 | 1 | 0.03749 | - | 0.03749 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 80 | 1 | 0.01403 | - | 0.01403 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 80 | 1 | -0.02345 | - | -0.02345 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 80 | 1 | - | - | -0.00617 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 79 | 1 | - | - | -0.00265 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 80 | 1 | - | - | 0.03131 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 79 | 1 | - | - | 0.03531 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 80 | 1 | - | - | 0.00786 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 79 | 1 | - | - | 0.01156 | - | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 4, 'GAME_WINNER': 2, 'SPREAD': 27, 'TEAM_TOTAL': 28, 'TOTAL': 19}; settlement: {'SETTLED': 80}; close: {'OK': 79, 'OK_STALE': 1}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 15 / 0.050 / 0.200 | 16 / 0.046 / 0.312 | 15 / 0.055 / 0.267 |
| 0.10-0.20 | 13 / 0.144 / 0.462 | 13 / 0.143 / 0.538 | 11 / 0.147 / 0.455 |
| 0.20-0.30 | 11 / 0.255 / 0.455 | 10 / 0.242 / 0.300 | 12 / 0.252 / 0.417 |
| 0.30-0.40 | 9 / 0.355 / 0.556 | 8 / 0.346 / 0.750 | 8 / 0.353 / 0.625 |
| 0.40-0.50 | 8 / 0.459 / 0.625 | 8 / 0.447 / 0.500 | 8 / 0.447 / 0.625 |
| 0.50-0.60 | 5 / 0.559 / 0.400 | 4 / 0.549 / 0.250 | 7 / 0.562 / 0.429 |
| 0.60-0.70 | 7 / 0.654 / 0.429 | 7 / 0.651 / 0.429 | 7 / 0.656 / 0.286 |
| 0.70-0.80 | 2 / 0.753 / 0.500 | 4 / 0.757 / 0.500 | 3 / 0.768 / 0.667 |
| 0.80-0.90 | 4 / 0.851 / 0.750 | 3 / 0.849 / 0.667 | 4 / 0.846 / 0.750 |
| 0.90-1.00 | 6 / 0.952 / 1.000 | 7 / 0.951 / 0.857 | 5 / 0.950 / 1.000 |

## Contract pricing — T-30m (80 contracts, 1 games; INSUFFICIENT_EVIDENCE)

Event space (binary settlements only) and contract space (exact payouts) are separate tables.

| arm | event contracts | Brier | log loss | mean predicted | actual rate | payout contracts | payout MSE | market@snap MSE | market@close MSE |
|---|---|---|---|---|---|---|---|---|---|
| CURRENT | 80 | 0.2508 | 0.7045 | 0.378 | 0.487 | 80 | 0.2508 | 0.2530 | 0.2554 |
| DATA_ONLY | 80 | 0.2851 | 0.8177 | 0.379 | 0.487 | 80 | 0.2851 | 0.2530 | 0.2554 |
| HYBRID_30 | 80 | 0.2624 | 0.7414 | 0.385 | 0.487 | 80 | 0.2624 | 0.2530 | 0.2554 |

### Paired contract differences (game-clustered bootstrap; negative favours the first arm)

| comparison | contracts | games | Brier diff | 95% CI | payout MSE diff | 95% CI | evidence |
|---|---|---|---|---|---|---|---|
| DATA_ONLY vs CURRENT | 80 | 1 | 0.03430 | - | 0.03430 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs CURRENT | 80 | 1 | 0.01163 | - | 0.01163 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs DATA_ONLY | 80 | 1 | -0.02267 | - | -0.02267 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_snapshot | 80 | 1 | - | - | -0.00219 | - | INSUFFICIENT_EVIDENCE |
| CURRENT vs market_at_close | 79 | 1 | - | - | -0.00141 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_snapshot | 80 | 1 | - | - | 0.03211 | - | INSUFFICIENT_EVIDENCE |
| DATA_ONLY vs market_at_close | 79 | 1 | - | - | 0.03332 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_snapshot | 80 | 1 | - | - | 0.00944 | - | INSUFFICIENT_EVIDENCE |
| HYBRID_30 vs market_at_close | 79 | 1 | - | - | 0.01036 | - | INSUFFICIENT_EVIDENCE |

Families: {'BOTH_TEAMS_SCORE_N': 4, 'GAME_WINNER': 2, 'SPREAD': 27, 'TEAM_TOTAL': 28, 'TOTAL': 19}; settlement: {'SETTLED': 80}; close: {'OK': 79, 'OK_STALE': 1}.

### Calibration by predicted-probability decile (event space)

| band | CURRENT n / predicted / actual | DATA_ONLY n / predicted / actual | HYBRID_30 n / predicted / actual |
|---|---|---|---|
| 0.00-0.10 | 15 / 0.049 / 0.200 | 16 / 0.045 / 0.312 | 15 / 0.055 / 0.267 |
| 0.10-0.20 | 13 / 0.143 / 0.462 | 13 / 0.143 / 0.538 | 11 / 0.147 / 0.455 |
| 0.20-0.30 | 10 / 0.249 / 0.500 | 10 / 0.241 / 0.300 | 12 / 0.252 / 0.417 |
| 0.30-0.40 | 9 / 0.343 / 0.556 | 9 / 0.350 / 0.667 | 8 / 0.353 / 0.625 |
| 0.40-0.50 | 9 / 0.451 / 0.556 | 7 / 0.453 / 0.571 | 8 / 0.448 / 0.625 |
| 0.50-0.60 | 5 / 0.559 / 0.400 | 4 / 0.544 / 0.250 | 7 / 0.560 / 0.429 |
| 0.60-0.70 | 7 / 0.654 / 0.429 | 7 / 0.651 / 0.429 | 7 / 0.655 / 0.286 |
| 0.70-0.80 | 2 / 0.755 / 0.500 | 3 / 0.743 / 0.333 | 3 / 0.767 / 0.667 |
| 0.80-0.90 | 4 / 0.850 / 0.750 | 5 / 0.851 / 0.600 | 4 / 0.844 / 0.750 |
| 0.90-1.00 | 6 / 0.950 / 1.000 | 6 / 0.961 / 1.000 | 5 / 0.949 / 1.000 |

## Reading this report

Preregistration ef0a095ace1ec698 (H-20260910-026): arms CURRENT, DATA_ONLY, HYBRID_30; hybrid 0.70 market / 0.30 data; horizons T-24h, T-6h, T-90m, T-30m; verdict floor 64 games.
The sample size is games (and contracts within games), never snapshots. The historical closing line beat this football model in every season on record; the open question is the earlier horizons, and only the accumulated prospective record answers it. No challenger has betting authority.

## LOCALIZED SIGNAL (GAME CENTRE)

Preregistered hypotheses H2-GC-MARGIN-2026W02 / H2-GC-TOTAL-2026W02 (research/hypothesis_registry/v2/hypotheses.jsonl): when DATA_ONLY's centre deviates from the snapshot market centre by >= 1.0 point, the market moves toward it by the close. Unit: one game per horizon view. The toward rate is toward / (toward + away); `unchanged` and `no close` are shown and are NEVER in its denominator. HYBRID_30's deviation is 0.3 × DATA_ONLY's, so its split is the same games — **derived, not independent evidence**. The same section, with the future-window evaluation, is in the shadow-v2 weekly report (LOCALIZED SIGNAL RESEARCH).

| view | arm | quantity | games | below 1.0 pt | toward | away | unchanged | no close | toward rate [95% Wilson] | closer than snap mkt | closer than close | mean signed close move (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-24h | DATA_ONLY | margin | 0 | 0 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-24h | DATA_ONLY | total | 0 | 0 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-24h | HYBRID_30 (derived) | margin | 0 | 0 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-24h | HYBRID_30 (derived) | total | 0 | 0 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-6h | DATA_ONLY | margin | 1 | 0 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-6h | DATA_ONLY | total | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-6h | HYBRID_30 (derived) | margin | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-6h | HYBRID_30 (derived) | total | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-90m | DATA_ONLY | margin | 0 | 0 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-90m | DATA_ONLY | total | 0 | 0 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-90m | HYBRID_30 (derived) | margin | 0 | 0 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-90m | HYBRID_30 (derived) | total | 0 | 0 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-30m | DATA_ONLY | margin | 1 | 0 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| T-30m | DATA_ONLY | total | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-30m | HYBRID_30 (derived) | margin | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| T-30m | HYBRID_30 (derived) | total | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| latest_pregame | DATA_ONLY | margin | 1 | 0 | 0 | 0 | 1 | 0 | - - | 0.000 | 0.000 | 0.00 |
| latest_pregame | DATA_ONLY | total | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| latest_pregame | HYBRID_30 (derived) | margin | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |
| latest_pregame | HYBRID_30 (derived) | total | 1 | 1 | 0 | 0 | 0 | 0 | - - | - | - | - |

### DATA_ONLY by disagreement band, latest pregame (every usable game; threshold not applied)

| quantity | band | games | toward | away | unchanged | no close | toward rate |
|---|---|---|---|---|---|---|---|
| margin | <=1 | 0 | 0 | 0 | 0 | 0 | - |
| margin | 1-2 | 1 | 0 | 0 | 1 | 0 | - |
| margin | 2-3 | 0 | 0 | 0 | 0 | 0 | - |
| margin | 3-5 | 0 | 0 | 0 | 0 | 0 | - |
| margin | >5 | 0 | 0 | 0 | 0 | 0 | - |
| total | <=1 | 1 | 0 | 0 | 1 | 0 | - |
| total | 1-2 | 0 | 0 | 0 | 0 | 0 | - |
| total | 2-3 | 0 | 0 | 0 | 0 | 0 | - |
| total | 3-5 | 0 | 0 | 0 | 0 | 0 | - |
| total | >5 | 0 | 0 | 0 | 0 | 0 | - |

## Player projection autopsy (largest standardised misses; diagnosis, never a model change)

69 player-stat-game projections diagnosed. Ranked by |robust z| of the actual inside the fitted distribution (cross-statistic), ties by game and player. Classification is deterministic from the recorded intermediates.

| game | player | stat | mean | q05–q95 | actual | z | pct | proj opp | act opp | proj eff | act eff | avail | played | model vs market | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_03_ATL_GB | MarShawn Lloyd | receiving_yards | 1.0 | 0–11 | 7 | 9.44 | 0.87 | 1.0 | 3 | 1.04 | 2.33 | EXPECTED_ACTIVE | True | -0.193 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Drake London | receiving_yards | 52.7 | 4–123 | 194 | 4.10 | 0.99 | 5.9 | 10 | 8.96 | 19.40 | EXPECTED_ACTIVE | True | 0.190 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Matthew Golden | receiving_yards | 24.0 | 0–67 | 100 | 3.95 | 0.99 | 2.4 | 12 | 10.15 | 8.33 | EXPECTED_ACTIVE | True | 0.435 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Bijan Robinson | rushing_yards | 63.1 | 14–128 | 194 | 3.90 | 0.99 | 12.2 | 29 | 5.16 | 6.69 | EXPECTED_ACTIVE | True | 0.200 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Austin Hooper | touchdowns | 0.1 | -–- | 1 | 3.87 | - | 2.2 | 2 | - | - | EXPECTED_ACTIVE | True | -0.006 | UNEXPLAINED_VARIANCE |
| 2026_03_ATL_GB | Christian Watson | receptions | 2.1 | 0–6 | 7 | 3.37 | 0.96 | 3.4 | 10 | 0.62 | 0.70 | EXPECTED_ACTIVE | True | 0.467 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Bijan Robinson | carries | 12.2 | 5–22 | 29 | 3.28 | 0.99 | 12.2 | 29 | - | - | EXPECTED_ACTIVE | True | 0.435 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Matthew Golden | touchdowns | 0.1 | -–- | 1 | 2.80 | - | 4.0 | 12 | - | - | EXPECTED_ACTIVE | True | 0.193 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Brian Robinson | touchdowns | 0.1 | -–- | 1 | 2.75 | - | 7.9 | 10 | - | - | EXPECTED_ACTIVE | True | 0.050 | UNEXPLAINED_VARIANCE |
| 2026_03_ATL_GB | MarShawn Lloyd | receptions | 0.7 | 0–5 | 2 | 2.70 | 0.80 | 1.0 | 3 | 0.74 | 0.67 | EXPECTED_ACTIVE | True | 0.352 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Matthew Golden | receptions | 1.5 | 0–5 | 5 | 2.70 | 0.95 | 2.4 | 12 | 0.63 | 0.42 | EXPECTED_ACTIVE | True | 0.480 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Drake London | receptions | 3.3 | 1–7 | 9 | 2.70 | 0.99 | 5.9 | 10 | 0.57 | 0.90 | EXPECTED_ACTIVE | True | 0.246 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Skyy Moore | receiving_yards | 12.2 | 0–53 | 31 | 2.61 | 0.83 | 1.6 | 7 | 7.75 | 4.43 | EXPECTED_ACTIVE | True | 0.200 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Jordan Love | attempts | 32.5 | 18–47 | 53 | 2.45 | 0.98 | 32.5 | 53 | - | - | EXPECTED_ACTIVE | True | -0.019 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Christian Watson | receiving_yards | 41.0 | 3–95 | 96 | 2.15 | 0.95 | 3.4 | 10 | 12.02 | 9.60 | EXPECTED_ACTIVE | True | 0.315 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Christian Watson | touchdowns | 0.2 | -–- | 1 | 2.09 | - | 5.1 | 10 | - | - | EXPECTED_ACTIVE | True | 0.201 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Chris Brooks | receiving_yards | 3.1 | 0–33 | 4 | 1.80 | 0.76 | 1.3 | 1 | 2.43 | 4.00 | EXPECTED_ACTIVE | True | -0.140 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Brian Robinson | rushing_yards | 21.5 | 0–67 | 50 | 1.75 | 0.86 | 4.7 | 10 | 4.59 | 5.00 | EXPECTED_ACTIVE | True | 0.213 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Jordan Love | passing_tds | 1.4 | 0–4 | 2 | 1.35 | 0.75 | 32.5 | 53 | 0.04 | 0.04 | EXPECTED_ACTIVE | True | 0.096 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Skyy Moore | receptions | 1.0 | 0–5 | 3 | 1.35 | 0.82 | 1.6 | 7 | 0.66 | 0.43 | EXPECTED_ACTIVE | True | 0.122 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Chris Brooks | receptions | 0.9 | 0–5 | 1 | 1.35 | 0.75 | 1.3 | 1 | 0.72 | 1.00 | EXPECTED_ACTIVE | True | -0.138 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Tucker Kraft | receptions | 1.8 | 0–5 | 4 | 1.35 | 0.85 | 2.5 | 8 | 0.72 | 0.50 | EXPECTED_ACTIVE | True | 0.368 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Bijan Robinson | touchdowns | 0.4 | -–- | 2 | 1.34 | - | 17.2 | 31 | - | - | EXPECTED_ACTIVE | True | 0.193 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Jordan Love | completions | 21.1 | 11–31 | 28 | 1.18 | 0.85 | 32.5 | 53 | 0.65 | 0.53 | EXPECTED_ACTIVE | True | -0.095 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Brian Robinson | carries | 4.7 | 0–18 | 10 | 1.16 | 0.79 | 4.7 | 10 | - | - | EXPECTED_ACTIVE | True | 0.253 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Jordan Love | passing_yards | 238.6 | 115–362 | 312 | 0.98 | 0.81 | 32.5 | 53 | 7.33 | 5.89 | EXPECTED_ACTIVE | True | -0.058 | TEAM_VOLUME_MISS |
| 2026_03_ATL_GB | Kyle Pitts Sr. | receptions | 2.7 | 0–6 | 1 | -0.90 | 0.25 | 3.7 | 2 | 0.72 | 0.50 | EXPECTED_ACTIVE | True | -0.208 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Michael Penix Jr. | rushing_yards | 10.7 | 0–33 | -2 | -0.81 | 0.05 | 2.8 | 2 | 3.82 | -1.00 | EXPECTED_ACTIVE | True | 0.106 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Michael Penix Jr. | attempts | 32.2 | 18–47 | 25 | -0.79 | 0.23 | 32.2 | 25 | - | - | EXPECTED_ACTIVE | True | 0.069 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Jonnu Smith | receiving_yards | 13.4 | 0–45 | 16 | 0.75 | 0.71 | 1.9 | 3 | 7.07 | 5.33 | EXPECTED_ACTIVE | True | 0.038 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Kyle Pitts Sr. | receiving_yards | 36.6 | 0–102 | 5 | -0.69 | 0.16 | 3.7 | 2 | 9.92 | 2.50 | EXPECTED_ACTIVE | True | -0.165 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Austin Hooper | receptions | 1.1 | 0–5 | 2 | 0.67 | 0.75 | 1.6 | 2 | 0.69 | 1.00 | EXPECTED_ACTIVE | True | -0.025 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Jonnu Smith | receptions | 1.3 | 0–5 | 2 | 0.67 | 0.75 | 1.9 | 3 | 0.70 | 0.67 | EXPECTED_ACTIVE | True | -0.024 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Jordan Love | rushing_yards | 14.7 | 0–46 | 0 | -0.64 | 0.05 | 3.2 | 1 | 4.56 | 0.00 | EXPECTED_ACTIVE | True | 0.063 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Drake London | touchdowns | 0.2 | -–- | 0 | -0.53 | - | 6.7 | 10 | - | - | EXPECTED_ACTIVE | True | -0.097 | NO_LARGE_MISS |
| 2026_03_ATL_GB | Jordan Love | touchdowns | 0.2 | -–- | 0 | -0.51 | - | 2.8 | 1 | - | - | EXPECTED_ACTIVE | True | 0.087 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Michael Penix Jr. | passing_yards | 219.0 | 94–344 | 256 | 0.49 | 0.68 | 32.2 | 25 | 6.79 | 10.24 | EXPECTED_ACTIVE | True | -0.076 | EFFICIENCY_MISS |
| 2026_03_ATL_GB | Kyle Pitts Sr. | touchdowns | 0.2 | -–- | 0 | -0.49 | - | 5.1 | 2 | - | - | EXPECTED_ACTIVE | True | 0.004 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Tucker Kraft | touchdowns | 0.2 | -–- | 0 | -0.47 | - | 4.0 | 8 | - | - | EXPECTED_ACTIVE | True | -0.114 | OPPORTUNITY_MISS |
| 2026_03_ATL_GB | Olamide Zaccheaus | receptions | 1.6 | 0–5 | 2 | 0.45 | 0.62 | 2.6 | 2 | 0.60 | 1.00 | EXPECTED_ACTIVE | True | -0.036 | EFFICIENCY_MISS |

Classification counts over every diagnosed projection: {'TEAM_VOLUME_MISS': 21, 'EFFICIENCY_MISS': 13, 'UNEXPLAINED_VARIANCE': 2, 'OPPORTUNITY_MISS': 13, 'NO_LARGE_MISS': 20}.
Missing usage (no snap table or stats row): 0.

## Decision funnel

No funnel accounting is available for this period.

