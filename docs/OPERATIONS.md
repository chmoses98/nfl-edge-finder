# Operations

## Workflows (GitHub Actions, public repo → free minutes)
| workflow | trigger | purpose | output branch |
|---|---|---|---|
| Kalshi NFL Capture Conductor | hourly cron `7 * * * *` + dispatch | loops capture every 10 min for ~5h50m on one runner, hands off to the queued successor | `market-data` |
| Kalshi NFL Capture | dispatch only | single capture pass (manual / external scheduler) | `market-data` |
| Kalshi NFL Discovery | daily 09:17 UTC + dispatch | catalogue refresh, all NFL markets in every status (settlements), endpoint probes; proposes registry additions | `market-data` |
| Kalshi NFL Historical Backfill | dispatch (self-chains) | historical tier market lists + candles + trades | `market-data` |

Manual dispatch from the GitHub UI or API (`POST /repos/chmoses98/nfl-edge-finder/actions/workflows/<file>/dispatches`).
Check health: `git fetch origin market-data && git worktree add /tmp/md origin/market-data && python scripts/ops/health.py --market-data-dir /tmp/md`.

## Failure modes and responses
* `partial=true` in a capture manifest → a series fetch failed; the universe for that run is incomplete. Rows are still valid; do not treat missing tickers as closed.
* 429s in `client_stats` → lower `--rps` (default 4) or reduce `--max-books`.
* Publish conflicts (exit 3) → concurrent writers; the next pass retries. Never force-push `market-data`.
* Conductor gap > 20 min with no manifest → dispatch the conductor manually; check GitHub status.
* Registry `proposed_additions` non-empty after discovery → review and move to `series` with a tier.
* nflverse 2026 files 404 → expected until the season starts; the downloader records the 404 in the manifest.

## Data retention
`market-data` is append-only. Compaction (per-day JSONL → parquet) is planned once a week of data exists; raw JSONL stays as the immutable record.

## Not automated on purpose
Order placement, portfolio access, model promotion, registry tier changes.
