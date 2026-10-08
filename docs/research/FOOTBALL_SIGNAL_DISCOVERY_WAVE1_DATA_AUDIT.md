# nfl-edge-finder audit for NFL signal discovery (2026-10-08)

Repo `/home/user/nfl-edge-finder`, branch `claude/football-signal-discovery-wave1-6ug9z6`. HEAD `e6fb9e1`, which is the same commit as `main` and `origin/main`. I committed nothing and changed no tracked files. Test runs left three `__pycache__` directories, which I removed. Everything I wrote is under `scratchpad/nfl_audit/`.

## 1. Historical football data (nflverse bronze)

**Downloader.** `scripts/data/nflverse_download.py`. It fetches `https://github.com/nflverse/nflverse-data/releases/download/<release>/<file>` and writes the bytes unchanged to `data/raw/nflverse/<release>/`. Each file gets a row in `_manifest.jsonl` (url, retrieved_at, bytes, sha256, ETag, Last-Modified).
- Defaults are `--seasons 1999-2026`, `--only <releases>` and `--force`.
- `schedules` is now `games.csv.gz` (`games.csv` returns 404 since 2026-10-06). `derive_schedule_csv()` gunzips it to `games.csv`, which every reader opens.
- `SNAPSHOT_RELEASES=("injuries",)`. Each injuries download is also written as a content-addressed vintage through `nfl_edge/shadow_v2/vintage_snapshots.py`.
- One file comes from outside nflverse: dynastyprocess `db_playerids.csv`, from raw.githubusercontent.com.

**Catalog** (`catalog()`). I verified season boundaries with HTTP probes:

| release/file | seasons (verified) |
|---|---|
| `pbp/play_by_play_{s}` | 1999–2026; 2026 has 64 games, wks 1–4 |
| `schedules/games.csv.gz` | 1999–2026; 7,548 games, 2026 has 64 results |
| `stats_player/stats_player_week_{s}` (150 cols, includes `opponent_team`) | 1999–2026 |
| `stats_team/stats_team_week_{s}` | 2025 verified |
| `weekly_rosters/roster_weekly_{s}` (`status` ACT/INA/RES/DEV/CUT…) | 2002–2026 (2001 = 404) |
| `rosters/roster_{s}` | 2024–2026 verified |
| `snap_counts_{s}` (PFR ids) | 2012–2026 |
| `injuries_{s}` | 2009–2026 (2008 = 404) |
| `depth_charts_{s}` | 2001–2026 |
| `ftn_charting_{s}` | 2022–2026 |
| `pbp_participation_{s}` (offense_players, personnel, route, was_pressure, time_to_throw, coverage type) | 2016–2025; **2026 = 404** |
| `ngs_{passing,rushing,receiving}` | 2016–2026 |
| `advstats_week_{pass,rush,rec,def}_{s}` | 2018–2026 |
| `qbr_week_level`, `players`, `historical_contracts`, `officials` (2015–2026), `combine`, `draft_picks`, `trades`, `teams_colors_logos` | single files |

**Local state.** No bronze, silver or gold data is present: `data/` holds only `shadow/` and `shocks/`, and `data/raw`, `data/silver` and `data/gold` are gitignored. The README says a full pull is ~590 MB.

**Download test.** The repo's own script works unmodified. I ran a copy whose ROOT resolved into the scratchpad:
```
python3 scripts/data/nflverse_download.py --only pbp,schedules,injuries,depth_charts,stats_player,snap_counts,rosters,weekly_rosters,pbp_participation,players,ff_playerids --seasons 2024-2025
```
- That pull is 2 seasons × 11 releases, 65 MB, in **8.3 s**, all HTTP 200.
- `play_by_play_2024.parquet` is 20.6 MB (0.85 s; 49,492 rows × 372 cols). `play_by_play_2025.parquet` is 20.3 MB. `games.csv.gz` is 0.51 MB (0.28 s).
- In a repo checkout the plain command above writes to `data/raw/nflverse/` (gitignored). Workflows use `--seasons 2012-2026` or `2013-2026`.

**Schedule lines** (`games.csv`) are the only non-Kalshi historical lines:
- `spread_line` (positive = home favoured) and `total_line` are 100% populated 1999–2025.
- `away_moneyline`, `home_moneyline`, `away_spread_odds`, `home_spread_odds`, `over_odds` and `under_odds` are 0% before 2006, 82% in 2006, and 100% from 2007–2025.
- In 2026, 34% of games have lines, filled as weeks approach.
- The vintage is a single near-close consensus with undocumented timing (`docs/KNOWN_LIMITATIONS.md` #1), so **it is not point-in-time for any pre-close horizon**.
- Other columns: `temp`/`wind` are observed game-time values (post hoc). The file also has `away_qb_id`/`home_qb_id` (realised starters), `referee`, `roof`, `surface` and rest days.

**There is no historical player-prop line source other than Kalshi.** The Odds API was rejected as paid (`docs/DATA_SOURCE_AUDIT.md` L67/L72), and no sportsbook code exists in the repo.

## 2. Silver tables, opponent adjustment, player ID crosswalk

**`nfl_edge/data/silver.py`**
- `team_game_from_pbp(season)` produces one row per team-game with 83 columns. I measured 570 rows for 2024.
- Offence and defence aggregates are computed on pass/run scrimmage plays: EPA/play, success rate, dropback and designed-rush EPA, early-down EPA, non-garbage versions (`wp` between 0.05 and 0.95), explosive passes and runs, sacks, turnovers, PROE (`proe_early_ng`), CPOE, aDOT, red-zone EPA, no-huddle and shotgun rates.
- It also adds special-teams EPA for and against, FG made/attempted, and drive outcomes (TD, FG and turnover drives).
- `build()` defaults to 2006–2025 and writes `team_game_{s}.parquet`, `team_game.parquet` and `games.parquet`.
- **None of these are opponent-adjusted.** They are raw per-game values; all point-in-time joins happen downstream.

**Opponent-adjustment methods that exist**
1. `nfl_edge/research/team_ratings.py` (game model). Weighted ridge `y = off_t + def_opp + hfa·home` on strictly earlier team-games, with a 10-week recency half-life and ×0.4 per prior season.
2. `nfl_edge/sim/opponent_adjust.py` (`sim-oppadj-1.0.0`, research arm, not deployed). Ridge `y = mu + off[t] + def[opp] + h·home`, half-life 8 weeks, 0.5 season carry, 3-season window.
   - λ is chosen per metric on seasons Y−2 and Y−1 only.
   - 11 metrics: `epa_play`, `success_rate`, `dropback_epa`, `designed_rush_epa`, `explosive_rate`, `sack_rate`, `plays`, `sec_per_play`, `neutral_pass_rate`, `neutral_proe`, `td_per_drive`.
   - Output is the matchup expectation `mx_<metric>`.
3. `nfl_edge/features/defense.py`. Point-in-time EWMA of what each defence allowed (receptions, receiving and rushing yards, targets, carries, passing yards and TDs, yards per target and per carry), shrunk to the league mean. It is a defence-allowed feature; it does not adjust for the offences that defence faced.

**`nfl_edge/data/ids.py`.** The canonical key is the GSIS id.
- `build_player_crosswalk()` merges three sources with `*_src` provenance columns: `players.parquet`, `roster_{2016..2026}` (latest row per gsis) and dynastyprocess `db_playerids.csv`.
- It flags `espn_id_conflict` and `pfr_id_conflict`, and builds a normalised `name_key` (strips Jr/Sr/II…).
- My rebuild with 2024–25 rosters gave 24,844 players, 1 ESPN and 3 PFR conflicts, and 15 duplicated name keys among active players. Name is therefore never a join key.
- Snap counts join through `pfr_id`.

## 3. Projection engines

| engine | where | what it projects | point-in-time | role / injuries | uncertainty |
|---|---|---|---|---|---|
| Incumbent shadow pricer `shadow-0.4.0` | `nfl_edge/shadow/models.py`, `scripts/shadow/price_slate.py`, `nfl_edge/pricing/game_env.py` (40,000-draw residual bank) | game families (winner, spread, total, team total) centred on the Kalshi-implied line; player props from an EWMA mean plus a family per stat; anytime TD via `DirectTDModel` | fitted on prior seasons | role features OFF by default since H-022; availability multiplier `STATE_PLAY_RATES` | family distributions (H-007) |
| Sim engine `sim-1.1.0` | `nfl_edge/sim/*`, `scripts/sim/*` | one coherent Monte Carlo per game (team volume, script, shares, efficiency, TDs). Stats: carries, rush yds, targets, rec, rec yds, attempts, completions, pass yds, pass TD, any TD | walk-forward 2023–25 (and 2021–25 in `baseline_5y`); `tests/test_sim_pit.py` poisons later weeks | depth chart and weekly roster for eligibility; see the injury-handling note below | full lattice per player-stat; reconciliation weights `research/simulation_engine/reconciliation_weights.json` (only `any_td`=0.25 non-zero) |
| Player engine v2 `DATA_PLAYER_DIST` | `nfl_edge/engines/player/{features_v2,data_dist,market_dist,hybrid_dist}.py` | opportunity × efficiency; 11 stats including `rush_rec_yards` | yes | — | `LatticeDistribution` |
| v3 | `features_v3.py`, `prospective_v3.py` | v2 plus recency, and fixes for blank-line and missing-current-season input wiring | yes | — | — |
| v4 | `engines/player/v4/{snap,volume,model,features,prospective}.py` | snap → team volume → share with teammate redistribution → outcome | fit ≤ target−1 | teammate injury statuses from the cutoff's injury vintage | snap-share sd from a residual ridge |
| v5 | `engines/player/v5/*` | v4 plus a point-in-time QB resolution (`nfl_edge/context/qb_resolution.py`) and QB-identity features | same | QB Out → backup | same |
| Game, period, season, joint and coherence engines | `nfl_edge/engines/*.py` | score-function families, quarter/half markets (1H margin = 0.47+0.559·spread…), season Monte Carlo, composites | — | — | — |

**How the sim engine handles injuries.** `nfl_edge/sim/features.eligible_players`:
- It excludes weekly-roster `status != ACT`, which includes **INA**, the game-day inactive list.
- It excludes players designated Out or Doubtful on the week's **final** injury report.
- So the **historical backtests use game-day information**. `research/game_script_v2` and `research/simulation_engine/RECONCILIATION.md` mark T-24h as `NON_PIT_DESCRIPTIVE`.
- Prospectively it uses content-addressed injury vintages, plus Sleeper and ESPN captures at or before the cutoff (`nfl_edge/sim/prospective.py`).

**What counts as production.** `docs/PRODUCTION_ELIGIBILITY.md` and `nfl_edge/evaluation/eligibility.py` assign each arm a status:

| status | arms |
|---|---|
| WATCH | BOARD_V2, MARKET_PLAYER_DIST |
| RESEARCH_ONLY | DATA_PLAYER_V3/V4/V5 and the matching HYBRID arms |
| DISABLED | DATA_PLAYER_DIST (v2) |

- No arm is LIMITED or TRUSTED.
- The RUN NFL packet shows three views side by side: the incumbent, the coherent sim, and Shadow v2.

### Key research findings (seasons used → verdict)

**Game level**
- `game_model`, H-001 **REJECTED**. Opponent-adjusted EPA ridge on pbp 2006–25, tested 2014–25 (n=3,151; hyperparameters tuned on 2011–13).
  - Margin RMSE: model 13.26, close 12.88. Optimal blend weight on the model is 0.
  - Encompassing regression: 1.01 on the close, 0.03 on the model. ATS 50.0% (n=928).
- `ladder_calibration` (2016–25, 2,639 games). Empirical recency-weighted margin residual for spread ladders; Normal for totals.
  - σ(margin−spread) fell from 13.5–14.5 to 11.4–13.2. 4.7% of games finish within ±0.5 of the line.
- `edge_lab` quick effects (2010–25, at the close).
  - QB change −0.50 [−1.43, +0.44] (H-005 REJECTED_AT_CLOSE).
  - Wind 10–20 mph −0.9 to −1.3 (H-006 PROMISING; needs forecast vintages, H-014).
  - Rest, Thursday, divisional, temperature and neutral site are all priced.
- `game_script_v2` (2021–25): the lattice NEEDS MORE WORK.
  - Score-path arm P1 REJECTED. Opponent-adjustment arms A1–A5 and R1 REJECTED: 0.15–0.21% CRPS gain against a 0.5% bar.
  - "Better ratings, but the game centre is the market's and player share dominates the error."
- `three_arm` (H-026): the CURRENT / DATA_ONLY / HYBRID_30 game centre runs prospectively; nothing tested yet.

**Kalshi 2025 archive**

`efficiency_map` covers all 54,364 settled markets, using books ≤10¢ wide, BH q=0.10.
- Props are overpriced on the YES side by about −0.03 to −0.04 for mids above 0.35, and calibrated below 0.20. Net after fees is negative (YES −0.055 to −0.086; NO −0.013).
- Spreads and totals are efficient.
- GAME_WINNER shows a favourite-longshot pattern (+0.054 / +0.044 for dogs at 0.20–0.50, about 1.1 SE; H-019).
- Pregame movement is directionless (moves toward the outcome 0.48–0.52 of the time).
- First-TD and receptions results inverted once restricted to tradable books (H-016 REJECTED).

`model_vs_market` (18,555 contracts, 254 games):
- The market beats the model on Brier by +0.00999 ± 0.00162. Trading the disagreement nets −0.031 per contract at any threshold.
- Logit encompassing gives market ≈0.94–0.97 and model ≈0. That holds with role features and with opponent-defence features (opponent defence is the best standalone model and still fully encompassed). H-011 LARGELY_ANSWERED; H-018.

Other 2025-archive studies:

| study | finding | verdict |
|---|---|---|
| `residual_pit` (98,169 point-in-time obs) | model predicts later market movement (b=+0.033, z=2.8 at T-24h; CLV +0.002) | executable net negative in every bucket (H-020) |
| `market_prior` | 64% of model–market disagreement is location, 26% shape, 10% residual; passing yards fit Weibull poorly | — |
| `joint_structure` (202 games, 399k cross-player pairs) | after leg debiasing, no unpriced cross-player dependence | tail dependence not tested |
| `listed_validation` (24,731 rungs) | role features +0.00029 ± 0.00072 | role features **RETIRED** (H-022: "full-population gains do not transfer to listed players", 3 of 3) |
| `tail_calibration` (2019–25) | model long-shot rungs are overconfident (0.033 → 0.023) | the calibrator reverses on listed rungs (H-015 IN_DOUBT) |
| `kalshi_2025/RESULTS_prop_model` | families fitted on 2016–24, scored on 2025 rungs: positive skill against base rate; passing yards over-predicted at 300+ (0.194 vs 0.125) | — |

**Player level**

`player_distributions` (2016–25, tested 2020–25) picked a family per stat:

| stat | family |
|---|---|
| receiving and rushing yards | empirical, binned by mu |
| passing yards | censored Normal |
| targets, receptions, carries | negative binomial |
| attempts, completions | Normal |
| passing TDs | Poisson |
| anytime TD | direct binary model (count families under-predict 1+ by 2–3 points) |

- `anytime_td`: the direct logistic beats every count family in 6 of 6 seasons.
- `opportunity` (2016–25, tested 2019–25):
  - Multiplying team volume by player share is **rejected** for targets and carries.
  - Role features added to the EWMA help in 7 of 7 seasons on the full population, but not on listed players.
  - Team volume is barely predictable: MAE 6.62 against 6.93 for a constant.
- `role_features` (2018–24): snap share is the main gain (−2.7% to −7.1% MAE).

Player engines v2→v5 against the 2025 market midpoint:
- v2/v3 ≈ +0.0085 Brier worse than the market. Production v2 failed because blanked lines were read as a zero-point implied total.
- v4 halves that gap to +0.0043 at T-90m but is still worse than the market at every horizon. Passing TDs is at parity.

Sim engine:
- Walk-forward 2023–25 beats the prior-only projection on every stat.
- Against 2025 rungs at the close it is worse than the market on every stat except passing TD (−0.0021).
- Reconciliation deploys a weight only for any_td (0.25).

`availability` (2015–25):

| designation | play rate |
|---|---|
| Questionable | 0.690 |
| Doubtful | 0.007 |
| Out | 0.0005 |

H-008 VALIDATED.

**Registry** (`research/hypothesis_registry/registry.md`, 28 entries plus 26 rows in `v2/hypotheses.jsonl`):

| status | hypotheses |
|---|---|
| REJECTED | 001, 016 |
| REJECTED_AT_CLOSE | 005 |
| VALIDATED_RESEARCH | 007, 008 |
| PROMISING | 006 |
| TESTING | 003 |
| IN_DOUBT | 015 |
| LARGELY_ANSWERED | 011 |
| PROPOSED | 004 (WR height vs CB), 009 (red-zone anytime TD), 028 (QB starter) |
| REGISTERED_PROSPECTIVE (on 2026) | 010, 012–014, 017–027 |

Board-miner preregistrations:
- H-20261001-B01…B11 were generated from 2026 **weeks 1–3** (48 games) and test 2026 weeks 4–18. They cover mid buckets, high-ask fee-adjusted returns, rungs adjacent to the main rung, team total vs spread, role certainty, and momentum.
- H2-GC-MARGIN/TOTAL-2026W02 were generated from week 2 and test weeks 3–18.

**Contamination map**

| data | how it has been used |
|---|---|
| nflverse 2006–2025 | fully mined at game level |
| player stats 2013/2016–2025 | fully mined |
| 2025 Kalshi archive | heavily mined: efficiency map, model_vs_market, residual_pit, v2–v5, reconciliation weights **fitted on 2025** |
| 2026 week 2 | diagnosis for v3 |
| 2026 weeks 1–3 | weekly research, board discovery and hypothesis generation |
| 2026 weeks 4+ | the only clean prospective holdout; already preregistered for B01–B11 and GC |

## 4. Market data (`market-data` orphan branch)

How to access it:
- `git fetch --filter=blob:none origin market-data` takes 4 s (6,109 commits, 75,390 files, newest pass 2026-10-08T18:24Z).
- A full shallow clone is **12 GB and took 6.4 min**. I deleted it after analysis.
- For bulk reads, use `git cat-file --batch`.

**Workflows** (`.github/workflows`):
- `kalshi-conductor.yml` and `kalshi-capture.yml` loop about every 10 minutes and are change-suppressed.
- `kalshi-discover.yml` runs daily and records every market in every status, which is where settlements come from.
- `kalshi-backfill*.yml` handles the historical tier.

**2026 prospective capture** (`data/kalshi/capture/<date>/<run>.{quotes,books,trades,live}.jsonl`, `.manifest.json`, `.openset.json`):
- Runs from **2026-09-04T11:48Z to 2026-10-08T18:12Z**: 4,300 quote files, **12,846,303 quote rows**, 22.3 GB uncompressed (quotes 12.2 GB, trades 6.6 GB, books 2.7 GB).
- Cadence is 92–144 runs per day; 144 per day means a full 10-minute cadence.
- Coverage: 69,166 tickers, 5,196 events, 79 games (2026 weeks 1–5, week 5 in progress), 526 Kalshi player ids.
- Each row carries `yes_bid/yes_ask/no_bid/no_ask_dollars` (both asks captured), YES-side top-of-book sizes, last price, volume, OI, status, classifier fields, `game_id`, `kickoff_utc`, `minutes_to_kickoff` and `pregame`.
- Books are depth-10 for both YES and NO, within 72 h of kickoff. Trades carry `taker_side` and `count_fp`.
- **The quote stream never contains settled rows.** Settlement comes from discovery: the 20261008 run lists 71,799 settled markets, 57,583 of them 2026 Sep/Oct events (`result`, `settlement_value_dollars`, `settlement_ts`), which covers weeks 1–4.
- Close construction: `nfl_edge/evaluation/close.py` (last change before the cutoff, confirmed by a run that fetched the series). In my approximation, a last pregame executable quote within 60 minutes of kickoff exists for about 80–84% of player-yardage tickers. Because rows are change-suppressed, that figure undercounts.

**Player props with executable pregame quotes** (yes_ask and no_ask both inside (0,1)). Tickers by 2026 week, distinct players in brackets:

| stat | wk1 | wk2 | wk3 | wk4 | wk5 (partial) | total |
|---|---|---|---|---|---|---|
| receiving_yards | 1429 (192) | 1416 (189) | 1384 (191) | 1508 (205) | 941 (114) | 6,678 |
| receptions | 1214 (192) | 1182 (186) | 1205 (191) | 1269 (201) | 434 (72) | 5,304 |
| rushing_yards | 801 (91) | 777 (87) | 791 (94) | 841 (96) | 620 (72) | 3,830 |
| touchdowns (anytime) | 716 (398) | 688 (366) | 742 (375) | 748 (387) | 605 (321) | 3,499 |
| passing_yards | 287 (33) | 275 (32) | 263 (32) | 287 (32) | 260 (29) | 1,372 |
| carries | 461 (68) | 167 (57) | 167 (57) | 181 (62) | 46 (18) | 1,022 |
| attempts / completions | 363 / 358 | 96 / 89 | 96 / 95 | 96 / 88 | 44 / 43 | 695 / 673 |
| passing_tds | 132 | 134 | 124 | 133 | 116 | 639 |
| interceptions | 99 | 95 | 96 | 96 | 51 | 437 |
| rush_rec_yards | 132 | 135 | 132 | 137 | 36 | 572 |
| fantasy_points / longest_reception / longest_rush / field_goals | — | — | — | — | — | 857 / 723 / 323 / 592 |

**Game-level families with executable quotes**, per week (about 16 games):

| family | tickers per week |
|---|---|
| SPREAD full game | ~405–415 |
| TOTAL full game | 304 |
| TEAM_TOTAL full game | ~435 |
| TEAM_TOTAL 1H | ~350 |
| SPREAD 1H/2H | ~250 |
| TOTAL 1H/2H | ~217 |
| SPREAD per quarter | ~165–175 |
| TOTAL per quarter | 160 |
| FIRST_TD_SCORER / FIRST_TD_TEAM | ~400 / ~460 |
| RACE_TO_N | ~240 |
| HALF_FULL_RESULT | ~140 |
| WIN_MARGIN_BUCKET | ~97 |
| PERIOD_WINNER (each period) | ~47 |

GAME_WINNER has 186 tickers over 93 games. The registry (`config/kalshi_nfl_series.json`) lists 392 series in about 60 families.

**Other data on the branch**
- `data/context/` holds about 3-hourly captures since 2026-09-04: ESPN injuries (141), Sleeper (143) and weather forecast vintages (146).
- `data/shadow/v2/` holds projections, closes, settlements, depth, inactives, eligibility, scorecards and similar outputs.
- `data/raw/nflverse/_vintages/injuries/` has **44 distinct `injuries_2026` snapshots (2026-09-13 to 2026-10-06)**. Seasons 2012–2025 have one snapshot each (the final file).

**2025 historical Kalshi data** (`data/kalshi/backfill/`, from the `/historical` API)
- `markets/<series>.jsonl` covers 381 series: **61,557 archived markets, 61,068 settled**, close times 2025-01-12 to 2026-06-17.
- `horizons/{0..5}.jsonl` (84 MB) has **54,364 settled markets**, each with a snapshot at T-168h, 72h, 48h, 24h, 12h, 6h, 3h, 90m, 30m and T-0.
  - Snapshot fields: `{bid, ask, last, mean, vol, oi, book_empty, ts, age_min}`.
  - These are **YES bid/ask only**, from 60-minute candles (last 14 days) plus 1-minute candles (final 3 h). The NO ask has to be taken as 1−YES bid.
  - Settled counts:

| family / stat | settled | ≤10¢ wide at T-0 | games |
|---|---|---|---|
| PLAYER_STAT receiving yards | 10,170 | 6,827 | 189 |
| PLAYER_STAT touchdowns | 7,471 | — | — |
| PLAYER_STAT receptions | 7,358 | — | 148 |
| PLAYER_STAT rushing yards | 4,625 | — | — |
| PLAYER_STAT passing yards | 3,248 | — | — |
| PLAYER_STAT passing TDs | 812 | — | — |
| SPREAD | 7,420 | — | 264 |
| TOTAL | 5,918 | — | — |
| FIRST_TD | 5,355 | — | — |
| TEAM_TOTAL (wk 14–15 and playoffs only) | 809 | — | — |
| GAME_WINNER | 658 | — | 260 |
| 1H/1Q families | < 100 each | — | — |

  - Player ladders are thin before 2025 week 6 (363–486 per week) and run 1.3k–2.8k per week from week 6 on.
- `candles/` and `trades/` hold 1-minute candles and full trades for **KXNFLGAME (658)** and **KXNFLSPREAD (349, Jan–Feb 2026 only)**.
  - Discrepancy: H-025 says 2025 regular-season spread ladders were not listed. That is true of the 1-minute archive, but `horizons/` does contain regular-season SPREAD snapshots for 2025 weeks 1–22.
- Committed derivatives:

| file | contents |
|---|---|
| `research/kalshi_2025/archived_markets.parquet` | 61,557 × 16 |
| `prop_model_probs_2025.parquet` | 24,731 rungs |
| `research/residual_pit/pit_dataset_p_base.parquet` | 98,169 rows |
| `research/shocks/shocks_2025.parquet` | 2025 shock log |
| `research/passive/passive_orders_2025.parquet` | 2025 passive-order sample |

**Fees and settlement**
- `nfl_edge/execution/fees.py` implements the 2026 fixed-point fee model: quadratic coefficient × p(1−p), trade fee rounded up to $0.000001, rounding fee, per-order rebate accumulator, maker fees, and KNOWN/UNVERIFIED/CONFLICTED states. Studies used `ceil(0.07·p(1−p)·100)/100`.
- Settlement modules:
  - `nfl_edge/settlement/settle.py` is the incumbent.
  - `settle_v2.py` handles extended families.
  - `kalshi_settlement.py` handles scalar settlement for players who are active but take no snap.
  - `availability.py` and `nflverse_results.py` derive results from schedules, stats_player and snap_counts.
- Rule to remember: an inactive player's contract settles NO.

## 5. Kalshi player identity

`scripts/kalshi/build_player_map.py` maps `custom_strike.football_player` UUIDs (from `nfl_edge/kalshi/classifier.py`) to GSIS. The evidence is the modal title name, the team token and the jersey token from the ticker. Matching runs in this order:
1. Exact normalised name plus team within `roster_{season}`.
2. If the name matches several roster players, the jersey number breaks the tie.
3. A jersey disagreement after a match is recorded as `RESOLVED_JERSEY_MISMATCH`.
4. A name unique in the season roster gives `RESOLVED_TEAM_UNCONFIRMED`.
5. A name unique among recent players in `players.parquet` gives `RESOLVED_PLAYERS_TABLE`.
6. Anything else is `UNRESOLVED`. D/ST and "No Touchdown" legs are `NOT_A_PLAYER`.

There is no fuzzy matching; the only alias table is `NAME_ALIASES` (two entries). The output is `data/silver/kalshi_player_map.parquet`, rebuilt by the workflows. For 2025 it resolved 454 players (424 by exact name+team) and left 98 unresolved, mostly D/ST. Downstream, `engines/player/abstention.py` applies `ABSTAIN_IDENTITY`.

## 6. Injuries, depth charts and context

**Injuries**
- 2024 files have `date_modified`; **2025 and 2026 have no row timestamp**, and the file is rebuilt in place.
- Point-in-time access therefore needs the content-addressed vintages (`shadow_v2/vintage_snapshots.resolve_injuries`), which exist only from 2026-09-13.
- Historical seasons have only the final report, with `report_status`/`practice_status` per week (2025: 6,068 rows).

**Depth charts**
- 2001–2024 are weekly files with a `week` column (NFL Data Exchange schema, with `depth_team`).
- **2025 and 2026 are ESPN daily scrapes with an ISO `dt`**:
  - 2025: 554,215 rows, 221 distinct `dt` from 2025-08-03 to 2026-03-14.
  - 2026: 622,339 rows, 224 `dt` from 2026-03-22 to 2026-10-08.
- `nfl_edge/context/role.py::DepthChartBook` takes the newest `dt <= cutoff` per team, offensive slots only.

**Weekly rosters.** INA is the game-day inactive list. It is only point-in-time at T-90m and is not timestamped.

**`nfl_edge/context`**
- `role.py`: depth book and role certainty.
- `qb_resolution.py`: point-in-time QB1 that respects Out designations.
- `weather_vintages.py`: kickoff-hour forecasts per capture.

Inactives are captured prospectively by `scripts/shadow_v2/capture_inactives_v2.py`.

## 7. Tests

- Command: `python -m pytest -q -x`. It needs numpy, pandas, polars, scipy, pyarrow, pyyaml and pytest; the system Python lacked pyarrow and pytest, so I used a scratch venv.
- Result on HEAD (= main): **2931 passed, 9 skipped in 157 s**.
- CI runs `.github/workflows/tests.yml`. `tests/test_ci_dependencies.py` checks that `requirements-test.txt` stays complete.

## 8. Production surfaces that must not change

**Pinned by hash** in `tests/test_incumbent_unchanged.py::SOURCE_PINS`:
- `nfl_edge/pricing/game_env.py`, `pricing/market_implied.py`, `settlement/semantics.py`
- `handicap/gates.py`, `handicap/risk.py`, `handicap/schema.py`, `handicap/preflight.py`
- `config/risk_policy.json`
- `nfl_edge/shadow/ledger.py`, `shadow/models.py`, `scripts/shadow/price_slate.py`
- the frozen Week-1 lineage `research/FREEZE_WEEK1_2026.json`

**Production paths**
- RUN NFL: `scripts/handicap/run_nfl.py`, `nfl_edge/handicap/*` (coverage, `shadow_v2_block`, `sim_block`, `script_block`, packet, render, analysis, horizons), `nfl_edge/board/*`.
- Shadow v2: `nfl_edge/shadow_v2/*`, `nfl_edge/projection/*`, `nfl_edge/engines/*`, `nfl_edge/evaluation/*` including eligibility, `scripts/shadow_v2/*`.
- Settlement: `nfl_edge/settlement/*`. Fees: `nfl_edge/execution/*`.
- Capture: `nfl_edge/kalshi/*`, `scripts/kalshi/*`, `scripts/ci/publish_market_data.py`.
- Data: `scripts/data/nflverse_download.py`, an entrypoint for 9 workflows.
- App export: `scripts/app_export.py` and `contract/edge_finder_contract/*`, which publish to `handicap-reports/app/latest`.
- Imported (routed) wagers from the `kalshi-router/{NFL,backfill-NFL,settle-NFL}` branches: `scripts/handicap/import_routed_*`, `contract/.../routed_ledger.py`.

**Workflows**: `run-nfl.yml`, `run-nfl-horizons.yml`, `shadow-price.yml`, `shadow-v2-{project,horizons,horizon-conductor,settle,depth}.yml`, `kalshi-{conductor,capture,discover,backfill*,fee-health}.yml`, `postgame-settle.yml`, `preflight*.yml`, `horizon-conductor.yml`, `three-arm-horizons.yml`, `actual-wagers.yml`, `sync-handicap-airtable.yml`, `context-capture.yml`, `workflow-health.yml`, `wave2-research.yml`, `weekly-research.yml`.

**Branches**: `market-data`, `handicap-reports`, `handicap-data`, `kalshi-router/*`.

## Dataset matrix

| dataset | seasons | timestamp safety | opponent-adjustable | prospective reproducibility |
|---|---|---|---|---|
| pbp | 1999–2026 (wk 1–4) | postgame; safe if strictly prior games are used | yes (posteam/defteam; `team_ratings`, `opponent_adjust`) | yes (republished in place) |
| schedules lines (spread/total; ML/odds from 2006–07) | 1999–2026 | **near-close, untimed: not PIT before the close** | n/a (market) | overwritten, so no early-week vintage |
| schedules scores / QB ids / referee | 1999–2026 | postgame (`*_qb_id` are realised starters) | — | yes |
| stats_player_week | 1999–2026 | postgame | yes (`opponent_team`) | yes |
| snap_counts | 2012–2026 | postgame | via team join | yes |
| pbp_participation (routes, personnel, coverage) | 2016–2025 | postgame | yes | **no in-season 2026 file (404)** |
| ftn_charting | 2022–2026 | postgame (`date_pulled`) | yes | yes |
| ngs / pfr advstats / qbr | 2016+ / 2018+ / 2006+ | postgame | partial | yes |
| weekly_rosters | 2002–2026 | INA is game-day; not timestamped | — | weekly file, mutable |
| injuries | 2009–2026 | 2024 has `date_modified`; 2025–26 none, mutable | — | only from 2026-09-13 vintages (44 snaps) |
| depth_charts | 2001–2024 weekly; 2025–26 daily `dt` | **PIT-safe from 2025** | — | yes (`dt <= cutoff`) |
| officials | 2015–2026 | no timestamp | — | single file, mutable |
| Kalshi 2025 horizons | 2025 season | horizon-stamped candles (age_min) | n/a | fixed archive; YES side only |
| Kalshi 2026 capture | 2026-09-04→ | timestamped every ~10 min | n/a | append-only, immutable |
| Context (Sleeper/ESPN injuries/weather) | 2026-09-04→ | timestamped vintages | — | yes |

## Bottom line

- Game-line, prop-mean, opponent-defence, role and joint-dependence edges have all been tested against the 2025 close and rejected or encompassed.
- The open avenues are:
  - early-week timing (H-002/020, which is CLV-positive but not executable)
  - forecast-vintage weather (H-014)
  - the GAME_WINNER longshot pattern (H-019)
  - QB-resolution and availability timing (H-021/025/028)
  - prospective 2026 weeks 4+ preregistrations (B01–B11)
- Any new 2025-archive analysis reuses an already heavily mined season.
