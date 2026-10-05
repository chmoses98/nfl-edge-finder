# GAME SCRIPT V2 — WAVE 2 (RESEARCH_ONLY)

Starting point: `main` at `0574cafa8cccd555a2e27ce7dbb6417aa8af867b` (merge of PR #112). **No arm in this wave has
betting, staking, BET/PASS, model-probability, price-limit, unit-size or reconciliation-weight authority.** GAME
SCRIPT V2 stays displayed in RUN NFL as RESEARCH_ONLY and controls nothing.

**PROSPECTIVE CUTOFF: 2026-10-05T16:14:02+00:00** (committer time of `0aea50fcd30b4eafc94c1228f716cd77e01f5db9`, the
commit that added `PREREGISTRATION.md`). Seasons <= 2020 are DEVELOPMENT; 2021-2025 and every 2026 game kicking off
before the cutoff are CONTAMINATED_DIAGNOSTIC (descriptive only); only games kicking off after the cutoff with a frozen
pre-kickoff record are PROSPECTIVE evidence.

| file | what | generated from |
|---|---|---|
| `PREREGISTRATION.md` | designs, development-only selection procedures, gates, sample-size procedure; byte-frozen (tested) | hand-written, committed first |
| `PREREGISTRATION_ADDENDUM.md` | the OUTPUTS of the preregistered procedures: selected forms, frozen components, statuses, minimum samples | hand-written, committed before any prospective record exists |
| `PROSPECTIVE_PROTOCOL.md` | how prospective records are captured, selected and scored | hand-written |
| `S1_SHARE_DISPERSION.md` | S1 selection, 2020 mechanism check, 2021-2025 diagnostic, subgroups | `S1_SHARE_DISPERSION.json` |
| `Q1_QB_EXIT_TAIL.md` | Q1 regimes, identification error vs exit, lower-tail check, regime bands | `Q1_QB_EXIT_TAIL.json` |
| `M1_KEY_NUMBERS.md` | M1-K / M1-S vs the incumbent residual bank, emergent key numbers, bank audit | `M1_KEY_NUMBERS.json` |
| `A1_AVAILABILITY_HORIZONS.md` | T0_INACTIVES and T24 against the incumbent's mixed horizon | `A1_AVAILABILITY_HORIZONS.json` |
| `RISK1_SCRIPT_ROBUSTNESS.md` | RISK1 design, power study, collection status | `RISK1_SCRIPT_ROBUSTNESS.json` |
| `components_2026.json` | frozen S1 / Q1 components for the 2026 prospective records (refit on 2018-2025; forms fixed) | `scripts/sim/wave2_components.py` |

Every report is a pure render of its JSON (`python scripts/sim/wave2_render.py`; `--check` and
`tests/test_wave2_results_consistency.py` fail on drift). The JSON is built by `scripts/sim/wave2_report.py`
(S1 / Q1 / A1 / RISK1) and `scripts/sim/wave2_m1.py` from the runs of `scripts/sim/wave2_arms.py`.

## Status

| arm | status | in one line |
|---|---|---|
| S1 | **PROSPECTIVE_CHALLENGER** | the incumbent's opportunity concentration double-counts multinomial noise; likelihood-fitted, concentration-conditioned alphas cut the five opportunity statistics' CRPS by ~1% in 2020 and in every diagnostic season, PIT chi-square falls 1.4-4x; worse for players with no prior game (small subgroup) |
| Q1 | **REJECTED_AT_DEVELOPMENT** | fixes the lower-decile QB tail but the 2018-2019 regime model's PARTIAL band misses 2020 (49 vs 19-40), the feature model does not beat plain frequencies, and the mean overshoots |
| M1 | **PROSPECTIVE_CHALLENGER** | kernel-tilted empirical (margin, total) keeps key numbers, is exactly centred and coherent; exact-margin log score +0.30 on 2018-2020, point estimate positive in every diagnostic season |
| A1 | **PROSPECTIVE_CHALLENGER** | at T0_INACTIVES the incumbent's second questionable discount is removed: questionable players' bias moves to near zero, CRPS -4% to -10%, teammates unchanged; but yardage overshoots (MAE +3-5%) and the effect shrinks by 2025; T24 is reported as the honest earlier horizon and is worse |
| RISK1 | **COLLECTING** | design and power frozen (397 games, ~1.4 seasons); no result before the minimum sample; never changes a probability |

No arm earned more than PROSPECTIVE_CHALLENGER; nothing is promoted automatically, and promotion would itself be a
human decision with no authority change in this wave.

## Reproduce

```
python scripts/sim/wave2_s1_dev.py && python scripts/sim/wave2_q1_dev.py          # development selection (<= 2020)
python scripts/sim/wave2_arms.py --arm A0 --seasons 2019,2020 --phase dev           # incumbent on the dev bundle
python scripts/sim/wave2_arms.py --arm S1 --seasons 2020 --phase dev               # likewise Q1, A1T0, A1T24
python scripts/sim/wave2_arms.py --arm S1 --seasons 2021,2022,2023,2024,2025 --phase diag # contaminated diagnostic
python scripts/sim/wave2_m1.py                                                     # M1 (dev + diag)
python scripts/sim/wave2_risk1_power.py                                            # RISK1 sample size (2020)
python scripts/sim/wave2_report.py {s1,q1,a1,risk1} && python scripts/sim/wave2_render.py
python scripts/sim/wave2_components.py                                             # frozen 2026 components
```

The diagnostic comparison base is the Wave-1 five-season incumbent run (`data/cache/game_script_v2/baseline`,
`nfl_edge/sim/five_year.py`), the same code and seeds.
