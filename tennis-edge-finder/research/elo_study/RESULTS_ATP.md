# Elo walk-forward study (ATP)

Matches: 234722 from 1990; evaluated 86973 matches in seasons >= 2015.
Orientation randomised (symmetric scores). Ratings use only matches strictly before each prediction (chronological replay).

| variant | n | brier | log_loss | accuracy | ECE | cal_slope | cal_intercept |
|---|---|---|---|---|---|---|---|
| rank | 86973 | nan | nan | 0.5007 | nan | nan | nan |
| elo_surface_k_lo | 86973 | 0.2238 | 0.6386 | 0.6336 | 0.0323 | 0.779 | -0.005 |
| elo_surface_levelk | 86973 | 0.2239 | 0.6400 | 0.6369 | 0.0446 | 0.714 | -0.005 |
| elo_surface | 86973 | 0.2242 | 0.6410 | 0.6367 | 0.0478 | 0.699 | -0.005 |
| elo_plain | 86973 | 0.2245 | 0.6414 | 0.6354 | 0.0462 | 0.705 | -0.004 |
| elo_levelprior | 86973 | 0.2247 | 0.6422 | 0.6363 | 0.0480 | 0.693 | -0.004 |
| elo_surface_k_hi | 86973 | 0.2254 | 0.6458 | 0.6382 | 0.0588 | 0.643 | -0.005 |

## Paired bootstrap (Brier diff vs elo_plain; negative = better)

| variant | diff | 95% CI | P(better) |
|---|---|---|---|
| rank | +nan | [+nan, +nan] | 0.00 |
| elo_levelprior | +0.00020 | [+0.00014, +0.00025] | 0.00 |
| elo_surface | -0.00028 | [-0.00070, +0.00006] | 0.91 |
| elo_surface_levelk | -0.00057 | [-0.00099, -0.00020] | 1.00 |
| elo_surface_k_hi | +0.00092 | [+0.00047, +0.00132] | 0.00 |
| elo_surface_k_lo | -0.00067 | [-0.00112, -0.00026] | 1.00 |

## By level (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| CHALLENGER | 56980 | nan | 0.6566 |
| GRAND_SLAM | 5308 | nan | 0.5350 |
| MASTERS_1000 | 5953 | nan | 0.6259 |
| TEAM | 2458 | nan | 0.5766 |
| TOUR_500_250 | 15919 | nan | 0.6406 |

## By surface (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| Clay | 36776 | nan | 0.6519 |
| Grass | 4381 | nan | 0.6279 |
| Hard | 45243 | nan | 0.6340 |

## By season (log_loss: rank vs elo_plain)

| group | n | best | elo_plain |
|---|---|---|---|
| 2015 | 7523 | nan | 0.6051 |
| 2016 | 7854 | nan | 0.6132 |
| 2017 | 7377 | nan | 0.6255 |
| 2018 | 7764 | nan | 0.6520 |
| 2019 | 5766 | nan | 0.6478 |
| 2020 | 3618 | nan | 0.6646 |
| 2021 | 7011 | nan | 0.6497 |
| 2022 | 8236 | nan | 0.6475 |
| 2023 | 8593 | nan | 0.6476 |
| 2024 | 9112 | nan | 0.6493 |
| 2025 | 8613 | nan | 0.6557 |
| 2026 | 5506 | nan | 0.6515 |
