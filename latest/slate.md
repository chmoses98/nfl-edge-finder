# NFL HANDICAP PACKET — 2026 Week 3

- run id: `20260926T172322Z`  ·  packet sha: `3864dfcf9c530c430590`
- built at: 2026-09-26T17:23:22.519888+00:00  (all timestamps UTC)
- ledger: `20260926T170122Z.shadow-0.4.0.observations.jsonl.gz`  ·  model: `shadow-0.4.0`
- context captures: ['20260926T163128Z', '20260926T170815Z']
- team-profile basis: **current_season**
- **REAL-MONEY STATUS: NOT VALIDATED -- this packet recommends nothing and authorises nothing**

> This packet contains no recommendations. Every model-vs-market number is a *disagreement*, which is not an edge. The model has been shown redundant to the closing market on player props and behind it on game outcomes; it is here as structure and context, not as a superior forecast.

## SLATE SUMMARY

- games: **16**
- markets listed this slate: **11378**, model-supported: **5414**
- ledger support states (all weeks): `{'UNSUPPORTED_MODEL': 13469, 'UNSUPPORTED_RULES': 2643, 'SUPPORTED': 5638, 'UNSUPPORTED_IDENTITY': 122, 'POST_KICKOFF_EXCLUDED': 24171}`

### FULL-BOARD COVERAGE

_RUN NFL examines every executable Kalshi contract for every requested unstarted NFL game. UNSUPPORTED_MODEL is a statement about one model, never a reason to hide a contract. Every listed contract terminates in exactly one analysis state, in one of four buckets: A validated model view, B coherent/Shadow research view, C manual handicap from the packet's own football and context data, D explicit PASS with a named reason._

| bucket | contracts | meaning |
|---|---|---|
| **A** | 5414 | validated/production model view available |
| **B** | 3106 | coherent / Shadow research model view available |
| **C** | 1832 | no automated pricing authority; handicap from the football and context data in this packet |
| **D** | 184 | cannot defensibly price -- explicit PASS / RESEARCH REQUIRED, with a reason |
| **-** | 842 | outside the pregame window (kickoff has passed) |
| **!** | 0 | INVARIANT VIOLATION -- a listed contract with no analysis state |

- listed: **11378** · executable books: **10301**
- incumbent priced: **5414** · coherent simulation: **0** · Shadow v2 research: **3106**
- manual handicap required: **1832** · research required: **60**
- rules blocked: **2** · identity blocked: **122** · non-football: **0**
- post-kickoff (stale): **842**
- **silently omitted: 0** — this must be 0.

| family / period | listed | executable | incumbent priced | coherent sim | shadow v2 | manual research | research required | rules blocked | identity blocked | non football | post kickoff | silently omitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PLAYER_STAT/FULL | 5286 | 5019 | 4243 | 0 | 99 | 388 | 0 | 0 | 122 | 0 | 434 | 0 |
| FIRST_TD_TEAM/FULL | 456 | 313 | 0 | 0 | 0 | 426 | 0 | 1 | 0 | 0 | 29 | 0 |
| TEAM_TOTAL/FULL | 437 | 437 | 409 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 28 | 0 |
| SPREAD/FULL | 418 | 418 | 387 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 31 | 0 |
| FIRST_TD_SCORER/FULL | 399 | 399 | 0 | 0 | 0 | 373 | 0 | 1 | 0 | 0 | 25 | 0 |
| TEAM_TOTAL/1H | 352 | 333 | 0 | 0 | 329 | 0 | 0 | 0 | 0 | 0 | 23 | 0 |
| TEAM_STAT/FULL | 326 | 23 | 0 | 0 | 0 | 300 | 0 | 0 | 0 | 0 | 26 | 0 |
| TOTAL/FULL | 304 | 304 | 285 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 19 | 0 |
| SPREAD/2H | 252 | 248 | 0 | 0 | 233 | 0 | 0 | 0 | 0 | 0 | 19 | 0 |
| SPREAD/1H | 250 | 250 | 0 | 0 | 233 | 0 | 0 | 0 | 0 | 0 | 17 | 0 |
| RACE_TO_N/FULL | 240 | 64 | 0 | 0 | 0 | 225 | 0 | 0 | 0 | 0 | 15 | 0 |
| TOTAL/1H | 216 | 216 | 0 | 0 | 203 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |
| TOTAL/2H | 216 | 216 | 0 | 0 | 203 | 0 | 0 | 0 | 0 | 0 | 13 | 0 |
| SPREAD/3Q | 174 | 169 | 0 | 0 | 163 | 0 | 0 | 0 | 0 | 0 | 11 | 0 |
| SPREAD/4Q | 173 | 166 | 0 | 0 | 162 | 0 | 0 | 0 | 0 | 0 | 11 | 0 |
| SPREAD/2Q | 170 | 163 | 0 | 0 | 160 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| SPREAD/1Q | 163 | 162 | 0 | 0 | 151 | 0 | 0 | 0 | 0 | 0 | 12 | 0 |
| TOTAL/1Q | 160 | 160 | 0 | 0 | 150 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/2Q | 160 | 160 | 0 | 0 | 150 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/3Q | 160 | 160 | 0 | 0 | 150 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| TOTAL/4Q | 160 | 156 | 0 | 0 | 150 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| HALF_FULL_RESULT/1H | 144 | 144 | 0 | 0 | 135 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| GAME_PLAYER_LEADER/FULL | 132 | 57 | 0 | 0 | 0 | 120 | 0 | 0 | 0 | 0 | 12 | 0 |
| WIN_MARGIN_BUCKET/FULL | 112 | 112 | 0 | 0 | 105 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| BOTH_TEAMS_SCORE_N/FULL | 64 | 63 | 60 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| GAME_EVENT/FULL | 64 | 47 | 0 | 0 | 0 | 0 | 60 | 0 | 0 | 0 | 4 | 0 |
| PERIOD_WINNER/1H | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/1Q | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2H | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/2Q | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/3Q | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| PERIOD_WINNER/4Q | 48 | 48 | 0 | 0 | 45 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| GAME_WINNER/FULL | 32 | 32 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| BOTH_TEAMS_SCORE/1Q | 16 | 10 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/2Q | 16 | 6 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/3Q | 16 | 1 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| BOTH_TEAMS_SCORE/4Q | 16 | 1 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| TOTAL_TD/FULL | 6 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |

_A Shadow v2 or coherent-simulation projection is RESEARCH. It is not validated, it is never mixed into the incumbent's probability or its disagreement ranking, and it reaches no recommendation, staking or preflight path._

**Skill players ruled OUT (24)**

- Cooper Rush (QB, ATL) — Out · 2026_03_ATL_GB
- Jack Strand (QB, ATL) — Out · 2026_03_ATL_GB
- Jayden Reed (WR, GB) — Out · 2026_03_ATL_GB
- Jonathon Brooks (RB, CAR) — Injured Reserve · 2026_03_CAR_CLE
- Andrei Iosivas (WR, CIN) — Out · 2026_03_CIN_PIT
- Rico Dowdle (RB, PIT) — Out · 2026_03_CIN_PIT
- Nico Collins (WR, HOU) — Out · 2026_03_HOU_IND
- Ashton Dulin (WR, IND) — Out · 2026_03_HOU_IND
- Alec Pierce (WR, IND) — Injured Reserve · 2026_03_HOU_IND
- Caleb Douglas (WR, MIA) — Out · 2026_03_KC_MIA
- Brenen Thompson (WR, LAC) — Out · 2026_03_LAC_BUF
- Charlie Kolar (TE, LAC) — Out · 2026_03_LAC_BUF
- David Njoku (TE, LAC) — Injured Reserve · 2026_03_LAC_BUF
- Mason Taylor (TE, NYJ) — Out · 2026_03_NYJ_DET
- Arian Smith (WR, NYJ) — Injured Reserve · 2026_03_NYJ_DET

**New or changed since the previous capture (4)** — the most decision-relevant section on the page

- Anthony Gould (WR, IND): **Active** (new record) · 2026_03_HOU_IND
- Nick Westbrook-Ikhine (WR, IND): **Active** (new record) · 2026_03_HOU_IND
- Erick Hallett II (S, TEN): **Active** (new record) · 2026_03_TEN_NYG
- Michael Carter (RB, TEN): **Active** (new record) · 2026_03_TEN_NYG

**Weather flagged material**

- 2026_03_CIN_PIT: wind 15 mph, precip 0%
- 2026_03_SEA_WAS: wind 18 mph, precip 65%
- 2026_03_TEN_NYG: wind 17 mph, precip 94%

**Largest market moves since first capture**

| ticker | game | family | move |
|---|---|---|---|
| `KXNFLRSHYDS-26SEP24ATLGB-ATLBROBINSON7-160` | 2026_03_ATL_GB | PLAYER_STAT | +0.960 |
| `KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5-140` | 2026_03_ATL_GB | PLAYER_STAT | +0.955 |
| `KXNFLTD-26SEP24ATLGB-ATLAHOOPER81-1` | 2026_03_ATL_GB | PLAYER_STAT | +0.955 |
| `KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5-130` | 2026_03_ATL_GB | PLAYER_STAT | +0.945 |
| `KXNFLRSHYDS-26SEP24ATLGB-ATLBROBINSON7-140` | 2026_03_ATL_GB | PLAYER_STAT | +0.935 |
| `KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5-120` | 2026_03_ATL_GB | PLAYER_STAT | +0.930 |
| `KXNFLREC-26SEP24ATLGB-ATLDLONDON5-9` | 2026_03_ATL_GB | PLAYER_STAT | +0.930 |
| `KXNFLRSHYDS-26SEP24ATLGB-ATLBROBINSON7-130` | 2026_03_ATL_GB | PLAYER_STAT | +0.915 |
| `KXNFLRSHYDS-26SEP24ATLGB-ATLBROBINSON7-150` | 2026_03_ATL_GB | PLAYER_STAT | +0.910 |
| `KXNFLRECYDS-26SEP24ATLGB-ATLDLONDON5-110` | 2026_03_ATL_GB | PLAYER_STAT | +0.910 |

**Largest model/market disagreements** — DISAGREEMENT ONLY, REQUIRES HANDICAP

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26SEP27SEAWAS-SEAJPRICE8-10` | Jadarian Price | 10.0 | 0.81 | 0.81 | 0.17 | -0.636 |
| `KXNFLREC-26SEP27LARDEN-LARTFERGUSON18-2` | Terrance Ferguson | 2.0 | 0.90 | 0.91 | 0.27 | -0.622 |
| `KXNFLRSHYDS-26SEP27SEAWAS-SEAJPRICE8-25` | Jadarian Price | 25.0 | 0.82 | 0.83 | 0.21 | -0.617 |
| `KXNFLRECYDS-26SEP27LARDEN-LARTFERGUSON18-25` | Terrance Ferguson | 25.0 | 0.78 | 0.80 | 0.16 | -0.615 |
| `KXNFLRSHATT-26SEP27CARCLE-CLEDWATSON4-3` | Deshaun Watson | 3.0 | 0.88 | 0.88 | 0.27 | -0.607 |
| `KXNFLREC-26SEP27NYJDET-NYJKSADIQ16-2` | Kenyon Sadiq | 2.0 | 0.79 | 0.80 | 0.18 | -0.607 |
| `KXNFLRSHYDS-26SEP27SEAWAS-SEAJPRICE8-30` | Jadarian Price | 30.0 | 0.77 | 0.77 | 0.17 | -0.597 |
| `KXNFLREC-26SEP27LARDEN-LARTFERGUSON18-3` | Terrance Ferguson | 3.0 | 0.76 | 0.77 | 0.16 | -0.596 |
| `KXNFLRSHATT-26SEP27NYJDET-DETJGIBBS0-15` | Jahmyr Gibbs | 15.0 | 0.78 | 0.81 | 0.19 | -0.591 |
| `KXNFLRSHATT-26SEP27NEJAC-JACBTUTEN33-10` | Bhayshul Tuten | 10.0 | 0.79 | 0.80 | 0.20 | -0.588 |
| `KXNFLRECYDS-26SEP27NYJDET-NYJKSADIQ16-15` | Kenyon Sadiq | 15.0 | 0.72 | 0.74 | 0.13 | -0.588 |
| `KXNFLRSHYDS-26SEP27CARCLE-CARCHUBBARD30-40` | Chuba Hubbard | 40.0 | 0.82 | 0.83 | 0.25 | -0.568 |

**Highest-liquidity markets**

- `KXNFLGAME-26SEP24ATLGB-GB` (GAME_WINNER, 2026_03_ATL_GB): volume 26098490, OI 13344344
- `KXNFLGAME-26SEP24ATLGB-ATL` (GAME_WINNER, 2026_03_ATL_GB): volume 25115932, OI 15174846
- `KXNFLTOTAL-26SEP24ATLGB-44` (TOTAL, 2026_03_ATL_GB): volume 3425614, OI 2440145
- `KXNFLSPREAD-26SEP24ATLGB-GB6` (SPREAD, 2026_03_ATL_GB): volume 2315943, OI 1362612
- `KXNFLSPREAD-26SEP24ATLGB-GB5` (SPREAD, 2026_03_ATL_GB): volume 2179297, OI 1227711
- `KXNFLSPREAD-26SEP24ATLGB-GB7` (SPREAD, 2026_03_ATL_GB): volume 1775328, OI 1106589
- `KXNFLTD-26SEP24ATLGB-GBCWATSON9-1` (PLAYER_STAT, 2026_03_ATL_GB): volume 1195658, OI 1183461
- `KXNFLGAME-26SEP27KCMIA-KC` (GAME_WINNER, 2026_03_KC_MIA): volume 1159729, OI 995107

**BLOCKING data issues**

- 2026_03_ATL_GB: `GAME_STARTED` — kickoff has passed; this is not a pregame packet

### GAME PRIORITY FOR HANDICAP

_Priority ranks where deeper review may be most useful. It is NOT a bet ranking and carries no expectation that these games contain value._

| # | game | score | why |
|---|---|---|---|
| 1 | 2026_03_TEN_NYG | 15.42 | 2 new/changed injury records; 1 skill players ruled out (role change); material weather; largest market move 0.220; largest reconciled simulation disagreement 0.142; raw incumbent disagreement 0.551 (NOT scored: unvalidated); 266 supported player-prop rungs |
| 2 | 2026_03_SEA_WAS | 14.45 | 3 skill players ruled out (role change); material weather; largest market move 0.305; largest reconciled simulation disagreement 0.145; raw incumbent disagreement 0.636 (NOT scored: unvalidated); 271 supported player-prop rungs |
| 3 | 2026_03_HOU_IND | 14.0 | 2 new/changed injury records; 3 skill players ruled out (role change); largest market move 0.120; raw incumbent disagreement 0.514 (NOT scored: unvalidated); 281 supported player-prop rungs |
| 4 | 2026_03_CIN_PIT | 12.56 | 2 skill players ruled out (role change); material weather; largest market move 0.210; largest reconciled simulation disagreement 0.106; raw incumbent disagreement 0.482 (NOT scored: unvalidated); 246 supported player-prop rungs |
| 5 | 2026_03_LAC_BUF | 10.8 | 3 skill players ruled out (role change); largest market move 0.250; largest reconciled simulation disagreement 0.080; raw incumbent disagreement 0.530 (NOT scored: unvalidated); 287 supported player-prop rungs |
| 6 | 2026_03_NYJ_DET | 9.32 | 2 skill players ruled out (role change); largest market move 0.215; largest reconciled simulation disagreement 0.082; raw incumbent disagreement 0.607 (NOT scored: unvalidated); 309 supported player-prop rungs |
| 7 | 2026_03_ATL_GB | 8.5 | 3 skill players ruled out (role change); largest market move 0.960; BLOCKING data issue -- review before trusting anything here |
| 8 | 2026_03_ARI_SF | 8.5 | 2 skill players ruled out (role change); largest market move 0.175; raw incumbent disagreement 0.558 (NOT scored: unvalidated); 271 supported player-prop rungs |
| 9 | 2026_03_LA_DEN | 8.5 | 2 skill players ruled out (role change); largest market move 0.145; raw incumbent disagreement 0.622 (NOT scored: unvalidated); 284 supported player-prop rungs |
| 10 | 2026_03_CAR_CLE | 7.0 | 1 skill players ruled out (role change); largest market move 0.165; raw incumbent disagreement 0.607 (NOT scored: unvalidated); 273 supported player-prop rungs |
| 11 | 2026_03_KC_MIA | 7.0 | 1 skill players ruled out (role change); largest market move 0.310; raw incumbent disagreement 0.529 (NOT scored: unvalidated); 270 supported player-prop rungs |
| 12 | 2026_03_LV_NO | 7.0 | 1 skill players ruled out (role change); largest market move 0.150; raw incumbent disagreement 0.462 (NOT scored: unvalidated); 257 supported player-prop rungs |
| 13 | 2026_03_MIN_TB | 6.62 | largest market move 0.150; largest reconciled simulation disagreement 0.112; raw incumbent disagreement 0.456 (NOT scored: unvalidated); 310 supported player-prop rungs |
| 14 | 2026_03_NE_JAX | 6.32 | largest market move 0.180; largest reconciled simulation disagreement 0.082; raw incumbent disagreement 0.588 (NOT scored: unvalidated); 322 supported player-prop rungs |
| 15 | 2026_03_BAL_DAL | 6.01 | largest market move 0.225; largest reconciled simulation disagreement 0.051; raw incumbent disagreement 0.514 (NOT scored: unvalidated); 339 supported player-prop rungs |
| 16 | 2026_03_PHI_CHI | 5.5 | largest market move 0.170; raw incumbent disagreement 0.449 (NOT scored: unvalidated); 257 supported player-prop rungs |

> Each game below is summarised. Full detail -- complete market board, every player ladder, all best-expression groups -- is in that game's own file under `games/`.


---

## ATL @ GB — `2026_03_ATL_GB`

- kickoff: 2026-09-25T00:15:00+00:00 (-2468 minutes away) · state **STARTED_OR_UNKNOWN**
- venue: unknown · roof None · surface None
- markets: 842 listed across 17 families — 0 supported, 16 no model, 54 rules unresolved, 0 identity unresolved

**Data health**

- `GAME_STARTED` (block) — kickoff has passed; this is not a pregame packet
- `MOSTLY_UNCHANGED_QUOTES` (warn) — 842/842 quotes unchanged >240m. The capture is change-suppressed, so this means the price has not MOVED, not that the feed is broken.
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 54 markets have unestablished settlement semantics
- `WEATHER_MISSING` (warn) — no weather row captured for this game

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 22.05 | -- |
| total | 48.72 | -- |
| score | GB 13.3 – ATL 35.4 | GB -- – ATL -- |
| win prob GB | 0.5% | --% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 10.00 / total 23.50 · **2H** spread 5.40 / total 32.00 · **1Q** spread -0.00 / total 14.50 · **2Q** spread 9.00 / total 9.50 · **3Q** spread 7.00 / total 7.50 · **4Q** spread -1.81 / total 24.18

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (12)**

- Cooper Rush (QB, ATL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jack Strand (QB, ATL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jayden Reed (WR, GB) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Aaron Banks (G, GB) — Out [high] — ruled out
- Ethan Onianwa (OT, ATL) — Out [high] — ruled out
- Zach Bako-Bewele (OT, GB) — Out [high] — ruled out
- A.J. Terrell Jr. (CB, ATL) — Injured Reserve [single_source] — ruled out
- Anthony Campbell (DT, GB) — Out [high] — ruled out
- _...and 4 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Jacob Monk (C, GB) — Questionable [high]
- Edgerrin Cooper (LB, GB) — Questionable [high]

### WEATHER

Not available — no weather row captured for this game

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 105 listed player/stat groups simulated and exposed, 105 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

_Ranked 0 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Cooper Rush (QB, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jack Strand (QB, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLRSHYDS-26SEP24ATLGB-ATLBROBINSON7-160 moved +0.960 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_ATL_GB.md`_


---

## CAR @ CLE — `2026_03_CAR_CLE`

- kickoff: 2026-09-27T17:00:00+00:00 (1417 minutes away) · state **PREGAME**
- venue: Huntington Bank Field · roof outdoors · surface grass
- markets: 686 listed across 15 families — 351 supported, 279 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.00 | 1.94 |
| total | 42.83 | 43.19 |
| score | CLE 20.4 – CAR 22.4 | CLE 20.6 – CAR 22.6 |
| win prob CLE | 44.5% | 42.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 0.43 / total 21.50 · **2H** spread 0.77 / total 20.75 · **1Q** spread 0.10 / total 7.80 · **2Q** spread -0.06 / total 12.82 · **3Q** spread 0.09 / total 7.94 · **4Q** spread -0.28 / total 11.75

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (5)**

- Jonathon Brooks (RB, CAR) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Teven Jenkins (G, CLE) — Out [high] — ruled out
- Claudin Cherelus (LB, CAR) — Out [high] — ruled out
- Devin Lloyd (LB, CAR) — Out [high] — ruled out
- Nick Scott (S, CAR) — Out [high] — ruled out

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Jalen Coker (WR, CAR) — Questionable [high]
- Xavier Legette (WR, CAR) — Questionable [high]
- Grant Delpit (S, CLE) — Questionable [high]
- Tyson Campbell (CB, CLE) — Questionable [high]

### WEATHER

- Sunny · 68°F · wind 14 mph N · precip 0%
- forecast vintage 2026-09-26T17:08:18+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 55 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bryce Young | CAR | attempts | 30.3 | 30.0 | 25.0 | 36.0 | 17.0 | 43.0 | 32.8 | 32.0 | 30.3 | 30.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chuba Hubbard | CAR | carries | 16.9 | 17.0 | 12.0 | 22.0 | 5.0 | 30.0 | 17.4 | 17.0 | 16.9 | 17.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | carries | 3.5 | 3.0 | 2.0 | 5.0 | 0.0 | 8.0 | 3.7 | 3.0 | 3.5 | 3.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | completions | 18.8 | 19.0 | 15.0 | 22.0 | 10.0 | 28.0 | 19.5 | 19.0 | 18.8 | 19.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Bryce Young | CAR | passing_yards | 211.2 | 206.0 | 160.0 | 259.0 | 97.0 | 342.0 | 226.6 | 220.0 | 226.6 | 221.0 | 0.00 | 0.98 | 9 | PRICED |
| Tetairoa McMillan | CAR | receiving_yards | 60.4 | 51.0 | 24.0 | 87.0 | 0.0 | 153.0 | 68.4 | 61.0 | 68.4 | 58.0 | 0.00 | 0.98 | 13 | PRICED |
| Darren Waller | CAR | receiving_yards | 24.8 | 16.0 | 2.0 | 37.0 | 0.0 | 81.0 | 25.5 | 20.0 | 25.5 | 17.0 | 0.00 | 0.97 | 7 | PRICED |

_8 of 55 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 55 of 87 listed player/stat groups simulated and exposed, 32 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26SEP27CARCLE-CLEDWATSON4-3` | Deshaun Watson | 3.0 | 0.88 | 0.88 | 0.27 | -0.607 |
| `KXNFLRSHYDS-26SEP27CARCLE-CARCHUBBARD30-40` | Chuba Hubbard | 40.0 | 0.82 | 0.83 | 0.25 | -0.568 |
| `KXNFLRSHATT-26SEP27CARCLE-CARCHUBBARD30-15` | Chuba Hubbard | 15.0 | 0.67 | 0.72 | 0.10 | -0.567 |
| `KXNFLREC-26SEP27CARCLE-CLEDBOSTON12-2` | Denzel Boston | 2.0 | 0.86 | 0.88 | 0.32 | -0.541 |
| `KXNFLRSHYDS-26SEP27CARCLE-CARCHUBBARD30-50` | Chuba Hubbard | 50.0 | 0.72 | 0.73 | 0.19 | -0.539 |
| `KXNFLREC-26SEP27CARCLE-CLEDBOSTON12-3` | Denzel Boston | 3.0 | 0.68 | 0.69 | 0.19 | -0.493 |

_Ranked 346 tradable markets; 5 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jonathon Brooks (RB, CAR) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 2 skill players are Questionable (Jalen Coker (WR), Xavier Legette (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLFFPTS-26SEP27CARCLE-CARRFITZGERALD10-7P4 moved -0.165 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.607 on KXNFLRSHATT-26SEP27CARCLE-CLEDWATSON4-3 (Deshaun Watson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.568 on KXNFLRSHYDS-26SEP27CARCLE-CARCHUBBARD30-40 (Chuba Hubbard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26SEP27CARCLE-CLEHFANNIN44-2 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_CAR_CLE.md`_


---

## CIN @ PIT — `2026_03_CIN_PIT`

- kickoff: 2026-09-27T17:00:00+00:00 (1417 minutes away) · state **PREGAME**
- venue: Acrisure Stadium · roof outdoors · surface grass
- markets: 651 listed across 16 families — 324 supported, 271 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.22 | 3.62 |
| total | 42.88 | 43.02 |
| score | PIT 19.8 – CIN 23.0 | PIT 19.7 – CIN 23.3 |
| win prob PIT | 38.5% | 36.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.67 / total 21.50 · **2H** spread 1.71 / total 20.88 · **1Q** spread 0.97 / total 7.90 · **2Q** spread 0.80 / total 12.76 · **3Q** spread 0.17 / total 7.94 · **4Q** spread 0.29 / total 11.43

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (3)**

- Andrei Iosivas (WR, CIN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Rico Dowdle (RB, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Gennings Dunker (G, PIT) — Out [single_source] — ruled out

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Jaylen Warren (RB, PIT) — Questionable [high]
- Michael Pittman Jr. (WR, PIT) — Questionable [single_source]
- B.J. Hill (DT, CIN) — Doubtful [high]
- Jamel Dean (CB, PIT) — Questionable [high]
- Joey Porter Jr. (CB, PIT) — Questionable [single_source]

### WEATHER

- Mostly Sunny · 68°F · wind 15 mph N · precip 0%
- forecast vintage 2026-09-26T17:09:28+00:00 · material: **True**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 51 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Joe Burrow | CIN | attempts | 32.8 | 33.0 | 28.0 | 38.0 | 19.0 | 46.0 | 35.5 | 35.0 | 32.8 | 33.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chase Brown | CIN | carries | 18.8 | 19.0 | 14.0 | 24.0 | 7.0 | 31.0 | 16.2 | 16.0 | 18.8 | 19.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Joe Burrow | CIN | completions | 21.6 | 22.0 | 18.0 | 25.0 | 12.0 | 32.0 | 23.7 | 23.0 | 21.6 | 22.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Joe Burrow | CIN | passing_tds | 1.6 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Joe Burrow | CIN | passing_yards | 238.3 | 234.0 | 183.0 | 290.0 | 114.0 | 378.0 | 255.2 | 250.0 | 255.2 | 250.0 | 0.00 | 0.98 | 8 | PRICED |
| Ja'Marr Chase | CIN | receiving_yards | 78.8 | 72.0 | 42.0 | 108.0 | 8.0 | 173.0 | 81.5 | 75.0 | 81.5 | 74.0 | 0.00 | 0.97 | 13 | PRICED |
| Tee Higgins | CIN | receiving_yards | 62.5 | 53.0 | 25.0 | 90.0 | 0.0 | 157.0 | 60.8 | 53.0 | 60.8 | 51.0 | 0.00 | 0.98 | 11 | PRICED |
| Mike Gesicki | CIN | receiving_yards | 27.1 | 18.0 | 4.0 | 40.0 | 0.0 | 86.0 | 29.5 | 23.0 | 29.5 | 20.0 | 0.00 | 0.98 | 7 | PRICED |

_8 of 51 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 51 of 78 listed player/stat groups simulated and exposed, 27 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP27CINPIT-PITPFREIERMUTH88-3` | Pat Freiermuth | 3.0 | 0.73 | 0.74 | 0.25 | -0.482 |
| `KXNFLRSHATT-26SEP27CINPIT-CINCBROWN30-14` | Chase Brown | 14.0 | 0.69 | 0.70 | 0.22 | -0.468 |
| `KXNFLREC-26SEP27CINPIT-PITPFREIERMUTH88-2` | Pat Freiermuth | 2.0 | 0.89 | 0.90 | 0.43 | -0.460 |
| `KXNFLREC-26SEP27CINPIT-PITPFREIERMUTH88-4` | Pat Freiermuth | 4.0 | 0.56 | 0.56 | 0.14 | -0.415 |
| `KXNFLRECYDS-26SEP27CINPIT-PITPFREIERMUTH88-15` | Pat Freiermuth | 15.0 | 0.82 | 0.83 | 0.41 | -0.413 |
| `KXNFLRECYDS-26SEP27CINPIT-PITPFREIERMUTH88-25` | Pat Freiermuth | 25.0 | 0.69 | 0.70 | 0.28 | -0.412 |

_Ranked 321 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Andrei Iosivas (WR, CIN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Rico Dowdle (RB, PIT) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Jaylen Warren (RB), Michael Pittman Jr. (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. Wind/precipitation is flagged material (15 mph, 0% precip). Is that already in the total, and does the forecast vintage (2026-09-26T17:09:28+00:00) predate the last big market move?
5. KXNFLFIRSTTD-26SEP27CINPIT-CINAIOSIVAS80 moved +0.210 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
6. The model disagrees by -0.482 on KXNFLREC-26SEP27CINPIT-PITPFREIERMUTH88-3 (Pat Freiermuth). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. The model disagrees by -0.468 on KXNFLRSHATT-26SEP27CINPIT-CINCBROWN30-14 (Chase Brown). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
8. KXNFLREC-26SEP27CINPIT-PITPFREIERMUTH88-2 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_CIN_PIT.md`_


---

## HOU @ IND — `2026_03_HOU_IND`

- kickoff: 2026-09-27T17:00:00+00:00 (1417 minutes away) · state **PREGAME**
- venue: Lucas Oil Stadium · roof  · surface fieldturf
- markets: 708 listed across 16 families — 358 supported, 293 no model, 48 rules unresolved, 9 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 9 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 1.67 | 0.71 |
| total | 43.09 | 43.26 |
| score | IND 20.7 – HOU 22.4 | IND 21.3 – HOU 22.0 |
| win prob IND | 46.5% | 47.4% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 0.47 / total 21.50 · **2H** spread 0.79 / total 21.00 · **1Q** spread -0.10 / total 7.82 · **2Q** spread 0.13 / total 12.93 · **3Q** spread 0.22 / total 7.97 · **4Q** spread -0.28 / total 11.65

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Alec Pierce (WR, IND) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Ashton Dulin (WR, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Nico Collins (WR, HOU) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Ed Ingram (G, HOU) — Out [high] — ruled out
- Henry To'oTo'o (LB, HOU) — Injured Reserve [high] — ruled out
- Jadeveon Clowney (DE, HOU) — Out [high] — ruled out
- Jake Hummel (LB, HOU) — Out [high] — ruled out
- M.J. Stewart (S, HOU) — Out [high] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Trent Brown (OT, HOU) — Questionable [high]
- Charvarius Ward (CB, IND) — Questionable [high]

### WEATHER

- Sunny · 67°F · wind 6 mph N · precip 0%
- forecast vintage 2026-09-26T17:08:21+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 61 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C.J. Stroud | HOU | attempts | 33.5 | 34.0 | 28.0 | 39.0 | 19.0 | 47.0 | 33.0 | 33.0 | 33.5 | 34.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Woody Marks | HOU | carries | 11.6 | 11.0 | 6.0 | 16.0 | 2.0 | 24.0 | 8.6 | 8.0 | 11.6 | 11.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| David Montgomery | HOU | carries | 11.5 | 11.0 | 6.0 | 16.0 | 2.0 | 24.0 | 12.5 | 12.0 | 11.5 | 11.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| C.J. Stroud | HOU | completions | 21.1 | 21.0 | 17.0 | 25.0 | 11.0 | 31.0 | 20.8 | 20.0 | 21.1 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| C.J. Stroud | HOU | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| C.J. Stroud | HOU | passing_yards | 233.8 | 230.0 | 179.0 | 284.0 | 110.0 | 374.0 | 244.0 | 238.0 | 244.0 | 240.0 | 0.00 | 0.98 | 9 | PRICED |
| Dalton Schultz | HOU | receiving_yards | 53.2 | 46.0 | 23.0 | 75.0 | 0.0 | 131.0 | 61.5 | 54.0 | 61.5 | 53.0 | 0.00 | 0.98 | 1 | PRICED |
| Xavier Hutchinson | HOU | receiving_yards | 42.1 | 33.0 | 13.0 | 62.0 | 0.0 | 117.0 | 44.8 | 39.0 | 44.8 | 35.0 | 0.00 | 0.97 | 1 | PRICED |

_8 of 61 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 61 of 100 listed player/stat groups simulated and exposed, 39 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP27HOUIND-HOUDSCHULTZ86-4` | Dalton Schultz | 4.0 | 0.76 | 0.77 | 0.25 | -0.514 |
| `KXNFLRSHATT-26SEP27HOUIND-HOUDMONTGOMERY32-10` | David Montgomery | 10.0 | 0.73 | 0.75 | 0.25 | -0.479 |
| `KXNFLREC-26SEP27HOUIND-HOUDSCHULTZ86-5` | Dalton Schultz | 5.0 | 0.61 | 0.62 | 0.13 | -0.477 |
| `KXNFLREC-26SEP27HOUIND-INDTWARREN84-4` | Tyler Warren | 4.0 | 0.70 | 0.72 | 0.23 | -0.475 |
| `KXNFLREC-26SEP27HOUIND-HOUDSCHULTZ86-3` | Dalton Schultz | 3.0 | 0.87 | 0.88 | 0.42 | -0.451 |
| `KXNFLREC-26SEP27HOUIND-INDJDOWNS2-4` | Josh Downs | 4.0 | 0.70 | 0.71 | 0.25 | -0.448 |

_Ranked 356 tradable markets; 2 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Nico Collins (WR, HOU) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Ashton Dulin (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLTOTAL-26SEP27HOUIND-44 moved -0.120 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.514 on KXNFLREC-26SEP27HOUIND-HOUDSCHULTZ86-4 (Dalton Schultz). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.479 on KXNFLRSHATT-26SEP27HOUIND-HOUDMONTGOMERY32-10 (David Montgomery). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLRSHYDS-26SEP27HOUIND-HOUWMARKS4-60 sits at a market price of 0.11 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_HOU_IND.md`_


---

## KC @ MIA — `2026_03_KC_MIA`

- kickoff: 2026-09-27T17:00:00+00:00 (1417 minutes away) · state **PREGAME**
- venue: Hard Rock Stadium · roof outdoors · surface grass
- markets: 703 listed across 16 families — 348 supported, 299 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 10.38 | 11.64 |
| total | 45.62 | 45.87 |
| score | MIA 17.6 – KC 28.0 | MIA 17.1 – KC 28.8 |
| win prob MIA | 14.5% | 15.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 6.85 / total 23.60 · **2H** spread 4.81 / total 21.73 · **1Q** spread 2.88 / total 8.38 · **2Q** spread 3.89 / total 14.13 · **3Q** spread 2.69 / total 8.75 · **4Q** spread 2.74 / total 12.77

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Caleb Douglas (WR, MIA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Cooper McDonald (LB, KC) — Injured Reserve [high] — ruled out
- Robert Beal Jr. (DE, MIA) — Out [single_source] — ruled out
- Ronnie Harrison Jr. (LB, MIA) — Injured Reserve [single_source] — ruled out

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Jaylen Wright (RB, MIA) — Doubtful [high]
- Ryan Miller (WR, MIA) — Questionable [high]
- JuJu Brents (CB, MIA) — Questionable [high]

### WEATHER

- Sunny · 83°F · wind 3 mph N · precip 0%
- forecast vintage 2026-09-26T17:09:24+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 61 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Patrick Mahomes | KC | attempts | 30.2 | 30.0 | 25.0 | 35.0 | 17.0 | 43.0 | 31.0 | 31.0 | 30.2 | 30.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kenneth Walker III | KC | carries | 15.8 | 15.0 | 10.0 | 21.0 | 4.0 | 29.0 | 17.6 | 17.0 | 15.8 | 15.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | carries | 4.3 | 4.0 | 3.0 | 6.0 | 1.0 | 8.0 | 4.0 | 4.0 | 4.3 | 4.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Emmett Johnson | KC | carries | 3.2 | 2.0 | 0.0 | 5.0 | 0.0 | 11.0 | 9.1 | 8.0 | 3.2 | 2.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | completions | 20.7 | 21.0 | 17.0 | 25.0 | 11.0 | 31.0 | 21.5 | 21.0 | 20.7 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Patrick Mahomes | KC | passing_tds | 1.9 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.0 | 2.0 | 2.0 | 2.0 | 0.00 | 0.98 | 5 | PRICED |
| Patrick Mahomes | KC | passing_yards | 218.2 | 214.0 | 167.0 | 266.0 | 102.0 | 348.0 | 238.7 | 233.0 | 238.7 | 234.0 | 0.00 | 0.98 | 9 | PRICED |
| Rashee Rice | KC | receiving_yards | 48.2 | 40.0 | 19.0 | 69.0 | 0.0 | 122.0 | 53.8 | 47.0 | 53.8 | 45.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 61 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 61 of 98 listed player/stat groups simulated and exposed, 37 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26SEP27KCMIA-KCKWALKER9-16` | Kenneth Walker III | 16.0 | 0.65 | 0.67 | 0.12 | -0.529 |
| `KXNFLREC-26SEP27KCMIA-KCKWALKER9-2` | Kenneth Walker III | 2.0 | 0.83 | 0.84 | 0.34 | -0.489 |
| `KXNFLREC-26SEP27KCMIA-KCKWALKER9-3` | Kenneth Walker III | 3.0 | 0.65 | 0.66 | 0.20 | -0.446 |
| `KXNFLREC-26SEP27KCMIA-KCTKELCE87-4` | Travis Kelce | 4.0 | 0.67 | 0.68 | 0.23 | -0.436 |
| `KXNFLREC-26SEP27KCMIA-KCTKELCE87-3` | Travis Kelce | 3.0 | 0.82 | 0.84 | 0.39 | -0.425 |
| `KXNFLREC-26SEP27KCMIA-MIAMWASHINGTON6-3` | Malik Washington | 3.0 | 0.72 | 0.74 | 0.30 | -0.422 |

_Ranked 345 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Caleb Douglas (WR, MIA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 1 skill players are Questionable (Ryan Miller (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLRSHATT-26SEP27KCMIA-KCEJOHNSON10-9 moved +0.310 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.529 on KXNFLRSHATT-26SEP27KCMIA-KCKWALKER9-16 (Kenneth Walker III). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.489 on KXNFLREC-26SEP27KCMIA-KCKWALKER9-2 (Kenneth Walker III). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLRSHATT-26SEP27KCMIA-KCPMAHOMES15-1 sits at a market price of 0.93 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?
7. Model and market differ by +1.3 points of spread. Does that come from one team's rating, from the total, or from a single ladder rung driving the reconstruction?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_KC_MIA.md`_


---

## LAC @ BUF — `2026_03_LAC_BUF`

- kickoff: 2026-09-27T17:00:00+00:00 (1417 minutes away) · state **PREGAME**
- venue: Highmark Stadium · roof outdoors · surface a_turf
- markets: 712 listed across 16 families — 366 supported, 290 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -7.29 | -7.94 |
| total | 50.50 | 50.43 |
| score | BUF 28.9 – LAC 21.6 | BUF 29.2 – LAC 21.2 |
| win prob BUF | 75.5% | 75.4% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -4.35 / total 24.91 · **2H** spread -3.50 / total 24.65 · **1Q** spread -2.76 / total 9.34 · **2Q** spread -2.88 / total 15.16 · **3Q** spread -1.17 / total 9.78 · **4Q** spread -1.31 / total 14.23

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Brenen Thompson (WR, LAC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Charlie Kolar (TE, LAC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- David Njoku (TE, LAC) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Kayode Awosika (G, LAC) — Out [high] — ruled out
- Trey Pipkins III (OT, LAC) — Out [single_source] — ruled out
- Dalvin Tomlinson (DT, LAC) — Out [high] — ruled out
- Elijah Molden (CB, LAC) — Out [high] — ruled out
- Jordan Hancock (CB, BUF) — Injured Reserve [high] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (6)** — resolves at the inactive release, T−90m

- Trey Lance (QB, LAC) — Questionable [high]
- DJ Moore (WR, BUF) — Questionable [high]
- Keon Coleman (WR, BUF) — Questionable [high]
- Ar'maj Reed-Adams (G, BUF) — Questionable [single_source]
- Ed Oliver (DT, BUF) — Questionable [high]
- Rodney Shelley (CB, LAC) — Questionable [high]

### WEATHER

- Mostly Cloudy · 66°F · wind 9 mph NE · precip 2%
- forecast vintage 2026-09-26T17:08:16+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 56 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Josh Allen | BUF | attempts | 30.0 | 30.0 | 25.0 | 35.0 | 16.0 | 43.0 | 30.0 | 30.0 | 30.0 | 30.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| James Cook III | BUF | carries | 15.5 | 15.0 | 10.0 | 20.0 | 4.0 | 29.0 | 17.5 | 17.0 | 15.5 | 15.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | carries | 8.2 | 7.0 | 5.0 | 11.0 | 2.0 | 18.0 | 8.0 | 8.0 | 8.2 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | completions | 20.3 | 20.0 | 17.0 | 24.0 | 11.0 | 30.0 | 20.4 | 20.0 | 20.3 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Josh Allen | BUF | passing_tds | 1.8 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 1.8 | 2.0 | 1.8 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Josh Allen | BUF | passing_yards | 230.7 | 227.0 | 177.0 | 282.0 | 105.0 | 368.0 | 242.5 | 237.0 | 242.5 | 238.0 | 0.00 | 0.97 | 9 | PRICED |
| Dalton Kincaid | BUF | receiving_yards | 47.3 | 38.0 | 16.0 | 69.0 | 0.0 | 127.0 | 63.2 | 56.0 | 63.1 | 51.0 | 0.00 | 0.98 | 12 | PRICED |
| Khalil Shakir | BUF | receiving_yards | 43.5 | 36.0 | 15.0 | 63.0 | 0.0 | 114.0 | 46.6 | 39.0 | 46.6 | 38.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 56 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 56 of 91 listed player/stat groups simulated and exposed, 35 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP27LACBUF-BUFDKINCAID86-3` | Dalton Kincaid | 3.0 | 0.79 | 0.81 | 0.26 | -0.530 |
| `KXNFLRSHATT-26SEP27LACBUF-LACOHAMPTON8-13` | Omarion Hampton | 13.0 | 0.72 | 0.75 | 0.21 | -0.513 |
| `KXNFLREC-26SEP27LACBUF-BUFDKINCAID86-4` | Dalton Kincaid | 4.0 | 0.64 | 0.66 | 0.15 | -0.494 |
| `KXNFLREC-26SEP27LACBUF-BUFDKINCAID86-2` | Dalton Kincaid | 2.0 | 0.92 | 0.93 | 0.44 | -0.472 |
| `KXNFLRECYDS-26SEP27LACBUF-BUFDKINCAID86-40` | Dalton Kincaid | 40.0 | 0.69 | 0.70 | 0.22 | -0.467 |
| `KXNFLRSHATT-26SEP27LACBUF-BUFJALLEN17-5` | Josh Allen | 5.0 | 0.78 | 0.80 | 0.31 | -0.462 |

_Ranked 363 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Brenen Thompson (WR, LAC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Charlie Kolar (TE, LAC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 3 skill players are Questionable (DJ Moore (WR), Keon Coleman (WR), Trey Lance (QB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL1HTEAMTOTAL-26SEP27LACBUF-BUF10 moved +0.250 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.530 on KXNFLREC-26SEP27LACBUF-BUFDKINCAID86-3 (Dalton Kincaid). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.513 on KXNFLRSHATT-26SEP27LACBUF-LACOHAMPTON8-13 (Omarion Hampton). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26SEP27LACBUF-BUFDKINCAID86-2 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_LAC_BUF.md`_


---

## NE @ JAX — `2026_03_NE_JAX`

- kickoff: 2026-09-27T17:00:00+00:00 (1417 minutes away) · state **PREGAME**
- venue: EverBank Stadium · roof outdoors · surface grass
- markets: 764 listed across 16 families — 398 supported, 310 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.85 | -2.36 |
| total | 46.62 | 47.18 |
| score | JAX 24.7 – NE 21.9 | JAX 24.8 – NE 22.4 |
| win prob JAX | 59.5% | 57.5% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -2.02 / total 23.39 · **2H** spread -0.71 / total 23.36 · **1Q** spread -0.97 / total 8.15 · **2Q** spread -0.45 / total 13.90 · **3Q** spread 0.23 / total 8.81 · **4Q** spread -0.10 / total 13.48

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- Mike Onwenu (G, NE) — Injured Reserve [high] — ruled out
- B.J. Green II (DE, JAX) — Injured Reserve [single_source] — ruled out
- Brenden Schooler (S, NE) — Out [high] — ruled out
- Dell Pettus (S, NE) — Injured Reserve [high] — ruled out
- Dre'Mont Jones (DE, NE) — Out [high] — ruled out
- Quintayvious Hutchins (LB, NE) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Eli Raridon (TE, NE) — Questionable [high]
- Albert Regis (DT, JAX) — Doubtful [high]
- Craig Woodson (S, NE) — Questionable [high]

### WEATHER

- Mostly Sunny · 85°F · wind 9 mph W · precip 0%
- forecast vintage 2026-09-26T17:08:23+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 64 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trevor Lawrence | JAX | attempts | 32.2 | 32.0 | 27.0 | 38.0 | 19.0 | 45.0 | 32.6 | 32.0 | 32.2 | 32.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bhayshul Tuten | JAX | carries | 10.9 | 10.0 | 6.0 | 15.0 | 1.0 | 23.0 | 13.0 | 13.0 | 10.9 | 10.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Trevor Lawrence | JAX | completions | 20.1 | 20.0 | 16.0 | 24.0 | 11.0 | 29.0 | 20.0 | 20.0 | 20.1 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Trevor Lawrence | JAX | passing_tds | 1.6 | 2.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Trevor Lawrence | JAX | passing_yards | 233.2 | 229.0 | 179.0 | 284.0 | 109.0 | 371.0 | 229.6 | 223.0 | 229.6 | 226.0 | 0.00 | 0.97 | 9 | PRICED |
| Parker Washington | JAX | receiving_yards | 67.0 | 58.0 | 29.0 | 95.0 | 0.0 | 162.0 | 70.7 | 63.0 | 70.7 | 62.0 | 0.00 | 0.98 | 13 | PRICED |
| Brian Thomas Jr. | JAX | receiving_yards | 42.4 | 32.0 | 12.0 | 62.0 | 0.0 | 120.0 | 43.3 | 35.0 | 43.3 | 33.0 | 0.00 | 0.97 | 10 | PRICED |
| Jakobi Meyers | JAX | receiving_yards | 35.0 | 26.0 | 8.0 | 52.0 | 0.0 | 103.0 | 39.9 | 33.0 | 39.9 | 30.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 64 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 64 of 104 listed player/stat groups simulated and exposed, 40 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26SEP27NEJAC-JACBTUTEN33-10` | Bhayshul Tuten | 10.0 | 0.79 | 0.80 | 0.20 | -0.588 |
| `KXNFLRSHYDS-26SEP27NEJAC-JACBTUTEN33-30` | Bhayshul Tuten | 30.0 | 0.78 | 0.80 | 0.25 | -0.530 |
| `KXNFLRSHYDS-26SEP27NEJAC-JACBTUTEN33-40` | Bhayshul Tuten | 40.0 | 0.67 | 0.69 | 0.16 | -0.509 |
| `KXNFLREC-26SEP27NEJAC-JACPWASHINGTON11-4` | Parker Washington | 4.0 | 0.73 | 0.75 | 0.30 | -0.438 |
| `KXNFLRSHATT-26SEP27NEJAC-NEDMAYE10-3` | Drake Maye | 3.0 | 0.85 | 0.87 | 0.41 | -0.437 |
| `KXNFLRSHYDS-26SEP27NEJAC-JACBTUTEN33-50` | Bhayshul Tuten | 50.0 | 0.54 | 0.55 | 0.10 | -0.437 |

_Ranked 393 tradable markets; 5 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. 1 skill players are Questionable (Eli Raridon (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
2. KXNFLFFPTS-26SEP27NEJAC-JACPWASHINGTON11-15P2 moved -0.180 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
3. The model disagrees by -0.588 on KXNFLRSHATT-26SEP27NEJAC-JACBTUTEN33-10 (Bhayshul Tuten). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
4. The model disagrees by -0.530 on KXNFLRSHYDS-26SEP27NEJAC-JACBTUTEN33-30 (Bhayshul Tuten). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. KXNFLREC-26SEP27NEJAC-NEHHENRY85-2 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_NE_JAX.md`_


---

## NYJ @ DET — `2026_03_NYJ_DET`

- kickoff: 2026-09-27T17:00:00+00:00 (1417 minutes away) · state **PREGAME**
- venue: Ford Field · roof dome · surface fieldturf
- markets: 713 listed across 16 families — 388 supported, 269 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -6.67 | -6.47 |
| total | 48.88 | 49.02 |
| score | DET 27.8 – NYJ 21.1 | DET 27.7 – NYJ 21.3 |
| win prob DET | 72.5% | 71.3% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -3.80 / total 24.47 · **2H** spread -3.08 / total 24.18 · **1Q** spread -2.29 / total 8.69 · **2Q** spread -2.69 / total 14.73 · **3Q** spread -1.25 / total 9.38 · **4Q** spread -0.88 / total 14.00

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Arian Smith (WR, NYJ) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Mason Taylor (TE, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Ben Bartch (G, DET) — Out [high] — ruled out
- Avonte Maddox (CB, DET) — Injured Reserve [high] — ruled out
- David Onyemata (DT, NYJ) — Injured Reserve [high] — ruled out
- Kiko Mauigoa (LB, NYJ) — Out [high] — ruled out
- Marcelino McCrary-Ball (LB, NYJ) — Injured Reserve [high] — ruled out
- Minkah Fitzpatrick (S, NYJ) — Out [high] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Adonai Mitchell (WR, NYJ) — Questionable [high]
- Kene Nwangwu (RB, NYJ) — Doubtful [high]
- Joseph Ossai (DE, NYJ) — Questionable [high]

### WEATHER

roof is dome -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 53 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jared Goff | DET | attempts | 32.2 | 32.0 | 27.0 | 38.0 | 19.0 | 46.0 | 33.4 | 33.0 | 32.2 | 32.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jahmyr Gibbs | DET | carries | 22.3 | 22.0 | 17.0 | 28.0 | 9.0 | 36.0 | 18.9 | 18.0 | 22.3 | 22.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jared Goff | DET | completions | 21.8 | 22.0 | 18.0 | 26.0 | 12.0 | 32.0 | 23.2 | 23.0 | 21.8 | 22.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jared Goff | DET | passing_tds | 1.8 | 2.0 | 1.0 | 3.0 | 0.0 | 4.0 | 2.0 | 2.0 | 2.0 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Jared Goff | DET | passing_yards | 240.0 | 235.0 | 185.0 | 292.0 | 115.0 | 380.0 | 261.3 | 257.0 | 261.3 | 256.0 | 0.00 | 0.97 | 10 | PRICED |
| Amon-Ra St. Brown | DET | receiving_yards | 80.0 | 72.0 | 42.0 | 110.0 | 8.0 | 175.0 | 81.4 | 75.0 | 81.4 | 74.0 | 0.00 | 0.97 | 13 | PRICED |
| Jameson Williams | DET | receiving_yards | 45.3 | 35.0 | 13.0 | 66.0 | 0.0 | 127.0 | 60.7 | 53.0 | 60.6 | 47.0 | 0.00 | 0.97 | 12 | PRICED |
| Sam LaPorta | DET | receiving_yards | 43.9 | 36.0 | 16.0 | 63.0 | 0.0 | 113.0 | 50.7 | 45.0 | 50.7 | 42.0 | 0.00 | 0.98 | 9 | PRICED |

_8 of 53 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 53 of 84 listed player/stat groups simulated and exposed, 31 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP27NYJDET-NYJKSADIQ16-2` | Kenyon Sadiq | 2.0 | 0.79 | 0.80 | 0.18 | -0.607 |
| `KXNFLRSHATT-26SEP27NYJDET-DETJGIBBS0-15` | Jahmyr Gibbs | 15.0 | 0.78 | 0.81 | 0.19 | -0.591 |
| `KXNFLRECYDS-26SEP27NYJDET-NYJKSADIQ16-15` | Kenyon Sadiq | 15.0 | 0.72 | 0.74 | 0.13 | -0.588 |
| `KXNFLREC-26SEP27NYJDET-NYJGWILSON5-5` | Garrett Wilson | 5.0 | 0.72 | 0.73 | 0.19 | -0.535 |
| `KXNFLREC-26SEP27NYJDET-NYJGWILSON5-4` | Garrett Wilson | 4.0 | 0.84 | 0.86 | 0.33 | -0.519 |
| `KXNFLREC-26SEP27NYJDET-NYJGWILSON5-6` | Garrett Wilson | 6.0 | 0.59 | 0.60 | 0.10 | -0.498 |

_Ranked 383 tradable markets; 5 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Mason Taylor (TE, NYJ) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Arian Smith (WR, NYJ) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Adonai Mitchell (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL1HTEAMTOTAL-26SEP27NYJDET-NYJ14 moved -0.215 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.607 on KXNFLREC-26SEP27NYJDET-NYJKSADIQ16-2 (Kenyon Sadiq). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.591 on KXNFLRSHATT-26SEP27NYJDET-DETJGIBBS0-15 (Jahmyr Gibbs). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26SEP27NYJDET-NYJGWILSON5-3 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_NYJ_DET.md`_


---

## SEA @ WAS — `2026_03_SEA_WAS`

- kickoff: 2026-09-27T17:00:00+00:00 (1417 minutes away) · state **PREGAME**
- venue: Northwest Stadium · roof outdoors · surface grass
- markets: 697 listed across 16 families — 351 supported, 290 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 7.72 | 8.55 |
| total | 40.17 | 40.02 |
| score | WAS 16.2 – SEA 23.9 | WAS 15.7 – SEA 24.3 |
| win prob WAS | 24.5% | 21.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 4.20 / total 20.46 · **2H** spread 3.68 / total 19.08 · **1Q** spread 2.00 / total 7.68 · **2Q** spread 2.92 / total 12.04 · **3Q** spread 1.42 / total 7.75 · **4Q** spread 2.50 / total 10.42

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Jayden Daniels (QB, WAS) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Chig Okonkwo (TE, WAS) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Zach Charbonnet (RB, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Anthony Bradford (G, SEA) — Injured Reserve [high] — ruled out
- Sam Cosmi (G, WAS) — Out [high] — ruled out
- Frankie Luvu (LB, WAS) — Out [high] — ruled out
- Julian Love (S, SEA) — Out [high] — ruled out
- Nick Cross (S, WAS) — Out [high] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Brandon Pili (DT, SEA) — Questionable [high]

### WEATHER

- Light Rain Likely · 62°F · wind 18 mph NW · precip 65%
- forecast vintage 2026-09-26T17:09:30+00:00 · material: **True**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 55 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sam Darnold | SEA | attempts | 27.9 | 28.0 | 23.0 | 33.0 | 15.0 | 41.0 | 28.3 | 28.0 | 27.9 | 28.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jadarian Price | SEA | carries | 12.0 | 11.0 | 7.0 | 16.0 | 2.0 | 25.0 | 13.4 | 13.0 | 12.0 | 11.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Sam Darnold | SEA | completions | 18.7 | 19.0 | 15.0 | 22.0 | 10.0 | 28.0 | 18.9 | 19.0 | 18.7 | 19.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Sam Darnold | SEA | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.5 | 1.0 | 1.5 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Sam Darnold | SEA | passing_yards | 218.9 | 214.0 | 164.0 | 268.0 | 97.0 | 356.0 | 223.8 | 218.0 | 223.8 | 219.0 | 0.00 | 0.98 | 9 | PRICED |
| Jaxon Smith-Njigba | SEA | receiving_yards | 79.8 | 71.0 | 40.0 | 111.0 | 6.0 | 181.0 | 99.1 | 91.0 | 98.7 | 89.0 | 0.00 | 0.97 | 14 | PRICED |
| Rashid Shaheed | SEA | receiving_yards | 31.5 | 22.0 | 5.0 | 47.0 | 0.0 | 98.0 | 35.2 | 27.0 | 35.2 | 24.0 | 0.00 | 0.97 | 8 | PRICED |
| Cooper Kupp | SEA | receiving_yards | 28.4 | 19.0 | 4.0 | 43.0 | 0.0 | 90.0 | 26.3 | 19.0 | 26.3 | 18.0 | 0.00 | 0.97 | 7 | PRICED |

_8 of 55 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 55 of 83 listed player/stat groups simulated and exposed, 28 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26SEP27SEAWAS-SEAJPRICE8-10` | Jadarian Price | 10.0 | 0.81 | 0.81 | 0.17 | -0.636 |
| `KXNFLRSHYDS-26SEP27SEAWAS-SEAJPRICE8-25` | Jadarian Price | 25.0 | 0.82 | 0.83 | 0.21 | -0.617 |
| `KXNFLRSHYDS-26SEP27SEAWAS-SEAJPRICE8-30` | Jadarian Price | 30.0 | 0.77 | 0.77 | 0.17 | -0.597 |
| `KXNFLRSHYDS-26SEP27SEAWAS-SEAJPRICE8-40` | Jadarian Price | 40.0 | 0.65 | 0.65 | 0.11 | -0.535 |
| `KXNFLRSHYDS-26SEP27SEAWAS-SEAJPRICE8-50` | Jadarian Price | 50.0 | 0.53 | 0.53 | 0.07 | -0.451 |
| `KXNFLRSHATT-26SEP27SEAWAS-SEAJPRICE8-13` | Jadarian Price | 13.0 | 0.56 | 0.56 | 0.11 | -0.444 |

_Ranked 349 tradable markets; 2 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Zach Charbonnet (RB, SEA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Chig Okonkwo (TE, WAS) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. Wind/precipitation is flagged material (18 mph, 65% precip). Is that already in the total, and does the forecast vintage (2026-09-26T17:09:30+00:00) predate the last big market move?
4. KXNFLGAME-26SEP27SEAWAS-SEA moved +0.305 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.636 on KXNFLRSHATT-26SEP27SEAWAS-SEAJPRICE8-10 (Jadarian Price). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.617 on KXNFLRSHYDS-26SEP27SEAWAS-SEAJPRICE8-25 (Jadarian Price). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRECYDS-26SEP27SEAWAS-SEATHORTON15-40 sits at a market price of 0.05 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_SEA_WAS.md`_


---

## TEN @ NYG — `2026_03_TEN_NYG`

- kickoff: 2026-09-27T17:00:00+00:00 (1417 minutes away) · state **PREGAME**
- venue: MetLife Stadium · roof outdoors · surface fieldturf
- markets: 693 listed across 16 families — 345 supported, 292 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.36 | -1.96 |
| total | 38.15 | 38.24 |
| score | NYG 20.3 – TEN 17.9 | NYG 20.1 – TEN 18.1 |
| win prob NYG | 55.5% | 57.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -0.98 / total 18.62 · **2H** spread -0.50 / total 18.72 · **1Q** spread -0.39 / total 7.62 · **2Q** spread -0.20 / total 10.78 · **3Q** spread 0.23 / total 7.65 · **4Q** spread -0.02 / total 10.18

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (1)**

- Jaxson Dart (QB, NYG) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him

**Questionable / Doubtful (5)** — resolves at the inactive release, T−90m

- Tyjae Spears (RB, TEN) — Questionable [high]
- Brian Burns (LB, NYG) — Questionable [high]
- Cor'Dale Flott (CB, TEN) — Questionable [high]
- Deonte Banks (CB, NYG) — Questionable [high]
- Tyler Nubin (S, NYG) — Questionable [high]

### WEATHER

- Rain Showers · 65°F · wind 17 mph NE · precip 94%
- forecast vintage 2026-09-26T17:09:26+00:00 · material: **True**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 57 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jameis Winston | NYG | attempts | 30.3 | 30.0 | 25.0 | 36.0 | 17.0 | 43.0 | 30.1 | 30.0 | 30.3 | 30.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Cam Skattebo | NYG | carries | 11.6 | 11.0 | 7.0 | 16.0 | 2.0 | 24.0 | 17.2 | 16.0 | 11.6 | 11.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jameis Winston | NYG | completions | 19.7 | 20.0 | 16.0 | 23.0 | 10.0 | 29.0 | 17.9 | 18.0 | 19.7 | 20.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jameis Winston | NYG | passing_tds | 1.2 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.1 | 1.0 | 1.1 | 1.0 | 0.00 | 0.98 | 4 | PRICED |
| Jameis Winston | NYG | passing_yards | 215.0 | 210.0 | 162.0 | 262.0 | 98.0 | 349.0 | 218.9 | 204.0 | 218.9 | 214.0 | 0.00 | 0.98 | 1 | PRICED |
| Malik Nabers | NYG | receiving_yards | 52.9 | 44.0 | 21.0 | 76.0 | 0.0 | 136.0 | 61.8 | 54.0 | 61.8 | 52.0 | 0.00 | 0.97 | 11 | PRICED |
| Isaiah Likely | NYG | receiving_yards | 35.1 | 28.0 | 10.0 | 51.0 | 0.0 | 99.0 | 46.1 | 39.0 | 46.1 | 36.0 | 0.00 | 0.97 | 10 | PRICED |
| Malachi Fields | NYG | receiving_yards | 33.4 | 24.0 | 7.0 | 50.0 | 0.0 | 102.0 | 30.1 | 23.0 | 30.1 | 22.0 | 0.00 | 0.97 | 7 | PRICED |

_8 of 57 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 57 of 90 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26SEP27TENNYG-NYGCSKATTEBO44-13` | Cam Skattebo | 13.0 | 0.74 | 0.77 | 0.19 | -0.551 |
| `KXNFLREC-26SEP27TENNYG-NYGILIKELY9-3` | Isaiah Likely | 3.0 | 0.74 | 0.75 | 0.21 | -0.537 |
| `KXNFLREC-26SEP27TENNYG-TENCTATE14-2` | Carnell Tate | 2.0 | 0.83 | 0.85 | 0.31 | -0.519 |
| `KXNFLRECYDS-26SEP27TENNYG-NYGILIKELY9-25` | Isaiah Likely | 25.0 | 0.71 | 0.73 | 0.20 | -0.508 |
| `KXNFLREC-26SEP27TENNYG-NYGILIKELY9-2` | Isaiah Likely | 2.0 | 0.86 | 0.90 | 0.36 | -0.508 |
| `KXNFLRECYDS-26SEP27TENNYG-NYGILIKELY9-15` | Isaiah Likely | 15.0 | 0.84 | 0.86 | 0.34 | -0.499 |

_Ranked 343 tradable markets; 2 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jaxson Dart (QB, NYG) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 1 skill players are Questionable (Tyjae Spears (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. Wind/precipitation is flagged material (17 mph, 94% precip). Is that already in the total, and does the forecast vintage (2026-09-26T17:09:26+00:00) predate the last big market move?
4. KXNFLTEAMTOTAL-26SEP27TENNYG-NYG22 moved -0.220 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.551 on KXNFLRSHATT-26SEP27TENNYG-NYGCSKATTEBO44-13 (Cam Skattebo). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.537 on KXNFLREC-26SEP27TENNYG-NYGILIKELY9-3 (Isaiah Likely). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLRSHATT-26SEP27TENNYG-TENCWARD1-1 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_TEN_NYG.md`_


---

## ARI @ SF — `2026_03_ARI_SF`

- kickoff: 2026-09-27T20:05:00+00:00 (1602 minutes away) · state **PREGAME**
- venue: Levi's Stadium · roof outdoors · surface grass
- markets: 683 listed across 16 families — 351 supported, 276 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -7.88 | -8.76 |
| total | 48.50 | 48.31 |
| score | SF 28.2 – ARI 20.3 | SF 28.5 – ARI 19.8 |
| win prob SF | 77.5% | 76.5% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -5.50 / total 24.08 · **2H** spread -4.14 / total 24.00 · **1Q** spread -2.71 / total 8.75 · **2Q** spread -3.19 / total 14.53 · **3Q** spread -2.70 / total 9.42 · **4Q** spread -2.28 / total 14.05

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Brandon Aiyuk (WR, SF) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Demarcus Robinson (WR, SF) — Out [conflicting] — ruled out -- role redistributes to the depth chart behind him
- C.J. West (DT, SF) — Injured Reserve [high] — ruled out
- Dadrion Taylor-Demerson (S, ARI) — Out [high] — ruled out
- James Thompson Jr. (DT, SF) — Out [single_source] — ruled out
- Nick Bosa (DE, SF) — Out [high] — ruled out
- Romello Height (DE, SF) — Out [high] — ruled out
- Will Johnson (CB, ARI) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Mike Evans (WR, SF) — Questionable [high]
- Jack Jones (CB, SF) — Questionable [high]
- Max Melton (CB, ARI) — Questionable [high]
- Roy Lopez (DT, ARI) — Questionable [high]

### WEATHER

- Sunny · 66°F · wind 6 mph W · precip 0%
- forecast vintage 2026-09-26T17:09:32+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 50 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jacoby Brissett | ARI | attempts | 35.3 | 35.0 | 30.0 | 41.0 | 22.0 | 49.0 | 33.2 | 33.0 | 35.3 | 35.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jeremiyah Love | ARI | carries | 9.7 | 9.0 | 5.0 | 13.0 | 1.0 | 21.0 | 11.1 | 11.0 | 9.7 | 9.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | ARI | completions | 22.4 | 22.0 | 19.0 | 26.0 | 13.0 | 32.0 | 22.3 | 22.0 | 22.4 | 22.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Jacoby Brissett | ARI | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.2 | 1.0 | 1.2 | 1.0 | 0.00 | 0.97 | 1 | PRICED |
| Jacoby Brissett | ARI | passing_yards | 224.4 | 220.0 | 173.0 | 271.0 | 109.0 | 357.0 | 229.9 | 224.0 | 229.9 | 226.0 | 0.00 | 0.97 | 9 | PRICED |
| Trey McBride | ARI | receiving_yards | 62.4 | 56.0 | 32.0 | 86.0 | 5.0 | 140.0 | 72.0 | 66.0 | 72.0 | 64.0 | 0.00 | 0.98 | 11 | PRICED |
| Michael Wilson | ARI | receiving_yards | 54.6 | 46.0 | 22.0 | 78.0 | 0.0 | 137.0 | 51.0 | 44.0 | 51.0 | 43.0 | 0.00 | 0.97 | 10 | PRICED |
| Marvin Harrison Jr. | ARI | receiving_yards | 31.0 | 21.0 | 4.0 | 46.0 | 0.0 | 100.0 | 39.2 | 31.0 | 39.2 | 27.0 | 0.00 | 0.97 | 8 | PRICED |

_8 of 50 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 50 of 79 listed player/stat groups simulated and exposed, 29 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP27ARISF-ARIJLOVE4-2` | Jeremiyah Love | 2.0 | 0.72 | 0.73 | 0.16 | -0.558 |
| `KXNFLRSHYDS-26SEP27ARISF-ARIJLOVE4-20` | Jeremiyah Love | 20.0 | 0.80 | 0.80 | 0.24 | -0.550 |
| `KXNFLRSHATT-26SEP27ARISF-ARIJLOVE4-9` | Jeremiyah Love | 9.0 | 0.73 | 0.75 | 0.20 | -0.538 |
| `KXNFLRSHYDS-26SEP27ARISF-ARIJLOVE4-25` | Jeremiyah Love | 25.0 | 0.72 | 0.73 | 0.20 | -0.528 |
| `KXNFLRSHYDS-26SEP27ARISF-ARIJLOVE4-30` | Jeremiyah Love | 30.0 | 0.64 | 0.65 | 0.15 | -0.486 |
| `KXNFLRECYDS-26SEP27ARISF-ARIJLOVE4-15` | Jeremiyah Love | 15.0 | 0.51 | 0.52 | 0.03 | -0.477 |

_Ranked 343 tradable markets; 8 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Brandon Aiyuk (WR, SF) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Demarcus Robinson (WR, SF) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Mike Evans (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLRECYDS-26SEP27ARISF-ARIMHARRISON18-25 moved +0.175 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.558 on KXNFLREC-26SEP27ARISF-ARIJLOVE4-2 (Jeremiyah Love). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.550 on KXNFLRSHYDS-26SEP27ARISF-ARIJLOVE4-20 (Jeremiyah Love). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26SEP27ARISF-ARITMCBRIDE85-4 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_ARI_SF.md`_


---

## MIN @ TB — `2026_03_MIN_TB`

- kickoff: 2026-09-27T20:05:00+00:00 (1602 minutes away) · state **PREGAME**
- venue: Raymond James Stadium · roof outdoors · surface grass
- markets: 739 listed across 16 families — 387 supported, 296 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 0.75 | 1.54 |
| total | 42.84 | 43.12 |
| score | TB 21.0 – MIN 21.8 | TB 20.8 – MIN 22.3 |
| win prob TB | 47.5% | 44.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 0.56 / total 21.44 · **2H** spread 0.43 / total 20.88 · **1Q** spread 0.05 / total 7.85 · **2Q** spread -0.24 / total 13.10 · **3Q** spread -0.50 / total 7.94 · **4Q** spread -0.15 / total 11.78

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (5)**

- Nick Samac (C, MIN) — Out [high] — ruled out
- Brett Thorson (P, MIN) — Out [high] — ruled out
- Josh Hayes (CB, TB) — Injured Reserve [high] — ruled out
- Josiah Trotter (LB, TB) — Out [high] — ruled out
- Rueben Bain Jr. (LB, TB) — Out [single_source] — ruled out

### WEATHER

- Mostly Sunny · 86°F · wind 5 mph WNW · precip 0%
- forecast vintage 2026-09-26T17:10:33+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 62 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kyler Murray | MIN | attempts | 28.2 | 28.0 | 24.0 | 33.0 | 16.0 | 40.0 | 30.5 | 30.0 | 28.2 | 28.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Aaron Jones Sr. | MIN | carries | 18.7 | 19.0 | 14.0 | 24.0 | 7.0 | 31.0 | 14.5 | 14.0 | 18.7 | 19.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kyler Murray | MIN | completions | 18.2 | 18.0 | 15.0 | 22.0 | 10.0 | 27.0 | 19.1 | 19.0 | 18.2 | 18.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kyler Murray | MIN | passing_tds | 1.3 | 1.0 | 0.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Kyler Murray | MIN | passing_yards | 195.5 | 191.0 | 146.0 | 240.0 | 87.0 | 320.0 | 214.7 | 209.0 | 214.7 | 210.0 | 0.00 | 0.97 | 9 | PRICED |
| Justin Jefferson | MIN | receiving_yards | 61.1 | 53.0 | 28.0 | 86.0 | 0.0 | 144.0 | 76.4 | 70.0 | 76.4 | 67.0 | 0.00 | 0.97 | 12 | PRICED |
| Jordan Addison | MIN | receiving_yards | 33.8 | 25.0 | 8.0 | 50.0 | 0.0 | 100.0 | 43.1 | 35.0 | 43.1 | 32.0 | 0.00 | 0.98 | 9 | PRICED |
| T.J. Hockenson | MIN | receiving_yards | 30.0 | 23.0 | 8.0 | 44.0 | 0.0 | 88.0 | 35.3 | 30.0 | 35.3 | 27.0 | 0.00 | 0.98 | 7 | PRICED |

_8 of 62 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 62 of 97 listed player/stat groups simulated and exposed, 35 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP27MINTB-MINJJEFFERSON18-5` | Justin Jefferson | 5.0 | 0.69 | 0.71 | 0.23 | -0.456 |
| `KXNFLREC-26SEP27MINTB-MINJJEFFERSON18-4` | Justin Jefferson | 4.0 | 0.82 | 0.84 | 0.39 | -0.428 |
| `KXNFLREC-26SEP27MINTB-MINJJEFFERSON18-6` | Justin Jefferson | 6.0 | 0.55 | 0.56 | 0.13 | -0.418 |
| `KXNFLREC-26SEP27MINTB-MINTHOCKENSON87-3` | T.J. Hockenson | 3.0 | 0.69 | 0.69 | 0.28 | -0.406 |
| `KXNFLREC-26SEP27MINTB-MINTHOCKENSON87-2` | T.J. Hockenson | 2.0 | 0.86 | 0.88 | 0.47 | -0.388 |
| `KXNFLRSHATT-26SEP27MINTB-MINAJONES33-12` | Aaron Jones Sr. | 12.0 | 0.63 | 0.64 | 0.26 | -0.375 |

_Ranked 384 tradable markets; 3 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. KXNFLRECYDS-26SEP27MINTB-MINJADDISON3-40 moved +0.150 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
2. The model disagrees by -0.456 on KXNFLREC-26SEP27MINTB-MINJJEFFERSON18-5 (Justin Jefferson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
3. The model disagrees by -0.428 on KXNFLREC-26SEP27MINTB-MINJJEFFERSON18-4 (Justin Jefferson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
4. KXNFLREC-26SEP27MINTB-MINJJEFFERSON18-3 sits at a market price of 0.91 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_MIN_TB.md`_


---

## BAL @ DAL — `2026_03_BAL_DAL`

- kickoff: 2026-09-27T20:25:00+00:00 (1622 minutes away) · state **PREGAME**
- venue: Maracana Stadium · roof  · surface matrixturf
- markets: 752 listed across 16 families — 416 supported, 279 no model, 48 rules unresolved, 9 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 9 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 3.35 | 3.61 |
| total | 53.88 | 54.21 |
| score | DAL 25.3 – BAL 28.6 | DAL 25.3 – BAL 28.9 |
| win prob DAL | 37.5% | 36.4% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.81 / total 27.27 · **2H** spread 1.50 / total 27.00 · **1Q** spread 1.20 / total 10.00 · **2Q** spread 1.17 / total 15.97 · **3Q** spread 0.36 / total 10.29 · **4Q** spread 0.29 / total 14.84

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- Ronnie Stanley (OT, BAL) — Out [high] — ruled out
- Cobie Durant (CB, DAL) — Out [high] — ruled out
- DeMarvion Overshown (LB, DAL) — Out [high] — ruled out
- Malik Hooker (S, DAL) — Out [high] — ruled out
- P.J. Locke (S, DAL) — Out [high] — ruled out
- T.J. Tampa (CB, BAL) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Zay Flowers (WR, BAL) — Questionable [high]

### WEATHER

- None · None°F · wind None  · precip None%
- forecast vintage None · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 60 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Lamar Jackson | BAL | attempts | 27.3 | 27.0 | 23.0 | 32.0 | 15.0 | 39.0 | 28.1 | 28.0 | 27.3 | 27.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Derrick Henry | BAL | carries | 20.9 | 21.0 | 16.0 | 26.0 | 8.0 | 35.0 | 18.7 | 18.0 | 20.9 | 21.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Lamar Jackson | BAL | carries | 5.1 | 5.0 | 3.0 | 6.0 | 1.0 | 11.0 | 6.2 | 6.0 | 5.1 | 5.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Lamar Jackson | BAL | completions | 18.0 | 18.0 | 15.0 | 22.0 | 9.0 | 27.0 | 19.1 | 19.0 | 18.0 | 18.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Lamar Jackson | BAL | passing_tds | 1.6 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.8 | 2.0 | 1.8 | 2.0 | 0.00 | 0.97 | 5 | PRICED |
| Lamar Jackson | BAL | passing_yards | 207.5 | 202.0 | 155.0 | 256.0 | 91.0 | 341.0 | 242.6 | 236.0 | 242.6 | 236.0 | 0.00 | 0.97 | 10 | PRICED |
| Mark Andrews | BAL | receiving_yards | 40.5 | 33.0 | 14.0 | 59.0 | 0.0 | 109.0 | 44.1 | 37.0 | 44.1 | 36.0 | 0.00 | 0.97 | 12 | PRICED |
| Rashod Bateman | BAL | receiving_yards | 35.5 | 26.0 | 8.0 | 52.0 | 0.0 | 108.0 | 49.2 | 40.0 | 49.2 | 36.0 | 0.00 | 0.98 | 13 | PRICED |

_8 of 60 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 60 of 90 listed player/stat groups simulated and exposed, 30 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP27BALDAL-DALCLAMB88-5` | CeeDee Lamb | 5.0 | 0.77 | 0.79 | 0.26 | -0.514 |
| `KXNFLREC-26SEP27BALDAL-DALCLAMB88-6` | CeeDee Lamb | 6.0 | 0.65 | 0.66 | 0.14 | -0.508 |
| `KXNFLRSHATT-26SEP27BALDAL-BALLJACKSON8-4` | Lamar Jackson | 4.0 | 0.81 | 0.82 | 0.31 | -0.504 |
| `KXNFLREC-26SEP27BALDAL-BALMANDREWS89-3` | Mark Andrews | 3.0 | 0.74 | 0.76 | 0.24 | -0.495 |
| `KXNFLREC-26SEP27BALDAL-DALCLAMB88-4` | CeeDee Lamb | 4.0 | 0.88 | 0.90 | 0.42 | -0.459 |
| `KXNFLREC-26SEP27BALDAL-BALMANDREWS89-2` | Mark Andrews | 2.0 | 0.88 | 0.89 | 0.42 | -0.455 |

_Ranked 412 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. 1 skill players are Questionable (Zay Flowers (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
2. KXNFLFFPTS-26SEP27BALDAL-BALMANDREWS89-11P6 moved -0.225 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
3. The model disagrees by -0.514 on KXNFLREC-26SEP27BALDAL-DALCLAMB88-5 (CeeDee Lamb). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
4. The model disagrees by -0.508 on KXNFLREC-26SEP27BALDAL-DALCLAMB88-6 (CeeDee Lamb). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. KXNFLREC-26SEP27BALDAL-DALCLAMB88-4 sits at a market price of 0.88 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_BAL_DAL.md`_


---

## LV @ NO — `2026_03_LV_NO`

- kickoff: 2026-09-27T20:25:00+00:00 (1622 minutes away) · state **PREGAME**
- venue: Caesars Superdome · roof dome · surface sportturf
- markets: 673 listed across 15 families — 334 supported, 283 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.22 | -3.28 |
| total | 44.38 | 44.05 |
| score | NO 23.8 – LV 20.6 | NO 23.7 – LV 20.4 |
| win prob NO | 61.5% | 61.3% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread -2.50 / total 22.00 · **2H** spread -1.77 / total 21.75 · **1Q** spread -0.70 / total 7.91 · **2Q** spread -0.68 / total 13.07 · **3Q** spread -0.28 / total 8.32 · **4Q** spread -0.34 / total 12.44

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (5)**

- Barion Brown (WR, NO) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Kelvin Banks Jr. (OT, NO) — Injured Reserve [single_source] — ruled out
- Christen Miller (DT, NO) — Out [high] — ruled out
- Treydan Stukes (S, LV) — Out [high] — ruled out
- Zach Wood (LS, NO) — Injured Reserve [single_source] — ruled out

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Aidan O'Connell (QB, LV) — Questionable [high]
- Brock Bowers (TE, LV) — Questionable [high]
- Kwity Paye (DE, LV) — Questionable [high]
- Martin Emerson Jr. (CB, NO) — Questionable [single_source]

### WEATHER

roof is dome -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 52 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kirk Cousins | LV | attempts | 31.5 | 32.0 | 27.0 | 37.0 | 18.0 | 45.0 | 32.3 | 32.0 | 31.5 | 32.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Ashton Jeanty | LV | carries | 16.8 | 17.0 | 12.0 | 22.0 | 5.0 | 29.0 | 18.0 | 18.0 | 16.8 | 17.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kirk Cousins | LV | completions | 20.4 | 20.0 | 17.0 | 24.0 | 11.0 | 30.0 | 20.7 | 20.0 | 20.4 | 20.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kirk Cousins | LV | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.3 | 1.0 | 1.3 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Kirk Cousins | LV | passing_yards | 201.6 | 198.0 | 153.0 | 245.0 | 93.0 | 325.0 | 236.0 | 226.0 | 236.0 | 231.0 | 0.00 | 0.97 | 1 | PRICED |
| Tre Tucker | LV | receiving_yards | 42.9 | 34.0 | 13.0 | 63.0 | 0.0 | 118.0 | 47.5 | 39.0 | 47.5 | 38.0 | 0.00 | 0.97 | 11 | PRICED |
| Ashton Jeanty | LV | receiving_yards | 27.4 | 21.0 | 8.0 | 39.0 | 0.0 | 77.0 | 25.6 | 20.0 | 25.6 | 20.0 | 0.00 | 0.98 | 7 | PRICED |
| Jalen Nailor | LV | receiving_yards | 24.2 | 15.0 | 0.0 | 36.0 | 0.0 | 83.0 | 29.7 | 23.0 | 29.7 | 18.0 | 0.00 | 0.98 | 8 | PRICED |

_8 of 52 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 52 of 85 listed player/stat groups simulated and exposed, 33 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP27LVNO-NODVELE14-3` | Devaughn Vele | 3.0 | 0.77 | 0.78 | 0.31 | -0.462 |
| `KXNFLREC-26SEP27LVNO-LVAJEANTY2-3` | Ashton Jeanty | 3.0 | 0.71 | 0.74 | 0.27 | -0.447 |
| `KXNFLREC-26SEP27LVNO-NODVELE14-4` | Devaughn Vele | 4.0 | 0.59 | 0.61 | 0.17 | -0.417 |
| `KXNFLRSHATT-26SEP27LVNO-LVAJEANTY2-18` | Ashton Jeanty | 18.0 | 0.54 | 0.55 | 0.12 | -0.417 |
| `KXNFLREC-26SEP27LVNO-LVAJEANTY2-2` | Ashton Jeanty | 2.0 | 0.86 | 0.90 | 0.46 | -0.409 |
| `KXNFLREC-26SEP27LVNO-LVAJEANTY2-4` | Ashton Jeanty | 4.0 | 0.55 | 0.56 | 0.15 | -0.400 |

_Ranked 330 tradable markets; 4 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Barion Brown (WR, NO) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 2 skill players are Questionable (Aidan O'Connell (QB), Brock Bowers (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFL1HTEAMTOTAL-26SEP27LVNO-NO10 moved +0.150 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.462 on KXNFLREC-26SEP27LVNO-NODVELE14-3 (Devaughn Vele). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.447 on KXNFLREC-26SEP27LVNO-LVAJEANTY2-3 (Ashton Jeanty). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLREC-26SEP27LVNO-NODVELE14-2 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_LV_NO.md`_


---

## LA @ DEN — `2026_03_LA_DEN`

- kickoff: 2026-09-28T00:20:00+00:00 (1857 minutes away) · state **PREGAME**
- venue: Empower Field at Mile High · roof outdoors · surface grass
- markets: 704 listed across 16 families — 362 supported, 286 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 2.12 | 1.47 |
| total | 44.44 | 44.01 |
| score | DEN 21.2 – LA 23.3 | DEN 21.3 – LA 22.7 |
| win prob DEN | 45.5% | 45.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 1.09 / total 23.07 · **2H** spread 0.67 / total 22.00 · **1Q** spread 0.24 / total 8.00 · **2Q** spread -0.06 / total 13.28 · **3Q** spread -0.05 / total 8.32 · **4Q** spread -0.24 / total 12.56

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (5)**

- Jonah Coleman (RB, DEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Ronnie Rivers (RB, LA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Frank Crum (OT, DEN) — Injured Reserve [single_source] — ruled out
- Nick Gargiulo (G, DEN) — Out [high] — ruled out
- Jonathon Cooper (LB, DEN) — Out [high] — ruled out

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Colby Parkinson (TE, LA) — Questionable [single_source]
- Marvin Mims Jr. (WR, DEN) — Questionable [single_source]
- Puka Nacua (WR, LA) — Doubtful [single_source]
- Kamren Kinchens (S, LA) — Doubtful [single_source]

### WEATHER

- Mostly Cloudy · 80°F · wind 10 mph SSE · precip 3%
- forecast vintage 2026-09-26T17:10:37+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 50 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bo Nix | DEN | attempts | 34.3 | 34.0 | 29.0 | 40.0 | 20.0 | 48.0 | 34.1 | 33.0 | 34.3 | 34.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| J.K. Dobbins | DEN | carries | 10.8 | 10.0 | 6.0 | 15.0 | 2.0 | 22.0 | 12.3 | 12.0 | 10.8 | 10.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bo Nix | DEN | carries | 4.7 | 4.0 | 2.0 | 6.0 | 1.0 | 11.0 | 4.8 | 5.0 | 4.7 | 4.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bo Nix | DEN | completions | 21.3 | 21.0 | 18.0 | 25.0 | 12.0 | 31.0 | 21.3 | 21.0 | 21.3 | 21.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bo Nix | DEN | passing_tds | 1.4 | 1.0 | 1.0 | 2.0 | 0.0 | 3.0 | 1.4 | 1.0 | 1.4 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Bo Nix | DEN | passing_yards | 227.4 | 223.0 | 174.0 | 276.0 | 107.0 | 365.0 | 216.0 | 210.0 | 216.0 | 212.0 | 0.00 | 0.97 | 9 | PRICED |
| Jaylen Waddle | DEN | receiving_yards | 52.7 | 43.0 | 19.0 | 76.0 | 0.0 | 140.0 | 62.8 | 56.0 | 62.8 | 51.0 | 0.00 | 0.97 | 11 | PRICED |
| Courtland Sutton | DEN | receiving_yards | 38.7 | 29.0 | 11.0 | 56.0 | 0.0 | 112.0 | 42.8 | 35.0 | 42.8 | 33.0 | 0.00 | 0.97 | 10 | PRICED |

_8 of 50 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 50 of 84 listed player/stat groups simulated and exposed, 34 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26SEP27LARDEN-LARTFERGUSON18-2` | Terrance Ferguson | 2.0 | 0.90 | 0.91 | 0.27 | -0.622 |
| `KXNFLRECYDS-26SEP27LARDEN-LARTFERGUSON18-25` | Terrance Ferguson | 25.0 | 0.78 | 0.80 | 0.16 | -0.615 |
| `KXNFLREC-26SEP27LARDEN-LARTFERGUSON18-3` | Terrance Ferguson | 3.0 | 0.76 | 0.77 | 0.16 | -0.596 |
| `KXNFLRECYDS-26SEP27LARDEN-LARTFERGUSON18-40` | Terrance Ferguson | 40.0 | 0.61 | 0.62 | 0.07 | -0.544 |
| `KXNFLREC-26SEP27LARDEN-LARTFERGUSON18-4` | Terrance Ferguson | 4.0 | 0.60 | 0.61 | 0.10 | -0.499 |
| `KXNFLREC-26SEP27LARDEN-LARDADAMS17-5` | Davante Adams | 5.0 | 0.68 | 0.69 | 0.19 | -0.489 |

_Ranked 355 tradable markets; 7 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Jonah Coleman (RB, DEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Ronnie Rivers (RB, LA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Marvin Mims Jr. (WR), Colby Parkinson (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLPASSYDS-26SEP27LARDEN-DENBNIX10-350 moved -0.145 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by -0.622 on KXNFLREC-26SEP27LARDEN-LARTFERGUSON18-2 (Terrance Ferguson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.615 on KXNFLRECYDS-26SEP27LARDEN-LARTFERGUSON18-25 (Terrance Ferguson). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLREC-26SEP27LARDEN-LARTFERGUSON18-2 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_LA_DEN.md`_


---

## PHI @ CHI — `2026_03_PHI_CHI`

- kickoff: 2026-09-29T00:15:00+00:00 (3292 minutes away) · state **PREGAME**
- venue: Soldier Field · roof outdoors · surface grass
- markets: 658 listed across 15 families — 335 supported, 267 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 4.25 | 5.08 |
| total | 41.61 | 41.97 |
| score | CHI 18.7 – PHI 22.9 | CHI 18.4 – PHI 23.5 |
| win prob CHI | 31.5% | 31.3% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

Period market-implied: **1H** spread 2.71 / total 20.89 · **2H** spread 2.38 / total 20.74 · **1Q** spread 0.44 / total 7.77 · **2Q** spread 1.33 / total 12.61 · **3Q** spread 0.82 / total 7.86 · **4Q** spread 0.61 / total 11.60

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Landon Dickerson (G, PHI) — Injured Reserve [high] — ruled out
- Anthony Johnson Jr. (S, CHI) — Injured Reserve [single_source] — ruled out
- Noah Sewell (LB, CHI) — Out [high] — ruled out
- Shemar Turner (DT, CHI) — Out [high] — ruled out

**Questionable / Doubtful (10)** — resolves at the inactive release, T−90m

- Caleb Williams (QB, CHI) — Doubtful [high]
- Tyson Bagent (QB, CHI) — Questionable [high]
- Dallas Goedert (TE, PHI) — Doubtful [high]
- DeVonta Smith (WR, PHI) — Questionable [high]
- Hollywood Brown (WR, PHI) — Questionable [single_source]
- Tank Bigsby (RB, PHI) — Questionable [high]
- Will Shipley (RB, PHI) — Questionable [high]
- Cairo Santos (PK, CHI) — Questionable [high]

### WEATHER

- Mostly Clear · 65°F · wind 5 mph NE · precip 0%
- forecast vintage 2026-09-26T17:10:39+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

**This is the current projection system (sim-1.x, run `20260926T132005Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 47 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D'Andre Swift | CHI | carries | 13.6 | 13.0 | 8.0 | 18.0 | 3.0 | 27.0 | 14.7 | 14.0 | 13.6 | 13.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Kyle Monangai | CHI | carries | 8.3 | 7.0 | 4.0 | 12.0 | 0.0 | 20.0 | 10.4 | 9.0 | 8.3 | 7.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Rome Odunze | CHI | receiving_yards | 44.4 | 34.0 | 13.0 | 66.0 | 0.0 | 125.0 | 31.3 | 24.0 | 31.3 | 24.0 | 0.00 | 0.97 | 8 | PRICED |
| Luther Burden III | CHI | receiving_yards | 41.1 | 33.0 | 13.0 | 60.0 | 0.0 | 113.0 | 38.4 | 31.0 | 38.4 | 31.0 | 0.00 | 0.98 | 8 | PRICED |
| Colston Loveland | CHI | receiving_yards | 39.8 | 32.0 | 13.0 | 58.0 | 0.0 | 109.0 | 38.7 | 31.0 | 38.7 | 31.0 | 0.00 | 0.98 | 9 | PRICED |
| Kalif Raymond | CHI | receiving_yards | 27.4 | 19.0 | 5.0 | 41.0 | 0.0 | 85.0 | 28.9 | 23.0 | 28.9 | 20.0 | 0.00 | 0.97 | 7 | PRICED |
| D'Andre Swift | CHI | receiving_yards | 16.1 | 10.0 | 0.0 | 24.0 | 0.0 | 56.0 | 15.5 | 10.0 | 15.5 | 9.0 | 0.00 | 0.97 | 4 | PRICED |
| Luther Burden III | CHI | receptions | 3.4 | 3.0 | 1.0 | 5.0 | 0.0 | 8.0 | 3.5 | 3.0 | 3.5 | 3.0 | 0.00 | 0.98 | 8 | PRICED |

_8 of 47 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 47 of 79 listed player/stat groups simulated and exposed, 32 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLRSHATT-26SEP28PHICHI-PHIJHURTS1-4` | Jalen Hurts | 4.0 | 0.81 | 0.81 | 0.36 | -0.449 |
| `KXNFLRSHATT-26SEP28PHICHI-CHIDSWIFT4-12` | D'Andre Swift | 12.0 | 0.72 | 0.74 | 0.31 | -0.412 |
| `KXNFLRECYDS-26SEP28PHICHI-PHIDSMITH6-50` | DeVonta Smith | 50.0 | 0.70 | 0.73 | 0.29 | -0.402 |
| `KXNFLRECYDS-26SEP28PHICHI-PHIDSMITH6-60` | DeVonta Smith | 60.0 | 0.61 | 0.64 | 0.21 | -0.401 |
| `KXNFLRECYDS-26SEP28PHICHI-PHIDSMITH6-40` | DeVonta Smith | 40.0 | 0.79 | 0.82 | 0.39 | -0.398 |
| `KXNFLREC-26SEP28PHICHI-PHIMLEMON9-2` | Makai Lemon | 2.0 | 0.70 | 0.74 | 0.32 | -0.384 |

_Ranked 328 tradable markets; 7 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. 5 skill players are Questionable (Tyson Bagent (QB), DeVonta Smith (WR), Hollywood Brown (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
2. KXNFLGAME-26SEP28PHICHI-CHI moved -0.170 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
3. The model disagrees by -0.449 on KXNFLRSHATT-26SEP28PHICHI-PHIJHURTS1-4 (Jalen Hurts). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
4. The model disagrees by -0.412 on KXNFLRSHATT-26SEP28PHICHI-CHIDSWIFT4-12 (D'Andre Swift). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. KXNFLPASSYDS-26SEP28PHICHI-CHICKEENUM11-250 sits at a market price of 0.09 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_03_PHI_CHI.md`_


---

## HOW TO USE THIS PACKET

1. Handicap each game independently. The model's ranked disagreements are an input, not a shortlist.
2. For any thesis you form, check **BEST EXPRESSIONS** before choosing a contract — the largest disagreement is rarely the best payout for the risk.
3. Check **CORRELATION GROUPS** before sizing more than one position in a game.
4. Record every serious decision, including passes, via the recommendation ledger (`scripts/handicap/validate_recommendations.py`, then commit to the `handicap-data` branch).