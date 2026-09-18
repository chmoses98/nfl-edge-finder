# Discovery -> registry drift (20260918T134026Z)

Registry holds 392 series; discovery lists 461 NFL candidates.

| quantity | n |
|---|---|
| new_series | 8 |
| new_series_open_markets | 786 |
| unclassified_series | 9 |
| capture_gap_contracts | 786 |
| capture_gap_contracts_outside_registry | 786 |

## NEW_SERIES (not in the reviewed registry)

| series | family | open | first seen | lag (days) | title |
|---|---|---|---|---|---|
| KXNFLFFWEEKLEAD | UNKNOWN_NEEDS_CLASSIFICATION | 254 | 20260918T134026Z | 0.0 | Weekly Fantasy Football Leader |
| KXNFLPOTM | UNKNOWN_NEEDS_CLASSIFICATION | 200 | 20260918T134026Z | 0.0 | NFL Player of the Month |
| KXNFLFFWEEKTOP | UNKNOWN_NEEDS_CLASSIFICATION | 155 | 20260918T134026Z | 0.0 | Weekly Fantasy Football Top Players |
| KXNFLFFPLAYOFFLEADER | UNKNOWN_NEEDS_CLASSIFICATION | 75 | 20260918T134026Z | 0.0 | Fantasy Football Playoffs Leader |
| KXNFLROTM | UNKNOWN_NEEDS_CLASSIFICATION | 60 | 20260918T134026Z | 0.0 | NFL Rookie of the Month |
| KXNFLFFSEASONTOTAL | UNKNOWN_NEEDS_CLASSIFICATION | 36 | 20260918T134026Z | 0.0 | Pro Football Player's Fantasy Season Total |
| KXNFLLONGESTPLAY | UNKNOWN_NEEDS_CLASSIFICATION | 5 | 20260918T134026Z | 0.0 | NFL Longest Touchdown |
| KXNFLWEEKTIE | UNKNOWN_NEEDS_CLASSIFICATION | 1 | 20260918T134026Z | 0.0 | NFL Weekly Tie |

## UNCLASSIFIED

| series | open | title |
|---|---|---|
| KXNFLFFWEEKLEAD | 254 | Weekly Fantasy Football Leader |
| KXNFLPOTM | 200 | NFL Player of the Month |
| KXNFLFFWEEKTOP | 155 | Weekly Fantasy Football Top Players |
| KXNFLFFPLAYOFFLEADER | 75 | Fantasy Football Playoffs Leader |
| KXNFLROTM | 60 | NFL Rookie of the Month |
| KXNFLFFSEASONTOTAL | 36 | Pro Football Player's Fantasy Season Total |
| KXNFLLONGESTPLAY | 5 | NFL Longest Touchdown |
| KXNFLWEEKTIE | 1 | NFL Weekly Tie |
| KXTENNCOACH | 0 | Tennessee Pro Football Team Next Coach |

## CAPTURE_GAP (open contracts never confirmed open by any capture run)

| series | open | never seen | in registry | tier |
|---|---|---|---|---|
| KXNFLFFWEEKLEAD | 254 | 254 | False | None |
| KXNFLPOTM | 200 | 200 | False | None |
| KXNFLFFWEEKTOP | 155 | 155 | False | None |
| KXNFLFFPLAYOFFLEADER | 75 | 75 | False | None |
| KXNFLROTM | 60 | 60 | False | None |
| KXNFLFFSEASONTOTAL | 36 | 36 | False | None |
| KXNFLLONGESTPLAY | 5 | 5 | False | None |
| KXNFLWEEKTIE | 1 | 1 | False | None |

## NEW_MARKET_STRUCTURES: 440 contracts on PROVEN families did not parse PROVEN

* KXNFLFG-26SEP20INDKC-KC4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20INDKC-KC3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20INDKC-KC2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20INDKC-KC1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20INDKC-IND4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20INDKC-IND3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20INDKC-IND2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20INDKC-IND1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20WASDAL-WAS4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20WASDAL-WAS3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20WASDAL-WAS2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20WASDAL-WAS1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20WASDAL-DAL4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20WASDAL-DAL3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20WASDAL-DAL2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20WASDAL-DAL1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20MIASF-SF4 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20MIASF-SF3 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20MIASF-SF2 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
* KXNFLFG-26SEP20MIASF-SF1 (PLAYER_STAT/FULL, greater): LIKELY ['team-level statistic under a player-stat series; no engine yet']
