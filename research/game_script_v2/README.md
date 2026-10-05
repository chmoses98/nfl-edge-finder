# GAME SCRIPT V2 and the five-season study (RESEARCH_ONLY)

Starting point: `main` at `d5c7f8dfa014b9be3aff7550734b6208e7314554`. Nothing here changes betting authority,
production thresholds, staking, incumbent model probabilities, recommendation authority or reconciliation weights.

| file | what | generated from |
|---|---|---|
| `PREREGISTRATION.md` | every threshold, arm, baseline and decision rule, committed before the results (stage 1; stage-2 addendum) | hand-written |
| `METHODOLOGY.md` | how each part works and how to reproduce it | hand-written |
| `LIMITATIONS.md` | point-in-time caveats, data-vintage findings, what was not fixed and why | hand-written |
| `BASELINE_5Y.md` | the frozen incumbent, 2021-2025, per season and pooled | `baseline_5y.json` |
| `SCRIPT_CALIBRATION_5Y.md` | the nine-cell script calibration, marginal events, post-hoc margin shape, score-path arm | `script_calibration_5y.json`, `validation_5y.json` |
| `OPPONENT_ADJUSTMENT_ABLATION.md` | arms A1-A5 and R1 against the frozen baseline | `opponent_adjustment_ablation.json` |
| `VALIDATION_5Y.md` | injury redistribution, weather (NON_PIT historical; 2026 point-in-time accumulation) | `validation_5y.json` |
| `reproduction_2023_2025.json` | the committed 2023-2025 run against a fresh unmodified-code reproduction | `scripts/sim/reproduction_check.py` |
| `example_2025_11_KC_DEN.md` | ILLUSTRATIVE: what the RUN NFL section looks like for one completed game | `scripts/sim/script_v2_example.py` |

Every generated Markdown file is a pure render of its JSON (`scripts/sim/write_game_script_v2.py`), and
`tests/test_game_script_v2_results_consistency.py` re-renders and compares.

## Verdicts

| item | verdict | basis |
|---|---|---|
| GAME SCRIPT V2 (lattice, matrix, dependency) | **NEEDS MORE WORK** (preregistered rule) | pooled multiclass Brier beats the unconditional prior and ties the spread-bucket prior; ECE inside the calibrated-forecaster null; but 2022 is worse than the unconditional prior. Every invariant holds (cells exhaustive, sum to 1, no random draw, reconciliation identity exact, pricer semantics identical, incoherent games refused). |
| Score-path arm P1 | **REJECTED** | small wins on half / Q3 leader and quarter margins, none on early blowout, late comeback or lead changes -- the registered rule needs all |
| A1 env_adj, A3 env_eff_adj, A5 fix_env_adj | **REJECTED** | improve every season and all eight statistics, but 0.15-0.21% relative CRPS, below the registered 0.5% materiality bar |
| A4 def_join_fix (train/serve skew) | **REJECTED** | 0.18%, below the bar, and fails the calibration criterion; the skew is documented |
| A2 eff_adj | **REJECTED** | no effect (+0.01%) -- consistent with the earlier rushing ablation |
| R1 outside_share_repair | **REJECTED** | slightly worse (+0.04%, interval excludes zero) |
| QB usage-first starter rule | **NOT RUN** | lost to the depth chart on the design seasons 2018-2020 |

## What the five seasons say

* The frozen incumbent reproduces: 1,424 games, no skipped game, no coherence failure, ~20,000 scored player-stat rows a
  season. It beats the naive prior-only projection on every statistic in every season (pooled MAE: carries -14.9%,
  rushing yards -9.6%, attempts -5.5%, passing yards -3.4%, targets -3.0%, receptions -1.8%).
* 2021-2022 (the retrospective challenge seasons) look like 2023-2024; 2025 is the best season, most visibly for
  quarterbacks (attempts CRPS 5.09 against 6.0-6.3), coinciding with daily depth charts (simulated QB1 = leading passer
  96.3% against 90-93%).
* The error is upstream: player share is the largest component for receptions (60-64%) and rushing yards (36-47%);
  for passing yards it is the starter's share of attempts.
* Calibration problems the old coverage metric hid: targets / receptions / receiving yards are over-dispersed;
  quarterback volume is left-tail heavy; the incumbent residual bank puts about half the realized mass on a margin of
  exactly 3. None was fixed here -- see `LIMITATIONS.md` items 2 and 13 for the preregistrations they call for.
* Injury redistribution after a starter's absence is calibrated on average; QUESTIONABLE players are under-projected in
  the backtest by construction (game-day inactives already removed, discount applied again), not prospectively.
* Opponent-adjusted ratings are better ratings (lower next-week error on every metric) but do not move the simulated
  player distributions materially: the game centre is the market's and player share dominates the error.
