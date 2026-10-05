# Shadow evaluation scorecard - cumulative

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 534218 | 25284 | 63 |
| **latest pregame per contract (primary)** | 25284 | 25284 | 63 |

The raw view holds 534218 snapshots of 25284 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 15977 |
| SETTLED | 518241 |

| close status | n |
|---|---|
| OK | 515756 |
| OK_STALE | 18462 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 24912 contracts whose payout is a 0/1 realisation (372 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 24912 | 0.1671 | 0.5125 | 0.2658 | 0.3271 | -0.0613 |
| market mid (only where value == event probability) | 4781 | 0.1566 | 0.4747 | 0.4090 | 0.4100 | -0.0009 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 8742 | 0.0409 | 0.0923 |
| 0.10-0.20 | 4462 | 0.1465 | 0.2246 |
| 0.20-0.30 | 2911 | 0.2462 | 0.3411 |
| 0.30-0.40 | 2201 | 0.3478 | 0.4398 |
| 0.40-0.50 | 1814 | 0.4484 | 0.5287 |
| 0.50-0.60 | 1573 | 0.5463 | 0.5989 |
| 0.60-0.70 | 1173 | 0.6490 | 0.6718 |
| 0.70-0.80 | 853 | 0.7485 | 0.7597 |
| 0.80-0.90 | 649 | 0.8447 | 0.8320 |
| 0.90-1.00 | 534 | 0.9512 | 0.9401 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 24912 contracts whose payout is exactly known (0 settled without an exact payout, 372 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 24912 | 0.16744 | 0.29942 | -0.06481 | 0.2623 | 0.3271 |
| market mid at the same snapshot | 24912 | 0.15017 | 0.29607 | -0.00690 | 0.3202 | 0.3271 |

On the 24607 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 24607 | 0.16820 | 0.30073 | -0.06515 | 0.2628 | 0.3280 |
| market mid at snapshot | 24607 | 0.15088 | 0.29749 | -0.00655 | 0.3214 | 0.3280 |
| market mid at close | 24607 | 0.15110 | 0.29777 | -0.00719 | 0.3208 | 0.3280 |

Lower is better: **the closing market** is ahead by 0.01710 in squared payout error on this set.

## 3. Closing-line value and market movement

On 24699 contracts with a legitimate close (585 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00075**
* mean signed CLV (executable, crossing the spread): **0.00178**
* share with positive midpoint CLV: 0.2520
* movement: {'away': 5199, 'no_view': 1, 'toward': 6180, 'unchanged': 13319}
* toward-share of directional moves: 0.5431 on 11379 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 585 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00025
* toward-share of directional moves: 0.7027 on 37 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 8548 | 16736 | 1442/1509/1559 | 0.1707 | 0.17119 | 0.15504 |
| T-6h | 3696 | 21588 | 361/389/477 | 0.1552 | 0.15601 | 0.13287 |
| T-90m | 12755 | 12529 | 96/122/208 | 0.1678 | 0.16845 | 0.14881 |
| T-30m | 19014 | 6270 | 32/73/150 | 0.1709 | 0.17132 | 0.15326 |
| latest pregame | 25284 | - | 0/103/5721 | 0.1671 | 0.16744 | 0.15017 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 252 | 252 | 252 | 0.1372 | 0.13722 | 0.13496 | -0.00427 |
| GAME_WINNER | 126 | 126 | 126 | 0.2290 | 0.22900 | 0.22860 | 0.00087 |
| PLAYER_STAT | 20377 | 20005 | 20005 | 0.1692 | 0.16968 | 0.14814 | 0.00078 |
| SPREAD | 1614 | 1614 | 1614 | 0.1753 | 0.17531 | 0.17434 | 0.00064 |
| TEAM_TOTAL | 1718 | 1718 | 1718 | 0.1342 | 0.13424 | 0.13534 | 0.00137 |
| TOTAL | 1197 | 1197 | 1197 | 0.1669 | 0.16690 | 0.16769 | 0.00033 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 126 | 126 | 126 | 0.2290 | 0.22900 | 0.22860 | 0.00087 |
| attempts | 642 | 631 | 631 | 0.2266 | 0.22461 | 0.21183 | 0.00247 |
| carries | 965 | 965 | 965 | 0.2877 | 0.28944 | 0.21048 | 0.00575 |
| completions | 642 | 631 | 631 | 0.1939 | 0.19337 | 0.19394 | 0.00530 |
| interceptions | 378 | 375 | 375 | 0.1297 | 0.12963 | 0.13203 | 0.00415 |
| margin | 1614 | 1614 | 1614 | 0.1753 | 0.17531 | 0.17434 | 0.00064 |
| min_team_points | 252 | 252 | 252 | 0.1372 | 0.13722 | 0.13496 | -0.00427 |
| passing_tds | 518 | 515 | 515 | 0.1515 | 0.15228 | 0.14978 | -0.00017 |
| passing_yards | 1093 | 1086 | 1086 | 0.1708 | 0.17039 | 0.16864 | 0.00049 |
| receiving_yards | 5499 | 5381 | 5381 | 0.1758 | 0.17641 | 0.15616 | 0.00053 |
| receptions | 4779 | 4718 | 4718 | 0.1771 | 0.17797 | 0.14391 | 0.00017 |
| rushing_yards | 3125 | 3081 | 3081 | 0.1685 | 0.16894 | 0.14799 | -0.00031 |
| team_points | 1718 | 1718 | 1718 | 0.1342 | 0.13424 | 0.13534 | 0.00137 |
| total_points | 1197 | 1197 | 1197 | 0.1669 | 0.16690 | 0.16769 | 0.00033 |
| touchdowns | 2736 | 2622 | 2622 | 0.0875 | 0.08767 | 0.08369 | 0.00035 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 9138 | 8846 | 8846 | 0.0850 | 0.08502 | 0.07712 | 0.00041 |
| 0.10-0.20 | 4513 | 4485 | 4485 | 0.1827 | 0.18300 | 0.15992 | 0.00069 |
| 0.20-0.30 | 2926 | 2907 | 2907 | 0.2346 | 0.23529 | 0.20687 | 0.00104 |
| 0.30-0.40 | 2209 | 2202 | 2202 | 0.2536 | 0.25458 | 0.21851 | 0.00134 |
| 0.40-0.50 | 1837 | 1823 | 1823 | 0.2556 | 0.25673 | 0.22640 | 0.00128 |
| 0.50-0.60 | 1559 | 1553 | 1553 | 0.2421 | 0.24274 | 0.22677 | 0.00041 |
| 0.60-0.70 | 1163 | 1158 | 1158 | 0.2177 | 0.21844 | 0.20503 | 0.00127 |
| 0.70-0.80 | 846 | 846 | 846 | 0.1796 | 0.17995 | 0.17888 | 0.00154 |
| 0.80-0.90 | 591 | 590 | 590 | 0.1303 | 0.13000 | 0.13268 | -0.00010 |
| 0.90-1.00 | 502 | 502 | 502 | 0.0537 | 0.05371 | 0.05418 | 0.00036 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 8903 | 8742 | 8742 | 0.0848 | 0.08481 | 0.07690 | 0.00060 |
| 0.10-0.20 | 4531 | 4462 | 4462 | 0.1792 | 0.17939 | 0.15736 | 0.00055 |
| 0.20-0.30 | 2951 | 2911 | 2911 | 0.2334 | 0.23410 | 0.20600 | 0.00107 |
| 0.30-0.40 | 2230 | 2201 | 2201 | 0.2542 | 0.25520 | 0.21962 | 0.00110 |
| 0.40-0.50 | 1842 | 1814 | 1814 | 0.2564 | 0.25751 | 0.22492 | 0.00103 |
| 0.50-0.60 | 1591 | 1573 | 1573 | 0.2433 | 0.24410 | 0.22757 | 0.00047 |
| 0.60-0.70 | 1195 | 1173 | 1173 | 0.2207 | 0.22127 | 0.20528 | 0.00098 |
| 0.70-0.80 | 856 | 853 | 853 | 0.1819 | 0.18245 | 0.18229 | 0.00149 |
| 0.80-0.90 | 651 | 649 | 649 | 0.1394 | 0.13900 | 0.14066 | 0.00007 |
| 0.90-1.00 | 534 | 534 | 534 | 0.0556 | 0.05563 | 0.05629 | 0.00056 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 3963 | 3889 | 3889 | 0.2084 | 0.20898 | 0.18696 | 0.00029 |
| 20%+ | 3700 | 3585 | 3585 | 0.3016 | 0.30359 | 0.21758 | 0.00327 |
| 3-5% | 3038 | 3004 | 3004 | 0.1302 | 0.13012 | 0.12870 | 0.00018 |
| 5-10% | 4111 | 4041 | 4041 | 0.1646 | 0.16470 | 0.15764 | 0.00068 |
| <3% | 10472 | 10393 | 10393 | 0.1168 | 0.11678 | 0.11645 | 0.00023 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 16980 | 16694 | 16694 | 0.1776 | 0.17848 | 0.15362 | 0.00098 |
| none | 3 | 3 | 3 | 0.0143 | 0.01429 | 0.01429 | 0.00000 |
| yes | 8301 | 8215 | 8215 | 0.1457 | 0.14507 | 0.14322 | 0.00027 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 10559 | 10391 | 10391 | 0.1718 | 0.17197 | 0.15563 | 0.00073 |
| 6-24h | 209 | 151 | 151 | 0.0670 | 0.06708 | 0.06245 | 0.00136 |
| 90m-6h | 13142 | 13101 | 13101 | 0.1652 | 0.16581 | 0.14675 | 0.00058 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 102 | 2 | 2 | 0.0340 | 0.03248 | 0.00450 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 25284 | 24912 | 24912 | 0.1671 | 0.16744 | 0.15017 | 0.00075 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |
| 2 | 6132 | 6063 | 6063 | 0.1586 | 0.15895 | 0.14573 | 0.00045 |
| 3 | 6059 | 5981 | 5981 | 0.1629 | 0.16349 | 0.14506 | 0.00053 |
| 4 | 6007 | 5911 | 5911 | 0.1711 | 0.17149 | 0.15025 | 0.00071 |

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
| 3-5c | 6224 | 6142 | 6142 | 0.1439 | 0.14436 | 0.12502 | 0.00072 |
| 6-10c | 857 | 811 | 811 | 0.1731 | 0.17350 | 0.15472 | 0.00192 |
| <=2c | 17440 | 17269 | 17269 | 0.1737 | 0.17401 | 0.15762 | 0.00042 |
| >10c | 763 | 690 | 690 | 0.2007 | 0.20128 | 0.18238 | 0.00852 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 6007 | 5911 | 5911 | 0.1711 | 0.17149 | 0.15025 | 0.00071 |
| none | 19277 | 19001 | 19001 | 0.1658 | 0.16618 | 0.15015 | 0.00076 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| DOUBTFUL | 30 | 0 | 0 | - | - | - | - |
| EXPECTED_ACTIVE | 20011 | 19896 | 19896 | 0.1693 | 0.16981 | 0.14839 | 0.00086 |
| EXPECTED_OUT | 42 | 0 | 0 | - | - | - | -0.14750 |
| None | 4907 | 4907 | 4907 | 0.1583 | 0.15830 | 0.15843 | 0.00059 |
| OUT | 151 | 0 | 0 | - | - | - | -0.00105 |
| QUESTIONABLE | 120 | 89 | 89 | 0.1569 | 0.16290 | 0.11494 | 0.00044 |
| UNKNOWN | 23 | 20 | 20 | 0.0811 | 0.07316 | 0.05227 | 0.00025 |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
