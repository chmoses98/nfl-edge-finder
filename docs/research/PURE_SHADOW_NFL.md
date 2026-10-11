# PURE shadow collection — NFL (Phase 2, research only)

Prospective, append-only collection of the frozen market-independent arms **PURE_PLAYER_V1**
(`pure-player-v1.0.0`, code frozen at 0441dfc, merged unchanged in 762d69d) and **PURE_EWM_BASELINE**
(`pure-ewm-baseline-1.0.0`), with the market listing and the incumbent market-informed V4/V5 projections kept in
separate file families. Nothing here selects, recommends, stakes, gates, or publishes to a production surface,
and nothing reads its output for a decision.

## What runs

`.github/workflows/shadow-pure-nfl.yml`, hourly at :35 UTC, plus `workflow_dispatch` (optional `adhoc` = `ALL` or
game ids), plus `pull_request` as a **dry run**: it fetches live inputs, captures every upcoming game as ADHOC into a
scratch store, validates and verifies the store, uploads it as an artifact, and never publishes.

1. **Gate.** The workflow downloads the schedule only and asks `collect.py --check-windows` whether a capture window
   is open. A scheduled run with no open window that isn't a scoring hour (05/11/17/23 UTC) stops there.
2. **Inputs.** `scripts/data/nflverse_download.py` downloads the schedule, `stats_player_week` and `snap_counts`
   for 2013 through the current season, plus `players` and `rosters`. Each file gets a manifest row: url,
   `retrieved_at`, sha256, and HTTP last-modified.
3. **Market-data, read-only and sparse** (`scripts/shadow_pure/checkout_market_data.sh`). This fetches the published
   store, the newest Kalshi discovery (`KXNFL*` series), the last 3 h of capture quote files, and the newest two
   shadow-v2 `DATA_PLAYER_V4` and `DATA_PLAYER_V5` snapshots. `build_player_map.py` then maps Kalshi player ids to gsis.
4. **Immutability checks before anything is written.** These check the hash chain of the published store, and
   then the branch history: no commit may have modified, deleted, or renamed a path under `data/shadow_pure`.
5. **Capture** (`scripts/shadow_pure/collect.py`). Each (game, kind) is captured at most once, and its `as_of` is
   the instant the run started.

   | kind | window (minutes before kickoff) |
   |---|---|
   | DAY_BEFORE | 1800 – 1080 (T-30h … T-18h) |
   | MORNING_OF | 480 – 165 (T-8h … T-2h45m) |
   | FINAL_T90 | 90 – 30 (after the official inactive list, published about T-90m) |
   | ADHOC | dispatch / dry run, any time strictly before kickoff |

6. **Settle and score** (`scripts/shadow_pure/settle_evaluate.py`). This writes outcomes for matured rows, then
   reconciliation, then `pure_gate compare` scorecards.
7. **Verify** that the local store chain is intact and that publishing only **adds** files. Then upload the
   artifact and, on `main` only, publish to `market-data` through the repository's publisher, which handles
   fetch/rebase retries and fails loudly on conflict. The concurrency group is `shadow-pure-nfl-collect`.

## Store layout (`data/shadow_pure/nfl/` on `market-data`)

| family | file | content |
|---|---|---|
| projections | `projections/<day>/<run>.<ARM>.pure_forecast_v1.jsonl.gz` | `pure_forecast.v1` rows (validated with the vendored gate `--require-v1` semantics before writing). Each row has one player-game-statistic and the ladder inside it. |
| inputs | `inputs/<day>/<run>.inputs.json` | every input file: path, url, fetched_at, sha256, bytes, last-modified. Combined per-source snapshot sha256. |
| market | `market/<day>/<run>.kalshi_listings.jsonl.gz`, `.listed_cohort.jsonl.gz` | Kalshi player-stat contracts with `open_time`, `created_time`, our first observation, and the latest captured quote at or before as_of. Also the per (game, player, statistic) pregame-listed cohort. |
| incumbent_diagnostic | `incumbent_diagnostic/<day>/<run>.v4_v5_market_informed.jsonl.gz` | latest DATA_PLAYER_V4/V5 record at or before as_of, labelled `MARKET_INFORMED_DIAGNOSTIC`. It holds the distribution summary and rung probabilities. |
| outcomes | `outcomes/<day>/<run>.outcomes.jsonl.gz` | nflverse box-score outcome per player-game-statistic, with source and `observed_at` (fetched_at). Only new or corrected values are written. |
| reconciliation | `reconciliation/<day>/<run>.reconciliation.jsonl.gz` | projection to outcome join, the listed flag, and market-settlement vs sports-outcome mismatch tickers. |
| evaluations | `evaluations/<day>/<run>.evaluation.json` | `pure_gate compare` per capture kind on the full eligible population and on the pregame listed cohort. These are descriptive only. |
| runs, manifests | `runs/<day>/<run>.summary.json`, `manifests/<run>.manifest.json` | run summary. The manifest holds every file written with its sha256 and `prev_manifest_sha256`, which forms the hash chain. |

## Population, conditioning, and what each row carries

* **Population.** Football data alone defines it, before kickoff. It covers every QB, RB, WR, or TE whose most recent
  appearance was for the team in one of its last three games, plus the team's designated starting QB.
  Market listing plays no part. Only each team's **next** game is forecast. A later game would be computed
  through an unplayed one, and the PIT guard refuses that; it caught the case in development.
* **Conditioning.** Forecasts are conditional on own participation, and `participation_probability` is null:
  participation isn't modelled, and no availability source is certified (see the PIT availability PR).
  QB passing statistics are also conditional on starting. The assumed starter comes from the schedule
  vintage's starting-QB id as fetched, and from the previous game's starter if that is blank. Scoring drops
  rows whose condition failed, and pure_gate counts them as conditional DNP.
* **Feature lineage** (each entry has a source and an `observed_at`):
  * frozen model inputs;
  * expected workload: snap share, targets, carries, pass attempts, target and carry share, team plays;
  * opponent-adjusted inputs: prior-only rates the opponent allowed;
  * the sports-only team environment: team and opponent pass/rush attempts, points, expected margin and points,
    pass rate, home, fixed dome venue, rest, recent QB change;
  * script sensitivity: forecast-mean change for +7 points of football-only expected margin;
  * the assumed-starter flag and its basis.
* **Timestamps.** Box-score features are observed at kickoff + 4 h of the latest game used, and schedule facts at
  the schedule's fetched_at. Sources' `max_observed_at` is the files' fetched_at. The guards require
  `source_max_observed_at` < `as_of` < `kickoff`. Every input's fetched_at must be < `as_of`, or the run refuses.
* **Frozen model.** The collector refuses to run if the sha256 over the `pure_v1` package and its estimator differs
  from `PURE_V1_CODE_SHA256`. A changed model must be a new version. `model_frozen_hash` on every row is that sha256.

## Pregame market-listed cohort

A player-game-statistic is in a capture's cohort only if both of these hold:
* a contract on it had `open_time ≤ as_of`;
* the contract was observed by our own pregame record (a discovery run or a capture quote) at or before `as_of`.

Settlement and trading play no part. The cohort is joined to the PURE rows only at scoring time.

## Evidence that the prospective path is the evaluated model

`scripts/shadow_pure/equivalence_check.py` re-forecasts already-played 2026 weeks through the prospective path,
using only games observable 2 h before the week's first kickoff. It compares the results with the frozen
walk-forward pipeline. Results are in `research/pure_shadow_nfl/equivalence_2026_wk0{3,4}.json`.

* **Week 4.** All 1,653 matched rows per arm are identical (max |Δmean| 1.8e-15).
* **Week 3.** 1,634 of 1,638 rows are identical. The 4 that differ are one player (00-0040390), whom nflverse
  labels TE in his previous game and WR in the target game. The backtest groups him by the target game's own
  label; the prospective path uses the label known pregame. This is a small hindsight in the walk-forward frame,
  not a defect of the collector.
* **Population.** 72 (wk 4) and 94 (wk 3) played rows had no prospective forecast. These are players with no
  appearance for the team in its last three games, such as returns from long absences and first appearances.
  Each capture's run summary reports candidate counts, and scoring counts those players' outcomes as
  `outcomes_without_matched_forecasts`.

## Runtime market independence of the collector

`tests/test_shadow_pure.py::test_capture_end_to_end_validates_is_idempotent_and_market_independent` runs the whole
capture with market-data present, removed, and randomised. The PURE projection files must be byte-identical
across all three runs. The separate market family is the negative control, and it must change. The model's own
mutation proof is `research/pure_player_v1/pure_gate_rerun.json` (PASS_RUNTIME_NONLEAKAGE).

## Known limits

* Hourly cron with a 60-minute FINAL_T90 window: a GitHub schedule delay of more than about 55 minutes can miss a
  FINAL_T90 capture. A missed window is never captured late; it stays missing and is visible in the run summaries.
* Quotes: only the last 3 h of capture files are read, so prices for contracts that didn't change in that window
  come from the newest discovery and carry its observation time.
* The incumbent V4/V5 family is empty while `shadow-v2-project.yml` doesn't publish. Its scheduled runs since
  2026-10-05 fail in the publish step, and each capture records that as `NO_INCUMBENT_RECORD_AT_OR_BEFORE_AS_OF`.
* There is no participation model. Inactive players are excluded only at scoring, as conditional DNP.

## Rollback

Delete or disable `.github/workflows/shadow-pure-nfl.yml`. The collector touches only new paths:
`nfl_edge/shadow_pure/`, `scripts/shadow_pure/`, `tools/pure_gate/`, `tests/test_shadow_pure.py`,
`research/pure_shadow_nfl/`, `data/shadow_pure/` on `market-data`.
