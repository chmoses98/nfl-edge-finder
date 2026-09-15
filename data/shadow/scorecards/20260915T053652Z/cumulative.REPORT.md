# Shadow evaluation scorecard - cumulative

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 158197 | 6613 | 15 |
| **latest pregame per contract (primary)** | 6613 | 6613 | 15 |

The raw view holds 158197 snapshots of 6613 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 3225 |
| SETTLED | 154972 |

| close status | n |
|---|---|
| OK | 154201 |
| OK_STALE | 3996 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 6486 contracts whose payout is a 0/1 realisation (127 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 6486 | 0.1742 | 0.5257 | 0.2923 | 0.3571 | -0.0648 |
| market mid (only where value == event probability) | 1135 | 0.1763 | 0.5289 | 0.4135 | 0.4582 | -0.0447 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 1959 | 0.0426 | 0.0878 |
| 0.10-0.20 | 1114 | 0.1467 | 0.2379 |
| 0.20-0.30 | 780 | 0.2455 | 0.3538 |
| 0.30-0.40 | 642 | 0.3479 | 0.4424 |
| 0.40-0.50 | 553 | 0.4478 | 0.5009 |
| 0.50-0.60 | 476 | 0.5474 | 0.6134 |
| 0.60-0.70 | 376 | 0.6512 | 0.7048 |
| 0.70-0.80 | 282 | 0.7483 | 0.7553 |
| 0.80-0.90 | 174 | 0.8421 | 0.8621 |
| 0.90-1.00 | 130 | 0.9512 | 0.9385 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 6486 contracts whose payout is exactly known (0 settled without an exact payout, 127 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 6486 | 0.17466 | 0.31727 | -0.06901 | 0.2881 | 0.3571 |
| market mid at the same snapshot | 6486 | 0.15835 | 0.30965 | -0.03019 | 0.3269 | 0.3571 |

On the 6375 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 6375 | 0.17444 | 0.31720 | -0.06902 | 0.2880 | 0.3570 |
| market mid at snapshot | 6375 | 0.15813 | 0.30979 | -0.02901 | 0.3280 | 0.3570 |
| market mid at close | 6375 | 0.15875 | 0.31057 | -0.03086 | 0.3262 | 0.3570 |

Lower is better: **the closing market** is ahead by 0.01568 in squared payout error on this set.

## 3. Closing-line value and market movement

On 6437 contracts with a legitimate close (176 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00098**
* mean signed CLV (executable, crossing the spread): **0.00435**
* share with positive midpoint CLV: 0.2683
* movement: {'away': 1494, 'toward': 1708, 'unchanged': 3235}
* toward-share of directional moves: 0.5334 on 3202 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 176 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00031
* toward-share of directional moves: 0.9000 on 10 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 563 | 6050 | 1448/1455/1538 | 0.1663 | 0.16612 | 0.16007 |
| T-6h | 672 | 5941 | 363/457/477 | 0.1420 | 0.14199 | 0.12296 |
| T-90m | 2546 | 4067 | 99/109/207 | 0.1763 | 0.17667 | 0.15983 |
| T-30m | 5466 | 1147 | 32/44/150 | 0.1788 | 0.17938 | 0.16157 |
| latest pregame | 6613 | - | 0/44/2751 | 0.1742 | 0.17466 | 0.15835 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 60 | 60 | 60 | 0.1639 | 0.16387 | 0.16014 | -0.01079 |
| GAME_WINNER | 30 | 30 | 30 | 0.2112 | 0.21124 | 0.21196 | -0.00067 |
| PLAYER_STAT | 5448 | 5321 | 5321 | 0.1734 | 0.17393 | 0.15422 | 0.00120 |
| SPREAD | 379 | 379 | 379 | 0.2080 | 0.20800 | 0.20571 | 0.00041 |
| TEAM_TOTAL | 411 | 411 | 411 | 0.1478 | 0.14775 | 0.14858 | 0.00123 |
| TOTAL | 285 | 285 | 285 | 0.1810 | 0.18103 | 0.18052 | -0.00003 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 30 | 30 | 30 | 0.2112 | 0.21124 | 0.21196 | -0.00067 |
| attempts | 341 | 330 | 330 | 0.2304 | 0.22836 | 0.21680 | 0.00228 |
| carries | 437 | 437 | 437 | 0.2803 | 0.28235 | 0.22674 | 0.01055 |
| completions | 341 | 330 | 330 | 0.1882 | 0.18793 | 0.19479 | 0.00534 |
| interceptions | 93 | 90 | 90 | 0.1306 | 0.13038 | 0.13295 | 0.01306 |
| margin | 379 | 379 | 379 | 0.2080 | 0.20800 | 0.20571 | 0.00041 |
| min_team_points | 60 | 60 | 60 | 0.1639 | 0.16387 | 0.16014 | -0.01079 |
| passing_tds | 124 | 121 | 121 | 0.1504 | 0.15111 | 0.15033 | -0.00000 |
| passing_yards | 269 | 262 | 262 | 0.1764 | 0.17544 | 0.17278 | 0.00072 |
| receiving_yards | 1304 | 1282 | 1282 | 0.1712 | 0.17187 | 0.15355 | 0.00026 |
| receptions | 1148 | 1131 | 1131 | 0.1581 | 0.15891 | 0.13100 | 0.00011 |
| rushing_yards | 749 | 729 | 729 | 0.1713 | 0.17257 | 0.14495 | -0.00309 |
| team_points | 411 | 411 | 411 | 0.1478 | 0.14775 | 0.14858 | 0.00123 |
| total_points | 285 | 285 | 285 | 0.1810 | 0.18103 | 0.18052 | -0.00003 |
| touchdowns | 642 | 609 | 609 | 0.1030 | 0.10326 | 0.09790 | 0.00034 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 2101 | 1991 | 1991 | 0.0802 | 0.08025 | 0.07567 | 0.00042 |
| 0.10-0.20 | 1130 | 1123 | 1123 | 0.1927 | 0.19295 | 0.16847 | 0.00139 |
| 0.20-0.30 | 786 | 782 | 782 | 0.2416 | 0.24229 | 0.20851 | 0.00174 |
| 0.30-0.40 | 642 | 640 | 640 | 0.2503 | 0.25113 | 0.21831 | 0.00207 |
| 0.40-0.50 | 556 | 554 | 554 | 0.2532 | 0.25385 | 0.22906 | 0.00266 |
| 0.50-0.60 | 464 | 463 | 463 | 0.2401 | 0.24098 | 0.21882 | 0.00042 |
| 0.60-0.70 | 381 | 380 | 380 | 0.2093 | 0.21073 | 0.20776 | 0.00044 |
| 0.70-0.80 | 282 | 282 | 282 | 0.1806 | 0.18097 | 0.18807 | -0.00073 |
| 0.80-0.90 | 148 | 148 | 148 | 0.1093 | 0.10994 | 0.11896 | -0.00175 |
| 0.90-1.00 | 123 | 123 | 123 | 0.0533 | 0.05341 | 0.05401 | -0.00034 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 2005 | 1959 | 1959 | 0.0805 | 0.08059 | 0.07589 | 0.00117 |
| 0.10-0.20 | 1133 | 1114 | 1114 | 0.1881 | 0.18830 | 0.16586 | 0.00096 |
| 0.20-0.30 | 797 | 780 | 780 | 0.2383 | 0.23897 | 0.20555 | 0.00139 |
| 0.30-0.40 | 655 | 642 | 642 | 0.2534 | 0.25434 | 0.22109 | 0.00155 |
| 0.40-0.50 | 563 | 553 | 553 | 0.2518 | 0.25220 | 0.22327 | 0.00206 |
| 0.50-0.60 | 486 | 476 | 476 | 0.2416 | 0.24247 | 0.22268 | 0.00052 |
| 0.60-0.70 | 386 | 376 | 376 | 0.2117 | 0.21311 | 0.20546 | 0.00009 |
| 0.70-0.80 | 284 | 282 | 282 | 0.1843 | 0.18480 | 0.19246 | -0.00022 |
| 0.80-0.90 | 174 | 174 | 174 | 0.1198 | 0.12035 | 0.13119 | -0.00277 |
| 0.90-1.00 | 130 | 130 | 130 | 0.0571 | 0.05709 | 0.05792 | 0.00036 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 1102 | 1081 | 1081 | 0.2191 | 0.21973 | 0.19495 | -0.00096 |
| 20%+ | 882 | 825 | 825 | 0.2966 | 0.29858 | 0.21368 | 0.00834 |
| 3-5% | 778 | 766 | 766 | 0.1439 | 0.14399 | 0.14092 | -0.00045 |
| 5-10% | 1107 | 1090 | 1090 | 0.1695 | 0.16971 | 0.16499 | 0.00069 |
| <3% | 2744 | 2724 | 2724 | 0.1297 | 0.12984 | 0.12932 | 0.00005 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 4157 | 4055 | 4055 | 0.1847 | 0.18571 | 0.15945 | 0.00205 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 2455 | 2430 | 2430 | 0.1568 | 0.15627 | 0.15658 | -0.00081 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 3360 | 3336 | 3336 | 0.1784 | 0.17909 | 0.16032 | 0.00132 |
| 6-24h | 48 | 12 | 12 | 0.1013 | 0.10043 | 0.08397 | 0.00857 |
| 90m-6h | 1895 | 1870 | 1870 | 0.1774 | 0.17772 | 0.16007 | -0.00070 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 38 | 1 | 1 | 0.0653 | 0.06229 | 0.00810 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 6613 | 6486 | 6486 | 0.1742 | 0.17466 | 0.15835 | 0.00098 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 6613 | 6486 | 6486 | 0.1742 | 0.17466 | 0.15835 | 0.00098 |

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
| 2026_01_GB_MIN | 446 | 445 | 445 | 0.2181 | 0.21777 | 0.18373 | 0.00074 |
| 2026_01_MIA_LV | 420 | 385 | 385 | 0.1693 | 0.17017 | 0.14476 | -0.00161 |
| 2026_01_NE_SEA | 451 | 451 | 451 | 0.1633 | 0.16325 | 0.14665 | 0.00011 |
| 2026_01_NO_DET | 422 | 420 | 420 | 0.2157 | 0.21761 | 0.18134 | 0.00313 |
| 2026_01_NYJ_TEN | 429 | 427 | 427 | 0.1552 | 0.15499 | 0.13118 | 0.00033 |
| 2026_01_SF_LA | 510 | 508 | 508 | 0.1517 | 0.15129 | 0.15228 | 0.00078 |
| 2026_01_TB_CIN | 442 | 440 | 440 | 0.1409 | 0.14134 | 0.13030 | 0.00295 |
| 2026_01_WAS_PHI | 447 | 434 | 434 | 0.1370 | 0.13720 | 0.12624 | -0.00138 |

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 2187 | 2160 | 2160 | 0.1604 | 0.16090 | 0.14056 | 0.00084 |
| 6-10c | 643 | 621 | 621 | 0.1750 | 0.17561 | 0.15539 | 0.00093 |
| <=2c | 3138 | 3103 | 3103 | 0.1775 | 0.17776 | 0.16421 | 0.00016 |
| >10c | 645 | 602 | 602 | 0.2061 | 0.20707 | 0.19506 | 0.00638 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 6613 | 6486 | 6486 | 0.1742 | 0.17466 | 0.15835 | 0.00098 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| EXPECTED_ACTIVE | 5349 | 5321 | 5321 | 0.1734 | 0.17393 | 0.15422 | 0.00149 |
| EXPECTED_OUT | 9 | 0 | 0 | - | - | - | -0.16500 |
| None | 1165 | 1165 | 1165 | 0.1780 | 0.17796 | 0.17721 | 0.00000 |
| OUT | 89 | 0 | 0 | - | - | - | -0.00080 |
| UNKNOWN | 1 | 0 | 0 | - | - | - | - |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
