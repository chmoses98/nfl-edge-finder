# Circumstance hypotheses — pre-registered 2026-10-17, BEFORE any circumstance feature was joined to a price or outcome

Question: under which point-in-time circumstances is the Kalshi player-prop price systematically wrong? Projection gaps alone are
never evidence. Each hypothesis is a statement about `y - mid` (outcome minus the contemporaneous midpoint) on the YES side of a
rung, or about the model-minus-market slope inside the circumstance. Unit of evidence = player-stat-game cluster. EV = buy the
indicated side at the ask, after Kalshi fee.

Population: PLAYER_STAT receptions and receiving_yards rungs, valid two-sided quotes (width <= 0.10), latest pre-kickoff quote.
Corpus: 2026 weeks 1-4 are DISCOVERY EVIDENCE ONLY (the model defects were diagnosed on them). A hypothesis is a validated signal
only if its rule, frozen as written below, is positive after fees on 2026 weeks 5+ (untouched; accrues automatically).

Features (all point-in-time, from nflverse stats through the prior game only):
* `trend3` = mean targets in the player's last 3 games minus his EWMA targets (role change)
* `opp_soft` = opponent's trailing-EWMA targets allowed to WR/TE/RB, ranked among teams that week; tercile 3 = softest
* `implied_total`, `spread_team` (closing consensus line, known pregame)

| id | circumstance | prediction | test |
|---|---|---|---|
| C1 | trend3 >= +1.5 (rising role) | market under-prices YES | mean(y - mid) > 0 |
| C2 | trend3 <= -1.5 (falling role) | market over-prices YES | mean(y - mid) < 0 |
| C3 | opp_soft in top tercile | market under-prices YES | mean(y - mid) > 0 |
| C4 | opp_soft in bottom tercile | market over-prices YES | mean(y - mid) < 0 |
| C5 | implied_total >= 26 | market under-prices YES | mean(y - mid) > 0 |
| C6 | spread_team >= +7 (heavy underdog) | market under-prices YES for pass-catchers (volume in catch-up script) | mean(y - mid) > 0 |
| C7 | challenger-minus-market gap >= +0.05 AND C1 | the model's disagreement is informative only when the role change explains it | EV at ask > 0 |

Decision rule: one-sided cluster z; 14 tests (7 x 2 stats) -> Bonferroni alpha 0.05/14 = 0.0036 (z >= 2.69). A hypothesis passing on weeks
1-4 is "DISCOVERY_SUPPORTED", not validated. Fails stay recorded as negatives.
