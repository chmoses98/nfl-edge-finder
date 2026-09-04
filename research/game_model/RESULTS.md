# Game model research v1 (Milestone E) — walk-forward vs the closing line

Script: `scripts/research/game_model_study.py`; ratings: `nfl_edge/research/team_ratings.py`.
Data: nflverse play-by-play 2006–2025 → silver `team_game` (per team-game EPA/play, success rate, dropback/rush EPA,
early-down EPA, explosive rate, sack rate, turnover rate, PROE, special-teams EPA), schedule with consensus closing
spread/total (vintage undocumented). Test seasons 2014–2025 (n = 3,151 regular-season games), training strictly on
prior seasons; ratings at each (season, week) use only games before that week.

## Method
Opponent-adjusted team ratings by weighted ridge regression on prior team-games (`y = off_team + def_opp + hfa`),
recency half-life 10 weeks, prior seasons discounted ×0.4/season, ridge shrinkage toward the league mean
(hyper-parameters chosen on 2011–2013 only; a bug measuring recency in league-wide game index instead of weeks was
found and fixed — the first run's RMSE of 14.1 was that bug). Margin and total models: standardized ridge on
matchup differences (11 rating features + rest diff + divisional + neutral site), λ chosen on ≤2015 nested folds.
Market-aware residual model: `result − spread ~ same features + spread`.

## Results (pooled 2014–2025)
| predictor | margin RMSE | margin MAE | win log-loss | win Brier |
|---|---|---|---|---|
| closing spread | **12.88** | **9.95** | **0.612** | **0.212** |
| football-only model | 13.26 | 10.31 | 0.634 | 0.222 |
| market residual model (spread + features) | 12.92 | — | 0.613 | 0.213 |
| 30/70 model/market blend | 12.91 | — | 0.615 | 0.213 |

Totals: closing total RMSE 13.18 vs model 13.52 vs residual 13.24.
Optimal blend weight on the model is 0.0 (RMSE rises monotonically with model weight). Encompassing regression
`result ~ spread + model` gives coefficients 1.01 on spread and 0.03 on the model. Model-vs-spread "ATS" hit rate
when the model disagrees by >3 points: 50.0% (n = 928, 95% CI 46.8–53.2%). Early-season (weeks 1–4) model RMSE
13.45 vs spread 13.18; the model is not closer to the line early either. Correlation between model margin and spread: 0.81–0.89 by season.

## Conclusion (honest)
A team-level EPA rating model of this kind carries **no information beyond the closing line** for full-game
spreads and totals, in any season, early or late. This is the expected NFL result and it sets the bar: any claim of
edge must come from (a) earlier-in-week prices (Kalshi opens vs close, now being captured), (b) player-level and
derivative markets where our simulation of the full distribution can be sharper than a thin ladder, (c) information
shocks (QB/OL/WR availability, weather) that reprice with lag, or (d) Kalshi-internal inconsistencies. It also means
the closing line is the right *prior* for the game environment in the joint simulation; a market-aware model
(MODEL B) is the default for game-level inputs.

## Next steps recorded in the hypothesis registry
QB-change feature (schedule has starting QB ids), rest/travel/international, weather from forecast vintages,
ladder-level (alternate spread/total) calibration against the normal/empirical margin distribution, and — most
importantly — the same test against **Kalshi prices at T-48h/T-24h** once enough prospective snapshots exist.
