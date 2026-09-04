# Availability: measured play rates, not assumed ones

`scripts/research/availability_calibration.py`. Kalshi pays a YES holder **$0** when the player is inactive
(docs/KALSHI_SETTLEMENT.md), so P(plays) multiplies every player-prop contract value. These rates were guessed
in the first draft of `nfl_edge/settlement/availability.py`; here they are measured.

## League-wide: 101,917 established-role offensive player-weeks, 2015–2025
A player-week enters the sample if the player had ≥10 offensive snaps in any of the previous three weeks. The
grid is built from every week his team played, so a player who was inactive (and therefore **absent from the
snap-count file**) is counted — the first attempt at this analysis silently dropped exactly those players and
produced the absurd result that Out players play 100% of the time.

| official designation | player-weeks | plays (≥1 snap) | dressed, no snap | did not dress |
|---|---|---|---|---|
| not on the report | 78,954 | 0.885 | 0.029 | 0.086 |
| on the report, no game status | 11,811 | 0.944 | 0.014 | 0.041 |
| Questionable | 5,717 | **0.690** | 0.019 | 0.291 |
| Probable | 1,034 | 0.967 | 0.009 | 0.024 |
| Doubtful | 686 | **0.007** | 0.000 | 0.993 |
| Out | 3,713 | **0.0005** | 0.000 | 0.9995 |

The Questionable rate is remarkably stable: 0.63–0.80 across the eleven seasons, ten of them in 0.65–0.71.
**Doubtful is not "probably out" — it is out**, at 0.7%. The original prior of 0.25 was wrong by a factor of 35.

## The population we actually price: 4,243 player-games Kalshi listed a prop for (2025 archive)
| designation | n | plays | dressed, no snap | did not dress |
|---|---|---|---|---|
| not on the report | 3,470 | 0.971 | 0.005 | 0.024 |
| on the report, no game status | 634 | 0.992 | 0.000 | 0.008 |
| Questionable | 104 | 0.827 | 0.010 | 0.163 |
| Out | 33 | 0.000 | 0.000 | 1.000 |
| Doubtful | 2 | 0.000 | 0.000 | 1.000 |

Kalshi lists props for questionable players it expects to play, so the listed-population rate (0.827) sits above
the league-wide one (0.690); with n = 104 the deployed value shrinks toward the 11-season estimate → **0.78**.
The unconditional listed play rate is 0.962, which is what an UNKNOWN state would be worth if we assumed the
player were typical — we deliberately price UNKNOWN below it (0.90) and raise a quality flag instead.

The fair-price branch ("active but never takes a snap") is 0.5–1.0% in the listed population, consistent with
the 348 scalar settlements found in the archive (~1% of prop rungs).

## Deployed rates
EXPECTED_ACTIVE 0.975 · QUESTIONABLE 0.78 · DOUBTFUL 0.03 · EXPECTED_OUT 0.02 · OUT 0.005 ·
INACTIVE_CONFIRMED 0.0 · UNKNOWN 0.90, with a mild depth-chart adjustment for third/fourth-stringers only.
Registered as H-20260904-008 for prospective recalibration against 2026 outcomes.
