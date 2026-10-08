# NFL player-prop signal catalog — Football Signal Discovery Wave 1

One row per (prop family × football signal group). Baseline = the best of season-average / EWMA / usage-only for that family. Incremental = out-of-sample MAE gain from including the group (walk-forward 2018–2026, game-cluster CI). Line residual = slope of (actual − Kalshi ladder median) on the group's lead feature. Economics are per family (pre-registered natural-rung rule), not per group. RETROSPECTIVE; Kalshi 2025 archive previously mined.

| Signal ID | Position | Stat | Group | n | Baseline MAE (best) | Incremental MAE gain [95%] (q) | Line residual β/SD (q) | Family economics (model rule) | Stability (seasons +) | Concentration (family gain w/o top-10) | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NFL-PROP-QB_attempts-HOME | QB | attempts | HOME | 3995 | 7.78 (USAGE) | -0.004 [-0.014, +0.007] (0.67) | +0.70 (0.97) | n 18, ROI -8.6% | 4/9 | -0.014 | **REJECTED** |
| NFL-PROP-QB_attempts-IX_PACE_x_SCRIPT | QB | attempts | IX_PACE_x_SCRIPT | 3995 | 7.78 (USAGE) | -0.000 [-0.001, +0.000] (0.73) | — | n 18, ROI -8.6% | 4/9 | -0.014 | **REJECTED** |
| NFL-PROP-QB_attempts-PACE | QB | attempts | PACE | 3995 | 7.78 (USAGE) | -0.004 [-0.021, +0.012] (0.76) | -0.33 (0.98) | n 18, ROI -8.6% | 3/9 | -0.014 | **REJECTED** |
| NFL-PROP-QB_attempts-PASS_DEF | QB | attempts | PASS_DEF | 3995 | 7.78 (USAGE) | -0.005 [-0.012, +0.003] (0.44) | +1.70 (0.86) | n 18, ROI -8.6% | 3/9 | -0.014 | **REJECTED** |
| NFL-PROP-QB_attempts-PASS_TENDENCY | QB | attempts | PASS_TENDENCY | 3995 | 7.78 (USAGE) | +0.006 [-0.026, +0.038] (0.84) | +1.79 (0.83) | n 18, ROI -8.6% | 6/9 | -0.014 | **REJECTED** |
| NFL-PROP-QB_attempts-PRESSURE | QB | attempts | PRESSURE | 3995 | 7.78 (USAGE) | -0.016 [-0.033, -0.001] (0.14) | -0.37 (0.98) | n 18, ROI -8.6% | 2/9 | -0.014 | **REJECTED** |
| NFL-PROP-QB_attempts-QB_EFF | QB | attempts | QB_EFF | 3995 | 7.78 (USAGE) | +0.007 [-0.007, +0.022] (0.53) | -0.16 (0.98) | n 18, ROI -8.6% | 6/9 | -0.014 | **REJECTED** |
| NFL-PROP-QB_attempts-ROLE_RECENCY | QB | attempts | ROLE_RECENCY | 3995 | 7.78 (USAGE) | +0.109 [+0.057, +0.163] (0.00) | +0.23 (0.98) | n 18, ROI -8.6% | 6/9 | -0.014 | **FOOTBALL_VALIDATED** |
| NFL-PROP-QB_attempts-RUSH_DEF | QB | attempts | RUSH_DEF | 3995 | 7.78 (USAGE) | +0.001 [-0.019, +0.022] (0.98) | -0.57 (0.97) | n 18, ROI -8.6% | 4/9 | -0.014 | **REJECTED** |
| NFL-PROP-QB_attempts-SCRIPT | QB | attempts | SCRIPT | 3995 | 7.78 (USAGE) | +0.005 [-0.014, +0.023] (0.76) | +0.64 (0.98) | n 18, ROI -8.6% | 5/9 | -0.014 | **REJECTED** |
| NFL-PROP-QB_completions-HOME | QB | completions | HOME | 3995 | 5.36 (USAGE) | -0.001 [-0.016, +0.013] (0.93) | +0.07 (0.99) | n 23, ROI +2.5% | 4/9 | -0.036 | **REJECTED** |
| NFL-PROP-QB_completions-PACE | QB | completions | PACE | 3995 | 5.36 (USAGE) | -0.008 [-0.022, +0.006] (0.44) | -0.08 (0.98) | n 23, ROI +2.5% | 2/9 | -0.036 | **REJECTED** |
| NFL-PROP-QB_completions-PASS_DEF | QB | completions | PASS_DEF | 3995 | 5.36 (USAGE) | -0.007 [-0.018, +0.003] (0.38) | -0.44 (0.97) | n 23, ROI +2.5% | 3/9 | -0.036 | **REJECTED** |
| NFL-PROP-QB_completions-PASS_TENDENCY | QB | completions | PASS_TENDENCY | 3995 | 5.36 (USAGE) | +0.011 [-0.009, +0.032] (0.48) | +1.33 (0.83) | n 23, ROI +2.5% | 6/9 | -0.036 | **REJECTED** |
| NFL-PROP-QB_completions-PRESSURE | QB | completions | PRESSURE | 3995 | 5.36 (USAGE) | -0.005 [-0.016, +0.006] (0.58) | -0.58 (0.97) | n 23, ROI +2.5% | 4/9 | -0.036 | **REJECTED** |
| NFL-PROP-QB_completions-QB_EFF | QB | completions | QB_EFF | 3995 | 5.36 (USAGE) | +0.000 [-0.008, +0.009] (0.99) | +0.25 (0.98) | n 23, ROI +2.5% | 5/9 | -0.036 | **REJECTED** |
| NFL-PROP-QB_completions-ROLE_RECENCY | QB | completions | ROLE_RECENCY | 3995 | 5.36 (USAGE) | +0.079 [+0.045, +0.114] (0.00) | -0.13 (0.98) | n 23, ROI +2.5% | 6/9 | -0.036 | **FOOTBALL_VALIDATED** |
| NFL-PROP-QB_completions-RUSH_DEF | QB | completions | RUSH_DEF | 3995 | 5.36 (USAGE) | +0.004 [-0.011, +0.018] (0.76) | -0.81 (0.89) | n 23, ROI +2.5% | 5/9 | -0.036 | **REJECTED** |
| NFL-PROP-QB_completions-SCRIPT | QB | completions | SCRIPT | 3995 | 5.36 (USAGE) | +0.002 [-0.007, +0.010] (0.84) | +0.53 (0.97) | n 23, ROI +2.5% | 5/9 | -0.036 | **REJECTED** |
| NFL-PROP-QB_ints-HOME | QB | ints | HOME | 3995 | 0.71 (USAGE) | -0.000 [-0.001, +0.000] (0.67) | +0.11 (0.97) | n 39, ROI +8.5% | 3/9 | -0.004 | **REJECTED** |
| NFL-PROP-QB_ints-PACE | QB | ints | PACE | 3995 | 0.71 (USAGE) | +0.001 [-0.000, +0.001] (0.35) | -0.11 (0.86) | n 39, ROI +8.5% | 7/9 | -0.004 | **REJECTED** |
| NFL-PROP-QB_ints-PASS_DEF | QB | ints | PASS_DEF | 3995 | 0.71 (USAGE) | -0.000 [-0.001, +0.001] (0.76) | -0.00 (0.99) | n 39, ROI +8.5% | 4/9 | -0.004 | **REJECTED** |
| NFL-PROP-QB_ints-PASS_TENDENCY | QB | ints | PASS_TENDENCY | 3995 | 0.71 (USAGE) | -0.001 [-0.002, +0.000] (0.38) | -0.12 (0.97) | n 39, ROI +8.5% | 4/9 | -0.004 | **REJECTED** |
| NFL-PROP-QB_ints-PRESSURE | QB | ints | PRESSURE | 3995 | 0.71 (USAGE) | -0.001 [-0.002, -0.000] (0.11) | -0.03 (0.98) | n 39, ROI +8.5% | 1/9 | -0.004 | **REJECTED** |
| NFL-PROP-QB_ints-QB_EFF | QB | ints | QB_EFF | 3995 | 0.71 (USAGE) | -0.000 [-0.001, +0.001] (0.93) | -0.07 (0.97) | n 39, ROI +8.5% | 2/9 | -0.004 | **REJECTED** |
| NFL-PROP-QB_ints-ROLE_RECENCY | QB | ints | ROLE_RECENCY | 3995 | 0.71 (USAGE) | +0.001 [-0.002, +0.003] (0.65) | +0.04 (0.98) | n 39, ROI +8.5% | 7/9 | -0.004 | **REJECTED** |
| NFL-PROP-QB_ints-RUSH_DEF | QB | ints | RUSH_DEF | 3995 | 0.71 (USAGE) | +0.002 [+0.001, +0.004] (0.04) | +0.09 (0.97) | n 39, ROI +8.5% | 6/9 | -0.004 | **FOOTBALL_VALIDATED** |
| NFL-PROP-QB_ints-SCRIPT | QB | ints | SCRIPT | 3995 | 0.71 (USAGE) | +0.000 [-0.001, +0.002] (0.84) | +0.05 (0.98) | n 39, ROI +8.5% | 5/9 | -0.004 | **REJECTED** |
| NFL-PROP-QB_pass_td-HOME | QB | pass_td | HOME | 3995 | 0.92 (USAGE) | -0.002 [-0.003, +0.000] (0.25) | -0.10 (0.89) | n 211, ROI -6.1% | 4/9 | -0.009 | **REJECTED** |
| NFL-PROP-QB_pass_td-PACE | QB | pass_td | PACE | 3995 | 0.92 (USAGE) | -0.002 [-0.003, -0.000] (0.11) | -0.06 (0.97) | n 211, ROI -6.1% | 4/9 | -0.009 | **REJECTED** |
| NFL-PROP-QB_pass_td-PASS_DEF | QB | pass_td | PASS_DEF | 3995 | 0.92 (USAGE) | -0.002 [-0.004, +0.000] (0.25) | -0.06 (0.97) | n 211, ROI -6.1% | 4/9 | -0.009 | **REJECTED** |
| NFL-PROP-QB_pass_td-PASS_TENDENCY | QB | pass_td | PASS_TENDENCY | 3995 | 0.92 (USAGE) | -0.002 [-0.004, +0.000] (0.31) | +0.02 (0.98) | n 211, ROI -6.1% | 3/9 | -0.009 | **REJECTED** |
| NFL-PROP-QB_pass_td-PRESSURE | QB | pass_td | PRESSURE | 3995 | 0.92 (USAGE) | -0.001 [-0.003, +0.000] (0.30) | +0.02 (0.98) | n 211, ROI -6.1% | 4/9 | -0.009 | **REJECTED** |
| NFL-PROP-QB_pass_td-QB_EFF | QB | pass_td | QB_EFF | 3995 | 0.92 (USAGE) | -0.002 [-0.003, -0.001] (0.03) | -0.09 (0.96) | n 211, ROI -6.1% | 2/9 | -0.009 | **REJECTED** |
| NFL-PROP-QB_pass_td-ROLE_RECENCY | QB | pass_td | ROLE_RECENCY | 3995 | 0.92 (USAGE) | +0.002 [-0.001, +0.005] (0.44) | -0.03 (0.98) | n 211, ROI -6.1% | 4/9 | -0.009 | **REJECTED** |
| NFL-PROP-QB_pass_td-RUSH_DEF | QB | pass_td | RUSH_DEF | 3995 | 0.92 (USAGE) | -0.000 [-0.001, +0.001] (0.99) | -0.04 (0.97) | n 211, ROI -6.1% | 5/9 | -0.009 | **REJECTED** |
| NFL-PROP-QB_pass_td-SCRIPT | QB | pass_td | SCRIPT | 3995 | 0.92 (USAGE) | -0.000 [-0.001, +0.000] (0.40) | -0.08 (0.97) | n 211, ROI -6.1% | 3/9 | -0.009 | **REJECTED** |
| NFL-PROP-QB_pass_yards-HOME | QB | pass_yards | HOME | 3995 | 65.55 (USAGE) | -0.064 [-0.254, +0.119] (0.70) | +3.50 (0.97) | n 85, ROI -18.4% | 3/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_pass_yards-IX_PACE_x_PASSDEF | QB | pass_yards | IX_PACE_x_PASSDEF | 3995 | 65.55 (USAGE) | +0.005 [-0.019, +0.028] (0.83) | — | n 85, ROI -18.4% | 6/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_pass_yards-IX_PRESSURE_x_PASSDEF | QB | pass_yards | IX_PRESSURE_x_PASSDEF | 3995 | 65.55 (USAGE) | +0.026 [-0.130, +0.182] (0.84) | — | n 85, ROI -18.4% | 6/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_pass_yards-PACE | QB | pass_yards | PACE | 3995 | 65.55 (USAGE) | -0.035 [-0.190, +0.126] (0.81) | +5.31 (0.83) | n 85, ROI -18.4% | 3/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_pass_yards-PASS_DEF | QB | pass_yards | PASS_DEF | 3995 | 65.55 (USAGE) | -0.028 [-0.256, +0.206] (0.89) | -6.01 (0.83) | n 85, ROI -18.4% | 5/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_pass_yards-PASS_TENDENCY | QB | pass_yards | PASS_TENDENCY | 3995 | 65.55 (USAGE) | +0.010 [-0.188, +0.218] (0.97) | +5.81 (0.86) | n 85, ROI -18.4% | 5/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_pass_yards-PRESSURE | QB | pass_yards | PRESSURE | 3995 | 65.55 (USAGE) | -0.048 [-0.236, +0.144] (0.76) | -3.57 (0.97) | n 85, ROI -18.4% | 4/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_pass_yards-QB_EFF | QB | pass_yards | QB_EFF | 3995 | 65.55 (USAGE) | -0.100 [-0.195, -0.007] (0.11) | -2.47 (0.97) | n 85, ROI -18.4% | 4/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_pass_yards-ROLE_RECENCY | QB | pass_yards | ROLE_RECENCY | 3995 | 65.55 (USAGE) | +0.946 [+0.533, +1.341] (0.00) | +1.12 (0.98) | n 85, ROI -18.4% | 8/9 | -0.088 | **FOOTBALL_VALIDATED** |
| NFL-PROP-QB_pass_yards-RUSH_DEF | QB | pass_yards | RUSH_DEF | 3995 | 65.55 (USAGE) | +0.088 [-0.110, +0.285] (0.57) | -4.57 (0.89) | n 85, ROI -18.4% | 6/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_pass_yards-SCRIPT | QB | pass_yards | SCRIPT | 3995 | 65.55 (USAGE) | -0.082 [-0.218, +0.050] (0.40) | +5.13 (0.83) | n 85, ROI -18.4% | 2/9 | -0.088 | **REJECTED** |
| NFL-PROP-QB_rush_yards-HOME | QB | rush_yards | HOME | 3995 | 11.45 (EWMA) | -0.007 [-0.022, +0.008] (0.58) | +1.84 (0.86) | n 116, ROI +1.7% | 6/9 | -0.575 | **REJECTED** |
| NFL-PROP-QB_rush_yards-PACE | QB | rush_yards | PACE | 3995 | 11.45 (EWMA) | -0.056 [-0.074, -0.040] (0.00) | +1.88 (0.83) | n 116, ROI +1.7% | 1/9 | -0.575 | **REJECTED** |
| NFL-PROP-QB_rush_yards-PASS_DEF | QB | rush_yards | PASS_DEF | 3995 | 11.45 (EWMA) | -0.063 [-0.090, -0.036] (0.00) | -2.61 (0.83) | n 116, ROI +1.7% | 0/9 | -0.575 | **REJECTED** |
| NFL-PROP-QB_rush_yards-PASS_TENDENCY | QB | rush_yards | PASS_TENDENCY | 3995 | 11.45 (EWMA) | -0.014 [-0.026, -0.002] (0.07) | -0.60 (0.98) | n 116, ROI +1.7% | 4/9 | -0.575 | **REJECTED** |
| NFL-PROP-QB_rush_yards-PRESSURE | QB | rush_yards | PRESSURE | 3995 | 11.45 (EWMA) | -0.069 [-0.093, -0.045] (0.00) | -2.38 (0.83) | n 116, ROI +1.7% | 3/9 | -0.575 | **REJECTED** |
| NFL-PROP-QB_rush_yards-QB_EFF | QB | rush_yards | QB_EFF | 3995 | 11.45 (EWMA) | -0.013 [-0.024, -0.002] (0.05) | -0.28 (0.98) | n 116, ROI +1.7% | 5/9 | -0.575 | **REJECTED** |
| NFL-PROP-QB_rush_yards-ROLE_RECENCY | QB | rush_yards | ROLE_RECENCY | 3995 | 11.45 (EWMA) | +0.010 [-0.048, +0.067] (0.84) | -1.44 (0.83) | n 116, ROI +1.7% | 5/9 | -0.575 | **REJECTED** |
| NFL-PROP-QB_rush_yards-RUSH_DEF | QB | rush_yards | RUSH_DEF | 3995 | 11.45 (EWMA) | +0.047 [+0.024, +0.070] (0.00) | -2.20 (0.83) | n 116, ROI +1.7% | 7/9 | -0.575 | **FOOTBALL_VALIDATED** |
| NFL-PROP-QB_rush_yards-SCRIPT | QB | rush_yards | SCRIPT | 3995 | 11.45 (EWMA) | -0.027 [-0.042, -0.011] (0.00) | +0.09 (0.99) | n 116, ROI +1.7% | 2/9 | -0.575 | **REJECTED** |
| NFL-PROP-RB_carries-HOME | RB | carries | HOME | 6709 | 4.40 (SEASON_AVG) | +0.001 [-0.001, +0.003] (0.38) | +0.06 (0.98) | n 51, ROI +1.3% | 6/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_carries-IX_SHARE_x_RUSHDEF | RB | carries | IX_SHARE_x_RUSHDEF | 6709 | 4.40 (SEASON_AVG) | -0.000 [-0.001, +0.001] (0.99) | — | n 51, ROI +1.3% | 4/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_carries-IX_SHARE_x_SCRIPT | RB | carries | IX_SHARE_x_SCRIPT | 6709 | 4.40 (SEASON_AVG) | -0.000 [-0.001, +0.000] (0.63) | — | n 51, ROI +1.3% | 4/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_carries-PACE | RB | carries | PACE | 6709 | 4.40 (SEASON_AVG) | +0.005 [-0.003, +0.013] (0.35) | -0.14 (0.98) | n 51, ROI +1.3% | 6/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_carries-PASS_DEF | RB | carries | PASS_DEF | 6709 | 4.40 (SEASON_AVG) | +0.008 [+0.001, +0.016] (0.13) | -0.42 (0.97) | n 51, ROI +1.3% | 5/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_carries-PASS_TENDENCY | RB | carries | PASS_TENDENCY | 6709 | 4.40 (SEASON_AVG) | +0.010 [-0.004, +0.024] (0.32) | -0.61 (0.83) | n 51, ROI +1.3% | 6/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_carries-PRESSURE | RB | carries | PRESSURE | 6709 | 4.40 (SEASON_AVG) | -0.004 [-0.009, +0.002] (0.39) | +0.27 (0.98) | n 51, ROI +1.3% | 2/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_carries-QB_EFF | RB | carries | QB_EFF | 6709 | 4.40 (SEASON_AVG) | +0.002 [-0.003, +0.008] (0.57) | -0.02 (0.99) | n 51, ROI +1.3% | 5/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_carries-ROLE_RECENCY | RB | carries | ROLE_RECENCY | 6709 | 4.40 (SEASON_AVG) | +0.217 [+0.180, +0.254] (0.00) | -0.05 (0.98) | n 51, ROI +1.3% | 9/9 | +0.223 | **FOOTBALL_VALIDATED** |
| NFL-PROP-RB_carries-RUSH_DEF | RB | carries | RUSH_DEF | 6709 | 4.40 (SEASON_AVG) | +0.002 [-0.001, +0.004] (0.44) | +0.95 (0.83) | n 51, ROI +1.3% | 5/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_carries-SCRIPT | RB | carries | SCRIPT | 6709 | 4.40 (SEASON_AVG) | +0.007 [-0.001, +0.014] (0.24) | +0.48 (0.97) | n 51, ROI +1.3% | 8/9 | +0.223 | **REJECTED** |
| NFL-PROP-RB_rec_yards-HOME | RB | rec_yards | HOME | 6128 | 14.15 (USAGE) | -0.004 [-0.012, +0.004] (0.57) | +0.46 (0.98) | n 186, ROI -0.4% | 4/9 | +0.181 | **REJECTED** |
| NFL-PROP-RB_rec_yards-PACE | RB | rec_yards | PACE | 6128 | 14.15 (USAGE) | +0.002 [-0.009, +0.012] (0.84) | -0.74 (0.97) | n 186, ROI -0.4% | 5/9 | +0.181 | **REJECTED** |
| NFL-PROP-RB_rec_yards-PASS_DEF | RB | rec_yards | PASS_DEF | 6128 | 14.15 (USAGE) | +0.048 [+0.015, +0.080] (0.01) | -0.14 (0.98) | n 186, ROI -0.4% | 5/9 | +0.181 | **DISCOVERY_ONLY** |
| NFL-PROP-RB_rec_yards-PASS_TENDENCY | RB | rec_yards | PASS_TENDENCY | 6128 | 14.15 (USAGE) | -0.022 [-0.049, +0.005] (0.25) | +1.16 (0.97) | n 186, ROI -0.4% | 2/9 | +0.181 | **REJECTED** |
| NFL-PROP-RB_rec_yards-PRESSURE | RB | rec_yards | PRESSURE | 6128 | 14.15 (USAGE) | -0.044 [-0.061, -0.026] (0.00) | -1.37 (0.97) | n 186, ROI -0.4% | 2/9 | +0.181 | **REJECTED** |
| NFL-PROP-RB_rec_yards-QB_EFF | RB | rec_yards | QB_EFF | 6128 | 14.15 (USAGE) | +0.033 [+0.019, +0.047] (0.00) | -0.89 (0.97) | n 186, ROI -0.4% | 6/9 | +0.181 | **FOOTBALL_VALIDATED** |
| NFL-PROP-RB_rec_yards-ROLE_RECENCY | RB | rec_yards | ROLE_RECENCY | 6128 | 14.15 (USAGE) | +0.152 [+0.070, +0.228] (0.00) | -2.72 (0.83) | n 186, ROI -0.4% | 8/9 | +0.181 | **FOOTBALL_VALIDATED** |
| NFL-PROP-RB_rec_yards-RUSH_DEF | RB | rec_yards | RUSH_DEF | 6128 | 14.15 (USAGE) | +0.017 [+0.007, +0.027] (0.00) | +0.90 (0.97) | n 186, ROI -0.4% | 7/9 | +0.181 | **FOOTBALL_VALIDATED** |
| NFL-PROP-RB_rec_yards-SCRIPT | RB | rec_yards | SCRIPT | 6128 | 14.15 (USAGE) | -0.017 [-0.031, -0.003] (0.05) | -0.26 (0.98) | n 186, ROI -0.4% | 1/9 | +0.181 | **REJECTED** |
| NFL-PROP-RB_receptions-HOME | RB | receptions | HOME | 6128 | 1.47 (USAGE) | -0.000 [-0.001, +0.000] (0.31) | +0.06 (0.98) | n 190, ROI +14.9% | 3/9 | -0.080 | **REJECTED** |
| NFL-PROP-RB_receptions-IX_SHARE_x_PRESSURE | RB | receptions | IX_SHARE_x_PRESSURE | 6128 | 1.47 (USAGE) | +0.001 [+0.001, +0.002] (0.01) | — | n 190, ROI +14.9% | 6/9 | -0.080 | **FOOTBALL_VALIDATED** |
| NFL-PROP-RB_receptions-IX_SHARE_x_SCRIPT | RB | receptions | IX_SHARE_x_SCRIPT | 6128 | 1.47 (USAGE) | +0.004 [+0.002, +0.006] (0.00) | — | n 190, ROI +14.9% | 5/9 | -0.080 | **DISCOVERY_ONLY** |
| NFL-PROP-RB_receptions-PACE | RB | receptions | PACE | 6128 | 1.47 (USAGE) | +0.001 [-0.002, +0.003] (0.70) | +0.08 (0.97) | n 190, ROI +14.9% | 3/9 | -0.080 | **REJECTED** |
| NFL-PROP-RB_receptions-PASS_DEF | RB | receptions | PASS_DEF | 6128 | 1.47 (USAGE) | +0.005 [+0.002, +0.008] (0.01) | +0.16 (0.97) | n 190, ROI +14.9% | 6/9 | -0.080 | **FOOTBALL_VALIDATED** |
| NFL-PROP-RB_receptions-PASS_TENDENCY | RB | receptions | PASS_TENDENCY | 6128 | 1.47 (USAGE) | -0.006 [-0.009, -0.002] (0.01) | +0.05 (0.98) | n 190, ROI +14.9% | 4/9 | -0.080 | **REJECTED** |
| NFL-PROP-RB_receptions-PRESSURE | RB | receptions | PRESSURE | 6128 | 1.47 (USAGE) | -0.005 [-0.007, -0.003] (0.00) | -0.11 (0.97) | n 190, ROI +14.9% | 4/9 | -0.080 | **REJECTED** |
| NFL-PROP-RB_receptions-QB_EFF | RB | receptions | QB_EFF | 6128 | 1.47 (USAGE) | +0.002 [+0.000, +0.003] (0.09) | +0.11 (0.97) | n 190, ROI +14.9% | 6/9 | -0.080 | **DISCOVERY_ONLY** |
| NFL-PROP-RB_receptions-ROLE_RECENCY | RB | receptions | ROLE_RECENCY | 6128 | 1.47 (USAGE) | +0.006 [-0.005, +0.017] (0.44) | -0.29 (0.83) | n 190, ROI +14.9% | 8/9 | -0.080 | **REJECTED** |
| NFL-PROP-RB_receptions-RUSH_DEF | RB | receptions | RUSH_DEF | 6128 | 1.47 (USAGE) | +0.001 [-0.001, +0.003] (0.60) | -0.01 (0.99) | n 190, ROI +14.9% | 5/9 | -0.080 | **REJECTED** |
| NFL-PROP-RB_receptions-SCRIPT | RB | receptions | SCRIPT | 6128 | 1.47 (USAGE) | +0.008 [+0.003, +0.012] (0.00) | +0.08 (0.97) | n 190, ROI +14.9% | 3/9 | -0.080 | **DISCOVERY_ONLY** |
| NFL-PROP-RB_rush_yards-HOME | RB | rush_yards | HOME | 6709 | 25.74 (EWMA) | -0.016 [-0.030, -0.002] (0.08) | -1.16 (0.97) | n 251, ROI -12.4% | 2/9 | +0.411 | **REJECTED** |
| NFL-PROP-RB_rush_yards-IX_SHARE_x_RUSHDEF | RB | rush_yards | IX_SHARE_x_RUSHDEF | 6709 | 25.74 (EWMA) | +0.000 [-0.019, +0.019] (0.99) | — | n 251, ROI -12.4% | 4/9 | +0.411 | **REJECTED** |
| NFL-PROP-RB_rush_yards-IX_SHARE_x_SCRIPT | RB | rush_yards | IX_SHARE_x_SCRIPT | 6709 | 25.74 (EWMA) | -0.004 [-0.010, +0.003] (0.51) | — | n 251, ROI -12.4% | 5/9 | +0.411 | **REJECTED** |
| NFL-PROP-RB_rush_yards-PACE | RB | rush_yards | PACE | 6709 | 25.74 (EWMA) | -0.021 [-0.068, +0.026] (0.58) | -2.85 (0.83) | n 251, ROI -12.4% | 5/9 | +0.411 | **REJECTED** |
| NFL-PROP-RB_rush_yards-PASS_DEF | RB | rush_yards | PASS_DEF | 6709 | 25.74 (EWMA) | +0.027 [-0.013, +0.071] (0.40) | -0.63 (0.98) | n 251, ROI -12.4% | 5/9 | +0.411 | **REJECTED** |
| NFL-PROP-RB_rush_yards-PASS_TENDENCY | RB | rush_yards | PASS_TENDENCY | 6709 | 25.74 (EWMA) | +0.040 [-0.032, +0.109] (0.44) | -0.45 (0.98) | n 251, ROI -12.4% | 8/9 | +0.411 | **REJECTED** |
| NFL-PROP-RB_rush_yards-PRESSURE | RB | rush_yards | PRESSURE | 6709 | 25.74 (EWMA) | +0.047 [+0.020, +0.076] (0.00) | +1.18 (0.97) | n 251, ROI -12.4% | 6/9 | +0.411 | **FOOTBALL_VALIDATED** |
| NFL-PROP-RB_rush_yards-QB_EFF | RB | rush_yards | QB_EFF | 6709 | 25.74 (EWMA) | +0.006 [-0.008, +0.021] (0.63) | +1.57 (0.97) | n 251, ROI -12.4% | 5/9 | +0.411 | **REJECTED** |
| NFL-PROP-RB_rush_yards-ROLE_RECENCY | RB | rush_yards | ROLE_RECENCY | 6709 | 25.74 (EWMA) | +0.566 [+0.383, +0.739] (0.00) | +0.71 (0.98) | n 251, ROI -12.4% | 8/9 | +0.411 | **FOOTBALL_VALIDATED** |
| NFL-PROP-RB_rush_yards-RUSH_DEF | RB | rush_yards | RUSH_DEF | 6709 | 25.74 (EWMA) | +0.065 [+0.031, +0.095] (0.00) | +2.83 (0.83) | n 251, ROI -12.4% | 6/9 | +0.411 | **FOOTBALL_VALIDATED** |
| NFL-PROP-RB_rush_yards-SCRIPT | RB | rush_yards | SCRIPT | 6709 | 25.74 (EWMA) | +0.017 [-0.012, +0.046] (0.44) | +0.22 (0.98) | n 251, ROI -12.4% | 6/9 | +0.411 | **REJECTED** |
| NFL-PROP-TE_rec_yards-HOME | TE | rec_yards | HOME | 4083 | 21.00 (EWMA) | -0.019 [-0.043, +0.005] (0.31) | +1.25 (0.97) | n 207, ROI -1.0% | 3/9 | -0.017 | **REJECTED** |
| NFL-PROP-TE_rec_yards-IX_SHARE_x_PASSDEF | TE | rec_yards | IX_SHARE_x_PASSDEF | 4083 | 21.00 (EWMA) | -0.018 [-0.046, +0.011] (0.44) | — | n 207, ROI -1.0% | 5/9 | -0.017 | **REJECTED** |
| NFL-PROP-TE_rec_yards-PACE | TE | rec_yards | PACE | 4083 | 21.00 (EWMA) | +0.017 [-0.019, +0.051] (0.53) | +1.28 (0.97) | n 207, ROI -1.0% | 7/9 | -0.017 | **REJECTED** |
| NFL-PROP-TE_rec_yards-PASS_DEF | TE | rec_yards | PASS_DEF | 4083 | 21.00 (EWMA) | -0.026 [-0.066, +0.013] (0.40) | -2.70 (0.86) | n 207, ROI -1.0% | 3/9 | -0.017 | **REJECTED** |
| NFL-PROP-TE_rec_yards-PASS_TENDENCY | TE | rec_yards | PASS_TENDENCY | 4083 | 21.00 (EWMA) | +0.000 [-0.022, +0.022] (0.99) | +0.64 (0.98) | n 207, ROI -1.0% | 6/9 | -0.017 | **REJECTED** |
| NFL-PROP-TE_rec_yards-PRESSURE | TE | rec_yards | PRESSURE | 4083 | 21.00 (EWMA) | +0.017 [-0.005, +0.041] (0.34) | -1.62 (0.94) | n 207, ROI -1.0% | 6/9 | -0.017 | **REJECTED** |
| NFL-PROP-TE_rec_yards-QB_EFF | TE | rec_yards | QB_EFF | 4083 | 21.00 (EWMA) | -0.009 [-0.059, +0.039] (0.84) | +0.98 (0.97) | n 207, ROI -1.0% | 4/9 | -0.017 | **REJECTED** |
| NFL-PROP-TE_rec_yards-ROLE_RECENCY | TE | rec_yards | ROLE_RECENCY | 4083 | 21.00 (EWMA) | +0.520 [+0.302, +0.765] (0.00) | -1.26 (0.97) | n 207, ROI -1.0% | 8/9 | -0.017 | **FOOTBALL_VALIDATED** |
| NFL-PROP-TE_rec_yards-RUSH_DEF | TE | rec_yards | RUSH_DEF | 4083 | 21.00 (EWMA) | +0.069 [+0.022, +0.116] (0.02) | -2.82 (0.83) | n 207, ROI -1.0% | 7/9 | -0.017 | **FOOTBALL_VALIDATED** |
| NFL-PROP-TE_rec_yards-SCRIPT | TE | rec_yards | SCRIPT | 4083 | 21.00 (EWMA) | -0.024 [-0.045, -0.005] (0.06) | +2.18 (0.86) | n 207, ROI -1.0% | 0/9 | -0.017 | **REJECTED** |
| NFL-PROP-TE_receptions-HOME | TE | receptions | HOME | 4083 | 1.65 (USAGE) | -0.000 [-0.001, +0.001] (0.76) | +0.11 (0.97) | n 210, ROI +0.4% | 6/9 | -0.022 | **REJECTED** |
| NFL-PROP-TE_receptions-IX_SHARE_x_PASSDEF | TE | receptions | IX_SHARE_x_PASSDEF | 4083 | 1.65 (USAGE) | -0.000 [-0.002, +0.001] (0.76) | — | n 210, ROI +0.4% | 2/9 | -0.022 | **REJECTED** |
| NFL-PROP-TE_receptions-PACE | TE | receptions | PACE | 4083 | 1.65 (USAGE) | -0.002 [-0.005, +0.001] (0.44) | -0.11 (0.97) | n 210, ROI +0.4% | 5/9 | -0.022 | **REJECTED** |
| NFL-PROP-TE_receptions-PASS_DEF | TE | receptions | PASS_DEF | 4083 | 1.65 (USAGE) | -0.001 [-0.004, +0.001] (0.57) | -0.12 (0.97) | n 210, ROI +0.4% | 4/9 | -0.022 | **REJECTED** |
| NFL-PROP-TE_receptions-PASS_TENDENCY | TE | receptions | PASS_TENDENCY | 4083 | 1.65 (USAGE) | -0.000 [-0.002, +0.002] (0.89) | +0.04 (0.98) | n 210, ROI +0.4% | 5/9 | -0.022 | **REJECTED** |
| NFL-PROP-TE_receptions-PRESSURE | TE | receptions | PRESSURE | 4083 | 1.65 (USAGE) | -0.000 [-0.003, +0.002] (0.97) | +0.01 (0.99) | n 210, ROI +0.4% | 4/9 | -0.022 | **REJECTED** |
| NFL-PROP-TE_receptions-QB_EFF | TE | receptions | QB_EFF | 4083 | 1.65 (USAGE) | -0.000 [-0.004, +0.003] (0.89) | -0.02 (0.98) | n 210, ROI +0.4% | 6/9 | -0.022 | **REJECTED** |
| NFL-PROP-TE_receptions-ROLE_RECENCY | TE | receptions | ROLE_RECENCY | 4083 | 1.65 (USAGE) | +0.034 [+0.015, +0.054] (0.00) | +0.03 (0.98) | n 210, ROI +0.4% | 7/9 | -0.022 | **FOOTBALL_VALIDATED** |
| NFL-PROP-TE_receptions-RUSH_DEF | TE | receptions | RUSH_DEF | 4083 | 1.65 (USAGE) | +0.001 [-0.003, +0.004] (0.76) | -0.03 (0.98) | n 210, ROI +0.4% | 6/9 | -0.022 | **REJECTED** |
| NFL-PROP-TE_receptions-SCRIPT | TE | receptions | SCRIPT | 4083 | 1.65 (USAGE) | -0.002 [-0.003, -0.000] (0.10) | +0.07 (0.98) | n 210, ROI +0.4% | 0/9 | -0.022 | **REJECTED** |
| NFL-PROP-WR_rec_yards-HOME | WR | rec_yards | HOME | 10111 | 27.69 (USAGE) | -0.013 [-0.025, -0.002] (0.08) | -0.26 (0.98) | n 438, ROI -7.4% | 4/9 | +0.498 | **REJECTED** |
| NFL-PROP-WR_rec_yards-IX_SHARE_x_PASSDEF | WR | rec_yards | IX_SHARE_x_PASSDEF | 10111 | 27.69 (USAGE) | -0.009 [-0.018, +0.001] (0.20) | — | n 438, ROI -7.4% | 5/9 | +0.498 | **REJECTED** |
| NFL-PROP-WR_rec_yards-IX_SHARE_x_QBEFF | WR | rec_yards | IX_SHARE_x_QBEFF | 10111 | 27.69 (USAGE) | -0.019 [-0.041, +0.004] (0.28) | — | n 438, ROI -7.4% | 3/9 | +0.498 | **REJECTED** |
| NFL-PROP-WR_rec_yards-PACE | WR | rec_yards | PACE | 10111 | 27.69 (USAGE) | +0.026 [+0.001, +0.051] (0.11) | +2.03 (0.83) | n 438, ROI -7.4% | 4/9 | +0.498 | **REJECTED** |
| NFL-PROP-WR_rec_yards-PASS_DEF | WR | rec_yards | PASS_DEF | 10111 | 27.69 (USAGE) | +0.000 [-0.013, +0.014] (0.99) | +0.35 (0.98) | n 438, ROI -7.4% | 4/9 | +0.498 | **REJECTED** |
| NFL-PROP-WR_rec_yards-PASS_TENDENCY | WR | rec_yards | PASS_TENDENCY | 10111 | 27.69 (USAGE) | -0.018 [-0.030, -0.006] (0.01) | +0.88 (0.97) | n 438, ROI -7.4% | 5/9 | +0.498 | **REJECTED** |
| NFL-PROP-WR_rec_yards-PRESSURE | WR | rec_yards | PRESSURE | 10111 | 27.69 (USAGE) | -0.041 [-0.061, -0.020] (0.00) | -0.60 (0.98) | n 438, ROI -7.4% | 3/9 | +0.498 | **REJECTED** |
| NFL-PROP-WR_rec_yards-QB_EFF | WR | rec_yards | QB_EFF | 10111 | 27.69 (USAGE) | +0.016 [-0.013, +0.044] (0.48) | -0.40 (0.98) | n 438, ROI -7.4% | 4/9 | +0.498 | **REJECTED** |
| NFL-PROP-WR_rec_yards-ROLE_RECENCY | WR | rec_yards | ROLE_RECENCY | 10111 | 27.69 (USAGE) | +0.384 [+0.296, +0.470] (0.00) | -0.70 (0.98) | n 438, ROI -7.4% | 9/9 | +0.498 | **FOOTBALL_VALIDATED** |
| NFL-PROP-WR_rec_yards-RUSH_DEF | WR | rec_yards | RUSH_DEF | 10111 | 27.69 (USAGE) | +0.030 [+0.004, +0.054] (0.05) | -1.59 (0.86) | n 438, ROI -7.4% | 5/9 | +0.498 | **DISCOVERY_ONLY** |
| NFL-PROP-WR_rec_yards-SCRIPT | WR | rec_yards | SCRIPT | 10111 | 27.69 (USAGE) | -0.021 [-0.036, -0.007] (0.01) | -0.14 (0.98) | n 438, ROI -7.4% | 4/9 | +0.498 | **REJECTED** |
| NFL-PROP-WR_receptions-HOME | WR | receptions | HOME | 10111 | 1.79 (USAGE) | -0.001 [-0.002, -0.000] (0.03) | -0.01 (0.99) | n 443, ROI -0.1% | 1/9 | +0.028 | **REJECTED** |
| NFL-PROP-WR_receptions-IX_SHARE_x_PASSDEF | WR | receptions | IX_SHARE_x_PASSDEF | 10111 | 1.79 (USAGE) | -0.000 [-0.001, +0.000] (0.44) | — | n 443, ROI -0.1% | 3/9 | +0.028 | **REJECTED** |
| NFL-PROP-WR_receptions-IX_SHARE_x_SCRIPT | WR | receptions | IX_SHARE_x_SCRIPT | 10111 | 1.79 (USAGE) | +0.000 [-0.001, +0.001] (0.88) | — | n 443, ROI -0.1% | 5/9 | +0.028 | **REJECTED** |
| NFL-PROP-WR_receptions-PACE | WR | receptions | PACE | 10111 | 1.79 (USAGE) | +0.000 [-0.002, +0.002] (0.82) | +0.06 (0.97) | n 443, ROI -0.1% | 5/9 | +0.028 | **REJECTED** |
| NFL-PROP-WR_receptions-PASS_DEF | WR | receptions | PASS_DEF | 10111 | 1.79 (USAGE) | -0.000 [-0.001, +0.001] (0.97) | -0.02 (0.98) | n 443, ROI -0.1% | 3/9 | +0.028 | **REJECTED** |
| NFL-PROP-WR_receptions-PASS_TENDENCY | WR | receptions | PASS_TENDENCY | 10111 | 1.79 (USAGE) | -0.000 [-0.002, +0.001] (0.76) | +0.11 (0.97) | n 443, ROI -0.1% | 3/9 | +0.028 | **REJECTED** |
| NFL-PROP-WR_receptions-PRESSURE | WR | receptions | PRESSURE | 10111 | 1.79 (USAGE) | -0.001 [-0.002, +0.000] (0.14) | -0.05 (0.97) | n 443, ROI -0.1% | 5/9 | +0.028 | **REJECTED** |
| NFL-PROP-WR_receptions-QB_EFF | WR | receptions | QB_EFF | 10111 | 1.79 (USAGE) | +0.000 [-0.001, +0.001] (0.83) | +0.06 (0.97) | n 443, ROI -0.1% | 4/9 | +0.028 | **REJECTED** |
| NFL-PROP-WR_receptions-ROLE_RECENCY | WR | receptions | ROLE_RECENCY | 10111 | 1.79 (USAGE) | +0.023 [+0.018, +0.029] (0.00) | -0.15 (0.86) | n 443, ROI -0.1% | 9/9 | +0.028 | **FOOTBALL_VALIDATED** |
| NFL-PROP-WR_receptions-RUSH_DEF | WR | receptions | RUSH_DEF | 10111 | 1.79 (USAGE) | +0.001 [-0.000, +0.003] (0.28) | -0.07 (0.97) | n 443, ROI -0.1% | 6/9 | +0.028 | **REJECTED** |
| NFL-PROP-WR_receptions-SCRIPT | WR | receptions | SCRIPT | 10111 | 1.79 (USAGE) | -0.001 [-0.002, +0.001] (0.65) | +0.00 (0.99) | n 443, ROI -0.1% | 4/9 | +0.028 | **REJECTED** |
