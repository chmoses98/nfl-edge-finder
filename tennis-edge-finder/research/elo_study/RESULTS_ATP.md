# Elo walk-forward study (ATP)

Matches: 852843 from 1990; evaluated 321293 matches in seasons >= 2015.
Orientation randomised (symmetric scores). Ratings use only matches strictly before each prediction (chronological replay).

| variant | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| rank | 321293 | nan | nan | 0.5012 | nan | nan | nan |
| elo_levelprior | 321293 | 0.2000 | 0.5835 | 0.6866 | 0.0152 | 0.906 | -0.004 |
| elo_plain | 321293 | 0.2001 | 0.5836 | 0.6862 | 0.0142 | 0.913 | -0.004 |
| elo_surface_k_hi | 321293 | 0.2003 | 0.5843 | 0.6870 | 0.0202 | 0.876 | -0.003 |
| elo_surface | 321293 | 0.2006 | 0.5848 | 0.6855 | 0.0130 | 0.922 | -0.003 |
| elo_surface_levelk | 321293 | 0.2015 | 0.5870 | 0.6832 | 0.0061 | 0.971 | -0.003 |
| elo_surface_k_lo | 321293 | 0.2041 | 0.5933 | 0.6780 | 0.0085 | 1.069 | -0.003 |

## Paired bootstrap (Brier diff vs elo_plain; negative = better)

| variant | diff | 95% CI | P(better) |
|---|---|---|---|
| rank | +nan | [+nan, +nan] | 0.00 |
| elo_levelprior | -0.00008 | [-0.00011, -0.00005] | 1.00 |
| elo_surface | +0.00054 | [+0.00032, +0.00074] | 0.00 |
| elo_surface_levelk | +0.00145 | [+0.00124, +0.00165] | 0.00 |
| elo_surface_k_hi | +0.00019 | [-0.00002, +0.00039] | 0.05 |
| elo_surface_k_lo | +0.00406 | [+0.00381, +0.00431] | 0.00 |

## By level (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| CHALLENGER | 89578 | nan | 0.6114 |
| GRAND_SLAM | 10496 | nan | 0.5892 |
| ITF | 185286 | nan | 0.5641 |
| MASTERS_1000 | 9086 | nan | 0.6264 |
| TEAM | 2495 | nan | 0.5312 |
| TOUR_500_250 | 24139 | nan | 0.6169 |

## By surface (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| Carpet | 3520 | nan | 0.5975 |
| Clay | 144590 | nan | 0.5806 |
| Grass | 7505 | nan | 0.6140 |
| Hard | 165626 | nan | 0.5845 |

## By season (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| 2015 | 31011 | nan | 0.5579 |
| 2016 | 32501 | nan | 0.5555 |
| 2017 | 30401 | nan | 0.5659 |
| 2018 | 29983 | nan | 0.5860 |
| 2019 | 27862 | nan | 0.5869 |
| 2020 | 9270 | nan | 0.6159 |
| 2021 | 21928 | nan | 0.6100 |
| 2022 | 29073 | nan | 0.5964 |
| 2023 | 31100 | nan | 0.5984 |
| 2024 | 32784 | nan | 0.5892 |
| 2025 | 31568 | nan | 0.5883 |
| 2026 | 13812 | nan | 0.5859 |
