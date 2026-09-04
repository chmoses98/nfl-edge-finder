# Prospective protocol (2026 season)

1. **Freeze.** `research/FREEZE_2026-09-04.json` hashes every research artifact produced before the first 2026 regular-season
   outcome (kickoff 2026-09-09). These files are never overwritten; new analyses get new paths and a new freeze entry.
2. **Ledger.** Every prospective probability is written once with: prediction_id, timestamp, game, market ticker,
   player, threshold, raw p, calibrated p, model version + artifact hash, calibration version, feature cutoff,
   market bid/ask observed, data-source health, quality state. Rows are append-only on `market-data`
   (`data/ledger/<date>/*.jsonl`, to be created with Milestone J).
3. **Windows.** Snapshots are labelled after the fact from `minutes_to_kickoff` (OPEN, T-48H, T-24H, T-12H, T-6H,
   T-3H, T-90M, T-60M, T-30M, CLOSE) with the actual distance recorded; missing windows are MISSED, never filled.
4. **Full universe.** Every supported market is priced at every window, selected or not, so CLV and calibration are
   measured without selection bias.
5. **Settlement.** Outcomes come from Kalshi `result`/`settlement_value` (daily discovery) cross-checked against
   nflverse box scores; disagreements are flagged, not resolved by hand in the ledger.
6. **Calibration cadence.** No calibration artifact is fitted before ≥ 4 weeks and ≥ 300 settled rungs per family
   group; a candidate must beat the incumbent on held-out weeks before it becomes ACTIVE; old artifacts are RETIRED,
   never deleted.
7. **No self-training on losses.** Weekly error analysis generates hypotheses into the registry; production changes
   only through the promotion gates (docs/ROADMAP.md, milestone L).
8. **Real money.** Not authorized. Automatic execution is not implemented.
