# NFL HANDICAP PACKET — 2026 Week 6

- run id: `20261018T010846Z`  ·  packet sha: `25b757423c983e62190b`
- built at: 2026-10-18T01:08:46.609939+00:00  (all timestamps UTC)
- ledger: `20261018T003825Z.shadow-0.4.0.observations.jsonl.gz`  ·  model: `shadow-0.4.0`
- context captures: ['20261017T232036Z', '20261018T003737Z']
- team-profile basis: **current_season**
- **REAL-MONEY STATUS: NOT VALIDATED -- this packet recommends nothing and authorises nothing**
- **SIMULATION FRESHNESS: SIM_CURRENT** — run `20261018T003825Z` (RUN_NFL_FROZEN_BUNDLE), lag 0.0m vs target <= 180.0m; the simulation priced this packet's own board

> This packet contains no recommendations. Every model-vs-market number is a *disagreement*, which is not an edge. The model has been shown redundant to the closing market on player props and behind it on game outcomes; it is here as structure and context, not as a superior forecast.

## SLATE SUMMARY

- games: **14**
- markets listed this slate: **10387**, model-supported: **4960**
- ledger support states (all weeks): `{'UNSUPPORTED_MODEL': 14660, 'UNSUPPORTED_RULES': 4817, 'SUPPORTED': 5420, 'UNSUPPORTED_IDENTITY': 120, 'UNSUPPORTED_GAME': 2, 'POST_KICKOFF_EXCLUDED': 58242}`

### FULL-BOARD COVERAGE

_RUN NFL examines every executable Kalshi contract for every requested unstarted NFL game. UNSUPPORTED_MODEL is a statement about one model, never a reason to hide a contract. Every listed contract terminates in exactly one analysis state, in one of four buckets: A validated model view, B coherent/Shadow research view, C manual handicap from the packet's own football and context data, D explicit PASS with a named reason._

| bucket | contracts | meaning |
|---|---|---|
| **A** | 4960 | validated/production model view available |
| **B** | 2686 | coherent / Shadow research model view available |
| **C** | 1658 | no automated pricing authority; handicap from the football and context data in this packet |
| **D** | 207 | cannot defensibly price -- explicit PASS / RESEARCH REQUIRED, with a reason |
| **-** | 876 | outside the pregame window (kickoff has passed) |
| **!** | 0 | INVARIANT VIOLATION -- a listed contract with no analysis state |

- listed: **10387** · executable books: **9107**
- incumbent priced: **4960** · coherent simulation: **0** · Shadow v2 research: **2686**
- manual handicap required: **1658** · research required: **52**
- rules blocked: **35** · identity blocked: **120** · non-football: **0**
- post-kickoff (stale): **876**
- **silently omitted: 0** — this must be 0.

| family / period | listed | executable | incumbent priced | coherent sim | shadow v2 | manual research | research required | rules blocked | identity blocked | non football | post kickoff | silently omitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLAYER_STAT/FULL | 4986 | 4616 | 3956 | 0 | 81 | 358 | 0 | 0 | 120 | 0 | 471 | 0 |
| FIRST_TD_TEAM/FULL | 413 | 105 | 0 | 0 | 0 | 371 | 0 | 10 | 0 | 0 | 32 | 0 |
| FIRST_TD_SCORER/FULL | 372 | 372 | 0 | 0 | 0 | 337 | 0 | 7 | 0 | 0 | 28 | 0 |
| TEAM_TOTAL/FULL | 371 | 370 | 344 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 27 | 0 |
| SPREAD/FULL | 359 | 359 | 335 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 24 | 0 |
| TEAM_TOTAL/1H | 305 | 303 | 0 | 0 | 284 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| TEAM_STAT/FULL | 280 | 35 | 0 | 0 | 0 | 260 | 0 | 0 | 0 | 0 | 20 | 0 |
| TOTAL/FULL | 267 | 267 | 247 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| SPREAD/1H | 221 | 221 | 0 | 0 | 204 | 0 | 0 | 0 | 0 | 0 | 17 | 0 |
| SPREAD/2H | 220 | 217 | 0 | 0 | 204 | 0 | 0 | 0 | 0 | 0 | 16 | 0 |
| RACE_TO_N/FULL | 210 | 82 | 0 | 0 | 0 | 195 | 0 | 0 | 0 | 0 | 15 | 0 |
| TOTAL/1H | 186 | 186 | 0 | 0 | 173 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |
| TOTAL/2H | 186 | 178 | 0 | 0 | 173 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |
| GAME_PLAYER_LEADER/FULL | 172 | 76 | 0 | 0 | 0 | 137 | 0 | 18 | 0 | 0 | 17 | 0 |
| SPREAD/4Q | 154 | 149 | 0 | 0 | 141 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |
| SPREAD/2Q | 153 | 153 | 0 | 0 | 139 | 0 | 0 | 0 | 0 | 0 | 14 | 0 |
| SPREAD/3Q | 151 | 151 | 0 | 0 | 140 | 0 | 0 | 0 | 0 | 0 | 11 | 0 |
| SPREAD/1Q | 143 | 143 | 0 | 0 | 133 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/1Q | 140 | 140 | 0 | 0 | 130 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/2Q | 140 | 136 | 0 | 0 | 130 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/3Q | 140 | 140 | 0 | 0 | 130 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/4Q | 140 | 118 | 0 | 0 | 130 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| HALF_FULL_RESULT/1H | 126 | 124 | 0 | 0 | 117 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| WIN_MARGIN_BUCKET/FULL | 98 | 97 | 0 | 0 | 91 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| BOTH_TEAMS_SCORE_N/FULL | 56 | 18 | 52 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| GAME_EVENT/FULL | 56 | 53 | 0 | 0 | 0 | 0 | 52 | 0 | 0 | 0 | 4 | 0 |
| PERIOD_WINNER/1H | 42 | 42 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/1Q | 42 | 42 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2H | 42 | 42 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2Q | 42 | 42 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/3Q | 42 | 42 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/4Q | 42 | 42 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| GAME_WINNER/FULL | 28 | 28 | 26 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| BOTH_TEAMS_SCORE/1Q | 14 | 5 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/2Q | 14 | 3 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/3Q | 14 | 2 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/4Q | 14 | 2 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| PLAYER_H2H/FULL | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |

_A Shadow v2 or coherent-simulation projection is RESEARCH. It is not validated, it is never mixed into the incumbent's probability or its disagreement ranking, and it reaches no recommendation, staking or preflight path._

**Skill players ruled OUT (40)**

- Dallen Bentley (TE, DEN) — Out · 2026_06_SEA_DEN
- Sam Ehlinger (QB, DEN) — Out · 2026_06_SEA_DEN
- Pat Bryant (WR, DEN) — Injured Reserve · 2026_06_SEA_DEN
- Jalen Milroe (QB, SEA) — Out · 2026_06_SEA_DEN
- Montorie Foster Jr. (WR, SEA) — Out · 2026_06_SEA_DEN
- Robert Henry Jr. (RB, SEA) — Out · 2026_06_SEA_DEN
- Zach Charbonnet (RB, SEA) — Out · 2026_06_SEA_DEN
- Jadarian Price (RB, SEA) — Injured Reserve · 2026_06_SEA_DEN
- David Montgomery (RB, HOU) — Out · 2026_06_HOU_JAX
- Tank Dell (WR, HOU) — Injured Reserve · 2026_06_HOU_JAX
- Lamar Jackson (QB, BAL) — Out · 2026_06_BAL_CLE
- Matt Hibner (TE, BAL) — Out · 2026_06_BAL_CLE
- Dillon Gabriel (QB, CLE) — Injured Reserve · 2026_06_BAL_CLE
- Dylan Sampson (RB, CLE) — Injured Reserve · 2026_06_BAL_CLE
- Raheim Sanders (RB, CLE) — Injured Reserve · 2026_06_BAL_CLE

**New or changed since the previous capture (4)** — the most decision-relevant section on the page

- Jawhar Jordan (RB, HOU): **Active** (new record) · 2026_06_HOU_JAX
- Zavier Scott (RB, CHI): **Active** (new record) · 2026_06_CHI_ATL
- Cedric Tillman (WR, NO): **Active** (new record) · 2026_06_NO_NYG
- Romello Height (DE, SF): **Active** (was Questionable) · 2026_06_WAS_SF

**Weather flagged material**

- 2026_06_PIT_TB: wind 15 mph, precip 0%

**Largest market moves since first capture**

| ticker | game | family | move |
|---|---|---|---|
| `KXNFL4QSPREAD-26OCT15SEADEN-SEA11` | 2026_06_SEA_DEN | SPREAD | +0.925 |
| `KXNFLOT-26OCT15SEADEN-Y` | 2026_06_SEA_DEN | GAME_EVENT | +0.925 |
| `KXNFLREC-26OCT15SEADEN-SEARSHAHEED22-5` | 2026_06_SEA_DEN | PLAYER_STAT | +0.925 |
| `KXNFL2QSPREAD-26OCT15SEADEN-DEN11` | 2026_06_SEA_DEN | SPREAD | +0.920 |
| `KXNFLREC-26OCT15SEADEN-SEAJSMITHNJIGBA11-11` | 2026_06_SEA_DEN | PLAYER_STAT | +0.915 |
| `KXNFLREC-26OCT15SEADEN-SEACKUPP10-5` | 2026_06_SEA_DEN | PLAYER_STAT | +0.900 |
| `KXNFL2QSPREAD-26OCT15SEADEN-DEN8` | 2026_06_SEA_DEN | SPREAD | +0.895 |
| `KXNFLRECYDS-26OCT15SEADEN-SEACKUPP10-50` | 2026_06_SEA_DEN | PLAYER_STAT | +0.890 |
| `KXNFL4QSPREAD-26OCT15SEADEN-SEA8` | 2026_06_SEA_DEN | SPREAD | +0.890 |
| `KXNFLRECYDS-26OCT15SEADEN-SEARSHAHEED22-60` | 2026_06_SEA_DEN | PLAYER_STAT | +0.885 |

**Largest model/market disagreements** — DISAGREEMENT ONLY, REQUIRES HANDICAP

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT18NONYG-NYGILIKELY9-3` | Isaiah Likely | 3.0 | 0.88 | 0.88 | 0.19 | -0.685 |
| `KXNFLRSHYDS-26OCT18NYJNE-NYJBALLEN0-40` | Braelon Allen | 40.0 | 0.79 | 0.81 | 0.13 | -0.657 |
| `KXNFLRSHATT-26OCT18NYJNE-NYJBALLEN0-14` | Braelon Allen | 14.0 | 0.74 | 0.76 | 0.10 | -0.644 |
| `KXNFLREC-26OCT18NONYG-NYGILIKELY9-4` | Isaiah Likely | 4.0 | 0.76 | 0.76 | 0.11 | -0.642 |
| `KXNFLRSHATT-26OCT18BALCLE-CLEDWATSON4-4` | Deshaun Watson | 4.0 | 0.85 | 0.88 | 0.22 | -0.639 |
| `KXNFLRECYDS-26OCT18NONYG-NYGILIKELY9-25` | Isaiah Likely | 25.0 | 0.81 | 0.82 | 0.18 | -0.636 |
| `KXNFLRSHYDS-26OCT18CARPHI-PHIDPIERCE39-30` | Dameon Pierce | 30.0 | 0.78 | 0.80 | 0.15 | -0.634 |
| `KXNFLRSHATT-26OCT18LACKC-KCKWALKER9-16` | Kenneth Walker III | 16.0 | 0.75 | 0.76 | 0.12 | -0.634 |
| `KXNFLRSHYDS-26OCT18HOUJAC-JACBTUTEN33-40` | Bhayshul Tuten | 40.0 | 0.78 | 0.78 | 0.14 | -0.631 |
| `KXNFLREC-26OCT18TENIND-TENCTATE14-3` | Carnell Tate | 3.0 | 0.81 | 0.83 | 0.18 | -0.631 |
| `KXNFLPASSTDS-26OCT18CARPHI-PHIJHURTS1-1` | Jalen Hurts | 1.0 | 0.65 | 0.65 | 0.02 | -0.629 |
| `KXNFLREC-26OCT18BUFLV-LVBBOWERS89-5` | Brock Bowers | 5.0 | 0.78 | 0.78 | 0.15 | -0.626 |

**Highest-liquidity markets**

- `KXNFLGAME-26OCT15SEADEN-SEA` (GAME_WINNER, 2026_06_SEA_DEN): volume 43767688, OI 19982052
- `KXNFLGAME-26OCT15SEADEN-DEN` (GAME_WINNER, 2026_06_SEA_DEN): volume 21849104, OI 10638907
- `KXNFLSPREAD-26OCT15SEADEN-SEA3` (SPREAD, 2026_06_SEA_DEN): volume 5634203, OI 4043102
- `KXNFLTD-26OCT15SEADEN-SEAJSMITHNJIGBA11-1` (PLAYER_STAT, 2026_06_SEA_DEN): volume 1808571, OI 1348823
- `KXNFLTOTAL-26OCT15SEADEN-41` (TOTAL, 2026_06_SEA_DEN): volume 1578988, OI 772751
- `KXNFLSPREAD-26OCT15SEADEN-DEN8` (SPREAD, 2026_06_SEA_DEN): volume 1220614, OI 571100
- `KXNFLGAME-26OCT18CARPHI-PHI` (GAME_WINNER, 2026_06_CAR_PHI): volume 1218881, OI 1018635
- `KXNFLGAME-26OCT18CARPHI-CAR` (GAME_WINNER, 2026_06_CAR_PHI): volume 1185865, OI 944836

**BLOCKING data issues**

- 2026_06_SEA_DEN: `GAME_STARTED` — kickoff has passed; this is not a pregame packet

### GAME PRIORITY FOR HANDICAP

_Priority ranks where deeper review may be most useful. It is NOT a bet ranking and carries no expectation that these games contain value._

| # | game | score | why |
|---|---|---|---|
| 1 | 2026_06_WAS_SF | 14.98 | 1 new/changed injury records; 6 skill players ruled out (role change); largest market move 0.460; largest reconciled simulation disagreement 0.148; raw incumbent disagreement 0.531 (NOT scored: unvalidated); 283 supported player-prop rungs |
| 2 | 2026_06_PIT_TB | 14.5 | 5 skill players ruled out (role change); material weather; largest market move 0.180; raw incumbent disagreement 0.585 (NOT scored: unvalidated); 297 supported player-prop rungs |
| 3 | 2026_06_NO_NYG | 13.51 | 1 new/changed injury records; 3 skill players ruled out (role change); largest market move 0.145; largest reconciled simulation disagreement 0.151; raw incumbent disagreement 0.685 (NOT scored: unvalidated); 296 supported player-prop rungs |
| 4 | 2026_06_CAR_PHI | 12.65 | 7 skill players ruled out (role change); largest market move 0.405; largest reconciled simulation disagreement 0.115; raw incumbent disagreement 0.634 (NOT scored: unvalidated); 289 supported player-prop rungs |
| 5 | 2026_06_BAL_CLE | 12.27 | 5 skill players ruled out (role change); largest market move 0.205; largest reconciled simulation disagreement 0.077; raw incumbent disagreement 0.639 (NOT scored: unvalidated); 266 supported player-prop rungs |
| 6 | 2026_06_HOU_JAX | 11.55 | 1 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.180; largest reconciled simulation disagreement 0.105; raw incumbent disagreement 0.631 (NOT scored: unvalidated); 343 supported player-prop rungs |
| 7 | 2026_06_LAC_KC | 10.78 | 3 skill players ruled out (role change); largest market move 0.200; largest reconciled simulation disagreement 0.078; raw incumbent disagreement 0.634 (NOT scored: unvalidated); 318 supported player-prop rungs |
| 8 | 2026_06_CHI_ATL | 10.42 | 1 new/changed injury records; 1 skill players ruled out (role change); largest market move 0.200; largest reconciled simulation disagreement 0.142; raw incumbent disagreement 0.534 (NOT scored: unvalidated); 327 supported player-prop rungs |
| 9 | 2026_06_SEA_DEN | 10.0 | 8 skill players ruled out (role change); largest market move 0.925; BLOCKING data issue -- review before trusting anything here |
| 10 | 2026_06_NYJ_NE | 9.91 | 2 skill players ruled out (role change); largest market move 0.245; largest reconciled simulation disagreement 0.141; raw incumbent disagreement 0.657 (NOT scored: unvalidated); 259 supported player-prop rungs |
| 11 | 2026_06_BUF_LV | 9.61 | 2 skill players ruled out (role change); largest market move 0.150; largest reconciled simulation disagreement 0.111; raw incumbent disagreement 0.626 (NOT scored: unvalidated); 278 supported player-prop rungs |
| 12 | 2026_06_ARI_LA | 9.58 | 2 skill players ruled out (role change); largest market move 0.470; largest reconciled simulation disagreement 0.108; raw incumbent disagreement 0.558 (NOT scored: unvalidated); 347 supported player-prop rungs |
| 13 | 2026_06_DAL_GB | 9.54 | 2 skill players ruled out (role change); largest market move 0.225; largest reconciled simulation disagreement 0.104; raw incumbent disagreement 0.617 (NOT scored: unvalidated); 343 supported player-prop rungs |
| 14 | 2026_06_TEN_IND | 9.03 | 2 skill players ruled out (role change); largest market move 0.145; largest reconciled simulation disagreement 0.053; raw incumbent disagreement 0.631 (NOT scored: unvalidated); 310 supported player-prop rungs |

> Each game below is summarised. Full detail -- complete market board, every player ladder, all best-expression groups -- is in that game's own file under `games/`.


---

## SEA @ DEN — `2026_06_SEA_DEN`

- kickoff: 2026-10-16T00:15:00+00:00 (-2934 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 876 listed across 17 families — 0 supported, 25 no model, 54 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 876/876 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 54 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.17 | -- |
| total | 33.55 | -- |
| score | DEN 15.7 – SEA 17.9 | DEN -- – SEA -- |
| win prob DEN | 45.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -12.00 / total 16.50 · **2H** spread 11.94 / total 14.27 · **1Q** spread 3.00 / total -- · **2Q** spread -12.50 / total 14.50 · **3Q** spread -0.50 / total -- · **4Q** spread 12.50 / total 12.50

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.17 · total 33.55
- move `KXNFL4QSPREAD-26OCT15SEADEN-SEA11` +0.925
- move `KXNFL2QSPREAD-26OCT15SEADEN-DEN11` +0.920
- move `KXNFL2QSPREAD-26OCT15SEADEN-DEN8` +0.895
- move `KXNFL4QSPREAD-26OCT15SEADEN-SEA8` +0.890

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261018T003825Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (6; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 29 market(s), e.g. KXNFLTD-26OCT15SEADEN-SEAEARROYO18-2, KXNFL1HFT-26OCT15SEADEN-DENTIE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 12 market(s), e.g. KXNFLSPREAD-26OCT15SEADEN-SEA7, KXNFLSPREAD-26OCT15SEADEN-SEA6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 253 market(s), e.g. KXNFL1HFT-26OCT15SEADEN-DENTIE, KXNFL2HTOTAL-26OCT15SEADEN-25
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 20 market(s), e.g. KXNFL2HSPREAD-26OCT15SEADEN-SEA7, KXNFLFFPTS-26OCT15SEADEN-DENDENDST-6P5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 219 market(s), e.g. KXNFLFFPTS-26OCT15SEADEN-SEASDARNOLD14-14P2, KXNFLFFPTS-26OCT15SEADEN-SEAJMYERS5-7P9
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 161 market(s), e.g. KXNFLFG-26OCT15SEADEN-SEA4, KXNFLFG-26OCT15SEADEN-SEA3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261018T003825Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (17)**

- Jalen Milroe (QB, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Sam Ehlinger (QB, DEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Dallen Bentley (TE, DEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jadarian Price (RB, SEA) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Montorie Foster Jr. (WR, SEA) — Out [single_source] — ruled out -- role redistributes to the depth chart behind him
- Pat Bryant (WR, DEN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Robert Henry Jr. (RB, SEA) — Out [single_source] — ruled out -- role redistributes to the depth chart behind him
- Zach Charbonnet (RB, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- _...and 9 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Elijah Arroyo (TE, SEA) — Questionable [conflicting]
- Tyler Badie (RB, DEN) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 118 listed player/stat groups simulated and exposed, 118 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Dallen Bentley (TE, DEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Sam Ehlinger (QB, DEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Tyler Badie (RB), Elijah Arroyo (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL4QSPREAD-26OCT15SEADEN-SEA11 moved +0.925 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_SEA_DEN.md`_


---

## HOU @ JAX — `2026_06_HOU_JAX`

- kickoff: 2026-10-18T13:30:00+00:00 (741 minutes away) · state **PREGAME**
- venue: Wembley Stadium · roof outdoors · surface grass
- markets: 793 listed across 16 families — 420 supported, 310 no model, 48 rules unresolved, 15 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 15 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.67 | -2.46 |
| total | 42.83 | 42.95 |
| score | JAX 22.8 – HOU 20.1 | JAX 22.7 – HOU 20.2 |
| win prob JAX | 56.5% | 57.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -1.36 / total 21.10 · **2H** spread -0.36 / total 21.00 · **1Q** spread -0.97 / total 7.81 · **2Q** spread -0.47 / total 12.68 · **3Q** spread 0.15 / total 8.07 · **4Q** spread -0.08 / total 11.52

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -2.67 · total 42.83
- move `KXNFLTOTAL-26OCT18HOUJAC-49` -0.105
- move `KXNFL2QTOTAL-26OCT18HOUJAC-15` +0.100

**Game environment** (simulation, mean and middle 50%) — home margin 2.6 (-5.0–10.0) · total 43.6 (35.0–51.0) · P(one score) 52.8% · P(17+ blowout) 18.0% · P(total 10+ over centre) 23.4%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| JAX | 62.4 (57.0–68.0) | 32.2 (27.0–37.0) | 24.5 (20.0–29.0) | 36.9 (31.0–42.0) | 0.593 (0.525–0.661) | 0.503 / 0.688 |
| HOU | 62.5 (57.0–68.0) | 34.9 (30.0–40.0) | 23.4 (18.0–28.0) | 38.5 (33.0–44.0) | 0.617 (0.551–0.684) | 0.514 / 0.690 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| JAX | 00-0040719 | RB | 2.2 (0.0–3.0) | 16.0 (11.0–21.0) | 7.1% | 65.0% | MEDIUM |
| JAX | 00-0038606 | WR | 6.8 (4.0–9.0) | 0.3 (0.0–0.0) | 21.9% | 1.3% | HIGH |
| JAX | 00-0038611 | RB | 0.5 (0.0–1.0) | 5.2 (1.0–8.0) | 1.7% | 21.2% | HIGH |
| JAX | 00-0038935 | TE | 5.3 (3.0–7.0) | 0.0 (0.0–0.0) | 17.0% | 0.1% | HIGH |
| HOU | 00-0040583 | RB | 2.4 (0.0–3.0) | 16.9 (12.0–22.0) | 7.2% | 72.2% | MEDIUM |
| HOU | 00-0036554 | WR | 7.1 (4.0–10.0) | 0.2 (0.0–0.0) | 21.7% | 0.9% | HIGH |
| HOU | 00-0039163 | QB | 0.2 (0.0–0.0) | 5.3 (2.0–7.0) | 0.6% | 12.9% | HIGH |
| HOU | 00-0034383 | TE | 4.5 (2.0–6.0) | 0.0 (0.0–0.0) | 13.8% | 0.0% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 13 market(s), e.g. KXNFLPASSCOMP-26OCT18HOUJAC-JACTLAWRENCE16-25, KXNFLPASSCOMP-26OCT18HOUJAC-JACTLAWRENCE16-20
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 42 market(s), e.g. KXNFL3QSPREAD-26OCT18HOUJAC-JAC4, KXNFL4Q-26OCT18HOUJAC-JAC
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 24 market(s), e.g. KXNFLSPREAD-26OCT18HOUJAC-JAC8, KXNFLSPREAD-26OCT18HOUJAC-JAC18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTEAMTOTAL-26OCT18HOUJAC-HOU18, KXNFLTOTAL-26OCT18HOUJAC-37
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 255 market(s), e.g. KXNFL1H-26OCT18HOUJAC-TIE, KXNFL1HFT-26OCT18HOUJAC-TIEJAC
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 24 market(s), e.g. KXNFL1HTOTAL-26OCT18HOUJAC-8, KXNFL1HTOTAL-26OCT18HOUJAC-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 28.6%  _(final margin within one score (8 points) either way; total within 10 of the centre 42.8333 (median favourite-oriented margin +2, median total 43))_
2. favourite controls / normal scoring — 17.7%  _(JAX (favourite) wins by more than one score; total within 10 of the centre 42.8333 (median favourite-oriented margin +13, median total 42))_
3. competitive / low scoring — 12.4%  _(final margin within one score (8 points) either way; total 32.8333 or fewer (centre 42.8333) (median favourite-oriented margin +2, median total 28))_
4. competitive / high scoring — 11.9%  _(final margin within one score (8 points) either way; total 52.8333+ (centre 42.8333) (median favourite-oriented margin +1, median total 60))_
5. underdog controls / normal scoring — 10.0%  _(HOU (underdog) wins by more than one score; total within 10 of the centre 42.8333 (median favourite-oriented margin -13, median total 43))_
   Other — 19.5%

Marginal events (overlapping): one_score 52.8% · blowout_17 18.0% · favorite_wins 60.7% · favorite_controls 29.6% · upset 39.1% · shootout 23.4% · low_scoring 20.4% · low_possession 11.0% · high_volume_passing 7.3% · run_heavy_control 12.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): no point-in-time forecast attached._

**`KXNFLTD-26OCT18HOUJAC-HOUFMOREAU87-1`** Foster Moreau touchdowns 1
- MODEL / MARKET: football 8.4% · market 7.5% · reconciled 18.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.5% · failure mass 100.0% · win-contribution HHI 0.169

**`KXNFLTD-26OCT18HOUJAC-JACBTUTEN33-2`** Bhayshul Tuten touchdowns 2
- MODEL / MARKET: football 12.0% · market 6.5% · reconciled 9.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 2.3% · failure mass 100.0% · win-contribution HHI 0.205

**`KXNFLTD-26OCT18HOUJAC-HOUCSTROUD7-1`** C.J. Stroud touchdowns 1
- MODEL / MARKET: football 17.9% · market 9.5% · reconciled 11.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.8% · failure mass 100.0% · win-contribution HHI 0.168

**`KXNFLTD-26OCT18HOUJAC-HOUNCOLLINS12-1`** Nico Collins touchdowns 1
- MODEL / MARKET: football 28.0% · market 34.5% · reconciled 32.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 18.1% · failure mass 100.0% · win-contribution HHI 0.175
- THESIS DEPENDENCY with `KXNFLPASSTDS-26OCT18HOUJAC-HOUCSTROUD7-2`: cash correlation 0.322 · joint cash 17.6% · Jaccard of winning rows 0.365 · shared failure 51.7%

_410 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 47 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- David Montgomery (RB, HOU) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tank Dell (WR, HOU) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Anton Harrison (OT, JAX) — Injured Reserve [high] — ruled out
- Jalen Pitre (S, HOU) — Out [high] — ruled out
- Montaric Brown (CB, JAX) — Out [high] — ruled out
- Ross Matiscik (LS, JAX) — Out [single_source] — ruled out

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Henry To'oTo'o (LB, HOU) — Questionable [high]
- Ja'Marcus Ingram (CB, HOU) — Questionable [high]

### WEATHER

played at Wembley Stadium, not JAX's home stadium -- no forecast for this venue is captured, and the home stadium's forecast is not shown (scheduled stadium id LON00 (Wembley Stadium) is not JAX's home stadium JAX00 (EverBank Stadium))

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 69 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C.J. Stroud | HOU | attempts | 33.6 | 34.0 | 29.0 | 39.0 | 20.0 | 47.0 | 36.1 | 36.0 | 33.6 | 34.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Woody Marks | HOU | carries | 16.9 | 17.0 | 12.0 | 22.0 | 5.0 | 29.0 | 14.8 | 14.0 | 16.9 | 17.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| C.J. Stroud | HOU | carries | 5.3 | 4.0 | 2.0 | 7.0 | 1.0 | 13.0 | 3.2 | 3.0 | 5.3 | 4.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| C.J. Stroud | HOU | completions | 20.1 | 20.0 | 16.0 | 24.0 | 11.0 | 30.0 | 22.6 | 22.0 | 20.1 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| C.J. Stroud | HOU | passing_tds | 1.3 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.5 | 1.0 | 1.5 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| C.J. Stroud | HOU | passing_yards | 238.6 | 235.0 | 182.0 | 290.0 | 112.0 | 381.0 | 257.7 | 253.0 | 257.7 | 254.0 | 0.00 | 0.97 | 10 | PRICED |
| Nico Collins | HOU | receiving_yards | 59.7 | 51.0 | 24.0 | 85.0 | 0.0 | 148.0 | 81.2 | 72.0 | 81.0 | 69.0 | 0.00 | 0.98 | 13 | PRICED |
| Dalton Schultz | HOU | receiving_yards | 32.9 | 25.0 | 9.0 | 48.0 | 0.0 | 95.0 | 35.1 | 29.0 | 35.2 | 27.0 | 0.00 | 0.97 | 8 | PRICED |

_8 of 69 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 69 of 110 listed player/stat groups simulated and exposed, 41 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26OCT18HOUJAC-JACBTUTEN33-40` | Bhayshul Tuten | 40.0 | 0.78 | 0.78 | 0.14 | -0.631 |
| `KXNFLRSHATT-26OCT18HOUJAC-JACBTUTEN33-14` | Bhayshul Tuten | 14.0 | 0.70 | 0.71 | 0.11 | -0.599 |
| `KXNFLRSHYDS-26OCT18HOUJAC-JACBTUTEN33-50` | Bhayshul Tuten | 50.0 | 0.65 | 0.66 | 0.09 | -0.564 |
| `KXNFLREC-26OCT18HOUJAC-HOUNCOLLINS12-5` | Nico Collins | 5.0 | 0.68 | 0.68 | 0.16 | -0.510 |
| `KXNFLREC-26OCT18HOUJAC-HOUNCOLLINS12-4` | Nico Collins | 4.0 | 0.81 | 0.81 | 0.30 | -0.509 |
| `KXNFLRSHYDS-26OCT18HOUJAC-JACBTUTEN33-60` | Bhayshul Tuten | 60.0 | 0.56 | 0.56 | 0.06 | -0.500 |

_Ranked 417 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. David Montgomery (RB, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Tank Dell (WR, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLRSHATT-26OCT18HOUJAC-HOUCSTROUD7-1 moved +0.180 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.631 on KXNFLRSHYDS-26OCT18HOUJAC-JACBTUTEN33-40 (Bhayshul Tuten). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.599 on KXNFLRSHATT-26OCT18HOUJAC-JACBTUTEN33-14 (Bhayshul Tuten). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLRSHATT-26OCT18HOUJAC-HOUCSTROUD7-1 sits at a market price of 0.94 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_HOU_JAX.md`_


---

## BAL @ CLE — `2026_06_BAL_CLE`

- kickoff: 2026-10-18T17:00:00+00:00 (951 minutes away) · state **PREGAME**
- venue: Huntington Bank Field · roof outdoors · surface grass
- markets: 669 listed across 16 families — 330 supported, 282 no model, 48 rules unresolved, 9 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 9 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.11 | 2.86 |
| total | 40.14 | 40.26 |
| score | CLE 18.5 – BAL 21.6 | CLE 18.7 – BAL 21.6 |
| win prob CLE | 38.5% | 39.3% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.06 / total 19.92 · **2H** spread 1.86 / total 19.27 · **1Q** spread 0.59 / total 7.65 · **2Q** spread 0.87 / total 11.46 · **3Q** spread 0.35 / total 7.73 · **4Q** spread 0.43 / total 10.58

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 3.11 · total 40.14
- move `KXNFLSPREAD-26OCT18BALCLE-BAL11` -0.130
- move `KXNFLTEAMTOTAL-26OCT18BALCLE-BAL24` -0.130
- move `KXNFLSPREAD-26OCT18BALCLE-BAL14` -0.125
- move `KXNFLSPREAD-26OCT18BALCLE-BAL10` -0.125

**Game environment** (simulation, mean and middle 50%) — home margin -3.5 (-11.0–4.0) · total 41.7 (32.0–50.0) · P(one score) 54.3% · P(17+ blowout) 19.1% · P(total 10+ over centre) 23.7%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CLE | 61.1 (56.0–67.0) | 32.5 (28.0–37.0) | 21.7 (17.0–26.0) | 38.8 (33.0–44.0) | 0.636 (0.570–0.704) | 0.530 / 0.701 |
| BAL | 61.3 (56.0–67.0) | 27.6 (23.0–32.0) | 27.6 (23.0–32.0) | 32.7 (27.0–38.0) | 0.535 (0.467–0.603) | 0.458 / 0.627 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CLE | 00-0040784 | RB | 2.7 (0.0–4.0) | 8.2 (2.0–13.0) | 8.7% | 37.9% | HIGH |
| CLE | 00-0039373 | RB | 1.9 (0.0–3.0) | 8.3 (3.0–12.0) | 6.1% | 38.2% | HIGH |
| CLE | 00-0033537 | QB | 0.1 (0.0–0.0) | 6.3 (4.0–8.0) | 0.4% | 10.8% | HIGH |
| CLE | 00-0041037 | WR | 6.2 (3.0–8.0) | 0.0 (0.0–0.0) | 19.7% | 0.0% | HIGH |
| BAL | 00-0032764 | RB | 1.7 (0.0–3.0) | 20.6 (15.0–26.0) | 6.3% | 74.5% | MEDIUM |
| BAL | 00-0039064 | WR | 7.2 (4.0–10.0) | 0.5 (0.0–0.0) | 27.1% | 1.8% | MEDIUM |
| BAL | 00-0034975 | RB | 2.3 (1.0–3.0) | 3.6 (0.0–5.0) | 8.8% | 13.1% | HIGH |
| BAL | 00-0035993 | QB | 0.4 (0.0–0.0) | 5.0 (3.0–6.0) | 1.5% | 6.2% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 20 market(s), e.g. KXNFLPASSATT-26OCT18BALCLE-BALTHUNTLEY5-27, KXNFLPASSATT-26OCT18BALCLE-CLEDWATSON4-36
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 31 market(s), e.g. KXNFL2H-26OCT18BALCLE-CLE, KXNFLFIRSTTD-26OCT18BALCLE-BALDHENRY22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 19 market(s), e.g. KXNFLSPREAD-26OCT18BALCLE-CLE8, KXNFLSPREAD-26OCT18BALCLE-CLE7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLGAME-26OCT18BALCLE-BAL, KXNFLTEAMTOTAL-26OCT18BALCLE-BAL18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 228 market(s), e.g. KXNFL1H-26OCT18BALCLE-TIE, KXNFL1HFT-26OCT18BALCLE-TIECLE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 24 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT18BALCLE-CLE3, KXNFL2QTOTAL-26OCT18BALCLE-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.5%  _(final margin within one score (8 points) either way; total within 10 of the centre 40.1429 (median favourite-oriented margin +2, median total 40))_
2. favourite controls / normal scoring — 17.2%  _(BAL (favourite) wins by more than one score; total within 10 of the centre 40.1429 (median favourite-oriented margin +15, median total 41))_
3. competitive / high scoring — 12.1%  _(final margin within one score (8 points) either way; total 50.1429+ (centre 40.1429) (median favourite-oriented margin +1, median total 58))_
4. competitive / low scoring — 10.7%  _(final margin within one score (8 points) either way; total 30.1429 or fewer (centre 40.1429) (median favourite-oriented margin +2, median total 26))_
5. favourite controls / high scoring — 7.5%  _(BAL (favourite) wins by more than one score; total 50.1429+ (centre 40.1429) (median favourite-oriented margin +16, median total 57))_
   Other — 20.9%

Marginal events (overlapping): one_score 54.3% · blowout_17 19.1% · favorite_wins 63.6% · favorite_controls 32.1% · upset 36.3% · shootout 23.7% · low_scoring 20.3% · low_possession 17.6% · high_volume_passing 1.0% · run_heavy_control 15.6%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 8.80 mph, gusts 13.40, precip prob 0%, temp 58F, forecast retrieved 2026-10-18T00:37:37+00:00 (16.37 h before kickoff)._

**`KXNFLTD-26OCT18BALCLE-CLEIBOND0-1`** Isaiah Bond touchdowns 1
- MODEL / MARKET: football 8.1% · market 6.5% · reconciled 14.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.9% · failure mass 100.0% · win-contribution HHI 0.186

**`KXNFLTD-26OCT18BALCLE-BALDWALKER81-1`** Devontez Walker touchdowns 1
- MODEL / MARKET: football 8.5% · market 5.5% · reconciled 11.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.7% · failure mass 100.0% · win-contribution HHI 0.192

**`KXNFLTD-26OCT18BALCLE-CLEJMCLAUGHLIN38-1`** Jaleel McLaughlin touchdowns 1
- MODEL / MARKET: football 7.2% · market 30.5% · reconciled 25.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.6% · failure mass 100.0% · win-contribution HHI 0.188

**`KXNFLTD-26OCT18BALCLE-CLEAESTIME30-1`** Audric Estime touchdowns 1
- MODEL / MARKET: football 23.6% · market 9.5% · reconciled 13.6%
- SCRIPT ROBUSTNESS: P50 mass 4.1% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 12.3% · failure mass 95.9% · win-contribution HHI 0.188

_320 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 36 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (10)**

- Dillon Gabriel (QB, CLE) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Lamar Jackson (QB, BAL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Dylan Sampson (RB, CLE) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Matt Hibner (TE, BAL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Raheim Sanders (RB, CLE) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Cam Jurgens (C, BAL) — Out [high] — ruled out
- Teven Jenkins (G, CLE) — Out [high] — ruled out
- Broderick Washington Jr. (DT, BAL) — Out [single_source] — ruled out
- _...and 2 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (7)** — resolves at the inactive release, T−90m

- Ja'Kobi Lane (WR, BAL) — Questionable [high]
- Quinshon Judkins (RB, CLE) — Questionable [high]
- Andrew Vorhees (G, BAL) — Questionable [high]
- Emery Jones Jr. (OT, BAL) — Questionable [single_source]
- Carson Schwesinger (LB, CLE) — Questionable [high]
- Derek Barnett (DE, CLE) — Questionable [high]
- Mason Graham (DT, CLE) — Questionable [high]

### WEATHER

- Sunny · 57°F · wind 8 mph SW · precip 0%
- forecast vintage 2026-10-18T00:37:39+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 53 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tyler Huntley | BAL | attempts | 26.5 | 27.0 | 22.0 | 31.0 | 14.0 | 38.0 | 26.4 | 26.0 | 26.5 | 27.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Derrick Henry | BAL | carries | 20.6 | 20.0 | 15.0 | 26.0 | 8.0 | 34.0 | 21.1 | 21.0 | 20.6 | 20.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Huntley | BAL | carries | 5.0 | 4.0 | 3.0 | 6.0 | 1.0 | 12.0 | 5.2 | 5.0 | 5.0 | 4.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Huntley | BAL | completions | 17.6 | 18.0 | 14.0 | 21.0 | 9.0 | 27.0 | 17.4 | 17.0 | 17.6 | 18.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Huntley | BAL | passing_tds | 1.2 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.2 | 1.0 | 1.2 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Tyler Huntley | BAL | passing_yards | 199.1 | 194.0 | 148.0 | 245.0 | 86.0 | 330.0 | 166.7 | 158.0 | 166.7 | 162.0 | 0.00 | 0.97 | 9 | PRICED |
| Zay Flowers | BAL | receiving_yards | 65.1 | 56.0 | 29.0 | 92.0 | 0.0 | 156.0 | 64.8 | 56.0 | 64.8 | 56.0 | 0.00 | 0.97 | 11 | PRICED |
| Mark Andrews | BAL | receiving_yards | 38.6 | 31.0 | 14.0 | 55.0 | 0.0 | 102.0 | 33.4 | 27.0 | 33.4 | 27.0 | 0.00 | 0.98 | 9 | PRICED |

_8 of 53 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 53 of 83 listed player/stat groups simulated and exposed, 30 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT18BALCLE-CLEDWATSON4-4` | Deshaun Watson | 4.0 | 0.85 | 0.88 | 0.22 | -0.639 |
| `KXNFLREC-26OCT18BALCLE-CLEKCONCEPCION1-2` | KC Concepcion Jr. | 2.0 | 0.91 | 0.91 | 0.32 | -0.585 |
| `KXNFLREC-26OCT18BALCLE-CLEKCONCEPCION1-3` | KC Concepcion Jr. | 3.0 | 0.77 | 0.79 | 0.19 | -0.577 |
| `KXNFLRSHATT-26OCT18BALCLE-BALDHENRY22-18` | Derrick Henry | 18.0 | 0.71 | 0.73 | 0.14 | -0.576 |
| `KXNFLREC-26OCT18BALCLE-CLEDBOSTON12-2` | Denzel Boston | 2.0 | 0.85 | 0.87 | 0.32 | -0.530 |
| `KXNFLRECYDS-26OCT18BALCLE-CLEDBOSTON12-25` | Denzel Boston | 25.0 | 0.78 | 0.78 | 0.28 | -0.499 |

_Ranked 325 tradable markets; 5 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Lamar Jackson (QB, BAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Matt Hibner (TE, BAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Ja'Kobi Lane (WR), Quinshon Judkins (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLFFPTS-26OCT18BALCLE-BALDHENRY22-16P2 moved -0.205 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.639 on KXNFLRSHATT-26OCT18BALCLE-CLEDWATSON4-4 (Deshaun Watson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.585 on KXNFLREC-26OCT18BALCLE-CLEKCONCEPCION1-2 (KC Concepcion Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT18BALCLE-CLEKCONCEPCION1-2 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_BAL_CLE.md`_


---

## CAR @ PHI — `2026_06_CAR_PHI`

- kickoff: 2026-10-18T17:00:00+00:00 (951 minutes away) · state **PREGAME**
- venue: Lincoln Financial Field · roof outdoors · surface grass
- markets: 712 listed across 16 families — 364 supported, 289 no model, 48 rules unresolved, 11 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 11 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.15 | 3.06 |
| total | 39.55 | 39.19 |
| score | PHI 18.2 – CAR 21.3 | PHI 18.1 – CAR 21.1 |
| win prob PHI | 38.5% | 38.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.56 / total 19.23 · **2H** spread 1.73 / total 19.15 · **1Q** spread 0.77 / total 7.61 · **2Q** spread 1.60 / total 11.12 · **3Q** spread 0.19 / total 7.74 · **4Q** spread 1.01 / total 10.51

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 3.15 · total 39.55
- move `KXNFLTEAMTOTAL-26OCT18CARPHI-PHI18` -0.175
- move `KXNFLSPREAD-26OCT18CARPHI-CAR5` +0.170
- move `KXNFLTEAMTOTAL-26OCT18CARPHI-PHI22` -0.165
- move `KXNFLTEAMTOTAL-26OCT18CARPHI-PHI21` -0.160

**Game environment** (simulation, mean and middle 50%) — home margin -3.4 (-11.0–4.0) · total 40.5 (31.0–49.0) · P(one score) 53.7% · P(17+ blowout) 18.8% · P(total 10+ over centre) 23.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| PHI | 61.5 (56.0–67.0) | 33.5 (29.0–38.0) | 23.7 (19.0–28.0) | 37.2 (32.0–42.0) | 0.606 (0.541–0.672) | 0.500 / 0.670 |
| CAR | 63.3 (58.0–69.0) | 33.8 (29.0–39.0) | 25.0 (20.0–30.0) | 37.3 (32.0–42.0) | 0.591 (0.524–0.658) | 0.514 / 0.682 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| PHI | 00-0037258 | RB | 1.9 (0.0–3.0) | 17.5 (13.0–22.0) | 6.1% | 73.9% | MEDIUM |
| PHI | 00-0036912 | WR | 7.4 (4.0–10.0) | 0.1 (0.0–0.0) | 23.4% | 0.3% | MEDIUM |
| PHI | 00-0038393 | WR | 4.7 (2.0–7.0) | 0.3 (0.0–0.0) | 14.9% | 1.2% | HIGH |
| PHI | 00-0034351 | TE | 5.0 (2.0–7.0) | 0.0 (0.0–0.0) | 15.8% | 0.0% | HIGH |
| CAR | 00-0036555 | RB | 2.8 (1.0–4.0) | 22.9 (18.0–28.0) | 8.9% | 91.4% | LOW |
| CAR | 00-0040124 | WR | 7.9 (5.0–10.0) | 0.1 (0.0–0.0) | 25.0% | 0.3% | MEDIUM |
| CAR | 00-0039491 | WR | 5.0 (2.0–7.0) | 0.1 (0.0–0.0) | 16.0% | 0.4% | HIGH |
| CAR | 00-0031610 | TE | 4.0 (2.0–6.0) | 0.1 (0.0–0.0) | 12.8% | 0.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 1 market(s), e.g. KXNFLRSHYDS-26OCT18CARPHI-CARBYOUNG9-10
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 48 market(s), e.g. KXNFL1HFT-26OCT18CARPHI-CARCAR, KXNFL1HSPREAD-26OCT18CARPHI-CAR8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 20 market(s), e.g. KXNFLSPREAD-26OCT18CARPHI-PHI8, KXNFLSPREAD-26OCT18CARPHI-PHI7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLGAME-26OCT18CARPHI-CAR, KXNFLTOTAL-26OCT18CARPHI-34
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 242 market(s), e.g. KXNFL1H-26OCT18CARPHI-TIE, KXNFL1HFT-26OCT18CARPHI-PHICAR
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 18 market(s), e.g. KXNFL1HTOTAL-26OCT18CARPHI-4, KXNFL2HTOTAL-26OCT18CARPHI-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.5%  _(final margin within one score (8 points) either way; total within 10 of the centre 39.55 (median favourite-oriented margin +1, median total 39))_
2. favourite controls / normal scoring — 17.1%  _(CAR (favourite) wins by more than one score; total within 10 of the centre 39.55 (median favourite-oriented margin +15, median total 40))_
3. competitive / high scoring — 11.6%  _(final margin within one score (8 points) either way; total 49.55+ (centre 39.55) (median favourite-oriented margin +1, median total 57))_
4. competitive / low scoring — 10.6%  _(final margin within one score (8 points) either way; total 29.55 or fewer (centre 39.55) (median favourite-oriented margin +2, median total 25))_
5. underdog controls / normal scoring — 7.8%  _(PHI (underdog) wins by more than one score; total within 10 of the centre 39.55 (median favourite-oriented margin -16, median total 39))_
   Other — 21.5%

Marginal events (overlapping): one_score 53.7% · blowout_17 18.8% · favorite_wins 63.3% · favorite_controls 32.3% · upset 36.5% · shootout 23.1% · low_scoring 20.6% · low_possession 11.1% · high_volume_passing 7.6% · run_heavy_control 12.8%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 8.70 mph, gusts 13.90, precip prob 0%, temp 54F, forecast retrieved 2026-10-18T00:37:37+00:00 (16.37 h before kickoff)._

**`KXNFLTD-26OCT18CARPHI-CARJMETCHIE13-1`** John Metchie III touchdowns 1
- MODEL / MARKET: football 12.6% · market 7.5% · reconciled 19.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.6% · failure mass 100.0% · win-contribution HHI 0.185

**`KXNFLTD-26OCT18CARPHI-PHIDCOOPER80-1`** Darius Cooper touchdowns 1
- MODEL / MARKET: football 11.1% · market 6.5% · reconciled 15.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.9% · failure mass 100.0% · win-contribution HHI 0.183

**`KXNFLTD-26OCT18CARPHI-PHICSTEELE34-1`** Carson Steele touchdowns 1
- MODEL / MARKET: football 7.2% · market 6.5% · reconciled 14.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.8% · failure mass 100.0% · win-contribution HHI 0.180

**`KXNFLTD-26OCT18CARPHI-CARCHUBBARD30-2`** Chuba Hubbard touchdowns 2
- MODEL / MARKET: football 19.1% · market 13.5% · reconciled 15.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.0% · failure mass 100.0% · win-contribution HHI 0.212

_338 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 42 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (14)**

- Jalen Hurts (QB, PHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- AJ Dillon (RB, CAR) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Eli Stowers (TE, PHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Grant Calcaterra (TE, PHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jonathon Brooks (RB, CAR) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Saquon Barkley (RB, PHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Will Shipley (RB, PHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Ikem Ekwonu (OT, CAR) — Out [high] — ruled out
- _...and 6 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (8)** — resolves at the inactive release, T−90m

- Trevor Etienne (RB, CAR) — Questionable [high]
- Damien Lewis (G, CAR) — Questionable [high]
- Drew Kendall (C, PHI) — Questionable [high]
- Monroe Freeling (OT, CAR) — Doubtful [single_source]
- Taylor Moton (OT, CAR) — Questionable [high]
- AJ Epenesa (DE, PHI) — Doubtful [single_source]
- Jaelan Phillips (LB, CAR) — Questionable [high]
- Tershawn Wharton (DT, CAR) — Questionable [high]

### WEATHER

- Sunny · 54°F · wind 10 mph NE · precip 0%
- forecast vintage 2026-10-18T00:38:46+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 53 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bryce Young | CAR | attempts | 32.5 | 33.0 | 27.0 | 38.0 | 19.0 | 46.0 | 34.4 | 34.0 | 32.5 | 33.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chuba Hubbard | CAR | carries | 22.9 | 23.0 | 18.0 | 28.0 | 10.0 | 36.0 | 18.4 | 18.0 | 22.9 | 23.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | completions | 20.1 | 20.0 | 17.0 | 24.0 | 11.0 | 30.0 | 21.1 | 21.0 | 20.1 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Bryce Young | CAR | passing_yards | 232.6 | 228.0 | 178.0 | 283.0 | 109.0 | 372.0 | 240.8 | 235.0 | 240.8 | 236.0 | 0.00 | 0.97 | 10 | PRICED |
| Tetairoa McMillan | CAR | receiving_yards | 67.5 | 58.0 | 30.0 | 95.0 | 0.0 | 163.0 | 70.7 | 63.0 | 70.7 | 61.0 | 0.00 | 0.97 | 13 | PRICED |
| Jalen Coker | CAR | receiving_yards | 41.3 | 33.0 | 12.0 | 60.0 | 0.0 | 115.0 | 62.7 | 55.0 | 62.6 | 50.0 | 0.00 | 0.97 | 11 | PRICED |
| Darren Waller | CAR | receiving_yards | 30.9 | 22.0 | 7.0 | 46.0 | 0.0 | 94.0 | 29.9 | 24.0 | 29.9 | 22.0 | 0.00 | 0.97 | 8 | PRICED |

_8 of 53 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 53 of 90 listed player/stat groups simulated and exposed, 37 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26OCT18CARPHI-PHIDPIERCE39-30` | Dameon Pierce | 30.0 | 0.78 | 0.80 | 0.15 | -0.634 |
| `KXNFLPASSTDS-26OCT18CARPHI-PHIJHURTS1-1` | Jalen Hurts | 1.0 | 0.65 | 0.65 | 0.02 | -0.629 |
| `KXNFLRSHATT-26OCT18CARPHI-CARCHUBBARD30-16` | Chuba Hubbard | 16.0 | 0.68 | 0.69 | 0.09 | -0.595 |
| `KXNFLRSHYDS-26OCT18CARPHI-CARCHUBBARD30-40` | Chuba Hubbard | 40.0 | 0.82 | 0.84 | 0.23 | -0.592 |
| `KXNFLRSHYDS-26OCT18CARPHI-PHIDPIERCE39-40` | Dameon Pierce | 40.0 | 0.67 | 0.68 | 0.10 | -0.570 |
| `KXNFLRSHYDS-26OCT18CARPHI-CARCHUBBARD30-50` | Chuba Hubbard | 50.0 | 0.73 | 0.74 | 0.17 | -0.569 |

_Ranked 354 tradable markets; 10 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. AJ Dillon (RB, CAR) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jonathon Brooks (RB, CAR) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Trevor Etienne (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLFFPTS-26OCT18CARPHI-PHITMCKEE16-11P2 moved +0.405 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.634 on KXNFLRSHYDS-26OCT18CARPHI-PHIDPIERCE39-30 (Dameon Pierce). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.629 on KXNFLPASSTDS-26OCT18CARPHI-PHIJHURTS1-1 (Jalen Hurts). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRECYDS-26OCT18CARPHI-CARTMCMILLAN4-120 sits at a market price of 0.11 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_CAR_PHI.md`_


---

## CHI @ ATL — `2026_06_CHI_ATL`

- kickoff: 2026-10-18T17:00:00+00:00 (951 minutes away) · state **PREGAME**
- venue: Mercedes-Benz Stadium · roof  · surface fieldturf
- markets: 750 listed across 16 families — 405 supported, 289 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 0.25 | 0.87 |
| total | 53.25 | 52.15 |
| score | ATL 26.5 – CHI 26.8 | ATL 25.6 – CHI 26.5 |
| win prob ATL | 49.5% | 47.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 0.78 / total 25.43 · **2H** spread -0.06 / total 26.38 · **1Q** spread 0.05 / total 9.39 · **2Q** spread -0.18 / total 15.39 · **3Q** spread -0.42 / total 10.19 · **4Q** spread -0.37 / total 14.95

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 0.25 · total 53.25
- move `KXNFLTEAMTOTAL-26OCT18CHIATL-ATL25` +0.175
- move `KXNFL2QTOTAL-26OCT18CHIATL-18` +0.175
- move `KXNFLTOTAL-26OCT18CHIATL-39` +0.170
- move `KXNFLTOTAL-26OCT18CHIATL-42` +0.155

**Game environment** (simulation, mean and middle 50%) — home margin -0.5 (-8.0–7.0) · total 54.8 (46.0–63.0) · P(one score) 55.3% · P(17+ blowout) 17.8% · P(total 10+ over centre) 24.2%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| ATL | 63.1 (58.0–69.0) | 31.9 (27.0–37.0) | 26.8 (22.0–31.0) | 35.5 (30.0–40.0) | 0.564 (0.499–0.631) | 0.468 / 0.640 |
| CHI | 67.5 (62.0–73.0) | 34.4 (29.0–39.0) | 26.9 (22.0–32.0) | 39.8 (34.0–45.0) | 0.590 (0.525–0.657) | 0.502 / 0.674 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| ATL | 00-0038542 | RB | 5.4 (3.0–7.0) | 17.7 (12.0–23.0) | 17.7% | 66.1% | MEDIUM |
| ATL | 00-0037746 | RB | 1.2 (0.0–2.0) | 8.0 (3.0–11.0) | 3.9% | 29.8% | HIGH |
| ATL | 00-0037238 | WR | 8.5 (5.0–11.0) | 0.2 (0.0–0.0) | 27.8% | 0.7% | MEDIUM |
| ATL | 00-0036970 | TE | 4.6 (2.0–7.0) | 0.0 (0.0–0.0) | 15.1% | 0.0% | HIGH |
| CHI | 00-0036275 | RB | 2.9 (1.0–4.0) | 15.9 (10.0–21.0) | 8.8% | 59.1% | MEDIUM |
| CHI | 00-0040735 | WR | 5.9 (3.0–8.0) | 2.8 (0.0–4.0) | 18.3% | 10.3% | HIGH |
| CHI | 00-0039919 | WR | 6.6 (4.0–9.0) | 0.1 (0.0–0.0) | 20.4% | 0.3% | HIGH |
| CHI | 00-0039021 | RB | 1.9 (0.0–3.0) | 4.1 (1.0–6.0) | 5.8% | 15.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 10 market(s), e.g. KXNFLPASSATT-26OCT18CHIATL-CHICWILLIAMS18-38, KXNFLPASSCOMP-26OCT18CHIATL-CHICWILLIAMS18-25
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 110 market(s), e.g. KXNFL1H-26OCT18CHIATL-ATL, KXNFL1HSPREAD-26OCT18CHIATL-ATL8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT18CHIATL-CHI14, KXNFLSPREAD-26OCT18CHIATL-CHI10
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLTEAMTOTAL-26OCT18CHIATL-CHI22, KXNFLTEAMTOTAL-26OCT18CHIATL-ATL23
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 215 market(s), e.g. KXNFL1H-26OCT18CHIATL-TIE, KXNFL1HFT-26OCT18CHIATL-CHIATL
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 37 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT18CHIATL-CHI3, KXNFL1HTEAMTOTAL-26OCT18CHIATL-ATL3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.6%  _(final margin within one score (8 points) either way; total within 10 of the centre 53.25 (median favourite-oriented margin -0, median total 54))_
2. favourite controls / normal scoring — 13.2%  _(CHI (favourite) wins by more than one score; total within 10 of the centre 53.25 (median favourite-oriented margin +13, median total 55))_
3. competitive / high scoring — 12.8%  _(final margin within one score (8 points) either way; total 63.25+ (centre 53.25) (median favourite-oriented margin +1, median total 70))_
4. underdog controls / normal scoring — 11.1%  _(ATL (underdog) wins by more than one score; total within 10 of the centre 53.25 (median favourite-oriented margin -15, median total 52))_
5. competitive / low scoring — 10.9%  _(final margin within one score (8 points) either way; total 43.25 or fewer (centre 53.25) (median favourite-oriented margin +1, median total 39))_
   Other — 20.4%

Marginal events (overlapping): one_score 55.3% · blowout_17 17.8% · favorite_wins 52.3% · favorite_controls 24.0% · upset 47.3% · shootout 24.2% · low_scoring 20.0% · low_possession 3.0% · high_volume_passing 6.2% · run_heavy_control 18.4%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 13.70 mph, gusts 20.80, precip prob 0%, temp 60F, forecast retrieved 2026-10-18T00:37:37+00:00 (16.37 h before kickoff)._

**`KXNFLTD-26OCT18CHIATL-ATLOZACCHEAUS14-1`** Olamide Zaccheaus touchdowns 1
- MODEL / MARKET: football 9.4% · market 8.5% · reconciled 22.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.3% · failure mass 100.0% · win-contribution HHI 0.174

**`KXNFLTD-26OCT18CHIATL-ATLZBRANCH17-1`** Zachariah Branch touchdowns 1
- MODEL / MARKET: football 8.7% · market 8.5% · reconciled 22.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.3% · failure mass 100.0% · win-contribution HHI 0.177

**`KXNFLTD-26OCT18CHIATL-ATLCWOERNER89-1`** Charlie Woerner touchdowns 1
- MODEL / MARKET: football 6.8% · market 6.5% · reconciled 13.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.3% · failure mass 100.0% · win-contribution HHI 0.182

**`KXNFLTD-26OCT18CHIATL-ATLBROBINSON15-1`** Brian Robinson touchdowns 1
- MODEL / MARKET: football 35.4% · market 26.5% · reconciled 29.9%
- SCRIPT ROBUSTNESS: P50 mass 5.8% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 24.3% · failure mass 94.2% · win-contribution HHI 0.178
- THESIS DEPENDENCY with `KXNFLRSHATT-26OCT18CHIATL-ATLBROBINSON15-6`: cash correlation 0.316 · joint cash 27.9% · Jaccard of winning rows 0.428 · shared failure 34.7%

_395 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 43 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Kyle Monangai (RB, CHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Anthony Johnson Jr. (S, CHI) — Out [single_source] — ruled out
- C.J. Henderson (CB, ATL) — Out [high] — ruled out
- Dayo Odeyingbo (DE, CHI) — Injured Reserve [high] — ruled out
- Keyshaun Elliott (LB, CHI) — Out [high] — ruled out
- Montez Sweat (DE, CHI) — Suspension [high] — ruled out
- T.J. Edwards (LB, CHI) — Out [high] — ruled out
- Yasir Abdullah (LB, ATL) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Caleb Williams (QB, CHI) — Questionable [high]
- Kyler Gordon (CB, CHI) — Questionable [high]
- Tyrique Stevenson Sr. (CB, CHI) — Questionable [single_source]
- Za'Darius Smith (DE, ATL) — Questionable [high]

### WEATHER

- retractable roof (Mercedes-Benz Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Sunny · 60°F · wind 15 mph E · precip 0%
- forecast vintage 2026-10-18T00:37:38+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 61 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Michael Penix Jr. | ATL | attempts | 30.8 | 31.0 | 26.0 | 36.0 | 18.0 | 44.0 | 30.7 | 30.0 | 30.8 | 31.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bijan Robinson | ATL | carries | 17.7 | 17.0 | 12.0 | 23.0 | 5.0 | 31.0 | 18.9 | 18.0 | 17.7 | 17.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Brian Robinson | ATL | carries | 8.0 | 7.0 | 3.0 | 11.0 | 0.0 | 20.0 | 8.4 | 8.0 | 8.0 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | completions | 19.9 | 20.0 | 16.0 | 24.0 | 11.0 | 29.0 | 20.4 | 20.0 | 19.9 | 20.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | passing_tds | 1.6 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Michael Penix Jr. | ATL | passing_yards | 226.2 | 221.0 | 172.0 | 275.0 | 105.0 | 366.0 | 241.7 | 236.0 | 241.7 | 236.0 | 0.00 | 0.98 | 10 | PRICED |
| Drake London | ATL | receiving_yards | 76.3 | 67.0 | 36.0 | 106.0 | 4.0 | 178.0 | 96.3 | 88.0 | 95.9 | 85.0 | 0.00 | 0.98 | 15 | PRICED |
| Kyle Pitts Sr. | ATL | receiving_yards | 35.0 | 27.0 | 10.0 | 51.0 | 0.0 | 99.0 | 36.4 | 29.0 | 36.4 | 28.0 | 0.00 | 0.97 | 8 | PRICED |

_8 of 61 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 61 of 94 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT18CHIATL-ATLDLONDON5-5` | Drake London | 5.0 | 0.72 | 0.73 | 0.19 | -0.534 |
| `KXNFLRSHATT-26OCT18CHIATL-ATLBROBINSON7-16` | Bijan Robinson | 16.0 | 0.69 | 0.70 | 0.17 | -0.522 |
| `KXNFLREC-26OCT18CHIATL-ATLDLONDON5-4` | Drake London | 4.0 | 0.83 | 0.84 | 0.33 | -0.501 |
| `KXNFLREC-26OCT18CHIATL-ATLDLONDON5-6` | Drake London | 6.0 | 0.57 | 0.58 | 0.10 | -0.475 |
| `KXNFLRSHATT-26OCT18CHIATL-CHIDSWIFT4-15` | D'Andre Swift | 15.0 | 0.58 | 0.59 | 0.13 | -0.448 |
| `KXNFLRECYDS-26OCT18CHIATL-ATLDLONDON5-60` | Drake London | 60.0 | 0.78 | 0.78 | 0.33 | -0.444 |

_Ranked 399 tradable markets; 6 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Kyle Monangai (RB, CHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 1 skill players are Questionable (Caleb Williams (QB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLPASSCOMP-26OCT18CHIATL-CHICWILLIAMS18-15 moved +0.200 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.534 on KXNFLREC-26OCT18CHIATL-ATLDLONDON5-5 (Drake London). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.522 on KXNFLRSHATT-26OCT18CHIATL-ATLBROBINSON7-16 (Bijan Robinson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26OCT18CHIATL-CHILBURDEN10-2 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_CHI_ATL.md`_


---

## NO @ NYG — `2026_06_NO_NYG`

- kickoff: 2026-10-18T17:00:00+00:00 (951 minutes away) · state **PREGAME**
- venue: MetLife Stadium · roof outdoors · surface fieldturf
- markets: 717 listed across 16 families — 373 supported, 288 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -0.60 | 0.29 |
| total | 46.38 | 46.44 |
| score | NYG 23.5 – NO 22.9 | NYG 23.1 – NO 23.4 |
| win prob NYG | 50.5% | 48.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 0.26 / total 23.23 · **2H** spread 0.12 / total 23.35 · **1Q** spread -0.10 / total 8.22 · **2Q** spread 0.35 / total 13.64 · **3Q** spread -0.38 / total 8.79 · **4Q** spread -0.32 / total 13.57

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -0.60 · total 46.38
- move `KXNFLGAME-26OCT18NONYG-NYG` -0.145
- move `KXNFLGAME-26OCT18NONYG-NO` +0.140
- move `KXNFL4QTOTAL-26OCT18NONYG-18` +0.130
- move `KXNFL2QTOTAL-26OCT18NONYG-18` +0.120

**Game environment** (simulation, mean and middle 50%) — home margin 0.6 (-7.0–8.0) · total 47.7 (39.0–56.0) · P(one score) 55.1% · P(17+ blowout) 17.2% · P(total 10+ over centre) 24.0%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NYG | 64.3 (59.0–70.0) | 32.4 (27.0–37.0) | 27.3 (22.0–32.0) | 36.2 (31.0–41.0) | 0.564 (0.497–0.632) | 0.473 / 0.646 |
| NO | 63.9 (58.0–70.0) | 34.4 (29.0–39.0) | 25.0 (20.0–30.0) | 38.1 (33.0–43.0) | 0.598 (0.532–0.665) | 0.505 / 0.679 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NYG | 00-0040715 | RB | 3.1 (1.0–5.0) | 12.6 (7.0–17.0) | 10.0% | 46.3% | MEDIUM |
| NYG | 00-0039337 | WR | 9.2 (6.0–12.0) | 0.0 (0.0–0.0) | 29.2% | 0.1% | MEDIUM |
| NYG | 00-0037838 | TE | 6.9 (4.0–9.0) | 0.0 (0.0–0.0) | 22.0% | 0.2% | HIGH |
| NYG | 00-0036893 | RB | 0.9 (0.0–1.0) | 5.8 (2.0–9.0) | 3.0% | 21.4% | HIGH |
| NO | 00-0038551 | RB | 1.4 (0.0–2.0) | 10.6 (6.0–15.0) | 4.1% | 42.6% | MEDIUM |
| NO | 00-0033906 | RB | 2.8 (0.0–4.0) | 6.9 (1.0–11.0) | 8.4% | 27.8% | HIGH |
| NO | 00-0037239 | WR | 7.5 (3.0–11.0) | 0.1 (0.0–0.0) | 22.8% | 0.3% | HIGH |
| NO | 00-0039424 | WR | 6.7 (3.0–9.0) | 0.2 (0.0–0.0) | 20.3% | 0.7% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 7 market(s), e.g. KXNFLPASSCOMP-26OCT18NONYG-NYGJWINSTON19-25, KXNFLRSHYDS-26OCT18NONYG-NYGJWINSTON19-25
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 39 market(s), e.g. KXNFL2QTOTAL-26OCT18NONYG-21, KXNFL2QTOTAL-26OCT18NONYG-18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT18NONYG-NYG7, KXNFLSPREAD-26OCT18NONYG-NO7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTOTAL-26OCT18NONYG-43, KXNFLTOTAL-26OCT18NONYG-40
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 232 market(s), e.g. KXNFL1HFT-26OCT18NONYG-NONYG, KXNFL1HTEAMTOTAL-26OCT18NONYG-NYG21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 27 market(s), e.g. KXNFLREC-26OCT18NONYG-NOJJOHNSON83-2, KXNFLTEAMTOTAL-26OCT18NONYG-NO4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 30.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 46.375 (median favourite-oriented margin +1, median total 46))_
2. favourite controls / normal scoring — 13.2%  _(NYG (favourite) wins by more than one score; total within 10 of the centre 46.375 (median favourite-oriented margin +14, median total 46))_
3. competitive / high scoring — 13.2%  _(final margin within one score (8 points) either way; total 56.375+ (centre 46.375) (median favourite-oriented margin -1, median total 63))_
4. underdog controls / normal scoring — 12.2%  _(NO (underdog) wins by more than one score; total within 10 of the centre 46.375 (median favourite-oriented margin -12, median total 47))_
5. competitive / low scoring — 11.0%  _(final margin within one score (8 points) either way; total 36.375 or fewer (centre 46.375) (median favourite-oriented margin +1, median total 30))_
   Other — 19.5%

Marginal events (overlapping): one_score 55.1% · blowout_17 17.2% · favorite_wins 52.3% · favorite_controls 23.7% · upset 47.4% · shootout 24.0% · low_scoring 19.7% · low_possession 5.4% · high_volume_passing 6.8% · run_heavy_control 16.7%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.00 mph, gusts 7.60, precip prob 0%, temp 55F, forecast retrieved 2026-10-17T23:20:36+00:00 (17.66 h before kickoff)._

**`KXNFLTD-26OCT18NONYG-NYGJWINSTON19-1`** Jameis Winston touchdowns 1
- MODEL / MARKET: football 13.4% · market 8.5% · reconciled 23.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.8% · failure mass 100.0% · win-contribution HHI 0.186

**`KXNFLTD-26OCT18NONYG-NOCOLAVE12-1`** Chris Olave touchdowns 1
- MODEL / MARKET: football 27.3% · market 38.5% · reconciled 35.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 16.4% · failure mass 100.0% · win-contribution HHI 0.176
- THESIS DEPENDENCY with `KXNFLRECYDS-26OCT18NONYG-NOCOLAVE12-50`: cash correlation 0.305 · joint cash 21.0% · Jaccard of winning rows 0.360 · shared failure 41.6%

**`KXNFLTD-26OCT18NONYG-NYGJWINSTON19-2`** Jameis Winston touchdowns 2
- MODEL / MARKET: football 1.3% · market 0.5% · reconciled 3.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.4% · failure mass 100.0% · win-contribution HHI 0.191

**`KXNFLTD-26OCT18NONYG-NYGDSINGLETARY26-1`** Devin Singletary touchdowns 1
- MODEL / MARKET: football 18.5% · market 10.5% · reconciled 12.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 11.1% · failure mass 100.0% · win-contribution HHI 0.180

_361 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 41 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Braxton Berrios (WR, NYG) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jordyn Tyson (WR, NO) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Theo Johnson (TE, NYG) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Anfernee Jennings (LB, NO) — Out [high] — ruled out
- Chauncey Golston (DE, NYG) — Injured Reserve [high] — ruled out
- Colton Hood (CB, NYG) — Out [high] — ruled out
- Kaden Elliss (LB, NO) — Out [high] — ruled out
- Tyler Nubin (S, NYG) — Out [high] — ruled out

**Questionable / Doubtful (9)** — resolves at the inactive release, T−90m

- Alvin Kamara (RB, NO) — Questionable [high]
- Chris Olave (WR, NO) — Questionable [high]
- Andrew Thomas (OT, NYG) — Questionable [high]
- Jeremiah Wright (G, NO) — Questionable [high]
- Jermaine Eluemunor (OT, NYG) — Questionable [high]
- Abdul Carter (LB, NYG) — Questionable [high]
- Lorenzo Styles Jr. (S, NO) — Questionable [single_source]
- Nathan Shepherd (DT, NO) — Questionable [high]

### WEATHER

- Sunny · 60°F · wind 5 mph N · precip 0%
- forecast vintage 2026-10-18T00:37:45+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 59 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tyler Shough | NO | attempts | 33.1 | 33.0 | 28.0 | 39.0 | 20.0 | 46.0 | 35.6 | 35.0 | 33.1 | 33.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kendre Miller | NO | carries | 10.6 | 10.0 | 6.0 | 15.0 | 1.0 | 23.0 | 10.0 | 9.0 | 10.6 | 10.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Shough | NO | completions | 21.3 | 21.0 | 18.0 | 25.0 | 12.0 | 31.0 | 22.6 | 22.0 | 21.3 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Shough | NO | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Tyler Shough | NO | passing_yards | 223.6 | 219.0 | 172.0 | 271.0 | 106.0 | 359.0 | 234.0 | 228.0 | 234.0 | 229.0 | 0.00 | 0.98 | 10 | PRICED |
| Chris Olave | NO | receiving_yards | 61.8 | 53.0 | 10.0 | 96.0 | 0.0 | 166.0 | 84.7 | 77.0 | 84.2 | 73.0 | 0.00 | 0.78 | 14 | PRICED |
| Devaughn Vele | NO | receiving_yards | 48.9 | 40.0 | 18.0 | 70.0 | 0.0 | 129.0 | 48.3 | 41.0 | 48.3 | 39.0 | 0.00 | 0.98 | 10 | PRICED |
| Juwan Johnson | NO | receiving_yards | 44.5 | 37.0 | 16.0 | 64.0 | 0.0 | 117.0 | 46.1 | 39.0 | 46.1 | 38.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 59 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 59 of 92 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT18NONYG-NYGILIKELY9-3` | Isaiah Likely | 3.0 | 0.88 | 0.88 | 0.19 | -0.685 |
| `KXNFLREC-26OCT18NONYG-NYGILIKELY9-4` | Isaiah Likely | 4.0 | 0.76 | 0.76 | 0.11 | -0.642 |
| `KXNFLRECYDS-26OCT18NONYG-NYGILIKELY9-25` | Isaiah Likely | 25.0 | 0.81 | 0.82 | 0.18 | -0.636 |
| `KXNFLRECYDS-26OCT18NONYG-NYGILIKELY9-40` | Isaiah Likely | 40.0 | 0.65 | 0.66 | 0.08 | -0.573 |
| `KXNFLREC-26OCT18NONYG-NYGMNABERS1-4` | Malik Nabers | 4.0 | 0.81 | 0.82 | 0.25 | -0.562 |
| `KXNFLREC-26OCT18NONYG-NYGILIKELY9-5` | Isaiah Likely | 5.0 | 0.62 | 0.63 | 0.07 | -0.558 |

_Ranked 365 tradable markets; 8 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jordyn Tyson (WR, NO) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Theo Johnson (TE, NYG) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Alvin Kamara (RB), Chris Olave (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLGAME-26OCT18NONYG-NYG moved -0.145 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.685 on KXNFLREC-26OCT18NONYG-NYGILIKELY9-3 (Isaiah Likely). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.642 on KXNFLREC-26OCT18NONYG-NYGILIKELY9-4 (Isaiah Likely). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT18NONYG-NYGMNABERS1-3 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_NO_NYG.md`_


---

## NYJ @ NE — `2026_06_NYJ_NE`

- kickoff: 2026-10-18T17:00:00+00:00 (951 minutes away) · state **PREGAME**
- venue: Gillette Stadium · roof outdoors · surface fieldturf
- markets: 667 listed across 16 families — 338 supported, 273 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -7.14 | -6.88 |
| total | 43.50 | 42.76 |
| score | NE 25.3 – NYJ 18.2 | NE 24.8 – NYJ 17.9 |
| win prob NE | 75.5% | 75.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -4.00 / total 21.90 · **2H** spread -3.70 / total 21.50 · **1Q** spread -2.60 / total 7.94 · **2Q** spread -2.70 / total 13.04 · **3Q** spread -1.50 / total 8.24 · **4Q** spread -1.50 / total 9.59

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -7.14 · total 43.50
- move `KXNFLTOTAL-26OCT18NYJNE-42` -0.120

**Game environment** (simulation, mean and middle 50%) — home margin 7.7 (1.0–15.0) · total 44.6 (35.0–53.0) · P(one score) 45.8% · P(17+ blowout) 22.7% · P(total 10+ over centre) 23.4%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NE | 63.7 (58.0–69.0) | 30.7 (26.0–35.0) | 25.6 (20.0–30.0) | 37.1 (31.0–42.0) | 0.582 (0.514–0.651) | 0.515 / 0.688 |
| NYJ | 60.3 (55.0–66.0) | 31.8 (27.0–36.0) | 23.4 (19.0–28.0) | 36.4 (31.0–41.0) | 0.605 (0.541–0.670) | 0.483 / 0.657 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NE | 00-0036875 | RB | 3.9 (2.0–6.0) | 12.6 (7.0–17.0) | 13.4% | 49.2% | MEDIUM |
| NE | 00-0040734 | RB | 1.2 (0.0–2.0) | 6.0 (0.0–9.0) | 4.1% | 23.3% | HIGH |
| NE | 00-0039851 | QB | 0.2 (0.0–0.0) | 6.0 (4.0–8.0) | 0.5% | 5.2% | MEDIUM |
| NE | 00-0037816 | WR | 5.8 (3.0–8.0) | 0.1 (0.0–0.0) | 19.8% | 0.2% | HIGH |
| NYJ | 00-0039794 | RB | 3.1 (1.0–5.0) | 14.7 (10.0–19.0) | 10.1% | 62.6% | MEDIUM |
| NYJ | 00-0037740 | WR | 9.3 (6.0–12.0) | 0.0 (0.0–0.0) | 30.6% | 0.2% | MEDIUM |
| NYJ | 00-0036842 | RB | 0.3 (0.0–0.0) | 4.4 (1.0–6.0) | 0.9% | 18.7% | HIGH |
| NYJ | 00-0039451 | WR | 3.6 (1.0–5.0) | 0.6 (0.0–0.0) | 12.0% | 2.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 6 market(s), e.g. KXNFLPASSATT-26OCT18NYJNE-NEDMAYE10-31, KXNFLPASSCOMP-26OCT18NYJNE-NEDMAYE10-25
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 15 market(s), e.g. KXNFL1HSPREAD-26OCT18NYJNE-NYJ3, KXNFLFIRSTTD-26OCT18NYJNE-NERSTEVENSON38
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLGAME-26OCT18NYJNE-NYJ, KXNFLSPREAD-26OCT18NYJNE-NYJ6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLSPREAD-26OCT18NYJNE-NE4, KXNFLTEAMTOTAL-26OCT18NYJNE-NE22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 238 market(s), e.g. KXNFL1HSPREAD-26OCT18NYJNE-NYJ8, KXNFL1HSPREAD-26OCT18NYJNE-NYJ11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 26 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT18NYJNE-NYJ3, KXNFL1HTOTAL-26OCT18NYJNE-11

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 25.8%  _(NE (favourite) wins by more than one score; total within 10 of the centre 43.5 (median favourite-oriented margin +16, median total 43))_
2. competitive / normal scoring — 25.3%  _(final margin within one score (8 points) either way; total within 10 of the centre 43.5 (median favourite-oriented margin +3, median total 43))_
3. favourite controls / high scoring — 11.4%  _(NE (favourite) wins by more than one score; total 53.5+ (centre 43.5) (median favourite-oriented margin +17, median total 60))_
4. competitive / low scoring — 10.8%  _(final margin within one score (8 points) either way; total 33.5 or fewer (centre 43.5) (median favourite-oriented margin +3, median total 29))_
5. competitive / high scoring — 9.6%  _(final margin within one score (8 points) either way; total 53.5+ (centre 43.5) (median favourite-oriented margin +3, median total 63))_
   Other — 17.0%

Marginal events (overlapping): one_score 45.8% · blowout_17 22.7% · favorite_wins 75.7% · favorite_controls 45.6% · upset 24.1% · shootout 23.4% · low_scoring 20.6% · low_possession 13.0% · high_volume_passing 2.3% · run_heavy_control 14.9%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 3.80 mph, gusts 4.90, precip prob 0%, temp 51F, forecast retrieved 2026-10-18T00:37:37+00:00 (16.37 h before kickoff)._

**`KXNFLTD-26OCT18NYJNE-NYJTPATRICK17-1`** Tim Patrick touchdowns 1
- MODEL / MARKET: football 9.0% · market 8.5% · reconciled 22.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.8% · failure mass 100.0% · win-contribution HHI 0.173

**`KXNFLTD-26OCT18NYJNE-NYJIWILLIAMS18-1`** Isaiah Williams touchdowns 1
- MODEL / MARKET: football 13.7% · market 7.5% · reconciled 19.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.2% · failure mass 100.0% · win-contribution HHI 0.175

**`KXNFLTD-26OCT18NYJNE-NEKWILLIAMS18-1`** Kyle Williams touchdowns 1
- MODEL / MARKET: football 11.9% · market 7.5% · reconciled 18.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.2% · failure mass 100.0% · win-contribution HHI 0.195

**`KXNFLTD-26OCT18NYJNE-NEDDOUGLAS3-1`** DeMario Douglas touchdowns 1
- MODEL / MARKET: football 23.6% · market 12.5% · reconciled 15.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 13.4% · failure mass 100.0% · win-contribution HHI 0.190

_328 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 38 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Adonai Mitchell (WR, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Breece Hall (RB, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Dylan Parham (G, NYJ) — Out [high] — ruled out
- Marcus Bryant (OT, NE) — Injured Reserve [high] — ruled out
- Braiden McGregor (DE, NYJ) — Injured Reserve [high] — ruled out
- Carlton Davis III (CB, NE) — Out [single_source] — ruled out
- Joseph Ossai (DE, NYJ) — Out [high] — ruled out
- Karon Prunty (CB, NE) — Out [high] — ruled out

**Questionable / Doubtful (9)** — resolves at the inactive release, T−90m

- A.J. Brown (WR, NE) — Questionable [high]
- Kenyon Sadiq (TE, NYJ) — Questionable [high]
- Omar Cooper Jr. (WR, NYJ) — Questionable [single_source]
- TreVeyon Henderson (RB, NE) — Questionable [high]
- Will Campbell (OT, NE) — Questionable [single_source]
- Channing Canada (CB, NE) — Questionable [high]
- Christian Elliss (LB, NE) — Questionable [high]
- Craig Woodson (S, NE) — Questionable [high]

### WEATHER

- Sunny · 51°F · wind 3 mph N · precip 0%
- forecast vintage 2026-10-18T00:37:43+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 51 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Drake Maye | NE | attempts | 29.5 | 29.0 | 25.0 | 35.0 | 17.0 | 42.0 | 30.4 | 30.0 | 29.5 | 29.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Rhamondre Stevenson | NE | carries | 12.6 | 12.0 | 7.0 | 17.0 | 2.0 | 26.0 | 14.7 | 14.0 | 12.6 | 12.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Drake Maye | NE | carries | 6.0 | 5.0 | 4.0 | 8.0 | 2.0 | 12.0 | 6.1 | 6.0 | 6.0 | 5.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Drake Maye | NE | completions | 19.4 | 19.0 | 16.0 | 23.0 | 10.0 | 29.0 | 20.4 | 20.0 | 19.4 | 19.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Drake Maye | NE | passing_tds | 1.7 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.9 | 2.0 | 1.9 | 2.0 | 0.00 | 0.98 | 5 | PRICED |
| Drake Maye | NE | passing_yards | 224.1 | 219.0 | 170.0 | 274.0 | 104.0 | 361.0 | 241.2 | 235.0 | 241.2 | 236.0 | 0.00 | 0.98 | 10 | PRICED |
| Romeo Doubs | NE | receiving_yards | 51.9 | 43.0 | 18.0 | 75.0 | 0.0 | 137.0 | 37.6 | 29.0 | 37.6 | 31.0 | 0.00 | 0.97 | 9 | PRICED |
| Hunter Henry | NE | receiving_yards | 39.3 | 31.0 | 12.0 | 57.0 | 0.0 | 109.0 | 33.0 | 25.0 | 33.0 | 26.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 51 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 51 of 78 listed player/stat groups simulated and exposed, 27 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26OCT18NYJNE-NYJBALLEN0-40` | Braelon Allen | 40.0 | 0.79 | 0.81 | 0.13 | -0.657 |
| `KXNFLRSHATT-26OCT18NYJNE-NYJBALLEN0-14` | Braelon Allen | 14.0 | 0.74 | 0.76 | 0.10 | -0.644 |
| `KXNFLREC-26OCT18NYJNE-NYJGWILSON5-5` | Garrett Wilson | 5.0 | 0.75 | 0.76 | 0.14 | -0.610 |
| `KXNFLREC-26OCT18NYJNE-NYJGWILSON5-4` | Garrett Wilson | 4.0 | 0.85 | 0.86 | 0.26 | -0.598 |
| `KXNFLRSHYDS-26OCT18NYJNE-NYJBALLEN0-50` | Braelon Allen | 50.0 | 0.68 | 0.69 | 0.09 | -0.583 |
| `KXNFLREC-26OCT18NYJNE-NYJBALLEN0-2` | Braelon Allen | 2.0 | 0.73 | 0.74 | 0.21 | -0.528 |

_Ranked 320 tradable markets; 18 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Adonai Mitchell (WR, NYJ) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Breece Hall (RB, NYJ) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 4 skill players are Questionable (A.J. Brown (WR), TreVeyon Henderson (RB), Kenyon Sadiq (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLFFPTS-26OCT18NYJNE-NERSTEVENSON38-17P6 moved -0.245 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.657 on KXNFLRSHYDS-26OCT18NYJNE-NYJBALLEN0-40 (Braelon Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.644 on KXNFLRSHATT-26OCT18NYJNE-NYJBALLEN0-14 (Braelon Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRECYDS-26OCT18NYJNE-NYJBALLEN0-40 sits at a market price of 0.11 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_NYJ_NE.md`_


---

## PIT @ TB — `2026_06_PIT_TB`

- kickoff: 2026-10-18T17:00:00+00:00 (951 minutes away) · state **PREGAME**
- venue: Raymond James Stadium · roof outdoors · surface grass
- markets: 732 listed across 16 families — 374 supported, 300 no model, 48 rules unresolved, 10 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 10 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.56 | 2.31 |
| total | 39.29 | 39.01 |
| score | TB 18.4 – PIT 20.9 | TB 18.4 – PIT 20.7 |
| win prob TB | 43.5% | 41.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 1.47 / total 18.95 · **2H** spread 0.88 / total 18.92 · **1Q** spread 0.37 / total 7.58 · **2Q** spread 0.17 / total 11.11 · **3Q** spread -0.01 / total 7.61 · **4Q** spread -0.07 / total 10.45

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.56 · total 39.29
- move `KXNFLTOTAL-26OCT18PITTB-38` -0.135

**Game environment** (simulation, mean and middle 50%) — home margin -2.6 (-10.0–5.0) · total 40.8 (32.0–49.0) · P(one score) 53.6% · P(17+ blowout) 18.3% · P(total 10+ over centre) 23.7%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| TB | 61.8 (56.0–68.0) | 29.5 (25.0–34.0) | 24.0 (19.0–28.0) | 37.1 (32.0–42.0) | 0.602 (0.536–0.670) | 0.500 / 0.667 |
| PIT | 61.3 (56.0–67.0) | 34.6 (29.0–39.0) | 23.1 (18.0–28.0) | 37.3 (32.0–42.0) | 0.608 (0.542–0.676) | 0.528 / 0.698 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| TB | 00-0039361 | RB | 3.0 (1.0–4.0) | 15.4 (10.0–20.0) | 10.7% | 63.9% | MEDIUM |
| TB | 00-0036919 | RB | 3.5 (1.0–5.0) | 4.2 (1.0–6.0) | 12.4% | 17.4% | HIGH |
| TB | 00-0040129 | WR | 6.7 (4.0–9.0) | 0.4 (0.0–0.0) | 23.6% | 1.9% | HIGH |
| TB | 00-0041251 | QB | 0.5 (0.0–1.0) | 6.1 (4.0–8.0) | 1.7% | 1.7% | MEDIUM |
| PIT | 00-0037228 | RB | 6.3 (3.0–9.0) | 14.0 (9.0–19.0) | 19.1% | 60.4% | MEDIUM |
| PIT | 00-0036139 | RB | 2.7 (0.0–4.0) | 5.6 (0.0–9.0) | 8.3% | 24.1% | HIGH |
| PIT | 00-0035640 | WR | 6.7 (2.0–10.0) | 0.3 (0.0–0.0) | 20.6% | 1.5% | HIGH |
| PIT | 00-0041489 | WR | 5.9 (3.0–8.0) | 0.5 (0.0–0.0) | 18.0% | 2.1% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 21 market(s), e.g. KXNFLPASSATT-26OCT18PITTB-TBJDANIELS10-34, KXNFLPASSATT-26OCT18PITTB-TBJDANIELS10-29
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 47 market(s), e.g. KXNFL2QSPREAD-26OCT18PITTB-PIT4, KXNFL3QSPREAD-26OCT18PITTB-TB4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT18PITTB-TB7, KXNFLSPREAD-26OCT18PITTB-TB6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTEAMTOTAL-26OCT18PITTB-TB15, KXNFLTOTAL-26OCT18PITTB-35
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 242 market(s), e.g. KXNFL1H-26OCT18PITTB-TIE, KXNFL1HFT-26OCT18PITTB-TBPIT
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 22 market(s), e.g. KXNFL1HTOTAL-26OCT18PITTB-4, KXNFL2HTOTAL-26OCT18PITTB-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 32.2%  _(final margin within one score (8 points) either way; total within 10 of the centre 39.2857 (median favourite-oriented margin +1, median total 39))_
2. favourite controls / normal scoring — 16.0%  _(PIT (favourite) wins by more than one score; total within 10 of the centre 39.2857 (median favourite-oriented margin +15, median total 40))_
3. competitive / high scoring — 11.5%  _(final margin within one score (8 points) either way; total 49.2857+ (centre 39.2857) (median favourite-oriented margin +1, median total 56))_
4. competitive / low scoring — 9.9%  _(final margin within one score (8 points) either way; total 29.2857 or fewer (centre 39.2857) (median favourite-oriented margin +2, median total 25))_
5. underdog controls / normal scoring — 8.3%  _(TB (underdog) wins by more than one score; total within 10 of the centre 39.2857 (median favourite-oriented margin -16, median total 39))_
   Other — 22.1%

Marginal events (overlapping): one_score 53.6% · blowout_17 18.3% · favorite_wins 60.9% · favorite_controls 30.7% · upset 38.9% · shootout 23.7% · low_scoring 19.7% · low_possession 15.4% · high_volume_passing 3.4% · run_heavy_control 10.5%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 13.30 mph, gusts 22.40, precip prob 0%, temp 75F, forecast retrieved 2026-10-18T00:37:37+00:00 (16.37 h before kickoff)._

**`KXNFLTD-26OCT18PITTB-PITJWARREN30-2`** Jaylen Warren touchdowns 2
- MODEL / MARKET: football 15.1% · market 9.5% · reconciled 12.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 10.8% · failure mass 100.0% · win-contribution HHI 0.205

**`KXNFLTD-26OCT18PITTB-PITDMETCALF4-1`** DK Metcalf touchdowns 1
- MODEL / MARKET: football 24.9% · market 32.5% · reconciled 30.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 24.4% · failure mass 100.0% · win-contribution HHI 0.190
- THESIS DEPENDENCY with `KXNFLREC-26OCT18PITTB-PITDMETCALF4-4`: cash correlation 0.326 · joint cash 19.9% · Jaccard of winning rows 0.352 · shared failure 43.4%
- THESIS DEPENDENCY with `KXNFLRECYDS-26OCT18PITTB-PITDMETCALF4-50`: cash correlation 0.303 · joint cash 18.2% · Jaccard of winning rows 0.340 · shared failure 46.4%

**`KXNFLTD-26OCT18PITTB-TBSTUCKER44-1`** Sean Tucker touchdowns 1
- MODEL / MARKET: football 8.2% · market 15.5% · reconciled 14.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.2% · failure mass 100.0% · win-contribution HHI 0.179

**`KXNFLTD-26OCT18PITTB-PITEHEIDENREICH29-1`** Eli Heidenreich touchdowns 1
- MODEL / MARKET: football 0.0% · market 6.0% · reconciled 4.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.0% · failure mass 100.0% · win-contribution HHI --

_364 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 47 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Baker Mayfield (QB, TB) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Ben Skowronek (WR, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- David Sills V (WR, TB) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Michael Pittman Jr. (WR, PIT) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Roman Wilson (WR, PIT) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Antoine Winfield Jr. (S, TB) — Out [single_source] — ruled out
- DeShon Elliott (S, PIT) — Injured Reserve [high] — ruled out
- Derrick Harmon (DT, PIT) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (10)** — resolves at the inactive release, T−90m

- Pat Freiermuth (TE, PIT) — Questionable [high]
- Rico Dowdle (RB, PIT) — Questionable [high]
- Sean Tucker (RB, TB) — Questionable [high]
- Ayden Garnes (CB, TB) — Questionable [high]
- Benjamin Morrison (CB, TB) — Doubtful [high]
- Jalen Ramsey (CB, PIT) — Questionable [high]
- Jamel Dean (CB, PIT) — Questionable [high]
- Josiah Trotter (LB, TB) — Questionable [high]

### WEATHER

- Sunny · 77°F · wind 15 mph NE · precip 0%
- forecast vintage 2026-10-18T00:38:48+00:00 · material: **True**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 60 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Aaron Rodgers | PIT | attempts | 33.3 | 33.0 | 28.0 | 39.0 | 20.0 | 47.0 | 34.2 | 34.0 | 33.3 | 33.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jaylen Warren | PIT | carries | 14.0 | 13.0 | 9.0 | 19.0 | 3.0 | 27.0 | 14.6 | 14.0 | 14.0 | 13.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Rico Dowdle | PIT | carries | 5.6 | 4.0 | 0.0 | 9.0 | 0.0 | 17.0 | 6.5 | 6.0 | 5.6 | 4.0 | -- | 0.78 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Aaron Rodgers | PIT | completions | 21.8 | 22.0 | 18.0 | 26.0 | 12.0 | 32.0 | 21.6 | 21.0 | 21.8 | 22.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Aaron Rodgers | PIT | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Aaron Rodgers | PIT | passing_yards | 225.4 | 221.0 | 173.0 | 274.0 | 109.0 | 357.0 | 229.4 | 224.0 | 229.4 | 225.0 | 0.00 | 0.97 | 8 | PRICED |
| DK Metcalf | PIT | receiving_yards | 54.3 | 45.0 | 2.0 | 86.0 | 0.0 | 154.0 | 58.4 | 50.0 | 58.4 | 48.0 | 0.00 | 0.77 | 11 | PRICED |
| Germie Bernard | PIT | receiving_yards | 44.1 | 35.0 | 14.0 | 64.0 | 0.0 | 122.0 | 50.1 | 42.0 | 50.1 | 40.0 | 0.00 | 0.98 | 9 | PRICED |

_8 of 60 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 60 of 103 listed player/stat groups simulated and exposed, 43 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT18PITTB-PITGBERNARD17-2` | Germie Bernard | 2.0 | 0.90 | 0.90 | 0.31 | -0.585 |
| `KXNFLREC-26OCT18PITTB-PITGBERNARD17-3` | Germie Bernard | 3.0 | 0.76 | 0.77 | 0.18 | -0.577 |
| `KXNFLREC-26OCT18PITTB-PITPFREIERMUTH88-2` | Pat Freiermuth | 2.0 | 0.85 | 0.87 | 0.30 | -0.552 |
| `KXNFLREC-26OCT18PITTB-PITJWARREN30-2` | Jaylen Warren | 2.0 | 0.87 | 0.88 | 0.32 | -0.549 |
| `KXNFLRECYDS-26OCT18PITTB-PITJWARREN30-15` | Jaylen Warren | 15.0 | 0.74 | 0.75 | 0.20 | -0.541 |
| `KXNFLREC-26OCT18PITTB-PITJWARREN30-3` | Jaylen Warren | 3.0 | 0.72 | 0.73 | 0.19 | -0.536 |

_Ranked 365 tradable markets; 9 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Ben Skowronek (WR, PIT) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Michael Pittman Jr. (WR, PIT) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 3 skill players are Questionable (Pat Freiermuth (TE), Rico Dowdle (RB), Sean Tucker (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. Wind/precipitation is flagged material (15 mph, 0% precip). Is that already in the total, and does the forecast vintage (2026-10-18T00:38:48+00:00) predate the last big market move?
5. KXNFLRSHYDS-26OCT18PITTB-TBKGAINWELL1-20 moved +0.180 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
6. The model disagrees by -0.585 on KXNFLREC-26OCT18PITTB-PITGBERNARD17-2 (Germie Bernard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. The model disagrees by -0.577 on KXNFLREC-26OCT18PITTB-PITGBERNARD17-3 (Germie Bernard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
8. KXNFLREC-26OCT18PITTB-PITGBERNARD17-2 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_PIT_TB.md`_


---

## TEN @ IND — `2026_06_TEN_IND`

- kickoff: 2026-10-18T17:00:00+00:00 (951 minutes away) · state **PREGAME**
- venue: Lucas Oil Stadium · roof  · surface fieldturf
- markets: 749 listed across 16 families — 390 supported, 300 no model, 48 rules unresolved, 11 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 11 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -6.71 | -7.12 |
| total | 45.17 | 45.03 |
| score | IND 25.9 – TEN 19.2 | IND 26.1 – TEN 19.0 |
| win prob IND | 74.5% | 74.6% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -4.00 / total 22.48 · **2H** spread -3.08 / total 21.90 · **1Q** spread -2.63 / total 8.00 · **2Q** spread -2.78 / total 13.42 · **3Q** spread -0.77 / total 8.45 · **4Q** spread -1.32 / total 12.35

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -6.71 · total 45.17
- move `KXNFLGAME-26OCT18TENIND-IND` +0.095

**Game environment** (simulation, mean and middle 50%) — home margin 6.6 (-1.0–14.0) · total 46.5 (37.0–55.0) · P(one score) 48.4% · P(17+ blowout) 21.0% · P(total 10+ over centre) 22.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| IND | 63.1 (58.0–69.0) | 32.1 (27.0–37.0) | 26.8 (22.0–32.0) | 35.3 (30.0–41.0) | 0.559 (0.492–0.630) | 0.486 / 0.667 |
| TEN | 60.6 (55.0–66.0) | 32.0 (27.0–37.0) | 24.1 (19.0–29.0) | 36.0 (31.0–41.0) | 0.594 (0.530–0.660) | 0.476 / 0.653 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| IND | 00-0036223 | RB | 3.5 (1.0–5.0) | 16.0 (11.0–21.0) | 11.5% | 59.7% | MEDIUM |
| IND | 00-0038997 | WR | 6.8 (4.0–9.0) | 0.1 (0.0–0.0) | 22.3% | 0.5% | HIGH |
| IND | 00-0030279 | WR | 6.6 (4.0–9.0) | 0.1 (0.0–0.0) | 21.6% | 0.3% | HIGH |
| IND | 00-0040128 | TE | 5.3 (1.0–8.0) | 0.4 (0.0–0.0) | 17.2% | 1.6% | HIGH |
| TEN | 00-0035261 | RB | 1.8 (0.0–3.0) | 12.1 (7.0–16.0) | 6.1% | 50.2% | MEDIUM |
| TEN | 00-0036924 | RB | 2.1 (0.0–3.0) | 6.4 (2.0–9.0) | 7.0% | 26.6% | HIGH |
| TEN | 00-0041438 | WR | 6.2 (3.0–9.0) | 0.0 (0.0–0.0) | 20.6% | 0.1% | HIGH |
| TEN | 00-0038117 | WR | 5.5 (3.0–8.0) | 0.1 (0.0–0.0) | 18.1% | 0.6% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 17 market(s), e.g. KXNFLPASSATT-26OCT18TENIND-INDDJONES17-36, KXNFLPASSYDS-26OCT18TENIND-INDDJONES17-300
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 37 market(s), e.g. KXNFL4Q-26OCT18TENIND-TEN, KXNFLREC-26OCT18TENIND-TENTPOLLARD20-3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLGAME-26OCT18TENIND-TEN, KXNFLSPREAD-26OCT18TENIND-TEN7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLSPREAD-26OCT18TENIND-IND4, KXNFLSPREAD-26OCT18TENIND-IND3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 253 market(s), e.g. KXNFL1HSPREAD-26OCT18TENIND-TEN11, KXNFL1HSPREAD-26OCT18TENIND-TEN10
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 29 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT18TENIND-IND3, KXNFLPASSCOMP-26OCT18TENIND-TENCWARD1-15

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 26.8%  _(final margin within one score (8 points) either way; total within 10 of the centre 45.1667 (median favourite-oriented margin +3, median total 45))_
2. favourite controls / normal scoring — 24.3%  _(IND (favourite) wins by more than one score; total within 10 of the centre 45.1667 (median favourite-oriented margin +15, median total 45))_
3. competitive / low scoring — 11.2%  _(final margin within one score (8 points) either way; total 35.1667 or fewer (centre 45.1667) (median favourite-oriented margin +2, median total 31))_
4. competitive / high scoring — 10.4%  _(final margin within one score (8 points) either way; total 55.1667+ (centre 45.1667) (median favourite-oriented margin +3, median total 64))_
5. favourite controls / high scoring — 9.9%  _(IND (favourite) wins by more than one score; total 55.1667+ (centre 45.1667) (median favourite-oriented margin +16, median total 63))_
   Other — 17.3%

Marginal events (overlapping): one_score 48.4% · blowout_17 21.0% · favorite_wins 72.3% · favorite_controls 41.4% · upset 27.5% · shootout 22.8% · low_scoring 20.9% · low_possession 13.8% · high_volume_passing 3.5% · run_heavy_control 17.4%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 7.90 mph, gusts 13.90, precip prob 0%, temp 56F, forecast retrieved 2026-10-18T00:37:37+00:00 (16.37 h before kickoff)._

**`KXNFLTD-26OCT18TENIND-TENMCARTER35-1`** Michael Carter touchdowns 1
- MODEL / MARKET: football 20.9% · market 2.5% · reconciled 7.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 14.0% · failure mass 100.0% · win-contribution HHI 0.169

**`KXNFLTD-26OCT18TENIND-INDJTAYLOR28-1`** Jonathan Taylor touchdowns 1
- MODEL / MARKET: football 58.8% · market 69.5% · reconciled 66.2%
- SCRIPT ROBUSTNESS: P50 mass 81.1% · P55 mass 51.8% · P60 mass 51.8% · major-script floor 37.1% · failure mass 18.9% · win-contribution HHI 0.189

**`KXNFLTD-26OCT18TENIND-INDTWARREN84-1`** Tyler Warren touchdowns 1
- MODEL / MARKET: football 25.8% · market 36.5% · reconciled 34.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 16.1% · failure mass 100.0% · win-contribution HHI 0.185
- THESIS DEPENDENCY with `KXNFLREC-26OCT18TENIND-INDTWARREN84-4`: cash correlation 0.336 · joint cash 20.4% · Jaccard of winning rows 0.365 · shared failure 44.2%
- THESIS DEPENDENCY with `KXNFLRECYDS-26OCT18TENIND-INDTWARREN84-25`: cash correlation 0.320 · joint cash 21.1% · Jaccard of winning rows 0.355 · shared failure 40.5%

**`KXNFLTD-26OCT18TENIND-INDJTAYLOR28-2`** Jonathan Taylor touchdowns 2
- MODEL / MARKET: football 23.9% · market 31.5% · reconciled 29.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.0% · failure mass 100.0% · win-contribution HHI 0.217

_378 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 41 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- Alec Pierce (WR, IND) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Ashton Dulin (WR, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Arden Key (DE, IND) — Injured Reserve [high] — ruled out
- Jaylon Carlies (LB, IND) — Out [high] — ruled out
- Jordan Elliott (DT, TEN) — Out [high] — ruled out
- Kevin Winston Jr. (S, TEN) — Out [single_source] — ruled out

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Tyjae Spears (RB, TEN) — Questionable [high]
- Tyler Warren (TE, IND) — Questionable [high]

### WEATHER

- retractable roof (Lucas Oil Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Sunny · 57°F · wind 6 mph S · precip 0%
- forecast vintage 2026-10-18T00:37:41+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 61 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Daniel Jones | IND | attempts | 30.9 | 31.0 | 26.0 | 36.0 | 17.0 | 44.0 | 30.9 | 31.0 | 30.9 | 31.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jonathan Taylor | IND | carries | 16.0 | 16.0 | 11.0 | 21.0 | 4.0 | 29.0 | 21.4 | 20.0 | 16.0 | 16.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Daniel Jones | IND | completions | 20.9 | 21.0 | 17.0 | 25.0 | 11.0 | 31.0 | 21.5 | 21.0 | 20.9 | 21.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Daniel Jones | IND | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Daniel Jones | IND | passing_yards | 216.1 | 213.0 | 166.0 | 262.0 | 102.0 | 346.0 | 233.9 | 228.0 | 233.9 | 230.0 | 0.00 | 0.97 | 9 | PRICED |
| Josh Downs | IND | receiving_yards | 54.0 | 46.0 | 22.0 | 77.0 | 0.0 | 136.0 | 56.8 | 47.0 | 56.8 | 48.0 | 0.00 | 0.98 | 10 | PRICED |
| Keenan Allen | IND | receiving_yards | 49.2 | 42.0 | 20.0 | 70.0 | 0.0 | 125.0 | 48.7 | 42.0 | 48.7 | 41.0 | 0.00 | 0.97 | 9 | PRICED |
| Tyler Warren | IND | receiving_yards | 37.5 | 29.0 | 0.0 | 59.0 | 0.0 | 109.0 | 52.6 | 46.0 | 52.6 | 41.0 | 0.00 | 0.78 | 11 | PRICED |

_8 of 61 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 61 of 99 listed player/stat groups simulated and exposed, 38 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT18TENIND-TENCTATE14-3` | Carnell Tate | 3.0 | 0.81 | 0.83 | 0.18 | -0.631 |
| `KXNFLREC-26OCT18TENIND-INDTWARREN84-3` | Tyler Warren | 3.0 | 0.85 | 0.87 | 0.26 | -0.591 |
| `KXNFLREC-26OCT18TENIND-INDTWARREN84-4` | Tyler Warren | 4.0 | 0.71 | 0.73 | 0.15 | -0.563 |
| `KXNFLREC-26OCT18TENIND-TENCTATE14-4` | Carnell Tate | 4.0 | 0.66 | 0.67 | 0.11 | -0.550 |
| `KXNFLRECYDS-26OCT18TENIND-TENCTATE14-25` | Carnell Tate | 25.0 | 0.81 | 0.82 | 0.27 | -0.542 |
| `KXNFLRECYDS-26OCT18TENIND-TENCTATE14-40` | Carnell Tate | 40.0 | 0.65 | 0.66 | 0.15 | -0.496 |

_Ranked 376 tradable markets; 14 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Ashton Dulin (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Alec Pierce (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Tyler Warren (TE), Tyjae Spears (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLREC-26OCT18TENIND-INDKALLEN10-6 moved +0.145 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.631 on KXNFLREC-26OCT18TENIND-TENCTATE14-3 (Carnell Tate). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.591 on KXNFLREC-26OCT18TENIND-INDTWARREN84-3 (Tyler Warren). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT18TENIND-INDJDOWNS2-2 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_TEN_IND.md`_


---

## ARI @ LA — `2026_06_ARI_LA`

- kickoff: 2026-10-18T20:05:00+00:00 (1136 minutes away) · state **PREGAME**
- venue: SoFi Stadium · roof dome · surface matrixturf
- markets: 775 listed across 16 families — 427 supported, 292 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -12.30 | -11.62 |
| total | 51.89 | 52.33 |
| score | LA 32.1 – ARI 19.8 | LA 32.0 – ARI 20.4 |
| win prob LA | 87.5% | 83.6% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -6.94 / total 26.75 · **2H** spread -5.88 / total 25.00 · **1Q** spread -3.33 / total 9.75 · **2Q** spread -3.77 / total 15.65 · **3Q** spread -3.15 / total 10.31 · **4Q** spread -2.79 / total 14.35

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -12.30 · total 51.89
- move `KXNFLGAME-26OCT18ARILAR-LAR` +0.235
- move `KXNFLGAME-26OCT18ARILAR-ARI` -0.230
- move `KXNFL1HTEAMTOTAL-26OCT18ARILAR-LAR3` +0.205

**Game environment** (simulation, mean and middle 50%) — home margin 12.5 (5.0–20.0) · total 52.5 (43.0–61.0) · P(one score) 32.3% · P(17+ blowout) 35.9% · P(total 10+ over centre) 23.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| LA | 66.9 (61.0–72.0) | 35.5 (30.0–41.0) | 27.9 (22.0–33.0) | 37.7 (32.0–43.0) | 0.564 (0.496–0.634) | 0.512 / 0.707 |
| ARI | 62.5 (57.0–68.0) | 38.1 (33.0–43.0) | 20.1 (15.0–24.0) | 42.0 (37.0–47.0) | 0.674 (0.610–0.739) | 0.539 / 0.711 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| LA | 00-0037840 | RB | 3.7 (1.0–5.0) | 16.5 (11.0–22.0) | 10.7% | 59.1% | MEDIUM |
| LA | 00-0039075 | WR | 10.2 (6.0–13.0) | 1.4 (0.0–2.0) | 29.8% | 5.1% | MEDIUM |
| LA | 00-0039738 | RB | 1.4 (0.0–2.0) | 7.4 (3.0–11.0) | 4.2% | 26.5% | HIGH |
| LA | 00-0031381 | WR | 6.5 (3.0–9.0) | 0.1 (0.0–0.0) | 19.1% | 0.4% | HIGH |
| ARI | 00-0037263 | RB | 2.4 (0.0–4.0) | 10.4 (6.0–14.0) | 6.6% | 51.8% | MEDIUM |
| ARI | 00-0037744 | TE | 10.4 (7.0–14.0) | 0.0 (0.0–0.0) | 28.3% | 0.0% | MEDIUM |
| ARI | 00-0038559 | WR | 9.1 (5.0–12.0) | 0.1 (0.0–0.0) | 24.8% | 0.5% | MEDIUM |
| ARI | 00-0037157 | RB | 0.8 (0.0–1.0) | 5.7 (2.0–8.0) | 2.3% | 28.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 6 market(s), e.g. KXNFLRECYDS-26OCT18ARILAR-LARCPARKINSON84-15, KXNFLRECYDS-26OCT18ARILAR-LARCPARKINSON84-25
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 49 market(s), e.g. KXNFL3QSPREAD-26OCT18ARILAR-LAR8, KXNFLFFPTS-26OCT18ARILAR-ARIKBOURNE17-8P3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 15 market(s), e.g. KXNFLGAME-26OCT18ARILAR-ARI, KXNFLSPREAD-26OCT18ARILAR-LAR28
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLSPREAD-26OCT18ARILAR-LAR7, KXNFLSPREAD-26OCT18ARILAR-LAR8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 256 market(s), e.g. KXNFL1H-26OCT18ARILAR-TIE, KXNFL1HSPREAD-26OCT18ARILAR-ARI8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 37 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT18ARILAR-LAR7, KXNFL1HTOTAL-26OCT18ARILAR-11

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 37.2%  _(LA (favourite) wins by more than one score; total within 10 of the centre 51.8889 (median favourite-oriented margin +18, median total 51))_
2. competitive / normal scoring — 16.2%  _(final margin within one score (8 points) either way; total within 10 of the centre 51.8889 (median favourite-oriented margin +3, median total 52))_
3. favourite controls / high scoring — 14.5%  _(LA (favourite) wins by more than one score; total 61.8889+ (centre 51.8889) (median favourite-oriented margin +18, median total 69))_
4. favourite controls / low scoring — 12.4%  _(LA (favourite) wins by more than one score; total 41.8889 or fewer (centre 51.8889) (median favourite-oriented margin +17, median total 37))_
5. competitive / low scoring — 8.0%  _(final margin within one score (8 points) either way; total 41.8889 or fewer (centre 51.8889) (median favourite-oriented margin +3, median total 36))_
   Other — 11.6%

Marginal events (overlapping): one_score 32.3% · blowout_17 35.9% · favorite_wins 86.0% · favorite_controls 64.1% · upset 13.8% · shootout 23.1% · low_scoring 21.2% · low_possession 4.4% · high_volume_passing 25.4% · run_heavy_control 23.0%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 8.10 mph, gusts 9.20, precip prob 1%, temp 87F, forecast retrieved 2026-10-18T00:37:37+00:00 (19.46 h before kickoff)._

**`KXNFLTD-26OCT18ARILAR-ARIEHIGGINS84-1`** Elijah Higgins touchdowns 1
- MODEL / MARKET: football 9.6% · market 7.5% · reconciled 18.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.8% · failure mass 100.0% · win-contribution HHI 0.190

**`KXNFLTD-26OCT18ARILAR-LARKMUMPFIELD4-1`** Konata Mumpfield touchdowns 1
- MODEL / MARKET: football 9.2% · market 6.5% · reconciled 14.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.5% · failure mass 100.0% · win-contribution HHI 0.240

**`KXNFLTD-26OCT18ARILAR-LARDADAMS17-1`** Davante Adams touchdowns 1
- MODEL / MARKET: football 38.1% · market 52.5% · reconciled 48.5%
- SCRIPT ROBUSTNESS: P50 mass 14.5% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 31.2% · failure mass 85.5% · win-contribution HHI 0.235

**`KXNFLTD-26OCT18ARILAR-LARPNACUA12-1`** Puka Nacua touchdowns 1
- MODEL / MARKET: football 49.9% · market 57.5% · reconciled 54.9%
- SCRIPT ROBUSTNESS: P50 mass 59.7% · P55 mass 22.5% · P60 mass 14.5% · major-script floor 42.6% · failure mass 40.3% · win-contribution HHI 0.235

_400 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 42 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- James Conner (RB, ARI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jeremiyah Love (RB, ARI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Alaric Jackson (OT, LA) — Suspension [single_source] — ruled out
- Andrew Wingard (S, ARI) — Out [high] — ruled out
- Myles Garrett (DE, LA) — Injured Reserve [single_source] — ruled out
- Wydett Williams Jr. (S, ARI) — Out [single_source] — ruled out

**Questionable / Doubtful (7)** — resolves at the inactive release, T−90m

- Keagen Trost (OT, LA) — Questionable [single_source]
- Blake Gillikin (P, ARI) — Questionable [high]
- Budda Baker (S, ARI) — Questionable [high]
- Kam Curl (S, LA) — Questionable [single_source]
- Kitan Crawford (S, ARI) — Questionable [high]
- Trent McDuffie (CB, LA) — Questionable [single_source]
- Zaven Collins (LB, ARI) — Questionable [high]

### WEATHER

fixed-roof stadium (SoFi Stadium) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 62 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jacoby Brissett | ARI | attempts | 36.7 | 37.0 | 32.0 | 42.0 | 23.0 | 50.0 | 37.7 | 37.0 | 36.7 | 37.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Allgeier | ARI | carries | 10.4 | 10.0 | 6.0 | 14.0 | 2.0 | 21.0 | 13.4 | 13.0 | 10.4 | 10.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | ARI | completions | 22.1 | 22.0 | 18.0 | 26.0 | 13.0 | 32.0 | 23.6 | 23.0 | 22.1 | 22.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | ARI | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Jacoby Brissett | ARI | passing_yards | 222.5 | 219.0 | 172.0 | 269.0 | 108.0 | 350.0 | 239.5 | 233.0 | 239.5 | 236.0 | 0.00 | 0.98 | 9 | PRICED |
| Trey McBride | ARI | receiving_yards | 64.1 | 58.0 | 34.0 | 88.0 | 6.0 | 141.0 | 68.4 | 62.0 | 68.4 | 62.0 | 0.00 | 0.98 | 11 | PRICED |
| Michael Wilson | ARI | receiving_yards | 62.8 | 55.0 | 29.0 | 88.0 | 1.0 | 150.0 | 65.8 | 57.0 | 65.8 | 57.0 | 0.00 | 0.98 | 12 | PRICED |
| Kendrick Bourne | ARI | receiving_yards | 26.6 | 18.0 | 4.0 | 40.0 | 0.0 | 85.0 | 37.9 | 31.0 | 37.9 | 26.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 62 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 62 of 98 listed player/stat groups simulated and exposed, 36 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26OCT18ARILAR-ARIJLOVE4-40` | Jeremiyah Love | 40.0 | 0.56 | 0.61 | 0.00 | -0.558 |
| `KXNFLREC-26OCT18ARILAR-ARITMCBRIDE85-6` | Trey McBride | 6.0 | 0.70 | 0.71 | 0.16 | -0.545 |
| `KXNFLREC-26OCT18ARILAR-ARITMCBRIDE85-5` | Trey McBride | 5.0 | 0.81 | 0.81 | 0.28 | -0.529 |
| `KXNFLRSHATT-26OCT18ARILAR-ARITALLGEIER22-11` | Tyler Allgeier | 11.0 | 0.70 | 0.73 | 0.20 | -0.497 |
| `KXNFLREC-26OCT18ARILAR-ARITMCBRIDE85-7` | Trey McBride | 7.0 | 0.57 | 0.58 | 0.08 | -0.489 |
| `KXNFLREC-26OCT18ARILAR-LARKWILLIAMS23-2` | Kyren Williams | 2.0 | 0.78 | 0.78 | 0.31 | -0.464 |

_Ranked 414 tradable markets; 13 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jeremiyah Love (RB, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. James Conner (RB, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLRSHYDS-26OCT18ARILAR-ARITALLGEIER22-40 moved +0.470 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.558 on KXNFLRSHYDS-26OCT18ARILAR-ARIJLOVE4-40 (Jeremiyah Love). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.545 on KXNFLREC-26OCT18ARILAR-ARITMCBRIDE85-6 (Trey McBride). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26OCT18ARILAR-ARITMCBRIDE85-4 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_ARI_LA.md`_


---

## BUF @ LV — `2026_06_BUF_LV`

- kickoff: 2026-10-18T20:25:00+00:00 (1156 minutes away) · state **PREGAME**
- venue: Allegiant Stadium · roof dome · surface grass
- markets: 704 listed across 16 families — 358 supported, 290 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 4.67 | 4.70 |
| total | 53.88 | 54.08 |
| score | LV 24.6 – BUF 29.3 | LV 24.7 – BUF 29.4 |
| win prob LV | 32.5% | 33.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 3.19 / total 27.11 · **2H** spread 2.26 / total 27.32 · **1Q** spread 1.14 / total 10.16 · **2Q** spread 2.00 / total 15.94 · **3Q** spread 0.40 / total 10.42 · **4Q** spread 0.82 / total 15.00

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 4.67 · total 53.88
- move `KXNFL2QTOTAL-26OCT18BUFLV-4` +0.115
- move `KXNFL4QTOTAL-26OCT18BUFLV-22` +0.115
- move `KXNFL3QSPREAD-26OCT18BUFLV-LV4` +0.105
- move `KXNFL3QSPREAD-26OCT18BUFLV-LV3` +0.100

**Game environment** (simulation, mean and middle 50%) — home margin -4.3 (-12.0–3.0) · total 54.5 (45.0–62.0) · P(one score) 51.9% · P(17+ blowout) 19.6% · P(total 10+ over centre) 23.2%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| LV | 63.1 (57.0–69.0) | 36.8 (32.0–42.0) | 22.8 (18.0–27.0) | 39.7 (34.0–45.0) | 0.630 (0.565–0.698) | 0.525 / 0.691 |
| BUF | 63.3 (58.0–69.0) | 30.0 (25.0–35.0) | 26.7 (22.0–31.0) | 35.6 (30.0–41.0) | 0.563 (0.495–0.630) | 0.484 / 0.661 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| LV | 00-0040122 | RB | 5.2 (2.0–7.0) | 14.1 (9.0–19.0) | 14.7% | 61.8% | MEDIUM |
| LV | 00-0039338 | TE | 8.3 (5.0–11.0) | 0.0 (0.0–0.0) | 23.6% | 0.0% | MEDIUM |
| LV | 00-0038563 | WR | 5.6 (3.0–8.0) | 1.0 (0.0–1.0) | 15.8% | 4.6% | HIGH |
| LV | 00-0040878 | RB | 1.0 (0.0–1.0) | 3.6 (1.0–5.0) | 2.7% | 16.0% | HIGH |
| BUF | 00-0037248 | RB | 2.0 (0.0–3.0) | 18.5 (13.0–24.0) | 7.1% | 69.3% | MEDIUM |
| BUF | 00-0034857 | QB | 0.2 (0.0–0.0) | 7.7 (4.0–10.0) | 0.7% | 12.7% | HIGH |
| BUF | 00-0037261 | WR | 4.8 (2.0–7.0) | 0.1 (0.0–0.0) | 16.8% | 0.4% | HIGH |
| BUF | 00-0035537 | RB | 2.6 (1.0–4.0) | 1.9 (0.0–3.0) | 9.0% | 7.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 14 market(s), e.g. KXNFLPASSATT-26OCT18BUFLV-BUFJALLEN17-31, KXNFLPASSCOMP-26OCT18BUFLV-BUFJALLEN17-26
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 43 market(s), e.g. KXNFL3QSPREAD-26OCT18BUFLV-LV7, KXNFLPASSTDS-26OCT18BUFLV-BUFJALLEN17-3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26OCT18BUFLV-LV8, KXNFLSPREAD-26OCT18BUFLV-LV7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLGAME-26OCT18BUFLV-BUF, KXNFLSPREAD-26OCT18BUFLV-BUF3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 204 market(s), e.g. KXNFL1H-26OCT18BUFLV-TIE, KXNFL1HFT-26OCT18BUFLV-LVBUF
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 36 market(s), e.g. KXNFL1HTOTAL-26OCT18BUFLV-11, KXNFL2QTOTAL-26OCT18BUFLV-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 30.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 53.875 (median favourite-oriented margin +2, median total 53))_
2. favourite controls / normal scoring — 18.5%  _(BUF (favourite) wins by more than one score; total within 10 of the centre 53.875 (median favourite-oriented margin +16, median total 54))_
3. competitive / high scoring — 10.8%  _(final margin within one score (8 points) either way; total 63.875+ (centre 53.875) (median favourite-oriented margin +2, median total 71))_
4. competitive / low scoring — 10.2%  _(final margin within one score (8 points) either way; total 43.875 or fewer (centre 53.875) (median favourite-oriented margin +3, median total 39))_
5. favourite controls / high scoring — 8.2%  _(BUF (favourite) wins by more than one score; total 63.875+ (centre 53.875) (median favourite-oriented margin +16, median total 70))_
   Other — 21.4%

Marginal events (overlapping): one_score 51.9% · blowout_17 19.6% · favorite_wins 65.8% · favorite_controls 34.5% · upset 33.9% · shootout 23.2% · low_scoring 20.2% · low_possession 8.1% · high_volume_passing 7.2% · run_heavy_control 15.6%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 3.10 mph, gusts 4.00, precip prob 2%, temp 80F, forecast retrieved 2026-10-18T00:37:37+00:00 (19.79 h before kickoff)._

**`KXNFLTD-26OCT18BUFLV-LVCWHITE82-1`** Cody White touchdowns 1
- MODEL / MARKET: football 13.9% · market 11.0% · reconciled 22.1%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.6% · failure mass 100.0% · win-contribution HHI 0.175

**`KXNFLTD-26OCT18BUFLV-BUFJALLEN17-1`** Josh Allen touchdowns 1
- MODEL / MARKET: football 42.0% · market 58.5% · reconciled 54.2%
- SCRIPT ROBUSTNESS: P50 mass 37.5% · P55 mass 8.2% · P60 mass 0.0% · major-script floor 29.9% · failure mass 62.5% · win-contribution HHI 0.180

**`KXNFLTD-26OCT18BUFLV-LVBBOWERS89-1`** Brock Bowers touchdowns 1
- MODEL / MARKET: football 37.1% · market 49.5% · reconciled 46.2%
- SCRIPT ROBUSTNESS: P50 mass 15.0% · P55 mass 4.2% · P60 mass 0.0% · major-script floor 27.8% · failure mass 85.0% · win-contribution HHI 0.182
- THESIS DEPENDENCY with `KXNFLPASSTDS-26OCT18BUFLV-LVKCOUSINS8-2`: cash correlation 0.321 · joint cash 27.7% · Jaccard of winning rows 0.438 · shared failure 36.8%

**`KXNFLTD-26OCT18BUFLV-LVAJEANTY2-1`** Ashton Jeanty touchdowns 1
- MODEL / MARKET: football 45.2% · market 53.5% · reconciled 50.9%
- SCRIPT ROBUSTNESS: P50 mass 24.4% · P55 mass 22.3% · P60 mass 15.0% · major-script floor 32.8% · failure mass 75.6% · win-contribution HHI 0.178

_348 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 36 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (3)**

- Carter Runyon (TE, LV) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Dont'e Thornton Jr. (WR, LV) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Tonka Hemingway (DT, LV) — Out [high] — ruled out

**Questionable / Doubtful (7)** — resolves at the inactive release, T−90m

- DJ Moore (WR, BUF) — Questionable [high]
- Joshua Palmer (WR, BUF) — Questionable [high]
- Trey Zuhn III (C, LV) — Questionable [single_source]
- Dee Alford (CB, BUF) — Questionable [high]
- Ed Oliver (DT, BUF) — Questionable [high]
- T.J. Sanders (DT, BUF) — Questionable [high]
- Te'Cory Couch (CB, BUF) — Questionable [high]

### WEATHER

fixed-roof stadium (Allegiant Stadium) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 56 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Josh Allen | BUF | attempts | 28.9 | 29.0 | 24.0 | 34.0 | 16.0 | 41.0 | 30.7 | 30.0 | 28.9 | 29.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| James Cook III | BUF | carries | 18.5 | 18.0 | 13.0 | 24.0 | 6.0 | 32.0 | 18.6 | 18.0 | 18.5 | 18.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | carries | 7.7 | 7.0 | 4.0 | 10.0 | 2.0 | 17.0 | 7.5 | 7.0 | 7.7 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | completions | 19.2 | 19.0 | 16.0 | 23.0 | 10.0 | 28.0 | 20.7 | 20.0 | 19.2 | 19.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | passing_tds | 1.7 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.8 | 2.0 | 1.8 | 2.0 | 0.00 | 0.97 | 4 | PRICED |
| Josh Allen | BUF | passing_yards | 219.7 | 215.0 | 167.0 | 268.0 | 100.0 | 355.0 | 245.3 | 240.0 | 245.3 | 241.0 | 0.00 | 0.97 | 9 | PRICED |
| Dalton Kincaid | BUF | receiving_yards | 35.8 | 26.0 | 8.0 | 52.0 | 0.0 | 107.0 | 56.0 | 48.0 | 55.9 | 41.0 | 0.00 | 0.97 | 10 | PRICED |
| Ty Johnson | BUF | receiving_yards | 17.7 | 11.0 | 0.0 | 26.0 | 0.0 | 62.0 | 21.0 | 15.0 | 21.0 | 13.0 | 0.00 | 0.98 | 5 | PRICED |

_8 of 56 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 56 of 87 listed player/stat groups simulated and exposed, 31 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT18BUFLV-LVBBOWERS89-5` | Brock Bowers | 5.0 | 0.78 | 0.78 | 0.15 | -0.626 |
| `KXNFLREC-26OCT18BUFLV-LVBBOWERS89-6` | Brock Bowers | 6.0 | 0.67 | 0.67 | 0.08 | -0.589 |
| `KXNFLREC-26OCT18BUFLV-LVBBOWERS89-4` | Brock Bowers | 4.0 | 0.85 | 0.86 | 0.27 | -0.584 |
| `KXNFLRSHATT-26OCT18BUFLV-BUFJALLEN17-5` | Josh Allen | 5.0 | 0.83 | 0.86 | 0.27 | -0.561 |
| `KXNFLREC-26OCT18BUFLV-BUFDKINCAID86-3` | Dalton Kincaid | 3.0 | 0.78 | 0.79 | 0.22 | -0.560 |
| `KXNFLRECYDS-26OCT18BUFLV-LVBBOWERS89-40` | Brock Bowers | 40.0 | 0.86 | 0.87 | 0.32 | -0.545 |

_Ranked 353 tradable markets; 5 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Carter Runyon (TE, LV) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Dont'e Thornton Jr. (WR, LV) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (DJ Moore (WR), Joshua Palmer (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLPASSYDS-26OCT18BUFLV-BUFJALLEN17-250 moved +0.150 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.626 on KXNFLREC-26OCT18BUFLV-LVBBOWERS89-5 (Brock Bowers). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.589 on KXNFLREC-26OCT18BUFLV-LVBBOWERS89-6 (Brock Bowers). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT18BUFLV-BUFDKINCAID86-2 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_BUF_LV.md`_


---

## LAC @ KC — `2026_06_LAC_KC`

- kickoff: 2026-10-18T20:25:00+00:00 (1156 minutes away) · state **PREGAME**
- venue: GEHA Field at Arrowhead Stadium · roof outdoors · surface grass
- markets: 763 listed across 16 families — 399 supported, 308 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -7.44 | -7.89 |
| total | 41.88 | 40.70 |
| score | KC 24.7 – LAC 17.2 | KC 24.3 – LAC 16.4 |
| win prob KC | 78.5% | 78.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -4.20 / total 21.30 · **2H** spread -3.43 / total 20.04 · **1Q** spread -2.64 / total 7.81 · **2Q** spread -2.91 / total 12.68 · **3Q** spread -2.30 / total 7.91 · **4Q** spread -2.39 / total 10.91

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -7.44 · total 41.88
- move `KXNFLGAME-26OCT18LACKC-KC` +0.200
- move `KXNFL1HTEAMTOTAL-26OCT18LACKC-KC3` +0.130
- move `KXNFL2HTOTAL-26OCT18LACKC-4` +0.105
- move `KXNFLGAME-26OCT18LACKC-LAC` -0.105

**Game environment** (simulation, mean and middle 50%) — home margin 7.6 (1.0–15.0) · total 42.7 (33.0–51.0) · P(one score) 46.4% · P(17+ blowout) 22.6% · P(total 10+ over centre) 23.6%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| KC | 63.0 (57.0–69.0) | 32.0 (27.0–37.0) | 24.7 (20.0–29.0) | 37.2 (32.0–42.0) | 0.591 (0.524–0.660) | 0.527 / 0.702 |
| LAC | 61.1 (55.0–67.0) | 30.3 (26.0–35.0) | 24.3 (19.0–29.0) | 36.3 (31.0–41.0) | 0.595 (0.531–0.661) | 0.474 / 0.646 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| KC | 00-0038134 | RB | 5.1 (2.0–7.0) | 18.2 (13.0–23.0) | 17.0% | 73.7% | MEDIUM |
| KC | 00-0030506 | TE | 7.2 (4.0–10.0) | 0.0 (0.0–0.0) | 24.1% | 0.0% | MEDIUM |
| KC | 00-0039894 | WR | 6.9 (4.0–9.0) | 0.3 (0.0–0.0) | 22.9% | 1.1% | HIGH |
| KC | 00-0041013 | RB | 1.7 (0.0–3.0) | 2.8 (0.0–4.0) | 5.8% | 11.5% | HIGH |
| LAC | 00-0040666 | RB | 1.7 (0.0–3.0) | 12.1 (7.0–16.0) | 6.0% | 49.5% | MEDIUM |
| LAC | 00-0038454 | RB | 2.8 (1.0–4.0) | 5.4 (2.0–8.0) | 9.7% | 22.0% | HIGH |
| LAC | 00-0036355 | QB | 0.2 (0.0–0.0) | 5.6 (3.0–7.0) | 0.7% | 6.8% | HIGH |
| LAC | 00-0039391 | RB | 1.4 (0.0–2.0) | 4.2 (1.0–6.0) | 5.0% | 17.1% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 18 market(s), e.g. KXNFLPASSATT-26OCT18LACKC-KCPMAHOMES15-36, KXNFLPASSATT-26OCT18LACKC-KCPMAHOMES15-31
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 36 market(s), e.g. KXNFL2H-26OCT18LACKC-LAC, KXNFLFIRSTTD-26OCT18LACKC-KCKWALKER9
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 20 market(s), e.g. KXNFLGAME-26OCT18LACKC-LAC, KXNFLSPREAD-26OCT18LACKC-LAC4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLSPREAD-26OCT18LACKC-KC6, KXNFLSPREAD-26OCT18LACKC-KC5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 254 market(s), e.g. KXNFL1H-26OCT18LACKC-TIE, KXNFL1HFT-26OCT18LACKC-TIEKC
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 25 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT18LACKC-LAC3, KXNFL2HTOTAL-26OCT18LACKC-8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 25.8%  _(KC (favourite) wins by more than one score; total within 10 of the centre 41.875 (median favourite-oriented margin +16, median total 41))_
2. competitive / normal scoring — 25.5%  _(final margin within one score (8 points) either way; total within 10 of the centre 41.875 (median favourite-oriented margin +3, median total 41))_
3. favourite controls / high scoring — 11.0%  _(KC (favourite) wins by more than one score; total 51.875+ (centre 41.875) (median favourite-oriented margin +17, median total 59))_
4. competitive / low scoring — 10.7%  _(final margin within one score (8 points) either way; total 31.875 or fewer (centre 41.875) (median favourite-oriented margin +3, median total 27))_
5. competitive / high scoring — 10.2%  _(final margin within one score (8 points) either way; total 51.875+ (centre 41.875) (median favourite-oriented margin +3, median total 61))_
   Other — 16.9%

Marginal events (overlapping): one_score 46.4% · blowout_17 22.6% · favorite_wins 75.3% · favorite_controls 44.8% · upset 24.6% · shootout 23.6% · low_scoring 20.4% · low_possession 13.1% · high_volume_passing 1.9% · run_heavy_control 13.2%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 12.80 mph, gusts 19.50, precip prob 0%, temp 64F, forecast retrieved 2026-10-18T00:37:37+00:00 (19.79 h before kickoff)._

**`KXNFLTD-26OCT18LACKC-LACMVALDESSCANTLING13-1`** Marquez Valdes-Scantling touchdowns 1
- MODEL / MARKET: football 8.4% · market 6.5% · reconciled 14.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.9% · failure mass 100.0% · win-contribution HHI 0.176

**`KXNFLTD-26OCT18LACKC-KCBSMITH24-1`** Brashard Smith touchdowns 1
- MODEL / MARKET: football 10.2% · market 5.5% · reconciled 11.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.3% · failure mass 100.0% · win-contribution HHI 0.194

**`KXNFLTD-26OCT18LACKC-LACOHAMPTON8-1`** Omarion Hampton touchdowns 1
- MODEL / MARKET: football 31.0% · market 24.5% · reconciled 26.6%
- SCRIPT ROBUSTNESS: P50 mass 17.4% · P55 mass 7.2% · P60 mass 2.5% · major-script floor 19.8% · failure mass 82.6% · win-contribution HHI 0.177

**`KXNFLTD-26OCT18LACKC-KCKWALKER9-2`** Kenneth Walker III touchdowns 2
- MODEL / MARKET: football 23.7% · market 20.5% · reconciled 22.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.8% · failure mass 100.0% · win-contribution HHI 0.226

_389 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 45 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (10)**

- Rashee Rice (WR, KC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tre' Harris (WR, LAC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tyquan Thornton (WR, KC) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Joe Alt (OT, LAC) — Out [high] — ruled out
- Josh Simmons (OT, KC) — Out [high] — ruled out
- Kayode Awosika (G, LAC) — Out [high] — ruled out
- Alec Ingold (FB, LAC) — Injured Reserve [high] — ruled out
- Denzel Perryman (LB, LAC) — Injured Reserve [high] — ruled out
- _...and 2 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (7)** — resolves at the inactive release, T−90m

- Brenen Thompson (WR, LAC) — Questionable [high]
- KeAndre Lambert-Smith (WR, LAC) — Questionable [high]
- Daiyan Henley (LB, LAC) — Questionable [high]
- Dalvin Tomlinson (DT, LAC) — Questionable [high]
- Jamaree Caldwell (DT, LAC) — Questionable [high]
- L'Jarius Sneed (CB, KC) — Questionable [high]
- Rodney Shelley (CB, LAC) — Doubtful [high]

### WEATHER

- Sunny · 68°F · wind 12 mph S · precip 0%
- forecast vintage 2026-10-18T00:38:51+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 70 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Patrick Mahomes | KC | attempts | 30.7 | 31.0 | 26.0 | 36.0 | 18.0 | 44.0 | 30.5 | 30.0 | 30.7 | 31.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kenneth Walker III | KC | carries | 18.2 | 18.0 | 13.0 | 23.0 | 6.0 | 31.0 | 19.5 | 19.0 | 18.2 | 18.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | carries | 4.0 | 4.0 | 2.0 | 5.0 | 1.0 | 8.0 | 4.0 | 4.0 | 4.0 | 4.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | completions | 20.5 | 20.0 | 17.0 | 24.0 | 11.0 | 30.0 | 20.2 | 20.0 | 20.5 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | passing_tds | 1.6 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.7 | 1.0 | 1.7 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Patrick Mahomes | KC | passing_yards | 214.2 | 210.0 | 164.0 | 261.0 | 100.0 | 342.0 | 229.5 | 223.0 | 229.5 | 225.0 | 0.00 | 0.97 | 9 | PRICED |
| Travis Kelce | KC | receiving_yards | 58.5 | 51.0 | 26.0 | 82.0 | 0.0 | 140.0 | 58.6 | 51.0 | 58.6 | 51.0 | 0.00 | 0.97 | 13 | PRICED |
| Xavier Worthy | KC | receiving_yards | 55.6 | 47.0 | 23.0 | 79.0 | 0.0 | 139.0 | 54.9 | 47.0 | 54.9 | 46.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 70 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 70 of 104 listed player/stat groups simulated and exposed, 34 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT18LACKC-KCKWALKER9-16` | Kenneth Walker III | 16.0 | 0.75 | 0.76 | 0.12 | -0.634 |
| `KXNFLRSHYDS-26OCT18LACKC-KCKWALKER9-60` | Kenneth Walker III | 60.0 | 0.79 | 0.79 | 0.27 | -0.516 |
| `KXNFLRSHYDS-26OCT18LACKC-KCKWALKER9-70` | Kenneth Walker III | 70.0 | 0.70 | 0.71 | 0.20 | -0.504 |
| `KXNFLRSHATT-26OCT18LACKC-KCKWALKER9-19` | Kenneth Walker III | 19.0 | 0.55 | 0.57 | 0.06 | -0.494 |
| `KXNFLRSHYDS-26OCT18LACKC-KCKWALKER9-50` | Kenneth Walker III | 50.0 | 0.86 | 0.87 | 0.38 | -0.489 |
| `KXNFLREC-26OCT18LACKC-KCXWORTHY1-3` | Xavier Worthy | 3.0 | 0.80 | 0.81 | 0.31 | -0.485 |

_Ranked 392 tradable markets; 7 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Rashee Rice (WR, KC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Tyquan Thornton (WR, KC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Brenen Thompson (WR), KeAndre Lambert-Smith (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLGAME-26OCT18LACKC-KC moved +0.200 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.634 on KXNFLRSHATT-26OCT18LACKC-KCKWALKER9-16 (Kenneth Walker III). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.516 on KXNFLRSHYDS-26OCT18LACKC-KCKWALKER9-60 (Kenneth Walker III). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT18LACKC-KCXWORTHY1-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_LAC_KC.md`_


---

## DAL @ GB — `2026_06_DAL_GB`

- kickoff: 2026-10-19T00:20:00+00:00 (1391 minutes away) · state **PREGAME**
- venue: Lambeau Field · roof outdoors · surface grass
- markets: 778 listed across 16 families — 420 supported, 302 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -0.25 | -0.53 |
| total | 53.62 | 53.10 |
| score | GB 26.9 – DAL 26.7 | GB 26.8 – DAL 26.3 |
| win prob GB | 51.5% | 52.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -0.47 / total 26.75 · **2H** spread -0.18 / total 27.20 · **1Q** spread -0.16 / total 10.03 · **2Q** spread 0.23 / total 15.62 · **3Q** spread 0.29 / total 10.53 · **4Q** spread 0.37 / total 14.89

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -0.25 · total 53.62
- move `KXNFLTEAMTOTAL-26OCT18DALGB-DAL4` +0.125
- move `KXNFL4QTOTAL-26OCT18DALGB-22` +0.120
- move `KXNFLGAME-26OCT18DALGB-DAL` -0.105
- move `KXNFLGAME-26OCT18DALGB-GB` +0.100

**Game environment** (simulation, mean and middle 50%) — home margin 0.6 (-7.0–8.0) · total 54.7 (46.0–63.0) · P(one score) 54.2% · P(17+ blowout) 17.5% · P(total 10+ over centre) 23.4%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| GB | 62.3 (57.0–68.0) | 35.5 (30.0–40.0) | 23.4 (18.0–28.0) | 38.1 (33.0–43.0) | 0.612 (0.545–0.680) | 0.518 / 0.692 |
| DAL | 65.3 (60.0–71.0) | 36.8 (32.0–42.0) | 24.0 (19.0–29.0) | 40.5 (35.0–46.0) | 0.621 (0.555–0.688) | 0.525 / 0.702 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| GB | 00-0039811 | RB | 2.9 (1.0–4.0) | 10.5 (6.0–14.0) | 8.6% | 45.0% | MEDIUM |
| GB | 00-0038124 | WR | 8.1 (5.0–11.0) | 0.1 (0.0–0.0) | 23.6% | 0.4% | MEDIUM |
| GB | 00-0040667 | WR | 7.2 (4.0–10.0) | 0.3 (0.0–0.0) | 21.1% | 1.2% | HIGH |
| GB | 00-0038098 | RB | 3.0 (1.0–4.0) | 4.3 (1.0–6.0) | 8.7% | 18.2% | HIGH |
| DAL | 00-0036997 | RB | 3.4 (1.0–5.0) | 16.5 (11.0–21.0) | 9.6% | 68.5% | MEDIUM |
| DAL | 00-0036358 | WR | 8.1 (5.0–11.0) | 0.3 (0.0–0.0) | 22.8% | 1.1% | MEDIUM |
| DAL | 00-0037247 | WR | 7.2 (4.0–10.0) | 0.1 (0.0–0.0) | 20.2% | 0.3% | HIGH |
| DAL | 00-0038041 | TE | 4.7 (2.0–7.0) | 0.0 (0.0–0.0) | 13.1% | 0.1% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 11 market(s), e.g. KXNFLREC-26OCT18DALGB-DALKTURPIN9-3, KXNFLREC-26OCT18DALGB-DALKTURPIN9-2
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 31 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT18DALGB-DAL21, KXNFL1Q-26OCT18DALGB-GB
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT18DALGB-GB8, KXNFLSPREAD-26OCT18DALGB-GB7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTOTAL-26OCT18DALGB-50, KXNFLTOTAL-26OCT18DALGB-47
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 239 market(s), e.g. KXNFL1H-26OCT18DALGB-TIE, KXNFL1HFT-26OCT18DALGB-GBDAL
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 38 market(s), e.g. KXNFL1HTOTAL-26OCT18DALGB-4, KXNFL2HTOTAL-26OCT18DALGB-15

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 30.8%  _(final margin within one score (8 points) either way; total within 10 of the centre 53.625 (median favourite-oriented margin +1, median total 53))_
2. favourite controls / normal scoring — 13.9%  _(GB (favourite) wins by more than one score; total within 10 of the centre 53.625 (median favourite-oriented margin +14, median total 53))_
3. competitive / high scoring — 12.5%  _(final margin within one score (8 points) either way; total 63.625+ (centre 53.625) (median favourite-oriented margin -1, median total 71))_
4. underdog controls / normal scoring — 12.2%  _(DAL (underdog) wins by more than one score; total within 10 of the centre 53.625 (median favourite-oriented margin -12, median total 54))_
5. competitive / low scoring — 11.0%  _(final margin within one score (8 points) either way; total 43.625 or fewer (centre 53.625) (median favourite-oriented margin +1, median total 38))_
   Other — 19.7%

Marginal events (overlapping): one_score 54.2% · blowout_17 17.5% · favorite_wins 51.8% · favorite_controls 24.1% · upset 47.8% · shootout 23.4% · low_scoring 19.7% · low_possession 6.0% · high_volume_passing 19.6% · run_heavy_control 11.2%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 8.70 mph, gusts 18.80, precip prob 0%, temp 51F, forecast retrieved 2026-10-18T00:37:37+00:00 (23.71 h before kickoff)._

**`KXNFLTD-26OCT18DALGB-DALBSPANNFORD89-1`** Brevyn Spann-Ford touchdowns 1
- MODEL / MARKET: football 8.2% · market 7.5% · reconciled 17.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.4% · failure mass 100.0% · win-contribution HHI 0.175

**`KXNFLTD-26OCT18DALGB-GBKJOHNSON26-1`** Kaleb Johnson touchdowns 1
- MODEL / MARKET: football 18.0% · market 11.5% · reconciled 14.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 10.9% · failure mass 100.0% · win-contribution HHI 0.176

**`KXNFLTD-26OCT18DALGB-DALTGOODSON32-2`** Tyler Goodson touchdowns 2
- MODEL / MARKET: football 0.7% · market 0.5% · reconciled 2.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.2% · failure mass 100.0% · win-contribution HHI 0.187

**`KXNFLTD-26OCT18DALGB-DALJWILLIAMS33-1`** Javonte Williams touchdowns 1
- MODEL / MARKET: football 58.1% · market 63.5% · reconciled 61.8%
- SCRIPT ROBUSTNESS: P50 mass 71.2% · P55 mass 71.2% · P60 mass 34.1% · major-script floor 40.4% · failure mass 28.7% · win-contribution HHI 0.170

_410 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 41 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (10)**

- Josh Jacobs (RB, GB) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Skyy Moore (WR, GB) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Drew Shelton (OT, DAL) — Out [single_source] — ruled out
- Benjamin St-Juste (CB, GB) — Out [high] — ruled out
- Cobie Durant (CB, DAL) — Out [high] — ruled out
- DeMarvion Overshown (LB, DAL) — Out [high] — ruled out
- Javon Hargrave (DT, GB) — Injured Reserve [high] — ruled out
- Jonathan Ford (DT, GB) — Injured Reserve [high] — ruled out
- _...and 2 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (8)** — resolves at the inactive release, T−90m

- Savion Williams (WR, GB) — Questionable [high]
- Aaron Banks (G, GB) — Questionable [high]
- Jacob Monk (C, GB) — Questionable [high]
- Ameer Speed (CB, DAL) — Questionable [high]
- Anthony Campbell (DT, GB) — Questionable [high]
- Brandon Cisse (CB, GB) — Questionable [high]
- Joey Porter Jr. (CB, DAL) — Questionable [single_source]
- LT Overton (DT, DAL) — Questionable [high]

### WEATHER

- Clear · 56°F · wind 9 mph SSW · precip 0%
- forecast vintage 2026-10-18T00:38:55+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 67 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Dak Prescott | DAL | attempts | 35.3 | 36.0 | 30.0 | 41.0 | 21.0 | 50.0 | 36.3 | 36.0 | 35.3 | 36.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Javonte Williams | DAL | carries | 16.5 | 16.0 | 11.0 | 21.0 | 5.0 | 29.0 | 17.1 | 17.0 | 16.5 | 16.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | completions | 23.1 | 23.0 | 19.0 | 27.0 | 13.0 | 33.0 | 23.9 | 24.0 | 23.1 | 23.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | passing_tds | 1.8 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 1.9 | 2.0 | 1.9 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Dak Prescott | DAL | passing_yards | 250.5 | 247.0 | 195.0 | 303.0 | 123.0 | 392.0 | 277.5 | 274.0 | 277.5 | 273.0 | 0.00 | 0.97 | 9 | PRICED |
| CeeDee Lamb | DAL | receiving_yards | 66.3 | 58.0 | 30.0 | 93.0 | 0.0 | 159.0 | 86.4 | 79.0 | 86.2 | 75.0 | 0.00 | 0.98 | 14 | PRICED |
| George Pickens | DAL | receiving_yards | 59.8 | 50.0 | 24.0 | 86.0 | 0.0 | 151.0 | 74.9 | 67.0 | 74.8 | 63.0 | 0.00 | 0.98 | 13 | PRICED |
| Ryan Flournoy | DAL | receiving_yards | 33.2 | 24.0 | 8.0 | 49.0 | 0.0 | 100.0 | 37.1 | 30.0 | 37.1 | 27.0 | 0.00 | 0.98 | 8 | PRICED |

_8 of 67 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 67 of 107 listed player/stat groups simulated and exposed, 40 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT18DALGB-GBMGOLDEN0-3` | Matthew Golden | 3.0 | 0.85 | 0.86 | 0.23 | -0.617 |
| `KXNFLREC-26OCT18DALGB-GBMGOLDEN0-4` | Matthew Golden | 4.0 | 0.71 | 0.72 | 0.13 | -0.583 |
| `KXNFLRSHATT-26OCT18DALGB-GBMLLOYD32-9` | MarShawn Lloyd | 9.0 | 0.77 | 0.79 | 0.20 | -0.570 |
| `KXNFLREC-26OCT18DALGB-DALCLAMB88-5` | CeeDee Lamb | 5.0 | 0.73 | 0.75 | 0.18 | -0.558 |
| `KXNFLRECYDS-26OCT18DALGB-GBMGOLDEN0-40` | Matthew Golden | 40.0 | 0.76 | 0.76 | 0.20 | -0.552 |
| `KXNFLRSHATT-26OCT18DALGB-DALJWILLIAMS33-14` | Javonte Williams | 14.0 | 0.73 | 0.74 | 0.18 | -0.546 |

_Ranked 416 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Josh Jacobs (RB, GB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Skyy Moore (WR, GB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Savion Williams (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLREC-26OCT18DALGB-GBBMELTON16-2 moved -0.225 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.617 on KXNFLREC-26OCT18DALGB-GBMGOLDEN0-3 (Matthew Golden). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.583 on KXNFLREC-26OCT18DALGB-GBMGOLDEN0-4 (Matthew Golden). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT18DALGB-GBTKRAFT85-2 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_DAL_GB.md`_


---

## WAS @ SF — `2026_06_WAS_SF`

- kickoff: 2026-10-20T00:15:00+00:00 (2826 minutes away) · state **PREGAME**
- venue: Levi's Stadium · roof outdoors · surface grass
- markets: 702 listed across 16 families — 362 supported, 284 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -7.42 | -7.96 |
| total | 52.62 | 52.51 |
| score | SF 30.0 – WAS 22.6 | SF 30.2 – WAS 22.3 |
| win prob SF | 77.5% | 76.5% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -4.50 / total 26.10 · **2H** spread -3.60 / total 25.93 · **1Q** spread -2.87 / total 9.80 · **2Q** spread -3.04 / total 15.39 · **3Q** spread -2.56 / total 10.21 · **4Q** spread -1.16 / total 14.68

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -7.42 · total 52.62
- move `KXNFLGAME-26OCT19WASSF-SF` +0.165
- move `KXNFLGAME-26OCT19WASSF-WAS` -0.135

**Game environment** (simulation, mean and middle 50%) — home margin 7.5 (1.0–15.0) · total 53.7 (44.0–62.0) · P(one score) 45.9% · P(17+ blowout) 22.3% · P(total 10+ over centre) 23.4%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| SF | 63.8 (58.0–69.0) | 33.7 (29.0–39.0) | 24.8 (20.0–29.0) | 37.9 (32.0–43.0) | 0.595 (0.526–0.665) | 0.527 / 0.702 |
| WAS | 62.8 (57.0–69.0) | 30.7 (26.0–35.0) | 23.6 (19.0–28.0) | 38.7 (33.0–44.0) | 0.618 (0.553–0.684) | 0.498 / 0.672 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| SF | 00-0033280 | RB | 4.5 (2.0–6.0) | 12.4 (7.0–17.0) | 14.0% | 49.9% | MEDIUM |
| SF | 00-0031408 | WR | 6.6 (4.0–9.0) | 0.0 (0.0–0.0) | 20.3% | 0.2% | HIGH |
| SF | 00-0041052 | RB | 0.5 (0.0–0.0) | 6.0 (2.0–9.0) | 1.5% | 24.1% | HIGH |
| SF | 00-0035719 | WR | 4.2 (2.0–6.0) | 1.6 (0.0–2.0) | 13.0% | 6.4% | HIGH |
| WAS | 00-0037256 | RB | 1.8 (0.0–3.0) | 11.0 (6.0–15.0) | 6.4% | 46.7% | MEDIUM |
| WAS | 00-0039910 | QB | 0.0 (0.0–0.0) | 9.1 (6.0–11.0) | 0.0% | 10.5% | MEDIUM |
| WAS | 00-0033699 | RB | 1.5 (0.0–2.0) | 7.5 (3.0–11.0) | 5.2% | 31.8% | HIGH |
| WAS | 00-0035659 | WR | 5.3 (3.0–7.0) | 0.1 (0.0–0.0) | 18.2% | 0.2% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 17 market(s), e.g. KXNFLPASSATT-26OCT19WASSF-WASJDANIELS5-31, KXNFLPASSCOMP-26OCT19WASSF-WASJDANIELS5-19
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 41 market(s), e.g. KXNFL4QSPREAD-26OCT19WASSF-SF8, KXNFLFIRSTTD-26OCT19WASSF-SFCMCCAFFREY23
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLGAME-26OCT19WASSF-WAS, KXNFLSPREAD-26OCT19WASSF-WAS6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLSPREAD-26OCT19WASSF-SF5, KXNFLSPREAD-26OCT19WASSF-SF4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 222 market(s), e.g. KXNFL1HFT-26OCT19WASSF-TIESF, KXNFL1HSPREAD-26OCT19WASSF-WAS8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 51 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT19WASSF-SF7, KXNFL1HTOTAL-26OCT19WASSF-8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 26.0%  _(SF (favourite) wins by more than one score; total within 10 of the centre 52.625 (median favourite-oriented margin +16, median total 52))_
2. competitive / normal scoring — 25.4%  _(final margin within one score (8 points) either way; total within 10 of the centre 52.625 (median favourite-oriented margin +3, median total 52))_
3. favourite controls / high scoring — 11.3%  _(SF (favourite) wins by more than one score; total 62.625+ (centre 52.625) (median favourite-oriented margin +16, median total 70))_
4. competitive / low scoring — 10.9%  _(final margin within one score (8 points) either way; total 42.625 or fewer (centre 52.625) (median favourite-oriented margin +2, median total 38))_
5. competitive / high scoring — 9.5%  _(final margin within one score (8 points) either way; total 62.625+ (centre 52.625) (median favourite-oriented margin +2, median total 71))_
   Other — 16.8%

Marginal events (overlapping): one_score 45.9% · blowout_17 22.3% · favorite_wins 75.3% · favorite_controls 45.1% · upset 24.6% · shootout 23.4% · low_scoring 20.3% · low_possession 7.7% · high_volume_passing 3.9% · run_heavy_control 13.8%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 11.50 mph, gusts 9.40, precip prob 0%, temp 66F, forecast retrieved 2026-10-17T23:20:36+00:00 (48.91 h before kickoff)._

**`KXNFLTD-26OCT19WASSF-WASDBROWN6-1`** Dyami Brown touchdowns 1
- MODEL / MARKET: football 8.8% · market 7.5% · reconciled 22.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.6% · failure mass 100.0% · win-contribution HHI 0.172

**`KXNFLTD-26OCT19WASSF-SFCMCCAFFREY23-1`** Christian McCaffrey touchdowns 1
- MODEL / MARKET: football 56.2% · market 70.5% · reconciled 66.0%
- SCRIPT ROBUSTNESS: P50 mass 82.6% · P55 mass 46.9% · P60 mass 46.9% · major-script floor 38.5% · failure mass 17.4% · win-contribution HHI 0.192

**`KXNFLTD-26OCT19WASSF-SFMEVANS5-1`** Mike Evans touchdowns 1
- MODEL / MARKET: football 36.7% · market 53.5% · reconciled 49.4%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 23.8% · failure mass 100.0% · win-contribution HHI 0.189

**`KXNFLTD-26OCT19WASSF-SFGKITTLE85-1`** George Kittle touchdowns 1
- MODEL / MARKET: football 32.4% · market 45.5% · reconciled 42.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 22.7% · failure mass 100.0% · win-contribution HHI 0.185

_340 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261018T003825Z.sim-1.1.0.scripts_v2.json.gz); 36 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (14)**

- Marcus Mariota (QB, WAS) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Christian Kirk (WR, SF) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Deebo Samuel Sr. (WR, SF) — Out [single_source] — ruled out -- role redistributes to the depth chart behind him
- Demarcus Robinson (WR, SF) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jacory Croskey-Merritt (RB, WAS) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jeremy McNichols (RB, WAS) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Charles Omenihu (DE, WAS) — Out [high] — ruled out
- Dre Greenlaw (LB, SF) — Suspension [high] — ruled out
- _...and 6 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (11)** — resolves at the inactive release, T−90m

- Mike Evans (WR, SF) — Questionable [high]
- Stefon Diggs (WR, WAS) — Questionable [high]
- Lucas Patrick (G, WAS) — Questionable [high]
- Gracen Halton (DT, SF) — Questionable [high]
- Javon Kinlaw (DT, WAS) — Questionable [high]
- Mykel Williams (DE, SF) — Questionable [high]
- Nick Cross (S, WAS) — Questionable [high]
- Percy Butler (S, WAS) — Questionable [high]

### WEATHER

- Mostly Sunny · 63°F · wind 13 mph WNW · precip 6%
- forecast vintage 2026-10-18T00:38:56+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261018T003825Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 51 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Brock Purdy | SF | attempts | 32.4 | 33.0 | 27.0 | 38.0 | 18.0 | 46.0 | 30.6 | 30.0 | 32.4 | 33.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Christian McCaffrey | SF | carries | 12.4 | 12.0 | 7.0 | 17.0 | 2.0 | 25.0 | 14.6 | 14.0 | 12.4 | 12.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Brock Purdy | SF | carries | 5.2 | 5.0 | 3.0 | 7.0 | 1.0 | 11.0 | 4.6 | 4.0 | 5.2 | 5.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Brock Purdy | SF | completions | 21.4 | 21.0 | 18.0 | 25.0 | 12.0 | 31.0 | 22.1 | 21.0 | 21.4 | 21.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Brock Purdy | SF | passing_tds | 2.1 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.3 | 2.0 | 2.3 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Brock Purdy | SF | passing_yards | 249.7 | 246.0 | 192.0 | 303.0 | 118.0 | 396.0 | 251.2 | 246.0 | 251.2 | 247.0 | 0.00 | 0.97 | 9 | PRICED |
| Mike Evans | SF | receiving_yards | 60.1 | 50.0 | 23.0 | 87.0 | 0.0 | 152.0 | 77.0 | 70.0 | 76.8 | 64.0 | 0.00 | 0.98 | 13 | PRICED |
| George Kittle | SF | receiving_yards | 43.4 | 35.0 | 15.0 | 63.0 | 0.0 | 118.0 | 71.9 | 64.0 | 71.7 | 58.0 | 0.00 | 0.98 | 13 | PRICED |

_8 of 51 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 51 of 79 listed player/stat groups simulated and exposed, 28 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT19WASSF-SFGKITTLE85-4` | George Kittle | 4.0 | 0.74 | 0.79 | 0.21 | -0.531 |
| `KXNFLREC-26OCT19WASSF-SFGKITTLE85-3` | George Kittle | 3.0 | 0.85 | 0.89 | 0.37 | -0.482 |
| `KXNFLRSHYDS-26OCT19WASSF-WASJCROSKEYMERRITT22-40` | Jacory Croskey-Merritt | 40.0 | 0.48 | 0.51 | 0.00 | -0.477 |
| `KXNFLREC-26OCT19WASSF-SFGKITTLE85-5` | George Kittle | 5.0 | 0.59 | 0.63 | 0.11 | -0.476 |
| `KXNFLREC-26OCT19WASSF-SFCMCCAFFREY23-3` | Christian McCaffrey | 3.0 | 0.81 | 0.86 | 0.37 | -0.445 |
| `KXNFLREC-26OCT19WASSF-SFCMCCAFFREY23-4` | Christian McCaffrey | 4.0 | 0.65 | 0.69 | 0.21 | -0.437 |

_Ranked 312 tradable markets; 50 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Deebo Samuel Sr. (WR, SF) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Christian Kirk (WR, SF) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Mike Evans (WR), Stefon Diggs (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRSHYDS-26OCT19WASSF-WASRWHITE1-40 moved +0.460 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.531 on KXNFLREC-26OCT19WASSF-SFGKITTLE85-4 (George Kittle). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.482 on KXNFLREC-26OCT19WASSF-SFGKITTLE85-3 (George Kittle). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRSHYDS-26OCT19WASSF-WASRWHITE1-15 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_06_WAS_SF.md`_


---

## HOW TO USE THIS PACKET

1. Handicap each game independently. The model's ranked disagreements are an input, not a shortlist.
2. For any thesis you form, check **BEST EXPRESSIONS** before choosing a contract — the largest disagreement is rarely the best payout for the risk.
3. Check **CORRELATION GROUPS** before sizing more than one position in a game.
4. Record every serious decision, including passes, via the recommendation ledger (`scripts/handicap/validate_recommendations.py`, then commit to the `handicap-data` branch).