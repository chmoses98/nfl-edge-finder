# Owner actual placed wagers — season 2026, week 3

> OWNER ACTUAL PLACED WAGERS -- ACCOUNTING ONLY. Every wager here was placed by the owner and recommended by nothing in this repository. These are real-money facts about a bankroll, not evidence about any model, and they are never used to train or tune one. Counts are small; no rate below establishes an edge.

Stake is contracts x execution price PLUS the entry fee the exchange charged on the fills; `fees` is that entry fee. Net P&L is the router's settlement figure: gross return - stake - settlement fee (settlement fees on established wagers: 0.00). CLV is per contract on the side held, against the canonical close of the exact contract, excluding fees.

## Totals

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 6 | 2 | 4 | 0 | 0 | 202.63 | 7.06 | 152.92 | -49.71 | -24.5% | 6 | +0.0657 | 33.3% | 0 |

ECONOMICS: figures above are CANONICAL -- the settlement as amended, where an append-only amendment corrected it (0 amended; versions {'router-settlement-economics.v2': 6}). As ORIGINALLY RECORDED, net P&L: -49.71. The exchange evidence and the filed settlements are unchanged; an amendment sits beside the record it supersedes.

FEE RECONCILIATION (a finding, not a rewrite). Kalshi's settlement `fee_cost` equals, to the cent, the entry fees already inside the stakes on every reconciled position, so the recorded net subtracts the trading fee twice. Recorded net stays as filed; the reconciled net is gross - stake where the exchange's own figures prove that equality (0 of 6 established wagers). Not every established wager reconciles, so no fee-reconciled total is stated.

## By week

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 6 | 2 | 4 | 0 | 0 | 202.63 | 7.06 | 152.92 | -49.71 | -24.5% | 6 | +0.0657 | 33.3% | 0 |

## By market family

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| game_winner | 1 | 0 | 1 | 0 | 0 | 20.00 | 0.91 | 0.00 | -20.00 | -100.0% | 1 | +0.3650 | 100.0% | 0 |
| series:KXNFL1HTEAMTOTAL | 1 | 0 | 1 | 0 | 0 | 50.00 | 1.72 | 0.00 | -50.00 | -100.0% | 1 | -0.0050 | 0.0% | 0 |
| series:KXNFLPASSYDS | 2 | 1 | 1 | 0 | 0 | 87.66 | 2.65 | 91.41 | 3.75 | 4.3% | 2 | +0.0350 | 50.0% | 0 |
| series:KXNFLRECYDS | 1 | 0 | 1 | 0 | 0 | 19.99 | 0.76 | 0.00 | -19.99 | -100.0% | 1 | -0.0109 | 0.0% | 0 |
| series:KXNFLRSHYDS | 1 | 1 | 0 | 0 | 0 | 24.99 | 1.02 | 61.51 | 36.52 | 146.2% | 1 | -0.0246 | 0.0% | 0 |

## By game

| group | wagers | W | L | pending | P&L unestablished | stake | fees | gross return | net P&L | ROI | CLV valid | mean CLV/contract | CLV>0 | no close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026_03_ATL_GB | 6 | 2 | 4 | 0 | 0 | 202.63 | 7.06 | 152.92 | -49.71 | -24.5% | 6 | +0.0657 | 33.3% | 0 |

## Wagers

| week | game | family | side | contracts | price | stake | fees | result | gross | net | close | CLV/contract | CLV state |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 2026_03_ATL_GB | series:KXNFL1HTEAMTOTAL | NO | 98.52 | 0.49 | 50.00 | 1.72 | LOST | 0.00 | -50.00 | 0.485 | -0.0050 | CLV_VALID |
| 3 | 2026_03_ATL_GB | game_winner | YES | 59.66 | 0.32 | 20.00 | 0.91 | LOST | 0.00 | -20.00 | 0.685 | +0.3650 | CLV_VALID |
| 3 | 2026_03_ATL_GB | series:KXNFLPASSYDS | NO | 91.41 | 0.67 | 62.66 | 1.41 | LOST | 0.00 | -62.66 | 0.755 | +0.0850 | CLV_VALID |
| 3 | 2026_03_ATL_GB | series:KXNFLPASSYDS | YES | 91.41 | 0.26 | 25.00 | 1.23 | WON | 91.41 | 66.41 | 0.245 | -0.0150 | CLV_VALID |
| 3 | 2026_03_ATL_GB | series:KXNFLRECYDS | NO | 44.11 | 0.43594423033325774 | 19.99 | 0.76 | LOST | 0.00 | -19.99 | 0.425 | -0.0109 | CLV_VALID |
| 3 | 2026_03_ATL_GB | series:KXNFLRSHYDS | NO | 61.51 | 0.38959518777434565 | 24.99 | 1.02 | WON | 61.51 | 36.52 | 0.365 | -0.0246 | CLV_VALID |

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
| 2026_03_ATL_GB#1 | 6 | 100.0% | 100.0% | 6 | 25.69 | +0.0575 | POSITIVE | -68.34 | 7.06 | -49.71 |

### Rules and thresholds

* SAME_MARKET: identical market ticker (two orders on one contract are one exposure)
* OPPOSING_POSITION_PAIR: YES and NO held on the identical market ticker
* SAME_LADDER: different rungs of one underlying variable (same series + event [+ subject])
* SAME_GAME_CORRELATED: same game, both families in `same_game_linked_families` (default: every family; spread, game winner, team total, totals and player props on one game all settle on one game state)
* Thresholds (share of scope stake, strictly greater fires): CONCENTRATION_HIGH > 25.0% for one cluster; CORRELATED_EXPOSURE_HIGH > 16.7% for a cluster of ≥ 2 legs; SINGLE_GAME_DOMINATES_WEEK > 33.3% for one game; OPPOSING_POSITION_PAIR for any YES+NO pair above 0.0%. Same-game linked families: every family.
