# MORNING REPORT — tennis-edge-finder (session of 2026-09-11)

## EXECUTIVE VERDICT

**We built a working, tested, fail-closed tennis research platform that discovers and prices the whole
Kalshi tennis universe, captures it prospectively, and benchmarks its models honestly. The honest result:
every model we built is worse than both Pinnacle and Kalshi's own pregame price. There is no evidence of
edge. Real-money authority stays OFF.**

1. **What was built.** A local project `tennis-edge-finder/` (7,200 lines of Python, 215 passing tests):
   Kalshi tennis discovery + taxonomy + market parser (165k markets, 99.9 % parsed), a 10-minute prospective
   capture loop (quotes, orderbooks, global trade tape, settlements, candles), a canonical 1.6 M-match
   historical table with validation/quarantine/provenance, identity layer, a data-driven scoring-format
   registry, an exact DP scoring engine validated against Monte Carlo, Elo family + structural serve/return
   models, walk-forward evaluation with bookmaker and Kalshi benchmarks, fee model, append-only hash-chained
   ledger, sports-vs-exchange truth objects, canonical close/CLV logic, draw DP for futures, doubles
   baseline interface, 14 health gates, and `scripts/run_tennis.py` which prices every open projectable
   market from one coherent distribution per match and writes the owner-facing report.
2. **Data acquired** (all on the `tennis-data` branch with sha256 manifests): Sackmann ATP + WTA snapshots
   from public forks (upstream repos are gone; ATP rows end 2026-06-01, WTA 2026-04-27), TML-Database ATP
   1968-2026, TML Challenger 2000-2026 and tennis-data.co.uk ATP 2020-2026 odds workbooks via a mirror
   (the primary site returned 503 to every request), Match Charting Project stat files, the full Kalshi
   series catalogue (13,971 series), 143 tennis series with 61,592 live + 103,962 archived markets,
   15,894 markets' hourly candles and 13.1 M trade rows, 286 contract-terms PDFs.
3. **Historical coverage.** 1,624,759 clean singles matches 1990-2026 (ATP 953k incl. 519k ITF and 282k
   Challenger; WTA 671k incl. 468k ITF, 48k WTA-125); 13,729 rows quarantined with reasons; 142,827
   cross-source duplicates dropped. Serve stats on 61-81 % of tour/Challenger rows, 5 % of ITF.
4. **Kalshi universe discovered.** 143 tennis-tagged series covering ATP/WTA/Challenger/ITF men & women,
   singles and doubles, mixed, team events, exhibitions, match winner, set winner, exact score, game
   totals, game spreads, set totals/spreads, tiebreak, aces, in-play game winners, tournament winners,
   round advancement, nationality props, season markets, novelty markets (docs/KALSHI_MARKET_TAXONOMY.md).
5. **Families projectable now:** MATCH_WINNER (singles all levels; doubles via an unvalidated baseline),
   SET_WINNER, EXACT_SET_SCORE, TOTAL_GAMES, GAME_SPREAD, TOTAL_SETS, SET_SPREAD, TIEBREAK, ANY_SET.
   Built but not wired (no draw feed): TOURNAMENT_WINNER, ROUND_ADVANCE. Not priced: aces, in-play,
   season/novelty, team competition winners.
6. **Models:** naive rank, Elo (plain, level prior, surface-pooled, level-K, K variants), structural
   serve/return (three shrinkage settings), logit ensemble, doubles baseline, market-model hybrid.
7. **Best out of sample:** the ENSEMBLE (Elo + structural) — Brier 0.2111 on 13,323 Pinnacle-linked ATP
   matches; among Elo-only variants elo_levelprior/elo_plain on all-level corpora (WTA 299k matches: Brier
   0.1933, naive rank baseline 0.2196).
8. **Did anything beat the market? No.** Pinnacle 0.2026 vs ensemble 0.2111 (paired bootstrap CI excludes
   zero); walk-forward hybrid puts a small NEGATIVE weight on the model. Kalshi's conservative pregame quote
   (≥ 7 h before close) Brier 0.1871 vs our frozen model 0.2060 on 1,869 settled markets.
9. **Calibration:** ensemble slope 1.04 (ATP) — calibrated; Elo with K0 ≥ 250 over-confident (slope
   0.83-0.89). Markets: Pinnacle 1.02, Kalshi 1.01.
10. **Strongest:** Grand Slam / tour-level matches with serve evidence; KXATPMATCH is the only slice where the
    ensemble's log-loss equals Kalshi's (n = 167 — not evidence).
11. **Weakest:** ITF and Challenger (Elo-only, no serve stats), WTA (stale to April), any market whose
    "scheduled" time is nominal (ITF/Challenger), doubles.
12. **Evidence of signal:** structural > Elo, ensemble > both, consistently across seasons — the models
    contain real information, just less than the market already has.
13. **Evidence of model error:** disagreement buckets — when the model and market differ by > 20 pp the
    model-favoured side wins 32.5 % (market says 35 %); every Kalshi disagreement bucket loses after fees.
14. **Blocked:** sandbox egress (Kalshi, kalshi docs, tennis sites, tennis-data.co.uk, wikipedia, github raw
    for other repos); tennis-data.co.uk 503; upstream Sackmann repos 404; no first-ball feed; no draw feed.
15. **Needs credentials:** Kalshi authenticated orderbook/WebSocket (adapter interface only), Kaggle (WTA
    odds mirrors), any paid live-score API.
16. **Before prospective capture is complete:** move workflows to the default branch (so `schedule:` crons
    replace the self-dispatch chain), add a first-ball/live-score adapter, add daily Sackmann/TML refresh
    (weekly rebuild of matches.parquet + states), settle ledger rows automatically (settlement stream →
    SportsTruth/ExchangeTruth → canonical close → CLV), fix the 19 name-recovery events and the 4 unmapped
    players, wire draws for futures.
17. **Before real-money authority could ever turn on:** a pre-registered prospective window (≥ 1,000
    pregame-valid match-winner rows, ≥ 8 weeks) in which some model column beats the Kalshi mid on log-loss
    with CI excluding zero AND shows non-negative executable CLV after fees; then a human decision.

## DATA SOURCE MATRIX
See docs/DATA_SOURCES.md (21-column registry with CONFIRMED / UNKNOWN / UNUSABLE labels and licences).
Summary: Sackmann forks (CONFIRMED, CC BY-NC-SA, stale by 3-4 months), TML (CONFIRMED, research-only terms),
tennis-data.co.uk (UNUSABLE direct; ATP 2020-26 via mirror), MCP (CONFIRMED), Kalshi public API (CONFIRMED,
runner only), official tours / live scores / draws (UNKNOWN — unreachable), Kaggle (UNKNOWN — auth).

## ARCHITECTURE
docs/ARCHITECTURE.md. Runner-side acquisition/capture → orphan `tennis-data` branch → local build/models/
projections/ledger/gates. One MatchDistribution per match; every family a functional of it.

## CURRENT KALSHI TAXONOMY
docs/KALSHI_MARKET_TAXONOMY.md and config/kalshi_tennis_series.json. Settlement rules harvested into
config/kalshi_settlement_rules.json: tour match series → walkover = fair price, retirement after first ball =
retiring player NO; ITF → $0.50 on no ball; derivative markets settle what is determined, else fair price.
3 % of all finalized tennis contracts settled scalar.

## DATA QUALITY REPORT
| item | value |
|---|---|
| clean rows / quarantined | 1,624,759 / 13,729 (DUPLICATE_MATCH_KEY 8,964; IMPOSSIBLE_SCORE 4,260; MISSING_PLAYER_ID 490; SELF_MATCH 15) |
| largest quarantine pocket (fixed) | WTA qual/ITF wrote match tiebreaks as a bare "10-7" set; parser now accepts it, recovering 7,454 rows |
| outcome types | COMPLETED 1,567,845; RETIRED 49,036; WALKOVER 7,149; DEFAULT 411; UNKNOWN 289; UNFINISHED 29 |
| surface missing | 0.06 % |
| serve stats present | Masters 81 %, 500/250 78 %, slams 63 %, Challenger 61 %, WTA-125 17 %, ITF 5 % |
| cross-source duplicates dropped | 142,827 (Sackmann preferred over TML) |
| id systems | Sackmann 1,527,723 rows (production); TML 97,036 (separate id universe, not merged) |
| freshness | ATP ends 2026-06-01, WTA 2026-04-27 (TENNIS-14 FAIL) |
| tennis-data ↔ canonical link | 14,195 MATCHED / 593 AMBIGUOUS / 373 UNMATCHED (ATP 2020-26) |

## MODEL RESULTS / WALK-FORWARD RESULTS
docs/MODELING.md, research/elo_study/RESULTS_ATP.md, RESULTS_WTA.md, research/market_benchmark/RESULTS_ATP.md,
RESULTS_SR_ATP.md, research/kalshi_backtest/RESULTS.md.

| forecaster | set | n | Brier | log-loss | slope |
|---|---|---|---|---|---|
| elo_levelprior | ATP all levels 2015-26 | 321,293 | 0.2000 | 0.5835 | 0.91 |
| elo_levelprior | WTA all levels 2015-26 (post parser fix) | 299,185 | 0.1933 | 0.5667 | 1.04 |
| Pinnacle | ATP tour 2020-26 (linked) | 13,323 | 0.2026 | 0.5884 | 1.02 |
| ensemble | same | 13,323 | 0.2111 | 0.6084 | 1.04 |
| structural sr300 | same | 13,323 | 0.2133 | 0.6135 | 0.92 |
| elo_surface_k_lo | same | 13,323 | 0.2169 | 0.6221 | 0.83 |
| Kalshi mid (≥7 h pre-close) | settled Jul-Sep 2026 | 1,869 | 0.1871 | 0.5503 | 1.01 |
| ensemble (frozen) | same | 1,869 | 0.2060 | 0.5974 | 1.10 |

## CALIBRATION RESULTS
Reliability tables in research/market_benchmark/results_ATP.json and research/kalshi_backtest/RESULTS.md.
Ensemble ECE 0.017-0.033; Kalshi ECE 0.016; Pinnacle 0.009.

## MARKET COMPARISON
Hybrid (fit on seasons < t): w_market 1.04-1.08, w_model −0.04 to −0.07, hybrid Brier 0.2033 vs market 0.2031
(diff +0.0002 [+0.0000, +0.0004]). Disagreement buckets (ATP vs Pinnacle, vig-free hypothetical ROI): 0-2.5 pp
−5.7 %, 2.5-5 −3.2 %, 5-10 −5.6 %, 10-15 +1.7 %, 15-20 +5.8 % (n=1,040), 20+ −9.0 %. Versus Kalshi at the ask
after fees: −8.8 %, −10.2 %, −7.0 %, −4.4 %, −8.8 %, −0.4 %. Answer to the central question: **when we disagree
with the market, we are usually wrong.**

## ABLATION RESULTS
research/market_benchmark/RESULTS_ABLATION_ATP.md — walk-forward (seasons < t → t) logistic models on top of the
ensemble logit, ATP Pinnacle-linked set (n = 12,221):

| feature set | Brier | Δ vs ensemble [95 % CI] |
|---|---|---|
| ensemble only | 0.2114 | — |
| + log rank difference | 0.2113 | −0.00007 [−0.00019, +0.00004] |
| + rest (log days since last match) | 0.2114 | −0.00005 [−0.00058, +0.00052] |
| + 14-day load (matches, games) | 0.2110 | −0.00043 [−0.00097, +0.00008] |
| + surface switch | 0.2112 | −0.00021 [−0.00061, +0.00017] |
| + all | 0.2110 | −0.00040 [−0.00114, +0.00021] |
| Pinnacle | 0.2031 | −0.0083 vs ensemble |

No feature survives: every CI includes zero (recent load is the only borderline one). None is promoted.
Elo variants: surface pooling helps on tour-only data, hurts slightly on all-level corpora; level priors help
marginally; K0 = 180 calibrates but loses sharpness.

## LOWER-LEVEL TENNIS RESULTS
Elo log-loss by level (ATP 2015+): ITF 0.556-0.564, Challenger 0.628, 500/250 0.620, Masters 0.630, slams
0.589. Kalshi pregame log-loss: ITF-M 0.525, ITF-W 0.538, Challenger 0.604, ATP 0.574, WTA 0.494 — ITF markets
look efficient; the model is worst exactly where serve evidence is absent. Data-quality grades on live
projections: A 122 / B 44 / C 38 / D 16 / F 30 (before the stricter grading).

## DOUBLES STATUS
Schema, team identity, baseline prior (singles-Elo blend) and live pricing of MATCH_WINNER exist; 8 doubles
markets priced tonight, grade capped C, `unvalidated=True`, never actionable. No modern doubles truth in the
free corpus; Kalshi lists ~9,800 doubles markets (ITF/Challenger/tour/mixed).

## FUTURES STATUS
Exact bracket DP with invariants (title mass = 1, monotone reach probabilities, byes, withdrawals, TBD refusal)
is built and tested; tournament-winner / advance markets parse (2,787 + 541 historical). Not priced live: no
draw feed reachable.

## CURRENT LIVE PROJECTION STATUS (run 20260911T135922Z, refreshed states)
Active 533 → closed since discovery 178, past nominal start 43, unsupported families 118, tournament scope 11,
excluded events 65 (19 name-recovery, doubles players unmapped), unmapped players 4 → **projected 114 (incl.
8 doubles)**, consistency violations 0, 0 markets pass the actionability filter (two-sided, ≤ 10 c spread,
liquidity > 0, grade A/B, SCHEDULED start basis, > 15 min to start). Report:
data/research/projections/REPORT_20260911T135922Z.md. Ledger: hash-chained rows across the day's runs; 4 rows already
settled through scripts/ops/settle_ledger.py (close basis SCHEDULED_MINUS_MARGIN; scorecard withheld below 30
gradeable rows). The `RUN TENNIS` workflow reproduces this on the runner and publishes data/research to the
`tennis-data` branch.

## TEST STATUS
215 tests pass (`python -m pytest -q tests`): scoring engine vs closed forms and Monte Carlo, format registry,
score parser (48 cases), Sackmann/tennis-data normalisation, identity linking, Kalshi classifier/parser on real
fixtures, payoff coherence (winner = Σ exact scores, monotone ladders), fees, ledger chain tamper detection,
close/CLV boundaries, truth reconciliation, draw DP vs brute force, health gates, quality score, mapper.

## HEALTH GATES (data/research/health_latest.json)
PASS: 1 discovery, 2 taxonomy, 3 active mapping, 6 no post-start leakage (schedule basis), 7 identity,
11 consistency, 12 ledger chain, 13 reproducible artifacts. FAIL: 4 projection coverage (67 + 4 markets not
priced), 5 capture freshness (trade tape page budget — fixed, chain restarted 13:43 UTC), 14 source freshness
(ratings 102 / 137 days stale). UNKNOWN: 8, 9, 10 (no settled predictions yet).

## KNOWN RISKS
docs/KNOWN_LIMITATIONS.md. Top five: (1) no first-ball truth — every close is SCHEDULED_MINUS_MARGIN and ITF /
Challenger nominal times are not start times; (2) stale ratings (forks); (3) retirement mass ignored in
derivative pricing; (4) capture continuity depends on the self-dispatch chain; (5) licences (CC BY-NC-SA,
TML terms) constrain any commercial use.

## BLOCKERS
Egress policy (all tennis/Kalshi hosts), tennis-data.co.uk 503, upstream Sackmann 404, no draw / live-score
feed, Kalshi fee schedule not byte-verified, contract PDFs unparsed.

## NEXT 10 HIGHEST-VALUE ACTIONS
1. Move the two workflows to the default branch → cron-driven capture/discovery; keep the chain as fallback.
2. Wire the settlement stream into the ledger: SportsTruth/ExchangeTruth per prediction, canonical close from
   candles, executable CLV, TENNIS-8/9/10 → prospective scorecard (this is the only path to an edge claim).
3. First-ball adapter (any live-score feed reachable from the runner) — until then treat all closes as
   schedule-based and never score ITF/Challenger rows as strict pregame.
4. Daily Sackmann-fork + TML refresh with automatic rebuild and rating refit; alert on staleness > 8 days.
5. Re-run the WTA studies on the recovered ITF rows (parser fixed; refit in progress at hand-off) and add Shin vig removal to the headline tables.
6. Price derivative markets against settled Kalshi histories (the 60-min candles exist for 6,900 totals /
   5,700 spreads / 9,700 exact-score markets) — H-T08.
7. Fix name recovery for derivative-only events and the doubles "Surname-only" names (19 + 111 markets).
8. Fit walk-forward calibration of the ensemble per level and a market+model hybrid on Kalshi mids once
   ≥ 1,000 ledger rows have settled.
9. Draw feed → futures pricing with the bracket DP; team-competition and combo families next.
10. Parse the 286 contract PDFs into the settlement-rule registry and byte-verify the fee schedule.

## SELF-AUDIT (adversarial)
* Leakage: ratings replay strictly chronological (date, tournament, round order); prediction rows emitted
  before updates; Kalshi backtest ratings frozen before every market; hybrid/ablation fits use prior seasons
  only; ranks are pre-tournament. Same-date ordering across tournaments is an approximation (documented).
* Timestamp leakage caught and fixed: the first Kalshi backtest used `occurrence_datetime` as the start; for
  ITF/Challenger it falls after the close (in-play prices leaked, Kalshi looked 84 % accurate). Replaced by
  min(nominal − 5 min, close − 7 h). Residual risk: rain-delayed matches.
* Survivorship: all settled markets with a qualifying quote included; funnel reported (3,921 events → 1,869).
* Identity: 769 Kalshi events unmapped (fail closed); namesakes fail closed; no fuzzy auto-accept.
* Duplicates: cross-source dedupe on tour|date|round|names; 8,964 within-source duplicate keys quarantined.
* Rules: format registry dated; retirement weight 0.5 in Elo (untested alternative: 0/1); walkovers skipped.
* Vig: proportional removal (Shin available, not used for headline numbers).
* Non-executable prices: all ROI figures are hypothetical; Kalshi ROI uses the ask + taker fee; bookmaker ROI
  uses vig-free prices (not executable).
* Mixed id systems contaminated the first state fit (Zverev twice) — fixed; studies rerun on one system.
* Unresolved: rank baseline NaN (broken), WTA ITF score notation, doubles names, first-ball truth.
