# Owner actual placed wagers — season 2026, week 4

> OWNER ACTUAL PLACED WAGERS -- ACCOUNTING ONLY. Every wager here was placed by the owner and recommended by nothing in this repository. These are real-money facts about a bankroll, not evidence about any model, and they are never used to train or tune one. Counts are small; no rate below establishes an edge.

## POSITION EPISODES (the economically meaningful record)

> POSITION LIFECYCLE -- ACCOUNTING ONLY. An order is a transaction, not a bet: orders on one market are replayed on Kalshi's single signed position, and each flat-to-flat EPISODE is one independent position. A cashout is position management, not a second wager. Nothing here is model evidence or a recommendation.

* Independent position episodes: **7** (from 9 transactions/orders)
* Pregame thesis: 3 · live thesis: 0 · unknown phase: 4 · opened within 10 min after scheduled kickoff: 0
* Full cashouts: 1 · partial cashouts: 0 · reversals: 0 · held to settlement: 6
* Total P&L (all executions and fees): — = realized trading -138.40 + settlement — - fees 15.02
* PREGAME ENTRY CLV (one observation per pregame-opened episode; exits and live entries excluded): 3 valid, mean +0.0017/contract, positive 66.7%; states {'CLV_VALID': 3, 'PHASE_UNKNOWN_NO_PREGAME_CLV': 4}
* Live exit benchmark: {'exits': 1, 'valued': 1, 'states': {'LIVE_EXIT_VALUE': 1}}
* Lifecycle vs order-settlement reconciliation: {'ORDER_SETTLEMENTS_INCOMPLETE': 2, 'RECONCILED': 5}

| episode | market | opened | phase | side | opened qty | entry cost | adds | reductions | cashouts | final qty | settlement | fees | realized trading | settlement P&L | total P&L | entry CLV | exit benchmark | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ep-e5b65751cb33f91ba4c7 | KXNFLGAME-26OCT01PITCLE-PIT | 2026-10-01T23:52:22Z | PRE_GAME | LONG_YES | 247.14 | 150.00 | 0 | 0 | 1 | 0 | NOT_APPLICABLE | 4.69 | -138.40 | 0.00 | -143.09 | +0.0050 | LIVE_EXIT_VALUE -0.1500 | PREGAME_POSITION_FULL_CASHOUT_LIVE |
| ep-4018b97a93d92daf15d1 | KXNFLGAME-26OCT04INDWAS-IND | 2026-10-04T06:08:56Z | UNKNOWN | LONG_YES | 36.99 | 24.99 | 0 | 0 | 0 | 36.99 | NOT_SETTLED | 0.58 | 0.00 | — | — | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |
| ep-0a1b2f36b1956f1a8499 | KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8-1 | 2026-10-01T23:53:06Z | PRE_GAME | LONG_YES | 104.73 | 50.00 | 0 | 0 | 0 | 104.73 | SETTLED | 1.82 | 0.00 | 56.55 | 54.73 | -0.0050 | — | PREGAME_POSITION_HELD_TO_SETTLEMENT |
| ep-70d2afc98953076fb840 | KXNFLRECYDS-26OCT04ARINYG-ARIJLOVE4-15 | 2026-10-04T13:06:48Z | UNKNOWN | LONG_YES | 170.3 | 99.99 | 1 | 0 | 0 | 170.3 | NOT_SETTLED | 2.92 | 0.00 | — | — | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |
| ep-be9443ad01c248a0604e | KXNFLRSHYDS-26OCT01PITCLE-PITJWARREN30-70 | 2026-10-01T23:52:41Z | PRE_GAME | LONG_YES | 129.92 | 75.00 | 0 | 0 | 0 | 129.92 | SETTLED | 2.24 | 0.00 | 57.16 | 54.92 | +0.0050 | — | PREGAME_POSITION_HELD_TO_SETTLEMENT |
| ep-76d6eb0ef147e6f38409 | KXNFLTD-26OCT04INDWAS-INDJTAYLOR28-1 | 2026-10-04T06:08:39Z | UNKNOWN | LONG_YES | 53.93 | 37.49 | 0 | 0 | 0 | 53.93 | SETTLED | 0.82 | 0.00 | 17.26 | 16.44 | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |
| ep-1488978a33b6bb0b6b9d | KXNFLTEAMTOTAL-26OCT04INDWAS-IND25 | 2026-10-04T06:08:19Z | UNKNOWN | LONG_YES | 112.13 | 62.50 | 0 | 0 | 0 | 112.13 | SETTLED | 1.95 | 0.00 | 51.58 | 49.63 | PHASE_UNKNOWN_NO_PREGAME_CLV | — | UNKNOWN_POSITION_HELD_TO_SETTLEMENT |

### Transactions (chronological, per market)

| market | executed | action | side | qty | price | fee | before | after | role | phase | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KXNFLGAME-26OCT01PITCLE-PIT | 2026-10-01T23:52:22Z | BUY | YES | 247.14 | 0.59 | 4.1849 | 0.0 | 247.14 | OPEN | PRE_GAME | — |
| KXNFLGAME-26OCT01PITCLE-PIT | 2026-10-02T03:27:53Z | SELL | NO | 247.14 | 0.97 | 0.5035 | 247.14 | 0.0 | CASHOUT_CLOSE | LIVE | — |
| KXNFLGAME-26OCT04INDWAS-IND | 2026-10-04T06:08:56Z | BUY | YES | 36.99 | 0.66 | 0.5811 | 0.0 | 36.99 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8-1 | 2026-10-01T23:53:06Z | BUY | YES | 104.73 | 0.46 | 1.8211 | 0.0 | 104.73 | OPEN | PRE_GAME | — |
| KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8-1 | (settlement) | — | — | 104.73 | 1.0 | — | 104.73 | 0.0 | SETTLEMENT | POST_FINAL | — |
| KXNFLRECYDS-26OCT04ARINYG-ARIJLOVE4-15 | 2026-10-04T13:06:48Z | BUY | YES | 85.15 | 0.57 | 1.461 | 0.0 | 85.15 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLRECYDS-26OCT04ARINYG-ARIJLOVE4-15 | 2026-10-04T13:08:18Z | BUY | YES | 85.15 | 0.57 | 1.461 | 85.15 | 170.3 | ADD | UNKNOWN | NO_KICKOFF |
| KXNFLRSHYDS-26OCT01PITCLE-PITJWARREN30-70 | 2026-10-01T23:52:41Z | BUY | YES | 129.92 | 0.56 | 2.2409 | 0.0 | 129.92 | OPEN | PRE_GAME | — |
| KXNFLRSHYDS-26OCT01PITCLE-PITJWARREN30-70 | (settlement) | — | — | 129.92 | 1.0 | — | 129.92 | 0.0 | SETTLEMENT | POST_FINAL | — |
| KXNFLTD-26OCT04INDWAS-INDJTAYLOR28-1 | 2026-10-04T06:08:39Z | BUY | YES | 53.93 | 0.68 | 0.8215 | 0.0 | 53.93 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLTD-26OCT04INDWAS-INDJTAYLOR28-1 | (settlement) | — | — | 53.93 | 1.0 | — | 53.93 | 0.0 | SETTLEMENT | POST_FINAL | — |
| KXNFLTEAMTOTAL-26OCT04INDWAS-IND25 | 2026-10-04T06:08:19Z | BUY | YES | 112.13 | 0.54 | 1.9498 | 0.0 | 112.13 | OPEN | UNKNOWN | NO_KICKOFF |
| KXNFLTEAMTOTAL-26OCT04INDWAS-IND25 | (settlement) | — | — | 112.13 | 1.0 | — | 112.13 | 0.0 | SETTLEMENT | POST_FINAL | — |

`*` the verb was not delivered (pre-`execution_action` record); the side is replayed as the exposure it states. Position before/after are on Kalshi's signed YES axis (+ long YES, - long NO).

### Exposure: turnover vs capital at risk

| game | orders | episodes | original cash outlay | added | cashout proceeds | gross transaction volume | recycled in volume | max simultaneous capital at risk | at | total P&L |
|---|---|---|---|---|---|---|---|---|---|---|
| 26OCT01PITCLE | 4 | 3 | 274.99 | 0.00 | 7.41 | 515.22 | 240.23 | 274.99 | 2026-10-01T23:53:06Z | -33.43 |
| 26OCT04ARINYG | 2 | 1 | 50.00 | 50.00 | 0.00 | 99.99 | 0.00 | 99.99 | 2026-10-04T13:08:18Z | — |
| 26OCT04INDWAS | 3 | 3 | 124.99 | 0.00 | 0.00 | 124.99 | 0.00 | 124.99 | 2026-10-04T06:08:56Z | — |

Gross transaction volume is the sum of order stakes (turnover). It is NOT capital at risk: an exit bought on the complementary side carries a large stake while returning cash.

### Anti-chase governance

> ANTI-CHASE GOVERNANCE -- REPORTING ONLY. Previous losses are sunk: past P&L never changes the probability of a new wager and a past loss never justifies a larger stake. These flags describe what the transaction timeline shows; nothing here blocks, sizes or recommends a wager.

| code | subject | market | detail |
|---|---|---|---|
| SINGLE_GAME_EXPOSURE_HIGH | 26OCT01PITCLE | — | peak capital at risk 274.99 is 55.0% of the sum of per-game peaks (> 50%) |
| CORRELATED_EXPOSURE_HIGH | 26OCT01PITCLE | — | 3 position episodes on one game settle on one game state |
| CORRELATED_EXPOSURE_HIGH | 26OCT04INDWAS | — | 3 position episodes on one game settle on one game state |

## Orders (transactions -- NOT independent bets)

The tables below count ORDERS. An order that reduced or closed a position (a cashout) is a transaction in the same position, not a second wager; W/L per order and stake summed over orders (turnover) are therefore not a betting record. Order-level CLV counts pregame entries only; exits and live entries carry the states NOT_AN_ENTRY_EXIT_OR_REDUCTION / NOT_APPLICABLE_LIVE_ENTRY.

Stake is contracts x execution price PLUS the entry fee the exchange charged on the fills; `fees` is that entry fee. Net P&L is the router's settlement figure: gross return - stake - settlement fee (settlement fees on established wagers: 0.00). CLV is per contract on the side held, against the canonical close of the exact contract, excluding fees.

## Totals

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 9 | 5 | 1 | 3 | 0 | 740.20 | 15.02 | — | — | — | 3 | +0.0017 | 66.7% | 6 |

ECONOMICS: figures above are CANONICAL -- the settlement as amended, where an append-only amendment corrected it (0 amended; versions {'router-settlement-economics.v2': 6}). As ORIGINALLY RECORDED, net P&L: —. The exchange evidence and the filed settlements are unchanged; an amendment sits beside the record it supersedes.

FEE RECONCILIATION (a finding, not a rewrite). Kalshi's settlement `fee_cost` equals, to the cent, the entry fees already inside the stakes on every reconciled position, so the recorded net subtracts the trading fee twice. Recorded net stays as filed; the reconciled net is gross - stake where the exchange's own figures prove that equality (0 of 6 established wagers). Not every established wager reconciles, so no fee-reconciled total is stated.

Headline gross/net/ROI withheld: 3 pending and 0 settled with an unestablished figure. ESTABLISHED SUBSET ONLY (6 of 9 wagers, not the period's P&L): stake 615.21, gross 647.85, net 32.64, ROI 5.3%.

## By week

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 9 | 5 | 1 | 3 | 0 | 740.20 | 15.02 | — | — | — | 3 | +0.0017 | 66.7% | 6 |

## By market family

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| game_winner | 3 | 1 | 1 | 1 | 0 | 415.22 | 5.27 | — | — | — | 1 | +0.0050 | 100.0% | 2 |
| series:KXNFLPASSINT | 1 | 1 | 0 | 0 | 0 | 50.00 | 1.82 | 104.73 | 54.73 | 109.5% | 1 | -0.0050 | 0.0% | 0 |
| series:KXNFLRECYDS | 2 | 0 | 0 | 2 | 0 | 99.99 | 2.92 | — | — | — | 0 | — | — | 2 |
| series:KXNFLRSHYDS | 1 | 1 | 0 | 0 | 0 | 75.00 | 2.24 | 129.92 | 54.92 | 73.2% | 1 | +0.0050 | 100.0% | 0 |
| series:KXNFLTD | 1 | 1 | 0 | 0 | 0 | 37.49 | 0.82 | 53.93 | 16.44 | 43.8% | 0 | — | — | 1 |
| team_total | 1 | 1 | 0 | 0 | 0 | 62.50 | 1.95 | 112.13 | 49.63 | 79.4% | 0 | — | — | 1 |

## By game

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_04_PIT_CLE | 4 | 3 | 1 | 0 | 0 | 515.22 | 8.75 | 481.79 | -33.43 | -6.5% | 3 | +0.0017 | 66.7% | 1 |
| KXNFLGAME-26OCT04INDWAS | 1 | 0 | 0 | 1 | 0 | 24.99 | 0.58 | — | — | — | 0 | — | — | 1 |
| KXNFLRECYDS-26OCT04ARINYG | 2 | 0 | 0 | 2 | 0 | 99.99 | 2.92 | — | — | — | 0 | — | — | 2 |
| KXNFLTD-26OCT04INDWAS | 1 | 1 | 0 | 0 | 0 | 37.49 | 0.82 | 53.93 | 16.44 | 43.8% | 0 | — | — | 1 |
| KXNFLTEAMTOTAL-26OCT04INDWAS | 1 | 1 | 0 | 0 | 0 | 62.50 | 1.95 | 112.13 | 49.63 | 79.4% | 0 | — | — | 1 |

## Orders

| week | game | family | side | contracts | price | stake | fees | result | gross | net | close | CLV/contract | CLV state | role | phase |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 2026_04_PIT_CLE | game_winner | YES | 247.14 | 0.59 | 150.00 | 4.18 | LOST | 0.00 | -150.00 | 0.595 | +0.0050 | CLV_VALID | OPEN | PRE_GAME |
| 4 | 2026_04_PIT_CLE | game_winner | NO | 247.14 | 0.97 | 240.23 | 0.50 | WON | 247.14 | 6.91 | 0.405 | — | NOT_AN_ENTRY_EXIT_OR_REDUCTION | CASHOUT_CLOSE | LIVE |
| 4 | 2026_04_PIT_CLE | series:KXNFLPASSINT | YES | 104.73 | 0.46 | 50.00 | 1.82 | WON | 104.73 | 54.73 | 0.455 | -0.0050 | CLV_VALID | OPEN | PRE_GAME |
| 4 | 2026_04_PIT_CLE | series:KXNFLRSHYDS | YES | 129.92 | 0.56 | 75.00 | 2.24 | WON | 129.92 | 54.92 | 0.565 | +0.0050 | CLV_VALID | OPEN | PRE_GAME |
| 4 | KXNFLGAME-26OCT04INDWAS | game_winner | YES | 36.99 | 0.66 | 24.99 | 0.58 | PENDING | — | — | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |
| 4 | KXNFLRECYDS-26OCT04ARINYG | series:KXNFLRECYDS | YES | 85.15 | 0.57 | 50.00 | 1.46 | PENDING | — | — | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |
| 4 | KXNFLRECYDS-26OCT04ARINYG | series:KXNFLRECYDS | YES | 85.15 | 0.57 | 50.00 | 1.46 | PENDING | — | — | — | — | NO_CANONICAL_CLOSE | ADD | UNKNOWN |
| 4 | KXNFLTD-26OCT04INDWAS | series:KXNFLTD | YES | 53.93 | 0.68 | 37.49 | 0.82 | WON | 53.93 | 16.44 | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |
| 4 | KXNFLTEAMTOTAL-26OCT04INDWAS | team_total | YES | 112.13 | 0.54 | 62.50 | 1.95 | WON | 112.13 | 49.63 | — | — | NO_CANONICAL_CLOSE | OPEN | UNKNOWN |

## RISK & CONCENTRATION

Governance reporting only: where the placed stake sat and how much of the result each exposure explains. Nothing here changes, recommends or caps a stake. Different tickers are not diversification: wagers are grouped by game, market, ladder (one underlying variable) and correlated cluster.

Net basis: **NONE COMPLETE** (preference net_canonical > net_fee_reconciled > net_profit_loss). No net basis covers every wager in scope; P&L figures are for the wagers that have one and are labelled incomplete.

| basis | wagers with figure | complete | stake | net P&L | ROI |
|---|---|---|---|---|---|
| net_canonical | 6 | NO | 740.20 | 32.64 | — |
| net_fee_reconciled | 6 | NO | 740.20 | 32.64 | — |
| net_profit_loss | 6 | NO | 740.20 | 32.64 | — |

Share of starting bankroll: NOT_AVAILABLE — no readable starting-bankroll evidence for the owner's account (the router's bankroll is a secret; nothing is guessed).

### Warnings

| code | subject | value | threshold | detail |
|---|---|---|---|---|
| CONCENTRATION_HIGH | 2026_04_PIT_CLE#1 | 69.6% | > 25.0% | one correlated cluster carries 69.6% of the scope's stake |
| CORRELATED_EXPOSURE_HIGH | 2026_04_PIT_CLE#1 | 69.6% | > 16.7% | 4 linked legs (OPPOSING_POSITION_PAIR, SAME_GAME_CORRELATED, SAME_MARKET) carry 69.6% of stake |
| CORRELATED_EXPOSURE_HIGH | 26OCT04INDWAS#1 | 16.9% | > 16.7% | 3 linked legs (SAME_GAME_CORRELATED) carry 16.9% of stake |
| OPPOSING_POSITION_PAIR | KXNFLGAME-26OCT01PITCLE-PIT | 52.7% | > 0.0% | YES and NO on one contract; 247.14 matched contracts at a combined 1.56 per contract fix that part's result at entry |
| SINGLE_GAME_DOMINATES_WEEK | 2026_04_PIT_CLE | 69.6% | > 33.3% | one game carries 69.6% of the scope's stake |

### Largest exposures

| exposure | which | stake | % of scope stake | % of bankroll |
|---|---|---|---|---|
| wager | KXNFLGAME-26OCT01PITCLE-PIT | 240.23 | 32.5% | NOT_AVAILABLE |
| game | 2026_04_PIT_CLE | 515.22 | 69.6% | NOT_AVAILABLE |
| market | KXNFLGAME-26OCT01PITCLE-PIT | 390.23 | 52.7% | NOT_AVAILABLE |
| ladder | KXNFLGAME-26OCT01PITCLE | 390.23 | 52.7% | NOT_AVAILABLE |
| cluster | 2026_04_PIT_CLE#1 | 515.22 | 69.6% | NOT_AVAILABLE |
| player | ARIJLOVE4 | 99.99 | 13.5% | NOT_AVAILABLE |

`% of net` is the group's net divided by the scope's net on that basis: when the scope lost, it is the group's share of the total loss (a winning group shows a negative share); shares sum to 100%.

### By correlated cluster

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) | links |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026_04_PIT_CLE#1 | 4 | 515.22 | 69.6% | -33.43 | -102.4% | -33.43 | -102.4% | -33.43 | -102.4% | OPPOSING_POSITION_PAIR, SAME_GAME_CORRELATED, SAME_MARKET |
| 26OCT04INDWAS#1 | 3 | 124.99 | 16.9% | 66.07 (partial) | 202.4% | 66.07 (partial) | 202.4% | 66.07 (partial) | 202.4% | SAME_GAME_CORRELATED |
| 26OCT04ARINYG#1 | 2 | 99.99 | 13.5% | — (partial) | — | — (partial) | — | — (partial) | — | SAME_MARKET |

### By game

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| 2026_04_PIT_CLE | 4 | 515.22 | 69.6% | -33.43 | -102.4% | -33.43 | -102.4% | -33.43 | -102.4% |
| 26OCT04INDWAS | 3 | 124.99 | 16.9% | 66.07 (partial) | 202.4% | 66.07 (partial) | 202.4% | 66.07 (partial) | 202.4% |
| 26OCT04ARINYG | 2 | 99.99 | 13.5% | — (partial) | — | — (partial) | — | — (partial) | — |

### By market family

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| game_winner | 3 | 415.22 | 56.1% | -143.09 (partial) | -438.4% | -143.09 (partial) | -438.4% | -143.09 (partial) | -438.4% |
| series:KXNFLRECYDS | 2 | 99.99 | 13.5% | — (partial) | — | — (partial) | — | — (partial) | — |
| series:KXNFLRSHYDS | 1 | 75.00 | 10.1% | 54.92 | 168.3% | 54.92 | 168.3% | 54.92 | 168.3% |
| team_total | 1 | 62.50 | 8.4% | 49.63 | 152.1% | 49.63 | 152.1% | 49.63 | 152.1% |
| series:KXNFLPASSINT | 1 | 50.00 | 6.8% | 54.73 | 167.7% | 54.73 | 167.7% | 54.73 | 167.7% |
| series:KXNFLTD | 1 | 37.49 | 5.1% | 16.44 | 50.4% | 16.44 | 50.4% | 16.44 | 50.4% |

### By ladder (underlying variable)

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLGAME-26OCT01PITCLE | 2 | 390.23 | 52.7% | -143.09 | -438.4% | -143.09 | -438.4% | -143.09 | -438.4% |
| KXNFLRECYDS-26OCT04ARINYG-ARIJLOVE4 | 2 | 99.99 | 13.5% | — (partial) | — | — (partial) | — | — (partial) | — |
| KXNFLRSHYDS-26OCT01PITCLE-PITJWARREN30 | 1 | 75.00 | 10.1% | 54.92 | 168.3% | 54.92 | 168.3% | 54.92 | 168.3% |
| KXNFLTEAMTOTAL-26OCT04INDWAS-IND | 1 | 62.50 | 8.4% | 49.63 | 152.1% | 49.63 | 152.1% | 49.63 | 152.1% |
| KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8 | 1 | 50.00 | 6.8% | 54.73 | 167.7% | 54.73 | 167.7% | 54.73 | 167.7% |
| KXNFLTD-26OCT04INDWAS-INDJTAYLOR28 | 1 | 37.49 | 5.1% | 16.44 | 50.4% | 16.44 | 50.4% | 16.44 | 50.4% |
| KXNFLGAME-26OCT04INDWAS | 1 | 24.99 | 3.4% | — (partial) | — | — (partial) | — | — (partial) | — |

### By market

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| KXNFLGAME-26OCT01PITCLE-PIT | 2 | 390.23 | 52.7% | -143.09 | -438.4% | -143.09 | -438.4% | -143.09 | -438.4% |
| KXNFLRECYDS-26OCT04ARINYG-ARIJLOVE4-15 | 2 | 99.99 | 13.5% | — (partial) | — | — (partial) | — | — (partial) | — |
| KXNFLRSHYDS-26OCT01PITCLE-PITJWARREN30-70 | 1 | 75.00 | 10.1% | 54.92 | 168.3% | 54.92 | 168.3% | 54.92 | 168.3% |
| KXNFLTEAMTOTAL-26OCT04INDWAS-IND25 | 1 | 62.50 | 8.4% | 49.63 | 152.1% | 49.63 | 152.1% | 49.63 | 152.1% |
| KXNFLPASSINT-26OCT01PITCLE-PITARODGERS8-1 | 1 | 50.00 | 6.8% | 54.73 | 167.7% | 54.73 | 167.7% | 54.73 | 167.7% |
| KXNFLTD-26OCT04INDWAS-INDJTAYLOR28-1 | 1 | 37.49 | 5.1% | 16.44 | 50.4% | 16.44 | 50.4% | 16.44 | 50.4% |
| KXNFLGAME-26OCT04INDWAS-IND | 1 | 24.99 | 3.4% | — (partial) | — | — (partial) | — | — (partial) | — |

### By player (parsable player props; not a partition of stake)

| group | wagers | stake | % stake | net (net_canonical) | % of net (net_canonical) | net (net_fee_reconciled) | % of net (net_fee_reconciled) | net (net_profit_loss) | % of net (net_profit_loss) |
|---|---|---|---|---|---|---|---|---|---|
| ARIJLOVE4 | 2 | 99.99 | 13.5% | — (partial) | — | — (partial) | — | — (partial) | — |
| PITJWARREN30 | 1 | 75.00 | 10.1% | 54.92 | 168.3% | 54.92 | 168.3% | 54.92 | 168.3% |
| PITARODGERS8 | 1 | 50.00 | 6.8% | 54.73 | 167.7% | 54.73 | 167.7% | 54.73 | 167.7% |
| INDJTAYLOR28 | 1 | 37.49 | 5.1% | 16.44 | 50.4% | 16.44 | 50.4% | 16.44 | 50.4% |

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
| 2026_04_PIT_CLE#1 | 4 | 69.6% | — | 3 | 1.36 | +0.0028 | POSITIVE | 113.59 | — | — |
| 26OCT04INDWAS#1 | 3 | 16.9% | — | 0 | — | — | — | — | — | — |
| 26OCT04ARINYG#1 | 2 | 13.5% | — | 0 | — | — | — | — | — | — |

### Rules and thresholds

* SAME_MARKET: identical market ticker (two orders on one contract are one exposure)
* OPPOSING_POSITION_PAIR: YES and NO held on the identical market ticker
* SAME_LADDER: different rungs of one underlying variable (same series + event [+ subject])
* SAME_GAME_CORRELATED: same game, both families in `same_game_linked_families` (default: every family; spread, game winner, team total, totals and player props on one game all settle on one game state)
* Thresholds (share of scope stake, strictly greater fires): CONCENTRATION_HIGH > 25.0% for one cluster; CORRELATED_EXPOSURE_HIGH > 16.7% for a cluster of ≥ 2 legs; SINGLE_GAME_DOMINATES_WEEK > 33.3% for one game; OPPOSING_POSITION_PAIR for any YES+NO pair above 0.0%. Same-game linked families: every family.
