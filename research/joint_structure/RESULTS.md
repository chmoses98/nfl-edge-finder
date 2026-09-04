# Does the market price within-game dependence?

Reproduce: `python3 scripts/research/joint_structure.py '<horizons glob>'`

Kalshi prices each contract on its own. Outcomes inside a game are not independent — a quarterback's big day
lifts his receivers, a blowout suppresses the loser's rushing and inflates its passing. Since the exchange's
*marginals* beat the model outright and encompass it entirely (`research/model_vs_market`), the joint
structure is the one place left where a model could hold information a market of single-contract quotes does
not: no single quote has to encode a correlation.

**202 games, 399,558 cross-player contract pairs**, tradable books only (≤ 10 cents), legs restricted to
0.05 < mid < 0.95 because near-certain legs carry no information about dependence. Pairs on the same player's
own ladder are excluded — those are mechanically dependent and say nothing about the market.

## The confound that had to be removed first

The naive test compares the realised joint rate with the product of the two quoted midpoints. Run that way it
reports:

| pair type | implied | realised | excess | z |
|---|---|---|---|---|
| same team | 0.1578 | 0.1465 | −0.0113 ± 0.0074 | −1.5 |
| opposing teams | 0.1575 | 0.1390 | −0.0186 ± 0.0075 | **−2.5** |

which looks like significant *negative* dependence going unpriced. It is not. The marginals are already known
to be overpriced on the YES side by 1.5–4.9 points (`research/efficiency_map`), and multiplying two
overpriced legs produces a product that is overpriced roughly twice over. That test measures the marginal
bias a second time and mislabels it as dependence.

Each leg is therefore debiased to its own realised rate by price bucket first. That calibration map is itself
a third independent confirmation of the YES-side overpricing:

| quoted midpoint | n | mid | realised |
|---|---|---|---|
| 0.25–0.35 | 2134 | 0.2957 | 0.2793 |
| 0.35–0.45 | 1896 | 0.3994 | 0.3761 |
| 0.45–0.55 | 2135 | 0.5000 | 0.4651 |
| 0.55–0.65 | 1464 | 0.5950 | 0.5335 |
| 0.65–0.75 | 1199 | 0.6950 | 0.6522 |
| 0.75–0.85 | 853 | 0.7939 | 0.7597 |

Monotone overpricing above about 0.25, matching the efficiency map and the encompassing regression's negative
intercept.

## Result: no detectable unpriced dependence

With debiased legs:

| pair type | pairs | games | implied | realised | excess | z |
|---|---|---|---|---|---|---|
| same team | 187,538 | 197 | 0.1399 | 0.1465 | **+0.0065 ± 0.0074** | 0.9 |
| opposing teams | 212,020 | 199 | 0.1398 | 0.1390 | **−0.0008 ± 0.0075** | −0.1 |

The entire apparent effect was the marginal confound. Same-team pairs point the right way — teammates do
co-occur more often than independence implies, which is what the football says — but at 0.9 standard errors
it is not a finding. Opposing-team pairs are essentially exactly independent once the marginals are right.

**The market's implied independence is approximately correct**, and this closes the last candidate named in
`research/model_vs_market` as a plausible source of information the price lacks.

## What this does not test

* Dependence within one player's own ladder, excluded here as mechanically dependent.
* **Tail dependence specifically** — whether the extreme joint scenarios (a blowout, a shootout) are priced.
  The averages above could be right while the tails are wrong, and the tails are where a correlation product
  would actually pay.
* Power is limited. A clustered SE of 0.0074 on 202 games would not detect an effect of a point or two, which
  is the size that would matter. This is a null result at this sample size, not a demonstration of exact
  independence.
