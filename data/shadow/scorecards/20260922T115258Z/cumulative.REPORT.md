# Shadow evaluation scorecard - cumulative

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 316362 | 13218 | 32 |
| **latest pregame per contract (primary)** | 13218 | 13218 | 32 |

The raw view holds 316362 snapshots of 13218 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 8312 |
| SETTLED | 308050 |

| close status | n |
|---|---|
| OK | 306985 |
| OK_STALE | 9377 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 13020 contracts whose payout is a 0/1 realisation (198 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 13020 | 0.1671 | 0.5073 | 0.2789 | 0.3263 | -0.0474 |
| market mid (only where value == event probability) | 2427 | 0.1730 | 0.5176 | 0.4112 | 0.4124 | -0.0013 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 4267 | 0.0421 | 0.0785 |
| 0.10-0.20 | 2294 | 0.1466 | 0.2228 |
| 0.20-0.30 | 1539 | 0.2461 | 0.3353 |
| 0.30-0.40 | 1208 | 0.3479 | 0.4205 |
| 0.40-0.50 | 1021 | 0.4484 | 0.4976 |
| 0.50-0.60 | 873 | 0.5469 | 0.5865 |
| 0.60-0.70 | 685 | 0.6495 | 0.6715 |
| 0.70-0.80 | 507 | 0.7473 | 0.7318 |
| 0.80-0.90 | 355 | 0.8438 | 0.7944 |
| 0.90-1.00 | 271 | 0.9513 | 0.9041 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 13020 contracts whose payout is exactly known (0 settled without an exact payout, 198 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 13020 | 0.16741 | 0.30445 | -0.05119 | 0.2751 | 0.3263 |
| market mid at the same snapshot | 13020 | 0.15248 | 0.30035 | -0.00276 | 0.3235 | 0.3263 |

On the 12859 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 12859 | 0.16756 | 0.30481 | -0.05102 | 0.2750 | 0.3260 |
| market mid at snapshot | 12859 | 0.15271 | 0.30097 | -0.00198 | 0.3240 | 0.3260 |
| market mid at close | 12859 | 0.15311 | 0.30147 | -0.00288 | 0.3231 | 0.3260 |

Lower is better: **the closing market** is ahead by 0.01445 in squared payout error on this set.

## 3. Closing-line value and market movement

On 12925 contracts with a legitimate close (293 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00086**
* mean signed CLV (executable, crossing the spread): **0.00278**
* share with positive midpoint CLV: 0.2536
* movement: {'away': 2855, 'toward': 3247, 'unchanged': 6823}
* toward-share of directional moves: 0.5321 on 6102 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 293 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00020
* toward-share of directional moves: 0.9091 on 11 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 4775 | 8443 | 1443/1521/1559 | 0.1712 | 0.17155 | 0.15685 |
| T-6h | 1573 | 11645 | 361/391/477 | 0.1497 | 0.15026 | 0.13097 |
| T-90m | 4717 | 8501 | 96/117/207 | 0.1700 | 0.17049 | 0.15203 |
| T-30m | 11406 | 1812 | 32/57/150 | 0.1684 | 0.16874 | 0.15386 |
| latest pregame | 13218 | - | 0/57/3302 | 0.1671 | 0.16741 | 0.15248 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 128 | 128 | 128 | 0.1450 | 0.14500 | 0.14060 | -0.00522 |
| GAME_WINNER | 64 | 64 | 64 | 0.2194 | 0.21936 | 0.22303 | -0.00016 |
| PLAYER_STAT | 10727 | 10529 | 10529 | 0.1653 | 0.16564 | 0.14733 | 0.00096 |
| SPREAD | 819 | 819 | 819 | 0.2048 | 0.20479 | 0.20356 | 0.00039 |
| TEAM_TOTAL | 872 | 872 | 872 | 0.1502 | 0.15018 | 0.15007 | 0.00127 |
| TOTAL | 608 | 608 | 608 | 0.1718 | 0.17178 | 0.17141 | 0.00048 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 64 | 64 | 64 | 0.2194 | 0.21936 | 0.22303 | -0.00016 |
| attempts | 456 | 445 | 445 | 0.2287 | 0.22605 | 0.21485 | 0.00326 |
| carries | 632 | 632 | 632 | 0.2737 | 0.27556 | 0.21735 | 0.00794 |
| completions | 456 | 445 | 445 | 0.1925 | 0.19158 | 0.19485 | 0.00677 |
| interceptions | 192 | 189 | 189 | 0.1230 | 0.12259 | 0.12478 | 0.00730 |
| margin | 819 | 819 | 819 | 0.2048 | 0.20479 | 0.20356 | 0.00039 |
| min_team_points | 128 | 128 | 128 | 0.1450 | 0.14500 | 0.14060 | -0.00522 |
| passing_tds | 266 | 263 | 263 | 0.1529 | 0.15346 | 0.15121 | -0.00015 |
| passing_yards | 562 | 555 | 555 | 0.1712 | 0.17019 | 0.17271 | 0.00035 |
| receiving_yards | 2811 | 2756 | 2756 | 0.1677 | 0.16826 | 0.15110 | 0.00069 |
| receptions | 2425 | 2403 | 2403 | 0.1640 | 0.16478 | 0.13490 | -0.00025 |
| rushing_yards | 1566 | 1546 | 1546 | 0.1631 | 0.16397 | 0.14475 | -0.00141 |
| team_points | 872 | 872 | 872 | 0.1502 | 0.15018 | 0.15007 | 0.00127 |
| total_points | 608 | 608 | 608 | 0.1718 | 0.17178 | 0.17141 | 0.00048 |
| touchdowns | 1361 | 1295 | 1295 | 0.0870 | 0.08709 | 0.08341 | 0.00034 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 4480 | 4327 | 4327 | 0.0725 | 0.07256 | 0.06786 | 0.00040 |
| 0.10-0.20 | 2316 | 2301 | 2301 | 0.1816 | 0.18175 | 0.15976 | 0.00106 |
| 0.20-0.30 | 1559 | 1548 | 1548 | 0.2321 | 0.23281 | 0.20615 | 0.00124 |
| 0.30-0.40 | 1202 | 1197 | 1197 | 0.2465 | 0.24719 | 0.21591 | 0.00122 |
| 0.40-0.50 | 1036 | 1029 | 1029 | 0.2537 | 0.25440 | 0.22982 | 0.00165 |
| 0.50-0.60 | 869 | 864 | 864 | 0.2437 | 0.24426 | 0.22693 | 0.00030 |
| 0.60-0.70 | 688 | 686 | 686 | 0.2190 | 0.21986 | 0.21010 | 0.00148 |
| 0.70-0.80 | 499 | 499 | 499 | 0.1978 | 0.19764 | 0.19873 | 0.00215 |
| 0.80-0.90 | 313 | 313 | 313 | 0.1507 | 0.15045 | 0.15584 | -0.00078 |
| 0.90-1.00 | 256 | 256 | 256 | 0.0856 | 0.08544 | 0.08562 | -0.00044 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 4350 | 4267 | 4267 | 0.0723 | 0.07232 | 0.06754 | 0.00074 |
| 0.10-0.20 | 2324 | 2294 | 2294 | 0.1778 | 0.17799 | 0.15768 | 0.00083 |
| 0.20-0.30 | 1562 | 1539 | 1539 | 0.2299 | 0.23053 | 0.20377 | 0.00113 |
| 0.30-0.40 | 1226 | 1208 | 1208 | 0.2480 | 0.24882 | 0.21803 | 0.00093 |
| 0.40-0.50 | 1036 | 1021 | 1021 | 0.2538 | 0.25439 | 0.22758 | 0.00139 |
| 0.50-0.60 | 885 | 873 | 873 | 0.2447 | 0.24541 | 0.22745 | 0.00030 |
| 0.60-0.70 | 699 | 685 | 685 | 0.2211 | 0.22194 | 0.20890 | 0.00082 |
| 0.70-0.80 | 509 | 507 | 507 | 0.1960 | 0.19623 | 0.19829 | 0.00248 |
| 0.80-0.90 | 356 | 355 | 355 | 0.1651 | 0.16431 | 0.16958 | -0.00055 |
| 0.90-1.00 | 271 | 271 | 271 | 0.0874 | 0.08715 | 0.08754 | -0.00002 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 2139 | 2106 | 2106 | 0.2114 | 0.21221 | 0.19216 | -0.00010 |
| 20%+ | 1766 | 1710 | 1710 | 0.2928 | 0.29484 | 0.21653 | 0.00515 |
| 3-5% | 1609 | 1584 | 1584 | 0.1297 | 0.12946 | 0.12713 | 0.00003 |
| 5-10% | 2162 | 2122 | 2122 | 0.1645 | 0.16439 | 0.15858 | 0.00078 |
| <3% | 5542 | 5498 | 5498 | 0.1228 | 0.12272 | 0.12232 | 0.00017 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 8656 | 8504 | 8504 | 0.1754 | 0.17628 | 0.15422 | 0.00125 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 4561 | 4515 | 4515 | 0.1515 | 0.15074 | 0.14925 | 0.00013 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 7729 | 7674 | 7674 | 0.1675 | 0.16775 | 0.15388 | 0.00102 |
| 6-24h | 57 | 18 | 18 | 0.0681 | 0.06749 | 0.05636 | 0.01958 |
| 90m-6h | 4091 | 4060 | 4060 | 0.1692 | 0.16978 | 0.15063 | -0.00000 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 69 | 1 | 1 | 0.0653 | 0.06229 | 0.00810 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 13218 | 13020 | 13020 | 0.1671 | 0.16741 | 0.15248 | 0.00086 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |
| 2 | 6132 | 6063 | 6063 | 0.1586 | 0.15895 | 0.14573 | 0.00045 |

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

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 3936 | 3897 | 3897 | 0.1463 | 0.14671 | 0.12845 | 0.00075 |
| 6-10c | 766 | 730 | 730 | 0.1729 | 0.17343 | 0.15401 | 0.00101 |
| <=2c | 7784 | 7720 | 7720 | 0.1740 | 0.17420 | 0.16168 | 0.00030 |
| >10c | 732 | 673 | 673 | 0.2022 | 0.20287 | 0.18453 | 0.00852 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 13218 | 13020 | 13020 | 0.1671 | 0.16741 | 0.15248 | 0.00086 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| DOUBTFUL | 16 | 0 | 0 | - | - | - | - |
| EXPECTED_ACTIVE | 10558 | 10516 | 10516 | 0.1653 | 0.16561 | 0.14743 | 0.00110 |
| EXPECTED_OUT | 9 | 0 | 0 | - | - | - | -0.16500 |
| None | 2491 | 2491 | 2491 | 0.1749 | 0.17492 | 0.17425 | 0.00044 |
| OUT | 98 | 0 | 0 | - | - | - | -0.00118 |
| QUESTIONABLE | 43 | 13 | 13 | 0.1659 | 0.18762 | 0.06960 | 0.00385 |
| UNKNOWN | 3 | 0 | 0 | - | - | - | - |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
