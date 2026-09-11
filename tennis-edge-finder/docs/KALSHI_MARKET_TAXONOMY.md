# Kalshi tennis market taxonomy (discovered 2026-09-11, snapshot 20260911T063759Z)

Discovery is dynamic: `scripts/kalshi/discover_tennis.py` pulls the full series catalogue (13,971 series),
classifies tennis by the exchange's own `Tennis` tag (with title/prefix nets for untagged series), then
enumerates events, markets (open/unopened/closed/settled) and the archived tier per series. The
machine-readable inventory is `config/kalshi_tennis_series.json`; `tennis_edge/kalshi/families.py` is the
series -> family registry; `tennis_edge/kalshi/markets.py` parses each market's `rules_primary` into a payoff.

**Invariant (gate TENNIS-1/2/3):** ACTIVE_KALSHI_TENNIS_MARKETS = DISCOVERED = NORMALIZED (parsed or explicitly
UNSUPPORTED) = PROJECTED (for projectable families). Unknown series or unparsed markets are hard failures.

## Universe size at snapshot
143 tennis-tagged series; 61,592 live-tier markets (404 open at 06:38Z, 129 of them in non-projectable
families) + 103,962 archived markets. Parse status over all 165,554: 163,553 PARSED, 1,855 explicitly
UNSUPPORTED family, 146 UNPARSED (0.09%, almost all 2025-vintage same-surname tickers).

## Families (payoff scope)
| family | scope | series (examples) | markets live+hist | payoff | projectable |
|---|---|---|---|---|---|
| MATCH_WINNER | match | KXATPMATCH, KXWTAMATCH, KXATPCHALLENGERMATCH, KXWTACHALLENGERMATCH, KXITFMATCH, KXITFWMATCH, KX*DOUBLES, KXMIXEDDOUBLESMATCH, KXUNITEDCUPMATCH, KXDAVISCUPMATCH, exhibitions; legacy 2025 per-tournament series (KXATPMAD, KXFOMEN, ...) | 118,708 | P(subject wins \| ball played) | yes (singles); doubles baseline only |
| SET_WINNER | match | KXATPSETWINNER, KXWTASETWINNER | 19,660 | P(subject wins set n) | yes |
| EXACT_SET_SCORE | match | KXATPEXACTMATCH, KXWTAEXACTMATCH | 9,662 | P(final set score = x-y for subject) | yes |
| TOTAL_GAMES | match | KXATPGTOTAL, KXWTAGTOTAL, KXATPGAMETOTAL | 6,918 | P(completed games > line) | yes |
| GAME_SPREAD | match | KXATPGSPREAD, KXATPGAMESPREAD | 5,671 | P(subject games - opponent games > line) | yes |
| TOTAL_SETS | match | KXATPTOTALSETS | 348 | P(sets played > line) | yes |
| SET_SPREAD | match | KXATPSSPREAD | 204 | P(set differential > line) | yes |
| TIEBREAK_OCCURS, ANY_SET_WINNER | match | KXATPTIEBREAK, KXATPANYSET (no markets yet) | 0 | from DP tiebreak / set-score distribution | yes |
| PLAYER_ACES | match | KXATPACES, KXWTAACES | 110 | aces >= n | no (no ace model) |
| GAME_WINNER_INPLAY | in-play | KXATPS1GWINNER..S5, KXATPGWINNER | 480 | game g of set s | no (in-play) |
| TOURNAMENT_WINNER | tournament | KXATP, KXWTA, slam/1000 winner series (KXUSOMENSINGLES, KXIWMEN, ...) | 2,787 | reach title | draw DP built (`tennis_edge/futures/draw.py`), draw feed not wired |
| ROUND_ADVANCE / ROUND_OF_ELIMINATION | tournament | KXATPADVANCE, KXWTAADVANCE, KXWTAROE | 541 | reach round | as above |
| NATIONALITY_*, SET_SWEEP, COMBO_TOURNAMENT_WINNERS, TEAM_* | tournament combos | KXATPNATSTAGE, KXATPWTA, KXDAVISCUP, KXUNITEDCUP ... | ~170 | derived from draws/team ties | no |
| SEASON_RANKING/QUALIFICATION/MAJORS, PLAYER_PARTICIPATION, CAREER_OR_NOVELTY | season/other | KXATP1RANK, KXATPFINALSQUAL, KXATPGRANDSLAM, KXATPRETURN, KXALCARAZCOACH, ... | ~180 | not priceable from match distributions | no |
| NOT_TENNIS | -- | KXPICKLEBALLMATCH (tagged Tennis by the exchange) | 2 | -- | refused explicitly |

## Record grammar (verified)
* Event ticker `<SERIES>-<YY><MON><DD><CODE_A><CODE_B>[dup digit]`; market suffix `<CODE_subject>[strike]`.
  Singles codes are 3 letters, doubles 5-6 letters per team. A same-surname pairing appends the duplicate
  digit to the SECOND competitor (`KIMKIM2-KIM` vs `-KIM2`). The parser cross-checks the rules-text names
  against the ticker side and fails closed on disagreement.
* `custom_strike.tennis_competitor` / `tennis_doubles_competitor` carry the exchange's competitor UUID --
  a stable identity key we cache against canonical ids (`config/kalshi_competitor_map.json`).
* `rules_primary` names both competitors (opponent abbreviated), the competition and the round; `floor_strike`
  duplicates the numeric line and is cross-checked against the rules text.
* `occurrence_datetime` = scheduled start (UTC); `expected_expiration_time` is usually equal to it;
  `close_time` = when the market actually closed (after the winner was declared). There is **no first-ball
  timestamp** anywhere in the API.
* Settlement: `result` in {yes, no, scalar}; `settlement_value_dollars`; `expiration_value` text (winner name,
  "Alexander Zverev 3-0", the total, "p1=19 p2=3" for aces, "No").

## Settlement rules (from `product_metadata.important_info`, harvested into config/kalshi_settlement_rules.json)
* ATP/WTA tour match series: no ball played -> ALL markets incl. set winners resolve to a **fair price**;
  withdrawal/forfeit after the match begins -> that player resolves **No** for the match market; derivative
  markets that are already determined settle, the rest resolve to fair price.
* ITF singles/doubles: no ball played -> **$0.50**; retirement after start -> retiring player No.
* Derivative series (totals, spreads, exact, set winner): retirement -> settle what is unconditionally
  determined, else Fair Market Price.
* 118 of 143 series carry no important_info text (tournament winner series etc.) -> rules known only from
  the contract PDFs (downloaded, not parsed) and observed settlements.
* Observed: 1,836 live-tier and 2,931 archived finalized markets settled `scalar` (fair price), i.e. ~3% of
  all tennis contracts never had a binary sporting outcome from the exchange's point of view.

## Fees
`fee_type = quadratic_with_maker_fees` on KXATPMATCH, KXWTAMATCH and the Grand Slam singles winner series;
`quadratic` (taker only) on the other 132; `fee_multiplier = 1` everywhere. See `tennis_edge/pricing/fees.py`.
