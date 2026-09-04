# Hypothesis index

| id | status | rationale | result |
|---|---|---|---|
| H-20260904-001 | REJECTED | Opponent-adjusted EPA team ratings predict margin/total beyond the closing line. | RMSE 13.26 vs close 12.88; residual model 12.92; blend weight 0; ATS 50.0% (n=928) |
| H-20260904-002 | PROSPECTIVE_REQUIRED | Kalshi early-week prices (T-5d..T-48h) are less efficient than the close; football features predict subsequent movement. |  |
| H-20260904-003 | TESTING | Integer-threshold Kalshi ladders (totals, yards) are mispriced at tails relative to a well-calibrated empirical distribution; market monotonicity violations exist within ladders. |  |
| H-20260904-004 | PROPOSED | WR height advantage over likely covering CBs increases target share / end-zone targets. |  |
| H-20260904-005 | REJECTED_AT_CLOSE | Starting-QB change (backup starting) is under-reflected in early-week Kalshi prices. | team margin residual vs close after QB change: -0.50 [-1.43,+0.44], n=766 -> close already reflects |
| H-20260904-006 | PROMISING | Wind ≥15 mph forecast lowers totals and passing-yard tails more than the market prices. | observed wind 10-20 mph: total residual -0.9..-1.3 (CIs touch 0); calm 0-5 mph +1.2 [+0.1,+2.3] |
| H-20260904-007 | VALIDATED_RESEARCH | Distribution family choice matters for tail probabilities: NB/hurdle-lognormal beats normal for yards ladders. | yards: mu-binned empirical scale family wins (rec Brier 0.1009 vs normal 0.1024; only family with uniform PIT; P(rec>=100) 7.1% vs 7.0% obs; normal 4.7%); passing yards: censored normal; counts (targets/receptions/carrie |
