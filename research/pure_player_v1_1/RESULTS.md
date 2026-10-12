# PURE_PLAYER_V1_1 (PIT availability ablation): held-out results (research only)

* Preregistration: `docs/research/PURE_PLAYER_V1_1_PREREGISTRATION.md`, committed alone in **4441249** before any
  V1_1 forecast was scored. The code in `nfl_edge/engines/player/pure_v1_1/` was written after that commit and was
  not changed after the development run. PURE_PLAYER_V1 (0441dfc) is unchanged.
* Command: `python3 scripts/research/pure_player_v1_1_study.py --seasons 2023,2024 --label holdout_2023_2024`
  (full output in `holdout_2023_2024.json`; the development run is `dev_2022.json`).
* Data:
  * nflverse `stats_player_week` and `snap_counts` 2013–2024, `players`, the schedule's allowlisted columns, and
    `injuries` 2013–2024, retrieved 2026-10-11 (sha256 values in `research/pit_availability/certification.json`
    inputs);
  * injury rows go through `injuries_certified` with a 90 min lead. It refused 25 rows whose `date_modified` was at
    or after the cutoff and 17 rows that didn't join a team-game.
* Holdout coverage: 99.82% of 2023–2024 team-weeks have at least one certified injury row, against the 90%
  threshold. 42.5% of holdout player-game-statistic rows have a non-zero teammate-availability feature.

## Verdict (preregistered rule): **REJECTED**

* ΔMAE (V1_1 − V1) has its 95% CI below 0 on 4 of 9 statistics: carries, rushing yards, targets, and receptions.
  That meets the ≥ 4 requirement.
* One preregistered metric is significantly worse. For receptions, |p10–p90 coverage − 0.8| worsened by
  +0.0019 [+0.0003, +0.0035]: coverage went from 0.9202 to 0.9221, moving further from the 0.80 nominal.
  The rule is strict, so this one worsening rejects the challenger. PURE_PLAYER_V1 remains the PURE arm in collection.

## V1_1 vs V1, holdout 2023 + 2024 (Δ = V1_1 − V1; game-clustered 95% CI, B = 1000; 544 games)

| statistic | n | MAE V1 | MAE V1_1 | ΔMAE [CI] | ΔMSE [CI] | ΔCRPS [CI] | ΔBrier [CI] | Δlog loss [CI] | cov80 V1 → V1_1 |
|---|---|---|---|---|---|---|---|---|---|
| snap_share | 12,655 | 0.1210 | 0.1210 | −0.00003 [−0.00014, +0.00008] | −0.00003 [−0.00007, +0.00002] | −0.00001 [−0.0001, +0.0001] | −0.0001 [−0.0004, +0.0002] | −0.0002 [−0.0010, +0.0005] | 0.822 → 0.822 |
| targets | 11,603 | 1.5740 | 1.5695 | **−0.0045 [−0.0073, −0.0017]** | −0.029 [−0.046, −0.012] | −0.0052 [−0.0082, −0.0025] | −0.0006 [−0.0013, −0.0001] | −0.0013 [−0.0027, −0.0001] | 0.910 → 0.912 |
| receptions | 11,603 | 1.2213 | 1.2187 | **−0.0026 [−0.0043, −0.0009]** | −0.012 [−0.019, −0.005] | −0.0025 [−0.0047, −0.0005] | −0.0005 [−0.0011, −0.00002] | −0.0011 [−0.0024, +0.00003] | 0.920 → 0.922 (**worse, CI > 0**) |
| receiving_yards | 11,603 | 15.622 | 15.604 | −0.017 [−0.039, +0.008] | −1.79 [−3.12, −0.34] | −0.025 [−0.040, −0.010] | −0.0005 [−0.0010, −0.000003] | −0.0015 [−0.0027, −0.0003] | 0.879 → 0.879 |
| carries | 4,031 | 3.0855 | 3.0591 | **−0.026 [−0.039, −0.015]** | −0.28 [−0.41, −0.16] | −0.020 [−0.030, −0.010] | −0.0013 [−0.0027, +0.0001] | −0.0023 [−0.0055, +0.0009] | 0.884 → 0.880 |
| rushing_yards | 4,031 | 17.910 | 17.834 | **−0.076 [−0.131, −0.020]** | −4.10 [−7.39, −1.02] | −0.042 [−0.082, −0.005] | −0.0020 [−0.0033, −0.0007] | −0.0043 [−0.0072, −0.0014] | 0.841 → 0.838 |
| passing_attempts / completions / passing_yards | 1,088 each | identical | identical | 0 | 0 | 0 | 0 | 0 | unchanged (QB passing stages take no new input, as preregistered) |

Against PURE_EWM_BASELINE, V1_1's ΔMAE is below 0 on all 9 statistics, with the CI below 0 on 8. The exception is
passing yards: −1.27 [−2.46, +0.02].

## Subgroups (preregistered, descriptive; ΔMAE V1_1 − V1)

| statistic | rows with a teammate listed Out/Doubtful, or the prior starting QB Out/Doubtful | all other rows |
|---|---|---|
| targets | **+0.011 [+0.006, +0.017]** (4,933) | −0.016 [−0.018, −0.014] (6,670) |
| receptions | **+0.007 [+0.004, +0.010]** | −0.010 [−0.011, −0.008] |
| receiving yards | **+0.154 [+0.111, +0.199]** | −0.144 [−0.162, −0.129] |
| carries | −0.029 [−0.053, −0.004] (1,701) | −0.025 [−0.031, −0.019] (2,330) |
| rushing yards | −0.010 [−0.128, +0.105] | −0.124 [−0.159, −0.091] |

By season, the ΔMAE signs match in 2023 and 2024 for every affected statistic (`holdout_2023_2024.json`). By
position group, RB carries and rushing yards and WR targets and receptions improve, while QB rushing doesn't change.

**Reading (not part of the verdict).** For receiving, the aggregate gain sits in the rows where the new
features are zero, and the rows they were meant to help get worse. The likely mechanism comes from the
preregistered definition: `vac_t` counts every teammate listed Out or Doubtful, including players already absent
for weeks. Their absence is already in the team's recent shares, so it is counted twice, and the refit shifts the
share model's baseline instead. A version that counts only teammates who played in the team's previous game
("newly vacated") is the obvious next hypothesis. It would be a new preregistration (V1_2). It needs a holdout
V1_1 hasn't seen: 2010–2022 is training here, so the honest test is the prospective PIT capture.

## Market independence

V1_1 reads only V1's football inputs plus the certified injury report. `tests/test_pit_availability.py`
checks three things:
* With no injury rows, V1_1 reproduces V1's forecasts exactly.
* V1_1's forecasts are bit-identical with the schedule's market columns removed or randomised, while V4's
  VolumeModel (the negative control) changes.
* No feature reads a future box score.
