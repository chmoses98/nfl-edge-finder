# Discovery -> registry drift (20260921T155747Z)

Registry holds 392 series; discovery lists 463 NFL candidates.

| quantity | n |
|---|---|
| new_series | 10 |
| new_series_open_markets | 797 |
| unclassified_series | 0 |
| capture_gap_contracts | 797 |
| capture_gap_contracts_outside_registry | 797 |

## NEW_SERIES (not in the reviewed registry)

| series | family | open | first seen | lag (days) | title |
|---|---|---|---|---|---|
| KXNFLFFWEEKLEAD | WEEK_LEADER | 254 | 20260921T155747Z | 0.0 | Weekly Fantasy Football Leader |
| KXNFLPOTM | AWARD | 200 | 20260921T155747Z | 0.0 | NFL Player of the Month |
| KXNFLFFWEEKTOP | WEEK_LEADER | 156 | 20260921T155747Z | 0.0 | Weekly Fantasy Football Top Players |
| KXNFLFFPLAYOFFLEADER | SEASON_FANTASY | 75 | 20260921T155747Z | 0.0 | Fantasy Football Playoffs Leader |
| KXNFLROTM | AWARD | 60 | 20260921T155747Z | 0.0 | NFL Rookie of the Month |
| KXNFLFFSEASONTOTAL | SEASON_FANTASY | 36 | 20260921T155747Z | 0.0 | Pro Football Player's Fantasy Season Total |
| KXNFLFFPTSLADDER | SEASON_FANTASY | 7 | 20260921T155747Z | 0.0 | Fantasy Ladder |
| KXNFLLONGESTPLAY | SEASON_SPECIAL | 5 | 20260921T155747Z | 0.0 | NFL Longest Touchdown |
| KXNFLWEEKHIGHSCORE | WEEK_EVENT | 3 | 20260921T155747Z | 0.0 | NFL Highest Scoring Team of the Week |
| KXNFLWEEKTIE | WEEK_EVENT | 1 | 20260921T155747Z | 0.0 | NFL Weekly Tie |

## UNCLASSIFIED

| series | open | title |
|---|---|---|

## CAPTURE_GAP (open contracts never confirmed open by any capture run)

| series | open | never seen | in registry | tier |
|---|---|---|---|---|
| KXNFLFFWEEKLEAD | 254 | 254 | False | None |
| KXNFLPOTM | 200 | 200 | False | None |
| KXNFLFFWEEKTOP | 156 | 156 | False | None |
| KXNFLFFPLAYOFFLEADER | 75 | 75 | False | None |
| KXNFLROTM | 60 | 60 | False | None |
| KXNFLFFSEASONTOTAL | 36 | 36 | False | None |
| KXNFLFFPTSLADDER | 7 | 7 | False | None |
| KXNFLLONGESTPLAY | 5 | 5 | False | None |
| KXNFLWEEKHIGHSCORE | 3 | 3 | False | None |
| KXNFLWEEKTIE | 1 | 1 | False | None |

## NEW_MARKET_STRUCTURES: 35 contracts on PROVEN families did not parse PROVEN

* KXNFLFG-26SEP21NYGLAR-NYG4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP21NYGLAR-NYG3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP21NYGLAR-NYG2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP21NYGLAR-NYG1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP21NYGLAR-LAR4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP21NYGLAR-LAR3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP21NYGLAR-LAR2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP21NYGLAR-LAR1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-LAR-CDANIELS6 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-LAR-XSMITH19 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-LAR-TATWELL8 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-NYG-OBECKHAM13 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-NYG-TJOHNSON84 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-NYG-NYGDST (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-NYG-NO-TD (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-NYG-NHARRIS23 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-NYG-MNABERS1 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-NYG-MFIELDS88 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-NYG-JDART6 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP21NYGLAR-NYG-ILIKELY9 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
