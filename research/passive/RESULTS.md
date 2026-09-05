# Can passive execution monetize the timing signal? On the core game markets: no.

Reproduce: `python3 scripts/research/passive_backtest.py`
Artifacts: `research/passive/passive_orders_2025.parquet`, `passive_results.json`

Session 3 established that the model is slightly early but the signal (+0.002 probability points of CLV) is
~7% of the half-spread when crossing. The remaining economic question was whether resting passively could
capture enough price improvement to make that survive. Four findings, in the order they bite.

## 0. Maker fees apply to exactly the markets we would trade

From captured API metadata in `config/kalshi_nfl_series.json`, not assumption. Across 392 NFL series there
are two fee regimes:

| fee_type | series | meaning |
|---|---|---|
| `quadratic` | 367 | taker fee only |
| `quadratic_with_maker_fees` | 25 | taker fee **and** a maker fee |

The 25 maker-fee series include **every headline NFL market**: `KXNFLGAME`, `KXNFLSPREAD`, `KXNFLTOTAL`,
`KXNFLANYTD`, `KXNFLFIRSTTD`, `KXNFL2TD`. The 98 fee-free `FULL_MICROSTRUCTURE` series are the period and
quarter derivatives. Passive entry on the markets this project studies is **not free**.

The maker *coefficient* is not in the captured metadata — only the fee type — so it is carried as an explicit
uncertain parameter and every economic result below is swept across 0, 0.0025, 0.005 and 0.01 per contract
rather than reported at one assumed value.

## 1. On these books there is usually no passive level to take

Across 3,208 decision-time book observations (804 markets, at T−3h, T−90m, T−60m, T−30m):

| quoted spread | share |
|---|---|
| exactly 1 cent | **86.2%** |
| ≥ 2 cents (a passive level exists at all) | **8.8%** |

Median spread 0.010, p75 0.010, p90 0.020. **The book is already at the minimum tick most of the time.** You
cannot improve on a one-cent spread — improving would cross it — so for 86% of observations the entire
strategy is undefined before any question of fills arises. That is a structural property of these markets,
not a sampling artefact, and it is why the usable study collapses from 1,007 markets to **174 markets across
73 games**.

## 2. Touch is not fill, and the gap is enormous

For the 8.8% of books where a passive level exists, hypothetical resting orders with a 30-minute horizon:

| level | orders | touch rate | **trade-at-level rate** | median volume at/through | median seconds to trade |
|---|---|---|---|---|---|
| join_bid | 562 | 98.2% | **3.6%** | 365 | 1268 |
| improve_bid | 562 | 100.0% | **26.7%** | 428 | 594 |

The quoted book reaches our level essentially always. A trade actually printing at or through it with the
taker hitting our side happens 3.6% of the time when joining the bid and 26.7% when improving it. Anyone
equating touch with fill would overstate opportunity by a factor of roughly 27× at the join level.

And even 26.7% is an **upper bound on our own fill**: Kalshi's historical trade feed gives price, size, time
and which side the taker hit, but no order identity or queue priority. Some of that 428-contract median
volume would have been ahead of us. Nothing here is called a fill.

## 3. The orders that would have filled are the losing ones

Markout from the trade instant, in our position's direction (improve_bid, n=150):

| +1m | +5m | +10m | +30m | +60m | close |
|---|---|---|---|---|---|
| −0.0035 | −0.0018 | −0.0027 | −0.0041 | **−0.0154** | −0.0040 |

Negative at every horizon and worst at an hour. The price moves against us after the moment we would have
been filled.

Gross P&L to settlement, splitting the same candidate orders by whether they were reachable:

| level | group | n | gross P&L | z |
|---|---|---|---|---|
| improve_bid | **trade-at-level** | 150 | **−0.0287** | −1.62 |
| improve_bid | not reachable | 412 | **+0.0110** | +1.74 |
| join_bid | not reachable | 542 | **+0.0168** | +4.45 |

Reachable minus non-reachable, clustered on game: **−0.0396 ± 0.0237 (z = −1.67)** for improve_bid and
**−0.1798 ± 0.0873 (z = −2.06)** for join_bid. By side, the effect is on the YES side (−0.0825 ± 0.0476)
and absent on NO (+0.0028 ± 0.0581).

This is the textbook signature of adverse selection: **the orders that get hit are the ones that were wrong,
and the orders left unfilled are the ones that were right.** A one-cent price improvement is being paid for
with roughly three cents of selection.

## 4. Economics at the upper bound

| level | n | gross | net @0.0000 | net @0.0025 | net @0.0050 | net @0.0100 |
|---|---|---|---|---|---|---|
| improve_bid | 150 | −0.0287 | −0.0287 | −0.0312 | −0.0337 | −0.0387 |

Negative before any maker fee, and the fee only deepens it. The result does not depend on resolving the
maker-coefficient uncertainty.

## Verdict, and its limits

For `KXNFLGAME` and `KXNFLSPREAD` — the only 2025 series with cached minute candles and a full trade feed —
**passive execution fails on all three counts at once**: the level usually does not exist (86% one-cent
books), it rarely trades when it does (3.6–26.7%), and when it does trade the order is adversely selected
(−0.0287 gross, markout negative at every horizon). Maker fees make it worse. Session 3's timing signal
cannot be rescued this way on these markets.

**What this does not settle.** The sample is 174 markets across **73 games**, and the individual contrasts
are 1.6–2.1 standard errors — directionally consistent and underpowered. More importantly it covers **game
markets only**. Player-prop books ran a median 5–6 cents wide in session 3, so a passive level exists there
far more often than 8.8% of the time, and the structural objection in finding 1 may not apply. There is no
2025 candle or trade archive for prop series, so that cannot be tested retrospectively — it is registered as
`H-20260904-023` for prospective measurement, where the live capture already records `yes_bid_size_fp` and
`yes_ask_size_fp` and depth-10 books arm automatically 72 hours before kickoff.
