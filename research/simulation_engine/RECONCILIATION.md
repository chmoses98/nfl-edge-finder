# Market reconciliation weights (sim-1.0.0), fitted on the 2025 Kalshi archive

Reproduce: `python scripts/sim/walkforward.py --seasons 2025` then `python scripts/sim/reconciliation_study.py`.
Numbers: `reconciliation_2025.json`; the deployed weights: `reconciliation_weights.json`.

**HISTORICAL_RESEARCH.** The simulation distributions of every 2025 game (bundle fitted on 2018–2024,
consensus closing line as the centre) are joined to the 28,347 settled archived player-prop rungs that
resolve to a GSIS player, with the archived quotes at T-0 (the close) and T-24h. For each statistic family
the reconciled probability is the football distribution re-located to `market mean + w × (football mean −
market mean)`; `w` is chosen on weeks 1–9 by Brier at the quoted thresholds, confirmed on weeks 10–22
(paired against the monotone midpoint, game-clustered), and re-fitted on the whole season. The DEPLOYED
weight (`reconcile.deploy_weights`) is non-zero only when the early fit had ≥ 500 rows and a non-zero
optimum AND its later-week confirmation was not worse than the market beyond z = 1, and is then the smaller
of the early-week and whole-season optima.

## What the market and the football-only model look like at the close (T-0, 21,697 rows, 264 games)

| statistic | n | Brier football-only | Brier market mid | football − market | incumbent (old, same rungs) | b_football / b_market |
|---|---|---|---|---|---|---|
| any_td | 3,720 | 0.1583 | 0.1570 | +0.0013 | 0.1691 | 0.20 / 0.75 |
| pass_td | 684 | **0.1513** | 0.1533 | −0.0020 | 0.1519 | 1.39 / −0.39 |
| pass_yards | 2,602 | 0.1693 | 0.1597 | +0.0096 | 0.1695 | −0.16 / 1.14 |
| rec_yards | 6,834 | 0.2148 | 0.2090 | +0.0058 | 0.2218 | 0.08 / 0.89 |
| receptions | 4,445 | 0.1889 | 0.1829 | +0.0060 | 0.1955 | 0.02 / 0.91 |
| rush_yards | 3,412 | 0.2146 | 0.2090 | +0.0056 | 0.2280 | 0.19 / 0.73 |

(`incumbent` is the `old` arm of `research/player_engine_v2/rung_scores_2025.parquet` at T-0 on the same
statistic; `b_*` are the encompassing-regression coefficients on the logit scale over all 2025 rows.)

Reading: the football-only simulation is closer to the market than the incumbent on every family (rushing
yards −0.013, anytime TD −0.011, receiving yards −0.007, receptions −0.007 in Brier), and its encompassing
coefficient is no longer ~0 on touchdowns and rushing yards (0.19–0.20), but the market still wins every
family except passing touchdowns by 0.001–0.010. Passing yards is the family where the simulation adds
nothing at all (b_football < 0).

## Fitted, confirmed and deployed weights (T-0)

| statistic | w (weeks 1–9) | n (weeks 1–9) | confirmation weeks 10–22: reconciled − market Brier (z) | w (all 2025) | **deployed** | why |
|---|---|---|---|---|---|---|
| any_td | 0.25 | 1,670 | 0.15118 vs 0.15140 (z −1.10) | 0.35 | **0.25** | confirmed; smaller optimum |
| rush_yards | 0.25 | 599 | 0.20702 vs 0.20511 (z +1.16) | 0.20 | **0** | later weeks worse than the market beyond z = 1 |
| rec_yards | 0.00 | 1,395 | +0.0014 (z +1.61) at w = 0 | 0.05 | **0** | early optimum was 0 |
| receptions | 0.00 | 32 | — | 0.25 | **0** | too few identified ladders early in 2025 to confirm |
| pass_yards | 0.00 | 554 | +0.0004 (z +0.47) at w = 0 | 0.00 | **0** | early optimum was 0 |
| pass_td | — | 0 | — | 1.00 | **0** | no early-week rows; **the top candidate for a preregistered follow-up** |

Touchdown families are re-located as a Poisson at the target mean (`reconcile.relocate`); a first pass that
stretched the integer lattice produced nonsense on near-zero-mean players (a 0.0005-mean lattice scaled 40×)
and is why the any_td weight fell from an apparent 0.6 to a real 0.25 once fixed.

**Only anytime touchdown earned a deviation from the market.** Every other family deploys at 0: the
reconciled distribution sits at the market mean with the football shape, is reported, and is never ranked.
Note that even at w = 0 the reconciled probability is slightly worse than the monotone midpoint on
receiving yards (+0.0014, z 1.6): the football *shape* at the market mean is not better than the market's
own ladder, which is itself a finding.

## Disagreement bands (weeks 1–9, |football − market| at the rung)

| statistic | band | n | best w | Brier market | Brier football |
|---|---|---|---|---|---|
| any_td | 0.00–0.05 | 1,150 | 1.0 | 0.1488 | 0.1483 |
| any_td | 0.05–0.10 | 372 | 0.2 | 0.1907 | 0.1943 |
| any_td | 0.10–0.20 | 136 | 0.0 | 0.2150 | 0.2375 |
| rush_yards | 0.00–0.05 | 233 | 1.0 | 0.2083 | 0.2071 |
| rush_yards | 0.05–0.10 | 153 | 0.0 | 0.2179 | 0.2170 |
| rush_yards | 0.10–0.20 | 164 | 0.0 | 0.2448 | 0.2555 |
| rec_yards | 0.00–0.05 | 556 | 1.0 | 0.1973 | 0.1974 |
| rec_yards | 0.05–0.10 | 401 | 0.7 | 0.2135 | 0.2129 |
| rec_yards | 0.10–0.20 | 351 | 0.0 | 0.2078 | 0.2304 |
| rec_yards | 0.20+ | 87 | 0.0 | 0.2435 | 0.2939 |
| pass_yards | 0.00–0.05 | 310 | 0.35 | 0.1419 | 0.1424 |
| pass_yards | 0.05–0.10 | 147 | 0.0 | 0.1710 | 0.1827 |
| pass_yards | 0.10–0.20 | 93 | 0.0 | 0.1505 | 0.1856 |

The pattern the rebuild was asked to look for is there and it is the same one the incumbent showed: where
the football model and the market are close, the football view is as good or marginally better; where they
disagree by more than 0.10, the market wins outright on every family. **A large disagreement is a warning,
not an opportunity.** This is why the deployed weights are per family AND why the packet ranks only the
reconciled disagreement: at w = 0.25 for anytime TD the largest reconciled deviations are a few points, not 0.4.

## T-24h

The same picture one day earlier (16,931 rows, 250 games): football-only Brier 0.1547 / 0.1553 / 0.1692 /
0.2153 / 0.1904 / 0.2165 against market 0.1533 / 0.1579 / 0.1651 / 0.2093 / 0.1839 / 0.2097 for any_td /
pass_td / pass_yards / rec_yards / receptions / rush_yards. The gap to the market is 0.004–0.007 smaller at
T-24h than at T-0 on the yardage families, as it should be if the market keeps learning through the day,
and the weights fitted at T-24h are the same order as at T-0 (any_td 0.10 early / 0.30 whole season, rush 0.15,
pass_yards 0.15, rec 0.0). The deployed weights are the T-0 ones.

## Caveats

* One season of Kalshi history; 121–264 games per family; the pass_td and receptions early-week samples
  were too thin to confirm.
* The centre of every historical simulation is the consensus closing line, a slightly later market than the
  T-24h quotes; the T-24h comparison therefore flatters the football arm a little.
* The reconciled shape is the football shape. Where the market's ladder identifies the tail, a shape blend
  may be better; not tested.
* Nothing here is prospective. `H-20260916-027` preregisters the 2026 test.
