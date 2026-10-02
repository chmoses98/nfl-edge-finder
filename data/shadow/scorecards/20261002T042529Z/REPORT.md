# Shadow evaluation scorecard (20261002T042529Z)

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 428490 | 19277 | 48 |
| **latest pregame per contract (primary)** | 19277 | 19277 | 48 |

The raw view holds 428490 snapshots of 19277 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 12921 |
| SETTLED | 415569 |

| close status | n |
|---|---|
| OK | 413218 |
| OK_STALE | 15272 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 19001 contracts whose payout is a 0/1 realisation (276 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 19001 | 0.1658 | 0.5043 | 0.2720 | 0.3280 | -0.0560 |
| market mid (only where value == event probability) | 3646 | 0.1658 | 0.4992 | 0.4084 | 0.4128 | -0.0044 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 6466 | 0.0415 | 0.0829 |
| 0.10-0.20 | 3378 | 0.1466 | 0.2250 |
| 0.20-0.30 | 2217 | 0.2461 | 0.3365 |
| 0.30-0.40 | 1727 | 0.3475 | 0.4354 |
| 0.40-0.50 | 1432 | 0.4482 | 0.5210 |
| 0.50-0.60 | 1237 | 0.5466 | 0.6023 |
| 0.60-0.70 | 941 | 0.6496 | 0.6738 |
| 0.70-0.80 | 691 | 0.7477 | 0.7554 |
| 0.80-0.90 | 509 | 0.8444 | 0.8251 |
| 0.90-1.00 | 403 | 0.9507 | 0.9231 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 19001 contracts whose payout is exactly known (0 settled without an exact payout, 276 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 19001 | 0.16618 | 0.30055 | -0.05962 | 0.2684 | 0.3280 |
| market mid at the same snapshot | 19001 | 0.15015 | 0.29663 | -0.00670 | 0.3213 | 0.3280 |

On the 18732 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 18732 | 0.16687 | 0.30181 | -0.05986 | 0.2689 | 0.3288 |
| market mid at snapshot | 18732 | 0.15082 | 0.29804 | -0.00619 | 0.3226 | 0.3288 |
| market mid at close | 18732 | 0.15112 | 0.29845 | -0.00693 | 0.3219 | 0.3288 |

Lower is better: **the closing market** is ahead by 0.01576 in squared payout error on this set.

## 3. Closing-line value and market movement

On 18819 contracts with a legitimate close (458 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00076**
* mean signed CLV (executable, crossing the spread): **0.00216**
* share with positive midpoint CLV: 0.2555
* movement: {'away': 4155, 'toward': 4770, 'unchanged': 9894}
* toward-share of directional moves: 0.5345 on 8925 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 458 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00027
* toward-share of directional moves: 0.7333 on 30 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 5504 | 13773 | 1443/1521/1559 | 0.1702 | 0.17055 | 0.15525 |
| T-6h | 3273 | 16004 | 361/389/477 | 0.1520 | 0.15274 | 0.13108 |
| T-90m | 9153 | 10124 | 96/136/207 | 0.1671 | 0.16768 | 0.14852 |
| T-30m | 13627 | 5650 | 32/66/150 | 0.1694 | 0.16984 | 0.15397 |
| latest pregame | 19277 | - | 0/83/5721 | 0.1658 | 0.16618 | 0.15015 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 192 | 192 | 192 | 0.1434 | 0.14342 | 0.13945 | -0.00579 |
| GAME_WINNER | 96 | 96 | 96 | 0.2318 | 0.23180 | 0.23302 | 0.00083 |
| PLAYER_STAT | 15535 | 15259 | 15259 | 0.1654 | 0.16590 | 0.14589 | 0.00081 |
| SPREAD | 1233 | 1233 | 1233 | 0.1880 | 0.18801 | 0.18732 | 0.00056 |
| TEAM_TOTAL | 1309 | 1309 | 1309 | 0.1435 | 0.14347 | 0.14452 | 0.00145 |
| TOTAL | 912 | 912 | 912 | 0.1717 | 0.17171 | 0.17269 | 0.00034 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 96 | 96 | 96 | 0.2318 | 0.23180 | 0.23302 | 0.00083 |
| attempts | 552 | 541 | 541 | 0.2260 | 0.22379 | 0.21263 | 0.00276 |
| carries | 797 | 797 | 797 | 0.2848 | 0.28660 | 0.21314 | 0.00652 |
| completions | 552 | 541 | 541 | 0.1897 | 0.18913 | 0.19106 | 0.00615 |
| interceptions | 288 | 285 | 285 | 0.1233 | 0.12314 | 0.12554 | 0.00524 |
| margin | 1233 | 1233 | 1233 | 0.1880 | 0.18801 | 0.18732 | 0.00056 |
| min_team_points | 192 | 192 | 192 | 0.1434 | 0.14342 | 0.13945 | -0.00579 |
| passing_tds | 394 | 391 | 391 | 0.1604 | 0.16134 | 0.15775 | -0.00035 |
| passing_yards | 825 | 818 | 818 | 0.1628 | 0.16230 | 0.16310 | 0.00036 |
| receiving_yards | 4122 | 4043 | 4043 | 0.1681 | 0.16880 | 0.14976 | 0.00059 |
| receptions | 3605 | 3564 | 3564 | 0.1688 | 0.16967 | 0.13890 | -0.00006 |
| rushing_yards | 2339 | 2306 | 2306 | 0.1679 | 0.16870 | 0.14796 | -0.00070 |
| team_points | 1309 | 1309 | 1309 | 0.1435 | 0.14347 | 0.14452 | 0.00145 |
| total_points | 912 | 912 | 912 | 0.1717 | 0.17171 | 0.17269 | 0.00034 |
| touchdowns | 2061 | 1973 | 1973 | 0.0874 | 0.08749 | 0.08378 | 0.00033 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 6756 | 6546 | 6546 | 0.0763 | 0.07631 | 0.07014 | 0.00030 |
| 0.10-0.20 | 3420 | 3396 | 3396 | 0.1831 | 0.18328 | 0.16172 | 0.00090 |
| 0.20-0.30 | 2243 | 2227 | 2227 | 0.2328 | 0.23348 | 0.20786 | 0.00117 |
| 0.30-0.40 | 1719 | 1714 | 1714 | 0.2515 | 0.25250 | 0.21643 | 0.00135 |
| 0.40-0.50 | 1449 | 1437 | 1437 | 0.2553 | 0.25635 | 0.22833 | 0.00138 |
| 0.50-0.60 | 1225 | 1220 | 1220 | 0.2419 | 0.24278 | 0.22535 | 0.00034 |
| 0.60-0.70 | 944 | 941 | 941 | 0.2182 | 0.21894 | 0.20571 | 0.00118 |
| 0.70-0.80 | 680 | 680 | 680 | 0.1831 | 0.18345 | 0.18300 | 0.00170 |
| 0.80-0.90 | 461 | 460 | 460 | 0.1324 | 0.13243 | 0.13693 | -0.00040 |
| 0.90-1.00 | 380 | 380 | 380 | 0.0701 | 0.07003 | 0.07018 | -0.00006 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 6577 | 6466 | 6466 | 0.0760 | 0.07602 | 0.06986 | 0.00055 |
| 0.10-0.20 | 3428 | 3378 | 3378 | 0.1796 | 0.17977 | 0.15948 | 0.00074 |
| 0.20-0.30 | 2249 | 2217 | 2217 | 0.2309 | 0.23157 | 0.20645 | 0.00118 |
| 0.30-0.40 | 1750 | 1727 | 1727 | 0.2528 | 0.25375 | 0.21772 | 0.00103 |
| 0.40-0.50 | 1455 | 1432 | 1432 | 0.2557 | 0.25672 | 0.22605 | 0.00113 |
| 0.50-0.60 | 1253 | 1237 | 1237 | 0.2433 | 0.24420 | 0.22617 | 0.00033 |
| 0.60-0.70 | 959 | 941 | 941 | 0.2203 | 0.22111 | 0.20575 | 0.00084 |
| 0.70-0.80 | 693 | 691 | 691 | 0.1840 | 0.18465 | 0.18531 | 0.00159 |
| 0.80-0.90 | 510 | 509 | 509 | 0.1443 | 0.14402 | 0.14749 | -0.00016 |
| 0.90-1.00 | 403 | 403 | 403 | 0.0707 | 0.07062 | 0.07099 | 0.00037 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 3057 | 3007 | 3007 | 0.2093 | 0.21003 | 0.18845 | 0.00023 |
| 20%+ | 2670 | 2585 | 2585 | 0.2971 | 0.29925 | 0.21591 | 0.00378 |
| 3-5% | 2330 | 2302 | 2302 | 0.1278 | 0.12776 | 0.12669 | 0.00006 |
| 5-10% | 3168 | 3116 | 3116 | 0.1627 | 0.16269 | 0.15618 | 0.00069 |
| <3% | 8052 | 7991 | 7991 | 0.1191 | 0.11906 | 0.11886 | 0.00020 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 12762 | 12560 | 12560 | 0.1744 | 0.17529 | 0.15176 | 0.00107 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 6514 | 6440 | 6440 | 0.1490 | 0.14843 | 0.14702 | 0.00015 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 8570 | 8441 | 8441 | 0.1700 | 0.17029 | 0.15638 | 0.00094 |
| 6-24h | 159 | 120 | 120 | 0.0533 | 0.05343 | 0.04149 | 0.00066 |
| 90m-6h | 9203 | 9171 | 9171 | 0.1643 | 0.16486 | 0.14568 | 0.00035 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 73 | 2 | 2 | 0.0340 | 0.03248 | 0.00450 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 19277 | 19001 | 19001 | 0.1658 | 0.16618 | 0.15015 | 0.00076 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |
| 2 | 6132 | 6063 | 6063 | 0.1586 | 0.15895 | 0.14573 | 0.00045 |
| 3 | 6059 | 5981 | 5981 | 0.1629 | 0.16349 | 0.14506 | 0.00053 |

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

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 5209 | 5154 | 5154 | 0.1424 | 0.14288 | 0.12474 | 0.00072 |
| 6-10c | 825 | 788 | 788 | 0.1728 | 0.17334 | 0.15444 | 0.00179 |
| <=2c | 12506 | 12382 | 12382 | 0.1731 | 0.17346 | 0.15862 | 0.00032 |
| >10c | 737 | 677 | 677 | 0.2014 | 0.20207 | 0.18361 | 0.00868 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 19277 | 19001 | 19001 | 0.1658 | 0.16618 | 0.15015 | 0.00076 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| DOUBTFUL | 37 | 0 | 0 | - | - | - | - |
| EXPECTED_ACTIVE | 15313 | 15236 | 15236 | 0.1655 | 0.16599 | 0.14603 | 0.00091 |
| EXPECTED_OUT | 20 | 0 | 0 | - | - | - | -0.16500 |
| None | 3742 | 3742 | 3742 | 0.1673 | 0.16729 | 0.16750 | 0.00053 |
| OUT | 111 | 0 | 0 | - | - | - | -0.00095 |
| QUESTIONABLE | 49 | 21 | 21 | 0.1086 | 0.11987 | 0.05784 | 0.00333 |
| UNKNOWN | 5 | 2 | 2 | 0.0207 | 0.01737 | 0.01213 | -0.00500 |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
