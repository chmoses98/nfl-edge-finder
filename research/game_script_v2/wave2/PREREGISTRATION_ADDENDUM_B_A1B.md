# GAME SCRIPT V2 — WAVE 2: preregistration addendum B — A1B (verified pregame inactives)

**RESEARCH_ONLY. `betting_authority: NONE`.** Nothing here changes betting, staking, BET/PASS, model weights,
market priors, price limits, unit sizes, reconciliation weights, SIFT recommendations, or the authority of any arm.

This addendum ADDS a separately identified research variant, **A1B**. It does not modify `PREREGISTRATION.md`
(sha256 `2d4870e3…`), addendum A (`PREREGISTRATION_ADDENDUM.md`, sha256 `52d2100a…`), the frozen components
(`components_2026.json`, sha256 `353541d18e7e77f4cb06de4233f1b33ef0ff9772941c7792044f55a936ea7008`), the Wave-2
scorer (`nfl_edge/sim/wave2_score.py`, sha256 `f7a0596d…`), A1's rules, or any record. A1 keeps collecting under its
frozen rules (in practice T24). A1 and A1B are never pooled, and A1B inherits no A1 observation — in particular the
TB@DAL A1 record (T24) is never relabelled.

## B.1 Why A1 cannot collect T0 evidence (root cause, established 2026-10-09)

A1 may claim `T0_INACTIVES` only when the nflverse weekly-roster vintage read at its cutoff already carries game-day
`INA` statuses for the team (`availability_horizons.prospective_horizon`). nflverse fills `INA` retrospectively on
a roughly daily cycle: `roster_weekly_2026.parquet` last modified 2026-10-08 14:34 GMT carried **no** `INA` row for
week 5 while week 4 carried 199 (added after those games). The TB@DAL LATE record (T−72.7 min) therefore claimed
T24 with reason "inactive list not observed in the roster vintage read at the cutoff". A1 can essentially never
reach its T0 minimum (64 games) prospectively.

## B.2 Sources examined

| source | game-day inactives? | pregame? | verdict |
|---|---|---|---|
| nflverse weekly rosters (`INA`) | yes (official GSIS status) | **no** — filled after the games | unusable prospectively (B.1) |
| Sleeper `players/nfl` (market-data context) | **no** — injury designations (`Out`, `Questionable`, `IR`) and roster status (`Active`/`Inactive`) | yes | unusable: designations are not the inactive list |
| ESPN summary `inactives` block | would be | — | **absent** in all 31 in-window observations of 28 games (2026-09-13 … 10-02), incl. T−10 … T−62 (`data/shadow/v2/inactives`) |
| ESPN core per-competition roster `active` flag | **candidate** | unproven | the only candidate not refuted; never snapshotted with timestamps |
| ESPN injuries feed, NFL.com | designations / not freely accessible | — | not considered |

The candidate is used ONLY through this repository's own write-once snapshots, and ONLY after it passes the
source qualification of B.4. If it fails, A1B is BLOCKED and A1 continues unchanged.

## B.3 Hypothesis and primary endpoint

H: verified pregame inactive information improves player projections relative to the incumbent (A0) at the same
cutoff. **A1B** = A0's inputs with (i) every projected player the source names inactive set to
`INACTIVE_CONFIRMED` (play probability 0; the row is kept, as a certain zero) and (ii) every `QUESTIONABLE` projected
player NOT named inactive set to `EXPECTED_ACTIVE` (a usable list is complete). Same bundle, same components,
same game input, same seed (11), same 10,000 simulations, same (M0) game draws as A0.

**Primary endpoint:** mean over the five opportunity statistics (targets, receptions, receiving yards, carries,
rushing yards) of `sum A1B CRPS / sum A0 CRPS − 1`, over the A0 population (rows with A0 predictive mean ≥
`backtest.FLOORS`), with a 2,000-resample game-clustered percentile interval (seed 20261005). A1B passes the
primary when the interval's upper bound is < 0.

**Non-inferiority (each must hold):** MAE of each of the five (upper bound of the ratio − 1 ≤ +0.5%); CRPS of every
other scored statistic (≤ +0.5%); zero integrity / coherence failures; leave-one-game-out sign stable and no game
> 10% of the improvement.

**Secondary (descriptive, Holm-adjusted across the three, never a gate):** (a) A1's endpoint — change in |bias| of
questionable players' carries + targets; (b) CRPS of teammates of confirmed inactives; (c) CRPS of the confirmed
inactives' own rows. Only the primary can support a claim (one confirmatory test: no multiplicity adjustment
is needed for it).

## B.4 Source qualification (mechanical; source behaviour only, no projection outcome)

Collection of source snapshots starts when `.github/workflows/a1b-research.yml` first reaches `main` (the
**activation instant** = committer time of that commit, read from git). The **qualification set** is the first 24
games kicking off after the activation instant (after the Wave-2 cutoff); every one counts, including games with no
snapshot. Per team-game (48), using only snapshots retrieved by this repository:

| id | criterion | pass |
|---|---|---|
| QA | availability: a USABLE snapshot (both teams 4–12 flagged inactive) retrieved in [T−100, T−35] | ≥ 90% of the 24 games |
| QR | release, not an echo: among team-games with a snapshot retrieved before T−110, the flagged set at the first USABLE in-window snapshot differs from the last pre-T−110 set (or the pre-T−110 count is 0) | ≥ 90%, and ≥ 12 team-games evaluable |
| QS | stability: the set at the latest snapshot ≤ T−35 equals the set at the last snapshot before kickoff | ≥ 90% |
| QT | truth: Jaccard(set at T−35, mapped to gsis; nflverse postgame `INA` for that team-week) ≥ 0.80 | ≥ 90% of team-games |
| QM | identity: flagged-inactive ESPN ids that map to a gsis id | ≥ 98% |

QT reads nflverse's postgame `INA` list solely to validate the SOURCE; it never enters an A1B prediction. If every
criterion passes, the source is QUALIFIED; otherwise A1B is BLOCKED. The evaluator
(`scripts/sim/a1b_qualify.py`) is committed now, before any snapshot exists, and is run once the 24th game's
postgame nflverse weekly roster carries `INA` rows. Its output and the resulting status are committed as
addendum C together with `research/game_script_v2/wave2/a1b/SOURCE_STATUS.json` (`QUALIFIED` with
`qualified_at` = that commit's committer time, or `BLOCKED`). No criterion, threshold or set may change after any
snapshot exists.

## B.5 Capture, cutoff, eligibility, missingness

* **Snapshots:** each post-cutoff game with kickoff in (now, now + 150 min], at most one per 10 minutes, NEVER at or
  after kickoff. File `data/research/wave2_a1b/sources/<day>/<game_id>.<run_id>.a1b_src.json.gz` (write-once):
  raw bodies, HTTP status, the source's `Date` / `Last-Modified` / `ETag` (recorded, never trusted), raw-bytes
  sha256, and OUR request / retrieval instants — the only availability evidence.
* **A1B cutoff:** the A1B capture runs with its cutoff in **(T−80, T−35]** (inactives are released ≈ T−90; ≥ 10
  minutes for the source to reflect them; frozen ≥ 35 minutes before kickoff). It uses the LATEST snapshot
  retrieved in [T−100, cutoff] with both teams USABLE.
* **Record:** `data/research/wave2_a1b/records/<day>/<game_id>.A1B.<run_id>.a1b.json.gz`, one per game, write-once:
  A0 and A1B on identical rows, the snapshot used (path, sha256, retrieved_at), the mapped inactive set, the
  qualification status read at capture, versions, `research_only: true`, `betting_authority: NONE`.
* **Missingness:** no usable snapshot by T−45 → a `NO_USABLE_SOURCE` record naming `SOURCE_OUTAGE` (no HTTP 200),
  `NOT_PUBLISHED_OR_IMPLAUSIBLE` (200 without a plausible list) or `NO_SNAPSHOT_IN_WINDOW` (collector did not run).
  A projected player without an ESPN id → `UNUSABLE_IDENTITY`. These are missing observations, counted, never
  imputed, never re-captured later.
* **Identity:** gsis ↔ ESPN via the nflverse players table (`espn_id`); exact ids only, never names.
* **Eligibility for the primary:** a record with `state: OK`, generated before kickoff, cutoff inside (T−80, T−35],
  the frozen components, and `source_qualification.status == QUALIFIED` read at capture with kickoff after
  `qualified_at`. Records captured while QUALIFYING are pipeline validation only, never evidence.

## B.6 Sample, analysis set, scorer

Minimum prospective sample (section-8 formula on DEVELOPMENT data only — 2020, A1T0 vs A1T24 replays, inactive rows
as certain zeros): effect −0.0436 (relative CRPS, per game), sd 0.0614 → n = 15.5 → **64 games** (floor), 4 weeks of 16.
The gate is applied ONCE on the first 64 eligible games in (kickoff, game_id) order; later games are descriptive.
Below 64 the status is COLLECTING. The A1B scorer (`nfl_edge/sim/a1b_score.py`, `wave2-a1b-score-1.0.0`) is
committed with this addendum, before any A1B record exists. A1B can at most become a PROMOTION_CANDIDATE — a human
decision with no authority change in this wave.

## B.7 Expected opportunities

About 14–16 games a week; every game whose snapshots and capture succeed and whose source is QUALIFIED is eligible
(both teams), so ≈ 4–5 weeks of collection after qualification (≈ 2 weeks of qualification first).
