# Discovery -> registry drift (20260922T140549Z)

Registry holds 392 series; discovery lists 469 NFL candidates.

| quantity | n |
|---|---|
| new_series | 16 |
| new_series_open_markets | 874 |
| unclassified_series | 4 |
| capture_gap_contracts | 874 |
| capture_gap_contracts_outside_registry | 874 |

## NEW_SERIES (not in the reviewed registry)

| series | family | open | first seen | lag (days) | title |
|---|---|---|---|---|---|
| KXNFLWEEKHIGHSCORE | WEEK_EVENT | 480 | 20260922T140549Z | 0.0 | NFL Highest Scoring Team of the Week |
| KXNFLPOTM | AWARD | 200 | 20260922T140549Z | 0.0 | NFL Player of the Month |
| KXNFLFFPLAYOFFLEADER | SEASON_FANTASY | 75 | 20260922T140549Z | 0.0 | Fantasy Football Playoffs Leader |
| KXNFLROTM | AWARD | 60 | 20260922T140549Z | 0.0 | NFL Rookie of the Month |
| KXNFLFFSEASONTOTAL | SEASON_FANTASY | 36 | 20260922T140549Z | 0.0 | Pro Football Player's Fantasy Season Total |
| KXNFLMVPSPECIALS | UNKNOWN_NEEDS_CLASSIFICATION | 14 | 20260922T140549Z | 0.0 | NFL MVP Award Specials |
| KXNFLLONGESTPLAY | SEASON_SPECIAL | 5 | 20260922T140549Z | 0.0 | NFL Longest Touchdown |
| KXNFLDPOYSPECIALS | UNKNOWN_NEEDS_CLASSIFICATION | 2 | 20260922T140549Z | 0.0 | NFL Defensive Player of the Year Specials |
| KXNFLOPOYSPECIALS | UNKNOWN_NEEDS_CLASSIFICATION | 2 | 20260922T140549Z | 0.0 | NFL Offensive Player of the Year Specials |
| KXNFLFFPTSLADDER | SEASON_FANTASY | 0 | 20260922T140549Z | 0.0 | Fantasy Ladder |
| KXNFLFFWEEKLEAD | WEEK_LEADER | 0 | 20260922T140549Z | 0.0 | Weekly Fantasy Football Leader |
| KXNFLFFWEEKTOP | WEEK_LEADER | 0 | 20260922T140549Z | 0.0 | Weekly Fantasy Football Top Players |
| KXNFLLADDERREC | UNKNOWN_NEEDS_CLASSIFICATION | 0 | 20260922T140549Z | 0.0 | Receptions Ladder |
| KXNFLWEEKTIE | WEEK_EVENT | 0 | 20260922T140549Z | 0.0 | NFL Weekly Tie |
| KXSBLSPREAD | SUPER_BOWL_EVENT | 0 | 20260922T140549Z | 0.0 | Slovakia SBL Spread |
| KXSBLTOTAL | SUPER_BOWL_EVENT | 0 | 20260922T140549Z | 0.0 | Slovakia SBL Total |

## UNCLASSIFIED

| series | open | title |
|---|---|---|
| KXNFLMVPSPECIALS | 14 | NFL MVP Award Specials |
| KXNFLDPOYSPECIALS | 2 | NFL Defensive Player of the Year Specials |
| KXNFLOPOYSPECIALS | 2 | NFL Offensive Player of the Year Specials |
| KXNFLLADDERREC | 0 | Receptions Ladder |

## CAPTURE_GAP (open contracts never confirmed open by any capture run)

| series | open | never seen | in registry | tier |
|---|---|---|---|---|
| KXNFLWEEKHIGHSCORE | 480 | 480 | False | None |
| KXNFLPOTM | 200 | 200 | False | None |
| KXNFLFFPLAYOFFLEADER | 75 | 75 | False | None |
| KXNFLROTM | 60 | 60 | False | None |
| KXNFLFFSEASONTOTAL | 36 | 36 | False | None |
| KXNFLMVPSPECIALS | 14 | 14 | False | None |
| KXNFLLONGESTPLAY | 5 | 5 | False | None |
| KXNFLDPOYSPECIALS | 2 | 2 | False | None |
| KXNFLOPOYSPECIALS | 2 | 2 | False | None |

## NEW_MARKET_STRUCTURES: 31 contracts on PROVEN families did not parse PROVEN

* KXNFLFG-26SEP24ATLGB-GB4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP24ATLGB-GB3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP24ATLGB-GB2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP24ATLGB-GB1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP24ATLGB-ATL4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP24ATLGB-ATL3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP24ATLGB-ATL2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP24ATLGB-ATL1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-CWOERNER89 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-ZBRANCH17 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-OZACCHEAUS14 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-NO-TD (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-KPITTS8 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-JDOTSON4 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-DLONDON5 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-BROBINSON7 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-ATLDST (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-ATL-AHOOPER81 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-GB-TKRAFT85 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP24ATLGB-GB-SMOORE23 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
