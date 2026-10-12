# NFL HANDICAP PACKET — 2026 Week 5

- run id: `20261012T012726Z`  ·  packet sha: `51a89285db586a252c99`
- built at: 2026-10-12T01:27:26.391626+00:00  (all timestamps UTC)
- ledger: `20261012T010506Z.shadow-0.4.0.observations.jsonl.gz`  ·  model: `shadow-0.4.0`
- context captures: ['20261012T004839Z', '20261012T010351Z']
- team-profile basis: **current_season**
- **REAL-MONEY STATUS: NOT VALIDATED -- this packet recommends nothing and authorises nothing**
- **SIMULATION FRESHNESS: SIM_CURRENT** — run `20261012T010506Z` (RUN_NFL_FROZEN_BUNDLE), lag 0.0m vs target <= 180.0m; the simulation priced this packet's own board

> This packet contains no recommendations. Every model-vs-market number is a *disagreement*, which is not an edge. The model has been shown redundant to the closing market on player props and behind it on game outcomes; it is here as structure and context, not as a superior forecast.

## SLATE SUMMARY

- games: **15**
- markets listed this slate: **11915**, model-supported: **484**
- ledger support states (all weeks): `{'UNSUPPORTED_MODEL': 11061, 'POST_KICKOFF_EXCLUDED': 56563, 'UNSUPPORTED_RULES': 4143, 'UNSUPPORTED_IDENTITY': 8, 'SUPPORTED': 920, 'UNSUPPORTED_GAME': 44}`

### FULL-BOARD COVERAGE

_RUN NFL examines every executable Kalshi contract for every requested unstarted NFL game. UNSUPPORTED_MODEL is a statement about one model, never a reason to hide a contract. Every listed contract terminates in exactly one analysis state, in one of four buckets: A validated model view, B coherent/Shadow research view, C manual handicap from the packet's own football and context data, D explicit PASS with a named reason._

| bucket | contracts | meaning |
|---|---|---|
| **A** | 484 | validated/production model view available |
| **B** | 9 | coherent / Shadow research model view available |
| **C** | 1267 | no automated pricing authority; handicap from the football and context data in this packet |
| **D** | 68 | cannot defensibly price -- explicit PASS / RESEARCH REQUIRED, with a reason |
| **-** | 10087 | outside the pregame window (kickoff has passed) |
| **!** | 0 | INVARIANT VIOLATION -- a listed contract with no analysis state |

- listed: **11915** · executable books: **10267**
- incumbent priced: **484** · coherent simulation: **0** · Shadow v2 research: **9**
- manual handicap required: **1267** · research required: **60**
- rules blocked: **0** · identity blocked: **8** · non-football: **0**
- post-kickoff (stale): **10087**
- **silently omitted: 0** — this must be 0.

| family / period | listed | executable | incumbent priced | coherent sim | shadow v2 | manual research | research required | rules blocked | identity blocked | non football | post kickoff | silently omitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLAYER_STAT/FULL | 5898 | 4850 | 407 | 0 | 0 | 42 | 0 | 0 | 8 | 0 | 5441 | 0 |
| FIRST_TD_TEAM/FULL | 461 | 284 | 0 | 0 | 0 | 50 | 0 | 0 | 0 | 0 | 411 | 0 |
| FIRST_TD_SCORER/FULL | 423 | 418 | 0 | 0 | 0 | 51 | 0 | 0 | 0 | 0 | 372 | 0 |
| TEAM_TOTAL/FULL | 410 | 402 | 27 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 383 | 0 |
| SPREAD/FULL | 407 | 407 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 382 | 0 |
| TEAM_TOTAL/1H | 333 | 333 | 0 | 0 | 0 | 22 | 0 | 0 | 0 | 0 | 311 | 0 |
| TEAM_STAT/FULL | 300 | 160 | 0 | 0 | 0 | 300 | 0 | 0 | 0 | 0 | 0 | 0 |
| TOTAL/FULL | 296 | 294 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 277 | 0 |
| SPREAD/1H | 260 | 260 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 245 | 0 |
| SPREAD/2H | 257 | 249 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 242 | 0 |
| GAME_PLAYER_LEADER/FULL | 225 | 61 | 0 | 0 | 0 | 225 | 0 | 0 | 0 | 0 | 0 | 0 |
| RACE_TO_N/FULL | 225 | 209 | 0 | 0 | 0 | 225 | 0 | 0 | 0 | 0 | 0 | 0 |
| TOTAL/2H | 205 | 197 | 0 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 191 | 0 |
| TOTAL/1H | 203 | 203 | 0 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 189 | 0 |
| SPREAD/4Q | 181 | 156 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 170 | 0 |
| SPREAD/2Q | 170 | 170 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 160 | 0 |
| SPREAD/1Q | 169 | 169 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 159 | 0 |
| SPREAD/3Q | 168 | 162 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 158 | 0 |
| TOTAL/2Q | 152 | 151 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 142 | 0 |
| TOTAL/1Q | 150 | 150 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 140 | 0 |
| TOTAL/3Q | 150 | 149 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 140 | 0 |
| TOTAL/4Q | 150 | 139 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 140 | 0 |
| HALF_FULL_RESULT/1H | 135 | 130 | 0 | 0 | 9 | 126 | 0 | 0 | 0 | 0 | 0 | 0 |
| WIN_MARGIN_BUCKET/FULL | 105 | 103 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 98 | 0 |
| BOTH_TEAMS_SCORE_N/FULL | 60 | 55 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 56 | 0 |
| GAME_EVENT/FULL | 60 | 50 | 0 | 0 | 0 | 0 | 60 | 0 | 0 | 0 | 0 | 0 |
| PERIOD_WINNER/1H | 45 | 45 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 42 | 0 |
| PERIOD_WINNER/1Q | 45 | 45 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 42 | 0 |
| PERIOD_WINNER/2H | 45 | 45 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 42 | 0 |
| PERIOD_WINNER/2Q | 45 | 45 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 42 | 0 |
| PERIOD_WINNER/3Q | 45 | 45 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 42 | 0 |
| PERIOD_WINNER/4Q | 45 | 44 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 42 | 0 |
| GAME_WINNER/FULL | 30 | 30 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 28 | 0 |
| BOTH_TEAMS_SCORE/1Q | 15 | 15 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/2Q | 15 | 15 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/3Q | 15 | 14 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/4Q | 15 | 11 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 0 |
| PLAYER_H2H/FULL | 2 | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |

_A Shadow v2 or coherent-simulation projection is RESEARCH. It is not validated, it is never mixed into the incumbent's probability or its disagreement ranking, and it reaches no recommendation, staking or preflight path._

**Skill players ruled OUT (40)**

- Camden Brown (WR, DAL) — Out · 2026_05_TB_DAL
- Baker Mayfield (QB, TB) — Out · 2026_05_TB_DAL
- CJ Williams (WR, JAX) — Out · 2026_05_PHI_JAX
- DeVonta Smith (WR, PHI) — Out · 2026_05_PHI_JAX
- Hollywood Brown (WR, PHI) — Out · 2026_05_PHI_JAX
- Saquon Barkley (RB, PHI) — Out · 2026_05_PHI_JAX
- Tank Bigsby (RB, PHI) — Injured Reserve · 2026_05_PHI_JAX
- Caleb Williams (QB, CHI) — Out · 2026_05_CHI_GB
- Kyle Monangai (RB, CHI) — Out · 2026_05_CHI_GB
- Chris Brooks (RB, GB) — Injured Reserve · 2026_05_CHI_GB
- Savion Williams (WR, GB) — Injured Reserve · 2026_05_CHI_GB
- Colbie Young (WR, CIN) — Out · 2026_05_CIN_MIA
- Jack Endries (TE, CIN) — Out · 2026_05_CIN_MIA
- Caleb Douglas (WR, MIA) — Out · 2026_05_CIN_MIA
- Justin Joly (TE, MIA) — Out · 2026_05_CIN_MIA

**New or changed since the previous capture (2)** — the most decision-relevant section on the page

- Justin Herbert (QB, LAC): **Active** (new record) · 2026_05_DEN_LAC
- Trey McBride (TE, ARI): **Active** (new record) · 2026_05_DET_ARI

**Largest market moves since first capture**

| ticker | game | family | move |
|---|---|---|---|
| `KXNFLWINMARGIN-26OCT11NYGWAS-TIE` | 2026_05_NYG_WAS | WIN_MARGIN_BUCKET | +0.990 |
| `KXNFL3QSPREAD-26OCT08TBDAL-TB11` | 2026_05_TB_DAL | SPREAD | +0.970 |
| `KXNFLREC-26OCT11NYGWAS-NYGMNABERS1-11` | 2026_05_NYG_WAS | PLAYER_STAT | +0.965 |
| `KXNFLREC-26OCT08TBDAL-DALGPICKENS3-9` | 2026_05_TB_DAL | PLAYER_STAT | +0.960 |
| `KXNFL3QSPREAD-26OCT08TBDAL-TB8` | 2026_05_TB_DAL | SPREAD | +0.955 |
| `KXNFLREC-26OCT11HOUTEN-HOUJNOEL13-5` | 2026_05_HOU_TEN | PLAYER_STAT | +0.955 |
| `KXNFLREC-26OCT11NYGWAS-NYGILIKELY9-10` | 2026_05_NYG_WAS | PLAYER_STAT | +0.955 |
| `KXNFLTD-26OCT11PHIJAC-JACPWASHINGTON11-2` | 2026_05_PHI_JAX | PLAYER_STAT | +0.950 |
| `KXNFLTD-26OCT11CHIGB-GBCWATSON9-2` | 2026_05_CHI_GB | PLAYER_STAT | +0.950 |
| `KXNFLRECYDS-26OCT11DETARI-ARIEHIGGINS84-50` | 2026_05_DET_ARI | PLAYER_STAT | +0.950 |

**Largest model/market disagreements** — DISAGREEMENT ONLY, REQUIRES HANDICAP

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRECYDS-26OCT11INDPIT-PITMPITTMAN11-25` | Michael Pittman Jr. | 25.0 | 0.60 | 0.62 | 0.01 | -0.587 |
| `KXNFLRSHATT-26OCT12BUFLAR-BUFJALLEN17-5` | Josh Allen | 5.0 | 0.86 | 0.88 | 0.28 | -0.577 |
| `KXNFLREC-26OCT12BUFLAR-BUFDKINCAID86-3` | Dalton Kincaid | 3.0 | 0.78 | 0.80 | 0.23 | -0.544 |
| `KXNFLREC-26OCT12BUFLAR-BUFDKINCAID86-2` | Dalton Kincaid | 2.0 | 0.94 | 0.94 | 0.40 | -0.538 |
| `KXNFLREC-26OCT12BUFLAR-BUFJPALMER5-2` | Joshua Palmer | 2.0 | 0.53 | 0.54 | 0.00 | -0.527 |
| `KXNFLRECYDS-26OCT12BUFLAR-BUFJPALMER5-20` | Joshua Palmer | 20.0 | 0.53 | 0.55 | 0.00 | -0.527 |
| `KXNFLREC-26OCT12BUFLAR-BUFDKINCAID86-4` | Dalton Kincaid | 4.0 | 0.65 | 0.65 | 0.13 | -0.514 |
| `KXNFLREC-26OCT11DETARI-ARIMHARRISON18-3` | Marvin Harrison Jr. | 3.0 | 0.51 | 0.52 | 0.00 | -0.502 |
| `KXNFLREC-26OCT11DETARI-ARIMHARRISON18-2` | Marvin Harrison Jr. | 2.0 | 0.51 | 0.51 | 0.00 | -0.501 |
| `KXNFLRECYDS-26OCT12BUFLAR-BUFDKINCAID86-40` | Dalton Kincaid | 40.0 | 0.65 | 0.65 | 0.18 | -0.469 |
| `KXNFLRSHATT-26OCT12BUFLAR-BUFJCOOK4-15` | James Cook III | 15.0 | 0.68 | 0.70 | 0.21 | -0.465 |
| `KXNFLRECYDS-26OCT12BUFLAR-BUFDKINCAID86-25` | Dalton Kincaid | 25.0 | 0.81 | 0.82 | 0.35 | -0.462 |

**Highest-liquidity markets**

- `KXNFLGAME-26OCT08TBDAL-DAL` (GAME_WINNER, 2026_05_TB_DAL): volume 31106664, OI 18411291
- `KXNFLGAME-26OCT08TBDAL-TB` (GAME_WINNER, 2026_05_TB_DAL): volume 27398901, OI 12320751
- `KXNFLGAME-26OCT11SFSEA-SF` (GAME_WINNER, 2026_05_SF_SEA): volume 23798973, OI 14656673
- `KXNFLGAME-26OCT11PHIJAC-PHI` (GAME_WINNER, 2026_05_PHI_JAX): volume 23192822, OI 10766755
- `KXNFLGAME-26OCT11NYGWAS-NYG` (GAME_WINNER, 2026_05_NYG_WAS): volume 18321985, OI 6373084
- `KXNFLGAME-26OCT11DENLAC-LAC` (GAME_WINNER, 2026_05_DEN_LAC): volume 14731093, OI 6514703
- `KXNFLGAME-26OCT11CLENYJ-CLE` (GAME_WINNER, 2026_05_CLE_NYJ): volume 13815322, OI 7316115
- `KXNFLGAME-26OCT11BALATL-BAL` (GAME_WINNER, 2026_05_BAL_ATL): volume 13746046, OI 11328109

**BLOCKING data issues**

- 2026_05_TB_DAL: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_PHI_JAX: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_CHI_GB: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_CIN_MIA: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_CLE_NYJ: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_HOU_TEN: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_IND_PIT: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_LV_NE: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_MIN_NO: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_NYG_WAS: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_DEN_LAC: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_DET_ARI: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_SF_SEA: `GAME_STARTED` — kickoff has passed; this is not a pregame packet
- 2026_05_BAL_ATL: `GAME_STARTED` — kickoff has passed; this is not a pregame packet

### GAME PRIORITY FOR HANDICAP

_Priority ranks where deeper review may be most useful. It is NOT a bet ranking and carries no expectation that these games contain value._

| # | game | score | why |
|---|---|---|---|
| 1 | 2026_05_DEN_LAC | 12.0 | 1 new/changed injury records; 6 skill players ruled out (role change); largest market move 0.945; raw incumbent disagreement 0.239 (NOT scored: unvalidated); BLOCKING data issue -- review before trusting anything here |
| 2 | 2026_05_BAL_ATL | 11.0 | 6 skill players ruled out (role change); forecast changed; largest market move 0.855; BLOCKING data issue -- review before trusting anything here |
| 3 | 2026_05_DET_ARI | 10.5 | 1 new/changed injury records; 3 skill players ruled out (role change); largest market move 0.950; raw incumbent disagreement 0.502 (NOT scored: unvalidated); BLOCKING data issue -- review before trusting anything here |
| 4 | 2026_05_PHI_JAX | 10.0 | 5 skill players ruled out (role change); largest market move 0.950; BLOCKING data issue -- review before trusting anything here |
| 5 | 2026_05_CHI_GB | 10.0 | 4 skill players ruled out (role change); largest market move 0.950; BLOCKING data issue -- review before trusting anything here |
| 6 | 2026_05_CIN_MIA | 10.0 | 5 skill players ruled out (role change); largest market move 0.945; BLOCKING data issue -- review before trusting anything here |
| 7 | 2026_05_CLE_NYJ | 10.0 | 6 skill players ruled out (role change); largest market move 0.885; BLOCKING data issue -- review before trusting anything here |
| 8 | 2026_05_HOU_TEN | 10.0 | 5 skill players ruled out (role change); largest market move 0.955; BLOCKING data issue -- review before trusting anything here |
| 9 | 2026_05_IND_PIT | 10.0 | 9 skill players ruled out (role change); largest market move 0.935; raw incumbent disagreement 0.587 (NOT scored: unvalidated); BLOCKING data issue -- review before trusting anything here |
| 10 | 2026_05_LV_NE | 10.0 | 7 skill players ruled out (role change); largest market move 0.945; BLOCKING data issue -- review before trusting anything here |
| 11 | 2026_05_MIN_NO | 10.0 | 5 skill players ruled out (role change); largest market move 0.890; raw incumbent disagreement 0.254 (NOT scored: unvalidated); BLOCKING data issue -- review before trusting anything here |
| 12 | 2026_05_NYG_WAS | 10.0 | 7 skill players ruled out (role change); largest market move 0.990; BLOCKING data issue -- review before trusting anything here |
| 13 | 2026_05_SF_SEA | 10.0 | 7 skill players ruled out (role change); largest market move 0.950; BLOCKING data issue -- review before trusting anything here |
| 14 | 2026_05_BUF_LA | 8.5 | 2 skill players ruled out (role change); largest market move 0.140; raw incumbent disagreement 0.577 (NOT scored: unvalidated); 357 supported player-prop rungs |
| 15 | 2026_05_TB_DAL | 7.0 | 2 skill players ruled out (role change); largest market move 0.970; raw incumbent disagreement 0.281 (NOT scored: unvalidated); BLOCKING data issue -- review before trusting anything here |

> Each game below is summarised. Full detail -- complete market board, every player ladder, all best-expression groups -- is in that game's own file under `games/`.


---

## TB @ DAL — `2026_05_TB_DAL`

- kickoff: 2026-10-09T00:15:00+00:00 (-4392 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 863 listed across 17 families — 2 supported, 26 no model, 50 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 863/863 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 50 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.33 | -- |
| total | 46.73 | -- |
| score | DAL 22.2 – TB 24.5 | DAL -- – TB -- |
| win prob DAL | 28.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -3.00 / total 16.50 · **2H** spread 5.93 / total 30.70 · **1Q** spread -7.00 / total 7.50 · **2Q** spread 5.00 / total 9.50 · **3Q** spread 16.00 / total 16.50 · **4Q** spread -- / total 12.68

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.33 · total 46.73
- move `KXNFL3QSPREAD-26OCT08TBDAL-TB11` +0.970
- move `KXNFL3QSPREAD-26OCT08TBDAL-TB8` +0.955

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (7; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 19 market(s), e.g. KXNFLMOSTRECYDS-26OCT08TBDAL-DALRFLOURNOY19, KXNFLMOSTRSHYDS-26OCT08TBDAL-DALTGOODSON32
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 6 market(s), e.g. KXNFLGAME-26OCT08TBDAL-DAL, KXNFLSPREAD-26OCT08TBDAL-DAL3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLTEAMTOTAL-26OCT08TBDAL-DAL18, KXNFLTOTAL-26OCT08TBDAL-46
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 48 market(s), e.g. KXNFLLONGREC-26OCT08TBDAL-TBTHURST17-17, KXNFLRECYDS-26OCT08TBDAL-TBTHURST17-80
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 16 market(s), e.g. KXNFLRECYDS-26OCT08TBDAL-DALGPICKENS3-130, KXNFL2H-26OCT08TBDAL-TB
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 18 market(s), e.g. KXNFLLONGREC-26OCT08TBDAL-TBTHURST17-17, KXNFLRECYDS-26OCT08TBDAL-TBTHURST17-80

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (15)**

- Baker Mayfield (QB, TB) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Camden Brown (WR, DAL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Ajani Cornelius (OT, DAL) — Out [high] — ruled out
- Billy Schrauth (G, TB) — Out [high] — ruled out
- Drew Shelton (OT, DAL) — Out [single_source] — ruled out
- Luke Haggard (G, TB) — Out [single_source] — ruled out
- Antoine Winfield Jr. (S, TB) — Out [single_source] — ruled out
- Benjamin Morrison (CB, TB) — Out [high] — ruled out
- _...and 7 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- CeeDee Lamb (WR, DAL) — Questionable [high]
- Tyler Guyton (OT, DAL) — Questionable [high]
- Alijah Clark (S, DAL) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 110 listed player/stat groups simulated and exposed, 110 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTD-26OCT08TBDAL-DALJWILLIAMS33-1` | Javonte Williams | 1.0 | 0.65 | 0.65 | 0.36 | -0.281 |
| `KXNFLTD-26OCT08TBDAL-DALEDEMERCADO31-1` | Emari Demercado | 1.0 | 0.07 | 0.08 | 0.16 | +0.087 |

_Ranked 2 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Camden Brown (WR, DAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Baker Mayfield (QB, TB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (CeeDee Lamb (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL3QSPREAD-26OCT08TBDAL-TB11 moved +0.970 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.281 on KXNFLTD-26OCT08TBDAL-DALJWILLIAMS33-1 (Javonte Williams). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by +0.087 on KXNFLTD-26OCT08TBDAL-DALEDEMERCADO31-1 (Emari Demercado). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLTD-26OCT08TBDAL-DALEDEMERCADO31-1 sits at a market price of 0.07 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_TB_DAL.md`_


---

## PHI @ JAX — `2026_05_PHI_JAX`

- kickoff: 2026-10-11T13:30:00+00:00 (-717 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 804 listed across 16 families — 0 supported, 21 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 804/804 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -0.30 | -- |
| total | 34.14 | -- |
| score | JAX 17.2 – PHI 16.9 | JAX -- – PHI -- |
| win prob JAX | 29.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 7.00 / total 21.50 · **2H** spread -5.82 / total 10.83 · **1Q** spread -7.00 / total 7.50 · **2Q** spread 12.50 / total 14.50 · **3Q** spread -3.00 / total -- · **4Q** spread -3.56 / total 6.91

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -0.30 · total 34.14
- move `KXNFL2QSPREAD-26OCT11PHIJAC-PHI11` +0.940
- move `KXNFL2QSPREAD-26OCT11PHIJAC-PHI8` +0.915

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (6; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 6 market(s), e.g. KXNFLRSHYDS-26OCT11PHIJAC-JACBTUTEN33-120, KXNFL1HFT-26OCT11PHIJAC-PHIJAC
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 5 market(s), e.g. KXNFLGAME-26OCT11PHIJAC-JAC, KXNFLSPREAD-26OCT11PHIJAC-JAC2
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 62 market(s), e.g. KXNFLRSHYDS-26OCT11PHIJAC-JACTLAWRENCE16-50, KXNFLMOSTRSHYDS-26OCT11PHIJAC-PHIDPIERCE39
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 21 market(s), e.g. KXNFL2HSPREAD-26OCT11PHIJAC-JAC5, KXNFL2HSPREAD-26OCT11PHIJAC-JAC4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 15 market(s), e.g. KXNFLRSHYDS-26OCT11PHIJAC-JACTLAWRENCE16-50, KXNFLREC-26OCT11PHIJAC-PHIDCOOPER80-3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 245 market(s), e.g. KXNFLFG-26OCT11PHIJAC-PHI4, KXNFLFG-26OCT11PHIJAC-PHI3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (14)**

- CJ Williams (WR, JAX) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- DeVonta Smith (WR, PHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Hollywood Brown (WR, PHI) — Out [single_source] — ruled out -- role redistributes to the depth chart behind him
- Saquon Barkley (RB, PHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tank Bigsby (RB, PHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Daniel Faalele (G, JAX) — Out [high] — ruled out
- Drew Kendall (C, PHI) — Out [high] — ruled out
- Albert Regis (DT, JAX) — Out [high] — ruled out
- _...and 6 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (7)** — resolves at the inactive release, T−90m

- Will Shipley (RB, PHI) — Questionable [conflicting]
- Anton Harrison (OT, JAX) — Questionable [high]
- Chance Campbell (LB, PHI) — Questionable [single_source]
- Jalyx Hunt (LB, PHI) — Questionable [high]
- Michael Carter II (CB, PHI) — Questionable [single_source]
- Montaric Brown (CB, JAX) — Questionable [high]
- Ross Matiscik (LS, JAX) — Questionable [single_source]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 99 listed player/stat groups simulated and exposed, 99 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. CJ Williams (WR, JAX) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. DeVonta Smith (WR, PHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Will Shipley (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLTD-26OCT11PHIJAC-JACPWASHINGTON11-2 moved +0.950 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_PHI_JAX.md`_


---

## CHI @ GB — `2026_05_CHI_GB`

- kickoff: 2026-10-11T17:00:00+00:00 (-507 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 816 listed across 16 families — 0 supported, 20 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 719/816 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -25.28 | -- |
| total | 38.81 | -- |
| score | GB 32.0 – CHI 6.8 | GB -- – CHI -- |
| win prob GB | 99.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -7.00 / total 21.50 · **2H** spread -- / total 16.83 · **1Q** spread -7.00 / total 7.50 · **2Q** spread -0.50 / total 14.50 · **3Q** spread -9.00 / total 9.50 · **4Q** spread -8.65 / total 9.87

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -25.28 · total 38.81
- move `KXNFL3QSPREAD-26OCT11CHIGB-GB8` +0.925
- move `KXNFL3QSPREAD-26OCT11CHIGB-GB7` +0.875

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (6; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 2 market(s), e.g. KXNFLMOSTRSHYDS-26OCT11CHIGB-CHIRJOHNSON23, KXNFLTEAMSACK-26OCT11CHIGB-GB4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 8 market(s), e.g. KXNFLBOTH-26OCT11CHIGB-14, KXNFLSPREAD-26OCT11CHIGB-GB28
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 77 market(s), e.g. KXNFLMOSTRECYDS-26OCT11CHIGB-GBTKRAFT85, KXNFLMOSTRECYDS-26OCT11CHIGB-GBMGOLDEN0
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 37 market(s), e.g. KXNFLLONGREC-26OCT11CHIGB-CHIRODUNZE15-20, KXNFLMOSTRECYDS-26OCT11CHIGB-GBCWATSON9
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 30 market(s), e.g. KXNFLREC-26OCT11CHIGB-GBMLLOYD32-2, KXNFLREC-26OCT11CHIGB-CHIRODUNZE15-4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 171 market(s), e.g. KXNFLREC-26OCT11CHIGB-CHICKMET85-4, KXNFLREC-26OCT11CHIGB-GBMLLOYD32-7

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (18)**

- Caleb Williams (QB, CHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Chris Brooks (RB, GB) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Kyle Monangai (RB, CHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Savion Williams (WR, GB) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Aaron Banks (G, GB) — Out [high] — ruled out
- Donovan Jennings (G, GB) — Out [high] — ruled out
- Jacob Monk (C, GB) — Out [high] — ruled out
- Ozzy Trapilo (OT, CHI) — Out [high] — ruled out
- _...and 10 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Skyy Moore (WR, GB) — Questionable [conflicting]
- Benjamin St-Juste (CB, GB) — Questionable [high]
- Dayo Odeyingbo (DE, CHI) — Questionable [high]
- T.J. Edwards (LB, CHI) — Questionable [high]
- Tyrique Stevenson Sr. (CB, CHI) — Questionable [single_source]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 100 listed player/stat groups simulated and exposed, 100 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Caleb Williams (QB, CHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Kyle Monangai (RB, CHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Skyy Moore (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLTD-26OCT11CHIGB-GBCWATSON9-2 moved +0.950 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_CHI_GB.md`_


---

## CIN @ MIA — `2026_05_CIN_MIA`

- kickoff: 2026-10-11T17:00:00+00:00 (-507 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 796 listed across 16 families — 3 supported, 29 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 795/796 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 7.00 | -- |
| total | 56.25 | -- |
| score | MIA 24.6 – CIN 31.6 | MIA -- – CIN -- |
| win prob MIA | 0.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 14.00 / total 27.00 · **2H** spread -6.98 / total 28.07 · **1Q** spread -0.00 / total 14.50 · **2Q** spread 12.50 / total 14.50 · **3Q** spread 5.62 / total 10.06 · **4Q** spread -12.51 / total 16.50

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 7.00 · total 56.25
- move `KXNFL1HTEAMTOTAL-26OCT11CINMIA-CIN21` +0.890
- move `KXNFL4QSPREAD-26OCT11CINMIA-MIA11` +0.870

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 8 market(s), e.g. KXNFLFG-26OCT11CINMIA-MIA4, KXNFLPASSCOMP-26OCT11CINMIA-CINJBURROW9-24
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 55 market(s), e.g. KXNFLMOSTRSHYDS-26OCT11CINMIA-MIAMWILLIS2, KXNFLPASSATT-26OCT11CINMIA-MIAMWILLIS2-34
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 35 market(s), e.g. KXNFLLONGREC-26OCT11CINMIA-CINCBROWN30-11, KXNFLMOSTRSHYDS-26OCT11CINMIA-MIAOGORDON0
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 35 market(s), e.g. KXNFLPASSATT-26OCT11CINMIA-MIAMWILLIS2-34, KXNFLPASSATT-26OCT11CINMIA-MIAMWILLIS2-29
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 155 market(s), e.g. KXNFLTD-26OCT11CINMIA-MIACWASHINGTON26-1, KXNFLTD-26OCT11CINMIA-CINMTINSLEY84-3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (15)**

- Caleb Douglas (WR, MIA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Colbie Young (WR, CIN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jack Endries (TE, CIN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Justin Joly (TE, MIA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Kaytron Allen (RB, MIA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Chukwuebuka Godrick (OT, MIA) — Out [high] — ruled out
- Connor Lew (C, CIN) — Out [high] — ruled out
- DJ Campbell (G, MIA) — Out [high] — ruled out
- _...and 7 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Jonah Savaiinaea (G, MIA) — Questionable [high]
- JuJu Brents (CB, MIA) — Questionable [high]
- Michael Taaffe (S, MIA) — Questionable [high]
- Swayze Bozeman (LB, CIN) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 93 listed player/stat groups simulated and exposed, 93 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTD-26OCT11CINMIA-CINCYOUNG86-1` | Colbie Young | 1.0 | 0.08 | 0.09 | 0.00 | -0.084 |
| `KXNFLTD-26OCT11CINMIA-CINJENDRIES84-1` | Jack Endries | 1.0 | 0.06 | 0.06 | 0.00 | -0.055 |
| `KXNFLTD-26OCT11CINMIA-CINCYOUNG86-2` | Colbie Young | 2.0 | 0.01 | 0.01 | 0.00 | -0.005 |

_Ranked 3 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Colbie Young (WR, CIN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jack Endries (TE, CIN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLFIRSTTD-26OCT11CINMIA-CINMGESICKI88 moved +0.945 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.084 on KXNFLTD-26OCT11CINMIA-CINCYOUNG86-1 (Colbie Young). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.055 on KXNFLTD-26OCT11CINMIA-CINJENDRIES84-1 (Jack Endries). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTD-26OCT11CINMIA-CINCYOUNG86-1 sits at a market price of 0.08 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_CIN_MIA.md`_


---

## CLE @ NYJ — `2026_05_CLE_NYJ`

- kickoff: 2026-10-11T17:00:00+00:00 (-507 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 749 listed across 16 families — 0 supported, 19 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 749/749 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -5.00 | -- |
| total | 29.35 | -- |
| score | NYJ 17.2 – CLE 12.2 | NYJ -- – CLE -- |
| win prob NYJ | 99.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -0.00 / total 13.00 · **2H** spread -4.00 / total 16.50 · **1Q** spread -5.00 / total 9.50 · **2Q** spread 3.00 / total -- · **3Q** spread -0.00 / total -- · **4Q** spread -5.00 / total 16.50

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -5.00 · total 29.35
- move `KXNFL2QTOTAL-26OCT11CLENYJ-4` -0.885
- move `KXNFL2QTOTAL-26OCT11CLENYJ-7` -0.800
- move `KXNFL3QTOTAL-26OCT11CLENYJ-4` -0.760

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (6; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 2 market(s), e.g. KXNFLTEAMFIRSTTD-26OCT11CLENYJ-CLE-CLEDST, KXNFLTEAMFIRSTTD-26OCT11CLENYJ-NYJ-KNWANGWU3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 1 market(s), e.g. KXNFLTEAMTOTAL-26OCT11CLENYJ-CLE8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 146 market(s), e.g. KXNFLLONGREC-26OCT11CLENYJ-NYJBALLEN0-9, KXNFLREC-26OCT11CLENYJ-NYJIWILLIAMS18-7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 41 market(s), e.g. KXNFLLONGRSH-26OCT11CLENYJ-CLEQJUDKINS10-13, KXNFLREC-26OCT11CLENYJ-NYJGWILSON5-7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 106 market(s), e.g. KXNFLLONGREC-26OCT11CLENYJ-NYJBALLEN0-9, KXNFLREC-26OCT11CLENYJ-NYJIWILLIAMS18-7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 161 market(s), e.g. KXNFLREC-26OCT11CLENYJ-NYJIWILLIAMS18-2, KXNFLREC-26OCT11CLENYJ-NYJMTAYLOR85-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (16)**

- Dillon Gabriel (QB, CLE) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Taylen Green (QB, CLE) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Adonai Mitchell (WR, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Breece Hall (RB, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Carsen Ryan (TE, CLE) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tylan Wallace (WR, CLE) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Dylan Parham (G, NYJ) — Out [high] — ruled out
- Parker Brailsford (C, CLE) — Out [high] — ruled out
- _...and 8 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (7)** — resolves at the inactive release, T−90m

- KC Concepcion (WR, CLE) — Questionable [conflicting]
- Kenyon Sadiq (TE, NYJ) — Questionable [conflicting]
- Quinshon Judkins (RB, CLE) — Questionable [high]
- Raheim Sanders (RB, CLE) — Questionable [high]
- Tytus Howard (OT, CLE) — Questionable [high]
- Carson Schwesinger (LB, CLE) — Questionable [high]
- Joseph Ossai (DE, NYJ) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 92 listed player/stat groups simulated and exposed, 92 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Carsen Ryan (TE, CLE) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Taylen Green (QB, CLE) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 4 skill players are Questionable (KC Concepcion (WR), Quinshon Judkins (RB), Raheim Sanders (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL2QTOTAL-26OCT11CLENYJ-4 moved -0.885 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_CLE_NYJ.md`_


---

## HOU @ TEN — `2026_05_HOU_TEN`

- kickoff: 2026-10-11T17:00:00+00:00 (-507 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 815 listed across 16 families — 1 supported, 28 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 720/815 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 22.00 | -- |
| total | 29.19 | -- |
| score | TEN 3.6 – HOU 25.6 | TEN -- – HOU -- |
| win prob TEN | 0.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 8.50 / total 16.50 · **2H** spread 14.00 / total 13.00 · **1Q** spread -0.00 / total 5.50 · **2Q** spread 9.00 / total 9.50 · **3Q** spread 7.00 / total 7.50 · **4Q** spread 7.00 / total 7.50

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 22.00 · total 29.19
- move `KXNFL2HSPREAD-26OCT11HOUTEN-HOU14` +0.880

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (6; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 9 market(s), e.g. KXNFLRSHYDS-26OCT11HOUTEN-HOUWMARKS4-70, KXNFLRECYDS-26OCT11HOUTEN-TENCTATE14-120
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 2 market(s), e.g. KXNFLTEAMTOTAL-26OCT11HOUTEN-HOU25, KXNFLTEAMTOTAL-26OCT11HOUTEN-HOU24
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 88 market(s), e.g. KXNFLMOSTRECYDS-26OCT11HOUTEN-HOUNCOLLINS12, KXNFLPASSCOMP-26OCT11HOUTEN-HOUCSTROUD7-27
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 32 market(s), e.g. KXNFLREC-26OCT11HOUTEN-TENGHELM84-1, KXNFLRRYDS-26OCT11HOUTEN-TENTSPEARS2-30
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 44 market(s), e.g. KXNFLPASSCOMP-26OCT11HOUTEN-HOUCSTROUD7-27, KXNFLREC-26OCT11HOUTEN-TENGHELM84-1
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 185 market(s), e.g. KXNFLREC-26OCT11HOUTEN-HOUXHUTCHINSON19-5, KXNFLREC-26OCT11HOUTEN-HOUNCOLLINS12-6

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (17)**

- David Martin-Robinson (TE, TEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Marlin Klein (TE, HOU) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Michael Carter (RB, TEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Nicholas Singleton (RB, TEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tank Dell (WR, HOU) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Braden Smith (OT, HOU) — Injured Reserve [high] — ruled out
- Brandon Crenshaw-Dickson (OT, TEN) — Out [single_source] — ruled out
- Febechi Nwaiwu (G, HOU) — Out [high] — ruled out
- _...and 9 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- David Montgomery (RB, HOU) — Questionable [conflicting]
- Cor'Dale Flott (CB, TEN) — Questionable [high]
- Jalen Pitre (S, HOU) — Questionable [high]
- Kevin Winston Jr. (S, TEN) — Questionable [single_source]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 108 listed player/stat groups simulated and exposed, 108 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTD-26OCT11HOUTEN-TENNSINGLETON32-1` | Nicholas Singleton | 1.0 | 0.04 | 0.05 | 0.00 | -0.045 |

_Ranked 1 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Marlin Klein (TE, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Tank Dell (WR, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (David Montgomery (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLREC-26OCT11HOUTEN-HOUJNOEL13-5 moved +0.955 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.045 on KXNFLTD-26OCT11HOUTEN-TENNSINGLETON32-1 (Nicholas Singleton). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTD-26OCT11HOUTEN-TENNSINGLETON32-1 sits at a market price of 0.04 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_HOU_TEN.md`_


---

## IND @ PIT — `2026_05_IND_PIT`

- kickoff: 2026-10-11T17:00:00+00:00 (-507 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 778 listed across 16 families — 13 supported, 30 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 778/778 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -11.37 | -- |
| total | 58.91 | -- |
| score | PIT 35.1 – IND 23.8 | PIT -- – IND -- |
| win prob PIT | 98.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -4.00 / total 30.50 · **2H** spread -8.50 / total 28.84 · **1Q** spread -0.00 / total 12.50 · **2Q** spread -3.00 / total 16.50 · **3Q** spread -0.00 / total 12.50 · **4Q** spread -5.94 / total 13.83

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -11.37 · total 58.91

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (7; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 22 market(s), e.g. KXNFLMOSTRECYDS-26OCT11INDPIT-INDJDOWNS2, KXNFLRECYDS-26OCT11INDPIT-INDTWARREN84-130
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 2 market(s), e.g. KXNFLTEAMTOTAL-26OCT11INDPIT-PIT36, KXNFLTEAMTOTAL-26OCT11INDPIT-IND29
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLSPREAD-26OCT11INDPIT-PIT7, KXNFLSPREAD-26OCT11INDPIT-PIT11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 135 market(s), e.g. KXNFLRSHATT-26OCT11INDPIT-INDJTAYLOR28-17, KXNFLMOSTRECYDS-26OCT11INDPIT-PITDMETCALF4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 64 market(s), e.g. KXNFLMOSTRECYDS-26OCT11INDPIT-PITJWARREN30, KXNFLREC-26OCT11INDPIT-INDJDOWNS2-3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 85 market(s), e.g. KXNFLRSHATT-26OCT11INDPIT-INDJTAYLOR28-17, KXNFLPASSTDS-26OCT11INDPIT-INDDJONES17-2

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (17)**

- Drew Allar (QB, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Riley Leonard (QB, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Will Howard (QB, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Ashton Dulin (WR, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Darius Slayton (WR, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Eli Heidenreich (RB, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Michael Pittman Jr. (WR, PIT) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Rico Dowdle (RB, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- _...and 9 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Ben Skowronek (WR, PIT) — Questionable [high]
- Roman Wilson (WR, PIT) — Questionable [conflicting]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 94 listed player/stat groups simulated and exposed, 94 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRECYDS-26OCT11INDPIT-PITMPITTMAN11-25` | Michael Pittman Jr. | 25.0 | 0.60 | 0.62 | 0.01 | -0.587 |
| `KXNFLRECYDS-26OCT11INDPIT-PITMPITTMAN11-40` | Michael Pittman Jr. | 40.0 | 0.33 | 0.34 | 0.01 | -0.316 |
| `KXNFLTD-26OCT11INDPIT-PITMPITTMAN11-1` | Michael Pittman Jr. | 1.0 | 0.22 | 0.23 | 0.00 | -0.211 |
| `KXNFLRECYDS-26OCT11INDPIT-PITMPITTMAN11-50` | Michael Pittman Jr. | 50.0 | 0.19 | 0.21 | 0.01 | -0.184 |
| `KXNFLRECYDS-26OCT11INDPIT-PITMPITTMAN11-60` | Michael Pittman Jr. | 60.0 | 0.10 | 0.14 | 0.00 | -0.091 |
| `KXNFLTD-26OCT11INDPIT-INDADULIN16-1` | Ashton Dulin | 1.0 | 0.12 | 0.13 | 0.06 | -0.070 |

_Ranked 12 tradable markets; 1 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Ashton Dulin (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Darius Slayton (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Ben Skowronek (WR), Roman Wilson (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRECYDS-26OCT11INDPIT-PITJWARREN30-60 moved +0.935 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.587 on KXNFLRECYDS-26OCT11INDPIT-PITMPITTMAN11-25 (Michael Pittman Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.316 on KXNFLRECYDS-26OCT11INDPIT-PITMPITTMAN11-40 (Michael Pittman Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRECYDS-26OCT11INDPIT-PITMPITTMAN11-60 sits at a market price of 0.10 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_IND_PIT.md`_


---

## LV @ NE — `2026_05_LV_NE`

- kickoff: 2026-10-11T17:00:00+00:00 (-507 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 828 listed across 16 families — 2 supported, 16 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 828/828 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -23.21 | -- |
| total | 69.38 | -- |
| score | NE 46.3 – LV 23.1 | NE -- – LV -- |
| win prob NE | 99.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -14.00 / total 27.00 · **2H** spread -13.79 / total 36.11 · **1Q** spread -7.00 / total 21.50 · **2Q** spread -7.00 / total 7.50 · **3Q** spread -12.50 / total 16.50 · **4Q** spread -2.85 / total 21.32

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -23.21 · total 69.38
- move `KXNFLTEAMTOTAL-26OCT11LVNE-NE43` +0.945
- move `KXNFL3QSPREAD-26OCT11LVNE-NE11` +0.940
- move `KXNFL1QTOTAL-26OCT11LVNE-21` +0.935
- move `KXNFLTEAMTOTAL-26OCT11LVNE-NE39` +0.925

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (7; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 9 market(s), e.g. KXNFLTEAMSACK-26OCT11LVNE-LV5, KXNFL4QSPREAD-26OCT11LVNE-LV8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 6 market(s), e.g. KXNFLBOTH-26OCT11LVNE-35, KXNFLBOTH-26OCT11LVNE-28
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTEAMTOTAL-26OCT11LVNE-LV18, KXNFLTOTAL-26OCT11LVNE-66
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 156 market(s), e.g. KXNFLRECYDS-26OCT11LVNE-NERDOUBS87-20, KXNFLRECYDS-26OCT11LVNE-NERSTEVENSON38-25
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 63 market(s), e.g. KXNFLRECYDS-26OCT11LVNE-NERDOUBS87-15, KXNFLRECYDS-26OCT11LVNE-NEERARIDON82-55
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 99 market(s), e.g. KXNFLRECYDS-26OCT11LVNE-NERDOUBS87-20, KXNFLRECYDS-26OCT11LVNE-NERSTEVENSON38-25

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (17)**

- Aidan O'Connell (QB, LV) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Behren Morton (QB, NE) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- A.J. Brown (WR, NE) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Dont'e Thornton Jr. (WR, LV) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Jalen Nailor (WR, LV) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Mack Hollins (WR, NE) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Roman Hemby (RB, LV) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Dametrious Crownover (OT, NE) — Out [single_source] — ruled out
- _...and 9 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (6)** — resolves at the inactive release, T−90m

- TreVeyon Henderson (RB, NE) — Questionable [conflicting]
- Will Campbell (OT, NE) — Questionable [single_source]
- Charles Woods (CB, NE) — Questionable [high]
- Dre'Mont Jones (DE, NE) — Questionable [high]
- Patrick Johnson (DE, LV) — Questionable [high]
- Tonka Hemingway (DT, LV) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 105 listed player/stat groups simulated and exposed, 105 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTD-26OCT11LVNE-LVRHEMBY37-1` | Roman Hemby | 1.0 | 0.07 | 0.07 | 0.00 | -0.064 |
| `KXNFLTD-26OCT11LVNE-NERGILLIAM44-1` | Reggie Gilliam | 1.0 | 0.06 | 0.06 | 0.00 | -0.053 |

_Ranked 2 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Aidan O'Connell (QB, LV) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jalen Nailor (WR, LV) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (TreVeyon Henderson (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLTEAMTOTAL-26OCT11LVNE-NE43 moved +0.945 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.064 on KXNFLTD-26OCT11LVNE-LVRHEMBY37-1 (Roman Hemby). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.053 on KXNFLTD-26OCT11LVNE-NERGILLIAM44-1 (Reggie Gilliam). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLTD-26OCT11LVNE-LVRHEMBY37-1 sits at a market price of 0.07 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_LV_NE.md`_


---

## MIN @ NO — `2026_05_MIN_NO`

- kickoff: 2026-10-11T17:00:00+00:00 (-507 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 767 listed across 16 families — 4 supported, 23 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 767/767 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 10.00 | -- |
| total | 37.39 | -- |
| score | NO 13.7 – MIN 23.7 | NO -- – MIN -- |
| win prob NO | 1.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -0.50 / total 13.00 · **2H** spread 12.00 / total 23.50 · **1Q** spread 3.00 / total -- · **2Q** spread -5.00 / total 9.50 · **3Q** spread 0.50 / total 12.50 · **4Q** spread 9.00 / total 9.50

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 10.00 · total 37.39
- move `KXNFL2HSPREAD-26OCT11MINNO-MIN11` +0.870
- move `KXNFL4QSPREAD-26OCT11MINNO-MIN8` +0.860
- move `KXNFL2HSPREAD-26OCT11MINNO-MIN10` +0.835
- move `KXNFL2HSPREAD-26OCT11MINNO-MIN8` +0.805

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 6 market(s), e.g. KXNFLMOSTRSHYDS-26OCT11MINNO-NOKMILLER5, KXNFLTEAMFIRSTTD-26OCT11MINNO-MIN-MINDST
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 139 market(s), e.g. KXNFLLONGREC-26OCT11MINNO-MINJJEFFERSON18-26, KXNFLLONGREC-26OCT11MINNO-MINJJENNINGS14-13
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 37 market(s), e.g. KXNFLREC-26OCT11MINNO-NOJJOHNSON83-4, KXNFLRECYDS-26OCT11MINNO-NODVELE14-10
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 106 market(s), e.g. KXNFLLONGREC-26OCT11MINNO-MINJJEFFERSON18-26, KXNFLLONGREC-26OCT11MINNO-MINJJENNINGS14-13
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 164 market(s), e.g. KXNFLFG-26OCT11MINNO-NO1, KXNFLPASSCOMP-26OCT11MINNO-NOTSHOUGH6-18

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (16)**

- Max Brosmer (QB, MIN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Zach Wilson (QB, NO) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jordan Addison (WR, MIN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Josh Oliver (TE, MIN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Odell Beckham Jr. (WR, MIN) — Out [single_source] — ruled out -- role redistributes to the depth chart behind him
- Christian Darrisaw (OT, MIN) — Out [high] — ruled out
- Donovan Jackson (G, MIN) — Injured Reserve [high] — ruled out
- Jeremiah Wright (G, NO) — Out [high] — ruled out
- _...and 8 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- T.J. Hockenson (TE, MIN) — Questionable [conflicting]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 90 listed player/stat groups simulated and exposed, 90 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTD-26OCT11MINNO-MINJADDISON3-1` | Jordan Addison | 1.0 | 0.26 | 0.26 | 0.00 | -0.254 |
| `KXNFLTD-26OCT11MINNO-MINOBECKHAM13-1` | Odell Beckham Jr. | 1.0 | 0.07 | 0.08 | 0.00 | -0.069 |
| `KXNFLTD-26OCT11MINNO-NOKAUSTIN81-1` | Kevin Austin Jr. | 1.0 | 0.03 | 0.03 | 0.09 | +0.067 |
| `KXNFLTD-26OCT11MINNO-MINJADDISON3-2` | Jordan Addison | 2.0 | 0.06 | 0.06 | 0.00 | -0.055 |

_Ranked 4 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jordan Addison (WR, MIN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Max Brosmer (QB, MIN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (T.J. Hockenson (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL1HFT-26OCT11MINNO-NOMIN moved +0.890 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.254 on KXNFLTD-26OCT11MINNO-MINJADDISON3-1 (Jordan Addison). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.069 on KXNFLTD-26OCT11MINNO-MINOBECKHAM13-1 (Odell Beckham Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLTD-26OCT11MINNO-MINOBECKHAM13-1 sits at a market price of 0.07 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_MIN_NO.md`_


---

## NYG @ WAS — `2026_05_NYG_WAS`

- kickoff: 2026-10-11T17:00:00+00:00 (-507 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 768 listed across 16 families — 3 supported, 24 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 702/768 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -0.00 | -- |
| total | 55.50 | -- |
| score | WAS 27.8 – NYG 27.8 | WAS -- – NYG -- |
| win prob WAS | 50.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -8.50 / total 16.50 · **2H** spread 8.54 / total 41.13 · **1Q** spread -3.00 / total 9.50 · **2Q** spread -5.00 / total 5.51 · **3Q** spread 3.00 / total 16.50 · **4Q** spread 5.58 / total 24.30

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -0.00 · total 55.50
- move `KXNFL2HTOTAL-26OCT11NYGWAS-39` +0.920

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 10 market(s), e.g. KXNFLMOSTRSHYDS-26OCT11NYGWAS-WASJCROSKEYMERRITT22, KXNFLRSHYDS-26OCT11NYGWAS-WASJCROSKEYMERRITT22-90
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 103 market(s), e.g. KXNFLMOSTRSHYDS-26OCT11NYGWAS-WASJCROSKEYMERRITT22, KXNFLPASSYDS-26OCT11NYGWAS-WASJDANIELS5-200
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 44 market(s), e.g. KXNFLTEAMYDS-26OCT11NYGWAS-NYG350, KXNFLREC-26OCT11NYGWAS-NYGDMOONEY17-2
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 85 market(s), e.g. KXNFLPASSYDS-26OCT11NYGWAS-WASJDANIELS5-200, KXNFLRSHATT-26OCT11NYGWAS-WASJDANIELS5-10
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 132 market(s), e.g. KXNFLREC-26OCT11NYGWAS-WASJCROSKEYMERRITT22-1, KXNFLREC-26OCT11NYGWAS-WASTMCLAURIN17-8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (18)**

- Jake Haener (QB, NYG) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Marcus Mariota (QB, WAS) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Braxton Berrios (WR, NYG) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Devin Singletary (RB, NYG) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jaylin Lane (WR, WAS) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jeremy McNichols (RB, WAS) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Stefon Diggs (WR, WAS) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- J.C. Davis (OT, NYG) — Out [single_source] — ruled out
- _...and 10 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Jermaine Eluemunor (OT, NYG) — Questionable [high]
- Colton Hood (CB, NYG) — Questionable [high]
- Tyler Nubin (S, NYG) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 91 listed player/stat groups simulated and exposed, 91 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTD-26OCT11NYGWAS-WASKALLEN31-1` | Kaytron Allen | 1.0 | 0.10 | 0.11 | 0.00 | -0.099 |
| `KXNFLTD-26OCT11NYGWAS-NYGDSINGLETARY26-1` | Devin Singletary | 1.0 | 0.08 | 0.08 | 0.15 | +0.075 |
| `KXNFLTD-26OCT11NYGWAS-WASKALLEN31-2` | Kaytron Allen | 2.0 | 0.03 | 0.03 | 0.00 | -0.025 |

_Ranked 3 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Devin Singletary (RB, NYG) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jake Haener (QB, NYG) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLWINMARGIN-26OCT11NYGWAS-TIE moved +0.990 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.099 on KXNFLTD-26OCT11NYGWAS-WASKALLEN31-1 (Kaytron Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by +0.075 on KXNFLTD-26OCT11NYGWAS-NYGDSINGLETARY26-1 (Devin Singletary). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTD-26OCT11NYGWAS-WASKALLEN31-1 sits at a market price of 0.10 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_NYG_WAS.md`_


---

## DEN @ LAC — `2026_05_DEN_LAC`

- kickoff: 2026-10-11T20:05:00+00:00 (-322 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 776 listed across 16 families — 2 supported, 27 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 5.96 | -- |
| total | 39.19 | -- |
| score | LAC 16.6 – DEN 22.6 | LAC -- – DEN -- |
| win prob LAC | 9.0% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 7.00 / total 13.00 · **2H** spread -0.20 / total 28.25 · **1Q** spread 7.00 / total 7.50 · **2Q** spread -0.00 / total 5.50 · **3Q** spread -12.50 / total 14.50 · **4Q** spread 12.48 / total 12.69

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 5.96 · total 39.19
- move `KXNFL3QSPREAD-26OCT11DENLAC-LAC11` +0.945
- move `KXNFL3QSPREAD-26OCT11DENLAC-LAC8` +0.930
- move `KXNFL3QSPREAD-26OCT11DENLAC-LAC7` +0.885
- move `KXNFL2QTOTAL-26OCT11DENLAC-7` -0.830

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (7; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 5 market(s), e.g. KXNFLLONGREC-26OCT11DENLAC-DENCSUTTON14-18, KXNFLREC-26OCT11DENLAC-DENMMIMS19-5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 4 market(s), e.g. KXNFLBOTH-26OCT11DENLAC-21, KXNFLTEAMTOTAL-26OCT11DENLAC-LAC22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 1 market(s), e.g. KXNFLTEAMTOTAL-26OCT11DENLAC-DEN15
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 193 market(s), e.g. KXNFLRECYDS-26OCT11DENLAC-DENJWADDLE17-20, KXNFLPASSATT-26OCT11DENLAC-DENBNIX10-29
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 28 market(s), e.g. KXNFLLONGRSH-26OCT11DENLAC-DENJDOBBINS27-14, KXNFLTEAMSACK-26OCT11DENLAC-DEN5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 137 market(s), e.g. KXNFLRECYDS-26OCT11DENLAC-DENJWADDLE17-20, KXNFLPASSATT-26OCT11DENLAC-DENBNIX10-29

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (18)**

- Sam Ehlinger (QB, DEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Trey Lance (QB, LAC) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Brenen Thompson (WR, LAC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Dallen Bentley (TE, DEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Pat Bryant (WR, DEN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Quentin Johnston (WR, LAC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Joe Alt (OT, LAC) — Out [high] — ruled out
- Kage Casey (OT, DEN) — Out [single_source] — ruled out
- _...and 10 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Tre' Harris (WR, LAC) — Questionable [high]
- Bud Dupree (LB, LAC) — Questionable [high]
- Talanoa Hufanga (S, DEN) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 96 listed player/stat groups simulated and exposed, 96 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTD-26OCT11DENLAC-LACQJOHNSTON1-1` | Quentin Johnston | 1.0 | 0.24 | 0.25 | 0.00 | -0.239 |
| `KXNFLTD-26OCT11DENLAC-LACQJOHNSTON1-2` | Quentin Johnston | 2.0 | 0.03 | 0.04 | 0.00 | -0.030 |

_Ranked 2 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Dallen Bentley (TE, DEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Sam Ehlinger (QB, DEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Tre' Harris (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL3QSPREAD-26OCT11DENLAC-LAC11 moved +0.945 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.239 on KXNFLTD-26OCT11DENLAC-LACQJOHNSTON1-1 (Quentin Johnston). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.030 on KXNFLTD-26OCT11DENLAC-LACQJOHNSTON1-2 (Quentin Johnston). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLTD-26OCT11DENLAC-LACQJOHNSTON1-2 sits at a market price of 0.03 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_DEN_LAC.md`_


---

## DET @ ARI — `2026_05_DET_ARI`

- kickoff: 2026-10-11T20:25:00+00:00 (-302 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 854 listed across 16 families — 20 supported, 21 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 25.50 | -- |
| total | 60.64 | -- |
| score | ARI 17.6 – DET 43.1 | ARI -- – DET -- |
| win prob ARI | 0.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -- / total 30.50 · **2H** spread 7.00 / total 34.00 · **1Q** spread -7.00 / total 7.50 · **2Q** spread -- / total 23.50 · **3Q** spread 7.00 / total 21.50 · **4Q** spread -0.50 / total 14.50

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 25.50 · total 60.64
- move `KXNFLTEAMTOTAL-26OCT11DETARI-DET43` +0.915
- move `KXNFL1HTEAMTOTAL-26OCT11DETARI-DET24` +0.895
- move `KXNFL3QTOTAL-26OCT11DETARI-21` +0.890
- move `KXNFLTEAMTOTAL-26OCT11DETARI-DET39` +0.875

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (6; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 6 market(s), e.g. KXNFLTOTAL-26OCT11DETARI-64, KXNFLTEAMFIRSTTD-26OCT11DETARI-DET-JGIBBS0
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 2 market(s), e.g. KXNFLBOTH-26OCT11DETARI-21, KXNFLTEAMTOTAL-26OCT11DETARI-ARI21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 44 market(s), e.g. KXNFLLONGREC-26OCT11DETARI-ARITALLGEIER22-9, KXNFLMOSTRSHYDS-26OCT11DETARI-ARITALLGEIER22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 21 market(s), e.g. KXNFLRECYDS-26OCT11DETARI-ARIKBOURNE17-70, KXNFLMOSTRECYDS-26OCT11DETARI-ARIEHIGGINS84
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 32 market(s), e.g. KXNFLLONGREC-26OCT11DETARI-ARITALLGEIER22-9, KXNFLREC-26OCT11DETARI-DETITESLAA18-1
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 255 market(s), e.g. KXNFLFG-26OCT11DETARI-DET4, KXNFLFG-26OCT11DETARI-DET3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (15)**

- Carson Beck (QB, ARI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Hunter Long (TE, ARI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jackson Meeks (WR, DET) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Ben Bartch (G, DET) — Out [high] — ruled out
- Cade Mays (C, DET) — Injured Reserve [high] — ruled out
- Isaiah Adams (G, ARI) — Injured Reserve [high] — ruled out
- Paris Johnson Jr. (OT, ARI) — Injured Reserve [single_source] — ruled out
- Ahmed Hassanein (DE, DET) — Out [high] — ruled out
- _...and 7 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Tom Kennedy (WR, DET) — Questionable [high]
- Devin White (LB, DET) — Questionable [high]
- Wydett Williams Jr. (S, ARI) — Questionable [single_source]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 101 listed player/stat groups simulated and exposed, 101 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT11DETARI-ARIMHARRISON18-3` | Marvin Harrison Jr. | 3.0 | 0.51 | 0.52 | 0.00 | -0.502 |
| `KXNFLREC-26OCT11DETARI-ARIMHARRISON18-2` | Marvin Harrison Jr. | 2.0 | 0.51 | 0.51 | 0.00 | -0.501 |
| `KXNFLRECYDS-26OCT11DETARI-ARIMHARRISON18-35` | Marvin Harrison Jr. | 35.0 | 0.46 | 0.47 | 0.00 | -0.457 |
| `KXNFLRECYDS-26OCT11DETARI-ARIMHARRISON18-50` | Marvin Harrison Jr. | 50.0 | 0.30 | 0.33 | 0.00 | -0.298 |
| `KXNFLREC-26OCT11DETARI-ARIMHARRISON18-4` | Marvin Harrison Jr. | 4.0 | 0.29 | 0.34 | 0.00 | -0.283 |
| `KXNFLTD-26OCT11DETARI-ARIMHARRISON18-1` | Marvin Harrison Jr. | 1.0 | 0.22 | 0.23 | 0.00 | -0.219 |

_Ranked 15 tradable markets; 5 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Carson Beck (QB, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Hunter Long (TE, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Tom Kennedy (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRECYDS-26OCT11DETARI-ARIEHIGGINS84-50 moved +0.950 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.502 on KXNFLREC-26OCT11DETARI-ARIMHARRISON18-3 (Marvin Harrison Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.501 on KXNFLREC-26OCT11DETARI-ARIMHARRISON18-2 (Marvin Harrison Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRECYDS-26OCT11DETARI-ARIMHARRISON18-80 sits at a market price of 0.09 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_DET_ARI.md`_


---

## SF @ SEA — `2026_05_SF_SEA`

- kickoff: 2026-10-11T20:25:00+00:00 (-302 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 775 listed across 16 families — 0 supported, 22 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.68 | -- |
| total | 62.82 | -- |
| score | SEA 30.1 – SF 32.7 | SEA -- – SF -- |
| win prob SEA | 40.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 8.50 / total 34.00 · **2H** spread -5.50 / total 27.00 · **1Q** spread -0.00 / total 14.50 · **2Q** spread 9.00 / total 19.50 · **3Q** spread -13.08 / total 12.50 · **4Q** spread 9.00 / total 14.50

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.68 · total 62.82
- move `KXNFL3QSPREAD-26OCT11SFSEA-SEA11` +0.920
- move `KXNFL1HTEAMTOTAL-26OCT11SFSEA-SF21` +0.920
- move `KXNFL1HTEAMTOTAL-26OCT11SFSEA-SF20` +0.905
- move `KXNFL4QSPREAD-26OCT11SFSEA-SF8` +0.880

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (6; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 15 market(s), e.g. KXNFL1HFT-26OCT11SFSEA-SFSEA, KXNFLOT-26OCT11SFSEA-Y
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 5 market(s), e.g. KXNFLBOTH-26OCT11SFSEA-35, KXNFLSPREAD-26OCT11SFSEA-SEA4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 64 market(s), e.g. KXNFLLONGRSH-26OCT11SFSEA-SFCMCCAFFREY23-14, KXNFLLONGREC-26OCT11SFSEA-SEATHORTON15-9
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 29 market(s), e.g. KXNFLMOSTRSHYDS-26OCT11SFSEA-SEAJSMITHNJIGBA11, KXNFLMOSTRSHYDS-26OCT11SFSEA-SFDSAMUEL19
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 42 market(s), e.g. KXNFLLONGRSH-26OCT11SFSEA-SFCMCCAFFREY23-14, KXNFLLONGREC-26OCT11SFSEA-SEATHORTON15-9
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 226 market(s), e.g. KXNFLFG-26OCT11SFSEA-SF2, KXNFLTD-26OCT11SFSEA-SFJSTOLL83-1

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (15)**

- Jalen Milroe (QB, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Kurtis Rourke (QB, SF) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Irv Charles (WR, SEA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Montorie Foster Jr. (WR, SEA) — Out [single_source] — ruled out -- role redistributes to the depth chart behind him
- Nick Kallerup (TE, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Robert Henry Jr. (RB, SEA) — Out [single_source] — ruled out -- role redistributes to the depth chart behind him
- Zach Charbonnet (RB, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Enrique Cruz Jr. (OT, SF) — Out [single_source] — ruled out
- _...and 7 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Deebo Samuel Sr. (WR, SF) — Questionable [single_source]
- Drake Thomas (LB, SEA) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 95 listed player/stat groups simulated and exposed, 95 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jalen Milroe (QB, SEA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Montorie Foster Jr. (WR, SEA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Deebo Samuel Sr. (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLTEAMSACK-26OCT11SFSEA-SF5 moved +0.950 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_SF_SEA.md`_


---

## BAL @ ATL — `2026_05_BAL_ATL`

- kickoff: 2026-10-12T00:20:00+00:00 (-67 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: Mercedes-Benz Stadium · roof  · surface fieldturf
- markets: 744 listed across 16 families — 0 supported, 16 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -6.57 | -- |
| total | 47.11 | -- |
| score | ATL 26.8 – BAL 20.3 | ATL -- – BAL -- |
| win prob ATL | 71.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -6.30 / total 24.67 · **2H** spread -1.43 / total 22.00 · **1Q** spread -5.35 / total 10.14 · **2Q** spread -1.84 / total 13.42 · **3Q** spread -1.65 / total 8.31 · **4Q** spread 0.69 / total 12.64

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -6.57 · total 47.11
- move `KXNFL1QSPREAD-26OCT11BALATL-ATL4` +0.695
- move `KXNFL1QSPREAD-26OCT11BALATL-ATL3` +0.560
- move `KXNFL1QTOTAL-26OCT11BALATL-8` +0.515
- move `KXNFLGAME-26OCT11BALATL-BAL` -0.415

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (7; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 76 market(s), e.g. KXNFL1HSPREAD-26OCT11BALATL-ATL8, KXNFL1HSPREAD-26OCT11BALATL-ATL14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 17 market(s), e.g. KXNFLBOTH-26OCT11BALATL-28, KXNFLGAME-26OCT11BALATL-BAL
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLSPREAD-26OCT11BALATL-ATL3, KXNFLSPREAD-26OCT11BALATL-ATL2
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 211 market(s), e.g. KXNFL1H-26OCT11BALATL-TIE, KXNFL1HFT-26OCT11BALATL-TIEBAL
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 30 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT11BALATL-ATL10, KXNFL1HTOTAL-26OCT11BALATL-18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 157 market(s), e.g. KXNFLFFPTS-26OCT11BALATL-BALTLOOP33-7P5, KXNFLFFPTS-26OCT11BALATL-ATLNFOLK6-8P2

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261012T010506Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (16)**

- Cooper Rush (QB, ATL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jack Strand (QB, ATL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Lamar Jackson (QB, BAL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Durham Smythe (TE, BAL) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Elijah Sarratt (WR, BAL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Ja'Kobi Lane (WR, BAL) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Andrew Vorhees (G, BAL) — Out [high] — ruled out
- Cam Jurgens (C, BAL) — Out [high] — ruled out
- _...and 8 more (mostly non-skill positions); full list in the game file_

### WEATHER

- Partly Cloudy · 65°F · wind 10 mph W · precip 0%
- forecast vintage 2026-10-12T01:03:51+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 66, 'wind': '10 mph', 'precipitation_probability': 1})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 93 listed player/stat groups simulated and exposed, 93 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Cooper Rush (QB, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jack Strand (QB, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
4. KXNFLRSHYDS-26OCT11BALATL-BALJHILL43-25 moved +0.855 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_BAL_ATL.md`_


---

## BUF @ LA — `2026_05_BUF_LA`

- kickoff: 2026-10-13T00:15:00+00:00 (1368 minutes away) · state **PREGAME**
- venue: SoFi Stadium · roof dome · surface matrixturf
- markets: 782 listed across 16 families — 434 supported, 292 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.22 | -3.00 |
| total | 54.62 | 54.40 |
| score | LA 28.9 – BUF 25.7 | LA 28.7 – BUF 25.7 |
| win prob LA | 61.5% | 60.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -2.58 / total 27.64 · **2H** spread -1.62 / total 27.86 · **1Q** spread -0.94 / total 9.95 · **2Q** spread -1.28 / total 16.15 · **3Q** spread -1.33 / total 10.76 · **4Q** spread -0.04 / total 15.43

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.22 · total 54.62
- move `KXNFLTEAMTOTAL-26OCT12BUFLAR-LAR8` +0.120
- move `KXNFLTEAMTOTAL-26OCT12BUFLAR-BUF4` +0.115
- move `KXNFLTEAMTOTAL-26OCT12BUFLAR-LAR4` +0.110

**Game environment** (simulation, mean and middle 50%) — home margin 3.6 (-4.0–11.0) · total 55.6 (46.0–64.0) · P(one score) 52.1% · P(17+ blowout) 17.7% · P(total 10+ over centre) 23.5%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| LA | 66.0 (60.0–72.0) | 38.4 (33.0–44.0) | 24.1 (19.0–29.0) | 40.9 (35.0–46.0) | 0.620 (0.553–0.689) | 0.537 / 0.719 |
| BUF | 63.1 (57.0–69.0) | 33.1 (28.0–38.0) | 24.4 (19.0–29.0) | 38.1 (33.0–43.0) | 0.605 (0.539–0.672) | 0.498 / 0.673 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| LA | 00-0037840 | RB | 4.0 (1.0–6.0) | 14.2 (9.0–19.0) | 10.8% | 58.9% | MEDIUM |
| LA | 00-0039075 | WR | 9.9 (6.0–13.0) | 0.8 (0.0–1.0) | 26.9% | 3.5% | MEDIUM |
| LA | 00-0039738 | RB | 1.3 (0.0–2.0) | 6.8 (3.0–10.0) | 3.7% | 28.2% | HIGH |
| LA | 00-0031381 | WR | 7.5 (4.0–10.0) | 0.1 (0.0–0.0) | 20.3% | 0.3% | HIGH |
| BUF | 00-0037248 | RB | 2.8 (1.0–4.0) | 15.2 (10.0–20.0) | 8.8% | 62.5% | MEDIUM |
| BUF | 00-0034857 | QB | 0.3 (0.0–0.0) | 7.7 (4.0–10.0) | 0.9% | 17.6% | HIGH |
| BUF | 00-0037261 | WR | 6.7 (4.0–9.0) | 0.1 (0.0–0.0) | 21.0% | 0.4% | HIGH |
| BUF | 00-0038933 | TE | 5.1 (2.0–7.0) | 0.1 (0.0–0.0) | 16.0% | 0.2% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 3 market(s), e.g. KXNFLREC-26OCT12BUFLAR-LARKMUMPFIELD4-3, KXNFLTD-26OCT12BUFLAR-LARMSTAFFORD9-1
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 46 market(s), e.g. KXNFLFIRSTTD-26OCT12BUFLAR-LARKWILLIAMS23, KXNFLPASSTDS-26OCT12BUFLAR-LARMSTAFFORD9-4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 24 market(s), e.g. KXNFLSPREAD-26OCT12BUFLAR-LAR17, KXNFLSPREAD-26OCT12BUFLAR-LAR11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLGAME-26OCT12BUFLAR-LAR, KXNFLTEAMTOTAL-26OCT12BUFLAR-LAR25
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 211 market(s), e.g. KXNFL1H-26OCT12BUFLAR-TIE, KXNFL1HFT-26OCT12BUFLAR-TIELAR
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 49 market(s), e.g. KXNFL1HTOTAL-26OCT12BUFLAR-15, KXNFL4QTOTAL-26OCT12BUFLAR-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 28.6%  _(final margin within one score (8 points) either way; total within 10 of the centre 54.625 (median favourite-oriented margin +2, median total 54))_
2. favourite controls / normal scoring — 19.6%  _(LA (favourite) wins by more than one score; total within 10 of the centre 54.625 (median favourite-oriented margin +14, median total 54))_
3. competitive / high scoring — 12.0%  _(final margin within one score (8 points) either way; total 64.625+ (centre 54.625) (median favourite-oriented margin +2, median total 72))_
4. competitive / low scoring — 11.5%  _(final margin within one score (8 points) either way; total 44.625 or fewer (centre 54.625) (median favourite-oriented margin +2, median total 40))_
5. underdog controls / normal scoring — 7.8%  _(BUF (underdog) wins by more than one score; total within 10 of the centre 54.625 (median favourite-oriented margin -14, median total 55))_
   Other — 20.5%

Marginal events (overlapping): one_score 52.1% · blowout_17 17.7% · favorite_wins 63.7% · favorite_controls 32.8% · upset 36.1% · shootout 23.5% · low_scoring 20.6% · low_possession 4.3% · high_volume_passing 17.6% · run_heavy_control 13.0%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 1.80 mph, gusts 7.20, precip prob 0%, temp 64F, forecast retrieved 2026-10-12T01:03:51+00:00 (23.19 h before kickoff)._

**`KXNFLTD-26OCT12BUFLAR-BUFJALLEN17-1`** Josh Allen touchdowns 1
- MODEL / MARKET: football 40.6% · market 52.5% · reconciled 48.9%
- SCRIPT ROBUSTNESS: P50 mass 23.8% · P55 mass 23.8% · P60 mass 0.0% · major-script floor 29.7% · failure mass 76.2% · win-contribution HHI 0.169

**`KXNFLTD-26OCT12BUFLAR-LARPNACUA12-1`** Puka Nacua touchdowns 1
- MODEL / MARKET: football 43.4% · market 53.5% · reconciled 50.1%
- SCRIPT ROBUSTNESS: P50 mass 19.5% · P55 mass 7.5% · P60 mass 0.0% · major-script floor 29.4% · failure mass 80.5% · win-contribution HHI 0.175

**`KXNFLTD-26OCT12BUFLAR-LARDADAMS17-1`** Davante Adams touchdowns 1
- MODEL / MARKET: football 36.6% · market 47.5% · reconciled 44.5%
- SCRIPT ROBUSTNESS: P50 mass 7.5% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 22.9% · failure mass 92.5% · win-contribution HHI 0.177

**`KXNFLTD-26OCT12BUFLAR-BUFTJOHNSON26-1`** Ty Johnson touchdowns 1
- MODEL / MARKET: football 17.5% · market 11.5% · reconciled 13.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 12.2% · failure mass 100.0% · win-contribution HHI 0.168

_409 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261012T010506Z.sim-1.1.0.scripts_v2.json.gz); 40 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Joshua Palmer (WR, BUF) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Terrance Ferguson (TE, LA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Ed Oliver (DT, BUF) — Out [high] — ruled out
- Myles Garrett (DE, LA) — Injured Reserve [single_source] — ruled out

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- DJ Moore (WR, BUF) — Questionable [high]
- Dee Alford (CB, BUF) — Questionable [high]
- Landon Jackson (DE, BUF) — Questionable [high]
- Quentin Lake (S, LA) — Questionable [single_source]
- Te'Cory Couch (CB, BUF) — Questionable [high]

### WEATHER

roof is dome -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261012T010506Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 65 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Josh Allen | BUF | attempts | 31.8 | 32.0 | 27.0 | 37.0 | 19.0 | 45.0 | 32.7 | 32.0 | 31.8 | 32.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| James Cook III | BUF | carries | 15.2 | 15.0 | 10.0 | 20.0 | 4.0 | 28.0 | 17.0 | 17.0 | 15.2 | 15.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | carries | 7.7 | 7.0 | 4.0 | 10.0 | 2.0 | 17.0 | 7.8 | 8.0 | 7.7 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | completions | 20.4 | 20.0 | 17.0 | 24.0 | 11.0 | 30.0 | 21.1 | 21.0 | 20.4 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.7 | 2.0 | 1.7 | 2.0 | 0.00 | 0.97 | 1 | PRICED |
| Josh Allen | BUF | passing_yards | 218.5 | 213.0 | 167.0 | 267.0 | 103.0 | 349.0 | 250.1 | 245.0 | 250.1 | 244.0 | 0.00 | 0.97 | 9 | PRICED |
| Khalil Shakir | BUF | receiving_yards | 47.0 | 39.0 | 19.0 | 67.0 | 0.0 | 118.0 | 51.4 | 43.0 | 51.4 | 43.0 | 0.00 | 0.98 | 11 | PRICED |
| Dalton Kincaid | BUF | receiving_yards | 41.6 | 32.0 | 12.0 | 61.0 | 0.0 | 117.0 | 60.9 | 53.0 | 60.9 | 47.0 | 0.00 | 0.98 | 11 | PRICED |

_8 of 65 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 65 of 109 listed player/stat groups simulated and exposed, 44 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT12BUFLAR-BUFJALLEN17-5` | Josh Allen | 5.0 | 0.86 | 0.88 | 0.28 | -0.577 |
| `KXNFLREC-26OCT12BUFLAR-BUFDKINCAID86-3` | Dalton Kincaid | 3.0 | 0.78 | 0.80 | 0.23 | -0.544 |
| `KXNFLREC-26OCT12BUFLAR-BUFDKINCAID86-2` | Dalton Kincaid | 2.0 | 0.94 | 0.94 | 0.40 | -0.538 |
| `KXNFLREC-26OCT12BUFLAR-BUFJPALMER5-2` | Joshua Palmer | 2.0 | 0.53 | 0.54 | 0.00 | -0.527 |
| `KXNFLRECYDS-26OCT12BUFLAR-BUFJPALMER5-20` | Joshua Palmer | 20.0 | 0.53 | 0.55 | 0.00 | -0.527 |
| `KXNFLREC-26OCT12BUFLAR-BUFDKINCAID86-4` | Dalton Kincaid | 4.0 | 0.65 | 0.65 | 0.13 | -0.514 |

_Ranked 427 tradable markets; 7 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Joshua Palmer (WR, BUF) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Terrance Ferguson (TE, LA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (DJ Moore (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLFFPTS-26OCT12BUFLAR-BUFKCOLEMAN0-9P7 moved -0.140 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.577 on KXNFLRSHATT-26OCT12BUFLAR-BUFJALLEN17-5 (Josh Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.544 on KXNFLREC-26OCT12BUFLAR-BUFDKINCAID86-3 (Dalton Kincaid). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT12BUFLAR-BUFDKINCAID86-2 sits at a market price of 0.94 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_05_BUF_LA.md`_


---

## HOW TO USE THIS PACKET

1. Handicap each game independently. The model's ranked disagreements are an input, not a shortlist.
2. For any thesis you form, check **BEST EXPRESSIONS** before choosing a contract — the largest disagreement is rarely the best payout for the risk.
3. Check **CORRELATION GROUPS** before sizing more than one position in a game.
4. Record every serious decision, including passes, via the recommendation ledger (`scripts/handicap/validate_recommendations.py`, then commit to the `handicap-data` branch).