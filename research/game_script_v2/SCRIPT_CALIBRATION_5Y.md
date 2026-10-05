# GAME SCRIPT V2: five-season script calibration (2021-2025)

Generated from `script_calibration_5y.json and validation_5y.json` by `scripts/sim/write_game_script_v2.py` -- do not edit by hand. **RESEARCH_ONLY: no betting authority.**

Reproduce: `python scripts/sim/script_backtest.py` after the five-season walk-forward. Every game's nine-cell distribution comes from the SAME simulated rows that were scored in `BASELINE_5Y.md`; the realized game is classified by the same function with the same centre. Baselines are fitted on training seasons only (2016..Y-1): B0 = unconditional cell frequencies, B1 = frequencies within the absolute closing-spread bucket. Provenance: **MARKET_CENTRED_GAME** -- the nine-cell lattice is the market centre plus the incumbent's residual bank: a test of that bank, not of the volume or player models.

## Verdict: **NEEDS_MORE_WORK**

- pooled_brier_better_than_B0: **True**
- pooled_brier_not_worse_than_B1: **True**
- pooled_ece_within_null_95: **True**
- no_season_worse_than_B0: **False**

## Multiclass scores

| season | games | Brier model / B0 / B1 | model − B0 [95% CI] | model − B1 [95% CI] | log loss model / B0 / B1 | top-script p | top-script hit | entropy | ECE model (null 95%) |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 285 | 0.8368 / 0.8573 / 0.8396 | -0.0205 [-0.0314, -0.0096] | -0.0028 [-0.0105, 0.0052] | 1.9870 / 2.0492 / 1.9908 | 0.289 | 0.288 | 1.946 | 0.0040 (0.0154) |
| 2022 | 284 | 0.8222 / 0.8148 / 0.8141 | 0.0074 [-0.0043, 0.0187] | 0.0081 [-0.0001, 0.0161] | 1.9318 / 1.9097 / 1.9041 | 0.276 | 0.342 | 1.978 | 0.0128 (0.0148) |
| 2023 | 285 | 0.8205 / 0.8252 / 0.8183 | -0.0046 [-0.0145, 0.0056] | 0.0023 [-0.0042, 0.0091] | 1.9153 / 1.9261 / 1.9088 | 0.289 | 0.309 | 1.957 | 0.0078 (0.0152) |
| 2024 | 285 | 0.8048 / 0.8146 / 0.8064 | -0.0098 [-0.0192, -0.0003] | -0.0016 [-0.0087, 0.0053] | 1.8475 / 1.8951 / 1.8630 | 0.283 | 0.337 | 1.958 | 0.0153 (0.0146) |
| 2025 | 285 | 0.8234 / 0.8313 / 0.8220 | -0.0079 [-0.0200, 0.0030] | 0.0014 [-0.0059, 0.0086] | 1.9314 / 1.9543 / 1.9243 | 0.307 | 0.291 | 1.912 | 0.0051 (0.0154) |
| pooled | 1424 | 0.8215 / 0.8286 / 0.8201 | -0.0071 [-0.0119, -0.0026] | 0.0015 [-0.0019, 0.0048] | 1.9226 / 1.9469 / 1.9182 | 0.289 | 0.313 | 1.950 | 0.0053 (0.0070) |

## Predicted vs realized frequency by cell (pooled)

| cell | model | realized | B0 | B1 |
|---|---|---|---|---|
| FAVORITE_CONTROL|HIGH_SCORING | 8.9% | 7.9% | 7.3% | 7.1% |
| FAVORITE_CONTROL|NORMAL_SCORING | 21.3% | 19.5% | 19.6% | 19.1% |
| FAVORITE_CONTROL|LOW_SCORING | 8.3% | 7.0% | 7.9% | 7.8% |
| COMPETITIVE|HIGH_SCORING | 10.8% | 12.1% | 12.0% | 12.0% |
| COMPETITIVE|NORMAL_SCORING | 26.2% | 29.6% | 28.5% | 28.4% |
| COMPETITIVE|LOW_SCORING | 10.7% | 11.8% | 11.9% | 12.0% |
| UNDERDOG_CONTROL|HIGH_SCORING | 3.3% | 2.5% | 3.1% | 3.3% |
| UNDERDOG_CONTROL|NORMAL_SCORING | 7.6% | 7.2% | 6.7% | 6.9% |
| UNDERDOG_CONTROL|LOW_SCORING | 2.9% | 2.3% | 3.2% | 3.3% |

## Reliability (pooled, one-vs-rest over all nine cells)

| bin | n | mean p | realized |
|---|---|---|---|
| 0.0-0.1 | 6905 | 0.055 | 0.051 |
| 0.1-0.2 | 3986 | 0.131 | 0.129 |
| 0.2-0.3 | 1545 | 0.258 | 0.274 |
| 0.3-0.4 | 361 | 0.326 | 0.349 |
| 0.4-0.5 | 19 | 0.425 | 0.421 |

## Marginal events (Brier; pooled, game-clustered 95% CI)

| event | n | mean p | rate | Brier model | Brier B0 | Brier B1 | model − B0 | model − B1 |
|---|---|---|---|---|---|---|---|---|
| one_score | 1424 | 0.477 | 0.536 | 0.2441 | 0.2490 | 0.2423 | -0.0049 [-0.0091, -0.0005] | 0.0018 [-0.0014, 0.0050] |
| blowout_17 | 1424 | 0.235 | 0.263 | 0.1899 | 0.1941 | 0.1890 | -0.0042 [-0.0074, -0.0011] | 0.0009 [-0.0009, 0.0026] |
| favorite_wins | 1424 | 0.670 | 0.663 | 0.2129 | 0.2236 | 0.2144 | -0.0107 [-0.0147, -0.0069] | -0.0015 [-0.0040, 0.0011] |
| favorite_controls | 1424 | 0.385 | 0.345 | 0.2114 | 0.2260 | 0.2119 | -0.0146 [-0.0204, -0.0089] | -0.0005 [-0.0037, 0.0027] |
| upset | 1424 | 0.327 | 0.334 | 0.2118 | 0.2226 | 0.2131 | -0.0109 [-0.0148, -0.0070] | -0.0013 [-0.0038, 0.0011] |
| shootout | 1424 | 0.230 | 0.225 | 0.1752 | 0.1746 | 0.1748 | 0.0006 [-0.0002, 0.0013] | 0.0004 [-0.0006, 0.0013] |
| low_scoring | 1424 | 0.219 | 0.211 | 0.1674 | 0.1670 | 0.1673 | 0.0004 [-0.0007, 0.0015] | 0.0001 [-0.0016, 0.0018] |
| low_possession | 1424 | 0.095 | 0.086 | 0.0763 | 0.0795 | 0.0792 | -0.0032 [-0.0056, -0.0010] | -0.0030 [-0.0053, -0.0008] |
| high_volume_passing | 1424 | 0.101 | 0.129 | 0.1023 | 0.1142 | 0.1148 | -0.0119 [-0.0163, -0.0078] | -0.0125 [-0.0169, -0.0084] |
| run_heavy_control | 1424 | 0.165 | 0.141 | 0.1193 | 0.1213 | 0.1211 | -0.0020 [-0.0043, 0.0004] | -0.0018 [-0.0039, 0.0004] |

Calibration in the large (pooled): mean forecast − realized rate, in binomial standard errors of the rate.

| event | mean p − rate | z |
|---|---|---|
| one_score | -0.0584 | -4.4 |
| blowout_17 | -0.0281 | -2.4 |
| favorite_wins | +0.0072 | +0.6 |
| favorite_controls | +0.0401 | +3.2 |
| upset | -0.0068 | -0.5 |
| shootout | +0.0045 | +0.4 |
| low_scoring | +0.0076 | +0.7 |
| low_possession | +0.0097 | +1.3 |
| high_volume_passing | -0.0279 | -3.1 |
| run_heavy_control | +0.0237 | +2.6 |

Per season (model − B1 Brier, mean):

| event | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| one_score | -0.0034 | 0.0073 | 0.0019 | 0.0014 | 0.0019 |
| blowout_17 | 0.0020 | 0.0017 | -0.0001 | -0.0004 | 0.0011 |
| favorite_wins | 0.0009 | 0.0015 | -0.0008 | -0.0068 | -0.0023 |
| favorite_controls | 0.0006 | 0.0015 | 0.0005 | -0.0021 | -0.0031 |
| upset | 0.0009 | 0.0015 | -0.0005 | -0.0068 | -0.0018 |
| shootout | -0.0004 | 0.0027 | 0.0010 | -0.0010 | -0.0003 |
| low_scoring | -0.0034 | 0.0034 | 0.0021 | -0.0012 | -0.0004 |
| low_possession | -0.0018 | -0.0006 | 0.0006 | -0.0006 | -0.0123 |
| high_volume_passing | -0.0256 | -0.0130 | -0.0077 | -0.0113 | -0.0049 |
| run_heavy_control | -0.0066 | -0.0043 | 0.0019 | -0.0021 | 0.0020 |

Favourite events exclude pick'em games (no favourite); volume events use the play-by-play team-game table. The nine cells and the score events are a test of the market centre plus the residual bank; low_possession, high_volume_passing and run_heavy_control also test the volume model.

## POST-HOC: the shape of the simulated final margin

**POST_HOC_DESCRIPTIVE** -- not preregistered; examined because `one_score` was under-forecast in every season. The (margin, total) of every simulated row is the market centre plus a historical residual drawn from the incumbent's `pricing/game_env.ResidualBank`. Adding a residual to the target spread is translation-invariant, so the NFL's key-number structure (final margins of exactly 3 and 7) is smeared into the 9-16 band. This concerns the incumbent's game-environment shape, which this study does not change; a key-number-aware margin model is a separate, to-be-preregistered research item.

| |m| | predicted (pooled) | realized (pooled) ± SE | 2021 pred / real | 2022 pred / real | 2023 pred / real | 2024 pred / real | 2025 pred / real |
|---|---|---|---|---|---|---|---|
| |m| 0-3 | 20.0% | 25.6% ± 1.2% | 19% / 24% | 20% / 27% | 20% / 26% | 21% / 24% | 20% / 27% |
| |m| 4-8 | 27.8% | 27.9% ± 1.2% | 27% / 24% | 27% / 31% | 28% / 28% | 28% / 31% | 28% / 26% |
| |m| 9-16 | 28.8% | 20.2% ± 1.1% | 29% / 24% | 29% / 23% | 29% / 18% | 28% / 17% | 28% / 19% |
| |m| 17-+ | 23.5% | 26.3% ± 1.2% | 25% / 28% | 24% / 19% | 22% / 28% | 23% / 28% | 23% / 28% |
| |m| = 3 | 7.9% | 15.4% ± 1.0% | 8% / 15% | 8% / 17% | 8% / 15% | 8% / 14% | 8% / 16% |
| |m| = 7 | 5.5% | 7.8% ± 0.7% | 5% / 7% | 6% / 8% | 6% / 8% | 6% / 7% | 5% / 9% |
| |m| = 10 | 4.4% | 4.6% ± 0.6% | 4% / 6% | 5% / 5% | 4% / 4% | 4% / 5% | 4% / 4% |
| |m| = 14 | 3.4% | 4.3% ± 0.5% | 4% / 3% | 3% / 5% | 3% / 7% | 3% / 2% | 3% / 4% |

## Score-path research arm P1 (preregistered; not part of GAME SCRIPT V2)

**Verdict: REJECTED.** P1 averages, over the simulated rows, a kernel conditional of each path event on the row's final margin and scoring cell (training games only); the baseline is the training frequency in the signed closing-spread bucket. 2761 games with quarter scores; 15 where the play-by-play running score's final differs from the schedule final (kept and counted).

| target | metric | P1 | baseline | P1 − baseline [95% CI] | beats baseline |
|---|---|---|---|---|---|
| home_leads_half | Brier | 0.2350 | 0.2373 | -0.0023 [-0.0042, -0.0005] | True |
| home_leads_q3 | Brier | 0.2260 | 0.2285 | -0.0025 [-0.0045, -0.0006] | True |
| early_blowout | Brier | 0.1266 | 0.1269 | -0.0003 [-0.0014, 0.0008] | False |
| late_comeback | Brier | 0.0574 | 0.0575 | -0.0002 [-0.0004, 0.0002] | False |
| lead_changes_2plus | Brier | 0.2222 | 0.2241 | -0.0018 [-0.0042, 0.0004] | False |
| margin_half | CRPS | 5.6400 | 5.6885 | -0.0485 [-0.0803, -0.0164] | True |
| margin_q3 | CRPS | 6.6841 | 6.7398 | -0.0557 [-0.1021, -0.0101] | True |

Lead changes, time leading, early blowouts and late comebacks therefore stay `not_simulated` in GAME SCRIPT V2.

