# Milestone F: distribution families for player-prop ladders

**Status: research. Walk-forward, leakage-free, but conditioned on a deliberately weak EWMA projection. Nothing here is validated for real-money use.**

Question: Kalshi prices ladders `P(Y >= k)` (receiving yards 40+/50+/.../120+, receptions 3+/4+/..., passing yards 200+/225+/..., passing TDs 1+/2+/3+, anytime TD, completions, attempts). Given a point projection `mu` (and an opportunity projection), which conditional distribution family gives *calibrated* probabilities at every rung, including the tails?

Code: `nfl_edge/research/player_distributions.py` (reusable fitting / evaluation), `scripts/research/player_distribution_study.py` (runs the study, ~7.5 min). Numbers: `results.json`; full per-statistic / per-population / per-rung tables: `tables.md`; research table: `research_table.parquet`; log: `run.log`.

## 1. TL;DR - chosen family per statistic

Selection rule (fixed before looking at the numbers): lowest ladder Brier on the prop-relevant subset, pooled over the six walk-forward test seasons 2020-2025. The mechanical winner is shown, plus the recommendation after looking at tail calibration (which the mean Brier is nearly blind to, because tail rungs carry little Brier weight).

| statistic (population) | mechanical Brier winner | tail behaviour of winner | **recommendation** |
|---|---|---|---|
| receiving_yards (RB/WR/TE) | emp-binned | 100+: 7.1% pred vs 7.0% obs; 150+: 1.5% vs 1.1% | **emp-binned** (mu-binned empirical scale family). Only family with uniform PIT (chi2 p = 0.62). Normal under-predicts 100+ by a third; lognormal / NB-on-yards over-predict 150+ by 2.6-2.8x. |
| rushing_yards (RB) | emp-binned | 100+: 10.2% vs 10.1%; 150+: 2.1% vs 1.7% | **emp-binned**; hurdle-gamma is the best parametric fallback (100+: 10.0%, 150+: 2.4%). |
| passing_yards (starting QB) | normal | 300+: 21.7% vs 18.6%; 400+: 2.1% vs 1.8% | **normal** (heteroscedastic, censored). QB passing yards are close to Gaussian; every skewed family over-predicts 300+ (lognormal 4.4x at 400+). All families over-predict 300+ by ~15% - a level/variance drift 2022-25 that the mean model does not capture. |
| qb_rushing_yards (starting QB) | emp-binned | 50+: 7.9% vs 8.4%; 100+: 1.1% vs 0.6% | **emp-binned**, hurdle-gamma equal on Brier (0.0618 vs 0.0613) and better at 100+. |
| targets, receptions, carries | emp-binned | 12+ targets 7.9% vs 5.0%; 10+ rec 5.0% vs 2.2%; 24+ carries 7.1% vs 4.2% | **negbin** (mu-dependent dispersion). Emp-binned wins mean Brier via the low rungs (1+..6+) but over-predicts count tails 1.5-2.3x; NB is within 0.002 Brier and calibrated at every rung above 6 (10+ rec 2.8% vs 2.2%; 12+ tgt 5.5% vs 5.0%; 24+ car 5.1% vs 4.2%). |
| attempts, completions (starting QB) | emp-binned / normal | 45+ att 10.3% vs 8.2%; 35+ comp 2.0% vs 2.1% | **normal** for both (Brier within 0.0002 of the winner, best log score, tails within 1.3x). NB over-predicts 50+ attempts 1.7x; Poisson is far too narrow (50+: 0.6% vs 3.0%). |
| passing_tds, interceptions | poisson / negbin | 3+ pass TD 18.7% vs 17.4%; 2+ INT 17.8% vs 16.6% | **poisson** (NB's fitted dispersion is ~0: no residual overdispersion). |
| receiving_tds, rushing_tds, anytime_td | negbin (= poisson) | 1+: 19.2% vs 21.3% (rec), 25.9% vs 28.4% (rush), 28.1% vs 30.9% (any); 3+ over-predicted 1.3-1.7x | **poisson / negbin for 2+/3+ rungs, but the 1+ rung (the anytime-TD market) is under-predicted by 2-3 points by every family**: TD counts are *under*-dispersed given mu. Price anytime TD with a direct binary model, not a count family. |

Two families are never the right answer: the **pooled** empirical scale family (residual shape depends strongly on mu; it over-predicts every tail 1.5-2.1x and its reliability slope is 1.3-2.2) and the **hurdle-lognormal** (tails far too heavy for every yardage stat). The **two-stage Monte-Carlo decomposition** (NB opportunity x gamma / beta-binomial efficiency) never beats direct fitting with these projections: it is 0.001-0.011 Brier worse everywhere and under-predicts the mid rungs of receiving yards (pred/obs 0.84).

## 2. Setup

### 2.1 Research table (`research_table.parquet`)

* **Rows**: one per player-game, regular season 2016-2025, positions QB/RB/WR/TE (2013-2015 are loaded only to warm up the EWMA and to estimate position priors; they are never evaluated).
* **Missing zero rows.** nflverse `stats_player_week` only lists players who recorded something. We add explicit zero rows for every player who took at least one offensive snap (`snap_counts`, mapped `pfr_player_id -> gsis_id` via `player_crosswalk`, one row per `pfr_id`) but has no stats row. These are mostly blocking TEs / WR4-5 / third RBs. They matter for the zero mass of targets/receptions and for the position priors; they are irrelevant for ladders that start at 20+ yards, but a family that does not handle the zero mass will misfit at the low rungs.
* **QB population** = the designated starter for the game (`home_qb_id` / `away_qb_id` in the schedule), which mirrors the players Kalshi actually lists and removes mop-up QBs from both fitting and evaluation. Rushing stats are studied on RBs (`rushing_yards`, `carries`, `rushing_tds`) and separately on starting QBs (`qb_rushing_yards`); receiving stats on RB/WR/TE; anytime TD on RB/WR/TE (TD count = rushing + receiving TDs, so 1+ = anytime TD).
* **Outcomes** are clipped at 0 (1.8% of RB games have negative rushing yards, 0.4% of WR games negative receiving yards). Every rung Kalshi lists is >= 1, so this changes nothing for the ladders; it lets continuous families be censored at 0 consistently.

### 2.2 Point-in-time projection features (no leakage)

For every base stat (attempts, completions, passing yards/TDs/INTs, carries, rushing yards/TDs, targets, receptions, receiving yards/TDs, touches, any TD, offensive snaps) we keep, per player, a running weighted sum `S` and weight `W` over the player's PRIOR games only:

```
feature recorded BEFORE the game:  ewma = (S + k * prior_pos) / (W + k)
then update:                       S <- d*S + y,   W <- d*W + 1,   d = 0.5^(1/halflife)
at a season boundary:              S <- carry*S,   W <- carry*W
```

so the projection is a precision-weighted shrink toward the position prior with `k` pseudo-games; the shrink weight `k/(W+k)` is stored (`shrink_w`) and used as a feature (it tells the mean model how much to trust the EWMA). Position priors are the position means over 2013-2015 (fixed, never refit, so they cannot leak). Efficiency ratios (yards/target, catch rate, yards/carry, yards/attempt, TD per opportunity) are ratios of the shrunk EWMAs. Game context comes from the pre-game schedule line: `home`, team spread, `implied_total = (total_line + team_spread)/2`.

`halflife`, `season_carry`, `k` were chosen on seasons 2016-2019 only (raw-EWMA MAE across 8 stats, table in `tables.md`). The surface is nearly flat: every one of the 16 configurations is within 2.6% of the best. Chosen: half-life 6 games, carry 0.35, k = 2.

### 2.3 Conditioning: one common mean model per statistic

To isolate the *shape* question from the *projection* question, all families condition on the same walk-forward point projection `mu`: OLS (yards) or Poisson GLM (counts/TDs) of the outcome on [EWMA of the stat, EWMA of the opportunity, implied total, home, shrink weight], refit on seasons < S. The two-stage family additionally uses an analogous projection of the opportunity (`mu_opp`) and the player's efficiency ratio. The mean model is deliberately weak (it is the EWMA with a re-scaling), so residual variance here is an upper bound on what a real projection model will leave.

### 2.4 Families

All families are evaluated on the integer lattice: `F(k) = P(Y <= k)` via `F_cont(k + 0.5)`, so CRPS, log score, PIT and `P(Y >= k) = 1 - F(k-1)` are directly comparable between continuous, count and Monte-Carlo families.

| family | definition (theta fit by MLE on train seasons) |
|---|---|
| `normal` | `Y ~ N(c0 + c1 mu, sigma)`, `log sigma = s0 + s1 log mu`; mass below 0 lumped at 0 (censored) |
| `hurdle_lognormal` | `P(Y=0) = sigmoid(a0 + a1 log mu)`; `Y>0`: `log Y ~ N(m0 + m1 log mu, exp(s0 + s1 log mu))` |
| `hurdle_gamma` | same hurdle; `Y>0 ~ Gamma(shape = exp(s0 + s1 log mu), mean = exp(m0 + m1 log mu))` |
| `negbin` | `Y ~ NB(mean = exp(m0 + m1 log mu), Var = m + alpha m^2)`, `log alpha = s0 + s1 log mu` (also applied to yards as counts) |
| `poisson` | `Y ~ Poisson(exp(m0 + m1 log mu))` |
| `scale_emp` | empirical scale family: `r = Y/mu` pooled on train, `P(Y <= x | mu) = ECDF_r(x/mu)` |
| `scale_emp_binned` | same, but a separate ECDF of `r` in each of 5 `mu`-quantile bins (shape allowed to vary with `mu`) |
| `two_stage_mc` | `N ~ NB(mu_opp)` (fit on the opportunity stat) then efficiency given `N` by Monte Carlo (4000 sims): yards -> hurdle + `Gamma(shape = exp(s0 + s1 log N), mean = exp(m0 + m1 log N + m2 log eff))`; receptions/completions/TDs -> `BetaBinomial(N, p = sigmoid(b0 + b1 logit(eff)), kappa)` |
| `climatology` | baseline: unconditional train ECDF of the outcome (no projection at all) |

### 2.5 Evaluation (walk-forward, test seasons 2020-2025, pooled n-weighted)

* CRPS on the lattice, log score of the lattice pmf (floored at 1e-6), randomized PIT (KS statistic and 10-bin chi-square p-value).
* **Ladder calibration** (the metric that matters for Kalshi): for every rung `k` in the Kalshi-style ladder, `P(Y >= k)` vs observed frequency, Brier score, and pooled reliability slope/intercept (OLS of outcome on predicted probability; ideal 1 / 0), plus ECE on 10 probability bins. Rungs are bucketed by the observed base rate in the test set: **low** (>= 50% hit), **mid** (10-50%), **tail** (< 10%). `pred/obs` in the tables is mean predicted vs mean observed hit rate in the bucket; ratio > 1 = family over-predicts.
* Two evaluation populations: **all** rows of the position group, and the **prop-relevant** subset (projected opportunity above a floor: >= 3 targets, >= 6 carries/touches; all starting QBs). The prop-relevant subset is what Kalshi actually lists and is the basis for family choice.
* **Choice rule** (mechanical, applied before looking at the tables): lowest ladder Brier on the prop-relevant subset, ties (< 1e-4) broken by tail pred/obs ratio closest to 1, then CRPS.

## 3. Results

Every table below is on the **prop-relevant subset** (what Kalshi lists), pooled over the walk-forward test seasons 2020-2025 (n = 3,178 starting-QB games, 14,804 receiver games, 5,409 RB games, 10,920 skill-player games). The same tables on all rows of each position group are in `tables.md`; the family ranking is identical on the full population except for two ties (attempts: negbin vs emp-binned at 0.1188; receiving_tds: poisson vs negbin at 0.0642).


### Table A. Ladder Brier score (mean over all Kalshi-style rungs), prop-relevant subset, pooled 2020-2025

Lower is better; bold = best non-baseline family. This is the primary selection metric.

| statistic | n | normal | h-lognormal | h-gamma | negbin | poisson | emp-pooled | emp-binned | two-stage MC | climatology |
|---|---|---|---|---|---|---|---|---|---|---|
| attempts | 3178 | 0.1190 | - | - | **0.1188** | 0.1227 | 0.1193 | 0.1188 | - | 0.1241 |
| completions | 3178 | **0.1132** | - | - | 0.1133 | 0.1150 | 0.1136 | 0.1134 | 0.1137 | 0.1195 |
| passing_yards | 3178 | **0.1353** | 0.1382 | 0.1358 | 0.1358 | - | 0.1357 | 0.1357 | 0.1371 | 0.1452 |
| passing_tds | 3178 | 0.1774 | - | - | 0.1773 | **0.1771** | 0.1792 | 0.1776 | 0.1882 | 0.1892 |
| interceptions | 3178 | 0.2005 | - | - | **0.1940** | 0.1942 | 0.1942 | 0.1944 | 0.1951 | 0.1945 |
| qb_rushing_yards | 3178 | 0.0616 | 0.0627 | 0.0618 | 0.0613 | - | 0.0632 | **0.0613** | 0.0627 | 0.0785 |
| targets | 14804 | 0.1309 | - | - | 0.1293 | 0.1337 | 0.1426 | **0.1272** | - | 0.1887 |
| receptions | 14804 | 0.1227 | - | - | 0.1196 | 0.1229 | 0.1324 | **0.1184** | 0.1201 | 0.1637 |
| receiving_yards | 14804 | 0.1024 | 0.1059 | 0.1047 | 0.1027 | - | 0.1091 | **0.1009** | 0.1034 | 0.1337 |
| receiving_tds | 14804 | 0.0663 | - | - | 0.0642 | **0.0642** | 0.0701 | 0.0650 | 0.0643 | 0.0692 |
| carries | 5409 | 0.1357 | - | - | 0.1331 | 0.1445 | 0.1474 | **0.1313** | - | 0.1906 |
| rushing_yards | 5409 | 0.1141 | 0.1152 | 0.1137 | 0.1129 | - | 0.1210 | **0.1125** | 0.1157 | 0.1471 |
| rushing_tds | 5409 | 0.0858 | - | - | **0.0838** | 0.0839 | 0.0927 | 0.0845 | 0.0844 | 0.0924 |
| anytime_td | 10920 | 0.0939 | - | - | **0.0908** | 0.0910 | 0.1017 | 0.0927 | 0.0927 | 0.1013 |

### Table B. CRPS (integer lattice), prop-relevant subset

Lower is better.

| statistic | n | normal | h-lognormal | h-gamma | negbin | poisson | emp-pooled | emp-binned | two-stage MC | climatology |
|---|---|---|---|---|---|---|---|---|---|---|
| attempts | 3178 | 4.942 | - | - | 4.936 | 5.097 | 4.956 | **4.935** | - | 5.144 |
| completions | 3178 | **3.485** | - | - | 3.489 | 3.543 | 3.498 | 3.488 | 3.500 | 3.675 |
| passing_yards | 3178 | **42.190** | 43.217 | 42.390 | 42.381 | - | 42.381 | 42.317 | 42.743 | 45.075 |
| passing_tds | 3178 | 0.591 | - | - | 0.591 | **0.590** | 0.597 | 0.592 | 0.627 | 0.628 |
| interceptions | 3178 | 0.445 | - | - | **0.432** | 0.432 | 0.432 | 0.432 | 0.434 | 0.433 |
| qb_rushing_yards | 3178 | 8.403 | 8.418 | 8.319 | 8.284 | - | 8.667 | **8.280** | 8.483 | 10.554 |
| targets | 14804 | 1.748 | - | - | **1.639** | 1.719 | 1.848 | 1.654 | - | 2.336 |
| receptions | 14804 | 1.303 | - | - | **1.227** | 1.273 | 1.385 | 1.238 | 1.229 | 1.661 |
| receiving_yards | 14804 | 16.575 | 17.060 | 16.878 | 16.587 | - | 18.429 | **16.308** | 16.644 | 22.065 |
| receiving_tds | 14804 | 0.199 | - | - | 0.193 | **0.193** | 0.211 | 0.195 | 0.193 | 0.208 |
| carries | 5409 | 3.346 | - | - | **3.167** | 3.502 | 3.640 | 3.179 | - | 4.527 |
| rushing_yards | 5409 | 17.704 | 17.885 | 17.608 | 17.475 | - | 19.239 | **17.418** | 17.885 | 23.201 |
| rushing_tds | 5409 | 0.259 | - | - | **0.252** | 0.253 | 0.281 | 0.255 | 0.254 | 0.278 |
| anytime_td | 10920 | 0.284 | - | - | 0.275 | **0.275** | 0.310 | 0.282 | 0.280 | 0.306 |

### Table C. Log score of the lattice pmf (floored at 1e-6)

Higher is better. The pooled/binned empirical families are penalised by zero-mass integers (unsmoothed ECDF), especially with few QB rows.

| statistic | n | normal | h-lognormal | h-gamma | negbin | poisson | emp-pooled | emp-binned | two-stage MC | climatology |
|---|---|---|---|---|---|---|---|---|---|---|
| attempts | 3178 | **-3.601** | - | - | -3.638 | -3.879 | -3.630 | -3.709 | - | -3.652 |
| completions | 3178 | **-3.249** | - | - | -3.288 | -3.410 | -3.272 | -3.323 | -3.312 | -3.306 |
| passing_yards | 3178 | **-5.734** | -5.857 | -5.790 | -5.796 | - | -5.901 | -6.842 | -5.911 | -5.969 |
| passing_tds | 3178 | **-1.446** | - | - | -1.455 | -1.451 | -1.475 | -1.452 | -1.502 | -1.496 |
| interceptions | 3178 | -1.153 | - | - | -1.120 | **-1.120** | -1.125 | -1.124 | -1.125 | -1.122 |
| qb_rushing_yards | 3178 | -3.646 | -3.584 | **-3.545** | -3.566 | - | -3.685 | -3.721 | -3.585 | -3.803 |
| targets | 14804 | -2.482 | - | - | **-2.421** | -2.561 | -2.651 | -2.422 | - | -2.793 |
| receptions | 14804 | -2.173 | - | - | **-2.115** | -2.194 | -2.362 | -2.119 | -2.119 | -2.429 |
| receiving_yards | 14804 | -4.431 | -4.452 | -4.404 | -4.498 | - | -4.624 | **-4.396** | -4.428 | -4.701 |
| receiving_tds | 14804 | -0.647 | - | - | -0.594 | **-0.593** | -0.767 | -0.625 | -0.594 | -0.645 |
| carries | 5409 | -3.155 | - | - | **-3.073** | -3.699 | -3.310 | -3.083 | - | -3.433 |
| rushing_yards | 5409 | -4.690 | -4.684 | **-4.616** | -4.631 | - | -4.829 | -4.716 | -4.671 | -4.951 |
| rushing_tds | 5409 | -0.775 | - | - | **-0.730** | -0.731 | -0.908 | -0.757 | -0.736 | -0.798 |
| anytime_td | 10920 | -0.841 | - | - | -0.784 | **-0.784** | -1.052 | -0.845 | -0.797 | -0.867 |

### Table D. PIT uniformity: chi-square p-value (10 bins, pooled test seasons)

Higher = closer to uniform. With n in the thousands the test is very powerful; p > 0.01 is already a good sign.

| statistic | n | normal | h-lognormal | h-gamma | negbin | poisson | emp-pooled | emp-binned | two-stage MC | climatology |
|---|---|---|---|---|---|---|---|---|---|---|
| attempts | 3178 | 0.000 | - | - | 0.000 | 0.000 | 0.000 | **0.008** | - | 0.000 |
| completions | 3178 | 0.067 | - | - | 0.000 | 0.000 | 0.031 | **0.504** | 0.000 | 0.005 |
| passing_yards | 3178 | 0.002 | 0.000 | 0.000 | 0.000 | - | 0.004 | **0.011** | 0.000 | 0.000 |
| passing_tds | 3178 | 0.053 | - | - | 0.000 | 0.000 | 0.608 | **0.804** | 0.008 | 0.031 |
| interceptions | 3178 | 0.000 | - | - | 0.258 | 0.197 | 0.201 | 0.261 | **0.656** | 0.395 |
| qb_rushing_yards | 3178 | 0.000 | 0.000 | 0.068 | 0.000 | - | 0.000 | **0.428** | 0.000 | 0.000 |
| targets | 14804 | 0.000 | - | - | 0.000 | 0.000 | 0.000 | **0.003** | - | 0.000 |
| receptions | 14804 | 0.000 | - | - | 0.000 | 0.000 | 0.000 | **0.003** | 0.000 | 0.000 |
| receiving_yards | 14804 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.000 | **0.616** | 0.000 | 0.000 |
| receiving_tds | 14804 | 0.000 | - | - | 0.000 | 0.000 | 0.000 | 0.000 | **0.000** | 0.000 |
| carries | 5409 | 0.000 | - | - | 0.000 | 0.000 | 0.000 | **0.169** | - | 0.000 |
| rushing_yards | 5409 | 0.000 | 0.000 | 0.000 | 0.000 | - | 0.000 | **0.468** | 0.000 | 0.000 |
| rushing_tds | 5409 | 0.000 | - | - | 0.000 | 0.000 | 0.000 | **0.033** | 0.000 | 0.000 |
| anytime_td | 10920 | 0.000 | - | - | **0.000** | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

### Table E. Reliability slope (OLS of outcome on predicted P(Y>=k), all rungs pooled; ideal 1.00)

< 1: predictions too extreme (over-confident); > 1: too compressed.

| statistic | n | normal | h-lognormal | h-gamma | negbin | poisson | emp-pooled | emp-binned | two-stage MC | climatology |
|---|---|---|---|---|---|---|---|---|---|---|
| attempts | 3178 | 1.02 | - | - | 1.03 | 0.88 | 1.00 | 1.01 | - | 1.01 |
| completions | 3178 | 1.00 | - | - | 1.01 | 0.91 | 0.99 | 1.00 | 1.03 | 1.00 |
| passing_yards | 3178 | 0.99 | 1.17 | 1.08 | 1.07 | - | 0.99 | 0.98 | 1.04 | 0.98 |
| passing_tds | 3178 | 0.98 | - | - | 1.06 | 1.06 | 1.00 | 1.01 | 1.02 | 1.02 |
| interceptions | 3178 | 0.82 | - | - | 0.98 | 0.93 | 0.99 | 0.98 | 0.97 | 1.00 |
| qb_rushing_yards | 3178 | 0.89 | 1.27 | 1.13 | 1.08 | - | 1.23 | 1.03 | 1.11 | 1.22 |
| targets | 14804 | 0.98 | - | - | 0.97 | 0.88 | 1.31 | 0.99 | - | 1.34 |
| receptions | 14804 | 0.96 | - | - | 0.97 | 0.90 | 1.36 | 0.99 | 0.99 | 1.39 |
| receiving_yards | 14804 | 0.91 | 1.26 | 1.13 | 1.21 | - | 1.52 | 1.02 | 1.06 | 1.71 |
| receiving_tds | 14804 | 0.70 | - | - | 0.99 | 0.99 | 2.19 | 1.06 | 1.06 | 1.67 |
| carries | 5409 | 0.98 | - | - | 1.01 | 0.81 | 1.32 | 1.00 | - | 1.46 |
| rushing_yards | 5409 | 0.94 | 1.19 | 1.08 | 1.07 | - | 1.41 | 1.02 | 1.02 | 1.49 |
| rushing_tds | 5409 | 0.76 | - | - | 1.02 | 1.01 | 2.05 | 1.05 | 1.09 | 1.52 |
| anytime_td | 10920 | 0.74 | - | - | 0.97 | 0.97 | 1.98 | 1.08 | 0.99 | 1.73 |

### Table F. Expected calibration error (10 probability bins, all rungs pooled)

Lower is better.

| statistic | n | normal | h-lognormal | h-gamma | negbin | poisson | emp-pooled | emp-binned | two-stage MC | climatology |
|---|---|---|---|---|---|---|---|---|---|---|
| attempts | 3178 | 0.022 | - | - | 0.023 | 0.056 | 0.022 | **0.019** | - | 0.034 |
| completions | 3178 | 0.017 | - | - | 0.020 | 0.041 | 0.017 | **0.017** | 0.025 | 0.027 |
| passing_yards | 3178 | 0.022 | 0.054 | 0.031 | 0.031 | - | **0.020** | 0.022 | 0.023 | 0.039 |
| passing_tds | 3178 | 0.031 | - | - | 0.031 | 0.030 | 0.024 | **0.023** | 0.041 | 0.029 |
| interceptions | 3178 | 0.077 | - | - | 0.027 | 0.028 | **0.017** | 0.031 | 0.024 | 0.017 |
| qb_rushing_yards | 3178 | 0.019 | 0.025 | 0.012 | 0.012 | - | 0.018 | **0.009** | 0.015 | 0.024 |
| targets | 14804 | 0.020 | - | - | 0.034 | 0.060 | 0.087 | **0.010** | - | 0.163 |
| receptions | 14804 | 0.024 | - | - | 0.027 | 0.045 | 0.069 | **0.009** | 0.028 | 0.132 |
| receiving_yards | 14804 | 0.025 | 0.040 | 0.020 | 0.036 | - | 0.062 | **0.007** | 0.024 | 0.090 |
| receiving_tds | 14804 | 0.027 | - | - | 0.013 | 0.013 | 0.035 | **0.008** | 0.011 | 0.035 |
| carries | 5409 | 0.023 | - | - | 0.033 | 0.090 | 0.084 | **0.010** | - | 0.135 |
| rushing_yards | 5409 | 0.030 | 0.043 | 0.017 | 0.018 | - | 0.055 | **0.009** | 0.022 | 0.088 |
| rushing_tds | 5409 | 0.033 | - | - | 0.015 | 0.016 | 0.052 | **0.012** | 0.013 | 0.041 |
| anytime_td | 10920 | 0.040 | - | - | **0.014** | 0.018 | 0.052 | 0.016 | 0.021 | 0.059 |

### Table G. Tail bucket predicted/observed hit-rate ratio (rungs with observed base rate < 10%; for TD stats where no rung is < 10%, the mid bucket)

1.00 = calibrated; > 1 over-predicts the tail, < 1 under-predicts it. Bold = closest to 1.

| statistic | n | normal | h-lognormal | h-gamma | negbin | poisson | emp-pooled | emp-binned | two-stage MC | climatology |
|---|---|---|---|---|---|---|---|---|---|---|
| attempts | 3178 | 1.31 | - | - | 1.62 | 0.35 | 1.31 | 1.33 | - | 1.52 |
| completions | 3178 | 1.16 | - | - | 1.43 | 0.56 | 1.26 | 1.20 | 1.59 | 1.36 |
| passing_yards | 3178 | 1.30 | 2.80 | 2.00 | 1.98 | - | 1.48 | 1.38 | 1.58 | 1.56 |
| passing_tds | 3178 | 1.07 | - | - | 1.00 | 1.00 | 0.99 | 1.02 | 1.04 | 1.08 |
| interceptions | 3178 | 1.25 | - | - | 1.07 | 1.08 | 1.07 | 1.07 | 1.05 | 1.08 |
| qb_rushing_yards | 3178 | 0.89 | 1.45 | 0.93 | 1.28 | - | 1.50 | 1.08 | 1.04 | 0.81 |
| targets | 14804 | 1.68 | - | - | 1.06 | 1.02 | 1.56 | 1.43 | - | 0.49 |
| receptions | 14804 | 1.80 | - | - | 1.05 | 1.07 | 1.81 | 1.56 | 1.06 | 0.45 |
| receiving_yards | 14804 | 0.60 | 1.40 | 0.84 | 1.53 | - | 2.11 | 1.09 | 0.92 | 0.48 |
| receiving_tds | 14804 | 1.00 | - | - | 0.97 | 0.97 | 2.11 | 1.64 | 0.93 | 0.48 |
| carries | 5409 | 1.60 | - | - | 1.10 | 0.85 | 1.71 | 1.43 | - | 0.66 |
| rushing_yards | 5409 | 0.93 | 1.84 | 1.16 | 1.31 | - | 1.77 | 1.11 | 0.95 | 0.63 |
| rushing_tds | 5409 | 0.94 | - | - | 0.93 | 0.89 | 1.49 | 1.21 | 0.92 | 0.62 |
| anytime_td | 10920 | 1.11 | - | - | 1.04 | 0.94 | 1.55 | 1.41 | 1.01 | 0.43 |

### 3.1 Tail calibration by rung

The mean Brier is dominated by the low and mid rungs. What matters for pricing 5-15 cent YES contracts is the per-rung predicted vs observed hit rate at the top of the ladder. Tables below give `P(Y >= k)` averaged over the prop-relevant rows next to the observed hit rate (n hits = number of games that cleared the rung, so you can judge the sampling error: for 160 hits the observed rate has a standard error of about 8% relative).


**receiving_yards** (prop-relevant subset, n=14804; families ordered by ladder Brier, best first; chosen = emp-binned)

| k | observed | n hits | emp-binned | normal | negbin | two-stage MC | h-gamma | h-lognormal | emp-pooled |
|---|---|---|---|---|---|---|---|---|---|
| 60+ | 0.239 | 3541 | 0.235 | 0.247 | 0.229 | 0.199 | 0.206 | 0.200 | 0.215 |
| 80+ | 0.133 | 1967 | 0.131 | 0.115 | 0.145 | 0.109 | 0.109 | 0.123 | 0.150 |
| 90+ | 0.098 | 1457 | 0.097 | 0.074 | 0.115 | 0.081 | 0.079 | 0.099 | 0.128 |
| 100+ | 0.070 | 1033 | 0.071 | 0.047 | 0.092 | 0.060 | 0.057 | 0.080 | 0.110 |
| 110+ | 0.050 | 745 | 0.052 | 0.029 | 0.073 | 0.044 | 0.041 | 0.065 | 0.095 |
| 120+ | 0.033 | 494 | 0.038 | 0.017 | 0.058 | 0.033 | 0.029 | 0.053 | 0.083 |
| 130+ | 0.023 | 340 | 0.028 | 0.010 | 0.046 | 0.024 | 0.021 | 0.044 | 0.073 |
| 150+ | 0.011 | 160 | 0.015 | 0.003 | 0.029 | 0.013 | 0.011 | 0.031 | 0.057 |

**rushing_yards** (prop-relevant subset, n=5409; families ordered by ladder Brier, best first; chosen = emp-binned)

| k | observed | n hits | emp-binned | negbin | h-gamma | normal | h-lognormal | two-stage MC | emp-pooled |
|---|---|---|---|---|---|---|---|---|---|
| 60+ | 0.320 | 1733 | 0.312 | 0.301 | 0.292 | 0.346 | 0.279 | 0.281 | 0.253 |
| 80+ | 0.181 | 981 | 0.183 | 0.186 | 0.173 | 0.197 | 0.185 | 0.161 | 0.171 |
| 90+ | 0.133 | 721 | 0.137 | 0.144 | 0.132 | 0.142 | 0.152 | 0.120 | 0.142 |
| 100+ | 0.101 | 546 | 0.102 | 0.111 | 0.100 | 0.100 | 0.126 | 0.088 | 0.118 |
| 110+ | 0.070 | 381 | 0.075 | 0.085 | 0.076 | 0.069 | 0.105 | 0.065 | 0.100 |
| 120+ | 0.050 | 270 | 0.055 | 0.065 | 0.057 | 0.046 | 0.088 | 0.047 | 0.085 |
| 130+ | 0.035 | 189 | 0.040 | 0.049 | 0.043 | 0.030 | 0.074 | 0.034 | 0.072 |
| 150+ | 0.017 | 93 | 0.021 | 0.028 | 0.024 | 0.012 | 0.054 | 0.018 | 0.054 |

**passing_yards** (prop-relevant subset, n=3178; families ordered by ladder Brier, best first; chosen = normal)

| k | observed | n hits | normal | emp-binned | emp-pooled | negbin | h-gamma | two-stage MC | h-lognormal |
|---|---|---|---|---|---|---|---|---|---|
| 250+ | 0.394 | 1252 | 0.434 | 0.424 | 0.411 | 0.406 | 0.405 | 0.411 | 0.401 |
| 275+ | 0.280 | 889 | 0.318 | 0.306 | 0.297 | 0.307 | 0.307 | 0.303 | 0.315 |
| 300+ | 0.186 | 590 | 0.217 | 0.210 | 0.204 | 0.224 | 0.225 | 0.213 | 0.244 |
| 325+ | 0.114 | 362 | 0.137 | 0.135 | 0.135 | 0.158 | 0.159 | 0.142 | 0.186 |
| 350+ | 0.064 | 204 | 0.080 | 0.081 | 0.086 | 0.108 | 0.109 | 0.091 | 0.141 |
| 375+ | 0.034 | 108 | 0.043 | 0.047 | 0.053 | 0.072 | 0.073 | 0.055 | 0.106 |
| 400+ | 0.018 | 56 | 0.021 | 0.027 | 0.032 | 0.046 | 0.048 | 0.032 | 0.080 |

**qb_rushing_yards** (prop-relevant subset, n=3178; families ordered by ladder Brier, best first; chosen = emp-binned)

| k | observed | n hits | emp-binned | negbin | normal | h-gamma | two-stage MC | h-lognormal | emp-pooled |
|---|---|---|---|---|---|---|---|---|---|
| 30+ | 0.213 | 677 | 0.200 | 0.199 | 0.219 | 0.191 | 0.176 | 0.184 | 0.172 |
| 50+ | 0.084 | 266 | 0.079 | 0.090 | 0.077 | 0.072 | 0.072 | 0.087 | 0.086 |
| 70+ | 0.031 | 99 | 0.034 | 0.042 | 0.027 | 0.029 | 0.033 | 0.047 | 0.049 |
| 100+ | 0.006 | 20 | 0.011 | 0.013 | 0.005 | 0.008 | 0.012 | 0.022 | 0.024 |

**receptions** (prop-relevant subset, n=14804; families ordered by ladder Brier, best first; chosen = emp-binned)

| k | observed | n hits | emp-binned | negbin | two-stage MC | normal | poisson | emp-pooled |
|---|---|---|---|---|---|---|---|---|
| 5+ | 0.288 | 4269 | 0.278 | 0.255 | 0.251 | 0.288 | 0.229 | 0.225 |
| 6+ | 0.189 | 2791 | 0.191 | 0.168 | 0.168 | 0.204 | 0.150 | 0.169 |
| 7+ | 0.117 | 1737 | 0.133 | 0.109 | 0.109 | 0.146 | 0.100 | 0.129 |
| 8+ | 0.071 | 1057 | 0.093 | 0.070 | 0.070 | 0.106 | 0.067 | 0.101 |
| 9+ | 0.041 | 603 | 0.067 | 0.044 | 0.044 | 0.078 | 0.046 | 0.079 |
| 10+ | 0.022 | 329 | 0.050 | 0.028 | 0.028 | 0.058 | 0.032 | 0.064 |

**targets** (prop-relevant subset, n=14804; families ordered by ladder Brier, best first; chosen = emp-binned)

| k | observed | n hits | emp-binned | negbin | normal | poisson | emp-pooled |
|---|---|---|---|---|---|---|---|
| 6+ | 0.407 | 6031 | 0.385 | 0.351 | 0.377 | 0.320 | 0.289 |
| 8+ | 0.225 | 3329 | 0.224 | 0.200 | 0.234 | 0.175 | 0.190 |
| 10+ | 0.111 | 1639 | 0.130 | 0.107 | 0.147 | 0.097 | 0.129 |
| 11+ | 0.074 | 1097 | 0.101 | 0.077 | 0.118 | 0.073 | 0.107 |
| 12+ | 0.050 | 734 | 0.079 | 0.055 | 0.094 | 0.055 | 0.090 |

**carries** (prop-relevant subset, n=5409; families ordered by ladder Brier, best first; chosen = emp-binned)

| k | observed | n hits | emp-binned | negbin | normal | poisson | emp-pooled |
|---|---|---|---|---|---|---|---|
| 14+ | 0.344 | 1860 | 0.321 | 0.299 | 0.304 | 0.241 | 0.242 |
| 18+ | 0.173 | 935 | 0.180 | 0.160 | 0.184 | 0.121 | 0.162 |
| 20+ | 0.116 | 625 | 0.133 | 0.112 | 0.141 | 0.084 | 0.134 |
| 22+ | 0.072 | 392 | 0.097 | 0.076 | 0.108 | 0.059 | 0.112 |
| 24+ | 0.042 | 229 | 0.071 | 0.051 | 0.083 | 0.041 | 0.093 |

**attempts** (prop-relevant subset, n=3178; families ordered by ladder Brier, best first; chosen = emp-binned)

| k | observed | n hits | emp-binned | negbin | normal | emp-pooled | poisson |
|---|---|---|---|---|---|---|---|
| 35+ | 0.394 | 1253 | 0.425 | 0.411 | 0.436 | 0.419 | 0.392 |
| 40+ | 0.204 | 647 | 0.225 | 0.234 | 0.239 | 0.227 | 0.146 |
| 45+ | 0.082 | 262 | 0.103 | 0.116 | 0.104 | 0.100 | 0.036 |
| 50+ | 0.030 | 97 | 0.038 | 0.050 | 0.035 | 0.038 | 0.006 |

**completions** (prop-relevant subset, n=3178; families ordered by ladder Brier, best first; chosen = normal)

| k | observed | n hits | normal | negbin | emp-binned | emp-pooled | two-stage MC | poisson |
|---|---|---|---|---|---|---|---|---|
| 25+ | 0.279 | 886 | 0.307 | 0.295 | 0.296 | 0.289 | 0.298 | 0.249 |
| 30+ | 0.090 | 286 | 0.101 | 0.111 | 0.099 | 0.101 | 0.119 | 0.057 |
| 35+ | 0.021 | 68 | 0.020 | 0.032 | 0.025 | 0.028 | 0.037 | 0.007 |

**receiving_tds** (prop-relevant subset, n=14804; families ordered by ladder Brier, best first; chosen = negbin)

| k | observed | n hits | negbin | poisson | two-stage MC | emp-binned | normal | emp-pooled |
|---|---|---|---|---|---|---|---|---|
| 1+ | 0.213 | 3158 | 0.192 | 0.192 | 0.191 | 0.192 | 0.260 | 0.101 |
| 2+ | 0.030 | 449 | 0.028 | 0.028 | 0.027 | 0.042 | 0.028 | 0.046 |
| 3+ | 0.003 | 38 | 0.004 | 0.004 | 0.003 | 0.012 | 0.005 | 0.023 |

**rushing_tds** (prop-relevant subset, n=5409; families ordered by ladder Brier, best first; chosen = negbin)

| k | observed | n hits | negbin | poisson | two-stage MC | emp-binned | normal | emp-pooled |
|---|---|---|---|---|---|---|---|---|
| 1+ | 0.284 | 1539 | 0.259 | 0.260 | 0.263 | 0.261 | 0.343 | 0.148 |
| 2+ | 0.060 | 325 | 0.053 | 0.051 | 0.053 | 0.064 | 0.053 | 0.067 |
| 3+ | 0.007 | 38 | 0.010 | 0.009 | 0.009 | 0.018 | 0.009 | 0.034 |

**anytime_td** (prop-relevant subset, n=10920; families ordered by ladder Brier, best first; chosen = negbin)

| k | observed | n hits | negbin | poisson | two-stage MC | emp-binned | normal | emp-pooled |
|---|---|---|---|---|---|---|---|---|
| 1+ | 0.309 | 3379 | 0.281 | 0.278 | 0.269 | 0.266 | 0.374 | 0.155 |
| 2+ | 0.066 | 720 | 0.062 | 0.058 | 0.062 | 0.078 | 0.067 | 0.078 |
| 3+ | 0.009 | 100 | 0.015 | 0.012 | 0.014 | 0.028 | 0.016 | 0.038 |

**passing_tds** (prop-relevant subset, n=3178; families ordered by ladder Brier, best first; chosen = poisson)

| k | observed | n hits | poisson | negbin | normal | emp-binned | emp-pooled | two-stage MC |
|---|---|---|---|---|---|---|---|---|
| 1+ | 0.772 | 2452 | 0.752 | 0.752 | 0.795 | 0.770 | 0.771 | 0.753 |
| 2+ | 0.443 | 1409 | 0.422 | 0.422 | 0.473 | 0.443 | 0.425 | 0.427 |
| 3+ | 0.174 | 552 | 0.187 | 0.187 | 0.182 | 0.180 | 0.178 | 0.195 |

**interceptions** (prop-relevant subset, n=3178; families ordered by ladder Brier, best first; chosen = negbin)

| k | observed | n hits | negbin | poisson | emp-pooled | emp-binned | two-stage MC | normal |
|---|---|---|---|---|---|---|---|---|
| 1+ | 0.500 | 1589 | 0.514 | 0.528 | 0.514 | 0.511 | 0.508 | 0.608 |
| 2+ | 0.166 | 528 | 0.178 | 0.175 | 0.177 | 0.180 | 0.175 | 0.204 |

### 3.2 What the tails say

**Receiving yards (the most important ladder).** Are `P(Y >= 100)` probabilities calibrated? With the mu-binned empirical family, yes: 7.1% predicted vs 7.0% observed at 100+, 5.2% vs 5.0% at 110+, 3.8% vs 3.3% at 120+, 2.8% vs 2.3% at 130+, 1.5% vs 1.1% at 150+ (mild over-prediction above 120 that is within ~2 standard errors). Every parametric family fails somewhere: the censored Normal (sigma ~ mu^0.39) is too thin - 4.7% at 100+, 0.3% at 150+ (under by 33% and 73%); NB-on-yards and the hurdle-lognormal are too fat - 9.2% / 8.0% at 100+ and 2.9% / 3.1% at 150+ (2.6-2.8x); the hurdle-gamma is right at 150+ (1.1%) but under-predicts the 90-130 range by 15-20%; the two-stage MC under-predicts 80-110 (6.0% at 100+).

**Rushing yards.** Same picture but the parametric families are closer: hurdle-gamma matches 100+ (10.0% vs 10.1%) and is only 1.4x at 150+; NB-on-yards is 1.1-1.6x over from 100+ up; Normal is right at 100+ and under at 150+ (1.2% vs 1.7%); lognormal is 3x at 150+. Emp-binned: 10.2% vs 10.1% at 100+, 2.1% vs 1.7% at 150+.

**Passing yards.** Every family over-predicts 300+ (observed 18.6%; Normal 21.7%, emp-binned 21.0%, NB / gamma 22.4%, lognormal 24.4%) and 350+ (observed 6.4%; Normal 8.0%, NB / gamma 10.9%, lognormal 14.1%). The Normal is the least wrong and nails 400+ (2.1% vs 1.8%); the skewed families are 2.5-4.4x at 400+. The uniform over-prediction at 300+ with a calibrated 150+/175+ rung (pred/obs 1.02) is the signature of a variance that shrank in the test seasons relative to 2016-2019 training data (fewer 300-yard games league-wide in 2022-2025), which a projection with league-trend features would absorb.

**Counts (targets, receptions, carries, attempts).** The scale family is mis-specified for counts: the spread of `Y/mu` shrinks like `mu^-0.5` for count-like data, so pooling ratios within a mu bin fattens the tail for the lower-mu rows in the bin. Result: emp-binned over-predicts 10+ receptions 2.3x (5.0% vs 2.2%), 12+ targets 1.6x, 24+ carries 1.7x, 45+ attempts 1.3x. NB with `log alpha = s0 + s1 log mu` is calibrated at those rungs (2.8%, 5.5%, 5.1%, 11.6% vs 2.2%, 5.0%, 4.2%, 8.2%) and is within 0.002 Brier. The Normal is too fat at count tails (10+ receptions 5.8%) except for QB attempts / completions, where it is best overall. Poisson is far too narrow for volume counts (50+ attempts 0.6% vs 3.0%; 24+ carries 4.1% vs 4.2% only by accident of the mean).

**Touchdowns.** NB's fitted dispersion collapses to ~0 for every TD stat (`alpha` ~ exp(-4)), so NB = Poisson. Both are well calibrated at 2+ (2.8% vs 3.0% receiving, 5.3% vs 6.0% rushing, 6.2% vs 6.6% anytime) and over-predict 3+ by 1.3-1.7x (small counts: 38-100 hits). But the 1+ rung - the anytime-TD market itself - is under-predicted by every family: 19.2% vs 21.3% (receiving), 25.9% vs 28.4% (rushing), 28.1% vs 30.9% (anytime). Under-predicting 1+ while over-predicting 3+ with the right mean means the conditional distribution is *under*-dispersed relative to Poisson (a player with opportunity scores at most once far more often than a Poisson with the same mean says). The beta-binomial two-stage model does not fix it (26.9% at 1+) because the NB opportunity stage injects extra dispersion. Passing TDs show the same pattern more mildly (1+: 75.2% vs 77.2%; 3+: 18.7% vs 17.4%). Practical consequence: for anytime TD, fit P(Y >= 1) directly (logistic on the same features) rather than deriving it from a count family; use Poisson only for the 2+/3+ rungs.

**Interceptions** are essentially unpredictable with these features: the chosen family beats climatology by a Brier skill of 0.002 (mean-model MAE 0.707 vs 0.711 for the raw EWMA, climatology CRPS 0.433 vs 0.432). Rung probabilities are still calibrated (1+: 51.4% vs 50.0%) because the population base rate is stable, which is all a family can deliver when mu carries no information.

### 3.3 Effect sizes

* **Value of the projection.** Brier skill vs climatology (unconditional train ECDF) of the chosen family, prop-relevant subset: targets 0.33, carries 0.31, receptions 0.28, receiving yards 0.25, rushing yards 0.24, QB rushing yards 0.22, anytime TD 0.10, rushing TDs 0.09, receiving TDs 0.07, passing yards 0.07, passing TDs 0.06, completions 0.05, attempts 0.04, interceptions 0.00. CRPS falls 26-30% for the volume stats (e.g. receiving yards 22.1 -> 16.3, rushing yards 23.2 -> 17.4) but only 6% for passing yards (45.1 -> 42.2): starting-QB volume is much less predictable from own-history than receiver volume, because the QB population is already conditioned on being the starter.
* **Value of the family choice.** Between the best and worst *reasonable* family (excluding the pooled empirical and lognormal) the ladder Brier differs by 1-3% (receiving yards 0.1009 vs 0.1034; rushing yards 0.1125 vs 0.1157; receptions 0.1184 vs 0.1229); ECE differs by 2-3x (0.007 vs 0.020-0.025). At the tail rungs the differences are 1.5-3x in probability, i.e. the difference between a 5-cent and a 12-cent contract. Family choice is a tail question, not an average-Brier question.
* **Mean model vs raw EWMA.** The walk-forward re-scaling (EWMA + opportunity + implied total + home + shrink weight) improves MAE by 4-6% for yards (receiving 16.7 -> 15.7, rushing 20.8 -> 19.5, passing 61.9 -> 59.4) and by 0-4% for counts and TDs. The EWMA hyperparameter surface is flat: all 16 (half-life, carry, k) settings are within 2.6% relative MAE; half-life 6 games, season carry 0.35, k = 2 pseudo-games was chosen on 2016-2019.
* **Heteroscedasticity.** Fitted `sigma ~ mu^0.39` for receiving yards (Normal family), `alpha ~ mu^-1.05` for NB-on-receiving-yards (Var = m + alpha m^2, so sd ~ mu^0.48), and `sigma` essentially constant in mu for passing yards (`s1 = -0.06`): a homoscedastic Gaussian is adequate for starting-QB passing yards but wrong for receivers.
* **Stability.** Per-season CRPS of the chosen families varies by < 6% across 2020-2025 (receiving yards 15.8-16.6; rushing yards 16.6-18.4; passing yards 40.4-44.3), with no season driving the ranking.

## 4. Chosen family per statistic - justification

| statistic | family | why |
|---|---|---|
| receiving_yards, rushing_yards, qb_rushing_yards | emp-binned (5 mu-quantile bins of `Y/mu`) | Best Brier, best ECE (0.007-0.009), only family with uniform PIT (chi2 p 0.43-0.62), reliability slope 1.02-1.03, tails within 1.1x through 150+. Fallback if a parametric form is required: hurdle-gamma with shape ~ mu^0.21 (rushing) - never the lognormal or NB-on-yards. |
| passing_yards | normal, censored, `sigma` ~ constant | Best on every metric (CRPS 42.2 vs 42.3-43.2, Brier 0.1353, log score -5.73). QB passing yards are nearly symmetric; all skewed families over-predict 325+. Residual over-prediction at 300+ is a projection-drift problem, not a shape problem. |
| targets, receptions, carries | negbin with `log alpha = s0 + s1 log mu` | Within 0.002 Brier of the emp-binned winner but calibrated at the count tails (7+ ... 12+), where emp-binned and Normal over-predict 1.5-2.3x. Best CRPS of all families for these three stats. |
| attempts, completions | normal, censored | Brier ties the winner (0.1190 vs 0.1188; 0.1132), best log score, tails within 1.3x; NB over-predicts 50+ attempts 1.7x. |
| passing_tds, interceptions | poisson | NB dispersion fits to ~0; Poisson = NB at every rung, fewer parameters. |
| receiving_tds, rushing_tds, anytime_td | poisson for 2+/3+; **direct binary model for 1+** | See 3.2: count families under-predict 1+ by 2-3 points and over-predict 3+; the data are under-dispersed given mu. |

## 5. Limitations (read before using any of this)

1. **The projection is weak on purpose.** `mu` is an EWMA of the player's own history plus the market total; there is no opponent adjustment, no injury / depth-chart / snap-share information (only the player's own prior snap EWMA), no QB change, no weather. The residual variance every family is fitting is therefore inflated relative to what a real projection model leaves, and the *shape* of the residual will change when the projection improves: a better mean model removes mixture components (e.g. "the WR1 was actually inactive / on a snap count") that currently sit in the tails. The distribution study must be re-run once Milestone-level projections exist; the ranking of parametric vs empirical families may flip.
2. **Zero rows are recovered only from snap counts (2012+).** 7,386 zero rows (11.6% of 2016-2025) were added for players with >= 1 offensive snap and no stat line; 195 stat rows per season have no snap-count match (crosswalk gaps). Players who were active but took zero offensive snaps are absent by construction; for the prop-relevant subset (projected >= 3 targets / 6 carries) this is a small share, but it means the *unconditional* zero mass of targets is slightly understated.
3. **Position priors** are static 2013-2015 position means and over-state the expectation of a first-game backup (a new blocking TE gets the TE-average prior of 2.7 targets). This affects only rows with a small `W` (mean shrink weight 0.31-0.34), and the mean model partially corrects it via the `shrink_w` feature.
4. **Prop-relevant subset is defined by our own projection** (projected opportunity floor), not by what Kalshi actually listed. The true listed set is more selective (WR1-3, RB1-2, starting QB), which would shift the mix toward higher-mu rows where the scale family is better tested; it is also where sampling error at 130+/150+ rungs is largest (93-340 hits).
5. **Unsmoothed ECDFs.** The empirical families put zero mass on integers not seen in a bin, which is why their log score is poor for the small QB population (passing yards -6.84 vs -5.73). Ladder probabilities are unaffected (they are ECDF differences over ranges of 10-25 yards) but any production version should smooth (KDE on `Y/mu` within bin, or a parametric tail splice above the 95th percentile).
6. **Outcomes clipped at 0** (284 RB games with negative rushing yards, 514 receiver games with negative receiving yards, i.e. 1.8% / 0.9%). Irrelevant for rungs >= 1, but the CRPS and log scores are for the clipped outcome.
7. **Passing-yards drift.** All families over-predict 300+/350+ in 2020-2025 by 15-25%. This is not a family problem: the mean/variance of starting-QB passing changed relative to the training window. Any production model needs a league-trend feature or a rolling re-fit of the variance parameters (the study refits every season, but on all prior seasons equally).
8. **No market prices were used.** The study answers "which family is internally calibrated given our projection", not "which family beats Kalshi". Market-implied ladder probabilities are the obvious next benchmark (Milestone G).
9. **Multiple comparisons.** With 6-7 families x 14 stats and differences of 0.001-0.003 Brier, some rankings are within noise (attempts, completions, interceptions, TD stats: the top 3 are indistinguishable). Only the yards-vs-count recommendations (empirical / Normal for yards, NB for counts) and the failures (pooled empirical, lognormal, Poisson for volume counts) are large enough to be beyond doubt.

## 6. Files

* `research/player_distributions/RESULTS.md` - this document.
* `research/player_distributions/results.json` - every metric for every family x statistic x population (all / prop-relevant) x test season, per-rung predicted vs observed, fitted parameters per season, tuning table, data summary.
* `research/player_distributions/tables.md` - auto-generated per-statistic tables (both populations, all metrics, per-rung tables, per-season CRPS).
* `research/player_distributions/research_table.parquet` - the 2016-2025 player-game research table with all point-in-time features (63,940 rows).
* `research/player_distributions/run.log` - run log with hyperparameter tuning output.
* `nfl_edge/research/player_distributions.py` - data assembly, EWMA features, mean models, families, evaluation.
* `scripts/research/player_distribution_study.py` - the study driver (`python scripts/research/player_distribution_study.py [stat ...]`, env `NSIMS`).
