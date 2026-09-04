# Shadow ledger: reading the disagreements without fooling ourselves

Reproduce: `python3 scripts/shadow/ledger_report.py --json-out research/shadow/ledger_report.json`

Snapshot `20260904T174955Z`, model `shadow-0.3.0` (the first bundle carrying the validated role features).
12,408 observations written, 1,343 SUPPORTED and quoted, 10,663 UNSUPPORTED_MODEL, 402 UNSUPPORTED_RULES.

**Nothing below is an edge.** These are prospective model-market disagreements recorded before kickoff on
markets with no settled outcome yet.

## The midpoint is not a price, and ranking by it ranks by illiquidity

| family | n | median width | model inside spread | clears ask | clears bid | clears after fee | mean \|vs mid\| |
|---|---|---|---|---|---|---|---|
| PLAYER_STAT | 452 | 0.060 | 49.1% | 9.7% | 41.2% | 36.9% | 0.0635 |
| SPREAD | 404 | 0.020 | 53.7% | 19.1% | 27.2% | 7.2% | 0.0136 |
| TOTAL | 304 | 0.030 | 64.5% | 18.8% | 16.8% | 8.2% | 0.0125 |
| GAME_WINNER | 64 | 0.020 | 37.5% | 29.7% | 32.8% | 12.5% | 0.0144 |
| **BOTH_TEAMS_SCORE_N** | 64 | **0.510** | **98.4%** | 0.0% | 1.6% | **0.0%** | **0.1399** |
| TEAM_TOTAL | 55 | 0.090 | 92.7% | 7.3% | 0.0% | 7.3% | 0.0400 |
| all | 1343 | 0.030 | 57.6% | 15.0% | 27.5% | 17.3% | 0.0373 |

`BOTH_TEAMS_SCORE_N` has by far the largest disagreement against the midpoint — 0.140, four times any other
family. It is also quoted **51 cents wide**, and the model's price falls inside that spread 98.4% of the
time. There is no disagreement there that anyone could act on; there is an empty book and an arithmetic
midpoint between two prices nobody is trading at.

Stated as the ranking it would produce: take the 50 contracts with the largest \|disagreement vs midpoint\|.
Their median quoted width is **0.240 against 0.030 for the supported set as a whole** — an eight-fold wider
book — and 17 of the 50 have the model price inside the spread, meaning zero executable disagreement. A
selection rule based on distance from the midpoint is, to a good approximation, a selection rule for the
widest and thinnest markets on the exchange. This is why no selective "official card" has been created.

## Where the player-prop bias comes from

PLAYER_STAT disagreement averages −0.0334 (the model prices below the market). It decomposes as:

* **−0.0140** the availability haircut. The model prices the *contract*, not the event: a player who does not
  dress settles at $0.00, so contract value = P(plays) × P(event) + P(active, no snap) × fair price. Mean
  P(plays) across this slate is 0.934.
* **−0.0194** the model's event probability sitting below the market (0.2498 against a 0.2692 mean mid).

And it is not uniform. By market price: −0.007 in [0, 0.10) where the median width is 0.030, against −0.083
in [0.35, 0.50) and −0.073 in [0.50, 0.65) where the median widths are 0.045 and **0.210**. The apparent
disagreement grows with the spread, which is the signature of a midpoint artifact rather than of a view.

Whether the remaining −0.019 is market juice on the YES side or model bias **cannot be settled from
prospective quotes alone**. It needs the 2025 settled ladders, where model prices, closing quotes and
realised outcomes can all be compared on the same contracts — which is what the horizon backfill is for.

## Support states are doing their job

10,663 of 12,408 observations are UNSUPPORTED_MODEL: season-long awards, draft, transaction, business and
Super Bowl markets that this platform has no model for and deliberately does not price. 402 are
UNSUPPORTED_RULES, mostly settlement semantics the pricer refuses to guess at. Failing closed on 86% of the
listed universe is the intended behaviour, not a coverage gap to be closed by loosening the rules.
