# Football Signal Discovery Lab — Wave 1 (NFL): results

**Verdict.**

* **Game level.** Opponent-adjusted NFL football signals are real but **priced at the close**.
  * The efficiency net, QB/dropback efficiency, pressure × protection and explosiveness all predict margin
    (q < 0.001). None predicts the closing-spread residual.
  * The pre-registered football + market models add nothing out of sample on spreads or moneylines.
  * Two weak leads (indoor totals, success-rate offence) are MARKET_WATCH at best.
* **Player props.** A transparent opportunity model beats simple baselines by 1–6.5 % MAE in most families. Almost all
  of that comes from **recent role** (short-window shares, last-game usage, snap share).
  * Matchup context (opponent pass defence, pace, expected script, pressure) adds little or nothing out of sample.
  * **No football signal explains the residual against the Kalshi line** (140 tests, every BH q ≥ 0.83).
  * The football model is **less accurate than the Kalshi ladder median for every yardage family**.
* **Market structure.** One economic pattern appears: the YES side of low-volume count props is over-priced, so
  buying NO is profitable on RB receptions.
  * It is market-wide, not a football signal.
  * It was found by a post-hoc comparator.
  * It matches the repository's earlier `efficiency_map` finding.
  * It goes forward only as a frozen prospective candidate.

* **Kind of study:** RETROSPECTIVE DISCOVERY / VALIDATION; see protocol §2.
* **Protocol:** `docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE1_PROTOCOL.md`.
  * Set 1 (sha `83861082…`) was committed at `e8959411`.
  * Set 2 (sha `5f257647…`) was committed at `31ddffb9`.
* **Numbers:** `docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE1_TABLES.md`, generated from
  `research/signal_discovery_wave1/{game,prop}_evaluation_report.json`.
* **Catalogs:** `docs/research/NFL_SIGNAL_CATALOG.md`, `docs/research/NFL_PLAYER_PROP_SIGNAL_CATALOG.md`.
* **Registry:** `research/signal_discovery_wave1/football_signal_registry.json` (177 entries).

## C. Data used (NFL)

| Layer | Source | Coverage | Limitations |
|---|---|---|---|
| Play-by-play, schedules, player games, snaps, rosters, injuries, depth charts, participation | nflverse releases (downloaded 2026-10-08; manifests in `data/raw/nflverse/_manifest.jsonl`) | 2012–2026 (participation 2016–2025) | participation has **no 2026 file**; injury reports for 2025–26 carry no timestamp |
| Game features | `sim-oppadj-1.0.0` solver, 16 metrics | 3,300 games 2015–2026; 2,985 evaluable 2015–25 | 33 pbp/schedule score mismatches and 10 ties excluded |
| Player features | `nfl_edge.sim.features` + game context | 62,920 player-games 2016–2026 (QB 6,639; RB 14,478; WR 25,995; TE 15,808) | conditional on the player appearing |
| Game lines | nflverse consensus close | spread and total 100 %, moneyline 2,984 / 2,985 | untimestamped; −110 standard |
| Kalshi props | `market-data` @ `912aac02` | 2025 archive, 24,268 rungs (5 families); 2026 capture, 19,003 rungs (10 families, ≤ 24 h pre-kick). 5,203 / 7,731 ladders have a median. | 2025 YES side only; 2026 is 5 weeks; identity: 43,157 name+team, 110 unique-name, 4 unresolved |

## D/M. Market and prop data audit

Full audit: `docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE1_DATA_AUDIT.md`.

**2026 capture with executable quotes** (both asks):

| Family | Tickers |
|---|---|
| receiving yards | 6,678 |
| receptions | 5,304 |
| rushing yards | 3,830 |
| anytime TD | 3,499 |
| passing yards | 1,372 |
| carries | 1,022 |
| attempts / completions | 695 / 673 |
| passing TDs | 639 |
| interceptions | 437 |
| rush + rec yards | 572 |

**2025 archive (settled):**

| Family | Settled markets |
|---|---|
| receiving yards | 10,170 |
| TDs | 7,471 |
| receptions | 7,358 |
| rushing yards | 4,625 |
| passing yards | 3,248 |
| passing TDs | 812 |

The 2025 archive has **no attempts, completions or carries**.

**Game markets:**

* GAME_WINNER, SPREAD, TOTAL and TEAM_TOTAL are all captured from 2026 week 1.
* 1H/1Q families have only about 1–2 seasons of thin history.
* No historical sportsbook prop line exists anywhere in the repository.

## K. NFL game signal catalog (summary)

Full rows are in `NFL_SIGNAL_CATALOG.md`.

| Signal | Football (A) | Market vs close (B) | Economic (C) | Status |
|---|---|---|---|---|
| Efficiency CONTROL (≥ 0.075 EPA/play net) → winner/ML (001) | win lift +0.21, q < 0.001 | ML: won 71.2 % vs implied ≈ 70.5 % (+0.7 pp) | ML ROI −2.5 % [−6.2, +1.2] | FOOTBALL_VALIDATED (market efficient) |
| MODERATE / STRONG CONTROL → ATS (002/003) | yes | 49.0 % / 48.2 % cover | −6.5 % / −8.1 % | APPROX_EFFICIENT |
| EPA net (continuous) (004) | +5.2 pts/SD | +0.23/SD (p 0.33) | follow 48.4 % | APPROX_EFFICIENT |
| QB/dropback mismatch (005) | +5.0/SD | +0.17/SD | 48.0 % | APPROX_EFFICIENT |
| Pass beyond efficiency (006) | −0.03 | −0.50/SD (p 0.49); same sign as CFB's over-pricing, not significant | 48.0 % | REJECTED |
| Rush beyond efficiency (007) | +0.46 (q 0.16) | +0.54/SD (p 0.06); block A +0.01, **block B +0.92 (p 0.015)**; same sign as CFB | 48.3 % | REJECTED (unstable) |
| Pressure × protection (008) | +3.0/SD | +0.27 | 51.6 % | APPROX_EFFICIENT |
| Pressure-rate matchup (009) | +0.56 (q 0.07) | −0.35 | — | REJECTED (and not prospectively reproducible) |
| Explosive × prevention (010) | +3.4/SD | +0.09 | — | APPROX_EFFICIENT |
| Pace → total (011), tempo (012) | +0.86 / −0.80 pts | ≈ 0 | 47.7 % | APPROX_EFFICIENT |
| Defensive suppression (013/014) | −1.7 / −0.7 pts | ≈ 0 | — | REJECTED / APPROX_EFFICIENT |
| Control style: run-leaning favourite → under (015) | none | −1.06 (p 0.04) but q 0.31 | 49.3 % | REJECTED |
| Football baseline vs spread / total / team total (016–018) | — | ≈ 0 | — | REJECTED |
| Rest differential / off-bye / divisional / QB change (019, 021–023) | small | ≈ 0 | — | APPROX_EFFICIENT / FOOTBALL_VALIDATED / REJECTED |
| Short week (020) | — | n = 5 | — | DISCOVERY_ONLY |
| **Indoor → total (024)** | +2.1 pts | **+1.32 pts (p 0.004, q 0.08)**; over hit only 50.4 % | −3.9 % | MARKET_WATCH (mean shift from tails, not hit rate) |
| CLOSENESS → underdog (025) | — | 53.2 %, +0.92 (q 0.31) | +1.5 % | REJECTED |
| CONTROL → 1H margin (026) | +3.8 pts, q < 0.001 | — | — | FOOTBALL_VALIDATED |
| Weather, injury shocks (027/028) | — | — | — | DATA_UNAVAILABLE |
| **Set 2 (block B):** success-rate offence (DSC-002) | — | block B +0.54/SD, q 0.22 (all seasons +0.66, p 0.005) | follow 49.5 % | APPROX_EFFICIENT on block B |
| Set 2: DSC-001 / 003 / 004 / 005 | — | ≈ 0 on block B | — | REJECTED |

## L. NFL market-efficiency matrix

| Signal | ML | Spread | Total | Team total | 1H / 1Q |
|---|---|---|---|---|---|
| Efficiency CONTROL | NO_SIGNAL | NO_SIGNAL | NOT_TESTED | DATA_UNAVAILABLE (derived: NO_SIGNAL) | DATA_UNAVAILABLE (football +3.8 at half) |
| QB / pass efficiency | NOT_TESTED | NO_SIGNAL | NOT_TESTED | DATA_UNAVAILABLE | DATA_UNAVAILABLE |
| Rush matchup | NOT_TESTED | POSSIBLE (block B only) | NOT_TESTED | DATA_UNAVAILABLE | DATA_UNAVAILABLE |
| Pressure × protection | NOT_TESTED | NO_SIGNAL | NOT_TESTED | DATA_UNAVAILABLE | DATA_UNAVAILABLE |
| Pace / tempo | NOT_TESTED | NOT_TESTED | NO_SIGNAL | NO_SIGNAL (derived) | DATA_UNAVAILABLE |
| Defensive suppression | NOT_TESTED | NOT_TESTED | NO_SIGNAL | NO_SIGNAL (derived) | DATA_UNAVAILABLE |
| Indoor | NOT_TESTED | NOT_TESTED | POSSIBLE | NOT_TESTED | DATA_UNAVAILABLE |
| Football baseline vs line | NO_SIGNAL (WF-ML Δlog-loss +0.0001) | NO_SIGNAL (WF-ATS r −0.001) | POSSIBLE (WF-TOTAL r +0.046 [0.004, 0.087]) | NO_SIGNAL | DATA_UNAVAILABLE |
| Context (rest, bye, division, QB change) | NO_SIGNAL | NO_SIGNAL | NOT_TESTED | DATA_UNAVAILABLE | DATA_UNAVAILABLE |

**WF-TOTAL detail.** Pre-registered, five fixed features, walk-forward 2018–2025.

* OOS correlation +0.046 [+0.004, +0.087].
* Picks with |prediction| ≥ 2: 134-106-3, 55.8 %. ROI +6.6 % [−5.3, +18.3] at −110.
* 7 of 8 test seasons were at or above 52 %; 2025 was 41 %.
* Its coefficients **fade** the football total's disagreement with the line (−0.3 per point). It reads as "the market
  is right where the football baseline is extreme", not as football information.
* Status: DISCOVERY_ONLY. It is tracked as a candidate, never used.

## N. Player opportunity model (final research architecture)

```
GAME   opponent-adjusted ratings (sim-oppadj solver) -> expected plays, tempo, neutral pass rate,
       football scoring baseline (expected margin = "expected script"), opponent pass/rush/explosive
       defence, pass rush vs protection, QB efficiency                         [market-blind]
  -> TEAM   team volume EWMAs (pass attempts, rush attempts, plays, pass rate), frozen league priors
  -> PLAYER share (target / carry / attempt / red-zone / snap; 3- and 10-game half-lives, last game)
            x per-touch efficiency (ypt, catch rate, aDOT, ypc, ypa, completion rate; shrunk to frozen
            position priors fitted on 2012-2015) -> ridge (λ = 1), walk-forward by season
  -> DISTRIBUTION  prediction + training-residual quantiles (50 % / 80 % intervals; median offset for skew)
```

* **Interval coverage (OOS):** 50 % intervals cover 47–52 %; 80 % intervals cover 77–81 %. The one exception is QB
  rush yards, at 42 % / 73 %.
* **ROLE_STABILITY:** 49,825 STABLE / 7,828 INJURY_DEPENDENT / 3,839 INSUFFICIENT_HISTORY / 1,428 ROLE_CHANGE. The
  model's gain is concentrated in ROLE_CHANGE rows:

  | Family | MAE gain on ROLE_CHANGE rows | MAE gain on STABLE rows |
  |---|---|---|
  | QB pass yards | +14.5 yards (n 218) | +0.14 |
  | WR receiving yards | +4.8 | +0.52 |
  | RB rushing yards | +3.4 | +0.47 |

## O. QB prop results

| Stat | Baseline MAE (best) | Model MAE | Gain [95 %] | Validated groups | Line residual (Kalshi) | Economics (model rule) |
|---|---|---|---|---|---|---|
| Passing yards | 65.55 (usage) | 64.61 | +0.94 [+0.25, +1.60]; 7/9 seasons; **not robust to removing the top 10 QBs (−0.09)** | ROLE_RECENCY only | market median MAE 55.9 vs model 58.9: **market better**; residual ~ model gap β −0.05 (q 0.98) | n 85, ROI −18.4 % [−36.1, +0.6] |
| Attempts | 7.78 | 7.67 | +0.11 [+0.02, +0.20] | ROLE_RECENCY | 2026 only (75): market 7.36 vs model 8.04 | n 18, −8.6 % |
| Completions | 5.36 | 5.32 | +0.05 (n.s.) | ROLE_RECENCY | market 5.13 vs model 5.22 | n 23, +2.5 % (n.s.) |
| Pass TD | 0.92 | 0.92 | 0 | none | actual below median (34 % over) | −6.1 % |
| Interceptions | 0.71 | 0.71 | +0.007 | RUSH_DEF (tiny) | 2026: actual far below median (7.7 % over); always-NO +8.5 % (n 39) | +8.5 % (n 39, n.s.) |
| Rush yards | 11.45 (EWMA) | 11.84 | **−0.40: model worse** | RUSH_DEF only; other groups hurt | always-NO +7.6 % [−5.1, +19.7] | +1.7 % |

## P. RB prop results

| Stat | Baseline MAE | Model MAE | Gain | Validated groups | Line residual | Economics |
|---|---|---|---|---|---|---|
| Carries | 4.40 | 4.11 | **+0.29 (+6.5 %) [+0.24, +0.34]**, 9/9 seasons, robust without top 10 | ROLE_RECENCY | 2026 only (98): market 3.58 vs model 3.96 | n 51, +1.3 % |
| Rush yards | 25.74 | 25.09 | +0.65 (+2.5 %), 7/9 | ROLE_RECENCY, RUSH_DEF, PRESSURE | market 24.5 vs model 25.8; residual mean +3.0 (median −1.7) | **−12.4 % [−23.7, −1.1]** |
| Receptions | 1.47 (usage) | 1.53 | **−0.06: model worse** (one bad season, 2019) | PASS_DEF, IX share × pressure (tiny) | actual below median (30.5 % over); model 1.49 vs market 1.64 | **+14.9 % [+2.3, +26.8]** (n 190, 178 NO); **always-NO +10.6 % [−1.0, +22.9]**, so most of it is market-wide |
| Receiving yards | 14.15 | 13.83 | +0.32 (+2.3 %), 7/9 | ROLE_RECENCY, QB_EFF, RUSH_DEF | median −5.0, 40.5 % over | −0.4 %; always-NO +9.1 % [−2.6, +21.1] |

## Q. WR / TE prop results

| Stat | Baseline MAE | Model MAE | Gain | Validated groups | Line residual | Economics |
|---|---|---|---|---|---|---|
| WR receptions | 1.79 | 1.76 | +0.03 (+1.9 %), 9/9, robust | ROLE_RECENCY | 37.1 % over median; model 1.74 vs market 1.76 | −0.1 % |
| WR receiving yards | 27.69 | 27.10 | **+0.58 (+2.1 %), 9/9, robust (+0.50 without top 10)** | ROLE_RECENCY (RUSH_DEF discovery-only) | market 25.9 vs model 26.8: **market better** | −7.4 % [−15.7, +1.1] |
| TE receptions | 1.65 | 1.65 | 0 | ROLE_RECENCY | 37.4 % over | +0.4 % |
| TE receiving yards | 21.00 | 20.80 | +0.20 (n.s.) | ROLE_RECENCY, RUSH_DEF | market 20.9 vs model 21.3 | −1.0 % |

Longest reception and other families were not modelled. Their market data exists only for 2026, and the outcome
definitions were not validated in this wave.

## S. Game script → props

Each figure is the effect of 1 SD, controlling for the player's own EWMA.

* **Realised script is a large effect (post hoc, not forecastable):**
  * Leading reduces QB attempts by −7.8 % and RB receptions by −9.1 %.
  * Leading raises RB carries by +13.2 %.
  * Realised team plays raise every volume stat by 11–16 %.
* **Pregame expected script (football baseline margin) is small:**
  * RB carries +1.4 % (p 0.018).
  * WR receiving yards +2.0 % (p 0.001).
  * TE receptions +2.5 %.
  * QB attempts −0.8 % (p 0.09).
* **Pregame expected plays:** ≤ 1 % on everything.
* **Conclusion:** the mechanism the prompt hypothesised is real. Pregame, though, the script is mostly unknown, so
  little of it can be forecast; what can is already in usage.

**Residual correlations within a team-game** (§47):

| Pair | r |
|---|---|
| QB pass yards ~ WR receiving yards | +0.56 |
| QB attempts ~ WR receptions | +0.39 |
| QB pass yards ~ TE receiving yards | +0.31 |
| QB completions ~ RB receptions | +0.25 |
| QB attempts ~ RB carries | −0.17 |
| RB carries ~ RB rush yards | +0.76 |

These are metadata for any future same-game exposure accounting. No parlay was built.

## T. Prop market-efficiency matrix

States: STRONG / POSSIBLE / NO_SIGNAL / NOT_TESTED / DATA_UNAVAILABLE. Each cell gives the football (A) state, then
the line-residual (B) state.

| Signal group | QB yds | QB att | QB cmp | RB carries | RB rush yds | RB rec | WR rec | WR yds | TE rec | TE yds |
|---|---|---|---|---|---|---|---|---|---|---|
| ROLE_RECENCY | STRONG / NO_SIGNAL | STRONG / NO_SIGNAL | STRONG / NO_SIGNAL | STRONG / NO_SIGNAL | STRONG / NO_SIGNAL | NO_SIGNAL / POSSIBLE (p 0.03, q 0.83) | STRONG / NO_SIGNAL | STRONG / NO_SIGNAL | STRONG / NO_SIGNAL | STRONG / NO_SIGNAL |
| PACE | NO_SIGNAL / NO_SIGNAL | NO_SIGNAL / NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL / POSSIBLE (p 0.07) | NO_SIGNAL | NO_SIGNAL |
| SCRIPT | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | POSSIBLE / NO_SIGNAL | NO_SIGNAL | NO_SIGNAL (hurts) | NO_SIGNAL | NO_SIGNAL |
| PASS_DEF | NO_SIGNAL / POSSIBLE (p 0.10) | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | STRONG (tiny) / NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL |
| RUSH_DEF | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL / POSSIBLE (p 0.03) | STRONG / POSSIBLE (p 0.08) | NO_SIGNAL | NO_SIGNAL | POSSIBLE | NO_SIGNAL | STRONG / POSSIBLE |
| PRESSURE | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | STRONG / NO_SIGNAL | NO_SIGNAL (hurts) | NO_SIGNAL | NO_SIGNAL (hurts) | NO_SIGNAL | NO_SIGNAL |
| QB_EFF | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | POSSIBLE | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL | NO_SIGNAL |
| Market-wide YES over-pricing (post hoc) | — | — | — | — | — | **always-NO +10.6 %** | always-NO −2.1 % | −4.4 % | −2.6 % | −0.8 % |

No line-residual cell survives BH (every q ≥ 0.83).

## U. Market disagreement (NFL)

* **Football strong / market strong** (control side favoured ≥ 7): win 80.9 % against an implied 80.8 %; ATS 48.9 %.
  The market is right.
* **Football strong / market skeptical** (n 36): ATS 55.6 %, +1.78 points, p 0.36. Unlike CFB, this is nothing.
* **Football moderate / market skeptical** (n 121): won 43.8 % against an implied 48.5 %. ATS 42.5 %, ML ROI −12.9 %.
  **The market is right and the football edge is wrong.**
* **Football baseline vs spread disagree on the favourite** (480 games): football side won 43.1 % against an implied
  42.3 %. ATS 52.5 %, +1.23 points, p 0.04, ROI +0.1 %. Not significant after correction.
* **Walk-forward combined models:**
  * WF-ATS OOS r −0.001 [−0.041, +0.040].
  * WF-ML Δlog-loss +0.0001.
  * The market fully encompasses the football signal, as H-001 already found.

## V. Multiple testing (NFL)

| Family | Count |
|---|---|
| Game Stage A screen | 272 associations; 1 at q < 0.05 |
| Game locked tests | football 33, market 32 (sets 1 + 2) |
| Game market tests at BH q < 0.05 | **0**; at q < 0.10: 2 (indoor total, DSC-002 all-seasons) |
| Prop group ablations (BH over 141) | 19 FOOTBALL_VALIDATED (10 of them ROLE_RECENCY), 5 DISCOVERY_ONLY, 117 REJECTED |
| Prop line-residual tests (BH over 126 signal tests + 14 model-gap tests) | **0** at q < 0.10 (minimum q 0.83) |
| Methods | Benjamini–Hochberg (primary), Holm (reported), game-clustered bootstrap, season stability, top-10-player removal |

## W. Failed and rejected ideas (NFL)

* Every game efficiency family against the spread (CONTROL tiers 48–49 % cover).
* The football baseline against the line.
* Pace and suppression against totals.
* Context effects: rest, bye, division, QB change (H-005 REJECTED_AT_CLOSE, confirmed).
* Control-style under.
* Closeness → underdog.
* The CFB rushing/passing finding **did not replicate cleanly in the NFL**. Signs matched (rush +0.54, pass −0.50),
  but neither was significant or stable.
* Set 2: 4 of 5 rejected on block B. The block-A top hit (DSC-001, within STRONG pass rate, q 0.027) went to
  +0.002 on block B.
* Props:
  * PACE, SCRIPT, PASS_DEF, PRESSURE and QB_EFF add nothing out of sample for QB and WR/TE families; some hurt.
  * All pre-registered interactions (share × pass defence, share × script, pace × pass defence, etc.) gave
    |ΔMAE| ≤ 0.03.
  * The model is worse than the baseline for QB rush yards and RB receptions.
  * The model is worse than the Kalshi median for every yardage family.

## Z. Player-prop prospective candidates (tracking only)

| Rank | Candidate | Exact rule | Market | Required n | Why | Falsified by |
|---|---|---|---|---|---|---|
| 1 | **RB receptions: YES over-pricing** (market structure, post hoc) | For every RB receptions ladder in the 2026+ capture: the natural rung (mid closest to 50 %) at the LAST_PREGAME quote ≤ 24 h before kickoff. Buy NO at the captured NO ask, taker fee included. Track separately: the subset where the opportunity-model median ≤ 0.9 × threshold. | Kalshi KXNFLREC (RB) | ≥ 300 rungs (≈ 4–5 weeks of 2026 slates) | 2025 and 2026 both positive (+9.1 %, +13.4 %); consistent with `efficiency_map` (props YES-overpriced) | ROI ≤ 0 after 300 settled rungs, or no-ask ≥ 0.60 making it unexecutable |
| 2 | **ROLE_CHANGE-flagged yardage props** (football) | Players flagged ROLE_CHANGE pregame (\|short − long share\| ≥ 0.10 or snap ≥ 0.15): compare the opportunity-model median with the ladder median at LAST_PREGAME | Kalshi receiving and rushing yards | ≥ 200 flagged ladders | the model's out-of-sample gain is 5–30× larger on these rows (QB yds +14.5, WR yds +4.8, RB yds +3.4) | the model-gap slope on the line residual ≤ 0 over 200 ladders |

No candidate meets the full eligibility rule (interpretable football + FDR-surviving market relationship). Both are
**prospective research tracking only**.

## AA. Tests and leakage proof (NFL)

`tests/test_signal_discovery_nfl.py`: 13 tests pass. The full suite gives **2,950 passed, 3 skipped**. The tests
prove:

* week-W features are unchanged when week W and later are doctored, and change when an earlier week is;
* appending a future season changes nothing;
* the game layer never reads line, odds or score columns, and a poisoned line value never appears;
* the feature modules cannot import the market, outcome or evaluator modules;
* the PIT primitive excludes the row itself;
* the ladder median refuses to extrapolate;
* quote validity and the fee;
* NO is never derived as 1 − YES when both asks were captured;
* identity never joins on display name across teams;
* evaluator orientation;
* the runner refuses unregistered hypotheses.

## AB. Files (NFL)

| Path | What |
|---|---|
| `nfl_edge/signal_discovery/` | `game_features.py`, `player_features.py`, `markets.py`, `outcomes.py`, `screen.py`, `evaluate_game.py` (ported CFB evaluator), `evaluate_props.py`, `deep_dive.py`, `hypotheses.py`, `stats.py` |
| `scripts/research/signal_discovery_wave1.py` | stages: game-features, player-features, prop-ladders, freeze-set1, screen, freeze-set2, evaluate-game, evaluate-props |
| `scripts/research/signal_discovery_wave1_report.py` | tables, registry, catalogs |
| `scripts/research/signal_discovery_kalshi_quote_aggregate.py` | the 2026 capture → last-pregame quote aggregator |
| `research/signal_discovery_wave1/` | features plus manifests, `hypotheses_set{1,2}.json`, `stage_a_screen.json`, `{game,prop}_evaluation_report.json`, `prop_ladders.parquet`, `prop_oos_predictions.parquet`, `football_signal_registry.json` |
| `docs/research/` | `…_PROTOCOL.md`, `…_RESULTS.md`, `…_TABLES.md`, `…_DATA_AUDIT.md`, `NFL_SIGNAL_CATALOG.md`, `NFL_PLAYER_PROP_SIGNAL_CATALOG.md` |

## AC. Production impact

**None.** The following are untouched:

* RUN NFL, Shadow v2, the incumbent pricer, the sim engine;
* board, handicap gates, risk, settlement, fees;
* app export, the router, every workflow;
* every hash-pinned source (`tests/test_incumbent_unchanged.py` passes).

`.gitignore` gained one line, for the 31 MB rebuildable player table.

## Deviations

1. **Prop signal-vs-residual join.** The first prop evaluation joined no feature columns to the ladder rows, so the
   pre-registered "signal feature vs line residual" tests were silently empty. The join was fixed and the
   evaluation rerun. It is deterministic, and every other number was unchanged.
2. **Always-YES / always-NO comparator.** Added after seeing the RB receptions result, labelled post hoc. It only
   ever *reduces* the credit given to the model.
3. **QB change** uses realised starter ids: NEAR_PIT, stated in the protocol.
4. **Kalshi 2025 NO asks** are 1 − YES bid (the archive has no NO quotes). Stated in the protocol.
