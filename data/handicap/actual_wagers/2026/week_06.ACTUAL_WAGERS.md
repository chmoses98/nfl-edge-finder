# Owner actual placed wagers — season 2026, week 6

> OWNER ACTUAL PLACED WAGERS -- ACCOUNTING ONLY. Every wager here was placed by the owner and recommended by nothing in this repository. These are real-money facts about a bankroll, not evidence about any model, and they are never used to train or tune one. Counts are small; no rate below establishes an edge.

## POSITION EPISODES (the economically meaningful record)

> POSITION LIFECYCLE -- ACCOUNTING ONLY. An order is a transaction, not a bet: orders on one market are replayed on Kalshi's single signed position, and each flat-to-flat EPISODE is one independent position. A cashout is position management, not a second wager. Nothing here is model evidence or a recommendation.

* Independent position episodes: **2** (from 2 transactions/orders)
* Pregame thesis: 0 · live thesis: 0 · unknown phase: 2 · opened within 10 min after scheduled kickoff: 0
* Full cashouts: 0 · partial cashouts: 0 · reversals: 0 · held to settlement: 2
* Total P&L (all executions and fees): 44.11 = realized trading 0.00 + settlement 51.13 - fees 7.02
* PREGAME ENTRY CLV (one observation per pregame-opened episode; exits and live entries excluded): 0 valid, mean —/contract, positive —; states {'PHASE_UNKNOWN_NO_PREGAME_CLV': 2}
* Live exit benchmark: {'exits': 0, 'valued': 0, 'states': {}}
* Lifecycle vs order-settlement reconciliation: {'RECONCILED': 2}

| episode | market | opened | phase | side | opened qty | entry cost | adds | reductions | cashouts | final qty | settlement | fees | realized trading | settlement P&L | total P&L | entry CLV | exit benchmark | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ep-d19460bce1974bba5a89 | KXNFLRECYDS-26OCT15SEADEN-SEAJSMITHNJIGBA11-90 | 2026-10-16T00:07:26Z | UNKNOWN | LONG_YES | 269.11 | 150.00 | 0 | 0 | 0 | 269.11 | SETTLED | 4.68 | 0.00 | 123.79 | 119.11 | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |
| ep-1e29a3263a2329598e08 | KXNFLRSHATT-26OCT15SEADEN-SEAEWILSON23-18 | 2026-10-16T00:08:07Z | UNKNOWN | LONG_YES | 134.55 | 75.00 | 0 | 0 | 0 | 134.55 | SETTLED | 2.34 | 0.00 | -72.66 | -75.00 | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |

### Transactions (chronological, per market)

| market | executed | action | side | qty | price | fee | before | after | role | phase | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KXNFLRECYDS-26OCT15SEADEN-SEAJSMITHNJIGBA11-90 | 2026-10-16T00:07:26Z | BUY | YES | 269.11 | 0.54 | 4.6793 | 0.0 | 269.11 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLRECYDS-26OCT15SEADEN-SEAJSMITHNJIGBA11-90 | (settlement) | — | — | 269.11 | 1.0 | — | 269.11 | 0.0 | SETTLEMENT | POST_FINAL | — |
| KXNFLRSHATT-26OCT15SEADEN-SEAEWILSON23-18 | 2026-10-16T00:08:07Z | BUY | YES | 134.55 | 0.54 | 2.3396 | 0.0 | 134.55 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLRSHATT-26OCT15SEADEN-SEAEWILSON23-18 | (settlement) | — | — | 134.55 | 0.0 | — | 134.55 | 0.0 | SETTLEMENT | POST_FINAL | — |

`*` the verb was not delivered (pre-`execution_action` record); the side is replayed as the exposure it states. Position before/after are on Kalshi's signed YES axis (+ long YES, - long NO).

### Exposure: turnover vs capital at risk

| game | orders | episodes | original cash outlay | added | cashout proceeds | gross transaction volume | recycled in volume | max simultaneous capital at risk | at | total P&L |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT15SEADEN | 2 | 2 | 225.00 | 0.00 | 0.00 | 225.00 | 0.00 | 225.00 | 2026-10-16T00:08:07Z | 44.11 |

Gross transaction volume is the sum of order stakes (turnover). It is NOT capital at risk: an exit bought on the complementary side carries a large stake while returning cash.

### Anti-chase governance

> ANTI-CHASE GOVERNANCE -- REPORTING ONLY. Previous losses are sunk: past P&L never changes the probability of a new wager and a past loss never justifies a larger stake. These flags describe what the transaction timeline shows; nothing here blocks, sizes or recommends a wager.

No flags.

## Orders (transactions -- NOT independent bets)

The tables below count ORDERS. An order that reduced or closed a position (a cashout) is a transaction in the same position, not a second wager; W/L per order and stake summed over orders (turnover) are therefore not a betting record. Order-level CLV counts pregame entries only; exits and live entries carry the states NOT_AN_ENTRY_EXIT_OR_REDUCTION / NOT_APPLICABLE_LIVE_ENTRY.

Stake is contracts x execution price PLUS the entry fee the exchange charged on the fills; `fees` is that entry fee. Net P&L is the router's settlement figure: gross return - stake - settlement fee (settlement fees on established wagers: 0.00). CLV is per contract on the side held, against the canonical close of the exact contract, excluding fees.

## Totals

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 2 | 1 | 1 | 0 | 0 | 225.00 | 7.02 | 269.11 | 44.11 | 19.6% | 0 | — | — | 2 |

ECONOMICS: figures above are CANONICAL -- the settlement as amended, where an append-only amendment corrected it (0 amended; versions {'router-settlement-economics.v2': 2}). As ORIGINALLY RECORDED, net P&L: 44.11. The exchange evidence and the filed settlements are unchanged; an amendment sits beside the record it supersedes.

FEE RECONCILIATION (a finding, not a rewrite). Kalshi's settlement `fee_cost` equals, to the cent, the entry fees already inside the stakes on every reconciled position, so the recorded net subtracts the trading fee twice. Recorded net stays as filed; the reconciled net is gross - stake where the exchange's own figures prove that equality (0 of 2 established wagers). Not every established wager reconciles, so no fee-reconciled total is stated.

## By week

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6 | 2 | 1 | 1 | 0 | 0 | 225.00 | 7.02 | 269.11 | 44.11 | 19.6% | 0 | — | — | 2 |

## By market family

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| series:KXNFLRECYDS | 1 | 1 | 0 | 0 | 0 | 150.00 | 4.68 | 269.11 | 119.11 | 79.4% | 0 | — | — | 1 |
| series:KXNFLRSHATT | 1 | 0 | 1 | 0 | 0 | 75.00 | 2.34 | 0.00 | -75.00 | -100.0% | 0 | — | — | 1 |

## By game

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KXNFLRECYDS-26OCT15SEADEN | 1 | 1 | 0 | 0 | 0 | 150.00 | 4.68 | 269.11 | 119.11 | 79.4% | 0 | — | — | 1 |
| KXNFLRSHATT-26OCT15SEADEN | 1 | 0 | 1 | 0 | 0 | 75.00 | 2.34 | 0.00 | -75.00 | -100.0% | 0 | — | — | 1 |

## Orders

| week | game | family | side | contracts | price | stake | fees | result | gross | net | close | CLV/contract | CLV state | role | phase |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6 | KXNFLRECYDS-26OCT15SEADEN | series:KXNFLRECYDS | YES | 269.11 | 0.54 | 150.00 | 4.68 | WON | 269.11 | 119.11 | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |
| 6 | KXNFLRSHATT-26OCT15SEADEN | series:KXNFLRSHATT | YES | 134.55 | 0.54 | 75.00 | 2.34 | LOST | 0.00 | -75.00 | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |

## RISK & CONCENTRATION

Governance reporting only: where the placed stake sat and how much of the result each exposure explains. Nothing here changes, recommends or caps a stake. Different tickers are not diversification: wagers are grouped by game, market, ladder (one underlying variable) and correlated cluster.

Net basis: **net_canonical** (preference net_canonical > net_fee_reconciled > net_profit_loss). P&L below is on the primary basis (the most-preferred one every wager has); other bases are shown beside it, never merged.

| basis | wagers with figure | complete | stake | net P&L | ROI |
|---|---|---|---|---|---|
| net_canonical (primary) | 2 | yes | 225.00 | 44.11 | 19.6% |
| net_fee_reconciled | 2 | yes | 225.00 | 44.11 | 19.6% |
| net_profit_loss | 2 | yes | 225.00 | 44.11 | 19.6% |

Share of starting bankroll: NOT_AVAILABLE — no readable starting-bankroll evidence for the owner's account (the router's bankroll is a secret; nothing is guessed).

### Warnings

| code | subject | value | threshold | detail |
|---|---|---|---|---|
| CONCENTRATION_HIGH | 26OCT15SEADEN#1 | 100.0% | > 25.0% | one correlated cluster carries 100.0% of the scope's stake |
| CORRELATED_EXPOSURE_HIGH | 26OCT15SEADEN#1 | 100.0% | > 16.7% | 2 linked legs (SAME_GAME_CORRELATED) carry 100.0% of stake |
| SINGLE_GAME_DOMINATES_WEEK | 26OCT15SEADEN | 100.0% | > 33.3% | one game carries 100.0% of the scope's stake |

### Largest exposures

| exposure | which | stake | % of scope stake | % of bankroll |
|---|---|---|---|---|
| wager | KXNFLRECYDS-26OCT15SEADEN-SEAJSMITHNJIGBA11-90 | 150.00 | 66.7% | NOT_AVAILABLE |
| game | 26OCT15SEADEN | 225.00 | 100.0% | NOT_AVAILABLE |
| market | KXNFLRECYDS-26OCT15SEADEN-SEAJSMITHNJIGBA11-90 | 150.00 | 66.7% | NOT_AVAILABLE |
| ladder | KXNFLRECYDS-26OCT15SEADEN-SEAJSMITHNJIGBA11 | 150.00 | 66.7% | NOT_AVAILABLE |
| cluster | 26OCT15SEADEN#1 | 225.00 | 100.0% | NOT_AVAILABLE |
| player | SEAJSMITHNJIGBA11 | 150.00 | 66.7% | NOT_AVAILABLE |

`% of net` is the group's net divided by the scope's net on that basis: when the scope lost, it is the group's share of the total loss (a winning group shows a negative share); shares sum to 100%.

### By correlated cluster

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) | links |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT15SEADEN#1 | 2 | 225.00 | 100.0% | 44.11 | 100.0% | 44.11 | 100.0% | 44.11 | 100.0% | SAME_GAME_CORRELATED |

### By game

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| 26OCT15SEADEN | 2 | 225.00 | 100.0% | 44.11 | 100.0% | 44.11 | 100.0% | 44.11 | 100.0% |

### By market family

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| series:KXNFLRECYDS | 1 | 150.00 | 66.7% | 119.11 | 270.0% | 119.11 | 270.0% | 119.11 | 270.0% |
| series:KXNFLRSHATT | 1 | 75.00 | 33.3% | -75.00 | -170.0% | -75.00 | -170.0% | -75.00 | -170.0% |

### By ladder (underlying variable)

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLRECYDS-26OCT15SEADEN-SEAJSMITHNJIGBA11 | 1 | 150.00 | 66.7% | 119.11 | 270.0% | 119.11 | 270.0% | 119.11 | 270.0% |
| KXNFLRSHATT-26OCT15SEADEN-SEAEWILSON23 | 1 | 75.00 | 33.3% | -75.00 | -170.0% | -75.00 | -170.0% | -75.00 | -170.0% |

### By market

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLRECYDS-26OCT15SEADEN-SEAJSMITHNJIGBA11-90 | 1 | 150.00 | 66.7% | 119.11 | 270.0% | 119.11 | 270.0% | 119.11 | 270.0% |
| KXNFLRSHATT-26OCT15SEADEN-SEAEWILSON23-18 | 1 | 75.00 | 33.3% | -75.00 | -170.0% | -75.00 | -170.0% | -75.00 | -170.0% |

### By player (parsable player props; not a partition of stake)

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| SEAJSMITHNJIGBA11 | 1 | 150.00 | 66.7% | 119.11 | 270.0% | 119.11 | 270.0% | 119.11 | 270.0% |
| SEAEWILSON23 | 1 | 75.00 | 33.3% | -75.00 | -170.0% | -75.00 | -170.0% | -75.00 | -170.0% |

### Decomposition: entry quality, outcome variance, sizing

* Entry quality, outcome variance and sizing CANNOT be perfectly separated. The split below is an accounting identity, not a causal attribution: net = CLV$ + outcome residual - friction, where CLV$ = contracts x (canonical close price of the side held - price paid), outcome residual = gross return - contracts x close price (what the result paid beyond what the close priced), and friction is the remainder (fees and, on the recorded basis, the settlement fee).
* The canonical close is itself an estimate (a mid, at one moment). A YES+NO pair's legs offset each other's residuals by construction, so a pair's outcome residual says nothing about the game.
* Sizing/concentration is shown as the cluster's share of stake beside its share of net P&L; a large loss share on a large stake share is what concentration does whether or not the entry was good.
* One or two weeks of wagers is far too few to establish skill or its absence. Nothing here does.

| cluster | wagers | % stake | % of net (net_canonical) | CLV valid | CLV$ | mean CLV/contract | sign | outcome residual vs close | friction | net (net_canonical) |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT15SEADEN#1 | 2 | 100.0% | 100.0% | 0 | — | — | — | — | — | 44.11 |

### Rules and thresholds

* SAME_MARKET: identical market ticker (two orders on one contract are one exposure)
* OPPOSING_POSITION_PAIR: YES and NO held on the identical market ticker
* SAME_LADDER: different rungs of one underlying variable (same series + event [+ subject])
* SAME_GAME_CORRELATED: same game, both families in `same_game_linked_families` (default: every family; spread, game winner, team total, totals and player props on one game all settle on one game state)
* Thresholds (share of scope stake, strictly greater fires): CONCENTRATION_HIGH > 25.0% for one cluster; CORRELATED_EXPOSURE_HIGH > 16.7% for a cluster of ≥ 2 legs; SINGLE_GAME_DOMINATES_WEEK > 33.3% for one game; OPPOSING_POSITION_PAIR for any YES+NO pair above 0.0%. Same-game linked families: every family.
