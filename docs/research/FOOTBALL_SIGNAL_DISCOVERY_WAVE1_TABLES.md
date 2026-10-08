# Football Signal Discovery Wave 1 (NFL) — generated tables

From `game_evaluation_report.json` (code `31ddffb9`, set 1 `83861082cc37`, set 2 `5f25764743e1`) and `prop_evaluation_report.json` (code `31ddffb9`). Do not edit: `python3 scripts/research/signal_discovery_wave1_report.py`.

Games: 2985 (2015–2025) with spread 2985, moneyline 2984; exclusions {'OUTCOME_MISMATCH': 33, 'TIE': 10}. Prop group tests: 141; prop market tests: 140.

## G1. Every game hypothesis (2015–2025; set-2 rows judged on block B in G2)

| Id | Status | Football effect | q | Market effect | q | Holm p (market) | Name |
|---|---|---|---|---|---|---|---|
| NFL-GAME-001 | FOOTBALL_VALIDATED | +0.210 | 0.000 | +0.007 | 0.788 | 1.000 | Efficiency CONTROL (|net EPA| >= moderate) -> winner / moneyline |
| NFL-GAME-002 | APPROX_EFFICIENT | +0.173 | 0.000 | +0.241 | 0.822 | 1.000 | MODERATE efficiency CONTROL -> closing spread |
| NFL-GAME-003 | APPROX_EFFICIENT | +0.243 | 0.000 | +0.474 | 0.614 | 1.000 | STRONG efficiency CONTROL -> closing spread |
| NFL-GAME-004 | APPROX_EFFICIENT | +5.249 | 0.000 | +0.231 | 0.614 | 1.000 | Opponent-adjusted EPA net (continuous) -> margin / ATS |
| NFL-GAME-005 | APPROX_EFFICIENT | +4.959 | 0.000 | +0.165 | 0.777 | 1.000 | QB / dropback efficiency mismatch -> margin / ATS |
| NFL-GAME-006 | REJECTED | -0.034 | 0.964 | -0.502 | 0.777 | 1.000 | Pass offence x pass defence, beyond overall efficiency -> margin / ATS |
| NFL-GAME-007 | REJECTED | +0.455 | 0.159 | +0.543 | 0.308 | 1.000 | Rush offence x rush defence, beyond overall efficiency -> margin / ATS |
| NFL-GAME-008 | APPROX_EFFICIENT | +3.006 | 0.000 | +0.272 | 0.513 | 1.000 | Pressure x protection (sack-rate matchup net) -> margin / ATS |
| NFL-GAME-009 | REJECTED | +0.557 | 0.070 | -0.347 | 0.464 | 1.000 | Pressure-rate matchup (participation, 2016-2025 only) -> ATS |
| NFL-GAME-010 | APPROX_EFFICIENT | +3.388 | 0.000 | +0.087 | 0.822 | 1.000 | Explosive offence x explosive prevention -> margin / ATS |
| NFL-GAME-011 | APPROX_EFFICIENT | +0.856 | 0.002 | -0.106 | 0.822 | 1.000 | Expected pace (both teams' adjusted plays) -> total residual |
| NFL-GAME-012 | APPROX_EFFICIENT | -0.795 | 0.004 | -0.269 | 0.554 | 1.000 | Tempo (adjusted seconds per play) -> total residual |
| NFL-GAME-013 | REJECTED | +1.689 | 0.070 | -0.353 | 0.822 | 1.000 | DEFENSIVE SUPPRESSION (both defences >= +0.5 SD on EPA allowed) -> under |
| NFL-GAME-014 | APPROX_EFFICIENT | -0.700 | 0.010 | +0.423 | 0.309 | 1.000 | Defensive quality sum (continuous) -> total residual |
| NFL-GAME-015 | REJECTED | +0.201 | 0.737 | -1.061 | 0.308 | 1.000 | CONTROL style: efficiency favourite that is run-leaning -> under |
| NFL-GAME-016 | REJECTED | -3.603 | 0.000 | -0.036 | 0.915 | 1.000 | Football scoring-baseline margin vs closing spread disagreement -> ATS |
| NFL-GAME-017 | REJECTED | -2.397 | 0.000 | -0.586 | 0.162 | 0.454 | Football scoring-baseline total vs closing total disagreement -> total residual |
| NFL-GAME-018 | REJECTED | -2.280 | 0.000 | -0.201 | 0.513 | 1.000 | Team scoring expectation vs DERIVED implied home team total |
| NFL-GAME-019 | APPROX_EFFICIENT | +0.629 | 0.014 | +0.129 | 0.788 | 1.000 | Rest differential -> home ATS |
| NFL-GAME-020 | DISCOVERY_ONLY | +0.099 | 0.737 | +2.700 | 0.822 | 1.000 | Short-week team (rest <= 5 vs opponent >= 6) -> ATS |
| NFL-GAME-021 | FOOTBALL_VALIDATED | +0.077 | 0.012 | +0.115 | 0.915 | 1.000 | Off-bye team (rest >= 13 vs opponent <= 8) -> ATS |
| NFL-GAME-022 | REJECTED | -0.156 | 0.000 | +0.037 | 0.924 | 1.000 | Divisional game: market underdog ATS |
| NFL-GAME-023 | APPROX_EFFICIENT | -0.132 | 0.000 | -0.934 | 0.336 | 1.000 | QB change (starter differs from previous game; NEAR_PIT) -> ATS of that team |
| NFL-GAME-024 | MARKET_WATCH | +2.073 | 0.000 | +1.317 | 0.082 | 0.135 | Indoor (dome/closed roof) -> total residual |
| NFL-GAME-025 | REJECTED | +0.041 | 0.051 | +0.922 | 0.308 | 1.000 | CLOSENESS (|net EPA| below the closeness threshold) -> market underdog ATS |
| NFL-GAME-026 | FOOTBALL_VALIDATED | +3.755 | 0.000 | — | — | — | Efficiency CONTROL -> first-half margin (football only) |
| NFL-GAME-027 | DATA_UNAVAILABLE | — | — | — | — | — | Weather (forecast vintages) |
| NFL-GAME-028 | DATA_UNAVAILABLE | — | — | — | — | — | Line / injury shocks (OL, skill, defensive injuries) |
| NFL-BASE-001 | BASELINE_REFERENCE | -0.000 | — | -0.003 | — | — | BASELINE: home team ATS |
| NFL-BASE-002 | BASELINE_REFERENCE | +0.149 | — | -0.067 | — | — | BASELINE: market favourite ATS |
| NFL-BASE-003 | BASELINE_REFERENCE | +5.247 | — | +0.245 | — | — | BASELINE: RAW (unadjusted) EPA net -> margin / ATS |
| NFL-DSC-001 | REJECTED | -0.206 | 0.737 | -0.794 | 0.351 | 1.000 | Within STRONG CONTROL: control side's neutral pass-rate advantage -> control-side ATS (negative) |
| NFL-DSC-002 | MARKET_WATCH | +4.335 | 0.000 | +0.659 | 0.082 | 0.158 | Offensive success-rate quality difference -> home ATS |
| NFL-DSC-003 | REJECTED | -0.381 | 0.164 | -0.438 | 0.309 | 1.000 | Defences that slow opponents (adjusted seconds/play allowed, both teams) -> total residual (under) |
| NFL-DSC-004 | REJECTED | -0.113 | 0.737 | +0.034 | 0.915 | 1.000 | Efficiency mismatch size |net EPA| -> total residual (under) |
| NFL-DSC-005 | REJECTED | +0.478 | 0.097 | -0.365 | 0.351 | 1.000 | Neutral pass-rate difference (unconditional) -> home ATS (negative) -- cross-sport test of CFB-DSC-003 |

## G2. Set 2 on block B only

| Id | Status | Market effect | q | n |
|---|---|---|---|---|
| NFL-DSC-001 | REJECTED | +0.002 | 0.998 | 416 |
| NFL-DSC-002 | APPROX_EFFICIENT | +0.539 | 0.221 | 1676 |
| NFL-DSC-003 | REJECTED | -0.125 | 0.875 | 1676 |
| NFL-DSC-004 | REJECTED | +0.559 | 0.221 | 1676 |
| NFL-DSC-005 | REJECTED | -0.417 | 0.341 | 1676 |

## G3. Slope hypotheses: market residual detail

| Id | n | β/SD | p | Block A β (p) | Block B β (p) | seasons expected sign | Follow \|z\|≥1: n, cover, ROI@−110 |
|---|---|---|---|---|---|---|---|
| NFL-BASE-003 | 2985 | +0.245 | 0.303 | +0.261 (0.485) | +0.231 (0.451) | 54.5% | 916, 48.7%, -7.0% |
| NFL-DSC-001 | 661 | -0.794 | 0.128 | -2.365 (0.006) | +0.002 (0.998) | 63.6% | 228, 52.9%, 1.1% |
| NFL-DSC-002 | 2985 | +0.659 | 0.005 | +0.816 (0.023) | +0.536 (0.089) | 100.0% | 957, 49.5%, -5.5% |
| NFL-DSC-003 | 2985 | -0.438 | 0.074 | -0.851 (0.023) | -0.125 (0.700) | 81.8% | 981, 51.3%, -2.0% |
| NFL-DSC-004 | 2985 | +0.034 | 0.885 | -0.832 (0.033) | +0.536 (0.068) | 54.5% | 901, 48.8%, -6.9% |
| NFL-DSC-005 | 2985 | -0.365 | 0.129 | -0.296 (0.393) | -0.423 (0.204) | 63.6% | 962, 51.6%, -1.5% |
| NFL-GAME-004 | 2985 | +0.231 | 0.327 | +0.315 (0.407) | +0.188 (0.531) | 54.5% | 908, 48.4%, -7.7% |
| NFL-GAME-005 | 2985 | +0.165 | 0.482 | +0.370 (0.336) | +0.061 (0.838) | 54.5% | 918, 48.0%, -8.4% |
| NFL-GAME-006 | 2985 | -0.502 | 0.492 | +0.564 (0.621) | -1.210 (0.205) | 27.3% | 918, 48.0%, -8.4% |
| NFL-GAME-007 | 2985 | +0.543 | 0.061 | +0.010 (0.982) | +0.921 (0.015) | 54.5% | 891, 48.3%, -7.7% |
| NFL-GAME-008 | 2985 | +0.272 | 0.237 | +0.449 (0.251) | +0.160 (0.572) | 72.7% | 878, 51.6%, -1.5% |
| NFL-GAME-009 | 2691 | -0.347 | 0.186 | -0.594 (0.095) | -0.014 (0.971) | 40.0% | 799, 48.8%, -6.8% |
| NFL-GAME-010 | 2985 | +0.087 | 0.713 | +0.033 (0.936) | +0.158 (0.587) | 54.5% | 905, 47.9%, -8.5% |
| NFL-GAME-011 | 2985 | -0.106 | 0.662 | +0.418 (0.306) | -0.319 (0.327) | 36.4% | 974, 47.7%, -8.9% |
| NFL-GAME-012 | 2985 | -0.269 | 0.277 | -0.706 (0.061) | -0.154 (0.684) | 81.8% | 863, 50.6%, -3.4% |
| NFL-GAME-014 | 2985 | +0.423 | 0.082 | +0.380 (0.319) | +0.454 (0.151) | 45.5% | 979, 47.7%, -9.0% |
| NFL-GAME-016 | 2985 | -0.036 | 0.876 | +0.004 (0.991) | -0.089 (0.758) | 36.4% | 860, 50.4%, -3.8% |
| NFL-GAME-017 | 2985 | -0.586 | 0.016 | -0.764 (0.054) | -0.534 (0.086) | 18.2% | 920, 49.9%, -4.7% |
| NFL-GAME-018 | 2985 | -0.201 | 0.239 | -0.654 (0.018) | +0.044 (0.840) | 36.4% | 871, 47.2%, -9.8% |
| NFL-GAME-019 | 2985 | +0.129 | 0.544 | +0.061 (0.848) | +0.178 (0.531) | 36.4% | 653, 51.3%, -2.0% |

## G4. Side / total hypotheses

| Id | n | Win / lift | Market n | Cover or O/U hit | Mean resid (p) | ROI@−110 | ML win − implied | ML ROI |
|---|---|---|---|---|---|---|---|---|
| NFL-BASE-001 | 2926 | 55.0% | 2926 | 48.9% | -0.00 (0.991) | -6.6% | -0.009 | -5.1% |
| NFL-BASE-002 | 2981 | 66.3% | 2981 | 48.8% | -0.07 (0.774) | -6.9% | +0.000 | -3.2% |
| NFL-GAME-001 | 1252 | 71.2% | 1252 | 48.5% | +0.36 (0.312) | -7.3% | +0.007 | -2.5% |
| NFL-GAME-002 | 591 | 67.5% | 591 | 49.0% | +0.24 (0.638) | -6.5% | +0.015 | -1.6% |
| NFL-GAME-003 | 661 | 74.6% | 661 | 48.2% | +0.47 (0.348) | -8.1% | +0.000 | -3.3% |
| NFL-GAME-013 | 245 | +1.69 | 245 | 52.7% | -0.35 (0.673) | 0.6% | — | — |
| NFL-GAME-015 | 632 | +0.20 | 632 | 49.3% | -1.06 (0.042) | -5.9% | — | — |
| NFL-GAME-020 | 5 | 60.0% | 5 | 60.0% | +2.70 (0.700) | 14.5% | +0.008 | -4.4% |
| NFL-GAME-021 | 292 | 58.2% | 292 | 50.5% | +0.11 (0.865) | -3.5% | +0.033 | 2.1% |
| NFL-GAME-022 | 1061 | 33.2% | 1061 | 51.8% | +0.04 (0.924) | -1.1% | +0.002 | -4.4% |
| NFL-GAME-023 | 500 | 37.2% | 500 | 49.7% | -0.93 (0.101) | -5.1% | -0.030 | -13.6% |
| NFL-GAME-024 | 842 | +2.07 | 842 | 50.4% | +1.32 (0.004) | -3.9% | — | — |
| NFL-GAME-025 | 634 | 40.4% | 634 | 53.2% | +0.92 (0.062) | 1.5% | +0.015 | 0.8% |
| NFL-GAME-026 | 1252 | 71.2% | 1252 | 48.5% | +0.36 (0.312) | -7.3% | +0.007 | -2.5% |

## G5. Efficiency-CONTROL tiers (|net EPA/play| ≥ 0.075 moderate, ≥ 0.115 strong)

| Tier | n | Win | ATS W-L-P | Cover [95%] | Mean resid (p) | ROI@−110 | Mean spread (side) | ML n | Win − implied | ML ROI [95%] |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL_CONTROL | 1252 | 71.2% | 596-632-24 | 48.5% [45.7%, 51.3%] | +0.36 (0.312) | -7.3% | -6.8 | 1251 | +0.007 | -2.5% [-6.2%, 1.2%] |
| ALL_MODERATE | 591 | 67.5% | 283-295-13 | 49.0% [44.9%, 53.0%] | +0.24 (0.638) | -6.5% | -5.0 | 590 | +0.015 | -1.6% [-7.4%, 4.1%] |
| ALL_STRONG | 661 | 74.6% | 313-337-11 | 48.2% [44.3%, 52.0%] | +0.47 (0.348) | -8.1% | -8.4 | 661 | +0.000 | -3.3% [-7.8%, 1.4%] |
| AWAY_MODERATE | 311 | 62.4% | 148-157-6 | 48.5% [43.0%, 54.1%] | +0.23 (0.735) | -7.4% | -2.9 | 311 | +0.027 | -0.2% [-9.2%, 9.1%] |
| AWAY_STRONG | 361 | 69.5% | 168-187-6 | 47.3% [42.2%, 52.5%] | +0.25 (0.722) | -9.7% | -6.7 | 361 | -0.011 | -4.3% [-11.3%, 2.4%] |
| HOME_MODERATE | 280 | 73.2% | 135-138-7 | 49.5% [43.6%, 55.3%] | +0.25 (0.743) | -5.6% | -7.3 | 279 | +0.002 | -3.1% [-10.3%, 4.0%] |
| HOME_STRONG | 300 | 80.7% | 145-150-5 | 49.2% [43.5%, 54.8%] | +0.75 (0.312) | -6.2% | -10.4 | 300 | +0.013 | -2.0% [-7.9%, 3.8%] |

## G6. Market disagreement regimes

| Football | Market regime | n | Win | ATS cover | Mean resid (p) | ML implied | ML win | ML ROI |
|---|---|---|---|---|---|---|---|---|
| CONTROL_STRONG | MARKET_MODERATE(fav 3-6.5) | 201 | 65.2% | 45.2% | +0.17 (0.852) | 66.1% | 65.2% | -4.8% |
| CONTROL_STRONG | MARKET_SKEPTICAL(fav<3 or dog) | 36 | 52.8% | 55.6% | +1.78 (0.356) | 48.3% | 52.8% | 3.5% |
| CONTROL_STRONG | MARKET_STRONG(fav>=7) | 424 | 80.9% | 48.9% | +0.51 (0.427) | 80.8% | 80.9% | -3.1% |
| CONTROL_MODERATE | MARKET_MODERATE(fav 3-6.5) | 274 | 69.0% | 53.5% | +1.16 (0.121) | 65.4% | 69.0% | 2.4% |
| CONTROL_MODERATE | MARKET_SKEPTICAL(fav<3 or dog) | 121 | 43.8% | 42.5% | -1.63 (0.165) | 48.5% | 43.8% | -12.9% |
| CONTROL_MODERATE | MARKET_STRONG(fav>=7) | 196 | 80.1% | 46.6% | +0.12 (0.891) | 77.6% | 80.0% | -0.2% |

Football baseline and closing spread disagree on the favourite in 480 games: football side won 43.1% (implied 42.3%); football side ATS 52.5%, mean resid +1.23 (p 0.042).

## G7. Walk-forward

* **WF-ATS**: {"n": 2201, "oos_corr": -0.0009, "oos_corr_ci_boot": [-0.040755512904684474, 0.040249183134860395], "oos_mse_model": 164.608, "oos_mse_zero": 163.7887}
  * picks: n 74, 34-39-1, cover 46.6%, ROI@−110 -11.1% [-32.0%, 10.2%]
  * folds: 2018: r +0.018, picks 31 @ 48.4%; 2019: r -0.115, picks 16 @ 60.0%; 2020: r +0.088, picks 6 @ 33.3%; 2021: r +0.023, picks 5 @ 60.0%; 2022: r -0.017, picks 2 @ 100.0%; 2023: r +0.017, picks 2 @ 0.0%; 2024: r +0.037, picks 1 @ 0.0%; 2025: r -0.001, picks 11 @ 27.3%
* **WF-ML**: {"brier_market": 0.2103, "brier_market_plus_football": 0.2103, "delta_logloss": 0.0001, "delta_logloss_ci_boot": [-0.0013567742578711737, 0.0015673497731709572], "logloss_market": 0.608, "logloss_market_plus_football": 0.6081, "n": 2201}
  * folds: 2018: Δlogloss +0.0000; 2019: Δlogloss -0.0002; 2020: Δlogloss +0.0008; 2021: Δlogloss +0.0004; 2022: Δlogloss +0.0006; 2023: Δlogloss +0.0004; 2024: Δlogloss -0.0009; 2025: Δlogloss -0.0001
* **WF-TOTAL**: {"n": 2201, "oos_corr": 0.0455, "oos_corr_ci_boot": [0.004431593922582805, 0.0871865271349551], "oos_mse_model": 174.2743, "oos_mse_zero": 173.914}
  * picks: n 243, 134-106-3, cover 55.8%, ROI@−110 6.6% [-5.3%, 18.3%]
  * folds: 2018: r +0.021, picks 53 @ 54.9%; 2019: r +0.006, picks 23 @ 69.6%; 2020: r +0.134, picks 21 @ 57.1%; 2021: r +0.065, picks 45 @ 56.8%; 2022: r +0.038, picks 40 @ 52.5%; 2023: r +0.103, picks 18 @ 55.6%; 2024: r -0.011, picks 26 @ 57.7%; 2025: r -0.027, picks 17 @ 41.2%

## G8. Stage A screen (block A 2015–2019; exploration only)

272 associations; market q<0.05: 1; q<0.10: 3.

| Scope | Feature | Target | n | β/SD | z | q |
|---|---|---|---|---|---|---|
| WITHIN_STRONG | offdiff.neutral_pass_rate | control_side_ats_resid | 245 | -2.255 | -2.73 | 0.027 |
| TOTAL | defsum.sec_per_play | total_resid | 1309 | -0.845 | -2.27 | 0.091 |
| SIDE | offdiff.success_rate | home_ats_resid | 1309 | +0.811 | +2.27 | 0.091 |
| TOTAL | abs_net.epa_play | total_resid | 1309 | -0.777 | -2.13 | 0.124 |
| WITHIN_STRONG | offdiff.early_epa | control_side_ats_resid | 245 | +1.697 | +2.07 | 0.142 |
| WITHIN_STRONG | offdiff.epa_play | control_side_ats_resid | 245 | +1.689 | +2.05 | 0.147 |
| WITHIN_STRONG | offdiff.neutral_proe | control_side_ats_resid | 245 | -1.690 | -2.04 | 0.147 |
| WITHIN_STRONG | offdiff.explosive_rush_rate | control_side_ats_resid | 245 | +1.636 | +2.01 | 0.156 |
| TOTAL | gap.total | total_resid | 1309 | -0.719 | -1.93 | 0.181 |
| TOTAL | env.sec_per_play | total_resid | 1309 | -0.709 | -1.88 | 0.202 |
| WITHIN_MODERATE | net.early_epa | control_side_ats_resid | 253 | +1.401 | +1.87 | 0.202 |
| WITHIN_STRONG | defdiff.success_rate | control_side_ats_resid | 245 | -1.634 | -1.78 | 0.239 |
| TOTAL | baseline.total | total_resid | 1309 | -0.643 | -1.66 | 0.301 |
| TOTAL | defsum.td_per_drive | total_resid | 1309 | +0.599 | +1.66 | 0.301 |
| TOTAL | offsum.success_rate | total_resid | 1309 | -0.640 | -1.66 | 0.301 |

## P1. Prop families: walk-forward accuracy (test seasons 2018–2026; MAE, lower is better)

| Family | n | Players | Season avg | EWMA | Usage | Opportunity model | Gain vs best baseline [95% game-cluster] | Seasons model ahead | Gain w/o top-10 players | PI50 / PI80 coverage |
|---|---|---|---|---|---|---|---|---|---|---|
| QB_attempts | 3995 | 121 | 8.15 | 7.86 | 7.78 | 7.67 | +0.108 (+1.4%) [+0.018, +0.198] vs USAGE | 5/9 | -0.014 | 0.49 / 0.78 |
| QB_completions | 3995 | 121 | 5.61 | 5.42 | 5.36 | 5.32 | +0.045 (+0.8%) [-0.012, +0.104] vs USAGE | 5/9 | -0.036 | 0.48 / 0.77 |
| QB_ints | 3995 | 121 | 0.74 | 0.71 | 0.71 | 0.71 | +0.007 (+0.9%) [-0.002, +0.015] vs USAGE | 7/9 | -0.004 | 0.52 / 0.81 |
| QB_pass_td | 3995 | 121 | 0.96 | 0.93 | 0.92 | 0.92 | +0.001 (+0.1%) [-0.008, +0.009] vs USAGE | 3/9 | -0.009 | 0.49 / 0.79 |
| QB_pass_yards | 3995 | 121 | 68.76 | 66.11 | 65.55 | 64.61 | +0.935 (+1.4%) [+0.253, +1.597] vs USAGE | 7/9 | -0.088 | 0.47 / 0.77 |
| QB_rush_yards | 3995 | 121 | 11.77 | 11.45 | 12.28 | 11.84 | -0.396 (-3.5%) [-0.524, -0.271] vs EWMA | 3/9 | -0.575 | 0.42 / 0.73 |
| RB_carries | 6709 | 236 | 4.40 | 4.40 | 4.62 | 4.11 | +0.287 (+6.5%) [+0.235, +0.340] vs SEASON_AVG | 9/9 | +0.223 | 0.50 / 0.80 |
| RB_rec_yards | 6128 | 229 | 14.83 | 14.17 | 14.15 | 13.83 | +0.320 (+2.3%) [+0.205, +0.427] vs USAGE | 7/9 | +0.181 | 0.51 / 0.81 |
| RB_receptions | 6128 | 229 | 1.54 | 1.48 | 1.47 | 1.53 | -0.057 (-3.9%) [-0.104, -0.014] vs USAGE | 8/9 | -0.080 | 0.50 / 0.81 |
| RB_rush_yards | 6709 | 236 | 26.16 | 25.74 | 26.75 | 25.09 | +0.648 (+2.5%) [+0.397, +0.900] vs EWMA | 7/9 | +0.411 | 0.48 / 0.79 |
| TE_rec_yards | 4083 | 124 | 21.83 | 21.00 | 21.01 | 20.80 | +0.203 (+1.0%) [-0.025, +0.419] vs EWMA | 8/9 | -0.017 | 0.52 / 0.81 |
| TE_receptions | 4083 | 124 | 1.72 | 1.66 | 1.65 | 1.65 | -0.002 (-0.1%) [-0.020, +0.014] vs USAGE | 6/9 | -0.022 | 0.49 / 0.79 |
| WR_rec_yards | 10111 | 312 | 29.01 | 27.74 | 27.69 | 27.10 | +0.581 (+2.1%) [+0.452, +0.708] vs USAGE | 9/9 | +0.498 | 0.50 / 0.80 |
| WR_receptions | 10111 | 312 | 1.88 | 1.80 | 1.79 | 1.76 | +0.034 (+1.9%) [+0.025, +0.042] vs USAGE | 9/9 | +0.028 | 0.49 / 0.79 |

## P2. Feature-group ablations (MAE gain when the group is included; + = helps; BH q over all 140 group tests)

| Family | HOME | IX_PACE_x_PASSDEF | IX_PACE_x_SCRIPT | IX_PRESSURE_x_PASSDEF | IX_SHARE_x_PASSDEF | IX_SHARE_x_PRESSURE | IX_SHARE_x_QBEFF | IX_SHARE_x_RUSHDEF | IX_SHARE_x_SCRIPT | PACE | PASS_DEF | PASS_TENDENCY | PRESSURE | QB_EFF | ROLE_RECENCY | RUSH_DEF | SCRIPT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| QB_attempts | -0.004 (q 0.67, 4/9) | · | -0.000 (q 0.73, 4/9) | · | · | · | · | · | · | -0.004 (q 0.76, 3/9) | -0.005 (q 0.44, 3/9) | +0.006 (q 0.84, 6/9) | -0.016 (q 0.14, 2/9) | +0.007 (q 0.53, 6/9) | **+0.109** (q 0.00, 6/9) | +0.001 (q 0.98, 4/9) | +0.005 (q 0.76, 5/9) |
| QB_completions | -0.001 (q 0.93, 4/9) | · | · | · | · | · | · | · | · | -0.008 (q 0.44, 2/9) | -0.007 (q 0.38, 3/9) | +0.011 (q 0.48, 6/9) | -0.005 (q 0.58, 4/9) | +0.000 (q 0.99, 5/9) | **+0.079** (q 0.00, 6/9) | +0.004 (q 0.76, 5/9) | +0.002 (q 0.84, 5/9) |
| QB_ints | -0.000 (q 0.67, 3/9) | · | · | · | · | · | · | · | · | +0.001 (q 0.35, 7/9) | -0.000 (q 0.76, 4/9) | -0.001 (q 0.38, 4/9) | -0.001 (q 0.11, 1/9) | -0.000 (q 0.93, 2/9) | +0.001 (q 0.65, 7/9) | **+0.002** (q 0.04, 6/9) | +0.000 (q 0.84, 5/9) |
| QB_pass_td | -0.002 (q 0.25, 4/9) | · | · | · | · | · | · | · | · | -0.002 (q 0.11, 4/9) | -0.002 (q 0.25, 4/9) | -0.002 (q 0.31, 3/9) | -0.001 (q 0.30, 4/9) | -0.002 (q 0.03, 2/9) | +0.002 (q 0.44, 4/9) | -0.000 (q 0.99, 5/9) | -0.000 (q 0.40, 3/9) |
| QB_pass_yards | -0.064 (q 0.70, 3/9) | +0.005 (q 0.83, 6/9) | · | +0.026 (q 0.84, 6/9) | · | · | · | · | · | -0.035 (q 0.81, 3/9) | -0.028 (q 0.89, 5/9) | +0.010 (q 0.97, 5/9) | -0.048 (q 0.76, 4/9) | -0.100 (q 0.11, 4/9) | **+0.946** (q 0.00, 8/9) | +0.088 (q 0.57, 6/9) | -0.082 (q 0.40, 2/9) |
| QB_rush_yards | -0.007 (q 0.58, 6/9) | · | · | · | · | · | · | · | · | -0.056 (q 0.00, 1/9) | -0.063 (q 0.00, 0/9) | -0.014 (q 0.07, 4/9) | -0.069 (q 0.00, 3/9) | -0.013 (q 0.05, 5/9) | +0.010 (q 0.84, 5/9) | **+0.047** (q 0.00, 7/9) | -0.027 (q 0.00, 2/9) |
| RB_carries | +0.001 (q 0.38, 6/9) | · | · | · | · | · | · | -0.000 (q 0.99, 4/9) | -0.000 (q 0.63, 4/9) | +0.005 (q 0.35, 6/9) | +0.008 (q 0.13, 5/9) | +0.010 (q 0.32, 6/9) | -0.004 (q 0.39, 2/9) | +0.002 (q 0.57, 5/9) | **+0.217** (q 0.00, 9/9) | +0.002 (q 0.44, 5/9) | +0.007 (q 0.24, 8/9) |
| RB_rec_yards | -0.004 (q 0.57, 4/9) | · | · | · | · | · | · | · | · | +0.002 (q 0.84, 5/9) | *+0.048* (q 0.01, 5/9) | -0.022 (q 0.25, 2/9) | -0.044 (q 0.00, 2/9) | **+0.033** (q 0.00, 6/9) | **+0.152** (q 0.00, 8/9) | **+0.017** (q 0.00, 7/9) | -0.017 (q 0.05, 1/9) |
| RB_receptions | -0.000 (q 0.31, 3/9) | · | · | · | · | **+0.001** (q 0.01, 6/9) | · | · | *+0.004* (q 0.00, 5/9) | +0.001 (q 0.70, 3/9) | **+0.005** (q 0.01, 6/9) | -0.006 (q 0.01, 4/9) | -0.005 (q 0.00, 4/9) | *+0.002* (q 0.09, 6/9) | +0.006 (q 0.44, 8/9) | +0.001 (q 0.60, 5/9) | *+0.008* (q 0.00, 3/9) |
| RB_rush_yards | -0.016 (q 0.08, 2/9) | · | · | · | · | · | · | +0.000 (q 0.99, 4/9) | -0.004 (q 0.51, 5/9) | -0.021 (q 0.58, 5/9) | +0.027 (q 0.40, 5/9) | +0.040 (q 0.44, 8/9) | **+0.047** (q 0.00, 6/9) | +0.006 (q 0.63, 5/9) | **+0.566** (q 0.00, 8/9) | **+0.065** (q 0.00, 6/9) | +0.017 (q 0.44, 6/9) |
| TE_rec_yards | -0.019 (q 0.31, 3/9) | · | · | · | -0.018 (q 0.44, 5/9) | · | · | · | · | +0.017 (q 0.53, 7/9) | -0.026 (q 0.40, 3/9) | +0.000 (q 0.99, 6/9) | +0.017 (q 0.34, 6/9) | -0.009 (q 0.84, 4/9) | **+0.520** (q 0.00, 8/9) | **+0.069** (q 0.02, 7/9) | -0.024 (q 0.06, 0/9) |
| TE_receptions | -0.000 (q 0.76, 6/9) | · | · | · | -0.000 (q 0.76, 2/9) | · | · | · | · | -0.002 (q 0.44, 5/9) | -0.001 (q 0.57, 4/9) | -0.000 (q 0.89, 5/9) | -0.000 (q 0.97, 4/9) | -0.000 (q 0.89, 6/9) | **+0.034** (q 0.00, 7/9) | +0.001 (q 0.76, 6/9) | -0.002 (q 0.10, 0/9) |
| WR_rec_yards | -0.013 (q 0.08, 4/9) | · | · | · | -0.009 (q 0.20, 5/9) | · | -0.019 (q 0.28, 3/9) | · | · | +0.026 (q 0.11, 4/9) | +0.000 (q 0.99, 4/9) | -0.018 (q 0.01, 5/9) | -0.041 (q 0.00, 3/9) | +0.016 (q 0.48, 4/9) | **+0.384** (q 0.00, 9/9) | *+0.030* (q 0.05, 5/9) | -0.021 (q 0.01, 4/9) |
| WR_receptions | -0.001 (q 0.03, 1/9) | · | · | · | -0.000 (q 0.44, 3/9) | · | · | · | +0.000 (q 0.88, 5/9) | +0.000 (q 0.82, 5/9) | -0.000 (q 0.97, 3/9) | -0.000 (q 0.76, 3/9) | -0.001 (q 0.14, 5/9) | +0.000 (q 0.83, 4/9) | **+0.023** (q 0.00, 9/9) | +0.001 (q 0.28, 6/9) | -0.001 (q 0.65, 4/9) |

Bold = FOOTBALL_VALIDATED (q<0.05, gain>0, ≥60% seasons); italic = DISCOVERY_ONLY.

## P3. Role stability: model gain over the best baseline by role class (MAE points)

| Family | STABLE_ROLE | ROLE_CHANGE | INJURY_DEPENDENT |
|---|---|---|---|
| QB_attempts | -0.020 (n 3561) | +2.115 (n 218) | +0.198 (n 216) |
| QB_completions | -0.030 (n 3561) | +1.342 (n 218) | -0.028 (n 216) |
| QB_ints | +0.005 (n 3561) | +0.030 (n 218) | +0.009 (n 216) |
| QB_pass_td | -0.001 (n 3561) | +0.018 (n 218) | +0.012 (n 216) |
| QB_pass_yards | +0.137 (n 3561) | +14.515 (n 218) | +0.377 (n 216) |
| QB_rush_yards | -0.405 (n 3561) | +0.117 (n 218) | -0.767 (n 216) |
| RB_carries | +0.265 (n 5658) | +0.304 (n 388) | +0.460 (n 663) |
| RB_rec_yards | +0.303 (n 5260) | +0.758 (n 275) | +0.270 (n 593) |
| RB_receptions | -0.024 (n 5260) | +0.101 (n 275) | -0.430 (n 593) |
| RB_rush_yards | +0.472 (n 5658) | +3.419 (n 388) | +0.530 (n 663) |
| TE_rec_yards | +0.141 (n 3786) | +0.948 (n 40) | +0.996 (n 257) |
| TE_receptions | -0.007 (n 3786) | +0.122 (n 40) | +0.046 (n 257) |
| WR_rec_yards | +0.521 (n 8624) | +4.797 (n 97) | +0.657 (n 1390) |
| WR_receptions | +0.031 (n 8624) | +0.283 (n 97) | +0.031 (n 1390) |

## P4. Kalshi ladders: residual vs line, information, economics

Checkpoints: 2025 T-90m (YES bid/ask), 2026 LAST_PREGAME ≤ 24 h (both asks). Market median = interpolated 50% rung.

| Family | Ladders (2025/2026) | Actual − median: mean / median [95%] | Share over median | MAE market / model | Resid ~ (model − market): β (p, q) | Model rule: n, win, ROI [95%] | Always-NO ROI [95%] (post hoc) | Always-YES ROI (post hoc) |
|---|---|---|---|---|---|---|---|---|
| QB_attempts | 0/75 | +0.79 / -0.90 [-1.35, +2.96] | 46.7% | 7.36 / 8.04 | +0.062 (0.88, 0.98) | 18, 50.0%, -8.6% [-48.9%, +31.8%] | -2.2% [-22.3%, 17.0%] | -8.2% |
| QB_completions | 0/75 | +0.53 / +0.44 [-0.73, +1.75] | 52.0% | 5.13 / 5.22 | +0.442 (0.40, 0.97) | 23, 56.5%, +2.5% [-36.1%, +40.4%] | -18.0% [-38.1%, 3.8%] | 8.2% |
| QB_ints | 0/39 | -0.55 / -1.01 [-0.75, -0.34] | 7.7% | 0.68 / 0.56 | +0.150 (0.88, 0.98) | 39, 53.8%, +8.5% [-22.7%, +40.6%] | 8.5% [-22.7%, 40.6%] | -17.2% |
| QB_pass_td | 145/89 | -0.38 / -0.50 [-0.54, -0.24] | 34.2% | 1.00 / 0.96 | -0.280 (0.46, 0.97) | 211, 53.1%, -6.1% [-17.7%, +5.9%] | -8.4% [-19.9%, 3.1%] | -4.8% |
| QB_pass_yards | 261/87 | +0.94 / +2.61 [-6.88, +8.75] | 51.1% | 55.94 / 58.93 | -0.049 (0.80, 0.98) | 85, 47.1%, -18.4% [-36.1%, +0.6%] | -8.1% [-18.0%, 1.7%] | -5.9% |
| QB_rush_yards | 138/58 | -1.31 / -3.28 [-3.48, +0.97] | 39.8% | 13.23 / 13.40 | +0.231 (0.47, 0.97) | 116, 57.8%, +1.7% [-15.3%, +18.1%] | 7.6% [-5.1%, 19.7%] | -21.1% |
| RB_carries | 0/98 | -0.11 / -0.19 [-1.07, +0.88] | 49.0% | 3.58 / 3.96 | +0.026 (0.91, 0.98) | 51, 54.9%, +1.3% [-25.2%, +26.4%] | -9.8% [-28.2%, 8.9%] | -0.5% |
| RB_rec_yards | 188/44 | +0.50 / -5.00 [-2.00, +3.14] | 40.5% | 16.11 / 15.95 | -0.272 (0.50, 0.97) | 186, 55.4%, -0.4% [-12.9%, +13.4%] | 9.1% [-2.6%, 21.1%] | -23.8% |
| RB_receptions | 140/83 | -0.55 / -0.85 [-0.81, -0.30] | 30.5% | 1.64 / 1.49 | +0.371 (0.20, 0.89) | 190, 63.7%, +14.9% [+2.3%, +26.8%] | 10.6% [-1.0%, 22.9%] | -24.5% |
| RB_rush_yards | 332/127 | +2.98 / -1.67 [+0.54, +5.51] | 47.1% | 24.46 / 25.75 | -0.123 (0.50, 0.97) | 251, 48.2%, -12.4% [-23.7%, -1.1%] | -3.7% [-11.9%, 5.1%] | -10.6% |
| TE_rec_yards | 235/92 | +3.34 / -2.12 [+0.11, +6.31] | 46.5% | 20.93 / 21.28 | +0.315 (0.16, 0.86) | 207, 55.1%, -1.0% [-12.7%, +10.8%] | -0.8% [-10.3%, 9.4%] | -13.8% |
| TE_receptions | 175/98 | -0.43 / -0.67 [-0.67, -0.19] | 37.4% | 1.74 / 1.69 | +0.184 (0.40, 0.97) | 210, 56.2%, +0.4% [-11.8%, +12.2%] | -2.6% [-13.8%, 7.7%] | -11.4% |
| WR_rec_yards | 497/205 | +3.66 / -1.90 [+1.15, +6.22] | 47.9% | 25.92 / 26.80 | -0.111 (0.53, 0.97) | 438, 51.4%, -7.4% [-15.7%, +1.1%] | -4.4% [-11.3%, 2.2%] | -10.3% |
| WR_receptions | 373/204 | -0.47 / -0.69 [-0.65, -0.30] | 37.1% | 1.76 / 1.74 | +0.090 (0.58, 0.97) | 443, 56.0%, -0.1% [-8.2%, +8.4%] | -2.1% [-9.6%, 5.0%] | -12.2% |

## P5. Signal features vs the line residual (β per SD of the group's lead feature; BH q over all market tests)

* **QB_attempts**: HOME +0.70 (p 0.573, q 0.97); PACE -0.33 (p 0.772, q 0.98); PASS_DEF +1.70 (p 0.134, q 0.86); PASS_TENDENCY +1.79 (p 0.080, q 0.83); PRESSURE -0.37 (p 0.682, q 0.98); QB_EFF -0.16 (p 0.852, q 0.98); ROLE_RECENCY +0.23 (p 0.748, q 0.98); RUSH_DEF -0.57 (p 0.548, q 0.97); SCRIPT +0.64 (p 0.625, q 0.98)
* **QB_completions**: HOME +0.07 (p 0.937, q 0.99); PACE -0.08 (p 0.919, q 0.98); PASS_DEF -0.44 (p 0.537, q 0.97); PASS_TENDENCY +1.33 (p 0.040, q 0.83); PRESSURE -0.58 (p 0.374, q 0.97); QB_EFF +0.25 (p 0.720, q 0.98); ROLE_RECENCY -0.13 (p 0.819, q 0.98); RUSH_DEF -0.81 (p 0.195, q 0.89); SCRIPT +0.53 (p 0.592, q 0.97)
* **QB_ints**: HOME +0.11 (p 0.260, q 0.97); PACE -0.11 (p 0.147, q 0.86); PASS_DEF -0.00 (p 0.994, q 0.99); PASS_TENDENCY -0.12 (p 0.270, q 0.97); PRESSURE -0.03 (p 0.784, q 0.98); QB_EFF -0.07 (p 0.509, q 0.97); ROLE_RECENCY +0.04 (p 0.793, q 0.98); RUSH_DEF +0.09 (p 0.463, q 0.97); SCRIPT +0.05 (p 0.716, q 0.98)
* **QB_pass_td**: HOME -0.10 (p 0.194, q 0.89); PACE -0.06 (p 0.421, q 0.97); PASS_DEF -0.06 (p 0.374, q 0.97); PASS_TENDENCY +0.02 (p 0.793, q 0.98); PRESSURE +0.02 (p 0.837, q 0.98); QB_EFF -0.09 (p 0.226, q 0.96); ROLE_RECENCY -0.03 (p 0.659, q 0.98); RUSH_DEF -0.04 (p 0.579, q 0.97); SCRIPT -0.08 (p 0.254, q 0.97)
* **QB_pass_yards**: HOME +3.50 (p 0.318, q 0.97); PACE +5.31 (p 0.103, q 0.83); PASS_DEF -6.01 (p 0.103, q 0.83); PASS_TENDENCY +5.81 (p 0.155, q 0.86); PRESSURE -3.57 (p 0.338, q 0.97); QB_EFF -2.47 (p 0.485, q 0.97); ROLE_RECENCY +1.12 (p 0.693, q 0.98); RUSH_DEF -4.57 (p 0.180, q 0.89); SCRIPT +5.13 (p 0.107, q 0.83)
* **QB_rush_yards**: HOME +1.84 (p 0.127, q 0.86); PACE +1.88 (p 0.099, q 0.83); PASS_DEF -2.61 (p 0.054, q 0.83); PASS_TENDENCY -0.60 (p 0.638, q 0.98); PRESSURE -2.38 (p 0.036, q 0.83); QB_EFF -0.28 (p 0.833, q 0.98); ROLE_RECENCY -1.44 (p 0.070, q 0.83); RUSH_DEF -2.20 (p 0.090, q 0.83); SCRIPT +0.09 (p 0.948, q 0.99)
* **RB_carries**: HOME +0.06 (p 0.908, q 0.98); PACE -0.14 (p 0.790, q 0.98); PASS_DEF -0.42 (p 0.413, q 0.97); PASS_TENDENCY -0.61 (p 0.088, q 0.83); PRESSURE +0.27 (p 0.638, q 0.98); QB_EFF -0.02 (p 0.964, q 0.99); ROLE_RECENCY -0.05 (p 0.923, q 0.98); RUSH_DEF +0.95 (p 0.031, q 0.83); SCRIPT +0.48 (p 0.446, q 0.97)
* **RB_rec_yards**: HOME +0.46 (p 0.741, q 0.98); PACE -0.74 (p 0.548, q 0.97); PASS_DEF -0.14 (p 0.914, q 0.98); PASS_TENDENCY +1.16 (p 0.434, q 0.97); PRESSURE -1.37 (p 0.293, q 0.97); QB_EFF -0.89 (p 0.510, q 0.97); ROLE_RECENCY -2.72 (p 0.047, q 0.83); RUSH_DEF +0.90 (p 0.468, q 0.97); SCRIPT -0.26 (p 0.852, q 0.98)
* **RB_receptions**: HOME +0.06 (p 0.675, q 0.98); PACE +0.08 (p 0.532, q 0.97); PASS_DEF +0.16 (p 0.280, q 0.97); PASS_TENDENCY +0.05 (p 0.697, q 0.98); PRESSURE -0.11 (p 0.438, q 0.97); QB_EFF +0.11 (p 0.442, q 0.97); ROLE_RECENCY -0.29 (p 0.027, q 0.83); RUSH_DEF -0.01 (p 0.972, q 0.99); SCRIPT +0.08 (p 0.572, q 0.97)
* **RB_rush_yards**: HOME -1.16 (p 0.516, q 0.97); PACE -2.85 (p 0.099, q 0.83); PASS_DEF -0.63 (p 0.680, q 0.98); PASS_TENDENCY -0.45 (p 0.796, q 0.98); PRESSURE +1.18 (p 0.471, q 0.97); QB_EFF +1.57 (p 0.350, q 0.97); ROLE_RECENCY +0.71 (p 0.669, q 0.98); RUSH_DEF +2.83 (p 0.083, q 0.83); SCRIPT +0.22 (p 0.902, q 0.98)
* **TE_rec_yards**: HOME +1.25 (p 0.421, q 0.97); PACE +1.28 (p 0.369, q 0.97); PASS_DEF -2.70 (p 0.135, q 0.86); PASS_TENDENCY +0.64 (p 0.682, q 0.98); PRESSURE -1.62 (p 0.214, q 0.94); QB_EFF +0.98 (p 0.462, q 0.97); ROLE_RECENCY -1.26 (p 0.416, q 0.97); RUSH_DEF -2.82 (p 0.086, q 0.83); SCRIPT +2.18 (p 0.165, q 0.86)
* **TE_receptions**: HOME +0.11 (p 0.414, q 0.97); PACE -0.11 (p 0.389, q 0.97); PASS_DEF -0.12 (p 0.467, q 0.97); PASS_TENDENCY +0.04 (p 0.754, q 0.98); PRESSURE +0.01 (p 0.962, q 0.99); QB_EFF -0.02 (p 0.885, q 0.98); ROLE_RECENCY +0.03 (p 0.795, q 0.98); RUSH_DEF -0.03 (p 0.852, q 0.98); SCRIPT +0.07 (p 0.629, q 0.98)
* **WR_rec_yards**: HOME -0.26 (p 0.819, q 0.98); PACE +2.03 (p 0.071, q 0.83); PASS_DEF +0.35 (p 0.762, q 0.98); PASS_TENDENCY +0.88 (p 0.456, q 0.97); PRESSURE -0.60 (p 0.641, q 0.98); QB_EFF -0.40 (p 0.729, q 0.98); ROLE_RECENCY -0.70 (p 0.613, q 0.98); RUSH_DEF -1.59 (p 0.157, q 0.86); SCRIPT -0.14 (p 0.884, q 0.98)
* **WR_receptions**: HOME -0.01 (p 0.955, q 0.99); PACE +0.06 (p 0.545, q 0.97); PASS_DEF -0.02 (p 0.775, q 0.98); PASS_TENDENCY +0.11 (p 0.269, q 0.97); PRESSURE -0.05 (p 0.564, q 0.97); QB_EFF +0.06 (p 0.475, q 0.97); ROLE_RECENCY -0.15 (p 0.164, q 0.86); RUSH_DEF -0.07 (p 0.395, q 0.97); SCRIPT +0.00 (p 0.985, q 0.99)

## P6. Game script → player volume (β per SD, % of the stat's mean, p; controls for the player's EWMA)

| Stat | Pregame expected script | Pregame expected plays | Realised lead−trail share (post hoc) | Realised team plays (post hoc) |
|---|---|---|---|---|
| QB.attempts | -0.24 (-0.8%, p 0.090) | -0.17 (-0.6%, p 0.267) | -2.41 (-7.8%, p 0.000) | +4.43 (+14.3%, p 0.000) |
| QB.completions | +0.05 (+0.3%, p 0.574) | +0.01 (+0.1%, p 0.884) | -0.85 (-4.3%, p 0.000) | +2.80 (+14.1%, p 0.000) |
| QB.pass_yards | +2.72 (+1.2%, p 0.014) | +2.13 (+1.0%, p 0.073) | -0.30 (-0.1%, p 0.802) | +27.19 (+12.3%, p 0.000) |
| RB.carries | +0.17 (+1.4%, p 0.018) | -0.11 (-0.9%, p 0.091) | +1.64 (+13.2%, p 0.000) | +1.34 (+10.8%, p 0.000) |
| RB.receptions | +0.02 (+1.0%, p 0.252) | -0.02 (-0.9%, p 0.277) | -0.22 (-9.1%, p 0.000) | +0.30 (+12.6%, p 0.000) |
| TE.receptions | +0.09 (+2.5%, p 0.006) | +0.04 (+1.1%, p 0.214) | -0.20 (-5.5%, p 0.000) | +0.57 (+15.8%, p 0.000) |
| WR.rec_yards | +1.04 (+2.0%, p 0.001) | +0.21 (+0.4%, p 0.525) | +1.36 (+2.6%, p 0.000) | +5.54 (+10.7%, p 0.000) |
| WR.receptions | +0.05 (+1.3%, p 0.013) | +0.02 (+0.4%, p 0.456) | -0.06 (-1.4%, p 0.008) | +0.55 (+13.5%, p 0.000) |

## P7. Correlation of out-of-sample residuals within a team-game

* QB_attempts~RB_carries: r = -0.17 (n 3660)
* QB_attempts~WR_receptions: r = +0.39 (n 3754)
* QB_completions~RB_receptions: r = +0.25 (n 3564)
* QB_pass_yards~TE_rec_yards: r = +0.31 (n 3112)
* QB_pass_yards~WR_rec_yards: r = +0.56 (n 3754)
* RB_carries~RB_rush_yards: r = +0.76 (n 3950)
