# NFL Full-Board Shadow v2

> SHADOW / RESEARCH ONLY. Nothing in this document, in `nfl_edge/engines/`, `nfl_edge/semantics/`,
> `nfl_edge/projection/`, `nfl_edge/board/`, `nfl_edge/evaluation/`, `nfl_edge/shadow_v2/`, `scripts/shadow_v2/` or the
> three `shadow-v2-*` workflows selects, recommends, gates or reaches the recommendation path. The incumbent
> pricer, ledger, gates, risk policy, settlement engine and three-arm experiment are pinned
> (`tests/test_incumbent_unchanged.py`) and are imported, never modified. No new family has real-money authority.

## 1. What v2 is for

Before v2 the system priced 32.8% of the NFL contracts Kalshi listed (the five full-game families and ten
player statistics), 371 open contracts in four series were invisible (discovered, never captured, absent from
the ledger), and a contract outside the priced set had no record saying why. v2 makes the whole board
accountable:

* **every NFL contract is visible** — Board Accounting v1 walks every open market of the latest discovery and
  assigns exactly one terminal state with a reason (0 unexplained on the 2026-09-10 discovery, 17,323 contracts);
* **every defensible contract is projected from a coherent engine** — one question grammar
  (`nfl_edge/semantics/questions.py`) routes each contract to the game, period, joint, season or player engine;
  each engine answers every question from ONE simulation or ONE distribution object, so ladders, buckets and
  composites are coherent by construction;
* **every unsupported contract says exactly why** — a terminal support state (`SEMANTICS_AMBIGUOUS`,
  `IDENTITY_UNRESOLVED`, `DATA_UNAVAILABLE`, `RESEARCH_REQUIRED`, `JOINT_MODEL_REQUIRED`, `NON_FOOTBALL_MODEL`,
  `UNSUPPORTED`, `POST_KICKOFF`, `STALE_MARKET`) and never a probability;
* **every prediction is frozen and settleable** — `ProjectionRecord` (schema `projection-2.0.0`) is append-only,
  content-hashed, PROSPECTIVE only when both the observation and the run precede kickoff, and carries the question
  it priced so settlement v2 pays it from proven results or refuses with a named reason;
* **the system accumulates evidence about whether the model adds information beyond the market** — the universal
  scorecard scores every arm against the market midpoint (probability benchmarking) with game-clustered standard
  errors, and against the ask after fees (economics), with HISTORICAL_RESEARCH and PROSPECTIVE_FROZEN never pooled.

## 2. Pipeline

```
discovery (kalshi-discover.yml)  ──► drift report + provisional series list ──► capture (registry + provisional at LIGHT tier)
                                                                                     │
        latest capture snapshot + discovery static semantics                          ▼
        ┌──────────────── scripts/shadow_v2/project_slate_v2.py (2-hourly + T-24h/T-6h/T-90m/T-30m) ────────────────┐
        │ semantics: classify → Question(kind, engine, stat, period, subject, op/k/lo/hi/event/legs, confidence)      │
        │ GAME   joint (margin,total) simulation from Kalshi-implied lines  (frozen game_env / market_implied)         │
        │ PERIOD joint quarter simulation at the same lines                   (nfl_edge/engines/period.py)             │
        │ JOINT  composites on shared draws, else JOINT_MODEL_REQUIRED       (nfl_edge/engines/joint.py)              │
        │ SEASON schedule Monte Carlo                                          (nfl_edge/engines/season.py)             │
        │ PLAYER DATA_PLAYER_DIST / MARKET_PLAYER_DIST / HYBRID_PLAYER_DIST    (nfl_edge/engines/player/*)              │
        │ coherence audit of every ME/CE group (mid = research; bid/ask + fee once = executable)                        │
        └──► data/shadow/v2/projections/<day>/<snapshot>.<arm>.projections.jsonl.gz  (+ manifest, run summary)       ┘
                                                                                     │
        scripts/shadow_v2/settle_v2.py (3-hourly)                                    ▼
        proven results (schedule finals + postgame tables, play-by-play quarter scores, player stats + snaps)
        ──► data/shadow/v2/settlements/<game>/  (write-once batches)  ──► autopsy v2 (DATA arm)  ──► scorecard v2
```

Board Accounting (`scripts/shadow_v2/board_accounting.py`) joins the latest discovery, the registry, the provisional
list, the capture state and the projections into the funnel
`DISCOVERED → NFL_BOARD → CLASSIFIED → CAPTURED → SEMANTICS_PROVEN → IDENTITY_RESOLVED → DATA_AVAILABLE → MODEL_SUPPORTED → PROJECTED → SETTLEMENT_CAPABLE`.

## 3. Semantics: the question grammar

`Question(kind ∈ {THRESHOLD, RANGE, EVENT, COMPOSITE}, engine ∈ {GAME, PERIOD, PLAYER, SEASON, JOINT, NONE}, stat, period,
subject, op, k, lo, hi, event, legs, semantic_confidence ∈ {PROVEN, LIKELY, AMBIGUOUS, UNKNOWN}, overtime, tie_rule)`.

* PROVEN needs the bounds to come from the rules text or strike fields and to agree with the ticker and the custom
  strike; a disagreement between readings is AMBIGUOUS and is never priced. Margin buckets: 2026 tickers
  `-KC7TO14`, `-KC15PLUS`, `-TIE`; 2025 archive `between` strikes with "either team (inclusive)".
* Only PROVEN questions on a validated engine become `PRICED`; PROVEN on a shadow engine or LIKELY anywhere become
  `PROJECTABLE_NOT_YET_VALIDATED` (a probability is written, research only).
* Composites (parlays, half/full doubles) carry their legs; the joint engine prices them only when every leg is a
  score function of one shared simulation.

`nfl_edge/semantics/catalog.py` is the family catalog: engine, semantic confidence, model support, settlement
support and source, evidence and reason per (family, period) and per player statistic.

## 4. Engines

| engine | version | distribution | validated for | shadow status |
|---|---|---|---|---|
| GAME | game-engine-2.0.0 | incumbent residual bank (game_env-0.2.0), 40,000 draws | GAME_WINNER, SPREAD, TOTAL, TEAM_TOTAL, BOTH_TEAMS_SCORE_N (PRICED) | WIN_MARGIN_BUCKET, min/max team points, abs margin: PROJECTABLE |
| PERIOD | period-engine-2.0.0 | period-residual-bank-1.0.0: per-quarter regression centres on implied team totals + kernel-resampled historical 8-vectors shifted by the integer centre difference (KERNEL_EMPIRICAL_SHIFTED, preregistered choice; research/period_engine) | nothing (no historical market comparison exists: 203 archived period contracts over six playoff games) | 1H/2H/1Q..4Q winner, spread, total, team total, both-score: PROJECTABLE |
| JOINT | joint-engine-1.0.0 | the game or period simulation | nothing | HALF_FULL_RESULT and score-only parlays: PROJECTABLE; anything with a player/season leg: JOINT_MODEL_REQUIRED |
| SEASON | season-engine-1.0.0 | schedule Monte Carlo, 20,000 seasons, consensus spread where published else home-field prior, approximate tie-breakers | nothing | SEASON_WINS, SEASON_WINS_EXACT, MAKE_PLAYOFFS, DIVISION_WINNER: PROJECTABLE (LIKELY semantics) |
| PLAYER | data-player-dist-2.0.0 / market-player-dist-1.0.0 / hybrid-player-dist-1.0.0 | one `LatticeDistribution` per (player, game, statistic) | nothing | eleven statistics incl. rush_rec_yards: PROJECTABLE on three arms |

### 4.1 Period engine (research/period_engine/RESULTS.md)

Quarter scores come from the last post-play score of each quarter in nflverse play-by-play and reproduce the
final in 256/256 non-overtime 2024 games. The naive "divide the full-game line" baseline mis-centres every period
(1H margin ≈ 0.47 + 0.559·spread, 1Q total ≈ 0.40 + 0.187·total) and is 0.028 Brier worse on the 1Q total ladder.
Among the regression-centred candidates the differences are inside one clustered standard error on most ladders;
the preregistered rule chose KERNEL_EMPIRICAL_SHIFTED (best 1H total ladder Brier and CRPS, exact centring). Its
known weakness is key-number mass (predicted |1H margin| = 3: 0.088 vs observed 0.124); the unshifted kernel
matches key numbers but mis-centres. The cross-engine gap between the period engine's implied full game and the
game engine on the same centre is reported per game on every run (mean margin gap typically under 1 point).

### 4.2 Player engine v2 (research/player_engine_v2/RESULTS.md)

* `LatticeDistribution` — a validated pmf on the integer grid; every rung, range and moment is derived from it.
* `DATA_PLAYER_DIST` — opportunity × efficiency with the v2 features (team volume, target/carry/snap share, recent
  share change, QB change), family chosen out of sample per statistic (Study A: attempts → normal, passing_tds →
  negbin; the rest confirmed); prior-only by construction (tested).
* `MARKET_PLAYER_DIST` — PAV-monotone bid / mid / ask envelopes of the quoted ladder, identification
  FULL / PARTIAL / UNDERIDENTIFIED / NONE, a two-parameter family fitted to the monotone mids (dispersion from a
  statistic prior when underidentified). Rungs wider than 20c or one-sided are excluded.
* `HYBRID_PLAYER_DIST` — pmf mixture (0.7 market) — a RESEARCH arm. The preregistered selection on 2025 weeks 1-9
  chose the market outright; **no hybrid beat the market** on weeks 10-18 (closest +0.00091 ± 0.00056 Brier).
* Study B (77,207 rung × horizon rows, 264 games): market 0.187 Brier, data v2 0.197, old model 0.199; the market
  wins at every horizon and every statistic except passing TDs (n=684, z −0.4). data_v2 beats the old model on
  touchdowns (z −2.2) and modestly on passing / rushing yards; it is worse on receptions (z +1.5).

### 4.3 Coherence engine (`nfl_edge/engines/coherence.py`)

Groups contracts by event through their questions, decides MUTUALLY_EXCLUSIVE / COLLECTIVELY_EXHAUSTIVE /
PARTIAL_SET / AMBIGUOUS, reports Σmid − 1 as **research incoherence**, and computes the executable statement
from the bids and asks with the exchange fee applied exactly once per leg through the committed schedule
(`net_executable_ev`). "Executable opportunity" is claimed only when buying every leg costs < $1 or selling every
leg pays > $1 after fees with every leg two-sided at the same instant. On the 2026-09-11 snapshot: 151
collectively exhaustive groups, 101 with |Σmid − 1| > 2c, **0 executable opportunities**.

## 5. Projection records and horizons

`ProjectionRecord` fields: identity (record_id, snapshot, ticker, arm, engine/distribution/model versions,
evidence class), contract (family, period, stat, the question verbatim, semantic confidence, settlement rule
version), football identity (game, season, week, teams, subject id/kind/kalshi id, identity confidence), time
(observed_at, generated_at, kickoff, minutes to kickoff, data cutoff, horizon label/target/lateness/id), market
(bid/ask both sides, mid marked research-only, width, volume, OI, liquidity, confirmed), projection (p_yes,
contract_value, band, support state and reason, data quality, lineage, distribution summary), disagreement
(vs mid, vs yes ask, vs no ask). `finalize()` refuses a probability outside [0, 1] or on a refused state.

The store is append-only: the same snapshot/arm is NO_OP when identical and CONFLICT (nothing written, exit 4)
when different. Horizons T-24h / T-6h / T-90m / T-30m are marked append-only under `data/shadow/v2/horizons/`;
a horizon whose kickoff passed is MISSED, reported, never reconstructed. A run that happens after kickoff writes
`POST_KICKOFF` without a probability unless `--allow-historical` is passed (local validation only; the workflows
never pass it), in which case the records are `HISTORICAL_RESEARCH` and the scorecard keeps them apart.

## 6. Settlement v2, autopsy v2, scorecard v2

* `nfl_edge/settlement/settle_v2.py` settles WIN_MARGIN_BUCKET, every period market (from `period_results.py`,
  contradiction-aware against the schedule final), HALF_FULL_RESULT, PLAYER_STAT incl. rush_rec_yards (through the
  incumbent's participation logic), SEASON_WINS / SEASON_WINS_EXACT (only when every regular-season game is FINAL);
  everything else is refused with a reason. Deterministic and idempotent; the corpus is write-once per game per
  settlement version (`EvaluationCorpus` pattern, contradiction = hard error).
* `nfl_edge/engines/player/autopsy_v2.py` classifies the first component off in causal order:
  AVAILABILITY_MISS → SNAP_SHARE_MISS → ROUTE_PARTICIPATION_MISS (needs route data; INSUFFICIENT_DATA today) →
  QB_ENVIRONMENT_MISS → TEAM_VOLUME_MISS → TARGET/CARRY_SHARE_MISS → EFFICIENCY_MISS → TAIL_SHAPE_MISS →
  UNEXPLAINED_VARIANCE / NO_LARGE_MISS / INSUFFICIENT_DATA. Diagnosis only; feeds nothing.
* `nfl_edge/evaluation/scorecard_v2.py`: Brier, log loss, calibration (ECE), sharpness, Brier − market with
  game-clustered SE, directional hit rate, executable P&L at the ask with fees once, per engine / arm / family /
  statistic / horizon / identification / availability / liquidity / width, paired arms on common contracts, per
  evidence class.

## 7. Isolation

* Frozen files (`tests/test_incumbent_unchanged.py` SOURCE_PINS and `FREEZE_WEEK1_2026.json`) are unchanged.
* v2 writes only under `data/shadow/v2/` on `market-data`; it never reads or writes `data/shadow/ledger`,
  `data/shadow/evaluations`, `data/shadow/arms`; `tests/test_project_slate_v2.py` pins that the projector
  imports none of the pricer, ledger, gates, risk or preflight modules.
* The three workflows are guarded `if: github.ref == 'refs/heads/main'` and, being scheduled, only fire from the
  default branch: inert until merged.
* Sunday 2026-09-13's frozen forecasts are produced by main's experiment; branch code never reinterprets them.
  Local validation runs on this branch wrote nothing to `market-data`.

## 8. Operating

```
python3 scripts/shadow_v2/board_accounting.py --market-data /tmp/md [--projections data/shadow/v2/projections] [--assume-provisional-capture]
python3 scripts/shadow_v2/project_slate_v2.py --market-data /tmp/md --out data [--horizon-id <id>] [--snapshot-id <id>] [--limit-games N]
python3 scripts/shadow_v2/verify_projections.py --root data/shadow/v2/projections --require-rows
python3 scripts/shadow_v2/settle_v2.py --market-data /tmp/md --out data/shadow/v2 [--game <id>] [--dry-run]
python3 scripts/research/period_engine_study.py ; python3 scripts/research/player_engine_v2_study.py
```

Performance (2026-09-11 snapshot, 12,281 quoted contracts, 30 game environments, 40,000 draws, 4 vCPU):
see the run summary under `data/shadow/v2/runs/<snapshot>.SUMMARY.md` (runtime, peak RSS, bytes written, zero
API calls — v2 reads captures only). The first run per season builds the period-score silver table from
play-by-play (2012-2025, 264 MB of parquet already downloaded by the shadow cycle) and caches it.

## 9. Limitations (also in KNOWN_LIMITATIONS.md)

1. Every v2 family is shadow: zero prospective evidence exists before merge; the first record that counts is the
   first written by main after merge.
2. The period engine under-predicts key-number mass; the alternative that matches it mis-centres. No historical
   market comparison is possible.
3. No hybrid player blend beat the market historically; the HYBRID arm exists to accumulate prospective evidence
   about the best-known blend, not as a candidate for authority.
4. Availability inputs are UNKNOWN when the context captures are absent (recorded per record); P(plays) then
   falls back to the population rate for UNKNOWN.
5. Season engine: approximate tie-breakers; centres from the consensus spread where published (102 of 271
   remaining games at the time of writing) and a home-field prior elsewhere; conference / Super Bowl winners need
   a bracket simulation and stay RESEARCH_REQUIRED.
6. RACE_TO_N, FIRST_TD_TEAM, TOTAL_TD, TEAM_STAT and the season leader / matchup / fantasy families are
   RESEARCH_REQUIRED (no scoring-sequence or drive model); the season-seed grammar is AMBIGUOUS.
7. ROUTE_PARTICIPATION_MISS cannot fire: routes are not in free data.
8. `market_confirmed` follows the capture manifest; a series not fetched completely in the run is STALE_MARKET.
