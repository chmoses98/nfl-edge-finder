# NFL point-in-time availability sources: certification (Phase 3, research only)

Measured 2026-10-11. The numbers come from `scripts/pit_availability/certify.py` and are stored in
`research/pit_availability/certification.json`, which also records each input file's retrieved_at and sha256.
The inputs are nflverse releases downloaded 2026-10-11 and a sparse read of `market-data` at f109eb5 (the
repository's injury vintages, its ESPN injury context captures and its ESPN-summary inactives collector).

**Certified** means two things hold. First, each value can be shown to have existed before a cutoff
(kickoff − 90 min by default). Second, the source's history can't be silently rewritten in a way that changes what
a past cutoff would have seen. The loaders in `nfl_edge/availability_pit/loaders.py` return only such rows. Every
other row is refused and counted.

## Verdicts

| source | seasons | verdict | timestamp basis | identity |
|---|---|---|---|---|
| nflverse `injuries` (weekly report: game status + final practice status) | 2010–2024 | **CERTIFIED** (final weekly report) | row-level `date_modified` | `gsis_id` 100% present, 100% in `players` |
| nflverse `injuries` | 2009 | REJECTED | `date_modified` 0.4% populated | — |
| nflverse `injuries` | **2025** | **REJECTED** | no row time; the only vintage (2026-09-13) post-dates the season | 100% |
| nflverse `injuries` | 2026+ | **CERTIFIED via vintages only** (from 2026-09-13; gap 2026-10-06 → now) | our content-addressed snapshot's `retrieved_at` | 100% |
| nflverse `depth_charts` | 2025, 2026 | **CERTIFIED** (daily snapshots) | row-level `dt` | `gsis_id` present 99.0% (2025), 95.9% (2026) |
| nflverse `depth_charts` | ≤ 2024 | REJECTED | weekly file, no time | — |
| ESPN league injuries endpoint (our captures, `data/context`) | 2026-09-04 → | **CERTIFIED prospectively** | our capture's `retrieved_at` (the row `date` is ≤ it on 100%) | no athlete id; name + team → gsis 98.1% unique |
| ESPN summary `inactives` block (existing collector) | 2026 wk 1–4 | **REJECTED** | — | 0 of 31 in-window game observations carried the block |
| nflverse `weekly_rosters` `status` (INA) | all | REJECTED as pregame | no time | usable only as a realised label |
| ESPN per-event roster `active` flag | — | **NOT YET EVALUABLE**: the new capture starts the evidence | our capture's `retrieved_at` | ESPN athlete id → `players.espn_id` |
| NFL.com / official PDF reports | — | not evaluated | no free machine-readable historical feed found in this repository | — |

## 1. nflverse `injuries`: row-level `date_modified` (2010–2024)

The file has one row per (season, week, team, player): the player's final weekly report, giving the game status
(Out / Doubtful / Questionable) and the final practice status. Rows were joined to the team's scheduled kickoff
(join rate 99.7–100%).

| season | rows | `date_modified` < kickoff | rows modified at/after kickoff | lead h p01 | lead h median |
|---|---|---|---|---|---|
| 2010 | 4,491 | 100% | 0 | 34.9 | 55.1 |
| 2013 | 5,070 | 99.98% | 1 | 34.4 | 55.1 |
| 2016 | 5,115 | 100% | 0 | 31.3 | 54.8 |
| 2019 | 5,392 | 99.91% | 5 | 33.3 | 54.7 |
| 2020 | 5,661 | 99.77% | 13 | 30.1 | 55.1 |
| 2021 | 5,587 | 99.95% | 3 | 22.4 | 47.6 |
| 2022 | 5,682 | 100% | 0 | 25.0 | 47.1 |
| 2023 | 5,599 | 100% | 0 | 24.8 | 47.1 |
| 2024 | 6,215 | 99.98% | 1 | 23.9 | 47.2 |

The JSON has every season. Over 2010–2024 there are 26 rows modified at or after kickoff, and the loader
refuses them. With a 90-minute cutoff it refuses 25 rows for `date_modified` ≥ cutoff and 62 rows with no
`date_modified`.

The timestamps mean what they appear to mean. The weekday of `date_modified` matches the NFL reporting
calendar, as the crosstab over 2010–2024 shows:

| game day | final report day (rows) |
|---|---|
| Sunday | Friday 63,602; Wednesday 1,444; Thursday 1,449; Saturday 299 |
| Monday | Saturday 4,772 |
| Thursday | Wednesday 4,624 |
| Saturday | Thursday 1,518; Friday 1,107 |

Each team-week carries a median of 6 distinct `date_modified` values, so the timestamp is per row, not one
stamp per file.

**Residual trust assumption.** `date_modified` is the source system's timestamp, not our observation. It
certifies the final weekly report as of that time. The file holds no Wednesday or Thursday intermediate versions:
the 2010–2024 history has only the final practice status, and those daily reports can't be recovered
historically. The 2024 file is byte-identical to the vintage the repository took on 2026-09-13 (sha256 7ebabbba…),
so it hasn't been rewritten in the last month. That is weak evidence of stability, not proof.

## 2. nflverse `injuries` 2025–2026: no row time, so vintages only

`date_modified` is absent from the 2025 and 2026 files, and nflverse rebuilds the file in place. The
repository's vintage store (`data/raw/nflverse/_vintages/injuries/` on `market-data`, see
`nfl_edge/shadow_v2/vintage_snapshots.py`) holds 44 distinct 2026 versions, from 2026-09-13T02:46Z to
2026-10-06T20:55Z. It holds only one 2025 version, retrieved after the season ended, so **2025 cannot be made
point-in-time**.

Each 2026 team-game below compares the last vintage taken before kickoff with the newest file:

| week | team-games | with a pre-kickoff vintage | rows final | rows in pre-kickoff vintage | rows added after kickoff | rows changed after kickoff | median vintage lead (h) |
|---|---|---|---|---|---|---|---|
| 1 | 32 | 28 | 182 | 153 | 0 | 0 | 4.0 |
| 2 | 32 | 32 | 251 | 251 | 0 | 0 | 4.1 |
| 3 | 32 | 32 | 301 | 301 | 0 | 0 | 3.1 |
| 4 | 32 | 32 | 318 | 317 | 1 | 9 | 4.4 |
| 5 (TNF only) | 2 | 2 | 20 | 0 | 20 | 0 | 51.3 |

Two findings follow:

* **Post-kickoff edits exist.** Week 4 TNF (CLE, PIT): in the vintage 5.9 h before kickoff, 9 rows were still
  Wednesday-state and one player was missing. Both were filled in only after the game. Reading the current
  file for that game would leak post-kickoff information. The vintage reader can't leak it.
* **The vintage stream stopped after 2026-10-06.** The current file has 1,409 rows against 1,052 in the last
  published vintage, and nothing for week 5 has been published. Week 5 2026 therefore has no PIT injury data,
  except what the new capture records from today.

## 3. nflverse `depth_charts`

* **2025 and 2026 are certified.** Each is a series of daily ESPN snapshots with a row-level `dt`, mostly around
  07:00 UTC:
  * 2025: 221 snapshots, 151 of them in season, every snapshot covering all 32 teams. The median gap is 23 h
    (max 97 h).
  * 2026: 228 snapshots so far, max gap 47 h.
  * At a T-90 cutoff, the newest 2025 snapshot is a median of 11.2 h old (max 38.7 h).
* **History isn't rewritten, as far as row counts can show.** `docs/DATA_SOURCE_AUDIT.md`, written 2026-09-03,
  records "494k rows timestamped `dt` 2026-03-22 → 2026-09-03". Today's file has **494,524** rows with
  `dt` ≤ 2026-09-03. This is count-level evidence. The new capture stores a sha256 per `dt` snapshot, so a future
  rewrite will be detected at the byte level.
* **2020–2024 are rejected.** Those files are weekly, keyed by a `week` label with no time. It's unknowable whether
  a given week's chart preceded that week's kickoff.

## 4. ESPN injuries endpoint (the repository's 3-hourly context capture)

* **Coverage.** There are 148 captures from 2026-09-04 to 2026-10-10. The median gap between captures is 5.6 h and
  the maximum is 15.7 h, because the 3-hourly cron runs late. Those gaps are too coarse for a T-90 read.
* **Timestamps.** All 118,400 rows carry an ESPN `date` that is ≤ the capture time.
* **Identity.** No row carries an athlete id. By normalised name and team, 98.1% of distinct (name, team) pairs
  match exactly one rostered gsis. 9 are ambiguous and 22 unmatched (for example "Hollywood Brown" and
  "Joshua Palmer"). The loader refuses ambiguous and unmatched rows: over the 2026 games played through week 5,
  it returned 3,190 rows and refused 60 for identity.

## 5. Official inactives (published about T-90m)

* **The ESPN summary block is rejected.** The existing collector (`nfl_edge/shadow_v2/inactives.py`) made 125 runs
  with 31 game observations in its window, and every one was `NO_INACTIVES_BLOCK`. It confirmed 0 players inactive.
* **The ESPN per-event roster `active` flag is unproven.** It is probed by `scripts/data/probe_inactives.py`, but
  that probe has never been scheduled. The new capture records it for games in [T-240m, T+30m], with athlete id
  and the `active` and `didNotPlay` flags. Certifying it needs several game days of captures that show the flag
  changes for about 4–12 players per team only after about T-90m. That flagged set can then be scored against
  realised participation (snap counts, or `weekly_rosters` INA).
* **No historical inactive list is certifiable.** No source exists. Inactives are therefore not usable for any
  historical model.

## Loaders (`nfl_edge/availability_pit/loaders.py`)

* **`injuries_certified(root, seasons, lead=90m, vintage_roots=[...])`.** For 2010–2024 it uses the row's
  `date_modified` and requires it to be before the cutoff. For other seasons it uses the newest vintage (the
  repository's store or this capture's) retrieved before the cutoff. It refuses rows with:
  * no time;
  * a time at or after the cutoff;
  * no pre-cutoff vintage;
  * a row that wasn't in the pre-cutoff vintage.
* **`depth_chart_certified(root, season, lead)`.** It uses the newest `dt` snapshot before each team-game's cutoff
  and refuses any season before 2025.
* **`espn_injuries_captured(capture_files, roster, team_games, lead)`.** It uses the newest of our captures before
  the cutoff. It requires the row `date` to be before the cutoff and the identity to be unique.
* **`assert_pre_cutoff`.** Every loader calls it, and it raises if any returned row lacks `observed_at < cutoff`.

## Prospective capture (`.github/workflows/pit-availability-nfl.yml`, `nfl_edge/availability_pit/capture.py`)

The capture is append-only and write-once, under `data/pit_availability/nfl/` on `market-data`. Each run writes
a manifest hash chain. It is verified before publishing, and publishing may only add files. Each run captures:

* new nflverse injury-file content, content-addressed, with `retrieved_at`;
* a per-`dt` sha256 digest of the depth-chart file;
* the raw ESPN injuries endpoint;
* ESPN per-event rosters for games in [T-240m, T+30m].

Cadence: Wednesday to Saturday at 02/08/14/20 UTC (practice reports, then Friday and Saturday final statuses),
hourly on Sunday from 11 to 23 UTC, and Monday and Thursday at 21–23 UTC (T-90m windows). A pull_request run is a
dry run.

Coverage limits of this cadence (known, not yet addressed):

* The T-240m..T+30m roster window is only reached on Sunday, Monday and Thursday. Saturday games (late season),
  and holiday games on other weekdays (Christmas, Black Friday, Wednesday), get the four-a-day runs only, which may
  miss their window entirely. Their event-roster evidence will be absent, not wrong.
* The season captured is the NFL season (calendar year from March, previous year in January and February), so
  playoff runs capture the season's own `injuries_<season>` file.

## Consequence for modelling

Only the 2010–2024 injury report is certified historically, so only one ablation is possible on a real holdout:
`docs/research/PURE_PLAYER_V1_1_PREREGISTRATION.md` (2023 + 2024). The other sources wait for prospective data:
* depth-chart features, since 2025 is the only certified past season and it overlaps PURE_PLAYER_V1's holdout;
* 2025–2026 injury features;
* inactives.
