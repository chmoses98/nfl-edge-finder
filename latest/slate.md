# NFL HANDICAP PACKET — 2026 Week 4

- run id: `20261003T202715Z`  ·  packet sha: `9b673b64a0fbc61fa304`
- built at: 2026-10-03T20:27:15.482926+00:00  (all timestamps UTC)
- ledger: `20261003T200006Z.shadow-0.4.0.observations.jsonl.gz`  ·  model: `shadow-0.4.0`
- context captures: ['20261003T163355Z', '20261003T200853Z']
- team-profile basis: **current_season**
- **REAL-MONEY STATUS: NOT VALIDATED -- this packet recommends nothing and authorises nothing**
- **SIMULATION FRESHNESS: SIM_CURRENT** — run `20261003T200006Z` (RUN_NFL_FROZEN_BUNDLE), lag 0.0m vs target <= 180.0m; the simulation priced this packet's own board

> This packet contains no recommendations. Every model-vs-market number is a *disagreement*, which is not an edge. The model has been shown redundant to the closing market on player props and behind it on game outcomes; it is here as structure and context, not as a superior forecast.

## SLATE SUMMARY

- games: **16**
- markets listed this slate: **11920**, model-supported: **5848**
- ledger support states (all weeks): `{'UNSUPPORTED_MODEL': 14158, 'UNSUPPORTED_RULES': 3411, 'SUPPORTED': 6150, 'UNSUPPORTED_IDENTITY': 124, 'POST_KICKOFF_EXCLUDED': 35483}`

### FULL-BOARD COVERAGE

_RUN NFL examines every executable Kalshi contract for every requested unstarted NFL game. UNSUPPORTED_MODEL is a statement about one model, never a reason to hide a contract. Every listed contract terminates in exactly one analysis state, in one of four buckets: A validated model view, B coherent/Shadow research view, C manual handicap from the packet's own football and context data, D explicit PASS with a named reason._

| bucket | contracts | meaning |
|---|---|---|
| **A** | 5848 | validated/production model view available |
| **B** | 3101 | coherent / Shadow research model view available |
| **C** | 1976 | no automated pricing authority; handicap from the football and context data in this packet |
| **D** | 187 | cannot defensibly price -- explicit PASS / RESEARCH REQUIRED, with a reason |
| **-** | 808 | outside the pregame window (kickoff has passed) |
| **!** | 0 | INVARIANT VIOLATION -- a listed contract with no analysis state |

- listed: **11920** · executable books: **10653**
- incumbent priced: **5848** · coherent simulation: **0** · Shadow v2 research: **3101**
- manual handicap required: **1976** · research required: **60**
- rules blocked: **3** · identity blocked: **124** · non-football: **0**
- post-kickoff (stale): **808**
- **silently omitted: 0** — this must be 0.

| family / period | listed | executable | incumbent priced | coherent sim | shadow v2 | manual research | research required | rules blocked | identity blocked | non football | post kickoff | silently omitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLAYER_STAT/FULL | 5753 | 5416 | 4683 | 0 | 111 | 428 | 0 | 0 | 124 | 0 | 407 | 0 |
| FIRST_TD_TEAM/FULL | 473 | 316 | 0 | 0 | 0 | 444 | 0 | 0 | 0 | 0 | 29 | 0 |
| TEAM_TOTAL/FULL | 437 | 436 | 409 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 28 | 0 |
| FIRST_TD_SCORER/FULL | 421 | 420 | 0 | 0 | 0 | 391 | 0 | 3 | 0 | 0 | 27 | 0 |
| SPREAD/FULL | 408 | 408 | 381 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 27 | 0 |
| TEAM_TOTAL/1H | 352 | 330 | 0 | 0 | 330 | 0 | 0 | 0 | 0 | 0 | 22 | 0 |
| TEAM_STAT/FULL | 320 | 19 | 0 | 0 | 0 | 300 | 0 | 0 | 0 | 0 | 20 | 0 |
| TOTAL/FULL | 306 | 306 | 285 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| SPREAD/1H | 249 | 249 | 0 | 0 | 231 | 0 | 0 | 0 | 0 | 0 | 18 | 0 |
| SPREAD/2H | 247 | 243 | 0 | 0 | 231 | 0 | 0 | 0 | 0 | 0 | 16 | 0 |
| RACE_TO_N/FULL | 240 | 51 | 0 | 0 | 0 | 225 | 0 | 0 | 0 | 0 | 15 | 0 |
| TOTAL/1H | 219 | 219 | 0 | 0 | 205 | 0 | 0 | 0 | 0 | 0 | 14 | 0 |
| TOTAL/2H | 219 | 216 | 0 | 0 | 205 | 0 | 0 | 0 | 0 | 0 | 14 | 0 |
| GAME_PLAYER_LEADER/FULL | 204 | 49 | 0 | 0 | 0 | 188 | 0 | 0 | 0 | 0 | 16 | 0 |
| SPREAD/4Q | 174 | 170 | 0 | 0 | 163 | 0 | 0 | 0 | 0 | 0 | 11 | 0 |
| SPREAD/2Q | 167 | 163 | 0 | 0 | 153 | 0 | 0 | 0 | 0 | 0 | 14 | 0 |
| SPREAD/3Q | 162 | 159 | 0 | 0 | 151 | 0 | 0 | 0 | 0 | 0 | 11 | 0 |
| SPREAD/1Q | 161 | 161 | 0 | 0 | 151 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/1Q | 160 | 158 | 0 | 0 | 150 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/2Q | 160 | 156 | 0 | 0 | 150 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/3Q | 160 | 157 | 0 | 0 | 150 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/4Q | 160 | 138 | 0 | 0 | 150 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| HALF_FULL_RESULT/1H | 144 | 144 | 0 | 0 | 135 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| WIN_MARGIN_BUCKET/FULL | 112 | 109 | 0 | 0 | 105 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| BOTH_TEAMS_SCORE_N/FULL | 64 | 63 | 60 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| GAME_EVENT/FULL | 64 | 62 | 0 | 0 | 0 | 0 | 60 | 0 | 0 | 0 | 4 | 0 |
| PERIOD_WINNER/1H | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/1Q | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2H | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2Q | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/3Q | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/4Q | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| GAME_WINNER/FULL | 32 | 32 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| BOTH_TEAMS_SCORE/1Q | 16 | 10 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/2Q | 16 | 2 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/3Q | 16 | 2 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/4Q | 16 | 1 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

_A Shadow v2 or coherent-simulation projection is RESEARCH. It is not validated, it is never mixed into the incumbent's probability or its disagreement ranking, and it reaches no recommendation, staking or preflight path._

**Skill players ruled OUT (40)**

- Taylen Green (QB, CLE) — Out · 2026_04_PIT_CLE
- Tylan Wallace (WR, CLE) — Out · 2026_04_PIT_CLE
- Drew Allar (QB, PIT) — Out · 2026_04_PIT_CLE
- Eli Heidenreich (RB, PIT) — Out · 2026_04_PIT_CLE
- Rico Dowdle (RB, PIT) — Out · 2026_04_PIT_CLE
- Will Howard (QB, PIT) — Out · 2026_04_PIT_CLE
- Keenan Allen (WR, IND) — Out · 2026_04_IND_WAS
- Alec Pierce (WR, IND) — Injured Reserve · 2026_04_IND_WAS
- Jayden Daniels (QB, WAS) — Out · 2026_04_IND_WAS
- Rachaad White (RB, WAS) — Out · 2026_04_IND_WAS
- Jaxson Dart (QB, NYG) — Injured Reserve · 2026_04_ARI_NYG
- British Brooks (RB, HOU) — Injured Reserve · 2026_04_DAL_HOU
- Jayden Reed (WR, GB) — Injured Reserve · 2026_04_GB_TB
- Baker Mayfield (QB, TB) — Out · 2026_04_GB_TB
- Ko Kieft (TE, TB) — Out · 2026_04_GB_TB

**New or changed since the previous capture (14)** — the most decision-relevant section on the page

- Craig Reynolds (RB, WAS): **Active** (new record) · 2026_04_IND_WAS
- Edgerrin Cooper (LB, GB): **Active** (was Questionable) · 2026_04_GB_TB
- Warren Brinson (DT, GB): **Injured Reserve** (was Out) · 2026_04_GB_TB
- Anthony Johnson Jr. (S, CHI): **Injured Reserve** (was Out) · 2026_04_NYJ_CHI
- Garrett Dellinger (G, TEN): **Questionable** (new record) · 2026_04_TEN_BAL
- Aidan O'Connell (QB, LV): **Active** (was Questionable) · 2026_04_KC_LV
- Jadarian Price (RB, SEA): **Injured Reserve** (was Out) · 2026_04_LAC_SEA
- Yasir Abdullah (LB, ATL): **Questionable** (new record) · 2026_04_ATL_NO
- Kendal Daniels (LB, ATL): **Active** (was Questionable) · 2026_04_ATL_NO
- Anfernee Jennings (LB, NO): **Out** (was Questionable) · 2026_04_ATL_NO
- Carl Granderson (DE, NO): **Out** (was Questionable) · 2026_04_ATL_NO
- Kaden Elliss (LB, NO): **Out** (was Questionable) · 2026_04_ATL_NO
- Barion Brown (WR, NO): **Active** (was Questionable) · 2026_04_ATL_NO
- Christen Miller (DT, NO): **Active** (was Questionable) · 2026_04_ATL_NO

**Largest market moves since first capture**

| ticker | game | family | move |
|---|---|---|---|
| `KXNFLTD-26OCT01PITCLE-CLEJMCLAUGHLIN38-1` | 2026_04_PIT_CLE | PLAYER_STAT | +0.960 |
| `KXNFLRECYDS-26OCT01PITCLE-PITDMETCALF4-100` | 2026_04_PIT_CLE | PLAYER_STAT | +0.940 |
| `KXNFL1HTEAMTOTAL-26OCT01PITCLE-CLE21` | 2026_04_PIT_CLE | TEAM_TOTAL | +0.940 |
| `KXNFLRECYDS-26OCT01PITCLE-PITDMETCALF4-90` | 2026_04_PIT_CLE | PLAYER_STAT | +0.935 |
| `KXNFLTEAMSACK-26OCT01PITCLE-CLE5` | 2026_04_PIT_CLE | TEAM_STAT | +0.930 |
| `KXNFL1HTEAMTOTAL-26OCT01PITCLE-CLE20` | 2026_04_PIT_CLE | TEAM_TOTAL | +0.930 |
| `KXNFL2QSPREAD-26OCT01PITCLE-CLE11` | 2026_04_PIT_CLE | SPREAD | +0.920 |
| `KXNFLRECYDS-26OCT01PITCLE-PITRWILSON14-60` | 2026_04_PIT_CLE | PLAYER_STAT | +0.915 |
| `KXNFLRECYDS-26OCT01PITCLE-CLEDBOSTON12-80` | 2026_04_PIT_CLE | PLAYER_STAT | +0.915 |
| `KXNFLPASSTDS-26OCT01PITCLE-PITARODGERS8-3` | 2026_04_PIT_CLE | PLAYER_STAT | +0.915 |

**Largest model/market disagreements** — DISAGREEMENT ONLY, REQUIRES HANDICAP

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT04INDWAS-INDKALLEN10-2` | Keenan Allen | 2.0 | 0.88 | 0.89 | 0.01 | -0.870 |
| `KXNFLRSHYDS-26OCT04LACSEA-SEAJPRICE8-20` | Jadarian Price | 20.0 | 0.79 | 0.83 | 0.01 | -0.781 |
| `KXNFLREC-26OCT04INDWAS-INDKALLEN10-3` | Keenan Allen | 3.0 | 0.72 | 0.74 | 0.00 | -0.721 |
| `KXNFLRSHYDS-26OCT04ARINYG-ARIJLOVE4-30` | Jeremiyah Love | 30.0 | 0.89 | 0.89 | 0.17 | -0.718 |
| `KXNFLRSHYDS-26OCT04LACSEA-SEAJPRICE8-25` | Jadarian Price | 25.0 | 0.70 | 0.73 | 0.01 | -0.687 |
| `KXNFLREC-26OCT04INDWAS-INDJDOWNS2-5` | Josh Downs | 5.0 | 0.81 | 0.81 | 0.12 | -0.684 |
| `KXNFLRECYDS-26OCT04LARPHI-PHIDSMITH6-40` | DeVonta Smith | 40.0 | 0.69 | 0.71 | 0.00 | -0.681 |
| `KXNFLRSHATT-26OCT04GBTB-TBJDANIELS10-4` | Jalon Daniels | 4.0 | 0.85 | 0.89 | 0.18 | -0.671 |
| `KXNFLRSHYDS-26OCT04ARINYG-ARIJLOVE4-40` | Jeremiyah Love | 40.0 | 0.78 | 0.80 | 0.11 | -0.670 |
| `KXNFLRECYDS-26OCT04INDWAS-INDKALLEN10-25` | Keenan Allen | 25.0 | 0.67 | 0.69 | 0.00 | -0.660 |
| `KXNFLREC-26OCT04INDWAS-INDJDOWNS2-4` | Josh Downs | 4.0 | 0.88 | 0.88 | 0.22 | -0.651 |
| `KXNFLRSHATT-26OCT04ARINYG-ARIJLOVE4-13` | Jeremiyah Love | 13.0 | 0.74 | 0.76 | 0.11 | -0.633 |

**Highest-liquidity markets**

- `KXNFLGAME-26OCT01PITCLE-PIT` (GAME_WINNER, 2026_04_PIT_CLE): volume 32856421, OI 14868125
- `KXNFLGAME-26OCT01PITCLE-CLE` (GAME_WINNER, 2026_04_PIT_CLE): volume 25497766, OI 11546450
- `KXNFLSPREAD-26OCT01PITCLE-PIT3` (SPREAD, 2026_04_PIT_CLE): volume 2969740, OI 1816060
- `KXNFLGAME-26OCT04KCLV-LV` (GAME_WINNER, 2026_04_KC_LV): volume 1626518, OI 1412841
- `KXNFLSPREAD-26OCT01PITCLE-CLE8` (SPREAD, 2026_04_PIT_CLE): volume 1443319, OI 548564
- `KXNFLTOTAL-26OCT01PITCLE-38` (TOTAL, 2026_04_PIT_CLE): volume 1199842, OI 758456
- `KXNFLTOTAL-26OCT01PITCLE-39` (TOTAL, 2026_04_PIT_CLE): volume 1192473, OI 753558
- `KXNFLSPREAD-26OCT01PITCLE-PIT4` (SPREAD, 2026_04_PIT_CLE): volume 1072556, OI 712501

**BLOCKING data issues**

- 2026_04_PIT_CLE: `GAME_STARTED` — kickoff has passed; this is not a pregame packet

### GAME PRIORITY FOR HANDICAP

_Priority ranks where deeper review may be most useful. It is NOT a bet ranking and carries no expectation that these games contain value._

| # | game | score | why |
|---|---|---|---|
| 1 | 2026_04_ATL_NO | 17.33 | 7 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.155; largest reconciled simulation disagreement 0.083; raw incumbent disagreement 0.532 (NOT scored: unvalidated); 310 supported player-prop rungs |
| 2 | 2026_04_GB_TB | 16.5 | 2 new/changed injury records; 4 skill players ruled out (role change); forecast changed; largest market move 0.215; raw incumbent disagreement 0.671 (NOT scored: unvalidated); 324 supported player-prop rungs |
| 3 | 2026_04_IND_WAS | 14.94 | 1 new/changed injury records; 4 skill players ruled out (role change); largest market move 0.655; largest reconciled simulation disagreement 0.144; raw incumbent disagreement 0.870 (NOT scored: unvalidated); 304 supported player-prop rungs |
| 4 | 2026_04_LAC_SEA | 14.5 | 1 new/changed injury records; 4 skill players ruled out (role change); forecast changed; largest market move 0.190; raw incumbent disagreement 0.781 (NOT scored: unvalidated); 303 supported player-prop rungs |
| 5 | 2026_04_NYJ_CHI | 13.5 | 1 new/changed injury records; 5 skill players ruled out (role change); largest market move 0.160; raw incumbent disagreement 0.631 (NOT scored: unvalidated); 281 supported player-prop rungs |
| 6 | 2026_04_LA_PHI | 13.08 | 5 skill players ruled out (role change); largest market move 0.245; largest reconciled simulation disagreement 0.158; raw incumbent disagreement 0.681 (NOT scored: unvalidated); 275 supported player-prop rungs |
| 7 | 2026_04_MIA_MIN | 13.05 | 4 skill players ruled out (role change); largest market move 0.230; largest reconciled simulation disagreement 0.155; raw incumbent disagreement 0.555 (NOT scored: unvalidated); 299 supported player-prop rungs |
| 8 | 2026_04_DEN_SF | 10.98 | 2 skill players ruled out (role change); forecast changed; largest market move 0.155; largest reconciled simulation disagreement 0.148; raw incumbent disagreement 0.505 (NOT scored: unvalidated); 300 supported player-prop rungs |
| 9 | 2026_04_KC_LV | 10.5 | 1 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.195; raw incumbent disagreement 0.617 (NOT scored: unvalidated); 330 supported player-prop rungs |
| 10 | 2026_04_PIT_CLE | 10.0 | 6 skill players ruled out (role change); largest market move 0.960; BLOCKING data issue -- review before trusting anything here |
| 11 | 2026_04_DET_CAR | 9.4 | 1 skill players ruled out (role change); forecast changed; largest market move 0.200; largest reconciled simulation disagreement 0.140; raw incumbent disagreement 0.601 (NOT scored: unvalidated); 299 supported player-prop rungs |
| 12 | 2026_04_TEN_BAL | 8.5 | 1 new/changed injury records; forecast changed; largest market move 0.215; raw incumbent disagreement 0.610 (NOT scored: unvalidated); 306 supported player-prop rungs |
| 13 | 2026_04_DAL_HOU | 8.13 | 1 skill players ruled out (role change); largest market move 0.205; largest reconciled simulation disagreement 0.113; raw incumbent disagreement 0.494 (NOT scored: unvalidated); 340 supported player-prop rungs |
| 14 | 2026_04_JAX_CIN | 8.07 | 1 skill players ruled out (role change); largest market move 0.140; largest reconciled simulation disagreement 0.107; raw incumbent disagreement 0.590 (NOT scored: unvalidated); 347 supported player-prop rungs |
| 15 | 2026_04_ARI_NYG | 8.0 | 1 skill players ruled out (role change); forecast changed; largest market move 0.210; raw incumbent disagreement 0.718 (NOT scored: unvalidated); 312 supported player-prop rungs |
| 16 | 2026_04_NE_BUF | 8.0 | 1 skill players ruled out (role change); forecast changed; largest market move 0.225; raw incumbent disagreement 0.562 (NOT scored: unvalidated); 353 supported player-prop rungs |

> Each game below is summarised. Full detail -- complete market board, every player ladder, all best-expression groups -- is in that game's own file under `games/`.


---

## PIT @ CLE — `2026_04_PIT_CLE`

- kickoff: 2026-10-02T00:15:00+00:00 (-2652 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 808 listed across 16 families — 0 supported, 22 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 808/808 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.98 | -- |
| total | 52.46 | -- |
| score | CLE 27.7 – PIT 24.7 | CLE -- – PIT -- |
| win prob CLE | 98.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -12.00 / total 30.50 · **2H** spread 8.96 / total 20.08 · **1Q** spread 7.00 / total 7.50 · **2Q** spread -19.50 / total 23.50 · **3Q** spread -0.50 / total -- · **4Q** spread 9.05 / total 19.69

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -2.98 · total 52.46
- move `KXNFL1HTEAMTOTAL-26OCT01PITCLE-CLE21` +0.940
- move `KXNFL1HTEAMTOTAL-26OCT01PITCLE-CLE20` +0.930
- move `KXNFL2QSPREAD-26OCT01PITCLE-CLE11` +0.920
- move `KXNFL1HTEAMTOTAL-26OCT01PITCLE-CLE17` +0.900

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261003T200006Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (7; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 1 market(s), e.g. KXNFLMOSTRSHYDS-26OCT01PITCLE-CLEDWATSON4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 2 market(s), e.g. KXNFLBOTH-26OCT01PITCLE-28, KXNFLTEAMTOTAL-26OCT01PITCLE-PIT32
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 1 market(s), e.g. KXNFLBOTH-26OCT01PITCLE-14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 34 market(s), e.g. KXNFLMOSTRECYDS-26OCT01PITCLE-PITRWILSON14, KXNFL2HSPREAD-26OCT01PITCLE-PIT15
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 23 market(s), e.g. KXNFLRECYDS-26OCT01PITCLE-CLERSANDERS23-10, KXNFL1HFT-26OCT01PITCLE-CLECLE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 5 market(s), e.g. KXNFLFFPTS-26OCT01PITCLE-PITPITDST-8P7, KXNFLFFPTS-26OCT01PITCLE-CLEHFANNIN44-11P8

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (11)**

- Drew Allar (QB, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Taylen Green (QB, CLE) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Will Howard (QB, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Eli Heidenreich (RB, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Rico Dowdle (RB, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tylan Wallace (WR, CLE) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Elgton Jenkins (C, CLE) — Out [high] — ruled out
- Teven Jenkins (G, CLE) — Out [high] — ruled out
- _...and 3 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Derrick Harmon (DT, PIT) — Questionable [high]
- Jamel Dean (CB, PIT) — Questionable [high]
- Mason Graham (DT, CLE) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 103 listed player/stat groups simulated and exposed, 103 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Taylen Green (QB, CLE) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Tylan Wallace (WR, CLE) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLTD-26OCT01PITCLE-CLEJMCLAUGHLIN38-1 moved +0.960 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_PIT_CLE.md`_


---

## IND @ WAS — `2026_04_IND_WAS`

- kickoff: 2026-10-04T13:30:00+00:00 (1023 minutes away) · state **PREGAME**
- venue: Tottenham Hotspur Stadium · roof outdoors · surface grass
- markets: 740 listed across 16 families — 380 supported, 302 no model, 48 rules unresolved, 10 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 10 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 4.33 | 4.52 |
| total | 47.62 | 47.18 |
| score | WAS 21.6 – IND 26.0 | WAS 21.3 – IND 25.8 |
| win prob WAS | 34.5% | 34.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.69 / total 23.62 · **2H** spread 2.23 / total 23.60 · **1Q** spread 1.56 / total 8.38 · **2Q** spread 1.84 / total 14.31 · **3Q** spread 1.10 / total 8.83 · **4Q** spread 0.66 / total 13.59

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 4.33 · total 47.62

**Game environment** (simulation, mean and middle 50%) — home margin -4.5 (-12.0–3.0) · total 48.6 (40.0–57.0) · P(one score) 51.4% · P(17+ blowout) 19.6% · P(total 10+ over centre) 23.5%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| WAS | 63.8 (58.0–69.0) | 34.0 (29.0–39.0) | 24.9 (20.0–30.0) | 38.4 (33.0–43.0) | 0.602 (0.536–0.669) | 0.499 / 0.668 |
| IND | 62.7 (57.0–68.0) | 31.8 (27.0–36.0) | 26.5 (21.0–31.0) | 35.3 (30.0–40.0) | 0.563 (0.496–0.631) | 0.484 / 0.660 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| WAS | 00-0040242 | RB | 1.0 (0.0–1.0) | 12.4 (7.0–17.0) | 3.3% | 49.8% | MEDIUM |
| WAS | 00-0033699 | RB | 2.6 (1.0–4.0) | 7.6 (3.0–11.0) | 8.1% | 30.7% | HIGH |
| WAS | 00-0031588 | WR | 5.5 (3.0–8.0) | 0.1 (0.0–0.0) | 17.3% | 0.3% | HIGH |
| WAS | 00-0035659 | WR | 5.0 (1.0–8.0) | 0.0 (0.0–0.0) | 15.6% | 0.1% | HIGH |
| IND | 00-0036223 | RB | 3.8 (1.0–6.0) | 17.6 (12.0–23.0) | 12.6% | 66.5% | MEDIUM |
| IND | 00-0040128 | TE | 7.8 (5.0–10.0) | 0.4 (0.0–0.0) | 25.5% | 1.7% | MEDIUM |
| IND | 00-0038997 | WR | 8.0 (5.0–11.0) | 0.1 (0.0–0.0) | 26.2% | 0.6% | MEDIUM |
| IND | 00-0035535 | WR | 5.2 (2.0–7.0) | 0.0 (0.0–0.0) | 17.0% | 0.0% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 7 market(s), e.g. KXNFLPASSATT-26OCT04INDWAS-INDDJONES17-37, KXNFLPASSYDS-26OCT04INDWAS-INDDJONES17-300
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 89 market(s), e.g. KXNFL2QSPREAD-26OCT04INDWAS-IND8, KXNFLFIRSTTD-26OCT04INDWAS-INDJTAYLOR28
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26OCT04INDWAS-WAS8, KXNFLSPREAD-26OCT04INDWAS-WAS7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLGAME-26OCT04INDWAS-IND, KXNFLSPREAD-26OCT04INDWAS-IND3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 195 market(s), e.g. KXNFL1HFT-26OCT04INDWAS-WASIND, KXNFL1HFT-26OCT04INDWAS-TIEIND
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 44 market(s), e.g. KXNFLRECYDS-26OCT04INDWAS-WASSDIGGS3-15, KXNFLTEAMTOTAL-26OCT04INDWAS-IND15

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Jayden Daniels (QB, WAS) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Alec Pierce (WR, IND) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Keenan Allen (WR, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Rachaad White (RB, WAS) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Sam Cosmi (G, WAS) — Out [high] — ruled out
- Leo Chenal (LB, WAS) — Injured Reserve [high] — ruled out
- Micheal Clemons (DE, IND) — Injured Reserve [high] — ruled out
- Nick Cross (S, WAS) — Out [high] — ruled out

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Mo Alie-Cox (TE, IND) — Questionable [high]
- Terry McLaurin (WR, WAS) — Doubtful [high]
- Percy Butler (S, WAS) — Questionable [high]

### WEATHER

- None · None°F · wind None  · precip None%
- forecast vintage None · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 58 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Daniel Jones | IND | attempts | 30.5 | 31.0 | 25.0 | 36.0 | 17.0 | 44.0 | 31.4 | 31.0 | 30.5 | 31.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jonathan Taylor | IND | carries | 17.6 | 17.0 | 12.0 | 23.0 | 6.0 | 31.0 | 20.7 | 20.0 | 17.6 | 17.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Daniel Jones | IND | carries | 3.7 | 3.0 | 2.0 | 5.0 | 0.0 | 9.0 | 3.4 | 3.0 | 3.7 | 3.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Daniel Jones | IND | completions | 20.2 | 20.0 | 17.0 | 24.0 | 11.0 | 30.0 | 20.6 | 20.0 | 20.2 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Daniel Jones | IND | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Daniel Jones | IND | passing_yards | 218.5 | 214.0 | 166.0 | 266.0 | 101.0 | 351.0 | 227.4 | 221.0 | 227.4 | 222.0 | 0.00 | 0.97 | 9 | PRICED |
| Josh Downs | IND | receiving_yards | 64.3 | 56.0 | 29.0 | 90.0 | 1.0 | 152.0 | 76.6 | 70.0 | 76.5 | 67.0 | 0.00 | 0.97 | 11 | PRICED |
| Tyler Warren | IND | receiving_yards | 54.0 | 47.0 | 25.0 | 75.0 | 1.0 | 128.0 | 59.9 | 54.0 | 59.9 | 52.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 58 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 58 of 98 listed player/stat groups simulated and exposed, 40 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT04INDWAS-INDKALLEN10-2` | Keenan Allen | 2.0 | 0.88 | 0.89 | 0.01 | -0.870 |
| `KXNFLREC-26OCT04INDWAS-INDKALLEN10-3` | Keenan Allen | 3.0 | 0.72 | 0.74 | 0.00 | -0.721 |
| `KXNFLREC-26OCT04INDWAS-INDJDOWNS2-5` | Josh Downs | 5.0 | 0.81 | 0.81 | 0.12 | -0.684 |
| `KXNFLRECYDS-26OCT04INDWAS-INDKALLEN10-25` | Keenan Allen | 25.0 | 0.67 | 0.69 | 0.00 | -0.660 |
| `KXNFLREC-26OCT04INDWAS-INDJDOWNS2-4` | Josh Downs | 4.0 | 0.88 | 0.88 | 0.22 | -0.651 |
| `KXNFLREC-26OCT04INDWAS-INDJDOWNS2-6` | Josh Downs | 6.0 | 0.68 | 0.68 | 0.06 | -0.613 |

_Ranked 362 tradable markets; 18 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Keenan Allen (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Alec Pierce (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Mo Alie-Cox (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLFFPTS-26OCT04INDWAS-INDKALLEN10-8P6 moved -0.655 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.870 on KXNFLREC-26OCT04INDWAS-INDKALLEN10-2 (Keenan Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.721 on KXNFLREC-26OCT04INDWAS-INDKALLEN10-3 (Keenan Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT04INDWAS-INDTWARREN84-3 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_IND_WAS.md`_


---

## ARI @ NYG — `2026_04_ARI_NYG`

- kickoff: 2026-10-04T17:00:00+00:00 (1233 minutes away) · state **PREGAME**
- venue: MetLife Stadium · roof outdoors · surface fieldturf
- markets: 738 listed across 16 families — 390 supported, 292 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.57 | 2.09 |
| total | 44.62 | 45.06 |
| score | NYG 21.0 – ARI 23.6 | NYG 21.5 – ARI 23.6 |
| win prob NYG | 42.5% | 41.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 1.37 / total 22.10 · **2H** spread 0.88 / total 22.22 · **1Q** spread 0.58 / total 7.90 · **2Q** spread 0.75 / total 13.33 · **3Q** spread 0.52 / total 8.32 · **4Q** spread -0.01 / total 12.86

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.57 · total 44.62
- move `KXNFLGAME-26OCT04ARINYG-NYG` -0.210
- move `KXNFLSPREAD-26OCT04ARINYG-ARI3` +0.155
- move `KXNFLSPREAD-26OCT04ARINYG-ARI2` +0.155
- move `KXNFL1HTEAMTOTAL-26OCT04ARINYG-ARI17` +0.145

**Game environment** (simulation, mean and middle 50%) — home margin -2.4 (-10.0–5.0) · total 45.8 (37.0–54.0) · P(one score) 53.9% · P(17+ blowout) 17.8% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NYG | 62.8 (57.0–69.0) | 32.6 (28.0–37.0) | 26.5 (21.0–31.0) | 35.7 (30.0–41.0) | 0.569 (0.504–0.637) | 0.470 / 0.638 |
| ARI | 63.1 (57.0–69.0) | 35.3 (30.0–40.0) | 23.8 (19.0–28.0) | 38.4 (33.0–44.0) | 0.610 (0.542–0.677) | 0.527 / 0.699 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NYG | 00-0040715 | RB | 3.6 (1.0–5.0) | 12.1 (7.0–16.2) | 11.5% | 45.8% | MEDIUM |
| NYG | 00-0039337 | WR | 7.6 (4.0–10.0) | 0.0 (0.0–0.0) | 24.3% | 0.1% | MEDIUM |
| NYG | 00-0036893 | RB | 1.0 (0.0–1.0) | 5.9 (2.0–9.0) | 3.0% | 22.5% | HIGH |
| NYG | 00-0035250 | RB | 1.6 (0.0–2.0) | 3.9 (1.0–6.0) | 4.9% | 14.6% | HIGH |
| ARI | 00-0041027 | RB | 3.3 (1.0–5.0) | 12.9 (8.0–17.0) | 9.8% | 54.4% | MEDIUM |
| ARI | 00-0037744 | TE | 8.5 (5.0–11.0) | 0.0 (0.0–0.0) | 25.1% | 0.0% | MEDIUM |
| ARI | 00-0038559 | WR | 7.6 (4.0–10.0) | 0.0 (0.0–0.0) | 22.5% | 0.2% | HIGH |
| ARI | 00-0037263 | RB | 2.1 (0.0–3.0) | 4.9 (1.0–7.0) | 6.1% | 20.4% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 16 market(s), e.g. KXNFLPASSATT-26OCT04ARINYG-NYGJWINSTON19-36, KXNFLPASSCOMP-26OCT04ARINYG-NYGJWINSTON19-24
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 60 market(s), e.g. KXNFL1HTEAMTOTAL-26OCT04ARINYG-ARI17, KXNFL1Q-26OCT04ARINYG-ARI
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 20 market(s), e.g. KXNFLSPREAD-26OCT04ARINYG-NYG8, KXNFLSPREAD-26OCT04ARINYG-NYG7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTOTAL-26OCT04ARINYG-41, KXNFLTEAMTOTAL-26OCT04ARINYG-NYG18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 196 market(s), e.g. KXNFL1HFT-26OCT04ARINYG-ARINYG, KXNFL1HTEAMTOTAL-26OCT04ARINYG-ARI21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 58 market(s), e.g. KXNFL1HTOTAL-26OCT04ARINYG-11, KXNFLTEAMTOTAL-26OCT04ARINYG-ARI8

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Jaxson Dart (QB, NYG) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Brian Burns (LB, NYG) — Injured Reserve [high] — ruled out
- Dadrion Taylor-Demerson (S, ARI) — Out [high] — ruled out
- Will Johnson (CB, ARI) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Josh Sweat (LB, ARI) — Questionable [high]

### WEATHER

- Slight Chance Rain Showers · 65°F · wind 8 mph E · precip 15%
- forecast vintage 2026-10-03T20:09:19+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 64, 'wind': '8 mph', 'precipitation_probability': 13})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 59 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jacoby Brissett | ARI | attempts | 33.8 | 34.0 | 29.0 | 39.0 | 20.0 | 47.0 | 34.5 | 34.0 | 33.8 | 34.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jeremiyah Love | ARI | carries | 12.9 | 12.0 | 8.0 | 17.0 | 3.0 | 25.0 | 16.3 | 16.0 | 12.9 | 12.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | ARI | completions | 22.4 | 22.0 | 18.0 | 26.0 | 12.0 | 32.0 | 22.9 | 23.0 | 22.4 | 22.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | ARI | passing_tds | 1.6 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.5 | 1.0 | 1.5 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Jacoby Brissett | ARI | passing_yards | 228.3 | 224.0 | 176.0 | 276.0 | 111.0 | 363.0 | 235.3 | 230.0 | 235.3 | 231.0 | 0.00 | 0.97 | 9 | PRICED |
| Trey McBride | ARI | receiving_yards | 60.6 | 54.0 | 29.0 | 84.0 | 4.0 | 140.0 | 67.4 | 62.0 | 67.4 | 60.0 | 0.00 | 0.98 | 11 | PRICED |
| Michael Wilson | ARI | receiving_yards | 58.6 | 50.0 | 25.0 | 83.0 | 0.0 | 143.0 | 62.6 | 56.0 | 62.6 | 53.0 | 0.00 | 0.98 | 11 | PRICED |
| Marvin Harrison Jr. | ARI | receiving_yards | 31.9 | 22.0 | 5.0 | 48.0 | 0.0 | 101.0 | 40.0 | 32.0 | 40.0 | 27.0 | 0.00 | 0.97 | 8 | PRICED |

_8 of 59 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 59 of 95 listed player/stat groups simulated and exposed, 36 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26OCT04ARINYG-ARIJLOVE4-30` | Jeremiyah Love | 30.0 | 0.89 | 0.89 | 0.17 | -0.718 |
| `KXNFLRSHYDS-26OCT04ARINYG-ARIJLOVE4-40` | Jeremiyah Love | 40.0 | 0.78 | 0.80 | 0.11 | -0.670 |
| `KXNFLRSHATT-26OCT04ARINYG-ARIJLOVE4-13` | Jeremiyah Love | 13.0 | 0.74 | 0.76 | 0.11 | -0.633 |
| `KXNFLREC-26OCT04ARINYG-ARIJLOVE4-2` | Jeremiyah Love | 2.0 | 0.79 | 0.80 | 0.16 | -0.624 |
| `KXNFLRSHYDS-26OCT04ARINYG-ARIJLOVE4-50` | Jeremiyah Love | 50.0 | 0.68 | 0.68 | 0.07 | -0.602 |
| `KXNFLREC-26OCT04ARINYG-NYGILIKELY9-3` | Isaiah Likely | 3.0 | 0.76 | 0.76 | 0.20 | -0.553 |

_Ranked 389 tradable markets; 1 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jaxson Dart (QB, NYG) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
3. KXNFLGAME-26OCT04ARINYG-NYG moved -0.210 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.718 on KXNFLRSHYDS-26OCT04ARINYG-ARIJLOVE4-30 (Jeremiyah Love). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.670 on KXNFLRSHYDS-26OCT04ARINYG-ARIJLOVE4-40 (Jeremiyah Love). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLRSHYDS-26OCT04ARINYG-ARIJLOVE4-30 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_ARI_NYG.md`_


---

## DAL @ HOU — `2026_04_DAL_HOU`

- kickoff: 2026-10-04T17:00:00+00:00 (1233 minutes away) · state **PREGAME**
- venue: Reliant Stadium · roof  · surface astroturf
- markets: 774 listed across 16 families — 417 supported, 301 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.89 | -2.88 |
| total | 48.90 | 49.27 |
| score | HOU 25.9 – DAL 23.0 | HOU 26.1 – DAL 23.2 |
| win prob HOU | 58.5% | 60.6% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -2.03 / total 24.28 · **2H** spread -1.25 / total 24.30 · **1Q** spread -0.90 / total 8.60 · **2Q** spread -1.39 / total 14.64 · **3Q** spread -0.77 / total 9.31 · **4Q** spread -0.23 / total 13.87

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -2.89 · total 48.90
- move `KXNFLTOTAL-26OCT04DALHOU-33` +0.205
- move `KXNFLGAME-26OCT04DALHOU-HOU` +0.140
- move `KXNFLTOTAL-26OCT04DALHOU-27` +0.120
- move `KXNFL1HTOTAL-26OCT04DALHOU-4` +0.110

**Game environment** (simulation, mean and middle 50%) — home margin 2.6 (-5.0–10.0) · total 49.7 (41.0–57.0) · P(one score) 53.3% · P(17+ blowout) 17.6% · P(total 10+ over centre) 23.4%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| HOU | 65.2 (60.0–71.0) | 34.6 (29.0–40.0) | 26.1 (21.0–31.0) | 38.2 (33.0–43.0) | 0.587 (0.520–0.655) | 0.500 / 0.676 |
| DAL | 63.7 (58.0–69.0) | 35.1 (30.0–40.0) | 23.2 (18.0–28.0) | 39.8 (34.0–45.0) | 0.627 (0.562–0.692) | 0.523 / 0.699 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| HOU | 00-0035685 | RB | 2.0 (0.0–3.0) | 12.7 (7.0–17.0) | 6.2% | 48.5% | MEDIUM |
| HOU | 00-0040583 | RB | 1.8 (0.0–3.0) | 9.2 (4.0–13.0) | 5.6% | 35.4% | HIGH |
| HOU | 00-0036554 | WR | 6.7 (4.0–9.0) | 0.4 (0.0–0.0) | 20.6% | 1.5% | HIGH |
| HOU | 00-0038618 | WR | 4.4 (2.0–6.0) | 1.1 (0.0–1.0) | 13.4% | 4.3% | HIGH |
| DAL | 00-0036997 | RB | 3.2 (1.0–5.0) | 14.1 (9.0–19.0) | 9.4% | 60.7% | MEDIUM |
| DAL | 00-0036358 | WR | 7.8 (4.0–10.0) | 0.2 (0.0–0.0) | 22.8% | 0.8% | MEDIUM |
| DAL | 00-0037247 | WR | 6.9 (4.0–10.0) | 0.0 (0.0–0.0) | 20.4% | 0.2% | HIGH |
| DAL | 00-0039410 | WR | 4.6 (2.0–7.0) | 0.1 (0.0–0.0) | 13.6% | 0.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 2 market(s), e.g. KXNFLTD-26OCT04DALHOU-HOUCSTROUD7-1, KXNFLPASSCOMP-26OCT04DALHOU-HOUCSTROUD7-27
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 61 market(s), e.g. KXNFL2HSPREAD-26OCT04DALHOU-HOU8, KXNFLPASSYDS-26OCT04DALHOU-HOUCSTROUD7-300
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 24 market(s), e.g. KXNFLSPREAD-26OCT04DALHOU-HOU18, KXNFLSPREAD-26OCT04DALHOU-HOU11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTEAMTOTAL-26OCT04DALHOU-HOU22, KXNFLTOTAL-26OCT04DALHOU-45
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 202 market(s), e.g. KXNFL1HFT-26OCT04DALHOU-TIEHOU, KXNFL1HFT-26OCT04DALHOU-HOUDAL
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 36 market(s), e.g. KXNFLREC-26OCT04DALHOU-HOUNCOLLINS12-3, KXNFLREC-26OCT04DALHOU-HOUNCOLLINS12-2

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (10)**

- British Brooks (RB, HOU) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Tyler Smith (G, DAL) — Injured Reserve [high] — ruled out
- Azeez Al-Shaair (LB, HOU) — Out [high] — ruled out
- Cobie Durant (CB, DAL) — Out [high] — ruled out
- DeMarvion Overshown (LB, DAL) — Out [high] — ruled out
- Jalen Thompson (S, DAL) — Injured Reserve [high] — ruled out
- Jonathan Bullard (DT, DAL) — Injured Reserve [high] — ruled out
- M.J. Stewart (S, HOU) — Out [high] — ruled out
- _...and 2 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Ed Ingram (G, HOU) — Questionable [high]
- Trent Brown (OT, HOU) — Questionable [high]
- Jadeveon Clowney (DE, HOU) — Questionable [high]
- Jake Hansen (LB, HOU) — Questionable [high]
- Logan Hall (DE, HOU) — Questionable [high]

### WEATHER

- Chance Showers And Thunderstorms · 80°F · wind 10 mph N · precip 33%
- forecast vintage 2026-10-03T20:09:17+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 68 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Dak Prescott | DAL | attempts | 33.7 | 34.0 | 29.0 | 39.0 | 20.0 | 47.0 | 35.8 | 35.0 | 33.7 | 34.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Javonte Williams | DAL | carries | 14.1 | 14.0 | 9.0 | 19.0 | 3.0 | 26.0 | 15.8 | 15.0 | 14.1 | 14.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | carries | 3.3 | 3.0 | 2.0 | 4.0 | 0.0 | 7.0 | 3.2 | 3.0 | 3.3 | 3.0 | -- | 0.98 | 2 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | completions | 21.6 | 22.0 | 18.0 | 25.0 | 12.0 | 31.0 | 24.5 | 24.0 | 21.6 | 22.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.7 | 2.0 | 1.7 | 2.0 | 0.00 | 0.98 | 4 | PRICED |
| Dak Prescott | DAL | passing_yards | 238.6 | 234.0 | 183.0 | 289.0 | 114.0 | 379.0 | 267.8 | 263.0 | 267.7 | 263.0 | 0.00 | 0.98 | 9 | PRICED |
| CeeDee Lamb | DAL | receiving_yards | 65.4 | 56.0 | 28.0 | 92.0 | 0.0 | 161.0 | 81.8 | 74.0 | 81.6 | 71.0 | 0.00 | 0.97 | 13 | PRICED |
| George Pickens | DAL | receiving_yards | 55.9 | 47.0 | 22.0 | 80.0 | 0.0 | 142.0 | 73.7 | 66.0 | 73.6 | 62.0 | 0.00 | 0.98 | 12 | PRICED |

_8 of 68 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 68 of 108 listed player/stat groups simulated and exposed, 40 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT04DALHOU-HOUDMONTGOMERY32-9` | David Montgomery | 9.0 | 0.79 | 0.80 | 0.30 | -0.494 |
| `KXNFLREC-26OCT04DALHOU-DALCLAMB88-5` | CeeDee Lamb | 5.0 | 0.70 | 0.71 | 0.22 | -0.479 |
| `KXNFLRSHATT-26OCT04DALHOU-DALJWILLIAMS33-13` | Javonte Williams | 13.0 | 0.73 | 0.75 | 0.26 | -0.468 |
| `KXNFLREC-26OCT04DALHOU-DALCLAMB88-4` | CeeDee Lamb | 4.0 | 0.82 | 0.84 | 0.38 | -0.450 |
| `KXNFLREC-26OCT04DALHOU-DALJWILLIAMS33-2` | Javonte Williams | 2.0 | 0.74 | 0.75 | 0.31 | -0.437 |
| `KXNFLREC-26OCT04DALHOU-DALCLAMB88-6` | CeeDee Lamb | 6.0 | 0.55 | 0.55 | 0.12 | -0.427 |

_Ranked 415 tradable markets; 2 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. British Brooks (RB, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. KXNFLTOTAL-26OCT04DALHOU-33 moved +0.205 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
3. The model disagrees by -0.494 on KXNFLRSHATT-26OCT04DALHOU-HOUDMONTGOMERY32-9 (David Montgomery). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
4. The model disagrees by -0.479 on KXNFLREC-26OCT04DALHOU-DALCLAMB88-5 (CeeDee Lamb). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. KXNFLREC-26OCT04DALHOU-DALCLAMB88-3 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_DAL_HOU.md`_


---

## GB @ TB — `2026_04_GB_TB`

- kickoff: 2026-10-04T17:00:00+00:00 (1233 minutes away) · state **PREGAME**
- venue: Raymond James Stadium · roof outdoors · surface grass
- markets: 753 listed across 16 families — 400 supported, 297 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.11 | 2.76 |
| total | 39.29 | 39.30 |
| score | TB 18.1 – GB 21.2 | TB 18.3 – GB 21.0 |
| win prob TB | 39.5% | 39.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.34 / total 20.19 · **2H** spread 1.52 / total 19.80 · **1Q** spread 0.67 / total 7.62 · **2Q** spread 0.64 / total 11.12 · **3Q** spread 0.93 / total 7.71 · **4Q** spread 0.34 / total 10.47

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 3.11 · total 39.29
- move `KXNFLTOTAL-26OCT04GBTB-47` -0.215
- move `KXNFLSPREAD-26OCT04GBTB-GB3` +0.185
- move `KXNFLSPREAD-26OCT04GBTB-GB2` +0.175
- move `KXNFLTOTAL-26OCT04GBTB-46` -0.145

**Game environment** (simulation, mean and middle 50%) — home margin -3.7 (-11.0–4.0) · total 40.4 (31.0–49.0) · P(one score) 53.8% · P(17+ blowout) 19.2% · P(total 10+ over centre) 22.9%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| TB | 62.0 (56.0–68.0) | 32.8 (28.0–37.0) | 23.5 (19.0–28.0) | 37.9 (33.0–43.0) | 0.612 (0.546–0.679) | 0.505 / 0.675 |
| GB | 60.9 (55.0–67.0) | 32.5 (27.0–37.0) | 24.7 (20.0–29.0) | 35.3 (30.0–40.0) | 0.580 (0.513–0.648) | 0.500 / 0.676 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| TB | 00-0039361 | RB | 3.8 (1.0–5.0) | 15.7 (11.0–20.0) | 12.1% | 66.7% | MEDIUM |
| TB | 00-0036919 | RB | 4.0 (2.0–6.0) | 4.7 (1.0–7.0) | 12.8% | 20.2% | HIGH |
| TB | 00-0040129 | WR | 6.9 (4.0–9.0) | 0.2 (0.0–0.0) | 21.9% | 0.9% | HIGH |
| TB | 00-0038129 | TE | 5.4 (3.0–8.0) | 0.0 (0.0–0.0) | 17.0% | 0.0% | HIGH |
| GB | 00-0039811 | RB | 1.9 (0.0–3.0) | 10.3 (6.0–14.0) | 6.0% | 41.6% | MEDIUM |
| GB | 00-0040142 | RB | 1.1 (0.0–2.0) | 9.6 (5.0–13.0) | 3.4% | 39.0% | HIGH |
| GB | 00-0038124 | WR | 7.5 (4.0–10.0) | 0.1 (0.0–0.0) | 24.3% | 0.4% | MEDIUM |
| GB | 00-0040667 | WR | 6.1 (3.0–8.0) | 0.2 (0.0–0.0) | 19.8% | 0.8% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 26 market(s), e.g. KXNFLPASSATT-26OCT04GBTB-TBJDANIELS10-33, KXNFLPASSATT-26OCT04GBTB-TBJDANIELS10-23
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 28 market(s), e.g. KXNFLPASSYDS-26OCT04GBTB-TBJDANIELS10-225, KXNFLPASSYDS-26OCT04GBTB-TBJDANIELS10-200
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 25 market(s), e.g. KXNFLSPREAD-26OCT04GBTB-TB8, KXNFLSPREAD-26OCT04GBTB-TB7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLGAME-26OCT04GBTB-GB, KXNFLTEAMTOTAL-26OCT04GBTB-GB18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 213 market(s), e.g. KXNFL1H-26OCT04GBTB-TIE, KXNFL1HSPREAD-26OCT04GBTB-TB11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 53 market(s), e.g. KXNFL1HTOTAL-26OCT04GBTB-8, KXNFL4QTOTAL-26OCT04GBTB-4

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (12)**

- Baker Mayfield (QB, TB) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jalen McMillan (WR, TB) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jayden Reed (WR, GB) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Ko Kieft (TE, TB) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Aaron Banks (G, GB) — Out [high] — ruled out
- Jacob Monk (C, GB) — Out [high] — ruled out
- Zach Bako-Bewele (OT, GB) — Injured Reserve [high] — ruled out
- Anthony Campbell (DT, GB) — Out [high] — ruled out
- _...and 4 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Jager Burton (C, GB) — Questionable [high]
- Rakeem Nunez-Roches (DT, TB) — Questionable [high]
- SirVocea Dennis (LB, TB) — Questionable [high]

### WEATHER

- Partly Sunny · 88°F · wind 7 mph SSE · precip 7%
- forecast vintage 2026-10-03T20:10:21+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 89, 'wind': '7 mph', 'precipitation_probability': 0})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 62 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jordan Love | GB | attempts | 31.2 | 31.0 | 26.0 | 37.0 | 18.0 | 44.0 | 33.5 | 33.0 | 31.2 | 31.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kaleb Johnson | GB | carries | 9.6 | 9.0 | 5.0 | 13.0 | 1.0 | 21.0 | 9.3 | 9.0 | 9.6 | 9.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jordan Love | GB | completions | 19.5 | 20.0 | 16.0 | 23.0 | 11.0 | 29.0 | 20.6 | 20.0 | 19.5 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jordan Love | GB | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.5 | 1.0 | 1.5 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Jordan Love | GB | passing_yards | 231.4 | 227.0 | 176.0 | 283.0 | 106.0 | 373.0 | 243.9 | 238.0 | 243.8 | 239.0 | 0.00 | 0.97 | 10 | PRICED |
| Christian Watson | GB | receiving_yards | 66.2 | 57.0 | 28.0 | 94.0 | 0.0 | 164.0 | 73.7 | 66.0 | 73.7 | 63.0 | 0.00 | 0.98 | 13 | PRICED |
| Matthew Golden | GB | receiving_yards | 52.0 | 42.0 | 18.0 | 75.0 | 0.0 | 139.0 | 64.0 | 56.0 | 64.0 | 52.0 | 0.00 | 0.98 | 12 | PRICED |
| Tucker Kraft | GB | receiving_yards | 39.8 | 32.0 | 13.0 | 57.0 | 0.0 | 110.0 | 47.3 | 41.0 | 47.3 | 38.0 | 0.00 | 0.98 | 10 | PRICED |

_8 of 62 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 62 of 98 listed player/stat groups simulated and exposed, 36 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT04GBTB-TBJDANIELS10-4` | Jalon Daniels | 4.0 | 0.85 | 0.89 | 0.18 | -0.671 |
| `KXNFLREC-26OCT04GBTB-GBMGOLDEN0-3` | Matthew Golden | 3.0 | 0.82 | 0.83 | 0.24 | -0.589 |
| `KXNFLRSHATT-26OCT04GBTB-GBKJOHNSON26-6` | Kaleb Johnson | 6.0 | 0.83 | 0.84 | 0.29 | -0.547 |
| `KXNFLREC-26OCT04GBTB-GBMGOLDEN0-4` | Matthew Golden | 4.0 | 0.68 | 0.68 | 0.13 | -0.541 |
| `KXNFLRSHYDS-26OCT04GBTB-GBKJOHNSON26-15` | Kaleb Johnson | 15.0 | 0.80 | 0.80 | 0.27 | -0.527 |
| `KXNFLREC-26OCT04GBTB-GBCWATSON9-4` | Christian Watson | 4.0 | 0.71 | 0.72 | 0.20 | -0.514 |

_Ranked 400 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jayden Reed (WR, GB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Baker Mayfield (QB, TB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
4. KXNFLTOTAL-26OCT04GBTB-47 moved -0.215 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.671 on KXNFLRSHATT-26OCT04GBTB-TBJDANIELS10-4 (Jalon Daniels). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.589 on KXNFLREC-26OCT04GBTB-GBMGOLDEN0-3 (Matthew Golden). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT04GBTB-GBTKRAFT85-2 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_GB_TB.md`_


---

## JAX @ CIN — `2026_04_JAX_CIN`

- kickoff: 2026-10-04T17:00:00+00:00 (1233 minutes away) · state **PREGAME**
- venue: Paycor Stadium · roof outdoors · surface fieldturf
- markets: 787 listed across 16 families — 424 supported, 307 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.69 | -2.48 |
| total | 52.12 | 52.01 |
| score | CIN 27.4 – JAX 24.7 | CIN 27.2 – JAX 24.8 |
| win prob CIN | 56.5% | 57.7% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -1.41 / total 25.13 · **2H** spread -1.25 / total 26.03 · **1Q** spread -0.48 / total 9.50 · **2Q** spread -0.88 / total 15.09 · **3Q** spread -0.83 / total 10.13 · **4Q** spread -0.10 / total 14.88

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -2.69 · total 52.12
- move `KXNFLTOTAL-26OCT04JACCIN-35` +0.140
- move `KXNFL2HTOTAL-26OCT04JACCIN-8` +0.130
- move `KXNFLTOTAL-26OCT04JACCIN-38` +0.120
- move `KXNFLGAME-26OCT04JACCIN-JAC` -0.110

**Game environment** (simulation, mean and middle 50%) — home margin 2.6 (-5.0–10.0) · total 53.7 (45.0–62.0) · P(one score) 53.0% · P(17+ blowout) 17.9% · P(total 10+ over centre) 23.5%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CIN | 63.5 (58.0–69.0) | 36.8 (32.0–42.0) | 22.3 (17.0–27.0) | 40.3 (35.0–46.0) | 0.635 (0.568–0.703) | 0.550 / 0.722 |
| JAX | 62.4 (57.0–68.0) | 34.2 (29.0–39.0) | 23.0 (18.0–27.0) | 38.7 (33.0–44.0) | 0.622 (0.556–0.689) | 0.524 / 0.692 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CIN | 00-0038597 | RB | 4.1 (2.0–6.0) | 17.7 (13.0–22.0) | 11.6% | 79.6% | MEDIUM |
| CIN | 00-0036900 | WR | 10.1 (6.0–13.0) | 0.1 (0.0–0.0) | 28.4% | 0.3% | MEDIUM |
| CIN | 00-0036410 | WR | 6.9 (4.0–9.0) | 0.1 (0.0–0.0) | 19.3% | 0.2% | HIGH |
| CIN | 00-0034829 | TE | 3.7 (1.0–5.0) | 0.0 (0.0–0.0) | 10.3% | 0.1% | HIGH |
| JAX | 00-0040719 | RB | 1.9 (0.0–3.0) | 11.1 (6.0–15.0) | 5.9% | 48.2% | MEDIUM |
| JAX | 00-0038606 | WR | 7.6 (4.0–10.0) | 0.2 (0.0–0.0) | 23.0% | 1.0% | MEDIUM |
| JAX | 00-0038611 | RB | 0.6 (0.0–1.0) | 6.8 (3.0–10.0) | 1.9% | 29.6% | HIGH |
| JAX | 00-0034960 | WR | 5.8 (3.0–8.0) | 0.2 (0.0–0.0) | 17.6% | 0.9% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 14 market(s), e.g. KXNFLRECYDS-26OCT04JACCIN-JACBTHOMAS7-40, KXNFLRECYDS-26OCT04JACCIN-JACBTHOMAS7-30
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 76 market(s), e.g. KXNFL2HSPREAD-26OCT04JACCIN-CIN10, KXNFLPASSYDS-26OCT04JACCIN-JACTLAWRENCE16-300
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLBOTH-26OCT04JACCIN-28, KXNFLSPREAD-26OCT04JACCIN-JAC8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLTEAMTOTAL-26OCT04JACCIN-JAC22, KXNFLTOTAL-26OCT04JACCIN-48
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 200 market(s), e.g. KXNFL1H-26OCT04JACCIN-TIE, KXNFL1HFT-26OCT04JACCIN-JACCIN
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 64 market(s), e.g. KXNFL4QTOTAL-26OCT04JACCIN-4, KXNFLREC-26OCT04JACCIN-JACPWASHINGTON11-3

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (3)**

- Colbie Young (WR, CIN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jalen Davis (CB, CIN) — Injured Reserve [high] — ruled out
- Kyle Dugger (S, CIN) — Out [high] — ruled out

**Questionable / Doubtful (7)** — resolves at the inactive release, T−90m

- Dalton Risner (G, CIN) — Questionable [high]
- Albert Regis (DT, JAX) — Questionable [high]
- B.J. Hill (DT, CIN) — Questionable [high]
- Bryan Cook (S, CIN) — Questionable [high]
- Christian Braswell (CB, JAX) — Questionable [high]
- Montaric Brown (CB, JAX) — Questionable [high]
- Swayze Bozeman (LB, CIN) — Questionable [high]

### WEATHER

- None · None°F · wind None  · precip None%
- forecast vintage None · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 69 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Joe Burrow | CIN | attempts | 35.4 | 36.0 | 30.0 | 41.0 | 21.0 | 49.0 | 36.0 | 36.0 | 35.4 | 36.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chase Brown | CIN | carries | 17.7 | 18.0 | 13.0 | 22.0 | 6.0 | 30.0 | 16.1 | 16.0 | 17.7 | 18.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Joe Burrow | CIN | completions | 23.5 | 24.0 | 20.0 | 28.0 | 13.0 | 34.0 | 24.7 | 24.0 | 23.5 | 24.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Joe Burrow | CIN | passing_tds | 2.0 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.0 | 2.0 | 2.0 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Joe Burrow | CIN | passing_yards | 255.5 | 252.0 | 199.0 | 310.0 | 123.0 | 400.0 | 271.6 | 268.0 | 271.5 | 268.0 | 0.00 | 0.97 | 9 | PRICED |
| Ja'Marr Chase | CIN | receiving_yards | 79.6 | 72.0 | 42.0 | 109.0 | 8.0 | 177.0 | 90.3 | 82.0 | 90.2 | 81.0 | 0.00 | 0.97 | 13 | PRICED |
| Tee Higgins | CIN | receiving_yards | 59.2 | 49.0 | 23.0 | 85.0 | 0.0 | 154.0 | 69.0 | 61.0 | 68.9 | 57.0 | 0.00 | 0.97 | 12 | PRICED |
| Mike Gesicki | CIN | receiving_yards | 28.2 | 19.0 | 4.0 | 42.0 | 0.0 | 90.0 | 32.3 | 26.0 | 32.3 | 22.0 | 0.00 | 0.97 | 8 | PRICED |

_8 of 69 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 69 of 109 listed player/stat groups simulated and exposed, 40 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT04JACCIN-JACBTUTEN33-10` | Bhayshul Tuten | 10.0 | 0.78 | 0.79 | 0.19 | -0.590 |
| `KXNFLRSHYDS-26OCT04JACCIN-JACBTUTEN33-30` | Bhayshul Tuten | 30.0 | 0.81 | 0.82 | 0.23 | -0.583 |
| `KXNFLRSHYDS-26OCT04JACCIN-JACBTUTEN33-40` | Bhayshul Tuten | 40.0 | 0.70 | 0.71 | 0.14 | -0.561 |
| `KXNFLREC-26OCT04JACCIN-JACPWASHINGTON11-4` | Parker Washington | 4.0 | 0.77 | 0.77 | 0.27 | -0.497 |
| `KXNFLRSHYDS-26OCT04JACCIN-JACBTUTEN33-50` | Bhayshul Tuten | 50.0 | 0.57 | 0.58 | 0.09 | -0.488 |
| `KXNFLREC-26OCT04JACCIN-JACPWASHINGTON11-5` | Parker Washington | 5.0 | 0.62 | 0.63 | 0.15 | -0.474 |

_Ranked 421 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Colbie Young (WR, CIN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. KXNFLRECYDS-26OCT04JACCIN-CINJCHASE1-110 moved +0.140 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
3. The model disagrees by -0.590 on KXNFLRSHATT-26OCT04JACCIN-JACBTUTEN33-10 (Bhayshul Tuten). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
4. The model disagrees by -0.583 on KXNFLRSHYDS-26OCT04JACCIN-JACBTUTEN33-30 (Bhayshul Tuten). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. KXNFLREC-26OCT04JACCIN-JACPWASHINGTON11-3 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_JAX_CIN.md`_


---

## LA @ PHI — `2026_04_LA_PHI`

- kickoff: 2026-10-04T17:00:00+00:00 (1233 minutes away) · state **PREGAME**
- venue: Lincoln Financial Field · roof outdoors · surface grass
- markets: 698 listed across 16 families — 353 supported, 289 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.62 | 3.53 |
| total | 43.30 | 43.30 |
| score | PHI 19.8 – LA 23.5 | PHI 19.9 – LA 23.4 |
| win prob PHI | 36.5% | 36.4% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.69 / total 22.25 · **2H** spread 1.67 / total 21.17 · **1Q** spread 0.93 / total 7.91 · **2Q** spread 1.62 / total 13.35 · **3Q** spread 1.28 / total 8.00 · **4Q** spread 0.33 / total 11.09

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 3.62 · total 43.30
- move `KXNFLGAME-26OCT04LARPHI-PHI` -0.225
- move `KXNFLGAME-26OCT04LARPHI-LAR` +0.175

**Game environment** (simulation, mean and middle 50%) — home margin -3.6 (-11.0–4.0) · total 44.7 (36.0–53.0) · P(one score) 53.7% · P(17+ blowout) 18.7% · P(total 10+ over centre) 23.0%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| PHI | 61.6 (56.0–67.0) | 31.9 (27.0–36.0) | 24.1 (19.0–29.0) | 36.9 (32.0–42.0) | 0.600 (0.534–0.667) | 0.494 / 0.663 |
| LA | 64.4 (59.0–70.0) | 35.5 (30.0–40.0) | 25.6 (21.0–30.0) | 37.8 (32.0–43.0) | 0.588 (0.522–0.656) | 0.509 / 0.683 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| PHI | 00-0034844 | RB | 4.3 (2.0–6.0) | 16.3 (11.0–21.0) | 14.3% | 67.5% | MEDIUM |
| PHI | 00-0038393 | WR | 7.4 (4.0–10.0) | 0.1 (0.0–0.0) | 24.6% | 0.5% | MEDIUM |
| PHI | 00-0040867 | WR | 5.5 (3.0–8.0) | 0.2 (0.0–0.0) | 18.5% | 0.6% | HIGH |
| PHI | 00-0036389 | QB | 0.1 (0.0–0.0) | 5.4 (3.0–7.0) | 0.3% | 7.3% | HIGH |
| LA | 00-0037840 | RB | 2.8 (1.0–4.0) | 14.4 (9.0–19.0) | 8.2% | 56.2% | MEDIUM |
| LA | 00-0039075 | WR | 9.6 (6.0–13.0) | 0.5 (0.0–0.0) | 28.2% | 2.1% | MEDIUM |
| LA | 00-0039738 | RB | 1.4 (0.0–2.0) | 8.0 (3.0–11.0) | 4.2% | 31.4% | HIGH |
| LA | 00-0031381 | WR | 7.1 (4.0–10.0) | 0.0 (0.0–0.0) | 21.1% | 0.2% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 15 market(s), e.g. KXNFLPASSCOMP-26OCT04LARPHI-PHIJHURTS1-25, KXNFLPASSCOMP-26OCT04LARPHI-PHIJHURTS1-20
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 50 market(s), e.g. KXNFLDSTTD-26OCT04LARPHI-Y, KXNFLPASSYDS-26OCT04LARPHI-LARMSTAFFORD9-300
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT04LARPHI-PHI8, KXNFLSPREAD-26OCT04LARPHI-PHI7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLGAME-26OCT04LARPHI-LAR, KXNFLSPREAD-26OCT04LARPHI-LAR3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 194 market(s), e.g. KXNFL1HFT-26OCT04LARPHI-PHILAR, KXNFL1HFT-26OCT04LARPHI-LARPHI
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 45 market(s), e.g. KXNFLREC-26OCT04LARPHI-LARPNACUA12-3, KXNFLRECYDS-26OCT04LARPHI-PHIDWICKS13-15

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (11)**

- Dallas Goedert (TE, PHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- DeVonta Smith (WR, PHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Hollywood Brown (WR, PHI) — Out [single_source] — ruled out -- role redistributes to the depth chart behind him
- Ronnie Rivers (RB, LA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Terrance Ferguson (TE, LA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Fred Johnson (OT, PHI) — Out [high] — ruled out
- Aaron Donald (DT, LA) — Out [single_source] — ruled out
- Jaylen Watson (CB, LA) — Out [single_source] — ruled out
- _...and 3 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Colby Parkinson (TE, LA) — Questionable [single_source]

### WEATHER

- Chance Rain Showers · 65°F · wind 5 mph E · precip 45%
- forecast vintage 2026-10-03T20:09:20+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 52 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Matthew Stafford | LA | attempts | 34.1 | 34.0 | 29.0 | 40.0 | 20.0 | 48.0 | 34.8 | 34.0 | 34.1 | 34.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kyren Williams | LA | carries | 14.4 | 14.0 | 9.0 | 19.0 | 3.0 | 27.0 | 13.7 | 13.0 | 14.4 | 14.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Blake Corum | LA | carries | 8.0 | 7.0 | 3.0 | 11.0 | 0.0 | 20.0 | 10.2 | 10.0 | 8.0 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Matthew Stafford | LA | completions | 21.0 | 21.0 | 17.0 | 25.0 | 11.0 | 31.0 | 21.4 | 21.0 | 21.0 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Matthew Stafford | LA | passing_tds | 1.6 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.7 | 1.0 | 1.7 | 2.0 | 0.00 | 0.98 | 5 | PRICED |
| Matthew Stafford | LA | passing_yards | 260.6 | 256.0 | 201.0 | 317.0 | 124.0 | 414.0 | 250.6 | 245.0 | 250.6 | 246.0 | 0.00 | 0.98 | 9 | PRICED |
| Puka Nacua | LA | receiving_yards | 82.2 | 74.0 | 41.0 | 114.0 | 7.0 | 186.0 | 71.0 | 64.0 | 71.0 | 64.0 | 0.00 | 0.97 | 14 | PRICED |
| Davante Adams | LA | receiving_yards | 64.3 | 54.0 | 24.0 | 93.0 | 0.0 | 165.0 | 71.3 | 63.0 | 71.2 | 59.0 | 0.00 | 0.97 | 14 | PRICED |

_8 of 52 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 52 of 86 listed player/stat groups simulated and exposed, 34 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRECYDS-26OCT04LARPHI-PHIDSMITH6-40` | DeVonta Smith | 40.0 | 0.69 | 0.71 | 0.00 | -0.681 |
| `KXNFLREC-26OCT04LARPHI-PHIMLEMON9-2` | Makai Lemon | 2.0 | 0.85 | 0.87 | 0.32 | -0.531 |
| `KXNFLREC-26OCT04LARPHI-PHIMLEMON9-3` | Makai Lemon | 3.0 | 0.69 | 0.70 | 0.19 | -0.502 |
| `KXNFLREC-26OCT04LARPHI-PHIDWICKS13-3` | Dontayvion Wicks | 3.0 | 0.74 | 0.75 | 0.26 | -0.484 |
| `KXNFLRSHATT-26OCT04LARPHI-PHIJHURTS1-4` | Jalen Hurts | 4.0 | 0.82 | 0.84 | 0.36 | -0.464 |
| `KXNFLRECYDS-26OCT04LARPHI-PHIDWICKS13-50` | Dontayvion Wicks | 50.0 | 0.56 | 0.57 | 0.11 | -0.452 |

_Ranked 341 tradable markets; 12 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Ronnie Rivers (RB, LA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Terrance Ferguson (TE, LA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Colby Parkinson (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLREC-26OCT04LARPHI-PHIMLEMON9-4 moved +0.245 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.681 on KXNFLRECYDS-26OCT04LARPHI-PHIDSMITH6-40 (DeVonta Smith). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.531 on KXNFLREC-26OCT04LARPHI-PHIMLEMON9-2 (Makai Lemon). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT04LARPHI-PHIDWICKS13-2 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_LA_PHI.md`_


---

## NE @ BUF — `2026_04_NE_BUF`

- kickoff: 2026-10-04T17:00:00+00:00 (1233 minutes away) · state **PREGAME**
- venue: Highmark Stadium · roof outdoors · surface a_turf
- markets: 796 listed across 16 families — 432 supported, 308 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -6.81 | -6.98 |
| total | 50.62 | 50.76 |
| score | BUF 28.7 – NE 21.9 | BUF 28.9 – NE 21.9 |
| win prob BUF | 73.5% | 74.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -4.25 / total 24.72 · **2H** spread -3.32 / total 24.75 · **1Q** spread -2.56 / total 8.95 · **2Q** spread -2.77 / total 15.00 · **3Q** spread -0.94 / total 9.67 · **4Q** spread -1.30 / total 14.40

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -6.81 · total 50.62
- move `KXNFL1HTEAMTOTAL-26OCT04NEBUF-BUF10` +0.225
- move `KXNFLTOTAL-26OCT04NEBUF-40` +0.170
- move `KXNFL3QTOTAL-26OCT04NEBUF-7` +0.135
- move `KXNFLTOTAL-26OCT04NEBUF-50` +0.130

**Game environment** (simulation, mean and middle 50%) — home margin 6.6 (-1.0–14.0) · total 51.7 (42.0–60.0) · P(one score) 48.1% · P(17+ blowout) 20.6% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| BUF | 63.9 (58.0–70.0) | 31.4 (26.0–36.0) | 26.1 (21.0–31.0) | 36.7 (31.0–42.0) | 0.575 (0.508–0.644) | 0.504 / 0.682 |
| NE | 61.4 (56.0–67.0) | 32.3 (28.0–37.0) | 21.5 (17.0–26.0) | 39.4 (34.0–44.0) | 0.642 (0.578–0.709) | 0.527 / 0.698 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| BUF | 00-0037248 | RB | 2.4 (1.0–4.0) | 17.2 (12.0–22.0) | 7.9% | 66.0% | MEDIUM |
| BUF | 00-0034857 | QB | 0.3 (0.0–0.0) | 8.3 (5.0–11.0) | 1.0% | 16.6% | HIGH |
| BUF | 00-0034827 | WR | 5.3 (3.0–7.0) | 0.3 (0.0–0.0) | 17.5% | 1.0% | HIGH |
| BUF | 00-0037261 | WR | 5.0 (2.0–7.0) | 0.1 (0.0–0.0) | 16.5% | 0.3% | HIGH |
| NE | 00-0036875 | RB | 3.5 (1.0–5.0) | 8.3 (4.0–12.0) | 11.4% | 38.8% | MEDIUM |
| NE | 00-0040734 | RB | 1.8 (0.0–3.0) | 7.7 (4.0–11.0) | 5.7% | 35.7% | HIGH |
| NE | 00-0039851 | QB | 0.1 (0.0–0.0) | 5.7 (4.0–7.0) | 0.2% | 5.5% | MEDIUM |
| NE | 00-0037816 | WR | 5.5 (3.0–8.0) | 0.0 (0.0–0.0) | 17.9% | 0.1% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 16 market(s), e.g. KXNFLPASSATT-26OCT04NEBUF-BUFJALLEN17-30, KXNFLPASSCOMP-26OCT04NEBUF-NEDMAYE10-25
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 80 market(s), e.g. KXNFL1QSPREAD-26OCT04NEBUF-NE3, KXNFLPASSYDS-26OCT04NEBUF-BUFJALLEN17-250
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLGAME-26OCT04NEBUF-NE, KXNFLSPREAD-26OCT04NEBUF-NE7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLSPREAD-26OCT04NEBUF-BUF4, KXNFLSPREAD-26OCT04NEBUF-BUF3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 198 market(s), e.g. KXNFL1HSPREAD-26OCT04NEBUF-NE8, KXNFL1HSPREAD-26OCT04NEBUF-NE11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 44 market(s), e.g. KXNFL1HTOTAL-26OCT04NEBUF-11, KXNFL4QTOTAL-26OCT04NEBUF-4

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (7)**

- A.J. Brown (WR, NE) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Greg Van Roten (G, NE) — Injured Reserve [single_source] — ruled out
- Christian Barmore (DT, NE) — Out [high] — ruled out
- Christian Gonzalez (CB, NE) — Out [high] — ruled out
- Dell Pettus (S, NE) — Injured Reserve [high] — ruled out
- Jordan Hancock (CB, BUF) — Injured Reserve [high] — ruled out
- Quintayvious Hutchins (LB, NE) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (11)** — resolves at the inactive release, T−90m

- Eli Raridon (TE, NE) — Questionable [high]
- Ray Davis (RB, BUF) — Questionable [high]
- Morgan Moses (OT, NE) — Questionable [high]
- Channing Canada (CB, NE) — Questionable [high]
- Christian Benford (CB, BUF) — Questionable [high]
- Christian Elliss (LB, NE) — Questionable [high]
- Craig Woodson (S, NE) — Questionable [high]
- Dre'Mont Jones (DE, NE) — Questionable [high]

### WEATHER

- Mostly Sunny · 67°F · wind 6 mph SW · precip 4%
- forecast vintage 2026-10-03T20:09:14+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 66, 'wind': '6 mph', 'precipitation_probability': 5})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 67 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Josh Allen | BUF | attempts | 30.2 | 30.0 | 25.0 | 35.0 | 17.0 | 43.0 | 29.7 | 29.0 | 30.2 | 30.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| James Cook III | BUF | carries | 17.2 | 17.0 | 12.0 | 22.0 | 5.0 | 31.0 | 17.9 | 18.0 | 17.2 | 17.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | carries | 8.3 | 7.0 | 5.0 | 11.0 | 2.0 | 18.0 | 8.1 | 8.0 | 8.3 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | completions | 20.1 | 20.0 | 16.0 | 24.0 | 11.0 | 30.0 | 20.3 | 20.0 | 20.1 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | passing_tds | 1.8 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 1.9 | 2.0 | 1.9 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Josh Allen | BUF | passing_yards | 223.3 | 219.0 | 171.0 | 272.0 | 102.0 | 356.0 | 245.4 | 240.0 | 245.4 | 241.0 | 0.00 | 0.97 | 9 | PRICED |
| DJ Moore | BUF | receiving_yards | 43.9 | 35.0 | 14.0 | 64.0 | 0.0 | 120.0 | 57.0 | 49.0 | 57.0 | 45.0 | 0.00 | 0.98 | 12 | PRICED |
| Dalton Kincaid | BUF | receiving_yards | 40.4 | 31.0 | 12.0 | 59.0 | 0.0 | 114.0 | 56.3 | 50.0 | 56.3 | 43.0 | 0.00 | 0.97 | 12 | PRICED |

_8 of 67 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 67 of 108 listed player/stat groups simulated and exposed, 41 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT04NEBUF-BUFDKINCAID86-3` | Dalton Kincaid | 3.0 | 0.81 | 0.82 | 0.25 | -0.562 |
| `KXNFLRSHATT-26OCT04NEBUF-BUFJALLEN17-5` | Josh Allen | 5.0 | 0.85 | 0.86 | 0.30 | -0.548 |
| `KXNFLREC-26OCT04NEBUF-BUFDKINCAID86-4` | Dalton Kincaid | 4.0 | 0.65 | 0.65 | 0.14 | -0.505 |
| `KXNFLRSHATT-26OCT04NEBUF-BUFJCOOK4-15` | James Cook III | 15.0 | 0.74 | 0.76 | 0.24 | -0.496 |
| `KXNFLREC-26OCT04NEBUF-BUFDKINCAID86-2` | Dalton Kincaid | 2.0 | 0.92 | 0.92 | 0.42 | -0.491 |
| `KXNFLRSHATT-26OCT04NEBUF-NEDMAYE10-3` | Drake Maye | 3.0 | 0.88 | 0.89 | 0.40 | -0.481 |

_Ranked 432 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. A.J. Brown (WR, NE) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 2 skill players are Questionable (Ray Davis (RB), Eli Raridon (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
4. KXNFL1HTEAMTOTAL-26OCT04NEBUF-BUF10 moved +0.225 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.562 on KXNFLREC-26OCT04NEBUF-BUFDKINCAID86-3 (Dalton Kincaid). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.548 on KXNFLRSHATT-26OCT04NEBUF-BUFJALLEN17-5 (Josh Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT04NEBUF-BUFDKINCAID86-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_NE_BUF.md`_


---

## NYJ @ CHI — `2026_04_NYJ_CHI`

- kickoff: 2026-10-04T17:00:00+00:00 (1233 minutes away) · state **PREGAME**
- venue: Soldier Field · roof outdoors · surface grass
- markets: 709 listed across 16 families — 358 supported, 295 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.44 | -3.38 |
| total | 43.83 | 42.85 |
| score | CHI 23.6 – NYJ 20.2 | CHI 23.1 – NYJ 19.7 |
| win prob CHI | 63.5% | 61.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -2.69 / total 21.70 · **2H** spread -1.73 / total 21.44 · **1Q** spread -1.22 / total 7.90 · **2Q** spread -1.73 / total 13.16 · **3Q** spread -1.10 / total 8.00 · **4Q** spread -0.38 / total 11.75

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.44 · total 43.83
- move `KXNFLTOTAL-26OCT04NYJCHI-28` +0.120
- move `KXNFL3QSPREAD-26OCT04NYJCHI-CHI3` +0.115
- move `KXNFLSPREAD-26OCT04NYJCHI-CHI18` -0.115
- move `KXNFL1HTOTAL-26OCT04NYJCHI-4` +0.105

**Game environment** (simulation, mean and middle 50%) — home margin 3.6 (-4.0–11.0) · total 44.5 (35.0–52.0) · P(one score) 52.4% · P(17+ blowout) 17.9% · P(total 10+ over centre) 23.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CHI | 64.8 (59.0–70.0) | 33.8 (29.0–39.0) | 26.6 (21.0–31.0) | 37.2 (32.0–42.0) | 0.575 (0.507–0.644) | 0.493 / 0.667 |
| NYJ | 61.8 (56.0–67.0) | 31.9 (27.0–36.0) | 24.6 (20.0–29.0) | 36.5 (31.0–42.0) | 0.593 (0.527–0.660) | 0.486 / 0.660 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CHI | 00-0036275 | RB | 2.8 (1.0–4.0) | 15.4 (10.0–20.0) | 8.7% | 57.8% | MEDIUM |
| CHI | 00-0040236 | RB | 1.6 (0.0–2.0) | 8.5 (4.0–12.0) | 5.2% | 32.1% | HIGH |
| CHI | 00-0040735 | WR | 6.1 (3.0–8.0) | 0.7 (0.0–0.0) | 19.4% | 2.5% | HIGH |
| CHI | 00-0039919 | WR | 5.7 (3.0–8.0) | 0.0 (0.0–0.0) | 18.0% | 0.1% | HIGH |
| NYJ | 00-0039794 | RB | 2.4 (0.0–3.0) | 10.7 (6.0–15.0) | 7.8% | 43.4% | MEDIUM |
| NYJ | 00-0037740 | WR | 11.6 (8.0–15.0) | 0.0 (0.0–0.0) | 38.0% | 0.1% | MEDIUM |
| NYJ | 00-0036842 | RB | 0.4 (0.0–0.0) | 7.1 (3.0–10.0) | 1.2% | 29.1% | HIGH |
| NYJ | 00-0039798 | RB | 1.7 (0.0–2.0) | 4.4 (1.0–6.0) | 5.4% | 17.8% | HIGH |

**Historical research tags** (7; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 56 market(s), e.g. KXNFLPASSYDS-26OCT04NYJCHI-NYJGSMITH7-275, KXNFLPASSYDS-26OCT04NYJCHI-NYJGSMITH7-250
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT04NYJCHI-NYJ8, KXNFLSPREAD-26OCT04NYJCHI-NYJ6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLGAME-26OCT04NYJCHI-CHI, KXNFLTEAMTOTAL-26OCT04NYJCHI-CHI21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 185 market(s), e.g. KXNFL1H-26OCT04NYJCHI-TIE, KXNFL1QSPREAD-26OCT04NYJCHI-NYJ8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 51 market(s), e.g. KXNFL1HTOTAL-26OCT04NYJCHI-11, KXNFLPASSYDS-26OCT04NYJCHI-NYJGSMITH7-150
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 147 market(s), e.g. KXNFLPASSCOMP-26OCT04NYJCHI-CHITBAGENT17-25, KXNFLPASSINT-26OCT04NYJCHI-NYJGSMITH7-2

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (13)**

- Caleb Williams (QB, CHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Adonai Mitchell (WR, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Arian Smith (WR, NYJ) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Breece Hall (RB, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Mason Taylor (TE, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Braxton Jones (OT, CHI) — Out [high] — ruled out
- Dylan Parham (G, NYJ) — Out [high] — ruled out
- Anthony Johnson Jr. (S, CHI) — Injured Reserve [single_source] · **CHANGED from Out** — ruled out
- _...and 5 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Kenyon Sadiq (TE, NYJ) — Questionable [high]
- Cam Lewis (CB, CHI) — Doubtful [high]
- Kingsley Enagbare (LB, NYJ) — Questionable [high]

### WEATHER

- Mostly Sunny · 67°F · wind 10 mph WNW · precip 0%
- forecast vintage 2026-10-03T20:09:15+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 55 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tyson Bagent | CHI | attempts | 32.4 | 33.0 | 27.0 | 38.0 | 19.0 | 46.0 | 29.7 | 29.0 | 32.4 | 33.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| D'Andre Swift | CHI | carries | 15.4 | 15.0 | 10.0 | 20.0 | 4.0 | 29.0 | 15.2 | 15.0 | 15.4 | 15.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kyle Monangai | CHI | carries | 8.5 | 7.0 | 4.0 | 12.0 | 0.0 | 21.0 | 9.6 | 9.0 | 8.5 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyson Bagent | CHI | completions | 20.6 | 21.0 | 17.0 | 24.0 | 11.0 | 30.0 | 19.2 | 19.0 | 20.6 | 21.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Tyson Bagent | CHI | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Tyson Bagent | CHI | passing_yards | 227.7 | 223.0 | 174.0 | 276.0 | 107.0 | 365.0 | 204.6 | 198.0 | 204.6 | 200.0 | 0.00 | 0.97 | 7 | PRICED |
| Rome Odunze | CHI | receiving_yards | 48.2 | 38.0 | 15.0 | 71.0 | 0.0 | 134.0 | 39.1 | 31.0 | 39.1 | 30.0 | 0.00 | 0.98 | 8 | PRICED |
| Luther Burden III | CHI | receiving_yards | 47.7 | 39.0 | 18.0 | 69.0 | 0.0 | 123.0 | 52.8 | 46.0 | 52.8 | 44.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 55 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 55 of 94 listed player/stat groups simulated and exposed, 39 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26OCT04NYJCHI-NYJBALLEN0-30` | Braelon Allen | 30.0 | 0.83 | 0.84 | 0.20 | -0.631 |
| `KXNFLREC-26OCT04NYJCHI-NYJGWILSON5-5` | Garrett Wilson | 5.0 | 0.74 | 0.76 | 0.17 | -0.577 |
| `KXNFLRSHYDS-26OCT04NYJCHI-NYJBALLEN0-40` | Braelon Allen | 40.0 | 0.71 | 0.72 | 0.14 | -0.568 |
| `KXNFLREC-26OCT04NYJCHI-NYJGWILSON5-4` | Garrett Wilson | 4.0 | 0.86 | 0.87 | 0.30 | -0.564 |
| `KXNFLRSHATT-26OCT04NYJCHI-NYJBALLEN0-12` | Braelon Allen | 12.0 | 0.68 | 0.69 | 0.13 | -0.545 |
| `KXNFLREC-26OCT04NYJCHI-NYJGWILSON5-6` | Garrett Wilson | 6.0 | 0.61 | 0.62 | 0.09 | -0.523 |

_Ranked 357 tradable markets; 1 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Caleb Williams (QB, CHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Adonai Mitchell (WR, NYJ) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Kenyon Sadiq (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRECYDS-26OCT04NYJCHI-CHICLOVELAND84-50 moved +0.160 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.631 on KXNFLRSHYDS-26OCT04NYJCHI-NYJBALLEN0-30 (Braelon Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.577 on KXNFLREC-26OCT04NYJCHI-NYJGWILSON5-5 (Garrett Wilson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT04NYJCHI-CHILBURDEN10-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_NYJ_CHI.md`_


---

## TEN @ BAL — `2026_04_TEN_BAL`

- kickoff: 2026-10-04T17:00:00+00:00 (1233 minutes away) · state **PREGAME**
- venue: M&T Bank Stadium · roof outdoors · surface grass
- markets: 740 listed across 16 families — 386 supported, 296 no model, 48 rules unresolved, 10 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 10 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -11.33 | -12.07 |
| total | 42.88 | 42.99 |
| score | BAL 27.1 – TEN 15.8 | BAL 27.5 – TEN 15.5 |
| win prob BAL | 84.5% | 86.3% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -7.11 / total 22.25 · **2H** spread -4.96 / total 20.48 · **1Q** spread -2.95 / total 7.92 · **2Q** spread -4.18 / total 13.42 · **3Q** spread -2.79 / total 8.00 · **4Q** spread -2.80 / total 10.83

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -11.33 · total 42.88
- move `KXNFLGAME-26OCT04TENBAL-BAL` +0.215
- move `KXNFLGAME-26OCT04TENBAL-TEN` -0.115

**Game environment** (simulation, mean and middle 50%) — home margin 11.5 (4.0–19.0) · total 43.8 (35.0–52.0) · P(one score) 33.6% · P(17+ blowout) 33.5% · P(total 10+ over centre) 23.9%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| BAL | 61.2 (56.0–67.0) | 24.9 (20.0–29.0) | 30.3 (25.0–35.0) | 29.7 (24.0–35.0) | 0.485 (0.417–0.554) | 0.431 / 0.624 |
| TEN | 59.1 (53.0–65.0) | 32.5 (28.0–37.0) | 22.5 (18.0–27.0) | 36.3 (31.0–41.0) | 0.615 (0.551–0.680) | 0.466 / 0.655 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| BAL | 00-0032764 | RB | 1.5 (0.0–2.0) | 21.2 (15.0–27.0) | 6.2% | 69.8% | MEDIUM |
| BAL | 00-0034796 | QB | 0.1 (0.0–0.0) | 6.1 (3.0–8.0) | 0.3% | 7.2% | HIGH |
| BAL | 00-0034975 | RB | 1.7 (0.0–3.0) | 4.1 (0.0–6.0) | 7.0% | 13.5% | HIGH |
| BAL | 00-0039064 | WR | 4.8 (1.0–7.0) | 0.3 (0.0–0.0) | 19.8% | 1.1% | HIGH |
| TEN | 00-0035261 | RB | 1.9 (0.0–3.0) | 10.6 (6.0–14.0) | 6.2% | 47.5% | MEDIUM |
| TEN | 00-0036924 | RB | 2.0 (0.0–3.0) | 5.9 (2.0–9.0) | 6.6% | 26.3% | HIGH |
| TEN | 00-0041438 | WR | 6.1 (3.0–8.0) | 0.0 (0.0–0.0) | 20.1% | 0.0% | HIGH |
| TEN | 00-0038117 | WR | 5.8 (3.0–8.0) | 0.0 (0.0–0.0) | 19.1% | 0.2% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 16 market(s), e.g. KXNFLPASSATT-26OCT04TENBAL-BALLJACKSON8-33, KXNFLPASSATT-26OCT04TENBAL-BALLJACKSON8-28
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 48 market(s), e.g. KXNFLFIRSTTD-26OCT04TENBAL-BALDHENRY22, KXNFLREC-26OCT04TENBAL-BALJHILL43-3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 15 market(s), e.g. KXNFLGAME-26OCT04TENBAL-TEN, KXNFLSPREAD-26OCT04TENBAL-BAL28
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLSPREAD-26OCT04TENBAL-BAL8, KXNFLSPREAD-26OCT04TENBAL-BAL7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 219 market(s), e.g. KXNFL1HFT-26OCT04TENBAL-TENBAL, KXNFL1QSPREAD-26OCT04TENBAL-TEN7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 51 market(s), e.g. KXNFLMOSTRSHYDS-26OCT04TENBAL-BALLJACKSON8, KXNFLREC-26OCT04TENBAL-TENWROBINSON4-2

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (5)**

- Ethan Pocic (C, BAL) — Out [high] — ruled out
- Fernando Carmona (G, TEN) — Injured Reserve [high] — ruled out
- Jackson Slater (G, TEN) — Injured Reserve [high] — ruled out
- Jovaughn Gwyn (G, BAL) — Out [high] — ruled out
- Trey Hendrickson (LB, BAL) — Out [high] — ruled out

**Questionable / Doubtful (6)** — resolves at the inactive release, T−90m

- Chris Moore (WR, BAL) — Questionable [high]
- Tyjae Spears (RB, TEN) — Questionable [high]
- Zay Flowers (WR, BAL) — Questionable [high]
- Garrett Dellinger (G, TEN) — Questionable [single_source]
- Ronnie Stanley (OT, BAL) — Questionable [high]
- Kevin Winston Jr. (S, TEN) — Questionable [single_source]

### WEATHER

- Chance Rain Showers · 64°F · wind 6 mph NE · precip 34%
- forecast vintage 2026-10-03T20:08:54+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 65, 'wind': '7 mph', 'precipitation_probability': 75})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 63 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Lamar Jackson | BAL | attempts | 23.9 | 24.0 | 19.0 | 29.0 | 12.0 | 36.0 | 26.5 | 26.0 | 23.9 | 24.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Derrick Henry | BAL | carries | 21.2 | 21.0 | 15.0 | 27.0 | 7.0 | 36.0 | 21.4 | 21.0 | 21.2 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Lamar Jackson | BAL | carries | 6.1 | 5.0 | 3.0 | 8.0 | 1.0 | 14.0 | 6.3 | 6.0 | 6.1 | 5.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Justice Hill | BAL | carries | 4.1 | 2.0 | 0.0 | 6.0 | 0.0 | 14.0 | 4.6 | 4.0 | 4.1 | 2.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Lamar Jackson | BAL | completions | 16.5 | 16.0 | 13.0 | 20.0 | 8.0 | 25.0 | 18.1 | 18.0 | 16.5 | 16.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Lamar Jackson | BAL | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.7 | 2.0 | 1.7 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Lamar Jackson | BAL | passing_yards | 192.8 | 188.0 | 141.0 | 239.0 | 80.0 | 323.0 | 218.2 | 211.0 | 218.2 | 213.0 | 0.00 | 0.97 | 9 | PRICED |
| Zay Flowers | BAL | receiving_yards | 46.8 | 36.0 | 0.0 | 73.0 | 0.0 | 139.0 | 78.4 | 71.0 | 77.6 | 60.0 | 0.00 | 0.78 | 13 | PRICED |

_8 of 63 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 63 of 95 listed player/stat groups simulated and exposed, 32 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT04TENBAL-TENCTATE14-3` | Carnell Tate | 3.0 | 0.80 | 0.81 | 0.18 | -0.610 |
| `KXNFLREC-26OCT04TENBAL-TENCTATE14-2` | Carnell Tate | 2.0 | 0.91 | 0.91 | 0.31 | -0.592 |
| `KXNFLRSHATT-26OCT04TENBAL-BALDHENRY22-17` | Derrick Henry | 17.0 | 0.79 | 0.82 | 0.24 | -0.553 |
| `KXNFLREC-26OCT04TENBAL-TENCTATE14-4` | Carnell Tate | 4.0 | 0.64 | 0.65 | 0.11 | -0.530 |
| `KXNFLREC-26OCT04TENBAL-BALMANDREWS89-3` | Mark Andrews | 3.0 | 0.74 | 0.75 | 0.24 | -0.498 |
| `KXNFLRSHATT-26OCT04TENBAL-BALDHENRY22-20` | Derrick Henry | 20.0 | 0.61 | 0.62 | 0.12 | -0.494 |

_Ranked 379 tradable markets; 7 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. 3 skill players are Questionable (Chris Moore (WR), Zay Flowers (WR), Tyjae Spears (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
2. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
3. KXNFLGAME-26OCT04TENBAL-BAL moved +0.215 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.610 on KXNFLREC-26OCT04TENBAL-TENCTATE14-3 (Carnell Tate). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.592 on KXNFLREC-26OCT04TENBAL-TENCTATE14-2 (Carnell Tate). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26OCT04TENBAL-TENCTATE14-2 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_TEN_BAL.md`_


---

## MIA @ MIN — `2026_04_MIA_MIN`

- kickoff: 2026-10-04T20:05:00+00:00 (1418 minutes away) · state **PREGAME**
- venue: U.S. Bank Stadium · roof dome · surface sportturf
- markets: 731 listed across 16 families — 377 supported, 298 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -9.80 | -9.87 |
| total | 39.12 | 37.76 |
| score | MIN 24.5 – MIA 14.7 | MIN 23.8 – MIA 13.9 |
| win prob MIN | 83.5% | 82.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -6.75 / total 20.41 · **2H** spread -4.00 / total 19.00 · **1Q** spread -2.79 / total 7.58 · **2Q** spread -3.41 / total 11.75 · **3Q** spread -2.54 / total 7.69 · **4Q** spread -2.67 / total 9.94

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -9.80 · total 39.12
- move `KXNFLGAME-26OCT04MIAMIN-MIN` +0.175
- move `KXNFLGAME-26OCT04MIAMIN-MIA` -0.145
- move `KXNFLTOTAL-26OCT04MIAMIN-39` -0.125
- move `KXNFLTOTAL-26OCT04MIAMIN-51` -0.125

**Game environment** (simulation, mean and middle 50%) — home margin 9.6 (2.0–17.0) · total 40.7 (32.0–49.0) · P(one score) 38.5% · P(17+ blowout) 26.8% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| MIN | 60.2 (55.0–66.0) | 27.8 (23.0–32.0) | 26.4 (21.0–31.0) | 32.7 (27.0–38.0) | 0.543 (0.475–0.614) | 0.483 / 0.668 |
| MIA | 59.0 (53.0–65.0) | 27.9 (24.0–32.0) | 23.3 (19.0–28.0) | 35.3 (30.0–40.0) | 0.599 (0.535–0.664) | 0.466 / 0.644 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| MIN | 00-0033293 | RB | 4.4 (2.0–6.0) | 19.1 (14.0–24.0) | 16.8% | 72.7% | MEDIUM |
| MIN | 00-0038994 | WR | 6.7 (4.0–9.0) | 0.1 (0.0–0.0) | 25.1% | 0.4% | HIGH |
| MIN | 00-0035229 | TE | 5.5 (3.0–8.0) | 0.0 (0.0–0.0) | 20.9% | 0.1% | HIGH |
| MIN | 00-0035228 | QB | 0.0 (0.0–0.0) | 4.6 (3.0–6.0) | 0.0% | 3.7% | HIGH |
| MIA | 00-0040198 | RB | 1.6 (0.0–2.0) | 10.6 (6.0–14.0) | 5.8% | 45.4% | MEDIUM |
| MIA | 00-0039880 | WR | 7.3 (4.0–10.0) | 1.5 (0.0–2.0) | 26.9% | 6.4% | MEDIUM |
| MIA | 00-0038128 | QB | 0.7 (0.0–1.0) | 7.4 (4.0–9.0) | 2.5% | 12.6% | MEDIUM |
| MIA | 00-0039874 | RB | 0.8 (0.0–1.0) | 6.7 (3.0–10.0) | 3.1% | 28.9% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 14 market(s), e.g. KXNFLPASSATT-26OCT04MIAMIN-MINKMURRAY1-34, KXNFLPASSATT-26OCT04MIAMIN-MINKMURRAY1-29
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 58 market(s), e.g. KXNFL1Q-26OCT04MIAMIN-TIE, KXNFL3Q-26OCT04MIAMIN-TIE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 15 market(s), e.g. KXNFLGAME-26OCT04MIAMIN-MIA, KXNFLSPREAD-26OCT04MIAMIN-MIN21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLSPREAD-26OCT04MIAMIN-MIN6, KXNFLSPREAD-26OCT04MIAMIN-MIN5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 219 market(s), e.g. KXNFL1H-26OCT04MIAMIN-TIE, KXNFL1HFT-26OCT04MIAMIN-TIEMIN
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 59 market(s), e.g. KXNFLPASSCOMP-26OCT04MIAMIN-MINKMURRAY1-15, KXNFLREC-26OCT04MIAMIN-MINTHOCKENSON87-2

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (10)**

- Caleb Douglas (WR, MIA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- De'Von Achane (RB, MIA) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Josh Oliver (TE, MIN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Justin Jefferson (WR, MIN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Nick Samac (C, MIN) — Injured Reserve [high] — ruled out
- Brett Thorson (P, MIN) — Out [high] — ruled out
- Charles Demmings (CB, MIN) — Out [high] — ruled out
- Kenneth Grant (DT, MIA) — Injured Reserve [high] — ruled out
- _...and 2 more (mostly non-skill positions); full list in the game file_

### WEATHER

roof is dome -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 62 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Malik Willis | MIA | attempts | 26.8 | 27.0 | 22.0 | 31.0 | 16.0 | 38.0 | 28.5 | 28.0 | 26.8 | 27.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Ollie Gordon II | MIA | carries | 10.6 | 10.0 | 6.0 | 14.0 | 2.0 | 22.0 | 7.3 | 7.0 | 10.6 | 10.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Malik Willis | MIA | carries | 7.4 | 7.0 | 4.0 | 9.0 | 2.0 | 15.0 | 6.5 | 6.0 | 7.4 | 7.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jaylen Wright | MIA | carries | 6.7 | 6.0 | 3.0 | 10.0 | 0.0 | 17.0 | 11.4 | 10.0 | 6.7 | 6.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Malik Willis | MIA | completions | 16.0 | 16.0 | 13.0 | 19.0 | 8.0 | 24.0 | 16.0 | 16.0 | 16.0 | 16.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Malik Willis | MIA | passing_tds | 0.9 | 1.0 | 0.0 | 1.0 | 0.0 | 3.0 | 0.7 | 1.0 | 0.7 | 1.0 | 0.00 | 0.98 | 3 | PRICED |
| Malik Willis | MIA | passing_yards | 173.1 | 168.0 | 127.0 | 214.0 | 74.0 | 289.0 | 174.0 | 166.0 | 174.0 | 169.0 | 0.00 | 0.98 | 8 | PRICED |
| Malik Washington | MIA | receiving_yards | 50.1 | 43.0 | 21.0 | 72.0 | 0.0 | 124.0 | 44.8 | 38.0 | 44.8 | 38.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 62 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 62 of 96 listed player/stat groups simulated and exposed, 34 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT04MIAMIN-MINAJONES33-15` | Aaron Jones Sr. | 15.0 | 0.70 | 0.71 | 0.14 | -0.555 |
| `KXNFLRSHATT-26OCT04MIAMIN-MIAMWILLIS2-4` | Malik Willis | 4.0 | 0.82 | 0.86 | 0.27 | -0.550 |
| `KXNFLREC-26OCT04MIAMIN-MINTHOCKENSON87-3` | T.J. Hockenson | 3.0 | 0.80 | 0.81 | 0.27 | -0.523 |
| `KXNFLRSHATT-26OCT04MIAMIN-MINKMURRAY1-2` | Kyler Murray | 2.0 | 0.95 | 0.97 | 0.44 | -0.507 |
| `KXNFLREC-26OCT04MIAMIN-MINJADDISON3-3` | Jordan Addison | 3.0 | 0.81 | 0.82 | 0.31 | -0.498 |
| `KXNFLREC-26OCT04MIAMIN-MIAMWASHINGTON6-3` | Malik Washington | 3.0 | 0.79 | 0.79 | 0.29 | -0.497 |

_Ranked 372 tradable markets; 5 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Caleb Douglas (WR, MIA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. De'Von Achane (RB, MIA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLFG-26OCT04MIAMIN-MIN3 moved -0.230 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.555 on KXNFLRSHATT-26OCT04MIAMIN-MINAJONES33-15 (Aaron Jones Sr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.550 on KXNFLRSHATT-26OCT04MIAMIN-MIAMWILLIS2-4 (Malik Willis). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLRSHATT-26OCT04MIAMIN-MINKMURRAY1-2 sits at a market price of 0.95 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_MIA_MIN.md`_


---

## DEN @ SF — `2026_04_DEN_SF`

- kickoff: 2026-10-04T20:25:00+00:00 (1438 minutes away) · state **PREGAME**
- venue: Levi's Stadium · roof outdoors · surface grass
- markets: 734 listed across 16 families — 377 supported, 301 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.67 | -2.36 |
| total | 48.62 | 47.96 |
| score | SF 25.6 – DEN 23.0 | SF 25.2 – DEN 22.8 |
| win prob SF | 57.5% | 57.5% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -1.67 / total 24.15 · **2H** spread -0.66 / total 24.39 · **1Q** spread -0.69 / total 8.71 · **2Q** spread -1.00 / total 14.43 · **3Q** spread -0.70 / total 9.37 · **4Q** spread -0.17 / total 14.25

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -2.67 · total 48.62
- move `KXNFLTOTAL-26OCT04DENSF-29` +0.155
- move `KXNFLTOTAL-26OCT04DENSF-48` +0.145
- move `KXNFLTOTAL-26OCT04DENSF-32` +0.135
- move `KXNFLTOTAL-26OCT04DENSF-35` +0.120

**Game environment** (simulation, mean and middle 50%) — home margin 2.5 (-5.0–10.0) · total 49.8 (41.0–58.0) · P(one score) 52.8% · P(17+ blowout) 18.1% · P(total 10+ over centre) 23.4%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| SF | 62.8 (57.0–68.0) | 34.1 (29.0–39.0) | 23.0 (18.0–28.0) | 38.9 (33.0–44.0) | 0.620 (0.553–0.689) | 0.531 / 0.710 |
| DEN | 62.6 (57.0–68.0) | 35.9 (31.0–41.0) | 22.8 (18.0–27.0) | 39.2 (34.0–44.0) | 0.626 (0.560–0.693) | 0.527 / 0.699 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| SF | 00-0033280 | RB | 5.2 (2.0–7.0) | 12.2 (7.0–16.0) | 15.7% | 53.1% | MEDIUM |
| SF | 00-0041052 | RB | 0.8 (0.0–1.0) | 5.4 (2.0–8.0) | 2.4% | 23.7% | HIGH |
| SF | 00-0035719 | WR | 4.5 (2.0–6.0) | 1.2 (0.0–1.0) | 13.7% | 5.3% | HIGH |
| SF | 00-0033288 | TE | 5.3 (2.0–7.0) | 0.0 (0.0–0.0) | 16.2% | 0.0% | HIGH |
| DEN | 00-0036158 | RB | 1.3 (0.0–2.0) | 12.6 (8.0–17.0) | 3.9% | 55.5% | MEDIUM |
| DEN | 00-0040730 | RB | 4.3 (2.0–6.0) | 5.3 (2.0–8.0) | 12.6% | 23.3% | HIGH |
| DEN | 00-0036613 | WR | 6.7 (4.0–9.0) | 0.4 (0.0–0.0) | 19.8% | 1.7% | HIGH |
| DEN | 00-0034348 | WR | 5.6 (3.0–8.0) | 0.0 (0.0–0.0) | 16.5% | 0.2% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 19 market(s), e.g. KXNFLPASSCOMP-26OCT04DENSF-SFBPURDY13-21, KXNFLPASSYDS-26OCT04DENSF-SFBPURDY13-275
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 67 market(s), e.g. KXNFLGAME-26OCT04DENSF-DEN, KXNFLPASSYDS-26OCT04DENSF-SFBPURDY13-300
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 24 market(s), e.g. KXNFLSPREAD-26OCT04DENSF-SF11, KXNFLSPREAD-26OCT04DENSF-SF10
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLTEAMTOTAL-26OCT04DENSF-SF22, KXNFLTEAMTOTAL-26OCT04DENSF-SF21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 190 market(s), e.g. KXNFL1QSPREAD-26OCT04DENSF-DEN8, KXNFL1QTOTAL-26OCT04DENSF-18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 62 market(s), e.g. KXNFL1HTOTAL-26OCT04DENSF-11, KXNFLPASSYDS-26OCT04DENSF-SFBPURDY13-150

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- Christian Kirk (WR, SF) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jonah Coleman (RB, DEN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Dondrea Tillman (LB, DEN) — Out [high] — ruled out
- James Thompson Jr. (DT, SF) — Out [single_source] — ruled out
- Mykel Williams (DE, SF) — Out [high] — ruled out
- Nick Bosa (DE, SF) — Out [high] — ruled out

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Mike Evans (WR, SF) — Questionable [high]
- Dre Greenlaw (LB, SF) — Questionable [high]
- Jaden Dugger (LB, SF) — Questionable [high]
- Keion White (DE, SF) — Questionable [high]

### WEATHER

- Partly Sunny · 87°F · wind 2 mph NW · precip 1%
- forecast vintage 2026-10-03T20:10:32+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 89, 'wind': '1 mph', 'precipitation_probability': 0})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 61 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bo Nix | DEN | attempts | 34.5 | 35.0 | 29.0 | 40.0 | 20.0 | 48.0 | 35.0 | 35.0 | 34.5 | 35.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| J.K. Dobbins | DEN | carries | 12.6 | 12.0 | 8.0 | 17.0 | 3.0 | 24.0 | 13.9 | 14.0 | 12.6 | 12.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bo Nix | DEN | carries | 5.0 | 4.0 | 2.0 | 7.0 | 1.0 | 13.0 | 4.6 | 4.0 | 5.0 | 4.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bo Nix | DEN | completions | 21.6 | 22.0 | 18.0 | 25.0 | 12.0 | 31.0 | 22.6 | 22.0 | 21.6 | 22.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bo Nix | DEN | passing_tds | 1.6 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.5 | 1.0 | 1.5 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Bo Nix | DEN | passing_yards | 221.8 | 218.0 | 171.0 | 269.0 | 104.0 | 355.0 | 228.4 | 222.0 | 228.4 | 224.0 | 0.00 | 0.98 | 9 | PRICED |
| Jaylen Waddle | DEN | receiving_yards | 52.1 | 43.0 | 19.0 | 75.0 | 0.0 | 134.0 | 62.1 | 55.0 | 62.1 | 52.0 | 0.00 | 0.97 | 12 | PRICED |
| Courtland Sutton | DEN | receiving_yards | 41.7 | 33.0 | 12.0 | 61.0 | 0.0 | 117.0 | 45.9 | 37.0 | 45.9 | 36.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 61 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 61 of 99 listed player/stat groups simulated and exposed, 38 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT04DENSF-SFBPURDY13-2` | Brock Purdy | 2.0 | 0.90 | 0.92 | 0.39 | -0.505 |
| `KXNFLRSHATT-26OCT04DENSF-DENBNIX10-2` | Bo Nix | 2.0 | 0.92 | 0.94 | 0.46 | -0.460 |
| `KXNFLREC-26OCT04DENSF-DENRHARVEY12-2` | RJ Harvey | 2.0 | 0.84 | 0.86 | 0.39 | -0.454 |
| `KXNFLREC-26OCT04DENSF-SFGKITTLE85-4` | George Kittle | 4.0 | 0.71 | 0.73 | 0.27 | -0.450 |
| `KXNFLREC-26OCT04DENSF-SFCMCCAFFREY23-4` | Christian McCaffrey | 4.0 | 0.70 | 0.71 | 0.26 | -0.440 |
| `KXNFLREC-26OCT04DENSF-DENRHARVEY12-3` | RJ Harvey | 3.0 | 0.66 | 0.67 | 0.23 | -0.433 |

_Ranked 373 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jonah Coleman (RB, DEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Christian Kirk (WR, SF) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Mike Evans (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
5. KXNFLTOTAL-26OCT04DENSF-29 moved +0.155 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
6. The model disagrees by -0.505 on KXNFLRSHATT-26OCT04DENSF-SFBPURDY13-2 (Brock Purdy). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. The model disagrees by -0.460 on KXNFLRSHATT-26OCT04DENSF-DENBNIX10-2 (Bo Nix). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
8. KXNFLRSHATT-26OCT04DENSF-SFBPURDY13-2 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_DEN_SF.md`_


---

## KC @ LV — `2026_04_KC_LV`

- kickoff: 2026-10-04T20:25:00+00:00 (1438 minutes away) · state **PREGAME**
- venue: Allegiant Stadium · roof dome · surface grass
- markets: 765 listed across 16 families — 407 supported, 302 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 4.38 | 4.47 |
| total | 47.90 | 48.09 |
| score | LV 21.8 – KC 26.1 | LV 21.8 – KC 26.3 |
| win prob LV | 33.5% | 34.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 3.10 / total 24.39 · **2H** spread 2.57 / total 24.08 · **1Q** spread 1.44 / total 8.62 · **2Q** spread 1.50 / total 14.62 · **3Q** spread 1.46 / total 9.15 · **4Q** spread 0.46 / total 14.00

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 4.38 · total 47.90
- move `KXNFLTOTAL-26OCT04KCLV-29` +0.195
- move `KXNFLTOTAL-26OCT04KCLV-32` +0.170
- move `KXNFL1HTEAMTOTAL-26OCT04KCLV-LV14` -0.165
- move `KXNFL2HTOTAL-26OCT04KCLV-4` +0.135

**Game environment** (simulation, mean and middle 50%) — home margin -4.3 (-12.0–3.0) · total 48.6 (40.0–56.0) · P(one score) 52.0% · P(17+ blowout) 19.5% · P(total 10+ over centre) 23.2%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| LV | 61.5 (56.0–67.0) | 34.6 (30.0–39.0) | 22.9 (18.0–27.0) | 38.0 (33.0–43.0) | 0.619 (0.555–0.686) | 0.512 / 0.683 |
| KC | 63.3 (58.0–69.0) | 32.8 (28.0–38.0) | 23.9 (19.0–28.0) | 38.4 (33.0–44.0) | 0.608 (0.540–0.675) | 0.528 / 0.702 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| LV | 00-0040122 | RB | 5.1 (2.0–7.0) | 16.2 (11.0–21.0) | 15.3% | 70.8% | MEDIUM |
| LV | 00-0039338 | TE | 8.4 (5.0–11.0) | 0.0 (0.0–0.0) | 25.4% | 0.1% | MEDIUM |
| LV | 00-0038563 | WR | 5.3 (3.0–7.0) | 0.2 (0.0–0.0) | 15.9% | 0.7% | HIGH |
| LV | 00-0040878 | RB | 0.6 (0.0–1.0) | 4.2 (1.0–6.0) | 1.8% | 18.5% | HIGH |
| KC | 00-0038134 | RB | 3.9 (2.0–6.0) | 15.1 (10.0–20.0) | 12.7% | 63.4% | MEDIUM |
| KC | 00-0039067 | WR | 7.4 (4.0–10.0) | 0.1 (0.0–0.0) | 24.0% | 0.6% | MEDIUM |
| KC | 00-0041013 | RB | 1.2 (0.0–2.0) | 4.5 (1.0–7.0) | 3.8% | 19.0% | HIGH |
| KC | 00-0030506 | TE | 5.3 (3.0–7.0) | 0.0 (0.0–0.0) | 17.2% | 0.0% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 8 market(s), e.g. KXNFLPASSYDS-26OCT04KCLV-KCPMAHOMES15-300, KXNFLRSHATT-26OCT04KCLV-LVMWASHINGTON4-8
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 67 market(s), e.g. KXNFL4Q-26OCT04KCLV-LV, KXNFLFIRSTTD-26OCT04KCLV-KCKWALKER9
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26OCT04KCLV-LV8, KXNFLSPREAD-26OCT04KCLV-LV7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLGAME-26OCT04KCLV-KC, KXNFLSPREAD-26OCT04KCLV-KC3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 206 market(s), e.g. KXNFL1HFT-26OCT04KCLV-TIELV, KXNFL1HFT-26OCT04KCLV-TIEKC
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 59 market(s), e.g. KXNFLPASSCOMP-26OCT04KCLV-KCPMAHOMES15-16, KXNFLPASSYDS-26OCT04KCLV-KCPMAHOMES15-150

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Dont'e Thornton Jr. (WR, LV) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Jack Bech (WR, LV) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jackson Powers-Johnson (G, LV) — Out [high] — ruled out
- Josh Simmons (OT, KC) — Out [high] — ruled out

### WEATHER

roof is dome -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 64 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Patrick Mahomes | KC | attempts | 31.5 | 32.0 | 27.0 | 37.0 | 18.0 | 45.0 | 32.2 | 32.0 | 31.5 | 32.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kenneth Walker III | KC | carries | 15.1 | 15.0 | 10.0 | 20.0 | 4.0 | 28.0 | 18.4 | 18.0 | 15.1 | 15.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | completions | 21.0 | 21.0 | 17.0 | 25.0 | 11.0 | 31.0 | 21.0 | 21.0 | 21.0 | 21.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | passing_tds | 1.8 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 1.8 | 2.0 | 1.8 | 2.0 | 0.00 | 0.97 | 4 | PRICED |
| Patrick Mahomes | KC | passing_yards | 220.7 | 217.0 | 169.0 | 268.0 | 103.0 | 354.0 | 243.1 | 237.0 | 243.1 | 239.0 | 0.00 | 0.97 | 9 | PRICED |
| Rashee Rice | KC | receiving_yards | 58.4 | 51.0 | 26.0 | 82.0 | 0.0 | 139.0 | 63.0 | 56.0 | 63.0 | 55.0 | 0.00 | 0.97 | 12 | PRICED |
| Travis Kelce | KC | receiving_yards | 42.5 | 34.0 | 14.0 | 61.0 | 0.0 | 113.0 | 53.4 | 47.0 | 53.4 | 43.0 | 0.00 | 0.97 | 10 | PRICED |
| Xavier Worthy | KC | receiving_yards | 34.6 | 26.0 | 9.0 | 51.0 | 0.0 | 100.0 | 39.6 | 32.0 | 39.6 | 30.0 | 0.00 | 0.98 | 9 | PRICED |

_8 of 64 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 64 of 100 listed player/stat groups simulated and exposed, 36 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT04KCLV-LVBBOWERS89-5` | Brock Bowers | 5.0 | 0.81 | 0.82 | 0.19 | -0.617 |
| `KXNFLREC-26OCT04KCLV-LVBBOWERS89-6` | Brock Bowers | 6.0 | 0.69 | 0.70 | 0.10 | -0.588 |
| `KXNFLRSHATT-26OCT04KCLV-KCKWALKER9-16` | Kenneth Walker III | 16.0 | 0.70 | 0.71 | 0.12 | -0.579 |
| `KXNFLREC-26OCT04KCLV-LVBBOWERS89-4` | Brock Bowers | 4.0 | 0.91 | 0.92 | 0.34 | -0.568 |
| `KXNFLREC-26OCT04KCLV-LVBBOWERS89-7` | Brock Bowers | 7.0 | 0.55 | 0.56 | 0.05 | -0.500 |
| `KXNFLRSHYDS-26OCT04KCLV-KCKWALKER9-60` | Kenneth Walker III | 60.0 | 0.77 | 0.77 | 0.28 | -0.482 |

_Ranked 402 tradable markets; 5 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Dont'e Thornton Jr. (WR, LV) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jack Bech (WR, LV) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLTOTAL-26OCT04KCLV-29 moved +0.195 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.617 on KXNFLREC-26OCT04KCLV-LVBBOWERS89-5 (Brock Bowers). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.588 on KXNFLREC-26OCT04KCLV-LVBBOWERS89-6 (Brock Bowers). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26OCT04KCLV-LVBBOWERS89-4 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_KC_LV.md`_


---

## LAC @ SEA — `2026_04_LAC_SEA`

- kickoff: 2026-10-04T20:25:00+00:00 (1438 minutes away) · state **PREGAME**
- venue: Lumen Field · roof outdoors · surface fieldturf
- markets: 719 listed across 16 families — 382 supported, 281 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -7.14 | -7.04 |
| total | 43.38 | 42.86 |
| score | SEA 25.3 – LAC 18.1 | SEA 24.9 – LAC 17.9 |
| win prob SEA | 75.5% | 74.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -4.10 / total 21.75 · **2H** spread -3.70 / total 21.00 · **1Q** spread -2.29 / total 7.87 · **2Q** spread -2.91 / total 13.11 · **3Q** spread -2.40 / total 8.00 · **4Q** spread -1.50 / total 11.68

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -7.14 · total 43.38
- move `KXNFL2HTOTAL-26OCT04LACSEA-4` +0.120
- move `KXNFL1HTEAMTOTAL-26OCT04LACSEA-LAC10` -0.110
- move `KXNFLTOTAL-26OCT04LACSEA-29` +0.110

**Game environment** (simulation, mean and middle 50%) — home margin 7.7 (1.0–15.0) · total 44.6 (36.0–52.0) · P(one score) 46.4% · P(17+ blowout) 22.9% · P(total 10+ over centre) 23.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| SEA | 62.8 (57.0–68.0) | 31.1 (26.0–36.0) | 27.4 (22.0–32.0) | 34.3 (29.0–39.0) | 0.547 (0.479–0.616) | 0.481 / 0.657 |
| LAC | 60.9 (55.0–67.0) | 31.7 (27.0–36.0) | 22.4 (18.0–27.0) | 38.1 (33.0–43.0) | 0.626 (0.561–0.693) | 0.506 / 0.678 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| SEA | 00-0038797 | RB | 1.0 (0.0–1.0) | 16.7 (11.0–22.0) | 3.4% | 61.0% | MEDIUM |
| SEA | 00-0038543 | WR | 9.7 (6.0–13.0) | 0.1 (0.0–0.0) | 32.4% | 0.5% | MEDIUM |
| SEA | 00-0039299 | RB | 1.7 (0.0–3.0) | 7.2 (3.0–10.0) | 5.8% | 26.5% | HIGH |
| SEA | 00-0039793 | TE | 4.0 (2.0–6.0) | 0.3 (0.0–0.0) | 13.2% | 1.2% | HIGH |
| LAC | 00-0040666 | RB | 2.3 (0.0–3.0) | 11.6 (7.0–16.0) | 7.4% | 52.0% | MEDIUM |
| LAC | 00-0038454 | RB | 2.1 (0.0–3.0) | 4.6 (1.0–7.0) | 6.8% | 20.8% | HIGH |
| LAC | 00-0038544 | WR | 6.4 (3.0–9.0) | 0.2 (0.0–0.0) | 20.8% | 0.7% | HIGH |
| LAC | 00-0036355 | QB | 0.1 (0.0–0.0) | 5.1 (3.0–7.0) | 0.4% | 5.8% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 12 market(s), e.g. KXNFLPASSATT-26OCT04LACSEA-LACJHERBERT10-35, KXNFLPASSCOMP-26OCT04LACSEA-LACJHERBERT10-24
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 43 market(s), e.g. KXNFLFIRSTTD-26OCT04LACSEA-SEAJSMITHNJIGBA11, KXNFLPASSCOMP-26OCT04LACSEA-SEASDARNOLD14-27
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 20 market(s), e.g. KXNFLGAME-26OCT04LACSEA-LAC, KXNFLSPREAD-26OCT04LACSEA-SEA24
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLSPREAD-26OCT04LACSEA-SEA5, KXNFLSPREAD-26OCT04LACSEA-SEA4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 222 market(s), e.g. KXNFL1H-26OCT04LACSEA-TIE, KXNFL1HFT-26OCT04LACSEA-TIESEA
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 52 market(s), e.g. KXNFLPASSCOMP-26OCT04LACSEA-LACJHERBERT10-14, KXNFLPASSYDS-26OCT04LACSEA-SEASDARNOLD14-150

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Brenen Thompson (WR, LAC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Charlie Kolar (TE, LAC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jadarian Price (RB, SEA) — Injured Reserve [high] · **CHANGED from Out** — ruled out -- role redistributes to the depth chart behind him
- Zach Charbonnet (RB, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Anthony Bradford (G, SEA) — Injured Reserve [high] — ruled out
- Kayode Awosika (G, LAC) — Out [high] — ruled out
- Trey Pipkins III (OT, LAC) — Injured Reserve [single_source] — ruled out
- Dalvin Tomlinson (DT, LAC) — Out [high] — ruled out

**Questionable / Doubtful (7)** — resolves at the inactive release, T−90m

- Trey Lance (QB, LAC) — Questionable [high]
- Ladd McConkey (WR, LAC) — Questionable [high]
- Chazz Surratt (LB, SEA) — Questionable [high]
- Derwin James Jr. (S, LAC) — Questionable [single_source]
- Donte Jackson (CB, LAC) — Questionable [high]
- Elijah Molden (CB, LAC) — Questionable [high]
- Ty Okada (S, SEA) — Questionable [high]

### WEATHER

- Sunny · 66°F · wind 3 mph NW · precip 0%
- forecast vintage 2026-10-03T20:10:31+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 67, 'wind': '3 mph', 'precipitation_probability': 0})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 59 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Justin Herbert | LAC | attempts | 30.5 | 31.0 | 26.0 | 35.0 | 18.0 | 43.0 | 30.2 | 30.0 | 30.5 | 31.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Omarion Hampton | LAC | carries | 11.6 | 11.0 | 7.0 | 16.0 | 2.0 | 23.0 | 13.5 | 13.0 | 11.6 | 11.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Justin Herbert | LAC | carries | 5.1 | 5.0 | 3.0 | 7.0 | 1.0 | 11.0 | 4.7 | 4.0 | 5.1 | 5.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Justin Herbert | LAC | completions | 18.5 | 18.0 | 15.0 | 22.0 | 10.0 | 27.0 | 18.9 | 19.0 | 18.5 | 18.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Justin Herbert | LAC | passing_tds | 1.1 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.1 | 1.0 | 1.1 | 1.0 | 0.00 | 0.98 | 3 | PRICED |
| Justin Herbert | LAC | passing_yards | 192.4 | 188.0 | 144.0 | 235.0 | 87.0 | 314.0 | 205.2 | 198.0 | 205.2 | 200.0 | 0.00 | 0.98 | 8 | PRICED |
| Quentin Johnston | LAC | receiving_yards | 45.0 | 36.0 | 16.0 | 65.0 | 0.0 | 121.0 | 41.2 | 31.0 | 41.2 | 33.0 | 0.00 | 0.97 | 9 | PRICED |
| Ladd McConkey | LAC | receiving_yards | 37.4 | 27.0 | 0.0 | 58.0 | 0.0 | 116.0 | 49.3 | 42.0 | 49.3 | 36.0 | 0.00 | 0.78 | 11 | PRICED |

_8 of 59 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 59 of 88 listed player/stat groups simulated and exposed, 29 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26OCT04LACSEA-SEAJPRICE8-20` | Jadarian Price | 20.0 | 0.79 | 0.83 | 0.01 | -0.781 |
| `KXNFLRSHYDS-26OCT04LACSEA-SEAJPRICE8-25` | Jadarian Price | 25.0 | 0.70 | 0.73 | 0.01 | -0.687 |
| `KXNFLRSHYDS-26OCT04LACSEA-SEAJPRICE8-30` | Jadarian Price | 30.0 | 0.64 | 0.69 | 0.01 | -0.628 |
| `KXNFLRSHYDS-26OCT04LACSEA-SEAJPRICE8-40` | Jadarian Price | 40.0 | 0.49 | 0.50 | 0.00 | -0.485 |
| `KXNFLRSHATT-26OCT04LACSEA-LACJHERBERT10-2` | Justin Herbert | 2.0 | 0.94 | 0.97 | 0.47 | -0.461 |
| `KXNFLRSHATT-26OCT04LACSEA-LACOHAMPTON8-11` | Omarion Hampton | 11.0 | 0.73 | 0.74 | 0.29 | -0.442 |

_Ranked 367 tradable markets; 15 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Brenen Thompson (WR, LAC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Charlie Kolar (TE, LAC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Ladd McConkey (WR), Trey Lance (QB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
5. KXNFLTD-26OCT04LACSEA-SEAGHOLANI36-1 moved +0.190 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
6. The model disagrees by -0.781 on KXNFLRSHYDS-26OCT04LACSEA-SEAJPRICE8-20 (Jadarian Price). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. The model disagrees by -0.687 on KXNFLRSHYDS-26OCT04LACSEA-SEAJPRICE8-25 (Jadarian Price). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
8. KXNFLRSHATT-26OCT04LACSEA-LACJHERBERT10-2 sits at a market price of 0.94 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_LAC_SEA.md`_


---

## DET @ CAR — `2026_04_DET_CAR`

- kickoff: 2026-10-05T00:20:00+00:00 (1673 minutes away) · state **PREGAME**
- venue: Bank of America Stadium · roof outdoors · surface grass
- markets: 700 listed across 16 families — 377 supported, 267 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.88 | 4.08 |
| total | 51.38 | 51.02 |
| score | CAR 23.8 – DET 27.6 | CAR 23.5 – DET 27.5 |
| win prob CAR | 35.5% | 35.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.81 / total 25.14 · **2H** spread 1.97 / total 25.52 · **1Q** spread 1.28 / total 9.18 · **2Q** spread 1.39 / total 15.26 · **3Q** spread 1.04 / total 9.92 · **4Q** spread 0.50 / total 14.61

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 3.88 · total 51.38
- move `KXNFL1HTEAMTOTAL-26OCT04DETCAR-DET10` +0.200
- move `KXNFLTOTAL-26OCT04DETCAR-32` +0.165
- move `KXNFL1HTOTAL-26OCT04DETCAR-8` +0.140
- move `KXNFLTOTAL-26OCT04DETCAR-59` +0.130

**Game environment** (simulation, mean and middle 50%) — home margin -3.4 (-11.0–4.0) · total 52.6 (43.0–61.0) · P(one score) 53.5% · P(17+ blowout) 18.7% · P(total 10+ over centre) 23.4%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CAR | 64.1 (58.0–70.0) | 35.6 (30.0–40.0) | 23.3 (18.0–28.0) | 40.2 (35.0–45.0) | 0.628 (0.562–0.695) | 0.528 / 0.691 |
| DET | 64.4 (59.0–70.0) | 34.2 (29.0–39.0) | 26.2 (21.0–31.0) | 37.3 (32.0–42.0) | 0.580 (0.513–0.648) | 0.502 / 0.671 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CAR | 00-0036555 | RB | 3.2 (1.0–5.0) | 16.1 (11.0–21.0) | 9.7% | 69.1% | MEDIUM |
| CAR | 00-0040124 | WR | 7.3 (4.0–10.0) | 0.0 (0.0–0.0) | 22.3% | 0.1% | HIGH |
| CAR | 00-0036265 | RB | 0.6 (0.0–1.0) | 4.5 (1.0–7.0) | 1.9% | 19.2% | HIGH |
| CAR | 00-0031610 | TE | 4.3 (2.0–6.0) | 0.1 (0.0–0.0) | 13.0% | 0.2% | HIGH |
| DET | 00-0039139 | RB | 5.6 (3.0–8.0) | 20.4 (15.0–26.0) | 16.9% | 77.9% | LOW |
| DET | 00-0036963 | WR | 9.4 (6.0–12.0) | 0.0 (0.0–0.0) | 28.6% | 0.1% | MEDIUM |
| DET | 00-0039065 | TE | 5.5 (3.0–8.0) | 0.0 (0.0–0.0) | 16.7% | 0.0% | HIGH |
| DET | 00-0039364 | RB | 1.1 (0.0–2.0) | 4.4 (1.0–6.0) | 3.3% | 16.9% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 1 market(s), e.g. KXNFLPASSATT-26OCT04DETCAR-DETJGOFF16-40
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 67 market(s), e.g. KXNFL2H-26OCT04DETCAR-CAR, KXNFLPASSYDS-26OCT04DETCAR-DETJGOFF16-275
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT04DETCAR-DET14, KXNFLSPREAD-26OCT04DETCAR-DET11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLGAME-26OCT04DETCAR-DET, KXNFLSPREAD-26OCT04DETCAR-DET2
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 178 market(s), e.g. KXNFL1HFT-26OCT04DETCAR-CARDET, KXNFL1HSPREAD-26OCT04DETCAR-CAR11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 56 market(s), e.g. KXNFL4QTOTAL-26OCT04DETCAR-4, KXNFLFG-26OCT04DETCAR-DET2

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Xavier Legette (WR, CAR) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Ben Bartch (G, DET) — Out [high] — ruled out
- Cade Mays (C, DET) — Injured Reserve [high] — ruled out
- Damien Lewis (G, CAR) — Out [high] — ruled out
- Avonte Maddox (CB, DET) — Injured Reserve [high] — ruled out
- Brian Branch (S, DET) — Out [high] — ruled out
- Jaycee Horn (CB, CAR) — Injured Reserve [high] — ruled out
- Mike Jackson (CB, CAR) — Injured Reserve [high] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Jalen Coker (WR, CAR) — Questionable [high]
- Monroe Freeling (OT, CAR) — Questionable [single_source]
- Cam Jackson (DT, CAR) — Questionable [high]
- D.J. Reed (CB, DET) — Questionable [high]
- Lee Hunter (DT, CAR) — Questionable [high]

### WEATHER

- Chance Light Rain · 67°F · wind 2 mph NW · precip 29%
- forecast vintage 2026-10-03T20:10:34+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 69, 'wind': '1 mph', 'precipitation_probability': 59})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 52 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bryce Young | CAR | attempts | 34.2 | 34.0 | 29.0 | 40.0 | 21.0 | 48.0 | 35.9 | 35.0 | 34.2 | 34.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chuba Hubbard | CAR | carries | 16.1 | 16.0 | 11.0 | 21.0 | 5.0 | 29.0 | 17.1 | 17.0 | 16.1 | 16.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | carries | 3.0 | 3.0 | 1.0 | 4.0 | 0.0 | 7.0 | 3.0 | 3.0 | 3.0 | 3.0 | -- | 0.97 | 2 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | completions | 21.0 | 21.0 | 17.0 | 25.0 | 12.0 | 30.0 | 21.3 | 21.0 | 21.0 | 21.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | passing_tds | 1.6 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.7 | 2.0 | 1.7 | 2.0 | 0.00 | 0.97 | 4 | PRICED |
| Bryce Young | CAR | passing_yards | 231.0 | 227.0 | 178.0 | 280.0 | 110.0 | 364.0 | 245.6 | 240.0 | 245.6 | 242.0 | 0.00 | 0.97 | 10 | PRICED |
| Tetairoa McMillan | CAR | receiving_yards | 59.9 | 51.0 | 24.0 | 85.0 | 0.0 | 150.0 | 76.4 | 68.0 | 76.2 | 65.0 | 0.00 | 0.98 | 16 | PRICED |
| Darren Waller | CAR | receiving_yards | 31.3 | 23.0 | 7.0 | 46.0 | 0.0 | 93.0 | 34.9 | 28.0 | 34.9 | 26.0 | 0.00 | 0.97 | 7 | PRICED |

_8 of 52 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 52 of 81 listed player/stat groups simulated and exposed, 29 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT04DETCAR-DETJGIBBS0-17` | Jahmyr Gibbs | 17.0 | 0.71 | 0.74 | 0.11 | -0.601 |
| `KXNFLRSHATT-26OCT04DETCAR-CARCHUBBARD30-14` | Chuba Hubbard | 14.0 | 0.72 | 0.74 | 0.12 | -0.596 |
| `KXNFLRSHYDS-26OCT04DETCAR-CARCHUBBARD30-40` | Chuba Hubbard | 40.0 | 0.80 | 0.80 | 0.26 | -0.538 |
| `KXNFLRSHYDS-26OCT04DETCAR-CARCHUBBARD30-50` | Chuba Hubbard | 50.0 | 0.69 | 0.70 | 0.19 | -0.504 |
| `KXNFLREC-26OCT04DETCAR-DETJGIBBS0-4` | Jahmyr Gibbs | 4.0 | 0.69 | 0.70 | 0.20 | -0.481 |
| `KXNFLRSHYDS-26OCT04DETCAR-DETJGIBBS0-60` | Jahmyr Gibbs | 60.0 | 0.81 | 0.83 | 0.33 | -0.480 |

_Ranked 368 tradable markets; 9 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Xavier Legette (WR, CAR) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 1 skill players are Questionable (Jalen Coker (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
4. KXNFL1HTEAMTOTAL-26OCT04DETCAR-DET10 moved +0.200 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.601 on KXNFLRSHATT-26OCT04DETCAR-DETJGIBBS0-17 (Jahmyr Gibbs). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.596 on KXNFLRSHATT-26OCT04DETCAR-CARCHUBBARD30-14 (Chuba Hubbard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT04DETCAR-DETSLAPORTA87-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_DET_CAR.md`_


---

## ATL @ NO — `2026_04_ATL_NO`

- kickoff: 2026-10-06T00:15:00+00:00 (3108 minutes away) · state **PREGAME**
- venue: Caesars Superdome · roof dome · surface sportturf
- markets: 728 listed across 16 families — 388 supported, 284 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -1.67 | -1.36 |
| total | 48.29 | 47.94 |
| score | NO 25.0 – ATL 23.3 | NO 24.7 – ATL 23.3 |
| win prob NO | 54.5% | 54.5% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -0.93 / total 24.08 · **2H** spread -0.25 / total 24.10 · **1Q** spread -0.52 / total 8.59 · **2Q** spread -0.61 / total 14.58 · **3Q** spread -0.30 / total 9.11 · **4Q** spread 0.23 / total 14.06

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -1.67 · total 48.29
- move `KXNFL2HTOTAL-26OCT05ATLNO-4` +0.115
- move `KXNFL1HTEAMTOTAL-26OCT05ATLNO-NO10` +0.100

**Game environment** (simulation, mean and middle 50%) — home margin 1.6 (-6.0–9.0) · total 49.8 (41.0–58.0) · P(one score) 54.2% · P(17+ blowout) 17.4% · P(total 10+ over centre) 23.9%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NO | 66.4 (61.0–72.0) | 35.6 (30.0–41.0) | 25.4 (20.0–30.0) | 40.2 (34.0–46.0) | 0.606 (0.538–0.674) | 0.510 / 0.689 |
| ATL | 63.3 (58.0–69.0) | 31.1 (26.0–36.0) | 28.0 (23.0–33.0) | 34.6 (29.0–40.0) | 0.547 (0.481–0.614) | 0.451 / 0.624 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NO | 00-0033906 | RB | 3.3 (1.0–5.0) | 13.0 (8.0–18.0) | 9.6% | 51.2% | MEDIUM |
| NO | 00-0037239 | WR | 10.0 (6.0–13.0) | 0.1 (0.0–0.0) | 29.6% | 0.3% | MEDIUM |
| NO | 00-0038551 | RB | 1.4 (0.0–2.0) | 7.3 (3.0–10.0) | 4.1% | 28.6% | HIGH |
| NO | 00-0039424 | WR | 5.6 (3.0–8.0) | 0.2 (0.0–0.0) | 16.4% | 0.6% | HIGH |
| ATL | 00-0038542 | RB | 5.1 (2.0–7.0) | 19.3 (14.0–25.0) | 17.3% | 68.9% | MEDIUM |
| ATL | 00-0037746 | RB | 1.0 (0.0–1.0) | 7.5 (3.0–11.0) | 3.2% | 26.7% | HIGH |
| ATL | 00-0037238 | WR | 7.9 (5.0–11.0) | 0.3 (0.0–0.0) | 26.9% | 1.0% | MEDIUM |
| ATL | 00-0036970 | TE | 4.2 (2.0–6.0) | 0.0 (0.0–0.0) | 14.1% | 0.0% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 4 market(s), e.g. KXNFLRECYDS-26OCT05ATLNO-ATLOZACCHEAUS14-25, KXNFLRECYDS-26OCT05ATLNO-ATLOZACCHEAUS14-15
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 44 market(s), e.g. KXNFLFIRSTTD-26OCT05ATLNO-ATLBROBINSON7, KXNFLGAME-26OCT05ATLNO-ATL
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26OCT05ATLNO-NO8, KXNFLSPREAD-26OCT05ATLNO-NO18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLTEAMTOTAL-26OCT05ATLNO-NO22, KXNFLTEAMTOTAL-26OCT05ATLNO-NO21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 174 market(s), e.g. KXNFL1HFT-26OCT05ATLNO-NOATL, KXNFL1HFT-26OCT05ATLNO-ATLNO
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 71 market(s), e.g. KXNFL1HTOTAL-26OCT05ATLNO-11, KXNFL2HTOTAL-26OCT05ATLNO-11

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- Jordyn Tyson (WR, NO) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Travis Etienne Jr. (RB, NO) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Kelvin Banks Jr. (OT, NO) — Injured Reserve [single_source] — ruled out
- Anfernee Jennings (LB, NO) — Out [high] · **CHANGED from Questionable** — ruled out
- Carl Granderson (DE, NO) — Out [high] · **CHANGED from Questionable** — ruled out
- Kaden Elliss (LB, NO) — Out [high] · **CHANGED from Questionable** — ruled out

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Noah Fant (TE, NO) — Questionable [high]
- Divine Deablo (LB, ATL) — Questionable [high]
- Pete Werner (LB, NO) — Questionable [high]
- Samson Ebukam (DE, ATL) — Questionable [high]
- Yasir Abdullah (LB, ATL) — Questionable [high]

### WEATHER

roof is dome -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261003T200006Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 56 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Michael Penix Jr. | ATL | attempts | 29.8 | 30.0 | 25.0 | 35.0 | 17.0 | 43.0 | 31.0 | 31.0 | 29.8 | 30.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bijan Robinson | ATL | carries | 19.3 | 19.0 | 14.0 | 25.0 | 6.0 | 33.0 | 19.8 | 19.0 | 19.3 | 19.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | completions | 18.9 | 19.0 | 15.0 | 23.0 | 10.0 | 28.0 | 20.5 | 20.0 | 18.9 | 19.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | passing_tds | 1.3 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.5 | 1.0 | 1.5 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Michael Penix Jr. | ATL | passing_yards | 198.9 | 195.0 | 149.0 | 244.0 | 88.0 | 325.0 | 229.8 | 224.0 | 229.8 | 225.0 | 0.00 | 0.98 | 9 | PRICED |
| Drake London | ATL | receiving_yards | 65.2 | 57.0 | 30.0 | 91.0 | 1.0 | 153.0 | 84.4 | 77.0 | 84.2 | 74.0 | 0.00 | 0.98 | 14 | PRICED |
| Bijan Robinson | ATL | receiving_yards | 30.1 | 24.0 | 10.0 | 43.0 | 0.0 | 84.0 | 43.7 | 38.0 | 43.7 | 34.0 | 0.00 | 0.97 | 9 | PRICED |
| Kyle Pitts Sr. | ATL | receiving_yards | 29.6 | 22.0 | 7.0 | 43.0 | 0.0 | 87.0 | 34.3 | 28.0 | 34.3 | 26.0 | 0.00 | 0.98 | 7 | PRICED |

_8 of 56 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 56 of 89 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26OCT05ATLNO-ATLBROBINSON7-17` | Bijan Robinson | 17.0 | 0.70 | 0.73 | 0.17 | -0.532 |
| `KXNFLREC-26OCT05ATLNO-NOCOLAVE12-6` | Chris Olave | 6.0 | 0.70 | 0.71 | 0.22 | -0.473 |
| `KXNFLREC-26OCT05ATLNO-ATLDLONDON5-5` | Drake London | 5.0 | 0.70 | 0.72 | 0.23 | -0.470 |
| `KXNFLREC-26OCT05ATLNO-ATLBROBINSON7-4` | Bijan Robinson | 4.0 | 0.67 | 0.68 | 0.21 | -0.460 |
| `KXNFLREC-26OCT05ATLNO-NODVELE14-3` | Devaughn Vele | 3.0 | 0.76 | 0.76 | 0.30 | -0.457 |
| `KXNFLREC-26OCT05ATLNO-ATLBROBINSON7-3` | Bijan Robinson | 3.0 | 0.81 | 0.83 | 0.36 | -0.454 |

_Ranked 384 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jordyn Tyson (WR, NO) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Travis Etienne Jr. (RB, NO) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Noah Fant (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRSHYDS-26OCT05ATLNO-NOKMILLER5-25 moved +0.155 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.532 on KXNFLRSHATT-26OCT05ATLNO-ATLBROBINSON7-17 (Bijan Robinson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.473 on KXNFLREC-26OCT05ATLNO-NOCOLAVE12-6 (Chris Olave). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26OCT05ATLNO-NODVELE14-2 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_04_ATL_NO.md`_


---

## HOW TO USE THIS PACKET

1. Handicap each game independently. The model's ranked disagreements are an input, not a shortlist.
2. For any thesis you form, check **BEST EXPRESSIONS** before choosing a contract — the largest disagreement is rarely the best payout for the risk.
3. Check **CORRELATION GROUPS** before sizing more than one position in a game.
4. Record every serious decision, including passes, via the recommendation ledger (`scripts/handicap/validate_recommendations.py`, then commit to the `handicap-data` branch).