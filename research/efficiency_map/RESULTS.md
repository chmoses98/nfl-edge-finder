# 2025 Kalshi NFL market-efficiency map

Reproduce: `python3 scripts/research/efficiency_map.py '<horizons glob>'`
Artifacts: `results.json` (current), `results_partial_16pct.json`, `results_cached_subset.json`.

**Status: COMPLETE.** **39,226 kickoff-anchored markets, 269,949 tradable executable quote snapshots** from
52,491 of the 54,364 settled archived markets (97%). Reported at 16% and again at 54% during construction;
the findings below are the full-coverage versions and are stable against both earlier passes. Nothing here
is an edge.

## Method

Every number is measured on **executable** prices: `ask` is what a YES buyer pays, `bid` what a YES seller
receives. Midpoints appear only where the midpoint itself is the object of study. Returns are net of the
Kalshi taker fee, `ceil(0.07·p·(1−p)·100)/100`. Standard errors are **clustered on game** — both sides of a
game are one outcome and a twelve-rung player ladder is one performance, so unclustered errors here run
1.5–2× too small. Multiplicity is handled by Benjamini–Hochberg at q = 0.10 across all 195 calibration cells. Calibration is
computed only on books quoted within 10 cents (`EFFMAP_MAX_WIDTH`) — see the correction below for why that
is not an optional refinement.

The FDR budget is deliberately **not** spent on "is the mean execution return non-zero". That is the
overround, it is nearly deterministic, and testing it returns p ≈ 0 for almost every cell while saying only
that a market maker charges a spread. It is reported as a cost table instead.

## A correction: two findings reported at 54% were artefacts of untradable books

An earlier version of this file reported two headline results — a first-touchdown longshot bias reaching
−0.181 ± 0.026, and receptions at 0.35–0.50 *underpriced* by +0.111 ± 0.016. Both were computed against the
quoted midpoint across all books. **Both invert or vanish once the sample is restricted to books a trader
could actually cross.**

The mechanism is the one this platform already documented for the live ledger and then walked straight into.
In the receptions 0.35–0.50 bucket the median spread is 7 cents but the **mean** bid is 0.234 against a mean
ask of 0.624: a minority of enormously wide books drags the mean. On such a book the midpoint is not an
estimate of anything, it is an arithmetic artefact of where a maker parked an empty quote, and "the contract
settled above the midpoint" is not evidence that the market was wrong.

| cell (closing price) | all books | tradable books (≤ 0.10 wide) |
|---|---|---|
| receptions 0.35–0.50 | **+0.083** ± 0.017 | **−0.053** ± 0.018 |
| FIRST_TD_SCORER 0.10–0.20 | **−0.059** ± 0.016 | **+0.006** ± 0.029 |
| FIRST_TD_SCORER 0.20–0.35 | **−0.181** ± 0.026 | too few narrow-book quotes to report |

FDR survivors fall from 29 of 219 to **9 of 195**. 84.4% of closing quotes are within 10 cents, so the
discarded 15.6% was overturning conclusions drawn from the other 84%. Every calibration figure below is now
computed on tradable books by default (`EFFMAP_MAX_WIDTH`, default 0.10).

## The headline: player props are overpriced, consistently, and it is still not tradable

**12 of 223 calibration cells survive Benjamini–Hochberg at q = 0.10.** Nine of the twelve are receptions
contracts and all nine point the same way. Player props are **overpriced on the YES side**, flat below 0.20
and roughly −0.04 above 0.35:

| closing price | n | games | mid | realised | bias |
|---|---|---|---|---|---|
| 0.05–0.10 | 2160 | 260 | 0.071 | 0.072 | +0.0005 ± 0.0061 |
| 0.10–0.20 | 3534 | 259 | 0.146 | 0.151 | +0.0043 ± 0.0071 |
| 0.20–0.35 | 4956 | 257 | 0.269 | 0.258 | −0.0117 ± 0.0087 |
| 0.35–0.50 | 4204 | 251 | 0.425 | 0.395 | **−0.0304 ± 0.0107** |
| 0.50–0.65 | 3645 | 229 | 0.563 | 0.521 | **−0.0417 ± 0.0127** |
| 0.65–0.80 | 2392 | 183 | 0.716 | 0.677 | **−0.0394 ± 0.0121** |
| 0.80–0.90 | 850 | 168 | 0.842 | 0.802 | **−0.0397 ± 0.0143** |

Four adjacent buckets at 2.8–3.3 SE, on 168–251 games each, with a clean threshold at 0.20 below which the
market is exactly calibrated. This is the most robust finding in the study and it is confirmed by two
unrelated methods elsewhere: the encompassing regression's intercept (`research/model_vs_market`) and the
leg-calibration map built for the dependence test (`research/joint_structure`).

**And it is not tradable.** The YES-side net return after the Kalshi taker fee is −0.055 to −0.086 across
those buckets; the NO side pooled to −0.0126 ± 0.0104 at 54% coverage. A 3–4 point pricing error against a
5–7 cent spread nets nothing.

First-touchdown-scorer markets show the mirror image at the cheap end — contracts at 0.030 settle 0.040
(+0.0100 ± 0.0041) and at 0.067 settle 0.081 (+0.0135 ± 0.0079), i.e. very cheap long shots are mildly
*under*priced. Buying them still nets −0.021. Note that the dramatic first-TD *over*pricing this file
reported at 54% coverage (−0.181 ± 0.026 at 0.20–0.35) has vanished entirely at full coverage on tradable
books: 0.10–0.20 now reads −0.0002 ± 0.0194.

Game markets are efficient. SPREAD and TOTAL biases are within about 1.5 SE at every bucket. The one family
with a positive net return anywhere is GAME_WINNER, where underdogs look underpriced (0.35–0.50: mid 0.418,
realised 0.470, bias +0.0523 ± 0.0461, YES net **+0.0270**) and favourites overpriced (0.65–0.80: mid 0.723,
realised 0.656, bias −0.0669 ± 0.0493) — the classic favourite–longshot bias, on 93–124 games per bucket at
**about 1.1–1.4 standard errors**. It is the only positive expected return in the entire map and it is not
significant. It is recorded rather than acted on, and re-testing it on 2026 is the obvious use of the
prospective ledger.

**Spreads and totals are efficient; player props are consistently overpriced; game winners may carry a
favourite–longshot bias too small to distinguish from noise; and the spread is wider than the error in every
case.**

## Does efficiency vary with liquidity? Yes — but not the way edge-hunting assumes

Closing quotes bucketed by open interest, with game-clustered standard errors:

| open interest at close | n | games | median width | bias | \|bias\| | Brier | YES net | NO net |
|---|---|---|---|---|---|---|---|---|
| zero / none | 1021 | 58 | 0.060 | +0.0123 ± 0.0205 | 0.344 | 0.1758 | −0.1045 | −0.1258 |
| Q1 thinnest | 1888 | 61 | 0.050 | +0.0042 ± 0.0170 | 0.346 | 0.1753 | −0.0684 | −0.0745 |
| Q2 | 1886 | 61 | 0.050 | −0.0219 ± 0.0156 | 0.323 | 0.1619 | −0.0744 | −0.0286 |
| Q3 | 1886 | 61 | 0.030 | −0.0110 ± 0.0161 | 0.331 | 0.1666 | −0.0515 | −0.0281 |
| Q4 deepest | 1887 | 61 | 0.020 | −0.0276 ± 0.0191 | 0.330 | 0.1653 | −0.0566 | −0.0008 |

At full coverage, Brier is 0.1725 in the deepest quartile against 0.1761 with no open interest at all, and
mean absolute bias 0.344 against 0.350. That difference is small — smaller than it looked at 54%. What
changes enormously is the **cost**: the median spread falls from 8 cents to 2, and the NO-side net return
improves from −0.164 to −0.017.

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

## Player ladder tails, on tradable books

The high rungs of a ladder are more overpriced than the low ones, on top of the across-the-board prop
overpricing above:

| stat | rung bucket | n | games | mid | realised | bias | NO net after fees |
|---|---|---|---|---|---|---|---|
| receiving_yards | low | 1199 | 158 | 0.575 | 0.558 | −0.0171 ± 0.0191 | −0.0294 ± 0.0190 |
| receiving_yards | middle | 2380 | 177 | 0.389 | 0.360 | −0.0291 ± 0.0145 | −0.0143 ± 0.0145 |
| receiving_yards | **tail** | 1182 | 167 | 0.354 | 0.312 | **−0.0413 ± 0.0196** | −0.0023 ± 0.0197 |
| receptions | **tail** | 726 | 124 | 0.284 | 0.238 | **−0.0461 ± 0.0194** | +0.0010 ± 0.0196 |
| rushing_yards | tail | 599 | 152 | 0.370 | 0.357 | −0.0130 ± 0.0263 | −0.0278 ± 0.0263 |
| passing_yards | tail | 355 | 136 | 0.063 | 0.045 | −0.0176 ± 0.0131 | −0.0140 ± 0.0131 |

**This is a third correction.** On all books at 16% coverage the receiving-yards tail read −0.0755 ± 0.0303
with a NO-side net of **+0.0258 ± 0.0308**, which an earlier version of this file singled out as the only
positive number in the study. On tradable books at 54% coverage the bias is real but roughly half the size
(−0.0413 ± 0.0196, 2.1 SE) and the NO-side net is **−0.0023 ± 0.0197** — indistinguishable from zero, not
positive. The receptions tail behaves the same way (+0.0010 ± 0.0196).

The direction still supports `H-20260904-013`: high rungs are overpriced, so the market's upper tail is
already too fat, and `research/tail_calibration` shows the model's is fatter still. That remains a model
defect rather than an edge, and the supporting evidence from this map is weaker than first reported.

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

## Errors caught before any of this was believed

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
