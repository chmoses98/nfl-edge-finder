# NFL HANDICAP PACKET — 2026 Week 9

- run id: `20261107T154739Z`  ·  packet sha: `ae3099a76207a9c5b667`
- built at: 2026-11-07T15:47:39.190365+00:00  (all timestamps UTC)
- ledger: `20261107T150411Z.shadow-0.4.0.observations.jsonl.gz`  ·  model: `shadow-0.4.0`
- context captures: ['20261028T133921Z', '20261107T145630Z']
- team-profile basis: **current_season**
- **REAL-MONEY STATUS: NOT VALIDATED -- this packet recommends nothing and authorises nothing**
- **SIMULATION FRESHNESS: SIM_CURRENT** — run `20261107T150411Z` (RUN_NFL_FROZEN_BUNDLE), lag 0.0m vs target <= 180.0m; the simulation priced this packet's own board

> This packet contains no recommendations. Every model-vs-market number is a *disagreement*, which is not an edge. The model has been shown redundant to the closing market on player props and behind it on game outcomes; it is here as structure and context, not as a superior forecast.

## SLATE SUMMARY

- games: **15**
- markets listed this slate: **11488**, model-supported: **5611**
- ledger support states (all weeks): `{'UNSUPPORTED_MODEL': 19076, 'UNSUPPORTED_RULES': 6463, 'SUPPORTED': 8492, 'UNSUPPORTED_IDENTITY': 286, 'UNSUPPORTED_GAME': 2, 'POST_KICKOFF_EXCLUDED': 80639}`

### FULL-BOARD COVERAGE

_RUN NFL examines every executable Kalshi contract for every requested unstarted NFL game. UNSUPPORTED_MODEL is a statement about one model, never a reason to hide a contract. Every listed contract terminates in exactly one analysis state, in one of four buckets: A validated model view, B coherent/Shadow research view, C manual handicap from the packet's own football and context data, D explicit PASS with a named reason._

| bucket | contracts | meaning |
|---|---|---|
| **A** | 5611 | validated/production model view available |
| **B** | 2789 | coherent / Shadow research model view available |
| **C** | 970 | no automated pricing authority; handicap from the football and context data in this packet |
| **D** | 1233 | cannot defensibly price -- explicit PASS / RESEARCH REQUIRED, with a reason |
| **-** | 885 | outside the pregame window (kickoff has passed) |
| **!** | 0 | INVARIANT VIOLATION -- a listed contract with no analysis state |

- listed: **11488** · executable books: **9859**
- incumbent priced: **5611** · coherent simulation: **0** · Shadow v2 research: **2789**
- manual handicap required: **970** · research required: **56**
- rules blocked: **904** · identity blocked: **273** · non-football: **0**
- post-kickoff (stale): **885**
- **silently omitted: 0** — this must be 0.

| family / period | listed | executable | incumbent priced | coherent sim | shadow v2 | manual research | research required | rules blocked | identity blocked | non football | post kickoff | silently omitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLAYER_STAT/FULL | 5764 | 4992 | 4523 | 0 | 105 | 391 | 0 | 0 | 273 | 0 | 472 | 0 |
| FIRST_TD_TEAM/FULL | 409 | 153 | 0 | 0 | 0 | 72 | 0 | 305 | 0 | 0 | 32 | 0 |
| TEAM_TOTAL/FULL | 406 | 406 | 378 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 28 | 0 |
| SPREAD/FULL | 393 | 393 | 360 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 33 | 0 |
| FIRST_TD_SCORER/FULL | 363 | 363 | 0 | 0 | 0 | 15 | 0 | 318 | 0 | 0 | 30 | 0 |
| TEAM_TOTAL/1H | 325 | 319 | 0 | 0 | 304 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| TEAM_STAT/FULL | 300 | 34 | 0 | 0 | 0 | 280 | 0 | 0 | 0 | 0 | 20 | 0 |
| TOTAL/FULL | 287 | 287 | 266 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| SPREAD/1H | 240 | 240 | 0 | 0 | 221 | 0 | 0 | 0 | 0 | 0 | 19 | 0 |
| SPREAD/2H | 240 | 234 | 0 | 0 | 221 | 0 | 0 | 0 | 0 | 0 | 19 | 0 |
| RACE_TO_N/FULL | 225 | 138 | 0 | 0 | 0 | 210 | 0 | 0 | 0 | 0 | 15 | 0 |
| TOTAL/1H | 205 | 205 | 0 | 0 | 192 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |
| TOTAL/2H | 205 | 199 | 0 | 0 | 192 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |
| GAME_PLAYER_LEADER/FULL | 174 | 64 | 0 | 0 | 0 | 2 | 0 | 155 | 0 | 0 | 17 | 0 |
| SPREAD/4Q | 163 | 163 | 0 | 0 | 151 | 0 | 0 | 0 | 0 | 0 | 12 | 0 |
| SPREAD/3Q | 159 | 159 | 0 | 0 | 149 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| SPREAD/2Q | 157 | 157 | 0 | 0 | 147 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| SPREAD/1Q | 153 | 153 | 0 | 0 | 141 | 0 | 0 | 0 | 0 | 0 | 12 | 0 |
| TOTAL/1Q | 150 | 149 | 0 | 0 | 140 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/2Q | 150 | 137 | 0 | 0 | 140 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/3Q | 150 | 148 | 0 | 0 | 140 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/4Q | 150 | 137 | 0 | 0 | 140 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| HALF_FULL_RESULT/1H | 135 | 135 | 0 | 0 | 0 | 0 | 0 | 126 | 0 | 0 | 9 | 0 |
| WIN_MARGIN_BUCKET/FULL | 105 | 98 | 0 | 0 | 98 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| BOTH_TEAMS_SCORE_N/FULL | 60 | 27 | 56 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| GAME_EVENT/FULL | 60 | 54 | 0 | 0 | 0 | 0 | 56 | 0 | 0 | 0 | 4 | 0 |
| PERIOD_WINNER/1H | 45 | 45 | 0 | 0 | 42 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/1Q | 45 | 45 | 0 | 0 | 42 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2H | 45 | 44 | 0 | 0 | 42 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2Q | 45 | 45 | 0 | 0 | 42 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/3Q | 45 | 45 | 0 | 0 | 42 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/4Q | 45 | 45 | 0 | 0 | 42 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| GAME_WINNER/FULL | 30 | 30 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| BOTH_TEAMS_SCORE/1Q | 15 | 5 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/2Q | 15 | 4 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/3Q | 15 | 4 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/4Q | 15 | 3 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

_A Shadow v2 or coherent-simulation projection is RESEARCH. It is not validated, it is never mixed into the incumbent's probability or its disagreement ranking, and it reaches no recommendation, staking or preflight path._

**Skill players ruled OUT (40)**

- Elijah Sarratt (WR, BAL) — Out · 2026_09_JAX_BAL
- Kedon Slovis (QB, BAL) — Out · 2026_09_JAX_BAL
- Adam Randall (RB, BAL) — Injured Reserve · 2026_09_JAX_BAL
- Lamar Jackson (QB, BAL) — Injured Reserve · 2026_09_JAX_BAL
- Tyler Huntley (QB, BAL) — Injured Reserve · 2026_09_JAX_BAL
- CJ Williams (WR, JAX) — Out · 2026_09_JAX_BAL
- Brian Robinson Jr. (RB, ATL) — Out · 2026_09_CIN_ATL
- Zachariah Branch (WR, ATL) — Out · 2026_09_CIN_ATL
- Beaux Collins (WR, ATL) — Injured Reserve · 2026_09_CIN_ATL
- Andrei Iosivas (WR, CIN) — Injured Reserve · 2026_09_CIN_ATL
- Erick All Jr. (TE, CIN) — Injured Reserve · 2026_09_CIN_ATL
- CJ Donaldson (RB, NO) — Out · 2026_09_CLE_NO
- Jordyn Tyson (WR, NO) — Injured Reserve · 2026_09_CLE_NO
- Travis Etienne Jr. (RB, NO) — Injured Reserve · 2026_09_CLE_NO
- KaVontae Turpin (WR, DAL) — Out · 2026_09_DAL_IND

**New or changed since the previous capture (40)** — the most decision-relevant section on the page

- Aeneas Peebles (DT, BAL): **Out** (new record) · 2026_09_JAX_BAL
- Elijah Sarratt (WR, BAL): **Out** (was Active) · 2026_09_JAX_BAL
- Emery Jones Jr. (OT, BAL): **Out** (was Active) · 2026_09_JAX_BAL
- Jaylinn Hawkins (S, BAL): **Out** (was Questionable) · 2026_09_JAX_BAL
- Kedon Slovis (QB, BAL): **Out** (new record) · 2026_09_JAX_BAL
- Nate Wiggins (CB, BAL): **Out** (new record) · 2026_09_JAX_BAL
- Adisa Isaac (LB, BAL): **Questionable** (new record) · 2026_09_JAX_BAL
- Kyle Hamilton (S, BAL): **Questionable** (was Active) · 2026_09_JAX_BAL
- Adam Randall (RB, BAL): **Injured Reserve** (new record) · 2026_09_JAX_BAL
- Devontez Walker (WR, BAL): **Active** (new record) · 2026_09_JAX_BAL
- Jacoby Brissett (QB, BAL): **Active** (new record) · 2026_09_JAX_BAL
- Jake Moody (PK, BAL): **Active** (new record) · 2026_09_JAX_BAL
- Joe Fagnano (QB, BAL): **Active** (new record) · 2026_09_JAX_BAL
- Lamar Jackson (QB, BAL): **Injured Reserve** (was Questionable) · 2026_09_JAX_BAL
- Roger Rosengarten (OT, BAL): **Active** (new record) · 2026_09_JAX_BAL

**Largest market moves since first capture**

| ticker | game | family | move |
|---|---|---|---|
| `KXNFLRSHYDS-26NOV05JACBAL-BALJHILL43-50` | 2026_09_JAX_BAL | PLAYER_STAT | +0.945 |
| `KXNFLRRYDS-26NOV05JACBAL-BALJHILL43-80` | 2026_09_JAX_BAL | PLAYER_STAT | +0.940 |
| `KXNFLRECYDS-26NOV05JACBAL-JACNBOERKIRCHER87-50` | 2026_09_JAX_BAL | PLAYER_STAT | +0.930 |
| `KXNFLRSHYDS-26NOV05JACBAL-BALJHILL43-60` | 2026_09_JAX_BAL | PLAYER_STAT | +0.925 |
| `KXNFLRECYDS-26NOV05JACBAL-JACNBOERKIRCHER87-30` | 2026_09_JAX_BAL | PLAYER_STAT | +0.890 |
| `KXNFLRRYDS-26NOV05JACBAL-BALJHILL43-55` | 2026_09_JAX_BAL | PLAYER_STAT | +0.880 |
| `KXNFLRECYDS-26NOV05JACBAL-JACNBOERKIRCHER87-25` | 2026_09_JAX_BAL | PLAYER_STAT | +0.875 |
| `KXNFLFIRSTTD-26NOV05JACBAL-JACBTUTEN33` | 2026_09_JAX_BAL | FIRST_TD_SCORER | +0.875 |
| `KXNFLRSHYDS-26NOV05JACBAL-BALJHILL43-40` | 2026_09_JAX_BAL | PLAYER_STAT | +0.865 |
| `KXNFLRECYDS-26NOV05JACBAL-JACNBOERKIRCHER87-40` | 2026_09_JAX_BAL | PLAYER_STAT | +0.845 |

**Largest model/market disagreements** — DISAGREEMENT ONLY, REQUIRES HANDICAP

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26NOV08DETMIA-MIAOGORDON0-40` | Ollie Gordon II | 40.0 | 0.83 | 0.85 | 0.11 | -0.715 |
| `KXNFLREC-26NOV08LVSF-LVBBOWERS89-4` | Brock Bowers | 4.0 | 0.89 | 0.92 | 0.19 | -0.690 |
| `KXNFLREC-26NOV08DENCAR-DENJCOLEMAN20-2` | Jonah Coleman | 2.0 | 0.84 | 0.86 | 0.16 | -0.678 |
| `KXNFLREC-26NOV08LVSF-LVBBOWERS89-5` | Brock Bowers | 5.0 | 0.77 | 0.80 | 0.10 | -0.666 |
| `KXNFLRSHYDS-26NOV08DETMIA-MIAOGORDON0-50` | Ollie Gordon II | 50.0 | 0.73 | 0.75 | 0.08 | -0.658 |
| `KXNFLRECYDS-26NOV08GBNE-GBSWILLIAMS83-10` | Savion Williams | 10.0 | 0.67 | 0.69 | 0.01 | -0.658 |
| `KXNFLRSHATT-26NOV08NYJKC-KCKWALKER9-17` | Kenneth Walker III | 17.0 | 0.74 | 0.77 | 0.08 | -0.657 |
| `KXNFLREC-26NOV08GBNE-GBMGOLDEN0-3` | Matthew Golden | 3.0 | 0.88 | 0.91 | 0.22 | -0.656 |
| `KXNFLREC-26NOV08LARWAS-WASAWILLIAMS14-3` | Antonio Williams | 3.0 | 0.83 | 0.84 | 0.19 | -0.647 |
| `KXNFLREC-26NOV08ARISEA-ARITMCBRIDE85-5` | Trey McBride | 5.0 | 0.81 | 0.83 | 0.16 | -0.646 |
| `KXNFLRSHYDS-26NOV08ARISEA-SEAJPRICE8-30` | Jadarian Price | 30.0 | 0.81 | 0.82 | 0.18 | -0.634 |
| `KXNFLREC-26NOV08CLENO-CLEKCONCEPCION1-3` | KC Concepcion Jr. | 3.0 | 0.81 | 0.84 | 0.18 | -0.631 |

**Highest-liquidity markets**

- `KXNFLGAME-26NOV05JACBAL-BAL` (GAME_WINNER, 2026_09_JAX_BAL): volume 17765708, OI 12570423
- `KXNFLGAME-26NOV05JACBAL-JAC` (GAME_WINNER, 2026_09_JAX_BAL): volume 8668037, OI 5749147
- `KXNFLSPREAD-26NOV05JACBAL-JAC10` (SPREAD, 2026_09_JAX_BAL): volume 5619342, OI 3548811
- `KXNFLSPREAD-26NOV05JACBAL-JAC11` (SPREAD, 2026_09_JAX_BAL): volume 2025061, OI 1417248
- `KXNFLTOTAL-26NOV05JACBAL-40` (TOTAL, 2026_09_JAX_BAL): volume 1921392, OI 1293123
- `KXNFLTD-26NOV05JACBAL-BALDHENRY22-1` (PLAYER_STAT, 2026_09_JAX_BAL): volume 1854817, OI 1460856
- `KXNFLGAME-26NOV08NYGPHI-NYG` (GAME_WINNER, 2026_09_NYG_PHI): volume 1283950, OI 1020573
- `KXNFLSPREAD-26NOV05JACBAL-JAC7` (SPREAD, 2026_09_JAX_BAL): volume 1223339, OI 892174

**BLOCKING data issues**

- 2026_09_JAX_BAL: `GAME_STARTED` — kickoff has passed; this is not a pregame packet

### GAME PRIORITY FOR HANDICAP

_Priority ranks where deeper review may be most useful. It is NOT a bet ranking and carries no expectation that these games contain value._

| # | game | score | why |
|---|---|---|---|
| 1 | 2026_09_CIN_ATL | 20.91 | 22 new/changed injury records; 5 skill players ruled out (role change); largest market move 0.180; largest reconciled simulation disagreement 0.141; raw incumbent disagreement 0.584 (NOT scored: unvalidated); 346 supported player-prop rungs |
| 2 | 2026_09_ARI_SEA | 20.73 | 28 new/changed injury records; 6 skill players ruled out (role change); largest market move 0.235; largest reconciled simulation disagreement 0.123; raw incumbent disagreement 0.646 (NOT scored: unvalidated); 287 supported player-prop rungs |
| 3 | 2026_09_LA_WAS | 19.5 | 28 new/changed injury records; 7 skill players ruled out (role change); largest market move 0.170; raw incumbent disagreement 0.647 (NOT scored: unvalidated); 283 supported player-prop rungs |
| 4 | 2026_09_NYG_PHI | 19.5 | 25 new/changed injury records; 4 skill players ruled out (role change); largest market move 0.495; raw incumbent disagreement 0.620 (NOT scored: unvalidated); 305 supported player-prop rungs |
| 5 | 2026_09_LV_SF | 19.5 | 19 new/changed injury records; 6 skill players ruled out (role change); largest market move 0.145; raw incumbent disagreement 0.690 (NOT scored: unvalidated); 345 supported player-prop rungs |
| 6 | 2026_09_GB_NE | 19.5 | 30 new/changed injury records; 5 skill players ruled out (role change); largest market move 0.145; raw incumbent disagreement 0.658 (NOT scored: unvalidated); 313 supported player-prop rungs |
| 7 | 2026_09_DEN_CAR | 18.89 | 24 new/changed injury records; 3 skill players ruled out (role change); largest market move 0.145; largest reconciled simulation disagreement 0.089; raw incumbent disagreement 0.678 (NOT scored: unvalidated); 356 supported player-prop rungs |
| 8 | 2026_09_HOU_LAC | 18.87 | 21 new/changed injury records; 3 skill players ruled out (role change); largest market move 0.205; largest reconciled simulation disagreement 0.087; raw incumbent disagreement 0.493 (NOT scored: unvalidated); 351 supported player-prop rungs |
| 9 | 2026_09_JAX_BAL | 18.0 | 27 new/changed injury records; 6 skill players ruled out (role change); largest market move 0.945; BLOCKING data issue -- review before trusting anything here |
| 10 | 2026_09_CLE_NO | 18.0 | 20 new/changed injury records; 3 skill players ruled out (role change); largest market move 0.120; raw incumbent disagreement 0.631 (NOT scored: unvalidated); 289 supported player-prop rungs |
| 11 | 2026_09_DAL_IND | 16.5 | 29 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.125; raw incumbent disagreement 0.579 (NOT scored: unvalidated); 314 supported player-prop rungs |
| 12 | 2026_09_TB_CHI | 16.5 | 20 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.115; raw incumbent disagreement 0.630 (NOT scored: unvalidated); 315 supported player-prop rungs |
| 13 | 2026_09_DET_MIA | 15.0 | 22 new/changed injury records; 1 skill players ruled out (role change); largest market move 0.160; raw incumbent disagreement 0.715 (NOT scored: unvalidated); 320 supported player-prop rungs |
| 14 | 2026_09_NYJ_KC | 15.0 | 23 new/changed injury records; 1 skill players ruled out (role change); largest market move 0.155; raw incumbent disagreement 0.657 (NOT scored: unvalidated); 364 supported player-prop rungs |
| 15 | 2026_09_BUF_MIN | 13.5 | 25 new/changed injury records; largest market move 0.160; raw incumbent disagreement 0.555 (NOT scored: unvalidated); 335 supported player-prop rungs |

> Each game below is summarised. Full detail -- complete market board, every player ladder, all best-expression groups -- is in that game's own file under `games/`.


---

## JAX @ BAL — `2026_09_JAX_BAL`

- kickoff: 2026-11-06T01:15:00+00:00 (-2313 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 885 listed across 16 families — 0 supported, 24 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 885/885 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 21.95 | -- |
| total | 36.53 | -- |
| score | BAL 7.3 – JAX 29.2 | BAL -- – JAX -- |
| win prob BAL | 0.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 14.00 / total 19.50 · **2H** spread 8.32 / total 23.70 · **1Q** spread 7.00 / total 12.50 · **2Q** spread 7.00 / total 7.50 · **3Q** spread 3.00 / total -- · **4Q** spread 4.92 / total 19.71

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 21.95 · total 36.53
- move `KXNFL4QTOTAL-26NOV05JACBAL-18` +0.845

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261107T150411Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (6; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 6 market(s), e.g. KXNFLREC-26NOV05JACBAL-BALJHILL43-4, KXNFLTEAMFIRSTTD-26NOV05JACBAL-BAL-BALDST
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 4 market(s), e.g. KXNFLBOTH-26NOV05JACBAL-14, KXNFLTEAMTOTAL-26NOV05JACBAL-BAL11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 98 market(s), e.g. KXNFL2HSPREAD-26NOV05JACBAL-JAC15, KXNFL2HSPREAD-26NOV05JACBAL-JAC14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 27 market(s), e.g. KXNFL2HSPREAD-26NOV05JACBAL-JAC8, KXNFL2HSPREAD-26NOV05JACBAL-JAC6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 53 market(s), e.g. KXNFLLONGREC-26NOV05JACBAL-BALJHILL43-9, KXNFLLONGREC-26NOV05JACBAL-JACBTHOMAS7-10
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 271 market(s), e.g. KXNFLRECYDS-26NOV05JACBAL-BALJLANE6-5, KXNFLRECYDS-26NOV05JACBAL-BALZFLOWERS4-10

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261107T150411Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (14)**

- Kedon Slovis (QB, BAL) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Lamar Jackson (QB, BAL) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Tyler Huntley (QB, BAL) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Adam Randall (RB, BAL) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- CJ Williams (WR, JAX) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Elijah Sarratt (WR, BAL) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Emery Jones Jr. (OT, BAL) — Out [high] · **CHANGED from Active** — ruled out
- Aeneas Peebles (DT, BAL) — Out [high] · **NEW** — ruled out
- _...and 6 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Adisa Isaac (LB, BAL) — Questionable [high]
- Kyle Hamilton (S, BAL) — Questionable [conflicting]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 106 listed player/stat groups simulated and exposed, 106 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Elijah Sarratt (WR, BAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Kedon Slovis (QB, BAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLRSHYDS-26NOV05JACBAL-BALJHILL43-50 moved +0.945 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_JAX_BAL.md`_


---

## CIN @ ATL — `2026_09_CIN_ATL`

- kickoff: 2026-11-08T14:30:00+00:00 (1362 minutes away) · state **PREGAME**
- venue: Bernabeu · roof  · surface fieldturf
- markets: 776 listed across 16 families — 424 supported, 294 no model, 48 rules unresolved, 10 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 10 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.15 | 3.03 |
| total | 53.19 | 53.33 |
| score | ATL 25.0 – CIN 28.2 | ATL 25.1 – CIN 28.2 |
| win prob ATL | 38.5% | 38.7% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.56 / total 27.09 · **2H** spread 0.94 / total 26.75 · **1Q** spread 1.04 / total 9.62 · **2Q** spread 1.32 / total 15.77 · **3Q** spread 0.93 / total 10.00 · **4Q** spread 0.11 / total 14.84

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 3.15 · total 53.19

**Game environment** (simulation, mean and middle 50%) — home margin -3.4 (-11.0–4.0) · total 54.6 (45.0–63.0) · P(one score) 53.6% · P(17+ blowout) 18.6% · P(total 10+ over centre) 23.2%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| ATL | 62.5 (57.0–68.0) | 32.8 (28.0–37.0) | 25.4 (20.0–30.0) | 36.5 (31.0–42.0) | 0.585 (0.518–0.652) | 0.481 / 0.653 |
| CIN | 64.3 (59.0–70.0) | 37.7 (32.0–43.0) | 22.0 (17.0–26.0) | 41.3 (36.0–47.0) | 0.643 (0.577–0.711) | 0.562 / 0.735 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| ATL | 00-0038542 | RB | 5.0 (2.0–7.0) | 21.7 (17.0–27.0) | 15.8% | 85.7% | LOW |
| ATL | 00-0037238 | WR | 9.5 (6.0–12.0) | 0.2 (0.0–0.0) | 30.2% | 0.7% | MEDIUM |
| ATL | 00-0036970 | TE | 5.6 (3.0–8.0) | 0.0 (0.0–0.0) | 17.8% | 0.0% | HIGH |
| ATL | 00-0037741 | WR | 4.4 (2.0–6.0) | 0.2 (0.0–0.0) | 13.8% | 0.7% | HIGH |
| CIN | 00-0038597 | RB | 4.4 (2.0–6.0) | 16.9 (12.0–22.0) | 12.1% | 76.8% | MEDIUM |
| CIN | 00-0036900 | WR | 10.1 (6.0–13.0) | 0.1 (0.0–0.0) | 27.8% | 0.2% | MEDIUM |
| CIN | 00-0036410 | WR | 7.8 (4.0–11.0) | 0.1 (0.0–0.0) | 21.6% | 0.4% | HIGH |
| CIN | 00-0034829 | TE | 4.1 (2.0–6.0) | 0.1 (0.0–0.0) | 11.2% | 0.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 16 market(s), e.g. KXNFLPASSCOMP-26NOV08CINATL-ATLMPENIX9-25, KXNFLRECYDS-26NOV08CINATL-ATLOZACCHEAUS14-40
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 65 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV08CINATL-CIN21, KXNFL2QSPREAD-26NOV08CINATL-CIN8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLBOTH-26NOV08CINATL-28, KXNFLSPREAD-26NOV08CINATL-CIN18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 8 market(s), e.g. KXNFLGAME-26NOV08CINATL-CIN, KXNFLTOTAL-26NOV08CINATL-47
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 227 market(s), e.g. KXNFL1HFT-26NOV08CINATL-TIECIN, KXNFL1HFT-26NOV08CINATL-ATLCIN
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 41 market(s), e.g. KXNFL1HTOTAL-26NOV08CINATL-15, KXNFL2QTOTAL-26NOV08CINATL-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.2%  _(final margin within one score (8 points) either way; total within 10 of the centre 53.1875 (median favourite-oriented margin +1, median total 53))_
2. favourite controls / normal scoring — 16.8%  _(CIN (favourite) wins by more than one score; total within 10 of the centre 53.1875 (median favourite-oriented margin +15, median total 54))_
3. competitive / high scoring — 11.7%  _(final margin within one score (8 points) either way; total 63.1875+ (centre 53.1875) (median favourite-oriented margin +2, median total 71))_
4. competitive / low scoring — 10.6%  _(final margin within one score (8 points) either way; total 43.1875 or fewer (centre 53.1875) (median favourite-oriented margin +2, median total 39))_
5. underdog controls / normal scoring — 8.0%  _(ATL (underdog) wins by more than one score; total within 10 of the centre 53.1875 (median favourite-oriented margin -15, median total 53))_
   Other — 21.6%

Marginal events (overlapping): one_score 53.6% · blowout_17 18.6% · favorite_wins 63.6% · favorite_controls 32.2% · upset 36.2% · shootout 23.2% · low_scoring 20.7% · low_possession 7.5% · high_volume_passing 14.6% · run_heavy_control 10.8%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): no point-in-time forecast attached._

**`KXNFLTD-26NOV08CINATL-CINDSAMPLE89-1`** Drew Sample touchdowns 1
- MODEL / MARKET: football 8.6% · market 8.5% · reconciled 22.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.8% · failure mass 100.0% · win-contribution HHI 0.179

**`KXNFLTD-26NOV08CINATL-ATLMPENIX9-1`** Michael Penix Jr. touchdowns 1
- MODEL / MARKET: football 17.2% · market 8.5% · reconciled 11.1%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 10.1% · failure mass 100.0% · win-contribution HHI 0.178

**`KXNFLTD-26NOV08CINATL-CINSPERINE34-1`** Samaje Perine touchdowns 1
- MODEL / MARKET: football 13.6% · market 24.5% · reconciled 21.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.9% · failure mass 100.0% · win-contribution HHI 0.178

**`KXNFLTD-26NOV08CINATL-CINDSAMPLE89-2`** Drew Sample touchdowns 2
- MODEL / MARKET: football 1.1% · market 0.5% · reconciled 2.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.3% · failure mass 100.0% · win-contribution HHI 0.192

_414 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 44 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (11)**

- Andrei Iosivas (WR, CIN) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Beaux Collins (WR, ATL) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Brian Robinson Jr. (RB, ATL) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Erick All Jr. (TE, CIN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Zachariah Branch (WR, ATL) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Cameron Williams (OL, ATL) — Injured Reserve [high] · **NEW** — ruled out
- Anterio Thompson (DT, ATL) — Out [high] · **NEW** — ruled out
- Cashius Howell (DE, CIN) — Injured Reserve [high] · **NEW** — ruled out
- _...and 3 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Cedric Johnson (DE, CIN) — Questionable [high]
- Divine Deablo (LB, ATL) — Questionable [high]
- James Pearce Jr. (LB, ATL) — Questionable [high]

### WEATHER

played at Bernabeu, not ATL's home stadium -- no forecast for this venue is captured, and the home stadium's forecast is not shown (scheduled stadium id MAD01 (Bernabeu) is not ATL's home stadium ATL97 (Mercedes-Benz Stadium))

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 62 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Michael Penix Jr. | ATL | attempts | 31.5 | 32.0 | 27.0 | 37.0 | 18.0 | 44.0 | 32.2 | 32.0 | 31.5 | 32.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bijan Robinson | ATL | carries | 21.7 | 22.0 | 17.0 | 27.0 | 9.0 | 35.0 | 19.9 | 19.0 | 21.7 | 22.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | completions | 19.6 | 20.0 | 16.0 | 23.0 | 11.0 | 29.0 | 20.1 | 20.0 | 19.6 | 20.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | passing_tds | 1.6 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Michael Penix Jr. | ATL | passing_yards | 225.5 | 221.0 | 172.0 | 275.0 | 105.0 | 365.0 | 229.3 | 223.0 | 229.3 | 224.0 | 0.00 | 0.98 | 9 | PRICED |
| Drake London | ATL | receiving_yards | 79.9 | 72.0 | 40.0 | 110.0 | 6.0 | 179.0 | 86.0 | 78.0 | 86.0 | 77.0 | 0.00 | 0.97 | 14 | PRICED |
| Kyle Pitts Sr. | ATL | receiving_yards | 39.4 | 32.0 | 14.0 | 57.0 | 0.0 | 105.0 | 49.3 | 42.0 | 49.3 | 40.0 | 0.00 | 0.97 | 12 | PRICED |
| Jahan Dotson | ATL | receiving_yards | 37.8 | 26.0 | 7.0 | 57.0 | 0.0 | 116.0 | 37.3 | 28.0 | 37.3 | 26.0 | 0.00 | 0.98 | 11 | PRICED |

_8 of 62 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 62 of 102 listed player/stat groups simulated and exposed, 40 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26NOV08CINATL-ATLBROBINSON7-17` | Bijan Robinson | 17.0 | 0.69 | 0.70 | 0.11 | -0.584 |
| `KXNFLREC-26NOV08CINATL-ATLDLONDON5-4` | Drake London | 4.0 | 0.82 | 0.84 | 0.26 | -0.562 |
| `KXNFLREC-26NOV08CINATL-CINTHIGGINS5-4` | Tee Higgins | 4.0 | 0.78 | 0.79 | 0.22 | -0.557 |
| `KXNFLREC-26NOV08CINATL-ATLDLONDON5-5` | Drake London | 5.0 | 0.69 | 0.70 | 0.14 | -0.545 |
| `KXNFLREC-26NOV08CINATL-CINTHIGGINS5-5` | Tee Higgins | 5.0 | 0.64 | 0.66 | 0.12 | -0.523 |
| `KXNFLREC-26NOV08CINATL-CINCBROWN30-3` | Chase Brown | 3.0 | 0.74 | 0.76 | 0.24 | -0.501 |

_Ranked 420 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Brian Robinson Jr. (RB, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Zachariah Branch (WR, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLTEAMFIRSTTD-26NOV08CINATL-CIN-THIGGINS5 moved +0.180 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.584 on KXNFLRSHATT-26NOV08CINATL-ATLBROBINSON7-17 (Bijan Robinson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.562 on KXNFLREC-26NOV08CINATL-ATLDLONDON5-4 (Drake London). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26NOV08CINATL-CINTHIGGINS5-3 sits at a market price of 0.88 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_CIN_ATL.md`_


---

## CLE @ NO — `2026_09_CLE_NO`

- kickoff: 2026-11-08T18:00:00+00:00 (1572 minutes away) · state **PREGAME**
- venue: Caesars Superdome · roof dome · surface sportturf
- markets: 749 listed across 16 families — 366 supported, 293 no model, 48 rules unresolved, 42 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 42 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.31 | -3.35 |
| total | 42.83 | 42.40 |
| score | NO 23.1 – CLE 19.8 | NO 22.9 – CLE 19.5 |
| win prob NO | 61.5% | 61.6% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -2.34 / total 21.00 · **2H** spread -1.88 / total 20.76 · **1Q** spread -0.73 / total 7.73 · **2Q** spread -0.78 / total 12.38 · **3Q** spread -0.46 / total 8.00 · **4Q** spread -0.43 / total 11.48

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.31 · total 42.83
- move `KXNFL2QSPREAD-26NOV08CLENO-CLE7` -0.120
- move `KXNFL3QSPREAD-26NOV08CLENO-NO7` +0.100
- move `KXNFLTOTAL-26NOV08CLENO-23` +0.100
- move `KXNFL1QTOTAL-26NOV08CLENO-11` -0.095

**Game environment** (simulation, mean and middle 50%) — home margin 3.7 (-4.0–11.0) · total 43.7 (34.0–52.0) · P(one score) 52.4% · P(17+ blowout) 17.4% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NO | 64.1 (59.0–70.0) | 34.0 (29.0–39.0) | 25.1 (20.0–30.0) | 38.0 (32.0–43.0) | 0.593 (0.526–0.662) | 0.512 / 0.687 |
| CLE | 61.5 (56.0–67.0) | 31.0 (26.0–35.0) | 23.3 (19.0–28.0) | 37.6 (32.0–43.0) | 0.612 (0.547–0.679) | 0.507 / 0.680 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NO | 00-0033906 | RB | 3.8 (1.0–5.0) | 7.4 (3.0–11.0) | 11.6% | 29.4% | MEDIUM |
| NO | 00-0038551 | RB | 2.1 (0.0–3.0) | 8.0 (4.0–11.0) | 6.3% | 31.8% | HIGH |
| NO | 00-0037239 | WR | 8.4 (5.0–11.0) | 0.0 (0.0–0.0) | 25.5% | 0.2% | MEDIUM |
| NO | 00-0039373 | RB | 1.4 (0.0–2.0) | 6.9 (3.0–10.0) | 4.3% | 27.4% | HIGH |
| CLE | 00-0040784 | RB | 2.5 (1.0–4.0) | 14.7 (10.0–19.0) | 8.4% | 63.3% | MEDIUM |
| CLE | 00-0040162 | RB | 3.4 (1.0–5.0) | 3.7 (1.0–5.0) | 11.4% | 15.8% | HIGH |
| CLE | 00-0041037 | WR | 6.1 (3.0–8.0) | 0.0 (0.0–0.0) | 20.3% | 0.1% | HIGH |
| CLE | 00-0040663 | TE | 5.8 (3.0–8.0) | 0.1 (0.0–0.0) | 19.5% | 0.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 8 market(s), e.g. KXNFLPASSYDS-26NOV08CLENO-NOTSHOUGH6-275, KXNFLREC-26NOV08CLENO-CLEJJEUDY3-3
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 36 market(s), e.g. KXNFL1HFT-26NOV08CLENO-NONO, KXNFL3QSPREAD-26NOV08CLENO-NO7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV08CLENO-NO14, KXNFLSPREAD-26NOV08CLENO-NO11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLGAME-26NOV08CLENO-NO, KXNFLBOTH-26NOV08CLENO-14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 202 market(s), e.g. KXNFL1HFT-26NOV08CLENO-TIENO, KXNFL1HFT-26NOV08CLENO-TIECLE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 28 market(s), e.g. KXNFL2QTOTAL-26NOV08CLENO-4, KXNFLPASSCOMP-26NOV08CLENO-CLESSANDERS2-14

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.0%  _(final margin within one score (8 points) either way; total within 10 of the centre 42.8333 (median favourite-oriented margin +2, median total 42))_
2. favourite controls / normal scoring — 19.5%  _(NO (favourite) wins by more than one score; total within 10 of the centre 42.8333 (median favourite-oriented margin +14, median total 42))_
3. competitive / high scoring — 12.2%  _(final margin within one score (8 points) either way; total 52.8333+ (centre 42.8333) (median favourite-oriented margin +2, median total 60))_
4. competitive / low scoring — 11.2%  _(final margin within one score (8 points) either way; total 32.8333 or fewer (centre 42.8333) (median favourite-oriented margin +2, median total 28))_
5. favourite controls / high scoring — 7.8%  _(NO (favourite) wins by more than one score; total 52.8333+ (centre 42.8333) (median favourite-oriented margin +17, median total 60))_
   Other — 20.2%

Marginal events (overlapping): one_score 52.4% · blowout_17 17.4% · favorite_wins 63.8% · favorite_controls 33.0% · upset 36.0% · shootout 23.8% · low_scoring 20.6% · low_possession 9.5% · high_volume_passing 4.5% · run_heavy_control 12.9%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): no point-in-time forecast attached._

**`KXNFLTD-26NOV08CLENO-NOAESTIME30-1`** Audric Estime touchdowns 1
- MODEL / MARKET: football 24.4% · market 9.5% · reconciled 13.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 13.1% · failure mass 100.0% · win-contribution HHI 0.185

**`KXNFLTD-26NOV08CLENO-CLEDSAMPSON22-1`** Dylan Sampson touchdowns 1
- MODEL / MARKET: football 19.0% · market 13.5% · reconciled 15.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 11.4% · failure mass 100.0% · win-contribution HHI 0.175

**`KXNFLTD-26NOV08CLENO-NOKMILLER5-1`** Kendre Miller touchdowns 1
- MODEL / MARKET: football 26.1% · market 34.5% · reconciled 32.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 13.7% · failure mass 100.0% · win-contribution HHI 0.183

**`KXNFLTD-26NOV08CLENO-NOAKAMARA41-2`** Alvin Kamara touchdowns 2
- MODEL / MARKET: football 6.0% · market 2.0% · reconciled 3.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 1.2% · failure mass 100.0% · win-contribution HHI 0.203

_359 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 37 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (5)**

- CJ Donaldson (RB, NO) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Jordyn Tyson (WR, NO) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Travis Etienne Jr. (RB, NO) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Kelvin Banks Jr. (OT, NO) — Injured Reserve [high] · **NEW** — ruled out
- Maliek Collins (DT, CLE) — Out [high] · **CHANGED from Active** — ruled out

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Deshaun Watson (QB, CLE) — Questionable [high]
- Asim Richards (OT, NO) — Questionable [high]
- Martin Emerson Jr. (CB, NO) — Questionable [high]

### WEATHER

fixed-roof stadium (Caesars Superdome) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 51 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Quinshon Judkins | CLE | carries | 14.7 | 14.0 | 10.0 | 19.0 | 4.0 | 27.0 | 16.8 | 16.0 | 14.7 | 14.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Denzel Boston | CLE | receiving_yards | 47.9 | 39.0 | 16.0 | 70.0 | 0.0 | 129.0 | 50.2 | 41.0 | 50.2 | 41.0 | 0.00 | 0.97 | 13 | PRICED |
| Harold Fannin Jr. | CLE | receiving_yards | 43.0 | 35.0 | 16.0 | 62.0 | 0.0 | 111.0 | 49.5 | 42.0 | 49.6 | 41.0 | 0.00 | 0.98 | 13 | PRICED |
| KC Concepcion Jr. | CLE | receiving_yards | 35.8 | 28.0 | 11.0 | 52.0 | 0.0 | 101.0 | 51.8 | 44.0 | 51.8 | 40.0 | 0.00 | 0.98 | 12 | PRICED |
| Jerry Jeudy | CLE | receiving_yards | 22.4 | 14.0 | 0.0 | 34.0 | 0.0 | 76.0 | 21.4 | 14.0 | 21.4 | 13.0 | 0.00 | 0.98 | 8 | PRICED |
| Dylan Sampson | CLE | receiving_yards | 19.8 | 13.0 | 3.0 | 29.0 | 0.0 | 64.0 | 24.3 | 19.0 | 24.4 | 16.0 | 0.00 | 0.98 | 8 | PRICED |
| Quinshon Judkins | CLE | receiving_yards | 13.4 | 8.0 | 0.0 | 20.0 | 0.0 | 48.0 | 12.9 | 9.0 | 12.9 | 7.0 | 0.00 | 0.98 | 6 | PRICED |
| Harold Fannin Jr. | CLE | receptions | 4.1 | 4.0 | 2.0 | 6.0 | 0.0 | 9.0 | 4.6 | 4.0 | 4.6 | 4.0 | 0.00 | 0.98 | 10 | PRICED |

_8 of 51 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 51 of 93 listed player/stat groups simulated and exposed, 42 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV08CLENO-CLEKCONCEPCION1-3` | KC Concepcion Jr. | 3.0 | 0.81 | 0.84 | 0.18 | -0.631 |
| `KXNFLREC-26NOV08CLENO-CLEKCONCEPCION1-2` | KC Concepcion Jr. | 2.0 | 0.93 | 0.96 | 0.31 | -0.614 |
| `KXNFLREC-26NOV08CLENO-CLEHFANNIN44-3` | Harold Fannin Jr. | 3.0 | 0.81 | 0.84 | 0.26 | -0.553 |
| `KXNFLREC-26NOV08CLENO-CLEKCONCEPCION1-4` | KC Concepcion Jr. | 4.0 | 0.65 | 0.67 | 0.11 | -0.540 |
| `KXNFLRSHATT-26NOV08CLENO-CLEQJUDKINS10-14` | Quinshon Judkins | 14.0 | 0.70 | 0.72 | 0.17 | -0.529 |
| `KXNFLREC-26NOV08CLENO-CLEHFANNIN44-4` | Harold Fannin Jr. | 4.0 | 0.65 | 0.67 | 0.14 | -0.506 |

_Ranked 323 tradable markets; 43 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. CJ Donaldson (RB, NO) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jordyn Tyson (WR, NO) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Deshaun Watson (QB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLTD-26NOV08CLENO-CLEDBOSTON12-1 moved +0.120 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.631 on KXNFLREC-26NOV08CLENO-CLEKCONCEPCION1-3 (KC Concepcion Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.614 on KXNFLREC-26NOV08CLENO-CLEKCONCEPCION1-2 (KC Concepcion Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV08CLENO-CLEKCONCEPCION1-2 sits at a market price of 0.93 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_CLE_NO.md`_


---

## DAL @ IND — `2026_09_DAL_IND`

- kickoff: 2026-11-08T18:00:00+00:00 (1572 minutes away) · state **PREGAME**
- venue: Lucas Oil Stadium · roof  · surface fieldturf
- markets: 732 listed across 16 families — 391 supported, 285 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 4.67 | 4.86 |
| total | 52.12 | 52.51 |
| score | IND 23.7 – DAL 28.4 | IND 23.8 – DAL 28.7 |
| win prob IND | 32.5% | 32.7% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 3.07 / total 27.00 · **2H** spread 2.50 / total 26.00 · **1Q** spread 1.23 / total 9.46 · **2Q** spread 2.00 / total 15.42 · **3Q** spread 0.99 / total 10.15 · **4Q** spread 0.50 / total 14.61

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 4.67 · total 52.12
- move `KXNFL2QSPREAD-26NOV08DALIND-DAL7` -0.100
- move `KXNFLTOTAL-26NOV08DALIND-74` -0.095
- move `KXNFL3QSPREAD-26NOV08DALIND-IND4` +0.095
- move `KXNFL2QSPREAD-26NOV08DALIND-DAL8` -0.090

**Game environment** (simulation, mean and middle 50%) — home margin -4.5 (-12.0–3.0) · total 53.7 (45.0–62.0) · P(one score) 51.9% · P(17+ blowout) 19.8% · P(total 10+ over centre) 23.6%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| IND | 63.7 (58.0–69.0) | 34.6 (30.0–39.0) | 24.4 (19.0–29.0) | 38.7 (33.0–44.0) | 0.609 (0.543–0.675) | 0.500 / 0.670 |
| DAL | 65.3 (60.0–71.0) | 34.8 (30.0–40.0) | 26.1 (21.0–31.0) | 38.3 (33.0–44.0) | 0.587 (0.520–0.655) | 0.511 / 0.686 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| IND | 00-0036223 | RB | 3.4 (1.0–5.0) | 12.4 (7.0–17.0) | 10.2% | 50.9% | MEDIUM |
| IND | 00-0040128 | TE | 6.8 (4.0–9.0) | 0.2 (0.0–0.0) | 20.4% | 1.0% | HIGH |
| IND | 00-0038997 | WR | 6.0 (3.0–8.0) | 0.2 (0.0–0.0) | 18.2% | 0.7% | HIGH |
| IND | 00-0030279 | WR | 5.9 (3.0–8.0) | 0.1 (0.0–0.0) | 18.0% | 0.3% | HIGH |
| DAL | 00-0036997 | RB | 3.1 (1.0–4.0) | 18.3 (13.0–23.0) | 9.1% | 70.3% | MEDIUM |
| DAL | 00-0036358 | WR | 10.9 (7.0–14.0) | 0.2 (0.0–0.0) | 32.2% | 0.7% | MEDIUM |
| DAL | 00-0037120 | RB | 1.5 (0.0–2.0) | 4.8 (1.0–7.0) | 4.3% | 18.4% | HIGH |
| DAL | 00-0039410 | WR | 5.1 (2.0–7.0) | 0.4 (0.0–0.0) | 15.3% | 1.6% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 17 market(s), e.g. KXNFLPASSATT-26NOV08DALIND-INDDJONES17-37, KXNFLPASSATT-26NOV08DALIND-DALDPRESCOTT4-39
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 39 market(s), e.g. KXNFL1HFT-26NOV08DALIND-INDIND, KXNFL2H-26NOV08DALIND-IND
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 20 market(s), e.g. KXNFLSPREAD-26NOV08DALIND-IND8, KXNFLSPREAD-26NOV08DALIND-IND5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLGAME-26NOV08DALIND-DAL, KXNFLSPREAD-26NOV08DALIND-DAL2
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 179 market(s), e.g. KXNFL1HFT-26NOV08DALIND-INDDAL, KXNFL1HFT-26NOV08DALIND-DALIND
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 42 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV08DALIND-DAL3, KXNFL1QTOTAL-26NOV08DALIND-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 30.7%  _(final margin within one score (8 points) either way; total within 10 of the centre 52.125 (median favourite-oriented margin +2, median total 52))_
2. favourite controls / normal scoring — 18.7%  _(DAL (favourite) wins by more than one score; total within 10 of the centre 52.125 (median favourite-oriented margin +16, median total 53))_
3. competitive / high scoring — 11.7%  _(final margin within one score (8 points) either way; total 62.125+ (centre 52.125) (median favourite-oriented margin +2, median total 70))_
4. competitive / low scoring — 9.6%  _(final margin within one score (8 points) either way; total 42.125 or fewer (centre 52.125) (median favourite-oriented margin +3, median total 38))_
5. favourite controls / low scoring — 8.6%  _(DAL (favourite) wins by more than one score; total 42.125 or fewer (centre 52.125) (median favourite-oriented margin +15, median total 37))_
   Other — 20.8%

Marginal events (overlapping): one_score 51.9% · blowout_17 19.8% · favorite_wins 66.0% · favorite_controls 35.2% · upset 33.8% · shootout 23.6% · low_scoring 20.3% · low_possession 4.4% · high_volume_passing 12.1% · run_heavy_control 16.0%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 12.90 mph, gusts 25.10, precip prob 0%, temp 51F, forecast retrieved 2026-11-07T14:56:30+00:00 (27.06 h before kickoff)._

**`KXNFLTD-26NOV08DALIND-DALGPICKENS3-1`** George Pickens touchdowns 1
- MODEL / MARKET: football 23.8% · market 40.5% · reconciled 37.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 23.5% · failure mass 100.0% · win-contribution HHI 0.184
- THESIS DEPENDENCY with `KXNFLRECYDS-26NOV08DALIND-DALGPICKENS3-30`: cash correlation 0.334 · joint cash 19.8% · Jaccard of winning rows 0.345 · shared failure 42.6%

**`KXNFLTD-26NOV08DALIND-INDJTAYLOR28-1`** Jonathan Taylor touchdowns 1
- MODEL / MARKET: football 48.7% · market 56.5% · reconciled 53.8%
- SCRIPT ROBUSTNESS: P50 mass 63.1% · P55 mass 22.4% · P60 mass 22.4% · major-script floor 37.0% · failure mass 36.9% · win-contribution HHI 0.179

**`KXNFLTD-26NOV08DALIND-DALJWILLIAMS33-3`** Javonte Williams touchdowns 3
- MODEL / MARKET: football 8.2% · market 6.0% · reconciled 8.4%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.8% · failure mass 100.0% · win-contribution HHI 0.239

**`KXNFLTD-26NOV08DALIND-INDSMCGOWAN20-1`** Seth McGowan touchdowns 1
- MODEL / MARKET: football 13.8% · market 25.0% · reconciled 23.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.7% · failure mass 100.0% · win-contribution HHI 0.173

_381 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 38 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (7)**

- Alec Pierce (WR, IND) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- KaVontae Turpin (WR, DAL) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Akeem Davis-Gaither (LB, IND) — Out [high] · **CHANGED from Active** — ruled out
- Jalen Thompson (S, DAL) — Injured Reserve [high] · **NEW** — ruled out
- Jonathan Bullard (DT, DAL) — Injured Reserve [high] · **NEW** — ruled out
- Justin Walley (CB, IND) — Out [high] · **CHANGED from Questionable** — ruled out
- Malachi Lawrence (LB, DAL) — Out [high] · **NEW** — ruled out

**Questionable / Doubtful (7)** — resolves at the inactive release, T−90m

- George Pickens (WR, DAL) — Questionable [high]
- Jake Ferguson (TE, DAL) — Questionable [high]
- Luke Schoonmaker (TE, DAL) — Questionable [high]
- Jalen Travis (OT, IND) — Questionable [single_source]
- A.J. Haulcy (S, IND) — Questionable [high]
- DeMarvion Overshown (LB, DAL) — Questionable [high]
- Joey Porter Jr. (CB, DAL) — Questionable [high]

### WEATHER

- retractable roof (Lucas Oil Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Sunny · 56°F · wind 12 mph SW · precip 0%
- forecast vintage 2026-11-07T14:56:32+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 53 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Dak Prescott | DAL | attempts | 33.4 | 34.0 | 28.0 | 39.0 | 19.0 | 47.0 | 33.2 | 33.0 | 33.4 | 34.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Javonte Williams | DAL | carries | 18.3 | 18.0 | 13.0 | 23.0 | 6.0 | 32.0 | 17.7 | 17.0 | 18.3 | 18.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | completions | 21.9 | 22.0 | 18.0 | 26.0 | 12.0 | 32.0 | 22.7 | 22.0 | 21.9 | 22.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | passing_tds | 1.9 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.1 | 2.0 | 2.1 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Dak Prescott | DAL | passing_yards | 250.9 | 247.0 | 193.0 | 306.0 | 119.0 | 398.0 | 266.5 | 262.0 | 266.5 | 263.0 | 0.00 | 0.97 | 10 | PRICED |
| CeeDee Lamb | DAL | receiving_yards | 91.0 | 83.0 | 48.0 | 125.0 | 10.0 | 200.0 | 90.4 | 83.0 | 90.4 | 82.0 | 0.00 | 0.97 | 14 | PRICED |
| George Pickens | DAL | receiving_yards | 45.7 | 34.0 | 0.0 | 72.0 | 0.0 | 140.0 | 64.1 | 55.0 | 63.8 | 48.0 | 0.00 | 0.77 | 13 | PRICED |
| Ryan Flournoy | DAL | receiving_yards | 41.2 | 31.0 | 12.0 | 60.0 | 0.0 | 117.0 | 44.7 | 37.0 | 44.7 | 34.0 | 0.00 | 0.97 | 11 | PRICED |

_8 of 53 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 53 of 86 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV08DALIND-INDTWARREN84-4` | Tyler Warren | 4.0 | 0.74 | 0.78 | 0.17 | -0.579 |
| `KXNFLRSHATT-26NOV08DALIND-DALJWILLIAMS33-15` | Javonte Williams | 15.0 | 0.70 | 0.73 | 0.13 | -0.574 |
| `KXNFLREC-26NOV08DALIND-INDTWARREN84-3` | Tyler Warren | 3.0 | 0.86 | 0.89 | 0.30 | -0.563 |
| `KXNFLREC-26NOV08DALIND-DALCLAMB88-6` | CeeDee Lamb | 6.0 | 0.59 | 0.63 | 0.07 | -0.523 |
| `KXNFLRSHYDS-26NOV08DALIND-DALTGOODSON32-10` | Tyler Goodson | 10.0 | 0.68 | 0.74 | 0.17 | -0.513 |
| `KXNFLREC-26NOV08DALIND-INDTWARREN84-5` | Tyler Warren | 5.0 | 0.59 | 0.61 | 0.09 | -0.501 |

_Ranked 350 tradable markets; 41 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. KaVontae Turpin (WR, DAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Alec Pierce (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 3 skill players are Questionable (George Pickens (WR), Jake Ferguson (TE), Luke Schoonmaker (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRECYDS-26NOV08DALIND-INDKALLEN10-50 moved +0.125 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.579 on KXNFLREC-26NOV08DALIND-INDTWARREN84-4 (Tyler Warren). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.574 on KXNFLRSHATT-26NOV08DALIND-DALJWILLIAMS33-15 (Javonte Williams). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLPASSYDS-26NOV08DALIND-INDDJONES17-300 sits at a market price of 0.08 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_DAL_IND.md`_


---

## DEN @ CAR — `2026_09_DEN_CAR`

- kickoff: 2026-11-08T18:00:00+00:00 (1572 minutes away) · state **PREGAME**
- venue: Bank of America Stadium · roof outdoors · surface grass
- markets: 790 listed across 16 families — 433 supported, 301 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.69 | 2.20 |
| total | 45.12 | 45.08 |
| score | CAR 21.2 – DEN 23.9 | CAR 21.4 – DEN 23.6 |
| win prob CAR | 42.5% | 41.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 1.35 / total 22.00 · **2H** spread 0.61 / total 22.67 · **1Q** spread 0.58 / total 7.97 · **2Q** spread 0.53 / total 13.25 · **3Q** spread -0.13 / total 8.62 · **4Q** spread 0.26 / total 13.09

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 2.69 · total 45.12
- move `KXNFL1HTEAMTOTAL-26NOV08DENCAR-DEN31` -0.110
- move `KXNFL2QSPREAD-26NOV08DENCAR-DEN7` -0.095

**Game environment** (simulation, mean and middle 50%) — home margin -2.6 (-10.0–5.0) · total 46.8 (38.0–55.0) · P(one score) 53.5% · P(17+ blowout) 18.1% · P(total 10+ over centre) 24.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CAR | 64.9 (59.0–71.0) | 36.7 (32.0–42.0) | 22.8 (18.0–27.0) | 41.4 (36.0–47.0) | 0.639 (0.573–0.707) | 0.538 / 0.707 |
| DEN | 62.2 (56.0–68.0) | 34.0 (29.0–39.0) | 24.4 (19.0–29.0) | 36.9 (31.0–42.0) | 0.593 (0.526–0.662) | 0.511 / 0.685 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CAR | 00-0036555 | RB | 3.9 (1.0–6.0) | 14.5 (10.0–19.0) | 11.6% | 63.7% | MEDIUM |
| CAR | 00-0040124 | WR | 8.1 (5.0–11.0) | 0.0 (0.0–0.0) | 23.8% | 0.2% | MEDIUM |
| CAR | 00-0039491 | WR | 5.7 (3.0–8.0) | 0.1 (0.0–0.0) | 16.7% | 0.3% | HIGH |
| CAR | 00-0031610 | TE | 3.4 (1.0–5.0) | 0.1 (0.0–0.0) | 10.0% | 0.4% | HIGH |
| DEN | 00-0041496 | RB | 3.3 (1.0–5.0) | 10.4 (6.0–14.0) | 10.4% | 42.5% | MEDIUM |
| DEN | 00-0036158 | RB | 1.3 (0.0–2.0) | 9.9 (5.0–14.0) | 4.1% | 40.5% | MEDIUM |
| DEN | 00-0036613 | WR | 7.3 (4.0–10.0) | 0.2 (0.0–0.0) | 23.0% | 0.6% | MEDIUM |
| DEN | 00-0034348 | WR | 5.3 (2.0–7.0) | 0.1 (0.0–0.0) | 16.7% | 0.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 38 market(s), e.g. KXNFLPASSATT-26NOV08DENCAR-DENBNIX10-38, KXNFLPASSATT-26NOV08DENCAR-DENBNIX10-33
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 48 market(s), e.g. KXNFLPASSYDS-26NOV08DENCAR-DENBNIX10-250, KXNFLRECYDS-26NOV08DENCAR-DENJCOLEMAN20-40
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 24 market(s), e.g. KXNFLSPREAD-26NOV08DENCAR-DEN11, KXNFLSPREAD-26NOV08DENCAR-DEN10
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLTEAMTOTAL-26NOV08DENCAR-CAR18, KXNFLTOTAL-26NOV08DENCAR-42
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 208 market(s), e.g. KXNFL1HFT-26NOV08DENCAR-TIEDEN, KXNFL1HFT-26NOV08DENCAR-DENCAR
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 25 market(s), e.g. KXNFL2HTOTAL-26NOV08DENCAR-11, KXNFL2QTOTAL-26NOV08DENCAR-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.4%  _(final margin within one score (8 points) either way; total within 10 of the centre 45.125 (median favourite-oriented margin +1, median total 45))_
2. favourite controls / normal scoring — 15.8%  _(DEN (favourite) wins by more than one score; total within 10 of the centre 45.125 (median favourite-oriented margin +15, median total 46))_
3. competitive / high scoring — 12.0%  _(final margin within one score (8 points) either way; total 55.125+ (centre 45.125) (median favourite-oriented margin +1, median total 63))_
4. competitive / low scoring — 10.1%  _(final margin within one score (8 points) either way; total 35.125 or fewer (centre 45.125) (median favourite-oriented margin +2, median total 31))_
5. underdog controls / normal scoring — 8.4%  _(CAR (underdog) wins by more than one score; total within 10 of the centre 45.125 (median favourite-oriented margin -16, median total 45))_
   Other — 22.4%

Marginal events (overlapping): one_score 53.5% · blowout_17 18.1% · favorite_wins 60.8% · favorite_controls 30.4% · upset 39.0% · shootout 24.3% · low_scoring 20.1% · low_possession 7.0% · high_volume_passing 15.2% · run_heavy_control 11.5%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 7.30 mph, gusts 11.20, precip prob 0%, temp 65F, forecast retrieved 2026-11-07T14:56:30+00:00 (27.06 h before kickoff)._

**`KXNFLTD-26NOV08DENCAR-DENTFRANKLIN11-1`** Troy Franklin touchdowns 1
- MODEL / MARKET: football 12.9% · market 10.0% · reconciled 18.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.0% · failure mass 100.0% · win-contribution HHI 0.177

**`KXNFLTD-26NOV08DENCAR-CARJMETCHIE13-1`** John Metchie III touchdowns 1
- MODEL / MARKET: football 12.2% · market 10.0% · reconciled 18.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 8.1% · failure mass 100.0% · win-contribution HHI 0.175

**`KXNFLTD-26NOV08DENCAR-DENNADKINS45-2`** Nate Adkins touchdowns 2
- MODEL / MARKET: football 0.9% · market 0.5% · reconciled 2.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.2% · failure mass 100.0% · win-contribution HHI 0.194

**`KXNFLTD-26NOV08DENCAR-DENJDOBBINS27-3`** J.K. Dobbins touchdowns 3
- MODEL / MARKET: football 0.9% · market 2.5% · reconciled 0.4%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.0% · failure mass 100.0% · win-contribution HHI 0.266

_423 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 45 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (12)**

- Jonathon Brooks (RB, CAR) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Pat Bryant (WR, DEN) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Xavier Legette (WR, CAR) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Brady Christensen (G, CAR) — Injured Reserve [high] · **NEW** — ruled out
- Damien Lewis (G, CAR) — Out [high] · **CHANGED from Questionable** — ruled out
- Akayleb Evans (CB, CAR) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out
- Bobby Okereke (LB, CAR) — Out [high] · **CHANGED from Active** — ruled out
- Brandon Jones (S, DEN) — Out [high] · **CHANGED from Active** — ruled out
- _...and 4 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Corey Bullock (C, CAR) — Questionable [high]
- Torricelli Simpkins III (G, CAR) — Questionable [high]
- Dondrea Tillman (LB, DEN) — Questionable [high]
- Talanoa Hufanga (S, DEN) — Questionable [high]

### WEATHER

- Sunny · 62°F · wind 6 mph WSW · precip 0%
- forecast vintage 2026-11-07T14:56:30+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 64 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bryce Young | CAR | attempts | 35.2 | 35.0 | 30.0 | 41.0 | 21.0 | 49.0 | 34.8 | 34.0 | 35.2 | 35.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chuba Hubbard | CAR | carries | 14.5 | 14.0 | 10.0 | 19.0 | 3.0 | 27.0 | 17.7 | 17.0 | 14.5 | 14.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | completions | 21.4 | 21.0 | 18.0 | 25.0 | 12.0 | 31.0 | 22.0 | 22.0 | 21.4 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Bryce Young | CAR | passing_yards | 229.1 | 225.0 | 177.0 | 278.0 | 108.0 | 364.0 | 229.6 | 223.0 | 229.6 | 225.0 | 0.00 | 0.98 | 10 | PRICED |
| Tetairoa McMillan | CAR | receiving_yards | 63.9 | 55.0 | 28.0 | 91.0 | 0.0 | 155.0 | 67.7 | 60.0 | 67.7 | 58.0 | 0.00 | 0.97 | 13 | PRICED |
| Jalen Coker | CAR | receiving_yards | 43.7 | 34.0 | 14.0 | 63.0 | 0.0 | 120.0 | 57.6 | 49.0 | 57.5 | 45.0 | 0.00 | 0.97 | 13 | PRICED |
| Darren Waller | CAR | receiving_yards | 24.7 | 16.0 | 1.0 | 37.0 | 0.0 | 81.0 | 25.2 | 18.0 | 25.2 | 17.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 64 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 64 of 102 listed player/stat groups simulated and exposed, 38 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV08DENCAR-DENJCOLEMAN20-2` | Jonah Coleman | 2.0 | 0.84 | 0.86 | 0.16 | -0.678 |
| `KXNFLRSHYDS-26NOV08DENCAR-CARCHUBBARD30-40` | Chuba Hubbard | 40.0 | 0.82 | 0.84 | 0.22 | -0.608 |
| `KXNFLRSHATT-26NOV08DENCAR-CARCHUBBARD30-15` | Chuba Hubbard | 15.0 | 0.69 | 0.72 | 0.10 | -0.591 |
| `KXNFLRSHYDS-26NOV08DENCAR-CARCHUBBARD30-50` | Chuba Hubbard | 50.0 | 0.72 | 0.74 | 0.15 | -0.578 |
| `KXNFLRECYDS-26NOV08DENCAR-DENJCOLEMAN20-20` | Jonah Coleman | 20.0 | 0.59 | 0.61 | 0.02 | -0.574 |
| `KXNFLREC-26NOV08DENCAR-DENJCOLEMAN20-3` | Jonah Coleman | 3.0 | 0.67 | 0.69 | 0.11 | -0.562 |

_Ranked 420 tradable markets; 13 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jonathon Brooks (RB, CAR) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Xavier Legette (WR, CAR) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLRECYDS-26NOV08DENCAR-DENJWADDLE17-70 moved +0.145 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.678 on KXNFLREC-26NOV08DENCAR-DENJCOLEMAN20-2 (Jonah Coleman). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.608 on KXNFLRSHYDS-26NOV08DENCAR-CARCHUBBARD30-40 (Chuba Hubbard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26NOV08DENCAR-DENJWADDLE17-2 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_DEN_CAR.md`_


---

## DET @ MIA — `2026_09_DET_MIA`

- kickoff: 2026-11-08T18:00:00+00:00 (1572 minutes away) · state **PREGAME**
- venue: Hard Rock Stadium · roof outdoors · surface grass
- markets: 736 listed across 16 families — 399 supported, 281 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 6.57 | 6.70 |
| total | 50.50 | 50.36 |
| score | MIA 22.0 – DET 28.5 | MIA 21.8 – DET 28.5 |
| win prob MIA | 26.5% | 26.4% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 3.67 / total 25.00 · **2H** spread 3.12 / total 24.77 · **1Q** spread 1.33 / total 9.13 · **2Q** spread 2.79 / total 14.93 · **3Q** spread 1.09 / total 9.63 · **4Q** spread 1.06 / total 14.38

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 6.57 · total 50.50

**Game environment** (simulation, mean and middle 50%) — home margin -6.5 (-14.0–1.0) · total 51.7 (43.0–60.0) · P(one score) 48.4% · P(17+ blowout) 23.5% · P(total 10+ over centre) 23.7%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| MIA | 61.2 (56.0–67.0) | 29.1 (25.0–33.0) | 25.0 (20.0–30.0) | 35.7 (30.0–41.0) | 0.585 (0.518–0.651) | 0.472 / 0.639 |
| DET | 64.4 (59.0–70.0) | 32.5 (27.0–37.0) | 28.3 (23.0–33.0) | 35.0 (30.0–40.0) | 0.544 (0.477–0.612) | 0.473 / 0.650 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| MIA | 00-0040198 | RB | 1.9 (0.0–3.0) | 15.5 (10.0–20.0) | 6.8% | 62.1% | MEDIUM |
| MIA | 00-0039880 | WR | 5.7 (3.0–8.0) | 0.9 (0.0–1.0) | 20.1% | 3.5% | HIGH |
| MIA | 00-0038128 | QB | 0.5 (0.0–0.0) | 5.8 (3.0–7.0) | 1.6% | 6.7% | HIGH |
| MIA | 00-0041523 | WR | 4.5 (2.0–6.0) | 0.0 (0.0–0.0) | 15.8% | 0.1% | HIGH |
| DET | 00-0039139 | RB | 5.7 (3.0–8.0) | 21.6 (16.0–27.0) | 18.2% | 76.4% | MEDIUM |
| DET | 00-0036963 | WR | 7.4 (2.0–11.0) | 0.4 (0.0–0.0) | 23.6% | 1.4% | HIGH |
| DET | 00-0039065 | TE | 5.9 (3.0–8.0) | 0.3 (0.0–0.0) | 18.9% | 1.1% | HIGH |
| DET | 00-0037240 | WR | 6.0 (3.0–8.0) | 0.1 (0.0–0.0) | 19.3% | 0.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 13 market(s), e.g. KXNFLPASSATT-26NOV08DETMIA-MIAMWILLIS2-33, KXNFLPASSATT-26NOV08DETMIA-DETJGOFF16-36
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 53 market(s), e.g. KXNFL1HFT-26NOV08DETMIA-MIAMIA, KXNFL2H-26NOV08DETMIA-MIA
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 20 market(s), e.g. KXNFLGAME-26NOV08DETMIA-MIA, KXNFLSPREAD-26NOV08DETMIA-MIA5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLBOTH-26NOV08DETMIA-14, KXNFLSPREAD-26NOV08DETMIA-DET3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 188 market(s), e.g. KXNFL1HFT-26NOV08DETMIA-TIEDET, KXNFL1HFT-26NOV08DETMIA-MIADET
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 39 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV08DETMIA-DET3, KXNFL2QTOTAL-26NOV08DETMIA-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 27.0%  _(final margin within one score (8 points) either way; total within 10 of the centre 50.5 (median favourite-oriented margin +3, median total 51))_
2. favourite controls / normal scoring — 23.0%  _(DET (favourite) wins by more than one score; total within 10 of the centre 50.5 (median favourite-oriented margin +16, median total 50))_
3. competitive / high scoring — 11.4%  _(final margin within one score (8 points) either way; total 60.5+ (centre 50.5) (median favourite-oriented margin +3, median total 69))_
4. competitive / low scoring — 10.0%  _(final margin within one score (8 points) either way; total 40.5 or fewer (centre 50.5) (median favourite-oriented margin +3, median total 35))_
5. favourite controls / high scoring — 9.5%  _(DET (favourite) wins by more than one score; total 60.5+ (centre 50.5) (median favourite-oriented margin +15, median total 66))_
   Other — 19.1%

Marginal events (overlapping): one_score 48.4% · blowout_17 23.5% · favorite_wins 73.1% · favorite_controls 41.1% · upset 26.7% · shootout 23.7% · low_scoring 20.1% · low_possession 9.6% · high_volume_passing 1.8% · run_heavy_control 21.0%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.60 mph, gusts 5.40, precip prob 3%, temp 82F, forecast retrieved 2026-11-07T14:56:30+00:00 (27.06 h before kickoff)._

**`KXNFLTD-26NOV08DETMIA-DETASTBROWN14-1`** Amon-Ra St. Brown touchdowns 1
- MODEL / MARKET: football 33.3% · market 50.5% · reconciled 46.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 23.1% · failure mass 100.0% · win-contribution HHI 0.180
- THESIS DEPENDENCY with `KXNFLRECYDS-26NOV08DETMIA-DETASTBROWN14-60`: cash correlation 0.337 · joint cash 23.6% · Jaccard of winning rows 0.416 · shared failure 43.2%

**`KXNFLTD-26NOV08DETMIA-DETJGIBBS0-1`** Jahmyr Gibbs touchdowns 1
- MODEL / MARKET: football 74.0% · market 77.5% · reconciled 74.9%
- SCRIPT ROBUSTNESS: P50 mass 98.5% · P55 mass 92.3% · P60 mass 82.3% · major-script floor 58.7% · failure mass 1.5% · win-contribution HHI 0.180

**`KXNFLTD-26NOV08DETMIA-DETJGOFF16-1`** Jared Goff touchdowns 1
- MODEL / MARKET: football 12.4% · market 6.5% · reconciled 8.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.4% · failure mass 100.0% · win-contribution HHI 0.197

**`KXNFLTD-26NOV08DETMIA-DETJGIBBS0-2`** Jahmyr Gibbs touchdowns 2
- MODEL / MARKET: football 38.9% · market 38.5% · reconciled 40.2%
- SCRIPT ROBUSTNESS: P50 mass 43.9% · P55 mass 9.5% · P60 mass 9.5% · major-script floor 15.0% · failure mass 56.1% · win-contribution HHI 0.204
- THESIS DEPENDENCY with `KXNFLTEAMTOTAL-26NOV08DETMIA-DET29`: cash correlation 0.322 · joint cash 28.2% · Jaccard of winning rows 0.447 · shared failure 37.0%

_389 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 39 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Isiah Pacheco (RB, DET) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Cade Mays (C, DET) — Out [high] · **CHANGED from Active** — ruled out
- D.J. Reed (CB, DET) — Out [high] · **NEW** — ruled out
- DJ Wonnum (LB, DET) — Out [high] · **CHANGED from Active** — ruled out
- Darrell Baker Jr. (CB, MIA) — Out [high] · **NEW** — ruled out
- Jack Campbell (LB, DET) — Out [high] · **CHANGED from Active** — ruled out
- Jimmy Rolder (LB, DET) — Injured Reserve [high] · **NEW** — ruled out
- Kerby Joseph (S, DET) — Out [high] — ruled out

**Questionable / Doubtful (6)** — resolves at the inactive release, T−90m

- Amon-Ra St. Brown (WR, DET) — Questionable [high]
- Jacob Saylors (RB, DET) — Questionable [high]
- Jaylen Wright (RB, MIA) — Questionable [high]
- Kaytron Allen (RB, MIA) — Questionable [high]
- Sione Vaki (RB, DET) — Questionable [high]
- Malik Herring (DE, MIA) — Questionable [high]

### WEATHER

- Mostly Sunny · 82°F · wind 6 mph NE · precip 3%
- forecast vintage 2026-11-07T14:56:36+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 53 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jared Goff | DET | attempts | 31.2 | 31.0 | 26.0 | 37.0 | 17.0 | 45.0 | 31.6 | 31.0 | 31.2 | 31.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jahmyr Gibbs | DET | carries | 21.6 | 21.0 | 16.0 | 27.0 | 8.0 | 36.0 | 20.6 | 20.0 | 21.6 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Sione Vaki | DET | carries | 4.3 | 2.0 | 0.0 | 7.0 | 0.0 | 15.0 | 5.9 | 5.0 | 4.3 | 2.0 | -- | 0.78 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jared Goff | DET | completions | 22.0 | 22.0 | 18.0 | 26.0 | 12.0 | 32.0 | 23.1 | 22.0 | 22.0 | 22.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jared Goff | DET | passing_tds | 1.8 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.1 | 2.0 | 2.1 | 2.0 | 0.00 | 0.97 | 1 | PRICED |
| Jared Goff | DET | passing_yards | 244.2 | 240.0 | 188.0 | 297.0 | 114.0 | 389.0 | 262.8 | 258.0 | 262.8 | 259.0 | 0.00 | 0.97 | 10 | PRICED |
| Amon-Ra St. Brown | DET | receiving_yards | 62.2 | 55.0 | 11.0 | 95.0 | 0.0 | 164.0 | 82.0 | 75.0 | 81.7 | 73.0 | 0.00 | 0.78 | 13 | PRICED |
| Jameson Williams | DET | receiving_yards | 56.6 | 45.0 | 19.0 | 82.0 | 0.0 | 154.0 | 58.2 | 50.0 | 58.2 | 46.0 | 0.00 | 0.97 | 13 | PRICED |

_8 of 53 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 53 of 85 listed player/stat groups simulated and exposed, 32 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26NOV08DETMIA-MIAOGORDON0-40` | Ollie Gordon II | 40.0 | 0.83 | 0.85 | 0.11 | -0.715 |
| `KXNFLRSHYDS-26NOV08DETMIA-MIAOGORDON0-50` | Ollie Gordon II | 50.0 | 0.73 | 0.75 | 0.08 | -0.658 |
| `KXNFLRSHATT-26NOV08DETMIA-MIAOGORDON0-14` | Ollie Gordon II | 14.0 | 0.71 | 0.73 | 0.10 | -0.604 |
| `KXNFLRSHYDS-26NOV08DETMIA-DETJGIBBS0-70` | Jahmyr Gibbs | 70.0 | 0.75 | 0.78 | 0.18 | -0.569 |
| `KXNFLRSHYDS-26NOV08DETMIA-MIAOGORDON0-60` | Ollie Gordon II | 60.0 | 0.61 | 0.63 | 0.05 | -0.565 |
| `KXNFLREC-26NOV08DETMIA-MIAGDULCICH85-2` | Greg Dulcich | 2.0 | 0.89 | 0.92 | 0.32 | -0.563 |

_Ranked 364 tradable markets; 35 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Isiah Pacheco (RB, DET) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 5 skill players are Questionable (Amon-Ra St. Brown (WR), Jacob Saylors (RB), Sione Vaki (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLRECYDS-26NOV08DETMIA-DETSLAPORTA87-70 moved +0.160 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.715 on KXNFLRSHYDS-26NOV08DETMIA-MIAOGORDON0-40 (Ollie Gordon II). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.658 on KXNFLRSHYDS-26NOV08DETMIA-MIAOGORDON0-50 (Ollie Gordon II). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26NOV08DETMIA-MIAGDULCICH85-2 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_DET_MIA.md`_


---

## LA @ WAS — `2026_09_LA_WAS`

- kickoff: 2026-11-08T18:00:00+00:00 (1572 minutes away) · state **PREGAME**
- venue: Northwest Stadium · roof outdoors · surface grass
- markets: 691 listed across 16 families — 360 supported, 275 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 4.38 | 4.80 |
| total | 48.30 | 48.48 |
| score | WAS 22.0 – LA 26.3 | WAS 21.8 – LA 26.6 |
| win prob WAS | 33.5% | 33.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 3.00 / total 24.12 · **2H** spread 2.73 / total 24.10 · **1Q** spread 1.40 / total 8.54 · **2Q** spread 1.39 / total 14.29 · **3Q** spread 0.92 / total 9.18 · **4Q** spread 0.83 / total 14.11

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 4.38 · total 48.30

**Game environment** (simulation, mean and middle 50%) — home margin -4.6 (-12.0–3.0) · total 49.7 (41.0–58.0) · P(one score) 51.4% · P(17+ blowout) 20.0% · P(total 10+ over centre) 23.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| WAS | 62.7 (57.0–68.0) | 32.0 (27.0–36.0) | 22.9 (18.0–27.0) | 39.2 (34.0–44.0) | 0.626 (0.561–0.693) | 0.520 / 0.688 |
| LA | 64.9 (59.0–70.0) | 35.9 (31.0–41.0) | 25.7 (21.0–30.0) | 38.2 (33.0–43.0) | 0.589 (0.521–0.657) | 0.511 / 0.684 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| WAS | 00-0037256 | RB | 3.2 (1.0–5.0) | 11.3 (7.0–15.0) | 10.7% | 49.6% | MEDIUM |
| WAS | 00-0033699 | RB | 2.0 (0.0–3.0) | 7.3 (3.0–10.0) | 6.5% | 31.8% | HIGH |
| WAS | 00-0031588 | WR | 7.7 (5.0–10.0) | 0.1 (0.0–0.0) | 25.7% | 0.4% | MEDIUM |
| WAS | 00-0039910 | QB | 0.1 (0.0–0.0) | 6.8 (5.0–8.0) | 0.4% | 4.2% | MEDIUM |
| LA | 00-0037840 | RB | 3.8 (1.0–5.0) | 14.5 (9.0–19.0) | 10.9% | 56.5% | MEDIUM |
| LA | 00-0039075 | WR | 12.6 (9.0–16.0) | 0.7 (0.0–0.0) | 36.3% | 2.5% | MEDIUM |
| LA | 00-0039738 | RB | 1.8 (0.0–3.0) | 9.3 (4.0–13.0) | 5.3% | 36.0% | HIGH |
| LA | 00-0033110 | TE | 4.6 (2.0–7.0) | 0.1 (0.0–0.0) | 13.3% | 0.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 4 market(s), e.g. KXNFLPASSATT-26NOV08LARWAS-LARMSTAFFORD9-39, KXNFLPASSYDS-26NOV08LARWAS-LARMSTAFFORD9-275
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 43 market(s), e.g. KXNFL1HFT-26NOV08LARWAS-WASWAS, KXNFL2H-26NOV08LARWAS-WAS
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV08LARWAS-WAS7, KXNFLSPREAD-26NOV08LARWAS-LAR18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLBOTH-26NOV08LARWAS-14, KXNFLGAME-26NOV08LARWAS-LAR
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 181 market(s), e.g. KXNFL1HFT-26NOV08LARWAS-TIELAR, KXNFL1HFT-26NOV08LARWAS-LARWAS
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 35 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV08LARWAS-LAR3, KXNFL2QTOTAL-26NOV08LARWAS-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.0%  _(final margin within one score (8 points) either way; total within 10 of the centre 48.3 (median favourite-oriented margin +2, median total 49))_
2. favourite controls / normal scoring — 19.0%  _(LA (favourite) wins by more than one score; total within 10 of the centre 48.3 (median favourite-oriented margin +16, median total 49))_
3. competitive / high scoring — 10.9%  _(final margin within one score (8 points) either way; total 58.3+ (centre 48.3) (median favourite-oriented margin +2, median total 66))_
4. competitive / low scoring — 9.5%  _(final margin within one score (8 points) either way; total 38.3 or fewer (centre 48.3) (median favourite-oriented margin +3, median total 34))_
5. favourite controls / high scoring — 8.5%  _(LA (favourite) wins by more than one score; total 58.3+ (centre 48.3) (median favourite-oriented margin +15, median total 65))_
   Other — 21.1%

Marginal events (overlapping): one_score 51.4% · blowout_17 20.0% · favorite_wins 66.5% · favorite_controls 35.7% · upset 33.3% · shootout 23.1% · low_scoring 19.7% · low_possession 6.3% · high_volume_passing 8.9% · run_heavy_control 14.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 9.90 mph, gusts 17.90, precip prob 0%, temp 59F, forecast retrieved 2026-11-07T14:56:30+00:00 (27.06 h before kickoff)._

**`KXNFLTD-26NOV08LARWAS-LARKWILLIAMS23-2`** Kyren Williams touchdowns 2
- MODEL / MARKET: football 19.5% · market 18.0% · reconciled 20.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 15.2% · failure mass 100.0% · win-contribution HHI 0.202

**`KXNFLTD-26NOV08LARWAS-LARKWILLIAMS23-3`** Kyren Williams touchdowns 3
- MODEL / MARKET: football 5.2% · market 3.0% · reconciled 5.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 2.5% · failure mass 100.0% · win-contribution HHI 0.236

**`KXNFLTD-26NOV08LARWAS-LARKWILLIAMS23-1`** Kyren Williams touchdowns 1
- MODEL / MARKET: football 53.9% · market 58.5% · reconciled 56.5%
- SCRIPT ROBUSTNESS: P50 mass 81.4% · P55 mass 38.4% · P60 mass 38.4% · major-script floor 50.4% · failure mass 18.6% · win-contribution HHI 0.181

**`KXNFLTD-26NOV08LARWAS-LARBCORUM24-1`** Blake Corum touchdowns 1
- MODEL / MARKET: football 34.4% · market 42.5% · reconciled 40.6%
- SCRIPT ROBUSTNESS: P50 mass 8.5% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 31.4% · failure mass 91.5% · win-contribution HHI 0.182

_335 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 38 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (13)**

- Dean Connors (RB, LA) — Injured Reserve [single_source] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Dyami Brown (WR, WAS) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Jeremy McNichols (RB, WAS) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Ronnie Rivers (RB, LA) — Injured Reserve [single_source] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Terrance Ferguson (TE, LA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Terry McLaurin (WR, WAS) — Injured Reserve [high] · **CHANGED from Out** — ruled out -- role redistributes to the depth chart behind him
- Treylon Burks (WR, WAS) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Laremy Tunsil (OT, WAS) — Injured Reserve [high] · **NEW** — ruled out
- _...and 5 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (6)** — resolves at the inactive release, T−90m

- Colby Parkinson (TE, LA) — Questionable [single_source]
- Jordan Whittington (WR, LA) — Questionable [single_source]
- Grant Stuard (LB, LA) — Questionable [single_source]
- Joe Cardona (LS, LA) — Doubtful [single_source]
- Kam Curl (S, LA) — Questionable [single_source]
- Trent McDuffie (CB, LA) — Questionable [single_source]

### WEATHER

- Sunny · 61°F · wind 12 mph W · precip 0%
- forecast vintage 2026-11-07T14:57:40+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 47 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Matthew Stafford | LA | attempts | 34.5 | 35.0 | 29.0 | 40.0 | 20.0 | 49.0 | 32.9 | 33.0 | 34.5 | 35.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kyren Williams | LA | carries | 14.5 | 14.0 | 9.0 | 19.0 | 3.0 | 28.0 | 13.8 | 13.0 | 14.5 | 14.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Blake Corum | LA | carries | 9.3 | 8.0 | 4.0 | 13.0 | 1.0 | 21.0 | 11.3 | 11.0 | 9.3 | 8.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Matthew Stafford | LA | completions | 23.6 | 24.0 | 19.0 | 28.0 | 13.0 | 34.0 | 22.4 | 22.0 | 23.6 | 24.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Matthew Stafford | LA | passing_tds | 1.8 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.9 | 2.0 | 1.9 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Matthew Stafford | LA | passing_yards | 253.7 | 250.0 | 197.0 | 307.0 | 125.0 | 399.0 | 248.7 | 243.0 | 248.7 | 245.0 | 0.00 | 0.97 | 9 | PRICED |
| Puka Nacua | LA | receiving_yards | 104.3 | 98.0 | 61.0 | 139.0 | 18.0 | 213.0 | 98.8 | 92.0 | 98.8 | 93.0 | 0.00 | 0.98 | 15 | PRICED |
| Kyren Williams | LA | receiving_yards | 23.4 | 16.0 | 4.0 | 35.0 | 0.0 | 74.0 | 24.8 | 19.0 | 24.8 | 17.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 47 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 47 of 80 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV08LARWAS-WASAWILLIAMS14-3` | Antonio Williams | 3.0 | 0.83 | 0.84 | 0.19 | -0.647 |
| `KXNFLREC-26NOV08LARWAS-LARPNACUA12-6` | Puka Nacua | 6.0 | 0.81 | 0.84 | 0.19 | -0.618 |
| `KXNFLREC-26NOV08LARWAS-WASAWILLIAMS14-2` | Antonio Williams | 2.0 | 0.92 | 0.96 | 0.32 | -0.601 |
| `KXNFLREC-26NOV08LARWAS-LARPNACUA12-7` | Puka Nacua | 7.0 | 0.70 | 0.72 | 0.10 | -0.592 |
| `KXNFLREC-26NOV08LARWAS-LARPNACUA12-5` | Puka Nacua | 5.0 | 0.90 | 0.93 | 0.33 | -0.569 |
| `KXNFLREC-26NOV08LARWAS-WASAWILLIAMS14-4` | Antonio Williams | 4.0 | 0.64 | 0.65 | 0.11 | -0.524 |

_Ranked 349 tradable markets; 11 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Dean Connors (RB, LA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Ronnie Rivers (RB, LA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Colby Parkinson (TE), Jordan Whittington (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRECYDS-26NOV08LARWAS-WASSDIGGS3-50 moved +0.170 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.647 on KXNFLREC-26NOV08LARWAS-WASAWILLIAMS14-3 (Antonio Williams). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.618 on KXNFLREC-26NOV08LARWAS-LARPNACUA12-6 (Puka Nacua). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV08LARWAS-WASAWILLIAMS14-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_LA_WAS.md`_


---

## NYG @ PHI — `2026_09_NYG_PHI`

- kickoff: 2026-11-08T18:00:00+00:00 (1572 minutes away) · state **PREGAME**
- venue: Lincoln Financial Field · roof outdoors · surface grass
- markets: 769 listed across 16 families — 382 supported, 287 no model, 48 rules unresolved, 52 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 52 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.11 | 3.14 |
| total | 39.12 | 38.73 |
| score | PHI 18.0 – NYG 21.1 | PHI 17.8 – NYG 20.9 |
| win prob PHI | 38.5% | 38.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.34 / total 20.13 · **2H** spread 1.55 / total 19.40 · **1Q** spread 0.68 / total 7.59 · **2Q** spread 0.76 / total 11.00 · **3Q** spread 0.14 / total 7.65 · **4Q** spread 0.41 / total 10.23

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 3.11 · total 39.12
- move `KXNFLTOTAL-26NOV08NYGPHI-39` -0.115
- move `KXNFLTOTAL-26NOV08NYGPHI-47` -0.110
- move `KXNFL1HTEAMTOTAL-26NOV08NYGPHI-PHI31` -0.100
- move `KXNFL3QSPREAD-26NOV08NYGPHI-NYG4` -0.095

**Game environment** (simulation, mean and middle 50%) — home margin -3.4 (-11.0–4.0) · total 40.6 (31.0–49.0) · P(one score) 53.7% · P(17+ blowout) 18.6% · P(total 10+ over centre) 23.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| PHI | 61.4 (56.0–67.0) | 32.9 (28.0–37.0) | 23.4 (18.0–28.0) | 37.4 (32.0–42.0) | 0.610 (0.543–0.677) | 0.506 / 0.672 |
| NYG | 64.3 (59.0–70.0) | 31.2 (26.0–36.0) | 28.5 (23.0–33.0) | 34.9 (29.0–40.0) | 0.542 (0.475–0.610) | 0.465 / 0.638 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| PHI | 00-0034844 | RB | 2.2 (0.0–3.0) | 15.6 (11.0–20.0) | 7.0% | 66.7% | MEDIUM |
| PHI | 00-0034351 | TE | 6.8 (4.0–9.0) | 0.5 (0.0–0.0) | 22.0% | 2.1% | HIGH |
| PHI | 00-0040867 | WR | 7.2 (4.0–10.0) | 0.1 (0.0–0.0) | 23.1% | 0.5% | HIGH |
| PHI | 00-0040586 | RB | 0.9 (0.0–1.0) | 5.0 (1.0–7.0) | 3.0% | 21.3% | HIGH |
| NYG | 00-0035250 | RB | 2.1 (0.0–3.0) | 13.1 (8.0–18.0) | 7.1% | 46.0% | MEDIUM |
| NYG | 00-0039337 | WR | 9.3 (6.0–12.0) | 0.2 (0.0–0.0) | 30.9% | 0.6% | MEDIUM |
| NYG | 00-0037838 | TE | 6.6 (4.0–9.0) | 0.2 (0.0–0.0) | 22.1% | 0.7% | HIGH |
| NYG | 00-0041376 | RB | 0.2 (0.0–0.0) | 5.7 (2.0–8.0) | 0.7% | 20.0% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 14 market(s), e.g. KXNFLPASSATT-26NOV08NYGPHI-NYGJMCCARTHY9-36, KXNFLPASSYDS-26NOV08NYGPHI-PHITMCKEE16-150
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 38 market(s), e.g. KXNFL1HFT-26NOV08NYGPHI-NYGNYG, KXNFL2H-26NOV08NYGPHI-PHI
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV08NYGPHI-PHI8, KXNFLSPREAD-26NOV08NYGPHI-PHI7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLGAME-26NOV08NYGPHI-NYG, KXNFLTEAMTOTAL-26NOV08NYGPHI-NYG18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 222 market(s), e.g. KXNFL1HFT-26NOV08NYGPHI-TIENYG, KXNFL1HFT-26NOV08NYGPHI-PHINYG
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 27 market(s), e.g. KXNFL4QTOTAL-26NOV08NYGPHI-4, KXNFLPASSYDS-26NOV08NYGPHI-PHIJMILTON10-100

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.5%  _(final margin within one score (8 points) either way; total within 10 of the centre 39.125 (median favourite-oriented margin +1, median total 39))_
2. favourite controls / normal scoring — 17.1%  _(NYG (favourite) wins by more than one score; total within 10 of the centre 39.125 (median favourite-oriented margin +15, median total 40))_
3. competitive / high scoring — 11.7%  _(final margin within one score (8 points) either way; total 49.125+ (centre 39.125) (median favourite-oriented margin +1, median total 57))_
4. competitive / low scoring — 10.6%  _(final margin within one score (8 points) either way; total 29.125 or fewer (centre 39.125) (median favourite-oriented margin +2, median total 25))_
5. underdog controls / normal scoring — 7.7%  _(PHI (underdog) wins by more than one score; total within 10 of the centre 39.125 (median favourite-oriented margin -16, median total 39))_
   Other — 21.5%

Marginal events (overlapping): one_score 53.7% · blowout_17 18.6% · favorite_wins 63.3% · favorite_controls 32.3% · upset 36.5% · shootout 23.3% · low_scoring 20.5% · low_possession 9.5% · high_volume_passing 3.5% · run_heavy_control 18.5%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 10.90 mph, gusts 18.30, precip prob 0%, temp 56F, forecast retrieved 2026-11-07T14:56:30+00:00 (27.06 h before kickoff)._

**`KXNFLTD-26NOV08NYGPHI-NYGDSINGLETARY26-1`** Devin Singletary touchdowns 1
- MODEL / MARKET: football 38.2% · market 45.5% · reconciled 43.6%
- SCRIPT ROBUSTNESS: P50 mass 36.4% · P55 mass 7.6% · P60 mass 7.6% · major-script floor 21.2% · failure mass 63.6% · win-contribution HHI 0.187

**`KXNFLTD-26NOV08NYGPHI-NYGTJOHNSON84-2`** Theo Johnson touchdowns 2
- MODEL / MARKET: football 0.9% · market 0.5% · reconciled 2.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.1% · failure mass 100.0% · win-contribution HHI 0.229

**`KXNFLTD-26NOV08NYGPHI-PHIMBROWN0-1`** Hollywood Brown touchdowns 1
- MODEL / MARKET: football 12.6% · market 9.5% · reconciled 10.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.8% · failure mass 100.0% · win-contribution HHI 0.183

**`KXNFLTD-26NOV08NYGPHI-PHIDGOEDERT88-2`** Dallas Goedert touchdowns 2
- MODEL / MARKET: football 4.2% · market 2.0% · reconciled 3.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.4% · failure mass 100.0% · win-contribution HHI 0.207

_375 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 39 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (7)**

- Britain Covey (WR, PHI) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- DeVonta Smith (WR, PHI) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Dontayvion Wicks (WR, PHI) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Tyrone Tracy Jr. (RB, NYG) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jihaad Campbell (LB, PHI) — Out [high] · **NEW** — ruled out
- Jonathan Jones (CB, PHI) — Out [high] · **NEW** — ruled out
- Michael Carter II (CB, PHI) — Out [high] · **CHANGED from Questionable** — ruled out

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Tanner McKee (QB, PHI) — Questionable [high]
- Cam Skattebo (RB, NYG) — Doubtful [high]
- Charlie Jones (WR, NYG) — Questionable [high]

### WEATHER

- Sunny · 60°F · wind 10 mph W · precip 0%
- forecast vintage 2026-11-07T14:57:39+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 49 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| J.J. McCarthy | NYG | attempts | 30.0 | 30.0 | 25.0 | 35.0 | 17.0 | 43.0 | 30.0 | 30.0 | 30.0 | 30.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Devin Singletary | NYG | carries | 13.1 | 12.0 | 8.0 | 18.0 | 2.0 | 26.0 | 16.3 | 15.0 | 13.1 | 12.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| J.J. McCarthy | NYG | completions | 18.2 | 18.0 | 15.0 | 22.0 | 9.0 | 27.0 | 18.0 | 18.0 | 18.2 | 18.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| J.J. McCarthy | NYG | passing_tds | 1.2 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.2 | 1.0 | 1.2 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| J.J. McCarthy | NYG | passing_yards | 224.7 | 220.0 | 169.0 | 275.0 | 100.0 | 366.0 | 216.9 | 211.0 | 216.9 | 212.0 | 0.00 | 0.97 | 9 | PRICED |
| Malik Nabers | NYG | receiving_yards | 77.7 | 69.0 | 39.0 | 107.0 | 7.0 | 176.0 | 79.7 | 72.0 | 79.7 | 71.0 | 0.00 | 0.98 | 14 | PRICED |
| Isaiah Likely | NYG | receiving_yards | 50.0 | 42.0 | 20.0 | 71.0 | 0.0 | 126.0 | 49.6 | 43.0 | 49.6 | 42.0 | 0.00 | 0.98 | 12 | PRICED |
| Malachi Fields | NYG | receiving_yards | 34.9 | 25.0 | 7.0 | 52.0 | 0.0 | 107.0 | 30.9 | 23.0 | 30.9 | 22.0 | 0.00 | 0.97 | 11 | PRICED |

_8 of 49 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 49 of 85 listed player/stat groups simulated and exposed, 36 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV08NYGPHI-NYGILIKELY9-2` | Isaiah Likely | 2.0 | 0.92 | 0.95 | 0.30 | -0.620 |
| `KXNFLREC-26NOV08NYGPHI-NYGILIKELY9-3` | Isaiah Likely | 3.0 | 0.79 | 0.82 | 0.18 | -0.619 |
| `KXNFLRECYDS-26NOV08NYGPHI-NYGILIKELY9-20` | Isaiah Likely | 20.0 | 0.82 | 0.84 | 0.21 | -0.609 |
| `KXNFLRECYDS-26NOV08NYGPHI-NYGILIKELY9-25` | Isaiah Likely | 25.0 | 0.76 | 0.78 | 0.16 | -0.596 |
| `KXNFLREC-26NOV08NYGPHI-NYGMNABERS1-4` | Malik Nabers | 4.0 | 0.79 | 0.82 | 0.21 | -0.584 |
| `KXNFLRECYDS-26NOV08NYGPHI-NYGILIKELY9-30` | Isaiah Likely | 30.0 | 0.69 | 0.70 | 0.13 | -0.560 |

_Ranked 346 tradable markets; 36 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Tyrone Tracy Jr. (RB, NYG) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Britain Covey (WR, PHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Charlie Jones (WR), Tanner McKee (QB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLPASSYDS-26NOV08NYGPHI-PHITMCKEE16-125 moved -0.495 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.620 on KXNFLREC-26NOV08NYGPHI-NYGILIKELY9-2 (Isaiah Likely). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.619 on KXNFLREC-26NOV08NYGPHI-NYGILIKELY9-3 (Isaiah Likely). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV08NYGPHI-NYGILIKELY9-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_NYG_PHI.md`_


---

## NYJ @ KC — `2026_09_NYJ_KC`

- kickoff: 2026-11-08T18:00:00+00:00 (1572 minutes away) · state **PREGAME**
- venue: GEHA Field at Arrowhead Stadium · roof outdoors · surface grass
- markets: 807 listed across 16 families — 442 supported, 309 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -9.60 | -10.21 |
| total | 48.38 | 48.35 |
| score | KC 29.0 – NYJ 19.4 | KC 29.3 – NYJ 19.1 |
| win prob KC | 80.5% | 81.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -6.50 / total 24.18 · **2H** spread -4.17 / total 23.60 · **1Q** spread -3.03 / total 8.59 · **2Q** spread -3.50 / total 14.43 · **3Q** spread -2.66 / total 9.30 · **4Q** spread -2.39 / total 13.86

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -9.60 · total 48.38
- move `KXNFL1HTEAMTOTAL-26NOV08NYJKC-KC14` -0.155
- move `KXNFLGAME-26NOV08NYJKC-KC` +0.145
- move `KXNFLGAME-26NOV08NYJKC-NYJ` -0.135
- move `KXNFLTOTAL-26NOV08NYJKC-26` +0.110

**Game environment** (simulation, mean and middle 50%) — home margin 9.6 (2.0–17.0) · total 49.4 (40.0–57.0) · P(one score) 38.4% · P(17+ blowout) 27.1% · P(total 10+ over centre) 23.0%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| KC | 63.7 (58.0–69.0) | 33.3 (28.0–38.0) | 24.8 (20.0–30.0) | 37.8 (32.0–43.0) | 0.594 (0.525–0.664) | 0.531 / 0.723 |
| NYJ | 60.5 (55.0–66.0) | 33.4 (29.0–38.0) | 22.8 (18.0–27.0) | 37.3 (32.0–42.0) | 0.617 (0.552–0.682) | 0.482 / 0.665 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| KC | 00-0038134 | RB | 4.0 (2.0–6.0) | 18.3 (13.0–23.0) | 12.8% | 73.8% | MEDIUM |
| KC | 00-0039067 | WR | 6.1 (3.0–8.0) | 0.1 (0.0–0.0) | 19.2% | 0.4% | HIGH |
| KC | 00-0030506 | TE | 5.6 (3.0–8.0) | 0.0 (0.0–0.0) | 17.8% | 0.1% | HIGH |
| KC | 00-0039894 | WR | 5.3 (3.0–7.0) | 0.2 (0.0–0.0) | 16.9% | 0.7% | HIGH |
| NYJ | 00-0039794 | RB | 3.6 (1.0–5.0) | 8.6 (4.0–12.0) | 11.2% | 37.7% | MEDIUM |
| NYJ | 00-0038120 | RB | 2.7 (1.0–4.0) | 9.2 (5.0–13.0) | 8.4% | 40.2% | MEDIUM |
| NYJ | 00-0039890 | WR | 6.1 (3.0–8.0) | 0.1 (0.0–0.0) | 18.9% | 0.2% | HIGH |
| NYJ | 00-0040736 | TE | 4.9 (2.0–7.0) | 0.0 (0.0–0.0) | 15.2% | 0.0% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 10 market(s), e.g. KXNFLPASSATT-26NOV08NYJKC-KCPMAHOMES15-37, KXNFLPASSCOMP-26NOV08NYJKC-KCPMAHOMES15-27
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 47 market(s), e.g. KXNFL3Q-26NOV08NYJKC-NYJ, KXNFLFFPTS-26NOV08NYJKC-KCKWALKER9-22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 15 market(s), e.g. KXNFLGAME-26NOV08NYJKC-NYJ, KXNFLSPREAD-26NOV08NYJKC-KC21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLSPREAD-26NOV08NYJKC-KC5, KXNFLTEAMTOTAL-26NOV08NYJKC-NYJ15
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 215 market(s), e.g. KXNFL1HFT-26NOV08NYJKC-NYJNYJ, KXNFL1HFT-26NOV08NYJKC-NYJKC
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 37 market(s), e.g. KXNFL4QTOTAL-26NOV08NYJKC-4, KXNFLPASSYDS-26NOV08NYJKC-NYJGSMITH7-125

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 30.9%  _(KC (favourite) wins by more than one score; total within 10 of the centre 48.375 (median favourite-oriented margin +16, median total 49))_
2. competitive / normal scoring — 21.8%  _(final margin within one score (8 points) either way; total within 10 of the centre 48.375 (median favourite-oriented margin +3, median total 48))_
3. favourite controls / high scoring — 12.8%  _(KC (favourite) wins by more than one score; total 58.375+ (centre 48.375) (median favourite-oriented margin +17, median total 66))_
4. favourite controls / low scoring — 11.0%  _(KC (favourite) wins by more than one score; total 38.375 or fewer (centre 48.375) (median favourite-oriented margin +15, median total 34))_
5. competitive / high scoring — 8.6%  _(final margin within one score (8 points) either way; total 58.375+ (centre 48.375) (median favourite-oriented margin +3, median total 64))_
   Other — 15.0%

Marginal events (overlapping): one_score 38.4% · blowout_17 27.1% · favorite_wins 79.6% · favorite_controls 54.7% · upset 20.3% · shootout 23.0% · low_scoring 20.8% · low_possession 12.7% · high_volume_passing 6.9% · run_heavy_control 14.1%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.20 mph, gusts 8.30, precip prob 0%, temp 57F, forecast retrieved 2026-11-07T14:56:30+00:00 (27.06 h before kickoff)._

**`KXNFLTD-26NOV08NYJKC-NYJIDAVIS32-1`** Isaiah Davis touchdowns 1
- MODEL / MARKET: football 8.0% · market 3.5% · reconciled 6.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.2% · failure mass 100.0% · win-contribution HHI 0.168

**`KXNFLTD-26NOV08NYJKC-KCKWALKER9-3`** Kenneth Walker III touchdowns 3
- MODEL / MARKET: football 8.5% · market 6.5% · reconciled 8.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.0% · failure mass 100.0% · win-contribution HHI 0.307

**`KXNFLTD-26NOV08NYJKC-NYJTPATRICK17-2`** Tim Patrick touchdowns 2
- MODEL / MARKET: football 0.6% · market 0.5% · reconciled 2.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.0% · failure mass 100.0% · win-contribution HHI 0.181

**`KXNFLTD-26NOV08NYJKC-NYJOCOOPER11-1`** Omar Cooper Jr. touchdowns 1
- MODEL / MARKET: football 15.2% · market 23.5% · reconciled 21.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.7% · failure mass 100.0% · win-contribution HHI 0.178

_431 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 42 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Garrett Wilson (WR, NYJ) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Max Mitchell (OT, NYJ) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out
- L'Jarius Sneed (CB, KC) — Injured Reserve [high] · **CHANGED from Active** — ruled out
- Mansoor Delane (CB, KC) — Out [high] · **NEW** — ruled out
- Omarr Norman-Lott (DT, KC) — Out [high] · **NEW** — ruled out
- Peter Woods (DT, KC) — Out [high] · **NEW** — ruled out
- T'Vondre Sweat (DT, NYJ) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out
- Trevin Wallace (LB, NYJ) — Out [high] · **NEW** — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Nikko Remigio (WR, KC) — Questionable [high]
- Harrison Phillips (DT, NYJ) — Questionable [high]
- Joseph Ossai (DE, NYJ) — Questionable [high]
- Nahshon Wright (CB, NYJ) — Questionable [high]

### WEATHER

- Sunny · 60°F · wind 5 mph W · precip 0%
- forecast vintage 2026-11-07T14:56:34+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 65 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Patrick Mahomes | KC | attempts | 32.1 | 32.0 | 27.0 | 38.0 | 19.0 | 46.0 | 32.0 | 32.0 | 32.1 | 32.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kenneth Walker III | KC | carries | 18.3 | 18.0 | 13.0 | 23.0 | 6.0 | 32.0 | 20.1 | 20.0 | 18.3 | 18.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | carries | 4.3 | 4.0 | 2.0 | 5.0 | 1.0 | 9.0 | 3.5 | 3.0 | 4.3 | 4.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | completions | 21.9 | 22.0 | 18.0 | 26.0 | 12.0 | 32.0 | 21.9 | 22.0 | 21.9 | 22.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | passing_tds | 2.0 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.1 | 2.0 | 2.1 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Patrick Mahomes | KC | passing_yards | 235.2 | 231.0 | 181.0 | 285.0 | 114.0 | 372.0 | 249.0 | 244.0 | 249.0 | 245.0 | 0.00 | 0.97 | 10 | PRICED |
| Rashee Rice | KC | receiving_yards | 49.0 | 41.0 | 19.0 | 70.0 | 0.0 | 125.0 | 65.1 | 58.0 | 65.0 | 54.0 | 0.00 | 0.97 | 13 | PRICED |
| Travis Kelce | KC | receiving_yards | 46.5 | 38.0 | 17.0 | 67.0 | 0.0 | 121.0 | 51.9 | 45.0 | 51.9 | 42.0 | 0.00 | 0.97 | 11 | PRICED |

_8 of 65 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 65 of 106 listed player/stat groups simulated and exposed, 41 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26NOV08NYJKC-KCKWALKER9-17` | Kenneth Walker III | 17.0 | 0.74 | 0.77 | 0.08 | -0.657 |
| `KXNFLRSHYDS-26NOV08NYJKC-KCKWALKER9-60` | Kenneth Walker III | 60.0 | 0.81 | 0.82 | 0.22 | -0.594 |
| `KXNFLRSHYDS-26NOV08NYJKC-KCKWALKER9-50` | Kenneth Walker III | 50.0 | 0.88 | 0.90 | 0.31 | -0.570 |
| `KXNFLRECYDS-26NOV08NYJKC-NYJTPATRICK17-10` | Tim Patrick | 10.0 | 0.56 | 0.58 | 0.01 | -0.553 |
| `KXNFLRSHYDS-26NOV08NYJKC-KCKWALKER9-70` | Kenneth Walker III | 70.0 | 0.71 | 0.73 | 0.16 | -0.552 |
| `KXNFLREC-26NOV08NYJKC-NYJOCOOPER11-3` | Omar Cooper Jr. | 3.0 | 0.74 | 0.79 | 0.18 | -0.552 |

_Ranked 398 tradable markets; 44 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Garrett Wilson (WR, NYJ) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 1 skill players are Questionable (Nikko Remigio (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFL1HTEAMTOTAL-26NOV08NYJKC-KC14 moved -0.155 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.657 on KXNFLRSHATT-26NOV08NYJKC-KCKWALKER9-17 (Kenneth Walker III). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.594 on KXNFLRSHYDS-26NOV08NYJKC-KCKWALKER9-60 (Kenneth Walker III). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLRSHYDS-26NOV08NYJKC-KCKWALKER9-50 sits at a market price of 0.88 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_NYJ_KC.md`_


---

## HOU @ LAC — `2026_09_HOU_LAC`

- kickoff: 2026-11-08T21:05:00+00:00 (1757 minutes away) · state **PREGAME**
- venue: SoFi Stadium · roof dome · surface matrixturf
- markets: 801 listed across 16 families — 428 supported, 301 no model, 48 rules unresolved, 24 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 24 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 5.67 | 5.84 |
| total | 41.12 | 41.45 |
| score | LAC 17.7 – HOU 23.4 | LAC 17.8 – HOU 23.6 |
| win prob LAC | 30.5% | 29.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 3.21 / total 20.48 · **2H** spread 2.83 / total 20.16 · **1Q** spread 1.48 / total 7.71 · **2Q** spread 1.50 / total 11.72 · **3Q** spread 0.68 / total 7.97 · **4Q** spread 1.04 / total 10.92

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 5.67 · total 41.12
- move `KXNFLSPREAD-26NOV08HOULAC-HOU3` +0.100

**Game environment** (simulation, mean and middle 50%) — home margin -5.7 (-13.0–2.0) · total 42.5 (33.0–51.0) · P(one score) 49.7% · P(17+ blowout) 21.9% · P(total 10+ over centre) 23.0%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| LAC | 62.2 (57.0–68.0) | 30.5 (26.0–35.0) | 24.4 (19.0–29.0) | 37.3 (32.0–42.0) | 0.600 (0.535–0.666) | 0.492 / 0.657 |
| HOU | 62.3 (57.0–68.0) | 31.4 (26.0–36.0) | 26.8 (22.0–31.0) | 34.5 (29.0–40.0) | 0.555 (0.487–0.623) | 0.482 / 0.657 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| LAC | 00-0040666 | RB | 1.9 (0.0–3.0) | 11.1 (6.0–15.0) | 6.6% | 45.7% | MEDIUM |
| LAC | 00-0039391 | RB | 1.8 (0.0–3.0) | 6.6 (2.0–9.0) | 6.1% | 26.9% | HIGH |
| LAC | 00-0038454 | RB | 2.1 (0.0–3.0) | 4.0 (1.0–6.0) | 7.1% | 16.6% | HIGH |
| LAC | 00-0036355 | QB | 0.2 (0.0–0.0) | 5.3 (3.0–7.0) | 0.6% | 6.0% | HIGH |
| HOU | 00-0040583 | RB | 2.1 (0.0–3.0) | 13.0 (8.0–18.0) | 7.2% | 48.7% | MEDIUM |
| HOU | 00-0035685 | RB | 1.1 (0.0–2.0) | 7.1 (3.0–10.0) | 3.6% | 26.7% | HIGH |
| HOU | 00-0036554 | WR | 5.9 (3.0–8.0) | 0.2 (0.0–0.0) | 19.9% | 0.8% | HIGH |
| HOU | 00-0034383 | TE | 4.3 (2.0–6.0) | 0.0 (0.0–0.0) | 14.6% | 0.0% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 11 market(s), e.g. KXNFLPASSCOMP-26NOV08HOULAC-LACJHERBERT10-24, KXNFLRSHYDS-26NOV08HOULAC-LACKMITCHELL34-20
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 48 market(s), e.g. KXNFL1HFT-26NOV08HOULAC-LACLAC, KXNFL4Q-26NOV08HOULAC-LAC
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26NOV08HOULAC-HOU21, KXNFLTEAMTOTAL-26NOV08HOULAC-LAC25
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLGAME-26NOV08HOULAC-HOU, KXNFLSPREAD-26NOV08HOULAC-HOU3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 220 market(s), e.g. KXNFL1HFT-26NOV08HOULAC-HOULAC, KXNFL1HTEAMTOTAL-26NOV08HOULAC-HOU21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 26 market(s), e.g. KXNFL2QTOTAL-26NOV08HOULAC-4, KXNFL4QTOTAL-26NOV08HOULAC-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 28.6%  _(final margin within one score (8 points) either way; total within 10 of the centre 41.125 (median favourite-oriented margin +3, median total 41))_
2. favourite controls / normal scoring — 20.8%  _(HOU (favourite) wins by more than one score; total within 10 of the centre 41.125 (median favourite-oriented margin +16, median total 42))_
3. competitive / high scoring — 10.7%  _(final margin within one score (8 points) either way; total 51.125+ (centre 41.125) (median favourite-oriented margin +3, median total 59))_
4. competitive / low scoring — 10.3%  _(final margin within one score (8 points) either way; total 31.125 or fewer (centre 41.125) (median favourite-oriented margin +4, median total 27))_
5. favourite controls / low scoring — 9.2%  _(HOU (favourite) wins by more than one score; total 31.125 or fewer (centre 41.125) (median favourite-oriented margin +16, median total 26))_
   Other — 20.3%

Marginal events (overlapping): one_score 49.7% · blowout_17 21.9% · favorite_wins 70.0% · favorite_controls 38.8% · upset 29.7% · shootout 23.0% · low_scoring 21.1% · low_possession 12.0% · high_volume_passing 1.8% · run_heavy_control 16.8%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.50 mph, gusts 5.10, precip prob 0%, temp 90F, forecast retrieved 2026-11-07T14:56:30+00:00 (30.14 h before kickoff)._

**`KXNFLTD-26NOV08HOULAC-HOUKBOUTTE14-1`** Kayshon Boutte touchdowns 1
- MODEL / MARKET: football 12.1% · market 10.0% · reconciled 18.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.0% · failure mass 100.0% · win-contribution HHI 0.186

**`KXNFLTD-26NOV08HOULAC-HOUWMARKS4-1`** Woody Marks touchdowns 1
- MODEL / MARKET: football 36.4% · market 44.5% · reconciled 42.4%
- SCRIPT ROBUSTNESS: P50 mass 8.8% · P55 mass 8.8% · P60 mass 0.0% · major-script floor 21.3% · failure mass 91.2% · win-contribution HHI 0.182

**`KXNFLTD-26NOV08HOULAC-HOUDSCHULTZ86-1`** Dalton Schultz touchdowns 1
- MODEL / MARKET: football 17.0% · market 25.5% · reconciled 23.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.4% · failure mass 100.0% · win-contribution HHI 0.185

**`KXNFLTD-26NOV08HOULAC-LACKVIDAL28-1`** Kimani Vidal touchdowns 1
- MODEL / MARKET: football 20.4% · market 14.5% · reconciled 16.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 12.7% · failure mass 100.0% · win-contribution HHI 0.176

_418 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 43 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- David Montgomery (RB, HOU) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- David Njoku (TE, LAC) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Jaylin Noel (WR, HOU) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Deane Leonard (CB, LAC) — Out [high] · **NEW** — ruled out
- Denzel Perryman (LB, LAC) — Injured Reserve [high] — ruled out
- Derwin James Jr. (S, LAC) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out
- Kendall Williamson (S, LAC) — Out [high] · **CHANGED from Active** — ruled out
- Reed Blankenship (S, HOU) — Out [high] · **CHANGED from Questionable** — ruled out

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Brenen Thompson (WR, LAC) — Doubtful [high]
- Kayode Awosika (G, LAC) — Doubtful [high]

### WEATHER

fixed-roof stadium (SoFi Stadium) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 65 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C.J. Stroud | HOU | attempts | 30.2 | 30.0 | 25.0 | 35.0 | 17.0 | 43.0 | 32.2 | 32.0 | 30.2 | 30.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Woody Marks | HOU | carries | 13.0 | 12.0 | 8.0 | 18.0 | 2.0 | 26.0 | 17.4 | 16.0 | 13.0 | 12.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| C.J. Stroud | HOU | completions | 19.0 | 19.0 | 15.0 | 23.0 | 10.0 | 28.0 | 21.7 | 21.0 | 19.0 | 19.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| C.J. Stroud | HOU | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.97 | 5 | PRICED |
| C.J. Stroud | HOU | passing_yards | 224.0 | 219.0 | 169.0 | 274.0 | 101.0 | 363.0 | 253.4 | 248.0 | 253.3 | 248.0 | 0.00 | 0.97 | 9 | PRICED |
| Nico Collins | HOU | receiving_yards | 52.1 | 43.0 | 18.0 | 75.0 | 0.0 | 137.0 | 75.0 | 67.0 | 74.8 | 62.0 | 0.00 | 0.98 | 13 | PRICED |
| Dalton Schultz | HOU | receiving_yards | 33.0 | 25.0 | 9.0 | 48.0 | 0.0 | 94.0 | 38.5 | 34.0 | 38.5 | 30.0 | 0.00 | 0.98 | 1 | PRICED |
| Xavier Hutchinson | HOU | receiving_yards | 30.2 | 21.0 | 5.0 | 45.0 | 0.0 | 95.0 | 27.8 | 21.0 | 27.8 | 19.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 65 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 65 of 109 listed player/stat groups simulated and exposed, 44 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV08HOULAC-HOUNCOLLINS12-4` | Nico Collins | 4.0 | 0.74 | 0.77 | 0.25 | -0.493 |
| `KXNFLRSHATT-26NOV08HOULAC-LACJHERBERT10-2` | Justin Herbert | 2.0 | 0.92 | 0.94 | 0.44 | -0.470 |
| `KXNFLREC-26NOV08HOULAC-HOUDSCHULTZ86-3` | Dalton Schultz | 3.0 | 0.73 | 0.75 | 0.29 | -0.442 |
| `KXNFLREC-26NOV08HOULAC-HOUNCOLLINS12-3` | Nico Collins | 3.0 | 0.86 | 0.88 | 0.43 | -0.432 |
| `KXNFLREC-26NOV08HOULAC-HOUNCOLLINS12-5` | Nico Collins | 5.0 | 0.56 | 0.58 | 0.14 | -0.428 |
| `KXNFLRECYDS-26NOV08HOULAC-HOUWMARKS4-10` | Woody Marks | 10.0 | 0.61 | 0.63 | 0.19 | -0.416 |

_Ranked 404 tradable markets; 24 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. David Montgomery (RB, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jaylin Noel (WR, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLRSHYDS-26NOV08HOULAC-LACOHAMPTON8-30 moved +0.205 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.493 on KXNFLREC-26NOV08HOULAC-HOUNCOLLINS12-4 (Nico Collins). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.470 on KXNFLRSHATT-26NOV08HOULAC-LACJHERBERT10-2 (Justin Herbert). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLRSHATT-26NOV08HOULAC-LACJHERBERT10-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_HOU_LAC.md`_


---

## LV @ SF — `2026_09_LV_SF`

- kickoff: 2026-11-08T21:05:00+00:00 (1757 minutes away) · state **PREGAME**
- venue: Levi's Stadium · roof outdoors · surface grass
- markets: 770 listed across 16 families — 425 supported, 288 no model, 48 rules unresolved, 9 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 9 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -9.60 | -9.89 |
| total | 51.90 | 51.71 |
| score | SF 30.8 – LV 21.1 | SF 30.8 – LV 20.9 |
| win prob SF | 79.5% | 82.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -6.67 / total 27.00 · **2H** spread -4.28 / total 25.73 · **1Q** spread -2.75 / total 9.74 · **2Q** spread -3.88 / total 15.73 · **3Q** spread -2.70 / total 10.23 · **4Q** spread -2.29 / total 14.58

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -9.60 · total 51.90
- move `KXNFLGAME-26NOV08LVSF-SF` +0.120
- move `KXNFLGAME-26NOV08LVSF-LV` -0.115

**Game environment** (simulation, mean and middle 50%) — home margin 9.6 (2.0–17.0) · total 52.7 (44.0–61.0) · P(one score) 38.4% · P(17+ blowout) 26.8% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| SF | 63.3 (58.0–69.0) | 32.3 (27.0–37.0) | 25.8 (21.0–31.0) | 36.4 (31.0–42.0) | 0.575 (0.508–0.644) | 0.516 / 0.702 |
| LV | 61.7 (56.0–67.0) | 36.7 (32.0–41.0) | 22.0 (17.0–26.0) | 39.3 (34.0–44.0) | 0.638 (0.574–0.704) | 0.494 / 0.685 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| SF | 00-0033280 | RB | 6.2 (3.0–8.0) | 11.8 (7.0–16.0) | 19.8% | 45.8% | MEDIUM |
| SF | 00-0041052 | RB | 1.3 (0.0–2.0) | 8.9 (4.0–13.0) | 4.2% | 34.5% | HIGH |
| SF | 00-0033288 | TE | 7.1 (4.0–10.0) | 0.0 (0.0–0.0) | 22.8% | 0.1% | HIGH |
| SF | 00-0036261 | WR | 5.9 (3.0–8.0) | 0.0 (0.0–0.0) | 18.8% | 0.0% | HIGH |
| LV | 00-0040122 | RB | 4.4 (2.0–6.0) | 8.9 (4.0–12.0) | 12.6% | 40.4% | MEDIUM |
| LV | 00-0040878 | RB | 1.0 (0.0–1.0) | 9.5 (5.0–13.0) | 2.9% | 43.2% | MEDIUM |
| LV | 00-0039338 | TE | 8.1 (5.0–11.0) | 0.0 (0.0–0.0) | 23.1% | 0.1% | MEDIUM |
| LV | 00-0038563 | WR | 4.8 (2.0–7.0) | 0.2 (0.0–0.0) | 13.6% | 1.1% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 13 market(s), e.g. KXNFLPASSATT-26NOV08LVSF-SFBPURDY13-36, KXNFLPASSCOMP-26NOV08LVSF-SFBPURDY13-27
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 49 market(s), e.g. KXNFL2H-26NOV08LVSF-LV, KXNFL3Q-26NOV08LVSF-LV
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 16 market(s), e.g. KXNFLGAME-26NOV08LVSF-LV, KXNFLSPREAD-26NOV08LVSF-SF21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLSPREAD-26NOV08LVSF-SF6, KXNFLSPREAD-26NOV08LVSF-SF7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 204 market(s), e.g. KXNFL1HFT-26NOV08LVSF-TIESF, KXNFL1HFT-26NOV08LVSF-SFLV
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 41 market(s), e.g. KXNFL2HTOTAL-26NOV08LVSF-15, KXNFL2QTOTAL-26NOV08LVSF-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 30.9%  _(SF (favourite) wins by more than one score; total within 10 of the centre 51.9 (median favourite-oriented margin +16, median total 51))_
2. competitive / normal scoring — 22.0%  _(final margin within one score (8 points) either way; total within 10 of the centre 51.9 (median favourite-oriented margin +3, median total 51))_
3. favourite controls / high scoring — 13.0%  _(SF (favourite) wins by more than one score; total 61.9+ (centre 51.9) (median favourite-oriented margin +17, median total 69))_
4. favourite controls / low scoring — 11.1%  _(SF (favourite) wins by more than one score; total 41.9 or fewer (centre 51.9) (median favourite-oriented margin +15, median total 37))_
5. competitive / high scoring — 8.9%  _(final margin within one score (8 points) either way; total 61.9+ (centre 51.9) (median favourite-oriented margin +2, median total 68))_
   Other — 14.1%

Marginal events (overlapping): one_score 38.4% · blowout_17 26.8% · favorite_wins 79.3% · favorite_controls 55.0% · upset 20.6% · shootout 23.8% · low_scoring 20.0% · low_possession 10.9% · high_volume_passing 11.1% · run_heavy_control 15.6%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 7.70 mph, gusts 11.60, precip prob 0%, temp 66F, forecast retrieved 2026-11-07T14:56:30+00:00 (30.14 h before kickoff)._

**`KXNFLTD-26NOV08LVSF-SFGKITTLE85-1`** George Kittle touchdowns 1
- MODEL / MARKET: football 43.8% · market 54.5% · reconciled 51.0%
- SCRIPT ROBUSTNESS: P50 mass 21.9% · P55 mass 13.0% · P60 mass 0.0% · major-script floor 38.8% · failure mass 78.1% · win-contribution HHI 0.203
- THESIS DEPENDENCY with `KXNFLPASSTDS-26NOV08LVSF-SFBPURDY13-2`: cash correlation 0.303 · joint cash 35.4% · Jaccard of winning rows 0.486 · shared failure 27.3%

**`KXNFLTD-26NOV08LVSF-LVBBOWERS89-1`** Brock Bowers touchdowns 1
- MODEL / MARKET: football 31.2% · market 43.5% · reconciled 40.2%
- SCRIPT ROBUSTNESS: P50 mass 1.9% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 13.3% · failure mass 98.1% · win-contribution HHI 0.183
- THESIS DEPENDENCY with `KXNFLPASSTDS-26NOV08LVSF-LVKCOUSINS8-2`: cash correlation 0.336 · joint cash 21.1% · Jaccard of winning rows 0.398 · shared failure 47.0%

**`KXNFLTD-26NOV08LVSF-SFCMCCAFFREY23-1`** Christian McCaffrey touchdowns 1
- MODEL / MARKET: football 61.7% · market 71.5% · reconciled 69.0%
- SCRIPT ROBUSTNESS: P50 mass 87.8% · P55 mass 65.8% · P60 mass 52.8% · major-script floor 54.2% · failure mass 12.2% · win-contribution HHI 0.209

**`KXNFLTD-26NOV08LVSF-SFJWATKINS17-1`** Jordan Watkins touchdowns 1
- MODEL / MARKET: football 13.1% · market 21.5% · reconciled 19.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.8% · failure mass 100.0% · win-contribution HHI 0.212

_415 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 43 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Brandon Aiyuk (WR, SF) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Christian Kirk (WR, SF) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- De'Zhaun Stribling (WR, SF) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Deebo Samuel Sr. (WR, SF) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Demarcus Robinson (WR, SF) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Mike Evans (WR, SF) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Nate Hobbs (CB, SF) — Injured Reserve [high] · **NEW** — ruled out
- Thomas Booker IV (DT, LV) — Out [high] · **CHANGED from Active** — ruled out

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Darien Porter (CB, LV) — Questionable [high]
- Siran Neal (S, SF) — Questionable [high]
- Upton Stout (CB, SF) — Questionable [high]

### WEATHER

- Mostly Sunny · 70°F · wind 7 mph NW · precip 0%
- forecast vintage 2026-11-07T14:57:43+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 61 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kirk Cousins | LV | attempts | 35.2 | 36.0 | 30.0 | 41.0 | 21.0 | 49.0 | 36.6 | 36.0 | 35.2 | 36.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Mike Washington Jr. | LV | carries | 9.5 | 9.0 | 5.0 | 13.0 | 1.0 | 20.0 | 9.7 | 9.0 | 9.5 | 9.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Ashton Jeanty | LV | carries | 8.9 | 8.0 | 4.0 | 12.0 | 1.0 | 20.0 | 9.1 | 9.0 | 8.9 | 8.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kirk Cousins | LV | completions | 22.2 | 22.0 | 18.0 | 26.0 | 12.0 | 32.0 | 23.4 | 23.0 | 22.2 | 22.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kirk Cousins | LV | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.7 | 1.0 | 1.7 | 2.0 | 0.00 | 0.98 | 4 | PRICED |
| Kirk Cousins | LV | passing_yards | 226.8 | 223.0 | 175.0 | 276.0 | 108.0 | 359.0 | 252.0 | 246.0 | 252.0 | 247.0 | 0.00 | 0.98 | 8 | PRICED |
| Brock Bowers | LV | receiving_yards | 59.3 | 52.0 | 27.0 | 84.0 | 0.0 | 141.0 | 81.3 | 74.0 | 81.1 | 71.0 | 0.00 | 0.97 | 13 | PRICED |
| Tre Tucker | LV | receiving_yards | 36.5 | 27.0 | 9.0 | 54.0 | 0.0 | 108.0 | 43.0 | 34.0 | 43.0 | 32.0 | 0.00 | 0.97 | 12 | PRICED |

_8 of 61 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 61 of 97 listed player/stat groups simulated and exposed, 36 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV08LVSF-LVBBOWERS89-4` | Brock Bowers | 4.0 | 0.89 | 0.92 | 0.19 | -0.690 |
| `KXNFLREC-26NOV08LVSF-LVBBOWERS89-5` | Brock Bowers | 5.0 | 0.77 | 0.80 | 0.10 | -0.666 |
| `KXNFLREC-26NOV08LVSF-SFGKITTLE85-4` | George Kittle | 4.0 | 0.80 | 0.85 | 0.18 | -0.622 |
| `KXNFLREC-26NOV08LVSF-LVAJEANTY2-3` | Ashton Jeanty | 3.0 | 0.79 | 0.84 | 0.20 | -0.598 |
| `KXNFLRECYDS-26NOV08LVSF-LVBBOWERS89-40` | Brock Bowers | 40.0 | 0.83 | 0.86 | 0.24 | -0.592 |
| `KXNFLREC-26NOV08LVSF-LVBBOWERS89-6` | Brock Bowers | 6.0 | 0.65 | 0.67 | 0.05 | -0.591 |

_Ranked 387 tradable markets; 38 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Brandon Aiyuk (WR, SF) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Christian Kirk (WR, SF) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLTEAMSACK-26NOV08LVSF-SF4 moved +0.145 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.690 on KXNFLREC-26NOV08LVSF-LVBBOWERS89-4 (Brock Bowers). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.666 on KXNFLREC-26NOV08LVSF-LVBBOWERS89-5 (Brock Bowers). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26NOV08LVSF-LVBBOWERS89-4 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_LV_SF.md`_


---

## ARI @ SEA — `2026_09_ARI_SEA`

- kickoff: 2026-11-08T21:25:00+00:00 (1777 minutes away) · state **PREGAME**
- venue: Lumen Field · roof outdoors · surface fieldturf
- markets: 770 listed across 16 families — 366 supported, 285 no model, 48 rules unresolved, 71 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 71 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -8.50 | -8.70 |
| total | 39.68 | 38.78 |
| score | SEA 24.1 – ARI 15.6 | SEA 23.7 – ARI 15.0 |
| win prob SEA | 78.5% | 80.6% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -4.68 / total 19.91 · **2H** spread -4.14 / total 19.38 · **1Q** spread -2.58 / total 7.62 · **2Q** spread -3.24 / total 11.43 · **3Q** spread -2.50 / total 7.86 · **4Q** spread -2.64 / total 10.29

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -8.50 · total 39.68
- move `KXNFLTOTAL-26NOV08ARISEA-44` -0.235
- move `KXNFLTOTAL-26NOV08ARISEA-43` -0.215
- move `KXNFLTOTAL-26NOV08ARISEA-51` -0.215
- move `KXNFLTOTAL-26NOV08ARISEA-46` -0.190

**Game environment** (simulation, mean and middle 50%) — home margin 8.7 (2.0–16.0) · total 40.7 (32.0–49.0) · P(one score) 42.8% · P(17+ blowout) 25.7% · P(total 10+ over centre) 23.0%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| SEA | 63.3 (58.0–69.0) | 29.9 (25.0–35.0) | 29.0 (24.0–34.0) | 33.2 (28.0–38.0) | 0.525 (0.455–0.596) | 0.461 / 0.645 |
| ARI | 62.7 (57.0–68.0) | 36.8 (32.0–42.0) | 21.6 (17.0–26.0) | 40.7 (35.0–46.0) | 0.650 (0.587–0.714) | 0.522 / 0.698 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| SEA | 00-0038797 | RB | 1.5 (0.0–2.0) | 9.3 (4.0–13.0) | 5.3% | 32.2% | HIGH |
| SEA | 00-0041512 | RB | 2.5 (1.0–4.0) | 8.3 (3.0–12.0) | 8.6% | 28.8% | HIGH |
| SEA | 00-0038543 | WR | 9.4 (6.0–12.0) | 0.2 (0.0–0.0) | 33.0% | 0.8% | MEDIUM |
| SEA | 00-0039165 | RB | 1.9 (0.0–3.0) | 7.8 (3.0–11.0) | 6.6% | 26.7% | HIGH |
| ARI | 00-0037263 | RB | 3.4 (1.0–5.0) | 14.3 (10.0–19.0) | 9.6% | 66.1% | MEDIUM |
| ARI | 00-0038559 | WR | 10.9 (7.0–14.0) | 1.0 (0.0–1.0) | 31.1% | 4.4% | MEDIUM |
| ARI | 00-0037744 | TE | 11.1 (7.0–14.0) | 0.0 (0.0–0.0) | 31.9% | 0.1% | MEDIUM |
| ARI | 00-0039041 | TE | 3.0 (1.0–4.0) | 0.1 (0.0–0.0) | 8.6% | 0.6% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 6 market(s), e.g. KXNFLPASSATT-26NOV08ARISEA-SEADLOCK2-33, KXNFLPASSYDS-26NOV08ARISEA-SEADLOCK2-250
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 35 market(s), e.g. KXNFLREC-26NOV08ARISEA-SEACKUPP10-8, KXNFLREC-26NOV08ARISEA-SEAZCHARBONNET26-3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 19 market(s), e.g. KXNFLGAME-26NOV08ARISEA-ARI, KXNFLSPREAD-26NOV08ARISEA-SEA24
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLTOTAL-26NOV08ARISEA-36, KXNFLSPREAD-26NOV08ARISEA-SEA4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 219 market(s), e.g. KXNFL1HFT-26NOV08ARISEA-ARISEA, KXNFL1HFT-26NOV08ARISEA-ARIARI
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 29 market(s), e.g. KXNFL1HTOTAL-26NOV08ARISEA-8, KXNFL2HTOTAL-26NOV08ARISEA-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 28.7%  _(SEA (favourite) wins by more than one score; total within 10 of the centre 39.6818 (median favourite-oriented margin +16, median total 39))_
2. competitive / normal scoring — 24.1%  _(final margin within one score (8 points) either way; total within 10 of the centre 39.6818 (median favourite-oriented margin +3, median total 39))_
3. favourite controls / high scoring — 11.7%  _(SEA (favourite) wins by more than one score; total 49.6818+ (centre 39.6818) (median favourite-oriented margin +17, median total 57))_
4. competitive / high scoring — 9.7%  _(final margin within one score (8 points) either way; total 49.6818+ (centre 39.6818) (median favourite-oriented margin +2, median total 58))_
5. favourite controls / low scoring — 9.5%  _(SEA (favourite) wins by more than one score; total 29.6818 or fewer (centre 39.6818) (median favourite-oriented margin +14, median total 24))_
   Other — 16.3%

Marginal events (overlapping): one_score 42.8% · blowout_17 25.7% · favorite_wins 78.0% · favorite_controls 49.9% · upset 21.9% · shootout 23.0% · low_scoring 20.1% · low_possession 9.0% · high_volume_passing 6.9% · run_heavy_control 23.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 11.30 mph, gusts 19.50, precip prob 9%, temp 54F, forecast retrieved 2026-11-07T14:56:30+00:00 (30.48 h before kickoff)._

**`KXNFLTD-26NOV08ARISEA-SEAEWILSON23-1`** Emanuel Wilson touchdowns 1
- MODEL / MARKET: football 31.0% · market 5.5% · reconciled 17.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 25.3% · failure mass 100.0% · win-contribution HHI 0.212

**`KXNFLTD-26NOV08ARISEA-SEAGHOLANI36-1`** George Holani touchdowns 1
- MODEL / MARKET: football 12.2% · market 7.5% · reconciled 18.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 10.4% · failure mass 100.0% · win-contribution HHI 0.209

**`KXNFLTD-26NOV08ARISEA-SEAJSMITHNJIGBA11-1`** Jaxon Smith-Njigba touchdowns 1
- MODEL / MARKET: football 42.9% · market 53.5% · reconciled 49.8%
- SCRIPT ROBUSTNESS: P50 mass 21.4% · P55 mass 21.4% · P60 mass 11.7% · major-script floor 38.7% · failure mass 78.6% · win-contribution HHI 0.204
- THESIS DEPENDENCY with `KXNFLPASSTDS-26NOV08ARISEA-SEADLOCK2-2`: cash correlation 0.397 · joint cash 28.1% · Jaccard of winning rows 0.488 · shared failure 42.3%

**`KXNFLTD-26NOV08ARISEA-SEAJPRICE8-1`** Jadarian Price touchdowns 1
- MODEL / MARKET: football 25.9% · market 35.5% · reconciled 33.1%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 21.2% · failure mass 100.0% · win-contribution HHI 0.216

_339 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 35 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (14)**

- Sam Darnold (QB, SEA) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Bam Knight (RB, ARI) — Out [single_source] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- James Conner (RB, ARI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jeremiyah Love (RB, ARI) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Kendrick Bourne (WR, ARI) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Rashid Shaheed (WR, SEA) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Charles Cross (OT, SEA) — Out [high] · **CHANGED from Doubtful** — ruled out
- Isaiah Adams (G, ARI) — Injured Reserve [high] · **NEW** — ruled out
- _...and 6 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Connor O'Toole (LB, SEA) — Questionable [high]
- Max Melton (CB, ARI) — Questionable [high]
- Walter Nolen III (DT, ARI) — Questionable [high]

### WEATHER

- Chance Rain Showers · 55°F · wind 10 mph SSW · precip 35%
- forecast vintage 2026-11-07T14:57:46+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 45 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tyler Allgeier | ARI | carries | 14.3 | 14.0 | 10.0 | 19.0 | 4.0 | 26.0 | 15.5 | 15.0 | 14.3 | 14.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Wilson | ARI | receiving_yards | 76.9 | 69.0 | 40.0 | 106.0 | 7.0 | 171.0 | 55.9 | 47.0 | 55.9 | 50.0 | 0.00 | 0.98 | 14 | PRICED |
| Trey McBride | ARI | receiving_yards | 70.6 | 64.0 | 39.0 | 95.0 | 9.0 | 152.0 | 66.5 | 59.0 | 66.5 | 60.0 | 0.00 | 0.98 | 14 | PRICED |
| Elijah Higgins | ARI | receiving_yards | 18.0 | 11.0 | 0.0 | 27.0 | 0.0 | 62.0 | 19.4 | 14.0 | 19.4 | 12.0 | 0.00 | 0.98 | 9 | PRICED |
| Tyler Allgeier | ARI | receiving_yards | 15.4 | 10.0 | 1.0 | 23.0 | 0.0 | 51.0 | 21.4 | 16.0 | 21.5 | 14.0 | 0.00 | 0.97 | 9 | PRICED |
| Reggie Virgil | ARI | receiving_yards | 13.6 | 4.0 | 0.0 | 20.0 | 0.0 | 57.0 | 20.8 | 13.0 | 20.9 | 6.0 | 0.00 | 0.97 | 8 | PRICED |
| Trey McBride | ARI | receptions | 7.9 | 7.0 | 5.0 | 10.0 | 2.0 | 15.0 | 7.2 | 7.0 | 7.2 | 7.0 | 0.00 | 0.98 | 12 | PRICED |
| Michael Wilson | ARI | receptions | 6.2 | 6.0 | 4.0 | 8.0 | 1.0 | 13.0 | 4.5 | 4.0 | 4.5 | 4.0 | 0.00 | 0.98 | 9 | PRICED |

_8 of 45 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 45 of 96 listed player/stat groups simulated and exposed, 51 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV08ARISEA-ARITMCBRIDE85-5` | Trey McBride | 5.0 | 0.81 | 0.83 | 0.16 | -0.646 |
| `KXNFLRSHYDS-26NOV08ARISEA-SEAJPRICE8-30` | Jadarian Price | 30.0 | 0.81 | 0.82 | 0.18 | -0.634 |
| `KXNFLRSHYDS-26NOV08ARISEA-SEAJPRICE8-25` | Jadarian Price | 25.0 | 0.84 | 0.85 | 0.22 | -0.626 |
| `KXNFLRECYDS-26NOV08ARISEA-ARITALLGEIER22-10` | Tyler Allgeier | 10.0 | 0.68 | 0.69 | 0.06 | -0.616 |
| `KXNFLREC-26NOV08ARISEA-ARITMCBRIDE85-4` | Trey McBride | 4.0 | 0.89 | 0.91 | 0.29 | -0.595 |
| `KXNFLREC-26NOV08ARISEA-SEAJSMITHNJIGBA11-5` | Jaxon Smith-Njigba | 5.0 | 0.82 | 0.85 | 0.23 | -0.592 |

_Ranked 314 tradable markets; 52 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Bam Knight (RB, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. James Conner (RB, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLTOTAL-26NOV08ARISEA-44 moved -0.235 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.646 on KXNFLREC-26NOV08ARISEA-ARITMCBRIDE85-5 (Trey McBride). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.634 on KXNFLRSHYDS-26NOV08ARISEA-SEAJPRICE8-30 (Jadarian Price). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26NOV08ARISEA-ARITMCBRIDE85-4 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_ARI_SEA.md`_


---

## GB @ NE — `2026_09_GB_NE`

- kickoff: 2026-11-08T21:25:00+00:00 (1777 minutes away) · state **PREGAME**
- venue: Gillette Stadium · roof outdoors · surface fieldturf
- markets: 725 listed across 16 families — 390 supported, 278 no model, 48 rules unresolved, 9 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 9 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.15 | -3.45 |
| total | 45.38 | 45.17 |
| score | NE 24.3 – GB 21.1 | NE 24.3 – GB 20.9 |
| win prob NE | 61.0% | 62.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -2.50 / total 22.80 · **2H** spread -1.58 / total 22.47 · **1Q** spread -1.07 / total 7.92 · **2Q** spread -0.76 / total 13.44 · **3Q** spread -0.03 / total 8.65 · **4Q** spread -0.45 / total 12.70

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.15 · total 45.38
- move `KXNFLTOTAL-26NOV08GBNE-57` -0.130
- move `KXNFLTOTAL-26NOV08GBNE-45` -0.125
- move `KXNFLTOTAL-26NOV08GBNE-54` -0.120
- move `KXNFLTOTAL-26NOV08GBNE-47` -0.115

**Game environment** (simulation, mean and middle 50%) — home margin 3.8 (-4.0–11.0) · total 46.6 (37.0–55.0) · P(one score) 51.9% · P(17+ blowout) 17.8% · P(total 10+ over centre) 23.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NE | 63.5 (58.0–69.0) | 31.5 (27.0–36.0) | 24.8 (20.0–30.0) | 37.7 (32.0–43.0) | 0.594 (0.528–0.663) | 0.511 / 0.685 |
| GB | 61.8 (56.0–68.0) | 36.6 (31.0–41.0) | 21.6 (17.0–26.0) | 39.5 (34.0–45.0) | 0.641 (0.577–0.707) | 0.535 / 0.707 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NE | 00-0036875 | RB | 4.9 (2.0–7.0) | 15.2 (10.0–20.0) | 16.2% | 61.1% | MEDIUM |
| NE | 00-0039851 | QB | 0.2 (0.0–0.0) | 6.4 (4.0–8.0) | 0.8% | 6.8% | MEDIUM |
| NE | 00-0040556 | RB | 0.6 (0.0–1.0) | 5.8 (2.0–8.0) | 1.8% | 23.2% | HIGH |
| NE | 00-0038621 | WR | 6.0 (3.0–8.0) | 0.2 (0.0–0.0) | 19.8% | 0.9% | HIGH |
| GB | 00-0035700 | RB | 3.7 (1.0–5.0) | 11.5 (7.0–16.0) | 10.7% | 53.4% | MEDIUM |
| GB | 00-0040667 | WR | 7.9 (5.0–11.0) | 0.2 (0.0–0.0) | 22.5% | 0.7% | MEDIUM |
| GB | 00-0038124 | WR | 7.3 (4.0–10.0) | 0.1 (0.0–0.0) | 20.9% | 0.2% | HIGH |
| GB | 00-0038996 | TE | 5.6 (3.0–8.0) | 0.1 (0.0–0.0) | 16.0% | 0.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 7 market(s), e.g. KXNFLPASSATT-26NOV08GBNE-NEDMAYE10-37, KXNFLPASSCOMP-26NOV08GBNE-NEDMAYE10-25
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 52 market(s), e.g. KXNFL2H-26NOV08GBNE-GB, KXNFL2QSPREAD-26NOV08GBNE-GB7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLBOTH-26NOV08GBNE-21, KXNFLSPREAD-26NOV08GBNE-NE11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLBOTH-26NOV08GBNE-14, KXNFLGAME-26NOV08GBNE-NE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 186 market(s), e.g. KXNFL1HFT-26NOV08GBNE-GBNE, KXNFL1HTEAMTOTAL-26NOV08GBNE-NE21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 32 market(s), e.g. KXNFL2HTOTAL-26NOV08GBNE-11, KXNFL2QTOTAL-26NOV08GBNE-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.1%  _(final margin within one score (8 points) either way; total within 10 of the centre 45.375 (median favourite-oriented margin +2, median total 46))_
2. favourite controls / normal scoring — 19.5%  _(NE (favourite) wins by more than one score; total within 10 of the centre 45.375 (median favourite-oriented margin +14, median total 45))_
3. competitive / high scoring — 11.5%  _(final margin within one score (8 points) either way; total 55.375+ (centre 45.375) (median favourite-oriented margin +2, median total 63))_
4. competitive / low scoring — 11.3%  _(final margin within one score (8 points) either way; total 35.375 or fewer (centre 45.375) (median favourite-oriented margin +2, median total 30))_
5. favourite controls / high scoring — 7.9%  _(NE (favourite) wins by more than one score; total 55.375+ (centre 45.375) (median favourite-oriented margin +17, median total 62))_
   Other — 20.7%

Marginal events (overlapping): one_score 51.9% · blowout_17 17.8% · favorite_wins 64.5% · favorite_controls 33.3% · upset 35.4% · shootout 23.3% · low_scoring 20.3% · low_possession 10.4% · high_volume_passing 9.3% · run_heavy_control 11.6%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 8.80 mph, gusts 24.20, precip prob 1%, temp 50F, forecast retrieved 2026-11-07T14:56:30+00:00 (30.48 h before kickoff)._

**`KXNFLTD-26NOV08GBNE-NERSTEVENSON38-2`** Rhamondre Stevenson touchdowns 2
- MODEL / MARKET: football 16.2% · market 12.0% · reconciled 15.1%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.5% · failure mass 100.0% · win-contribution HHI 0.203

**`KXNFLTD-26NOV08GBNE-GBJJACOBS8-1`** Josh Jacobs touchdowns 1
- MODEL / MARKET: football 40.9% · market 50.5% · reconciled 47.5%
- SCRIPT ROBUSTNESS: P50 mass 23.2% · P55 mass 23.2% · P60 mass 3.9% · major-script floor 27.2% · failure mass 76.8% · win-contribution HHI 0.174

**`KXNFLTD-26NOV08GBNE-GBPSTRONG22-2`** Pierre Strong Jr. touchdowns 2
- MODEL / MARKET: football 0.7% · market 0.5% · reconciled 2.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.1% · failure mass 100.0% · win-contribution HHI 0.191

**`KXNFLTD-26NOV08GBNE-NEDMAYE10-1`** Drake Maye touchdowns 1
- MODEL / MARKET: football 26.2% · market 20.5% · reconciled 22.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 14.9% · failure mass 100.0% · win-contribution HHI 0.182

_380 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 40 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (10)**

- A.J. Brown (WR, NE) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Chris Brooks (RB, GB) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Josh Whyle (TE, GB) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Mack Hollins (WR, NE) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- TreVeyon Henderson (RB, NE) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Greg Van Roten (G, NE) — Injured Reserve [single_source] · **NEW** — ruled out
- Sean Rhyan (G, GB) — Out [high] — ruled out
- Travis Glover (OT, GB) — Out [single_source] · **CHANGED from Questionable** — ruled out
- _...and 2 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Hunter Henry (TE, NE) — Questionable [high]
- MarShawn Lloyd (RB, GB) — Questionable [high]
- Morgan Moses (OT, NE) — Questionable [high]
- Brenden Schooler (S, NE) — Questionable [high]
- Keisean Nixon (CB, GB) — Questionable [high]

### WEATHER

- Sunny · 57°F · wind 7 mph W · precip 0%
- forecast vintage 2026-11-07T14:57:45+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 52 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jordan Love | GB | attempts | 35.2 | 35.0 | 30.0 | 41.0 | 21.0 | 49.0 | 38.4 | 38.0 | 35.2 | 35.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Jacobs | GB | carries | 11.5 | 11.0 | 7.0 | 16.0 | 2.0 | 23.0 | 15.6 | 15.0 | 11.5 | 11.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jordan Love | GB | completions | 21.8 | 22.0 | 18.0 | 26.0 | 12.0 | 32.0 | 22.8 | 23.0 | 21.8 | 22.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jordan Love | GB | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.97 | 5 | PRICED |
| Jordan Love | GB | passing_yards | 248.4 | 243.0 | 191.0 | 301.0 | 118.0 | 396.0 | 276.5 | 273.0 | 276.4 | 270.0 | 0.00 | 0.97 | 9 | PRICED |
| Christian Watson | GB | receiving_yards | 65.0 | 55.0 | 25.0 | 93.0 | 0.0 | 165.0 | 77.5 | 70.0 | 77.3 | 65.0 | 0.00 | 0.98 | 14 | PRICED |
| Matthew Golden | GB | receiving_yards | 64.6 | 55.0 | 26.0 | 92.0 | 0.0 | 162.0 | 74.0 | 66.0 | 73.9 | 63.0 | 0.00 | 0.97 | 14 | PRICED |
| Tucker Kraft | GB | receiving_yards | 40.4 | 32.0 | 14.0 | 59.0 | 0.0 | 109.0 | 51.6 | 45.0 | 51.6 | 41.0 | 0.00 | 0.97 | 12 | PRICED |

_8 of 52 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 52 of 85 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRECYDS-26NOV08GBNE-GBSWILLIAMS83-10` | Savion Williams | 10.0 | 0.67 | 0.69 | 0.01 | -0.658 |
| `KXNFLREC-26NOV08GBNE-GBMGOLDEN0-3` | Matthew Golden | 3.0 | 0.88 | 0.91 | 0.22 | -0.656 |
| `KXNFLREC-26NOV08GBNE-GBMGOLDEN0-4` | Matthew Golden | 4.0 | 0.74 | 0.78 | 0.13 | -0.619 |
| `KXNFLREC-26NOV08GBNE-GBTKRAFT85-3` | Tucker Kraft | 3.0 | 0.81 | 0.84 | 0.21 | -0.596 |
| `KXNFLREC-26NOV08GBNE-GBSWILLIAMS83-2` | Savion Williams | 2.0 | 0.60 | 0.61 | 0.01 | -0.596 |
| `KXNFLRECYDS-26NOV08GBNE-GBMGOLDEN0-40` | Matthew Golden | 40.0 | 0.76 | 0.78 | 0.17 | -0.591 |

_Ranked 352 tradable markets; 38 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Josh Whyle (TE, GB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Chris Brooks (RB, GB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (MarShawn Lloyd (RB), Hunter Henry (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLTEAMSACK-26NOV08GBNE-GB5 moved +0.145 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.658 on KXNFLRECYDS-26NOV08GBNE-GBSWILLIAMS83-10 (Savion Williams). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.656 on KXNFLREC-26NOV08GBNE-GBMGOLDEN0-3 (Matthew Golden). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV08GBNE-GBTKRAFT85-2 sits at a market price of 0.93 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_GB_NE.md`_


---

## TB @ CHI — `2026_09_TB_CHI`

- kickoff: 2026-11-09T01:20:00+00:00 (2012 minutes away) · state **PREGAME**
- venue: Soldier Field · roof outdoors · surface grass
- markets: 734 listed across 16 families — 394 supported, 284 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -6.08 | -6.17 |
| total | 48.17 | 47.93 |
| score | CHI 27.1 – TB 21.0 | CHI 27.0 – TB 20.9 |
| win prob CHI | 71.5% | 72.5% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -3.33 / total 23.87 · **2H** spread -3.04 / total 24.08 · **1Q** spread -2.30 / total 8.51 · **2Q** spread -2.56 / total 14.36 · **3Q** spread -1.25 / total 9.30 · **4Q** spread -1.06 / total 14.00

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -6.08 · total 48.17
- move `KXNFL4QSPREAD-26NOV08TBCHI-TB3` -0.105
- move `KXNFLTOTAL-26NOV08TBCHI-49` +0.105
- move `KXNFL4QSPREAD-26NOV08TBCHI-TB4` -0.100
- move `KXNFL1HTEAMTOTAL-26NOV08TBCHI-TB31` -0.100

**Game environment** (simulation, mean and middle 50%) — home margin 6.5 (-2.0–14.0) · total 49.7 (41.0–58.0) · P(one score) 48.5% · P(17+ blowout) 20.3% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CHI | 66.5 (61.0–72.0) | 34.2 (29.0–39.0) | 26.4 (21.0–31.0) | 39.1 (33.0–45.0) | 0.588 (0.520–0.657) | 0.514 / 0.696 |
| TB | 60.8 (55.0–67.0) | 29.2 (25.0–33.0) | 25.9 (21.0–30.0) | 34.4 (29.0–39.0) | 0.567 (0.503–0.633) | 0.457 / 0.625 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CHI | 00-0036275 | RB | 3.3 (1.0–5.0) | 14.2 (9.0–19.0) | 10.2% | 53.9% | MEDIUM |
| CHI | 00-0040236 | RB | 1.2 (0.0–2.0) | 6.5 (1.0–10.0) | 3.8% | 24.5% | HIGH |
| CHI | 00-0040126 | TE | 7.1 (4.0–10.0) | 0.0 (0.0–0.0) | 21.8% | 0.2% | HIGH |
| CHI | 00-0040735 | WR | 6.2 (3.0–9.0) | 0.6 (0.0–0.0) | 19.2% | 2.4% | HIGH |
| TB | 00-0039361 | RB | 2.4 (0.0–3.0) | 14.0 (9.0–19.0) | 8.3% | 54.2% | MEDIUM |
| TB | 00-0036919 | RB | 3.4 (1.0–5.0) | 6.7 (2.0–10.0) | 12.1% | 26.0% | HIGH |
| TB | 00-0033921 | WR | 5.5 (3.0–8.0) | 0.2 (0.0–0.0) | 19.6% | 0.9% | HIGH |
| TB | 00-0040129 | WR | 5.0 (1.0–8.0) | 0.2 (0.0–0.0) | 17.8% | 0.8% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 8 market(s), e.g. KXNFLPASSATT-26NOV08TBCHI-TBBMAYFIELD6-35, KXNFLPASSATT-26NOV08TBCHI-CHICWILLIAMS18-37
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 28 market(s), e.g. KXNFL3Q-26NOV08TBCHI-TB, KXNFL4QSPREAD-26NOV08TBCHI-CHI8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 24 market(s), e.g. KXNFLBOTH-26NOV08TBCHI-21, KXNFLGAME-26NOV08TBCHI-TB
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLSPREAD-26NOV08TBCHI-CHI3, KXNFLSPREAD-26NOV08TBCHI-CHI2
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 196 market(s), e.g. KXNFL1H-26NOV08TBCHI-TIE, KXNFL1HFT-26NOV08TBCHI-CHITB
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 39 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV08TBCHI-CHI3, KXNFL4QTOTAL-26NOV08TBCHI-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 26.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 48.1667 (median favourite-oriented margin +3, median total 48))_
2. favourite controls / normal scoring — 23.5%  _(CHI (favourite) wins by more than one score; total within 10 of the centre 48.1667 (median favourite-oriented margin +15, median total 48))_
3. competitive / low scoring — 10.9%  _(final margin within one score (8 points) either way; total 38.1667 or fewer (centre 48.1667) (median favourite-oriented margin +3, median total 34))_
4. competitive / high scoring — 10.6%  _(final margin within one score (8 points) either way; total 58.1667+ (centre 48.1667) (median favourite-oriented margin +3, median total 66))_
5. favourite controls / high scoring — 10.4%  _(CHI (favourite) wins by more than one score; total 58.1667+ (centre 48.1667) (median favourite-oriented margin +16, median total 65))_
   Other — 17.6%

Marginal events (overlapping): one_score 48.5% · blowout_17 20.3% · favorite_wins 72.1% · favorite_controls 40.9% · upset 27.6% · shootout 23.8% · low_scoring 20.3% · low_possession 6.5% · high_volume_passing 3.1% · run_heavy_control 18.1%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 7.30 mph, gusts 26.40, precip prob 0%, temp 45F, forecast retrieved 2026-11-07T14:56:30+00:00 (34.39 h before kickoff)._

**`KXNFLTD-26NOV08TBCHI-TBEEGBUKA2-1`** Emeka Egbuka touchdowns 1
- MODEL / MARKET: football 19.0% · market 28.5% · reconciled 26.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 12.7% · failure mass 100.0% · win-contribution HHI 0.175

**`KXNFLTD-26NOV08TBCHI-TBBIRVING7-2`** Bucky Irving touchdowns 2
- MODEL / MARKET: football 11.9% · market 10.0% · reconciled 12.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.9% · failure mass 100.0% · win-contribution HHI 0.186

**`KXNFLTD-26NOV08TBCHI-CHIDSWIFT4-1`** D'Andre Swift touchdowns 1
- MODEL / MARKET: football 54.3% · market 61.5% · reconciled 59.6%
- SCRIPT ROBUSTNESS: P50 mass 51.5% · P55 mass 51.5% · P60 mass 44.5% · major-script floor 36.8% · failure mass 48.5% · win-contribution HHI 0.187

**`KXNFLTD-26NOV08TBCHI-CHIRODUNZE15-1`** Rome Odunze touchdowns 1
- MODEL / MARKET: football 26.7% · market 33.5% · reconciled 31.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 17.5% · failure mass 100.0% · win-contribution HHI 0.180

_384 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 39 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- Jalen McMillan (WR, TB) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Zavier Scott (RB, CHI) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Braxton Jones (OT, CHI) — Injured Reserve [high] · **NEW** — ruled out
- Josh Hayes (CB, TB) — Injured Reserve [high] · **NEW** — ruled out
- Kentavius Street (DT, CHI) — Injured Reserve [high] · **NEW** — ruled out
- Yaya Diaby (LB, TB) — Out [high] · **CHANGED from Active** — ruled out

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Emeka Egbuka (WR, TB) — Questionable [high]
- Kyle Monangai (RB, CHI) — Questionable [high]
- Malik Muhammad II (CB, CHI) — Questionable [high]
- Tyrique Stevenson Sr. (CB, CHI) — Questionable [high]

### WEATHER

- Mostly Clear · 53°F · wind 10 mph WNW · precip 0%
- forecast vintage 2026-11-07T14:57:48+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 56 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Caleb Williams | CHI | attempts | 32.9 | 33.0 | 28.0 | 39.0 | 19.0 | 47.0 | 31.9 | 32.0 | 32.9 | 33.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| D'Andre Swift | CHI | carries | 14.2 | 13.0 | 9.0 | 19.0 | 3.0 | 28.0 | 15.9 | 16.0 | 14.2 | 13.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Roschon Johnson | CHI | carries | 3.1 | 1.0 | 0.0 | 4.0 | 0.0 | 12.0 | 5.4 | 5.0 | 3.1 | 1.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Caleb Williams | CHI | completions | 21.5 | 21.0 | 18.0 | 25.0 | 12.0 | 31.0 | 21.0 | 21.0 | 21.5 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Caleb Williams | CHI | passing_tds | 1.7 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.8 | 2.0 | 1.8 | 2.0 | 0.00 | 0.98 | 5 | PRICED |
| Caleb Williams | CHI | passing_yards | 240.7 | 237.0 | 185.0 | 292.0 | 112.0 | 384.0 | 248.0 | 243.0 | 248.0 | 244.0 | 0.00 | 0.98 | 9 | PRICED |
| Rome Odunze | CHI | receiving_yards | 57.4 | 47.0 | 20.0 | 83.0 | 0.0 | 152.0 | 56.6 | 48.0 | 56.6 | 46.0 | 0.00 | 0.97 | 15 | PRICED |
| Colston Loveland | CHI | receiving_yards | 54.6 | 47.0 | 23.0 | 77.0 | 0.0 | 134.0 | 58.8 | 52.0 | 58.8 | 51.0 | 0.00 | 0.98 | 13 | PRICED |

_8 of 56 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 56 of 93 listed player/stat groups simulated and exposed, 37 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV08TBCHI-CHICLOVELAND84-3` | Colston Loveland | 3.0 | 0.89 | 0.93 | 0.26 | -0.630 |
| `KXNFLREC-26NOV08TBCHI-CHICLOVELAND84-4` | Colston Loveland | 4.0 | 0.77 | 0.80 | 0.15 | -0.623 |
| `KXNFLREC-26NOV08TBCHI-CHILBURDEN10-4` | Luther Burden III | 4.0 | 0.74 | 0.76 | 0.17 | -0.566 |
| `KXNFLREC-26NOV08TBCHI-CHILBURDEN10-3` | Luther Burden III | 3.0 | 0.85 | 0.87 | 0.31 | -0.545 |
| `KXNFLREC-26NOV08TBCHI-CHICLOVELAND84-5` | Colston Loveland | 5.0 | 0.61 | 0.64 | 0.08 | -0.535 |
| `KXNFLRSHATT-26NOV08TBCHI-CHIDSWIFT4-14` | D'Andre Swift | 14.0 | 0.66 | 0.69 | 0.15 | -0.515 |

_Ranked 369 tradable markets; 25 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Zavier Scott (RB, CHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jalen McMillan (WR, TB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Kyle Monangai (RB), Emeka Egbuka (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL1HFT-26NOV08TBCHI-CHICHI moved +0.115 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.630 on KXNFLREC-26NOV08TBCHI-CHICLOVELAND84-3 (Colston Loveland). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.623 on KXNFLREC-26NOV08TBCHI-CHICLOVELAND84-4 (Colston Loveland). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV08TBCHI-CHICLOVELAND84-3 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_TB_CHI.md`_


---

## BUF @ MIN — `2026_09_BUF_MIN`

- kickoff: 2026-11-10T01:15:00+00:00 (3447 minutes away) · state **PREGAME**
- venue: U.S. Bank Stadium · roof dome · surface sportturf
- markets: 753 listed across 16 families — 411 supported, 286 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.09 | 3.15 |
| total | 44.62 | 44.97 |
| score | MIN 20.8 – BUF 23.9 | MIN 20.9 – BUF 24.1 |
| win prob MIN | 38.5% | 38.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.56 / total 22.40 · **2H** spread 1.60 / total 22.60 · **1Q** spread 0.73 / total 7.97 · **2Q** spread 1.47 / total 13.25 · **3Q** spread 1.00 / total 8.53 · **4Q** spread 0.10 / total 12.75

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 3.09 · total 44.62
- move `KXNFLTEAMTOTAL-26NOV09BUFMIN-BUF25` -0.115
- move `KXNFL4QSPREAD-26NOV09BUFMIN-MIN3` +0.110
- move `KXNFL1HTEAMTOTAL-26NOV09BUFMIN-BUF3` +0.090

**Game environment** (simulation, mean and middle 50%) — home margin -3.4 (-11.0–4.0) · total 45.7 (36.0–54.0) · P(one score) 53.4% · P(17+ blowout) 18.8% · P(total 10+ over centre) 23.7%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| MIN | 61.2 (56.0–67.0) | 31.9 (27.0–36.0) | 22.9 (18.0–27.0) | 37.7 (32.0–43.0) | 0.617 (0.551–0.685) | 0.512 / 0.684 |
| BUF | 63.0 (57.0–69.0) | 29.9 (25.0–34.0) | 26.2 (21.0–31.0) | 35.8 (30.0–41.0) | 0.569 (0.501–0.637) | 0.491 / 0.661 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| MIN | 00-0033293 | RB | 3.0 (1.0–4.0) | 9.1 (5.0–13.0) | 9.8% | 39.6% | MEDIUM |
| MIN | 00-0037525 | RB | 0.9 (0.0–1.0) | 9.9 (5.0–14.0) | 2.9% | 43.2% | MEDIUM |
| MIN | 00-0036322 | WR | 7.6 (4.0–10.0) | 0.1 (0.0–0.0) | 25.0% | 0.5% | MEDIUM |
| MIN | 00-0038994 | WR | 5.5 (3.0–8.0) | 0.2 (0.0–0.0) | 18.0% | 1.0% | HIGH |
| BUF | 00-0037248 | RB | 2.1 (0.0–3.0) | 16.6 (11.0–22.0) | 7.3% | 63.5% | MEDIUM |
| BUF | 00-0034857 | QB | 0.2 (0.0–0.0) | 7.1 (4.0–9.0) | 0.6% | 12.4% | HIGH |
| BUF | 00-0034827 | WR | 4.3 (2.0–6.0) | 0.6 (0.0–0.0) | 15.0% | 2.2% | HIGH |
| BUF | 00-0037261 | WR | 4.7 (2.0–7.0) | 0.1 (0.0–0.0) | 16.6% | 0.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 11 market(s), e.g. KXNFLPASSATT-26NOV09BUFMIN-BUFJALLEN17-36, KXNFLPASSCOMP-26NOV09BUFMIN-MINCWENTZ11-25
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 39 market(s), e.g. KXNFL1HFT-26NOV09BUFMIN-MINMIN, KXNFL1HFT-26NOV09BUFMIN-BUFBUF
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLTEAMTOTAL-26NOV09BUFMIN-MIN32, KXNFLTEAMTOTAL-26NOV09BUFMIN-BUF36
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLGAME-26NOV09BUFMIN-BUF, KXNFLTEAMTOTAL-26NOV09BUFMIN-BUF21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 204 market(s), e.g. KXNFL1HFT-26NOV09BUFMIN-TIEMIN, KXNFL1HFT-26NOV09BUFMIN-TIEBUF
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 41 market(s), e.g. KXNFL2HTOTAL-26NOV09BUFMIN-4, KXNFL2HTOTAL-26NOV09BUFMIN-11

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 30.6%  _(final margin within one score (8 points) either way; total within 10 of the centre 44.625 (median favourite-oriented margin +2, median total 44))_
2. favourite controls / normal scoring — 17.5%  _(BUF (favourite) wins by more than one score; total within 10 of the centre 44.625 (median favourite-oriented margin +15, median total 45))_
3. competitive / high scoring — 11.8%  _(final margin within one score (8 points) either way; total 54.625+ (centre 44.625) (median favourite-oriented margin +1, median total 62))_
4. competitive / low scoring — 11.1%  _(final margin within one score (8 points) either way; total 34.625 or fewer (centre 44.625) (median favourite-oriented margin +2, median total 30))_
5. underdog controls / normal scoring — 7.9%  _(MIN (underdog) wins by more than one score; total within 10 of the centre 44.625 (median favourite-oriented margin -15, median total 44))_
   Other — 21.1%

Marginal events (overlapping): one_score 53.4% · blowout_17 18.8% · favorite_wins 63.5% · favorite_controls 32.2% · upset 36.3% · shootout 23.7% · low_scoring 20.4% · low_possession 12.8% · high_volume_passing 1.7% · run_heavy_control 14.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 5.80 mph, gusts 20.10, precip prob 0%, temp 54F, forecast retrieved 2026-11-07T14:56:30+00:00 (58.31 h before kickoff)._

**`KXNFLTD-26NOV09BUFMIN-BUFJALLEN17-1`** Josh Allen touchdowns 1
- MODEL / MARKET: football 32.7% · market 52.5% · reconciled 47.7%
- SCRIPT ROBUSTNESS: P50 mass 7.8% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 19.3% · failure mass 92.2% · win-contribution HHI 0.181

**`KXNFLTD-26NOV09BUFMIN-MINTHOCKENSON87-1`** T.J. Hockenson touchdowns 1
- MODEL / MARKET: football 21.2% · market 29.5% · reconciled 27.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 14.4% · failure mass 100.0% · win-contribution HHI 0.179

**`KXNFLTD-26NOV09BUFMIN-MINJJEFFERSON18-1`** Justin Jefferson touchdowns 1
- MODEL / MARKET: football 30.1% · market 37.5% · reconciled 35.7%
- SCRIPT ROBUSTNESS: P50 mass 4.1% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 18.9% · failure mass 95.9% · win-contribution HHI 0.180

**`KXNFLTD-26NOV09BUFMIN-BUFTJOHNSON26-1`** Ty Johnson touchdowns 1
- MODEL / MARKET: football 15.4% · market 10.5% · reconciled 12.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.0% · failure mass 100.0% · win-contribution HHI 0.181

_401 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261107T150411Z.sim-1.1.0.scripts_v2.json.gz); 43 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (1)**

- Jordan Hancock (CB, BUF) — Injured Reserve [high] · **NEW** — ruled out

**Questionable / Doubtful (13)** — resolves at the inactive release, T−90m

- Kyler Murray (QB, MIN) — Questionable [high]
- DJ Moore (WR, BUF) — Questionable [high]
- Demond Claiborne (RB, MIN) — Questionable [high]
- Jauan Jennings (WR, MIN) — Questionable [high]
- Joshua Palmer (WR, BUF) — Questionable [high]
- Keon Coleman (WR, BUF) — Questionable [high]
- Alec Anderson (OT, BUF) — Questionable [high]
- Dion Dawkins (OT, BUF) — Questionable [single_source]

### WEATHER

fixed-roof stadium (U.S. Bank Stadium) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261107T150411Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 62 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Josh Allen | BUF | attempts | 28.8 | 29.0 | 24.0 | 34.0 | 16.0 | 41.0 | 30.8 | 30.0 | 28.8 | 29.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| James Cook III | BUF | carries | 16.6 | 16.0 | 11.0 | 22.0 | 5.0 | 30.0 | 18.6 | 18.0 | 16.6 | 16.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | carries | 7.1 | 6.0 | 4.0 | 9.0 | 2.0 | 16.0 | 7.3 | 7.0 | 7.1 | 6.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | completions | 18.5 | 18.0 | 15.0 | 22.0 | 10.0 | 27.0 | 20.4 | 20.0 | 18.5 | 18.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Josh Allen | BUF | passing_yards | 213.1 | 209.0 | 160.0 | 261.0 | 96.0 | 346.0 | 240.4 | 235.0 | 240.4 | 236.0 | 0.00 | 0.97 | 10 | PRICED |
| Dalton Kincaid | BUF | receiving_yards | 37.0 | 28.0 | 10.0 | 55.0 | 0.0 | 107.0 | 48.3 | 41.0 | 48.3 | 37.0 | 0.00 | 0.97 | 13 | PRICED |
| Khalil Shakir | BUF | receiving_yards | 36.7 | 29.0 | 11.0 | 53.0 | 0.0 | 101.0 | 43.1 | 36.0 | 43.1 | 34.0 | 0.00 | 0.97 | 11 | PRICED |

_8 of 62 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 62 of 97 listed player/stat groups simulated and exposed, 35 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26NOV09BUFMIN-BUFJALLEN17-5` | Josh Allen | 5.0 | 0.81 | 0.85 | 0.26 | -0.555 |
| `KXNFLRSHATT-26NOV09BUFMIN-BUFJCOOK4-16` | James Cook III | 16.0 | 0.68 | 0.71 | 0.13 | -0.549 |
| `KXNFLREC-26NOV09BUFMIN-MINBYUROSEK85-1` | Ben Yurosek | 1.0 | 0.55 | 0.56 | 0.01 | -0.535 |
| `KXNFLREC-26NOV09BUFMIN-MINJJEFFERSON18-6` | Justin Jefferson | 6.0 | 0.56 | 0.61 | 0.08 | -0.481 |
| `KXNFLRECYDS-26NOV09BUFMIN-MINTHOCKENSON87-30` | T.J. Hockenson | 30.0 | 0.62 | 0.69 | 0.17 | -0.446 |
| `KXNFLRECYDS-26NOV09BUFMIN-MINJJEFFERSON18-70` | Justin Jefferson | 70.0 | 0.58 | 0.60 | 0.16 | -0.416 |

_Ranked 321 tradable markets; 90 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. 6 skill players are Questionable (DJ Moore (WR), Joshua Palmer (WR), Keon Coleman (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
2. KXNFL1HFT-26NOV09BUFMIN-BUFBUF moved +0.160 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
3. The model disagrees by -0.555 on KXNFLRSHATT-26NOV09BUFMIN-BUFJALLEN17-5 (Josh Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
4. The model disagrees by -0.549 on KXNFLRSHATT-26NOV09BUFMIN-BUFJCOOK4-16 (James Cook III). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. KXNFLRSHYDS-26NOV09BUFMIN-BUFRDAVIS7-25 sits at a market price of 0.08 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_09_BUF_MIN.md`_


---

## HOW TO USE THIS PACKET

1. Handicap each game independently. The model's ranked disagreements are an input, not a shortlist.
2. For any thesis you form, check **BEST EXPRESSIONS** before choosing a contract — the largest disagreement is rarely the best payout for the risk.
3. Check **CORRELATION GROUPS** before sizing more than one position in a game.
4. Record every serious decision, including passes, via the recommendation ledger (`scripts/handicap/validate_recommendations.py`, then commit to the `handicap-data` branch).