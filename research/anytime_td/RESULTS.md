# Direct anytime-touchdown model (replaces the count-derived probability)

`scripts/research/anytime_td_study.py`, model in `nfl_edge/shadow/models.py::DirectTDModel`.
The distribution study flagged that count families under-predict the 1+ TD rung by 2–3 points. Four candidates,
walk-forward (train seasons < S, test S), 35,774 player-games 2020–2025:

| model | Brier | log loss | mean pred | observed |
|---|---|---|---|---|
| **direct binary (logistic on role features)** | **0.12220** | **0.3921** | 0.168 | 0.168 |
| count → NB, P(Y ≥ 1) | 0.12528 | 0.4056 | 0.173 | 0.168 |
| count → Poisson, P(Y ≥ 1) | 0.12560 | 0.4069 | 0.173 | 0.168 |
| position base rate | 0.13805 | 0.4465 | 0.174 | 0.168 |

The direct model wins in **every one of the six test seasons** (2020: .1338 vs .1371 … 2025: .1200 vs .1238).
The gain is calibration, not sharpness: the count families are badly wrong at the ends —
predicted 0.085 vs observed 0.047 in the lowest bin, predicted 0.240 vs observed 0.300 in the 0.2–0.3 bin, and
predicted 0.649 vs observed 0.578 in the 0.6–0.7 bin. The direct model is within ~1 point in every populated bin.

On Kalshi's own 3,369 settled 2025 anytime-TD rungs: direct 0.16777 vs NB 0.17126 vs base rate 0.18345, with
mean prediction 0.223 against an observed 0.240 (the count family said 0.207). A residual under-prediction of
~1.7 points remains — Kalshi lists anytime-TD markets for players with above-average scoring roles, so the
listed population is not the modelled population. Red-zone and goal-line usage features are the registered next
step (H-20260904-009).

Features: log1p EWMA of prior touchdowns, touches, targets and carries; team implied total; home; the
small-sample shrinkage weight; position dummies. All strictly pre-kickoff. Fitted by IRLS with ridge 1.0.
