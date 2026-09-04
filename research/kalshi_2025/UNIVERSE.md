# Kalshi NFL archived universe (historical tier, backfilled 2026-09-04)

Source: `GET /historical/markets?series_ticker=…` for every registry series except parlay/combo families
(KXMVENFLMULTIGAMEEXTENDED alone holds 1,991,987 archived multivariate contracts and is excluded). 381 series files,
**61,557 archived markets, 61,068 settled**, close times 2025-01-12 → 2026-06-17 (i.e. the 2024 playoffs, the full 2025
season incl. preseason and playoffs, and 2025-26 futures). 48,127 join to an nflverse game by (date, away, home);
the rest are futures/awards/draft or preseason games absent from the nflverse schedule.

| family | markets | settled | YES rate | median volume ($ contracts) | traded share |
|---|---|---|---|---|---|
| player ladders (PLAYER_STAT) | 34,032 | 33,684 | 0.349 | 667 | 0.87 |
| spread ladder (full game) | 7,420 | 7,420 | 0.219 | 3,396 | 0.62 |
| total ladder (full game) | 5,918 | 5,918 | 0.509 | 3,260 | 0.62 |
| first TD scorer | 5,487 | 5,355 | 0.047 | 1,121 | 0.88 |
| draft | 2,768 | 2,768 | 0.088 | 983 | 0.83 |
| game winner | 666 | 666 | — | — | — |
| team totals | 809 | 809 | — | — | — |
| 1H/1Q spreads & totals, period winners | < 100 each | | | (2025 launched late in the season) | |

Player ladders by statistic (settled): receiving yards 10,170 (YES 40.2%, median volume 400), touchdowns 7,471 (16.2%,
4,266), receptions 7,358 (43.2%, 82), rushing yards 4,625 (41.8%, 1,058), passing yards 3,248 (36.1%, 1,292),
passing TDs 812 (37.4%, 915).

What this enables (once the per-market 60-min/1-min bid-ask candlesticks and trades finish backfilling):
market calibration by family × threshold × time-to-kickoff, ladder monotonicity at each horizon, prop-market
efficiency vs our distribution families on the exact rungs Kalshi listed, and CLV-style analysis of early vs late
prices for the whole 2025 season. Kalshi player UUID → GSIS map for 2025: 454 resolved (424 exact name+team), 98
unresolved of which most are team D/ST or "no touchdown" legs (now tagged NOT_A_PLAYER).
