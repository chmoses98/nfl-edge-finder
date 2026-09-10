# The prospective three-arm game-centre experiment

> Shadow research. Zero betting authority. Preregistered as `H-20260910-026`.

## The question, in plain language

The incumbent prices every game contract from a distribution whose **centre is the market** (the Kalshi-implied
spread and total) and whose **shape is history** (jointly sampled residuals of past games around their lines). The
closing-line research showed that a football-only model adds nothing to the *closing* market
(`research/game_model/RESULTS.md`). That is not the question the shadow pricer lives with. It prices at T-24h,
T-6h, T-90m and T-30m, and whether football data contains information the market has **not yet** incorporated at
those horizons is unresolved. This experiment resolves it, prospectively and honestly, by changing exactly one thing.

| arm | centre | distribution |
|---|---|---|
| **CURRENT_MARKET_PRIOR** (control) | the market sets it: Kalshi-implied spread/total, or the documented consensus fallback | historical residual simulation, 40,000 rows |
| **DATA_ONLY** | football data sets it, independently: point-in-time team ratings through a frozen model; no same-game market input of any kind | the **same** residual machinery, the **same** draws |
| **HYBRID_30_DATA** | 0.70 × CURRENT centre + 0.30 × DATA_ONLY centre, for margin and for total | the same again |

Why the common distribution machinery matters: if DATA_ONLY used its own variance, its own overtime model and its
own random numbers, a difference between arms would be a difference in ten things. Here every arm gets one set of
uniform draws per game and the incumbent's own residual bank, so the only thing that differs is the centre — which
is the thing the question is about (`nfl_edge/arms/crn.py`).

## What happens automatically

**Before every game.**

* Every ~2 hours the shadow-pricing cycle prices the slate as before. `price_slate.py` now also writes a
  `game_env.json` sidecar beside the ledger snapshot with the exact centre each game was priced from (nothing about
  the pricing changed). `three_arm_snapshot.py` reads that sidecar and the snapshot's rows, rates the teams from
  football data as of the capture time, blends, simulates the three arms on common random numbers, prices the same
  game contracts the incumbent priced, and writes one immutable three-arm snapshot. The incumbent's own price for
  every ticker is carried alongside and the CURRENT arm is checked against it (`reproduction_check`, Monte Carlo
  tolerance); a snapshot that fails the check is flagged DEGRADED, never silently used.
* At **T-24h, T-6h, T-90m and T-30m** before every kickoff cluster, `three-arm-horizons.yml` wakes (every 15
  minutes, stdlib-only gate, blobless fetch of the marker list) and, only when a horizon is due, rates the teams
  from four seasons of play-by-play and freezes the three arms from the latest capture. No ledger snapshot exists at
  that instant, so the CURRENT centre is **re-derived with the incumbent's own estimator** on the same quotes
  (`nfl_edge/arms/incumbent_center.py`); the record says `center_provenance: incumbent_estimator_rerun`. The
  horizon is then marked captured by one new marker file; a failed build leaves it due; a horizon whose kickoff
  passed is MISSED and is never reconstructed.
* Every record carries `observed_at < kickoff` **and** `generated_at < kickoff`, or it is written as
  `POST_KICKOFF_EXCLUDED` with no forecast. A snapshot generated more than four hours after its capture is refused.

**After every game.**

* The 3-hourly postgame job (`postgame-settle.yml`) now also runs `settle_arms.py` and `player_autopsy.py` behind
  the same cheap gate. Both use the incumbent's result book, readiness gate (a game is deferred whole until its
  final is proven and its statistics are published), strict pre-kickoff close and settlement engine. Arm evaluations
  and autopsies are write-once batches; a contradictory rerun fails the run and writes nothing.
* The closing market **centre** is measured the way the incumbent measures a snapshot centre — `implied_game_lines`
  over the last complete pre-kickoff quotes — so "toward the close" is a like-for-like statement.
* `arm_report.py` then rebuilds the per-game, weekly and cumulative reports from the durable evidence alone.

Nothing in the pregame or postgame path needs a human. Nothing in it can reach the handicap packet, the gates, the
risk policy, Airtable or the recommendation ledger (`tests/test_run_nfl_isolation.py`, `tests/test_funnel.py`).

## Where the evidence lives (`market-data`, append-only)

| path | what |
|---|---|
| `data/shadow/arms/<day>/<run>.three-arm-1.0.0.arm_games.jsonl.gz` | one row per game: all three centres, lineage, simulation identity, reproduction check |
| `data/shadow/arms/<day>/<run>.three-arm-1.0.0.arm_contracts.jsonl.gz` | one row per contract: the three probabilities, the incumbent's own, the market it saw |
| `data/shadow/arms/<day>/<run>.three-arm-1.0.0.funnel.json` | the BET/WATCH/PASS accounting of that snapshot |
| `data/shadow/arms/horizons/<slate>__<cluster>__T-<n>m.json` | horizon capture markers |
| `data/shadow/arm_evaluations/<game_id>/arm-eval-1.0.0.<batch>.arm_game_evaluations.jsonl.gz` | centre errors, market at snapshot, closing centre, movement |
| `data/shadow/arm_evaluations/<game_id>/arm-eval-1.0.0.<batch>.arm_contract_evaluations.jsonl.gz` | settlement, close, the three probabilities verbatim |
| `data/shadow/player_autopsy/<game_id>/autopsy-1.0.0.<batch>.autopsy.jsonl.gz` | one diagnosis per player-stat projection |
| `data/shadow/arm_reports/<batch>/{cumulative,weekNN}.REPORT.md`, `games/<game_id>.REPORT.md` | derived reports (regenerable) |

The incumbent ledger and its evaluation corpus are read and never written. Identity is deterministic
(`sha1(run_id | game_id or ticker | arms_version)`); an identical rerun is a no-op; a contradictory one fails closed.

## DATA_ONLY, exactly

The Milestone-E research model made reusable and point-in-time safe (`nfl_edge/arms/data_only.py`):

* opponent-adjusted team ratings by weighted ridge on prior team-games (`team_ratings.solve_ratings`, half-life 10
  weeks, prior seasons × 0.4, ridge 4) over eleven play-by-play metrics — EPA/play, success rate, dropback and rush
  EPA, non-garbage EPA, explosive rate, sack rate, turnover rate, PROE, special-teams EPA, early-down EPA;
* matchup features (home offence + away defence, away offence + home defence, their difference), rest difference,
  divisional game, neutral site, indoor;
* ridge margin and total models (λ = 30) fitted on seasons 2018–2025 and **frozen** as
  `research/three_arm/data_only_artifact_2026.json` (sha `e544b99917b9d0b1`, refit-reproducible from the frozen
  research features).

Point in time: only games whose result is published and whose kickoff plus four hours precedes the capture time
enter the ratings, so Thursday informs Sunday and a game in progress never does. The design matrix is a
**whitelist**; the schedule is stripped of every market column before any feature code runs; a row that still
carries one is refused; and the tests poison the market columns and assert the projection does not move by a bit.
Not included, and recorded as unavailable inputs: quarterback identity, weather, injuries — none has a pre-2026
validated coefficient, and a coefficient invented now would be a guess.

If DATA_ONLY cannot produce a projection (no artifact, no rating for a team, no football data), it is
`UNAVAILABLE` with a reason and **HYBRID is unavailable too**. There is no fallback to the market anywhere.

## What is measured

Sample units: raw snapshots (descriptive only), canonical T-24h / T-6h / T-90m / T-30m (one row per game or
contract per horizon by the incumbent scorecard's documented rule), and latest-pregame (primary). Every block prints
rows, contracts, games and weeks. Uncertainty is clustered at the game.

* Game centre: margin and total MAE / RMSE / bias per arm; paired differences (arm − CURRENT, arm − market at
  snapshot, arm − close) with game-level SEs and intervals; implied home/away score errors.
* Information addition: for DATA_ONLY and HYBRID, the deviation from the snapshot market centre, whether it pointed
  toward or away from the closing centre, whether the arm was closer to the actual result than the market, by
  disagreement band (≤1, 1–2, 2–3, 3–5, >5 points — descriptive cuts of one sample, never independent studies).
* Contracts: Brier and log loss in event space (binary settlements only), payout MSE in contract space, against the
  market midpoint at the snapshot and at the close; paired differences with a game-clustered bootstrap; calibration.
* **No verdict before 64 distinct games.** Below that every report says INSUFFICIENT_EVIDENCE. Above it, intervals.
  There is no "winning model" banner in the code.

## Player props: instrumented and autopsied, not redesigned

Player props are a different architecture and are **not** part of the game-centre hybrid. Their probabilities did
not change. Every supported player projection now freezes the real intermediates the model computes — the projected
statistic mean (`mu`), the projected opportunity mean (`muo`), the efficiency feature the family conditions on, the
family, the fitted quantiles, the EWMA inputs, availability branches — in the ledger (schema 1.1.0, optional fields,
old rows unchanged). After each game the autopsy places every projection against the box score, standardises the miss
inside the model's own distribution, and classifies deterministically: OPPORTUNITY_MISS, EFFICIENCY_MISS,
AVAILABILITY_MISS, TEAM_VOLUME_MISS, UNEXPLAINED_VARIANCE, NO_LARGE_MISS, INSUFFICIENT_DATA, with a separate
model-vs-market verdict. Missing usage is explicit. No player is special-cased.

## The funnel

`nfl_edge/shadow/funnel.py` replays the existing gate sequence mechanically over each snapshot with the model's own
contract value standing in for a handicap: discovered → mapped → supported → priced → positive disagreement against
the *executable* ask → tradable book → data quality → executable price (the zero-net-EV ceiling from the committed
fee schedule, via the preflight's own `net_executable_ev`) → observed liquidity → BET / WATCH / PASS. WATCH carries the
ceiling; PASS carries its reasons. It introduces no threshold and has no authority; it answers whether one
recommendation means one good contract or a board that mostly failed mapping and coverage.

## What this cannot do

* It cannot change anything. The evaluator measures, reports and diagnoses; it opens no weight, feature, threshold,
  gate or policy for writing, and `tests/test_three_arm_preregistration.py` pins the constants.
* It cannot backfill. The opener (`2026_01_NE_SEA`) was played before this code existed; it is excluded by the
  kickoff gate and by the registry text, and the tests try to insert it and fail.
* It cannot settle what the incumbent cannot: refused families stay refused, missing closes stay missing.

## Audit findings that shaped it (Phase 0)

1. **The incumbent's centre** is chosen in `scripts/shadow/price_slate.py`: `implied_game_lines` over the liquid
   full-game winner/spread/total quotes (grid −17…17 × 34…62 by 0.5, 12,000 draws per grid point, width ≤ 0.06,
   ≥ 6 liquid rungs), else the nflverse consensus line, else no environment. Then `simulate_game(…, n=40000)`.
2. **Randomness**: one `ResidualBank` seeded 11 per run whose generator is consumed sequentially by every grid
   search and every simulation, in game order. The grid search's own `seed=3` generator is created and unused.
   This is why the harness reproduces the CURRENT arm to Monte Carlo tolerance rather than bit for bit.
3. **Residual population**: REG games since 2016 with a result and a spread line, residual = result − spread and
   total − total line, season half-life 3, fractional-part matching of lines, overtime model from historical OT games.
4. **The player model's game context is the consensus line**, not Kalshi (`prospective.upcoming_from_markets` reads
   the schedule's `spread_line`/`total_line` into `implied_total`). Recorded on each row as `implied_total_input`.
5. **Horizon runs never published a ledger** (by design and by test); only the 2-hourly cycle does. The canonical
   T-24h…T-30m challenger record therefore needed its own conductor and its own CURRENT-centre derivation.
6. **`eval_report.py` crashed on every run** after writing its files (`KeyError: n_evaluations`, hidden behind
   `continue-on-error`); fixed in passing because the new reports share that step.
7. **Evaluations join by `prediction_id`**; the store is generic enough to host the arm and autopsy corpora under
   their own suffixes, which is what was done rather than a second store.
8. **Nothing on the report path can import the experiment**: the isolation audit's reachable set was checked and a
   test now asserts the arms package, the funnel and the autopsy are unreachable from the packet and the gates.
