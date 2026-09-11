# Period engine: walk-forward comparison of period distributions (HISTORICAL_RESEARCH)

`scripts/research/period_engine_study.py`. 1612 regular-season games, test seasons 2020-2025, every candidate fitted on seasons strictly before the test season and centred on the consensus closing line; 6000 draws per game. HISTORICAL_RESEARCH evidence: used to choose the shadow engine, never mixed with prospective records.

## Ladder Brier (lower is better)

| candidate | 1H winner | 1H spread ladder | 1H total ladder | 1Q total ladder | 1Q spread ladder | 1Q winner | CRPS 1H total |
|---|---|---|---|---|---|---|---|
| NAIVE_SCALE | 0.17591 | 0.19722 | 0.18787 | 0.20529 | 0.20659 | 0.21875 | 4.891 |
| REG_NORMAL | 0.17613 | 0.19719 | 0.18833 | 0.18037 | 0.20780 | 0.21720 | 4.899 |
| REG_EMPIRICAL_JOINT | 0.17651 | 0.19713 | 0.18673 | 0.17795 | 0.20750 | 0.21803 | 4.865 |
| LINE_BUCKET_EMPIRICAL | 0.17829 | 0.19973 | 0.18806 | 0.17728 | 0.20755 | 0.21228 | 4.898 |
| KERNEL_EMPIRICAL | 0.17734 | 0.19795 | 0.18802 | 0.17746 | 0.20690 | 0.21174 | 4.896 |
| KERNEL_EMPIRICAL_SHIFTED (default) | 0.17757 | 0.19794 | 0.18702 | 0.17756 | 0.20715 | 0.21223 | 4.874 |

## Log loss

| candidate | 1H winner | 1H spread ladder | 1H total ladder | 1Q total ladder | 1Q spread ladder | 1Q winner |
|---|---|---|---|---|---|---|
| NAIVE_SCALE | 0.52291 | 0.57833 | 0.55757 | 0.60466 | 0.60102 | 0.64461 |
| REG_NORMAL | 0.52298 | 0.57843 | 0.55872 | 0.54029 | 0.60428 | 0.63539 |
| REG_EMPIRICAL_JOINT | 0.52456 | 0.57816 | 0.55492 | 0.53445 | 0.60297 | 0.63995 |
| LINE_BUCKET_EMPIRICAL | 0.52919 | 0.58516 | 0.55898 | 0.53295 | 0.60531 | 0.61454 |
| KERNEL_EMPIRICAL | 0.52430 | 0.58021 | 0.55870 | 0.53339 | 0.60213 | 0.61327 |
| KERNEL_EMPIRICAL_SHIFTED | 0.52640 | 0.58019 | 0.55643 | 0.53362 | 0.60284 | 0.61481 |

## Reliability slope (ideal 1.00) and mean predicted / observed

| candidate | 1H winner | 1H spread ladder | 1H total ladder | 1Q total ladder | 1Q spread ladder | 1Q winner |
|---|---|---|---|---|---|---|
| NAIVE_SCALE | 0.95 (0.333/0.333) | 0.94 (0.527/0.533) | 1.03 (0.506/0.472) | 1.04 (0.609/0.451) | 0.94 (0.521/0.518) | 0.54 (0.333/0.333) |
| REG_NORMAL | 0.93 (0.333/0.333) | 0.93 (0.541/0.533) | 1.02 (0.510/0.472) | 0.99 (0.498/0.451) | 0.90 (0.535/0.518) | 0.57 (0.333/0.333) |
| REG_EMPIRICAL_JOINT | 0.93 (0.333/0.333) | 1.02 (0.538/0.533) | 0.99 (0.479/0.472) | 1.01 (0.462/0.451) | 0.99 (0.534/0.518) | 0.56 (0.333/0.333) |
| LINE_BUCKET_EMPIRICAL | 0.98 (0.333/0.333) | 1.01 (0.540/0.533) | 1.00 (0.460/0.472) | 1.02 (0.455/0.451) | 0.99 (0.536/0.518) | 0.88 (0.333/0.333) |
| KERNEL_EMPIRICAL | 1.00 (0.333/0.333) | 1.02 (0.536/0.533) | 1.01 (0.463/0.472) | 1.02 (0.452/0.451) | 1.00 (0.531/0.518) | 0.93 (0.333/0.333) |
| KERNEL_EMPIRICAL_SHIFTED | 0.92 (0.333/0.333) | 1.00 (0.537/0.533) | 0.99 (0.465/0.472) | 1.02 (0.453/0.451) | 1.00 (0.532/0.518) | 0.77 (0.333/0.333) |

## Key-number mass of the 1H margin (predicted / observed)

| candidate | |m|=0 | |m|=3 | |m|=7 |
|---|---|---|---|
| NAIVE_SCALE | 0.043 / 0.069 | 0.081 / 0.124 | 0.065 / 0.114 |
| REG_NORMAL | 0.043 / 0.069 | 0.080 / 0.124 | 0.065 / 0.114 |
| REG_EMPIRICAL_JOINT | 0.040 / 0.069 | 0.075 / 0.124 | 0.061 / 0.114 |
| LINE_BUCKET_EMPIRICAL | 0.070 / 0.069 | 0.117 / 0.124 | 0.124 / 0.114 |
| KERNEL_EMPIRICAL | 0.073 / 0.069 | 0.115 / 0.124 | 0.117 / 0.114 |
| KERNEL_EMPIRICAL_SHIFTED | 0.049 / 0.069 | 0.088 / 0.124 | 0.079 / 0.114 |

## Paired Brier differences vs KERNEL_EMPIRICAL_SHIFTED (game-clustered SE; positive = KERNEL_EMPIRICAL_SHIFTED better)

| candidate | 1H winner | 1H spread ladder | 1H total ladder | 1Q total ladder | 1Q spread ladder | 1Q winner |
|---|---|---|---|---|---|---|
| NAIVE_SCALE | -0.00167 ± 0.00056 | -0.00072 ± 0.00060 | +0.00085 ± 0.00085 | +0.02773 ± 0.00264 | -0.00056 ± 0.00062 | +0.00652 ± 0.00124 |
| REG_NORMAL | -0.00144 ± 0.00052 | -0.00075 ± 0.00052 | +0.00131 ± 0.00091 | +0.00281 ± 0.00088 | +0.00065 ± 0.00054 | +0.00497 ± 0.00103 |
| REG_EMPIRICAL_JOINT | -0.00106 ± 0.00053 | -0.00081 ± 0.00051 | -0.00029 ± 0.00047 | +0.00039 ± 0.00047 | +0.00034 ± 0.00052 | +0.00580 ± 0.00105 |
| LINE_BUCKET_EMPIRICAL | +0.00072 ± 0.00075 | +0.00179 ± 0.00073 | +0.00104 ± 0.00060 | -0.00028 ± 0.00060 | +0.00040 ± 0.00063 | +0.00005 ± 0.00074 |
| KERNEL_EMPIRICAL | -0.00023 ± 0.00029 | +0.00001 ± 0.00020 | +0.00100 ± 0.00039 | -0.00010 ± 0.00021 | -0.00026 ± 0.00016 | -0.00049 ± 0.00051 |

## KERNEL_EMPIRICAL_SHIFTED by test season (1H spread ladder Brier)

| season | games | Brier |
|---|---|---|
| 2020 | 256 | 0.20756 |
| 2021 | 269 | 0.20486 |
| 2022 | 271 | 0.19413 |
| 2023 | 272 | 0.19642 |
| 2024 | 272 | 0.19605 |
| 2025 | 272 | 0.18928 |

## Market comparison

Not possible historically: the 2025 Kalshi archive holds 203 first-half / first-quarter contracts over six playoff games (68 1H spread, 63 1H total, 24 1Q spread, 21 1H winner, 18 1Q total, 9 1Q winner). The prospective record is the only way to learn whether this engine adds information to Kalshi's period quotes, which is why it is shadow-only.

## What this establishes and does not

* The regression centres are the point: the naive division baseline mis-centres every period ladder (1Q total is 19% of the full line, 1H margin 56% of the spread).
* Ladders within one period are coherent by construction (one simulation); the choice among candidates is a shape question (key-number mass, tails), which the Brier alone is nearly blind to -- read the key-number and reliability rows.
* Nothing here is a betting result. The engine is SHADOW: it writes projections and accumulates prospective evidence.
