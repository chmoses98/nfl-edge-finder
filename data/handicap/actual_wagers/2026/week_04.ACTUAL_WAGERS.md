# Owner actual placed wagers — season 2026, week 4

> OWNER ACTUAL PLACED WAGERS -- ACCOUNTING ONLY. Every wager here was placed by the owner and recommended by nothing in this repository. These are real-money facts about a bankroll, not evidence about any model, and they are never used to train or tune one. Counts are small; no rate below establishes an edge.

## POSITION EPISODES (the economically meaningful record)

> POSITION LIFECYCLE -- ACCOUNTING ONLY. An order is a transaction, not a bet: orders on one market are replayed on Kalshi's single signed position, and each flat-to-flat EPISODE is one independent position. A cashout is position management, not a second wager. Nothing here is model evidence or a recommendation.

* Independent position episodes: **3** (from 4 transactions/orders)
* Pregame thesis: 0 · live thesis: 0 · unknown phase: 3 · opened within 10 min after scheduled kickoff: 0
* Full cashouts: 1 · partial cashouts: 0 · reversals: 0 · held to settlement: 2
* Total P&L (all executions and fees): — = realized trading -138.40 + settlement — - fees 8.75
* PREGAME ENTRY CLV (one observation per pregame-opened episode; exits and live entries excluded): 0 valid, mean —/contract, positive —; states {'PHASE_UNKNOWN_NO_PREGAME_CLV': 3}
* Live exit benchmark: {'exits': 1, 'valued': 0, 'states': {'EXIT_UNKNOWN_NO_LIVE_BENCHMARK': 1}}
* Lifecycle vs order-settlement reconciliation: {'ORDER_SETTLEMENTS_INCOMPLETE': 2, 'RECONCILED': 1}

| episode | market | opened | phase | side | opened qty | entry cost | adds | reductions | cashouts | final qty | settlement | fees | realized trading | settlement P&L | total P&L | entry CLV | exit benchmark | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ep-e5b65751cb33f91ba4c7 | KXNFLGAME-26OCT01PITCLE-PIT | 2026-10-01T23:52:22Z | UNKNOWN | LONG_YES | 247.14 | 150.00 | 0 | 0 | 1 | 0 | NOT_APPLICABLE | 4.69 | -138.40 | 0.00 | -143.09 | PHASE_UNKNOWN_NO_PREGAME_CLV | EXIT_UNKNOWN_NO_LIVE_BENCHMARK | UNKNOWN_POSITION_FULL_CASHOUT_UNKNOWN |
| ep-0a1b2f36b1956f1a8499 | KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8-1 | 2026-10-01T23:53:06Z | UNKNOWN | LONG_YES | 104.73 | 50.00 | 0 | 0 | 0 | 104.73 | SETTLED | 1.82 | 0.00 | 56.55 | 54.73 | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |
| ep-be9443ad01c248a0604e | KXNFLRSHYDS-26OCT01PITCLE-PITJWARREN30-70 | 2026-10-01T23:52:41Z | UNKNOWN | LONG_YES | 129.92 | 75.00 | 0 | 0 | 0 | 129.92 | NOT_SETTLED | 2.24 | 0.00 | — | — | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |

### Transactions (chronological, per market)

| market | executed | action | side | qty | price | fee | before | after | role | phase | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KXNFLGAME-26OCT01PITCLE-PIT | 2026-10-01T23:52:22Z | BUY | YES | 247.14 | 0.59 | 4.1849 | 0.0 | 247.14 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLGAME-26OCT01PITCLE-PIT | 2026-10-02T03:27:53Z | SELL | NO | 247.14 | 0.97 | 0.5035 | 247.14 | 0.0 | CASHOUT_CLOSE | UNKNOWN | NO_KICKOFF |
| KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8-1 | 2026-10-01T23:53:06Z | BUY | YES | 104.73 | 0.46 | 1.8211 | 0.0 | 104.73 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8-1 | (settlement) | — | — | 104.73 | 1.0 | — | 104.73 | 0.0 | SETTLEMENT | POST_FINAL | — |
| KXNFLRSHYDS-26OCT01PITCLE-PITJWARREN30-70 | 2026-10-01T23:52:41Z | BUY | YES | 129.92 | 0.56 | 2.2409 | 0.0 | 129.92 | OPEN | UNKNOWN | NO_KICKOFF |

`*` the verb was not delivered (pre-`execution_action` record); the side is replayed as the exposure it states. Position before/after are on Kalshi's signed YES axis (+ long YES, - long NO).

### Exposure: turnover vs capital at risk

| game | orders | episodes | original cash outlay | added | cashout proceeds | gross transaction volume | recycled in volume | max simultaneous capital at risk | at | total P&L |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT01PITCLE | 4 | 3 | 274.99 | 0.00 | 7.41 | 515.22 | 240.23 | 274.99 | 2026-10-01T23:53:06Z | — |

Gross transaction volume is the sum of order stakes (turnover). It is NOT capital at risk: an exit bought on the complementary side carries a large stake while returning cash.

### Anti-chase governance

> ANTI-CHASE GOVERNANCE -- REPORTING ONLY. Previous losses are sunk: past P&L never changes the probability of a new wager and a past loss never justifies a larger stake. These flags describe what the transaction timeline shows; nothing here blocks, sizes or recommends a wager.

| code | subject | market | detail |
|---|---|---|---|
| CORRELATED_EXPOSURE_HIGH | 26OCT01PITCLE | — | 3 position episodes on one game settle on one game state |

## Orders (transactions -- NOT independent bets)

The tables below count ORDERS. An order that reduced or closed a position (a cashout) is a transaction in the same position, not a second wager; W/L per order and stake summed over orders (turnover) are therefore not a betting record. Order-level CLV counts pregame entries only; exits and live entries carry the states NOT_AN_ENTRY_EXIT_OR_REDUCTION / NOT_APPLICABLE_LIVE_ENTRY.

Stake is contracts x execution price PLUS the entry fee the exchange charged on the fills; `fees` is that entry fee. Net P&L is the router's settlement figure: gross return - stake - settlement fee (settlement fees on established wagers: 0.00). CLV is per contract on the side held, against the canonical close of the exact contract, excluding fees.

## Totals

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 4 | 1 | 0 | 3 | 0 | 515.22 | 8.75 | — | — | — | 0 | — | — | 4 |

ECONOMICS: figures above are CANONICAL -- the settlement as amended, where an append-only amendment corrected it (0 amended; versions {'router-settlement-economics.v2': 1}). As ORIGINALLY RECORDED, net P&L: —. The exchange evidence and the filed settlements are unchanged; an amendment sits beside the record it supersedes.

FEE RECONCILIATION (a finding, not a rewrite). Kalshi's settlement `fee_cost` equals, to the cent, the entry fees already inside the stakes on every reconciled position, so the recorded net subtracts the trading fee twice. Recorded net stays as filed; the reconciled net is gross - stake where the exchange's own figures prove that equality (0 of 1 established wagers). Not every established wager reconciles, so no fee-reconciled total is stated.

Headline gross/net/ROI withheld: 3 pending and 0 settled with an unestablished figure. ESTABLISHED SUBSET ONLY (1 of 4 wagers, not the period's P&L): stake 50.00, gross 104.73, net 54.73, ROI 109.5%.

## By week

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 4 | 1 | 0 | 3 | 0 | 515.22 | 8.75 | — | — | — | 0 | — | — | 4 |

## By market family

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| game_winner | 2 | 0 | 0 | 2 | 0 | 390.23 | 4.69 | — | — | — | 0 | — | — | 2 |
| series:KXNFLPASSINT | 1 | 1 | 0 | 0 | 0 | 50.00 | 1.82 | 104.73 | 54.73 | 109.5% | 0 | — | — | 1 |
| series:KXNFLRSHYDS | 1 | 0 | 0 | 1 | 0 | 75.00 | 2.24 | — | — | — | 0 | — | — | 1 |

## By game

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KXNFLGAME-26OCT01PITCLE | 2 | 0 | 0 | 2 | 0 | 390.23 | 4.69 | — | — | — | 0 | — | — | 2 |
| KXNFLPASSINT-26OCT01PITCLE | 1 | 1 | 0 | 0 | 0 | 50.00 | 1.82 | 104.73 | 54.73 | 109.5% | 0 | — | — | 1 |
| KXNFLRSHYDS-26OCT01PITCLE | 1 | 0 | 0 | 1 | 0 | 75.00 | 2.24 | — | — | — | 0 | — | — | 1 |

## Orders

| week | game | family | side | contracts | price | stake | fees | result | gross | net | close | CLV/contract | CLV state | role | phase |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | KXNFLGAME-26OCT01PITCLE | game_winner | YES | 247.14 | 0.59 | 150.00 | 4.18 | PENDING | — | — | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |
| 4 | KXNFLGAME-26OCT01PITCLE | game_winner | NO | 247.14 | 0.97 | 240.23 | 0.50 | PENDING | — | — | — | — | NOT_AN_ENTRY_EXIT_OR_REDUCTION | CASHOUT_CLOSE | UNKNOWN |
| 4 | KXNFLPASSINT-26OCT01PITCLE | series:KXNFLPASSINT | YES | 104.73 | 0.46 | 50.00 | 1.82 | WON | 104.73 | 54.73 | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |
| 4 | KXNFLRSHYDS-26OCT01PITCLE | series:KXNFLRSHYDS | YES | 129.92 | 0.56 | 75.00 | 2.24 | PENDING | — | — | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |

## RISK & CONCENTRATION

Governance reporting only: where the placed stake sat and how much of the result each exposure explains. Nothing here changes, recommends or caps a stake. Different tickers are not diversification: wagers are grouped by game, market, ladder (one underlying variable) and correlated cluster.

Net basis: **NONE COMPLETE** (preference net_canonical > net_fee_reconciled > net_profit_loss). No net basis covers every wager in scope; P&L figures are for the wagers that have one and are labelled incomplete.

| basis | wagers with figure | complete | stake | net P&L | ROI |
|---|---|---|---|---|---|
| net_canonical | 1 | NO | 515.22 | 54.73 | — |
| net_fee_reconciled | 1 | NO | 515.22 | 54.73 | — |
| net_profit_loss | 1 | NO | 515.22 | 54.73 | — |

Share of starting bankroll: NOT_AVAILABLE — no readable starting-bankroll evidence for the owner's account (the router's bankroll is a secret; nothing is guessed).

### Warnings

| code | subject | value | threshold | detail |
|---|---|---|---|---|
| CONCENTRATION_HIGH | 26OCT01PITCLE#1 | 100.0% | > 25.0% | one correlated cluster carries 100.0% of the scope's stake |
| CORRELATED_EXPOSURE_HIGH | 26OCT01PITCLE#1 | 100.0% | > 16.7% | 4 linked legs (OPPOSING_POSITION_PAIR, SAME_GAME_CORRELATED, SAME_MARKET) carry 100.0% of stake |
| OPPOSING_POSITION_PAIR | KXNFLGAME-26OCT01PITCLE-PIT | 75.7% | > 0.0% | YES and NO on one contract; 247.14 matched contracts at a combined 1.56 per contract fix that part's result at entry |
| SINGLE_GAME_DOMINATES_WEEK | 26OCT01PITCLE | 100.0% | > 33.3% | one game carries 100.0% of the scope's stake |

### Largest exposures

| exposure | which | stake | % of scope stake | % of bankroll |
|---|---|---|---|---|
| wager | KXNFLGAME-26OCT01PITCLE-PIT | 240.23 | 46.6% | NOT_AVAILABLE |
| game | 26OCT01PITCLE | 515.22 | 100.0% | NOT_AVAILABLE |
| market | KXNFLGAME-26OCT01PITCLE-PIT | 390.23 | 75.7% | NOT_AVAILABLE |
| ladder | KXNFLGAME-26OCT01PITCLE | 390.23 | 75.7% | NOT_AVAILABLE |
| cluster | 26OCT01PITCLE#1 | 515.22 | 100.0% | NOT_AVAILABLE |
| player | PITJWARREN30 | 75.00 | 14.6% | NOT_AVAILABLE |

`% of net` is the group's net divided by the scope's net on that basis: when the scope lost, it is the group's share of the total loss (a winning group shows a negative share); shares sum to 100%.

### By correlated cluster

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) | links |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT01PITCLE#1 | 4 | 515.22 | 100.0% | 54.73 (partial) | 100.0% | 54.73 (partial) | 100.0% | 54.73 (partial) | 100.0% | OPPOSING_POSITION_PAIR, SAME_GAME_CORRELATED, SAME_MARKET |

### By game

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| 26OCT01PITCLE | 4 | 515.22 | 100.0% | 54.73 (partial) | 100.0% | 54.73 (partial) | 100.0% | 54.73 (partial) | 100.0% |

### By market family

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| game_winner | 2 | 390.23 | 75.7% | — (partial) | — | — (partial) | — | — (partial) | — |
| series:KXNFLRSHYDS | 1 | 75.00 | 14.6% | — (partial) | — | — (partial) | — | — (partial) | — |
| series:KXNFLPASSINT | 1 | 50.00 | 9.7% | 54.73 | 100.0% | 54.73 | 100.0% | 54.73 | 100.0% |

### By ladder (underlying variable)

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLGAME-26OCT01PITCLE | 2 | 390.23 | 75.7% | — (partial) | — | — (partial) | — | — (partial) | — |
| KXNFLRSHYDS-26OCT01PITCLE-PITJWARREN30 | 1 | 75.00 | 14.6% | — (partial) | — | — (partial) | — | — (partial) | — |
| KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8 | 1 | 50.00 | 9.7% | 54.73 | 100.0% | 54.73 | 100.0% | 54.73 | 100.0% |

### By market

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLGAME-26OCT01PITCLE-PIT | 2 | 390.23 | 75.7% | — (partial) | — | — (partial) | — | — (partial) | — |
| KXNFLRSHYDS-26OCT01PITCLE-PITJWARREN30-70 | 1 | 75.00 | 14.6% | — (partial) | — | — (partial) | — | — (partial) | — |
| KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8-1 | 1 | 50.00 | 9.7% | 54.73 | 100.0% | 54.73 | 100.0% | 54.73 | 100.0% |

### By player (parsable player props; not a partition of stake)

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| PITJWARREN30 | 1 | 75.00 | 14.6% | — (partial) | — | — (partial) | — | — (partial) | — |
| PITARODGERS8 | 1 | 50.00 | 9.7% | 54.73 | 100.0% | 54.73 | 100.0% | 54.73 | 100.0% |

### Opposing positions (YES + NO on one contract)

| market | YES contracts | NO contracts | matched | combined price | locked P&L before fees | stake |
|---|---|---|---|---|---|---|
| KXNFLGAME-26OCT01PITCLE-PIT | 247.14 | 247.14 | 247.14 | 1.56 | -138.40 | 390.23 |

### Decomposition: entry quality, outcome variance, sizing

* Entry quality, outcome variance and sizing CANNOT be perfectly separated. The split below is an accounting identity, not a causal attribution: net = CLV$ + outcome residual - friction, where CLV$ = contracts x (canonical close price of the side held - price paid), outcome residual = gross return - contracts x close price (what the result paid beyond what the close priced), and friction is the remainder (fees and, on the recorded basis, the settlement fee).
* The canonical close is itself an estimate (a mid, at one moment). A YES+NO pair's legs offset each other's residuals by construction, so a pair's outcome residual says nothing about the game.
* Sizing/concentration is shown as the cluster's share of stake beside its share of net P&L; a large loss share on a large stake share is what concentration does whether or not the entry was good.
* One or two weeks of wagers is far too few to establish skill or its absence. Nothing here does.

| cluster | wagers | % stake | % of net (None) | CLV valid | CLV$ | mean CLV/contract | sign | outcome residual vs close | friction | net (None) |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT01PITCLE#1 | 4 | 100.0% | — | 0 | — | — | — | — | — | — |

### Rules and thresholds

* SAME_MARKET: identical market ticker (two orders on one contract are one exposure)
* OPPOSING_POSITION_PAIR: YES and NO held on the identical market ticker
* SAME_LADDER: different rungs of one underlying variable (same series + event [+ subject])
* SAME_GAME_CORRELATED: same game, both families in `same_game_linked_families` (default: every family; spread, game winner, team total, totals and player props on one game all settle on one game state)
* Thresholds (share of scope stake, strictly greater fires): CONCENTRATION_HIGH > 25.0% for one cluster; CORRELATED_EXPOSURE_HIGH > 16.7% for a cluster of ≥ 2 legs; SINGLE_GAME_DOMINATES_WEEK > 33.3% for one game; OPPOSING_POSITION_PAIR for any YES+NO pair above 0.0%. Same-game linked families: every family.
