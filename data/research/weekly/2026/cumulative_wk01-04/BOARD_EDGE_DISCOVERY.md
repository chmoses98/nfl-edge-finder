# BOARD EDGE DISCOVERY — 2026 weeks 1–4 (cumulative)

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

_Inputs: board board-research-1.0.0, miner board-miner-1.0.0, script autopsy script-autopsy-1.0.0, weeks [1, 2, 3, 4]; board rows 258,705_

## 1. Coverage — what was and was not analysed

| stage | contracts |
|---|---|
| discovered | 51,974 |
| mapped_to_game | 51,974 |
| captured_pregame | 49,279 |
| settled_any_source | 49,279 |
| football_settled | 39,453 |
| price_at_primary_horizon | 39,453 |
| executable_quote | 39,453 |
| fee_known | 39,437 |
| analyzed_primary | 39,364 |

Exclusions (every contract that left the funnel, by reason):

- 2,462 — captured_pregame: never quoted before kickoff
- 1,910 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_TEAM:FULL:first_td_team]
- 1,660 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_SCORER:FULL:first_td]
- 1,005 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [RACE_TO_N:FULL:race]
- 718 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_yards]
- 670 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:fantasy_points]
- 669 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_reception]
- 640 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_sacks]
- 512 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:field_goals]
- 303 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:receiving_yards]
- 294 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_rush]
- 233 — captured_pregame: discovered, never in a pregame capture row (series outside the capture tiers, or listed only after kickoff)
- 199 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_touchdowns]
- 198 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TOTAL_TD:FULL:total_touchdowns]
- 144 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:rushing_yards]
- 136 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:touchdowns]
- 128 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:fantasy_points]
- 124 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receiving_yards]
- 118 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:touchdowns]
- 73 — analyzed_primary: football settlement contradicted by the exchange's terminal result (flagged, never resolved)
- 64 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:defensive_st_td]
- 64 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:btts]
- 64 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:overtime]
- 63 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:safety]
- 61 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receptions]
- 44 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rushing_yards]
- 16 — fee_known: fee unknown
- 11 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:attempts]
- 11 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:completions]
- 7 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:passing_yards]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:interceptions]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:passing_tds]
- 3 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:rush_rec_yards]

Discovery universe: GAME_NOT_IN_REG_SCHEDULE (preseason / prior season) 10,294 · GAME_OTHER_WEEKS 14,569 · GAME_TARGET_WEEKS 51,974 · NON_GAME (season / futures / awards / leaders) 25,572

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

## 2. How to read the cells

Unit = one contract SIDE bought at its executable ask. **mid bias** = event rate − the side's mid (is the market's fair price wrong?). **return** = payout − ask − fee per contract (is it exploitable after costs?). Intervals are game-clustered bootstrap (B=2000); rare-outcome cells also get a binomial floor. Cells with < 20 games, < 2 weeks or < 40 sides are DESCRIPTIVE_ONLY. Multiplicity: Benjamini–Hochberg q ≤ 0.2 across all 1155 tested cells (≈57.8 would exclude zero by chance alone).

Status counts at latest pregame: CANDIDATE 115, DESCRIPTIVE_ONLY 577, NOT_SIGNIFICANT_AFTER_MULTIPLICITY 26, NO_SIGNAL 932, UNSTABLE 82.

## 3. Price bands

### Five full-game families, YES side, binned by QUOTED MID (the owner's Weeks 1–3 framing)

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| YES | 00-10c | 833 | 64 | 0.057 | 0.049 | -0.8c [-3.0, +1.9]c | -2.1c [-4.3, +0.6]c | W1:+2.8 W2:-5.1 W3:-0.3 W4:-3.9 | NO_SIGNAL |
| YES | 10-20c | 744 | 64 | 0.146 | 0.168 | +2.2c [-2.1, +6.9]c | +0.5c [-3.7, +5.3]c | W1:+6.8 W2:+4.0 W3:-0.0 W4:-4.7 | NO_SIGNAL |
| YES | 20-30c | 571 | 64 | 0.247 | 0.268 | +2.1c [-2.7, +7.2]c | +0.2c [-4.7, +5.2]c | W1:+6.0 W2:-0.2 W3:+0.9 W4:-0.6 | NO_SIGNAL |
| YES | 30-40c | 529 | 64 | 0.351 | 0.359 | +0.8c [-4.8, +6.4]c | -1.5c [-7.1, +4.0]c | W1:+7.4 W2:-2.6 W3:-2.4 W4:-2.8 | NO_SIGNAL |
| YES | 40-50c | 509 | 64 | 0.449 | 0.444 | -0.5c [-7.7, +6.4]c | -3.0c [-10.1, +3.9]c | W1:+0.1 W2:-8.9 W3:+0.7 W4:+2.7 | NO_SIGNAL |
| YES | 50-60c | 465 | 64 | 0.546 | 0.578 | +3.2c [-4.5, +10.4]c | +0.7c [-7.0, +7.9]c | W1:+8.2 W2:-3.0 W3:+2.2 W4:+1.7 | NO_SIGNAL |
| YES | 60-70c | 331 | 64 | 0.646 | 0.604 | -4.1c [-12.1, +4.0]c | -6.8c [-14.6, +1.2]c | W1:-1.5 W2:-15.1 W3:-5.5 W4:+2.3 | NO_SIGNAL |
| YES | 70-80c | 265 | 64 | 0.749 | 0.732 | -1.6c [-9.7, +5.9]c | -3.7c [-11.6, +3.9]c | W1:-3.7 W2:-14.6 W3:+5.1 W4:+4.0 | NO_SIGNAL |
| YES | 80-90c | 280 | 64 | 0.852 | 0.879 | +2.7c [-2.8, +7.5]c | +1.0c [-4.4, +5.9]c | W1:-1.3 W2:-6.4 W3:+6.3 W4:+8.9 | NO_SIGNAL |
| YES | 90-100c | 438 | 64 | 0.948 | 0.943 | -0.5c [-4.3, +2.7]c | -1.5c [-5.4, +1.6]c | W1:-0.9 W2:-9.2 W3:+0.5 W4:+4.5 | NO_SIGNAL |

### Whole board, binned by the ASK actually paid

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| NO | 00-10c | 789 | 64 | 0.057 | 0.044 | -0.4c [-2.7, +2.5]c | -1.6c [-4.0, +1.3]c | W1:-0.2 W2:+3.2 W3:-3.2 W4:-4.2 | NO_SIGNAL |
| NO | 10-20c | 1,494 | 64 | 0.150 | 0.127 | -1.0c [-3.6, +1.8]c | -3.3c [-5.9, -0.5]c | W1:-3.5 W2:+0.8 W3:-3.1 W4:-3.8 | CANDIDATE |
| NO | 20-30c | 1,958 | 64 | 0.245 | 0.219 | -1.0c [-4.0, +2.0]c | -3.9c [-6.9, -0.8]c | W1:-6.7 W2:+2.5 W3:-6.3 W4:-0.4 | UNSTABLE |
| NO | 30-40c | 2,020 | 64 | 0.346 | 0.329 | -0.4c [-3.6, +2.9]c | -3.3c [-6.5, -0.1]c | W1:-1.7 W2:+0.7 W3:-3.7 W4:-2.1 | NOT_SIGNIFICANT_AFTER_MULTIPLICITY |
| NO | 40-50c | 2,650 | 64 | 0.449 | 0.452 | +1.3c [-2.2, +4.9]c | -1.4c [-4.9, +2.2]c | W1:-3.0 W2:+5.3 W3:-0.9 W4:-0.2 | NO_SIGNAL |
| NO | 50-60c | 3,561 | 64 | 0.544 | 0.548 | +1.3c [-2.4, +4.8]c | -1.4c [-5.1, +2.1]c | W1:-4.0 W2:+7.3 W3:-1.4 W4:-0.0 | NO_SIGNAL |
| NO | 60-70c | 3,617 | 64 | 0.646 | 0.630 | -0.4c [-3.0, +2.0]c | -3.2c [-5.7, -0.7]c | W1:-3.8 W2:+0.5 W3:-1.5 W4:-1.0 | CANDIDATE |
| NO | 70-80c | 4,540 | 64 | 0.749 | 0.716 | -1.4c [-3.7, +0.9]c | -4.6c [-7.1, -2.1]c | W1:-9.2 W2:+0.5 W3:-1.4 W4:-2.6 | CANDIDATE |
| NO | 80-90c | 6,297 | 64 | 0.849 | 0.820 | -1.4c [-3.3, +0.4]c | -3.8c [-5.9, -2.0]c | W1:-6.4 W2:-0.2 W3:-2.1 W4:-2.8 | CANDIDATE |
| NO | 90-100c | 10,800 | 64 | 0.951 | 0.933 | -0.2c [-1.4, +0.9]c | -2.1c [-3.4, -1.0]c | W1:-4.6 W2:+0.2 W3:-0.8 W4:-1.8 | CANDIDATE |
| YES | 00-10c | 9,167 | 64 | 0.055 | 0.045 | +0.1c [-0.7, +0.9]c | -1.4c [-2.1, -0.5]c | W1:+0.1 W2:-2.5 W3:-1.4 W4:-0.2 | CANDIDATE |
| YES | 10-20c | 7,287 | 64 | 0.142 | 0.134 | +0.6c [-0.9, +2.3]c | -1.6c [-3.2, +0.1]c | W1:+0.0 W2:-2.5 W3:-0.5 W4:-0.1 | NO_SIGNAL |
| YES | 20-30c | 5,108 | 64 | 0.242 | 0.235 | +0.8c [-1.1, +2.9]c | -2.0c [-4.0, +0.1]c | W1:-1.9 W2:-2.8 W3:-0.5 W4:+2.2 | NO_SIGNAL |
| YES | 30-40c | 3,912 | 64 | 0.344 | 0.337 | +0.9c [-1.3, +3.3]c | -2.3c [-4.4, +0.1]c | W1:-0.0 W2:-2.8 W3:+0.3 W4:-0.4 | NO_SIGNAL |
| YES | 40-50c | 3,692 | 64 | 0.445 | 0.420 | -1.1c [-4.2, +1.9]c | -4.2c [-7.2, -1.1]c | W1:-0.8 W2:-6.1 W3:-2.0 W4:-1.5 | CANDIDATE |
| YES | 50-60c | 3,002 | 64 | 0.540 | 0.512 | -1.7c [-5.2, +1.8]c | -4.5c [-7.9, -0.9]c | W1:+0.6 W2:-8.7 W3:-0.8 W4:-2.1 | CANDIDATE |
| YES | 60-70c | 2,058 | 64 | 0.644 | 0.625 | -0.1c [-4.0, +3.7]c | -3.5c [-7.4, +0.2]c | W1:-3.6 W2:-6.4 W3:+1.7 W4:+0.9 | NO_SIGNAL |
| YES | 70-80c | 1,958 | 64 | 0.745 | 0.736 | +1.5c [-2.1, +4.7]c | -2.3c [-5.5, +1.0]c | W1:-1.3 W2:-5.0 W3:+2.4 W4:+0.4 | NO_SIGNAL |
| YES | 80-90c | 1,821 | 64 | 0.842 | 0.841 | +2.8c [-0.3, +5.9]c | -1.0c [-4.0, +1.8]c | W1:+0.3 W2:-4.3 W3:+3.4 W4:+0.3 | NO_SIGNAL |
| YES | 90-100c | 1,322 | 64 | 0.949 | 0.933 | +1.4c [-1.0, +3.6]c | -1.9c [-4.4, +0.5]c | W1:-2.8 W2:-4.1 W3:-0.2 W4:+1.3 | NO_SIGNAL |

## 4. Market families

| family | contract-sides | mean return at the ask |
|---|---|---|
| PLAYER_STAT | 41,542 | -2.5c |
| SPREAD | 12,646 | -2.4c |
| TOTAL | 10,983 | -2.6c |
| TEAM_TOTAL | 6,144 | -2.6c |
| PERIOD_WINNER | 2,300 | -2.2c |
| HALF_FULL_RESULT | 907 | -1.9c |
| WIN_MARGIN_BUCKET | 820 | -3.1c |
| BOTH_TEAMS_SCORE | 512 | -3.1c |
| BOTH_TEAMS_SCORE_N | 479 | -4.7c |
| GAME_PLAYER_LEADER | 464 | -8.6c |
| GAME_WINNER | 256 | -2.0c |

## 5. Conditional patterns that survived every safeguard (CANDIDATE) — discovery only

115 CANDIDATE cells at latest pregame. Negative returns dominate: most survivors are COST (half-spread + fee) or favourite–longshot effects, not hidden value. Mid bias says which are mispricing.

| cell | sides | games | weeks | price | event | mid bias (CI) | return (CI) | q | by week |
|---|---|---|---|---|---|---|---|---|---|
| `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=NO|env_total_band=total41-45` | 141 | 24 | 4 | 0.864 | 0.830 | -1.3c [-1.8, -0.9]c | -4.2c [-5.3, -3.3]c | 0.000 | W1:-6.5 W2:-5.5 W3:-2.4 W4:-3.1 |
| `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=YES|env_total_band=total41-45` | 168 | 24 | 4 | 0.152 | 0.143 | +1.0c [+0.7, +1.3]c | -1.7c [-2.2, -1.3]c | 0.000 | W1:-3.2 W2:-1.3 W3:-1.6 W4:-1.0 |
| `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=80-90c` | 152 | 50 | 4 | 0.856 | 0.618 | -12.9c [-18.7, -6.2]c | -24.7c [-31.4, -16.1]c | 0.000 | W1:-33.8 W2:-11.9 W3:-15.1 W4:-0.0 |
| `S13_player_disagreement_x_side|stat=completions|player_disagreement_band=>10pp|side=NO` | 241 | 54 | 4 | 0.756 | 0.523 | -11.2c [-20.6, -2.2]c | -24.4c [-33.8, -14.4]c | 0.000 | W1:-29.7 W2:-21.7 W3:-11.8 W4:-8.2 |
| `S02_family_x_side_x_price|family=GAME_PLAYER_LEADER|side=YES|price_band=10-20c` | 78 | 30 | 3 | 0.138 | 0.000 | -7.9c [-8.7, -7.3]c | -14.6c [-15.2, -3.2]c | 0.000 | W2:-18.0 W3:-14.7 W4:-14.4 |
| `S16_period_family_x_side_x_price|subfamily=TOTAL:2H:total_points|side=NO|price_band=10-20c` | 116 | 63 | 4 | 0.137 | 0.026 | -7.8c [-10.3, -4.6]c | -12.0c [-14.5, -4.6]c | 0.000 | W1:-14.1 W2:-8.0 W3:-11.0 W4:-15.0 |
| `S10_player_stat_x_total_env|stat=receptions|env_total_band=total41-45|side=YES` | 1,854 | 24 | 4 | 0.309 | 0.272 | -2.7c [-4.7, -0.7]c | -4.7c [-6.7, -2.6]c | 0.001 | W1:-6.4 W2:-7.3 W3:-2.3 W4:-3.8 |
| `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=40-50c` | 193 | 52 | 4 | 0.439 | 0.295 | -10.7c [-17.2, -3.5]c | -16.1c [-23.0, -8.6]c | 0.001 | W1:-16.7 W2:-19.5 W3:-16.8 W4:-6.3 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=80-90c` | 3,368 | 64 | 4 | 0.850 | 0.813 | -1.9c [-3.8, -0.0]c | -4.6c [-6.6, -2.6]c | 0.001 | W1:-7.6 W2:-1.4 W3:-4.7 W4:-4.1 |
| `S13_player_disagreement_x_side|stat=receiving_yards|player_disagreement_band=5-10pp|side=NO` | 1,103 | 63 | 4 | 0.780 | 0.731 | -4.0c [-6.7, -1.4]c | -5.9c [-8.5, -3.3]c | 0.001 | W1:-4.2 W2:-6.1 W3:-3.4 W4:-9.9 |
| `S03_family_x_side_x_rung|family=SPREAD|side=NO|rung_offset_band=main` | 894 | 64 | 4 | 0.619 | 0.598 | -0.9c [-2.5, +0.9]c | -3.6c [-5.3, -1.9]c | 0.002 | W1:-3.7 W2:-3.1 W3:-3.9 W4:-3.7 |
| `S16_period_family_x_side_x_price|subfamily=GAME_PLAYER_LEADER:FULL:receiving_yards|side=YES|price_band=10-20c` | 59 | 26 | 2 | 0.135 | 0.000 | -7.6c [-8.6, -6.8]c | -14.3c [-14.9, -1.4]c | 0.002 | W3:-14.4 W4:-14.2 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=90-100c` | 6,639 | 64 | 4 | 0.952 | 0.930 | -0.8c [-2.0, +0.3]c | -2.5c [-3.7, -1.4]c | 0.002 | W1:-4.4 W2:-0.7 W3:-1.2 W4:-3.5 |
| `S14_move_x_side_x_price|move_band=down>5c|side=YES|price_band=00-10c` | 364 | 56 | 4 | 0.058 | 0.025 | -1.8c [-3.4, +0.3]c | -3.7c [-5.4, -1.7]c | 0.003 | W1:-2.8 W2:-5.9 W3:-0.9 W4:-5.2 |
| `S01_side_x_price|side=NO|price_band=80-90c` | 6,297 | 64 | 4 | 0.849 | 0.820 | -1.4c [-3.3, +0.4]c | -3.8c [-5.9, -2.0]c | 0.004 | W1:-7.3 W2:-1.1 W3:-3.0 W4:-3.7 |
| `S03_family_x_side_x_rung|family=PLAYER_STAT|side=NO|rung_offset_band=adjacent+1` | 3,613 | 64 | 4 | 0.778 | 0.750 | -1.3c [-3.3, +0.6]c | -3.9c [-5.9, -1.9]c | 0.004 | W1:-6.7 W2:-1.1 W3:-3.8 W4:-3.9 |
| `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=10-20c` | 186 | 56 | 4 | 0.161 | 0.097 | -5.0c [-8.7, -1.2]c | -7.4c [-11.1, -3.7]c | 0.004 | W1:-7.1 W2:-8.9 W3:-8.2 W4:-5.4 |
| `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=70-80c` | 2,268 | 64 | 4 | 0.750 | 0.700 | -2.3c [-5.0, +0.4]c | -6.3c [-9.5, -3.0]c | 0.005 | W1:-15.0 W2:-0.6 W3:-4.2 W4:-3.2 |
| `S08_player_stat_x_side_x_price|stat=receptions|side=YES|price_band=50-60c` | 321 | 64 | 4 | 0.546 | 0.467 | -7.2c [-12.1, -2.6]c | -9.6c [-14.5, -4.9]c | 0.005 | W1:-6.3 W2:-7.8 W3:-15.9 W4:-9.1 |
| `S15_availability_x_side|availability_state=EXPECTED_ACTIVE|stat=completions|side=NO` | 568 | 63 | 4 | 0.598 | 0.470 | -6.1c [-12.5, +0.2]c | -14.0c [-21.2, -6.8]c | 0.005 | W1:-18.7 W2:-6.9 W3:-10.4 W4:-9.0 |
| `S09_player_stat_x_role_certainty|stat=completions|role_certainty=HIGH|side=NO` | 565 | 63 | 4 | 0.599 | 0.471 | -6.1c [-12.5, +0.2]c | -14.0c [-21.2, -6.8]c | 0.006 | W1:-18.7 W2:-6.9 W3:-10.4 W4:-8.8 |
| `S04_rung_x_price_x_side|rung_offset_band=adjacent+1|price_band=80-90c|side=NO` | 848 | 64 | 4 | 0.842 | 0.791 | -3.2c [-6.4, -0.2]c | -6.0c [-9.3, -3.0]c | 0.006 | W1:-13.1 W2:-0.7 W3:-6.3 W4:-5.1 |
| `S11_player_position_x_stat|position=QB|stat=completions|side=NO` | 590 | 64 | 4 | 0.596 | 0.473 | -5.7c [-12.1, +0.8]c | -13.6c [-20.4, -6.2]c | 0.007 | W1:-17.6 W2:-6.6 W3:-10.4 W4:-9.0 |
| `S04_rung_x_price_x_side|rung_offset_band=adjacent+1|price_band=90-100c|side=NO` | 840 | 64 | 4 | 0.964 | 0.931 | -1.5c [-3.3, +0.2]c | -3.6c [-5.5, -1.7]c | 0.007 | W1:-6.3 W2:-4.3 W3:-0.1 W4:-2.7 |
| `S18_family_x_side_x_mid|family=PLAYER_STAT|side=NO|mid_band=90-100c` | 6,040 | 64 | 4 | 0.955 | 0.938 | -0.7c [-1.8, +0.4]c | -2.0c [-3.1, -1.0]c | 0.008 | W1:-3.1 W2:-0.4 W3:-1.1 W4:-3.5 |
| `S18_family_x_side_x_mid|family=WIN_MARGIN_BUCKET|side=NO|mid_band=80-90c` | 179 | 63 | 4 | 0.870 | 0.804 | -4.0c [-7.8, -0.3]c | -7.3c [-11.3, -3.5]c | 0.008 | W1:-10.1 W2:-5.8 W3:-4.9 W4:-8.2 |
| `S03_family_x_side_x_rung|family=PLAYER_STAT|side=NO|rung_offset_band=far+` | 8,734 | 64 | 4 | 0.895 | 0.872 | -1.0c [-2.6, +0.6]c | -3.0c [-4.5, -1.4]c | 0.009 | W1:-3.9 W2:-1.6 W3:-2.3 W4:-3.8 |
| `S01_side_x_price|side=NO|price_band=70-80c` | 4,540 | 64 | 4 | 0.749 | 0.716 | -1.4c [-3.7, +0.9]c | -4.6c [-7.1, -2.1]c | 0.009 | W1:-10.5 W2:-0.8 W3:-2.7 W4:-3.9 |
| `S05_family_x_side_x_total_env|family=PLAYER_STAT|side=YES|env_total_band=total41-45` | 7,833 | 24 | 4 | 0.307 | 0.281 | -1.3c [-3.3, +0.9]c | -3.7c [-5.7, -1.7]c | 0.010 | W1:-4.8 W2:-7.3 W3:-0.8 W4:-2.8 |
| `S08_player_stat_x_side_x_price|stat=receiving_yards|side=NO|price_band=90-100c` | 1,957 | 64 | 4 | 0.948 | 0.921 | -1.6c [-3.3, +0.2]c | -3.1c [-4.7, -1.3]c | 0.010 | W1:-4.3 W2:-1.6 W3:-0.5 W4:-5.6 |
| `S11_player_position_x_stat|position=WR|stat=receiving_yards|side=NO` | 3,420 | 64 | 4 | 0.709 | 0.666 | -3.4c [-6.4, -0.5]c | -5.3c [-8.4, -2.5]c | 0.010 | W1:-4.9 W2:-3.6 W3:-5.9 W4:-7.0 |
| `S13_player_disagreement_x_side|stat=receptions|player_disagreement_band=2-5pp|side=NO` | 874 | 63 | 4 | 0.909 | 0.874 | -2.4c [-4.7, -0.2]c | -4.0c [-6.2, -1.8]c | 0.010 | W1:-3.8 W2:-1.6 W3:-4.3 W4:-5.9 |
| `S15_availability_x_side|availability_state=EXPECTED_ACTIVE|stat=receiving_yards|side=NO` | 5,336 | 63 | 4 | 0.727 | 0.701 | -1.7c [-3.7, +0.3]c | -3.6c [-5.6, -1.6]c | 0.010 | W1:-4.3 W2:-2.1 W3:-3.3 W4:-4.6 |
| `S18_family_x_side_x_mid|family=PLAYER_STAT|side=NO|mid_band=80-90c` | 3,425 | 64 | 4 | 0.864 | 0.835 | -1.6c [-3.6, +0.4]c | -3.7c [-5.7, -1.7]c | 0.010 | W1:-4.8 W2:-2.2 W3:-4.2 W4:-3.5 |
| `S08_player_stat_x_side_x_price|stat=completions|side=NO|price_band=80-90c` | 121 | 57 | 4 | 0.855 | 0.727 | -7.7c [-15.2, -0.5]c | -13.7c [-21.3, -6.1]c | 0.011 | W1:-13.9 W2:-5.2 W3:-10.3 W4:-23.4 |
| `S13_player_disagreement_x_side|stat=attempts|player_disagreement_band=>10pp|side=NO` | 274 | 58 | 4 | 0.751 | 0.577 | -6.4c [-15.6, +3.7]c | -18.5c [-28.3, -7.4]c | 0.011 | W1:-24.7 W2:-16.0 W3:-0.9 W4:-4.0 |
| `S16_period_family_x_side_x_price|subfamily=TOTAL:2H:total_points|side=NO|price_band=20-30c` | 66 | 55 | 4 | 0.247 | 0.121 | -8.8c [-15.9, -0.5]c | -13.9c [-21.3, -5.4]c | 0.013 | W1:-22.0 W2:-6.7 W3:-10.9 W4:-10.0 |
| `S02_family_x_side_x_price|family=TOTAL|side=NO|price_band=10-20c` | 472 | 64 | 4 | 0.144 | 0.081 | -4.4c [-8.4, +0.0]c | -7.3c [-11.2, -2.9]c | 0.015 | W1:-6.2 W2:-2.2 W3:-9.9 W4:-10.5 |
| `S01_side_x_price|side=NO|price_band=90-100c` | 10,800 | 64 | 4 | 0.951 | 0.933 | -0.2c [-1.4, +0.9]c | -2.1c [-3.4, -1.0]c | 0.016 | W1:-4.9 W2:-0.2 W3:-1.2 W4:-2.1 |
| `S16_period_family_x_side_x_price|subfamily=SPREAD:2Q:margin|side=YES|price_band=10-20c` | 175 | 64 | 4 | 0.145 | 0.074 | -5.5c [-9.8, -0.7]c | -8.0c [-12.4, -3.1]c | 0.016 | W1:-12.7 W2:-10.5 W3:-5.4 W4:-4.6 |

## 6. Patterns that did NOT survive (rejected in discovery)

- UNSTABLE (a week or a held-out week flips the sign): 82 cells. Largest:
  - `S08_player_stat_x_side_x_price|stat=attempts|side=NO|price_band=70-80c` -23.1c (51 games) — W1:-31.2 W2:+11.5 W3:-4.0 W4:-28.3
  - `S12_price_x_data_only_disagreement|data_only_disagreement_band=<2pp|side=NO|price_band=40-50c` -22.0c (30 games) — W1:-41.9 W2:+19.7 W3:-30.5 W4:-15.2
  - `S12_price_x_data_only_disagreement|data_only_disagreement_band=<2pp|side=YES|price_band=50-60c` +19.0c (31 games) — W1:+36.8 W2:-16.4 W3:+18.4 W4:+17.8
  - `S14_move_x_side_x_price|move_band=down>5c|side=NO|price_band=70-80c` -18.0c (45 games) — W1:-27.3 W2:+4.5 W3:-9.9 W4:+2.3
  - `S16_period_family_x_side_x_price|subfamily=SPREAD:2H:margin|side=YES|price_band=50-60c` -17.8c (34 games) — W1:-41.1 W2:-12.4 W3:+20.4 W4:-24.5
  - `S13_player_disagreement_x_side|stat=carries|player_disagreement_band=5-10pp|side=NO` -16.6c (45 games) — W1:-27.0 W2:-10.8 W3:+3.5 W4:-3.2
  - `S16_period_family_x_side_x_price|subfamily=TOTAL:4Q:total_points|side=NO|price_band=20-30c` -16.3c (63 games) — W1:-22.8 W2:+0.6 W3:-25.8 W4:-20.8
  - `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=70-80c` -16.0c (59 games) — W1:-31.6 W2:+1.7 W3:-3.7 W4:+1.5
  - `S13_player_disagreement_x_side|stat=carries|player_disagreement_band=2-5pp|side=NO` -15.6c (37 games) — W1:-33.4 W2:+5.1 W3:+7.2 W4:-25.3
  - `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=90-100c` -14.7c (35 games) — W1:-22.3 W2:+3.6 W3:+6.5 W4:-13.4
  - `S02_family_x_side_x_price|family=BOTH_TEAMS_SCORE|side=NO|price_band=30-40c` -13.5c (50 games) — W1:+4.3 W2:-27.7 W3:-19.7 W4:-15.1
  - `S08_player_stat_x_side_x_price|stat=touchdowns|side=YES|price_band=40-50c` -12.9c (43 games) — W1:+2.5 W2:-9.9 W3:-33.0 W4:-17.4
- NO_SIGNAL (interval includes zero): 932 cells. NOT_SIGNIFICANT_AFTER_MULTIPLICITY: 26 cells.

## 7. Ladders (one ladder = one thesis)

4,614 ladders with ≥ 3 live rungs at latest pregame. a ladder's realised best rung is one draw of one outcome; read the by-family shares across many ladders, never one ladder's winner.

| family | ladders | best realised = main rung | best CLV = main rung | incoherent | a rung ≥ 2c under the ladder's own fair curve |
|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 63 | 30.2% | 38.1% | 1 | 0 |
| PLAYER_STAT | 2951 | 17.8% | 34.2% | 113 | 0 |
| SPREAD | 896 | 8.0% | 34.9% | 39 | 0 |
| TEAM_TOTAL | 256 | 9.4% | 16.4% | 92 | 18 |
| TOTAL | 448 | 10.3% | 17.4% | 54 | 0 |

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

- `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=NO|env_total_band=total41-45` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S05_family_x_side_x_total_env|family=WIN_MARGIN_BUCKET|side=YES|env_total_band=total41-45` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S08_player_stat_x_side_x_price|stat=carries|side=NO|price_band=80-90c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S13_player_disagreement_x_side|stat=completions|player_disagreement_band=>10pp|side=NO` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S02_family_x_side_x_price|family=GAME_PLAYER_LEADER|side=YES|price_band=10-20c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S16_period_family_x_side_x_price|subfamily=TOTAL:2H:total_points|side=NO|price_band=10-20c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S10_player_stat_x_total_env|stat=receptions|env_total_band=total41-45|side=YES` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S14_move_x_side_x_price|move_band=up>5c|side=YES|price_band=40-50c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S02_family_x_side_x_price|family=PLAYER_STAT|side=NO|price_band=80-90c` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).
- `S13_player_disagreement_x_side|stat=receiving_yards|player_disagreement_band=5-10pp|side=NO` — a CANDIDATE in discovery; would need its own preregistration before any week it is tested on (registering it now would make Weeks 1–3 its generation window).

