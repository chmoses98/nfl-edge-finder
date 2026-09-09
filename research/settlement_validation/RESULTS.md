# Settlement validation against Kalshi's own 2025 settlements

`scripts/research/settlement_archive_validation.py --md /tmp/md --season 2025`

The settlement engine (`nfl_edge/settlement/settle.py`) is re-run over every finalized 2025 Kalshi NFL market
in the archive on `market-data` and compared with Kalshi's actual `result` / `settlement_value_dollars`. This
is the only way to test a semantics reading before it is used on live money-adjacent evidence: a reading built
from the common cases looks perfect until it meets a fumble recovered in the end zone.

## Result

| family | agree | disagree | agreement | refused (fail closed) |
|---|---|---|---|---|
| GAME_WINNER | 528 | 0 | 1.000 | 0 |
| SPREAD (full game) | 5,455 | 0 | 1.000 | 103 (1H/2H periods) |
| TOTAL (full game) | 4,301 | 0 | 1.000 | 92 (1H/2H periods) |
| TEAM_TOTAL | 701 | 0 | 1.000 | 0 |
| PLAYER_STAT | 4,024 | 12 | 0.99703 | 1,922 (all KXNFL2TD, no parseable strike) |
| **overall** | **15,009** | **12** | **0.99920** | |

Every full-game team market Kalshi settled in 2025 is reproduced exactly from nflverse final scores. Refusals
are all deliberate: period markets (1H/2H) have no period scores in the free schedule feed, and KXNFL2TD
tickers carry no numeric strike, so the threshold cannot be proven and is not assumed to be 2.

## What the cross-check found that a reading would not

**1. A fumble recovered in the end zone is a touchdown, and lives in its own column.**
Two anytime-touchdown markets settled YES on players nflverse credits with zero rushing, receiving,
special-teams and defensive touchdowns:

* `KXNFLANYTD-25DEC14ARIHOU-HOUWMARKS27` — Woody Marks, `2025_15_ARI_HOU`
* `KXNFLANYTD-25OCT05TENARI-TENTLOCKETT4` — Tyler Lockett, `2025_05_TEN_ARI`

Both have `fumble_recovery_tds = 1`. Kalshi was right and the first reading of "touchdowns scored" was wrong.
`TOUCHDOWN_COLUMNS` now sums rushing + receiving + special-teams + defensive + fumble-recovery touchdowns.
A defensive end-zone fumble recovery can appear in both `def_tds` and `fumble_recovery_tds` (one 2025
player-game shows both), which cannot change a 1+ contract but could double-count a 2+ one, so a touchdown
threshold of 2 or more with both columns non-zero is refused rather than settled.

**2. Return touchdowns count.** Eight YES settlements are players whose only touchdown was a kick or punt
return (Rashid Shaheed twice, Marvin Mims Jr., Ray Davis, Chimere Dike, Parker Washington, Kalif Raymond,
Malik Washington). The unqualified "touchdowns scored" reading is confirmed by Kalshi's own settlements.

**3. Four Kalshi settlements contradict the game's own final score.** All were settled on 2025-12-22, weeks
to months after kickoff, in one batch — including `KXNFLTOTAL-25NOV02ATLNE-ABOVE`, "over **0.5** total points",
settled NO on a game that scored 47. `KXNFLSPREAD-25SEP28CARNE-NE22` and `KXNFLTOTAL-25SEP28WASATL-38.5` are
the same shape, and `KXNFLANYTD-25SEP14SFNO-SFJJENNINGS15` settled at the no-snap fair price for a player with
62 offensive snaps and a receiving touchdown. These are counted separately as
`kalshi_late_bulk_settlement`, not folded into the agreement rate: an engine that "agreed" with them would be
wrong about the football.

**4. The 12 genuine player disagreements are one anomalous day.** Every one is an anytime-touchdown market
from **2025-09-07** (week 1) on a player who finished with an empty stat line; Kalshi paid the
active-but-no-snap fair price even for players with 4 to 37 offensive snaps, which its own rules text says
settles on touchdowns scored. It never recurs across the remaining 17 weeks and the postseason (4,024
agreements). The engine keeps the reading that matches both the rules text and the football fact: a player
who took offensive snaps and recorded nothing settled NO.

## Consequences carried into the engine

* `fumble_recovery_tds` added to the touchdown sum; 2+ thresholds refused when double counting is possible.
* A player with proven snaps and **no** statistics row in a **published** table recorded a proven zero
  (`zero_row` evidence), rather than being refused for a missing value. This is the same explicit zero-row
  rule the pricing side already applies, and it is what makes the low rungs of a ladder evaluable.
* Absence of a snap-count row is never read as inactivity: it is `REFUSED_PARTICIPATION_UNPROVEN`.
