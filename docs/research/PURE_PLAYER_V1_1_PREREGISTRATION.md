# PURE_PLAYER_V1_1 preregistration: one ablation that adds point-in-time availability features

Frozen 2026-10-11. This document is committed on its own, before any PURE_PLAYER_V1_1 forecast is scored on
the holdout. The results commit cites its hash. PURE_PLAYER_V1 (`pure-player-v1.0.0`, code frozen at
0441dfc) stays frozen and unchanged. This experiment creates a new version, `pure-player-v1.1.0`, in a new package.

## Why only this one

The PIT certification (`docs/research/NFL_PIT_AVAILABILITY_CERTIFICATION.md`) certifies exactly one historical
availability source: the nflverse weekly injury report for 2010–2024. Its row-level `date_modified` precedes
kickoff on 99.77–100% of rows per season. The other candidate sources are handled as follows:

* 2025 injuries are rejected.
* Depth charts are certified only from 2025, so they can't cover a historical holdout.
* Inactive lists are rejected for history.

PURE_PLAYER_V1's results note that V4's remaining edge most plausibly comes from teammate-status features. This
ablation adds those features in their point-in-time-provable form, and adds nothing else.

## What was looked at before freezing

* Certification statistics only (timestamps, counts, identity match). No V1_1 forecast has been scored on any
  season. A development run on **2022** (fit on 2014–2021) may follow this commit, to find bugs only. If it
  changes the code, the change is reported. It never changes a feature, constant, or rule.
* Disclosure: seasons 2023 and 2024 were scored for PURE_PLAYER_V1 in its own study (2023 as its development
  season, 2024 as its holdout). Those results are aggregate tables. V1_1's feature set below was fixed from the
  certification and from V4's existing feature names (`own_q`, `own_d`, vacated shares). It was not fixed from
  any V1 residual on 2023 or 2024.

## Hypothesis

H1 states that adding PIT teammate-status and own-status features to PURE_PLAYER_V1's snap-share,
target-share, and carry-share stages lowers forecast error, on the same held-out player-game rows. The
features come from the final weekly injury report, using only rows whose `date_modified` is before kickoff − 90 min.

## Features (all computed for target game G of team T, from certified rows of (season, week, T) only)

| name | definition | enters |
|---|---|---|
| `own_q`, `own_d` | the player's own report_status is Questionable / Doubtful | snap, target share, carry share |
| `own_lim`, `own_dnp` | the player's own final practice_status is Limited Participation / Did Not Participate | snap, target share, carry share |
| `vac_t` | sum, over RB/WR/TE teammates listed Out or Doubtful, of each teammate's mean target share over his last ≤ 3 games played before G (prior-only) | target share |
| `vac_c` | the same for carry share, over RB teammates | carry share |
| `qb1_out` | the starter of T's previous game is listed Out or Doubtful | target share |

A player or teammate missing from the certified report counts as not listed (0). This covers absent rows and
rows refused because their `date_modified` is at or after the cutoff: information that wasn't provably available
pregame is treated as absent. Every other stage, constant, ladder, and distribution is V1's own:
* team volume;
* count stacks;
* efficiency;
* NB / ratio / residual distributions, refitted on the same training rows.

The stage models are refitted with the extra columns. The ridge penalty is unchanged (1.0), and there is no search.

## Data and split (chronological)

* Sources: V1's sources (nflverse `stats_player_week`, `snap_counts`, `players`, and the schedule's allowlisted
  non-market columns), plus nflverse `injuries_<season>` 2010–2024 through `nfl_edge.availability_pit.loaders.
  injuries_certified`, with a lead of 90 min. The `retrieved_at` and sha256 of every file are recorded with the
  results.
* For target season S, every stage is fitted on seasons 2014 .. S-1, as in V1.
* **Holdout: seasons 2023 and 2024, pooled.** Each season is forecast by a model fitted strictly before it.
  Development (bugs only): 2022.

## Population, arms, metrics

* Population: V1's population exactly (conditional on playing; QB passing conditional on starting), on the
  identical rows for every arm.
* Arms:
  * PURE_PLAYER_V1, the incumbent;
  * PURE_EWM_BASELINE, the simplest sports-only baseline;
  * PURE_PLAYER_V1_1, the challenger.
* Metrics are reported per statistic and are never pooled across statistics:
  * MAE and RMSE;
  * bias;
  * p10–p90 coverage, as |coverage − 0.8|;
  * CRPS, approximated as 2 × mean pinball loss over p10 / median / p90;
  * Brier score and log loss at ONE representative rung per player-game-statistic: V1's rung closest to 50%,
    which is outcome-blind and used for every arm.
* Uncertainty: paired bootstrap resampling whole games, with B = 1000, seed 20261011, and 95% percentile intervals.
* Preregistered subgroups (descriptive): rows of team-games with any skill teammate listed Out/Doubtful
  (`vac_t + vac_c > 0` or `qb1_out`) versus none; position group; season.

## Decision rule (holdout 2023 + 2024, PURE_PLAYER_V1_1 vs PURE_PLAYER_V1, 9 player statistics)

* **REJECTED** if ANY preregistered metric gets worse with its 95% CI entirely above 0, on any of the 9
  statistics. The metrics are MAE, RMSE (as ΔMSE), |coverage − 0.8|, CRPS, Brier, and log loss.
* **ACCEPTED_CHALLENGER** (research only) if nothing gets significantly worse AND ΔMAE < 0 with its 95% CI
  entirely below 0 on at least 4 of the 9 statistics.
* **INCONCLUSIVE** otherwise.
* **BLOCKED_DATA** if the certified injury rows cover less than 90% of holdout team-weeks.

The comparison against PURE_EWM_BASELINE is also reported; it can't rescue a REJECTED verdict. Nothing is
promoted. A research ACCEPTED_CHALLENGER would still need prospective collection with the PIT capture before
any further use.

## Runtime non-leakage

Unit tests rerun V1_1 on synthetic data under three versions of the schedule's market columns: as published,
removed, and randomised. The forecasts must be bit-identical. V4's VolumeModel is the negative control and must
change. The injury loader is checked to refuse any row whose `date_modified` is at or after the cutoff.
