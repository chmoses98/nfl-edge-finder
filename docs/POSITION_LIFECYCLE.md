# Position lifecycle: transactions are not bets

`nfl_edge/handicap/position_lifecycle.py`, rendered first in every OWNER ACTUAL PLACED WAGERS postmortem
(`data/handicap/actual_wagers/` on `market-data`). Derived, reporting only: no record on `handicap-data` is
changed, nothing reads or feeds a model, nothing sizes, blocks or recommends a wager.

## Why

`imported_wagers` holds one record per ORDER. On TNF 2026-09-24 (ATL@GB) the owner bought 91.41 YES on
`KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275` at 0.26 and later "cashed out because I didn't think it was going to
hit": 91.41 NO at 0.67. The ledger holds two records, YES WON +66.41 and NO LOST -62.66, and the postmortem
reported "6 wagers, 2-4, 6 valid CLV observations". Kalshi keeps one signed position per market, so buying NO
while long YES *reduces* the YES position. It was one position with one P&L (+3.75). Week 2 had the same
pattern twice (CLE/TB 1H total 246.08, IND/KC KC-5 1794.08).

## Model

Orders on one market are replayed in time order on the signed YES axis (+ long YES, - long NO):

| role | meaning |
|---|---|
| OPEN | from flat |
| ADD | same direction, larger |
| REDUCE | same direction, smaller: a PARTIAL cashout |
| CASHOUT_CLOSE | to flat by trading: a FULL cashout |
| REVERSE | through zero (closes one episode, opens another; the fee is not split) |
| SETTLEMENT | the exchange closed what remained |

An EPISODE (flat to flat) is one independent position. Phase is by the repository's pregame boundary, the
SCHEDULED kickoff (the canonical close is the last valid observation strictly before it): PRE_GAME, LIVE,
POST_FINAL, UNKNOWN. A transaction within 10 minutes after scheduled kickoff is flagged
`NEAR_SCHEDULED_KICKOFF` because the actual first snap is not captured.

Classifications: `PREGAME_POSITION_HELD_TO_SETTLEMENT`, `PREGAME_POSITION_FULL_CASHOUT_LIVE`,
`PREGAME_POSITION_PARTIAL_CASHOUT_LIVE`, `LIVE_POSITION_HELD_TO_SETTLEMENT`, `LIVE_POSITION_FULL_CASHOUT_LIVE`, …
A pregame position cashed out live stays ONE pregame thesis with a live exit. `LIVE_HEDGE` across different
markets is not classified: direction across different contracts is not modelled, and inventing it would be
a guess.

## What is measured where

* **Entry quality**: `PRE_GAME_ENTRY_CLV` = canonical close of the held side - price paid, over the episode's
  pregame OPEN/ADD quantity; one observation per episode. Live entries: `NOT_APPLICABLE_LIVE_ENTRY` (compared
  descriptively with the contemporaneous quote, never called CLV).
* **Exit quality**: `LIVE_EXIT_VALUE` = exit price vs the contemporaneous executable quote (YES bid when
  selling YES, YES ask when buying it back), from the 10-minute capture, when the quote is at most 300 s old;
  otherwise `NO_VALID_LIVE_EXIT_BENCHMARK` with the reason. Exits are never compared with the pregame close.
* **Hindsight** (`hindsight_cashout_vs_hold`): what the exited contracts would have paid at settlement. Shown,
  labelled, never in P&L, never exit quality.
* **Cash P&L**: every execution and every fee. Computed twice per episode (lifecycle: realized trading +
  settlement - fees; orders: Σ gross - stake) and reconciled to the cent.

The order-level tables remain, relabelled *transactions*; exits and live entries there carry
`NOT_AN_ENTRY_EXIT_OR_REDUCTION` / `NOT_APPLICABLE_LIVE_ENTRY` and are not counted in CLV.

## Exposure vocabulary

| quantity | definition |
|---|---|
| ORIGINAL CASH OUTLAY | stake (cost + entry fee) of every OPEN |
| ADDITIONAL CASH ADDED | stake of every ADD |
| CASHOUT PROCEEDS | held-side price x quantity of every exit, before its fee |
| GROSS TRANSACTION VOLUME | Σ order stakes. Turnover, **not** risk |
| RECYCLED CAPITAL IN VOLUME | volume - outlay - added (the exit legs' stakes) |
| MAX SIMULTANEOUS CAPITAL AT RISK | peak cost basis (+ fees) of everything open at once = max loss for binary longs |
| CONTRACT NOTIONAL AT PEAK | contracts x $1 at that peak |

IND@KC week 2: volume **2,792.46**; original cash outlay **1,049.99** (KC-5 YES 999.9987 + Walker TD 49.9944) =
max simultaneous capital at risk; the KC-5 NO leg (1,742.47) was the close of the KC-5 YES position at YES 0.03,
not new risk.

## The buy/sell verb

The router's production path used Kalshi's `outcome_side` (the CONTRACT traded) as the side. For a buy that is
the exposure; for a SELL it inverts it. The router now derives side from the exposure (a SELL of YES at p is
recorded as NO at 1 - p, cash-identical on Kalshi's netted book) and sends `execution_action` (BUY/SELL).
The NFL record accepts it as optional evidence (not identity; absent from older records, which keep their bytes).
Records without it are replayed with `action_source = SIDE_AS_EXPOSURE_V1`. Every 2026 NFL order that could be
matched to the public trade tape at its second (count and price) showed the taker direction equal to the
recorded side, so no filed record is a mis-recorded sell.

## Anti-chase governance (reporting only)

`CHASE_RISK` (a new position in a game after a realized trading loss in that game), `STAKE_ESCALATION_AFTER_LOSS`
(outlay > 1.5x the last realized loser), `REPEATED_ADD_AFTER_ADVERSE_MOVE` (an ADD below the average entry on the
held side), `SINGLE_GAME_EXPOSURE_HIGH` (one game's peak capital > 50% of the sum of per-game peaks),
`CORRELATED_EXPOSURE_HIGH` (≥ 3 episodes on one game). A loss is "known" at a trading exit's timestamp only;
settlement loss times are not captured, so flags can under-fire but never invent a visible loss. Past P&L never
changes a probability and a past loss never raises a stake; nothing here blocks or sizes.
