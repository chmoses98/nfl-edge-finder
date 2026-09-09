# Settlement validation against Kalshi's own 2025 settlements

`scripts/research/settlement_archive_validation.py --md /tmp/md --season 2025`

The settlement engine (`nfl_edge/settlement/settle.py`) is re-run over every finalized 2025 Kalshi NFL market in
the archive on `market-data` and compared with Kalshi's actual `result` / `settlement_value_dollars`. This is the
only way to test a semantics reading before it is used on live money-adjacent evidence: a reading built from the
common cases looks perfect until it meets a fumble recovered in the end zone.

## What was examined, and what the agreement rate is over

The headline rate is over **independently comparable settlements**, not over markets examined. Every market that
drops out is counted, and the buckets reconcile to the examined total exactly (`reconciles: true`, asserted by
`tests/test_archive_validation_report.py`).

| bucket | markets |
|---|---|
| finalized archive markets examined | **61,557** |
| in a settleable family | 49,089 |
| dropped: family this engine does not settle | 12,468 |
| dropped: did not join a scheduled game | 6,348 |
| dropped: player identity unresolved *(name-based, research only)* | 25,598 |
| dropped: engine refused on semantics | 2,117 |
| set aside: Kalshi late bulk settlement | 5 |
| **independently comparable settlements** | **15,021** |
| agreements | 15,009 |
| disagreements | 12 |
| **agreement on comparable settlements** | **0.99920** |

The 25,598 identity drops are an artifact of THIS script, not of production: it matches players by name against
the players who appear in the game's stats and snap tables, so anyone who never appeared cannot be matched.
Production settles on the GSIS id resolved at pricing time and does not use names at all.

The 2,117 semantic refusals are deliberate: 1,922 `KXNFL2TD` markets carry no parseable strike (the threshold is
never assumed to be 2), and 195 are 1H/2H period markets, which have no period scores in the free feed.

## Coverage per family this engine settles in production

| family | archive markets examined | comparable | agreement | evidence |
|---|---|---|---|---|
| GAME_WINNER | 666 | 528 | 1.00000 | archive cross-check + rules text + unit tests |
| SPREAD (full game) | 7,548 | 5,455 | 1.00000 | archive cross-check + rules text + unit tests |
| TOTAL (full game) | 6,034 | 4,301 | 1.00000 | archive cross-check + rules text + unit tests |
| TEAM_TOTAL | 809 | 701 | 1.00000 | archive cross-check + rules text + unit tests |
| PLAYER_STAT | 34,032 | 4,036 | 0.99703 | archive cross-check + rules text + unit tests |
| **BOTH_TEAMS_SCORE_N** | **0** | **0** | — | **rules text + unit tests ONLY** |

`BOTH_TEAMS_SCORE_N` is the honest gap: Kalshi's `KXNFLBOTH` series is not in the historical archive this repo
holds, so **no archived market has ever exercised its settlement path**. Its evidence is the contract's own rules
text ("If both teams score N+ points…") and the unit tests in `tests/test_postgame_settlement.py`, and it should
not be read as archive-validated. Every other production family is.

## What the cross-check found that a reading would not

**1. A fumble recovered in the end zone is a touchdown, and lives in its own column.**
Two anytime-touchdown markets settled YES on players nflverse credits with zero rushing, receiving,
special-teams and defensive touchdowns:

* `KXNFLANYTD-25DEC14ARIHOU-HOUWMARKS27` — Woody Marks, `2025_15_ARI_HOU`
* `KXNFLANYTD-25OCT05TENARI-TENTLOCKETT4` — Tyler Lockett, `2025_05_TEN_ARI`

Both have `fumble_recovery_tds = 1`. Kalshi was right and the first reading of "touchdowns scored" was wrong.
`TOUCHDOWN_COLUMNS` now sums rushing + receiving + special-teams + defensive + fumble-recovery touchdowns. A
defensive end-zone fumble recovery can appear in both `def_tds` and `fumble_recovery_tds` (one 2025 player-game
shows both), which cannot change a 1+ contract but could double-count a 2+ one, so a touchdown threshold of 2 or
more with both columns non-zero is refused rather than settled.

**2. Return touchdowns count.** Eight YES settlements are players whose only touchdown was a kick or punt return
(Rashid Shaheed twice, Marvin Mims Jr., Ray Davis, Chimere Dike, Parker Washington, Kalif Raymond, Malik
Washington). The unqualified "touchdowns scored" reading is confirmed by Kalshi's own settlements.

**3. Five Kalshi settlements contradict the game's own final score.** All were settled weeks to months after
kickoff in bulk sweeps — including `KXNFLTOTAL-25NOV02ATLNE-ABOVE`, "over **0.5** total points", settled NO on a
game that scored 47. They are counted as `set_aside_kalshi_late_bulk_settlement`, not folded into the agreement
rate: an engine that "agreed" with them would be wrong about the football.

**4. The 12 genuine player disagreements are one anomalous day.** Every one is an anytime-touchdown market from
**2025-09-07** (week 1) on a player who finished with an empty stat line; Kalshi paid the active-but-no-snap
scalar even for players with 4 to 37 offensive snaps, which its own rules text says settles on touchdowns scored.
It never recurs across the remaining 17 weeks and the postseason (4,024 agreements). The engine keeps the reading
that matches both the rules text and the football fact: a player who took offensive snaps and recorded nothing
settled NO.

## Consequences carried into the engine

* `fumble_recovery_tds` added to the touchdown sum; 2+ thresholds refused when double counting is possible.
* A player with proven snaps and **no** statistics row in a **published** table recorded a proven zero
  (`zero_row` evidence), rather than being refused for a missing value. This is the same explicit zero-row rule
  the pricing side already applies, and it is what makes the low rungs of a ladder evaluable.
* Absence of a snap-count row is never read as inactivity: it is `REFUSED_PARTICIPATION_UNPROVEN`.
* The active-but-never-played branch settles at the exchange's own `settlement_value_dollars` and at nothing
  else. In this validation that value comes from the archive record itself; in production it comes from a pinned
  settlement snapshot, and where it is unavailable the row is `REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE` with the
  participation branch still recorded as proven. A pregame midpoint is a pricing-time proxy for that branch and
  is never recorded as the payout.
