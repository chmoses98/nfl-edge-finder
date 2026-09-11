# Hypothesis registry (pre-registration log)

Every hypothesis is registered BEFORE its evaluation window; results are appended, never edited.

| id | registered | hypothesis | test | status / result |
|---|---|---|---|---|
| H-T01 | 2026-09-11 | Walk-forward Elo carries information beyond Pinnacle pre-match prices (ATP 2020-26) | paired bootstrap Brier; walk-forward logit hybrid weight | REJECTED: model +0.0143 Brier worse; hybrid weight on model −0.05 |
| H-T02 | 2026-09-11 | Structural serve/return beats Elo on tour-level matches | same linked set | SUPPORTED (Brier 0.2133 vs 0.2169, CI excludes 0) but still worse than market |
| H-T03 | 2026-09-11 | Logit-average ensemble beats both components | same | SUPPORTED (0.2111); still worse than market by 0.0085 |
| H-T04 | 2026-09-11 | Large model-market disagreements (>20 pp) are market error | disagreement buckets, hypothetical ROI at vig-free price | REJECTED: model-favoured side wins 32.5 % vs 35 % implied; ROI −9 % |
| H-T05 | 2026-09-11 | Frozen (1-4 month stale) model beats Kalshi conservative pregame quote | 1,869 settled match markets Jul-Sep 2026 | REJECTED: Kalshi Brier 0.1871 vs 0.2060; all buckets negative ROI after fees |
| H-T06 | 2026-09-11 | Rest / recent load / surface switch / rank add walk-forward value on top of the ensemble | feature ablation, seasons < t → t | see research/market_benchmark/RESULTS_ABLATION_ATP.md |
| H-T07 | 2026-09-11 | On KXATPMATCH specifically the ensemble matches Kalshi (LL 0.5736 vs 0.5735, n=167) | PROSPECTIVE: needs ≥ 1,000 pregame-valid ledger rows with a first-ball-based close | OPEN (registered, not evidence) |
| H-T08 | 2026-09-11 | Derivative markets (totals / spreads / exact) priced from the DP distribution are closer to settlement than the Kalshi pre-start quote | PROSPECTIVE via ledger + settlement streams; needs canonical close | OPEN |
| H-T09 | 2026-09-11 | Kalshi ITF markets are efficient relative to Challenger (LL 0.525 vs 0.604 at 7 h pre-close) | descriptive only | NOTED, not a tradable claim |
