# Market-as-prior joint game environment — OOS validation (2016–2025, 2,639 games)

`nfl_edge/pricing/game_env.py`, `scripts/research/game_env_validation.py`. One coherent distribution per game from
the market-implied margin and total: jointly-sampled historical residual pairs (recency half-life 3 seasons; sampled
from games whose lines share the target lines' fractional parts so margins/totals stay integers), regulation ties
resolved with an overtime model (historical tie-given-OT rate, OT margin and points), home/away scores derived by
parity-consistent halving. Every derivative market is priced from the same samples, so winner, spread rungs, total
rungs, team totals, margin buckets and both-teams-score can never contradict each other.

| market | predicted | observed | Brier |
|---|---|---|---|
| home win | 0.544 | 0.545 | 0.2110 |
| tie | 0.002 | 0.004 | 0.0038 |
| home team total ≥ 21 / ≥ 28 / ≥ 35 | 0.613 / 0.340 / 0.142 | 0.606 / 0.324 / 0.133 | 0.215 / 0.199 / 0.109 |
| away team total ≥ 21 / ≥ 28 / ≥ 35 | 0.552 / 0.281 / 0.106 | 0.528 / 0.275 / 0.097 | 0.226 / 0.180 / 0.083 |
| both teams ≥ 21 / ≥ 28 | 0.333 / 0.099 | 0.324 / 0.106 | 0.209 / 0.091 |
| home wins by 1–6 / 7–14 / 15+ | 0.188 / 0.179 / 0.177 | 0.201 / 0.169 / 0.175 | 0.159 / 0.138 / 0.131 |
| away wins by 1–6 / 7–14 / 15+ | 0.176 / 0.155 / 0.124 | 0.197 / 0.136 / 0.119 | 0.156 / 0.115 / 0.095 |

Team-total reliability across 14 rungs and 36,946 rung-games: slope 1.01, intercept −0.01, every decile within 1–2
points of the diagonal. Residual correlation between margin and total is ≈ 0.03, so the joint bank matters mainly for
integer/key-number structure and OT, not for margin–total dependence.

Remaining miscalibration: the 1–6 point margin buckets are under-predicted by ~1.5–2 points of probability and 7–14
slightly over (the OT model puts too much mass on 3/6/7 walk-off margins vs 1–6 late field goals); tails and team totals are
fine. This is the game-environment prior for Milestone G: player simulations condition on samples from it.
