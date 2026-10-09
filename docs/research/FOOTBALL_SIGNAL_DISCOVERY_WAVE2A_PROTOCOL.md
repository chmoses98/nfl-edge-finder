# Football Signal Discovery Lab — Wave 2A (NFL): retrospective replay protocol

Status: **PRE-REGISTERED** (committed before the 2026 replay of any stream was run).

Wave 2A asks: *if the three frozen Wave-2 NFL rules had existed earlier, what would they have done?* It is
**RETROSPECTIVE RESEARCH**. It does not replace, feed or alter the prospective Wave-2 experiment
(`FOOTBALL_SIGNAL_DISCOVERY_WAVE2_PROTOCOL.md`, candidates SHA-256 `5f31bd3b…3436`, WF-TOTAL `37baf8ec…fe98`, prop
models `7e308d26…c6f9`, classifier `eeec3777…a981`). Nothing is refit, retuned or re-chosen. Replay records are
written to a scratch directory and summarised into `research/signal_discovery_wave2a/`; they are **never** published
to `market-data:data/research/signal_lab_wave2/` and never counted in a prospective n.

## 1. The frozen job, replayed

The 2026 replay runs the Wave-2 job's own stage functions (`scripts/research/signal_lab_wave2.py`:
`stage_observe`, `stage_enter`, `stage_settle`) unchanged, game by game, on 2026 REG **weeks 1–5** (all completed
before the Wave-2 population, week ≥ 6):

| Stage | Replay instant | Inputs |
|---|---|---|
| observe | **kickoff − 300 min**, the earliest instant the frozen job may observe | nflverse (downloaded 2026-10-08; week-W features from strictly earlier games; the builders' phantom rows), the injury-report **vintage** resolved from `market-data`'s timestamped vintage index (retrieved ≤ cutoff), daily depth-chart snapshots (`dt` ≤ cutoff) |
| enter | kickoff + 5 min | `market-data` capture @ `4f049279` (only pre-kickoff rows are read by `close-2.1.0`) |
| settle | kickoff + 8 days | the exchange's own settled-market records, read from the `market-data` discovery archive (`data/kalshi/discovery/20261008T163830Z`, the same fields the live fetch returns), then nflverse stats / scores |

Kalshi's API is not reachable from the replay environment, so the live settlement fetch is replaced by that archive
read. That is the only substitution, and it is labelled on every row (`EXCHANGE_RESULT_FROM_DISCOVERY_ARCHIVE`).

**Inputs that are not timestamp-safe, declared.** The weekly roster (`F.weekly_roster`) is the final nflverse file.
It carries game-day `INA` designations, which are published about 90 minutes before kickoff (before kickoff, after
the observe instant). It is labelled `ROSTER_NEAR_PIT`, and the number of skill players it removed is reported.
Before the first injury vintage (2026-09-13) the frozen classifier cannot run, so ROLE_CHANGE rows are
`INJURY_VINTAGE_UNAVAILABLE`; the current injury file is never substituted.

## 2. Evidence labels

| Stream | 2025 / history | 2026 weeks 1–5 |
|---|---|---|
| NFL-PROP-PROS-001 | `RETROSPECTIVE_DISCOVERY_CORPUS`. The exact rule is `HISTORICAL_REPLAY_UNAVAILABLE`: the 2025 archive has no NO quote and no last-pre-kick quote. It is characterised on the Wave-1 basis instead (T-90m horizon snapshot, NO ask = 1 − YES bid, Wave-1 player rows) with the frozen natural rung and tie-break. | `RETROSPECTIVE_2026_REPLAY`, **discovery-contaminated**: Wave 1 used the 2026 weeks 1–5 capture when it proposed this candidate (+13.4 %). |
| NFL-PROP-PROS-002 | 2016–2025 classes used the final weekly injury file: `INJURY_VINTAGE_UNAVAILABLE` for every row (counted, not used) | `RETROSPECTIVE_2026_REPLAY`, **partially contaminated**: Wave 1 displayed 2026 ROLE_CHANGE-versus-market rows |
| NFL-GAME-PROS-001 | Wave-1 walk-forward folds 2018–2025 reproduced as published: reproducibility, not discovery | `RETROSPECTIVE_2026_REPLAY`. Independence is audited in the results (fit, features, threshold, sign, prior inspection). |

`PROSPECTIVE_WAVE2` stays untouched: it is shown beside the replay, never pooled.

## 3. Metrics (frozen definitions)

* **PROP-001.** One natural rung per player-game, NO at the captured NO ask, taker fee from the fee engine
  (`FEE_UNAVAILABLE` never 0). Fee-adjusted ROI with a game-clustered bootstrap, win rate with a Wilson interval,
  and player, team and week concentration.
  * **Baselines on the same eligible player-games (descriptive):**
    * `ALWAYS_NO_EVERY_VALID_RUNG`: NO on every valid rung of the same ladders;
    * `ALWAYS_YES_NATURAL_RUNG`;
    * `ALWAYS_NO_NATURAL_RUNG` on WR/TE receptions ladders and on every stream-stat ladder at the same checkpoint
      (generic NO bias).
* **PROP-002.** d = |market median − actual| − |model median − actual| (> 0 = model wins), averaged per
  player-game. Reported: model and market MAE, mean and median d, a game-clustered bootstrap interval, the share
  with d > 0, results by family / position / week / team / player, top-5-player-removed, one-team-removed, and
  injury-driven versus usage-driven where the frozen fields allow it. Economics are secondary and use only the
  Wave-1 pre-registered side rule already in the frozen job.
* **GAME-001.** Signed residual s·(actual − market_implied_total), hit rate, pushes, OVER/UNDER split,
  fee-adjusted ROI on the natural rung, CLV (side-aware; a missing close stays missing), week-by-week results. The
  same statistics are shown for all games with a ladder centre, for comparison only, never as a new rule.

Seeds and draws are the Wave-2 constants (`default_rng(20261015)`, 4,000 draws).

## 4. Integrity

* Every quote read is pre-kickoff (`close-2.1.0`), and every observation is generated before kickoff.
* Population membership is decided by the observe and enter stages, which read no outcome. A test alters the
  outcomes and shows membership unchanged.
* No replay row is written to the prospective store, and no replay n is added to a prospective n.
* New ideas go to `docs/research/FOOTBALL_SIGNAL_WAVE2A_FUTURE_HYPOTHESES.md` and are not tested.

## 5. Interpretation rule (fixed now; 2026 replay only)

| Class | PROP-001 (ROI) | PROP-002 (mean d) | GAME-001 (mean signed residual) |
|---|---|---|---|
| `INSUFFICIENT_REPLAY_DATA` | settled n < 30 | n < 30 | n < 10 |
| `STRONGLY_SUPPORTIVE` | ROI > 0, interval excludes 0 | mean d > 0, interval excludes 0 | mean > 0, interval excludes 0, hit rate ≥ 52.4 % |
| `SUPPORTIVE` | ROI > 0 | mean d > 0 and share d > 0 ≥ 50 % | mean > 0 and hit rate ≥ 50 % |
| `UNSUPPORTIVE` | ROI ≤ 0 and interval upper bound < 0 | mean d ≤ 0 and share < 50 % | mean ≤ 0 and hit rate < 50 % |
| `MIXED` | anything else | anything else | anything else |

The prospective status of every stream stays `PROSPECTIVE_TRACKING`.
