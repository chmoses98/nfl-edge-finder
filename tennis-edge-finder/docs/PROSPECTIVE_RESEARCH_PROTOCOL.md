# Prospective research protocol

1. Every projection run appends one row per priced market to `data/research/ledger/<day>.jsonl`
   (`ledger/predictions.py`): prediction_id, generated_at_utc, match_id (event ticker), ticker, family,
   feature_snapshot_id (ratings hash), data_source_versions (discovery run, ratings build time), model_version,
   git_sha, market quote at prediction time (bid/ask both sides, source, timestamp, volume, OI, liquidity),
   all model probabilities (ELO, STRUCTURAL, ENSEMBLE, ELO_DP_FAIR, MARKET_MID, HYBRID placeholder),
   quality pillars, scheduled_start, seconds_to_scheduled_start, fee-adjusted EV fields, prev_hash, row_hash.
2. Rows are never rewritten. Actual start, sports truth, exchange truth and canonical close are recorded in
   SEPARATE settlement tables keyed by prediction_id. Gate TENNIS-12 verifies the hash chain.
3. Pregame validity: a row counts as a pregame prediction only if generated_at < actual_first_ball (or, while
   first-ball truth is unavailable, < scheduled_start - 5 min, flagged SCHEDULED_MINUS_MARGIN). Post-start rows
   are excluded from every evaluation (TENNIS-6).
4. Scoring: Brier/log-loss/calibration of each model column vs the market mid at prediction time AND vs the
   canonical close; executable CLV against the close; disagreement buckets. Reported per family, tour, level.
5. Promotion: a model column may become the decision model only after a pre-registered prospective window
   (>= 1,000 gradeable match-winner predictions, >= 8 weeks, all tours) in which it beats the market mid on
   log-loss with a bootstrap CI excluding zero AND shows non-negative executable CLV. Real-money authority
   is a separate, human decision after that.
6. Multiple testing: subgroup claims require n >= 300 per subgroup, holdout confirmation, and the
   hypothesis must have been registered in `research/hypothesis_registry.md` before the evaluation window.
