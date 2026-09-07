# RUN NFL

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
  -> AIRTABLE RECOMMENDATION RUN   ChatGPT writes one row -- the only write ChatGPT can make
  -> AIRTABLE -> GITHUB SYNC       sync-handicap-airtable workflow, validates and materialises
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

### 4. Produce recommendations and passes

For each contract seriously considered, emit a record. The shape the user reads:

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

### 5. Write the records

ChatGPT emits the whole run as **one Airtable row** in the `Sports Betting Bridge` base:

| field | value |
|---|---|
| `Sport` | `NFL` |
| `Status` | `READY_FOR_SYNC` |
| `Run ID` | the `handicap_run_id`, identical on every record in the payload |
| `Payload` | the canonical JSON **array** for the whole batch — recommendations, passes, watchlist, alerts |

That is the only write ChatGPT makes. Within the hour the `sync-handicap-airtable` workflow validates the
batch, materialises one immutable file per record on `handicap-data`, pushes, and flips the row to `SYNCED`.

See **GitHub write-back** below, and `docs/AIRTABLE_BRIDGE.md` for the full contract.

### 6. User reports actual bets

The user may not take every recommendation, and may get a different price. That is an **execution** record,
never an edit to the recommendation:

```json
{"execution_id": "exe_...", "recommendation_id": "rec_...", "executed_at": "...",
 "actual_price": 0.64, "stake": 25, "side": "YES", "notes": "filled 2c worse"}
```

This is what lets recommendation quality and bankroll performance be measured separately.

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

`.github/workflows/sync-handicap-airtable.yml` polls hourly through the season and can be dispatched
manually. It checks out `main` and `handicap-data` as separate directories, runs
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
