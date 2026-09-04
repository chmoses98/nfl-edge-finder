# Kalshi NFL Market Taxonomy

Source of truth: the API. This document describes what the classifier (`nfl_edge/kalshi/classifier.py`) extracts and
what was actually observed in the 2026-09-04 discovery run (23,275 NFL markets across 183 series with markets;
392 NFL series in the registry `config/kalshi_nfl_series.json`). Anything the classifier cannot place becomes
`UNKNOWN_NEEDS_CLASSIFICATION` and is still captured; the test suite fails if any `KXNFL*` series in the fixture is unknown.

## Ticker grammar (verified)

* Single-game event: `{SERIES}-{YY}{MON}{DD}{AWAY}{HOME}` e.g. `KXNFLSPREAD-26SEP14DENKC` (Denver at Kansas City, 2026-09-14). No kickoff time in the ticker; kickoff comes from the nflverse schedule join.
* Kalshi team codes = nflverse codes except `JAC→JAX`, `LAR→LA`.
* Spread/team-total legs: `-{TEAM}{N}` with `floor_strike = N − 0.5`, `strike_type=greater` ⇒ YES iff team margin (or team points) > N − 0.5. Both teams get a full ladder in the same event.
* Totals: `-{N}`, floor N − 0.5 ⇒ YES iff total ≥ N. **Integer rungs settle ≥ N, never > N**; no pushes exist.
* Player props: `-{TEAM}{INITIAL}{SURNAME}{JERSEY}-{K}` e.g. `KXNFLRECYDS-26SEP10SFLAR-LARDADAMS17-120` (floor 119.5 ⇒ receiving yards ≥ 120). Title `"Davante Adams: 120+ receiving yards"`. `custom_strike.football_player` is Kalshi's stable player UUID; `scripts/kalshi/build_player_map.py` maps it to GSIS (name+team+jersey, auditable, 118/141 resolved exactly on audit day, the rest flagged).
* Older (preseason) props use `strike_type=structured` with the same x.5 floor — handled identically.
* Win margin: `custom_strike["Winning Margin"]` ∈ {"tie", "1 to 6", "7 to 14", "15 or more"}.
* Race-to-N: event `KXNFLRACE-{game}-35`, legs `-KC` / `-NONE`.
* Period variants: `KXNFL{1H,2H,1Q,2Q,3Q,4Q}{"",SPREAD,TOTAL,TEAMTOTAL,BTTS,TD}`, plus `KXNFL1HFT` (half-time/full-time double result).
* Player-prop settlement nuance (series important_info): a player who is active but never takes a snap ⇒ market settles at a fair pre-game price, not NO. Inactive ⇒ same. This must be modelled as a separate outcome state, not as 0 yards.

## Semantics extracted per market
family · scope (GAME/WEEK/SEASON/EVENT) · period · stat · game_date · away/home (Kalshi + nflverse codes) · subject team · player name / Kalshi player UUID / jersey · threshold K and operator (">=" for integer ladders, ">" floor for spreads, range for margin buckets, "event" otherwise) · yes_meaning · tie/none legs · confidence · notes.

## Families observed on 2026-09-04 (live tier; open vs settled/closed counts, one example each)

| family | period | open | settled/closed | example ticker | title | YES meaning |
|---|---|---|---|---|---|---|
| SPREAD | FULL | 404 | 1203 | `KXNFLSPREAD-26SEP14DENKC-KC8` | Kansas City wins by over 7.5 points? | KC wins FULL by more than 7.5 |
| TOTAL | FULL | 304 | 939 | `KXNFLTOTAL-26SEP14DENKC-64` | Will there be over 63.5 points scored? | FULL total points >= 64 |
| SEASON_PLAYER_STAT | - | 1129 | 0 | `KXNFLSEASONRSHYDS-27C1500-SBARKLEY26` | Will Saquon Barkley record 1500+ rushing yards during 2026-2 | None season rushing_yards >= 1500 |
| AWARD | - | 825 | 300 | `KXNFLWPMOTY-27-TKELCE87` | Will Travis Kelce win the Walter Payton Man of the Year Awar | Will Travis Kelce win the Walter Payton Man of the Year Award? |
| SPREAD | 1H | 249 | 747 | `KXNFL1HSPREAD-26SEP14DENKC-KC8` | KC Chiefs wins 1H by over 7.5 points? | KC wins 1H by more than 7.5 |
| SPREAD | 2H | 249 | 747 | `KXNFL2HSPREAD-26SEP14DENKC-KC8` | KC Chiefs wins 2H by over 7.5 points? | KC wins 2H by more than 7.5 |
| SEASON_FANTASY | - | 930 | 0 | `KXNFLFFHIGHSCORE-27DST-36` | Highest scoring game by a defense/special teams: 36+ points | Highest scoring game by a defense/special teams: 36+ points |
| TOTAL | 2H | 217 | 671 | `KXNFL2HTOTAL-26SEP14DENKC-8` | Will there be over 7.5 2H points scored? | 2H total points >= 8 |
| TOTAL | 1H | 217 | 671 | `KXNFL1HTOTAL-26SEP14DENKC-8` | Will there be over 7.5 1H points scored? | 1H total points >= 8 |
| PLAYER_STAT | FULL | 458 | 394 | `KXNFLRSHYDS-26SEP09NESEA-NERSTEVENSON38-100` | Rhamondre Stevenson: 100+ rushing yards | Rhamondre Stevenson rushing_yards >= 100 |
| TEAM_WINS_BY_WEEK | - | 728 | 0 | `KXNFLWINSWEEK-26W12-WAS9` | Will Washington win at least 9 games in the first 12 weeks? | WAS wins >= 9 through week 12 |
| SPREAD | 3Q | 173 | 490 | `KXNFL3QSPREAD-26SEP14DENKC-KC8` | KC Chiefs wins 3Q by over 7.5 points? | KC wins 3Q by more than 7.5 |
| SPREAD | 1Q | 172 | 490 | `KXNFL1QSPREAD-26SEP14DENKC-KC8` | KC Chiefs wins 1Q by over 7.5 points? | KC wins 1Q by more than 7.5 |
| SPREAD | 4Q | 170 | 490 | `KXNFL4QSPREAD-26SEP14DENKC-KC8` | KC Chiefs wins 4Q by over 7.5 points? | KC wins 4Q by more than 7.5 |
| SPREAD | 2Q | 170 | 490 | `KXNFL2QSPREAD-26SEP14DENKC-KC8` | KC Chiefs wins 2Q by over 7.5 points? | KC wins 2Q by more than 7.5 |
| TOTAL | 1Q | 160 | 490 | `KXNFL1QTOTAL-26SEP14DENKC-8` | Will there be over 7.5 1Q points scored? | 1Q total points >= 8 |
| TOTAL | 4Q | 160 | 490 | `KXNFL4QTOTAL-26SEP14DENKC-8` | Will there be over 7.5 4Q points scored? | 4Q total points >= 8 |
| TOTAL | 3Q | 160 | 490 | `KXNFL3QTOTAL-26SEP14DENKC-8` | Will there be over 7.5 3Q points scored? | 3Q total points >= 8 |
| TOTAL | 2Q | 160 | 490 | `KXNFL2QTOTAL-26SEP14DENKC-8` | Will there be over 7.5 2Q points scored? | 2Q total points >= 8 |
| SEASON_WINS | - | 547 | 0 | `KXNFLWINS-ANY-27-17` | Will any Pro Football team win 17 games this regular season? | None season wins >= 17.0 |
| SEASON_MATCHUP | - | 496 | 0 | `KXNFLMATCHUP-27NFC-TBWAS` | 2026-27 NFC Championship Matchup: Tampa Bay vs Washington | 2026-27 NFC Championship Matchup: Tampa Bay vs Washington |
| SEASON_TEAM_EVENT | - | 390 | 0 | `KXNFLDIVUNDEFEATED-27-WAS` | Will Washington go undefeated in their division? | Will Washington go undefeated in their division? |
| SEASON_PLAYER_SPECIAL | - | 306 | 0 | `KXNFLTSPEC-27LV-MWASHINGTON30RUY500` | Mike Washington Jr. records 500+ rushing yards? | Mike Washington Jr. records 500+ rushing yards? |
| SEASON_LEADER | - | 260 | 0 | `KXLEADERNFLRUSHTDS-27-TETIENNE1` | Will Travis Etienne Jr. lead Pro Football in rushing touchdo | Will Travis Etienne Jr. lead Pro Football in rushing touchdowns for the 2026-2027 regular season? |
| RACE_TO_N | FULL | 240 | 0 | `KXNFLRACE-26SEP14DENKC-35-NONE` | Will neither team reach 35 points? | neither first to 35.0 points |
| SUPER_BOWL_EVENT | - | 234 | 1 | `KXSUPERBOWLHEADLINE-27-ELL` | Who will headline the Pro Football Championship Halftime Sho | Who will headline the Pro Football Championship Halftime Show? |
| SEASON_SEED | - | 224 | 0 | `KXNFL1SEED-NFC26-WAS` | Will Washington be the NFC 1 Seed? | Will Washington be the NFC 1 Seed? |
| TRANSACTION_EVENT | - | 211 | 1 | `KXNFLRETIRE-DHENRY22-2930` | Will Derrick Henry announce his retirement before the 2029-3 | Will Derrick Henry announce his retirement before the 2029-30 NFL season? |
| PERIOD_WINNER | 3Q | 48 | 147 | `KXNFL3Q-26SEP14DENKC-TIE` | Will neither team win the 3rd Quarter? | 3Q ends tied |
| PERIOD_WINNER | 1H | 48 | 147 | `KXNFL1H-26SEP14DENKC-TIE` | Will neither team win the 1st Half? | 1H ends tied |
| PERIOD_WINNER | 2Q | 48 | 147 | `KXNFL2Q-26SEP14DENKC-TIE` | Will neither team win the 2nd Quarter? | 2Q ends tied |
| PERIOD_WINNER | 4Q | 48 | 147 | `KXNFL4Q-26SEP14DENKC-TIE` | Will neither team win the 4th Quarter? | 4Q ends tied |
| PERIOD_WINNER | 2H | 48 | 147 | `KXNFL2H-26SEP14DENKC-TIE` | Will neither team win the 2nd Half? | 2H ends tied |
| PERIOD_WINNER | 1Q | 48 | 147 | `KXNFL1Q-26SEP14DENKC-TIE` | Will neither team win the 1st Quarter? | 1Q ends tied |
| SEASON_DIVISION_ORDER | - | 192 | 0 | `KXNFLDIVISIONORDER-27NFCNORTH-MINGBDETCHI` | What will be the exact order of standings for the NFC North  | What will be the exact order of standings for the NFC North at the conclusion of the 2026-27 Pro Football regular season? |
| PLAYER_ROLE_EVENT | - | 177 | 3 | `KXSTARTINGQBWEEK1-26SEP15ATL-JSTR` | Will Jack Strand be Starting Quarterback for Atlanta in Week | Will Jack Strand be Starting Quarterback for Atlanta in Week 1? |
| GAME_WINNER | FULL | 64 | 98 | `KXNFLGAME-26SEP21NYGLAR-NYG` | New York G wins | NYG wins FULL |
| WIN_MARGIN_BUCKET | FULL | 112 | 0 | `KXNFLWINMARGIN-26SEP14DENKC-TIE` | Will Denver vs Kansas City end in a tie? | game ends tied |
| WEEK_LEADER | - | 111 | 0 | `KXNFLWEEKMOSTRECYDS-26W1-WASTMCLAURIN17` | Terry McLaurin: most receiving yards in Pro Football Week 1 | Terry McLaurin: most receiving yards in Pro Football Week 1 |
| HALF_FULL_RESULT | 1H | 96 | 0 | `KXNFL1HFT-26SEP14DENKC-TIEKC` | Tie in 1st Half / Kansas City wins game | Tie in 1st Half / Kansas City wins game |
| TOTAL_TD | FULL | 96 | 0 | `KXNFLTOTALTD-26SEP14DENKC-8` | 8+ total touchdowns in the game? | total touchdowns >= 8 |
| SEASON_TEAM_LEADER | - | 96 | 0 | `KXNFLTEAMPTS-LEAST27-WAS` | Will Washington be the lowest scoring team? | Will Washington be the lowest scoring team? |
| DRAFT | - | 39 | 52 | `KXNFLDRAFTPICK-27-1-DMES` | Who will be picked 1st in the Pro Football Draft? | Who will be picked 1st in the Pro Football Draft? |
| COACH_EVENT | - | 64 | 22 | `KXNFLCOACHOUT-27MAR01-ZTAY` | Zac Taylor out before Mar 1, 2027 | Zac Taylor out before Mar 1, 2027 |
| SEASON_DIVISION_STAT | - | 80 | 0 | `KXNFLDIVMOSTWINS-27-NFCWEST` | Will the teams in the NFC West have the most total wins out  | Will the teams in the NFC West have the most total wins out of any division in the 2026-27 Pro Football regular season? |
| BOTH_TEAMS_SCORE_N | FULL | 64 | 0 | `KXNFLBOTH-26SEP14DENKC-35` | Both teams score at least 35 points | both teams score >= 35.0 |
| SEASON_SPECIAL | - | 63 | 0 | `KXNFLSZNRECORD-27REC-Y` | Will the single season receptions record be broken? | Will the single season receptions record be broken? |
| TEAM_TOTAL | FULL | 55 | 0 | `KXNFLTEAMTOTAL-26SEP10SFLAR-SF8` | SF 49ers over 7.5 points scored | SF FULL points >= 8 |
| GAME_EVENT | FULL | 52 | 0 | `KXNFLEQBTTS-26SEP14DENKC-Y` | Both teams to score in every quarter | Both teams to score in every quarter |
| FIRST_TD_TEAM | FULL | 48 | 0 | `KXNFLFIRSTTDTEAM-26SEP14DENKC-NONE` | No team scores a TD | no TD |
| NFL_BUSINESS_EVENT | - | 5 | 33 | `KXNFLSTADIUM-27MAR01TENNSTAD-Y` | Will Tennessee complete the New Nissan Stadium before Mar 1, | Will Tennessee complete the New Nissan Stadium before Mar 1, 2027? |
| PARLAY | FULL | 0 | 36 | `KXNFLPREPACKSGP-25DEC083235-56U41` | Over 56.5 points scored wins against Over 35.5 points scored | Over 56.5 points scored wins against Over 35.5 points scored, Over 35.5 points scored and Over 32.5 points scored collectively score under 41.5 points |
| MAKE_PLAYOFFS | - | 33 | 0 | `KXNFLPLAYOFFC-27NYJNYG-Y` | Will New York J and New York G both make the playoffs in the | Will New York J and New York G both make the playoffs in the 2026-27 Pro Football season? |
| DIVISION_WINNER | - | 32 | 0 | `KXNFLAFCSOUTH-27-TEN` | Will Tennessee win the Pro Football AFC South Division? | Will Tennessee win the Pro Football AFC South Division? |
| CONFERENCE_WINNER | - | 32 | 0 | `KXNFLAFCCHAMP-27-TEN` | Will Tennessee win the Pro Football AFC Championship? | Will Tennessee win the Pro Football AFC Championship? |
| WEEK_EVENT | - | 32 | 0 | `KXNFLPRIMETIME-27-WAS` | Pro Football: Teams with 5+ Primetime Games | Pro Football: Teams with 5+ Primetime Games |
| SUPER_BOWL_WINNER | - | 32 | 0 | `KXSB-27-WAS` | Will Washington win the 2027 Pro Football Championship? | Will Washington win the 2027 Pro Football Championship? |
| FIRST_TD_SCORER | FULL | 31 | 0 | `KXNFLFIRSTTD-26SEP10SFLAR-NONE` | No Touchdown: 1st Touchdown | no touchdown |
| PLAYER_AVAILABILITY | - | 23 | 0 | `KXNFLWEEKCOMPETE-26W1-ADONALD99` | Will Aaron Donald play in a Pro Football game in Week 1? | Will Aaron Donald play in a Pro Football game in Week 1? |
| NEXT_TD_SCORER | FULL | 0 | 22 | `KXNFLNEXTTD-26FEB06SEANETD4-SEASDARNOLD14` | Seattle vs New England: 4th TD: Sam Darnold | Seattle vs New England scores next TD |
| SEASON_TEAM_H2H | - | 22 | 0 | `KXNFLH2HWINS-27ATLNYG-NYG` | Will New York G record more wins than Atlanta in the 2026-27 | Will New York G record more wins than Atlanta in the 2026-27 Pro Football regular season? |
| BOTH_TEAMS_SCORE | 4Q | 16 | 0 | `KXNFL4QBTTS-26SEP14DENKC-Y` | Both teams to score in the 4th quarter | Both teams to score in the 4th quarter |
| BOTH_TEAMS_SCORE | 1Q | 16 | 0 | `KXNFL1QBTTS-26SEP14DENKC-Y` | Both teams to score in the 1st quarter | Both teams to score in the 1st quarter |
| BOTH_TEAMS_SCORE | 2Q | 16 | 0 | `KXNFL2QBTTS-26SEP14DENKC-Y` | Both teams to score in the 2nd quarter | Both teams to score in the 2nd quarter |
| BOTH_TEAMS_SCORE | 3Q | 16 | 0 | `KXNFL3QBTTS-26SEP14DENKC-Y` | Both teams to score in the 3rd quarter | Both teams to score in the 3rd quarter |
| TEAM_STAT | - | 9 | 0 | `KXNFLNEXTINT-26NYJ-W8` | Will the New York J Pro Football team record an interception | Will the New York J Pro Football team record an interception after issuance and before Week 8 of the 2026-27 season? |
| GAME_STAT | FULL | 5 | 0 | `KXNFLLONGESTFG-27-70` | Longest field goal in 2026-27 regular season: 70+ yards | Longest field goal in 2026-27 regular season: 70+ yards |

Not shown: the 2025 season archive in the historical tier (KXNFLGAME 666 markets; KXNFLSPREAD and KXNFLTOTAL > 3,000 each; props to be enumerated by the backfill job).

## Capture tiers
FULL_MICROSTRUCTURE (104 series: every single-game family) → quotes every run + order book within 72h of kickoff + full trade tape. LIGHT (166: season wins, futures, awards with liquidity, weekly leaders, parlays) → quotes every run. DAILY (122: business/coach/draft/misc) → one quote per day. Nothing is NOT_CAPTURED yet; exclusions must carry a reason.
