# NFL operating policy (authoritative)

**This is the one authoritative statement of how the NFL desk operates.** Where `RUN_NFL.md`, `DECISION_STANDARD.md`,
`PREFLIGHT.md`, `AIRTABLE_BRIDGE.md`, `OPERATIONS.md` or `config/risk_policy.json` disagree with it, this document is right and
the other needs fixing. Those documents keep their mechanics (gates, fee arithmetic, ledger rules); they no longer own the staking
numbers, the Airtable assumptions or the operating loop.

Owner: the person who places the bets. Effective 2026-10-25. Replaces the `pilot-2026-v1` settings (0.5%-of-bankroll units, 2U per
position, the "6-8 week pilot" and the Airtable operating foundation), which were never the owner's preferences.

---

## 1. Staking: the owner's preferences

| | |
|---|---|
| 1 unit (1U) | **$75**, fixed (not a bankroll fraction) |
| Permitted stakes | whole units, **1U to 5U** ($75 to $375) |
| Maximum single stake | **5U = $375** |
| Bets per game | zero is a valid answer; nothing obliges a number of bets or a bet on every game |
| Correlated bets | assessed as **combined exposure** (one budget per game thesis / correlation group) |
| Larger stakes | allowed for a defensible, highly confident recommendation; see the evidence ladder (section 4) |
| Model-market disagreement | **never** a reason for an aggressive stake |

Enforced in `config/risk_policy.json` (`owner-2026-10-v1`) and `nfl_edge/handicap/risk.py`, pinned by `tests/test_owner_policy.py`
and the source hashes in `tests/test_incumbent_unchanged.py`:

| limit | value | note |
|---|---|---|
| fixed unit | $75 | `fixed_unit_dollars`; independent of any bankroll |
| stake increment / minimum | 1U / 1U | a position that cannot be 1U is **rejected**, not taken at a token size |
| per position | 5U | was 2U in the pilot |
| per game (combined) | 8U | pilot: 4U (2x the position cap); now 1.6x it, so a bigger stake never loosens game protection |
| per correlation group | 6U | pilot: 3U (1.5x); now 1.2x. Kept **tighter** than the game cap on purpose |
| per slate | 25U ($1,875) | pilot: 12U (6x); now 5x. When a bankroll is supplied the **more binding** of this and 10% of bankroll |
| per position vs bankroll | 3% | applies **only** when a bankroll snapshot is supplied; otherwise the report says `NOT_EVALUATED` instead of assuming one |
| grade caps | A+ 5U, A 4U, A- 3U, B+/B 2U, B-/C 1U | ceilings, not targets; the evidence ladder decides what a candidate reaches |

The aggregate caps (8 / 6 / 25U) are **not the owner's words**: the owner gave the 1U-5U range. The three aggregate caps are this
policy's translation of the old protection into the new units, sized so that each is a smaller multiple of the single-stake cap than
the pilot's was, and so that the 2026 season's actual weekly outlay (about 12U to 54U gross, much of it recycled capital) is not
mistaken for simultaneous risk. They are config values; change them in one reviewed edit if the owner wants different ones. Nothing else
in the safety stack moved: quote and book freshness stay at 15 minutes, the full-position depth walk, side-correct executable ask,
fee-schedule verification (45 days), net-EV > 0 after fees, cumulative exposure across runs, fail-closed on missing evidence.

Kelly and edge-proportional sizing remain **off**. No model here has earned the calibration they would need.

## 2. Operating policies

1. **All executable Kalshi NFL markets are accounted for.** Every listed contract ends in exactly one coverage state (`docs/RUN_NFL.md`,
   `nfl_edge/handicap/coverage.py`); `silently_omitted` must be 0 and the card builder refuses to run if the coverage invariants are not true.
2. **Game theses and matchup analysis come first.** A bet is the best expression of a football thesis, not a model-market gap.
3. **History is used now.** The 2025 season (Kalshi top-of-book at ten horizons) and 2026 to date are replayed immediately
   (`docs/research/STRATEGY_REPLAY.md`); there is no waiting period before a hypothesis may be tested. Out-of-sample discipline, not the
   calendar, decides what counts. This does **not** relax `PRODUCTION_ELIGIBILITY.md`: a *model's* authority over real money still needs its own prospective evidence (a backtest, however good, never promotes anything). What changed is that hypotheses and strategies are tested on the existing records now instead of waiting for a pilot to accumulate.
4. **Actual wagers and settlements come from the Kalshi router and the canonical NFL ledger** (`handicap-data`: `imported_wagers`,
   `wager_settlements`), immutable. Nobody reports a win or a loss by hand; the postmortem and the diagnosis rebuild from the ledger
   (`.github/workflows/actual-wagers.yml`, every 6 hours).
5. **Airtable is not the operating foundation.** See section 8 for what still touches it and what replaces it.
6. **Three things stay separate, always:** *actual wagers* (owner fills), *hypothetical selections* (card lines and replays), *research
   projections* (Shadow v2, coherent simulation, player arms). No report adds them together; no research number is a fair value.
7. **No automatic bet placement.** Kalshi account interaction is read-only (the client has no order surface; `tests/test_card.py` and
   `tests/test_preflight_no_weakening.py` pin it). The card says BET only when the real preflight approved the line.

## 3. RUN NFL: what happens when the owner says "RUN NFL"

```
A discovery      packet + analysis manifest: every game, every contract; coverage invariants checked; stale or incomplete data FAILS CLOSED
B deep review    dossiers/<game>.json for every unstarted game; triage ORDERS the review and never removes a game
C theses         the analyst writes a thesis per game that deserves one (schema below); a game without one is TRIAGED_NO_THESIS (a PASS)
D scripts        nine scripts (favourite controls / competitive / underdog outperforms x low / normal / high scoring), from the same draws as the fair value
E expression     every derivable contract, both sides, on one footing, plus declared contracts; ranked by conservative edge per unit of payoff risk
F challenge      ten questions; any OPEN or FAIL means PASS
G staking        evidence ladder -> risk policy (game / group / slate caps incl. the owner's open positions) -> preflight (depth, fees, quote age)
H card           Game | Bet | Current price | Bet up to | Stake | Reason, then every game's terminal state, then what was rejected and why
```

Commands (the card builder reads and computes; it places nothing):

```bash
# inputs: handicap-reports/latest (packet.json, analysis/), market-data (live preflight), handicap-data, the nflverse schedule
python3 scripts/handicap/run_card.py --reports-dir /tmp/hr/latest --theses theses.json \
    --schedule-csv /tmp/md/data/kalshi/capture/schedule_cache.csv --handicap-root /tmp/hd --market-data /tmp/md --out /tmp/card
# a replay of an old snapshot at its own capture time (nothing executable):  --mode REHEARSAL
```

`latest/dossiers/index.md` (written by `RUN NFL`, `scripts/handicap/build_dossiers.py`) is the review order; `dossiers/<game_id>.json` is the
football brief. **Each feature is labelled MEASURED, SIMULATION or UNAVAILABLE.** Not captured, and therefore never reported or implied:
coverage scheme and assignments, blitz rate, boundary/slot and route data, inside/outside run splits, run fits, OL pass/run-block grades and
pass-rush win rate, snap shares per play, travel and time zone, score-state paths. Measured and used: schedule-adjusted offence-v-defence
splits (pass, run, neutral-script, early-down, explosive, success, sack), quarterback EPA clean vs under pressure beside the opposing
defence's QB-hit and sack rates, OL injury lists, rest days, weather and roof, injuries and availability changes, simulated team volume by
game state and simulated player opportunity **with its uncertainty**.

**Timing on a Sunday.** The conductor refreshes the packet at T-24h, T-6h, T-90m and T-30m of each kickoff cluster. The live card is run
against the newest packet **after the inactive list** (about 90 minutes before the kickoff of the games it covers), because a Questionable
player is `OPEN` under C5 until then and the option value of waiting is not spent. The early game (the 9:30 a.m. ET kickoff, 13:30Z) is run
first and on its own; the 1 p.m., 4 p.m. and night games follow their own inactive lists. A card whose capture is more than 15 minutes old
at its decision time is BLOCKED, not stale-but-usable.

**Parlays and teasers.** Not produced. Kalshi's multi-leg combo series (`KXMVE*`) exist and 37 of the owner's 199 positions are combos, but the engine can
neither derive a combo's price nor its legs' correlation, so a combo has no defensible fair value here; and a Stanford Wong teaser is a sportsbook
product with no Kalshi equivalent. A future optional section needs the executable combo quote, a correlation estimate and the exact settlement
semantics before any price is shown. On the 2026 ledger the combos cost 4.2% in fees and returned -39% on 37 positions.

### The thesis record

```json
{ "thesis_id": "2026_07_NYG_HOU::T1", "game_id": "2026_07_NYG_HOU", "statement": "...", "short_reason": "<= 150 chars for the card",
  "drivers": ["HOU_SIDE", "NYG_SCORING_DOWN"],                         // theses that share a driver share one correlation budget
  "shift": {"home_margin": [0.5, 2.0], "total": [-1.5, 0.5]},          // a RANGE, in points, on the market centre (home = the home team)
  "candidates": [ {"ticker": "...", "side": "YES|NO", "fair": {"low": 0.70, "high": 0.80, "basis": "..."},   // fair = P(the SIDE YOU BUY wins)
                   "usage": {"projected_opportunity": "..", "recent_usage": "..", "role_stability": "..", "teammate_context": ".."},   // player props only (C5)
                   "script_results": {"COMPETITIVE|NORMAL_SCORING": "WIN", "FAVORITE_CONTROL|NORMAL_SCORING": "WIN"},  // required for a declared contract (C6)
                   "winning_scripts": 5, "major_scripts": 6} ],   // declared fair ranges for contracts the engine cannot derive
  "evidence": {"measured": [{"ref": "...", "claim": "...", "opponent_adjusted": true, "market_unmoved": false}],
               "simulation": [], "hypotheses": []},                    // measured evidence, simulation output and qualitative hypotheses stay apart
  "challenge": {"fail_modes": ["..", ".."], "market_already_priced": "..", "matchup_check": "..", "uncertainties": [".."]},
  "corroborations": [{"kind": "TACTICAL_DATA", "evidence": ".."}],
  "blocked_reason": "..." }                                            // an explicit PASS by thesis (source conflict, status unresolved)
```

### Fair value: what may be called one

* **DERIVED**: moneyline, every spread rung, game total, both team totals from the incumbent's market-centred joint simulation
  (`nfl_edge/pricing/game_env.py`: the market's own centre plus historical (margin, total) residual pairs) **shifted by the thesis range**,
  and widened by the engine's measured disagreement with the market when no thesis is applied (its noise floor). All four corners of the
  shift range are priced; the conservative end is what is traded on. Reproducible and consistent across expressions.
* **DECLARED**: the analyst's stated range for a contract the engine cannot derive (player props, periods), with a named basis. Recorded as the
  analyst's, never as a model probability.
* **NONE**: `NO_DEFENSIBLE_FAIR_ESTIMATE`. Shown for context, **cannot be ranked, staked or recommended.** No number is invented to fill a column.
* Shadow v2, the coherent simulation and the player arms are **context**. They are `RESEARCH_ONLY`/`WATCH` in `PRODUCTION_ELIGIBILITY.md`, and a
  research view never becomes authority by appearing beside a row. `BOARD_V2` is WATCH; no arm or family is LIMITED or TRUSTED.

## 4. The stake ladder (`nfl_edge/handicap/staking.py`)

A candidate receives the highest tier whose every requirement it meets, measured at the **conservative end** of its fair range, after fees,
at the price actually payable.

| tier | requires (cumulative) |
|---|---|
| 1U | complete thesis; challenge cleared; net edge >= 2.0c at fair_low; full stake executable; price <= ceiling |
| 2U | net edge >= 4.0c; wins in >= 3 plausible scripts and does not lean on a single one; fair range <= 0.20 wide |
| 3U | net edge >= 5.5c; **one** independent corroboration |
| 4U | net edge >= 7.0c; **two** corroborations; the market family is LIMITED or better |
| 5U | net edge >= 9.0c; **three** corroborations; the family is TRUSTED (**unreachable today by design**) |

Corroborations that count: `INCUMBENT_AGREES` (deployed incumbent prices the contract, agrees after fees, family WATCH+), `LINE_MOVE_TOWARD_US`
(price moved >= 1c toward us with a tight book), `REPLAY_SEGMENT` (non-negative net ROI and CLV in that family and price bucket in the historical
replay), `TACTICAL_DATA` (a **measured** availability or tactical fact marked market-unmoved). Never corroborations: Shadow v2 or any research arm,
the coherent simulation, a model-market gap of any size, the analyst's own confidence.

Caps at every tier: a model-market gap above 10 points caps the contract at 1U (the market won where the football-only model disagreed by more than
0.10 on every scored family); a fair range wider than 0.20 steps down a tier; a single-script thesis cannot exceed 1U.

## 5. The independent challenge (`nfl_edge/handicap/challenge.py`)

Ten items; any **OPEN** or **FAIL** is a PASS. C1 failure modes (two or more, concrete) · C2 has the market already priced it (the price history is
checked against the answer) · C3 matchup self-check with measured evidence · C4 opponent-adjusted statistics (raw statistics fail) · C5 player usage
(availability resolved, usage record complete; a Questionable player is OPEN until the inactive list) · C6 single-script dependence (computed from the
script draws) · C7 price compensates for uncertainty (>= 2.0c net at the conservative end) · C8 a superior expression exists (computed) · C9 quote and
book current (<= 15 min; a replay flags instead) · C10 duplicates exposure already on the book (the owner's unsettled positions from the ledger).

## 6. Provenance and the learning loop

* **Every owner fill is owner-selected unless a recorded recommendation links to it.** The `handicap-data` ledger holds no real recommendation
  today (three TEST_ONLY records), so none of the 209 wagers in the 2026 ledger can be called a model or ChatGPT pick, and none will be.
* `nfl_edge/handicap/attribution.py` links a fill to a recommendation only when ticker, side, time window (after the recommendation, before kickoff)
  and ceiling all agree and the recommendation is unique; otherwise the fill is `NO_RECOMMENDATION_ON_RECORD`, `OUTSIDE_RECOMMENDATION_TERMS` or
  `AMBIGUOUS_RECOMMENDATIONS`. Cashouts are position management and are never matched as new theses (`position_lifecycle.py`).
* Recommendation identifiers are deterministic: `rec_` + sha1(packet sha, thesis id, ticker, side). Each record carries the packet sha, run id, thesis
  id (a `thesis:` tag), the fair range (`probability_low/mid/high` for the side taken), the ceiling and the stake. PASS decisions are recorded with the
  same fidelity (`scripts/handicap/validate_recommendations.py --write`, the existing gated write path to `handicap-data`).
* After games settle, `actual-wagers.yml` rebuilds the postmortem (episodes, CLV, fees, risk) and the **redacted** diagnosis
  (`nfl_edge/handicap/wager_diagnostics.py`): ROI by week / family / entry price / timing / stake size, CLV (canonical, plus a labelled capture fallback),
  a fair-price null for variance, concentration, correlated exposure, cashouts, and a verdict (`SUPPORTED`, `CONSISTENT`, `NOT_SUPPORTED`,
  `NOT_DISTINGUISHABLE`, `NOT_MEASURABLE`) with its evidence for each of ten candidate causes. No one files a postmortem by hand.

## 7. Privacy

`chmoses98/nfl-edge-finder` is a **public** repository, and so are its data branches. The router keeps the owner's fills private in its own repo, but
delivers each fill (ticker, price, size) to `handicap-data` here, and the actual-wager postmortem files on `market-data` carry stakes and P&L.
That is how the system was built and this change does not alter it. What this change guarantees: the **new** published diagnosis is redacted
(ratios, counts and z-scores only), nothing prints a stake, price or ticker to an Actions log, and the card builder never writes the owner's open
exposure beyond a unit count. **If the owner wants the ledger private, the decision is theirs and the fix is infrastructural** (make the data
branches private or move the ledger); see section 9, item 1.

## 8. Airtable: what still depends on it, and what replaces it

Airtable was the transport between a ChatGPT session that could write Airtable but not run scripts, and the preflight worker. It is **not** on the
RUN NFL path (`scripts/ci/assert_no_airtable.py` proves it) and the card path above does not touch it.

| component | still Airtable? | replacement / disposition |
|---|---|---|
| `run-nfl.yml`, `shadow-price.yml`, `horizon-conductor.yml` (packet, dossiers, card inputs) | no (asserted) | unchanged |
| `scripts/handicap/run_card.py` (thesis -> card), `preflight_candidate.py` (CLI), `validate_recommendations.py --write` | no | the GitHub-native path: `preflight_batch` against a market-data checkout and the `handicap-data` ledger, then the gated write |
| `sync-handicap-airtable.yml` (12-hourly importer, `sync_airtable.py`, `airtable_bridge.py`) | yes | **superseded**; left in place and inert without the secret. Retire once the owner confirms no Airtable rows are still being written |
| `preflight.yml` (10-minute worker, `preflight_airtable.py`, `preflight_budget.py`, `approval.py` signing) | yes | **superseded** for the owner's loop by `run_card.py` + `preflight_candidate.py`; the worker remains the only path for a ChatGPT runtime that cannot run scripts (its approvals are signed and replayable) |
| `preflight-approval-audit.yml`, `audit_preflight_approval.py`, `replay_preflight_evidence.py` | yes | audit tooling for already-issued Airtable approvals; keep until none are outstanding |
| `docs/AIRTABLE_BRIDGE.md`, parts of `DECISION_STANDARD.md`, `PREFLIGHT.md`, `OPERATIONS.md` | describe it | each now carries a pointer to this document |

Nothing was deleted: the Airtable path is deprecated, not removed, so that no approval already issued stops being auditable.

## 9. What is not validated, and standing risks

1. **Privacy of the ledger** (section 7) is an open decision for the owner.
2. **Profitability is unproven.** On the 2026 ledger the result is what fair prices plus fees imply (`NOT_DISTINGUISHABLE`), and no model is
   LIMITED or TRUSTED. The system exists to find, price and size bets that have a *defensible* chance of positive net return, and PASS when it cannot.
3. Canonical CLV for weeks 5-7 is missing because `shadow-v2-settle.yml` has hit its 120-minute job limit on every scheduled run since at least
   2026-10-23 (the "Settle every ready game" step is cancelled), so no settlements or closes are published after week 4. The diagnosis falls back to
   the captured pre-kickoff quote, labelled `CAPTURE_FALLBACK`. Fixing the settlement job is separate work.
4. Historical depth does not exist before 2026-09-04; replays assume top-of-book fills (`STRATEGY_REPLAY.md`).
5. `fairvalue.py` prices through the incumbent's game-centre simulation; its disagreement with the market with no thesis (family rms 1-4 points of
   probability) is carried into every range, and the 4 corner pricing means a thesis must be worth about two points of margin or total to clear fees.
   That is a deliberately high bar, not a bug.

## 10. File map

| what | where |
|---|---|
| staking policy | `config/risk_policy.json`, `nfl_edge/handicap/risk.py`, `nfl_edge/handicap/staking.py`, `tests/test_owner_policy.py` |
| card builder | `nfl_edge/handicap/card.py`, `scripts/handicap/run_card.py` |
| fair value / expression / challenge | `fairvalue.py`, `expression.py`, `challenge.py` (all `nfl_edge/handicap/`) |
| dossiers and triage | `dossier.py`, `scripts/handicap/build_dossiers.py` (run by `RUN NFL`) |
| actual-wager accounting and diagnosis | `actual_wager_postmortem.py`, `position_lifecycle.py`, `wager_diagnostics.py`, `schedule_kickoffs.py`, `attribution.py` |
| historical replay | `nfl_edge/research/strategy_replay.py`, `docs/research/STRATEGY_REPLAY.md` |
| rehearsal | `docs/rehearsal/2026-10-25/` |
