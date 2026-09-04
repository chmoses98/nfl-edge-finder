# Player opportunity engine

Reproduce: `python3 scripts/research/opportunity_study.py` → `research/opportunity/results.json`

## The data: real routes, free, 2016–2025

nflverse `pbp_participation.offense_players` lists the eleven men on the field for every play. A route is a
dropback the player was on the field for. After restricting to run/pass plays the coverage is **100% of
plays in every season including 2025** (99.98% in 2016 — 0.982 for the worst single team-game). This yields
routes, route share, targets per route run, red-zone routes and red-zone/inside-5 carry shares — the role
data that is normally paywalled — for 102,422 player-games.

## Finding 1: the multiplicative decomposition fails, and it fails for a specific reason

The obvious construction — project team volume, project the player's share, multiply — is **worse than an
EWMA of the player's raw counts in every season tested**:

| target | pooled 2019–2025 | decomposition MAE | raw-EWMA MAE | delta |
|---|---|---|---|---|
| targets | n=26,560 | 2.116 | 2.097 | **+0.019** |
| carries | n=11,043 | 4.075 | 3.919 | **+0.156** |

`routes × targets-per-route` instead of `dropbacks × target share` does not rescue it (2.12 pooled).

The reason is upstream. **Team volume is close to unpredictable.** Projecting a team's dropbacks from its own
prior form *and the market's spread and total* gives MAE 6.62 plays; simply guessing the league constant
gives 6.93. All that structure buys 4.5%. Rush attempts: 5.54 versus 5.74, buying 3.5%. Multiplying a share
estimated with error by a volume estimate that is barely better than a constant compounds two errors to
replace one — meanwhile the raw-count EWMA gets the player's typical team volume for free, with no variance.

Two subgroup tests were **specified before any subgroup result was looked at**, on the decomposition's own
premise — it should win where this game's team volume is unusual for that player, and where his role is
still unsettled. It won neither (top quartile by volume gap: 2.100 vs 2.087, winning 2 of 7 seasons; top
quartile by role instability: 2.207 vs 2.205, winning 4 of 7). No third subgroup was tried. **The
decomposition is rejected.**

## Finding 2: the same features, added rather than substituted, work — 7/7 seasons

Whether the role data should *replace* the baseline is a different question from whether it carries
information the baseline lacks. Put the share features alongside `ewma_targets` in one walk-forward ridge on
the full population:

| target | n | baseline alone | + role features | delta | seasons improved |
|---|---|---|---|---|---|
| targets | 26,560 | 2.0630 | **2.0101** | −0.0530 (−2.6%) | **7 / 7** |
| carries | 11,043 | 3.9222 | **3.8009** | −0.1213 (−3.1%) | **7 / 7** |

Per season the improvement runs −0.030 to −0.072 (targets) and −0.106 to −0.142 (carries), monotone in sign
across every season, including 2025. Nothing here was selected on: one population, one model class, one
fit-on-prior-seasons rule, and the sign is the same every year. This is the version of the opportunity engine
that earns its place — route share, targets per route run, snap share, red-zone and inside-5 shares as
**regressors**, not as a reconstruction.

Added features, in order of what they contribute: `pit_route_share`, `pit_tprr`, `pit_snap_share`,
`pit_rz_target_share`, `pit_adot`, `proj_team_dropbacks`, `pit_shrink_w`, `implied_total`, `spread_team`
(carries: `pit_carry_share`, `pit_snap_share`, `pit_rz_carry_share`, `pit_i5_carry_share`,
`proj_team_rush_att`, …).

## Leakage control

Every feature is an EWMA written *before* the current row's update, with a season-boundary discount and
shrinkage toward a prior estimated only on 2016–2018 (evaluation starts 2019). `tests/test_opportunity_leakage.py`
asserts the property rather than the implementation: perturbing row *i*'s own outcome must leave row *i*'s
feature bit-identical while moving row *i+1*'s; appending future games must not move any past feature; a
player's first game must equal the pure prior; players must not bleed into one another; and priors must not
absorb data from outside their window.

## What this does not yet establish

MAE on the conditional mean is not the quantity that prices a ladder. Whether these features improve
**calibrated P(Y ≥ k)** — the only thing the shadow ledger consumes — is the next test, and a mean
improvement of 2.6% may or may not survive into the tails. Nothing here has been fed into the pricer.
