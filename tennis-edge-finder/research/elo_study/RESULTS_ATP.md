# Elo walk-forward study (ATP)

Matches: 853037 from 1990; evaluated 321480 matches in seasons >= 2015.
Orientation randomised (symmetric scores). Ratings use only matches strictly before each prediction (chronological replay).

| variant | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| elo_levelprior | 321480 | 0.2000 | 0.5836 | 0.6864 | 0.0152 | 0.905 | -0.005 |
| elo_plain | 321480 | 0.2001 | 0.5837 | 0.6859 | 0.0143 | 0.913 | -0.005 |
| elo_surface_k_hi | 321480 | 0.2003 | 0.5844 | 0.6869 | 0.0202 | 0.876 | -0.005 |
| elo_surface | 321480 | 0.2007 | 0.5849 | 0.6853 | 0.0130 | 0.922 | -0.005 |
| elo_surface_levelk | 321480 | 0.2016 | 0.5871 | 0.6830 | 0.0059 | 0.971 | -0.005 |
| elo_surface_k_lo | 321480 | 0.2042 | 0.5934 | 0.6778 | 0.0079 | 1.068 | -0.005 |
| rank | 321480 | 0.2142 | 0.6182 | 0.6629 | 0.0329 | 1.209 | -0.005 |

## Paired bootstrap (Brier diff vs elo_plain; negative = better)

| variant | diff | 95% CI | P(better) |
|---|---|---|---|
| rank | +0.01409 | [+0.01371, +0.01452] | 0.00 |
| elo_levelprior | -0.00008 | [-0.00011, -0.00005] | 1.00 |
| elo_surface | +0.00054 | [+0.00035, +0.00076] | 0.00 |
| elo_surface_levelk | +0.00144 | [+0.00125, +0.00167] | 0.00 |
| elo_surface_k_hi | +0.00019 | [+0.00001, +0.00041] | 0.02 |
| elo_surface_k_lo | +0.00405 | [+0.00382, +0.00431] | 0.00 |

## By level (log_loss: elo_levelprior vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| CHALLENGER | 89578 | 0.6125 | 0.6114 |
| GRAND_SLAM | 10496 | 0.5894 | 0.5893 |
| ITF | 185466 | 0.5633 | 0.5643 |
| MASTERS_1000 | 9086 | 0.6268 | 0.6264 |
| TEAM | 2502 | 0.5398 | 0.5315 |
| TOUR_500_250 | 24139 | 0.6175 | 0.6169 |

## By surface (log_loss: elo_levelprior vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| Carpet | 3520 | 0.5977 | 0.5975 |
| Clay | 144689 | 0.5805 | 0.5807 |
| Grass | 7505 | 0.6145 | 0.6140 |
| Hard | 165714 | 0.5845 | 0.5846 |

## By season (log_loss: elo_levelprior vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| 2015 | 31016 | 0.5570 | 0.5579 |
| 2016 | 32504 | 0.5566 | 0.5556 |
| 2017 | 30401 | 0.5661 | 0.5659 |
| 2018 | 29983 | 0.5858 | 0.5860 |
| 2019 | 27867 | 0.5864 | 0.5870 |
| 2020 | 9283 | 0.6168 | 0.6161 |
| 2021 | 21952 | 0.6100 | 0.6100 |
| 2022 | 29103 | 0.5962 | 0.5965 |
| 2023 | 31144 | 0.5984 | 0.5986 |
| 2024 | 32819 | 0.5891 | 0.5895 |
| 2025 | 31580 | 0.5883 | 0.5884 |
| 2026 | 13828 | 0.5861 | 0.5860 |
