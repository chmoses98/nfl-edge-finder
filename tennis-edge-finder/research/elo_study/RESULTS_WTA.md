# Elo walk-forward study (WTA)

Matches: 667926 from 1990; evaluated 299185 matches in seasons >= 2015.
Orientation randomised (symmetric scores). Ratings use only matches strictly before each prediction (chronological replay).

| variant | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| elo_levelprior | 299185 | 0.1933 | 0.5667 | 0.6995 | 0.0051 | 1.043 | -0.006 |
| elo_plain | 299185 | 0.1936 | 0.5675 | 0.6988 | 0.0062 | 1.056 | -0.006 |
| elo_surface_k_hi | 299185 | 0.1938 | 0.5679 | 0.6993 | 0.0034 | 1.007 | -0.006 |
| elo_surface | 299185 | 0.1946 | 0.5700 | 0.6971 | 0.0070 | 1.063 | -0.006 |
| elo_surface_levelk | 299185 | 0.1964 | 0.5748 | 0.6939 | 0.0155 | 1.133 | -0.006 |
| elo_surface_k_lo | 299185 | 0.2004 | 0.5850 | 0.6878 | 0.0300 | 1.266 | -0.006 |
| rank | 299185 | 0.2196 | 0.6304 | 0.6515 | 0.0425 | 1.211 | -0.007 |

## Paired bootstrap (Brier diff vs elo_plain; negative = better)

| variant | diff | 95% CI | P(better) |
|---|---|---|---|
| rank | +0.02598 | [+0.02555, +0.02648] | 0.00 |
| elo_levelprior | -0.00033 | [-0.00036, -0.00031] | 1.00 |
| elo_surface | +0.00100 | [+0.00082, +0.00117] | 0.00 |
| elo_surface_levelk | +0.00283 | [+0.00266, +0.00302] | 0.00 |
| elo_surface_k_hi | +0.00016 | [-0.00002, +0.00033] | 0.05 |
| elo_surface_k_lo | +0.00682 | [+0.00662, +0.00707] | 0.00 |

## By level (log_loss: elo_levelprior vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| GRAND_SLAM | 9975 | 0.5909 | 0.5910 |
| ITF | 245805 | 0.5589 | 0.5601 |
| MASTERS_1000 | 5042 | 0.6229 | 0.6223 |
| OTHER | 644 | 0.6054 | 0.6047 |
| TEAM | 2158 | 0.5491 | 0.5292 |
| TOUR_500_250 | 27197 | 0.6071 | 0.6065 |
| TOUR_FINALS | 210 | 0.6700 | 0.6698 |
| WTA_125 | 7963 | 0.6022 | 0.6019 |

## By surface (log_loss: elo_levelprior vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| Carpet | 5680 | 0.5710 | 0.5729 |
| Clay | 129938 | 0.5635 | 0.5645 |
| Grass | 7188 | 0.6077 | 0.6075 |
| Hard | 156264 | 0.5674 | 0.5680 |

## By season (log_loss: elo_levelprior vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| 2015 | 22184 | 0.5700 | 0.5709 |
| 2016 | 22174 | 0.5724 | 0.5724 |
| 2017 | 21613 | 0.5765 | 0.5765 |
| 2018 | 21323 | 0.5832 | 0.5834 |
| 2019 | 31671 | 0.5772 | 0.5787 |
| 2020 | 10625 | 0.5784 | 0.5788 |
| 2021 | 26558 | 0.5668 | 0.5680 |
| 2022 | 35341 | 0.5584 | 0.5598 |
| 2023 | 36811 | 0.5578 | 0.5588 |
| 2024 | 40583 | 0.5527 | 0.5537 |
| 2025 | 23352 | 0.5644 | 0.5645 |
| 2026 | 6950 | 0.5704 | 0.5702 |
