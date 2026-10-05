# GAME SCRIPT V2 / five-season study -- preregistration (stage 1)

**Status: RESEARCH_ONLY. Zero betting authority.** Registered on branch `claude/game-script-v2-research`
before any of the evaluations below was run. Starting point: `main` at
`d5c7f8dfa014b9be3aff7550734b6208e7314554`. Every threshold, arm, scoring rule, baseline and decision rule
in this file is fixed here; anything chosen later is labelled POST-HOC wherever it is reported.

Nothing here changes betting authority, production thresholds, staking, incumbent model probabilities,
recommendation authority or reconciliation weights.

## 0. Evidence classes

| class | seasons | why |
|---|---|---|
| RETROSPECTIVE_DEVELOPMENT | 2023, 2024, 2025 | the simulation layer was built and published against these seasons |
| RETROSPECTIVE_CHALLENGE | 2021, 2022 | never scored by this layer before; still retrospective (data, code and every design choice were available) |
| PROSPECTIVE | 2026 | the only prospective evidence; none is claimed in this study |

2021 and 2022 are never called prospective. Every table reports seasons separately before any pooled number.

## 1. Frozen baseline

The incumbent simulation (`sim-1.1.0`, `sim-engine-1.0.0`, `sim-models-1.0.0`, `features-1.0.0`,
`sim-priors-1.0.0`) is run unchanged for evaluation seasons 2021-2025 with the existing walk-forward design
(history start 2016, two warm-up seasons, bundle fitted on seasons 2018..Y-1, priors fitted on 2016..Y-1,
frames rebuilt per evaluation season, consensus closing line as the game centre, 10,000 rows per game,
seed `11 + game index`). The 2023-2025 run is first reproduced from unmodified `main` and compared with the
committed `research/simulation_engine/walkforward.json`; any difference is reported with its cause.

A game the backtest cannot build is never skipped silently: it is counted, listed with the exception, and
the population is reported as unsupported.

## 2. The script lattice (sim-script-2.0.0)

Orientation uses the centre the simulation actually used (`GameInput.spread_home`, expected home margin):

* favourite = home if `spread_home > 0`, away if `spread_home < 0`;
* `spread_home == 0` is PICK'EM: orientation is the home team and labels say "home"/"away", never
  "favourite"/"underdog"; favourite-dependent marginal events are reported as not applicable.

With `fm` = the favourite-oriented final margin of a row and `T` = the centre total:

| dimension | cell | rule |
|---|---|---|
| control | FAVORITE_CONTROL | `fm > 8` |
| control | COMPETITIVE | `-8 <= fm <= 8` (ties included) |
| control | UNDERDOG_CONTROL | `fm < -8` |
| scoring | HIGH_SCORING | `total >= T + 10` |
| scoring | NORMAL_SCORING | otherwise |
| scoring | LOW_SCORING | `total <= T - 10` |

8 = `script_autopsy.ONE_SCORE`; 10 = `script_autopsy.SHOOTOUT_OVER` / `LOW_SCORING_UNDER`. They are imported,
not re-typed. The nine cells are mutually exclusive and exhaustive by construction; a game's probabilities are
row counts divided by the row count. The realized game is classified by the SAME function applied to the
realized final margin (overtime included) and total with the same centre.

NOTE (definition drift, declared): `script_autopsy`'s realized `FAVORITE_CONTROL` label additionally requires
the favourite to lead at half and after Q3. The simulator draws no score path, so the V2 cell is a FINAL-STATE
definition. V2 cells are scored only against V2 realized cells (same function), never against autopsy labels.

Marginal events (may overlap), thresholds from `script_autopsy`:

| event | rule |
|---|---|
| one_score | `abs(margin) <= 8` |
| blowout_17 | `abs(margin) >= 17` |
| favorite_wins | `fm > 0` |
| favorite_controls | `fm > 8` |
| upset | `fm < 0` |
| shootout | `total >= T + 10` |
| low_scoring | `total <= T - 10` |
| low_possession | combined offensive plays `< 115` |
| high_volume_passing | combined pass attempts `>= 80` |
| run_heavy_control | `abs(margin) > 8` and the winner's designed rushes `>= 33` |

Realized volume labels use the team-game table built from play-by-play (`sim.data.team_games`: plays =
run/pass/kneel/spike plays, pass attempts exclude sacks, designed rushes exclude scrambles and kneels), which is
the definition the volume model was trained on and the one `script_autopsy.team_volume_from_pbp` uses.

Labels are generated from the cell and the cell's own quantiles (team codes inserted); no narrative is written
first. Not simulated and therefore never reported: lead changes, time leading, scoring sequence, early
blowout, late comeback.

## 3. Script calibration backtest

For every game of 2021-2025 that the frozen baseline simulates, the nine-cell distribution comes from the SAME
rows that produced the player distributions (a read-only hook in the backtest loop; no extra random draw).

Scores, per season and pooled:

* multiclass Brier `sum_k (p_k - y_k)^2`;
* log loss on smoothed probabilities `(count_k + 0.5) / (n + 4.5)` (a row-count estimate can be exactly 0);
* top-script probability, top-script hit rate, entropy (nats);
* reliability: one-vs-rest probabilities of all nine cells pooled, 10 equal-width bins; ECE
  `sum_b (n_b / N) |mean p_b - freq_b|`;
* predicted vs realized frequency per cell.

Baselines, fitted on TRAINING seasons only (2016..Y-1, every game with a consensus closing line, same cell
function with that game's own closing line), Laplace +1 per cell:

* B0: unconditional nine-cell frequencies;
* B1: nine-cell frequencies conditional on the absolute closing spread bucket `[0,3)`, `[3,7)`, `[7,10)`, `[10,inf)`.

Marginal events are Brier-scored against the same two baselines (B1 = event frequency in the spread bucket).

Inference: 2,000 game-level bootstrap resamples (seed 20261005), 95% percentile interval of the
model-minus-baseline difference. Calibration test: the model's pooled ECE is compared with the ECE
distribution obtained by drawing outcomes FROM the model's own probabilities (2,000 draws, same seed) -- the
spread of ECE a perfectly calibrated forecaster would show on these games.

The simulator's (margin, total) is the market centre plus the incumbent's residual bank, so the nine-cell
lattice is a test of that residual bank, not of the volume or player models. It is expected to be close to
B1. Volume-dependent events (low_possession, high_volume_passing, run_heavy_control) do test the volume model.

Verdict rule for GAME SCRIPT V2 (fixed now):

* READY FOR PROSPECTIVE RESEARCH: every invariant test passes; pooled multiclass Brier better than B0 with a
  95% CI excluding 0; pooled Brier not worse than B1 beyond its 95% CI; pooled ECE inside the 95% range of the
  perfectly-calibrated null; no season individually worse than B0.
* NEEDS MORE WORK: invariants pass but any calibration/baseline condition fails.
* REJECTED: an invariant fails or the model is worse than B0 pooled.

## 4. Script x market matrix (descriptive)

For each supported FULL-period contract (GAME_WINNER, SPREAD, TOTAL, TEAM_TOTAL, PLAYER_STAT with operator
`>=` on a simulated statistic) the per-row cash value uses exactly the pricer's semantics
(`sim.prospective.price_slate`): GAME_WINNER pays 1 on a win and 0.5 on a tie row; SPREAD `x > floor_strike`;
TOTAL / TEAM_TOTAL `x >= threshold`; PLAYER_STAT `clip(round(x), 0, GRID_MAX) >= ceil(threshold)`. Anything
else is refused with a reason.

* material script: `P(s) >= 0.10`; THIN cell: fewer than 200 rows (reported, excluded from the floor);
* major-script floor: min `P(cash | s)` over material, non-thin cells;
* `script_robustness_q = sum P(s)` over cells with `P(cash | s) >= q`, q in {0.50, 0.55, 0.60};
* failure-script mass: `sum P(s)` over cells with `P(cash | s) < 0.50`;
* win-contribution HHI: `sum_s (P(s) P(cash|s) / P(cash))^2`;
* reconciliation identity: `P(cash) = sum_s P(s) P(cash | s)` to floating tolerance.

Thesis dependency, for pairs in one game on the common rows: Pearson correlation of cash values, joint cash
probability, `P(A|B)`, `P(B|A)`, shared failure mass `E[(1-a)(1-b)]`, lift `P(A and B) / (P(A) P(B))`,
Jaccard of winning rows `E[ab] / E[a + b - ab]`. No staking consequence.

## 5. Opponent-adjusted team ratings (separate research arm)

Ratings: for each metric, a weighted ridge on prior team-games `y = mu + off_team + def_opp + h * home + e`,
weights `0.5 ** (weeks_ago / 8) * 0.5 ** seasons_back` (the incumbent's `team_halflife` and
`team_season_carry`), window = the three seasons before the snapshot plus the current season's earlier weeks,
ridge on team effects toward 0 (the prior-window league mean). The ridge strength for evaluation season Y is
chosen per metric from {1, 2, 4, 8, 16, 32} by one-week-ahead squared error of the matchup prediction over
seasons Y-2 and Y-1 only. A snapshot for (season, week) uses games of strictly earlier weeks only; week 1
uses only previous seasons (the carry is explicit: the season discount). `mu` is the weighted mean of the
window, never a statistic of the evaluation season's later games.

Metrics (offence perspective): epa_play, success_rate, dropback_epa, designed_rush_epa, explosive_rate (pass
>= 20 yards or rush >= 10 yards per play), sack_rate (per dropback), plays, sec_per_play (neutral),
neutral_pass_rate, neutral_proe, td_per_drive.

The matchup feature for a team facing an opponent is `mx_<metric> = mu + off_team + def_opp + h * home_sign`.

Arms (each a full walk-forward simulation, 2021-2025, identical seeds):

| arm | change |
|---|---|
| A0 baseline | the frozen incumbent |
| A1 env_adj | plays model + `mx_plays`, `mx_sec_per_play`; pass-rate model + `mx_neutral_pass_rate`, `mx_neutral_proe` |
| A2 eff_adj | carry model + `mx_designed_rush_epa`, `mx_success_rate`, `mx_explosive_rate`; target model + `mx_dropback_epa`, `mx_success_rate`, `mx_explosive_rate` |
| A3 env_eff_adj | A1 + A2 |
| A4 def_join_fix | the volume / TD-split models are trained with the OPPONENT's `def_*` columns (see below) |
| A5 fix_env_adj | A4 + A1 |

A4 comes from the code audit, not from data: `models.fit_game_env` reads `def_plays`, `def_sec_per_play`,
`def_pass_rate`, `def_neutral_pass_rate` and `def_pass_td_share` from the team's OWN team-game row (what its own
defence allowed), while `simulate._team_env_rows` and the TD split serve the OPPONENT's `def_*`. That is a
train/serve skew. It is registered as a candidate, not silently fixed; the incumbent stays as it is unless A4
earns promotion under the rule below.

Primitive diagnostic (reported, not a promotion criterion): one-week-ahead prediction error of each realized
team-game metric from `mx_<metric>` against the incumbent's unadjusted EWMA pair.

## 6. Promotion rule for any projection arm

Primary metric: for the eight statistics carries, rush_yards, targets, receptions, rec_yards, attempts,
completions, pass_yards, the relative CRPS change `CRPS_arm / CRPS_A0 - 1` on the backtest's scored rows; the
primary summary is the mean of the eight relative changes (scale-free). An arm is PROMOTABLE only if ALL hold:

1. the primary summary improves in at least 4 of the 5 seasons;
2. no season's primary summary is worse with a game-clustered 95% CI entirely above 0;
3. pooled, the game-clustered bootstrap 95% CI of the primary summary is entirely below 0;
4. materiality: the pooled improvement is at least 0.5% relative (fixed now; the rushing ablation already
   rejected a 0.2% all-seasons improvement as immaterial, and a 0.5% bar can only make passing harder);
5. calibration: pooled |cover50 - 0.50| and |cover90 - 0.90| averaged over the eight statistics do not worsen
   by more than their bootstrap standard error;
6. breadth: at least 5 of the 8 statistics improve pooled, and dropping the single most-improved statistic
   still leaves the primary summary improved.

Team-level CRPS of plays, pass attempts, rush attempts, dropbacks and targets is reported for every arm.
Failing arms are kept and reported as REJECTED.

## 7. Score-path arm (preregistered; rejected unless it beats its baseline)

Targets, from play-by-play quarter-end scores of held-out games: home leads at half; home leads entering Q4;
early blowout (`abs(margin) >= 17` after Q3 or final, and `abs(half margin) >= 14`); late comeback
(`abs(Q3 margin) >= 7` and the final margin is a tie or the other sign); two or more lead changes; half and Q3
margins (CRPS).

Arm P1 (conditional path bank, no random draw): `P(event) = mean over simulated rows of P(event | final margin,
final total)`, the conditional estimated from training-season games by a margin kernel (Gaussian, bandwidth 3
points; total enters through its centre-relative bucket from section 2). Baseline: the event frequency /
margin distribution in the training games of the same signed closing-spread bucket (`<=-7, (-7,-3], (-3,0),
0, (0,3), [3,7), >=7` in home-margin units). Same bootstrap as section 3. P1 is rejected unless its pooled
Brier (events) and CRPS (margins) beat the baseline with a 95% CI excluding 0. GAME SCRIPT V2 does not depend
on it.

## 8. Weather

Historical: roof is the only pregame weather-like input allowed; observed game-time weather from the schedule
is NON_PIT and may appear only in descriptive tables labelled so. 2026 prospective: kickoff-hour forecast from
the newest vintage retrieved at or before the projection cutoff (`context.weather_vintages.latest_before`),
with retrieval time and lead time. Preregistered prospective hypotheses (no readout in this study): outdoor
games with forecast sustained wind >= 15 mph have (W1) a negative mean total residual against the closing
total and (W2) a negative mean residual of combined pass attempts against the simulation's mean. GAME SCRIPT V2
reports the forecast with `weather_model_status = NOT_IN_MODEL`; weather never alters a probability.

## 9. Injury redistribution (validation, no arm)

Populations (historical designations are the FINAL pregame report -- a documented limitation): teammates of a
depth-chart-1 RB/WR/TE ruled OUT or DOUBTFUL; QUESTIONABLE players themselves; team-games with two or more skill
players OUT/DOUBTFUL; depth-chart-1 players with no prior history; quarterback-starter errors (the simulated
starter is not the player who threw the most passes). Scored: bias, cover50 / cover90 and PIT of carries and
targets, against the rest of the population.

## 10. Stage 2

Player-projection candidates beyond A1-A5 are chosen only after the frozen five-season baseline and its error
decomposition exist, and are registered in an addendum to this file before they are run.

---

# Stage 2 addendum (registered after the frozen baseline's error decomposition, before any arm result was read)

**What the baseline said.** Variance shares of player-game error along TEAM VOLUME -> PLAYER SHARE -> EFFICIENCY
(2021-2024, read before 2025 finished): receptions 60-64% share; rush yards 36-47% share, 37-42% efficiency,
14-17% team volume; passing yards 45-50% share (the starter's share of team attempts), 31-40% team volume. The
simulated QB1 was not the team's leading passer in 7-10% of team-games.

**Candidate considered and NOT registered (negative design result).** A usage-first quarterback-starter rule was
designed on the pre-evaluation seasons 2018-2020 ONLY. Starter identification accuracy there: incumbent
(depth-chart rank, then long-run attempt share) 0.933 / 0.918 / 0.944; short-run attempt share first 0.884 / 0.878
/ 0.877; previous-game share first 0.890 / 0.890 / 0.879; hybrids (switch only when another eligible QB holds
>= 0.5-0.7 of recent attempts and the chart QB1 < 0.5) 0.925 / 0.919 / 0.939-0.946. No variant beats the
incumbent on the design seasons, so none is run on 2021-2025. Recorded so it is not re-tried silently.

**R1 outside_share_repair (registered).** From the reproduction audit: `training.fit_bundle` estimates the share of
team volume that goes outside the eligible set from `assemble`'s per-team-game "first" eligible row after
`fillna(0)`. When that row's player has no player-feature row (today's nflverse rebuild of snap_counts_2020 labels
616 two-way players with compound positions such as `FB/D`), the team's volume reads 0 and the estimate turns
negative (2023 bundle: carry -0.0053, target -0.0046 today vs +0.0055 / +0.0025 committed). R1 takes the team
volume from the team-game row. It is judged by the same section-6 promotion rule as A1-A5.

**Calibration diagnostic added (reporting only, no rule changes).** The incumbent's 50% / 90% coverage counts an
integer outcome on the interval's endpoint as covered, which inflates coverage for small counts. Every
calibration table therefore also reports the RANDOMIZED PIT `F(y-1) + U * p(y)` (U from a fixed seed) computed
from the stored pmf, and its 10-bin chi-square uniformity statistic. The promotion rule (section 6) is unchanged.
