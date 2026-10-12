# Indirect sportsbook dependencies: PROE, xpass, win probability and team ratings (audit, research only)

**Date:** 2026-10-12, at `origin/main` d4cdcb3. **Machine-readable table:**
`research/pure_gap/dependency_table.json`, written by `scripts/research/pure_gap_dependency_table.py`.
`tests/test_pure_gap.py` checks the table against the PURE_PLAYER_V1 source: every feature marked "not used by
PURE" must have no identifier in `nfl_edge/engines/player/pure_v1/*.py`.

This extends `PURE_PLAYER_V1_DEPENDENCY_AUDIT.md` and `PURE_PLAYER_V1_XPASS_VERIFICATION.md`, which covered xpass
only. Here every nflverse-provided modelled field is checked against nflverse's own model code.

## Upstream sources read

| source | what | fetched |
|---|---|---|
| nflfastR `R/helper_add_ep_wp.R` | EP, WP and spread-WP model feature selectors | 2026-10-12, sha256 39cd3849… |
| nflfastR `R/helper_add_xpass.R` | xpass / pass_oe feature matrix | 2026-10-12, sha256 fc73ba5d… |
| nflfastR `R/helper_add_cp_cpoe.R`, `R/helper_add_xyac.R` | CP and xYAC feature matrices | 2026-10-12 |
| nflreadr `data-raw/dictionary_pbp.csv`, `dictionary_schedules.csv` | nflverse data dictionary | 2026-10-12, sha256 137f3c1a… / f07a07a0… |
| ffverse/ffopportunity `R/ep_preprocess.R` | expected-fantasy-points preprocessing | 2026-10-12 |

## Findings

| feature | market dependency | evidence | PURE_PLAYER_V1 uses | DATA_PLAYER_V4 uses |
|---|---|---|---|---|
| `spread_line`, `total_line` (schedule, pbp) | **DIRECT** (closing consensus line; dictionary: "The closing spread line ... (Source: Pro-Football-Reference)") | dictionary | **no**: allowlist `pure_v1/data.py:31`, refusal `:34-50`, mutation tests | **yes**: `player_distributions.py:139-146` → `spread_team`, `implied_total` in volume (`v4/volume.py:26-27`) and seven rate models (`v4/model.py:435-482`); training-sample gate `volume.py:74` even with `market_env=False` |
| moneylines, spread / total odds | DIRECT | dictionary | no | no (not selected) |
| `implied_total`, `spread_team` | DIRECT (derived) | `player_distributions.py:144-146` | no | yes |
| Kalshi quotes, ticker inventory | DIRECT | earlier audit rows 1-10 | no (population = all player-games) | yes, in production population / environment |
| `vegas_wp`, `vegas_home_wp`, `vegas_wpa` | **INDIRECT (verified)** | `helper_add_ep_wp.R`: `wp_spread_model_select()` takes `spread_time = posteam_spread * exp(-4 * elapsed_share)`, with `posteam_spread` from `spread_line`; dictionary: "incorporating pre-game Vegas line" | no (reads no play-by-play) | no |
| `xpass` | **INDIRECT (verified)** | `helper_add_xpass.R::prepare_xpass_data()` selects `wp` **and `vegas_wp`**. The dictionary entry ("Probability of dropback") does **not** disclose this; only the code does | no | no |
| `pass_oe` and every PROE aggregate (`proe`, `proe_early_ng`, `off_proe_early_ng`, `neutral_proe`, `off_proe`) | **INDIRECT (verified)**: `pass_oe = 100 * (pass - xpass)` | as above | no | no |
| team ratings (`research/team_ratings.py`) and the DATA_ONLY game centre | **INDIRECT (verified)** through the `proe` metric (`team_ratings.py:29`, `arms/data_only.py:57-60`). The other ten metrics (EPA, success rate, explosive, sack, turnover, special teams) are market-free | code | no; DATA_ONLY_GAME appears only as a *comparison arm* in the V1 study | no |
| `wp`, `wpa` (no-spread win probability) | NONE (verified): `wp_model_select()` has no spread term; `wpa` from `home_wp` | code + dictionary | no | no |
| `ep`, `epa`, stats_player_week `*_epa` | NONE (verified): `ep_model_select()` has no spread | code | no (only count / yard columns selected) | no |
| `cp`, `cpoe`, `xyac_*` | NONE (verified) | code | no | no |
| ffopportunity expected fantasy stats | **DIRECT**: implied team totals from `spread_line` / `total_line`, plus `vegas_wp` | `ep_preprocess.R` | no (never downloaded) | no |
| ESPN QBR | UNVERIFIED: ESPN's win-probability inputs are undocumented; treat as market-suspect | — | no | no (no consumer in `nfl_edge`) |
| box-score counts, snap counts, crosswalk, schedule non-market columns | NONE (verified) | code | **yes** | yes |
| schedule starting-QB id (`home_qb_id`, `away_qb_id`) | NONE (not market), but hindsight for the target game | dictionary | yes (QB-passing population; prior-game QB change) | yes (population) |
| EWMA constants (half-life 6, carry 0.35, shrink 2) | NONE (verified): grid scored by plain EWMA MAE on 2016-2019 outcomes (`scripts/research/player_distribution_study.py:31-50`) | code | yes | yes |
| injury report / weekly-roster status | NONE (not market); point-in-time only for 2010-2024 and 2026 vintages (PR #137) | certification doc | no (abstained) | yes (`v4/features.py:55-75`) |

## Verdict on PURE_PLAYER_V1's independence label

**No direct or indirect sportsbook dependency was found. The PURE_INDEPENDENT label stands.**

PURE_PLAYER_V1 reads the following, and nothing else:
* nflverse box-score counts (`STAT_COLS`);
* snap counts;
* the `players` crosswalk;
* the allowlisted non-market schedule columns.

It reads no play-by-play, so no nflfastR model output can reach it: not `vegas_wp`, `xpass`, `pass_oe`, PROE or the
PROE-based team ratings. Its football-only team environment is built from box-score EWMs (`features.add_team_features`),
not from the repository's team ratings. Its constants were selected on sports outcomes alone. The runtime mutation
tests show bit-identical forecasts with the market columns removed or randomised.

Caveats (none of them a market input):
1. The target game's starting-QB id defines the QB-passing population, so QB passing rows are labelled
   conditional-on-starting.
2. The V1 study's **DATA_ONLY_GAME** comparison arm is indirectly market-informed through PROE. The
   "PURE vs DATA_ONLY points" comparison is therefore PURE versus an indirectly market-informed arm.

PURE_PLAYER_V1_2 adds only box-score-derived features: positional allowed rates, the available pool, and PURE's own
team-points forecast. Its dependency status is identical to V1's (`pure_v1_2_uses` in the JSON).
`tests/test_pure_player_v1_2.py` scans its source and reruns it under the market mutations.

## Consequences outside PURE (flagged, not changed here)

These consumers of PROE or `vegas_wp` are **indirectly market-informed** and must not be labelled market-free:
* `nfl_edge/arms/data_only.py`. Its `attest_market_free()` guards the schedule's market columns but cannot see the
  PROE path through play-by-play.
* `nfl_edge/research/team_ratings.py`.
* `nfl_edge/sim/data.py` and `nfl_edge/sim/models.py`. The coherent simulation is market-centred anyway.
* `nfl_edge/research/opportunity.py`.
* the Wave 1/2 signal-discovery features using `neutral_proe` (`nfl_edge/signal_discovery/game_features.py:41`,
  `screen.py:20`).
* the handicap team profile display (`nfl_edge/handicap/teamprofile.py:32`).

A sports-only replacement would refit an expected-pass model without `vegas_wp`, for example on nflfastR's
no-spread `wp`.
