# Production health gates (tennis_edge/health/gates.py)

| gate | name | PASS condition | evidence |
|---|---|---|---|
| TENNIS-1 | complete Kalshi tennis discovery | latest discovery complete, catalogue fully paginated, no failures, < 36 h old | data/kalshi/discovery/<run>/summary.json |
| TENNIS-2 | taxonomy normalization | no tennis series outside the family registry; >= 99.5 % of live markets PARSED or explicitly UNSUPPORTED | series_tennis.json + parser |
| TENNIS-3 | active-market mapping | zero UNPARSED among OPEN markets | markets/*.json (open) |
| TENNIS-4 | active-market projection | every open projectable market present in the latest projection run | data/research/projections/latest.json |
| TENNIS-5 | capture freshness | latest capture manifest <= 30 min old, no incomplete stage | data/kalshi/capture/<day>/<run>.manifest.json |
| TENNIS-6 | no post-start leakage | every ledger row generated before actual first ball (or scheduled - 5 min when unknown, counted) | ledger + starts |
| TENNIS-7 | player identity integrity | no AMBIGUOUS mapping used in production | link/mapping summaries |
| TENNIS-8 | sports truth health | >= 98 % of settled predictions have gradeable sports truth | settlement table |
| TENNIS-9 | exchange settlement health | zero unexplained sports/exchange conflicts; no unreviewed important_info id change | settlements + config/kalshi_settlement_rules.json |
| TENNIS-10 | CLV close coverage | canonical close for >= 95 % of settled pregame predictions (basis breakdown reported) | close table |
| TENNIS-11 | probability consistency | no invariant violation across a match's priced markets | payoffs.check_consistency |
| TENNIS-12 | append-only ledger | hash chain intact | data/research/ledger/*.jsonl |
| TENNIS-13 | reproducible artifacts | build manifest hash matches matches.parquet; source run ids recorded | data/processed/build_manifest.json |
| TENNIS-14 | data-source freshness | newest match-data snapshot <= 8 days old and covers the current season | data/sources/*/manifest.json |

UNKNOWN (evidence absent) is treated as not-PASS. Gates are never relaxed to go green; fix the pipeline.
`python -c "from tennis_edge.health.gates import run_all; [print(g.to_dict()) for g in run_all()]"`.
