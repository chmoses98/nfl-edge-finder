# Architecture

```
GitHub Actions runner (open internet)                      dev sandbox / owner machine (egress-restricted)
┌──────────────────────────────────────────┐              ┌──────────────────────────────────────────────┐
│ tennis-bootstrap.yml  (on demand)        │              │ tennis_edge/data/build.py  -> matches.parquet │
│   scripts/data/bootstrap_sources.py      │  git fetch   │ tennis_edge/models/state.py -> ratings_*.json │
│   scripts/kalshi/discover_tennis.py      │ ───────────► │ scripts/run_tennis.py -> projections + ledger │
│ tennis-capture.yml (self-chaining loop)  │  tennis-data │ scripts/research/*  -> RESULTS_*.md           │
│   scripts/kalshi/capture_tennis.py       │   branch     │ tennis_edge/health/gates.py -> TENNIS-1..14   │
└──────────────────────────────────────────┘              └──────────────────────────────────────────────┘
```

Immutable evidence lives on the orphan `tennis-data` branch (`tennis-edge-finder/data/sources/<run>/`,
`data/kalshi/discovery/<run>/`, `data/kalshi/capture/<day>/<run>.*.jsonl.gz`); code lives on the code branch;
nothing under `data/` is committed to the code branch.

## Layers (tennis_edge/)
| package | role |
|---|---|
| `kalshi/` | read-only API client; series taxonomy classifier; family registry; market parser (rules text -> payoff) |
| `data/` | gz/xlsx readers; Sackmann/TML normaliser + validation/quarantine; tennis-data odds loader + vig removal; multi-source builder with provenance |
| `identity/` | name normalisation; player registry + alias table; tennis-data ↔ canonical linking with confidence; Kalshi competitor mapper (fail closed) |
| `rules/` | score parser; match formats + data-driven registry (config/formats.json) |
| `sim/` | exact DP engine (game/tiebreak/set/match distributions, inversion); Monte Carlo validator |
| `models/` | Elo family; structural serve/return; production state fitter; data-quality score |
| `pricing/` | payoff pricing from one distribution; consistency invariants; fees; competition/level/surface inference |
| `futures/` | exact bracket DP for tournament winner / round advancement |
| `doubles/` | team identity + baseline interface (explicitly unvalidated) |
| `ledger/` | append-only hash-chained prediction ledger; SportsTruth / ExchangeTruth; canonical close + CLV |
| `eval/` | proper scores, calibration, paired bootstrap |
| `health/` | gates TENNIS-1..14 |

## One universe, many payoffs
`run_tennis` builds, per match, ONE `MatchDistribution` from point-win probabilities (inverted from the
ensemble match probability with the tour/surface serve baseline) and prices every family on that event as a
functional of it; `check_consistency` enforces winner = sum of exact-score paths, monotone ladders, set-mass
constraints. Tournament markets reuse the same matchup function through the bracket DP.

## Automated settlement flow (designed; parts pending external feeds)
DISCOVER MATCH (discovery/capture) → CAPTURE MARKETS (10-min quotes/books, global trade tape) → GENERATE
PREGAME PROJECTIONS (run_tennis, ledger) → DETECT ACTUAL START (**needs live-score feed; interface in
ledger/close.py**) → FREEZE PREGAME CORPUS → DETECT FINAL RESULT (Sackmann/TML refresh, Kalshi
expiration_value as secondary) → INGEST SPORTS TRUTH → INGEST KALSHI TERMINAL SETTLEMENT (capture
settlements stream) → SELECT CANONICAL CLOSE (candles/quotes before cutoff) → SCORE MODEL → CLV → REPORTS.
