# tennis-edge-finder

Free-data tennis projection and Kalshi tennis-market research platform. **Status: research / market capture.
Real-money authority OFF. No model has shown edge against bookmaker prices; see MORNING_REPORT.md.**

## What it does
* Discovers the entire Kalshi tennis universe dynamically (143 series, 165k markets parsed), normalises every
  market into a payoff definition, and captures quotes/books/trades/settlements/candles prospectively.
* Builds a canonical match table from Sackmann (ATP/WTA all levels) + TML (ATP) snapshots with validation,
  quarantine and provenance (1.6M matches, 1990-2026).
* Rates players walk-forward (Elo family, structural serve/return), prices every match-scope market family
  from ONE exact match distribution (DP engine validated against Monte Carlo), checks probability invariants,
  and writes an append-only, hash-chained prediction ledger with the market quote beside every projection.
* Benchmarks against Pinnacle closing-style prices, fits walk-forward hybrids, reports disagreement buckets.

## Run
```
pip install -e . && python -m pytest -q tests
git fetch origin tennis-data && git archive origin/tennis-data tennis-edge-finder/data | tar -x   # snapshots
python tennis_edge/data/build.py                 # canonical matches.parquet
python -m tennis_edge.models.state --tour ATP && python -m tennis_edge.models.state --tour WTA
python scripts/run_tennis.py                      # projections + ledger + REPORT_<run>.md
python scripts/research/elo_study.py --tour ATP; python scripts/research/market_benchmark.py --tour ATP
```
Docs: docs/ARCHITECTURE.md, DATA_SOURCES.md, KALSHI_MARKET_TAXONOMY.md, IDENTITY.md, MODELING.md,
VALIDATION.md, CLV_AND_SETTLEMENT.md, PROSPECTIVE_RESEARCH_PROTOCOL.md, PRODUCTION_HEALTH.md,
KNOWN_LIMITATIONS.md. Report: MORNING_REPORT.md.
