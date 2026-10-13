# SCRIPT AUTOPSY — 2026 week 4

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

Hierarchy: GAME ENVIRONMENT → TEAM VOLUME → PLAYER OPPORTUNITY → EFFICIENCY. Expectations are frozen or point-in-time only: the board's latest-pregame ladders, the simulation's script summary from Week 4, the team's prior-game mean, the incumbent's frozen projected opportunity. Weeks 1–3 have no frozen team-volume projection; their team-volume expectation is a QB pass-attempts ladder or the prior mean, and says so.

## 1. Game-centre errors (market at latest pregame vs final)

16 games. Market MAE — margin 7.28, total 9.66, home points 5.51, away points 5.56.

## 2. What kind of games were played

| label | games |
|---|---|
| UPSET | 7 |
| UNDERDOG_CONTROL | 6 |
| SHOOTOUT | 4 |
| LOW_SCORING | 3 |
| EARLY_BLOWOUT | 2 |
| RUN_HEAVY_CONTROL | 2 |
| HIGH_VOLUME_PASSING | 2 |
| FAVORITE_CONTROL | 2 |
| COMPETITIVE_THROUGHOUT | 2 |
| BLOWOUT | 1 |
| LATE_COMEBACK | 1 |
| LOW_POSSESSION | 1 |

_Labels read the play-by-play score progression and the PREGAME market favourite / total only; no label reads a wager._

| game | primary script | labels | final | market margin / total | margin err | total err | plays H/A | pass att H/A |
|---|---|---|---|---|---|---|---|---|
| 2026_04_ARI_NYG | UPSET | UNDERDOG_CONTROL, UPSET, SHOOTOUT | 36-24 | -2.3 / 44.6 | 14.3 | 15.4 | 63/63 | 30/35 |
| 2026_04_ATL_NO | EARLY_BLOWOUT | UNDERDOG_CONTROL, UPSET, EARLY_BLOWOUT, SHOOTOUT, RUN_HEAVY_CONTROL | 24-45 | 0.6 / 48.1 | -21.6 | 20.9 | 69/56 | 48/20 |
| 2026_04_DAL_HOU | UPSET | UPSET, SHOOTOUT | 30-34 | 2.7 / 49.5 | -6.7 | 14.5 | 52/73 | 31/45 |
| 2026_04_DEN_SF | LOW_SCORING | LOW_SCORING | 24-14 | 3.0 / 49.1 | 7.0 | -11.1 | 65/65 | 30/42 |
| 2026_04_DET_CAR | UPSET | UNDERDOG_CONTROL, UPSET, HIGH_VOLUME_PASSING | 32-26 | -4.4 / 52.8 | 10.4 | 5.2 | 72/68 | 41/52 |
| 2026_04_GB_TB | UNREMARKABLE |  | 14-17 | -2.7 / 39.4 | -0.3 | -8.4 | 61/55 | 27/30 |
| 2026_04_IND_WAS | BLOWOUT | FAVORITE_CONTROL, BLOWOUT | 13-30 | -4.7 / 47.4 | -12.3 | -4.4 | 61/66 | 37/34 |
| 2026_04_JAX_CIN | UPSET | UNDERDOG_CONTROL, UPSET, LOW_SCORING | 17-22 | 2.6 / 52.5 | -7.6 | -13.5 | 71/55 | 54/24 |
| 2026_04_KC_LV | COMPETITIVE_THROUGHOUT | COMPETITIVE_THROUGHOUT, HIGH_VOLUME_PASSING | 27-30 | -5.3 / 47.6 | 2.3 | 9.4 | 79/59 | 53/31 |
| 2026_04_LAC_SEA | EARLY_BLOWOUT | EARLY_BLOWOUT | 30-23 | 7.1 / 43.3 | -0.1 | 9.7 | 58/68 | 22/32 |
| 2026_04_LA_PHI | LATE_COMEBACK | LATE_COMEBACK | 20-24 | -3.4 / 43.3 | -0.6 | 0.7 | 58/77 | 27/51 |
| 2026_04_MIA_MIN | LOW_SCORING | LOW_SCORING, LOW_POSSESSION | 15-10 | 9.8 / 39.1 | -4.8 | -14.1 | 72/37 | 37/17 |
| 2026_04_NE_BUF | UPSET | COMPETITIVE_THROUGHOUT, UNDERDOG_CONTROL, UPSET | 26-29 | 6.8 / 49.9 | -9.8 | 5.1 | 55/74 | 34/38 |
| 2026_04_NYJ_CHI | FAVORITE_CONTROL | FAVORITE_CONTROL, RUN_HEAVY_CONTROL | 23-12 | 3.4 / 43.8 | 7.6 | -8.8 | 89/32 | 34/15 |
| 2026_04_PIT_CLE | UPSET | UNDERDOG_CONTROL, UPSET, SHOOTOUT | 27-24 | -2.9 / 38.4 | 5.9 | 12.6 | 62/66 | 33/41 |
| 2026_04_TEN_BAL | UNREMARKABLE |  | 24-18 | 11.3 / 42.8 | -5.3 | -0.8 | 61/59 | 29/32 |

## 3. Team-volume errors (beyond ±25%)

- pass_att|over|not-explained: 6
- designed_rush|under|not-explained: 5
- designed_rush|over|not-explained: 3
- pass_att|under|not-explained: 3
- designed_rush|under|script-explained: 2
- pass_att|under|script-explained: 2
- plays|under|not-explained: 2
- plays|over|not-explained: 2
- pass_att|over|script-explained: 1
- plays|under|script-explained: 1

## 4. Player projection misses, by the layer that left expectation first

1,061 canonical player-stat units (one per game × player × statistic, autopsy rule autopsy-1.1.0). Classification: OPPORTUNITY_MISS 362, NO_LARGE_MISS 342, EFFICIENCY_MISS 195, TEAM_VOLUME_MISS 100, UNEXPLAINED_VARIANCE 36, INSUFFICIENT_DATA 15, AVAILABILITY_MISS 11.

Of 704 meaningful misses (excluding NO_LARGE_MISS and INSUFFICIENT_DATA): OPPORTUNITY + TEAM_VOLUME 65.6%, EFFICIENCY 27.7%.

| miss layer | units | share of meaningful misses |
|---|---|---|
| NO_LARGE_MISS | 342 | — |
| PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | 301 | 42.8% |
| EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | 195 | 27.7% |
| TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | 91 | 12.9% |
| ROLE_UNCERTAINTY | 47 | 6.7% |
| VARIANCE_ONLY | 36 | 5.1% |
| GAME_SCRIPT_DROVE_TEAM_VOLUME | 23 | 3.3% |
| INSUFFICIENT_DATA | 15 | — |
| AVAILABILITY | 11 | 1.6% |

**Would better game scripting plausibly have prevented the miss?** For 3.3% of meaningful misses: the team's volume missed in the miss's direction AND the realized script (a big lead or deficit, or a low-possession game) explains it by the volume model's own mechanism. The largest layer is a player's SHARE with team volume on expectation — who got the ball, not how many plays there were.

**Sensitivity — excluding anytime-touchdown props** (502 meaningful misses; a TD prop's opportunity is total touches, so almost all of its variation reads as share): EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION 39%, PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION 35%, TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT 16%, GAME_SCRIPT_DROVE_TEAM_VOLUME 4%, VARIANCE_ONLY 3%, ROLE_UNCERTAINTY 3%, AVAILABILITY 1%.

| primary script | PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | GAME_SCRIPT_DROVE_TEAM_VOLUME | ROLE_UNCERTAINTY | AVAILABILITY | VARIANCE_ONLY |
|---|---|---|---|---|---|---|---|
| UPSET | 127 | 73 | 41 | 0 | 11 | 2 | 14 |
| EARLY_BLOWOUT | 35 | 30 | 2 | 12 | 7 | 2 | 6 |
| UNREMARKABLE | 52 | 22 | 0 | 0 | 11 | 1 | 4 |
| LOW_SCORING | 30 | 31 | 8 | 11 | 4 | 2 | 3 |
| BLOWOUT | 17 | 17 | 0 | 0 | 6 | 3 | 3 |
| COMPETITIVE_THROUGHOUT | 14 | 5 | 17 | 0 | 5 | 0 | 0 |
| LATE_COMEBACK | 17 | 10 | 5 | 0 | 3 | 1 | 3 |
| FAVORITE_CONTROL | 9 | 7 | 18 | 0 | 0 | 0 | 3 |

## 5. Recurring failure modes

- touchdowns: 202 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (125, 62%).
- receiving_yards: 169 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (84, 50%).
- receptions: 140 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (66, 47%).
- rushing_yards: 80 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (33, 41%).
- carries: 36 meaningful misses; the most common first-failing layer is PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION (27, 75%).
- interceptions: 25 meaningful misses; the most common first-failing layer is EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION (24, 96%).
- team pass attempts over expectation by > 25% while trailing: 4 team-games.
- team pass attempts under expectation by > 25% while leading/tied: 3 team-games.
- team pass attempts over expectation by > 25% while leading/tied: 3 team-games.
- team pass attempts under expectation by > 25% while trailing: 2 team-games.

## 6. Autopsy coverage

- week 4: expected 16 games, diagnosed 16, excluded 0 (none).

