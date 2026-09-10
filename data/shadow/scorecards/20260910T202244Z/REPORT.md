# Shadow evaluation scorecard (20260910T202244Z)

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 10628 | 451 | 1 |
| **latest pregame per contract (primary)** | 451 | 451 | 1 |

The raw view holds 10628 snapshots of 451 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| SETTLED | 10628 |

| close status | n |
|---|---|
| OK | 10628 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 451 contracts whose payout is a 0/1 realisation (0 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 451 | 0.1633 | 0.4870 | 0.2836 | 0.2395 | 0.0441 |
| market mid (only where value == event probability) | 75 | 0.1832 | 0.5542 | 0.4057 | 0.0933 | 0.3124 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 141 | 0.0443 | 0.0426 |
| 0.10-0.20 | 80 | 0.1476 | 0.1875 |
| 0.20-0.30 | 55 | 0.2447 | 0.2545 |
| 0.30-0.40 | 42 | 0.3452 | 0.3095 |
| 0.40-0.50 | 37 | 0.4462 | 0.3514 |
| 0.50-0.60 | 33 | 0.5483 | 0.4545 |
| 0.60-0.70 | 25 | 0.6443 | 0.5200 |
| 0.70-0.80 | 20 | 0.7489 | 0.4500 |
| 0.80-0.90 | 9 | 0.8541 | 0.4444 |
| 0.90-1.00 | 9 | 0.9459 | 0.6667 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 451 contracts whose payout is exactly known (0 settled without an exact payout, 0 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 451 | 0.16325 | 0.30429 | 0.03988 | 0.2794 | 0.2395 |
| market mid at the same snapshot | 451 | 0.14665 | 0.29845 | 0.09816 | 0.3376 | 0.2395 |

On the 451 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 451 | 0.16325 | 0.30429 | 0.03988 | 0.2794 | 0.2395 |
| market mid at snapshot | 451 | 0.14665 | 0.29845 | 0.09816 | 0.3376 | 0.2395 |
| market mid at close | 451 | 0.14652 | 0.29831 | 0.09798 | 0.3375 | 0.2395 |

Lower is better: **the closing market** is ahead by 0.01673 in squared payout error on this set.

## 3. Closing-line value and market movement

On 451 contracts with a legitimate close (0 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00011**
* mean signed CLV (executable, crossing the spread): **0.00018**
* share with positive midpoint CLV: 0.0554
* movement: {'away': 18, 'toward': 25, 'unchanged': 408}
* toward-share of directional moves: 0.5814 on 43 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 123 | 328 | 1448/1458/1538 | 0.1701 | 0.16981 | 0.14588 |
| T-6h | 392 | 59 | 457/457/477 | 0.1722 | 0.17194 | 0.14615 |
| T-90m | 340 | 111 | 206/206/206 | 0.1779 | 0.17776 | 0.15627 |
| T-30m | 2 | 449 | 32/32/32 | 0.0097 | 0.00826 | 0.00016 |
| latest pregame | 451 | - | 0/0/307 | 0.1633 | 0.16325 | 0.14665 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 4 | 4 | 4 | 0.1612 | 0.16120 | 0.12572 | 0.00000 |
| GAME_WINNER | 2 | 2 | 2 | 0.1484 | 0.14836 | 0.14822 | 0.00000 |
| PLAYER_STAT | 374 | 374 | 374 | 0.1583 | 0.15821 | 0.13930 | 0.00007 |
| SPREAD | 25 | 25 | 25 | 0.0797 | 0.07970 | 0.08051 | 0.00060 |
| TEAM_TOTAL | 27 | 27 | 27 | 0.1908 | 0.19081 | 0.18470 | 0.00093 |
| TOTAL | 19 | 19 | 19 | 0.3354 | 0.33536 | 0.32844 | -0.00079 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 2 | 2 | 2 | 0.1484 | 0.14836 | 0.14822 | 0.00000 |
| attempts | 22 | 22 | 22 | 0.2537 | 0.24842 | 0.18487 | 0.00000 |
| carries | 27 | 27 | 27 | 0.2786 | 0.27930 | 0.14657 | 0.00000 |
| completions | 22 | 22 | 22 | 0.2080 | 0.20568 | 0.18699 | 0.00000 |
| interceptions | 6 | 6 | 6 | 0.3489 | 0.34990 | 0.34805 | 0.00000 |
| margin | 25 | 25 | 25 | 0.0797 | 0.07970 | 0.08051 | 0.00060 |
| min_team_points | 4 | 4 | 4 | 0.1612 | 0.16120 | 0.12572 | 0.00000 |
| passing_tds | 8 | 8 | 8 | 0.1277 | 0.12410 | 0.13959 | 0.00000 |
| passing_yards | 18 | 18 | 18 | 0.2081 | 0.20055 | 0.19089 | 0.00000 |
| receiving_yards | 97 | 97 | 97 | 0.1225 | 0.12330 | 0.14317 | 0.00000 |
| receptions | 87 | 87 | 87 | 0.1369 | 0.13819 | 0.14458 | 0.00000 |
| rushing_yards | 53 | 53 | 53 | 0.1696 | 0.17135 | 0.08787 | 0.00000 |
| team_points | 27 | 27 | 27 | 0.1908 | 0.19081 | 0.18470 | 0.00093 |
| total_points | 19 | 19 | 19 | 0.3354 | 0.33536 | 0.32844 | -0.00079 |
| touchdowns | 34 | 34 | 34 | 0.0554 | 0.05508 | 0.06462 | 0.00073 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 143 | 143 | 143 | 0.0393 | 0.03926 | 0.04125 | 0.00011 |
| 0.10-0.20 | 81 | 81 | 81 | 0.1563 | 0.15626 | 0.11098 | 0.00037 |
| 0.20-0.30 | 53 | 53 | 53 | 0.1819 | 0.18262 | 0.15165 | 0.00057 |
| 0.30-0.40 | 46 | 46 | 46 | 0.2142 | 0.21461 | 0.18115 | -0.00011 |
| 0.40-0.50 | 34 | 34 | 34 | 0.2407 | 0.24271 | 0.22149 | -0.00059 |
| 0.50-0.60 | 33 | 33 | 33 | 0.2554 | 0.25441 | 0.24791 | 0.00030 |
| 0.60-0.70 | 26 | 26 | 26 | 0.2777 | 0.27626 | 0.29347 | 0.00058 |
| 0.70-0.80 | 19 | 19 | 19 | 0.3345 | 0.33064 | 0.30995 | 0.00026 |
| 0.80-0.90 | 8 | 8 | 8 | 0.3847 | 0.38311 | 0.38366 | -0.00063 |
| 0.90-1.00 | 8 | 8 | 8 | 0.3285 | 0.32848 | 0.32257 | -0.00313 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 141 | 141 | 141 | 0.0397 | 0.03968 | 0.04163 | 0.00011 |
| 0.10-0.20 | 80 | 80 | 80 | 0.1495 | 0.14951 | 0.11144 | 0.00038 |
| 0.20-0.30 | 55 | 55 | 55 | 0.1868 | 0.18741 | 0.14724 | 0.00055 |
| 0.30-0.40 | 42 | 42 | 42 | 0.2125 | 0.21336 | 0.17702 | -0.00012 |
| 0.40-0.50 | 37 | 37 | 37 | 0.2358 | 0.23662 | 0.19925 | -0.00054 |
| 0.50-0.60 | 33 | 33 | 33 | 0.2537 | 0.25347 | 0.26770 | 0.00030 |
| 0.60-0.70 | 25 | 25 | 25 | 0.2666 | 0.26606 | 0.28177 | 0.00060 |
| 0.70-0.80 | 20 | 20 | 20 | 0.3376 | 0.33325 | 0.31102 | 0.00025 |
| 0.80-0.90 | 9 | 9 | 9 | 0.4179 | 0.41395 | 0.41829 | -0.00056 |
| 0.90-1.00 | 9 | 9 | 9 | 0.2930 | 0.29347 | 0.28720 | -0.00278 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 83 | 83 | 83 | 0.1896 | 0.18810 | 0.19650 | 0.00030 |
| 20%+ | 57 | 57 | 57 | 0.3208 | 0.32571 | 0.20244 | 0.00000 |
| 3-5% | 51 | 51 | 51 | 0.0992 | 0.09855 | 0.09971 | -0.00010 |
| 5-10% | 80 | 80 | 80 | 0.1239 | 0.12372 | 0.11037 | -0.00006 |
| <3% | 180 | 180 | 180 | 0.1370 | 0.13625 | 0.13543 | 0.00019 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 304 | 304 | 304 | 0.1621 | 0.16211 | 0.13882 | 0.00021 |
| yes | 147 | 147 | 147 | 0.1660 | 0.16561 | 0.16284 | -0.00010 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 2 | 2 | 2 | 0.0097 | 0.00826 | 0.00016 | 0.00000 |
| 90m-6h | 104 | 104 | 104 | 0.1481 | 0.14797 | 0.14843 | 0.00048 |
| <30m | 345 | 345 | 345 | 0.1688 | 0.16876 | 0.14696 | 0.00000 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 451 | 451 | 451 | 0.1633 | 0.16325 | 0.14665 | 0.00011 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 451 | 451 | 451 | 0.1633 | 0.16325 | 0.14665 | 0.00011 |

### by game

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 2026_01_NE_SEA | 451 | 451 | 451 | 0.1633 | 0.16325 | 0.14665 | 0.00011 |

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 110 | 110 | 110 | 0.1155 | 0.11641 | 0.12623 | 0.00009 |
| 6-10c | 42 | 42 | 42 | 0.2166 | 0.21657 | 0.19574 | 0.00000 |
| <=2c | 255 | 255 | 255 | 0.1694 | 0.16916 | 0.15055 | 0.00016 |
| >10c | 44 | 44 | 44 | 0.1968 | 0.19526 | 0.12821 | 0.00000 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 451 | 451 | 451 | 0.1633 | 0.16325 | 0.14665 | 0.00011 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| EXPECTED_ACTIVE | 374 | 374 | 374 | 0.1583 | 0.15821 | 0.13930 | 0.00007 |
| None | 77 | 77 | 77 | 0.1878 | 0.18776 | 0.18233 | 0.00032 |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
