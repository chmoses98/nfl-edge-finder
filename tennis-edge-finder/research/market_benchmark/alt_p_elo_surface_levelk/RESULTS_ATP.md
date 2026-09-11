# Model vs bookmaker benchmark (ATP)

Linked matches with Pinnacle odds: 13327 (link summary: {'rows': 15161, 'by_status': {'MATCHED': 14195, 'AMBIGUOUS': 593, 'UNMATCHED': 373}, 'confidence_quantiles': {'p10': 1.0, 'p50': 1.0, 'p90': 1.0}}). Orientation randomised.
Model column: p_elo_surface_levelk. Market = Pinnacle, vig removed proportionally.

| forecaster | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| model | 13327 | 0.2162 | 0.6210 | 0.6484 | 0.0398 | 0.781 | -0.003 |
| market_pinnacle | 13327 | 0.2026 | 0.5883 | 0.6784 | 0.0090 | 1.023 | 0.001 |
| market_avg | 13325 | 0.2028 | 0.5892 | 0.6789 | 0.0091 | 1.070 | 0.001 |

Paired bootstrap Brier(model) - Brier(market): +0.01356 [+0.01182, +0.01525]

## Walk-forward hybrid (fit on prior seasons only)

| forecaster | n | brier | log_loss | cal_slope |
|---|---|---|---|---|
| market | 12225 | 0.2031 | 0.5895 | 1.023 |
| market_recalibrated | 12225 | 0.2034 | 0.5900 | 0.998 |
| model | 12225 | 0.2165 | 0.6217 | 0.777 |
| hybrid | 12225 | 0.2034 | 0.5901 | 0.999 |

| season | w_market | w_model | intercept | n_train |
|---|---|---|---|---|
| 2021 | 1.160 | -0.160 | +0.076 | 1102 |
| 2022 | 1.011 | -0.012 | -0.039 | 3431 |
| 2023 | 1.049 | -0.028 | -0.004 | 5849 |
| 2024 | 1.069 | -0.047 | +0.000 | 8356 |
| 2025 | 1.084 | -0.049 | -0.002 | 10959 |
| 2026 | 1.087 | -0.069 | -0.001 | 13257 |

Hybrid - market Brier: +0.00025 [+0.00006, +0.00044]

## Disagreement buckets |model - market|

| bucket | n | model brier | market brier | model LL | market LL | model-side win% | avg mkt prob of model side | hypothetical ROI vs vig-free market |
|---|---|---|---|---|---|---|---|---|
| 0.000-0.025 | 2991 | 0.1861 | 0.1858 | 0.5474 | 0.5463 | 0.501 | 0.506 | -0.040 |
| 0.025-0.050 | 2690 | 0.1998 | 0.1971 | 0.5824 | 0.5752 | 0.490 | 0.508 | -0.048 |
| 0.050-0.100 | 3670 | 0.2120 | 0.2058 | 0.6129 | 0.5970 | 0.498 | 0.501 | -0.006 |
| 0.100-0.150 | 2040 | 0.2322 | 0.2179 | 0.6597 | 0.6253 | 0.467 | 0.465 | +0.016 |
| 0.150-0.200 | 1019 | 0.2552 | 0.2198 | 0.7157 | 0.6285 | 0.422 | 0.439 | -0.041 |
| 0.200-1.000 | 917 | 0.2998 | 0.2077 | 0.8151 | 0.6021 | 0.349 | 0.378 | -0.085 |

## By season

| season | n | model LL | market LL |
|---|---|---|---|
| 2020 | 1102 | 0.6129 | 0.5751 |
| 2021 | 2329 | 0.6216 | 0.5910 |
| 2022 | 2418 | 0.6132 | 0.5805 |
| 2023 | 2507 | 0.6175 | 0.5865 |
| 2024 | 2603 | 0.6173 | 0.5850 |
| 2025 | 2298 | 0.6397 | 0.6055 |

## By level

| level | n | model LL | market LL |
|---|---|---|---|
| GRAND_SLAM | 2811 | 0.5459 | 0.5104 |
| MASTERS_1000 | 2851 | 0.6381 | 0.6068 |
| TOUR_500_250 | 7602 | 0.6423 | 0.6100 |
