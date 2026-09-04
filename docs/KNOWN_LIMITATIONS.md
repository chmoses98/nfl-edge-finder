# Known limitations (2026-09-04)

1. **No timestamped sportsbook lines.** The only free historical line is the nflverse consensus (near-close, vintage undocumented). Opening/midweek research on game markets must use Kalshi's own history, which we started recording today; historical Kalshi candlesticks (bid/ask, 1-min) exist for the 2025 season via the backfill but there are no historical order books.
2. **Injury feed.** nflverse injuries have no intra-week timestamps and the 2026 file is not published yet; daily depth-chart/roster vintages are the timestamped proxy. Sleeper/ESPN runner-side feeds are unverified candidates.
3. **Participation/coverage data arrives after the season.** Matchup features built from it are priors, not current-week features.
4. **GitHub cron is best-effort.** Capture cadence is nominally 10 minutes; expect gaps. `trigger_source` in manifests exposes them. An external dispatcher needs the owner's PAT.
5. **Game model v1 has no edge vs the close** (documented in research/game_model/RESULTS.md). Nothing in this repo is validated for betting.
6. **Player-prop settlement**: inactive/no-snap players settle at a fair price, a third outcome the pricing layer must model.
7. **Sandbox egress** blocks Kalshi/NWS/ESPN; all live collection depends on GitHub Actions availability.
8. **Storage growth** on `market-data` is unmeasured beyond day one (~14 MB after the first discovery+capture); compaction is planned, not built.
9. **Kalshi player UUID map** resolves 121/141 players exactly; 20 are flagged for review and must not be used in pricing until resolved.
