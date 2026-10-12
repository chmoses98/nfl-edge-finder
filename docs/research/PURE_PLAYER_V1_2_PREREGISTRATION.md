# PURE_PLAYER_V1_2: preregistration (frozen before any held-out evaluation)

Frozen 2026-10-12.
* **Code:** frozen at commit **7f81ed2**: `nfl_edge/engines/player/pure_v1_2/`, version `pure-player-v1.2.0`, and
  the study and decision code in `scripts/research/pure_player_v1_2_study.py`.
* **Rule for this document:** it is committed on its own, and the results commit cites its hash.
* **No changes after this commit:** no model code, feature, constant or rule changes for this experiment. A bug fix
  that changed forecasts would void the run and would be reported as such.
* **PURE_PLAYER_V1 stays frozen:** `pure-player-v1.0.0` is imported read-only, and `tests/test_pure_player_v1_2.py`
  pins its source sha256 (`23a7ce16…`).

## What was looked at before freezing (disclosed)

* **The gap decomposition** (`docs/research/PURE_GAP_DECOMPOSITION.md`, commit 7f81ed2). It scored PURE_PLAYER_V1
  and the V4 arms on **the same 2024 + 2025 held-out rows** that serve as this challenger's primary holdout. Its
  findings chose *which* components V1_2 changes:
  * the environment channel of the efficiency models;
  * opponent adjustment (which the task required, although the decomposition found little upside);
  * opportunity and availability.

  This is a design-selection contamination of the primary window. No V1_2 parameter, feature form, constant or
  threshold was tuned on 2024 or 2025 outcomes, and V1_2 itself has never been scored on 2024, 2025 or 2026.
  Because of this contamination, the rule below also requires non-inferiority on **2026 weeks 1-5**. No
  decomposition and no V1_2 design step looked at that window.
* **Development season 2023 only.** V1_2 was fit on 2014-2022 and scored on 2023
  (`research/pure_player_v1_2/dev_2023.json`), to find bugs. The design was not changed in response to the scores.
  For the record (not evidence):
  * snap share −0.0010 [−0.0014, −0.0006];
  * passing yards −0.44 [−1.02, +0.13];
  * every other statistic within ±0.015 MAE, with CIs spanning 0.
* **Constants.** All constants are PURE_PLAYER_V1's: EWM half-life 6, carry 0.35, team shrink 4, ridge 1.0, ladders
  and distribution families. There was no hyperparameter search.

## Hypothesis

**H1.** On held-out regular-season games, PURE_PLAYER_V1_2 forecasts player statistics more accurately than the
frozen PURE_PLAYER_V1, on the same player-game rows. It does so by adding three football-only, point-in-time
feature families to V1's stage designs:

* **(A) Environment-conditioned efficiency.** PURE's own football-only team points forecast (`vol_pts`) and its
  expected margin enter the catch-rate, yards-per-reception, yards-per-carry, completion-rate and
  yards-per-attempt models. This is the sports-only analogue of how V4's market-implied total helps its yardage
  forecasts.
* **(B) Positional opponent adjustment.** The opponent's prior-only allowed-to-position-group rates enter the target
  and carry share models and the rate models. The rates are target share, catch rate, yards per target, carry share
  and yards per carry, each as a level and over expected.
* **(C) Available-pool opportunity.** The team's opportunity pool after its previous game enters the snap and share
  models. This is the total recent share of the teammates who played that game, plus the player's share of it.

## Excluded: point-in-time injuries

The only certified historical injury source is nflverse `injuries` 2010-2024, via its row-level `date_modified`.
**2025 is REJECTED**: there is no row time, and the only vintage post-dates the season. 2026 is certified only
through vintages from 2026-09-13, with a gap from 2026-10-06 that covers week 5. The source for this is
`docs/research/NFL_PIT_AVAILABILITY_CERTIFICATION.md` (PR #137).

The primary holdout includes 2025, so **no injury, inactive or roster-status input is used**. PR #137's injury
ablation (PURE_PLAYER_V1_1, 2023+2024) was itself REJECTED. A PIT-injury challenger needs the prospective capture
(2026+) as its holdout.

## Data and split (chronological)

* **Sources.** The nflverse files are `stats_player_week`, `snap_counts`, `players` and the schedule's allowlisted
  non-market columns. They were retrieved 2026-10-12T01:53Z. The 2024 and 2025 files are byte-identical to the
  PURE_PLAYER_V1 study manifest. 2026 sha256 prefixes: `stats_player_week_2026` 380616b6, `snap_counts_2026` fff11528.
* **Fit window.** For target season S every stage is fitted on 2014..S-1, with EWM warm-up from 2013. In-season
  features use only games whose kickoff + 4 h precedes the forecast cutoff (kickoff − 90 min), and this is asserted
  per row.
* **Primary holdout:** 2024 and 2025, pooled, each forecast by a model fitted strictly before it.
* **Supplementary holdout** (part of the rule, as a guard): every 2026 game with a box score in the retrieved
  files, fitted on 2014-2025. That is weeks 1-4 (64 games) plus 13 week-5 games. Snap counts for week 5 cover 1
  game, so snap share there is scored only where a snap count exists.

## Population (identical for every arm)

PURE_PLAYER_V1's population, unchanged:
* every QB / RB / WR / TE player-game with ≥ 1 offensive snap or a box-score line, conditional on own participation;
* QB passing statistics conditional on starting.

Arms are compared on matched (game, player, statistic) rows only.

## Arms

1. **PURE_PLAYER_V1** (frozen): the decision reference.
2. **PURE_EWM_BASELINE** (frozen): the simplest sports-only arm.
3. **PURE_PLAYER_V1_2**: the challenger.
4. **V4_MARKET_CLOSE**: DATA_PLAYER_V4 on the closing spread and total. A **market-informed benchmark**, descriptive
   only.
5. **V4_MEF_AS_IS**: V4 with `market_env=False`. **Not market-free**: its training sample is gated on a line, and
   it uses injury / roster statuses that are not PIT for 2025. Descriptive only.

The V4 comparisons cannot change the verdict.

## Metrics

Per statistic, never pooled across statistics; one row per player-game-statistic:
* MAE of the mean (primary);
* ΔMSE and bias;
* p10-p90 coverage, as Δ|cov80 − 0.80|;
* the Brier score of the representative rung: the baseline's ladder rung closest to 50%, chosen outcome-blind and
  used for every arm.

Uncertainty is a paired bootstrap resampling whole games (B = 1000, seed 20261010), reported as 95% percentile
intervals of challenger − reference. Results are reported by season and by position group, with counts.

## Decision rule (PURE_PLAYER_V1_2 vs PURE_PLAYER_V1, nine statistics)

Primary scope is 2024 + 2025. The rule is implemented in `pure_player_v1_2_study.decide`.

**ACCEPTED_CHALLENGER** (research collection only) iff all of the following hold:
* (a) ΔMAE < 0 on at least **6 of 9** statistics, with the 95% CI entirely below 0 on at least **3**;
* (b) no statistic has a ΔMAE or ΔBrier 95% CI entirely above 0;
* (c) no statistic has a Δ|cov80 − 0.80| whose 95% CI lies entirely above **+0.01**. The tolerance is fixed here
  because the count intervals' coverage is dominated by discreteness: V1's coverage is 0.88-0.93 on counts;
* (d) **2026 supplementary:** no statistic has a ΔMAE 95% CI entirely above 0.

Otherwise the verdict is:
* **REJECTED** otherwise;
* **BLOCKED_DATA** if fewer than 7 of 9 statistics have ≥ 200 scored player-games in each primary season.

## Runtime non-leakage (must hold independently of accuracy)

`--mutation` rebuilds the 2025 V1_2 forecasts from files with the schedule's market columns removed and randomised.
The forecast digests must equal the original's. `tests/test_pure_player_v1_2.py` repeats this on synthetic data,
including partial blanking, and adds three more checks:
* a future-box-score test;
* a defence-feature prior-only test;
* a source scan for market / injury tokens.

Historical evidence never authorises live use. **There is no promotion and no production wiring.** An accepted
challenger would only be added to research collection, pending prospective validation and separate approval.
