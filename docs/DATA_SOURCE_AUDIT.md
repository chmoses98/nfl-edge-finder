# Data Source Audit (Milestone A)

Date of audit: 2026-09-04 (five days before the 2026 NFL kickoff, SEA vs NE on 2026-09-09).
Everything below was verified by actually downloading/querying the source unless marked *not verified*.

## 0. Environment constraint that shapes the architecture

The development sandbox's egress proxy allows only GitHub (release downloads, raw files, git) and PyPI.
It **blocks** api.elections.kalshi.com, api.weather.gov, ESPN, Sleeper, Open-Meteo, PFR, huggingface.co and every
other host tried. GitHub Actions runners have normal egress. Therefore:

* nflverse bronze data is pulled directly in the sandbox (release URLs) and in Actions;
* all Kalshi and live-source collection runs **inside GitHub Actions** in this repo and is published to the
  orphan branch `market-data`, which the sandbox then fetches with git;
* every fallback source must be probed **from the runner** before it is called a fallback (the CFB project's
  ESPN fallback returned 403 only from runners).

## 1. nflverse (primary football data) — verified by download

Release URL pattern: `https://github.com/nflverse/nflverse-data/releases/download/<release>/<file>`.
License: nflverse data is CC-BY 4.0 unless stated otherwise (FTN charting/participation CC-BY-SA 4.0). Free, no key, no rate limits observed. `scripts/data/nflverse_download.py` writes a manifest (url, retrieval time, bytes, sha256, HTTP Last-Modified) for every file.

| release / file | seasons (verified) | rows / size | last modified (upstream) | in-season latency (documented / observed) | role |
|---|---|---|---|---|---|
| `pbp/play_by_play_{s}.parquet` | 1999–2025 (2026 file appears after week 1) | 372 cols, ~49k plays/season, 488 MB total | 2025 file: 2026-08-13 | nightly during season | **primary** for team/QB/player modelling, EPA, WP, xpass, cpoe, drives |
| `schedules/games.csv` | 1999–2026 (2026 full 272-game slate present) | 7,548 rows, 46 cols incl. `spread_line`, `total_line`, moneylines, `roof`, `surface`, `temp`, `wind`, QBs, coaches, referee, stadium | 2026-09-04 | daily; **2026 lines present for weeks 1–5 and a few later games** | primary schedule + historical closing-line proxy (Lee Sharpe's games file; line vintage is undocumented, treat as "near-close consensus", not a timestamped close) |
| `stats_player/stats_player_week_{s}.parquet` | 1999–2025 | 150 cols; offense+defense+kicking per player-game | 2026-08-26 | nightly | player prop targets (yards, receptions, TDs, attempts, completions…) |
| `stats_team/stats_team_week_{s}.parquet` | 1999–2025 | 138 cols | 2026-08-26 | nightly | team box aggregates |
| `rosters/roster_{s}.parquet` | 1999–2026 (2026 present, 3,118 rows) | ids: gsis, espn, sportradar, yahoo, rotowire, pff, pfr, fantasy_data, sleeper, esb, smart | 2026-09-03 | daily | current roster + ID crosswalk |
| `weekly_rosters/roster_weekly_{s}.parquet` | 2002–2026 (2026 week 1 present) | status per player-week (ACT/RES/CUT/PUP/SUS…) | 2026-09-02 | weekly | point-in-time roster status |
| `depth_charts/depth_charts_{s}.parquet` | 2001–2026 | **2026: 494k rows timestamped `dt` from 2026-03-22 to 2026-09-03** (ESPN source, daily snapshots incl. preseason) | 2026-09-03 | daily | depth-chart vintage series — point-in-time safe from 2026 onward; pre-2025 files are the old NFL Data Exchange structure (weekly) |
| `injuries/injuries_{s}.parquet` | 2009–2025; **2026 file not yet published** | report_status (Out/Doubtful/Questionable), practice_status (DNP/Limited/Full), body parts, per team-week; no timestamps | 2025 file 2026-03-18 | unknown until observed in-season (was weekly historically) | historical availability modelling; **not** a live injury feed |
| `snap_counts/snap_counts_{s}.parquet` | 2012–2025 | offense/defense/ST snaps & pct, keyed by `pfr_player_id` + `game_id` | 2026-02-09 | weekly after games (PFR source) | role inference, "played but zero" rows |
| `ftn_charting/ftn_charting_{s}.parquet` | 2022–2025 | per play: motion, play action, RPO, screens, n_pass_rushers, n_blitzers, box count, QB out of pocket, catchable/contested/drop, interception-worthy, qb_fault_sack | 2026-09-01 | within 48h of each game, 4×/day updates | **rich free charting** — pressure/blitz/box/motion research (CC-BY-SA) |
| `pbp_participation/pbp_participation_{s}.parquet` | 2016–2025 | offense/defense players on every play, formation, personnel, defenders_in_box, pass rushers, time_to_throw, was_pressure, route (99.98% filled 2025), coverage type (49% filled) | 2025 file 2026-02-10 | **only after the season ends (FTN)** | matchup research (WR vs DB on-field), *not* usable for current-week features |
| `nextgen_stats/ngs_{passing,rushing,receiving}.parquet` | 2016–2025 (one file per stat) | receiving: cushion, separation, intended air yards, YAC over expected; passing: time to throw, aggressiveness, CPOE; rushing: efficiency, RYOE | 2026-09-02 | weekly | player efficiency features (week-level, qualifying players only) |
| `pfr_advstats/advstats_week_{pass,rush,rec,def}_{s}.parquet` | 2018–2025 | pressures, hurries, hits, blitzes, bad throws, drops, broken tackles, coverage stats allowed by defender | 2026-02-11 | weekly | OL/pressure proxies, defender coverage quality |
| `espn_data/qbr_week_level.parquet` | 2006–2025 | ESPN QBR components | 2026-09-03 | weekly | QB model feature |
| `players/players.parquet` | all | 25,065 players; gsis/esb/nfl/pfr/pff/otc/espn/smart ids, height/weight/DOB/draft | 2026-09-02 | daily | canonical player table |
| `combine/combine.parquet` | 2000–2026 | 40, vertical, broad, cone, shuttle, bench, ht/wt (pfr_id, cfb_id) | 2026-03-12 | yearly | athletic profile |
| `draft_picks/draft_picks.parquet` | 1980–2026 | pick, team, gsis/pfr/cfb ids | 2026-09-02 | yearly | draft capital priors |
| `contracts/historical_contracts.parquet` | all (OTC) | APY, guarantees, contract history | 2026-09-03 | ongoing | incentives research (weak) |
| `officials/officials.parquet` | 2015–2025 | crew per game | 2026-09-02 | weekly | referee effects |
| `trades/trades.parquet`, `teams/teams_colors_logos.parquet` | — | — | 2026-05 | — | misc |
| dynastyprocess `db_playerids.csv` (raw.githubusercontent.com) | current | 12,484 players × 20 id systems (mfl, sleeper, espn, yahoo, cbs, pfr, rotowire, fantasypros, sportradar, cfbref…) | 2026 | weekly | crosswalk fallback |

Season-availability caveats discovered: NGS starts 2016; FTN charting 2022; participation 2016 (2023+ from FTN and only post-season); snap counts 2012; pfr advstats 2018; injuries 2009 (2026 not yet). nflverse switched depth charts and player stats from NFL Data Exchange to ESPN in nflreadr 1.5.0, so pre/post structures differ.

### ID coverage (players active in 2025+, n=3,545)
espn 98.7%, pff 96.8%, pfr 91.2%, sleeper/sportradar/rotowire 67.8% (roster-derived). 13 espn-id and 3 pfr-id conflicts between players.parquet and rosters are flagged in `data/silver/player_crosswalk.parquet` (`*_conflict` columns). 19 active players share a normalized name with another active player, so name matching is never a join key.

## 2. Kalshi (market data + execution venue) — verified via GitHub Actions run 2026-09-04

* Base: `https://api.elections.kalshi.com/trade-api/v2`; public GETs need **no auth**. 2,649 requests at 4 rps drew **zero** HTTP 429s.
* Catalogue: 13,794 series exchange-wide, 3,612 in category Sports. 392 series are NFL-related after filtering (registry `config/kalshi_nfl_series.json`); 183 had at least one market; **23,275 NFL markets** were in the live tier on audit day (open+settled), plus the entire 2025 season in the *historical* tier (cutoff 2026-07-05: markets settled before it are only reachable via `/historical/markets`, `/historical/trades`, `/historical/markets/{t}/candlesticks`).
* Fields captured verbatim (see docs/KALSHI_API_NOTES.md): dollar-string prices (`yes_bid_dollars`…), `open_interest_fp`, `volume_fp`, `liquidity_dollars`, `floor_strike`, `strike_type`, `custom_strike` (Kalshi's own `football_team` / `football_player` UUIDs), `rules_primary`, `result`, `settlement_value_dollars`, `settlement_ts`, `expiration_value`.
* Order book: `/markets/{t}/orderbook` → `orderbook_fp` with `yes_dollars`/`no_dollars` levels `[price, size]`. **No historical order books exist**; only trades + bid/ask candlesticks (1/60/1440-minute). This is why prospective capture started immediately.
* Fees (from series detail): all NFL series `fee_multiplier: 1`; game winner/spread/total, anytime/first TD, awards, division/conference/SB use `quadratic_with_maker_fees`; all other families `quadratic` (taker only).
* Liquidity on audit day (T-5 days): week-1 game winners had $20k–$370k volume per side; player prop ladders mostly quoted with $0 volume and wide books (e.g. 0.29/0.31 spread on a KC -7.5, but 0.05/0.44 on a 1H spread).
* Role: **primary** market source (execution venue) and **primary** price history. Fallback: none for Kalshi itself; source health is monitored by manifests.

## 3. Reference sportsbook lines

| source | what | verdict |
|---|---|---|
| nflverse `games.csv` spread/total/moneyline | one consensus line per game, 1999–2026, vintage undocumented (near close) | **primary historical benchmark**; not timestamped, so no open/close split |
| The Odds API | live + historical props, Pinnacle | paid beyond 500 req/month; historical tier $99/mo → **rejected** for production |
| Princeton historical odds DB | NFL 2009–2023 open/close | academic access only → research-only, *not verified* |
| scoresandodds / sportsbookreview / covers pages | scraped consensus | blocked from sandbox; brittle HTML; **not adopted** (would need Actions-side scraping and ToS review) |
| Polymarket gamma API | NFL winner markets | blocked from sandbox; free; could be a second prediction-market reference from Actions → **candidate fallback, not verified** |

Honest gap: there is no sustainable free source of timestamped sportsbook **player-prop** lines. Kalshi's own price history (captured from now on) becomes the prop reference; the nflverse line covers game markets.

## 4. Injuries / availability

| source | verified? | notes |
|---|---|---|
| nflverse injuries | yes (2009–2025) | official report statuses by team-week; no intra-week timestamps; 2026 not yet published |
| nflverse weekly rosters + depth charts (ESPN, daily `dt`) | yes | best free *timestamped* availability signal: status changes (ACT→RES/IR) and depth-chart moves are dated |
| ESPN core API `.../teams/{id}/injuries` | blocked in sandbox; CFB found `site.api.espn.com` 403s from runners while `site.web.api.espn.com` and `cdn.espn.com/core/...?xhr=1` work | **candidate**, must be probed from Actions |
| Sleeper `/v1/players/nfl` (injury_status, depth_chart_order, practice) | blocked in sandbox; free public, no key | **candidate** for game-day inactives-style updates, to be probed from Actions |
| NFL.com injury pages | no API; scraping not adopted | — |
| Sportradar / Injury Expertz / FantasyPros API | paid | rejected |

## 5. Weather

| source | verified? | notes |
|---|---|---|
| NWS api.weather.gov | blocked in sandbox; free, public, no key; hourly forecast + gridpoints | **primary** (from Actions), forecast vintages recorded at capture time |
| Open-Meteo | blocked in sandbox; free non-commercial 10k calls/day; has *Historical Forecast* (2021+) and *Previous Runs* (2024+) archives | **fallback + historical forecast vintages** for backtests |
| nflverse `games.csv` temp/wind | verified | game-time observation only (post hoc), fine for outcome analysis, **not** a forecast |

## 6. Other

* Stadium/roof/surface: nflverse schedule fields (verified). Altitude/orientation: to be hand-curated (32 rows).
* Coaches: schedule `home_coach/away_coach` (verified); coordinators not in nflverse → gap, hand-curated table needed.
* Kalshi historical bulk mirrors (Hugging Face `TrevorJS/kalshi-trades`, 154M trades 2021–Jan 2026): blocked in sandbox, licence unverified → research-only candidate, not adopted.

## 7. Verdict

Free data is unusually deep for the NFL: full play-by-play with EPA/WP, FTN charting (pressure, blitz, motion, box counts), NGS separation/cushion/time-to-throw, PFR pressure and coverage stats, daily timestamped depth charts, and a complete official-API path to Kalshi prices. The real gaps are (1) timestamped sportsbook lines and props, (2) a live injury feed with timestamps, and (3) in-season participation/coverage data. (1) is replaced by Kalshi's own history from today; (2) is approximated by daily roster/depth-chart vintages plus a to-be-probed Sleeper/ESPN runner-side feed; (3) is a research-only limitation (participation arrives after the season).
