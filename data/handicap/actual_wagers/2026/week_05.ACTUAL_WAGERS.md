# Owner actual placed wagers — season 2026, week 5

> OWNER ACTUAL PLACED WAGERS -- ACCOUNTING ONLY. Every wager here was placed by the owner and recommended by nothing in this repository. These are real-money facts about a bankroll, not evidence about any model, and they are never used to train or tune one. Counts are small; no rate below establishes an edge.

## POSITION EPISODES (the economically meaningful record)

> POSITION LIFECYCLE -- ACCOUNTING ONLY. An order is a transaction, not a bet: orders on one market are replayed on Kalshi's single signed position, and each flat-to-flat EPISODE is one independent position. A cashout is position management, not a second wager. Nothing here is model evidence or a recommendation.

* Independent position episodes: **3** (from 3 transactions/orders)
* Pregame thesis: 0 · live thesis: 0 · unknown phase: 3 · opened within 10 min after scheduled kickoff: 0
* Full cashouts: 0 · partial cashouts: 0 · reversals: 0 · held to settlement: 3
* Total P&L (all executions and fees): — = realized trading 0.00 + settlement — - fees 5.66
* PREGAME ENTRY CLV (one observation per pregame-opened episode; exits and live entries excluded): 0 valid, mean —/contract, positive —; states {'PHASE_UNKNOWN_NO_PREGAME_CLV': 3}
* Live exit benchmark: {'exits': 0, 'valued': 0, 'states': {}}
* Lifecycle vs order-settlement reconciliation: {'ORDER_SETTLEMENTS_INCOMPLETE': 1, 'RECONCILED': 2}

| episode | market | opened | phase | side | opened qty | entry cost | adds | reductions | cashouts | final qty | settlement | fees | realized trading | settlement P&L | total P&L | entry CLV | exit benchmark | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ep-6b8209f7c0910983fca3 | KXMVECROSSCATEGORY0-S202651C3A8A0798-F6322FBCCFC | 2026-10-11T16:27:47Z | UNKNOWN | LONG_YES | 423.72 | 9.96 | 0 | 0 | 0 | 423.72 | NOT_SETTLED | 0.64 | 0.00 | — | — | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |
| ep-b112d6519a9cee06ce39 | KXNFLSPREAD-26OCT08TBDAL-DAL8 | 2026-10-09T00:16:57Z | UNKNOWN | LONG_YES | 125.61 | 75.00 | 0 | 0 | 0 | 125.61 | SETTLED | 2.14 | 0.00 | -72.85 | -75.00 | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |
| ep-1c3494895fd85111c72e | KXNFLTEAMTOTAL-26OCT08TBDAL-DAL32 | 2026-10-09T00:16:41Z | UNKNOWN | LONG_YES | 167.72 | 75.00 | 0 | 0 | 0 | 167.72 | SETTLED | 2.88 | 0.00 | -72.12 | -75.00 | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |

### Transactions (chronological, per market)

| market | executed | action | side | qty | price | fee | before | after | role | phase | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KXMVECROSSCATEGORY0-S202651C3A8A0798-F6322FBCCFC | 2026-10-11T16:27:47Z | BUY | YES | 423.72 | 0.022 | 0.63826 | 0.0 | 423.72 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLSPREAD-26OCT08TBDAL-DAL8 | 2026-10-09T00:16:57Z | BUY | YES | 125.61 | 0.58 | 2.142 | 0.0 | 125.61 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLSPREAD-26OCT08TBDAL-DAL8 | (settlement) | — | — | 125.61 | 0.0 | — | 125.61 | 0.0 | SETTLEMENT | POST_FINAL | — |
| KXNFLTEAMTOTAL-26OCT08TBDAL-DAL32 | 2026-10-09T00:16:41Z | BUY | YES | 167.72 | 0.43 | 2.8776 | 0.0 | 167.72 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLTEAMTOTAL-26OCT08TBDAL-DAL32 | (settlement) | — | — | 167.72 | 0.0 | — | 167.72 | 0.0 | SETTLEMENT | POST_FINAL | — |

`*` the verb was not delivered (pre-`execution_action` record); the side is replayed as the exposure it states. Position before/after are on Kalshi's signed YES axis (+ long YES, - long NO).

### Exposure: turnover vs capital at risk

| game | orders | episodes | original cash outlay | added | cashout proceeds | gross transaction volume | recycled in volume | max simultaneous capital at risk | at | total P&L |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT08TBDAL | 2 | 2 | 149.99 | 0.00 | 0.00 | 149.99 | 0.00 | 149.99 | 2026-10-09T00:16:57Z | -149.99 |
| S202651C3A8A0798 | 1 | 1 | 9.96 | 0.00 | 0.00 | 9.96 | 0.00 | 9.96 | 2026-10-11T16:27:47Z | — |

Gross transaction volume is the sum of order stakes (turnover). It is NOT capital at risk: an exit bought on the complementary side carries a large stake while returning cash.

### Anti-chase governance

> ANTI-CHASE GOVERNANCE -- REPORTING ONLY. Previous losses are sunk: past P&L never changes the probability of a new wager and a past loss never justifies a larger stake. These flags describe what the transaction timeline shows; nothing here blocks, sizes or recommends a wager.

| code | subject | market | detail |
|---|---|---|---|
| SINGLE_GAME_EXPOSURE_HIGH | 26OCT08TBDAL | — | peak capital at risk 149.99 is 93.8% of the sum of per-game peaks (> 50%) |

## Orders (transactions -- NOT independent bets)

The tables below count ORDERS. An order that reduced or closed a position (a cashout) is a transaction in the same position, not a second wager; W/L per order and stake summed over orders (turnover) are therefore not a betting record. Order-level CLV counts pregame entries only; exits and live entries carry the states NOT_AN_ENTRY_EXIT_OR_REDUCTION / NOT_APPLICABLE_LIVE_ENTRY.

Stake is contracts x execution price PLUS the entry fee the exchange charged on the fills; `fees` is that entry fee. Net P&L is the router's settlement figure: gross return - stake - settlement fee (settlement fees on established wagers: 0.00). CLV is per contract on the side held, against the canonical close of the exact contract, excluding fees.

## Totals

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 3 | 0 | 2 | 1 | 0 | 159.95 | 5.66 | — | — | — | 0 | — | — | 3 |

ECONOMICS: figures above are CANONICAL -- the settlement as amended, where an append-only amendment corrected it (0 amended; versions {'router-settlement-economics.v2': 2}). As ORIGINALLY RECORDED, net P&L: —. The exchange evidence and the filed settlements are unchanged; an amendment sits beside the record it supersedes.

FEE RECONCILIATION (a finding, not a rewrite). Kalshi's settlement `fee_cost` equals, to the cent, the entry fees already inside the stakes on every reconciled position, so the recorded net subtracts the trading fee twice. Recorded net stays as filed; the reconciled net is gross - stake where the exchange's own figures prove that equality (0 of 2 established wagers). Not every established wager reconciles, so no fee-reconciled total is stated.

Headline gross/net/ROI withheld: 1 pending and 0 settled with an unestablished figure. ESTABLISHED SUBSET ONLY (2 of 3 wagers, not the period's P&L): stake 149.99, gross 0.00, net -149.99, ROI -100.0%.

## By week

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 3 | 0 | 2 | 1 | 0 | 159.95 | 5.66 | — | — | — | 0 | — | — | 3 |

## By market family

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| series:KXMVECROSSCATEGORY0 | 1 | 0 | 0 | 1 | 0 | 9.96 | 0.64 | — | — | — | 0 | — | — | 1 |
| spread | 1 | 0 | 1 | 0 | 0 | 75.00 | 2.14 | 0.00 | -75.00 | -100.0% | 0 | — | — | 1 |
| team_total | 1 | 0 | 1 | 0 | 0 | 75.00 | 2.88 | 0.00 | -75.00 | -100.0% | 0 | — | — | 1 |

## By game

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KXMVECROSSCATEGORY0-S202651C3A8A0798 | 1 | 0 | 0 | 1 | 0 | 9.96 | 0.64 | — | — | — | 0 | — | — | 1 |
| KXNFLSPREAD-26OCT08TBDAL | 1 | 0 | 1 | 0 | 0 | 75.00 | 2.14 | 0.00 | -75.00 | -100.0% | 0 | — | — | 1 |
| KXNFLTEAMTOTAL-26OCT08TBDAL | 1 | 0 | 1 | 0 | 0 | 75.00 | 2.88 | 0.00 | -75.00 | -100.0% | 0 | — | — | 1 |

## Orders

| week | game | family | side | contracts | price | stake | fees | result | gross | net | close | CLV/contract | CLV state | role | phase |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | KXNFLSPREAD-26OCT08TBDAL | spread | YES | 125.61 | 0.58 | 75.00 | 2.14 | LOST | 0.00 | -75.00 | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |
| 5 | KXNFLTEAMTOTAL-26OCT08TBDAL | team_total | YES | 167.72 | 0.43 | 75.00 | 2.88 | LOST | 0.00 | -75.00 | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |
| 5 | KXMVECROSSCATEGORY0-S202651C3A8A0798 | series:KXMVECROSSCATEGORY0 | YES | 423.72 | 0.022 | 9.96 | 0.64 | PENDING | — | — | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |

## RISK & CONCENTRATION

Governance reporting only: where the placed stake sat and how much of the result each exposure explains. Nothing here changes, recommends or caps a stake. Different tickers are not diversification: wagers are grouped by game, market, ladder (one underlying variable) and correlated cluster.

Net basis: **NONE COMPLETE** (preference net_canonical > net_fee_reconciled > net_profit_loss). No net basis covers every wager in scope; P&L figures are for the wagers that have one and are labelled incomplete.

| basis | wagers with figure | complete | stake | net P&L | ROI |
|---|---|---|---|---|---|
| net_canonical | 2 | NO | 159.95 | -149.99 | — |
| net_fee_reconciled | 2 | NO | 159.95 | -149.99 | — |
| net_profit_loss | 2 | NO | 159.95 | -149.99 | — |

Share of starting bankroll: NOT_AVAILABLE — no readable starting-bankroll evidence for the owner's account (the router's bankroll is a secret; nothing is guessed).

### Warnings

| code | subject | value | threshold | detail |
|---|---|---|---|---|
| CONCENTRATION_HIGH | 26OCT08TBDAL#1 | 93.8% | > 25.0% | one correlated cluster carries 93.8% of the scope's stake |
| CORRELATED_EXPOSURE_HIGH | 26OCT08TBDAL#1 | 93.8% | > 16.7% | 2 linked legs (SAME_GAME_CORRELATED) carry 93.8% of stake |
| SINGLE_GAME_DOMINATES_WEEK | 26OCT08TBDAL | 93.8% | > 33.3% | one game carries 93.8% of the scope's stake |

### Largest exposures

| exposure | which | stake | % of scope stake | % of bankroll |
|---|---|---|---|---|
| wager | KXNFLTEAMTOTAL-26OCT08TBDAL-DAL32 | 75.00 | 46.9% | NOT_AVAILABLE |
| game | 26OCT08TBDAL | 149.99 | 93.8% | NOT_AVAILABLE |
| market | KXNFLTEAMTOTAL-26OCT08TBDAL-DAL32 | 75.00 | 46.9% | NOT_AVAILABLE |
| ladder | KXNFLTEAMTOTAL-26OCT08TBDAL-DAL | 75.00 | 46.9% | NOT_AVAILABLE |
| cluster | 26OCT08TBDAL#1 | 149.99 | 93.8% | NOT_AVAILABLE |
| player | none parsable | — | — | — |

`% of net` is the group's net divided by the scope's net on that basis: when the scope lost, it is the group's share of the total loss (a winning group shows a negative share); shares sum to 100%.

### By correlated cluster

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) | links |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT08TBDAL#1 | 2 | 149.99 | 93.8% | -149.99 | 100.0% | -149.99 | 100.0% | -149.99 | 100.0% | SAME_GAME_CORRELATED |
| S202651C3A8A0798#1 | 1 | 9.96 | 6.2% | — (partial) | — | — (partial) | — | — (partial) | — | single wager |

### By game

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| 26OCT08TBDAL | 2 | 149.99 | 93.8% | -149.99 | 100.0% | -149.99 | 100.0% | -149.99 | 100.0% |
| S202651C3A8A0798 | 1 | 9.96 | 6.2% | — (partial) | — | — (partial) | — | — (partial) | — |

### By market family

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| team_total | 1 | 75.00 | 46.9% | -75.00 | 50.0% | -75.00 | 50.0% | -75.00 | 50.0% |
| spread | 1 | 75.00 | 46.9% | -75.00 | 50.0% | -75.00 | 50.0% | -75.00 | 50.0% |
| series:KXMVECROSSCATEGORY0 | 1 | 9.96 | 6.2% | — (partial) | — | — (partial) | — | — (partial) | — |

### By ladder (underlying variable)

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLTEAMTOTAL-26OCT08TBDAL-DAL | 1 | 75.00 | 46.9% | -75.00 | 50.0% | -75.00 | 50.0% | -75.00 | 50.0% |
| KXNFLSPREAD-26OCT08TBDAL | 1 | 75.00 | 46.9% | -75.00 | 50.0% | -75.00 | 50.0% | -75.00 | 50.0% |
| KXMVECROSSCATEGORY0-S202651C3A8A0798 | 1 | 9.96 | 6.2% | — (partial) | — | — (partial) | — | — (partial) | — |

### By market

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLTEAMTOTAL-26OCT08TBDAL-DAL32 | 1 | 75.00 | 46.9% | -75.00 | 50.0% | -75.00 | 50.0% | -75.00 | 50.0% |
| KXNFLSPREAD-26OCT08TBDAL-DAL8 | 1 | 75.00 | 46.9% | -75.00 | 50.0% | -75.00 | 50.0% | -75.00 | 50.0% |
| KXMVECROSSCATEGORY0-S202651C3A8A0798-F6322FBCCFC | 1 | 9.96 | 6.2% | — (partial) | — | — (partial) | — | — (partial) | — |

### Decomposition: entry quality, outcome variance, sizing

* Entry quality, outcome variance and sizing CANNOT be perfectly separated. The split below is an accounting identity, not a causal attribution: net = CLV$ + outcome residual - friction, where CLV$ = contracts x (canonical close price of the side held - price paid), outcome residual = gross return - contracts x close price (what the result paid beyond what the close priced), and friction is the remainder (fees and, on the recorded basis, the settlement fee).
* The canonical close is itself an estimate (a mid, at one moment). A YES+NO pair's legs offset each other's residuals by construction, so a pair's outcome residual says nothing about the game.
* Sizing/concentration is shown as the cluster's share of stake beside its share of net P&L; a large loss share on a large stake share is what concentration does whether or not the entry was good.
* One or two weeks of wagers is far too few to establish skill or its absence. Nothing here does.

| cluster | wagers | % stake | % of net (None) | CLV valid | CLV$ | mean CLV/contract | sign | outcome residual vs close | friction | net (None) |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT08TBDAL#1 | 2 | 93.8% | — | 0 | — | — | — | — | — | — |
| S202651C3A8A0798#1 | 1 | 6.2% | — | 0 | — | — | — | — | — | — |

### Rules and thresholds

* SAME_MARKET: identical market ticker (two orders on one contract are one exposure)
* OPPOSING_POSITION_PAIR: YES and NO held on the identical market ticker
* SAME_LADDER: different rungs of one underlying variable (same series + event [+ subject])
* SAME_GAME_CORRELATED: same game, both families in `same_game_linked_families` (default: every family; spread, game winner, team total, totals and player props on one game all settle on one game state)
* Thresholds (share of scope stake, strictly greater fires): CONCENTRATION_HIGH > 25.0% for one cluster; CORRELATED_EXPOSURE_HIGH > 16.7% for a cluster of ≥ 2 legs; SINGLE_GAME_DOMINATES_WEEK > 33.3% for one game; OPPOSING_POSITION_PAIR for any YES+NO pair above 0.0%. Same-game linked families: every family.
