# Shadow evaluation scorecard (20260925T120346Z)

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 323769 | 13636 | 33 |
| **latest pregame per contract (primary)** | 13636 | 13636 | 33 |

The raw view holds 323769 snapshots of 13636 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 9250 |
| SETTLED | 314519 |

| close status | n |
|---|---|
| OK | 313412 |
| OK_STALE | 10357 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 13438 contracts whose payout is a 0/1 realisation (198 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 13438 | 0.1685 | 0.5119 | 0.2775 | 0.3277 | -0.0502 |
| market mid (only where value == event probability) | 2505 | 0.1753 | 0.5236 | 0.4102 | 0.4148 | -0.0046 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 4429 | 0.0420 | 0.0820 |
| 0.10-0.20 | 2371 | 0.1466 | 0.2269 |
| 0.20-0.30 | 1592 | 0.2461 | 0.3367 |
| 0.30-0.40 | 1247 | 0.3480 | 0.4242 |
| 0.40-0.50 | 1044 | 0.4484 | 0.5019 |
| 0.50-0.60 | 894 | 0.5468 | 0.5850 |
| 0.60-0.70 | 704 | 0.6494 | 0.6719 |
| 0.70-0.80 | 515 | 0.7473 | 0.7301 |
| 0.80-0.90 | 365 | 0.8440 | 0.7973 |
| 0.90-1.00 | 277 | 0.9513 | 0.9061 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 13438 contracts whose payout is exactly known (0 settled without an exact payout, 198 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 13438 | 0.16887 | 0.30552 | -0.05397 | 0.2738 | 0.3277 |
| market mid at the same snapshot | 13438 | 0.15358 | 0.30131 | -0.00450 | 0.3232 | 0.3277 |

On the 13274 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 13274 | 0.16907 | 0.30595 | -0.05385 | 0.2737 | 0.3276 |
| market mid at snapshot | 13274 | 0.15385 | 0.30198 | -0.00378 | 0.3238 | 0.3276 |
| market mid at close | 13274 | 0.15421 | 0.30245 | -0.00465 | 0.3229 | 0.3276 |

Lower is better: **the closing market** is ahead by 0.01486 in squared payout error on this set.

## 3. Closing-line value and market movement

On 13340 contracts with a legitimate close (296 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00086**
* mean signed CLV (executable, crossing the spread): **0.00272**
* share with positive midpoint CLV: 0.2531
* movement: {'away': 2908, 'toward': 3345, 'unchanged': 7087}
* toward-share of directional moves: 0.5349 on 6253 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 296 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00020
* toward-share of directional moves: 0.9091 on 11 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 4861 | 8775 | 1443/1521/1559 | 0.1711 | 0.17143 | 0.15668 |
| T-6h | 1623 | 12013 | 361/391/477 | 0.1490 | 0.14952 | 0.13046 |
| T-90m | 4723 | 8913 | 96/117/207 | 0.1698 | 0.17032 | 0.15185 |
| T-30m | 11823 | 1813 | 32/57/150 | 0.1700 | 0.17038 | 0.15507 |
| latest pregame | 13636 | - | 0/57/3302 | 0.1685 | 0.16887 | 0.15358 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 132 | 132 | 132 | 0.1422 | 0.14216 | 0.13777 | -0.00504 |
| GAME_WINNER | 66 | 66 | 66 | 0.2273 | 0.22726 | 0.23091 | 0.00015 |
| PLAYER_STAT | 11065 | 10867 | 10867 | 0.1665 | 0.16689 | 0.14811 | 0.00094 |
| SPREAD | 846 | 846 | 846 | 0.2101 | 0.21014 | 0.20910 | 0.00043 |
| TEAM_TOTAL | 900 | 900 | 900 | 0.1522 | 0.15216 | 0.15226 | 0.00133 |
| TOTAL | 627 | 627 | 627 | 0.1710 | 0.17103 | 0.17056 | 0.00061 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 66 | 66 | 66 | 0.2273 | 0.22726 | 0.23091 | 0.00015 |
| attempts | 462 | 451 | 451 | 0.2296 | 0.22695 | 0.21579 | 0.00308 |
| carries | 649 | 649 | 649 | 0.2735 | 0.27532 | 0.21928 | 0.00761 |
| completions | 462 | 451 | 451 | 0.1919 | 0.19108 | 0.19471 | 0.00691 |
| interceptions | 198 | 195 | 195 | 0.1219 | 0.12162 | 0.12408 | 0.00722 |
| margin | 846 | 846 | 846 | 0.2101 | 0.21014 | 0.20910 | 0.00043 |
| min_team_points | 132 | 132 | 132 | 0.1422 | 0.14216 | 0.13777 | -0.00504 |
| passing_tds | 275 | 272 | 272 | 0.1502 | 0.15080 | 0.14803 | -0.00009 |
| passing_yards | 580 | 573 | 573 | 0.1707 | 0.16995 | 0.17313 | 0.00034 |
| receiving_yards | 2901 | 2846 | 2846 | 0.1704 | 0.17095 | 0.15192 | 0.00068 |
| receptions | 2506 | 2484 | 2484 | 0.1656 | 0.16645 | 0.13532 | -0.00023 |
| rushing_yards | 1626 | 1606 | 1606 | 0.1653 | 0.16614 | 0.14817 | -0.00130 |
| team_points | 900 | 900 | 900 | 0.1522 | 0.15216 | 0.15226 | 0.00133 |
| total_points | 627 | 627 | 627 | 0.1710 | 0.17103 | 0.17056 | 0.00061 |
| touchdowns | 1406 | 1340 | 1340 | 0.0876 | 0.08764 | 0.08351 | 0.00032 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 4638 | 4489 | 4489 | 0.0756 | 0.07563 | 0.07004 | 0.00039 |
| 0.10-0.20 | 2396 | 2381 | 2381 | 0.1845 | 0.18469 | 0.16156 | 0.00106 |
| 0.20-0.30 | 1610 | 1597 | 1597 | 0.2327 | 0.23339 | 0.20703 | 0.00120 |
| 0.30-0.40 | 1242 | 1237 | 1237 | 0.2476 | 0.24834 | 0.21830 | 0.00124 |
| 0.40-0.50 | 1064 | 1056 | 1056 | 0.2540 | 0.25477 | 0.23000 | 0.00168 |
| 0.50-0.60 | 890 | 885 | 885 | 0.2435 | 0.24413 | 0.22672 | 0.00034 |
| 0.60-0.70 | 703 | 701 | 701 | 0.2194 | 0.22027 | 0.21048 | 0.00151 |
| 0.70-0.80 | 509 | 509 | 509 | 0.1980 | 0.19790 | 0.19909 | 0.00221 |
| 0.80-0.90 | 322 | 321 | 321 | 0.1497 | 0.14955 | 0.15479 | -0.00079 |
| 0.90-1.00 | 262 | 262 | 262 | 0.0837 | 0.08356 | 0.08374 | -0.00035 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 4512 | 4429 | 4429 | 0.0754 | 0.07544 | 0.06977 | 0.00072 |
| 0.10-0.20 | 2401 | 2371 | 2371 | 0.1808 | 0.18098 | 0.15942 | 0.00083 |
| 0.20-0.30 | 1615 | 1592 | 1592 | 0.2304 | 0.23111 | 0.20513 | 0.00109 |
| 0.30-0.40 | 1265 | 1247 | 1247 | 0.2492 | 0.25003 | 0.21994 | 0.00095 |
| 0.40-0.50 | 1059 | 1044 | 1044 | 0.2541 | 0.25478 | 0.22767 | 0.00141 |
| 0.50-0.60 | 906 | 894 | 894 | 0.2450 | 0.24562 | 0.22804 | 0.00036 |
| 0.60-0.70 | 718 | 704 | 704 | 0.2211 | 0.22200 | 0.20861 | 0.00086 |
| 0.70-0.80 | 517 | 515 | 515 | 0.1969 | 0.19710 | 0.19932 | 0.00243 |
| 0.80-0.90 | 366 | 365 | 365 | 0.1632 | 0.16257 | 0.16758 | -0.00039 |
| 0.90-1.00 | 277 | 277 | 277 | 0.0856 | 0.08533 | 0.08571 | 0.00006 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 2210 | 2176 | 2176 | 0.2135 | 0.21433 | 0.19355 | -0.00007 |
| 20%+ | 1839 | 1784 | 1784 | 0.2954 | 0.29753 | 0.21822 | 0.00495 |
| 3-5% | 1650 | 1627 | 1627 | 0.1298 | 0.12967 | 0.12745 | 0.00008 |
| 5-10% | 2228 | 2191 | 2191 | 0.1648 | 0.16472 | 0.15872 | 0.00075 |
| <3% | 5709 | 5660 | 5660 | 0.1238 | 0.12372 | 0.12336 | 0.00021 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 8953 | 8806 | 8806 | 0.1770 | 0.17785 | 0.15526 | 0.00123 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 4682 | 4631 | 4631 | 0.1525 | 0.15183 | 0.15041 | 0.00016 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 8140 | 8085 | 8085 | 0.1700 | 0.17028 | 0.15575 | 0.00102 |
| 6-24h | 57 | 18 | 18 | 0.0681 | 0.06749 | 0.05636 | 0.01958 |
| 90m-6h | 4098 | 4067 | 4067 | 0.1690 | 0.16955 | 0.15039 | -0.00002 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 69 | 1 | 1 | 0.0653 | 0.06229 | 0.00810 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 13636 | 13438 | 13438 | 0.1685 | 0.16887 | 0.15358 | 0.00086 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |
| 2 | 6132 | 6063 | 6063 | 0.1586 | 0.15895 | 0.14573 | 0.00045 |
| 3 | 418 | 418 | 418 | 0.2136 | 0.21434 | 0.18765 | 0.00094 |

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
| 2026_03_ATL_GB | 418 | 418 | 418 | 0.2136 | 0.21434 | 0.18765 | 0.00094 |

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 3973 | 3934 | 3934 | 0.1469 | 0.14735 | 0.12930 | 0.00076 |
| 6-10c | 769 | 733 | 733 | 0.1724 | 0.17292 | 0.15353 | 0.00107 |
| <=2c | 8161 | 8097 | 8097 | 0.1759 | 0.17615 | 0.16282 | 0.00031 |
| >10c | 733 | 674 | 674 | 0.2020 | 0.20264 | 0.18427 | 0.00860 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 13636 | 13438 | 13438 | 0.1685 | 0.16887 | 0.15358 | 0.00086 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| DOUBTFUL | 16 | 0 | 0 | - | - | - | - |
| EXPECTED_ACTIVE | 10903 | 10854 | 10854 | 0.1665 | 0.16686 | 0.14820 | 0.00108 |
| EXPECTED_OUT | 9 | 0 | 0 | - | - | - | -0.16500 |
| None | 2571 | 2571 | 2571 | 0.1773 | 0.17725 | 0.17670 | 0.00053 |
| OUT | 86 | 0 | 0 | - | - | - | -0.00118 |
| QUESTIONABLE | 48 | 13 | 13 | 0.1659 | 0.18762 | 0.06960 | 0.00385 |
| UNKNOWN | 3 | 0 | 0 | - | - | - | - |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
