# Full-board research: what the whole Kalshi board teaches, without hindsight

> RESEARCH ONLY. Nothing here selects, gates, sizes or authorises a wager. Every row carries
> `betting_authorized: false`, and `tests/test_board_research.py` pins that the gates, risk, wager-risk, preflight,
> approval and evaluation modules import none of it.

## 1. Why

Weeks 1–3 captured the whole NFL board: 71,753 markets in discovery, 38,919 of them game contracts of the 48
Weeks 1–3 games. The arm evaluations score the 3,665 latest-pregame contracts the incumbent prices; the Shadow v2
export is one row per (projection, arm, snapshot) and is built per week before the week settles. Neither answers
**"what did the board teach us?"**, which is a question about the market rather than about one of our models.

## 2. The table (`nfl_edge/research/board.py`, `scripts/research/board_research.py`, `board-research-1.0.0`)

One row per **contract × canonical horizon** (T-24h, T-6h, T-90m, T-30m, latest_pregame) for every contract that
maps to a requested week's game.

* **Raw snapshots stay raw.** The capture (`data/kalshi/capture/<day>/<run>.quotes.jsonl`) is the raw store; the
  table never copies it. Each row counts its contract's pregame snapshots (`n_pregame_snapshots`) and the
  post-kickoff rows ignored.
* **One observation per horizon, the close rule generalised.** The state at a horizon is the last price change
  strictly before the cutoff, confirmed by the last capture run before the cutoff that fetched the series while the
  contract was open (`close.py`'s rule; tiers on the confirmation age). latest_pregame *is* the canonical close; on
  Weeks 1–3 it reproduces the arm evaluations' close mid for all 3,665 contracts exactly, and their settlement for
  all 3,665. A price no run confirmed within 24 h is `UNCONFIRMED_AT_HORIZON`; a contract not yet quoted is
  `NOT_LISTED_YET`; a closed one is `NOT_OPEN_AT_HORIZON`.
* **Settlement, two tiers that never mix.** `FOOTBALL_PROVEN`: the production engines on the question the
  production semantics engine reads from the discovery record (`settle_v2.settle_projection`, which defers to
  `settle.settle_observation` for player statistics). `EXCHANGE_TERMINAL`: the exchange's own terminal settlement for
  a contract football cannot settle (first-TD, race-to-N, team stats, fantasy points, longest plays, unresolved
  players, ...), kept as a separate tier and out of the canonical analysis. A football settlement the exchange
  contradicts is flagged and excluded, never overwritten (Weeks 1–3: 42, all `2H` contracts of one overtime game and
  `GAME_PLAYER_LEADER`).
* **Fees** from the committed schedule (`execution/fees.py`) as of the observation: the marginal per-contract
  taker fee (the quadratic a multi-contract order converges to; used in returns) and the one-contract fee rounded up
  to the cent (on the row). Returns are `payout − ask − fee` per contract, both sides.
* **Structure**: ladder id (game, family, period, subject, statistic), rung index, the main ("headline") rung (the
  two-sided rung nearest 50c), offset and distance from it, monotone violations.
* **Game environment** from the board's own full-game ladders at that horizon (ladder medians of both teams' spread
  ladders, the total ladder, the team-total ladders), never the schedule's consensus line, which is a closing
  number. Favourite / underdog, spread-magnitude, total and team-implied-points bands.
* **Research context, point in time**: the three-arm DATA_ONLY / HYBRID readings and the incumbent player projection
  known strictly before the cutoff (only anatomy rows computed before kickoff — autopsy-1.1.0's rule), the model–mid
  disagreement, P(plays), availability, a transparent role-certainty proxy (HIGH: P(plays) ≥ 0.9 and ≥ 8 prior games;
  LOW: P(plays) < 0.75 or < 4), movement since T-24h, CLV to the close.

**Memory.** One streaming pass over the capture straight out of git objects (`git cat-file --batch`): a capture day
is ~0.5 GB as JSON and ~10 MB packed, so nothing is checked out. Other weeks' rows are rejected before parsing.
Weeks 1–3: 3,229 quote files, 9.7 M lines, 38,794 contracts, 193,970 rows, ~190 s, ~1 GB peak RSS.

## 3. Coverage (`board_coverage.json`)

A contract-level funnel per week × family at the primary horizon, and a placement of every discovery market.
Weeks 1–3:

| stage | contracts |
|---|---|
| discovered, mapped to a Weeks 1–3 game | 38,919 |
| captured pregame | 37,069 |
| settled (either tier) | 37,069 |
| settled from football | 29,508 |
| price confirmed at latest pregame | 29,508 |
| executable quote | 29,508 |
| fee known | 29,492 |
| **analysed** | **29,450** |

Every contract that leaves the funnel carries its reason (1,725 never quoted before kickoff, 125 discovered but
never captured, 7,561 exchange-only by family / statistic / identity, 42 contradicted, 16 without a fee …). The rest
of the discovery universe: 16,108 non-game markets (season, futures, awards, leaders), 6,432 later-week games,
10,294 preseason / prior-season game markets.

## 4. The conditional miner (`nfl_edge/research/board_miner.py`, `board-miner-1.0.0`)

**Planned slices only** (S01–S18 in the module, the same every week): family × side × price; rung offset; total
environment; team-total role; spread magnitude × role; player stat × price / role certainty / environment / position
/ availability / model disagreement; DATA_ONLY disagreement × price; movement since T-24h; period and derivative
families; and the owner's leads restated in their own terms (by quoted mid, not ask). Every cell is reported, flat
and negative ones included.

Per cell: contracts, distinct games, weeks and ladders; mean price, event rate, calibration vs the ask, **mid bias**
(event rate − the side's mid: is the market's fair price wrong?) and **return at the ask** after fees (is it
exploitable?), CLV where defined, by-week values and the cell with each week held out.

Safeguards: game-clustered bootstrap (games resampled whole); a binomial floor for rare outcomes (fewer than 5
events or non-events: never narrower than a Wilson interval with one effective observation per game); small cells
(< 20 games, < 2 weeks or < 40 contract-sides) are `DESCRIPTIVE_ONLY`; Benjamini–Hochberg (q ≤ 0.20) across every
tested cell of the family, with the number of cells the family would flag by chance printed beside the number
flagged; empirical-Bayes shrinkage toward zero per slice.

Statuses (discovery only): `DESCRIPTIVE_ONLY`, `NO_SIGNAL`, `UNSTABLE` (a week or a hold-out flips the sign),
`NOT_SIGNIFICANT_AFTER_MULTIPLICITY`, `CANDIDATE`. `PREREGISTERED` / `TESTING` / `SUPPORTED` / `NOT_SUPPORTED` exist
only in the hypothesis registry.

**What Weeks 1–3 say, in one paragraph.** Buying at the ask loses in almost every cell: half the spread plus the fee
costs 2–6c, and the market's mid is calibrated within noise in 845 of 901 tested cells at latest pregame. The owner's
10–20c lead is real in the arm-priced set when binned by the mid (14.7% quoted, 19.0% paid) but, clustered by game,
the mid bias is +4.4pp with an interval of −1.0 to +9.9 and Week 3 shows none of it. The cells that survive every
safeguard are mostly cost and favourite-longshot effects (player-prop NO at 80c+, longshot YES under 10c, chasing a
late move), plus two information leads: DATA_ONLY disagreement at T-24h predicting movement, and a large incumbent
player-model over view marking an underpriced YES.

## 5. Preregistered board hypotheses (`nfl_edge/research/board_hypotheses.py`)

Eleven hypotheses, `H-20261001-B01` … `B11`, registered `GENERATED` with the discovery window 2026 weeks 1–3 and
**preregistered** on 2026-10-01 at 07:33Z — before Week 4's first kickoff (2026-10-02T00:15Z, PIT–CLE), which the
registry itself enforces — with frozen, hashed thresholds and the binding future window weeks 4–18:

| id | hypothesis | metric | discovery (W1–3) |
|---|---|---|---|
| B01 | full-game YES at 10–30c mid is underpriced | MID_BIAS > 0 | +3.7pp, CI −1.5/+9.0 |
| B02 | full-game YES at 60–70c mid is overpriced | MID_BIAS < 0 | −6.4pp, CI −15.5/+3.1 |
| B03 | sides at 90c+ lose after fees | RETURN_AT_ASK < 0 | −2.2c, CI −3.7/−0.9 |
| B04 | 2–10pp DATA_ONLY disagreement at T-24h predicts movement toward it | MOVE_TOWARD_MODEL > 0.5 | 58% toward, CI 52/65% |
| B05 | adjacent yardage rungs beat the main rung | PAIRED_RUNG > 0 | +1.1c, CI −0.8/+3.1 |
| B06 | team total beats spread for an offence thesis (implied ≥ 24) | PAIRED_EXPRESSION > 0 | +10.5c, CI −9.5/+31.1 (33 games) |
| B07 | uncertain roles are priced worse than certain ones | EXCESS_BRIER_GAP > 0 | −0.5, CI −2.7/+2.0 (×100) |
| B08 | player-prop NO at 80c+ loses after fees | RETURN_AT_ASK < 0 | −3.0c, CI −4.8/−1.4 |
| B09 | player-prop YES longshots under 10c lose after fees | RETURN_AT_ASK < 0 | −1.4c, CI −2.3/−0.4 |
| B10 | chasing a > 5c pregame move (YES 10–50c) loses | RETURN_AT_ASK < 0 | −10.1c, CI −13.5/−6.2 |
| B11 | incumbent player model > 10pp over the mid marks an underpriced YES | MID_BIAS > 0 | +7.8pp, CI +2.3/+13.5 |

Supported only if the family-adjusted (Bonferroni over the hypotheses under test, α = 0.10) game-clustered interval
excludes zero on the registered side after ≥ 48 future games, 3 weeks and 60 contracts; a suggestion only, the owner
transitions the registry. The registered locator — not the current constant — defines what each hypothesis means.

## 6. Ladders (`board_miner.ladder_report`)

One ladder = one continuous-outcome thesis. Per ladder: the main rung, the best realised rung, the rung whose ask
sat furthest below the ladder's own monotone (PAV) fair curve, the best entry-to-close CLV rung, the tail slope
around the main rung and monotone violations. Aggregated by family as shares, because a ladder's realised best rung
is one draw of one outcome.

## 7. Limitations

* Weeks 1–3 are 48 games. Every reading above is hypothesis-generating.
* The exchange-only tier (7,561 contracts) is outside the canonical analysis by design; first-TD, race-to-N, team
  stats and longest-play markets therefore have no football-proven research result yet.
* The role-certainty proxy is two numbers from the incumbent's anatomy, not a role model.
* Game environment is a ladder median, not a simulation; a game without two-sided spread / total ladders at a
  horizon has `UNAVAILABLE` environment rather than a consensus fallback.
* Open-set evidence (delisting) is not consulted for horizons; confirmation relies on manifests and `last_seen`, as
  the close does without an open-set ledger.
