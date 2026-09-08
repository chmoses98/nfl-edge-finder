# Airtable bridge

> Airtable is transport. GitHub is canonical. The standard a record must satisfy before it reaches the
> canonical ledger is [`DECISION_STANDARD.md`](DECISION_STANDARD.md).

**Airtable is a transport inbox. `handicap-data` remains the canonical ledger.**

ChatGPT cannot write to GitHub. The GitHub integration exposes write-shaped tools, but every branch or file
write returns `403 Resource not accessible by integration`. Reads work; writes do not. ChatGPT *can* write to
Airtable — that path is proven (base created, record created, record read back).

So the decision handoff goes through Airtable:

```
ChatGPT handicaps the slate
  -> PRE-TRADE PREFLIGHT (scripts/handicap/preflight_candidate.py) approves or blocks each candidate
  -> writes ONE Airtable row per handicap run   (Status = READY_FOR_SYNC)
  -> sync-handicap-airtable workflow polls twice daily (or on manual dispatch)
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
| `READY_FOR_SYNC` | ChatGPT has finished writing the batch **and every RECOMMENDED record in it has already passed pre-trade preflight at its approved stake**; GitHub may ingest it. This is the only status the importer picks up. |
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
  - cron: '23 */12 * 9-12,1-2 *'   # every 12 hours, September through February (season + playoffs)
workflow_dispatch:                    # manual immediate sync, with an optional dry-run
```

| | requests |
|---|---|
| idle poll (no pending rows) | **1** (one filtered list; the filter runs server-side) |
| successful sync, any number of rows | **2** (one list + one batched status update, 10 rows per request) |
| sync with >100 pending rows | +1 per extra page — not a realistic state |

Roughly **60 requests/month in season, 0 out of season** — two idle polls a day, plus one extra request on
each day something is actually waiting. That leaves the large majority of the free allowance for ChatGPT's own
Airtable writes, status updates, retries, live E2E testing and any future sport's bridge.

Polling faster would buy latency this system has no use for. The bridge **archives** decisions that have
already been made: the prospective timestamp is the **Airtable `createdTime`**, stamped server-side when
ChatGPT writes the batch, so the scientific record is equally prospective whether GitHub ingests it in one
minute or twelve hours. Retrospective CLV, calibration, ROI and process analysis all read the ledger long
after the fact.

When you do want it now — a live E2E, or a batch you want on `handicap-data` immediately — use
`workflow_dispatch`. That is a zero-latency path that costs the same one or two requests.

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
| **a real `RECOMMENDED` record fails a decision gate** | nothing written | `ERROR` |
| **a real `RECOMMENDED` record with no gate context** | nothing written | `ERROR` |
| Airtable unreachable / timeout / `5xx` | nothing written | stays `READY_FOR_SYNC` |
| Airtable `429` | retried, then deferred | stays `READY_FOR_SYNC` |
| token rejected (`401`/`403`) | nothing written | stays `READY_FOR_SYNC` |
| **GitHub push fails** | records not durable | stays `READY_FOR_SYNC` |
| status update fails *after* a good push | ledger correct | stays `READY_FOR_SYNC`, healed next run |

A rejected token is deliberately **not** an `ERROR`: a misconfigured secret must never permanently condemn a
real recommendation.

### The decision gates

Beyond per-record schema validity, every **new** `RECOMMENDED` record is checked against the world **as it
was at the decision**: was the executable price confirmed and fresh then, was the ask under the stated
ceiling then, is the player identity resolved, was availability resolved, are the transaction costs known,
was the full approved stake executable from observed depth, and does the portfolio have room. See
[`DECISION_STANDARD.md` §8](DECISION_STANDARD.md#8-the-gates).

**This is the point most easily got wrong, and it is why the twelve-hour cadence is safe.** The bridge is
retrospective archival transport; ingestion is when a decision is *filed*, not when it is *made*. Gating
against the market at import time would reject a perfectly sound 13:00 call because the 01:00 sync found the
game already kicked off. Every market gate therefore reads the record's own `created_at`, evidence captured
after it is invisible, and freshness is measured backwards from it — so a recommendation that was valid when
made stays valid however late the importer runs, and one that was stale when made cannot be rescued by a
later capture. Airtable's `createdTime` keeps its separate job as the anti-backfill bound.

Three properties of how that is wired into this transport:

* **A gate failure fails the whole batch**, exactly like a schema failure. The atomicity rule is the same and
  for the same reason: a handicap run that is half in the ledger is a run nobody can score, and the missing
  half looks like decisions that were never made.
* **Only NEW records are gated.** A record already durably in the ledger passed its gates when it was
  written; re-gating it on a replay would test today's market against yesterday's decision and fail for the
  wrong reason — and would break the guarantee that identical replay is harmless.
* **Gate results go into a separate `decision_gates` record**, never into the recommendation. The
  recommendation must hash identically on every replay for the idempotency comparison to work, and gate
  results are import-time observations that differ between replays by definition. Keeping them apart is what
  lets "identical replay is harmless" and "gates ran and passed" both be true.

`TEST_ONLY` records keep full structural schema validation and skip the live-market gates — they risk no
capital, and gating them would make the E2E depend on the live state of a market their fake ticker does not
have.

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

Scheduled every 12 hours in season (roughly 00:23 and 12:23 UTC). To run immediately: **Actions → Sync
handicap runs from Airtable → Run workflow**, optionally ticking `dry_run` to validate pending rows without
writing or changing any status. Manual dispatch is the intended path whenever the twice-daily cadence is too
slow — it is unchanged and unthrottled.

Locally:

```bash
AIRTABLE_TOKEN=... python3 scripts/handicap/sync_airtable.py \
    --handicap-root /path/to/handicap-data-wt --market-data /path/to/market-data-wt --dry-run
AIRTABLE_TOKEN=... python3 scripts/handicap/sync_airtable.py \
    --handicap-root /path/to/handicap-data-wt --market-data /path/to/market-data-wt
```

`--market-data` must point at a `market-data` checkout: the decision-time price gate reads its capture
stream, and without it no `RECOMMENDED` record can be verified against a live executable price. The sync
refuses to start rather than importing real recommendations ungated.

`--max-quote-age-minutes` (default 15) is the freshness window. The conductor captures roughly every 10
minutes, so the default accepts one on-time capture and rejects a missed one.

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
    "packet_sha": "9328642968522db8ddcd",
    "yes_bid": 0.60, "yes_ask": 0.62, "no_bid": 0.38, "no_ask": 0.40, "mid": 0.61,
    "market_timestamp": "2026-09-07T17:58:00+00:00",
    "minutes_to_kickoff": 3260.0,
    "support_state": "SUPPORTED",
    "model_version": "shadow-0.4.0",
    "artifact_hash": "deadbeefcafe",
    "model_probability": 0.64,
    "decision": "RECOMMENDED", "grade": "B+",
    "bet_up_to_probability": 0.65,
    "proposed_stake": 25, "recommended_stake": 25,
    "probability_low": 0.61, "probability_mid": 0.66, "probability_high": 0.71,
    "primary_thesis": "TEST_ONLY end-to-end bridge verification. Not a real decision.",
    "key_supporting_factors": ["TEST_ONLY placeholder"],
    "counterarguments": ["TEST_ONLY placeholder"],
    "uncertainties": ["TEST_ONLY placeholder"],
    "source_freshness": {"shadow_snapshot": "2026-09-07T17:30:00+00:00"},
    "reasoning_tags": ["ROLE_EXPANSION"],
    "test_only": true
  }
]
```

Every field above is required for a `RECOMMENDED` record; the authoritative list is
[`DECISION_STANDARD.md` §2](DECISION_STANDARD.md#2-what-a-recommended-record-must-carry). A `PASS` needs far fewer — decision,
side, ticker, run id, and a `primary_thesis` saying why — because the cost of an incomplete `PASS` is lost
information, not lost money.

---

## Scope

This bridge carries **recommendation batches only**: `RECOMMENDED`, `PASS`, `WATCHLIST`, `RESEARCH_ALERT`.

Executions, evaluations and postmortems are unchanged and are not transported. Evaluations are *derived* by
`scripts/handicap/attach_evaluations.py` from close and settlement and must never arrive over a wire; a
payload carrying `evaluation_id`, `execution_id` or `postmortem_id` is refused with an explanatory error.

**Extension point** (deliberately not built): supporting execution payloads would mean adding a kind
discriminator to the batch check in `airtable_bridge.check_batch` and a second entry in the write path in
`plan_run`. That is a small change and should stay small — this is a transport, not a workflow engine.


---

## The PRE-TRADE leg (event-driven) — separate from everything above

Everything above this line is the **recommendation** transport: twelve-hourly archival movement of a
decision that has already been made and already been approved. It is not changing.

This section is a **different leg with a different job and a different cadence**. It answers the question
"may this candidate be shown to the owner as a BET?" — before the owner acts, not twelve hours afterwards.

```
ChatGPT
  → writes a PREFLIGHT_REQUESTED row (candidates in Payload)
  → an Airtable Automation calls the preflight workflow                     ← one-time owner setup
  → the workflow checks out main + market-data + handicap-data
  → scripts/handicap/preflight_airtable.py runs the SAME gates the ledger later replays
  → the row becomes PREFLIGHT_APPROVED or PREFLIGHT_BLOCKED, verdict in `Preflight Result`
  → ChatGPT reads the row
  → ONLY an APPROVED candidate may be surfaced as a BET, and only at `approved_stake`
  → the final recommendation is then submitted READY_FOR_SYNC for normal archival transport
```

### Why event-driven, and why the archival leg stays twelve-hourly

A confirmed executable quote is fresh for **fifteen minutes** and the owner needs the answer inside that
window. Polling for it would also spend the Airtable free-tier allowance the archival importer depends on,
to buy latency on a leg that has no use for it. So: preflight is invoked by an event, the importer is a
schedule, and neither is a workaround for the other.

### Statuses and fields

| status | meaning |
|---|---|
| `PREFLIGHT_REQUESTED` | ChatGPT wants a pre-trade verdict on the candidates in `Payload` |
| `PREFLIGHT_APPROVED` | **every** candidate on the row may be surfaced as a BET, at its approved stake, from `Approved Payload` |
| `PREFLIGHT_BLOCKED` | at least one may not — including an EXPIRED request. Per-candidate verdicts are in `Preflight Result`. |
| `PREFLIGHT_ERROR` | the request itself was unusable |

### Three artifacts, three stages

| field | what it is | who writes it |
|---|---|---|
| `Payload` | the immutable candidate **request** | ChatGPT, once |
| `Approved Payload` | the exact canonical batch the worker **approved** — approval timestamp, approved stake, approval-time market state | the preflight worker |
| `Preflight Result` | the verdict, plus `candidate_payload_sha256`, `approved_payload_sha256`, the Airtable row id, the approval timestamp and a per-candidate gate summary | the preflight worker |

To archive an approved bet, ChatGPT changes **only** `Status: PREFLIGHT_APPROVED → READY_FOR_SYNC` on that
same row. The importer then:

1. notices the batch contains a real `RECOMMENDED` record;
2. re-derives `sha256(Approved Payload)` and requires it to equal `approved_payload_sha256`;
3. requires the result to say `APPROVED` and to name this row;
4. archives **`Approved Payload`**, never the candidate `Payload`;
5. independently replays the gates at the approved record's `created_at` — which is the approval time.

**A real `RECOMMENDED` record written straight to `READY_FOR_SYNC` is refused.** So is one whose approved
batch was edited after approval, one carrying a `BLOCKED`/`EXPIRED`/`ERROR` verdict, and one whose approval
was issued for a different row. A PASS/WATCHLIST-only batch keeps the simple path: a pass costs nothing, is
scientifically valuable, and requiring an approval for it would only discourage recording passes.

### Approval time is the decision time

A candidate drafted at 13:00 and preflighted at 13:30 is a **13:30** decision. The worker re-prices the
record's market state — the two-sided quote, the mid, the market timestamp, the minutes to kickoff — to the
approval moment and gates it there, so a market that moved against the candidate blocks it. The **handicap**
is carried forward untouched: no probability, thesis or grade is recomputed.

A request older than `preflight.MAX_REQUEST_AGE_MIN` (30 minutes) comes back **EXPIRED**. The market can be
re-priced; the thesis cannot. Submit a fresh request rather than approving an opinion nobody has revisited.

**A row that is not `PREFLIGHT_APPROVED` has not been approved.** There is no third state and no default: a
request that errored, timed out, or was never picked up is not a bet. Silence is never yes.

`Preflight Result` is a long-text field carrying `preflight-result/1` JSON: per candidate the verdict,
`approved_stake`, `blocking_reasons`, the executable price, the full-position VWAP and worst fill, net EV
and conservative net EV, and each gate's status — plus the outstanding portfolio exposure the caps were
measured against.

The worker writes **only** `Status`, `Preflight Result` and `Approved Payload`. `Run ID`, `Sport` and
`Payload` are source data; `AirtableClient.write_fields` enforces the whitelist, so neither leg can rewrite
the candidate request — which is what keeps the three stages distinguishable.

### One-time owner setup

Two things cannot be provisioned from a code change and are the owner's to do once — **and they come after
this PR merges**, because the workflow does not exist on `main` until then. **Until both exist and a live
end-to-end run has succeeded, this leg is not operational.** The repository side being complete and tested
is a different claim.

**1. Add the fields and statuses in Airtable.**
Add `Preflight Result` and `Approved Payload` as **Long text** fields on the `Recommendation Runs` table,
and add `PREFLIGHT_REQUESTED`, `PREFLIGHT_APPROVED`, `PREFLIGHT_BLOCKED`, `PREFLIGHT_ERROR` as options on
the existing `Status` single-select.

**2. Create a GitHub token and an Airtable Automation.**

Create a **fine-grained personal access token** scoped to `chmoses98/nfl-edge-finder` only, with a single
permission:

| permission | level | why |
|---|---|---|
| **Actions** | Read and write | the minimum that can call `workflow_dispatch`. Nothing else is needed. |

Do **not** grant `Contents: write`. It would also work — via `repository_dispatch` — but it is a strictly
larger blast radius: a leaked `contents: write` token can push to any branch, including the ledger. An
`actions: write` token can only start workflows that already exist in the repository. The workflow accepts
`repository_dispatch` as well, for an Automation that prefers it; the narrower grant is the documented
default.

Then in Airtable: **Automations → Create → Trigger: When record matches conditions** (Table
`Recommendation Runs`, condition `Status is PREFLIGHT_REQUESTED`) → **Action: Run script**:

```js
// Airtable Automation script. The token lives in the Automation's secret input, never in this repository.
const GITHUB_PAT = input.config().githubPat;   // Automations → this script → Input variables
const res = await fetch(
  "https://api.github.com/repos/chmoses98/nfl-edge-finder/actions/workflows/preflight.yml/dispatches",
  { method: "POST",
    headers: { "Authorization": `Bearer ${GITHUB_PAT}`,
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28" },
    body: JSON.stringify({ ref: "main" }) });
if (res.status !== 204) throw new Error(`workflow_dispatch failed: ${res.status} ${await res.text()}`);
```

The workflow answers **every** pending `PREFLIGHT_REQUESTED` row, so the dispatch carries no payload and two
requests arriving together cost one run.

`AIRTABLE_TOKEN` is already configured as a repository secret for the importer; the preflight workflow uses
the same one. No credential is ever committed.

### TEST_ONLY end-to-end

Same discipline as the importer's E2E, and the same reason it is safe: a `TEST_ONLY` candidate risks no
capital, is excluded from every report, and the situational gates do not apply to it — so it can name a
ticker that does not exist.

1. Write one row: `Sport = NFL`, `Status = PREFLIGHT_REQUESTED`, `Run ID = E2E-PREFLIGHT`, `Payload` = a
   one-element array containing a complete candidate with `"test_only": true` and a fake ticker.
2. The Automation fires; the workflow runs.
3. The row should land on **`PREFLIGHT_BLOCKED`** with a `Preflight Result` whose single candidate has
   `may_be_shown_as_a_bet: false`. That is the correct answer, and a `TEST_ONLY` probe coming back approved
   would itself be the bug.
4. Nothing is written to any ledger branch. Preflight files no records.

`tests/test_preflight_transport.py` runs this whole leg against a fake Airtable, including the TEST_ONLY
probe, so the repository side is proven before the Automation exists. What the live run proves is the two
things tests cannot: that the Automation fires and that the token works.

### Debugging fallbacks — not the operating workflow

If the Automation is down, the owner can run the workflow by hand (`workflow_dispatch`, with `dry_run` to
see verdicts without writing), or run `scripts/handicap/preflight_candidate.py` locally against a candidate
file. Both are for debugging. Requiring either for a routine bet is what this leg exists to remove.
