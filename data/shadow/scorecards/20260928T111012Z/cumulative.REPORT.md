# Shadow evaluation scorecard - cumulative

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 420490 | 18885 | 47 |
| **latest pregame per contract (primary)** | 18885 | 18885 | 47 |

The raw view holds 420490 snapshots of 18885 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 11467 |
| SETTLED | 409023 |

| close status | n |
|---|---|
| OK | 406357 |
| OK_STALE | 14133 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 18610 contracts whose payout is a 0/1 realisation (275 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 18610 | 0.1658 | 0.5043 | 0.2724 | 0.3285 | -0.0562 |
| market mid (only where value == event probability) | 3570 | 0.1642 | 0.4950 | 0.4090 | 0.4146 | -0.0056 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 6320 | 0.0415 | 0.0826 |
| 0.10-0.20 | 3305 | 0.1466 | 0.2263 |
| 0.20-0.30 | 2179 | 0.2461 | 0.3355 |
| 0.30-0.40 | 1689 | 0.3475 | 0.4352 |
| 0.40-0.50 | 1404 | 0.4482 | 0.5192 |
| 0.50-0.60 | 1216 | 0.5466 | 0.6028 |
| 0.60-0.70 | 921 | 0.6495 | 0.6754 |
| 0.70-0.80 | 681 | 0.7477 | 0.7577 |
| 0.80-0.90 | 501 | 0.8443 | 0.8244 |
| 0.90-1.00 | 394 | 0.9510 | 0.9264 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 18610 contracts whose payout is exactly known (0 settled without an exact payout, 275 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 18610 | 0.16615 | 0.30064 | -0.05974 | 0.2688 | 0.3285 |
| market mid at the same snapshot | 18610 | 0.15025 | 0.29681 | -0.00671 | 0.3218 | 0.3285 |

On the 18341 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 18341 | 0.16686 | 0.30193 | -0.05999 | 0.2693 | 0.3293 |
| market mid at snapshot | 18341 | 0.15094 | 0.29825 | -0.00619 | 0.3231 | 0.3293 |
| market mid at close | 18341 | 0.15122 | 0.29865 | -0.00694 | 0.3224 | 0.3293 |

Lower is better: **the closing market** is ahead by 0.01564 in squared payout error on this set.

## 3. Closing-line value and market movement

On 18428 contracts with a legitimate close (457 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00075**
* mean signed CLV (executable, crossing the spread): **0.00219**
* share with positive midpoint CLV: 0.2545
* movement: {'away': 4053, 'toward': 4651, 'unchanged': 9724}
* toward-share of directional moves: 0.5344 on 8704 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 457 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00027
* toward-share of directional moves: 0.7333 on 30 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 5225 | 13660 | 1443/1521/1559 | 0.1684 | 0.16880 | 0.15424 |
| T-6h | 3273 | 15612 | 361/389/477 | 0.1520 | 0.15274 | 0.13108 |
| T-90m | 9153 | 9732 | 96/136/207 | 0.1671 | 0.16768 | 0.14852 |
| T-30m | 13627 | 5258 | 32/66/150 | 0.1694 | 0.16984 | 0.15397 |
| latest pregame | 18885 | - | 0/83/5721 | 0.1658 | 0.16615 | 0.15025 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 188 | 188 | 188 | 0.1439 | 0.14388 | 0.13994 | -0.00590 |
| GAME_WINNER | 94 | 94 | 94 | 0.2281 | 0.22811 | 0.22912 | 0.00064 |
| PLAYER_STAT | 15221 | 14946 | 14946 | 0.1657 | 0.16625 | 0.14641 | 0.00081 |
| SPREAD | 1208 | 1208 | 1208 | 0.1844 | 0.18437 | 0.18352 | 0.00056 |
| TEAM_TOTAL | 1281 | 1281 | 1281 | 0.1420 | 0.14198 | 0.14291 | 0.00127 |
| TOTAL | 893 | 893 | 893 | 0.1728 | 0.17284 | 0.17375 | 0.00047 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 94 | 94 | 94 | 0.2281 | 0.22811 | 0.22912 | 0.00064 |
| attempts | 546 | 535 | 535 | 0.2265 | 0.22427 | 0.21261 | 0.00300 |
| carries | 783 | 783 | 783 | 0.2843 | 0.28613 | 0.21402 | 0.00662 |
| completions | 546 | 535 | 535 | 0.1901 | 0.18952 | 0.19098 | 0.00628 |
| interceptions | 282 | 279 | 279 | 0.1234 | 0.12326 | 0.12575 | 0.00520 |
| margin | 1208 | 1208 | 1208 | 0.1844 | 0.18437 | 0.18352 | 0.00056 |
| min_team_points | 188 | 188 | 188 | 0.1439 | 0.14388 | 0.13994 | -0.00590 |
| passing_tds | 387 | 384 | 384 | 0.1597 | 0.16069 | 0.15673 | -0.00048 |
| passing_yards | 807 | 800 | 800 | 0.1635 | 0.16308 | 0.16316 | 0.00048 |
| receiving_yards | 4040 | 3961 | 3961 | 0.1687 | 0.16937 | 0.15014 | 0.00054 |
| receptions | 3529 | 3488 | 3488 | 0.1686 | 0.16946 | 0.13931 | -0.00012 |
| rushing_yards | 2284 | 2251 | 2251 | 0.1687 | 0.16943 | 0.14956 | -0.00072 |
| team_points | 1281 | 1281 | 1281 | 0.1420 | 0.14198 | 0.14291 | 0.00127 |
| total_points | 893 | 893 | 893 | 0.1728 | 0.17284 | 0.17375 | 0.00047 |
| touchdowns | 2017 | 1930 | 1930 | 0.0877 | 0.08775 | 0.08382 | 0.00036 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 6614 | 6400 | 6400 | 0.0761 | 0.07609 | 0.06989 | 0.00028 |
| 0.10-0.20 | 3344 | 3322 | 3322 | 0.1841 | 0.18438 | 0.16237 | 0.00086 |
| 0.20-0.30 | 2202 | 2189 | 2189 | 0.2321 | 0.23280 | 0.20758 | 0.00109 |
| 0.30-0.40 | 1681 | 1676 | 1676 | 0.2514 | 0.25238 | 0.21757 | 0.00139 |
| 0.40-0.50 | 1421 | 1410 | 1410 | 0.2550 | 0.25603 | 0.22867 | 0.00140 |
| 0.50-0.60 | 1205 | 1199 | 1199 | 0.2417 | 0.24256 | 0.22533 | 0.00028 |
| 0.60-0.70 | 922 | 919 | 919 | 0.2175 | 0.21830 | 0.20585 | 0.00120 |
| 0.70-0.80 | 672 | 672 | 672 | 0.1823 | 0.18276 | 0.18147 | 0.00183 |
| 0.80-0.90 | 452 | 451 | 451 | 0.1331 | 0.13310 | 0.13710 | -0.00032 |
| 0.90-1.00 | 372 | 372 | 372 | 0.0667 | 0.06662 | 0.06677 | -0.00000 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 6431 | 6320 | 6320 | 0.0758 | 0.07579 | 0.06959 | 0.00054 |
| 0.10-0.20 | 3354 | 3305 | 3305 | 0.1806 | 0.18075 | 0.16005 | 0.00069 |
| 0.20-0.30 | 2211 | 2179 | 2179 | 0.2304 | 0.23106 | 0.20616 | 0.00110 |
| 0.30-0.40 | 1712 | 1689 | 1689 | 0.2525 | 0.25345 | 0.21899 | 0.00106 |
| 0.40-0.50 | 1427 | 1404 | 1404 | 0.2555 | 0.25648 | 0.22633 | 0.00114 |
| 0.50-0.60 | 1232 | 1216 | 1216 | 0.2431 | 0.24400 | 0.22615 | 0.00028 |
| 0.60-0.70 | 939 | 921 | 921 | 0.2198 | 0.22068 | 0.20579 | 0.00081 |
| 0.70-0.80 | 683 | 681 | 681 | 0.1830 | 0.18368 | 0.18390 | 0.00178 |
| 0.80-0.90 | 502 | 501 | 501 | 0.1449 | 0.14456 | 0.14757 | -0.00007 |
| 0.90-1.00 | 394 | 394 | 394 | 0.0676 | 0.06756 | 0.06793 | 0.00042 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 2988 | 2941 | 2941 | 0.2104 | 0.21121 | 0.18978 | 0.00016 |
| 20%+ | 2607 | 2523 | 2523 | 0.2978 | 0.29986 | 0.21678 | 0.00384 |
| 3-5% | 2284 | 2254 | 2254 | 0.1276 | 0.12761 | 0.12653 | 0.00004 |
| 5-10% | 3113 | 3059 | 3059 | 0.1626 | 0.16261 | 0.15630 | 0.00070 |
| <3% | 7893 | 7833 | 7833 | 0.1187 | 0.11865 | 0.11843 | 0.00019 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 12503 | 12294 | 12294 | 0.1745 | 0.17543 | 0.15211 | 0.00106 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 6381 | 6315 | 6315 | 0.1487 | 0.14812 | 0.14664 | 0.00014 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 8570 | 8441 | 8441 | 0.1700 | 0.17029 | 0.15638 | 0.00094 |
| 6-24h | 156 | 117 | 117 | 0.0547 | 0.05478 | 0.04255 | 0.00063 |
| 90m-6h | 8815 | 8783 | 8783 | 0.1641 | 0.16469 | 0.14565 | 0.00031 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 72 | 2 | 2 | 0.0340 | 0.03248 | 0.00450 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 18885 | 18610 | 18610 | 0.1658 | 0.16615 | 0.15025 | 0.00075 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |
| 2 | 6132 | 6063 | 6063 | 0.1586 | 0.15895 | 0.14573 | 0.00045 |
| 3 | 5667 | 5590 | 5590 | 0.1626 | 0.16323 | 0.14504 | 0.00048 |

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
| 2026_03_SEA_WAS | 377 | 377 | 377 | 0.1817 | 0.18315 | 0.18829 | 0.00000 |
| 2026_03_TEN_NYG | 366 | 351 | 351 | 0.1461 | 0.14629 | 0.12764 | -0.00017 |

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 5141 | 5086 | 5086 | 0.1425 | 0.14295 | 0.12523 | 0.00072 |
| 6-10c | 824 | 787 | 787 | 0.1723 | 0.17277 | 0.15416 | 0.00165 |
| <=2c | 12184 | 12061 | 12061 | 0.1731 | 0.17348 | 0.15866 | 0.00030 |
| >10c | 736 | 676 | 676 | 0.2017 | 0.20234 | 0.18376 | 0.00865 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 18885 | 18610 | 18610 | 0.1658 | 0.16615 | 0.15025 | 0.00075 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| DOUBTFUL | 26 | 0 | 0 | - | - | - | - |
| EXPECTED_ACTIVE | 14991 | 14923 | 14923 | 0.1658 | 0.16633 | 0.14656 | 0.00091 |
| EXPECTED_OUT | 20 | 0 | 0 | - | - | - | -0.16500 |
| None | 3664 | 3664 | 3664 | 0.1658 | 0.16578 | 0.16588 | 0.00049 |
| OUT | 130 | 0 | 0 | - | - | - | -0.00080 |
| QUESTIONABLE | 49 | 21 | 21 | 0.1086 | 0.11987 | 0.05784 | 0.00333 |
| UNKNOWN | 5 | 2 | 2 | 0.0207 | 0.01737 | 0.01213 | -0.00500 |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
