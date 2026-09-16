# The simulation engine (sim-1.x)

> Shadow research. Zero betting authority. The incumbent pricer, its ledger, the three-arm experiment
> (`H-20260910-026`) and every artifact frozen for Week 1 are untouched by this layer.

## Why it exists

Week 1 2026 showed the incumbent player-prop layer materially behind the market it was scanning
(`data/shadow/scorecards` on `market-data`: player-prop payout MSE 0.174 model vs 0.154 market; carries
0.288 vs 0.228; a systematic −0.06 signed bias), and its largest disagreements were its worst contracts
(Price 50+ rush yards priced 0.08 against a 0.52 market after Charbonnet was ruled out; Stevenson 3+
receptions 0.22 against 0.59 after Montgomery was ruled out). The 2025 archive had said the same thing in
advance: the incumbent is *encompassed* by the closing price (market coefficient ≈ 1, model ≈ 0), and
two-thirds of its disagreement is a dispute about the mean that the market wins.

The incumbent has three structural gaps a scanner cannot paper over: every player is projected alone
(no reconciliation with the team's volume, no redistribution when a teammate is out), the pass/rush split
does not depend on the game script, and nothing on a player's line knows the opponent. This layer is
the replacement architecture:

```
nflverse history ─► strictly-prior features ─► fitted primitives ─► one Monte Carlo game ─► every market
                     (team, player, opponent)   (bundle_<season>)     (20,000 common rows)     (one ladder = one distribution)
                                                                                                    │
                                                                    Kalshi ladder ─► market centre ─┴─► reconciled probability
                                                                                     (weight fitted out of sample, per family)
```

## What one simulated row contains

| stage | what is drawn on the row | fitted from |
|---|---|---|
| score | (margin, total) from the incumbent's residual bank around the centre; home/away points | `nfl_edge/pricing/game_env.py` (unchanged) |
| touchdowns | offensive TD count given points; pass/rush split given the row's pass rate and margin | `models.fit_game_env` |
| volume | plays and pass rate for each team **conditional on the row's margin and total** (a 14-point lead lowers the pass rate on that row); the two teams' residuals are correlated | ridge on team-game rows, `PLAYS_FEATURES`, `PASS_RATE_FEATURES` |
| dropbacks | sacks, scrambles, pass attempts, targets, kneels, designed rushes | league/team/QB rates |
| opportunity | Dirichlet-multinomial allocation of designed carries and targets over the players available on that row (questionable players sit out on the rows their availability draw says so; the rest absorb the share) | `models.fit_share_model`: ridge propensity from prior usage, depth-chart rank cell prior (an RB1 with no history starts at the RB1 prior), Dirichlet concentration by moments |
| efficiency | per-carry and per-target outcomes from **empirical banks** binned on the player's expected per-touch value (runner history, opponent's allowed rate, own team's rate, position, the row's margin); completions with the player's catch probability; yards-given-completion rescaled to the player's expected yards per reception | `models.fit_carry_model`, `models.fit_target_model` |
| identities | Σ player carries = team rush attempts; Σ targets = team targets; QB passing yards = Σ receiving yards; completions = Σ receptions; TDs reconcile with the team count | `simulate.coherence_report` (every row, every game, refused on failure) |

The centre (expected home margin and total) is an input, never derived here: the prospective path reads
the Kalshi-implied lines (50% crossings of the monotone spread and total ladders, falling back to the
consensus line), the backtest uses the consensus closing line, and the market-free arm can pass the
three-arm `DATA_ONLY` centre. Game families are therefore reported as `MARKET_CENTRED_GAME`: the layer
claims no football deviation on them, by design, until `H-20260910-026` reads out.

## Point in time

The invariant: **for every prediction row at time T, every statistic used to build that row depends only on
observations strictly earlier than T, or is a constant frozen before the evaluation period.** That includes
the shrinkage targets, which is where the first version of this layer failed.

* **Shrinkage priors are a fitted artifact, not a statistic of the frame.** League levels, pooled rate
  numerators/denominators and position rates are fitted by `features.fit_priors` on the RAW rows of seasons
  strictly before the season being predicted (`training.fit_priors_for`), carried on the bundle as
  `bundle["priors"]`, and passed into every feature call. `features.team_features` and
  `player_features` raise `MissingPriors` rather than computing their own, `fit_bundle` refuses a
  `PriorSet` whose fit seasons reach the evaluation season, and the walk-forward rebuilds its frames once
  per evaluation season. The first version computed these targets over the whole assembled frame, so a
  week-1 projection's league play-volume prior had seen week 18 of the same season.
* Every per-subject feature is an exponentially decayed sum over that subject's strictly earlier rows
  (`features.decayed_prior_sums`). Eligible players who did not appear get a **phantom** row that reads the
  state and leaves it untouched.
* Eligibility uses the week's roster file (status `ACT`; `RES`/`INA`/`CUT`/`DEV` are unavailable even
  if the depth chart still lists them), the depth chart at the cutoff (daily snapshots from 2025, weekly
  before), injury designations from the **content-addressed vintage** at the cutoff (below), and,
  prospectively, the newest Sleeper capture at or before the cutoff.
* History for a prospective run is every game whose kickoff plus four hours precedes the cutoff.
* **Injury vintages.** `prospective.injury_vintage` resolves the nflverse injury release through
  `shadow_v2.vintage_snapshots.resolve_injuries`: the newest content-addressed snapshot whose retrieval
  time is at or before the cutoff, and **nothing at all** rather than the mutable file when none qualifies.
  The snapshot path, sha256, retrieval instant, reason and per-status counts are recorded on every run's
  manifest. Sleeper supplements it and can only tighten a designation, never clear one
  (`tests/test_sim_injury_vintage.py`).

`tests/test_sim_pit.py` is the adversarial suite: it multiplies every evaluation-season game after week 3
by 1,000 and asserts that no feature of an earlier row moves by a bit, with a negative control proving the
same poison does reach later rows and a second control proving that priors refitted over the whole frame
*would* move.

## Reconciliation

`reconcile.reconcile_distribution` re-locates the football distribution so that

    final mean = market mean + w_family × (football mean − market mean)

with the football **shape** kept (the market ladder rarely identifies a tail; the simulation always has
one). `w_family` is fitted by `scripts/sim/reconciliation_study.py` on the 2025 archive — weights on
weeks 1-9, **confirmed** on weeks 10-22 against the market with game-clustered standard errors, then the
whole-season fit — and `reconcile.deploy_weights` deploys a non-zero weight only when the early fit had
enough rows AND the later-week confirmation was not worse than the market beyond z = 1, taking the smaller
of the two optima. A family that fails any of that deploys 0: reported football-only at the market mean,
**never ranked**. Only the close (T-0) is evidence — the historical simulator's centre is the consensus
closing line, so an earlier horizon would score the football arm against a price it was not centred on.
See `research/simulation_engine/RECONCILIATION.md`.

## Outputs

`scripts/sim/project_week.py` writes one row per contract to
`data/shadow/sim/<day>/<run_id>.sim-1.0.0.projections.jsonl.gz` (write-once) with: football-only,
market and reconciled probabilities; the reconciliation weight; the football / market / final means and
football sd; the disagreement of the reconciled probability against the mid (and the raw football one,
separately); support state and reason; centre and its source; every version (sim, engine, models,
reconcile, bundle training seasons) and every instant (market observed, generated, feature cutoff,
kickoff). The handicap packet attaches these per market (`simulation`) and per game
(`simulation.largest_reconciled_disagreements`), and `game_priority` now ignores the incumbent's raw
disagreement entirely: only a reconciled disagreement moves the review priority, capped below the
injury and weather signals.

## Evidence

Every committed summary is a pure render of its JSON by `scripts/sim/write_results.py`, and
`tests/test_sim_results_consistency.py` re-renders and compares, so a table cannot drift from the data.

* `research/simulation_engine/RESULTS.md` — walk-forward 2023 → 2024 → 2025 primitives (MAE / RMSE /
  bias / CRPS / coverage / ladder Brier) and the coherence audit.
* `research/simulation_engine/RECONCILIATION.md` — the 2025 Kalshi head-to-head, fitted / confirmed /
  deployed weights, Brier curves, disagreement bands, encompassing regression.
* `research/simulation_engine/RUSHING_ABLATION.md` — the rushing input audit: what was retained, what was
  rejected and why, and the walk-forward ablation that kept none of it out of the deployed model.
* `research/simulation_engine/role_signal_2025.json` — whether the existence of a Kalshi ladder identifies
  a role the depth chart missed (it does; the share model already absorbs it, so nothing is deployed).
* `research/simulation_engine/WEEK1_2026_DIAGNOSTIC.md` — **development / diagnostic only**.

## What is deliberately not done yet

* A genuinely point-in-time **T-24h** study. It needs a T-24h game centre (the Kalshi archive's own T-24h
  spread and total ladders) and dated injury/depth vintages for 2025; until then T-24h is reported as
  `NON_PIT_DESCRIPTIVE` and cannot fit or promote a weight.
* **Rushing efficiency covariates.** Offensive-line blocking, opponent-adjusted defensive front, yards
  before/after contact, stuff and explosive rates were all built, audited and ablated; per-carry yardage
  has an out-of-sample r² of 0.006 and no arm moved it materially, so none is deployed. FTN scheme data
  and observed weather were rejected on point-in-time grounds. See `RUSHING_ABLATION.md`.
* No in-game QB replacement branch (Darnold → Lock) beyond the fitted starter-share tail.
* Game-level centres carry no football deviation (see above).
* Longest reception/rush, fantasy points, interceptions, field goals, first-TD scorer, period markets:
  unsupported, reported as `UNSUPPORTED_STAT` — a professional model passes on what it cannot price.
* Weather, offensive-line continuity, FTN concepts and PFR yards-before-contact are not features yet;
  the opponent term is the defence's allowed rates and the offence's own rates.
* The Dirichlet concentration is one number per family; it should depend on the concentration of the
  expected shares.
* Component attribution ("+2.4 yards workload") is reported as the football / market / final means only;
  additive attribution is not statistically valid on a nonlinear simulation and is not faked.
