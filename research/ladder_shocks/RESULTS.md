# Structural ladder repricing after a precisely-timed shock

Reproduce: `python3 scripts/research/ladder_shock_repricing.py`
Machinery: `scripts/research/ladder_shock_repricing.py`, tests in `tests/test_ladder_shock_repricing.py`.

## The question a single contract cannot answer

Session 3 asked whether prices *move* after the inactive release. This asks what shape the move has. When a
team loses a player it expected to have, the market-implied distribution over game margin can:

* **translate** — the market treats the absence as a change in expected strength (location);
* **widen** — it treats the absence as a change in *uncertainty* (scale);
* **fatten at the blowout end** — it prices a different failure mode (tail).

These are different economic claims and they imply different trades. Only a ladder separates them.

## Reconstruction

Kalshi's `KXNFLSPREAD` is a genuine ladder: each rung is `P(TEAM margin > strike)` at a half-point strike,
listed for **both** teams. The two sides compose exactly into a survival curve over signed home margin:

```
home rung, strike s   ->  S(s)  = P(M > s)
away rung, strike s   ->  S(-s) = 1 - P(-M > s)
```

The complement is exact, not approximate: margins are integers and the strikes are half-integers, so
`P(M > -9.5)` and `P(-M > 9.5)` partition the space with no atom in between.

Curves are built from **minute** candles, PAV-monotonised, and summarised as location (implied median),
scale (implied interquartile width) and tail (`P(|margin| > 13.5)`). Discipline enforced by test:

* a quote more than 15 minutes old is not "the price at t" — it is refused, not carried forward;
* nothing is ever read from after the reconstructed instant;
* books wider than 10 cents and empty books are dropped;
* fewer than 6 rungs cannot pin three components and the snapshot is refused;
* the tail is **never extrapolated** past the widest quoted strike — it is reported as unknown instead.

Shock instant is the inactive release, kickoff − 90 minutes, exactly, by league rule. Treatment is the
**corrected** surprise population (see `research/shocks/RESULTS.md`); the ungated version was 69% non-events.

## Result: the study cannot be run on 2025, and that is the finding

The 2025 `KXNFLSPREAD` minute-candle archive covers **22 games — week 18 and the playoffs only.** Kalshi did
not list spread ladders for the regular season, so there is nothing earlier to reconstruct.

| | games |
|---|---|
| ladder games with minute candles | 22 |
| mapped to a schedule row | 21 |
| pre **and** +60m ladder both reconstructable | 18 |
| — treated (≥1 genuine surprise inactive) | **14** |
| — control (none) | **4** |

Four control games cannot support a matched-control design. The preregistered gate — 40 treated and 40
control, fixed in the script before 2026 data exists — is not met, and the script prints
`NO VERDICT` rather than a number.

Descriptives, stated with their sample and **not** to be read as an effect:

| component | group | n | mean Δ (pre → +60m) | se |
|---|---|---|---|---|
| location | treated | 14 | +0.052 | 0.103 |
| location | control | 4 | −0.146 | 0.182 |
| scale | treated | 14 | +0.088 | 0.094 |
| scale | control | 4 | −0.064 | 0.241 |
| tail | treated | 8 | −0.0013 | 0.0025 |
| tail | control | 3 | −0.0050 | 0.0029 |

Every contrast is well inside one standard error of zero on both sides, and the control group is four games.
Nothing here is evidence for or against structural repricing.

The per-game trajectories are more informative than the aggregate: of 14 treated games, **6 show an implied
median that does not move at all** across the full 90 minutes (LA_CAR −9.92 at every offset; LAC_NE +3.50;
LA_SEA +2.55; LA_CHI −3.97; SEA_NE −4.62; GB_CHI −2.22). A ladder that is literally unchanged from
90 minutes out through kickoff is not a market absorbing news slowly — it is a market with no flow.

## Status: UNTESTED, not disproved

This is the one Part of session 4 that produced no answer, and the reason is data availability rather than a
negative result. Recorded as such. The machinery is built, tested and preregistered, so 2026 answers the
question with thresholds that were fixed before the data existed.

Registered as **H-025**. Primary endpoint: 40 treated and 40 control games with a reconstructable pre/+60m
ladder pair. α = 0.01 across the three structural components.

## What would make this answerable sooner

Spread ladders are listed for far more 2026 games than 2025 left behind, and the live capture stream records
them from listing. The binding constraint is not statistics — it is that the 2025 archive begins in week 18.
