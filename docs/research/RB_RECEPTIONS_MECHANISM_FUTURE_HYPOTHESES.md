# Wave 2B (NFL): RB receptions mechanism — future hypotheses (observations only, NOT tested)

* **Nothing here is a rule.** None of these entries was tested, none changes `NFL-PROP-PROS-001`, and none is a
  Wave-2 candidate.
* **Source.** They came out of the explanatory mechanism study (`RB_RECEPTIONS_MECHANISM_RESULTS.md`; protocol
  `a5f18324`).
* **Contamination.** Every observation below comes from the 2025 (weeks 9–18) and 2026 (weeks 1–5) samples that
  Wave 1 used to discover the RB-receptions pattern. **All of them are contaminated.**
* **Required before any use:**
  * a new pre-registration, written and committed before any outcome of its test population exists;
  * a population disjoint from Wave 2's prospective PROP-001 sample, or explicitly nested in it as a secondary,
    non-decision metric.
* **Not a recommendation.** "Minimum sample" is the smallest prospective n at which a read would be worth
  pre-registering, not a promise that it would be decisive.

---

### B2B-F1 — Dispersion mismatch on RB receptions ladders

* **Observation.**
  * The market's RB receptions ladder is close to Poisson-shaped: a Poisson fitted to each ladder reproduces the
    natural-rung YES mid (0.529 vs 0.519 in 2026; 0.502 vs 0.499 in 2025).
  * Historical RB receptions (2016–2025) are over-dispersed: variance/mean 1.34–1.64 in every baseline decile.
  * A negative binomial with the ladder's own mean and the historical dispersion puts P(X ≥ t) about 3 pp below the
    market (0.491 vs 0.519 in 2026; 0.468 vs 0.499 in 2025).
  * The realized rate was lower still (0.434 / 0.407).
* **Possible mechanism.** The market prices a count with roughly the right mean but too little spread. For a
  right-skewed count, that over-states P(X ≥ t) for thresholds near the mean (the mean-vs-median effect) and
  under-states mass at t − 1.
* **Exact future test.**
  * For every prospective RB receptions ladder at the Wave-2 checkpoint, compute pregame, from frozen code:
    `gap = NB_P(X ≥ t | ladder-fitted mean, dispersion frozen from 2016–2025) − market YES mid` at the natural rung.
  * Pre-register the sign test: the mean realized residual (ŷ − mid) of rows with `gap ≤ −0.02` is below that of
    rows with `gap > −0.02`.
  * Secondary: the same on WR receptions, as a control.
* **Why the current evidence is contaminated.** The dispersion idea was formed after looking at the discovery-period
  residuals.
* **Minimum sample.** ≥ 300 RB natural rungs.

### B2B-F2 — High-volume / workhorse receiving backs

* **Observation.** The natural-rung residual was most negative in both seasons for:
  * the top tercile of prior-season receptions per game: −0.18 (2026, n 21) and −0.19 (2025, n 29);
  * concentrated backfields: −0.135 (n 41) and −0.124 (n 93);
  * the top tercile of long-window snap share: −0.19 and −0.15.

  Among the top P/L players were Warren, Barkley, McCaffrey, B. Robinson and Spears (2026), and Irving, Neal,
  Achane, Hall and Barkley (2025).
* **Possible mechanism.** Two candidates:
  * YES demand on prominent backs;
  * the dispersion mismatch growing with the mean.

  The data cannot separate them.
* **Exact future test.**
  * The prior-season receptions-per-game tercile is frozen from the prior season's nflverse file before week 1.
  * Pre-register the difference in mean natural-rung residual, top tercile minus the rest.
* **Why the current evidence is contaminated.** The split was chosen descriptively, on the discovery seasons.
* **Minimum sample.** ≥ 100 top-tercile rows and ≥ 200 other rows.

### B2B-F3 — Day games versus prime time

* **Observation.** The residual was negative in day games (−0.117 in 2026, n 65; −0.139 in 2025, n 101) and about 0
  in prime-time games (+0.03 / +0.03, n 18 / 39).
* **Possible mechanism.** Different flow or attention in stand-alone games. Unknown.
* **Exact future test.** Pre-register the kickoff slot (Thursday / Sunday-night / Monday = prime time) and the
  difference in mean natural-rung residual.
* **Why the current evidence is contaminated.** The split was found post hoc in the discovery seasons. The
  prime-time n is small.
* **Minimum sample.** ≥ 80 prime-time rows.

### B2B-F4 — The whole ladder centre, not only the natural rung

* **Observation.** Rungs one step below and one step above the natural rung were also YES-rich:
  * offset −1: −0.056 (2026) and −0.073 (2025);
  * offset +1: −0.068 and −0.039.

  The tails (|offset| ≥ 2) were near calibrated.
* **Possible mechanism.** A distribution-shape error, which peaks where the density is highest.
* **Exact future test.** Track the mean residual on offsets −1, 0, +1 jointly, as a descriptive Wave-2 side metric.
  No position is taken.
* **Why the current evidence is contaminated.** The same discovery seasons.
* **Minimum sample.** ≥ 300 ladders.

### B2B-F5 — Mild YES richness on rushing-type props outside RB receptions

* **Observation.** 2026 natural-rung residuals (all intervals include 0):
  * QB rushing yards −0.074 (n 81);
  * QB carries −0.053 (n 52);
  * RB rushing yards −0.048 (n 214);
  * RB receiving yards −0.043 (n 70).

  QB completions (+0.068) and passing yards (+0.035) went the other way.
* **Possible mechanism.** The same shape mismatch on skewed low-count or low-yardage stats. Alternatively, noise.
* **Exact future test.** Pre-register a family-level calibration panel (residual by stat × position at the natural
  rung) as a monitoring table. No rule.
* **Why the current evidence is contaminated.** These were found while reading the controls of a contaminated sample.
* **Minimum sample.** ≥ 300 per family.

### B2B-F6 — Formation of the shortfall between listing and T-24h

* **Observation.**
  * In 2025 the natural-rung residual was ≈ 0 at T-48h (n 44) and about −0.085 from T-24h through T-0.
  * In 2026 the mid rose +3.3 pp from the first listing quote (wide, about 63 h out) to the checkpoint, and was
    flat from T-24h to kickoff.
* **Possible mechanism.** The first liquid quotes set the YES-rich level. Later flow does not correct it.
* **Exact future test.** Pre-register the residual at the first valid (≤ 10¢-wide) quote versus at the checkpoint,
  on the same rungs. Descriptive.
* **Why the current evidence is contaminated.** The T-48h n is small, and the period is the discovery one.
* **Minimum sample.** ≥ 200 rungs with a valid early quote.

### B2B-F7 — Frozen model below the market

* **Observation.** The frozen 2026 projection sat 0.73 receptions below the market median.
  * Where it was lower (n 58), the residual was −0.156; where they agreed (n 25), it was +0.079.
  * In 2025 (Wave-1 out-of-sample ridge) the residual was −0.10 whether or not they agreed.
* **Possible mechanism.** The model encodes the median better than the market. Inconsistent across seasons.
* **Exact future test.** Already partly measurable inside Wave 2 (the frozen projection exists for every PROP-001
  row). Pre-register `model_median − market_median < −0.5` versus not, as a secondary characterisation only.
* **Why the current evidence is contaminated.** The 2026 split is in a discovery period, and the 2025 split
  disagrees.
* **Minimum sample.** ≥ 150 rows in each arm.
