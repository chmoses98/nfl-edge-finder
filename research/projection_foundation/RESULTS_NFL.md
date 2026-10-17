# NFL Projection Foundation — walk-forward results

*Generated 2026-10-17T07:27:25Z from code `aba4cdc2a2`, pf_core 1.0.0. Research only: nothing here changes betting authority. Reproduce: `cd research/projection_foundation && python -m nfl.incumbent && python -m nfl.run_walkforward --stage all && python -m nfl.project`.*

## Bottom line

- **Every frozen winner beat the season-average baseline on the untouched 2024-25 holdout** (13/13 families, game-clustered 95% CIs exclude 0). Against the incumbent `shadow-0.4.0` replayed walk-forward with its own code, the frozen winners are significantly better in 8 of 10 player families (targets, receptions, receiving_yards, carries, rushing_yards, passing_attempts, completions, anytime_td), tied on passing yards, and **worse on passing TDs** (passing_tds).
- Biggest gains are on opportunity: targets CRPS 1.373 vs 1.496 for shadow-0.4.0 (holdout), driven by a LightGBM rung refitted every season and stacked with the structured opportunity x efficiency model.
- Readiness: READY — team_pass_attempts, team_rush_attempts, team_points, targets, receptions, completions, passing_yards; SHADOW VALIDATION — receiving_yards, carries, rushing_yards, passing_attempts, anytime_td; NEEDS IMPROVEMENT — passing_tds.
- Verified defects found and fixed before the freeze: (1) QB volume was under-projected ~5% because a QB's history included relief/garbage-time appearances (fixed with starts-only history + implied-total term); (2) players who play through a Questionable tag produce ~7-12% below projection, and teammates listed OUT redistribute carries (not targets) — both now in the 'availability' rung.
- Verified defects found AFTER the freeze (pre-registered, not adopted): a player's first games with a new team are over-projected 14-37% on development (rushing yards +99% on 2022-23), and backup tiers (RB2+/TE2+/WR3+) are over-projected 7-18%. Dev-fitted corrections improve validation CRPS with CIs excluding 0; they wait for untouched data before adoption.
- Distributions are calibrated: holdout 80% coverage 0.79-0.82 and PIT variance ratios 0.95-1.03 in every family. The gate's real value was catching two publication defects (pmf mean vs published mean; E/F extrapolation outside their training population), not flagging larger errors — REVIEW projections carry only ~4% higher CRPS on validation and none on holdout.
- Nothing here is a betting claim: the foundation measures projection accuracy; betting authority is unchanged.

| family | best model (frozen) | val CRPS vs A | holdout CRPS vs A | holdout vs shadow-0.4.0 | readiness |
|---|---|---|---|---|---|
| team_pass_attempts | F_stack | -0.0589 [-0.1049, -0.0101] ✔ | -0.0600 [-0.1038, -0.0177] ✔ | — | READY |
| team_rush_attempts | F_stack | -0.0732 [-0.1200, -0.0232] ✔ | -0.1018 [-0.1461, -0.0600] ✔ | — | READY |
| team_points | F_stack | -0.2173 [-0.3053, -0.1306] ✔ | -0.3515 [-0.4531, -0.2590] ✔ | — | READY |
| targets | F_plus_availability | -0.0688 [-0.0802, -0.0573] ✔ | -0.0828 [-0.0956, -0.0718] ✔ | -0.1231 [-0.1409, -0.1073] ✔ | READY |
| receptions | F_plus_availability | -0.0381 [-0.0460, -0.0306] ✔ | -0.0429 [-0.0505, -0.0363] ✔ | -0.0690 [-0.0818, -0.0576] ✔ | READY |
| receiving_yards | F_plus_availability | -0.3446 [-0.4283, -0.2617] ✔ | -0.3768 [-0.4491, -0.3061] ✔ | -0.3253 [-0.4058, -0.2523] ✔ | SHADOW VALIDATION |
| carries | F_plus_availability | -0.3227 [-0.3853, -0.2574] ✔ | -0.2742 [-0.3324, -0.2205] ✔ | -0.2332 [-0.2854, -0.1808] ✔ | SHADOW VALIDATION |
| rushing_yards | F_plus_availability | -1.0155 [-1.2755, -0.7649] ✔ | -0.7376 [-0.9845, -0.5106] ✔ | -0.2433 [-0.4522, -0.0306] ✔ | SHADOW VALIDATION |
| passing_attempts | F_qb_starts_env_stack | -0.0712 [-0.1482, +0.0057] | -0.1961 [-0.2802, -0.1109] ✔ | -0.1355 [-0.2026, -0.0684] ✔ | SHADOW VALIDATION |
| completions | F_qb_starts_env_stack | -0.0763 [-0.1406, -0.0176] ✔ | -0.1360 [-0.1937, -0.0780] ✔ | -0.0907 [-0.1366, -0.0431] ✔ | READY |
| passing_yards | F_qb_starts_env_stack | -0.7832 [-1.5115, -0.0155] ✔ | -1.3678 [-2.1312, -0.6495] ✔ | -0.5631 [-1.1936, +0.0871] | READY |
| passing_tds | D_qb_starts_env | -0.0066 [-0.0141, +0.0010] | -0.0129 [-0.0222, -0.0038] ✔ | +0.0123 [+0.0045, +0.0209] ✘ | NEEDS IMPROVEMENT |
| anytime_td | F_plus_availability | -0.0055 [-0.0070, -0.0040] ✔ | -0.0063 [-0.0076, -0.0050] ✔ | -0.0011 [-0.0021, -0.0001] ✔ | SHADOW VALIDATION |


CRPS differences are paired on identical player-games (negative = better), 95% CI from a game-clustered bootstrap; ✔ = CI excludes zero in favour of the first model, ✘ = significantly worse.

## Design

- **Splits (chronological, frozen before evaluation):** development 2016-2021 regular seasons (2012-2015 feature warm-up only); validation 2022-2023 regular seasons; holdout 2024-2025 regular seasons (evaluated once, frozen candidates only); 2026 weeks 1-4, read-only accuracy check (already used in market discovery; never tuned on); 2026 weeks >= 5: untouched market holdout, never scored here. All tuning (shrinkage k, EWMA halflife, elasticities, stack weights, distribution parameters) uses development rows only; validation picks the model and the distribution family; the holdout was scored once, after `results/nfl_frozen_selection.json` had been committed (commit aba4cdc precedes the holdout run).
- **Point-in-time features:** every feature at game g uses only games that kicked off earlier (pf_core.pit.lagged_features shifts within player/team; rolling ridge opponent ratings are refitted before every (season, week) block; positional priors are expanding means over earlier weeks). Pregame market context = closing spread/total from the nflverse schedule. `tests/test_nfl_pf.py` asserts that changing a game's outcome cannot change any feature of that game or earlier.
- **Walk-forward:** A-D are formula models evaluated sequentially with frozen hyperparameters; E (LightGBM) is refitted before every season on all earlier seasons (2013+), so every 2016-2026 prediction is out-of-sample; F stacks B, C, D, E with non-negative weights fitted on development predictions (holdout uses the pre-declared refit on development + validation). The incumbents are refitted the same way (seasons 2016..T-1) with their own frozen code (`nfl/incumbent.py`, in-memory challenger swap, no file edits).
- **Availability:** player metrics are conditional on participation (>= 1 offensive snap or a stat line), the prop-settlement convention (DNP = void). 'Did he play' is post-game, so it is never a feature; participation is modelled separately from the final injury designation (see Availability) and its effect quantified.
- **Populations (point-in-time):** receiving families = RB/WR/TE averaging >= 2 targets over their previous 4 games played; rushing families = RBs averaging >= 4 carries; QB families = the scheduled starter; anytime TD = RB/WR/TE meeting either role rule. A player's first career game is outside these populations by construction (no history).
- **Metrics:** MAE/RMSE/bias of the mean; CRPS and log score of the full integer distribution; randomised-PIT coverage; Brier at Kalshi-like rungs. Every comparison is paired on identical player-games with a game-clustered bootstrap (pf_core.metrics).

## Data inventory

| dataset | seasons | rows | pit_class | notes |
|---|---|---|---|---|
| nflverse player weekly stats (stats_player) | 2012-2026 | 257732 | reconstructable | Outcomes and, lagged, the core features. Release available 1999+; 2012-2026 downloaded (2012-2015 warm-up only). 2026 = weeks 1-5 + Thursday week 6. |
| nflverse team weekly stats (stats_team) | 2012-2026 | 7818 | reconstructable | Team pass attempts / carries / yards per game: team-volume outcomes and opponent 'allowed' histories. |
| schedules with closing lines (games.csv) | 1999-2026 | 7548 | archived | spread_line / total_line are the final pregame (closing) lines: pregame by construction, but recorded retrospectively (not our own vintage). QB ids are the ACTUAL starter for past games (retrospective; announced pregame in practice) and the projected starter for upcoming games. |
| weather / roof (schedule temp, wind, roof) | 1999-2026 | 0 | retrospective | temp/wind are game-time observations, not forecasts -> not used as features. Roof is pregame-known and used. Timestamped NWS/Open-Meteo forecasts exist only from the 2026 context capture on the market-data branch. |
| snap counts (PFR) | 2012-2026 | 332075 | reconstructable | 2012+. Used for offense-snap share history and to add zero-stat participation rows. Participation itself is post-game. |
| injury reports (final designation) | 2012-2026 | 78236 | retrospective | 2009-2026 Out/Doubtful/Questionable + practice status. No per-row timestamp (date_modified in 2024 only), rebuilt in place; treated as NEAR-pregame (Friday report) and flagged. |
| weekly rosters (status ACT/INA/RES) | 2012-2026 | 609004 | retrospective | Snapshot time unknown; INA is the gameday inactive list (90 min pre-kickoff). Used only for the forward candidate set, never as a backtest feature. |
| depth charts | 2012-2026 | 1689644 | retrospective | 2012-2024 weekly NFL depth charts without timestamps (retrospective). 2025+ are ESPN daily snapshots with a 'dt' timestamp (archived). Not used in models (only 2 archived seasons). |
| Next Gen Stats (passing/rushing/receiving) | all | 27613 | reconstructable | 2016+ weekly aggregates (separation, cushion). Downloaded, not used in these models (not evaluated here). |
| players / rosters / crosswalk | all | 24854 | reconstructable | IDs, rookie season, draft round (draft round is pregame). gsis<->pfr crosswalk built by nfl_edge/data/ids.py. |
| play-by-play | 1999-2026 | 0 | reconstructable | Not downloaded for this study (team totals from stats_team suffice); available from the pbp release if drive-level pace is needed. |
| pbp participation (routes, personnel) | 2016-2025 | 0 | reconstructable | Not downloaded. research/opportunity found route/role shares improve target and carry projection as extra regressors (7/7 seasons) but not on the Kalshi-listed population (research/listed_validation) — priority candidate. |
| archived pregame incumbent projections (shadow ledger) | 2026 | 2 | archived | Week-1 2026 ledger in this checkout; later weeks on the market-data branch. Not needed: the incumbent was replayed walk-forward with its own code (nfl/incumbent.py). |
| pregame timestamped injury/availability vintages | 2026 only | 0 | archived | Sleeper/ESPN captures on the market-data branch (context-capture.yml) start in 2026: too short for a backtest. Historical seasons have no timestamped vintage -> missing. |


## Model comparison by family (validation 2022-2023)

Sorted by validation CRPS. dist = distribution family chosen for that mean model on validation (fitted on development residuals). PIT var = variance of the randomised PIT relative to uniform (1 = calibrated, >1 over-confident). ★ = frozen winner.

### team_pass_attempts

*Unit:* team-game. *Population:* every regular-season team-game. *Opportunity family:* —. *Readiness:* **READY** — F_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.97, 80% coverage 0.81, no subgroup with >25% relative bias.

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F (stack) ★ | nb_binned | 1086 | 6.079 | 7.611 | 0.449 | 4.257 | 0.829 | 0.950 | -0.0589 [-0.1049, -0.0101] ✔ | — | — |
| D (C + opponent + game env) | nb_binned | 1086 | 6.085 | 7.630 | 0.571 | 4.265 | 0.829 | 0.950 | -0.0511 [-0.0974, +0.0004] | — | — |
| D_opp (opponent only) | nb_binned | 1086 | 6.136 | 7.677 | 0.623 | 4.288 | 0.839 | 0.960 | -0.0280 [-0.0723, +0.0162] | — | — |
| B (EWMA, shrunk) | nb | 1086 | 6.184 | 7.707 | 0.629 | 4.312 | 0.824 | 0.970 | -0.0035 [-0.0383, +0.0332] | — | — |
| A (season avg, shrunk) | empirical_ratio | 1086 | 6.194 | 7.707 | 0.732 | 4.316 | 0.834 | 0.960 | — | — | — |
| C (opportunity x efficiency) | nb | 1086 | 6.200 | 7.729 | 0.614 | 4.325 | 0.829 | 0.970 | +0.0089 [-0.0304, +0.0485] | — | — |
| E (LightGBM walk-forward) | empirical_ratio | 1086 | 6.204 | 7.737 | 0.000 | 4.326 | 0.831 | 0.960 | +0.0100 [-0.0495, +0.0682] | — | — |

Team pass volume is barely spread-dependent in aggregate (2016-21: 34.0 attempts as a 7+ point dog vs 34.6 as a 7+ favourite); the gain comes from the schedule-adjusted opponent factor (D_opp - B -0.0245 [-0.0467, +0.0006]) and the total.

### team_rush_attempts

*Unit:* team-game. *Population:* every regular-season team-game. *Opportunity family:* —. *Readiness:* **READY** — F_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 1.00, 80% coverage 0.80, no subgroup with >25% relative bias.

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F (stack) ★ | nb_binned | 1086 | 5.867 | 7.311 | -0.135 | 4.137 | 0.785 | 1.020 | -0.0732 [-0.1200, -0.0232] ✔ | — | — |
| D (C + opponent + game env) | nb_binned | 1086 | 5.879 | 7.331 | -0.139 | 4.147 | 0.787 | 1.030 | -0.0633 [-0.1083, -0.0112] ✔ | — | — |
| D_opp (opponent only) | nb_binned | 1086 | 5.911 | 7.363 | -0.209 | 4.167 | 0.791 | 1.030 | -0.0436 [-0.0901, +0.0036] | — | — |
| E (LightGBM walk-forward) | nb_binned | 1086 | 5.937 | 7.358 | -0.114 | 4.167 | 0.789 | 1.010 | -0.0435 [-0.1025, +0.0193] | — | — |
| C (opportunity x efficiency) | nb | 1086 | 5.995 | 7.431 | -0.096 | 4.207 | 0.791 | 1.030 | -0.0032 [-0.0206, +0.0145] | — | — |
| A (season avg, shrunk) | nb_binned | 1086 | 5.976 | 7.435 | -0.273 | 4.210 | 0.795 | 1.020 | — | — | — |
| B (EWMA, shrunk) | nb_binned | 1086 | 5.994 | 7.438 | -0.210 | 4.211 | 0.794 | 1.030 | +0.0008 [-0.0155, +0.0167] | — | — |

Game script matters for rushing: 24.4 rush attempts as a 7+ dog vs 28.5 as a 7+ favourite (2016-21). D - D_opp -0.0197 [-0.0432, +0.0026].

### team_points

*Unit:* team-game. *Population:* every regular-season team-game. *Opportunity family:* —. *Readiness:* **READY** — F_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.97, 80% coverage 0.80, no subgroup with >25% relative bias. Mean is essentially the closing implied team total (stack weight on the market-driven D rung).

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| closing implied team total | normal_binned | 1086 | 7.117 | 9.007 | -0.063 | 5.044 | 0.808 | 0.960 | -0.2220 [-0.3073, -0.1360] ✔ | — | — |
| F (stack) ★ | normal_binned | 1086 | 7.123 | 9.015 | -0.028 | 5.049 | 0.806 | 0.960 | -0.2173 [-0.3053, -0.1306] ✔ | — | — |
| D (C + opponent + game env) | normal_binned | 1086 | 7.125 | 9.017 | -0.100 | 5.049 | 0.808 | 0.960 | -0.2167 [-0.3049, -0.1309] ✔ | — | — |
| E (LightGBM walk-forward) | nb | 1086 | 7.355 | 9.267 | 1.195 | 5.166 | 0.795 | 0.990 | -0.0998 [-0.1967, -0.0021] ✔ | — | — |
| D_opp (opponent only) | nb | 1086 | 7.377 | 9.278 | 0.651 | 5.198 | 0.786 | 1.020 | -0.0682 [-0.1211, -0.0122] ✔ | — | — |
| C (opportunity x efficiency) | empirical_resid | 1086 | 7.406 | 9.351 | 0.221 | 5.230 | 0.805 | 0.960 | -0.0355 [-0.1018, +0.0333] | — | — |
| B (EWMA, shrunk) | nb | 1086 | 7.468 | 9.404 | 0.648 | 5.262 | 0.786 | 1.020 | -0.0037 [-0.0293, +0.0211] | — | — |
| A (season avg, shrunk) | nb | 1086 | 7.451 | 9.403 | 0.591 | 5.266 | 0.777 | 1.020 | — | — | — |

The closing implied total is the information: D (B x opponent x implied/B) has elasticity ~1.05 on the implied total; MKT - D -0.0053 [-0.0121, +0.0011]. Treat as a sanity anchor, not an independent forecast.

### targets

*Unit:* player-game. *Population:* RB/WR/TE who played, mean >= 2 targets over their previous 4 games played (PIT). *Opportunity family:* —. *Readiness:* **READY** — F_plus_availability beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.98, 80% coverage 0.81, no subgroup with >25% relative bias.

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F + availability (vacated + own Questionable) ★ | nb_binned | 6373 | 2.014 | 2.566 | 0.121 | 1.384 | 0.806 | 0.990 | -0.0688 [-0.0802, -0.0573] ✔ | -0.1292 [-0.1460, -0.1126] ✔ | -0.0785 [-0.0901, -0.0667] ✔ |
| E (LightGBM walk-forward) | nb_binned | 6373 | 2.009 | 2.569 | 0.080 | 1.385 | 0.806 | 0.990 | -0.0683 [-0.0804, -0.0561] ✔ | -0.1287 [-0.1457, -0.1120] ✔ | -0.0780 [-0.0900, -0.0654] ✔ |
| F (stack) | nb_binned | 6373 | 2.012 | 2.569 | 0.086 | 1.386 | 0.806 | 0.990 | -0.0674 [-0.0787, -0.0562] ✔ | -0.1279 [-0.1443, -0.1114] ✔ | -0.0771 [-0.0888, -0.0651] ✔ |
| F + vacated opportunity | nb_binned | 6373 | 2.018 | 2.570 | 0.147 | 1.386 | 0.806 | 0.990 | -0.0674 [-0.0786, -0.0559] ✔ | -0.1278 [-0.1443, -0.1109] ✔ | -0.0771 [-0.0883, -0.0648] ✔ |
| F + oracle availability (bound) | nb_binned | 6373 | 2.020 | 2.571 | 0.153 | 1.386 | 0.806 | 0.990 | -0.0668 [-0.0783, -0.0552] ✔ | -0.1273 [-0.1444, -0.1102] ✔ | -0.0765 [-0.0882, -0.0641] ✔ |
| D + availability (vacated + own Questionable) | nb_binned | 6373 | 2.082 | 2.636 | 0.159 | 1.430 | 0.800 | 1.000 | -0.0234 [-0.0325, -0.0136] ✔ | -0.0839 [-0.0997, -0.0677] ✔ | -0.0331 [-0.0436, -0.0226] ✔ |
| D (C + opponent + game env) | nb_binned | 6373 | 2.081 | 2.638 | 0.124 | 1.431 | 0.799 | 1.000 | -0.0219 [-0.0309, -0.0129] ✔ | -0.0824 [-0.0982, -0.0667] ✔ | -0.0316 [-0.0418, -0.0211] ✔ |
| C (opportunity x efficiency) | nb_binned | 6373 | 2.081 | 2.640 | 0.128 | 1.432 | 0.800 | 1.000 | -0.0215 [-0.0306, -0.0131] ✔ | -0.0819 [-0.0974, -0.0667] ✔ | -0.0312 [-0.0411, -0.0216] ✔ |
| B (EWMA, shrunk) | nb_binned | 6373 | 2.074 | 2.637 | 0.099 | 1.432 | 0.801 | 1.000 | -0.0211 [-0.0288, -0.0137] ✔ | -0.0815 [-0.0962, -0.0679] ✔ | -0.0308 [-0.0398, -0.0223] ✔ |
| D + oracle availability (bound) | nb_binned | 6373 | 2.087 | 2.642 | 0.178 | 1.432 | 0.800 | 1.000 | -0.0210 [-0.0302, -0.0119] ✔ | -0.0814 [-0.0976, -0.0655] ✔ | -0.0307 [-0.0413, -0.0198] ✔ |
| D + vacated opportunity | nb_binned | 6373 | 2.088 | 2.642 | 0.194 | 1.432 | 0.798 | 1.000 | -0.0208 [-0.0300, -0.0111] ✔ | -0.0813 [-0.0974, -0.0652] ✔ | -0.0305 [-0.0412, -0.0196] ✔ |
| A (season avg, shrunk) | nb_binned | 6373 | 2.094 | 2.663 | 0.017 | 1.453 | 0.797 | 1.000 | — | -0.0604 [-0.0762, -0.0459] ✔ | -0.0097 [-0.0207, -0.0002] ✔ |
| challenger shadow-0.5.0 | incumbent_own | 6373 | 2.099 | 2.704 | -0.041 | 1.463 | 0.803 | 0.990 | +0.0097 [+0.0002, +0.0207] ✘ | -0.0507 [-0.0600, -0.0421] ✔ | — |
| incumbent shadow-0.4.0 | incumbent_own | 6373 | 2.202 | 2.949 | -0.194 | 1.514 | 0.792 | 1.000 | +0.0604 [+0.0459, +0.0762] ✘ | — | +0.0507 [+0.0421, +0.0600] ✘ |

E (LightGBM) is the single best rung (E - D -0.0464 [-0.0565, -0.0367] ✔); the opponent term adds nothing for targets (D - C -0.0004 [-0.0024, +0.0018]); the availability rung's gain is not significant for targets (F_av - F -0.0013 [-0.0040, +0.0012]) but is for receptions and receiving yards.

### receptions

*Unit:* player-game. *Population:* RB/WR/TE who played, mean >= 2 targets over their previous 4 games played (PIT). *Opportunity family:* targets. *Readiness:* **READY** — F_plus_availability beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.98, 80% coverage 0.81, no subgroup with >25% relative bias.

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F + availability (vacated + own Questionable) ★ | nb_binned | 6373 | 1.578 | 2.028 | 0.034 | 1.082 | 0.791 | 1.020 | -0.0381 [-0.0460, -0.0306] ✔ | -0.0806 [-0.0938, -0.0680] ✔ | -0.0474 [-0.0566, -0.0387] ✔ |
| F + vacated opportunity | nb_binned | 6373 | 1.581 | 2.030 | 0.049 | 1.083 | 0.791 | 1.020 | -0.0369 [-0.0450, -0.0295] ✔ | -0.0795 [-0.0929, -0.0669] ✔ | -0.0462 [-0.0554, -0.0376] ✔ |
| E (LightGBM walk-forward) | nb_binned | 6373 | 1.575 | 2.032 | -0.002 | 1.084 | 0.792 | 1.020 | -0.0366 [-0.0452, -0.0285] ✔ | -0.0792 [-0.0925, -0.0663] ✔ | -0.0459 [-0.0558, -0.0364] ✔ |
| F (stack) | nb_binned | 6373 | 1.578 | 2.031 | 0.009 | 1.084 | 0.792 | 1.020 | -0.0364 [-0.0442, -0.0292] ✔ | -0.0790 [-0.0923, -0.0666] ✔ | -0.0457 [-0.0547, -0.0371] ✔ |
| D + availability (vacated + own Questionable) | nb_binned | 6373 | 1.616 | 2.060 | 0.077 | 1.105 | 0.788 | 1.020 | -0.0150 [-0.0222, -0.0081] ✔ | -0.0575 [-0.0701, -0.0456] ✔ | -0.0243 [-0.0325, -0.0164] ✔ |
| D (C + opponent + game env) | nb_binned | 6373 | 1.617 | 2.063 | 0.051 | 1.107 | 0.791 | 1.020 | -0.0138 [-0.0205, -0.0070] ✔ | -0.0563 [-0.0686, -0.0449] ✔ | -0.0231 [-0.0308, -0.0150] ✔ |
| D + vacated opportunity | nb_binned | 6373 | 1.622 | 2.065 | 0.098 | 1.107 | 0.788 | 1.020 | -0.0130 [-0.0202, -0.0058] ✔ | -0.0556 [-0.0685, -0.0439] ✔ | -0.0223 [-0.0307, -0.0139] ✔ |
| C (opportunity x efficiency) | nb_binned | 6373 | 1.619 | 2.068 | 0.054 | 1.109 | 0.790 | 1.020 | -0.0115 [-0.0178, -0.0055] ✔ | -0.0540 [-0.0667, -0.0423] ✔ | -0.0208 [-0.0284, -0.0129] ✔ |
| B (EWMA, shrunk) | nb_binned | 6373 | 1.614 | 2.066 | -0.011 | 1.110 | 0.790 | 1.020 | -0.0106 [-0.0161, -0.0054] ✔ | -0.0532 [-0.0654, -0.0423] ✔ | -0.0200 [-0.0272, -0.0133] ✔ |
| A (season avg, shrunk) | nb_binned | 6373 | 1.622 | 2.082 | -0.052 | 1.120 | 0.788 | 1.020 | — | -0.0426 [-0.0549, -0.0310] ✔ | -0.0093 [-0.0173, -0.0020] ✔ |
| challenger shadow-0.5.0 | incumbent_own | 6373 | 1.632 | 2.117 | -0.051 | 1.130 | 0.785 | 1.030 | +0.0093 [+0.0020, +0.0173] ✘ | -0.0332 [-0.0400, -0.0270] ✔ | — |
| incumbent shadow-0.4.0 | incumbent_own | 6373 | 1.703 | 2.289 | -0.155 | 1.163 | 0.772 | 1.050 | +0.0426 [+0.0310, +0.0549] ✘ | — | +0.0332 [+0.0270, +0.0400] ✘ |

Inherits targets; catch rate x opponent factor is a small gain (D - C -0.0023 [-0.0041, -0.0004] ✔).

### receiving_yards

*Unit:* player-game. *Population:* RB/WR/TE who played, mean >= 2 targets over their previous 4 games played (PIT). *Opportunity family:* targets. *Readiness:* **SHADOW VALIDATION** — subgroup failure: team_changed=new team (1st game) bias +6.30 on mean 21.52 (n=506)

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F + availability (vacated + own Questionable) ★ | empirical_ratio | 6373 | 21.112 | 28.149 | 0.436 | 14.395 | 0.804 | 1.000 | -0.3446 [-0.4283, -0.2618] ✔ | -0.3250 [-0.4139, -0.2417] ✔ | -0.3250 [-0.4139, -0.2417] ✔ |
| F + vacated opportunity | empirical_ratio | 6373 | 21.176 | 28.193 | 0.721 | 14.416 | 0.805 | 1.000 | -0.3229 [-0.4053, -0.2426] ✔ | -0.3033 [-0.3876, -0.2221] ✔ | -0.3033 [-0.3876, -0.2221] ✔ |
| F (stack) | empirical_ratio | 6373 | 21.107 | 28.205 | 0.277 | 14.425 | 0.805 | 1.000 | -0.3142 [-0.3969, -0.2342] ✔ | -0.2946 [-0.3813, -0.2167] ✔ | -0.2946 [-0.3813, -0.2167] ✔ |
| E (LightGBM walk-forward) | empirical_ratio | 6373 | 20.991 | 28.406 | -0.422 | 14.479 | 0.807 | 0.990 | -0.2598 [-0.3759, -0.1488] ✔ | -0.2402 [-0.3505, -0.1295] ✔ | -0.2402 [-0.3505, -0.1295] ✔ |
| D + availability (vacated + own Questionable) | empirical_ratio | 6373 | 21.581 | 28.422 | 1.427 | 14.585 | 0.804 | 1.000 | -0.1536 [-0.2399, -0.0758] ✔ | -0.1340 [-0.2260, -0.0509] ✔ | -0.1340 [-0.2260, -0.0509] ✔ |
| D + vacated opportunity | empirical_ratio | 6373 | 21.671 | 28.495 | 1.792 | 14.609 | 0.805 | 1.000 | -0.1297 [-0.2126, -0.0519] ✔ | -0.1101 [-0.1965, -0.0328] ✔ | -0.1101 [-0.1965, -0.0328] ✔ |
| D (C + opponent + game env) | empirical_ratio | 6373 | 21.574 | 28.476 | 1.262 | 14.611 | 0.805 | 0.990 | -0.1275 [-0.2073, -0.0513] ✔ | -0.1079 [-0.1900, -0.0332] ✔ | -0.1079 [-0.1900, -0.0332] ✔ |
| C (opportunity x efficiency) | empirical_ratio | 6373 | 21.642 | 28.569 | 1.286 | 14.660 | 0.803 | 0.990 | -0.0793 [-0.1503, -0.0125] ✔ | -0.0597 [-0.1386, +0.0179] | -0.0597 [-0.1386, +0.0179] |
| incumbent shadow-0.4.0 | incumbent_own | 6373 | 21.428 | 28.615 | -0.002 | 14.720 | 0.806 | 0.980 | -0.0196 [-0.0955, +0.0631] | — | +0.0000 [+0.0000, +0.0000] |
| challenger shadow-0.5.0 | incumbent_own | 6373 | 21.428 | 28.615 | -0.002 | 14.720 | 0.806 | 0.980 | -0.0196 [-0.0955, +0.0631] | +0.0000 [+0.0000, +0.0000] | — |
| B (EWMA, shrunk) | empirical_ratio | 6373 | 21.474 | 28.642 | -0.175 | 14.726 | 0.803 | 0.990 | -0.0132 [-0.0612, +0.0327] | +0.0064 [-0.0795, +0.0855] | +0.0064 [-0.0795, +0.0855] |
| A (season avg, shrunk) | empirical_ratio | 6373 | 21.446 | 28.624 | -0.305 | 14.739 | 0.805 | 0.990 | — | +0.0196 [-0.0631, +0.0955] | +0.0196 [-0.0631, +0.0955] |

Opponent yards-per-target factor helps (D - C -0.0483 [-0.0758, -0.0204] ✔); the stack beats E (F - E -0.0544 [-0.1062, +0.0000]).

### carries

*Unit:* player-game. *Population:* RBs who played, mean >= 4 carries over their previous 4 games played (PIT). *Opportunity family:* —. *Readiness:* **SHADOW VALIDATION** — subgroup failure: team_changed=new team (1st game) bias +2.21 on mean 6.22 (n=181)

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F + availability (vacated + own Questionable) ★ | empirical_ratio | 1964 | 4.125 | 5.214 | 0.226 | 2.855 | 0.810 | 0.980 | -0.3227 [-0.3853, -0.2573] ✔ | -0.2780 [-0.3350, -0.2185] ✔ | -0.2117 [-0.2650, -0.1579] ✔ |
| F + vacated opportunity | empirical_ratio | 1964 | 4.127 | 5.215 | 0.239 | 2.857 | 0.808 | 0.980 | -0.3201 [-0.3827, -0.2568] ✔ | -0.2754 [-0.3317, -0.2155] ✔ | -0.2092 [-0.2624, -0.1553] ✔ |
| F + oracle availability (bound) | empirical_ratio | 1964 | 4.152 | 5.227 | 0.440 | 2.859 | 0.805 | 0.980 | -0.3180 [-0.3780, -0.2504] ✔ | -0.2733 [-0.3279, -0.2143] ✔ | -0.2070 [-0.2591, -0.1538] ✔ |
| F (stack) | empirical_ratio | 1964 | 4.153 | 5.248 | 0.056 | 2.881 | 0.808 | 0.990 | -0.2962 [-0.3553, -0.2358] ✔ | -0.2515 [-0.3036, -0.1958] ✔ | -0.1852 [-0.2317, -0.1356] ✔ |
| E (LightGBM walk-forward) | nb_binned | 1964 | 4.142 | 5.244 | 0.142 | 2.885 | 0.791 | 1.020 | -0.2924 [-0.3564, -0.2253] ✔ | -0.2477 [-0.3057, -0.1885] ✔ | -0.1815 [-0.2386, -0.1224] ✔ |
| D + availability (vacated + own Questionable) | empirical_ratio | 1964 | 4.226 | 5.360 | 0.079 | 2.936 | 0.799 | 0.980 | -0.2412 [-0.2993, -0.1820] ✔ | -0.1965 [-0.2511, -0.1403] ✔ | -0.1302 [-0.1786, -0.0853] ✔ |
| D + vacated opportunity | empirical_ratio | 1964 | 4.228 | 5.361 | 0.097 | 2.937 | 0.797 | 0.980 | -0.2399 [-0.2979, -0.1812] ✔ | -0.1952 [-0.2493, -0.1396] ✔ | -0.1290 [-0.1769, -0.0840] ✔ |
| D + oracle availability (bound) | empirical_ratio | 1964 | 4.258 | 5.374 | 0.290 | 2.948 | 0.800 | 0.980 | -0.2295 [-0.2876, -0.1717] ✔ | -0.1848 [-0.2378, -0.1265] ✔ | -0.1185 [-0.1658, -0.0709] ✔ |
| D (C + opponent + game env) | empirical_ratio | 1964 | 4.260 | 5.401 | -0.112 | 2.969 | 0.798 | 0.980 | -0.2081 [-0.2625, -0.1560] ✔ | -0.1634 [-0.2114, -0.1127] ✔ | -0.0971 [-0.1395, -0.0569] ✔ |
| C (opportunity x efficiency) | empirical_ratio | 1964 | 4.299 | 5.425 | -0.145 | 2.982 | 0.803 | 0.980 | -0.1950 [-0.2509, -0.1425] ✔ | -0.1503 [-0.1964, -0.0980] ✔ | -0.0840 [-0.1238, -0.0414] ✔ |
| B (EWMA, shrunk) | empirical_ratio | 1964 | 4.358 | 5.490 | -0.071 | 3.015 | 0.808 | 1.000 | -0.1624 [-0.2169, -0.1034] ✔ | -0.1176 [-0.1663, -0.0660] ✔ | -0.0514 [-0.0905, -0.0114] ✔ |
| challenger shadow-0.5.0 | incumbent_own | 1964 | 4.364 | 5.605 | -0.115 | 3.066 | 0.803 | 1.000 | -0.1110 [-0.1555, -0.0634] ✔ | -0.0663 [-0.0892, -0.0437] ✔ | — |
| incumbent shadow-0.4.0 | incumbent_own | 1964 | 4.550 | 5.971 | -0.625 | 3.133 | 0.794 | 1.000 | -0.0447 [-0.0924, +0.0101] | — | +0.0663 [+0.0437, +0.0892] ✘ |
| A (season avg, shrunk) | empirical_ratio | 1964 | 4.511 | 5.741 | -0.208 | 3.177 | 0.797 | 0.990 | — | +0.0447 [-0.0101, +0.0924] | +0.1110 [+0.0634, +0.1555] ✘ |

Vacated carries from teammates listed OUT/DOUBTFUL is a real signal (D_vac - D -0.0318 [-0.0499, -0.0152] ✔), unlike targets.

### rushing_yards

*Unit:* player-game. *Population:* RBs who played, mean >= 4 carries over their previous 4 games played (PIT). *Opportunity family:* carries. *Readiness:* **SHADOW VALIDATION** — subgroup failure: team_changed=new team (1st game) bias +12.26 on mean 24.49 (n=181)

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F + availability (vacated + own Questionable) ★ | empirical_ratio | 1964 | 24.238 | 31.468 | 1.493 | 16.610 | 0.804 | 0.960 | -1.0155 [-1.2755, -0.7649] ✔ | -0.4353 [-0.6374, -0.2322] ✔ | -0.4353 [-0.6374, -0.2322] ✔ |
| F + vacated opportunity | empirical_ratio | 1964 | 24.282 | 31.488 | 1.653 | 16.622 | 0.807 | 0.960 | -1.0035 [-1.2574, -0.7564] ✔ | -0.4233 [-0.6219, -0.2265] ✔ | -0.4233 [-0.6219, -0.2265] ✔ |
| F (stack) | empirical_ratio | 1964 | 24.305 | 31.575 | 0.874 | 16.708 | 0.808 | 0.970 | -0.9174 [-1.1545, -0.6736] ✔ | -0.3372 [-0.5146, -0.1620] ✔ | -0.3372 [-0.5146, -0.1620] ✔ |
| D + availability (vacated + own Questionable) | empirical_ratio | 1964 | 24.578 | 31.938 | 1.144 | 16.858 | 0.814 | 0.960 | -0.7681 [-1.0130, -0.5369] ✔ | -0.1879 [-0.3797, -0.0046] ✔ | -0.1879 [-0.3797, -0.0046] ✔ |
| D + vacated opportunity | empirical_ratio | 1964 | 24.618 | 31.953 | 1.321 | 16.871 | 0.809 | 0.960 | -0.7547 [-1.0006, -0.5222] ✔ | -0.1745 [-0.3638, +0.0012] | -0.1745 [-0.3638, +0.0012] |
| E (LightGBM walk-forward) | empirical_ratio | 1964 | 24.483 | 31.918 | 1.651 | 16.940 | 0.808 | 0.960 | -0.6853 [-0.9880, -0.3918] ✔ | -0.1051 [-0.3624, +0.1430] | -0.1051 [-0.3624, +0.1430] |
| D (C + opponent + game env) | empirical_ratio | 1964 | 24.656 | 32.059 | 0.421 | 17.026 | 0.806 | 0.970 | -0.5998 [-0.8229, -0.3713] ✔ | -0.0196 [-0.1877, +0.1519] | -0.0196 [-0.1877, +0.1519] |
| incumbent shadow-0.4.0 | incumbent_own | 1964 | 24.625 | 32.300 | 0.229 | 17.045 | 0.808 | 0.970 | -0.5802 [-0.7452, -0.4149] ✔ | — | +0.0000 [+0.0000, +0.0000] |
| challenger shadow-0.5.0 | incumbent_own | 1964 | 24.625 | 32.300 | 0.229 | 17.045 | 0.808 | 0.970 | -0.5802 [-0.7452, -0.4149] ✔ | +0.0000 [+0.0000, +0.0000] | — |
| C (opportunity x efficiency) | empirical_ratio | 1964 | 24.774 | 32.210 | 0.261 | 17.077 | 0.812 | 0.970 | -0.5482 [-0.7681, -0.3360] ✔ | +0.0320 [-0.1346, +0.1995] | +0.0320 [-0.1346, +0.1995] |
| B (EWMA, shrunk) | empirical_ratio | 1964 | 24.879 | 32.521 | 0.060 | 17.242 | 0.799 | 0.980 | -0.3838 [-0.5444, -0.2271] ✔ | +0.1964 [+0.0663, +0.3379] ✘ | +0.1964 [+0.0663, +0.3379] ✘ |
| A (season avg, shrunk) | empirical_ratio | 1964 | 25.230 | 33.112 | -0.818 | 17.626 | 0.799 | 0.980 | — | +0.5802 [+0.4149, +0.7452] ✘ | +0.5802 [+0.4149, +0.7452] ✘ |

Largest relative gain over the incumbent among yardage families; vacated carries D_vac - D -0.1548 [-0.2338, -0.0841] ✔.

### passing_attempts

*Unit:* player-game. *Population:* the team's starting QB (nflverse schedule starter id; announced pregame). *Opportunity family:* team_pass_attempts. *Readiness:* **SHADOW VALIDATION** — validation gain over baseline A not significant (CI crosses 0) although the frozen winner beat A and the incumbent on the 2024-25 holdout; needs a further untouched season before READY

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F, QB starts-only stack ★ | nb | 1082 | 6.682 | 8.686 | 0.568 | 4.796 | 0.820 | 0.970 | -0.0712 [-0.1482, +0.0057] | -0.0680 [-0.1364, -0.0012] ✔ | -0.1162 [-0.1907, -0.0434] ✔ |
| D, QB starts-only + implied total | empirical_ratio | 1082 | 6.705 | 8.729 | 0.660 | 4.807 | 0.818 | 0.970 | -0.0597 [-0.1438, +0.0259] | -0.0566 [-0.1299, +0.0132] | -0.1047 [-0.1830, -0.0273] ✔ |
| B, QB starts-only | nb | 1082 | 6.769 | 8.733 | 1.004 | 4.818 | 0.822 | 0.950 | -0.0495 [-0.1260, +0.0257] | -0.0463 [-0.1173, +0.0293] | -0.0945 [-0.1757, -0.0147] ✔ |
| A, QB starts-only | empirical_ratio | 1082 | 6.815 | 8.816 | 1.282 | 4.826 | 0.817 | 0.970 | -0.0408 [-0.1124, +0.0302] | -0.0377 [-0.1051, +0.0324] | -0.0858 [-0.1594, -0.0107] ✔ |
| F (stack) | empirical_ratio | 1082 | 6.852 | 8.833 | -1.221 | 4.860 | 0.809 | 0.970 | -0.0069 [-0.0729, +0.0537] | -0.0038 [-0.0559, +0.0462] | -0.0519 [-0.1061, +0.0018] |
| incumbent shadow-0.4.0 | incumbent_own | 1082 | 6.836 | 8.788 | 0.737 | 4.864 | 0.838 | 0.920 | -0.0031 [-0.0499, +0.0432] | — | -0.0482 [-0.0659, -0.0325] ✔ |
| A (season avg, shrunk) | empirical_ratio | 1082 | 6.945 | 8.946 | -1.846 | 4.867 | 0.823 | 0.950 | — | +0.0031 [-0.0432, +0.0499] | -0.0450 [-0.0942, +0.0053] |
| C, QB starts-only | nb | 1082 | 6.851 | 8.865 | 0.937 | 4.882 | 0.823 | 0.960 | +0.0146 [-0.0668, +0.0909] | +0.0178 [-0.0590, +0.0897] | -0.0304 [-0.1120, +0.0445] |
| D (C + opponent + game env) | empirical_ratio | 1082 | 7.174 | 9.191 | -2.166 | 4.894 | 0.818 | 0.960 | +0.0267 [-0.0440, +0.0953] | +0.0299 [-0.0332, +0.0947] | -0.0183 [-0.0802, +0.0477] |
| B (EWMA, shrunk) | empirical_ratio | 1082 | 7.038 | 9.011 | -2.128 | 4.899 | 0.816 | 0.960 | +0.0323 [-0.0208, +0.0860] | +0.0355 [-0.0186, +0.0851] | -0.0127 [-0.0705, +0.0411] |
| challenger shadow-0.5.0 | incumbent_own | 1082 | 6.904 | 8.873 | 0.826 | 4.912 | 0.831 | 0.920 | +0.0450 [-0.0053, +0.0942] | +0.0482 [+0.0325, +0.0659] ✘ | — |
| E (LightGBM walk-forward) | empirical_ratio | 1082 | 6.880 | 8.930 | 0.018 | 4.925 | 0.810 | 0.990 | +0.0582 [-0.0378, +0.1459] | +0.0614 [-0.0161, +0.1355] | +0.0132 [-0.0682, +0.0939] |
| C (opportunity x efficiency) | empirical_ratio | 1082 | 7.197 | 9.214 | -2.136 | 4.951 | 0.818 | 0.970 | +0.0844 [+0.0202, +0.1526] ✘ | +0.0875 [+0.0297, +0.1502] ✘ | +0.0394 [-0.0225, +0.1044] |

QB starts-only fix: D_qs - D -0.0865 [-0.1609, -0.0116] ✔, F_qs - F -0.0642 [-0.1112, -0.0166] ✔. Validation gain over A is not significant (A is a strong baseline for QB volume).

### completions

*Unit:* player-game. *Population:* the team's starting QB (nflverse schedule starter id; announced pregame). *Opportunity family:* passing_attempts. *Readiness:* **READY** — F_qb_starts_env_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.98, 80% coverage 0.81, no subgroup with >25% relative bias.

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F, QB starts-only stack ★ | empirical_ratio | 1082 | 4.714 | 6.086 | 0.210 | 3.375 | 0.805 | 0.990 | -0.0763 [-0.1407, -0.0176] ✔ | -0.0593 [-0.1078, -0.0110] ✔ | -0.0930 [-0.1452, -0.0376] ✔ |
| D, QB starts-only + implied total | empirical_ratio | 1082 | 4.744 | 6.118 | 0.323 | 3.396 | 0.811 | 0.990 | -0.0562 [-0.1175, +0.0023] | -0.0391 [-0.0858, +0.0104] | -0.0728 [-0.1245, -0.0185] ✔ |
| F (stack) | empirical_ratio | 1082 | 4.811 | 6.177 | -0.681 | 3.414 | 0.799 | 0.990 | -0.0373 [-0.0885, +0.0119] | -0.0202 [-0.0631, +0.0232] | -0.0539 [-0.0984, -0.0101] ✔ |
| incumbent shadow-0.4.0 | incumbent_own | 1082 | 4.799 | 6.166 | 0.245 | 3.435 | 0.823 | 0.940 | -0.0171 [-0.0564, +0.0217] | — | -0.0337 [-0.0492, -0.0187] ✔ |
| E (LightGBM walk-forward) | empirical_ratio | 1082 | 4.798 | 6.199 | -0.086 | 3.437 | 0.804 | 0.990 | -0.0151 [-0.0801, +0.0465] | +0.0019 [-0.0506, +0.0561] | -0.0318 [-0.0865, +0.0245] |
| B, QB starts-only | nb | 1082 | 4.808 | 6.181 | 0.554 | 3.438 | 0.800 | 0.970 | -0.0137 [-0.0685, +0.0459] | +0.0033 [-0.0539, +0.0622] | -0.0304 [-0.0934, +0.0360] |
| A, QB starts-only | nb | 1082 | 4.802 | 6.204 | 0.751 | 3.443 | 0.805 | 0.960 | -0.0085 [-0.0575, +0.0463] | +0.0085 [-0.0454, +0.0686] | -0.0252 [-0.0846, +0.0410] |
| A (season avg, shrunk) | empirical_ratio | 1082 | 4.937 | 6.296 | -1.234 | 3.452 | 0.799 | 0.980 | — | +0.0171 [-0.0217, +0.0564] | -0.0166 [-0.0564, +0.0220] |
| challenger shadow-0.5.0 | incumbent_own | 1082 | 4.849 | 6.224 | 0.321 | 3.468 | 0.818 | 0.950 | +0.0166 [-0.0220, +0.0564] | +0.0337 [+0.0187, +0.0492] ✘ | — |
| D (C + opponent + game env) | empirical_ratio | 1082 | 5.036 | 6.401 | -1.388 | 3.472 | 0.814 | 0.990 | +0.0208 [-0.0265, +0.0682] | +0.0378 [-0.0077, +0.0853] | +0.0041 [-0.0441, +0.0527] |
| C, QB starts-only | empirical_ratio | 1082 | 4.855 | 6.262 | 0.583 | 3.476 | 0.799 | 0.990 | +0.0240 [-0.0329, +0.0814] | +0.0410 [-0.0185, +0.1014] | +0.0073 [-0.0521, +0.0702] |
| B (EWMA, shrunk) | empirical_ratio | 1082 | 5.028 | 6.388 | -1.320 | 3.487 | 0.809 | 0.980 | +0.0351 [-0.0051, +0.0729] | +0.0521 [+0.0063, +0.0970] ✘ | +0.0184 [-0.0279, +0.0670] |
| C (opportunity x efficiency) | empirical_ratio | 1082 | 5.088 | 6.456 | -1.380 | 3.506 | 0.814 | 0.990 | +0.0541 [+0.0090, +0.0974] ✘ | +0.0712 [+0.0211, +0.1191] ✘ | +0.0375 [-0.0131, +0.0871] |

QB starts-only fix: F_qs - F -0.0390 [-0.0692, -0.0059] ✔.

### passing_yards

*Unit:* player-game. *Population:* the team's starting QB (nflverse schedule starter id; announced pregame). *Opportunity family:* passing_attempts. *Readiness:* **READY** — F_qb_starts_env_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.99, 80% coverage 0.81, no subgroup with >25% relative bias.

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| incumbent shadow-0.4.0 | incumbent_own | 1082 | 58.140 | 74.025 | 3.764 | 41.446 | 0.818 | 0.940 | -0.7971 [-1.3182, -0.2796] ✔ | — | +0.0000 [+0.0000, +0.0000] |
| challenger shadow-0.5.0 | incumbent_own | 1082 | 58.140 | 74.025 | 3.764 | 41.446 | 0.818 | 0.940 | -0.7971 [-1.3182, -0.2796] ✔ | +0.0000 [+0.0000, +0.0000] | — |
| F, QB starts-only stack ★ | empirical_resid | 1082 | 58.122 | 74.178 | 5.899 | 41.460 | 0.797 | 0.980 | -0.7832 [-1.5115, -0.0155] ✔ | +0.0140 [-0.5926, +0.6522] | +0.0140 [-0.5926, +0.6522] |
| D, QB starts-only + implied total | empirical_resid | 1082 | 58.294 | 74.409 | 6.933 | 41.474 | 0.809 | 0.970 | -0.7685 [-1.5106, -0.0778] ✔ | +0.0286 [-0.6108, +0.6636] | +0.0286 [-0.6108, +0.6636] |
| F (stack) | empirical_resid | 1082 | 59.105 | 75.338 | -6.147 | 42.029 | 0.793 | 0.990 | -0.2135 [-0.8777, +0.4485] | +0.5837 [-0.0380, +1.1980] | +0.5837 [-0.0380, +1.1980] |
| B, QB starts-only | empirical_resid | 1082 | 59.273 | 75.825 | 10.326 | 42.133 | 0.807 | 0.960 | -0.1100 [-0.7706, +0.4886] | +0.6871 [-0.0759, +1.4373] | +0.6871 [-0.0759, +1.4373] |
| A, QB starts-only | empirical_resid | 1082 | 59.646 | 76.054 | 11.698 | 42.151 | 0.813 | 0.950 | -0.0923 [-0.6739, +0.4950] | +0.7049 [-0.0784, +1.4819] | +0.7049 [-0.0784, +1.4819] |
| D (C + opponent + game env) | empirical_resid | 1082 | 60.428 | 76.801 | -11.589 | 42.236 | 0.805 | 0.980 | -0.0064 [-0.5971, +0.5612] | +0.7907 [+0.0933, +1.4383] ✘ | +0.7907 [+0.0933, +1.4383] ✘ |
| A (season avg, shrunk) | empirical_resid | 1082 | 59.386 | 75.752 | -9.982 | 42.243 | 0.819 | 0.950 | — | +0.7971 [+0.2796, +1.3182] ✘ | +0.7971 [+0.2796, +1.3182] ✘ |
| B (EWMA, shrunk) | empirical_resid | 1082 | 60.427 | 76.799 | -10.046 | 42.697 | 0.811 | 0.960 | +0.4537 [-0.0127, +0.9017] | +1.2508 [+0.6059, +1.9207] ✘ | +1.2508 [+0.6059, +1.9207] ✘ |
| C, QB starts-only | empirical_resid | 1082 | 60.064 | 76.721 | 10.699 | 42.698 | 0.800 | 0.970 | +0.4548 [-0.1842, +1.0949] | +1.2520 [+0.4578, +2.0518] ✘ | +1.2520 [+0.4578, +2.0518] ✘ |
| C (opportunity x efficiency) | empirical_resid | 1082 | 61.047 | 77.698 | -11.524 | 42.880 | 0.805 | 0.970 | +0.6371 [+0.1446, +1.1353] ✘ | +1.4342 [+0.7495, +2.1416] ✘ | +1.4342 [+0.7495, +2.1416] ✘ |
| E (LightGBM walk-forward) | empirical_resid | 1082 | 61.018 | 77.356 | 2.667 | 42.948 | 0.791 | 1.010 | +0.7047 [-0.1206, +1.5281] | +1.5018 [+0.7472, +2.2484] ✘ | +1.5018 [+0.7472, +2.2484] ✘ |

QB starts-only + implied-total fix: D_qs - D -0.7621 [-1.3268, -0.2250] ✔; ties the incumbent (F_qs - INC +0.0140 [-0.5926, +0.6522]). Remaining positive bias (+6 to +9 yards) tracks the 2022-25 league-wide fall in passing yards.

### passing_tds

*Unit:* player-game. *Population:* the team's starting QB (nflverse schedule starter id; announced pregame). *Opportunity family:* passing_attempts. *Readiness:* **NEEDS IMPROVEMENT** — frozen winner is significantly worse than the incumbent shadow-0.4.0 on holdout

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| incumbent shadow-0.4.0 | incumbent_own | 1082 | 0.834 | 1.037 | 0.047 | 0.557 | 0.847 | 0.900 | -0.0089 [-0.0163, -0.0020] ✔ | — | +0.0000 [+0.0000, +0.0000] |
| challenger shadow-0.5.0 | incumbent_own | 1082 | 0.834 | 1.037 | 0.047 | 0.557 | 0.847 | 0.900 | -0.0089 [-0.0163, -0.0020] ✔ | +0.0000 [+0.0000, +0.0000] | — |
| D, QB starts-only + implied total ★ | empirical_ratio | 1082 | 0.855 | 1.055 | 0.105 | 0.559 | 0.831 | 0.950 | -0.0066 [-0.0141, +0.0010] | +0.0024 [-0.0048, +0.0096] | +0.0024 [-0.0048, +0.0096] |
| D (C + opponent + game env) | empirical_ratio | 1082 | 0.842 | 1.051 | -0.017 | 0.560 | 0.830 | 0.950 | -0.0055 [-0.0124, +0.0017] | +0.0034 [-0.0034, +0.0107] | +0.0034 [-0.0034, +0.0107] |
| F, QB starts-only stack | empirical_ratio | 1082 | 0.847 | 1.049 | 0.093 | 0.560 | 0.827 | 0.950 | -0.0055 [-0.0131, +0.0028] | +0.0034 [-0.0029, +0.0103] | +0.0034 [-0.0029, +0.0103] |
| F (stack) | poisson | 1082 | 0.837 | 1.046 | 0.002 | 0.563 | 0.835 | 0.920 | -0.0034 [-0.0103, +0.0039] | +0.0056 [-0.0010, +0.0121] | +0.0056 [-0.0010, +0.0121] |
| A (season avg, shrunk) | poisson | 1082 | 0.843 | 1.052 | -0.002 | 0.566 | 0.844 | 0.920 | — | +0.0089 [+0.0020, +0.0163] ✘ | +0.0089 [+0.0020, +0.0163] ✘ |
| C (opportunity x efficiency) | poisson | 1082 | 0.849 | 1.057 | 0.000 | 0.569 | 0.835 | 0.930 | +0.0030 [-0.0025, +0.0087] | +0.0119 [+0.0034, +0.0209] ✘ | +0.0119 [+0.0034, +0.0209] ✘ |
| E (LightGBM walk-forward) | empirical_ratio | 1082 | 0.850 | 1.062 | 0.051 | 0.570 | 0.828 | 0.930 | +0.0037 [-0.0070, +0.0146] | +0.0126 [+0.0053, +0.0206] ✘ | +0.0126 [+0.0053, +0.0206] ✘ |
| B (EWMA, shrunk) | poisson | 1082 | 0.851 | 1.058 | 0.015 | 0.570 | 0.836 | 0.930 | +0.0038 [-0.0018, +0.0096] | +0.0128 [+0.0040, +0.0219] ✘ | +0.0128 [+0.0040, +0.0219] ✘ |
| B, QB starts-only | empirical_ratio | 1082 | 0.872 | 1.070 | 0.133 | 0.572 | 0.822 | 0.950 | +0.0062 [-0.0012, +0.0144] | +0.0151 [+0.0058, +0.0252] ✘ | +0.0151 [+0.0058, +0.0252] ✘ |
| C, QB starts-only | empirical_ratio | 1082 | 0.872 | 1.069 | 0.136 | 0.573 | 0.831 | 0.940 | +0.0069 [-0.0004, +0.0150] | +0.0158 [+0.0062, +0.0255] ✘ | +0.0158 [+0.0062, +0.0255] ✘ |
| A, QB starts-only | empirical_ratio | 1082 | 0.883 | 1.071 | 0.145 | 0.574 | 0.832 | 0.930 | +0.0080 [+0.0011, +0.0145] ✘ | +0.0170 [+0.0076, +0.0262] ✘ | +0.0170 [+0.0076, +0.0262] ✘ |

No rung separates from the others (D_qs - D -0.0011 [-0.0050, +0.0028]); the incumbent's OLS on implied total is better on holdout.

### anytime_td

*Unit:* player-game. *Population:* RB/WR/TE who played with >= 2 targets or >= 4 carries per game over their previous 4 games (PIT). *Opportunity family:* touches. *Readiness:* **SHADOW VALIDATION** — subgroup failure: team_changed=new team (1st game) bias +0.07 on mean 0.14 (n=607)

| Model | dist | n | MAE | RMSE | Bias | CRPS | cover80 | PIT var | vs A (CRPS) | vs shadow-0.4.0 | vs shadow-0.5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F + availability (vacated + own Questionable) ★ | bernoulli | 7118 | 0.330 | 0.401 | 0.011 | 0.161 | 0.803 | 0.980 | -0.0055 [-0.0070, -0.0040] ✔ | -0.0000 [-0.0009, +0.0008] | -0.0000 [-0.0009, +0.0008] |
| incumbent shadow-0.4.0 | incumbent_own | 7118 | 0.325 | 0.401 | 0.003 | 0.161 | 0.799 | 1.000 | -0.0054 [-0.0069, -0.0040] ✔ | — | +0.0000 [+0.0000, +0.0000] |
| challenger shadow-0.5.0 | incumbent_own | 7118 | 0.325 | 0.401 | 0.003 | 0.161 | 0.799 | 1.000 | -0.0054 [-0.0069, -0.0040] ✔ | +0.0000 [+0.0000, +0.0000] | — |
| F (stack) | bernoulli | 7118 | 0.330 | 0.402 | 0.011 | 0.161 | 0.803 | 0.990 | -0.0053 [-0.0067, -0.0039] ✔ | +0.0001 [-0.0007, +0.0010] | +0.0001 [-0.0007, +0.0010] |
| F + vacated opportunity | bernoulli | 7118 | 0.331 | 0.402 | 0.014 | 0.161 | 0.804 | 0.980 | -0.0053 [-0.0068, -0.0038] ✔ | +0.0001 [-0.0007, +0.0010] | +0.0001 [-0.0007, +0.0010] |
| D + availability (vacated + own Questionable) | bernoulli | 7118 | 0.331 | 0.402 | 0.013 | 0.162 | 0.801 | 0.990 | -0.0048 [-0.0062, -0.0033] ✔ | +0.0007 [-0.0003, +0.0016] | +0.0007 [-0.0003, +0.0016] |
| D (C + opponent + game env) | bernoulli | 7118 | 0.331 | 0.402 | 0.012 | 0.162 | 0.801 | 0.990 | -0.0046 [-0.0060, -0.0032] ✔ | +0.0008 [-0.0000, +0.0018] | +0.0008 [-0.0000, +0.0018] |
| D + vacated opportunity | bernoulli | 7118 | 0.332 | 0.403 | 0.015 | 0.162 | 0.802 | 0.980 | -0.0046 [-0.0060, -0.0031] ✔ | +0.0009 [-0.0000, +0.0018] | +0.0009 [-0.0000, +0.0018] |
| E (LightGBM walk-forward) | bernoulli | 7118 | 0.327 | 0.403 | 0.007 | 0.162 | 0.798 | 1.000 | -0.0043 [-0.0062, -0.0025] ✔ | +0.0011 [-0.0002, +0.0024] | +0.0011 [-0.0002, +0.0024] |
| C (opportunity x efficiency) | bernoulli | 7118 | 0.337 | 0.404 | 0.019 | 0.163 | 0.804 | 0.980 | -0.0036 [-0.0050, -0.0023] ✔ | +0.0018 [+0.0008, +0.0028] ✘ | +0.0018 [+0.0008, +0.0028] ✘ |
| B (EWMA, shrunk) | bernoulli | 7118 | 0.331 | 0.407 | -0.000 | 0.166 | 0.799 | 1.000 | -0.0009 [-0.0017, -0.0002] ✔ | +0.0045 [+0.0031, +0.0060] ✘ | +0.0045 [+0.0031, +0.0060] ✘ |
| A (season avg, shrunk) | bernoulli | 7118 | 0.327 | 0.408 | -0.011 | 0.167 | 0.794 | 1.010 | — | +0.0054 [+0.0040, +0.0069] ✘ | +0.0054 [+0.0040, +0.0069] ✘ |

All structured rungs are within noise of the incumbent's direct binary model (F_av vs incumbent -0.0000 [-0.0009, +0.0008]).

## Holdout (2024-2025, frozen winners, evaluated once) and the read-only 2026 weeks 1-4 check

F on holdout uses the pre-declared stack refitted on development+validation predictions. Incumbent columns are the replayed incumbents scored with their own pmfs on the same rows.

| family | split | model | n | MAE | Bias | CRPS | A CRPS | vs A | 0.4.0 CRPS | vs 0.4.0 | vs 0.5.0 | cover80 | PIT var |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| team_pass_attempts | holdout | F (stack) | 1088 | 6.130 | 1.091 | 4.301 | 4.361 | -0.0600 [-0.1038, -0.0177] ✔ | — | — | — | 0.805 | 0.970 |
| team_pass_attempts | check2026 | F (stack) | 128 | 6.154 | -0.069 | 4.404 | 4.473 | -0.0695 [-0.1693, +0.0285] | — | — | — | 0.789 | 0.960 |
| team_rush_attempts | holdout | F (stack) | 1088 | 5.736 | -0.039 | 4.008 | 4.109 | -0.1018 [-0.1461, -0.0600] ✔ | — | — | — | 0.804 | 1.000 |
| team_rush_attempts | check2026 | F (stack) | 128 | 5.419 | 0.036 | 3.778 | 3.704 | +0.0748 [-0.0522, +0.1938] | — | — | — | 0.844 | 0.930 |
| team_points | holdout | F (stack) | 1088 | 7.167 | -0.662 | 5.062 | 5.414 | -0.3516 [-0.4531, -0.2590] ✔ | — | — | — | 0.800 | 0.970 |
| team_points | check2026 | F (stack) | 128 | 7.381 | -0.617 | 5.120 | 5.522 | -0.4019 [-0.6508, -0.1491] ✔ | — | — | — | 0.844 | 0.980 |
| targets | holdout | F + availability (vacated + own Questionable) | 6160 | 1.996 | 0.171 | 1.373 | 1.456 | -0.0828 [-0.0956, -0.0718] ✔ | 1.496 | -0.1231 [-0.1409, -0.1073] ✔ | -0.0837 [-0.0963, -0.0723] ✔ | 0.810 | 0.980 |
| targets | check2026 | F + availability (vacated + own Questionable) | 743 | 2.105 | 0.068 | 1.448 | 1.548 | -0.1002 [-0.1330, -0.0700] ✔ | 1.634 | -0.1860 [-0.2398, -0.1342] ✔ | -0.1169 [-0.1529, -0.0819] ✔ | 0.794 | 1.030 |
| receptions | holdout | F + availability (vacated + own Questionable) | 6160 | 1.552 | 0.073 | 1.063 | 1.105 | -0.0429 [-0.0505, -0.0363] ✔ | 1.132 | -0.0690 [-0.0817, -0.0576] ✔ | -0.0447 [-0.0531, -0.0363] ✔ | 0.806 | 0.980 |
| receptions | check2026 | F + availability (vacated + own Questionable) | 743 | 1.623 | 0.039 | 1.110 | 1.165 | -0.0546 [-0.0764, -0.0347] ✔ | 1.220 | -0.1092 [-0.1493, -0.0745] ✔ | -0.0639 [-0.0917, -0.0376] ✔ | 0.795 | 1.010 |
| receiving_yards | holdout | F + availability (vacated + own Questionable) | 6160 | 20.977 | 0.965 | 14.322 | 14.699 | -0.3768 [-0.4491, -0.3061] ✔ | 14.647 | -0.3253 [-0.4058, -0.2523] ✔ | -0.3253 [-0.4058, -0.2523] ✔ | 0.811 | 0.970 |
| receiving_yards | check2026 | F + availability (vacated + own Questionable) | 743 | 21.861 | 0.157 | 14.873 | 15.476 | -0.6027 [-0.8547, -0.3795] ✔ | 15.481 | -0.6084 [-0.8433, -0.3709] ✔ | -0.6084 [-0.8433, -0.3709] ✔ | 0.786 | 1.010 |
| carries | holdout | F + availability (vacated + own Questionable) | 1957 | 3.975 | 0.100 | 2.760 | 3.034 | -0.2742 [-0.3324, -0.2205] ✔ | 2.993 | -0.2332 [-0.2854, -0.1808] ✔ | -0.1793 [-0.2284, -0.1336] ✔ | 0.817 | 0.950 |
| carries | check2026 | F + availability (vacated + own Questionable) | 242 | 3.990 | -0.197 | 2.771 | 3.005 | -0.2343 [-0.3855, -0.0914] ✔ | 3.096 | -0.3249 [-0.4771, -0.1793] ✔ | -0.1532 [-0.2748, -0.0327] ✔ | 0.835 | 0.950 |
| rushing_yards | holdout | F + availability (vacated + own Questionable) | 1957 | 24.258 | -0.326 | 16.765 | 17.503 | -0.7376 [-0.9845, -0.5106] ✔ | 17.008 | -0.2433 [-0.4522, -0.0306] ✔ | -0.2433 [-0.4522, -0.0306] ✔ | 0.807 | 0.970 |
| rushing_yards | check2026 | F + availability (vacated + own Questionable) | 242 | 23.128 | 0.573 | 15.773 | 16.355 | -0.5822 [-1.2629, +0.0460] | 16.043 | -0.2700 [-0.7937, +0.2526] | -0.2700 [-0.7937, +0.2526] | 0.847 | 0.930 |
| passing_attempts | holdout | F, QB starts-only stack | 1050 | 6.777 | 1.194 | 4.821 | 5.017 | -0.1961 [-0.2802, -0.1109] ✔ | 4.956 | -0.1355 [-0.2026, -0.0684] ✔ | -0.1574 [-0.2301, -0.0842] ✔ | 0.804 | 0.990 |
| passing_attempts | check2026 | F, QB starts-only stack | 124 | 7.093 | 0.485 | 5.236 | 5.529 | -0.2932 [-0.4752, -0.1135] ✔ | 5.444 | -0.2080 [-0.3716, -0.0430] ✔ | -0.1837 [-0.3456, -0.0218] ✔ | 0.798 | 0.990 |
| completions | holdout | F, QB starts-only stack | 1050 | 4.685 | 0.556 | 3.336 | 3.472 | -0.1360 [-0.1937, -0.0780] ✔ | 3.426 | -0.0907 [-0.1366, -0.0431] ✔ | -0.1076 [-0.1589, -0.0562] ✔ | 0.806 | 0.980 |
| completions | check2026 | F, QB starts-only stack | 124 | 4.793 | 0.457 | 3.480 | 3.587 | -0.1075 [-0.2185, +0.0017] | 3.603 | -0.1235 [-0.2158, -0.0342] ✔ | -0.1355 [-0.2284, -0.0393] ✔ | 0.815 | 0.980 |
| passing_yards | holdout | F, QB starts-only stack | 1050 | 58.279 | 9.041 | 41.434 | 42.802 | -1.3678 [-2.1312, -0.6495] ✔ | 41.997 | -0.5631 [-1.1936, +0.0871] | -0.5631 [-1.1936, +0.0871] | 0.811 | 0.990 |
| passing_yards | check2026 | F, QB starts-only stack | 124 | 60.717 | 6.274 | 43.655 | 44.576 | -0.9205 [-2.8267, +0.9473] | 43.920 | -0.2645 [-2.0329, +1.5861] | -0.2645 [-2.0329, +1.5861] | 0.790 | 1.040 |
| passing_tds | holdout | D, QB starts-only + implied total | 1050 | 0.927 | 0.026 | 0.619 | 0.631 | -0.0129 [-0.0222, -0.0038] ✔ | 0.606 | +0.0123 [+0.0045, +0.0209] ✘ | +0.0123 [+0.0045, +0.0209] ✘ | 0.792 | 1.030 |
| passing_tds | check2026 | D, QB starts-only + implied total | 124 | 0.884 | 0.012 | 0.596 | 0.614 | -0.0187 [-0.0424, +0.0046] | 0.606 | -0.0104 [-0.0318, +0.0096] | -0.0104 [-0.0318, +0.0096] | 0.782 | 0.960 |
| anytime_td | holdout | F + availability (vacated + own Questionable) | 6965 | 0.343 | -0.007 | 0.172 | 0.179 | -0.0063 [-0.0076, -0.0050] ✔ | 0.174 | -0.0011 [-0.0021, -0.0001] ✔ | -0.0011 [-0.0021, -0.0001] ✔ | 0.798 | 1.010 |
| anytime_td | check2026 | F + availability (vacated + own Questionable) | 850 | 0.335 | 0.005 | 0.165 | 0.173 | -0.0072 [-0.0114, -0.0033] ✔ | 0.167 | -0.0013 [-0.0047, +0.0016] | -0.0013 [-0.0047, +0.0016] | 0.816 | 0.970 |


The 2026 weeks 1-4 check (read-only; never tuned on) agrees in direction with the holdout for every player family; it is too small (124 QB starts, 743 receiving player-games) to be decisive on its own. Team rush attempts were worse than baseline on 2026 weeks 1-4 (not significant), the only sign flip.

## Experiments

### NFL-PF-01-ladder

- **Question:** Which rung of the A..F ladder projects each family best?
- **Hypothesis:** Structured opportunity x efficiency models (C/D) and learned models (E/F) beat shrunk averages (A/B).
- **Method:** Walk-forward: A-D are point-in-time formulas whose few hyperparameters (shrinkage k, EWMA halflife, elasticities) were tuned on 2016-2021; E is LightGBM refitted every season on all earlier seasons; F is a non-negative stack fitted on 2016-2021 predictions. Each model gets its own distribution fitted on its development residuals; validation (2022-23) selects.
- **Data:** nflverse 2012-2025 regular seasons; team_pass_attempts n_val=1086, team_rush_attempts n_val=1086, team_points n_val=1086, targets n_val=6373, receptions n_val=6373, receiving_yards n_val=6373, carries n_val=1964, rushing_yards n_val=1964, passing_attempts n_val=1082, completions n_val=1082, passing_yards n_val=1082, passing_tds n_val=1082, anytime_td n_val=7118
- **Result:** team_pass_attempts: best F (val CRPS 4.2570 vs A 4.3159); team_rush_attempts: best F (val CRPS 4.1370 vs A 4.2102); team_points: best F (val CRPS 5.0486 vs A 5.2659); targets: best F_av (val CRPS 1.3844 vs A 1.4531); receptions: best F_av (val CRPS 1.0822 vs A 1.1203); receiving_yards: best F_av (val CRPS 14.3945 vs A 14.7391); carries: best F_av (val CRPS 2.8547 vs A 3.1774); rushing_yards: best F_av (val CRPS 16.6101 vs A 17.6256); passing_attempts: best F_qs (val CRPS 4.7959 vs A 4.8671); completions: best F_qs (val CRPS 3.3753 vs A 3.4516); passing_yards: best F_qs (val CRPS 41.4598 vs A 42.2430); passing_tds: best D_qs (val CRPS 0.5594 vs A 0.5659); anytime_td: best F_av (val CRPS 0.1611 vs A 0.1665)
- **Interpretation:** See per-family tables. Gains over A are game-clustered paired differences on identical player-games.
- **Decision:** adopt

### NFL-PF-02-opponent

- **Question:** Does a schedule-adjusted opponent factor (rolling ridge, refitted before every week) plus closing spread/total improve player projections beyond opportunity x efficiency?
- **Hypothesis:** D beats C on validation CRPS.
- **Method:** D = C with team volume from the opponent/environment team model and an efficiency elasticity beta on the opponent's ridge factor, beta fitted by Poisson (Bernoulli for TD) likelihood on 2016-2021 only.
- **Data:** validation 2022-2023, paired on identical player-games, games as clusters
- **Result:** D better than C (CI excludes 0) in 6/7 efficiency families, worse in 0/7. receptions: -0.0023 [-0.0041, -0.0004] ✔; receiving_yards: -0.0483 [-0.0758, -0.0204] ✔; rushing_yards: -0.0517 [-0.1205, +0.0206]; completions: -0.0333 [-0.0578, -0.0101] ✔; passing_yards: -0.6435 [-1.0147, -0.2745] ✔; passing_tds: -0.0085 [-0.0142, -0.0030] ✔; anytime_td: -0.0010 [-0.0016, -0.0003] ✔
- **Interpretation:** Negative = D better. Opponent effects in the NFL box score are small relative to player-game noise; the gain, where it exists, is modest.
- **Decision:** adopt

### NFL-PF-03-game-environment

- **Question:** Do the closing spread and total add to the opponent-adjusted team volume projection?
- **Hypothesis:** D (opponent + environment) beats D_opp (opponent only) for team pass/rush attempts and points.
- **Method:** Poisson log-linear elasticities on B (EWMA) fitted on 2016-2021; spread/7 and (total-44)/7 terms; for points log(implied/B).
- **Data:** validation 2022-2023 team-games
- **Result:** team_pass_attempts: D - D_opp -0.0231 [-0.0460, -0.0002] ✔; D_opp - B -0.0245 [-0.0467, +0.0006]; team_rush_attempts: D - D_opp -0.0197 [-0.0432, +0.0026]; D_opp - B -0.0443 [-0.0851, +0.0006]; team_points: D - D_opp -0.1485 [-0.2193, -0.0720] ✔; D_opp - B -0.0644 [-0.1090, -0.0134] ✔
- **Interpretation:** The closing line carries most of the pregame information on team points and rush volume; pass volume is nearly spread-neutral in aggregate (2016-21: 34.0 attempts as a 7+ point underdog vs 34.6 as a 7+ favourite) while rush attempts rise from 24.4 to 28.5.
- **Decision:** adopt

### NFL-PF-04-vacated-opportunity

- **Question:** Do teammates listed OUT/DOUBTFUL on the final injury report explain part of the opportunity error (the mean_defect 'listing/role' residual)?
- **Hypothesis:** Renormalising a player's share for vacated teammate opportunity, share x (1-vacated)^(-gamma), improves targets/carries projections.
- **Method:** vacated = sum of the listed teammates' EWMA target-per-attempt (carry share) among players who appeared in the team's last 3 games; gamma fitted on 2016-2021 (gamma=1 is proportional redistribution). An 'oracle' version uses who actually did not play (post-game) as an upper bound.
- **Data:** 29.0% of player-games have >5% of team targets vacated by listed teammates
- **Result:** gamma(D,targets)=0.29, gamma(D,carries)=0.40; oracle gammas 0.06/0.14. Validation: targets: D_vac-D +0.0011 [-0.0014, +0.0034], F_vac-F +0.0001 [-0.0022, +0.0021], oracle-D +0.0009 [-0.0004, +0.0024]; receptions: D_vac-D +0.0007 [-0.0010, +0.0021], F_vac-F -0.0005 [-0.0019, +0.0007], oracle-D n/a; receiving_yards: D_vac-D -0.0021 [-0.0186, +0.0145], F_vac-F -0.0087 [-0.0235, +0.0061], oracle-D n/a; carries: D_vac-D -0.0318 [-0.0499, -0.0152] ✔, F_vac-F -0.0239 [-0.0405, -0.0100] ✔, oracle-D -0.0214 [-0.0346, -0.0088] ✔; rushing_yards: D_vac-D -0.1548 [-0.2338, -0.0841] ✔, F_vac-F -0.0861 [-0.1584, -0.0237] ✔, oracle-D n/a; anytime_td: D_vac-D +0.0000 [-0.0002, +0.0002], F_vac-F +0.0000 [-0.0002, +0.0002], oracle-D n/a
- **Interpretation:** Injury-report availability is the pregame-legitimate part of the role signal; the oracle bound shows how much better gameday availability information could be worth.
- **Decision:** adopt

### NFL-PF-05-incumbent

- **Question:** How do the frozen winners compare with the incumbent shadow-0.4.0 and the shadow-0.5.0 challenger, replayed walk-forward with their own code?
- **Hypothesis:** The foundation models are at least as accurate as the incumbents.
- **Method:** nfl/incumbent.py replays fit_bundle (seasons 2016..T-1) for T=2017..2026 with the frozen design (0.4.0) and the challenger design (0.5.0, in-memory function swap, no file edits) and scores the incumbents' own pmfs on the same player-games.
- **Data:** validation 2022-2023 and holdout 2024-2025, paired rows present in both
- **Result:** targets: best-vs-0.4.0 -0.1292 [-0.1460, -0.1126] ✔, 0.5.0-0.4.0 -0.0507 [-0.0600, -0.0421] ✔; receptions: best-vs-0.4.0 -0.0806 [-0.0938, -0.0680] ✔, 0.5.0-0.4.0 -0.0332 [-0.0400, -0.0270] ✔; receiving_yards: best-vs-0.4.0 -0.3250 [-0.4139, -0.2417] ✔, 0.5.0-0.4.0 +0.0000 [+0.0000, +0.0000]; carries: best-vs-0.4.0 -0.2780 [-0.3350, -0.2185] ✔, 0.5.0-0.4.0 -0.0663 [-0.0892, -0.0437] ✔; rushing_yards: best-vs-0.4.0 -0.4353 [-0.6374, -0.2322] ✔, 0.5.0-0.4.0 +0.0000 [+0.0000, +0.0000]; passing_attempts: best-vs-0.4.0 -0.0680 [-0.1364, -0.0012] ✔, 0.5.0-0.4.0 +0.0482 [+0.0325, +0.0659] ✘; completions: best-vs-0.4.0 -0.0593 [-0.1078, -0.0110] ✔, 0.5.0-0.4.0 +0.0337 [+0.0187, +0.0492] ✘; passing_yards: best-vs-0.4.0 +0.0140 [-0.5926, +0.6522], 0.5.0-0.4.0 +0.0000 [+0.0000, +0.0000]; passing_tds: best-vs-0.4.0 +0.0024 [-0.0048, +0.0096], 0.5.0-0.4.0 +0.0000 [+0.0000, +0.0000]; anytime_td: best-vs-0.4.0 -0.0000 [-0.0009, +0.0008], 0.5.0-0.4.0 +0.0000 [+0.0000, +0.0000]
- **Interpretation:** Replay note: the research frame includes current-season games, so defect D1 (live history missing this season) does not affect this replay; the comparison is of model design only, which understates the incumbent's live 2026 error.
- **Decision:** adopt

### NFL-PF-06-availability

- **Question:** How much does the participation convention matter, and how well does pregame information predict participation?
- **Hypothesis:** Final injury designations predict DNP well; most DNPs of role players are flagged.
- **Method:** Candidates = role players (>=2 targets or >=4 carries per game) who appeared in one of the team's last 3 games; P(play | designation) fitted on 2016-21; targets CRPS on the full candidate set (DNP = 0) for 'assume he plays' vs the participation hurdle.
- **Data:** validation candidates n=8165
- **Result:** DNP rate 15.8%; Brier designation model 0.0967 vs constant 0.1330; 59% of DNPs carried no designation; among published (not OUT) projections DNP rate 12.2%, CRPS assume-plays 1.457 vs hurdle 1.415
- **Interpretation:** Projections are published conditional on participation (prop void convention); the hurdle is the right object for any consumer that does not void DNPs.
- **Decision:** adopt

## Error investigations (development + validation, frozen winners)

Method: per-segment bias/MAE of the frozen winner on development + validation player-games (`pf_core.metrics.segment_table`), segments defined only from pregame information; causes tested on development, corrections validated on 2022-23.

1. **QB history polluted by non-starts (verified, fixed pre-freeze).** 18% of QB rows are not the scheduled starter (6.5 attempts on average vs 33.1). On 2016-21 starts whose previous 4 games include a non-start, D projected 189.8 passing yards vs 209.9 realised (attempts 27.2 vs 31.4); with clean histories D still under-projected 237.7 vs 247.6, and the gap grew with the implied total (193 vs 193 at <=18 points, 263 vs 278 at 27+). Fix = starts-only history + implied-total elasticity (`nfl/qb_fix.py`).
2. **Playing through a Questionable tag (verified, fixed pre-freeze).** Role players tagged Questionable who play realise 0.91x their projection (availability study, n=1,603); dev-fitted haircuts are 7-12% for receiving volume and 18% on the TD intensity.
3. **Teammate absences (verified for carries, ruled out for targets).** Renormalising for teammates listed OUT/DOUBTFUL helps carries and rushing yards with CIs excluding 0 but not targets: target trees already re-allocate through recent role, and an 'oracle' using who actually sat (post-game) is no better — absent teammates' roles are already absorbed into the others' recent history.
4. **First games with a new team (verified, NOT adopted — found after the freeze).** Over-projection by games with the current team, development / validation: targets k=0 +14% (n=356) / +29% (n=150), k=1 +6% (n=497) / +4% (n=194); receiving yards k=0 +27% (n=356) / +35% (n=150); rushing yards k=0 +37% (n=129) / +99% (n=52); anytime TD k=0 +28% (n=429) / +127% (n=178). Candidate C1 (tenure multipliers fitted on dev) on validation: targets all -0.0017 [-0.0032, -0.0002] ✔, segment -0.0159 [-0.0288, -0.0007] ✔; rushing yards all -0.0902 [-0.1442, -0.0388] ✔, segment -0.7766 [-1.2354, -0.3562] ✔.
5. **Backup tiers regress (verified, NOT adopted).** RB2+/TE2+ targets +13%/+16%, WR3+ +7%: players enter the population after a hot stretch (>= 2 targets over 4 games) and regress. Candidate C2 on validation: targets all -0.0044 [-0.0065, -0.0024] ✔, segment -0.0122 [-0.0178, -0.0065] ✔; receiving yards all -0.0259 [-0.0430, -0.0088] ✔, segment -0.0722 [-0.1234, -0.0161] ✔.
6. **Early season, rookies, QB changes: no material defect.** Weeks 1-3 bias +1% on targets (the incumbent's -11 to -14% early-season gap from mean_defect D2 does not exist in this design); rookies after their first game -2% to +1%; receivers after a QB change +3% targets / +6% receiving yards (minor).
7. **Game script:** projections on 7+ point underdogs run +4-5% high on targets/receiving yards/passing yards; favourites are unbiased. Small, plausibly the spread effect being under-weighted at the player level.

| pattern | frequency | impact | cause | status | action |
|---|---|---|---|---|---|
| targets: early season (weeks 1-3) | n=4791 player-games (dev+val) | bias +0.05 on mean 4.53 (+1%), MAE 2.11 |  | ruled out |  |
| targets: rookies | n=2836 player-games (dev+val) | bias +0.03 on mean 4.18 (+1%), MAE 1.99 |  | ruled out |  |
| targets: first game with a new team | n=506 player-games (dev+val) | bias +0.54 on mean 2.95 (+18%), MAE 2.04 |  | verified defect |  |
| targets: team's starting QB changed | n=2978 player-games (dev+val) | bias +0.11 on mean 4.47 (+3%), MAE 2.12 |  | ruled out |  |
| targets: teammates listed out vacate >25% of targets | n=848 player-games (dev+val) | bias +0.00 on mean 4.77 (+0%), MAE 2.21 |  | ruled out |  |
| carries: RB committees | n=3277 player-games (dev+val) | bias +0.02 on mean 12.16 (+0%), MAE 4.38 |  | ruled out |  |
| carries: change-of-pace RBs | n=3175 player-games (dev+val) | bias +0.30 on mean 6.64 (+5%), MAE 3.81 |  | ruled out |  |
| receiving_yards: WR1s | n=4185 player-games (dev+val) | bias -2.20 on mean 63.52 (-3%), MAE 30.39 |  | ruled out |  |
| receiving_yards: WR3+ | n=5486 player-games (dev+val) | bias +2.13 on mean 25.83 (+8%), MAE 20.67 |  | hypothesis |  |
| targets: played through a Questionable tag | n=1592 player-games (dev+val) | bias +0.03 on mean 4.76 (+1%), MAE 2.15 |  | ruled out |  |
| passing_yards: QB starts after a QB change | n=510 player-games (dev+val) | bias +10.76 on mean 212.76 (+5%), MAE 60.58 |  | hypothesis |  |
| rushing_yards: RBs on 7+ point favourites | n=968 player-games (dev+val) | bias -1.02 on mean 48.40 (-2%), MAE 24.64 |  | ruled out |  |


*targets by tier*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| RB1 | 3757 | 3.960 | 3.940 | -0.020 | -0.6% | 1.940 |
| RB2+ | 2091 | 2.250 | 2.540 | 0.290 | +12.8% | 1.560 |
| TE1 | 3818 | 4.990 | 4.880 | -0.110 | -2.2% | 2.100 |
| TE2+ | 1695 | 2.310 | 2.690 | 0.380 | +16.4% | 1.550 |
| WR1 | 4185 | 7.740 | 7.660 | -0.080 | -1.1% | 2.590 |
| WR2 | 4091 | 5.560 | 5.610 | 0.060 | +1.0% | 2.300 |
| WR3+ | 5486 | 3.380 | 3.620 | 0.240 | +7.2% | 1.940 |

*targets by season_phase*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| wk1-3 | 4791 | 4.530 | 4.580 | 0.050 | +1.0% | 2.110 |
| wk10-18 | 11978 | 4.640 | 4.720 | 0.070 | +1.6% | 2.060 |
| wk4-9 | 8354 | 4.660 | 4.760 | 0.100 | +2.2% | 2.080 |

*targets by career_games*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| 17+ | 20621 | 4.800 | 4.870 | 0.070 | +1.5% | 2.100 |
| 4-8 | 1345 | 3.810 | 3.940 | 0.130 | +3.5% | 1.950 |
| 9-16 | 2431 | 3.940 | 4.010 | 0.070 | +1.8% | 1.970 |
| <=3 | 726 | 3.630 | 3.740 | 0.110 | +3.0% | 1.990 |

*targets by team_changed*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| new team (1st game) | 506 | 2.950 | 3.500 | 0.540 | +18.3% | 2.040 |
| same team | 24617 | 4.660 | 4.730 | 0.070 | +1.5% | 2.070 |

*targets by qb_changed*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| QB changed | 2978 | 4.470 | 4.590 | 0.110 | +2.5% | 2.120 |
| same QB | 22145 | 4.650 | 4.720 | 0.070 | +1.6% | 2.070 |

*targets by vacated_targets*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| 0 | 15642 | 4.590 | 4.680 | 0.090 | +2.0% | 2.060 |
| 0-0.10 | 4497 | 4.670 | 4.750 | 0.080 | +1.8% | 2.080 |
| 0.10-0.25 | 4136 | 4.700 | 4.730 | 0.030 | +0.6% | 2.090 |
| >0.25 | 848 | 4.770 | 4.780 | 0.000 | +0.1% | 2.210 |

*targets by designation*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| None | 23525 | 4.620 | 4.700 | 0.080 | +1.7% | 2.070 |
| Questionable | 1592 | 4.760 | 4.790 | 0.030 | +0.6% | 2.150 |


*carries by rb_role*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| change-of-pace(<.35) | 3175 | 6.640 | 6.950 | 0.300 | +4.6% | 3.810 |
| committee(.35-.6) | 3277 | 12.160 | 12.180 | 0.020 | +0.2% | 4.380 |
| workhorse(cs>=.6) | 1131 | 16.890 | 16.630 | -0.260 | -1.6% | 4.820 |

*carries by spread_bucket*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| dog 3-7 | 1772 | 10.380 | 10.590 | 0.210 | +2.0% | 4.320 |
| dog 7+ | 1033 | 10.240 | 10.410 | 0.170 | +1.7% | 4.050 |
| fav 3-7 | 1505 | 10.920 | 10.840 | -0.080 | -0.7% | 4.170 |
| fav 7+ | 968 | 10.480 | 10.560 | 0.090 | +0.8% | 3.980 |
| pk +-3 | 2305 | 10.640 | 10.730 | 0.090 | +0.9% | 4.310 |

*carries by season_phase*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| wk1-3 | 1411 | 9.910 | 10.260 | 0.340 | +3.5% | 4.220 |
| wk10-18 | 3669 | 10.780 | 10.800 | 0.020 | +0.2% | 4.190 |
| wk4-9 | 2503 | 10.590 | 10.660 | 0.070 | +0.7% | 4.220 |


*receiving_yards by tier*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| RB1 | 3757 | 23.700 | 23.400 | -0.300 | -1.2% | 16.260 |
| RB2+ | 2091 | 12.800 | 15.060 | 2.260 | +17.7% | 12.400 |
| TE1 | 3818 | 36.940 | 35.450 | -1.490 | -4.0% | 21.270 |
| TE2+ | 1695 | 16.800 | 19.670 | 2.870 | +17.1% | 15.040 |
| WR1 | 4185 | 63.520 | 61.320 | -2.200 | -3.5% | 30.390 |
| WR2 | 4091 | 44.080 | 44.170 | 0.090 | +0.2% | 26.460 |
| WR3+ | 5486 | 25.830 | 27.960 | 2.130 | +8.3% | 20.670 |


*passing_yards by qb_changed*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| QB changed | 510 | 212.760 | 223.520 | 10.760 | +5.1% | 60.580 |
| same QB | 3666 | 241.710 | 247.640 | 5.930 | +2.5% | 58.800 |

*passing_yards by career_games*

| segment | n | mean actual | mean proj | bias | rel bias | MAE |
|---|---|---|---|---|---|---|
| 17+ | 3321 | 244.320 | 250.380 | 6.060 | +2.5% | 59.030 |
| 4-8 | 275 | 210.790 | 221.140 | 10.350 | +4.9% | 58.810 |
| 9-16 | 380 | 221.670 | 224.320 | 2.660 | +1.2% | 58.160 |
| <=3 | 200 | 205.150 | 221.320 | 16.180 | +7.9% | 60.730 |


### Targets bias anatomy (mean_defect follow-up)

| split | weeks | usage | n | mean_pred | mean_actual | realised_over_pred |
|---|---|---|---|---|---|---|
| development | wk1-6 | ewm<3 | 1680 | 2.479 | 2.385 | 0.962 |
| development | wk1-6 | ewm3-6 | 3156 | 4.270 | 4.266 | 0.999 |
| development | wk1-6 | ewm6+ | 1961 | 7.358 | 7.267 | 0.988 |
| development | wk7+ | ewm<3 | 3135 | 2.571 | 2.464 | 0.958 |
| development | wk7+ | ewm3-6 | 5517 | 4.401 | 4.318 | 0.981 |
| development | wk7+ | ewm6+ | 3301 | 7.389 | 7.377 | 0.998 |
| validation | wk1-6 | ewm<3 | 636 | 2.421 | 2.110 | 0.872 |
| validation | wk1-6 | ewm3-6 | 1065 | 4.215 | 3.984 | 0.945 |
| validation | wk1-6 | ewm6+ | 609 | 7.438 | 7.506 | 1.009 |
| validation | wk7+ | ewm<3 | 1155 | 2.457 | 2.321 | 0.945 |
| validation | wk7+ | ewm3-6 | 1849 | 4.334 | 4.268 | 0.985 |
| validation | wk7+ | ewm6+ | 1059 | 7.548 | 7.460 | 0.988 |
| check2026 | wk1-6 | ewm<3 | 193 | 2.261 | 2.228 | 0.985 |
| check2026 | wk1-6 | ewm3-6 | 386 | 4.345 | 4.238 | 0.975 |
| check2026 | wk1-6 | ewm6+ | 164 | 7.242 | 7.226 | 0.998 |


research/mean_defect found shadow-0.4.0 under-projecting targets 11-14% in weeks 1-6 and a residual under-prediction on the *listed* (Kalshi) population. On the uncontaminated population used here the frozen model shows realised/projected 0.96-1.00 in weeks 1-6 of 2016-21 and 0.98-1.00 in 2026 weeks 1-4 at every usage tier — no early-season opportunity deficit. The direction is the opposite at low usage (EWMA < 3: realised/projected 0.87-0.96), i.e. regression of fringe players, not missing opportunity. So the remaining listed-population gap in mean_defect is a listing-selection effect (the exchange lists players whose role the box-score history has not yet caught up with), consistent with that study's conclusion; it is not a defect of an opportunity model on representative data. Remedy: a pregame role signal (depth chart vintages, route participation) — see priorities.

## Opponent adjustment

Opponent factors come from pf_core.pit.rolling_ridge_ratings (schedule-adjusted offence/defence ridge, refitted before every week on all earlier games, prior seasons decayed x0.5). Elasticities were fitted on 2016-2021 only. Negative = adjusted model better.

| family | comparison | validation CRPS diff |
|---|---|---|
| team_pass_attempts | D_opp - B | -0.0245 [-0.0467, +0.0006] |
| team_rush_attempts | D_opp - B | -0.0443 [-0.0851, +0.0006] |
| team_points | D_opp - B | -0.0644 [-0.1090, -0.0134] ✔ |
| targets | D - C | -0.0004 [-0.0024, +0.0018] |
| receptions | D - C | -0.0023 [-0.0041, -0.0004] ✔ |
| receiving_yards | D - C | -0.0483 [-0.0758, -0.0204] ✔ |
| carries | D - C | -0.0131 [-0.0260, -0.0002] ✔ |
| rushing_yards | D - C | -0.0517 [-0.1205, +0.0206] |
| passing_attempts | D - C | -0.0577 [-0.0892, -0.0248] ✔ |
| completions | D - C | -0.0333 [-0.0578, -0.0101] ✔ |
| passing_yards | D - C | -0.6435 [-1.0147, -0.2745] ✔ |
| passing_tds | D - C | -0.0085 [-0.0142, -0.0030] ✔ |
| anytime_td | D - C | -0.0010 [-0.0016, -0.0003] ✔ |


Fitted elasticities (1.0 = full pass-through of the schedule-adjusted factor; 0 = no effect):

| family | factors | beta (dev) |
|---|---|---|
| receptions | opp_factor_catch_rate | +0.88 |
| receiving_yards | opp_factor_ypt | +0.82 |
| rushing_yards | opp_factor_ypc | +0.70 |
| completions | opp_factor_comp_pct | +1.03 |
| passing_yards | opp_factor_ypa | +0.88 |
| passing_tds | opp_factor_ptd_rate, _implied_ratio | +0.35, +0.47 |
| anytime_td | implied_ratio, opp_factor_points | +0.81, +0.28 |
| team_pass_attempts | log opp ridge factor, home | +0.58, -0.00 |
| team_rush_attempts | log opp ridge factor, home | +0.90, +0.03 |
| team_points | log opp ridge factor, home | +0.88, +0.07 |


Reading: at the team level the opponent adjustment is worth ~0.5-1% CRPS on volume and the closing line carries most of the points signal. At the player level, opponent efficiency factors help receiving yards and rushing yards modestly and do nothing for targets; elasticities well below 1 say raw opponent splits over-state matchup effects even after schedule adjustment.

## Opportunity model accuracy

| family | best | val MAE | val bias | corr(pred, actual) | val CRPS | vs A |
|---|---|---|---|---|---|---|
| team_pass_attempts | F | 6.079 | 0.449 | 0.341 | 4.257 | -0.0589 [-0.1049, -0.0101] ✔ |
| team_rush_attempts | F | 5.867 | -0.135 | 0.290 | 4.137 | -0.0732 [-0.1200, -0.0232] ✔ |
| targets | F_av | 2.014 | 0.121 | 0.652 | 1.384 | -0.0688 [-0.0802, -0.0573] ✔ |
| carries | F_av | 4.125 | 0.226 | 0.649 | 2.855 | -0.3227 [-0.3853, -0.2573] ✔ |
| passing_attempts | F_qs | 6.682 | 0.568 | 0.335 | 4.796 | -0.0712 [-0.1482, +0.0057] |


Team volume is projected to within ~6 pass attempts and ~5.5 rush attempts MAE; the team volume x share decomposition (C) on its own is no better than a player EWMA (B) for targets, but it is what lets the game environment and opponent enter (D), and as a stack component it carries 15-50% weight.

## Distributions and calibration

Validation CRPS / log score of each candidate family for the winning mean model (lower is better):

| family | mean model | chosen | poisson | nb | nb_binned | empirical_ratio | normal_binned | empirical_resid | bernoulli |
|---|---|---|---|---|---|---|---|---|---|
| team_pass_attempts | F | nb_binned | 4.3240 / 3.531 | 4.2574 / 3.441 | 4.2570 / 3.441 | 4.2591 / 3.601 |  |  |  |
| team_rush_attempts | F | nb_binned | 4.2450 / 3.553 | 4.1371 / 3.404 | 4.1370 / 3.404 | 4.1446 / 3.524 |  |  |  |
| team_points | F | normal_binned | 5.4120 / 4.423 | 5.0712 / 3.674 |  |  | 5.0486 / 3.603 | 5.0558 / 3.634 |  |
| targets | F_av | nb_binned | 1.4028 / 2.293 | 1.3912 / 2.254 | 1.3844 / 2.240 | 1.3865 / 2.257 |  |  |  |
| receptions | F_av | nb_binned | 1.0924 / 2.010 | 1.0859 / 1.986 | 1.0822 / 1.977 | 1.0847 / 1.989 |  |  |  |
| receiving_yards | F_av | empirical_ratio |  |  |  | 14.3945 / 4.449 | 14.8426 / 4.664 | 14.4634 / 4.681 |  |
| carries | F_av | empirical_ratio | 3.0327 / 3.396 | 2.9205 / 3.062 | 2.8686 / 2.982 | 2.8547 / 3.002 |  |  |  |
| rushing_yards | F_av | empirical_ratio |  |  |  | 16.6101 / 4.935 | 17.1226 / 4.836 | 16.6473 / 5.084 |  |
| passing_attempts | F_qs | nb | 4.9073 / 3.911 | 4.7959 / 3.654 | 4.7976 / 3.647 | 4.8069 / 3.752 |  |  |  |
| completions | F_qs | empirical_ratio | 3.4192 / 3.400 | 3.3858 / 3.288 | 3.3856 / 3.279 | 3.3753 / 3.348 |  |  |  |
| passing_yards | F_qs | empirical_resid |  |  |  | 41.4787 / 7.193 | 41.5552 / 5.725 | 41.4598 / 7.285 |  |
| passing_tds | D_qs | empirical_ratio | 0.5654 / 1.410 | 0.5654 / 1.410 | 0.5654 / 1.410 | 0.5594 / 1.401 |  |  |  |
| anytime_td | F_av | bernoulli |  |  |  |  |  |  | 0.1611 / 0.495 |


Holdout reliability at Kalshi-like rungs (frozen winner):

| family | rung | mean P | hit rate | over(+)/under(-) confidence | Brier | ECE |
|---|---|---|---|---|---|---|
| targets | 3+ | 0.692 | 0.680 | +1.2 pp | 0.162 | 0.012 |
| targets | 5+ | 0.448 | 0.425 | +2.2 pp | 0.172 | 0.024 |
| targets | 7+ | 0.258 | 0.238 | +1.9 pp | 0.133 | 0.022 |
| targets | 9+ | 0.133 | 0.125 | +0.9 pp | 0.087 | 0.010 |
| receptions | 3+ | 0.522 | 0.517 | +0.4 pp | 0.195 | 0.010 |
| receptions | 5+ | 0.247 | 0.239 | +0.8 pp | 0.143 | 0.013 |
| receptions | 7+ | 0.098 | 0.092 | +0.6 pp | 0.071 | 0.011 |
| receiving_yards | 40+ | 0.348 | 0.342 | +0.7 pp | 0.173 | 0.011 |
| receiving_yards | 60+ | 0.200 | 0.191 | +0.9 pp | 0.123 | 0.009 |
| receiving_yards | 80+ | 0.109 | 0.104 | +0.5 pp | 0.080 | 0.007 |
| receiving_yards | 100+ | 0.058 | 0.051 | +0.7 pp | 0.044 | 0.007 |
| carries | 10+ | 0.527 | 0.532 | -0.5 pp | 0.152 | 0.018 |
| carries | 15+ | 0.293 | 0.278 | +1.4 pp | 0.145 | 0.028 |
| carries | 20+ | 0.120 | 0.111 | +0.9 pp | 0.085 | 0.015 |
| rushing_yards | 40+ | 0.485 | 0.486 | -0.1 pp | 0.184 | 0.027 |
| rushing_yards | 60+ | 0.303 | 0.315 | -1.2 pp | 0.169 | 0.027 |
| rushing_yards | 80+ | 0.178 | 0.184 | -0.7 pp | 0.129 | 0.015 |
| rushing_yards | 100+ | 0.100 | 0.102 | -0.1 pp | 0.082 | 0.008 |
| passing_attempts | 30+ | 0.600 | 0.571 | +2.9 pp | 0.235 | 0.032 |
| passing_attempts | 35+ | 0.372 | 0.336 | +3.6 pp | 0.215 | 0.038 |
| passing_attempts | 40+ | 0.194 | 0.158 | +3.6 pp | 0.131 | 0.038 |
| completions | 18+ | 0.701 | 0.681 | +2.0 pp | 0.203 | 0.021 |
| completions | 22+ | 0.447 | 0.426 | +2.1 pp | 0.230 | 0.039 |
| completions | 25+ | 0.266 | 0.238 | +2.8 pp | 0.174 | 0.044 |
| passing_yards | 200+ | 0.627 | 0.624 | +0.4 pp | 0.224 | 0.049 |
| passing_yards | 250+ | 0.370 | 0.363 | +0.7 pp | 0.217 | 0.024 |
| passing_yards | 300+ | 0.172 | 0.142 | +3.0 pp | 0.117 | 0.031 |
| passing_tds | 1+ | 0.763 | 0.767 | -0.4 pp | 0.176 | 0.027 |
| passing_tds | 2+ | 0.437 | 0.445 | -0.8 pp | 0.241 | 0.037 |
| passing_tds | 3+ | 0.171 | 0.174 | -0.3 pp | 0.136 | 0.013 |
| anytime_td | 1+ | 0.245 | 0.253 | -0.7 pp | 0.172 | 0.011 |


Distribution choice (validation CRPS, fitted on development residuals): NB with mean-binned dispersion wins for targets and receptions; an empirical ratio (quantile-mapped residual ratios by mean bin) wins for receiving/rushing yards, carries, QB counts and passing TDs; Bernoulli for anytime TD. The discretised normal never wins for yards (it misses the right skew). Over/under-confidence on the holdout is small: PIT variance ratios 0.95-1.03 (slightly under-confident where < 1). Role-specific tails (validation): WR1 100+ receiving yards projected 17.0% vs 19.9% realised (under-confident at the top), workhorse RBs 100+ rushing 24.7% vs 17.8% (over-confident, n=219), backup TEs/RBs at high rungs slightly over-confident (1-2 pp). Projections publish the pmf's own mean: for empirical-ratio families the raw model mean and the pmf mean differ by >5% for 16-32% of rows (mostly low volume), and the pmf mean is the more accurate of the two (receiving yards MAE 21.01 vs 21.11).

## Availability (participation) convention

Convention: player projections are conditional on participation (DNP = void, as props settle). 'Played' is never a feature.
- Role-player candidates (pregame-definable) miss 15.8% of games (validation). Final designations predict it: P(play) Out 0.001, Doubtful 0.017, Questionable 0.729, none 0.878 (development); Brier 0.0967 vs 0.1330 for a constant.
- But 59% of DNPs carry no designation (IR moves, releases, healthy scratches, demotions): the weekly injury report alone cannot produce an unconditional projection. Weekly roster status would catch IR moves but its snapshot time is unknown (retrospective), so it is used only for the forward candidate list.
- Effect of the convention on targets (validation, projections published for everyone not listed OUT, DNP scored as 0): 12.2% of published projections would be voids; assuming participation gives CRPS 1.457 and bias +0.49, the participation hurdle gives 1.415 and -0.10. Consumers that do not void DNPs must use the hurdle.
- Conditional bias: players who play through a Questionable tag realise 0.91x projection (n=1603); adopted as the own-designation term of the availability rung.

## Projection Quality Gate

Every validation and holdout projection of the frozen winners was run through `pf_core.gate.evaluate` with role-aware inputs (own last-8 opportunity and stat history, opponent games this season, final injury designation, the pmf and its rungs). Relative CRPS = CRPS / family mean CRPS (1.0 = average).

- Status rates (published = pmf mean): validation PASS 91.3% / REVIEW 8.7% / BLOCK 0.0%; holdout PASS 93.3% / REVIEW 6.7%.
- Does REVIEW mean larger error? Barely: relative CRPS REVIEW 1.04 vs PASS 1.00 on validation, 0.99 vs 1.00 on holdout. The role/confidence checks are informative for QBs (REVIEW rel CRPS 1.1-1.3) and targets (1.15) but not for the yardage families, where thin-history players are also low-volume players with small absolute errors. Verdict: as an error predictor the gate is weak; it should not be sold as one.
- What the gate did catch: with the raw model mean published, 8.3% of validation projections were BLOCKed for 'distribution mean disagrees with published mean' (empirical-ratio pmfs do not preserve the model mean at low volume). Fixed by publishing the pmf's moments. Team reconciliation caught E/F extrapolating outside their training population: applying the frozen carries model to every participant summed to 1.71x the team's rush attempts (BLOCK in 1060 of 1086 team-games). Population-aware sums (frozen model inside the population, B outside) reconcile at 1.03x (targets) and 1.05x (carries) vs realised 0.99/1.00. Rule adopted: E/F are never published outside their training population.

| family | PASS n | REVIEW n | BLOCK n | REVIEW rel CRPS (val) | REVIEW rel CRPS (holdout) | checks (val) |
|---|---|---|---|---|---|---|
| targets | 5842 | 531 | 0 | 1.070 | 1.010 | injury:REVIEW, role:REVIEW, confidence:REVIEW |
| receptions | 5841 | 532 | 0 | 1.030 | 1.010 | injury:REVIEW, role:REVIEW, confidence:REVIEW, plausibility:REVIEW |
| receiving_yards | 5838 | 535 | 0 | 1.020 | 1.050 | injury:REVIEW, role:REVIEW, confidence:REVIEW, plausibility:REVIEW |
| carries | 1803 | 161 | 0 | 1.020 | 0.960 | injury:REVIEW, role:REVIEW, confidence:REVIEW, plausibility:REVIEW |
| rushing_yards | 1803 | 161 | 0 | 1.020 | 0.850 | injury:REVIEW, role:REVIEW, confidence:REVIEW |
| passing_attempts | 988 | 94 | 0 | 1.200 | 1.180 | role:REVIEW, confidence:REVIEW, injury:REVIEW, plausibility:REVIEW |
| completions | 988 | 94 | 0 | 1.070 | 1.100 | role:REVIEW, confidence:REVIEW, injury:REVIEW, plausibility:REVIEW |
| passing_yards | 988 | 94 | 0 | 1.110 | 1.120 | role:REVIEW, confidence:REVIEW, injury:REVIEW, plausibility:REVIEW |
| passing_tds | 986 | 96 | 0 | 1.090 | 0.860 | role:REVIEW, confidence:REVIEW, injury:REVIEW, plausibility:REVIEW |
| anytime_td | 6404 | 714 | 0 | 1.020 | 0.920 | injury:REVIEW, role:REVIEW, confidence:REVIEW |


## Failed experiments and lessons

- **LightGBM (E) as a stand-alone projection** — E beats the structured D rung only in targets, receptions, receiving_yards, carries; it does not in team_pass_attempts, team_rush_attempts, team_points, rushing_yards, passing_attempts, completions, passing_yards, passing_tds, anytime_td (team families and QB families: too few rows per season for trees). On its own it also extrapolates badly outside its training population (non-RB carries projected 3.4 vs 0.76 realised). *Use trees only inside a stack and only for players inside their training population.*
- **Vacated targets from teammates listed OUT** — gamma fitted on development is positive but validation CRPS does not improve (targets D_vac - D +0.0011 [-0.0014, +0.0034]); the oracle version using who actually sat is no better (+0.0009 [-0.0004, +0.0024]). *Do not spend effort on better absence data for targets; the remaining target error is role (depth chart / routes), not absences. Carries are different (absences matter).*
- **Opportunity x efficiency decomposition (C) on its own** — For targets C - B -0.0004 [-0.0053, +0.0049]: decomposing into team volume x share does not beat a player EWMA (consistent with research/opportunity, which found the same on 2019-2025); its value is structural (it is where game environment and opponent enter). *Keep C/D for interpretability and as stack inputs, not as the headline model.*
- **QB efficiency from the generic ladder (pre-fix)** — Ladder rungs B-D were worse than the season average for QB volume because relief appearances contaminated histories; a seemingly 'robust' EWMA was the problem, not the baseline. *Condition every role-based history on the role (starts for QBs) before smoothing.*
- **Discretised normal for yards / NB on yards** — The normal misses the right skew and loses to empirical ratios in every yards family; 0-based NB cannot represent negative yards and is mis-scored by pf_core's out-of-support clipping. *Empirical (quantile-mapped) residual ratios by mean bin are the default for yards.*

## Readiness and ranked priorities

| family | readiness | why |
|---|---|---|
| team_pass_attempts | READY | F_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.97, 80% coverage 0.81, no subgroup with >25% relative bias. |
| team_rush_attempts | READY | F_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 1.00, 80% coverage 0.80, no subgroup with >25% relative bias. |
| team_points | READY | F_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.97, 80% coverage 0.80, no subgroup with >25% relative bias. Mean is essentially the closing implied team total (stack weight on the market-driven D rung). |
| targets | READY | F_plus_availability beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.98, 80% coverage 0.81, no subgroup with >25% relative bias. |
| receptions | READY | F_plus_availability beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.98, 80% coverage 0.81, no subgroup with >25% relative bias. |
| receiving_yards | SHADOW VALIDATION | subgroup failure: team_changed=new team (1st game) bias +6.30 on mean 21.52 (n=506) |
| carries | SHADOW VALIDATION | subgroup failure: team_changed=new team (1st game) bias +2.21 on mean 6.22 (n=181) |
| rushing_yards | SHADOW VALIDATION | subgroup failure: team_changed=new team (1st game) bias +12.26 on mean 24.49 (n=181) |
| passing_attempts | SHADOW VALIDATION | validation gain over baseline A not significant (CI crosses 0) although the frozen winner beat A and the incumbent on the 2024-25 holdout; needs a further untouched season before READY |
| completions | READY | F_qb_starts_env_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.98, 80% coverage 0.81, no subgroup with >25% relative bias. |
| passing_yards | READY | F_qb_starts_env_stack beats baseline A on validation and holdout (game-clustered 95% CIs exclude 0), holdout PIT variance ratio 0.99, 80% coverage 0.81, no subgroup with >25% relative bias. |
| passing_tds | NEEDS IMPROVEMENT | frozen winner is significantly worse than the incumbent shadow-0.4.0 on holdout |
| anytime_td | SHADOW VALIDATION | subgroup failure: team_changed=new team (1st game) bias +0.07 on mean 0.14 (n=607) |


| rank | item | impact | evidence | complexity | data |
|---|---|---|---|---|---|
| 1 | Adopt the new-team tenure correction (C1) prospectively | first 1-4 games with a new team: 14-37% over-projection removed; family-wide CRPS -0.1% to -0.5% | dev-fitted, validated 2022-23 with CIs excluding 0 in 5/6 families (post-freeze, not yet holdout-tested) | low (one tenure feature + 3 multipliers) | existing nflverse |
| 2 | Adopt the backup-tier regression correction (C2) prospectively | RB2+/TE2+/WR3+ 7-18% over-projection; targets CRPS -0.3% | dev-fitted, validated 2022-23, CIs exclude 0 in 6/6 families | low | existing |
| 3 | Pregame role signal for listed players (archived depth-chart vintages 2025+, route participation) | the remaining opportunity error is role change; mean_defect's listed-population gap (+7%) is a role-selection effect | vacated-target and oracle-absence tests rejected; tenure/backup segments are the largest residuals | medium | ESPN depth chart snapshots (dt-stamped) 2025+, pbp participation (2016-2025) |
| 4 | Passing TDs: add the incumbent's direct implied-total regression as a ladder rung | only family where the incumbent wins on holdout (CRPS +0.012) | holdout vs shadow-0.4.0 | low | existing |
| 5 | Participation model for non-voiding consumers (injury designation + weekly roster status vintages) | 12% of published role-player projections are voids; 58% of DNPs carry no designation | availability study | medium | timestamped roster/injury captures (context-capture.yml, 2026+) |
| 6 | QB passing-yards level drift | +6 to +9 yards holdout bias tracks the 2022-25 league passing decline | holdout bias | low (league-level PIT trend term) | existing |


## Limitations

- Injury designations carry no timestamp in nflverse (rebuilt in place); they are treated as near-pregame (final Friday report). A timestamped vintage exists only from the 2026 context capture. In the forward file, players on the week's report without a final designation yet are marked 'Pending' and gated REVIEW.
- Conditional-on-participation evaluation: a consumer that does not void DNPs must use the participation hurdle (Availability section).
- No route participation / personnel data was used (not downloaded); prior repo research found route share helps raw-EWMA targets.
- The incumbent replay uses the research frame (current-season games included), so it measures the incumbent's design, not the live D1 history defect; its 2026 live error was larger (research/mean_defect). Incumbent pmfs live on 0..grid_max and were left-padded to the family support so negative-yard games are scored correctly.
- pf_core issue (reported, not edited): `DistBatch._index` clips outcomes outside the support to the boundary, so `crps`/`logpmf` understate the loss of out-of-support outcomes (e.g. y=-5 on a 0-based pmf is scored as y=0; y above the support loses the lattice points beyond it). Worked around here by supports down to -20/-30 for yards, by dropping 0-based NB from the yards candidates, and by left-padding the incumbents' pmfs.
- Selection used the minimum validation CRPS among 6-12 candidates per family; several winners beat the runner-up by less than the CI width (see per-family tables). The holdout is the honest estimate.
- 2026 weeks >= 5 are the untouched market holdout and are never scored here; forward projections for them are archived by the workflow.
