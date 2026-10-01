# BOARD EDGE DISCOVERY — 2026 weeks 1–3 (cumulative)

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

_Inputs: board board-research-1.0.0, miner board-miner-1.0.0, script autopsy script-autopsy-1.0.0, weeks [1, 2, 3]; board rows 193,970_

## 1. Coverage — what was and was not analysed

| stage | contracts |
|---|---|
| discovered | 38,919 |
| mapped_to_game | 38,919 |
| captured_pregame | 37,069 |
| settled_any_source | 37,069 |
| football_settled | 29,508 |
| price_at_primary_horizon | 29,508 |
| executable_quote | 29,508 |
| fee_known | 29,492 |
| analyzed_primary | 29,450 |

Exclusions (every contract that left the funnel, by reason):

- 1,725 — captured_pregame: never quoted before kickoff
- 1,421 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_TEAM:FULL:first_td_team]
- 1,224 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_SCORER:FULL:first_td]
- 765 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [RACE_TO_N:FULL:race]
- 558 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_yards]
- 507 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:fantasy_points]
- 494 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_reception]
- 480 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_sacks]
- 384 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:field_goals]
- 303 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:receiving_yards]
- 215 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_rush]
- 199 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_touchdowns]
- 198 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TOTAL_TD:FULL:total_touchdowns]
- 144 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:rushing_yards]
- 125 — captured_pregame: discovered, never in a pregame capture row (series outside the capture tiers, or listed only after kickoff)
- 101 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:touchdowns]
- 96 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:fantasy_points]
- 90 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:touchdowns]
- 79 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receiving_yards]
- 48 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:defensive_st_td]
- 48 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:btts]
- 48 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:overtime]
- 47 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:safety]
- 42 — analyzed_primary: football settlement contradicted by the exchange's terminal result (flagged, never resolved)
- 41 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receptions]
- 33 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rushing_yards]
- 16 — fee_known: fee unknown
- 11 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:attempts]
- 11 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:completions]
- 7 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:passing_yards]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:interceptions]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:passing_tds]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rush_rec_yards]

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

## 2. How to read the cells

Unit = one contract SIDE bought at its executable ask. **mid bias** = event rate − the side's mid (is the market's fair price wrong?). **return** = payout − ask − fee per contract (is it exploitable after costs?). Intervals are game-clustered bootstrap (B=2000); rare-outcome cells also get a binomial floor. Cells with < 20 games, < 2 weeks or < 40 sides are DESCRIPTIVE_ONLY. Multiplicity: Benjamini–Hochberg q ≤ 0.2 across all 1024 tested cells (≈51.2 would exclude zero by chance alone).

Status counts at latest pregame: CANDIDATE 89, DESCRIPTIVE_ONLY 677, NOT_SIGNIFICANT_AFTER_MULTIPLICITY 41, NO_SIGNAL 845, UNSTABLE 49.

## 3. Price bands

### Five full-game families, YES side, binned by QUOTED MID (the owner's Weeks 1–3 framing)

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| YES | 00-10c | 634 | 48 | 0.058 | 0.057 | -0.1c [-2.9, +3.4]c | -1.4c [-4.3, +2.1]c | W1:+2.8 W2:-5.1 W3:-0.3 | NO_SIGNAL |
| YES | 10-20c | 552 | 48 | 0.147 | 0.190 | +4.4c [-1.0, +9.9]c | +2.7c [-2.6, +8.2]c | W1:+6.8 W2:+4.0 W3:-0.0 | NO_SIGNAL |
| YES | 20-30c | 428 | 48 | 0.247 | 0.276 | +2.9c [-2.8, +8.6]c | +0.9c [-4.8, +6.7]c | W1:+6.0 W2:-0.2 W3:+0.9 | NO_SIGNAL |
| YES | 30-40c | 403 | 48 | 0.352 | 0.370 | +1.8c [-4.5, +8.3]c | -0.6c [-6.8, +5.8]c | W1:+7.4 W2:-2.6 W3:-2.4 | NO_SIGNAL |
| YES | 40-50c | 384 | 48 | 0.449 | 0.432 | -1.7c [-10.1, +6.7]c | -4.2c [-12.5, +4.1]c | W1:+0.1 W2:-8.9 W3:+0.7 | NO_SIGNAL |
| YES | 50-60c | 346 | 48 | 0.545 | 0.581 | +3.5c [-5.4, +12.0]c | +1.0c [-8.0, +9.4]c | W1:+8.2 W2:-3.0 W3:+2.2 | NO_SIGNAL |
| YES | 60-70c | 252 | 48 | 0.647 | 0.583 | -6.3c [-15.5, +3.1]c | -9.1c [-18.2, +0.2]c | W1:-1.5 W2:-15.1 W3:-5.5 | NO_SIGNAL |
| YES | 70-80c | 193 | 48 | 0.750 | 0.710 | -4.0c [-14.2, +5.6]c | -6.1c [-16.2, +3.5]c | W1:-3.7 W2:-14.6 W3:+5.1 | NO_SIGNAL |
| YES | 80-90c | 207 | 48 | 0.852 | 0.855 | +0.3c [-7.3, +6.8]c | -1.4c [-8.9, +5.1]c | W1:-1.3 W2:-6.4 W3:+6.3 | NO_SIGNAL |
| YES | 90-100c | 326 | 48 | 0.947 | 0.923 | -2.4c [-7.1, +1.7]c | -3.5c [-8.3, +0.6]c | W1:-0.9 W2:-9.2 W3:+0.5 | NO_SIGNAL |

### Whole board, binned by the ASK actually paid

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| NO | 00-10c | 575 | 48 | 0.057 | 0.056 | +0.7c [-2.3, +4.5]c | -0.5c [-3.6, +3.3]c | W1:-0.2 W2:+3.2 W3:-3.2 | NO_SIGNAL |
| NO | 10-20c | 1,090 | 48 | 0.151 | 0.132 | -0.4c [-3.5, +3.3]c | -2.8c [-5.9, +0.9]c | W1:-3.5 W2:+0.8 W3:-3.1 | NO_SIGNAL |
| NO | 20-30c | 1,458 | 48 | 0.246 | 0.212 | -1.6c [-5.0, +2.3]c | -4.7c [-8.2, -0.8]c | W1:-6.7 W2:+2.5 W3:-6.3 | UNSTABLE |
| NO | 30-40c | 1,532 | 48 | 0.345 | 0.330 | -0.0c [-3.9, +4.1]c | -3.2c [-7.1, +1.0]c | W1:-1.7 W2:+0.7 W3:-3.7 | NO_SIGNAL |
| NO | 40-50c | 1,979 | 48 | 0.449 | 0.453 | +1.6c [-2.2, +5.9]c | -1.3c [-5.1, +3.1]c | W1:-3.0 W2:+5.3 W3:-0.9 | NO_SIGNAL |
| NO | 50-60c | 2,704 | 48 | 0.544 | 0.548 | +1.5c [-2.8, +5.9]c | -1.3c [-5.6, +3.2]c | W1:-4.0 W2:+7.3 W3:-1.4 | NO_SIGNAL |
| NO | 60-70c | 2,708 | 48 | 0.646 | 0.628 | -0.4c [-3.2, +2.3]c | -3.3c [-6.2, -0.6]c | W1:-3.8 W2:+0.5 W3:-1.5 | CANDIDATE |
| NO | 70-80c | 3,417 | 48 | 0.750 | 0.714 | -1.2c [-3.9, +1.3]c | -4.9c [-8.0, -2.0]c | W1:-9.2 W2:+0.5 W3:-1.4 | CANDIDATE |
| NO | 80-90c | 4,650 | 48 | 0.850 | 0.820 | -1.2c [-3.6, +1.0]c | -3.9c [-6.4, -1.6]c | W1:-6.4 W2:-0.2 W3:-2.1 | CANDIDATE |
| NO | 90-100c | 8,141 | 48 | 0.952 | 0.934 | +0.0c [-1.6, +1.4]c | -2.1c [-3.9, -0.7]c | W1:-4.6 W2:+0.2 W3:-0.8 | CANDIDATE |
| YES | 00-10c | 6,684 | 48 | 0.055 | 0.042 | -0.2c [-1.1, +1.0]c | -1.6c [-2.6, -0.4]c | W1:+0.1 W2:-2.5 W3:-1.4 | CANDIDATE |
| YES | 10-20c | 5,420 | 48 | 0.142 | 0.132 | +0.6c [-1.4, +2.8]c | -1.8c [-3.8, +0.4]c | W1:+0.0 W2:-2.5 W3:-0.5 | NO_SIGNAL |
| YES | 20-30c | 3,847 | 48 | 0.242 | 0.225 | +0.1c [-2.1, +2.6]c | -3.0c [-5.3, -0.5]c | W1:-1.9 W2:-2.8 W3:-0.5 | CANDIDATE |
| YES | 30-40c | 2,946 | 48 | 0.343 | 0.336 | +1.0c [-1.5, +3.6]c | -2.4c [-4.9, +0.1]c | W1:-0.0 W2:-2.8 W3:+0.3 | NO_SIGNAL |
| YES | 40-50c | 2,829 | 48 | 0.445 | 0.417 | -1.3c [-5.1, +2.5]c | -4.5c [-8.2, -0.7]c | W1:-0.8 W2:-6.1 W3:-2.0 | CANDIDATE |
| YES | 50-60c | 2,255 | 48 | 0.539 | 0.510 | -1.8c [-6.0, +2.2]c | -4.7c [-8.8, -0.7]c | W1:+0.6 W2:-8.7 W3:-0.8 | NOT_SIGNIFICANT_AFTER_MULTIPLICITY |
| YES | 60-70c | 1,567 | 48 | 0.644 | 0.616 | -0.6c [-5.6, +4.0]c | -4.4c [-9.1, +0.1]c | W1:-3.6 W2:-6.4 W3:+1.7 | NO_SIGNAL |
| YES | 70-80c | 1,491 | 48 | 0.745 | 0.732 | +1.5c [-2.8, +5.6]c | -2.7c [-6.7, +1.1]c | W1:-1.3 W2:-5.0 W3:+2.4 | NO_SIGNAL |
| YES | 80-90c | 1,379 | 48 | 0.843 | 0.840 | +3.3c [-0.6, +6.9]c | -1.1c [-4.8, +2.0]c | W1:+0.3 W2:-4.3 W3:+3.4 | NO_SIGNAL |
| YES | 90-100c | 1,004 | 48 | 0.949 | 0.925 | +1.0c [-2.2, +3.8]c | -2.7c [-6.1, +0.2]c | W1:-2.8 W2:-4.1 W3:-0.2 | NO_SIGNAL |

## 4. Market families

| family | contract-sides | mean return at the ask |
|---|---|---|
| PLAYER_STAT | 31,140 | -2.8c |
| SPREAD | 9,532 | -2.5c |
| TOTAL | 8,226 | -2.8c |
| TEAM_TOTAL | 4,602 | -2.8c |
| PERIOD_WINNER | 1,724 | -2.3c |
| HALF_FULL_RESULT | 677 | -2.2c |
| WIN_MARGIN_BUCKET | 613 | -3.5c |
| BOTH_TEAMS_SCORE | 384 | -3.3c |
| BOTH_TEAMS_SCORE_N | 361 | -5.5c |
| GAME_PLAYER_LEADER | 225 | -9.8c |
| GAME_WINNER | 192 | -2.0c |

## 5. Conditional patterns that survived every safeguard (CANDIDATE) — discovery only

89 CANDIDATE cells at latest pregame. Negative returns dominate: most survivors are COST (half-spread + fee) or favourite–longshot effects, not hidden value. Mid bias says which are mispricing.

| cell | sides | games | weeks | price | event | mid bias (CI) | return (CI) | q | by week |
|---|---|---|---|---|---|---|---|---|---|
| `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=80-90c` | 132 | 39 | 3 | 0.859 | 0.583 | -15.1c [-21.5, -7.7]c | -28.4c [-35.2, -19.4]c | 0.000 | W1:-33.8 W2:-11.9 W3:-15.1 |
| `S14_move_x_side_x_price|move_band=up2-5c|side=NO|price_band=80-90c` | 683 | 47 | 3 | 0.852 | 0.779 | -4.2c [-6.7, -1.6]c | -8.2c [-11.1, -5.3]c | 0.000 | W1:-11.1 W2:-3.6 W3:-9.9 |
| `S13_player_disagreement_x_side|stat=completions|player_disagreement_band=>10pp|side=NO` | 215 | 39 | 3 | 0.774 | 0.521 | -11.8c [-21.9, -2.5]c | -26.3c [-36.8, -16.2]c | 0.000 | W1:-29.7 W2:-21.7 W3:-11.8 |
| `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=40-50c` | 173 | 44 | 3 | 0.438 | 0.283 | -11.5c [-17.8, -4.8]c | -17.2c [-23.7, -10.2]c | 0.000 | W1:-16.7 W2:-19.5 W3:-16.8 |
| `S08_player_stat_x_side_x_price|stat=receptions|side=YES|price_band=00-10c` | 1,133 | 48 | 3 | 0.057 | 0.038 | -0.5c [-1.6, +0.6]c | -2.3c [-3.4, -1.2]c | 0.006 | W1:-2.9 W2:-2.4 W3:-1.6 |
| `S02_family_x_side_x_price|family=WIN_MARGIN_BUCKET|side=NO|price_band=90-100c` | 108 | 48 | 3 | 0.945 | 0.843 | -6.5c [-11.9, -1.4]c | -10.6c [-16.0, -5.5]c | 0.007 | W1:-13.9 W2:-10.4 W3:-3.1 |
| `S16_period_family_x_side_x_price|subfamily=WIN_MARGIN_BUCKET:FULL:margin|side=NO|price_band=90-100c` | 108 | 48 | 3 | 0.945 | 0.843 | -6.5c [-11.9, -1.4]c | -10.6c [-16.0, -5.5]c | 0.007 | W1:-13.9 W2:-10.4 W3:-3.1 |
| `S06_teamtotal_x_role_x_side|team_role=UNDERDOG|side=YES|price_band=00-10c` | 261 | 47 | 3 | 0.053 | 0.019 | -2.1c [-3.8, -0.0]c | -3.7c [-5.4, -1.6]c | 0.012 | W1:-4.1 W2:-4.7 W3:-2.5 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=80-90c` | 2,496 | 48 | 3 | 0.851 | 0.812 | -1.7c [-4.1, +0.5]c | -4.8c [-7.3, -2.3]c | 0.015 | W1:-7.6 W2:-1.4 W3:-4.7 |
| `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=10-20c` | 145 | 42 | 3 | 0.160 | 0.090 | -5.5c [-9.6, -1.0]c | -8.0c [-11.9, -3.6]c | 0.015 | W1:-7.1 W2:-8.9 W3:-8.2 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=70-80c` | 1,713 | 48 | 3 | 0.752 | 0.691 | -2.6c [-5.9, +0.6]c | -7.3c [-11.5, -3.3]c | 0.021 | W1:-15.0 W2:-0.6 W3:-4.2 |
| `S09_player_stat_x_role_certainty|stat=completions|role_certainty=HIGH|side=NO` | 480 | 47 | 3 | 0.619 | 0.481 | -6.0c [-13.0, +1.8]c | -15.0c [-22.6, -6.3]c | 0.021 | W1:-18.7 W2:-6.9 W3:-10.4 |
| `S13_player_disagreement_x_side|stat=attempts|player_disagreement_band=>10pp|side=NO` | 241 | 43 | 3 | 0.772 | 0.577 | -7.1c [-17.7, +3.4]c | -20.5c [-31.9, -8.9]c | 0.021 | W1:-24.7 W2:-16.0 W3:-0.9 |
| `S15_availability_x_side|availability_state=EXPECTED_ACTIVE|stat=completions|side=NO` | 480 | 47 | 3 | 0.619 | 0.481 | -6.0c [-13.0, +1.8]c | -15.0c [-22.6, -6.3]c | 0.021 | W1:-18.7 W2:-6.9 W3:-10.4 |
| `S16_period_family_x_side_x_price|subfamily=SPREAD:2Q:margin|side=YES|price_band=10-20c` | 129 | 48 | 3 | 0.145 | 0.062 | -6.5c [-11.1, -1.0]c | -9.2c [-13.8, -3.6]c | 0.021 | W1:-12.7 W2:-10.5 W3:-5.4 |
| `S16_period_family_x_side_x_price|subfamily=TOTAL:2H:total_points|side=NO|price_band=10-20c` | 93 | 47 | 3 | 0.136 | 0.032 | -6.7c [-9.7, -2.5]c | -11.2c [-14.4, -1.7]c | 0.021 | W1:-14.1 W2:-8.0 W3:-11.0 |
| `S08_player_stat_x_side_x_price|stat=receptions|side=YES|price_band=50-60c` | 241 | 48 | 3 | 0.544 | 0.465 | -7.4c [-12.9, -2.0]c | -9.7c [-15.3, -4.3]c | 0.026 | W1:-6.3 W2:-7.8 W3:-15.9 |
| `S11_player_position_x_stat|position=QB|stat=completions|side=NO` | 502 | 48 | 3 | 0.615 | 0.484 | -5.5c [-13.1, +1.8]c | -14.3c [-22.6, -5.9]c | 0.030 | W1:-17.6 W2:-6.6 W3:-10.4 |
| `S13_player_disagreement_x_side|stat=receiving_yards|player_disagreement_band=5-10pp|side=NO` | 827 | 47 | 3 | 0.767 | 0.732 | -2.6c [-5.1, +0.0]c | -4.5c [-7.1, -1.9]c | 0.030 | W1:-4.2 W2:-6.1 W3:-3.4 |
| `S16_period_family_x_side_x_price|subfamily=TOTAL:2H:total_points|side=NO|price_band=20-30c` | 54 | 43 | 3 | 0.246 | 0.111 | -9.0c [-16.6, +0.5]c | -14.8c [-22.5, -4.8]c | 0.041 | W1:-22.0 W2:-6.7 W3:-10.9 |
| `S03_family_x_side_x_rung|family=SPREAD|side=NO|rung_offset_band=main` | 670 | 48 | 3 | 0.620 | 0.600 | -0.7c [-2.8, +1.5]c | -3.6c [-5.7, -1.4]c | 0.041 | W1:-3.7 W2:-3.1 W3:-3.9 |
| `S11_player_position_x_stat|position=RB|stat=rush_rec_yards|side=YES` | 384 | 48 | 3 | 0.322 | 0.253 | -2.9c [-8.1, +2.3]c | -8.2c [-13.2, -3.4]c | 0.042 | W1:-7.2 W2:-10.0 W3:-7.3 |
| `S01_side_x_price|side=NO|price_band=70-80c` | 3,417 | 48 | 3 | 0.750 | 0.714 | -1.2c [-3.9, +1.3]c | -4.9c [-8.0, -2.0]c | 0.043 | W1:-10.5 W2:-0.8 W3:-2.7 |
| `S01_side_x_price|side=NO|price_band=80-90c` | 4,650 | 48 | 3 | 0.850 | 0.820 | -1.2c [-3.6, +1.0]c | -3.9c [-6.4, -1.6]c | 0.043 | W1:-7.3 W2:-1.1 W3:-3.0 |
| `S03_family_x_side_x_rung|family=PLAYER_STAT|side=NO|rung_offset_band=adjacent+1` | 2,683 | 48 | 3 | 0.779 | 0.751 | -1.0c [-3.4, +1.2]c | -3.9c [-6.3, -1.5]c | 0.043 | W1:-6.7 W2:-1.1 W3:-3.8 |
| `S03_family_x_side_x_rung|family=PLAYER_STAT|side=NO|rung_offset_band=far-` | 1,377 | 48 | 3 | 0.263 | 0.204 | -2.6c [-6.3, +1.4]c | -7.1c [-11.3, -2.6]c | 0.043 | W1:-12.9 W2:-0.3 W3:-4.3 |
| `S04_rung_x_price_x_side|rung_offset_band=adjacent+1|price_band=90-100c|side=NO` | 660 | 48 | 3 | 0.964 | 0.929 | -1.4c [-3.7, +0.6]c | -3.8c [-6.2, -1.5]c | 0.043 | W1:-6.3 W2:-4.3 W3:-0.1 |
| `S11_player_position_x_stat|position=WR|stat=receiving_yards|side=NO` | 2,555 | 48 | 3 | 0.712 | 0.675 | -2.7c [-5.6, +0.1]c | -4.8c [-7.7, -1.9]c | 0.043 | W1:-4.9 W2:-3.6 W3:-5.9 |
| `S18_family_x_side_x_mid|family=WIN_MARGIN_BUCKET|side=NO|mid_band=80-90c` | 129 | 47 | 3 | 0.877 | 0.814 | -3.2c [-7.4, +0.8]c | -7.0c [-11.4, -2.8]c | 0.043 | W1:-10.1 W2:-5.8 W3:-4.9 |
| `S04_rung_x_price_x_side|rung_offset_band=far+|price_band=00-10c|side=YES` | 5,130 | 48 | 3 | 0.059 | 0.043 | -0.4c [-1.5, +1.0]c | -2.0c [-3.1, -0.6]c | 0.050 | W1:-0.2 W2:-3.5 W3:-2.2 |
| `S04_rung_x_price_x_side|rung_offset_band=adjacent+1|price_band=80-90c|side=NO` | 593 | 48 | 3 | 0.843 | 0.788 | -3.1c [-7.4, +0.8]c | -6.4c [-10.6, -2.4]c | 0.055 | W1:-13.1 W2:-0.7 W3:-6.3 |
| `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=20-30c` | 291 | 47 | 3 | 0.244 | 0.179 | -4.3c [-8.9, +0.9]c | -7.8c [-12.5, -2.6]c | 0.055 | W1:-10.8 W2:-7.7 W3:-0.8 |
| `S08_player_stat_x_side_x_price|stat=rush_rec_yards|side=YES|price_band=20-30c` | 57 | 35 | 3 | 0.252 | 0.140 | -7.3c [-14.9, +0.5]c | -12.5c [-20.5, -4.4]c | 0.055 | W1:-26.4 W2:-9.8 W3:-8.5 |
| `S18_family_x_side_x_mid|family=PLAYER_STAT|side=NO|mid_band=80-90c` | 2,528 | 48 | 3 | 0.867 | 0.837 | -1.4c [-3.9, +0.8]c | -3.8c [-6.2, -1.4]c | 0.055 | W1:-4.8 W2:-2.2 W3:-4.2 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=20-30c` | 881 | 48 | 3 | 0.246 | 0.209 | -2.3c [-5.4, +1.0]c | -5.0c [-8.2, -1.7]c | 0.056 | W1:-6.8 W2:-1.8 W3:-6.6 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=90-100c` | 4,964 | 48 | 3 | 0.953 | 0.935 | -0.3c [-1.7, +0.9]c | -2.2c [-3.7, -0.9]c | 0.056 | W1:-4.4 W2:-0.7 W3:-1.2 |
| `S01_side_x_price|side=YES|price_band=00-10c` | 6,684 | 48 | 3 | 0.055 | 0.042 | -0.2c [-1.1, +1.0]c | -1.6c [-2.6, -0.4]c | 0.056 | W1:-0.2 W2:-2.8 W3:-1.8 |
| `S16_period_family_x_side_x_price|subfamily=TEAM_TOTAL:1H:team_points|side=YES|price_band=20-30c` | 141 | 48 | 3 | 0.239 | 0.142 | -4.9c [-11.6, +2.4]c | -10.9c [-17.6, -3.3]c | 0.058 | W1:-6.5 W2:-18.5 W3:-8.5 |
| `S08_player_stat_x_side_x_price|stat=attempts|side=NO|price_band=90-100c` | 58 | 24 | 2 | 0.979 | 0.759 | -6.9c [-21.9, +6.3]c | -22.1c [-37.5, -8.8]c | 0.065 | W1:-22.7 W2:-19.0 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=YES|price_band=00-10c` | 4,412 | 48 | 3 | 0.054 | 0.043 | -0.0c [-0.9, +1.0]c | -1.4c [-2.3, -0.4]c | 0.066 | W1:-0.5 W2:-2.3 W3:-1.4 |

## 6. Patterns that did NOT survive (rejected in discovery)

- UNSTABLE (a week or a held-out week flips the sign): 49 cells. Largest:
  - `S12_price_x_data_only_disagreement|data_only_disagreement_band=<2pp|side=NO|price_band=40-50c` -23.4c (24 games) — W1:-41.9 W2:+19.7 W3:-30.5
  - `S08_player_stat_x_side_x_price|stat=attempts|side=NO|price_band=70-80c` -22.2c (37 games) — W1:-31.2 W2:+11.5 W3:-4.0
  - `S14_move_x_side_x_price|move_band=down>5c|side=NO|price_band=70-80c` -20.8c (36 games) — W1:-27.3 W2:+4.5 W3:-9.9
  - `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=70-80c` -19.7c (45 games) — W1:-31.6 W2:+1.7 W3:-3.7
  - `S13_player_disagreement_x_side|stat=carries|player_disagreement_band=5-10pp|side=NO` -19.5c (33 games) — W1:-27.0 W2:-10.8 W3:+3.5
  - `S12_price_x_data_only_disagreement|data_only_disagreement_band=<2pp|side=YES|price_band=50-60c` +19.2c (26 games) — W1:+36.8 W2:-16.4 W3:+18.4
  - `S12_price_x_data_only_disagreement|data_only_disagreement_band=2-5pp|side=YES|price_band=40-50c` +16.9c (34 games) — W1:+23.9 W2:-2.5 W3:+22.7
  - `S12_price_x_data_only_disagreement|data_only_disagreement_band=5-10pp|side=YES|price_band=70-80c` -15.5c (31 games) — W1:-21.3 W2:-27.3 W3:+8.1
  - `S14_move_x_side_x_price|move_band=down>5c|side=NO|price_band=50-60c` -15.4c (31 games) — W1:-21.7 W2:+4.5 W3:-22.7
  - `S16_period_family_x_side_x_price|subfamily=TOTAL:4Q:total_points|side=YES|price_band=40-50c` -15.3c (45 games) — W1:-25.6 W2:-23.4 W3:+3.9
  - `S16_period_family_x_side_x_price|subfamily=TOTAL:4Q:total_points|side=NO|price_band=20-30c` -14.9c (47 games) — W1:-22.8 W2:+0.6 W3:-25.8
  - `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=90-100c` -14.9c (27 games) — W1:-22.3 W2:+3.6 W3:+6.5
- NO_SIGNAL (interval includes zero): 845 cells. NOT_SIGNIFICANT_AFTER_MULTIPLICITY: 41 cells.

## 7. Ladders (one ladder = one thesis)

3,424 ladders with ≥ 3 live rungs at latest pregame. a ladder's realised best rung is one draw of one outcome; read the by-family shares across many ladders, never one ladder's winner.

| family | ladders | best realised = main rung | best CLV = main rung | incoherent | a rung ≥ 2c under the ladder's own fair curve |
|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 48 | 25.0% | 33.3% | 1 | 0 |
| PLAYER_STAT | 2176 | 17.9% | 32.9% | 112 | 0 |
| SPREAD | 672 | 7.7% | 36.8% | 33 | 0 |
| TEAM_TOTAL | 192 | 8.3% | 15.1% | 82 | 18 |
| TOTAL | 336 | 11.6% | 17.6% | 53 | 0 |

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

- `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=80-90c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S14_move_x_side_x_price|move_band=up2-5c|side=NO|price_band=80-90c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S13_player_disagreement_x_side|stat=completions|player_disagreement_band=>10pp|side=NO` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=40-50c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S08_player_stat_x_side_x_price|stat=receptions|side=YES|price_band=00-10c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S02_family_x_side_x_price|family=WIN_MARGIN_BUCKET|side=NO|price_band=90-100c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S16_period_family_x_side_x_price|subfamily=WIN_MARGIN_BUCKET:FULL:margin|side=NO|price_band=90-100c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S06_teamtotal_x_role_x_side|team_role=UNDERDOG|side=YES|price_band=00-10c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=80-90c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=10-20c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).

