# GAME SCRIPT V2 — WAVE 2: prospective protocol

**RESEARCH_ONLY.** No arm, record or result described here has betting, staking, BET/PASS, price-limit, unit-size,
model-probability or reconciliation-weight authority. Nothing in the pricing path, the ledger, the packet's decision
fields, gates, preflight, risk or staking reads a Wave-2 module or record (tested in `tests/test_wave2.py`).

This document says HOW prospective evidence is produced and scored. WHAT counts as a pass is fixed in
`PREREGISTRATION.md` (sections 7 and 8) and its addendum, and is not restated or changed here.

## 1. The cutoff

**PROSPECTIVE CUTOFF = 2026-10-05T16:14:02+00:00** — the committer time of commit
`0aea50fcd30b4eafc94c1228f716cd77e01f5db9`, which added `PREREGISTRATION.md`. A game is prospective evidence for an
arm only if (a) its scheduled kickoff is after the cutoff and (b) a write-once record for that game, generated before
kickoff from inputs retrieved before kickoff, exists for that arm. A game without a record is missing — never imputed,
never back-filled by a later re-simulation. Every 2026 game that kicked off before the cutoff is
CONTAMINATED_DIAGNOSTIC like 2021-2025.

## 2. What is captured, when, and by what

| item | producer | window | file (market-data branch) |
|---|---|---|---|
| S1, Q1, A1, M1 vs A0 (incumbent) | `.github/workflows/wave2-research.yml` → `scripts/sim/wave2_prospective.py` | EARLY: 90-240 min before kickoff; LATE: 30-90 min | `data/research/wave2/<day>/<game_id>.<window>.<run_id>.wave2.json.gz` |
| RISK1 (GAME SCRIPT V2 document + projection rows) | the existing shadow-price cycle (merged in PR #112) | every shadow cycle | `data/shadow/sim/<day>/<run>.sim-1.1.0.scripts_v2.json.gz` + `...projections.jsonl.gz` |
| RISK1 world fingerprints | the same shadow cycle, contracts of games within 6 h of kickoff | from the Wave-2 merge on | inside the `scripts_v2` document (`fingerprint`) |

The research workflow runs at :07 and :37 every hour. It first asks — from the schedule and a blob-less listing of
market-data only — whether any game after the cutoff is inside a window with no record for that window; only then does
it download inputs and simulate. All arms of one record share the incumbent bundle
(`research/simulation_engine/bundle_<season>.json`), the frozen Wave-2 components
(`research/game_script_v2/wave2/components_2026.json`, SHA-256 recorded in every record), the same game input, the
same seed (11) and 10,000 simulations. S1 and Q1 differ from A0 ONLY in the grafted component; M1 differs only in the
(margin, total) draws; A1 differs only in participation states, and only when the record may claim T0_INACTIVES
(`horizon` and `horizon_by_team` say which and why; otherwise `a1_identical_to_a0` is true).

Each record carries: wave2 / sim / engine / model versions, run id, generation time, the cutoff, minutes to kickoff,
the prospective cutoff, the market centre read (spread, total, source), each arm's per-player distributions (pmfs for
count statistics, 50 quantiles for yardage) and team distributions, M0 and M1 exact-margin pmfs and GAME SCRIPT V2 cell
probabilities, a coherence flag per arm, and `research_only: true`, `betting_authority: "NONE"`.

Records are write-once: the writer refuses to overwrite, the runner skips a (game, window) that already has a record,
and publication appends to market-data. A record is never edited, deleted or regenerated. A failed capture is a
missing observation.

## 3. Which record scores a game

For each (game, arm): the LAST record generated before kickoff (LATE if it exists, else EARLY). For A1 only records
whose `horizon` is `T0_INACTIVES` enter the A1 primary; T24 records are reported separately as the honest
earlier-horizon accuracy. For RISK1: the last `scripts_v2` capture generated before kickoff (`risk1.select_captures`).

## 4. Outcomes

Player and team statistics: nflverse weekly player stats and play-by-play for the game, as used by the five-season
study (`nfl_edge/sim/backtest.py`), retrieved after the game. Margin and total: the final score. RISK1 contracts:
the Kalshi settlement where recorded, otherwise the box score under the pricer's settlement semantics
(`risk1.realized_cash`); both counts are reported. An outcome that cannot be determined is reported as such and the
contract is excluded with a count, never guessed.

## 5. Scoring (the preregistered metrics, on identical rows)

* Population: the incumbent's scored rows — rows whose A0 predictive mean clears `backtest.FLOORS` — so a candidate
  cannot choose which rows judge it.
* Player metrics from the stored distributions: CRPS (from quantiles / pmf), absolute error of the mean, randomized
  PIT (pmf statistics) and its chi-square / edge-bin mass, as in `nfl_edge/sim/wave2_eval.py`.
* Margin: exact-margin log score (probability floored at 1e-4), spread- and total-ladder Brier, GAME SCRIPT V2
  multiclass Brier.
* Intervals: 2,000-resample game-clustered bootstrap, seed 20261005.
* Gates and minimum samples: PREREGISTRATION section 7 and the addendum. An arm is not scored for promotion before its
  minimum sample is reached; interim looks, if any are reported, are labelled INTERIM, carry no status change and do
  not alter the minimum.
* The scorer for prospective records (`scripts/sim/wave2_score.py`) is committed, with tests on synthetic records,
  BEFORE the first record is scored; once a record has been scored the scorer's metric code is frozen (fixes to I/O
  are allowed and logged, a change to a metric is a DEVIATION).

Never: dropping a bad observation; redefining a subgroup; changing a gate, a metric, a window or a minimum after any
prospective outcome is known; citing 2021-2025 or pre-cutoff 2026 as validation.

## 6. Status words

* **PROSPECTIVE_CHALLENGER** — eligible to accumulate prospective evidence toward promotion.
* **REJECTED_AT_DEVELOPMENT** / **DIAGNOSTIC_FAIL** — records may still be captured (the workflow captures every arm
  on identical rows, which keeps the A0 comparison intact) but they are descriptive only and cannot promote the arm
  under this preregistration. A new form would need a new preregistration and a new cutoff.
* **PROMOTION_CANDIDATE** — passed every prospective gate at its minimum sample. A human decision follows; nothing is
  deployed automatically, and even then authority changes are outside this wave.
* **COLLECTING** (RISK1) — design frozen, observations accumulating, no result read before the minimum sample.

## 7. Failure modes and what they mean

| failure | consequence |
|---|---|
| workflow not on `main` | no projection-arm records exist; the arm has no prospective evidence (reported as such) |
| schedule / roster download fails | the run captures nothing; games missed in both windows are missing |
| market centre unavailable at the cutoff | the game is not in the slate (`NOT_IN_SLATE`) and is missing |
| roster vintage retrieved after the cutoff | A1 cannot claim T0_INACTIVES for that record (T24) |
| coherence flag false for an arm | that record counts as a coherence failure for the arm (a gate) — it is not dropped |
