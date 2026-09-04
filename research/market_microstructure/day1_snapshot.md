# Kalshi NFL microstructure snapshot — 2026-09-04 (T-5 days before week 1)

Source: first prospective capture run (12,408 quoted markets; single-game markets with a two-sided quote shown). Spread = yes_ask − yes_bid in dollars.

| family | period | two-sided markets | median spread | share ever traded | median volume | total volume |
|---|---|---|---|---|---|---|
| PLAYER_STAT | FULL | 424 | 0.055 | 0.76 | 56.0 | 248012 |
| SPREAD | FULL | 404 | 0.020 | 0.99 | 922.9 | 1247885 |
| TOTAL | FULL | 304 | 0.030 | 0.91 | 274.0 | 578125 |
| SPREAD | 1H | 249 | 0.340 | 0.06 | 0.0 | 1153 |
| SPREAD | 2H | 249 | 0.670 | 0.00 | 0.0 | 0 |
| TOTAL | 1H | 217 | 0.050 | 0.42 | 0.0 | 12426 |
| TOTAL | 2H | 217 | 0.590 | 0.01 | 0.0 | 500 |
| RACE_TO_N | FULL | 216 | 0.520 | 0.02 | 0.0 | 10 |
| SPREAD | 3Q | 173 | 0.510 | 0.08 | 0.0 | 202 |
| SPREAD | 1Q | 172 | 0.370 | 0.01 | 0.0 | 56 |
| SPREAD | 2Q | 170 | 0.510 | 0.01 | 0.0 | 2 |
| SPREAD | 4Q | 170 | 0.510 | 0.04 | 0.0 | 85 |
| TOTAL | 1Q | 160 | 0.370 | 0.18 | 0.0 | 549 |
| TOTAL | 2Q | 160 | 0.460 | 0.01 | 0.0 | 67 |
| TOTAL | 3Q | 160 | 0.420 | 0.06 | 0.0 | 93 |
| TOTAL | 4Q | 160 | 0.555 | 0.00 | 0.0 | 0 |
| TOTAL_TD | FULL | 96 | 0.470 | 0.00 | 0.0 | 0 |
| WIN_MARGIN_BUCKET | FULL | 94 | 0.365 | 0.24 | 0.0 | 1063 |
| GAME_WINNER | FULL | 64 | 0.020 | 1.00 | 10608.9 | 2968852 |
| HALF_FULL_RESULT | 1H | 60 | 0.395 | 0.03 | 0.0 | 23 |
| BOTH_TEAMS_SCORE_N | FULL | 58 | 0.560 | 0.05 | 0.0 | 12 |
| PERIOD_WINNER | 1H | 48 | 0.380 | 0.60 | 5.8 | 12436 |
| PERIOD_WINNER | 1Q | 48 | 0.310 | 0.50 | 0.5 | 1154 |
| PERIOD_WINNER | 2H | 48 | 0.430 | 0.52 | 1.5 | 3740 |
| PERIOD_WINNER | 2Q | 48 | 0.350 | 0.27 | 0.0 | 342 |
| PERIOD_WINNER | 3Q | 48 | 0.310 | 0.31 | 0.0 | 501 |
| PERIOD_WINNER | 4Q | 48 | 0.360 | 0.35 | 0.0 | 289 |
| GAME_EVENT | FULL | 48 | 0.410 | 0.10 | 0.0 | 156 |
| TEAM_TOTAL | FULL | 43 | 0.090 | 0.05 | 0.0 | 108 |
| FIRST_TD_TEAM | FULL | 32 | 0.435 | 0.28 | 0.0 | 103 |
| FIRST_TD_SCORER | FULL | 25 | 0.010 | 0.96 | 507.9 | 29185 |
| BOTH_TEAMS_SCORE | 1Q | 16 | 0.620 | 0.06 | 0.0 | 11 |
| BOTH_TEAMS_SCORE | 2Q | 16 | 0.610 | 0.00 | 0.0 | 0 |
| BOTH_TEAMS_SCORE | 3Q | 16 | 0.620 | 0.00 | 0.0 | 0 |
| BOTH_TEAMS_SCORE | 4Q | 16 | 0.610 | 0.00 | 0.0 | 0 |
| SEASON_LEADER | - | 2 | 0.920 | 0.00 | 0.0 | 0 |

Ladder consistency: 405 ladders checked (spread/total/team-total/player/total-TD). **No crossed ladders** (no harder rung bid above an easier rung's ask, i.e. no locked arbitrage). Mid-price non-monotonicity: {'SPREAD/1H/mid_nonmonotone': 1, 'TOTAL/1H/mid_nonmonotone': 13, 'SPREAD/1Q/mid_nonmonotone': 8, 'TOTAL/1Q/mid_nonmonotone': 1, 'TOTAL/2Q/mid_nonmonotone': 4, 'SPREAD/3Q/mid_nonmonotone': 1, 'TOTAL/3Q/mid_nonmonotone': 2, 'SPREAD/4Q/mid_nonmonotone': 7, 'TOTAL/4Q/mid_nonmonotone': 1, 'PLAYER_STAT/FULL/mid_nonmonotone': 31, 'TEAM_TOTAL/FULL/mid_nonmonotone': 4} — all inside wide, untraded quotes, i.e. noise in resting orders rather than exploitable mispricing.

Reading: five days out, Kalshi is a two-tier venue. Full-game winner/spread/total are tight (2–3¢) and universally traded (volume in the $10k–$370k range per market). Player-prop ladders are quoted at ~5–6¢ with three quarters already traded. Everything derivative (quarters, halves, race-to, both-teams-score, total TDs, half/full) is 30–65¢ wide and essentially untraded: those families cannot be evaluated for edge until they tighten near kickoff, and any 'edge' measured against a 50¢-wide quote is fiction. This snapshot is the baseline for the market-efficiency map; the same table will be recomputed at T-24h, T-6h, T-1h and close.
