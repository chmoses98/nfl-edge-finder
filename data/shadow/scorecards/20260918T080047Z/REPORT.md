# Shadow evaluation scorecard (20260918T080047Z)

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 174324 | 7086 | 16 |
| **latest pregame per contract (primary)** | 7086 | 7086 | 16 |

The raw view holds 174324 snapshots of 7086 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 4780 |
| SETTLED | 169544 |

| close status | n |
|---|---|
| OK | 169025 |
| OK_STALE | 5299 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 6957 contracts whose payout is a 0/1 realisation (129 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 6957 | 0.1745 | 0.5257 | 0.2924 | 0.3500 | -0.0577 |
| market mid (only where value == event probability) | 1210 | 0.1781 | 0.5330 | 0.4125 | 0.4579 | -0.0453 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 2091 | 0.0428 | 0.0870 |
| 0.10-0.20 | 1198 | 0.1467 | 0.2337 |
| 0.20-0.30 | 841 | 0.2459 | 0.3520 |
| 0.30-0.40 | 697 | 0.3481 | 0.4304 |
| 0.40-0.50 | 592 | 0.4480 | 0.4882 |
| 0.50-0.60 | 513 | 0.5472 | 0.5984 |
| 0.60-0.70 | 401 | 0.6512 | 0.6858 |
| 0.70-0.80 | 303 | 0.7484 | 0.7294 |
| 0.80-0.90 | 183 | 0.8422 | 0.8470 |
| 0.90-1.00 | 138 | 0.9509 | 0.9420 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 6957 contracts whose payout is exactly known (0 settled without an exact payout, 129 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 6957 | 0.17479 | 0.31777 | -0.06194 | 0.2881 | 0.3500 |
| market mid at the same snapshot | 6957 | 0.15837 | 0.30959 | -0.02376 | 0.3262 | 0.3500 |

On the 6844 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 6844 | 0.17458 | 0.31772 | -0.06194 | 0.2880 | 0.3499 |
| market mid at snapshot | 6844 | 0.15814 | 0.30971 | -0.02266 | 0.3273 | 0.3499 |
| market mid at close | 6844 | 0.15889 | 0.31059 | -0.02421 | 0.3257 | 0.3499 |

Lower is better: **the closing market** is ahead by 0.01569 in squared payout error on this set.

## 3. Closing-line value and market movement

On 6908 contracts with a legitimate close (178 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00122**
* mean signed CLV (executable, crossing the spread): **0.00412**
* share with positive midpoint CLV: 0.2668
* movement: {'away': 1586, 'toward': 1824, 'unchanged': 3498}
* toward-share of directional moves: 0.5349 on 3410 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 178 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00031
* toward-share of directional moves: 0.9000 on 10 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 999 | 6087 | 1446/1455/1543 | 0.1735 | 0.17278 | 0.16129 |
| T-6h | 678 | 6408 | 363/457/477 | 0.1414 | 0.14148 | 0.12237 |
| T-90m | 2561 | 4525 | 96/109/207 | 0.1755 | 0.17582 | 0.15909 |
| T-30m | 5935 | 1151 | 32/44/150 | 0.1789 | 0.17928 | 0.16144 |
| latest pregame | 7086 | - | 0/44/2751 | 0.1745 | 0.17479 | 0.15837 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 64 | 64 | 64 | 0.1624 | 0.16240 | 0.15850 | -0.01008 |
| GAME_WINNER | 32 | 32 | 32 | 0.2107 | 0.21074 | 0.21194 | -0.00063 |
| PLAYER_STAT | 5844 | 5715 | 5715 | 0.1733 | 0.17370 | 0.15390 | 0.00147 |
| SPREAD | 404 | 404 | 404 | 0.2168 | 0.21678 | 0.21458 | 0.00042 |
| TEAM_TOTAL | 438 | 438 | 438 | 0.1485 | 0.14854 | 0.14909 | 0.00128 |
| TOTAL | 304 | 304 | 304 | 0.1761 | 0.17612 | 0.17536 | -0.00005 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 32 | 32 | 32 | 0.2107 | 0.21074 | 0.21194 | -0.00063 |
| attempts | 363 | 352 | 352 | 0.2348 | 0.23213 | 0.21863 | 0.00356 |
| carries | 465 | 465 | 465 | 0.2856 | 0.28765 | 0.22769 | 0.01033 |
| completions | 363 | 352 | 352 | 0.1931 | 0.19218 | 0.19552 | 0.00881 |
| interceptions | 99 | 96 | 96 | 0.1277 | 0.12767 | 0.13109 | 0.01208 |
| margin | 404 | 404 | 404 | 0.2168 | 0.21678 | 0.21458 | 0.00042 |
| min_team_points | 64 | 64 | 64 | 0.1624 | 0.16240 | 0.15850 | -0.01008 |
| passing_tds | 132 | 129 | 129 | 0.1462 | 0.14704 | 0.14597 | 0.00008 |
| passing_yards | 287 | 280 | 280 | 0.1776 | 0.17629 | 0.17265 | 0.00070 |
| receiving_yards | 1407 | 1385 | 1385 | 0.1675 | 0.16798 | 0.15083 | 0.00027 |
| receptions | 1241 | 1224 | 1224 | 0.1550 | 0.15568 | 0.13019 | 0.00008 |
| rushing_yards | 801 | 781 | 781 | 0.1768 | 0.17797 | 0.14947 | -0.00284 |
| team_points | 438 | 438 | 438 | 0.1485 | 0.14854 | 0.14909 | 0.00128 |
| total_points | 304 | 304 | 304 | 0.1761 | 0.17612 | 0.17536 | -0.00005 |
| touchdowns | 686 | 651 | 651 | 0.1023 | 0.10257 | 0.09700 | 0.00035 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 2212 | 2127 | 2127 | 0.0794 | 0.07942 | 0.07469 | 0.00038 |
| 0.10-0.20 | 1217 | 1203 | 1203 | 0.1902 | 0.19038 | 0.16593 | 0.00130 |
| 0.20-0.30 | 858 | 847 | 847 | 0.2406 | 0.24127 | 0.20857 | 0.00186 |
| 0.30-0.40 | 696 | 691 | 691 | 0.2469 | 0.24758 | 0.21458 | 0.00202 |
| 0.40-0.50 | 603 | 596 | 596 | 0.2522 | 0.25257 | 0.22733 | 0.00276 |
| 0.50-0.60 | 506 | 500 | 500 | 0.2415 | 0.24201 | 0.22084 | 0.00025 |
| 0.60-0.70 | 410 | 409 | 409 | 0.2179 | 0.21859 | 0.21414 | 0.00231 |
| 0.70-0.80 | 298 | 298 | 298 | 0.1897 | 0.18960 | 0.19552 | 0.00241 |
| 0.80-0.90 | 155 | 155 | 155 | 0.1194 | 0.11977 | 0.12849 | -0.00150 |
| 0.90-1.00 | 131 | 131 | 131 | 0.0503 | 0.05038 | 0.05097 | -0.00012 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 2139 | 2091 | 2091 | 0.0798 | 0.07985 | 0.07501 | 0.00109 |
| 0.10-0.20 | 1217 | 1198 | 1198 | 0.1852 | 0.18543 | 0.16296 | 0.00089 |
| 0.20-0.30 | 858 | 841 | 841 | 0.2374 | 0.23797 | 0.20625 | 0.00149 |
| 0.30-0.40 | 710 | 697 | 697 | 0.2501 | 0.25079 | 0.21660 | 0.00160 |
| 0.40-0.50 | 602 | 592 | 592 | 0.2508 | 0.25107 | 0.22228 | 0.00224 |
| 0.50-0.60 | 523 | 513 | 513 | 0.2429 | 0.24346 | 0.22382 | 0.00043 |
| 0.60-0.70 | 411 | 401 | 401 | 0.2174 | 0.21838 | 0.21034 | 0.00122 |
| 0.70-0.80 | 305 | 303 | 303 | 0.1966 | 0.19635 | 0.20311 | 0.00274 |
| 0.80-0.90 | 183 | 183 | 183 | 0.1304 | 0.13057 | 0.13875 | -0.00084 |
| 0.90-1.00 | 138 | 138 | 138 | 0.0540 | 0.05400 | 0.05481 | 0.00052 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 1170 | 1149 | 1149 | 0.2194 | 0.21996 | 0.19604 | -0.00081 |
| 20%+ | 913 | 872 | 872 | 0.2985 | 0.30031 | 0.21259 | 0.00976 |
| 3-5% | 845 | 831 | 831 | 0.1432 | 0.14311 | 0.14028 | -0.00034 |
| 5-10% | 1188 | 1165 | 1165 | 0.1696 | 0.16967 | 0.16440 | 0.00085 |
| <3% | 2970 | 2940 | 2940 | 0.1309 | 0.13088 | 0.13029 | 0.00007 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 4421 | 4336 | 4336 | 0.1859 | 0.18684 | 0.16115 | 0.00202 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 2664 | 2620 | 2620 | 0.1556 | 0.15491 | 0.15382 | -0.00010 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 3817 | 3791 | 3791 | 0.1790 | 0.17941 | 0.16064 | 0.00171 |
| 6-24h | 48 | 12 | 12 | 0.1013 | 0.10043 | 0.08397 | 0.00857 |
| 90m-6h | 1911 | 1886 | 1886 | 0.1761 | 0.17647 | 0.15900 | -0.00070 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 38 | 1 | 1 | 0.0653 | 0.06229 | 0.00810 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |

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

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 2294 | 2267 | 2267 | 0.1614 | 0.16174 | 0.14137 | 0.00089 |
| 6-10c | 654 | 632 | 632 | 0.1772 | 0.17780 | 0.15598 | 0.00105 |
| <=2c | 3482 | 3445 | 3445 | 0.1767 | 0.17681 | 0.16369 | 0.00018 |
| >10c | 656 | 613 | 613 | 0.2078 | 0.20853 | 0.19378 | 0.00925 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| EXPECTED_ACTIVE | 5750 | 5715 | 5715 | 0.1733 | 0.17370 | 0.15390 | 0.00175 |
| EXPECTED_OUT | 9 | 0 | 0 | - | - | - | -0.16500 |
| None | 1242 | 1242 | 1242 | 0.1798 | 0.17981 | 0.17893 | 0.00006 |
| OUT | 51 | 0 | 0 | - | - | - | -0.00100 |
| QUESTIONABLE | 33 | 0 | 0 | - | - | - | - |
| UNKNOWN | 1 | 0 | 0 | - | - | - | - |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
