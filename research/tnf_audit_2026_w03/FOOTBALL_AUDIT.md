# 2026 Week 3 TNF — ATL @ GB — football-side audit

> **Evidence only: one game.** Nothing here tunes a model, promotes V3/V4/V5, changes production, betting or
> staking authority, or recommends a bet. No edge is claimed. Retrospective numbers are labelled.
> Audit date 2026-09-26 (Saturday). Repo `main` = `84bf469`. Final: **ATL 35, GB 14** (home margin −21, total 49).
> ATL rushed for 242 yards, GB for 17.

Machine-readable companions in this directory:

| file | what it is |
|---|---|
| `data_only_decomposition.json` | exact per-feature decomposition of the archived DATA_ONLY centre, per horizon, plus the full three-arm timeline |
| `data_only_counterfactuals.json` | bit-exact reproduction of DATA_ONLY at T-30m from public nflverse data, plus counterfactual rating inputs |
| `data_only_rating_split.json` | the margin split into the four team-rating components (GB off / ATL def / ATL off / GB def) |
| `sra_retrospective_diagnostic.json` | DATA_ONLY_SRA grid for this game. **Diagnostic only. Must not be used to select a parameter.** |
| `traded_markets_by_horizon.json`, `traded_markets_close.json` | the five contracts the owner traded, at each horizon and at the pregame close |
| `rushing_autopsy.json` | volume × efficiency split of both rushing misses, game-script counts |
| `coverage_by_horizon.json` | player-simulation coverage counts for each archived horizon packet, the post-game rebuild, and Sunday's packet |
| `decompose_data_only.py`, `reproduce_data_only.py`, `extract_traded_markets.py` | the scripts that produced them. They are research-only and read-only against evidence |

Sources: horizon packets are the Actions artifacts `run-nfl-2026-w03-{35937741435, 36040075511, 36069483473, 36074571204}`.
`handicap-reports` is a single orphan commit (`9dc07671`) with no history, so the archived packets exist only as
artifacts, which expire 2026-12-23. The other sources are the three-arm snapshots and evaluations on `market-data`
(`data/shadow/arms/…`, `data/shadow/arm_evaluations/2026_03_ATL_GB/…`), the player autopsy
(`data/shadow/player_autopsy/2026_03_ATL_GB/autopsy-1.0.0.20260925T121348Z`), the Sleeper/ESPN context captures
(`data/context/2026-09-*`), Kalshi captures, the owner receipts on `handicap-data`
(`data/imported_wagers/2026/week_03`, `data/wager_settlements/2026/week_03`), and nflverse play-by-play re-downloaded
on 2026-09-26.

## 0. Given facts: verified, no corrections

| fact | repository evidence | verdict |
|---|---|---|
| latest-pregame CURRENT GB +5.50 / 42.00 | arm_games `20260924T234509Z` (T-30m, 29.8 min pre-KO): `kalshi_implied_spread 5.5, total 42.0` | confirmed |
| DATA_ONLY GB +7.14 / 42.90 | same row: `7.135009442584407 / 42.90451514658339` | confirmed |
| HYBRID_30 GB +5.99 / 42.27 | `5.990502832775322 / 42.271354543975015` | confirmed |
| close ~GB +5.5 / 42 | arm evaluation `close`: margin 5.5, total 42.0, from 80 quotes, 12.7 min pre-KO | confirmed |
| DATA_ONLY farther from the actual side; slightly closer on the total | `margin_closer_than_market: false`; `total_closer_than_market: true` (\|42.90−49\| = 6.10 vs 7.0) | confirmed |
| close did not move, so the game contributes UNCHANGED | `margin_movement_vs_close: "unchanged"` for every snapshot from `20260923T134249Z` on, including all four canonical horizons | confirmed |

Two things to keep in mind when reading the numbers:

* The handicap packet's "market (research-implied)" spread, GB −5.00 / 43.55 at T-30m, is a different estimator from
  the incumbent's 5.5 / 42.0. The packet infers it from midpoints. It does not contradict the given fact.
* The first 14 evaluation rows (2026-09-15 to 09-20) used a consensus-line CURRENT centre and a pre-Week-2 DATA_ONLY
  (GB +4.2 to +4.4). Those rows are the source of the "toward" labels that appear early in the per-snapshot evaluation.
  The canonical horizons are all "unchanged".

---

## 5. Handicap audit per horizon

### 5a. What the system saw

| | T-24h | T-6h | T-90m | T-30m |
|---|---|---|---|---|
| packet built (UTC) | 09-24 00:32 | 09-24 18:36 | 09-24 23:05 | 09-25 00:06 |
| main sha | `afe584b` | `c53294d` | `c53294d` | `c53294d` |
| three-arm snapshot | `20260924T012615Z` | `20260924T180036Z` | `20260924T224601Z` | `20260924T234509Z` |
| CURRENT (Kalshi-implied) | GB +5.50 / 42.00 | +5.50 / 42.00 | +5.50 / 42.00 | +5.50 / 42.00 |
| consensus line (nflverse) | +5.5 / 42.5 | +4.5 / 42.5 | +4.5 / 43.5 | +4.5 / 42.5 |
| packet research-implied | −4.75 / 43.05 | −4.88 / 43.25 | −5.12 / 43.55 | −5.00 / 43.55 |
| packet legacy model view | −5.24 / 43.04 | −5.38 / 43.09 | −5.35 / 43.01 | −5.25 / 43.15 |
| DATA_ONLY | +7.135 / 42.905 | same | same | same |
| HYBRID_30 | +5.99 / 42.27 | same | same | same |
| P(GB win): CURRENT / DATA_ONLY / HYBRID | 0.697 / 0.755 / 0.694 at T-30m (CRN simulation) | | | |
| injuries (Out-IR / Q-D) | 6 / 3 | 6 / 3 | 7 / 1 (GB DT A. Campbell Q→Out) | 12 / 0 (adds ATL QB Rush and QB Strand inactive, ATL OT Onianwa, CB DeWalt, CB Longerbeam) |
| GB interior DL | Brinson Out, Campbell Q, Hargrave Q | same | Brinson Out, Campbell Out, Hargrave Q | same |
| QB state (packet) | ATL QB1 Penix, Active; GB QB1 Love | same | same; Rush "injury Out" | same; Rush and Strand Out |
| depth chart | ATL QB: Penix, Rush, Tagovailoa, Strand; RB: Bijan Robinson, Brian Robinson. GB RB: Lloyd, Brooks, K. Johnson (Jacobs has an injury tag) | same, plus WR slots | same | same |
| weather (Lambeau, outdoors) | 62°F, 3 mph, 0% | 62°F, 2 mph | 61°F, 2 mph | 64°F, 5 mph E; "material: False" |
| packet team-strength basis | **prior season 2025** (no 2026 games) | current season | current season | current season |
| ATL off dropback EPA (packet table) | −0.021 | **−0.135** | −0.135 | −0.135 |
| GB off / def dropback EPA | +0.107 / +0.038 | +0.063 / +0.043 | same | same |
| coherent simulation run attached | `20260923T213328Z` | `20260924T133700Z` | `20260924T183032Z` | `20260924T183032Z` |
| sim market lag vs ledger capture | 167 min | 283 min | 268 min | **327 min** |
| player arms present (shadow_v2) | V3, HYBRID_V3, MARKET_DIST (no V4 yet) | V3, V4, HYBRID_V3, HYBRID_V4, MARKET_DIST | same | same |
| QB profile for Penix | "no play-by-play profile matched" at every horizon, because `qb_profile_basis = 2026` and Penix had no 2026 dropbacks (he has 2024–25 dropbacks) | | | |

About the T-24h row: the packet's team-strength table used 2025 only. PR #52 ("build silver through the current season")
reached main between T-24h and T-6h. The three-arm DATA_ONLY was not affected, because it always rebuilt 2026 from
play-by-play.

### 5b. Major market moves: Kalshi-implied CURRENT centre across the week (`data_only_decomposition.json → timeline`)

| snapshot | CURRENT margin / total | consensus | DATA_ONLY | event |
|---|---|---|---|---|
| 09-18 07:35 | 6.5 / – (consensus fallback) | 6.5 | **4.21** | pre-Week-2 ratings |
| 09-20 22:30 | 7.0 / 46.5 | 7.0 | **7.17** | CAR@ATL (Wk 2, Rush and Strand) enters the ratings: **+2.96** in one game |
| 09-21 19:32 | 7.5 / 43.0 | 7.0 | 7.26 | ESPN: "Penix named starter", item dated 09-21 20:39Z, first captured 09-22 00:13Z |
| 09-21 23:22 | **6.0** / 44.0 | 6.5 | 7.26 | market moves ~1–1.5 toward ATL within ~3h of the announcement |
| 09-22 05:11 | 6.5 / 44.0 | 6.0 | 7.14 | MNF Wk 2 enters the ratings |
| 09-22 17:04 | – | – | – | Sleeper chart: Penix QB1 (still tagged Out/Surgery) |
| 09-23 11:49 | – | – | – | Sleeper: Penix injury tag cleared |
| 09-23 13:42 | **5.5** / 43.5 | 5.5 | 7.14 | market settles at 5.5 |
| 09-23 18:33 → close | 5.5 / 42.0 | 4.5 | 7.14 | flat to the close (5.5 / 42.0) |

The market moved about 1.5–2 points toward ATL, from 7.0–7.5 to 5.5, across the ~40 hours after the QB news
(consensus went 7.0 → 4.5). The total dropped from ~44.5–45 to 42. DATA_ONLY moved in the opposite direction on the
Week-2 data and never reacted to the QB news, because it has no QB input by design.

### 5c. Decomposition of DATA_ONLY's +1.64-point disagreement with the market

DATA_ONLY is a standardised ridge regression, so `pred = ym + Σ βᵢ(xᵢ−x̄ᵢ)/sᵢ` is exact. The archived feature vector
was recomputed with the frozen artifact (`e544b99917b9d0b1`) and reproduces the recorded 7.135009442584407 exactly. It
is identical at all four horizons: no football game finished between T-24h and T-30m. The centre was also
**re-derived from scratch** from re-downloaded nflverse play-by-play through the unmodified production code, and the
result was bit-identical (`7.135009442584407`).

**Per metric** (contribution in points of GB margin; "vs zero" means relative to a league-average matchup):

| term | contribution |
|---|---|
| intercept + context (rest 0, non-divisional, not neutral) | +1.662 |
| special-teams EPA (`d_st_epa`) | **+1.667** |
| EPA/play | +0.883 |
| explosive rate | +0.789 |
| PROE (early, non-garbage) | +0.723 |
| early-down EPA | +0.597 |
| success rate | +0.576 |
| dropback EPA | +0.333 |
| non-garbage EPA | +0.170 |
| turnover rate | +0.130 |
| sack rate | −0.092 |
| rush EPA | −0.304 |
| **DATA_ONLY total** | **+7.135** |
| market (Kalshi-implied) | +5.500 |
| **gap** | **+1.635** |

**Per team-rating component** (`data_only_rating_split.json`; `d_f = GB_off + ATL_def − ATL_off − GB_def`):

| component | points | of which special teams |
|---|---|---|
| intercept + context | +1.662 | – |
| GB offence | +0.977 | +0.788 |
| ATL defence | +0.086 | +0.348 |
| **ATL offence (negative rating → GB margin)** | **+4.183** | +0.928 |
| GB defence | +0.226 | −0.397 |
| total | +7.135 | |

**Counterfactual rating inputs** (same code, same cutoff, same artifact; `data_only_counterfactuals.json`):

| ratings input | DATA_ONLY margin | Δ vs recorded | vs market 5.5 |
|---|---|---|---|
| as recorded | +7.135 | – | +1.64 (GB side) |
| ATL 2026 offensive metrics removed (Rush/Strand games; special teams kept) | **+3.855** | **−3.28** | −1.65 (ATL side) |
| every 2026 row involving ATL removed | +3.552 | −3.58 | −1.95 |
| no 2026 games at all (week-0 view) | +3.702 | −3.43 | −1.80 |

Interpretation. The whole +1.64 disagreement, and about twice that amount, is explained by one input: ATL's offensive
ratings from its two 2026 games. Those games were quarterbacked by Cooper Rush (and Jack Strand), whose dropback
EPA/play was −0.61 and −0.68. With those two games removed, ATL's offensive dropback rating goes from −0.140 to −0.020.
Special teams add a further +0.93 through ATL's 2026 special-teams EPA (−1.13 vs −0.35 without 2026), and that is not
QB-related. Everything else (GB's ratings, context, the intercept) is roughly market-consistent. The explanation is
exact within the model's architecture. Whether it describes football causality is a separate question (§6).

---

## 6. ATL QB / regime change

| question | answer (evidence) |
|---|---|
| Who started ATL Weeks 1–2? | **Cooper Rush** both weeks (nflverse pbp: W1 at PIT, Rush 26 dropbacks, −0.61 EPA/db; W2 vs CAR, Rush 18 and J. Strand 17 dropbacks, −0.68 EPA/db for the team). Sleeper chart: Rush QB1 from 09-12; Tagovailoa and Penix Out. ESPN 09-07: "Penix inactive for opener" |
| Which QB environment produced ATL's 2026 offensive features? | The Rush/Strand environment, 100% of 2026 ATL offensive rows (`2026_01_ATL_PIT`, `2026_02_CAR_ATL`) |
| What did the system expect at QB for ATL? | **Penix QB1, Active, at every horizon packet** (T-24h to T-30m). The coherent sim priced Penix as starter (30.1 attempts, passing-yards football mean 189 vs market mean 210) |
| When was Penix known or expected to start? | Rapoport "could start Thursday" (ESPN item 09-20 11:13Z); **named starter 09-21 20:39Z** (captured 09-22 00:13Z); Sleeper chart QB1 09-22 17:04Z; tag cleared 09-23 11:49Z. All of this was before T-24h (09-24 00:15Z) |
| Did the team-strength model adjust? | **No.** DATA_ONLY has no QB input (recorded on every row as `unavailable_inputs: quarterback identity (no validated coefficient)`). The handicap packet's TEAM STRENGTH table (ATL off dropback −0.135, basis `current_season`) is the same Rush/Strand-era rating, with no regime caveat |
| Did games under a different QB stay fully weighted? | **Yes.** Weight = recency (half-life 10 weeks) × season carry (0.4), nothing else. The two Rush/Strand games are the most recent and therefore the heaviest ATL offence rows |
| Did player / team projections include the change? | Partly. QB identity was correct in the sim and in V3/V4 (Penix charted, not Out). But the pass-catchers' usage and efficiency inputs are EWMA or recent-game based and came from Rush/Strand games (Drake London W1–2: 9 targets, 80 yds). The QB profile ignored Penix's 2024–25 history (`qb_profile_basis = 2026`). V5's resolver would have kept Penix too (`CHART_QB1_AVAILABLE`), so V5 changes nothing on the QB input here |
| Did the market move when the QB information became established? | **Yes.** Kalshi-implied 7.0–7.5 → 6.0 within ~3h of the 09-21 announcement, and 5.5 by 09-23 13:42; consensus 7.0 → 4.5 |

**Did DATA_ONLY over-weight ATL's Weeks 1–2 offence under a different QB regime? Yes.** Without those offensive rows
the centre is GB +3.85, not +7.14. The Week-2 game alone moved it by +2.96. The market, which did incorporate the QB
news, moved the other way. Per the rules, Atlanta is **not patched**. The generic research design is
`research/starter_regime/PREREGISTRATION.md`: model `DATA_ONLY_SRA`, version `starter-regime-0.1.0`,
RESEARCH_ONLY. It adds one parameter, `w_regime`, which down-weights past offensive rows started by a QB other than
the resolver's projected starter. Stage A fits it on 2018–2025 walk-forward only, then freezes it. Stage B is a
preregistered prospective test starting **2026 Week 4**, provided the freeze is committed before Week 4's first
kickoff; otherwise the first week after the freeze. ATL@GB is generation and diagnostic evidence only and is
permanently excluded from validation. It is a separate record and overwrites nothing (V3/V4/V5, DATA_ONLY and its
artifact are untouched).

Research-only implementation: `nfl_edge/research/starter_regime.py`, with 10 tests in
`tests/test_starter_regime_research.py`. The tests cover no-leakage (post-cutoff rows and starters refused; poisoning
post-cutoff rows does not move the ratings; the target game's pbp is never read), equivalence to the production solver
at w = 1, and isolation from every report, arm and shadow path. The retrospective grid for this game (**diagnostic
only; it must not select w**) gives w = 1 → +7.14, 0.5 → +5.98, 0.25 → +5.03, 0 → +3.61. ATL had 41 offensive rows
down-weighted (every non-Penix start in 2023–26) and GB had 5 (non-Love starts).

---

## 7. Rushing / game-script autopsy (descriptive; nothing fitted to 242 or 17)

Projections are from the T-30m packet (sim `20260924T183032Z`, football means). Actuals are from pbp, non-kneel. The
split below is exact: volume effect = (actual − projected carries) × projected yards per carry; efficiency effect =
actual carries × (actual − projected yards per carry).

| | proj carries | proj yds | proj ypc | actual carries | actual yds | actual ypc | **volume effect** | **efficiency effect** | total miss |
|---|---|---|---|---|---|---|---|---|---|
| ATL | 25.0¹ | 119.2 | 4.77 | 39 | 244 | 6.26 | **+66.8** | **+58.0** | +124.8 |
| GB | 27.3 | 110.5 | 4.05 | 9 | 17 | 1.89 | **−74.1** | **−19.4** | −93.5 |

¹ Brian Robinson's carries were `NOT_IN_SIMULATION_RUN` at T-30m, so his 4.7 projected carries come from the legacy
anatomy. Market means at T-30m: ATL rushing 116.8 yds; GB rushing 104.6 yds on 25.1 carries. The market was no
better than the model on either side.

Context:

* **Game script.** ATL led 17–7 at half and 24–7 after three quarters. 42 of GB's 63 plays came while trailing by 8
  or more, and GB ran on 10% of those. ATL ran on 74% of its 27 plays while leading by 8 or more.
* **GB's run rate was low even in neutral script.** 24% within 7 points (xpass 0.61), against W1–2 rush shares of 31%
  and 36%.
* **Efficiency priors.** DATA_ONLY's T-30m ratings: ATL off rush EPA −0.013, GB def rush EPA −0.039 (slightly good),
  GB off rush EPA −0.075, ATL def rush EPA −0.010.
  * ATL's W3 rush offence: +0.28 EPA/rush, against −0.11 and −0.18 in the Rush/Strand games.
  * GB's run defence allowed +0.28, against −0.12 and −0.54 before.
  * GB's own rushing (−0.30) and ATL's run defence (−0.34 allowed) were **in line with their priors**.

| side | attribution |
|---|---|
| GB rushing (−93.5 yds) | **GAME SCRIPT → VOLUME** dominates (−74 yds). There was also some pass-heavy intent beyond script (neutral rush rate below prior). Efficiency (−19) was consistent with GB's poor 2026 rushing and ATL's strong run defence, which is roughly NORMAL VARIANCE around the prior |
| ATL rushing (+124.8 yds) | Split between VOLUME via GAME SCRIPT (+67) and EFFICIENCY (+58). The efficiency jump coincides with (a) the QB change (**QB ENVIRONMENT**: a credible passer plausibly lightens boxes; not measured, since box counts are not captured) and (b) GB's interior DL: Brinson Out; Campbell Out at T-90m; Hargrave Questionable (**OL-DL CONTEXT / UNMODELED STRUCTURAL INPUT**: the system has no DL-availability coefficient, and ATL OT Onianwa was also Out). The residual is **NORMAL VARIANCE** (39 carries at 6.3 ypc is a tail, but a reachable one). Nothing here supports a rushing-model change |

The player autopsy (`autopsy-1.0.0.20260925T121348Z`, legacy anatomy, 69 rows) classifies the misses as
TEAM_VOLUME_MISS 21, NO_LARGE_MISS 20, EFFICIENCY_MISS 13, OPPORTUNITY_MISS 13 and UNEXPLAINED_VARIANCE 2. The
market verdicts are SIMILAR 53, MODEL_MUCH_WORSE 10 and MODEL_BETTER 6. Examples:

* Bijan Robinson rushing: TEAM_VOLUME_MISS (12.2 carries projected by legacy vs 29; ATL team rushes 41 vs a prior mean
  of 31.5).
* Jordan Love attempts: TEAM_VOLUME_MISS (32.5 vs 53).

---

## 8. Player props and the two game-level contracts the owner traded

Entry prices come from the owner receipts on `handicap-data`. The close is the last pregame quote or trade in the
Kalshi captures (kickoff 00:15:00Z). Model columns are from the T-30m packet; T-24h/T-6h/T-90m are in
`traded_markets_by_horizon.json`. **V5** had not been merged at kickoff. It was not replayed here, and any replay would
be **RETROSPECTIVE / EXPLORATORY ONLY**. Its only changed input (QB identity) was the same as V4's for both teams in
this game (Penix and Love, charted and undesignated). The fitted bundle does differ (`qb_identity` config), so V5's
numbers are **not computed and not claimed**.

Timing: **five of the six orders executed after kickoff**:

* 00:15:28Z (Love YES)
* 00:16:21Z (Johnson NO)
* 00:16:45Z (London NO)
* 01:59:59Z (GB YES)
* 02:43:34Z (Love NO)

Only the ATL 1H NO (00:14:46Z) was pregame. Pregame model numbers do not describe in-game prices.

| contract | owner side @ entry | T-30m mid | pregame close | legacy (shadow-0.4) | sim football / reconciled | V3 (DATA_PLAYER_V3) | V4 | HYBRID V3 / V4 (market-derived) | MARKET_PLAYER_DIST (market-derived) | actual | settles |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Love ≥275 pass yds (`GBJLOVE10-275`) | YES @0.26 (in-game 00:15:28) and NO @0.67 (in-game 02:43) | 0.245 | 0.24/0.25, last trade 0.25 | 0.299 | 0.275 / 0.293 | 0.287 | 0.270 | 0.269 / 0.266 | 0.265 | **312** (28/53, 1 sack) | YES |
| K. Johnson ≥30 rush yds (`GBKJOHNSON26-30`) | NO @0.390 (in-game 00:16:21) | 0.635 | 0.63/0.64, last trade 0.63 | 0.146 | 0.359 / 0.517 | 0.252 | 0.350 | 0.564 / 0.579 | 0.619 | **6** (4 carries, 24 snaps) | NO |
| London ≥60 rec yds (`ATLDLONDON5-60`) | NO @0.436 (in-game 00:16:45) | 0.575 | 0.57/0.58, last trade 0.58 | 0.370 | 0.360 / 0.514 | 0.367 | 0.338 | 0.521 / 0.517 | 0.549 | **194** (9/10 targets, 66 snaps) | YES |
| ATL 1H team total ≥10 (`1HTEAMTOTAL…ATL10`) | NO @0.49 (pregame 00:14:46) | 0.515 | 0.51/0.52, last trade 0.51 (the owner's fill) | unsupported | unsupported | – | – | – | BOARD_V2 0.458 | **17** | YES |
| GB moneyline (`KXNFLGAME…GB`) | YES @0.32 (in-game 01:59:59, ATL leading) | 0.695 | 0.68/0.69, last trade 0.69 | 0.694 | 0.667 (sim) | – | – | – | BOARD_V2 0.694; three-arm CURRENT 0.697 / DATA_ONLY **0.755** / HYBRID 0.694 | GB lost 14–35 | NO |

The three-arm values for the moneyline are CRN simulation probabilities at T-30m. Their contract values are 0.6985 /
0.7562 / 0.6951.

Role, usage and classification:

| contract | role / snap expectation | actual usage | classification |
|---|---|---|---|
| Love 275 | QB1. Sim 30.5 attempts; legacy 32.5 | 53 attempts, 66 snaps | **TEAM VOLUME via game script.** Efficiency was *below* projection (5.9 vs 7.3 yds/att). All models leaned modestly above the market in the direction of the result. Mostly NORMAL VARIANCE |
| K. Johnson 30 | RB3 on the depth chart (Lloyd, Brooks, Johnson). Sim 6.8 carries; market-implied ~10 | 4 carries, 24 snaps; GB 9 non-kneel rushes | **TEAM VOLUME (game script) + ROLE ID** (the market priced a larger Johnson role than the chart or sim). Every data arm was far below the market (0.15–0.36 vs 0.635), in the right direction. MARKET DISAGREEMENT resolved in the models' favour on one observation |
| London 60 | LWR1. Sim 4.3 receptions; legacy 5.9 targets | 10 targets, 9 catches, 66 snaps | **QB ENVIRONMENT + TARGET SHARE, then efficiency tail.** The data arms were far below the market (0.34–0.37 vs 0.575) because London's inputs came from the Rush/Strand games (W1–2: 9 targets, 80 yds). The market priced the Penix environment. This is the player-level counterpart of §6. 194 yards is a tail even for the market (NORMAL VARIANCE on top) |
| ATL 1H ≥10 | no football model covers 1H team totals | ATL 17 1H points | **UNSUPPORTED FAMILY.** Only BOARD_V2 (market-shape) has a number. Nothing football-side to autopsy beyond §5/§6 (the ATL offence rating was stale) |
| GB ML | – | – | Pregame: every arm put GB at 0.67–0.76 and GB lost by 21; in a sample of one that is NORMAL VARIANCE. DATA_ONLY was the most wrong (home-win Brier at T-30m, from the arm evaluation: DATA_ONLY 0.570, CURRENT 0.486, HYBRID 0.482). The owner's entry was in-game and outside any model's scope |

---

## 9. Player-simulation coverage

**The 105 × NOT_IN_SIMULATION_RUN in today's packet is expected.** The Saturday rebuild (`11b5b2c8f5c0cd72c4a0`,
20:26Z) attaches today's sim run `20260926T174604Z`, which prices only unplayed games. ATL@GB kicked off on 09-25, so
there are no rows for it. The game is marked `STARTED_OR_UNKNOWN` with a GAME_STARTED block flag.

**The actionable T-30m packet had coherent-simulation coverage** (`coverage_by_horizon.json`):

| | T-24h | T-6h | T-90m | **T-30m** |
|---|---|---|---|---|
| listed FULL player/stat groups | 99 | 104 | 105 | **105** |
| simulated and exposed | 60 | 63 | 66 | **66** |
| unsupported stat (fantasy, longest, rush+rec, INT, FG) | 36 | 36 | 36 | 36 |
| identity unresolved (D/ST TD) | 2 | 2 | 2 | 2 |
| not in simulation run | 1 | 3 | 1 | **1** (Brian Robinson carries) |
| unsupported coherence / error / not eligible / rules | 0 | 0 | 0 | 0 |
| silently missing | 0 | 0 | 0 | 0 |

The traded Love, Johnson and London rungs were all `PRICED` by the simulation at T-30m. So there is no coverage root
cause to fix.

**A real defect was found: simulation staleness, which the packet did not record.** A force_fresh RUN NFL build
freshens the ledger (`price_slate.py`, gated at 45 min) and the context (gated), but takes the coherent simulation from
the market-data clone as fetched. The simulation has no age gate and no age record. The consequences at each horizon:

* **T-30m:** the sim's market was observed at 18:18Z, against a ledger capture of 23:45Z: **327 min of lag**, and 348
  min old at build. The sim therefore predates the Rush/Strand/Onianwa/DeWalt/Longerbeam Out designations the ledger
  had.
* **The newer run was missed by four minutes.** Sim run `20260924T231506Z` reached market-data at 23:52:59Z. The
  packet's clone was `846891c` (23:49:07Z).
* **Other horizons:** the lag was 167 / 283 / 268 min at T-24h / T-6h / T-90m. Today's Sunday packet (latest/) lags by
  **145 min**. The ~5-hour gap between sim runs (00:46, 07:45, 13:37, 18:30, 23:15 on 09-24) makes this structural.

**Fix implemented (reporting only, no gate, no packet number changed).** `simulation_vintage()` in
`nfl_edge/handicap/report_freshness.py` records the simulation's run id, `market_observed_at`, age at build and lag
against the ledger's capture in `manifest.json → vintages.simulation`. It also records a status: `ALIGNED`,
`LAGS_LEDGER` (lag > 120 min), `UNKNOWN` or `MISSING`, and `build_report.py` prints it. Tests are in
`tests/test_simulation_vintage.py` (6), which pin the Thursday case at 326.7 min.

**Proposed, not implemented (infrastructure, needs owner review):**

1. Re-fetch market-data immediately before "Build the handicap packet" in `run-nfl.yml`, so a sim run published during
   the build is used.
2. Or, in force_fresh horizon runs, run the sim projection locally against the fresh ledger, as is already done for
   `price_slate.py`.

Either way, a lagging simulation must stay labelled as such. It must never be silently replaced with legacy
projections presented as simulation.

**Sunday Week 3 (tomorrow).** Coverage exists for every game. NOT_IN_SIMULATION_RUN is 0 for 13 of the 15 remaining
games. The exceptions are PHI@CHI with 6 (Cole Kmet receiving yards / receptions / longest reception; Odunze, Barkley
and Hurts longest) and MIN@TB with 2 (Aaron Jones longest reception, rush+rec). The Kmet yards/receptions groups are
normally simulated stats and are worth checking at the T-24h/T-6h packets. Most likely they are listings newer than
the 17:46Z sim run (not verified).

---

## 10. What went well / what failed / what was just variance / what should change

**WHAT WENT WELL**
* Point-in-time discipline held. DATA_ONLY was reproduced bit-for-bit from public data, with Week 3 excluded exactly as
  at capture. All four horizons were captured and the arm evaluation ran automatically. Movement was correctly scored
  UNCHANGED.
* QB identity was right everywhere it is modelled (packet, sim, V3/V4): Penix was QB1 from T-24h.
* Coverage accounting was complete: 0 silently missing, and every refusal was reasoned.
* On the two GB rushing contracts the data arms disagreed strongly with the market in the direction of the result
  (one observation; no inference).

**WHAT FAILED**
* DATA_ONLY priced a QB regime that no longer existed. It had no QB input by design, and the Rush/Strand games were
  fully weighted. This is a documented limitation that bit, rather than a bug.
* The packet's team-strength table showed Rush/Strand-era ATL ratings with no regime caveat. The QB profile ignored
  Penix's 2024–25 history (`qb_profile_basis = 2026`).
* Player inputs for ATL pass-catchers carried the old QB environment (London).
* The simulation attached to the T-30m packet was 5.5 h stale relative to the ledger, and the manifest did not say so.
* Five of the six owner orders were in-game, outside any pregame model's scope. This is a process observation, not a
  football one.

**WHAT WAS JUST VARIANCE**
* The 21-point margin against a 5.5 line: roughly a 2-SD event on the residual SD of ~12.6. Every arm, and the market,
  missed it by 25+ points.
* The size of ATL's rushing (39 carries at 6.3 ypc) and London's 194 yards, beyond what any QB-regime correction
  implies.
* GB's rushing efficiency, which was in line with priors.

**WHAT SHOULD CHANGE**

| type | item |
|---|---|
| INFRASTRUCTURE FIX | Re-fetch market-data right before the packet build, or run the sim locally in force_fresh builds (proposal §9) |
| REPORTING FIX | Simulation vintage in the manifest (**done**, `simulation_vintage`). Add a "QB regime" caveat to TEAM STRENGTH when the projected starter did not start the games behind the rating. Widen `qb_profile_basis` beyond the current season for a starter with no current-season dropbacks. Both are proposals, not implemented |
| RESEARCH QUESTION | Do pass-catcher usage/efficiency inputs need QB-regime conditioning? (London: V3/V4 at 0.34–0.37 vs market 0.575) |
| MODEL CHALLENGER | `DATA_ONLY_SRA` / `starter-regime-0.1.0`: preregistered, RESEARCH_ONLY, Stage A historical then Stage B prospective from Week 4 (`research/starter_regime/PREREGISTRATION.md`) |
| NO CHANGE / NEED MORE DATA | Rushing model, game-script model, DATA_ONLY coefficients, HYBRID weight, V3/V4/V5 status, every gate and threshold. The three-arm experiment is at 1 game of its 64-game minimum |

## Open limitations

* Archived packets exist only as Actions artifacts (expire 2026-12-23). `handicap-reports` keeps no history.
* nflverse play-by-play was re-downloaded on 09-26. The reproduction matched bit-for-bit, so no revision affected
  Weeks 1–2, but that is only established for the DATA_ONLY inputs.
* V5 was not replayed. Snap counts beyond the autopsy's are not captured. There are no box-count, pressure or OL-grade
  data, so QB-environment and OL-DL attributions are qualitative.
* The ATL projected-carry figure mixes the sim and legacy anatomy (Brian Robinson not in the sim run).
