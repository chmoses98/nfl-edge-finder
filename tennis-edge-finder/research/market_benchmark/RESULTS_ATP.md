# Model vs bookmaker benchmark (ATP)

Linked matches with Pinnacle odds: 13327 (link summary: {'rows': 15161, 'by_status': {'MATCHED': 14195, 'AMBIGUOUS': 593, 'UNMATCHED': 373}, 'confidence_quantiles': {'p10': 1.0, 'p50': 1.0, 'p90': 1.0}}). Orientation randomised.
Model column: p_elo_surface_k_lo. Market = Pinnacle, vig removed proportionally.

| forecaster | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| model | 13327 | 0.2169 | 0.6221 | 0.6432 | 0.0332 | 0.826 | -0.003 |
| market_pinnacle | 13327 | 0.2026 | 0.5883 | 0.6784 | 0.0090 | 1.023 | 0.001 |
| market_avg | 13325 | 0.2028 | 0.5892 | 0.6789 | 0.0091 | 1.070 | 0.001 |

Paired bootstrap Brier(model) - Brier(market): +0.01426 [+0.01250, +0.01600]

## Walk-forward hybrid (fit on prior seasons only)

| forecaster | n | brier | log_loss | cal_slope |
|---|---|---|---|---|
| market | 12225 | 0.2031 | 0.5895 | 1.023 |
| market_recalibrated | 12225 | 0.2034 | 0.5900 | 0.998 |
| model | 12225 | 0.2172 | 0.6228 | 0.823 |
| hybrid | 12225 | 0.2034 | 0.5901 | 0.999 |

| season | w_market | w_model | intercept | n_train |
|---|---|---|---|---|
| 2021 | 1.164 | -0.180 | +0.077 | 1102 |
| 2022 | 1.036 | -0.044 | -0.038 | 3431 |
| 2023 | 1.056 | -0.041 | -0.004 | 5849 |
| 2024 | 1.068 | -0.051 | +0.000 | 8356 |
| 2025 | 1.082 | -0.052 | -0.002 | 10959 |
| 2026 | 1.079 | -0.068 | -0.001 | 13257 |

Hybrid - market Brier: +0.00024 [+0.00003, +0.00044]

## Disagreement buckets |model - market|

| bucket | n | model brier | market brier | model LL | market LL | model-side win% | avg mkt prob of model side | hypothetical ROI vs vig-free market |
|---|---|---|---|---|---|---|---|---|
| 0.000-0.025 | 2921 | 0.1902 | 0.1895 | 0.5582 | 0.5564 | 0.480 | 0.492 | -0.057 |
| 0.025-0.050 | 2630 | 0.1996 | 0.1977 | 0.5819 | 0.5764 | 0.476 | 0.480 | -0.032 |
| 0.050-0.100 | 3618 | 0.2132 | 0.2053 | 0.6146 | 0.5942 | 0.445 | 0.462 | -0.056 |
| 0.100-0.150 | 2048 | 0.2293 | 0.2144 | 0.6540 | 0.6169 | 0.430 | 0.428 | +0.017 |
| 0.150-0.200 | 1041 | 0.2482 | 0.2206 | 0.6940 | 0.6323 | 0.415 | 0.408 | +0.057 |
| 0.200-1.000 | 1069 | 0.2902 | 0.2013 | 0.7900 | 0.5873 | 0.325 | 0.351 | -0.089 |

## By season

| season | n | model LL | market LL |
|---|---|---|---|
| 2020 | 1102 | 0.6151 | 0.5751 |
| 2021 | 2329 | 0.6263 | 0.5910 |
| 2022 | 2418 | 0.6150 | 0.5805 |
| 2023 | 2507 | 0.6175 | 0.5865 |
| 2024 | 2603 | 0.6185 | 0.5850 |
| 2025 | 2298 | 0.6374 | 0.6055 |

## By level

| level | n | model LL | market LL |
|---|---|---|---|
| GRAND_SLAM | 2811 | 0.5499 | 0.5104 |
| MASTERS_1000 | 2851 | 0.6373 | 0.6068 |
| TOUR_500_250 | 7602 | 0.6430 | 0.6100 |
