# Architecture

```
FREE DATA INGESTION            nflverse releases (bronze, immutable, manifest+sha256)   Kalshi API (Actions only)
        │                                 │                                               │
        ▼                                 ▼                                               ▼
BRONZE  data/raw/nflverse/<release>/…     data/kalshi/{discovery,capture,backfill}/…  (orphan branch market-data)
        │
SILVER  data/silver/games.parquet, team_game.parquet, player_crosswalk.parquet, kalshi_player_map.parquet
        │      (nfl_edge/data/silver.py, ids.py)   canonical ids: GSIS player, nflverse team code, nflverse game_id, Kalshi ticker
        ▼
GOLD    point-in-time features: ratings snapshots (season, week) built only from prior games
        │      (nfl_edge/research/team_ratings.py)   player EWMA/opportunity features (nfl_edge/research/player_distributions.py)
        ▼
MODELS  team/game (Milestone E), player distributions (F), calibration (I) …  →  PROJECTION rows with model/calibration/data-cutoff versions
        ▼
PRICER  P(YES) for every Kalshi market from the classifier's semantics (family, threshold, operator, period)
        ▼
MARKET  executable bid/ask, book depth, trades, fees  → edge, uncertainty, correlation groups, best expression
        ▼
LEDGER  immutable prospective predictions (never overwritten) → EVALUATIONS (a second immutable corpus: settlement proven from nflverse, close chosen strictly pre-kickoff) → CLV / calibration / error analysis
```

Hard boundaries: RESEARCH (this repo's `research/`, free to experiment) → SHADOW (prospective predictions written to the ledger with no authority) → PRODUCTION (only models that pass `docs/PROMOTION.md` gates; none exist yet). Automatic trade execution is not implemented and not authorized.

## Repository layout
* `nfl_edge/kalshi/` — read-only client, classifier (market semantics), registry helpers.
* `nfl_edge/data/` — bronze→silver builders and entity resolution.
* `nfl_edge/research/` — reusable research code (ratings, distributions).
* `nfl_edge/settlement/` — contract semantics, proven final results, and the postgame settlement engine.
* `nfl_edge/shadow/` — the prospective ledger, the derived evaluation corpus, the evaluation scorecard, the decision funnel and the player autopsy.
* `nfl_edge/arms/` — the prospective three-arm game-centre experiment (CURRENT / DATA_ONLY / HYBRID_30): common-random-number simulation, football-only centre, an exact replay of the frozen pricer for the CURRENT centre, the player-anatomy corpus, immutable arm records, evaluation and scorecard. Reads the ledger, never writes it (`docs/PROSPECTIVE_THREE_ARM_EXPERIMENT.md`).
* `nfl_edge/semantics/`, `nfl_edge/engines/`, `nfl_edge/projection/`, `nfl_edge/board/`, `nfl_edge/evaluation/`, `nfl_edge/shadow_v2/`, `scripts/shadow_v2/` — the full-board SHADOW v2 layer (question grammar, game / period / joint / season / player engines, coherence audit, universal projection records, board accounting, settlement v2 and the universal scorecard). Shadow only; reads the frozen incumbent, never writes its ledger (`docs/SHADOW_V2.md`).
* `scripts/data|kalshi|research|ci` — runnable entry points; `.github/workflows` — discovery/capture/backfill.
* `config/kalshi_nfl_series.json` — reviewed series registry with capture tiers.
* `research/` — experiment outputs (results.json + RESULTS.md per study), `research/hypothesis_registry/`.
* `docs/` — audit, taxonomy, API notes, capture, architecture, roadmap, limitations, postgame settlement.

## Data lineage rules
1. Bronze files are never edited; each has url, retrieval time, sha256 and upstream Last-Modified in `_manifest.jsonl`.
2. Silver tables are pure functions of bronze (rebuildable with `python nfl_edge/data/silver.py`).
3. Gold/feature code takes an explicit `(season, week)` or timestamp and may only read rows strictly before it.
4. Kalshi rows carry `observed_at`, `run_id`, `trigger_source`, and preserve Kalshi's own `result` verbatim — the capture never infers a settlement.
   The EVALUATION corpus is the one place a settlement is derived, and it derives it from nflverse final results with the evidence attached, refusing
   whatever it cannot prove (`docs/POSTGAME_SETTLEMENT.md`). Kalshi's `result` is recorded there as a cross-check and never as the truth: it reproduces
   15,009 of 15,021 archived 2025 settlements, and the exceptions are Kalshi settlements that contradict their games' own final scores
   (`research/settlement_validation/RESULTS.md`).
5. Every prospective prediction row must carry model version, calibration version, feature cutoff and market price observed.
