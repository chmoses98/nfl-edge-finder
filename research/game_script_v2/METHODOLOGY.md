# GAME SCRIPT V2 and the five-season study: methodology

**RESEARCH_ONLY.** Nothing in this directory changes betting authority, production thresholds, staking, incumbent
model probabilities, recommendation authority or reconciliation weights. The incumbent simulation (sim-1.1.0) is the
foundation and is preserved: with every research switch off, the bundle, the simulated rows and every evaluation
number are bit-identical to the incumbent's (shown on 2023 and 2024 against an unmodified-code reproduction, and
pinned by `tests/test_five_year.py`).

Every design choice below was registered in `PREREGISTRATION.md` before the corresponding result existed. Stage 2
(R1, and the QB-starter design that was rejected on 2018-2020 and never run) was registered after the baseline's
error decomposition and before any arm result was read.

## 1. The five-season frozen baseline

`scripts/sim/baseline_5y.py` runs, for each evaluation season Y in 2021-2025, exactly the calls of
`scripts/sim/walkforward.py`: `training.fit_priors_for(Y)` (shrinkage targets fitted on raw rows of 2016..Y-1),
`training.assemble(2016..Y)` (frames rebuilt per evaluation season; every feature strictly prior to its game),
`training.fit_bundle(Y)` (fitted on 2018..Y-1; 2016-17 warm the EWMAs), `backtest.run_season` (10,000 rows per game,
consensus closing line as the market centre, seed `11 + game index`) and `backtest.evaluate`. Two additive changes,
both behaviour-preserving:

* a game whose inputs cannot be built is listed in `skipped` with its exception instead of being dropped silently;
* a read-only `on_game(res, gi)` hook receives each coherent game's rows. It has no access to a generator; the bank's
  generator is shared across a season's games, and `tests/test_five_year.py` shows a later game is unchanged by the
  hook.

`nfl_edge/sim/baseline_report.py` re-derives `evaluate`'s per-season numbers (and checks them against what `evaluate`
wrote), pools the seasons, and attaches game-clustered bootstrap intervals (games resampled, never rows: one game
contributes dozens of correlated player rows). It adds a randomized PIT (`F(y−1) + U·p(y)` on the stored pmf), because
endpoint-inclusive interval coverage overstates calibration for small integer outcomes, and an error decomposition
along TEAM VOLUME → PLAYER SHARE → EFFICIENCY by sequential substitution.

Evidence classes: 2023-2025 RETROSPECTIVE_DEVELOPMENT (the layer was built against them), 2021-2022 RETROSPECTIVE
CHALLENGE (never scored before, still retrospective), 2026 PROSPECTIVE (none claimed here).

## 2. GAME SCRIPT V2 (`nfl_edge/sim/script_v2.py`, sim-script-2.0.0)

Additive to sim-script-1.0.0, which is untouched. A pure function of a `SimResult`: no random draw (enforced by a test
that replaces every numpy sampler with one that raises), no mutation (every array compared before/after).

* **Lattice.** control × scoring = nine cells, exhaustive and mutually exclusive by construction. Control uses the
  favourite-oriented final margin (favourite from the centre the simulation used; pick'em oriented on home and
  labelled home/away); thresholds `ONE_SCORE = 8`, `SHOOTOUT_OVER = LOW_SCORING_UNDER = 10` are imported from
  `research/script_autopsy.py`. Probabilities are row counts over the row count, so they sum to exactly one.
* **Cell state.** For each cell: probability, rows, home/away points, margin, total, each team's plays / pass
  attempts / dropbacks / designed rushes / pass rate / targets, target concentration, and the major players'
  targets / carries / pass attempts with their opportunity CV and active share -- all on that cell's rows.
* **Labels** are generated from the cell definition and the cell's own medians. No text is written first.
* **Marginal events** (overlapping) use one function for simulated rows and realized games.
* **Not simulated, therefore absent:** lead changes, time leading, scoring sequence, early blowout, late comeback,
  red-zone trips, routes, snaps, drives.
* **Provenance:** `MARKET_CENTRED_GAME`. The (margin, total) of every row is the market centre plus the incumbent's
  historical residual bank, so a script probability describes how the market-centred distribution splits. It is not
  a football edge on the side; a data-only game model that earns an out-of-sample deviation from the market would be a
  separate result.

## 3. Script × market matrix and thesis dependency

`contract_cash` returns each contract's per-row cash value with the pricer's own settlement semantics (pinned equal to
`price_slate`'s `p_football` to 1e-12): GAME_WINNER pays 1 on a win and 0.5 on a tied row, SPREAD `x > floor_strike`,
TOTAL / TEAM_TOTAL `x >= threshold`, PLAYER_STAT `clip(round(x), 0, GRID_MAX) >= ceil(threshold)`. Unsupported
contracts are refused with a reason (period, family, identity, eligibility, rules, statistic).

For each contract: P(cash), P(cash | script) for all nine cells, contributions, the major-script floor (minimum over
cells with P(s) ≥ 0.10 and ≥ 200 rows), script robustness at 0.50 / 0.55 / 0.60, failure-script mass (P(cash | s) <
0.50) and the win-contribution HHI. `P(cash) = Σ P(s) P(cash | s)` holds to floating tolerance by construction and is
asserted.

Thesis dependency is computed on the same rows: cash correlation, joint cash probability, both conditionals, shared
failure mass, lift and the Jaccard overlap of winning rows. In the packet it is computed among each ladder's headline
rung (the rung nearest 0.50) and only pairs with |correlation| ≥ 0.30 are listed. None of it changes a stake.

## 4. Script calibration (`nfl_edge/sim/script_backtest.py`)

Per game: the nine-cell distribution from the scored rows, the realized cell from the same function, and two
training-only baselines (B0 unconditional; B1 within the absolute closing-spread bucket). Multiclass Brier, smoothed
log loss, top-script probability / hit, entropy, one-vs-rest reliability and ECE, predicted vs realized frequency per
cell; marginal events scored by Brier against the same baselines. The calibration test compares the model's ECE with
the ECE distribution of a perfectly calibrated forecaster on the same games (outcomes drawn from the forecasts). The
verdict rule is the one registered in `PREREGISTRATION.md` section 3.

## 5. Opponent-adjusted ratings (`nfl_edge/sim/opponent_adjust.py`)

A weighted ridge `y = μ + off_team + def_opp + h·home + e` per metric, re-solved at every (season, week) on strictly
earlier games, with the incumbent's recency half-life and season carry, a three-season window, shrinkage toward the
window mean and a ridge strength chosen per metric on Y-2 / Y-1 only. Tests poison every later game by ×1000 and show
earlier snapshots unchanged (with a negative control), show the λ choice ignores the evaluation season, and show the
solver removes schedule strength that a raw allowed-average keeps. The matchup expectation `mx_<metric>` is attached
to the team's own row, so the volume and efficiency models read the opponent's adjusted defence directly.

The arms (A1-A5, R1) and the promotion rule are in `PREREGISTRATION.md` sections 5-6. Evaluation is paired on A0's
scored rows with identical seeds, and every interval is game-clustered.

## 6. Score path, injuries, weather

* **Score path** (`nfl_edge/sim/score_path.py`): a deterministic kernel conditional of quarter-score events on each
  simulated row's final state, against a spread-bucket historical baseline; rejected unless it wins (section 7).
* **Injury redistribution** (`nfl_edge/sim/injury_validation.py`): descriptive calibration of carries and targets for
  the populations in section 9 (plus one labelled post-hoc broadening).
* **Weather** (`nfl_edge/sim/weather_research.py`): observed weather only in NON_PIT descriptive tables; 2026 forecasts
  only through `weather_vintages.latest_before` at the cutoff, with retrieval and lead time, accumulate-only.

## 7. RUN NFL exposure

`price_slate(..., scripts_v2=...)` builds the GAME SCRIPT V2 document for each game after that game's contracts are
priced (projections are byte-identical with or without it -- tested) and refuses an incoherent game
(`UNSUPPORTED_COHERENCE`). `scripts/sim/project_week.py` writes it write-once as `<run_id>.sim-1.1.0.scripts_v2.json.gz`.
The packet (`handicap/script_block.game_script_v2_view`, stdlib only) loads only the file of the simulation run the
packet attached, fails open, and is read by no gate, preflight, risk, approval, evaluation or scorecard module
(tested). The rendered section shows numbers only -- no adjective grades a market.

## 8. Reproducing everything

```
python scripts/data/nflverse_download.py --only pbp,schedules,weekly_rosters,rosters,snap_counts,injuries,depth_charts,players,teams,ff_playerids --seasons 2016-2026
python nfl_edge/data/silver.py 2016 2026 && python nfl_edge/data/ids.py
python scripts/sim/walkforward.py --seasons 2023,2024,2025 --out-dir <REPRO>     # unmodified-path reproduction
python scripts/sim/reproduction_check.py --repro-dir <REPRO>
python scripts/sim/baseline_5y.py --seasons 2021,2022,2023,2024,2025 --n-sims 10000
python scripts/sim/oppadj_ablation.py features
python scripts/sim/oppadj_ablation.py run --arm <A1|A2|A3|A4|A5|R1> --seasons <Y>   # every arm x season
python scripts/sim/script_backtest.py
python scripts/sim/game_script_v2_report.py baseline
python scripts/sim/game_script_v2_report.py validation      # needs the 2026 weather vintages from market-data under data/context
python scripts/sim/game_script_v2_report.py ablation
python scripts/sim/write_game_script_v2.py
```

nflverse rebuilds releases in place, so a later download can differ from the one used here (the reproduction audit
found exactly that for `snap_counts_2020`). The download manifest of this study is not committed (bronze is
gitignored); the JSON artifacts record what was computed.
