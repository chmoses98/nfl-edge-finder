# Known limitations (2026-09-04)

1. **No timestamped sportsbook lines.** The only free historical line is the nflverse consensus (near-close, vintage undocumented). Opening/midweek research on game markets must use Kalshi's own history, which we started recording today; historical Kalshi candlesticks (bid/ask, 1-min) exist for the 2025 season via the backfill but there are no historical order books.
2. **Injury feed.** nflverse injuries have no intra-week timestamps and the 2026 file is not published yet. Runner-side probes (2026-09-04) confirmed Sleeper players (injury_status, practice_participation, depth_chart_order) and ESPN injuries are reachable and free; `context-capture.yml` now snapshots them every 3 hours with retrieval timestamps. Official practice-report timing is still only as good as those feeds' update latency, which is unmeasured.
3. **Participation/coverage data arrives after the season.** Matchup features built from it are priors, not current-week features.
4. **GitHub cron is best-effort.** Capture cadence is nominally 10 minutes; expect gaps. `trigger_source` in manifests exposes them. An external dispatcher needs the owner's PAT.
5. **Game model v1 has no edge vs the close** (documented in research/game_model/RESULTS.md). Nothing in this repo is validated for betting.
6. **Player-prop settlement**: inactive/no-snap players settle at a fair price, a third outcome the pricing layer must model.
7. **Sandbox egress** blocks Kalshi/NWS/ESPN/Sleeper/Open-Meteo; all live collection depends on GitHub Actions availability. Weather forecasts (NWS + Open-Meteo, with gusts) are now captured per upcoming game every 3 hours; forecast-vintage history before 2026-09-04 must come from Open-Meteo's historical-forecast/previous-runs archives.
8. **Storage growth** on `market-data` is unmeasured beyond day one (~14 MB after the first discovery+capture); compaction is planned, not built.
9. **Kalshi player UUID map** resolves 121/141 players exactly; 20 are flagged for review and must not be used in pricing until resolved.
10. **Kalshi parlay series** (KXMVENFL*, KXNFLPREPACK*) hold millions of archived multivariate contracts and are excluded from backfill; live capture keeps them at LIGHT tier.
