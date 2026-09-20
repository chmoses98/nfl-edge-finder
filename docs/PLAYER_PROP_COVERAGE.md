# Player-prop coverage: which statistics have a model, and what kind

Generated from the 2026 week 2 board (`handicap-reports/latest`, packet built 2026-09-20 from ledger
`20260920T052030Z`). Reproduce with `scripts/handicap/run_nfl.py` and read
`analysis/games/<game_id>.json`, or recompute the table straight off `packet.json`.

This document answers one question per statistic: **what would a number attached to this contract actually
be?** "There is a model" is not an answer; "there is a validated model", "there is a research model", and
"there is nothing" are different claims with different authority.

## The board, by statistic

`listed` is every contract of that statistic on the 16-game slate, including contracts of games that had
already kicked off. The state columns are the accounting states of `nfl_edge/handicap/coverage.py`.

| statistic | listed | incumbent priced | Shadow v2 projected | manual handicap | identity unresolved | post-kickoff | coherent sim p | reconciled | deployed weight |
|---|---|---|---|---|---|---|---|---|---|
| receiving_yards | 1380 | 1257 | 0 | 0 | 0 | 123 | 1238 | 1238 | 0.00 |
| receptions | 1156 | 1056 | 0 | 0 | 0 | 100 | 1051 | 1051 | 0.00 |
| rushing_yards | 769 | 706 | 0 | 0 | 0 | 63 | 706 | 706 | 0.00 |
| touchdowns (anytime) | 706 | 619 | 0 | 30 | 4 | 53 | 610 | 610 | **0.25** |
| passing_yards | 276 | 257 | 0 | 0 | 0 | 19 | 257 | 257 | 0.00 |
| fantasy_points | 201 | 0 | 0 | 187 | 0 | 14 | 0 | 0 | — |
| carries | 167 | 158 | 0 | 0 | 0 | 9 | 158 | 0 | — |
| longest_reception | 155 | 0 | 0 | 146 | 0 | 9 | 0 | 0 | — |
| passing_tds | 134 | 124 | 0 | 0 | 0 | 10 | 124 | 124 | 0.00 |
| rush_rec_yards | 133 | 0 | **123** | 0 | 0 | 10 | 0 | 0 | — |
| field_goals | 128 | 0 | 0 | 0 | 120 | 8 | 0 | 0 | — |
| attempts | 93 | 87 | 0 | 0 | 0 | 6 | 87 | 0 | — |
| completions | 93 | 87 | 0 | 0 | 0 | 6 | 87 | 0 | — |
| interceptions | 93 | 87 | 0 | 0 | 0 | 6 | 0 | 0 | — |
| longest_rush | 62 | 0 | 0 | 59 | 0 | 3 | 0 | 0 | — |

Every one of those 5,546 contracts is in exactly one state. None is silently omitted.

## Four honest categories

**1. Independent football simulation, ZERO reconciliation authority** —
`receiving_yards`, `receptions`, `rushing_yards`, `passing_yards`, `passing_tds`.

The coherent simulation produces a football distribution and a reconciled probability for these, and the
deployed reconciliation weight is **0**. At weight 0 the reconciled mean *is* the market mean: the only
thing left that can move the probability away from the mid is the football SHAPE, which has never been
confirmed out of sample. Those rows are reported under `unranked_zero_weight_disagreements` and carry no
authority. The incumbent prices them too, and it is the incumbent's number that appears in
`model_probability`.

**2. Earned a non-zero reconciliation weight** — `touchdowns` (anytime TD), weight **0.25**, and nothing else.

Read this carefully, because it is the single easiest number in the repository to overstate.

* The weight was fitted on 2025 weeks 1–9 (1,670 rungs), confirmed on weeks 10–22 (0.15121 vs the market's
  0.15140, z = −0.99), and deployed at the smaller of the early-week and whole-season optima.
* **It does not make touchdown props validated bets.** The football-only model did **not** beat the market:
  over 3,720 settled anytime-TD rungs its Brier was 0.1583 against the market's 0.1570.
* **Large disagreements were dangerous.** Split by |football − market| at the rung: at 0.00–0.05 the best
  weight is 1.00; at 0.05–0.10 it is 0.10; at 0.10–0.20 it is 0.00 and the football Brier is 0.2283 against
  the market's 0.2097. Across every family, where the two disagreed by more than 0.10 the market won. **A
  large disagreement is a warning, not an opportunity.**
* The ranked gap is not even a pure football opinion: the reconciled probability re-locates the football
  shape onto the market's *estimated* mean, and on a thin two-rung ladder that estimate is poorly
  identified. On a live slate the mean ranked gap was +0.0115 against a football view of +0.0056, and 21 of
  225 ranked rows pointed the opposite way. Every ranked row therefore carries
  `football_disagreement_vs_mid` and `disagrees_with_own_football_view`.

A non-zero weight means exactly one thing: **this limited market/football blend earned non-zero research
weight under the preregistered procedure.** Nothing more.

**3. Priced by the incumbent, no independent research view** — `interceptions`, `attempts`, `completions`,
`carries`.

`carries`, `attempts` and `completions` have a coherent-simulation football probability but no reconciled
one; `interceptions` has neither. All four are priced by the incumbent, so bucket A, and none of them has a
research cross-check.

**4. No defensible model anywhere** — `longest_reception`, `longest_rush`, `fantasy_points`, `field_goals`,
and `first_td` / `first_td_team` (not player-stat families but the same situation).

These are bucket C (`MANUAL_HANDICAP`): the question is pinned, the subject is identified, and the packet
carries the football context to reason about them — but no engine owns them and none pretends to.

* `longest_reception` / `longest_rush` — the distribution of the MAXIMUM of per-target or per-carry gains,
  not a marginal stat model. The coherent simulation draws per-touch outcomes from empirical banks, so the
  maximum is in principle measurable from the same rows; it has never been scored as a functional.
* `fantasy_points` — a composite of several statistics, and many legs are team D/ST entities rather than
  players.
* `field_goals` — 120 of the 128 listed contracts are `IDENTITY_UNRESOLVED`: they are TEAM ladders listed
  under a player series ("New York G: 4+ Field Goals"), which the identity layer correctly refuses to
  resolve to a player. Kicker attempts also depend on drive outcomes, which no engine models.
* `first_td` / `first_td_team` — need the scoring ORDER, and the final-score simulation carries none.

## Newly surfaced, and what changed

`rush_rec_yards` (133 contracts) had no incumbent model and now shows **123 Shadow v2 research
projections** — v2 fits the sum as its own marginal from the same player simulation. Before the Shadow v2
join these contracts read as `UNSUPPORTED_MODEL` and nothing else.

## A named gap: no Shadow v2 projection for any quarterback passing statistic

Shadow v2 reports `DATA_UNAVAILABLE` for `passing_yards`, `passing_tds`, `attempts`, `completions` and
`interceptions` — 642 pregame contracts on this board. The cause is **not** a missing engine: the v2 data
arm fits all five, on 6,753 quarterback-games of 2013–2025 history
(`passing_yards: normal`, `passing_tds: negbin`, `attempts: normal`, `completions: normal`,
`interceptions: negbin`).

The cause is a point-in-time guard working exactly as designed. The QB population mask is
`(position == "QB") & qb_starter`; `qb_starter` is read from the schedule's `home_qb_id` / `away_qb_id`;
and `mask_target_season` blanks those for every UNPLAYED game, because nflverse fills them in during the
week and finalises them after kickoff — they are not knowable at the snapshot. So no prospective row can
satisfy the mask, and the fitted models have nothing to apply.

Until 2026-09-20 every one of those contracts reported *"no data distribution for statistic
'passing_yards'"*, which reads as "this engine cannot model passing yards" and is false. The refusal now
names the real cause, and the run summary carries a `population_empty` block so the hole is visible at run
level rather than only at the bottom of eleven thousand rows.

**Nothing is lost operationally** — the incumbent prices all five families, so they are bucket A — but
Shadow v2 has no independent cross-check on any quarterback passing market. Closing it needs a
point-in-time starting-quarterback source (the depth charts and ESPN/Sleeper data in the context capture are
the obvious candidates) plus the validation that any new feature requires. It is not an overnight change.
