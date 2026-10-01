# BOARD EDGE DISCOVERY — 2026 week 2

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

_Inputs: board board-research-1.0.0, miner board-miner-1.0.0, script autopsy script-autopsy-1.0.0, weeks [2]; board rows 63,845_

## 1. Coverage — what was and was not analysed

| stage | contracts |
|---|---|
| discovered | 12,786 |
| mapped_to_game | 12,786 |
| captured_pregame | 11,994 |
| settled_any_source | 11,994 |
| football_settled | 9,473 |
| price_at_primary_horizon | 9,473 |
| executable_quote | 9,473 |
| fee_known | 9,473 |
| analyzed_primary | 9,460 |

Exclusions (every contract that left the funnel, by reason):

- 775 — captured_pregame: never quoted before kickoff
- 468 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_TEAM:FULL:first_td_team]
- 386 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [FIRST_TD_SCORER:FULL:first_td]
- 240 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [RACE_TO_N:FULL:race]
- 169 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:fantasy_points]
- 162 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_reception]
- 160 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_sacks]
- 160 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_yards]
- 128 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:field_goals]
- 128 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:receiving_yards]
- 96 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TEAM_STAT:FULL:team_touchdowns]
- 96 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [TOTAL_TD:FULL:total_touchdowns]
- 66 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [SEASON_LEADER:FULL:rushing_yards]
- 64 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_STAT [PLAYER_STAT:FULL:longest_rush]
- 33 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:touchdowns]
- 33 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receiving_yards]
- 32 — football_settled: exchange-only tier: REFUSED_PLAYER_IDENTITY [PLAYER_STAT:FULL:fantasy_points]
- 31 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:touchdowns]
- 17 — captured_pregame: discovered, never in a pregame capture row (series outside the capture tiers, or listed only after kickoff)
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:defensive_st_td]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:btts]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:overtime]
- 16 — football_settled: exchange-only tier: REFUSED_UNSUPPORTED_FAMILY [GAME_EVENT:FULL:safety]
- 13 — analyzed_primary: football settlement contradicted by the exchange's terminal result (flagged, never resolved)
- 5 — football_settled: exchange-only tier: REFUSED_PARTICIPATION_UNPROVEN [PLAYER_STAT:FULL:receptions]

Discovery universe: GAME_NOT_IN_REG_SCHEDULE (preseason / prior season) 10,294 · GAME_OTHER_WEEKS 6,432 · GAME_TARGET_WEEKS 38,919 · NON_GAME (season / futures / awards / leaders) 16,108

By week × family (primary horizon):

| week | family | discovered | captured | football-settled | analysed |
|---|---|---|---|---|---|
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

## 2. How to read the cells

Unit = one contract SIDE bought at its executable ask. **mid bias** = event rate − the side's mid (is the market's fair price wrong?). **return** = payout − ask − fee per contract (is it exploitable after costs?). Intervals are game-clustered bootstrap (B=2000); rare-outcome cells also get a binomial floor. Cells with < 20 games, < 2 weeks or < 40 sides are DESCRIPTIVE_ONLY. Multiplicity: Benjamini–Hochberg q ≤ 0.2 across all 0 tested cells (≈0.0 would exclude zero by chance alone).

Status counts at latest pregame: DESCRIPTIVE_ONLY 1596.

## 3. Price bands

### Five full-game families, YES side, binned by QUOTED MID (the owner's Weeks 1–3 framing)

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| YES | 00-10c | 220 | 16 | 0.056 | 0.014 | -4.2c [-5.8, -2.0]c | -5.5c [-7.0, +14.6]c | W2:-5.1 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 180 | 16 | 0.147 | 0.194 | +4.7c [-2.5, +12.1]c | +3.1c [-4.2, +10.5]c | W2:+4.0 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 145 | 16 | 0.250 | 0.255 | +0.5c [-7.0, +7.8]c | -1.5c [-9.2, +5.8]c | W2:-0.2 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 123 | 16 | 0.353 | 0.333 | -2.0c [-10.1, +6.7]c | -4.2c [-12.3, +4.5]c | W2:-2.6 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 121 | 16 | 0.447 | 0.364 | -8.4c [-23.3, +8.2]c | -10.6c [-25.6, +5.9]c | W2:-8.9 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 113 | 16 | 0.545 | 0.522 | -2.3c [-17.3, +10.4]c | -4.7c [-19.7, +7.9]c | W2:-3.0 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 88 | 16 | 0.645 | 0.500 | -14.5c [-31.7, +3.4]c | -16.7c [-34.0, +1.2]c | W2:-15.1 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 74 | 16 | 0.745 | 0.608 | -13.7c [-31.3, +4.5]c | -15.9c [-33.3, +2.0]c | W2:-14.6 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 69 | 16 | 0.852 | 0.797 | -5.5c [-22.4, +6.8]c | -7.3c [-24.2, +5.0]c | W2:-6.4 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 110 | 16 | 0.946 | 0.864 | -8.2c [-19.7, +1.6]c | -9.5c [-21.0, +0.5]c | W2:-9.2 | DESCRIPTIVE_ONLY |

### Whole board, binned by the ASK actually paid

| side | band | sides | games | mean price/mid | event rate | mid bias (CI) | return (CI) | by week (event − price) | status |
|---|---|---|---|---|---|---|---|---|---|
| NO | 00-10c | 198 | 16 | 0.059 | 0.091 | +4.2c [-3.4, +13.8]c | +2.8c [-4.8, +12.5]c | W2:+3.2 | DESCRIPTIVE_ONLY |
| NO | 10-20c | 376 | 16 | 0.151 | 0.160 | +2.3c [-3.8, +10.7]c | -0.1c [-6.2, +8.3]c | W2:+0.8 | DESCRIPTIVE_ONLY |
| NO | 20-30c | 507 | 16 | 0.246 | 0.270 | +4.1c [-2.3, +10.7]c | +1.2c [-5.2, +7.8]c | W2:+2.5 | DESCRIPTIVE_ONLY |
| NO | 30-40c | 486 | 16 | 0.345 | 0.352 | +2.0c [-6.1, +10.2]c | -0.8c [-8.9, +7.4]c | W2:+0.7 | DESCRIPTIVE_ONLY |
| NO | 40-50c | 674 | 16 | 0.449 | 0.503 | +6.3c [-1.0, +14.5]c | +3.6c [-3.7, +11.7]c | W2:+5.3 | DESCRIPTIVE_ONLY |
| NO | 50-60c | 849 | 16 | 0.544 | 0.617 | +8.2c [+0.2, +15.8]c | +5.6c [-2.3, +13.1]c | W2:+7.3 | DESCRIPTIVE_ONLY |
| NO | 60-70c | 832 | 16 | 0.647 | 0.651 | +1.4c [-3.8, +6.4]c | -1.1c [-6.3, +3.9]c | W2:+0.5 | DESCRIPTIVE_ONLY |
| NO | 70-80c | 1,089 | 16 | 0.748 | 0.753 | +1.5c [-3.3, +5.6]c | -0.8c [-5.6, +3.3]c | W2:+0.5 | DESCRIPTIVE_ONLY |
| NO | 80-90c | 1,484 | 16 | 0.850 | 0.847 | +1.0c [-1.9, +3.7]c | -1.1c [-3.9, +1.6]c | W2:-0.2 | DESCRIPTIVE_ONLY |
| NO | 90-100c | 2,687 | 16 | 0.952 | 0.954 | +1.6c [+0.4, +2.7]c | -0.2c [-1.3, +1.0]c | W2:+0.2 | DESCRIPTIVE_ONLY |
| YES | 00-10c | 2,227 | 16 | 0.056 | 0.031 | -1.3c [-2.2, -0.5]c | -2.8c [-3.7, -2.0]c | W2:-2.5 | DESCRIPTIVE_ONLY |
| YES | 10-20c | 1,755 | 16 | 0.141 | 0.117 | -1.1c [-3.6, +1.4]c | -3.3c [-5.8, -0.7]c | W2:-2.5 | DESCRIPTIVE_ONLY |
| YES | 20-30c | 1,248 | 16 | 0.242 | 0.215 | -1.3c [-4.2, +2.1]c | -4.1c [-7.1, -0.7]c | W2:-2.8 | DESCRIPTIVE_ONLY |
| YES | 30-40c | 925 | 16 | 0.343 | 0.315 | -1.8c [-6.1, +3.0]c | -4.4c [-8.7, +0.4]c | W2:-2.8 | DESCRIPTIVE_ONLY |
| YES | 40-50c | 820 | 16 | 0.447 | 0.385 | -5.2c [-12.4, +2.3]c | -7.8c [-15.1, -0.4]c | W2:-6.1 | DESCRIPTIVE_ONLY |
| YES | 50-60c | 760 | 16 | 0.539 | 0.453 | -7.8c [-14.9, -0.8]c | -10.4c [-17.5, -3.4]c | W2:-8.7 | DESCRIPTIVE_ONLY |
| YES | 60-70c | 480 | 16 | 0.644 | 0.579 | -5.5c [-13.9, +3.7]c | -8.0c [-16.4, +1.2]c | W2:-6.4 | DESCRIPTIVE_ONLY |
| YES | 70-80c | 470 | 16 | 0.746 | 0.696 | -3.9c [-10.6, +3.3]c | -6.4c [-13.1, +0.8]c | W2:-5.0 | DESCRIPTIVE_ONLY |
| YES | 80-90c | 435 | 16 | 0.840 | 0.798 | -2.7c [-10.6, +3.7]c | -5.2c [-13.2, +1.3]c | W2:-4.3 | DESCRIPTIVE_ONLY |
| YES | 90-100c | 331 | 16 | 0.950 | 0.909 | -1.7c [-10.0, +4.3]c | -4.4c [-12.7, +1.5]c | W2:-4.1 | DESCRIPTIVE_ONLY |

## 4. Market families

| family | contract-sides | mean return at the ask |
|---|---|---|
| PLAYER_STAT | 9,845 | -2.1c |
| SPREAD | 3,182 | -2.4c |
| TOTAL | 2,738 | -2.4c |
| TEAM_TOTAL | 1,548 | -2.4c |
| PERIOD_WINNER | 572 | -2.3c |
| HALF_FULL_RESULT | 220 | -1.3c |
| WIN_MARGIN_BUCKET | 202 | -3.1c |
| BOTH_TEAMS_SCORE | 128 | -3.3c |
| BOTH_TEAMS_SCORE_N | 121 | -3.9c |
| GAME_WINNER | 64 | -2.0c |
| GAME_PLAYER_LEADER | 13 | -2.7c |

## 5. Conditional patterns that survived every safeguard (CANDIDATE) — discovery only

0 CANDIDATE cells at latest pregame. Negative returns dominate: most survivors are COST (half-spread + fee) or favourite–longshot effects, not hidden value. Mid bias says which are mispricing.

| cell | sides | games | weeks | price | event | mid bias (CI) | return (CI) | q | by week |
|---|---|---|---|---|---|---|---|---|---|

## 6. Patterns that did NOT survive (rejected in discovery)

- UNSTABLE (a week or a held-out week flips the sign): 0 cells. Largest:
- NO_SIGNAL (interval includes zero): 0 cells. NOT_SIGNIFICANT_AFTER_MULTIPLICITY: 0 cells.

## 7. Ladders (one ladder = one thesis)

1,118 ladders with ≥ 3 live rungs at latest pregame. a ladder's realised best rung is one draw of one outcome; read the by-family shares across many ladders, never one ladder's winner.

| family | ladders | best realised = main rung | best CLV = main rung | incoherent | a rung ≥ 2c under the ladder's own fair curve |
|---|---|---|---|---|---|
| BOTH_TEAMS_SCORE_N | 16 | 31.2% | 37.5% | 1 | 0 |
| PLAYER_STAT | 702 | 17.0% | 36.8% | 3 | 0 |
| SPREAD | 224 | 7.1% | 35.7% | 6 | 0 |
| TEAM_TOTAL | 64 | 7.8% | 15.6% | 30 | 4 |
| TOTAL | 112 | 13.4% | 20.5% | 13 | 0 |

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


