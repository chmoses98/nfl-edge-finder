# Airtable bridge

**Airtable is a transport inbox. `handicap-data` remains the canonical ledger.**

ChatGPT cannot write to GitHub. The GitHub integration exposes write-shaped tools, but every branch or file
write returns `403 Resource not accessible by integration`. Reads work; writes do not. ChatGPT *can* write to
Airtable — that path is proven (base created, record created, record read back).

So the decision handoff goes through Airtable:

```
ChatGPT handicaps the slate
  -> writes ONE Airtable row per handicap run   (Status = READY_FOR_SYNC)
  -> sync-handicap-airtable workflow polls hourly
  -> existing handicap schema validates the batch
  -> immutable JSON files created on handicap-data
  -> git push succeeds
  -> Airtable row becomes SYNCED
  -> close / CLV / settlement / postmortem tooling continues unchanged
```

No manual copy/paste, no direct ChatGPT GitHub write, no second schema, no second ledger.

---

## The base

| | |
|---|---|
| Base | **Sports Betting Bridge** |
| Base ID | `appYrRmZ1Ax9sFByP` |
| Table | **Recommendation Runs** |
| Table ID | `tbl6kIANJRv6u8gEp` |

| Field | Type | Used for |
|---|---|---|
| `Run ID` | singleLineText (primary) | must equal every record's `handicap_run_id` |
| `Sport` | singleSelect — NFL / MLB / CFB | the importer polls `NFL` only |
| `Status` | singleSelect — TEST_ONLY / READY_FOR_SYNC / SYNCED / ERROR | lifecycle, below |
| `Payload` | multilineText | the canonical JSON array for one handicap run |
| `Notes` | multilineText | human use only; the importer never reads or writes it |

### One row = one handicap run

The `Payload` is a JSON **array** holding the whole serious-decision batch:

```json
[ recommendation_1, recommendation_2, pass_1, watchlist_1 ]
```

Each element is an ordinary Session-5 recommendation record — the same shape
`scripts/handicap/validate_recommendations.py` already accepts. GitHub explodes the batch into
`data/recommendations/<season>/week_<NN>/<recommendation_id>.json`, one immutable file each.

A bare single object is also accepted, but a list is the intended shape: one row is one run.

**Not one row per bet.** That would multiply Airtable API usage by the size of the slate for no benefit, and
would break batch atomicity.

---

## Status lifecycle

| Status | Meaning |
|---|---|
| `TEST_ONLY` | connectivity/scratch row. **Scheduled polling ignores it entirely** — it is excluded by the server-side filter, so it costs nothing and can never be imported. |
| `READY_FOR_SYNC` | ChatGPT has finished writing the batch; GitHub may ingest it. This is the only status the importer picks up. |
| `SYNCED` | every record in the payload was validated and is **durably present on `handicap-data`, and the push succeeded**. |
| `ERROR` | a permanent payload/schema/conflict problem. Fix by submitting a **corrected new row**, never by editing the failed one. |

`Status` is the **only** field the importer ever writes. `Run ID`, `Sport` and `Payload` are source data once
a row says `READY_FOR_SYNC`; the importer treats them as immutable and a later edit to `Payload` is detected
as a conflict (see below).

The existing probe row `recfB9h7TJeNRk2EF` / `test_nfl_chatgpt_write_001` carries `Status = TEST_ONLY`. It
proved ChatGPT can write to Airtable and **its payload is not a valid recommendation**. It is ignored, never
imported, and must not be deleted or reinterpreted.

> Airtable `Status = TEST_ONLY` and payload `test_only: true` are unrelated. The first is a scratch row the
> importer skips. The second is a real, importable recommendation that every report excludes. A proper E2E
> test uses `Status = READY_FOR_SYNC` **with** `test_only: true` records.

---

## Token setup (owner action)

1. In Airtable, create a **personal access token**.
2. Scopes — the minimum that works:
   * `data.records:read` — list pending rows
   * `data.records:write` — set `Status` after processing
3. Restrict its access to the **Sports Betting Bridge** base (`appYrRmZ1Ax9sFByP`) and nothing else.
4. In GitHub: `chmoses98/nfl-edge-finder` → **Settings** → **Secrets and variables** → **Actions** →
   **New repository secret**.
5. Name it exactly `AIRTABLE_TOKEN` and paste the token there.

**Never paste the token into a chat, an issue, a PR, a log, or this file.** The workflow passes it only
through the step environment — never on a command line, because argv is readable by other processes on the
runner. `nfl_edge/handicap/airtable_bridge.py::scrub` strips it from every message the bridge raises or
prints, and a test asserts it never reaches stdout or stderr.

The workflow fails with an explicit, non-leaking message if the secret is absent.

---

## Schedule and API budget

Airtable's free tier meters API requests per month, so the poll is deliberately cheap.

```yaml
schedule:
  - cron: '23 * * 9-12,1-2 *'   # hourly, September through February (season + playoffs)
workflow_dispatch:               # manual immediate sync, with an optional dry-run
```

| | requests |
|---|---|
| idle poll (no pending rows) | **1** (one filtered list; the filter runs server-side) |
| successful sync, any number of rows | **2** (one list + one batched status update, 10 rows per request) |
| sync with >100 pending rows | +1 per extra page — not a realistic state |

Roughly **750 requests/month in season, 0 out of season**. That is a small fraction of the free allowance.

Polling every 5–10 minutes would multiply this for no scientific gain: the **Airtable `createdTime` is the
decision handoff timestamp**, so the record is prospective whether GitHub ingests it in one minute or fifty.

Airtable `429`, `5xx`, timeouts and malformed responses are retried with bounded exponential backoff
(honouring `Retry-After`) and then reported as transient. The bridge fails closed and never hammers the API.

---

## Immutability and idempotency

`schema.write_record` refuses to overwrite an existing path. On top of that the bridge compares content:

| Case | Ledger state | Behaviour |
|---|---|---|
| **A** | recommendation file absent | validate → create the immutable file |
| **B** | file exists, content **semantically identical** | already imported. Nothing rewritten, no commit, row may become `SYNCED` |
| **C** | file exists, content **differs** | **hard fail.** No overwrite. Classified as a conflict, row becomes `ERROR`, surfaced loudly |

Case B is not a nicety — it is the required heal path. A push can succeed and the follow-up Airtable status
update can then fail, leaving a durable ledger and a row still marked `READY_FOR_SYNC`. The next run must
recognise the identical records and finish the job, **not** report an overwrite error.

Safety of that heal: every row is *planned* before any row is *applied*, so "already present" can only ever
refer to files that came out of the origin checkout — never to files a sibling row created moments earlier
in the same cycle.

**Amendments still work.** Immutability does not block revision: submit a new row whose records carry new
`recommendation_id`s and set `amends` to the original id. Both records survive; `store.latest_amendment_chain`
collapses them to the current opinion for reporting.

### Atomicity

One row is one atomic batch. If a payload holds 8 decisions and #7 is invalid, **none of the 8 are written**
and the row goes `ERROR`. Anything already written for that batch is rolled back.

Different rows in the same polling cycle are independent: Run A valid → imported; Run B invalid → `ERROR`;
Run C valid → imported. One corrupt run never blocks the others.

---

## Failure semantics

The distinction that matters: **permanent data problems become `ERROR`; infrastructure problems never do.**

| Failure | Result | Row status |
|---|---|---|
| invalid JSON in `Payload` | nothing written | `ERROR` |
| schema-invalid recommendation | nothing written | `ERROR` |
| `handicap_run_id` disagrees with `Run ID` | nothing written | `ERROR` |
| batch spans two slates, or duplicate ids | nothing written | `ERROR` |
| recommendation id exists with different content | nothing written, original untouched | `ERROR` |
| `Payload` edited after a prior sync (hash mismatch) | nothing written | `ERROR` |
| Airtable unreachable / timeout / `5xx` | nothing written | stays `READY_FOR_SYNC` |
| Airtable `429` | retried, then deferred | stays `READY_FOR_SYNC` |
| token rejected (`401`/`403`) | nothing written | stays `READY_FOR_SYNC` |
| **GitHub push fails** | records not durable | stays `READY_FOR_SYNC` |
| status update fails *after* a good push | ledger correct | stays `READY_FOR_SYNC`, healed next run |

A rejected token is deliberately **not** an `ERROR`: a misconfigured secret must never permanently condemn a
real recommendation.

Exit codes: `0` nothing to do or all imported · `1` at least one row failed permanently · `2` configuration
problem · `3` transient failure, work still pending.

---

## Timestamp / provenance integrity

Airtable stamps `createdTime` server-side — it is the one timestamp ChatGPT cannot forge — so every payload
timestamp is judged against it. **There is no backfill and never will be.**

* `created_at` must be ISO-8601 **with an explicit timezone**.
* `created_at` may be at most **5 minutes after** `createdTime` (clock skew between two machines).
* `created_at` may be at most **24 hours before** `createdTime`. Handicapping then submitting takes hours,
  not days; anything older is a retrospective recommendation and is refused.
* `createdTime` may not be in the future.
* If `kickoff_utc` is present, **both** `created_at` and `createdTime` must precede kickoff. A post-kickoff
  recommendation is not a prediction.

Every import also writes a small receipt:

```
data/import_receipts/<season>/week_<NN>/<airtable_record_id>.json
```

holding the Airtable base id, table id, record id, `createdTime`, `Run ID`, season/week, the payload
**SHA-256**, the recommendation ids, decision counts and the GitHub import timestamp.

The receipt documents **transport only**. It never replaces or modifies a recommendation, nothing in the
scorecard reads it, and the recommendation remains the canonical betting-history evidence. Its second job is
provenance enforcement: the same Airtable record id reappearing with a *different* payload hash means the
source row was edited after being synced, which the lifecycle forbids — that is a conflict.

---

## Running it

Scheduled hourly in season. To run immediately: **Actions → Sync handicap runs from Airtable → Run
workflow**, optionally ticking `dry_run` to validate pending rows without writing or changing any status.

Locally:

```bash
AIRTABLE_TOKEN=... python3 scripts/handicap/sync_airtable.py --handicap-root /path/to/handicap-data-wt --dry-run
AIRTABLE_TOKEN=... python3 scripts/handicap/sync_airtable.py --handicap-root /path/to/handicap-data-wt
```

`--no-push` writes records locally without committing, pushing, or touching any Airtable status.

### Inspecting a failed run

1. Open the workflow run. Each row logs one line: Airtable record id, `Run ID`, season/week, payload hash
   prefix, record count, decision counts, new vs already-present.
2. A rejected row logs `ERROR <record id>: <reason>` naming the offending field and payload index.
3. `ERROR` rows are visible in Airtable by filtering `Status = ERROR`.
4. Fix by creating a **corrected new row** (`READY_FOR_SYNC`). Never edit the failed row's payload — that is
   what conflict detection is for.

**Logs never contain payloads.** Identities, counts and hashes only — theses and probabilities stay out of a
log that could be read before the market resolves. Secrets are never logged.

---

## TEST_ONLY end-to-end test procedure

This proves the whole path without contaminating performance history. Do **not** reuse the old
`test_nfl_chatgpt_write_001` probe row.

1. ChatGPT creates a **new** row in `Recommendation Runs`:
   * `Sport` = `NFL`
   * `Status` = `READY_FOR_SYNC`
   * `Run ID` = e.g. `20260907T180000Z_e2e`
   * `Payload` = a JSON array of canonical recommendation records where **every** record has
     `"test_only": true` and `"handicap_run_id"` exactly equal to the `Run ID` above.
2. Timestamps must be live, not copied: `created_at` within the last 24 hours and before `kickoff_utc`, and
   `kickoff_utc` in the future. A stale example payload will be refused by the anti-backfill rule — that is
   the rule working.
3. Run the workflow (scheduled, or **Run workflow** manually).
4. Verify, in order:
   * the log shows the row was read and validated;
   * `data/recommendations/<season>/week_<NN>/<recommendation_id>.json` exists on `handicap-data`;
   * the sync commit is on `handicap-data`;
   * the Airtable row is now `SYNCED`;
   * `python3 scripts/handicap/scorecard.py --handicap-root <wt>` still reports **0 recommendations**,
     because `test_only` records are excluded from every report.

A worked minimal payload (replace all timestamps and ids with live values):

```json
[
  {
    "recommendation_id": "rec_e2e_20260907_001",
    "handicap_run_id": "20260907T180000Z_e2e",
    "created_at": "2026-09-07T18:00:00+00:00",
    "season": 2026, "week": 1,
    "game_id": "2026_01_NE_SEA",
    "kickoff_utc": "2026-09-10T00:20:00+00:00",
    "market_ticker": "KXNFLGAME-26SEP09NESEA-SEA",
    "market_family": "GAME_WINNER",
    "side": "YES",
    "yes_bid": 0.60, "yes_ask": 0.62, "no_bid": 0.38, "no_ask": 0.40, "mid": 0.61,
    "decision": "RECOMMENDED", "grade": "B+",
    "bet_up_to_probability": 0.65, "recommended_stake": 25,
    "probability_low": 0.61, "probability_mid": 0.66, "probability_high": 0.71,
    "primary_thesis": "TEST_ONLY end-to-end bridge verification. Not a real decision.",
    "reasoning_tags": ["ROLE_EXPANSION"],
    "test_only": true
  }
]
```

---

## Scope

This bridge carries **recommendation batches only**: `RECOMMENDED`, `PASS`, `WATCHLIST`, `RESEARCH_ALERT`.

Executions, evaluations and postmortems are unchanged and are not transported. Evaluations are *derived* by
`scripts/handicap/attach_evaluations.py` from close and settlement and must never arrive over a wire; a
payload carrying `evaluation_id`, `execution_id` or `postmortem_id` is refused with an explanatory error.

**Extension point** (deliberately not built): supporting execution payloads would mean adding a kind
discriminator to the batch check in `airtable_bridge.check_batch` and a second entry in the write path in
`plan_run`. That is a small change and should stay small — this is a transport, not a workflow engine.
