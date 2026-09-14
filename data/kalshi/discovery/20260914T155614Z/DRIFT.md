# Discovery -> registry drift (20260914T155614Z)

Registry holds 392 series; discovery lists 460 NFL candidates.

| quantity | n |
|---|---|
| new_series | 7 |
| new_series_open_markets | 778 |
| unclassified_series | 8 |
| capture_gap_contracts | 778 |
| capture_gap_contracts_outside_registry | 778 |

## NEW_SERIES (not in the reviewed registry)

| series | family | open | first seen | lag (days) | title |
|---|---|---|---|---|---|
| KXNFLFFWEEKLEAD | UNKNOWN_NEEDS_CLASSIFICATION | 254 | 20260914T155614Z | 0.0 | Weekly Fantasy Football Leader |
| KXNFLPOTM | UNKNOWN_NEEDS_CLASSIFICATION | 200 | 20260914T155614Z | 0.0 | NFL Player of the Month |
| KXNFLFFWEEKTOP | UNKNOWN_NEEDS_CLASSIFICATION | 148 | 20260914T155614Z | 0.0 | Weekly Fantasy Football Top Players |
| KXNFLFFPLAYOFFLEADER | UNKNOWN_NEEDS_CLASSIFICATION | 75 | 20260914T155614Z | 0.0 | Fantasy Football Playoffs Leader |
| KXNFLROTM | UNKNOWN_NEEDS_CLASSIFICATION | 60 | 20260914T155614Z | 0.0 | NFL Rookie of the Month |
| KXNFLFFSEASONTOTAL | UNKNOWN_NEEDS_CLASSIFICATION | 36 | 20260914T155614Z | 0.0 | Pro Football Player's Fantasy Season Total |
| KXNFLLONGESTPLAY | UNKNOWN_NEEDS_CLASSIFICATION | 5 | 20260914T155614Z | 0.0 | NFL Longest Touchdown |

## UNCLASSIFIED

| series | open | title |
|---|---|---|
| KXNFLFFWEEKLEAD | 254 | Weekly Fantasy Football Leader |
| KXNFLPOTM | 200 | NFL Player of the Month |
| KXNFLFFWEEKTOP | 148 | Weekly Fantasy Football Top Players |
| KXNFLFFPLAYOFFLEADER | 75 | Fantasy Football Playoffs Leader |
| KXNFLROTM | 60 | NFL Rookie of the Month |
| KXNFLFFSEASONTOTAL | 36 | Pro Football Player's Fantasy Season Total |
| KXNFLLONGESTPLAY | 5 | NFL Longest Touchdown |
| KXTENNCOACH | 0 | Tennessee Pro Football Team Next Coach |

## CAPTURE_GAP (open contracts never confirmed open by any capture run)

| series | open | never seen | in registry | tier |
|---|---|---|---|---|
| KXNFLFFWEEKLEAD | 254 | 254 | False | None |
| KXNFLPOTM | 200 | 200 | False | None |
| KXNFLFFWEEKTOP | 148 | 148 | False | None |
| KXNFLFFPLAYOFFLEADER | 75 | 75 | False | None |
| KXNFLROTM | 60 | 60 | False | None |
| KXNFLFFSEASONTOTAL | 36 | 36 | False | None |
| KXNFLLONGESTPLAY | 5 | 5 | False | None |

## NEW_MARKET_STRUCTURES: 36 contracts on PROVEN families did not parse PROVEN

* KXNFLFG-26SEP14DENKC-KC4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP14DENKC-KC3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP14DENKC-KC2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP14DENKC-KC1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP14DENKC-DEN4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP14DENKC-DEN3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP14DENKC-DEN2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP14DENKC-DEN1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLTEAMFIRSTTD-26SEP14DENKC-KC-JBRININGSTOOL88 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-NO-TD (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-KC-NO-TD (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-TFRANKLIN11 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-RHARVEY12 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-PBRYANT13 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-MMIMS19 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-LHUMPHREY5 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-JWADDLE17 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-JDOBBINS27 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-JCOLEMAN20 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
* KXNFLTEAMFIRSTTD-26SEP14DENKC-DEN-EENGRAM1 (FIRST_TD_TEAM/FULL, structured): LIKELY ["player scores his TEAM's first touchdown (KXNFLTEAMFIRSTTD); scoring order + identity"]
