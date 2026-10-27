# NFL HANDICAP PACKET — 2026 Week 8

- run id: `20261027T050325Z`  ·  packet sha: `c58c3593e272b3bc2b3b`
- built at: 2026-10-27T05:03:25.682854+00:00  (all timestamps UTC)
- ledger: `20261027T042733Z.shadow-0.4.0.observations.jsonl.gz`  ·  model: `shadow-0.4.0`
- context captures: ['20261027T015743Z', '20261027T042022Z']
- team-profile basis: **current_season**
- **REAL-MONEY STATUS: NOT VALIDATED -- this packet recommends nothing and authorises nothing**
- **SIMULATION FRESHNESS: SIM_CURRENT** — run `20261027T042733Z` (RUN_NFL_FROZEN_BUNDLE), lag 0.0m vs target <= 180.0m; the simulation priced this packet's own board

> This packet contains no recommendations. Every model-vs-market number is a *disagreement*, which is not an edge. The model has been shown redundant to the closing market on player props and behind it on game outcomes; it is here as structure and context, not as a superior forecast.

## SLATE SUMMARY

- games: **14**
- markets listed this slate: **1740**, model-supported: **1314**
- ledger support states (all weeks): `{'UNSUPPORTED_MODEL': 12138, 'UNSUPPORTED_RULES': 5537, 'UNSUPPORTED_GAME': 30, 'SUPPORTED': 1873, 'UNSUPPORTED_IDENTITY': 12, 'POST_KICKOFF_EXCLUDED': 78306}`

### FULL-BOARD COVERAGE

_RUN NFL examines every executable Kalshi contract for every requested unstarted NFL game. UNSUPPORTED_MODEL is a statement about one model, never a reason to hide a contract. Every listed contract terminates in exactly one analysis state, in one of four buckets: A validated model view, B coherent/Shadow research view, C manual handicap from the packet's own football and context data, D explicit PASS with a named reason._

| bucket | contracts | meaning |
|---|---|---|
| **A** | 1314 | validated/production model view available |
| **B** | 249 | coherent / Shadow research model view available |
| **C** | 165 | no automated pricing authority; handicap from the football and context data in this packet |
| **D** | 12 | cannot defensibly price -- explicit PASS / RESEARCH REQUIRED, with a reason |
| **-** | 0 | outside the pregame window (kickoff has passed) |
| **!** | 0 | INVARIANT VIOLATION -- a listed contract with no analysis state |

- listed: **1740** · executable books: **1599**
- incumbent priced: **1314** · coherent simulation: **0** · Shadow v2 research: **249**
- manual handicap required: **165** · research required: **4**
- rules blocked: **0** · identity blocked: **8** · non-football: **0**
- post-kickoff (stale): **0**
- **silently omitted: 0** — this must be 0.

| family / period | listed | executable | incumbent priced | coherent sim | shadow v2 | manual research | research required | rules blocked | identity blocked | non football | post kickoff | silently omitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TEAM_TOTAL/FULL | 377 | 375 | 377 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| SPREAD/FULL | 356 | 356 | 356 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| PLAYER_STAT/FULL | 317 | 271 | 283 | 0 | 0 | 26 | 0 | 0 | 8 | 0 | 0 | 0 |
| TEAM_TOTAL/1H | 280 | 253 | 0 | 0 | 240 | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| TOTAL/FULL | 266 | 266 | 266 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| GAME_WINNER/FULL | 28 | 28 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FIRST_TD_TEAM/FULL | 27 | 3 | 0 | 0 | 0 | 27 | 0 | 0 | 0 | 0 | 0 | 0 |
| FIRST_TD_SCORER/FULL | 26 | 26 | 0 | 0 | 0 | 26 | 0 | 0 | 0 | 0 | 0 | 0 |
| TEAM_STAT/FULL | 20 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 |
| RACE_TO_N/FULL | 15 | 3 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 0 |
| HALF_FULL_RESULT/1H | 9 | 9 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| WIN_MARGIN_BUCKET/FULL | 7 | 7 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE_N/FULL | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| GAME_EVENT/FULL | 4 | 2 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/1Q | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/2Q | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/3Q | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| BOTH_TEAMS_SCORE/4Q | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

_A Shadow v2 or coherent-simulation projection is RESEARCH. It is not validated, it is never mixed into the incumbent's probability or its disagreement ranking, and it reaches no recommendation, staking or preflight path._

**Skill players ruled OUT (40)**

- Carson Beck (QB, ARI) — Out · 2026_08_ARI_DAL
- Jalen Brooks (WR, ARI) — Out · 2026_08_ARI_DAL
- Jeremiyah Love (RB, ARI) — Out · 2026_08_ARI_DAL
- Tip Reiman (TE, ARI) — Out · 2026_08_ARI_DAL
- James Conner (RB, ARI) — Injured Reserve · 2026_08_ARI_DAL
- Emari Demercado (RB, DAL) — Out · 2026_08_ARI_DAL
- KaVontae Turpin (WR, DAL) — Out · 2026_08_ARI_DAL
- Brian Robinson Jr. (RB, ATL) — Out · 2026_08_ATL_TB
- Olamide Zaccheaus (WR, ATL) — Out · 2026_08_ATL_TB
- Beaux Collins (WR, ATL) — Injured Reserve · 2026_08_ATL_TB
- Emeka Egbuka (WR, TB) — Out · 2026_08_ATL_TB
- Lamar Jackson (QB, BAL) — Out · 2026_08_BAL_BUF
- Ben Skowronek (WR, PIT) — Out · 2026_08_CLE_PIT
- Anthony Gould (WR, IND) — Out · 2026_08_IND_JAX
- Tyler Warren (TE, IND) — Out · 2026_08_IND_JAX

**New or changed since the previous capture (5)** — the most decision-relevant section on the page

- DJ Giddens (RB, IND): **Active** (new record) · 2026_08_IND_JAX
- Saquon Barkley (RB, PHI): **Questionable** (was Active) · 2026_08_PHI_WAS
- Makai Lemon (WR, PHI): **Active** (new record) · 2026_08_PHI_WAS
- Tanner McKee (QB, PHI): **Active** (new record) · 2026_08_PHI_WAS
- Anthony Johnson Jr. (S, CHI): **Out** (was Injured Reserve) · 2026_08_CHI_SEA

**Largest market moves since first capture**

| ticker | game | family | move |
|---|---|---|---|
| `KXNFLFIRSTTD-26OCT29CARGB-NONE` | 2026_08_CAR_GB | FIRST_TD_SCORER | -0.370 |
| `KXNFLGAME-26NOV01TENCIN-CIN` | 2026_08_TEN_CIN | GAME_WINNER | +0.190 |
| `KXNFL1HTEAMTOTAL-26NOV01ARIDAL-DAL3` | 2026_08_ARI_DAL | TEAM_TOTAL | +0.140 |
| `KXNFL1HTEAMTOTAL-26NOV01KCDEN-DEN3` | 2026_08_KC_DEN | TEAM_TOTAL | +0.130 |
| `KXNFLGAME-26NOV01INDJAC-JAC` | 2026_08_IND_JAX | GAME_WINNER | +0.125 |
| `KXNFLGAME-26NOV01MINDET-DET` | 2026_08_MIN_DET | GAME_WINNER | +0.125 |
| `KXNFLTOTAL-26OCT29CARGB-46` | 2026_08_CAR_GB | TOTAL | +0.120 |
| `KXNFLGAME-26NOV01TENCIN-TEN` | 2026_08_TEN_CIN | GAME_WINNER | -0.120 |
| `KXNFLGAME-26NOV01NEMIA-MIA` | 2026_08_NE_MIA | GAME_WINNER | -0.120 |
| `KXNFLTEAMTOTAL-26NOV01NEMIA-NE4` | 2026_08_NE_MIA | TEAM_TOTAL | +0.120 |

**Largest model/market disagreements** — DISAGREEMENT ONLY, REQUIRES HANDICAP

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT29CARGB-GBSWILLIAMS83-2` | Savion Williams | 2.0 | 0.71 | 0.74 | 0.01 | -0.705 |
| `KXNFLRECYDS-26OCT29CARGB-GBSWILLIAMS83-10` | Savion Williams | 10.0 | 0.71 | 0.74 | 0.01 | -0.697 |
| `KXNFLRSHYDS-26OCT29CARGB-CARCHUBBARD30-40` | Chuba Hubbard | 40.0 | 0.83 | 0.85 | 0.22 | -0.618 |
| `KXNFLRSHATT-26OCT29CARGB-CARCHUBBARD30-13` | Chuba Hubbard | 13.0 | 0.74 | 0.77 | 0.14 | -0.603 |
| `KXNFLRSHYDS-26OCT29CARGB-CARCHUBBARD30-50` | Chuba Hubbard | 50.0 | 0.72 | 0.74 | 0.15 | -0.577 |
| `KXNFLRECYDS-26OCT29CARGB-GBSWILLIAMS83-20` | Savion Williams | 20.0 | 0.56 | 0.57 | 0.01 | -0.552 |
| `KXNFLRSHYDS-26OCT29CARGB-CARCHUBBARD30-60` | Chuba Hubbard | 60.0 | 0.61 | 0.63 | 0.10 | -0.516 |
| `KXNFLREC-26OCT29CARGB-GBTKRAFT85-4` | Tucker Kraft | 4.0 | 0.64 | 0.66 | 0.13 | -0.504 |
| `KXNFLREC-26OCT29CARGB-CARTMCMILLAN4-5` | Tetairoa McMillan | 5.0 | 0.60 | 0.63 | 0.11 | -0.495 |
| `KXNFLRECYDS-26OCT29CARGB-GBMGOLDEN0-60` | Matthew Golden | 60.0 | 0.55 | 0.55 | 0.06 | -0.484 |
| `KXNFLREC-26OCT29CARGB-GBCWATSON9-4` | Christian Watson | 4.0 | 0.66 | 0.68 | 0.17 | -0.484 |
| `KXNFLREC-26OCT29CARGB-GBSWILLIAMS83-3` | Savion Williams | 3.0 | 0.48 | 0.49 | 0.01 | -0.474 |

**Highest-liquidity markets**

- `KXNFLGAME-26NOV01TENCIN-CIN` (GAME_WINNER, 2026_08_TEN_CIN): volume 300991, OI 278208
- `KXNFLGAME-26NOV01MINDET-MIN` (GAME_WINNER, 2026_08_MIN_DET): volume 154002, OI 124769
- `KXNFLGAME-26NOV01TENCIN-TEN` (GAME_WINNER, 2026_08_TEN_CIN): volume 104638, OI 78874
- `KXNFLGAME-26OCT29CARGB-GB` (GAME_WINNER, 2026_08_CAR_GB): volume 99519, OI 88276
- `KXNFLGAME-26NOV02CHISEA-CHI` (GAME_WINNER, 2026_08_CHI_SEA): volume 81513, OI 67784
- `KXNFLTOTAL-26OCT29CARGB-47` (TOTAL, 2026_08_CAR_GB): volume 69879, OI 69833
- `KXNFLGAME-26OCT29CARGB-CAR` (GAME_WINNER, 2026_08_CAR_GB): volume 61523, OI 52048
- `KXNFLSPREAD-26NOV01MINDET-DET3` (SPREAD, 2026_08_MIN_DET): volume 51609, OI 51462

### GAME PRIORITY FOR HANDICAP

_Priority ranks where deeper review may be most useful. It is NOT a bet ranking and carries no expectation that these games contain value._

| # | game | score | why |
|---|---|---|---|
| 1 | 2026_08_PHI_WAS | 16.0 | 3 new/changed injury records; 6 skill players ruled out (role change); largest market move 0.100 |
| 2 | 2026_08_ATL_TB | 11.0 | 4 skill players ruled out (role change); forecast changed; largest market move 0.100 |
| 3 | 2026_08_IND_JAX | 10.5 | 1 new/changed injury records; 3 skill players ruled out (role change); largest market move 0.125 |
| 4 | 2026_08_ARI_DAL | 10.0 | 7 skill players ruled out (role change); largest market move 0.140 |
| 5 | 2026_08_LV_NYJ | 10.0 | 5 skill players ruled out (role change); largest market move 0.105 |
| 6 | 2026_08_CHI_SEA | 9.2 | 1 new/changed injury records; 5 skill players ruled out (role change); largest market move 0.030 |
| 7 | 2026_08_TEN_CIN | 8.5 | 3 skill players ruled out (role change); largest market move 0.190 |
| 8 | 2026_08_KC_DEN | 8.5 | 3 skill players ruled out (role change); largest market move 0.130 |
| 9 | 2026_08_CLE_PIT | 6.5 | 1 skill players ruled out (role change); forecast changed; largest market move 0.105 |
| 10 | 2026_08_CAR_GB | 5.5 | largest market move 0.370; raw incumbent disagreement 0.705 (NOT scored: unvalidated); 283 supported player-prop rungs |
| 11 | 2026_08_MIN_DET | 5.5 | 1 skill players ruled out (role change); largest market move 0.125 |
| 12 | 2026_08_BAL_BUF | 5.3 | 1 skill players ruled out (role change); largest market move 0.095 |
| 13 | 2026_08_LAC_LA | 5.1 | 1 skill players ruled out (role change); largest market move 0.090 |
| 14 | 2026_08_NE_MIA | 4.0 | largest market move 0.120 |

> Each game below is summarised. Full detail -- complete market board, every player ladder, all best-expression groups -- is in that game's own file under `games/`.


---

## CAR @ GB — `2026_08_CAR_GB`

- kickoff: 2026-10-30T00:15:00+00:00 (4032 minutes away) · state **PREGAME**
- venue: Lambeau Field · roof outdoors · surface grass
- markets: 526 listed across 14 families — 360 supported, 110 no model, 48 rules unresolved, 8 identity unresolved

**Data health**

- `MAPPING_UNKNOWN` (warn) — 8 player markets have an unresolved Kalshi->GSIS identity; they are shown but carry no model view
- `SETTLEMENT_SEMANTICS_UNRESOLVED` (warn) — 48 markets have unestablished settlement semantics

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.62 | -4.28 |
| total | 48.38 | 48.39 |
| score | GB 26.0 – CAR 22.4 | GB 26.3 – CAR 22.1 |
| win prob GB | 64.5% | 64.6% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.62 · total 48.38
- move `KXNFLTOTAL-26OCT29CARGB-46` +0.120
- move `KXNFLTOTAL-26OCT29CARGB-42` +0.115
- move `KXNFLTOTAL-26OCT29CARGB-39` +0.105
- move `KXNFLTOTAL-26OCT29CARGB-45` +0.100

**Game environment** (simulation, mean and middle 50%) — home margin 3.6 (-4.0–11.0) · total 49.6 (40.0–58.0) · P(one score) 52.1% · P(17+ blowout) 17.7% · P(total 10+ over centre) 23.5%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| GB | 63.3 (58.0–69.0) | 36.1 (31.0–41.0) | 23.8 (19.0–28.0) | 38.6 (33.0–44.0) | 0.610 (0.542–0.678) | 0.527 / 0.709 |
| CAR | 64.1 (58.0–70.0) | 36.4 (31.0–41.0) | 23.0 (18.0–28.0) | 40.4 (35.0–46.0) | 0.631 (0.566–0.698) | 0.524 / 0.699 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| GB | 00-0035700 | RB | 3.4 (1.0–5.0) | 11.7 (7.0–16.0) | 9.9% | 49.3% | MEDIUM |
| GB | 00-0039811 | RB | 2.4 (0.0–3.0) | 6.7 (3.0–10.0) | 6.8% | 28.2% | HIGH |
| GB | 00-0038124 | WR | 7.4 (4.0–10.0) | 0.1 (0.0–0.0) | 21.2% | 0.4% | HIGH |
| GB | 00-0040667 | WR | 5.8 (1.0–9.0) | 0.1 (0.0–0.0) | 16.8% | 0.6% | HIGH |
| CAR | 00-0036555 | RB | 3.7 (1.0–5.0) | 14.5 (10.0–19.0) | 11.0% | 63.1% | MEDIUM |
| CAR | 00-0040124 | WR | 8.3 (5.0–11.0) | 0.0 (0.0–0.0) | 24.4% | 0.2% | MEDIUM |
| CAR | 00-0040644 | RB | 1.1 (0.0–2.0) | 4.9 (1.0–7.0) | 3.3% | 21.4% | HIGH |
| CAR | 00-0039491 | WR | 4.9 (1.0–8.0) | 0.1 (0.0–0.0) | 14.4% | 0.2% | HIGH |

**Historical research tags** (8; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `DISAGREEMENT_RESEARCH_CANDIDATE` · H-20261001-B11 YES · A large incumbent player-model OVER view marks an underpriced YES · 7 market(s), e.g. KXNFLRSHYDS-26OCT29CARGB-GBJLOVE10-5, KXNFLRSHYDS-26OCT29CARGB-GBJLOVE10-10
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 26 market(s), e.g. KXNFLPASSINT-26OCT29CARGB-CARBYOUNG9-2, KXNFLPASSYDS-26OCT29CARGB-GBJLOVE10-300
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 24 market(s), e.g. KXNFLSPREAD-26OCT29CARGB-GB18, KXNFLSPREAD-26OCT29CARGB-GB14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLGAME-26OCT29CARGB-GB, KXNFLSPREAD-26OCT29CARGB-GB2
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 199 market(s), e.g. KXNFLFIRSTTD-26OCT29CARGB-CARTMCMILLAN4, KXNFLFIRSTTD-26OCT29CARGB-GBCWATSON9
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 28 market(s), e.g. KXNFLRECYDS-26OCT29CARGB-GBMGOLDEN0-25, KXNFLFG-26OCT29CARGB-CAR3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 28.6%  _(final margin within one score (8 points) either way; total within 10 of the centre 48.375 (median favourite-oriented margin +2, median total 48))_
2. favourite controls / normal scoring — 19.6%  _(GB (favourite) wins by more than one score; total within 10 of the centre 48.375 (median favourite-oriented margin +14, median total 48))_
3. competitive / high scoring — 12.0%  _(final margin within one score (8 points) either way; total 58.375+ (centre 48.375) (median favourite-oriented margin +2, median total 66))_
4. competitive / low scoring — 11.5%  _(final margin within one score (8 points) either way; total 38.375 or fewer (centre 48.375) (median favourite-oriented margin +2, median total 34))_
5. underdog controls / normal scoring — 7.8%  _(CAR (underdog) wins by more than one score; total within 10 of the centre 48.375 (median favourite-oriented margin -14, median total 49))_
   Other — 20.5%

Marginal events (overlapping): one_score 52.1% · blowout_17 17.7% · favorite_wins 63.8% · favorite_controls 32.8% · upset 36.0% · shootout 23.5% · low_scoring 20.6% · low_possession 6.4% · high_volume_passing 20.9% · run_heavy_control 11.4%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 6.60 mph, gusts 9.40, precip prob 10%, temp 53F, forecast retrieved 2026-10-27T04:20:22+00:00 (67.91 h before kickoff)._

**`KXNFLTD-26OCT29CARGB-GBMGOLDEN0-1`** Matthew Golden touchdowns 1
- MODEL / MARKET: football 24.9% · market 39.5% · reconciled 35.7%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 14.9% · failure mass 100.0% · win-contribution HHI 0.178
- THESIS DEPENDENCY with `KXNFLRECYDS-26OCT29CARGB-GBMGOLDEN0-40`: cash correlation 0.324 · joint cash 19.1% · Jaccard of winning rows 0.351 · shared failure 45.6%

**`KXNFLTD-26OCT29CARGB-GBJJACOBS8-1`** Josh Jacobs touchdowns 1
- MODEL / MARKET: football 45.4% · market 54.0% · reconciled 50.7%
- SCRIPT ROBUSTNESS: P50 mass 39.1% · P55 mass 39.1% · P60 mass 7.5% · major-script floor 29.4% · failure mass 60.9% · win-contribution HHI 0.179

**`KXNFLTD-26OCT29CARGB-CARTETIENNE23-1`** Trevor Etienne touchdowns 1
- MODEL / MARKET: football 14.8% · market 4.5% · reconciled 7.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 9.3% · failure mass 100.0% · win-contribution HHI 0.165

**`KXNFLTD-26OCT29CARGB-CARMEVANS84-1`** Mitchell Evans touchdowns 1
- MODEL / MARKET: football 9.3% · market 8.5% · reconciled 11.3%
- SCRIPT ROBUSTNESS: P50 mass 0.0% · P55 mass 0.0% · P60 mass 0.0% · major-script floor 5.8% · failure mass 100.0% · win-contribution HHI 0.171

_350 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 40 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (4)**

- Jacob Monk (C, GB) — Injured Reserve [high] — ruled out
- Taylor Moton (OT, CAR) — Injured Reserve [high] — ruled out
- Jaelan Phillips (LB, CAR) — Out [high] — ruled out
- Zaire Franklin (LB, GB) — Out [high] — ruled out

**Questionable / Doubtful (11)** — resolves at the inactive release, T−90m

- Jalen Coker (WR, CAR) — Questionable [high]
- Matthew Golden (WR, GB) — Questionable [high]
- Aaron Banks (G, GB) — Questionable [high]
- Damien Lewis (G, CAR) — Questionable [high]
- Sean Rhyan (G, GB) — Doubtful [conflicting]
- Torricelli Simpkins III (G, CAR) — Questionable [high]
- Travis Glover (OT, GB) — Questionable [single_source]
- Akayleb Evans (CB, CAR) — Questionable [high]

### WEATHER

- Mostly Clear · 60°F · wind 2 mph WNW · precip 1%
- forecast vintage 2026-10-27T04:20:23+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

> **TRUNCATED: 8 of 54 projection rows shown.** This is the compact slate summary. The complete table, with every row, is in this game's own file under `games/`.

| player | team | stat | football mean | football median (p50) | p25 | p75 | p05 | p95 | market mean | market median | reconciled mean | reconciled median | w | P(active) | rungs | support |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bryce Young | CAR | attempts | 35.0 | 35.0 | 30.0 | 40.0 | 21.0 | 49.0 | 35.8 | 35.0 | 35.0 | 35.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Chuba Hubbard | CAR | carries | 14.5 | 14.0 | 10.0 | 19.0 | 4.0 | 27.0 | 16.1 | 16.0 | 14.5 | 14.0 | -- | 0.98 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | completions | 21.4 | 21.0 | 18.0 | 25.0 | 12.0 | 31.0 | 21.7 | 21.0 | 21.4 | 21.0 | -- | 0.97 | 3 | FOOTBALL_ONLY_NO_RECONCILIATION |
| Bryce Young | CAR | passing_tds | 1.5 | 1.0 | 1.0 | 2.0 | 0.0 | 4.0 | 1.6 | 1.0 | 1.6 | 1.0 | 0.00 | 0.97 | 4 | PRICED |
| Bryce Young | CAR | passing_yards | 231.7 | 228.0 | 179.0 | 281.0 | 110.0 | 366.0 | 255.8 | 251.0 | 255.8 | 252.0 | 0.00 | 0.97 | 8 | PRICED |
| Tetairoa McMillan | CAR | receiving_yards | 66.3 | 57.0 | 29.0 | 94.0 | 0.0 | 159.0 | 77.9 | 71.0 | 77.8 | 67.0 | 0.00 | 0.98 | 13 | PRICED |
| Jalen Coker | CAR | receiving_yards | 37.6 | 27.0 | 0.0 | 59.0 | 0.0 | 118.0 | 65.8 | 59.0 | 65.4 | 47.0 | 0.00 | 0.78 | 13 | PRICED |
| Darren Waller | CAR | receiving_yards | 28.7 | 20.0 | 5.0 | 43.0 | 0.0 | 91.0 | 24.0 | 18.0 | 24.0 | 17.0 | 0.00 | 0.97 | 9 | PRICED |

_8 of 54 simulation player/stat projection rows rendered. GSIS and Kalshi ids for every row are in `packet.json` under `simulation.player_projections`. `w` is the reconciliation weight; at w = 0 the reconciled mean IS the market's._

_Simulation coverage: 54 of 80 listed player/stat groups simulated and exposed, 26 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLREC-26OCT29CARGB-GBSWILLIAMS83-2` | Savion Williams | 2.0 | 0.71 | 0.74 | 0.01 | -0.705 |
| `KXNFLRECYDS-26OCT29CARGB-GBSWILLIAMS83-10` | Savion Williams | 10.0 | 0.71 | 0.74 | 0.01 | -0.697 |
| `KXNFLRSHYDS-26OCT29CARGB-CARCHUBBARD30-40` | Chuba Hubbard | 40.0 | 0.83 | 0.85 | 0.22 | -0.618 |
| `KXNFLRSHATT-26OCT29CARGB-CARCHUBBARD30-13` | Chuba Hubbard | 13.0 | 0.74 | 0.77 | 0.14 | -0.603 |
| `KXNFLRSHYDS-26OCT29CARGB-CARCHUBBARD30-50` | Chuba Hubbard | 50.0 | 0.72 | 0.74 | 0.15 | -0.577 |
| `KXNFLRECYDS-26OCT29CARGB-GBSWILLIAMS83-20` | Savion Williams | 20.0 | 0.56 | 0.57 | 0.01 | -0.552 |

_Ranked 328 tradable markets; 32 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. 2 skill players are Questionable (Jalen Coker (WR), Matthew Golden (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
2. KXNFLFIRSTTD-26OCT29CARGB-NONE moved -0.370 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
3. The model disagrees by -0.705 on KXNFLREC-26OCT29CARGB-GBSWILLIAMS83-2 (Savion Williams). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
4. The model disagrees by -0.697 on KXNFLRECYDS-26OCT29CARGB-GBSWILLIAMS83-10 (Savion Williams). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. KXNFLRSHATT-26OCT29CARGB-GBMLLOYD32-3 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_CAR_GB.md`_


---

## ARI @ DAL — `2026_08_ARI_DAL`

- kickoff: 2026-11-01T18:00:00+00:00 (7977 minutes away) · state **PREGAME**
- venue: AT&T Stadium · roof  · surface matrixturf
- markets: 96 listed across 4 families — 76 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -6.00 | -5.92 |
| total | 55.00 | 53.87 |
| score | DAL 30.5 – ARI 24.5 | DAL 29.9 – ARI 24.0 |
| win prob DAL | 71.5% | 72.4% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -6.00 · total 55.00
- move `KXNFL1HTEAMTOTAL-26NOV01ARIDAL-DAL3` +0.140
- move `KXNFLTEAMTOTAL-26NOV01ARIDAL-DAL8` +0.110
- move `KXNFLTEAMTOTAL-26NOV01ARIDAL-DAL11` +0.110
- move `KXNFLTEAMTOTAL-26NOV01ARIDAL-ARI4` +0.090

**Game environment** (simulation, mean and middle 50%) — home margin 6.5 (-1.0–14.0) · total 55.1 (46.0–63.0) · P(one score) 48.8% · P(17+ blowout) 21.6% · P(total 10+ over centre) 22.5%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| DAL | 66.0 (60.0–72.0) | 36.1 (31.0–41.0) | 25.5 (20.0–30.0) | 39.4 (34.0–45.0) | 0.597 (0.529–0.668) | 0.519 / 0.697 |
| ARI | 64.0 (58.0–70.0) | 37.4 (32.0–42.0) | 22.8 (18.0–27.0) | 40.8 (35.0–46.0) | 0.638 (0.572–0.704) | 0.530 / 0.699 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| DAL | 00-0036997 | RB | 3.2 (1.0–5.0) | 19.2 (14.0–24.0) | 9.1% | 75.2% | MEDIUM |
| DAL | 00-0036358 | WR | 9.3 (6.0–12.0) | 0.3 (0.0–0.0) | 26.4% | 1.1% | MEDIUM |
| DAL | 00-0037247 | WR | 7.0 (4.0–10.0) | 0.1 (0.0–0.0) | 20.1% | 0.4% | HIGH |
| DAL | 00-0039410 | WR | 4.9 (2.0–7.0) | 0.1 (0.0–0.0) | 14.1% | 0.5% | HIGH |
| ARI | 00-0037263 | RB | 2.7 (1.0–4.0) | 8.9 (5.0–12.0) | 7.6% | 39.4% | MEDIUM |
| ARI | 00-0037744 | TE | 10.9 (7.0–14.0) | 0.0 (0.0–0.0) | 30.5% | 0.1% | MEDIUM |
| ARI | 00-0038559 | WR | 9.2 (6.0–12.0) | 1.0 (0.0–1.0) | 25.8% | 4.2% | MEDIUM |
| ARI | 00-0037157 | RB | 2.2 (0.0–3.0) | 6.6 (3.0–9.0) | 6.1% | 29.1% | HIGH |

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 1 market(s), e.g. KXNFLTOTAL-26NOV01ARIDAL-56
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 20 market(s), e.g. KXNFLGAME-26NOV01ARIDAL-ARI, KXNFLSPREAD-26NOV01ARIDAL-DAL18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLTOTAL-26NOV01ARIDAL-50, KXNFLSPREAD-26NOV01ARIDAL-DAL3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 18 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV01ARIDAL-ARI21, KXNFLSPREAD-26NOV01ARIDAL-ARI11
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 14 market(s), e.g. KXNFLTEAMTOTAL-26NOV01ARIDAL-DAL8, KXNFLTEAMTOTAL-26NOV01ARIDAL-DAL4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 27.8%  _(final margin within one score (8 points) either way; total within 10 of the centre 55 (median favourite-oriented margin +3, median total 53))_
2. favourite controls / normal scoring — 22.6%  _(DAL (favourite) wins by more than one score; total within 10 of the centre 55 (median favourite-oriented margin +17, median total 53))_
3. competitive / high scoring — 10.7%  _(final margin within one score (8 points) either way; total 65+ (centre 55) (median favourite-oriented margin +3, median total 71))_
4. competitive / low scoring — 10.2%  _(final margin within one score (8 points) either way; total 45 or fewer (centre 55) (median favourite-oriented margin +2, median total 41))_
5. favourite controls / low scoring — 9.0%  _(DAL (favourite) wins by more than one score; total 45 or fewer (centre 55) (median favourite-oriented margin +13, median total 40))_
   Other — 19.7%

Marginal events (overlapping): one_score 48.8% · blowout_17 21.6% · favorite_wins 71.9% · favorite_controls 40.0% · upset 28.0% · shootout 22.5% · low_scoring 21.3% · low_possession 3.3% · high_volume_passing 24.5% · run_heavy_control 14.9%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 8.10 mph, gusts 10.50, precip prob 4%, temp 81F, forecast retrieved 2026-10-27T04:20:22+00:00 (133.66 h before kickoff)._

**`KXNFLGAME-26NOV01ARIDAL-ARI`** GAME_WINNER  
- MODEL / MARKET: football 28.1% · market 29.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 11.2% · P55 mass 11.2% · P60 mass 11.2% · major-script floor 0.0% · failure mass 88.8% · win-contribution HHI 0.208
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ARIDAL-DAL`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.001 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ARIDAL-ARI2`: cash correlation 0.922 · joint cash 24.9% · Jaccard of winning rows 0.887 · shared failure 72.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ARIDAL-DAL6`: cash correlation -0.655 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 19.6%

**`KXNFLGAME-26NOV01ARIDAL-DAL`** GAME_WINNER  
- MODEL / MARKET: football 72.0% · market 71.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 88.8% · P55 mass 88.8% · P60 mass 78.6% · major-script floor 57.8% · failure mass 11.2% · win-contribution HHI 0.212
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ARIDAL-ARI`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.001 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ARIDAL-ARI2`: cash correlation -0.922 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.2%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ARIDAL-DAL6`: cash correlation 0.655 · joint cash 52.3% · Jaccard of winning rows 0.728 · shared failure 28.1%

**`KXNFLSPREAD-26NOV01ARIDAL-ARI2`** SPREAD margin 1.5
- MODEL / MARKET: football 24.9% · market 25.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 11.2% · P55 mass 11.2% · P60 mass 11.2% · major-script floor 0.0% · failure mass 88.8% · win-contribution HHI 0.208
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ARIDAL-DAL`: cash correlation -0.922 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.2%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ARIDAL-ARI`: cash correlation 0.922 · joint cash 24.9% · Jaccard of winning rows 0.887 · shared failure 72.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ARIDAL-DAL6`: cash correlation -0.603 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 22.8%

**`KXNFLSPREAD-26NOV01ARIDAL-DAL6`** SPREAD margin 5.5
- MODEL / MARKET: football 52.3% · market 51.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 40.0% · P55 mass 40.0% · P60 mass 40.0% · major-script floor 21.9% · failure mass 60.0% · win-contribution HHI 0.264
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ARIDAL-DAL`: cash correlation 0.655 · joint cash 52.3% · Jaccard of winning rows 0.728 · shared failure 28.1%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ARIDAL-ARI`: cash correlation -0.655 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 19.6%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ARIDAL-ARI2`: cash correlation -0.603 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 22.8%

_76 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (16)**

- Carson Beck (QB, ARI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Emari Demercado (RB, DAL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jalen Brooks (WR, ARI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- James Conner (RB, ARI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jeremiyah Love (RB, ARI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- KaVontae Turpin (WR, DAL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tip Reiman (TE, ARI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Drew Shelton (OT, DAL) — Out [single_source] — ruled out
- _...and 8 more (mostly non-skill positions); full list in the game file_

### WEATHER

- retractable roof (AT&T Stadium), open/closed not yet announced (nflverse leaves the roof blank until it is) -- the outside forecast is context only and is never flagged material
- Slight Chance Rain Showers · 80°F · wind 5 mph S · precip 21%
- forecast vintage 2026-10-27T04:20:27+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTOTAL-26NOV01ARIDAL-38` | TOTAL | 38.0 | 0.90 | 0.91 | 0.94 | +0.048 |
| `KXNFLTEAMTOTAL-26NOV01ARIDAL-ARI11` | TEAM_TOTAL | 11.0 | 0.91 | 0.93 | 0.95 | +0.045 |
| `KXNFLTEAMTOTAL-26NOV01ARIDAL-ARI18` | TEAM_TOTAL | 18.0 | 0.74 | 0.75 | 0.78 | +0.041 |
| `KXNFLTOTAL-26NOV01ARIDAL-44` | TOTAL | 44.0 | 0.79 | 0.80 | 0.83 | +0.041 |
| `KXNFLTOTAL-26NOV01ARIDAL-55` | TOTAL | 55.0 | 0.50 | 0.51 | 0.46 | -0.038 |
| `KXNFLTEAMTOTAL-26NOV01ARIDAL-ARI4` | TEAM_TOTAL | 4.0 | 0.96 | 0.97 | 1.00 | +0.037 |

_Ranked 76 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Carson Beck (QB, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Jalen Brooks (WR, ARI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFL1HTEAMTOTAL-26NOV01ARIDAL-DAL3 moved +0.140 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by +0.048 on KXNFLTOTAL-26NOV01ARIDAL-38 (TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by +0.045 on KXNFLTEAMTOTAL-26NOV01ARIDAL-ARI11 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTOTAL-26NOV01ARIDAL-38 sits at a market price of 0.90 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_ARI_DAL.md`_


---

## ATL @ TB — `2026_08_ATL_TB`

- kickoff: 2026-11-01T18:00:00+00:00 (7977 minutes away) · state **PREGAME**
- venue: Raymond James Stadium · roof outdoors · surface grass
- markets: 93 listed across 4 families — 73 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -2.21 | -1.32 |
| total | 46.71 | 47.01 |
| score | TB 24.5 – ATL 22.2 | TB 24.2 – ATL 22.8 |
| win prob TB | 54.5% | 54.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -2.21 · total 46.71
- move `KXNFLTEAMTOTAL-26NOV01ATLTB-ATL4` +0.100
- move `KXNFLTEAMTOTAL-26NOV01ATLTB-TB4` +0.095
- move `KXNFLGAME-26NOV01ATLTB-TB` +0.090
- move `KXNFLTEAMTOTAL-26NOV01ATLTB-ATL8` +0.085

**Game environment** (simulation, mean and middle 50%) — home margin 2.4 (-5.0–10.0) · total 47.5 (38.0–55.0) · P(one score) 52.9% · P(17+ blowout) 17.8% · P(total 10+ over centre) 23.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| TB | 63.7 (58.0–69.0) | 31.1 (26.0–36.0) | 26.5 (21.0–31.0) | 36.4 (31.0–41.0) | 0.571 (0.505–0.639) | 0.485 / 0.661 |
| ATL | 61.6 (56.0–67.0) | 32.3 (27.0–37.0) | 25.3 (20.0–30.0) | 35.6 (30.0–41.0) | 0.579 (0.513–0.645) | 0.480 / 0.649 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| TB | 00-0039361 | RB | 4.2 (2.0–6.0) | 16.5 (11.0–22.0) | 13.9% | 62.4% | MEDIUM |
| TB | 00-0033921 | WR | 7.4 (4.0–10.0) | 0.3 (0.0–0.0) | 24.7% | 1.2% | MEDIUM |
| TB | 00-0036919 | RB | 2.4 (0.0–4.0) | 4.4 (0.0–7.0) | 8.1% | 16.6% | HIGH |
| TB | 00-0038129 | TE | 5.3 (2.0–7.0) | 0.0 (0.0–0.0) | 17.5% | 0.0% | HIGH |
| ATL | 00-0038542 | RB | 5.3 (2.0–7.0) | 18.9 (14.0–24.0) | 17.0% | 74.7% | MEDIUM |
| ATL | 00-0037238 | WR | 6.9 (2.0–11.0) | 0.1 (0.0–0.0) | 22.3% | 0.4% | HIGH |
| ATL | 00-0036906 | RB | 1.3 (0.0–2.0) | 4.0 (1.0–6.0) | 4.2% | 15.8% | HIGH |
| ATL | 00-0036970 | TE | 5.1 (2.0–7.0) | 0.0 (0.0–0.0) | 16.4% | 0.0% | HIGH |

**Historical research tags** (4; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV01ATLTB-TB10, KXNFLTOTAL-26NOV01ATLTB-63
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLTOTAL-26NOV01ATLTB-42, KXNFLTOTAL-26NOV01ATLTB-43
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 19 market(s), e.g. KXNFLTEAMTOTAL-26NOV01ATLTB-ATL36, KXNFL1HTEAMTOTAL-26NOV01ATLTB-TB21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 11 market(s), e.g. KXNFLTOTAL-26NOV01ATLTB-24, KXNFL1HTEAMTOTAL-26NOV01ATLTB-ATL3

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.0%  _(final margin within one score (8 points) either way; total within 10 of the centre 46.7143 (median favourite-oriented margin +2, median total 46))_
2. favourite controls / normal scoring — 17.0%  _(TB (favourite) wins by more than one score; total within 10 of the centre 46.7143 (median favourite-oriented margin +13, median total 46))_
3. competitive / low scoring — 12.4%  _(final margin within one score (8 points) either way; total 36.7143 or fewer (centre 46.7143) (median favourite-oriented margin +2, median total 31))_
4. competitive / high scoring — 11.6%  _(final margin within one score (8 points) either way; total 56.7143+ (centre 46.7143) (median favourite-oriented margin +1, median total 64))_
5. underdog controls / normal scoring — 10.0%  _(ATL (underdog) wins by more than one score; total within 10 of the centre 46.7143 (median favourite-oriented margin -13, median total 47))_
   Other — 20.1%

Marginal events (overlapping): one_score 52.9% · blowout_17 17.8% · favorite_wins 59.9% · favorite_controls 29.0% · upset 39.9% · shootout 23.1% · low_scoring 20.9% · low_possession 10.2% · high_volume_passing 2.9% · run_heavy_control 16.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 10.60 mph, gusts 11.60, precip prob 5%, temp 85F, forecast retrieved 2026-10-27T04:20:22+00:00 (133.66 h before kickoff)._

**`KXNFLGAME-26NOV01ATLTB-ATL`** GAME_WINNER  
- MODEL / MARKET: football 40.0% · market 45.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 18.1% · P55 mass 18.1% · P60 mass 18.1% · major-script floor 0.0% · failure mass 81.9% · win-contribution HHI 0.204
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ATLTB-TB`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ATLTB-ATL2`: cash correlation 0.941 · joint cash 37.0% · Jaccard of winning rows 0.927 · shared failure 60.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ATLTB-TB3`: cash correlation -0.833 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 9.1%

**`KXNFLGAME-26NOV01ATLTB-TB`** GAME_WINNER  
- MODEL / MARKET: football 60.0% · market 54.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 81.9% · P55 mass 81.9% · P60 mass 41.3% · major-script floor 57.0% · failure mass 18.1% · win-contribution HHI 0.209
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ATLTB-ATL`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ATLTB-ATL2`: cash correlation -0.941 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 2.9%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ATLTB-TB3`: cash correlation 0.833 · joint cash 51.0% · Jaccard of winning rows 0.849 · shared failure 40.0%

**`KXNFLSPREAD-26NOV01ATLTB-ATL2`** SPREAD margin 1.5
- MODEL / MARKET: football 37.1% · market 43.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 18.1% · P55 mass 18.1% · P60 mass 18.1% · major-script floor 0.0% · failure mass 81.9% · win-contribution HHI 0.197
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ATLTB-ATL`: cash correlation 0.941 · joint cash 37.0% · Jaccard of winning rows 0.927 · shared failure 60.0%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ATLTB-TB`: cash correlation -0.941 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 2.9%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ATLTB-TB3`: cash correlation -0.782 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 12.0%

**`KXNFLSPREAD-26NOV01ATLTB-TB3`** SPREAD margin 2.5
- MODEL / MARKET: football 51.0% · market 49.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 29.0% · P55 mass 29.0% · P60 mass 29.0% · major-script floor 40.2% · failure mass 71.0% · win-contribution HHI 0.216
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ATLTB-ATL`: cash correlation -0.833 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 9.1%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01ATLTB-TB`: cash correlation 0.833 · joint cash 51.0% · Jaccard of winning rows 0.849 · shared failure 40.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01ATLTB-ATL2`: cash correlation -0.782 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 12.0%

_73 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (11)**

- Beaux Collins (WR, ATL) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Brian Robinson Jr. (RB, ATL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Emeka Egbuka (WR, TB) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Olamide Zaccheaus (WR, ATL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Luke Goedeke (OT, TB) — Out [high] — ruled out
- Michael Jerrell (OT, ATL) — Injured Reserve [single_source] — ruled out
- Antoine Winfield Jr. (S, TB) — Out [high] — ruled out
- Avieon Terrell (CB, ATL) — Out [high] — ruled out
- _...and 3 more (mostly non-skill positions); full list in the game file_

### WEATHER

- Chance Rain Showers · 84°F · wind 8 mph E · precip 25%
- forecast vintage 2026-10-27T04:21:33+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 84, 'wind': '8 mph', 'precipitation_probability': 17})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTEAMTOTAL-26NOV01ATLTB-ATL32` | TEAM_TOTAL | 32.0 | 0.15 | 0.16 | 0.20 | +0.050 |
| `KXNFLSPREAD-26NOV01ATLTB-TB3` | SPREAD | 2.5 | 0.49 | 0.50 | 0.44 | -0.046 |
| `KXNFLTEAMTOTAL-26NOV01ATLTB-ATL29` | TEAM_TOTAL | 29.0 | 0.24 | 0.25 | 0.28 | +0.036 |
| `KXNFLTEAMTOTAL-26NOV01ATLTB-TB4` | TEAM_TOTAL | 4.0 | 0.95 | 0.97 | 0.99 | +0.035 |
| `KXNFLTEAMTOTAL-26NOV01ATLTB-ATL4` | TEAM_TOTAL | 4.0 | 0.96 | 0.97 | 0.99 | +0.033 |
| `KXNFLTEAMTOTAL-26NOV01ATLTB-TB25` | TEAM_TOTAL | 25.0 | 0.45 | 0.46 | 0.48 | +0.032 |

_Ranked 73 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Brian Robinson Jr. (RB, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Olamide Zaccheaus (WR, ATL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
4. KXNFLTEAMTOTAL-26NOV01ATLTB-ATL4 moved +0.100 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by +0.050 on KXNFLTEAMTOTAL-26NOV01ATLTB-ATL32 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.046 on KXNFLSPREAD-26NOV01ATLTB-TB3 (SPREAD). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLTEAMTOTAL-26NOV01ATLTB-TB4 sits at a market price of 0.95 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_ATL_TB.md`_


---

## BAL @ BUF — `2026_08_BAL_BUF`

- kickoff: 2026-11-01T18:00:00+00:00 (7977 minutes away) · state **PREGAME**
- venue: Highmark Stadium · roof outdoors · surface a_turf
- markets: 92 listed across 4 families — 72 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.26 | -3.24 |
| total | 54.12 | 53.80 |
| score | BUF 28.7 – BAL 25.4 | BUF 28.5 – BAL 25.3 |
| win prob BUF | 63.5% | 61.6% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.26 · total 54.12
- move `KXNFLTEAMTOTAL-26NOV01BALBUF-BUF8` +0.095
- move `KXNFLTOTAL-26NOV01BALBUF-32` +0.090
- move `KXNFLTEAMTOTAL-26NOV01BALBUF-BUF15` +0.090
- move `KXNFLTOTAL-26NOV01BALBUF-65` -0.080

**Game environment** (simulation, mean and middle 50%) — home margin 3.5 (-4.0–11.0) · total 55.8 (46.0–64.0) · P(one score) 52.1% · P(17+ blowout) 17.8% · P(total 10+ over centre) 24.1%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| BUF | 63.8 (58.0–69.0) | 32.4 (27.0–37.0) | 25.0 (20.0–30.0) | 37.8 (32.0–43.0) | 0.593 (0.526–0.663) | 0.510 / 0.689 |
| BAL | 62.2 (56.0–68.0) | 31.6 (27.0–36.0) | 24.9 (20.0–29.0) | 36.6 (31.0–42.0) | 0.590 (0.524–0.657) | 0.486 / 0.658 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| BUF | 00-0037248 | RB | 2.8 (1.0–4.0) | 18.4 (13.0–23.0) | 9.2% | 73.6% | MEDIUM |
| BUF | 00-0034857 | QB | 0.3 (0.0–0.0) | 7.0 (4.0–9.0) | 0.9% | 10.9% | HIGH |
| BUF | 00-0037261 | WR | 6.2 (3.0–9.0) | 0.1 (0.0–0.0) | 20.1% | 0.5% | HIGH |
| BUF | 00-0035537 | RB | 2.8 (1.0–4.0) | 2.1 (0.0–3.0) | 9.2% | 8.2% | HIGH |
| BAL | 00-0032764 | RB | 1.7 (0.0–2.0) | 17.6 (13.0–22.0) | 5.4% | 70.6% | MEDIUM |
| BAL | 00-0039064 | WR | 8.1 (5.0–11.0) | 0.4 (0.0–0.0) | 26.3% | 1.5% | MEDIUM |
| BAL | 00-0034975 | RB | 2.6 (1.0–4.0) | 2.9 (0.0–4.0) | 8.4% | 11.7% | HIGH |
| BAL | 00-0035993 | QB | 0.6 (0.0–1.0) | 4.6 (3.0–6.0) | 2.0% | 4.5% | HIGH |

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 2 market(s), e.g. KXNFLTOTAL-26NOV01BALBUF-56, KXNFLTOTAL-26NOV01BALBUF-55
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV01BALBUF-BAL8, KXNFLSPREAD-26NOV01BALBUF-BAL6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLGAME-26NOV01BALBUF-BUF, KXNFLTEAMTOTAL-26NOV01BALBUF-BUF25
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 15 market(s), e.g. KXNFLSPREAD-26NOV01BALBUF-BAL15, KXNFLSPREAD-26NOV01BALBUF-BAL14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 14 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV01BALBUF-BAL3, KXNFLTEAMTOTAL-26NOV01BALBUF-BUF8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 28.8%  _(final margin within one score (8 points) either way; total within 10 of the centre 54.125 (median favourite-oriented margin +2, median total 54))_
2. favourite controls / normal scoring — 19.1%  _(BUF (favourite) wins by more than one score; total within 10 of the centre 54.125 (median favourite-oriented margin +14, median total 54))_
3. competitive / high scoring — 12.0%  _(final margin within one score (8 points) either way; total 64.125+ (centre 54.125) (median favourite-oriented margin +2, median total 72))_
4. competitive / low scoring — 11.3%  _(final margin within one score (8 points) either way; total 44.125 or fewer (centre 54.125) (median favourite-oriented margin +2, median total 40))_
5. underdog controls / normal scoring — 7.9%  _(BAL (underdog) wins by more than one score; total within 10 of the centre 54.125 (median favourite-oriented margin -14, median total 56))_
   Other — 21.0%

Marginal events (overlapping): one_score 52.1% · blowout_17 17.8% · favorite_wins 63.2% · favorite_controls 32.6% · upset 36.6% · shootout 24.1% · low_scoring 20.2% · low_possession 8.9% · high_volume_passing 3.4% · run_heavy_control 14.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 13.20 mph, gusts 22.60, precip prob 12%, temp 62F, forecast retrieved 2026-10-27T04:20:22+00:00 (133.66 h before kickoff)._

**`KXNFLGAME-26NOV01BALBUF-BAL`** GAME_WINNER  
- MODEL / MARKET: football 36.7% · market 36.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 15.3% · P55 mass 15.3% · P60 mass 15.3% · major-script floor 0.0% · failure mass 84.7% · win-contribution HHI 0.201
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01BALBUF-BUF`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01BALBUF-BAL2`: cash correlation 0.932 · joint cash 33.5% · Jaccard of winning rows 0.912 · shared failure 63.3%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01BALBUF-BUF4`: cash correlation -0.768 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 12.9%

**`KXNFLGAME-26NOV01BALBUF-BUF`** GAME_WINNER  
- MODEL / MARKET: football 63.3% · market 63.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 84.7% · P55 mass 73.4% · P60 mass 73.4% · major-script floor 54.2% · failure mass 15.3% · win-contribution HHI 0.211
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01BALBUF-BAL`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01BALBUF-BAL2`: cash correlation -0.932 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.2%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01BALBUF-BUF4`: cash correlation 0.768 · joint cash 50.4% · Jaccard of winning rows 0.796 · shared failure 36.7%

**`KXNFLSPREAD-26NOV01BALBUF-BAL2`** SPREAD margin 1.5
- MODEL / MARKET: football 33.5% · market 34.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 15.3% · P55 mass 15.3% · P60 mass 15.3% · major-script floor 0.0% · failure mass 84.7% · win-contribution HHI 0.197
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01BALBUF-BAL`: cash correlation 0.932 · joint cash 33.5% · Jaccard of winning rows 0.912 · shared failure 63.3%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01BALBUF-BUF`: cash correlation -0.932 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.2%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01BALBUF-BUF4`: cash correlation -0.715 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 16.2%

**`KXNFLSPREAD-26NOV01BALBUF-BUF4`** SPREAD margin 3.5
- MODEL / MARKET: football 50.4% · market 47.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 32.6% · P55 mass 32.6% · P60 mass 32.6% · major-script floor 32.8% · failure mass 67.4% · win-contribution HHI 0.229
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01BALBUF-BAL`: cash correlation -0.768 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 12.9%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01BALBUF-BUF`: cash correlation 0.768 · joint cash 50.4% · Jaccard of winning rows 0.796 · shared failure 36.7%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01BALBUF-BAL2`: cash correlation -0.715 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 16.2%

_72 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- Lamar Jackson (QB, BAL) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Broderick Washington Jr. (DT, BAL) — Out [high] — ruled out
- C.J. Gardner-Johnson (S, BUF) — Suspension [high] — ruled out
- Jaylinn Hawkins (S, BAL) — Out [single_source] — ruled out
- T.J. Tampa (CB, BAL) — Injured Reserve [single_source] — ruled out
- Tavius Robinson (LB, BAL) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- DJ Moore (WR, BUF) — Questionable [conflicting]
- Olaivavega Ioane (G, BAL) — Questionable [single_source]
- Ed Oliver (DT, BUF) — Questionable [conflicting]

### WEATHER

- Slight Chance Rain Showers · 65°F · wind 5 mph S · precip 24%
- forecast vintage 2026-10-27T04:20:24+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTOTAL-26NOV01BALBUF-44` | TOTAL | 44.0 | 0.77 | 0.79 | 0.84 | +0.069 |
| `KXNFLTOTAL-26NOV01BALBUF-41` | TOTAL | 41.0 | 0.84 | 0.86 | 0.90 | +0.063 |
| `KXNFLTOTAL-26NOV01BALBUF-38` | TOTAL | 38.0 | 0.89 | 0.91 | 0.95 | +0.061 |
| `KXNFLTEAMTOTAL-26NOV01BALBUF-BAL18` | TEAM_TOTAL | 18.0 | 0.78 | 0.79 | 0.83 | +0.059 |
| `KXNFLTOTAL-26NOV01BALBUF-47` | TOTAL | 47.0 | 0.70 | 0.72 | 0.75 | +0.053 |
| `KXNFLTEAMTOTAL-26NOV01BALBUF-BAL25` | TEAM_TOTAL | 25.0 | 0.50 | 0.52 | 0.55 | +0.052 |

_Ranked 71 tradable markets; 1 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Lamar Jackson (QB, BAL) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 1 skill players are Questionable (DJ Moore (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLTEAMTOTAL-26NOV01BALBUF-BUF8 moved +0.095 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by +0.069 on KXNFLTOTAL-26NOV01BALBUF-44 (TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by +0.063 on KXNFLTOTAL-26NOV01BALBUF-41 (TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTOTAL-26NOV01BALBUF-38 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_BAL_BUF.md`_


---

## CLE @ PIT — `2026_08_CLE_PIT`

- kickoff: 2026-11-01T18:00:00+00:00 (7977 minutes away) · state **PREGAME**
- venue: Acrisure Stadium · roof outdoors · surface grass
- markets: 93 listed across 4 families — 73 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.40 | -3.35 |
| total | 39.42 | 39.33 |
| score | PIT 21.4 – CLE 18.0 | PIT 21.3 – CLE 18.0 |
| win prob PIT | 63.5% | 61.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.40 · total 39.42
- move `KXNFLTOTAL-26NOV01CLEPIT-19` +0.105
- move `KXNFLTOTAL-26NOV01CLEPIT-22` +0.095
- move `KXNFLTEAMTOTAL-26NOV01CLEPIT-CLE25` -0.085
- move `KXNFLTEAMTOTAL-26NOV01CLEPIT-PIT4` +0.080

**Game environment** (simulation, mean and middle 50%) — home margin 3.4 (-4.0–11.0) · total 40.8 (32.0–49.0) · P(one score) 52.2% · P(17+ blowout) 17.4% · P(total 10+ over centre) 23.5%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| PIT | 62.6 (57.0–68.0) | 34.7 (29.0–40.0) | 23.2 (18.0–28.0) | 38.4 (33.0–44.0) | 0.615 (0.547–0.684) | 0.530 / 0.712 |
| CLE | 61.0 (55.0–67.0) | 30.7 (26.0–35.0) | 23.2 (18.0–28.0) | 37.1 (32.0–42.0) | 0.610 (0.545–0.676) | 0.503 / 0.680 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| PIT | 00-0037228 | RB | 4.5 (2.0–6.0) | 13.2 (8.0–18.0) | 13.8% | 56.9% | MEDIUM |
| PIT | 00-0036139 | RB | 3.7 (1.0–5.0) | 7.3 (3.0–10.0) | 11.3% | 31.2% | MEDIUM |
| PIT | 00-0035640 | WR | 7.7 (4.0–10.0) | 0.2 (0.0–0.0) | 23.4% | 0.7% | MEDIUM |
| PIT | 00-0041489 | WR | 5.6 (3.0–8.0) | 0.2 (0.0–0.0) | 17.1% | 0.9% | HIGH |
| CLE | 00-0040784 | RB | 2.6 (1.0–4.0) | 11.7 (7.0–16.0) | 8.9% | 50.6% | MEDIUM |
| CLE | 00-0040162 | RB | 2.6 (1.0–4.0) | 4.3 (1.0–6.0) | 8.9% | 18.5% | HIGH |
| CLE | 00-0041547 | WR | 5.4 (3.0–8.0) | 1.2 (0.0–1.0) | 18.3% | 5.1% | HIGH |
| CLE | 00-0033537 | QB | 0.1 (0.0–0.0) | 5.7 (3.0–7.0) | 0.4% | 7.7% | HIGH |

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 5 market(s), e.g. KXNFLSPREAD-26NOV01CLEPIT-CLE4, KXNFLSPREAD-26NOV01CLEPIT-CLE3
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 19 market(s), e.g. KXNFLSPREAD-26NOV01CLEPIT-PIT15, KXNFLSPREAD-26NOV01CLEPIT-PIT14
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLGAME-26NOV01CLEPIT-PIT, KXNFLTEAMTOTAL-26NOV01CLEPIT-CLE15
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 24 market(s), e.g. KXNFLSPREAD-26NOV01CLEPIT-CLE15, KXNFLTEAMTOTAL-26NOV01CLEPIT-CLE29
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 10 market(s), e.g. KXNFLTEAMTOTAL-26NOV01CLEPIT-PIT11, KXNFLTOTAL-26NOV01CLEPIT-25

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.5%  _(final margin within one score (8 points) either way; total within 10 of the centre 39.4167 (median favourite-oriented margin +2, median total 40))_
2. favourite controls / normal scoring — 19.2%  _(PIT (favourite) wins by more than one score; total within 10 of the centre 39.4167 (median favourite-oriented margin +14, median total 39))_
3. competitive / high scoring — 11.8%  _(final margin within one score (8 points) either way; total 49.4167+ (centre 39.4167) (median favourite-oriented margin +2, median total 57))_
4. competitive / low scoring — 10.9%  _(final margin within one score (8 points) either way; total 29.4167 or fewer (centre 39.4167) (median favourite-oriented margin +2, median total 24))_
5. underdog controls / normal scoring — 8.2%  _(CLE (underdog) wins by more than one score; total within 10 of the centre 39.4167 (median favourite-oriented margin -14, median total 41))_
   Other — 20.4%

Marginal events (overlapping): one_score 52.2% · blowout_17 17.4% · favorite_wins 63.0% · favorite_controls 32.4% · upset 36.8% · shootout 23.5% · low_scoring 19.7% · low_possession 14.1% · high_volume_passing 4.7% · run_heavy_control 10.1%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.90 mph, gusts 16.30, precip prob 24%, temp 54F, forecast retrieved 2026-10-27T04:20:22+00:00 (133.66 h before kickoff)._

**`KXNFLGAME-26NOV01CLEPIT-CLE`** GAME_WINNER  
- MODEL / MARKET: football 36.9% · market 36.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 15.4% · P55 mass 15.4% · P60 mass 15.4% · major-script floor 0.0% · failure mass 84.6% · win-contribution HHI 0.206
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01CLEPIT-PIT`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01CLEPIT-CLE2`: cash correlation 0.936 · joint cash 33.8% · Jaccard of winning rows 0.917 · shared failure 63.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01CLEPIT-PIT4`: cash correlation -0.765 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 13.1%

**`KXNFLGAME-26NOV01CLEPIT-PIT`** GAME_WINNER  
- MODEL / MARKET: football 63.1% · market 63.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 84.6% · P55 mass 84.6% · P60 mass 32.4% · major-script floor 56.8% · failure mass 15.4% · win-contribution HHI 0.215
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01CLEPIT-CLE`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01CLEPIT-CLE2`: cash correlation -0.936 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01CLEPIT-PIT4`: cash correlation 0.765 · joint cash 50.0% · Jaccard of winning rows 0.792 · shared failure 36.9%

**`KXNFLSPREAD-26NOV01CLEPIT-CLE2`** SPREAD margin 1.5
- MODEL / MARKET: football 33.8% · market 34.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 15.4% · P55 mass 15.4% · P60 mass 15.4% · major-script floor 0.0% · failure mass 84.6% · win-contribution HHI 0.202
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01CLEPIT-CLE`: cash correlation 0.936 · joint cash 33.8% · Jaccard of winning rows 0.917 · shared failure 63.1%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01CLEPIT-PIT`: cash correlation -0.936 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01CLEPIT-PIT4`: cash correlation -0.715 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 16.2%

**`KXNFLSPREAD-26NOV01CLEPIT-PIT4`** SPREAD margin 3.5
- MODEL / MARKET: football 50.0% · market 49.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 32.4% · P55 mass 32.4% · P60 mass 32.4% · major-script floor 32.4% · failure mass 67.6% · win-contribution HHI 0.233
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01CLEPIT-CLE`: cash correlation -0.765 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 13.1%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01CLEPIT-PIT`: cash correlation 0.765 · joint cash 50.0% · Jaccard of winning rows 0.792 · shared failure 36.9%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01CLEPIT-CLE2`: cash correlation -0.715 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 16.2%

_73 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (5)**

- Ben Skowronek (WR, PIT) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Teven Jenkins (G, CLE) — Injured Reserve [high] — ruled out
- Brandin Echols (CB, PIT) — Out [high] — ruled out
- Mike Hall Jr. (DT, CLE) — Out [high] — ruled out
- Sebastian Joseph-Day (DT, PIT) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Tytus Howard (OT, CLE) — Questionable [high]
- Myles Harden (CB, CLE) — Questionable [high]

### WEATHER

- Chance Rain Showers · 66°F · wind 8 mph SE · precip 45%
- forecast vintage 2026-10-27T04:21:32+00:00 · material: **False**
- **changed since previous capture** (was {'temperature_f': 66, 'wind': '6 mph', 'precipitation_probability': 32})

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTEAMTOTAL-26NOV01CLEPIT-CLE18` | TEAM_TOTAL | 18.0 | 0.48 | 0.50 | 0.53 | +0.047 |
| `KXNFLSPREAD-26NOV01CLEPIT-CLE8` | SPREAD | 7.5 | 0.15 | 0.17 | 0.19 | +0.043 |
| `KXNFLTOTAL-26NOV01CLEPIT-43` | TOTAL | 43.0 | 0.41 | 0.43 | 0.37 | -0.039 |
| `KXNFLTEAMTOTAL-26NOV01CLEPIT-CLE21` | TEAM_TOTAL | 21.0 | 0.35 | 0.37 | 0.39 | +0.038 |
| `KXNFLTEAMTOTAL-26NOV01CLEPIT-CLE32` | TEAM_TOTAL | 32.0 | 0.04 | 0.08 | 0.08 | +0.038 |
| `KXNFLSPREAD-26NOV01CLEPIT-PIT7` | SPREAD | 6.5 | 0.40 | 0.41 | 0.37 | -0.034 |

_Ranked 73 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Ben Skowronek (WR, PIT) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. The forecast changed since the previous capture but is not flagged material. Does the market appear to have reacted to it anyway?
3. KXNFLTOTAL-26NOV01CLEPIT-19 moved +0.105 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by +0.047 on KXNFLTEAMTOTAL-26NOV01CLEPIT-CLE18 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by +0.043 on KXNFLSPREAD-26NOV01CLEPIT-CLE8 (SPREAD). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTEAMTOTAL-26NOV01CLEPIT-CLE32 sits at a market price of 0.04 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_CLE_PIT.md`_


---

## IND @ JAX — `2026_08_IND_JAX`

- kickoff: 2026-11-01T18:00:00+00:00 (7977 minutes away) · state **PREGAME**
- venue: EverBank Stadium · roof outdoors · surface grass
- markets: 95 listed across 4 families — 75 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -8.17 | -8.03 |
| total | 47.30 | 46.96 |
| score | JAX 27.7 – IND 19.6 | JAX 27.5 – IND 19.5 |
| win prob JAX | 76.5% | 76.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -8.17 · total 47.30
- move `KXNFLGAME-26NOV01INDJAC-JAC` +0.125
- move `KXNFLGAME-26NOV01INDJAC-IND` -0.115
- move `KXNFLTEAMTOTAL-26NOV01INDJAC-JAC4` +0.100
- move `KXNFLTOTAL-26NOV01INDJAC-26` +0.100

**Game environment** (simulation, mean and middle 50%) — home margin 8.7 (2.0–16.0) · total 48.6 (39.0–57.0) · P(one score) 43.0% · P(17+ blowout) 25.1% · P(total 10+ over centre) 23.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| JAX | 63.5 (58.0–69.0) | 32.2 (27.0–37.0) | 26.6 (21.0–31.0) | 35.8 (30.0–41.0) | 0.564 (0.495–0.635) | 0.499 / 0.683 |
| IND | 62.0 (56.0–68.0) | 34.7 (30.0–39.0) | 23.3 (18.0–28.0) | 38.2 (33.0–43.0) | 0.618 (0.553–0.683) | 0.488 / 0.667 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| JAX | 00-0040719 | RB | 2.4 (0.0–4.0) | 14.7 (9.0–19.0) | 7.7% | 55.3% | MEDIUM |
| JAX | 00-0038611 | RB | 0.6 (0.0–1.0) | 8.4 (4.0–12.0) | 2.0% | 31.8% | HIGH |
| JAX | 00-0038606 | WR | 7.2 (4.0–10.0) | 0.3 (0.0–0.0) | 23.1% | 1.1% | HIGH |
| JAX | 00-0034960 | WR | 5.3 (2.0–7.0) | 0.2 (0.0–0.0) | 16.8% | 0.6% | HIGH |
| IND | 00-0036223 | RB | 3.7 (1.0–5.0) | 13.0 (8.0–17.0) | 11.2% | 55.9% | MEDIUM |
| IND | 00-0038997 | WR | 7.1 (4.0–10.0) | 0.2 (0.0–0.0) | 21.6% | 0.8% | HIGH |
| IND | 00-0030279 | WR | 6.6 (4.0–9.0) | 0.1 (0.0–0.0) | 20.1% | 0.3% | HIGH |
| IND | 00-0041125 | RB | 1.3 (0.0–2.0) | 4.6 (1.0–7.0) | 4.1% | 20.0% | HIGH |

**Historical research tags** (4; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 18 market(s), e.g. KXNFLGAME-26NOV01INDJAC-IND, KXNFLSPREAD-26NOV01INDJAC-JAC18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 6 market(s), e.g. KXNFLTEAMTOTAL-26NOV01INDJAC-IND15, KXNFLTOTAL-26NOV01INDJAC-44
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 25 market(s), e.g. KXNFLSPREAD-26NOV01INDJAC-IND8, KXNFLTOTAL-26NOV01INDJAC-68
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 12 market(s), e.g. KXNFLTEAMTOTAL-26NOV01INDJAC-JAC4, KXNFLTEAMTOTAL-26NOV01INDJAC-JAC8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 28.4%  _(JAX (favourite) wins by more than one score; total within 10 of the centre 47.3 (median favourite-oriented margin +16, median total 48))_
2. competitive / normal scoring — 24.0%  _(final margin within one score (8 points) either way; total within 10 of the centre 47.3 (median favourite-oriented margin +3, median total 47))_
3. favourite controls / high scoring — 11.9%  _(JAX (favourite) wins by more than one score; total 57.3+ (centre 47.3) (median favourite-oriented margin +17, median total 65))_
4. competitive / high scoring — 9.8%  _(final margin within one score (8 points) either way; total 57.3+ (centre 47.3) (median favourite-oriented margin +2, median total 66))_
5. favourite controls / low scoring — 9.7%  _(JAX (favourite) wins by more than one score; total 37.3 or fewer (centre 47.3) (median favourite-oriented margin +14, median total 33))_
   Other — 16.2%

Marginal events (overlapping): one_score 43.0% · blowout_17 25.1% · favorite_wins 78.3% · favorite_controls 50.0% · upset 21.6% · shootout 23.3% · low_scoring 20.6% · low_possession 9.8% · high_volume_passing 7.4% · run_heavy_control 17.5%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 9.30 mph, gusts 14.10, precip prob 22%, temp 83F, forecast retrieved 2026-10-27T01:57:43+00:00 (136.04 h before kickoff)._

**`KXNFLGAME-26NOV01INDJAC-IND`** GAME_WINNER  
- MODEL / MARKET: football 21.6% · market 22.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 7.0% · P55 mass 7.0% · P60 mass 7.0% · major-script floor 0.0% · failure mass 93.0% · win-contribution HHI 0.233
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01INDJAC-JAC`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01INDJAC-IND2`: cash correlation 0.958 · joint cash 20.2% · Jaccard of winning rows 0.933 · shared failure 78.4%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01INDJAC-JAC10`: cash correlation -0.477 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 33.2%

**`KXNFLGAME-26NOV01INDJAC-JAC`** GAME_WINNER  
- MODEL / MARKET: football 78.4% · market 76.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 93.0% · P55 mass 93.0% · P60 mass 93.0% · major-script floor 65.3% · failure mass 7.0% · win-contribution HHI 0.223
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01INDJAC-IND`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01INDJAC-IND2`: cash correlation -0.958 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 1.5%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01INDJAC-JAC10`: cash correlation 0.477 · joint cash 45.2% · Jaccard of winning rows 0.577 · shared failure 21.6%

**`KXNFLSPREAD-26NOV01INDJAC-IND2`** SPREAD margin 1.5
- MODEL / MARKET: football 20.2% · market 20.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 7.0% · P55 mass 7.0% · P60 mass 7.0% · major-script floor 0.0% · failure mass 93.0% · win-contribution HHI 0.224
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01INDJAC-IND`: cash correlation 0.958 · joint cash 20.2% · Jaccard of winning rows 0.933 · shared failure 78.4%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01INDJAC-JAC`: cash correlation -0.958 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 1.5%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01INDJAC-JAC10`: cash correlation -0.457 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 34.6%

**`KXNFLSPREAD-26NOV01INDJAC-JAC10`** SPREAD margin 9.5
- MODEL / MARKET: football 45.2% · market 47.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 50.0% · P55 mass 50.0% · P60 mass 50.0% · major-script floor 0.0% · failure mass 50.0% · win-contribution HHI 0.424
- THESIS DEPENDENCY with `KXNFLTEAMTOTAL-26NOV01INDJAC-JAC29`: cash correlation 0.503 · joint cash 35.0% · Jaccard of winning rows 0.584 · shared failure 40.0%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01INDJAC-IND`: cash correlation -0.477 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 33.2%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01INDJAC-JAC`: cash correlation 0.477 · joint cash 45.2% · Jaccard of winning rows 0.577 · shared failure 21.6%

_75 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (7)**

- Alec Pierce (WR, IND) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Anthony Gould (WR, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tyler Warren (TE, IND) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Anton Harrison (OT, JAX) — Injured Reserve [high] — ruled out
- Bryce Boettcher (LB, IND) — Out [high] — ruled out
- CJ Allen (LB, IND) — Out [high] — ruled out
- Sauce Gardner (CB, IND) — Out [high] — ruled out

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Antonio Johnson (S, JAX) — Questionable [high]
- Justin Walley (CB, IND) — Questionable [high]
- Montaric Brown (CB, JAX) — Questionable [conflicting]
- Ross Matiscik (LS, JAX) — Questionable [single_source]

### WEATHER

- Chance Showers And Thunderstorms · 78°F · wind 13 mph E · precip 36%
- forecast vintage 2026-10-27T04:20:29+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLSPREAD-26NOV01INDJAC-JAC14` | SPREAD | 13.5 | 0.35 | 0.37 | 0.30 | -0.059 |
| `KXNFLTEAMTOTAL-26NOV01INDJAC-JAC36` | TEAM_TOTAL | 36.0 | 0.22 | 0.23 | 0.16 | -0.057 |
| `KXNFLSPREAD-26NOV01INDJAC-JAC17` | SPREAD | 16.5 | 0.28 | 0.29 | 0.22 | -0.056 |
| `KXNFLTEAMTOTAL-26NOV01INDJAC-IND32` | TEAM_TOTAL | 32.0 | 0.07 | 0.10 | 0.11 | +0.049 |
| `KXNFLSPREAD-26NOV01INDJAC-JAC10` | SPREAD | 9.5 | 0.47 | 0.48 | 0.43 | -0.043 |
| `KXNFLSPREAD-26NOV01INDJAC-JAC24` | SPREAD | 23.5 | 0.14 | 0.15 | 0.10 | -0.042 |

_Ranked 75 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Anthony Gould (WR, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Tyler Warren (TE, IND) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLGAME-26NOV01INDJAC-JAC moved +0.125 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.059 on KXNFLSPREAD-26NOV01INDJAC-JAC14 (SPREAD). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by -0.057 on KXNFLTEAMTOTAL-26NOV01INDJAC-JAC36 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTEAMTOTAL-26NOV01INDJAC-IND32 sits at a market price of 0.07 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_IND_JAX.md`_


---

## LV @ NYJ — `2026_08_LV_NYJ`

- kickoff: 2026-11-01T18:00:00+00:00 (7977 minutes away) · state **PREGAME**
- venue: MetLife Stadium · roof outdoors · surface fieldturf
- markets: 93 listed across 4 families — 73 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 0.25 | 0.12 |
| total | 45.88 | 46.24 |
| score | NYJ 22.8 – LV 23.1 | NYJ 23.1 – LV 23.2 |
| win prob NYJ | 48.5% | 50.5% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 0.25 · total 45.88
- move `KXNFLTEAMTOTAL-26NOV01LVNYJ-LV4` +0.105
- move `KXNFLTEAMTOTAL-26NOV01LVNYJ-LV22` +0.105
- move `KXNFLTEAMTOTAL-26NOV01LVNYJ-NYJ21` +0.100
- move `KXNFLTOTAL-26NOV01LVNYJ-24` +0.095

**Game environment** (simulation, mean and middle 50%) — home margin -0.4 (-8.0–7.0) · total 46.7 (38.0–55.0) · P(one score) 55.2% · P(17+ blowout) 17.4% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| NYJ | 61.8 (56.0–67.0) | 31.2 (26.0–36.0) | 25.5 (21.0–30.0) | 35.5 (30.0–40.0) | 0.575 (0.509–0.643) | 0.480 / 0.654 |
| LV | 62.8 (57.0–69.0) | 34.0 (29.0–39.0) | 25.1 (20.0–30.0) | 36.9 (31.0–42.0) | 0.588 (0.521–0.654) | 0.497 / 0.673 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| NYJ | 00-0039794 | RB | 3.1 (1.0–4.0) | 18.5 (13.0–23.0) | 10.2% | 72.4% | MEDIUM |
| NYJ | 00-0037740 | WR | 6.2 (3.0–8.0) | 0.1 (0.0–0.0) | 20.6% | 0.3% | HIGH |
| NYJ | 00-0039890 | WR | 4.0 (2.0–6.0) | 0.1 (0.0–0.0) | 13.2% | 0.5% | HIGH |
| NYJ | 00-0039798 | RB | 1.2 (0.0–2.0) | 2.7 (0.0–4.0) | 4.1% | 10.5% | HIGH |
| LV | 00-0040122 | RB | 4.8 (2.0–7.0) | 14.2 (9.0–19.0) | 14.8% | 56.4% | MEDIUM |
| LV | 00-0040878 | RB | 1.0 (0.0–1.0) | 7.2 (3.0–10.0) | 3.1% | 28.8% | HIGH |
| LV | 00-0039338 | TE | 7.5 (4.0–10.0) | 0.0 (0.0–0.0) | 23.0% | 0.1% | HIGH |
| LV | 00-0038563 | WR | 5.9 (3.0–8.0) | 0.4 (0.0–0.0) | 18.1% | 1.4% | HIGH |

**Historical research tags** (4; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV01LVNYJ-NYJ7, KXNFLTEAMTOTAL-26NOV01LVNYJ-NYJ32
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 2 market(s), e.g. KXNFLTOTAL-26NOV01LVNYJ-42, KXNFLTEAMTOTAL-26NOV01LVNYJ-NYJ21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 21 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV01LVNYJ-LV24, KXNFLTEAMTOTAL-26NOV01LVNYJ-NYJ36
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 11 market(s), e.g. KXNFLTEAMTOTAL-26NOV01LVNYJ-LV8, KXNFLTEAMTOTAL-26NOV01LVNYJ-NYJ11

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 31.4%  _(final margin within one score (8 points) either way; total within 10 of the centre 45.875 (median favourite-oriented margin -0, median total 46))_
2. favourite controls / normal scoring — 13.3%  _(LV (favourite) wins by more than one score; total within 10 of the centre 45.875 (median favourite-oriented margin +13, median total 46))_
3. competitive / high scoring — 12.8%  _(final margin within one score (8 points) either way; total 55.875+ (centre 45.875) (median favourite-oriented margin +1, median total 62))_
4. underdog controls / normal scoring — 11.5%  _(NYJ (underdog) wins by more than one score; total within 10 of the centre 45.875 (median favourite-oriented margin -15, median total 44))_
5. competitive / low scoring — 11.1%  _(final margin within one score (8 points) either way; total 35.875 or fewer (centre 45.875) (median favourite-oriented margin +1, median total 31))_
   Other — 19.9%

Marginal events (overlapping): one_score 55.2% · blowout_17 17.4% · favorite_wins 51.8% · favorite_controls 23.7% · upset 47.9% · shootout 23.8% · low_scoring 20.0% · low_possession 11.7% · high_volume_passing 4.8% · run_heavy_control 13.9%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 9.50 mph, gusts 12.10, precip prob 3%, temp 62F, forecast retrieved 2026-10-27T04:20:22+00:00 (133.66 h before kickoff)._

**`KXNFLGAME-26NOV01LVNYJ-LV`** GAME_WINNER  
- MODEL / MARKET: football 51.9% · market 50.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 79.0% · P55 mass 23.7% · P60 mass 23.7% · major-script floor 0.0% · failure mass 21.0% · win-contribution HHI 0.206
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LVNYJ-NYJ`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LVNYJ-NYJ2`: cash correlation -0.923 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 4.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LVNYJ-LV2`: cash correlation 0.904 · joint cash 46.9% · Jaccard of winning rows 0.902 · shared failure 48.1%

**`KXNFLGAME-26NOV01LVNYJ-NYJ`** GAME_WINNER  
- MODEL / MARKET: football 48.1% · market 48.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 21.0% · P55 mass 21.0% · P60 mass 21.0% · major-script floor 0.0% · failure mass 79.0% · win-contribution HHI 0.212
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LVNYJ-LV`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LVNYJ-NYJ2`: cash correlation 0.923 · joint cash 44.0% · Jaccard of winning rows 0.916 · shared failure 51.9%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LVNYJ-LV2`: cash correlation -0.904 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 5.1%

**`KXNFLSPREAD-26NOV01LVNYJ-LV2`** SPREAD margin 1.5
- MODEL / MARKET: football 46.9% · market 47.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 23.7% · P55 mass 23.7% · P60 mass 23.7% · major-script floor 0.0% · failure mass 76.3% · win-contribution HHI 0.207
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LVNYJ-LV`: cash correlation 0.904 · joint cash 46.9% · Jaccard of winning rows 0.902 · shared failure 48.1%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LVNYJ-NYJ`: cash correlation -0.904 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 5.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LVNYJ-NYJ2`: cash correlation -0.833 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 9.1%

**`KXNFLSPREAD-26NOV01LVNYJ-NYJ2`** SPREAD margin 1.5
- MODEL / MARKET: football 44.0% · market 46.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 21.0% · P55 mass 21.0% · P60 mass 21.0% · major-script floor 0.0% · failure mass 79.0% · win-contribution HHI 0.212
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LVNYJ-LV`: cash correlation -0.923 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 4.0%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LVNYJ-NYJ`: cash correlation 0.923 · joint cash 44.0% · Jaccard of winning rows 0.916 · shared failure 51.9%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LVNYJ-LV2`: cash correlation -0.833 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 9.1%

_73 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Breece Hall (RB, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Carter Runyon (TE, LV) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Dont'e Thornton Jr. (WR, LV) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jack Bech (WR, LV) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Kene Nwangwu (RB, NYJ) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Dylan Parham (G, NYJ) — Out [high] — ruled out
- Max Mitchell (OT, NYJ) — Out [high] — ruled out
- Joseph Ossai (DE, NYJ) — Out [high] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Patrick Johnson (DE, LV) — Questionable [high]
- T'Vondre Sweat (DT, NYJ) — Questionable [high]

### WEATHER

- Mostly Cloudy · 67°F · wind 6 mph S · precip 5%
- forecast vintage 2026-10-27T04:21:31+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTEAMTOTAL-26NOV01LVNYJ-LV32` | TEAM_TOTAL | 32.0 | 0.16 | 0.17 | 0.21 | +0.051 |
| `KXNFLTEAMTOTAL-26NOV01LVNYJ-LV29` | TEAM_TOTAL | 29.0 | 0.24 | 0.25 | 0.28 | +0.043 |
| `KXNFLTEAMTOTAL-26NOV01LVNYJ-LV4` | TEAM_TOTAL | 4.0 | 0.96 | 0.97 | 0.99 | +0.028 |
| `KXNFLTEAMTOTAL-26NOV01LVNYJ-LV25` | TEAM_TOTAL | 25.0 | 0.41 | 0.42 | 0.43 | +0.028 |
| `KXNFLTEAMTOTAL-26NOV01LVNYJ-NYJ4` | TEAM_TOTAL | 4.0 | 0.96 | 0.97 | 0.99 | +0.028 |
| `KXNFLTEAMTOTAL-26NOV01LVNYJ-NYJ29` | TEAM_TOTAL | 29.0 | 0.24 | 0.25 | 0.27 | +0.027 |

_Ranked 73 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Carter Runyon (TE, LV) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Dont'e Thornton Jr. (WR, LV) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. KXNFLTEAMTOTAL-26NOV01LVNYJ-LV4 moved +0.105 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by +0.051 on KXNFLTEAMTOTAL-26NOV01LVNYJ-LV32 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by +0.043 on KXNFLTEAMTOTAL-26NOV01LVNYJ-LV29 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTEAMTOTAL-26NOV01LVNYJ-LV4 sits at a market price of 0.96 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_LV_NYJ.md`_


---

## MIN @ DET — `2026_08_MIN_DET`

- kickoff: 2026-11-01T18:00:00+00:00 (7977 minutes away) · state **PREGAME**
- venue: Ford Field · roof dome · surface fieldturf
- markets: 92 listed across 4 families — 72 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.31 | -3.40 |
| total | 46.43 | 46.24 |
| score | DET 24.9 – MIN 21.6 | DET 24.8 – MIN 21.4 |
| win prob DET | 62.5% | 62.3% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.31 · total 46.43
- move `KXNFLGAME-26NOV01MINDET-DET` +0.125
- move `KXNFLGAME-26NOV01MINDET-MIN` -0.115
- move `KXNFLTEAMTOTAL-26NOV01MINDET-MIN4` +0.100
- move `KXNFLTOTAL-26NOV01MINDET-26` +0.090

**Game environment** (simulation, mean and middle 50%) — home margin 3.6 (-4.0–11.0) · total 47.6 (38.0–56.0) · P(one score) 52.2% · P(17+ blowout) 17.5% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| DET | 64.3 (59.0–70.0) | 33.9 (29.0–39.0) | 25.7 (21.0–30.0) | 37.6 (32.0–43.0) | 0.586 (0.518–0.654) | 0.504 / 0.682 |
| MIN | 62.1 (56.0–68.0) | 31.1 (26.0–36.0) | 23.8 (19.0–28.0) | 37.7 (32.0–43.0) | 0.608 (0.542–0.675) | 0.503 / 0.675 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| DET | 00-0039139 | RB | 6.0 (3.0–8.0) | 21.1 (16.0–26.0) | 18.4% | 82.1% | LOW |
| DET | 00-0036963 | WR | 7.9 (3.0–12.0) | 0.3 (0.0–0.0) | 24.0% | 1.2% | HIGH |
| DET | 00-0037240 | WR | 6.3 (3.0–9.0) | 0.1 (0.0–0.0) | 19.1% | 0.5% | HIGH |
| DET | 00-0039065 | TE | 5.7 (3.0–8.0) | 0.0 (0.0–0.0) | 17.5% | 0.0% | HIGH |
| MIN | 00-0037525 | RB | 1.2 (0.0–2.0) | 11.1 (5.0–16.0) | 4.1% | 46.8% | HIGH |
| MIN | 00-0033293 | RB | 2.3 (0.0–4.0) | 9.4 (3.0–14.0) | 7.8% | 39.4% | HIGH |
| MIN | 00-0036322 | WR | 7.0 (4.0–9.0) | 0.2 (0.0–0.0) | 23.6% | 0.7% | HIGH |
| MIN | 00-0038994 | WR | 4.6 (2.0–7.0) | 0.6 (0.0–0.0) | 15.6% | 2.5% | HIGH |

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 1 market(s), e.g. KXNFLTEAMTOTAL-26NOV01MINDET-MIN29
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 22 market(s), e.g. KXNFLSPREAD-26NOV01MINDET-MIN7, KXNFLSPREAD-26NOV01MINDET-MIN5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLGAME-26NOV01MINDET-DET, KXNFLTEAMTOTAL-26NOV01MINDET-DET22
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 19 market(s), e.g. KXNFLTEAMTOTAL-26NOV01MINDET-DET36, KXNFLSPREAD-26NOV01MINDET-MIN15
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 10 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV01MINDET-DET3, KXNFLTEAMTOTAL-26NOV01MINDET-MIN4

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.1%  _(final margin within one score (8 points) either way; total within 10 of the centre 46.4286 (median favourite-oriented margin +2, median total 46))_
2. favourite controls / normal scoring — 19.3%  _(DET (favourite) wins by more than one score; total within 10 of the centre 46.4286 (median favourite-oriented margin +14, median total 46))_
3. competitive / high scoring — 11.9%  _(final margin within one score (8 points) either way; total 56.4286+ (centre 46.4286) (median favourite-oriented margin +2, median total 65))_
4. competitive / low scoring — 11.2%  _(final margin within one score (8 points) either way; total 36.4286 or fewer (centre 46.4286) (median favourite-oriented margin +2, median total 32))_
5. favourite controls / high scoring — 7.9%  _(DET (favourite) wins by more than one score; total 56.4286+ (centre 46.4286) (median favourite-oriented margin +17, median total 64))_
   Other — 20.6%

Marginal events (overlapping): one_score 52.2% · blowout_17 17.5% · favorite_wins 63.5% · favorite_controls 33.1% · upset 36.3% · shootout 23.8% · low_scoring 20.5% · low_possession 8.2% · high_volume_passing 4.4% · run_heavy_control 14.2%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 10.80 mph, gusts 26.20, precip prob 26%, temp 58F, forecast retrieved 2026-10-27T04:20:22+00:00 (133.66 h before kickoff)._

**`KXNFLGAME-26NOV01MINDET-DET`** GAME_WINNER  
- MODEL / MARKET: football 63.6% · market 62.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 85.3% · P55 mass 74.1% · P60 mass 33.1% · major-script floor 54.6% · failure mass 14.7% · win-contribution HHI 0.212
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01MINDET-MIN`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01MINDET-MIN2`: cash correlation -0.932 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.2%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01MINDET-DET4`: cash correlation 0.771 · joint cash 50.9% · Jaccard of winning rows 0.800 · shared failure 36.4%

**`KXNFLGAME-26NOV01MINDET-MIN`** GAME_WINNER  
- MODEL / MARKET: football 36.4% · market 38.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 14.7% · P55 mass 14.7% · P60 mass 14.7% · major-script floor 0.0% · failure mass 85.3% · win-contribution HHI 0.203
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01MINDET-DET`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01MINDET-MIN2`: cash correlation 0.932 · joint cash 33.1% · Jaccard of winning rows 0.911 · shared failure 63.6%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01MINDET-DET4`: cash correlation -0.771 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 12.7%

**`KXNFLSPREAD-26NOV01MINDET-DET4`** SPREAD margin 3.5
- MODEL / MARKET: football 50.9% · market 48.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 33.1% · P55 mass 33.1% · P60 mass 33.1% · major-script floor 32.4% · failure mass 66.9% · win-contribution HHI 0.229
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01MINDET-DET`: cash correlation 0.771 · joint cash 50.9% · Jaccard of winning rows 0.800 · shared failure 36.4%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01MINDET-MIN`: cash correlation -0.771 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 12.7%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01MINDET-MIN2`: cash correlation -0.717 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 16.0%

**`KXNFLSPREAD-26NOV01MINDET-MIN2`** SPREAD margin 1.5
- MODEL / MARKET: football 33.1% · market 35.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 14.7% · P55 mass 14.7% · P60 mass 14.7% · major-script floor 0.0% · failure mass 85.3% · win-contribution HHI 0.197
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01MINDET-DET`: cash correlation -0.932 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.2%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01MINDET-MIN`: cash correlation 0.932 · joint cash 33.1% · Jaccard of winning rows 0.911 · shared failure 63.6%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01MINDET-DET4`: cash correlation -0.717 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 16.0%

_72 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (5)**

- Tom Kennedy (WR, DET) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Ben Bartch (G, DET) — Injured Reserve [high] — ruled out
- Donovan Jackson (G, MIN) — Injured Reserve [high] — ruled out
- Devin White (LB, DET) — Injured Reserve [high] — ruled out
- Kerby Joseph (S, DET) — Out [high] — ruled out

**Questionable / Doubtful (3)** — resolves at the inactive release, T−90m

- Aaron Jones Sr. (RB, MIN) — Questionable [high]
- Amon-Ra St. Brown (WR, DET) — Questionable [high]
- Ennis Rakestraw Jr. (CB, DET) — Questionable [high]

### WEATHER

fixed-roof stadium (Ford Field) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTOTAL-26NOV01MINDET-50` | TOTAL | 50.0 | 0.40 | 0.41 | 0.37 | -0.033 |
| `KXNFLTEAMTOTAL-26NOV01MINDET-MIN4` | TEAM_TOTAL | 4.0 | 0.96 | 0.97 | 0.99 | +0.031 |
| `KXNFLTEAMTOTAL-26NOV01MINDET-DET4` | TEAM_TOTAL | 4.0 | 0.96 | 0.97 | 1.00 | +0.030 |
| `KXNFLSPREAD-26NOV01MINDET-DET3` | SPREAD | 2.5 | 0.58 | 0.59 | 0.56 | -0.030 |
| `KXNFLTEAMTOTAL-26NOV01MINDET-MIN11` | TEAM_TOTAL | 11.0 | 0.86 | 0.89 | 0.89 | +0.029 |
| `KXNFLTOTAL-26NOV01MINDET-53` | TOTAL | 53.0 | 0.32 | 0.33 | 0.30 | -0.022 |

_Ranked 72 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Tom Kennedy (WR, DET) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 2 skill players are Questionable (Amon-Ra St. Brown (WR), Aaron Jones Sr. (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLGAME-26NOV01MINDET-DET moved +0.125 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.033 on KXNFLTOTAL-26NOV01MINDET-50 (TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by +0.031 on KXNFLTEAMTOTAL-26NOV01MINDET-MIN4 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTEAMTOTAL-26NOV01MINDET-MIN4 sits at a market price of 0.96 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_MIN_DET.md`_


---

## TEN @ CIN — `2026_08_TEN_CIN`

- kickoff: 2026-11-01T18:00:00+00:00 (7977 minutes away) · state **PREGAME**
- venue: Paycor Stadium · roof outdoors · surface fieldturf
- markets: 94 listed across 4 families — 74 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -10.20 | -11.07 |
| total | 47.12 | 47.55 |
| score | CIN 28.7 – TEN 18.5 | CIN 29.3 – TEN 18.2 |
| win prob CIN | 82.5% | 82.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -10.20 · total 47.12
- move `KXNFLGAME-26NOV01TENCIN-CIN` +0.190
- move `KXNFLGAME-26NOV01TENCIN-TEN` -0.120
- move `KXNFLSPREAD-26NOV01TENCIN-CIN5` +0.100
- move `KXNFLTOTAL-26NOV01TENCIN-27` +0.100

**Game environment** (simulation, mean and middle 50%) — home margin 10.6 (3.0–18.0) · total 48.7 (40.0–57.0) · P(one score) 35.1% · P(17+ blowout) 31.0% · P(total 10+ over centre) 23.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| CIN | 63.5 (58.0–69.0) | 34.7 (29.0–40.0) | 24.4 (19.0–29.0) | 38.0 (32.0–43.0) | 0.598 (0.529–0.668) | 0.539 / 0.734 |
| TEN | 59.4 (54.0–65.0) | 32.3 (27.0–37.0) | 22.4 (18.0–27.0) | 36.7 (31.0–41.0) | 0.618 (0.555–0.683) | 0.480 / 0.661 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| CIN | 00-0038597 | RB | 4.0 (1.0–6.0) | 18.9 (14.0–24.0) | 12.1% | 77.5% | MEDIUM |
| CIN | 00-0036900 | WR | 8.7 (5.0–12.0) | 0.0 (0.0–0.0) | 25.9% | 0.2% | MEDIUM |
| CIN | 00-0036410 | WR | 7.0 (4.0–10.0) | 0.1 (0.0–0.0) | 20.9% | 0.4% | HIGH |
| CIN | 00-0036442 | QB | 0.1 (0.0–0.0) | 3.6 (2.0–5.0) | 0.4% | 5.1% | HIGH |
| TEN | 00-0035261 | RB | 2.5 (1.0–4.0) | 15.1 (10.0–20.0) | 8.1% | 67.4% | MEDIUM |
| TEN | 00-0041438 | WR | 7.5 (4.0–10.0) | 0.0 (0.0–0.0) | 24.6% | 0.1% | MEDIUM |
| TEN | 00-0036924 | RB | 2.1 (0.0–3.0) | 4.7 (1.0–7.0) | 6.7% | 21.1% | HIGH |
| TEN | 00-0038117 | WR | 6.3 (3.0–9.0) | 0.1 (0.0–0.0) | 20.5% | 0.5% | HIGH |

**Historical research tags** (4; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 15 market(s), e.g. KXNFLGAME-26NOV01TENCIN-TEN, KXNFLSPREAD-26NOV01TENCIN-TEN4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLSPREAD-26NOV01TENCIN-CIN7, KXNFLSPREAD-26NOV01TENCIN-CIN6
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 23 market(s), e.g. KXNFLSPREAD-26NOV01TENCIN-TEN4, KXNFLSPREAD-26NOV01TENCIN-TEN8
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 12 market(s), e.g. KXNFLTEAMTOTAL-26NOV01TENCIN-CIN15, KXNFLTEAMTOTAL-26NOV01TENCIN-CIN8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 33.2%  _(CIN (favourite) wins by more than one score; total within 10 of the centre 47.125 (median favourite-oriented margin +17, median total 47))_
2. competitive / normal scoring — 19.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 47.125 (median favourite-oriented margin +3, median total 47))_
3. favourite controls / high scoring — 14.1%  _(CIN (favourite) wins by more than one score; total 57.125+ (centre 47.125) (median favourite-oriented margin +17, median total 65))_
4. favourite controls / low scoring — 11.6%  _(CIN (favourite) wins by more than one score; total 37.125 or fewer (centre 47.125) (median favourite-oriented margin +15, median total 33))_
5. competitive / high scoring — 7.9%  _(final margin within one score (8 points) either way; total 57.125+ (centre 47.125) (median favourite-oriented margin +3, median total 63))_
   Other — 13.2%

Marginal events (overlapping): one_score 35.1% · blowout_17 31.0% · favorite_wins 81.8% · favorite_controls 59.0% · upset 18.0% · shootout 23.3% · low_scoring 20.3% · low_possession 16.1% · high_volume_passing 7.1% · run_heavy_control 13.3%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 8.20 mph, gusts 23.50, precip prob 54%, temp 59F, forecast retrieved 2026-10-27T04:20:22+00:00 (133.66 h before kickoff)._

**`KXNFLGAME-26NOV01TENCIN-CIN`** GAME_WINNER  
- MODEL / MARKET: football 81.9% · market 82.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 94.0% · P55 mass 94.0% · P60 mass 94.0% · major-script floor 66.4% · failure mass 6.0% · win-contribution HHI 0.247
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01TENCIN-TEN`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01TENCIN-TEN2`: cash correlation -0.915 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 2.5%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01TENCIN-CIN11`: cash correlation 0.472 · joint cash 50.1% · Jaccard of winning rows 0.612 · shared failure 18.1%

**`KXNFLGAME-26NOV01TENCIN-TEN`** GAME_WINNER  
- MODEL / MARKET: football 18.1% · market 17.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 6.0% · P55 mass 6.0% · P60 mass 6.0% · major-script floor 0.0% · failure mass 94.0% · win-contribution HHI 0.227
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01TENCIN-CIN`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01TENCIN-TEN2`: cash correlation 0.915 · joint cash 15.6% · Jaccard of winning rows 0.862 · shared failure 81.9%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01TENCIN-CIN11`: cash correlation -0.472 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 31.8%

**`KXNFLSPREAD-26NOV01TENCIN-CIN11`** SPREAD margin 10.5
- MODEL / MARKET: football 50.1% · market 48.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 59.0% · P55 mass 59.0% · P60 mass 59.0% · major-script floor 0.0% · failure mass 41.0% · win-contribution HHI 0.416
- THESIS DEPENDENCY with `KXNFLTEAMTOTAL-26NOV01TENCIN-CIN30`: cash correlation 0.499 · joint cash 37.5% · Jaccard of winning rows 0.599 · shared failure 37.5%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01TENCIN-CIN`: cash correlation 0.472 · joint cash 50.1% · Jaccard of winning rows 0.612 · shared failure 18.1%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01TENCIN-TEN`: cash correlation -0.472 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 31.8%

**`KXNFLSPREAD-26NOV01TENCIN-TEN2`** SPREAD margin 1.5
- MODEL / MARKET: football 15.6% · market 15.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 6.0% · P55 mass 6.0% · P60 mass 6.0% · major-script floor 0.0% · failure mass 94.0% · win-contribution HHI 0.202
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01TENCIN-CIN`: cash correlation -0.915 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 2.5%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01TENCIN-TEN`: cash correlation 0.915 · joint cash 15.6% · Jaccard of winning rows 0.862 · shared failure 81.9%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01TENCIN-CIN11`: cash correlation -0.431 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 34.3%

_74 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (6)**

- Calvin Ridley (WR, TEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tanner Hudson (TE, CIN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Tyjae Spears (RB, TEN) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Dorian Mausi (LB, TEN) — Injured Reserve [high] — ruled out
- Kyle Dugger (S, CIN) — Out [high] — ruled out
- Swayze Bozeman (LB, CIN) — Injured Reserve [high] — ruled out

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Erick All Jr. (TE, CIN) — Questionable [high]
- Tommy Townsend (P, TEN) — Questionable [high]

### WEATHER

- Chance Light Rain · 69°F · wind 6 mph S · precip 43%
- forecast vintage 2026-10-27T04:20:25+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTEAMTOTAL-26NOV01TENCIN-TEN18` | TEAM_TOTAL | 18.0 | 0.47 | 0.48 | 0.52 | +0.049 |
| `KXNFLTEAMTOTAL-26NOV01TENCIN-CIN32` | TEAM_TOTAL | 32.0 | 0.37 | 0.38 | 0.42 | +0.047 |
| `KXNFLTEAMTOTAL-26NOV01TENCIN-CIN29` | TEAM_TOTAL | 29.0 | 0.51 | 0.52 | 0.55 | +0.039 |
| `KXNFLSPREAD-26NOV01TENCIN-CIN11` | SPREAD | 10.5 | 0.48 | 0.49 | 0.52 | +0.036 |
| `KXNFLTEAMTOTAL-26NOV01TENCIN-TEN21` | TEAM_TOTAL | 21.0 | 0.35 | 0.37 | 0.39 | +0.036 |
| `KXNFLTEAMTOTAL-26NOV01TENCIN-CIN8` | TEAM_TOTAL | 8.0 | 0.96 | 0.97 | 1.00 | +0.034 |

_Ranked 74 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Tanner Hudson (TE, CIN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Calvin Ridley (WR, TEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Erick All Jr. (TE)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLGAME-26NOV01TENCIN-CIN moved +0.190 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by +0.049 on KXNFLTEAMTOTAL-26NOV01TENCIN-TEN18 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by +0.047 on KXNFLTEAMTOTAL-26NOV01TENCIN-CIN32 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLTEAMTOTAL-26NOV01TENCIN-CIN8 sits at a market price of 0.96 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_TEN_CIN.md`_


---

## LAC @ LA — `2026_08_LAC_LA`

- kickoff: 2026-11-01T21:05:00+00:00 (8162 minutes away) · state **PREGAME**
- venue: SoFi Stadium · roof dome · surface matrixturf
- markets: 94 listed across 4 families — 74 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -6.57 | -6.80 |
| total | 44.30 | 44.23 |
| score | LA 25.4 – LAC 18.9 | LA 25.5 – LAC 18.7 |
| win prob LA | 74.5% | 73.1% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -6.57 · total 44.30
- move `KXNFLGAME-26NOV01LACLAR-LAR` +0.090
- move `KXNFLSPREAD-26NOV01LACLAR-LAC2` +0.090
- move `KXNFLTEAMTOTAL-26NOV01LACLAR-LAR8` +0.090
- move `KXNFLGAME-26NOV01LACLAR-LAC` -0.080

**Game environment** (simulation, mean and middle 50%) — home margin 6.6 (-1.0–14.0) · total 45.8 (36.0–54.0) · P(one score) 48.7% · P(17+ blowout) 20.6% · P(total 10+ over centre) 23.9%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| LA | 64.9 (59.0–71.0) | 35.5 (30.0–41.0) | 26.0 (21.0–31.0) | 37.9 (32.0–43.0) | 0.584 (0.516–0.653) | 0.513 / 0.682 |
| LAC | 62.0 (56.0–68.0) | 30.8 (26.0–35.0) | 24.5 (20.0–29.0) | 37.0 (32.0–42.0) | 0.597 (0.532–0.663) | 0.487 / 0.654 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| LA | 00-0037840 | RB | 4.1 (2.0–6.0) | 13.3 (8.0–18.0) | 11.8% | 51.1% | MEDIUM |
| LA | 00-0039075 | WR | 11.6 (8.0–15.0) | 1.1 (0.0–1.0) | 33.8% | 4.2% | MEDIUM |
| LA | 00-0039738 | RB | 1.8 (0.0–3.0) | 9.1 (4.0–13.0) | 5.3% | 35.0% | HIGH |
| LA | 00-0033110 | TE | 4.7 (2.0–7.0) | 0.1 (0.0–0.0) | 13.7% | 0.3% | HIGH |
| LAC | 00-0040666 | RB | 2.4 (0.0–4.0) | 11.2 (6.0–15.0) | 8.0% | 45.7% | MEDIUM |
| LAC | 00-0039391 | RB | 1.9 (0.0–3.0) | 5.4 (2.0–8.0) | 6.5% | 22.1% | HIGH |
| LAC | 00-0038454 | RB | 2.6 (1.0–4.0) | 4.5 (1.0–7.0) | 8.7% | 18.4% | HIGH |
| LAC | 00-0036355 | QB | 0.2 (0.0–0.0) | 5.8 (3.0–7.0) | 0.8% | 7.7% | HIGH |

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 2 market(s), e.g. KXNFLSPREAD-26NOV01LACLAR-LAC3, KXNFLSPREAD-26NOV01LACLAR-LAC2
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLGAME-26NOV01LACLAR-LAC, KXNFLSPREAD-26NOV01LACLAR-LAR17
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLSPREAD-26NOV01LACLAR-LAR3, KXNFLTOTAL-26NOV01LACLAR-40
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 22 market(s), e.g. KXNFLSPREAD-26NOV01LACLAR-LAC11, KXNFLTEAMTOTAL-26NOV01LACLAR-LAR39
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 10 market(s), e.g. KXNFLTEAMTOTAL-26NOV01LACLAR-LAR4, KXNFLTEAMTOTAL-26NOV01LACLAR-LAR15

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 26.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 44.3 (median favourite-oriented margin +3, median total 44))_
2. favourite controls / normal scoring — 23.8%  _(LA (favourite) wins by more than one score; total within 10 of the centre 44.3 (median favourite-oriented margin +15, median total 44))_
3. competitive / high scoring — 11.0%  _(final margin within one score (8 points) either way; total 54.3+ (centre 44.3) (median favourite-oriented margin +3, median total 62))_
4. competitive / low scoring — 10.8%  _(final margin within one score (8 points) either way; total 34.3 or fewer (centre 44.3) (median favourite-oriented margin +3, median total 30))_
5. favourite controls / high scoring — 10.1%  _(LA (favourite) wins by more than one score; total 54.3+ (centre 44.3) (median favourite-oriented margin +16, median total 61))_
   Other — 17.4%

Marginal events (overlapping): one_score 48.7% · blowout_17 20.6% · favorite_wins 72.6% · favorite_controls 41.0% · upset 27.2% · shootout 23.9% · low_scoring 20.2% · low_possession 7.3% · high_volume_passing 6.4% · run_heavy_control 16.0%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 4.60 mph, gusts 2.70, precip prob 25%, temp 69F, forecast retrieved 2026-10-27T04:20:22+00:00 (136.74 h before kickoff)._

**`KXNFLGAME-26NOV01LACLAR-LAC`** GAME_WINNER  
- MODEL / MARKET: football 27.3% · market 26.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 10.3% · P55 mass 10.3% · P60 mass 10.3% · major-script floor 0.0% · failure mass 89.7% · win-contribution HHI 0.208
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LACLAR-LAR`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LACLAR-LAC2`: cash correlation 0.939 · joint cash 24.8% · Jaccard of winning rows 0.909 · shared failure 72.7%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LACLAR-LAR7`: cash correlation -0.613 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 22.8%

**`KXNFLGAME-26NOV01LACLAR-LAR`** GAME_WINNER  
- MODEL / MARKET: football 72.7% · market 74.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 89.7% · P55 mass 89.7% · P60 mass 89.7% · major-script floor 62.3% · failure mass 10.3% · win-contribution HHI 0.214
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LACLAR-LAC`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LACLAR-LAC2`: cash correlation -0.939 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 2.5%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LACLAR-LAR7`: cash correlation 0.613 · joint cash 49.9% · Jaccard of winning rows 0.687 · shared failure 27.3%

**`KXNFLSPREAD-26NOV01LACLAR-LAC2`** SPREAD margin 1.5
- MODEL / MARKET: football 24.8% · market 25.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 10.3% · P55 mass 10.3% · P60 mass 10.3% · major-script floor 0.0% · failure mass 89.7% · win-contribution HHI 0.205
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LACLAR-LAC`: cash correlation 0.939 · joint cash 24.8% · Jaccard of winning rows 0.909 · shared failure 72.7%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LACLAR-LAR`: cash correlation -0.939 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 2.5%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LACLAR-LAR7`: cash correlation -0.574 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 25.3%

**`KXNFLSPREAD-26NOV01LACLAR-LAR7`** SPREAD margin 6.5
- MODEL / MARKET: football 49.9% · market 50.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 41.0% · P55 mass 41.0% · P60 mass 41.0% · major-script floor 15.0% · failure mass 59.0% · win-contribution HHI 0.300
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LACLAR-LAC`: cash correlation -0.613 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 22.8%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01LACLAR-LAR`: cash correlation 0.613 · joint cash 49.9% · Jaccard of winning rows 0.687 · shared failure 27.3%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01LACLAR-LAC2`: cash correlation -0.574 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 25.3%

_74 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Terrance Ferguson (TE, LA) — Injured Reserve [single_source] — ruled out -- role redistributes to the depth chart behind him
- Alec Ingold (FB, LAC) — Injured Reserve [high] — ruled out
- Denzel Perryman (LB, LAC) — Injured Reserve [high] — ruled out
- Kobie Turner (DE, LA) — Injured Reserve [single_source] — ruled out
- Myles Garrett (DE, LA) — Injured Reserve [single_source] — ruled out
- Nate Landman (LB, LA) — Out [single_source] — ruled out
- Poona Ford (DT, LA) — Injured Reserve [single_source] — ruled out
- Trent McDuffie (CB, LA) — Out [single_source] — ruled out

**Questionable / Doubtful (9)** — resolves at the inactive release, T−90m

- Brenen Thompson (WR, LAC) — Questionable [high]
- Ladd McConkey (WR, LAC) — Questionable [conflicting]
- Tre' Harris (WR, LAC) — Questionable [conflicting]
- Joe Alt (OT, LAC) — Questionable [conflicting]
- Kayode Awosika (G, LAC) — Questionable [conflicting]
- Bud Dupree (LB, LAC) — Questionable [conflicting]
- Derwin James Jr. (S, LAC) — Questionable [conflicting]
- Donte Jackson (CB, LAC) — Questionable [conflicting]

### WEATHER

fixed-roof stadium (SoFi Stadium) -- weather is not a factor

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTEAMTOTAL-26NOV01LACLAR-LAC8` | TEAM_TOTAL | 8.0 | 0.92 | 0.95 | 0.86 | -0.053 |
| `KXNFLSPREAD-26NOV01LACLAR-LAC8` | SPREAD | 7.5 | 0.10 | 0.12 | 0.14 | +0.035 |
| `KXNFLTEAMTOTAL-26NOV01LACLAR-LAC21` | TEAM_TOTAL | 21.0 | 0.39 | 0.39 | 0.42 | +0.032 |
| `KXNFLSPREAD-26NOV01LACLAR-LAR4` | SPREAD | 3.5 | 0.59 | 0.60 | 0.62 | +0.032 |
| `KXNFLTEAMTOTAL-26NOV01LACLAR-LAR4` | TEAM_TOTAL | 4.0 | 0.97 | 0.99 | 1.00 | +0.029 |
| `KXNFLSPREAD-26NOV01LACLAR-LAR5` | SPREAD | 4.5 | 0.56 | 0.57 | 0.59 | +0.029 |

_Ranked 74 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Terrance Ferguson (TE, LA) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. 3 skill players are Questionable (Brenen Thompson (WR), Ladd McConkey (WR), Tre' Harris (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
3. KXNFLGAME-26NOV01LACLAR-LAR moved +0.090 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
4. The model disagrees by -0.053 on KXNFLTEAMTOTAL-26NOV01LACLAR-LAC8 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. The model disagrees by +0.035 on KXNFLSPREAD-26NOV01LACLAR-LAC8 (SPREAD). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. KXNFLTEAMTOTAL-26NOV01LACLAR-LAC8 sits at a market price of 0.92 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_LAC_LA.md`_


---

## KC @ DEN — `2026_08_KC_DEN`

- kickoff: 2026-11-01T21:25:00+00:00 (8182 minutes away) · state **PREGAME**
- venue: Empower Field at Mile High · roof outdoors · surface grass
- markets: 91 listed across 4 families — 71 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 1.25 | 0.89 |
| total | 41.45 | 41.30 |
| score | DEN 20.1 – KC 21.4 | DEN 20.2 – KC 21.1 |
| win prob DEN | 48.5% | 46.6% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 1.25 · total 41.45
- move `KXNFL1HTEAMTOTAL-26NOV01KCDEN-DEN3` +0.130
- move `KXNFLTEAMTOTAL-26NOV01KCDEN-DEN4` +0.095
- move `KXNFLTEAMTOTAL-26NOV01KCDEN-KC4` +0.095
- move `KXNFLTEAMTOTAL-26NOV01KCDEN-KC8` +0.080

**Game environment** (simulation, mean and middle 50%) — home margin -1.3 (-9.0–6.0) · total 42.6 (34.0–51.0) · P(one score) 55.5% · P(17+ blowout) 18.3% · P(total 10+ over centre) 22.9%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| DEN | 61.9 (56.0–68.0) | 35.3 (30.0–40.0) | 22.9 (18.0–27.0) | 38.3 (33.0–43.0) | 0.620 (0.554–0.687) | 0.521 / 0.694 |
| KC | 62.5 (57.0–68.0) | 34.0 (29.0–39.0) | 22.4 (18.0–27.0) | 39.2 (34.0–44.0) | 0.629 (0.562–0.697) | 0.541 / 0.715 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| DEN | 00-0036158 | RB | 1.6 (0.0–2.0) | 9.7 (5.0–13.0) | 4.8% | 42.5% | MEDIUM |
| DEN | 00-0040730 | RB | 4.0 (1.0–6.0) | 4.1 (1.0–6.0) | 12.3% | 17.9% | HIGH |
| DEN | 00-0041496 | RB | 2.0 (0.0–3.0) | 5.4 (2.0–8.0) | 6.2% | 23.8% | HIGH |
| DEN | 00-0036613 | WR | 5.7 (1.0–9.0) | 0.1 (0.0–0.0) | 17.5% | 0.6% | HIGH |
| KC | 00-0038134 | RB | 4.9 (2.0–7.0) | 17.0 (12.0–22.0) | 15.1% | 75.9% | MEDIUM |
| KC | 00-0030506 | TE | 6.9 (4.0–9.0) | 0.0 (0.0–0.0) | 21.5% | 0.1% | HIGH |
| KC | 00-0039894 | WR | 6.4 (3.0–9.0) | 0.2 (0.0–0.0) | 19.9% | 0.8% | HIGH |
| KC | 00-0041013 | RB | 2.4 (0.0–4.0) | 2.0 (0.0–3.0) | 7.5% | 8.9% | HIGH |

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 2 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV01KCDEN-KC17, KXNFLTEAMTOTAL-26NOV01KCDEN-KC29
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 19 market(s), e.g. KXNFLSPREAD-26NOV01KCDEN-KC11, KXNFLSPREAD-26NOV01KCDEN-KC10
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 3 market(s), e.g. KXNFLTEAMTOTAL-26NOV01KCDEN-KC18, KXNFLTEAMTOTAL-26NOV01KCDEN-DEN18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 21 market(s), e.g. KXNFLTOTAL-26NOV01KCDEN-63, KXNFL1HTEAMTOTAL-26NOV01KCDEN-KC20
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 10 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV01KCDEN-DEN3, KXNFLTEAMTOTAL-26NOV01KCDEN-KC8

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 32.9%  _(final margin within one score (8 points) either way; total within 10 of the centre 41.4545 (median favourite-oriented margin +1, median total 41))_
2. favourite controls / normal scoring — 13.6%  _(KC (favourite) wins by more than one score; total within 10 of the centre 41.4545 (median favourite-oriented margin +14, median total 43))_
3. competitive / high scoring — 12.1%  _(final margin within one score (8 points) either way; total 51.4545+ (centre 41.4545) (median favourite-oriented margin +1, median total 60))_
4. underdog controls / normal scoring — 10.5%  _(DEN (underdog) wins by more than one score; total within 10 of the centre 41.4545 (median favourite-oriented margin -16, median total 41))_
5. competitive / low scoring — 10.4%  _(final margin within one score (8 points) either way; total 31.4545 or fewer (centre 41.4545) (median favourite-oriented margin +1, median total 27))_
   Other — 20.4%

Marginal events (overlapping): one_score 55.5% · blowout_17 18.3% · favorite_wins 55.9% · favorite_controls 25.6% · upset 43.8% · shootout 22.9% · low_scoring 20.1% · low_possession 12.0% · high_volume_passing 11.4% · run_heavy_control 8.7%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 6.70 mph, gusts 7.40, precip prob 30%, temp 65F, forecast retrieved 2026-10-27T04:20:22+00:00 (137.08 h before kickoff)._

**`KXNFLGAME-26NOV01KCDEN-DEN`** GAME_WINNER  
- MODEL / MARKET: football 44.0% · market 48.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 18.9% · P55 mass 18.9% · P60 mass 18.9% · major-script floor 0.0% · failure mass 81.1% · win-contribution HHI 0.225
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01KCDEN-KC`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01KCDEN-DEN2`: cash correlation 0.923 · joint cash 40.0% · Jaccard of winning rows 0.910 · shared failure 56.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01KCDEN-KC2`: cash correlation -0.909 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 4.8%

**`KXNFLGAME-26NOV01KCDEN-KC`** GAME_WINNER  
- MODEL / MARKET: football 56.0% · market 52.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 81.1% · P55 mass 36.0% · P60 mass 36.0% · major-script floor 0.0% · failure mass 18.9% · win-contribution HHI 0.205
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01KCDEN-DEN`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01KCDEN-DEN2`: cash correlation -0.923 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 4.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01KCDEN-KC2`: cash correlation 0.909 · joint cash 51.2% · Jaccard of winning rows 0.914 · shared failure 44.0%

**`KXNFLSPREAD-26NOV01KCDEN-DEN2`** SPREAD margin 1.5
- MODEL / MARKET: football 40.0% · market 44.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 18.9% · P55 mass 18.9% · P60 mass 18.9% · major-script floor 0.0% · failure mass 81.1% · win-contribution HHI 0.218
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01KCDEN-DEN`: cash correlation 0.923 · joint cash 40.0% · Jaccard of winning rows 0.910 · shared failure 56.0%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01KCDEN-KC`: cash correlation -0.923 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 4.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01KCDEN-KC2`: cash correlation -0.837 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 8.8%

**`KXNFLSPREAD-26NOV01KCDEN-KC2`** SPREAD margin 1.5
- MODEL / MARKET: football 51.2% · market 49.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 25.6% · P55 mass 25.6% · P60 mass 25.6% · major-script floor 0.0% · failure mass 74.4% · win-contribution HHI 0.205
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01KCDEN-DEN`: cash correlation -0.909 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 4.8%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01KCDEN-KC`: cash correlation 0.909 · joint cash 51.2% · Jaccard of winning rows 0.914 · shared failure 44.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01KCDEN-DEN2`: cash correlation -0.837 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 8.8%

_71 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (8)**

- Brashard Smith (RB, KC) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Rashee Rice (WR, KC) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Tyler Badie (RB, DEN) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jaylon Moore (OT, KC) — Out [high] — ruled out
- Josh Simmons (OT, KC) — Injured Reserve [high] — ruled out
- Jonah Elliss (LB, DEN) — Injured Reserve [high] — ruled out
- Pat Surtain II (CB, DEN) — Out [high] — ruled out
- Talanoa Hufanga (S, DEN) — Out [high] — ruled out

**Questionable / Doubtful (2)** — resolves at the inactive release, T−90m

- Jaylen Waddle (WR, DEN) — Questionable [high]
- Zach Allen (DE, DEN) — Questionable [high]

### WEATHER

- Chance Rain Showers · 61°F · wind 6 mph NE · precip 27%
- forecast vintage 2026-10-27T04:21:36+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTEAMTOTAL-26NOV01KCDEN-KC4` | TEAM_TOTAL | 4.0 | 0.95 | 0.97 | 0.99 | +0.035 |
| `KXNFLSPREAD-26NOV01KCDEN-DEN3` | SPREAD | 2.5 | 0.42 | 0.43 | 0.39 | -0.034 |
| `KXNFLTOTAL-26NOV01KCDEN-30` | TOTAL | 30.0 | 0.84 | 0.87 | 0.82 | -0.027 |
| `KXNFLTOTAL-26NOV01KCDEN-33` | TOTAL | 33.0 | 0.78 | 0.79 | 0.75 | -0.025 |
| `KXNFLTEAMTOTAL-26NOV01KCDEN-DEN32` | TEAM_TOTAL | 32.0 | 0.08 | 0.12 | 0.11 | +0.024 |
| `KXNFLSPREAD-26NOV01KCDEN-KC3` | SPREAD | 2.5 | 0.46 | 0.47 | 0.44 | -0.023 |

_Ranked 71 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Tyler Badie (RB, DEN) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Rashee Rice (WR, KC) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 1 skill players are Questionable (Jaylen Waddle (WR)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFL1HTEAMTOTAL-26NOV01KCDEN-DEN3 moved +0.130 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by +0.035 on KXNFLTEAMTOTAL-26NOV01KCDEN-KC4 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by -0.034 on KXNFLSPREAD-26NOV01KCDEN-DEN3 (SPREAD). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLTEAMTOTAL-26NOV01KCDEN-KC4 sits at a market price of 0.95 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_KC_DEN.md`_


---

## NE @ MIA — `2026_08_NE_MIA`

- kickoff: 2026-11-01T21:25:00+00:00 (8182 minutes away) · state **PREGAME**
- venue: Hard Rock Stadium · roof outdoors · surface grass
- markets: 95 listed across 4 families — 75 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | 7.11 | 7.93 |
| total | 44.73 | 44.99 |
| score | MIA 18.8 – NE 25.9 | MIA 18.5 – NE 26.5 |
| win prob MIA | 23.5% | 23.2% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) 7.11 · total 44.73
- move `KXNFLGAME-26NOV01NEMIA-MIA` -0.120
- move `KXNFLTEAMTOTAL-26NOV01NEMIA-NE4` +0.120
- move `KXNFLGAME-26NOV01NEMIA-NE` +0.115
- move `KXNFLTEAMTOTAL-26NOV01NEMIA-NE8` +0.110

**Game environment** (simulation, mean and middle 50%) — home margin -7.5 (-15.0–-1.0) · total 45.6 (37.0–53.0) · P(one score) 44.2% · P(17+ blowout) 24.3% · P(total 10+ over centre) 23.3%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| MIA | 59.1 (54.0–65.0) | 27.9 (23.0–32.0) | 23.9 (19.0–28.0) | 34.8 (30.0–40.0) | 0.589 (0.524–0.656) | 0.470 / 0.641 |
| NE | 62.2 (57.0–68.0) | 30.1 (25.0–35.0) | 25.7 (21.0–30.0) | 35.5 (30.0–41.0) | 0.570 (0.502–0.638) | 0.504 / 0.680 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| MIA | 00-0040198 | RB | 2.0 (0.0–3.0) | 13.3 (8.0–18.0) | 7.5% | 55.9% | MEDIUM |
| MIA | 00-0039880 | WR | 5.6 (3.0–8.0) | 1.3 (0.0–2.0) | 20.8% | 5.6% | HIGH |
| MIA | 00-0038128 | QB | 0.5 (0.0–1.0) | 6.5 (4.0–8.0) | 1.8% | 7.0% | MEDIUM |
| MIA | 00-0039874 | RB | 0.6 (0.0–1.0) | 3.7 (0.0–6.0) | 2.3% | 15.5% | HIGH |
| NE | 00-0036875 | RB | 3.4 (1.0–5.0) | 11.5 (6.0–16.0) | 11.9% | 44.7% | MEDIUM |
| NE | 00-0040734 | RB | 1.4 (0.0–2.0) | 6.9 (3.0–10.0) | 4.9% | 26.7% | HIGH |
| NE | 00-0035676 | WR | 7.3 (4.0–10.0) | 0.0 (0.0–0.0) | 25.4% | 0.0% | MEDIUM |
| NE | 00-0039851 | QB | 0.2 (0.0–0.0) | 5.9 (4.0–7.0) | 0.5% | 5.2% | MEDIUM |

**Historical research tags** (5; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `MOVEMENT_RESEARCH_CANDIDATE` · H-20261001-B10 YES · Chasing a pregame move loses · 2 market(s), e.g. KXNFLTEAMTOTAL-26NOV01NEMIA-NE29, KXNFL1HTEAMTOTAL-26NOV01NEMIA-NE21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLGAME-26NOV01NEMIA-MIA, KXNFLSPREAD-26NOV01NEMIA-MIA5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLTEAMTOTAL-26NOV01NEMIA-MIA15, KXNFLSPREAD-26NOV01NEMIA-NE4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 23 market(s), e.g. KXNFLSPREAD-26NOV01NEMIA-MIA8, KXNFLSPREAD-26NOV01NEMIA-MIA5
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 11 market(s), e.g. KXNFLTEAMTOTAL-26NOV01NEMIA-NE4, KXNFLTEAMTOTAL-26NOV01NEMIA-NE15

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. favourite controls / normal scoring — 25.8%  _(NE (favourite) wins by more than one score; total within 10 of the centre 44.7273 (median favourite-oriented margin +16, median total 44))_
2. competitive / normal scoring — 24.8%  _(final margin within one score (8 points) either way; total within 10 of the centre 44.7273 (median favourite-oriented margin +2, median total 45))_
3. favourite controls / high scoring — 10.4%  _(NE (favourite) wins by more than one score; total 54.7273+ (centre 44.7273) (median favourite-oriented margin +16, median total 61))_
4. competitive / high scoring — 10.2%  _(final margin within one score (8 points) either way; total 54.7273+ (centre 44.7273) (median favourite-oriented margin +3, median total 63))_
5. favourite controls / low scoring — 9.4%  _(NE (favourite) wins by more than one score; total 34.7273 or fewer (centre 44.7273) (median favourite-oriented margin +16, median total 29))_
   Other — 19.5%

Marginal events (overlapping): one_score 44.2% · blowout_17 24.3% · favorite_wins 75.4% · favorite_controls 45.6% · upset 24.5% · shootout 23.3% · low_scoring 20.2% · low_possession 21.2% · high_volume_passing 0.6% · run_heavy_control 15.5%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 10.40 mph, gusts 8.90, precip prob 29%, temp 85F, forecast retrieved 2026-10-27T01:57:43+00:00 (139.45 h before kickoff)._

**`KXNFLGAME-26NOV01NEMIA-MIA`** GAME_WINNER  
- MODEL / MARKET: football 24.6% · market 23.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 10.2% · P55 mass 10.2% · P60 mass 10.2% · major-script floor 0.0% · failure mass 89.8% · win-contribution HHI 0.215
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01NEMIA-NE`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01NEMIA-MIA2`: cash correlation 0.918 · joint cash 21.5% · Jaccard of winning rows 0.876 · shared failure 75.4%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01NEMIA-NE8`: cash correlation -0.576 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 25.0%

**`KXNFLGAME-26NOV01NEMIA-NE`** GAME_WINNER  
- MODEL / MARKET: football 75.4% · market 76.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 89.8% · P55 mass 89.8% · P60 mass 89.8% · major-script floor 61.4% · failure mass 10.2% · win-contribution HHI 0.216
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01NEMIA-MIA`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01NEMIA-MIA2`: cash correlation -0.918 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01NEMIA-NE8`: cash correlation 0.576 · joint cash 50.4% · Jaccard of winning rows 0.668 · shared failure 24.6%

**`KXNFLSPREAD-26NOV01NEMIA-MIA2`** SPREAD margin 1.5
- MODEL / MARKET: football 21.5% · market 21.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 10.2% · P55 mass 10.2% · P60 mass 10.2% · major-script floor 0.0% · failure mass 89.8% · win-contribution HHI 0.205
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01NEMIA-MIA`: cash correlation 0.918 · joint cash 21.5% · Jaccard of winning rows 0.876 · shared failure 75.4%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01NEMIA-NE`: cash correlation -0.918 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01NEMIA-NE8`: cash correlation -0.528 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 28.0%

**`KXNFLSPREAD-26NOV01NEMIA-NE8`** SPREAD margin 7.5
- MODEL / MARKET: football 50.4% · market 46.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 45.6% · P55 mass 45.6% · P60 mass 45.6% · major-script floor 9.6% · failure mass 54.4% · win-contribution HHI 0.342
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01NEMIA-MIA`: cash correlation -0.576 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 25.0%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01NEMIA-NE`: cash correlation 0.576 · joint cash 50.4% · Jaccard of winning rows 0.668 · shared failure 24.6%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01NEMIA-MIA2`: cash correlation -0.528 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 28.0%

_75 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (9)**

- Alijah Vera-Tucker (G, NE) — Injured Reserve [high] — ruled out
- Ben Brown (C, NE) — Out [single_source] — ruled out
- Marcus Bryant (OT, NE) — Injured Reserve [high] — ruled out
- Carlton Davis III (CB, NE) — Out [high] — ruled out
- Channing Canada (CB, NE) — Out [high] — ruled out
- Karon Prunty (CB, NE) — Out [high] — ruled out
- Reese Taylor (CB, MIA) — Out [high] — ruled out
- Robert Beal Jr. (DE, MIA) — Out [single_source] — ruled out
- _...and 1 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (1)** — resolves at the inactive release, T−90m

- Jaylen Wright (RB, MIA) — Questionable [high]

### WEATHER

- Chance Showers And Thunderstorms · 84°F · wind 9 mph E · precip 36%
- forecast vintage 2026-10-27T04:21:37+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLSPREAD-26NOV01NEMIA-NE8` | SPREAD | 7.5 | 0.46 | 0.47 | 0.52 | +0.052 |
| `KXNFLSPREAD-26NOV01NEMIA-NE14` | SPREAD | 13.5 | 0.34 | 0.34 | 0.29 | -0.043 |
| `KXNFLTEAMTOTAL-26NOV01NEMIA-NE27` | TEAM_TOTAL | 27.0 | 0.52 | 0.53 | 0.48 | -0.042 |
| `KXNFLTEAMTOTAL-26NOV01NEMIA-MIA11` | TEAM_TOTAL | 11.0 | 0.79 | 0.80 | 0.83 | +0.041 |
| `KXNFLSPREAD-26NOV01NEMIA-NE21` | SPREAD | 20.5 | 0.17 | 0.19 | 0.14 | -0.037 |
| `KXNFLSPREAD-26NOV01NEMIA-NE18` | SPREAD | 17.5 | 0.23 | 0.24 | 0.20 | -0.033 |

_Ranked 75 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. 1 skill players are Questionable (Jaylen Wright (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
2. KXNFLGAME-26NOV01NEMIA-MIA moved -0.120 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
3. The model disagrees by +0.052 on KXNFLSPREAD-26NOV01NEMIA-NE8 (SPREAD). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
4. The model disagrees by -0.043 on KXNFLSPREAD-26NOV01NEMIA-NE14 (SPREAD). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
5. KXNFLTEAMTOTAL-26NOV01NEMIA-NE8 sits at a market price of 0.96 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_NE_MIA.md`_


---

## PHI @ WAS — `2026_08_PHI_WAS`

- kickoff: 2026-11-02T01:20:00+00:00 (8417 minutes away) · state **PREGAME**
- venue: Northwest Stadium · roof outdoors · surface grass
- markets: 93 listed across 4 families — 73 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -4.30 | -4.37 |
| total | 41.25 | 41.44 |
| score | WAS 22.8 – PHI 18.5 | WAS 22.9 – PHI 18.5 |
| win prob WAS | 64.5% | 65.0% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -4.30 · total 41.25
- move `KXNFLTEAMTOTAL-26NOV01PHIWAS-WAS4` +0.100
- move `KXNFLTOTAL-26NOV01PHIWAS-21` +0.100
- move `KXNFLTOTAL-26NOV01PHIWAS-63` -0.095
- move `KXNFLTOTAL-26NOV01PHIWAS-60` -0.085

**Game environment** (simulation, mean and middle 50%) — home margin 4.5 (-3.0–12.0) · total 42.7 (34.0–51.0) · P(one score) 51.7% · P(17+ blowout) 17.3% · P(total 10+ over centre) 23.5%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| WAS | 63.6 (58.0–69.0) | 29.4 (25.0–34.0) | 26.2 (21.0–31.0) | 36.4 (31.0–42.0) | 0.573 (0.506–0.642) | 0.494 / 0.668 |
| PHI | 61.3 (56.0–67.0) | 34.2 (29.0–39.0) | 23.4 (19.0–28.0) | 37.4 (32.0–42.0) | 0.610 (0.544–0.677) | 0.500 / 0.675 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| WAS | 00-0037256 | RB | 2.1 (0.0–3.0) | 12.3 (7.0–17.0) | 7.7% | 46.8% | MEDIUM |
| WAS | 00-0039910 | QB | 0.0 (0.0–0.0) | 7.4 (5.0–9.0) | 0.1% | 4.7% | MEDIUM |
| WAS | 00-0033955 | RB | 1.1 (0.0–2.0) | 6.1 (2.0–9.0) | 4.1% | 23.3% | HIGH |
| WAS | 00-0033699 | RB | 1.5 (0.0–2.0) | 5.1 (1.0–7.0) | 5.5% | 19.3% | HIGH |
| PHI | 00-0037258 | RB | 3.9 (1.0–6.0) | 13.0 (8.0–18.0) | 12.0% | 55.8% | MEDIUM |
| PHI | 00-0034844 | RB | 2.0 (0.0–3.0) | 7.0 (1.0–11.0) | 6.3% | 29.9% | HIGH |
| PHI | 00-0034351 | TE | 7.7 (4.0–10.0) | 0.0 (0.0–0.0) | 24.0% | 0.0% | MEDIUM |
| PHI | 00-0040867 | WR | 6.2 (3.0–9.0) | 0.1 (0.0–0.0) | 19.0% | 0.4% | HIGH |

**Historical research tags** (4; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV01PHIWAS-WAS21, KXNFLSPREAD-26NOV01PHIWAS-WAS18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 4 market(s), e.g. KXNFLGAME-26NOV01PHIWAS-WAS, KXNFLTEAMTOTAL-26NOV01PHIWAS-PHI15
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 24 market(s), e.g. KXNFL1HTEAMTOTAL-26NOV01PHIWAS-WAS21, KXNFL1HTEAMTOTAL-26NOV01PHIWAS-WAS20
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 10 market(s), e.g. KXNFLTEAMTOTAL-26NOV01PHIWAS-WAS11, KXNFLTOTAL-26NOV01PHIWAS-27

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 29.6%  _(final margin within one score (8 points) either way; total within 10 of the centre 41.25 (median favourite-oriented margin +2, median total 41))_
2. favourite controls / normal scoring — 20.5%  _(WAS (favourite) wins by more than one score; total within 10 of the centre 41.25 (median favourite-oriented margin +14, median total 41))_
3. competitive / high scoring — 11.5%  _(final margin within one score (8 points) either way; total 51.25+ (centre 41.25) (median favourite-oriented margin +3, median total 60))_
4. competitive / low scoring — 10.7%  _(final margin within one score (8 points) either way; total 31.25 or fewer (centre 41.25) (median favourite-oriented margin +3, median total 26))_
5. favourite controls / high scoring — 8.4%  _(WAS (favourite) wins by more than one score; total 51.25+ (centre 41.25) (median favourite-oriented margin +15, median total 59))_
   Other — 19.4%

Marginal events (overlapping): one_score 51.7% · blowout_17 17.3% · favorite_wins 66.1% · favorite_controls 35.1% · upset 33.7% · shootout 23.5% · low_scoring 20.3% · low_possession 11.1% · high_volume_passing 2.9% · run_heavy_control 14.8%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 6.80 mph, gusts 23.30, precip prob 37%, temp 58F, forecast retrieved 2026-10-27T04:20:22+00:00 (140.99 h before kickoff)._

**`KXNFLGAME-26NOV01PHIWAS-PHI`** GAME_WINNER  
- MODEL / MARKET: football 33.8% · market 35.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 13.2% · P55 mass 13.2% · P60 mass 13.2% · major-script floor 0.0% · failure mass 86.8% · win-contribution HHI 0.210
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01PHIWAS-WAS`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01PHIWAS-PHI2`: cash correlation 0.949 · joint cash 31.4% · Jaccard of winning rows 0.930 · shared failure 66.2%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01PHIWAS-WAS5`: cash correlation -0.720 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 15.8%

**`KXNFLGAME-26NOV01PHIWAS-WAS`** GAME_WINNER  
- MODEL / MARKET: football 66.2% · market 64.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 86.8% · P55 mass 86.8% · P60 mass 76.1% · major-script floor 57.6% · failure mass 13.2% · win-contribution HHI 0.213
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01PHIWAS-PHI`: cash correlation -1.000 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 0.0%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01PHIWAS-PHI2`: cash correlation -0.949 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 2.4%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01PHIWAS-WAS5`: cash correlation 0.720 · joint cash 50.3% · Jaccard of winning rows 0.760 · shared failure 33.8%

**`KXNFLSPREAD-26NOV01PHIWAS-PHI2`** SPREAD margin 1.5
- MODEL / MARKET: football 31.4% · market 32.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 13.2% · P55 mass 13.2% · P60 mass 13.2% · major-script floor 0.0% · failure mass 86.8% · win-contribution HHI 0.201
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01PHIWAS-PHI`: cash correlation 0.949 · joint cash 31.4% · Jaccard of winning rows 0.930 · shared failure 66.2%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01PHIWAS-WAS`: cash correlation -0.949 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 2.4%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01PHIWAS-WAS5`: cash correlation -0.682 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 18.2%

**`KXNFLSPREAD-26NOV01PHIWAS-WAS5`** SPREAD margin 4.5
- MODEL / MARKET: football 50.3% · market 49.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 35.1% · P55 mass 35.1% · P60 mass 35.1% · major-script floor 26.9% · failure mass 64.9% · win-contribution HHI 0.244
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01PHIWAS-PHI`: cash correlation -0.720 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 15.8%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV01PHIWAS-WAS`: cash correlation 0.720 · joint cash 50.3% · Jaccard of winning rows 0.760 · shared failure 33.8%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV01PHIWAS-PHI2`: cash correlation -0.682 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 18.2%

_73 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (12)**

- Cole Payton (QB, PHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Britain Covey (WR, PHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- DeVonta Smith (WR, PHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Dontayvion Wicks (WR, PHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jaylin Lane (WR, WAS) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Terry McLaurin (WR, WAS) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Jake Majors (C, PHI) — Out [high] — ruled out
- Lane Johnson (OT, PHI) — Out [single_source] — ruled out
- _...and 4 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Marcus Mariota (QB, WAS) — Questionable [conflicting]
- Saquon Barkley (RB, PHI) — Questionable [high]
- Charles Omenihu (DE, WAS) — Questionable [conflicting]
- Javon Kinlaw (DT, WAS) — Questionable [high]

### WEATHER

- Mostly Cloudy · 61°F · wind 3 mph SE · precip 12%
- forecast vintage 2026-10-27T04:22:39+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLTEAMTOTAL-26NOV01PHIWAS-PHI18` | TEAM_TOTAL | 18.0 | 0.50 | 0.52 | 0.55 | +0.048 |
| `KXNFLTEAMTOTAL-26NOV01PHIWAS-PHI22` | TEAM_TOTAL | 22.0 | 0.33 | 0.35 | 0.38 | +0.042 |
| `KXNFLTEAMTOTAL-26NOV01PHIWAS-PHI21` | TEAM_TOTAL | 21.0 | 0.37 | 0.39 | 0.41 | +0.040 |
| `KXNFLTEAMTOTAL-26NOV01PHIWAS-PHI11` | TEAM_TOTAL | 11.0 | 0.79 | 0.80 | 0.82 | +0.040 |
| `KXNFLSPREAD-26NOV01PHIWAS-WAS17` | SPREAD | 16.5 | 0.17 | 0.19 | 0.14 | -0.037 |
| `KXNFLTEAMTOTAL-26NOV01PHIWAS-PHI25` | TEAM_TOTAL | 25.0 | 0.22 | 0.23 | 0.25 | +0.031 |

_Ranked 73 tradable markets; 0 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Britain Covey (WR, PHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Cole Payton (QB, PHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Saquon Barkley (RB), Marcus Mariota (QB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLTEAMTOTAL-26NOV01PHIWAS-WAS4 moved +0.100 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by +0.048 on KXNFLTEAMTOTAL-26NOV01PHIWAS-PHI18 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by +0.042 on KXNFLTEAMTOTAL-26NOV01PHIWAS-PHI22 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLTEAMTOTAL-26NOV01PHIWAS-WAS36 sits at a market price of 0.07 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_PHI_WAS.md`_


---

## CHI @ SEA — `2026_08_CHI_SEA`

- kickoff: 2026-11-03T01:15:00+00:00 (9852 minutes away) · state **PREGAME**
- venue: Lumen Field · roof outdoors · surface fieldturf
- markets: 93 listed across 4 families — 73 supported, 20 no model, 0 rules unresolved, 0 identity unresolved

### MARKET-IMPLIED vs MODEL

| | market (research-implied) | model |
|---|---|---|
| spread (home) | -3.10 | -2.95 |
| total | 47.14 | 47.42 |
| score | SEA 25.1 – CHI 22.0 | SEA 25.2 – CHI 22.2 |
| win prob SEA | 61.0% | 59.9% |

_RESEARCH MARKET-IMPLIED -- inferred from midpoints, not executable_

### GAME SCRIPT INPUTS (context only — authorises nothing)

_GAME ENVIRONMENT -> TEAM VOLUME -> PLAYER OPPORTUNITY -> EFFICIENCY -> MARKET EXPRESSION. CONTEXT ONLY: no tag or script input creates a BET state, bypasses preflight, or changes an edge, a threshold, a stake or a model probability._

**Market baseline** — spread (home) -3.10 · total 47.14
- move `KXNFLGAME-26NOV02CHISEA-CHI` -0.030
- move `KXNFLSPREAD-26NOV02CHISEA-SEA21` +0.025
- move `KXNFLSPREAD-26NOV02CHISEA-CHI14` +0.025
- move `KXNFLSPREAD-26NOV02CHISEA-SEA15` +0.020

**Game environment** (simulation, mean and middle 50%) — home margin 3.6 (-4.0–11.0) · total 48.6 (39.0–57.0) · P(one score) 51.6% · P(17+ blowout) 18.0% · P(total 10+ over centre) 23.8%
_Score state: NOT_SIMULATED: final margin/total only; see team_volume.by_final_margin for the conditional proxy_

| team | plays | pass att | designed rush | dropbacks | pass rate | pass rate if leading 14+ / trailing 14+ |
|---|---|---|---|---|---|---|
| SEA | 62.8 (57.0–68.0) | 31.8 (27.0–36.0) | 26.4 (21.0–31.0) | 35.6 (30.0–41.0) | 0.566 (0.499–0.635) | 0.484 / 0.658 |
| CHI | 65.3 (60.0–71.0) | 35.1 (30.0–40.0) | 24.1 (19.0–29.0) | 40.7 (35.0–46.0) | 0.623 (0.558–0.690) | 0.520 / 0.692 |

| team | player | pos | targets | carries | target share | carry share | role uncertainty |
|---|---|---|---|---|---|---|---|
| SEA | 00-0038797 | RB | 2.1 (0.0–3.0) | 18.1 (13.0–23.0) | 6.9% | 68.6% | MEDIUM |
| SEA | 00-0038543 | WR | 11.9 (8.0–15.0) | 0.8 (0.0–1.0) | 39.3% | 3.0% | MEDIUM |
| SEA | 00-0039299 | RB | 2.3 (0.0–3.0) | 4.8 (1.0–7.0) | 7.6% | 18.3% | HIGH |
| SEA | 00-0039793 | TE | 5.1 (2.0–7.0) | 1.0 (0.0–1.0) | 17.0% | 3.7% | HIGH |
| CHI | 00-0036275 | RB | 3.7 (1.0–5.0) | 16.5 (11.0–21.0) | 11.2% | 68.5% | MEDIUM |
| CHI | 00-0040126 | TE | 7.7 (4.0–10.0) | 0.0 (0.0–0.0) | 23.4% | 0.2% | MEDIUM |
| CHI | 00-0040735 | WR | 6.0 (3.0–8.0) | 1.2 (0.0–1.0) | 18.3% | 4.9% | HIGH |
| CHI | 00-0039919 | WR | 6.7 (4.0–9.0) | 0.1 (0.0–0.0) | 20.4% | 0.3% | HIGH |

**Historical research tags** (4; preregistered hypotheses under test — NOT evidence, NOT a signal)
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B01 YES · Full-game longshot YES underpriced at the mid · 21 market(s), e.g. KXNFLSPREAD-26NOV02CHISEA-SEA18, KXNFLSPREAD-26NOV02CHISEA-CHI4
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B02 YES · Full-game YES at 60-70c overpriced at the mid · 5 market(s), e.g. KXNFLGAME-26NOV02CHISEA-SEA, KXNFLTEAMTOTAL-26NOV02CHISEA-CHI18
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 NO · Sides priced 90c+ lose after fees · 17 market(s), e.g. KXNFLTOTAL-26NOV02CHISEA-68, KXNFLSPREAD-26NOV02CHISEA-SEA21
- `PRICE_BUCKET_RESEARCH_CANDIDATE` · H-20261001-B03 YES · Sides priced 90c+ lose after fees · 11 market(s), e.g. KXNFLTEAMTOTAL-26NOV02CHISEA-SEA4, KXNFLTEAMTOTAL-26NOV02CHISEA-CHI11

### GAME SCRIPT V2 (RESEARCH_ONLY — authorises nothing)

_RESEARCH_ONLY (GAME SCRIPT V2): script probabilities, robustness and dependency describe the market-centred simulation; they create no BET state and change no edge, threshold, stake or probability. MARKET_CENTRED_GAME: every script probability is the market centre plus the historical residual bank; a favourite-control share is not a football edge on the side._

**PRIMARY PLAUSIBLE SCRIPTS** (final-state cells of the simulated rows)

1. competitive / normal scoring — 28.5%  _(final margin within one score (8 points) either way; total within 10 of the centre 47.1429 (median favourite-oriented margin +2, median total 48))_
2. favourite controls / normal scoring — 19.2%  _(SEA (favourite) wins by more than one score; total within 10 of the centre 47.1429 (median favourite-oriented margin +14, median total 47))_
3. competitive / high scoring — 11.9%  _(final margin within one score (8 points) either way; total 57.1429+ (centre 47.1429) (median favourite-oriented margin +2, median total 65))_
4. competitive / low scoring — 11.2%  _(final margin within one score (8 points) either way; total 37.1429 or fewer (centre 47.1429) (median favourite-oriented margin +2, median total 32))_
5. underdog controls / normal scoring — 8.1%  _(CHI (underdog) wins by more than one score; total within 10 of the centre 47.1429 (median favourite-oriented margin -14, median total 49))_
   Other — 21.1%

Marginal events (overlapping): one_score 51.6% · blowout_17 18.0% · favorite_wins 63.5% · favorite_controls 33.2% · upset 36.2% · shootout 23.8% · low_scoring 20.4% · low_possession 5.3% · high_volume_passing 7.1% · run_heavy_control 15.8%
_Not simulated: lead changes, time leading, scoring sequence / quarter scores, early blowout, late comeback, red-zone trips, routes and snaps, drive counts._
_Weather (NOT_IN_MODEL): wind 5.60 mph, gusts 10.10, precip prob 7%, temp 47F, forecast retrieved 2026-10-27T04:20:22+00:00 (164.91 h before kickoff)._

**`KXNFLGAME-26NOV02CHISEA-CHI`** GAME_WINNER  
- MODEL / MARKET: football 36.4% · market 38.5% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 15.1% · P55 mass 15.1% · P60 mass 15.1% · major-script floor 0.0% · failure mass 84.9% · win-contribution HHI 0.207
- THESIS DEPENDENCY with `KXNFLGAME-26NOV02CHISEA-SEA`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV02CHISEA-CHI2`: cash correlation 0.935 · joint cash 33.2% · Jaccard of winning rows 0.914 · shared failure 63.6%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV02CHISEA-SEA4`: cash correlation -0.768 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 12.9%

**`KXNFLGAME-26NOV02CHISEA-SEA`** GAME_WINNER  
- MODEL / MARKET: football 63.6% · market 61.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 84.9% · P55 mass 84.9% · P60 mass 45.2% · major-script floor 57.7% · failure mass 15.1% · win-contribution HHI 0.208
- THESIS DEPENDENCY with `KXNFLGAME-26NOV02CHISEA-CHI`: cash correlation -1.000 · joint cash 0.1% · Jaccard of winning rows 0.001 · shared failure 0.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV02CHISEA-CHI2`: cash correlation -0.935 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV02CHISEA-SEA4`: cash correlation 0.768 · joint cash 50.7% · Jaccard of winning rows 0.797 · shared failure 36.4%

**`KXNFLSPREAD-26NOV02CHISEA-CHI2`** SPREAD margin 1.5
- MODEL / MARKET: football 33.2% · market 36.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 15.1% · P55 mass 15.1% · P60 mass 15.1% · major-script floor 0.0% · failure mass 84.9% · win-contribution HHI 0.204
- THESIS DEPENDENCY with `KXNFLGAME-26NOV02CHISEA-CHI`: cash correlation 0.935 · joint cash 33.2% · Jaccard of winning rows 0.914 · shared failure 63.6%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV02CHISEA-SEA`: cash correlation -0.935 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 3.1%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV02CHISEA-SEA4`: cash correlation -0.716 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 16.0%

**`KXNFLSPREAD-26NOV02CHISEA-SEA4`** SPREAD margin 3.5
- MODEL / MARKET: football 50.7% · market 46.0% · reconciled not validated for this family (deployed weight 0) -- not shown
- SCRIPT ROBUSTNESS: P50 mass 33.2% · P55 mass 33.2% · P60 mass 33.2% · major-script floor 31.7% · failure mass 66.8% · win-contribution HHI 0.228
- THESIS DEPENDENCY with `KXNFLGAME-26NOV02CHISEA-CHI`: cash correlation -0.768 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 12.9%
- THESIS DEPENDENCY with `KXNFLGAME-26NOV02CHISEA-SEA`: cash correlation 0.768 · joint cash 50.7% · Jaccard of winning rows 0.797 · shared failure 36.4%
- THESIS DEPENDENCY with `KXNFLSPREAD-26NOV02CHISEA-CHI2`: cash correlation -0.716 · joint cash 0.0% · Jaccard of winning rows 0.000 · shared failure 16.0%

_73 contracts carry a script matrix in the run's GAME SCRIPT V2 file (20261027T042733Z.sim-1.1.0.scripts_v2.json.gz); 16 headline pairs with |cash correlation| >= 0.30._

### INJURIES / AVAILABILITY

_compared against the previous capture_

**Out / IR (11)**

- Drew Lock (QB, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Cole Kmet (TE, CHI) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Jadarian Price (RB, SEA) — Injured Reserve [high] — ruled out -- role redistributes to the depth chart behind him
- Kyle Monangai (RB, CHI) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Zach Charbonnet (RB, SEA) — Out [high] — ruled out -- role redistributes to the depth chart behind him
- Anthony Johnson Jr. (S, CHI) — Out [high] · **CHANGED from Injured Reserve** — ruled out
- Chazz Surratt (LB, SEA) — Out [high] — ruled out
- Connor O'Toole (LB, SEA) — Out [high] — ruled out
- _...and 3 more (mostly non-skill positions); full list in the game file_

**Questionable / Doubtful (4)** — resolves at the inactive release, T−90m

- Rashid Shaheed (WR, SEA) — Questionable [conflicting]
- Velus Jones Jr. (RB, SEA) — Questionable [conflicting]
- Charles Cross (OT, SEA) — Doubtful [conflicting]
- Malik Muhammad II (CB, CHI) — Questionable [conflicting]

### WEATHER

- None · None°F · wind None  · precip None%
- forecast vintage 2026-10-27T04:22:40+00:00 · material: **False**

### COHERENT SIMULATION — PLAYER PROJECTIONS

_Simulation freshness: **SIM_CURRENT** (lag 0.0m, target <= 180.0m)._
**This is the current projection system (sim-1.x, run `20261027T042733Z`).** Every number below is read off the coherent simulation's own distribution for that player and statistic: one simulated football game, one distribution per player/stat, and that distribution prices the whole Kalshi ladder. `football median` is that distribution's own p50.

_This simulation run priced no player/stat market in this game. The coverage accounting below says why, market group by market group._

_Simulation coverage: 0 of 0 listed player/stat groups simulated and exposed, 0 refused with a reason, silently missing 0. The full accounting is in this game's own file under `games/`._

### TOP DISAGREEMENTS (tradable books only)

| market | who | line | mkt mid | YES ask | model | disagree |
|---|---|---|---|---|---|---|
| `KXNFLSPREAD-26NOV02CHISEA-CHI8` | SPREAD | 7.5 | 0.16 | 0.17 | 0.20 | +0.049 |
| `KXNFLTEAMTOTAL-26NOV02CHISEA-SEA25` | TEAM_TOTAL | 25.0 | 0.51 | 0.52 | 0.54 | +0.040 |
| `KXNFLTEAMTOTAL-26NOV02CHISEA-CHI25` | TEAM_TOTAL | 25.0 | 0.35 | 0.37 | 0.39 | +0.036 |
| `KXNFLSPREAD-26NOV02CHISEA-CHI11` | SPREAD | 10.5 | 0.12 | 0.13 | 0.15 | +0.034 |
| `KXNFLSPREAD-26NOV02CHISEA-CHI10` | SPREAD | 9.5 | 0.14 | 0.15 | 0.17 | +0.032 |
| `KXNFLTEAMTOTAL-26NOV02CHISEA-CHI32` | TEAM_TOTAL | 32.0 | 0.13 | 0.15 | 0.16 | +0.031 |

_Ranked 72 tradable markets; 1 excluded as untradable._

### KEY QUESTIONS FOR THE HANDICAPPER

1. Kyle Monangai (RB, CHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
2. Cole Kmet (TE, CHI) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
3. 2 skill players are Questionable (Rashid Shaheed (WR), Velus Jones Jr. (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
4. KXNFLGAME-26NOV02CHISEA-CHI moved -0.030 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
5. The model disagrees by +0.049 on KXNFLSPREAD-26NOV02CHISEA-CHI8 (SPREAD). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
6. The model disagrees by +0.040 on KXNFLTEAMTOTAL-26NOV02CHISEA-SEA25 (TEAM_TOTAL). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
7. KXNFLSPREAD-26NOV02CHISEA-CHI11 sits at a market price of 0.12 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

_Full board, player ladders, best expressions and correlation groups: `games/2026_08_CHI_SEA.md`_


---

## HOW TO USE THIS PACKET

1. Handicap each game independently. The model's ranked disagreements are an input, not a shortlist.
2. For any thesis you form, check **BEST EXPRESSIONS** before choosing a contract — the largest disagreement is rarely the best payout for the risk.
3. Check **CORRELATION GROUPS** before sizing more than one position in a game.
4. Record every serious decision, including passes, via the recommendation ledger (`scripts/handicap/validate_recommendations.py`, then commit to the `handicap-data` branch).