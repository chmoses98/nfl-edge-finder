# Close, CLV and settlement

## Two truths
* **SPORTS_TRUTH** (`tennis_edge/ledger/truth.py:SportsTruth`): winner, score, outcome type
  (COMPLETED/RETIRED/WALKOVER/DEFAULT/UNFINISHED/UNKNOWN), retiring player, sets/games completed, actual
  first ball / finish when known, source and confidence. Model scoring uses this and only when
  `gradeable_binary` (completed/retired/default with a winner and confidence >= 0.9).
* **EXCHANGE_TRUTH** (`ExchangeTruth`): Kalshi `result` (yes/no/scalar), `settlement_value_dollars`,
  `settlement_ts`, `expiration_value` verbatim. P/L, hypothetical or real, is computed from this only.
* `reconcile()` cross-checks them; a contradiction is a TENNIS-8/9 failure, never auto-resolved.

## Canonical close (`tennis_edge/ledger/close.py`)
CANONICAL_CLOSE = last EXECUTABLE quote (both sides present, 0 < bid <= ask < 1, from a market record,
orderbook top or candle bid/ask -- never a trade print, never a settlement value) strictly before the cutoff.
* cutoff = actual first ball when known (close_basis ACTUAL_FIRST_BALL);
* else scheduled_start - 5 min (close_basis SCHEDULED_MINUS_MARGIN) -- strict pregame evaluations exclude
  these rows; the report shows both bases separately;
* no quote before the cutoff -> no close. Nothing is synthesised.
Preserved with the close: yes/no bid/ask, mid, sizes, timestamp, seconds_to_cutoff.

CLV for a YES bought at the decision ask: midpoint CLV = close_mid - decision_ask; executable CLV =
close_bid - decision_ask (primary); raw movement = close_mid - decision_mid. Fees are never inside CLV.

## First-ball problem
Kalshi exposes `occurrence_datetime` (scheduled) and `close_time` (after the winner is declared) but no start.
Actual first-ball truth needs an external live-score feed (blocked from the sandbox; adapter interface
only). Until it exists every prospective close is labelled SCHEDULED_MINUS_MARGIN and TENNIS-10 reports the
basis breakdown. Price-path evidence (first large 1-minute candle move after the scheduled time) can bound
the start from above but is not used as truth.

## Bookmaker benchmark vs Kalshi close
tennis-data.co.uk prices are a separate, pre-match reference benchmark (capture time undocumented) used for
historical model-vs-market research; they are never substituted for Kalshi closes or CLV.
