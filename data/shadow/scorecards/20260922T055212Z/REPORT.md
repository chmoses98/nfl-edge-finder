# Shadow evaluation scorecard (20260922T055212Z)

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 307288 | 12795 | 31 |
| **latest pregame per contract (primary)** | 12795 | 12795 | 31 |

The raw view holds 307288 snapshots of 12795 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 7762 |
| SETTLED | 299526 |

| close status | n |
|---|---|
| OK | 298461 |
| OK_STALE | 8827 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 12618 contracts whose payout is a 0/1 realisation (177 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 12618 | 0.1676 | 0.5089 | 0.2793 | 0.3283 | -0.0490 |
| market mid (only where value == event probability) | 2351 | 0.1730 | 0.5181 | 0.4110 | 0.4147 | -0.0037 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 4130 | 0.0421 | 0.0794 |
| 0.10-0.20 | 2218 | 0.1467 | 0.2254 |
| 0.20-0.30 | 1492 | 0.2462 | 0.3365 |
| 0.30-0.40 | 1172 | 0.3479 | 0.4198 |
| 0.40-0.50 | 992 | 0.4485 | 0.4990 |
| 0.50-0.60 | 848 | 0.5469 | 0.5908 |
| 0.60-0.70 | 669 | 0.6498 | 0.6726 |
| 0.70-0.80 | 492 | 0.7476 | 0.7378 |
| 0.80-0.90 | 344 | 0.8440 | 0.7994 |
| 0.90-1.00 | 261 | 0.9515 | 0.9042 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 12618 contracts whose payout is exactly known (0 settled without an exact payout, 177 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 12618 | 0.16791 | 0.30510 | -0.05280 | 0.2755 | 0.3283 |
| market mid at the same snapshot | 12618 | 0.15295 | 0.30099 | -0.00454 | 0.3237 | 0.3283 |

On the 12457 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 12457 | 0.16806 | 0.30548 | -0.05264 | 0.2754 | 0.3280 |
| market mid at snapshot | 12457 | 0.15319 | 0.30164 | -0.00376 | 0.3243 | 0.3280 |
| market mid at close | 12457 | 0.15360 | 0.30214 | -0.00471 | 0.3233 | 0.3280 |

Lower is better: **the closing market** is ahead by 0.01447 in squared payout error on this set.

## 3. Closing-line value and market movement

On 12523 contracts with a legitimate close (272 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00091**
* mean signed CLV (executable, crossing the spread): **0.00291**
* share with positive midpoint CLV: 0.2551
* movement: {'away': 2756, 'toward': 3163, 'unchanged': 6604}
* toward-share of directional moves: 0.5344 on 5919 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 272 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00022
* toward-share of directional moves: 0.9091 on 11 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 4564 | 8231 | 1443/1521/1559 | 0.1720 | 0.17239 | 0.15768 |
| T-6h | 1564 | 11231 | 361/391/477 | 0.1503 | 0.15092 | 0.13155 |
| T-90m | 4706 | 8089 | 96/117/207 | 0.1702 | 0.17073 | 0.15223 |
| T-30m | 10987 | 1808 | 32/57/150 | 0.1690 | 0.16933 | 0.15442 |
| latest pregame | 12795 | - | 0/57/3302 | 0.1676 | 0.16791 | 0.15295 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 124 | 124 | 124 | 0.1444 | 0.14439 | 0.13930 | -0.00545 |
| GAME_WINNER | 62 | 62 | 62 | 0.2241 | 0.22409 | 0.22760 | -0.00016 |
| PLAYER_STAT | 10382 | 10205 | 10205 | 0.1658 | 0.16620 | 0.14787 | 0.00102 |
| SPREAD | 792 | 792 | 792 | 0.2054 | 0.20545 | 0.20388 | 0.00038 |
| TEAM_TOTAL | 846 | 846 | 846 | 0.1503 | 0.15030 | 0.15038 | 0.00120 |
| TOTAL | 589 | 589 | 589 | 0.1714 | 0.17135 | 0.17113 | 0.00051 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 62 | 62 | 62 | 0.2241 | 0.22409 | 0.22760 | -0.00016 |
| attempts | 450 | 439 | 439 | 0.2286 | 0.22600 | 0.21551 | 0.00328 |
| carries | 620 | 620 | 620 | 0.2757 | 0.27758 | 0.21778 | 0.00807 |
| completions | 450 | 439 | 439 | 0.1923 | 0.19145 | 0.19447 | 0.00688 |
| interceptions | 186 | 183 | 183 | 0.1237 | 0.12333 | 0.12566 | 0.00754 |
| margin | 792 | 792 | 792 | 0.2054 | 0.20545 | 0.20388 | 0.00038 |
| min_team_points | 124 | 124 | 124 | 0.1444 | 0.14439 | 0.13930 | -0.00545 |
| passing_tds | 257 | 254 | 254 | 0.1503 | 0.15085 | 0.14832 | -0.00014 |
| passing_yards | 544 | 537 | 537 | 0.1704 | 0.16942 | 0.17037 | 0.00037 |
| receiving_yards | 2708 | 2667 | 2667 | 0.1685 | 0.16904 | 0.15195 | 0.00078 |
| receptions | 2347 | 2325 | 2325 | 0.1638 | 0.16462 | 0.13515 | -0.00027 |
| rushing_yards | 1514 | 1494 | 1494 | 0.1635 | 0.16435 | 0.14513 | -0.00136 |
| team_points | 846 | 846 | 846 | 0.1503 | 0.15030 | 0.15038 | 0.00120 |
| total_points | 589 | 589 | 589 | 0.1714 | 0.17135 | 0.17113 | 0.00051 |
| touchdowns | 1306 | 1247 | 1247 | 0.0879 | 0.08799 | 0.08463 | 0.00040 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 4328 | 4189 | 4189 | 0.0734 | 0.07338 | 0.06861 | 0.00045 |
| 0.10-0.20 | 2238 | 2225 | 2225 | 0.1834 | 0.18362 | 0.16130 | 0.00111 |
| 0.20-0.30 | 1508 | 1499 | 1499 | 0.2323 | 0.23300 | 0.20647 | 0.00132 |
| 0.30-0.40 | 1166 | 1162 | 1162 | 0.2463 | 0.24699 | 0.21622 | 0.00125 |
| 0.40-0.50 | 1007 | 1001 | 1001 | 0.2539 | 0.25462 | 0.23005 | 0.00169 |
| 0.50-0.60 | 842 | 838 | 838 | 0.2436 | 0.24417 | 0.22682 | 0.00044 |
| 0.60-0.70 | 672 | 670 | 670 | 0.2174 | 0.21839 | 0.20873 | 0.00159 |
| 0.70-0.80 | 484 | 484 | 484 | 0.1945 | 0.19450 | 0.19525 | 0.00210 |
| 0.80-0.90 | 303 | 303 | 303 | 0.1506 | 0.15021 | 0.15555 | -0.00097 |
| 0.90-1.00 | 247 | 247 | 247 | 0.0853 | 0.08514 | 0.08512 | -0.00060 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 4203 | 4130 | 4130 | 0.0731 | 0.07312 | 0.06827 | 0.00080 |
| 0.10-0.20 | 2245 | 2218 | 2218 | 0.1796 | 0.17974 | 0.15917 | 0.00088 |
| 0.20-0.30 | 1513 | 1492 | 1492 | 0.2303 | 0.23103 | 0.20446 | 0.00118 |
| 0.30-0.40 | 1189 | 1172 | 1172 | 0.2476 | 0.24840 | 0.21781 | 0.00097 |
| 0.40-0.50 | 1004 | 992 | 992 | 0.2540 | 0.25459 | 0.22791 | 0.00141 |
| 0.50-0.60 | 859 | 848 | 848 | 0.2444 | 0.24516 | 0.22764 | 0.00044 |
| 0.60-0.70 | 682 | 669 | 669 | 0.2206 | 0.22148 | 0.20808 | 0.00094 |
| 0.70-0.80 | 494 | 492 | 492 | 0.1933 | 0.19368 | 0.19558 | 0.00244 |
| 0.80-0.90 | 345 | 344 | 344 | 0.1621 | 0.16138 | 0.16632 | -0.00071 |
| 0.90-1.00 | 261 | 261 | 261 | 0.0875 | 0.08721 | 0.08734 | -0.00023 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 2055 | 2025 | 2025 | 0.2114 | 0.21220 | 0.19191 | -0.00005 |
| 20%+ | 1710 | 1656 | 1656 | 0.2932 | 0.29532 | 0.21697 | 0.00536 |
| 3-5% | 1552 | 1531 | 1531 | 0.1292 | 0.12906 | 0.12653 | -0.00004 |
| 5-10% | 2095 | 2061 | 2061 | 0.1657 | 0.16567 | 0.15994 | 0.00083 |
| <3% | 5383 | 5345 | 5345 | 0.1238 | 0.12364 | 0.12322 | 0.00019 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 8384 | 8252 | 8252 | 0.1756 | 0.17650 | 0.15427 | 0.00132 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 4410 | 4365 | 4365 | 0.1524 | 0.15169 | 0.15048 | 0.00013 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 7318 | 7279 | 7279 | 0.1682 | 0.16848 | 0.15463 | 0.00110 |
| 6-24h | 56 | 18 | 18 | 0.0681 | 0.06749 | 0.05636 | 0.01958 |
| 90m-6h | 4080 | 4053 | 4053 | 0.1695 | 0.17006 | 0.15086 | -0.00001 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 69 | 1 | 1 | 0.0653 | 0.06229 | 0.00810 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 12795 | 12618 | 12618 | 0.1676 | 0.16791 | 0.15295 | 0.00091 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |
| 2 | 5709 | 5661 | 5661 | 0.1591 | 0.15945 | 0.14629 | 0.00052 |

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
| 2026_02_PHI_TEN | 359 | 359 | 359 | 0.1465 | 0.14646 | 0.15004 | 0.00045 |
| 2026_02_PIT_NE | 396 | 394 | 394 | 0.1303 | 0.13053 | 0.12885 | -0.00057 |
| 2026_02_SEA_ARI | 370 | 370 | 370 | 0.1494 | 0.14896 | 0.14032 | 0.00045 |
| 2026_02_WAS_DAL | 401 | 398 | 398 | 0.1712 | 0.17148 | 0.15033 | 0.00094 |

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 3873 | 3842 | 3842 | 0.1467 | 0.14713 | 0.12874 | 0.00076 |
| 6-10c | 756 | 725 | 725 | 0.1737 | 0.17425 | 0.15442 | 0.00090 |
| <=2c | 7437 | 7379 | 7379 | 0.1747 | 0.17490 | 0.16251 | 0.00035 |
| >10c | 729 | 672 | 672 | 0.2024 | 0.20305 | 0.18478 | 0.00856 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 12795 | 12618 | 12618 | 0.1676 | 0.16791 | 0.15295 | 0.00091 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| DOUBTFUL | 16 | 0 | 0 | - | - | - | - |
| EXPECTED_ACTIVE | 10234 | 10192 | 10192 | 0.1658 | 0.16617 | 0.14797 | 0.00117 |
| EXPECTED_OUT | 9 | 0 | 0 | - | - | - | -0.16500 |
| None | 2413 | 2413 | 2413 | 0.1751 | 0.17513 | 0.17442 | 0.00041 |
| OUT | 90 | 0 | 0 | - | - | - | -0.00118 |
| QUESTIONABLE | 32 | 13 | 13 | 0.1659 | 0.18762 | 0.06960 | 0.00385 |
| UNKNOWN | 1 | 0 | 0 | - | - | - | - |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
