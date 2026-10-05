# Five-season baseline of the frozen incumbent simulation (2021-2025)

Generated from `baseline_5y.json` by `scripts/sim/write_game_script_v2.py` -- do not edit by hand. **RESEARCH_ONLY: no betting authority.**

Reproduce: `python scripts/sim/baseline_5y.py --seasons 2021,2022,2023,2024,2025 --n-sims 10000` (equivalent to `python scripts/sim/walkforward.py --seasons 2021,2022,2023,2024,2025 --n-sims 10000 --out-dir DIR`), then `python scripts/sim/game_script_v2_report.py baseline`. Starting point: `main` at `d5c7f8dfa014b9be3aff7550734b6208e7314554`. 10,000 simulated rows per game; game-clustered bootstrap (2000 resamples, seed 20261005).

Walk-forward exactly as the incumbent: for evaluation season Y the shrinkage priors are fitted on 2016..Y-1, the frames are rebuilt for Y, the bundle is fitted on 2018..Y-1 (2016-17 warm the EWMAs), every completed game of Y is simulated with the consensus CLOSING line as the market centre, and every (game, player, statistic) row is scored against the box score. Nothing was tuned on these results.

## Evidence classes

| season | class | games | simulated | skipped | coherence failures | bundle trained on | priors fitted on |
|---|---|---|---|---|---|---|---|
| 2021 | RETROSPECTIVE_CHALLENGE | 285 | 285 | 0 | 0 | 2018-2020 | 2016-2020 |
| 2022 | RETROSPECTIVE_CHALLENGE | 284 | 284 | 0 | 0 | 2018-2021 | 2016-2021 |
| 2023 | RETROSPECTIVE_DEVELOPMENT | 285 | 285 | 0 | 0 | 2018-2022 | 2016-2022 |
| 2024 | RETROSPECTIVE_DEVELOPMENT | 285 | 285 | 0 | 0 | 2018-2023 | 2016-2023 |
| 2025 | RETROSPECTIVE_DEVELOPMENT | 285 | 285 | 0 | 0 | 2018-2024 | 2016-2024 |

2022 has 284 games: the cancelled Week 17 BUF @ CIN game is not in the nflverse schedule (never played; not an exclusion). 2021-2022 are a RETROSPECTIVE CHALLENGE set -- never scored by this layer before, but every design choice was available when they were run. Nothing here is prospective evidence.

## Reproduction of the committed 2023-2025 run

Game environment, efficiency, touchdown and QB-share models reproduce bit for bit, and so does every team-level volume, points and touchdown metric; team passing / rushing yards (sums of player yards) move with the player allocation. The opportunity share models agree to floating-point precision. The one material difference is other_share (the share of team volume outside the eligible set), whose sign flips: nflverse has since rebuilt snap_counts_2020 with compound position labels (616 rows, e.g. FB/D; no other season has any), such a player falls out of the skill filter, his eligible row merges to NaN team volume, and assemble's fillna(0) followed by groupby 'first' reads the team's volume as 0 whenever that row sorts first. Falling back to the roster position moves other_share but does not restore the committed bundle, so the original bytes differed in more than the labels and cannot be recovered (the repository records no checksum of the old file). The frozen baseline is therefore run on today's vintage unchanged, and the aggregation repair is a registered candidate (R1).

| season | bundle components that moved | other_share committed → reproduced (carry / target) | team stats that moved | max |rel. change| MAE / CRPS / cover90 |
|---|---|---|---|---|
| 2023 | carry_share, other_share, sim_version, target_share | 0.0055 / 0.0025 → -0.0053 / -0.0046 | pass_yards, rush_yards | 0.32% / 0.62% / 0.84% |
| 2024 | carry_share, other_share, sim_version, target_share | 0.0048 / 0.0022 → -0.0042 / -0.0037 | pass_yards, rush_yards | 0.28% / 0.42% / 0.61% |
| 2025 | carry_share, other_share, sim_version, target_share | 0.0042 / 0.0020 → -0.0034 / -0.0031 | pass_yards, rush_yards | 0.09% / 0.22% / 0.40% |

`sim_version` differs only because the committed bundles predate the additive sim-1.1.0 label. The 2023 and 2024 seasons of the five-season run below are bit-identical to an unmodified-code reproduction (same bundle, same evaluation), which shows the GAME SCRIPT V2 hook and the research-arm plumbing change nothing.

## Player projections by season

Rows are `backtest.evaluate`'s scored population (predictive mean above a per-statistic floor). Coverage counts an integer outcome on the interval endpoint as covered, so it overstates calibration for small counts; the randomized PIT χ² (10 bins; 16.9 is the 5% critical value at df 9) is the honest uniformity check.

### 2021 (RETROSPECTIVE_CHALLENGE)

| statistic | n | games | MAE | naive MAE | Δ% vs naive | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier | randomized-PIT χ² (df 9) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1608 | 285 | 3.776 | 4.388 | -14.0 | 4.887 | -0.170 | 2.628 | 0.626 | 0.960 | 0.0838 | 41.6 |
| rush_yards | 1631 | 285 | 20.583 | 23.189 | -11.2 | 27.523 | -0.231 | 14.307 | 0.566 | 0.944 | 0.0908 | 18.3 |
| targets | 3577 | 285 | 2.123 | 2.167 | -2.0 | 2.695 | 0.015 | 1.509 | 0.718 | 0.988 | 0.1088 | 335.5 |
| receptions | 3384 | 285 | 1.647 | 1.671 | -1.5 | 2.087 | 0.034 | 1.151 | 0.741 | 0.986 | 0.1038 | 188.5 |
| rec_yards | 3807 | 285 | 21.209 | 21.592 | -1.8 | 28.190 | 0.479 | 14.569 | 0.658 | 0.959 | 0.0918 | 109.4 |
| attempts | 570 | 285 | 8.037 | 8.392 | -4.2 | 11.149 | 2.077 | 6.009 | 0.511 | 0.847 | 0.1201 | 34.8 |
| completions | 570 | 285 | 5.615 | 5.733 | -2.0 | 7.625 | 1.287 | 4.168 | 0.525 | 0.856 | 0.1087 | 42.7 |
| pass_yards | 570 | 285 | 67.394 | 68.323 | -1.4 | 88.069 | 15.870 | 48.935 | 0.489 | 0.867 | 0.1315 | 31.0 |
| pass_td | 570 | 285 | 0.921 | — | — | 1.118 | 0.142 | 0.605 | 0.726 | 0.981 | 0.1479 | 12.4 |
| any_td | 4697 | 285 | 0.388 | — | — | 0.525 | 0.012 | 0.203 | 0.872 | 0.984 | 0.0990 | 8.0 |

### 2022 (RETROSPECTIVE_CHALLENGE)

| statistic | n | games | MAE | naive MAE | Δ% vs naive | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier | randomized-PIT χ² (df 9) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1603 | 284 | 3.590 | 4.136 | -13.2 | 4.668 | -0.148 | 2.527 | 0.641 | 0.968 | 0.0808 | 74.3 |
| rush_yards | 1666 | 284 | 21.387 | 23.317 | -8.3 | 28.821 | -0.865 | 14.773 | 0.559 | 0.936 | 0.0939 | 25.7 |
| targets | 3427 | 284 | 2.107 | 2.151 | -2.1 | 2.691 | -0.073 | 1.498 | 0.722 | 0.987 | 0.1076 | 293.3 |
| receptions | 3190 | 284 | 1.659 | 1.686 | -1.6 | 2.122 | -0.059 | 1.164 | 0.731 | 0.985 | 0.1050 | 165.2 |
| rec_yards | 3617 | 284 | 20.798 | 21.363 | -2.6 | 27.571 | -0.507 | 14.305 | 0.659 | 0.964 | 0.0904 | 135.6 |
| attempts | 568 | 284 | 8.367 | 8.560 | -2.3 | 11.664 | 2.003 | 6.276 | 0.498 | 0.842 | 0.1191 | 42.7 |
| completions | 568 | 284 | 5.665 | 5.732 | -1.2 | 7.700 | 1.355 | 4.213 | 0.523 | 0.829 | 0.1071 | 32.8 |
| pass_yards | 568 | 284 | 65.201 | 67.125 | -2.9 | 87.409 | 12.648 | 48.229 | 0.526 | 0.852 | 0.1217 | 25.3 |
| pass_td | 568 | 284 | 0.888 | — | — | 1.061 | 0.145 | 0.571 | 0.773 | 0.984 | 0.1414 | 19.4 |
| any_td | 4513 | 284 | 0.375 | — | — | 0.514 | 0.007 | 0.196 | 0.872 | 0.981 | 0.0954 | 7.5 |

### 2023 (RETROSPECTIVE_DEVELOPMENT)

| statistic | n | games | MAE | naive MAE | Δ% vs naive | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier | randomized-PIT χ² (df 9) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1619 | 285 | 3.498 | 4.115 | -15.0 | 4.553 | 0.074 | 2.459 | 0.648 | 0.966 | 0.0785 | 66.6 |
| rush_yards | 1677 | 285 | 19.516 | 21.693 | -10.0 | 25.883 | 1.577 | 13.421 | 0.577 | 0.943 | 0.0853 | 21.3 |
| targets | 3307 | 285 | 2.053 | 2.105 | -2.4 | 2.643 | -0.108 | 1.475 | 0.719 | 0.987 | 0.1063 | 337.6 |
| receptions | 3097 | 285 | 1.625 | 1.647 | -1.3 | 2.100 | -0.112 | 1.153 | 0.739 | 0.987 | 0.1037 | 218.7 |
| rec_yards | 3481 | 285 | 21.276 | 21.809 | -2.4 | 28.946 | -1.547 | 14.812 | 0.636 | 0.953 | 0.0932 | 141.2 |
| attempts | 570 | 285 | 8.195 | 8.708 | -5.9 | 11.309 | 1.510 | 6.112 | 0.468 | 0.849 | 0.1170 | 29.6 |
| completions | 570 | 285 | 5.720 | 6.004 | -4.7 | 7.630 | 0.777 | 4.227 | 0.481 | 0.840 | 0.1062 | 37.6 |
| pass_yards | 570 | 285 | 69.590 | 72.417 | -3.9 | 89.256 | 6.063 | 50.618 | 0.472 | 0.842 | 0.1257 | 42.1 |
| pass_td | 570 | 285 | 0.842 | — | — | 1.038 | 0.074 | 0.553 | 0.796 | 0.977 | 0.1367 | 5.5 |
| any_td | 4333 | 285 | 0.370 | — | — | 0.502 | 0.001 | 0.194 | 0.876 | 0.985 | 0.0948 | 23.8 |

### 2024 (RETROSPECTIVE_DEVELOPMENT)

| statistic | n | games | MAE | naive MAE | Δ% vs naive | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier | randomized-PIT χ² (df 9) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1632 | 285 | 3.524 | 4.031 | -12.6 | 4.550 | -0.035 | 2.457 | 0.631 | 0.969 | 0.0792 | 52.8 |
| rush_yards | 1686 | 285 | 21.039 | 22.697 | -7.3 | 28.102 | -0.655 | 14.546 | 0.554 | 0.936 | 0.0916 | 11.4 |
| targets | 3355 | 285 | 2.033 | 2.137 | -4.8 | 2.653 | -0.127 | 1.466 | 0.732 | 0.981 | 0.1055 | 354.9 |
| receptions | 3140 | 285 | 1.622 | 1.660 | -2.3 | 2.093 | -0.152 | 1.152 | 0.734 | 0.979 | 0.1038 | 201.7 |
| rec_yards | 3577 | 285 | 20.705 | 21.286 | -2.7 | 27.797 | -1.481 | 14.427 | 0.648 | 0.958 | 0.0911 | 146.1 |
| attempts | 570 | 285 | 8.413 | 8.930 | -5.8 | 11.613 | 2.162 | 6.325 | 0.460 | 0.823 | 0.1208 | 49.5 |
| completions | 570 | 285 | 5.758 | 5.996 | -4.0 | 7.653 | 1.053 | 4.245 | 0.481 | 0.844 | 0.1051 | 35.6 |
| pass_yards | 570 | 285 | 68.754 | 70.287 | -2.2 | 88.805 | 8.841 | 49.967 | 0.470 | 0.860 | 0.1245 | 20.9 |
| pass_td | 570 | 285 | 0.914 | — | — | 1.115 | 0.033 | 0.597 | 0.756 | 0.961 | 0.1459 | 9.4 |
| any_td | 4414 | 285 | 0.384 | — | — | 0.524 | -0.017 | 0.209 | 0.858 | 0.982 | 0.1020 | 18.2 |

### 2025 (RETROSPECTIVE_DEVELOPMENT)

| statistic | n | games | MAE | naive MAE | Δ% vs naive | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier | randomized-PIT χ² (df 9) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carries | 1582 | 285 | 3.394 | 4.223 | -19.6 | 4.418 | -0.063 | 2.406 | 0.661 | 0.971 | 0.0780 | 57.4 |
| rush_yards | 1649 | 285 | 20.348 | 22.929 | -11.4 | 27.547 | 0.382 | 14.045 | 0.569 | 0.936 | 0.0882 | 13.4 |
| targets | 3290 | 285 | 2.014 | 2.099 | -4.0 | 2.582 | 0.099 | 1.433 | 0.736 | 0.987 | 0.1036 | 338.0 |
| receptions | 3075 | 285 | 1.561 | 1.602 | -2.5 | 1.998 | 0.106 | 1.095 | 0.764 | 0.987 | 0.0988 | 222.6 |
| rec_yards | 3523 | 285 | 20.459 | 21.096 | -2.9 | 27.215 | 0.303 | 14.115 | 0.664 | 0.957 | 0.0894 | 122.2 |
| attempts | 570 | 285 | 7.031 | 7.781 | -9.6 | 9.219 | 0.734 | 5.092 | 0.493 | 0.882 | 0.1078 | 14.4 |
| completions | 570 | 285 | 4.745 | 5.226 | -9.2 | 6.207 | 0.733 | 3.420 | 0.537 | 0.904 | 0.0940 | 9.5 |
| pass_yards | 570 | 285 | 60.183 | 64.713 | -7.0 | 76.969 | 3.615 | 42.968 | 0.519 | 0.904 | 0.1206 | 13.9 |
| pass_td | 570 | 285 | 0.910 | — | — | 1.108 | -0.028 | 0.604 | 0.719 | 0.975 | 0.1487 | 4.1 |
| any_td | 4349 | 285 | 0.395 | — | — | 0.536 | -0.005 | 0.213 | 0.865 | 0.984 | 0.1029 | 11.4 |

### Pooled 2021-2025 (game-clustered 95% intervals)

| statistic | n | games | MAE | naive MAE | Δ% vs naive | RMSE | bias | CRPS | cover50 | cover90 | ladder Brier | randomized-PIT χ² (df 9) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carries | 8044 | 1424 | 3.557 | 4.178 | -14.9 | 4.618 | -0.068 | 2.495 | 0.641 | 0.967 | 0.0800 | 246.0 |
| rush_yards | 8309 | 1424 | 20.575 | 22.761 | -9.6 | 27.592 | 0.042 | 14.218 | 0.565 | 0.939 | 0.0900 | 54.2 |
| targets | 16956 | 1424 | 2.067 | 2.132 | -3.0 | 2.654 | -0.039 | 1.477 | 0.725 | 0.986 | 0.1064 | 1629.6 |
| receptions | 15886 | 1424 | 1.624 | 1.654 | -1.8 | 2.081 | -0.036 | 1.143 | 0.742 | 0.985 | 0.1031 | 945.6 |
| rec_yards | 18005 | 1424 | 20.892 | 21.430 | -2.5 | 27.949 | -0.535 | 14.446 | 0.653 | 0.958 | 0.0912 | 617.2 |
| attempts | 2848 | 1424 | 8.008 | 8.474 | -5.5 | 11.028 | 1.697 | 5.962 | 0.486 | 0.849 | 0.1169 | 124.8 |
| completions | 2848 | 1424 | 5.501 | 5.738 | -4.1 | 7.386 | 1.041 | 4.054 | 0.509 | 0.855 | 0.1042 | 111.2 |
| pass_yards | 2848 | 1424 | 66.225 | 68.574 | -3.4 | 86.224 | 9.405 | 48.143 | 0.495 | 0.865 | 0.1248 | 76.5 |
| pass_td | 2848 | 1424 | 0.895 | — | — | 1.089 | 0.073 | 0.586 | 0.754 | 0.976 | 0.1441 | 17.6 |
| any_td | 22306 | 1424 | 0.383 | — | — | 0.520 | -0.000 | 0.203 | 0.869 | 0.983 | 0.0988 | 31.2 |

| statistic | MAE [95% CI] | MAE − naive MAE [95% CI] | CRPS [95% CI] | cover50 [95% CI] | cover90 [95% CI] |
|---|---|---|---|---|---|
| carries | 3.557 [3.496, 3.617] | -0.621 [-0.680, -0.563] | 2.495 [2.456, 2.533] | 0.641 [0.631, 0.652] | 0.967 [0.963, 0.971] |
| rush_yards | 20.575 [20.195, 20.977] | -2.193 [-2.478, -1.925] | 14.218 [13.946, 14.505] | 0.565 [0.555, 0.575] | 0.939 [0.934, 0.944] |
| targets | 2.067 [2.041, 2.093] | -0.065 [-0.078, -0.051] | 1.477 [1.459, 1.494] | 0.725 [0.718, 0.732] | 0.986 [0.984, 0.988] |
| receptions | 1.624 [1.602, 1.643] | -0.030 [-0.040, -0.021] | 1.143 [1.130, 1.157] | 0.742 [0.735, 0.749] | 0.985 [0.983, 0.987] |
| rec_yards | 20.892 [20.614, 21.173] | -0.532 [-0.640, -0.423] | 14.446 [14.243, 14.644] | 0.653 [0.646, 0.660] | 0.958 [0.955, 0.961] |
| attempts | 8.008 [7.749, 8.292] | -0.466 [-0.680, -0.248] | 5.962 [5.749, 6.191] | 0.486 [0.468, 0.504] | 0.849 [0.835, 0.861] |
| completions | 5.501 [5.326, 5.685] | -0.238 [-0.373, -0.102] | 4.054 [3.919, 4.198] | 0.509 [0.491, 0.526] | 0.855 [0.841, 0.867] |
| pass_yards | 66.225 [64.282, 68.281] | -2.349 [-3.894, -0.918] | 48.143 [46.703, 49.650] | 0.495 [0.476, 0.514] | 0.865 [0.852, 0.878] |
| pass_td | 0.895 [0.872, 0.917] | — | 0.586 [0.570, 0.602] | 0.754 [0.739, 0.771] | 0.976 [0.970, 0.981] |
| any_td | 0.383 [0.378, 0.387] | — | 0.203 [0.199, 0.207] | 0.869 [0.864, 0.873] | 0.983 [0.982, 0.985] |

## Calibration shape (pooled randomized PIT)

Bin heights relative to uniform (1.00). Shape is read by a fixed rule: OVER-DISPERSED (forecast too wide) when the two edge bins average below 0.8 and the middle four above 1.1; UNDER-DISPERSED when BOTH edge bins exceed 1.15; LEFT-TAIL HEAVY / RIGHT-TAIL HEAVY when the lowest / highest bin exceeds 1.25; otherwise NEAR-UNIFORM.

| statistic | PIT bins (relative) | P(PIT < 0.05) | P(PIT > 0.95) | χ² | shape |
|---|---|---|---|---|---|
| carries | 0.86 0.83 0.87 0.97 1.12 1.24 1.15 1.17 1.11 0.68 | 0.045 | 0.023 | 246.0 | OVER-DISPERSED |
| rush_yards | 0.94 0.91 0.99 1.01 0.97 1.05 1.08 1.15 1.03 0.86 | 0.047 | 0.035 | 54.2 | NEAR-UNIFORM |
| targets | 0.50 0.70 0.89 1.08 1.21 1.29 1.38 1.33 1.08 0.54 | 0.025 | 0.017 | 1629.6 | OVER-DISPERSED |
| receptions | 0.62 0.73 0.90 1.03 1.17 1.27 1.25 1.26 1.12 0.65 | 0.030 | 0.022 | 945.6 | OVER-DISPERSED |
| rec_yards | 0.66 0.78 0.94 1.05 1.13 1.18 1.18 1.19 1.11 0.79 | 0.032 | 0.033 | 617.2 | OVER-DISPERSED |
| attempts | 1.62 1.00 0.88 0.94 0.87 0.90 0.92 0.92 1.00 0.95 | 0.107 | 0.053 | 124.8 | LEFT-TAIL HEAVY |
| completions | 1.57 1.00 0.81 0.88 0.97 0.90 0.95 1.00 1.00 0.92 | 0.110 | 0.048 | 111.2 | LEFT-TAIL HEAVY |
| pass_yards | 1.39 0.88 0.85 0.84 0.97 1.03 1.07 1.05 1.11 0.81 | 0.104 | 0.032 | 76.5 | LEFT-TAIL HEAVY |
| pass_td | 1.06 1.13 1.10 0.99 0.95 0.96 1.01 1.03 0.87 0.90 | 0.050 | 0.046 | 17.6 | NEAR-UNIFORM |
| any_td | 0.97 0.98 1.00 1.00 0.95 1.00 1.06 1.04 1.05 0.94 | 0.048 | 0.045 | 31.2 | NEAR-UNIFORM |

## Season-to-season instability (CRPS)

| statistic | 2021 | 2022 | 2023 | 2024 | 2025 | max/min |
|---|---|---|---|---|---|---|
| carries | 2.628 | 2.527 | 2.459 | 2.457 | 2.406 | 1.092 |
| rush_yards | 14.307 | 14.773 | 13.421 | 14.546 | 14.045 | 1.101 |
| targets | 1.509 | 1.498 | 1.475 | 1.466 | 1.433 | 1.053 |
| receptions | 1.151 | 1.164 | 1.153 | 1.152 | 1.095 | 1.063 |
| rec_yards | 14.569 | 14.305 | 14.812 | 14.427 | 14.115 | 1.049 |
| attempts | 6.009 | 6.276 | 6.112 | 6.325 | 5.092 | 1.242 |
| completions | 4.168 | 4.213 | 4.227 | 4.245 | 3.420 | 1.241 |
| pass_yards | 48.935 | 48.229 | 50.618 | 49.967 | 42.968 | 1.178 |
| pass_td | 0.605 | 0.571 | 0.553 | 0.597 | 0.604 | 1.094 |
| any_td | 0.203 | 0.196 | 0.194 | 0.209 | 0.213 | 1.095 |

## Team level

| season | plays CRPS / cover90 | pass_att CRPS / cover90 | rush_att CRPS / cover90 | dropbacks CRPS / cover90 | points CRPS / cover90 |
|---|---|---|---|---|---|
| 2021 | 4.783 / 0.921 | 4.556 / 0.886 | 4.239 / 0.916 | 4.860 / 0.900 | 5.382 / 0.902 |
| 2022 | 4.545 / 0.930 | 4.395 / 0.894 | 4.120 / 0.908 | 4.733 / 0.905 | 4.965 / 0.923 |
| 2023 | 4.731 / 0.918 | 4.207 / 0.909 | 4.100 / 0.918 | 4.486 / 0.925 | 5.204 / 0.932 |
| 2024 | 4.686 / 0.925 | 4.322 / 0.893 | 3.970 / 0.925 | 4.612 / 0.900 | 5.026 / 0.926 |
| 2025 | 4.782 / 0.904 | 4.321 / 0.900 | 3.990 / 0.911 | 4.585 / 0.900 | 5.127 / 0.926 |
| pooled | 4.706 / 0.919 | 4.360 / 0.896 | 4.084 / 0.915 | 4.655 / 0.906 | 5.141 / 0.922 |

## Eligibility and missing data

| season | eligible rows | team-games with a set | questionable | no prior history | no depth-chart rank | realized carries / targets / attempts covered | players with touches outside the set | sim QB1 = leading passer |
|---|---|---|---|---|---|---|---|---|
| 2021 | 7983 | 570 / 570 | 318 | 246 | 1035 | 99.9% / 99.9% / 99.9% | 50 | 529/570 (92.8%) |
| 2022 | 7906 | 568 / 568 | 326 | 217 | 848 | 99.9% / 99.9% / 100.0% | 36 | 521/568 (91.7%) |
| 2023 | 7873 | 570 / 570 | 327 | 179 | 829 | 99.9% / 99.9% / 100.0% | 34 | 516/570 (90.5%) |
| 2024 | 7887 | 570 / 570 | 263 | 217 | 917 | 99.9% / 99.9% / 99.9% | 40 | 514/570 (90.2%) |
| 2025 | 7886 | 570 / 570 | 253 | 250 | 364 | 99.9% / 99.9% / 100.0% | 27 | 549/570 (96.3%) |

## Where the error is (decomposition)

Sequential substitution along TEAM VOLUME -> PLAYER SHARE -> EFFICIENCY per player-game: component errors are `C·s·e − μ`, `c·e − C·s·e`, `y − c·e` (C team volume, c player opportunity, s expected share, e expected per-opportunity yield). Shares of the summed squared error; the remainder is covariance.

| season | statistic | n | team volume | player share | efficiency | covariance |
|---|---|---|---|---|---|---|
| 2021 | rush_yards | 1631 | 16% | 47% | 37% | 0% |
| 2021 | rec_yards | 3807 | 10% | 42% | 55% | -7% |
| 2021 | receptions | 3384 | 14% | 64% | 25% | -4% |
| 2021 | pass_yards | 570 | 40% | 45% | 41% | -27% |
| 2022 | rush_yards | 1666 | 14% | 36% | 42% | 8% |
| 2022 | rec_yards | 3617 | 9% | 42% | 52% | -3% |
| 2022 | receptions | 3190 | 13% | 61% | 24% | 1% |
| 2022 | pass_yards | 568 | 37% | 50% | 33% | -19% |
| 2023 | rush_yards | 1677 | 17% | 43% | 40% | -0% |
| 2023 | rec_yards | 3481 | 8% | 37% | 58% | -3% |
| 2023 | receptions | 3097 | 12% | 60% | 25% | 3% |
| 2023 | pass_yards | 570 | 31% | 47% | 37% | -14% |
| 2024 | rush_yards | 1686 | 14% | 37% | 42% | 7% |
| 2024 | rec_yards | 3577 | 9% | 40% | 54% | -3% |
| 2024 | receptions | 3140 | 14% | 61% | 24% | 1% |
| 2024 | pass_yards | 570 | 34% | 49% | 34% | -17% |
| 2025 | rush_yards | 1649 | 16% | 36% | 49% | -1% |
| 2025 | rec_yards | 3523 | 10% | 40% | 54% | -4% |
| 2025 | receptions | 3075 | 16% | 62% | 25% | -3% |
| 2025 | pass_yards | 570 | 44% | 22% | 46% | -12% |

Player share is the largest component for receptions and rushing yards in every season; for passing yards it is the starter's share of team attempts, i.e. starter identification and in-game exits. Efficiency covariates were already shown not to move rushing efficiency (`research/simulation_engine/RUSHING_ABLATION.md`).

