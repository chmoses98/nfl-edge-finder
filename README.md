# nfl-edge-finder

Free-data NFL analytics, projection, and Kalshi market-pricing research platform for game lines, totals, player props, calibration, and edge research.

**Status (2026-09-04): RESEARCH / MARKET CAPTURE.** Nothing here is validated for real-money use. Automatic trade execution is not authorized and not implemented.

## What exists
| area | where | state |
|---|---|---|
| Free-data audit (nflverse, Kalshi, weather, injuries, reference lines) | `docs/DATA_SOURCE_AUDIT.md` | done, verified by download |
| Bronze nflverse downloader with manifests | `scripts/data/nflverse_download.py` | 1999–2026, ~590 MB local (gitignored) |
| Silver tables: games, team-game EPA aggregates, player ID crosswalk, Kalshi player map | `nfl_edge/data/` | rebuildable |
| Kalshi read-only client, discovery, classifier (real-fixture tests), series registry | `nfl_edge/kalshi/`, `config/kalshi_nfl_series.json` | 392 NFL series, 60+ families |
| Prospective capture (10-min conductor), daily discovery, historical backfill | `.github/workflows/`, branch `market-data` | running since 2026-09-04 |
| Game-model study vs closing line | `research/game_model/RESULTS.md` | no edge vs close (documented) |
| Ladder calibration from the line, day-1 microstructure, quick effects, role features, player distribution families | `research/*/RESULTS.md` | see hypothesis registry |
| Pricing primitives (ladder semantics, monotonicity checks) | `nfl_edge/pricing/ladder.py` | tested |

## Run
```
pip install -e . && python -m pytest -q
python scripts/data/nflverse_download.py            # bronze
python nfl_edge/data/silver.py && python nfl_edge/data/ids.py
python scripts/research/game_model_study.py         # example study
git fetch origin market-data                        # Kalshi observations
```
Docs: `docs/ARCHITECTURE.md`, `docs/KALSHI_MARKET_TAXONOMY.md`, `docs/KALSHI_API_NOTES.md`, `docs/KALSHI_CAPTURE.md`, `docs/ROADMAP.md`, `docs/KNOWN_LIMITATIONS.md`, `research/hypothesis_registry/registry.md`.
