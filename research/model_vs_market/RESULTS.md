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

The research posture this implies is not "find the edge". It is: **the player-prop model is not yet
competitive with the closing line, and the measurable objective is to close a 0.0104 Brier gap.** The
opportunity engine (−2.6 to −3.8% relative) and the tail calibrator (bias removal, Brier flat) are both
steps in that direction and neither is nearly enough on its own.
