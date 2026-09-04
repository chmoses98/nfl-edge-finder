# 2025 Kalshi NFL market-efficiency map

**Status: INTERIM.** This covers only the 802 kickoff-anchored markets whose raw candles were already cached
locally (KXNFLGAME moneylines, KXNFLSPREAD ladders) — 259 games of moneyline and 18 games of spread ladder.
The full 54k-market backfill is refetching after the parse bug below and this file will be regenerated.
Nothing here is an edge, and nothing here is close to significant.

Reproduce: `python3 scripts/research/efficiency_map.py '<horizons glob>'`

## Two errors found and fixed before any of these numbers were believed

**1. Every price in the first backfill was null.** `snapshot()` read `yes_bid.close_dollars` and `volume_fp`;
the candlestick endpoint returns `yes_bid.close` and `volume`. The run produced 54,364 rows that were
structurally valid, carried correct `result` and `anchor_ts`, reported `n_candles > 0`, and contained no
prices whatsoever. Nothing downstream objected. Guards added: a frozen real-response fixture in
`tests/test_candle_parsing.py`, and a chunk abort (rc=4) if under 20% of the first 200 markets yield a quote.

**2. A fifth of the sample was post-game, and it looked like brilliance.** Horizons are offsets from an
anchor. Where a market could not be matched to an nflverse kickoff, the anchor fell back to the market's
*close* time — so its "T-0" quote was taken *after* the game finished. 65% of those quotes sat at settled
certainty (under 2c or over 98c) versus 0% of kickoff-anchored ones. Including them made closing-price Brier
fall from 0.218 to 0.171 and made the market look increasingly clairvoyant toward kickoff. The efficiency map
now drops every non-kickoff anchor (`tests/test_horizon_pregame.py`), and the effect disappears entirely.

A third, smaller error: `np.sign(0) == 0`, so unchanged quotes were being scored as "moved away from the
outcome". With a median quote change of a penny that alone pushed the share moving toward the outcome to
0.367 ± 0.030 — a 4-sigma "finding" that was pure tie-handling. Unchanged quotes are now excluded and counted.

## What the pregame sample actually shows

### Moneyline (KXNFLGAME, 259 games, both sides)

| horizon | n | median width | Brier (mid) |
|---|---|---|---|
| T-168h | 476 | 0.030 | 0.2176 |
| T-72h | 518 | 0.010 | 0.2152 |
| T-24h | 518 | 0.010 | 0.2154 |
| T-6h | 518 | 0.010 | 0.2161 |
| T-90m | 518 | 0.010 | 0.2160 |
| T-0 | 518 | 0.010 | 0.2150 |

The moneyline is **flat**. Brier at T-0 (0.2150) is indistinguishable from Brier a week out (0.2176), and the
quoted spread reaches its floor of one cent by T-72h and stays there. On this sample there is no
"information accumulates toward kickoff" effect to exploit and no widening to trade around.

### Spread ladders (KXNFLSPREAD, 18 games)

Brier improves 0.157 (T-72h) → 0.144 (T-0) and width tightens 0.030 → 0.010. Eighteen games. This is
suggestive of the ladders being genuinely less settled early, and it is far too small to lean on — it is
listed so the full rerun has something to confirm or kill.

### Calibration — the only question the FDR was spent on

Whether a contract quoted at *p* settles at rate *p*, by family × horizon × price bucket, with standard
errors clustered on game (both sides of a game are one outcome; a ladder is one performance).

**20 tests, Benjamini-Hochberg at q = 0.10, zero significant.** The largest deviation is
`GAME_WINNER T-72h [0.35,0.50)`: +0.056 ± 0.044, p = 0.20.

At the close, favourites priced 0.65–0.80 won 66.7% against a 72.3% mid, and dogs priced 0.20–0.35 won 33.0%
against a 27.6% mid. That is the *reverse* of the classic favourite-longshot bias, it is one finding rather
than two (the buckets are the same ~100 games seen from both sides), and it is 1.2 standard errors. It is
noise. It is written down only so the full rerun tests it out of sample rather than rediscovering it.

### Cost to cross

Buying at the ask and holding to settlement loses **2.3–2.7% per contract** at every horizon from T-72h in,
net of the Kalshi taker fee, and it loses that on *both* sides — the two are near-mirror images because
within a game the two sides' losses sum to the overround. At T-168h the cost roughly doubles (−5.4%) on the
wider early book.

This is worth stating precisely because it is the hurdle: **a model must beat the market's midpoint by more
than ~2.5 points of probability before crossing the spread breaks even**, and a naive significance test of
"is the mean execution return non-zero" returns p ≈ 0 for nearly every cell. That is not an inefficiency
finding, it is a market maker charging a spread, which is why the FDR budget is not spent there.

### Price movement

| window | markets | unchanged | of those that moved, share toward the outcome | Brier |
|---|---|---|---|---|
| T-72h → T-0 | 800 | 12% | 0.516 ± 0.035 | 0.195 → 0.190 |
| T-24h → T-0 | 800 | 16% | 0.532 ± 0.032 | 0.194 → 0.190 |
| T-6h → T-0 | 802 | 21% | 0.534 ± 0.033 | 0.194 → 0.190 |
| T-24h → T-6h | 800 | 30% | 0.525 ± 0.037 | 0.194 → 0.194 |

Late movement is weakly informative — about 53% of moves point the right way, roughly one standard error
above a coin flip, with mean absolute moves of 1–3 cents. Consistent with a market that is already close to
its final answer three days out.

## Limitations

* 259 moneyline games and 18 spread games, one season. Player props, totals, team totals and every period
  market are absent until the refetch lands — and those are the families where the shadow ledger's largest
  model-market disagreements sit, so this map does not yet speak to them at all.
* Quotes are candle closes, so the reconstructed book is the book at the end of the minute or hour, not at
  the instant. Sub-minute execution is not represented.
* Volume is per-candle and mostly zero on these series, so the liquidity axis (does efficiency vary with
  liquidity?) is not yet answerable and is deliberately left out rather than reported from near-empty data.
* No adjustment for the possibility that the cached subset — the two series cached first — is unrepresentative.
