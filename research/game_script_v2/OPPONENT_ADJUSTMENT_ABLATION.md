# Opponent-adjusted team ratings: walk-forward ablation (2021-2025)

Generated from `opponent_adjustment_ablation.json` by `scripts/sim/write_game_script_v2.py` -- do not edit by hand. **RESEARCH_ONLY: no betting authority.**

Reproduce: `python scripts/sim/oppadj_ablation.py features`, `python scripts/sim/oppadj_ablation.py run --arm <ARM> --seasons <Y>` for every arm and season, then `python scripts/sim/game_script_v2_report.py ablation`. Design and the promotion rule: `PREREGISTRATION.md` sections 5-6 (stage 1) and the stage-2 addendum (R1).

Comparison is paired on A0's scored rows (backtest.FLOORS on the A0 predictive mean); intervals are game-clustered (2000 resamples). Primary summary = mean over the eight statistics of `CRPS_arm / CRPS_A0 − 1` (negative is better); material = -0.005.

## Arms

- **A1** — `plays_extra`: mx_plays, mx_sec_per_play; `pass_rate_extra`: mx_neutral_pass_rate, mx_neutral_proe
- **A2** — `carry_extra`: mx_designed_rush_epa, mx_success_rate, mx_explosive_rate; `target_extra`: mx_dropback_epa, mx_success_rate, mx_explosive_rate
- **A3** — `plays_extra`: mx_plays, mx_sec_per_play; `pass_rate_extra`: mx_neutral_pass_rate, mx_neutral_proe; `carry_extra`: mx_designed_rush_epa, mx_success_rate, mx_explosive_rate; `target_extra`: mx_dropback_epa, mx_success_rate, mx_explosive_rate
- **A4** — `opponent_def`: True
- **A5** — `opponent_def`: True; `plays_extra`: mx_plays, mx_sec_per_play; `pass_rate_extra`: mx_neutral_pass_rate, mx_neutral_proe
- **R1** — `outside_share_repair`: True

## Verdicts

| arm | 2021 | 2022 | 2023 | 2024 | 2025 | pooled [95% CI] | stats improved | verdict |
|---|---|---|---|---|---|---|---|---|
| A1 | -0.17% | -0.15% | -0.24% | -0.05% | -0.16% | -0.15% [-0.23, -0.07] | 8/8 | **REJECTED** |
| A2 | +0.03% | +0.04% | -0.01% | -0.02% | +0.02% | +0.01% [-0.01, +0.03] | 1/8 | **REJECTED** |
| A3 | -0.14% | -0.13% | -0.26% | -0.07% | -0.14% | -0.15% [-0.23, -0.07] | 8/8 | **REJECTED** |
| A4 | -0.26% | -0.08% | -0.33% | -0.06% | -0.14% | -0.18% [-0.27, -0.09] | 8/8 | **REJECTED** |
| A5 | -0.27% | -0.11% | -0.38% | -0.10% | -0.17% | -0.21% [-0.31, -0.10] | 8/8 | **REJECTED** |
| R1 | +0.06% | +0.06% | +0.05% | +0.03% | +0.01% | +0.04% [+0.03, +0.06] | 2/8 | **REJECTED** |

## Promotion criteria by arm

| arm | improves_in_at_least_4_of_5_seasons | no_season_materially_worse | pooled_ci_below_zero | pooled_improvement_material | calibration_not_materially_worse | broad_at_least_5_of_8_stats | survives_dropping_best_stat |
|---|---|---|---|---|---|---|---|
| A1 | True | True | True | False | True | True | True |
| A2 | False | False | False | False | True | False | False |
| A3 | True | True | True | False | True | True | True |
| A4 | True | True | True | False | False | True | True |
| A5 | True | True | True | False | True | True | True |
| R1 | False | False | False | False | True | False | False |

## Pooled relative CRPS change by statistic

| arm | carries | rush_yards | targets | receptions | rec_yards | attempts | completions | pass_yards | calibration Δ (SE) |
|---|---|---|---|---|---|---|---|---|---|
| A1 | -0.11% | -0.06% | -0.05% | -0.06% | -0.03% | -0.25% | -0.39% | -0.28% | -0.0003 (0.0005) |
| A2 | +0.00% | -0.01% | +0.00% | +0.02% | +0.01% | +0.00% | +0.05% | +0.01% | -0.0001 (0.0002) |
| A3 | -0.11% | -0.06% | -0.05% | -0.04% | -0.02% | -0.25% | -0.36% | -0.29% | -0.0004 (0.0005) |
| A4 | -0.11% | -0.03% | -0.08% | -0.07% | -0.05% | -0.33% | -0.39% | -0.36% | +0.0005 (0.0005) |
| A5 | -0.13% | -0.04% | -0.08% | -0.07% | -0.07% | -0.38% | -0.43% | -0.44% | -0.0000 (0.0005) |
| R1 | +0.13% | +0.04% | +0.08% | +0.07% | +0.04% | +0.03% | -0.01% | -0.02% | +0.0002 (0.0002) |

## Team-level CRPS (pooled over seasons, mean of season values)

| arm | plays | pass_att | rush_att | dropbacks | targets |
|---|---|---|---|---|---|
| A0 | 4.705 | 4.360 | 4.084 | 4.655 | 4.199 |
| A1 | 4.709 | 4.348 | 4.073 | 4.641 | 4.182 |
| A2 | 4.705 | 4.360 | 4.084 | 4.655 | 4.199 |
| A3 | 4.709 | 4.348 | 4.073 | 4.641 | 4.182 |
| A4 | 4.701 | 4.340 | 4.075 | 4.635 | 4.177 |
| A5 | 4.707 | 4.342 | 4.070 | 4.635 | 4.179 |
| R1 | 4.705 | 4.360 | 4.084 | 4.655 | 4.199 |

## Primitive diagnostic: do the adjusted ratings predict next week's team metric better?

One-week-ahead RMSE of the realized team-game metric from the adjusted matchup `mx` versus the unadjusted pair (same window and weights, no opponent model); `Δ MSE` = adjusted − unadjusted with a game-clustered 95% CI. Not a promotion criterion: a better rating that does not improve the simulated distributions is not deployed.

| season | metric | λ | RMSE adjusted | RMSE unadjusted | Δ MSE [95% CI] |
|---|---|---|---|---|---|
| 2021 | epa_play | 4 | 0.1976 | 0.2022 | -0.00184 [-0.00332, -0.00031] |
| 2021 | success_rate | 4 | 0.0698 | 0.0714 | -0.00023 [-0.00040, -0.00005] |
| 2021 | dropback_epa | 4 | 0.3200 | 0.3271 | -0.00458 [-0.00822, -0.00105] |
| 2021 | designed_rush_epa | 8 | 0.2047 | 0.2140 | -0.00387 [-0.00565, -0.00211] |
| 2021 | explosive_rate | 4 | 0.0402 | 0.0415 | -0.00011 [-0.00016, -0.00005] |
| 2021 | sack_rate | 8 | 0.0429 | 0.0444 | -0.00013 [-0.00021, -0.00006] |
| 2021 | plays | 16 | 8.5465 | 8.8230 | -4.80195 [-9.05814, -0.38612] |
| 2021 | sec_per_play | 8 | 3.9983 | 4.1952 | -1.61287 [-2.46277, -0.82379] |
| 2021 | neutral_pass_rate | 4 | 0.1110 | 0.1149 | -0.00088 [-0.00137, -0.00041] |
| 2021 | neutral_proe | 4 | 0.1036 | 0.1071 | -0.00072 [-0.00116, -0.00030] |
| 2021 | td_per_drive | 4 | 0.1316 | 0.1357 | -0.00110 [-0.00179, -0.00045] |
| 2022 | epa_play | 4 | 0.1694 | 0.1756 | -0.00216 [-0.00333, -0.00102] |
| 2022 | success_rate | 4 | 0.0685 | 0.0702 | -0.00024 [-0.00042, -0.00005] |
| 2022 | dropback_epa | 4 | 0.2638 | 0.2753 | -0.00622 [-0.00933, -0.00336] |
| 2022 | designed_rush_epa | 8 | 0.2315 | 0.2429 | -0.00542 [-0.00761, -0.00311] |
| 2022 | explosive_rate | 8 | 0.0387 | 0.0404 | -0.00013 [-0.00021, -0.00007] |
| 2022 | sack_rate | 8 | 0.0451 | 0.0462 | -0.00010 [-0.00020, -0.00001] |
| 2022 | plays | 16 | 8.1788 | 8.5607 | -6.39202 [-11.11264, -2.02599] |
| 2022 | sec_per_play | 8 | 3.7398 | 3.8975 | -1.20433 [-1.83301, -0.55642] |
| 2022 | neutral_pass_rate | 4 | 0.1017 | 0.1040 | -0.00047 [-0.00088, -0.00008] |
| 2022 | neutral_proe | 4 | 0.0975 | 0.0991 | -0.00032 [-0.00071, 0.00008] |
| 2022 | td_per_drive | 4 | 0.1210 | 0.1262 | -0.00127 [-0.00199, -0.00054] |
| 2023 | epa_play | 4 | 0.1903 | 0.1942 | -0.00150 [-0.00312, 0.00003] |
| 2023 | success_rate | 4 | 0.0692 | 0.0708 | -0.00023 [-0.00045, -0.00002] |
| 2023 | dropback_epa | 8 | 0.2952 | 0.2999 | -0.00278 [-0.00739, 0.00183] |
| 2023 | designed_rush_epa | 16 | 0.2154 | 0.2251 | -0.00428 [-0.00698, -0.00160] |
| 2023 | explosive_rate | 8 | 0.0402 | 0.0418 | -0.00014 [-0.00022, -0.00006] |
| 2023 | sack_rate | 8 | 0.0462 | 0.0477 | -0.00015 [-0.00026, -0.00003] |
| 2023 | plays | 8 | 8.4737 | 8.9386 | -8.09511 [-11.63273, -4.87574] |
| 2023 | sec_per_play | 8 | 3.5926 | 3.7828 | -1.40313 [-1.89908, -0.88647] |
| 2023 | neutral_pass_rate | 4 | 0.1000 | 0.1045 | -0.00092 [-0.00132, -0.00055] |
| 2023 | neutral_proe | 4 | 0.0953 | 0.0995 | -0.00083 [-0.00120, -0.00046] |
| 2023 | td_per_drive | 4 | 0.1232 | 0.1276 | -0.00110 [-0.00183, -0.00039] |
| 2024 | epa_play | 4 | 0.1926 | 0.1972 | -0.00179 [-0.00335, -0.00032] |
| 2024 | success_rate | 4 | 0.0697 | 0.0717 | -0.00027 [-0.00049, -0.00006] |
| 2024 | dropback_epa | 4 | 0.3036 | 0.3130 | -0.00578 [-0.00928, -0.00221] |
| 2024 | designed_rush_epa | 16 | 0.2203 | 0.2279 | -0.00341 [-0.00657, -0.00048] |
| 2024 | explosive_rate | 8 | 0.0389 | 0.0402 | -0.00010 [-0.00018, -0.00002] |
| 2024 | sack_rate | 8 | 0.0462 | 0.0481 | -0.00018 [-0.00027, -0.00010] |
| 2024 | plays | 16 | 8.3380 | 8.8323 | -8.48726 [-12.51615, -4.58908] |
| 2024 | sec_per_play | 16 | 3.7788 | 3.9635 | -1.42996 [-2.23164, -0.63788] |
| 2024 | neutral_pass_rate | 4 | 0.1083 | 0.1136 | -0.00117 [-0.00160, -0.00075] |
| 2024 | neutral_proe | 4 | 0.1009 | 0.1060 | -0.00106 [-0.00154, -0.00062] |
| 2024 | td_per_drive | 4 | 0.1311 | 0.1351 | -0.00105 [-0.00179, -0.00034] |
| 2025 | epa_play | 4 | 0.1963 | 0.1987 | -0.00098 [-0.00242, 0.00037] |
| 2025 | success_rate | 4 | 0.0714 | 0.0719 | -0.00007 [-0.00026, 0.00011] |
| 2025 | dropback_epa | 4 | 0.3069 | 0.3124 | -0.00343 [-0.00701, 0.00006] |
| 2025 | designed_rush_epa | 8 | 0.2226 | 0.2325 | -0.00450 [-0.00688, -0.00190] |
| 2025 | explosive_rate | 8 | 0.0405 | 0.0419 | -0.00011 [-0.00021, -0.00001] |
| 2025 | sack_rate | 8 | 0.0476 | 0.0485 | -0.00008 [-0.00020, 0.00003] |
| 2025 | plays | 32 | 8.6136 | 8.8579 | -4.26901 [-9.07631, 0.62910] |
| 2025 | sec_per_play | 16 | 3.5378 | 3.7224 | -1.34031 [-2.15250, -0.59909] |
| 2025 | neutral_pass_rate | 8 | 0.1051 | 0.1092 | -0.00088 [-0.00144, -0.00034] |
| 2025 | neutral_proe | 8 | 0.1022 | 0.1055 | -0.00069 [-0.00126, -0.00011] |
| 2025 | td_per_drive | 4 | 0.1320 | 0.1351 | -0.00084 [-0.00151, -0.00019] |

