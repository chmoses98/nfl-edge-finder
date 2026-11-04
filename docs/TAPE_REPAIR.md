# NFL trade-tape repair and coverage audit (#246) — research-only, read-only API

## Root cause of the 10,000-print truncation (audited in code, not assumed)
`scripts/kalshi/backfill.py` called `historical_trades(ticker, limit=1000, max_pages=10)` = 10 × 1,000 = **10,000 prints, newest first**, and stored `complete = ok and not e1`, which ignores the cap.
So the limit is **self-imposed by the collector, not an API limit**, and a capped tape was recorded as complete. In the published `trades/` feed 439 of 1,007 tapes have exactly 10,000 lines
(KXNFLGAME 420/658, KXNFLSPREAD 19/349). Because the newest prints are kept, the retained tape of a capped moneyline ticker is mostly **in-game**; pre-kickoff history is what is missing.
The live capture (`capture.py`) has a related, smaller defect: `max_pages=5` (5,000 prints per ticker per run); on a capped fetch the per-ticker cursor was not advanced, so later runs re-fetched the same newest prints and the older ones in the window were never recovered **and nothing recorded the hole**.

## What this change does
| piece | behaviour |
|---|---|
| `nfl_edge/kalshi/tape.py::fetch_tape` | pages `historical/trades?ticker&max_ts=<kickoff>` newest→oldest until the cursor is exhausted, a per-run page budget is hit, or a page fails. Failed page ⇒ the cursor is kept and retried (never skipped). `max_ts` is re-enforced client-side: **no post-start print is ever kept**. Duplicates (by `trade_id`) are dropped and counted; out-of-order pages are counted. `tape_complete` is true **only** when the cursor was exhausted without error |
| `final_status` / `hourly_candle_vs_tape` | per-ticker audit row: `COMPLETE`, `COMPLETE_WITH_SOURCE_GAP` (cursor exhausted but exchange candles show volume the tape lacks ⇒ an **irrecoverable window** is written), `INCOMPLETE_RESUMABLE` (page budget), `INCOMPLETE_ERROR`. Hourly candle `price.low/high/volume` are compared with the tape on pre-start hours |
| `scripts/kalshi/tape_repair.py` | resumable, bounded (`--budget`, `--page-budget`), additive outputs only: `trades_v2/<SERIES>/<TICKER>.jsonl`, `tape_meta.jsonl`, `tape_state.json`. The published `trades/` and `candles/` feeds are untouched |
| `.github/workflows/kalshi-tape-repair.yml` | manual dispatch; read-only public GET endpoints; publishes only new paths to `market-data`; bounded self-chain |
| `scripts/kalshi/capture.py` | capped live trade fetches now advance the cursor and record an explicit gap `{from,to,run_id}` in `state.trade_gaps`; a bounded gap-fill pass (`--max-gap-fills`) re-fetches `min_ts..max_ts` of the oldest gaps; manifests report `gaps_open` |
| `scripts/kalshi/tape_coverage_report.py` | family-level audit with explicit denominators (unique contracts ≠ horizon rows ≠ games), per-horizon two-sided pre-start quote counts, legacy tape cap counts, recovered-tape statuses, input hashes |

## Coverage BEFORE (market-data backfill, 2026-11-04; `docs/research/nfl_tape_coverage_before_2026-11-04.{json,md}`)
* 61,557 archived contracts in 381 series (61,068 settled with a `result` join).
* **54,364 horizon rows** (`backfill/horizons`, T-168h … T-0) of which **46,077 have a two-sided pre-start quote at ≥1 horizon**, across totals, team totals, halves and props — e.g. KXNFLTOTAL 4,825 of 5,918 contracts (4,134 at T-24h), KXNFLRECYDS 9,800/10,254, KXNFLPASSYDS 3,122/3,283, KXNFLRSHYDS 4,558/4,639, KXNFLSPREAD 5,312/7,420.
  Sift-alpha PR #25 called these families "outcome-only"; that was true of **candles and tape** (only 1,007 contracts have either: 658 moneyline + 349 spread) but **not** of price history: horizon snapshots already exist and were not used. They are one-quote-per-horizon (with stated `age_min`), not a tape.
* Tape: 1,007 legacy tapes, 439 capped at exactly 10,000 prints; recovered tape = 0.

## Coverage AFTER
Recovery requires the Kalshi API, which is **not reachable from the build sandbox** (HTTP 403 on the CONNECT tunnel). The collector is therefore verified by unit tests against a faithful paged fake (pagination past 25k prints, budget stop + resume, 429 mid-pagination, duplicate page boundaries, server ignoring `max_ts`, empty tape, side orientation, candle agreement and source-gap detection, gap bookkeeping) and **must be dispatched from GitHub Actions** (`Kalshi NFL tape repair`) to produce real "after" numbers; the workflow regenerates `tape_coverage.{json,md}` on `market-data` each run. No "after" numbers are claimed here.

## Still open / honest limits
* Whether the archive can return pre-kickoff history for every contract is unproven until the workflow runs; the status vocabulary above records the answer per ticker (`COMPLETE_WITH_SOURCE_GAP` = the source is exhausted yet candles show missing volume).
* Horizon rows carry no depth or queue; depth exists only from live capture (`yes_bid_size_fp` per quote and top-10 books for a subset of tickers).
* Player-prop tape recovery is not scheduled by default (volume is small, value is in the horizon quotes); add series to `--series` to include them.
* Realised maker/taker role and fee per own fill remain a private-ledger concern: nothing here reads or publishes personal orders.
