# NFL HANDICAP PACKET — 2026 Week 7

- run id: `20261024T204558Z`  ·  packet sha: `2f9b48ffb96dd5072bf4`
- built at: 2026-10-24T20:45:58.376584+00:00  (all timestamps UTC)
- ledger: `20261024T201739Z.shadow-0.4.0.observations.jsonl.gz`  ·  model: `shadow-0.4.0`
- context captures: ['20261024T161757Z', '20261024T201410Z']
- team-profile basis: **current_season**
- **REAL-MONEY STATUS: NOT VALIDATED -- this packet recommends nothing and authorises nothing**
- **SIMULATION FRESHNESS: SIM_CURRENT** — run `20261024T201739Z` (RUN_NFL_FROZEN_BUNDLE), lag 0.0m vs target <= 180.0m; the simulation priced this packet's own board

> This packet contains no recommendations. Every model-vs-market number is a *disagreement*, which is not an edge. The model has been shown redundant to the closing market on player props and behind it on game outcomes; it is here as structure and context, not as a superior forecast.

## SLATE SUMMARY

- games: **14**
- markets listed this slate: **10398**, model-supported: **5023**
- ledger support states (all weeks): `{'UNSUPPORTED_MODEL': 15265, 'UNSUPPORTED_RULES': 5489, 'SUPPORTED': 5577, 'UNSUPPORTED_IDENTITY': 111, 'POST_KICKOFF_EXCLUDED': 68677}`

### FULL-BOARD COVERAGE

_RUN NFL examines every executable Kalshi contract for every requested unstarted NFL game. UNSUPPORTED_MODEL is a statement about one model, never a reason to hide a contract. Every listed contract terminates in exactly one analysis state, in one of four buckets: A validated model view, B coherent/Shadow research view, C manual handicap from the packet's own football and context data, D explicit PASS with a named reason._

| bucket | contracts | meaning |
|---|---|---|
| **A** | 5023 | validated/production model view available |
| **B** | 2678 | coherent / Shadow research model view available |
| **C** | 1644 | no automated pricing authority; handicap from the football and context data in this packet |
| **D** | 164 | cannot defensibly price -- explicit PASS / RESEARCH REQUIRED, with a reason |
| **-** | 889 | outside the pregame window (kickoff has passed) |
| **!** | 0 | INVARIANT VIOLATION -- a listed contract with no analysis state |

- listed: **10398** · executable books: **8925**
- incumbent priced: **5023** · coherent simulation: **0** · Shadow v2 research: **2678**
- manual handicap required: **1644** · research required: **52**
- rules blocked: **5** · identity blocked: **107** · non-football: **0**
- post-kickoff (stale): **889**
- **silently omitted: 0** — this must be 0.

| family / period | listed | executable | incumbent priced | coherent sim | shadow v2 | manual research | research required | rules blocked | identity blocked | non football | post kickoff | silently omitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLAYER_STAT/FULL | 5054 | 4570 | 4014 | 0 | 93 | 350 | 0 | 0 | 107 | 0 | 490 | 0 |
| FIRST_TD_TEAM/FULL | 405 | 81 | 0 | 0 | 0 | 376 | 0 | 1 | 0 | 0 | 28 | 0 |
| TEAM_TOTAL/FULL | 385 | 383 | 355 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 | 0 |
| FIRST_TD_SCORER/FULL | 364 | 364 | 0 | 0 | 0 | 337 | 0 | 3 | 0 | 0 | 24 | 0 |
| SPREAD/FULL | 355 | 355 | 329 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 26 | 0 |
| TEAM_TOTAL/1H | 308 | 300 | 0 | 0 | 287 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| TEAM_STAT/FULL | 280 | 20 | 0 | 0 | 0 | 260 | 0 | 0 | 0 | 0 | 20 | 0 |
| TOTAL/FULL | 268 | 268 | 247 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| SPREAD/1H | 213 | 213 | 0 | 0 | 196 | 0 | 0 | 0 | 0 | 0 | 17 | 0 |
| SPREAD/2H | 211 | 210 | 0 | 0 | 196 | 0 | 0 | 0 | 0 | 0 | 15 | 0 |
| RACE_TO_N/FULL | 210 | 86 | 0 | 0 | 0 | 195 | 0 | 0 | 0 | 0 | 15 | 0 |
| TOTAL/1H | 190 | 190 | 0 | 0 | 176 | 0 | 0 | 0 | 0 | 0 | 14 | 0 |
| TOTAL/2H | 190 | 178 | 0 | 0 | 176 | 0 | 0 | 0 | 0 | 0 | 14 | 0 |
| SPREAD/4Q | 153 | 143 | 0 | 0 | 142 | 0 | 0 | 0 | 0 | 0 | 11 | 0 |
| SPREAD/2Q | 148 | 148 | 0 | 0 | 135 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |
| GAME_PLAYER_LEADER/FULL | 146 | 72 | 0 | 0 | 0 | 126 | 0 | 1 | 0 | 0 | 19 | 0 |
| SPREAD/3Q | 145 | 145 | 0 | 0 | 132 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |
| SPREAD/1Q | 141 | 141 | 0 | 0 | 131 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/1Q | 140 | 140 | 0 | 0 | 130 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/2Q | 140 | 127 | 0 | 0 | 130 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/3Q | 140 | 135 | 0 | 0 | 130 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/4Q | 140 | 110 | 0 | 0 | 130 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| HALF_FULL_RESULT/1H | 126 | 126 | 0 | 0 | 117 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| WIN_MARGIN_BUCKET/FULL | 98 | 95 | 0 | 0 | 91 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| BOTH_TEAMS_SCORE_N/FULL | 56 | 22 | 52 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| GAME_EVENT/FULL | 56 | 46 | 0 | 0 | 0 | 0 | 52 | 0 | 0 | 0 | 4 | 0 |
| PERIOD_WINNER/1H | 42 | 42 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/1Q | 42 | 42 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2H | 42 | 33 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2Q | 42 | 41 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/3Q | 42 | 33 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/4Q | 42 | 31 | 0 | 0 | 39 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| GAME_WINNER/FULL | 28 | 28 | 26 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| BOTH_TEAMS_SCORE/1Q | 14 | 4 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/2Q | 14 | 1 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/3Q | 14 | 1 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/4Q | 14 | 1 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

_A Shadow v2 or coherent-simulation projection is RESEARCH. It is not validated, it is never mixed into the incumbent's probability or its disagreement ranking, and it reaches no recommendation, staking or preflight path._

**Skill players ruled OUT (40)**

- Case Keenum (QB, CHI) — Out · 2026_07_NE_CHI
- Kyle Monangai (RB, CHI) — Out · 2026_07_NE_CHI
- Cole Kmet (TE, CHI) — Injured Reserve · 2026_07_NE_CHI
- Behren Morton (QB, NE) — Out · 2026_07_NE_CHI
- Romeo Doubs (WR, NE) — Injured Reserve · 2026_07_NE_CHI
- Jordyn Tyson (WR, NO) — Injured Reserve · 2026_07_PIT_NO
- Ben Skowronek (WR, PIT) — Out · 2026_07_PIT_NO
- Lamar Jackson (QB, BAL) — Out · 2026_07_CIN_BAL
- Tanner Hudson (TE, CIN) — Injured Reserve · 2026_07_CIN_BAL
- Dillon Gabriel (QB, CLE) — Injured Reserve · 2026_07_CLE_TEN
- Anthony Gould (WR, IND) — Out · 2026_07_IND_MIN
- Tyler Warren (TE, IND) — Out · 2026_07_IND_MIN
- Alec Pierce (WR, IND) — Injured Reserve · 2026_07_IND_MIN
- Jordan Mason (RB, MIN) — Injured Reserve · 2026_07_IND_MIN
- Josh Oliver (TE, MIN) — Injured Reserve · 2026_07_IND_MIN

**New or changed since the previous capture (26)** — the most decision-relevant section on the page

- Cedric Tillman (WR, NO): **Active** (new record) · 2026_07_PIT_NO
- Brandon Johnson (WR, PIT): **Active** (new record) · 2026_07_PIT_NO
- Brandon Smith (WR, PIT): **Active** (new record) · 2026_07_PIT_NO
- Lamar Jackson (QB, BAL): **Out** (was Questionable) · 2026_07_CIN_BAL
- Dylan Sampson (RB, CLE): **Active** (was Injured Reserve) · 2026_07_CLE_TEN
- Grant Delpit (S, CLE): **Active** (was Questionable) · 2026_07_CLE_TEN
- Teven Jenkins (G, CLE): **Injured Reserve** (was Out) · 2026_07_CLE_TEN
- K.J. Osborn (WR, TEN): **Active** (new record) · 2026_07_CLE_TEN
- Kalel Mullings (RB, TEN): **Active** (new record) · 2026_07_CLE_TEN
- Timmy Horne (DT, TEN): **Active** (new record) · 2026_07_CLE_TEN
- Kyle Louis (LB, MIA): **Active** (was Injured Reserve) · 2026_07_MIA_NYJ
- Zane Gonzalez (PK, MIA): **Active** (new record) · 2026_07_MIA_NYJ
- Kiko Mauigoa (LB, NYJ): **Injured Reserve** (was Out) · 2026_07_MIA_NYJ
- Jevon Holland (S, NYG): **Out** (was Questionable) · 2026_07_NYG_HOU
- Theo Johnson (TE, NYG): **Out** (was Doubtful) · 2026_07_NYG_HOU

**Largest market moves since first capture**

| ticker | game | family | move |
|---|---|---|---|
| `KXNFLRECYDS-26OCT22NECHI-NERSTEVENSON38-70` | 2026_07_NE_CHI | PLAYER_STAT | +0.955 |
| `KXNFLRECYDS-26OCT22NECHI-CHILBURDEN10-130` | 2026_07_NE_CHI | PLAYER_STAT | +0.940 |
| `KXNFLRECYDS-26OCT22NECHI-NERSTEVENSON38-60` | 2026_07_NE_CHI | PLAYER_STAT | +0.935 |
| `KXNFLRECYDS-26OCT22NECHI-CHILBURDEN10-120` | 2026_07_NE_CHI | PLAYER_STAT | +0.930 |
| `KXNFLRECYDS-26OCT22NECHI-NEERARIDON82-50` | 2026_07_NE_CHI | PLAYER_STAT | +0.920 |
| `KXNFLREC-26OCT22NECHI-NEHHENRY85-6` | 2026_07_NE_CHI | PLAYER_STAT | +0.910 |
| `KXNFLRECYDS-26OCT22NECHI-CHILBURDEN10-110` | 2026_07_NE_CHI | PLAYER_STAT | +0.910 |
| `KXNFLRECYDS-26OCT22NECHI-NEERARIDON82-40` | 2026_07_NE_CHI | PLAYER_STAT | +0.890 |
| `KXNFLTEAMFIRSTTD-26OCT22NECHI-NE-DMAYE10` | 2026_07_NE_CHI | FIRST_TD_TEAM | +0.890 |
| `KXNFLRECYDS-26OCT22NECHI-NERSTEVENSON38-50` | 2026_07_NE_CHI | PLAYER_STAT | +0.885 |

**Largest model/market disagreements** — DISAGREEMENT ONLY, REQUIRES HANDICAP

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT25NYGHOU-NYGILIKELY9-3` | Isaiah Likely | 3.0 | 0.89 | 0.91 | 0.18 | -0.708 |
| `KXNFLREC-26OCT25PITNO-PITGBERNARD17-3` | Germie Bernard | 3.0 | 0.86 | 0.88 | 0.18 | -0.677 |
| `KXNFLRECYDS-26OCT25INDMIN-INDWMALLORY86-10` | Will Mallory | 10.0 | 0.68 | 0.69 | 0.01 | -0.673 |
| `KXNFLRSHYDS-26OCT25MIANYJ-MIAOGORDON0-25` | Ollie Gordon II | 25.0 | 0.86 | 0.87 | 0.19 | -0.671 |
| `KXNFLRECYDS-26OCT25NYGHOU-NYGILIKELY9-25` | Isaiah Likely | 25.0 | 0.82 | 0.84 | 0.16 | -0.667 |
| `KXNFLRSHYDS-26OCT25MIANYJ-MIAOGORDON0-30` | Ollie Gordon II | 30.0 | 0.81 | 0.82 | 0.15 | -0.667 |
| `KXNFLRECYDS-26OCT25NYGHOU-NYGILIKELY9-20` | Isaiah Likely | 20.0 | 0.87 | 0.88 | 0.20 | -0.666 |
| `KXNFLREC-26OCT26DALPHI-DALCLAMB88-5` | CeeDee Lamb | 5.0 | 0.82 | 0.85 | 0.16 | -0.664 |
| `KXNFLREC-26OCT25NYGHOU-NYGILIKELY9-4` | Isaiah Likely | 4.0 | 0.77 | 0.78 | 0.11 | -0.661 |
| `KXNFLREC-26OCT25GBDET-GBSWILLIAMS83-2` | Savion Williams | 2.0 | 0.67 | 0.70 | 0.01 | -0.660 |
| `KXNFLRECYDS-26OCT25NYGHOU-NYGILIKELY9-30` | Isaiah Likely | 30.0 | 0.77 | 0.78 | 0.12 | -0.641 |
| `KXNFLREC-26OCT25GBDET-GBMGOLDEN0-3` | Matthew Golden | 3.0 | 0.86 | 0.90 | 0.22 | -0.641 |

**Highest-liquidity markets**

- `KXNFLGAME-26OCT22NECHI-NE` (GAME_WINNER, 2026_07_NE_CHI): volume 29941665, OI 17812475
- `KXNFLGAME-26OCT22NECHI-CHI` (GAME_WINNER, 2026_07_NE_CHI): volume 14076084, OI 7528727
- `KXNFLTOTAL-26OCT22NECHI-51` (TOTAL, 2026_07_NE_CHI): volume 8073493, OI 2793975
- `KXNFLSPREAD-26OCT22NECHI-CHI3` (SPREAD, 2026_07_NE_CHI): volume 3784201, OI 2890616
- `KXNFLGAME-26OCT25CINBAL-CIN` (GAME_WINNER, 2026_07_CIN_BAL): volume 2193020, OI 1795420
- `KXNFLSPREAD-26OCT22NECHI-CHI4` (SPREAD, 2026_07_NE_CHI): volume 1864718, OI 1216916
- `KXNFLGAME-26OCT25KCSEA-KC` (GAME_WINNER, 2026_07_KC_SEA): volume 1493061, OI 1313070
- `KXNFLGAME-26OCT25NYGHOU-NYG` (GAME_WINNER, 2026_07_NYG_HOU): volume 1348505, OI 1197207

**BLOCKING data issues**

- 2026_07_NE_CHI: `GAME_STARTED` — kickoff has passed; this is not a pregame packet

### GAME PRIORITY FOR HANDICAP

_Priority ranks where deeper review may be most useful. It is NOT a bet ranking and carries no expectation that these games contain value._

| # | game | score | why |
|---|---|---|---|
| 1 | 2026_07_KC_SEA | 20.5 | 4 new/changed injury records; 4 skill players ruled out (role change); forecast changed; largest market move 0.415; raw incumbent disagreement 0.597 (NOT scored: unvalidated); 328 supported player-prop rungs |
| 2 | 2026_07_DAL_PHI | 19.24 | 3 new/changed injury records; 5 skill players ruled out (role change); forecast changed; largest market move 0.320; largest reconciled simulation disagreement 0.074; raw incumbent disagreement 0.664 (NOT scored: unvalidated); 241 supported player-prop rungs |
| 3 | 2026_07_SF_ATL | 17.95 | 2 new/changed injury records; 5 skill players ruled out (role change); forecast changed; largest market move 0.175; largest reconciled simulation disagreement 0.145; raw incumbent disagreement 0.605 (NOT scored: unvalidated); 319 supported player-prop rungs |
| 4 | 2026_07_NYG_HOU | 15.87 | 2 new/changed injury records; 3 skill players ruled out (role change); forecast changed; largest market move 0.305; largest reconciled simulation disagreement 0.087; raw incumbent disagreement 0.708 (NOT scored: unvalidated); 353 supported player-prop rungs |
| 5 | 2026_07_CLE_TEN | 15.77 | 6 new/changed injury records; 1 skill players ruled out (role change); largest market move 0.155; largest reconciled simulation disagreement 0.077; raw incumbent disagreement 0.616 (NOT scored: unvalidated); 299 supported player-prop rungs |
| 6 | 2026_07_PIT_NO | 15.3 | 3 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.150; largest reconciled simulation disagreement 0.080; raw incumbent disagreement 0.677 (NOT scored: unvalidated); 349 supported player-prop rungs |
| 7 | 2026_07_LA_LV | 14.99 | 1 new/changed injury records; 4 skill players ruled out (role change); largest market move 0.390; largest reconciled simulation disagreement 0.149; raw incumbent disagreement 0.586 (NOT scored: unvalidated); 318 supported player-prop rungs |
| 8 | 2026_07_MIA_NYJ | 13.65 | 3 new/changed injury records; forecast changed; largest market move 0.185; largest reconciled simulation disagreement 0.115; raw incumbent disagreement 0.671 (NOT scored: unvalidated); 291 supported player-prop rungs |
| 9 | 2026_07_IND_MIN | 12.65 | 5 skill players ruled out (role change); largest market move 0.155; largest reconciled simulation disagreement 0.115; raw incumbent disagreement 0.673 (NOT scored: unvalidated); 305 supported player-prop rungs |
| 10 | 2026_07_CIN_BAL | 12.54 | 1 new/changed injury records; 2 skill players ruled out (role change); forecast changed; largest market move 0.215; largest reconciled simulation disagreement 0.104; raw incumbent disagreement 0.495 (NOT scored: unvalidated); 234 supported player-prop rungs |
| 11 | 2026_07_GB_DET | 11.6 | 1 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.145; largest reconciled simulation disagreement 0.110; raw incumbent disagreement 0.660 (NOT scored: unvalidated); 322 supported player-prop rungs |
| 12 | 2026_07_DEN_ARI | 11.0 | 3 skill players ruled out (role change); forecast changed; largest market move 0.300; raw incumbent disagreement 0.579 (NOT scored: unvalidated); 340 supported player-prop rungs |
| 13 | 2026_07_TB_CAR | 10.01 | 2 skill players ruled out (role change); largest market move 0.140; largest reconciled simulation disagreement 0.151; raw incumbent disagreement 0.589 (NOT scored: unvalidated); 315 supported player-prop rungs |
| 14 | 2026_07_NE_CHI | 10.0 | 5 skill players ruled out (role change); largest market move 0.955; BLOCKING data issue -- review before trusting anything here |

> Each game below is summarised. Full detail -- complete market board, every player ladder, all best-expression groups -- is in that game's own file under `games/`.


---

## NE @ CHI — `2026_07_NE_CHI`

- kickoff: 2026-10-23T00:15:00+00:00 (-2671 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 889 listed across 16 families — 0 supported, 23 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 889/889 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -6.36 | -- |
| total | 51.86 | -- |
| score | CHI 29.1 – NE 22.7 | CHI -- – NE -- |
| win prob CHI | 84.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -5.50 / total 34.00 · **2H** spread 0.30 / total 14.09 · **1Q** spread -9.00 / total 9.50 · **2Q** spread 5.00 / total 23.50 · **3Q** spread 0.50 / total 14.50 · **4Q** spread 0.80 / total --

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -6.36 · total 51.86
- move `KXNFL1QSPREAD-26OCT22NECHI-CHI8` +0.880

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261024T201739Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (6; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 12 market(s), e.g. KXNFL4QSPREAD-26OCT22NECHI-NE4, KXNFLPASSATT-26OCT22NECHI-NEDMAYE10-32
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 6 market(s), e.g. KXNFLGAME-26OCT22NECHI-NE, KXNFLTEAMTOTAL-26OCT22NECHI-NE29
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 201 market(s), e.g. KXNFL1HFT-26OCT22NECHI-CHINE, KXNFL2H-26OCT22NECHI-CHI
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 36 market(s), e.g. KXNFL1HFT-26OCT22NECHI-CHICHI, KXNFLFFPTS-26OCT22NECHI-CHIRODUNZE15-10P8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 162 market(s), e.g. KXNFLFFPTS-26OCT22NECHI-NENEDST-6P3, KXNFLFFPTS-26OCT22NECHI-NEDDOUGLAS3-8P5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 191 market(s), e.g. KXNFLFG-26OCT22NECHI-NE4, KXNFLFG-26OCT22NECHI-NE3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261024T201739Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (18)**

- Behren Morton (QB, NE) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Case Keenum (QB, CHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Cole Kmet (TE, CHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Kyle Monangai (RB, CHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Romeo Doubs (WR, NE) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Alijah Vera-Tucker (G, NE) — Injured Reserve [high] — ruled out
- Ben Brown (C, NE) — Out [single_source] — ruled out
- Jordan McFadden (G, CHI) — Out [high] — ruled out
- _...and 10 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Malik Muhammad II (CB, CHI) — Questionable [conflicting]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 114 listed player/stat groups simulated and exposed, 114 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Case Keenum (QB, CHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Kyle Monangai (RB, CHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLRECYDS-26OCT22NECHI-NERSTEVENSON38-70 moved +0.955 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_NE_CHI.md`_


---

## PIT @ NO — `2026_07_PIT_NO`

- kickoff: 2026-10-25T13:30:00+00:00 (1004 minutes away) · state **PREGAME**
- venue: Stade de France · roof dome · surface sportturf
- markets: 779 listed across 16 families — 426 supported, 297 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.95 | 3.00 |
| total | 45.17 | 45.24 |
| score | NO 21.1 – PIT 24.1 | NO 21.1 – PIT 24.1 |
| win prob NO | 39.5% | 38.7% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.33 / total 22.50 · **2H** spread 0.96 / total 23.17 · **1Q** spread 0.90 / total 7.97 · **2Q** spread 1.16 / total 13.31 · **3Q** spread -0.02 / total 8.71 · **4Q** spread -0.01 / total 12.86

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.95 · total 45.17

**Game environment** (simulation, mean and middle 50%) — home margin -2.5 (-10.0–5.0) · total 46.6 (38.0–55.0) · P(one score) 53.7% · P(17+ blowout) 18.0% · P(total 10+ over centre) 23.7%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NO | 64.4 (59.0–70.0) | 35.0 (30.0–40.0) | 24.6 (20.0–29.0) | 39.1 (34.0–44.0) | 0.608 (0.541–0.675) | 0.507 / 0.682 |
| PIT | 62.9 (57.0–69.0) | 35.0 (30.0–40.0) | 23.5 (19.0–28.0) | 38.5 (33.0–44.0) | 0.612 (0.545–0.680) | 0.528 / 0.702 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NO | 00-0038551 | RB | 1.7 (0.0–2.0) | 10.1 (5.0–14.0) | 4.9% | 41.2% | MEDIUM |
| NO | 00-0033906 | RB | 3.4 (1.0–5.0) | 8.2 (4.0–12.0) | 10.1% | 33.2% | MEDIUM |
| NO | 00-0037239 | WR | 8.8 (5.0–12.0) | 0.1 (0.0–0.0) | 26.3% | 0.2% | MEDIUM |
| NO | 00-0039424 | WR | 6.0 (3.0–8.0) | 0.1 (0.0–0.0) | 17.9% | 0.6% | HIGH |
| PIT | 00-0037228 | RB | 4.9 (2.0–7.0) | 13.9 (9.0–19.0) | 14.8% | 59.0% | MEDIUM |
| PIT | 00-0035640 | WR | 8.7 (5.0–12.0) | 0.2 (0.0–0.0) | 26.5% | 0.7% | MEDIUM |
| PIT | 00-0036139 | RB | 2.6 (0.0–4.0) | 5.7 (0.0–9.0) | 7.8% | 24.1% | HIGH |
| PIT | 00-0041489 | WR | 6.2 (3.0–9.0) | 0.3 (0.0–0.0) | 18.9% | 1.1% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 6 market(s), e.g. KXNFLRSHYDS-26OCT25PITNO-NOAKAMARA41-30, KXNFLRSHYDS-26OCT25PITNO-NOAKAMARA41-25
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 74 market(s), e.g. KXNFL1HFT-26OCT25PITNO-NONO, KXNFLPASSYDS-26OCT25PITNO-NOTSHOUGH6-275
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26OCT25PITNO-PIT11, KXNFLSPREAD-26OCT25PITNO-NO6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLGAME-26OCT25PITNO-PIT, KXNFLTEAMTOTAL-26OCT25PITNO-PIT22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 222 market(s), e.g. KXNFL1H-26OCT25PITNO-TIE, KXNFL1HFT-26OCT25PITNO-NOPIT
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 25 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25PITNO-PIT3, KXNFL1HTOTAL-26OCT25PITNO-11

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.5%  _(final margin within one score (8 points) either way; total within 10 of the centre 45.1667 (median favourite-oriented margin +1, median total 45))_
2. favourite controls / normal scoring — 15.6%  _(PIT (favourite) wins by more than one score; total within 10 of the centre 45.1667 (median favourite-oriented margin +15, median total 46))_
3. competitive / high scoring — 11.8%  _(final margin within one score (8 points) either way; total 55.1667+ (centre 45.1667) (median favourite-oriented margin +1, median total 63))_
4. competitive / low scoring — 10.4%  _(final margin within one score (8 points) either way; total 35.1667 or fewer (centre 45.1667) (median favourite-oriented margin +2, median total 31))_
5. underdog controls / normal scoring — 8.7%  _(NO (underdog) wins by more than one score; total within 10 of the centre 45.1667 (median favourite-oriented margin -16, median total 45))_
   Other — 22.0%

Marginal events (overlapping): one_score 53.7% · blowout_17 18.0% · favorite_wins 60.8% · favorite_controls 30.0% · upset 39.0% · shootout 23.7% · low_scoring 20.4% · low_possession 6.5% · high_volume_passing 13.5% · run_heavy_control 12.1%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): no point-in-time forecast attached._

**`KXNFLTD-26OCT25PITNO-PITARODGERS8-1`** Aaron Rodgers touchdowns 1
- MODEL / MARKET: football 9.4% · market 6.5% · reconciled 14.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.5% · failure mass 100.0% · win-contribution HHI 0.188

**`KXNFLTD-26OCT25PITNO-NOAKAMARA41-1`** Alvin Kamara touchdowns 1
- MODEL / MARKET: football 30.0% · market 21.5% · reconciled 24.7%
- SCRIPT ROBUSTNESS: P50 mass 4.2% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 19.5% · failure mass 95.8% · win-contribution HHI 0.180

**`KXNFLTD-26OCT25PITNO-NOJJOHNSON83-1`** Juwan Johnson touchdowns 1
- MODEL / MARKET: football 19.4% · market 23.5% · reconciled 22.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 12.3% · failure mass 100.0% · win-contribution HHI 0.176

**`KXNFLTD-26OCT25PITNO-PITPFREIERMUTH88-2`** Pat Freiermuth touchdowns 2
- MODEL / MARKET: football 5.2% · market 3.5% · reconciled 4.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.9% · failure mass 100.0% · win-contribution HHI 0.201

_416 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 45 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Ben Skowronek (WR, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jordyn Tyson (WR, NO) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Brandin Echols (CB, PIT) — Out [high] — ruled out
- Sebastian Joseph-Day (DT, PIT) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Rico Dowdle (RB, PIT) — Questionable [high]
- Cesar Ruiz (G, NO) — Questionable [high]
- Nathan Shepherd (DT, NO) — Questionable [high]

### WEATHER

played at Stade de France, not NO's home stadium -- no forecast for this venue is captured, and the home stadium's forecast is not shown (scheduled stadium id PAR00 (Stade de France) is not NO's home stadium NOR00 (Caesars Superdome))

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 63 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tyler Shough | NO | attempts | 33.6 | 34.0 | 29.0 | 39.0 | 20.0 | 47.0 | 36.4 | 36.0 | 33.6 | 34.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kendre Miller | NO | carries | 10.1 | 9.0 | 5.0 | 14.0 | 1.0 | 22.0 | 11.9 | 12.0 | 10.1 | 9.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Shough | NO | carries | 3.8 | 3.0 | 2.0 | 5.0 | 0.0 | 10.0 | 3.5 | 3.0 | 3.8 | 3.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Shough | NO | completions | 21.3 | 21.0 | 17.0 | 25.0 | 12.0 | 31.0 | 23.1 | 23.0 | 21.3 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Shough | NO | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Tyler Shough | NO | passing_yards | 225.0 | 221.0 | 173.0 | 273.0 | 105.0 | 358.0 | 234.5 | 229.0 | 234.5 | 231.0 | 0.00 | 0.98 | 9 | PRICED |
| Chris Olave | NO | receiving_yards | 71.5 | 63.0 | 34.0 | 100.0 | 4.0 | 168.0 | 81.7 | 74.0 | 81.6 | 72.0 | 0.00 | 0.98 | 13 | PRICED |
| Devaughn Vele | NO | receiving_yards | 44.0 | 35.0 | 15.0 | 64.0 | 0.0 | 119.0 | 48.5 | 41.0 | 48.5 | 39.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 63 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 63 of 102 listed player/stat groups simulated and exposed, 39 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT25PITNO-PITGBERNARD17-3` | Germie Bernard | 3.0 | 0.86 | 0.88 | 0.18 | -0.677 |
| `KXNFLREC-26OCT25PITNO-PITGBERNARD17-4` | Germie Bernard | 4.0 | 0.73 | 0.74 | 0.11 | -0.625 |
| `KXNFLRSHATT-26OCT25PITNO-PITJWARREN30-11` | Jaylen Warren | 11.0 | 0.80 | 0.82 | 0.25 | -0.545 |
| `KXNFLRECYDS-26OCT25PITNO-PITGBERNARD17-25` | Germie Bernard | 25.0 | 0.82 | 0.83 | 0.29 | -0.536 |
| `KXNFLREC-26OCT25PITNO-PITJWARREN30-2` | Jaylen Warren | 2.0 | 0.82 | 0.84 | 0.31 | -0.513 |
| `KXNFLREC-26OCT25PITNO-PITGBERNARD17-5` | Germie Bernard | 5.0 | 0.57 | 0.58 | 0.07 | -0.509 |

_Ranked 422 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jordyn Tyson (WR, NO) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Ben Skowronek (WR, PIT) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Rico Dowdle (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL1HFT-26OCT25PITNO-PITPIT moved +0.150 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.677 on KXNFLREC-26OCT25PITNO-PITGBERNARD17-3 (Germie Bernard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.625 on KXNFLREC-26OCT25PITNO-PITGBERNARD17-4 (Germie Bernard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT25PITNO-NODVELE14-2 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_PIT_NO.md`_


---

## CIN @ BAL — `2026_07_CIN_BAL`

- kickoff: 2026-10-25T17:00:00+00:00 (1214 minutes away) · state **PREGAME**
- venue: M&T Bank Stadium · roof outdoors · surface grass
- markets: 652 listed across 15 families — 311 supported, 284 no model, 48 rules unresolved, 9 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 9 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.56 | 2.05 |
| total | 47.55 | 47.18 |
| score | BAL 22.5 – CIN 25.1 | BAL 22.6 – CIN 24.6 |
| win prob BAL | 42.5% | 42.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.32 / total 23.90 · **2H** spread 1.09 / total 23.88 · **1Q** spread 0.40 / total 8.66 · **2Q** spread 0.62 / total 14.21 · **3Q** spread 0.56 / total 9.00 · **4Q** spread 0.83 / total 13.75

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.56 · total 47.55
- move `KXNFLTOTAL-26OCT25CINBAL-50` -0.205
- move `KXNFLSPREAD-26OCT25CINBAL-CIN3` +0.195
- move `KXNFLSPREAD-26OCT25CINBAL-CIN2` +0.195
- move `KXNFLTEAMTOTAL-26OCT25CINBAL-BAL27` -0.195

**Game environment** (simulation, mean and middle 50%) — home margin -2.4 (-10.0–5.0) · total 48.7 (40.0–57.0) · P(one score) 54.3% · P(17+ blowout) 18.2% · P(total 10+ over centre) 24.0%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| BAL | 61.7 (56.0–67.0) | 30.2 (25.0–35.0) | 25.1 (20.0–30.0) | 36.0 (31.0–41.0) | 0.585 (0.519–0.652) | 0.486 / 0.654 |
| CIN | 63.1 (57.0–69.0) | 37.0 (32.0–42.0) | 21.9 (17.0–26.0) | 40.3 (35.0–46.0) | 0.639 (0.573–0.706) | 0.556 / 0.730 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| BAL | 00-0032764 | RB | 1.4 (0.0–2.0) | 19.5 (14.0–24.0) | 4.9% | 78.0% | MEDIUM |
| BAL | 00-0039064 | WR | 7.1 (4.0–10.0) | 0.8 (0.0–0.0) | 24.3% | 3.1% | HIGH |
| BAL | 00-0035993 | QB | 0.5 (0.0–1.0) | 5.0 (3.0–6.0) | 1.7% | 5.5% | HIGH |
| BAL | 00-0034753 | TE | 4.4 (2.0–6.0) | 0.1 (0.0–0.0) | 15.2% | 0.4% | HIGH |
| CIN | 00-0038597 | RB | 4.3 (2.0–6.0) | 17.2 (12.0–22.0) | 12.2% | 78.6% | MEDIUM |
| CIN | 00-0036900 | WR | 9.5 (6.0–13.0) | 0.0 (0.0–0.0) | 26.6% | 0.1% | MEDIUM |
| CIN | 00-0036410 | WR | 7.0 (4.0–10.0) | 0.1 (0.0–0.0) | 19.6% | 0.3% | HIGH |
| CIN | 00-0034829 | TE | 3.8 (1.0–6.0) | 0.1 (0.0–0.0) | 10.7% | 0.3% | HIGH |

**Historical research tags** (7; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 51 market(s), e.g. KXNFL1HFT-26OCT25CINBAL-CINCIN, KXNFL1HSPREAD-26OCT25CINBAL-CIN8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26OCT25CINBAL-CIN8, KXNFLSPREAD-26OCT25CINBAL-CIN15
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLTEAMTOTAL-26OCT25CINBAL-CIN22, KXNFLTEAMTOTAL-26OCT25CINBAL-CIN21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 195 market(s), e.g. KXNFL1H-26OCT25CINBAL-TIE, KXNFL1HFT-26OCT25CINBAL-TIECIN
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 31 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25CINBAL-CIN3, KXNFL1HTEAMTOTAL-26OCT25CINBAL-BAL3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 132 market(s), e.g. KXNFLLONGREC-26OCT25CINBAL-CINTHIGGINS5-23, KXNFLLONGREC-26OCT25CINBAL-CINMGESICKI88-13

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 32.0%  _(final margin within one score (8 points) either way; total within 10 of the centre 47.55 (median favourite-oriented margin +1, median total 47))_
2. favourite controls / normal scoring — 15.7%  _(CIN (favourite) wins by more than one score; total within 10 of the centre 47.55 (median favourite-oriented margin +15, median total 48))_
3. competitive / high scoring — 12.2%  _(final margin within one score (8 points) either way; total 57.55+ (centre 47.55) (median favourite-oriented margin +1, median total 65))_
4. competitive / low scoring — 10.2%  _(final margin within one score (8 points) either way; total 37.55 or fewer (centre 47.55) (median favourite-oriented margin +2, median total 33))_
5. underdog controls / normal scoring — 8.1%  _(BAL (underdog) wins by more than one score; total within 10 of the centre 47.55 (median favourite-oriented margin -16, median total 47))_
   Other — 21.9%

Marginal events (overlapping): one_score 54.3% · blowout_17 18.2% · favorite_wins 60.6% · favorite_controls 29.9% · upset 39.2% · shootout 24.0% · low_scoring 20.2% · low_possession 11.3% · high_volume_passing 7.4% · run_heavy_control 10.0%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 3.10 mph, gusts 4.90, precip prob 0%, temp 63F, forecast retrieved 2026-10-24T20:14:10+00:00 (20.76 h before kickoff)._

**`KXNFLTD-26OCT25CINBAL-BALJCUEVAS85-1`** Josh Cuevas touchdowns 1
- MODEL / MARKET: football 7.9% · market 7.5% · reconciled 17.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.9% · failure mass 100.0% · win-contribution HHI 0.194

**`KXNFLTD-26OCT25CINBAL-BALDWALKER81-1`** Devontez Walker touchdowns 1
- MODEL / MARKET: football 8.8% · market 6.5% · reconciled 14.4%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.8% · failure mass 100.0% · win-contribution HHI 0.180

**`KXNFLTD-26OCT25CINBAL-CINMTINSLEY84-1`** Mitchell Tinsley touchdowns 1
- MODEL / MARKET: football 8.6% · market 5.5% · reconciled 11.4%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.9% · failure mass 100.0% · win-contribution HHI 0.178

**`KXNFLTD-26OCT25CINBAL-BALDHENRY22-1`** Derrick Henry touchdowns 1
- MODEL / MARKET: football 53.4% · market 63.5% · reconciled 60.0%
- SCRIPT ROBUSTNESS: P50 mass 67.3% · P55 mass 59.9% · P60 mass 27.9% · major-script floor 36.8% · failure mass 32.7% · win-contribution HHI 0.182

_304 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 32 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- Lamar Jackson (QB, BAL) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Tanner Hudson (TE, CIN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jaylinn Hawkins (S, BAL) — Out [single_source] — ruled out
- Swayze Bozeman (LB, CIN) — Injured Reserve [high] — ruled out
- T.J. Tampa (CB, BAL) — Injured Reserve [single_source] — ruled out
- Tavius Robinson (LB, BAL) — Out [high] — ruled out

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Broderick Washington Jr. (DT, BAL) — Questionable [high]

### WEATHER

- Sunny · 66°F · wind 2 mph E · precip 0%
- forecast vintage 2026-10-24T20:14:12+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 64, 'wind': '2 mph', 'precipitation_probability': 0})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 48 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Derrick Henry | BAL | carries | 19.5 | 19.0 | 14.0 | 24.0 | 7.0 | 33.0 | 19.2 | 19.0 | 19.5 | 19.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Derrick Henry | BAL | receiving_yards | 8.3 | 0.0 | 0.0 | 12.0 | 0.0 | 37.0 | 11.5 | 6.0 | 11.6 | 1.0 | 0.00 | 0.97 | 7 | PRICED |
| Derrick Henry | BAL | receptions | 1.1 | 1.0 | 0.0 | 2.0 | 0.0 | 4.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Derrick Henry | BAL | rushing_yards | 93.3 | 87.0 | 58.0 | 122.0 | 22.0 | 187.0 | 89.9 | 83.0 | 89.9 | 84.0 | 0.00 | 0.97 | 14 | PRICED |
| Derrick Henry | BAL | touchdowns | 0.8 | 1.0 | 0.0 | 1.0 | 0.0 | 2.0 | 1.0 | 1.0 | 0.9 | 1.0 | 0.25 | 0.97 | 3 | PRICED |
| Zay Flowers | BAL | touchdowns | 0.4 | 0.0 | 0.0 | 1.0 | 0.0 | 2.0 | 0.4 | 0.0 | 0.4 | 0.0 | 0.25 | 0.97 | 3 | PRICED |
| Mark Andrews | BAL | touchdowns | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.3 | 0.0 | 0.3 | 0.0 | 0.25 | 0.97 | 3 | PRICED |
| Ja'Kobi Lane | BAL | touchdowns | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.2 | 0.0 | 0.2 | 0.0 | 0.25 | 0.97 | 2 | PRICED |

_8 of 48 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 48 of 79 listed player/stat groups simulated and exposed, 31 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT25CINBAL-BALDHENRY22-17` | Derrick Henry | 17.0 | 0.66 | 0.68 | 0.16 | -0.495 |
| `KXNFLREC-26OCT25CINBAL-CINTHIGGINS5-4` | Tee Higgins | 4.0 | 0.72 | 0.74 | 0.25 | -0.468 |
| `KXNFLREC-26OCT25CINBAL-CINTHIGGINS5-3` | Tee Higgins | 3.0 | 0.85 | 0.87 | 0.43 | -0.428 |
| `KXNFLREC-26OCT25CINBAL-CINJCHASE1-6` | Ja'Marr Chase | 6.0 | 0.72 | 0.73 | 0.29 | -0.426 |
| `KXNFLRSHATT-26OCT25CINBAL-CINSPERINE34-4` | Samaje Perine | 4.0 | 0.93 | 0.95 | 0.51 | -0.420 |
| `KXNFLREC-26OCT25CINBAL-CINJCHASE1-7` | Ja'Marr Chase | 7.0 | 0.58 | 0.60 | 0.17 | -0.411 |

_Ranked 308 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Lamar Jackson (QB, BAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Tanner Hudson (TE, CIN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
4. KXNFLFFPTS-26OCT25CINBAL-BALMANDREWS89-9P2 moved -0.215 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.495 on KXNFLRSHATT-26OCT25CINBAL-BALDHENRY22-17 (Derrick Henry). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.468 on KXNFLREC-26OCT25CINBAL-CINTHIGGINS5-4 (Tee Higgins). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRSHATT-26OCT25CINBAL-CINSPERINE34-4 sits at a market price of 0.93 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_CIN_BAL.md`_


---

## CLE @ TEN — `2026_07_CLE_TEN`

- kickoff: 2026-10-25T17:00:00+00:00 (1214 minutes away) · state **PREGAME**
- venue: Nissan Stadium · roof outdoors · surface grass
- markets: 727 listed across 16 families — 376 supported, 295 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.25 | 1.39 |
| total | 37.50 | 38.01 |
| score | TEN 17.6 – CLE 19.9 | TEN 18.3 – CLE 19.7 |
| win prob TEN | 45.5% | 45.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 0.98 / total 18.50 · **2H** spread 0.45 / total 19.00 · **1Q** spread 0.40 / total 7.42 · **2Q** spread 0.48 / total 10.50 · **3Q** spread 0.05 / total 7.61 · **4Q** spread -0.04 / total 10.14

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.25 · total 37.50
- move `KXNFL1HTEAMTOTAL-26OCT25CLETEN-TEN28` -0.110
- move `KXNFL1HTEAMTOTAL-26OCT25CLETEN-CLE28` -0.105
- move `KXNFL1HTEAMTOTAL-26OCT25CLETEN-TEN31` -0.095

**Game environment** (simulation, mean and middle 50%) — home margin -2.6 (-10.0–5.0) · total 38.8 (30.0–47.0) · P(one score) 53.6% · P(17+ blowout) 18.3% · P(total 10+ over centre) 23.7%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| TEN | 59.4 (54.0–65.0) | 30.8 (26.0–35.0) | 23.5 (19.0–28.0) | 35.2 (30.0–40.0) | 0.594 (0.527–0.661) | 0.490 / 0.662 |
| CLE | 60.7 (55.0–66.0) | 28.1 (24.0–32.0) | 24.9 (20.0–29.0) | 34.9 (30.0–40.0) | 0.576 (0.508–0.644) | 0.493 / 0.663 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| TEN | 00-0035261 | RB | 1.9 (0.0–3.0) | 12.2 (7.0–16.0) | 6.4% | 51.8% | MEDIUM |
| TEN | 00-0036924 | RB | 2.1 (0.0–3.0) | 6.2 (2.0–9.0) | 7.1% | 26.2% | HIGH |
| TEN | 00-0041438 | WR | 6.6 (4.0–9.0) | 0.0 (0.0–0.0) | 22.8% | 0.1% | HIGH |
| TEN | 00-0038117 | WR | 5.7 (3.0–8.0) | 0.1 (0.0–0.0) | 19.6% | 0.4% | HIGH |
| CLE | 00-0040784 | RB | 2.9 (1.0–4.0) | 11.5 (7.0–16.0) | 10.8% | 46.1% | MEDIUM |
| CLE | 00-0039373 | RB | 1.1 (0.0–2.0) | 6.0 (2.0–9.0) | 4.0% | 24.0% | HIGH |
| CLE | 00-0033537 | QB | 0.1 (0.0–0.0) | 6.2 (4.0–8.0) | 0.4% | 7.5% | MEDIUM |
| CLE | 00-0041547 | WR | 4.7 (2.0–7.0) | 0.8 (0.0–1.0) | 17.3% | 3.4% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 14 market(s), e.g. KXNFLPASSCOMP-26OCT25CLETEN-CLEDWATSON4-24, KXNFLPASSCOMP-26OCT25CLETEN-CLEDWATSON4-19
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 34 market(s), e.g. KXNFL1HFT-26OCT25CLETEN-TENTEN, KXNFL2H-26OCT25CLETEN-TEN
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 20 market(s), e.g. KXNFLSPREAD-26OCT25CLETEN-TEN6, KXNFLSPREAD-26OCT25CLETEN-CLE8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 2 market(s), e.g. KXNFLTEAMTOTAL-26OCT25CLETEN-TEN15, KXNFLTOTAL-26OCT25CLETEN-34
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 236 market(s), e.g. KXNFL1HFT-26OCT25CLETEN-TIETEN, KXNFL1HFT-26OCT25CLETEN-TIECLE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 25 market(s), e.g. KXNFL1HTOTAL-26OCT25CLETEN-4, KXNFL2HTOTAL-26OCT25CLETEN-8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 32.3%  _(final margin within one score (8 points) either way; total within 10 of the centre 37.5 (median favourite-oriented margin +1, median total 37))_
2. favourite controls / normal scoring — 15.9%  _(CLE (favourite) wins by more than one score; total within 10 of the centre 37.5 (median favourite-oriented margin +15, median total 38))_
3. competitive / high scoring — 11.4%  _(final margin within one score (8 points) either way; total 47.5+ (centre 37.5) (median favourite-oriented margin +1, median total 55))_
4. competitive / low scoring — 9.9%  _(final margin within one score (8 points) either way; total 27.5 or fewer (centre 37.5) (median favourite-oriented margin +2, median total 23))_
5. underdog controls / normal scoring — 8.3%  _(TEN (underdog) wins by more than one score; total within 10 of the centre 37.5 (median favourite-oriented margin -16, median total 37))_
   Other — 22.2%

Marginal events (overlapping): one_score 53.6% · blowout_17 18.3% · favorite_wins 60.8% · favorite_controls 30.7% · upset 39.0% · shootout 23.7% · low_scoring 19.8% · low_possession 25.1% · high_volume_passing 0.7% · run_heavy_control 12.1%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 3.10 mph, gusts 4.70, precip prob 0%, temp 72F, forecast retrieved 2026-10-24T11:36:14+00:00 (29.40 h before kickoff)._

**`KXNFLTD-26OCT25CLETEN-CLEJMCLAUGHLIN38-1`** Jaleel McLaughlin touchdowns 1
- MODEL / MARKET: football 15.7% · market 5.5% · reconciled 13.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 14.1% · failure mass 100.0% · win-contribution HHI 0.189

**`KXNFLTD-26OCT25CLETEN-CLEAESTIME30-1`** Audric Estime touchdowns 1
- MODEL / MARKET: football 21.2% · market 9.5% · reconciled 13.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 18.0% · failure mass 100.0% · win-contribution HHI 0.181

**`KXNFLTD-26OCT25CLETEN-TENTPOLLARD20-1`** Tony Pollard touchdowns 1
- MODEL / MARKET: football 28.6% · market 39.5% · reconciled 36.7%
- SCRIPT ROBUSTNESS: P50 mass 4.3% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 15.0% · failure mass 95.7% · win-contribution HHI 0.187

**`KXNFLTD-26OCT25CLETEN-CLEDWATSON4-1`** Deshaun Watson touchdowns 1
- MODEL / MARKET: football 14.9% · market 19.5% · reconciled 18.4%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 13.0% · failure mass 100.0% · win-contribution HHI 0.186

_366 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 41 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (5)**

- Dillon Gabriel (QB, CLE) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Teven Jenkins (G, CLE) — Injured Reserve [high] · **CHANGED from Out** — ruled out
- Dorian Mausi (LB, TEN) — Injured Reserve [high] — ruled out
- Kalia Davis (DT, CLE) — Injured Reserve [high] — ruled out
- Mike Hall Jr. (DT, CLE) — Out [high] — ruled out

**Questionable / Doubtful (6)** — resolves at the inactive release, T−90m

- Calvin Ridley (WR, TEN) — Questionable [high]
- Tyjae Spears (RB, TEN) — Questionable [high]
- Denzel Ward (CB, CLE) — Questionable [high]
- Kevin Winston Jr. (S, TEN) — Questionable [high]
- Quincy Williams (LB, CLE) — Questionable [high]
- Tony Adams (S, TEN) — Questionable [high]

### WEATHER

- Sunny · 72°F · wind 0 mph  · precip 0%
- forecast vintage 2026-10-24T20:14:21+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 59 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Deshaun Watson | CLE | attempts | 27.1 | 27.0 | 22.0 | 32.0 | 15.0 | 39.0 | 29.9 | 30.0 | 27.1 | 27.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Quinshon Judkins | CLE | carries | 11.5 | 11.0 | 7.0 | 16.0 | 2.0 | 24.0 | 14.5 | 14.0 | 11.5 | 11.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Deshaun Watson | CLE | completions | 17.4 | 17.0 | 14.0 | 21.0 | 9.0 | 26.0 | 18.8 | 18.0 | 17.4 | 17.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Deshaun Watson | CLE | passing_tds | 1.3 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.2 | 1.0 | 1.2 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Deshaun Watson | CLE | passing_yards | 187.8 | 182.0 | 140.0 | 231.0 | 82.0 | 312.0 | 213.7 | 207.0 | 213.7 | 207.0 | 0.00 | 0.98 | 9 | PRICED |
| Denzel Boston | CLE | receiving_yards | 44.4 | 35.0 | 13.0 | 65.0 | 0.0 | 124.0 | 59.6 | 50.0 | 59.5 | 47.0 | 0.00 | 0.98 | 10 | PRICED |
| KC Concepcion Jr. | CLE | receiving_yards | 33.6 | 26.0 | 10.0 | 49.0 | 0.0 | 94.0 | 43.7 | 37.0 | 43.7 | 34.0 | 0.00 | 0.98 | 9 | PRICED |
| Harold Fannin Jr. | CLE | receiving_yards | 33.0 | 26.0 | 10.0 | 48.0 | 0.0 | 91.0 | 34.2 | 28.0 | 34.2 | 27.0 | 0.00 | 0.98 | 8 | PRICED |

_8 of 59 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 59 of 93 listed player/stat groups simulated and exposed, 34 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT25CLETEN-CLEKCONCEPCION1-3` | KC Concepcion Jr. | 3.0 | 0.80 | 0.84 | 0.18 | -0.616 |
| `KXNFLREC-26OCT25CLETEN-TENCTATE14-3` | Carnell Tate | 3.0 | 0.80 | 0.82 | 0.19 | -0.616 |
| `KXNFLREC-26OCT25CLETEN-TENCTATE14-2` | Carnell Tate | 2.0 | 0.93 | 0.96 | 0.32 | -0.604 |
| `KXNFLREC-26OCT25CLETEN-CLEKCONCEPCION1-2` | KC Concepcion Jr. | 2.0 | 0.89 | 0.94 | 0.31 | -0.579 |
| `KXNFLRECYDS-26OCT25CLETEN-TENCTATE14-25` | Carnell Tate | 25.0 | 0.81 | 0.83 | 0.27 | -0.539 |
| `KXNFLRSHATT-26OCT25CLETEN-TENTPOLLARD20-14` | Tony Pollard | 14.0 | 0.71 | 0.73 | 0.19 | -0.527 |

_Ranked 369 tradable markets; 7 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Dillon Gabriel (QB, CLE) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 2 skill players are Questionable (Calvin Ridley (WR), Tyjae Spears (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLRECYDS-26OCT25CLETEN-TENEAYOMANOR5-30 moved +0.155 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.616 on KXNFLREC-26OCT25CLETEN-CLEKCONCEPCION1-3 (KC Concepcion Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.616 on KXNFLREC-26OCT25CLETEN-TENCTATE14-3 (Carnell Tate). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26OCT25CLETEN-TENCTATE14-2 sits at a market price of 0.93 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_CLE_TEN.md`_


---

## IND @ MIN — `2026_07_IND_MIN`

- kickoff: 2026-10-25T17:00:00+00:00 (1214 minutes away) · state **PREGAME**
- venue: U.S. Bank Stadium · roof dome · surface sportturf
- markets: 732 listed across 16 families — 384 supported, 290 no model, 48 rules unresolved, 10 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 10 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -6.40 | -6.11 |
| total | 42.12 | 41.99 |
| score | MIN 24.3 – IND 17.9 | MIN 24.1 – IND 17.9 |
| win prob MIN | 71.5% | 72.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -3.44 / total 21.12 · **2H** spread -2.97 / total 20.28 · **1Q** spread -2.54 / total 7.78 · **2Q** spread -2.55 / total 12.45 · **3Q** spread -1.50 / total 7.91 · **4Q** spread -1.32 / total 10.92

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -6.40 · total 42.12
- move `KXNFL1HTEAMTOTAL-26OCT25INDMIN-IND28` -0.125

**Game environment** (simulation, mean and middle 50%) — home margin 6.7 (-1.0–14.0) · total 43.7 (34.0–52.0) · P(one score) 48.6% · P(17+ blowout) 20.8% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| MIN | 62.4 (57.0–68.0) | 29.5 (25.0–34.0) | 26.1 (21.0–31.0) | 35.2 (30.0–40.0) | 0.565 (0.497–0.634) | 0.493 / 0.670 |
| IND | 61.9 (56.0–68.0) | 33.6 (29.0–38.0) | 23.3 (18.0–28.0) | 38.1 (33.0–43.0) | 0.616 (0.551–0.682) | 0.497 / 0.675 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| MIN | 00-0033293 | RB | 3.4 (1.0–5.0) | 20.6 (15.0–26.0) | 12.2% | 79.0% | MEDIUM |
| MIN | 00-0036322 | WR | 6.4 (4.0–9.0) | 0.5 (0.0–0.0) | 22.7% | 1.8% | HIGH |
| MIN | 00-0038994 | WR | 4.7 (2.0–7.0) | 0.5 (0.0–0.0) | 16.6% | 2.0% | HIGH |
| MIN | 00-0035228 | QB | 0.0 (0.0–0.0) | 5.1 (3.0–6.0) | 0.0% | 3.3% | HIGH |
| IND | 00-0036223 | RB | 3.6 (1.0–5.0) | 14.5 (10.0–19.0) | 11.3% | 62.3% | MEDIUM |
| IND | 00-0038997 | WR | 7.2 (4.0–10.0) | 0.4 (0.0–0.0) | 22.6% | 1.6% | HIGH |
| IND | 00-0030279 | WR | 7.3 (4.0–10.0) | 0.1 (0.0–0.0) | 22.9% | 0.3% | MEDIUM |
| IND | 00-0041125 | RB | 1.0 (0.0–1.0) | 3.2 (0.0–5.0) | 3.2% | 13.8% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 23 market(s), e.g. KXNFLPASSYDS-26OCT25INDMIN-MINKMURRAY1-300, KXNFLPASSYDS-26OCT25INDMIN-MINKMURRAY1-275
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 38 market(s), e.g. KXNFL1Q-26OCT25INDMIN-TIE, KXNFL3Q-26OCT25INDMIN-IND
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLBOTH-26OCT25INDMIN-21, KXNFLGAME-26OCT25INDMIN-IND
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLTEAMTOTAL-26OCT25INDMIN-MIN22, KXNFLTEAMTOTAL-26OCT25INDMIN-MIN21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 225 market(s), e.g. KXNFL1H-26OCT25INDMIN-TIE, KXNFL1HFT-26OCT25INDMIN-MININD
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 27 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25INDMIN-IND3, KXNFL2HTOTAL-26OCT25INDMIN-8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 26.8%  _(final margin within one score (8 points) either way; total within 10 of the centre 42.125 (median favourite-oriented margin +3, median total 43))_
2. favourite controls / normal scoring — 23.9%  _(MIN (favourite) wins by more than one score; total within 10 of the centre 42.125 (median favourite-oriented margin +15, median total 42))_
3. competitive / high scoring — 10.9%  _(final margin within one score (8 points) either way; total 52.125+ (centre 42.125) (median favourite-oriented margin +3, median total 60))_
4. competitive / low scoring — 10.9%  _(final margin within one score (8 points) either way; total 32.125 or fewer (centre 42.125) (median favourite-oriented margin +3, median total 28))_
5. favourite controls / high scoring — 10.3%  _(MIN (favourite) wins by more than one score; total 52.125+ (centre 42.125) (median favourite-oriented margin +17, median total 59))_
   Other — 17.2%

Marginal events (overlapping): one_score 48.6% · blowout_17 20.8% · favorite_wins 72.8% · favorite_controls 41.3% · upset 27.0% · shootout 23.8% · low_scoring 20.6% · low_possession 12.6% · high_volume_passing 2.8% · run_heavy_control 15.4%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 6.70 mph, gusts 15.20, precip prob 28%, temp 51F, forecast retrieved 2026-10-24T20:14:10+00:00 (20.76 h before kickoff)._

**`KXNFLTD-26OCT25INDMIN-MINGBARTHOLOMEW86-1`** Gavin Bartholomew touchdowns 1
- MODEL / MARKET: football 12.7% · market 7.5% · reconciled 19.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.0% · failure mass 100.0% · win-contribution HHI 0.196

**`KXNFLTD-26OCT25INDMIN-MINTFELTON13-1`** Tai Felton touchdowns 1
- MODEL / MARKET: football 8.2% · market 7.5% · reconciled 18.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.6% · failure mass 100.0% · win-contribution HHI 0.190

**`KXNFLTD-26OCT25INDMIN-MINMPRICE4-1`** Myles Price touchdowns 1
- MODEL / MARKET: football 7.6% · market 7.5% · reconciled 17.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.6% · failure mass 100.0% · win-contribution HHI 0.190

**`KXNFLTD-26OCT25INDMIN-MINAJONES33-1`** Aaron Jones Sr. touchdowns 1
- MODEL / MARKET: football 55.5% · market 38.5% · reconciled 43.7%
- SCRIPT ROBUSTNESS: P50 mass 79.0% · P55 mass 45.1% · P60 mass 45.1% · major-script floor 36.2% · failure mass 20.9% · win-contribution HHI 0.190

_372 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 42 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Alec Pierce (WR, IND) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Anthony Gould (WR, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jordan Mason (RB, MIN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Josh Oliver (TE, MIN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Tyler Warren (TE, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Donovan Jackson (G, MIN) — Injured Reserve [high] — ruled out
- CJ Allen (LB, IND) — Out [high] — ruled out
- Sauce Gardner (CB, IND) — Out [high] — ruled out

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Bryce Boettcher (LB, IND) — Questionable [high]
- Justin Walley (CB, IND) — Questionable [high]

### WEATHER

fixed-roof stadium (U.S. Bank Stadium) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 57 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Daniel Jones | IND | attempts | 32.3 | 32.0 | 27.0 | 37.0 | 19.0 | 45.0 | 33.2 | 33.0 | 32.3 | 32.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jonathan Taylor | IND | carries | 14.5 | 14.0 | 10.0 | 19.0 | 4.0 | 27.0 | 17.8 | 17.0 | 14.5 | 14.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Daniel Jones | IND | completions | 19.0 | 19.0 | 16.0 | 23.0 | 10.0 | 28.0 | 19.7 | 19.0 | 19.0 | 19.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Daniel Jones | IND | passing_tds | 1.0 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.00 | 0.97 | 3 | PRICED |
| Daniel Jones | IND | passing_yards | 202.0 | 197.0 | 154.0 | 246.0 | 93.0 | 326.0 | 194.5 | 177.0 | 194.5 | 190.0 | 0.00 | 0.97 | 1 | PRICED |
| Josh Downs | IND | receiving_yards | 50.7 | 43.0 | 20.0 | 72.0 | 0.0 | 127.0 | 56.9 | 48.0 | 56.9 | 48.0 | 0.00 | 0.97 | 12 | PRICED |
| Keenan Allen | IND | receiving_yards | 48.2 | 41.0 | 20.0 | 69.0 | 0.0 | 119.0 | 47.8 | 40.0 | 47.8 | 41.0 | 0.00 | 0.98 | 11 | PRICED |
| Laquon Treadwell | IND | receiving_yards | 27.0 | 18.0 | 0.0 | 41.0 | 0.0 | 88.0 | 27.9 | 20.0 | 27.9 | 18.0 | 0.00 | 0.98 | 9 | PRICED |

_8 of 57 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 57 of 91 listed player/stat groups simulated and exposed, 34 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRECYDS-26OCT25INDMIN-INDWMALLORY86-10` | Will Mallory | 10.0 | 0.68 | 0.69 | 0.01 | -0.673 |
| `KXNFLREC-26OCT25INDMIN-INDWMALLORY86-2` | Will Mallory | 2.0 | 0.62 | 0.63 | 0.01 | -0.612 |
| `KXNFLRECYDS-26OCT25INDMIN-INDWMALLORY86-15` | Will Mallory | 15.0 | 0.58 | 0.59 | 0.01 | -0.574 |
| `KXNFLREC-26OCT25INDMIN-MINTHOCKENSON87-3` | T.J. Hockenson | 3.0 | 0.77 | 0.79 | 0.25 | -0.525 |
| `KXNFLRECYDS-26OCT25INDMIN-INDWMALLORY86-20` | Will Mallory | 20.0 | 0.49 | 0.50 | 0.00 | -0.485 |
| `KXNFLREC-26OCT25INDMIN-INDKALLEN10-4` | Keenan Allen | 4.0 | 0.72 | 0.74 | 0.25 | -0.479 |

_Ranked 375 tradable markets; 9 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Anthony Gould (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Tyler Warren (TE, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLRECYDS-26OCT25INDMIN-INDJDOWNS2-50 moved +0.155 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.673 on KXNFLRECYDS-26OCT25INDMIN-INDWMALLORY86-10 (Will Mallory). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.612 on KXNFLREC-26OCT25INDMIN-INDWMALLORY86-2 (Will Mallory). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26OCT25INDMIN-MINJJEFFERSON18-3 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_IND_MIN.md`_


---

## MIA @ NYJ — `2026_07_MIA_NYJ`

- kickoff: 2026-10-25T17:00:00+00:00 (1214 minutes away) · state **PREGAME**
- venue: MetLife Stadium · roof outdoors · surface fieldturf
- markets: 707 listed across 16 families — 369 supported, 282 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -4.12 | -4.13 |
| total | 39.70 | 38.78 |
| score | NYJ 21.9 – MIA 17.8 | NYJ 21.5 – MIA 17.3 |
| win prob NYJ | 66.5% | 65.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -3.00 / total 20.18 · **2H** spread -2.50 / total 20.08 · **1Q** spread -1.52 / total 7.60 · **2Q** spread -2.12 / total 11.00 · **3Q** spread -1.27 / total 7.74 · **4Q** spread -0.93 / total 10.66

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -4.12 · total 39.70
- move `KXNFLGAME-26OCT25MIANYJ-MIA` -0.185
- move `KXNFL1HTEAMTOTAL-26OCT25MIANYJ-MIA28` -0.120

**Game environment** (simulation, mean and middle 50%) — home margin 4.7 (-3.0–12.0) · total 40.6 (32.0–49.0) · P(one score) 51.4% · P(17+ blowout) 17.3% · P(total 10+ over centre) 23.2%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NYJ | 61.5 (56.0–67.0) | 29.8 (25.0–34.0) | 26.9 (22.0–32.0) | 33.6 (28.0–39.0) | 0.547 (0.480–0.615) | 0.471 / 0.643 |
| MIA | 59.0 (53.0–65.0) | 26.9 (23.0–31.0) | 25.5 (21.0–30.0) | 33.0 (28.0–38.0) | 0.560 (0.494–0.626) | 0.455 / 0.624 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NYJ | 00-0039794 | RB | 2.0 (0.0–3.0) | 10.4 (5.0–15.0) | 7.1% | 38.6% | HIGH |
| NYJ | 00-0038120 | RB | 1.4 (0.0–2.0) | 9.3 (2.0–14.0) | 4.9% | 34.5% | HIGH |
| NYJ | 00-0037740 | WR | 5.9 (3.0–8.0) | 0.0 (0.0–0.0) | 20.8% | 0.1% | HIGH |
| NYJ | 00-0039890 | WR | 4.0 (2.0–6.0) | 0.0 (0.0–0.0) | 14.2% | 0.0% | HIGH |
| MIA | 00-0040198 | RB | 1.2 (0.0–2.0) | 12.0 (7.0–16.0) | 4.8% | 47.1% | MEDIUM |
| MIA | 00-0038128 | QB | 0.5 (0.0–0.0) | 6.8 (4.0–9.0) | 1.7% | 10.0% | MEDIUM |
| MIA | 00-0039880 | WR | 5.6 (3.0–8.0) | 1.2 (0.0–1.0) | 21.4% | 4.7% | HIGH |
| MIA | 00-0039874 | RB | 0.6 (0.0–1.0) | 5.3 (1.0–8.0) | 2.1% | 20.6% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 6 market(s), e.g. KXNFLPASSCOMP-26OCT25MIANYJ-MIAMWILLIS2-22, KXNFLPASSATT-26OCT25MIANYJ-NYJGSMITH7-30
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 38 market(s), e.g. KXNFL1HFT-26OCT25MIANYJ-NYJNYJ, KXNFL1Q-26OCT25MIANYJ-TIE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLBOTH-26OCT25MIANYJ-21, KXNFLSPREAD-26OCT25MIANYJ-NYJ14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLGAME-26OCT25MIANYJ-NYJ, KXNFLSPREAD-26OCT25MIANYJ-NYJ3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 227 market(s), e.g. KXNFL1H-26OCT25MIANYJ-TIE, KXNFL1HFT-26OCT25MIANYJ-MIANYJ
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 21 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25MIANYJ-NYJ3, KXNFL1HTEAMTOTAL-26OCT25MIANYJ-MIA3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.3%  _(final margin within one score (8 points) either way; total within 10 of the centre 39.7 (median favourite-oriented margin +2, median total 39))_
2. favourite controls / normal scoring — 20.9%  _(NYJ (favourite) wins by more than one score; total within 10 of the centre 39.7 (median favourite-oriented margin +14, median total 39))_
3. competitive / high scoring — 11.5%  _(final margin within one score (8 points) either way; total 49.7+ (centre 39.7) (median favourite-oriented margin +3, median total 57))_
4. competitive / low scoring — 10.5%  _(final margin within one score (8 points) either way; total 29.7 or fewer (centre 39.7) (median favourite-oriented margin +3, median total 24))_
5. favourite controls / high scoring — 8.3%  _(NYJ (favourite) wins by more than one score; total 49.7+ (centre 39.7) (median favourite-oriented margin +16, median total 57))_
   Other — 19.4%

Marginal events (overlapping): one_score 51.4% · blowout_17 17.3% · favorite_wins 66.5% · favorite_controls 35.6% · upset 33.3% · shootout 23.2% · low_scoring 20.4% · low_possession 23.8% · high_volume_passing 0.3% · run_heavy_control 17.1%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.90 mph, gusts 8.10, precip prob 0%, temp 64F, forecast retrieved 2026-10-24T20:14:10+00:00 (20.76 h before kickoff)._

**`KXNFLTD-26OCT25MIANYJ-MIAKCOLEMAN21-1`** Kevin Coleman Jr. touchdowns 1
- MODEL / MARKET: football 12.9% · market 7.5% · reconciled 19.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.4% · failure mass 100.0% · win-contribution HHI 0.182

**`KXNFLTD-26OCT25MIANYJ-NYJTPATRICK17-1`** Tim Patrick touchdowns 1
- MODEL / MARKET: football 8.4% · market 6.5% · reconciled 14.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.7% · failure mass 100.0% · win-contribution HHI 0.190

**`KXNFLTD-26OCT25MIANYJ-NYJBALLEN0-1`** Braelon Allen touchdowns 1
- MODEL / MARKET: football 34.1% · market 46.5% · reconciled 44.0%
- SCRIPT ROBUSTNESS: P50 mass 8.2% · P55 mass 8.2% · P60 mass 0.0% · major-script floor 16.6% · failure mass 91.7% · win-contribution HHI 0.191

**`KXNFLTD-26OCT25MIANYJ-NYJGWILSON5-1`** Garrett Wilson touchdowns 1
- MODEL / MARKET: football 25.9% · market 35.5% · reconciled 33.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 13.8% · failure mass 100.0% · win-contribution HHI 0.187
- THESIS DEPENDENCY with `KXNFLPASSTDS-26OCT25MIANYJ-NYJGSMITH7-2`: cash correlation 0.322 · joint cash 16.8% · Jaccard of winning rows 0.354 · shared failure 52.6%

_359 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 38 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Max Mitchell (OT, NYJ) — Out [high] — ruled out
- Joseph Ossai (DE, NYJ) — Out [high] — ruled out
- Kiko Mauigoa (LB, NYJ) — Injured Reserve [high] · **CHANGED from Out** — ruled out
- Reese Taylor (CB, MIA) — Out [high] — ruled out

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Breece Hall (RB, NYJ) — Questionable [high]
- Kene Nwangwu (RB, NYJ) — Questionable [high]
- Dylan Parham (G, NYJ) — Questionable [high]
- Robert Beal Jr. (DE, MIA) — Doubtful [single_source]
- Willie Gay Jr. (LB, MIA) — Questionable [high]

### WEATHER

- Sunny · 65°F · wind 2 mph W · precip 0%
- forecast vintage 2026-10-24T20:14:19+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 63, 'wind': '2 mph', 'precipitation_probability': 0})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 55 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Malik Willis | MIA | attempts | 25.9 | 26.0 | 22.0 | 30.0 | 15.0 | 37.0 | 27.5 | 27.0 | 25.9 | 26.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Ollie Gordon II | MIA | carries | 12.0 | 11.0 | 7.0 | 16.0 | 2.0 | 24.0 | 14.5 | 14.0 | 12.0 | 11.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Malik Willis | MIA | carries | 6.8 | 6.0 | 4.0 | 9.0 | 2.0 | 15.0 | 6.5 | 6.0 | 6.8 | 6.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Malik Willis | MIA | completions | 15.5 | 15.0 | 12.0 | 19.0 | 8.0 | 23.0 | 16.6 | 16.0 | 15.5 | 15.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Malik Willis | MIA | passing_tds | 0.9 | 1.0 | 0.0 | 1.0 | 0.0 | 3.0 | 0.9 | 1.0 | 0.9 | 1.0 | 0.00 | 0.98 | 3 | PRICED |
| Malik Willis | MIA | passing_yards | 172.8 | 167.0 | 126.0 | 215.0 | 73.0 | 289.0 | 186.4 | 179.0 | 186.4 | 181.0 | 0.00 | 0.98 | 8 | PRICED |
| Malik Washington | MIA | receiving_yards | 39.2 | 32.0 | 14.0 | 57.0 | 0.0 | 104.0 | 45.8 | 39.0 | 45.8 | 37.0 | 0.00 | 0.97 | 12 | PRICED |
| Caleb Douglas | MIA | receiving_yards | 29.6 | 21.0 | 6.0 | 44.0 | 0.0 | 91.0 | 40.2 | 31.0 | 40.2 | 29.0 | 0.00 | 0.97 | 12 | PRICED |

_8 of 55 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 55 of 83 listed player/stat groups simulated and exposed, 28 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26OCT25MIANYJ-MIAOGORDON0-25` | Ollie Gordon II | 25.0 | 0.86 | 0.87 | 0.19 | -0.671 |
| `KXNFLRSHYDS-26OCT25MIANYJ-MIAOGORDON0-30` | Ollie Gordon II | 30.0 | 0.81 | 0.82 | 0.15 | -0.667 |
| `KXNFLRSHATT-26OCT25MIANYJ-MIAOGORDON0-11` | Ollie Gordon II | 11.0 | 0.79 | 0.82 | 0.15 | -0.637 |
| `KXNFLRSHYDS-26OCT25MIANYJ-MIAOGORDON0-40` | Ollie Gordon II | 40.0 | 0.70 | 0.71 | 0.10 | -0.610 |
| `KXNFLRSHATT-26OCT25MIANYJ-MIAMWILLIS2-4` | Malik Willis | 4.0 | 0.83 | 0.85 | 0.25 | -0.575 |
| `KXNFLREC-26OCT25MIANYJ-NYJGWILSON5-4` | Garrett Wilson | 4.0 | 0.80 | 0.82 | 0.24 | -0.556 |

_Ranked 366 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. 2 skill players are Questionable (Breece Hall (RB), Kene Nwangwu (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
2. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
3. KXNFLGAME-26OCT25MIANYJ-MIA moved -0.185 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.671 on KXNFLRSHYDS-26OCT25MIANYJ-MIAOGORDON0-25 (Ollie Gordon II). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.667 on KXNFLRSHYDS-26OCT25MIANYJ-MIAOGORDON0-30 (Ollie Gordon II). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26OCT25MIANYJ-NYJGWILSON5-3 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_MIA_NYJ.md`_


---

## NYG @ HOU — `2026_07_NYG_HOU`

- kickoff: 2026-10-25T17:00:00+00:00 (1214 minutes away) · state **PREGAME**
- venue: Reliant Stadium · roof  · surface astroturf
- markets: 785 listed across 16 families — 433 supported, 296 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -10.25 | -9.85 |
| total | 43.38 | 43.38 |
| score | HOU 26.8 – NYG 16.6 | HOU 26.6 – NYG 16.8 |
| win prob HOU | 80.5% | 80.3% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -6.65 / total 21.88 · **2H** spread -4.28 / total 21.00 · **1Q** spread -2.95 / total 7.94 · **2Q** spread -3.36 / total 12.85 · **3Q** spread -2.63 / total 8.38 · **4Q** spread -2.68 / total 11.14

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -10.25 · total 43.38
- move `KXNFL1HTEAMTOTAL-26OCT25NYGHOU-HOU17` -0.305
- move `KXNFLGAME-26OCT25NYGHOU-NYG` -0.200
- move `KXNFLGAME-26OCT25NYGHOU-HOU` +0.160
- move `KXNFL1HTEAMTOTAL-26OCT25NYGHOU-NYG28` -0.125

**Game environment** (simulation, mean and middle 50%) — home margin 10.7 (3.0–18.0) · total 44.6 (35.0–53.0) · P(one score) 35.0% · P(17+ blowout) 31.3% · P(total 10+ over centre) 23.5%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| HOU | 63.9 (58.0–70.0) | 32.5 (27.0–37.0) | 27.1 (22.0–32.0) | 35.7 (30.0–41.0) | 0.558 (0.490–0.628) | 0.499 / 0.693 |
| NYG | 62.8 (57.0–69.0) | 33.6 (29.0–38.0) | 23.6 (19.0–28.0) | 38.8 (33.0–44.0) | 0.619 (0.555–0.685) | 0.477 / 0.662 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| HOU | 00-0040583 | RB | 2.4 (1.0–4.0) | 20.4 (15.0–26.0) | 8.0% | 75.1% | MEDIUM |
| HOU | 00-0036554 | WR | 6.5 (4.0–9.0) | 0.9 (0.0–1.0) | 21.4% | 3.4% | HIGH |
| HOU | 00-0034383 | TE | 4.5 (2.0–6.0) | 0.0 (0.0–0.0) | 14.6% | 0.0% | HIGH |
| HOU | 00-0039163 | QB | 0.2 (0.0–0.0) | 4.2 (2.0–5.0) | 0.6% | 5.9% | HIGH |
| NYG | 00-0040715 | RB | 2.4 (0.0–3.0) | 9.2 (5.0–13.0) | 7.3% | 39.1% | MEDIUM |
| NYG | 00-0039337 | WR | 9.6 (6.0–13.0) | 0.1 (0.0–0.0) | 29.7% | 0.2% | MEDIUM |
| NYG | 00-0039384 | RB | 1.7 (0.0–3.0) | 5.7 (2.0–8.0) | 5.2% | 24.3% | HIGH |
| NYG | 00-0037838 | TE | 7.3 (4.0–10.0) | 0.1 (0.0–0.0) | 22.6% | 0.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 7 market(s), e.g. KXNFLRSHYDS-26OCT25NYGHOU-NYGTTRACY29-60, KXNFLRSHYDS-26OCT25NYGHOU-NYGTTRACY29-15
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 53 market(s), e.g. KXNFL2H-26OCT25NYGHOU-NYG, KXNFL4Q-26OCT25NYGHOU-NYG
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 17 market(s), e.g. KXNFLGAME-26OCT25NYGHOU-NYG, KXNFLSPREAD-26OCT25NYGHOU-NYG3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLSPREAD-26OCT25NYGHOU-HOU6, KXNFLSPREAD-26OCT25NYGHOU-HOU7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 242 market(s), e.g. KXNFL1H-26OCT25NYGHOU-TIE, KXNFL1HFT-26OCT25NYGHOU-TIEHOU
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 26 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25NYGHOU-NYG3, KXNFLPASSYDS-26OCT25NYGHOU-NYGJMCCARTHY9-125

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 33.1%  _(HOU (favourite) wins by more than one score; total within 10 of the centre 43.375 (median favourite-oriented margin +17, median total 43))_
2. competitive / normal scoring — 19.5%  _(final margin within one score (8 points) either way; total within 10 of the centre 43.375 (median favourite-oriented margin +3, median total 43))_
3. favourite controls / high scoring — 14.1%  _(HOU (favourite) wins by more than one score; total 53.375+ (centre 43.375) (median favourite-oriented margin +17, median total 61))_
4. favourite controls / low scoring — 12.0%  _(HOU (favourite) wins by more than one score; total 33.375 or fewer (centre 43.375) (median favourite-oriented margin +15, median total 29))_
5. competitive / high scoring — 8.1%  _(final margin within one score (8 points) either way; total 53.375+ (centre 43.375) (median favourite-oriented margin +3, median total 59))_
   Other — 13.2%

Marginal events (overlapping): one_score 35.0% · blowout_17 31.3% · favorite_wins 82.2% · favorite_controls 59.2% · upset 17.6% · shootout 23.5% · low_scoring 20.7% · low_possession 7.8% · high_volume_passing 6.3% · run_heavy_control 20.6%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 10.90 mph, gusts 14.80, precip prob 0%, temp 81F, forecast retrieved 2026-10-24T20:14:10+00:00 (20.76 h before kickoff)._

**`KXNFLTD-26OCT25NYGHOU-HOUCSTOVER8-1`** Cade Stover touchdowns 1
- MODEL / MARKET: football 11.5% · market 6.5% · reconciled 15.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.2% · failure mass 100.0% · win-contribution HHI 0.243

**`KXNFLTD-26OCT25NYGHOU-NYGDMOONEY17-1`** Darnell Mooney touchdowns 1
- MODEL / MARKET: football 9.1% · market 9.0% · reconciled 15.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 2.0% · failure mass 100.0% · win-contribution HHI 0.183

**`KXNFLTD-26OCT25NYGHOU-HOUCSTROUD7-1`** C.J. Stroud touchdowns 1
- MODEL / MARKET: football 19.3% · market 12.5% · reconciled 15.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 15.7% · failure mass 100.0% · win-contribution HHI 0.236

**`KXNFLTD-26OCT25NYGHOU-HOUXHUTCHINSON19-1`** Xavier Hutchinson touchdowns 1
- MODEL / MARKET: football 17.1% · market 11.5% · reconciled 13.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 13.1% · failure mass 100.0% · win-contribution HHI 0.222

_423 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 44 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (11)**

- David Montgomery (RB, HOU) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tank Dell (WR, HOU) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Theo Johnson (TE, NYG) — Out [high] · **CHANGED from Doubtful** — ruled out -- role redistributes to the depth chart behind him
- Blake Fisher (OT, HOU) — Out [high] — ruled out
- Greg Newsome II (CB, NYG) — Out [high] — ruled out
- Jake Hummel (LB, HOU) — Injured Reserve [high] — ruled out
- Jalen Pitre (S, HOU) — Out [high] — ruled out
- Jevon Holland (S, NYG) — Out [single_source] · **CHANGED from Questionable** — ruled out
- _...and 3 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Jermaine Eluemunor (OT, NYG) — Questionable [high]
- Marcus Mbow (OT, NYG) — Questionable [high]
- Tyler Nubin (S, NYG) — Questionable [high]

### WEATHER

- retractable roof (Reliant Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Mostly Sunny · 78°F · wind 10 mph E · precip 0%
- forecast vintage 2026-10-24T20:14:15+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 79, 'wind': '10 mph', 'precipitation_probability': 0})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 64 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C.J. Stroud | HOU | attempts | 31.2 | 31.0 | 26.0 | 37.0 | 17.0 | 45.0 | 33.3 | 33.0 | 31.2 | 31.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Woody Marks | HOU | carries | 20.4 | 20.0 | 15.0 | 26.0 | 7.0 | 34.0 | 16.3 | 16.0 | 20.4 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| C.J. Stroud | HOU | completions | 19.9 | 20.0 | 16.0 | 24.0 | 11.0 | 29.0 | 21.6 | 21.0 | 19.9 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| C.J. Stroud | HOU | passing_tds | 1.8 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.0 | 2.0 | 2.0 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| C.J. Stroud | HOU | passing_yards | 240.2 | 235.0 | 182.0 | 294.0 | 110.0 | 390.0 | 259.7 | 255.0 | 259.7 | 254.0 | 0.00 | 0.97 | 9 | PRICED |
| Nico Collins | HOU | receiving_yards | 60.1 | 50.0 | 24.0 | 85.0 | 0.0 | 155.0 | 73.7 | 65.0 | 73.5 | 61.0 | 0.00 | 0.98 | 13 | PRICED |
| Dalton Schultz | HOU | receiving_yards | 35.1 | 28.0 | 10.0 | 52.0 | 0.0 | 99.0 | 32.3 | 26.0 | 32.3 | 25.0 | 0.00 | 0.97 | 11 | PRICED |
| Xavier Hutchinson | HOU | receiving_yards | 30.6 | 21.0 | 5.0 | 46.0 | 0.0 | 98.0 | 21.1 | 14.0 | 21.1 | 14.0 | 0.00 | 0.98 | 7 | PRICED |

_8 of 64 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 64 of 101 listed player/stat groups simulated and exposed, 37 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT25NYGHOU-NYGILIKELY9-3` | Isaiah Likely | 3.0 | 0.89 | 0.91 | 0.18 | -0.708 |
| `KXNFLRECYDS-26OCT25NYGHOU-NYGILIKELY9-25` | Isaiah Likely | 25.0 | 0.82 | 0.84 | 0.16 | -0.667 |
| `KXNFLRECYDS-26OCT25NYGHOU-NYGILIKELY9-20` | Isaiah Likely | 20.0 | 0.87 | 0.88 | 0.20 | -0.666 |
| `KXNFLREC-26OCT25NYGHOU-NYGILIKELY9-4` | Isaiah Likely | 4.0 | 0.77 | 0.78 | 0.11 | -0.661 |
| `KXNFLRECYDS-26OCT25NYGHOU-NYGILIKELY9-30` | Isaiah Likely | 30.0 | 0.77 | 0.78 | 0.12 | -0.641 |
| `KXNFLRSHATT-26OCT25NYGHOU-HOUWMARKS4-12` | Woody Marks | 12.0 | 0.83 | 0.85 | 0.23 | -0.596 |

_Ranked 427 tradable markets; 6 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. David Montgomery (RB, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Tank Dell (WR, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
4. KXNFL1HTEAMTOTAL-26OCT25NYGHOU-HOU17 moved -0.305 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.708 on KXNFLREC-26OCT25NYGHOU-NYGILIKELY9-3 (Isaiah Likely). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.667 on KXNFLRECYDS-26OCT25NYGHOU-NYGILIKELY9-25 (Isaiah Likely). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT25NYGHOU-NYGILIKELY9-3 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_NYG_HOU.md`_


---

## SF @ ATL — `2026_07_SF_ATL`

- kickoff: 2026-10-25T17:00:00+00:00 (1214 minutes away) · state **PREGAME**
- venue: Mercedes-Benz Stadium · roof  · surface fieldturf
- markets: 738 listed across 16 families — 397 supported, 285 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.73 | 2.29 |
| total | 50.12 | 49.95 |
| score | ATL 23.7 – SF 26.4 | ATL 23.8 – SF 26.1 |
| win prob ATL | 41.5% | 40.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 1.96 / total 24.52 · **2H** spread 0.96 / total 24.89 · **1Q** spread -0.10 / total 8.91 · **2Q** spread 0.24 / total 14.75 · **3Q** spread 0.14 / total 9.65 · **4Q** spread 0.17 / total 14.54

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.73 · total 50.12
- move `KXNFLSPREAD-26OCT25SFATL-ATL2` +0.150
- move `KXNFLSPREAD-26OCT25SFATL-SF4` -0.125
- move `KXNFLSPREAD-26OCT25SFATL-SF15` -0.125
- move `KXNFLSPREAD-26OCT25SFATL-SF5` -0.120

**Game environment** (simulation, mean and middle 50%) — home margin -2.5 (-10.0–5.0) · total 51.8 (43.0–60.0) · P(one score) 53.6% · P(17+ blowout) 18.1% · P(total 10+ over centre) 24.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| ATL | 62.3 (57.0–68.0) | 32.8 (28.0–37.0) | 25.3 (20.0–30.0) | 36.4 (31.0–41.0) | 0.584 (0.519–0.651) | 0.485 / 0.652 |
| SF | 63.0 (57.0–69.0) | 33.7 (29.0–38.0) | 23.6 (19.0–28.0) | 38.5 (33.0–44.0) | 0.612 (0.545–0.680) | 0.530 / 0.701 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| ATL | 00-0038542 | RB | 5.2 (2.0–7.0) | 23.4 (19.0–28.0) | 16.5% | 92.5% | LOW |
| ATL | 00-0037238 | WR | 9.5 (6.0–12.0) | 0.3 (0.0–0.0) | 30.1% | 1.2% | MEDIUM |
| ATL | 00-0036970 | TE | 5.4 (3.0–8.0) | 0.0 (0.0–0.0) | 17.3% | 0.0% | HIGH |
| ATL | 00-0037741 | WR | 4.0 (2.0–6.0) | 0.2 (0.0–0.0) | 12.6% | 0.9% | HIGH |
| SF | 00-0033280 | RB | 7.7 (4.0–10.0) | 12.5 (8.0–17.0) | 23.7% | 53.1% | MEDIUM |
| SF | 00-0033288 | TE | 7.9 (5.0–11.0) | 0.0 (0.0–0.0) | 24.4% | 0.1% | MEDIUM |
| SF | 00-0041052 | RB | 0.9 (0.0–1.0) | 6.1 (2.0–9.0) | 2.9% | 26.0% | HIGH |
| SF | 00-0036261 | WR | 6.5 (3.0–9.0) | 0.0 (0.0–0.0) | 20.2% | 0.0% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 15 market(s), e.g. KXNFLPASSATT-26OCT25SFATL-SFBPURDY13-31, KXNFLPASSCOMP-26OCT25SFATL-SFBPURDY13-26
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 73 market(s), e.g. KXNFL1Q-26OCT25SFATL-TIE, KXNFL1Q-26OCT25SFATL-SF
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT25SFATL-SF8, KXNFLSPREAD-26OCT25SFATL-SF15
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLTOTAL-26OCT25SFATL-45, KXNFLTEAMTOTAL-26OCT25SFATL-ATL22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 220 market(s), e.g. KXNFL1H-26OCT25SFATL-TIE, KXNFL1HFT-26OCT25SFATL-TIESF
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 35 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25SFATL-SF3, KXNFL1HTEAMTOTAL-26OCT25SFATL-ATL3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.2%  _(final margin within one score (8 points) either way; total within 10 of the centre 50.125 (median favourite-oriented margin +1, median total 50))_
2. favourite controls / normal scoring — 15.5%  _(SF (favourite) wins by more than one score; total within 10 of the centre 50.125 (median favourite-oriented margin +15, median total 51))_
3. competitive / high scoring — 12.4%  _(final margin within one score (8 points) either way; total 60.125+ (centre 50.125) (median favourite-oriented margin +1, median total 68))_
4. competitive / low scoring — 10.0%  _(final margin within one score (8 points) either way; total 40.125 or fewer (centre 50.125) (median favourite-oriented margin +2, median total 36))_
5. underdog controls / normal scoring — 8.6%  _(ATL (underdog) wins by more than one score; total within 10 of the centre 50.125 (median favourite-oriented margin -16, median total 51))_
   Other — 22.3%

Marginal events (overlapping): one_score 53.6% · blowout_17 18.1% · favorite_wins 60.7% · favorite_controls 30.3% · upset 39.0% · shootout 24.3% · low_scoring 20.3% · low_possession 10.3% · high_volume_passing 6.3% · run_heavy_control 12.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 12.70 mph, gusts 19.00, precip prob 0%, temp 66F, forecast retrieved 2026-10-24T20:14:10+00:00 (20.76 h before kickoff)._

**`KXNFLTD-26OCT25SFATL-ATLMPENIX9-1`** Michael Penix Jr. touchdowns 1
- MODEL / MARKET: football 11.0% · market 8.5% · reconciled 23.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.7% · failure mass 100.0% · win-contribution HHI 0.174

**`KXNFLTD-26OCT25SFATL-ATLZBRANCH17-1`** Zachariah Branch touchdowns 1
- MODEL / MARKET: football 9.7% · market 8.5% · reconciled 22.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.2% · failure mass 100.0% · win-contribution HHI 0.179

**`KXNFLTD-26OCT25SFATL-ATLDLONDON5-1`** Drake London touchdowns 1
- MODEL / MARKET: football 33.9% · market 41.5% · reconciled 39.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 23.3% · failure mass 100.0% · win-contribution HHI 0.179
- THESIS DEPENDENCY with `KXNFLPASSTDS-26OCT25SFATL-ATLMPENIX9-2`: cash correlation 0.333 · joint cash 22.9% · Jaccard of winning rows 0.413 · shared failure 44.5%

**`KXNFLTD-26OCT25SFATL-ATLMPENIX9-2`** Michael Penix Jr. touchdowns 2
- MODEL / MARKET: football 1.1% · market 0.5% · reconciled 2.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.4% · failure mass 100.0% · win-contribution HHI 0.178

_376 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 43 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (13)**

- Beaux Collins (WR, ATL) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Brian Robinson Jr. (RB, ATL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Christian Kirk (WR, SF) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Deebo Samuel Sr. (WR, SF) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Mike Evans (WR, SF) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Cameron Williams (OL, ATL) — Injured Reserve [high] — ruled out
- Michael Jerrell (OT, ATL) — Injured Reserve [single_source] · **CHANGED from Out** — ruled out
- Billy Bowman Jr. (CB, ATL) — Out [high] — ruled out
- _...and 5 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (9)** — resolves at the inactive release, T−90m

- Olamide Zaccheaus (WR, ATL) — Questionable [high]
- Avieon Terrell (CB, ATL) — Questionable [high]
- C.J. Henderson (CB, ATL) — Questionable [high]
- Gervon Dexter Sr. (DT, ATL) — Questionable [high]
- Kendal Daniels (LB, ATL) — Questionable [high]
- Samson Ebukam (DE, ATL) — Questionable [high]
- Siran Neal (S, SF) — Questionable [high]
- Upton Stout (CB, SF) — Questionable [high]

### WEATHER

- retractable roof (Mercedes-Benz Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Sunny · 66°F · wind 15 mph E · precip 0%
- forecast vintage 2026-10-24T20:14:11+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 66, 'wind': '10 mph', 'precipitation_probability': 0})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 56 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Michael Penix Jr. | ATL | attempts | 31.5 | 32.0 | 27.0 | 37.0 | 18.0 | 44.0 | 31.9 | 32.0 | 31.5 | 32.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bijan Robinson | ATL | carries | 23.4 | 23.0 | 19.0 | 28.0 | 11.0 | 36.0 | 19.6 | 19.0 | 23.4 | 23.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | completions | 20.3 | 20.0 | 17.0 | 24.0 | 11.0 | 30.0 | 20.0 | 20.0 | 20.3 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Michael Penix Jr. | ATL | passing_yards | 220.9 | 217.0 | 168.0 | 269.0 | 101.0 | 358.0 | 235.3 | 229.0 | 235.3 | 231.0 | 0.00 | 0.97 | 9 | PRICED |
| Drake London | ATL | receiving_yards | 80.1 | 72.0 | 40.0 | 111.0 | 7.0 | 181.0 | 90.0 | 82.0 | 89.9 | 81.0 | 0.00 | 0.97 | 13 | PRICED |
| Kyle Pitts Sr. | ATL | receiving_yards | 38.6 | 31.0 | 13.0 | 56.0 | 0.0 | 105.0 | 39.8 | 33.0 | 39.8 | 32.0 | 0.00 | 0.98 | 10 | PRICED |
| Jahan Dotson | ATL | receiving_yards | 32.6 | 22.0 | 4.0 | 49.0 | 0.0 | 104.0 | 35.5 | 27.0 | 35.5 | 24.0 | 0.00 | 0.97 | 8 | PRICED |

_8 of 56 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 56 of 92 listed player/stat groups simulated and exposed, 36 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT25SFATL-ATLBROBINSON7-15` | Bijan Robinson | 15.0 | 0.80 | 0.81 | 0.20 | -0.605 |
| `KXNFLREC-26OCT25SFATL-SFGKITTLE85-4` | George Kittle | 4.0 | 0.79 | 0.80 | 0.19 | -0.600 |
| `KXNFLREC-26OCT25SFATL-SFCMCCAFFREY23-4` | Christian McCaffrey | 4.0 | 0.77 | 0.77 | 0.18 | -0.580 |
| `KXNFLRSHATT-26OCT25SFATL-SFBPURDY13-2` | Brock Purdy | 2.0 | 0.92 | 0.95 | 0.35 | -0.573 |
| `KXNFLREC-26OCT25SFATL-SFGKITTLE85-3` | George Kittle | 3.0 | 0.91 | 0.93 | 0.34 | -0.570 |
| `KXNFLREC-26OCT25SFATL-SFGKITTLE85-5` | George Kittle | 5.0 | 0.66 | 0.67 | 0.10 | -0.559 |

_Ranked 385 tradable markets; 12 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Brian Robinson Jr. (RB, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Beaux Collins (WR, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Olamide Zaccheaus (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
5. KXNFLFFPTS-26OCT25SFATL-ATLDLONDON5-16P6 moved -0.175 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
6. The model disagrees by -0.605 on KXNFLRSHATT-26OCT25SFATL-ATLBROBINSON7-15 (Bijan Robinson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. The model disagrees by -0.600 on KXNFLREC-26OCT25SFATL-SFGKITTLE85-4 (George Kittle). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
8. KXNFLRSHATT-26OCT25SFATL-SFBPURDY13-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_SF_ATL.md`_


---

## TB @ CAR — `2026_07_TB_CAR`

- kickoff: 2026-10-25T17:00:00+00:00 (1214 minutes away) · state **PREGAME**
- venue: Bank of America Stadium · roof outdoors · surface grass
- markets: 745 listed across 16 families — 392 supported, 297 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.75 | -2.49 |
| total | 45.12 | 45.19 |
| score | CAR 23.9 – TB 21.2 | CAR 23.8 – TB 21.4 |
| win prob CAR | 59.5% | 58.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -1.85 / total 22.31 · **2H** spread -0.92 / total 22.54 · **1Q** spread -0.62 / total 7.87 · **2Q** spread -1.35 / total 13.44 · **3Q** spread -0.70 / total 8.77 · **4Q** spread 0.12 / total 12.77

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -2.75 · total 45.12
- move `KXNFL1HTEAMTOTAL-26OCT25TBCAR-CAR31` -0.105
- move `KXNFL2HTOTAL-26OCT25TBCAR-8` +0.095

**Game environment** (simulation, mean and middle 50%) — home margin 2.6 (-5.0–10.0) · total 46.5 (37.0–54.0) · P(one score) 53.0% · P(17+ blowout) 18.1% · P(total 10+ over centre) 22.9%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CAR | 64.2 (59.0–70.0) | 36.2 (31.0–41.0) | 23.5 (18.0–28.0) | 39.8 (34.0–45.0) | 0.621 (0.554–0.690) | 0.533 / 0.708 |
| TB | 63.1 (57.0–69.0) | 32.7 (28.0–37.0) | 24.4 (19.0–29.0) | 38.0 (33.0–43.0) | 0.604 (0.539–0.671) | 0.506 / 0.676 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CAR | 00-0036555 | RB | 3.0 (1.0–4.0) | 16.8 (12.0–22.0) | 8.9% | 71.5% | MEDIUM |
| CAR | 00-0040124 | WR | 7.7 (4.0–10.0) | 0.0 (0.0–0.0) | 23.0% | 0.2% | MEDIUM |
| CAR | 00-0039491 | WR | 6.4 (3.0–9.0) | 0.1 (0.0–0.0) | 19.1% | 0.3% | HIGH |
| CAR | 00-0036265 | RB | 0.7 (0.0–1.0) | 4.4 (1.0–6.0) | 2.1% | 18.9% | HIGH |
| TB | 00-0039361 | RB | 4.0 (2.0–6.0) | 16.6 (12.0–21.0) | 12.6% | 68.1% | MEDIUM |
| TB | 00-0036919 | RB | 3.8 (1.0–5.0) | 3.6 (0.0–5.0) | 12.0% | 14.7% | HIGH |
| TB | 00-0033921 | WR | 6.3 (3.0–9.0) | 0.3 (0.0–0.0) | 19.9% | 1.3% | HIGH |
| TB | 00-0038129 | TE | 5.8 (3.0–8.0) | 0.0 (0.0–0.0) | 18.4% | 0.0% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 18 market(s), e.g. KXNFLRECYDS-26OCT25TBCAR-CARJMETCHIE13-15, KXNFLRSHYDS-26OCT25TBCAR-TBKGAINWELL1-30
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 47 market(s), e.g. KXNFL1HFT-26OCT25TBCAR-TBTB, KXNFL1HFT-26OCT25TBCAR-CARCAR
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 24 market(s), e.g. KXNFLSPREAD-26OCT25TBCAR-TB4, KXNFLSPREAD-26OCT25TBCAR-TB10
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLTEAMTOTAL-26OCT25TBCAR-CAR22, KXNFLTEAMTOTAL-26OCT25TBCAR-TB18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 229 market(s), e.g. KXNFL1H-26OCT25TBCAR-TIE, KXNFL1HFT-26OCT25TBCAR-TIETB
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 27 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25TBCAR-TB3, KXNFL1HTOTAL-26OCT25TBCAR-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.2%  _(final margin within one score (8 points) either way; total within 10 of the centre 45.125 (median favourite-oriented margin +2, median total 45))_
2. favourite controls / normal scoring — 17.6%  _(CAR (favourite) wins by more than one score; total within 10 of the centre 45.125 (median favourite-oriented margin +14, median total 45))_
3. competitive / low scoring — 12.2%  _(final margin within one score (8 points) either way; total 35.125 or fewer (centre 45.125) (median favourite-oriented margin +2, median total 30))_
4. competitive / high scoring — 11.6%  _(final margin within one score (8 points) either way; total 55.125+ (centre 45.125) (median favourite-oriented margin +2, median total 63))_
5. underdog controls / normal scoring — 9.5%  _(TB (underdog) wins by more than one score; total within 10 of the centre 45.125 (median favourite-oriented margin -13, median total 47))_
   Other — 20.0%

Marginal events (overlapping): one_score 53.0% · blowout_17 18.1% · favorite_wins 60.3% · favorite_controls 29.5% · upset 39.5% · shootout 22.9% · low_scoring 20.9% · low_possession 6.9% · high_volume_passing 10.8% · run_heavy_control 11.5%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 10.80 mph, gusts 15.70, precip prob 0%, temp 65F, forecast retrieved 2026-10-24T20:14:10+00:00 (20.76 h before kickoff)._

**`KXNFLTD-26OCT25TBCAR-CARJMETCHIE13-1`** John Metchie III touchdowns 1
- MODEL / MARKET: football 13.4% · market 8.5% · reconciled 23.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.8% · failure mass 100.0% · win-contribution HHI 0.176

**`KXNFLTD-26OCT25TBCAR-CARADILLON28-1`** AJ Dillon touchdowns 1
- MODEL / MARKET: football 12.6% · market 8.5% · reconciled 23.4%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.6% · failure mass 100.0% · win-contribution HHI 0.182

**`KXNFLTD-26OCT25TBCAR-CARJMETCHIE13-2`** John Metchie III touchdowns 2
- MODEL / MARKET: football 1.6% · market 0.5% · reconciled 3.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.2% · failure mass 100.0% · win-contribution HHI 0.205

**`KXNFLTD-26OCT25TBCAR-CARADILLON28-2`** AJ Dillon touchdowns 2
- MODEL / MARKET: football 1.5% · market 0.5% · reconciled 3.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.3% · failure mass 100.0% · win-contribution HHI 0.209

_383 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 36 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Emeka Egbuka (WR, TB) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jonathon Brooks (RB, CAR) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Luke Goedeke (OT, TB) — Out [high] — ruled out
- Antoine Winfield Jr. (S, TB) — Out [high] — ruled out
- Bam Martin-Scott (LB, CAR) — Injured Reserve [high] — ruled out
- Cam Jackson (DT, CAR) — Injured Reserve [high] — ruled out
- Christian Rozeboom (LB, TB) — Injured Reserve [high] — ruled out
- Jaelan Phillips (LB, CAR) — Out [high] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Baker Mayfield (QB, TB) — Questionable [high]
- Monroe Freeling (OT, CAR) — Questionable [single_source]

### WEATHER

- Sunny · 66°F · wind 12 mph NE · precip 0%
- forecast vintage 2026-10-24T20:14:14+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 57 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bryce Young | CAR | attempts | 34.8 | 35.0 | 30.0 | 41.0 | 21.0 | 49.0 | 35.9 | 35.0 | 34.8 | 35.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chuba Hubbard | CAR | carries | 16.8 | 17.0 | 12.0 | 22.0 | 5.0 | 29.0 | 17.6 | 17.0 | 16.8 | 17.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | completions | 22.0 | 22.0 | 18.0 | 26.0 | 12.0 | 32.0 | 22.5 | 22.0 | 22.0 | 22.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | passing_tds | 1.6 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.8 | 2.0 | 1.8 | 2.0 | 0.00 | 0.98 | 5 | PRICED |
| Bryce Young | CAR | passing_yards | 243.7 | 239.0 | 189.0 | 295.0 | 119.0 | 384.0 | 259.1 | 254.0 | 259.1 | 254.0 | 0.00 | 0.98 | 9 | PRICED |
| Tetairoa McMillan | CAR | receiving_yards | 65.9 | 57.0 | 29.0 | 93.0 | 0.0 | 160.0 | 76.1 | 69.0 | 76.1 | 66.0 | 0.00 | 0.98 | 13 | PRICED |
| Jalen Coker | CAR | receiving_yards | 52.1 | 43.0 | 20.0 | 75.0 | 0.0 | 134.0 | 73.7 | 66.0 | 73.5 | 61.0 | 0.00 | 0.97 | 12 | PRICED |
| Darren Waller | CAR | receiving_yards | 27.3 | 19.0 | 5.0 | 40.0 | 0.0 | 86.0 | 28.3 | 22.0 | 28.3 | 19.0 | 0.00 | 0.97 | 7 | PRICED |

_8 of 57 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 57 of 90 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT25TBCAR-CARJCOKER18-4` | Jalen Coker | 4.0 | 0.78 | 0.79 | 0.19 | -0.589 |
| `KXNFLRSHATT-26OCT25TBCAR-CARCHUBBARD30-15` | Chuba Hubbard | 15.0 | 0.69 | 0.71 | 0.10 | -0.584 |
| `KXNFLRSHYDS-26OCT25TBCAR-CARCHUBBARD30-40` | Chuba Hubbard | 40.0 | 0.81 | 0.83 | 0.24 | -0.569 |
| `KXNFLREC-26OCT25TBCAR-CARJCOKER18-3` | Jalen Coker | 3.0 | 0.89 | 0.91 | 0.33 | -0.555 |
| `KXNFLREC-26OCT25TBCAR-CARTMCMILLAN4-4` | Tetairoa McMillan | 4.0 | 0.76 | 0.78 | 0.22 | -0.535 |
| `KXNFLRSHYDS-26OCT25TBCAR-CARCHUBBARD30-50` | Chuba Hubbard | 50.0 | 0.69 | 0.71 | 0.17 | -0.518 |

_Ranked 375 tradable markets; 17 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jonathon Brooks (RB, CAR) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Emeka Egbuka (WR, TB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Baker Mayfield (QB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLTD-26OCT25TBCAR-TBCGODWIN14-1 moved +0.140 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.589 on KXNFLREC-26OCT25TBCAR-CARJCOKER18-4 (Jalen Coker). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.584 on KXNFLRSHATT-26OCT25TBCAR-CARCHUBBARD30-15 (Chuba Hubbard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT25TBCAR-CARJCOKER18-3 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_TB_CAR.md`_


---

## DEN @ ARI — `2026_07_DEN_ARI`

- kickoff: 2026-10-25T20:05:00+00:00 (1399 minutes away) · state **PREGAME**
- venue: State Farm Stadium · roof  · surface grass
- markets: 776 listed across 16 families — 418 supported, 302 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 4.67 | 4.71 |
| total | 43.62 | 43.18 |
| score | ARI 19.5 – DEN 24.1 | ARI 19.2 – DEN 23.9 |
| win prob ARI | 33.5% | 33.5% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.95 / total 21.62 · **2H** spread 2.50 / total 21.88 · **1Q** spread 1.30 / total 7.89 · **2Q** spread 1.40 / total 13.00 · **3Q** spread 1.35 / total 8.24 · **4Q** spread 0.93 / total 12.17

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 4.67 · total 43.62

**Game environment** (simulation, mean and middle 50%) — home margin -4.6 (-12.0–3.0) · total 44.5 (35.0–52.0) · P(one score) 51.4% · P(17+ blowout) 20.0% · P(total 10+ over centre) 23.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| ARI | 64.1 (58.0–70.0) | 37.3 (32.0–42.0) | 21.9 (17.0–26.0) | 41.6 (36.0–47.0) | 0.649 (0.585–0.717) | 0.541 / 0.710 |
| DEN | 62.4 (57.0–68.0) | 32.2 (27.0–37.0) | 26.0 (21.0–31.0) | 35.4 (30.0–40.0) | 0.568 (0.500–0.637) | 0.491 / 0.669 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| ARI | 00-0037263 | RB | 2.6 (1.0–4.0) | 10.9 (6.0–15.0) | 7.2% | 50.0% | MEDIUM |
| ARI | 00-0037744 | TE | 10.4 (7.0–14.0) | 0.0 (0.0–0.0) | 28.9% | 0.1% | MEDIUM |
| ARI | 00-0037157 | RB | 1.4 (0.0–2.0) | 8.0 (4.0–11.0) | 3.9% | 36.3% | HIGH |
| ARI | 00-0038559 | WR | 9.0 (5.0–12.0) | 0.1 (0.0–0.0) | 25.0% | 0.4% | MEDIUM |
| DEN | 00-0036158 | RB | 1.9 (0.0–3.0) | 15.6 (10.0–20.0) | 6.2% | 60.1% | MEDIUM |
| DEN | 00-0040730 | RB | 4.1 (2.0–6.0) | 6.5 (2.0–9.0) | 13.6% | 24.9% | HIGH |
| DEN | 00-0036613 | WR | 6.7 (4.0–9.0) | 0.3 (0.0–0.0) | 22.3% | 1.1% | HIGH |
| DEN | 00-0034348 | WR | 4.8 (2.0–7.0) | 0.1 (0.0–0.0) | 16.1% | 0.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 25 market(s), e.g. KXNFLPASSYDS-26OCT25DENARI-DENBNIX10-300, KXNFLPASSYDS-26OCT25DENARI-DENBNIX10-250
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 35 market(s), e.g. KXNFL1HFT-26OCT25DENARI-DENDEN, KXNFL2H-26OCT25DENARI-ARI
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26OCT25DENARI-DEN15, KXNFLSPREAD-26OCT25DENARI-DEN14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLGAME-26OCT25DENARI-DEN, KXNFLSPREAD-26OCT25DENARI-DEN3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 247 market(s), e.g. KXNFL1HFT-26OCT25DENARI-TIEDEN, KXNFL1HSPREAD-26OCT25DENARI-ARI11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 29 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25DENARI-ARI3, KXNFL1HTOTAL-26OCT25DENARI-8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 30.2%  _(final margin within one score (8 points) either way; total within 10 of the centre 43.625 (median favourite-oriented margin +2, median total 43))_
2. favourite controls / normal scoring — 19.0%  _(DEN (favourite) wins by more than one score; total within 10 of the centre 43.625 (median favourite-oriented margin +16, median total 43))_
3. competitive / high scoring — 11.0%  _(final margin within one score (8 points) either way; total 53.625+ (centre 43.625) (median favourite-oriented margin +2, median total 61))_
4. competitive / low scoring — 10.2%  _(final margin within one score (8 points) either way; total 33.625 or fewer (centre 43.625) (median favourite-oriented margin +3, median total 29))_
5. favourite controls / high scoring — 8.5%  _(DEN (favourite) wins by more than one score; total 53.625+ (centre 43.625) (median favourite-oriented margin +16, median total 60))_
   Other — 21.1%

Marginal events (overlapping): one_score 51.4% · blowout_17 20.0% · favorite_wins 66.7% · favorite_controls 35.8% · upset 33.1% · shootout 23.3% · low_scoring 20.7% · low_possession 8.0% · high_volume_passing 12.2% · run_heavy_control 14.1%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 2.90 mph, gusts 7.60, precip prob 0%, temp 80F, forecast retrieved 2026-10-24T20:14:10+00:00 (23.85 h before kickoff)._

**`KXNFLTD-26OCT25DENARI-DENRHARVEY12-1`** RJ Harvey touchdowns 1
- MODEL / MARKET: football 34.6% · market 24.5% · reconciled 27.5%
- SCRIPT ROBUSTNESS: P50 mass 8.5% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 20.0% · failure mass 91.5% · win-contribution HHI 0.188

**`KXNFLTD-26OCT25DENARI-DENJDOBBINS27-1`** J.K. Dobbins touchdowns 1
- MODEL / MARKET: football 44.0% · market 40.5% · reconciled 42.4%
- SCRIPT ROBUSTNESS: P50 mass 38.5% · P55 mass 38.5% · P60 mass 8.5% · major-script floor 26.5% · failure mass 61.5% · win-contribution HHI 0.183

**`KXNFLTD-26OCT25DENARI-ARIJBRISSETT7-1`** Jacoby Brissett touchdowns 1
- MODEL / MARKET: football 13.9% · market 9.5% · reconciled 10.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.6% · failure mass 100.0% · win-contribution HHI 0.179

**`KXNFLTD-26OCT25DENARI-ARITMCBRIDE85-1`** Trey McBride touchdowns 1
- MODEL / MARKET: football 35.4% · market 39.5% · reconciled 38.2%
- SCRIPT ROBUSTNESS: P50 mass 14.8% · P55 mass 3.8% · P60 mass 0.0% · major-script floor 24.5% · failure mass 85.2% · win-contribution HHI 0.185
- THESIS DEPENDENCY with `KXNFLPASSTDS-26OCT25DENARI-ARIJBRISSETT7-2`: cash correlation 0.381 · joint cash 23.4% · Jaccard of winning rows 0.443 · shared failure 47.2%

_408 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 45 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Jeremiyah Love (RB, ARI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jonah Coleman (RB, DEN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Tyler Badie (RB, DEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jon Gaines II (G, ARI) — Out [high] — ruled out
- Andrew Wingard (S, ARI) — Out [high] — ruled out
- Jonah Elliss (LB, DEN) — Out [high] — ruled out
- Talanoa Hufanga (S, DEN) — Out [high] — ruled out
- Walter Nolen III (DT, ARI) — Out [high] — ruled out

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Carson Beck (QB, ARI) — Questionable [high]
- Budda Baker (S, ARI) — Questionable [high]
- Darius Robinson (DE, ARI) — Questionable [high]
- Max Melton (CB, ARI) — Questionable [high]
- Pat Surtain II (CB, DEN) — Questionable [high]

### WEATHER

- retractable roof (State Farm Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Sunny · 81°F · wind 0 mph  · precip 0%
- forecast vintage 2026-10-24T20:15:22+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 80, 'wind': '0 mph', 'precipitation_probability': 0})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 65 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jacoby Brissett | ARI | attempts | 35.8 | 36.0 | 31.0 | 42.0 | 21.0 | 49.0 | 37.0 | 37.0 | 35.8 | 36.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyler Allgeier | ARI | carries | 10.9 | 10.0 | 6.0 | 15.0 | 2.0 | 22.0 | 9.5 | 9.0 | 10.9 | 10.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bam Knight | ARI | carries | 8.0 | 7.0 | 4.0 | 11.0 | 0.0 | 19.0 | 10.3 | 10.0 | 8.0 | 7.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | ARI | completions | 22.7 | 23.0 | 19.0 | 27.0 | 13.0 | 33.0 | 23.6 | 23.0 | 22.7 | 23.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | ARI | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Jacoby Brissett | ARI | passing_yards | 226.4 | 223.0 | 176.0 | 274.0 | 109.0 | 356.0 | 230.4 | 224.0 | 230.4 | 227.0 | 0.00 | 0.97 | 10 | PRICED |
| Trey McBride | ARI | receiving_yards | 67.0 | 61.0 | 35.0 | 92.0 | 6.0 | 147.0 | 67.0 | 61.0 | 67.0 | 61.0 | 0.00 | 0.97 | 11 | PRICED |
| Michael Wilson | ARI | receiving_yards | 64.5 | 56.0 | 30.0 | 90.0 | 0.0 | 154.0 | 55.5 | 48.0 | 55.5 | 48.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 65 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 65 of 105 listed player/stat groups simulated and exposed, 40 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT25DENARI-ARITMCBRIDE85-5` | Trey McBride | 5.0 | 0.82 | 0.84 | 0.24 | -0.579 |
| `KXNFLREC-26OCT25DENARI-ARITMCBRIDE85-6` | Trey McBride | 6.0 | 0.70 | 0.72 | 0.13 | -0.573 |
| `KXNFLREC-26OCT25DENARI-DENRHARVEY12-2` | RJ Harvey | 2.0 | 0.86 | 0.88 | 0.34 | -0.521 |
| `KXNFLREC-26OCT25DENARI-ARITMCBRIDE85-4` | Trey McBride | 4.0 | 0.91 | 0.93 | 0.40 | -0.504 |
| `KXNFLREC-26OCT25DENARI-DENRHARVEY12-3` | RJ Harvey | 3.0 | 0.70 | 0.71 | 0.20 | -0.497 |
| `KXNFLRSHATT-26OCT25DENARI-DENJDOBBINS27-11` | J.K. Dobbins | 11.0 | 0.78 | 0.80 | 0.29 | -0.486 |

_Ranked 397 tradable markets; 21 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jeremiyah Love (RB, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Tyler Badie (RB, DEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Carson Beck (QB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
5. KXNFLRSHATT-26OCT25DENARI-ARITALLGEIER22-14 moved -0.300 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
6. The model disagrees by -0.579 on KXNFLREC-26OCT25DENARI-ARITMCBRIDE85-5 (Trey McBride). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. The model disagrees by -0.573 on KXNFLREC-26OCT25DENARI-ARITMCBRIDE85-6 (Trey McBride). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
8. KXNFLREC-26OCT25DENARI-ARITMCBRIDE85-4 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_DEN_ARI.md`_


---

## GB @ DET — `2026_07_GB_DET`

- kickoff: 2026-10-25T20:25:00+00:00 (1419 minutes away) · state **PREGAME**
- venue: Ford Field · roof dome · surface fieldturf
- markets: 737 listed across 16 families — 399 supported, 282 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.44 | -3.44 |
| total | 54.17 | 54.26 |
| score | DET 28.8 – GB 25.4 | DET 28.9 – GB 25.4 |
| win prob DET | 62.5% | 62.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -2.86 / total 27.45 · **2H** spread -0.92 / total 27.30 · **1Q** spread -1.83 / total 10.06 · **2Q** spread -1.58 / total 15.97 · **3Q** spread -0.52 / total 10.68 · **4Q** spread -0.43 / total 15.00

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.44 · total 54.17
- move `KXNFL1HTEAMTOTAL-26OCT25GBDET-GB31` -0.105

**Game environment** (simulation, mean and middle 50%) — home margin 3.6 (-4.0–11.0) · total 55.7 (46.0–64.0) · P(one score) 51.9% · P(17+ blowout) 17.6% · P(total 10+ over centre) 23.9%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| DET | 65.9 (60.0–72.0) | 36.4 (31.0–42.0) | 25.7 (21.0–30.0) | 39.3 (34.0–45.0) | 0.597 (0.529–0.665) | 0.514 / 0.688 |
| GB | 63.2 (57.0–69.0) | 36.4 (31.0–41.0) | 22.6 (18.0–27.0) | 39.9 (34.0–45.0) | 0.633 (0.568–0.700) | 0.528 / 0.700 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| DET | 00-0039139 | RB | 5.8 (3.0–8.0) | 20.2 (15.0–25.0) | 16.6% | 78.8% | LOW |
| DET | 00-0036963 | WR | 10.4 (7.0–14.0) | 0.1 (0.0–0.0) | 29.6% | 0.3% | MEDIUM |
| DET | 00-0039065 | TE | 6.2 (3.0–9.0) | 0.0 (0.0–0.0) | 17.6% | 0.0% | HIGH |
| DET | 00-0037240 | WR | 5.4 (3.0–8.0) | 0.1 (0.0–0.0) | 15.5% | 0.5% | HIGH |
| GB | 00-0039811 | RB | 2.6 (1.0–4.0) | 8.4 (4.0–12.0) | 7.3% | 37.2% | MEDIUM |
| GB | 00-0038098 | RB | 3.5 (1.0–5.0) | 6.4 (3.0–9.0) | 9.9% | 28.5% | HIGH |
| GB | 00-0040667 | WR | 7.8 (4.0–11.0) | 0.2 (0.0–0.0) | 22.3% | 1.1% | MEDIUM |
| GB | 00-0038124 | WR | 7.9 (5.0–11.0) | 0.1 (0.0–0.0) | 22.5% | 0.4% | MEDIUM |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 5 market(s), e.g. KXNFLRSHYDS-26OCT25GBDET-GBJLOVE10-25, KXNFLRSHYDS-26OCT25GBDET-GBJLOVE10-20
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 53 market(s), e.g. KXNFL1HFT-26OCT25GBDET-GBGB, KXNFL1HFT-26OCT25GBDET-DETDET
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26OCT25GBDET-GB8, KXNFLSPREAD-26OCT25GBDET-GB7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLGAME-26OCT25GBDET-DET, KXNFLTEAMTOTAL-26OCT25GBDET-GB22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 204 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25GBDET-DET28, KXNFL1HTOTAL-26OCT25GBDET-43
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 49 market(s), e.g. KXNFL2HTOTAL-26OCT25GBDET-15, KXNFL2QTOTAL-26OCT25GBDET-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 28.6%  _(final margin within one score (8 points) either way; total within 10 of the centre 54.1667 (median favourite-oriented margin +2, median total 54))_
2. favourite controls / normal scoring — 19.4%  _(DET (favourite) wins by more than one score; total within 10 of the centre 54.1667 (median favourite-oriented margin +14, median total 54))_
3. competitive / high scoring — 12.0%  _(final margin within one score (8 points) either way; total 64.1667+ (centre 54.1667) (median favourite-oriented margin +2, median total 72))_
4. competitive / low scoring — 11.3%  _(final margin within one score (8 points) either way; total 44.1667 or fewer (centre 54.1667) (median favourite-oriented margin +2, median total 39))_
5. underdog controls / normal scoring — 7.8%  _(GB (underdog) wins by more than one score; total within 10 of the centre 54.1667 (median favourite-oriented margin -14, median total 56))_
   Other — 20.9%

Marginal events (overlapping): one_score 51.9% · blowout_17 17.6% · favorite_wins 63.8% · favorite_controls 32.7% · upset 36.0% · shootout 23.9% · low_scoring 20.3% · low_possession 4.3% · high_volume_passing 22.3% · run_heavy_control 13.8%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 9.00 mph, gusts 12.10, precip prob 1%, temp 67F, forecast retrieved 2026-10-24T20:14:10+00:00 (24.18 h before kickoff)._

**`KXNFLTD-26OCT25GBDET-DETJGOFF16-1`** Jared Goff touchdowns 1
- MODEL / MARKET: football 10.5% · market 7.5% · reconciled 18.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.2% · failure mass 100.0% · win-contribution HHI 0.177

**`KXNFLTD-26OCT25GBDET-GBMLLOYD32-1`** MarShawn Lloyd touchdowns 1
- MODEL / MARKET: football 38.2% · market 18.5% · reconciled 24.8%
- SCRIPT ROBUSTNESS: P50 mass 24.0% · P55 mass 4.2% · P60 mass 4.2% · major-script floor 27.4% · failure mass 76.0% · win-contribution HHI 0.166

**`KXNFLTD-26OCT25GBDET-GBPSTRONG22-1`** Pierre Strong Jr. touchdowns 1
- MODEL / MARKET: football 26.9% · market 16.5% · reconciled 19.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 19.6% · failure mass 100.0% · win-contribution HHI 0.165

**`KXNFLTD-26OCT25GBDET-DETJGIBBS0-1`** Jahmyr Gibbs touchdowns 1
- MODEL / MARKET: football 71.0% · market 74.5% · reconciled 72.1%
- SCRIPT ROBUSTNESS: P50 mass 96.6% · P55 mass 85.3% · P60 mass 77.5% · major-script floor 53.4% · failure mass 3.4% · win-contribution HHI 0.173

_389 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 40 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (11)**

- Luke Musgrave (TE, GB) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tom Kennedy (WR, DET) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Ben Bartch (G, DET) — Injured Reserve [high] — ruled out
- Cade Mays (C, DET) — Injured Reserve [high] — ruled out
- Brian Branch (S, DET) — Out [high] — ruled out
- Devin White (LB, DET) — Injured Reserve [high] — ruled out
- Javon Hargrave (DT, GB) — Injured Reserve [high] — ruled out
- Jonathan Ford (DT, GB) — Injured Reserve [high] — ruled out
- _...and 3 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Bo Melton (WR, GB) — Questionable [high]
- Aaron Banks (G, GB) — Questionable [high]
- Benjamin St-Juste (CB, GB) — Questionable [high]
- Jordon Riley (DT, GB) — Questionable [high]

### WEATHER

fixed-roof stadium (Ford Field) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 56 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jared Goff | DET | attempts | 35.0 | 35.0 | 30.0 | 41.0 | 21.0 | 49.0 | 37.3 | 37.0 | 35.0 | 35.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jahmyr Gibbs | DET | carries | 20.2 | 20.0 | 15.0 | 25.0 | 7.0 | 34.0 | 20.4 | 20.0 | 20.2 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jared Goff | DET | completions | 23.5 | 24.0 | 19.0 | 28.0 | 13.0 | 34.0 | 25.6 | 25.0 | 23.5 | 24.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jared Goff | DET | passing_tds | 2.0 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.2 | 2.0 | 2.2 | 2.0 | 0.00 | 0.98 | 5 | PRICED |
| Jared Goff | DET | passing_yards | 257.9 | 254.0 | 201.0 | 311.0 | 126.0 | 404.0 | 283.8 | 281.0 | 283.8 | 280.0 | 0.00 | 0.98 | 9 | PRICED |
| Amon-Ra St. Brown | DET | receiving_yards | 81.7 | 74.0 | 43.0 | 113.0 | 9.0 | 179.0 | 84.0 | 78.0 | 84.0 | 76.0 | 0.00 | 0.97 | 13 | PRICED |
| Jameson Williams | DET | receiving_yards | 48.5 | 38.0 | 14.0 | 71.0 | 0.0 | 136.0 | 60.7 | 52.0 | 60.7 | 47.0 | 0.00 | 0.97 | 14 | PRICED |
| Sam LaPorta | DET | receiving_yards | 47.9 | 40.0 | 18.0 | 69.0 | 0.0 | 124.0 | 55.4 | 50.0 | 55.4 | 46.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 56 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 56 of 90 listed player/stat groups simulated and exposed, 34 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT25GBDET-GBSWILLIAMS83-2` | Savion Williams | 2.0 | 0.67 | 0.70 | 0.01 | -0.660 |
| `KXNFLREC-26OCT25GBDET-GBMGOLDEN0-3` | Matthew Golden | 3.0 | 0.86 | 0.90 | 0.22 | -0.641 |
| `KXNFLRECYDS-26OCT25GBDET-GBSWILLIAMS83-15` | Savion Williams | 15.0 | 0.64 | 0.64 | 0.01 | -0.625 |
| `KXNFLRECYDS-26OCT25GBDET-GBMGOLDEN0-40` | Matthew Golden | 40.0 | 0.81 | 0.83 | 0.19 | -0.621 |
| `KXNFLRECYDS-26OCT25GBDET-GBMGOLDEN0-50` | Matthew Golden | 50.0 | 0.72 | 0.74 | 0.12 | -0.609 |
| `KXNFLREC-26OCT25GBDET-GBMGOLDEN0-4` | Matthew Golden | 4.0 | 0.73 | 0.77 | 0.13 | -0.602 |

_Ranked 395 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Tom Kennedy (WR, DET) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Luke Musgrave (TE, GB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Bo Melton (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRECYDS-26OCT25GBDET-GBTKRAFT85-70 moved +0.145 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.660 on KXNFLREC-26OCT25GBDET-GBSWILLIAMS83-2 (Savion Williams). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.641 on KXNFLREC-26OCT25GBDET-GBMGOLDEN0-3 (Matthew Golden). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT25GBDET-GBTKRAFT85-2 sits at a market price of 0.93 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_GB_DET.md`_


---

## LA @ LV — `2026_07_LA_LV`

- kickoff: 2026-10-25T20:25:00+00:00 (1419 minutes away) · state **PREGAME**
- venue: Allegiant Stadium · roof dome · surface grass
- markets: 741 listed across 16 families — 397 supported, 288 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.09 | 3.14 |
| total | 48.88 | 49.01 |
| score | LV 22.9 – LA 26.0 | LV 22.9 – LA 26.1 |
| win prob LV | 39.5% | 37.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.50 / total 24.13 · **2H** spread 1.40 / total 24.33 · **1Q** spread 0.94 / total 8.77 · **2Q** spread 0.70 / total 14.58 · **3Q** spread 0.87 / total 9.42 · **4Q** spread 0.29 / total 14.06

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 3.09 · total 48.88
- move `KXNFLSPREAD-26OCT25LARLV-LAR10` -0.130

**Game environment** (simulation, mean and middle 50%) — home margin -3.2 (-11.0–4.0) · total 49.5 (40.0–57.0) · P(one score) 54.1% · P(17+ blowout) 19.0% · P(total 10+ over centre) 23.0%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| LV | 62.9 (57.0–69.0) | 35.9 (31.0–41.0) | 23.9 (19.0–28.0) | 38.4 (33.0–44.0) | 0.612 (0.546–0.679) | 0.507 / 0.678 |
| LA | 65.2 (59.0–71.0) | 36.4 (31.0–41.0) | 25.3 (20.0–30.0) | 39.0 (33.0–44.0) | 0.598 (0.531–0.666) | 0.519 / 0.687 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| LV | 00-0040122 | RB | 4.9 (2.0–7.0) | 14.7 (9.0–19.0) | 14.4% | 61.6% | MEDIUM |
| LV | 00-0039338 | TE | 8.1 (5.0–11.0) | 0.0 (0.0–0.0) | 23.7% | 0.1% | MEDIUM |
| LV | 00-0040878 | RB | 0.8 (0.0–1.0) | 5.3 (0.0–8.0) | 2.5% | 22.2% | HIGH |
| LV | 00-0038563 | WR | 5.7 (3.0–8.0) | 0.5 (0.0–0.0) | 16.5% | 1.9% | HIGH |
| LA | 00-0037840 | RB | 5.4 (2.0–8.0) | 13.8 (9.0–18.0) | 15.5% | 54.5% | MEDIUM |
| LA | 00-0039738 | RB | 2.0 (0.0–3.0) | 8.3 (4.0–12.0) | 5.8% | 32.9% | HIGH |
| LA | 00-0039075 | WR | 9.3 (4.0–14.0) | 0.5 (0.0–0.0) | 26.6% | 2.1% | HIGH |
| LA | 00-0033110 | TE | 5.3 (2.0–7.0) | 0.1 (0.0–0.0) | 15.3% | 0.2% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 4 market(s), e.g. KXNFLPASSCOMP-26OCT25LARLV-LARMSTAFFORD9-19, KXNFLRSHYDS-26OCT25LARLV-LVKCOUSINS8-15
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 62 market(s), e.g. KXNFL1HFT-26OCT25LARLV-LVLV, KXNFL1Q-26OCT25LARLV-LV
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26OCT25LARLV-LV7, KXNFLSPREAD-26OCT25LARLV-LV6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLGAME-26OCT25LARLV-LAR, KXNFLTEAMTOTAL-26OCT25LARLV-LAR22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 233 market(s), e.g. KXNFL1H-26OCT25LARLV-TIE, KXNFL1HFT-26OCT25LARLV-TIELAR
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 47 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25LARLV-LAR3, KXNFL2QTOTAL-26OCT25LARLV-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 48.875 (median favourite-oriented margin +2, median total 48))_
2. favourite controls / normal scoring — 16.9%  _(LA (favourite) wins by more than one score; total within 10 of the centre 48.875 (median favourite-oriented margin +15, median total 49))_
3. competitive / high scoring — 11.2%  _(final margin within one score (8 points) either way; total 58.875+ (centre 48.875) (median favourite-oriented margin +1, median total 66))_
4. competitive / low scoring — 10.9%  _(final margin within one score (8 points) either way; total 38.875 or fewer (centre 48.875) (median favourite-oriented margin +2, median total 34))_
5. underdog controls / normal scoring — 8.0%  _(LV (underdog) wins by more than one score; total within 10 of the centre 48.875 (median favourite-oriented margin -16, median total 48))_
   Other — 21.0%

Marginal events (overlapping): one_score 54.1% · blowout_17 19.0% · favorite_wins 63.1% · favorite_controls 31.3% · upset 36.7% · shootout 23.0% · low_scoring 20.2% · low_possession 5.5% · high_volume_passing 20.4% · run_heavy_control 13.9%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 3.10 mph, gusts 5.60, precip prob 0%, temp 73F, forecast retrieved 2026-10-24T20:14:10+00:00 (24.18 h before kickoff)._

**`KXNFLTD-26OCT25LARLV-LVDLAUBE23-1`** Dylan Laube touchdowns 1
- MODEL / MARKET: football 8.7% · market 7.5% · reconciled 22.4%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.8% · failure mass 100.0% · win-contribution HHI 0.176

**`KXNFLTD-26OCT25LARLV-LVCWHITE82-1`** Cody White touchdowns 1
- MODEL / MARKET: football 11.8% · market 8.5% · reconciled 23.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.6% · failure mass 100.0% · win-contribution HHI 0.178

**`KXNFLTD-26OCT25LARLV-LVAJEANTY2-1`** Ashton Jeanty touchdowns 1
- MODEL / MARKET: football 45.0% · market 53.0% · reconciled 49.7%
- SCRIPT ROBUSTNESS: P50 mass 25.8% · P55 mass 23.4% · P60 mass 23.4% · major-script floor 32.7% · failure mass 74.2% · win-contribution HHI 0.183

**`KXNFLTD-26OCT25LARLV-LVBBOWERS89-1`** Brock Bowers touchdowns 1
- MODEL / MARKET: football 32.5% · market 44.5% · reconciled 41.7%
- SCRIPT ROBUSTNESS: P50 mass 4.2% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 21.5% · failure mass 95.8% · win-contribution HHI 0.187
- THESIS DEPENDENCY with `KXNFLPASSTDS-26OCT25LARLV-LVKCOUSINS8-2`: cash correlation 0.322 · joint cash 22.9% · Jaccard of winning rows 0.403 · shared failure 43.1%

_387 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 44 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Carter Runyon (TE, LV) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Davante Adams (WR, LA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Dont'e Thornton Jr. (WR, LV) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Terrance Ferguson (TE, LA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Blake Grupe (PK, LA) — Injured Reserve [single_source] — ruled out
- Kobie Turner (DE, LA) — Injured Reserve [single_source] — ruled out
- Myles Garrett (DE, LA) — Injured Reserve [single_source] — ruled out
- Nate Landman (LB, LA) — Out [single_source] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Mike Washington Jr. (RB, LV) — Questionable [high]
- Puka Nacua (WR, LA) — Questionable [single_source]
- Quay Walker (LB, LV) — Questionable [high]
- Trent McDuffie (CB, LA) — Questionable [single_source]

### WEATHER

fixed-roof stadium (Allegiant Stadium) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 62 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Matthew Stafford | LA | attempts | 35.0 | 35.0 | 30.0 | 41.0 | 21.0 | 49.0 | 35.0 | 35.0 | 35.0 | 35.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kyren Williams | LA | carries | 13.8 | 13.0 | 9.0 | 18.0 | 3.0 | 27.0 | 16.7 | 16.0 | 13.8 | 13.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Blake Corum | LA | carries | 8.3 | 7.0 | 4.0 | 12.0 | 0.0 | 20.0 | 8.7 | 8.0 | 8.3 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Matthew Stafford | LA | completions | 23.6 | 24.0 | 20.0 | 28.0 | 13.0 | 34.0 | 24.7 | 23.0 | 23.6 | 24.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Matthew Stafford | LA | passing_tds | 1.8 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.9 | 2.0 | 1.9 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Matthew Stafford | LA | passing_yards | 254.3 | 250.0 | 197.0 | 307.0 | 123.0 | 403.0 | 260.3 | 255.0 | 260.2 | 255.0 | 0.00 | 0.97 | 10 | PRICED |
| Puka Nacua | LA | receiving_yards | 79.1 | 74.0 | 20.0 | 121.0 | 0.0 | 201.0 | 100.6 | 94.0 | 99.8 | 93.0 | 0.00 | 0.78 | 16 | PRICED |
| Tyler Higbee | LA | receiving_yards | 41.3 | 31.0 | 12.0 | 60.0 | 0.0 | 117.0 | 53.4 | 43.0 | 53.4 | 41.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 62 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 62 of 96 listed player/stat groups simulated and exposed, 34 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT25LARLV-LVBBOWERS89-4` | Brock Bowers | 4.0 | 0.83 | 0.88 | 0.24 | -0.586 |
| `KXNFLREC-26OCT25LARLV-LVBBOWERS89-5` | Brock Bowers | 5.0 | 0.72 | 0.75 | 0.13 | -0.583 |
| `KXNFLREC-26OCT25LARLV-LARKWILLIAMS23-3` | Kyren Williams | 3.0 | 0.72 | 0.74 | 0.17 | -0.545 |
| `KXNFLRECYDS-26OCT25LARLV-LARKWILLIAMS23-15` | Kyren Williams | 15.0 | 0.75 | 0.77 | 0.21 | -0.539 |
| `KXNFLREC-26OCT25LARLV-LVMMAYER87-2` | Michael Mayer | 2.0 | 0.88 | 0.91 | 0.37 | -0.512 |
| `KXNFLREC-26OCT25LARLV-LVBBOWERS89-6` | Brock Bowers | 6.0 | 0.57 | 0.59 | 0.07 | -0.508 |

_Ranked 302 tradable markets; 95 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Davante Adams (WR, LA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Terrance Ferguson (TE, LA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Puka Nacua (WR), Mike Washington Jr. (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRECYDS-26OCT25LARLV-LARKMUMPFIELD4-50 moved +0.390 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.586 on KXNFLREC-26OCT25LARLV-LVBBOWERS89-4 (Brock Bowers). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.583 on KXNFLREC-26OCT25LARLV-LVBBOWERS89-5 (Brock Bowers). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT25LARLV-LVMMAYER87-2 sits at a market price of 0.88 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_LA_LV.md`_


---

## KC @ SEA — `2026_07_KC_SEA`

- kickoff: 2026-10-26T00:20:00+00:00 (1654 minutes away) · state **PREGAME**
- venue: Lumen Field · roof outdoors · surface fieldturf
- markets: 749 listed across 16 families — 403 supported, 290 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.85 | -2.34 |
| total | 43.12 | 42.93 |
| score | SEA 23.0 – KC 20.1 | SEA 22.6 – KC 20.3 |
| win prob SEA | 58.5% | 57.7% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -1.72 / total 21.10 · **2H** spread -1.16 / total 21.00 · **1Q** spread -0.87 / total 7.76 · **2Q** spread -1.09 / total 12.44 · **3Q** spread -0.60 / total 7.97 · **4Q** spread -0.10 / total 11.72

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -2.85 · total 43.12

**Game environment** (simulation, mean and middle 50%) — home margin 2.6 (-5.0–10.0) · total 44.7 (36.0–53.0) · P(one score) 52.5% · P(17+ blowout) 17.9% · P(total 10+ over centre) 23.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| SEA | 63.3 (58.0–69.0) | 33.1 (28.0–38.0) | 26.0 (21.0–31.0) | 36.4 (31.0–42.0) | 0.575 (0.507–0.645) | 0.484 / 0.664 |
| KC | 62.1 (56.0–68.0) | 34.5 (29.0–39.0) | 21.5 (17.0–26.0) | 39.9 (34.0–45.0) | 0.643 (0.577–0.710) | 0.542 / 0.714 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| SEA | 00-0038797 | RB | 1.8 (0.0–3.0) | 14.9 (10.0–20.0) | 5.8% | 57.5% | MEDIUM |
| SEA | 00-0038543 | WR | 10.1 (7.0–13.0) | 0.2 (0.0–0.0) | 32.1% | 0.9% | MEDIUM |
| SEA | 00-0039299 | RB | 1.8 (0.0–3.0) | 4.7 (1.0–7.0) | 5.8% | 18.0% | HIGH |
| SEA | 00-0037545 | WR | 4.3 (2.0–6.0) | 0.8 (0.0–1.0) | 13.6% | 3.1% | HIGH |
| KC | 00-0038134 | RB | 5.0 (2.0–7.0) | 15.8 (11.0–20.0) | 15.2% | 73.2% | MEDIUM |
| KC | 00-0039894 | WR | 7.0 (4.0–9.0) | 0.2 (0.0–0.0) | 21.3% | 1.0% | HIGH |
| KC | 00-0030506 | TE | 6.9 (4.0–9.0) | 0.0 (0.0–0.0) | 21.3% | 0.0% | HIGH |
| KC | 00-0041013 | RB | 2.4 (0.0–3.0) | 3.1 (0.0–4.0) | 7.2% | 14.4% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 12 market(s), e.g. KXNFLRECYDS-26OCT25KCSEA-KCCALLEN13-30, KXNFLRECYDS-26OCT25KCSEA-KCCALLEN13-25
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 41 market(s), e.g. KXNFL1HFT-26OCT25KCSEA-SEASEA, KXNFL3Q-26OCT25KCSEA-TIE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT25KCSEA-SEA8, KXNFLSPREAD-26OCT25KCSEA-SEA17
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTOTAL-26OCT25KCSEA-37, KXNFLTEAMTOTAL-26OCT25KCSEA-SEA18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 236 market(s), e.g. KXNFL1HFT-26OCT25KCSEA-TIESEA, KXNFL1HSPREAD-26OCT25KCSEA-KC11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 34 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT25KCSEA-KC3, KXNFL1HTOTAL-26OCT25KCSEA-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.3%  _(final margin within one score (8 points) either way; total within 10 of the centre 43.125 (median favourite-oriented margin +1, median total 43))_
2. favourite controls / normal scoring — 17.8%  _(SEA (favourite) wins by more than one score; total within 10 of the centre 43.125 (median favourite-oriented margin +14, median total 43))_
3. competitive / low scoring — 11.6%  _(final margin within one score (8 points) either way; total 33.125 or fewer (centre 43.125) (median favourite-oriented margin +2, median total 28))_
4. competitive / high scoring — 11.5%  _(final margin within one score (8 points) either way; total 53.125+ (centre 43.125) (median favourite-oriented margin +1, median total 62))_
5. underdog controls / normal scoring — 9.6%  _(KC (underdog) wins by more than one score; total within 10 of the centre 43.125 (median favourite-oriented margin -13, median total 45))_
   Other — 20.1%

Marginal events (overlapping): one_score 52.5% · blowout_17 17.9% · favorite_wins 60.2% · favorite_controls 29.7% · upset 39.6% · shootout 23.1% · low_scoring 20.2% · low_possession 10.2% · high_volume_passing 8.4% · run_heavy_control 13.2%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 6.20 mph, gusts 13.40, precip prob 30%, temp 52F, forecast retrieved 2026-10-24T20:14:10+00:00 (28.10 h before kickoff)._

**`KXNFLTD-26OCT25KCSEA-SEAEWILSON23-2`** Emanuel Wilson touchdowns 2
- MODEL / MARKET: football 12.1% · market 8.5% · reconciled 10.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 2.6% · failure mass 100.0% · win-contribution HHI 0.203

**`KXNFLTD-26OCT25KCSEA-SEAABARNER88-1`** AJ Barner touchdowns 1
- MODEL / MARKET: football 17.9% · market 24.5% · reconciled 23.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 10.2% · failure mass 100.0% · win-contribution HHI 0.175

**`KXNFLTD-26OCT25KCSEA-SEAGHOLANI36-1`** George Holani touchdowns 1
- MODEL / MARKET: football 20.9% · market 16.5% · reconciled 17.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 11.5% · failure mass 100.0% · win-contribution HHI 0.179

**`KXNFLTD-26OCT25KCSEA-KCKWALKER9-1`** Kenneth Walker III touchdowns 1
- MODEL / MARKET: football 49.9% · market 53.5% · reconciled 52.2%
- SCRIPT ROBUSTNESS: P50 mass 66.1% · P55 mass 25.3% · P60 mass 25.3% · major-script floor 33.1% · failure mass 33.9% · win-contribution HHI 0.171
- THESIS DEPENDENCY with `KXNFLTEAMTOTAL-26OCT25KCSEA-KC21`: cash correlation 0.304 · joint cash 33.4% · Jaccard of winning rows 0.490 · shared failure 31.8%

_393 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 48 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Brashard Smith (RB, KC) — Injured Reserve [high] · **CHANGED from Out** — ruled out -- role redistributes to the depth chart behind him
- Elijah Arroyo (TE, SEA) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Rashee Rice (WR, KC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Zach Charbonnet (RB, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Anthony Bradford (G, SEA) — Injured Reserve [high] — ruled out
- Jaylon Moore (OT, KC) — Out [high] — ruled out
- Josh Simmons (OT, KC) — Injured Reserve [high] — ruled out
- Chazz Surratt (LB, SEA) — Out [high] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (6)** — resolves at the inactive release, T−90m

- Drew Lock (QB, SEA) — Questionable [high]
- Connor O'Toole (LB, SEA) — Questionable [high]
- DeMarcus Lawrence (LB, SEA) — Questionable [high]
- L'Jarius Sneed (CB, KC) — Questionable [high]
- Nick Emmanwori (S, SEA) — Questionable [high]
- Uchenna Nwosu (LB, SEA) — Questionable [high]

### WEATHER

- Chance Light Rain · 55°F · wind 2 mph NW · precip 32%
- forecast vintage 2026-10-24T20:15:27+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 55, 'wind': '2 mph', 'precipitation_probability': 37})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 61 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Patrick Mahomes | KC | attempts | 33.3 | 33.0 | 28.0 | 39.0 | 20.0 | 46.0 | 32.2 | 32.0 | 33.3 | 33.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kenneth Walker III | KC | carries | 15.8 | 15.0 | 11.0 | 20.0 | 5.0 | 28.0 | 18.9 | 18.0 | 15.8 | 15.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | carries | 4.0 | 4.0 | 2.0 | 5.0 | 1.0 | 8.0 | 3.5 | 3.0 | 4.0 | 4.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | completions | 21.4 | 21.0 | 18.0 | 25.0 | 12.0 | 31.0 | 20.7 | 20.0 | 21.4 | 21.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.3 | 1.0 | 1.3 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Patrick Mahomes | KC | passing_yards | 212.7 | 208.0 | 164.0 | 258.0 | 102.0 | 337.0 | 222.5 | 216.0 | 222.5 | 217.0 | 0.00 | 0.97 | 9 | PRICED |
| Xavier Worthy | KC | receiving_yards | 50.7 | 43.0 | 21.0 | 72.0 | 0.0 | 127.0 | 55.4 | 48.0 | 55.4 | 47.0 | 0.00 | 0.98 | 12 | PRICED |
| Travis Kelce | KC | receiving_yards | 50.6 | 43.0 | 22.0 | 71.0 | 0.0 | 125.0 | 52.3 | 46.0 | 52.3 | 45.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 61 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 61 of 95 listed player/stat groups simulated and exposed, 34 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT25KCSEA-KCKWALKER9-16` | Kenneth Walker III | 16.0 | 0.70 | 0.72 | 0.11 | -0.597 |
| `KXNFLREC-26OCT25KCSEA-SEAJSMITHNJIGBA11-6` | Jaxon Smith-Njigba | 6.0 | 0.70 | 0.72 | 0.17 | -0.527 |
| `KXNFLREC-26OCT25KCSEA-KCKWALKER9-2` | Kenneth Walker III | 2.0 | 0.83 | 0.86 | 0.31 | -0.526 |
| `KXNFLREC-26OCT25KCSEA-KCXWORTHY1-3` | Xavier Worthy | 3.0 | 0.82 | 0.86 | 0.30 | -0.522 |
| `KXNFLRSHYDS-26OCT25KCSEA-KCKWALKER9-60` | Kenneth Walker III | 60.0 | 0.74 | 0.75 | 0.23 | -0.515 |
| `KXNFLREC-26OCT25KCSEA-SEAJSMITHNJIGBA11-5` | Jaxon Smith-Njigba | 5.0 | 0.81 | 0.84 | 0.30 | -0.514 |

_Ranked 383 tradable markets; 20 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Rashee Rice (WR, KC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Brashard Smith (RB, KC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Drew Lock (QB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
5. KXNFLRSHYDS-26OCT25KCSEA-SEAEWILSON23-40 moved +0.415 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
6. The model disagrees by -0.597 on KXNFLRSHATT-26OCT25KCSEA-KCKWALKER9-16 (Kenneth Walker III). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. The model disagrees by -0.527 on KXNFLREC-26OCT25KCSEA-SEAJSMITHNJIGBA11-6 (Jaxon Smith-Njigba). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
8. KXNFLREC-26OCT25KCSEA-SEAJSMITHNJIGBA11-4 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_KC_SEA.md`_


---

## DAL @ PHI — `2026_07_DAL_PHI`

- kickoff: 2026-10-27T00:15:00+00:00 (3089 minutes away) · state **PREGAME**
- venue: Lincoln Financial Field · roof outdoors · surface grass
- markets: 641 listed across 16 families — 318 supported, 267 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 4.75 | 4.76 |
| total | 44.44 | 44.03 |
| score | PHI 19.8 – DAL 24.6 | PHI 19.6 – DAL 24.4 |
| win prob PHI | 34.5% | 33.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 3.06 / total 22.50 · **2H** spread 2.37 / total 22.20 · **1Q** spread 1.48 / total 7.97 · **2Q** spread 1.19 / total 13.25 · **3Q** spread 1.17 / total 8.62 · **4Q** spread 0.76 / total 12.36

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 4.75 · total 44.44

**Game environment** (simulation, mean and middle 50%) — home margin -4.5 (-12.0–3.0) · total 45.7 (36.0–54.0) · P(one score) 51.3% · P(17+ blowout) 19.9% · P(total 10+ over centre) 23.6%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| PHI | 61.5 (56.0–67.0) | 34.8 (30.0–40.0) | 23.0 (18.0–27.0) | 37.9 (33.0–43.0) | 0.617 (0.552–0.684) | 0.511 / 0.679 |
| DAL | 65.1 (59.0–71.0) | 36.0 (31.0–41.0) | 25.1 (20.0–30.0) | 39.0 (33.0–44.0) | 0.599 (0.532–0.667) | 0.522 / 0.699 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| PHI | 00-0037258 | RB | 3.9 (1.0–6.0) | 11.7 (7.0–16.0) | 11.8% | 50.9% | MEDIUM |
| PHI | 00-0034844 | RB | 2.9 (1.0–4.0) | 9.1 (5.0–13.0) | 8.8% | 39.6% | MEDIUM |
| PHI | 00-0034351 | TE | 7.7 (4.0–10.0) | 0.0 (0.0–0.0) | 23.4% | 0.0% | MEDIUM |
| PHI | 00-0040867 | WR | 6.1 (3.0–8.0) | 0.1 (0.0–0.0) | 18.6% | 0.4% | HIGH |
| DAL | 00-0036997 | RB | 3.0 (1.0–4.0) | 16.5 (11.0–21.0) | 8.6% | 65.6% | MEDIUM |
| DAL | 00-0036358 | WR | 8.8 (5.0–12.0) | 0.2 (0.0–0.0) | 25.1% | 0.9% | MEDIUM |
| DAL | 00-0037247 | WR | 6.7 (4.0–9.0) | 0.1 (0.0–0.0) | 19.2% | 0.3% | HIGH |
| DAL | 00-0039410 | WR | 4.6 (2.0–7.0) | 0.1 (0.0–0.0) | 13.2% | 0.4% | HIGH |

**Historical research tags** (7; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 31 market(s), e.g. KXNFL1HFT-26OCT26DALPHI-PHIPHI, KXNFL1Q-26OCT26DALPHI-PHI
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26OCT26DALPHI-PHI8, KXNFLSPREAD-26OCT26DALPHI-PHI7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLGAME-26OCT26DALPHI-DAL, KXNFLSPREAD-26OCT26DALPHI-DAL3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 211 market(s), e.g. KXNFL1H-26OCT26DALPHI-TIE, KXNFL1HFT-26OCT26DALPHI-TIEPHI
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 50 market(s), e.g. KXNFL1HTOTAL-26OCT26DALPHI-8, KXNFL1HTOTAL-26OCT26DALPHI-4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 136 market(s), e.g. KXNFLFFPTS-26OCT26DALPHI-PHIJELLIOTT4-7P2, KXNFLFFPTS-26OCT26DALPHI-DALBAUBREY17-8P9

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 44.4444 (median favourite-oriented margin +2, median total 44))_
2. favourite controls / normal scoring — 18.9%  _(DAL (favourite) wins by more than one score; total within 10 of the centre 44.4444 (median favourite-oriented margin +16, median total 45))_
3. competitive / high scoring — 11.5%  _(final margin within one score (8 points) either way; total 54.4444+ (centre 44.4444) (median favourite-oriented margin +2, median total 62))_
4. competitive / low scoring — 9.8%  _(final margin within one score (8 points) either way; total 34.4444 or fewer (centre 44.4444) (median favourite-oriented margin +3, median total 30))_
5. favourite controls / low scoring — 8.5%  _(DAL (favourite) wins by more than one score; total 34.4444 or fewer (centre 44.4444) (median favourite-oriented margin +15, median total 29))_
   Other — 21.3%

Marginal events (overlapping): one_score 51.3% · blowout_17 19.9% · favorite_wins 66.4% · favorite_controls 35.7% · upset 33.4% · shootout 23.6% · low_scoring 20.4% · low_possession 7.8% · high_volume_passing 16.0% · run_heavy_control 13.2%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 5.50 mph, gusts 15.40, precip prob 0%, temp 62F, forecast retrieved 2026-10-24T16:17:57+00:00 (55.95 h before kickoff)._

**`KXNFLTD-26OCT26DALPHI-PHIDPIERCE39-1`** Dameon Pierce touchdowns 1
- MODEL / MARKET: football 39.2% · market 14.5% · reconciled 21.9%
- SCRIPT ROBUSTNESS: P50 mass 22.4% · P55 mass 22.4% · P60 mass 3.7% · major-script floor 27.5% · failure mass 77.6% · win-contribution HHI 0.179

**`KXNFLTD-26OCT26DALPHI-DALCLAMB88-1`** CeeDee Lamb touchdowns 1
- MODEL / MARKET: football 34.1% · market 43.5% · reconciled 40.8%
- SCRIPT ROBUSTNESS: P50 mass 8.3% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 32.0% · failure mass 91.7% · win-contribution HHI 0.182
- THESIS DEPENDENCY with `KXNFLPASSTDS-26OCT26DALPHI-DALDPRESCOTT4-2`: cash correlation 0.319 · joint cash 24.3% · Jaccard of winning rows 0.412 · shared failure 41.2%

**`KXNFLTD-26OCT26DALPHI-DALJWILLIAMS33-1`** Javonte Williams touchdowns 1
- MODEL / MARKET: football 55.1% · market 59.5% · reconciled 57.1%
- SCRIPT ROBUSTNESS: P50 mass 77.2% · P55 mass 38.8% · P60 mass 38.8% · major-script floor 52.0% · failure mass 22.8% · win-contribution HHI 0.181

**`KXNFLTD-26OCT26DALPHI-DALGPICKENS3-1`** George Pickens touchdowns 1
- MODEL / MARKET: football 25.5% · market 34.0% · reconciled 32.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 23.9% · failure mass 100.0% · win-contribution HHI 0.179

_289 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261024T201739Z.sim-1.1.0.scripts_v2.json.gz); 34 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Jalen Hurts (QB, PHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- DeVonta Smith (WR, PHI) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Dontayvion Wicks (WR, PHI) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Eli Stowers (TE, PHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Grant Calcaterra (TE, PHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Landon Dickerson (G, PHI) — Injured Reserve [high] — ruled out
- Marist Liufau (LB, DAL) — Injured Reserve [high] — ruled out
- P.J. Locke (S, DAL) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (14)** — resolves at the inactive release, T−90m

- KaVontae Turpin (WR, DAL) — Questionable [high]
- Saquon Barkley (RB, PHI) — Questionable [high]
- Broderick Jones (OT, DAL) — Questionable [high]
- Drew Shelton (OT, DAL) — Questionable [single_source]
- Fred Johnson (OT, PHI) — Questionable [high]
- Tyler Steen (G, PHI) — Questionable [high]
- Willie Lampkin (C, PHI) — Questionable [high]
- AJ Epenesa (DE, PHI) — Questionable [single_source]

### WEATHER

- Clear · 58°F · wind 5 mph W · precip 0%
- forecast vintage 2026-10-24T20:15:29+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 60, 'wind': '5 mph', 'precipitation_probability': 0})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261024T201739Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 45 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Dak Prescott | DAL | attempts | 34.6 | 35.0 | 29.0 | 40.0 | 20.0 | 49.0 | 37.1 | 37.0 | 34.6 | 35.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Javonte Williams | DAL | carries | 16.5 | 16.0 | 11.0 | 21.0 | 5.0 | 29.0 | 16.9 | 16.0 | 16.5 | 16.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | completions | 22.5 | 23.0 | 19.0 | 27.0 | 12.0 | 33.0 | 23.7 | 23.0 | 22.5 | 23.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | passing_tds | 1.6 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.8 | 2.0 | 1.8 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Dak Prescott | DAL | passing_yards | 253.5 | 249.0 | 197.0 | 308.0 | 121.0 | 399.0 | 269.2 | 265.0 | 269.1 | 264.0 | 0.00 | 0.97 | 10 | PRICED |
| CeeDee Lamb | DAL | receiving_yards | 72.6 | 64.0 | 34.0 | 101.0 | 3.0 | 170.0 | 85.3 | 79.0 | 85.2 | 75.0 | 0.00 | 0.97 | 14 | PRICED |
| George Pickens | DAL | receiving_yards | 57.9 | 48.0 | 22.0 | 83.0 | 0.0 | 152.0 | 71.5 | 64.0 | 71.4 | 59.0 | 0.00 | 0.98 | 13 | PRICED |
| Ryan Flournoy | DAL | receiving_yards | 35.0 | 26.0 | 9.0 | 51.0 | 0.0 | 102.0 | 38.8 | 32.0 | 38.8 | 29.0 | 0.00 | 0.97 | 11 | PRICED |

_8 of 45 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 45 of 71 listed player/stat groups simulated and exposed, 26 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT26DALPHI-DALCLAMB88-5` | CeeDee Lamb | 5.0 | 0.82 | 0.85 | 0.16 | -0.664 |
| `KXNFLREC-26OCT26DALPHI-DALCLAMB88-4` | CeeDee Lamb | 4.0 | 0.91 | 0.94 | 0.29 | -0.621 |
| `KXNFLREC-26OCT26DALPHI-DALCLAMB88-6` | CeeDee Lamb | 6.0 | 0.70 | 0.72 | 0.08 | -0.617 |
| `KXNFLRSHATT-26OCT26DALPHI-DALJWILLIAMS33-14` | Javonte Williams | 14.0 | 0.72 | 0.74 | 0.17 | -0.547 |
| `KXNFLREC-26OCT26DALPHI-DALCLAMB88-7` | CeeDee Lamb | 7.0 | 0.55 | 0.57 | 0.04 | -0.515 |
| `KXNFLREC-26OCT26DALPHI-DALGPICKENS3-4` | George Pickens | 4.0 | 0.73 | 0.75 | 0.29 | -0.443 |

_Ranked 299 tradable markets; 19 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. DeVonta Smith (WR, PHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Dontayvion Wicks (WR, PHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (KaVontae Turpin (WR), Saquon Barkley (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
5. KXNFLRECYDS-26OCT26DALPHI-PHIDSMITH6-80 moved -0.320 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
6. The model disagrees by -0.664 on KXNFLREC-26OCT26DALPHI-DALCLAMB88-5 (CeeDee Lamb). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. The model disagrees by -0.621 on KXNFLREC-26OCT26DALPHI-DALCLAMB88-4 (CeeDee Lamb). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
8. KXNFLREC-26OCT26DALPHI-DALCLAMB88-4 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_07_DAL_PHI.md`_


---

## HOW TO USE THIS PACKET

1. Handicap each game independently. The model's ranked disagreements are an input, not a shortlist.
2. For any thesis you form, check **BEST EXPRESSIONS** before choosing a contract — the largest disagreement is rarely the best payout for the risk.
3. Check **CORRELATION GROUPS** before sizing more than one position in a game.
4. Record every serious decision, including passes, via the recommendation ledger (`scripts/handicap/validate_recommendations.py`, then commit to the `handicap-data` branch).