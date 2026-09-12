# Player Engine v2: historical walk-forward evidence (HISTORICAL_RESEARCH)

`scripts/research/player_engine_v2_study.py`. Nothing here uses a 2026 outcome. Study A chooses the distribution family per statistic out of sample on the v2 opportunity x efficiency features (test seasons 2020-2025, prop-relevant subset). Study B is the head-to-head on the exact 2025 Kalshi-listed rungs at every archived horizon, clustered by game.

## A. Family choice on v2 features (ladder Brier, prop-relevant subset, pooled 2020-2025)

| statistic | rows | v1 best family (Brier) | v2 best family (Brier) | MAE ewma / v1 / v2 |
|---|---|---|---|---|
| receiving_yards | 14804 | scale_emp_binned (0.10096) | scale_emp_binned (0.10061) | 24.009 / 23.874 / 23.862 |
| rushing_yards | 5409 | scale_emp_binned (0.11254) | scale_emp_binned (0.11147) | 25.537 / 25.215 / 24.970 |
| passing_yards | 3178 | normal (0.13540) | normal (0.13425) | 61.895 / 59.373 / 58.873 |
| receptions | 14804 | scale_emp_binned (0.11844) | scale_emp_binned (0.11732) | 1.725 / 1.788 / 1.745 |
| carries | 5409 | scale_emp_binned (0.13176) | scale_emp_binned (0.12882) | 4.560 / 4.638 / 4.510 |
| attempts | 3178 | scale_emp_binned (0.11872) | normal (0.11753) | 7.208 / 6.942 / 6.846 |
| completions | 3178 | normal (0.11313) | normal (0.11180) | 5.124 / 4.887 / 4.836 |
| passing_tds | 3178 | poisson (0.17724) | negbin (0.17740) | 0.901 / 0.885 / 0.885 |
| interceptions | 3178 | negbin (0.19426) | negbin (0.19408) | 0.711 / 0.706 / 0.705 |
| touchdowns | 10920 | negbin (0.09102) | negbin (0.08954) | 0.484 / 0.477 / 0.472 |
| rush_rec_yards | 22941 | scale_emp_binned (0.06690) | scale_emp_binned (0.06630) | 25.465 / 24.879 / 24.376 |

Per-family detail (Brier / CRPS / ECE / tail ratio) is in results.json.

## B. Head-to-head on the 2025 Kalshi rungs

77207 rung x horizon rows over 264 games (books quoted within 10 cents). Arms: OLD = the incumbent's family on v1 features (research/kalshi_2025); DATA_V2 = this engine on v2 features (fitted <= 2024); MARKET = the monotone ladder midpoint; HYB_LOC(w) = location blend, HYB_MIX(w) = pmf mixture, w = market weight.

### T-24h

| arm | n | games | Brier | log loss | mean p | observed | Brier vs MARKET (clustered) | z |
|---|---|---|---|---|---|---|---|---|
| old | 14347 | 240 | 0.20100 | 0.58761 | 0.370 | 0.378 | +0.01076 ± 0.00181 | +6.0 |
| data_v2 | 15446 | 240 | 0.19816 | 0.57970 | 0.373 | 0.370 | +0.00988 ± 0.00164 | +6.0 |
| market_mono | 16934 | 250 | 0.18713 | 0.55265 | 0.382 | 0.366 | - | - |
| hyb_loc_0.3 | 12723 | 176 | 0.20192 | 0.58667 | 0.411 | 0.401 | +0.00647 ± 0.00141 | +4.6 |
| hyb_loc_0.5 | 12723 | 176 | 0.19982 | 0.58174 | 0.414 | 0.401 | +0.00437 ± 0.00109 | +4.0 |
| hyb_loc_0.7 | 12723 | 176 | 0.19828 | 0.57836 | 0.416 | 0.401 | +0.00283 ± 0.00079 | +3.6 |
| hyb_mix_0.3 | 12723 | 176 | 0.20088 | 0.58445 | 0.409 | 0.401 | +0.00543 ± 0.00132 | +4.1 |
| hyb_mix_0.5 | 12723 | 176 | 0.19830 | 0.57840 | 0.412 | 0.401 | +0.00286 ± 0.00094 | +3.1 |
| hyb_mix_0.7 | 12723 | 176 | 0.19655 | 0.57439 | 0.414 | 0.401 | +0.00110 ± 0.00056 | +2.0 |

### T-6h

| arm | n | games | Brier | log loss | mean p | observed | Brier vs MARKET (clustered) | z |
|---|---|---|---|---|---|---|---|---|
| old | 15549 | 253 | 0.19926 | 0.58301 | 0.368 | 0.372 | +0.01035 ± 0.00167 | +6.2 |
| data_v2 | 16760 | 253 | 0.19685 | 0.57632 | 0.369 | 0.365 | +0.00998 ± 0.00155 | +6.4 |
| market_mono | 18400 | 263 | 0.18641 | 0.55051 | 0.378 | 0.363 | - | - |
| hyb_loc_0.3 | 13640 | 180 | 0.19985 | 0.58163 | 0.408 | 0.395 | +0.00658 ± 0.00136 | +4.8 |
| hyb_loc_0.5 | 13640 | 180 | 0.19779 | 0.57684 | 0.410 | 0.395 | +0.00452 ± 0.00106 | +4.3 |
| hyb_loc_0.7 | 13640 | 180 | 0.19629 | 0.57349 | 0.412 | 0.395 | +0.00302 ± 0.00078 | +3.9 |
| hyb_mix_0.3 | 13640 | 180 | 0.19866 | 0.57888 | 0.406 | 0.395 | +0.00539 ± 0.00127 | +4.2 |
| hyb_mix_0.5 | 13640 | 180 | 0.19604 | 0.57273 | 0.409 | 0.395 | +0.00277 ± 0.00090 | +3.1 |
| hyb_mix_0.7 | 13640 | 180 | 0.19427 | 0.56860 | 0.411 | 0.395 | +0.00100 ± 0.00053 | +1.9 |

### T-90m

| arm | n | games | Brier | log loss | mean p | observed | Brier vs MARKET (clustered) | z |
|---|---|---|---|---|---|---|---|---|
| old | 17188 | 253 | 0.19903 | 0.58267 | 0.365 | 0.370 | +0.01020 ± 0.00159 | +6.4 |
| data_v2 | 18563 | 253 | 0.19634 | 0.57524 | 0.367 | 0.361 | +0.00966 ± 0.00145 | +6.7 |
| market_mono | 20172 | 263 | 0.18620 | 0.55016 | 0.378 | 0.360 | - | - |
| hyb_loc_0.3 | 14990 | 181 | 0.19911 | 0.57984 | 0.406 | 0.392 | +0.00625 ± 0.00128 | +4.9 |
| hyb_loc_0.5 | 14990 | 181 | 0.19702 | 0.57495 | 0.408 | 0.392 | +0.00416 ± 0.00100 | +4.1 |
| hyb_loc_0.7 | 14990 | 181 | 0.19549 | 0.57157 | 0.410 | 0.392 | +0.00264 ± 0.00075 | +3.5 |
| hyb_mix_0.3 | 14990 | 181 | 0.19801 | 0.57734 | 0.404 | 0.392 | +0.00516 ± 0.00120 | +4.3 |
| hyb_mix_0.5 | 14990 | 181 | 0.19545 | 0.57131 | 0.407 | 0.392 | +0.00259 ± 0.00085 | +3.1 |
| hyb_mix_0.7 | 14990 | 181 | 0.19375 | 0.56742 | 0.409 | 0.392 | +0.00089 ± 0.00051 | +1.8 |

### T-0

| arm | n | games | Brier | log loss | mean p | observed | Brier vs MARKET (clustered) | z |
|---|---|---|---|---|---|---|---|---|
| old | 18555 | 254 | 0.19933 | 0.58329 | 0.367 | 0.371 | +0.00999 ± 0.00162 | +6.2 |
| data_v2 | 19978 | 254 | 0.19686 | 0.57635 | 0.369 | 0.363 | +0.00935 ± 0.00148 | +6.3 |
| market_mono | 21701 | 264 | 0.18704 | 0.55195 | 0.383 | 0.362 | - | - |
| hyb_loc_0.3 | 16373 | 181 | 0.19975 | 0.58126 | 0.407 | 0.392 | +0.00597 ± 0.00130 | +4.6 |
| hyb_loc_0.5 | 16373 | 181 | 0.19774 | 0.57657 | 0.411 | 0.392 | +0.00395 ± 0.00103 | +3.8 |
| hyb_loc_0.7 | 16373 | 181 | 0.19629 | 0.57336 | 0.413 | 0.392 | +0.00250 ± 0.00078 | +3.2 |
| hyb_mix_0.3 | 16373 | 181 | 0.19861 | 0.57865 | 0.406 | 0.392 | +0.00483 ± 0.00122 | +4.0 |
| hyb_mix_0.5 | 16373 | 181 | 0.19612 | 0.57278 | 0.409 | 0.392 | +0.00233 ± 0.00087 | +2.7 |
| hyb_mix_0.7 | 16373 | 181 | 0.19452 | 0.56910 | 0.412 | 0.392 | +0.00073 ± 0.00052 | +1.4 |

### By statistic at T-0 (the close)

| statistic | n | OLD Brier | DATA_V2 Brier | MARKET Brier | HYB_LOC(0.7) Brier | DATA_V2 − MARKET | DATA_V2 − OLD |
|---|---|---|---|---|---|---|---|
| passing_tds | 684 | 0.15185 | 0.15122 | 0.15335 | 0.15149 | -0.00078 ± 0.00197 (z -0.4) | -0.00051 ± 0.00050 (z -1.0) |
| passing_yards | 2602 | 0.16954 | 0.16579 | 0.15972 | 0.16057 | +0.00732 ± 0.00243 (z +3.0) | -0.00222 ± 0.00156 (z -1.4) |
| receiving_yards | 6834 | 0.22184 | 0.22166 | 0.20898 | 0.21405 | +0.01184 ± 0.00211 (z +5.6) | -0.00017 ± 0.00090 (z -0.2) |
| receptions | 4445 | 0.19553 | 0.19927 | 0.18289 | 0.18629 | +0.01594 ± 0.00322 (z +5.0) | +0.00374 ± 0.00253 (z +1.5) |
| rushing_yards | 3412 | 0.22800 | 0.21408 | 0.20902 | 0.20963 | +0.00414 ± 0.00389 (z +1.1) | -0.00230 ± 0.00226 (z -1.0) |
| touchdowns | 3724 | 0.16909 | 0.16345 | 0.15685 | - | +0.00524 ± 0.00117 (z +4.5) | -0.00232 ± 0.00108 (z -2.2) |

### By statistic at T-24h

| statistic | n | OLD Brier | DATA_V2 Brier | MARKET Brier | HYB_LOC(0.7) Brier | DATA_V2 − MARKET | DATA_V2 − OLD |
|---|---|---|---|---|---|---|---|
| passing_tds | 651 | 0.15597 | 0.15556 | 0.15789 | 0.15478 | -0.00145 ± 0.00214 (z -0.7) | -0.00050 ± 0.00052 (z -1.0) |
| passing_yards | 2143 | 0.17332 | 0.16955 | 0.16513 | 0.16532 | +0.00607 ± 0.00293 (z +2.1) | -0.00251 ± 0.00183 (z -1.4) |
| receiving_yards | 5294 | 0.22467 | 0.22400 | 0.20933 | 0.21534 | +0.01301 ± 0.00257 (z +5.1) | -0.00068 ± 0.00110 (z -0.6) |
| receptions | 3384 | 0.20117 | 0.20490 | 0.18389 | 0.19032 | +0.01854 ± 0.00371 (z +5.0) | +0.00373 ± 0.00307 (z +1.2) |
| rushing_yards | 2565 | 0.22763 | 0.21398 | 0.20975 | 0.21164 | +0.00302 ± 0.00377 (z +0.8) | -0.00225 ± 0.00284 (z -0.8) |
| touchdowns | 2897 | 0.16662 | 0.16026 | 0.15319 | - | +0.00561 ± 0.00130 (z +4.3) | -0.00248 ± 0.00127 (z -2.0) |

### Hybrid weight preregistration

Selection on weeks 1-9 at T-90m: hyb_loc_0.3 0.20423, hyb_loc_0.5 0.20203, hyb_loc_0.7 0.20039, hyb_mix_0.3 0.20337, hyb_mix_0.5 0.20084, hyb_mix_0.7 0.19919, market_mono 0.18307, data_v2 0.19235. **Selected: market_mono**.

Confirmation on weeks 10-18 (paired Brier vs MARKET, clustered):

| arm | n | Brier | vs MARKET | z |
|---|---|---|---|---|
| hyb_loc_0.3 | 13095 | 0.19837 | +0.00631 ± 0.00141 | +4.5 |
| hyb_loc_0.5 | 13095 | 0.19629 | +0.00423 ± 0.00110 | +3.8 |
| hyb_loc_0.7 | 13095 | 0.19478 | +0.00273 ± 0.00082 | +3.3 |
| hyb_mix_0.3 | 13095 | 0.19724 | +0.00518 ± 0.00132 | +3.9 |
| hyb_mix_0.5 | 13095 | 0.19467 | +0.00261 ± 0.00093 | +2.8 |
| hyb_mix_0.7 | 13095 | 0.19296 | +0.00091 ± 0.00056 | +1.6 |
| market_mono | 16545 | 0.18689 | - | - |
| data_v2 | 14945 | 0.19731 | +0.00986 ± 0.00171 | +5.8 |

Market-ladder identification by horizon: {"FULL": {"T-0": 7361, "T-24h": 5671, "T-6h": 6150, "T-90m": 6736}, "PARTIAL": {"T-0": 10523, "T-24h": 8335, "T-6h": 8923, "T-90m": 9652}, "UNDERIDENTIFIED": {"T-0": 3817, "T-24h": 2928, "T-6h": 3327, "T-90m": 3784}}

## Reading

* The market is scored on ITS OWN rungs with its own monotone midpoint; a data arm that beats it here would be beating the close, which the encompassing result (research/model_vs_market) says the old model could not do. Where the market wins, it says so above.
* The hybrid weight is preregistered from weeks 1-9 and confirmed on weeks 10-18 of 2025; it is not tuned on 2026.
* All arms stay shadow-only prospectively; this study decides structure and weights, not authority.
