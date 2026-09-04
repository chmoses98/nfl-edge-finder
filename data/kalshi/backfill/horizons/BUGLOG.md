# horizons/ rebuild log

## 2026-09-04 — full rebuild after a null-price parse bug

The first quote backfill (runs through 2026-09-04T17:00Z) wrote 54,364 rows in which **every price field was
null**. `snapshot()` read `yes_bid.close_dollars` / `volume_fp`; the candlestick endpoint returns
`yes_bid.close` / `volume` / `open_interest`. Every row was structurally valid, carried correct metadata
(`result`, `anchor_ts`, `n_candles` > 0) and contained no prices, so nothing downstream objected.

Those rows were deleted rather than kept: they hold no information that is not reproduced by the rerun, and
leaving them invites someone to build a study on 54k empty quotes. The failure itself is recorded here and in
`docs/KALSHI_API_NOTES.md`.

Guards added with the fix:
* `tests/test_candle_parsing.py` pins the parser to a frozen real API response (`tests/fixtures/`).
* `backfill_quotes.py` aborts with rc=4 if fewer than 20% of the first 200 markets in a chunk yield a quote.
* `snapshot()` accepts both field spellings, and flags `book_empty` (bid 0.00 / ask 1.00) instead of
  reporting it as a tradable 100-cent spread.
