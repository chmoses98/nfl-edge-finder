# SCRIPT AUTOPSY — 2026 weeks 1–3 (cumulative)

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

Hierarchy: GAME ENVIRONMENT → TEAM VOLUME → PLAYER OPPORTUNITY → EFFICIENCY. Expectations are frozen or point-in-time only: the board's latest-pregame ladders, the simulation's script summary from Week 4, the team's prior-game mean, the incumbent's frozen projected opportunity. Weeks 1–3 have no frozen team-volume projection; their team-volume expectation is a QB pass-attempts ladder or the prior mean, and says so.

## 1. Game-centre errors (market at latest pregame vs final)

48 games. Market MAE — margin 10.36, total 11.18, home points 8.14, away points 7.93.

## 2. What kind of games were played

| label | games |
|---|---|
| COMPETITIVE_THROUGHOUT | 21 |
| UPSET | 16 |
| UNDERDOG_CONTROL | 13 |
| FAVORITE_CONTROL | 13 |
| SHOOTOUT | 13 |
| BLOWOUT | 13 |
| LOW_SCORING | 10 |
| LOW_POSSESSION | 6 |
| EARLY_BLOWOUT | 4 |
| RUN_HEAVY_CONTROL | 4 |
| LATE_COMEBACK | 4 |
| HIGH_VOLUME_PASSING | 4 |

_Labels read the play-by-play score progression and the PREGAME market favourite / total only; no label reads a wager._

| game | primary script | labels | final | market margin / total | margin err | total err | plays H/A | pass att H/A |
|---|---|---|---|---|---|---|---|---|
| 2026_01_ARI_LAC | UPSET | UNDERDOG_CONTROL, UPSET | 14-26 | 8.8 / 47.5 | -20.8 | -7.5 | 51/72 | 27/37 |
| 2026_01_ATL_PIT | COMPETITIVE_THROUGHOUT | COMPETITIVE_THROUGHOUT | 20-13 | 6.4 / 41.1 | 0.6 | -8.1 | 64/57 | 41/22 |
| 2026_01_BAL_IND | EARLY_BLOWOUT | FAVORITE_CONTROL, EARLY_BLOWOUT, SHOOTOUT | 23-41 | -2.9 / 48.6 | -15.1 | 15.4 | 53/64 | 31/25 |
| 2026_01_BUF_HOU | SHOOTOUT | COMPETITIVE_THROUGHOUT, SHOOTOUT | 31-36 | -0.6 / 44.9 | -4.4 | 22.1 | 73/53 | 38/30 |
| 2026_01_CHI_CAR | BLOWOUT | FAVORITE_CONTROL, BLOWOUT, SHOOTOUT | 37-59 | -2.9 / 47.4 | -19.1 | 48.6 | 62/70 | 38/29 |
| 2026_01_CLE_JAX | EARLY_BLOWOUT | FAVORITE_CONTROL, EARLY_BLOWOUT, LOW_POSSESSION | 34-10 | 8.5 / 40.7 | 15.5 | 3.3 | 56/49 | 23/22 |
| 2026_01_DAL_NYG | UPSET | COMPETITIVE_THROUGHOUT, UNDERDOG_CONTROL, UPSET | 28-20 | -3.2 / 48.3 | 11.2 | -0.3 | 68/52 | 29/34 |
| 2026_01_DEN_KC | BLOWOUT | FAVORITE_CONTROL, BLOWOUT, LOW_POSSESSION | 31-10 | 1.8 / 43.1 | 19.2 | -2.1 | 67/47 | 27/28 |
| 2026_01_GB_MIN | BLOWOUT | BLOWOUT, SHOOTOUT | 39-22 | 2.5 / 45.8 | 14.5 | 15.2 | 62/67 | 25/42 |
| 2026_01_MIA_LV | FAVORITE_CONTROL | FAVORITE_CONTROL, RUN_HEAVY_CONTROL | 27-13 | 3.1 / 40.6 | 10.9 | -0.6 | 67/50 | 30/27 |
| 2026_01_NE_SEA | LATE_COMEBACK | COMPETITIVE_THROUGHOUT, LATE_COMEBACK, LOW_SCORING | 13-10 | 3.1 / 44.6 | -0.1 | -21.6 | 48/67 | 24/33 |
| 2026_01_NO_DET | SHOOTOUT | COMPETITIVE_THROUGHOUT, SHOOTOUT, HIGH_VOLUME_PASSING | 31-30 | 6.9 / 50.5 | -5.9 | 10.5 | 73/87 | 39/57 |
| 2026_01_NYJ_TEN | BLOWOUT | UNDERDOG_CONTROL, UPSET, BLOWOUT, LOW_POSSESSION, RUN_HEAVY_CONTROL | 10-23 | 0.6 / 40.0 | -13.6 | -7.0 | 49/63 | 32/24 |
| 2026_01_SF_LA | BLOWOUT | UNDERDOG_CONTROL, UPSET, BLOWOUT, LOW_SCORING | 7-27 | 3.8 / 48.1 | -23.8 | -14.1 | 57/64 | 28/34 |
| 2026_01_TB_CIN | UNREMARKABLE |  | 33-27 | 3.7 / 50.6 | 2.3 | 9.4 | 63/52 | 35/28 |
| 2026_01_WAS_PHI | COMPETITIVE_THROUGHOUT | COMPETITIVE_THROUGHOUT | 24-22 | 5.8 / 44.0 | -3.8 | 2.0 | 53/68 | 25/35 |
| 2026_02_CAR_ATL | EARLY_BLOWOUT | FAVORITE_CONTROL, EARLY_BLOWOUT | 3-34 | -2.7 / 43.9 | -28.3 | -6.9 | 67/60 | 32/36 |
| 2026_02_CIN_HOU | UPSET | UNDERDOG_CONTROL, UPSET, LOW_SCORING, HIGH_VOLUME_PASSING | 6-20 | 2.8 / 45.8 | -16.8 | -19.8 | 78/59 | 56/31 |
| 2026_02_CLE_TB | UPSET | COMPETITIVE_THROUGHOUT, UPSET | 19-23 | 7.9 / 41.9 | -11.9 | 0.1 | 62/55 | 34/30 |
| 2026_02_DET_BUF | EARLY_BLOWOUT | FAVORITE_CONTROL, EARLY_BLOWOUT, SHOOTOUT | 41-31 | 5.2 / 55.4 | 4.8 | 16.6 | 69/62 | 31/38 |
| 2026_02_GB_NYJ | LATE_COMEBACK | COMPETITIVE_THROUGHOUT, LATE_COMEBACK | 17-20 | -3.1 / 44.5 | 0.1 | -7.5 | 72/50 | 41/29 |
| 2026_02_IND_KC | SHOOTOUT | COMPETITIVE_THROUGHOUT, SHOOTOUT | 33-30 | 5.8 / 46.0 | -2.8 | 17.0 | 78/63 | 47/31 |
| 2026_02_JAX_DEN | LATE_COMEBACK | COMPETITIVE_THROUGHOUT, LATE_COMEBACK, LOW_SCORING, LOW_POSSESSION | 20-13 | 2.7 / 46.1 | 4.3 | -13.1 | 59/55 | 31/29 |
| 2026_02_LV_LAC | UPSET | UNDERDOG_CONTROL, UPSET | 14-26 | 6.7 / 43.9 | -18.7 | -3.9 | 62/60 | 27/29 |
| 2026_02_MIA_SF | BLOWOUT | FAVORITE_CONTROL, BLOWOUT, LOW_POSSESSION | 35-13 | 13.0 / 45.4 | 9.0 | 2.6 | 49/56 | 22/23 |
| 2026_02_MIN_CHI | UPSET | COMPETITIVE_THROUGHOUT, UNDERDOG_CONTROL, UPSET, LOW_SCORING | 3-9 | 4.4 / 47.1 | -10.4 | -35.1 | 70/51 | 35/20 |
| 2026_02_NO_BAL | UPSET | COMPETITIVE_THROUGHOUT, UPSET, LATE_COMEBACK | 17-24 | 8.0 / 45.9 | -15.0 | -4.9 | 56/65 | 31/34 |
| 2026_02_NYG_LA | BLOWOUT | FAVORITE_CONTROL, BLOWOUT, LOW_SCORING | 28-6 | 6.7 / 47.7 | 15.3 | -13.7 | 60/55 | 31/32 |
| 2026_02_PHI_TEN | COMPETITIVE_THROUGHOUT | COMPETITIVE_THROUGHOUT | 20-24 | -6.9 / 40.3 | 2.9 | 3.7 | 51/72 | 20/37 |
| 2026_02_PIT_NE | BLOWOUT | FAVORITE_CONTROL, BLOWOUT, LOW_SCORING | 20-3 | 4.9 / 41.7 | 12.1 | -18.7 | 53/67 | 22/40 |
| 2026_02_SEA_ARI | BLOWOUT | BLOWOUT, LOW_POSSESSION, RUN_HEAVY_CONTROL | 7-31 | -3.8 / 41.6 | -20.2 | -3.6 | 47/67 | 28/26 |
| 2026_02_WAS_DAL | BLOWOUT | FAVORITE_CONTROL, BLOWOUT | 37-20 | 4.0 / 51.6 | 13.0 | 5.4 | 54/67 | 31/35 |
| 2026_03_ARI_SF | SHOOTOUT | SHOOTOUT | 36-30 | 7.6 / 49.1 | -1.6 | 16.9 | 50/81 | 27/52 |
| 2026_03_ATL_GB | BLOWOUT | UNDERDOG_CONTROL, UPSET, BLOWOUT, RUN_HEAVY_CONTROL | 14-35 | 4.9 / 43.5 | -25.9 | 5.5 | 63/67 | 53/26 |
| 2026_03_BAL_DAL | SHOOTOUT | COMPETITIVE_THROUGHOUT, SHOOTOUT | 31-34 | -3.2 / 53.9 | 0.2 | 11.1 | 72/58 | 41/20 |
| 2026_03_CAR_CLE | UPSET | COMPETITIVE_THROUGHOUT, UNDERDOG_CONTROL, UPSET, HIGH_VOLUME_PASSING | 21-18 | -2.0 / 42.2 | 5.0 | -3.2 | 64/75 | 32/48 |
| 2026_03_CIN_PIT | UPSET | COMPETITIVE_THROUGHOUT, UNDERDOG_CONTROL, UPSET, SHOOTOUT | 30-27 | -3.1 / 42.6 | 6.1 | 14.4 | 59/56 | 34/37 |
| 2026_03_HOU_IND | UPSET | COMPETITIVE_THROUGHOUT, UNDERDOG_CONTROL, UPSET | 19-17 | -0.8 / 42.6 | 2.8 | -6.6 | 71/51 | 36/27 |
| 2026_03_KC_MIA | LOW_SCORING | FAVORITE_CONTROL, LOW_SCORING | 10-24 | -9.7 / 45.6 | -4.3 | -11.6 | 67/49 | 36/24 |
| 2026_03_LAC_BUF | LOW_SCORING | LOW_SCORING | 24-16 | 7.1 / 50.8 | 0.9 | -10.8 | 63/64 | 26/34 |
| 2026_03_LA_DEN | SHOOTOUT | SHOOTOUT, HIGH_VOLUME_PASSING | 30-26 | 0.0 / 44.4 | 4.0 | 11.6 | 62/82 | 36/55 |
| 2026_03_LV_NO | UPSET | COMPETITIVE_THROUGHOUT, UPSET, SHOOTOUT | 27-35 | 3.4 / 44.4 | -11.4 | 17.6 | 72/65 | 42/35 |
| 2026_03_MIN_TB | COMPETITIVE_THROUGHOUT | COMPETITIVE_THROUGHOUT | 16-23 | -0.7 / 43.1 | -6.3 | -4.1 | 64/55 | 37/29 |
| 2026_03_NE_JAX | BLOWOUT | FAVORITE_CONTROL, BLOWOUT | 35-6 | 3.0 / 47.4 | 26.1 | -6.4 | 60/60 | 29/31 |
| 2026_03_NYJ_DET | COMPETITIVE_THROUGHOUT | COMPETITIVE_THROUGHOUT | 31-24 | 6.8 / 50.4 | 0.2 | 4.6 | 64/63 | 32/39 |
| 2026_03_PHI_CHI | BLOWOUT | UNDERDOG_CONTROL, UPSET, BLOWOUT | 27-7 | -3.3 / 43.0 | 23.3 | -9.0 | 69/47 | 34/26 |
| 2026_03_SEA_WAS | UPSET | COMPETITIVE_THROUGHOUT, UNDERDOG_CONTROL, UPSET, SHOOTOUT | 33-31 | -8.3 / 40.6 | 10.3 | 23.4 | 65/64 | 31/46 |
| 2026_03_TEN_NYG | LOW_SCORING | LOW_SCORING | 12-7 | 2.6 / 38.2 | 2.4 | -19.2 | 58/57 | 22/36 |

## 3. Team-volume errors (beyond ±25%)

- designed_rush|over|not-explained: 15
- designed_rush|under|not-explained: 14
- pass_att|over|not-explained: 11
- designed_rush|under|script-explained: 11
- plays|under|not-explained: 9
- plays|over|not-explained: 9
- pass_att|under|not-explained: 6
- pass_att|over|script-explained: 5
- pass_att|under|script-explained: 5
- designed_rush|over|script-explained: 5
- plays|under|script-explained: 3

## 4. Player projection misses, by the layer that left expectation first

2,980 canonical player-stat units (one per game × player × statistic, autopsy rule autopsy-1.1.0). Classification: NO_LARGE_MISS 1130, OPPORTUNITY_MISS 980, EFFICIENCY_MISS 525, TEAM_VOLUME_MISS 174, UNEXPLAINED_VARIANCE 92, INSUFFICIENT_DATA 40, AVAILABILITY_MISS 39.

Of 1,810 meaningful misses (excluding NO_LARGE_MISS and INSUFFICIENT_DATA): OPPORTUNITY + TEAM_VOLUME 63.8%, EFFICIENCY 29.0%.

| miss layer | units | share of meaningful misses |
|---|---|---|
| NO_LARGE_MISS | 1,130 | — |
| PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | 744 | 41.1% |
| EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | 525 | 29.0% |
| TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | 192 | 10.6% |
| ROLE_UNCERTAINTY | 116 | 6.4% |
| GAME_SCRIPT_DROVE_TEAM_VOLUME | 102 | 5.6% |
| VARIANCE_ONLY | 92 | 5.1% |
| INSUFFICIENT_DATA | 40 | — |
| AVAILABILITY | 39 | 2.2% |

**Would better game scripting plausibly have prevented the miss?** For 5.6% of meaningful misses: the team's volume missed in the miss's direction AND the realized script (a big lead or deficit, or a low-possession game) explains it by the volume model's own mechanism. The largest layer is a player's SHARE with team volume on expectation — who got the ball, not how many plays there were.

**Sensitivity — excluding anytime-touchdown props** (1,261 meaningful misses; a TD prop's opportunity is total touches, so almost all of its variation reads as share): EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION 42%, PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION 34%, TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT 10%, GAME_SCRIPT_DROVE_TEAM_VOLUME 7%, ROLE_UNCERTAINTY 3%, VARIANCE_ONLY 2%, AVAILABILITY 1%.

| primary script | PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | GAME_SCRIPT_DROVE_TEAM_VOLUME | ROLE_UNCERTAINTY | AVAILABILITY | VARIANCE_ONLY |
|---|---|---|---|---|---|---|---|
| BLOWOUT | 203 | 166 | 16 | 74 | 39 | 9 | 29 |
| UPSET | 194 | 124 | 40 | 12 | 20 | 9 | 23 |
| SHOOTOUT | 82 | 64 | 75 | 0 | 13 | 6 | 12 |
| COMPETITIVE_THROUGHOUT | 71 | 55 | 28 | 0 | 18 | 7 | 8 |
| EARLY_BLOWOUT | 71 | 45 | 7 | 4 | 8 | 0 | 13 |
| LOW_SCORING | 52 | 36 | 15 | 8 | 9 | 4 | 2 |
| LATE_COMEBACK | 31 | 19 | 11 | 0 | 2 | 1 | 4 |
| FAVORITE_CONTROL | 19 | 6 | 0 | 4 | 4 | 3 | 1 |
| UNREMARKABLE | 21 | 10 | 0 | 0 | 3 | 0 | 0 |

## 5. Recurring failure modes

- touchdowns: 549 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (310, 56%).
- receiving_yards: 425 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (212, 50%).
- receptions: 364 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (172, 47%).
- rushing_yards: 189 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (83, 44%).
- carries: 95 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (58, 61%).
- interceptions: 69 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (67, 97%).
- team pass attempts over expectation by > 25% while trailing: 13 team-games.
- team pass attempts under expectation by > 25% while leading/tied: 8 team-games.
- team pass attempts over expectation by > 25% while leading/tied: 3 team-games.
- team pass attempts under expectation by > 25% while trailing: 3 team-games.

## 6. Autopsy coverage

- week 1: expected 16 games, diagnosed 15, excluded 1 (2026_01_NE_SEA: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed)).
- week 2: expected 16 games, diagnosed 16, excluded 0 (none).
- week 3: expected 16 games, diagnosed 16, excluded 0 (none).

