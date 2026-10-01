# SCRIPT AUTOPSY — 2026 week 3

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

Hierarchy: GAME ENVIRONMENT → TEAM VOLUME → PLAYER OPPORTUNITY → EFFICIENCY. Expectations are frozen or point-in-time only: the board's latest-pregame ladders, the simulation's script summary from Week 4, the team's prior-game mean, the incumbent's frozen projected opportunity. Weeks 1–3 have no frozen team-volume projection; their team-volume expectation is a QB pass-attempts ladder or the prior mean, and says so.

## 1. Game-centre errors (market at latest pregame vs final)

16 games. Market MAE — margin 8.18, total 11.00, home points 6.87, away points 7.76.

## 2. What kind of games were played

| label | games |
|---|---|
| COMPETITIVE_THROUGHOUT | 8 |
| UPSET | 7 |
| SHOOTOUT | 6 |
| UNDERDOG_CONTROL | 6 |
| BLOWOUT | 3 |
| LOW_SCORING | 3 |
| HIGH_VOLUME_PASSING | 2 |
| FAVORITE_CONTROL | 2 |
| RUN_HEAVY_CONTROL | 1 |

_Labels read the play-by-play score progression and the PREGAME market favourite / total only; no label reads a wager._

| game | primary script | labels | final | market margin / total | margin err | total err | plays H/A | pass att H/A |
|---|---|---|---|---|---|---|---|---|
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

- pass_att|over|not-explained: 4
- plays|over|not-explained: 4
- designed_rush|over|not-explained: 4
- designed_rush|under|not-explained: 4
- plays|under|not-explained: 3
- pass_att|over|script-explained: 2
- designed_rush|under|script-explained: 2
- pass_att|under|not-explained: 2
- designed_rush|over|script-explained: 1
- pass_att|under|script-explained: 1

## 4. Player projection misses, by the layer that left expectation first

999 canonical player-stat units (one per game × player × statistic, autopsy rule autopsy-1.1.0). Classification: NO_LARGE_MISS 368, OPPORTUNITY_MISS 300, EFFICIENCY_MISS 178, TEAM_VOLUME_MISS 100, UNEXPLAINED_VARIANCE 30, AVAILABILITY_MISS 16, INSUFFICIENT_DATA 7.

Of 624 meaningful misses (excluding NO_LARGE_MISS and INSUFFICIENT_DATA): OPPORTUNITY + TEAM_VOLUME 64.1%, EFFICIENCY 28.5%.

| miss layer | units | share of meaningful misses |
|---|---|---|
| NO_LARGE_MISS | 368 | — |
| PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | 253 | 40.5% |
| EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | 178 | 28.5% |
| TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | 80 | 12.8% |
| ROLE_UNCERTAINTY | 37 | 5.9% |
| GAME_SCRIPT_DROVE_TEAM_VOLUME | 30 | 4.8% |
| VARIANCE_ONLY | 30 | 4.8% |
| AVAILABILITY | 16 | 2.6% |
| INSUFFICIENT_DATA | 7 | — |

**Would better game scripting plausibly have prevented the miss?** For 4.8% of meaningful misses: the team's volume missed in the miss's direction AND the realized script (a big lead or deficit, or a low-possession game) explains it by the volume model's own mechanism. The largest layer is a player's SHARE with team volume on expectation — who got the ball, not how many plays there were.

**Sensitivity — excluding anytime-touchdown props** (441 meaningful misses; a TD prop's opportunity is total touches, so almost all of its variation reads as share): EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION 40%, PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION 35%, TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT 12%, GAME_SCRIPT_DROVE_TEAM_VOLUME 7%, ROLE_UNCERTAINTY 3%, AVAILABILITY 2%, VARIANCE_ONLY 2%.

| primary script | PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | GAME_SCRIPT_DROVE_TEAM_VOLUME | ROLE_UNCERTAINTY | AVAILABILITY | VARIANCE_ONLY |
|---|---|---|---|---|---|---|---|
| UPSET | 79 | 53 | 17 | 0 | 10 | 6 | 12 |
| LOW_SCORING | 52 | 36 | 15 | 8 | 9 | 4 | 2 |
| BLOWOUT | 49 | 34 | 5 | 22 | 5 | 1 | 7 |
| SHOOTOUT | 30 | 34 | 42 | 0 | 6 | 2 | 7 |
| COMPETITIVE_THROUGHOUT | 43 | 21 | 1 | 0 | 7 | 3 | 2 |

## 5. Recurring failure modes

- touchdowns: 183 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (99, 54%).
- receiving_yards: 141 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (63, 45%).
- receptions: 131 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (60, 46%).
- rushing_yards: 72 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (34, 47%).
- carries: 35 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (23, 66%).
- passing_tds: 24 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (21, 88%).
- team pass attempts over expectation by > 25% while trailing: 6 team-games.
- team pass attempts under expectation by > 25% while leading/tied: 3 team-games.

## 6. Autopsy coverage

- week 3: expected 16 games, diagnosed 16, excluded 0 (none).

