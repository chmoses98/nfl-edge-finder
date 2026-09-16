# Week 1 2026 -- DEVELOPMENT / DIAGNOSTIC -- Week 1 2026 was inspected before this layer was built; not validation

Universe: the newest incumbent ledger snapshot at or before kickoff - 75 min for each kickoff cluster; features from games completed 4 h before that instant; settlement from the nflverse box score.  Market = quoted midpoint (research, not executable).

## By family

| family | n | market mid | incumbent | football-only | reconciled (n) |
|---|---|---|---|---|---|
| GAME_WINNER | 32 | 0.2106 | 0.2072 | 0.2006 | None (0) |
| PLAYER_STAT | 5538 | 0.1564 | 0.1755 | 0.1623 | 0.1413 (4369) |
| SPREAD | 404 | 0.2142 | 0.2142 | 0.2098 | None (0) |
| TEAM_TOTAL | 438 | 0.1496 | 0.1476 | 0.1451 | None (0) |
| TOTAL | 304 | 0.1762 | 0.1761 | 0.1744 | None (0) |

## Player statistics (Brier)

| stat | n | market mid | incumbent | football-only | reconciled | mean mid / football / incumbent / rate |
|---|---|---|---|---|---|---|
| attempts | 352 | 0.2255 | 0.2302 | 0.2188 | None | 0.417 / 0.502 / 0.54 / 0.440 |
| carries | 465 | 0.2341 | 0.2877 | 0.2306 | None | 0.426 / 0.468 / 0.275 / 0.510 |
| completions | 352 | 0.2023 | 0.1894 | 0.1881 | None | 0.413 / 0.463 / 0.517 / 0.466 |
| passing_tds | 129 | 0.1459 | 0.1478 | 0.1433 | 0.1457 | 0.345 / 0.354 / 0.332 / 0.372 |
| passing_yards | 280 | 0.1716 | 0.1759 | 0.1769 | 0.1698 | 0.397 / 0.378 / 0.434 / 0.386 |
| receiving_yards | 1369 | 0.1516 | 0.1694 | 0.1617 | 0.1537 | 0.278 / 0.260 / 0.213 / 0.293 |
| receptions | 1203 | 0.1308 | 0.1574 | 0.1458 | 0.1354 | 0.301 / 0.287 / 0.192 / 0.295 |
| rushing_yards | 764 | 0.1462 | 0.1749 | 0.1579 | 0.1493 | 0.329 / 0.329 / 0.268 / 0.365 |
| touchdowns | 624 | 0.1010 | 0.1073 | 0.1009 | 0.1019 | 0.111 / 0.113 / 0.093 / 0.141 |

## By |disagreement vs mid| band (player props)

| band | football: n | football Brier | market Brier | reconciled Brier | incumbent: n | incumbent Brier | market Brier |
|---|---|---|---|---|---|---|---|
| 0.00-0.05 | 2612 | 0.12806339818529863 | 0.12785856623277184 | 0.11844054598341297 | 2422 | 0.11056020511196009 | 0.10954373451692817 |
| 0.05-0.10 | 1330 | 0.1670544832631579 | 0.16020116541353382 | 0.1464539435541366 | 1095 | 0.17444655340224244 | 0.16514602739726028 |
| 0.10-0.20 | 1065 | 0.19711133686384977 | 0.17723272300469484 | 0.16728696237963148 | 1148 | 0.22640015612567474 | 0.20118135888501743 |
| 0.20-1.01 | 531 | 0.24890970898305084 | 0.2451893126177024 | 0.23963014273131725 | 870 | 0.290386000635436 | 0.21709051724137932 |

## Largest football-only disagreements

| ticker | stat | k | mid | football | reconciled | incumbent | settled | football mean | market mean |
|---|---|---|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP10SFLAR-SFDSTRIBLING7-2` | receptions | 2.0 | 0.765 | 0.077 | 0.466 | 0.317 | 0 | 0.4 | 3.0 |
| `KXNFLRECYDS-26SEP10SFLAR-SFDSTRIBLING7-15` | receiving_yards | 15.0 | 0.685 | 0.109 | 0.207 | 0.421 | 0 | 4.5 | 37.2 |
| `KXNFLREC-26SEP13CLEJAC-CLEDBOSTON12-2` | receptions | 2.0 | 0.670 | 0.113 | 0.431 | 0.318 | 1 | 0.5 | 2.4 |
| `KXNFLRECYDS-26SEP13CLEJAC-CLEDBOSTON12-15` | receiving_yards | 15.0 | 0.680 | 0.139 | 0.274 | 0.405 | 1 | 5.7 | 29.4 |
| `KXNFLRECYDS-26SEP10SFLAR-SFDSTRIBLING7-25` | receiving_yards | 25.0 | 0.585 | 0.063 | 0.202 | 0.29 | 0 | 4.5 | 37.2 |
| `KXNFLREC-26SEP10SFLAR-SFDSTRIBLING7-3` | receptions | 3.0 | 0.555 | 0.034 | 0.372 | 0.189 | 0 | 0.4 | 3.0 |
| `KXNFLRECYDS-26SEP13WASPHI-PHIMLEMON9-15` | receiving_yards | 15.0 | 0.660 | 0.142 | 0.264 | 0.522 | 0 | 5.9 | 29.2 |
| `KXNFLREC-26SEP13WASPHI-PHIMLEMON9-2` | receptions | 2.0 | 0.615 | 0.106 | 0.411 | 0.321 | 1 | 0.5 | 2.2 |
| `KXNFLRSHATT-26SEP13BUFHOU-HOUWMARKS4-11` | carries | 11.0 | 0.120 | 0.615 | nan | 0.413 | 0 | 13.0 | 7.1 |
| `KXNFLRSHATT-26SEP13BUFHOU-HOUWMARKS4-7` | carries | 7.0 | 0.345 | 0.831 | nan | 0.715 | 1 | 13.0 | 7.1 |
| `KXNFLRSHATT-26SEP13ARILAC-ARIJBRISSETT7-1` | carries | 1.0 | 0.430 | 0.914 | nan | 0.493 | 1 | 3.1 | 2.4 |
| `KXNFLREC-26SEP13CLEJAC-JACBTUTEN33-2` | receptions | 2.0 | 0.575 | 0.106 | 0.364 | 0.235 | 0 | 0.5 | 2.0 |
| `KXNFLRSHATT-26SEP13GBMIN-MINAJONES33-12` | carries | 12.0 | 0.120 | 0.576 | nan | 0.294 | 1 | 13.2 | 8.6 |
| `KXNFLRSHATT-26SEP13BUFHOU-HOUWMARKS4-9` | carries | 9.0 | 0.275 | 0.729 | nan | 0.56 | 1 | 13.0 | 7.1 |
| `KXNFLRSHATT-26SEP13TBCIN-CINCBROWN30-13` | carries | 13.0 | 0.380 | 0.833 | nan | 0.314 | 1 | 19.4 | 14.6 |

## Largest incumbent disagreements (the Week-1 failure mode)

| ticker | stat | k | mid | incumbent | football | reconciled | settled |
|---|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26SEP09NESEA-SEAJPRICE8-25` | rushing_yards | 25.0 | 0.875 | 0.219 | 0.761 | 0.787 | 1 |
| `KXNFLRSHYDS-26SEP09NESEA-SEAJPRICE8-30` | rushing_yards | 30.0 | 0.805 | 0.18 | 0.702 | 0.736 | 1 |
| `KXNFLRSHYDS-26SEP09NESEA-SEAJPRICE8-40` | rushing_yards | 40.0 | 0.705 | 0.122 | 0.582 | 0.625 | 1 |
| `KXNFLREC-26SEP13MIALV-LVMMAYER87-3` | receptions | 3.0 | 0.815 | 0.281 | 0.611 | 0.718 | 1 |
| `KXNFLRSHATT-26SEP09NESEA-NERSTEVENSON38-10` | carries | 10.0 | 0.815 | 0.283 | 0.718 | nan | 1 |
| `KXNFLRSHATT-26SEP09NESEA-NERSTEVENSON38-11` | carries | 11.0 | 0.760 | 0.238 | 0.661 | nan | 1 |
| `KXNFLRSHATT-26SEP13NODET-DETJGIBBS0-17` | carries | 17.0 | 0.665 | 0.144 | 0.874 | nan | 1 |
| `KXNFLRSHATT-26SEP13BALIND-BALLJACKSON8-5` | carries | 5.0 | 0.805 | 0.287 | 0.573 | nan | 1 |
| `KXNFLREC-26SEP13MIALV-LVMMAYER87-4` | receptions | 4.0 | 0.675 | 0.157 | 0.456 | 0.606 | 1 |
| `KXNFLRSHATT-26SEP09NESEA-NERSTEVENSON38-12` | carries | 12.0 | 0.715 | 0.199 | 0.602 | nan | 1 |
| `KXNFLRSHATT-26SEP13CLEJAC-CLEDWATSON4-2` | carries | 2.0 | 0.850 | 0.334 | 0.866 | nan | 1 |
| `KXNFLRSHATT-26SEP13NODET-DETJGIBBS0-16` | carries | 16.0 | 0.690 | 0.179 | 0.899 | nan | 1 |
| `KXNFLRSHYDS-26SEP13GBMIN-GBMLLOYD32-25` | rushing_yards | 25.0 | 0.720 | 0.209 | 0.733 | 0.732 | 1 |
| `KXNFLRSHYDS-26SEP13CLEJAC-JACBTUTEN33-25` | rushing_yards | 25.0 | 0.820 | 0.323 | 0.513 | 0.631 | 1 |
| `KXNFLREC-26SEP13NYJTEN-TENCTATE14-2` | receptions | 2.0 | 0.815 | 0.319 | 0.503 | 0.647 | 1 |
