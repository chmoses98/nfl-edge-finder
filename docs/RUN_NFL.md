# RUN NFL

> The operating standard this workflow has to satisfy — required fields, the freshness policy, fees, risk
> limits and the price/P&L vocabulary — is [`DECISION_STANDARD.md`](DECISION_STANDARD.md).

**The model is the quantitative foundation. ChatGPT is the decision layer. The market is the benchmark.
The ledger is the memory.**

This document describes what happens when the user says **RUN NFL**, and how a decision becomes a permanent,
measurable record.

---

## Getting the report — the short version

**Manual.** GitHub → **Actions** → **RUN NFL** → **Run workflow** → leave every field blank → **Run**.

You do not need to know the current NFL week. The workflow resolves it from the schedule.

When it finishes, the report is in two places:

| where | what |
|---|---|
| **[`handicap-reports/latest/`](../../tree/handicap-reports/latest)** | the newest good report, always at the same URL — `slate.md`, `packet.json`, `games/<game_id>.md`, `manifest.json` |
| the run's **artifact**, `run-nfl-<season>-w<week>-<run_id>` | the same tree, immutable, kept 90 days — this is the history |

So tonight's opener is at `handicap-reports/latest/games/2026_01_NE_SEA.md`, and the run summary links
straight to it.

**Automatic.** Nothing needs to be triggered by hand:

* **every ~2 hours** — the `Shadow Pricing (full universe)` cycle builds a fresh report from the ledger it
  just wrote, in the same run. It already downloaded the nflverse inputs and priced the slate, so the report
  costs it seconds rather than a second twenty-minute job.
* **T−24h, T−6h, T−90m, T−30m before every kickoff cluster** — `RUN NFL decision horizons` wakes every 15
  minutes, spends a few seconds deciding whether a horizon is owed, and only then runs the full fresh path.

**ChatGPT.** When the user says *RUN NFL — Pats Seahawks*, read the newest generated report:
`handicap-reports/latest/slate.md` first, then `handicap-reports/latest/games/2026_01_NE_SEA.md`. Check
`latest/manifest.json` for how old it is. **No Airtable is involved.** Airtable begins only later, and only
if a serious wager candidate is deliberately promoted to **PREFLIGHT NFL** (step 4 below).

---

## The workflows

### `RUN NFL` (`.github/workflows/run-nfl.yml`)

`workflow_dispatch` and `workflow_call`. Every input optional:

| input | blank means |
|---|---|
| `season` | resolve from the schedule |
| `week` | resolve from the schedule |
| `game_id` | no focus game; supplying one still builds the **whole canonical packet** and simply surfaces that game in the run summary |
| `force_fresh` | **true** — capture fresh context and price a fresh LOCAL snapshot before building |

`force_fresh=true` rebuilds the state the packet is made of, reusing the shadow-pricing setup: nflverse
bronze → silver → identity crosswalk, the latest `market-data`, a rebuilt Kalshi player map, a fresh
weather/injury/availability capture, the latest Kalshi captures, and a **local** shadow-pricing snapshot
copied under the `--market-data` tree so the packet reads it.

That local snapshot is **not published**. A research question does not append to the canonical immutable
shadow ledger; that stream belongs to the scheduled pricing job.

### `RUN NFL decision horizons` (`.github/workflows/run-nfl-horizons.yml`)

A cheap gate on a `*/15` cron. It resolves the week, clusters the slate's kickoffs, and asks whether any of
T−24h / T−6h / T−90m / T−30m is due and uncaptured. Almost every wake answers no in a few seconds, with no
dependency install — `nfl_edge/data/nfl_calendar.py` and `nfl_edge/handicap/horizons.py` are stdlib-only for
exactly that reason.

* **Clustered, not per game.** Nine games kicking off at 17:00Z are one decision moment. A T−90m horizon
  fires **one** full-slate build, not nine identical ones.
* **Late is captured, not lost.** GitHub cron fires late routinely. Any horizon whose trigger has passed and
  whose kickoff has not is due, and one build satisfies all of a cluster's due horizons at once — a T−30m
  packet is strictly fresher than the T−90m packet it stands in for.
* **Idempotent.** The identity is `<slate_id>|<cluster kickoff>|T-<n>m`, derived from the schedule and
  recorded in `handicap-reports:state/horizons.json` **only after a build succeeded**. A failed build leaves
  the horizon due for the next wake.

### Which week is it? (`nfl_edge/data/nfl_calendar.py`)

```bash
python3 scripts/handicap/resolve_active_week.py --market-data /path/to/market-data-worktree
```

Before a week's first kickoff → that week. While its games are still being played → that week. Once it is
complete (last kickoff + 4h) → the next week with published kickoff times. Postseason comes back as
`season_type: POST` with its round named, never as regular-season week 19. Nothing upcoming, or kickoff
times not published → `status: NO_SLATE` with a reason. **There is no guessed week.**

---

## Freshness, and how the report proves it

`latest/manifest.json` (and the run summary) carry:

`built_at` · `trigger` · season/week/`season_type` · `packet_sha` · `handicap_run_id` · `model_version` ·
shadow-pricing vintage and age · Kalshi capture vintage and age · context vintage and age · `main` SHA ·
`market-data` SHA · workflow run id and URL · games / markets listed / model-supported · blocking
data-health issues · minutes to each kickoff · the horizons this run captured.

### Why the report branch is one commit

`latest/packet.json` is ~25MB. Committing a replacement on top of the previous one every two hours would add
~300MB of branch history a day and roughly 2GB an NFL week. So every publish rewrites `handicap-reports` as
a fresh **root commit**, carrying `history/index.jsonl` and `state/horizons.json` forward; the branch stays
one snapshot in size forever.

That force-push is safe here for a reason that does not generalise: this branch is a replaced *surface*, not
a ledger. `market-data` and `handicap-data` are append-only and are never rewritten. The immutable history
of reports is the per-run Actions artifact, and `history/index.jsonl` is the index that traces one back to
its workflow run, source SHAs, model version and packet SHA.

---

## Fail closed

**Fail closed.** No ledger, a ledger past `--max-ledger-age-min`, a Kalshi capture past
`--max-capture-age-min`, a failed or unproven fresh context capture, no valid active week, no rows for the
week, a nonzero packet build, a missing or truncated game file — any of these exits nonzero, publishes
nothing, and leaves the previous `latest/` in place **with its own `built_at`**. An old report is allowed to
be old. It is never allowed to look new.

### The three freshness gates

| gate | flag | fresh / horizon | shadow cycle |
|---|---|---|---|
| shadow ledger age | `--max-ledger-age-min` | 45m | 45m |
| **Kalshi capture the ledger was priced from** | `--max-capture-age-min` | **30m** | 45m |
| **this run's own context capture** | `--require-context-run-id` | required | n/a |

* **A fresh ledger is not a fresh market.** `price_slate.py` prices the newest capture it can find, so a
  ledger written a minute ago can quote a Kalshi poll from an hour ago. The gate reads the ledger's
  `snapshot_run_id` — the capture manifest's `finished_at`, i.e. **when Kalshi was last successfully
  queried**. Deliberately *not* `minutes_since_price_change`, which is the time since a price last moved
  and is a microstructure signal, not staleness. The manifest reports both the priced-from vintage and the
  newest capture in the tree.
* **A `force_fresh` context capture that fails, fails the run.** The step is not `continue-on-error`, and
  `context_capture.py` exits 2 when any source failed closed. The build then proves this run's capture
  exists, failed closed on nothing, and is one the packet actually read. No report, no `latest/`, no
  horizon marked captured.
* The capture is **change-suppressed** — the manifest is always written, the ESPN/Sleeper blobs only when
  their content hash changed — so the proof hangs off the manifest, and unchanged content is carried
  forward with both its written-at and confirmed-at vintages recorded. No timestamp is ever invented.
* The shadow cycle uses 45m rather than 30m because it publishes shocks, runs system health and pushes the
  ledger between pricing and reporting; 30m there would chronically skip the 2-hourly refresh for reasons
  that say nothing about the data. It matches `price_slate.py`'s own `--max-quote-age-min`.

### `latest/` never moves backward

The shadow cycle and the horizon conductor are in different concurrency groups and can overlap, and
`--force-with-lease` protects the other job's *commit*, not the freshness of our *content*.

Comparing the ledger's `written_at` is not enough — that is when the snapshot was written, not how old the
evidence in it is. A cycle can write a ledger at 15:40 that was priced from a **15:05** capture carrying
**14:50** context, and so replace a horizon report written at 15:35 off a 15:30 capture with 15:34 context:
newer by every artifact timestamp, older in everything a reader actually sees. So the guard runs on the
**critical source vintages**, and every one must be non-regressing:

| source | key | fallback |
|---|---|---|
| market | `vintages.kalshi_capture.queried_at` | `snapshot_run_id` (the same instant, run-stamp form) |
| context | `vintages.context.captured_at` | last entry of `captures_used` |
| *tie-break only* | `vintages.shadow_pricing.written_at` | `built_at` |

Never `injuries.sources.*.content_vintage`. The capture is change-suppressed, so a run that re-confirmed
byte-identical content writes no blob and carries an older content vintage while being strictly **newer
confirmation**; ranking on it would treat a fresh re-confirmation as a regression.

The rule: if either critical source is older than the published one, `latest/` is not replaced. Only when
neither regresses may it be replaced, and only when both are exactly equal does the ledger time break the
tie. Fallbacks, so a branch published by an earlier version is never frozen: a source the *published*
report does not record has no baseline and does not vote; a source the published report records and the
*incoming* one does not is a refusal, because non-regression cannot be shown against a baseline that
exists.

A superseded run still succeeds: it records its manifest line in `history/index.jsonl` and carries the
horizon capture state forward (the horizon *was* satisfied — by a fresher report), and only `latest/` is
left alone.

### RUN NFL builds from `main`

The workflow checks out `ref: main` explicitly. The contract is *current production main + current
market-data*; a plain checkout would let a dispatch from an experimental branch produce a report
indistinguishable from a canonical one — same artifact name, same `latest/`, same manifest. Code under
development is still exercised normally by `tests.yml`, which checks out the PR head.

---

## What this path never touches

`scripts/ci/assert_no_airtable.py` runs as the **first** step of RUN NFL, before anything is downloaded, and
again inside the shadow-pricing cycle before the report is built. It walks the import graph from every entry
point of the report path and fails the run if anything reachable can name Airtable, the preflight handshake
or the recommendation writers. `tests/test_run_nfl_isolation.py` asserts the same thing in CI, including a
negative control that the audit can actually fail.

The report workflows request **no secrets at all**.

```
RUN NFL         unlimited, read-only research and handicap packet generation.  No Airtable. No bets.
PREFLIGHT NFL   explicit real-money candidate validation.  Airtable begins here and nowhere earlier.
```

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
  -> PRE-TRADE PREFLIGHT           Airtable PREFLIGHT_REQUESTED -> preflight workflow -> APPROVED/BLOCKED
                                   (event-driven; BEFORE anything is shown as a BET)
  -> AIRTABLE RECOMMENDATION RUN   ChatGPT writes one row -- the only write ChatGPT can make
  -> AIRTABLE -> GITHUB SYNC       sync-handicap-airtable workflow, REPLAYS the same gates and materialises
  -> IMMUTABLE RECOMMENDATION      handicap-data branch, one file per record
  -> CLOSE / CLV / SETTLEMENT      scripts/handicap/attach_evaluations.py
  -> POSTMORTEM                    named categories, explicit confidence
  -> CALIBRATION AND LEARNING      scripts/handicap/scorecard.py
```

---

## Step by step

### 1. Collectors update — and the report builds itself

The `shadow-price` workflow runs every two hours, publishes a ledger snapshot to `market-data`, and then
builds the handicap packet from that snapshot in the same run. The capture conductor writes quotes roughly
every ten minutes. The horizon conductor guarantees a fresh packet at T−24h, T−6h, T−90m and T−30m. Nothing
needs to be triggered by hand.

Check health: `python3 scripts/shadow/system_health.py --md /home/user/_market_data_wt`

### 2. Read the packet

Open [`handicap-reports/latest/`](../../tree/handicap-reports/latest), or download the run's artifact.
`latest/manifest.json` says how old it is; if it is older than you want, dispatch **RUN NFL** and wait a few
minutes.

To build one by hand — for engineering work, or against a worktree you control:

```bash
# resolve the week, build, verify and write manifest.json in one step
python3 scripts/handicap/build_report.py --market-data /home/user/_market_data_wt \
    --out data/handicap_report --max-ledger-age-min 240

# or drive the canonical builder directly
python3 scripts/handicap/run_nfl.py --season 2026 --week 1
```

Runtime ~8s for a 16-game slate. Outputs:

| file | what it is |
|---|---|
| `packet.json` | complete machine record — every market, every ladder, every flag (~12MB) |
| `slate.md` | **read this first** — summary, priority ranking, one compact block per game (~21k tokens) |
| `games/<game_id>.md` | one full document per game, ~30KB each |
| `manifest.json` | vintages, SHAs, counts — written by `build_report.py`, not by `run_nfl.py` |

`--max-ledger-age-min 240` refuses to build from a stale snapshot rather than emitting a confidently stale
packet.

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

**How ChatGPT actually invokes it.** Write ONE Airtable row:

| field | value |
|---|---|
| `Sport` | `NFL` |
| `Status` | `PREFLIGHT_REQUESTED` |
| `Run ID` | the `handicap_run_id` |
| `Payload` | the candidate array |

An Airtable Automation fires the `Pre-trade preflight` workflow, which runs the gates **as of the moment it
runs** and writes the verdict back within about a minute. Read the row:

* `PREFLIGHT_APPROVED` — every candidate may be surfaced as a BET, at the `approved_stake`, **exactly as it
  appears in `Approved Payload`**. To archive it, change only `Status` to `READY_FOR_SYNC` on that same row.
* `PREFLIGHT_BLOCKED` — at least one may not; `Preflight Result` names which and why. Surface those as
  CANDIDATE / WATCHLIST / PASS. A verdict of `EXPIRED` means the request sat longer than 30 minutes: the
  market can be re-priced, the thesis cannot, so submit a **fresh** request.

**A row that is not `PREFLIGHT_APPROVED` has not been approved.** Errored, expired, timed out, still
`PREFLIGHT_REQUESTED` — none of those is a bet. Silence is never yes.

**The approved record is not the candidate.** Its `created_at` is the approval moment, its market fields are
the approval-time quote, and its stake is what the risk policy allowed. The handicap — probabilities, grade,
thesis — is carried through untouched.

**Do not hand-edit `Approved Payload` or `Preflight Result`.** The approval is signed with a key that exists
only in GitHub Actions, and the importer verifies that signature against the row's own id, Run ID and both
payload hashes. An edited payload, a copied approval or a hand-written one is refused — there is no way to
produce a valid approval except by asking for one.

**Expiry is measured from when Airtable stamped the row**, not from the `created_at` in your payload. An old
request cannot be refreshed by re-dating the candidate.

Debugging fallback only, when the Automation is down:

```
python3 scripts/handicap/preflight_candidate.py candidates.json \
    --market-data /home/user/_market_data_wt --handicap-root /home/user/_ledger_wt
```

Exit `0` means approved, exit `5` blocked. Neither path places anything or writes any record.

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
| fee schedule established | no committed window covers the decision, an announced Kalshi fee change is unmodelled, the fee-change feed could not be read, or the schedule has gone unverified past 45 days |
| transaction costs | costs are not `KNOWN`, or net executable EV — or **conservative** net EV, after the derived fee-rounding residual — is **≤ $0** at the full-position VWAP |
| portfolio risk | a per-position, grade, game, correlation-group or slate limit binds **cumulatively**, counting exposure already outstanding from earlier runs (a settlement releases exposure only as of a moment the outcome was available); or the committed ledger could not be read |

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
