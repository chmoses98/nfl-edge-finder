# Preregistration: betting-value evaluation of the NFL PURE shadow (dry-run diagnostic)

Committed 2026-10-12, before any prospective PURE shadow row has matured (the `market-data` branch held no
`data/shadow_pure/nfl` store on that date). The machine-readable copy, which the code loads and whose sha256 is
written into every `value_scorecard` record, is
[`PURE_SHADOW_NFL_VALUE_PREREG.json`](PURE_SHADOW_NFL_VALUE_PREREG.json). If the two disagree, the JSON is what
ran. Changing a setting means a new preregistration id and a new evaluation window. Earlier rows can't be
re-scored under the new settings and then reported as if they had been preregistered.

This is **track C** (market-value evaluation). It is separate from accuracy promotion, which uses the
`accuracy_scorecard` records. It runs only as a **dry-run diagnostic** inside `settle_and_evaluate`. Nothing reads
its output to place, size or route an order, and nothing touches staking or a production surface.

## Hypothesis and arms

* **H1.** At the FINAL_T90 capture (T−90m to T−30m, after the inactive list), buying the side preferred by the
  frozen `PURE_PLAYER_V1` ladder at the executable Kalshi price makes money after taker fees and one tick of
  slippage.
* **Primary arm (the only arm eligible for an independent-value verdict):** `PURE_PLAYER_V1`, at the
  `FINAL_T90` capture window.
* **Descriptive only:** `PURE_PLAYER_V1` at DAY_BEFORE, MORNING_OF and ADHOC, and `PURE_EWM_BASELINE` at FINAL_T90.
  Their verdicts are reported but don't count toward the decision.
* **Market-informed diagnostic:** `DATA_PLAYER_V4` and `DATA_PLAYER_V5`, read from the incumbent records the
  collector copies read-only. They are evaluated with `market_informed_source=true`, so they always read
  **`NOT_INDEPENDENT_EVIDENCE`**. A market-informed model's disagreement with the market it learned from is never
  evidence of value.

## Inputs (as_of information only)

* **Probabilities.** These are the captured `pure_forecast.v1` ladder exactly as written: `p_yes = P(actual ≥
  at_least)`, conditional on the player's own participation. `participation_probability` is null because PURE V1
  doesn't model participation, so no unconditional conversion is applied. As a result, a YES decision carries
  inactive risk that the model hasn't priced. The FINAL_T90 window comes after the inactive list, which is why
  it's the primary window.
* **Quotes.** These come from the separate `market/<day>/<run>.kalshi_listings.jsonl.gz` family, mapped by
  `nfl_edge/shadow_pure/scorecards.market_family`:
  * The player is the GSIS id from the player map. Unmapped rows are dropped and counted.
  * `yes_bid` and `yes_ask` are in **dollars**, from the capture's `*_dollars` fields.
  * The **strike** is converted explicitly. The NFL row's `threshold` K means YES iff stat ≥ K. A Kalshi `> f`
    strike becomes floor(f)+1. Because the PURE ladder publishes P(X ≥ k) at integer k, the strike maps to
    `at_least = K`. Matching is exact, so Kalshi 75+ against a ladder of 10, 20, … is a missing quote and not an
    interpolation.
  * Rows observed after the as_of of the capture that recorded them are dropped and counted. Crossed or
    out-of-range prices are dropped and counted.
  * The scorecard enters only at the latest quote with `observed_at ≤ as_of` on a market with `open_time ≤
    as_of`. A later quote is never used for entry, and such quotes are counted.
* **Outcomes.** These are the nflverse box-score outcomes the collector writes, as sports truth. Market
  settlement is never used.

## Decision rule, costs, settlement

| setting | value | why |
|---|---|---|
| decision unit | one per (game, player, statistic) at the as_of chosen by `as_of_policy=earliest` within the window | one capture per window per game, never chosen by price or outcome |
| rule | `max_edge_after_fees`, `min_edge = 0.02` | the largest EV after fees and slippage, and only if it is at least 2 cents per contract |
| fees | Kalshi taker, coefficient 0.07, multiplier 1, 1 contract per order, cent round-up | the conservative per-order estimate (SCORECARDS.md) |
| slippage | $0.01 per contract added to the ask | thin player-prop books |
| stale quote | a quote older than 21,600 s (6 h) at as_of is discarded and counted | the capture feed is change-suppressed, and discovery snapshots are up to a day old |
| calibration window | none (`calibration_fit_end = null`) | PURE_PLAYER_V1 is frozen and was fitted before collection, so no prospective rung is in-sample |
| DNP policy | **`settle_by_actual`** | see below |
| DNP sensitivity | `void`, reported as `dnp_sensitivity` and never verdict-bearing | — |

**The DNP policy, checked against the series rules.** The series rules are in `docs/KALSHI_SETTLEMENT.md` and
`nfl_edge/settlement/semantics.py`, taken from the contracts' `rules_secondary` text and 61,068 archived settled
markets. They define three branches. A player who takes ≥ 1 snap settles on the stat. An **inactive** player settles
**NO ($0)**. An active player who never takes a snap settles at the pregame fair price; this happened to 1.03% of
settled player rungs. `settle_by_actual` scores a non-participant at the recorded actual (0), so YES loses. That is
exact for the inactive branch, which is the economically important one. It is wrong only for the rare
active-no-snap scalar branch, which would pay roughly the pregame price. The collector's `played` flag counts
offensive snaps, while Kalshi counts any snap. That difference matters only for special-teams-only appearances,
and it's disclosed rather than modelled.

## Minimum sample and inference

* The minimums are `min_decisions = 200` and `min_games = 40` (the SCORECARDS.md defaults). Below them the verdict
  is `INSUFFICIENT_SAMPLE`, whatever the ROI.
* ROI after fees is reported with percentile **bootstrap CIs that resample whole games** (2,000 replicates, seed
  20261010), and also with a CI that resamples whole players.
* `VALIDATED_VALUE` requires ROI > 0 **and** the lower bound of every clustered 95% CI > 0 (`min_roi_ci_lower =
  0`). If ROI > 0 but a CI lower bound is ≤ 0, the verdict is `POSITIVE_BUT_INCONCLUSIVE`. If ROI ≤ 0, it is
  `NO_EVIDENCE_OF_VALUE`.
* CLV (the closing quote at or before kickoff, taken from later captures) is diagnostic only and never enters the
  verdict.

## What a verdict means

Even `VALIDATED_VALUE` describes a recorded, preregistered evaluation window. It isn't wagering authority. Any
use beyond the diagnostic would need its own reviewed change to the staking and routing code, and this
preregistration doesn't authorize that.
