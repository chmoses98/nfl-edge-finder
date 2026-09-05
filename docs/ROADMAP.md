# Roadmap (evidence-driven)

Updated after session 5. Historical research findings are not rewritten here — where a milestone produced a
negative result, the negative result *is* the outcome and is recorded as such.

## Where the project actually is

Data collection and prospective research infrastructure are mature. The predictive programme reached a clear
and mostly negative conclusion. The project has now pivoted from "find a statistical edge" to "build the best
NFL intelligence system and measure whether informed judgement on top of it has an edge" — a new, prospective
experiment with zero history.

| milestone | status 2026-09-05 | next step |
|---|---|---|
| **A** free data + market audit | **done** — context collectors live (NWS, Sleeper, ESPN); 23,275 markets across 430 series discovered | measure feed latency against official report times |
| **B** schemas + entity resolution | **done** — silver tables, crosswalk, Kalshi player map, 198 tests | 1,781 Week-1 player markets still fail Kalshi→GSIS resolution |
| **C** Kalshi discovery / backfill / capture | **mature** — capture ~10-min, 2-hourly shadow pricing, full 2025 backfill (54,364 markets) | keep running; watch for series schema drift |
| **D** point-in-time research dataset | **done** — team_game, ratings snapshots, player research table, shock log | 2026 in-season features arrive with Week 1 |
| **E** market baselines + game model | **REJECTED as an edge.** Model Brier 0.19933 vs market 0.18934 (6.2 SE). Encompassing: market coefficient +0.94, model −0.00 (z=−0.01) | retained as structure for the handicap packet, not as a forecast |
| **F** player opportunity + distributions | **done, and REJECTED on the traded population.** Role features improve 6/6 statistics on the full ladder and 0/6 on Kalshi-listed contracts; retired by H-022 | superseded — see H-022 as a standing rule |
| **G** ladder pricing | **done** — every supported ladder priced each snapshot; market-implied distributions reconstructed | — |
| **H** edge lab / hypothesis registry | **operational** — 25 registered hypotheses, FDR discipline, preregistered gates | H-023/024/025 read out on 2026 data |
| **I** calibration + market residual | **framework built, two-arm calibrator NOT deployed** | needs ≥4 weeks of settled 2026 markets |
| **J** full-universe shadow ledger | **operational** — 12,408 observations/snapshot; first machine-produced snapshot published 2026-09-05 after four nested workflow defects were fixed | accrue through Week 1 |
| **K** passive / maker execution | **REJECTED on game markets.** 86.2% of books are one cent wide (no passive level exists), touch 98% vs trade-at-level 3.6–26.7%, and reachable orders lose 0.0287 gross while unreachable ones win | H-023 tests whether prop books differ; prior is negative |
| **L** market-as-prior framework | **done** — disagreement decomposed into location vs shape; research-only | feeds the handicap packet |
| **M** structural ladder repricing | **UNTESTED, not disproved** — 2025 spread-ladder archive covers only 22 games (week 18 + playoffs); 14 treated / 4 control against a preregistered 40/40 gate | H-025 on 2026 |
| **N** handicap intelligence layer | **NEW, done this session** — `RUN NFL` builds a full slate packet in ~8s: every listed market, model and market-implied distributions, team/QB profiles, injuries with a real capture diff, weather, movement, matchup, best-expression groups, correlation tags, generated key questions | run weekly from Week 1 |
| **O** recommendation / evaluation layer | **NEW, built, zero history** — immutable four-record ledger on `handicap-data`, CLV/settlement evaluation, postmortem categories, model-vs-market-vs-ChatGPT scorecard | first real recommendations at Week 1 |
| **P** production / real money | **NOT EARNED** | requires a real prospective sample showing positive CLV *and* calibration, on contracts that were actually executable |

## The current experiment

> Does **NFL DATA + MODEL + MARKET + CHATGPT HANDICAP** produce better decisions than **MODEL ALONE** or
> **RAW DISAGREEMENT ALONE**?

Sample: **zero resolved recommendations.** Nothing is backfilled and nothing will be. The scorecard reports
the empty state rather than printing zeros.

## What is settled and should not be reopened

* Independent projections do not beat contemporaneous Kalshi pricing on outcomes (E).
* Role/opportunity features do not transfer to the traded population (F, H-022 — three for three).
* Passive execution fails on the core game markets (K).
* The session-3 shock-latency result did not survive correcting its treatment population, which was 69%
  non-events (H-021).

## Live prospective hypotheses

`H-019` favourite–longshot bias (untouched since registration) · `H-020` model CLV · `H-021` shock latency
(downgraded, underpowered) · `H-022` population transfer (standing rule; role features retired under it) ·
`H-023` passive on prop books · `H-024` adverse selection · `H-025` structural ladder repricing.
