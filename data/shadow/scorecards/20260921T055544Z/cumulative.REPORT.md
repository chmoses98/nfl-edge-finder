# Shadow evaluation scorecard - cumulative

## Sample units

| unit | observations | contracts | games |
|---|---|---|---|
| raw snapshots (correlated) | 183358 | 7499 | 17 |
| **latest pregame per contract (primary)** | 7499 | 7499 | 17 |

The raw view holds 183358 snapshots of 7499 contracts: they are repeated observations of the same markets and are reported as diagnostics, never as an independent sample size. No effective N is computed.

## What is in the corpus

| settlement status | n |
|---|---|
| REFUSED_PARTICIPATION_UNPROVEN | 6044 |
| SETTLED | 177314 |

| close status | n |
|---|---|
| OK | 176999 |
| OK_STALE | 6359 |

## 1. Event-probability calibration (the football model)

`model_event_probability` against the realised football event, on the 7370 contracts whose payout is a 0/1 realisation (129 excluded: no valid binary realisation).

| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |
|---|---|---|---|---|---|---|
| model event probability | 7370 | 0.1749 | 0.5266 | 0.2909 | 0.3547 | -0.0638 |
| market mid (only where value == event probability) | 1285 | 0.1757 | 0.5265 | 0.4167 | 0.4708 | -0.0541 |

| event probability band | n | mean predicted | actual event rate |
|---|---|---|---|
| 0.00-0.10 | 2238 | 0.0426 | 0.0885 |
| 0.10-0.20 | 1276 | 0.1466 | 0.2398 |
| 0.20-0.30 | 889 | 0.2458 | 0.3588 |
| 0.30-0.40 | 724 | 0.3479 | 0.4351 |
| 0.40-0.50 | 622 | 0.4478 | 0.5032 |
| 0.50-0.60 | 539 | 0.5472 | 0.6048 |
| 0.60-0.70 | 423 | 0.6510 | 0.6998 |
| 0.70-0.80 | 314 | 0.7487 | 0.7389 |
| 0.80-0.90 | 195 | 0.8424 | 0.8564 |
| 0.90-1.00 | 150 | 0.9521 | 0.9467 |

## 2. Contract-payout quality (the model against the market)

`model_contract_value` and the market against the ACTUAL payout, on the 7370 contracts whose payout is exactly known (0 settled without an exact payout, 129 not settled). Squared error, not log loss: a scalar payout is not a Bernoulli outcome.

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 7370 | 0.17527 | 0.31735 | -0.06804 | 0.2866 | 0.3547 |
| market mid at the same snapshot | 7370 | 0.15848 | 0.30932 | -0.02763 | 0.3271 | 0.3547 |

On the 7255 of those with a legitimate pregame close, including the market's last word:

| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |
|---|---|---|---|---|---|---|
| model contract value | 7255 | 0.17513 | 0.31738 | -0.06816 | 0.2866 | 0.3548 |
| market mid at snapshot | 7255 | 0.15832 | 0.30949 | -0.02667 | 0.3281 | 0.3548 |
| market mid at close | 7255 | 0.15904 | 0.31033 | -0.02815 | 0.3266 | 0.3548 |

Lower is better: **the closing market** is ahead by 0.01609 in squared payout error on this set.

## 3. Closing-line value and market movement

On 7319 contracts with a legitimate close (180 excluded for a missing or stale close):

* mean signed CLV (midpoint): **0.00114**
* mean signed CLV (executable, crossing the spread): **0.00388**
* share with positive midpoint CLV: 0.2663
* movement: {'away': 1691, 'toward': 1929, 'unchanged': 3699}
* toward-share of directional moves: 0.5329 on 3620 directional moves

`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.

Separately, on the 180 contracts whose last pregame quote breached the staleness budget (reported, not mixed into the numbers above):

* mean signed CLV (midpoint): 0.00031
* toward-share of directional moves: 0.9000 on 10 moves

## 4. Canonical horizons

One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within 120 minutes of it; otherwise the contract is unavailable at that horizon. The actual distance to kickoff is reported, so no label has to be trusted on its own.

| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |
|---|---|---|---|---|---|---|
| T-24h | 1018 | 6481 | 1443/1455/1554 | 0.1722 | 0.17149 | 0.16023 |
| T-6h | 1088 | 6411 | 363/391/477 | 0.1573 | 0.15782 | 0.13713 |
| T-90m | 2961 | 4538 | 96/122/207 | 0.1771 | 0.17762 | 0.15992 |
| T-30m | 5935 | 1564 | 32/44/150 | 0.1789 | 0.17928 | 0.16144 |
| latest pregame | 7499 | - | 0/44/2751 | 0.1749 | 0.17527 | 0.15848 |

## 5. Segmentation (contract view)

### by family

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 68 | 68 | 68 | 0.1642 | 0.16425 | 0.15907 | -0.00977 |
| GAME_WINNER | 34 | 34 | 34 | 0.2039 | 0.20393 | 0.20494 | -0.00059 |
| PLAYER_STAT | 6180 | 6051 | 6051 | 0.1744 | 0.17483 | 0.15456 | 0.00135 |
| SPREAD | 429 | 429 | 429 | 0.2100 | 0.21004 | 0.20822 | 0.00044 |
| TEAM_TOTAL | 465 | 465 | 465 | 0.1464 | 0.14644 | 0.14719 | 0.00149 |
| TOTAL | 323 | 323 | 323 | 0.1781 | 0.17814 | 0.17712 | 0.00002 |

### by player statistic

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| None | 34 | 34 | 34 | 0.2039 | 0.20393 | 0.20494 | -0.00059 |
| attempts | 369 | 358 | 358 | 0.2335 | 0.23092 | 0.21712 | 0.00352 |
| carries | 474 | 474 | 474 | 0.2877 | 0.28970 | 0.22790 | 0.01000 |
| completions | 369 | 358 | 358 | 0.1922 | 0.19133 | 0.19409 | 0.00829 |
| interceptions | 105 | 102 | 102 | 0.1253 | 0.12506 | 0.12762 | 0.01181 |
| margin | 429 | 429 | 429 | 0.2100 | 0.21004 | 0.20822 | 0.00044 |
| min_team_points | 68 | 68 | 68 | 0.1642 | 0.16425 | 0.15907 | -0.00977 |
| passing_tds | 142 | 139 | 139 | 0.1536 | 0.15475 | 0.15255 | 0.00011 |
| passing_yards | 305 | 298 | 298 | 0.1759 | 0.17478 | 0.17092 | 0.00059 |
| receiving_yards | 1509 | 1487 | 1487 | 0.1710 | 0.17157 | 0.15427 | 0.00028 |
| receptions | 1327 | 1310 | 1310 | 0.1572 | 0.15799 | 0.13150 | -0.00006 |
| rushing_yards | 849 | 829 | 829 | 0.1772 | 0.17850 | 0.15036 | -0.00264 |
| team_points | 465 | 465 | 465 | 0.1464 | 0.14644 | 0.14719 | 0.00149 |
| total_points | 323 | 323 | 323 | 0.1781 | 0.17814 | 0.17712 | 0.00002 |
| touchdowns | 731 | 696 | 696 | 0.1046 | 0.10490 | 0.09850 | 0.00032 |

### by contract value band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 2367 | 2276 | 2276 | 0.0809 | 0.08090 | 0.07533 | 0.00032 |
| 0.10-0.20 | 1295 | 1282 | 1282 | 0.1943 | 0.19459 | 0.16985 | 0.00124 |
| 0.20-0.30 | 903 | 894 | 894 | 0.2434 | 0.24406 | 0.21143 | 0.00175 |
| 0.30-0.40 | 722 | 718 | 718 | 0.2487 | 0.24944 | 0.21722 | 0.00180 |
| 0.40-0.50 | 631 | 625 | 625 | 0.2536 | 0.25419 | 0.22579 | 0.00261 |
| 0.50-0.60 | 533 | 529 | 529 | 0.2408 | 0.24135 | 0.22258 | 0.00019 |
| 0.60-0.70 | 429 | 427 | 427 | 0.2137 | 0.21453 | 0.20936 | 0.00218 |
| 0.70-0.80 | 311 | 311 | 311 | 0.1841 | 0.18428 | 0.18884 | 0.00248 |
| 0.80-0.90 | 165 | 165 | 165 | 0.1135 | 0.11394 | 0.12210 | -0.00147 |
| 0.90-1.00 | 143 | 143 | 143 | 0.0462 | 0.04632 | 0.04696 | 0.00047 |

### by event probability band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 0.00-0.10 | 2286 | 2238 | 2238 | 0.0810 | 0.08104 | 0.07535 | 0.00098 |
| 0.10-0.20 | 1295 | 1276 | 1276 | 0.1895 | 0.18971 | 0.16709 | 0.00084 |
| 0.20-0.30 | 906 | 889 | 889 | 0.2408 | 0.24151 | 0.20927 | 0.00142 |
| 0.30-0.40 | 737 | 724 | 724 | 0.2515 | 0.25230 | 0.21919 | 0.00147 |
| 0.40-0.50 | 632 | 622 | 622 | 0.2527 | 0.25315 | 0.22158 | 0.00203 |
| 0.50-0.60 | 549 | 539 | 539 | 0.2425 | 0.24300 | 0.22599 | 0.00044 |
| 0.60-0.70 | 433 | 423 | 423 | 0.2131 | 0.21420 | 0.20472 | 0.00103 |
| 0.70-0.80 | 316 | 314 | 314 | 0.1917 | 0.19175 | 0.19723 | 0.00274 |
| 0.80-0.90 | 195 | 195 | 195 | 0.1239 | 0.12422 | 0.13179 | -0.00071 |
| 0.90-1.00 | 150 | 150 | 150 | 0.0498 | 0.04985 | 0.05068 | 0.00103 |

### by disagreement band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 10-20% | 1240 | 1218 | 1218 | 0.2208 | 0.22151 | 0.19653 | -0.00094 |
| 20%+ | 980 | 936 | 936 | 0.3018 | 0.30369 | 0.21583 | 0.00907 |
| 3-5% | 895 | 882 | 882 | 0.1416 | 0.14146 | 0.13850 | -0.00032 |
| 5-10% | 1264 | 1241 | 1241 | 0.1704 | 0.17051 | 0.16505 | 0.00083 |
| <3% | 3120 | 3093 | 3093 | 0.1298 | 0.12975 | 0.12921 | 0.00011 |

### by model direction

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| no | 4721 | 4634 | 4634 | 0.1868 | 0.18771 | 0.16137 | 0.00189 |
| none | 1 | 1 | 1 | 0.0182 | 0.01823 | 0.01823 | 0.00000 |
| yes | 2777 | 2735 | 2735 | 0.1549 | 0.15426 | 0.15364 | -0.00014 |

### by time to kickoff

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 30-90m | 3817 | 3791 | 3791 | 0.1790 | 0.17941 | 0.16064 | 0.00171 |
| 6-24h | 48 | 12 | 12 | 0.1013 | 0.10043 | 0.08397 | 0.00857 |
| 90m-6h | 2324 | 2299 | 2299 | 0.1772 | 0.17772 | 0.15925 | -0.00061 |
| <30m | 1272 | 1267 | 1267 | 0.1593 | 0.15925 | 0.15146 | 0.00364 |
| >24h | 38 | 1 | 1 | 0.0653 | 0.06229 | 0.00810 | -0.16500 |

### by model version

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| shadow-0.4.0 | 7499 | 7370 | 7370 | 0.1749 | 0.17527 | 0.15848 | 0.00114 |

### by week

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 1 | 7086 | 6957 | 6957 | 0.1745 | 0.17479 | 0.15837 | 0.00122 |
| 2 | 413 | 413 | 413 | 0.1821 | 0.18344 | 0.16041 | -0.00022 |

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
| 2026_02_DET_BUF | 413 | 413 | 413 | 0.1821 | 0.18344 | 0.16041 | -0.00022 |

### by quote width band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| 3-5c | 2398 | 2371 | 2371 | 0.1601 | 0.16043 | 0.14013 | 0.00084 |
| 6-10c | 663 | 641 | 641 | 0.1763 | 0.17693 | 0.15612 | 0.00114 |
| <=2c | 3779 | 3742 | 3742 | 0.1788 | 0.17905 | 0.16484 | 0.00015 |
| >10c | 659 | 616 | 616 | 0.2070 | 0.20768 | 0.19298 | 0.00907 |

### by liquidity band

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| none | 7499 | 7370 | 7370 | 0.1749 | 0.17527 | 0.15848 | 0.00114 |

### by availability state

| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |
|---|---|---|---|---|---|---|---|
| DOUBTFUL | 18 | 0 | 0 | - | - | - | - |
| EXPECTED_ACTIVE | 6089 | 6051 | 6051 | 0.1744 | 0.17483 | 0.15456 | 0.00161 |
| EXPECTED_OUT | 9 | 0 | 0 | - | - | - | -0.16500 |
| None | 1319 | 1319 | 1319 | 0.1773 | 0.17729 | 0.17647 | 0.00017 |
| OUT | 44 | 0 | 0 | - | - | - | -0.00118 |
| QUESTIONABLE | 19 | 0 | 0 | - | - | - | - |
| UNKNOWN | 1 | 0 | 0 | - | - | - | - |

## Reading this report

Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or Brier difference of a few thousandths is not evidence. Segments with small counts are printed because hiding them would hide the sample size, not because they mean anything yet.
