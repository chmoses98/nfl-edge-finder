# TNF 2026 Week 3 ATL@GB — owner's actual positions, rebuilt as a position lifecycle

Accounting only. These are facts about the owner's bankroll, not model evidence, and not a recommendation.
Sources: `handicap-data` @ `38a999a` (imported_wagers + wager_settlements, week 3), canonical closes
(`market-data:data/shadow/v2/closes/`), and the 10-minute Kalshi capture's quotes and public trade tape
(`market-data:data/kalshi/capture/2026-09-2{4,5}/`). Generator: `nfl_edge/handicap/position_lifecycle.py`
(`docs/POSITION_LIFECYCLE.md`). Scheduled kickoff 2026-09-25T00:15:00Z; final ATL 35, GB 14.

## Correction to the published postmortem

The week-3 postmortem published before this change reported **6 wagers, 2 W / 4 L, 6 valid CLV observations,
mean CLV +0.0657**. Those figures counted orders, and they compared live entries and a live exit with the
pregame close. Corrected:

| measure | as published (orders) | corrected (positions) |
|---|---|---|
| independent positions | 6 | **5** |
| pregame thesis | (not distinguished) | **1** (ATL 1H team total ≥10, NO) |
| live thesis | (not distinguished) | **4** (3 opened 28 s–1 m 45 s after scheduled kickoff; GB ML at 01:59:59) |
| full cashouts | 0 | **1** (Love 275) |
| partial cashouts | 0 | 0 |
| held to settlement | 6 | 4 |
| valid pregame CLV observations | 6 (mean +0.0657, 33 % > 0) | **1** (−0.0050/contract) |
| cash P&L, all executions and fees | −49.71 | **−49.71** (unchanged — cash was always right) |

Season to date: 44 positions from 48 orders; 37 pregame / 7 live; 3 full cashouts (CLE/TB 1H total wk 2,
IND/KC KC-5 wk 2, Love 275 wk 3). Pregame entry CLV is 37 valid observations with a mean of −0.0051/contract
and 8.1 % positive. The published figure was 48 observations, mean −0.0111, 10.4 % positive. All 44 episodes
reconcile, to the cent, with the orders' own settlement figures.

## Chronological transaction ledger

YES axis: + means long YES, − means long NO. `BUY*` means the router did not deliver the verb; the side is
replayed as the exposure it states. The trade tape corroborates each order: a public trade at the same second,
with the same count and price, whose taker direction equals the recorded side.

| # | executed (UTC) | market | action | contract | qty | price | fee | before → after | role | phase | tape match |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 00:14:46 | KXNFL1HTEAMTOTAL…-ATL10 | BUY* | NO | 98.52 | 0.49 | 1.7235 | 0 → −98.52 | OPEN | PRE_GAME (−14 s) | 98.52 @ YES 0.51, taker no |
| 2 | 00:15:28 | KXNFLPASSYDS…-GBJLOVE10-275 | BUY* | YES | 91.41 | 0.26 | 1.2312 | 0 → +91.41 | OPEN | LIVE (+28 s, NEAR_SCHEDULED_KICKOFF) | 55.41 + 36.00 @ 0.26, taker yes |
| 3 | 00:16:21 | KXNFLRSHYDS…-GBKJOHNSON26-30 | BUY* | NO | 61.51 | 0.3896 | 1.0236 | 0 → −61.51 | OPEN | LIVE (+81 s, NEAR) | 27.51 + 10 + 20 + 4 @ YES 0.60–0.62, taker no |
| 4 | 00:16:45 | KXNFLRECYDS…-ATLDLONDON5-60 | BUY* | NO | 44.11 | 0.4359 | 0.7588 | 0 → −44.11 | OPEN | LIVE (+105 s, NEAR) | 4 + 10 + 20.11 + 10 @ YES 0.55–0.58, taker no |
| 5 | 01:59:59 | KXNFLGAME…-GB | BUY* | YES | 59.66 | 0.32 | 0.9088 | 0 → +59.66 | OPEN | LIVE | tape gap 01:50–02:05; quote 48 s old: ask 0.32 |
| 6 | 02:43:34 | KXNFLPASSYDS…-GBJLOVE10-275 | BUY* | NO | 91.41 | 0.67 | 1.4148 | +91.41 → 0 | **CASHOUT_CLOSE** | LIVE | 91.41 @ YES 0.33, taker no; taker fee reproduces 1.4148 exactly |

The in-play evidence for orders 2–4 comes from the GB moneyline tape. Its per-minute VWAP was flat at 0.69 from
00:05 to 00:14, then fell to 0.668 at 00:16 and 0.642 at 00:17, which is game-state trading. The actual first
snap is not captured, so these orders are LIVE by the repository's scheduled-kickoff standard and flagged
NEAR_SCHEDULED_KICKOFF.

## Position episodes

| position | opened | phase | side | opened qty | entry cost | exits | final qty | settlement | fees | realized trading | settlement P&L | total P&L | entry CLV | exit benchmark | class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ATL 1H ≥10 | 00:14:46 | PRE_GAME | NO | 98.52 | 50.00 | 0 | 98.52 | YES (ATL scored 17 1H) | 1.72 | 0.00 | −48.27 | **−50.00** | −0.0050 (close NO 0.485 vs 0.49) | — | PREGAME_POSITION_HELD_TO_SETTLEMENT |
| Love ≥275 pass yds | 00:15:28 | LIVE | YES | 91.41 | 25.00 | 1 full | 0 | (YES: 312 yds) | 2.65 | +6.40 | 0.00 | **+3.75** | N/A live entry | LIVE_EXIT_VALUE 0.00 (sold at YES 0.33 = bid 0.33, quote 18 s old) | LIVE_POSITION_FULL_CASHOUT_LIVE |
| K. Johnson ≥30 rush | 00:16:21 | LIVE | NO | 61.51 | 24.99 | 0 | 61.51 | NO (6 yds) | 1.02 | 0.00 | +37.55 | **+36.52** | N/A live entry | — | LIVE_POSITION_HELD_TO_SETTLEMENT |
| London ≥60 rec | 00:16:45 | LIVE | NO | 44.11 | 19.99 | 0 | 44.11 | YES (194 yds) | 0.76 | 0.00 | −19.23 | **−19.99** | N/A live entry | — | LIVE_POSITION_HELD_TO_SETTLEMENT |
| GB moneyline | 01:59:59 | LIVE | YES | 59.66 | 20.00 | 0 | 59.66 | NO (ATL won) | 0.91 | 0.00 | −19.09 | **−20.00** | N/A live entry (entry at the 0.32 ask) | — | LIVE_POSITION_HELD_TO_SETTLEMENT |
| **total** | | | | | 139.97 | | | | 7.06 | +6.40 | −49.05 | **−49.71** | 1 valid | 1 valued | |

## The cashout, economically

- Entry: 91.41 YES at 0.26 = 23.77, plus a 1.23 fee, for 25.00 cash.
- Exit: bought 91.41 NO at 0.67, which on Kalshi's netted book is selling the YES at 0.33. Proceeds were 30.17
  before a 1.41 fee.
- Realized trading P&L: (0.33 − 0.26) × 91.41 = +6.40. Net of both fees: **+3.75**, identical to the filed
  YES +66.41 plus NO −62.66.
- Exit quality: the sale hit the prevailing bid (YES bid 0.33 in the capture 18 s before), so the live exit
  value was 0.00/contract before the fee. The tape traded at 0.30–0.33 over the next minute.
- Hindsight only (not exit quality, not in P&L): Love finished with 312 yards and the rung settled YES.
  Holding would have paid 91.41, which is **61.24 more** than the cashout. The price was 0.48 at 02:50, 0.78
  at 02:52 and 0.99 by 03:09.
- The owner's stated reason, "I didn't think it was going to hit", is a live re-assessment of a live position.
  It is not a second, opposing thesis.

## IND@KC (week 2): $1,050 vs $2,792

| quantity | value | what it is |
|---|---|---|
| gross transaction volume (Σ order stakes) | **2,792.46** | turnover: 999.9987 + 49.9944 + 1,742.4686 |
| original cash outlay | **1,049.99** | KC-5 YES 1,794.08 @ 0.54 = 968.80 + fee 31.20 = 999.9987; Walker TD YES 79.78 @ 0.61 + fee = 49.9944 |
| additional cash added | 0.00 | no adds |
| max simultaneous capital at risk (= max loss) | **1,049.99** | from 00:18:22Z, when both positions were open |
| cashout proceeds | 53.82 | KC-5 closed at 03:52:15 by buying 1,794.08 NO @ 0.97, i.e. selling the YES at 0.03 (fee 2.21) |
| recycled capital in volume | 1,742.47 | the NO leg's "stake", which closed the YES position rather than adding risk |
| contract notional at peak | 1,873.86 | contracts × $1 |
| total P&L | −998.38 | KC-5 −948.39, Walker TD −49.99 |

The owner's ~$1,050 is exactly both the original cash outlay and the peak capital at risk. The $2,792 counts
the cashout leg as if it were a new stake. The CLE/TB 1H total position (week 2) follows the same pattern:
246.08 YES, then 246.08 NO at 18:08, a full cashout.

## Anti-chase governance (reporting only)

For the season, `STAKE_ESCALATION_AFTER_LOSS` fired twice in week 2. A $250 JAC moneyline and then a $1,000
KC-5 position both opened after the CLE/TB 1H-total cashout had realized a loss on a $115 position.
`CORRELATED_EXPOSURE_HIGH` fired on six games with at least 3 positions each; ATL@GB had 5. These flags
describe the timeline only. They block nothing and size nothing.

## Limits

- The buy/sell verb was not delivered for any filed order. It is inferred from the side and corroborated by the
  tape where the tape has the trade. The router now sends it (`execution_action`, kalshi-bet-router #94).
- Actual kickoff is not captured, so phase uses scheduled kickoff.
- The GB moneyline's 01:59:59 trade falls in a tape gap. The live-entry comparison uses a quote 48 s old.
- Settlement loss times are not captured, so the anti-chase flags use trading exits only and can under-fire.
