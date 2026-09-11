# Shadow evaluation scorecard (20260911T163650Z)

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 22855 | 961 | 2 |
| **latest pregame per contract (primary)** | 961 | 961 | 2 |

The raw view holds 22855 snapshots of 961 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 63 |
| SETTLED | 22792 |

| close status | n |
|---|---|
| OK | 22825 |
| OK_STALE | 30 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 959 contracts whose payout is a 0/1 realisation (2 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 959 | 0.1572 | 0.4744 | 0.2855 | 0.2450 | 0.0405 |
| market mid (only where value == event probability) | 151 | 0.2252 | 0.6681 | 0.4152 | 0.2053 | 0.2099 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 302 | 0.0434 | 0.0464 |
| 0.10-0.20 | 161 | 0.1472 | 0.1615 |
| 0.20-0.30 | 117 | 0.2432 | 0.2393 |
| 0.30-0.40 | 94 | 0.3446 | 0.3085 |
| 0.40-0.50 | 81 | 0.4462 | 0.3827 |
| 0.50-0.60 | 70 | 0.5485 | 0.4429 |
| 0.60-0.70 | 51 | 0.6520 | 0.5490 |
| 0.70-0.80 | 39 | 0.7491 | 0.5385 |
| 0.80-0.90 | 25 | 0.8435 | 0.5600 |
| 0.90-1.00 | 19 | 0.9510 | 0.6842 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 959 contracts whose payout is exactly known (0 settled without an exact payout, 2 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 959 | 0.15692 | 0.29748 | 0.03601 | 0.2811 | 0.2450 |
| market mid at the same snapshot | 959 | 0.14963 | 0.29867 | 0.08494 | 0.3300 | 0.2450 |

On the 959 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 959 | 0.15692 | 0.29748 | 0.03601 | 0.2811 | 0.2450 |
| market mid at snapshot | 959 | 0.14963 | 0.29867 | 0.08494 | 0.3300 | 0.2450 |
| market mid at close | 959 | 0.14935 | 0.29851 | 0.08486 | 0.3299 | 0.2450 |

Lower is better: **the closing market** is ahead by 0.00757 in squared payout error on this set.

## 3. Closing-line value and market movement

On 960 contracts with a legitimate close (1 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00046**
* mean signed CLV (executable, crossing the spread): **0.00054**
* share with positive midpoint CLV: 0.1208
* movement: {'away': 86, 'toward': 115, 'unchanged': 759}
* toward-share of directional moves: 0.5721 on 201 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 1 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00000
* toward-share of directional moves: - on 0 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 530 | 431 | 1448/1455/1538 | 0.1663 | 0.16617 | 0.16023 |
| T-6h | 393 | 568 | 451/457/477 | 0.1718 | 0.17150 | 0.14578 |
| T-90m | 340 | 621 | 206/206/206 | 0.1779 | 0.17776 | 0.15627 |
| T-30m | 17 | 944 | 32/38/65 | 0.0960 | 0.09617 | 0.06057 |
| latest pregame | 961 | - | 0/24/307 | 0.1572 | 0.15692 | 0.14963 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 8 | 8 | 8 | 0.1806 | 0.18060 | 0.15117 | 0.00125 |
| GAME_WINNER | 4 | 4 | 4 | 0.2978 | 0.29782 | 0.28213 | 0.00000 |
| PLAYER_STAT | 806 | 804 | 804 | 0.1425 | 0.14223 | 0.13477 | 0.00046 |
| SPREAD | 50 | 50 | 50 | 0.2341 | 0.23408 | 0.23037 | 0.00030 |
| TEAM_TOTAL | 55 | 55 | 55 | 0.2161 | 0.21613 | 0.20957 | 0.00100 |
| TOTAL | 38 | 38 | 38 | 0.2606 | 0.26062 | 0.25680 | -0.00013 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 4 | 4 | 4 | 0.2978 | 0.29782 | 0.28213 | 0.00000 |
| attempts | 44 | 44 | 44 | 0.2369 | 0.23204 | 0.18815 | 0.00011 |
| carries | 55 | 55 | 55 | 0.2363 | 0.23697 | 0.15994 | 0.00309 |
| completions | 44 | 44 | 44 | 0.2129 | 0.21102 | 0.20415 | 0.00057 |
| interceptions | 12 | 12 | 12 | 0.2185 | 0.22048 | 0.22020 | 0.00083 |
| margin | 50 | 50 | 50 | 0.2341 | 0.23408 | 0.23037 | 0.00030 |
| min_team_points | 8 | 8 | 8 | 0.1806 | 0.18060 | 0.15117 | 0.00125 |
| passing_tds | 17 | 17 | 17 | 0.1890 | 0.18607 | 0.19267 | 0.00059 |
| passing_yards | 35 | 35 | 35 | 0.2031 | 0.19614 | 0.19163 | -0.00043 |
| receiving_yards | 219 | 219 | 219 | 0.0992 | 0.09912 | 0.12163 | 0.00016 |
| receptions | 187 | 187 | 187 | 0.1242 | 0.12478 | 0.12813 | 0.00037 |
| rushing_yards | 117 | 117 | 117 | 0.1599 | 0.16180 | 0.11602 | 0.00043 |
| team_points | 55 | 55 | 55 | 0.2161 | 0.21613 | 0.20957 | 0.00100 |
| total_points | 38 | 38 | 38 | 0.2606 | 0.26062 | 0.25680 | -0.00013 |
| touchdowns | 76 | 74 | 74 | 0.0704 | 0.06999 | 0.07433 | 0.00013 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 308 | 306 | 306 | 0.0423 | 0.04220 | 0.04352 | -0.00016 |
| 0.10-0.20 | 166 | 166 | 166 | 0.1381 | 0.13789 | 0.12623 | 0.00108 |
| 0.20-0.30 | 113 | 113 | 113 | 0.1806 | 0.18022 | 0.16021 | 0.00049 |
| 0.30-0.40 | 96 | 96 | 96 | 0.2137 | 0.21358 | 0.20704 | -0.00021 |
| 0.40-0.50 | 78 | 78 | 78 | 0.2405 | 0.24214 | 0.22717 | 0.00263 |
| 0.50-0.60 | 70 | 70 | 70 | 0.2592 | 0.25764 | 0.24892 | 0.00007 |
| 0.60-0.70 | 52 | 52 | 52 | 0.2651 | 0.26433 | 0.26618 | 0.00096 |
| 0.70-0.80 | 40 | 40 | 40 | 0.2772 | 0.27616 | 0.25577 | 0.00075 |
| 0.80-0.90 | 20 | 20 | 20 | 0.3401 | 0.33647 | 0.33614 | 0.00050 |
| 0.90-1.00 | 18 | 18 | 18 | 0.2983 | 0.29841 | 0.29491 | -0.00111 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 304 | 302 | 302 | 0.0427 | 0.04264 | 0.04395 | -0.00016 |
| 0.10-0.20 | 161 | 161 | 161 | 0.1329 | 0.13283 | 0.12396 | 0.00093 |
| 0.20-0.30 | 117 | 117 | 117 | 0.1801 | 0.18004 | 0.15976 | 0.00094 |
| 0.30-0.40 | 94 | 94 | 94 | 0.2135 | 0.21310 | 0.20319 | -0.00048 |
| 0.40-0.50 | 81 | 81 | 81 | 0.2363 | 0.23692 | 0.21520 | 0.00253 |
| 0.50-0.60 | 70 | 70 | 70 | 0.2577 | 0.25696 | 0.25808 | 0.00014 |
| 0.60-0.70 | 51 | 51 | 51 | 0.2584 | 0.25818 | 0.25638 | 0.00088 |
| 0.70-0.80 | 39 | 39 | 39 | 0.2902 | 0.28865 | 0.26856 | 0.00090 |
| 0.80-0.90 | 25 | 25 | 25 | 0.3295 | 0.32542 | 0.32466 | 0.00020 |
| 0.90-1.00 | 19 | 19 | 19 | 0.2831 | 0.28341 | 0.27961 | -0.00105 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 145 | 145 | 145 | 0.1678 | 0.16738 | 0.18027 | 0.00093 |
| 20%+ | 91 | 91 | 91 | 0.2844 | 0.28846 | 0.20402 | 0.00077 |
| 3-5% | 132 | 130 | 130 | 0.1279 | 0.12647 | 0.12524 | 0.00023 |
| 5-10% | 174 | 174 | 174 | 0.1459 | 0.14578 | 0.14334 | 0.00078 |
| <3% | 419 | 419 | 419 | 0.1396 | 0.13880 | 0.13740 | 0.00018 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 627 | 627 | 627 | 0.1515 | 0.15155 | 0.14166 | 0.00042 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 333 | 331 | 331 | 0.1684 | 0.16751 | 0.16513 | 0.00056 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 17 | 16 | 16 | 0.0960 | 0.09617 | 0.06057 | -0.00125 |
| 90m-6h | 104 | 104 | 104 | 0.1481 | 0.14797 | 0.14843 | 0.00048 |
| <30m | 840 | 839 | 839 | 0.1595 | 0.15918 | 0.15148 | 0.00049 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 961 | 959 | 959 | 0.1572 | 0.15692 | 0.14963 | 0.00046 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 961 | 959 | 959 | 0.1572 | 0.15692 | 0.14963 | 0.00046 |

### by game

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 2026_01_NE_SEA | 451 | 451 | 451 | 0.1633 | 0.16325 | 0.14665 | 0.00011 |
| 2026_01_SF_LA | 510 | 508 | 508 | 0.1517 | 0.15129 | 0.15228 | 0.00078 |

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 215 | 215 | 215 | 0.1391 | 0.13901 | 0.14255 | 0.00095 |
| 6-10c | 68 | 68 | 68 | 0.2009 | 0.20024 | 0.19824 | 0.00177 |
| <=2c | 618 | 616 | 616 | 0.1547 | 0.15446 | 0.14835 | 0.00011 |
| >10c | 60 | 60 | 60 | 0.1979 | 0.19724 | 0.13309 | 0.00092 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 961 | 959 | 959 | 0.1572 | 0.15692 | 0.14963 | 0.00046 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| EXPECTED_ACTIVE | 806 | 804 | 804 | 0.1425 | 0.14223 | 0.13477 | 0.00046 |
| None | 155 | 155 | 155 | 0.2331 | 0.23310 | 0.22671 | 0.00048 |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
