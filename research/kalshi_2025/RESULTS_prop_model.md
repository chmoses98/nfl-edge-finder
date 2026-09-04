# Distribution models on the exact player-prop rungs Kalshi listed in 2025 (out-of-sample)

`scripts/research/kalshi_2025_prop_eval.py`. Models: the Milestone-F mean model (EWMA + implied total + home, shrunk
priors) and the chosen family per statistic, fitted on 2016–2024 only; evaluated on every settled, archived 2025 Kalshi
rung that joins to a nflverse game and a resolved player id (24,268 rungs joined; 21,362 scored).

| statistic | family | rungs | Brier | Brier (rung base rate) | skill | mean pred | observed YES |
|---|---|---|---|---|---|---|---|
| passing yards | censored normal | 2,757 | 0.1699 | 0.2285 | +0.256 | 0.400 | 0.353 |
| rushing yards | mu-binned empirical | 2,821 | 0.2277 | 0.2473 | +0.079 | 0.419 | 0.448 |
| receiving yards | mu-binned empirical | 8,892 | 0.2198 | 0.2408 | +0.087 | 0.393 | 0.404 |
| receptions | negative binomial | 6,244 | 0.1925 | 0.2459 | +0.217 | 0.418 | 0.436 |
| passing TDs | Poisson | 648 | 0.1527 | 0.2294 | +0.334 | 0.355 | 0.356 |
| anytime TD (1+) | negative binomial | 3,369 | 0.1713 | 0.1822 | +0.060 | 0.207 | 0.240 |

Per-rung calibration highlights (pred / observed): passing yards over-predicts every rung (300+: 0.194 / 0.125;
350+: 0.068 / 0.042) — the 2025 passing-level drift flagged in the study, now confirmed on market rungs; receiving
yards is within 1–3 points from 30+ to 100+; rushing yards under-predicts low rungs (20+: 0.58 / 0.62) —
Kalshi lists rushing ladders for backs whose role just grew, which an EWMA lags (a role/snap-share model fixes this,
see research/role_features); receptions under-predicts 1+..3+ and over-predicts 7+/8+ (0.34 / 0.25).

Reading: positive skill everywhere, but "skill vs the rung's base rate" is a weak bar. Kalshi places rungs around
its own projection, so observed YES rates hover near 0.40–0.45 at the central rungs; the decisive test is against
the *market prices* on those rungs at each horizon, which needs the per-market candlesticks now being backfilled.
Until then the honest statement is: the families are calibrated in shape (receiving yards, passing TDs), the
point projections are not yet competitive (passing level drift, rushing role lag), and no prop edge is claimed.
Anytime-TD contracts (no numeric strike; YES iff ≥ 1 TD) confirm the study's warning: the count family under-predicts
the 1+ rung (0.207 vs 0.240 observed, skill only +0.06). A direct binary model with red-zone role features is required.
