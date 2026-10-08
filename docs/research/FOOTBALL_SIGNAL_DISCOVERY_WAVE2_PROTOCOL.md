# Football Signal Discovery Lab — Wave 2 (NFL): prospective confirmation protocol

Status: **PRE-REGISTERED**

This protocol and its machine-readable twin were committed **before any Wave-2 population game kicked off**. The
population starts with 2026 REG week 6 (first kickoff 2026-10-15). The research job refuses to run unless the
candidate file's canonical SHA-256 equals the value pinned below.

| Item | Value |
|---|---|
| Base main | `4f15a6cd1829676ad106e217ac0e323acba7fb75` (Wave 1 merged, #126) |
| Version | `nfl-signal-discovery-wave2/1.0.0` |
| **Candidates** | `research/signal_discovery_wave2/candidates.json` |
| **Candidates canonical SHA-256** | **`5f31bd3b7c45316eadb4eb754dd4ca2e2b51981ec6ffca89835704a38e0f3436`** |
| Population | 2026 REG, **week ≥ 6**; observed before kickoff; **no backfill** |
| Kind | **PROSPECTIVE.** Research signals only. They are **not** bets, recommendations, SIFT badges, staking rules or automatic wagers. Nothing here is read by RUN NFL, Shadow v2, the incumbent pricer, the sim engine, board/gates, settlement, app export, the router, staking or bankroll. |

## 1. Streams

| Id | Hypothesis | Market | Primary metric | Reads | Falsified |
|---|---|---|---|---|---|
| **NFL-PROP-PROS-001** RB_RECEPTIONS_NO_STRUCTURE (H1-NFL-PROP) | "On eligible running-back receptions ladders, purchasing NO on the natural rung selected by the pre-registered ladder rule at the actual captured NO ask produces positive fee-adjusted ROI prospectively." | KXNFLREC, LAST_VALID_PREKICK_QUOTE_24H | fee-adjusted ROI on outlay | 50 EARLY_READ, 100/200 INTERIM, **300 PRIMARY_REVIEW** | ROI ≤ 0 at n ≥ 300 |
| **NFL-PROP-PROS-002** ROLE_CHANGE_MODEL_ADVANTAGE (H2-NFL-PROP) | "On player-prop ladders classified ROLE_CHANGE before kickoff, the frozen Wave-1 player projection is more accurate than the market line median at predicting the realized player statistic." | 11 prop families, LAST_VALID_PREKICK_QUOTE_24H | d = \|market median − actual\| − \|model − actual\| (> 0 = model wins), averaged per player-game | 50 EARLY_READ, 100 INTERIM, **200 PRIMARY_REVIEW** | mean d ≤ 0 at n ≥ 200 |
| **NFL-GAME-PROS-001** TOTALS_DISAGREEMENT_WF | Wave-1 WF-TOTAL, recovered exactly: \|p\| ≥ 2.0 → OVER if p > 0, UNDER if p < 0 | KXNFLTOTAL, **NFL_PRIMARY_60_180 (new prospective test condition)** | side-signed residual s·(actual − market_implied_total) | 25 EARLY_READ, 50 INTERIM, 100 INTERIM (meaningful), **200 PRIMARY_REVIEW** | mean ≤ 0 at n ≥ 200 |

Verdicts: `PROSPECTIVE_TRACKING` below the first read, then the read's state. At the primary review a falsified
stream is `REJECTED`; otherwise it is `REVIEW_REQUIRED`. **`EDGE_CONFIRMED` is never emitted by code.**

* RB_RECEPTIONS_NO_STRUCTURE is market-structure research, not a player edge.
* ROLE_CHANGE economics are secondary. No "bet when the model differs by X" rule is created.

## 2. What is recovered exactly from Wave 1

| Piece | Recovered from | Wave-2 handling |
|---|---|---|
| Natural rung | `markets.ladders`: the valid rung (0 < bid ≤ ask < 1, width ≤ 0.10) minimising \|mid − 0.5\| | **tie-break frozen here: lowest threshold.** Wave 1 left ties to iteration order. |
| Market median | `markets.ladder_median` | unchanged |
| RB receptions family | `evaluate_props.family_rows`: RB, sh_target_l ≥ 0.05, n_prior ≥ 3, b_season defined | unchanged, computed pregame |
| ROLE_STABILITY | `player_features._role_stability` (source SHA-256 `eeec3777…a981`) | unchanged thresholds; injury input = the latest captured injury vintage at the observation instant (Wave 1 used the final weekly file, declared NEAR_PIT) |
| Prop projection | Wave-1 ridge λ = 1, the 2026 walk-forward fold (train 2016–2025); model median = pred + median_offset | serialized and hashed **before week 6**; its predictions must reproduce the Wave-1 2026 OOS rows |
| WF-TOTAL | OLS of total_resid on [gap.total, env.plays, env.sec_per_play, def_quality_sum.epa, off_quality_sum.epa], train < test | the 2026 fold (train 2015–2025) serialized and hashed **before week 6**; the procedure must reproduce the Wave-1 2018–2025 fold coefficients exactly |
| Game context | `game_features.game_rows`, `sim-oppadj-1.0.0` | the frozen 2026 lambdas from the Wave-1 manifest; never re-chosen |

**WF-TOTAL market translation (pre-registered).** Wave 1's `gap.total` = baseline.total − m.total used the nflverse
consensus close. Wave 2 sets m.total := `market_implied_total`, the Kalshi KXNFLTOTAL ladder median at
NFL_PRIMARY_60_180. The prediction, the qualification and the side are therefore fixed at the checkpoint from
pre-kickoff data only.

## 3. Checkpoints

**LAST_VALID_PREKICK_QUOTE_24H** (props) works per rung through the repository's canonical close,
`evaluation.close.CloseIndex.select`, rule `close-2.1.0`. It gives the last complete valid pre-kickoff observation of
the exact contract on the change-suppressed capture, confirmed by a complete series fetch while the ticker was open.

* It is accepted when kickoff − 24 h < confirmed_at < kickoff and the status is open.
* Nothing after kickoff is read.

**NFL_PRIMARY_60_180** (totals) works per rung: the last capture run whose complete fetch saw the ticker open, with
its confirmation instant in [kickoff − 180, kickoff − 60]. Its price is the last written row at or before that
instant.

**Prices.** Prices are side-specific captured asks. **NO is never 1 − YES.** An ask that is not a whole cent in
[1, 99] is not executable.

**Fees.**

* Fees come from `execution.fees.load_fee_schedule(...).taker_fee(price, 1, series, as_of=confirmed_at)`.
* Any state other than KNOWN → `FEE_UNAVAILABLE`, never 0.
* KXNFLREC and KXNFLTOTAL are KNOWN today. Some prop series are DEGRADED; those rows carry `FEE_UNAVAILABLE`
  economics.

## 4. Identity

* Kalshi player → GSIS uses the Wave-1 resolver.
* It is accepted **only** as RESOLVED_NAME_TEAM or RESOLVED_NAME_TEAM_JERSEY. Name-only matches and unresolved
  players → `IDENTITY_FAILURE`.
* The Kalshi player UUID is recorded.

## 5. Ledger, statuses and settlement

* **Records.** Records are write-once files on `market-data` under `data/research/signal_lab_wave2/`, one per
  (record type, game, stream):
  * **OBSERVATION:** pregame, generated_at < kickoff, written in [kickoff − 300, kickoff − 20] min;
  * **ENTRY:** checkpoint quotes;
  * **SETTLEMENT:** after the final.
* **Fields.** Every row carries sport, signal_id, version, game_id, ticker, player_id (GSIS plus Kalshi UUID),
  candidate/model/classifier/protocol hashes, code SHA, generated_at, kickoff, quote timestamp, rung, side, ask, fee,
  status and exclusion reason.
* **Statuses.** PENDING, ELIGIBLE, ENTRY_UNAVAILABLE, MARKET_NOT_OFFERED, ORIENTATION_FAILURE, IDENTITY_FAILURE,
  FEE_UNAVAILABLE, SETTLEMENT_PENDING, SETTLED, EXCLUDED_PROTOCOL, SYSTEM_FAILURE.
* **Missing observation.** A population game with no observation by kickoff is `SYSTEM_FAILURE`.

**Settlement.**

* **Contracts:** the exchange's own result for the exact ticker when published. Otherwise the nflverse weekly stat
  of a player with ≥ 1 offensive snap. Otherwise `SETTLEMENT_PENDING`.
* **ROLE_CHANGE accuracy:** needs a player who played. Otherwise `EXCLUDED_PROTOCOL` (DID_NOT_PLAY).
* **Totals:** the final score including overtime.
* **CLV:** side-aware against the canonical close. A missing close stays missing.

## 6. Statistics

* One natural rung per player-game for RB receptions. One averaged d per player-game for ROLE_CHANGE. One row per
  game for totals.
* 95 % game-clustered bootstrap (4,000 resamples, `default_rng(20261015)`); Wilson intervals for rates.
* **NO SETTLED SAMPLE** is never shown as 0.

## 7. Not added

No further candidates. Ideas go to `docs/research/FUTURE_HYPOTHESES.md`.
