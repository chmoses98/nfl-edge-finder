# Owner actual placed wagers — season 2026, week 3

> OWNER ACTUAL PLACED WAGERS -- ACCOUNTING ONLY. Every wager here was placed by the owner and recommended by nothing in this repository. These are real-money facts about a bankroll, not evidence about any model, and they are never used to train or tune one. Counts are small; no rate below establishes an edge.

## POSITION EPISODES (the economically meaningful record)

> POSITION LIFECYCLE -- ACCOUNTING ONLY. An order is a transaction, not a bet: orders on one market are replayed on Kalshi's single signed position, and each flat-to-flat EPISODE is one independent position. A cashout is position management, not a second wager. Nothing here is model evidence or a recommendation.

* Independent position episodes: **5** (from 6 transactions/orders)
* Pregame thesis: 1 · live thesis: 4 · unknown phase: 0 · opened within 10 min after scheduled kickoff: 3
* Full cashouts: 1 · partial cashouts: 0 · reversals: 0 · held to settlement: 4
* Total P&L (all executions and fees): -49.71 = realized trading 6.40 + settlement -49.05 - fees 7.06
* PREGAME ENTRY CLV (one observation per pregame-opened episode; exits and live entries excluded): 1 valid, mean -0.0050/contract, positive 0.0%; states {'CLV_VALID': 1, 'NOT_APPLICABLE_LIVE_ENTRY': 4}
* Live exit benchmark: {'exits': 1, 'valued': 1, 'states': {'LIVE_EXIT_VALUE': 1}}
* Lifecycle vs order-settlement reconciliation: {'RECONCILED': 5}

| episode | market | opened | phase | side | opened qty | entry cost | adds | reductions | cashouts | final qty | settlement | fees | realized trading | settlement P&L | total P&L | entry CLV | exit benchmark | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ep-791b67c24889e1e9413e | KXNFL1HTEAMTOTAL-26SEP24ATLGB-ATL10 | 2026-09-25T00:14:46Z | PRE_GAME | LONG_NO | 98.52 | 50.00 | 0 | 0 | 0 | 98.52 | SETTLED | 1.72 | 0.00 | -48.27 | -50.00 | -0.0050 | — | PREGAME_POSITION_HELD_TO_SETTLEMENT |
| ep-7fbe594a597f916f8895 | KXNFLGAME-26SEP24ATLGB-GB | 2026-09-25T01:59:59Z | LIVE | LONG_YES | 59.66 | 20.00 | 0 | 0 | 0 | 59.66 | SETTLED | 0.91 | 0.00 | -19.09 | -20.00 | NOT_APPLICABLE_LIVE_ENTRY | — | LIVE_POSITION_HELD_TO_SETTLEMENT |
| ep-548ec278784a67038dca | KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275 | 2026-09-25T00:15:28Z | LIVE | LONG_YES | 91.41 | 25.00 | 0 | 0 | 1 | 0 | NOT_APPLICABLE | 2.65 | 6.40 | 0.00 | 3.75 | NOT_APPLICABLE_LIVE_ENTRY | LIVE_EXIT_VALUE +0.0000 | LIVE_POSITION_FULL_CASHOUT_LIVE |
| ep-a5bd30ec865cb5765943 | KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5-60 | 2026-09-25T00:16:45Z | LIVE | LONG_NO | 44.11 | 19.99 | 0 | 0 | 0 | 44.11 | SETTLED | 0.76 | 0.00 | -19.23 | -19.99 | NOT_APPLICABLE_LIVE_ENTRY | — | LIVE_POSITION_HELD_TO_SETTLEMENT |
| ep-8a295ead09e12b2e1935 | KXNFLRSHYDS-26SEP24ATLGB-GBKJOHNSON26-30 | 2026-09-25T00:16:21Z | LIVE | LONG_NO | 61.51 | 24.99 | 0 | 0 | 0 | 61.51 | SETTLED | 1.02 | 0.00 | 37.55 | 36.52 | NOT_APPLICABLE_LIVE_ENTRY | — | LIVE_POSITION_HELD_TO_SETTLEMENT |

### Transactions (chronological, per market)

| market | executed | action | side | qty | price | fee | before | after | role | phase | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KXNFL1HTEAMTOTAL-26SEP24ATLGB-ATL10 | 2026-09-25T00:14:46Z | BUY* | NO | 98.52 | 0.49 | 1.7235 | 0.0 | -98.52 | OPEN | PRE_GAME | — |
| KXNFL1HTEAMTOTAL-26SEP24ATLGB-ATL10 | (settlement) | — | — | 98.52 | 1.0 | — | -98.52 | 0.0 | SETTLEMENT | POST_FINAL | — |
| KXNFLGAME-26SEP24ATLGB-GB | 2026-09-25T01:59:59Z | BUY* | YES | 59.66 | 0.32 | 0.9088 | 0.0 | 59.66 | OPEN | LIVE | — |
| KXNFLGAME-26SEP24ATLGB-GB | (settlement) | — | — | 59.66 | 0.0 | — | 59.66 | 0.0 | SETTLEMENT | POST_FINAL | — |
| KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275 | 2026-09-25T00:15:28Z | BUY* | YES | 91.41 | 0.26 | 1.2312 | 0.0 | 91.41 | OPEN | LIVE | NEAR_SCHEDULED_KICKOFF |
| KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275 | 2026-09-25T02:43:34Z | BUY* | NO | 91.41 | 0.67 | 1.4148 | 91.41 | 0.0 | CASHOUT_CLOSE | LIVE | — |
| KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5-60 | 2026-09-25T00:16:45Z | BUY* | NO | 44.11 | 0.43594423033325774 | 0.7588 | 0.0 | -44.11 | OPEN | LIVE | NEAR_SCHEDULED_KICKOFF |
| KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5-60 | (settlement) | — | — | 44.11 | 1.0 | — | -44.11 | 0.0 | SETTLEMENT | POST_FINAL | — |
| KXNFLRSHYDS-26SEP24ATLGB-GBKJOHNSON26-30 | 2026-09-25T00:16:21Z | BUY* | NO | 61.51 | 0.38959518777434565 | 1.0236 | 0.0 | -61.51 | OPEN | LIVE | NEAR_SCHEDULED_KICKOFF |
| KXNFLRSHYDS-26SEP24ATLGB-GBKJOHNSON26-30 | (settlement) | — | — | 61.51 | 0.0 | — | -61.51 | 0.0 | SETTLEMENT | POST_FINAL | — |

`*` the verb was not delivered (pre-`execution_action` record); the side is replayed as the exposure it states. Position before/after are on Kalshi's signed YES axis (+ long YES, - long NO).

### Exposure: turnover vs capital at risk

| game | orders | episodes | original cash outlay | added | cashout proceeds | gross transaction volume | recycled in volume | max simultaneous capital at risk | at | total P&L |
|---|---|---|---|---|---|---|---|---|---|---|
| 26SEP24ATLGB | 6 | 5 | 139.97 | 0.00 | 30.17 | 202.63 | 62.66 | 139.97 | 2026-09-25T01:59:59Z | -49.71 |

Gross transaction volume is the sum of order stakes (turnover). It is NOT capital at risk: an exit bought on the complementary side carries a large stake while returning cash.

### Anti-chase governance

> ANTI-CHASE GOVERNANCE -- REPORTING ONLY. Previous losses are sunk: past P&L never changes the probability of a new wager and a past loss never justifies a larger stake. These flags describe what the transaction timeline shows; nothing here blocks, sizes or recommends a wager.

| code | subject | market | detail |
|---|---|---|---|
| CORRELATED_EXPOSURE_HIGH | 26SEP24ATLGB | — | 5 position episodes on one game settle on one game state |

## Orders (transactions -- NOT independent bets)

The tables below count ORDERS. An order that reduced or closed a position (a cashout) is a transaction in the same position, not a second wager; W/L per order and stake summed over orders (turnover) are therefore not a betting record. Order-level CLV counts pregame entries only; exits and live entries carry the states NOT_AN_ENTRY_EXIT_OR_REDUCTION / NOT_APPLICABLE_LIVE_ENTRY.

Stake is contracts x execution price PLUS the entry fee the exchange charged on the fills; `fees` is that entry fee. Net P&L is the router's settlement figure: gross return - stake - settlement fee (settlement fees on established wagers: 0.00). CLV is per contract on the side held, against the canonical close of the exact contract, excluding fees.

## Totals

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 6 | 2 | 4 | 0 | 0 | 202.63 | 7.06 | 152.92 | -49.71 | -24.5% | 1 | -0.0050 | 0.0% | 5 |

ECONOMICS: figures above are CANONICAL -- the settlement as amended, where an append-only amendment corrected it (0 amended; versions {'router-settlement-economics.v2': 6}). As ORIGINALLY RECORDED, net P&L: -49.71. The exchange evidence and the filed settlements are unchanged; an amendment sits beside the record it supersedes.

FEE RECONCILIATION (a finding, not a rewrite). Kalshi's settlement `fee_cost` equals, to the cent, the entry fees already inside the stakes on every reconciled position, so the recorded net subtracts the trading fee twice. Recorded net stays as filed; the reconciled net is gross - stake where the exchange's own figures prove that equality (0 of 6 established wagers). Not every established wager reconciles, so no fee-reconciled total is stated.

## By week

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 6 | 2 | 4 | 0 | 0 | 202.63 | 7.06 | 152.92 | -49.71 | -24.5% | 1 | -0.0050 | 0.0% | 5 |

## By market family

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| game_winner | 1 | 0 | 1 | 0 | 0 | 20.00 | 0.91 | 0.00 | -20.00 | -100.0% | 0 | — | — | 1 |
| series:KXNFL1HTEAMTOTAL | 1 | 0 | 1 | 0 | 0 | 50.00 | 1.72 | 0.00 | -50.00 | -100.0% | 1 | -0.0050 | 0.0% | 0 |
| series:KXNFLPASSYDS | 2 | 1 | 1 | 0 | 0 | 87.66 | 2.65 | 91.41 | 3.75 | 4.3% | 0 | — | — | 2 |
| series:KXNFLRECYDS | 1 | 0 | 1 | 0 | 0 | 19.99 | 0.76 | 0.00 | -19.99 | -100.0% | 0 | — | — | 1 |
| series:KXNFLRSHYDS | 1 | 1 | 0 | 0 | 0 | 24.99 | 1.02 | 61.51 | 36.52 | 146.2% | 0 | — | — | 1 |

## By game

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_03_ATL_GB | 6 | 2 | 4 | 0 | 0 | 202.63 | 7.06 | 152.92 | -49.71 | -24.5% | 1 | -0.0050 | 0.0% | 5 |

## Orders

| week | game | family | side | contracts | price | stake | fees | result | gross | net | close | CLV/contract | CLV state | role | phase |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 2026_03_ATL_GB | series:KXNFL1HTEAMTOTAL | NO | 98.52 | 0.49 | 50.00 | 1.72 | LOST | 0.00 | -50.00 | 0.485 | -0.0050 | CLV_VALID | OPEN | PRE_GAME |
| 3 | 2026_03_ATL_GB | game_winner | YES | 59.66 | 0.32 | 20.00 | 0.91 | LOST | 0.00 | -20.00 | 0.685 | — | NOT_APPLICABLE_LIVE_ENTRY | OPEN | LIVE |
| 3 | 2026_03_ATL_GB | series:KXNFLPASSYDS | NO | 91.41 | 0.67 | 62.66 | 1.41 | LOST | 0.00 | -62.66 | 0.755 | — | NOT_AN_ENTRY_EXIT_OR_REDUCTION | CASHOUT_CLOSE | LIVE |
| 3 | 2026_03_ATL_GB | series:KXNFLPASSYDS | YES | 91.41 | 0.26 | 25.00 | 1.23 | WON | 91.41 | 66.41 | 0.245 | — | NOT_APPLICABLE_LIVE_ENTRY | OPEN | LIVE |
| 3 | 2026_03_ATL_GB | series:KXNFLRECYDS | NO | 44.11 | 0.43594423033325774 | 19.99 | 0.76 | LOST | 0.00 | -19.99 | 0.425 | — | NOT_APPLICABLE_LIVE_ENTRY | OPEN | LIVE |
| 3 | 2026_03_ATL_GB | series:KXNFLRSHYDS | NO | 61.51 | 0.38959518777434565 | 24.99 | 1.02 | WON | 61.51 | 36.52 | 0.365 | — | NOT_APPLICABLE_LIVE_ENTRY | OPEN | LIVE |

## RISK & CONCENTRATION

Governance reporting only: where the placed stake sat and how much of the result each exposure explains. Nothing here changes, recommends or caps a stake. Different tickers are not diversification: wagers are grouped by game, market, ladder (one underlying variable) and correlated cluster.

Net basis: **net_canonical** (preference net_canonical > net_fee_reconciled > net_profit_loss). P&L below is on the primary basis (the most-preferred one every wager has); other bases are shown beside it, never merged.

| basis | wagers with figure | complete | stake | net P&L | ROI |
|---|---|---|---|---|---|
| net_canonical (primary) | 6 | yes | 202.63 | -49.71 | -24.5% |
| net_fee_reconciled | 6 | yes | 202.63 | -49.71 | -24.5% |
| net_profit_loss | 6 | yes | 202.63 | -49.71 | -24.5% |

Share of starting bankroll: NOT_AVAILABLE — no readable starting-bankroll evidence for the owner's account (the router's bankroll is a secret; nothing is guessed).

### Warnings

| code | subject | value | threshold | detail |
|---|---|---|---|---|
| CONCENTRATION_HIGH | 2026_03_ATL_GB#1 | 100.0% | > 25.0% | one correlated cluster carries 100.0% of the scope's stake |
| CORRELATED_EXPOSURE_HIGH | 2026_03_ATL_GB#1 | 100.0% | > 16.7% | 6 linked legs (OPPOSING_POSITION_PAIR, SAME_GAME_CORRELATED, SAME_MARKET) carry 100.0% of stake |
| OPPOSING_POSITION_PAIR | KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275 | 43.3% | > 0.0% | YES and NO on one contract; 91.41 matched contracts at a combined 0.93 per contract fix that part's result at entry |
| SINGLE_GAME_DOMINATES_WEEK | 2026_03_ATL_GB | 100.0% | > 33.3% | one game carries 100.0% of the scope's stake |

### Largest exposures

| exposure | which | stake | % of scope stake | % of bankroll |
|---|---|---|---|---|
| wager | KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275 | 62.66 | 30.9% | NOT_AVAILABLE |
| game | 2026_03_ATL_GB | 202.63 | 100.0% | NOT_AVAILABLE |
| market | KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275 | 87.66 | 43.3% | NOT_AVAILABLE |
| ladder | KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10 | 87.66 | 43.3% | NOT_AVAILABLE |
| cluster | 2026_03_ATL_GB#1 | 202.63 | 100.0% | NOT_AVAILABLE |
| player | GBJLOVE10 | 87.66 | 43.3% | NOT_AVAILABLE |

`% of net` is the group's net divided by the scope's net on that basis: when the scope lost, it is the group's share of the total loss (a winning group shows a negative share); shares sum to 100%.

### By correlated cluster

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) | links |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026_03_ATL_GB#1 | 6 | 202.63 | 100.0% | -49.71 | 100.0% | -49.71 | 100.0% | -49.71 | 100.0% | OPPOSING_POSITION_PAIR, SAME_GAME_CORRELATED, SAME_MARKET |

### By game

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| 2026_03_ATL_GB | 6 | 202.63 | 100.0% | -49.71 | 100.0% | -49.71 | 100.0% | -49.71 | 100.0% |

### By market family

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| series:KXNFLPASSYDS | 2 | 87.66 | 43.3% | 3.75 | -7.5% | 3.75 | -7.5% | 3.75 | -7.5% |
| series:KXNFL1HTEAMTOTAL | 1 | 50.00 | 24.7% | -50.00 | 100.6% | -50.00 | 100.6% | -50.00 | 100.6% |
| series:KXNFLRSHYDS | 1 | 24.99 | 12.3% | 36.52 | -73.5% | 36.52 | -73.5% | 36.52 | -73.5% |
| game_winner | 1 | 20.00 | 9.9% | -20.00 | 40.2% | -20.00 | 40.2% | -20.00 | 40.2% |
| series:KXNFLRECYDS | 1 | 19.99 | 9.9% | -19.99 | 40.2% | -19.99 | 40.2% | -19.99 | 40.2% |

### By ladder (underlying variable)

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10 | 2 | 87.66 | 43.3% | 3.75 | -7.5% | 3.75 | -7.5% | 3.75 | -7.5% |
| KXNFL1HTEAMTOTAL-26SEP24ATLGB | 1 | 50.00 | 24.7% | -50.00 | 100.6% | -50.00 | 100.6% | -50.00 | 100.6% |
| KXNFLRSHYDS-26SEP24ATLGB-GBKJOHNSON26 | 1 | 24.99 | 12.3% | 36.52 | -73.5% | 36.52 | -73.5% | 36.52 | -73.5% |
| KXNFLGAME-26SEP24ATLGB | 1 | 20.00 | 9.9% | -20.00 | 40.2% | -20.00 | 40.2% | -20.00 | 40.2% |
| KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5 | 1 | 19.99 | 9.9% | -19.99 | 40.2% | -19.99 | 40.2% | -19.99 | 40.2% |

### By market

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275 | 2 | 87.66 | 43.3% | 3.75 | -7.5% | 3.75 | -7.5% | 3.75 | -7.5% |
| KXNFL1HTEAMTOTAL-26SEP24ATLGB-ATL10 | 1 | 50.00 | 24.7% | -50.00 | 100.6% | -50.00 | 100.6% | -50.00 | 100.6% |
| KXNFLRSHYDS-26SEP24ATLGB-GBKJOHNSON26-30 | 1 | 24.99 | 12.3% | 36.52 | -73.5% | 36.52 | -73.5% | 36.52 | -73.5% |
| KXNFLGAME-26SEP24ATLGB-GB | 1 | 20.00 | 9.9% | -20.00 | 40.2% | -20.00 | 40.2% | -20.00 | 40.2% |
| KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5-60 | 1 | 19.99 | 9.9% | -19.99 | 40.2% | -19.99 | 40.2% | -19.99 | 40.2% |

### By player (parsable player props; not a partition of stake)

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| GBJLOVE10 | 2 | 87.66 | 43.3% | 3.75 | -7.5% | 3.75 | -7.5% | 3.75 | -7.5% |
| GBKJOHNSON26 | 1 | 24.99 | 12.3% | 36.52 | -73.5% | 36.52 | -73.5% | 36.52 | -73.5% |
| ATLDLONDON5 | 1 | 19.99 | 9.9% | -19.99 | 40.2% | -19.99 | 40.2% | -19.99 | 40.2% |

### Opposing positions (YES + NO on one contract)

| market | YES contracts | NO contracts | matched | combined price | locked P&L before fees | stake |
|---|---|---|---|---|---|---|
| KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275 | 91.41 | 91.41 | 91.41 | 0.93 | 6.40 | 87.66 |

### Decomposition: entry quality, outcome variance, sizing

* Entry quality, outcome variance and sizing CANNOT be perfectly separated. The split below is an accounting identity, not a causal attribution: net = CLV$ + outcome residual - friction, where CLV$ = contracts x (canonical close price of the side held - price paid), outcome residual = gross return - contracts x close price (what the result paid beyond what the close priced), and friction is the remainder (fees and, on the recorded basis, the settlement fee).
* The canonical close is itself an estimate (a mid, at one moment). A YES+NO pair's legs offset each other's residuals by construction, so a pair's outcome residual says nothing about the game.
* Sizing/concentration is shown as the cluster's share of stake beside its share of net P&L; a large loss share on a large stake share is what concentration does whether or not the entry was good.
* One or two weeks of wagers is far too few to establish skill or its absence. Nothing here does.

| cluster | wagers | % stake | % of net (net_canonical) | CLV valid | CLV$ | mean CLV/contract | sign | outcome residual vs close | friction | net (net_canonical) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026_03_ATL_GB#1 | 6 | 100.0% | 100.0% | 1 | -0.49 | -0.0050 | NEGATIVE | -68.34 | — | -49.71 |

### Rules and thresholds

* SAME_MARKET: identical market ticker (two orders on one contract are one exposure)
* OPPOSING_POSITION_PAIR: YES and NO held on the identical market ticker
* SAME_LADDER: different rungs of one underlying variable (same series + event [+ subject])
* SAME_GAME_CORRELATED: same game, both families in `same_game_linked_families` (default: every family; spread, game winner, team total, totals and player props on one game all settle on one game state)
* Thresholds (share of scope stake, strictly greater fires): CONCENTRATION_HIGH > 25.0% for one cluster; CORRELATED_EXPOSURE_HIGH > 16.7% for a cluster of ≥ 2 legs; SINGLE_GAME_DOMINATES_WEEK > 33.3% for one game; OPPOSING_POSITION_PAIR for any YES+NO pair above 0.0%. Same-game linked families: every family.
