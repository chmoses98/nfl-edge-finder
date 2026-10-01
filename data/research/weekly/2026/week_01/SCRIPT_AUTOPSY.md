# SCRIPT AUTOPSY — 2026 week 1

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

Hierarchy: GAME ENVIRONMENT → TEAM VOLUME → PLAYER OPPORTUNITY → EFFICIENCY. Expectations are frozen or point-in-time only: the board's latest-pregame ladders, the simulation's script summary from Week 4, the team's prior-game mean, the incumbent's frozen projected opportunity. Weeks 1–3 have no frozen team-volume projection; their team-volume expectation is a QB pass-attempts ladder or the prior mean, and says so.

## 1. Game-centre errors (market at latest pregame vs final)

16 games. Market MAE — margin 11.31, total 11.74, home points 8.48, away points 8.52.

## 2. What kind of games were played

| label | games |
|---|---|
| COMPETITIVE_THROUGHOUT | 6 |
| FAVORITE_CONTROL | 5 |
| SHOOTOUT | 5 |
| BLOWOUT | 5 |
| UNDERDOG_CONTROL | 4 |
| UPSET | 4 |
| LOW_POSSESSION | 3 |
| EARLY_BLOWOUT | 2 |
| RUN_HEAVY_CONTROL | 2 |
| LOW_SCORING | 2 |
| LATE_COMEBACK | 1 |
| HIGH_VOLUME_PASSING | 1 |

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

## 3. Team-volume errors (beyond ±25%)

- designed_rush|under|not-explained: 6
- designed_rush|under|script-explained: 5
- pass_att|over|not-explained: 4
- plays|under|not-explained: 3
- designed_rush|over|not-explained: 3
- designed_rush|over|script-explained: 3
- pass_att|under|not-explained: 2
- pass_att|over|script-explained: 2
- pass_att|under|script-explained: 2
- plays|under|script-explained: 1
- plays|over|not-explained: 1

## 4. Player projection misses, by the layer that left expectation first

983 canonical player-stat units (one per game × player × statistic, autopsy rule autopsy-1.1.0). Classification: NO_LARGE_MISS 380, OPPORTUNITY_MISS 373, EFFICIENCY_MISS 161, UNEXPLAINED_VARIANCE 34, INSUFFICIENT_DATA 19, AVAILABILITY_MISS 16.

Of 584 meaningful misses (excluding NO_LARGE_MISS and INSUFFICIENT_DATA): OPPORTUNITY + TEAM_VOLUME 63.9%, EFFICIENCY 27.6%.

| miss layer | units | share of meaningful misses |
|---|---|---|
| NO_LARGE_MISS | 380 | — |
| PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | 238 | 40.8% |
| EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | 161 | 27.6% |
| TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | 54 | 9.2% |
| GAME_SCRIPT_DROVE_TEAM_VOLUME | 41 | 7.0% |
| ROLE_UNCERTAINTY | 40 | 6.8% |
| VARIANCE_ONLY | 34 | 5.8% |
| INSUFFICIENT_DATA | 19 | — |
| AVAILABILITY | 16 | 2.7% |

**Would better game scripting plausibly have prevented the miss?** For 7.0% of meaningful misses: the team's volume missed in the miss's direction AND the realized script (a big lead or deficit, or a low-possession game) explains it by the volume model's own mechanism. The largest layer is a player's SHARE with team volume on expectation — who got the ball, not how many plays there were.

**Sensitivity — excluding anytime-touchdown props** (395 meaningful misses; a TD prop's opportunity is total touches, so almost all of its variation reads as share): EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION 41%, PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION 33%, TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT 11%, GAME_SCRIPT_DROVE_TEAM_VOLUME 9%, ROLE_UNCERTAINTY 3%, VARIANCE_ONLY 2%, AVAILABILITY 1%.

| primary script | PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | GAME_SCRIPT_DROVE_TEAM_VOLUME | ROLE_UNCERTAINTY | AVAILABILITY | VARIANCE_ONLY |
|---|---|---|---|---|---|---|---|
| BLOWOUT | 79 | 66 | 4 | 33 | 16 | 5 | 15 |
| SHOOTOUT | 33 | 19 | 25 | 0 | 3 | 1 | 2 |
| UPSET | 37 | 17 | 12 | 0 | 2 | 3 | 4 |
| COMPETITIVE_THROUGHOUT | 20 | 23 | 13 | 0 | 6 | 4 | 5 |
| EARLY_BLOWOUT | 29 | 20 | 0 | 4 | 6 | 0 | 7 |
| FAVORITE_CONTROL | 19 | 6 | 0 | 4 | 4 | 3 | 1 |
| UNREMARKABLE | 21 | 10 | 0 | 0 | 3 | 0 | 0 |

## 5. Recurring failure modes

- touchdowns: 189 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (106, 56%).
- receiving_yards: 137 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (71, 52%).
- receptions: 116 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (54, 47%).
- rushing_yards: 54 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (20, 37%).
- carries: 35 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (19, 54%).
- interceptions: 23 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (22, 96%).
- team pass attempts over expectation by > 25% while trailing: 5 team-games.
- team pass attempts under expectation by > 25% while trailing: 2 team-games.
- team pass attempts under expectation by > 25% while leading/tied: 2 team-games.
- team pass attempts over expectation by > 25% while leading/tied: 1 team-games.

## 6. Autopsy coverage

- week 1: expected 16 games, diagnosed 15, excluded 1 (2026_01_NE_SEA: no player-anatomy corpus for this game (no instrumented pregame projection)).

