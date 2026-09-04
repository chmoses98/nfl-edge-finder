# Model versus the Kalshi closing price, on the same settled contracts

Reproduce: `python3 scripts/research/model_vs_market_2025.py '<horizons glob>'`

Everything else in this repository compares the model to the market *prospectively* (no outcomes yet), or
the market to outcomes (no model). This joins the two. For every 2025 player-prop contract where a
walk-forward model probability and a reconstructed closing quote both exist, both are scored against what
actually happened — and then the only question that matters is asked: what would acting on the disagreement
have paid?

**18,412 matched contracts across 254 games** at full backfill coverage, restricted to books quoted within 10 cents. (An earlier version of this file reported 12,553 contracts over 190 games at 54% coverage; every figure below moved by less than the third decimal.)

## The market wins, and it wins everywhere

| | Brier | log loss | mean probability |
|---|---|---|---|
| model | 0.19943 | 0.58343 | 0.3685 |
| **market (closing mid)** | **0.18948** | **0.55762** | 0.3914 |
| realised | | | 0.3718 |

Brier difference, model minus market, clustered on game: **+0.00994 ± 0.00163** — the market is better by 6.1
standard errors. The model's *mean* probability (0.3685) is closer to the realised base rate (0.3718) than
the market's (0.3914), and it is still worse contract by contract: the model has the better unconditional
average and less discrimination, which is exactly what being encompassed looks like.

Per statistic, the market is better on every one:

| statistic | n | games | model Brier | market Brier | difference | z |
|---|---|---|---|---|---|---|
| receptions | 3970 | 128 | 0.19553 | 0.18333 | +0.01219 ± 0.00352 | 3.5 |
| receiving_yards | 6305 | 176 | 0.22168 | 0.20977 | +0.01191 ± 0.00235 | 5.1 |
| passing_yards | 2361 | 177 | 0.16974 | 0.16040 | +0.00934 ± 0.00293 | 3.2 |
| rushing_yards | 2253 | 167 | 0.22799 | 0.21998 | +0.00801 ± 0.00490 | 1.6 |
| anytime_td | 2923 | 253 | 0.16845 | 0.16176 | +0.00669 ± 0.00145 | 4.6 |
| passing_tds | 600 | 91 | 0.15185 | 0.15206 | −0.00021 ± 0.00197 | −0.1 |

The single exception is passing touchdowns, and it is a tie on 504 contracts, not a win.

## Acting on the disagreement loses money, and loses more the more it is filtered

| required edge | trades | games | net per contract after fees | z |
|---|---|---|---|---|
| > 0.00 | 12129 | 253 | −0.0314 ± 0.0081 | −3.9 |
| > 0.02 | 9493 | 253 | −0.0312 ± 0.0093 | −3.3 |
| > 0.05 | 6195 | 250 | −0.0321 ± 0.0112 | −2.9 |
| > 0.10 | 2985 | 237 | −0.0348 ± 0.0167 | −2.1 |
| > 0.15 | 1410 | 199 | −0.0308 ± 0.0248 | −1.2 |

Every threshold loses, at roughly the cost of crossing the spread, and demanding more disagreement never
helps. (At 54% coverage the losses appeared to *worsen* monotonically with the threshold, from −0.032 to
−0.050; at full coverage they are flat at about −0.031 to −0.035. The stronger reading was a small-sample
artefact — the conclusion that filtering harder buys nothing is unchanged, the claim that it actively hurts
is not supported.)

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
| base | −0.1217 ± 0.0505 | **+0.0000 ± 0.0763 (z = +0.00)** | **+0.9441 ± 0.0717 (z = +13.2)** |
| role features | −0.1220 ± 0.0474 | **−0.0031 ± 0.0737 (z = −0.04)** | **+0.9467 ± 0.0708 (z = +13.4)** |
| opponent defence | −0.1200 ± 0.0517 | **+0.0073 ± 0.0769 (z = +0.10)** | **+0.9378 ± 0.0722 (z = +13.0)** |

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

## Opponent defence: the most obvious missing feature, and it changes nothing

The player mean model had **no opponent term at all** — it projected a receiver from his own history and the
game's implied total, blind to whether he faced the best or worst coverage in the league. That is a real gap
and the most obvious candidate for information the price might not contain, so it was built and tested:
point-in-time EWMAs of what each defence has allowed (receptions, receiving and rushing yards, targets,
carries, passing yards and touchdowns, plus yards per target and per carry), constructed exactly like the
role features and with the same leakage discipline.

| model arm | standalone Brier | model coefficient | market coefficient | blend − market |
|---|---|---|---|---|
| base | 0.19977 | −0.0243 ± 0.0901 | +0.9683 ± 0.0836 | −0.00044 ± 0.00048 |
| + role features | 0.20123 | −0.0299 ± 0.0843 | +0.9731 ± 0.0814 | −0.00042 ± 0.00044 |
| **+ opponent defence** | **0.19891** | **−0.0067 ± 0.0908** | +0.9534 ± 0.0840 | −0.00042 ± 0.00048 |
| + both | 0.20012 | −0.0145 ± 0.0849 | +0.9601 ± 0.0816 | −0.00038 ± 0.00044 |

Opponent defence produces the **best standalone model of the four** (Brier 0.19891, better than base by
0.00086) — and moves the encompassing coefficient *closer to zero*, not away from it. The market coefficient
stays at 0.95–0.97 throughout, and no blend beats the price.

The reading is straightforward: opponent strength is among the first things any participant prices, so a
feature that genuinely improves the model in isolation is exactly the feature the market already has. This
eliminates the most obvious candidate on the list, and it should recalibrate expectations for the rest of
it — "the model is missing something obvious" is not the explanation for a 0.0104 Brier gap.

## Caveats

* These model probabilities come from `research/kalshi_2025`, fitted walk-forward on seasons before 2025 but
  **predating this session's role features**. Those improved ladder Brier by 2.6–3.8% in relative terms
  (`research/ladder_role`); the gap here is 5.5% relative. Role features would likely close part of it and
  are unlikely on that arithmetic to close all of it. Re-running this head-to-head with `shadow-0.3.0`
  probabilities is the obvious next step and is not done here.
* 254 games, one season. The horizon backfill is now essentially complete (52,491 of 54,364 markets).
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

What would actually count: information the market demonstrably lacks. Opponent defence has now been tried
and eliminated — it improves the model standalone and adds nothing to the price. What remains untested is
in-week news the price incorporates slowly (which requires the 2026 capture stream, since it cannot be
reconstructed from settled archives) and correlated-outcome structure within a game. Until the model
coefficient in the encompassing regression is distinguishable from zero, no selection rule built on
model-market disagreement can be expected to do anything but pay the spread.
