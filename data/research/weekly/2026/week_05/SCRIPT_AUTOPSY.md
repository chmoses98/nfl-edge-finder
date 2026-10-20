# SCRIPT AUTOPSY — 2026 week 5

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

Hierarchy: GAME ENVIRONMENT → TEAM VOLUME → PLAYER OPPORTUNITY → EFFICIENCY. Expectations are frozen or point-in-time only: the board's latest-pregame ladders, the simulation's script summary from Week 4, the team's prior-game mean, the incumbent's frozen projected opportunity. Weeks 1–3 have no frozen team-volume projection; their team-volume expectation is a QB pass-attempts ladder or the prior mean, and says so.

## 1. Game-centre errors (market at latest pregame vs final)

15 games. Market MAE — margin 10.36, total 10.11, home points 7.25, away points 6.35.

## 2. What kind of games were played

| label | games |
|---|---|
| COMPETITIVE_THROUGHOUT | 6 |
| SHOOTOUT | 6 |
| UPSET | 5 |
| FAVORITE_CONTROL | 4 |
| UNDERDOG_CONTROL | 3 |
| EARLY_BLOWOUT | 3 |
| BLOWOUT | 2 |
| LATE_COMEBACK | 1 |
| LOW_POSSESSION | 1 |
| HIGH_VOLUME_PASSING | 1 |

_Labels read the play-by-play score progression and the PREGAME market favourite / total only; no label reads a wager._

| game | primary script | labels | final | market margin / total | margin err | total err | plays H/A | pass att H/A |
|---|---|---|---|---|---|---|---|---|
| 2026_05_BAL_ATL | UPSET | COMPETITIVE_THROUGHOUT, UPSET | 23-30 | 3.2 / 44.6 | -10.2 | 8.4 | 64/73 | 35/33 |
| 2026_05_BUF_LA | UPSET | COMPETITIVE_THROUGHOUT, UNDERDOG_CONTROL, UPSET, SHOOTOUT | 34-37 | 3.3 / 55.6 | -6.3 | 15.4 | 79/58 | 55/20 |
| 2026_05_CHI_GB | BLOWOUT | UNDERDOG_CONTROL, UPSET, BLOWOUT | 31-7 | -0.7 / 47.1 | 24.8 | -9.1 | 60/68 | 32/40 |
| 2026_05_CIN_MIA | EARLY_BLOWOUT | EARLY_BLOWOUT | 24-31 | -7.0 / 45.4 | 0.0 | 9.6 | 65/63 | 28/32 |
| 2026_05_CLE_NYJ | COMPETITIVE_THROUGHOUT | COMPETITIVE_THROUGHOUT | 17-12 | 2.6 / 38.8 | 2.4 | -9.8 | 66/65 | 30/33 |
| 2026_05_DEN_LAC | LATE_COMEBACK | COMPETITIVE_THROUGHOUT, LATE_COMEBACK | 17-23 | -3.3 / 42.5 | -2.7 | -2.5 | 63/57 | 24/27 |
| 2026_05_DET_ARI | EARLY_BLOWOUT | FAVORITE_CONTROL, EARLY_BLOWOUT, SHOOTOUT | 21-45 | -5.3 / 55.4 | -18.7 | 10.6 | 71/65 | 48/30 |
| 2026_05_HOU_TEN | BLOWOUT | FAVORITE_CONTROL, BLOWOUT | 3-26 | -6.6 / 37.9 | -16.4 | -8.9 | 58/63 | 36/34 |
| 2026_05_IND_PIT | SHOOTOUT | FAVORITE_CONTROL, SHOOTOUT | 34-22 | 2.9 / 42.2 | 9.1 | 13.8 | 54/69 | 31/44 |
| 2026_05_LV_NE | EARLY_BLOWOUT | FAVORITE_CONTROL, EARLY_BLOWOUT, SHOOTOUT | 45-17 | 3.3 / 45.8 | 24.7 | 16.2 | 66/57 | 34/36 |
| 2026_05_MIN_NO | UNREMARKABLE | LOW_POSSESSION | 13-23 | -2.3 / 41.9 | -7.7 | -5.9 | 43/68 | 25/30 |
| 2026_05_NYG_WAS | SHOOTOUT | SHOOTOUT, HIGH_VOLUME_PASSING | 27-27 | 3.2 / 41.6 | -3.2 | 12.4 | 61/84 | 26/54 |
| 2026_05_PHI_JAX | COMPETITIVE_THROUGHOUT | COMPETITIVE_THROUGHOUT | 19-17 | 7.8 / 42.4 | -5.8 | -6.4 | 68/59 | 39/40 |
| 2026_05_SF_SEA | UPSET | COMPETITIVE_THROUGHOUT, UPSET, SHOOTOUT | 29-32 | 3.0 / 47.6 | -6.0 | 13.4 | 60/57 | 29/30 |
| 2026_05_TB_DAL | UPSET | UNDERDOG_CONTROL, UPSET | 16-24 | 9.6 / 49.4 | -17.6 | -9.4 | 56/65 | 43/25 |

## 3. Team-volume errors (beyond ±25%)

- designed_rush|under|script-explained: 5
- designed_rush|over|not-explained: 4
- pass_att|over|not-explained: 4
- pass_att|under|not-explained: 2
- designed_rush|under|not-explained: 2
- pass_att|over|script-explained: 1
- plays|under|script-explained: 1
- pass_att|under|script-explained: 1
- plays|over|not-explained: 1

## 4. Player projection misses, by the layer that left expectation first

0 canonical player-stat units (one per game × player × statistic, autopsy rule ). Classification: .

Of 0 meaningful misses (excluding NO_LARGE_MISS and INSUFFICIENT_DATA): OPPORTUNITY + TEAM_VOLUME —, EFFICIENCY —.

| miss layer | units | share of meaningful misses |
|---|---|---|

**Would better game scripting plausibly have prevented the miss?** For — of meaningful misses: the team's volume missed in the miss's direction AND the realized script (a big lead or deficit, or a low-possession game) explains it by the volume model's own mechanism. The largest layer is a player's SHARE with team volume on expectation — who got the ball, not how many plays there were.

| primary script | PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | GAME_SCRIPT_DROVE_TEAM_VOLUME | ROLE_UNCERTAINTY | AVAILABILITY | VARIANCE_ONLY |
|---|---|---|---|---|---|---|---|

## 5. Recurring failure modes

- team pass attempts over expectation by > 25% while trailing: 4 team-games.
- team pass attempts under expectation by > 25% while trailing: 2 team-games.
- team pass attempts under expectation by > 25% while leading/tied: 1 team-games.
- team pass attempts over expectation by > 25% while leading/tied: 1 team-games.

## 6. Autopsy coverage

- week 5: expected 15 games, diagnosed 0, excluded 15 (2026_05_BAL_ATL: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_BUF_LA: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_CHI_GB: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_CIN_MIA: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_CLE_NYJ: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_DEN_LAC: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_DET_ARI: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_HOU_TEN: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_IND_PIT: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_LV_NE: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_MIN_NO: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_NYG_WAS: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_PHI_JAX: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_SF_SEA: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed); 2026_05_TB_DAL: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed)).

