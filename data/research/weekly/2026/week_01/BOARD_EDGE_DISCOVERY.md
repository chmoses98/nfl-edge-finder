# BOARD EDGE DISCOVERY — 2026 week 1

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

_Inputs: board board-research-1.0.0, miner board-miner-1.0.0, script autopsy script-autopsy-1.0.0, weeks [1]; board rows 67,485_

## 1. Coverage — what was and was not analysed

| stage | contracts |
|---|---|
| discovered | 13,503 |
| mapped_to_game | 13,503 |
| captured_pregame | 13,197 |
| settled_any_source | 13,197 |
| football_settled | 10,349 |
| price_at_primary_horizon | 10,349 |
| executable_quote | 10,349 |
| fee_known | 10,333 |
| analyzed_primary | 10,333 |

Exclusions (every contract that left the funnel, by reason):

- 472 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_TEAM:FULL:first_td_team]
- 415 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_SCORER:FULL:first_td]
- 300 — captured_pregame: never quoted before kickoff
- 285 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [RACE_TO_N:FULL:race]
- 238 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_yards]
- 181 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_reception]
- 180 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:fantasy_points]
- 175 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:receiving_yards]
- 160 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_sacks]
- 128 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:field_goals]
- 97 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_touchdowns]
- 96 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TOTAL_TD:FULL:total_touchdowns]
- 83 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_rush]
- 78 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:rushing_yards]
- 37 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:touchdowns]
- 34 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:touchdowns]
- 32 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:fantasy_points]
- 22 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receiving_yards]
- 20 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rushing_yards]
- 17 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receptions]
- 16 — fee_known: fee unknown
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:defensive_st_td]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:btts]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:overtime]
- 15 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:safety]
- 11 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:attempts]
- 11 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:completions]
- 7 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:passing_yards]
- 6 — captured_pregame: discovered, never in a pregame capture row (series outside the capture tiers, or listed only after kickoff)
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:interceptions]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:passing_tds]

Discovery universe: GAME_NOT_IN_REG_SCHEDULE (preseason / prior season) 10,294 · GAME_OTHER_WEEKS 6,432 · GAME_TARGET_WEEKS 38,919 · NON_GAME (season / futures / awards / leaders) 16,108

By week × family (primary horizon):

| week | family | discovered | captured | football-settled | analysed |
|---|---|---|---|---|---|
| 1 | BOTH_TEAMS_SCORE | 64 | 64 | 64 | 64 |
| 1 | BOTH_TEAMS_SCORE_N | 64 | 64 | 64 | 64 |
| 1 | FIRST_TD_SCORER | 417 | 415 | 0 | 0 |
| 1 | FIRST_TD_TEAM | 473 | 472 | 0 | 0 |
| 1 | GAME_EVENT | 63 | 63 | 0 | 0 |
| 1 | GAME_PLAYER_LEADER | 4 | 0 | 0 | 0 |
| 1 | GAME_WINNER | 32 | 32 | 32 | 32 |
| 1 | HALF_FULL_RESULT | 144 | 144 | 144 | 144 |
| 1 | PERIOD_WINNER | 288 | 288 | 288 | 288 |
| 1 | PLAYER_STAT | 6,686 | 6,667 | 5,898 | 5,885 |
| 1 | RACE_TO_N | 285 | 285 | 0 | 0 |
| 1 | SEASON_LEADER | 329 | 253 | 0 | 0 |
| 1 | SPREAD | 1,740 | 1,587 | 1,587 | 1,587 |
| 1 | TEAM_STAT | 495 | 495 | 0 | 0 |
| 1 | TEAM_TOTAL | 792 | 782 | 782 | 779 |
| 1 | TOTAL | 1,408 | 1,378 | 1,378 | 1,378 |
| 1 | TOTAL_TD | 107 | 96 | 0 | 0 |
| 1 | WIN_MARGIN_BUCKET | 112 | 112 | 112 | 112 |

## 2. How to read the cells

Unit = one contract SIDE bought at its executable ask. **mid bias** = event rate − the side's mid (is the market's fair price wrong?). **return** = payout − ask − fee per contract (is it exploitable after costs?). Intervals are game-clustered bootstrap (B=2000); rare-outcome cells also get a binomial floor. Cells with < 20 games, < 2 weeks or < 40 sides are DESCRIPTIVE_ONLY. Multiplicity: Benjamini–Hochberg q ≤ 0.2 across all 0 tested cells (≈0.0 would exclude zero by chance alone).

Status counts at latest pregame: DESCRIPTIVE_ONLY 1570.

## 3. Price bands

### Five full-game families, YES side, binned by QUOTED MID (the owner's Weeks 1–3 framing)

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| YES | 00-10c | 198 | 16 | 0.061 | 0.101 | +4.0c [-2.5, +12.8]c | +2.3c [-4.2, +11.3]c | W1:+2.8 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 187 | 16 | 0.146 | 0.225 | +7.8c [-2.5, +19.0]c | +5.9c [-4.4, +17.0]c | W1:+6.8 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 141 | 16 | 0.245 | 0.312 | +6.7c [-3.6, +17.2]c | +4.7c [-5.6, +15.2]c | W1:+6.0 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 141 | 16 | 0.354 | 0.440 | +8.6c [-1.6, +18.2]c | +5.8c [-4.3, +15.3]c | W1:+7.4 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 126 | 16 | 0.450 | 0.460 | +1.0c [-14.3, +16.1]c | -1.6c [-16.9, +13.4]c | W1:+0.1 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 127 | 16 | 0.546 | 0.638 | +9.2c [-7.6, +24.5]c | +6.5c [-9.9, +21.9]c | W1:+8.2 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 82 | 16 | 0.653 | 0.659 | +0.6c [-14.3, +14.7]c | -3.0c [-17.6, +10.6]c | W1:-1.5 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 51 | 16 | 0.754 | 0.725 | -2.9c [-21.1, +13.8]c | -5.0c [-23.2, +11.7]c | W1:-3.7 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 72 | 16 | 0.850 | 0.847 | -0.3c [-14.1, +11.2]c | -2.1c [-15.8, +9.2]c | W1:-1.3 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 112 | 16 | 0.946 | 0.946 | +0.0c [-6.7, +5.4]c | -1.2c [-7.9, +4.1]c | W1:-0.9 | DESCRIPTIVE_ONLY |

### Whole board, binned by the ASK actually paid

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| NO | 00-10c | 165 | 16 | 0.057 | 0.055 | +0.7c [-3.6, +5.9]c | -0.6c [-5.0, +4.6]c | W1:-0.2 | DESCRIPTIVE_ONLY |
| NO | 10-20c | 333 | 16 | 0.152 | 0.117 | -1.4c [-5.6, +3.4]c | -4.4c [-8.6, +0.4]c | W1:-3.5 | DESCRIPTIVE_ONLY |
| NO | 20-30c | 486 | 16 | 0.246 | 0.179 | -4.1c [-9.4, +1.9]c | -8.0c [-13.3, -1.9]c | W1:-6.7 | DESCRIPTIVE_ONLY |
| NO | 30-40c | 555 | 16 | 0.345 | 0.328 | +0.6c [-5.0, +6.8]c | -3.3c [-9.0, +2.7]c | W1:-1.7 | DESCRIPTIVE_ONLY |
| NO | 40-50c | 717 | 16 | 0.447 | 0.417 | -1.3c [-8.2, +6.0]c | -4.7c [-11.6, +2.7]c | W1:-3.0 | DESCRIPTIVE_ONLY |
| NO | 50-60c | 947 | 16 | 0.543 | 0.504 | -2.7c [-10.6, +5.1]c | -5.7c [-13.6, +2.0]c | W1:-4.0 | DESCRIPTIVE_ONLY |
| NO | 60-70c | 989 | 16 | 0.645 | 0.607 | -1.7c [-6.4, +2.7]c | -5.4c [-10.2, -1.0]c | W1:-3.8 | DESCRIPTIVE_ONLY |
| NO | 70-80c | 1,218 | 16 | 0.752 | 0.660 | -4.3c [-9.2, +0.6]c | -10.5c [-15.7, -4.9]c | W1:-9.2 | DESCRIPTIVE_ONLY |
| NO | 80-90c | 1,612 | 16 | 0.851 | 0.787 | -3.2c [-7.7, +0.6]c | -7.3c [-12.0, -3.5]c | W1:-6.4 | DESCRIPTIVE_ONLY |
| NO | 90-100c | 2,824 | 16 | 0.953 | 0.908 | -1.8c [-6.1, +1.5]c | -4.9c [-9.3, -1.6]c | W1:-4.6 | DESCRIPTIVE_ONLY |
| YES | 00-10c | 2,105 | 16 | 0.056 | 0.057 | +1.3c [-0.9, +4.6]c | -0.2c [-2.5, +3.1]c | W1:+0.1 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 1,820 | 16 | 0.143 | 0.143 | +2.1c [-1.5, +6.5]c | -0.9c [-4.4, +3.5]c | W1:+0.0 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 1,364 | 16 | 0.243 | 0.224 | +0.9c [-2.7, +5.0]c | -3.2c [-6.8, +0.8]c | W1:-1.9 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 1,105 | 16 | 0.344 | 0.344 | +3.0c [-1.3, +7.5]c | -1.6c [-5.8, +2.9]c | W1:-0.0 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 1,078 | 16 | 0.443 | 0.435 | +1.6c [-4.8, +8.3]c | -2.5c [-8.8, +4.0]c | W1:-0.8 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 804 | 16 | 0.540 | 0.546 | +2.3c [-4.7, +9.3]c | -1.1c [-8.1, +5.7]c | W1:+0.6 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 593 | 16 | 0.645 | 0.609 | +0.5c [-9.0, +9.0]c | -5.2c [-14.4, +3.0]c | W1:-3.6 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 564 | 16 | 0.743 | 0.730 | +4.6c [-2.2, +11.0]c | -2.6c [-8.4, +3.1]c | W1:-1.3 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 532 | 16 | 0.843 | 0.846 | +7.3c [+0.8, +12.9]c | -0.7c [-6.4, +4.2]c | W1:+0.3 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 358 | 16 | 0.950 | 0.922 | +2.3c [-2.1, +6.3]c | -3.1c [-7.7, +1.0]c | W1:-2.8 | DESCRIPTIVE_ONLY |

## 4. Market families

| family | contract-sides | mean return at the ask |
|---|---|---|
| PLAYER_STAT | 11,430 | -4.2c |
| SPREAD | 3,174 | -2.9c |
| TOTAL | 2,742 | -3.6c |
| TEAM_TOTAL | 1,504 | -3.8c |
| PERIOD_WINNER | 576 | -2.5c |
| HALF_FULL_RESULT | 224 | -3.9c |
| WIN_MARGIN_BUCKET | 207 | -5.0c |
| BOTH_TEAMS_SCORE | 128 | -3.6c |
| BOTH_TEAMS_SCORE_N | 120 | -8.3c |
| GAME_WINNER | 64 | -2.1c |

## 5. Conditional patterns that survived every safeguard (CANDIDATE) — discovery only

0 CANDIDATE cells at latest pregame. Negative returns dominate: most survivors are COST (half-spread + fee) or favourite–longshot effects, not hidden value. Mid bias says which are mispricing.

| cell | sides | games | weeks | price | event | mid bias (CI) | return (CI) | q | by week |
|---|---|---|---|---|---|---|---|---|---|

## 6. Patterns that did NOT survive (rejected in discovery)

- UNSTABLE (a week or a held-out week flips the sign): 0 cells. Largest:
- NO_SIGNAL (interval includes zero): 0 cells. NOT_SIGNIFICANT_AFTER_MULTIPLICITY: 0 cells.

## 7. Ladders (one ladder = one thesis)

1,159 ladders with ≥ 3 live rungs at latest pregame. a ladder's realised best rung is one draw of one outcome; read the by-family shares across many ladders, never one ladder's winner.

| family | ladders | best realised = main rung | best CLV = main rung | incoherent | a rung ≥ 2c under the ladder's own fair curve |
|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 16 | 6.2% | 31.2% | 0 | 0 |
| PLAYER_STAT | 743 | 17.8% | 29.3% | 107 | 0 |
| SPREAD | 224 | 6.2% | 37.5% | 20 | 0 |
| TEAM_TOTAL | 64 | 7.8% | 6.2% | 44 | 14 |
| TOTAL | 112 | 12.5% | 9.8% | 35 | 0 |

## 8. Preregistered tests (discovery reading vs prospective reading)

| id | hypothesis | metric | discovery (W1–3) | prospective weeks | prospective value (family CI) | games | suggested |
|---|---|---|---|---|---|---|---|
| H-20261001-B01 | Full-game longshot YES underpriced at the mid | MID_BIAS (+) | 0.0372 [-0.0, +0.1] | — | — — | — | — |
| H-20261001-B02 | Full-game YES at 60-70c overpriced at the mid | MID_BIAS (−) | -0.0635 [-0.2, +0.0] | — | — — | — | — |
| H-20261001-B03 | Sides priced 90c+ lose after fees | RETURN_AT_ASK (−) | -0.0219 [-0.0, -0.0] | — | — — | — | — |
| H-20261001-B04 | Modest DATA_ONLY disagreement predicts movement toward it | MOVE_TOWARD_MODEL (+) | 0.0823 [+0.0, +0.1] | — | — — | — | — |
| H-20261001-B05 | Adjacent yardage rungs beat the main rung after fees | PAIRED_RUNG (+) | 0.0110 [-0.0, +0.0] | — | — — | — | — |
| H-20261001-B06 | Team total beats spread as the expression of an offensive thesis | PAIRED_EXPRESSION (+) | 0.1046 [-0.1, +0.3] | — | — — | — | — |
| H-20261001-B07 | Uncertain roles are priced worse than certain roles | EXCESS_BRIER_GAP (+) | -0.0046 [-0.0, +0.0] | — | — — | — | — |
| H-20261001-B08 | Player-prop NO at 80c+ loses after fees | RETURN_AT_ASK (−) | -0.0304 [-0.0, -0.0] | — | — — | — | — |
| H-20261001-B09 | Player-prop YES longshots lose after fees | RETURN_AT_ASK (−) | -0.0142 [-0.0, -0.0] | — | — — | — | — |
| H-20261001-B10 | Chasing a pregame move loses | RETURN_AT_ASK (−) | -0.1009 [-0.1, -0.1] | — | — — | — | — |
| H-20261001-B11 | A large incumbent player-model OVER view marks an underpriced YES | MID_BIAS (+) | 0.0784 [+0.0, +0.1] | — | — — | — | — |

_Suggested statuses are suggestions; only the owner transitions the registry. Weeks 1–3 are never evidence for these hypotheses._

## 9. Patterns worth testing next (not registered)


