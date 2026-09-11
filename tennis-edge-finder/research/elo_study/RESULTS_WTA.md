# Elo walk-forward study (WTA)

Matches: 660473 from 1990; evaluated 291738 matches in seasons >= 2015.
Orientation randomised (symmetric scores). Ratings use only matches strictly before each prediction (chronological replay).

| variant | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| rank | 291738 | nan | nan | 0.5015 | nan | nan | nan |
| elo_levelprior | 291738 | 0.1918 | 0.5634 | 0.7026 | 0.0061 | 1.053 | -0.005 |
| elo_plain | 291738 | 0.1922 | 0.5642 | 0.7019 | 0.0077 | 1.066 | -0.005 |
| elo_surface_k_hi | 291738 | 0.1923 | 0.5644 | 0.7017 | 0.0038 | 1.016 | -0.005 |
| elo_surface | 291738 | 0.1932 | 0.5667 | 0.6999 | 0.0084 | 1.074 | -0.005 |
| elo_surface_levelk | 291738 | 0.1951 | 0.5719 | 0.6967 | 0.0169 | 1.143 | -0.005 |
| elo_surface_k_lo | 291738 | 0.1993 | 0.5825 | 0.6905 | 0.0315 | 1.276 | -0.005 |

## Paired bootstrap (Brier diff vs elo_plain; negative = better)

| variant | diff | 95% CI | P(better) |
|---|---|---|---|
| rank | +nan | [+nan, +nan] | 0.00 |
| elo_levelprior | -0.00034 | [-0.00037, -0.00031] | 1.00 |
| elo_surface | +0.00100 | [+0.00080, +0.00117] | 0.00 |
| elo_surface_levelk | +0.00294 | [+0.00272, +0.00314] | 0.00 |
| elo_surface_k_hi | +0.00010 | [-0.00009, +0.00029] | 0.15 |
| elo_surface_k_lo | +0.00709 | [+0.00682, +0.00733] | 0.00 |

## By level (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| GRAND_SLAM | 9975 | nan | 0.5911 |
| ITF | 238358 | nan | 0.5558 |
| MASTERS_1000 | 5042 | nan | 0.6224 |
| OTHER | 644 | nan | 0.6064 |
| TEAM | 2158 | nan | 0.5292 |
| TOUR_500_250 | 27197 | nan | 0.6065 |
| TOUR_FINALS | 210 | nan | 0.6698 |
| WTA_125 | 7963 | nan | 0.6018 |

## By surface (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| Carpet | 5587 | nan | 0.5717 |
| Clay | 126206 | nan | 0.5604 |
| Grass | 7143 | nan | 0.6072 |
| Hard | 152687 | nan | 0.5650 |

## By season (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| 2015 | 22179 | nan | 0.5709 |
| 2016 | 22174 | nan | 0.5724 |
| 2017 | 21613 | nan | 0.5765 |
| 2018 | 21318 | nan | 0.5833 |
| 2019 | 31611 | nan | 0.5785 |
| 2020 | 10034 | nan | 0.5713 |
| 2021 | 25043 | nan | 0.5599 |
| 2022 | 33484 | nan | 0.5519 |
| 2023 | 35281 | nan | 0.5529 |
| 2024 | 38720 | nan | 0.5474 |
| 2025 | 23339 | nan | 0.5642 |
| 2026 | 6942 | nan | 0.5695 |
