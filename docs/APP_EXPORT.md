# Edge Finder app export (`app/latest`)

`scripts/app_export.py` turns one RUN NFL report plus the `handicap-data` ledger into the Edge Finder app
payload described by the vendored contract in `contract/edge_finder_contract/` (`edge_finder.app.v1`). It is
an adapter and nothing else: no model, gate, stake, bankroll rule or authority is computed here, and the
production pipelines that feed it are unchanged.

    python3 scripts/app_export.py --reports-dir data/handicap_report --handicap-root <handicap-data checkout> \
        [--market-data-root /tmp/md] [--horizon-state state/horizons.json] --out <staging>/app/latest \
        [--now <aware ISO>] [--commit-sha X] [--workflow-run-id Y]

Validate a tree with `PYTHONPATH=contract python3 -m edge_finder_contract validate <out>`.

## Where the app reads it

The registry (`contract/edge_finder_contract/registry.json`) names NFL at branch **`handicap-reports`**, path
**`app/latest`**: `https://raw.githubusercontent.com/chmoses98/nfl-edge-finder/handicap-reports/app/latest/`.

Files: `manifest.json`, `events.json`, `markets.json`, `model_prices.json`, `recommendations.json`,
`theses.json`, `wagers.json`, `settlements.json`, `runs.json`, `board.json`, `performance.json`,
`health.json`, `event_detail/<event_id>.json`.

## What is exported, from where

| document | source | notes |
|---|---|---|
| events | `latest/manifest.json` `kickoffs[]` + `latest/analysis/games/<game_id>.json` headers | one per game on the slate; plus any past game a ledger record refers to (see identities) |
| markets | one per analysis row (one row per executable Kalshi contract) | prices already in dollars `[0,1]`; `captured_at` = the Kalshi capture the ledger was priced from; plus stubs (prices null) for ledger tickers no longer on the board |
| model_prices | `incumbent.model_probability` of each row where the incumbent (production shadow ledger, `manifest.model_version`) priced it | `support_status` = `incumbent.support_state`; `data_quality_status` OK when SUPPORTED else UNSUPPORTED; `market_probability` = row `mid`; Shadow v2 (`engine`, `p_yes`, `support_state`, ...) and the coherent simulation (`p_football`, `p_market`, `p_reconciled`, ...) ride in `extensions` as research |
| theses | one per board game, `summary` null | the packet's own `latest/games/<game_id>.md` is the thesis; `evidence` points at it. No prose is generated |
| recommendations | `handicap-data` `data/recommendations/<season>/week_NN/*.json` via `nfl_edge.handicap.store.read_kind` + `latest_amendment_chain` | `test_only` excluded (as every repo reader does); amendment chains collapsed |
| wagers | `handicap-data` `data/imported_wagers/.../routed-*.json` (`imported_wager.v1`) | `source=KALSHI_ROUTER`, identity `source_bet_key`; `average_price=actual_price`, `fees=fees_paid`, `side=execution_action` (null where the router never sent it) |
| settlements | `handicap-data` `data/wager_settlements/.../stl-*.json` with `data/wager_settlement_amendments/` applied through `settlement_amendments.canonical_settlement` | newest admissible economics wins (v2 over v1), exactly like the repo's postmortem; `EXCHANGE_CONFIRMED` when the ledger says SETTLED |
| performance | wagers + settlements | CLV only from `market-data` `data/handicap/actual_wagers/<season>/season.actual_wagers.json` where the postmortem says `CLV_VALID`; never computed here |
| health / board / event_detail | the above | see thresholds |

Optional `--market-data-root` adds the nflverse schedule cache (real kickoffs for past-week events) and the
actual-wager postmortem (CLV). Without it the export still builds; past-week events then carry a
`PLACEHOLDER` start time (the ticker's game date) and performance carries no CLV.

## Identities

* **event_id**: `nflverse_game_id` (e.g. `2026_04_PIT_CLE`). For a ledger wager the game id is derived from
  the wager's own `season`/`week` and the away/home teams the ticker encodes
  (`nfl_edge.kalshi.classifier.classify`); a recommendation carries `game_id` directly. Every other provider
  id travels in `source_ids`.
* **participants**: teams `nflverse_team` (3-letter code, display name from `nfl_edge.data.ids.TEAM_NAMES`);
  players `gsis_id` when the row carries `player_id`, else `kalshi_player_id`. Player participant ids are
  computed deterministically and the raw id sits in the market's `extensions`.
* **market_id**: `mkt_kalshi_<TICKER>`; event/series tickers from the ticker shape.
* **model_price_id**: (run, market, model_version). **recommendation_id**: native `recommendation_id`.
  **wager_id**: `source_bet_key`. **settlement_id**: derived from the wager id.
* **run_id**: (NFL, repo, `handicap_run_id`, `built_at`) -- the run id of every document of one export;
  `commit_sha` = `sources.main_sha` (overridable), `workflow_run_id` = `sources.workflow_run_id`.

## Status and authority mapping

* `bet_authority` = **MANUAL**: ChatGPT writes the ledger, the preflight gate validates, the owner places by
  hand. The exporter never touches the bridge, preflight, Airtable or any credential.
* Ledger `decision` -> status: RECOMMENDED -> `RECOMMENDED` (authority MANUAL, `research_only` false);
  PASS -> `PASS`; WATCHLIST -> `WATCH`; RESEARCH_ALERT -> `RESEARCH_CANDIDATE` (authority RESEARCH_ONLY,
  `research_only` true). `fair_probability` = `probability_mid`, `current_price` = the frozen ask of the
  recommended side, `bet_up_to_*` = `bet_up_to_probability`, `stake_dollars` = `recommended_stake` (after
  portfolio limits; `proposed_stake` in `extensions`).
* **Model rows are never recommendations.** The packet states it recommends nothing
  (`real_money_status: NOT VALIDATED`, "model/market differences ... are never edges, selections or
  recommendations"), so a priced row becomes a `model_price` only. The repository's research candidates
  live in the ledger as RESEARCH_ALERT records and arrive through that path.
* Event status: `game_state` PREGAME -> SCHEDULED; STARTED_OR_UNKNOWN -> UNKNOWN (the report does not
  distinguish live from final). Off-board games: FINAL when the schedule cache has a result, SCHEDULED when
  the kickoff is ahead, otherwise UNKNOWN. Market status: on-board rows OPEN; stubs SETTLED/UNKNOWN.
* Settlement result WON/LOST as recorded; anything the ledger left null is `UNKNOWN` with the ledger's
  refusals (never a guessed zero). Settlement `fees` is null (the ledger records fees on the wager, not the
  settlement); `net_pnl` is the canonical (amended) figure and `gross_payout` the gross return.

## Freshness thresholds and health

| component | fresh | stale | as_of |
|---|---|---|---|
| market_data | 30 min | 3 h | `manifest.vintages.kalshi_capture.queried_at` (the capture the ledger was priced from) |
| model | 2 h | 24 h | `manifest.vintages.shadow_pricing.written_at` (falls back to `built_at`) |
| router / settlement | 7 d | 14 d | newest wager `placed_at` / newest `settled_at` (weekly cadence; informational) |

Horizons are T-24h..T-30m before kickoff and the shadow cycle re-prices every two hours from an hourly
capture, hence the market window. `next_scheduled_run` is the next pending decision horizon computed with
`nfl_edge.handicap.horizons.due_horizons` from the slate's kickoffs and `state/horizons.json` (`--horizon-state`),
or `now` when one is already due; null off-slate.

## Workflow placement and failure policy

`run-nfl.yml` (and the two-hourly `shadow-price.yml`, which publishes the same report) gained one step,
**"Export the Edge Finder app payload"**, placed immediately before "Publish the browsable latest report":

1. `git fetch --depth=1 origin handicap-data` + `git archive origin/handicap-data data | tar -x` into
   `$RUNNER_TEMP` -- a read-only extract; no worktree, no checkout, no push. The isolation tests in
   `tests/test_run_nfl_isolation.py` were refined to admit exactly these two command shapes and to assert
   that nothing on the report path pushes, checks out or adds a worktree on the ledger branch; the static
   import audit of the report path is unchanged and `scripts/app_export.py` is deliberately **not** a report
   entry point, because it legitimately imports the ledger reader (`store`). A separate test proves the
   exporter's import graph reaches none of the bridge / preflight / approval / risk / gates modules and no
   third-party package.
2. The previously published `app/latest` is extracted first (last-known-good), then the exporter writes
   into it. On failure the exporter writes **only** `health.json` (`export_failed: true`,
   `payload_run_id` = the previous manifest's run) and exits 1.
3. `publish_handicap_report.py --app-src <dir>` copies that directory to `app/latest` in the branch tree
   **exactly when `latest/` is replaced** (the non-regression guard applies to both surfaces), so the branch
   never carries an app payload describing a different report than `latest/`. Without `--app-src`, or with an
   empty directory, the branch's existing `app/latest` is carried forward (the branch is re-rooted from the
   worktree on every publish).

Why the export step is `continue-on-error: true` and NOT a plain failing step: the step sits before the
publish, and a failing step would skip every later step, including the report publish -- the one thing a
broken export must never prevent. So the export tolerates its own failure, the report publishes with the
degraded `health.json`, and a final step **"Fail the job if the app export failed"**
(`if: steps.app_export.outcome == 'failure'`, `exit 1`) makes the job red afterwards. In `run-nfl.yml` that
is a hard failure. In `shadow-price.yml` the report build and publish are themselves tolerated (the job's
product is the ledger), and the export follows the same policy there; its failure step still turns the job
red, which matches the spec and is visible in the run list.

## Real-data proof (2026-10-02, week 4 report, handicap-data as of the same day)

Built from `origin/handicap-reports` (`latest/`, `state/`) and `origin/handicap-data` plus the market-data
schedule cache and postmortem: 51 events (16 on the board, e.g. `2026_04_PIT_CLE`, 35 past games referenced
by wagers), 10,796 markets (10,721 on the board + 75 stubs), 5,612 model prices (every SUPPORTED incumbent
row), 0 recommendations (the three ledger records are `test_only`), 84 wagers, 84 settlements (48 WON /
36 LOST, 18 amended to v2 economics, 2 without established economics), health HEALTHY (capture AGING at 47
min, model FRESH), `verify_published` = `[]`, and the export is byte-identical across two runs with the same
`--now`. Performance totals: stake 7270.7879, gross 6067.90, net -1068.3543 over 82 wagers with economics --
equal to the market-data postmortem's `established_subset` to the cent.

## Known gaps

* `recommendations.json` is empty until a non-`test_only` record is committed to `handicap-data`.
* Rows the incumbent does not support (4,301 UNSUPPORTED_MODEL, 692 UNSUPPORTED_RULES, 116
  UNSUPPORTED_IDENTITY in week 4) have no `model_price`; their Shadow v2 `p_yes` is visible on the market
  (`extensions.shadow_v2_p_yes`) but is research and is not promoted to a price.
* `incumbent.model_uncertainty` is null on every row, so `uncertainty`, `lower_bound`, `upper_bound` are null.
* The report does not say whether a started game is live or final, so such events are `UNKNOWN`.
* Past-week events need `--market-data-root` for real kickoffs; without it they carry a PLACEHOLDER date.
* The board lists every event in the bundle (past wagered games included) because the contract requires
  every wager's event to be present; the app should filter on `status` / `extensions.on_board`.
* Payload size: ~37 MB (markets 13 MB, event_detail 19 MB) for a 10.7k-contract slate; the branch already
  carries a 64 MB packet, but a slimmer event_detail would help mobile readers.

## Contract feedback

* `board.build_board` has no notion of "current slate"; a `scope`/`on_board` filter in the contract would
  avoid every repository re-inventing the same extension flag.
* `build.event` requires `start_time_utc`; a wager on a game the schedule cannot place forces a PLACEHOLDER
  date rather than a null with provenance.
* `market.player_id` is typed as a participant-id string but events carry no player participants, so the
  cross reference cannot be checked; either a `players` collection or a documented "unchecked" status would
  make the field honest.

## Research explorer (`app/latest/explorer/`, contract 1.1.0)

`scripts/research_export.py` publishes the research graph beside the v1 payload, from the same report, after
the v1 export has run:

    python3 scripts/research_export.py --reports-dir data/handicap_report --market-data-root /tmp/md \
        --out <staging>/app/latest [--now <aware ISO>]

It reads the v1 publication in `--out` (`manifest.json` `run_id` and `generated_at`, events, markets, model
prices, recommendations, wagers, settlements), so every `evt_` / `prt_` / `mkt_` id is the v1 one (teams:
`nflverse_team` codes through the same `build.participant` call; players: `gsis_id`; games:
`nflverse_game_id`). It refuses an app root whose `health.json` says the v1 export failed. Stdlib only, no
network, no model fitting: per-game averages, rankings, rolling means and quote compression are arithmetic
over stored values. `research.publish_explorer` stages and swaps, so a failure leaves the previous tree as it
was and the script exits 1.

### What is published, from where

| directory | count (week 4 real data) | source |
|---|---|---|
| `teams/` | 32 | packet `team_profiles` (28 raw metrics x SEASON / L6 / L34 where n_games >= 4, 22 opponent-adjusted ridge ratings), schedule results (game list for 4 seasons, record), injuries of the current game, team-subject markets + model prices within 150 KB |
| `players/` | 318 | only players with `simulation.player_projections` in the packet: simulated stat means (+ sd, p05..p95, market/final means in extensions), projected target / carry shares, QB profile rates (SEASON, L200_DROPBACKS, split `pressure`), availability (injury + depth chart, joined by name within team), player markets + model prices |
| `events/` | 51 | every v1 event. Board games: matchup rows (22 adjusted ratings + 3 season scoring metrics, home vs away with ranks), players, simulation distributions (player stats + margin / total / team points), injuries, depth charts, weather, venue, notes, packet `matchup.pairs` / quarterbacks / offensive line / game script / model view in extensions, game-level markets + projections within 150 KB. Past (wagered) games: markets, wager ids with outcomes and owner CLV, final score |
| `rankings/` | 53 | one per team metric per published window, over every team with a value |
| `series/` | 96 | points for / against / margin per completed game (last 40 per team, trailing 4-game mean), linked to the game and the opponent |
| `market_history/` | 16 | per board event: pregame capture quotes of the game-level FULL markets (game winner, spread, total, team total), main lines first, change points + 6 h heartbeat, hourly-thinned above 240 points, within 400 KB (422 tickers, 37,117 points) |
| `metrics.json` | 73 metrics | including `met_nfl.incumbent_fair_probability` whose `extensions.scorecard` carries the incumbent cumulative scorecard (calibration bands, Brier / log loss vs market, CLV, per family) |

Measured bytes per directory (`research.tree_bytes`, real 2026-10-02 report): teams 4,526,848; players
6,677,718; events 2,470,069; market_history 6,057,752; rankings 481,265; series 1,206,729; metrics.json
152,970; search_index.json 169,286; index.json 141,638 (compact since contract 1.1.1); capabilities.json
19,432 -- 21.9 MB in all. Largest GAME packet (`packet.render_text`, contract 1.1.1): 63,415 chars (2026_04_JAX_CIN). Largest
files: team 144,994, event 144,956, player 62,972, market history 379,225. The capture read covers ten days
before the earliest kickoff (1,380 quote files for week 4).

### Capability statuses (audit 2026-10-03, section 4 matrix and section 10)

| status | capabilities | why |
|---|---|---|
| VERIFIED | historical_results, opponents, injuries, market_prices, market_price_history, player_props, team_props, game_markets, weather, calibration, historical_accuracy, clv, wager_history, search | production captures / schedule / scorecards / ledger; calibration, accuracy and CLV are research evaluations (the model trails the market) |
| PARTIAL | team_profiles, player_profiles, event_research, team_metrics, team_game_logs, opponent_adjustment, recent_form_windows, lineups, matchup_metrics, projection_distributions, raw_projections, advanced_stats, situational_splits, rankings, time_series, comparisons | current snapshot only; no committed history (silver tables rebuilt per run); fixed L6 / L34 windows; depth chart is intention, not snaps; projections research-only |
| RESEARCH | player_metrics, player_game_logs, usage | 2026 player values are not committed as a table; history only as 2016-2025 research parquets |
| UNAVAILABLE | schedule_strength, play_by_play, venue_effects | nothing computes SOS; pbp is never committed; no venue effect estimate |

OL quality metrics are not published (the packet states no blocking grades are captured; the injured/listed
linemen ride in event extensions). Home/away splits are listed as an UNAVAILABLE split dimension.

### Deliberately not published

Per-run incumbent model-probability history (`data/shadow/ledger`, too heavy for the export step), the 2025
backfill candles, Shadow v2 and three-arm arms, `research/game_model/ratings_snapshots.parquet` (parquet and a
different rating code path), per-game player logs, and any market history beyond the current week.

### Workflow

`run-nfl.yml` and `shadow-price.yml` run **"Export the Edge Finder research explorer"** (`id:
research_export`) immediately after the app export, `if: steps.app_export.outcome == 'success'`,
`continue-on-error: true`, writing into the same `$RUNNER_TEMP/app_out/app/latest`; the existing publish step
carries `explorer/` with `app/latest`. A final **"Fail the job if the research explorer export failed"** turns
the job red after the report is up. Since contract 1.1.1 `publish.publish` never prunes `explorer/`, so a failed
explorer run keeps the previous tree (whose `run_id` then names the previous publication). The step stays in
`shadow-price.yml` because that workflow republishes `app/latest` every two hours: without it the explorer
would describe an older payload (older markets and model prices) for most of the day. NFL publishes every
2 h, so no `research.refresh_due` gate is used; every run rebuilds the tree.

Tests: `tests/test_research_export.py` on `tests/fixtures/research_export/` (291 KB real slice).
