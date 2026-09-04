# Full-universe pricing, week 1 2026 game ladders (shadow, T-5 days)

`scripts/research/price_week1_game_ladders.py`. Every captured full-game rung (winner, spread ladder, total ladder,
team totals, both-teams-score) for the 16 week-1 games was priced from ONE coherent distribution per game
(`nfl_edge/pricing/game_env.py`) and compared with Kalshi's quotes from the first capture (2026-09-04 11:49–11:59 UTC).

Two priors were tried:
1. **nflverse consensus line** (vintage unknown): 6% of liquid rungs deviated by > 5¢ — and the largest "edges" were
   exactly the games where Kalshi had already moved (BUF–HOU: consensus BUF −1.5, Kalshi pick'em; DEN–KC: 3 vs ≈2).
   A stale reference line manufactures fake edge. Lesson recorded.
2. **Kalshi-implied line** by least squares over every liquid winner/spread/total rung: then the coherent distribution
   agrees with the market almost everywhere.

| family (liquid: quote ≤ 5¢, traded) | rungs | mean |model − mid| | mean signed dev | max "edge" vs executable |
|---|---|---|---|---|
| game winner | 32 | 1.1¢ | 0.0¢ | 3.2¢ |
| spread ladder | 347 | 1.6¢ | +0.3¢ | 6.3¢ |
| total ladder | 264 | 1.2¢ | +0.3¢ | 2.9¢ |

Only 0.9% of 643 liquid rungs sit more than 5¢ from the model; 8.1% more than 3¢. The residual deviations cluster on
spread rungs at 3.5–4.5 points (e.g. `KXNFLSPREAD-26SEP10SFLAR-LAR4` quoted 0.49/0.50 vs model 0.56 with an
implied line of 4.5): the market's mass around the key numbers 3–4 differs from the historical residual bank — a
shape question for the ladder calibration study once settled 2025 rungs are backfilled, not an edge claim.
Wide/untraded rungs (216, mostly team totals and both-teams-score): mean deviation 5.7¢, model outside the quoted
[bid, ask] on 8.3% — nothing executable.

Conclusions
* The coherent game-environment pricer reproduces Kalshi's liquid game ladders to ~1–2¢ five days out, so it is a
  sound *scaffold* for pricing derivative markets whose own quotes are 30–60¢ wide (quarters, halves, race-to,
  team totals) and for detecting internal inconsistencies when those tighten.
* Every candidate edge in this exercise is smaller than the taker fee at mid prices (≈1.75¢ at 50¢) except a handful
  of spread rungs near key numbers on thin volume. There is no game-market edge to report.
* The prospective ledger must store both the implied line and the consensus line per snapshot so this comparison can
  be run at every timing window through the season.
