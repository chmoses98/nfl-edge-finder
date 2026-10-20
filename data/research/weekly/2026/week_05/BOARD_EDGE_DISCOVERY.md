# BOARD EDGE DISCOVERY — 2026 week 5

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

_Inputs: board board-research-1.0.0, miner board-miner-1.0.0, script autopsy script-autopsy-1.0.0, weeks [5]; board rows 60,540_

## 1. Coverage — what was and was not analysed

| stage | contracts |
|---|---|
| discovered | 12,206 |
| mapped_to_game | 12,206 |
| captured_pregame | 11,347 |
| settled_any_source | 11,347 |
| football_settled | 9,241 |
| price_at_primary_horizon | 9,241 |
| executable_quote | 9,241 |
| fee_known | 9,241 |
| analyzed_primary | 9,204 |

Exclusions (every contract that left the funnel, by reason):

- 761 — captured_pregame: never quoted before kickoff
- 462 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_TEAM:FULL:first_td_team]
- 425 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_SCORER:FULL:first_td]
- 225 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [RACE_TO_N:FULL:race]
- 158 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_reception]
- 150 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_sacks]
- 150 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_yards]
- 147 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:fantasy_points]
- 120 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:field_goals]
- 98 — captured_pregame: discovered, never in a pregame capture row (series outside the capture tiers, or listed only after kickoff)
- 68 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_rush]
- 35 — analyzed_primary: football settlement contradicted by the exchange's terminal result (flagged, never resolved)
- 32 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:touchdowns]
- 30 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:fantasy_points]
- 27 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:touchdowns]
- 26 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receiving_yards]
- 15 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:defensive_st_td]
- 15 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:btts]
- 15 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:overtime]
- 15 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:safety]
- 12 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receptions]
- 4 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [PLAYER_H2H:FULL:receiving_yards]
- 3 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:receptions]
- 3 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:receiving_yards]
- 2 — analyzed_primary: non-binary payout (tie split / scalar): excluded from event-rate analysis
- 2 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [PLAYER_H2H:FULL:passing_yards]
- 2 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [PLAYER_H2H:FULL:rushing_yards]

Discovery universe: GAME_NOT_IN_REG_SCHEDULE (preseason / prior season) 10,050 · GAME_OTHER_WEEKS 13,813 · GAME_TARGET_WEEKS 64,180 · NON_GAME (season / futures / awards / leaders) 31,491

By week × family (primary horizon):

| week | family | discovered | captured | football-settled | analysed |
|---|---|---|---|---|---|
| 5 | BOTH_TEAMS_SCORE | 60 | 60 | 60 | 60 |
| 5 | BOTH_TEAMS_SCORE_N | 60 | 60 | 60 | 60 |
| 5 | FIRST_TD_SCORER | 425 | 425 | 0 | 0 |
| 5 | FIRST_TD_TEAM | 462 | 462 | 0 | 0 |
| 5 | GAME_EVENT | 60 | 60 | 0 | 0 |
| 5 | GAME_PLAYER_LEADER | 234 | 186 | 186 | 159 |
| 5 | GAME_WINNER | 30 | 30 | 30 | 28 |
| 5 | HALF_FULL_RESULT | 135 | 135 | 135 | 135 |
| 5 | PERIOD_WINNER | 270 | 270 | 270 | 270 |
| 5 | PLAYER_H2H | 8 | 8 | 0 | 0 |
| 5 | PLAYER_STAT | 6,064 | 5,525 | 4,899 | 4,899 |
| 5 | RACE_TO_N | 225 | 225 | 0 | 0 |
| 5 | SEASON_FANTASY | 95 | 0 | 0 | 0 |
| 5 | SPREAD | 1,618 | 1,466 | 1,466 | 1,460 |
| 5 | TEAM_STAT | 300 | 300 | 0 | 0 |
| 5 | TEAM_TOTAL | 743 | 739 | 739 | 739 |
| 5 | TOTAL | 1,312 | 1,291 | 1,291 | 1,289 |
| 5 | WIN_MARGIN_BUCKET | 105 | 105 | 105 | 105 |

## 2. How to read the cells

Unit = one contract SIDE bought at its executable ask. **mid bias** = event rate − the side's mid (is the market's fair price wrong?). **return** = payout − ask − fee per contract (is it exploitable after costs?). Intervals are game-clustered bootstrap (B=2000); rare-outcome cells also get a binomial floor. Cells with < 20 games, < 2 weeks or < 40 sides are DESCRIPTIVE_ONLY. Multiplicity: Benjamini–Hochberg q ≤ 0.2 across all 0 tested cells (≈0.0 would exclude zero by chance alone).

Status counts at latest pregame: DESCRIPTIVE_ONLY 1552.

## 3. Price bands

### Five full-game families, YES side, binned by QUOTED MID (the owner's Weeks 1–3 framing)

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| YES | 00-10c | 192 | 15 | 0.056 | 0.031 | -2.5c [-5.5, +1.4]c | -3.7c [-6.6, +0.3]c | W5:-3.2 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 176 | 15 | 0.148 | 0.176 | +2.8c [-5.1, +10.8]c | +1.4c [-6.5, +9.4]c | W5:+2.3 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 143 | 15 | 0.250 | 0.280 | +3.0c [-7.9, +14.6]c | +1.1c [-9.7, +12.7]c | W5:+2.5 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 126 | 15 | 0.357 | 0.429 | +7.2c [-6.3, +20.7]c | +5.0c [-8.5, +18.5]c | W5:+6.6 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 118 | 15 | 0.450 | 0.508 | +5.8c [-7.8, +18.7]c | +3.5c [-10.0, +16.5]c | W5:+5.3 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 102 | 15 | 0.552 | 0.637 | +8.5c [-7.3, +24.2]c | +6.3c [-9.6, +21.9]c | W5:+8.0 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 73 | 15 | 0.648 | 0.671 | +2.3c [-15.9, +18.0]c | +0.1c [-18.1, +15.8]c | W5:+1.6 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 58 | 15 | 0.746 | 0.793 | +4.7c [-11.2, +19.6]c | +2.7c [-13.2, +17.5]c | W5:+4.0 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 62 | 15 | 0.848 | 0.919 | +7.1c [-2.7, +14.6]c | +5.6c [-4.1, +13.1]c | W5:+6.5 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 100 | 15 | 0.945 | 0.960 | +1.5c [-3.1, +5.3]c | +0.5c [-21.8, +4.4]c | W5:+0.8 | DESCRIPTIVE_ONLY |

### Whole board, binned by the ASK actually paid

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| NO | 00-10c | 221 | 15 | 0.054 | 0.023 | -2.4c [-4.2, -0.4]c | -3.5c [-5.3, -1.5]c | W5:-3.1 | DESCRIPTIVE_ONLY |
| NO | 10-20c | 400 | 15 | 0.151 | 0.120 | -2.3c [-6.3, +2.1]c | -4.0c [-8.1, +0.4]c | W5:-3.1 | DESCRIPTIVE_ONLY |
| NO | 20-30c | 432 | 15 | 0.245 | 0.255 | +1.7c [-4.9, +7.6]c | -0.3c [-6.9, +5.6]c | W5:+1.0 | DESCRIPTIVE_ONLY |
| NO | 30-40c | 450 | 15 | 0.347 | 0.340 | +0.0c [-6.7, +6.5]c | -2.2c [-9.0, +4.3]c | W5:-0.7 | DESCRIPTIVE_ONLY |
| NO | 40-50c | 597 | 15 | 0.451 | 0.432 | -1.3c [-7.8, +5.4]c | -3.6c [-10.1, +3.1]c | W5:-1.9 | DESCRIPTIVE_ONLY |
| NO | 50-60c | 834 | 15 | 0.546 | 0.525 | -1.4c [-7.9, +4.6]c | -3.8c [-10.2, +2.2]c | W5:-2.0 | DESCRIPTIVE_ONLY |
| NO | 60-70c | 810 | 15 | 0.644 | 0.619 | -1.9c [-6.6, +2.7]c | -4.2c [-8.9, +0.4]c | W5:-2.6 | DESCRIPTIVE_ONLY |
| NO | 70-80c | 1,096 | 15 | 0.747 | 0.733 | -0.7c [-4.5, +3.1]c | -2.8c [-6.5, +1.0]c | W5:-1.4 | DESCRIPTIVE_ONLY |
| NO | 80-90c | 1,548 | 15 | 0.849 | 0.843 | +0.2c [-2.6, +3.2]c | -1.5c [-4.3, +1.5]c | W5:-0.6 | DESCRIPTIVE_ONLY |
| NO | 90-100c | 2,468 | 15 | 0.947 | 0.940 | +0.1c [-1.8, +2.0]c | -1.1c [-3.0, +0.8]c | W5:-0.8 | DESCRIPTIVE_ONLY |
| YES | 00-10c | 2,296 | 15 | 0.054 | 0.047 | +0.1c [-1.6, +1.9]c | -1.0c [-2.8, +0.7]c | W5:-0.7 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 1,724 | 15 | 0.141 | 0.130 | -0.3c [-3.0, +2.2]c | -2.0c [-4.7, +0.5]c | W5:-1.2 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 1,193 | 15 | 0.243 | 0.235 | -0.0c [-3.9, +3.6]c | -2.1c [-6.0, +1.5]c | W5:-0.8 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 862 | 15 | 0.344 | 0.350 | +1.4c [-2.8, +5.1]c | -1.0c [-5.1, +2.8]c | W5:+0.6 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 851 | 15 | 0.446 | 0.452 | +1.4c [-4.6, +8.2]c | -1.1c [-7.0, +5.7]c | W5:+0.7 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 672 | 15 | 0.540 | 0.552 | +1.9c [-4.8, +8.2]c | -0.5c [-7.2, +5.8]c | W5:+1.3 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 448 | 15 | 0.643 | 0.623 | -1.3c [-7.4, +4.9]c | -3.7c [-9.7, +2.5]c | W5:-2.1 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 434 | 15 | 0.745 | 0.733 | -0.5c [-6.7, +5.8]c | -2.5c [-8.7, +3.8]c | W5:-1.2 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 422 | 15 | 0.841 | 0.853 | +1.9c [-2.5, +6.3]c | +0.2c [-4.1, +4.7]c | W5:+1.2 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 291 | 15 | 0.947 | 0.966 | +2.9c [+0.4, +5.1]c | +1.5c [-0.9, +3.7]c | W5:+1.9 | DESCRIPTIVE_ONLY |

## 4. Market families

| family | contract-sides | mean return at the ask |
|---|---|---|
| PLAYER_STAT | 9,632 | -1.6c |
| SPREAD | 2,920 | -2.0c |
| TOTAL | 2,575 | -2.0c |
| TEAM_TOTAL | 1,465 | -1.8c |
| PERIOD_WINNER | 540 | -2.1c |
| HALF_FULL_RESULT | 224 | -1.0c |
| GAME_PLAYER_LEADER | 209 | -6.6c |
| WIN_MARGIN_BUCKET | 195 | -1.4c |
| BOTH_TEAMS_SCORE | 120 | -2.6c |
| BOTH_TEAMS_SCORE_N | 113 | -2.4c |
| GAME_WINNER | 56 | -2.0c |

## 5. Conditional patterns that survived every safeguard (CANDIDATE) — discovery only

0 CANDIDATE cells at latest pregame. Negative returns dominate: most survivors are COST (half-spread + fee) or favourite–longshot effects, not hidden value. Mid bias says which are mispricing.

| cell | sides | games | weeks | price | event | mid bias (CI) | return (CI) | q | by week |
|---|---|---|---|---|---|---|---|---|---|

## 6. Patterns that did NOT survive (rejected in discovery)

- UNSTABLE (a week or a held-out week flips the sign): 0 cells. Largest:
- NO_SIGNAL (interval includes zero): 0 cells. NOT_SIGNIFICANT_AFTER_MULTIPLICITY: 0 cells.

## 7. Ladders (one ladder = one thesis)

1,094 ladders with ≥ 3 live rungs at latest pregame. a ladder's realised best rung is one draw of one outcome; read the by-family shares across many ladders, never one ladder's winner.

| family | ladders | best realised = main rung | best CLV = main rung | incoherent | a rung ≥ 2c under the ladder's own fair curve |
|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 15 | 20.0% | 60.0% | 0 | 0 |
| PLAYER_STAT | 704 | 19.2% | 37.6% | 1 | 0 |
| SPREAD | 210 | 3.8% | 33.8% | 1 | 0 |
| TEAM_TOTAL | 60 | 10.0% | 25.0% | 9 | 0 |
| TOTAL | 105 | 17.1% | 21.0% | 0 | 0 |

## 8. Preregistered tests (discovery reading vs prospective reading)

| id | hypothesis | metric | discovery (W1–3) | prospective weeks | prospective value (family CI) | games | suggested |
|---|---|---|---|---|---|---|---|
| H-20261001-B01 | Full-game longshot YES underpriced at the mid | MID_BIAS (+) | 0.0372 [-0.0, +0.1] | [5] | 0.0291 [-0.1, +0.1] | 15 | INCONCLUSIVE |
| H-20261001-B02 | Full-game YES at 60-70c overpriced at the mid | MID_BIAS (−) | -0.0635 [-0.2, +0.0] | [5] | 0.0229 [-0.2, +0.2] | 15 | INCONCLUSIVE |
| H-20261001-B03 | Sides priced 90c+ lose after fees | RETURN_AT_ASK (−) | -0.0219 [-0.0, -0.0] | [5] | -0.0084 [-0.0, +0.0] | 15 | INCONCLUSIVE |
| H-20261001-B04 | Modest DATA_ONLY disagreement predicts movement toward it | MOVE_TOWARD_MODEL (+) | 0.0823 [+0.0, +0.1] | [5] | — — | 0 | INCONCLUSIVE |
| H-20261001-B05 | Adjacent yardage rungs beat the main rung after fees | PAIRED_RUNG (+) | 0.0110 [-0.0, +0.0] | [5] | 0.0307 [-0.0, +0.1] | 15 | INCONCLUSIVE |
| H-20261001-B06 | Team total beats spread as the expression of an offensive thesis | PAIRED_EXPRESSION (+) | 0.1046 [-0.1, +0.3] | [5] | 0.1616 [-0.1, +0.5] | 8 | INCONCLUSIVE |
| H-20261001-B07 | Uncertain roles are priced worse than certain roles | EXCESS_BRIER_GAP (+) | -0.0046 [-0.0, +0.0] | [5] | 0.0057 [-0.1, +0.1] | 13 | INCONCLUSIVE |
| H-20261001-B08 | Player-prop NO at 80c+ loses after fees | RETURN_AT_ASK (−) | -0.0304 [-0.0, -0.0] | [5] | -0.0192 [-0.1, +0.0] | 15 | INCONCLUSIVE |
| H-20261001-B09 | Player-prop YES longshots lose after fees | RETURN_AT_ASK (−) | -0.0142 [-0.0, -0.0] | [5] | 0.0016 [-0.0, +0.0] | 15 | INCONCLUSIVE |
| H-20261001-B10 | Chasing a pregame move loses | RETURN_AT_ASK (−) | -0.1009 [-0.1, -0.1] | [5] | -0.0661 [-0.2, +0.1] | 15 | INCONCLUSIVE |
| H-20261001-B11 | A large incumbent player-model OVER view marks an underpriced YES | MID_BIAS (+) | 0.0784 [+0.0, +0.1] | [5] | 0.0055 [-0.1, +0.1] | 15 | INCONCLUSIVE |

_Suggested statuses are suggestions; only the owner transitions the registry. Weeks 1–3 are never evidence for these hypotheses._

## 9. Patterns worth testing next (not registered)


