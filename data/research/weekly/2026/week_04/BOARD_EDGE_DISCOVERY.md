# BOARD EDGE DISCOVERY — 2026 week 4

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

_Inputs: board board-research-1.0.0, miner board-miner-1.0.0, script autopsy script-autopsy-1.0.0, weeks [4]; board rows 64,735_

## 1. Coverage — what was and was not analysed

| stage | contracts |
|---|---|
| discovered | 13,055 |
| mapped_to_game | 13,055 |
| captured_pregame | 12,210 |
| settled_any_source | 12,210 |
| football_settled | 9,945 |
| price_at_primary_horizon | 9,945 |
| executable_quote | 9,945 |
| fee_known | 9,945 |
| analyzed_primary | 9,914 |

Exclusions (every contract that left the funnel, by reason):

- 737 — captured_pregame: never quoted before kickoff
- 489 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_TEAM:FULL:first_td_team]
- 436 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_SCORER:FULL:first_td]
- 240 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [RACE_TO_N:FULL:race]
- 175 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_reception]
- 163 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:fantasy_points]
- 160 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_sacks]
- 160 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_yards]
- 128 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:field_goals]
- 108 — captured_pregame: discovered, never in a pregame capture row (series outside the capture tiers, or listed only after kickoff)
- 79 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_rush]
- 45 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receiving_yards]
- 35 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:touchdowns]
- 32 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:fantasy_points]
- 31 — analyzed_primary: football settlement contradicted by the exchange's terminal result (flagged, never resolved)
- 28 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:touchdowns]
- 20 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receptions]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:defensive_st_td]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:btts]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:overtime]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:safety]
- 11 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rushing_yards]

Discovery universe: GAME_NOT_IN_REG_SCHEDULE (preseason / prior season) 10,294 · GAME_OTHER_WEEKS 14,569 · GAME_TARGET_WEEKS 51,974 · NON_GAME (season / futures / awards / leaders) 25,572

By week × family (primary horizon):

| week | family | discovered | captured | football-settled | analysed |
|---|---|---|---|---|---|
| 4 | BOTH_TEAMS_SCORE | 64 | 64 | 64 | 64 |
| 4 | BOTH_TEAMS_SCORE_N | 64 | 64 | 64 | 64 |
| 4 | FIRST_TD_SCORER | 436 | 436 | 0 | 0 |
| 4 | FIRST_TD_TEAM | 489 | 489 | 0 | 0 |
| 4 | GAME_EVENT | 64 | 64 | 0 | 0 |
| 4 | GAME_PLAYER_LEADER | 253 | 218 | 218 | 187 |
| 4 | GAME_WINNER | 32 | 32 | 32 | 32 |
| 4 | HALF_FULL_RESULT | 144 | 144 | 144 | 144 |
| 4 | PERIOD_WINNER | 288 | 288 | 288 | 288 |
| 4 | PLAYER_STAT | 6,557 | 6,010 | 5,294 | 5,294 |
| 4 | RACE_TO_N | 240 | 240 | 0 | 0 |
| 4 | SEASON_FANTASY | 106 | 0 | 0 | 0 |
| 4 | SPREAD | 1,676 | 1,557 | 1,557 | 1,557 |
| 4 | TEAM_STAT | 320 | 320 | 0 | 0 |
| 4 | TEAM_TOTAL | 798 | 790 | 790 | 790 |
| 4 | TOTAL | 1,412 | 1,382 | 1,382 | 1,382 |
| 4 | WIN_MARGIN_BUCKET | 112 | 112 | 112 | 112 |

## 2. How to read the cells

Unit = one contract SIDE bought at its executable ask. **mid bias** = event rate − the side's mid (is the market's fair price wrong?). **return** = payout − ask − fee per contract (is it exploitable after costs?). Intervals are game-clustered bootstrap (B=2000); rare-outcome cells also get a binomial floor. Cells with < 20 games, < 2 weeks or < 40 sides are DESCRIPTIVE_ONLY. Multiplicity: Benjamini–Hochberg q ≤ 0.2 across all 0 tested cells (≈0.0 would exclude zero by chance alone).

Status counts at latest pregame: DESCRIPTIVE_ONLY 1666.

## 3. Price bands

### Five full-game families, YES side, binned by QUOTED MID (the owner's Weeks 1–3 framing)

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| YES | 00-10c | 199 | 16 | 0.056 | 0.025 | -3.1c [-5.7, +1.3]c | -4.3c [-6.9, +0.1]c | W4:-3.9 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 192 | 16 | 0.146 | 0.104 | -4.2c [-11.4, +4.7]c | -5.6c [-12.9, +3.3]c | W4:-4.7 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 143 | 16 | 0.246 | 0.245 | -0.1c [-9.2, +10.0]c | -2.0c [-11.1, +8.1]c | W4:-0.6 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 126 | 16 | 0.348 | 0.325 | -2.3c [-13.7, +9.3]c | -4.4c [-15.8, +7.1]c | W4:-2.8 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 125 | 16 | 0.448 | 0.480 | +3.2c [-10.4, +15.4]c | +0.9c [-12.7, +13.1]c | W4:+2.7 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 119 | 16 | 0.549 | 0.571 | +2.2c [-11.8, +15.8]c | -0.0c [-14.1, +13.6]c | W4:+1.7 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 79 | 16 | 0.642 | 0.671 | +2.9c [-12.2, +17.5]c | +0.7c [-14.4, +15.2]c | W4:+2.3 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 72 | 16 | 0.745 | 0.792 | +4.7c [-7.4, +16.1]c | +2.7c [-9.3, +14.2]c | W4:+4.0 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 73 | 16 | 0.850 | 0.945 | +9.5c [+3.0, +14.7]c | +8.0c [-13.8, +13.2]c | W4:+8.9 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 112 | 16 | 0.948 | 1.000 | +5.2c [+4.9, +5.4]c | +4.2c [-15.1, +4.4]c | W4:+4.5 | DESCRIPTIVE_ONLY |

### Whole board, binned by the ASK actually paid

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| NO | 00-10c | 214 | 16 | 0.056 | 0.014 | -3.3c [-4.9, -0.4]c | -4.6c [-6.2, +15.6]c | W4:-4.2 | DESCRIPTIVE_ONLY |
| NO | 10-20c | 404 | 16 | 0.149 | 0.111 | -2.8c [-7.0, +1.5]c | -4.7c [-8.9, -0.4]c | W4:-3.8 | DESCRIPTIVE_ONLY |
| NO | 20-30c | 500 | 16 | 0.244 | 0.240 | +0.6c [-5.8, +7.5]c | -1.7c [-7.9, +5.2]c | W4:-0.4 | DESCRIPTIVE_ONLY |
| NO | 30-40c | 488 | 16 | 0.347 | 0.326 | -1.4c [-6.6, +4.3]c | -3.7c [-8.9, +1.9]c | W4:-2.1 | DESCRIPTIVE_ONLY |
| NO | 40-50c | 671 | 16 | 0.450 | 0.449 | +0.4c [-6.3, +7.4]c | -1.9c [-8.6, +5.0]c | W4:-0.2 | DESCRIPTIVE_ONLY |
| NO | 50-60c | 857 | 16 | 0.545 | 0.545 | +0.6c [-4.9, +6.0]c | -1.8c [-7.3, +3.6]c | W4:-0.0 | DESCRIPTIVE_ONLY |
| NO | 60-70c | 909 | 16 | 0.646 | 0.636 | -0.3c [-5.2, +4.8]c | -2.6c [-7.6, +2.5]c | W4:-1.0 | DESCRIPTIVE_ONLY |
| NO | 70-80c | 1,123 | 16 | 0.747 | 0.721 | -1.9c [-5.5, +1.6]c | -3.9c [-7.6, -0.5]c | W4:-2.6 | DESCRIPTIVE_ONLY |
| NO | 80-90c | 1,647 | 16 | 0.847 | 0.819 | -2.0c [-5.4, +1.1]c | -3.7c [-7.1, -0.6]c | W4:-2.8 | DESCRIPTIVE_ONLY |
| NO | 90-100c | 2,659 | 16 | 0.948 | 0.930 | -0.8c [-2.4, +0.6]c | -2.1c [-3.7, -0.8]c | W4:-1.8 | DESCRIPTIVE_ONLY |
| YES | 00-10c | 2,483 | 16 | 0.055 | 0.053 | +0.7c [-0.3, +2.0]c | -0.6c [-1.7, +0.7]c | W4:-0.2 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 1,867 | 16 | 0.141 | 0.140 | +0.9c [-1.8, +3.5]c | -1.0c [-3.7, +1.7]c | W4:-0.1 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 1,261 | 16 | 0.242 | 0.264 | +3.1c [-0.7, +7.1]c | +0.9c [-2.8, +4.9]c | W4:+2.2 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 966 | 16 | 0.345 | 0.341 | +0.4c [-4.5, +5.5]c | -2.0c [-6.9, +3.1]c | W4:-0.4 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 863 | 16 | 0.445 | 0.430 | -0.8c [-5.7, +4.0]c | -3.2c [-8.2, +1.5]c | W4:-1.5 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 747 | 16 | 0.541 | 0.519 | -1.4c [-7.4, +4.5]c | -3.9c [-9.8, +2.0]c | W4:-2.1 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 491 | 16 | 0.642 | 0.652 | +1.6c [-4.4, +7.7]c | -0.7c [-6.7, +5.4]c | W4:+0.9 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 467 | 16 | 0.745 | 0.749 | +1.2c [-5.8, +7.6]c | -0.9c [-7.9, +5.5]c | W4:+0.4 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 442 | 16 | 0.841 | 0.844 | +1.2c [-4.0, +6.5]c | -0.6c [-5.8, +4.7]c | W4:+0.3 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 318 | 16 | 0.946 | 0.959 | +2.7c [-0.1, +5.2]c | +0.9c [-1.9, +3.3]c | W4:+1.3 | DESCRIPTIVE_ONLY |

## 4. Market families

| family | contract-sides | mean return at the ask |
|---|---|---|
| PLAYER_STAT | 10,402 | -1.7c |
| SPREAD | 3,114 | -2.0c |
| TOTAL | 2,757 | -2.1c |
| TEAM_TOTAL | 1,542 | -2.2c |
| PERIOD_WINNER | 576 | -2.1c |
| GAME_PLAYER_LEADER | 239 | -7.4c |
| HALF_FULL_RESULT | 230 | -1.2c |
| WIN_MARGIN_BUCKET | 207 | -2.1c |
| BOTH_TEAMS_SCORE | 128 | -2.7c |
| BOTH_TEAMS_SCORE_N | 118 | -2.4c |
| GAME_WINNER | 64 | -2.0c |

## 5. Conditional patterns that survived every safeguard (CANDIDATE) — discovery only

0 CANDIDATE cells at latest pregame. Negative returns dominate: most survivors are COST (half-spread + fee) or favourite–longshot effects, not hidden value. Mid bias says which are mispricing.

| cell | sides | games | weeks | price | event | mid bias (CI) | return (CI) | q | by week |
|---|---|---|---|---|---|---|---|---|---|

## 6. Patterns that did NOT survive (rejected in discovery)

- UNSTABLE (a week or a held-out week flips the sign): 0 cells. Largest:
- NO_SIGNAL (interval includes zero): 0 cells. NOT_SIGNIFICANT_AFTER_MULTIPLICITY: 0 cells.

## 7. Ladders (one ladder = one thesis)

1,190 ladders with ≥ 3 live rungs at latest pregame. a ladder's realised best rung is one draw of one outcome; read the by-family shares across many ladders, never one ladder's winner.

| family | ladders | best realised = main rung | best CLV = main rung | incoherent | a rung ≥ 2c under the ladder's own fair curve |
|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 15 | 46.7% | 53.3% | 0 | 0 |
| PLAYER_STAT | 775 | 17.5% | 37.9% | 1 | 0 |
| SPREAD | 224 | 8.9% | 29.5% | 6 | 0 |
| TEAM_TOTAL | 64 | 12.5% | 20.3% | 10 | 0 |
| TOTAL | 112 | 6.2% | 17.0% | 1 | 0 |

## 8. Preregistered tests (discovery reading vs prospective reading)

| id | hypothesis | metric | discovery (W1–3) | prospective weeks | prospective value (family CI) | games | suggested |
|---|---|---|---|---|---|---|---|
| H-20261001-B01 | Full-game longshot YES underpriced at the mid | MID_BIAS (+) | 0.0372 [-0.0, +0.1] | [4] | -0.0243 [-0.1, +0.1] | 16 | INCONCLUSIVE |
| H-20261001-B02 | Full-game YES at 60-70c overpriced at the mid | MID_BIAS (−) | -0.0635 [-0.2, +0.0] | [4] | 0.0294 [-0.2, +0.2] | 16 | INCONCLUSIVE |
| H-20261001-B03 | Sides priced 90c+ lose after fees | RETURN_AT_ASK (−) | -0.0219 [-0.0, -0.0] | [4] | -0.0178 [-0.0, -0.0] | 16 | INCONCLUSIVE |
| H-20261001-B04 | Modest DATA_ONLY disagreement predicts movement toward it | MOVE_TOWARD_MODEL (+) | 0.0823 [+0.0, +0.1] | [4] | -0.0415 [-0.2, +0.1] | 16 | INCONCLUSIVE |
| H-20261001-B05 | Adjacent yardage rungs beat the main rung after fees | PAIRED_RUNG (+) | 0.0110 [-0.0, +0.0] | [4] | 0.0333 [-0.0, +0.1] | 16 | INCONCLUSIVE |
| H-20261001-B06 | Team total beats spread as the expression of an offensive thesis | PAIRED_EXPRESSION (+) | 0.1046 [-0.1, +0.3] | [4] | -0.0283 [-0.4, +0.4] | 13 | INCONCLUSIVE |
| H-20261001-B07 | Uncertain roles are priced worse than certain roles | EXCESS_BRIER_GAP (+) | -0.0046 [-0.0, +0.0] | [4] | 0.0424 [-0.1, +0.2] | 15 | INCONCLUSIVE |
| H-20261001-B08 | Player-prop NO at 80c+ loses after fees | RETURN_AT_ASK (−) | -0.0304 [-0.0, -0.0] | [4] | -0.0369 [-0.1, -0.0] | 16 | INCONCLUSIVE |
| H-20261001-B09 | Player-prop YES longshots lose after fees | RETURN_AT_ASK (−) | -0.0142 [-0.0, -0.0] | [4] | 0.0074 [-0.0, +0.0] | 16 | INCONCLUSIVE |
| H-20261001-B10 | Chasing a pregame move loses | RETURN_AT_ASK (−) | -0.1009 [-0.1, -0.1] | [4] | -0.0492 [-0.2, +0.1] | 15 | INCONCLUSIVE |
| H-20261001-B11 | A large incumbent player-model OVER view marks an underpriced YES | MID_BIAS (+) | 0.0784 [+0.0, +0.1] | [4] | -0.0267 [-0.1, +0.1] | 15 | INCONCLUSIVE |

_Suggested statuses are suggestions; only the owner transitions the registry. Weeks 1–3 are never evidence for these hypotheses._

## 9. Patterns worth testing next (not registered)


