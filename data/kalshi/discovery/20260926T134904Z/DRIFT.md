# Discovery -> registry drift (20260926T134904Z)

Registry holds 392 series; discovery lists 484 NFL candidates.

| quantity | n |
|---|---|
| new_series | 30 |
| new_series_open_markets | 1830 |
| unclassified_series | 18 |
| capture_gap_contracts | 1830 |
| capture_gap_contracts_outside_registry | 1830 |

## NEW_SERIES (not in the reviewed registry)

| series | family | open | first seen | lag (days) | title |
|---|---|---|---|---|---|
| KXNFLWEEKHIGHSCORE | WEEK_EVENT | 480 | 20260926T134904Z | 0.0 | NFL Highest Scoring Team of the Week |
| KXNFLFFWEEKLEAD | WEEK_LEADER | 253 | 20260926T134904Z | 0.0 | Weekly Fantasy Football Leader |
| KXNFLPOTM | AWARD | 201 | 20260926T134904Z | 0.0 | NFL Player of the Month |
| KXNFLFFWEEKTOP | WEEK_LEADER | 157 | 20260926T134904Z | 0.0 | Weekly Fantasy Football Top Players |
| KXNFLFFPTSLADDER | SEASON_FANTASY | 88 | 20260926T134904Z | 0.0 | Fantasy Ladder |
| KXNFLFFPLAYOFFLEADER | SEASON_FANTASY | 75 | 20260926T134904Z | 0.0 | Fantasy Football Playoffs Leader |
| KXNFLESCALATORREC | UNKNOWN_NEEDS_CLASSIFICATION | 74 | 20260926T134904Z | 0.0 | Receptions Escalator |
| KXNFLESCALATORRECYDS | UNKNOWN_NEEDS_CLASSIFICATION | 74 | 20260926T134904Z | 0.0 | Receiving Yards Escalator |
| KXNFLLADDERREC | UNKNOWN_NEEDS_CLASSIFICATION | 74 | 20260926T134904Z | 0.0 | Receptions Ladder |
| KXNFLLADDERRECYDS | UNKNOWN_NEEDS_CLASSIFICATION | 74 | 20260926T134904Z | 0.0 | Receiving Yards Ladder |
| KXNFLROTM | AWARD | 60 | 20260926T134904Z | 0.0 | NFL Rookie of the Month |
| KXNFLESCALATORRSHYDS | UNKNOWN_NEEDS_CLASSIFICATION | 41 | 20260926T134904Z | 0.0 | Rushing Yards Escalator |
| KXNFLLADDERRSHYDS | UNKNOWN_NEEDS_CLASSIFICATION | 41 | 20260926T134904Z | 0.0 | Rushing Yards Ladder |
| KXNFLFFSEASONTOTAL | SEASON_FANTASY | 36 | 20260926T134904Z | 0.0 | Pro Football Player's Fantasy Season Total |
| KXSBLSPREAD | SUPER_BOWL_EVENT | 36 | 20260926T134904Z | 0.0 | Slovakia SBL Spread |
| KXSBLTOTAL | SUPER_BOWL_EVENT | 33 | 20260926T134904Z | 0.0 | Slovakia SBL Total |
| KXNFLMVPSPECIALS | UNKNOWN_NEEDS_CLASSIFICATION | 14 | 20260926T134904Z | 0.0 | NFL MVP Award Specials |
| KXNFLCAREERPASSYDS | UNKNOWN_NEEDS_CLASSIFICATION | 6 | 20260926T134904Z | 0.0 | NFL Career Passing Yards |
| KXNFLLONGESTPLAY | SEASON_SPECIAL | 5 | 20260926T134904Z | 0.0 | NFL Longest Touchdown |
| KXNFLDELAY | UNKNOWN_NEEDS_CLASSIFICATION | 2 | 20260926T134904Z | 0.0 | NFL Weather Delay |
| KXNFLDPOYSPECIALS | UNKNOWN_NEEDS_CLASSIFICATION | 2 | 20260926T134904Z | 0.0 | NFL Defensive Player of the Year Specials |
| KXNFLOPOYSPECIALS | UNKNOWN_NEEDS_CLASSIFICATION | 2 | 20260926T134904Z | 0.0 | NFL Offensive Player of the Year Specials |
| KXNFLGAMELOCATION | UNKNOWN_NEEDS_CLASSIFICATION | 1 | 20260926T134904Z | 0.0 | NFL Game Location |
| KXNFLHKANE | UNKNOWN_NEEDS_CLASSIFICATION | 1 | 20260926T134904Z | 0.0 | Harry Kane Pro Football signing |
| KXNFLCAREERPASSTDS | UNKNOWN_NEEDS_CLASSIFICATION | 0 | 20260926T134904Z | 0.0 | NFL Career Passing Touchdowns |
| KXNFLCAREERRECYDS | UNKNOWN_NEEDS_CLASSIFICATION | 0 | 20260926T134904Z | 0.0 | NFL Career Receiving Yards |
| KXNFLCAREERRSHTDS | UNKNOWN_NEEDS_CLASSIFICATION | 0 | 20260926T134904Z | 0.0 | NFL Career Rushing Touchdowns |
| KXNFLCAREERRSHYDS | UNKNOWN_NEEDS_CLASSIFICATION | 0 | 20260926T134904Z | 0.0 | NFL Career Rushing Yards |
| KXNFLWEEKTIE | WEEK_EVENT | 0 | 20260926T134904Z | 0.0 | NFL Weekly Tie |
| KXNFLWINNINGSTREAK | UNKNOWN_NEEDS_CLASSIFICATION | 0 | 20260926T134904Z | 0.0 | NFL Team Winning Streak |

## UNCLASSIFIED

| series | open | title |
|---|---|---|
| KXNFLESCALATORREC | 74 | Receptions Escalator |
| KXNFLESCALATORRECYDS | 74 | Receiving Yards Escalator |
| KXNFLLADDERREC | 74 | Receptions Ladder |
| KXNFLLADDERRECYDS | 74 | Receiving Yards Ladder |
| KXNFLESCALATORRSHYDS | 41 | Rushing Yards Escalator |
| KXNFLLADDERRSHYDS | 41 | Rushing Yards Ladder |
| KXNFLMVPSPECIALS | 14 | NFL MVP Award Specials |
| KXNFLCAREERPASSYDS | 6 | NFL Career Passing Yards |
| KXNFLDELAY | 2 | NFL Weather Delay |
| KXNFLDPOYSPECIALS | 2 | NFL Defensive Player of the Year Specials |
| KXNFLOPOYSPECIALS | 2 | NFL Offensive Player of the Year Specials |
| KXNFLGAMELOCATION | 1 | NFL Game Location |
| KXNFLHKANE | 1 | Harry Kane Pro Football signing |
| KXNFLCAREERPASSTDS | 0 | NFL Career Passing Touchdowns |
| KXNFLCAREERRECYDS | 0 | NFL Career Receiving Yards |
| KXNFLCAREERRSHTDS | 0 | NFL Career Rushing Touchdowns |
| KXNFLCAREERRSHYDS | 0 | NFL Career Rushing Yards |
| KXNFLWINNINGSTREAK | 0 | NFL Team Winning Streak |

## CAPTURE_GAP (open contracts never confirmed open by any capture run)

| series | open | never seen | in registry | tier |
|---|---|---|---|---|
| KXNFLWEEKHIGHSCORE | 480 | 480 | False | None |
| KXNFLFFWEEKLEAD | 253 | 253 | False | None |
| KXNFLPOTM | 201 | 201 | False | None |
| KXNFLFFWEEKTOP | 157 | 157 | False | None |
| KXNFLFFPTSLADDER | 88 | 88 | False | None |
| KXNFLFFPLAYOFFLEADER | 75 | 75 | False | None |
| KXNFLESCALATORREC | 74 | 74 | False | None |
| KXNFLESCALATORRECYDS | 74 | 74 | False | None |
| KXNFLLADDERREC | 74 | 74 | False | None |
| KXNFLLADDERRECYDS | 74 | 74 | False | None |
| KXNFLROTM | 60 | 60 | False | None |
| KXNFLESCALATORRSHYDS | 41 | 41 | False | None |
| KXNFLLADDERRSHYDS | 41 | 41 | False | None |
| KXNFLFFSEASONTOTAL | 36 | 36 | False | None |
| KXSBLSPREAD | 36 | 36 | False | None |
| KXSBLTOTAL | 33 | 33 | False | None |
| KXNFLMVPSPECIALS | 14 | 14 | False | None |
| KXNFLCAREERPASSYDS | 6 | 6 | False | None |
| KXNFLLONGESTPLAY | 5 | 5 | False | None |
| KXNFLDELAY | 2 | 2 | False | None |
| KXNFLDPOYSPECIALS | 2 | 2 | False | None |
| KXNFLOPOYSPECIALS | 2 | 2 | False | None |
| KXNFLGAMELOCATION | 1 | 1 | False | None |
| KXNFLHKANE | 1 | 1 | False | None |

## NEW_MARKET_STRUCTURES: 498 contracts on PROVEN families did not parse PROVEN

* KXNFLFG-26SEP28PHICHI-PHI4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP28PHICHI-PHI3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP28PHICHI-PHI2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP28PHICHI-PHI1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP28PHICHI-CHI4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP28PHICHI-CHI3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP28PHICHI-CHI2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP28PHICHI-CHI1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27LARDEN-LAR4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27LARDEN-LAR3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27LARDEN-LAR2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27LARDEN-LAR1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27LARDEN-DEN4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27LARDEN-DEN3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27LARDEN-DEN2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27LARDEN-DEN1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27BALDAL-DAL4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27BALDAL-DAL3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27BALDAL-DAL2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP27BALDAL-DAL1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
