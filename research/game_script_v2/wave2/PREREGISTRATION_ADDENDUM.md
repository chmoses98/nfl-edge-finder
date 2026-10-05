# GAME SCRIPT V2 — WAVE 2: preregistration addendum A

This addendum only RECORDS the outputs of the procedures fixed in `PREREGISTRATION.md` (commit
`0aea50fcd30b4eafc94c1228f716cd77e01f5db9`; PROSPECTIVE CUTOFF 2026-10-05T16:14:02+00:00). It changes no procedure,
metric, gate, window or subgroup. `PREREGISTRATION.md` itself is byte-frozen (sha256
`2d4870e310b3db1ed948de1889579f4cc4b09d05e0350983fd363f4b90ded3e9`, tested).

**State when this addendum was committed:** no Wave-2 projection record exists (the capture workflow is not on `main`;
`data/research/wave2` on market-data is empty), no GAME SCRIPT V2 `scripts_v2` capture exists yet, and no prospective
outcome of any kind has been read. Everything below comes from seasons <= 2020 (selection, mechanism checks, sample
sizes) or from the 2021-2025 contaminated diagnostic (status only, as section 7 defines).

## A.1 Selected forms (section 2-4 procedures)

| arm | selected | rule outcome (development) | detail |
|---|---|---|---|
| S1 carries | **S1-1** | S1-1 − S1-0 2020 DM log-lik per team-game +0.163 [+0.069, +0.277] | `S1_SHARE_DISPERSION.json` → `selection.carry` |
| S1 targets | **S1-1** | +0.041 [+0.018, +0.069] | `selection.target` |
| Q1 | **Q1-0** (unconditional three-regime mixture) | conditional − unconditional log loss −0.0147 [−0.0373, +0.0082]: interval includes zero | `Q1_QB_EXIT_TAIL.json` → `selection` |
| M1 | **M1-K** | log score vs incumbent bank, 2018-2020 pooled, +0.299 [+0.198, +0.403]; M1-S −1.16 | `M1_KEY_NUMBERS.json` → `selection` |
| A1 | T0_INACTIVES (no form to select; horizon rule of section 5) | — | `A1_AVAILABILITY_HORIZONS.json` |

## A.2 Statuses (section 7 status words, applied mechanically)

| arm | status | deciding facts |
|---|---|---|
| S1 | **PROSPECTIVE_CHALLENGER** | both families SELECTED; 2020 chi-square falls 5/5, edge-bin mass toward 0.20 5/5, CRPS of each of the five not worse; diagnostic primary −0.95% [−1.02, −0.87] |
| Q1 | **REJECTED_AT_DEVELOPMENT** | section-7 mechanism check fails: 2020 PARTIAL count 49 outside its 90% predictive band 19-40 (section-3 lower-decile check passes) |
| M1 | **PROSPECTIVE_CHALLENGER** | M1-K selected; coherent on every game; diagnostic log score +0.120 [+0.072, +0.169] |
| A1 | **PROSPECTIVE_CHALLENGER** | 2020 questionable abs-bias change −1.21 [−1.27, −0.28]; teammates' CRPS within +0.5%; diagnostic −0.76 [−1.14, −0.36] |
| RISK1 | **COLLECTING** | design of section 6; minimum sample below |

Ambiguities recorded (not resolved in any arm's favour): for Q1, section 3 and section 7 name different mechanism
checks — both are required. For S1, section 2 ("all five move toward uniform; CRPS not worse") is stricter than
section 7 (">= 3 of 5") — both are required, and both hold. For A1, "moves toward zero" (section 5) is applied to the
point estimate; the interval is also reported and also excludes zero.

## A.3 Minimum prospective samples (section 8 formula on the 2020 development simulation)

| arm | effect d | between-game sd | minimum games | weeks of 16 |
|---|---|---|---|---|
| S1 | −0.0109 (relative CRPS) | 0.0140 | **64** (floor) | 4 |
| M1 | +0.1222 (log score) | 1.1265 | **672** | 42 |
| A1 | −1.1921 (signed bias change) | 0.4385 | **64** (floor) | 4 |
| Q1 | — | — | not applicable (REJECTED_AT_DEVELOPMENT) | — |
| RISK1 | 0.02 (minimal effect of interest) | 0.1423 (synthetic 2020 study, 37,655 contracts) | **397** | 25 |

RISK1's 397 games is below two seasons, so the preregistered UNDERPOWERED label does not apply, but the primary test
cannot complete inside the 2026 season. A1's minimum counts only games whose last pre-kickoff record claims
T0_INACTIVES for both teams. Every arm also needs zero coherence failures and the leave-one-game-out condition of
section 7 at its minimum; promotion remains a human decision with no authority change in this wave.

## A.4 Frozen 2026 components

`research/game_script_v2/wave2/components_2026.json`, sha256
`353541d18e7e77f4cb06de4233f1b33ef0ff9772941c7792044f55a936ea7008` (committed in `85be89b`), recorded in every
prospective record. Parameters refit on 2018-2025 as section 1 allows (forms unchanged): S1-1 carry base alpha 9.69,
target 37.27 (log-alpha intercepts 2.271 / 3.618, nine standardised coefficients each, ridge 1.0); Q1-0 regime
probabilities FULL 0.868 / PARTIAL 0.075 / LOW 0.058 (captured for description only). M1-K uses history 2016..2025
with the section-4 parameters (h 2.0 / 4.0, half-life 3, effective n >= 200). A1 has no fitted component.

## A.5 Note appended after A.1-A.4 (still before any prospective record or outcome)

The Q1 conditional model was fitted with scikit-learn, which CI does not install. It is now fitted by
`qb_regimes._multinomial_ridge` (the same objective: summed multinomial log loss + ridge/2 * ||coef||^2, intercepts
unpenalised, L-BFGS). Re-running the section-3 selection gives conditional − unconditional log loss
−0.0146 [−0.0372, +0.0083] (A.1 recorded −0.0147 [−0.0373, +0.0082] from the scikit-learn fit; coefficients differ by
< 0.001). The selection (Q1-0), the unconditional model, the frozen components and every status are unchanged.
`Q1_QB_EXIT_TAIL.json` is rebuilt from the scipy fit.
