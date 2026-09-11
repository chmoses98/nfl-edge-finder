# Model vs bookmaker benchmark (ATP)

Linked matches with Pinnacle odds: 13327 (link summary: {'rows': 15161, 'by_status': {'MATCHED': 14195, 'AMBIGUOUS': 593, 'UNMATCHED': 373}, 'confidence_quantiles': {'p10': 1.0, 'p50': 1.0, 'p90': 1.0}}). Orientation randomised.
Model column: p_elo_plain. Market = Pinnacle, vig removed proportionally.

| forecaster | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| model | 13327 | 0.2155 | 0.6193 | 0.6470 | 0.0344 | 0.815 | 0.003 |
| market_pinnacle | 13327 | 0.2026 | 0.5883 | 0.6784 | 0.0090 | 1.023 | 0.001 |
| market_avg | 13325 | 0.2028 | 0.5892 | 0.6789 | 0.0091 | 1.070 | 0.001 |

Paired bootstrap Brier(model) - Brier(market): +0.01292 [+0.01127, +0.01461]

## Walk-forward hybrid (fit on prior seasons only)

| forecaster | n | brier | log_loss | cal_slope |
|---|---|---|---|---|
| market | 12225 | 0.2031 | 0.5895 | 1.023 |
| market_recalibrated | 12225 | 0.2034 | 0.5900 | 0.998 |
| model | 12225 | 0.2153 | 0.6189 | 0.817 |
| hybrid | 12225 | 0.2039 | 0.5913 | 0.988 |

| season | w_market | w_model | intercept | n_train |
|---|---|---|---|---|
| 2021 | 1.358 | -0.398 | +0.081 | 1102 |
| 2022 | 1.022 | -0.026 | -0.039 | 3431 |
| 2023 | 1.050 | -0.031 | -0.005 | 5849 |
| 2024 | 1.074 | -0.055 | -0.000 | 8356 |
| 2025 | 1.096 | -0.064 | -0.002 | 10959 |
| 2026 | 1.090 | -0.075 | -0.001 | 13257 |

Hybrid - market Brier: +0.00077 [+0.00040, +0.00114]

## Disagreement buckets |model - market|

| bucket | n | model brier | market brier | model LL | market LL | model-side win% | avg mkt prob of model side | hypothetical ROI vs vig-free market |
|---|---|---|---|---|---|---|---|---|
| 0.000-0.025 | 3009 | 0.1927 | 0.1925 | 0.5635 | 0.5628 | 0.497 | 0.497 | -0.029 |
| 0.025-0.050 | 2688 | 0.1992 | 0.1981 | 0.5817 | 0.5791 | 0.493 | 0.490 | +0.022 |
| 0.050-0.100 | 3764 | 0.2113 | 0.2063 | 0.6109 | 0.5966 | 0.478 | 0.475 | -0.014 |
| 0.100-0.150 | 2022 | 0.2282 | 0.2090 | 0.6514 | 0.6040 | 0.437 | 0.452 | -0.057 |
| 0.150-0.200 | 973 | 0.2613 | 0.2154 | 0.7254 | 0.6191 | 0.375 | 0.424 | -0.112 |
| 0.200-1.000 | 871 | 0.2824 | 0.2062 | 0.7715 | 0.5984 | 0.362 | 0.366 | -0.033 |

## By season

| season | n | model LL | market LL |
|---|---|---|---|
| 2020 | 1102 | 0.6242 | 0.5751 |
| 2021 | 2329 | 0.6162 | 0.5910 |
| 2022 | 2418 | 0.6093 | 0.5805 |
| 2023 | 2507 | 0.6183 | 0.5865 |
| 2024 | 2603 | 0.6157 | 0.5850 |
| 2025 | 2298 | 0.6347 | 0.6055 |

## By level

| level | n | model LL | market LL |
|---|---|---|---|
| GRAND_SLAM | 2811 | 0.5450 | 0.5104 |
| MASTERS_1000 | 2851 | 0.6420 | 0.6068 |
| TOUR_500_250 | 7602 | 0.6383 | 0.6100 |
