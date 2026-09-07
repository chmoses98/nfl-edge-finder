# The decision standard

One operating policy for the last mile: **model → market → context → packet → ChatGPT decision →
PRE-TRADE PREFLIGHT → recommendation → Airtable → delayed GitHub replay → immutable ledger → execution →
CLV → fees → P/L → scorecard.**

The order of those first two arrows is the whole point. Nothing is surfaced to the owner as a **BET** until
it has passed preflight; the twelve-hourly importer then *independently replays* the same checks and commits
the evidence. See §0.

This is the canonical document for what a real recommendation must satisfy. Where any other doc disagrees
with this one, this one is right and the other needs fixing.

---

## 0. Pre-trade preflight comes first

The decision gates were sound and, until this section existed, they ran in the wrong place.

The Airtable importer runs **every twelve hours**. That cadence is deliberate and is not changing: it is
archival transport for a decision log, and polling more often would only hide the architectural problem
rather than fix it. But it meant the operating sequence could be:

```
13:00   ChatGPT says BET
13:01   the owner places the bet
01:00   the importer runs
01:00   the gates discover the book was too thin, the fees ate the edge, or the group cap was already full
```

Every one of those findings is correct and every one is twelve hours late. A control that fires after the
money is down is an audit, not a control.

### The lifecycle

```
HANDICAP CANDIDATE
  → PRE-TRADE PREFLIGHT                 scripts/handicap/preflight_candidate.py
  → only if PASS: user-visible RECOMMENDED / BET, at the APPROVED stake
  → Airtable READY_FOR_SYNC             asserts preflight already passed
  → delayed GitHub import (12h)         independently REPLAYS the same evidence
  → immutable ledger                    recommendation + its DecisionGates record
```

A candidate that has not passed preflight may be called **PASS**, **WATCHLIST** or **CANDIDATE**. It may
**not** be surfaced as a final BET or RECOMMENDED instruction.

### One implementation, two places it runs

Preflight evaluates the candidate as the `RECOMMENDED` record it would become, and it does so by calling
`gates.evaluate_gates` — the same function the importer calls, assembled by the same
`preflight.build_context`, sized by the same `risk.report_for_batch`, on the same clock (the candidate's own
`created_at`). Nothing in `preflight.py` decides anything itself.

That is not tidiness. If the two were separate implementations, the importer's later agreement would only
tell us that the second copy agrees with itself. Because they are one implementation, the delayed run is a
genuine independent **replay**: same rules, same decision timestamp, evidence re-read from the capture stream
and committed as a `DecisionGates` record.

`tests/test_preflight.py` pins both halves — that a candidate failing depth, ceiling, fee knowledge, net EV,
identity, availability or the portfolio caps cannot reach the BET state, and that preflight and the delayed
import reach the same verdict on the same record.

### What preflight tells the owner

The stake it reports is the stake the **risk policy approved**, not the one the handicapper proposed — and
that approved size is what the depth walk and net-EV arithmetic are then run against, because that is the
position that would actually be worked. An oversized proposal is therefore an *answer* before the trade
("$10, not $500") and a *refusal* after it, since a filed record must carry the approved size.

Preflight places nothing, orders nothing, and writes nothing to the ledger. A PASS is permission for a human
to act.

---

## 1. Vocabulary

Ten quantities that are routinely confused. They are different numbers, they answer different questions, and
nothing in this system merges them.

| term | what it is | where it lives |
|---|---|---|
| **MODEL FAIR VALUE** | what the shadow model thinks the contract is worth. A quantitative input, **not** a forecast we have shown beats the market. | `model_probability`, from the shadow ledger snapshot |
| **HANDICAPPER FAIR VALUE** | what the ChatGPT layer thinks, as a band. This is the forecast the experiment is actually testing. | `probability_low` / `probability_mid` / `probability_high` |
| **DISPLAYED BET-UP-TO** | the maximum price the handicapper will pay, in the units on the Kalshi ticket. **Fees are not folded in.** | `bet_up_to_probability` |
| **EXECUTABLE ASK** | the price you would actually pay, on your side, right now. Never a midpoint. | `yes_ask` / `no_ask`; re-resolved at decision time by `nfl_edge/execution/quotes.py` |
| **ESTIMATED TRANSACTION COST** | modelled entry fee plus any stated slippage, before the trade. | `nfl_edge/execution/fees.net_executable_ev()` |
| **ACTUAL EXECUTION** | what was filled, per fill: price, stake, contracts. | one `Execution` record per fill |
| **ACTUAL FEES** | what the venue actually charged. | `Execution.fees_paid` with `fees_are_estimated=false` |
| **GROSS P/L** | payoff minus cost, before fees. Says whether the **call** was right. Always computable. | `Evaluation.gross_pnl` |
| **ACTUAL NET P/L** | gross minus the fees actually charged, **and only when every fill's charge was observed**. Says whether the **bankroll** grew. `null` otherwise — never gross standing in for net. | `Evaluation.net_pnl` |
| **ESTIMATED NET P/L** | gross minus every fee present, actual or modelled. A forecast, and named one. | `Evaluation.estimated_net_pnl` |
| **CLV** | close minus entry, signed in our direction. Says whether the **market moved toward us**. | `Evaluation.clv`, `clv_executable` |
| **CANDIDATE** | a proposal that has **not** passed preflight. May be shown as CANDIDATE / WATCHLIST / PASS. Never as a bet. | `nfl_edge/handicap/preflight.py` |
| **OUTSTANDING EXPOSURE** | what the book already carries at a decision: approved-and-unfilled *plus* filled-and-unsettled, across every earlier run. | `risk.outstanding_exposure()` |
| **CONSERVATIVE NET EV** | net executable EV less the worst-case fee-rounding residual from unknown fill fragmentation. A **cost** bound, not an edge buffer. | `NetEV.conservative_net_ev_dollars` |

### The word "edge"

Used in exactly two senses, each fully qualified, never bare:

* **`gross_edge`** — handicapper fair value minus the executable price, in probability units, *inside*
  `net_executable_ev()`. It is an input to a cost calculation.
* **`net_edge`** — the same after transaction costs.

Model-minus-market is **disagreement**, never edge. It is labelled
`DISAGREEMENT ONLY -- REQUIRES HANDICAP` in the packet, and `tests/test_negative_research_preserved.py`
fails the build if any module names such a quantity `edge`.

### CLV and fees are deliberately never merged

CLV asks whether the market moved toward us. Transaction costs ask whether the bankroll grew. A
"fee-adjusted CLV" answers neither, and would silently make a venue's fee schedule part of a forecasting
metric. Fees appear in `net_pnl` and in `net_executable_ev`. They never appear in CLV, and they never appear
in a recommendation's recorded price.

**The user-facing display does not change.** It stays:

```
Current:     56%
Bet up to:   59%
```

Never a fee-loaded probability. Cost arithmetic is a separate, separately-named calculation.

---

## 2. What a RECOMMENDED record must carry

Enforced by `nfl_edge/handicap/schema.validate_recommendation`. Every one of these **raises**; none is a
warning. A warning on an immutable record is a warning nobody reads.

**Identity and lineage** — `recommendation_id`, `created_at`, `handicap_run_id`, `packet_sha`, `season`,
`week`, `game_id`, `kickoff_utc`, `market_ticker`, `market_family`, `side`.

**Market state** — `market_timestamp`, `minutes_to_kickoff` (must be > 0), and the **side-specific
executable ask** (`yes_ask` for YES, `no_ask` for NO). A midpoint is not accepted in place of an ask.

**Handicap** — `probability_low`, `probability_mid`, `probability_high` (ordered), `bet_up_to_probability`,
`grade` (not `PASS`), a positive whole-dollar `recommended_stake`, `primary_thesis`, and non-empty
`key_supporting_factors`, `counterarguments` and `uncertainties`.

**Model and data lineage** — `support_state` and `source_freshness`. Where `support_state` is `SUPPORTED`,
also `model_version` and `model_probability`.

### The ceiling is a ceiling

If the executable ask on our side is **above** `bet_up_to_probability`, the record is **rejected**. The
ledger must never be able to say *"BET up to 0.58"* while the book is asking 0.61. Equal is fine — at the
ask is payable.

### Support state is stated, not inferred

`support_state` is one of `SUPPORTED`, `UNSUPPORTED_MODEL`, `UNSUPPORTED_RULES`, `UNSUPPORTED_IDENTITY`,
`UNSUPPORTED_GAME`, `QUALITATIVE_ONLY`.

A qualitative call on a market the model cannot price is legitimate and is **not** forced to invent model
fields. What is not legitimate is leaving it to be inferred from a null. `SUPPORTED` asserts the model priced
this market and therefore requires model lineage; anything else requires a `support_reason`.

`UNSUPPORTED_IDENTITY` can **never** carry a RECOMMENDED record — see §6.

### PASS is deliberately cheaper

`PASS`, `WATCHLIST` and `RESEARCH_ALERT` keep the light treatment. The rule deciding which side of the line a
check falls on: **does the failure mode cost money, or cost information?** Money-losing failures are errors on
RECOMMENDED. Information-losing failures are warnings.

Requiring a full market snapshot before you may record *"the price already reflects the news"* would mean the
passes never get written — and the comparison of what was taken against what was declined is the most
informative thing this ledger will ever produce.

---

## 3. Decision-time price freshness

### The clock is the DECISION, not the import

The Airtable bridge is **retrospective archival transport** on a twelve-hour cadence. GitHub ingestion is when
a decision is *filed*, not when it is *made*.

```
13:00   decision made, YES ask 0.56, recorded
01:00   importer runs. Game kicked off; the ask is gone; the book is closed.
```

Judged at 01:00 that record fails everything, which answers a question nobody asked. So every time-sensitive
gate is evaluated **`as_of` the record's own `created_at`**:

| | role |
|---|---|
| `created_at` | the exact decision timestamp. **This is the clock every market gate reads.** |
| Airtable `createdTime` | server-stamped, unforgeable proof the decision had been handed off by then. The anti-backfill bound, unchanged. |

Two rules follow, enforced in the resolvers rather than trusted:

* **Evidence after the decision is invisible.** A later capture is information the handicapper did not have;
  admitting it would rescue a bet that was stale when it was made.
* **Freshness is measured backwards from the decision.** Import latency cannot change a verdict.

`GateContext` has no `now` field at all, and `resolve_decision_quote` **raises** if the decision time is
omitted rather than defaulting to wall clock — that default *was* the bug. Only the **risk** gate is
evaluated at import time, and only because it is deterministic from the frozen batch, the recorded bankroll
snapshot and the versioned policy file: it reads no market state, so there is nothing for latency to change.

| case | verdict |
|---|---|
| valid at T, imported 12h later | **PASS** |
| quote exists only after T | not used → **FAIL** |
| fresh at T, ancient by import | **PASS** |
| stale at T, fresher later | **FAIL** |
| kickoff falls between T and import | **PASS** — it was prospective when made |
| created after kickoff | **FAIL**, as before |

### Which timestamp means "the information existed"

A capture run works through ~270 series over several minutes, so run-start and the moment a given series
actually returned are materially different. The manifest now records **`observed_at` per series**, and that is
used wherever present. Where only run-level timestamps exist, the bound is chosen per question — and both
directions round **against** the recommendation:

| question | timestamp used | why |
|---|---|---|
| did this predate the decision? | the **latest** plausible (`finished_at`) | erring late means an ambiguous capture is treated as possibly-after, and ignored |
| how old is it? | the **earliest** plausible (`started_at`) | erring early means it is treated as older than it may be |

`capture/state.json`'s `last_seen` is a **mutable, latest-only** file and cannot answer "which run last saw
this ticker as of last Tuesday". When its run postdates the decision it is simply not usable evidence, and
resolution falls through to the immutable per-run manifests — which can answer it exactly.

### Model snapshot vs executable price

The model snapshot and the executable price have **different freshness requirements**, and conflating them is
how a desk records a bet at a price that no longer exists.

| | source | may be old? |
|---|---|---|
| **Model / information snapshot** | the latest valid frozen shadow-pricing run | **yes.** A forecast does not decay on a ten-minute clock, and recomputing it at decision time would silently change the forecast the recommendation claims to rest on. |
| **Executable market price** | the freshest **confirmed** capture quote | **no.** Fifteen minutes, against a ~10-minute capture cadence. |

The recommendation preserves both: the model probability with its original snapshot lineage, and the price
recorded when the packet was built. The gate then resolves the **decision-time** quote separately and records
it in the `DecisionGates` record. Nothing recomputes the forecast.

### "Old" is not "stale"

`scripts/kalshi/capture.py` writes a quote row only when the price **changes**. A market that has not moved
in three hours has no row in the last seventeen captures and is nonetheless perfectly current — the capture
confirmed it seventeen times. Rejecting it would reject most of the board.

So two timestamps are tracked and they mean different things:

* **`quote_moved_at`** — when the price last changed. Can be arbitrarily old. **Not staleness.**
* **`confirmed_at`** — when the capture last confirmed the market was open. **This is freshness.**

Confirmation is established at the strongest level available, and the level used is recorded:

* `TICKER_LAST_SEEN` — `capture/state.json` records the run in which each ticker was last seen open. Exact.
  Preferred whenever present.
* `SERIES_COMPLETE` — the ticker's series was fetched completely in that run's manifest. Strong, but
  series-level.

A series whose fetch came back **PARTIAL** confirms nothing; resolution walks back to the last run that
succeeded.

### What the gate does

| state | meaning | RECOMMENDED | PASS / WATCHLIST |
|---|---|---|---|
| `FRESH` | confirmed inside the window, with an ask on our side | allowed | allowed |
| `STALE` | confirmed, but too long ago | **blocked** | allowed, with the stale-data reason |
| `NO_QUOTE` | current, but no ask on our side | **blocked** | allowed |
| `UNCONFIRMED` | no capture run confirms this ticker | **blocked** | allowed |

A stale quote on **one** selected market never prevents the packet being built. This is a final-recommendation
gate, not a packet gate.

The window is `--max-quote-age-minutes` on `scripts/handicap/sync_airtable.py`, default 15.

---

## 4. Fees

Two independent facts, from two sources, with two different confidences.

**Which regime applies** — `config/kalshi_nfl_series.json`, captured from the live Kalshi API. Records each
series' `fee_type` and `fee_multiplier`. Across 392 NFL series: 367 `quadratic` (taker only), 25
`quadratic_with_maker_fees`. The 25 include **every headline NFL market** — KXNFLGAME, KXNFLSPREAD,
KXNFLTOTAL, KXNFLANYTD, KXNFLFIRSTTD, KXNFL2TD — so passive entry on the markets this project studies is not
free.

**What the regime costs** — `config/kalshi_fee_schedule.json`, transcribed from Kalshi's published fee
schedule with a `primary_source` and a `verified_at`. Coefficients are configuration, not literals in code, so
a platform fee change is a reviewable commit.

### The 2026 fixed-point rounding model

A fill is charged in **three separately-named parts**, and the total is **not** `ceil(raw, $0.01)`:

| part | what |
|---|---|
| **raw quadratic fee** | `coefficient × multiplier × contracts × price × (1 − price)` |
| **trade fee** | the raw fee ceiled to a **centicent** (`$0.0001`) |
| **rounding fee** | cent-alignment — the balance change is floored to the account's precision and the shortfall charged |
| **rebate** | the overpayment accumulates **per order across fills**; once it exceeds a cent, a whole-cent rebate is issued and the accumulator drops by a cent |

```
net fee = trade fee + rounding fee − rebate        (never below zero)
```

The accumulator is the economically load-bearing part: it makes 100 small fills cost **within one cent** of a
single equivalent fill. Ceiling every fill to the next cent independently overstates a twenty-fill order by
up to twenty cents; ceiling the whole order to the next cent understates the rounding on a fragmented one.
Both change whether a marginal trade is worth doing.

All arithmetic is `Decimal`. Kalshi's documented worked example reproduces fill by fill:

```
fill 1   revenue −$0.0550, trade fee $0.0085 → balance −$0.0635 floors to −$0.0700
         rounding fee $0.0065, accumulator $0.0065, no rebate, net $0.0150
fill 2   same again → accumulator $0.0130 > $0.01
         rebate $0.0100, accumulator $0.0030, net $0.0050
```

**Pre-trade** (`entry_fee` / `net_executable_ev`) gives the economically equivalent whole-order cost, which is
what a decision needs. **Post-trade**, the exchange's own reported fee is authoritative and
`Execution.fees_paid` carries it; these functions are estimates and are labelled as such wherever recorded.

### Maker and taker multipliers: three sources, ranked, failing closed

Two multipliers exist per series and only one is in the API.

| rank | source | carries |
|---|---|---|
| 1 | **regulatory Fee Schedule** (CFTC-filed) | **both** Maker Multiplier and Taker Multiplier for listed non-standard series |
| 2 | `GET /series/{ticker}` | `fee_type` and `fee_multiplier` — the **taker** multiplier only |
| 3 | `GET /series/fee_changes` | announced future changes → builds the *next* window |

**The API object's silence about the maker multiplier is not evidence that it is unknown.** A value published
in the regulatory schedule is a known value. `KXNFLGAME` is **Maker Multiplier 1, Taker Multiplier 1**, and is
priced accordingly.

`UNVERIFIED` now means what it says: a series that *does* charge a maker fee (`quadratic_with_maker_fees`) and
is not listed in any schedule window we hold. Those, and only those, fail closed. A taker-only series has a
**known** maker multiplier of zero — not charging a fee is a fact, not an absence of information.

Rank decides who is *consulted* first. It does **not** decide a disagreement: two sources that disagree about
the same window produce **`CONFLICTED`** and fail closed, because one of them is wrong and rank does not say
which.

Every fee value preserves **series, fee type, maker multiplier, taker multiplier, source, effective time and
verification timestamp**, and schedules are looked up **as of the decision time** — a recommendation made at
13:00 is priced with the schedule in force at 13:00, not the one current when the importer runs.

Passive execution was rejected on core game markets by `research/passive` (Milestone K) — *not* by H-019,
which is the favourite/longshot hypothesis, nor by H-023, which is the still-open prospective prop-book
question. So a real recommendation is a **taker** order, and the taker path is fully known.

### Freshness is an operational control, not a documented intention

Three ranked sources were documented and only one was ever read. A hierarchy whose third source is never
ingested cannot detect the one failure it exists for: a change Kalshi has **announced** and we have not yet
modelled.

`scripts/kalshi/capture_fee_metadata.py` now reads `GET /series/fee_changes` alongside the per-series
metadata, preserves each announced change with its scheduled effective timestamp, and writes an append-only,
dated observation to `market-data` under `data/kalshi/fees/<YYYY-MM-DD>.json`. The weekly
`.github/workflows/kalshi-fee-health.yml` job runs it with `--check`.

`FeeSchedule.verification()` reads those observations and returns one of four states **as of the decision
timestamp** — a capture taken after a decision is not evidence about it, exactly as in §3:

| state | meaning | gate |
|---|---|---|
| `VERIFIED` | a window is in force and was confirmed within the policy age | pass |
| `PENDING_CHANGE` | Kalshi announced a change effective at or before this decision and no committed window covers it | **FAIL** |
| `STALE_VERIFICATION` | in force, but the last confirmation is older than `max_verification_age_days` (45) | **FAIL** |
| `NO_SCHEDULE` | no committed window covers this timestamp at all | **UNAVAILABLE** (blocks) |

Weekly against a 45-day tolerance absorbs three consecutive missed runs and does not absorb a months-old
unchecked registry. Fee schedules change on the order of once or twice a year and are announced in advance,
so a higher cadence would buy nothing.

**A change is never applied automatically.** Capture → surface → block → review. An API response must not
silently rewrite the schedule that every historical net-EV number in the ledger was computed against, so the
job fails loudly, the gate blocks affected real recommendations, and an operator commits a **new** effective
window (closing the previous window's `effective_to`). Existing windows are never edited: a past decision
keeps being priced with the schedule that was actually in force when it was made.

### Keeping it traceable

`scripts/kalshi/capture_fee_metadata.py` re-reads live per-series fee metadata, writes a dated snapshot to
`market-data`, and with `--check` exits non-zero when it disagrees with the committed registry — so a Kalshi
fee change surfaces as a failed job rather than as a quietly wrong number six weeks later. It never edits the
registry; that is a human decision.

### Net EV at or below zero BLOCKS

For `RECOMMENDED`:

| net executable EV | verdict |
|---|---|
| fee/cost state not `KNOWN` (`UNVERIFIED` / `CONFLICTED` / `DEGRADED`) | **FAIL** |
| cannot be calculated | **FAIL** |
| `<= $0` | **FAIL** |
| `> $0` but **conservative** net EV `<= $0` | **FAIL** — see below |
| conservative net EV `> $0` | this gate may pass |

This is **not** a minimum-edge rule. There is a real difference between

* *"require at least +3% edge"* — a strategy threshold, and
* *"do not knowingly record a trade worth ≤ $0 after its known entry costs"* — arithmetic.

Only the second is enforced. **No positive minimum beyond zero is invented**, and there is deliberately no
switch in the module to turn one on — a blocking rule with an off switch is a warning in costume.

The EV is computed at the **full-position VWAP** (§5), not the top ask: pricing a trade at its cheapest
contract is how a losing position looks profitable.

### The fee-rounding residual, and why it is not a buffer

The pre-trade estimate prices the order as **one fill**. The venue may fragment it, and the accumulator makes
fragmentation *converge* on the equivalent order without *equalling* it — so a single-fill estimate is
slightly optimistic by an amount nobody can know before the order is worked. That amount has a derivable
worst case, from the mechanism rather than from taste:

```
net_fee_order  =  SUM(trade_fee_i)  +  accumulator_final        (rounding fees minus rebates ARE the accumulator)

CEILING term   within a price level the raw quadratic is linear in contracts, so SUM(raw_i) == raw_total,
               and each fill's centicent ceiling adds at most $0.0001. With N fills: < N × $0.0001.
RESIDUAL term  the accumulator starts at 0, each fill adds < one balance precision, and anything above one
               precision unit immediately rebates one — so the final residual is at most $0.01, and the
               DIFFERENCE from the single-fill estimate's own residual is bounded by the same $0.01.
N              a Kalshi fill is at least one whole contract, so N <= ceil(contracts).

bound = ceil(contracts) × $0.0001  +  $0.01
```

`conservative_net_ev_dollars = net_ev_dollars − bound`, and the gate requires it to be **above zero**.

This is protection against a **known transaction-cost uncertainty**, not a strategy edge buffer. It is
computed, never configured — `tests/test_gates_and_risk.py` reproduces it independently and asserts the gate
demands nothing more, and `tests/test_fee_freshness.py` checks empirically that no fragmentation of a real
order ever exceeds it. It does not move when the edge moves, only when the size does. For a 100-contract
position it is two cents.

---

## 5. Full-position executability

The top of book proves a **price** exists. It does not prove your **position** exists at that price.

```
approved stake   $50
best ask         56c for 1 contract
next liquidity   59c, then 60c
```

That is a **59.4c** position, not a 56c one. Calling it 56c is false in the flattering direction: the
displayed price is the cheapest contract you buy and every other one costs more, so a desk that sizes against
top-of-book systematically pays more than it recorded — on exactly the thin books where it thought it had
found something.

`nfl_edge/execution/depth.py` therefore walks the observed book for the **whole approved stake** and records:

* top ask, and the size available at it
* contracts required
* **full-position VWAP**
* worst consumed price
* dollar and probability slippage against the displayed top
* whether the book can fill the position at all

A `RECOMMENDED` record **fails closed** when depth cannot be established (no book, a post-decision book, a
stale book), when the approved stake exceeds observable liquidity, when the fill walks above
`bet_up_to_probability`, or when full-position net EV is ≤ 0 at the resulting VWAP.

**Book semantics.** Kalshi returns resting **bids** per side, ascending, best last. There are no ask ladders,
because an ask on one side *is* a bid on the other: to buy YES you lift NO bids, and a NO bid at `q` is a YES
ask at `1 − q`. This orientation was **verified empirically, not assumed** — reconstructing `yes_bid` and
`yes_ask` from the ladders reproduces the separately-captured quote row across 126 tickers in one run, and
every residual mismatch is the ~13-second book-after-quote lag present in all 126. That lag is also why the
book's **own** `observed_at` decides its freshness, never the quote's or the run's.

**The user-facing display does not change.** It stays `Current: 56% / Bet up to: 59%`. What changes is that
the *record* now distinguishes the top ask (56%) from the expected full-position VWAP (59.4%) from the worst
consumed price (60%), so nothing downstream can mistake one for another.

---

## 6. Player identity and availability

### Identity is fail-closed

An unresolved Kalshi → GSIS mapping means **we do not know whose statistics we priced**.

* The market stays visible and quotable in the packet.
* Its support state is explicitly `UNSUPPORTED_IDENTITY`.
* It can be `WATCHLIST` or `PASS`.
* It can **never** be `RECOMMENDED`.

No heuristic force-matching to improve coverage. Coverage is never traded for identity integrity.

### Availability is a term in the price, not background colour

Applies **only** to `PLAYER_STAT`, `FIRST_TD_SCORER` and `ANYTIME_TD`. A moneyline is not gated on anybody's
injury status.

| availability | YES prop |
|---|---|
| `INACTIVE_CONFIRMED` | **blocked** — the contract settles at $0.00 |
| `OUT`, `EXPECTED_OUT` | **blocked** — measured play rate under 2%; the position is a bet on the injury report being wrong |
| `UNKNOWN` | **blocked** — our sources did not find the player; participation risk is unquantified, not small |
| `QUESTIONABLE`/`DOUBTFUL` inside T-90m | **blocked** → WATCHLIST — inactives drop at T-90m, so the answer is knowable and we have not looked |
| stale > 360 min | **blocked** — a stale availability silently reads as ACTIVE, which is the failure this stops |
| missing entirely | **blocked** — an unrecorded availability is an unpriced term |

### The official inactive list

`INACTIVE_CONFIRMED` is **reserved and unpopulated**. No free source has been shown to deliver the official
gameday inactive list reliably.

`scripts/data/probe_inactives.py` reports what candidate sources actually deliver, and is written to run in
GitHub Actions close to kickoff. It is a probe, not a collector, on purpose: a broken inactives feed does not
degrade to "no information", it degrades to **"everyone is playing"** — the one answer that removes the
protection. Promotion to a collector is a separate decision made from several game days of probe output.

The gap costs coverage, not safety: the gates above already fail closed on unresolved availability near
kickoff.

---

## 7. Bankroll and portfolio risk

`config/risk_policy.json`, applied by `nfl_edge/handicap/risk.py`.

```
ChatGPT proposes  ->  risk policy validates / caps  ->  the ledger records BOTH numbers
```

`proposed_stake` is what the handicapper wanted; `recommended_stake` is what was approved. Recording both is
what makes the policy auditable: if they always agree the policy is not binding, and if they often disagree
the handicapper is systematically oversized. A policy that silently overwrote the proposal would destroy the
evidence for both claims.

### It is not Kelly

Deliberately. Edge-proportional sizing is a bet on the calibration of the probability generating the edge, and
the ChatGPT handicap layer has **zero prospective betting history** — that calibration is precisely what this
ledger exists to measure, so it cannot also be an input to sizing. Sizing is flat in units with grade-based
caps. Kelly is a question for *after* the handicap layer demonstrates prospective calibration.

### The limits

Every limit is a bankroll fraction or a count of units, so the same file is correct at any bankroll. A unit is
`unit_fraction_of_bankroll × bankroll_snapshot` (currently 0.5%).

| limit | pilot value |
|---|---|
| max stake per position | 2 units |
| grade caps | A+/A 2u, A- 1.5u, B+/B 1u, B- /C 0.5u |
| max exposure per game | 4 units |
| **max exposure per correlation group** | **3 units** |
| max slate exposure | the *more binding* of 12 units and 6% of bankroll |

Caps round **down**. A risk cap that rounds up is not a cap.

### Correlation

The packet carries **qualitative** correlation groups. They are treated as exactly that — no covariance matrix
is invented, because no such estimate exists for these contracts and inventing one would be worse than
admitting there is none.

What the policy does is notice concentration. Team ML + team spread + opponent under is one thesis bought
three times; QB passing over + WR receiving over is one game script bought twice; multiple alternate rungs on
one player stat is one projection bought repeatedly. The per-group cap is deliberately **tighter** than the
per-game cap for that reason: a correlation you can name but cannot measure is handled with a tighter limit.

PASS records and TEST_ONLY records consume no budget — a slate of passes must not crowd out the one bet that
was taken.

### The limits are CUMULATIVE, or they are not limits

A cap measured against one batch is a cap on **batch size**, which is a much weaker statement than a cap on
**exposure**:

```
run A, 13:00   home-side thesis, 2u    → passes the 3u correlation cap
run B, 15:00   another home-side, 2u   → passes the 3u correlation cap, independently
the desk       4u in one thesis        → the policy is broken and every gate said PASS
```

So every aggregate budget starts **partly consumed** by what the book already carries. `risk.report_for_batch`
reads the committed ledger at the decision timestamp and adds the batch to it. The caps then bind across
separate Airtable rows, separate RUN NFL invocations, amendments, multiple games on a slate, and multiple
correlated markets in one game.

**Outstanding exposure** is defined conservatively, and its two halves are held for different reasons:

| component | what it is | released when |
|---|---|---|
| **reserved** | `max(approved stake − executed stake, 0)` — an approval the owner has not yet filled is still a commitment to fill it | **kickoff**, after which the pregame position can no longer be established; or supersession by an amendment |
| **at risk** | executed stake — the money is gone until the contract resolves | **settlement**, established from an `Evaluation` carrying a `settlement` |

Their sum is `max(approved, executed)` for a fully-filled position, so a recommendation and its own fills
never double count, and a partial fill neither forgets the filled half nor releases the unfilled one. A $6
fill against a $10 approval holds $10: $6 at risk, $4 still reservable.

What is **excluded** is recorded as explicitly as what is included, with a reason per record, so the
subtraction can be audited: `TEST_ONLY`; `PASS` / `WATCHLIST` / `RESEARCH_ALERT`; superseded links in an
amendment chain (the amendment carries the chain's fills); anything decided *after* the decision being
evaluated; settled positions; and the batch's own records, which are counted in the batch rather than twice.

Two conservative bounds, the same shape as §3's capture-time bounds: **inclusion** is judged at the batch's
*latest* decision so no prior position is missed, and **release** at its *earliest* so nothing is let go
early. Both round against the batch.

An **unreadable ledger is not an empty one.** If outstanding exposure cannot be read, the risk gate returns
`UNAVAILABLE` and blocks. Treating "I could not see the book" as "the book is flat" is exactly how two 2u
positions in one group both clear a 3u cap.

---

## 8. The gates

`nfl_edge/handicap/gates.py`. Run once, when a record is first materialised.

All are evaluated **as of the record's `created_at`** except the last — see §3 for why that one is different.

They run twice: once **before** the bet is shown to anyone (§0) and once again when the record is imported,
from the same function. The table below is the same in both places.

| gate | blocks RECOMMENDED when | clock |
|---|---|---|
| `decision_timestamp_resolved` | `created_at` missing, unparseable, or timezone-naive | — |
| `decision_time_quote_freshness` | no confirmed executable quote in the window **before the decision** | decision |
| `executable_price_within_ceiling` | the ask **at the decision** was above `bet_up_to_probability` | decision |
| `player_identity_resolved` | unresolved identity, or SUPPORTED with no `player_id` | — |
| `player_availability_resolved` | availability missing, stale, or read **after** the decision | decision |
| `full_position_executable` | depth unestablished, stake exceeds liquidity, or the fill walks above the ceiling | decision |
| `fee_schedule_established` | no window covers the decision, an announced change is unmodelled, or the schedule is unverified past its policy window | decision |
| `net_executable_ev` | costs not `KNOWN`, EV uncomputable, EV **≤ $0**, or **conservative** EV ≤ $0 at the full-position VWAP | decision |
| `portfolio_risk_policy` | rejected by a **cumulative** limit, the recorded stake is not the approved stake, or the committed book could not be read | import (deterministic) |

**UNKNOWN is a FAILURE.** A gate that cannot reach its evidence returns `UNAVAILABLE`, and `UNAVAILABLE`
blocks exactly as `FAIL` does. Treating "I could not check" as "it is fine" is the failure mode all of this
exists to prevent.

### Gates are their own record

Results go into a `DecisionGates` file, **not** into the recommendation. The recommendation must hash
identically on every replay — the bridge's idempotency check compares canonical bytes — and gate results are
observations *made* at import time *about* the decision time, which differ between replays. Keeping them
separate is what lets *"identical replay is harmless"* and *"gates ran and passed"* both be true.

The record carries both clocks explicitly: `evaluated_at` is when the gates ran, `decision_as_of` is the
timestamp they evaluated at.

A record already durably in the ledger was gated when it was written. Re-gating it later would test today's
market against yesterday's decision and fail for entirely the wrong reason.

### TEST_ONLY

`TEST_ONLY` records risk no capital and are excluded from every report, so the **situational** gates do not
apply — they would make the end-to-end connectivity check depend on the live state of a market the fake
ticker does not have. **Structural** schema validation still runs in full, and that is what the E2E is
proving.

---

## 9. Multiple fills

A recommendation is routinely filled in pieces:

```
BUY YES up to 58%   ->   $20 at 54%   and   $30 at 55%
```

Every fill is its own immutable `Execution` record. Economics are computed **per fill** and summed:

```
cost    = contracts * price          (== stake)
payoff  = contracts * $1 on a win, $0 on a loss
gross   = payoff - cost
```

On a win: `20*(1-0.54)/0.54 + 30*(1-0.55)/0.55 = $41.58`. On a loss: `-$50`.

Nothing invents a single blended fill price to stand in for two real ones. A stake-weighted
`average_execution_price` **is** computed — it is the price that buys the same contracts for the same money,
so it reproduces the aggregate exactly, which is what makes it a legitimate slippage basis — and it is
labelled **DERIVED**. No execution record carries it.

### "Net P/L" may only mean fully observed net P/L

**GROSS** P/L is always computable from observed fills and settlement: nothing about it depends on knowing
what the trade cost.

**ACTUAL NET** P/L is a different claim, and it is only true when the costs are actually known. So `net_pnl`
and `net_roi` are numeric **only when every counted fill carries an OBSERVED venue fee**. Anything less —
no fee data, modelled fees, one of two fills unreconciled — and both are `null`.

The behaviour this replaces was worse than either extreme: subtracting whatever fees happened to be supplied
produced a number that *read* as realised and had priced the missing fills at zero. An unobserved fee is not
a zero.

The modelled figure still exists, under a name that cannot be mistaken for accounting:

| field | meaning |
|---|---|
| `gross_pnl` | payoff minus cost. Always available. |
| `net_pnl` | realised. `null` unless `fee_coverage_complete`. |
| `estimated_net_pnl` | gross minus every fee present, actual or modelled. `null` if **any** fill has no fee at all. |
| `fees_paid` / `fees_estimated` | observed and modelled totals, never summed into one another |
| `settlement_fees_paid` | a venue-reported settlement or fixed-point rounding adjustment, **when observed** |
| `fees_basis` | `ACTUAL` / `ESTIMATED` / `MIXED` / `INCOMPLETE` / `NONE` |
| `fills_total`, `fills_with_actual_fees`, `missing_fee_count`, `actual_fee_coverage`, `fee_coverage_gap` | the coverage arithmetic, so a reader checks the verdict instead of trusting it |

When the reconciliation later completes, `net_pnl` becomes numeric on the next evaluation. Nothing has to be
corrected, because nothing false was written. The schema enforces the same rule structurally: a record
asserting `net_pnl` while admitting incomplete coverage is **refused**, not filed.

The **scorecard** applies the identical rule at the portfolio level. Desk net P/L is the sum of realised
nets and exists only if every contributing position has one; otherwise it is `null` alongside a
`fee_reconciliation` block. Falling back to gross for one unreconciled position would price its fees at zero
and report the result as though it had been measured.

On **settlement adjustments**: Kalshi charges no settlement fee on these markets today, which is recorded
explicitly in `config/kalshi_fee_schedule.json` rather than assumed. If a venue-reported settlement or
rounding adjustment appears it is preserved on the `Execution` and reconciled into the net. If the schedule
says one is charged and none was observed, the actual net is `null` — the cost is known to exist and is not
manufactured.

P/L is counted **once per recommendation**, not once per fill. The scorecard reads the evaluation's aggregate;
it does not re-derive it.

---

## 10. The write paths are equivalent

There are exactly two ways a record reaches the immutable ledger — and one way a candidate reaches a human
before it becomes a record at all. All three are held to the same standard.
If the manual one were permissive it would be a hole straight through every protection the bridge applies —
documented in the runbook, reachable by anyone who read it, and indistinguishable in the ledger from a
properly gated write.

| | path | gates |
|---|---|---|
| pre-trade | `scripts/handicap/preflight_candidate.py` | required; exit 5 means **not a bet**. Writes nothing. |
| unattended | `scripts/handicap/sync_airtable.py` | required; a failure fails the batch |
| manual | `scripts/handicap/validate_recommendations.py --write` | required; `--market-data` is mandatory for a real `RECOMMENDED` record |

All three assemble the context through `preflight.build_context` and size through `risk.report_for_batch`,
so the cumulative portfolio arithmetic cannot differ between them. Both writers need `--handicap-root`
because outstanding exposure is read from it; an unreadable ledger blocks rather than being read as an empty
book.

`tests/test_write_paths_equivalent.py` pins the property that matters — not "the same code runs", but **"the
same record is refused"**: a stale price, a thin book and a live ask above the ceiling are rejected on every
path, and a PASS or a `TEST_ONLY` record is accepted on both writers without market data. It also pins the
one place the pre-trade path legitimately differs: an oversized proposal is *capped* before the trade (the
useful answer is a size) and *refused* at write time (a filed record must carry the approved size).

---

## 11. Airtable is transport. GitHub is canonical.

**`READY_FOR_SYNC` asserts that the recommendation ALREADY passed pre-trade approval.** It is not a request
to check it. The delayed GitHub import independently replays that evidence from the capture stream and
commits it; it is the second look, never the first. The twelve-hour cadence is preserved precisely because
the bridge is no longer load-bearing for safety.

Full detail in [`AIRTABLE_BRIDGE.md`](AIRTABLE_BRIDGE.md). The properties this standard depends on:

* The **entire batch** validates — schema *and* gates — before a single byte is written.
* One bad RECOMMENDED record fails all of them. A half-imported handicap run cannot be scored, and the
  missing half looks like decisions that were never made.
* Airtable's server-side `createdTime` is the prospective decision timestamp. `created_at` may not postdate
  it, may not predate it by more than 24 hours, and may not be at or after kickoff.
* Deduplication is idempotent; identical replay is harmless and writes nothing.
* A differing payload under an existing `recommendation_id` is a **hard conflict**, never an overwrite.
* Nothing is marked `SYNCED` until the GitHub push succeeds.
* A real recommendation with **no gate context** is refused outright. The unattended writer never materialises
  a bet without checking the world.

---

## 12. What this standard does not do

* It does not place, route or automate a wager. The Kalshi client is read-only and has no order surface.
* It does not enforce a minimum edge (§4).
* It does not activate the tail calibrator or role features. Both remain off; see
  [`ROADMAP.md`](ROADMAP.md) §"What is settled".
* It does not claim the model has an edge. It has been measured and it does not
  (`research/game_model/RESULTS.md`).
* It does not make the system profitable. It makes the **process** safe enough to begin prospective
  measurement. Profitability still has to be earned with real prospective CLV, calibration and ROI.
