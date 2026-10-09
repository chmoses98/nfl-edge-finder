# Football Signal Discovery Lab — Wave 2B (NFL): RB receptions market-mechanism study — RESULTS

**Kind: EXPLANATORY, RETROSPECTIVE, DISCOVERY-CONTAMINATED.**

* This study creates no rule, filter, price cap, badge, recommendation or stake.
* `NFL-PROP-PROS-001` is unchanged and keeps tracking prospectively.
* Every number below comes from the 2025 and 2026 samples that Wave 1 used to discover the pattern.

| Item | Value |
|---|---|
| Protocol | `docs/research/RB_RECEPTIONS_MECHANISM_PROTOCOL.md`, committed first at **`a5f18324`** (2026-10-09T18:37:59Z), SHA-256 `aa7f6bb4…41f8` |
| Artifact | `research/rb_receptions_mechanism/mechanism_report.json`, schema `nfl_rb_receptions_mechanism/1.0.0`, SHA-256 `7fe2d858…ac7d1`; a rerun reproduces it byte for byte |
| Code | `nfl_edge/signal_discovery/rb_mechanism.py`, `scripts/research/rb_receptions_mechanism.py` (`extract-quotes` → `build`), `scripts/research/rb_receptions_mechanism_analyze.py`, `tests/test_rb_receptions_mechanism.py` |
| Market data | `market-data@4f04927982a1` (the Wave-2A pin): discovery run `20261008T163830Z`, 2025 horizon archive, capture quote history |
| Statistics | Game-clustered bootstrap, seed 20261015, 4,000 draws (player-clustered where stated) |

* **Notation.**
  * **Residual** = realized YES − price; negative means YES settled below its price.
  * **B** = YES midpoint.
  * **ROI** is fee-adjusted on outlay.

## A. Verdict

* **What made NO look profitable.** RB-receptions YES contracts near the middle of the ladder settled about 8–9
  points below their mid-prices in both seasons. NO on the natural rung looked profitable because of that.
* **Most likely explanation: a modest, same-sign distribution-shape mispricing, plus a lot of noise.**
  * **The shape.** The market's RB receptions ladder is close to Poisson-shaped. Real RB receptions are
    over-dispersed (variance ≈ 1.4–1.6 × the mean). So the market puts too much probability on the threshold and the
    rung above it, and too little on "one short".
    * Where the ladder allows the mean to be computed, the market-implied mean matched the realized mean
      (3.06 vs 3.06).
    * But realized mass at t − 1 was 27.6 % against an implied 21.2 %, and at t it was 10.3 % against 19.6 %.
  * **How much it explains.** A negative binomial with the ladder's own mean accounts for roughly **3 of the 8–9
    points**. The rest is not separable from noise at n = 83 / 140.
* **Ruled out:**
  * a generic NO bias (pooled controls −0.013);
  * bid/ask structure (1¢ markets; the midpoint gives the same result);
  * settlement artefacts (0 mismatches in 1,552 rungs);
  * recency over-reaction (the market weights the last game *less* than outcomes justify);
  * role instability (the effect is larger for *stable*, workhorse backs).
* **Not established.** None of the six formal tests survives FDR (all q = 0.43). It stays a plausible mechanism, not a
  proven edge.

## B. Repo / branch / PR / SHAs

* **Repository:** `chmoses98/nfl-edge-finder`.
* **Branch:** `claude/rb-receptions-mechanism-y8lhv7`. This is the session's designated branch, used instead of the
  suggested `research/rb-receptions-mechanism`.
* **Base:** `ad32b19` (main, after Wave 2A).
* **Commits, in order:**
  1. **`a5f18324`** — protocol only. Before any result.
  2. `ec46d00` — study code and tests. No results.
  3. `8ae41a9` — build artifacts.
  4. Later commits — fixes, results, docs.

## C. Research integrity

* **Wave 2 untouched.** `git diff ad32b19` shows no change under:
  * `nfl_edge/signal_discovery/wave2*.py`, `scripts/research/signal_lab_wave2*.py`;
  * `research/signal_discovery_wave2*/`, the Wave-2 docs and the workflows.

  Eleven frozen files are SHA-pinned in the tests, and `W.load_frozen` still validates every pin.
* **Isolation.**
  * Nothing is written to market-data or to the prospective store (guarded and tested).
  * No Wave-2 prospective outcome exists or was read.
* **Membership is outcome-blind.**
  * P1 is the frozen Wave-2A set. It was rebuilt independently, and all 83 natural rungs, NO asks, fees and
    settlements match the frozen records exactly.
  * The controls are decided by the frozen `W.ladder` on checkpoint quotes alone.
* **Pregame features.**
  * The frozen observe-stage builder was re-run at kickoff − 300 min, with the timestamped injury vintage.
  * It reproduced all 110 frozen observation rows of the P1 games exactly: role class, b_season, sh_target_l.
  * The 8 other frozen rows are in games with no P1 row, and were not rebuilt.
  * Roster: `ROSTER_NEAR_PIT`, as declared in Wave 2A.
* **Pricing labels.**
  * 2026 uses the captured NO ask: `CAPTURED_NO_ASK`.
  * 2025 NO = 1 − YES bid: `RECONSTRUCTED_NO_ASK`, on every row.

## D. Data populations

| Pop | Definition | n (binary-settled) |
|---|---|---|
| P1 | 2026 RB receptions natural rung, captured both-side quotes (Wave-2A frozen set) | **83** (44 games, 38 players) |
| P2 | 2025 RB receptions natural rung, Wave-1 basis, T-90m. T-0 is secondary. | **140** (84 games, 35 players); T-0: 160 |
| P3 | 2026 every valid rung of the P1 ladders | **525** |
| P4 | 2026 WR / TE receptions natural rung | 482 (471 binary; 3 non-binary, 8 unavailable) |
| P5 | 2026 other player-prop natural rungs (6 stats × positions) | 1,394 (1,362 binary; 8 non-binary, 24 unavailable) |

## E. Natural-rung reproduction

* **The rule:** valid `0 < bid ≤ ask < 1` with width ≤ 0.10; minimum |mid − 0.5|; ties go to the lowest threshold.
* It is imported as `W.ladder`, never restated.
* **83 / 83 P1 rungs match** the frozen entry, on ticker, mid and market median.
* Tie-break test: an exact tie picks the lowest threshold.
* **Note for future test writers.** Near-ties such as 0.55 vs 0.45 are not exact in floating point
  (0.0500000000000004 vs 0.0499999999999999). The frozen rule then picks the strictly closer one. That is the frozen
  behaviour, unchanged.

## F. 2025 result (characterisation; `RECONSTRUCTED_NO_ASK`)

| | NO ROI | YES ROI | Residual B | Record |
|---|---|---|---|---|
| P2 T-90m | **+8.5 %** [−6.1, +22.8] | −25.1 % | **−0.092** [−0.171, −0.010] | 83–57 |
| P2 T-0 | +7.2 % | −23.6 % | −0.084 [−0.157, −0.011] | 93–67 |
| Every valid rung, same ladders | +3.1 % | −24.9 % | −0.065 | 381–193 |

These reproduce Wave 2A exactly.

## G. 2026 result (actual both-side prices)

* **P1:**
  * NO ROI **+11.7 %** [−9.4, +33.2]; with player-clustering [−10.8, +35.7].
  * YES ROI **−20.3 %** [−40.0, −0.6].
  * Record 47–36.
  * Mean YES ask 0.524, mean B 0.519, realized YES 43.4 %.
  * Residual B **−0.085** [−0.194, +0.022].
* **P3, every valid rung:** NO +0.4 %, residual −0.026.

## H. Generic NO-bias test (M1)

**Not a generic NO effect.**

* **Pooled P4 + P5 natural rungs** (n 1,833): residual **−0.013** [−0.042, +0.017], NO ROI −2.6 %.
* **WR receptions:** −0.007, NO −3.6 %.
* **WR receiving yards:** +0.010, NO −6.9 %.
* **QB completions and passing yards** go the other way: +0.068 and +0.035 (YES cheap).

## I. RB-specificity test (M2)

**Direction RB-specific, magnitude not established.**

* **T2** (RB minus pooled controls): **−0.072** [−0.188, +0.041], p 0.22, BH q 0.43.
* **Matched controls** (YES ask 0.30–0.70, spread ≤ 3¢, ≥ 3 rungs, ≤ 90 min): −0.071, p 0.23.
* **Other cells** are mildly YES-rich, with every interval including 0:
  * QB rushing yards −0.074;
  * QB carries −0.053;
  * RB rushing yards −0.048;
  * RB receiving yards −0.043;
  * TE receptions −0.036.

  RB receptions is the most negative of the large cells.

## J. YES calibration (P1; asks include the spread)

| YES ask | n | Mean ask | Mean B | Realized YES | Residual B |
|---|---|---|---|---|---|
| 0.30–0.39 | 2 | 0.390 | 0.385 | 0.50 | +0.115 |
| 0.40–0.49 | 22 | 0.446 | 0.441 | 0.545 | +0.105 |
| 0.50–0.59 | 45 | 0.542 | 0.536 | **0.289** | **−0.247** |
| 0.60–0.69 | 14 | 0.611 | 0.605 | 0.714 | +0.109 |

* **Scores:**
  * Brier: A 0.257, B 0.256, against the base rate 0.246.
  * Log loss: B 0.705.
* **Logistic calibration** on logit(B):
  * 2026: slope 0.14 (SE 0.85), intercept −0.28 (SE 0.23). Uninformative at n 83.
  * 2025: slope **1.03** (SE 0.54), intercept −0.38 (SE 0.17).
  * That is a near-uniform **level shift of about −0.38 logits**, not a slope problem.
* **Where the shortfall sits.** In 2026 it all came from the 0.50–0.59 bucket. In 2025 it came from 0.40–0.49 and
  0.60–0.69 instead. The bucket pattern is unstable, which reads as noise around a level shift.

## K. NO calibration (P1)

* **Realized NO 56.6 %** against:
  * mean NO ask 0.487: residual +0.079 [−0.028, +0.188];
  * NO mid 0.481: +0.085.
* **By NO-ask bucket:** $0.40s 27/43 (62.8 %, break-even 46.4 %); $0.50s 16/32 (50.0 %, break-even 55.7 %).

## L. Bid/ask / microstructure (M9)

**The shortfall survives every reasonable price representation. Not a thin-market artefact.**

* **2026 quotes are tight and fresh:**
  * 72 of 83 at a 1¢ YES spread, with ask sum $1.01;
  * every checkpoint confirmed within 20 min of kickoff;
  * the quote-history row equals the checkpoint quote 83 / 83.
* **Residual by representation:** A −0.091, B −0.085, C −0.085. C equals B because NO bid = 1 − YES ask on Kalshi.
  The repo has no canonical fair estimator.
* **In 1¢ markets alone:** residual −0.055, NO +5.8 %.
* **In the 11 wider markets:** −0.282.
* **Volume / OI terciles:** flat, at −0.08 / −0.09 / −0.08.
* **2025 candles** are wider (127 of 140 > 1¢). The shortfall is −0.092 at the mid.

## M. Ladder shape (M3, §26)

* **Ladders are clean.** All 83 P1 and 140 P2 ladders are monotone, with integer spacing 1. Across 614 2026
  receptions ladders there was 1 violation.
* **Residual by rung offset:**

  | Offset | 2026 (P3) | 2025 |
  |---|---|---|
  | −2 | −0.011 | −0.128 |
  | −1 | −0.056 | −0.073 |
  | **0 (natural)** | **−0.085** | **−0.092** |
  | +1 | −0.068 | −0.039 |
  | +2 | +0.016 | −0.052 |
  | ≥ +3 | ≈ 0 | ≈ −0.04 |

* **By distance of the mid from 0.5:**
  * < 0.05: −0.151;
  * 0.05–0.15: −0.093;
  * 0.15–0.30: −0.053;
  * ≥ 0.30: +0.020.
* **T3** (natural minus other rungs): −0.070 [−0.152, +0.016], p 0.11, q 0.43.
* **Reading.** The shortfall is a **centre-of-ladder** phenomenon. It is biggest where the probability density is
  biggest, which is what a location or shape error produces. It is not a separate selection effect of the natural
  rung, though the rule does sample the place where the error is largest in probability units.

## N. Market-implied reception distribution (§27)

* **Construction.** S(k) = B on integer rungs, and P(X = k) = S(k) − S(k + 1). Masses are aggregated around the
  natural t. 58 of the 83 P1 ladders cover t − 1 … t + 2; no negative masses.

| Bin | 2026 implied | 2026 realized | Implied − realized [95 %] | 2025 implied | 2025 realized |
|---|---|---|---|---|---|
| ≤ t − 2 | 0.291 | 0.345 | −0.054 [−0.168, +0.058] | 0.292 | 0.380 |
| **t − 1** | 0.212 | **0.276** | −0.064 [−0.190, +0.056] | 0.227 | 0.250 |
| **t** | **0.196** | 0.103 | **+0.093** [−0.004, +0.162] | 0.195 | 0.130 |
| t + 1 | 0.135 | 0.086 | +0.049 | 0.137 | 0.120 |
| ≥ t + 2 | 0.167 | 0.190 | −0.023 | 0.150 | 0.120 |

* **The implied mean is right on average.** Market-implied mean (lower-bound convention) 3.06 vs realized 3.06, on
  52 ladders.
* **What is mispriced is the shape.** The market puts too much mass *exactly at* t and t + 1, and too little at
  t − 1 and below. Realized outcomes are more spread out.
* **2025 agrees** on t (+0.064) and on the lower bins.
* **Not covered:** implied P(X = 0) needs a 1+ rung. Only 2–3 ladders have one.

## O. Realized reception distribution (P1 / P2)

| Relative to t | ≤ t − 3 | t − 2 | **t − 1** | t | t + 1 | t + 2 | ≥ t + 3 |
|---|---|---|---|---|---|---|---|
| 2026 (n 83) | 8.4 % | 21.7 % | **26.5 %** | 19.3 % | 6.0 % | 7.2 % | 10.8 % |
| 2025 (n 140) | 17.1 % | 12.9 % | **29.3 %** | 15.0 % | 16.4 % | 3.6 % | 5.7 % |

* **2026:** P(X ≥ t) 0.434, P(X = t − 1) 0.265, P(X = t) 0.193, P(X ≤ t − 1) 0.566.
* **2025:** 0.407, 0.293, 0.150, 0.593.
* **Mean actual vs mean threshold:** 2.70 vs 3.04 (2026); 2.59 vs 3.22 (2025).

## P. Discrete-count effect (M4)

**Partially.**

* **YES losses** (= NO wins) are mostly **near misses**:

  | | Near miss (X = t − 1) | Low volume | Zero |
  |---|---|---|---|
  | 2026 (47 losses) | **22** | 16 | 9 |
  | 2025 (83 losses) | **41** | 25 | 17 |

* **NO losses, 2026:** 16 at exactly t, 5 at t + 1, 15 at t + 2 or more.
* **The comparison that matters.** At the natural rung:
  * Poisson fitted to each ladder: P(X ≥ t) 0.529 (2026) / 0.502 (2025);
  * market mid: 0.519 / 0.499;
  * negative binomial, same mean, 2016–2025 dispersion: **0.491 / 0.468**;
  * realized: **0.434 / 0.407**.
* **Reading.** Integer thresholds plus over-dispersion explain about 3 of the 8–9 points. Lines (t − 0.5) sat closer
  to the history mean than to the median, and 62–67 % of histories were right-skewed (§S, M15).

## Q. Zero / low-reception tail (M5)

**Not specifically.** The market's lower tail matches the dispersion, not a zero cliff.

* **Historical dispersion (2016–2025 RB rows).** Variance/mean was 1.34–1.64 in every baseline decile. The excess
  zeros are fully explained by the negative binomial (P0 matches NB within ±0.02), so no zero-inflation is needed.
* **P1 P(X = 0):**
  * realized 0.108;
  * NB at the ladder mean 0.126;
  * Poisson 0.084.
* **P(X ≤ t − 2):**
  * realized 0.301;
  * NB 0.287;
  * Poisson 0.228;
  * market-implied 0.291 (on the covered ladders).
* **Reading.** The excess shortfall lives at t − 1 (near misses) more than at 0.

## R. Role-stability analysis (M6)

**Role instability is not the explanation. The direction is the opposite.**

| Split | 2026 residual (n) | 2025 residual (n) |
|---|---|---|
| Concentrated backfield (top share ≥ 0.60) | **−0.135** (41) | **−0.124** (93) |
| Committee | −0.035 (42) | −0.027 (47) |
| Snap share (long), top tercile | −0.186 | −0.148 |
| STABLE_ROLE class | −0.068 (77) | −0.085 (130) |
| Target-share volatility: unstable / stable | −0.104 / −0.066 | −0.070 / −0.113 (inconsistent) |

* Injury-designated and ROLE_CHANGE rows: n ≤ 6.
* **Route participation: UNAVAILABLE.** nflverse publishes no 2026 participation file.

## S. Recency analysis (M14) and mean vs median (M15)

* **Recency: no evidence of over-reaction.**
  * The market median's relative weight on last-game receptions (against the 16-game average) was **0.13** (2026)
    and 0.12 (2025).
  * Outcomes in 2016–2025 justify **0.17** (n 6,945).
  * T14 −0.039 [−0.166, +0.100], p 0.43.
  * After spike games (last ≥ long + 2): 2026 −0.042 (n 21); 2025 −0.271 (n 18). Inconsistent.
* **Mean vs median.**
  * Lines sat nearest the 16-game mean in 33 of 81 rows, nearest the median in 24, and nearest the last-3 average
    in 24 (2026). 2025: 65 / 33 / 42.
  * Histories were right-skewed (mean > median) in 62 % / 67 % of rows.
  * Market mid minus historical P(X ≥ t): +0.029 [−0.008, +0.064] in 2026; **+0.019 [+0.003, +0.037]** in 2025.

## T. Price-bucket analysis (descriptive only)

| NO ask | 2026 n | Win rate | Break-even | ROI | 2025 n | ROI |
|---|---|---|---|---|---|---|
| 0.30s | 3 | 33 % | 39.7 % | −16 % | 4 | +92 % |
| 0.40s | 43 | **62.8 %** | 46.4 % | **+35.4 %** | 53 | +12.4 % |
| 0.50s | 32 | 50.0 % | 55.7 % | −10.2 % | 49 | −9.9 % |
| 0.60s | 5 | 60 % | 62.8 % | −4.5 % | 32 | +25.2 % |

The 2025 asks are reconstructed. The pattern is not stable, and no bucket is promoted.

## U. Threshold analysis (descriptive only)

| t | 2026 n | Residual | NO ROI | 2025 n | Residual | NO ROI |
|---|---|---|---|---|---|---|
| 2+ | 24 | +0.013 | −8.5 % | 37 | −0.094 | +10.7 % |
| 3+ | 35 | −0.124 | +18.5 % | 64 | −0.092 | +8.2 % |
| 4+ | 13 | −0.100 | +13.8 % | 19 | −0.054 | +1.9 % |
| 5+ | 9 | −0.277 | +48.0 % | 11 | −0.131 | +16.1 % |
| 6+ | — | — | — | 9 | −0.108 | +9.9 % |

* 2025 is negative at every threshold.
* The 2026 2+ cell is the only exception. That fits noise around a broad shift better than a threshold-specific
  cause.

## V. Player concentration (M12)

* **Without the top players by summed P/L:**

  | | 2026 NO ROI | 2025 NO ROI |
  |---|---|---|
  | All rows | +11.7 % | +8.5 % |
  | Without top 1 | +8.1 % | +6.0 % |
  | Without top 3 | +0.6 % | +3.0 % |
  | Without top 5 | **−7.1 %** | **−0.0 %** |
  | Without top 10 | −22.5 % | −7.9 % |

* **Leave-one-player-out:** every value positive. 2026 +8.1 % to +15.4 %; 2025 +6.0 % to +12.1 %.
* **Shares of total P/L:**
  * the top 5 players are 18 % of rows and **150 % of P/L** (2026); 17 % and 100 % (2025);
  * Herfindahl of observations 0.030 / 0.035.
* **Post-hoc null (labelled, not pre-registered).** Removing the top-P/L players is outcome-selected. To see what it
  does to a *homogeneous* effect, outcomes were simulated with every row's YES probability = B − 0.085 (the observed
  shift), and the same top-5 removal applied:
  * the median "without top 5" ROI is −3.7 % (90 % band −22.5 % to +15.7 %) in 2026;
  * and −2.9 % (−15.6 % to +10.2 %) in 2025;
  * the observed −7.1 % and 0.0 % sit inside those bands.
* **Answer: unresolved at this sample size.** The result *is* heavily P/L-concentrated. But that concentration is what
  a broad, uniform 8-point shift would also produce at n = 83, so "collapses without the top 5" does not by itself
  show it is a few player-specific mispricings.
* **Who the top contributors were.** Mostly prominent workhorse backs on near misses:
  * 2026: Warren, Barkley, McCaffrey, B. Robinson, Spears;
  * 2025: Irving, Neal, Achane, Hall, Barkley.

## W. Team / scheme concentration (M13)

* **2026:**
  * the top 5 teams are 167 % of P/L;
  * without the top 5 teams: −9.5 %;
  * leave-one-team-out: +7.0 % … +15.4 %.
* **2025:** the top 5 teams are 109 % of P/L; without them, −0.9 %.
* **Team prior-season RB target share:** the top tercile was most negative in 2026 (−0.196), the bottom tercile in
  2025 (−0.127). Inconsistent.
* **QB mobility** (top tercile of prior-season scramble rate): no difference (−0.137 vs −0.109; 2025 −0.059 vs
  −0.042).
* **Offensive coordinator / scheme: UNAVAILABLE** (no reliable timestamped source).

## X. Market-timing analysis

* **2026, the same frozen natural rung:**

  | Instant | n | Mean mid | Spread | Residual |
  |---|---|---|---|---|
  | First listing quote (about 63 h out) | 83 | 0.485 | 0.28 | −0.052 |
  | T-24h | 78 | 0.521 | 0.018 | −0.072 |
  | T-6h | 80 | 0.519 | — | −0.069 |
  | T-3h | 80 | 0.520 | — | −0.070 |
  | T-90m | 80 | 0.521 | — | −0.071 |
  | T-60m | 80 | 0.522 | — | −0.072 |
  | Checkpoint | 83 | 0.519 | 0.011 | −0.085 |

  * The mid changed by −0.001 from T-24h to the checkpoint.
  * From the first quote to the checkpoint it changed by +0.033 [+0.017, +0.054]: up in 65 % of rows.
* **2025** (T-90m rung; YES candles):

  | Instant | n | Residual |
  |---|---|---|
  | T-48h | 44 | −0.007 |
  | T-24h | 107 | −0.085 |
  | T-6h | 123 | −0.088 |
  | T-3h | 135 | −0.085 |
  | T-90m | 140 | −0.092 |
  | T-30m | 135 | −0.107 |
  | T-0 | 136 | −0.094 |

* **Reading.**
  * YES did *not* get progressively more expensive into kickoff, and the market did not correct toward the result.
  * The shortfall was already present a day out.
  * Where it formed, it formed between listing and T-24h, when the first liquid quotes set YES slightly richer.

## Y. Model vs market (M7)

* **2026 frozen projection.** The RB ridge plus median offset, rebuilt pregame and never refit.
  * Model median − threshold −0.65.
  * Model median − market median **−0.73**.
  * Actual − model median +0.32.
  * Share of actual ≥ model median 0.434.
* **Does the model also think YES is too expensive?** Yes: in 54 of 83 rows the model median is below t − 0.5.
* **Where model and market disagree vs agree:**
  * model lower (n 58): residual −0.156, NO +25.6 %;
  * agree within 0.5 (n 25): +0.079, NO −20.8 %.
* **Model band.** t − 0.5 fell in the model's q50–q75 band in 53 rows (residual −0.094), and in q25–q50 in 28 rows
  (−0.073). No model PMF was fabricated.
* **2025** (Wave-1 out-of-sample ridge mean): the residual was **−0.10 both where model and market agree (n 72) and
  where the model is lower (n 62)**. The anomaly exists even where they agree, so the 2026 split does not replicate.

## Z. Negative controls (2026 natural rung; raw / matched)

| Cell | n | Residual B | NO ROI |
|---|---|---|---|
| **RB receptions (P1)** | 83 | **−0.085** | **+11.7 %** |
| WR receptions | 321 / 319 | −0.007 / −0.011 | −3.6 % / −3.0 % |
| TE receptions | 150 / 150 | −0.036 / −0.036 | +1.9 % / +1.9 % |
| RB rushing yards | 214 / 213 | −0.048 / −0.045 | +4.1 % / +3.7 % |
| RB receiving yards | 70 / 68 | −0.043 / −0.045 | +3.1 % / +3.7 % |
| WR receiving yards | 331 / 330 | +0.010 / +0.008 | −6.9 % / −6.6 % |
| Pooled P4 + P5 | 1,833 / 1,769 | −0.013 / −0.014 | −2.6 % / −2.3 % |

* **Positive / mechanical controls all pass:**
  * thresholds ordered;
  * 0 realized-monotonicity failures across 614 ladders;
  * P3 YES rate falls with the threshold (2+ 66 %, 3+ 42 %, 4+ 29 %, 5+ 19 %, 6+ 13 %);
  * 0 YES / NO complement failures;
  * exchange = nflverse on 978 (2026) + 574 (2025) rungs.
* **Post-hoc observation.** RB receptions ladders *outside* the frozen family (low-share or short-history backs,
  n 46) had a residual of **+0.049**. The shortfall belongs to established receiving backs, not to RB receptions in
  general.

## AA. Player case studies (selected after P1 was fixed, by summed P/L)

**Top 5 profit contributors (NO won):**

* **Jaylen Warren, PIT** (3–0; t 3, 4, 4; actual 2, 3, 3).
  * Three near misses.
  * Backfield leader at a 0.55–0.67 share.
  * Mid rose from 0.495 at listing to 0.605 before wk 2, after a 5-reception game.
* **Saquon Barkley, PHI** (3–0; t 2, 2, 3; actual 1, 1, 1).
  * Workhorse: snap share 0.69–0.77.
  * Target share is only about 11 %; the model median was 0.73–1.83, below t.
* **Christian McCaffrey, SF** (3–0; t 5 each; actual 4, 4, 3).
  * Long-run average 5.0–5.4 receptions, so the line sat at the mean; two near misses.
* **Bijan Robinson, ATL** (3–0; t 5 each; actual 3, 2, 1).
  * Line at t 5 after an 8-reception game; 16-game average 4.6–4.9.
  * Model median 4.1–4.6, below t.
* **Tyjae Spears, TEN** (3–0; t 3 each; actual 2, 0, 1).
  * Not the backfield leader (share 0.28–0.37).
  * Questionable or INJURY_DEPENDENT in two of the three rows.

**Top 5 loss contributors (NO lost):**

* **D'Andre Swift, CHI** (0–3; t 2; actual 5, 2, 2). Two rows landed exactly at t.
* **RJ Harvey, DEN** (0–2; t 3, 4; actual 6, 10). Upper-tail games.
* **Raheim Sanders, CLE** (0–2; t 1, 2; actual 4, 2). A low-share back.
* **Travis Etienne Jr., NO** (0–2; t 2, 2; actual 2, 2). Exactly at t.
* **Kenny Gainwell, TB** (0–2; t 2, 2; actual 2, 2). Exactly at t.

**Reading (data only).** The wins are near misses by high-mean backs. The losses are mostly 2+ lines landing exactly
on the threshold. That is the discrete-mass story at the line in both directions.

## AB. Mechanism scorecard

| Mechanism | Evidence for | Evidence against | Confidence | Conclusion |
|---|---|---|---|---|
| Generic NO bias | — | Pooled controls −0.013; WR receptions −0.007; QB passing YES-cheap | High | **Rejected** |
| RB-specific calibration | −0.085 (2026) / −0.092 (2025) at the mid; controls ≈ 0; not seen outside the frozen family | T2 −0.072, p 0.22, q 0.43; other rushing props mildly negative | Low–moderate | Direction consistent; not established |
| Natural-rung selection | Natural rung most negative | Offsets ±1 also negative; scales with density; T3 p 0.11 | Moderate | **Not a separate cause**: amplifies a ladder-centre error |
| Discrete-count effect | Implied mass at t +0.093 too high, at t − 1 −0.064 too low; NB gives −3 pp; about half of losses are near misses | Intervals include 0 | Moderate | **Partial explanation (≈ ⅓)** |
| Downside-tail underpricing | Implied ≤ t − 2 below realized | Zeros ≈ NB (0.108 vs 0.126); market tail ≈ NB | Low | Not specifically a zero / collapse tail |
| Role uncertainty | — | Larger in stable / concentrated / high-snap backs, both seasons | Moderate | **Rejected** (opposite direction) |
| Recency bias | 2025 spike rows −0.27 (n 18) | Market weight on last game 0.12–0.13 < 0.17 justified; T14 p 0.43; 2026 spike rows −0.04 | Moderate | **Rejected** |
| Microstructure | 11 wide rows −0.28 | 1¢ / $1.01 / ≤ 20 min quotes; A ≈ B ≈ C; volume / OI flat; price stable from T-24h | High | **Rejected** |
| Player concentration | Top 5 = 150 % / 100 % of P/L; without top 5: −7.1 % / 0 % | Leave-one-out all positive; the post-hoc homogeneous-shift null produces the same drop | Low | Concentrated P/L, not shown to be player-specific |
| Random noise | Every interval of the 2026 natural-rung residual includes 0; no test survives FDR; bucket / threshold patterns flip between seasons | Same sign in two seasons; coherent ladder-centre and shape pattern | — | **Large share of the magnitude is plausibly noise** |

## AC. Most likely explanation

* **What happened.** In both contaminated seasons the market priced RB receptions ladders with about the right mean
  but too little spread. It put too much probability on "exactly t" and "t + 1", and too little on "one short".
* **Why that matters for YES.** For established receiving backs whose line sits near their (right-skewed) mean, the
  natural-rung YES priced around 50 % really cleared closer to 46–47 %. That is the over-dispersion /
  integer-threshold effect.
* **What the realized record adds.** It cleared at 41–43 %. The extra 4–5 points are not distinguishable from noise
  and are carried by a handful of high-volume backs.

## AD. Does the effect have a plausible reason to persist?

* **A plausible reason exists.**
  * Count-shape errors are structural: a market making a near-Poisson ladder for an over-dispersed count would keep
    doing so.
  * The YES side on popular workhorse backs may draw steady demand. The data are only *consistent with* that, and
    cannot show trader motive.
* **But plausibility is not proof.**
  * The structural part (≈ 3 points) is about the same size as the cost of buying NO near 50¢. Break-even sits about
    2.5 points above the mid-implied NO probability: half a 1¢ spread plus the 2¢ fee. So it leaves little or no
    margin.
  * The rest of the historical ROI is not established.
* Only the frozen prospective Wave-2 stream can say whether anything persists.

## AE. Future hypotheses (listed only; not tested)

These are in `docs/research/RB_RECEPTIONS_MECHANISM_FUTURE_HYPOTHESES.md`:

* **B2B-F1** NB-vs-ladder dispersion gap.
* **B2B-F2** High-volume / workhorse receiving backs.
* **B2B-F3** Day vs prime time.
* **B2B-F4** The whole ladder centre (offsets −1, 0, +1).
* **B2B-F5** Rushing-type props mildly YES-rich.
* **B2B-F6** Formation between listing and T-24h.
* **B2B-F7** Frozen model below the market.

## AF. Tests / CI

* **`tests/test_rb_receptions_mechanism.py`:** 36 pass locally, covering:
  * Wave-2 file pins and frozen pins;
  * the protocol hash;
  * no prospective writes;
  * the `W.ladder` import and tie-break;
  * outcome-blind membership;
  * settlement semantics and non-binary detection;
  * the captured 2026 NO ask and the labelled 2025 one;
  * pre-kickoff quotes;
  * no future role data;
  * ordered thresholds and stable identity;
  * deterministic controls;
  * case-study selection;
  * a deterministic rerun.
* **Full suite, locally:** 3,067 passed, 4 skipped, 1 failed.
* **The 1 failure is pre-existing and local-only.** `test_signal_discovery_wave2_nfl.py::test_prop_artifact_reproduces_the_wave1_2026_predictions`
  runs only when the gitignored Wave-1 player table is rebuilt locally (CI skips it). On the rebuilt table it differs
  by 4.4e-16, a floating-point artefact of the local rebuild (which also adds one week-5 game), not a code change.
  The frozen files are hash-identical.

## AG. Artifacts

`research/rb_receptions_mechanism/`:

| File | Contents | Note |
|---|---|---|
| `build_manifest.json` | Checks, hashes, the nflverse vintage | |
| `rows_2026.jsonl.gz` | P1, P3, P4, P5 rows, with quotes, settlement, pregame features and timeline | |
| `rows_2025.jsonl.gz` | P2 rows, every rung, T-90m / T-0 | |
| `ladders_2026.jsonl.gz`, `ladders_2025.jsonl.gz` | Ladders | |
| `quote_history_2026.jsonl.gz` | Pre-kickoff rows for the studied tickers | 10.5 MB |
| `rb_history_2016_2025.jsonl.gz` | The dispersion / recency corpus | |
| `mechanism_report.json` | The artifact | `nfl_rb_receptions_mechanism/1.0.0` |

Reproduce:

```
python scripts/research/rb_receptions_mechanism.py extract-quotes --market-data MD --out QDIR
python scripts/research/rb_receptions_mechanism.py build --market-data MD --quotes QDIR
python scripts/research/rb_receptions_mechanism.py analyze
```

## AH. Production impact

**None.** No change to:

* projections, Shadow v2, RUN NFL, the board, the recommendation engine, the pricer, staking, the router or SIFT;
* Wave-2 candidates, rules, scheduler or ledgers.

Every change is an addition under `docs/research/`, `research/rb_receptions_mechanism/`, `scripts/research/` (two new
scripts), `nfl_edge/signal_discovery/rb_mechanism.py` (new) and `tests/`.

## AI. Direct answers

1. **Is it just a generic NO bias?** **No.** Pooled controls are about 0 (−0.013), and several families lean the
   other way.
2. **Is YES systematically overpriced on the RB receptions natural rung?** In both contaminated seasons it settled
   8–9 points below the mid. That is consistent in sign, but not statistically established after correction.
3. **Does that survive bid/ask adjustment?** **Yes.** The midpoint and the normalised midpoint give the same −0.085.
   The 2026 markets were 1¢-wide.
4. **Is it caused by integer thresholds?** **Partly.** Over-dispersion at integer lines explains about 3 of the 8–9
   points; losses are mostly near misses.
5. **Does the market underestimate zero / low outcomes?** **Not specifically zeros.** The under-statement is at
   t − 1, plus mildly at ≤ t − 2. Zeros match a negative binomial.
6. **Is role uncertainty part of it?** **No.** The shortfall is larger for stable, workhorse, concentrated-backfield
   backs.
7. **Does recent performance influence pricing too much?** **No.** The market weights the last game less than
   outcomes justify.
8. **How dependent is it on a handful of players?** P/L is very concentrated: the top 5 players are 150 % / 100 % of
   it. But a uniform 8-point shift would show the same drop at this n, so player-specificity is not shown.
9. **Does the natural-rung rule add beyond ALWAYS_NO?** Descriptively yes: +11.7 % vs +0.4 % (2026), +8.5 % vs
   +3.1 % (2025). That is because the shape error is largest in probability units near 50 %. The difference is
   within noise (T3 p 0.11).
10. **The single most likely mechanism?** A count-distribution shape mismatch. The ladder is near-Poisson while RB
    receptions are over-dispersed, which over-prices "exactly t" for high-mean backs. The rest is noise.
11. **A credible reason it could persist?** A structural reason exists, but its size (≈ 3 points) is about the cost
    of buying NO (≈ 2.5 points over the mid). The rest of the historical ROI has no established reason to persist.
12. **Should NFL-PROP-PROS-001 be changed?** **NO.** No implementation or integrity defect was found. The frozen rule,
    natural rung, tie-break and settlement all reproduce exactly.
