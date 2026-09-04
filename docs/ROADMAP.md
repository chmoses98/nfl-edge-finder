# Roadmap (evidence-driven)

| milestone | status 2026-09-04 | next scientific step |
|---|---|---|
| A free data + market audit | done (docs/DATA_SOURCE_AUDIT.md) | probe Sleeper/ESPN/NWS/Open-Meteo from Actions; add runner-side weather + availability collectors |
| B schemas + entity resolution | done v1 (silver tables, crosswalk, Kalshi player map, tests) | resolve 20 flagged Kalshi player ids; coach/coordinator table |
| C Kalshi discovery/backfill/capture | running (discover daily, capture 10-min, backfill chaining) | verify cron delivery over 48h; measure storage; add compaction; external dispatcher if delivery < 80% |
| D point-in-time research dataset | v1 (team_game, ratings snapshots, player research table) | injury/depth-chart vintage features; QB starter change; weather forecast archive |
| E market baselines + game model | done v1 — REJECTED as edge vs close | market-as-prior joint simulation; alternate-spread/total ladder calibration from margin distribution |
| F player opportunity + distributions | in progress (distribution family study) | opportunity model (snaps/routes/targets) conditional on depth-chart vintage; injury reallocation |
| G ladder pricing | not started | price every open ladder from F's distributions; monotonicity + market consistency checks |
| H edge lab | registry seeded (7 hypotheses) | replicate published effects with held-out seasons; FDR discipline |
| I calibration + market residual | not started (needs prospective data) | hierarchical calibration by family × threshold after ≥4 weeks of 2026 |
| J full-universe shadow | design only | shadow ledger writing every priced market each capture window |
| K bet selection / best expression | not started | requires I and J |
| L production | NOT EARNED | — |
