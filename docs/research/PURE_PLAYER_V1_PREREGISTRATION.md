# PURE_PLAYER_V1 — preregistration (frozen before any held-out evaluation)

Frozen 2026-10-11. Model code frozen at commit `0441dfc` (`nfl_edge/engines/player/pure_v1/`, version
`pure-player-v1.0.0`; baseline `pure-ewm-baseline-1.0.0`). This document is committed on its own; the held-out
results commit cites its hash. No model code, feature, constant or ladder changes after this commit for this
experiment; a bug fix that changes forecasts would void the run and be reported as such.

## What was looked at before freezing

* Development / validation season **2023 only** (fit on 2014-2022), used to find bugs (a missing context join, a
  NaN snap outcome). The design was not changed in response to its scores. Dev result for the record (not
  evidence): PURE MAE below the EWM baseline on all 9 statistics; roughly level with V4 (market_env False/True).
* Nothing from 2024, 2025 or 2026 has been scored by any arm in this experiment. (Earlier repository research,
  e.g. research/player_engine_v4, scored 2025 against Kalshi rungs; PURE's design does not use those results.)
* All constants are the repository's pre-existing sports-only EWMA constants (half-life 6 games, season carry
  0.35, shrink 2 / 4 — `research/player_distributions/results.json`, tuned on 2016-2019 sports outcomes), V4's
  fixed ridge penalty (1.0) and fixed ladders. No hyperparameter search; nothing selected by market agreement.

## Hypothesis

H1: On held-out NFL regular-season games, PURE_PLAYER_V1 (football-only environment -> role -> opportunity ->
efficiency) forecasts player statistics more accurately than the simplest sports-only arm, PURE_EWM_BASELINE
(each player's own prior-only EWM with identical distribution machinery), on the same player-game rows.

## Data and split (chronological)

* Sources: nflverse `stats_player_week_<season>`, `snap_counts_<season>`, `players` (pfr->gsis crosswalk) and
  the schedule's allowlisted non-market columns (retrieved 2026-10-10 from the nflverse GitHub releases;
  sha256 manifest recorded with the results). Regular season only.
* For target season S every stage is fitted on seasons 2014 .. S-1 (EWM warm-up from 2013); in-season features
  use only games whose kickoff + 4 h precedes the forecast cutoff (kickoff - 90 min).
* **Primary holdout: seasons 2024 and 2025 (pooled), each forecast by a model fitted strictly before it.**
  Supplementary: 2026 weeks with completed box scores at retrieval (weeks 1-5), fitted on 2014-2025; reported
  separately, not part of the decision.

## Population and conditioning (identical for every arm)

Every QB/RB/WR/TE player-game in the sports data with >= 1 offensive snap or a box-score line ("played").
Forecasts are conditional on the player's own participation; QB passing statistics are conditional on starting
(schedule starting-QB id, box-score fallback). Teammates' realised participation is never used. Population per
statistic: snap share (RB/WR/TE + starting QB, snap count available); targets / receptions / receiving yards
(RB/WR/TE); carries / rushing yards (RB + starting QB); passing attempts / completions / passing yards (starting
QB). Rows whose outcome is missing in the sports data are forecast, counted and not scored, for every arm.
Market listing never selects a row; the 2025 Kalshi listing is joined afterwards only as a diagnostic.

## Arms

1. PURE_EWM_BASELINE (reference for the decision). 2. PURE_PLAYER_V1 (challenger). 3. V4_MEF_AS_IS:
DATA_PLAYER_V4 `market_env=False` exactly as it stands (training sample still filtered on `implied_total.notna()`,
injury/roster status features, realised schedule QB). 4. DATA_ONLY_GAME: the repository's existing football-only
game model (research/game_model walk-forward) — team points only; no sports-only player challenger exists in the
repository. 5. V4_MARKET_CLOSE (V4 `market_env=True`, consensus closing line) and the closing-line implied team
total: **price-of-independence diagnostic only**, never a decision input.

## Metrics (per statistic, never pooled across statistics; one row per player-game-statistic)

Layers: team pass attempts, rush attempts, plays, points; snap share; targets; carries; receptions; receiving,
rushing, passing yards; passing attempts; completions. MAE (primary), RMSE (as ΔMSE), bias, p10-p90 coverage,
and the Brier score of ONE representative ladder rung per player-game-statistic: the baseline's rung closest to
50% (outcome-blind), used for every arm. Uncertainty: paired bootstrap resampling whole games (B = 1000, seed
20261010), 95% percentile intervals of challenger − reference. Reported by season and by position group, with
counts and exclusions. The kit gate (`prop_projection_gate.py validate|compare`) is run on the sidecars.

## Decision rule (primary scope 2024+2025, PURE_PLAYER_V1 vs PURE_EWM_BASELINE, 9 player statistics)

* **ACCEPTED_CHALLENGER** (research collection only) iff
  (a) ΔMAE < 0 on at least 6 of the 9 statistics, with the 95% CI entirely below 0 on at least 4; and
  (b) no statistic has a ΔMAE or ΔBrier 95% CI entirely above 0 (significantly worse).
* **REJECTED** otherwise.
* **BLOCKED_DATA** if fewer than 7 of the 9 statistics can be scored on >= 200 player-games per primary season.

The V4 / market comparisons are descriptive and cannot change the verdict. Historical evidence never authorises
live use; promotion would require prospective validation and separate approval.

## Runtime non-leakage (must pass independently of accuracy)

`scripts/research/pure_player_v1_mutation.py` reruns the full pipeline for 2025 from files with the schedule's
market columns original / removed / randomised / 30%-blanked: PURE forecasts must be bit-identical; V4's
VolumeModel (negative control) must change or refuse.
