# Football Signal Discovery Lab — Wave 2 (NFL): status

**PROSPECTIVE TRACKING. NO SETTLED SAMPLE.** The population starts at 2026 REG week 6 (first kickoff
2026-10-15T00:15Z, SEA@DEN). No population game had kicked off when this was written.

| Stream | Verdict | Settled n | Next read |
|---|---|---|---|
| NFL-PROP-PROS-001 RB_RECEPTIONS_NO_STRUCTURE | PROSPECTIVE_TRACKING | NO SETTLED SAMPLE | EARLY_READ at 50 (primary 300) |
| NFL-PROP-PROS-002 ROLE_CHANGE_MODEL_ADVANTAGE | PROSPECTIVE_TRACKING | NO SETTLED SAMPLE | EARLY_READ at 50 player-games (primary 200) |
| NFL-GAME-PROS-001 TOTALS_DISAGREEMENT_WF | PROSPECTIVE_TRACKING | NO SETTLED SAMPLE | EARLY_READ at 25 (primary 200) |

## Frozen before week 6

| Item | Commit | SHA-256 |
|---|---|---|
| Protocol + candidates | `191230a8` | candidates `5f31bd3b…3436` |
| WF-TOTAL 2026 fold (train 2015–2025, n 2,985) | `e2016ee8` | `37baf8ec…fe98` |
| Prop ridge 2026 fold (14 families, train 2016–2025) | `e2016ee8` | `7e308d26…c6f9` |
| ROLE_STABILITY classifier source | — | `eeec3777…a981` |

**Reproduction proofs** (`research/signal_discovery_wave2/models/manifest.json`):

* The WF-TOTAL procedure re-run on the identical corpus reproduces every 2018–2025 Wave-1 fold coefficient exactly
  (max |diff| 0.0).
* Every prop family's 2026 predictions reproduce `prop_oos_predictions.parquet` exactly (max |diff| 0.0).
* The pregame (phantom-row) feature build reproduces the Wave-1 features of every week-4 player who played
  (372/372; shares, rates, context and baselines all max |diff| 0.0).
* The game rows for 2026 weeks 3, 5 and 6 reproduce the Wave-1 table exactly.

## How it runs

`.github/workflows/signal-lab-wave2.yml` is dispatched by the horizon conductor (new target `SIGNAL_LAB`, which
shares the due rule `nfl_edge/signal_discovery/wave2_due.py`). A `13,43` cron is the backstop.

| Stage | Owed when | Writes (write-once, `market-data:data/research/signal_lab_wave2/`) |
|---|---|---|
| observe | kickoff in [now+20, now+300] min | `observations/2026/<game_id>.json` |
| enter | after kickoff, ≤ 7 days | `entries/2026/<game_id>.json`, or a SYSTEM_FAILURE observation when none was frozen before kickoff |
| settle | ≥ 5 h after kickoff, until every row is settled (≤ 7 days) | `settlements/2026/<game_id>.json` |
| report | every run | `reports/<run_id>.status.json` |

A failed stage run fails the job visibly. Owed records stay owed and the next run retries. A `rehearsal_weeks`
dispatch runs observe → enter on a non-population week into `/tmp` and uploads the result as an artifact. It never
publishes.

## Current-slate eligibility dry run (week 6, cutoff 2026-10-08T22:54Z, pregame inputs only)

Full output: `research/signal_discovery_wave2/dry_run_eligibility_week6_2026-10-08.json`. It is not a checkpoint;
week 5 had not been played yet, so the real observation a week later will differ.

| Item | Count |
|---|---|
| Games | 14 |
| NFL-GAME-PROS-001 football inputs complete | 14 (qualification needs the PRIMARY_60_180 market total) |
| NFL-PROP-PROS-001 RB-receptions family rows | 46 (entry needs a KXNFLREC ladder at the checkpoint) |
| NFL-PROP-PROS-002 ROLE_CHANGE family rows | 20 |
| Injury vintage | resolved (retrieved 2026-10-08T18:59Z) |
| Phantom players | 521 |

## Verification

* `tests/test_signal_discovery_wave2_nfl.py` (25 tests) covers:
  * pins, and refusal of edited candidates or artifacts;
  * the WF-TOTAL translation;
  * the natural-rung tie-break, validity and missingness;
  * NO never 1 − YES, and fees never 0;
  * the 24 h checkpoint;
  * the shared due rule and the conductor dispatch;
  * a rehearsal never publishing;
  * the enter stage on a synthetic capture: post-kickoff rows ignored, the totals checkpoint confined to
    PRIMARY_60_180, identity failures named, write-once;
  * missing observation → SYSTEM_FAILURE;
  * settlement that is append-only and waits for results;
  * verdicts and NO SETTLED SAMPLE;
  * isolation from production paths.
* Full suite: 2,982 passed, 3 skipped.
