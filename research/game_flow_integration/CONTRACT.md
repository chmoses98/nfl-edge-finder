# `game_flow` block, version `game-flow-1.0.0` (DESIGN; nothing here is implemented in production)

Additive key inside `packet.games[].game_script_inputs`, forwarded by `scripts/research_export.py` into `event_research.extensions.game_script_inputs`. Absent, `UNAVAILABLE`, `STALE` or `SUPPRESSED` blocks must render as nothing, never as a default. Reference implementation and a worked example: `reference_impl.py`, `example_payload.json`.

## Common fields (every block)
| field | meaning |
|---|---|
| `version` | `game-flow-1.0.0`; `game_script_inputs.script_source` is unchanged (`sim-script-1.1.0`) |
| `state` | `OK` / `UNAVAILABLE` (+`reason`) / `STALE` / `SUPPRESSED` |
| `orientation` | all margins are home minus away; `*_home` / `*_away` are that team's own probability; `market_centre.favorite` is `HOME`, `AWAY` or null (pick'em) |
| `market_centre` | `{spread_home, total, source, observed_at, minutes_to_kickoff, favorite}`; `source` is `kalshi_implied_interpolated` or `consensus_line` (vintage undocumented) |
| `evidence_class` | always `MARKET_DERIVED_CONDITIONAL`; `independent_of_market: false`; `ranking_eligible: false` |
| `training` | `{seasons, games, effective_sample}`: trajectory seasons 2003..(season-1) REG, ~5,900 games; effective sample after kernel and tilt |
| `gates` | per-field display gate from `display_gates_v1.json` (the UI reads it; it hard-codes no evidence) |
| `explanation_policy` | text: "Derived from the same market line as the final-score projection. It describes what that line implies about the first half; it is not additional evidence for any side." |

## A. Halftime
| field | meaning / units | source and model | calibration | sample | availability | suppression |
|---|---|---|---|---|---|---|
| `halftime.margin_home.{mean,p05,p25,p50,p75,p95}` | home minus away points after the last first-half play; points | G0c (historical trajectories matched on closing spread and total, tilted to the simulation's mean margin/total), `game-flow-1.0.0` | DISPLAY: PIT p 0.94 / 0.29; CRPS -5.3% / -4.2% vs no-market | holdout 759 games (2010-12); 3,369 (2013-25; 1,351 in 2021-25 are SIFT-exposed) | needs centre + sim means | see below |
| `halftime.total.{mean,p05..p95}` | home plus away first-half points | same | DISPLAY: PIT p 0.45 / 0.39; CRPS -2.1% / -2.3% | same | same | same |
| `halftime.p_lead_7plus_home`, `p_lead_7plus_away` | P(that team leads by 7+ at halftime); probability 0..1, own side | same | DISPLAY_WITH_CAUTION: ECE 0.045 (holdout) / 0.020 / away 0.018; Brier -5% to -7% vs no-market | same | same | same |

## B. Flow
| field | meaning | calibration | gate |
|---|---|---|---|
| `flow.p_lead_14plus_any_time` | P(either team leads by 14+ at any play, incl. OT) | ECE 0.021 / 0.008; Brier only -1.0% to -1.6% vs no-market | DISPLAY_WITH_CAUTION (mostly base rate 0.61) |
| `flow.p_within_8_entering_q4` | P(abs margin <= 8 after the last Q3 play) | ECE 0.016 / 0.011; Brier -0.2% to -0.8% | RESEARCH_ONLY (near coin flip; forecast range 0.32-0.60) |
| comeback, Q4 lead change, scoring drought | not emitted | no information beyond base rate / miscalibrated | SUPPRESS |

## C. Offensive opportunity: reuse, do not add a model
The incumbent already publishes `team_volume[TEAM]` (`plays`, `dropbacks`, `pass_att`, `designed_rush`, `scrambles`, `pass_rate`, each `{mean, range_50, range_90}`, from the `fit_game_env` ridge conditioned on each simulated row's margin and total). Planned fields map one to one: `expected_plays = team_volume.plays.mean`, `expected_dropbacks = .dropbacks.mean`, `expected_rush_attempts = .designed_rush.mean` (designed runs; scrambles are separate), `expected_pass_rate = .pass_rate.mean` (dropbacks / plays). `rush_att` (all carries) is computed by the simulator but not forwarded by `script_block.py`; forwarding it is the only upstream change. **`expected_drives`: UNAVAILABLE and SUPPRESSED** (`not_simulated` lists "drive counts"). Units: counts per team per game; pass rate is a share of plays; orientation by team abbreviation, as today.
Evidence for reuse (like-for-like, 2,702 team-games 2021-25 REG): incumbent MAE plays 6.480 vs market-only baseline 6.542 (-0.96%), dropbacks 6.407 vs 6.607 (-3.02%); the research tendency model (T1) was -1.63% / -3.47% against the same baseline, i.e. about the incumbent's level. Gate: DISPLAY_WITH_CAUTION; ranges are the simulator's descriptive ranges, not separately interval-calibrated.

## Suppression and downgrade conditions
Block `UNAVAILABLE` when: no centre; simulation script absent or `coherence_ok` false; kickoff has passed. `STALE` when `market_centre.observed_at` is older than 180 minutes. Downgrade one level when `training.effective_sample < 150` (27 of 1,351 games in 2021-25, all |spread| >= 14 or extreme totals); `SUPPRESSED` below 60. `consensus_line` source caps every field at DISPLAY_WITH_CAUTION. Downgrade when |P(home win) implied by G0c - simulation's `p_home_win`| > 0.10 (observed p95 0.067, max 0.122); suppress above 0.15. The implied-final fields are diagnostics and are never published for display.
