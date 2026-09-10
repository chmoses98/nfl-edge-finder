# Three-arm implementation: historical validation (pre-2026, software and methodology only)

Reproduce: `python3 scripts/research/three_arm_validation.py`. Nothing here is a betting result and nothing was tuned: the
features, hyper-parameters and the 0.70/0.30 weight are the research's (`research/game_model/`), frozen before the first
2026 outcome. The **consensus closing line stands in for the market centre**, because it is the only historical market
this repository has; prospectively the CURRENT arm is the Kalshi-implied centre at each snapshot, which is the whole point.

## V1 — the reusable DATA_ONLY reproduces the frozen walk-forward research
Max |difference| against `walkforward_predictions.parquet` over 3151 games, 12 seasons: **0.00e+00** (ok: True).

## V2 — centre accuracy, 2014–2025 (n = 3,151), and the hybrid reconciliation

| arm | margin RMSE | margin MAE | margin bias | total RMSE | total MAE | total bias |
|---|---|---|---|---|---|---|
| CURRENT_MARKET_PRIOR | 12.881 | 9.946 | +0.006 | 13.179 | 10.454 | -0.300 |
| DATA_ONLY | 13.261 | 10.312 | +0.312 | 13.524 | 10.712 | -0.218 |
| HYBRID_30_DATA | 12.914 | 9.989 | +0.097 | 13.209 | 10.476 | -0.275 |

Frozen research: closing spread RMSE 12.8805, model 13.2610, 0.3 blend 12.9145; ours 12.8805 / 13.2610 / 12.9145 (reconciled: True).

| paired comparison | games | mean diff in abs margin error | 95% CI | total: mean diff | 95% CI |
|---|---|---|---|---|---|
| DATA_ONLY_vs_CURRENT_MARKET_PRIOR | 3151 | +0.366 | [+0.263, +0.469] | +0.258 | [+0.157, +0.358] |
| HYBRID_30_DATA_vs_CURRENT_MARKET_PRIOR | 3151 | +0.043 | [+0.011, +0.076] | +0.022 | [-0.010, +0.053] |
| HYBRID_30_DATA_vs_DATA_ONLY | 3151 | -0.323 | [-0.396, -0.249] | -0.236 | [-0.307, -0.165] |

Weeks 1–4 margin RMSE: CURRENT_MARKET_PRIOR 13.176, DATA_ONLY 13.449, HYBRID_30_DATA 13.178.

## V3 — ratings rebuilt from fresh silver reproduce the frozen snapshots

| season | week | teams | max |diff| |
|---|---|---|---|
| 2019 | 3 | 32 | 1.78e-15 |
| 2022 | 9 | 32 | 3.55e-15 |
| 2024 | 5 | 32 | 1.33e-15 |
| 2025 | 1 | 32 | 1.78e-15 |
| 2025 | 10 | 32 | 8.88e-16 |
| 2025 | 18 | 32 | 2.66e-15 |

## V4 — the three centres through the common-random-number simulator (2020–2025, consensus close as market)

1610 games, 40000 draws per arm, one uniform set per game shared by all three arms; the residual bank is the
four seasons before each test season. Rungs within a game are correlated, so the naive SEs are optimistic.

| arm | home win Brier / log loss | spread ladder Brier (5 rungs) | total ladder Brier (5 rungs) |
|---|---|---|---|
| CURRENT_MARKET_PRIOR | 0.2110 / 0.6096 | 0.1947 | 0.2334 |
| DATA_ONLY | 0.2232 / 0.6385 | 0.2037 | 0.2409 |
| HYBRID_30_DATA | 0.2127 / 0.6138 | 0.1954 | 0.2343 |

Paired Brier differences vs CURRENT: DATA_ONLY_minus_CURRENT_home_win +0.01224 (naive SE 0.00253); DATA_ONLY_minus_CURRENT_spread_ladder +0.00904 (naive SE 0.00103); DATA_ONLY_minus_CURRENT_total_ladder +0.00750 (naive SE 0.00111); HYBRID_30_DATA_minus_CURRENT_home_win +0.00174 (naive SE 0.00091); HYBRID_30_DATA_minus_CURRENT_spread_ladder +0.00071 (naive SE 0.00039); HYBRID_30_DATA_minus_CURRENT_total_ladder +0.00082 (naive SE 0.00051).
Frozen normal-CDF reference (research): {'logloss_spread': 0.6123459974987375, 'logloss_model': 0.634006248174119, 'logloss_blend30': 0.6152839910583767, 'brier_spread': 0.21219825517304075, 'brier_model': 0.2217693443840066, 'brier_blend30': 0.21341146069673347}.

## V5 — leakage audits

* future team-games perturbed by +100 at and after the cutoff leave every prior rating unchanged: {'max_abs_change': 0.0, 'ok': True}
* the frozen artifact trains only on seasons before its target: {'train_seasons': [2018, 2025], 'target': 2026, 'ok': True}
* market columns dropped from the schedule before DATA_ONLY sees it: ['away_moneyline', 'away_spread_odds', 'home_moneyline', 'home_spread_odds', 'over_odds', 'spread_line', 'total_line', 'under_odds']
* `spread_line` offered as a feature is refused by the whitelist attestation: {'ok': True}

## What this does and does not establish

It establishes that the production DATA_ONLY is the research model, that HYBRID_30 is the blend it says it is, that the simulator
is the incumbent's with shared draws, and that no future or market information reaches the football-only centre. It re-establishes
the research's negative result against the CLOSING line. It says nothing about T-24h, T-6h, T-90m or T-30m Kalshi centres, which is
the prospective question and begins only with the first three-arm snapshot written after this code is merged.
