# handicap-reports

Generated RUN NFL handicap packets. **Never merge into `main`.**

* `latest/` — the newest successful report, replaced atomically on every successful run.
  * `latest/slate.md` — read this first.
  * `latest/games/<game_id>.md` — the full canonical per-game document.
  * `latest/manifest.json` — freshness: when it was built and how old the ledger, Kalshi capture and
    context captures were at that moment.
* `state/horizons.json` — which decision horizons (T-24h / T-6h / T-90m / T-30m) have been captured.
* `history/index.jsonl` — one manifest line per published run, for tracing an Actions artifact back to its
  source SHAs, model version and packet SHA.

Evidence only. Nothing on this branch is a bet, a recommendation, or a real-money authority, and no part of
producing it touches Airtable. See `docs/RUN_NFL.md` on `main`.
