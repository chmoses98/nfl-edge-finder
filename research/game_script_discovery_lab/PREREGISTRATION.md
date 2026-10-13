# Preregistration (written into the runner BEFORE any candidate was scored)

Honesty note: the screening and qualification rules below were coded in `scripts/sim/gsdl_stats.py` before the tournament was
run, but are not independently timestamped. Two things were changed after seeing results and are disclosed: the match of
game types (postseason games use WC/DIV/CON/SB, not POST; fixed before any comparison was read) and the four `*_reg` variants of
sparse-support candidates (added after the raw versions put near-zero mass on realised outcomes). They are scored and counted.

A candidate QUALIFIES only if ALL hold: (1) >=0.5% relative improvement vs A0 on a primary metric over the selection seasons
(2021-2023); (2) max-t adjusted p < 0.10 over all candidate x primary tests; (3) the same metric improves >=0.5% on the
confirmation seasons (2024-2025) with a game-clustered 95% interval below zero; (4) no primary metric worse than 0.25%;
(5) randomized-PIT chi-square p >= 0.01 for margin and total; (6) every feature is PIT-clean or T0 (weather observations are not).
2021-2025 has informed earlier SIFT research: both sets are historical evidence, not untouched holdouts. 2026 is untouched.
