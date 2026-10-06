# GAME SCRIPT V2 — WAVE 2: preregistration

**RESEARCH_ONLY. No candidate in this wave can obtain betting, staking, BET/PASS, price-limit, unit-size,
model-probability or reconciliation-weight authority.** GAME SCRIPT V2 stays displayed in RUN NFL as RESEARCH_ONLY.

Starting point: `main` at `0574cafa8cccd555a2e27ce7dbb6417aa8af867b` (the merge of PR #112). Branch
`research/game-script-v2-wave2`. This file is committed BEFORE any Wave-2 prospective result exists and before any
Wave-2 candidate has been fitted. Everything below that is "chosen on development data" is chosen by the PROCEDURE
written here, so the choice is a deterministic function of seasons <= 2020 and cannot react to any later outcome.
Later addenda may only RECORD the outputs of these procedures (fitted coefficients, the selected form, the computed
minimum sample sizes); they may not change a procedure, a metric, a gate or a subgroup. Any deviation is labelled
DEVIATION with its reason and does not count toward promotion.

## 1. Evidence classes

| class | data | may be used for |
|---|---|---|
| DEVELOPMENT | seasons <= 2020 (pbp from 2016; schedules/lines from 2016) | choosing functional forms, features, regularisation, thresholds, key numbers, sample-size requirements |
| CONTAMINATED_DIAGNOSTIC | 2021-2025, and every 2026 game kicking off before the PROSPECTIVE CUTOFF | mechanism checks and description only -- never cited as validation of a Wave-2 idea, because the ideas came from them |
| PROSPECTIVE | games kicking off after the PROSPECTIVE CUTOFF, with a frozen pre-kickoff record (section 8) | promotion evidence |

**PROSPECTIVE CUTOFF = the committer timestamp of the commit that adds this file.** A game counts as prospective
evidence for an item only if (a) its scheduled kickoff is after the cutoff AND (b) a write-once record for that item
and game exists whose generation time and feature cutoff are both before kickoff. A game without such a record is
missing, not imputed. Model PARAMETERS may be refit on all seasons before a prospective season (training is not
validation); FORMS and procedures may not change.

## 2. S1 — concentration-conditioned opportunity dispersion

Mechanism under test. The incumbent fits one Dirichlet concentration per family by moments,
`Var(y_share) = p(1-p)/(alpha+1)`, on REALISED shares (counts / team volume), and the simulator then draws counts
from a Dirichlet-MULTINOMIAL. The realised share already contains the multinomial noise of `N` team opportunities,
so the multinomial layer is counted twice (variance inflated by `(N+alpha)/N`). And one concentration is used for a
bell-cow back and a five-man committee alike.

Forms (preregistered; nothing else is fitted):

* **S1-0 (N-corrected constant):** one `alpha` per family by maximum Dirichlet-multinomial likelihood of the observed
  COUNT vectors (eligible players + OTHER) given the expected shares.
* **S1-1 (concentration-conditioned):** `log alpha = b0 + b . z(x)` per team-game, same likelihood, ridge 1.0 on the
  standardised coefficients, with exactly these pregame team-game features computed from the expected shares the
  simulator will use: `hhi` (sum p_i^2), `top1` (largest p), `top2` (sum of two largest), `n_meaningful` (count of
  p_i >= 0.05), `other_share`, `entropy` (-sum p log p), `share_no_history` (expected share held by players with no
  prior game), `starter_unavailable` (the team's depth-chart-1 player at a position of this family is not eligible),
  `role_instability` (mean absolute change between the short- and long-half-life prior shares of the team's three
  largest expected shares).

Expected shares are taken from the incumbent share ridge CROSS-FITTED by season (each season's shares predicted by a
ridge fitted on the other training seasons), so `alpha` describes out-of-sample share uncertainty. Expected shares,
team volume, the OTHER bucket and per-row availability are untouched: only the concentration changes, so every
team identity still holds exactly.

Selection procedure (development only): fit both forms on 2018-2019 team-games, score the mean per-team-game
Dirichlet-multinomial log likelihood on 2020. S1 = S1-1 if its 2020 log likelihood exceeds S1-0's by a
game-clustered 95% interval excluding zero; otherwise S1 = S1-0. If neither beats the incumbent constant (evaluated
the same way), S1 is REJECTED_AT_DEVELOPMENT.

Mechanism check (development, full simulation of 2020 with the 2018-2019 bundle): randomized-PIT chi-square and the
edge-bin mass for targets, receptions, receiving yards, carries and rushing yards move toward uniform, and the CRPS of
those five statistics is not worse.

## 3. Q1 — quarterback starter-share regimes

The simulator's quarterback (`inputs._qb1`: depth-chart rank, then long-run attempt share) takes a share of the
team's pass attempts drawn per row; the incumbent tail is fitted only on depth-chart QB1 rows WITH attempts, so the
starter who was active but did not play the expected role never enters it.

Regimes of the simulated QB1's realised share of team pass attempts (thresholds fixed): **FULL** >= 0.90;
**PARTIAL** 0.25-0.90; **LOW** < 0.25 (zero included). Reported separately, never merged:
**IDENTIFICATION ERROR** = the simulated QB1 did not throw his team's first pass; **EXIT / PARTIAL GAME** = he threw
the first pass and finished below 0.90.

Pregame features (fixed list, strictly prior games): `last_game_starter` (threw the team's first pass in its
previous game), `starts_last4` (share of the team's previous four games he started), `questionable`,
`first_start_for_team`, `returning_from_absence` (has prior starts for the team but not in its previous game),
`low_history` (fewer than 100 prior career attempts), `other_viable_qb` (another eligible quarterback started one of
the team's previous four games). No market price is used; no ladder existence is used (H-20260916-028 is a separate,
unread hypothesis).

Model: three-class multinomial logistic, ridge 1.0 on standardised features. Within each regime the share is drawn
from that regime's empirical training quantiles; the game's share distribution is the mixture, sampled with ONE
uniform by inverse CDF (the incumbent's random-number consumption, so every other draw is unchanged). The remainder
goes to the next quarterback on the chart or OTHER exactly as now.

Selection procedure: fit on 2018-2019, multiclass log loss on 2020. Q1 = the conditional model if it beats the
unconditional regime frequencies by a game-clustered interval excluding zero, else Q1 = the unconditional three-regime
mixture (Q1-0). Mechanism check on 2020: lower-decile randomized-PIT mass of attempts / completions / passing yards
moves toward 0.10 without the CRPS of those three worsening by more than 0.5% relative.

In this architecture the team's pass attempts and every receiver's targets do not depend on WHICH quarterback throws;
Q1 must therefore leave receiver distributions unchanged (tested). Downstream receiver effects are not claimed.

## 4. M1 — key-number-aware margin distribution

Candidates (and only these):

* **M1-K (kernel-tilted empirical joint):** draw the (margin, total) of a whole historical game j with weight
  `K(s_j - s; h=2.0) * K(T_j - T; h=4.0) * 0.5^(seasons_ago/3)`, exponentially tilted (two parameters) so the
  simulated mean margin equals the centre `s` and mean total equals `T` exactly; if fewer than 200 effective games
  carry the weight, both bandwidths double until they do. Realised margins and totals keep their integer support, so
  no key number is assumed; overtime is inside the realised results.
* **M1-S (spread-stratified residual bank):** the incumbent residual bank restricted to games whose closing spread is
  within 1.5 points of `s` (widened in 0.5-point steps until 150 games), otherwise identical (overtime and parity
  handling unchanged).

History: seasons 2016..Y-1 (the 2015 extra-point change makes earlier margins a different distribution). Selection:
rolling origin, each of 2018, 2019, 2020 fitted on 2016..Y-1; primary = mean log score of the exact realised margin
(probability floored at 1e-4); tie-break = spread-ladder Brier at home-margin thresholds `s +/- {0.5, ..., 10.5}`.
M1 = the better of M1-K and M1-S if it beats the incumbent bank's log score with a game-clustered interval excluding
zero; else REJECTED_AT_DEVELOPMENT. Key numbers are REPORTED, not imposed: the margins whose 2016-2020 frequency
exceeds a kernel-smoothed (h = 2) version of the same histogram by more than two binomial standard errors.

Coherence requirements (tested): integer home/away points, `home + away = total`, `home - away = margin`, monotone
ladders, mean margin and total equal to the centre within simulation error.

## 5. A1 — information-horizon-correct availability

Horizons (named on every Wave-2 artifact):

* **T24** — no game-day inactive information: a player with weekly-roster status INA is treated as on the active
  roster; QUESTIONABLE keeps the participation discount.
* **T0_INACTIVES** — the inactive list is known: INA players are excluded, and a QUESTIONABLE player who is NOT
  inactive is treated as EXPECTED_ACTIVE (no second questionable discount).
* The incumbent historical backtest is relabelled **T0_GAMEDAY_INACTIVES_WITH_Q_DISCOUNT** -- the inconsistent mix the
  five-season study found.

Prospectively, T0_INACTIVES applies only when the cutoff is at or after kickoff - 90 minutes AND the roster vintage
read at the cutoff carries game-day statuses for that team-week; otherwise T24 applies and the record says why. No
information timestamped after the cutoff may change a pre-cutoff record.

Checks (development 2020, diagnostic 2021-2025): questionable-player carries / targets bias at T0_INACTIVES moves to
zero without degrading teammates' CRPS; T24 is reported as the honest earlier-horizon accuracy and never described as
the T0 number.

## 6. RISK1 — script robustness and thesis concentration (no probability ever changes)

Capture (prediction time, frozen, write-once): the GAME SCRIPT V2 document published every shadow-pricing cycle
(`data/shadow/sim/<day>/<run>.sim-1.1.0.scripts_v2.json.gz` on market-data, merged in PR #112) together with the same
run's projection rows (football / reconciled probability, mid, disagreement). Per contract: P(cash), P(cash | script)
for all nine cells, script probabilities, P50/P55/P60 robustness, major-script floor, failure mass, win-contribution
HHI; script entropy and the primary winning / failing scripts are pure functions of these frozen numbers. From the
Wave-2 merge on, captures within six hours of kickoff also freeze each contract's WORLD FINGERPRINT (its cash value on
the first 1,024 simulated rows), so the dependency of any two contracts -- including positions actually taken -- is
computed from pregame rows, never re-simulated.

Observation unit: for each prospective game, the LAST capture generated before kickoff; every contract there with a
football probability, a script matrix and a two-sided quote. Outcome: the settled result (Kalshi settlement where
recorded, otherwise the box score under the pricer's settlement semantics; both counts reported).

Primary test: logistic regression of the outcome on `logit(mid)`, `logit(p_model)` (reconciled where its deployed
weight is non-zero, else football) and the within-family z-score of P55 robustness, with family fixed effects;
the coefficient on robustness with a 2,000-resample game-clustered bootstrap interval. Robustness "predicts better
outcomes" only if that interval excludes zero in the positive direction. The same model is fitted separately for
major-script floor (+), win-contribution HHI (-) and failure mass (-); Holm correction across the four. Descriptive
companion: within cells of family x model-probability quintile x |p_model - mid| band (<0.03, 0.03-0.08, >0.08), the
mean of (outcome - p_model) for the top versus bottom robustness tercile. No ROI is optimised or used as a criterion.

Secondary (portfolio fragility; descriptive until its own sample requirement is met): for actual positions
(`data/handicap/actual_wagers`, episodes via `handicap/position_lifecycle`), group contracts whose fingerprint Jaccard
of winning rows is >= 0.80 into one thesis; thesis risk share w_i = stake share; `effective_theses = 1 / sum w_i^2`;
also maximum correlated-thesis exposure and shared-failure concentration. Compare left-tail P/L, loss clustering,
drawdown and all-or-nothing game outcomes between slates with equal nominal exposure but fewer versus more effective
theses. No staking use.

## 7. Prospective gates (fixed now; a gate is never changed after outcomes are known)

Every comparison is candidate vs incumbent on IDENTICAL rows (same game, player, statistic, cutoff, seeds), with
2,000-resample game-clustered bootstrap intervals. A bad observation is never removed.

| arm | primary (must improve, interval excluding zero) | must not degrade (non-inferiority) | mechanism check |
|---|---|---|---|
| S1 | mean relative CRPS over targets, receptions, rec yards, carries, rush yards | MAE of the same five (+0.5% relative bound); every other scored statistic (+0.5%) | randomized-PIT chi-square falls for >= 3 of the 5 |
| Q1 | lower-decile calibration error `abs(P(rPIT < 0.10) - 0.10)` for attempts, completions, passing yards | CRPS of those three (+0.5%); receiver statistics identical | regime frequencies inside the model's 90% predictive bands |
| M1 | mean exact-margin log score | spread-ladder Brier at s +/- 0.5..10.5; total-ladder Brier; GAME SCRIPT V2 multiclass Brier (each +0.5% relative) | coherence invariants on every game |
| A1 | absolute bias of questionable players' carries + targets at T0_INACTIVES | teammates' CRPS (+0.5%) | applies only to T0_INACTIVES records |

Additionally for every arm: zero coherence failures; no single game supplies more than 10% of the summed primary
improvement (leave-one-game-out sign stable); and the prospective sample has reached the arm's minimum (section 8).
Passing makes an arm **PROMOTION_CANDIDATE** (a human decision); nothing is deployed automatically.

Status words: **PROSPECTIVE_CHALLENGER** = passed its development selection and mechanism check, and its contaminated
2021-2025 diagnostic did not show the primary metric worse; it then accumulates frozen prospective records.
**REJECTED_AT_DEVELOPMENT**, **DIAGNOSTIC_FAIL** otherwise.

## 8. Minimum prospective sample (procedure; numbers recorded in an addendum before any prospective result)

For each arm, from the 2020 DEVELOPMENT simulation (candidate vs incumbent on identical rows): the per-game mean of
the primary metric's paired difference gives an effect `d` and a between-game standard deviation `sd`; the minimum
number of prospective games is `n = ((1.96 + 0.84) * sd / d)^2` (80% power, two-sided 5%), rounded up to whole weeks
of 16 games, floored at 64 games (four weeks). If the development effect is zero or of the wrong sign the arm does not
become a challenger. For RISK1 the minimum is computed by the same formula from a synthetic study on the 2020
development simulation (contracts at each player's simulated median and at alternate spread / total lines, outcome =
2020 result, price = the simulated probability), for a minimal effect of interest of 0.02 in cash rate between the top
and bottom robustness terciles; if that number exceeds two seasons of games, RISK1 is reported as UNDERPOWERED for its
primary test at one-season scale, and the addendum says so.

Prospective records (write-once, `data/research/wave2/<day>/<run>.wave2.json.gz` on market-data): run id, cutoff,
kickoff, horizon, sim / engine / model versions, candidate-arm versions, incumbent and candidate distributions on the
same rows (quantiles), the market state the run read, and the GAME SCRIPT V2 state. Captures only exist once the Wave-2
research workflow is on `main`; until then no projection arm has prospective evidence, and that is reported as such.

## 9. Not in this wave

No broad opponent-adjusted feature search (Wave 1 kept the code and the negative result). No score-path modelling.
No ROI optimisation. 2021-2025 and pre-cutoff 2026 games are never cited as validation of S1, Q1, M1 or A1.
