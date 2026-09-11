# Model vs bookmaker benchmark (ATP)

Linked matches with Pinnacle odds: 13323 (link summary: {'rows': 15161, 'by_status': {'MATCHED': 14195, 'AMBIGUOUS': 593, 'UNMATCHED': 373}, 'confidence_quantiles': {'p10': 1.0, 'p50': 1.0, 'p90': 1.0}}). Orientation randomised.
Model column: p_elo_surface_k_lo. Market = Pinnacle, vig removed proportionally.

| forecaster | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| model | 13323 | 0.2169 | 0.6221 | 0.6432 | 0.0333 | 0.826 | 0.016 |
| market_pinnacle | 13323 | 0.2026 | 0.5884 | 0.6782 | 0.0094 | 1.023 | 0.013 |
| market_avg | 13321 | 0.2028 | 0.5893 | 0.6790 | 0.0121 | 1.070 | 0.014 |

Paired bootstrap Brier(model) - Brier(market): +0.01426 [+0.01233, +0.01597]

## Walk-forward hybrid (fit on prior seasons only)

| forecaster | n | brier | log_loss | cal_slope |
|---|---|---|---|---|
| market | 12221 | 0.2031 | 0.5896 | 1.023 |
| market_recalibrated | 12221 | 0.2033 | 0.5899 | 0.999 |
| model | 12221 | 0.2172 | 0.6228 | 0.823 |
| hybrid | 12221 | 0.2033 | 0.5900 | 1.000 |

| season | w_market | w_model | intercept | n_train |
|---|---|---|---|---|
| 2021 | 1.164 | -0.180 | +0.077 | 1102 |
| 2022 | 1.041 | -0.050 | -0.022 | 3430 |
| 2023 | 1.059 | -0.043 | +0.012 | 5847 |
| 2024 | 1.069 | -0.052 | +0.008 | 8353 |
| 2025 | 1.082 | -0.053 | +0.005 | 10955 |
| 2026 | 1.080 | -0.069 | +0.010 | 13253 |

Hybrid - market Brier: +0.00018 [-0.00003, +0.00038]

## Disagreement buckets |model - market|

| bucket | n | model brier | market brier | model LL | market LL | model-side win% | avg mkt prob of model side | hypothetical ROI vs vig-free market |
|---|---|---|---|---|---|---|---|---|
| 0.000-0.025 | 2921 | 0.1902 | 0.1895 | 0.5582 | 0.5564 | 0.480 | 0.492 | -0.057 |
| 0.025-0.050 | 2630 | 0.1996 | 0.1977 | 0.5819 | 0.5764 | 0.476 | 0.480 | -0.032 |
| 0.050-0.100 | 3618 | 0.2132 | 0.2053 | 0.6146 | 0.5942 | 0.445 | 0.462 | -0.056 |
| 0.100-0.150 | 2048 | 0.2293 | 0.2144 | 0.6540 | 0.6169 | 0.430 | 0.428 | +0.017 |
| 0.150-0.200 | 1040 | 0.2483 | 0.2207 | 0.6942 | 0.6327 | 0.415 | 0.408 | +0.058 |
| 0.200-1.000 | 1066 | 0.2905 | 0.2013 | 0.7907 | 0.5876 | 0.325 | 0.352 | -0.090 |

## By season

| season | n | model LL | market LL |
|---|---|---|---|
| 2020 | 1102 | 0.6151 | 0.5751 |
| 2021 | 2328 | 0.6264 | 0.5908 |
| 2022 | 2417 | 0.6150 | 0.5807 |
| 2023 | 2506 | 0.6174 | 0.5867 |
| 2024 | 2602 | 0.6186 | 0.5851 |
| 2025 | 2298 | 0.6374 | 0.6055 |

## By level

| level | n | model LL | market LL |
|---|---|---|---|
| GRAND_SLAM | 2807 | 0.5500 | 0.5105 |
| MASTERS_1000 | 2851 | 0.6373 | 0.6068 |
| TOUR_500_250 | 7602 | 0.6430 | 0.6100 |
