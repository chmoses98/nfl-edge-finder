# The decision standard

One operating policy for the last mile: **model → market → context → packet → ChatGPT decision → executable
price check → recommendation → Airtable → immutable ledger → execution → CLV → fees → P/L → scorecard.**

This is the canonical document for what a real recommendation must satisfy. Where any other doc disagrees
with this one, this one is right and the other needs fixing.

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
| **GROSS P/L** | payoff minus cost, before fees. Says whether the **call** was right. | `Evaluation.gross_pnl` |
| **NET P/L** | gross minus the fees actually charged. Says whether the **bankroll** grew. | `Evaluation.net_pnl` |
| **CLV** | close minus entry, signed in our direction. Says whether the **market moved toward us**. | `Evaluation.clv`, `clv_executable` |

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

`UNSUPPORTED_IDENTITY` can **never** carry a RECOMMENDED record — see §5.

### PASS is deliberately cheaper

`PASS`, `WATCHLIST` and `RESEARCH_ALERT` keep the light treatment. The rule deciding which side of the line a
check falls on: **does the failure mode cost money, or cost information?** Money-losing failures are errors on
RECOMMENDED. Information-losing failures are warnings.

Requiring a full market snapshot before you may record *"the price already reflects the news"* would mean the
passes never get written — and the comparison of what was taken against what was declined is the most
informative thing this ledger will ever produce.

---

## 3. Decision-time price freshness

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

```
taker  fee = round_up_to_cent(0.07   * M * C * P * (1 - P))
maker  fee = round_up_to_cent(0.0175 * M * C * P * (1 - P))
```

`C` is contracts **in the order**; rounding is applied **once per order**, not per contract. For a 100-lot at
50c that is the difference between $1.75 and $1.00.

### The maker multiplier is UNKNOWN, loudly

Kalshi's series metadata exposes `fee_type` but **not** the maker multiplier, and the published schedule says
it defaults to 0 "unless otherwise indicated" without saying what the indicated value is. So for the 25
maker-fee NFL series the maker cost is genuinely unknown.

It is modelled as `UNKNOWN` and **never defaulted**. `maker_fee()` returns `amount=None`, and
`net_executable_ev()` refuses to produce a net EV from an unknown cost — it does **not** fall back to zero. A
hidden default that is too low manufactures profitable passive trades that do not exist, which is the single
failure this design exists to prevent. Research that needs a number sweeps `MAKER_MULTIPLIER_SWEEP` and
reports every value.

This costs nothing operationally: passive execution was rejected on core game markets under H-019, so a real
recommendation is a **taker** order, and the taker path is fully known.

### Keeping it traceable

`scripts/kalshi/capture_fee_metadata.py` re-reads live per-series fee metadata, writes a dated snapshot to
`market-data`, and with `--check` exits non-zero when it disagrees with the committed registry — so a Kalshi
fee change surfaces as a failed job rather than as a quietly wrong number six weeks later. It never edits the
registry; that is a human decision.

### What the gate does and does not do

The gate **does** refuse to record a recommendation whose transaction costs are `UNKNOWN` or `DEGRADED`.
That is a data-integrity check.

The gate **does not** enforce a minimum edge by default. This session built the primitives to *measure* net
executable EV; it did not invent a minimum-edge rule, because none has been justified for this desk and
inventing one would silently become a strategy decision wearing a safety check's clothes. The switch exists
(`GateContext.require_net_ev_positive`) and is off. Turning it on is a deliberate policy change with its own
justification.

---

## 5. Player identity and availability

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

## 6. Bankroll and portfolio risk

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

---

## 7. The gates

`nfl_edge/handicap/gates.py`. Run once, when a record is first materialised.

| gate | blocks RECOMMENDED when |
|---|---|
| `decision_time_quote_freshness` | no confirmed executable quote inside the window |
| `executable_price_within_ceiling` | the **live** ask is above `bet_up_to_probability` |
| `player_identity_resolved` | unresolved identity, or SUPPORTED with no `player_id` |
| `player_availability_resolved` | availability missing or stale |
| `net_executable_ev` | transaction costs are UNKNOWN or DEGRADED |
| `portfolio_risk_policy` | rejected by a limit, or the recorded stake is not the approved stake |

**UNKNOWN is a FAILURE.** A gate that cannot reach its evidence returns `UNAVAILABLE`, and `UNAVAILABLE`
blocks exactly as `FAIL` does. Treating "I could not check" as "it is fine" is the failure mode all of this
exists to prevent.

### Gates are their own record

Results go into a `DecisionGates` file, **not** into the recommendation. The recommendation must hash
identically on every replay — the bridge's idempotency check compares canonical bytes — and gate results are
observations made at import time, which by definition differ between replays. Keeping them separate is what
lets *"identical replay is harmless"* and *"gates ran and passed"* both be true.

A record already durably in the ledger was gated when it was written. Re-gating it later would test today's
market against yesterday's decision and fail for entirely the wrong reason.

### TEST_ONLY

`TEST_ONLY` records risk no capital and are excluded from every report, so the **situational** gates do not
apply — they would make the end-to-end connectivity check depend on the live state of a market the fake
ticker does not have. **Structural** schema validation still runs in full, and that is what the E2E is
proving.

---

## 8. Multiple fills

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

### Gross, net, and what an estimate may do

Only fees the venue **actually charged** reduce realised P/L. Modelled fees are summed separately into
`fees_estimated` and never touch `net_pnl`. `fees_basis` records `ACTUAL` / `ESTIMATED` / `MIXED` / `NONE`, so
the gap between modelled and charged stays measurable rather than smoothed away.

P/L is counted **once per recommendation**, not once per fill. The scorecard reads the evaluation's aggregate;
it does not re-derive it.

---

## 9. Airtable is transport. GitHub is canonical.

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

## 10. What this standard does not do

* It does not place, route or automate a wager. The Kalshi client is read-only and has no order surface.
* It does not enforce a minimum edge (§4).
* It does not activate the tail calibrator or role features. Both remain off; see
  [`ROADMAP.md`](ROADMAP.md) §"What is settled".
* It does not claim the model has an edge. It has been measured and it does not
  (`research/game_model/RESULTS.md`).
* It does not make the system profitable. It makes the **process** safe enough to begin prospective
  measurement. Profitability still has to be earned with real prospective CLV, calibration and ROI.
