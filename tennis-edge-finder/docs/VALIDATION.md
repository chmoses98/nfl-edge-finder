# Validation

* **Walk-forward only.** Ratings are replayed chronologically (tourney_date, tourney_id, round order, match_num);
  the prediction for a match uses the state before that match. No random splits. Evaluation seasons >= 2015;
  warm-up from 1990.
* **Symmetric scoring.** Orientation is randomised (winner-first rows would make calibration trivial).
* **Benchmarks.** Pinnacle and Avg bookmaker prices (vig removed proportionally; Shin available) on the
  linked ATP 2020-2026 subset. Market is always shown beside the model.
* **Hybrid.** Logit blend weights fitted on seasons < t, evaluated on t; a market-only recalibration control.
* **Disagreement buckets** with per-bucket Brier/log-loss/win rate/hypothetical ROI at vig-free prices.
* **Bootstrap** paired CIs for every model-vs-baseline difference.
* **Leakage defences:** as-of replay; retirements weighted 0.5 and walkovers skipped in updates; rank baseline
  uses pre-tournament ranks from the same row (Sackmann ranks are "as of tournament start"); no closing lines in
  any feature; final holdout: seasons 2025-2026 were evaluated once with the same code and reported as-is.
* **Engine validation:** DP vs Monte Carlo agreement tests; closed-form game values; format registry tests.

See research/elo_study/RESULTS_*.md, research/market_benchmark/RESULTS_*.md for numbers.
