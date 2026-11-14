# NFL HANDICAP PACKET — 2026 Week 10

- run id: `20261114T220628Z`  ·  packet sha: `064c9e4ab545102451d4`
- built at: 2026-11-14T22:06:28.431654+00:00  (all timestamps UTC)
- ledger: `20261114T213039Z.shadow-0.4.0.observations.jsonl.gz`  ·  model: `shadow-0.4.0`
- context captures: ['20261028T133921Z', '20261114T212258Z']
- team-profile basis: **current_season**
- **REAL-MONEY STATUS: NOT VALIDATED -- this packet recommends nothing and authorises nothing**
- **SIMULATION FRESHNESS: SIM_CURRENT** — run `20261114T213039Z` (RUN_NFL_FROZEN_BUNDLE), lag 0.0m vs target <= 180.0m; the simulation priced this packet's own board

> This packet contains no recommendations. Every model-vs-market number is a *disagreement*, which is not an edge. The model has been shown redundant to the closing market on player props and behind it on game outcomes; it is here as structure and context, not as a superior forecast.

## SLATE SUMMARY

- games: **14**
- markets listed this slate: **10927**, model-supported: **5371**
- ledger support states (all weeks): `{'UNSUPPORTED_MODEL': 19387, 'UNSUPPORTED_RULES': 7135, 'SUPPORTED': 8371, 'UNSUPPORTED_IDENTITY': 273, 'POST_KICKOFF_EXCLUDED': 92163}`

### FULL-BOARD COVERAGE

_RUN NFL examines every executable Kalshi contract for every requested unstarted NFL game. UNSUPPORTED_MODEL is a statement about one model, never a reason to hide a contract. Every listed contract terminates in exactly one analysis state, in one of four buckets: A validated model view, B coherent/Shadow research view, C manual handicap from the packet's own football and context data, D explicit PASS with a named reason._

| bucket | contracts | meaning |
|---|---|---|
| **A** | 5371 | validated/production model view available |
| **B** | 2169 | coherent / Shadow research model view available |
| **C** | 1992 | no automated pricing authority; handicap from the football and context data in this packet |
| **D** | 592 | cannot defensibly price -- explicit PASS / RESEARCH REQUIRED, with a reason |
| **-** | 803 | outside the pregame window (kickoff has passed) |
| **!** | 0 | INVARIANT VIOLATION -- a listed contract with no analysis state |

- listed: **10927** · executable books: **9678**
- incumbent priced: **5371** · coherent simulation: **0** · Shadow v2 research: **2169**
- manual handicap required: **1992** · research required: **56**
- rules blocked: **278** · identity blocked: **258** · non-football: **0**
- post-kickoff (stale): **803**
- **silently omitted: 0** — this must be 0.

| family / period | listed | executable | incumbent priced | coherent sim | shadow v2 | manual research | research required | rules blocked | identity blocked | non football | post kickoff | silently omitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLAYER_STAT/FULL | 5553 | 5152 | 4362 | 0 | 0 | 451 | 0 | 0 | 258 | 0 | 482 | 0 |
| FIRST_TD_TEAM/FULL | 404 | 147 | 0 | 0 | 0 | 374 | 0 | 0 | 0 | 0 | 30 | 0 |
| TEAM_TOTAL/FULL | 381 | 381 | 354 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 27 | 0 |
| FIRST_TD_SCORER/FULL | 358 | 358 | 0 | 0 | 0 | 183 | 0 | 148 | 0 | 0 | 27 | 0 |
| SPREAD/FULL | 354 | 354 | 330 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 24 | 0 |
| TEAM_TOTAL/1H | 307 | 307 | 0 | 0 | 262 | 23 | 0 | 0 | 0 | 0 | 22 | 0 |
| TEAM_STAT/FULL | 280 | 26 | 0 | 0 | 0 | 280 | 0 | 0 | 0 | 0 | 0 | 0 |
| TOTAL/FULL | 268 | 268 | 247 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| SPREAD/1H | 215 | 215 | 0 | 0 | 186 | 15 | 0 | 0 | 0 | 0 | 14 | 0 |
| SPREAD/2H | 215 | 204 | 0 | 0 | 186 | 15 | 0 | 0 | 0 | 0 | 14 | 0 |
| RACE_TO_N/FULL | 210 | 107 | 0 | 0 | 0 | 210 | 0 | 0 | 0 | 0 | 0 | 0 |
| TOTAL/1H | 192 | 192 | 0 | 0 | 165 | 14 | 0 | 0 | 0 | 0 | 13 | 0 |
| TOTAL/2H | 192 | 186 | 0 | 0 | 165 | 14 | 0 | 0 | 0 | 0 | 13 | 0 |
| GAME_PLAYER_LEADER/FULL | 175 | 72 | 0 | 0 | 0 | 162 | 0 | 13 | 0 | 0 | 0 | 0 |
| SPREAD/4Q | 153 | 146 | 0 | 0 | 129 | 11 | 0 | 0 | 0 | 0 | 13 | 0 |
| SPREAD/3Q | 151 | 147 | 0 | 0 | 129 | 10 | 0 | 0 | 0 | 0 | 12 | 0 |
| SPREAD/2Q | 147 | 140 | 0 | 0 | 127 | 10 | 0 | 0 | 0 | 0 | 10 | 0 |
| SPREAD/1Q | 140 | 134 | 0 | 0 | 120 | 10 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/1Q | 140 | 136 | 0 | 0 | 120 | 10 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/2Q | 140 | 136 | 0 | 0 | 120 | 10 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/3Q | 140 | 131 | 0 | 0 | 120 | 10 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/4Q | 140 | 126 | 0 | 0 | 120 | 10 | 0 | 0 | 0 | 0 | 10 | 0 |
| HALF_FULL_RESULT/1H | 126 | 126 | 0 | 0 | 0 | 9 | 0 | 117 | 0 | 0 | 0 | 0 |
| WIN_MARGIN_BUCKET/FULL | 98 | 96 | 0 | 0 | 0 | 91 | 0 | 0 | 0 | 0 | 7 | 0 |
| BOTH_TEAMS_SCORE_N/FULL | 56 | 42 | 52 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| GAME_EVENT/FULL | 56 | 52 | 0 | 0 | 0 | 0 | 56 | 0 | 0 | 0 | 0 | 0 |
| PERIOD_WINNER/1H | 42 | 42 | 0 | 0 | 36 | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/1Q | 42 | 42 | 0 | 0 | 36 | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2H | 42 | 41 | 0 | 0 | 36 | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2Q | 42 | 42 | 0 | 0 | 36 | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/3Q | 42 | 41 | 0 | 0 | 36 | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/4Q | 42 | 40 | 0 | 0 | 36 | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| GAME_WINNER/FULL | 28 | 28 | 26 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| BOTH_TEAMS_SCORE/1Q | 14 | 12 | 0 | 0 | 1 | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/2Q | 14 | 2 | 0 | 0 | 1 | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/3Q | 14 | 3 | 0 | 0 | 1 | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/4Q | 14 | 4 | 0 | 0 | 1 | 13 | 0 | 0 | 0 | 0 | 0 | 0 |

_A Shadow v2 or coherent-simulation projection is RESEARCH. It is not validated, it is never mixed into the incumbent's probability or its disagreement ranking, and it reaches no recommendation, staking or preflight path._

**Skill players ruled OUT (40)**

- Thomas Fidone II (TE, NYG) — Out · 2026_10_WAS_NYG
- Athan Kaliakmanis (QB, WAS) — Out · 2026_10_WAS_NYG
- Colson Yankoff (TE, WAS) — Out · 2026_10_WAS_NYG
- Dyami Brown (WR, WAS) — Injured Reserve · 2026_10_WAS_NYG
- Isiah Pacheco (RB, DET) — Injured Reserve · 2026_10_NE_DET
- TreVeyon Henderson (RB, NE) — Injured Reserve · 2026_10_NE_DET
- Tyrell Shavers (WR, BUF) — Out · 2026_10_BUF_NYJ
- Jonathon Brooks (RB, CAR) — Injured Reserve · 2026_10_CAR_NO
- CJ Donaldson (RB, NO) — Out · 2026_10_CAR_NO
- Brevin Jordan (TE, HOU) — Out · 2026_10_HOU_CLE
- David Montgomery (RB, HOU) — Out · 2026_10_HOU_CLE
- Marvin Harrison Jr. (WR, HOU) — Out · 2026_10_HOU_CLE
- Carnell Tate (WR, TEN) — Out · 2026_10_JAX_TEN
- Zachariah Branch (WR, ATL) — Out · 2026_10_KC_ATL
- Brian Robinson Jr. (RB, ATL) — Injured Reserve · 2026_10_KC_ATL

**New or changed since the previous capture (40)** — the most decision-relevant section on the page

- CJ Okoye (DT, NYG): **Out** (new record) · 2026_10_WAS_NYG
- J.C. Davis (OT, NYG): **Out** (new record) · 2026_10_WAS_NYG
- Josh Sills (G, NYG): **Out** (was Active) · 2026_10_WAS_NYG
- Malik Harrison (LB, NYG): **Out** (new record) · 2026_10_WAS_NYG
- Nikko Reed (CB, NYG): **Out** (was Active) · 2026_10_WAS_NYG
- Paulson Adebo (CB, NYG): **Out** (was Active) · 2026_10_WAS_NYG
- Thomas Fidone II (TE, NYG): **Out** (new record) · 2026_10_WAS_NYG
- Jason Pinnock (S, NYG): **Questionable** (new record) · 2026_10_WAS_NYG
- Abdul Carter (LB, NYG): **Active** (new record) · 2026_10_WAS_NYG
- Ar'Darius Washington (S, NYG): **Active** (new record) · 2026_10_WAS_NYG
- Bryan Hudson (C, NYG): **Active** (new record) · 2026_10_WAS_NYG
- Cam Skattebo (RB, NYG): **Active** (was Questionable) · 2026_10_WAS_NYG
- Colton Hood (CB, NYG): **Active** (new record) · 2026_10_WAS_NYG
- Jevon Holland (S, NYG): **Active** (was Questionable) · 2026_10_WAS_NYG
- Theo Johnson (TE, NYG): **Active** (was Questionable) · 2026_10_WAS_NYG

**Largest market moves since first capture**

| ticker | game | family | move |
|---|---|---|---|
| `KXNFLRECYDS-26NOV12WASNYG-NYGCSKATTEBO44-40` | 2026_10_WAS_NYG | PLAYER_STAT | +0.940 |
| `KXNFLRECYDS-26NOV12WASNYG-NYGILIKELY9-120` | 2026_10_WAS_NYG | PLAYER_STAT | +0.935 |
| `KXNFLREC-26NOV12WASNYG-NYGILIKELY9-9` | 2026_10_WAS_NYG | PLAYER_STAT | +0.915 |
| `KXNFLRECYDS-26NOV12WASNYG-NYGILIKELY9-110` | 2026_10_WAS_NYG | PLAYER_STAT | +0.915 |
| `KXNFLTD-26NOV12WASNYG-NYGCSKATTEBO44-2` | 2026_10_WAS_NYG | PLAYER_STAT | +0.905 |
| `KXNFLRECYDS-26NOV12WASNYG-NYGMFIELDS88-60` | 2026_10_WAS_NYG | PLAYER_STAT | +0.900 |
| `KXNFLRRYDS-26NOV12WASNYG-NYGCSKATTEBO44-110` | 2026_10_WAS_NYG | PLAYER_STAT | +0.900 |
| `KXNFLRECYDS-26NOV12WASNYG-NYGILIKELY9-90` | 2026_10_WAS_NYG | PLAYER_STAT | +0.895 |
| `KXNFLREC-26NOV12WASNYG-WASAEKELER30-4` | 2026_10_WAS_NYG | PLAYER_STAT | +0.890 |
| `KXNFLRECYDS-26NOV12WASNYG-NYGCSKATTEBO44-30` | 2026_10_WAS_NYG | PLAYER_STAT | +0.885 |

**Largest model/market disagreements** — DISAGREEMENT ONLY, REQUIRES HANDICAP

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26NOV15MIAIND-MIAOGORDON0-40` | Ollie Gordon II | 40.0 | 0.83 | 0.85 | 0.09 | -0.737 |
| `KXNFLRSHYDS-26NOV15CARNO-NOAESTIME30-10` | Audric Estime | 10.0 | 0.75 | 0.78 | 0.02 | -0.733 |
| `KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-30` | Emmett Johnson | 30.0 | 0.91 | 0.91 | 0.17 | -0.733 |
| `KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-40` | Emmett Johnson | 40.0 | 0.84 | 0.85 | 0.11 | -0.730 |
| `KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-25` | Emmett Johnson | 25.0 | 0.94 | 0.94 | 0.21 | -0.724 |
| `KXNFLRECYDS-26NOV15KCATL-KCEJOHNSON10-10` | Emmett Johnson | 10.0 | 0.77 | 0.78 | 0.06 | -0.711 |
| `KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-20` | Emmett Johnson | 20.0 | 0.96 | 0.97 | 0.26 | -0.704 |
| `KXNFLREC-26NOV15SFDAL-DALCLAMB88-5` | CeeDee Lamb | 5.0 | 0.82 | 0.85 | 0.13 | -0.693 |
| `KXNFLRECYDS-26NOV15MINGB-GBSWILLIAMS83-10` | Savion Williams | 10.0 | 0.70 | 0.72 | 0.01 | -0.692 |
| `KXNFLRSHYDS-26NOV15MIAIND-MIAOGORDON0-50` | Ollie Gordon II | 50.0 | 0.73 | 0.76 | 0.06 | -0.677 |
| `KXNFLREC-26NOV15SFDAL-DALCLAMB88-4` | CeeDee Lamb | 4.0 | 0.91 | 0.93 | 0.23 | -0.676 |
| `KXNFLREC-26NOV15KCATL-KCEJOHNSON10-2` | Emmett Johnson | 2.0 | 0.83 | 0.84 | 0.16 | -0.674 |

**Highest-liquidity markets**

- `KXNFLGAME-26NOV12WASNYG-NYG` (GAME_WINNER, 2026_10_WAS_NYG): volume 32456201, OI 13855576
- `KXNFLGAME-26NOV12WASNYG-WAS` (GAME_WINNER, 2026_10_WAS_NYG): volume 27168084, OI 11875033
- `KXNFLSPREAD-26NOV12WASNYG-NYG2` (SPREAD, 2026_10_WAS_NYG): volume 3611473, OI 2338507
- `KXNFLSPREAD-26NOV12WASNYG-NYG3` (SPREAD, 2026_10_WAS_NYG): volume 2810226, OI 1596052
- `KXNFLTOTAL-26NOV12WASNYG-42` (TOTAL, 2026_10_WAS_NYG): volume 2417634, OI 1502548
- `KXNFLSPREAD-26NOV12WASNYG-NYG4` (SPREAD, 2026_10_WAS_NYG): volume 1872243, OI 798287
- `KXNFLTD-26NOV12WASNYG-NYGCSKATTEBO44-1` (PLAYER_STAT, 2026_10_WAS_NYG): volume 972947, OI 846662
- `KXNFLSPREAD-26NOV12WASNYG-WAS3` (SPREAD, 2026_10_WAS_NYG): volume 961919, OI 410686

**BLOCKING data issues**

- 2026_10_WAS_NYG: `GAME_STARTED` — kickoff has passed; this is not a pregame packet

### GAME PRIORITY FOR HANDICAP

_Priority ranks where deeper review may be most useful. It is NOT a bet ranking and carries no expectation that these games contain value._

| # | game | score | why |
|---|---|---|---|
| 1 | 2026_10_MIA_IND | 20.95 | 32 new/changed injury records; 5 skill players ruled out (role change); largest market move 0.370; largest reconciled simulation disagreement 0.145; raw incumbent disagreement 0.737 (NOT scored: unvalidated); 315 supported player-prop rungs |
| 2 | 2026_10_SF_DAL | 20.63 | 31 new/changed injury records; 5 skill players ruled out (role change); largest market move 0.115; largest reconciled simulation disagreement 0.113; raw incumbent disagreement 0.693 (NOT scored: unvalidated); 394 supported player-prop rungs |
| 3 | 2026_10_MIN_GB | 19.5 | 32 new/changed injury records; 6 skill players ruled out (role change); largest market move 0.175; raw incumbent disagreement 0.692 (NOT scored: unvalidated); 338 supported player-prop rungs |
| 4 | 2026_10_LA_ARI | 19.5 | 31 new/changed injury records; 7 skill players ruled out (role change); largest market move 0.300; raw incumbent disagreement 0.649 (NOT scored: unvalidated); 340 supported player-prop rungs |
| 5 | 2026_10_KC_ATL | 18.84 | 28 new/changed injury records; 3 skill players ruled out (role change); largest market move 0.830; largest reconciled simulation disagreement 0.084; raw incumbent disagreement 0.733 (NOT scored: unvalidated); 342 supported player-prop rungs |
| 6 | 2026_10_WAS_NYG | 18.0 | 30 new/changed injury records; 4 skill players ruled out (role change); largest market move 0.940; BLOCKING data issue -- review before trusting anything here |
| 7 | 2026_10_HOU_CLE | 18.0 | 24 new/changed injury records; 3 skill players ruled out (role change); largest market move 0.280; raw incumbent disagreement 0.631 (NOT scored: unvalidated); 327 supported player-prop rungs |
| 8 | 2026_10_CAR_NO | 17.97 | 22 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.195; largest reconciled simulation disagreement 0.147; raw incumbent disagreement 0.733 (NOT scored: unvalidated); 329 supported player-prop rungs |
| 9 | 2026_10_PIT_CIN | 17.54 | 16 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.135; largest reconciled simulation disagreement 0.104; raw incumbent disagreement 0.642 (NOT scored: unvalidated); 376 supported player-prop rungs |
| 10 | 2026_10_LAC_BAL | 17.41 | 26 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.140; largest reconciled simulation disagreement 0.091; raw incumbent disagreement 0.577 (NOT scored: unvalidated); 288 supported player-prop rungs |
| 11 | 2026_10_NE_DET | 17.04 | 27 new/changed injury records; 2 skill players ruled out (role change); largest market move 0.145; largest reconciled simulation disagreement 0.054; raw incumbent disagreement 0.609 (NOT scored: unvalidated); 264 supported player-prop rungs |
| 12 | 2026_10_SEA_LV | 16.7 | 23 new/changed injury records; 1 skill players ruled out (role change); largest market move 0.230; largest reconciled simulation disagreement 0.170; raw incumbent disagreement 0.644 (NOT scored: unvalidated); 322 supported player-prop rungs |
| 13 | 2026_10_BUF_NYJ | 16.05 | 30 new/changed injury records; 1 skill players ruled out (role change); largest market move 0.150; largest reconciled simulation disagreement 0.105; raw incumbent disagreement 0.614 (NOT scored: unvalidated); 354 supported player-prop rungs |
| 14 | 2026_10_JAX_TEN | 15.0 | 22 new/changed injury records; 1 skill players ruled out (role change); largest market move 0.215; raw incumbent disagreement 0.643 (NOT scored: unvalidated); 373 supported player-prop rungs |

> Each game below is summarised. Full detail -- complete market board, every player ladder, all best-expression groups -- is in that game's own file under `games/`.


---

## WAS @ NYG — `2026_10_WAS_NYG`

- kickoff: 2026-11-13T01:15:00+00:00 (-2692 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 875 listed across 16 families — 0 supported, 24 no model, 48 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 875/875 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | WAS -3 | -- |
| total | 39.50 | -- |
| score | NYG 18.2 – WAS 21.2 | NYG -- – WAS -- |
| win prob NYG | 0.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread WAS -3 / total 16.50 · **2H** spread NYG -0.7 / total 28.96 · **1Q** spread Pick'em / total -- · **2Q** spread WAS -3 / total 16.50 · **3Q** spread Pick'em / total 14.50 · **4Q** spread NYG -1.1 / total 14.95

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread WAS -3 · total 39.50

**Game environment / team volume / player opportunity** — UNAVAILABLE: 20261114T213039Z.sim-1.1.0.scripts.json.gz

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 22 market(s), e.g. KXNFLMOSTRECYDS-26NOV12WASNYG-NYGCSKATTEBO44, KXNFLMOSTRECYDS-26NOV12WASNYG-WASAEKELER30
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 165 market(s), e.g. KXNFL2H-26NOV12WASNYG-WAS, KXNFL2H-26NOV12WASNYG-NYG
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 18 market(s), e.g. KXNFL2H-26NOV12WASNYG-TIE, KXNFLPASSINT-26NOV12WASNYG-NYGJMCCARTHY9-1
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B08 NO · Player-prop NO at 80c+ loses after fees · 147 market(s), e.g. KXNFLFFPTS-26NOV12WASNYG-WASRWHITE1-10P7, KXNFLFFPTS-26NOV12WASNYG-WASDSTEVENS19-7P5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B09 YES · Player-prop YES longshots lose after fees · 134 market(s), e.g. KXNFLFG-26NOV12WASNYG-WAS3, KXNFLFG-26NOV12WASNYG-NYG4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

GAME SCRIPT V2 — UNAVAILABLE: 20261114T213039Z.sim-1.1.0.scripts_v2.json.gz

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (14)**

- Athan Kaliakmanis (QB, WAS) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Colson Yankoff (TE, WAS) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Dyami Brown (WR, WAS) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Thomas Fidone II (TE, NYG) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- J.C. Davis (OT, NYG) — Out [single_source] · **NEW** — ruled out
- Josh Sills (G, NYG) — Out [high] · **CHANGED from Active** — ruled out
- Lucas Patrick (G, WAS) — Out [high] · **NEW** — ruled out
- Tanoa Togiai (G, WAS) — Out [single_source] · **CHANGED from Active** — ruled out
- _...and 6 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Jason Pinnock (S, NYG) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 108 listed player/stat groups simulated and exposed, 108 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Thomas Fidone II (TE, NYG) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Athan Kaliakmanis (QB, WAS) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLRECYDS-26NOV12WASNYG-NYGCSKATTEBO44-40 moved +0.940 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_WAS_NYG.md`_


---

## NE @ DET — `2026_10_NE_DET`

- kickoff: 2026-11-15T14:30:00+00:00 (984 minutes away) · state **PREGAME**
- venue: FC Bayern Munich Stadium · roof dome · surface fieldturf
- markets: 662 listed across 15 families — 340 supported, 262 no model, 48 rules unresolved, 12 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 12 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | DET -2.8 | DET -2.4 |
| total | 50.17 | 49.97 |
| score | DET 26.5 – NE 23.7 | DET 26.2 – NE 23.8 |
| win prob DET | 57.5% | 57.5% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread DET -1.7 / total 25.33 · **2H** spread DET -0.8 / total 24.31 · **1Q** spread DET -0.7 / total 9.05 · **2Q** spread DET -0.6 / total 14.85 · **3Q** spread NE -0.2 / total 9.54 · **4Q** spread DET -0.1 / total 14.23

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread DET -2.8 · total 50.17
- move `KXNFLSPREAD-26NOV15NEDET-DET3` +0.145
- move `KXNFLSPREAD-26NOV15NEDET-DET2` +0.125
- move `KXNFLSPREAD-26NOV15NEDET-DET11` +0.115
- move `KXNFL2HTOTAL-26NOV15NEDET-8` +0.115

**Game environment** (simulation, mean and middle 50%) — projected spread DET -2.6 · raw home-minus-away margin 2.6 (-5.0–10.0) · total 51.6 (43.0–59.0) · P(one score) 52.8% · P(17+ blowout) 18.0% · P(total 10+ over centre) 23.4%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| DET | 64.5 (59.0–70.0) | 34.4 (29.0–39.0) | 25.7 (20.0–30.0) | 37.9 (32.0–43.0) | 0.588 (0.521–0.657) | 0.499 / 0.684 |
| NE | 63.4 (58.0–69.0) | 32.9 (28.0–37.0) | 23.3 (18.0–28.0) | 39.4 (34.0–45.0) | 0.622 (0.556–0.689) | 0.520 / 0.695 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| DET | 00-0039139 | RB | 5.2 (2.0–7.0) | 20.1 (15.0–25.0) | 15.7% | 78.6% | MEDIUM |
| DET | 00-0036963 | WR | 8.2 (3.0–12.0) | 0.2 (0.0–0.0) | 24.5% | 0.7% | HIGH |
| DET | 00-0039065 | TE | 6.3 (3.0–9.0) | 0.1 (0.0–0.0) | 19.1% | 0.4% | HIGH |
| DET | 00-0037240 | WR | 5.7 (3.0–8.0) | 0.6 (0.0–0.0) | 17.1% | 2.1% | HIGH |
| NE | 00-0036875 | RB | 2.6 (0.0–4.0) | 9.7 (2.0–15.0) | 8.3% | 41.6% | HIGH |
| NE | 00-0040556 | RB | 0.4 (0.0–0.0) | 9.5 (4.0–14.0) | 1.2% | 40.8% | HIGH |
| NE | 00-0035676 | WR | 5.5 (1.0–8.0) | 0.0 (0.0–0.0) | 17.6% | 0.1% | HIGH |
| NE | 00-0039851 | QB | 0.1 (0.0–0.0) | 5.3 (3.0–7.0) | 0.2% | 4.9% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 2 market(s), e.g. KXNFLRSHYDS-26NOV15NEDET-DETJGOFF16-10, KXNFLRSHYDS-26NOV15NEDET-DETJGOFF16-15
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 47 market(s), e.g. KXNFL1Q-26NOV15NEDET-TIE, KXNFLFFPTS-26NOV15NEDET-NEDMAYE10-23P1
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26NOV15NEDET-DET8, KXNFLSPREAD-26NOV15NEDET-DET14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLTEAMTOTAL-26NOV15NEDET-NE21, KXNFLTEAMTOTAL-26NOV15NEDET-DET22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 176 market(s), e.g. KXNFL1H-26NOV15NEDET-TIE, KXNFL1QSPREAD-26NOV15NEDET-DET8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 32 market(s), e.g. KXNFLFG-26NOV15NEDET-DET1, KXNFLPASSTDS-26NOV15NEDET-DETJGOFF16-1

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 28.6%  _(final margin within one score (8 points) either way; total within 10 of the centre 50.1667 (median favourite-oriented margin +2, median total 51))_
2. favourite controls / normal scoring — 17.7%  _(DET (favourite) wins by more than one score; total within 10 of the centre 50.1667 (median favourite-oriented margin +13, median total 50))_
3. competitive / low scoring — 12.4%  _(final margin within one score (8 points) either way; total 40.1667 or fewer (centre 50.1667) (median favourite-oriented margin +2, median total 36))_
4. competitive / high scoring — 11.9%  _(final margin within one score (8 points) either way; total 60.1667+ (centre 50.1667) (median favourite-oriented margin +1, median total 68))_
5. underdog controls / normal scoring — 10.0%  _(NE (underdog) wins by more than one score; total within 10 of the centre 50.1667 (median favourite-oriented margin -13, median total 51))_
   Other — 19.5%

Marginal events (overlapping): one_score 52.8% · blowout_17 18.0% · favorite_wins 60.7% · favorite_controls 29.6% · upset 39.1% · shootout 23.4% · low_scoring 20.4% · low_possession 5.8% · high_volume_passing 7.9% · run_heavy_control 14.2%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): no point-in-time forecast attached._

**`KXNFLTD-26NOV15NEDET-DETASTBROWN14-1`** Amon-Ra St. Brown touchdowns 1
- MODEL / MARKET: football 33.2% · market 54.5% · reconciled 49.1%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 23.5% · failure mass 100.0% · win-contribution HHI 0.171
- THESIS DEPENDENCY with `KXNFLRECYDS-26NOV15NEDET-DETASTBROWN14-60`: cash correlation 0.357 · joint cash 25.4% · Jaccard of winning rows 0.431 · shared failure 41.0%

**`KXNFLTD-26NOV15NEDET-DETJGIBBS0-1`** Jahmyr Gibbs touchdowns 1
- MODEL / MARKET: football 67.8% · market 69.5% · reconciled 67.1%
- SCRIPT ROBUSTNESS: P50 mass 96.6% · P55 mass 74.2% · P60 mass 74.2% · major-script floor 51.1% · failure mass 3.4% · win-contribution HHI 0.172

**`KXNFLTD-26NOV15NEDET-DETBWRIGHT89-2`** Brock Wright touchdowns 2
- MODEL / MARKET: football 0.9% · market 0.5% · reconciled 2.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.2% · failure mass 100.0% · win-contribution HHI 0.199

**`KXNFLTD-26NOV15NEDET-NECKINER9-1`** Corey Kiner touchdowns 1
- MODEL / MARKET: football 25.0% · market 37.0% · reconciled 34.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 16.2% · failure mass 100.0% · win-contribution HHI 0.167
- THESIS DEPENDENCY with `KXNFLRSHATT-26NOV15NEDET-NECKINER9-11`: cash correlation 0.310 · joint cash 15.8% · Jaccard of winning rows 0.340 · shared failure 53.5%

_330 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 37 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Isiah Pacheco (RB, DET) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- TreVeyon Henderson (RB, NE) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Ben Brown (C, NE) — Out [single_source] · **CHANGED from Questionable** — ruled out
- Cade Mays (C, DET) — Out [high] · **CHANGED from Active** — ruled out
- Carlton Davis III (CB, NE) — Out [high] · **CHANGED from Questionable** — ruled out
- D.J. Reed (CB, DET) — Out [high] · **NEW** — ruled out
- Jack Campbell (LB, DET) — Injured Reserve [high] · **CHANGED from Active** — ruled out
- Jimmy Rolder (LB, DET) — Injured Reserve [high] · **NEW** — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (11)** — resolves at the inactive release, T−90m

- A.J. Brown (WR, NE) — Questionable [high]
- Amon-Ra St. Brown (WR, DET) — Questionable [high]
- Cameron Latu (TE, NE) — Questionable [high]
- Rhamondre Stevenson (RB, NE) — Questionable [high]
- Sione Vaki (RB, DET) — Questionable [high]
- Greg Van Roten (G, NE) — Questionable [single_source]
- Walter Rouse (OL, NE) — Questionable [high]
- Brenden Schooler (S, NE) — Questionable [high]

### WEATHER

played at FC Bayern Munich Stadium, not DET's home stadium -- no forecast for this venue is captured, and the home stadium's forecast is not shown (scheduled stadium id MUN01 (FC Bayern Munich Stadium) is not DET's home stadium DET00 (Ford Field))

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 47 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jared Goff | DET | attempts | 33.1 | 33.0 | 28.0 | 39.0 | 19.0 | 47.0 | 35.0 | 35.0 | 33.1 | 33.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jahmyr Gibbs | DET | carries | 20.1 | 20.0 | 15.0 | 25.0 | 7.0 | 34.0 | 20.6 | 20.0 | 20.1 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jared Goff | DET | completions | 22.5 | 23.0 | 19.0 | 27.0 | 12.0 | 33.0 | 22.8 | 22.0 | 22.5 | 23.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jared Goff | DET | passing_tds | 1.7 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 2.0 | 2.0 | 2.0 | 2.0 | 0.00 | 0.98 | 5 | PRICED |
| Jared Goff | DET | passing_yards | 252.2 | 248.0 | 195.0 | 306.0 | 122.0 | 398.0 | 270.6 | 266.0 | 270.5 | 266.0 | 0.00 | 0.98 | 10 | PRICED |
| Amon-Ra St. Brown | DET | receiving_yards | 67.2 | 61.0 | 14.0 | 104.0 | 0.0 | 173.0 | 88.7 | 81.0 | 88.3 | 81.0 | 0.00 | 0.78 | 13 | PRICED |
| Jameson Williams | DET | receiving_yards | 52.5 | 41.0 | 16.0 | 77.0 | 0.0 | 147.0 | 63.6 | 55.0 | 63.5 | 49.0 | 0.00 | 0.97 | 13 | PRICED |
| Sam LaPorta | DET | receiving_yards | 49.8 | 41.0 | 18.0 | 71.0 | 0.0 | 131.0 | 47.4 | 40.0 | 47.4 | 39.0 | 0.00 | 0.97 | 12 | PRICED |

_8 of 47 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 47 of 75 listed player/stat groups simulated and exposed, 28 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26NOV15NEDET-DETJGIBBS0-18` | Jahmyr Gibbs | 18.0 | 0.68 | 0.70 | 0.07 | -0.609 |
| `KXNFLRSHYDS-26NOV15NEDET-DETJGIBBS0-60` | Jahmyr Gibbs | 60.0 | 0.80 | 0.81 | 0.23 | -0.562 |
| `KXNFLRECYDS-26NOV15NEDET-NEERARIDON82-10` | Eli Raridon | 10.0 | 0.74 | 0.77 | 0.19 | -0.556 |
| `KXNFLRSHYDS-26NOV15NEDET-DETJGIBBS0-70` | Jahmyr Gibbs | 70.0 | 0.70 | 0.72 | 0.16 | -0.535 |
| `KXNFLRSHATT-26NOV15NEDET-NEDMAYE10-2` | Drake Maye | 2.0 | 0.91 | 0.92 | 0.39 | -0.523 |
| `KXNFLRECYDS-26NOV15NEDET-NEERARIDON82-15` | Eli Raridon | 15.0 | 0.67 | 0.70 | 0.15 | -0.520 |

_Ranked 334 tradable markets; 6 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Isiah Pacheco (RB, DET) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. TreVeyon Henderson (RB, NE) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 5 skill players are Questionable (Amon-Ra St. Brown (WR), Sione Vaki (RB), A.J. Brown (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLSPREAD-26NOV15NEDET-DET3 moved +0.145 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.609 on KXNFLRSHATT-26NOV15NEDET-DETJGIBBS0-18 (Jahmyr Gibbs). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.562 on KXNFLRSHYDS-26NOV15NEDET-DETJGIBBS0-60 (Jahmyr Gibbs). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRSHATT-26NOV15NEDET-NEDMAYE10-2 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_NE_DET.md`_


---

## BUF @ NYJ — `2026_10_BUF_NYJ`

- kickoff: 2026-11-15T18:00:00+00:00 (1194 minutes away) · state **PREGAME**
- venue: MetLife Stadium · roof outdoors · surface fieldturf
- markets: 795 listed across 16 families — 434 supported, 305 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | BUF -7.8 | BUF -8.8 |
| total | 51.12 | 51.36 |
| score | NYJ 21.7 – BUF 29.5 | NYJ 21.3 – BUF 30.1 |
| win prob NYJ | 20.5% | 21.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread BUF -6.2 / total 26.00 · **2H** spread BUF -3.2 / total 24.79 · **1Q** spread BUF -2.8 / total 9.33 · **2Q** spread BUF -3.3 / total 15.25 · **3Q** spread BUF -1.1 / total 9.75 · **4Q** spread BUF -1.2 / total 14.50

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread BUF -7.8 · total 51.12
- move `KXNFLGAME-26NOV15BUFNYJ-NYJ` -0.150
- move `KXNFL2HTOTAL-26NOV15BUFNYJ-8` +0.115
- move `KXNFLTEAMTOTAL-26NOV15BUFNYJ-BUF8` +0.100
- move `KXNFL2QTOTAL-26NOV15BUFNYJ-4` +0.090

**Game environment** (simulation, mean and middle 50%) — projected spread BUF -7.4 · raw home-minus-away margin -7.4 (-15.0–-1.0) · total 52.6 (43.0–61.0) · P(one score) 45.1% · P(17+ blowout) 24.3% · P(total 10+ over centre) 23.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NYJ | 61.8 (56.0–68.0) | 34.0 (29.0–39.0) | 23.1 (18.0–27.0) | 38.3 (33.0–43.0) | 0.620 (0.556–0.686) | 0.507 / 0.670 |
| BUF | 65.1 (59.0–71.0) | 30.3 (25.0–35.0) | 28.9 (24.0–34.0) | 35.1 (30.0–40.0) | 0.540 (0.473–0.608) | 0.473 / 0.649 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NYJ | 00-0038120 | RB | 2.7 (1.0–4.0) | 10.0 (5.0–14.0) | 8.3% | 43.1% | MEDIUM |
| NYJ | 00-0039794 | RB | 2.9 (1.0–4.0) | 7.4 (3.0–10.0) | 8.8% | 32.1% | HIGH |
| NYJ | 00-0037740 | WR | 6.0 (1.0–9.0) | 0.0 (0.0–0.0) | 18.3% | 0.1% | HIGH |
| NYJ | 00-0039890 | WR | 4.0 (0.0–6.0) | 0.1 (0.0–0.0) | 12.3% | 0.2% | HIGH |
| BUF | 00-0037248 | RB | 2.1 (0.0–3.0) | 20.0 (14.0–25.0) | 7.2% | 69.2% | MEDIUM |
| BUF | 00-0034857 | QB | 0.2 (0.0–0.0) | 7.1 (4.0–9.0) | 0.6% | 11.5% | HIGH |
| BUF | 00-0034827 | WR | 4.6 (2.0–6.0) | 0.7 (0.0–0.0) | 15.8% | 2.3% | HIGH |
| BUF | 00-0037261 | WR | 4.8 (2.0–7.0) | 0.1 (0.0–0.0) | 16.5% | 0.4% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 13 market(s), e.g. KXNFLPASSATT-26NOV15BUFNYJ-BUFJALLEN17-34, KXNFLPASSATT-26NOV15BUFNYJ-BUFJALLEN17-29
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 39 market(s), e.g. KXNFL3Q-26NOV15BUFNYJ-NYJ, KXNFLFIRSTTD-26NOV15BUFNYJ-BUFJCOOK4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 19 market(s), e.g. KXNFLGAME-26NOV15BUFNYJ-NYJ, KXNFLSPREAD-26NOV15BUFNYJ-BUF17
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLSPREAD-26NOV15BUFNYJ-BUF4, KXNFLSPREAD-26NOV15BUFNYJ-BUF5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 232 market(s), e.g. KXNFL1H-26NOV15BUFNYJ-TIE, KXNFL1HFT-26NOV15BUFNYJ-TIEBUF
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 33 market(s), e.g. KXNFLPASSYDS-26NOV15BUFNYJ-BUFJALLEN17-150, KXNFLREC-26NOV15BUFNYJ-BUFKSHAKIR10-2

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 25.3%  _(final margin within one score (8 points) either way; total within 10 of the centre 51.125 (median favourite-oriented margin +2, median total 52))_
2. favourite controls / normal scoring — 25.2%  _(BUF (favourite) wins by more than one score; total within 10 of the centre 51.125 (median favourite-oriented margin +16, median total 51))_
3. competitive / high scoring — 10.3%  _(final margin within one score (8 points) either way; total 61.125+ (centre 51.125) (median favourite-oriented margin +3, median total 70))_
4. favourite controls / high scoring — 10.1%  _(BUF (favourite) wins by more than one score; total 61.125+ (centre 51.125) (median favourite-oriented margin +16, median total 67))_
5. favourite controls / low scoring — 9.5%  _(BUF (favourite) wins by more than one score; total 41.125 or fewer (centre 51.125) (median favourite-oriented margin +17, median total 36))_
   Other — 19.6%

Marginal events (overlapping): one_score 45.1% · blowout_17 24.3% · favorite_wins 75.6% · favorite_controls 44.8% · upset 24.2% · shootout 23.1% · low_scoring 20.6% · low_possession 7.3% · high_volume_passing 3.7% · run_heavy_control 22.5%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 10.80 mph, gusts 17.70, precip prob 1%, temp 46F, forecast retrieved 2026-11-14T21:22:58+00:00 (20.62 h before kickoff)._

**`KXNFLTD-26NOV15BUFNYJ-NYJGSMITH7-1`** Geno Smith touchdowns 1
- MODEL / MARKET: football 8.5% · market 7.5% · reconciled 18.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.7% · failure mass 100.0% · win-contribution HHI 0.163

**`KXNFLTD-26NOV15BUFNYJ-BUFRDAVIS7-1`** Ray Davis touchdowns 1
- MODEL / MARKET: football 7.8% · market 7.5% · reconciled 17.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.5% · failure mass 100.0% · win-contribution HHI 0.184

**`KXNFLTD-26NOV15BUFNYJ-NYJIWILLIAMS18-1`** Isaiah Williams touchdowns 1
- MODEL / MARKET: football 8.6% · market 7.0% · reconciled 15.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.5% · failure mass 100.0% · win-contribution HHI 0.171

**`KXNFLTD-26NOV15BUFNYJ-BUFJALLEN17-1`** Josh Allen touchdowns 1
- MODEL / MARKET: football 38.9% · market 59.5% · reconciled 53.7%
- SCRIPT ROBUSTNESS: P50 mass 10.1% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 34.4% · failure mass 89.9% · win-contribution HHI 0.190

_424 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 41 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (3)**

- Tyrell Shavers (WR, BUF) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Trevin Wallace (LB, NYJ) — Out [high] · **NEW** — ruled out
- VJ Payne (S, NYJ) — Injured Reserve [high] · **NEW** — ruled out

**Questionable / Doubtful (11)** — resolves at the inactive release, T−90m

- Adonai Mitchell (WR, NYJ) — Questionable [high]
- Garrett Wilson (WR, NYJ) — Questionable [high]
- Omar Cooper Jr. (WR, NYJ) — Questionable [high]
- Spencer Brown (OT, BUF) — Doubtful [single_source]
- Christian Benford (CB, BUF) — Questionable [high]
- Harrison Phillips (DT, NYJ) — Questionable [high]
- Jarvis Brownlee Jr. (CB, NYJ) — Questionable [high]
- Jordan Hancock (CB, BUF) — Questionable [high]

### WEATHER

- Sunny · 51°F · wind 12 mph NW · precip 1%
- forecast vintage 2026-11-14T21:23:04+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 64 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Josh Allen | BUF | attempts | 29.1 | 29.0 | 24.0 | 34.0 | 16.0 | 42.0 | 28.9 | 29.0 | 29.1 | 29.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| James Cook III | BUF | carries | 20.0 | 20.0 | 14.0 | 25.0 | 7.0 | 34.0 | 19.9 | 20.0 | 20.0 | 20.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | carries | 7.1 | 6.0 | 4.0 | 9.0 | 2.0 | 16.0 | 7.0 | 7.0 | 7.1 | 6.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | completions | 19.6 | 20.0 | 16.0 | 23.0 | 10.0 | 29.0 | 19.6 | 19.0 | 19.6 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | passing_tds | 1.7 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.9 | 2.0 | 1.9 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Josh Allen | BUF | passing_yards | 224.5 | 220.0 | 170.0 | 274.0 | 103.0 | 362.0 | 239.7 | 234.0 | 239.7 | 235.0 | 0.00 | 0.97 | 9 | PRICED |
| DJ Moore | BUF | receiving_yards | 40.4 | 31.0 | 11.0 | 59.0 | 0.0 | 117.0 | 52.2 | 44.0 | 52.2 | 40.0 | 0.00 | 0.97 | 12 | PRICED |
| Khalil Shakir | BUF | receiving_yards | 39.1 | 31.0 | 12.0 | 57.0 | 0.0 | 108.0 | 50.8 | 43.0 | 50.8 | 40.0 | 0.00 | 0.97 | 12 | PRICED |

_8 of 64 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 64 of 103 listed player/stat groups simulated and exposed, 39 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26NOV15BUFNYJ-BUFJCOOK4-17` | James Cook III | 17.0 | 0.71 | 0.73 | 0.10 | -0.614 |
| `KXNFLRSHATT-26NOV15BUFNYJ-BUFJALLEN17-4` | Josh Allen | 4.0 | 0.87 | 0.88 | 0.28 | -0.590 |
| `KXNFLREC-26NOV15BUFNYJ-NYJOCOOPER11-2` | Omar Cooper Jr. | 2.0 | 0.82 | 0.85 | 0.26 | -0.566 |
| `KXNFLRECYDS-26NOV15BUFNYJ-NYJKSADIQ16-10` | Kenyon Sadiq | 10.0 | 0.73 | 0.75 | 0.19 | -0.548 |
| `KXNFLREC-26NOV15BUFNYJ-BUFDKINCAID86-2` | Dalton Kincaid | 2.0 | 0.85 | 0.88 | 0.33 | -0.524 |
| `KXNFLRECYDS-26NOV15BUFNYJ-NYJKSADIQ16-15` | Kenyon Sadiq | 15.0 | 0.64 | 0.65 | 0.15 | -0.489 |

_Ranked 431 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Tyrell Shavers (WR, BUF) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 3 skill players are Questionable (Adonai Mitchell (WR), Garrett Wilson (WR), Omar Cooper Jr. (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLGAME-26NOV15BUFNYJ-NYJ moved -0.150 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.614 on KXNFLRSHATT-26NOV15BUFNYJ-BUFJCOOK4-17 (James Cook III). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.590 on KXNFLRSHATT-26NOV15BUFNYJ-BUFJALLEN17-4 (Josh Allen). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLRECYDS-26NOV15BUFNYJ-NYJBALLEN0-30 sits at a market price of 0.10 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_BUF_NYJ.md`_


---

## CAR @ NO — `2026_10_CAR_NO`

- kickoff: 2026-11-15T18:00:00+00:00 (1194 minutes away) · state **PREGAME**
- venue: Caesars Superdome · roof dome · surface sportturf
- markets: 773 listed across 16 families — 405 supported, 288 no model, 48 rules unresolved, 32 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 32 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | NO -2 | NO -1.7 |
| total | 49.50 | 49.40 |
| score | NO 25.8 – CAR 23.8 | NO 25.6 – CAR 23.8 |
| win prob NO | 54.5% | 55.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread NO -1.1 / total 24.13 · **2H** spread NO -0.7 / total 24.44 · **1Q** spread NO -0.3 / total 8.71 · **2Q** spread NO -0.1 / total 14.42 · **3Q** spread NO -0.8 / total 9.42 · **4Q** spread CAR -0.1 / total 14.31

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread NO -2 · total 49.50
- move `KXNFL2HTOTAL-26NOV15CARNO-8` +0.130
- move `KXNFLTOTAL-26NOV15CARNO-49` +0.115

**Game environment** (simulation, mean and middle 50%) — projected spread NO -3 · raw home-minus-away margin 3.0 (-6.0–12.0) · total 49.9 (41.0–58.0) · P(one score) 46.7% · P(17+ blowout) 21.4% · P(total 10+ over centre) 22.0%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NO | 65.4 (60.0–71.0) | 34.9 (30.0–40.0) | 25.9 (20.0–31.0) | 38.7 (33.0–44.0) | 0.592 (0.522–0.665) | 0.494 / 0.684 |
| CAR | 63.6 (58.0–69.0) | 35.2 (30.0–40.0) | 23.1 (18.0–28.0) | 39.8 (34.0–45.0) | 0.627 (0.558–0.696) | 0.522 / 0.705 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NO | 00-0039373 | RB | 1.6 (0.0–2.0) | 12.5 (7.0–17.0) | 4.7% | 48.1% | MEDIUM |
| NO | 00-0033906 | RB | 3.6 (1.0–5.0) | 9.3 (4.0–13.0) | 10.7% | 36.1% | MEDIUM |
| NO | 00-0037239 | WR | 8.6 (5.0–12.0) | 0.1 (0.0–0.0) | 25.8% | 0.3% | MEDIUM |
| NO | 00-0040743 | QB | 0.2 (0.0–0.0) | 5.7 (3.0–7.0) | 0.6% | 11.2% | HIGH |
| CAR | 00-0036555 | RB | 3.8 (1.0–5.0) | 14.5 (9.0–19.0) | 11.7% | 62.5% | MEDIUM |
| CAR | 00-0040124 | WR | 7.3 (4.0–10.0) | 0.0 (0.0–0.0) | 22.4% | 0.2% | HIGH |
| CAR | 00-0039491 | WR | 5.5 (3.0–8.0) | 0.5 (0.0–0.0) | 16.8% | 2.0% | HIGH |
| CAR | 00-0031610 | TE | 4.2 (2.0–6.0) | 0.1 (0.0–0.0) | 13.0% | 0.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 17 market(s), e.g. KXNFLREC-26NOV15CARNO-CARJMETCHIE13-2, KXNFLRECYDS-26NOV15CARNO-CARJMETCHIE13-40
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 70 market(s), e.g. KXNFLPASSYDS-26NOV15CARNO-CARBYOUNG9-300, KXNFLREC-26NOV15CARNO-CARJCOKER18-5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 23 market(s), e.g. KXNFLSPREAD-26NOV15CARNO-CAR8, KXNFLSPREAD-26NOV15CARNO-CAR6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLTOTAL-26NOV15CARNO-46, KXNFLTEAMTOTAL-26NOV15CARNO-NO22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 199 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV15CARNO-NO28, KXNFL1QTOTAL-26NOV15CARNO-21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 29 market(s), e.g. KXNFLREC-26NOV15CARNO-NOCOLAVE12-3, KXNFLREC-26NOV15CARNO-CARJCOKER18-2

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 24.1%  _(final margin within one score (8 points) either way; total within 10 of the centre 49.5 (median favourite-oriented margin +2, median total 51))_
2. favourite controls / normal scoring — 18.6%  _(NO (favourite) wins by more than one score; total within 10 of the centre 49.5 (median favourite-oriented margin +15, median total 50))_
3. underdog controls / normal scoring — 13.1%  _(CAR (underdog) wins by more than one score; total within 10 of the centre 49.5 (median favourite-oriented margin -14, median total 47))_
4. competitive / high scoring — 12.2%  _(final margin within one score (8 points) either way; total 59.5+ (centre 49.5) (median favourite-oriented margin +1, median total 66))_
5. competitive / low scoring — 10.3%  _(final margin within one score (8 points) either way; total 39.5 or fewer (centre 49.5) (median favourite-oriented margin -1, median total 35))_
   Other — 21.6%

Marginal events (overlapping): one_score 46.7% · blowout_17 21.4% · favorite_wins 58.2% · favorite_controls 32.9% · upset 41.6% · shootout 22.0% · low_scoring 22.1% · low_possession 4.6% · high_volume_passing 13.8% · run_heavy_control 17.0%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 13.20 mph, gusts 18.80, precip prob 1%, temp 64F, forecast retrieved 2026-11-14T21:22:58+00:00 (20.62 h before kickoff)._

**`KXNFLTD-26NOV15CARNO-CARTETIENNE23-1`** Trevor Etienne touchdowns 1
- MODEL / MARKET: football 8.2% · market 7.5% · reconciled 22.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.1% · failure mass 100.0% · win-contribution HHI 0.160

**`KXNFLTD-26NOV15CARNO-CARJMETCHIE13-1`** John Metchie III touchdowns 1
- MODEL / MARKET: football 11.2% · market 7.5% · reconciled 18.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.7% · failure mass 100.0% · win-contribution HHI 0.164

**`KXNFLTD-26NOV15CARNO-NOBLANCE18-1`** Bryce Lance touchdowns 1
- MODEL / MARKET: football 11.0% · market 7.5% · reconciled 18.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.2% · failure mass 100.0% · win-contribution HHI 0.168

**`KXNFLTD-26NOV15CARNO-NOAESTIME30-1`** Audric Estime touchdowns 1
- MODEL / MARKET: football 40.8% · market 23.5% · reconciled 28.8%
- SCRIPT ROBUSTNESS: P50 mass 37.3% · P55 mass 6.5% · P60 mass 6.5% · major-script floor 23.8% · failure mass 62.7% · win-contribution HHI 0.167

_395 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 42 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- CJ Donaldson (RB, NO) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Jonathon Brooks (RB, CAR) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Brady Christensen (G, CAR) — Injured Reserve [high] · **NEW** — ruled out
- Erik McCoy (C, NO) — Out [high] · **NEW** — ruled out
- Taliese Fuaga (OT, NO) — Out [high] · **NEW** — ruled out
- Bobby Okereke (LB, CAR) — Out [high] · **CHANGED from Active** — ruled out
- Christen Miller (DT, NO) — Out [high] · **NEW** — ruled out
- Jaycee Horn (CB, CAR) — Injured Reserve [high] · **NEW** — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Travis Etienne Jr. (RB, NO) — Questionable [high]
- Xavier Legette (WR, CAR) — Questionable [high]
- Jaelan Phillips (LB, CAR) — Questionable [high]
- Martin Emerson Jr. (CB, NO) — Questionable [high]
- Will Lee III (CB, CAR) — Questionable [high]

### WEATHER

fixed-roof stadium (Caesars Superdome) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 57 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bryce Young | CAR | attempts | 33.7 | 34.0 | 29.0 | 39.0 | 20.0 | 47.0 | 36.5 | 36.0 | 33.7 | 34.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chuba Hubbard | CAR | carries | 14.5 | 14.0 | 9.0 | 19.0 | 4.0 | 27.0 | 18.8 | 18.0 | 14.5 | 14.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | carries | 2.3 | 2.0 | 1.0 | 3.0 | 0.0 | 6.0 | 2.4 | 2.0 | 2.3 | 2.0 | -- | 0.98 | 2 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | completions | 20.9 | 21.0 | 17.0 | 25.0 | 11.0 | 31.0 | 22.8 | 22.0 | 20.9 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.7 | 2.0 | 1.7 | 2.0 | 0.00 | 0.98 | 4 | PRICED |
| Bryce Young | CAR | passing_yards | 227.0 | 223.0 | 175.0 | 275.0 | 107.0 | 363.0 | 249.8 | 244.0 | 249.7 | 245.0 | 0.00 | 0.98 | 9 | PRICED |
| Tetairoa McMillan | CAR | receiving_yards | 59.4 | 51.0 | 25.0 | 84.0 | 0.0 | 147.0 | 72.5 | 64.0 | 72.4 | 62.0 | 0.00 | 0.97 | 13 | PRICED |
| Jalen Coker | CAR | receiving_yards | 42.9 | 34.0 | 14.0 | 62.0 | 0.0 | 119.0 | 58.2 | 49.0 | 58.2 | 46.0 | 0.00 | 0.98 | 12 | PRICED |

_8 of 57 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 57 of 93 listed player/stat groups simulated and exposed, 36 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26NOV15CARNO-NOAESTIME30-10` | Audric Estime | 10.0 | 0.75 | 0.78 | 0.02 | -0.733 |
| `KXNFLRSHYDS-26NOV15CARNO-CARCHUBBARD30-40` | Chuba Hubbard | 40.0 | 0.88 | 0.89 | 0.20 | -0.671 |
| `KXNFLRSHYDS-26NOV15CARNO-CARCHUBBARD30-50` | Chuba Hubbard | 50.0 | 0.79 | 0.81 | 0.13 | -0.656 |
| `KXNFLRSHATT-26NOV15CARNO-CARCHUBBARD30-15` | Chuba Hubbard | 15.0 | 0.74 | 0.77 | 0.10 | -0.649 |
| `KXNFLRSHYDS-26NOV15CARNO-NOAESTIME30-15` | Audric Estime | 15.0 | 0.65 | 0.67 | 0.01 | -0.631 |
| `KXNFLRSHYDS-26NOV15CARNO-CARCHUBBARD30-60` | Chuba Hubbard | 60.0 | 0.69 | 0.71 | 0.09 | -0.600 |

_Ranked 403 tradable markets; 2 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jonathon Brooks (RB, CAR) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. CJ Donaldson (RB, NO) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Xavier Legette (WR), Travis Etienne Jr. (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRECYDS-26NOV15CARNO-NOJTYSON0-40 moved +0.195 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.733 on KXNFLRSHYDS-26NOV15CARNO-NOAESTIME30-10 (Audric Estime). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.671 on KXNFLRSHYDS-26NOV15CARNO-CARCHUBBARD30-40 (Chuba Hubbard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRSHATT-26NOV15CARNO-NOTSHOUGH6-2 sits at a market price of 0.93 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_CAR_NO.md`_


---

## HOU @ CLE — `2026_10_HOU_CLE`

- kickoff: 2026-11-15T18:00:00+00:00 (1194 minutes away) · state **PREGAME**
- venue: Huntington Bank Field · roof outdoors · surface grass
- markets: 773 listed across 16 families — 404 supported, 292 no model, 48 rules unresolved, 29 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 29 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | HOU -4.7 | HOU -4.8 |
| total | 41.10 | 41.38 |
| score | CLE 18.2 – HOU 22.9 | CLE 18.3 – HOU 23.1 |
| win prob CLE | 32.5% | 32.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread HOU -3 / total 20.45 · **2H** spread HOU -2.4 / total 20.57 · **1Q** spread HOU -1.2 / total 7.71 · **2Q** spread HOU -1.4 / total 11.54 · **3Q** spread HOU -0.9 / total 7.91 · **4Q** spread HOU -0.7 / total 10.60

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread HOU -4.7 · total 41.10
- move `KXNFLGAME-26NOV15HOUCLE-HOU` +0.280
- move `KXNFLGAME-26NOV15HOUCLE-CLE` -0.115

**Game environment** (simulation, mean and middle 50%) — projected spread HOU -4.5 · raw home-minus-away margin -4.5 (-12.0–3.0) · total 42.7 (34.0–51.0) · P(one score) 51.9% · P(17+ blowout) 19.7% · P(total 10+ over centre) 23.6%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CLE | 62.2 (57.0–68.0) | 31.7 (27.0–36.0) | 22.6 (18.0–27.0) | 39.0 (34.0–44.0) | 0.628 (0.563–0.693) | 0.524 / 0.690 |
| HOU | 63.2 (57.0–69.0) | 32.9 (28.0–38.0) | 25.5 (20.8–30.0) | 36.7 (31.0–42.0) | 0.581 (0.514–0.649) | 0.505 / 0.674 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CLE | 00-0040784 | RB | 2.4 (0.0–4.0) | 12.5 (8.0–17.0) | 7.8% | 55.1% | MEDIUM |
| CLE | 00-0040162 | RB | 4.1 (2.0–6.0) | 4.7 (1.0–7.0) | 13.4% | 20.9% | HIGH |
| CLE | 00-0041547 | WR | 5.6 (3.0–8.0) | 0.8 (0.0–1.0) | 18.3% | 3.5% | HIGH |
| CLE | 00-0033537 | QB | 0.1 (0.0–0.0) | 5.4 (3.0–7.0) | 0.3% | 7.9% | HIGH |
| HOU | 00-0040583 | RB | 2.8 (1.0–4.0) | 13.6 (8.0–18.0) | 8.8% | 53.3% | MEDIUM |
| HOU | 00-0036554 | WR | 6.5 (3.0–9.0) | 0.2 (0.0–0.0) | 20.7% | 0.7% | HIGH |
| HOU | 00-0035685 | RB | 1.0 (0.0–1.0) | 5.4 (0.0–8.0) | 3.2% | 21.1% | HIGH |
| HOU | 00-0038705 | RB | 1.1 (0.0–2.0) | 3.9 (1.0–6.0) | 3.5% | 15.4% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 2 market(s), e.g. KXNFLPASSCOMP-26NOV15HOUCLE-CLEDWATSON4-25, KXNFLPASSATT-26NOV15HOUCLE-CLEDWATSON4-37
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 46 market(s), e.g. KXNFL1HFT-26NOV15HOUCLE-HOUHOU, KXNFL4Q-26NOV15HOUCLE-CLE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV15HOUCLE-HOU18, KXNFLSPREAD-26NOV15HOUCLE-HOU17
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLGAME-26NOV15HOUCLE-HOU, KXNFLSPREAD-26NOV15HOUCLE-HOU3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 217 market(s), e.g. KXNFL1QTOTAL-26NOV15HOUCLE-22, KXNFLBOTH-26NOV15HOUCLE-28
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 27 market(s), e.g. KXNFLLONGREC-26NOV15HOUCLE-CLEJJEUDY3-11, KXNFLPASSYDS-26NOV15HOUCLE-HOUCSTROUD7-150

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 30.7%  _(final margin within one score (8 points) either way; total within 10 of the centre 41.1 (median favourite-oriented margin +2, median total 41))_
2. favourite controls / normal scoring — 18.9%  _(HOU (favourite) wins by more than one score; total within 10 of the centre 41.1 (median favourite-oriented margin +16, median total 41))_
3. competitive / high scoring — 11.5%  _(final margin within one score (8 points) either way; total 51.1+ (centre 41.1) (median favourite-oriented margin +2, median total 59))_
4. competitive / low scoring — 9.8%  _(final margin within one score (8 points) either way; total 31.1 or fewer (centre 41.1) (median favourite-oriented margin +3, median total 27))_
5. favourite controls / low scoring — 8.2%  _(HOU (favourite) wins by more than one score; total 31.1 or fewer (centre 41.1) (median favourite-oriented margin +14, median total 26))_
   Other — 21.0%

Marginal events (overlapping): one_score 51.9% · blowout_17 19.7% · favorite_wins 66.0% · favorite_controls 35.1% · upset 33.9% · shootout 23.6% · low_scoring 20.1% · low_possession 10.0% · high_volume_passing 3.9% · run_heavy_control 13.1%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 12.50 mph, gusts 16.10, precip prob 6%, temp 44F, forecast retrieved 2026-11-14T21:22:58+00:00 (20.62 h before kickoff)._

**`KXNFLTD-26NOV15HOUCLE-CLEDBOSTON12-1`** Denzel Boston touchdowns 1
- MODEL / MARKET: football 18.4% · market 26.5% · reconciled 24.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 11.7% · failure mass 100.0% · win-contribution HHI 0.181

**`KXNFLTD-26NOV15HOUCLE-HOUDSCHULTZ86-1`** Dalton Schultz touchdowns 1
- MODEL / MARKET: football 17.3% · market 24.5% · reconciled 22.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 16.5% · failure mass 100.0% · win-contribution HHI 0.185

**`KXNFLTD-26NOV15HOUCLE-CLEDSAMPSON22-1`** Dylan Sampson touchdowns 1
- MODEL / MARKET: football 20.4% · market 15.5% · reconciled 17.1%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 12.3% · failure mass 100.0% · win-contribution HHI 0.179

**`KXNFLTD-26NOV15HOUCLE-HOUNCOLLINS12-1`** Nico Collins touchdowns 1
- MODEL / MARKET: football 30.2% · market 35.5% · reconciled 33.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 27.9% · failure mass 100.0% · win-contribution HHI 0.181
- THESIS DEPENDENCY with `KXNFLPASSTDS-26NOV15HOUCLE-HOUCSTROUD7-2`: cash correlation 0.306 · joint cash 21.2% · Jaccard of winning rows 0.379 · shared failure 44.0%

_382 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 42 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Brevin Jordan (TE, HOU) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- David Montgomery (RB, HOU) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Marvin Harrison Jr. (WR, HOU) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Keylan Rutledge (G, HOU) — Out [high] · **NEW** — ruled out
- Azeez Al-Shaair (LB, HOU) — Out [high] · **CHANGED from Active** — ruled out
- Danielle Hunter (DE, HOU) — Out [high] · **NEW** — ruled out
- Jaylin Smith (CB, HOU) — Injured Reserve [high] · **NEW** — ruled out
- Michael Burton (FB, CLE) — Injured Reserve [high] · **NEW** — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (6)** — resolves at the inactive release, T−90m

- Denzel Boston (WR, CLE) — Questionable [high]
- Braden Smith (OT, HOU) — Questionable [high]
- Trent Brown (OT, HOU) — Questionable [high]
- Wyatt Teller (G, HOU) — Questionable [high]
- Jake Hummel (LB, HOU) — Questionable [high]
- Will Anderson Jr. (DE, HOU) — Questionable [high]

### WEATHER

- Slight Chance Rain Showers · 47°F · wind 12 mph N · precip 16%
- forecast vintage 2026-11-14T21:22:59+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 55 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Deshaun Watson | CLE | attempts | 30.5 | 31.0 | 26.0 | 36.0 | 18.0 | 43.0 | 31.9 | 31.0 | 30.5 | 31.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Quinshon Judkins | CLE | carries | 12.5 | 12.0 | 8.0 | 17.0 | 2.0 | 24.0 | 13.8 | 13.0 | 12.5 | 12.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Deshaun Watson | CLE | carries | 5.4 | 5.0 | 3.0 | 7.0 | 1.0 | 12.0 | 6.7 | 6.0 | 5.4 | 5.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Deshaun Watson | CLE | completions | 19.4 | 19.0 | 16.0 | 23.0 | 10.0 | 29.0 | 19.9 | 20.0 | 19.4 | 19.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Deshaun Watson | CLE | passing_tds | 1.2 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.1 | 1.0 | 1.1 | 1.0 | 0.00 | 0.97 | 3 | PRICED |
| Deshaun Watson | CLE | passing_yards | 207.6 | 203.0 | 158.0 | 254.0 | 96.0 | 335.0 | 213.8 | 207.0 | 213.8 | 209.0 | 0.00 | 0.97 | 10 | PRICED |
| KC Concepcion Jr. | CLE | receiving_yards | 42.3 | 34.0 | 14.0 | 61.0 | 0.0 | 114.0 | 52.8 | 45.0 | 52.8 | 42.0 | 0.00 | 0.97 | 12 | PRICED |
| Denzel Boston | CLE | receiving_yards | 40.8 | 29.0 | 0.0 | 64.0 | 0.0 | 128.0 | 51.3 | 43.0 | 51.3 | 37.0 | 0.00 | 0.78 | 13 | PRICED |

_8 of 55 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 55 of 94 listed player/stat groups simulated and exposed, 39 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26NOV15HOUCLE-CLEDWATSON4-4` | Deshaun Watson | 4.0 | 0.84 | 0.85 | 0.21 | -0.631 |
| `KXNFLREC-26NOV15HOUCLE-CLEKCONCEPCION1-3` | KC Concepcion Jr. | 3.0 | 0.79 | 0.80 | 0.19 | -0.597 |
| `KXNFLRECYDS-26NOV15HOUCLE-HOUMHARRISON18-10` | Marvin Harrison Jr. | 10.0 | 0.59 | 0.62 | 0.00 | -0.590 |
| `KXNFLREC-26NOV15HOUCLE-CLEKCONCEPCION1-2` | KC Concepcion Jr. | 2.0 | 0.91 | 0.95 | 0.32 | -0.585 |
| `KXNFLRSHATT-26NOV15HOUCLE-HOUWMARKS4-14` | Woody Marks | 14.0 | 0.69 | 0.74 | 0.14 | -0.547 |
| `KXNFLRECYDS-26NOV15HOUCLE-CLEDBOSTON12-20` | Denzel Boston | 20.0 | 0.80 | 0.82 | 0.27 | -0.526 |

_Ranked 400 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Brevin Jordan (TE, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. David Montgomery (RB, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Denzel Boston (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLGAME-26NOV15HOUCLE-HOU moved +0.280 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.631 on KXNFLRSHATT-26NOV15HOUCLE-CLEDWATSON4-4 (Deshaun Watson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.597 on KXNFLREC-26NOV15HOUCLE-CLEKCONCEPCION1-3 (KC Concepcion Jr.). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV15HOUCLE-CLEKCONCEPCION1-2 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_HOU_CLE.md`_


---

## JAX @ TEN — `2026_10_JAX_TEN`

- kickoff: 2026-11-15T18:00:00+00:00 (1194 minutes away) · state **PREGAME**
- venue: Nissan Stadium · roof outdoors · surface grass
- markets: 806 listed across 16 families — 450 supported, 300 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | JAX -11.1 | JAX -11.1 |
| total | 46.83 | 45.92 |
| score | TEN 17.9 – JAX 28.9 | TEN 17.4 – JAX 28.5 |
| win prob TEN | 16.5% | 17.3% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread JAX -6.9 / total 23.88 · **2H** spread JAX -4.4 / total 22.46 · **1Q** spread JAX -2.9 / total 8.31 · **2Q** spread JAX -4.2 / total 14.15 · **3Q** spread JAX -2.7 / total 8.85 · **4Q** spread JAX -2.7 / total 12.57

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread JAX -11.1 · total 46.83
- move `KXNFLGAME-26NOV15JACTEN-TEN` -0.170
- move `KXNFLGAME-26NOV15JACTEN-JAC` +0.170

**Game environment** (simulation, mean and middle 50%) — projected spread JAX -11.6 · raw home-minus-away margin -11.6 (-19.0–-5.0) · total 47.7 (39.0–55.0) · P(one score) 31.4% · P(17+ blowout) 33.7% · P(total 10+ over centre) 23.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| TEN | 59.8 (54.0–66.0) | 34.1 (29.0–39.0) | 21.4 (17.0–26.0) | 38.1 (33.0–43.0) | 0.638 (0.573–0.702) | 0.512 / 0.677 |
| JAX | 62.3 (57.0–68.0) | 28.9 (24.0–34.0) | 28.6 (23.0–33.0) | 32.5 (27.0–37.0) | 0.521 (0.453–0.590) | 0.467 / 0.646 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| TEN | 00-0035261 | RB | 3.2 (1.0–5.0) | 13.1 (8.0–17.0) | 9.8% | 61.2% | MEDIUM |
| TEN | 00-0038117 | WR | 7.2 (4.0–10.0) | 0.1 (0.0–0.0) | 22.2% | 0.5% | HIGH |
| TEN | 00-0040584 | TE | 4.6 (2.0–7.0) | 0.0 (0.0–0.0) | 14.2% | 0.2% | HIGH |
| TEN | 00-0036924 | RB | 1.8 (0.0–3.0) | 2.6 (0.0–4.0) | 5.5% | 12.1% | HIGH |
| JAX | 00-0040719 | RB | 1.8 (0.0–3.0) | 14.3 (9.0–19.0) | 6.4% | 50.0% | MEDIUM |
| JAX | 00-0038611 | RB | 1.0 (0.0–2.0) | 8.2 (3.0–12.0) | 3.7% | 28.6% | HIGH |
| JAX | 00-0038606 | WR | 6.1 (3.0–8.0) | 0.3 (0.0–0.0) | 21.8% | 1.1% | HIGH |
| JAX | 00-0034960 | WR | 4.7 (2.0–7.0) | 0.1 (0.0–0.0) | 16.7% | 0.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 31 market(s), e.g. KXNFLPASSATT-26NOV15JACTEN-JACTLAWRENCE16-30, KXNFLPASSCOMP-26NOV15JACTEN-JACTLAWRENCE16-20
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 67 market(s), e.g. KXNFLREC-26NOV15JACTEN-JACJMEYERS3-5, KXNFLREC-26NOV15JACTEN-TENWROBINSON4-8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 14 market(s), e.g. KXNFLGAME-26NOV15JACTEN-TEN, KXNFLSPREAD-26NOV15JACTEN-TEN2
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLSPREAD-26NOV15JACTEN-JAC8, KXNFLSPREAD-26NOV15JACTEN-JAC7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 245 market(s), e.g. KXNFL1H-26NOV15JACTEN-TIE, KXNFL1HFT-26NOV15JACTEN-TENTEN
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 29 market(s), e.g. KXNFLTEAMTOTAL-26NOV15JACTEN-JAC8, KXNFLTEAMTOTAL-26NOV15JACTEN-JAC4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 35.1%  _(JAX (favourite) wins by more than one score; total within 10 of the centre 46.8333 (median favourite-oriented margin +17, median total 47))_
2. competitive / normal scoring — 18.7%  _(final margin within one score (8 points) either way; total within 10 of the centre 46.8333 (median favourite-oriented margin +3, median total 46))_
3. favourite controls / high scoring — 14.4%  _(JAX (favourite) wins by more than one score; total 56.8333+ (centre 46.8333) (median favourite-oriented margin +18, median total 64))_
4. favourite controls / low scoring — 13.3%  _(JAX (favourite) wins by more than one score; total 36.8333 or fewer (centre 46.8333) (median favourite-oriented margin +18, median total 31))_
5. competitive / high scoring — 7.3%  _(final margin within one score (8 points) either way; total 56.8333+ (centre 46.8333) (median favourite-oriented margin +2, median total 64))_
   Other — 11.3%

Marginal events (overlapping): one_score 31.4% · blowout_17 33.7% · favorite_wins 86.0% · favorite_controls 62.7% · upset 13.9% · shootout 23.3% · low_scoring 19.5% · low_possession 18.7% · high_volume_passing 2.8% · run_heavy_control 24.8%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 6.00 mph, gusts 8.10, precip prob 0%, temp 52F, forecast retrieved 2026-11-14T21:22:58+00:00 (20.62 h before kickoff)._

**`KXNFLTD-26NOV15JACTEN-JACAABDULLAH20-1`** Ameer Abdullah touchdowns 1
- MODEL / MARKET: football 13.0% · market 8.5% · reconciled 10.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 10.1% · failure mass 100.0% · win-contribution HHI 0.244

**`KXNFLTD-26NOV15JACTEN-JACPWASHINGTON11-1`** Parker Washington touchdowns 1
- MODEL / MARKET: football 36.3% · market 41.5% · reconciled 39.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 28.4% · failure mass 100.0% · win-contribution HHI 0.228

**`KXNFLTD-26NOV15JACTEN-JACPWASHINGTON11-2`** Parker Washington touchdowns 2
- MODEL / MARKET: football 8.5% · market 7.5% · reconciled 9.2%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.0% · failure mass 100.0% · win-contribution HHI 0.262

**`KXNFLTD-26NOV15JACTEN-JACBTHOMAS7-3`** Brian Thomas Jr. touchdowns 3
- MODEL / MARKET: football 0.2% · market 1.5% · reconciled 0.1%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.1% · failure mass 100.0% · win-contribution HHI 0.312

_440 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 40 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Carnell Tate (WR, TEN) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Peter Skoronski (G, TEN) — Injured Reserve [high] · **NEW** — ruled out
- Anthony Hill Jr. (LB, TEN) — Out [high] · **CHANGED from Active** — ruled out
- B.J. Green II (DE, JAX) — Injured Reserve [high] · **NEW** — ruled out
- Cody Barton (LB, TEN) — Out [high] · **NEW** — ruled out
- James Williams Sr. (LB, TEN) — Injured Reserve [high] · **NEW** — ruled out
- Jessie Bates III (S, JAX) — Out [high] · **NEW** — ruled out
- Tommy Townsend (P, TEN) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Tyjae Spears (RB, TEN) — Questionable [high]

### WEATHER

- Sunny · 54°F · wind 5 mph NE · precip 0%
- forecast vintage 2026-11-14T21:23:05+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 68 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trevor Lawrence | JAX | attempts | 27.8 | 28.0 | 23.0 | 33.0 | 15.0 | 41.0 | 29.6 | 29.0 | 27.8 | 28.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bhayshul Tuten | JAX | carries | 14.3 | 14.0 | 9.0 | 19.0 | 3.0 | 28.0 | 15.4 | 15.0 | 14.3 | 14.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Trevor Lawrence | JAX | carries | 3.7 | 3.0 | 2.0 | 5.0 | 1.0 | 9.0 | 3.3 | 3.0 | 3.7 | 3.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Trevor Lawrence | JAX | completions | 19.0 | 19.0 | 15.0 | 23.0 | 10.0 | 28.0 | 20.1 | 20.0 | 19.0 | 19.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Trevor Lawrence | JAX | passing_tds | 1.8 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.0 | 2.0 | 2.0 | 2.0 | 0.00 | 0.98 | 5 | PRICED |
| Trevor Lawrence | JAX | passing_yards | 230.2 | 225.0 | 174.0 | 283.0 | 103.0 | 376.0 | 250.6 | 245.0 | 250.6 | 245.0 | 0.00 | 0.98 | 10 | PRICED |
| Parker Washington | JAX | receiving_yards | 57.8 | 48.0 | 21.0 | 83.0 | 0.0 | 150.0 | 69.6 | 60.0 | 69.6 | 58.0 | 0.00 | 0.97 | 14 | PRICED |
| Jakobi Meyers | JAX | receiving_yards | 41.9 | 33.0 | 12.0 | 61.0 | 0.0 | 117.0 | 47.2 | 40.0 | 47.2 | 37.0 | 0.00 | 0.98 | 12 | PRICED |

_8 of 68 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 68 of 101 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26NOV15JACTEN-JACBTUTEN33-40` | Bhayshul Tuten | 40.0 | 0.80 | 0.83 | 0.16 | -0.643 |
| `KXNFLRSHYDS-26NOV15JACTEN-JACBTUTEN33-50` | Bhayshul Tuten | 50.0 | 0.69 | 0.70 | 0.12 | -0.570 |
| `KXNFLRSHATT-26NOV15JACTEN-TENTPOLLARD20-13` | Tony Pollard | 13.0 | 0.72 | 0.74 | 0.20 | -0.520 |
| `KXNFLRSHYDS-26NOV15JACTEN-JACBTUTEN33-60` | Bhayshul Tuten | 60.0 | 0.58 | 0.60 | 0.08 | -0.501 |
| `KXNFLRECYDS-26NOV15JACTEN-JACBTUTEN33-10` | Bhayshul Tuten | 10.0 | 0.58 | 0.60 | 0.11 | -0.478 |
| `KXNFLRECYDS-26NOV15JACTEN-TENGHELM84-10` | Gunnar Helm | 10.0 | 0.80 | 0.82 | 0.34 | -0.469 |

_Ranked 439 tradable markets; 11 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Carnell Tate (WR, TEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 1 skill players are Questionable (Tyjae Spears (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLRECYDS-26NOV15JACTEN-TENGHELM84-30 moved +0.215 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.643 on KXNFLRSHYDS-26NOV15JACTEN-JACBTUTEN33-40 (Bhayshul Tuten). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.570 on KXNFLRSHYDS-26NOV15JACTEN-JACBTUTEN33-50 (Bhayshul Tuten). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26NOV15JACTEN-JACPWASHINGTON11-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_JAX_TEN.md`_


---

## KC @ ATL — `2026_10_KC_ATL`

- kickoff: 2026-11-15T18:00:00+00:00 (1194 minutes away) · state **PREGAME**
- venue: Mercedes-Benz Stadium · roof  · surface fieldturf
- markets: 792 listed across 16 families — 418 supported, 295 no model, 48 rules unresolved, 31 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 31 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | KC -3.2 | KC -3.1 |
| total | 47.88 | 47.88 |
| score | ATL 22.3 – KC 25.5 | ATL 22.4 – KC 25.5 |
| win prob ATL | 37.5% | 38.4% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread KC -2.6 / total 23.79 · **2H** spread KC -1.3 / total 24.09 · **1Q** spread KC -0.8 / total 8.31 · **2Q** spread KC -0.9 / total 14.14 · **3Q** spread KC -0.3 / total 9.18 · **4Q** spread KC -0.1 / total 13.85

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread KC -3.2 · total 47.88

**Game environment** (simulation, mean and middle 50%) — projected spread KC -3.5 · raw home-minus-away margin -3.5 (-11.0–4.0) · total 48.8 (39.0–57.0) · P(one score) 53.4% · P(17+ blowout) 18.8% · P(total 10+ over centre) 23.7%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| ATL | 61.5 (56.0–67.0) | 32.7 (28.0–37.0) | 25.1 (20.0–30.0) | 35.8 (31.0–41.0) | 0.583 (0.519–0.649) | 0.479 / 0.648 |
| KC | 63.1 (57.0–69.0) | 34.4 (29.0–39.0) | 23.0 (18.0–27.0) | 39.2 (34.0–44.0) | 0.621 (0.555–0.689) | 0.544 / 0.714 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| ATL | 00-0038542 | RB | 5.3 (3.0–7.0) | 19.2 (14.0–24.0) | 17.0% | 76.5% | MEDIUM |
| ATL | 00-0037238 | WR | 8.3 (5.0–11.0) | 0.1 (0.0–0.0) | 26.7% | 0.5% | MEDIUM |
| ATL | 00-0036906 | RB | 1.9 (0.0–3.0) | 3.6 (0.0–5.0) | 6.0% | 14.3% | HIGH |
| ATL | 00-0036970 | TE | 5.1 (2.0–7.0) | 0.0 (0.0–0.0) | 16.5% | 0.1% | HIGH |
| KC | 00-0041013 | RB | 1.8 (0.0–3.0) | 9.7 (5.0–13.0) | 5.7% | 42.1% | MEDIUM |
| KC | 00-0039067 | WR | 6.4 (3.0–9.0) | 0.3 (0.0–0.0) | 19.6% | 1.1% | HIGH |
| KC | 00-0030506 | TE | 5.7 (3.0–8.0) | 0.8 (0.0–1.0) | 17.5% | 3.7% | HIGH |
| KC | 00-0038997 | WR | 5.7 (3.0–8.0) | 0.6 (0.0–0.0) | 17.4% | 2.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 15 market(s), e.g. KXNFLPASSYDS-26NOV15KCATL-ATLMPENIX9-250, KXNFLRECYDS-26NOV15KCATL-ATLOZACCHEAUS14-40
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 82 market(s), e.g. KXNFL2H-26NOV15KCATL-ATL, KXNFL4QTOTAL-26NOV15KCATL-21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26NOV15KCATL-KC15, KXNFLSPREAD-26NOV15KCATL-KC14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLGAME-26NOV15KCATL-KC, KXNFLTEAMTOTAL-26NOV15KCATL-KC22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 216 market(s), e.g. KXNFL1HFT-26NOV15KCATL-TIEKC, KXNFL1HFT-26NOV15KCATL-TIEATL
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 42 market(s), e.g. KXNFLLONGRSH-26NOV15KCATL-KCEJOHNSON10-6, KXNFLREC-26NOV15KCATL-KCTKELCE87-2

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.2%  _(final margin within one score (8 points) either way; total within 10 of the centre 47.875 (median favourite-oriented margin +1, median total 47))_
2. favourite controls / normal scoring — 17.1%  _(KC (favourite) wins by more than one score; total within 10 of the centre 47.875 (median favourite-oriented margin +15, median total 48))_
3. competitive / high scoring — 11.9%  _(final margin within one score (8 points) either way; total 57.875+ (centre 47.875) (median favourite-oriented margin +1, median total 65))_
4. competitive / low scoring — 10.3%  _(final margin within one score (8 points) either way; total 37.875 or fewer (centre 47.875) (median favourite-oriented margin +3, median total 33))_
5. favourite controls / high scoring — 7.9%  _(KC (favourite) wins by more than one score; total 57.875+ (centre 47.875) (median favourite-oriented margin +16, median total 65))_
   Other — 21.6%

Marginal events (overlapping): one_score 53.4% · blowout_17 18.8% · favorite_wins 63.8% · favorite_controls 32.6% · upset 36.0% · shootout 23.7% · low_scoring 20.3% · low_possession 11.8% · high_volume_passing 7.3% · run_heavy_control 10.9%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.10 mph, gusts 4.70, precip prob 0%, temp 54F, forecast retrieved 2026-11-14T21:22:58+00:00 (20.62 h before kickoff)._

**`KXNFLTD-26NOV15KCATL-KCJROYALS11-1`** Jalen Royals touchdowns 1
- MODEL / MARKET: football 10.9% · market 6.5% · reconciled 14.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.8% · failure mass 100.0% · win-contribution HHI 0.180

**`KXNFLTD-26NOV15KCATL-KCEJOHNSON10-1`** Emmett Johnson touchdowns 1
- MODEL / MARKET: football 34.5% · market 58.5% · reconciled 53.4%
- SCRIPT ROBUSTNESS: P50 mass 7.9% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 21.9% · failure mass 92.1% · win-contribution HHI 0.178

**`KXNFLTD-26NOV15KCATL-KCEJOHNSON10-2`** Emmett Johnson touchdowns 2
- MODEL / MARKET: football 8.5% · market 21.5% · reconciled 17.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 1.8% · failure mass 100.0% · win-contribution HHI 0.203

**`KXNFLTD-26NOV15KCATL-ATLBROBINSON7-1`** Bijan Robinson touchdowns 1
- MODEL / MARKET: football 58.3% · market 64.5% · reconciled 62.1%
- SCRIPT ROBUSTNESS: P50 mass 65.0% · P55 mass 65.0% · P60 mass 65.0% · major-script floor 43.8% · failure mass 34.9% · win-contribution HHI 0.184

_373 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 42 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (7)**

- Brian Robinson Jr. (RB, ATL) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Kenneth Walker III (RB, KC) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Zachariah Branch (WR, ATL) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Jaylon Moore (OT, KC) — Out [high] · **CHANGED from Questionable** — ruled out
- Divine Deablo (LB, ATL) — Out [conflicting] · **CHANGED from Questionable** — ruled out
- Peter Woods (DT, KC) — Out [high] · **NEW** — ruled out
- Samson Ebukam (DE, ATL) — Injured Reserve [high] · **CHANGED from Active** — ruled out

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Jaydn Ott (RB, KC) — Questionable [high]
- Gervon Dexter Sr. (DT, ATL) — Questionable [high]
- James Pearce Jr. (LB, ATL) — Questionable [high]
- Josh Woods (LB, ATL) — Questionable [high]
- Mansoor Delane (CB, KC) — Questionable [high]

### WEATHER

- retractable roof (Mercedes-Benz Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Partly Sunny · 56°F · wind 0 mph  · precip 0%
- forecast vintage 2026-11-14T21:22:58+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 56 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Michael Penix Jr. | ATL | attempts | 31.4 | 32.0 | 27.0 | 37.0 | 18.0 | 44.0 | 32.0 | 32.0 | 31.4 | 32.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bijan Robinson | ATL | carries | 19.2 | 19.0 | 14.0 | 24.0 | 7.0 | 32.0 | 20.0 | 20.0 | 19.2 | 19.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | completions | 19.7 | 20.0 | 16.0 | 23.0 | 11.0 | 29.0 | 20.4 | 20.0 | 19.7 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Michael Penix Jr. | ATL | passing_tds | 1.3 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Michael Penix Jr. | ATL | passing_yards | 208.2 | 203.0 | 157.0 | 254.0 | 96.0 | 338.0 | 222.3 | 216.0 | 222.3 | 217.0 | 0.00 | 0.97 | 9 | PRICED |
| Drake London | ATL | receiving_yards | 67.4 | 59.0 | 31.0 | 94.0 | 1.0 | 160.0 | 77.3 | 70.0 | 77.2 | 68.0 | 0.00 | 0.97 | 12 | PRICED |
| Kyle Pitts Sr. | ATL | receiving_yards | 34.5 | 27.0 | 11.0 | 50.0 | 0.0 | 95.0 | 42.2 | 36.0 | 42.2 | 33.0 | 0.00 | 0.97 | 11 | PRICED |
| Jahan Dotson | ATL | receiving_yards | 30.9 | 20.0 | 0.0 | 46.0 | 0.0 | 100.0 | 35.6 | 27.0 | 35.6 | 24.0 | 0.00 | 0.97 | 11 | PRICED |

_8 of 56 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 56 of 106 listed player/stat groups simulated and exposed, 50 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-30` | Emmett Johnson | 30.0 | 0.91 | 0.91 | 0.17 | -0.733 |
| `KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-40` | Emmett Johnson | 40.0 | 0.84 | 0.85 | 0.11 | -0.730 |
| `KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-25` | Emmett Johnson | 25.0 | 0.94 | 0.94 | 0.21 | -0.724 |
| `KXNFLRECYDS-26NOV15KCATL-KCEJOHNSON10-10` | Emmett Johnson | 10.0 | 0.77 | 0.78 | 0.06 | -0.711 |
| `KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-20` | Emmett Johnson | 20.0 | 0.96 | 0.97 | 0.26 | -0.704 |
| `KXNFLREC-26NOV15KCATL-KCEJOHNSON10-2` | Emmett Johnson | 2.0 | 0.83 | 0.84 | 0.16 | -0.674 |

_Ranked 389 tradable markets; 29 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Zachariah Branch (WR, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Brian Robinson Jr. (RB, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Jaydn Ott (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-25 moved +0.830 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.733 on KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-30 (Emmett Johnson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.730 on KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-40 (Emmett Johnson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRSHYDS-26NOV15KCATL-KCEJOHNSON10-30 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_KC_ATL.md`_


---

## MIA @ IND — `2026_10_MIA_IND`

- kickoff: 2026-11-15T18:00:00+00:00 (1194 minutes away) · state **PREGAME**
- venue: Lucas Oil Stadium · roof  · surface fieldturf
- markets: 737 listed across 16 families — 392 supported, 288 no model, 48 rules unresolved, 9 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 9 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | IND -4.1 | IND -4 |
| total | 38.50 | 38.42 |
| score | IND 21.3 – MIA 17.2 | IND 21.2 – MIA 17.2 |
| win prob IND | 66.5% | 65.3% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread IND -3 / total 19.18 · **2H** spread IND -2 / total 18.46 · **1Q** spread IND -1.2 / total 7.54 · **2Q** spread IND -2.2 / total 10.79 · **3Q** spread IND -1.1 / total 7.56 · **4Q** spread IND -1.1 / total 9.83

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread IND -4.1 · total 38.50
- move `KXNFLTOTAL-26NOV15MIAIND-42` -0.225
- move `KXNFLTOTAL-26NOV15MIAIND-41` -0.215
- move `KXNFLTOTAL-26NOV15MIAIND-40` -0.215
- move `KXNFLTOTAL-26NOV15MIAIND-37` -0.185

**Game environment** (simulation, mean and middle 50%) — projected spread IND -4.7 · raw home-minus-away margin 4.7 (-3.0–12.0) · total 39.7 (31.0–48.0) · P(one score) 51.9% · P(17+ blowout) 17.4% · P(total 10+ over centre) 23.6%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| IND | 62.4 (57.0–68.0) | 31.1 (26.0–36.0) | 26.6 (21.0–31.0) | 34.8 (29.0–40.0) | 0.559 (0.491–0.628) | 0.480 / 0.655 |
| MIA | 59.2 (53.0–65.0) | 28.6 (24.0–33.0) | 26.0 (21.0–30.0) | 32.6 (28.0–37.0) | 0.552 (0.487–0.618) | 0.446 / 0.617 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| IND | 00-0036223 | RB | 5.3 (3.0–7.0) | 13.9 (9.0–19.0) | 17.8% | 52.4% | MEDIUM |
| IND | 00-0040128 | TE | 10.0 (7.0–13.0) | 0.2 (0.0–0.0) | 33.8% | 0.7% | MEDIUM |
| IND | 00-0041125 | RB | 1.7 (0.0–2.0) | 5.4 (1.0–8.0) | 5.6% | 20.2% | HIGH |
| IND | 00-0032951 | WR | 5.3 (3.0–7.0) | 0.1 (0.0–0.0) | 17.7% | 0.5% | HIGH |
| MIA | 00-0040198 | RB | 2.2 (0.0–3.0) | 16.3 (11.0–21.0) | 7.9% | 62.8% | MEDIUM |
| MIA | 00-0039880 | WR | 6.0 (3.0–8.0) | 1.2 (0.0–1.0) | 22.1% | 4.4% | HIGH |
| MIA | 00-0041523 | WR | 6.4 (4.0–9.0) | 0.0 (0.0–0.0) | 23.4% | 0.2% | HIGH |
| MIA | 00-0039874 | RB | 0.9 (0.0–1.0) | 4.1 (1.0–6.0) | 3.1% | 15.9% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 33 market(s), e.g. KXNFLPASSATT-26NOV15MIAIND-INDDJONES17-30, KXNFLPASSCOMP-26NOV15MIAIND-INDDJONES17-24
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 49 market(s), e.g. KXNFL1HFT-26NOV15MIAIND-MIAMIA, KXNFL1HSPREAD-26NOV15MIAIND-IND7
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 19 market(s), e.g. KXNFLSPREAD-26NOV15MIAIND-IND15, KXNFLTEAMTOTAL-26NOV15MIAIND-IND29
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLGAME-26NOV15MIAIND-IND, KXNFLSPREAD-26NOV15MIAIND-IND3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 220 market(s), e.g. KXNFL1HFT-26NOV15MIAIND-TIEMIA, KXNFL1HFT-26NOV15MIAIND-TIEIND
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 18 market(s), e.g. KXNFLTEAMTOTAL-26NOV15MIAIND-IND11, KXNFL2HTOTAL-26NOV15MIAIND-8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 30.1%  _(final margin within one score (8 points) either way; total within 10 of the centre 38.5 (median favourite-oriented margin +2, median total 38))_
2. favourite controls / normal scoring — 20.3%  _(IND (favourite) wins by more than one score; total within 10 of the centre 38.5 (median favourite-oriented margin +14, median total 38))_
3. competitive / high scoring — 11.5%  _(final margin within one score (8 points) either way; total 48.5+ (centre 38.5) (median favourite-oriented margin +3, median total 56))_
4. competitive / low scoring — 10.3%  _(final margin within one score (8 points) either way; total 28.5 or fewer (centre 38.5) (median favourite-oriented margin +3, median total 23))_
5. favourite controls / high scoring — 8.5%  _(IND (favourite) wins by more than one score; total 48.5+ (centre 38.5) (median favourite-oriented margin +16, median total 56))_
   Other — 19.4%

Marginal events (overlapping): one_score 51.9% · blowout_17 17.4% · favorite_wins 66.6% · favorite_controls 35.4% · upset 33.2% · shootout 23.6% · low_scoring 20.0% · low_possession 20.2% · high_volume_passing 0.9% · run_heavy_control 17.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.50 mph, gusts 10.30, precip prob 0%, temp 48F, forecast retrieved 2026-11-14T21:22:58+00:00 (20.62 h before kickoff)._

**`KXNFLTD-26NOV15MIAIND-MIAJWRIGHT5-1`** Jaylen Wright touchdowns 1
- MODEL / MARKET: football 10.8% · market 8.5% · reconciled 23.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.8% · failure mass 100.0% · win-contribution HHI 0.180

**`KXNFLTD-26NOV15MIAIND-MIAKALLEN31-1`** Kaytron Allen touchdowns 1
- MODEL / MARKET: football 6.5% · market 4.5% · reconciled 10.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.2% · failure mass 100.0% · win-contribution HHI 0.183

**`KXNFLTD-26NOV15MIAIND-MIAJWRIGHT5-2`** Jaylen Wright touchdowns 2
- MODEL / MARKET: football 1.2% · market 0.5% · reconciled 2.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.2% · failure mass 100.0% · win-contribution HHI 0.198

**`KXNFLTD-26NOV15MIAIND-INDJTAYLOR28-2`** Jonathan Taylor touchdowns 2
- MODEL / MARKET: football 16.5% · market 13.5% · reconciled 15.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 2.8% · failure mass 100.0% · win-contribution HHI 0.210

_382 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 44 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (13)**

- Malik Willis (QB, MIA) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Alec Pierce (WR, IND) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jared Wayne (WR, MIA) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Mo Alie-Cox (TE, IND) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Will Mallory (TE, IND) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Aaron Brewer (C, MIA) — Out [high] · **NEW** — ruled out
- Jalen Travis (OT, IND) — Out [single_source] · **NEW** — ruled out
- Akeem Davis-Gaither (LB, IND) — Injured Reserve [high] · **CHANGED from Active** — ruled out
- _...and 5 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Chris Bell (WR, MIA) — Doubtful [high]

### WEATHER

- retractable roof (Lucas Oil Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Mostly Cloudy · 48°F · wind 5 mph N · precip 0%
- forecast vintage 2026-11-14T21:23:01+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 56 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Daniel Jones | IND | attempts | 29.8 | 30.0 | 25.0 | 35.0 | 17.0 | 43.0 | 30.2 | 30.0 | 29.8 | 30.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jonathan Taylor | IND | carries | 13.9 | 13.0 | 9.0 | 19.0 | 3.0 | 27.0 | 16.1 | 16.0 | 13.9 | 13.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Daniel Jones | IND | completions | 20.5 | 20.0 | 17.0 | 24.0 | 11.0 | 30.0 | 19.1 | 19.0 | 20.5 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Daniel Jones | IND | passing_tds | 1.2 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.2 | 1.0 | 1.2 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Daniel Jones | IND | passing_yards | 196.9 | 193.0 | 150.0 | 240.0 | 90.0 | 317.0 | 189.3 | 181.0 | 189.3 | 185.0 | 0.00 | 0.97 | 9 | PRICED |
| Tyler Warren | IND | receiving_yards | 69.0 | 63.0 | 38.0 | 94.0 | 8.0 | 149.0 | 50.3 | 44.0 | 50.3 | 46.0 | 0.00 | 0.98 | 11 | PRICED |
| Laquon Treadwell | IND | receiving_yards | 40.8 | 33.0 | 13.0 | 59.0 | 0.0 | 112.0 | 36.2 | 27.0 | 36.2 | 29.0 | 0.00 | 0.97 | 11 | PRICED |
| Jonathan Taylor | IND | receiving_yards | 31.4 | 25.0 | 11.0 | 45.0 | 0.0 | 85.0 | 26.9 | 21.0 | 26.9 | 21.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 56 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 56 of 89 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHYDS-26NOV15MIAIND-MIAOGORDON0-40` | Ollie Gordon II | 40.0 | 0.83 | 0.85 | 0.09 | -0.737 |
| `KXNFLRSHYDS-26NOV15MIAIND-MIAOGORDON0-50` | Ollie Gordon II | 50.0 | 0.73 | 0.76 | 0.06 | -0.677 |
| `KXNFLRSHATT-26NOV15MIAIND-MIAOGORDON0-15` | Ollie Gordon II | 15.0 | 0.74 | 0.76 | 0.09 | -0.653 |
| `KXNFLREC-26NOV15MIAIND-INDTWARREN84-4` | Tyler Warren | 4.0 | 0.80 | 0.82 | 0.16 | -0.649 |
| `KXNFLREC-26NOV15MIAIND-INDTWARREN84-3` | Tyler Warren | 3.0 | 0.91 | 0.93 | 0.28 | -0.631 |
| `KXNFLREC-26NOV15MIAIND-INDTWARREN84-5` | Tyler Warren | 5.0 | 0.68 | 0.69 | 0.08 | -0.595 |

_Ranked 391 tradable markets; 1 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Will Mallory (TE, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Alec Pierce (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLFFPTS-26NOV15MIAIND-MIAKMCCORD14-12P5 moved -0.370 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.737 on KXNFLRSHYDS-26NOV15MIAIND-MIAOGORDON0-40 (Ollie Gordon II). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.677 on KXNFLRSHYDS-26NOV15MIAIND-MIAOGORDON0-50 (Ollie Gordon II). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26NOV15MIAIND-INDTWARREN84-3 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_MIA_IND.md`_


---

## MIN @ GB — `2026_10_MIN_GB`

- kickoff: 2026-11-15T18:00:00+00:00 (1194 minutes away) · state **PREGAME**
- venue: Lambeau Field · roof outdoors · surface grass
- markets: 759 listed across 16 families — 416 supported, 287 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | GB -2.9 | GB -2.5 |
| total | 42.62 | 42.44 |
| score | GB 22.8 – MIN 19.9 | GB 22.5 – MIN 20.0 |
| win prob GB | 58.5% | 58.7% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread GB -1.7 / total 20.81 · **2H** spread GB -1.4 / total 21.00 · **1Q** spread GB -0.3 / total 7.74 · **2Q** spread GB -0.6 / total 12.22 · **3Q** spread GB -0.4 / total 8.00 · **4Q** spread GB -0.1 / total 11.75

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread GB -2.9 · total 42.62

**Game environment** (simulation, mean and middle 50%) — projected spread GB -2.6 · raw home-minus-away margin 2.6 (-5.0–10.0) · total 43.5 (34.0–51.0) · P(one score) 52.8% · P(17+ blowout) 18.2% · P(total 10+ over centre) 23.0%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| GB | 62.5 (57.0–68.0) | 34.4 (29.0–39.0) | 23.4 (18.0–28.0) | 38.2 (33.0–43.0) | 0.611 (0.544–0.680) | 0.523 / 0.701 |
| MIN | 61.3 (56.0–67.0) | 33.6 (29.0–38.0) | 23.5 (19.0–28.0) | 37.2 (32.0–42.0) | 0.608 (0.541–0.675) | 0.506 / 0.680 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| GB | 00-0039811 | RB | 2.0 (0.0–3.0) | 7.0 (3.0–10.0) | 6.0% | 30.0% | HIGH |
| GB | 00-0040667 | WR | 8.4 (5.0–11.0) | 0.2 (0.0–0.0) | 25.3% | 0.9% | MEDIUM |
| GB | 00-0040142 | RB | 0.5 (0.0–1.0) | 7.5 (3.0–11.0) | 1.5% | 32.0% | HIGH |
| GB | 00-0038124 | WR | 7.7 (4.0–10.0) | 0.1 (0.0–0.0) | 23.4% | 0.4% | MEDIUM |
| MIN | 00-0033293 | RB | 3.8 (1.0–6.0) | 9.4 (5.0–13.0) | 12.0% | 40.2% | MEDIUM |
| MIN | 00-0037525 | RB | 2.0 (0.0–3.0) | 10.3 (6.0–14.0) | 6.3% | 44.0% | MEDIUM |
| MIN | 00-0036322 | WR | 11.8 (8.0–15.0) | 0.1 (0.0–0.0) | 36.8% | 0.5% | MEDIUM |
| MIN | 00-0038994 | WR | 5.5 (1.0–8.0) | 0.2 (0.0–0.0) | 17.2% | 0.7% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 9 market(s), e.g. KXNFLRSHYDS-26NOV15MINGB-GBJLOVE10-5, KXNFLRSHYDS-26NOV15MINGB-MINKCOUSINS8-15
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 81 market(s), e.g. KXNFL1QTOTAL-26NOV15MINGB-14, KXNFL2H-26NOV15MINGB-MIN
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLBOTH-26NOV15MINGB-21, KXNFLSPREAD-26NOV15MINGB-MIN8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTOTAL-26NOV15MINGB-37, KXNFLTEAMTOTAL-26NOV15MINGB-GB18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 216 market(s), e.g. KXNFL1HSPREAD-26NOV15MINGB-GB14, KXNFL1QSPREAD-26NOV15MINGB-GB8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 30 market(s), e.g. KXNFLPASSCOMP-26NOV15MINGB-MINKCOUSINS8-17, KXNFLREC-26NOV15MINGB-MINJJEFFERSON18-3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.2%  _(final margin within one score (8 points) either way; total within 10 of the centre 42.625 (median favourite-oriented margin +2, median total 43))_
2. favourite controls / normal scoring — 17.3%  _(GB (favourite) wins by more than one score; total within 10 of the centre 42.625 (median favourite-oriented margin +13, median total 42))_
3. competitive / low scoring — 12.3%  _(final margin within one score (8 points) either way; total 32.625 or fewer (centre 42.625) (median favourite-oriented margin +2, median total 27))_
4. competitive / high scoring — 11.3%  _(final margin within one score (8 points) either way; total 52.625+ (centre 42.625) (median favourite-oriented margin +1, median total 60))_
5. underdog controls / normal scoring — 9.8%  _(MIN (underdog) wins by more than one score; total within 10 of the centre 42.625 (median favourite-oriented margin -13, median total 43))_
   Other — 20.0%

Marginal events (overlapping): one_score 52.8% · blowout_17 18.2% · favorite_wins 60.2% · favorite_controls 29.6% · upset 39.6% · shootout 23.0% · low_scoring 20.7% · low_possession 13.7% · high_volume_passing 8.8% · run_heavy_control 11.0%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 2.70 mph, gusts 5.40, precip prob 0%, temp 42F, forecast retrieved 2026-11-14T21:22:58+00:00 (20.62 h before kickoff)._

**`KXNFLTD-26NOV15MINGB-GBKJOHNSON26-1`** Kaleb Johnson touchdowns 1
- MODEL / MARKET: football 20.3% · market 31.5% · reconciled 28.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 11.2% · failure mass 100.0% · win-contribution HHI 0.181

**`KXNFLTD-26NOV15MINGB-GBMLLOYD32-1`** MarShawn Lloyd touchdowns 1
- MODEL / MARKET: football 26.1% · market 18.5% · reconciled 20.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 14.6% · failure mass 100.0% · win-contribution HHI 0.181

**`KXNFLTD-26NOV15MINGB-MINKCOUSINS8-1`** Kirk Cousins touchdowns 1
- MODEL / MARKET: football 13.5% · market 5.5% · reconciled 7.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.2% · failure mass 100.0% · win-contribution HHI 0.175

**`KXNFLTD-26NOV15MINGB-MINGBARTHOLOMEW86-1`** Gavin Bartholomew touchdowns 1
- MODEL / MARKET: football 6.6% · market 17.5% · reconciled 15.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 3.4% · failure mass 100.0% · win-contribution HHI 0.169

_393 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 44 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (11)**

- Kyler Murray (QB, MIN) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Demond Claiborne (RB, MIN) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Jauan Jennings (WR, MIN) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Josh Jacobs (RB, GB) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Josh Whyle (TE, GB) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- T.J. Hockenson (TE, MIN) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Sean Rhyan (G, GB) — Out [high] — ruled out
- Blake Cashman (LB, MIN) — Out [high] · **CHANGED from Active** — ruled out
- _...and 3 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (11)** — resolves at the inactive release, T−90m

- Chris Brooks (RB, GB) — Questionable [high]
- Jordan Addison (WR, MIN) — Questionable [high]
- Skyy Moore (WR, GB) — Questionable [high]
- Kevin Zeitler (G, GB) — Questionable [single_source]
- Travis Glover (OT, GB) — Questionable [single_source]
- Javon Bullard (S, GB) — Questionable [high]
- Joshua Metellus (S, MIN) — Questionable [high]
- Kyle Van Noy (LB, MIN) — Questionable [high]

### WEATHER

- Mostly Sunny · 43°F · wind 1 mph W · precip 0%
- forecast vintage 2026-11-14T21:23:00+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 59 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jordan Love | GB | attempts | 33.1 | 33.0 | 28.0 | 39.0 | 19.0 | 46.0 | 36.4 | 36.0 | 33.1 | 33.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kaleb Johnson | GB | carries | 7.5 | 6.0 | 3.0 | 11.0 | 0.0 | 18.0 | 9.7 | 9.0 | 7.5 | 6.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jordan Love | GB | completions | 20.5 | 20.0 | 17.0 | 24.0 | 11.0 | 30.0 | 21.8 | 21.0 | 20.5 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jordan Love | GB | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.8 | 2.0 | 1.8 | 2.0 | 0.00 | 0.97 | 4 | PRICED |
| Jordan Love | GB | passing_yards | 255.4 | 250.0 | 196.0 | 311.0 | 119.0 | 411.0 | 258.1 | 253.0 | 258.1 | 252.0 | 0.00 | 0.97 | 10 | PRICED |
| Christian Watson | GB | receiving_yards | 74.4 | 64.0 | 31.0 | 106.0 | 0.0 | 183.0 | 81.5 | 73.0 | 81.4 | 70.0 | 0.00 | 0.97 | 13 | PRICED |
| Matthew Golden | GB | receiving_yards | 73.2 | 64.0 | 32.0 | 103.0 | 0.0 | 176.0 | 75.7 | 67.0 | 75.6 | 66.0 | 0.00 | 0.98 | 13 | PRICED |
| Tucker Kraft | GB | receiving_yards | 40.3 | 32.0 | 13.0 | 58.0 | 0.0 | 110.0 | 41.9 | 35.0 | 41.9 | 33.0 | 0.00 | 0.97 | 11 | PRICED |

_8 of 59 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 59 of 90 listed player/stat groups simulated and exposed, 31 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRECYDS-26NOV15MINGB-GBSWILLIAMS83-10` | Savion Williams | 10.0 | 0.70 | 0.72 | 0.01 | -0.692 |
| `KXNFLREC-26NOV15MINGB-GBMGOLDEN0-3` | Matthew Golden | 3.0 | 0.89 | 0.92 | 0.22 | -0.664 |
| `KXNFLREC-26NOV15MINGB-GBMGOLDEN0-4` | Matthew Golden | 4.0 | 0.76 | 0.78 | 0.13 | -0.633 |
| `KXNFLREC-26NOV15MINGB-GBSWILLIAMS83-2` | Savion Williams | 2.0 | 0.64 | 0.65 | 0.01 | -0.625 |
| `KXNFLREC-26NOV15MINGB-MINJJEFFERSON18-5` | Justin Jefferson | 5.0 | 0.76 | 0.77 | 0.14 | -0.612 |
| `KXNFLREC-26NOV15MINGB-MINJJEFFERSON18-4` | Justin Jefferson | 4.0 | 0.87 | 0.90 | 0.26 | -0.608 |

_Ranked 403 tradable markets; 13 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Josh Jacobs (RB, GB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Josh Whyle (TE, GB) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 3 skill players are Questionable (Chris Brooks (RB), Skyy Moore (WR), Jordan Addison (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLFFPTS-26NOV15MINGB-MINJADDISON3-9 moved -0.175 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.692 on KXNFLRECYDS-26NOV15MINGB-GBSWILLIAMS83-10 (Savion Williams). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.664 on KXNFLREC-26NOV15MINGB-GBMGOLDEN0-3 (Matthew Golden). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV15MINGB-GBMGOLDEN0-3 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_MIN_GB.md`_


---

## LA @ ARI — `2026_10_LA_ARI`

- kickoff: 2026-11-15T21:05:00+00:00 (1378 minutes away) · state **PREGAME**
- venue: State Farm Stadium · roof  · surface grass
- markets: 818 listed across 16 families — 421 supported, 304 no model, 48 rules unresolved, 45 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 45 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | LA -9.3 | LA -9.9 |
| total | 39.88 | 39.35 |
| score | ARI 15.3 – LA 24.6 | ARI 14.7 – LA 24.6 |
| win prob ARI | 19.5% | 18.8% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread LA -5.2 / total 20.39 · **2H** spread LA -4.2 / total 19.67 · **1Q** spread LA -2.6 / total 7.67 · **2Q** spread LA -3.2 / total 11.43 · **3Q** spread LA -2.7 / total 7.78 · **4Q** spread LA -2.6 / total 10.03

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread LA -9.3 · total 39.88
- move `KXNFLTOTAL-26NOV15LARARI-46` -0.300
- move `KXNFLTOTAL-26NOV15LARARI-42` -0.230
- move `KXNFLTOTAL-26NOV15LARARI-47` -0.205
- move `KXNFLTOTAL-26NOV15LARARI-45` -0.185

**Game environment** (simulation, mean and middle 50%) — projected spread LA -9.7 · raw home-minus-away margin -9.7 (-17.0–-3.0) · total 40.4 (31.0–49.0) · P(one score) 37.2% · P(17+ blowout) 28.7% · P(total 10+ over centre) 22.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| ARI | 62.2 (57.0–68.0) | 37.1 (32.0–42.0) | 20.3 (16.0–25.0) | 41.5 (36.0–47.0) | 0.668 (0.604–0.735) | 0.543 / 0.714 |
| LA | 64.5 (59.0–70.0) | 33.5 (28.0–39.0) | 27.8 (23.0–33.0) | 35.6 (30.0–41.0) | 0.551 (0.482–0.620) | 0.491 / 0.668 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| ARI | 00-0037263 | RB | 4.4 (2.0–6.0) | 12.8 (8.0–17.0) | 12.4% | 62.9% | MEDIUM |
| ARI | 00-0037744 | TE | 13.0 (9.0–17.0) | 0.0 (0.0–0.0) | 36.8% | 0.1% | MEDIUM |
| ARI | 00-0037157 | RB | 2.8 (1.0–4.0) | 4.7 (1.0–7.0) | 8.0% | 23.2% | HIGH |
| ARI | 00-0041070 | WR | 4.6 (2.0–6.0) | 0.1 (0.0–0.0) | 12.9% | 0.4% | HIGH |
| LA | 00-0037840 | RB | 5.0 (2.0–7.0) | 14.5 (9.0–19.0) | 15.6% | 52.0% | MEDIUM |
| LA | 00-0039738 | RB | 2.4 (0.0–4.0) | 9.5 (4.0–13.0) | 7.6% | 34.1% | HIGH |
| LA | 00-0033110 | TE | 6.2 (3.0–9.0) | 0.1 (0.0–0.0) | 19.1% | 0.3% | HIGH |
| LA | 00-0036244 | TE | 5.3 (2.0–7.0) | 0.1 (0.0–0.0) | 16.4% | 0.3% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 14 market(s), e.g. KXNFLPASSATT-26NOV15LARARI-LARMSTAFFORD9-32, KXNFLPASSCOMP-26NOV15LARARI-LARMSTAFFORD9-26
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 31 market(s), e.g. KXNFL1Q-26NOV15LARARI-TIE, KXNFL4QSPREAD-26NOV15LARARI-LAR8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 20 market(s), e.g. KXNFLBOTH-26NOV15LARARI-21, KXNFLGAME-26NOV15LARARI-ARI
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLSPREAD-26NOV15LARARI-LAR7, KXNFLSPREAD-26NOV15LARARI-LAR6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 265 market(s), e.g. KXNFL1H-26NOV15LARARI-TIE, KXNFL1HFT-26NOV15LARARI-TIELAR
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 20 market(s), e.g. KXNFL1HTOTAL-26NOV15LARARI-4, KXNFL2HTOTAL-26NOV15LARARI-8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 30.3%  _(LA (favourite) wins by more than one score; total within 10 of the centre 39.875 (median favourite-oriented margin +16, median total 39))_
2. competitive / normal scoring — 21.4%  _(final margin within one score (8 points) either way; total within 10 of the centre 39.875 (median favourite-oriented margin +3, median total 40))_
3. favourite controls / low scoring — 13.1%  _(LA (favourite) wins by more than one score; total 29.875 or fewer (centre 39.875) (median favourite-oriented margin +16, median total 25))_
4. favourite controls / high scoring — 11.9%  _(LA (favourite) wins by more than one score; total 49.875+ (centre 39.875) (median favourite-oriented margin +17, median total 57))_
5. competitive / high scoring — 8.8%  _(final margin within one score (8 points) either way; total 49.875+ (centre 39.875) (median favourite-oriented margin +3, median total 57))_
   Other — 14.6%

Marginal events (overlapping): one_score 37.2% · blowout_17 28.7% · favorite_wins 81.3% · favorite_controls 55.2% · upset 18.6% · shootout 22.8% · low_scoring 21.3% · low_possession 7.9% · high_volume_passing 15.6% · run_heavy_control 21.2%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 1.40 mph, gusts 2.20, precip prob 0%, temp 74F, forecast retrieved 2026-11-14T21:22:58+00:00 (23.70 h before kickoff)._

**`KXNFLTD-26NOV15LARARI-ARITQUITORIANO47-1`** Teagan Quitoriano touchdowns 1
- MODEL / MARKET: football 4.2% · market 3.5% · reconciled 7.4%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.4% · failure mass 100.0% · win-contribution HHI 0.182

**`KXNFLTD-26NOV15LARARI-ARITMCBRIDE85-1`** Trey McBride touchdowns 1
- MODEL / MARKET: football 32.7% · market 25.5% · reconciled 27.5%
- SCRIPT ROBUSTNESS: P50 mass 15.2% · P55 mass 10.9% · P60 mass 2.1% · major-script floor 5.1% · failure mass 84.8% · win-contribution HHI 0.179

**`KXNFLTD-26NOV15LARARI-ARIZKNIGHT20-1`** Bam Knight touchdowns 1
- MODEL / MARKET: football 13.8% · market 22.5% · reconciled 20.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 1.8% · failure mass 100.0% · win-contribution HHI 0.169

**`KXNFLTD-26NOV15LARARI-LARCDANIELS6-1`** CJ Daniels touchdowns 1
- MODEL / MARKET: football 0.9% · market 11.5% · reconciled 9.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 0.5% · failure mass 100.0% · win-contribution HHI 0.230

_414 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 39 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (11)**

- Gardner Minshew II (QB, ARI) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Davante Adams (WR, LA) — Injured Reserve [single_source] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Hunter Long (TE, ARI) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Jordan Whittington (WR, LA) — Injured Reserve [single_source] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Michael Wilson (WR, ARI) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Puka Nacua (WR, LA) — Injured Reserve [single_source] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Terrance Ferguson (TE, LA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Hjalte Froholdt (C, ARI) — Out [high] · **NEW** — ruled out
- _...and 3 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (9)** — resolves at the inactive release, T−90m

- Davis Allen (TE, LA) — Questionable [single_source]
- Jayden Williams (OT, ARI) — Questionable [high]
- Andrew Wingard (S, ARI) — Questionable [high]
- Darius Robinson (DE, ARI) — Questionable [high]
- Joe Cardona (LS, LA) — Questionable [single_source]
- Kam Curl (S, LA) — Questionable [single_source]
- Max Melton (CB, ARI) — Questionable [high]
- Myles Garrett (DE, LA) — Questionable [single_source]

### WEATHER

- retractable roof (State Farm Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Sunny · 76°F · wind 5 mph N · precip 0%
- forecast vintage 2026-11-14T21:23:06+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 58 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tyler Allgeier | ARI | carries | 12.8 | 12.0 | 8.0 | 17.0 | 3.0 | 24.0 | 10.4 | 10.0 | 12.8 | 12.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bam Knight | ARI | carries | 4.7 | 4.0 | 1.0 | 7.0 | 0.0 | 13.0 | 8.7 | 8.0 | 4.7 | 4.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Trey McBride | ARI | receiving_yards | 84.3 | 79.0 | 50.0 | 113.0 | 15.0 | 172.0 | 64.5 | 58.0 | 64.5 | 60.0 | 0.00 | 0.98 | 11 | PRICED |
| Reggie Virgil | ARI | receiving_yards | 32.2 | 23.0 | 6.0 | 48.0 | 0.0 | 100.0 | 32.7 | 24.0 | 32.7 | 23.0 | 0.00 | 0.97 | 11 | PRICED |
| Elijah Higgins | ARI | receiving_yards | 22.2 | 15.0 | 2.0 | 33.0 | 0.0 | 73.0 | 23.2 | 18.0 | 23.2 | 15.0 | 0.00 | 0.97 | 9 | PRICED |
| Tyler Allgeier | ARI | receiving_yards | 20.6 | 15.0 | 5.0 | 30.0 | 0.0 | 62.0 | 15.0 | 10.0 | 15.0 | 11.0 | 0.00 | 0.97 | 7 | PRICED |
| Devin Duvernay | ARI | receiving_yards | 15.7 | 7.0 | 0.0 | 24.0 | 0.0 | 61.0 | 19.5 | 12.0 | 19.5 | 9.0 | 0.00 | 0.98 | 9 | PRICED |
| Bam Knight | ARI | receiving_yards | 14.0 | 8.0 | 0.0 | 21.0 | 0.0 | 49.0 | 10.7 | 7.0 | 10.7 | 6.0 | 0.00 | 0.98 | 6 | PRICED |

_8 of 58 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 58 of 102 listed player/stat groups simulated and exposed, 44 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV15LARARI-ARITMCBRIDE85-5` | Trey McBride | 5.0 | 0.79 | 0.82 | 0.15 | -0.649 |
| `KXNFLREC-26NOV15LARARI-ARITMCBRIDE85-4` | Trey McBride | 4.0 | 0.89 | 0.91 | 0.27 | -0.623 |
| `KXNFLREC-26NOV15LARARI-ARITMCBRIDE85-6` | Trey McBride | 6.0 | 0.67 | 0.69 | 0.07 | -0.595 |
| `KXNFLREC-26NOV15LARARI-LARTHIGBEE89-2` | Tyler Higbee | 2.0 | 0.88 | 0.89 | 0.31 | -0.566 |
| `KXNFLRSHATT-26NOV15LARARI-LARBCORUM24-9` | Blake Corum | 9.0 | 0.80 | 0.81 | 0.26 | -0.540 |
| `KXNFLRSHATT-26NOV15LARARI-LARKWILLIAMS23-13` | Kyren Williams | 13.0 | 0.72 | 0.74 | 0.18 | -0.539 |

_Ranked 416 tradable markets; 5 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Gardner Minshew II (QB, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Hunter Long (TE, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Davis Allen (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLTOTAL-26NOV15LARARI-46 moved -0.300 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.649 on KXNFLREC-26NOV15LARARI-ARITMCBRIDE85-5 (Trey McBride). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.623 on KXNFLREC-26NOV15LARARI-ARITMCBRIDE85-4 (Trey McBride). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV15LARARI-ARITMCBRIDE85-4 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_LA_ARI.md`_


---

## SEA @ LV — `2026_10_SEA_LV`

- kickoff: 2026-11-15T21:05:00+00:00 (1378 minutes away) · state **PREGAME**
- venue: Allegiant Stadium · roof dome · surface grass
- markets: 779 listed across 16 families — 400 supported, 290 no model, 48 rules unresolved, 41 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 41 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | SEA -6.6 | SEA -6.8 |
| total | 41.12 | 41.31 |
| score | LV 17.3 – SEA 23.8 | LV 17.3 – SEA 24.1 |
| win prob LV | 27.5% | 26.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread SEA -3.6 / total 20.65 · **2H** spread SEA -3.1 / total 19.61 · **1Q** spread SEA -1.8 / total 7.78 · **2Q** spread SEA -2.7 / total 12.24 · **3Q** spread SEA -1.1 / total 7.80 · **4Q** spread SEA -1.3 / total 10.57

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread SEA -6.6 · total 41.12
- move `KXNFLGAME-26NOV15SEALV-LV` -0.230
- move `KXNFLGAME-26NOV15SEALV-SEA` +0.170
- move `KXNFLTOTAL-26NOV15SEALV-43` -0.165
- move `KXNFLTOTAL-26NOV15SEALV-42` -0.165

**Game environment** (simulation, mean and middle 50%) — projected spread SEA -6.5 · raw home-minus-away margin -6.5 (-14.0–1.0) · total 42.8 (34.0–51.0) · P(one score) 48.1% · P(17+ blowout) 23.8% · P(total 10+ over centre) 24.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| LV | 60.8 (55.0–67.0) | 34.3 (29.0–39.0) | 21.7 (17.0–26.0) | 38.7 (33.0–44.0) | 0.637 (0.572–0.703) | 0.527 / 0.693 |
| SEA | 62.9 (57.0–69.0) | 29.9 (25.0–35.0) | 28.8 (24.0–34.0) | 33.0 (28.0–38.0) | 0.524 (0.457–0.593) | 0.455 / 0.630 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| LV | 00-0040122 | RB | 4.5 (2.0–6.0) | 10.5 (6.0–14.0) | 13.7% | 48.3% | MEDIUM |
| LV | 00-0040878 | RB | 0.9 (0.0–1.0) | 8.3 (4.0–12.0) | 2.8% | 38.5% | HIGH |
| LV | 00-0039338 | TE | 7.4 (4.0–10.0) | 0.5 (0.0–0.0) | 22.6% | 2.5% | MEDIUM |
| LV | 00-0038563 | WR | 5.2 (2.0–7.0) | 0.2 (0.0–0.0) | 15.8% | 1.1% | HIGH |
| SEA | 00-0039165 | RB | 1.7 (0.0–3.0) | 9.0 (4.0–13.0) | 5.9% | 31.3% | HIGH |
| SEA | 00-0038797 | RB | 1.3 (0.0–2.0) | 9.1 (4.0–13.0) | 4.7% | 31.6% | HIGH |
| SEA | 00-0041512 | RB | 2.5 (1.0–4.0) | 6.6 (2.0–10.0) | 8.6% | 22.8% | HIGH |
| SEA | 00-0038543 | WR | 8.1 (5.0–11.0) | 0.2 (0.0–0.0) | 28.4% | 0.7% | MEDIUM |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 23 market(s), e.g. KXNFLPASSATT-26NOV15SEALV-LVFMENDOZA15-36, KXNFLPASSATT-26NOV15SEALV-LVFMENDOZA15-31
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 65 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV15SEALV-SEA20, KXNFL1Q-26NOV15SEALV-TIE
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLBOTH-26NOV15SEALV-21, KXNFLGAME-26NOV15SEALV-LV
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLSPREAD-26NOV15SEALV-SEA4, KXNFLSPREAD-26NOV15SEALV-SEA3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 233 market(s), e.g. KXNFL1H-26NOV15SEALV-TIE, KXNFL1HFT-26NOV15SEALV-TIESEA
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 22 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV15SEALV-SEA3, KXNFL1HTOTAL-26NOV15SEALV-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 26.7%  _(final margin within one score (8 points) either way; total within 10 of the centre 41.125 (median favourite-oriented margin +3, median total 42))_
2. favourite controls / normal scoring — 23.1%  _(SEA (favourite) wins by more than one score; total within 10 of the centre 41.125 (median favourite-oriented margin +17, median total 41))_
3. competitive / high scoring — 11.5%  _(final margin within one score (8 points) either way; total 51.125+ (centre 41.125) (median favourite-oriented margin +3, median total 60))_
4. competitive / low scoring — 9.9%  _(final margin within one score (8 points) either way; total 31.125 or fewer (centre 41.125) (median favourite-oriented margin +3, median total 27))_
5. favourite controls / high scoring — 9.7%  _(SEA (favourite) wins by more than one score; total 51.125+ (centre 41.125) (median favourite-oriented margin +16, median total 56))_
   Other — 19.1%

Marginal events (overlapping): one_score 48.1% · blowout_17 23.8% · favorite_wins 73.4% · favorite_controls 41.2% · upset 26.4% · shootout 24.1% · low_scoring 20.0% · low_possession 14.2% · high_volume_passing 3.6% · run_heavy_control 20.0%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.40 mph, gusts 8.90, precip prob 1%, temp 67F, forecast retrieved 2026-11-14T21:22:58+00:00 (23.70 h before kickoff)._

**`KXNFLTD-26NOV15SEALV-SEAEWILSON23-1`** Emanuel Wilson touchdowns 1
- MODEL / MARKET: football 30.3% · market 6.5% · reconciled 23.5%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 27.1% · failure mass 100.0% · win-contribution HHI 0.189

**`KXNFLTD-26NOV15SEALV-SEAJSMITHNJIGBA11-1`** Jaxon Smith-Njigba touchdowns 1
- MODEL / MARKET: football 37.9% · market 47.5% · reconciled 44.9%
- SCRIPT ROBUSTNESS: P50 mass 21.2% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 35.5% · failure mass 78.8% · win-contribution HHI 0.184
- THESIS DEPENDENCY with `KXNFLPASSTDS-26NOV15SEALV-SEADLOCK2-2`: cash correlation 0.365 · joint cash 24.6% · Jaccard of winning rows 0.446 · shared failure 44.8%

**`KXNFLTD-26NOV15SEALV-SEAJPRICE8-1`** Jadarian Price touchdowns 1
- MODEL / MARKET: football 21.5% · market 32.5% · reconciled 30.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 18.2% · failure mass 100.0% · win-contribution HHI 0.185

**`KXNFLTD-26NOV15SEALV-SEAEWILSON23-2`** Emanuel Wilson touchdowns 2
- MODEL / MARKET: football 6.6% · market 1.5% · reconciled 3.0%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.3% · failure mass 100.0% · win-contribution HHI 0.218

_390 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 43 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Sam Darnold (QB, SEA) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Charles Cross (OT, SEA) — Out [high] · **CHANGED from Doubtful** — ruled out
- Quenton Nelson (G, SEA) — Out [high] · **NEW** — ruled out
- Leonard Williams (DT, SEA) — Out [high] · **NEW** — ruled out

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Dont'e Thornton Jr. (WR, LV) — Questionable [high]
- Thomas Booker IV (DT, LV) — Questionable [high]

### WEATHER

fixed-roof stadium (Allegiant Stadium) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 58 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fernando Mendoza | LV | attempts | 33.0 | 33.0 | 28.0 | 38.0 | 20.0 | 46.0 | 30.9 | 30.0 | 33.0 | 33.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Ashton Jeanty | LV | carries | 10.5 | 10.0 | 6.0 | 14.0 | 1.0 | 22.0 | 10.6 | 10.0 | 10.5 | 10.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Mike Washington Jr. | LV | carries | 8.3 | 7.0 | 4.0 | 12.0 | 1.0 | 19.0 | 9.0 | 9.0 | 8.3 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Fernando Mendoza | LV | completions | 20.7 | 21.0 | 17.0 | 24.0 | 11.0 | 30.0 | 18.4 | 18.0 | 20.7 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Fernando Mendoza | LV | passing_tds | 1.2 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.00 | 0.98 | 3 | PRICED |
| Fernando Mendoza | LV | passing_yards | 215.6 | 211.0 | 165.0 | 263.0 | 101.0 | 347.0 | 188.3 | 180.0 | 188.3 | 184.0 | 0.00 | 0.98 | 9 | PRICED |
| Brock Bowers | LV | receiving_yards | 56.1 | 48.0 | 25.0 | 79.0 | 0.0 | 137.0 | 64.8 | 57.0 | 64.8 | 56.0 | 0.00 | 0.97 | 12 | PRICED |
| Tre Tucker | LV | receiving_yards | 40.2 | 31.0 | 11.0 | 59.0 | 0.0 | 115.0 | 36.0 | 27.0 | 36.0 | 28.0 | 0.00 | 0.98 | 11 | PRICED |

_8 of 58 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 58 of 96 listed player/stat groups simulated and exposed, 38 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV15SEALV-SEAJSMITHNJIGBA11-5` | Jaxon Smith-Njigba | 5.0 | 0.83 | 0.86 | 0.19 | -0.644 |
| `KXNFLREC-26NOV15SEALV-SEAJSMITHNJIGBA11-6` | Jaxon Smith-Njigba | 6.0 | 0.71 | 0.73 | 0.10 | -0.609 |
| `KXNFLRSHYDS-26NOV15SEALV-SEAJPRICE8-20` | Jadarian Price | 20.0 | 0.85 | 0.86 | 0.25 | -0.595 |
| `KXNFLREC-26NOV15SEALV-SEAJSMITHNJIGBA11-4` | Jaxon Smith-Njigba | 4.0 | 0.92 | 0.94 | 0.33 | -0.586 |
| `KXNFLREC-26NOV15SEALV-LVBBOWERS89-4` | Brock Bowers | 4.0 | 0.77 | 0.79 | 0.18 | -0.586 |
| `KXNFLRSHYDS-26NOV15SEALV-SEAJPRICE8-25` | Jadarian Price | 25.0 | 0.78 | 0.79 | 0.21 | -0.573 |

_Ranked 396 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Sam Darnold (QB, SEA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 1 skill players are Questionable (Dont'e Thornton Jr. (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLGAME-26NOV15SEALV-LV moved -0.230 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.644 on KXNFLREC-26NOV15SEALV-SEAJSMITHNJIGBA11-5 (Jaxon Smith-Njigba). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.609 on KXNFLREC-26NOV15SEALV-SEAJSMITHNJIGBA11-6 (Jaxon Smith-Njigba). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26NOV15SEALV-SEAJSMITHNJIGBA11-4 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_SEA_LV.md`_


---

## SF @ DAL — `2026_10_SF_DAL`

- kickoff: 2026-11-15T21:25:00+00:00 (1398 minutes away) · state **PREGAME**
- venue: AT&T Stadium · roof  · surface matrixturf
- markets: 830 listed across 16 families — 472 supported, 302 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | SF -4.1 | SF -4.9 |
| total | 56.50 | 56.36 |
| score | DAL 26.2 – SF 30.3 | DAL 25.7 – SF 30.6 |
| win prob DAL | 34.5% | 33.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread SF -3.1 / total 27.88 · **2H** spread SF -2.2 / total 28.18 · **1Q** spread SF -1 / total 10.33 · **2Q** spread SF -2.6 / total 16.66 · **3Q** spread SF -0.7 / total 10.83 · **4Q** spread SF -0.6 / total 15.54

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread SF -4.1 · total 56.50
- move `KXNFLGAME-26NOV15SFDAL-SF` +0.115
- move `KXNFLGAME-26NOV15SFDAL-DAL` -0.115
- move `KXNFL1HTEAMTOTAL-26NOV15SFDAL-SF3` +0.110
- move `KXNFL2QTOTAL-26NOV15SFDAL-22` +0.110

**Game environment** (simulation, mean and middle 50%) — projected spread SF -4.3 · raw home-minus-away margin -4.3 (-12.0–3.0) · total 57.6 (48.0–66.0) · P(one score) 52.2% · P(17+ blowout) 19.5% · P(total 10+ over centre) 22.9%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| DAL | 65.7 (60.0–71.0) | 38.2 (33.0–43.0) | 23.5 (18.0–28.0) | 41.7 (36.0–47.0) | 0.635 (0.570–0.703) | 0.526 / 0.700 |
| SF | 63.5 (58.0–69.0) | 33.6 (28.0–38.0) | 24.7 (20.0–29.0) | 37.9 (32.0–43.0) | 0.597 (0.529–0.665) | 0.518 / 0.696 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| DAL | 00-0036997 | RB | 3.9 (1.0–6.0) | 20.6 (16.0–26.0) | 10.5% | 87.7% | MEDIUM |
| DAL | 00-0036358 | WR | 13.2 (9.0–17.0) | 0.3 (0.0–0.0) | 35.5% | 1.1% | MEDIUM |
| DAL | 00-0037247 | WR | 7.7 (4.0–10.0) | 0.1 (0.0–0.0) | 20.7% | 0.5% | HIGH |
| DAL | 00-0039410 | WR | 5.6 (3.0–8.0) | 0.3 (0.0–0.0) | 15.2% | 1.3% | HIGH |
| SF | 00-0033280 | RB | 4.7 (2.0–7.0) | 11.6 (7.0–16.0) | 14.6% | 47.0% | MEDIUM |
| SF | 00-0041052 | RB | 0.8 (0.0–1.0) | 7.0 (3.0–10.0) | 2.5% | 28.5% | HIGH |
| SF | 00-0033288 | TE | 6.0 (3.0–8.0) | 0.0 (0.0–0.0) | 18.7% | 0.2% | HIGH |
| SF | 00-0037834 | QB | 0.1 (0.0–0.0) | 5.3 (3.0–7.0) | 0.2% | 6.5% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 4 market(s), e.g. KXNFLPASSATT-26NOV15SFDAL-SFBPURDY13-32, KXNFLPASSCOMP-26NOV15SFDAL-SFBPURDY13-27
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 47 market(s), e.g. KXNFLFIRSTTD-26NOV15SFDAL-SFCMCCAFFREY23, KXNFLPASSYDS-26NOV15SFDAL-SFBPURDY13-300
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLBOTH-26NOV15SFDAL-28, KXNFLSPREAD-26NOV15SFDAL-SF18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLGAME-26NOV15SFDAL-SF, KXNFLSPREAD-26NOV15SFDAL-SF3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 228 market(s), e.g. KXNFL1H-26NOV15SFDAL-TIE, KXNFL1HTEAMTOTAL-26NOV15SFDAL-DAL24
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 43 market(s), e.g. KXNFLBOTH-26NOV15SFDAL-14, KXNFLREC-26NOV15SFDAL-DALCLAMB88-4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 30.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 56.5 (median favourite-oriented margin +2, median total 56))_
2. favourite controls / normal scoring — 18.4%  _(SF (favourite) wins by more than one score; total within 10 of the centre 56.5 (median favourite-oriented margin +16, median total 57))_
3. competitive / high scoring — 11.2%  _(final margin within one score (8 points) either way; total 66.5+ (centre 56.5) (median favourite-oriented margin +2, median total 74))_
4. competitive / low scoring — 10.0%  _(final margin within one score (8 points) either way; total 46.5 or fewer (centre 56.5) (median favourite-oriented margin +3, median total 42))_
5. favourite controls / low scoring — 8.2%  _(SF (favourite) wins by more than one score; total 46.5 or fewer (centre 56.5) (median favourite-oriented margin +15, median total 41))_
   Other — 21.3%

Marginal events (overlapping): one_score 52.2% · blowout_17 19.5% · favorite_wins 65.8% · favorite_controls 34.4% · upset 34.0% · shootout 22.9% · low_scoring 20.3% · low_possession 4.3% · high_volume_passing 18.5% · run_heavy_control 12.8%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 7.70 mph, gusts 13.00, precip prob 32%, temp 48F, forecast retrieved 2026-11-14T21:22:58+00:00 (24.03 h before kickoff)._

**`KXNFLTD-26NOV15SFDAL-SFBCOOKS84-1`** Brandin Cooks touchdowns 1
- MODEL / MARKET: football 11.8% · market 7.5% · reconciled 18.8%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.0% · failure mass 100.0% · win-contribution HHI 0.180

**`KXNFLTD-26NOV15SFDAL-SFCMCCAFFREY23-1`** Christian McCaffrey touchdowns 1
- MODEL / MARKET: football 58.9% · market 71.5% · reconciled 67.4%
- SCRIPT ROBUSTNESS: P50 mass 80.5% · P55 mass 80.5% · P60 mass 37.4% · major-script floor 44.0% · failure mass 19.5% · win-contribution HHI 0.180

**`KXNFLTD-26NOV15SFDAL-SFJCOWING4-1`** Jacob Cowing touchdowns 1
- MODEL / MARKET: football 8.0% · market 7.0% · reconciled 11.1%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.3% · failure mass 100.0% · win-contribution HHI 0.174

**`KXNFLTD-26NOV15SFDAL-DALJWILLIAMS33-2`** Javonte Williams touchdowns 2
- MODEL / MARKET: football 27.0% · market 19.5% · reconciled 23.1%
- SCRIPT ROBUSTNESS: P50 mass 11.3% · P55 mass 3.9% · P60 mass 3.9% · major-script floor 12.0% · failure mass 88.7% · win-contribution HHI 0.189

_460 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 46 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (10)**

- Brandon Aiyuk (WR, SF) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Jake Ferguson (TE, DAL) — Out [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- Jonathan Mingo (WR, DAL) — Out [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Mike Evans (WR, SF) — Out [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- Tyler Goodson (RB, DAL) — Injured Reserve [high] · **CHANGED from Active** — ruled out -- role redistributes to the depth chart behind him
- C.J. West (DT, SF) — Injured Reserve [high] · **NEW** — ruled out
- Devin Moore (CB, DAL) — Injured Reserve [high] · **NEW** — ruled out
- Donovan Ezeiruaku (LB, DAL) — Out [high] · **NEW** — ruled out
- _...and 2 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (10)** — resolves at the inactive release, T−90m

- Trent Williams (OT, SF) — Questionable [high]
- Alijah Clark (S, DAL) — Questionable [high]
- DaRon Bland (CB, DAL) — Questionable [high]
- Deommodore Lenoir (CB, SF) — Questionable [high]
- Dre Greenlaw (LB, SF) — Questionable [high]
- Joey Porter Jr. (CB, DAL) — Questionable [high]
- Jonathan Bullard (DT, DAL) — Questionable [high]
- Juanyeh Thomas (S, DAL) — Doubtful [high]

### WEATHER

- retractable roof (AT&T Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Chance Rain Showers · 51°F · wind 10 mph E · precip 28%
- forecast vintage 2026-11-14T21:23:09+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 65 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Dak Prescott | DAL | attempts | 36.7 | 37.0 | 31.0 | 42.0 | 22.0 | 51.0 | 37.1 | 37.0 | 36.7 | 37.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Javonte Williams | DAL | carries | 20.6 | 21.0 | 16.0 | 26.0 | 8.0 | 34.0 | 17.2 | 17.0 | 20.6 | 21.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | carries | 3.6 | 3.0 | 2.0 | 5.0 | 0.0 | 9.0 | 2.8 | 3.0 | 3.6 | 3.0 | -- | 0.97 | 2 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | completions | 23.8 | 24.0 | 20.0 | 28.0 | 14.0 | 34.0 | 24.3 | 24.0 | 23.8 | 24.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Dak Prescott | DAL | passing_tds | 1.8 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.0 | 2.0 | 2.0 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Dak Prescott | DAL | passing_yards | 262.6 | 259.0 | 205.0 | 317.0 | 130.0 | 410.0 | 275.6 | 272.0 | 275.6 | 271.0 | 0.00 | 0.97 | 10 | PRICED |
| CeeDee Lamb | DAL | receiving_yards | 105.0 | 97.0 | 61.0 | 141.0 | 18.0 | 219.0 | 95.4 | 88.0 | 95.4 | 88.0 | 0.00 | 0.97 | 15 | PRICED |
| George Pickens | DAL | receiving_yards | 62.8 | 54.0 | 26.0 | 89.0 | 0.0 | 157.0 | 68.0 | 60.0 | 67.9 | 58.0 | 0.00 | 0.97 | 13 | PRICED |

_8 of 65 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 65 of 102 listed player/stat groups simulated and exposed, 37 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV15SFDAL-DALCLAMB88-5` | CeeDee Lamb | 5.0 | 0.82 | 0.85 | 0.13 | -0.693 |
| `KXNFLREC-26NOV15SFDAL-DALCLAMB88-4` | CeeDee Lamb | 4.0 | 0.91 | 0.93 | 0.23 | -0.676 |
| `KXNFLREC-26NOV15SFDAL-DALCLAMB88-6` | CeeDee Lamb | 6.0 | 0.71 | 0.73 | 0.06 | -0.640 |
| `KXNFLREC-26NOV15SFDAL-SFGKITTLE85-3` | George Kittle | 3.0 | 0.87 | 0.89 | 0.28 | -0.586 |
| `KXNFLRSHATT-26NOV15SFDAL-SFBPURDY13-2` | Brock Purdy | 2.0 | 0.90 | 0.92 | 0.32 | -0.576 |
| `KXNFLRSHATT-26NOV15SFDAL-DALJWILLIAMS33-14` | Javonte Williams | 14.0 | 0.72 | 0.74 | 0.15 | -0.574 |

_Ranked 470 tradable markets; 2 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jake Ferguson (TE, DAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jonathan Mingo (WR, DAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLGAME-26NOV15SFDAL-SF moved +0.115 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.693 on KXNFLREC-26NOV15SFDAL-DALCLAMB88-5 (CeeDee Lamb). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.676 on KXNFLREC-26NOV15SFDAL-DALCLAMB88-4 (CeeDee Lamb). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26NOV15SFDAL-DALCLAMB88-4 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_SF_DAL.md`_


---

## PIT @ CIN — `2026_10_PIT_CIN`

- kickoff: 2026-11-16T01:20:00+00:00 (1634 minutes away) · state **PREGAME**
- venue: Paycor Stadium · roof outdoors · surface fieldturf
- markets: 808 listed across 16 families — 454 supported, 298 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | CIN -3.3 | CIN -3.4 |
| total | 49.88 | 50.17 |
| score | CIN 26.6 – PIT 23.3 | CIN 26.8 – PIT 23.4 |
| win prob CIN | 62.5% | 62.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread CIN -2.6 / total 24.47 · **2H** spread CIN -1.9 / total 24.60 · **1Q** spread CIN -1.1 / total 8.77 · **2Q** spread CIN -0.8 / total 14.67 · **3Q** spread CIN -0.5 / total 9.58 · **4Q** spread CIN -0.4 / total 14.19

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread CIN -3.3 · total 49.88
- move `KXNFL2HTOTAL-26NOV15PITCIN-8` +0.135
- move `KXNFLGAME-26NOV15PITCIN-CIN` +0.105
- move `KXNFLTOTAL-26NOV15PITCIN-40` +0.105

**Game environment** (simulation, mean and middle 50%) — projected spread CIN -3.7 · raw home-minus-away margin 3.7 (-4.0–11.0) · total 50.7 (42.0–59.0) · P(one score) 51.5% · P(17+ blowout) 17.8% · P(total 10+ over centre) 23.5%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CIN | 63.7 (58.0–69.0) | 37.8 (32.0–43.0) | 20.9 (16.0–25.0) | 41.9 (36.0–47.0) | 0.658 (0.591–0.727) | 0.575 / 0.748 |
| PIT | 62.7 (57.0–68.0) | 36.0 (31.0–41.0) | 22.6 (18.0–27.0) | 39.5 (34.0–45.0) | 0.630 (0.565–0.697) | 0.528 / 0.697 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CIN | 00-0038597 | RB | 4.4 (2.0–6.0) | 15.9 (11.0–20.0) | 11.9% | 75.9% | MEDIUM |
| CIN | 00-0036900 | WR | 10.7 (7.0–14.0) | 0.0 (0.0–0.0) | 29.3% | 0.2% | MEDIUM |
| CIN | 00-0036410 | WR | 7.5 (4.0–10.0) | 0.1 (0.0–0.0) | 20.5% | 0.4% | HIGH |
| CIN | 00-0034829 | TE | 3.7 (1.0–5.0) | 0.1 (0.0–0.0) | 10.2% | 0.3% | HIGH |
| PIT | 00-0037228 | RB | 4.5 (2.0–6.0) | 12.0 (7.0–16.0) | 13.4% | 53.1% | MEDIUM |
| PIT | 00-0036139 | RB | 3.2 (1.0–5.0) | 7.8 (4.0–11.0) | 9.4% | 34.4% | MEDIUM |
| PIT | 00-0035640 | WR | 8.7 (5.0–12.0) | 0.1 (0.0–0.0) | 25.6% | 0.5% | MEDIUM |
| PIT | 00-0041489 | WR | 6.5 (3.0–9.0) | 0.2 (0.0–0.0) | 19.3% | 0.8% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 7 market(s), e.g. KXNFLRSHYDS-26NOV15PITCIN-PITRDOWDLE13-50, KXNFLRSHYDS-26NOV15PITCIN-PITRDOWDLE13-40
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 47 market(s), e.g. KXNFLRECYDS-26NOV15PITCIN-PITRDOWDLE13-20, KXNFLRECYDS-26NOV15PITCIN-PITRDOWDLE13-15
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV15PITCIN-PIT7, KXNFLSPREAD-26NOV15PITCIN-CIN17
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLGAME-26NOV15PITCIN-CIN, KXNFLTOTAL-26NOV15PITCIN-47
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 221 market(s), e.g. KXNFLEQBTTS-26NOV15PITCIN-Y, KXNFLFIRSTTD-26NOV15PITCIN-CINDMEYERS81
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 36 market(s), e.g. KXNFLREC-26NOV15PITCIN-PITGBERNARD17-2, KXNFLREC-26NOV15PITCIN-PITDMETCALF4-2

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.0%  _(final margin within one score (8 points) either way; total within 10 of the centre 49.875 (median favourite-oriented margin +2, median total 50))_
2. favourite controls / normal scoring — 19.4%  _(CIN (favourite) wins by more than one score; total within 10 of the centre 49.875 (median favourite-oriented margin +14, median total 49))_
3. competitive / high scoring — 11.6%  _(final margin within one score (8 points) either way; total 59.875+ (centre 49.875) (median favourite-oriented margin +2, median total 68))_
4. competitive / low scoring — 10.9%  _(final margin within one score (8 points) either way; total 39.875 or fewer (centre 49.875) (median favourite-oriented margin +2, median total 34))_
5. favourite controls / high scoring — 8.0%  _(CIN (favourite) wins by more than one score; total 59.875+ (centre 49.875) (median favourite-oriented margin +17, median total 67))_
   Other — 21.1%

Marginal events (overlapping): one_score 51.5% · blowout_17 17.8% · favorite_wins 63.5% · favorite_controls 33.2% · upset 36.3% · shootout 23.5% · low_scoring 20.1% · low_possession 8.1% · high_volume_passing 24.8% · run_heavy_control 7.4%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 3.40 mph, gusts 8.90, precip prob 1%, temp 44F, forecast retrieved 2026-11-14T21:22:58+00:00 (27.95 h before kickoff)._

**`KXNFLTD-26NOV15PITCIN-CINDSAMPLE89-1`** Drew Sample touchdowns 1
- MODEL / MARKET: football 7.8% · market 7.5% · reconciled 17.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.7% · failure mass 100.0% · win-contribution HHI 0.180

**`KXNFLTD-26NOV15PITCIN-CINSPERINE34-1`** Samaje Perine touchdowns 1
- MODEL / MARKET: football 12.2% · market 25.5% · reconciled 22.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 6.4% · failure mass 100.0% · win-contribution HHI 0.176

**`KXNFLTD-26NOV15PITCIN-CINTHIGGINS5-1`** Tee Higgins touchdowns 1
- MODEL / MARKET: football 37.5% · market 44.5% · reconciled 41.9%
- SCRIPT ROBUSTNESS: P50 mass 19.6% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 22.3% · failure mass 80.4% · win-contribution HHI 0.175

**`KXNFLTD-26NOV15PITCIN-CINJCHASE1-1`** Ja'Marr Chase touchdowns 1
- MODEL / MARKET: football 46.7% · market 52.5% · reconciled 49.9%
- SCRIPT ROBUSTNESS: P50 mass 39.0% · P55 mass 19.6% · P60 mass 19.6% · major-script floor 30.7% · failure mass 61.0% · win-contribution HHI 0.177
- THESIS DEPENDENCY with `KXNFLPASSTDS-26NOV15PITCIN-CINJBURROW9-2`: cash correlation 0.332 · joint cash 37.8% · Jaccard of winning rows 0.519 · shared failure 27.2%

_444 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 46 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (7)**

- Andrei Iosivas (WR, CIN) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Michael Pittman Jr. (WR, PIT) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Brian Parker II (OT, CIN) — Injured Reserve [single_source] · **NEW** — ruled out
- Cashius Howell (DE, CIN) — Injured Reserve [high] · **NEW** — ruled out
- Jalen Davis (CB, CIN) — Injured Reserve [high] · **NEW** — ruled out
- Kyle Dugger (S, CIN) — Out [high] — ruled out
- Sebastian Joseph-Day (DT, PIT) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Pat Freiermuth (TE, PIT) — Questionable [high]
- Derrick Harmon (DT, PIT) — Questionable [high]

### WEATHER

- Mostly Cloudy · 41°F · wind 0 mph  · precip 0%
- forecast vintage 2026-11-14T21:23:10+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 62 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Joe Burrow | CIN | attempts | 36.3 | 37.0 | 31.0 | 42.0 | 22.0 | 50.0 | 37.8 | 37.0 | 36.3 | 37.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chase Brown | CIN | carries | 15.9 | 16.0 | 11.0 | 20.0 | 5.0 | 28.0 | 12.0 | 12.0 | 15.9 | 16.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Samaje Perine | CIN | carries | 1.7 | 1.0 | 0.0 | 2.0 | 0.0 | 7.0 | 6.1 | 6.0 | 1.7 | 1.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Joe Burrow | CIN | completions | 24.6 | 25.0 | 21.0 | 29.0 | 14.0 | 35.0 | 26.8 | 26.0 | 24.6 | 25.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Joe Burrow | CIN | passing_tds | 2.0 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.2 | 2.0 | 2.2 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Joe Burrow | CIN | passing_yards | 279.0 | 275.0 | 219.0 | 337.0 | 140.0 | 431.0 | 292.1 | 290.0 | 292.1 | 288.0 | 0.00 | 0.97 | 10 | PRICED |
| Ja'Marr Chase | CIN | receiving_yards | 90.6 | 83.0 | 49.0 | 124.0 | 11.0 | 196.0 | 95.4 | 89.0 | 95.3 | 88.0 | 0.00 | 0.97 | 14 | PRICED |
| Tee Higgins | CIN | receiving_yards | 68.9 | 58.0 | 29.0 | 98.0 | 0.0 | 174.0 | 80.7 | 74.0 | 80.5 | 68.0 | 0.00 | 0.97 | 13 | PRICED |

_8 of 62 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 62 of 103 listed player/stat groups simulated and exposed, 41 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26NOV15PITCIN-PITGBERNARD17-3` | Germie Bernard | 3.0 | 0.82 | 0.85 | 0.18 | -0.642 |
| `KXNFLREC-26NOV15PITCIN-PITGBERNARD17-2` | Germie Bernard | 2.0 | 0.91 | 0.94 | 0.31 | -0.601 |
| `KXNFLREC-26NOV15PITCIN-CINJCHASE1-6` | Ja'Marr Chase | 6.0 | 0.77 | 0.79 | 0.17 | -0.592 |
| `KXNFLREC-26NOV15PITCIN-PITGBERNARD17-4` | Germie Bernard | 4.0 | 0.70 | 0.71 | 0.11 | -0.586 |
| `KXNFLREC-26NOV15PITCIN-CINTHIGGINS5-4` | Tee Higgins | 4.0 | 0.79 | 0.82 | 0.21 | -0.582 |
| `KXNFLREC-26NOV15PITCIN-CINJCHASE1-5` | Ja'Marr Chase | 5.0 | 0.86 | 0.89 | 0.30 | -0.564 |

_Ranked 451 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Andrei Iosivas (WR, CIN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Michael Pittman Jr. (WR, PIT) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Pat Freiermuth (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL2HTOTAL-26NOV15PITCIN-8 moved +0.135 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.642 on KXNFLREC-26NOV15PITCIN-PITGBERNARD17-3 (Germie Bernard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.601 on KXNFLREC-26NOV15PITCIN-PITGBERNARD17-2 (Germie Bernard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV15PITCIN-PITGBERNARD17-2 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_PIT_CIN.md`_


---

## LAC @ BAL — `2026_10_LAC_BAL`

- kickoff: 2026-11-17T01:15:00+00:00 (3068 minutes away) · state **PREGAME**
- venue: M&T Bank Stadium · roof outdoors · surface grass
- markets: 720 listed across 16 families — 365 supported, 288 no model, 48 rules unresolved, 19 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 19 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (favourite -points) | BAL -4.2 | BAL -4 |
| total | 39.50 | 38.93 |
| score | BAL 21.9 – LAC 17.6 | BAL 21.5 – LAC 17.4 |
| win prob BAL | 66.5% | 65.6% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread BAL -3 / total 20.14 · **2H** spread BAL -2.5 / total 20.00 · **1Q** spread BAL -1.1 / total 7.59 · **2Q** spread BAL -2.1 / total 11.12 · **3Q** spread BAL -1.2 / total 7.68 · **4Q** spread BAL -0.8 / total 10.06

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread BAL -4.2 · total 39.50
- move `KXNFLGAME-26NOV16LACBAL-LAC` -0.140
- move `KXNFLGAME-26NOV16LACBAL-BAL` +0.135
- move `KXNFL1HTOTAL-26NOV16LACBAL-4` +0.085
- move `KXNFLTEAMTOTAL-26NOV16LACBAL-BAL29` -0.080

**Game environment** (simulation, mean and middle 50%) — projected spread BAL -4.5 · raw home-minus-away margin 4.5 (-3.0–12.0) · total 40.7 (32.0–49.0) · P(one score) 51.9% · P(17+ blowout) 17.2% · P(total 10+ over centre) 23.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| BAL | 60.9 (55.0–66.0) | 28.1 (23.0–33.0) | 28.5 (23.0–33.0) | 31.4 (26.0–36.0) | 0.517 (0.450–0.586) | 0.438 / 0.612 |
| LAC | 61.9 (56.0–68.0) | 29.7 (25.0–34.0) | 25.6 (21.0–30.0) | 35.7 (30.0–41.0) | 0.578 (0.513–0.643) | 0.473 / 0.641 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| BAL | 00-0032764 | RB | 1.2 (0.0–2.0) | 16.2 (11.0–21.0) | 4.5% | 57.1% | MEDIUM |
| BAL | 00-0039064 | WR | 7.2 (4.0–10.0) | 1.1 (0.0–1.0) | 26.6% | 3.8% | MEDIUM |
| BAL | 00-0034975 | RB | 3.1 (1.0–5.0) | 4.7 (1.0–7.0) | 11.4% | 16.4% | HIGH |
| BAL | 00-0034753 | TE | 4.2 (2.0–6.0) | 0.6 (0.0–0.0) | 15.3% | 2.2% | HIGH |
| LAC | 00-0040666 | RB | 1.4 (0.0–2.0) | 11.9 (7.0–16.0) | 5.0% | 46.6% | MEDIUM |
| LAC | 00-0039391 | RB | 1.8 (0.0–3.0) | 6.2 (2.0–9.0) | 6.3% | 24.0% | HIGH |
| LAC | 00-0038454 | RB | 2.1 (0.0–3.0) | 4.7 (1.0–7.0) | 7.2% | 18.4% | HIGH |
| LAC | 00-0036355 | QB | 0.1 (0.0–0.0) | 4.7 (3.0–6.0) | 0.2% | 4.2% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 16 market(s), e.g. KXNFLPASSATT-26NOV16LACBAL-BALJBRISSETT7-31, KXNFLPASSCOMP-26NOV16LACBAL-LACJHERBERT10-15
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 24 market(s), e.g. KXNFL3Q-26NOV16LACBAL-LAC, KXNFL3Q-26NOV16LACBAL-BAL
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLBOTH-26NOV16LACBAL-21, KXNFLTOTAL-26NOV16LACBAL-54
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 7 market(s), e.g. KXNFLGAME-26NOV16LACBAL-BAL, KXNFLSPREAD-26NOV16LACBAL-BAL3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 231 market(s), e.g. KXNFL1H-26NOV16LACBAL-TIE, KXNFL1HFT-26NOV16LACBAL-TIEBAL
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 28 market(s), e.g. KXNFL1HTOTAL-26NOV16LACBAL-4, KXNFL2HTOTAL-26NOV16LACBAL-8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 39.5 (median favourite-oriented margin +2, median total 39))_
2. favourite controls / normal scoring — 20.6%  _(BAL (favourite) wins by more than one score; total within 10 of the centre 39.5 (median favourite-oriented margin +14, median total 39))_
3. competitive / high scoring — 11.3%  _(final margin within one score (8 points) either way; total 49.5+ (centre 39.5) (median favourite-oriented margin +3, median total 58))_
4. competitive / low scoring — 10.7%  _(final margin within one score (8 points) either way; total 29.5 or fewer (centre 39.5) (median favourite-oriented margin +3, median total 25))_
5. favourite controls / high scoring — 8.1%  _(BAL (favourite) wins by more than one score; total 49.5+ (centre 39.5) (median favourite-oriented margin +15, median total 57))_
   Other — 19.4%

Marginal events (overlapping): one_score 51.9% · blowout_17 17.2% · favorite_wins 65.8% · favorite_controls 34.8% · upset 34.0% · shootout 23.1% · low_scoring 20.2% · low_possession 16.2% · high_volume_passing 0.5% · run_heavy_control 20.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 3.50 mph, gusts 9.20, precip prob 0%, temp 48F, forecast retrieved 2026-11-14T21:22:58+00:00 (51.87 h before kickoff)._

**`KXNFLTD-26NOV16LACBAL-LACKMITCHELL34-1`** Keaton Mitchell touchdowns 1
- MODEL / MARKET: football 13.8% · market 13.0% · reconciled 22.1%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 7.5% · failure mass 100.0% · win-contribution HHI 0.193

**`KXNFLTD-26NOV16LACBAL-BALJLANE6-1`** Ja'Kobi Lane touchdowns 1
- MODEL / MARKET: football 8.4% · market 19.5% · reconciled 16.9%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 4.0% · failure mass 100.0% · win-contribution HHI 0.192

**`KXNFLTD-26NOV16LACBAL-BALJHILL43-1`** Justice Hill touchdowns 1
- MODEL / MARKET: football 23.2% · market 17.5% · reconciled 19.6%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 11.6% · failure mass 100.0% · win-contribution HHI 0.188

**`KXNFLTD-26NOV16LACBAL-BALDHENRY22-1`** Derrick Henry touchdowns 1
- MODEL / MARKET: football 47.3% · market 53.5% · reconciled 51.5%
- SCRIPT ROBUSTNESS: P50 mass 40.0% · P55 mass 40.0% · P60 mass 19.4% · major-script floor 25.0% · failure mass 60.0% · win-contribution HHI 0.192

_355 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261114T213039Z.sim-1.1.0.scripts_v2.json.gz); 39 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Lamar Jackson (QB, BAL) — Injured Reserve [high] · **CHANGED from Questionable** — ruled out -- role redistributes to the depth chart behind him
- David Njoku (TE, LAC) — Injured Reserve [high] · **NEW** — ruled out -- role redistributes to the depth chart behind him
- Trey Pipkins III (OT, LAC) — Injured Reserve [high] · **NEW** — ruled out
- Jaylinn Hawkins (S, BAL) — Out [single_source] · **CHANGED from Questionable** — ruled out

**Questionable / Doubtful (9)** — resolves at the inactive release, T−90m

- Brenen Thompson (WR, LAC) — Questionable [high]
- Keaton Mitchell (RB, LAC) — Questionable [high]
- Ladd McConkey (WR, LAC) — Questionable [high]
- Branson Taylor (G, LAC) — Questionable [high]
- Kayode Awosika (G, LAC) — Questionable [high]
- Adisa Isaac (LB, BAL) — Questionable [high]
- Deane Leonard (CB, LAC) — Questionable [high]
- Kendall Williamson (S, LAC) — Questionable [high]

### WEATHER

- Clear · 43°F · wind 2 mph N · precip 0%
- forecast vintage 2026-11-14T21:23:11+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261114T213039Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 57 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jacoby Brissett | BAL | attempts | 27.0 | 27.0 | 22.0 | 32.0 | 15.0 | 39.0 | 30.6 | 30.0 | 27.0 | 27.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Derrick Henry | BAL | carries | 16.2 | 16.0 | 11.0 | 21.0 | 4.0 | 30.0 | 18.9 | 19.0 | 16.2 | 16.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | BAL | completions | 18.1 | 18.0 | 15.0 | 22.0 | 9.0 | 27.0 | 19.9 | 20.0 | 18.1 | 18.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | BAL | passing_tds | 1.2 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.3 | 1.0 | 1.3 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Jacoby Brissett | BAL | passing_yards | 200.1 | 195.0 | 149.0 | 247.0 | 88.0 | 329.0 | 215.9 | 208.0 | 215.9 | 210.0 | 0.00 | 0.98 | 10 | PRICED |
| Zay Flowers | BAL | receiving_yards | 62.9 | 55.0 | 29.0 | 88.0 | 0.0 | 151.0 | 73.6 | 66.0 | 73.5 | 64.0 | 0.00 | 0.97 | 15 | PRICED |
| Mark Andrews | BAL | receiving_yards | 30.3 | 23.0 | 8.0 | 45.0 | 0.0 | 88.0 | 26.8 | 21.0 | 26.8 | 20.0 | 0.00 | 0.97 | 9 | PRICED |
| Rashod Bateman | BAL | receiving_yards | 24.7 | 15.0 | 0.0 | 37.0 | 0.0 | 86.0 | 29.2 | 21.0 | 29.2 | 18.0 | 0.00 | 0.97 | 11 | PRICED |

_8 of 57 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 57 of 94 listed player/stat groups simulated and exposed, 37 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26NOV16LACBAL-BALDHENRY22-16` | Derrick Henry | 16.0 | 0.72 | 0.76 | 0.14 | -0.577 |
| `KXNFLREC-26NOV16LACBAL-BALZFLOWERS4-3` | Zay Flowers | 3.0 | 0.91 | 0.95 | 0.40 | -0.506 |
| `KXNFLRSHATT-26NOV16LACBAL-LACJHERBERT10-2` | Justin Herbert | 2.0 | 0.92 | 0.95 | 0.41 | -0.502 |
| `KXNFLRECYDS-26NOV16LACBAL-LACKMITCHELL34-10` | Keaton Mitchell | 10.0 | 0.52 | 0.55 | 0.06 | -0.463 |
| `KXNFLREC-26NOV16LACBAL-BALZFLOWERS4-6` | Zay Flowers | 6.0 | 0.51 | 0.52 | 0.06 | -0.447 |
| `KXNFLRSHATT-26NOV16LACBAL-BALDHENRY22-19` | Derrick Henry | 19.0 | 0.52 | 0.54 | 0.07 | -0.443 |

_Ranked 324 tradable markets; 41 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Lamar Jackson (QB, BAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. David Njoku (TE, LAC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 3 skill players are Questionable (Brenen Thompson (WR), Keaton Mitchell (RB), Ladd McConkey (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLGAME-26NOV16LACBAL-LAC moved -0.140 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.577 on KXNFLRSHATT-26NOV16LACBAL-BALDHENRY22-16 (Derrick Henry). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.506 on KXNFLREC-26NOV16LACBAL-BALZFLOWERS4-3 (Zay Flowers). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26NOV16LACBAL-BALZFLOWERS4-3 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_10_LAC_BAL.md`_


---

## HOW TO USE THIS PACKET

1. Handicap each game independently. The model's ranked disagreements are an input, not a shortlist.
2. For any thesis you form, check **BEST EXPRESSIONS** before choosing a contract — the largest disagreement is rarely the best payout for the risk.
3. Check **CORRELATION GROUPS** before sizing more than one position in a game.
4. Record every serious decision, including passes, via the recommendation ledger (`scripts/handicap/validate_recommendations.py`, then commit to the `handicap-data` branch).