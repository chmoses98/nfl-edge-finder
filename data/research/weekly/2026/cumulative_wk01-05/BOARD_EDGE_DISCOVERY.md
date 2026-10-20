# BOARD EDGE DISCOVERY — 2026 weeks 1–5 (cumulative)

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

_Inputs: board board-research-1.0.0, miner board-miner-1.0.0, script autopsy script-autopsy-1.0.0, weeks [1, 2, 3, 4, 5]; board rows 319,245_

## 1. Coverage — what was and was not analysed

| stage | contracts |
|---|---|
| discovered | 64,180 |
| mapped_to_game | 64,180 |
| captured_pregame | 60,626 |
| settled_any_source | 60,626 |
| football_settled | 48,694 |
| price_at_primary_horizon | 48,694 |
| executable_quote | 48,694 |
| fee_known | 48,678 |
| analyzed_primary | 48,568 |

Exclusions (every contract that left the funnel, by reason):

- 3,223 — captured_pregame: never quoted before kickoff
- 2,372 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_TEAM:FULL:first_td_team]
- 2,085 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_SCORER:FULL:first_td]
- 1,230 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [RACE_TO_N:FULL:race]
- 868 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_yards]
- 827 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_reception]
- 817 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:fantasy_points]
- 790 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_sacks]
- 632 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:field_goals]
- 362 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_rush]
- 331 — captured_pregame: discovered, never in a pregame capture row (series outside the capture tiers, or listed only after kickoff)
- 303 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:receiving_yards]
- 199 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_touchdowns]
- 198 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TOTAL_TD:FULL:total_touchdowns]
- 168 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:touchdowns]
- 158 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:fantasy_points]
- 150 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receiving_yards]
- 145 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:touchdowns]
- 144 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:rushing_yards]
- 108 — analyzed_primary: football settlement contradicted by the exchange's terminal result (flagged, never resolved)
- 79 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:defensive_st_td]
- 79 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:btts]
- 79 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:overtime]
- 78 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:safety]
- 73 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receptions]
- 44 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rushing_yards]
- 16 — fee_known: fee unknown
- 11 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:attempts]
- 11 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:completions]
- 7 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:passing_yards]
- 4 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [PLAYER_H2H:FULL:receiving_yards]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:interceptions]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:passing_tds]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rush_rec_yards]
- 3 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:receptions]
- 3 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:receiving_yards]
- 2 — analyzed_primary: non-binary payout (tie split / scalar): excluded from event-rate analysis
- 2 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [PLAYER_H2H:FULL:passing_yards]
- 2 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [PLAYER_H2H:FULL:rushing_yards]

Discovery universe: GAME_NOT_IN_REG_SCHEDULE (preseason / prior season) 10,050 · GAME_OTHER_WEEKS 13,813 · GAME_TARGET_WEEKS 64,180 · NON_GAME (season / futures / awards / leaders) 31,491

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
| 2 | BOTH_TEAMS_SCORE | 64 | 64 | 64 | 64 |
| 2 | BOTH_TEAMS_SCORE_N | 64 | 64 | 64 | 64 |
| 2 | FIRST_TD_SCORER | 387 | 386 | 0 | 0 |
| 2 | FIRST_TD_TEAM | 469 | 468 | 0 | 0 |
| 2 | GAME_EVENT | 64 | 64 | 0 | 0 |
| 2 | GAME_PLAYER_LEADER | 144 | 7 | 7 | 7 |
| 2 | GAME_WINNER | 32 | 32 | 32 | 32 |
| 2 | HALF_FULL_RESULT | 144 | 144 | 144 | 144 |
| 2 | PERIOD_WINNER | 288 | 288 | 288 | 286 |
| 2 | PLAYER_STAT | 6,118 | 5,661 | 5,004 | 5,004 |
| 2 | RACE_TO_N | 240 | 240 | 0 | 0 |
| 2 | SEASON_FANTASY | 13 | 0 | 0 | 0 |
| 2 | SEASON_LEADER | 196 | 194 | 0 | 0 |
| 2 | SPREAD | 1,736 | 1,594 | 1,594 | 1,591 |
| 2 | TEAM_STAT | 416 | 416 | 0 | 0 |
| 2 | TEAM_TOTAL | 798 | 786 | 786 | 786 |
| 2 | TOTAL | 1,400 | 1,378 | 1,378 | 1,370 |
| 2 | TOTAL_TD | 101 | 96 | 0 | 0 |
| 2 | WIN_MARGIN_BUCKET | 112 | 112 | 112 | 112 |
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

Unit = one contract SIDE bought at its executable ask. **mid bias** = event rate − the side's mid (is the market's fair price wrong?). **return** = payout − ask − fee per contract (is it exploitable after costs?). Intervals are game-clustered bootstrap (B=2000); rare-outcome cells also get a binomial floor. Cells with < 20 games, < 2 weeks or < 40 sides are DESCRIPTIVE_ONLY. Multiplicity: Benjamini–Hochberg q ≤ 0.2 across all 1249 tested cells (≈62.5 would exclude zero by chance alone).

Status counts at latest pregame: CANDIDATE 145, DESCRIPTIVE_ONLY 490, NOT_SIGNIFICANT_AFTER_MULTIPLICITY 6, NO_SIGNAL 973, UNSTABLE 125.

## 3. Price bands

### Five full-game families, YES side, binned by QUOTED MID (the owner's Weeks 1–3 framing)

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| YES | 00-10c | 1,025 | 79 | 0.057 | 0.046 | -1.1c [-3.1, +1.2]c | -2.4c [-4.5, -0.0]c | W1:+2.8 W2:-5.1 W3:-0.3 W4:-3.9 W5:-3.2 | UNSTABLE |
| YES | 10-20c | 920 | 79 | 0.147 | 0.170 | +2.3c [-1.6, +6.7]c | +0.7c [-3.2, +5.1]c | W1:+6.8 W2:+4.0 W3:-0.0 W4:-4.7 W5:+2.3 | NO_SIGNAL |
| YES | 20-30c | 714 | 79 | 0.247 | 0.270 | +2.3c [-2.3, +6.8]c | +0.4c [-4.2, +4.9]c | W1:+6.0 W2:-0.2 W3:+0.9 W4:-0.6 W5:+2.5 | NO_SIGNAL |
| YES | 30-40c | 655 | 79 | 0.352 | 0.373 | +2.0c [-3.6, +7.1]c | -0.3c [-5.9, +4.8]c | W1:+7.4 W2:-2.6 W3:-2.4 W4:-2.8 W5:+6.6 | NO_SIGNAL |
| YES | 40-50c | 627 | 79 | 0.449 | 0.456 | +0.7c [-5.8, +7.0]c | -1.7c [-8.2, +4.6]c | W1:+0.1 W2:-8.9 W3:+0.7 W4:+2.7 W5:+5.3 | NO_SIGNAL |
| YES | 50-60c | 567 | 79 | 0.547 | 0.589 | +4.2c [-2.7, +10.9]c | +1.7c [-5.1, +8.5]c | W1:+8.2 W2:-3.0 W3:+2.2 W4:+1.7 W5:+8.0 | NO_SIGNAL |
| YES | 60-70c | 404 | 79 | 0.646 | 0.616 | -3.0c [-10.4, +4.1]c | -5.5c [-13.0, +1.6]c | W1:-1.5 W2:-15.1 W3:-5.5 W4:+2.3 W5:+1.6 | NO_SIGNAL |
| YES | 70-80c | 323 | 79 | 0.748 | 0.743 | -0.5c [-7.5, +6.2]c | -2.5c [-9.5, +4.1]c | W1:-3.7 W2:-14.6 W3:+5.1 W4:+4.0 W5:+4.0 | NO_SIGNAL |
| YES | 80-90c | 342 | 79 | 0.851 | 0.886 | +3.5c [-1.4, +7.9]c | +1.9c [-3.0, +6.2]c | W1:-1.3 W2:-6.4 W3:+6.3 W4:+8.9 W5:+6.5 | NO_SIGNAL |
| YES | 90-100c | 538 | 79 | 0.947 | 0.946 | -0.1c [-3.3, +2.6]c | -1.2c [-4.4, +1.5]c | W1:-0.9 W2:-9.2 W3:+0.5 W4:+4.5 W5:+0.8 | NO_SIGNAL |

### Whole board, binned by the ASK actually paid

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| NO | 00-10c | 1,010 | 79 | 0.056 | 0.040 | -0.8c [-2.7, +1.6]c | -2.0c [-3.9, +0.4]c | W1:-0.2 W2:+3.2 W3:-3.2 W4:-4.2 W5:-3.1 | NO_SIGNAL |
| NO | 10-20c | 1,894 | 79 | 0.151 | 0.125 | -1.3c [-3.4, +1.1]c | -3.4c [-5.6, -1.1]c | W1:-3.5 W2:+0.8 W3:-3.1 W4:-3.8 W5:-3.1 | CANDIDATE |
| NO | 20-30c | 2,390 | 79 | 0.245 | 0.226 | -0.6c [-3.2, +2.1]c | -3.3c [-5.9, -0.6]c | W1:-6.7 W2:+2.5 W3:-6.3 W4:-0.4 W5:+1.0 | UNSTABLE |
| NO | 30-40c | 2,470 | 79 | 0.346 | 0.331 | -0.3c [-3.3, +2.8]c | -3.1c [-6.1, -0.0]c | W1:-1.7 W2:+0.7 W3:-3.7 W4:-2.1 W5:-0.7 | NOT_SIGNIFICANT_AFTER_MULTIPLICITY |
| NO | 40-50c | 3,247 | 79 | 0.449 | 0.448 | +0.8c [-2.4, +4.0]c | -1.8c [-5.0, +1.3]c | W1:-3.0 W2:+5.3 W3:-0.9 W4:-0.2 W5:-1.9 | NO_SIGNAL |
| NO | 50-60c | 4,395 | 79 | 0.545 | 0.543 | +0.7c [-2.5, +4.0]c | -1.9c [-5.2, +1.4]c | W1:-4.0 W2:+7.3 W3:-1.4 W4:-0.0 W5:-2.0 | NO_SIGNAL |
| NO | 60-70c | 4,427 | 79 | 0.645 | 0.628 | -0.7c [-2.8, +1.5]c | -3.3c [-5.5, -1.1]c | W1:-3.8 W2:+0.5 W3:-1.5 W4:-1.0 W5:-2.6 | CANDIDATE |
| NO | 70-80c | 5,636 | 79 | 0.749 | 0.719 | -1.2c [-3.2, +0.7]c | -4.3c [-6.4, -2.2]c | W1:-9.2 W2:+0.5 W3:-1.4 W4:-2.6 W5:-1.4 | CANDIDATE |
| NO | 80-90c | 7,845 | 79 | 0.849 | 0.824 | -1.1c [-2.8, +0.6]c | -3.4c [-5.2, -1.6]c | W1:-6.4 W2:-0.2 W3:-2.1 W4:-2.8 W5:-0.6 | CANDIDATE |
| NO | 90-100c | 13,268 | 79 | 0.950 | 0.934 | -0.1c [-1.3, +0.9]c | -1.9c [-3.1, -0.9]c | W1:-4.6 W2:+0.2 W3:-0.8 W4:-1.8 W5:-0.8 | CANDIDATE |
| YES | 00-10c | 11,463 | 79 | 0.055 | 0.046 | +0.1c [-0.7, +0.9]c | -1.3c [-2.0, -0.5]c | W1:+0.1 W2:-2.5 W3:-1.4 W4:-0.2 W5:-0.7 | CANDIDATE |
| YES | 10-20c | 9,011 | 79 | 0.142 | 0.133 | +0.5c [-1.0, +2.0]c | -1.7c [-3.1, -0.2]c | W1:+0.0 W2:-2.5 W3:-0.5 W4:-0.1 W5:-1.2 | CANDIDATE |
| YES | 20-30c | 6,301 | 79 | 0.242 | 0.235 | +0.7c [-1.1, +2.6]c | -2.1c [-3.9, -0.1]c | W1:-1.9 W2:-2.8 W3:-0.5 W4:+2.2 W5:-0.8 | UNSTABLE |
| YES | 30-40c | 4,774 | 79 | 0.344 | 0.339 | +1.0c [-1.1, +3.0]c | -2.0c [-4.0, +0.0]c | W1:-0.0 W2:-2.8 W3:+0.3 W4:-0.4 W5:+0.6 | NO_SIGNAL |
| YES | 40-50c | 4,543 | 79 | 0.445 | 0.426 | -0.7c [-3.6, +2.3]c | -3.6c [-6.5, -0.7]c | W1:-0.8 W2:-6.1 W3:-2.0 W4:-1.5 W5:+0.7 | CANDIDATE |
| YES | 50-60c | 3,674 | 79 | 0.540 | 0.520 | -1.1c [-4.2, +2.1]c | -3.7c [-6.8, -0.7]c | W1:+0.6 W2:-8.7 W3:-0.8 W4:-2.1 W5:+1.3 | CANDIDATE |
| YES | 60-70c | 2,506 | 79 | 0.644 | 0.625 | -0.3c [-3.7, +3.0]c | -3.5c [-6.9, -0.3]c | W1:-3.6 W2:-6.4 W3:+1.7 W4:+0.9 W5:-2.1 | UNSTABLE |
| YES | 70-80c | 2,392 | 79 | 0.745 | 0.735 | +1.1c [-1.8, +4.0]c | -2.3c [-5.2, +0.5]c | W1:-1.3 W2:-5.0 W3:+2.4 W4:+0.4 W5:-1.2 | NO_SIGNAL |
| YES | 80-90c | 2,243 | 79 | 0.842 | 0.844 | +2.6c [-0.0, +5.1]c | -0.8c [-3.2, +1.6]c | W1:+0.3 W2:-4.3 W3:+3.4 W4:+0.3 W5:+1.2 | NO_SIGNAL |
| YES | 90-100c | 1,613 | 79 | 0.948 | 0.939 | +1.7c [-0.6, +3.5]c | -1.2c [-3.6, +0.7]c | W1:-2.8 W2:-4.1 W3:-0.2 W4:+1.3 W5:+1.9 | NO_SIGNAL |

## 4. Market families

| family | contract-sides | mean return at the ask |
|---|---|---|
| PLAYER_STAT | 51,174 | -2.4c |
| SPREAD | 15,566 | -2.3c |
| TOTAL | 13,558 | -2.5c |
| TEAM_TOTAL | 7,609 | -2.4c |
| PERIOD_WINNER | 2,840 | -2.2c |
| HALF_FULL_RESULT | 1,131 | -1.7c |
| WIN_MARGIN_BUCKET | 1,015 | -2.8c |
| GAME_PLAYER_LEADER | 673 | -8.0c |
| BOTH_TEAMS_SCORE | 632 | -3.0c |
| BOTH_TEAMS_SCORE_N | 592 | -4.3c |
| GAME_WINNER | 312 | -2.0c |

## 5. Conditional patterns that survived every safeguard (CANDIDATE) — discovery only

145 CANDIDATE cells at latest pregame. Negative returns dominate: most survivors are COST (half-spread + fee) or favourite–longshot effects, not hidden value. Mid bias says which are mispricing.

| cell | sides | games | weeks | price | event | mid bias (CI) | return (CI) | q | by week |
|---|---|---|---|---|---|---|---|---|---|
| `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=YES|env_total_band=total41-45` | 210 | 30 | 5 | 0.151 | 0.143 | +0.9c [+0.6, +1.2]c | -1.6c [-2.0, -1.3]c | 0.000 | W1:-3.2 W2:-1.3 W3:-1.6 W4:-1.0 W5:-1.2 |
| `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=YES|env_total_band=total45-49` | 154 | 22 | 5 | 0.156 | 0.143 | +0.6c [+0.2, +1.1]c | -2.2c [-2.7, -1.7]c | 0.000 | W1:-3.0 W2:-2.1 W3:-2.7 W4:-1.8 W5:-1.2 |
| `S18_family_x_side_x_mid|family=GAME_PLAYER_LEADER|side=YES|mid_band=10-20c` | 51 | 32 | 3 | 0.229 | 0.000 | -14.1c [-14.6, -13.5]c | -24.1c [-26.5, -13.4]c | 0.000 | W3:-26.0 W4:-25.0 W5:-21.2 |
| `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=NO|env_total_band=total45-49` | 126 | 22 | 5 | 0.856 | 0.825 | -0.9c [-1.5, -0.4]c | -3.9c [-5.1, -2.9]c | 0.000 | W1:-5.9 W2:-3.9 W3:-2.9 W4:-2.3 W5:-2.7 |
| `S02_family_x_side_x_price|family=GAME_PLAYER_LEADER|side=YES|price_band=10-20c` | 114 | 43 | 4 | 0.139 | 0.000 | -8.1c [-8.7, -7.5]c | -14.7c [-15.2, -6.5]c | 0.000 | W2:-18.0 W3:-14.7 W4:-14.4 W5:-14.9 |
| `S16_period_family_x_side_x_price|subfamily=TOTAL:2H:total_points|side=NO|price_band=10-20c` | 134 | 78 | 5 | 0.138 | 0.022 | -8.6c [-10.6, -5.8]c | -12.4c [-14.6, -6.3]c | 0.000 | W1:-14.1 W2:-8.0 W3:-11.0 W4:-15.0 W5:-15.4 |
| `S16_period_family_x_side_x_price|subfamily=GAME_PLAYER_LEADER:FULL:receiving_yards|side=YES|price_band=10-20c` | 85 | 38 | 3 | 0.137 | 0.000 | -7.8c [-8.5, -7.1]c | -14.5c [-15.0, -5.3]c | 0.000 | W3:-14.4 W4:-14.2 W5:-15.0 |
| `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=40-50c` | 222 | 64 | 5 | 0.439 | 0.288 | -11.8c [-17.8, -5.1]c | -16.8c [-23.1, -10.1]c | 0.000 | W1:-16.7 W2:-19.5 W3:-16.8 W4:-6.3 W5:-21.6 |
| `S03_family_x_side_x_rung|family=SPREAD|side=NO|rung_offset_band=main` | 1,104 | 79 | 5 | 0.618 | 0.598 | -0.9c [-2.3, +0.7]c | -3.6c [-5.0, -2.1]c | 0.000 | W1:-3.7 W2:-3.1 W3:-3.9 W4:-3.7 W5:-3.5 |
| `S16_period_family_x_side_x_price|subfamily=TOTAL:2H:total_points|side=NO|price_band=20-30c` | 79 | 67 | 5 | 0.249 | 0.101 | -11.4c [-17.5, -4.6]c | -16.1c [-22.2, -9.1]c | 0.000 | W1:-22.0 W2:-6.7 W3:-10.9 W4:-10.0 W5:-26.9 |
| `S13_player_disagreement_x_side|stat=receiving_yards|player_disagreement_band=5-10pp|side=NO` | 1,364 | 78 | 5 | 0.792 | 0.746 | -3.8c [-6.1, -1.5]c | -5.6c [-7.9, -3.2]c | 0.000 | W1:-4.2 W2:-6.1 W3:-3.4 W4:-9.9 W5:-4.5 |
| `S14_move_x_side_x_price|move_band=down>5c|side=YES|price_band=00-10c` | 417 | 67 | 5 | 0.058 | 0.024 | -1.8c [-3.3, +0.1]c | -3.8c [-5.2, -1.9]c | 0.000 | W1:-2.8 W2:-5.9 W3:-0.9 W4:-5.2 W5:-4.3 |
| `S02_family_x_side_x_price|family=TOTAL|side=NO|price_band=10-20c` | 580 | 79 | 5 | 0.145 | 0.072 | -5.4c [-8.5, -1.5]c | -8.1c [-11.1, -4.2]c | 0.000 | W1:-6.2 W2:-2.2 W3:-9.9 W4:-10.5 W5:-11.7 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=90-100c` | 8,144 | 79 | 5 | 0.951 | 0.930 | -0.8c [-1.9, +0.2]c | -2.4c [-3.5, -1.4]c | 0.001 | W1:-4.4 W2:-0.7 W3:-1.2 W4:-3.5 W5:-2.0 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=80-90c` | 4,199 | 79 | 5 | 0.850 | 0.818 | -1.6c [-3.4, +0.1]c | -4.0c [-5.9, -2.2]c | 0.001 | W1:-7.6 W2:-1.4 W3:-4.7 W4:-4.1 W5:-1.8 |
| `S18_family_x_side_x_mid|family=PLAYER_STAT|side=NO|mid_band=90-100c` | 7,441 | 79 | 5 | 0.954 | 0.937 | -0.7c [-1.7, +0.2]c | -2.0c [-3.0, -1.1]c | 0.003 | W1:-3.1 W2:-0.4 W3:-1.1 W4:-3.5 W5:-2.0 |
| `S04_rung_x_price_x_side|rung_offset_band=adjacent+1|price_band=90-100c|side=NO` | 1,004 | 79 | 5 | 0.964 | 0.931 | -1.7c [-3.4, -0.0]c | -3.5c [-5.3, -1.8]c | 0.003 | W1:-6.3 W2:-4.3 W3:-0.1 W4:-2.7 W5:-3.4 |
| `S01_side_x_price|side=NO|price_band=70-80c` | 5,636 | 79 | 5 | 0.749 | 0.719 | -1.2c [-3.2, +0.7]c | -4.3c [-6.4, -2.2]c | 0.003 | W1:-10.5 W2:-0.8 W3:-2.7 W4:-3.9 W5:-2.8 |
| `S03_family_x_side_x_rung|family=PLAYER_STAT|side=NO|rung_offset_band=adjacent+1` | 4,467 | 79 | 5 | 0.777 | 0.753 | -1.1c [-2.9, +0.6]c | -3.5c [-5.3, -1.7]c | 0.004 | W1:-6.7 W2:-1.1 W3:-3.8 W4:-3.9 W5:-2.0 |
| `S08_player_stat_x_side_x_price|stat=receiving_yards|side=NO|price_band=90-100c` | 2,394 | 79 | 5 | 0.947 | 0.921 | -1.5c [-3.0, -0.1]c | -2.9c [-4.4, -1.5]c | 0.004 | W1:-4.3 W2:-1.6 W3:-0.5 W4:-5.6 W5:-2.3 |
| `S18_family_x_side_x_mid|family=GAME_PLAYER_LEADER|side=YES|mid_band=00-10c` | 392 | 49 | 4 | 0.071 | 0.000 | -3.9c [-4.1, -3.6]c | -7.5c [-8.0, -0.2]c | 0.004 | W2:-6.8 W3:-7.9 W4:-7.4 W5:-7.4 |
| `S10_player_stat_x_total_env|stat=attempts|env_total_band=total45-49|side=YES` | 221 | 22 | 5 | 0.525 | 0.416 | -4.4c [-12.5, +2.9]c | -12.3c [-18.6, -6.0]c | 0.004 | W1:-10.1 W2:-14.5 W3:-19.0 W4:-3.8 W5:-23.0 |
| `S01_side_x_price|side=NO|price_band=80-90c` | 7,845 | 79 | 5 | 0.849 | 0.824 | -1.1c [-2.8, +0.6]c | -3.4c [-5.2, -1.6]c | 0.005 | W1:-7.3 W2:-1.1 W3:-3.0 W4:-3.7 W5:-1.5 |
| `S03_family_x_side_x_rung|family=PLAYER_STAT|side=NO|rung_offset_band=far+` | 10,759 | 79 | 5 | 0.895 | 0.874 | -0.9c [-2.4, +0.4]c | -2.8c [-4.3, -1.4]c | 0.006 | W1:-3.9 W2:-1.6 W3:-2.3 W4:-3.8 W5:-2.1 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=70-80c` | 2,808 | 79 | 5 | 0.750 | 0.708 | -1.9c [-4.3, +0.7]c | -5.5c [-8.3, -2.5]c | 0.006 | W1:-15.0 W2:-0.6 W3:-4.2 W4:-3.2 W5:-1.9 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=YES|price_band=50-60c` | 2,006 | 79 | 5 | 0.540 | 0.508 | -2.2c [-4.7, +0.5]c | -4.9c [-7.4, -2.2]c | 0.006 | W1:-2.7 W2:-9.3 W3:-3.1 W4:-5.4 W5:-4.1 |
| `S03_family_x_side_x_rung|family=PLAYER_STAT|side=YES|rung_offset_band=main` | 5,270 | 79 | 5 | 0.401 | 0.383 | -0.8c [-2.6, +1.0]c | -3.2c [-4.9, -1.5]c | 0.006 | W1:-1.2 W2:-7.8 W3:-0.9 W4:-2.8 W5:-3.7 |
| `S04_rung_x_price_x_side|rung_offset_band=adjacent+1|price_band=80-90c|side=NO` | 1,064 | 79 | 5 | 0.842 | 0.799 | -2.7c [-5.5, +0.1]c | -5.2c [-8.1, -2.5]c | 0.006 | W1:-13.1 W2:-0.7 W3:-6.3 W4:-5.1 W5:-2.1 |
| `S11_player_position_x_stat|position=QB|stat=completions|side=NO` | 680 | 79 | 5 | 0.584 | 0.476 | -4.9c [-10.5, +0.9]c | -11.9c [-18.2, -5.4]c | 0.006 | W1:-17.6 W2:-6.6 W3:-10.4 W4:-9.0 W5:-1.3 |
| `S15_availability_x_side|availability_state=EXPECTED_ACTIVE|stat=completions|side=NO` | 658 | 78 | 5 | 0.585 | 0.474 | -5.2c [-10.9, +1.0]c | -12.3c [-18.8, -5.6]c | 0.007 | W1:-18.7 W2:-6.9 W3:-10.4 W4:-9.0 W5:-1.3 |
| `S09_player_stat_x_role_certainty|stat=completions|role_certainty=HIGH|side=NO` | 652 | 78 | 5 | 0.586 | 0.475 | -5.1c [-10.9, +1.1]c | -12.3c [-18.8, -5.5]c | 0.009 | W1:-18.7 W2:-6.9 W3:-10.4 W4:-8.8 W5:-0.8 |
| `S08_player_stat_x_side_x_price|stat=interceptions|side=YES|price_band=00-10c` | 117 | 68 | 5 | 0.067 | 0.009 | -3.9c [-4.9, -2.1]c | -6.3c [-7.3, -0.3]c | 0.009 | W1:-7.7 W2:-8.0 W3:-7.1 W4:-3.2 W5:-6.6 |
| `S18_family_x_side_x_mid|family=PLAYER_STAT|side=NO|mid_band=80-90c` | 4,291 | 79 | 5 | 0.863 | 0.839 | -1.3c [-3.1, +0.5]c | -3.3c [-5.1, -1.4]c | 0.010 | W1:-4.8 W2:-2.2 W3:-4.2 W4:-3.5 W5:-1.4 |
| `S11_player_position_x_stat|position=WR|stat=receiving_yards|side=NO` | 4,224 | 79 | 5 | 0.707 | 0.669 | -3.0c [-5.7, -0.2]c | -4.9c [-7.6, -2.1]c | 0.011 | W1:-4.9 W2:-3.6 W3:-5.9 W4:-7.0 W5:-3.0 |
| `S15_availability_x_side|availability_state=EXPECTED_ACTIVE|stat=receiving_yards|side=NO` | 6,547 | 78 | 5 | 0.725 | 0.702 | -1.5c [-3.3, +0.5]c | -3.4c [-5.2, -1.4]c | 0.011 | W1:-4.3 W2:-2.1 W3:-3.3 W4:-4.6 W5:-2.5 |
| `S16_period_family_x_side_x_price|subfamily=TOTAL:4Q:total_points|side=NO|price_band=30-40c` | 58 | 54 | 5 | 0.343 | 0.172 | -14.3c [-24.3, -3.0]c | -18.6c [-28.8, -7.4]c | 0.014 | W1:-36.4 W2:-7.5 W3:-21.9 W4:-5.7 W5:-26.2 |
| `S01_side_x_price|side=NO|price_band=90-100c` | 13,268 | 79 | 5 | 0.950 | 0.934 | -0.1c [-1.3, +0.9]c | -1.9c [-3.1, -0.9]c | 0.015 | W1:-4.9 W2:-0.2 W3:-1.2 W4:-2.1 W5:-1.1 |
| `S18_family_x_side_x_mid|family=PLAYER_STAT|side=YES|mid_band=40-50c` | 2,205 | 79 | 5 | 0.474 | 0.447 | -0.5c [-3.2, +2.4]c | -4.4c [-6.9, -1.8]c | 0.015 | W1:-2.8 W2:-8.6 W3:-1.9 W4:-2.5 W5:-6.9 |
| `S09_player_stat_x_role_certainty|stat=receiving_yards|role_certainty=HIGH|side=NO` | 6,053 | 78 | 5 | 0.723 | 0.700 | -1.5c [-3.4, +0.5]c | -3.3c [-5.2, -1.3]c | 0.017 | W1:-4.1 W2:-2.5 W3:-2.8 W4:-3.8 W5:-3.3 |
| `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=10-20c` | 215 | 67 | 5 | 0.162 | 0.107 | -4.2c [-7.8, -0.1]c | -6.5c [-10.1, -2.4]c | 0.017 | W1:-7.1 W2:-8.9 W3:-8.2 W4:-5.4 W5:-0.4 |

## 6. Patterns that did NOT survive (rejected in discovery)

- UNSTABLE (a week or a held-out week flips the sign): 125 cells. Largest:
  - `S08_player_stat_x_side_x_price|stat=completions|side=NO|price_band=70-80c` -45.4c (21 games) — W1:-47.7 W2:-29.7 W3:-80.2 W5:+19.8
  - `S12_price_x_data_only_disagreement|data_only_disagreement_band=<2pp|side=NO|price_band=40-50c` -22.0c (30 games) — W1:-41.9 W2:+19.7 W3:-30.5 W4:-15.2
  - `S13_player_disagreement_x_side|stat=completions|player_disagreement_band=>10pp|side=NO` -21.1c (67 games) — W1:-29.7 W2:-21.7 W3:-11.8 W4:-8.2 W5:+5.4
  - `S08_player_stat_x_side_x_price|stat=attempts|side=NO|price_band=70-80c` -20.5c (64 games) — W1:-31.2 W2:+11.5 W3:-4.0 W4:-28.3 W5:-5.2
  - `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=80-90c` -20.2c (64 games) — W1:-33.8 W2:-11.9 W3:-15.1 W4:-0.0 W5:+10.8
  - `S12_price_x_data_only_disagreement|data_only_disagreement_band=<2pp|side=YES|price_band=50-60c` +19.0c (31 games) — W1:+36.8 W2:-16.4 W3:+18.4 W4:+17.8
  - `S16_period_family_x_side_x_price|subfamily=TOTAL:4Q:total_points|side=NO|price_band=20-30c` -16.7c (77 games) — W1:-22.8 W2:+0.6 W3:-25.8 W4:-20.8 W5:-19.0
  - `S14_move_x_side_x_price|move_band=down>5c|side=NO|price_band=70-80c` -16.6c (56 games) — W1:-27.3 W2:+4.5 W3:-9.9 W4:+2.3 W5:-2.8
  - `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=70-80c` -15.3c (74 games) — W1:-31.6 W2:+1.7 W3:-3.7 W4:+1.5 W5:-10.9
  - `S13_player_disagreement_x_side|stat=attempts|player_disagreement_band=>10pp|side=NO` -15.1c (71 games) — W1:-24.7 W2:-16.0 W3:-0.9 W4:-4.0 W5:+14.3
  - `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=90-100c` -13.7c (38 games) — W1:-22.3 W2:+3.6 W3:+6.5 W4:-13.4 W5:+8.1
  - `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=50-60c` -13.6c (59 games) — W1:-8.2 W2:-30.9 W3:+0.9 W4:-11.0 W5:-20.5
- NO_SIGNAL (interval includes zero): 973 cells. NOT_SIGNIFICANT_AFTER_MULTIPLICITY: 6 cells.

## 7. Ladders (one ladder = one thesis)

5,708 ladders with ≥ 3 live rungs at latest pregame. a ladder's realised best rung is one draw of one outcome; read the by-family shares across many ladders, never one ladder's winner.

| family | ladders | best realised = main rung | best CLV = main rung | incoherent | a rung ≥ 2c under the ladder's own fair curve |
|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 78 | 28.2% | 42.3% | 1 | 0 |
| PLAYER_STAT | 3655 | 18.1% | 34.8% | 114 | 0 |
| SPREAD | 1106 | 7.2% | 34.7% | 40 | 0 |
| TEAM_TOTAL | 316 | 9.5% | 18.0% | 101 | 18 |
| TOTAL | 553 | 11.6% | 18.1% | 54 | 0 |

## 8. Preregistered tests (discovery reading vs prospective reading)

| id | hypothesis | metric | discovery (W1–3) | prospective weeks | prospective value (family CI) | games | suggested |
|---|---|---|---|---|---|---|---|
| H-20261001-B01 | Full-game longshot YES underpriced at the mid | MID_BIAS (+) | 0.0372 [-0.0, +0.1] | [4, 5] | 0.0017 [-0.1, +0.1] | 31 | INCONCLUSIVE |
| H-20261001-B02 | Full-game YES at 60-70c overpriced at the mid | MID_BIAS (−) | -0.0635 [-0.2, +0.0] | [4, 5] | 0.0263 [-0.1, +0.2] | 31 | INCONCLUSIVE |
| H-20261001-B03 | Sides priced 90c+ lose after fees | RETURN_AT_ASK (−) | -0.0219 [-0.0, -0.0] | [4, 5] | -0.0133 [-0.0, +0.0] | 31 | INCONCLUSIVE |
| H-20261001-B04 | Modest DATA_ONLY disagreement predicts movement toward it | MOVE_TOWARD_MODEL (+) | 0.0823 [+0.0, +0.1] | [4, 5] | -0.0415 [-0.2, +0.1] | 16 | INCONCLUSIVE |
| H-20261001-B05 | Adjacent yardage rungs beat the main rung after fees | PAIRED_RUNG (+) | 0.0110 [-0.0, +0.0] | [4, 5] | 0.0321 [-0.0, +0.1] | 31 | INCONCLUSIVE |
| H-20261001-B06 | Team total beats spread as the expression of an offensive thesis | PAIRED_EXPRESSION (+) | 0.1046 [-0.1, +0.3] | [4, 5] | 0.0448 [-0.2, +0.3] | 21 | INCONCLUSIVE |
| H-20261001-B07 | Uncertain roles are priced worse than certain roles | EXCESS_BRIER_GAP (+) | -0.0046 [-0.0, +0.0] | [4, 5] | 0.0253 [-0.0, +0.1] | 28 | INCONCLUSIVE |
| H-20261001-B08 | Player-prop NO at 80c+ loses after fees | RETURN_AT_ASK (−) | -0.0304 [-0.0, -0.0] | [4, 5] | -0.0285 [-0.1, -0.0] | 31 | INCONCLUSIVE |
| H-20261001-B09 | Player-prop YES longshots lose after fees | RETURN_AT_ASK (−) | -0.0142 [-0.0, -0.0] | [4, 5] | 0.0047 [-0.0, +0.0] | 31 | INCONCLUSIVE |
| H-20261001-B10 | Chasing a pregame move loses | RETURN_AT_ASK (−) | -0.1009 [-0.1, -0.1] | [4, 5] | -0.0580 [-0.1, +0.0] | 30 | INCONCLUSIVE |
| H-20261001-B11 | A large incumbent player-model OVER view marks an underpriced YES | MID_BIAS (+) | 0.0784 [+0.0, +0.1] | [4, 5] | -0.0115 [-0.1, +0.1] | 30 | INCONCLUSIVE |

_Suggested statuses are suggestions; only the owner transitions the registry. Weeks 1–3 are never evidence for these hypotheses._

## 9. Patterns worth testing next (not registered)

- `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=YES|env_total_band=total41-45` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=YES|env_total_band=total45-49` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S18_family_x_side_x_mid|family=GAME_PLAYER_LEADER|side=YES|mid_band=10-20c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=NO|env_total_band=total45-49` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S02_family_x_side_x_price|family=GAME_PLAYER_LEADER|side=YES|price_band=10-20c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S16_period_family_x_side_x_price|subfamily=TOTAL:2H:total_points|side=NO|price_band=10-20c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S16_period_family_x_side_x_price|subfamily=GAME_PLAYER_LEADER:FULL:receiving_yards|side=YES|price_band=10-20c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=40-50c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S03_family_x_side_x_rung|family=SPREAD|side=NO|rung_offset_band=main` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S16_period_family_x_side_x_price|subfamily=TOTAL:2H:total_points|side=NO|price_band=20-30c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).

