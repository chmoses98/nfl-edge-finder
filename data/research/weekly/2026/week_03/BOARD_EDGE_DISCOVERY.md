# BOARD EDGE DISCOVERY — 2026 week 3

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

_Inputs: board board-research-1.0.0, miner board-miner-1.0.0, script autopsy script-autopsy-1.0.0, weeks [3]; board rows 62,640_

## 1. Coverage — what was and was not analysed

| stage | contracts |
|---|---|
| discovered | 12,630 |
| mapped_to_game | 12,630 |
| captured_pregame | 11,878 |
| settled_any_source | 11,878 |
| football_settled | 9,686 |
| price_at_primary_horizon | 9,686 |
| executable_quote | 9,686 |
| fee_known | 9,686 |
| analyzed_primary | 9,657 |

Exclusions (every contract that left the funnel, by reason):

- 650 — captured_pregame: never quoted before kickoff
- 481 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_TEAM:FULL:first_td_team]
- 423 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_SCORER:FULL:first_td]
- 240 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [RACE_TO_N:FULL:race]
- 160 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_sacks]
- 160 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_yards]
- 158 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:fantasy_points]
- 151 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_reception]
- 128 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:field_goals]
- 102 — captured_pregame: discovered, never in a pregame capture row (series outside the capture tiers, or listed only after kickoff)
- 68 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_rush]
- 34 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:touchdowns]
- 32 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:fantasy_points]
- 29 — analyzed_primary: football settlement contradicted by the exchange's terminal result (flagged, never resolved)
- 24 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receiving_yards]
- 22 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:touchdowns]
- 19 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receptions]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:defensive_st_td]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:btts]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:overtime]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:safety]
- 13 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rushing_yards]
- 6 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_touchdowns]
- 6 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TOTAL_TD:FULL:total_touchdowns]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rush_rec_yards]

Discovery universe: GAME_NOT_IN_REG_SCHEDULE (preseason / prior season) 10,294 · GAME_OTHER_WEEKS 6,432 · GAME_TARGET_WEEKS 38,919 · NON_GAME (season / futures / awards / leaders) 16,108

By week × family (primary horizon):

| week | family | discovered | captured | football-settled | analysed |
|---|---|---|---|---|---|
| 3 | BOTH_TEAMS_SCORE | 64 | 64 | 64 | 64 |
| 3 | BOTH_TEAMS_SCORE_N | 64 | 64 | 64 | 64 |
| 3 | FIRST_TD_SCORER | 423 | 423 | 0 | 0 |
| 3 | FIRST_TD_TEAM | 481 | 481 | 0 | 0 |
| 3 | GAME_EVENT | 64 | 64 | 0 | 0 |
| 3 | GAME_PLAYER_LEADER | 224 | 187 | 187 | 158 |
| 3 | GAME_WINNER | 32 | 32 | 32 | 32 |
| 3 | HALF_FULL_RESULT | 144 | 144 | 144 | 144 |
| 3 | PERIOD_WINNER | 288 | 288 | 288 | 288 |
| 3 | PLAYER_STAT | 6,154 | 5,690 | 5,038 | 5,038 |
| 3 | RACE_TO_N | 240 | 240 | 0 | 0 |
| 3 | SEASON_FANTASY | 101 | 0 | 0 | 0 |
| 3 | SPREAD | 1,721 | 1,588 | 1,588 | 1,588 |
| 3 | TEAM_STAT | 326 | 326 | 0 | 0 |
| 3 | TEAM_TOTAL | 793 | 793 | 793 | 793 |
| 3 | TOTAL | 1,393 | 1,376 | 1,376 | 1,376 |
| 3 | TOTAL_TD | 6 | 6 | 0 | 0 |
| 3 | WIN_MARGIN_BUCKET | 112 | 112 | 112 | 112 |

## 2. How to read the cells

Unit = one contract SIDE bought at its executable ask. **mid bias** = event rate − the side's mid (is the market's fair price wrong?). **return** = payout − ask − fee per contract (is it exploitable after costs?). Intervals are game-clustered bootstrap (B=2000); rare-outcome cells also get a binomial floor. Cells with < 20 games, < 2 weeks or < 40 sides are DESCRIPTIVE_ONLY. Multiplicity: Benjamini–Hochberg q ≤ 0.2 across all 0 tested cells (≈0.0 would exclude zero by chance alone).

Status counts at latest pregame: DESCRIPTIVE_ONLY 1627.

## 3. Price bands

### Five full-game families, YES side, binned by QUOTED MID (the owner's Weeks 1–3 framing)

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| YES | 00-10c | 216 | 16 | 0.055 | 0.060 | +0.5c [-4.5, +6.1]c | -0.7c [-5.7, +4.9]c | W3:-0.3 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 185 | 16 | 0.146 | 0.151 | +0.6c [-8.7, +8.9]c | -0.9c [-10.2, +7.4]c | W3:-0.0 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 142 | 16 | 0.246 | 0.261 | +1.5c [-10.0, +12.7]c | -0.4c [-11.9, +10.8]c | W3:+0.9 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 139 | 16 | 0.349 | 0.331 | -1.8c [-13.6, +11.3]c | -4.0c [-15.8, +9.1]c | W3:-2.4 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 137 | 16 | 0.451 | 0.467 | +1.6c [-10.5, +13.2]c | -1.0c [-12.9, +10.5]c | W3:+0.7 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 106 | 16 | 0.546 | 0.575 | +3.0c [-10.8, +16.6]c | +0.5c [-13.4, +14.3]c | W3:+2.2 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 82 | 16 | 0.643 | 0.598 | -4.5c [-20.1, +11.0]c | -7.1c [-22.4, +8.1]c | W3:-5.5 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 68 | 16 | 0.752 | 0.809 | +5.7c [-8.9, +17.0]c | +3.8c [-10.8, +15.1]c | W3:+5.1 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 66 | 16 | 0.855 | 0.924 | +6.9c [-1.7, +13.1]c | +5.5c [-3.1, +11.7]c | W3:+6.3 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 104 | 16 | 0.950 | 0.962 | +1.2c [-3.4, +4.7]c | +0.2c [-21.0, +3.8]c | W3:+0.5 | DESCRIPTIVE_ONLY |

### Whole board, binned by the ASK actually paid

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| NO | 00-10c | 212 | 16 | 0.056 | 0.024 | -2.4c [-4.3, -0.1]c | -3.6c [-5.4, -1.3]c | W3:-3.2 | DESCRIPTIVE_ONLY |
| NO | 10-20c | 381 | 16 | 0.149 | 0.118 | -2.1c [-6.3, +2.7]c | -4.0c [-8.3, +0.8]c | W3:-3.1 | DESCRIPTIVE_ONLY |
| NO | 20-30c | 465 | 16 | 0.246 | 0.183 | -5.1c [-9.8, -0.3]c | -7.6c [-12.6, -2.6]c | W3:-6.3 | DESCRIPTIVE_ONLY |
| NO | 30-40c | 491 | 16 | 0.347 | 0.310 | -2.8c [-9.2, +4.1]c | -5.3c [-11.8, +1.7]c | W3:-3.7 | DESCRIPTIVE_ONLY |
| NO | 40-50c | 588 | 16 | 0.449 | 0.440 | -0.1c [-5.5, +5.6]c | -2.6c [-8.1, +3.2]c | W3:-0.9 | DESCRIPTIVE_ONLY |
| NO | 50-60c | 908 | 16 | 0.544 | 0.531 | -0.6c [-6.9, +5.9]c | -3.1c [-9.5, +3.5]c | W3:-1.4 | DESCRIPTIVE_ONLY |
| NO | 60-70c | 887 | 16 | 0.645 | 0.630 | -0.6c [-5.4, +4.0]c | -3.1c [-7.8, +1.4]c | W3:-1.5 | DESCRIPTIVE_ONLY |
| NO | 70-80c | 1,110 | 16 | 0.749 | 0.735 | -0.4c [-4.5, +3.5]c | -2.7c [-6.8, +1.3]c | W3:-1.4 | DESCRIPTIVE_ONLY |
| NO | 80-90c | 1,554 | 16 | 0.849 | 0.828 | -1.1c [-5.4, +3.2]c | -3.0c [-7.2, +1.3]c | W3:-2.1 | DESCRIPTIVE_ONLY |
| NO | 90-100c | 2,630 | 16 | 0.949 | 0.941 | +0.3c [-1.3, +2.0]c | -1.2c [-2.8, +0.5]c | W3:-0.8 | DESCRIPTIVE_ONLY |
| YES | 00-10c | 2,352 | 16 | 0.054 | 0.040 | -0.4c [-1.5, +0.7]c | -1.8c [-2.9, -0.6]c | W3:-1.4 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 1,845 | 16 | 0.140 | 0.135 | +0.6c [-3.0, +4.3]c | -1.4c [-5.0, +2.4]c | W3:-0.5 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 1,235 | 16 | 0.242 | 0.237 | +0.5c [-4.2, +5.5]c | -1.8c [-6.5, +3.2]c | W3:-0.5 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 916 | 16 | 0.344 | 0.347 | +1.4c [-2.8, +5.6]c | -1.3c [-5.5, +2.8]c | W3:+0.3 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 931 | 16 | 0.446 | 0.425 | -1.1c [-6.2, +4.2]c | -3.8c [-8.8, +1.5]c | W3:-2.0 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 691 | 16 | 0.539 | 0.531 | -0.0c [-6.2, +5.8]c | -2.5c [-8.7, +3.3]c | W3:-0.8 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 494 | 16 | 0.645 | 0.662 | +2.7c [-3.4, +8.5]c | +0.1c [-5.9, +5.8]c | W3:+1.7 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 457 | 16 | 0.747 | 0.770 | +3.3c [-2.9, +9.5]c | +1.0c [-5.1, +7.1]c | W3:+2.4 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 412 | 16 | 0.844 | 0.879 | +4.6c [+0.5, +8.7]c | +2.5c [-1.3, +6.3]c | W3:+3.4 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 315 | 16 | 0.948 | 0.946 | +2.4c [-0.3, +5.0]c | -0.5c [-4.9, +3.1]c | W3:-0.2 | DESCRIPTIVE_ONLY |

## 4. Market families

| family | contract-sides | mean return at the ask |
|---|---|---|
| PLAYER_STAT | 9,865 | -1.8c |
| SPREAD | 3,176 | -2.3c |
| TOTAL | 2,746 | -2.3c |
| TEAM_TOTAL | 1,550 | -2.1c |
| PERIOD_WINNER | 576 | -2.1c |
| HALF_FULL_RESULT | 233 | -1.4c |
| GAME_PLAYER_LEADER | 212 | -10.3c |
| WIN_MARGIN_BUCKET | 204 | -2.3c |
| BOTH_TEAMS_SCORE | 128 | -3.0c |
| BOTH_TEAMS_SCORE_N | 120 | -4.3c |
| GAME_WINNER | 64 | -2.0c |

## 5. Conditional patterns that survived every safeguard (CANDIDATE) — discovery only

0 CANDIDATE cells at latest pregame. Negative returns dominate: most survivors are COST (half-spread + fee) or favourite–longshot effects, not hidden value. Mid bias says which are mispricing.

| cell | sides | games | weeks | price | event | mid bias (CI) | return (CI) | q | by week |
|---|---|---|---|---|---|---|---|---|---|

## 6. Patterns that did NOT survive (rejected in discovery)

- UNSTABLE (a week or a held-out week flips the sign): 0 cells. Largest:
- NO_SIGNAL (interval includes zero): 0 cells. NOT_SIGNIFICANT_AFTER_MULTIPLICITY: 0 cells.

## 7. Ladders (one ladder = one thesis)

1,147 ladders with ≥ 3 live rungs at latest pregame. a ladder's realised best rung is one draw of one outcome; read the by-family shares across many ladders, never one ladder's winner.

| family | ladders | best realised = main rung | best CLV = main rung | incoherent | a rung ≥ 2c under the ladder's own fair curve |
|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 16 | 37.5% | 31.2% | 0 | 0 |
| PLAYER_STAT | 731 | 19.0% | 32.7% | 2 | 0 |
| SPREAD | 224 | 9.8% | 37.1% | 7 | 0 |
| TEAM_TOTAL | 64 | 9.4% | 23.4% | 8 | 0 |
| TOTAL | 112 | 8.9% | 22.3% | 5 | 0 |

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


