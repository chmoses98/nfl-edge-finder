# Model vs bookmaker benchmark (ATP)

Linked matches with Pinnacle odds: 13327 (link summary: {'rows': 15161, 'by_status': {'MATCHED': 14195, 'AMBIGUOUS': 593, 'UNMATCHED': 373}, 'confidence_quantiles': {'p10': 1.0, 'p50': 1.0, 'p90': 1.0}}). Orientation randomised.
Model column: p_elo_levelprior. Market = Pinnacle, vig removed proportionally.

| forecaster | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| model | 13327 | 0.2157 | 0.6197 | 0.6470 | 0.0354 | 0.808 | 0.003 |
| market_pinnacle | 13327 | 0.2026 | 0.5883 | 0.6784 | 0.0090 | 1.023 | 0.001 |
| market_avg | 13325 | 0.2028 | 0.5892 | 0.6789 | 0.0091 | 1.070 | 0.001 |

Paired bootstrap Brier(model) - Brier(market): +0.01307 [+0.01140, +0.01476]

## Walk-forward hybrid (fit on prior seasons only)

| forecaster | n | brier | log_loss | cal_slope |
|---|---|---|---|---|
| market | 12225 | 0.2031 | 0.5895 | 1.023 |
| market_recalibrated | 12225 | 0.2034 | 0.5900 | 0.998 |
| model | 12225 | 0.2155 | 0.6193 | 0.811 |
| hybrid | 12225 | 0.2039 | 0.5913 | 0.988 |

| season | w_market | w_model | intercept | n_train |
|---|---|---|---|---|
| 2021 | 1.357 | -0.393 | +0.081 | 1102 |
| 2022 | 1.024 | -0.028 | -0.039 | 3431 |
| 2023 | 1.051 | -0.032 | -0.005 | 5849 |
| 2024 | 1.075 | -0.055 | -0.000 | 8356 |
| 2025 | 1.097 | -0.065 | -0.002 | 10959 |
| 2026 | 1.091 | -0.076 | -0.001 | 13257 |

Hybrid - market Brier: +0.00076 [+0.00039, +0.00113]

## Disagreement buckets |model - market|

| bucket | n | model brier | market brier | model LL | market LL | model-side win% | avg mkt prob of model side | hypothetical ROI vs vig-free market |
|---|---|---|---|---|---|---|---|---|
| 0.000-0.025 | 3003 | 0.1922 | 0.1919 | 0.5623 | 0.5614 | 0.494 | 0.499 | -0.040 |
| 0.025-0.050 | 2653 | 0.1986 | 0.1975 | 0.5800 | 0.5774 | 0.493 | 0.490 | +0.022 |
| 0.050-0.100 | 3779 | 0.2116 | 0.2066 | 0.6120 | 0.5975 | 0.483 | 0.478 | -0.011 |
| 0.100-0.150 | 2026 | 0.2279 | 0.2091 | 0.6505 | 0.6041 | 0.441 | 0.455 | -0.053 |
| 0.150-0.200 | 987 | 0.2626 | 0.2160 | 0.7277 | 0.6206 | 0.376 | 0.427 | -0.114 |
| 0.200-1.000 | 879 | 0.2843 | 0.2074 | 0.7768 | 0.6010 | 0.363 | 0.368 | -0.033 |

## By season

| season | n | model LL | market LL |
|---|---|---|---|
| 2020 | 1102 | 0.6247 | 0.5751 |
| 2021 | 2329 | 0.6167 | 0.5910 |
| 2022 | 2418 | 0.6096 | 0.5805 |
| 2023 | 2507 | 0.6187 | 0.5865 |
| 2024 | 2603 | 0.6161 | 0.5850 |
| 2025 | 2298 | 0.6352 | 0.6055 |

## By level

| level | n | model LL | market LL |
|---|---|---|---|
| GRAND_SLAM | 2811 | 0.5452 | 0.5104 |
| MASTERS_1000 | 2851 | 0.6425 | 0.6068 |
| TOUR_500_250 | 7602 | 0.6387 | 0.6100 |
