# Historical strategy replay (Phase 3)

RESEARCH ONLY. Nothing here promotes a model, changes a status in `docs/PRODUCTION_ELIGIBILITY.md`, or has authority over the
pricer, gates, risk policy or staking.

Code: `nfl_edge/research/strategy_replay.py` (library), `scripts/research/strategy_replay.py` (CLI, about 4 minutes),
`tests/test_strategy_replay.py`. Numbers: `docs/research/strategy_replay_results.json` (aggregates only).
Reproduce: `python3 scripts/research/strategy_replay.py` (`--dev-only` prints the development block alone and writes nothing).

## Answer

**No strategy beat fees out of sample.** Every out-of-sample interval contains zero, the point estimates change sign between the
primary horizon and the robustness horizon, and the one cell whose interval excludes zero on the favourable side is a
two-game cell. The market baseline (A) loses roughly the fee plus spread. The football-informed strategies (C, D, E) have 77 to 87
independent out-of-sample games, which is enough only to rule out edges larger than about 17 percentage points of ROI, not the 2 to 5
points a real edge would be. This replay cannot tell "no edge" from "a small edge"; it can say that nothing here looks like a large one.

## What was replayed

Decision at a horizon (primary **T-90m**, robustness **T-24h**), buy one flat unit at the **executable ask of the side bought**
(YES -> yes ask, NO -> 1 - yes bid), pay the Kalshi taker fee from `config/kalshi_fee_schedule.json` (marginal fee of a 100-lot,
about 1.6c per contract on average here), hold to settlement. Families: moneyline, spread, total, team total, and overall.

| | rule (all thresholds are constants in the library, frozen 2026-10-25 before any replay) |
|---|---|
| A market baseline | per family, the cheapest executable side with ask in 0.60-0.85. No football. Control for favourite-longshot and fee/spread drag |
| B model disagreement | BOARD_V2 `p_yes` (PRICED, generated at or before the decision, at most 4h old) minus ask minus fee >= 5c. **2026 only** |
| C matchup-informed | point-in-time ridge EPA ratings -> rating-implied home margin (map fitted on the three prior seasons) vs the margin the market's own spread ladder implies; if the gap is 2.5 points or more, buy the spread rung nearest 50% on the side the ratings favour |
| D script-robust | C's gap, capped at 5 points, becomes a shift range [0.5 gap, 1.0 gap] of the market centre; `expression.py` over `fairvalue.py` picks any full-game contract by conservative edge per payoff-sd, needing a win in at least 3 of 9 scripts and a positive conservative edge |
| E conservative value | D's pick only if its conservative net edge is >= 2.0c per contract and the book is <= 6c wide |
| C_INVERSE (control) | the other side of C's contract. A control, not a strategy: if C and its inverse both lose, the signal is absent |

Books must be two-sided, at most 10c wide, ask between 0.05 and 0.95, and the quote at most 30 minutes old at the decision.

## Safeguards, and how each is enforced

* **Point in time.** Quotes carry an observation timestamp and the loader drops any later than the decision. Ratings for a game use
  only team-games from strictly earlier weeks. The rating-to-margin map for a season is fitted on the three previous seasons only. The
  residual bank behind D/E holds only games played on an earlier calendar date. BOARD_V2 probabilities must have been generated at or
  before the decision. `assert_point_in_time` runs on every board and every pick. Tests: a future quote, a future feature and a future
  projection each trip it; perturbing future weeks, future-season results or later-dated games leaves ratings, the map and the bank
  unchanged (and perturbing earlier ones does change them, so the tests have power).
* **Decisions cannot see outcomes.** Boards carry no outcome or closing price. All decisions are made first, outcomes are joined after.
  A test shuffles and flips every settlement: the decisions are identical, the returns move.
* **Executable prices only.** Mids are used only for the market's centre (a ladder median) and for CLV references, never as a fill.
* **One observation per game.** A game's contracts share one outcome. Each strategy places at most one unit per game and family; across
  families a game's unit is split equally. Intervals are 4,000-draw bootstrap over games (seed 20261025). The "games" column below is the
  count of independent observations.
* **Chronological split, nothing tuned on the test set.** Development block: 2025 weeks 1-9 (Kalshi). Held-out blocks: 2025 week 10
  onward including the playoffs, and 2026 weeks 1-5. No parameter was fitted on Kalshi data; the only fitted object is the 2-parameter
  rating-to-margin map, fitted on earlier seasons. Parameter-grid tables are labelled POST-HOC in the results file and below.
* **Fees from the schedule** through `FeeSchedule.taker_fee`. The schedule file has one window, effective 2026-07-07. 2025 decisions
  fall before it, so they are priced with the registry multiplier and the 0.07 base coefficient; the repo holds no separate 2025
  schedule, so the 2025 fee is an assumption (the quadratic formula has been the same shape throughout).
* **Settlement semantics checked.** The engine's contract definitions reproduce Kalshi's recorded outcome from the final score for 15,871
  contract sides; the only 2 mismatches are the two sides of one 2026 tie (27-27), which the board table records as 0.5. Returns use
  0.5 for that game.

## Results at T-90m (ROI = net profit / outlay, outlay = ask + fee; 95% game-bootstrap interval; hit = share of games won)

Held-out, pooled (2025 week 10+ and 2026 weeks 1-5):

| strategy | games | ROI | 95% interval | hit | mean ask | gross ROI before fee |
|---|---|---|---|---|---|---|
| A baseline, all | 216 | -3.8% | -9.5% to +2.0% | 62.5% | 0.633 | -1.3% |
| A moneyline | 145 | -11.2% | -22.0% to -0.6% | 63.1% | 0.696 | -9.3% |
| A spread | 216 | -0.2% | -10.5% to +10.3% | 63.0% | 0.614 | +2.5% |
| A total | 216 | +0.6% | -9.7% to +10.7% | 63.9% | 0.618 | +3.3% |
| A team total | 96 | -14.7% | -30.8% to +0.4% | 54.2% | 0.619 | -12.5% |
| B BOARD_V2 | 4 | -38.6% | -100% to -0.7% | 25% | 0.398 | n/a (4 games) |
| C ratings vs ladder (spread) | 87 | -5.2% | -25.1% to +14.6% | 49.4% | 0.504 | -1.9% |
| C_INVERSE (control) | 87 | -3.7% | -23.4% to +16.1% | 50.6% | 0.508 | -0.4% |
| D script-robust | 86 | +0.4% | -17.5% to +17.6% | 57.0% | 0.552 | +3.2% |
| E conservative | 77 | -0.1% | -18.2% to +18.7% | 57.1% | 0.557 | +2.6% |

D and E choose almost entirely spread rungs (78 of 86 and 72 of 77 games); their moneyline, total and team-total cells hold 1 to 6 games
and are not interpretable.

Out of sample by part, overall ROI (games): A: 2025 wk10+ -0.2% (137), 2026 -10.0% [-19.9%, -0.3%] (79). C: -2.2% (55), -10.4% (32). D: -4.9% (54),
+10.0% (32). E: -5.3% (48), +9.4% (29). Every football-informed interval spans zero by 17 points or more; A in 2026 is the only held-out part whose interval excludes zero.

Development block (2025 weeks 1-9), shown separately because it is the part visible while building: A -5.4% (127 games), C -29.5%
[-54.6%, -1.1%] (46), D -31.4% [-57.7%, -4.7%] (40), E -25.9% [-57.0%, +6.6%] (30). The ratings-based strategies looked clearly
bad there and middling out of sample; neither is distinguishable from the other given the intervals.

### Robustness horizon T-24h (held-out pooled)

A -6.4% [-12.3%, -0.9%] (216); C +3.4% [-17.6%, +24.7%] (81); D +10.1% [-6.8%, +28.0%] (80); E +7.0% [-11.6%, +25.4%] (74); B 1 game.
D moves from +0.4% to +10.1% between horizons with a +/-17 point interval each: that is the size of the noise, not a trend. Do not read
D at T-24h as a finding; it is one of roughly 200 cells in the results file and its interval includes zero (88% of bootstrap draws are
positive, a descriptive tail share and not a p-value).

### CLV (mean of closing mid on the side bought minus ask, against the T-30m mid; per contract)

At T-90m every strategy shows CLV of -0.5c to -0.7c (A -0.67c, C -0.57c, D -0.53c, E -0.54c, all intervals excluding zero): the price
paid is about half a spread above where the market sat 60 minutes later, which is what paying the ask against a stable market looks like. At T-24h, C, D and E
are at -0.1c to 0.0c with intervals spanning zero, A at -0.8c. Nothing buys at a price the market later moves toward by more
than the spread. `clv_ko` (against the kickoff / latest pre-game mid) tells the same story.

## What the ratings actually carry (descriptive, not executable)

Using the schedule's closing spread (legitimate here because nothing is traded on it), the rating-implied margin minus the closing line
regressed on how far the result missed the line: slope +0.09 (se 0.24, 285 games, 2024), -0.34 (se 0.22, 285, 2025), -0.07 (se 0.44, 94, 2026).
When |gap| >= 2.5, the ratings' side covered 50.9% (110 games), 46.1% (102) and 46.2% (39). The ratings explain about 13-15% of margin
variance in sample (rmse about 12.8-13.2 points) and add nothing measurable beyond the closing line. This is an honest finding about
this approximation: EPA-based team-level ratings with no injury, quarterback or availability input are already inside the market's number.
These descriptive numbers were looked at once during development, before the full run; no threshold was changed afterwards.

## Post-hoc sensitivity (NOT used to choose anything; same data as above; T-90m; ROI [interval], games)

| variant | development | held-out pooled |
|---|---|---|
| A band 0.50-0.75 | -7.3% (127) | -0.2% [-7.2, +6.5] (216) |
| A band 0.60-0.85 (pre-registered) | -5.4% (127) | -3.8% [-9.2, +2.4] (216) |
| A band 0.65-0.90 | -8.9% (124) | -6.6% [-11.5, -1.2] (216) |
| A band 0.70-0.90 | -3.1% (115) | -1.0% [-5.7, +4.2] (216) |
| C gap >= 1.0 / 1.5 / 2.5 / 3.5 / 5.0 | -19% / -24% / -29% / -32% / -61% (90 / 78 / 46 / 17 / 5) | -5.8% / -8.2% / -5.2% / -8.9% / -2.9% (165 / 134 / 87 / 55 / 30), every interval spans zero |
| B net edge >= 2c / 3c / 5c / 8c | none | +6.4% (53 games) / +23.7% (23) / -38.6% (4) / no bets |

The B rows are shown because the owner will ask: the 2c and 3c rows have wide intervals ([-13%, +28%] and [-14%, +66%]) and sit on 53 and 23
games drawn from 61 games with a projection. They are not evidence of an edge and select nothing. Across the grid, bigger thresholds do not
improve C, which is what an absent signal looks like (a real one would sharpen with the gap).

## Strategy B: why it is almost empty

BOARD_V2 has no history before 2026 and only PRICED rows carry a game-line probability (all 172,939 cached rows are PRICED;
`PROJECTABLE_NOT_YET_VALIDATED` rows have no `p_yes` for these families, so including them changes nothing). Projections were found for 61
of the 79 games at T-90m (the capture has no BOARD_V2 files for 2026-10-06 to 10-11, which removes week 5 and leaves some earlier games without a projection). The model
is the market's own centre re-simulated, so on spreads, totals and moneylines it rarely disagrees with the ask by 5c after fees; the
four 5c-or-more disagreements were all team totals, and they lost. Four games say nothing about BOARD_V2; the existing prospective
record in `PRODUCTION_ELIGIBILITY.md` remains the evidence, and its status is unchanged.

## Limits (all of them)

1. **No depth.** 2025 has top-of-book only (the candle `vol`/`oi` fields are traded volume and open interest, not displayed size), and
   the 2026 board table has no size either. BOARD_V2 projection rows carry the top-of-book size at their own snapshot, but it is not at
   the decision time and is not used. Fills are assumed to be available at the quoted ask for one flat unit with no size limit and no
   slippage. A real order larger than the displayed size would walk the book and do worse.
2. **No fill risk, no order latency, no maker orders.** Taker at the quoted ask only.
3. **2025 coverage.** The archive has no Rams (code LA) contracts: 20 scheduled 2025 games with the Rams plus one other game have no
   Kalshi rows, so 264 of 285 games are covered. Playoff rows anchored on market close time (3,851 rows) are excluded because their "T-0"
   falls after the game. Team totals exist for only 22 games in 2025 (79 in 2026).
4. **Staleness rule differs by source.** In 2025 a snapshot's `age_min` is how long before the horizon the last candle ended; quotes
   older than 30 minutes are dropped (12% at T-90m). In 2026 the age is the time since a capture run last confirmed the book, which
   keeps quiet but live books. The two are not identical in strictness.
5. **2026 is five weeks** (79 games) and week 6 has no board table, so it was not replayed.
6. **Rating approximation.** Only measured team-level opponent-adjusted EPA/play ratings (the repo's DATA_ONLY hyperparameters, one metric). No
   coverage, blitz, route, injury, quarterback or availability data exist in this replay, so C, D and E test the idea "team-level EPA
   matchup beats the market's number", not the qualitative analysis a handicapper would add. A failure here is not evidence against that analysis.
7. **Market centre from the ladder.** The centre D/E shift is the median of the market's own mid ladder (correlation 0.996 with the closing
   spread, mean difference 0.01 points), not the incumbent's grid-search centre. The thesis shift range is a mechanical rule, not an
   analyst's range; the noise buffer the engine adds is its own baseline gap against the unshifted ladder.
8. **Power.** 77 to 87 games per football-informed strategy; interval half-widths of about 18 points of ROI. Roughly 200 cells are
   reported in the results file (strategies x families x blocks x horizons); a few intervals exclude zero by chance (A moneyline at both
   horizons, A overall at T-24h, A in 2026) and none of them was pre-registered as a finding. The moneyline result (favourites priced 0.60-0.85 lose about 11% after fees,
   -9% before) is the one repeated across blocks and horizons, and is consistent with fee plus spread drag plus a mild favourite
   overpricing; it is a hypothesis for prospective testing, not a result.
9. **Fee assumption** for 2025 (see above) and a marginal 100-lot fee; a single-contract order pays the cent-rounded fee (2.0c at 50c
   versus 1.75c), which would lower every ROI by roughly half a point. Not recomputed.
10. **Information test peeked.** The descriptive information test (above) was seen once during development, before the full run. Thresholds
    were frozen before it and never changed.
11. **A tie** in 2026 (NYG-WAS) settles at 0.5 per the board table; it affects only moneyline sides in one game.
12. Not done: week-6 2026 replay; depth-aware fills; a separate 2025 fee schedule; any promotion decision.
