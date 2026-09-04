# 2025 Kalshi NFL market-efficiency map

Reproduce: `python3 scripts/research/efficiency_map.py '<horizons glob>'`
Artifacts: `results.json` (current), `results_partial_16pct.json`, `results_cached_subset.json`.

**Status: INTERIM, on a biased sample.** 8,603 kickoff-anchored markets across 10 families and 67,408
executable quote snapshots — but that is 16% of the 54,364-market universe, and it is **not a random 16%**.
The backfill processes markets newest-first, so what has landed is weighted toward late-season and playoff
games, and toward four of six shards. Everything below must be re-run on the full set before it is believed.
Nothing here is an edge.

## Method

Every number is measured on **executable** prices: `ask` is what a YES buyer pays, `bid` what a YES seller
receives. Midpoints appear only where the midpoint itself is the object of study. Returns are net of the
Kalshi taker fee, `ceil(0.07·p·(1−p)·100)/100`. Standard errors are **clustered on game** — both sides of a
game are one outcome and a twelve-rung player ladder is one performance, so unclustered errors here run
1.5–2× too small. Multiplicity is handled by Benjamini–Hochberg at q = 0.10 across all 136 calibration cells.

The FDR budget is deliberately **not** spent on "is the mean execution return non-zero". That is the
overround, it is nearly deterministic, and testing it returns p ≈ 0 for almost every cell while saying only
that a market maker charges a spread. It is reported as a cost table instead.

## The headline: the biases are real and the spread eats all of them

Seven of 136 calibration tests survive FDR. The two economically interesting ones:

| cell | n | games | bias (obs − mid) | clustered SE | z |
|---|---|---|---|---|---|
| FIRST_TD_SCORER, closing price 0.10–0.20 | 93 | 44 | **−0.0716** | 0.0219 | 3.3 |
| PLAYER_STAT receptions, 0.35–0.50 (T−6h) | 363 | 57 | **+0.0874** | 0.0283 | 3.1 |

First-touchdown-scorer contracts quoted between 10 and 20 cents settle **7.5%** of the time against a 14.7
cent midpoint — a classic longshot overpricing, and the largest single miscalibration found. Buying those
costs −0.186 per contract net; the NO side is where the bias points.

And yet **no family × horizon cell has a positive expected return from crossing the spread.** The one
positive number anywhere in the study is the NO side of the receiving-yards tail: **+0.0258 ± 0.0308** —
0.8 standard errors from zero. Its calibration bias is genuine (−0.0755 ± 0.0303, 2.5 SE: high receiving-yards
rungs settle 7.5 points less often than quoted) and the quoted spread plus fee still consumes it.

That is the central result. **A real, statistically significant miscalibration is not the same as a tradable
one**, and on this exchange the gap between the two is roughly the width of the book.

## Favourite/longshot structure at the close (bias = observed − midpoint, clustered SE)

| family | price bucket | n | games | mid | observed | bias |
|---|---|---|---|---|---|---|
| FIRST_TD_SCORER | 0.02–0.05 | 299 | 61 | 0.030 | 0.057 | +0.0269 ± 0.0114 |
| FIRST_TD_SCORER | 0.10–0.20 | 93 | 44 | 0.147 | 0.075 | **−0.0716 ± 0.0219** |
| PLAYER_STAT | 0.20–0.35 | 1378 | 60 | 0.269 | 0.261 | −0.0083 ± 0.0166 |
| PLAYER_STAT | 0.35–0.50 | 1162 | 60 | 0.424 | 0.421 | −0.0028 ± 0.0198 |
| PLAYER_STAT | 0.50–0.65 | 950 | 59 | 0.561 | 0.525 | −0.0359 ± 0.0257 |
| PLAYER_STAT | 0.65–0.80 | 624 | 58 | 0.716 | 0.675 | −0.0414 ± 0.0233 |
| PLAYER_STAT | 0.80–0.90 | 250 | 55 | 0.842 | 0.796 | −0.0465 ± 0.0323 |
| TOTAL | 0.35–0.50 | 77 | 49 | 0.420 | 0.312 | −0.1085 ± 0.0580 |

Player props are well calibrated through the middle of the price range and drift **negative at the top**:
contracts quoted above 0.50 settle 3.6 to 4.7 points less often than priced, consistently in sign across four
adjacent buckets though individually only 1.4–1.8 SE. Aggregating those four buckets is the obvious next test
and is deliberately left for the full sample rather than run now on a favourable subset.

## Player ladder tails

| stat | rung bucket | n | games | mid | observed | bias | NO net |
|---|---|---|---|---|---|---|---|
| receiving_yards | low | 519 | 56 | 0.528 | 0.528 | +0.0002 ± 0.0308 | −0.0831 |
| receiving_yards | middle | 945 | 57 | 0.368 | 0.366 | −0.0017 ± 0.0238 | −0.0520 |
| receiving_yards | **tail** | 416 | 57 | 0.337 | 0.262 | **−0.0755 ± 0.0303** | +0.0258 ± 0.0308 |
| rushing_yards | tail | 190 | 51 | 0.355 | 0.316 | −0.0395 ± 0.0508 | −0.0088 |
| passing_yards | middle | 335 | 56 | 0.309 | 0.343 | +0.0343 ± 0.0437 | −0.0781 |

The high rungs of receiving-yards ladders are overpriced by 7.5 points. This is the **same direction** as the
independent finding in `research/market_shape/RESULTS.md`, where the model held more upper-tail probability
than the market on live ladders — meaning the market's tail is if anything too *fat*, not too thin, and the
model's flatter tail is pointed the wrong way. That is a coherent story from two different data sources and
it is registered as `H-20260904-013`, not claimed.

## Price movement is uninformative pregame

| window | markets | unchanged | of those that moved, toward the outcome | Brier |
|---|---|---|---|---|
| T−72h → T−0 | 3031 | 6% | 0.497 ± 0.016 | 0.176 → 0.167 |
| T−24h → T−0 | 7587 | 11% | 0.496 ± 0.011 | 0.174 → 0.168 |
| T−6h → T−0 | 8054 | 16% | 0.476 ± 0.012 | 0.170 → 0.168 |
| T−24h → T−6h | 7596 | 24% | 0.518 ± 0.014 | 0.174 → 0.169 |

Pregame movement points toward the eventual outcome essentially half the time. Brier improves slightly toward
kickoff, but there is no directional information to follow here.

## Moneyline, on the separately cached subset (259 games)

Flat: Brier 0.2176 at T−168h against 0.2150 at T−0, spread at its one-cent floor from T−72h. Twenty
calibration tests, zero significant. Crossing costs 2.3–2.7% per contract on both sides at every horizon
inside T−72h, doubling to 5.4% on the wider week-out book.

## Three errors caught before any of this was believed

1. **Every price in the first backfill was null.** `snapshot()` read `yes_bid.close_dollars` and `volume_fp`;
   the API returns `yes_bid.close` and `volume`. 54,364 rows, structurally valid, correct `result` and
   `anchor_ts`, `n_candles > 0`, and no prices at all. Nothing objected. Now pinned by a frozen real response
   in `tests/test_candle_parsing.py`, plus a chunk abort if under 20% of the first 200 markets yield a quote.
2. **A fifth of the sample was post-game and looked like brilliance.** Where a market could not be matched to
   an nflverse kickoff the anchor fell back to the market's *close* time, so its "T−0" was taken after the
   game. 65% of those quotes sat at settled certainty against 0% of kickoff-anchored ones, pulling closing
   Brier from 0.215 to 0.171 and making the market look increasingly clairvoyant toward kickoff. Non-kickoff
   anchors are now dropped (`tests/test_horizon_pregame.py`).
3. **`np.sign(0) == 0`** scored unchanged quotes as "moved away from the outcome", which alone dragged the
   toward-outcome share to 0.367 ± 0.030 — a 4-sigma finding that was pure tie-handling.

## Limitations

* 16% of the universe, newest-first, four of six shards. Re-run on the full set before citing anything.
* Quotes are candle closes, so the book is as of the end of the minute or hour, not the instant.
* Volume is per-candle and mostly zero on these series, so "does efficiency vary with liquidity?" is still
  unanswerable and is left out rather than reported from near-empty data.
* Every bias here is measured against the midpoint. The midpoint is not tradable, which is exactly why the
  net-of-spread columns are carried alongside every one of them.
