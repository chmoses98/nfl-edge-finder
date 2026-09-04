# Kalshi prospective capture & the `market-data` branch

## Why
Kalshi's API has no historical order books, and its live tier forgets settled markets after the historical cutoff.
Everything we do not record ourselves — books, timing of moves, pregame vs live states — cannot be reconstructed later.
Capture therefore started on 2026-09-04, five days before kickoff, before any model existed.

## What runs where
| workflow | cadence | what | writes |
|---|---|---|---|
| `kalshi-discover.yml` | daily 09:17 UTC + manual | full series catalogue, all NFL series' markets in every status (this is also how settlements/results get recorded), endpoint probes | `data/kalshi/discovery/<run_id>/` |
| `kalshi-capture.yml` | every 10 min (GitHub cron, best effort) + manual/external dispatch | quotes for every open market of FULL+LIGHT series (change-suppressed), order books within 72h of kickoff (pregame only; post-kickoff books go to a separate live file), global trade tape filtered to NFL series | `data/kalshi/capture/<date>/<run_id>.{quotes,books,live,trades}.jsonl`, `.manifest.json`, `state.json` |
| `kalshi-backfill.yml` | manual, self-chaining | historical tier: archived market lists per series, then per-market 60-min + 1-min candlesticks and trades for single-game families | `data/kalshi/backfill/` |

All three publish to the orphan branch **`market-data`** via `scripts/ci/publish_market_data.py` (fetch → copy new files → commit → push, rebase-retry; conflicts fail loudly instead of committing markers). Code branches gitignore `data/kalshi/`. Discovery and capture share a concurrency group; backfill has its own so a 5-hour backfill never blocks a 10-minute capture.

## Row provenance
Every quote row carries `run_id`, `observed_at` (UTC), `trigger_source` (manifest), the classifier output (family, period, stat, team, player, threshold, operator), the nflverse `game_id` and `kickoff_utc` from the schedule join, `minutes_to_kickoff`, `pregame` flag, all raw price/volume/OI/status fields, and a fingerprint. Unchanged markets are counted per run in the manifest (so "no row" ≠ "no market"). A series whose fetch failed is listed in `manifest.errors` and the run exits non-zero (PARTIAL), never as an empty universe.

## Timing windows
Labels (OPEN, T-48H, T-24H, T-12H, T-6H, T-3H, T-90M, T-60M, T-30M, CLOSE) are **derived at research time** from `minutes_to_kickoff` rather than baked into capture, so a delayed cron does not mislabel a snapshot. The nearest observation to each label is used with its actual distance recorded; a window with no observation within tolerance is reported as MISSED, not backfilled.

## Known risks
* GitHub cron delivery is unreliable (the CFB project measured ~2% delivery over one stretch). Mitigation: `trigger_source` is recorded so a dead scheduler is visible in the manifests; an external 5–10 minute dispatcher (e.g. cron-job.org POSTing `workflow_dispatch` with a fine-grained PAT) is the documented upgrade path and needs the owner's credentials.
* Storage: ~50–150 KB per run compressed in git at 144 runs/day; order-book files dominate near game time. Growth is reviewed weekly; parquet compaction of closed days is the planned mitigation.
* Kalshi may add series: the daily discovery run diffs the catalogue against the registry and lists `proposed_additions` for review; until reviewed they are not captured at FULL tier.
