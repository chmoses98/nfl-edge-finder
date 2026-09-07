# RUN NFL

> The operating standard this workflow has to satisfy — required fields, the freshness policy, fees, risk
> limits and the price/P&L vocabulary — is [`DECISION_STANDARD.md`](DECISION_STANDARD.md).

**The model is the quantitative foundation. ChatGPT is the decision layer. The market is the benchmark.
The ledger is the memory.**

This document describes what happens when the user says **RUN NFL**, and how a decision becomes a permanent,
measurable record.

---

## Why the workflow is shaped this way

Sessions 1–4 established, and did not enjoy establishing, that:

* independent football projections do **not** reliably beat contemporaneous Kalshi pricing on outcomes
  (the market encompasses the model: market coefficient ≈ 1.0, model ≈ 0.0);
* passive execution on the core game markets fails on all three counts (no passive level exists on 86% of
  books, touch is not fill, and the orders that would fill are adversely selected);
* effects validated on the full player population attenuate or reverse on the contracts Kalshi actually
  lists (three for three, no counterexample).

So the workflow is **not** `model probability → bet`. That has been tested and it does not work.

What has *not* been tested is whether the model as a **structured information engine**, combined with market
prices and independent judgement, produces better decisions than either alone. That is a new experiment, and
it starts with zero history.

---

## The pipeline

```
MASSIVE NFL DATA COLLECTION        collectors -> market-data branch (continuous)
  -> STATISTICAL PROJECTIONS       shadow pricer -> immutable ledger, every listed market
  -> MARKET-IMPLIED EXPECTATIONS   latent distributions reconstructed from the same ladders
  -> CURRENT CONTEXT               injuries, depth charts, weather, movement
  -> STRUCTURED HANDICAP PACKET    scripts/handicap/run_nfl.py
  -> CHATGPT INDEPENDENT HANDICAP  <- you are the decision layer here
  -> KALSHI MARKET SELECTION       best-expression comparison, correlation groups
  -> PRE-TRADE PREFLIGHT           scripts/handicap/preflight_candidate.py  <- BEFORE anything is a BET
  -> AIRTABLE RECOMMENDATION RUN   ChatGPT writes one row -- the only write ChatGPT can make
  -> AIRTABLE -> GITHUB SYNC       sync-handicap-airtable workflow, REPLAYS the same gates and materialises
  -> IMMUTABLE RECOMMENDATION      handicap-data branch, one file per record
  -> CLOSE / CLV / SETTLEMENT      scripts/handicap/attach_evaluations.py
  -> POSTMORTEM                    named categories, explicit confidence
  -> CALIBRATION AND LEARNING      scripts/handicap/scorecard.py
```

---

## Step by step

### 1. Collectors update

The `shadow-price` workflow runs every two hours and publishes a ledger snapshot to `market-data`. The
capture conductor writes quotes roughly every ten minutes. Nothing needs to be triggered by hand.

Check health: `python3 scripts/shadow/system_health.py --md /home/user/_market_data_wt`

### 2. Build the packet

```bash
python3 scripts/handicap/run_nfl.py --season 2026 --week 1
```

Runtime ~8s for a 16-game slate. Outputs to `data/handicap/<run_id>/`:

| file | what it is |
|---|---|
| `packet.json` | complete machine record — every market, every ladder, every flag (~12MB) |
| `slate.md` | **read this first** — summary, priority ranking, one compact block per game (~21k tokens) |
| `games/<game_id>.md` | one full document per game, ~30KB each |

Add `--max-ledger-age-min 240` to refuse to build from a stale snapshot rather than emit a confidently
stale packet.

### 3. ChatGPT handicaps

Read `slate.md`. Use **GAME PRIORITY FOR HANDICAP** to choose which games to open in full — it ranks where
review is most likely to add something (new injuries, role changes, weather, large moves, many supported
props). **It is not a bet ranking and implies no value.**

Then, for each game you open:

* form a view from the football content — team profiles, QB splits, roles, matchup, injuries, weather;
* treat the model's disagreements as **one input among several**, never as a shortlist. Every one is labelled
  `DISAGREEMENT ONLY — REQUIRES HANDICAP` because that is exactly what it is;
* consult **BEST EXPRESSIONS** before choosing a contract. The largest disagreement is rarely the best
  payout for the risk taken;
* consult **CORRELATION GROUPS** before sizing more than one position in a game;
* answer the game's **KEY QUESTIONS**. They are generated from that game's actual data and are aimed at how
  this packet could be wrong.

### 4. Produce CANDIDATES, and preflight them before anything is called a bet

For each contract seriously considered, emit a record. Until it has passed preflight it is a **CANDIDATE**,
and a candidate may be shown as `CANDIDATE`, `WATCHLIST` or `PASS` — never as a BET or a final
`RECOMMENDED` instruction.

```
python3 scripts/handicap/preflight_candidate.py candidates.json \
    --market-data /home/user/_market_data_wt --handicap-root /home/user/_ledger_wt
```

Exit `0` means every candidate may be surfaced as a bet, **at the stake preflight approved**. Exit `5` means
at least one is blocked; surface those as CANDIDATE / WATCHLIST / PASS with the reasons it printed. The
script places nothing and writes nothing.

Preflight runs the same gates the ledger will later replay — decision-time price freshness, the ceiling,
full-position depth, the fee schedule, net EV, identity, availability, and the **cumulative** portfolio caps
— against the candidate's own `created_at`. That ordering is the point: the Airtable importer runs every
twelve hours, so without this step the first check on a bet the owner placed at 13:01 would happen at 01:00.
See [`DECISION_STANDARD.md`](DECISION_STANDARD.md) §0.

The shape the user reads, once approved:

```
BET
Market:        KXNFLGAME-26SEP09NESEA-SEA  (Seattle to win)
Current price: 62¢
Bet up to:     65¢
Stake:         $25
Grade:         B+
Probability:   66% (range 61–71%)
Key reasons:   ...
Reasons against: ...
```

**Record passes too.** A PASS on a contract that got serious consideration is a first-class scientific
record. Comparing RECOMMENDED against PASS on CLV and outcomes is the single most informative thing this
ledger will ever produce, and it only works if passes are recorded with equal care.

Prices are **Kalshi probability as displayed**. Fees are not folded into `bet_up_to_probability` — the
displayed price is the user's cost basis. Fee-aware analysis is separate, in `nfl_edge/execution/fees.py`.

#### What a RECOMMENDED record must carry

A `RECOMMENDED` record asks the user to risk money, and the ledger is immutable — a defective one is
permanent. So the full professional decision record is **required**, and every shortfall is a hard rejection
rather than a warning:

* **identity / lineage** — `packet_sha`, `season`, `week`, `game_id`, `kickoff_utc`, `market_family`
* **market state** — `market_timestamp`, `minutes_to_kickoff`, and the **side-specific executable ask**
  (`yes_ask` for YES, `no_ask` for NO). A midpoint is not accepted in its place.
* **handicap** — the full probability band, `bet_up_to_probability`, a grade, a positive whole-dollar stake,
  and non-empty `key_supporting_factors`, `counterarguments` and `uncertainties`
* **lineage** — `support_state` and `source_freshness`; plus `model_version` and `model_probability` where
  `support_state` is `SUPPORTED`

**The ceiling is a ceiling.** If the executable ask is *above* `bet_up_to_probability`, the record is
refused. The ledger must never be able to say "BET up to 58%" while the book is asking 61%.

`PASS`, `WATCHLIST` and `RESEARCH_ALERT` stay deliberately cheap to write — see
[`DECISION_STANDARD.md`](DECISION_STANDARD.md) §2 for why the asymmetry is the design and not an oversight.

#### The gates — run at preflight, replayed on ingestion

Beyond the record's own coherence, a real recommendation is checked against the **world**. The same gate
module runs twice: once **before** the bet is shown (step 4) and again when the importer archives it, which
is an independent replay from the capture stream rather than the first look. Any of these blocks it — and so
does a gate that could not reach its evidence, because "I could not check" must never resolve to "it is
fine":

| gate | blocks when |
|---|---|
| decision-time price freshness | no capture-confirmed executable quote within 15 minutes **before the decision** |
| ceiling | the ask **at the decision** was above `bet_up_to_probability` |
| player identity | the Kalshi → GSIS mapping is unresolved |
| player availability | availability is missing, UNKNOWN, blocking, stale, or read after the decision |
| full-position executability | the approved stake cannot be filled from observed depth, or the fill walks above the ceiling |
| fee schedule established | no committed window covers the decision, an announced Kalshi fee change is unmodelled, or the schedule has gone unverified past 45 days |
| transaction costs | costs are not `KNOWN`, or net executable EV — or **conservative** net EV, after the derived fee-rounding residual — is **≤ $0** at the full-position VWAP |
| portfolio risk | a per-position, grade, game, correlation-group or slate limit binds **cumulatively**, counting exposure already outstanding from earlier runs; or the committed ledger could not be read |

**Everything above is evaluated as of the recommendation's own `created_at`, not as of the import.** The
sync runs every twelve hours and archives decisions made hours earlier; judging them against the market at
import time would fail every call whose game had since kicked off. Import latency cannot change a verdict.
Only the risk gate runs on import-time state, and only because it reads no market data at all.

A failure fails the **whole batch**, and the reason is named in the workflow log. Full detail:
[`DECISION_STANDARD.md`](DECISION_STANDARD.md) §3–§8.

### 5. Write the records

ChatGPT emits the whole run as **one Airtable row** in the `Sports Betting Bridge` base:

| field | value |
|---|---|
| `Sport` | `NFL` |
| `Status` | `READY_FOR_SYNC` — asserts the batch **already passed pre-trade approval** |
| `Run ID` | the `handicap_run_id`, identical on every record in the payload |
| `Payload` | the canonical JSON **array** for the whole batch — recommendations, passes, watchlist, alerts |

That is the only write ChatGPT makes. `READY_FOR_SYNC` is an assertion, not a request: it says the
recommendation **has already been through preflight** at the approved stake. Within twelve hours — or
immediately, on manual dispatch — the `sync-handicap-airtable` workflow independently **replays** the gates
from the capture stream, materialises one immutable file per record on `handicap-data` plus its
`DecisionGates` evidence, pushes, and flips the row to `SYNCED`. The decision's prospective timestamp is
Airtable's server-side `createdTime`, so ingestion latency costs the audit trail nothing.

The twelve-hour cadence stays. It is right for archival transport, and it is no longer load-bearing for
safety.

See **GitHub write-back** below, and `docs/AIRTABLE_BRIDGE.md` for the full contract.

### 6. User reports actual bets — one record per FILL

The user may not take every recommendation, and may get a different price. That is an **execution** record,
never an edit to the recommendation. This is what lets recommendation quality and bankroll performance be
measured separately.

**One record per FILL, not per position.** A recommendation is routinely filled in pieces at different
prices, and each piece is its own immutable record:

```json
[
 {"execution_id": "exe_a", "recommendation_id": "rec_...", "executed_at": "...",
  "actual_price": 0.54, "stake": 20, "contracts": 37.037037, "side": "YES", "fees_paid": 0.35},
 {"execution_id": "exe_b", "recommendation_id": "rec_...", "executed_at": "...",
  "actual_price": 0.55, "stake": 30, "contracts": 54.545455, "side": "YES", "fees_paid": 0.52}
]
```

Economics are computed per fill and summed, so `BUY YES up to 58%` filled `$20 @ 54%` and `$30 @ 55%` scores
a `$41.58` gross win — not the number a single blended price would give. Never record a fake single-price
fill; the stake-weighted average IS computed and is labelled `average_execution_price` (DERIVED).

`fees_paid` is what the venue charged. Set `fees_are_estimated: true` if it is modelled rather than observed
— an estimated fee is carried and reported but **never** reduces realised P/L.

### 7. Close, CLV, settlement

```bash
python3 scripts/handicap/attach_evaluations.py --handicap-root <wt> --market-data <wt> --write
```

Close is the **last pregame** ledger observation for that ticker. A post-kickoff quote is never substituted;
when no pregame close exists the evaluation records `MISSING_CLOSE` as an outcome rather than reaching for
the nearest number.

### 8. Postmortem

Classify with named categories (`GOOD_PROCESS_VARIANCE`, `MODEL_TAIL_ERROR`, `ROLE_ERROR`,
`MARKET_ALREADY_PRICED`, …), multiple tags allowed, with explicit `confidence`. A won bet can still be a bad
process and a lost bet can still be a good one — `GOOD_PROCESS_VARIANCE` exists to be used honestly.

### 9. Scorecard

```bash
python3 scripts/handicap/scorecard.py --handicap-root <wt>
```

Compares **model vs market vs ChatGPT handicap** on the same resolved contracts, and RECOMMENDED vs PASS,
broken down by grade, market family, reasoning tag, time to kickoff, price bucket, model agreement, driver
and market type.

Also reports **gross ROI and net ROI after actual fees** (separately — see
[`DECISION_STANDARD.md`](DECISION_STANDARD.md) §1), total fees, mean entry slippage, the share of
recommendations that were actually executed, exposure by game and by correlation group, the missing-close
rate, gate-rejection counts, and an explicit **statistical power verdict**. An empty or underpowered sample
says so in words rather than printing zeros that read like measurements.

---

## GitHub write-back

**ChatGPT cannot write to GitHub.** The integration exposes write-shaped tools, but every branch or file
write returns `403 Resource not accessible by integration`. Reads work; writes do not. Anything in this
project that implies ChatGPT commits directly to `handicap-data` is wrong.

The write path is Airtable:

```
ChatGPT -> Airtable row (READY_FOR_SYNC) -> sync-handicap-airtable workflow
        -> existing schema validation -> immutable JSON on handicap-data -> push -> row becomes SYNCED
```

`.github/workflows/sync-handicap-airtable.yml` polls every 12 hours through the season and can be
dispatched manually for immediate ingestion. It checks out `main` and `handicap-data` as separate directories, runs
`scripts/handicap/sync_airtable.py`, and marks a row `SYNCED` **only after the push succeeds** — so a failed
push leaves the row pending for the next run instead of silently losing a decision.

**One immutable file per record.** That is the conflict-avoidance design: two records written minutes apart
touch different paths, so there is no shared append-target to serialise against and no merge conflict to
resolve.

1. The bridge validates the whole batch before writing anything — an invalid payload never reaches a commit.
2. Each record lands at `data/<kind>/<season>/week_<NN>/<record_id>.json` on `handicap-data`.
3. A whole handicap run's records commit together. Batching happens at the **commit** level, not the file
   level.
4. Nothing is ever edited or deleted. To revise, submit a new record whose `amends` names the original.

`write_record` refuses to overwrite an existing path (exit code 3), so immutability is enforced rather than
trusted. The bridge adds content comparison on top: an identical re-import is absorbed silently, a
*differing* record under an existing id is a hard conflict that writes nothing.

### Manual / engineering fallback

The direct local path still exists and is the right tool for engineering work, a repair, or a batch produced
outside ChatGPT:

```bash
python3 scripts/handicap/validate_recommendations.py payload.json                    # dry run first
python3 scripts/handicap/validate_recommendations.py payload.json --write \
    --handicap-root /path/to/handicap-data-worktree
```

Then commit to `handicap-data` by hand. This bypasses Airtable entirely and leaves no import receipt, which
is exactly why it is a fallback and not the routine path.

**Limitations.** The branch has no server-side protection: enforcement is client-side, in the validator and
the writer. Anyone with push access can bypass it. The audit trail is git history, which is why nothing is
ever rewritten or force-pushed on this branch.

---

## What this system does NOT do

* It does not place orders. Nothing here touches real money, and no code path can.
* It does not recommend anything on its own. `run_nfl.py` produces evidence; the handicap is a separate act.
* It does not backfill. There are no reconstructed historical ChatGPT picks and there never will be — a
  retrospective recommendation answers a question nobody asked and would corrupt the experiment.
* It does not claim the model beats the market. It does not.

## The experiment

> Does **NFL DATA + MODEL + MARKET + CHATGPT HANDICAP** produce better betting decisions than **MODEL
> ALONE** or **RAW DISAGREEMENT ALONE**?

Current sample: **zero resolved recommendations.** The scorecard reports that fact rather than printing
zeros. CLV, calibration and ROI over a real prospective sample are what will answer it.
