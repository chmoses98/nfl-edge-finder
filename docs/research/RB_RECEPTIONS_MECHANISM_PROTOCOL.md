# Football Signal Discovery Lab — Wave 2B (NFL): RB receptions market-mechanism study — PROTOCOL

Status: **PRE-REGISTERED.** This file is committed before any mechanism diagnostic is computed against outcomes.
Results go to `docs/research/RB_RECEPTIONS_MECHANISM_RESULTS.md` and `research/rb_receptions_mechanism/`
(artifact `nfl_rb_receptions_mechanism/1.0.0`). Unexpected observations found later are reported as
**post-hoc characterisations**, never re-labelled as pre-registered.

## 0. What this study is and is not

* **Purpose:** explain *why* YES contracts on the RB receptions natural rung settled below their market prices in the
  historical sample (Wave 2A: 2025 natural-rung NO +8.5 %, YES −25.1 %; 2026 replay NO +11.7 %, YES −20.3 %).
* **Explanatory only.**
  * It creates no betting rule, filter, cap, threshold, badge, recommendation, stake or verdict.
  * It changes no production code: projections, Shadow v2, RUN NFL, board, pricer, router, staking or SIFT.
  * It does not touch Wave 2: `NFL-PROP-PROS-001` keeps its rule, natural rung, tie-break, checkpoint, sample
    counts, scheduler and ledgers exactly as frozen. Pins: candidates `5f31bd3b…3436`, prop models
    `7e308d26…c6f9`, classifier `eeec3777…a981`.
* **No subgroup is promoted.** A subgroup that looks profitable becomes, at most, an entry in
  `docs/research/RB_RECEPTIONS_MECHANISM_FUTURE_HYPOTHESES.md`, and is not tested here.
* **Contamination.** Every period studied here (2025 weeks 9–18; 2026 weeks 1–5) was used by Wave 1 to discover the
  pattern. Nothing here is independent evidence for or against the edge. The only clean test is the frozen
  prospective Wave-2 stream, which this study never reads (no Wave-2 settlement exists yet, and none will be read).

## 1. Data and provenance

| Input | Source | Timestamp safety |
|---|---|---|
| 2026 frozen PROP-001 rows (natural rung, both-side quotes, settlement) | `research/signal_discovery_wave2a/replay_records_2026.jsonl.gz` (Wave 2A, code `227d3758`, market-data `4f049279`) | Frozen job's own observe/enter stages; every quote pre-kickoff (close-2.1.0) |
| 2026 every stream-stat ladder at the same checkpoint | `research/signal_discovery_wave2a/baseline_ladders_2026.jsonl.gz` | Same close-2.1.0 selection and identity rule |
| 2026 quote history (price movement, volume, open interest, top-of-book size) | `market-data@4f04927982a1` capture `*.quotes.jsonl` and `*.manifest.json`. Only full-game player-stat rows are kept; the extract is committed with its hash. | Rows with `observed_at` < kickoff only |
| 2026 exchange settlement | `market-data@4f049279` discovery run `20261008T163830Z` (`result`, `settlement_value_dollars`, `rules_primary`, `rules_secondary`) | Post-game, used only for outcomes |
| 2025 RB ladders | `market-data@4f049279` `data/kalshi/backfill/horizons/*.jsonl`. YES bid/ask candles at T-48h, T-24h, T-12h, T-6h, T-3h, T-90m, T-30m and T-0, with exchange `result`. | Horizon snapshot before kickoff |
| Player stats, schedules, snaps, depth charts, injuries | nflverse, downloaded 2026-10-09. The injury input for 2026 pregame rows is the market-data vintage index, as in Wave 2A. | Pregame features use strictly earlier games |
| Frozen player model | `research/signal_discovery_wave2/models/prop_models_2026.json` (`RB_receptions` ridge, median offset, residual quantiles q10/q25/q75/q90) | Trained 2016–2025; applied unchanged |

* **2025 pricing is labelled.** The 2025 archive has no captured NO quote. The 2025 NO ask is `1 − YES bid`,
  labelled **`RECONSTRUCTED_NO_ASK`** on every row and in every table. It is never presented as a captured ask.
* **2026 pricing** uses the captured side-specific asks: **`CAPTURED_NO_ASK`**.

## 2. Populations (fixed now; never pooled)

All membership is decided without reading any outcome. Settlement is attached afterwards.

* **P1 — 2026 RB receptions, natural rung, genuine both-side prices.**
  * The Wave-2A replay's `NFL-PROP-PROS-001` ENTRY rows with status `ELIGIBLE` and a SETTLEMENT row `SETTLED` (83).
  * The natural rung is the one the frozen entry stage stored, recomputed and checked with the frozen `W.ladder`:
    valid `0 < bid ≤ ask < 1`, width ≤ 0.10, minimum `|mid − 0.5|`, tie → lowest threshold.
  * NO at the captured NO ask plus the fee-engine fee.
  * Exchange result, as Wave 2A.
* **P2 — 2025 RB receptions, natural rung, Wave-1 archival basis.**
  * The Wave-2A history characterisation, reproduced: T-90m horizon, Wave-1 `RB_receptions` family rows, frozen
    natural rung and tie-break, `RECONSTRUCTED_NO_ASK`, fee engine, exchange `result`.
  * T-0 is reported as a secondary checkpoint.
  * Membership uses the Wave-1 player rows (players who appeared). This is outcome-adjacent; it is inherited from
    Wave 1 and declared.
* **P3 — 2026 every valid RB receptions rung, on the P1 ladders.** Every rung of the same checkpoint ladder that
  passes `W.valid`, each at its own captured quotes.
* **P4 — 2026 WR / TE receptions, natural rung (controls).**
  * Every receptions ladder in the checkpoint baseline file whose player's position is WR or TE.
  * Position comes from the nflverse 2026 roster file; position is not an outcome.
  * Same natural-rung rule, NO at the captured NO ask.
* **P5 — 2026 other player-prop natural rungs (controls).** Every other stream-stat ladder in the checkpoint
  baseline file (rushing yards, receiving yards, passing yards, attempts, completions, carries), by stat ×
  position.
* **Settlement of P3–P5.** Use the exchange `result` from the same discovery archive. A rung with no binary exchange
  result is `SETTLEMENT_UNAVAILABLE` and counted. No population is filtered on whether the player played.
* **Required negative controls** (subsets of P4/P5): WR receptions, TE receptions, RB rushing yards, RB receiving
  yards and WR receiving yards.
  * Each is shown raw.
  * Each is also shown **matched to P1's support**, fixed now: natural-rung YES ask in [0.30, 0.70], YES spread
    ≤ 0.03, ≥ 3 valid rungs, and checkpoint confirmation ≤ 90 min before kickoff.

## 3. Price representations (section 24 of the brief)

Every 2026 row preserves YES bid, YES ask, NO bid, NO ask, the YES midpoint, the NO midpoint, the ask sum and the
YES spread. The probability representations are:

* **A. YES ask.**
* **B. YES midpoint** = (YES bid + YES ask)/2.
* **C. Normalised midpoint** = YES mid / (YES mid + NO mid).
* **D. Repo canonical fair estimator.** None exists in this repository (searched `nfl_edge/` for fair, de-vig and
  no-vig functions). D is reported as "not available" and no new estimator is invented.
* **For 2025:** A and B only, from YES bid/ask. C needs a captured NO quote and is `NOT_AVAILABLE_2025`.
* **Calibration residual** = realized YES indicator − representation. Negative means YES settled below the price.

## 4. Pre-registered mechanism hypotheses

**Notation.** t is the natural threshold (YES iff receptions ≥ t). p is the representation (§3), ŷ the realized
YES indicator, and r = ŷ − p the residual. All intervals use the **game-clustered bootstrap**: seed 20261015,
4,000 draws, the Wave-2 constants. Player-clustered intervals are added for P1 headline statistics.

### M1 — Generic NO-side bias

* **Question:** are Kalshi player-prop NO contracts broadly underpriced?
* **Measured:** the mean natural-rung residual r (B) and the fee-adjusted NO ROI, for P1 and for every P4/P5
  stat × position cell, raw and matched.
* **Supports M1:** residuals similarly negative (and NO ROI similarly positive) across most families.
* **Against M1:** RB receptions materially more negative than the controls, with controls near 0.

### M2 — RB-receptions-specific calibration bias

* **Measured:** calibration of P1 (and P2) under A, B and C.
  * Calibration table by fixed YES-price bucket.
  * Brier score and log loss of each representation.
  * Logistic calibration intercept and slope of ŷ on logit(p), reported only if n ≥ 60 and both outcomes have
    ≥ 15 rows.
* **Formal test T2:** RB natural-rung mean residual (B) minus the pooled P4 + P5 natural-rung mean residual (B),
  with a game-clustered bootstrap over the union of games.
* **Supports M2:** RB residual materially negative and different from the controls.

### M3 — Natural-rung selection effect

* **Measured:** for each P1 ladder, the ordered thresholds, the natural rung, its distance from 0.5, the lower and
  upper neighbours, every rung's prices and every rung's settlement (P3).
* **Residual by rung offset** (−2, −1, 0, +1, +2 relative to natural) and by distance-from-0.5 bucket.
* **Formal test T3:** mean residual (B) at the natural rung minus at the non-natural valid rungs of the same
  ladders.
* **Supports M3:** miscalibration concentrated at offset 0.
* **Against M3:** similar residuals across the ladder.
* No alternative rung-selection rule is created.

### M4 — Discrete count / median effect

* **Measured:** for P1 and P2, the realized receptions relative to t, binned:
  * ≤ t−3, t−2, t−1, t, t+1, t+2, ≥ t+3;
  * P(X ≥ t), P(X = t−1), P(X = t), P(X ≤ t−1).
* **YES losses classified** as:
  * **near miss:** X = t−1;
  * **low-volume collapse:** 1 ≤ X ≤ t−2;
  * **zero:** X = 0;
  * **no snap / inactive:** settlement value not binary.
* **NO losses classified** as X = t, X = t+1 and X ≥ t+2.
* **Compared with the market-implied mass** in the same bins (M-27 below).
* **Supports M4:** realized mass at t−1 materially exceeds market-implied mass at t−1 while the market's S(t) sits
  near 0.5.

### M5 — Zero / low-reception tail

* **Measured:** the realized PMF of P1 (0, 1, 2, …) against:
  * **(i) Poisson** with the mean implied by each ladder;
  * **(ii) negative binomial** with the same mean. The dispersion is estimated **only from 2016–2025 RB
    player-games**, conditional on the frozen-model-free pregame baseline `b_ewma.receptions`. It is not
    estimated from the study sample.
  * **(iii) zero-inflation** characterisation (excess zeros versus NB), reported only if the 2016–2025 data
    show it;
  * **(iv) the market's own ladder-implied PMF.**
* **Formal test T5:** market-implied P(X ≤ t−2) minus the realized frequency, P1.
* **Supports M5:** the market under-states mass at 0 / low counts.
* The best-fitting distribution creates no rule.

### M6 — Role uncertainty

* **Pregame features** come from the frozen Wave-2 observe stage re-run at kickoff − 300 min:
  * snap share (short and long);
  * target share (short and long), and last-game target share;
  * recent receptions and targets;
  * injury designation;
  * the frozen `role_stability` class;
  * backfield concentration: the top RB's share of team RB carries + targets over the prior three games.
* **Route participation and routes per dropback:** 2026 participation data is not published by nflverse. These
  are declared `UNAVAILABLE`.
* **Splits, fixed now:**
  * `role_stability` class;
  * backfield concentration ≥ 0.60 (**concentrated**) versus < 0.60 (**committee**);
  * target-share volatility above or below the P1 median (**unstable / stable**), computed without outcomes.
* **Supports M6:** residual materially more negative in unstable / committee rows.

### M7 — Projection vs threshold

* **Model median** = frozen ridge prediction + `median_offset`, computed from the re-run pregame rows with the
  frozen parameters. Nothing is refit.
* **Measured:**
  * model_median − t versus p and versus ŷ;
  * model calibration: mean (actual − model median), and the share of actual ≥ model median;
  * the residual where model and market agree (|model_median − market_median| ≤ 0.5) versus where they
    disagree.
* **Model distribution.** The frozen artifact carries only global residual quantiles (q10, q25, q50 = offset, q75,
  q90). A model "band" for t is reported: the quantile interval that t − 0.5 falls in. No full model distribution
  is fabricated.

### M8 — Public / star-player effect

* **Proxies, fixed now:**
  * 2025 PPR fantasy rank among RBs (top 12 / 13–24 / other);
  * prior-season receptions per game (tercile within P1);
  * number of listed rungs;
  * natural-rung volume and open interest at the checkpoint (tercile);
  * prime-time game (Thursday, Sunday or Monday night).
* **Wording:** "consistent with" or "not consistent with". No claim about trader motivation is made.

### M9 — Market depth / quote quality

* **Measured:** residual and NO ROI by YES spread (1¢ / >1¢), ask sum (≤ 1.01 / > 1.01), number of valid rungs,
  checkpoint age (kickoff − confirmed_at), price staleness (kickoff − last price change), volume, open interest,
  top-of-book size, and |mid − 0.5|.
* **Supports M9:** the effect concentrates in wide, stale or thin markets, or disappears under B / C.

### M10 — Threshold-specific effect

* **Measured:** by natural threshold (1+, 2+, 3+, …): n, realized YES rate, mean A / B / C, residual, NO ROI.
  Shown for P1 and P2 separately.
* **Descriptive only.**

### M11 — Price-bucket effect

* **Buckets** of the NO ask: $0.20–0.29, 0.30–0.39, 0.40–0.49, 0.50–0.59, 0.60–0.69 and 0.70–0.79 (populated only).
* **Measured:** n, wins, win rate, mean ask, fee-inclusive break-even, residual and ROI.
* **Descriptive only.**

### M12 — Player concentration

* **Per player:** n, thresholds, NO asks, actual receptions, record, P/L, ROI and share of total P/L.
* **ROI after removing** the top 1 / 3 / 5 / 10 players by summed P/L (largest positive contributors first, ties by
  player id: the Wave-2A convention).
* **Leave-one-player-out distribution.**
* **Shares:** observation share and profit share, plus a Herfindahl index of observations and of |P/L|.
* **Formal test T12:** share of total P/L from the top 5 players.
* **Supports concentration:** removal of ≤ 5 players drives ROI to ≤ 0.

### M13 — Team / scheme concentration

* **Measured:** the same by team, by starting QB (the team's pass-attempt leader in that game, a role descriptor
  only) and by backfield (team-season).
* **QB mobility proxy:** the QB's prior-season scramble rate (top tercile of 2025 starters).
* **RB pass-game share proxy:** the team's prior-season share of targets to RBs (tercile).
* **Offensive coordinator / scheme:** no reliable timestamped source in the repository, so `UNAVAILABLE`.

### M14 — Recency bias

* **Pregame inputs:** last-game receptions, last-2 and last-3 averages, season-to-date and long-window
  averages, target share.
* **Measured:**
  * the regression of the market-implied mean (§M-27) on last-game receptions and the long-window average, in P1
    and P2;
  * the regression of actual receptions on the same inputs in 2016–2025 RB player-games (the "justified"
    response).
* **Formal test T14:** the market's last-game coefficient minus the historical outcome coefficient.
* **Supports M14:** the market loads materially more on last-game receptions than outcomes justify, and residuals
  are more negative after spike games (last game ≥ long average + 2).

### M15 — Mean vs median forecasting

* **For each P1 / P2 row with ≥ 6 prior games,** from the player's pregame history (last 16 regular-season games):
  * mean;
  * median;
  * mode;
  * the empirical P(X ≥ t).
* **Measured:** whether t sits closer to the mean, the median or the recent average, and whether the market's p
  sits above the history's P(X ≥ t).
* **Supports M15:** right-skewed histories with t ≈ mean > median, and p > P_hist(X ≥ t).

### M16 — Correlated game environment

* **Splits, fixed now:**
  * favourite / underdog (nflverse `spread_line`);
  * team implied total above / below the P1 median;
  * the frozen `ctx.expected_script` sign;
  * opponent prior-season RB receptions allowed per game (tercile).
* **Pace and pressure:** characterised by the frozen team features only if present.
* No interaction is mined.

### M17 — Settlement semantics

* **Audited:** `rules_primary` / `rules_secondary` wording, `strike_type`, `floor_strike`, and the ≥ semantics.
* **Push / non-binary settlement.** The contract text says an active player who never takes a snap settles at "the
  fair market price before game start". Every non-binary `settlement_value_dollars` is counted and listed.
* **Exchange vs nflverse.** Every 2026 receptions rung (P1, P3, P4) and every 2025 RB rung is compared with nflverse
  `stats_player_week` receptions. Mismatches are listed.
* **Positive controls, fail loudly:**
  * YES / NO complementarity;
  * monotone realized hit rate across thresholds of the same ladder;
  * ordered thresholds;
  * exchange = official stat.

### M18 — 2025 vs 2026 market structure

* P1 and P2 are reported in separate columns, never pooled.
* Only A, B, realized rates and thresholds are compared across seasons. C, ask sum and NO-side quotes exist
  only in 2026.

### Price movement (brief §25)

* **2026:** the frozen natural-rung ticker's quotes (last row at or before each instant) at the earliest captured
  row, T-24h, T-6h, T-3h, T-90m, T-60m and the frozen checkpoint.
* **2025:** the T-90m natural rung's ticker at T-48h, T-24h, T-12h, T-6h, T-3h, T-90m, T-30m and T-0.
* **Measured:** mean B and mean residual at each instant, and mean change between instants. The rung is fixed
  (the frozen natural rung). No entry checkpoint is chosen.

### Ladder shape (brief §26) and market-implied count distribution (brief §27, **M-27**)

* **Ladder shape:** for P3 ladders, B against threshold: monotonicity violations, adjacent-rung spacing, and the
  natural rung's position.
* **Implied PMF.** With S(k) = B at threshold k on integer-contiguous rungs:
  * P(X = k) = S(k) − S(k+1);
  * P(X < k_min) = 1 − S(k_min);
  * P(X ≥ k_max) = S(k_max).
* **Violations.** Negative masses (monotonicity violations) are reported, not repaired.
* **Market-implied mean** is computed only where the lowest rung is ≤ 1 or 2 and the top tail mass is ≤ 0.10:
  * Σ k·P(X = k) with the open tails at their boundary values;
  * labelled a lower bound when the top tail is open.
* **Aggregation.** By offset from t, aggregate the implied mass and the realized count in the bins of M4.
* **Formal test T27:** implied minus realized mass at t−1, and at ≤ t−2.

### Player-model distribution (brief §28)

Market-implied PMF versus the model band (M7) versus the outcome. The model gives quantiles only, and no model PMF
is fabricated.

### Case studies (brief §31)

* **Selection** happens after P1 is fixed: players ranked by summed NO P/L in P1.
* **Top 5** = highest; **bottom 5** = lowest. Ties go to more rows, then player id.
* **Each covers every P1 row of that player:**
  * matchup;
  * pregame role (M6 fields);
  * prior targets / receptions;
  * injury designation;
  * t;
  * YES / NO asks;
  * actual receptions;
  * price movement;
  * backfield teammates (other team RBs with ≥ 10 % of team RB opportunities in the prior three games);
  * a data-only miss description.

## 5. Formal tests and multiplicity

* **The family of formal tests is fixed at seven:** T2, T3, T5, T12, T14, T27(t−1) and T27(≤ t−2).
* **Each reports** an effect size, a 95 % game-clustered bootstrap interval and a two-sided bootstrap p-value
  (2 × the share of draws on the far side of 0).
* **Benjamini–Hochberg q-values** are reported across the seven. T12 is a share, not a null test, so it is reported
  without a p-value and excluded from the BH family, leaving six.
* **Everything else is descriptive.** No other table carries a p-value.

## 6. Interpretation criteria (qualitative, fixed now)

| Mechanism | Evidence that would support it |
|---|---|
| Generic NO bias | Negative residuals / positive NO ROI of similar size across most control families |
| RB-specific calibration | RB receptions residual materially below matched controls (T2) |
| Natural-rung selection | Residual concentrated at offset 0, not at neighbours (T3) |
| Discrete-count effect | Market-implied mass at t−1 below realized; the natural rung's S(t) ≈ 0.5 while realized P(X ≥ t) is lower; losses mostly near misses |
| Downside-tail underpricing | Implied P(X ≤ t−2) and P(X = 0) below realized; losses mostly collapses / zeros (T5, T27) |
| Role uncertainty | Residual more negative in unstable / committee / non-stable-role rows |
| Recency bias | Market loads on last-game receptions more than outcomes justify (T14); spike-game residuals more negative |
| Microstructure | The effect vanishes under B / C, or concentrates in wide / stale / thin quotes |
| Player concentration | The effect collapses after removing ≤ 5 players |
| Random noise | No coherent mechanism, unstable splits, wide intervals, concentrated P/L |

* **Allowed conclusions:** likely market calibration issue, likely role / distribution issue, likely microstructure
  artefact, likely player concentration, likely random noise, multiple mechanisms, or cannot distinguish yet.
* **The answer to "should NFL-PROP-PROS-001 change?" is NO** unless an implementation or integrity defect is found.

## 7. Integrity tests (in `tests/test_rb_receptions_mechanism.py`)

* The Wave-2 frozen files and pins are unchanged.
* No write path into a prospective ledger / market-data tree.
* The natural rung is imported from `W.ladder` (tie → lowest threshold).
* The 2026 NO price is the captured NO ask; the 2025 one is labelled `RECONSTRUCTED_NO_ASK`.
* Population membership is outcome-blind (outcomes doctored, membership unchanged).
* Quotes are strictly pre-kickoff.
* Pregame features use strictly earlier games.
* Settlement semantics: ≥ t, no push, non-binary detection.
* Thresholds are ordered.
* Player identity is stable across records.
* Controls are deterministic.
* Case-study selection runs on the fixed P1 only.
* A deterministic rerun reproduces the artifact hash.
