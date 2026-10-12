# Why PURE_PLAYER_V1 trails DATA_PLAYER_V4: error decomposition (research only)

**Date:** 2026-10-12. **Status:** research diagnostic. It changes no model, no production path and no label.
PURE_PLAYER_V1 (`pure-player-v1.0.0`) is frozen and is only re-run here.

* Data: nflverse `stats_player_week`, `snap_counts`, `players`, `injuries`, `weekly_rosters` and the schedule.
  Retrieved 2026-10-12T01:53Z. The 2024 and 2025 files are byte-identical to the V1 study's manifest
  (`research/pure_player_v1/data_manifest.sha256`).
* Reproduction check: every arm's MAE matches `research/pure_player_v1/results.json` exactly, on every statistic.
  For example, receiving yards: PURE 15.3353, V4_MARKET_CLOSE 15.2176, n = 11,559.
* Commands (outputs: `research/pure_gap/decomposition.json` and `DECOMPOSITION_TABLES.md`):
  * `python3 scripts/research/pure_gap_arms.py --data-root <root> --seasons 2024,2025 --cache <dir>`
  * `python3 scripts/research/pure_gap_decomposition.py --arms <dir>/pure_gap_arms_2024_2025.pkl --data-root <root>`
  * `python3 scripts/research/pure_gap_render.py`

## Population and method

* **Rows.** The rows are the held-out player-games of the PURE_PLAYER_V1 comparison: the 2024 and 2025 regular
  seasons, each forecast by models fitted strictly before that season. Only rows that all four arms forecast are
  kept.
  * There is one row per player-game-statistic, and the metric is the MAE of the forecast mean.
  * Every interval is a paired, game-clustered bootstrap 95% CI (B = 1000, seed 20261010), and n is reported with it.
  * Row counts: 544 games. Snap share n = 12,567; targets, receptions and receiving yards 11,559; carries and
    rushing yards 3,990; starting-QB passing statistics 1,050.
* **Arm ladder.** V4's own config switches give an exact additive split, with no new modelling:

  | arm | what it is |
  |---|---|
  | PURE_PLAYER_V1 | frozen |
  | V4_MEF_NO_AVAIL | V4 with `market_env=False` and `redistribution=False`. Every own-status and teammate-availability feature is dropped: injury report, weekly roster, vacated and returning roles. |
  | V4_MEF_AS_IS | V4 with `market_env=False` |
  | V4_MARKET_CLOSE | V4 with the closing spread and total (default config). Market-informed. |

  PURE − V4_MARKET_CLOSE = **(1)** (PURE − V4_NO_AVAIL) + **(2)** (V4_NO_AVAIL − V4_MEF) + **(3)** (V4_MEF − V4_MKT).
  * (1) is the difference in sports-only model structure.
  * (2) is the value of the availability features.
  * (3) is the value of the market environment.
* **Components.** Each arm's scored mean factors exactly into
  team volume × snap share × usage (opportunities per on-field team play) × efficiency (statistic per
  opportunity). The factors are:
  * team volume: pass or rush attempts;
  * usage: targets, carries or attempts per on-field team play;
  * efficiency: catches, yards or completions per opportunity.

  The volume, snap and usage parts together are opportunity/workload; efficiency is per-opportunity output.
  The Shapley value of each component over all 2^K hybrid forecasts splits a paired gap into parts that sum to it
  exactly. `max_abs_factorisation_error` is 0 for every statistic. An "oracle" version, which substitutes the
  realised components, splits each arm's own MAE.
* **Labels.** The availability strata and the opponent "oracle" use realised or hindsight information. They are
  diagnostic labels for slicing the error and are never model inputs.

## Headline: where the gap comes from

The table splits each gap into the ladder terms (1), (2) and (3); Δ is in MAE. A positive value means the first
arm is worse. **Bold** marks a CI that excludes 0.

| statistic | n | PURE − V4_MKT | (1) structure, sports-only | (2) availability features | (3) market environment |
|---|---|---|---|---|---|
| snap share | 12,567 | **+0.0018** [+0.0009, +0.0027] | **−0.0023** [−0.0030, −0.0016] | **+0.0041** [+0.0035, +0.0047] | 0 (by construction) |
| targets | 11,559 | **+0.013** [+0.008, +0.018] | **−0.004** [−0.009, −0.001] | **+0.017** [+0.014, +0.021] | +0.000 [−0.001, +0.002] |
| receptions | 11,559 | **+0.008** [+0.005, +0.011] | **−0.004** [−0.007, −0.002] | **+0.011** [+0.009, +0.013] | +0.001 [−0.001, +0.002] |
| receiving yards | 11,559 | **+0.12** [+0.07, +0.17] | −0.04 [−0.08, +0.00] | **+0.10** [+0.07, +0.12] | **+0.06** [+0.03, +0.08] |
| carries | 3,990 | **+0.050** [+0.028, +0.073] | +0.005 [−0.012, +0.024] | **+0.043** [+0.029, +0.057] | +0.002 [−0.002, +0.006] |
| rushing yards | 3,990 | +0.09 [−0.02, +0.20] | −0.05 [−0.16, +0.04] | **+0.08** [+0.02, +0.14] | **+0.06** [+0.03, +0.11] |
| passing attempts | 1,050 | −0.01 [−0.08, +0.05] | −0.05 [−0.10, +0.00] | +0.01 [−0.01, +0.03] | +0.02 [−0.03, +0.08] |
| completions | 1,050 | −0.03 [−0.09, +0.03] | **−0.06** [−0.10, −0.03] | +0.01 [−0.00, +0.02] | +0.02 [−0.02, +0.07] |
| passing yards | 1,050 | **+1.07** [+0.26, +1.86] | −0.15 [−0.84, +0.51] | **+0.17** [+0.05, +0.29] | **+1.05** [+0.33, +1.86] |

**Reading.**

1. **(b) and (c), player opportunity and availability.**
   * Take away V4's availability features and **PURE is as accurate as V4 or more accurate on every
     statistic**. Column (1) is ≤ 0 on 8 of 9 statistics and significantly below 0 on 4 of them; carries are
     +0.005, with a CI spanning 0.
   * On counting statistics, the whole of PURE's deficit is V4's use of the injury report and roster status
     (column 2): 132% of the targets gap, 143% of receptions, 86% of carries, and 228% of snap share. Shares above
     100% mean PURE's better structure offsets part of it.
2. **(a) team environment.**
   * The market environment (column 3) adds nothing to snap, target, carry or attempt forecasts.
   * It helps only the **yardage** statistics, and almost entirely through efficiency. The market-environment
     efficiency components are: receiving yards +0.049 [+0.027, +0.072]; rushing yards +0.066 [+0.028, +0.104];
     passing yards efficiency +0.69 [+0.20, +1.23] and usage +0.20 [+0.07, +0.36].
   * That is 98% of the passing-yards gap, 48% of receiving yards and 69% of rushing yards. It enters through V4's
     catch-rate, yards-per-reception, yards-per-carry, completion and yards-per-completion models, which regress on
     `implied_total` / `spread_team` (`v4/model.py:435-465`).
   * At the **team level**, PURE's football-only volume is not worse than V4's market-informed volume:
     * pass attempts: MAE 6.114 against 6.136, Δ −0.022 [−0.090, +0.049];
     * rush attempts: 5.727 against 5.744, Δ −0.017 [−0.074, +0.040];
     * n = 1,088 team-games.
3. **(d) opponent adjustment is not a measurable source of the gap.** Details are in the opponent section below.

## Component split (PURE − V4_MEF_AS_IS, the market-free-by-features V4)

| statistic | gap | volume | snap | usage | efficiency |
|---|---|---|---|---|---|
| snap share | **+0.0018** | — | **+0.0018** [+0.0009, +0.0027] | — | — |
| targets | **+0.013** | +0.002 [−0.000, +0.005] | **+0.023** [+0.019, +0.027] | **−0.013** [−0.016, −0.009] | — |
| receptions | **+0.007** | +0.001 [−0.000, +0.003] | **+0.013** [+0.011, +0.016] | **−0.009** [−0.011, −0.006] | **+0.001** [+0.000, +0.002] |
| receiving yards | **+0.06** | **+0.05** [+0.03, +0.07] | **+0.13** [+0.10, +0.15] | **−0.12** [−0.15, −0.10] | +0.01 [−0.02, +0.03] |
| carries | **+0.048** | +0.002 [−0.007, +0.011] | **+0.050** [+0.033, +0.067] | −0.004 [−0.020, +0.013] | — |
| rushing yards | +0.03 | **+0.07** [+0.03, +0.11] | **+0.11** [+0.05, +0.18] | −0.07 [−0.15, +0.00] | **−0.09** [−0.14, −0.04] |
| completions | **−0.055** | −0.017 | — | −0.011 | **−0.027** [−0.049, −0.003] |
| passing yards | +0.02 | +0.14 | — | −0.19 | +0.08 |

* The deficit is in the **snap-share component**: who plays and how much. PURE's **usage**, its opportunities per
  on-field play, is significantly better than V4's on targets, receptions and receiving yards. PURE's
  **opponent-adjusted efficiency** is better on rushing yards and completions.
* The player-level volume component is positive for yardage even though team-level volume is level. Volume and
  usage are partial substitutes in a multiplicative attribution (PURE's count stack blends team volume with the
  player's raw EWM). Their sum is −0.07 for receiving yards and +0.00 for rushing yards, in PURE's favour or level, so read them
  together.
* By position group, the snap deficit is RB / WR / TE (+0.004 to +0.005 snap share). On QB snap share PURE is better
  (−0.024 [−0.031, −0.017]). WR targets and receiving yards carry most of the receiving gap (+0.021 and +0.16);
  RB carries carry the rushing gap (+0.073).
* By season, the availability term is as large in **2024** as in **2025**: targets +0.020 vs +0.015, receiving
  yards +0.106 vs +0.093, carries +0.038 vs +0.048. This matters because 2024's injury file is
  point-in-time-certified and 2025's is not (see "Implication" below). The advantage is not a 2025 vintage leak.

## (c) Availability strata (realised labels, diagnostic only)

PURE − V4_MEF_AS_IS, split by whether a realised availability event touches the row. A row counts as an event if
any of these holds:
* a same-group teammate with a recent share ≥ 0.10 played the team's previous game and is absent from this one;
* a same-group teammate returns after missing the previous game;
* the player himself returns after missing games;
* the player is listed Q/D on the final injury report;
* the player's realised snap share is below half his prior;
* the team's starting QB changed.

| statistic | rows with an event | gap inside them | rows without | gap inside them |
|---|---|---|---|---|
| targets | 3,554 | **+0.047** [+0.035, +0.058] | 8,005 | −0.003 [−0.008, +0.003] |
| receiving yards | 3,554 | **+0.23** [+0.13, +0.32] | 8,005 | −0.01 [−0.06, +0.04] |
| carries | 1,199 | **+0.150** [+0.091, +0.206] | 2,791 | +0.004 [−0.015, +0.022] |
| snap share | 3,658 | **+0.0053** [+0.0033, +0.0073] | 8,909 | +0.0004 [−0.0005, +0.0013] |

The whole gap sits in rows where availability changes. Where nothing changes, PURE equals V4. The largest single
contributors are these, with contributions to the pooled gap in `DECOMPOSITION_TABLES.md`:
* carries: teammate new absence (+0.028 of the +0.048) and returning teammates (+0.017);
* receiving: own reduced role (+0.0051 of the targets gap) and team QB change (+0.019 of receiving yards).

## (d) Opponent

* **Tercile slices.** PURE's yardage deficit concentrates against defences that allow the most, in rushing
  yards: +0.28 [+0.09, +0.49] against the top tercile of allowed yards per carry, versus −0.19 [−0.38, +0.01]
  against the stingiest tercile.
  * Mean bias by tercile, stingiest → most generous: PURE −1.09 / −0.09 / −0.05; V4_MEF +0.37 / +0.14 / −0.89.
  * PURE slightly over-adjusts against stingy run defences, and V4 under-adjusts against generous ones.
  * PURE's MAE deficit sits where its mean is unbiased (the generous tercile). That points to the shape of the
    distribution, i.e. the median, not to a missed opponent effect.
* **Residual opponent signal.** For each arm, a cross-season least-absolute-deviation correction of the residual
  is fitted on opponent features (fit 2024 → score 2025 and back). The result is MAE with the features minus MAE
  with a scale-only correction, so < 0 means signal was left. Three feature sets are tried:
  * positional allowed-to-group rates, prior-only;
  * the same rates over expected;
  * a **hindsight oracle**: the opponent's full-season leave-one-game-out allowed-to-group rates.

  None significantly reduces any arm's MAE on any statistic. For PURE, every CI includes 0 or lies above it, and the
  best case is targets −0.0009 [−0.0018, +0.0001]. The oracle gives receiving yards +0.04 [+0.01, +0.07] and
  rushing yards −0.00 [−0.05, +0.04]. Re-adding PURE's own opponent features worsens MAE, as expected for
  redundant inputs.
* **Conclusion.** The upside from better opponent estimation is below this design's resolution, even with
  hindsight. Opponent adjustment is **not** a measurable source of the PURE-V4 gap. PURE's existing adjustment is
  already the better of the two on rushing efficiency and completions (component table above).

## Each arm's own error (oracle split; the share of MAE removed by the realised component)

| statistic | arm | MAE | volume | snap | usage | efficiency |
|---|---|---|---|---|---|---|
| targets | PURE | 1.560 | 18% | 26% | 56% | — |
| targets | V4_MKT | 1.547 | 19% | 24% | 57% | — |
| receiving yards | PURE | 15.34 | 11% | 15% | 34% | 39% |
| receiving yards | V4_MKT | 15.22 | 11% | 15% | 35% | 39% |
| carries | PURE | 3.048 | 28% | 37% | 35% | — |
| rushing yards | PURE | 18.17 | 18% | 23% | 21% | 39% |
| passing attempts | PURE | 6.804 | 77% | — | 23% | — |
| passing yards | PURE | 59.62 | 43% | — | 15% | 42% |
| passing yards | V4_MKT | 58.55 | 43% | — | 15% | 41% |

Both arms' errors are dominated by the same irreducible per-game noise: usage and efficiency for receivers, team
volume for QBs. The arms differ by less than 1% of MAE. Opportunity and workload (volume, snap and usage together)
is 61% of receiving-yards error and all of the counting-statistic error.

## Implication for a sports-only challenger

* **Addressable.** The two big sports-only sources are:
  * **point-in-time availability**: the injury report, worth 0.004 snap share and 0.10 receiving yards;
  * a **football-only substitute for the market's scoring environment** in the *efficiency* models.

  Opponent adjustment shows no measurable upside.
* **Not addressable on this window.** A certified point-in-time injury source exists only for 2010–2024. 2025 is
  rejected: its only vintage post-dates the season (PR #137, `NFL_PIT_AVAILABILITY_CERTIFICATION.md`). V4's
  availability edge on 2025 therefore uses data that a pregame forecaster could not provably have had, and the
  2024 result shows the edge is real where the data are certified.
* **The challenger.** PURE_PLAYER_V1_2 (`PURE_PLAYER_V1_2_PREREGISTRATION.md`) tests the sports-only parts. It
  excludes the injury report, for the reason above.

## Limitations

* The decomposition is over MAE of the mean. Shapley values on |error| include interaction effects, which are
  split evenly between components.
* The volume and usage parts are not separately identified for PURE's stacked count model; read them together.
* The availability strata and the opponent oracle use realised information. They describe where the error is, not
  what a pregame model could know.
* V4_MEF_AS_IS is not market-free: its volume training sample is gated on a line existing, which removes 0 rows
  historically. It also reads injury and roster statuses that are not point-in-time for 2025.
