# Model versus the Kalshi closing price, on the same settled contracts

Reproduce: `python3 scripts/research/model_vs_market_2025.py '<horizons glob>'`

Everything else in this repository compares the model to the market *prospectively* (no outcomes yet), or
the market to outcomes (no model). This joins the two. For every 2025 player-prop contract where a
walk-forward model probability and a reconstructed closing quote both exist, both are scored against what
actually happened — and then the only question that matters is asked: what would acting on the disagreement
have paid?

**12,553 matched contracts across 190 games**, restricted to books quoted within 10 cents.

## The market wins, and it wins everywhere

| | Brier | log loss | mean probability |
|---|---|---|---|
| model | 0.20035 | 0.58555 | 0.3773 |
| **market (closing mid)** | **0.18996** | **0.55827** | 0.3974 |
| realised | | | 0.3770 |

Brier difference, model minus market, clustered on game: **+0.01040 ± 0.00197** — the market is better by 5.3
standard errors. Note the model's *mean* probability (0.3773) is almost exactly the realised base rate
(0.3770) while the market's is higher (0.3974): the model has the better unconditional average and is still
worse contract by contract, which is what being less discriminating looks like.

Per statistic, the market is better on every one:

| statistic | n | games | model Brier | market Brier | difference | z |
|---|---|---|---|---|---|---|
| receiving_yards | 4309 | 171 | 0.22381 | 0.21129 | +0.01251 ± 0.00279 | 4.5 |
| receptions | 3165 | 124 | 0.19624 | 0.18385 | +0.01239 ± 0.00384 | 3.2 |
| passing_yards | 1573 | 174 | 0.17139 | 0.16202 | +0.00936 ± 0.00336 | 2.8 |
| rushing_yards | 1545 | 154 | 0.22443 | 0.21617 | +0.00825 ± 0.00520 | 1.6 |
| anytime_td | 1457 | 188 | 0.16289 | 0.15579 | +0.00710 ± 0.00184 | 3.9 |
| passing_tds | 504 | 91 | 0.15058 | 0.15146 | −0.00088 ± 0.00208 | −0.4 |

The single exception is passing touchdowns, and it is a tie on 504 contracts, not a win.

## Acting on the disagreement loses money, and loses more the more it is filtered

| required edge | trades | games | net per contract after fees | z |
|---|---|---|---|---|
| > 0.00 | 8219 | 189 | −0.0323 ± 0.0098 | −3.3 |
| > 0.02 | 6443 | 188 | −0.0304 ± 0.0114 | −2.7 |
| > 0.05 | 4182 | 185 | −0.0369 ± 0.0133 | −2.8 |
| > 0.10 | 2005 | 168 | −0.0463 ± 0.0202 | −2.3 |
| > 0.15 | 947 | 143 | −0.0501 ± 0.0302 | −1.7 |

**The losses get worse as the edge filter tightens.** That is the diagnostic signature of a model whose
largest disagreements are its largest errors. A model with genuine edge shows the opposite: returns improve
as you demand more disagreement. This one degrades monotonically from −0.032 to −0.050 as the threshold rises
from 0 to 0.15.

## What this settles

`H-20260904-011` asked whether the shadow model's persistent ~0.019 gap below the market on player props is
market juice or model bias. On this evidence it is **substantially model bias**. The market's price is a
better estimate of the outcome than the model's on every statistic, and trading the difference loses.

It also refutes a suggestion made earlier in this session — that the model looked better calibrated than the
market for props above 0.35. That comparison put the model's calibration (measured on all player-games,
2019–2025) beside the market's (measured on Kalshi-listed 2025 contracts): two different populations and two
different rung sets. A proper head-to-head on identical contracts reverses it.

Note that the 2025 market being overpriced on the YES side (`research/efficiency_map`, H-017) and the market
still beating the model are **both true and not in tension**. The closing price is biased *and* more
informative than what this platform currently produces. Removing a known bias from a price does not help if
your own estimate is noisier than the biased price.

## The market encompasses the model entirely

Losing to the market leaves one question that decides what to do about it: is the model *redundant*, or does
it carry orthogonal information a market-anchored combination could use? The standard test regresses the
settled outcome on both forecasts in logit space, fitted by IRLS with cluster-robust standard errors:

`logit P(y = 1) = a + b₁ · logit(model) + b₂ · logit(market)`

| arm | intercept | model coefficient b₁ | market coefficient b₂ |
|---|---|---|---|
| base | −0.1280 ± 0.0563 | **−0.0243 ± 0.0901 (z = −0.3)** | **+0.9683 ± 0.0836 (z = +11.6)** |
| role features | −0.1261 ± 0.0533 | **−0.0299 ± 0.0843 (z = −0.4)** | **+0.9731 ± 0.0814 (z = +12.0)** |

A market coefficient of essentially **1.0** with a model coefficient of essentially **0** is the textbook
signature of one forecast encompassing another. **The model contributes nothing the price does not already
contain**, and this holds identically with and without the role features.

The walk-forward blend confirms it. Fitting the combination weights on strictly earlier weeks and scoring on
later ones:

| arm | n | model | market | blend | blend − market |
|---|---|---|---|---|---|
| base | 11,529 | 0.19977 | 0.18945 | 0.18901 | −0.00044 ± 0.00048 (z = −0.9) |
| role | 11,529 | 0.20123 | 0.18945 | 0.18903 | −0.00042 ± 0.00044 (z = −1.0) |

The blend is not distinguishable from simply using the market price. There is no combination to be had.

One detail worth noting: the intercept is significantly negative (−0.128 ± 0.056, z = −2.3) while the market
slope is ≈1. In logit space at p ≈ 0.4 that is a shift of roughly −0.03 in probability — which independently
recovers the YES-side overpricing measured directly in `research/efficiency_map` (−0.028 to −0.049 across
buckets). The regression finds the market's bias without being told to look for it, and finds no model
signal in the same breath.

## Caveats

* These model probabilities come from `research/kalshi_2025`, fitted walk-forward on seasons before 2025 but
  **predating this session's role features**. Those improved ladder Brier by 2.6–3.8% in relative terms
  (`research/ladder_role`); the gap here is 5.5% relative. Role features would likely close part of it and
  are unlikely on that arithmetic to close all of it. Re-running this head-to-head with `shadow-0.3.0`
  probabilities is the obvious next step and is not done here.
* 190 games, one season, and the horizon backfill is still incomplete.
* Restricted to tradable books, which is correct for the calibration comparison and means the result does not
  describe the wide-book segment at all.

## What follows

The research posture this implies is not "find the edge". It is: **the player-prop model is not merely
behind the closing line, it is redundant to it**, and the measurable objective is to close a 0.0104 Brier gap
with information the price does not already contain.

Two candidate steps from this session both fail that bar. The opportunity engine improves the broad
population by 2.6–3.8% relative but is worth ~0 on Kalshi-listed players and slightly negative on Kalshi's
own rungs (`research/ladder_role`). The tail calibrator removes 75–80% of the long-shot bias with aggregate
Brier flat. Neither moves the encompassing coefficient off zero.

What would actually count: information the market demonstrably lacks. Candidates not yet tried here are
in-week news the price incorporates slowly, opponent-adjusted role projection, and correlated-outcome
structure within a game. Until the model coefficient in the encompassing regression is distinguishable from
zero, no selection rule built on model-market disagreement can be expected to do anything but pay the spread.
