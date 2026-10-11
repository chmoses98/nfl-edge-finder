# PURE_PLAYER_V1 — expected-pass-rate (xpass / PROE) market-dependency verification

**Date:** 2026-10-11. **Question:** do expected-pass-rate features carry direct or indirect sportsbook information,
and does PURE_PLAYER_V1 consume any of them?

## Finding 1 — nflfastR `xpass` is indirectly market-informed (VERIFIED)

nflfastR computes `xpass` (and `pass_oe = 100 * (pass - xpass)`) in `R/helper_add_xpass.R`. Its feature
matrix, built by `prepare_xpass_data()`, selects:

```
down, ydstogo, yardline_100, qtr, wp, vegas_wp, era2, era3, era4, score_differential, home,
half_seconds_remaining, posteam_timeouts_remaining, defteam_timeouts_remaining, outdoors, retractable, dome
```

Source: https://github.com/nflverse/nflfastR/blob/master/R/helper_add_xpass.R (`prepare_xpass_data`,
fetched 2026-10-11 from `raw.githubusercontent.com/nflverse/nflfastR/master/R/helper_add_xpass.R`).

`vegas_wp` is nflfastR's win probability conditioned on the closing point spread (`spread_line`). Every
play's `xpass` is therefore a function of the sportsbook spread, and so are `pass_oe` and every PROE aggregate
built from it.

**Consequence for existing (non-PURE) arms** — these consume PROE and are *not* market-free, even when called
"data only" (this was audit row 39, previously UNVERIFIED):

| consumer | feature |
|---|---|
| `nfl_edge/data/silver.py:87-88` | `proe_early_ng`, `proe` from `pass_oe` |
| `nfl_edge/arms/data_only.py:57-60` | `proe` → `off_proe_early_ng` |
| `nfl_edge/research/team_ratings.py:29, 96` | `off_proe_early_ng` |
| `nfl_edge/sim/data.py:91-105` | `xpass_mean`, `proe`, `neutral_proe` |
| `nfl_edge/sim/models.py:87` | `off_proe` in `PASS_RATE_FEATURES` |
| `nfl_edge/research/opportunity.py:112, 173` | `pass_oe` → `proe` |

No existing arm is modified by this note. Any future PURE use of expected-pass-rate needs a sports-only
re-fit of an xpass model without `vegas_wp` (e.g. with nflfastR's non-market `wp`, whose model does not take
the spread).

## Finding 2 — PURE_PLAYER_V1 consumes no expected-pass-rate or win-probability input (VERIFIED)

* PURE_PLAYER_V1 reads no play-by-play. Its inputs are nflverse `stats_player_week`, `snap_counts`,
  `players`, and the schedule columns in `nfl_edge/engines/player/pure_v1/data.py::SCHEDULE_ALLOWLIST`
  (`game_id, season, game_type, week, gameday, gametime, home_team, away_team, home_score, away_score, roof,
  home_qb_id, away_qb_id`).
* Its pass-rate / team-volume environment is built from prior box-score team pass and rush attempts (EWM,
  opponent-adjusted), not from `xpass`.
* `tests/test_pure_player_v1.py::test_module_source_never_reads_expected_pass_or_win_probability` now fails
  if any PURE module names `xpass`, `pass_oe`, `proe`, `vegas`, `wp` or play-by-play.
* The runtime mutation tests (`research/pure_player_v1/mutation.json`, `pure_gate_rerun.json`) are unaffected.

`home_qb_id` / `away_qb_id` (the target game's starter) define the *evaluation population* for QB passing
stats ("conditional on starting", identical across arms) and, through `shift(1)` / `shift(2)`, the
prior-game QB-change feature. Prospective use must take the starter from a source observed before the
cutoff; until then QB passing rows are labelled conditional-on-starting.

## Verdict

PURE_PLAYER_V1: **no direct or indirect sportsbook input through expected-pass-rate features.**
Existing PROE-consuming arms (DATA_ONLY, sim, team ratings): **indirectly market-informed.** The
PURE-vs-DATA_ONLY points comparison in `RESULTS.md` is therefore a PURE-vs-indirectly-market-informed
comparison.
