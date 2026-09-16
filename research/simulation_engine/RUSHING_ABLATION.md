# Rushing enrichment: source audit and walk-forward ablation

Reproduce: `python scripts/sim/rushing_ablation.py --seasons 2023,2024,2025`.  Generated from `rushing_ablation.json` by `scripts/sim/write_results.py` -- do not edit by hand.

Each arm adds columns to the per-carry efficiency model.  For every evaluation season the model is fitted on carries of earlier seasons only -- including the frozen shrinkage priors of both the base features and the enrichment -- and scored on the evaluation season.  Player-game rows are restricted to >= 6 carries, the population a rushing ladder is listed on.

## Arms

* **baseline** — the current model
* **ol** — `off_ybc_att`, `ol_continuity`, `ol_out`, `off_stuff_rate`
* **front** — `def_ybc_att_adj`, `def_stuff_rate_adj`, `def_rush_epa_att_adj`, `def_exp10_rate`
* **runner** — `rt_ybc_att`, `rt_yac_att`, `rt_stuff_rate`, `rt_broken_att`
* **context** — `off_qb_rush_share`, `indoor`
* **combined** — `off_ybc_att`, `ol_continuity`, `ol_out`, `off_stuff_rate`, `def_ybc_att_adj`, `def_stuff_rate_adj`, `def_rush_epa_att_adj`, `def_exp10_rate`, `rt_ybc_att`, `rt_yac_att`, `rt_stuff_rate`, `rt_broken_att`, `off_qb_rush_share`, `indoor`

## Out-of-sample result

| arm | per-carry MAE 2023 / 2024 / 2025 | per-carry r² | player-game MAE | Δ player-game MAE vs baseline | improves every season |
|---|---|---|---|---|---|
| baseline | 3.6725 / 3.7711 / 3.6790 | 0.00885 / 0.00584 / 0.00621 | 15.70 / 16.60 / 17.44 | 0.0000 / 0.0000 / 0.0000 (mean 0.0000) | False |
| ol | 3.6693 / 3.7683 / 3.6778 | 0.00914 / 0.00577 / 0.00599 | 15.63 / 16.57 / 17.43 | -0.0612 / -0.0258 / -0.0122 (mean -0.0330) | True |
| front | 3.6751 / 3.7697 / 3.6828 | 0.00893 / 0.00565 / 0.00602 | 15.69 / 16.64 / 17.50 | -0.0060 / 0.0477 / 0.0505 (mean 0.0307) | False |
| runner | 3.6710 / 3.7709 / 3.6817 | 0.00872 / 0.00612 / 0.00570 | 15.67 / 16.59 / 17.49 | -0.0235 / -0.0065 / 0.0482 (mean 0.0061) | False |
| context | 3.6797 / 3.7749 / 3.6749 | 0.00832 / 0.00623 / 0.00651 | 15.86 / 16.57 / 17.43 | 0.1636 / -0.0296 / -0.0120 (mean 0.0407) | False |
| combined | 3.6696 / 3.7684 / 3.6845 | 0.00853 / 0.00645 / 0.00532 | 15.81 / 16.60 / 17.58 | 0.1129 / 0.0065 / 0.1359 (mean 0.0851) | False |

## Verdict: none of it is deployed

Per-carry rushing yardage has an out-of-sample r² of 0.00584-0.00885 in the current model, and no arm moves it.  The offensive-line arm is the only one that improves player-game rushing-yards MAE in all three seasons, and it does so by 0.0330 yards on a ~16.6-yard error (0.2%), for four extra parameters.  That passes the direction test and fails any materiality bar, so it is NOT deployed; the code stays available behind `rushing.ARMS` for a future preregistered test on a larger sample.  The opponent-adjusted defensive front, the runner's yards-before/after-contact and the combined arm are all worse in at least one season, and `combined` is the worst of the six -- twenty-four parameters chasing a signal that is not there.

**The useful finding is where the value is not.** Across the same walk-forward the opportunity model beats its naive baseline by 12-20% on carries while the efficiency model explains under 1% of per-carry variance.  Rushing-projection accuracy is almost entirely an opportunity problem, so the next investment belongs in carry share, role change and availability -- not in more efficiency covariates.

## Rejected sources, and why

* **ftn_scheme** — only a file-level date_pulled, which moves when the file is rebuilt (weeks 1-5 of 2024 all carry 2025-09-01), so no per-row publication instant exists and no point-in-time claim can be made; coverage also starts in 2022, leaving one training season for the earliest evaluation
* **observed_weather** — the schedule's temp/wind are measured AT the game (hindsight) and are null indoors; forecast vintages only exist from 2026-09-04, so no historical fit can use them. 'indoor' (roof) is retained.

