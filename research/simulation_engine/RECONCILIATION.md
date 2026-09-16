# Market reconciliation weights (sim-1.0.0), fitted on the 2025 Kalshi archive

Reproduce: `python scripts/sim/walkforward.py --seasons 2025` then `python scripts/sim/reconciliation_study.py`.  Generated from `reconciliation_2025.json` and `reconciliation_weights.json` by `scripts/sim/write_results.py` -- do not edit by hand.

**HISTORICAL_RESEARCH.** The simulation distributions of every 2025 game (bundle and shrinkage priors both fitted on seasons <= 2024) are joined to the 28347 settled archived player-prop rungs that resolve to a GSIS player, with the archived quotes at the close.  The reconciled probability is the football distribution re-located to `market mean + w x (football mean - market mean)`; `w` is chosen on weeks 1-9 by Brier at the quoted thresholds, confirmed on weeks 10-22 (paired against the monotone midpoint, game-clustered), and re-fitted on the whole season. The DEPLOYED weight (`reconcile.deploy_weights`) is non-zero only when the early fit had >= 500 rows and a non-zero optimum AND its later-week confirmation was not worse than the market beyond z = 1, and is then the smaller of the early-week and whole-season optima.

Only the close is evidence: `PIT_EVIDENCE` -- the simulation centre is the consensus CLOSING line, so this comparison is like-for-like

## Football-only against the market at the close (21697 rows, 264 games)

| statistic | n | Brier football-only | Brier market mid | football − market | mean football / market / rate | b_football / b_market |
|---|---|---|---|---|---|---|
| any_td | 3720 | 0.1583 | 0.1570 | 0.0013 | 0.212 / 0.230 / 0.226 | 0.19 / 0.76 |
| pass_td | 684 | 0.1512 | 0.1533 | -0.0021 | 0.349 / 0.363 / 0.357 | 1.39 / -0.39 |
| pass_yards | 2602 | 0.1692 | 0.1597 | 0.0095 | 0.338 / 0.353 / 0.343 | -0.16 / 1.14 |
| rec_yards | 6834 | 0.2149 | 0.2090 | 0.0059 | 0.382 / 0.430 / 0.404 | 0.07 / 0.90 |
| receptions | 4445 | 0.1889 | 0.1829 | 0.0060 | 0.383 / 0.424 / 0.385 | 0.02 / 0.91 |
| rush_yards | 3412 | 0.2145 | 0.2090 | 0.0054 | 0.382 / 0.431 / 0.414 | 0.21 / 0.72 |

## Fitted, confirmed and deployed weights

| statistic | w (weeks 1-9) | n (weeks 1-9) | confirm weeks 10-22: reconciled vs market Brier (z) | w (all 2025) | **deployed** | why |
|---|---|---|---|---|---|---|
| any_td | 0.25 | 1670 | 0.15121 vs 0.15140 (z -0.99) | 0.35 | **0.25** | early-week fit confirmed on later weeks; smaller of the two optima |
| pass_td | — | — | — | 1.00 | **0.00** | no early-week fit with enough rows to confirm |
| pass_yards | 0.00 | 554 | 0.16301 vs 0.16203 (z 1.13) | 0.00 | **0.00** | early-week optimum was 0 |
| rec_yards | 0.00 | 1395 | 0.21079 vs 0.20936 (z 1.63) | 0.05 | **0.00** | early-week optimum was 0 |
| receptions | 0.00 | 32 | 0.18465 vs 0.18286 (z 1.60) | 0.15 | **0.00** | no early-week fit with enough rows to confirm |
| rush_yards | 0.25 | 599 | 0.20668 vs 0.20511 (z 0.93) | 0.20 | **0.00** | later-week confirmation point estimate is worse than the market (+0.00157 Brier, z=+0.93); inside the z gate but pointing the wrong way, so no deviation is earned |

**Families with a non-zero deployed weight: any_td = 0.25.**
Every other family deploys at 0: the reconciled distribution sits at the market mean with the football shape, is reported on the board, and is never ranked.

Touchdown families are re-located as a Poisson at the target mean and yardage families keep the football shape unless the target is more than 4x away, where the market's own two-parameter family is used instead (`reconcile.relocate`); a lattice with a 0.0005 mean cannot be stretched 40x.

## Disagreement bands (weeks 1-9, |football − market| at the rung)

| statistic | band | n | best w | Brier market | Brier football |
|---|---|---|---|---|---|
| any_td | 0.00-0.05 | 1144 | 1.00 | 0.1495 | 0.1490 |
| any_td | 0.05-0.10 | 380 | 0.10 | 0.1900 | 0.1945 |
| any_td | 0.10-0.20 | 133 | 0.00 | 0.2097 | 0.2283 |
| pass_yards | 0.00-0.05 | 312 | 0.25 | 0.1406 | 0.1420 |
| pass_yards | 0.05-0.10 | 143 | 0.00 | 0.1752 | 0.1871 |
| pass_yards | 0.10-0.20 | 94 | 0.00 | 0.1510 | 0.1802 |
| rec_yards | 0.00-0.05 | 568 | 1.00 | 0.1959 | 0.1957 |
| rec_yards | 0.05-0.10 | 397 | 0.50 | 0.2153 | 0.2161 |
| rec_yards | 0.10-0.20 | 344 | 0.00 | 0.2068 | 0.2294 |
| rec_yards | 0.20-1.01 | 86 | 0.00 | 0.2504 | 0.2952 |
| rush_yards | 0.00-0.05 | 233 | 1.00 | 0.2108 | 0.2103 |
| rush_yards | 0.05-0.10 | 149 | 0.10 | 0.2163 | 0.2159 |
| rush_yards | 0.10-0.20 | 164 | 0.00 | 0.2408 | 0.2535 |
| rush_yards | 0.20-1.01 | 53 | 0.80 | 0.2902 | 0.2441 |

Where the football model and the market are close the football view is as good or marginally better; where they disagree by more than 0.10 the market wins on every family.  **A large disagreement is a warning, not an opportunity** -- which is why the packet ranks only the reconciled disagreement, and only where a weight was earned.

## T-24h -- NON_PIT_DESCRIPTIVE

NOT point-in-time: the simulation centre is the consensus CLOSING line and the eligibility inputs are the week's final injury report and a weekly depth chart, none of which is a T-24h vintage. Descriptive only; cannot fit or promote a weight.

| statistic | n | Brier football-only | Brier market mid |
|---|---|---|---|
| any_td | 2894 | 0.1548 | 0.1533 |
| pass_td | 651 | 0.1553 | 0.1579 |
| pass_yards | 2143 | 0.1691 | 0.1651 |
| rec_yards | 5294 | 0.2154 | 0.2093 |
| receptions | 3384 | 0.1904 | 0.1839 |
| rush_yards | 2565 | 0.2164 | 0.2097 |

## Caveats

* One season of Kalshi history; the early-week samples for some families are thin, which is why the deployment rule requires a minimum row count rather than trusting a small optimum.
* The reconciled shape is the football shape.  Where the market's ladder identifies the tail a shape blend may be better; not tested.
* The market's dispersion prior for UNDERIDENTIFIED ladders is the incumbent's frozen 2025 constant (`engines/player/market_dist.DISPERSION_PRIOR`); underidentified ladders are excluded from fitting.
* Nothing here is prospective.  `H-20260916-027` preregisters the 2026 test.

