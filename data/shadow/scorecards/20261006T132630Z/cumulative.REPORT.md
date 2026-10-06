# Shadow evaluation scorecard - cumulative

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 542474 | 25704 | 64 |
| **latest pregame per contract (primary)** | 25704 | 25704 | 64 |

The raw view holds 542474 snapshots of 25704 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 16483 |
| SETTLED | 525991 |

| close status | n |
|---|---|
| OK | 523548 |
| OK_STALE | 18926 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 25324 contracts whose payout is a 0/1 realisation (380 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 25324 | 0.1675 | 0.5135 | 0.2655 | 0.3279 | -0.0624 |
| market mid (only where value == event probability) | 4857 | 0.1580 | 0.4788 | 0.4092 | 0.4142 | -0.0051 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 8895 | 0.0408 | 0.0926 |
| 0.10-0.20 | 4537 | 0.1465 | 0.2268 |
| 0.20-0.30 | 2957 | 0.2462 | 0.3422 |
| 0.30-0.40 | 2237 | 0.3479 | 0.4417 |
| 0.40-0.50 | 1845 | 0.4483 | 0.5306 |
| 0.50-0.60 | 1602 | 0.5462 | 0.5980 |
| 0.60-0.70 | 1190 | 0.6489 | 0.6731 |
| 0.70-0.80 | 863 | 0.7488 | 0.7613 |
| 0.80-0.90 | 656 | 0.8448 | 0.8323 |
| 0.90-1.00 | 542 | 0.9514 | 0.9410 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 25324 contracts whose payout is exactly known (0 settled without an exact payout, 380 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 25324 | 0.16786 | 0.29978 | -0.06588 | 0.2620 | 0.3279 |
| market mid at the same snapshot | 25324 | 0.15024 | 0.29611 | -0.00764 | 0.3203 | 0.3279 |

On the 25019 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 25019 | 0.16861 | 0.30107 | -0.06623 | 0.2626 | 0.3288 |
| market mid at snapshot | 25019 | 0.15094 | 0.29751 | -0.00730 | 0.3215 | 0.3288 |
| market mid at close | 25019 | 0.15113 | 0.29777 | -0.00789 | 0.3209 | 0.3288 |

Lower is better: **the closing market** is ahead by 0.01749 in squared payout error on this set.

## 3. Closing-line value and market movement

On 25111 contracts with a legitimate close (593 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00071**
* mean signed CLV (executable, crossing the spread): **0.00171**
* share with positive midpoint CLV: 0.2504
* movement: {'away': 5301, 'no_view': 1, 'toward': 6245, 'unchanged': 13564}
* toward-share of directional moves: 0.5409 on 11546 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 593 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00024
* toward-share of directional moves: 0.7027 on 37 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 8920 | 16784 | 1442/1521/1559 | 0.1717 | 0.17220 | 0.15514 |
| T-6h | 3696 | 22008 | 361/389/477 | 0.1552 | 0.15601 | 0.13287 |
| T-90m | 12844 | 12860 | 96/122/208 | 0.1674 | 0.16796 | 0.14844 |
| T-30m | 19433 | 6271 | 32/74/150 | 0.1714 | 0.17180 | 0.15329 |
| latest pregame | 25704 | - | 0/103/5721 | 0.1675 | 0.16786 | 0.15024 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 256 | 256 | 256 | 0.1366 | 0.13661 | 0.13458 | -0.00419 |
| GAME_WINNER | 128 | 128 | 128 | 0.2298 | 0.22983 | 0.22933 | 0.00070 |
| PLAYER_STAT | 20719 | 20339 | 20339 | 0.1694 | 0.16987 | 0.14788 | 0.00074 |
| SPREAD | 1639 | 1639 | 1639 | 0.1770 | 0.17696 | 0.17609 | 0.00061 |
| TEAM_TOTAL | 1746 | 1746 | 1746 | 0.1353 | 0.13530 | 0.13648 | 0.00135 |
| TOTAL | 1216 | 1216 | 1216 | 0.1688 | 0.16878 | 0.16966 | 0.00033 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 128 | 128 | 128 | 0.2298 | 0.22983 | 0.22933 | 0.00070 |
| attempts | 648 | 637 | 637 | 0.2279 | 0.22595 | 0.21229 | 0.00237 |
| carries | 977 | 977 | 977 | 0.2858 | 0.28754 | 0.20995 | 0.00563 |
| completions | 648 | 637 | 637 | 0.1953 | 0.19474 | 0.19496 | 0.00524 |
| interceptions | 384 | 381 | 381 | 0.1292 | 0.12910 | 0.13123 | 0.00419 |
| margin | 1639 | 1639 | 1639 | 0.1770 | 0.17696 | 0.17609 | 0.00061 |
| min_team_points | 256 | 256 | 256 | 0.1366 | 0.13661 | 0.13458 | -0.00419 |
| passing_tds | 527 | 524 | 524 | 0.1499 | 0.15065 | 0.14847 | -0.00018 |
| passing_yards | 1112 | 1105 | 1105 | 0.1695 | 0.16911 | 0.16705 | 0.00047 |
| receiving_yards | 5598 | 5474 | 5474 | 0.1757 | 0.17636 | 0.15544 | 0.00048 |
| receptions | 4859 | 4798 | 4798 | 0.1773 | 0.17821 | 0.14351 | 0.00012 |
| rushing_yards | 3180 | 3136 | 3136 | 0.1699 | 0.17040 | 0.14874 | -0.00033 |
| team_points | 1746 | 1746 | 1746 | 0.1353 | 0.13530 | 0.13648 | 0.00135 |
| total_points | 1216 | 1216 | 1216 | 0.1688 | 0.16878 | 0.16966 | 0.00033 |
| touchdowns | 2786 | 2670 | 2670 | 0.0884 | 0.08851 | 0.08421 | 0.00031 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 9298 | 9000 | 9000 | 0.0852 | 0.08526 | 0.07727 | 0.00037 |
| 0.10-0.20 | 4589 | 4560 | 4560 | 0.1843 | 0.18454 | 0.16073 | 0.00065 |
| 0.20-0.30 | 2974 | 2954 | 2954 | 0.2352 | 0.23596 | 0.20670 | 0.00097 |
| 0.30-0.40 | 2244 | 2237 | 2237 | 0.2542 | 0.25517 | 0.21889 | 0.00128 |
| 0.40-0.50 | 1869 | 1855 | 1855 | 0.2558 | 0.25696 | 0.22568 | 0.00122 |
| 0.50-0.60 | 1589 | 1583 | 1583 | 0.2422 | 0.24282 | 0.22683 | 0.00040 |
| 0.60-0.70 | 1177 | 1172 | 1172 | 0.2170 | 0.21780 | 0.20448 | 0.00124 |
| 0.70-0.80 | 857 | 857 | 857 | 0.1793 | 0.17971 | 0.17855 | 0.00152 |
| 0.80-0.90 | 597 | 596 | 596 | 0.1292 | 0.12892 | 0.13157 | -0.00009 |
| 0.90-1.00 | 510 | 510 | 510 | 0.0529 | 0.05289 | 0.05339 | 0.00040 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 9062 | 8895 | 8895 | 0.0850 | 0.08507 | 0.07707 | 0.00056 |
| 0.10-0.20 | 4607 | 4537 | 4537 | 0.1808 | 0.18100 | 0.15822 | 0.00050 |
| 0.20-0.30 | 2998 | 2957 | 2957 | 0.2340 | 0.23469 | 0.20588 | 0.00100 |
| 0.30-0.40 | 2266 | 2237 | 2237 | 0.2549 | 0.25587 | 0.21975 | 0.00103 |
| 0.40-0.50 | 1873 | 1845 | 1845 | 0.2566 | 0.25768 | 0.22454 | 0.00098 |
| 0.50-0.60 | 1620 | 1602 | 1602 | 0.2433 | 0.24407 | 0.22732 | 0.00046 |
| 0.60-0.70 | 1212 | 1190 | 1190 | 0.2202 | 0.22078 | 0.20488 | 0.00097 |
| 0.70-0.80 | 866 | 863 | 863 | 0.1811 | 0.18167 | 0.18145 | 0.00147 |
| 0.80-0.90 | 658 | 656 | 656 | 0.1391 | 0.13867 | 0.14025 | 0.00009 |
| 0.90-1.00 | 542 | 542 | 542 | 0.0549 | 0.05484 | 0.05552 | 0.00059 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 4021 | 3946 | 3946 | 0.2095 | 0.21006 | 0.18770 | 0.00023 |
| 20%+ | 3776 | 3660 | 3660 | 0.3028 | 0.30484 | 0.21706 | 0.00312 |
| 3-5% | 3080 | 3045 | 3045 | 0.1301 | 0.13005 | 0.12859 | 0.00015 |
| 5-10% | 4181 | 4109 | 4109 | 0.1638 | 0.16392 | 0.15680 | 0.00067 |
| <3% | 10646 | 10564 | 10564 | 0.1171 | 0.11707 | 0.11678 | 0.00022 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 17281 | 16986 | 16986 | 0.1780 | 0.17888 | 0.15354 | 0.00092 |
| none | 3 | 3 | 3 | 0.0143 | 0.01429 | 0.01429 | 0.00000 |
| yes | 8420 | 8335 | 8335 | 0.1461 | 0.14547 | 0.14357 | 0.00027 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 10889 | 10713 | 10713 | 0.1732 | 0.17341 | 0.15609 | 0.00065 |
| 6-24h | 209 | 151 | 151 | 0.0670 | 0.06708 | 0.06245 | 0.00136 |
| 90m-6h | 13232 | 13191 | 13191 | 0.1648 | 0.16535 | 0.14639 | 0.00057 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 102 | 2 | 2 | 0.0340 | 0.03248 | 0.00450 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 25704 | 25324 | 25324 | 0.1675 | 0.16786 | 0.15024 | 0.00071 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |
| 2 | 6132 | 6063 | 6063 | 0.1586 | 0.15895 | 0.14573 | 0.00045 |
| 3 | 6059 | 5981 | 5981 | 0.1629 | 0.16349 | 0.14506 | 0.00053 |
| 4 | 6427 | 6323 | 6323 | 0.1726 | 0.17291 | 0.15051 | 0.00055 |

### by game

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 2026_01_ARI_LAC | 411 | 411 | 411 | 0.1881 | 0.18873 | 0.18228 | -0.00028 |
| 2026_01_ATL_PIT | 454 | 416 | 416 | 0.1512 | 0.15113 | 0.13977 | 0.00215 |
| 2026_01_BAL_IND | 430 | 425 | 425 | 0.1756 | 0.17615 | 0.16181 | 0.00302 |
| 2026_01_BUF_HOU | 440 | 440 | 440 | 0.1845 | 0.18599 | 0.16415 | -0.00084 |
| 2026_01_CHI_CAR | 458 | 454 | 454 | 0.2487 | 0.25057 | 0.24317 | -0.00024 |
| 2026_01_CLE_JAX | 403 | 403 | 403 | 0.1533 | 0.15265 | 0.13044 | -0.00052 |
| 2026_01_DAL_NYG | 450 | 427 | 427 | 0.1593 | 0.15971 | 0.15166 | 0.00607 |
| 2026_01_DEN_KC | 473 | 471 | 471 | 0.1783 | 0.17659 | 0.15861 | 0.00444 |
| 2026_01_GB_MIN | 446 | 445 | 445 | 0.2181 | 0.21777 | 0.18373 | 0.00074 |
| 2026_01_MIA_LV | 420 | 385 | 385 | 0.1693 | 0.17017 | 0.14476 | -0.00161 |
| 2026_01_NE_SEA | 451 | 451 | 451 | 0.1633 | 0.16325 | 0.14665 | 0.00011 |
| 2026_01_NO_DET | 422 | 420 | 420 | 0.2157 | 0.21761 | 0.18134 | 0.00313 |
| 2026_01_NYJ_TEN | 429 | 427 | 427 | 0.1552 | 0.15499 | 0.13118 | 0.00033 |
| 2026_01_SF_LA | 510 | 508 | 508 | 0.1517 | 0.15129 | 0.15228 | 0.00078 |
| 2026_01_TB_CIN | 442 | 440 | 440 | 0.1409 | 0.14134 | 0.13030 | 0.00295 |
| 2026_01_WAS_PHI | 447 | 434 | 434 | 0.1370 | 0.13720 | 0.12624 | -0.00138 |
| 2026_02_CAR_ATL | 389 | 387 | 387 | 0.1660 | 0.16626 | 0.14904 | 0.00038 |
| 2026_02_CIN_HOU | 411 | 396 | 396 | 0.1808 | 0.18143 | 0.16613 | 0.00100 |
| 2026_02_CLE_TB | 332 | 332 | 332 | 0.1648 | 0.16511 | 0.14710 | -0.00055 |
| 2026_02_DET_BUF | 413 | 413 | 413 | 0.1821 | 0.18344 | 0.16041 | -0.00022 |
| 2026_02_GB_NYJ | 374 | 374 | 374 | 0.1291 | 0.12940 | 0.13583 | 0.00066 |
| 2026_02_IND_KC | 398 | 394 | 394 | 0.2146 | 0.21564 | 0.17534 | -0.00013 |
| 2026_02_JAX_DEN | 347 | 342 | 342 | 0.1579 | 0.15771 | 0.13432 | 0.00047 |
| 2026_02_LV_LAC | 364 | 364 | 364 | 0.1599 | 0.15981 | 0.15708 | 0.00151 |
| 2026_02_MIA_SF | 354 | 354 | 354 | 0.1065 | 0.10807 | 0.09599 | 0.00224 |
| 2026_02_MIN_CHI | 403 | 390 | 390 | 0.1596 | 0.15895 | 0.15921 | 0.00037 |
| 2026_02_NO_BAL | 398 | 394 | 394 | 0.1586 | 0.15942 | 0.13736 | 0.00094 |
| 2026_02_NYG_LA | 423 | 402 | 402 | 0.1521 | 0.15182 | 0.13791 | -0.00055 |
| 2026_02_PHI_TEN | 359 | 359 | 359 | 0.1465 | 0.14646 | 0.15004 | 0.00045 |
| 2026_02_PIT_NE | 396 | 394 | 394 | 0.1303 | 0.13053 | 0.12885 | -0.00057 |
| 2026_02_SEA_ARI | 370 | 370 | 370 | 0.1494 | 0.14896 | 0.14032 | 0.00045 |
| 2026_02_WAS_DAL | 401 | 398 | 398 | 0.1712 | 0.17148 | 0.15033 | 0.00094 |
| 2026_03_ARI_SF | 370 | 370 | 370 | 0.1893 | 0.19065 | 0.15817 | 0.00102 |
| 2026_03_ATL_GB | 418 | 418 | 418 | 0.2136 | 0.21434 | 0.18765 | 0.00094 |
| 2026_03_BAL_DAL | 419 | 409 | 409 | 0.1292 | 0.13051 | 0.10294 | 0.00668 |
| 2026_03_CAR_CLE | 364 | 352 | 352 | 0.1791 | 0.17956 | 0.14280 | -0.00003 |
| 2026_03_CIN_PIT | 331 | 327 | 327 | 0.1471 | 0.14798 | 0.13406 | 0.00003 |
| 2026_03_HOU_IND | 362 | 351 | 351 | 0.1275 | 0.12757 | 0.11321 | -0.00054 |
| 2026_03_KC_MIA | 351 | 351 | 351 | 0.1519 | 0.15257 | 0.14140 | 0.00080 |
| 2026_03_LAC_BUF | 367 | 365 | 365 | 0.1377 | 0.13778 | 0.13185 | 0.00025 |
| 2026_03_LA_DEN | 369 | 369 | 369 | 0.1644 | 0.16467 | 0.16482 | -0.00091 |
| 2026_03_LV_NO | 381 | 381 | 381 | 0.1738 | 0.17528 | 0.15450 | 0.00237 |
| 2026_03_MIN_TB | 388 | 388 | 388 | 0.1302 | 0.12962 | 0.11689 | 0.00008 |
| 2026_03_NE_JAX | 408 | 407 | 407 | 0.1639 | 0.16389 | 0.15443 | 0.00037 |
| 2026_03_NYJ_DET | 396 | 374 | 374 | 0.1964 | 0.19727 | 0.15083 | -0.00479 |
| 2026_03_PHI_CHI | 392 | 391 | 391 | 0.1669 | 0.16731 | 0.14539 | 0.00128 |
| 2026_03_SEA_WAS | 377 | 377 | 377 | 0.1817 | 0.18315 | 0.18829 | 0.00000 |
| 2026_03_TEN_NYG | 366 | 351 | 351 | 0.1461 | 0.14629 | 0.12764 | -0.00017 |
| 2026_04_ARI_NYG | 392 | 391 | 391 | 0.1906 | 0.19102 | 0.15678 | 0.00061 |
| 2026_04_ATL_NO | 420 | 412 | 412 | 0.1930 | 0.19329 | 0.15426 | -0.00178 |
| 2026_04_DAL_HOU | 417 | 416 | 416 | 0.1837 | 0.18450 | 0.15302 | 0.00159 |
| 2026_04_DEN_SF | 396 | 391 | 391 | 0.1455 | 0.14494 | 0.12317 | 0.00038 |
| 2026_04_DET_CAR | 411 | 411 | 411 | 0.2242 | 0.22529 | 0.18130 | -0.00134 |
| 2026_04_GB_TB | 401 | 401 | 401 | 0.1349 | 0.13487 | 0.11472 | 0.00125 |
| 2026_04_IND_WAS | 407 | 352 | 352 | 0.1432 | 0.14258 | 0.14839 | 0.00043 |
| 2026_04_JAX_CIN | 429 | 428 | 428 | 0.2105 | 0.21072 | 0.19034 | 0.00069 |
| 2026_04_KC_LV | 410 | 410 | 410 | 0.2016 | 0.20214 | 0.17055 | -0.00019 |
| 2026_04_LAC_SEA | 418 | 405 | 405 | 0.1437 | 0.14281 | 0.13394 | 0.00075 |
| 2026_04_LA_PHI | 382 | 367 | 367 | 0.1561 | 0.15651 | 0.15327 | 0.00245 |
| 2026_04_MIA_MIN | 378 | 378 | 378 | 0.1828 | 0.18223 | 0.15525 | -0.00020 |
| 2026_04_NE_BUF | 434 | 432 | 432 | 0.1494 | 0.15041 | 0.14784 | 0.00158 |
| 2026_04_NYJ_CHI | 371 | 370 | 370 | 0.1491 | 0.14954 | 0.15266 | 0.00130 |
| 2026_04_PIT_CLE | 375 | 375 | 375 | 0.1867 | 0.18805 | 0.15054 | 0.00068 |
| 2026_04_TEN_BAL | 386 | 384 | 384 | 0.1566 | 0.15800 | 0.11691 | 0.00082 |

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 6238 | 6155 | 6155 | 0.1436 | 0.14412 | 0.12480 | 0.00072 |
| 6-10c | 857 | 811 | 811 | 0.1731 | 0.17350 | 0.15472 | 0.00192 |
| <=2c | 17846 | 17668 | 17668 | 0.1742 | 0.17457 | 0.15764 | 0.00037 |
| >10c | 763 | 690 | 690 | 0.2007 | 0.20128 | 0.18238 | 0.00852 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 6427 | 6323 | 6323 | 0.1726 | 0.17291 | 0.15051 | 0.00055 |
| none | 19277 | 19001 | 19001 | 0.1658 | 0.16618 | 0.15015 | 0.00076 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| DOUBTFUL | 30 | 0 | 0 | - | - | - | - |
| EXPECTED_ACTIVE | 20351 | 20230 | 20230 | 0.1695 | 0.17000 | 0.14811 | 0.00081 |
| EXPECTED_OUT | 42 | 0 | 0 | - | - | - | -0.14750 |
| None | 4985 | 4985 | 4985 | 0.1597 | 0.15966 | 0.15988 | 0.00058 |
| OUT | 153 | 0 | 0 | - | - | - | -0.00105 |
| QUESTIONABLE | 120 | 89 | 89 | 0.1569 | 0.16290 | 0.11494 | 0.00044 |
| UNKNOWN | 23 | 20 | 20 | 0.0811 | 0.07316 | 0.05227 | 0.00025 |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
