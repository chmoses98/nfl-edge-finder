# Model distribution vs the market's own implied distribution

Reproduce: `python3 scripts/research/market_vs_model_shape.py`

Kalshi's ladder prices define a discrete survival function P(Y ≥ k) directly. Comparing it with the model's on
the same rungs separates a disagreement about the **centre** (different projected mean) from a disagreement
about the **shape** (same centre, different tail thickness). The second is the more interesting one: a
systematic tail disagreement across many independent ladders points at the distribution family rather than at
any one player.

Snapshot `20260904T174955Z`, 49 market-implied ladders, of which **30** have at least three rungs shared with
the model and a median quoted width ≤ 0.10. Ladders wider than that are excluded — above 10 cents the implied
survival is an artefact of an empty book, not a market view.

## Centre

Summed survival over the listed rungs (a proxy for the projected mean), model minus market: **−0.232** mean,
−0.173 median, sd 0.613 across 30 ladders. The model projects lower than the market, consistent with the
−0.019 event-probability gap in `research/shadow/RESULTS.md`. By statistic: rushing_yards −0.463 ± 0.335,
receptions −0.296 ± 0.188, receiving_yards −0.172 ± 0.092, passing_tds +0.016, passing_yards +0.170. Only
receiving_yards is even close to two standard errors, on n = 10 ladders.

## Shape

After removing each ladder's own centre disagreement, with **standard errors clustered on ladder** (the rungs
of one player's ladder are one observation, not three):

| ladder position | rungs | ladders | model − market | clustered SE | naive SE | z |
|---|---|---|---|---|---|---|
| low rungs (likely) | 94 | 30 | −0.0199 | 0.0139 | 0.0096 | 1.43 |
| middle rungs | 71 | 30 | +0.0052 | 0.0077 | 0.0057 | 0.68 |
| high rungs (tail) | 82 | 30 | +0.0183 | 0.0116 | 0.0062 | 1.57 |

The pattern is that the model's distribution is **flatter than the market's** — less mass on the likely
outcomes, more in the upper tail. It is suggestive and **it is not significant**: the largest effect is
1.6 standard errors on 30 ladders.

Clustering matters here. The naive standard errors are 1.5–1.9× too small, and would have reported the tail
effect at z = 2.95 — a publishable-looking result manufactured entirely by treating three rungs of one
player's ladder as three independent observations.

Registered as `H-20260904-013` for prospective testing across many snapshots and, once games are played,
against settled outcomes — which is the only way to tell whether the market's tighter tail is right.
