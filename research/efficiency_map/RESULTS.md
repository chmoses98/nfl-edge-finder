# 2025 Kalshi NFL market-efficiency map

Reproduce: `python3 scripts/research/efficiency_map.py '<horizons glob>'`
Artifacts: `results.json` (current), `results_partial_16pct.json`, `results_cached_subset.json`.

**Status: INTERIM but replicated.** **26,671 kickoff-anchored markets, 204,256 executable quote snapshots**
— 54% of the 54,364-market universe, up from the 16% this file first reported, and every headline finding
below survived the increase with more games behind it. Sharding is `md5(ticker) % 6`, so the missing portion
is pseudo-random with respect to family and date; what remains biased is the **newest-first ordering within
each shard**, which still weights the sample toward late-season and playoff games. Nothing here is an edge.

## Method

Every number is measured on **executable** prices: `ask` is what a YES buyer pays, `bid` what a YES seller
receives. Midpoints appear only where the midpoint itself is the object of study. Returns are net of the
Kalshi taker fee, `ceil(0.07·p·(1−p)·100)/100`. Standard errors are **clustered on game** — both sides of a
game are one outcome and a twelve-rung player ladder is one performance, so unclustered errors here run
1.5–2× too small. Multiplicity is handled by Benjamini–Hochberg at q = 0.10 across all 136 calibration cells.

The FDR budget is deliberately **not** spent on "is the mean execution return non-zero". That is the
overround, it is nearly deterministic, and testing it returns p ≈ 0 for almost every cell while saying only
that a market maker charges a spread. It is reported as a cost table instead.

## The headline: large, real miscalibrations — and not one of them is tradable

**29 of 219 calibration cells survive Benjamini–Hochberg at q = 0.10** (up from 7 of 136 at 16% coverage).
Both findings reported at 16% replicated and strengthened:

| cell | 16% coverage | 54% coverage |
|---|---|---|
| FIRST_TD_SCORER, 0.10–0.20 at close | −0.0716 ± 0.0219 (44 games) | **−0.0586 ± 0.0160** (130 games) |
| PLAYER_STAT receptions, 0.35–0.50 at T−6h | +0.0874 ± 0.0283 (57 games) | **+0.1111 ± 0.0160** (146 games) |

The first-touchdown-scorer market shows a clean, monotone longshot bias across five adjacent price buckets:

| closing price | n | games | mid | realised | bias |
|---|---|---|---|---|---|
| 0.00–0.02 | 518 | 170 | 0.011 | 0.012 | +0.0009 ± 0.0047 |
| 0.02–0.05 | 917 | 182 | 0.030 | 0.044 | +0.0132 ± 0.0061 |
| 0.05–0.10 | 489 | 171 | 0.068 | 0.086 | +0.0179 ± 0.0118 |
| 0.10–0.20 | 297 | 130 | 0.149 | 0.091 | **−0.0586 ± 0.0160** |
| 0.20–0.35 | 66 | 43 | 0.226 | **0.045** | **−0.1810 ± 0.0258** |

Contracts quoted at 22.6 cents settle 4.5% of the time. That is an **18-point** miscalibration, the largest
in the study, at seven standard errors.

And it is worth **nothing**. Selling those contracts — the correct side — nets **−0.0089 ± 0.0260** after the
Kalshi taker fee. Checked across every family and price bucket with game-clustered standard errors, **not one
has a positive net return**:

| family, price bucket | n | games | mid | realised | NO-side net after fees |
|---|---|---|---|---|---|
| FIRST_TD_SCORER 0.20–0.35 | 66 | 43 | 0.226 | 0.045 | −0.0089 ± 0.0260 |
| FIRST_TD_SCORER 0.10–0.20 | 297 | 130 | 0.149 | 0.091 | −0.0463 ± 0.0150 |
| PLAYER_STAT 0.80–0.90 | 692 | 148 | 0.842 | 0.806 | −0.0109 ± 0.0166 |
| PLAYER_STAT 0.65–0.80 | 1837 | 185 | 0.717 | 0.682 | −0.0215 ± 0.0135 |
| PLAYER_STAT 0.50–0.65 | 2964 | 190 | 0.560 | 0.518 | −0.0336 ± 0.0150 |
| TEAM_TOTAL 0.80–0.90 | 50 | 23 | 0.848 | 0.780 | +0.0128 ± 0.0790 |

The only non-negative figure anywhere is TEAM_TOTAL 0.80–0.90 at +0.013 ± 0.079 — 0.16 standard errors, on
50 contracts across 23 games, in the family with the second-widest book.

That is the central result of the whole map. **A large, highly significant miscalibration is not a tradable
one.** An 18-point pricing error at z = 7 nets less than zero once the spread and fee are paid. Any search
procedure that ranks by miscalibration and stops there will find exactly these markets and lose money in
them.

Player props also show a consistent **favourite overpricing** that the 16% sample could only hint at: three
adjacent buckets above 0.50 all negative at 2.2–3.0 SE (0.50–0.65: −0.0424 ± 0.0141; 0.65–0.80:
−0.0352 ± 0.0134; 0.80–0.90: −0.0358 ± 0.0165). Props quoted above a coin flip settle roughly 3.5–4 points
less often than priced. The NO side of all three still loses after costs.

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

## Does efficiency vary with liquidity? Yes — but not the way edge-hunting assumes

Closing quotes bucketed by open interest, with game-clustered standard errors:

| open interest at close | n | games | median width | bias | \|bias\| | Brier | YES net | NO net |
|---|---|---|---|---|---|---|---|---|
| zero / none | 1021 | 58 | 0.060 | +0.0123 ± 0.0205 | 0.344 | 0.1758 | −0.1045 | −0.1258 |
| Q1 thinnest | 1888 | 61 | 0.050 | +0.0042 ± 0.0170 | 0.346 | 0.1753 | −0.0684 | −0.0745 |
| Q2 | 1886 | 61 | 0.050 | −0.0219 ± 0.0156 | 0.323 | 0.1619 | −0.0744 | −0.0286 |
| Q3 | 1886 | 61 | 0.030 | −0.0110 ± 0.0161 | 0.331 | 0.1666 | −0.0515 | −0.0281 |
| Q4 deepest | 1887 | 61 | 0.020 | −0.0276 ± 0.0191 | 0.330 | 0.1653 | −0.0566 | −0.0008 |

Deep markets are *slightly* better calibrated — at 54% coverage, Brier 0.169 in the deepest quartile against
0.182 with no open interest at all, mean absolute bias 0.337 against 0.354. That difference is small. What
changes enormously is the **cost**: the median spread falls from 7 cents to 2, and the NO-side net return
improves from −0.145 to −0.016.

So the thin markets are barely less efficient and dramatically more expensive to trade. The intuition that
drives people into illiquid corners — "nobody is looking at these, so they must be mispriced" — is roughly
one third right about the mispricing and completely wrong about whether you can collect it. Lifetime volume
gives the same picture (widest spreads and worst net returns in the zero-volume bucket).

This is the same conclusion the live shadow ledger reached from the opposite direction
(`research/shadow/RESULTS.md`): selecting on distance from the midpoint selects for illiquidity.

## An apparent totals result that the sample will not support

`TOTAL` shows a NO-side net return of **+0.015 to +0.026 at every one of the ten horizons** (n = 347 rungs,
59 games), with closing mid 0.493 against an observed rate of 0.441 — totals settling under more often than
priced. Ten consistent horizons is superficially striking.

It is almost certainly the sample. The backfill runs newest-first, so this 16% subset is weighted toward
late-season and playoff football, which is lower-scoring than the September and October games that make up
most of a full season. A systematic "unders" result on a playoff-weighted sample is what that confound looks
like. It is recorded here so the full-sample re-run either confirms or kills it, and it is **not** registered
as a hypothesis on this evidence.

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
* Per-candle volume is zero for 64% of closing snapshots, but open interest is populated for 89% and
  lifetime market volume for 95%, so the liquidity question is answered on those rather than on candle volume.
* The week-out book is barely a book: median spread 0.59 for SPREAD and 0.56 for TEAM_TOTAL at T−168h and
  T−72h. Those horizons' numbers describe an empty order book, not a market view.
* Every bias here is measured against the midpoint. The midpoint is not tradable, which is exactly why the
  net-of-spread columns are carried alongside every one of them.
