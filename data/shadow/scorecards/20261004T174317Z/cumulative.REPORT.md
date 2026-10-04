# Shadow evaluation scorecard - cumulative

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 435028 | 19652 | 49 |
| **latest pregame per contract (primary)** | 19652 | 19652 | 49 |

The raw view holds 435028 snapshots of 19652 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 13779 |
| SETTLED | 421249 |

| close status | n |
|---|---|
| OK | 419129 |
| OK_STALE | 15899 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 19376 contracts whose payout is a 0/1 realisation (276 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 19376 | 0.1662 | 0.5054 | 0.2713 | 0.3296 | -0.0583 |
| market mid (only where value == event probability) | 3722 | 0.1653 | 0.4978 | 0.4077 | 0.4143 | -0.0066 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 6613 | 0.0415 | 0.0836 |
| 0.10-0.20 | 3447 | 0.1466 | 0.2269 |
| 0.20-0.30 | 2262 | 0.2461 | 0.3391 |
| 0.30-0.40 | 1759 | 0.3475 | 0.4400 |
| 0.40-0.50 | 1457 | 0.4482 | 0.5244 |
| 0.50-0.60 | 1255 | 0.5466 | 0.6056 |
| 0.60-0.70 | 957 | 0.6496 | 0.6782 |
| 0.70-0.80 | 698 | 0.7477 | 0.7579 |
| 0.80-0.90 | 519 | 0.8446 | 0.8285 |
| 0.90-1.00 | 409 | 0.9506 | 0.9242 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 19376 contracts whose payout is exactly known (0 settled without an exact payout, 276 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 19376 | 0.16660 | 0.30076 | -0.06184 | 0.2677 | 0.3296 |
| market mid at the same snapshot | 19376 | 0.15015 | 0.29656 | -0.00863 | 0.3210 | 0.3296 |

On the 19107 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 19107 | 0.16729 | 0.30200 | -0.06210 | 0.2682 | 0.3303 |
| market mid at snapshot | 19107 | 0.15082 | 0.29794 | -0.00815 | 0.3222 | 0.3303 |
| market mid at close | 19107 | 0.15111 | 0.29835 | -0.00887 | 0.3215 | 0.3303 |

Lower is better: **the closing market** is ahead by 0.01618 in squared payout error on this set.

## 3. Closing-line value and market movement

On 19194 contracts with a legitimate close (458 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00076**
* mean signed CLV (executable, crossing the spread): **0.00213**
* share with positive midpoint CLV: 0.2539
* movement: {'away': 4203, 'toward': 4836, 'unchanged': 10155}
* toward-share of directional moves: 0.5350 on 9039 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 458 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00027
* toward-share of directional moves: 0.7333 on 30 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 5511 | 14141 | 1443/1521/1559 | 0.1700 | 0.17034 | 0.15506 |
| T-6h | 3635 | 16017 | 361/389/477 | 0.1561 | 0.15688 | 0.13335 |
| T-90m | 9528 | 10124 | 96/124/207 | 0.1679 | 0.16849 | 0.14860 |
| T-30m | 13993 | 5659 | 32/71/150 | 0.1699 | 0.17037 | 0.15391 |
| latest pregame | 19652 | - | 0/87/5721 | 0.1662 | 0.16660 | 0.15015 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 196 | 196 | 196 | 0.1445 | 0.14450 | 0.14090 | -0.00569 |
| GAME_WINNER | 98 | 98 | 98 | 0.2345 | 0.23452 | 0.23501 | 0.00122 |
| PLAYER_STAT | 15832 | 15556 | 15556 | 0.1660 | 0.16657 | 0.14599 | 0.00080 |
| SPREAD | 1258 | 1258 | 1258 | 0.1865 | 0.18647 | 0.18570 | 0.00058 |
| TEAM_TOTAL | 1337 | 1337 | 1337 | 0.1427 | 0.14273 | 0.14409 | 0.00147 |
| TOTAL | 931 | 931 | 931 | 0.1721 | 0.17208 | 0.17337 | 0.00038 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 98 | 98 | 98 | 0.2345 | 0.23452 | 0.23501 | 0.00122 |
| attempts | 558 | 547 | 547 | 0.2259 | 0.22378 | 0.21263 | 0.00271 |
| carries | 806 | 806 | 806 | 0.2866 | 0.28838 | 0.21202 | 0.00644 |
| completions | 558 | 547 | 547 | 0.1893 | 0.18882 | 0.19164 | 0.00609 |
| interceptions | 294 | 291 | 291 | 0.1245 | 0.12444 | 0.12740 | 0.00516 |
| margin | 1258 | 1258 | 1258 | 0.1865 | 0.18647 | 0.18570 | 0.00058 |
| min_team_points | 196 | 196 | 196 | 0.1445 | 0.14450 | 0.14090 | -0.00569 |
| passing_tds | 402 | 399 | 399 | 0.1609 | 0.16190 | 0.15814 | -0.00034 |
| passing_yards | 841 | 834 | 834 | 0.1627 | 0.16240 | 0.16429 | 0.00042 |
| receiving_yards | 4206 | 4127 | 4127 | 0.1702 | 0.17082 | 0.15082 | 0.00058 |
| receptions | 3686 | 3645 | 3645 | 0.1690 | 0.16991 | 0.13859 | -0.00007 |
| rushing_yards | 2385 | 2352 | 2352 | 0.1672 | 0.16796 | 0.14646 | -0.00066 |
| team_points | 1337 | 1337 | 1337 | 0.1427 | 0.14273 | 0.14409 | 0.00147 |
| total_points | 931 | 931 | 931 | 0.1721 | 0.17208 | 0.17337 | 0.00038 |
| touchdowns | 2096 | 2008 | 2008 | 0.0883 | 0.08836 | 0.08456 | 0.00032 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 6903 | 6695 | 6695 | 0.0770 | 0.07702 | 0.07087 | 0.00030 |
| 0.10-0.20 | 3489 | 3465 | 3465 | 0.1844 | 0.18465 | 0.16188 | 0.00088 |
| 0.20-0.30 | 2286 | 2270 | 2270 | 0.2338 | 0.23451 | 0.20768 | 0.00117 |
| 0.30-0.40 | 1754 | 1748 | 1748 | 0.2529 | 0.25392 | 0.21694 | 0.00136 |
| 0.40-0.50 | 1474 | 1462 | 1462 | 0.2556 | 0.25674 | 0.22837 | 0.00135 |
| 0.50-0.60 | 1244 | 1238 | 1238 | 0.2414 | 0.24234 | 0.22539 | 0.00036 |
| 0.60-0.70 | 961 | 958 | 958 | 0.2165 | 0.21739 | 0.20434 | 0.00117 |
| 0.70-0.80 | 685 | 685 | 685 | 0.1821 | 0.18250 | 0.18213 | 0.00168 |
| 0.80-0.90 | 470 | 469 | 469 | 0.1302 | 0.13033 | 0.13485 | -0.00036 |
| 0.90-1.00 | 386 | 386 | 386 | 0.0691 | 0.06899 | 0.06916 | -0.00000 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 6724 | 6613 | 6613 | 0.0766 | 0.07664 | 0.07047 | 0.00054 |
| 0.10-0.20 | 3497 | 3447 | 3447 | 0.1809 | 0.18109 | 0.15971 | 0.00073 |
| 0.20-0.30 | 2294 | 2262 | 2262 | 0.2323 | 0.23300 | 0.20652 | 0.00117 |
| 0.30-0.40 | 1782 | 1759 | 1759 | 0.2541 | 0.25513 | 0.21840 | 0.00105 |
| 0.40-0.50 | 1480 | 1457 | 1457 | 0.2561 | 0.25710 | 0.22564 | 0.00111 |
| 0.50-0.60 | 1271 | 1255 | 1255 | 0.2429 | 0.24388 | 0.22656 | 0.00035 |
| 0.60-0.70 | 975 | 957 | 957 | 0.2189 | 0.21981 | 0.20460 | 0.00084 |
| 0.70-0.80 | 700 | 698 | 698 | 0.1828 | 0.18353 | 0.18426 | 0.00157 |
| 0.80-0.90 | 520 | 519 | 519 | 0.1419 | 0.14173 | 0.14529 | -0.00013 |
| 0.90-1.00 | 409 | 409 | 409 | 0.0697 | 0.06964 | 0.07002 | 0.00042 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 3118 | 3068 | 3068 | 0.2094 | 0.21022 | 0.18906 | 0.00024 |
| 20%+ | 2737 | 2652 | 2652 | 0.2986 | 0.30073 | 0.21436 | 0.00371 |
| 3-5% | 2381 | 2353 | 2353 | 0.1291 | 0.12914 | 0.12810 | 0.00004 |
| 5-10% | 3235 | 3186 | 3186 | 0.1631 | 0.16315 | 0.15662 | 0.00066 |
| <3% | 8181 | 8117 | 8117 | 0.1185 | 0.11851 | 0.11833 | 0.00023 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 13004 | 12808 | 12808 | 0.1751 | 0.17598 | 0.15164 | 0.00105 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 6647 | 6567 | 6567 | 0.1489 | 0.14833 | 0.14728 | 0.00018 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 8570 | 8441 | 8441 | 0.1700 | 0.17029 | 0.15638 | 0.00094 |
| 6-24h | 159 | 120 | 120 | 0.0533 | 0.05343 | 0.04149 | 0.00066 |
| 90m-6h | 9578 | 9546 | 9546 | 0.1651 | 0.16577 | 0.14587 | 0.00036 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 73 | 2 | 2 | 0.0340 | 0.03248 | 0.00450 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 19652 | 19376 | 19376 | 0.1662 | 0.16660 | 0.15015 | 0.00076 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |
| 2 | 6132 | 6063 | 6063 | 0.1586 | 0.15895 | 0.14573 | 0.00045 |
| 3 | 6059 | 5981 | 5981 | 0.1629 | 0.16349 | 0.14506 | 0.00053 |
| 4 | 375 | 375 | 375 | 0.1867 | 0.18805 | 0.15054 | 0.00068 |

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
| 2026_04_PIT_CLE | 375 | 375 | 375 | 0.1867 | 0.18805 | 0.15054 | 0.00068 |

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 5233 | 5178 | 5178 | 0.1420 | 0.14247 | 0.12431 | 0.00072 |
| 6-10c | 826 | 789 | 789 | 0.1726 | 0.17312 | 0.15425 | 0.00180 |
| <=2c | 12856 | 12732 | 12732 | 0.1737 | 0.17413 | 0.15863 | 0.00032 |
| >10c | 737 | 677 | 677 | 0.2014 | 0.20207 | 0.18361 | 0.00868 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 375 | 375 | 375 | 0.1867 | 0.18805 | 0.15054 | 0.00068 |
| none | 19277 | 19001 | 19001 | 0.1658 | 0.16618 | 0.15015 | 0.00076 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| DOUBTFUL | 31 | 0 | 0 | - | - | - | - |
| EXPECTED_ACTIVE | 15608 | 15525 | 15525 | 0.1662 | 0.16668 | 0.14613 | 0.00090 |
| EXPECTED_OUT | 21 | 0 | 0 | - | - | - | -0.16500 |
| None | 3820 | 3820 | 3820 | 0.1667 | 0.16673 | 0.16710 | 0.00056 |
| OUT | 110 | 0 | 0 | - | - | - | -0.00105 |
| QUESTIONABLE | 57 | 29 | 29 | 0.1078 | 0.11690 | 0.08207 | 0.00224 |
| UNKNOWN | 5 | 2 | 2 | 0.0207 | 0.01737 | 0.01213 | -0.00500 |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
