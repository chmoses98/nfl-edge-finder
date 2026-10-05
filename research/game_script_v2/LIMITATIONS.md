# Limitations and point-in-time caveats

Everything here is RESEARCH_ONLY. The list is ordered by how much it could mislead a reader.

## 1. The game script is market-centred, not a football opinion

Every simulated (margin, total) is the market centre plus a historical residual. A 62% favourite-control script mass
is the market's distribution split into cells; it is not a 62% football edge, and GAME SCRIPT V2 carries
`MARKET_CENTRED_GAME` on every artifact. Script robustness, the major-script floor and thesis dependency describe how
a contract's probability is distributed over plausible worlds and which contracts fail together. For a calibrated
simulation they carry no additional information about whether the contract cashes beyond P(cash) itself -- their value
is exposure and duplication, not edge. Nothing in this study tested whether robustness predicts outcomes, and no
staking use is supported.

## 2. The incumbent's margin shape misses the key numbers (post-hoc finding)

`SCRIPT_CALIBRATION_5Y.md` (POST-HOC section): the residual bank puts about half the realized mass on a final margin of
exactly 3 and too much in 9-16, consistently in every season. This is the incumbent game-environment shape
(`pricing/game_env.ResidualBank`), shared by the incumbent's game-market pricing. It explains the one-score
under-forecast and part of the NEEDS_MORE_WORK verdict. It was not preregistered, is reported as descriptive, and was
not "fixed" here: a key-number-aware margin model must be preregistered and earn its way like any other change.

## 3. Final-state scripts only

The simulator draws final margin and total, not a scoring sequence. Lead changes, time leading, early blowouts and late
comebacks are `not_simulated`. The preregistered score-path arm (P1) is reported in `SCRIPT_CALIBRATION_5Y.md`; V2 does
not depend on it. "FAVORITE_CONTROL" in V2 means "won by more than one score"; the realized-script autopsy's label of
the same name also requires leading at half and after Q3 -- they are never scored against each other.

## 4. The historical information set is T-0 with game-day inactives

Historical eligibility uses the FINAL weekly roster file, whose `INA` status is the game-day inactive list (public about
90 minutes before kickoff). About 1,100 skill-position rows per season are `INA`, roughly 670 of them with no injury
designation at all (healthy scratches and late decisions). That is consistent with the closing-line centre the backtest
uses (also a T-0 quantity) but is MORE than a T-24h or morning-of projection knows. Two consequences:

* historical opportunity accuracy is optimistic relative to an earlier-horizon prospective run;
* QUESTIONABLE players left in the historical eligible set are, by construction, players who were active, yet the
  simulator still applies the questionable play-probability discount -- so their carries and targets are biased low in
  the backtest (`VALIDATION_5Y.md`). Prospectively the discount is appropriate; historically it double-counts.

Historical injury designations are the final pregame report (the only historical artifact). Prospective runs read the
content-addressed vintage at the cutoff (`prospective.injury_vintage`, `tests/test_sim_injury_vintage.py`); Sleeper
may only tighten a designation.

## 5. Depth charts are weekly and stale before 2025

2016-2024 depth charts are weekly files. When a team's starting quarterback changed, the weekly chart's QB1 named the
PREVIOUS starter 67-77% of the time and the new one 19-27% (2019-2024); the 2025 daily charts at the game-day cutoff
named the new one 46% of the time. No leakage signal, but starter identification is weaker before 2025, and
2025 results are not directly comparable to 2021-2024 on anything starter-dependent. A usage-first QB rule was
designed on 2018-2020 and lost to the depth chart there, so it was not run (`PREREGISTRATION.md`, stage 2).

## 6. Data vintages move

nflverse rebuilds releases in place. Today's `snap_counts_2020` carries 616 compound position labels (e.g. `FB/D`)
that the file used for the committed 2023-2025 run evidently did not; together with a latent `fillna(0)` →
`groupby.first` aggregation in `training.assemble`, that flips the sign of the outside-the-eligible-set share
(`reproduction_2023_2025.json`). The frozen baseline was run on today's vintage unchanged, so it carries that negative
share; R1 is the registered repair (`OPPONENT_ADJUSTMENT_ABLATION.md`). Player metrics moved by at most 0.32% (MAE) and
0.62% (CRPS) relative against the committed run; team volume, points and touchdowns reproduced exactly.

## 7. Coverage on integer outcomes

The incumbent's 50% / 90% coverage counts an outcome on the interval endpoint as covered, which inflates coverage for
small counts (targets and receptions show 50% coverage near 0.73-0.76). The randomized-PIT χ² in `BASELINE_5Y.md` is the
honest uniformity check; the promotion rule's calibration criterion was registered on the endpoint-inclusive coverage
and was not changed afterwards.

## 8. Unequal training histories

The 2021 bundle trains on 2018-2020 (three seasons, including the 2020 no-crowd season); 2025 trains on seven. Season
differences mix model quality, training size and environment. 2016-2017 serve only to warm the EWMAs; pbp before
2016 was not used, so 2018's opponent-adjusted window has two seasons, not three.

## 9. Weather

No historical point-in-time forecast exists (Open-Meteo vintages begin 2026-09-04). Observed weather appears only in
NON_PIT descriptive tables and cannot fit or promote a feature. The 2026 prospective hypotheses W1/W2 had two qualifying
games when this study was written; nothing is read out. Retractable roofs are excluded from the outdoor tables because
open/closed is decided on game day.

## 10. Multiple comparisons and what "retrospective challenge" means

Six projection arms and ten marginal events were evaluated. The promotion rule demands consistency across seasons,
a pooled game-clustered interval, a materiality bar and breadth, which limits but does not eliminate chance passes.
2021-2022 were never scored by this layer before, but the code, features and every design choice existed when they
were run, so they are a challenge set, not out-of-sample evidence in the prospective sense. Only 2026 onward is.

## 11. Season-level dependence

Bootstraps resample games. Games within a week share league-wide conditions (officiating emphasis, weather fronts,
injuries spreading through a roster), so game-level intervals are somewhat optimistic; season-by-season tables are
always shown beside pooled numbers for that reason.
