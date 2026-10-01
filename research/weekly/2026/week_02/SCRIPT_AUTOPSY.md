# SCRIPT AUTOPSY — 2026 week 2

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

Hierarchy: GAME ENVIRONMENT → TEAM VOLUME → PLAYER OPPORTUNITY → EFFICIENCY. Expectations are frozen or point-in-time only: the board's latest-pregame ladders, the simulation's script summary from Week 4, the team's prior-game mean, the incumbent's frozen projected opportunity. Weeks 1–3 have no frozen team-volume projection; their team-volume expectation is a QB pass-attempts ladder or the prior mean, and says so.

## 1. Game-centre errors (market at latest pregame vs final)

16 games. Market MAE — margin 11.59, total 10.79, home points 9.08, away points 7.50.

## 2. What kind of games were played

| label | games |
|---|---|
| COMPETITIVE_THROUGHOUT | 7 |
| FAVORITE_CONTROL | 6 |
| UPSET | 5 |
| LOW_SCORING | 5 |
| BLOWOUT | 5 |
| UNDERDOG_CONTROL | 3 |
| LATE_COMEBACK | 3 |
| LOW_POSSESSION | 3 |
| EARLY_BLOWOUT | 2 |
| SHOOTOUT | 2 |
| HIGH_VOLUME_PASSING | 1 |
| RUN_HEAVY_CONTROL | 1 |

_Labels read the play-by-play score progression and the PREGAME market favourite / total only; no label reads a wager._

| game | primary script | labels | final | market margin / total | margin err | total err | plays H/A | pass att H/A |
|---|---|---|---|---|---|---|---|---|
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

## 3. Team-volume errors (beyond ±25%)

- designed_rush|over|not-explained: 8
- designed_rush|under|script-explained: 4
- plays|over|not-explained: 4
- designed_rush|under|not-explained: 4
- pass_att|over|not-explained: 3
- plays|under|not-explained: 3
- pass_att|under|script-explained: 2
- plays|under|script-explained: 2
- pass_att|under|not-explained: 2
- pass_att|over|script-explained: 1
- designed_rush|over|script-explained: 1

## 4. Player projection misses, by the layer that left expectation first

998 canonical player-stat units (one per game × player × statistic, autopsy rule autopsy-1.1.0). Classification: NO_LARGE_MISS 382, OPPORTUNITY_MISS 307, EFFICIENCY_MISS 186, TEAM_VOLUME_MISS 74, UNEXPLAINED_VARIANCE 28, INSUFFICIENT_DATA 14, AVAILABILITY_MISS 7.

Of 602 meaningful misses (excluding NO_LARGE_MISS and INSUFFICIENT_DATA): OPPORTUNITY + TEAM_VOLUME 63.3%, EFFICIENCY 30.9%.

| miss layer | units | share of meaningful misses |
|---|---|---|
| NO_LARGE_MISS | 382 | — |
| PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | 253 | 42.0% |
| EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | 186 | 30.9% |
| TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | 58 | 9.6% |
| ROLE_UNCERTAINTY | 39 | 6.5% |
| GAME_SCRIPT_DROVE_TEAM_VOLUME | 31 | 5.1% |
| VARIANCE_ONLY | 28 | 4.7% |
| INSUFFICIENT_DATA | 14 | — |
| AVAILABILITY | 7 | 1.2% |

**Would better game scripting plausibly have prevented the miss?** For 5.1% of meaningful misses: the team's volume missed in the miss's direction AND the realized script (a big lead or deficit, or a low-possession game) explains it by the volume model's own mechanism. The largest layer is a player's SHARE with team volume on expectation — who got the ball, not how many plays there were.

**Sensitivity — excluding anytime-touchdown props** (425 meaningful misses; a TD prop's opportunity is total touches, so almost all of its variation reads as share): EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION 44%, PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION 35%, TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT 9%, GAME_SCRIPT_DROVE_TEAM_VOLUME 6%, ROLE_UNCERTAINTY 4%, VARIANCE_ONLY 2%, AVAILABILITY 0%.

| primary script | PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | GAME_SCRIPT_DROVE_TEAM_VOLUME | ROLE_UNCERTAINTY | AVAILABILITY | VARIANCE_ONLY |
|---|---|---|---|---|---|---|---|
| BLOWOUT | 75 | 66 | 7 | 19 | 18 | 3 | 7 |
| UPSET | 78 | 54 | 11 | 12 | 8 | 0 | 7 |
| EARLY_BLOWOUT | 42 | 25 | 7 | 0 | 2 | 0 | 6 |
| LATE_COMEBACK | 31 | 19 | 11 | 0 | 2 | 1 | 4 |
| SHOOTOUT | 19 | 11 | 8 | 0 | 4 | 3 | 3 |
| COMPETITIVE_THROUGHOUT | 8 | 11 | 14 | 0 | 5 | 0 | 1 |

## 5. Recurring failure modes

- touchdowns: 177 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (105, 59%).
- receiving_yards: 147 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (78, 53%).
- receptions: 117 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (58, 50%).
- rushing_yards: 63 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (29, 46%).
- carries: 25 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (16, 64%).
- passing_tds: 24 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (23, 96%).
- team pass attempts under expectation by > 25% while leading/tied: 3 team-games.
- team pass attempts over expectation by > 25% while trailing: 2 team-games.
- team pass attempts over expectation by > 25% while leading/tied: 2 team-games.
- team pass attempts under expectation by > 25% while trailing: 1 team-games.

## 6. Autopsy coverage

- week 2: expected 16 games, diagnosed 16, excluded 0 (none).

