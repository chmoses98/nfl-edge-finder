# Hypothesis registry

Every hypothesis is written down before it is tested. Status is one of PROPOSED, REGISTERED_PROSPECTIVE, VALIDATED_RESEARCH, LARGELY_ANSWERED, REJECTED.

| id | status | target | expected direction |
|---|---|---|---|
| `H-20260904-001` | REJECTED | margin, total | lower RMSE than close |
| `H-20260904-002` | PROSPECTIVE_REQUIRED | close price − early price | feature-predictable movement |
| `H-20260904-003` | TESTING | ladder consistency, tail calibration | tails overpriced (YES ask too high at 100+/120+) |
| `H-20260904-004` | PROPOSED | target share, end-zone target rate | positive |
| `H-20260904-005` | REJECTED_AT_CLOSE | margin residual vs early price | price moves toward model after news |
| `H-20260904-006` | PROMISING | total residual, passing yards | negative |
| `H-20260904-007` | VALIDATED_RESEARCH | CRPS, tail Brier at 100+/120+ | heavy-tailed families win at tails |
| `H-20260904-008` | VALIDATED_RESEARCH | P(player takes >=1 offensive snap) | observed play rates within a few points of the priors |
| `H-20260904-009` | PROPOSED | P(anytime TD >= 1) | improves Brier and removes the -1.7pt bias on Kalshi rungs |
| `H-20260904-010` | REGISTERED_PROSPECTIVE | Brier and log loss of P(Y >= k) at listed Kalshi rungs, player statist | shadow-0.3.0 beats the shadow-0.2.0 feature set on 2026 rungs by roughly the ret |
| `H-20260904-011` | LARGELY_ANSWERED | realised settlement rate of player-prop contracts versus the model pri | If the market carries YES-side juice, realised settlement rates fall between the |
| `H-20260904-012` | REGISTERED_PROSPECTIVE | correlation between |model - mid| and quoted width across snapshots, a | The correlation persists across every 2026 snapshot, and contracts selected on m |
| `H-20260904-013` | REGISTERED_PROSPECTIVE | mean (model - market) probability by ladder position, centre removed,  | if the effect is real it persists across snapshots at roughly -0.02 low / +0.02  |
| `H-20260904-014` | REGISTERED_PROSPECTIVE | residual of realised total minus the Kalshi-implied total at the same  | If the market underprices forecast wind, high-forecast-wind games settle under t |
| `H-20260904-015` | REGISTERED_PROSPECTIVE | calibration bias on rungs the model prices below 0.20, and aggregate B | Bias on p<0.20 rungs shrinks by roughly 75-80% (retrospectively -0.0095 to -0.00 |
| `H-20260904-016` | REJECTED | realised settlement rate minus closing midpoint, and NO-side net retur | The calibration bias persists on 2026 settled markets at roughly the same magnit |
| `H-20260904-017` | REGISTERED_PROSPECTIVE | realised settlement rate minus closing midpoint on player props, and N | The YES-side overpricing persists on 2026 settled props at roughly 2-5 points an |
| `H-20260904-018` | REGISTERED_PROSPECTIVE | Brier difference (model minus market) and net return after fees from t | The gap narrows with shadow-0.3.0 role features but does not close: predicted re |
