# The market-implied distribution as the prior, and where we actually disagree with it

Reproduce: `python3 scripts/research/market_prior_study.py --horizon T-0`

Session 2 established that at the 2025 close the independent football model is redundant to the Kalshi price
(encompassing coefficient −0.0007 ± 0.0756). So the useful question is no longer "what is our projection?" but
"what distribution is the market quoting, and do we have any justified reason to move it?"

`nfl_edge/pricing/market_prior.py` fits each quoted ladder to a Weibull, S(k) = exp(−(k/λ)^γ), by weighted
regression of log(−log S) on log k, with rungs weighted by 1/width so a tight quote is not dragged by a wide
one beside it. It keeps four surfaces strictly separate — **executable YES ask**, **executable NO ask**,
**midpoint** (a research construct, never a fair value) and **fitted latent** (a research object only). The
economic benchmark is always the executable book.

Validated on synthetic ladders: a ladder generated from λ=60, γ=1.4 recovers λ=60.00, γ=1.400, RMSE 0.0000;
a model differing only in location attributes 100% of the disagreement to location, and one differing only in
shape attributes 100% to shape.

## What the market is quoting (2025 close, 9,653 ladders, tradable rungs only)

| statistic | ladders | λ | γ | implied mean | implied sd | fit RMSE | curvature |
|---|---|---|---|---|---|---|---|
| receiving_yards | 1189 | 41.68 | 1.422 | 38.10 | 26.97 | 0.0072 | +0.084 |
| receptions | 931 | 4.17 | 2.186 | 3.69 | 1.79 | 0.0047 | −0.091 |
| rushing_yards | 576 | 48.08 | 1.788 | 42.72 | 25.38 | 0.0067 | −0.034 |
| passing_yards | 321 | 249.11 | 3.560 | 224.18 | 68.47 | 0.0223 | **−1.558** |
| passing_tds | 165 | 2.24 | 1.970 | 1.99 | 1.06 | 0.0062 | +0.029 |

A Weibull describes the quoted ladders well (RMSE 0.005–0.007) for every statistic **except passing yards**,
where the fit is three times worse and the curvature term is large and negative. Passing-yard ladders are not
Weibull-shaped: the market quotes them far more concentrated (γ = 3.56) and with real curvature away from the
family. That is a property of the market's own surface, recorded here because it is where a shape-based claim
would be hardest to distinguish from a fitting artefact.

## Why we disagree — 64% of it is about the mean

Decomposing our model's disagreement across 2,748 ladders where a model curve exists on the same rungs:

| component | share of total disagreement | mean per ladder |
|---|---|---|
| **location** | **64.1%** | +0.2841 |
| shape | 26.3% | +0.1164 |
| residual | 9.6% | +0.0426 |

**Nearly two-thirds of our disagreement with the market is a dispute about the mean** — which is precisely the
quantity the market is demonstrably better at estimating. Only 9.6% is rung-level residual that no
location-or-shape move explains, and that residual is the only part where a localised distortion could live.

By statistic:

| statistic | ladders | location | shape | residual | model mean | market mean |
|---|---|---|---|---|---|---|
| receptions | 835 | 67.6% | 27.4% | 5.0% | 3.63 | 3.88 |
| rushing_yards | 384 | 66.8% | 27.0% | 6.2% | 54.28 | 55.02 |
| passing_yards | 294 | 64.5% | 5.7% | **29.8%** | 231.35 | 221.28 |
| receiving_yards | 1091 | 61.6% | 30.5% | 7.9% | 40.39 | 40.57 |
| **passing_tds** | 144 | **24.3%** | **57.4%** | 18.3% | 1.97 | 1.99 |

Two exceptions stand out and both are recorded rather than pursued:

* **passing_tds** is the one statistic where our disagreement is *not* mostly about location — model mean 1.97
  against market 1.99, essentially identical, with 57.4% of the gap in tail shape. If any shape-based claim
  survives scrutiny it should surface here first.
* **passing_yards** carries the largest residual (29.8%), but the market's own ladder is the worst Weibull fit
  of the five, so residual and mis-specification are confounded there. It is not evidence of distortion.

## What this changes

It reframes the disagreement signal. When the pricer reports "model 47%, market 40%", roughly two-thirds of
that gap is a claim about the mean on which the market has already beaten us at 6.2 standard errors. Ranking
contracts by raw disagreement therefore ranks mostly by our own location error. Any future selection rule
should be built on the residual and shape components, not on the total — and those are 10% and 26% of a signal
that was already worth nothing gross of costs.
