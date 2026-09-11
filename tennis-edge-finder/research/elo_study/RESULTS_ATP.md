# Elo walk-forward study (ATP)

Matches: 949494 from 1990; evaluated 365737 matches in seasons >= 2015.
Orientation randomised (symmetric scores). Ratings use only matches strictly before each prediction (chronological replay).

| variant | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| rank | 365737 | nan | nan | 0.5012 | nan | nan | nan |
| elo_levelprior | 365737 | 0.2041 | 0.5930 | 0.6779 | 0.0197 | 0.878 | -0.004 |
| elo_plain | 365737 | 0.2041 | 0.5931 | 0.6776 | 0.0187 | 0.885 | -0.004 |
| elo_surface | 365737 | 0.2046 | 0.5941 | 0.6771 | 0.0176 | 0.893 | -0.003 |
| elo_surface_k_hi | 365737 | 0.2045 | 0.5944 | 0.6785 | 0.0256 | 0.843 | -0.004 |
| elo_surface_levelk | 365737 | 0.2053 | 0.5958 | 0.6750 | 0.0107 | 0.938 | -0.003 |
| elo_surface_k_lo | 365737 | 0.2076 | 0.6011 | 0.6700 | 0.0040 | 1.036 | -0.003 |

## Paired bootstrap (Brier diff vs elo_plain; negative = better)

| variant | diff | 95% CI | P(better) |
|---|---|---|---|
| rank | +nan | [+nan, +nan] | 0.00 |
| elo_levelprior | -0.00006 | [-0.00009, -0.00004] | 1.00 |
| elo_surface | +0.00044 | [+0.00028, +0.00063] | 0.00 |
| elo_surface_levelk | +0.00118 | [+0.00101, +0.00137] | 0.00 |
| elo_surface_k_hi | +0.00034 | [+0.00018, +0.00053] | 0.00 |
| elo_surface_k_lo | +0.00342 | [+0.00321, +0.00365] | 0.00 |

## By level (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| CHALLENGER | 131172 | nan | 0.6275 |
| GRAND_SLAM | 10763 | nan | 0.5892 |
| ITF | 185286 | nan | 0.5641 |
| MASTERS_1000 | 9828 | nan | 0.6301 |
| TEAM | 2839 | nan | 0.5389 |
| TOUR_500_250 | 25603 | nan | 0.6197 |

## By surface (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| Carpet | 3584 | nan | 0.5990 |
| Clay | 166034 | nan | 0.5916 |
| Grass | 8710 | nan | 0.6220 |
| Hard | 187064 | nan | 0.5928 |

## By season (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| 2015 | 34960 | nan | 0.5665 |
| 2016 | 37225 | nan | 0.5647 |
| 2017 | 34448 | nan | 0.5748 |
| 2018 | 34093 | nan | 0.5962 |
| 2019 | 30592 | nan | 0.5949 |
| 2020 | 11101 | nan | 0.6285 |
| 2021 | 26059 | nan | 0.6204 |
| 2022 | 33685 | nan | 0.6062 |
| 2023 | 35968 | nan | 0.6068 |
| 2024 | 38356 | nan | 0.6013 |
| 2025 | 32788 | nan | 0.5917 |
| 2026 | 16462 | nan | 0.6015 |
