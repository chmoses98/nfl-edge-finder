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

## 9. First-week instrumentation: close, CLV, context, lineage, research record

### 9.1 Canonical close (`nfl_edge/evaluation/close.py`, rule close-2.0.0)
The capture is change-suppressed, so a close has two instants: the last pre-kickoff **price change** row and the
last pre-kickoff capture run that fetched the series **completely** with the ticker still open (its manifest
`observed_at` = `confirmed_at`). `close_age_seconds` = kickoff − confirmed_at. Tiers: EXCELLENT ≤ 20 min, GOOD
≤ 90 min, STALE ≤ 24 h, MISSING beyond. Every close record carries ticker, source run, price run, both instants,
minutes before kickoff, yes/no bid/ask, mid, width, volume, OI, liquidity, capture completeness, market quality,
`close_id` and the rule version. Refused (CLV_CLOSE_MISSING, reason named): no pre-kickoff row, kickoff moved after
the projection, non-open status at the last row, confirmation older than 24 h, capture stamped at or after
kickoff. One-sided books are kept as CLOSE_ONE_SIDED with the missing side unpriced. Post-kickoff, settled, live,
synthetic and neighbouring-rung prices never become a close.

### 9.2 CLV (`nfl_edge/evaluation/clv.py`, clv-2.0.0)
**Sign convention (the only one): POSITIVE CLV = the market subsequently moved toward the side the frozen model
would have bought.** The side is decided only from horizon information (model contract value vs horizon mid;
|difference| ≤ 1e-9 is NO_VIEW). Concepts kept separately: A/B raw YES/NO mid moves, C/D executable ask moves, E
model-to-close (model cv − close mid; was the model ahead of the eventual consensus), F entry-to-close on the
model's side (close mid of that side − horizon ask of that side), G fee-aware (entry ask, entry fee through the
committed schedule applied once, break-even, close executable price and mid). `clv_mid_toward_model` is the
research quantity; `clv_exec_toward_model` and `clv_net_of_fee` are the economic ones. **CLV is not profit**:
positive CLV is an intermediate signal; proven positive EV needs calibration, execution, fees, liquidity, sample
and prospective validation. No model is promoted on a week of CLV.

### 9.3 Frozen context, market state, lineage (`nfl_edge/shadow_v2/context.py`, schema projection-2.1.0)
Every record carries compact inline blocks plus ids into a write-once **sidecar** per snapshot
(`<snapshot>.contexts.json.gz`): `player_context` (availability with sources and staleness, injury report and
practice status with the file vintage, depth-chart rank and team QB1 at the latest chart at or before the
snapshot, teammates listed / out, snap / target / carry share EWMAs, team pass / rush volume, sample size and
shrink, weather from the latest context capture at or before the snapshot, UNKNOWN + reason otherwise; route
participation and red-zone usage are UNKNOWN by construction), `game_context` (centres and source, implied points,
QB state from schedule and depth chart, rest differential, division game, roof / surface / stadium, weather,
availability summary, market and data freshness), `market_state` (price-change run, snapshot run, series
confirmation instant and completeness, last trade time from the tape or UNKNOWN, ladder rungs / widths /
identification / raw violations), `lineage` (capture and discovery runs, identity-map sha, nflverse retrieval
timestamps and shas per table, engine / semantics / catalog / schema versions, bundle sha, period-bank
fingerprint), `flags` (has_probability, semantics_proven, identity_resolved, settlement_supported,
historically_validated, prospectively_validated=False, execution_supported=False, betting_authorized=False) and
`horizon_quality` (ON_TIME ≤ 10 min from target, LATE_ACCEPTABLE ≤ 45 min, LATE_DEGRADED later, MISSED; target /
observation / generation timestamps; snapshot_reused). A late T-24h is never pooled with a clean one.

### 9.4 Research record, export, scorecard v3, weekly report (`nfl_edge/evaluation/research_record.py`, `scorecard_v3.py`)
`scripts/shadow_v2/pair_closes_v2.py` writes write-once close (`closes_v2`) and CLV (`clv_v2`) batches per game;
`research_export_v2.py` rebuilds one row per frozen projection joined by `record_id` to horizon market, close, CLV,
settlement, context and autopsy (jsonl.gz + parquet, derived and rebuildable); `weekly_report_v2.py` writes the
weekly report and the coverage health gate (board capture, projection, horizons, settlement, close pairing, CLV,
player context, autopsy, unsupported retention). Scorecard v3 scores model vs market@horizon vs market@close vs
outcome (the four questions of Part 8 kept apart), CLV blocks, executable P&L (ask, fee once), per horizon /
engine / arm / family / stat / position / probability band / price band / disagreement band (0-0.5 / 0.5-1 / 1-2 /
2-3 / 3-5 / 5-10 / >10 pp) / width / liquidity / availability / close quality / horizon quality. Every block is
labelled DESCRIPTIVE or HYPOTHESIS_GENERATING; PREREGISTERED_TEST and CONFIRMATORY only exist through the
registry. `research/hypothesis_registry/v2/` is append-only with GENERATED → PREREGISTERED → TESTING → SUPPORTED /
NOT_SUPPORTED / INCONCLUSIVE → RETIRED; a hypothesis cannot be tested on the window that generated it (enforced).
Unsupported markets are retained per discovery run with their prices (`data/shadow/v2/board/`).

## 10. Limitations (also in KNOWN_LIMITATIONS.md)

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
9. The close's `confirmed_at` relies on `state.last_seen` (the last run a ticker was seen open) and the manifest's
   per-series instants; per-run open sets are not stored, so a ticker delisted between two complete runs is dated to
   the last run it was seen, not to the delisting.
10. Weather, Sleeper and ESPN context exist only where the context-capture workflow ran on market-data; locally they
    are UNKNOWN and the health gate says so. Route participation and red-zone usage are UNKNOWN everywhere.
11. CLV has no historical validation of its own here; the first prospective week is its first evidence.

---

## 10. First-week evidence: settlement paths, presence, depth and real context

Round 2 of the instrumentation closed the gaps the first-week audit found. Everything here is SHADOW / RESEARCH
ONLY and carries `betting_authorized: false`.

### 10.1 Season settlement (`nfl_edge/settlement/season_settlement.py`, `season-settle-1.0.0`)

`TEAM_WINS_BY_WEEK`, `DIVISION_WINNER` and `MAKE_PLAYOFFS` were the last families carrying probabilities with no
settlement path. They now have one, and it never runs the NFL's tie-breaking procedure — which this repo
deliberately does not reproduce, and which is exactly why the season engine's projections are LIKELY and
shadow-only.

* **Wins through week W.** Counted from the team's own regular-season games. The final total lies between the
  wins already proven and those wins plus every game still to play, so the contract settles as soon as the
  comparison is constant across that interval — often long before the week arrives. What a TIE is worth is not
  pinned by the rules text, so both readings are evaluated and the contract settles only where they agree.
* **Division winner.** Read back off the postseason bracket. By rule the four division winners of a conference
  take seeds 1–4, and the wild-card round is played at the higher seed's home field, so seeds 1–4 are exactly
  {wild-card hosts} ∪ {bye teams}. The league applies its own tie-breakers when it seeds the bracket; reading
  the bracket back is reading the official answer. Refused unless the bracket is structurally complete (eight
  winners, four per conference) and unless each derived winner is tied-for-best on W-L-T inside its own
  division.
* **Make playoffs.** Presence anywhere in the bracket proves qualification. Absence from a structurally
  complete bracket (12 or 14 participants, split evenly by conference) proves elimination. Standings are never
  consulted, so a team cannot be declared out because its record looks bad.

### 10.2 Exchange cross-check (`nfl_edge/settlement/crosscheck.py`)

Every settled row is compared against Kalshi's own terminal resolution, read from the daily discovery's
`settled` bucket and the historical backfill — no API calls. The derived football result is **never** replaced
by the exchange value: a settlement that failed on football evidence stays failed. A disagreement is a hard
research-quality warning naming the family, because it means either we read the contract wrong or the exchange
settled against the football facts, and every projection priced on that reading is suspect.

### 10.3 Open-set evidence (`nfl_edge/evaluation/openset.py`, `openset-1.0.0`)

`state.last_seen` says when a ticker was last open. It cannot say whether a ticker was open at an *earlier* run,
so a contract the exchange delisted before kickoff and one missing because a series fetch half-failed were
indistinguishable after the fact. The capture now records the open set per run as a delta with a set hash and
periodic anchors, and the reader answers six distinct states:

| state | meaning |
|---|---|
| `OPEN` | in the open set of that run |
| `CLOSED` | absent, series complete, the contract's own `close_time` had passed |
| `DELISTED` | absent, series complete, `close_time` not reached — its last live quote **is** a legitimate close |
| `NOT_RETURNED_DUE_PARTIAL_FETCH` | the series fetch did not complete: **absence is not evidence** |
| `SERIES_NOT_POLLED` | the series was not fetched in that run |
| `UNKNOWN` | no open-set record for that run |

Only the first three are statements about the market. Close selection is unchanged (`close-2.1.0` keeps the same
rule) but a close now says **why** nothing came after it, and never claims confirmation at a run the open set
says the ticker was not open in.

### 10.4 Executable size (`nfl_edge/evaluation/execution_depth.py`)

A 1.2-point edge means nothing if four contracts were resting at the ask. Every record carries the depth on the
side the model would have bought, or `DEPTH_NOT_CAPTURED` with a named reason. The derived table walks the real
ladder for 1 / 5 / 10 / 25 / 50 / 100 contracts with the exchange's own per-fill fee carried across the order.

Three rules: **no book, no number** (never extrapolate the top level down the ladder); **partial fills are said
so**; and **canonical CLV is untouched** — top-of-book CLV keeps its definition and sign convention, and
size-adjusted execution lives in its own block. A test pins that separation.

Depth is captured at the horizons by `scripts/shadow_v2/capture_depth_v2.py`, not by the 10-minutely capture,
which is capacity-bound. The priority is a function of **market** properties only — kickoff proximity, whole
ladders, traded before untraded — and never of the model's own disagreement, because selecting the depth sample
by the quantity under study would make "edges survive size" indistinguishable from "we only measured size where
we had an edge". Coverage is reported by disagreement band so any residual gradient is visible.

### 10.5 Official inactives (`nfl_edge/shadow_v2/inactives.py`)

`scripts/data/probe_inactives.py` explains why this repo never had an inactives collector: a feed that silently
returns nothing does not degrade to "no information", it degrades to "everyone is playing". The collector is
built so that cannot happen. It can only ever ADD a confirmed-inactive player; **no code path emits an active
state** (pinned by test). A team block with an implausible count is UNUSABLE rather than half-true, an outage
yields zero rows, and an observation after kickoff is `POSTGAME_OBSERVATION` and freezes nothing. It is research
only and is not wired into the availability gate, whose `INACTIVE_CONFIRMED` state remains unpopulated by
design.

### 10.6 Route participation and red-zone usage

The previous round recorded both as UNKNOWN, on the stated grounds that "routes are not in free data". That was
wrong about this repo. nflverse `pbp_participation` lists the eleven offensive players on the field for every
play from 2016 through 2025, and those counts were already built into `research/opportunity/player_usage.parquet`
(102,422 player-games). The v2 projector simply never attached the role features. It now does, so route share,
targets per route run, red-zone target and carry share and inside-5 carry share are frozen per record as
point-in-time values over strictly prior games — **95.3% known**, where they had been 0%.

### 10.7 Coverage, honestly (`nfl_edge/evaluation/coverage.py`)

Every context field is reported KNOWN / UNKNOWN / NOT_APPLICABLE separately, because one aggregate percentage
hides the fields that matter. Two rules: a **state is not a value** (`injury_state = NOT_LISTED` is a correct
answer but is not knowledge of an injury status), and **NOT_APPLICABLE is not KNOWN** (a dome has no missing
wind). The first run of this audit immediately exposed a gap the aggregate had concealed: `injury_report_status`
is 0% known, because only 275 of 6,419 player rows are on a published report at all.

### 10.8 Availability change events (`nfl_edge/evaluation/availability_events.py`)

Transitions between horizons are **derived** from the frozen records, never captured separately, so they cannot
contradict what was observed. Direction is ranked by severity, both raw states are kept on every event, and a
source going quiet is `EVIDENCE_LOST` rather than a downgrade.

---

## 11. The point-in-time contract (remediation of the pre-week audit)

The pre-week institutional audit found that the no-hindsight rule had been implemented per source and had
diverged: four unbounded loaders sat next to four correct ones, sometimes in the same file. It also found that
the headline claim "zero probability records without a settlement path" was false. Both are fixed here.

### 11.1 One rule, one place (`nfl_edge/shadow_v2/pit.py`)

    source_observed_or_retrieved_at <= projection.data_cutoff

`pick_at_or_before` replaces every `sorted(glob(...))[-1]`. A `VintageLedger` records the vintage of every
time-sensitive source a run consumed and is frozen onto each record's lineage, so a record carries what is
needed to re-check its own compliance after the files have been rebuilt in place.

Three outcomes, and only one is a breach:

| | |
|---|---|
| no evidence at or before the cutoff | `UNKNOWN` with a reason. Normal and common. Never an error. |
| **skew** — a source later than the snapshot but before kickoff | recorded as the record's `information_frontier`. Unavoidable in normal operation: the job downloads nflverse after the capture run it prices. Measured on a real run: 2,234 s. |
| **outcome leak** — a source at or after the kickoff it predicts | refused, per game. The records lose their probability and are relabelled; a later game's records are untouched. |

A source dated after the run's own wall clock fails the whole run.

### 11.2 What was actually leaking

* **Availability** took the newest Sleeper/ESPN file with no cutoff, and that value reaches the priced contract
  value through `p_plays` on all three player arms.
* **Target-season silver** was read unbounded: results, **closing** spread and total lines, and finalised QB ids.
  Closing lines are now blanked for every target-season game — the consensus fallback refuses rather than
  borrowing a number that did not exist at the snapshot. Measured cost, reported plainly: probability-carrying
  records fall from 18,226 to 16,160. That is hindsight being removed, not coverage being lost.
* **Quotes** bounded files but never rows, and nothing at all on the default path.
* **Books** bounded by run id while the docstring claimed `observed_at`. Both axes are now enforced, and a book
  observed at or after its game's kickoff is rejected — which also defends against the measured corpus defect
  where 646 of 677,253 rows in `books.jsonl` were fetched post-kickoff.

### 11.3 Settlement reachability is measured, not asserted (`nfl_edge/settlement/reachability.py`)

`flags.settlement_supported` previously reflected the family **catalog**, so editing the catalog flipped it on
1,336 season records the settlement driver dropped before dispatch. Reachability is now a property of the
record: a branch exists **and** the record carries the keys that branch needs. One function serves the
projection flags, the settlement driver and the coverage matrix.

Season records now carry a season, derived from the Kalshi two-digit year cross-checked against the contract's
own expiration — Kalshi's `-27` is the season *ending* in 2027, i.e. nflverse 2026 — and refusing if the two
disagree. Measured on the real board: **16,114 of 16,160 dispatchable (99.72%)**, the remaining 46 being
`PLAYER_STAT` rows with an unresolved subject id, each carrying `MISSING_SETTLEMENT_KEYS`. Season rows with no
kickoff receive `CLOSE_NOT_APPLICABLE_SEASON` rather than disappearing from close pairing, and no fake kickoff
is invented to make game logic apply.

### 11.4 Depth is an independent stream (`.github/workflows/shadow-v2-depth.yml`)

Depth was a step inside the horizon job. A 20–30 minute sweep on a 15-minute cron with a 60-minute timeout and
`cancel-in-progress: false` queues the next firing behind it, and a horizon whose kickoff passes while queued is
`MISSED` and never reconstructed — so collecting depth put the evidence that already works at risk. It now has
its own workflow, concurrency group and `cancel-in-progress: true`, at a rate below the incumbent capture's.

Every row carries the target horizon **and** the actual observation as separate facts: `observed_at`,
`kickoff_utc`, `minutes_to_kickoff` recomputed from that observation, `horizon_delta_min` and
`horizon_quality`. A ladder is entered only if the whole ladder can finish before its own kickoff; a response
arriving at or after kickoff is rejected rather than written as pregame.

**One sweep is not "T-30" for every contract, and the system no longer claims it is.** Rehearsed at T-30 for the
largest real cluster (8 games kicking together, 4,896 probability-carrying contracts): 27.2 minutes at 3 req/s,
so observations span roughly T-30 to T-3 with 328 of 328 ladders whole and zero post-kickoff rows accepted.
Because research pairing selects the latest observation at or before each projection's cutoff and strictly
before kickoff, the target label is not load-bearing — the pairing age is, and it is recorded.

### 11.5 Injury-report maturity, and honest absence

A player absent from the parquet is not the same fact as a player absent from a complete report. The per-week
row and team counts are now measured and frozen, and the states are `LISTED` / `NOT_LISTED_AT_THIS_VINTAGE` /
`REPORT_NOT_AVAILABLE` / `SOURCE_UNAVAILABLE`. At the replay vintage week 1 of 2026 held 139 rows against a 2025
mean of 275.8 per week — half a typical week. nflverse rebuilds the file in place, so those counts are captured
now or they are unrecoverable.

### 11.6 Research queryability

The cross-check now joins by `prediction_id` carried from the row itself (it was reattached by positional `zip`
after a filtered loop) and its verdict is exported, so a researcher can exclude a family the exchange
contradicted. Availability events get a content-addressed identity and a join key that matches every sibling
row. Autopsy runs once per eligible DATA-arm prediction at every horizon with the denominator stated on the
row. `range_lo` / `range_hi`, distribution quantiles, `subject_kalshi_id`, evaluation versions, injury maturity,
inactive state and the point-in-time frontier are all exported.

---

## 12. Three paths, three different guarantees (post-re-audit)

The pre-week re-audit asked one question: *can a later piece of information create what looks like a small model
edge against an earlier market price?* The answer has three parts, because the system has three paths and they
are not equally protected.

### 12.1 PRICE PATH — bounded, and proven bounded

`contract_value` is computed from the market ladder at the cutoff, walk-forward features over strictly prior
seasons, and **availability** (`p_plays`, `p_active_no_snap`). Availability is the only context source that
reaches the priced number, and it is selected with `pit.newest_file_at_or_before(pattern, run_ts)` where
`run_ts` is the capture cutoff.

Proven adversarially: a Sleeper/ESPN capture landing at T2 (after the quote, before kickoff) is invisible to a
projection cut at T1, while an unbounded loader takes it. **No later information can move a price.**

### 12.2 RESEARCH PATH — skew is classified, and cannot masquerade as a synchronized edge

The model's information frontier routinely runs later than the market cutoff it is scored against, because the
job downloads nflverse after the capture run it prices — measured at **2,234 s** on the real board, on **100%**
of records. That is operationally unavoidable and not a breach. It is also *not* a like-for-like comparison.

Every record now carries, as a first-class block and not merely in lineage:

| field | meaning |
|---|---|
| `market_observed_at` | when this ticker's price last changed |
| `market_observable_through` | the capture cutoff — the last instant the market could have reacted |
| `model_information_frontier` | the newest source the model consumed |
| `generation_time` | when the projection was computed |
| `information_skew_seconds` | frontier − cutoff |
| `synchronization_state` | `SYNCHRONIZED` / `ASYNC_MODEL_NEWER_THAN_MARKET` / `UNKNOWN_TIMING` |

The cutoff is the comparison point, not the last price change: a quote whose price had not moved for six hours
was still observable and still tradeable right up to the cutoff. A stale quote is therefore not asynchronous.

The state is wired into the research export, `SEGMENTS`, a dedicated `by_synchronization` partition of
scorecard v3, the weekly report, and the hypothesis miner. **`candidates_from_scorecard` mines the
`SYNCHRONIZED` bucket and nothing else.** Asynchronous rows are scored in full, in their own bucket, where they
cannot be read as an edge — they remain a true record of what was believed and what was quoted.

The claim this protects: *"Doubtful players outperform the market"* is mined only when the rows behind it had
the designation available to the market too. Otherwise it says nothing beyond *"we read it first"*.

### 12.3 INJURY PATH — snapshotted immutably, because the source rewrites itself

`injuries_<season>.parquet` is rebuilt in place, and `date_modified` — present in 2024 — is **gone from 2025
on**, so the file cannot be bounded from the inside. Re-running an old cutoff with a newer file on disk
produced a different frozen context: `NOT_LISTED_AT_THIS_VINTAGE` became `LISTED / Doubtful / DNP`.

`nfl_edge/shadow_v2/vintage_snapshots.py` keeps every distinct version, content-addressed, with `retrieved_at`,
`source_url`, `season`, `sha256`, the immutable path, and the row/week/team census. The context reads the newest
vintage at or before the cutoff and **never the mutable file**; when no vintage qualifies the state is
`SOURCE_UNAVAILABLE` with the reason, not a silent read of today's fuller report. A file that cannot be dated at
all is refused for the same reason.

Snapshots are taken at download time and published to the evidence branch, because `data/raw/` is git-ignored
and a CI runner is ephemeral. **Both of those sentences were only half true until section 13 below**; read it
before relying on this one.

### 12.4 The incumbent capture is behind a default-off switch

`scripts/kalshi/capture.py` runs the live Sunday experiment and `kalshi-capture.yml` carries no branch
condition, so anything this branch changed there would have taken effect on the first dispatch after merge.
An earlier version changed the order-book selection rule unconditionally — under the 2,500-book cap that
changes *which* books the running experiment captures.

All v2 capture behaviour is now behind `--v2-capture` / `NFL_EDGE_V2_CAPTURE`, **default off**: the provisional
series universe, the v2 book priority, and the static-semantics quote fields. Unswitched, the script plans the
same series, requests the same books in the same order, and writes the same quote fields as `main`.
`tests/test_capture_isolation.py` pins the incumbent plan against main's rule directly.

Two things stay outside the switch, having been shown to change nothing the incumbent does: the open-set delta
(written after every request, to its own file, never fatal) and the `books_dropped_by_cap` count (a count of
the candidate list, which it does not reorder).

---

## 13. What the second independent audit found, and what changed (H1 / H2 / H3)

A genuinely independent pre-merge audit returned **B — REMEDIATION REQUIRED** with exactly three blockers. All
three were in the wiring around mechanisms that were themselves correct, which is why the existing tests passed
over them. Everything else the audit checked — point-in-time bounds, async quarantine, settlement enumeration,
depth pairing, inactives semantics, incumbent isolation — it reproduced as sound.

### 13.1 H1 — a vintage could move FORWARD in time

`read_index` deduplicated vintages by content hash **first-root-wins, local root first**, and `ensure_snapshot`
checked for "have I seen these bytes" against the **local index only**. On an ephemeral runner the local index
starts empty, so a run that re-downloaded an *unchanged* injury file found no match, registered those bytes
again under today's retrieval time, and that fresh row then shadowed the published one.

The vintage's observation instant therefore moved forward, past cutoffs it legitimately preceded. Reproduced:
with V1 (10 Sep) and V2 (11 Sep) both published and today's bytes equal to V2's, a projection at a 12 Sep cutoff
— entitled to V2 — got `SOURCE_UNAVAILABLE`, because every registered vintage now appeared to post-date it.

Fixed structurally, not defensively:

* `read_index` merges across every root into **one canonical row per content hash**, carrying the **earliest**
  retrieval instant ever recorded for those bytes — the instant that content is *known* to have existed.
  Evidence cannot move forward in time. Every instant ever seen is kept in `retrieved_at_history`, so the merge
  is auditable rather than asserted. An undated row can never displace a dated one.
* `ensure_snapshot` takes `extra_roots` and consults **all** of them, so content already published is
  recognised, returned as it stands, and neither copied nor re-dated. `resolve_injuries` threads the caller's
  roots through.
* Selection is unchanged in intent and now correct in fact: the **latest** vintage with `retrieved_at <=`
  cutoff, never the mutable file, and `SOURCE_UNAVAILABLE` with a reason when none qualifies.

`tests/test_injury_vintage_multiroot.py` models both production roots. The existing freeze tests all used a
single root, which is exactly why the defect survived them.

### 13.2 H2 — only one workflow made vintages durable

`shadow-v2-project.yml` runs every two hours, downloads the same mutable injury file, snapshotted it — and
discarded it with the runner. Only `shadow-v2-horizons.yml` published. Horizons fire at T-24h / T-6h / T-90m /
T-30m before a kickoff cluster, so the **Wednesday, Thursday and Friday practice-report states were captured
and permanently lost every week**.

One shared command now owns this: `scripts/shadow_v2/publish_vintages.py`, called by both v2 data runs. It
re-runs `ensure_snapshot` with `--market-data` as an extra root (idempotent, and after H1 it cannot re-date
anything), shards the index, and publishes. It is **fail-soft by default and exits 0** even when publishing
fails, so a failed publish can never cost a run its projections; `--strict` inverts that.

Published indexes are **sharded per run** (`index.<run_id>.jsonl`). `publish_market_data.py` publishes by
copying the source tree over a checkout of the branch, and on a rebase conflict it resets to the fresh tip and
re-copies — which silently overwrites a peer's append-only `index.jsonl`. Sharding follows the publisher's own
documented conflict policy: no run writes a path another run writes, so no line can be lost. Readers glob
`index*.jsonl`, so the old single-file layout still reads.

Incumbent workflows (`run-nfl.yml`, `shadow-price.yml`) also download injuries and still discard their
snapshots. That is deliberate and unchanged: they are not v2 data runs, and giving them v2 publishing
behaviour would alter incumbent jobs for no first-week benefit. Recorded as a limitation, not fixed here.

### 13.3 H3 — a mined hypothesis counted rows, not outcomes

`candidates_from_scorecard` applied `min_n` to the **slice's total row count** and reported that same number as
`sample_size`, with the slice's distinct-game count as `game_count`. Both include probability-bearing rows that
never settled and never can. Reproduced: a slice of **40 rows carrying 4 graded outcomes** cleared a threshold
of 30 and was written out as `sample_size: 40, game_count: 40, uncertainty: 0.0`.

For a programme hunting one- to two-point edges over a sharp market, that is manufactured evidence.

The two denominators are now separate **by name**, and only one of them can qualify anything:

| counts every row in the slice | counts gradable outcome evidence |
|---|---|
| `n`, `n_games`, `segment_rows_total` | `outcome_n`, `model_n`, `market_n`, `model_minus_market_n`, `settled_game_count`, `clusters` |
| coverage | thresholds, effects, uncertainty, promotion |

* eligibility and `sample_size` use `model_minus_market_n` — the paired set the effect is actually computed from
* `game_count` uses `clusters` — independent games, not rows, so ten contracts on one game are one observation
* both denominators travel on every candidate, so the gap can never be invisible again
* a candidate needs a **usable** uncertainty: fewer than two clusters yields no standard error, and a clustered
  SE at or below `SE_FLOOR` means every paired difference was identical — degenerate, not precise. Both are
  refused rather than published with an implied infinite z
* slices that fail any of these are written to `<candidates>.refused.json` with the reason, because why a slice
  did *not* qualify is evidence too

### 13.4 Capture isolation is now pinned on the REAL path

The audit noted that `tests/test_capture_isolation.py` pins `plan_book_requests`, which `main()` never calls —
a parallel implementation, not the production path. `tests/test_capture_isolation_integration.py` now runs the
**actual `main()`** of both this branch and the merge-base against one deterministic board behind a recording
client and a frozen clock, comparing the full API request sequence, every quote row byte-for-byte, the carried
state, every output file and the exit code. Only additive manifest keys and the open-set file may differ.

No capture code was refactored for it. Mutating `main()`'s inline sort leaves the old unit test green and fails
the new one, which is the whole point.

