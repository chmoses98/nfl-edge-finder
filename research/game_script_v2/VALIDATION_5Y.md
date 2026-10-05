# Five-season validation: injury redistribution and weather

Generated from `validation_5y.json` by `scripts/sim/write_game_script_v2.py` -- do not edit by hand. **RESEARCH_ONLY: no betting authority.**

Reproduce: `python scripts/sim/game_script_v2_report.py validation`.

## Injury / availability redistribution (preregistration section 9)

historical designations are the final pregame report (the only historical artifact); a player can sit in several populations at once; populations are descriptive; all select on pregame information except QB_STARTER_ERROR, which is defined after the fact from who threw the most passes.

`TEAMMATE_OF_OUT_STARTER` is the registered population (depth-chart-1 RB/WR/TE designated Out/Doubtful). `TEAMMATE_OF_UNAVAILABLE_STARTER` is a POST-HOC broadening to any absence, added because the historical eligible set is the game-day active list and most absences carry no designation.

| season | dc1 RB/WR/TE unavailable, by reason | team-games with dc1 unavailable | with 2+ of dc1-2 unavailable |
|---|---|---|---|
| 2021 | DESIGNATED_OUT 105, ROSTER_RES 78, GAME_DAY_INACTIVE 55, DESIGNATED_DOUBTFUL 27, ROSTER_CUT 3, ROSTER_DEV 1 | 217 | 158 |
| 2022 | DESIGNATED_OUT 140, GAME_DAY_INACTIVE 75, ROSTER_RES 21, DESIGNATED_DOUBTFUL 15, ROSTER_CUT 3, ROSTER_DEV 1 | 195 | 144 |
| 2023 | DESIGNATED_OUT 109, GAME_DAY_INACTIVE 77, DESIGNATED_DOUBTFUL 21, ROSTER_RES 14, ROSTER_CUT 2, ROSTER_DEV 2 | 190 | 127 |
| 2024 | DESIGNATED_OUT 111, GAME_DAY_INACTIVE 58, DESIGNATED_DOUBTFUL 35, ROSTER_RES 17, ROSTER_CUT 2 | 184 | 122 |
| 2025 | DESIGNATED_OUT 99, GAME_DAY_INACTIVE 24, ROSTER_RES 11, DESIGNATED_DOUBTFUL 7 | 126 | 58 |

### carries (pooled 2021-2025)

| population | n | games | bias (pred − actual) [95% CI] | MAE | CRPS | cover50 | cover90 [95% CI] |
|---|---|---|---|---|---|---|---|
| TEAMMATE_OF_OUT_STARTER | 1673 | 530 | -0.015 [-0.203, 0.171] | 3.618 | 2.538 | 0.641 | 0.958 [0.948, 0.968] |
| TEAMMATE_OF_UNAVAILABLE_STARTER | 2596 | 758 | -0.024 [-0.164, 0.114] | 3.632 | 2.545 | 0.634 | 0.958 [0.950, 0.966] |
| QUESTIONABLE | 336 | 289 | -1.633 [-2.179, -1.083] | 4.047 | 3.154 | 0.667 | 0.943 [0.917, 0.967] |
| MULTIPLE_OUT | 1689 | 530 | 0.079 [-0.100, 0.258] | 3.665 | 2.539 | 0.637 | 0.960 [0.951, 0.970] |
| NEW_STARTER_NO_HISTORY | 36 | 35 | -0.991 [-2.475, 0.411] | 3.586 | 2.586 | 0.500 | 0.972 [0.914, 1.000] |
| QB_STARTER_ERROR | 605 | 207 | 0.629 [0.304, 0.947] | 4.095 | 2.810 | 0.534 | 0.891 [0.865, 0.916] |
| REST | 4525 | 1154 | -0.047 | 3.435 | 2.403 | 0.654 | 0.977 |

### targets (pooled 2021-2025)

| population | n | games | bias (pred − actual) [95% CI] | MAE | CRPS | cover50 | cover90 [95% CI] |
|---|---|---|---|---|---|---|---|
| TEAMMATE_OF_OUT_STARTER | 3447 | 530 | 0.011 [-0.088, 0.116] | 2.161 | 1.544 | 0.710 | 0.979 [0.974, 0.984] |
| TEAMMATE_OF_UNAVAILABLE_STARTER | 5346 | 758 | 0.079 [0.003, 0.155] | 2.137 | 1.520 | 0.715 | 0.982 [0.978, 0.985] |
| QUESTIONABLE | 874 | 619 | -0.711 [-0.897, -0.531] | 2.221 | 1.715 | 0.759 | 0.990 [0.982, 0.996] |
| MULTIPLE_OUT | 3593 | 530 | 0.040 [-0.056, 0.137] | 2.172 | 1.539 | 0.705 | 0.982 [0.978, 0.987] |
| NEW_STARTER_NO_HISTORY | 37 | 34 | -1.358 [-2.485, -0.305] | 2.571 | 1.989 | 0.595 | 0.919 [0.821, 1.000] |
| QB_STARTER_ERROR | 1305 | 207 | -0.063 [-0.226, 0.101] | 2.104 | 1.497 | 0.698 | 0.980 [0.972, 0.988] |
| REST | 9488 | 1156 | -0.059 | 2.014 | 1.439 | 0.733 | 0.988 |

## Weather

### Historical: NON_PIT_DESCRIPTIVE (2016-2025, outdoor stadiums)

observed game-time weather is hindsight: these rows describe, they cannot fit or promote a feature; retractable roofs are excluded because open/closed is decided on game day.

1920 outdoor games, 1794 with an observed wind reading.

| observed wind (mph) | games | total − closing total [95% CI] |
|---|---|---|
| 0-9 | 1186 | 0.82 [0.06, 1.58] |
| 10-14 | 404 | -1.31 [-2.49, -0.13] |
| 15-19 | 161 | -2.66 [-4.65, -0.68] |
| 20+ | 43 | 0.79 [-3.39, 4.97] |

| observed temperature | games | total − closing total [95% CI] |
|---|---|---|
| <32F | 113 | -0.47 [-2.87, 1.92] |
| 32-49F | 489 | -0.39 [-1.59, 0.81] |
| 50F+ | 1192 | 0.25 [-0.49, 0.98] |

| observed wind (mph) | games 2021-2025 | combined pass attempts − simulation mean [95% CI] |
|---|---|---|
| 0-9 | 539 | -0.08 [-0.91, 0.74] |
| 10-14 | 193 | -0.50 [-2.02, 1.03] |
| 15-19 | 74 | -2.20 [-4.35, -0.04] |
| 20+ | 21 | -7.64 [-12.56, -2.72] |

None of these rows may fit or promote a predictive feature.

### Prospective 2026: PROSPECTIVE_ACCUMULATING

Completed 2026 games: 63; with a point-in-time kickoff forecast (newest vintage retrieved at or before kickoff): 60 (median lead 4.0 h); outdoors with a forecast: 42; qualifying for W1/W2 (forecast wind ≥ 15 mph, outdoors): 2. Readout: NOT_READ: preregistered as accumulate-only in this study. GAME SCRIPT V2 shows the forecast with `weather_model_status = NOT_IN_MODEL`.

